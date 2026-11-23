#!/usr/bin/env python3
"""Apply/check the current Duo nickname at the public-reader layer.

The first80 source files, historical review snapshots, and sealed translation
bindings must remain unchanged. After regenerating/reinstalling the affected
reader chapters from those baselines, rerun this overlay with --write.
"""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / 'classics/hongloumeng'
PROSE = re.compile(r'(<p\b[^>]*\bclass="prose"[^>]*>)(.*?)(</p>)', re.S)
# The crowd's spoken nickname keeps its rhotic ending; the narrator does not.
SPOKEN = {
    'ch021.html': ('众人都呼他作', '儿'),
    'zh-hant/ch021.html': ('眾人都呼他作', '兒'),
}
EDITS = {
    'ch077.html': [('多浑虫灯姑娘儿的便是了', '多浑虫和多姑娘了', 1), ('灯姑娘', '多姑娘', 4)],
    'zh-hant/ch077.html': [('多渾蟲燈姑娘兒的便是了', '多渾蟲和多姑娘了', 1), ('燈姑娘', '多姑娘', 4)],
    'ja/ch077.html': [('灯姑娘', '多姑娘', 5)],
    'fr/ch077.html': [('la Dame Deng, appelée aussi la demoiselle Duo', 'la demoiselle Duo', 1),
                     ('la Dame Deng', 'la demoiselle Duo', 1), ('La Dame Deng', 'La demoiselle Duo', 1)],
    'de/ch077.html': [('die Frau Deng', 'Duoguniang', 1), ('Die Frau Deng', 'Duoguniang', 4)],
    'es/ch077.html': [('la muchacha Deng, a quien allí conocimos como la muchacha Duo', 'la muchacha Duo', 1),
                     ('la muchacha Deng', 'la muchacha Duo', 1), ('La muchacha Deng', 'La muchacha Duo', 3)],
    'ko/ch077.html': [('등고낭이', '다 낭자가', 2), ('등고낭은', '다 낭자는', 2), ('등고낭도', '다 낭자도', 1)],
}
NAMES = {'': '多姑娘', 'zh-hant': '多姑娘', 'ja': '多姑娘', 'en': 'Mrs Duo',
         'fr': 'demoiselle Duo', 'de': 'Duoguniang', 'es': 'muchacha Duo', 'ko': '다 낭자'}


def prose(html):
    return '\n'.join(m[2] for m in PROSE.finditer(html))


def chapter21(name, text):
    intro, suffix = SPOKEN[name]
    spoken = f'{intro}“多姑娘{suffix}”'
    uninflected = f'{intro}“多姑娘”'
    narrator = '那多姑娘'
    body = prose(text)
    if body.count(spoken) + body.count(uninflected) != 1 or body.count(narrator) != 1:
        raise ValueError(f'{name}: expected a quoted nickname and its narrator reference')
    def replace(match):
        value = match[2].replace(uninflected, spoken).replace(narrator + suffix, narrator)
        return match[1] + value + match[3]
    result = PROSE.sub(replace, text)
    if prose(result).count('多姑娘' + suffix) != 1:
        raise ValueError(f'{name}: rhotic ending outside the quoted nickname')
    return result


def edited(name, text):
    if name in SPOKEN:
        return chapter21(name, text)
    pairs = EDITS[name]
    before = prose(text)
    if not any(old in before for old, _, _ in pairs):
        return text
    remaining = before
    for old, new, count in pairs:
        if remaining.count(old) != count:
            raise ValueError(f'{name}: unexpected nickname context or count for {old!r}')
        remaining = remaining.replace(old, new)
    def replace(match):
        value = match[2]
        for old, new, _ in pairs:
            value = value.replace(old, new)
        return match[1] + value + match[3]
    return PROSE.sub(replace, text)


def validate(root, results):
    for language, preferred in NAMES.items():
        for chapter in (21, 77):
            name = '/'.join(x for x in (language, f'ch{chapter:03d}.html') if x)
            html = results[name] if name in results else (root / name).read_text(encoding='utf-8')
            body = prose(html)
            floor = 2 if chapter == 21 else 3 if language == 'fr' else 5 if language != 'en' else 4
            if body.casefold().count(preferred.casefold()) < floor:
                raise ValueError(f'{name}: preferred nickname missing from the chapter prose')
            if name in SPOKEN and chapter21(name, html) != html:
                raise ValueError(f'{name}: narration and quotation are not distinguished')
            if any(old in body for old, _, _ in EDITS.get(name, [])):
                raise ValueError(f'{name}: superseded nickname remains in the chapter prose')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    pages = (*SPOKEN, *EDITS)
    originals = {name: (ROOT / name).read_text(encoding='utf-8') for name in pages}
    planned = {name: edited(name, html) for name, html in originals.items()}
    validate(ROOT, planned)
    changed = [name for name in pages if originals[name] != planned[name]]
    if changed and not args.write:
        raise SystemExit(f'Nickname overlay missing: {", ".join(changed)}')
    for name in changed:
        (ROOT / name).write_text(planned[name], encoding='utf-8')
    print(f'Duo nickname checked in both chapters across eight languages; {len(changed)} pages updated.')


if __name__ == '__main__':
    main()
