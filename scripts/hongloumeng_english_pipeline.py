#!/usr/bin/env python3
"""Work-in-progress alignment only. No HTML renderer or publication operation."""
import argparse
import copy
from collections import Counter
import hashlib
import json
import os
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/hongloumeng/first80-english'
SOURCE = ROOT / 'data/hongloumeng/first80-public'
STANDARD = ROOT / 'docs/hongloumeng/translation'
VERSION = 'english-1-110-v0.10'
V09_VERSION = 'english-1-110-v0.9'
READING_SHA = '7621062e63ee03957e5de4a8a16a877d412599f24ee544ece9a7f1b0792e7aaf'
MANIFEST_SHA = 'de3a5e7e594b80a34093da8de178b25b070c29f1b25e44c2eeb91981d3e50071'
BODY_SHA = '36541c4b7a8dfe6dfb4d30f4107697c306feb813859259093dec562cdab6e18c'
NORMATIVE_FILES = ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md')
V09_NORMATIVE_FILES = NORMATIVE_FILES
NORMATIVE_FILES += ('english-batch-041-045.json', 'source-binding-ch46-ch55.json')
SOURCE_MAP_SHA = '11eab06a2cca2659cfe1821ad8398da5a178f289a4e3cf374fd843679c9bbc4c'
EXPECTED_NORMATIVE_SNAPSHOT = '7786d177dead8a27301bf753835bec4e676c0a2b6f056269a6bf2464dab08696'
V010_PREVIOUS_SNAPSHOT = 'd63863840a1c4f20e250791f8b4b16f7b60e964011bdad8eea619d59191ebd6b'
V010_BEFORE_FILENAME = 'v010-20261111.before.json'
V010_BEFORE_PROGRESS_SHA = '966955d4e75fb0ccc4c98b4bc633acc6531548d42414ef8838d8be9b51ff9464'
V010_PREVIOUS_PROVENANCE_SHA = 'f6b2b0e2a78e50b1be03cd5fd9d24ad7502b6df6b1fcc944936f65840a508ad5'
V010_PREVIOUS_CHECKPOINT_SHA = '617fca88bede92d026e5489de9e760db4e8147a37fa999f5c9a18f2463de9185'
V010_CORPUS_HASH = '8c4cd9bf289255f1bd889d783498c54777fca28d04d4a1d55413018134fcd173'
V010_FINAL_REFERENCE = 'EN-V010-FINAL-STATUS-INDEPENDENT-R1-20261111'
V010_MIGRATION_REFERENCE = 'EN-V010-CURRENT-1-40-NORM-MIGRATION-INDEPENDENT-R1-20261111'
V010_CURRENT_REFERENCE = 'EN-041-045-CURRENT-BINDING-INDEPENDENT-R1-20261111'
V010_EVIDENCE_HASHES = {'finalStatusReview': '000f6e7af6ff5159e10e68177ac6b2d32d74251654facff4859e53ae858fa8bd', 'currentBindingReview': 'e8cb9b6305670f2d70cdcb4041d855f90349174d926007092e5ce32850efa5a9', 'priorNormMigrationReview': '2c2eb327002a94081cc2257dad3a83726676ff96b394e57372222910c729d3d9'}
V010_B9_REFERENCE = '; '.join(('EN-041-045-CUMULATIVE-20261111', V010_CURRENT_REFERENCE, V010_FINAL_REFERENCE))
NORMATIVE_DELTA_REFERENCES = ('EN-V08-PROJECTION-R3-LISTENER-R4-DELTA-20261111', 'EN-V08-G07-11-QUANTITY-FINAL-STATUS-DELTA-20261111')
V07_BASE_NORMATIVE_SNAPSHOT = '534a727dcfcbd776460d8d357f6c77afb3385821f66a7bee51cc17b1a4c88f90'
V07_BASE_PROVENANCE_SHA = 'faced2fa7d4efc2271d04ebda9687227c99584d01f036f7d75351e7943f3010d'
V07_BASE_CHECKPOINT_SHA = 'e62aaf0ea3dbe4aff7cf2da17c21dcde0875a194c77d0e46d2b9d6fa5f9894d6'
V07_CLARIFICATION_ID = 'v07-stroke-count-attribution-2026-11-11'
V08_PREVIOUS_NORMATIVE_SNAPSHOT = '7e5d3fdb84f42130634f65cd51f17bd254a0636157feecd59ecabb1b38bd5eb9'
V08_PREVIOUS_PROVENANCE_SHA = '2badac48a6c76b555d376b3f1659a73e8766cb75a49f225430ade6f589b41d3a'
V08_PREVIOUS_CHECKPOINT_SHA = 'a348df10fe818888f00d898e3cfe6d989563060e05f855af46cc2c5496d48fcf'
SOURCE_AMENDMENT_KEY = 'source_amendment_ch38_ch40_v08'
SOURCE_AMENDMENT_ID = 'source-ch38-ch40-v08-20261111'
SOURCE_DELTA_REFERENCE = 'EN-V08-SOURCE-CH38-CH40-DELTA-20261111'
SOURCE_PREVIOUS_NORMATIVE_SNAPSHOT = '2a6e9fbd6d79e25fded68703579663dd060f0c9327ba987f1af9f951ff9999b0'
SOURCE_PREVIOUS_READING_SHA = '7454b775774692fd199302d8b68fec8f5d7f22f7823cd06d44bdac98b051aa21'
SOURCE_PREVIOUS_MAP_SHA = '978e6cdfa5abdfeb6605e3f84d9d6cdab85e3f5f3ee769d05b8de6c8eb67a25b'
SOURCE_PREVIOUS_PROVENANCE_SHA = '3c081a28aff7a44fb46283f2e74ed96af265cfb821f67f070cfadff4a197ee66'
SOURCE_PREVIOUS_CHECKPOINT_SHA = '9618cea039f93f541af943485406118cd697b4ef408b8cf6536113d308f93987'
SOURCE_DELTA_EVIDENCE_SHA = '80b806a16fbca2ae20c8df6fb8346938f7b30c45750334082103539e42deb5ce'

# Exact actual scoped semantic review; application requires separate final checks.
V09_SEMANTIC_EVIDENCE_SHA = '761d493f863f1fc5602c3e4535a87918e02ea41df3fdb10ab38b4adcd8722989'
V09_DELTA_REFERENCES = ('EN-V09-PROJECTION-R1-SEMANTIC-20261111', 'EN-V09-PROJECTION-R2-LOCATOR-DELTA-20261111')
V09_PREVIOUS_NORMATIVE_SNAPSHOT = 'e15dd208e033b1cfefdccef85d0c582b43783ea4c30f4edf775beee8d30e00f4'
V09_PREVIOUS_PROVENANCE_SHA = '7d37c96ba26cff4297a30a0cd21ca33104c9f787438453bb0e742ea73e2f48b9'
V09_PREVIOUS_CHECKPOINT_SHA = '42a92d4d083caa6e878f34544ed1b017732c4e8f1a4af21e393e0ed1172657a0'

