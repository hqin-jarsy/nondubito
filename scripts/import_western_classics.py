#!/usr/bin/env python3
"""One-time, lossless paragraph import of the author's two Western classics.

Only Markdown emphasis is removed; SAE asides are separated for optional display.
Never overwrite existing editorial files or change the external manuscripts.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'sae-descartes': ('claude_SAE沉思集-发布本-合订.md', 7),
    'sae-spinoza': ('claude_SAE伦理学-发布本-合订.md', 11),
}

def parse(text):
    entries = []
    for number, block in enumerate(re.split(r'(?m)^## ', text)[1:]):
        title, _, body = block.partition('\n')
        sections = []
        section = {'heading': '', 'paragraphs': []}
        aside = ''
        for para in re.split(r'\n\s*\n', body.strip()):
            para = para.strip()
            if para == '---':
                continue
            if para.startswith('### '):
                if section['paragraphs']:
                    sections.append(section)
                section = {'heading': para[4:], 'paragraphs': []}
            elif para.startswith('> **旁注。**'):
                assert not aside
                aside = para.removeprefix('> **旁注。**').strip().replace('**', '')
            else:
                section['paragraphs'].append(para.replace('**', ''))
        if section['paragraphs']:
            sections.append(section)
        copy = {'title': title, 'deck': '', 'sections': sections, 'notes': []}
        if aside:
            copy['aside'] = aside
        entries.append({'number': number, 'slug': 'intro' if number == 0 else f'ep{number:02}',
                        'zh': copy, 'sources': [], 'editorial': {'zh_edits': [], 'coverage': []}})
    return entries

def main():
    folder = Path('/Users/hanqin/Documents/SAE西哲')
    receipt = {}
    for slug, (filename, count) in SOURCES.items():
        source = folder / filename
        text = source.read_text()
        entries = parse(text)
        assert len(entries) == count
        dest = ROOT / 'data' / slug
        assert not dest.exists(), f'Never overwrite editorial work: {dest}'
        dest.mkdir()
        for entry in entries:
            (dest / f'{entry["number"]:02}.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2)+'\n')
        receipt[slug] = {'source': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                         'entries': [{ 'number': e['number'], 'sections': len(e['zh']['sections']),
                            'paragraphs': sum(len(s['paragraphs']) for s in e['zh']['sections']),
                            'original_zh': e['zh']} for e in entries]}
    out = ROOT / 'data/western-classics-received.json'
    assert not out.exists()
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print('Imported 18 complete Chinese reading units; originals untouched.')

if __name__ == '__main__':
    main()
