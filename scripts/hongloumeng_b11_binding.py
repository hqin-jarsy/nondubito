"""Bounded B11 and chapter25 acceptance delta over an authenticated B10 context.

Historical validation is performed on historical content, not on changed accepted
units. This preparation function is not an independent reading or approval.
Normal readiness requires the separate genuine exact-current-binding receipt.
"""
import copy,importlib.util,json,re,sys
from pathlib import Path
from hongloumeng_source4655_binding import regular,sha,canonical,require,read_json
HISTORY_RELATIVE='data/hongloumeng/first80-english/history/v012-before'
HISTORY_SHA256='c7184ecc86e756c304123a01a64e951a9fa87681290def20cf1cdb847b11906e'
PREVIOUS_SNAPSHOT='8c2ef3dbbdc686f1f81ccab81f75c26590cf35bd441c5c2a96eac3e6785f8826'
CURRENT_SNAPSHOT='9e49d30c44c8dadcb22da5da3abb8e1762b66fdbb871e74797aaafcdf496fab1'
REFERENCE='EN-051-055-AND-025-CURRENT-BINDING-INDEPENDENT-R1-20261112'
CORPUS_HASH='f6283a40ee0e763475b343b69dc9604276a3f854be0a2a6d0b8d31b5a2257ee5'
BATCH5_CORPUS_HASH='cfac632853c0413c6a91496bbd2ba0c7b6abf93f66c3d3c38065dbd1e78cc220'
EVIDENCE={'data/hongloumeng/first80-english/b11-evidence/full-review-manifest.json': '8e380b06db1674f01b4cc564c5c49bb146a81dabb798ed5dc1fea22b8eacbeeb', 'data/hongloumeng/first80-english/b11-evidence/full-review-receipt.json': '0ef6ecb48366f531e5b90599cfdb326d176f946d04adb330569e3f85fcc339d7', 'data/hongloumeng/first80-english/b11-evidence/term-review-manifest.json': '6da2dc0871587009034dd8c4214c27afcd1928b8dea06fe9543e7e505072fbb3', 'data/hongloumeng/first80-english/b11-evidence/current-draft-binding.json': '5c9a3b85e5efe851562138c2329fad959399641e4bf093e31c1e7633592edbf5', 'data/hongloumeng/first80-english/b11-evidence/accepted25-impact.json': 'c75415c36bcb04109758cbf36e4a2e3ece98084e2a82d40a45391b9b0b6ac08e', 'data/hongloumeng/first80-english/b11-evidence/content-assessments.json': 'c54f0faea07e27eab695835e02cd0debea638dee44271731d6f97842ee648f98', 'data/hongloumeng/first80-english/b11-evidence/accepted25-proposed-units.json': '336c2e06c6a43aeafc6a1966bb9be42dabeb05811eb6e09401d9f12aa3cb3bd6', 'data/hongloumeng/first80-english/b11-evidence/public-projection-review.json': 'a8688058d15b5de82576401df74916fc489cceeeb17c4040b75c2b5852d87dd7'}
RECEIPT_SHA256='3156f5e9072b2d959f1d37f2efc93978c0d10f336973b58b5528fd05221416d7'  # Must be populated only from a genuine independent review.
D='data/hongloumeng/first80-english/'
S='docs/hongloumeng/translation/'
E=D+'b11-evidence/'


def authenticate_history(root):
    h=root/HISTORY_RELATIVE
    raw=regular(h,'manifest.json');require(sha(raw)==HISTORY_SHA256,'B11 historical manifest changed')
    manifest=json.loads(raw)
    require(manifest['normativeSnapshot']==PREVIOUS_SNAPSHOT,'B11 prior snapshot differs')
    for p,digest in manifest['files'].items():
        require(sha(regular(h,p))==digest,'B11 historical bytes changed: '+p)
    for p,digest in manifest['unchangedRootFiles'].items():
        require(sha(regular(root,p))==digest,'B11 unchanged predecessor byte changed: '+p)
    return h,manifest


