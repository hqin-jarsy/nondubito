"""Print the explicit chapter-84 publication patch; received files stay immutable.

Run once after importing the package's non-HTML source files. No prose is
shortened or regenerated here. The package Chinese is the author-approved base.
"""
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/originals/hongloumeng'
RECEIVED = DATA / 'translations/received/ch084'
DATE = '2026-11-03'
FIXES = {
    'de': [
        ('von den anderen abgewandt', 'von den anderen unbemerkt', '背着人 means out of sight, not a specified posture.'),
        ('mit den Sänften, in denen die Aussteuer getragen wurde', 'mit der Sänfte, in der die Aussteuer getragen wurde', 'Preserve the singular dowry sedan.'),
        ('Kleider, Getreide und Reis', 'Kleider und Reisvorräte', '粮米 does not specify two separate commodities.'),
    ],
    'en': [('Everyone outside knows by now:', "Word’s all over the place now:", 'Preserve the status of hearsay in Xue Pan’s speech.')],
    'es': [('Fuera ya lo sabe todo el mundo:', 'Fuera ya corre la voz:', 'Preserve the status of hearsay in Xue Pan’s speech.')],
    'ja': [('人に背を向けて', '人目を避けて', '背着人 means out of sight, not a specified posture.')],
    'ko': [('사람들에게 등을 돌린 채', '남들 눈에 띄지 않게', '背着人 means out of sight, not a specified posture.')],
}


def main():
    patch = ['*** Begin Patch']

    def update(path, content):
        if path.exists():
            patch.append('*** Update File: ' + str(path))
            patch.extend('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(path.read_text().splitlines(), content.splitlines(), n=2, lineterm=''))[2:])
        else:
            patch.append('*** Add File: ' + str(path))
            patch.extend('+' + line for line in content.splitlines())

    corrections = json.loads((DATA / 'translations/corrections.json').read_text())
    assert not any(x['chapter'] == 'ch084' for x in corrections), 'Already prepared'
    for lang, fixes in FIXES.items():
        text = (RECEIVED / 'text' / (lang + '.md')).read_text()
        for before, after, reason in fixes:
            assert text.count(before) == 1, (lang, before)
            corrections.append(dict(chapter='ch084', language=lang, before=before, after=after, count=1, reason=reason))
            text = text.replace(before, after)
    update(DATA / 'translations/corrections.json', json.dumps(corrections, ensure_ascii=False, indent=2) + '\n')
    raw = (RECEIVED / 'text/zh-Hans.md').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '82cf09b0499232535f04cb2c6f19b5a4de50964cdec708a28d96bd36546b9a48'
    assert raw.startswith(b'# ')
    original = raw[2:].rstrip(b'\n') + b'\n'
    update(DATA / 'ch084.zh.txt', original.decode())
    record = json.loads((DATA / 'publication.json').read_text())
    record['published_chapters'].append(84)
    record['chapter_sources']['ch084'] = {
        'source': 'ch084.zh.txt', 'source_sha256': hashlib.sha256(original).hexdigest(),
        'source_bytes': len(original), 'received_sha256': hashlib.sha256(raw).hexdigest(),
        'modified': DATE, 'paragraphs': 51, 'source_filename': 'text/zh-Hans.md',
        'note': 'Author-approved Chinese from the supplied chapter-84 package. Only the initial Markdown title marker removed and one terminal newline added; wording, punctuation and paragraph boundaries retained. Package claims about earlier drafts are retained as received, not independently authenticated.'}
    receipt = record['multilingual_publication']
    files = sorted(p for p in RECEIVED.rglob('*') if p.is_file())
    assert len(files) == 32 and not any(p.suffix == '.html' for p in files)
    for path in files:
        receipt['received_files'][str(path.relative_to(DATA))] = hashlib.sha256(path.read_bytes()).hexdigest()
    package = Path('/Users/hanqin/Documents/SAE旗舰系列多语言/大知续红楼梦/Hongloumeng_Ch084_8Languages_v0.1_20261102.zip')
    receipt['source_packages']['ch084'] = dict(filename=package.name, sha256=hashlib.sha256(package.read_bytes()).hexdigest())
    record['chapter_publications']['ch084'] = {
        'published': DATE, 'languages': record['editions'], 'source': 'translations/received/ch084',
        'text_layout': 'text/{language}.md', 'continuity': 'translations/continuity.json',
        'note': '51 complete narrative paragraphs, no closing verse. Seven local foreign-text corrections; Chinese wording and chapter 81–83 narrative text retained. Incoming Traditional text archived; public Traditional edition follows the existing script-conversion policy.'}
    record['checks'] = [
        'Frozen Chinese chapter 81–83 manuscripts and all previously published narrative text retained',
        'Chapter 84 equals the supplied Simplified manuscript except its Markdown title marker and terminal newline',
        'All received source, notes and terminology hashes verified',
        '40 reading and collection pages: eight languages, four chapters, complete body units',
        'Chapter 84: 51 paragraphs, no fabricated closing verse; seven exact local corrections',
        'Naming continuity retained; hearsay and the unnamed bride remain unresolved',
        'No link to unpublished chapter 85; reciprocal hreflang and same-language navigation',
        'Search, sitemap, Latest and Cloudflare analytics checked',
        'Existing character essays and reader essays unchanged',
    ]
    update(DATA / 'publication.json', json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print('\n'.join(patch + ['*** End Patch']))


if __name__ == '__main__':
    main()
