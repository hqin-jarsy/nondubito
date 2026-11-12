"""Bounded current-source overlay over immutable completed-B9 v0.10 history.

Normative text and all prior accepted review reference prefixes remain unchanged. This module
never grants itself semantic or technical approval. Current readiness requires
real independently produced, exact-bound receipt bytes. The separately reviewed
final-state delta binds those receipts. validate_preparation checks the complete engineering
proposal without making a readiness or acceptance claim.
"""
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

OVERLAY_SHA256 = 'bccad33915b13f219a081ae44513170a0f279d3410a37f727579b62f8a1106b9'
HISTORY_MANIFEST_SHA256 = '98064e499e179fd9245e86d458e758239b53db7c7adcc177c1b5324d533e3bd4'
SEMANTIC_REVIEW_SHA256 = '9f950fad5f87d0105853f8309300326ea84efe326591115d2bf71d4eae89e049'
TECHNICAL_REVIEW_SHA256 = '0f2618b464cfe37c05de62f4c0e6b69eb7ef22cb9faf5a2be7b280438903e68e'
HISTORY_RELATIVE = 'data/hongloumeng/first80-english/history/source-ch46-ch55-before'
OVERLAY_RELATIVE = 'docs/hongloumeng/translation/source-binding-ch46-ch55.json'
CURRENT_SNAPSHOT = '7786d177dead8a27301bf753835bec4e676c0a2b6f056269a6bf2464dab08696'
PREVIOUS_SNAPSHOT = '20567ec192fb1353db5c40c98d2f53735f2a89308c84303a3cc0ea52012ab616'


def sha(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_bytes())


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def regular(root, relative):
    """Read only the exact bounded regular-file inventory, without aliases."""
    require(isinstance(relative, str) and relative and not Path(relative).is_absolute()
            and '..' not in Path(relative).parts, 'Source4655 invalid relative path')
    path = root / relative
    require(root in path.parents, 'Source4655 path escapes root')
    for ancestor in (path, *path.parents):
        require(not ancestor.is_symlink(), 'Source4655 symlink input')
    require(path.is_file() and path.stat().st_nlink == 1, 'Source4655 nonregular or hardlink input')
    return path.read_bytes()


