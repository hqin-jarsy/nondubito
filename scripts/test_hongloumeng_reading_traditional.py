#!/usr/bin/env python3
"""Public-only exact-text, bilingual-route and release-gate regressions."""
import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
from unittest.mock import patch
from pathlib import Path
import tempfile
from urllib.parse import urljoin
import build_hongloumeng_reading as base
import build_hongloumeng_reading_traditional as traditional
from test_hongloumeng_reading import Page, rejected, path_output_regressions
from hongloumeng_english_availability import english_published


def check(reading, manifest):
    assets = base.load_assets()
    simplified, sm = base.load()
    original = base.render(simplified, sm, 'release', assets=assets)
    bilingual = base.render(simplified, sm, 'release', assets=assets, bilingual=True)
    pages = traditional.render(reading, manifest, 'release', assets=assets)
    draft = traditional.render(reading, manifest, 'draft', assets=assets)
    assert set(pages) == set(original)
    # The published English edition adds its own alternate link (render() checks the same gate).
    english = english_published(base.ROOT)
    for name, value in pages.items():
        if not name.endswith('.html'):
            continue
        page = Page(value)
        assert page.h1 == 1
        attrs = lambda tag: [a for t, a in page.attrs if t == tag]
        assert attrs('html') == [{'lang': 'zh-Hant'}]
        assert [a['href'] for a in attrs('link') if a.get('rel') == 'canonical'] == [traditional.CANONICAL + ('' if name == 'index.html' else name)]
        alternatives = {a['hreflang']: a['href'] for a in attrs('link') if a.get('rel') == 'alternate'}
        assert set(alternatives) == {'zh-Hans', 'zh-Hant', 'x-default'} | ({'en'} if english else set())
        if english:
            assert alternatives['en'] == base.CANONICAL + 'en/' + ('' if name == 'index.html' else name)
        assert alternatives['zh-Hant'] == traditional.CANONICAL + ('' if name == 'index.html' else name)
        assert alternatives['zh-Hans'] == alternatives['x-default'] == base.CANONICAL + ('' if name == 'index.html' else name)
        assert 'noindex' not in value
        dp = Page(draft[name])
        assert not [a for t, a in dp.attrs if t == 'link' and a.get('rel') in ('canonical', 'alternate')]
        assert 'noindex,nofollow' in draft[name]
        for language, target, source, prefix in [('zh-Hans', name, value, traditional.CANONICAL), ('zh-Hant', 'zh-hant/'+name, bilingual[name], base.CANONICAL)]:
            matches = [a for t, a in Page(source).attrs if t == 'a' and a.get('lang') == language]
            assert len(matches) == 1
            assert urljoin(prefix, matches[0]['href']) == base.CANONICAL + target
        # Adding navigation must not mutate any simplified body paragraph.
        assert Page(original[name]).paragraphs == Page(bilingual[name]).paragraphs
        if name.startswith('ch'):
            chapter = reading['chapters'][int(name[2:5])-1]
            assert [p['text'] for p in page.paragraphs] == [b['text'] for b in chapter['blocks']]
            assert base.digest(''.join(p['text'] for p in page.paragraphs)) == manifest['chapters'][chapter['number']-1]['body_sha256']
    assert traditional.CONTINUATION in pages['ch080.html']
    assert 'ch081.html' not in pages['ch080.html']
    assert '並非曹雪芹佚稿' in pages['index.html']
    assert '繁體版依本版已校訂' in pages['edition.html']
    assert 'Songti TC' in pages['reader.css'] and 'U+24AEB' in pages['reader.css']
    wrong = copy.deepcopy(reading); wrong['language'] = 'zh-Hans'
    rejected(lambda: base.validate(wrong, manifest, b'', language='zh-Hant'))
    rejected(lambda: base.validate(reading, manifest, b'', language='en'))
    rejected(lambda: traditional.release_gate(manifest, None))
    with tempfile.TemporaryDirectory(prefix='hlm-hant-gates-') as temporary:
        path = Path(temporary)/'approval.json'
        approval = dict(action='publish-hongloumeng-first80-traditional', text_version=manifest['text_version'], reading_sha256=manifest['reading_sha256'], body_sha256=manifest['body_sha256'], boundaries_finalized=True, approved=True, assets_sha256=manifest['build']['assets_sha256'])
        final = dict(manifest, status='finalized')
        path.write_text(json.dumps(approval)); traditional.release_gate(final, path)
        for key, bad in [('action', 'publish-hongloumeng-first80'), ('reading_sha256', '0'*64), ('body_sha256', '0'*64), ('approved', 1), ('boundaries_finalized', 1), ('extra', True)]:
            changed = dict(approval); changed[key] = bad; path.write_text(json.dumps(changed))
            rejected(lambda: traditional.release_gate(final, path))
        rejected(lambda: traditional.release_gate(dict(final,status='draft'), path))
    path_output_regressions(base.PUBLIC, pages)
    print('PASS Traditional reader: 80 exact chapter bodies; 82 bilingual canonical/hreflang pages; original simplified paragraphs unchanged; shared 48 negative path cases and isolated approval gates')