V09_FINAL_STATUS_REFERENCE = 'EN-V09-FINAL-STATUS-R1-DELTA-20261111'
V09_FINAL_STATUS_EVIDENCE_SHA = '5f3bbd11de3293796159b5469808ea80c9f782282e750f403975327dae036479'

V09_HISTORICAL_NORMATIVE_SNAPSHOT = '5ec8290e4b6188b2746a7582b541cb0cf207b64bf11b6151519febcbb2b45fd5'
V09_HISTORICAL_READING_SHA = '564585568faa97b3b516443973c6c06a56493e5d91e81189b610c8606511dd4b'
V09_HISTORICAL_MAP_SHA = '191240e0e809bbd230e9647fbaa787f752b820af04b51f98a1bff628d0242a5f'
V09_HISTORICAL_PROVENANCE_SHA = '90e719ef0d52a62001c74151031c02eb513de334437f0b334b1540ed7e48071f'
V09_HISTORICAL_CHECKPOINT_SHA = '60b8508ed48cca1d3f2267abeb55fec2d6af8e233645429d30ce259426022ad8'
V09_HISTORICAL_DECISIONS_SHA = '222226fad0496467ad9965c97377f6e26a64fcbb78094730e08068aaf65d53a9'
V09_HISTORICAL_BINDING_SHA = '4a87b5a9af9a6b52c50c00e3921df1759b2b9fe11f73ea89e4c2afd1069f1327'
CURRENT_SOURCE_AMENDMENT_KEY = 'source_amendment_ch38_ch42_ch45_20261111'
CURRENT_SOURCE_AMENDMENT_ID = 'source-ch38-ch42-ch45-20261111'
CURRENT_SOURCE_CHANGED_IDS = ['hlm-c038-b0060', 'hlm-c042-title', 'hlm-c042-b0032', 'hlm-c045-b0035']
CURRENT_SOURCE_EVIDENCE_SHA = '16e37199180a74da5dab6c08670fda969603e9674fcb2411432fe435a9a6ddcd'
CURRENT_SOURCE_DELTA_REFERENCE = 'SOURCE-CH38-42-45-INDEPENDENT-SEMANTIC-R1-20261111'
CURRENT_SOURCE_TRADITIONAL_SHA = '52c6deffe02302e665fba2abd14ee2ff40f6ed70f12b319f85ac4867f8926da3'
CURRENT_SOURCE_REVIEW_ARTIFACT_SHA = 'd64c3e49174fa734b95562dc7829875704729b4a3063fc1dcc4ef06abd4c53ad'
CURRENT_SOURCE_REVIEW_REQUEST_SHA = '7d17a62eb2b6b224b407fc93de17243c8c01795db418c1f1540c85a865508365'
CURRENT_ACCEPTED_BODIES_SHA = '5c833abba391398de7e4dee28ba53f8107f64982e4a0bb7652d6e855490a3101'
CURRENT_REVIEW_CONTENT_SHA = '862d6fae80f441c7378a0d00fd8d1c9d5b29316d2e57ee194c79b03052e03db3'
CURRENT_OLD_REFERENCES_SHA = '2d9644cfcd70cd6a0d9f67c1ffe9256f42c0fcf03fab1da4feed3b455fc5d091'
CURRENT_CHECKPOINT_CORPUS_HASHES = ['ab09b0a93682e1ee10dd9ef5ea3504c229b0469b3bf8dec9c7c1355695cc8643', '14b84b8061425a29415d5e6f5eaf4530ad1c55ceaea4cc66ec7b2bc18785dcfb', 'a91a5357313a9ad5a011c92adbb92130721c11d94fe711a0ddba39b5a8440ea7', 'dbfe58abef590696f22d7ff0e9a3401066d8b5d2dcd24530945d9ab2de015943', '625d18c01ad40818cd2f0d93ecec80c4b6e59acdb397be0615df57be9c707507', '7b5c5e49f56e0430837a0cfbe98354fabdd2efacdc073ef781107d305a039e5e', '2f6bb5449185e1fbf9b3bbb2aab74bb3c927159071a6d3b5ae249d5f027ac30f']

