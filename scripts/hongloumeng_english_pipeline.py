#!/usr/bin/env python3
"""Work-in-progress alignment only. No HTML renderer or publication operation."""
import argparse
from collections import Counter
import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/hongloumeng/first80-english'
SOURCE = ROOT / 'data/hongloumeng/first80-public'
STANDARD = ROOT / 'docs/hongloumeng/translation'
VERSION = 'english-1-110-v0.6'
READING_SHA = '7454b775774692fd199302d8b68fec8f5d7f22f7823cd06d44bdac98b051aa21'
MANIFEST_SHA = 'cb6845224b3f02b82c1b5d1962184c57ce9c623aed996a13313af02a1eacb3b8'
BODY_SHA = 'ed46c59a19ff5960940a26bee1634f6ccd6cc85fc2fdcd555123427ba4b87bf5'
REVIEW_TYPES = ('bilingual', 'literary', 'consistency')
STATES = ('pending', 'draft', 'reviewed', 'accepted')


def sha(value):
    return hashlib.sha256(value.encode('utf-8') if isinstance(value, str) else value).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(obj, expected):
    require(isinstance(obj, dict) and set(obj) == set(expected.split()), 'Unexpected schema fields')


def load_source():
    raw = (SOURCE / 'reading.zh.json').read_bytes()
    manifest = (SOURCE / 'manifest.json').read_bytes()
    require(sha(raw) == READING_SHA and sha(manifest) == MANIFEST_SHA, 'Frozen Chinese source changed')
    reading = json.loads(raw)
    from build_hongloumeng_reading import validate
    validate(reading, json.loads(manifest), raw)
    require(sha(''.join(b['text'] for c in reading['chapters'] for b in c['blocks'])) == BODY_SHA, 'Body checksum differs')
    return reading


def source_map(reading):
    units = []
    for chapter in reading['chapters']:
        n = chapter['number']
        for index, block in enumerate([{'kind': 'title', 'text': chapter['title']}] + chapter['blocks']):
            units.append({'id': f'hlm-c{n:03d}-' + ('title' if index == 0 else f'b{index:04d}'),
                          'chapter': n, 'index': index, 'sourceHash': sha(block['text']),
                          'characterCount': len(block['text']),
                          'layout': {k: v for k, v in block.items() if k != 'text'}})
    return {'schemaVersion': 1, 'sourcePath': 'data/hongloumeng/first80-public/reading.zh.json',
            'sourceHash': READING_SHA, 'manifestHash': MANIFEST_SHA, 'bodyHash': BODY_SHA,
            'units': units}


def initial_progress(mapping):
    return {'schemaVersion': 1, 'status': 'translation-work-in-progress', 'sourceHash': READING_SHA,
            'standardVersion': VERSION,
            'sourceIssues': [],
            'units': [{'id': u['id'], 'sourceHash': u['sourceHash'], 'state': 'pending',
                       'segments': [], 'reviews': []} for u in mapping['units']],
            'checkpoints': [{'first': n, 'last': n + 4, 'state': 'pending', 'corpusHash': None,
                             'standardSnapshot': None, 'reviewReference': None}
                            for n in range(1, 81, 5)]}