def safety_regressions():
    """All mutations are isolated fixtures, never real publication or source files."""
    names = ('reading.zh.json', 'manifest.json', 'reading.zh-hant.json', 'manifest.zh-hant.json', *base.ASSET_HASHES)
    checks = 0
    assets = base.load_assets()
    with tempfile.TemporaryDirectory(prefix='hlm-hant-safety-') as directory:
        root = Path(directory).resolve()
        inputs = root/'inputs'; inputs.mkdir()
        for name in names:
            target = inputs/name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(base.PUBLIC/name, target)
        repo = root/'repo'; repo.mkdir()
        def no_reads(fn):
            nonlocal checks
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('Read before preflight')), patch.object(Path, 'read_text', side_effect=AssertionError('Read before preflight')), patch.object(Path, 'write_bytes', side_effect=AssertionError('Write before preflight')), patch.object(Path, 'mkdir', side_effect=AssertionError('Directory created before preflight')):
                try:
                    fn()
                except (ValueError, OSError):
                    pass
                else:
                    raise AssertionError('Unsafe path accepted')
            checks += 1
        for name in names:
            target = inputs/name
            raw = target.read_bytes()
            other = root/'sentinel'; other.write_bytes(raw)
            for kind in ('symlink', 'hardlink', 'fifo'):
                target.unlink()
                if kind == 'symlink': target.symlink_to(other)
                elif kind == 'hardlink': os.link(other, target)
                else: os.mkfifo(target)
                no_reads(lambda: traditional.load(inputs))
                if name in ('reading.zh.json','manifest.json',*base.ASSET_HASHES):
                    no_reads(lambda: base.load(inputs))
                if name in base.ASSET_HASHES:
                    no_reads(lambda: base.load_assets(inputs))
                target.unlink(); target.write_bytes(raw)
            other.unlink()
        alias = root/'input-alias'; alias.symlink_to(inputs, target_is_directory=True)
        no_reads(lambda: traditional.load(alias))
        no_reads(lambda: base.load(alias))
        ancestor = root/'parent-alias'; ancestor.symlink_to(root, target_is_directory=True)
        no_reads(lambda: traditional.load(ancestor/'inputs'))
        no_reads(lambda: traditional.load(inputs/'..'/'inputs'))
        approval = root/'approval.json'; approval.write_text('{}')
        alias_approval = root/'approval-alias'; alias_approval.symlink_to(approval)
        no_reads(lambda: traditional.build(inputs, root/'temp-output', 'release', alias_approval))
        no_reads(lambda: base.build(inputs, root/'temp-output', 'release', alias_approval))
        with patch.object(base, 'ROOT', repo):
            for relative in ('data/hongloumeng/first80', 'data/hongloumeng/first80/nested', 'originals/hongloumeng', 'data/hongloumeng/first80-public/child'):
                for loader in (base.load,traditional.load,base.load_assets):
                    no_reads(lambda l=loader,r=relative:l(repo/r))
            for loader in (base.load,traditional.load,base.load_assets):
                no_reads(lambda l=loader:l(Path.home()/'not-a-public-input-fixture'))
            for builder, language, wrong in ((base,'zh-Hans','classics/hongloumeng/zh-hant'), (traditional,'zh-Hant','classics/hongloumeng')):
                for relative in (wrong, wrong+'/nested', 'classics', '.', 'originals/hongloumeng', 'other-project', 'data/hongloumeng/first80-public'):
                    no_reads(lambda b=builder,r=relative: b.build(inputs, repo/r, 'release', approval))
                expected = repo/'classics/hongloumeng'
                if language == 'zh-Hant': expected /= 'zh-hant'
                # A full preflight succeeds for the correct production root without reading or writing.
                base.plan_output(inputs, expected, 'release', base.OUTPUT_NAMES, language=language)
                no_reads(lambda e=expected,l=language: base.plan_output(inputs,e,'draft',base.OUTPUT_NAMES,language=l))
                expected.mkdir(parents=True,exist_ok=True)
                for filename in ('index.html','fonts/FONT-NOTICE.txt'):
                    destination=expected/filename; destination.parent.mkdir(parents=True,exist_ok=True)
                    sentinel=root/'output-sentinel'; sentinel.write_text('must remain unchanged')
                    for kind in ('symlink','hardlink','fifo'):
                        if kind=='symlink': destination.symlink_to(sentinel)
                        elif kind=='hardlink': os.link(sentinel,destination)
                        else: os.mkfifo(destination)
                        no_reads(lambda b=builder,e=expected: b.build(inputs,e,'release',approval))
                        assert sentinel.read_text()=='must remain unchanged'
                        destination.unlink()
                    sentinel.unlink()
            r,m = traditional.load(inputs)
            pages = traditional.render(r,m,'release',assets=assets)
            no_reads(lambda: base.plan_output(inputs,repo/'classics/hongloumeng','release',pages))
            sr,sm=base.load(inputs); sp=base.render(sr,sm,'release',assets=assets)
            no_reads(lambda: base.plan_output(inputs,repo/'classics/hongloumeng/zh-hant','release',sp))
            no_reads(lambda: base.plan_output(inputs,repo/'classics/hongloumeng/zh-hant','release',pages,language='zh-Hans'))
            poisoned=dict(sp);poisoned['zh-hant/index.html']=poisoned.pop('index.html')
            no_reads(lambda: base.plan_output(inputs,repo/'classics/hongloumeng','release',poisoned))
            poisoned=dict(pages);poisoned['../index.html']=poisoned.pop('index.html')
            no_reads(lambda: base.plan_output(inputs,repo/'classics/hongloumeng/zh-hant','release',poisoned))
        # Source gate is independent of approval status and checks all three frozen baselines.
        traditional.source_gate(inputs)
        for name in ('reading.zh.json','manifest.json'):
            target=inputs/name; raw=target.read_bytes(); target.write_bytes(raw+b' ')
            rejected(lambda: traditional.source_gate(inputs))
            target.write_bytes(raw); checks += 1
        # Valid isolated release proves the target checks are reachable and not masked by missing approval.
        target=inputs/'manifest.zh-hant.json'; manifest=json.loads(target.read_bytes()); manifest['status']='finalized';target.write_text(json.dumps(manifest))
        permit=dict(action='publish-hongloumeng-first80-traditional',text_version=manifest['text_version'],reading_sha256=manifest['reading_sha256'],body_sha256=manifest['body_sha256'],boundaries_finalized=True,approved=True,assets_sha256=manifest['build']['assets_sha256'])
        approval.write_text(json.dumps(permit))
        written=traditional.build(inputs,root/'isolated-release','release',approval)
        assert len(written)==87
    print(f'PASS hardened reader: {checks} no-read namespace/alias and source-binding negative checks; isolated release positive')

