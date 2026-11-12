"""A single accepted-unit amendment after immutable source4655 history.

The prior complete validator runs only in its authentic parent context. This
layer does not extend source4655's pending-only proof to this changed accepted
unit. Real content review is pinned; final current-binding/engineering approval
is a separate required receipt. No English publication path is added.
"""
import copy,importlib.util,json,os,subprocess,sys
from pathlib import Path
from hongloumeng_source4655_binding import regular,sha,canonical,require,read_json
HISTORY_RELATIVE='data/hongloumeng/first80-english/history/ch002-ending-before'
HISTORY_SHA256='b863983db31da047348e5cac6b597668c3510441058c0d41263d3b205c5e8246'
OVERLAY_RELATIVE='docs/hongloumeng/translation/source-binding-ch002-ending.json'
OVERLAY_SHA256='14eaa0e376666857f957ce7b88ba0f1a64a7bd7c40b28c62f04e320d68211ccd'
PREVIOUS_SNAPSHOT='7786d177dead8a27301bf753835bec4e676c0a2b6f056269a6bf2464dab08696'
CURRENT_SNAPSHOT='f6326c33bb869033a215f845eb8e80c87950dc5197153f7fd325fca576a7cc89'
SEMANTIC_RECEIPT_SHA256='e1b76e44e6c5e9dc2f9ecea61312b0ddc0c7fd0a33588a909261479e086414bc'
SEMANTIC_REFERENCE='CH002-AUTHOR-ENDING-INDEPENDENT-SEMANTIC-DELTA-R1-20261111'
CURRENT_BINDING_REVIEW_SHA256='11731a2cd5b23ce4e0cc05fbe9341860ae0f5405fde392924616b4f1823e33a8'
TARGET='hlm-c002-b0039'

