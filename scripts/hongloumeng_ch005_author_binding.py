"""One explicit author reading, over an authenticated B16 predecessor.

Historical validators run with exact archived predecessor bytes. Current files
must match a separately reviewed bounded successor; no historical receipt is
relabeled as a new reading, and no global file reader is patched.
"""
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = 'data/hongloumeng/first80-english/'
S = 'docs/hongloumeng/translation/'
HISTORY = D + 'history/ch005-tanhuan-before'
BINDING = D + 'ch005-author-binding.json'
REVIEW = D + 'ch005-author-current-review.json'
PRIVATE_POLICY = 'data/hongloumeng/first80/author-ch005-tanhuan-policy.json'
POLICY = D + 'ch005-author-choice.json'
BINDING_SHA256 = '9d7345157a0ecbc9e29afd60a1ea3936069aada14e0c1f2554a45fecc4abf802'
REVIEW_SHA256 = '08f0de8b80c3027474b76c5ca650f5f4b0755f5eb735094feade77629cb135f9'
PRIVATE_POLICY_SHA256 = 'fc0e5370ba948203756be8cb211b39a9435392de4e3a0a2c900abc3ff80220d9'
POLICY_SHA256 = '15782738d72c1949f6b52e87f10b91c65c2130cadd9f85b7e9e7b84f10f26d1a'
REFERENCE = 'CH005-TANHUAN-INDEPENDENT-CURRENT-BINDING-20261112'
TARGET = 'hlm-c005-b0124'


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def regular(root, path):
    from hongloumeng_source4655_binding import regular as original
    return original(Path(root), path)


def binding(root=ROOT):
    raw = regular(root, BINDING)
    require(BINDING_SHA256 and sha(raw) == BINDING_SHA256, 'Unpinned chapter5 binding')
    value = json.loads(raw)
    require(value['target'] == TARGET and value['changedSourceUnits'] == 1,
            'Chapter5 source scope changed')
    return value


def policy(root=ROOT):
    raw = regular(root, POLICY)
    require(sha(raw) == POLICY_SHA256, 'Author chapter5 choice changed')
    return json.loads(raw)


def apply_model(model, raw_source, choice=None):
    """Final producer layer. Equal-length replacement, original source untouched."""
    if choice is None:
        raw_choice = regular(ROOT, PRIVATE_POLICY)
        require(sha(raw_choice) == PRIVATE_POLICY_SHA256, 'Private author choice changed')
        choice = json.loads(raw_choice)
    from build_hongloumeng_first80 import author_change_spans, selection_source_chars, effective_author_changes
    old, new = choice['before'], choice['after']
    require(len(old) == len(new), 'Chapter5 unexpected coordinate shift')
    chapter = model['chapters'][4]
    require(chapter['body'].count(old) == 1, 'Chapter5 producer source differs')
    rows = [b for b in chapter['blocks'] if old in b['text']]
    require(len(rows) == 1 and rows[0]['text'] == choice['beforeUnitText'], 'Chapter5 full source unit differs')
    start = raw_source.index(old); end = start + len(old)
    change = dict(id=choice['id'], chapter=5, title='\u4f5c\u8005\u6307\u5b9a\u300a\u559c\u51a4\u5bb6\u300b\u6539\u8bfb\u8d2a\u6b22\u5abe',
        status='author_approved', applied=True, mode='replace', source_start_char=start,
        source_end_char=end, original=old, proposed=new, context_before=raw_source[start-20:start],
        context_after=raw_source[end:end+20], reason=choice['interpretation'],
        authorization_type='explicit_author_edition_choice', decision_file=Path(PRIVATE_POLICY).name,
        decision_sha256=sha((json.dumps(choice,ensure_ascii=False,indent=2)+'\n').encode()),
        public_references=[])
    chapter['body'] = chapter['body'].replace(old,new)
    rows[0]['text'] = rows[0]['text'].replace(old,new)
    rows[0]['author_change_ids'].append(choice['id'])
    for row in chapter['layout_ranges'] + chapter['author_layout_ranges']:
        if 'exact_body_text' in row:
            row['exact_body_text'] = row['exact_body_text'].replace(old,new)
    chapter['author_changes'].append(change)
    model['author_emendations'].append(change)
    chapter['body_sha256'] = sha(chapter['body'])
    chapter['author_change_spans'] = author_change_spans(selection_source_chars(chapter,raw_source),effective_author_changes(chapter))
    for name in ('individually_confirmed','total_semantic_changes','current_active_semantic_changes',
                 'applied_occurrence_records','current_active_occurrence_records'):
        model['emendation_authority_counts'][name] += 1
    model['chapter5_tanhuan_author_choice'] = dict(policy_id=choice['id'],path=Path(PRIVATE_POLICY).name,
        sha256=change['decision_sha256'],originalReadingRetainedInHistoricalEvidence=True,bodyCodepointDelta=0)
    require(''.join(b['text'] for b in chapter['blocks']) == chapter['body'], 'Chapter5 block/body mismatch')
    return model


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def predecessor(root, bound):
    """Use exact archived bytes only for declared changed/root dependencies."""
    root = Path(root)
    history = root / HISTORY
    for path,digest in bound['unchangedRuntimeHashes'].items():
        require(sha(regular(root,path)) == digest, 'Predecessor runtime changed: '+path)
    for path, digest in bound['predecessorFiles'].items():
        require(sha(regular(history,path)) == digest, 'Changed predecessor archive: '+path)
    def before_bytes(context, path):
        context = Path(context)
        if context.resolve() == root.resolve() and path in bound['files']:
            row = bound['files'][path]
            current = regular(context,path)
            require(sha(current) in (row['beforeSHA256'],row['afterSHA256']), 'Unrecognized successor bytes: '+path)
            if row['beforeSHA256'] is not None:
                return regular(history,path)
        return regular(context,path)
    oldpipe = load_module(history/'scripts/hongloumeng_english_pipeline.py', '_hlm_ch005_predecessor_pipeline')
    oldpipe.ROOT = root
    oldpipe.DATA = history / D
    oldpipe.SOURCE = history / 'data/hongloumeng/first80-public'
    oldpipe.STANDARD = history / S
    presentation = load_module(history/'scripts/hongloumeng_reading_presentation_binding.py', '_hlm_ch005_predecessor_presentation')
    presentation.actual_regular = before_bytes
    readiness = load_module(history/'scripts/hongloumeng_english_presentation_readiness.py', '_hlm_ch005_predecessor_readiness')
    readiness.regular = presentation.read_historical
    mapping = json.loads(regular(history,D+'source-map.json'))
    progress = json.loads(regular(history,D+'progress.json'))
    notes = json.loads(regular(history,D+'reader-notes.json'))
    snapshot = readiness.validate_b16_readiness(oldpipe,mapping,progress)
    presentation.validate_state(root)
    presentation.require_review(root)
    require(snapshot == bound['previousNormativeSnapshot'], 'Predecessor normative context differs')
    return oldpipe,mapping,progress,notes


