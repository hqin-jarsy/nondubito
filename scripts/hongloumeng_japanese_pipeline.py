#!/usr/bin/env python3
"""Validate complete Japanese draft/source alignment and render private review copies.

No publication, network operation, or promotion to accepted status occurs here.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/hongloumeng/first80-public/reading.zh.json'
DATA = ROOT / 'data/hongloumeng/first80-japanese'


def source_hash(chapter):
    return hashlib.sha256(json.dumps(chapter, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def validate(chapter, draft):
    n = chapter['number']
    if draft.get('schemaVersion') != 1 or draft.get('language') != 'ja' or draft.get('number') != n:
        raise ValueError(f'Chapter {n}: incorrect identity')
    if draft.get('sourceSha256') != source_hash(chapter) or draft.get('sourceTitle') != chapter['title']:
        raise ValueError(f'Chapter {n}: source changed')
    if not isinstance(draft.get('title'), str) or not draft['title'].strip():
        raise ValueError(f'Chapter {n}: missing title')
    blocks = draft.get('blocks', [])
    if len(blocks) != len(chapter['blocks']):
        raise ValueError(f'Chapter {n}: block count differs')
    for i, (source, translated) in enumerate(zip(chapter['blocks'], blocks), 1):
        if translated.get('sourceText') != source['text']:
            raise ValueError(f'Chapter {n} block {i}: source text differs')
        for key in set(source) - {'text'}:
            if translated.get(key) != source.get(key):
                raise ValueError(f'Chapter {n} block {i}: {key} differs')
        text = translated.get('text')
        if not isinstance(text, str) or not text.strip() or '\ufffd' in text:
            raise ValueError(f'Chapter {n} block {i}: blank or damaged translation')
        if text == source['text']:
            raise ValueError(f'Chapter {n} block {i}: untranslated source copy')
    if not isinstance(draft.get('notes', []), list):
        raise ValueError(f'Chapter {n}: notes must be a list')
    return {'chapter': n, 'blocks': len(blocks),
            'sourceSha256': source_hash(chapter),
            'translationCharacters': sum(len(b['text']) for b in blocks),
            'status': 'structurally_validated_not_literary_acceptance'}


def validate_partial(chapter, draft):
    """Validate only recorded excerpts, never certify a complete translation."""
    n = chapter['number']
    if draft.get('schemaVersion') != 1 or draft.get('language') != 'ja' or draft.get('number') != n:
        raise ValueError(f'Chapter {n}: incorrect identity')
    if draft.get('sourceSha256') != source_hash(chapter):
        raise ValueError(f'Chapter {n}: source changed')
    omitted = draft.get('omittedSourceBlockIndices', draft.get('withheldBlockIndices', []))
    if isinstance(omitted, list):
        omitted = omitted + draft.get('partialSourceBlockIndices', draft.get('partiallyTranslatedSourceBlockIndices', []))
    if not isinstance(omitted, list) or not omitted or len(set(omitted)) != len(omitted):
        raise ValueError(f'Chapter {n}: explicit unique omission indices required')
    if any(type(i) is not int or not 0 <= i < len(chapter['blocks']) for i in omitted):
        raise ValueError(f'Chapter {n}: invalid omission index')
    if 'partial' not in draft.get('status', '') or draft.get('complete') is True:
        raise ValueError(f'Chapter {n}: partial status required')
    seen = set()
    translated_count = 0
    segmented_count = 0
    owner_ranges = []
    for position, b in enumerate(draft['blocks']):
        i = b.get('sourceIndex', b.get('sourceBlockIndex', position))
        if type(i) is not int or i in seen or not 0 <= i < len(chapter['blocks']):
            raise ValueError(f'Chapter {n}: duplicate or invalid source index')
        seen.add(i)
        source = chapter['blocks'][i]
        for key in set(source) - {'text'}:
            if b.get(key) != source[key]:
                raise ValueError(f'Chapter {n} block {i}: {key} differs')
        if 'sourceSegments' in b:
            if i not in omitted or 'sourceText' in b or 'text' in b:
                raise ValueError(f'Chapter {n}: segmented block must be explicitly partial')
            offset = 0
            has_gap = False
            for segment in b['sourceSegments']:
                start, end = segment.get('start'), segment.get('end')
                if type(start) is not int or type(end) is not int or start != offset or not start < end <= len(source['text']):
                    raise ValueError(f'Chapter {n} block {i}: noncontiguous segment range')
                original = source['text'][start:end]
                if segment.get('status') == 'owner_translation_needed':
                    if 'sourceText' in segment or 'text' in segment or segment.get('sourceTextSha256') != hashlib.sha256(original.encode()).hexdigest():
                        raise ValueError(f'Chapter {n} block {i}: invalid owner-only segment')
                    has_gap = True
                    owner_ranges.append({'sourceBlockIndex': i, 'start': start, 'end': end})
                else:
                    if segment.get('sourceText') != original or not isinstance(segment.get('text'), str) or not segment['text'].strip():
                        raise ValueError(f'Chapter {n} block {i}: segment text differs or translation missing')
                offset = end
            if offset != len(source['text']) or not has_gap:
                raise ValueError(f'Chapter {n} block {i}: incomplete or falsely partial segmentation')
            segmented_count += 1
            continue
        if i in omitted:
            if 'sourceText' in b or 'text' in b:
                raise ValueError(f'Chapter {n}: withheld block contains text')
            expected = hashlib.sha256(source['text'].encode()).hexdigest()
            if (b.get('sourceTextSha256') is not None and b['sourceTextSha256'] != expected) or (b.get('sourceTextSha256') is None and b.get('omitted') is not True):
                raise ValueError(f'Chapter {n}: withheld block hash differs')
            continue
        if b.get('sourceText') != source['text']:
            raise ValueError(f'Chapter {n} block {i}: source differs')
        for key in set(source) - {'text'}:
            if b.get(key) != source[key]:
                raise ValueError(f'Chapter {n} block {i}: {key} differs')
        if not isinstance(b.get('text'), str) or not b['text'].strip() or '\ufffd' in b['text']:
            raise ValueError(f'Chapter {n} block {i}: missing or damaged translation')
        translated_count += 1
    expected = set(range(len(chapter['blocks']))) - set(omitted)
    if seen - set(omitted) != expected:
        raise ValueError(f'Chapter {n}: excerpt coverage differs')
    return {'chapter': n, 'blocks': translated_count, 'omittedBlockIndices': omitted,
            'sourceSha256': source_hash(chapter), 'partiallyTranslatedBlocks': segmented_count,
            'ownerTranslationRanges': owner_ranges, 'status': 'partial_alignment_validated_not_complete'}


def render(draft):
    e = html.escape
    body = []
    for i, block in enumerate(draft['blocks'], 1):
        body.append(f'<section id="b{i}" data-source-block="{i}"><p class="label">{i} · {e(block["kind"])}</p>'
                    f'<div class="ja" lang="ja">{e(block["text"]).replace(chr(10), "<br>")}</div>'
                    f'<details><summary>中国語原文</summary><p lang="zh-Hans">{e(block["sourceText"]).replace(chr(10), "<br>")}</p></details></section>')
    notes = ''.join('<li>'+e(n if isinstance(n, str) else json.dumps(n, ensure_ascii=False))+'</li>' for n in draft.get('notes', []))
    return ('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow"><title>'+e(draft['title'])+'</title>'
            '<style>body{margin:2em auto;max-width:46em;padding:0 1.3em;background:#fcfaf4;color:#272522;font:18px/1.95 serif}'
            'h1{font-size:1.5em;line-height:1.7}section{margin:1.5em 0}.label,summary{font-size:.75em;color:#71695e}.ja{white-space:normal}'
            'details{margin-top:.4em}details p{font-size:.9em}li{margin:1em 0}a{color:#65442d}</style>'
            '<p>前八十回・日本語翻訳　非公開の校閲用原稿</p><h1>'+e(draft['title'])+'</h1>'
            +''.join(body)+(('<h2>注記</h2><ol>'+notes+'</ol>') if notes else '')+'</html>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', type=int, required=True)
    parser.add_argument('--end', type=int, required=True)
    parser.add_argument('--render-private', action='store_true')
    parser.add_argument('--allow-partial', action='store_true', help='Validate explicit excerpt coverage; never mark complete')
    args = parser.parse_args()
    if not 1 <= args.start <= args.end <= 80:
        parser.error('Expected chapter range within 1–80')
    source = json.loads(SOURCE.read_text())['chapters']
    results = []
    for n in range(args.start, args.end+1):
        path = DATA / 'chapters' / f'ch{n:03}.draft.json'
        partial = False
        if not path.exists() and args.allow_partial:
            candidates = [p for p in (path.with_name(f'ch{n:03}.partial.json'), path.with_name(f'ch{n:03}.excerpt.json')) if p.exists()]
            if len(candidates) != 1:
                raise ValueError(f'Chapter {n}: expected one partial file')
            path = candidates[0]
            partial = True
        draft = json.loads(path.read_text())
        results.append((validate_partial if partial else validate)(source[n-1], draft))
        if args.render_private and partial:
            raise ValueError('Partial chapters are not rendered as complete review pages')
        if args.render_private:
            target = DATA / 'private-review'
            target.mkdir(parents=True, exist_ok=True)
            (target/f'ch{n:03}.html').write_text(render(draft))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
