#!/usr/bin/env python3
"""Public-only regression tests and isolated, deterministic replay.

Uses only reading.zh.json, manifest.json, the three prepared font/license
assets, this test, the renderer and web_analytics.py. No private model, provenance, approval history or old reader.
"""
from __future__ import annotations
import argparse
import copy
import json
import os
import stat
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import build_hongloumeng_reading as renderer
from web_analytics import Document, issue


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.attrs = []
        self.h1 = 0
        self.paragraphs = []
        self.novel = False
        self.current = None
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.attrs.append((tag, a))
        if 'id' in a:
            assert a['id'] not in self.ids, 'Duplicate ID'
            self.ids.add(a['id'])
        self.h1 += tag == 'h1'
        for key in ('href', 'src'):
            if key in a:
                self.links.append(a[key])
        if tag == 'div' and a.get('class') == 'novel-text':
            self.novel = True
        if tag == 'p' and self.novel:
            self.current = dict(text='', classes=a.get('class', '').split())
            self.paragraphs.append(self.current)
        for key in a:
            if key.startswith('data-'):
                assert key in {'data-font', 'data-chapter', 'data-title', 'data-cf-beacon'}, key
        assert tag not in {'iframe', 'object', 'embed'}

    def handle_endtag(self, tag):
        if tag == 'p':
            self.current = None
        if tag == 'div' and self.novel:
            self.novel = False

    def handle_data(self, text):
        if self.current is not None:
            self.current['text'] += text


def rejected(fn):
    try:
        fn()
    except (ValueError, AssertionError, KeyError, TypeError):
        return
    raise AssertionError('Expected rejection')


def check(reading, manifest, pages):
    expected = {'index.html', 'edition.html', 'reader.css', 'reader.js'} | {f'ch{n:03d}.html' for n in range(1,81)} | set(renderer.ASSET_HASHES)
    assert set(pages) == expected
    htmls = {name: Page(content) for name, content in pages.items() if name.endswith('.html')}
    for name, page in htmls.items():
        raw = pages[name]
        assert page.h1 == 1
        assert Document(raw).noindex and not Document(raw).beacons
        assert '<link rel="canonical"' not in raw
        assert '本地预览 · 未定稿' in raw
        for forbidden in ('data-source', 'data-author', 'data-body', 'data-layout', '/audit/', 'preface.html', 'author-approved', 'model.json', '/Users/', 'file://', '原文字符', '审查记录', '审读稿', '校记'):
            assert forbidden not in raw, (name, forbidden)
        for href in page.links:
            target = urlsplit(href)
            if target.scheme or target.netloc:
                assert href == renderer.CONTINUATION
                continue
            assert not target.query and '..' not in Path(target.path).parts
            filename = unquote(target.path) or name
            assert filename in expected, (name, href)
            if target.fragment:
                assert filename in htmls and unquote(target.fragment) in htmls[filename].ids, (name, href)
    hashes = []
    for chapter in reading['chapters']:
        n = chapter['number']
        page = htmls[f'ch{n:03d}.html']
        assert len(page.paragraphs) == len(chapter['blocks'])
        assert ''.join(p['text'] for p in page.paragraphs) == renderer.body(chapter)
        for b,p in zip(chapter['blocks'], page.paragraphs):
            assert p['text'] == b['text']
            classes = [b['kind']] + [name for key,name in [('first','layout-first'),('last','layout-last'),('heading','diagram-heading'),('group_start','diagram-group-start')] if b.get(key)]
            assert p['classes'] == classes
        prev = [a['href'] for tag,a in page.attrs if tag=='a' and a.get('rel')=='prev']
        nxt = [a['href'] for tag,a in page.attrs if tag=='a' and a.get('rel')=='next']
        assert prev == ([f'ch{n-1:03d}.html'] if n>1 else [])
        assert nxt == ([f'ch{n+1:03d}.html'] if n<80 else [])
        sha = renderer.digest(''.join(p['text'] for p in page.paragraphs))
        assert sha == manifest['chapters'][n-1]['body_sha256']
        hashes.append(dict(number=n, body_sha256=sha, blocks=len(page.paragraphs), status='passed'))
    assert len([a for tag,a in htmls['index.html'].attrs if 'data-chapter' in a]) == 80
    diagram = [p for p in htmls['ch008.html'].paragraphs if 'diagram' in p['classes']]
    assert [p['text'] for p in diagram] == ['通灵宝玉正面图式','通灵宝玉','莫失莫忘','仙寿恒昌','通灵宝玉反面图式','一除邪崇','二疗冤疾','三知祸福']
    assert [i for i,p in enumerate(diagram) if 'diagram-heading' in p['classes']] == [0,4]
    assert [i for i,p in enumerate(diagram) if 'diagram-group-start' in p['classes']] == [0,4]
    assert sum('layout-first' in p['classes'] and 'diagram' not in p['classes'] for page in htmls.values() for p in page.paragraphs) == manifest['layout_group_count']
    return hashes