FELICITY_AMENDMENT_KEY = 'naming_revision_felicity_20261111'
FELICITY_AMENDMENT_ID = 'felicity-naming-revision-20261111'
FELICITY_BEFORE_FILENAME = 'felicity-20261111.before.json'
FELICITY_BEFORE_PROGRESS_SHA = '8f4b888bb0a3fb451d76e189712fc6a87328983fd995439fe6802419ba59e444'
FELICITY_BEFORE_NORMATIVE_SNAPSHOT = 'b6c7e62662179ce90fecb4ba9eaeb0ab127c3741e7b407ca248654aaf6096c28'
FELICITY_BEFORE_PROVENANCE_SHA = 'fe70e345ac78db95fb4858cdfd4d2772f662a87c5b539eada51cb9c1310dbfcd'
FELICITY_BEFORE_CHECKPOINT_SHA = '9a56d847f3f84e8d801e8e84f695d9ec14bd3d8cfb09b5222818c63a53735929'
FELICITY_CONTENT_REFERENCE = 'FENGER-FELICITY-INDEPENDENT-R1-20261111'
FELICITY_CONTENT_REVIEW_SHA = '7b2fd5d1ad5ee0ccf97e702998175210976a0b19f832b867b7988b4eee023cd5'
FELICITY_CHANGED_IDS = ('hlm-c007-b0015', 'hlm-c007-b0016', 'hlm-c014-b0010', 'hlm-c020-b0004', 'hlm-c020-b0020', 'hlm-c024-b0028', 'hlm-c025-b0029', 'hlm-c029-b0006')
FELICITY_AFTER_CONTENT_HASHES = {'hlm-c007-b0015': '72092dc44e8a0ddf20c3dd7e9f6ffebe72bf58be2cc09906ddad5b6bd2798802', 'hlm-c007-b0016': '4979f9a8deac64801011ecdd9a78e74943db223782f8e00b3eb57b901ec6aab9', 'hlm-c014-b0010': 'fe86751c36c86d195c190b1c1e01ca1157bec859475f8b0da8821a3076c8fcf7', 'hlm-c020-b0004': '0ce289c7c1cc331e422fbfbae9e9296e31e489274bfd07e4c0d06c41d9580c50', 'hlm-c020-b0020': 'd627899fb7561ae70ac2a9f560e5b45d5843ba4e21c724ca41e025a6696f5f5d', 'hlm-c024-b0028': 'd3a320e0fc847ef75d0b8efca0f1c497573014574807af3ee5c3862fac7841c2', 'hlm-c025-b0029': '298b374336fedfaf891782ea69b60008092932ca79794e7c9914a381a7919023', 'hlm-c029-b0006': 'c44f2fd2e88757951ba2624d2b667107ff0d59020e7e17496b67c537c4d104cd'}
FELICITY_HISTORICAL_LOCATORS = [{'file': 'english-batch-006-010.json', 'pointer': '/entries/55', 'sha256': 'b0935e3199f5f4bd1208673124f97266edc00e757d5050680e686e0e3e991f35'}, {'file': 'english-batch-011-015.json', 'pointer': '/existing_form_reuse/32', 'sha256': 'bfd4506049a6c759222ee5a6b7081224d7fd30b2e00c74b44802d1ad3fff052c'}, {'file': 'english-batch-016-020.json', 'pointer': '/inherited_applications/40', 'sha256': '2541e2be147c2536c0dc3bd2f54985a761e476af148838a541721f2cbe3b4239'}, {'file': 'english-batch-021-025.json', 'pointer': '/inherited_applications/68', 'sha256': 'c00cc5f9d1d23ce14178b27de77faef1967ff6d8730390950bd8c0fc9018e3cf'}, {'file': 'english-batch-026-030.json', 'pointer': '/inherited_applications/31', 'sha256': '16c95ecabc72728f5706bddb69888c069808d3606c796fb5c756109b1e8a4993'}, {'file': 'english-batch-036-040.json', 'pointer': '/inheritedApplications/27', 'sha256': '0973ab1fc6dd52db0c4165db87ba771c9c35e3067e78699bc01981ee6307fa8f'}]
FELICITY_MIGRATION_REFERENCE = 'FELICITY-INDEPENDENT-SEMANTIC-NORM-R1-20261111'
FELICITY_MIGRATION_EVIDENCE_SHA = 'f465131270d782ee338ba75b99059a54288e9437454f7b1e7ce5e122f79b270c'

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
    names = NORMATIVE_FILES
    require(all((STANDARD / n).is_file() for n in names), 'Standard baseline is not available')
    return sha(encoded({n: sha((STANDARD / n).read_bytes()) for n in names}))


def validate_standard_readiness(mapping, progress):
    """Current source4655 overlay; genuine independent review receipts are required."""
    from hongloumeng_source4655_binding import validate_readiness
    return validate_readiness(sys.modules[__name__], mapping, progress)


