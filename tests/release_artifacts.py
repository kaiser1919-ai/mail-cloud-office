#!/usr/bin/env python3
"""Opt-in offline check of downloaded publisher archives; never executes them.
Usage: python tests/release_artifacts.py /path/to/artifacts
Expected names: server.tar.bz2 and <app-id>.tar.gz. Not a deployment test.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import posixpath
import sys
import tarfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fetch_check',ROOT/'ansible/files/fetch.py')
fetch=importlib.util.module_from_spec(spec);spec.loader.exec_module(fetch)


def main(directory):
    manifest=json.loads((ROOT/'components.json').read_text())
    evidence=json.loads((ROOT/'reports/components-1.1.json').read_text())
    core=int(manifest['nc_version'].split('.')[0])
    items=[{'id':'server','version':manifest['nc_version'],'sha256':manifest['nc_sha256']},*manifest['apps']]
    for item in items:
        name=item['id'];prefix='nextcloud' if name=='server' else name
        archive=directory/(name+('.tar.bz2' if name=='server' else '.tar.gz'))
        with archive.open('rb') as f:
            assert hashlib.file_digest(f,'sha256').hexdigest()==item['sha256'],name+' checksum'
        # One streaming pass: random reads in compressed CODE archives are costly.
        members=[]; file_hashes={}; metadata={}; links={}
        wanted={prefix+'/version.php',prefix+'/appinfo/info.xml',prefix+'/appinfo/signature.json'}
        with tarfile.open(archive, 'r|*') as tar:
            for member in tar:
                members.append(member)
                if member.issym():
                    links[member.name]=posixpath.normpath(posixpath.join(posixpath.dirname(member.name),member.linkname))
                if not member.isfile(): continue
                with tar.extractfile(member) as f:
                    if member.name in wanted:
                        data=f.read();metadata[member.name]=data
                        if name!='server':file_hashes[member.name]=hashlib.sha512(data).hexdigest()
                    elif name!='server':
                        file_hashes[member.name]=hashlib.file_digest(f,'sha512').hexdigest()
        fetch.validate_members(members,prefix)
        if name=='server':
            version=metadata[prefix+'/version.php'].decode()
            assert f"$OC_VersionString = '{item['version']}';" in version
            assert "$OC_Channel = 'stable';" in version
        else:
            xml=ET.fromstring(metadata[prefix+'/appinfo/info.xml'])
            assert xml.findtext('version')==item['version']
            deps=xml.find('dependencies/nextcloud').attrib
            assert int(deps['min-version'].split('.')[0])<=core<=int(deps['max-version'].split('.')[0])
            php=xml.find('dependencies/php')
            if php is not None:
                as_tuple=lambda x:tuple(int(v) for v in x.split('.'))
                for target in ('8.3','8.4'):
                    assert as_tuple(php.get('min-version','0'))<=as_tuple(target)<=as_tuple(php.get('max-version','99'))
            signed=json.loads(metadata[prefix+'/appinfo/signature.json'])
            assert signed['hashes'] and signed['signature'] and signed['certificate']
            # Check signed file hashes (not certificate/signature validation).
            for path,digest in signed['hashes'].items():
                actual=prefix+'/'+path
                for _ in range(32):
                    if actual not in links:break
                    actual=links[actual]
                assert file_hashes.get(actual)==digest,(name,path)
        upstream=evidence['releases'][name]
        assert upstream['sha256']==item['sha256'] and not upstream['draft'] and not upstream['prerelease']
        print(f'PASS {name} {item["version"]}: SHA256/archive bounds/metadata'+('/signed file hashes' if name!='server' else ''),flush=True)
    print('NOT RUN: native occ certificate/signature verification, install, browser, reboot, load.')


if __name__=='__main__':
    main(Path(sys.argv[1]))