def require_review(root, bound):
    raw = regular(root,REVIEW)
    require(REVIEW_SHA256 and sha(raw) == REVIEW_SHA256, 'Independent chapter5 current review pending')
    value = json.loads(raw)
    expected = dict(status='PASS_BOUNDED_CH005_CURRENT_BINDING', bindingSHA256=BINDING_SHA256,
        target=TARGET, sourceHash=bound['sourceHash'], normativeSnapshot=bound['normativeSnapshot'],
        englishContentHash=bound['targetEnglishContentHash'], changedSourceUnits=1,
        changedEnglishUnits=1, unchangedEnglishUnits=4474, fullCorpusReread=False,
        requiredFindings=[], publicationToRemoteApproved=False)
    require(all(value.get(k)==v for k,v in expected.items()), 'Incomplete chapter5 review')
    return value


def validate_preparation(pipe, mapping, progress, *, reviewed=False):
    bound = binding(pipe.ROOT)
    for path,row in bound['files'].items():
        require(sha(regular(pipe.ROOT,path)) == row['afterSHA256'], 'Current chapter5 artifact differs: '+path)
    oldpipe, oldmap, oldprogress, oldnotes = predecessor(pipe.ROOT,bound)
    choice = policy(pipe.ROOT)
    source = pipe.load_source()
    previous = oldpipe.load_source()
    expected = copy.deepcopy(previous)
    index = choice['sourceBlockIndex']
    require(expected['chapters'][4]['blocks'][index]['text']==choice['beforeUnitText'],'Chapter5 predecessor text differs')
    expected['chapters'][4]['blocks'][index]['text']=choice['afterUnitText']
    require(source==expected, 'Chinese change escaped the one approved unit')
    require(mapping==pipe.source_map(source)==json.loads(regular(pipe.ROOT,D+'source-map.json')), 'Current map differs')
    expected_map=copy.deepcopy(oldmap)
    expected_map.update(sourceHash=bound['sourceHash'],manifestHash=bound['manifestHash'],bodyHash=bound['bodyHash'])
    next(u for u in expected_map['units'] if u['id']==TARGET)['sourceHash']=choice['afterUnitSHA256']
    require(mapping==expected_map,'Mapping delta widened')
    snapshot=pipe.standard_snapshot()
    require(snapshot==bound['normativeSnapshot']==pipe.EXPECTED_NORMATIVE_SNAPSHOT, 'New standard snapshot differs')
    expected_progress=copy.deepcopy(oldprogress);expected_progress['sourceHash']=bound['sourceHash']
    for unit in expected_progress['units']:
        if unit['id']==TARGET:
            require(len(unit['segments'])==1 and unit['segments'][0]['text'].count(choice['englishBefore'])==1,'Old English unit differs')
            unit['segments'][0]['text']=unit['segments'][0]['text'].replace(choice['englishBefore'],choice['englishAfter'])
            unit['sourceHash']=choice['afterUnitSHA256']
            for item in unit['reviews']:
                item.update(contentHash=pipe.content_hash(unit,expected_progress['sourceIssues']),standardSnapshot=snapshot,reference=REFERENCE)
        else:
            for item in unit['reviews']:
                item['standardSnapshot']=snapshot;item['reference']+='; '+REFERENCE+' (unchanged-content continuity)'
    for checkpoint in expected_progress['checkpoints']:
        checkpoint['standardSnapshot']=snapshot;checkpoint['reviewReference']+='; '+REFERENCE+' (bounded source amendment)'
        if checkpoint['first']==1:
            units=[u for s,u in zip(mapping['units'],expected_progress['units']) if s['chapter']<=5]
            checkpoint['corpusHash']=pipe.batch_hash(units,expected_progress['sourceIssues'])
    require(progress==expected_progress,'English text or review lineage delta widened')
    expected_notes=copy.deepcopy(oldnotes);expected_notes['sourceHash']=bound['sourceHash']
    notes=json.loads(regular(pipe.ROOT,D+'reader-notes.json'))
    require(notes==expected_notes,'Reader note delta widened')
    pipe.validate_progress(mapping,progress,snapshot)
    pipe.validate_reader_notes(mapping,notes)
    if reviewed:require_review(pipe.ROOT,bound)
    return snapshot


def validate_readiness(pipe,mapping,progress):
    return validate_preparation(pipe,mapping,progress,reviewed=True)