def validate_pre_source4655_readiness(mapping, progress):
    """Retained old implementation. Invoke it only in the exact historical context."""
    require(READING_SHA == '05b929a0f99d99d6c8ff061eccdb88210e4c2906ee3055a688475a0f629e0c29'
            and SOURCE_MAP_SHA == 'bbb80bd819736cf6bab23308018d23bd60960bed6a8c4db0fbbac59964a7c9fc',
            'Historical v0.10 readiness requires the exact pre-source4655 context')
    snapshot = standard_snapshot()
    require(snapshot == EXPECTED_NORMATIVE_SNAPSHOT, 'Unexpected normative snapshot')
    require(mapping == source_map(load_source()), 'Frozen source map differs')
    checkpoint = json.loads((STANDARD / 'CHECKPOINT.json').read_bytes())
    require(checkpoint.get('version') == VERSION and checkpoint.get('state') == 'frozen_editorial_checkpoint', 'Normative freeze is not ready')
    require(checkpoint.get('normative_snapshot') == snapshot, 'Partial or stale normative freeze')
    require(checkpoint.get('freeze_id') == 'english-v010-ch041-045-20261111', 'Wrong v0.10 freeze identifier')
    rows = checkpoint.get('files', [])
    require(isinstance(rows, list) and all(isinstance(r, dict) and isinstance(r.get('path'), str) for r in rows), 'Invalid checkpoint file inventory')
    lookup = {r['path']: r for r in rows}
    require(len(lookup) == len(rows) == len(NORMATIVE_FILES) + 1, 'Duplicate or extra checkpoint file inventory')
    for name in (*NORMATIVE_FILES, 'provenance.json'):
        raw = (STANDARD / name).read_bytes()
        row = lookup.get('docs/hongloumeng/translation/' + name, {})
        require(row.get('sha256') == sha(raw) and row.get('bytes') == len(raw), 'Partial or stale normative file inventory')
    batch = json.loads((STANDARD / 'english-batch-041-045.json').read_bytes())
    require(batch.get('version') == VERSION and batch.get('status') == 'frozen_editorial_checkpoint'
            and batch.get('freeze_id') == checkpoint['freeze_id'] and batch.get('chapters') == list(range(41, 46)), 'Wrong or unfrozen ninth batch')
    expected_units = [u for u in mapping['units'] if 41 <= u['chapter'] <= 45]
    require(batch.get('source_units') == expected_units, 'Ninth-batch source units differ')
    binding = batch.get('sourceBinding', {})
    require(binding.get('sourceSHA256') == READING_SHA and binding.get('sourceMapSHA256') == SOURCE_MAP_SHA
            and binding.get('unitCount') == len(expected_units) == 200, 'Ninth-batch source binding differs')
    document = json.loads((STANDARD / 'provenance.json').read_bytes())
    transition = document.get('normative_projection_v010', {})
    previous_document = {k: v for k, v in document.items() if k != 'normative_projection_v010'}
    require(sha(encoded(previous_document)) == V010_PREVIOUS_PROVENANCE_SHA
            == transition.get('previousProvenanceCanonicalSHA256'), 'v0.10 predecessor provenance changed')
    previous_checkpoint = transition.get('previousCheckpoint')
    require(sha(encoded(previous_checkpoint)) == V010_PREVIOUS_CHECKPOINT_SHA
            == transition.get('previousCheckpointCanonicalSHA256')
            and checkpoint.get('previousCheckpoint') == previous_checkpoint, 'v0.10 predecessor checkpoint changed')
    require(transition.get('previousProgressPath') == 'data/hongloumeng/first80-english/' + V010_BEFORE_FILENAME,
            'v0.10 historical progress path differs')
    raw = (DATA / V010_BEFORE_FILENAME).read_bytes()
    require(sha(raw) == V010_BEFORE_PROGRESS_SHA == transition.get('previousProgressSHA256'), 'v0.10 historical progress changed')
    previous = json.loads(raw)
    require(transition.get('version') == VERSION and transition.get('state') == 'frozen_editorial_checkpoint'
            and transition.get('freeze_id') == checkpoint['freeze_id']
            and transition.get('previousNormativeSnapshot') == V010_PREVIOUS_SNAPSHOT
            and transition.get('candidateNormativeSnapshot') == snapshot
            and transition.get('previousCheckpointSHA256') == '54b67bd8e08b81ea23e05abfa5797c2975a390eee1a15b38f696a81d0c8f6afd'
            and transition.get('previousProvenanceSHA256') == 'b43fe0ab3d35b4034608ea97a58c207e6983bd64978d9c76e90140a07dfb3981'
            and transition.get('sourceHash') == READING_SHA and transition.get('sourceMapHash') == SOURCE_MAP_SHA
            and transition.get('reviewBindingsMigrated') is True and transition.get('publicationEnabled') is False
            and transition.get('currentNamingForm') == 'Felicity' and transition.get('historicalObjectsPreserved') is True
            and transition.get('independentTechnicalReview') == 'required_by_installation_contract', 'Incomplete v0.10 transition')
    for name, digest in V010_EVIDENCE_HASHES.items():
        require(sha(encoded(transition.get(name))) == digest, 'v0.10 scoped review evidence missing or forged: ' + name)
    require(transition.get('reviewEvidenceCanonicalHashes') == V010_EVIDENCE_HASHES, 'v0.10 evidence hash binding differs')
    for field in ('independentExactProjectionReview', 'independentSemanticMigrationReview', 'independentFinalStatusReview'):
        require(transition.get(field) == 'PASS_SCOPED_READY_ONLY', 'Incomplete v0.10 scoped review')
    readiness = checkpoint.get('readiness', {})
    require(readiness == {'sourceInstalled': True, 'independentExactProjectionReview': 'PASS_SCOPED_READY_ONLY',
            'independentSemanticDeltaReview': 'PASS_SCOPED_READY_ONLY', 'independentTechnicalReview': 'required_by_installation_contract',
            'reviewBindingsCurrent': True, 'publicationEnabled': False, 'independentFinalStatusReview': 'PASS_SCOPED_READY_ONLY',
            'normativeDeltaReviewReferences': [V010_MIGRATION_REFERENCE, V010_FINAL_REFERENCE],
            'reviewEvidenceCanonicalHashes': V010_EVIDENCE_HASHES}, 'Incomplete v0.10 readiness')
    chain = {k: transition[k] for k in ('previousNormativeSnapshot', 'previousCheckpointSHA256', 'previousProvenanceSHA256',
             'previousCheckpointCanonicalSHA256', 'previousProvenanceCanonicalSHA256', 'previousProgressPath',
             'previousProgressSHA256', 'candidateNormativeSnapshot', 'reviewEvidenceCanonicalHashes')}
    require(checkpoint.get('normativeTransitionV010') == chain, 'v0.10 checkpoint transition differs')
    # The genuine before image is never relabelled or rewritten to pass old guards.
    validate_v09_readiness(mapping, previous, snapshot=V010_PREVIOUS_SNAPSHOT,
                           checkpoint=previous_checkpoint, document=previous_document)
    suffix = '; ' + V010_MIGRATION_REFERENCE + '; ' + V010_FINAL_REFERENCE
    old_issues = previous['sourceIssues']
    require(progress['sourceIssues'][:len(old_issues)] == old_issues, 'v0.10 source issues changed')
    later_ids = {u['id'] for u in mapping['units'] if u['chapter'] > 45}
    require(all(i['unitId'] in later_ids for i in progress['sourceIssues'][len(old_issues):]), 'v0.10 reviewed source issue scope changed')
    for source, before, after in zip(mapping['units'], previous['units'], progress['units']):
        if source['chapter'] <= 40:
            expected = copy.deepcopy(before)
            for review in expected['reviews']:
                review['standardSnapshot'] = snapshot
                review['reference'] += suffix
            require(after == expected, 'v0.10 prior body or review lineage changed')
        elif source['chapter'] <= 45:
            for review in after['reviews']:
                require(review['reference'] == V010_B9_REFERENCE, 'v0.10 current review lineage differs')
    for before, after in zip(previous['checkpoints'][:8], progress['checkpoints'][:8]):
        expected = dict(before, standardSnapshot=snapshot, reviewReference=before['reviewReference'] + suffix)
        require(after == expected, 'v0.10 prior checkpoint lineage changed')
    current = [u for source, u in zip(mapping['units'], progress['units']) if 41 <= source['chapter'] <= 45]
    # Before import the batch may be pending; partial import remains ordinary WIP.
    # Once any scoped review is claimed, bind the complete actual reviewed corpus.
    if any(u['reviews'] for u in current) or progress['checkpoints'][8]['state'] == 'accepted':
        require(batch_hash(current, progress['sourceIssues']) == V010_CORPUS_HASH, 'v0.10 current pipeline corpus differs')
    if progress['checkpoints'][8]['state'] == 'accepted':
        require(progress['checkpoints'][8]['reviewReference'] == V010_B9_REFERENCE, 'v0.10 ninth checkpoint review lineage differs')
    validate_progress(mapping, progress, snapshot)
    return snapshot