def load_parent(root):
    h=root/HISTORY_RELATIVE
    raw=regular(h,'history-manifest.json');require(sha(raw)==HISTORY_SHA256,'Chapter2 parent manifest changed')
    manifest=json.loads(raw)
    for p,digest in manifest['files'].items():
        require(sha(regular(h,p))==digest,'Chapter2 parent byte changed: '+p)
        if p.startswith('data/hongloumeng/first80-english/history/') or p.endswith('.before.json'):
            require(sha(regular(root,p))==digest,'Chapter2 existing historical archive changed: '+p)
    command=[sys.executable,'-B',str(h/'scripts/hongloumeng_english_pipeline.py'),'validate']
    result=subprocess.run(command,cwd=h,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
    require(result.returncode==0,'Chapter2 source4655 parent validation failed: '+result.stderr[-1000:])
    require(json.loads(result.stdout)=={'sourceUnits':4475,'states':{'accepted':2461,'pending':2014},'publishable':False},'Chapter2 wrong parent state')
    spec=importlib.util.spec_from_file_location('_chapter2_parent_pipeline',h/'scripts/hongloumeng_english_pipeline.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    require(module.standard_snapshot()==PREVIOUS_SNAPSHOT,'Chapter2 parent norm changed')
    return h,module

def validate_preparation(pipe,mapping,progress,*,exact_baseline=True,binding_reference=None,
                         normative_history=None,continuation_snapshot=None,continuation_reference=None):
    root=pipe.ROOT;h,parent=load_parent(root)
    # A later norm transition uses exact archived normative/metadata bytes only.
    # Sources, existing historical validators and author receipts still use root.
    # No override is accepted without all three tightly bound continuation fields.
    continuing = normative_history is not None
    require(continuing == (continuation_snapshot is not None) == (continuation_reference is not None),
            'Chapter2 incomplete normative continuation')
    normative_root = normative_history if continuing else root
    current_snapshot = continuation_snapshot if continuing else CURRENT_SNAPSHOT
    normative_names = tuple(parent.NORMATIVE_FILES)+('source-binding-ch002-ending.json',)
    if continuing:
        require(normative_root == root/B10_HISTORY_RELATIVE and continuation_snapshot == B10_SNAPSHOT
                and continuation_reference == B10_REFERENCE, 'Chapter2 wrong bounded continuation')
        authenticate_b10_history(root)
        require(sha(canonical({n:sha(regular(normative_root,'docs/hongloumeng/translation/'+n))
                    for n in normative_names})) == CURRENT_SNAPSHOT, 'Chapter2 archived norm changed')
    raw=regular(root,OVERLAY_RELATIVE);require(sha(raw)==OVERLAY_SHA256,'Chapter2 overlay changed');o=json.loads(raw)
    require(o['state']=='prospective_pending_current_binding_review' and o['publicationEnabled'] is False,'Chapter2 overlay scope changed')
    require(o['previousNormativeSnapshot']==PREVIOUS_SNAPSHOT and o['historyManifestSHA256']==HISTORY_SHA256,'Chapter2 overlay parent changed')
    require(pipe.standard_snapshot()==current_snapshot==pipe.EXPECTED_NORMATIVE_SNAPSHOT,'Chapter2 current norm changed')
    require(tuple(pipe.NORMATIVE_FILES)==normative_names+(('english-batch-046-050.json',) if continuing else ()),'Chapter2 norm scope expanded')
    for name in parent.NORMATIVE_FILES:
        rel='docs/hongloumeng/translation/'+name
        require(regular(normative_root,rel)==regular(h,rel),'Chapter2 prior normative bytes changed: '+name)
    receipt_raw=regular(root,'data/hongloumeng/first80-english/ch002-ending-semantic-review.json')
    require(sha(receipt_raw)==SEMANTIC_RECEIPT_SHA256,'Chapter2 semantic receipt changed');receipt=json.loads(receipt_raw)
    require(receipt['reference']==SEMANTIC_REFERENCE and receipt['target']==TARGET and receipt['mandatoryTranslationCorrections']==[],'Chapter2 semantic scope changed')
    require(receipt['currentNormativeSnapshot']==o['semanticReviewNormativeSnapshot'] and receipt['publicationEnabled'] is False,'Chapter2 old semantic context misrepresented')
    for path,digest in o['currentArtifactSHA256'].items():require(sha(regular(root,path))==digest,'Chapter2 artifact changed: '+path)
    before_map=read_json(h/'data/hongloumeng/first80-english/source-map.json');before=read_json(h/'data/hongloumeng/first80-english/progress.json');before_notes=read_json(h/'data/hongloumeng/first80-english/reader-notes.json')
    require(mapping==pipe.source_map(pipe.load_source())==read_json(pipe.DATA/'source-map.json'),'Chapter2 current source map differs')
    require(len(mapping['units'])==len(before_map['units'])==4475,'Chapter2 unit count differs')
    changed=[]
    for a,z in zip(before_map['units'],mapping['units']):
        require((a['id'],a['chapter'],a['index'],a['layout'])==(z['id'],z['chapter'],z['index'],z['layout']),'Chapter2 ID/layout/order changed')
        if a!=z:changed.append({'before':a,'after':z})
    require(changed==o['changedSourceUnits'] and len(changed)==1 and changed[0]['after']['id']==TARGET,'Chapter2 source amendment widened')
    require(changed[0]['after']['characterCount']-changed[0]['before']['characterCount']==12,'Chapter2 character delta changed')
    require(progress['sourceIssues'][:len(before['sourceIssues'])]==before['sourceIssues'],'Chapter2 old issue changed')
    source_by_id={u['id']:u for u in mapping['units']}
    require(all(source_by_id.get(i['unitId'],{}).get('chapter',0)>45 for i in progress['sourceIssues'][len(before['sourceIssues']):]),'Chapter2 new issue changes accepted source')
    suffix='; '+binding_reference if binding_reference else ''
    if continuing:suffix+='; '+continuation_reference
    for a,z,s in zip(before['units'],progress['units'],mapping['units']):
        expected=copy.deepcopy(a)
        for review in expected['reviews']:
            review['standardSnapshot']=current_snapshot;review['reference']+=suffix
        if a['id']==TARGET:
            expected.update(sourceHash=s['sourceHash'],segments=o['englishSegments'],state='accepted',reviews=[])
            for assessment in receipt['unitReviewAssessments']:
                require(assessment['verdict']=='PASS' and assessment['contentHash']==pipe.content_hash(expected,progress['sourceIssues'])==receipt['englishContentHash'],'Chapter2 genuine assessment content mismatch')
                expected['reviews'].append({'type':assessment['type'],'contentHash':assessment['contentHash'],'standardSnapshot':current_snapshot,'reference':SEMANTIC_REFERENCE+suffix})
        if a['state']=='accepted' or exact_baseline:require(z==expected,'Chapter2 accepted lineage or bounded unit delta changed: '+a['id'])
    checkpoints=copy.deepcopy(before['checkpoints'])
    for checkpoint in checkpoints[:9]:
        checkpoint['standardSnapshot']=current_snapshot;checkpoint['reviewReference']+=suffix
    checkpoints[0]['corpusHash']=receipt['cumulativeDelta']['corpusHash']
    checkpoints[0]['reviewReference']=before['checkpoints'][0]['reviewReference']+'; '+SEMANTIC_REFERENCE+suffix
    require(progress['checkpoints'][:9]==checkpoints[:9],'Chapter2 prior batch or scoped cumulative delta changed')
    notes=read_json(pipe.DATA/'reader-notes.json')
    require(notes['notes'][:len(before_notes['notes'])]==before_notes['notes'],'Chapter2 old note changed')
    if exact_baseline:
        require(progress['sourceIssues']==before['sourceIssues'] and len(progress['units'])==4475,'Chapter2 extra baseline records')
        require(notes==dict(before_notes,sourceHash=mapping['sourceHash']),'Chapter2 notes scope expanded')
        require(progress['checkpoints']==checkpoints,'Chapter2 future checkpoint changed in baseline')
    transition={'state':'pending_independent_current_binding_review','previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,'overlaySHA256':OVERLAY_SHA256,'historyManifestSHA256':HISTORY_SHA256,'semanticReference':SEMANTIC_REFERENCE,'semanticReceiptSHA256':SEMANTIC_RECEIPT_SHA256,'currentBindingReviewReference':binding_reference,'notFullCorpusReread':True,'publicationEnabled':False}
    if binding_reference:transition['state']='independently_reviewed_current_binding'
    for name in ('provenance.json','CHECKPOINT.json'):
        require(read_json(normative_root/'docs/hongloumeng/translation'/name)=={'schemaVersion':1,'status':transition['state'],'previousSource4655':read_json(h/'docs/hongloumeng/translation'/name),'chapter2AuthorEnding':transition},'Chapter2 transition metadata changed: '+name)
    stats=pipe.validate_progress(mapping,progress,current_snapshot);pipe.validate_reader_notes(mapping,notes)
    return {'status':'ENGINEERING_PREPARATION_PASS_BINDING_REVIEW_PENDING','normativeSnapshot':CURRENT_SNAPSHOT,'states':stats,'changedAcceptedUnits':1,'oldTargetReviewsPreserved':True,'parentProofUsedOnlyInExactParentContext':True,'publicationEnabled':False,'installationReady':False}

def validate_readiness(pipe,mapping,progress,**continuation):
    require(isinstance(CURRENT_BINDING_REVIEW_SHA256,str) and len(CURRENT_BINDING_REVIEW_SHA256)==64,'Chapter2 independent current-binding/engineering review pending')
    raw=regular(pipe.ROOT,'data/hongloumeng/first80-english/ch002-ending-current-binding-review.json')
    require(sha(raw)==CURRENT_BINDING_REVIEW_SHA256,'Chapter2 current binding receipt unpinned');r=json.loads(raw)
    require(r.get('status')=='PASS_SCOPED_CURRENT_BINDING_AND_ENGINEERING' and r.get('overlaySHA256')==OVERLAY_SHA256 and r.get('historyManifestSHA256')==HISTORY_SHA256 and r.get('semanticReceiptSHA256')==SEMANTIC_RECEIPT_SHA256 and r.get('previousNormativeSnapshot')==PREVIOUS_SNAPSHOT and r.get('normativeSnapshot')==CURRENT_SNAPSHOT and r.get('sourceHash')==pipe.READING_SHA and r.get('targetContentHash')=='504097d3d96b0e122f2fa7a02c6ac0a3865e5743bf3857e185bdf8a973bfebb9' and r.get('original13SemanticNormativeObjectsUnchanged') is True and r.get('scopedNormativeCompatibilityApproved') is True and r.get('notFullCorpusReread') is True and r.get('publicationApproved') is False and isinstance(r.get('reference'),str) and bool(r['reference'].strip()),'Chapter2 current binding review scope differs')
    validate_preparation(pipe,mapping,progress,exact_baseline=False,binding_reference=r['reference'],**continuation)
    return CURRENT_SNAPSHOT


# The B10 continuation is deliberately local to this one normative transition.
# It neither replaces historical receipt hashes nor creates a new framework.
B10_HISTORY_RELATIVE = 'data/hongloumeng/first80-english/history/v011-before'
B10_HISTORY_SHA256 = 'c93fc8108ef9f54835449cd1d3c08bbead3cd7638fba238210e1abc82928a347'
B10_SNAPSHOT = '8c2ef3dbbdc686f1f81ccab81f75c26590cf35bd441c5c2a96eac3e6785f8826'
B10_CORPUS_HASH = '83276ad0dfd321228e967aa24262cdc5c83dd194fff05c9fe5997346dacf2fe8'
B10_REFERENCE = 'EN-046-050-CURRENT-BINDING-INDEPENDENT-R1-20261111'
B10_RECEIPT_SHA256 = 'd531f596108cb112f3fc485491d6e393cd0e19285e70828761190dcff9ba1ab0'  # Real independent exact-current-binding review required.


def authenticate_b10_history(root):
    history = root/B10_HISTORY_RELATIVE
    raw = regular(history,'manifest.json')
    require(sha(raw)==B10_HISTORY_SHA256,'B10 historical manifest changed')
    manifest=json.loads(raw)
    require(manifest['normativeSnapshot']==CURRENT_SNAPSHOT,'B10 previous snapshot changed')
    for name,digest in manifest['files'].items():
        require(sha(regular(history,name))==digest,'B10 historical bytes changed: '+name)
    return history,manifest


def validate_batch046050_preparation(pipe,mapping,progress):
    """Exact proposed state checks only, never an independent approval receipt."""
    root=pipe.ROOT;history,manifest=authenticate_b10_history(root)
    require(pipe.standard_snapshot()==B10_SNAPSHOT==pipe.EXPECTED_NORMATIVE_SNAPSHOT,'B10 current norm changed')
    require(pipe.VERSION=='english-1-110-v0.11','B10 version differs')
    # Original source2 receipts retain their own old snapshot. This call checks
    # their source/author lineage with the narrowly authenticated norm suffix.
    validate_readiness(pipe,mapping,progress,normative_history=history,
                       continuation_snapshot=B10_SNAPSHOT,continuation_reference=B10_REFERENCE)
    before=read_json(history/'data/hongloumeng/first80-english/progress.json')
    oldnotes=read_json(history/'data/hongloumeng/first80-english/reader-notes.json')
    batch=read_json(pipe.STANDARD/'english-batch-046-050.json')
    require(batch['version']==pipe.VERSION and batch['status']=='frozen_editorial_checkpoint'
            and batch['freeze_id']=='english-v011-ch046-050-20261111' and batch['chapters']==list(range(46,51)),
            'B10 normative status differs')
    drafts=[]
    for row in batch['currentDraftBinding']['chapters']:
        raw=regular(root,'data/hongloumeng/first80-english/chapters/ch%03d.draft.json' % row['chapter'])
        require(sha(raw)==row['sha256'] and len(raw)==row['bytes'],'B10 final draft file changed')
        units=json.loads(raw)
        require(len(units)==row['unitCount'] and sum(len(u['segments']) for u in units)==row['segmentCount']
                and all(u['state']=='draft' and u['reviews']==[] for u in units),'B10 draft file inventory changed')
        drafts.extend(units)
    require(len(drafts)==402 and sha(canonical(drafts))==batch['currentDraftBinding']['fiveDraftCorpusSHA256'],
            'B10 authenticated draft corpus changed')
    sources=[u for u in mapping['units'] if 46<=u['chapter']<=50]
    require(batch['source_units']==sources and len(sources)==402,'B10 source units differ')
    binding=batch['sourceBinding']
    require(binding['sourceSHA256']==mapping['sourceHash']==pipe.READING_SHA
            and binding['sourceMapSHA256']==pipe.SOURCE_MAP_SHA
            and sha(regular(root,'data/hongloumeng/first80-english/source-map.json'))==pipe.SOURCE_MAP_SHA
            and binding['sourceAmendmentChapter2Included'] is True,'B10 source2 binding differs')
    expected_transition={'state':'scoped_editorial_checkpoint','version':pipe.VERSION,
        'previousNormativeSnapshot':CURRENT_SNAPSHOT,'normativeSnapshot':B10_SNAPSHOT,
        'historyManifestSHA256':B10_HISTORY_SHA256,'previousProgressSHA256':manifest['files']['data/hongloumeng/first80-english/progress.json'],
        'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,'currentCorpusHash':B10_CORPUS_HASH,
        'reviewReference':B10_REFERENCE,'currentBindingReceipt':'required_exact_independent_receipt',
        'notFullCorpusReread':True,'publicationEnabled':False}
    for name in ('provenance.json','CHECKPOINT.json'):
        metadata=read_json(pipe.STANDARD/name)
        expected={'schemaVersion':1,'status':'scoped_editorial_checkpoint',
            'previousChapter2AuthorEnding':read_json(history/'docs/hongloumeng/translation'/name),
            'normativeTransitionV011':expected_transition}
        if name=='CHECKPOINT.json':
            expected.update(version=pipe.VERSION,freeze_id=batch['freeze_id'],normative_snapshot=B10_SNAPSHOT,
                files=[{'path':'docs/hongloumeng/translation/'+n,
                        'sha256':sha(regular(root,'docs/hongloumeng/translation/'+n)),
                        'bytes':len(regular(root,'docs/hongloumeng/translation/'+n))} for n in pipe.NORMATIVE_FILES])
        require(metadata==expected,'B10 current metadata or predecessor changed: '+name)
    # Scope new issues to later work. Do not freeze the total number of later units,
    # reviews, notes or accepted checkpoints as the project progresses.
    source_by_id={u['id']:u for u in mapping['units']}
    require(progress['sourceIssues'][:len(before['sourceIssues'])]==before['sourceIssues']
            and all(source_by_id.get(i['unitId'],{}).get('chapter',0)>50
                    for i in progress['sourceIssues'][len(before['sourceIssues']):]),'B10 source issue scope changed')
    current=[u for s,u in zip(mapping['units'],progress['units']) if 46<=s['chapter']<=50]
    if any(u['reviews'] for u in current) or progress['checkpoints'][9]['state']=='accepted':
        require(pipe.batch_hash(current,progress['sourceIssues'])==B10_CORPUS_HASH,'B10 reviewed corpus changed')
    for u in current:
        require(all(r['reference']==B10_REFERENCE for r in u['reviews']),'B10 review lineage changed')
    if progress['checkpoints'][9]['state']=='accepted':
        require(progress['checkpoints'][9]['reviewReference']==B10_REFERENCE,'B10 checkpoint lineage changed')
    notes=read_json(pipe.DATA/'reader-notes.json');selected=batch['selectedReaderNotes']
    require(len(selected)==18,'B10 note selection differs')
    expected_notes=oldnotes['notes']+[{'unitId':n['anchor']['unitId'],'sourceHash':n['anchor']['sourceHash'],
        'glossaryId':'english-batch-046-050.json#/selectedReaderNotes/'+str(i),'type':'translator_note',
        'text':n['text'],'presentationStatus':'not_integrated_in_reading_presentation'} for i,n in enumerate(selected)]
    require(notes['notes'][:len(expected_notes)]==expected_notes,'B10 prior or selected note changed')
    require(all(source_by_id.get(n['unitId'],{}).get('chapter',0)>50 for n in notes['notes'][len(expected_notes):]),
            'B10 later note overlaps protected prefix')
    by_id={u['id']:u for u in current}
    for n in selected:
        a=n['anchor'];u=by_id[a['unitId']]
        if u['segments']:
            require(u['sourceHash']==a['sourceHash']
                and u['segments'][a['segmentIndex']]['text'][a['start']:a['end']]==a['text'], 'B10 note anchor changed')
    stats=pipe.validate_progress(mapping,progress,B10_SNAPSHOT);pipe.validate_reader_notes(mapping,notes)
    return {'status':'B10_PREPARATION_PASS_INDEPENDENT_CURRENT_BINDING_REQUIRED',
            'states':stats,'normativeSnapshot':B10_SNAPSHOT,'publicationEnabled':False,'installationReady':False}


def validate_batch046050_readiness(pipe,mapping,progress):
    require(isinstance(B10_RECEIPT_SHA256,str) and len(B10_RECEIPT_SHA256)==64,
            'B10 independent exact current-binding review pending')
    raw=regular(pipe.ROOT,'data/hongloumeng/first80-english/b10-current-binding-review.json')
    require(sha(raw)==B10_RECEIPT_SHA256,'B10 current-binding receipt changed')
    r=json.loads(raw)
    expected={'status':'PASS_SCOPED_CURRENT_BINDING','reference':B10_REFERENCE,'requiredFindings':[],
        'previousNormativeSnapshot':CURRENT_SNAPSHOT,'normativeSnapshot':B10_SNAPSHOT,
        'historyManifestSHA256':B10_HISTORY_SHA256,'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,
        'currentCorpusHash':B10_CORPUS_HASH,'supportedExistingUnits':2461,'supportedExistingReviewSlots':7383,
        'supportedExistingCheckpoints':9,'supportedCurrentUnits':402,'supportedCurrentSegments':1083,
        'supportedCurrentReviewSlots':1206,'selectedReaderNotes':18,'preservedOldReaderNotes':43,
        'exactFinalNormativeDeltaApproved':True,'oldAcceptedBodiesUnchanged':True,'notFullCorpusReread':True,
        'publicationApproved':False}
    require(all(r.get(k)==v for k,v in expected.items()),'B10 independent receipt scope differs')
    validate_batch046050_preparation(pipe,mapping,progress)
    return B10_SNAPSHOT