def load_parent(root):
    h,manifest=authenticate_history(root)
    # The exact prior code and mutable context are archived once. Source, genuine
    # receipts and previous archives use their unchanged original locations.
    # This is a read-only context selection, not a rewrite of historical inputs.
    name='_b11_exact_b10_parent'
    spec=importlib.util.spec_from_file_location(name,h/'scripts/hongloumeng_english_pipeline.py')
    p=importlib.util.module_from_spec(spec);sys.modules[name]=p;spec.loader.exec_module(p)
    p.ROOT=root;p.DATA=h/D;p.STANDARD=h/S;p.SOURCE=root/'data/hongloumeng/first80-public'
    mapping=p.source_map(p.load_source());before=read_json(h/D/'progress.json')
    require(p.standard_snapshot()==PREVIOUS_SNAPSHOT,'B11 exact parent norm differs')
    # Original B10 code has a few explicit ROOT/standard reads while its other
    # reads use STANDARD. Give that original module only the same authenticated
    # historical norm view. No source, receipt, validation rule or digest changes.
    parent_spec=importlib.util.spec_from_file_location('_b11_exact_b10_binding',root/'scripts/hongloumeng_ch002_ending_binding.py')
    binding=importlib.util.module_from_spec(parent_spec);parent_spec.loader.exec_module(binding)
    def historical_regular(base,relative):
        if base==root and relative in manifest['files'] and relative.startswith(S):
            return regular(h,relative)
        return regular(base,relative)
    binding.regular=historical_regular
    require(binding.validate_batch046050_readiness(p,mapping,before)==PREVIOUS_SNAPSHOT,'B11 parent readiness failed')
    require(p.validate_progress(mapping,before,PREVIOUS_SNAPSHOT)=={'accepted':2863,'pending':1612},'B11 exact parent counts differ')
    return h,manifest,p,mapping,before


def pointer(value,path):
    for key in path.split('/')[1:]:
        key=key.replace('~1','/').replace('~0','~')
        value=value[int(key)] if isinstance(value,list) else value[key]
    return value