def validate_v09_readiness(mapping, progress, *, snapshot=None, checkpoint=None, document=None):
    """Exact current norm binding. Editorial truth is separately authenticated."""
    if checkpoint is None:
        snapshot = standard_snapshot()
        require(snapshot == EXPECTED_NORMATIVE_SNAPSHOT, 'Unexpected normative snapshot')
        require(mapping == source_map(load_source()), 'Frozen source map differs')
        checkpoint = json.loads((STANDARD / 'CHECKPOINT.json').read_bytes())
        require(checkpoint.get('version') == V09_VERSION and checkpoint.get('state') == 'frozen_editorial_checkpoint', 'Normative freeze is not ready')
        require(checkpoint.get('normative_snapshot') == snapshot, 'Partial or stale normative freeze')
        freeze_id = checkpoint.get('freeze_id')
        require(isinstance(freeze_id, str) and bool(freeze_id.strip()), 'Freeze identifier required')
        rows = checkpoint.get('files', [])
        require(isinstance(rows, list) and all(isinstance(r, dict) and isinstance(r.get('path'), str) for r in rows), 'Invalid checkpoint file inventory')
        lookup = {r['path']: r for r in rows}
        require(len(lookup) == len(rows), 'Duplicate checkpoint file inventory')
        for name in (*NORMATIVE_FILES, 'provenance.json'):
            raw = (STANDARD / name).read_bytes()
            row = lookup.get('docs/hongloumeng/translation/' + name, {})
            require(row.get('sha256') == sha(raw) and row.get('bytes') == len(raw), 'Partial or stale normative file inventory')
    freeze_id = checkpoint.get('freeze_id')
    batch = json.loads((STANDARD / 'english-batch-036-040.json').read_bytes())
    require(batch.get('version') == V09_VERSION and batch.get('status') == 'frozen_editorial_checkpoint'
            and batch.get('freeze_id') == freeze_id, 'Wrong or unfrozen eighth batch')
    require(batch.get('chapters') == list(range(36, 41)), 'Wrong eighth-batch chapter scope')
    expected_units = [u for u in mapping['units'] if 36 <= u['chapter'] <= 40]
    actual_units = batch.get('source_units')
    require(isinstance(actual_units, list) and len(actual_units) == len(expected_units), 'Eighth-batch source units differ')
    for actual, expected in zip(actual_units, expected_units):
        require({k: v for k, v in actual.items() if k != 'sourceTextJSONPointer'} == expected, 'Eighth-batch source IDs or layouts drifted')
        pointer = '/chapters/' + str(expected['chapter'] - 1) + ('/title' if expected['index'] == 0 else '/blocks/' + str(expected['index'] - 1) + '/text')
        require(actual.get('sourceTextJSONPointer') == pointer, 'Eighth-batch source text pointer differs')
    binding = batch.get('sourceBinding', {})
    require(binding.get('observedSHA256') == READING_SHA == binding.get('boundSHA256')
            and binding.get('observedSourceMapSHA256') == SOURCE_MAP_SHA
            and binding.get('expectedUnitCount') == len(expected_units), 'Eighth-batch source binding differs')
    decisions = batch.get('sourceReadingDecisions', [])
    require(len(decisions) == 3 and sha(encoded(decisions[:2])) == V09_HISTORICAL_DECISIONS_SHA,
            'Historical source decisions changed')
    require([d.get('unitId') for d in decisions] == ['hlm-c038-b0060', 'hlm-c040-b0011', 'hlm-c038-b0060'],
            'Portable historical decisions and author override missing')
    require(sha(encoded(batch.get('sourceBindingHistory'))) == V09_HISTORICAL_BINDING_SHA,
            'Historical source binding changed')
    require(binding.get('sourceCommit') is None and binding.get('status') == 'current_source_bound',
            'Current binding must not invent an installation commit')
    mapped = {u['id']: u for u in mapping['units']}
    traditional_raw = (SOURCE / 'reading.zh-hant.json').read_bytes()
    require(sha(traditional_raw) == binding.get('traditionalSHA256'), 'Traditional source binding differs')
    traditional = json.loads(traditional_raw)
    # The prior ch38 decision remains an exact historical record, superseded by
    # the explicit author choice. The ch40 decision continues to govern ch40.
    for decision in (decisions[1], decisions[2]):
        source = mapped[decision['unitId']]
        require(decision.get('installedUnitSourceHash', decision.get('unitSourceHash')) == source['sourceHash']
                == sha(decision.get('adoptedUnit', '')), 'Portable adopted source differs')
        require(decision.get('traditionalAdoptedUnit') == traditional['chapters'][source['chapter']-1]['blocks'][source['index']-1]['text'],
                'Portable Traditional source differs')
        require(bool(decision.get('beforeUnit')) and bool(decision.get('traditionalBeforeUnit'))
                and bool(decision.get('evidenceLimit')) and bool(decision.get('publicEvidence')), 'Portable source evidence incomplete')
    require(decisions[2].get('kind') == 'author_aesthetic_override'
            and decisions[2].get('supersedesDecisionIndex') == 0
            and decisions[2].get('after') == '几霜痕'
            and decisions[2].get('englishBodyDelta') == 0,
            'Explicit author override missing')
    if document is None:
        document = json.loads((STANDARD / 'provenance.json').read_bytes())
    previous_progress = load_felicity_before(document)
    previous_document = {k: v for k, v in document.items() if k != FELICITY_AMENDMENT_KEY}
    transition = document.get('normative_projection_v09', {})
    history = {k: v for k, v in document.items() if k not in ('normative_projection_v09', CURRENT_SOURCE_AMENDMENT_KEY, FELICITY_AMENDMENT_KEY)}
    require(sha(encoded(history)) == V09_PREVIOUS_PROVENANCE_SHA, 'Historical provenance changed')
    previous = transition.get('previousCheckpoint')
    require(sha(encoded(previous)) == V09_PREVIOUS_CHECKPOINT_SHA, 'Historical checkpoint changed')
    require(transition.get('previousNormativeSnapshot') == V09_PREVIOUS_NORMATIVE_SNAPSHOT
            and transition.get('previousProvenanceSHA256') == V09_PREVIOUS_PROVENANCE_SHA
            and transition.get('previousCheckpointSHA256') == V09_PREVIOUS_CHECKPOINT_SHA, 'v0.9 predecessor differs')
    require(transition.get('version') == V09_VERSION and transition.get('state') == 'frozen_editorial_checkpoint'
            and transition.get('candidateNormativeSnapshot') == V09_HISTORICAL_NORMATIVE_SNAPSHOT
            and transition.get('sourceHash') == V09_HISTORICAL_READING_SHA and transition.get('sourceMapHash') == V09_HISTORICAL_MAP_SHA
            and transition.get('reviewBindingsMigrated') is True and transition.get('publicationEnabled') is False
            and transition.get('independentEditorialReview') == 'PASS'
            and transition.get('independentSemanticDeltaReview') == 'PASS'
            and transition.get('independentTechnicalReview') == 'required_by_installation_contract', 'Incomplete v0.9 transition')
    require(V09_SEMANTIC_EVIDENCE_SHA is not None and bool(V09_DELTA_REFERENCES), 'Awaiting authenticated normative delta review')
    evidence = transition.get('semanticDeltaReview')
    require(isinstance(evidence, dict) and sha(encoded(evidence)) == V09_SEMANTIC_EVIDENCE_SHA, 'Normative delta evidence differs')
    require(evidence.get('status') == 'PASS' and evidence.get('references') == list(V09_DELTA_REFERENCES)
            and evidence.get('previousNormativeSnapshot') == V09_PREVIOUS_NORMATIVE_SNAPSHOT
            and evidence.get('normativeSnapshot') == V09_HISTORICAL_NORMATIVE_SNAPSHOT and evidence.get('sourceHash') == V09_HISTORICAL_READING_SHA
            and evidence.get('sourceMapHash') == V09_HISTORICAL_MAP_SHA and evidence.get('acceptedBodiesUnchanged') is True
            and evidence.get('notFullCorpusReread') is True and bool(evidence.get('reviewedEarlierUnitIds')), 'Normative delta scope differs')
    final_status = transition.get('finalStatusReview')
    require(isinstance(final_status, dict) and sha(encoded(final_status)) == V09_FINAL_STATUS_EVIDENCE_SHA
            and final_status.get('status') == 'PASS' and final_status.get('reference') == V09_FINAL_STATUS_REFERENCE
            and final_status.get('normativeSnapshot') == V09_HISTORICAL_NORMATIVE_SNAPSHOT, 'Final-status review evidence differs')
    readiness = checkpoint.get('readiness', {})
    require(readiness.get('sourceInstalled') is True and readiness.get('independentEditorialReview') == 'PASS'
            and readiness.get('independentSemanticDeltaReview') == 'PASS'
            and readiness.get('independentTechnicalReview') == 'required_by_installation_contract'
            and readiness.get('reviewBindingsCurrent') is True and readiness.get('publicationEnabled') is False
            and readiness.get('normativeDeltaReviewReferences') == list(V09_DELTA_REFERENCES), 'Incomplete v0.9 readiness')
    require(readiness.get('independentFinalStatusReview') == 'PASS'
            and readiness.get('finalStatusReviewReference') == V09_FINAL_STATUS_REFERENCE
            and readiness.get('finalStatusEvidenceSHA256') == V09_FINAL_STATUS_EVIDENCE_SHA, 'Final-status readiness evidence missing')
    chain = {k: transition[k] for k in ('previousNormativeSnapshot', 'previousProvenanceSHA256', 'previousCheckpointSHA256', 'candidateNormativeSnapshot')}
    require(checkpoint.get('normativeTransitionV09') == chain, 'v0.9 checkpoint transition differs')
    # Earlier acceptance is a prerequisite, not a fixed pending-state cap on 36–40.
    for source, unit in zip(mapping['units'], previous_progress['units']):
        if source['chapter'] <= 35:
            require(unit['state'] == 'accepted', 'Prior seven batches must remain accepted')
            require(all(all(ref in r['reference'].split('; ') for ref in V09_DELTA_REFERENCES) for r in unit['reviews']), 'Accepted review missing actual normative delta reference')
            require(all(V09_FINAL_STATUS_REFERENCE in r['reference'].split('; ') for r in unit['reviews']), 'Accepted review missing final-status reference')
            require(all(SOURCE_DELTA_REFERENCE in r['reference'].split('; ') for r in unit['reviews']), 'Accepted review missing historical source delta reference')
            if source['chapter'] <= 30:
                require(all(all(ref in r['reference'].split('; ') for ref in NORMATIVE_DELTA_REFERENCES) for r in unit['reviews']), 'Accepted review missing historical normative delta reference')
    for i, item in enumerate(previous_progress['checkpoints'][:7]):
        require(item['state'] == 'accepted' and all(ref in item['reviewReference'].split('; ') for ref in V09_DELTA_REFERENCES), 'Checkpoint missing actual normative delta reference')
        require(V09_FINAL_STATUS_REFERENCE in item['reviewReference'].split('; '), 'Checkpoint missing final-status reference')
        require(SOURCE_DELTA_REFERENCE in item['reviewReference'].split('; '), 'Checkpoint missing historical source delta reference')
        if i < 6:
            require(all(ref in item['reviewReference'].split('; ') for ref in NORMATIVE_DELTA_REFERENCES), 'Checkpoint missing historical normative delta reference')
    validate_current_source_amendment(previous_document, checkpoint, mapping, previous_progress, FELICITY_BEFORE_NORMATIVE_SNAPSHOT)
    validate_felicity_revision(document, checkpoint, mapping, progress, previous_progress, snapshot)
    validate_progress(mapping, progress, snapshot, version=V09_VERSION)
    return snapshot