def standard_snapshot():
    # Bind the exact normative texts, not merely a version label. Any edit
    # invalidates prior reviews until an actual regression review is recorded.
    names = ('english-standard.md', 'english-terms.json', 'english-voices.json',
             'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'CHANGELOG.md')
    require(all((STANDARD / n).is_file() for n in names), 'Standard baseline is not available')
    return sha(encoded({n: sha((STANDARD / n).read_bytes()) for n in names}))


def content_hash(unit, issues=()):
    relevant = sorted((issue for issue in issues if issue['unitId'] == unit['id']), key=lambda issue: issue['id'])
    return sha(encoded({'id': unit['id'], 'sourceHash': unit['sourceHash'], 'segments': unit['segments'], 'sourceIssues': relevant}))


def batch_hash(units, issues=()):
    return sha(encoded([content_hash(u, issues) for u in units]))


def validate_progress(mapping, progress, snapshot=None):
    keys(progress, 'schemaVersion status sourceHash standardVersion units checkpoints sourceIssues')
    require(progress['schemaVersion'] == 1 and progress['status'] == 'translation-work-in-progress', 'Not a work-in-progress corpus')
    require(progress['sourceHash'] == mapping['sourceHash'] == READING_SHA, 'Wrong source binding')
    require(progress['standardVersion'] == VERSION, 'Wrong standard version')
    require(isinstance(progress['units'], list) and len(progress['units']) == len(mapping['units']), 'Missing or duplicate units')
    require(isinstance(progress['sourceIssues'], list), 'Source issue registry required')
    source_lookup = {u['id']: u for u in mapping['units']}
    issue_ids = set()
    for issue in progress['sourceIssues']:
        keys(issue, 'id unitId sourceHash state description resolution')
        require(isinstance(issue['id'], str) and issue['id'].strip() and issue['id'] not in issue_ids, 'Invalid or duplicate source issue ID')
        issue_ids.add(issue['id'])
        require(issue['unitId'] in source_lookup and issue['sourceHash'] == source_lookup[issue['unitId']]['sourceHash'], 'Source issue has stale source binding')
        require(issue['state'] in ('open', 'resolved'), 'Invalid source issue state')
        require(isinstance(issue['description'], str) and bool(issue['description'].strip()), 'Source issue description required')
        require((issue['state'] == 'open' and issue['resolution'] is None) or
                (issue['state'] == 'resolved' and isinstance(issue['resolution'], str) and bool(issue['resolution'].strip())), 'Resolved issue requires an actual resolution')
    for source, unit in zip(mapping['units'], progress['units']):
        keys(unit, 'id sourceHash state segments reviews')
        require((unit['id'], unit['sourceHash']) == (source['id'], source['sourceHash']), 'Unit missing, duplicated, reordered, or stale')
        require(unit['state'] in STATES, 'Unknown state')
        require(isinstance(unit['segments'], list) and isinstance(unit['reviews'], list), 'Invalid segments/reviews')
        if unit['state'] == 'pending':
            require(not unit['segments'] and not unit['reviews'], 'Pending unit must have no translation or review claims')
            continue
        require(bool(unit['segments']), 'Translated unit is empty')
        for segment in unit['segments']:
            keys(segment, 'kind text')
            require(segment['kind'] == source['layout']['kind'], 'Verse, diagram, or prose kind lost')
            require(isinstance(segment['text'], str) and segment['text'].strip(), 'Empty translated segment')
            require(sha(segment['text']) != source['sourceHash'], 'Chinese source cannot be a translation placeholder')
            require(any(c.isascii() and c.isalpha() for c in segment['text']), 'No English letters; auxiliary check only')
        if source['layout']['kind'] != 'prose':
            require(len(unit['segments']) == 1, 'Preserve each title/poem line/diagram line as one mapped unit')
        seen = set()
        for review in unit['reviews']:
            keys(review, 'type contentHash standardSnapshot reference')
            require(review['type'] in REVIEW_TYPES and review['type'] not in seen, 'Invalid or duplicate review type')
            seen.add(review['type'])
            require(review['contentHash'] == content_hash(unit, progress['sourceIssues']), 'Review is stale after text or source-issue change')
            require(snapshot is not None and review['standardSnapshot'] == snapshot, 'Review is stale after standard change')
            require(isinstance(review['reference'], str) and bool(review['reference'].strip()), 'Review reference required')
        if unit['state'] == 'accepted':
            require(not any(i['unitId'] == unit['id'] and i['state'] == 'open' for i in progress['sourceIssues']), 'Acceptance blocked by open source issue')
        if unit['state'] in ('reviewed', 'accepted'):
            require(seen == set(REVIEW_TYPES), 'Bilingual, literary, and consistency review are all required')
    require(isinstance(progress['checkpoints'], list) and len(progress['checkpoints']) == 16, 'Exactly 16 five-chapter checkpoints required')
    for first, checkpoint in zip(range(1, 81, 5), progress['checkpoints']):
        keys(checkpoint, 'first last state corpusHash standardSnapshot reviewReference')
        require(checkpoint['first'] == first and checkpoint['last'] == first + 4, 'Wrong checkpoint order')
        require(checkpoint['state'] in ('pending', 'accepted'), 'Invalid checkpoint state')
        if checkpoint['state'] == 'pending':
            require(all(checkpoint[k] is None for k in ('corpusHash', 'standardSnapshot', 'reviewReference')), 'Pending checkpoint cannot claim review')
        else:
            units = [u for s, u in zip(mapping['units'], progress['units']) if first <= s['chapter'] <= first + 4]
            require(all(u['state'] == 'accepted' for u in units), 'Batch contains unfinished units')
            require(checkpoint['corpusHash'] == batch_hash(units, progress['sourceIssues']), 'Batch review is stale')
            require(snapshot is not None and checkpoint['standardSnapshot'] == snapshot, 'Batch standard regression review required')
            require(isinstance(checkpoint['reviewReference'], str) and bool(checkpoint['reviewReference'].strip()), 'Batch review reference required')
        if first > 1:
            active = any(u['state'] != 'pending' for s, u in zip(mapping['units'], progress['units']) if first <= s['chapter'] <= first + 4)
            require(not active or progress['checkpoints'][(first - 1) // 5 - 1]['state'] == 'accepted', 'Finish preceding five-chapter quality review before expanding')
    return dict(Counter(u['state'] for u in progress['units']))


def assemble_wip(mapping, progress):
    # Every source location remains explicit, even where translation is absent.
    # These are JSON work records, never a reading edition or website input.
    return {'schemaVersion': 1, 'status': 'translation-work-in-progress', 'language': 'en',
            'publishable': False, 'sourceHash': mapping['sourceHash'],
            'standardVersion': progress['standardVersion'], 'sourceIssues': progress['sourceIssues'],
            'units': [dict(s, translation=u) for s, u in zip(mapping['units'], progress['units'])]}


def validate_reader_notes(mapping, notes):
    keys(notes, 'schemaVersion sourceHash notes')
    require(notes['schemaVersion'] == 1 and notes['sourceHash'] == mapping['sourceHash'], 'Reader notes source binding differs')
    require(isinstance(notes['notes'], list), 'Reader notes must be separate records')
    lookup = {u['id']: u for u in mapping['units']}
    seen = set()
    for note in notes['notes']:
        keys(note, 'unitId sourceHash glossaryId type text presentationStatus')
        require(note['unitId'] in lookup and note['unitId'] not in seen, 'Invalid or duplicate reader-note unit')
        seen.add(note['unitId'])
        require(note['sourceHash'] == lookup[note['unitId']]['sourceHash'], 'Reader note unit source binding differs')
        require(note['type'] == 'translator_note' and note['presentationStatus'] == 'not_integrated_in_reading_presentation', 'Reader note must remain separately labelled')
        require(isinstance(note['text'], str) and note['text'].strip(), 'Reader note text required')
        require(isinstance(note['glossaryId'], str) and note['glossaryId'].strip(), 'Reader note glossary reference required')
    return len(notes['notes'])


def save_progress(path, value):
    """Single-editor atomic save; failed writes leave the previous corpus intact."""
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.' + path.name + '.', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('initialize', 'import-draft', 'validate', 'assemble', 'release'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--chapter', type=int, choices=range(1, 81))
    args = parser.parse_args()
    require(args.action != 'release', 'English publication is disabled: a separately reviewed release pipeline and explicit publication scope are required')
    mapping = source_map(load_source())
    if args.action == 'initialize':
        require(not (DATA / 'source-map.json').exists() and not (DATA / 'progress.json').exists(), 'Never overwrite existing translation work')
        DATA.mkdir(parents=True, exist_ok=True)
        for name, value in [('source-map.json', mapping), ('progress.json', initial_progress(mapping))]:
            (DATA / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    saved = json.loads((DATA / 'source-map.json').read_text())
    require(saved == mapping, 'Stable source map differs from frozen Chinese source')
    progress = json.loads((DATA / 'progress.json').read_text())
    if args.action == 'import-draft':
        require(args.chapter is not None, '--chapter is required')
        incoming = json.loads((DATA / 'chapters' / f'ch{args.chapter:03d}.draft.json').read_text())
        positions = [i for i, u in enumerate(mapping['units']) if u['chapter'] == args.chapter]
        require(isinstance(incoming, list) and len(incoming) == len(positions), 'Chapter draft must cover every title/block exactly')
        for i, draft in zip(positions, incoming):
            require(progress['units'][i]['state'] == 'pending', 'Import never overwrites existing translation work')
            require(draft.get('state') == 'draft' and draft.get('reviews') == [], 'Import accepts unreviewed drafts only')
            progress['units'][i] = draft
    needs_snapshot = any(u.get('reviews') for u in progress['units']) or any(c.get('state') == 'accepted' for c in progress['checkpoints'])
    stats = validate_progress(mapping, progress, standard_snapshot() if needs_snapshot else None)
    if (DATA / 'reader-notes.json').exists():
        validate_reader_notes(mapping, json.loads((DATA / 'reader-notes.json').read_text()))
    if args.action == 'import-draft':
        save_progress(DATA / 'progress.json', progress)
    if args.action == 'assemble':
        require(args.output is not None, 'An explicit private QA output is required')
        output = args.output.resolve()
        qa = (ROOT / 'data/hongloumeng/first80/qa/english').resolve()
        require(qa in output.parents and output.suffix == '.json', 'WIP output must stay in ignored first80/qa/english/*.json')
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(assemble_wip(mapping, progress), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'sourceUnits': len(mapping['units']), 'states': stats, 'publishable': False}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit(str(error))