def validate_preparation(pipe,mapping,progress):
    root=pipe.ROOT;h,manifest,parent,parent_mapping,before=load_parent(root)
    require(mapping==parent_mapping==pipe.source_map(pipe.load_source())==read_json(pipe.DATA/'source-map.json'),'B11 current source map differs')
    require(pipe.READING_SHA==mapping['sourceHash'] and pipe.SOURCE_MAP_SHA==sha(regular(root,D+'source-map.json')),'B11 source file binding differs')
    require(pipe.VERSION=='english-1-110-v0.12' and tuple(pipe.NORMATIVE_FILES)==tuple(parent.NORMATIVE_FILES)+('english-batch-051-055.json',),'B11 norm scope differs')
    require(pipe.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT==CURRENT_SNAPSHOT,'B11 current norm changed')
    for p,digest in EVIDENCE.items():require(sha(regular(root,p))==digest,'B11 historical evidence changed: '+p)
    batch=read_json(pipe.STANDARD/'english-batch-051-055.json')
    require(batch['version']==pipe.VERSION and batch['status']=='frozen_editorial_checkpoint' and batch['freeze_id']=='english-v012-ch051-055-20261112','B11 normative state differs')
    sources=[s for s in mapping['units'] if 51<=s['chapter']<=55]
    require(batch['currentSourceUnits']==sources and len(sources)==292,'B11 exact source units differ')
    binding=batch['sourceBinding']
    require(binding['sourceSHA256']==pipe.READING_SHA and binding['sourceMapSHA256']==pipe.SOURCE_MAP_SHA and binding['chapter2Included'] is True,'B11 source2 binding differs')
    reading=pipe.load_source()
    for a,z in zip(batch['source_units'],sources):
        require(a['id']==z['id'] and a['proposedSourceHash']==z['sourceHash'] and sha(pointer(reading,a['sourcePointer']).encode())==z['sourceHash'],'B11 historical-to-current source identity differs')
    for row in batch['historicalNormReferences']:
        require(sha(canonical(pointer(read_json(root/row['originalPath']),row['originalPointer'])))==row['originalObjectCanonicalSHA256'],'B11 historical term or voice object changed')
    require(len(batch['historicalNormReferences'])==299,'B11 historical object inventory differs')
    terms=read_json(pipe.STANDARD/'english-terms.json');oldterms=read_json(h/S/'english-terms.json')
    expected=copy.deepcopy(oldterms);expected['version']=pipe.VERSION;expected['batch_glossaries'].append('english-batch-051-055.json')
    require(terms==expected,'B11 existing terms or batch list changed')
    voices=read_json(pipe.STANDARD/'english-voices.json');expected=read_json(h/S/'english-voices.json');expected['version']=pipe.VERSION;expected['batch_051_055_details']=batch['voices']['voices']
    require(voices==expected,'B11 old voices changed or new voices differ')
    drafts=[]
    for row in batch['currentDraftBinding']['files']:
        raw=regular(root,D+'chapters/ch%03d.draft.json'%row['chapter'])
        require(sha(raw)==row['sha256'] and len(raw)==row['bytes'],'B11 exact draft file changed')
        drafts.extend(json.loads(raw))
    require(len(drafts)==292 and sum(len(u['segments']) for u in drafts)==995 and sha(canonical(drafts))==batch['currentDraftBinding']['fiveDraftCorpusSHA256'],'B11 final draft corpus differs')
    receipt=read_json(root/E/'current-draft-binding.json')
    require(receipt['newFullCorpusReading'] is False and receipt['fiveDraftCorpusSHA256']==sha(canonical(drafts)),'B11 historical full/limited review scope differs')
    for u,s,r in zip(drafts,sources,receipt['units']):
        require(u['id']==s['id']==r['unitId'] and u['sourceHash']==s['sourceHash']==r['sourceHash'] and sha(canonical(u['segments']))==r['englishSegmentsSHA256'],'B11 final reviewed body binding differs')
    # Exact two-unit exception: accepted source proof is never reused for it.
    proposed25=read_json(root/E/'accepted25-proposed-units.json');impact=read_json(root/E/'accepted25-impact.json')
    assessments=read_json(root/E/'content-assessments.json')
    oldbyid={u['id']:u for u in before['units']}
    require([u['id'] for u in proposed25]==['hlm-c025-b0012','hlm-c025-b0013'],'B11 accepted25 scope expanded')
    tokens=0
    for u,r in zip(proposed25,impact['units']):
        a=oldbyid[u['id']]
        require(a['sourceHash']==u['sourceHash']==r['sourceHash'] and pipe.content_hash(a,before['sourceIssues'])==r['beforePipelineContentHash'] and pipe.content_hash(u,before['sourceIssues'])==r['proposedPipelineContentHash'],'B11 accepted25 content or source differs')
        require(len(a['segments'])==len(u['segments']),'B11 accepted25 segment count differs')
        count=0
        for x,y in zip(a['segments'],u['segments']):
            require(x['kind']==y['kind'] and x['text']==y['text'].replace('catties','jin').replace('catty','jin'),'B11 accepted25 non-weight text changed')
            count+=len(re.findall(r'\bjin\b',x['text']))
        require(count==r['tokens'],'B11 accepted25 token count differs');tokens+=count
        assessment=next(x for x in assessments['assessments'] if x['unitId']==u['id'])
        require(assessment['verdict']=='PASS_UNINSTALLED_PROPOSAL_LIMITED_DELTA' and assessment['contentBinding']['proposedPipelineContentHash']==r['proposedPipelineContentHash'],'B11 accepted25 genuine semantic evidence differs')
    require(tokens==8,'B11 accepted25 eight-token limit differs')
    source_by_id={s['id']:s for s in mapping['units']}
    require(progress['sourceIssues'][:len(before['sourceIssues'])]==before['sourceIssues'] and all(source_by_id.get(i['unitId'],{}).get('chapter',0)>55 for i in progress['sourceIssues'][len(before['sourceIssues']):]),'B11 existing source issue changed')
    new={u['id']:u for u in drafts+proposed25}
    for a,z,s in zip(before['units'],progress['units'],mapping['units']):
        if s['chapter']>55:continue
        expected=copy.deepcopy(new.get(a['id'],a))
        if a['id'] in new:
            expected['state']='accepted';expected['reviews']=[{'type':t,'contentHash':pipe.content_hash(expected,progress['sourceIssues']),'standardSnapshot':CURRENT_SNAPSHOT,'reference':REFERENCE} for t in pipe.REVIEW_TYPES]
        else:
            for r in expected['reviews']:r['standardSnapshot']=CURRENT_SNAPSHOT;r['reference']+='; '+REFERENCE
        require(z==expected,'B11 accepted body or review lineage changed: '+a['id'])
    cps=copy.deepcopy(before['checkpoints'][:11])
    for cp in cps[:10]:cp['standardSnapshot']=CURRENT_SNAPSHOT;cp['reviewReference']+='; '+REFERENCE
    cps[4]['corpusHash']=BATCH5_CORPUS_HASH;cps[4]['reviewReference']+='; EN-025-048-053-054-TERM-ALIGNMENT-INDEPENDENT-R1 (limited chapter25 delta only)'
    cps[10].update(state='accepted',corpusHash=CORPUS_HASH,standardSnapshot=CURRENT_SNAPSHOT,reviewReference=REFERENCE)
    require(progress['checkpoints'][:11]==cps,'B11 batch5 delta or checkpoint lineage changed')
    require(before['checkpoints'][4]['corpusHash']==impact['checkpoint21to25']['before'] and BATCH5_CORPUS_HASH==impact['checkpoint21to25']['conditionalAfter'],'B11 old batch5 impact context differs')
    notes=read_json(pipe.DATA/'reader-notes.json');oldnotes=read_json(h/D/'reader-notes.json');selected=batch['selectedReaderNotes']
    require(len(selected)==5,'B11 selected note inventory differs')
    expected_notes=oldnotes['notes']+[{'unitId':n['anchor']['unitId'],'sourceHash':n['anchor']['sourceHash'],'glossaryId':'english-batch-051-055.json#/selectedReaderNotes/'+str(i),'type':'translator_note','text':n['text'],'presentationStatus':'not_integrated_in_reading_presentation'} for i,n in enumerate(selected)]
    require(notes['notes'][:66]==expected_notes,'B11 prior or selected note changed')
    require(all(source_by_id.get(n['unitId'],{}).get('chapter',0)>55 for n in notes['notes'][66:]),'B11 extra note overlaps protected prefix')
    byid={u['id']:u for u in progress['units']}
    for n in selected:
        a=n['anchor'];u=byid[a['unitId']];text=u['segments'][a['segmentIndex']]['text']
        require(a['start']==0 and a['end']==len(text) and a['position']=='after_anchor' and text==a['text'] and a['sourceHash']==u['sourceHash'] and sha(n['text'].encode())==n['textSHA256'],'B11 exact complete-segment note anchor differs')
    transition={'state':'scoped_editorial_checkpoint','version':pipe.VERSION,'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,'historyManifestSHA256':HISTORY_SHA256,'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,'currentCorpusHash':CORPUS_HASH,'batch5DeltaCorpusHash':BATCH5_CORPUS_HASH,'reviewReference':REFERENCE,'currentBindingReceipt':'required_exact_independent_receipt','accepted25ChangedUnits':2,'notFullCorpusReread':True,'publicationEnabled':False}
    for name in ('provenance.json','CHECKPOINT.json'):
        expected={'schemaVersion':1,'status':'scoped_editorial_checkpoint','previousB10':read_json(h/S/name),'normativeTransitionV012':transition}
        if name=='CHECKPOINT.json':expected.update(version=pipe.VERSION,freeze_id=batch['freeze_id'],normative_snapshot=CURRENT_SNAPSHOT,files=[{'path':S+n,'sha256':sha(regular(root,S+n)),'bytes':len(regular(root,S+n))} for n in pipe.NORMATIVE_FILES])
        require(read_json(pipe.STANDARD/name)==expected,'B11 transition metadata or prior context changed')
    stats=pipe.validate_progress(mapping,progress,CURRENT_SNAPSHOT);pipe.validate_reader_notes(mapping,notes)
    return {'status':'B11_ENGINEERING_PREPARATION_PASS_CURRENT_BINDING_REQUIRED','normativeSnapshot':CURRENT_SNAPSHOT,'states':stats,'changedAccepted25Units':2,'publicationEnabled':False,'installationReady':False}