def validate_current_source_amendment(document, checkpoint, mapping, progress, snapshot):
    """Separate actual current migration evidence from untouched v0.9 history."""
    amendment = document.get(CURRENT_SOURCE_AMENDMENT_KEY)
    require(isinstance(amendment, dict), 'Current source amendment missing')
    historical = {k: v for k, v in document.items() if k != CURRENT_SOURCE_AMENDMENT_KEY}
    require(sha(encoded(historical)) == V09_HISTORICAL_PROVENANCE_SHA
            == amendment.get('previousProvenanceSHA256'), 'Historical v0.9 provenance changed')
    require(sha(encoded(amendment.get('previousCheckpoint'))) == V09_HISTORICAL_CHECKPOINT_SHA
            == amendment.get('previousCheckpointSHA256'), 'Historical v0.9 checkpoint changed')
    require(CURRENT_SOURCE_EVIDENCE_SHA is not None and CURRENT_SOURCE_DELTA_REFERENCE is not None,
            'Awaiting authenticated current source/norm migration review')
    evidence = amendment.get('evidence')
    require(isinstance(evidence, dict) and sha(encoded(evidence)) == CURRENT_SOURCE_EVIDENCE_SHA
            == amendment.get('evidenceSHA256'), 'Current source evidence missing or forged')
    require(amendment.get('id') == CURRENT_SOURCE_AMENDMENT_ID
            and amendment.get('state') == 'reviewed_binding_migration'
            and amendment.get('previousNormativeSnapshot') == V09_HISTORICAL_NORMATIVE_SNAPSHOT
            and amendment.get('normativeSnapshot') == snapshot
            and amendment.get('sourceHash') == READING_SHA
            and amendment.get('sourceMapHash') == SOURCE_MAP_SHA
            and amendment.get('traditionalHash') == CURRENT_SOURCE_TRADITIONAL_SHA
            and amendment.get('changedUnitIds') == CURRENT_SOURCE_CHANGED_IDS
            and amendment.get('reviewBindingsMigrated') is True
            and amendment.get('reference') == CURRENT_SOURCE_DELTA_REFERENCE
            and amendment.get('reviewArtifactSHA256') == CURRENT_SOURCE_REVIEW_ARTIFACT_SHA
            and amendment.get('notFullCorpusReread') is True
            and amendment.get('newEnglishAcceptance') is False
            and amendment.get('publicationEnabled') is False,
            'Current source migration scope differs')
    require(evidence.get('status') == 'PASS'
            and evidence.get('reference') == CURRENT_SOURCE_DELTA_REFERENCE
            and evidence.get('previousNormativeSnapshot') == V09_HISTORICAL_NORMATIVE_SNAPSHOT
            and evidence.get('normativeSnapshot') == snapshot
            and evidence.get('sourceHash') == READING_SHA
            and evidence.get('sourceMapHash') == SOURCE_MAP_SHA
            and evidence.get('traditionalHash') == CURRENT_SOURCE_TRADITIONAL_SHA
            and evidence.get('changedUnitIds') == CURRENT_SOURCE_CHANGED_IDS
            and evidence.get('acceptedBodiesUnchanged') is True
            and evidence.get('notFullCorpusReread') is True
            and evidence.get('reviewBindingsMigrationApproved') is True
            and evidence.get('reviewRequestSHA256') == CURRENT_SOURCE_REVIEW_REQUEST_SHA
            == amendment.get('reviewRequestSHA256'), 'Current source evidence scope differs')
    current = {k: amendment[k] for k in ('id', 'state', 'previousNormativeSnapshot', 'normativeSnapshot',
               'sourceHash', 'sourceMapHash', 'traditionalHash', 'reference', 'evidenceSHA256', 'reviewBindingsMigrated')}
    require(checkpoint.get('currentSourceAmendment') == current, 'Current checkpoint amendment differs')
    earlier = [u for s, u in zip(mapping['units'], progress['units']) if s['chapter'] <= 35]
    require(len(earlier) == 1885 and sha(encoded([{k: v for k, v in u.items() if k != 'reviews'} for u in earlier]))
            == CURRENT_ACCEPTED_BODIES_SHA == amendment.get('acceptedBodiesSHA256'),
            'Earlier accepted English bodies changed')
    reviews = [r for u in earlier for r in u['reviews']]
    require(len(reviews) == 5655 and sha(encoded([r['contentHash'] for r in reviews]))
            == CURRENT_REVIEW_CONTENT_SHA == amendment.get('acceptedReviewContentHashesSHA256'),
            'Earlier accepted review content hashes changed')
    suffix = '; ' + CURRENT_SOURCE_DELTA_REFERENCE
    require(all(r['reference'].endswith(suffix) for r in reviews), 'Accepted review missing current source reference')
    require(sha(encoded([r['reference'][:-len(suffix)] for r in reviews])) == CURRENT_OLD_REFERENCES_SHA,
            'Original review reference prefixes changed')
    require([c['corpusHash'] for c in progress['checkpoints'][:7]] == CURRENT_CHECKPOINT_CORPUS_HASHES
            == amendment.get('checkpointCorpusHashes'), 'Historical checkpoint corpus hashes changed')
    require(all(c['reviewReference'].endswith(suffix) for c in progress['checkpoints'][:7]),
            'Checkpoint missing current source reference')


