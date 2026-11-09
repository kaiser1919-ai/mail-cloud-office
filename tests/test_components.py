import json
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
import yaml
from test_bootstrap import ROOT, w, module

g = module('component_guard_tests', ROOT / 'installer/component_guard.py')


class Components(unittest.TestCase):
    def setUp(self):
        self.manifest = g.component_manifest()

    def test_release_manifest_has_stable_versions_pinned_https_and_hashes(self):
        self.assertEqual(self.manifest['release_version'], '1.1.0')
        self.assertEqual(self.manifest['nc_version'], '35.0.2')
        self.assertRegex(self.manifest['nc_sha256'], r'^[a-f0-9]{64}$')
        self.assertEqual({a['id'] for a in self.manifest['apps']},
                         {'mail', 'calendar', 'richdocuments', 'richdocumentscode'})
        for app in self.manifest['apps']:
            with self.subTest(app=app['id']):
                self.assertRegex(app['version'], r'^\d+\.\d+\.\d+$')
                self.assertRegex(app['sha256'], r'^[a-f0-9]{64}$')
                self.assertTrue(app['url'].startswith('https://github.com/'))
                self.assertIn(app['version'], app['url'])

    def test_ansible_consumes_manifest_and_checks_signed_apps_after_hashes(self):
        play = yaml.safe_load((ROOT / 'ansible/site.yml').read_text())[0]
        self.assertIn('../components.json', play['vars_files'])
        self.assertNotIn('nc_version', play['vars'])
        cloud = yaml.safe_load((ROOT / 'ansible/tasks/cloud.yml').read_text())
        fetch = next(t for t in cloud if t.get('name') == 'Fetch official pinned applications')
        self.assertIn('{{ item.sha256 }}', fetch['ansible.builtin.command']['argv'])
        check = next(i for i,t in enumerate(cloud) if t.get('name','').startswith('Check app signatures'))
        enable = next(i for i,t in enumerate(cloud) if t.get('name') == 'Enable official applications')
        self.assertLess(check, enable)
        self.assertIn('integrity:check-app', str(cloud[check]))

    def test_native_dependencies_select_fresh_stable_os_candidates(self):
        tasks = yaml.safe_load((ROOT / 'ansible/tasks/packages.yml').read_text())
        apt = tasks[0]['ansible.builtin.apt']
        self.assertEqual(apt['state'], 'latest')
        self.assertTrue(apt['update_cache'])
        self.assertEqual(apt['cache_valid_time'], 0)
        self.assertEqual(apt['policy_rc_d'], 101)
        self.assertNotIn('upgrade', apt)  # Not a full OS/dist upgrade.
        self.assertIn("if install or not shutil.which('ansible-playbook'):", (ROOT/'installer/wizard.py').read_text())

    def test_capacity_app_declares_current_core_and_new_version(self):
        xml=ET.parse(ROOT / 'ansible/files/sentinel_pool/appinfo/info.xml')
        self.assertEqual(xml.findtext('version'), '0.2.0')
        deps=xml.find('dependencies/nextcloud').attrib
        self.assertLessEqual(int(deps['min-version']),35)
        self.assertGreaterEqual(int(deps['max-version']),35)

    def core(self, base, version='35.0.2'):
        base.mkdir(exist_ok=True)
        (base/'version.php').write_text("<?php\n$OC_VersionString = '"+version+"';\n")

    def app(self, base, version=None):
        app=self.manifest['apps'][0]
        p=base/'custom_apps'/app['id']/'appinfo';p.mkdir(parents=True)
        (p/'info.xml').write_text('<info><version>'+ (version or app['version']) +'</version></info>')

    def test_fresh_and_same_release_interrupted_resume(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)/'nextcloud'
            g.validate_installed_components(base)
            self.core(base)
            g.validate_installed_components(base)
            self.app(base)
            g.validate_installed_components(base)

    def test_old_core_blocks_without_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)/'nextcloud';self.core(base,'34.0.4')
            before=(base/'version.php').read_bytes()
            with self.assertRaisesRegex(ValueError,'version mismatch'):
                g.validate_installed_components(base)
            self.assertEqual((base/'version.php').read_bytes(),before)

    def test_wrong_app_blocks_without_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)/'nextcloud';self.core(base);self.app(base,'5.12.4')
            with self.assertRaisesRegex(ValueError,'version mismatch'):
                g.validate_installed_components(base)

    def test_missing_version_invalid_xml_and_symlink_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)/'nextcloud';base.mkdir()
            with self.assertRaisesRegex(ValueError,'version'):g.validate_installed_components(base)
            self.core(base);self.app(base)
            info=base/'custom_apps/mail/appinfo/info.xml';info.write_text('<broken')
            with self.assertRaisesRegex(ValueError,'Invalid'):g.validate_installed_components(base)
            info.unlink();info.symlink_to(base/'version.php')
            with self.assertRaisesRegex(ValueError,'unsafe'):g.validate_installed_components(base)

    def test_guard_runs_before_preflight_swap_state_migration_or_packages(self):
        source=(ROOT/'installer/wizard.py').read_text()
        start=source.index('    profile = detect_platform()',source.index('def main():'))
        body=source[start:]
        guard=body.index('validate_installed_components()')
        for marker in ('atomic_json(stored, values)','preflight(c,','prepare_swap(',"run(['apt-get'"):
            self.assertLess(guard,body.index(marker),marker)

    def test_readmes_pin_this_release_and_disclose_no_new_live_acceptance(self):
        for name in ('README.md','README.ru.md'):
            s=(ROOT/name).read_text()
            self.assertIn('git clone --branch v1.1.0 --depth 1',s)
            self.assertIn('reports/release-1.1.md',s)
            for version in ('35.0.2','5.13.1','6.6.5','12.0.1','26.4.502'):
                self.assertIn(version,s)

    def test_verified_evidence_matches_manifest_and_php_profiles(self):
        evidence=json.loads((ROOT/'reports/components-1.1.json').read_text())
        self.assertEqual(evidence['checked_on'],self.manifest['checked_on'])
        self.assertEqual(evidence['releases']['server']['sha256'],self.manifest['nc_sha256'])
        for app in self.manifest['apps']:
            source=evidence['releases'][app['id']]
            self.assertEqual(source['tag'].removeprefix('v'),app['version'])
            self.assertEqual(source['sha256'],app['sha256'])
            self.assertEqual(source['url'],app['url'])
            self.assertTrue(source['signature_present'])
            self.assertFalse(source['draft']);self.assertFalse(source['prerelease'])
            deps=source['dependencies']['nextcloud']
            self.assertLessEqual(int(deps['min-version'].split('.')[0]),35)
            self.assertGreaterEqual(int(deps['max-version'].split('.')[0]),35)
