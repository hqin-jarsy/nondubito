#!/usr/bin/env python3
"""One-time, auditable import of the author's 2026-10-01 Emperor manuscripts.

No translation service. ZIPs are read-only. All replacements are exact-match,
reviewed edits, including explicitly authorized corrections of the ZH/EN lock.
Run without --apply to validate the complete transaction before writing it.
"""
import argparse
import hashlib
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile

import markdown
from build_emperor_full_editions import DATA, ROOT, ORIGINAL_MARKER

RECEIPT = DATA / 'new-edition-review.json'
PLAN = DATA / 'new-edition-copyedits.json'
LANGS = ('de', 'fr', 'es', 'ja', 'ko')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def structure(markup):
    """Count top-level prose/list blocks per heading, excluding nested <p>."""
    class Blocks(HTMLParser):
        def __init__(self):
            super().__init__()
            self.counts = [0]
            self.block = None

        def handle_starttag(self, tag, attrs):
            if tag in ('h2', 'h3'):
                self.counts.append(0)
            if tag in ('p', 'li') and self.block is None:
                self.block = tag
                self.counts[-1] += 1

        def handle_endtag(self, tag):
            if tag == self.block:
                self.block = None
    parser = Blocks()
    parser.feed(markup)
    return parser.counts


def prepare(folder):
    if RECEIPT.exists():
        raise ValueError('Already imported; edit checked-in sources, never reimport over reviewed prose')
    plan = json.loads(PLAN.read_text())
    baseline_path = DATA / 'original-zh-en.json'
    baseline_raw = baseline_path.read_text()
    baseline = json.loads(baseline_raw)
    receipt = dict(date='2026-10-01',
        baseline_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        authorization=plan['authorization'],
        scope='Full structural verification and targeted editorial review; not an exhaustive new historical audit.',
        copyedits_sha256=sha(PLAN.read_bytes()), archives={}, manuscripts={}, source_corrections=[])
    pending = {}
    for number in range(1, 26):
        ep = f'ep{number:02}'
        original = (DATA / f'{ep}.zh.md').read_text().split(ORIGINAL_MARKER)[1].strip()
        expected = structure(original)
        archive = folder / f'NonDubito_Emperor_EP{number:02}_DE_FR_ES_JA_KO_v1.0.zip'
        with ZipFile(archive) as zipped:
            assert zipped.testzip() is None, archive
            receipt['archives'][ep] = dict(name=archive.name, sha256=sha(archive.read_bytes()),
                notes={n:zipped.read(n).decode('utf-8-sig') for n in zipped.namelist() if n.endswith('notes.md')})
            for lang in LANGS:
                names = [n for n in zipped.namelist() if n.endswith('_'+lang+'.md')]
                assert len(names) == 1, (ep, lang)
                raw = zipped.read(names[0])
                submitted = raw.decode('utf-8-sig')
                parts = submitted.split('\n---\n')
                assert len(parts) == 3, (ep, lang, 'ambiguous manuscript boundaries')
                title = re.match(r'# (.+)', parts[0])[1].strip()
                body = parts[1].strip()
                assert structure(markdown.markdown(body)) == expected, (ep, lang, 'incomplete received body')
                changes = []
                for edit in plan['edits']:
                    if (edit['ep'], edit['lang']) == (ep, lang):
                        assert body.count(edit['before']) == 1, edit
                        body = body.replace(edit['before'], edit['after'])
                        changes.append(edit)
                assert structure(markdown.markdown(body)) == expected, (ep, lang, 'edit changed paragraph boundaries')
                text = '# '+title+'\n\n'+body+'\n'
                key = ep+'.'+lang
                receipt['manuscripts'][key] = dict(title=title, received_sha256=sha(raw),
                    published_sha256=sha(text.encode()), blocks_by_section=expected,
                    edits=changes, removed_preface=parts[0], removed_footer=parts[2])
                pending[DATA / (key+'.md')] = text
    for ep in baseline['editions']:
        for lang in ('zh', 'en'):
            path = DATA / f'{ep}.{lang}.md'
            before = path.read_text()
            original_body = before.split(ORIGINAL_MARKER)[1].strip()
            assert sha(original_body.encode()) == baseline['editions'][ep][lang]['body_sha256'], path
            after = before
            changes = []
            for edit in plan['edits']:
                if (edit['ep'], edit['lang']) == (ep, lang):
                    assert after.count(edit['before']) == 1, edit
                    after = after.replace(edit['before'], edit['after'])
                    changes.append(edit)
            if after != before:
                body = after.split(ORIGINAL_MARKER)[1].strip()
                assert structure(body) == structure(original_body), (path, 'original structure changed')
                baseline['editions'][ep][lang]['body_sha256'] = sha(body.encode())
                pending[path] = after
                receipt['source_corrections'].append(dict(ep=ep,lang=lang,
                    before_sha256=sha(before.encode()), after_sha256=sha(after.encode()), edits=changes))
    baseline['editorial_revision'] = dict(date='2026-10-01',
        approval=plan['authorization'], log='new-edition-review.json',
        original_snapshot='original-zh-en-2026-09-25.json')
    pending[DATA/'original-zh-en-2026-09-25.json'] = baseline_raw
    pending[baseline_path] = json.dumps(baseline, ensure_ascii=False, indent=2)+'\n'
    pending[RECEIPT] = json.dumps(receipt, ensure_ascii=False, indent=2)+'\n'
    return pending, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    pending, receipt = prepare(args.folder)
    if args.apply:
        for path, text in pending.items():
            path.write_text(text)
    print(('Imported' if args.apply else 'Validated')+f" {len(receipt['manuscripts'])} manuscripts; "
          f"{len(receipt['source_corrections'])} original-language files have logged local corrections")


if __name__ == '__main__':
    main()