def load_felicity_before(document):
    amendment = document.get(FELICITY_AMENDMENT_KEY)
    require(isinstance(amendment, dict), 'Felicity revision missing')
    require(amendment.get('previousProgressPath') == 'data/hongloumeng/first80-english/' + FELICITY_BEFORE_FILENAME,
            'Felicity historical progress path differs')
    raw = (DATA / FELICITY_BEFORE_FILENAME).read_bytes()
    require(sha(raw) == FELICITY_BEFORE_PROGRESS_SHA == amendment.get('previousProgressSHA256'),
            'Felicity historical progress changed')
    return json.loads(raw)


def validate_felicity_revision(document, checkpoint, mapping, progress, previous, snapshot):
    """One exact naming delta; historical source migration is checked separately."""
    amendment = document[FELICITY_AMENDMENT_KEY]
    historical = {k: v for k, v in document.items() if k != FELICITY_AMENDMENT_KEY}
    require(sha(encoded(historical)) == FELICITY_BEFORE_PROVENANCE_SHA == amendment.get('previousProvenanceSHA256'),
            'Felicity predecessor provenance changed')
    old_checkpoint = amendment.get('previousCheckpoint')
    require(sha(encoded(old_checkpoint)) == FELICITY_BEFORE_CHECKPOINT_SHA == amendment.get('previousCheckpointSHA256'),
            'Felicity predecessor checkpoint changed')
    require(FELICITY_MIGRATION_EVIDENCE_SHA is not None and FELICITY_MIGRATION_REFERENCE is not None,
            'Awaiting actual Felicity normative migration review')
    evidence = amendment.get('normativeMigrationReview')
    require(isinstance(evidence, dict) and sha(encoded(evidence)) == FELICITY_MIGRATION_EVIDENCE_SHA,
            'Felicity normative migration evidence missing or forged')
    require(evidence.get('status') == 'PASS'
            and evidence.get('reference') == FELICITY_MIGRATION_REFERENCE
            and evidence.get('previousNormativeSnapshot') == FELICITY_BEFORE_NORMATIVE_SNAPSHOT
            and evidence.get('normativeSnapshot') == snapshot
            and evidence.get('sourceHash') == READING_SHA and evidence.get('sourceMapHash') == SOURCE_MAP_SHA
            and evidence.get('changedUnitIds') == list(FELICITY_CHANGED_IDS)
            and evidence.get('unchangedAcceptedBodyCount') == 1877
            and evidence.get('unchangedReviewContentHashCount') == 5631
            and evidence.get('changedAcceptedUnitCount') == 8
            and evidence.get('nameReplacementCount') == 10
            and evidence.get('reviewBindingsMigrationApproved') is True
            and evidence.get('changedCorpusBatches') == [[6, 10], [11, 15], [16, 20], [21, 25], [26, 30]]
            and evidence.get('notFullCorpusReread') is True
            and isinstance(evidence.get('reviewArtifactSHA256'), str) and len(evidence['reviewArtifactSHA256']) == 64,
            'Felicity normative migration scope differs')
    require(amendment.get('id') == FELICITY_AMENDMENT_ID
            and amendment.get('state') == 'reviewed_naming_revision'
            and amendment.get('previousNormativeSnapshot') == FELICITY_BEFORE_NORMATIVE_SNAPSHOT
            and amendment.get('normativeSnapshot') == snapshot
            and amendment.get('sourceHash') == READING_SHA and amendment.get('sourceMapHash') == SOURCE_MAP_SHA
            and amendment.get('changedUnitIds') == list(FELICITY_CHANGED_IDS)
            and amendment.get('currentForm') == 'Felicity' and amendment.get('historicalForm') == 'Feng-er'
            and amendment.get('contentReviewReference') == FELICITY_CONTENT_REFERENCE
            and amendment.get('contentReviewArtifactSHA256') == FELICITY_CONTENT_REVIEW_SHA
            and amendment.get('contentReviewHashes') == FELICITY_AFTER_CONTENT_HASHES
            and amendment.get('historicalLocatorHashes') == FELICITY_HISTORICAL_LOCATORS
            and amendment.get('publicationEnabled') is False and amendment.get('newChapterAcceptance') is False,
            'Felicity revision identity or content scope differs')
    binding = {k: amendment[k] for k in ('id', 'state', 'previousNormativeSnapshot', 'normativeSnapshot',
               'sourceHash', 'sourceMapHash', 'previousProgressSHA256', 'contentReviewReference')}
    binding['normativeMigrationReference'] = FELICITY_MIGRATION_REFERENCE
    binding['normativeMigrationEvidenceSHA256'] = FELICITY_MIGRATION_EVIDENCE_SHA
    require(checkpoint.get('currentNamingRevision') == binding, 'Felicity checkpoint binding differs')
    for row in FELICITY_HISTORICAL_LOCATORS:
        value = json.loads((STANDARD / row['file']).read_bytes())
        for token in row['pointer'].split('/')[1:]:
            token = token.replace('~1', '/').replace('~0', '~')
            value = value[int(token)] if isinstance(value, list) else value[token]
        require(sha(encoded(value)) == row['sha256'], 'Historical Feng-er norm object changed')
    require(checkpoint.get('currentSourceAmendment') == old_checkpoint.get('currentSourceAmendment'),
            'Current checkpoint amendment differs')
    # Only the previously accepted prefix is constrained here. Later batches
    # retain their ordinary import/review/checkpoint lifecycle and are not capped.
    old = [u for s, u in zip(mapping['units'], previous['units']) if s['chapter'] <= 35]
    current = [u for s, u in zip(mapping['units'], progress['units']) if s['chapter'] <= 35]
    require(len(old) == len(current) == 1885, 'Felicity prior accepted inventory differs')
    suffix = '; ' + FELICITY_MIGRATION_REFERENCE
    replacements = 0
    for before, after in zip(old, current):
        require(before['id'] == after['id'], 'Felicity prior unit order differs')
        expected = copy.deepcopy(before)
        if before['id'] in FELICITY_CHANGED_IDS:
            for segment in expected['segments']:
                replacements += segment['text'].count('Feng-er')
                segment['text'] = segment['text'].replace('Feng-er', 'Felicity')
            expected['reviews'] = [{'type': kind, 'contentHash': FELICITY_AFTER_CONTENT_HASHES[before['id']],
                                    'standardSnapshot': snapshot,
                                    'reference': FELICITY_CONTENT_REFERENCE + suffix} for kind in REVIEW_TYPES]
            require(content_hash(after, progress['sourceIssues']) == FELICITY_AFTER_CONTENT_HASHES[before['id']],
                    'Felicity reviewed content differs')
        else:
            for review in expected['reviews']:
                review['standardSnapshot'] = snapshot
                review['reference'] += suffix
        require({k: v for k, v in after.items() if k != 'reviews'} ==
                {k: v for k, v in expected.items() if k != 'reviews'},
                'Earlier accepted English bodies changed outside exact Felicity delta')
        require(after['reviews'] == expected['reviews'], 'Felicity current review lineage or exact binding differs')
    require(replacements == 10, 'Felicity exact ten-name replacement scope differs')
    changed_batches = []
    for index, before in enumerate(previous['checkpoints'][:7]):
        units = [u for s, u in zip(mapping['units'], progress['units']) if before['first'] <= s['chapter'] <= before['last']]
        expected = copy.deepcopy(before)
        expected.update(corpusHash=batch_hash(units, progress['sourceIssues']), standardSnapshot=snapshot,
                        reviewReference=before['reviewReference'] + suffix)
        if expected['corpusHash'] != before['corpusHash']:
            changed_batches.append([before['first'], before['last']])
        require(progress['checkpoints'][index] == expected, 'Felicity current checkpoint lineage or corpus differs')
    require(changed_batches == [[6, 10], [11, 15], [16, 20], [21, 25], [26, 30]],
            'Felicity five-batch corpus delta differs')


