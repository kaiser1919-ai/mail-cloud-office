"""Read-only release consistency guard; never upgrades an existing installation."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def component_manifest():
    return json.loads((ROOT / 'components.json').read_text())


def validate_installed_components(base=Path('/srv/mail-cloud/nextcloud'), manifest=None):
    manifest = component_manifest() if manifest is None else manifest
    expected = [('nextcloud', base, 'version.php', str(manifest['nc_version']))]
    expected += [(app['id'], base / 'custom_apps' / app['id'], 'appinfo/info.xml',
                  str(app['version'])) for app in manifest['apps']]
    for name, directory, marker, version in expected:
        if directory.is_symlink():
            raise ValueError(f'Unexpected component symlink: {name}; inspect manually')
        if not directory.exists():
            continue  # Same-release interrupted installation, not an upgrade.
        path = directory / marker
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Missing/unsafe component version: {name}; inspect manually')
        try:
            if name == 'nextcloud':
                match = re.search(r"\$OC_VersionString\s*=\s*['\"]([0-9.]+)['\"]\s*;", path.read_text())
                actual = match.group(1) if match else None
            else:
                actual = ET.fromstring(path.read_text()).findtext('version')
        except (ET.ParseError, UnicodeError) as exc:
            raise ValueError(f'Invalid component version: {name}; inspect manually') from exc
        if actual != version:
            raise ValueError(f'Component version mismatch: {name}; this release is for a NEW VPS or identical-version resume, not an in-place upgrade. Use the original release for the existing installation.')