def finalized_test_fixture():
    """Draft remains unreleasable; positive release tests use a separate fixture."""
    rejected(lambda: traditional.source_gate(base.PUBLIC))
    with tempfile.TemporaryDirectory(prefix='hlm-hant-finalized-test-') as directory:
        root = Path(directory).resolve()
        public = root/'data/hongloumeng/first80-public'
        public.mkdir(parents=True)
        for name in ('reading.zh.json', 'manifest.json', 'reading.zh-hant.json', 'manifest.zh-hant.json', *base.ASSET_HASHES):
            target = public/name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(base.PUBLIC/name, target)
        original = (public/'manifest.json').read_bytes()
        manifest = json.loads(original); manifest['status'] = 'finalized'
        final = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode()
        (public/'manifest.json').write_bytes(final)
        scripts = root/'scripts'; scripts.mkdir()
        for name in ('build_hongloumeng_reading.py', 'build_hongloumeng_reading_traditional.py',
                     'test_hongloumeng_reading.py', 'test_hongloumeng_reading_traditional.py', 'web_analytics.py'):
            source = Path(__file__).resolve().parent/name
            raw = source.read_bytes()
            if name == 'build_hongloumeng_reading_traditional.py':
                before = base.digest(original).encode(); after = base.digest(final).encode()
                if raw.count(before) != 1:
                    raise ValueError('Test fixture expected exactly one source manifest binding')
                raw = raw.replace(before, after)
            (scripts/name).write_bytes(raw)
        # This is Chinese test-only fixture execution, never English release.
        subprocess.run([sys.executable, '-B', str(scripts/'test_hongloumeng_reading_traditional.py')],
                       cwd=root, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'}, check=True)
    print('PASS actual draft source gate rejected; explicit finalized Chinese test fixture passed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=base.PUBLIC)
    args = parser.parse_args()
    reading, manifest = traditional.load(args.input)
    check(reading, manifest)
    if base.load()[1]['status'] == 'draft':
        finalized_test_fixture()
    else:
        safety_regressions()


if __name__ == '__main__':
    main()