def content_hash(unit, issues=()):
    relevant = sorted((issue for issue in issues if issue['unitId'] == unit['id']), key=lambda issue: issue['id'])
    return sha(encoded({'id': unit['id'], 'sourceHash': unit['sourceHash'], 'segments': unit['segments'], 'sourceIssues': relevant}))


def batch_hash(units, issues=()):
    return sha(encoded([content_hash(u, issues) for u in units]))


def closing_quote_source_ids(mapping):
    """Derive the narrow punctuation exception from the verified Chinese source."""
    frozen = source_map(load_source())
    require(mapping == frozen, 'Closing-quote source map differs from verified Chinese source')
    return {u['id'] for u in frozen['units']
            if u['layout'] == {'kind': 'prose'} and u['characterCount'] == 1
            and u['sourceHash'] == sha('”')}


def validate_progress(mapping, progress, snapshot=None, *, version=None):
    keys(progress, 'schemaVersion status sourceHash standardVersion units checkpoints sourceIssues')
    require(progress['schemaVersion'] == 1 and progress['status'] == 'translation-work-in-progress', 'Not a work-in-progress corpus')
    require(progress['sourceHash'] == mapping['sourceHash'] == READING_SHA, 'Wrong source binding')
    require(progress['standardVersion'] == (VERSION if version is None else version), 'Wrong standard version')
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
    quote_source_ids = None
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
            has_letters = any(c.isascii() and c.isalpha() for c in segment['text'])
            if not has_letters and quote_source_ids is None:
                quote_source_ids = closing_quote_source_ids(mapping)
            require(has_letters or (len(unit['segments']) == 1 and unit['id'] in quote_source_ids
                                    and segment['text'] in ('’', "'", '"')),
                    'No English letters; only a verified standalone closing quote is exempt')
        if source['layout']['kind'] not in ('prose', 'letter'):
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
        validate_standard_readiness(mapping, progress)
        require(args.chapter is not None, '--chapter is required')
        incoming = json.loads((DATA / 'chapters' / f'ch{args.chapter:03d}.draft.json').read_text())
        positions = [i for i, u in enumerate(mapping['units']) if u['chapter'] == args.chapter]
        require(isinstance(incoming, list) and len(incoming) == len(positions), 'Chapter draft must cover every title/block exactly')
        for i, draft in zip(positions, incoming):
            require(progress['units'][i]['state'] == 'pending', 'Import never overwrites existing translation work')
            require(draft.get('state') == 'draft' and draft.get('reviews') == [], 'Import accepts unreviewed drafts only')
            progress['units'][i] = draft
    needs_snapshot = any(u.get('reviews') for u in progress['units']) or any(c.get('state') == 'accepted' for c in progress['checkpoints'])
    current_snapshot = validate_standard_readiness(mapping, progress) if needs_snapshot else None
    stats = validate_progress(mapping, progress, current_snapshot)
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