def load_history(root):
    history = root / HISTORY_RELATIVE
    manifest_raw = regular(history, 'history-manifest.json')
    require(sha(manifest_raw) == HISTORY_MANIFEST_SHA256, 'Source4655 historical manifest changed')
    manifest = json.loads(manifest_raw)
    for name, digest in manifest['files'].items():
        require(sha(regular(history, name)) == digest, 'Source4655 historical bytes changed: ' + name)
    path = history / 'scripts/hongloumeng_english_pipeline.py'
    spec = importlib.util.spec_from_file_location('_hongloumeng_source4655_before', path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    require(old.ROOT == history, 'Source4655 wrong historical context')
    # An independent Python import context prevents current sys.modules entries
    # from supplying the historical reader or web_analytics dependencies.
    checked = subprocess.run([sys.executable, '-B', str(path), 'validate'],
                             cwd=history, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                             capture_output=True, text=True, check=False)
    require(checked.returncode == 0, 'Source4655 original v0.10 readiness failed: ' + checked.stderr[-800:])
    expected = {'sourceUnits': 4475, 'states': {'accepted': 2461, 'pending': 2014}, 'publishable': False}
    require(json.loads(checked.stdout) == expected, 'Source4655 wrong historical validation result')
    mapping = read_json(old.DATA / 'source-map.json')
    progress = read_json(old.DATA / 'progress.json')
    notes = read_json(old.DATA / 'reader-notes.json')
    snapshot = old.standard_snapshot()
    return old, manifest, mapping, progress, notes, snapshot


SOURCE_POLICY_EVIDENCE_PATH = 'data/hongloumeng/first80/author-ch46-ch55-source-policy.json'
SOURCE_POLICY_EVIDENCE_SHA256 = '0d8322004725fc3d9ed92f38fb441d4450b69bd5a08f13863f3c7dec6524ec40'


def validate_public_artifacts(root, artifacts):
    """Policy digest is generation evidence; runtime reads public artifacts only.

    The normative overlay and genuine receipts bind the exact policy identity.
    Only the private source producer reads and hash-checks that local policy file.
    No private policy content or raw editorial coordinates are copied here.
    """
    require(artifacts.get(SOURCE_POLICY_EVIDENCE_PATH) == SOURCE_POLICY_EVIDENCE_SHA256,
            'Source4655 generation policy evidence identity changed')
    for name, digest in artifacts.items():
        if name == SOURCE_POLICY_EVIDENCE_PATH:
            continue
        require(sha(regular(root, name)) == digest, 'Source4655 current artifact changed: ' + name)


def validate_preparation(pipe, mapping, progress, *, exact_baseline=True, review_reference=None, approved_metadata=None):
    """All history/current engineering checks; does NOT authenticate review claims."""
    root = pipe.ROOT
    raw = regular(root, OVERLAY_RELATIVE)
    require(sha(raw) == OVERLAY_SHA256, 'Source4655 overlay changed')
    overlay = json.loads(raw)
    require(overlay['schemaVersion'] == 1 and overlay['status'] == 'proposal_pending_independent_review'
            and overlay['publicationEnabled'] is False and overlay['installationClaim'] is False,
            'Source4655 invalid proposal status')
    require(overlay['reviewReferences'] == {'semanticMigration': None, 'technicalImplementation': None},
            'Source4655 proposal manufactures review references')
    old, manifest, before_map, before, before_notes, snapshot = load_history(root)
    require(snapshot == PREVIOUS_SNAPSHOT == overlay['previousNormativeSnapshot'], 'Source4655 historical normative snapshot changed')
    current_snapshot = pipe.standard_snapshot()
    require(current_snapshot == CURRENT_SNAPSHOT == pipe.EXPECTED_NORMATIVE_SNAPSHOT, 'Source4655 current normative snapshot changed')
    for name in old.NORMATIVE_FILES:
        relative = 'docs/hongloumeng/translation/' + name
        require(regular(root, relative) == regular(old.ROOT, relative),
                'Source4655 frozen normative object changed: ' + name)
    transition = {'state': 'pending_independent_source_binding_review',
        'previousNormativeSnapshot': PREVIOUS_SNAPSHOT, 'candidateNormativeSnapshot': CURRENT_SNAPSHOT,
        'overlaySHA256': OVERLAY_SHA256, 'historyManifestSHA256': HISTORY_MANIFEST_SHA256,
        'semanticMigrationReviewReference': None, 'technicalReviewReference': None,
        'historicalReviewObjectsPreserved': True, 'publicationEnabled': False,
        'reviewSlots': 'snapshot_migrated_original_references_retained_pending_real_suffix'}
    if approved_metadata is not None:
        require(approved_metadata == {'semantic': review_reference, 'technical': approved_metadata.get('technical')}
                and all(isinstance(v, str) and v.strip() for v in approved_metadata.values()),
                'Source4655 incomplete approved metadata references')
        transition.update(state='independently_reviewed_source_binding',
                          semanticMigrationReviewReference=approved_metadata['semantic'],
                          technicalReviewReference=approved_metadata['technical'],
                          reviewSlots='new_snapshot_and_genuine_semantic_suffix_applied')
    for name in ['provenance.json', 'CHECKPOINT.json']:
        current = read_json(pipe.STANDARD / name)
        previous = read_json(old.STANDARD / name)
        require(current == {'schemaVersion': 1, 'status': transition['state'],
                            'previousV010': previous, 'source4655Transition': transition},
                'Source4655 current transition or frozen predecessor changed: ' + name)
    for name in (old.V010_BEFORE_FILENAME, old.FELICITY_BEFORE_FILENAME):
        relative = 'data/hongloumeng/first80-english/' + name
        require(regular(root, relative) == regular(old.ROOT, relative),
                'Source4655 live historical before image changed: ' + name)
    validate_public_artifacts(root, overlay['currentArtifactSHA256'])
    require(mapping == pipe.source_map(pipe.load_source())
            == read_json(pipe.DATA / 'source-map.json'), 'Source4655 current mapping differs')
    require(len(before_map['units']) == len(mapping['units']) == 4475, 'Source4655 unit inventory differs')
    changed = []
    for a, z in zip(before_map['units'], mapping['units']):
        require((a['id'], a['chapter'], a['index'], a['layout']) ==
                (z['id'], z['chapter'], z['index'], z['layout']), 'Source4655 ID, order or layout changed')
        if a != z:
            changed.append({'id': a['id'], 'beforeSourceHash': a['sourceHash'],
                            'sourceHash': z['sourceHash'], 'beforeCharacterCount': a['characterCount'],
                            'characterCount': z['characterCount']})
    require(changed == overlay['changedPendingUnits'] and len(changed) == 12,
            'Source4655 exact changed-unit scope differs')
    require(sum(z['characterCount']-z['beforeCharacterCount'] for z in changed) == 4,
            'Source4655 unexpected character delta')
    current_by_id = {u['id']: u for u in progress['units']}
    changed_ids = {u['id'] for u in changed}
    for a, source in zip(before['units'], mapping['units']):
        z = current_by_id.get(a['id'])
        require(z is not None, 'Source4655 prior unit missing')
        expected_accepted = copy.deepcopy(a)
        for review in expected_accepted['reviews']:
            review['standardSnapshot'] = current_snapshot
            if review_reference is not None: review['reference'] += '; ' + review_reference
        if a['state'] == 'accepted':
            require(z == expected_accepted, 'Source4655 accepted body or old review lineage changed: ' + a['id'])
        if exact_baseline:
            expected = expected_accepted
            if a['id'] in changed_ids:
                require(a['state'] == 'pending' and not a['segments'] and not a['reviews'],
                        'Source4655 changed source overlaps reviewed work')
                expected['sourceHash'] = source['sourceHash']
            require(z == expected, 'Source4655 extra progress delta: ' + a['id'])
    require(progress['sourceIssues'][:len(before['sourceIssues'])] == before['sourceIssues'],
            'Source4655 previous source issue changed')
    source_by_id = {u['id']: u for u in mapping['units']}
    require(all(source_by_id.get(i['unitId'], {}).get('chapter', 0) > 45
                for i in progress['sourceIssues'][len(before['sourceIssues']):]),
            'Source4655 new issue changes an accepted chapter')
    expected_checkpoints = copy.deepcopy(before['checkpoints'])
    for row in expected_checkpoints[:9]:
        row['standardSnapshot'] = current_snapshot
        if review_reference is not None: row['reviewReference'] += '; ' + review_reference
    require(progress['checkpoints'][:9] == expected_checkpoints[:9],
            'Source4655 accepted checkpoint or old reference lineage changed')
    notes = read_json(pipe.DATA / 'reader-notes.json')
    require(notes['notes'][:len(before_notes['notes'])] == before_notes['notes'],
            'Source4655 prior reader note changed')
    if exact_baseline:
        expected = copy.deepcopy(before); expected['sourceHash'] = mapping['sourceHash']
        expected['checkpoints'] = expected_checkpoints
        for unit in expected['units']:
            for review in unit['reviews']:
                review['standardSnapshot'] = current_snapshot
                if review_reference is not None: review['reference'] += '; ' + review_reference
        for unit, source in zip(expected['units'], mapping['units']):
            if unit['id'] in changed_ids: unit['sourceHash'] = source['sourceHash']
        require(progress == expected, 'Source4655 nonbounded current progress change')
        expected_notes = dict(before_notes, sourceHash=mapping['sourceHash'])
        require(notes == expected_notes, 'Source4655 extra reader-note delta')
    stats = pipe.validate_progress(mapping, progress, current_snapshot)
    pipe.validate_reader_notes(mapping, notes)
    # Cross-check the actual preserved review objects, not just their counts.
    preserved = {'acceptedBodiesSHA256': sha(canonical([{'id': u['id'], 'sourceHash': u['sourceHash'], 'segments': u['segments']} for u in before['units'] if u['state'] == 'accepted'])),
        'all7383ReviewsSHA256': sha(canonical([{'id': u['id'], 'reviews': u['reviews']} for u in before['units'] if u['state'] == 'accepted'])),
        'nineAcceptedCheckpointsSHA256': sha(canonical(before['checkpoints'][:9])),
        'all43NotesSHA256': sha(canonical(before_notes['notes'])),
        'all16SourceIssuesSHA256': sha(canonical(before['sourceIssues']))}
    require(preserved == overlay['preservation'], 'Source4655 preservation inventory differs')
    return {'status': 'ENGINEERING_CHECKS_PASS_REVIEW_PENDING', 'normativeSnapshot': current_snapshot, 'previousNormativeSnapshot': snapshot,
            'states': stats, 'sourceChanges': 12, 'reviewedSpans': 15,
            'historicalV010AndFelicityGates': 'PASS_IN_EXACT_OLD_CONTEXT',
            'currentSourceHash': mapping['sourceHash'], 'overlaySHA256': OVERLAY_SHA256,
            'historicalManifestSHA256': HISTORY_MANIFEST_SHA256, 'installationReady': False}


def validate_readiness(pipe, mapping, progress):
    # Missing independent approval is a hard gate, not a boolean escape hatch.
    # Engineering preparation is available separately and cannot return readiness.
    references = {}
    for kind, digest in [('semantic', SEMANTIC_REVIEW_SHA256), ('technical', TECHNICAL_REVIEW_SHA256)]:
        require(isinstance(digest, str) and len(digest) == 64,
                'Source4655 independent ' + kind + ' review is pending')
        raw = regular(pipe.ROOT, 'data/hongloumeng/first80-english/source4655-' + kind + '-review.json')
        require(sha(raw) == digest, 'Source4655 unpinned ' + kind + ' receipt')
        review = json.loads(raw)
        require(review.get('status') == 'PASS_SCOPED_READY_ONLY'
                and review.get('overlaySHA256') == OVERLAY_SHA256
                and review.get('historicalManifestSHA256') == HISTORY_MANIFEST_SHA256
                and review.get('previousNormativeSnapshot') == PREVIOUS_SNAPSHOT
                and review.get('normativeSnapshot') == CURRENT_SNAPSHOT
                and review.get('sourceHash') == pipe.READING_SHA
                and review.get('notFullCorpusReread') is True
                and review.get('publicationApproved') is False
                and isinstance(review.get('reference'), str) and review['reference'].strip(),
                'Source4655 incomplete ' + kind + ' review scope')
        references[kind] = review['reference']
    result = validate_preparation(pipe, mapping, progress, exact_baseline=False,
                                  review_reference=references['semantic'], approved_metadata=references)
    return result['normativeSnapshot']