def validate_readiness(pipe,mapping,progress):
    require(isinstance(RECEIPT_SHA256,str) and len(RECEIPT_SHA256)==64,'B11 independent exact current-binding and accepted25 review pending')
    raw=regular(pipe.ROOT,D+'b11-current-binding-review.json');require(sha(raw)==RECEIPT_SHA256,'B11 current-binding receipt changed')
    receipt=json.loads(raw)
    expected={'status':'PASS_SCOPED_CURRENT_BINDING_AND_TECHNICAL','reference':REFERENCE,'requiredFindings':[],'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,'historyManifestSHA256':HISTORY_SHA256,'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,'currentCorpusHash':CORPUS_HASH,'batch5DeltaCorpusHash':BATCH5_CORPUS_HASH,'newUnits':292,'newSegments':995,'selectedReaderNotes':5,'preservedOldReaderNotes':61,'preservedSourceIssues':16,'preservedAcceptedBodies':2861,'changedAccepted25Units':2,'exactMergedNormApproved':True,'accepted25FreshCurrentContentReview':True,'batch5LimitedDeltaApproved':True,'oldHistoricalContextsPreserved':True,'notFullCorpusReread':True,'publicationApproved':False}
    require(all(receipt.get(k)==v for k,v in expected.items()),'B11 independent review scope differs')
    proposed=read_json(pipe.ROOT/E/'accepted25-proposed-units.json')
    assessments=receipt.get('accepted25UnitAssessments',[])
    require(len(assessments)==6,'B11 six genuine new accepted25 assessments required')
    for assessment,(unit,kind) in zip(assessments,[(u,t) for u in proposed for t in pipe.REVIEW_TYPES]):
        require(assessment.get('unitId')==unit['id'] and assessment.get('type')==kind
                and assessment.get('contentHash')==pipe.content_hash(unit,progress['sourceIssues'])
                and assessment.get('sourceHash')==unit['sourceHash'] and assessment.get('verdict')=='PASS'
                and isinstance(assessment.get('assessment'),str) and bool(assessment['assessment'].strip()),
                'B11 accepted25 fresh current assessment differs')
    delta=receipt.get('batch5DeltaReview',{})
    require(delta.get('beforeCorpusHash')=='0e517c5e038c812608e0a9d427bef6bb7264a4672063a4b4cc15a6ad71c7dc4e'
            and delta.get('afterCorpusHash')==BATCH5_CORPUS_HASH and delta.get('status')=='PASS_LIMITED_DELTA'
            and delta.get('newFullBatchReading') is False and isinstance(delta.get('assessment'),str)
            and bool(delta['assessment'].strip()),'B11 explicit limited batch5 delta assessment required')
    validate_preparation(pipe,mapping,progress)
    return CURRENT_SNAPSHOT
