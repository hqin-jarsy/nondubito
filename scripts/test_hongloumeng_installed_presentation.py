#!/usr/bin/env python3
"""Run unchanged current tests in an exact authenticated, owned snapshot.

python3 -B scripts/test_hongloumeng_installed_presentation.py
runs all146 approved presentation cases; --anchors runs the other12 unchanged
anchor cases. Neither command runs tests in the installed source workspace.
Live CLI readiness and essential installed-output checks remain separate gates.
No Git/private-QA manifest, recursive source walk or test/validator rewrite.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
D='data/hongloumeng/first80-english/'
S='docs/hongloumeng/translation/'
BINDING=D+'reading-presentation-binding.json'
HISTORY=D+'history/v017-before'
OVERLAY=S+'english-binding-076-080.json'
CONTROL_HASHES={BINDING:'49f2c564325dda2565da801cc7b95176f2464bca0f6a13e1fbedc98ec8c3d57a',
 HISTORY+'/manifest.json':'fb7958eacd04e40ee450b9c18bdb69ed0734f69720d025c08af6eb177341614d',
 OVERLAY:'fda936f7f4d7ebf5682e6a6c9a02926b56a6a9eade6c0a5c316c62060df57e9b',
 'data/originals/hongloumeng/publication.json':'0b4be51aa96a2a702c35fead18051a1930145fec388dc9ee47272a15c43311d8'}
EXPECTED_INPUTS_SHA256='3ee33ec85822943b1b01fa4cf989c738cd89aa70467af455e3025d3a641e8adb'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

def checked_name(name):
    if not isinstance(name,str):raise ValueError('Non-string snapshot input')
    p=Path(name)
    if p.is_absolute() or '..' in p.parts or '.git' in p.parts or p.parts[:3]==('data','hongloumeng','first80'):
        raise ValueError('Forbidden snapshot input: '+name)
    return p


def regular(root,name):
    relative=checked_name(name);root=Path(root).absolute();path=root/relative
    for parent in (root,*[root/Path(*relative.parts[:i]) for i in range(1,len(relative.parts))]):
        st=parent.lstat()
        if not stat.S_ISDIR(st.st_mode) or parent.is_symlink():raise ValueError('Unsafe snapshot parent: '+name)
    st=path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1:raise ValueError('Nonregular or aliased snapshot input: '+name)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    with os.fdopen(fd,'rb') as stream:
        first=os.fstat(stream.fileno());raw=stream.read();last=os.fstat(stream.fileno())
    identity=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    if identity(st)!=identity(first) or identity(first)!=identity(last):raise ValueError('Snapshot input changed during read: '+name)
    return raw,stat.S_IMODE(st.st_mode)


def controls(root):
    result={}
    for name,digest in CONTROL_HASHES.items():
        raw,_=regular(root,name)
        if sha(raw)!=digest:raise ValueError('Snapshot control changed: '+name)
        result[name]=json.loads(raw)
    return result


def input_paths(root):
    data=controls(root);bound=data[BINDING];history=data[HISTORY+'/manifest.json'];overlay=data[OVERLAY]
    paths=set(CONTROL_HASHES)|{D+'reading-presentation-review.json',D+'reading-publication.json',
        D+'b16-semantic-review.json',D+'b16-technical-review.json','scripts/hongloumeng_reading_presentation_binding.py'}
    paths.update(history['files']);paths.update(history['unchangedRootFiles'])
    paths.update(HISTORY+'/'+p for p in history['files'])
    paths.update(overlay['publicFiles']);paths.update(overlay['evidence']);paths.update(r['path'] for r in overlay['draftFiles'])
    paths.update(S+n for n in (*history['normativeFiles'],'english-batch-076-080.json','english-binding-076-080.json'))
    for key in ('changedRootWitnesses','implementationHashes','unchangedContentHashes','publicRetrospectiveHashes','continuationUnchangedHashes'):paths.update(bound[key])
    paths.update(r['archivePath'] for r in bound['changedRootWitnesses'].values() if 'archivePath' in r)
    paths.add(bound['continuationDirectoryDisplay']['path'])
    # Exact public suite imports and discovery resources, not unrelated scripts.
    paths.update('scripts/'+n+'.py' for n in ('check_site_updates','build_search_index','build_sitemap','normalize_canonicals','build_home_updates','import_fairy_tales','build_hongloumeng_original','test_hongloumeng_b16_binding','test_hongloumeng_reading_discovery','test_hongloumeng_discovery_scope'))
    paths.update(('index.html','library.html','latest.html','sitemap.xml','search.js','zh-hant.js','essays/literature/index.html',
                  'essays/literature/hlm/index.html','essays/literature/hlm/en/index.html','essays/literature/hlm/zh-hant/index.html',
                  'data/site-updates.json','data/home-updates.json','data/search-index.json','data/hongloumeng/characters.json',
                  'data/originals/hongloumeng/translations/corrections.json'))
    paths.update('data/search/'+lang+'.json' for lang in ('en','zh-hans','zh-hant','ja','fr','de','es','ko'))
    paths.update(f'data/hongloumeng/readings/{n:02d}.json' for n in range(1,7))
    names=('index.html','edition.html','reader.css','reader.js',*(f'ch{n:03d}.html' for n in range(1,81)))
    for prefix in ('classics/hongloumeng/','classics/hongloumeng/zh-hant/','classics/hongloumeng/en/'):
        paths.update(prefix+n for n in names)
    publication=data['data/originals/hongloumeng/publication.json']
    paths.update('data/originals/hongloumeng/'+p for p in publication['multilingual_publication']['received_files'])
    paths.update(f'data/originals/hongloumeng/ch{n:03d}.zh.txt' for n in range(81,86))
    for p in paths:checked_name(p)
    return tuple(sorted(paths))


def snapshot(root,destination):
    if destination.exists() or destination.is_symlink():raise ValueError('Snapshot must be new')
    rows={};destination.mkdir()
    for name in input_paths(root):
        raw,mode=regular(root,name);rows[name]={'sha256':sha(raw),'mode':mode}
        target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);target.chmod(mode)
    digest=sha(encoded(rows))
    if digest!=EXPECTED_INPUTS_SHA256:raise ValueError('Snapshot required input hashes/modes differ')
    for name,row in rows.items():
        raw,mode=regular(destination,name)
        if {'sha256':sha(raw),'mode':mode}!=row:raise ValueError('Snapshot copy differs: '+name)
    return rows,digest


def verify_source(root,rows):
    for name,row in rows.items():
        raw,mode=regular(root,name)
        if {'sha256':sha(raw),'mode':mode}!=row:raise ValueError('Installed source changed during isolated tests: '+name)


def run(root,anchors=False):
    # Workspace and child TMPDIR are siblings of the snapshot, never inside it.
    with tempfile.TemporaryDirectory(prefix='hlm-installed-tests-') as workspace:
        workspace=Path(workspace).resolve();target=workspace/'snapshot';tmp=workspace/'tmp';tmp.mkdir()
        rows,digest=snapshot(root,target)
        command=[sys.executable,'-B',str(target/'scripts'/('test_hongloumeng_reading_english_anchors.py' if anchors else 'test_hongloumeng_current_presentation.py'))]
        if not anchors:command+=['--suite','all']
        env=dict(os.environ,PYTHONPATH=str(target/'scripts'),PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(tmp))
        result=subprocess.run(command,cwd=target,env=env)
        verify_source(root,rows)
        print(json.dumps({'scope':'unchanged tests in authenticated snapshot; not live readiness','tests':12 if anchors else 146,'snapshotInputs':len(rows),'inputManifestSHA256':digest,'sourcePrePostExact':True,'testReturnCode':result.returncode}),flush=True)
        return result.returncode


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--anchors',action='store_true');args=parser.parse_args()
    return run(ROOT,args.anchors)

if __name__=='__main__':raise SystemExit(main())
