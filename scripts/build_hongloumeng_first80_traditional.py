#!/usr/bin/env python3
"""Rebuild the frozen Traditional edition from the finalized public Simplified text.

No external converter, network, private editorial input or platform-specific API is
used by this build. The source-bound character table and contextual exceptions are
an edition artifact, not a general-purpose Simplified-to-Traditional converter.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/hongloumeng/first80-public'
SOURCE_SHA = 'feb85ce4efd6219c5e3c3b168935ac1f612e1abac88b7c6369cbeb084f7e33d0'
MANIFEST_SHA = 'af42240acc73e9fa94388c01da680a6b90ecc37f084d6a951b77e42282cfea5f'
BODY_SHA = '364fe7e83f67dc46c1d542ffb600dbd5c6e0038f7fe69e3ea6fdc97231530559'


def sha(value: bytes | str) -> str:
    return hashlib.sha256(value.encode('utf-8') if isinstance(value, str) else value).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def is_cjk(value):
    return len(value) == 1 and ("\u3400" <= value <= "\u4dbf" or "\u4e00" <= value <= "\u9fff")


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def load_source(data=DATA):
    raw = (data / 'reading.zh.json').read_bytes()
    manifest = (data / 'manifest.json').read_bytes()
    require(sha(raw) == SOURCE_SHA, 'Simplified reading source hash mismatch')
    require(sha(manifest) == MANIFEST_SHA, 'Simplified manifest hash mismatch')
    source = json.loads(raw)
    body = ''.join(b['text'] for ch in source['chapters'] for b in ch['blocks'])
    require(sha(body) == BODY_SHA, 'Simplified body hash mismatch')
    return source, json.loads(manifest)


def apply_rules(source, rules):
    require(sha(encoded(source)) == SOURCE_SHA, 'In-memory Simplified source hash mismatch')
    require(rules['source_sha256'] == SOURCE_SHA, 'Conversion source mismatch')
    require(rules['source_manifest_sha256'] == MANIFEST_SHA, 'Conversion manifest mismatch')
    require(rules['schema_version'] == 1, 'Unknown conversion schema')
    require(rules['status'] in ('review-in-progress', 'reviewed'), 'Unknown conversion status')
    mapping = rules['characters']
    require(all(is_cjk(k) and is_cjk(v) for k, v in mapping.items()), 'Not a single-codepoint CJK character mapping')
    result = copy.deepcopy(source)
    units = {(0, 'title'): (source['title'], result)}
    for sch, tch in zip(source['chapters'], result['chapters']):
        n = sch['number']
        units[n, 'title'] = (sch['title'], tch)
        for i, (sb, tb) in enumerate(zip(sch['blocks'], tch['blocks'])):
            units[n, i] = (sb['text'], tb)
    translated = {key: list(''.join(mapping.get(c, c) for c in value[0])) for key, value in units.items()}
    seen = set()
    for entry in rules['exceptions']:
        n, block, offset = entry['chapter'], entry['block'], entry['offset']
        key = (n, block)
        address = (n, block, offset)
        require(address not in seen, f'Duplicate exception: {address}')
        seen.add(address)
        require(key in units, f'Invalid exception unit: {key}')
        original = units[key][0]
        require(type(offset) is int and 0 <= offset < len(original), f'Invalid exception offset: {address}')
        require(original[offset] == entry['source'], f'Exception source mismatch: {address}')
        require(sha(original) == entry['unit_sha256'], f'Exception context hash mismatch: {address}')
        require(is_cjk(entry['target']) and bool(entry['reason']), f'Invalid exception: {address}')
        require(translated[key][offset] != entry['target'], f'Redundant exception: {address}')
        translated[key][offset] = entry['target']
    for key, (original, container) in units.items():
        target = ''.join(translated[key])
        require(len(target) == len(original), f'Character count changed: {key}')
        # Layout, punctuation, whitespace, ASCII and supplementary characters are
        # not editorial choices in this script-only edition.
        for a, b in zip(original, target):
            if not is_cjk(a):
                require(a == b, f'Non-CJK or supplementary character changed: {key}: {a!r}')
        container['title' if key[1] == 'title' else 'text'] = target
    result['language'] = 'zh-Hant'
    return result


def outputs(data=DATA):
    source, manifest = load_source(data)
    rules = json.loads((data / 'conversion.zh-hant.json').read_text())
    target = apply_rules(source, rules)
    manifest = copy.deepcopy(manifest)
    manifest['status'] = 'finalized' if manifest['status'] == 'finalized' and rules['status'] == 'reviewed' else 'draft'
    manifest['text_version'] += '-zh-hant'
    manifest['reading_sha256'] = sha(encoded(target))
    manifest['body_sha256'] = sha(''.join(b['text'] for ch in target['chapters'] for b in ch['blocks']))
    for ch, record in zip(target['chapters'], manifest['chapters']):
        body = ''.join(b['text'] for b in ch['blocks'])
        require(len(body) == record['character_count'], 'Chapter character count changed')
        require(len(ch['blocks']) == record['block_count'], 'Chapter block count changed')
        record['body_sha256'] = sha(body)
    return {'reading.zh-hant.json': encoded(target), 'manifest.zh-hant.json': encoded(manifest)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = outputs()
    stale = [name for name, text in result.items() if not (DATA / name).exists() or (DATA / name).read_text() != text]
    if args.check:
        require(not stale, f'Stale Traditional output: {stale}')
    else:
        for name in stale:
            (DATA / name).write_text(result[name])
    print(('Checked' if args.check else 'Built') + ' 80 Traditional chapters; frozen Simplified source unchanged.')


if __name__ == '__main__':
    main()