def path_output_regressions(inputs, pages):
    """All fixtures are temporary; no real protected target is ever modified."""
    def snapshot(folder):
        result = {}
        for node in [folder, *sorted(folder.rglob('*'))]:
            mode = node.lstat().st_mode
            key = str(node.relative_to(folder))
            if stat.S_ISLNK(mode):
                result[key] = ('link', os.readlink(node))
            elif stat.S_ISDIR(mode):
                result[key] = ('directory',)
            elif stat.S_ISREG(mode):
                result[key] = ('file', renderer.digest(node.read_bytes()), node.stat().st_nlink)
            else:
                result[key] = ('other', mode)
        return result

    cases = [
        'index-link-protected', 'late-font-link-protected', 'index-link-input',
        'index-link-outside', 'index-link-inside', 'dangling-index-link',
        'fonts-link-protected', 'dangling-fonts-link', 'root-link-protected',
        'dangling-root-link', 'ancestor-link', 'dangling-ancestor-link',
        'file-as-fonts-directory', 'directory-as-index-file', 'file-as-root',
        'index-hardlink-protected', 'late-font-hardlink-protected',
        'input-root', 'input-child', 'protected-root', 'protected-child',
        'parent-traversal'
    ]
    checks = []
    with tempfile.TemporaryDirectory(prefix='hlm-output-path-tests-') as tmp:
        # Canonicalize the fixture root, while clean-tree CLI replay also tests
        # the platform's ordinary tempfile path (macOS /var ancestor alias).
        root = Path(tmp).resolve()
        local_inputs = root/'public-inputs'
        local_inputs.mkdir()
        for name in ('reading.zh.json','manifest.json',*renderer.ASSET_HASHES):
            target=local_inputs/name; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(inputs/name,target)
        inputs=local_inputs
        for case in cases:
            fixture = root / case
            scripts = fixture / 'scripts'
            scripts.mkdir(parents=True)
            for name in ('build_hongloumeng_reading.py', 'web_analytics.py'):
                shutil.copyfile(Path(__file__).parent / name, scripts / name)
            output = fixture / 'data/hongloumeng/first80/qa/preview'
            output.mkdir(parents=True)
            for name in pages:
                target = output / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(('unchanged sentinel: ' + name).encode())
            protected = fixture / 'classics/hongloumeng'
            (protected / 'fonts').mkdir(parents=True)
            (protected / 'index.html').write_text('protected HTML sentinel')
            (protected / 'fonts/FONT-NOTICE.txt').write_text('protected font sentinel')
            outside = fixture / 'outside'
            outside.mkdir()
            (outside / 'target').write_text('outside sentinel')
            supplied = output
            if case in ('index-link-protected', 'index-link-input', 'index-link-outside', 'index-link-inside', 'dangling-index-link'):
                target = {'index-link-protected': protected / 'index.html', 'index-link-input': inputs / 'reading.zh.json', 'index-link-outside': outside / 'target', 'index-link-inside': output / 'ch001.html', 'dangling-index-link': outside / 'absent'}[case]
                (output / 'index.html').unlink()
                (output / 'index.html').symlink_to(target)
            elif case == 'late-font-link-protected':
                (output / 'fonts/FONT-NOTICE.txt').unlink()
                (output / 'fonts/FONT-NOTICE.txt').symlink_to(protected / 'fonts/FONT-NOTICE.txt')
            elif case in ('fonts-link-protected', 'dangling-fonts-link'):
                shutil.rmtree(output / 'fonts')
                (output / 'fonts').symlink_to(protected / 'fonts' if case == 'fonts-link-protected' else outside / 'absent', target_is_directory=True)
            elif case in ('root-link-protected', 'dangling-root-link'):
                supplied = fixture / 'output-link'
                supplied.symlink_to(protected if case == 'root-link-protected' else outside / 'absent', target_is_directory=True)
            elif case in ('ancestor-link', 'dangling-ancestor-link'):
                link = fixture / 'ancestor'
                link.symlink_to(outside if case == 'ancestor-link' else outside / 'absent', target_is_directory=True)
                supplied = link / 'preview'
            elif case == 'file-as-fonts-directory':
                shutil.rmtree(output / 'fonts')
                (output / 'fonts').write_text('directory-position sentinel')
            elif case == 'directory-as-index-file':
                (output / 'index.html').unlink()
                (output / 'index.html').mkdir()
                (output / 'index.html/marker').write_text('nested sentinel')
            elif case == 'file-as-root':
                supplied = fixture / 'root-file'
                supplied.write_text('root sentinel')
            elif case in ('index-hardlink-protected', 'late-font-hardlink-protected'):
                name = 'index.html' if case == 'index-hardlink-protected' else 'fonts/FONT-NOTICE.txt'
                (output / name).unlink()
                os.link(protected / name, output / name)
            elif case == 'input-root':
                supplied = inputs
            elif case == 'input-child':
                supplied = inputs / 'must-not-exist'
            elif case == 'protected-root':
                supplied = protected
            elif case == 'protected-child':
                supplied = protected / 'must-not-exist'
            elif case == 'parent-traversal':
                supplied = output / '..' / 'outside'
            before = snapshot(fixture)
            before_inputs = snapshot(inputs)
            for mode, flags in (('normal', []), ('optimized', ['-O'])):
                run = subprocess.run([sys.executable, '-B', *flags, str(scripts / 'build_hongloumeng_reading.py'), '--input', str(inputs), '--mode', 'draft', '--output', str(supplied)], capture_output=True, text=True)
                if run.returncode == 0:
                    raise AssertionError(case + ' unexpectedly accepted in ' + mode)
                if snapshot(fixture) != before or snapshot(inputs) != before_inputs:
                    raise AssertionError(case + ' changed files/directories before rejecting in ' + mode)
                checks.append(dict(case=case, mode=mode, status='passed', all_sentinels_and_directory_entries='unchanged'))
        for filename in ('../outside', '/absolute', '.', 'fonts/../../outside'):
            before = snapshot(root)
            rejected(lambda: renderer.plan_output(inputs, root / 'absent-output', 'draft', [filename]))
            assert snapshot(root) == before
            checks.append(dict(case='invalid-generated-name:' + filename, mode='direct-preflight', status='passed'))
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=renderer.PUBLIC)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--skip-replay', action='store_true')
    args = parser.parse_args()
    reading, manifest = renderer.load(args.input)
    pages = renderer.render(reading, manifest, 'draft', assets=renderer.load_assets(args.input))
    chapters = check(reading, manifest, pages)
    if args.output:
        assert {str(p.relative_to(args.output)) for p in args.output.rglob('*') if p.is_file()} == set(pages), 'Unexpected output file'
        for name,text in pages.items():
            assert (args.output/name).read_bytes() == renderer.as_bytes(text), name+' differs from deterministic renderer'
    raw = (args.input/'reading.zh.json').read_bytes()
    poisoned = copy.deepcopy(reading)
    poisoned['chapters'][0]['source_path'] = 'private'
    rejected(lambda: renderer.validate(poisoned, manifest, raw))
    poisoned = copy.deepcopy(reading)
    poisoned['chapters'][0]['blocks'][0]['author_change_ids'] = ['x']
    rejected(lambda: renderer.validate(poisoned, manifest, raw))
    poisoned = copy.deepcopy(reading)
    poisoned['chapters'][0]['blocks'][0]['text'] += '字'
    rejected(lambda: renderer.validate(poisoned, manifest, raw))
    rejected(lambda: renderer.release_gate(manifest, None))
    finalized = copy.deepcopy(manifest)
    finalized['status'] = 'finalized'
    rejected(lambda: renderer.release_gate(finalized, None))
    # Exercise release HTML in memory only; no formal output or publication.
    release_page = renderer.shell('Test', 'Test', '<h1>Test</h1>', 'ch001.html', False, reading['title'])
    assert not Document(release_page).noindex and issue(Document(release_page)) is None
    assert f'<link rel="canonical" href="{renderer.CANONICAL}ch001.html">' in release_page
    release_index = renderer.shell('Test', 'Test', '<h1>Test</h1>', 'index.html', False, reading['title'])
    assert f'<link rel="canonical" href="{renderer.CANONICAL}">' in release_index
    assert renderer.CANONICAL+'index.html' not in release_index
    assert 'unicode-range:U+24AEB' in pages['reader.css']
    for name, expected_sha in renderer.ASSET_HASHES.items():
        assert renderer.digest(pages[name]) == expected_sha
    output_path_checks = path_output_regressions(args.input.resolve(), pages)
    replay = 'skipped-child-test'
    if not args.skip_replay:
        with tempfile.TemporaryDirectory(prefix='hlm-public-replay-') as tmp:
            root = Path(tmp)
            scripts = root/'scripts'
            scripts.mkdir()
            inputs = root/'data/hongloumeng/first80-public'
            inputs.mkdir(parents=True)
            for name in ('build_hongloumeng_reading.py','test_hongloumeng_reading.py','web_analytics.py'):
                shutil.copyfile(Path(__file__).parent/name, scripts/name)
            for name in ('reading.zh.json','manifest.json', *renderer.ASSET_HASHES):
                (inputs/name).parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(args.input/name, inputs/name)
            output = root/'data/hongloumeng/first80/qa/preview'
            build = subprocess.run([sys.executable,'-B',str(scripts/'build_hongloumeng_reading.py'),'--mode','draft','--output',str(output)],capture_output=True,text=True)
            assert build.returncode == 0, build.stdout+build.stderr
            run = subprocess.run([sys.executable,'-B',str(scripts/'test_hongloumeng_reading.py'),'--output',str(output),'--skip-replay'],capture_output=True,text=True)
            assert run.returncode == 0, run.stdout+run.stderr
            for name,text in pages.items():
                assert (output/name).read_bytes() == renderer.as_bytes(text), 'Isolated replay differs: '+name
            blocked = subprocess.run([sys.executable,'-B',str(scripts/'build_hongloumeng_reading.py'),'--mode','release','--output',str(root/'data/hongloumeng/first80/qa/must-not-exist')],capture_output=True,text=True)
            expected_refusal = 'text is not finalized' if manifest['status'] != 'finalized' else 'explicit hash-bound approval required'
            assert blocked.returncode != 0 and expected_refusal in blocked.stderr
            assert not (root/'data/hongloumeng/first80/qa/must-not-exist').exists()
            missing_mode = subprocess.run([sys.executable,'-B',str(scripts/'build_hongloumeng_reading.py'),'--output',str(root/'data/hongloumeng/first80/qa/must-not-exist')],capture_output=True,text=True)
            assert missing_mode.returncode != 0 and not (root/'data/hongloumeng/first80/qa/must-not-exist').exists()
            approval = root/'release-approval.json'
            data = dict(action='publish-hongloumeng-first80',text_version=finalized['text_version'],reading_sha256=finalized['reading_sha256'],body_sha256=finalized['body_sha256'],boundaries_finalized=True,approved=True,assets_sha256=finalized['build']['assets_sha256'])
            approval.write_text(json.dumps(data))
            renderer.release_gate(finalized, approval)
            data['body_sha256']='0'*64
            approval.write_text(json.dumps(data))
            rejected(lambda: renderer.release_gate(finalized, approval))
            data['body_sha256']=finalized['body_sha256']
            data['assets_sha256']='0'*64
            approval.write_text(json.dumps(data))
            rejected(lambda: renderer.release_gate(finalized, approval))
            font=inputs/'fonts/nd-hlm-24aeb.woff2'
            font.write_bytes(font.read_bytes()+b'corrupt')
            rejected(lambda: renderer.load_assets(inputs))
            replay = f'passed: clean tree contains only public input/font assets, new renderer/test and web_analytics.py; {len(pages)} byte-identical outputs'
    report = dict(status='passed', mode='draft', chapter_count=80, html_count=82, output_file_count=len(pages), character_count=manifest['character_count'], layout_group_count=manifest['layout_group_count'], diagram_line_count=manifest['diagram_line_count'], reading_sha256=manifest['reading_sha256'], body_sha256=manifest['body_sha256'], assets_sha256=manifest['build']['assets_sha256'], font_assets=renderer.ASSET_HASHES, independent_replay=replay, privacy_allowlist='passed', navigation_links='passed', output_path_checks=output_path_checks, release_gate='passed; draft refused before output; missing and mismatched approvals refused', release_html='canonical and analytics checked in memory only', chapters=chapters)
    if args.report:
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    print(f'PASS output preflight: {len(output_path_checks)} negative path checks; every sentinel and directory entry unchanged')
    print(f"PASS public-only reading: 80 chapter hashes, 82 HTML, {manifest['layout_group_count']} layout groups, 8 diagram lines; "+replay)


if __name__ == '__main__':
    main()
