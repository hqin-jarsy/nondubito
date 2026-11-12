"""Bounded B14 continuation over the genuine receipt-bound source6680 context.

This authenticates prior readings without relabeling them as fresh reviews.
Preparation is mechanical only. Current readiness needs separate real semantic
and technical receipts. Historical runtime regression uses a finite fixture.
"""
import copy,json
from pathlib import Path
from hongloumeng_source4655_binding import regular,sha,canonical,require,read_json
D='data/hongloumeng/first80-english/'
S='docs/hongloumeng/translation/'
E=D+'b14-evidence/'
HISTORY_RELATIVE=D+'history/v015-before'
HISTORY_SHA256='351980e5bdf6fc814f99688d18e4e9998a5841ef55cfc3c5f7b409cab891002e'
OVERLAY_RELATIVE=S+'english-binding-066-070.json'
OVERLAY_SHA256='25f65be26cb220c800362acc56acced1e785044eeadf6dfab76d8dffc9233ff0'
PREVIOUS_SNAPSHOT='f665d4fa0a3c1816ffbfd408f4143007f96b74a80aa429ebbfbfd61eb46f45c7'
CURRENT_SNAPSHOT='fef2273f310025de1756b63868da4709122bac81800d07c92576bea52500c3a2'
REFERENCE='EN-066-070-CURRENT-BINDING-INDEPENDENT-R1-20261112'
TECHNICAL_REFERENCE='EN-066-070-TECHNICAL-INDEPENDENT-R1-20261112'
SEMANTIC_RECEIPT_SHA256='3394ecd1c3a9331220fb3848043a7d0d80ca19c801f22f4d1ebd3ff1aae411fa'
TECHNICAL_RECEIPT_SHA256='2e739b81228717459d2b2ba228c05afd0aea458543f408c9f235f9df857842f3'


def authenticate_history(root):
    h=root/HISTORY_RELATIVE
    raw=regular(h,'manifest.json');require(sha(raw)==HISTORY_SHA256,'B14 historical manifest changed')
    manifest=json.loads(raw)
    require(manifest['normativeSnapshot']==PREVIOUS_SNAPSHOT,'B14 prior normative snapshot changed')
    for p,digest in manifest['files'].items():require(sha(regular(h,p))==digest,'B14 archived predecessor changed: '+p)
    for p,digest in manifest['unchangedRootFiles'].items():require(sha(regular(root,p))==digest,'B14 unchanged predecessor changed: '+p)
    require(not set(manifest['files'])&set(manifest['unchangedRootFiles']),'B14 ambiguous predecessor paths')
    return h,manifest


def materialize_predecessor(root,destination):
    """Regression-only finite exact public source6680 fixture, never a ROOT copy."""
    h,manifest=authenticate_history(root)
    destination=Path(destination)
    require(not destination.is_symlink(),'B14 symlink output')
    destination=destination.resolve();require(not destination.exists(),'B14 predecessor output exists')
    destination.mkdir()
    for p in sorted(set(manifest['files'])|set(manifest['unchangedRootFiles'])):
        raw=regular(h if p in manifest['files'] else root,p)
        target=destination/p;require(destination in target.parents,'B14 output escapes fixture')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    return destination


def transition(overlay,approved=False):
    return {'state':'independently_reviewed_B14_current_binding' if approved else 'pending_independent_B14_current_binding_review',
        'version':'english-1-110-v0.15','previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,
        'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,'sourceHash':overlay['sourceHash'],
        'sourceMapSHA256':overlay['sourceMapSHA256'],'currentCorpusHash':overlay['currentCorpusHash'],
        'newUnits':224,'newSegments':911,'newNotes':4,'acceptedBodiesChanged':0,'notFullCorpusReread':True,'publicationEnabled':False}


def corpus(units):
    return [{'id':u['id'],'sourceHash':u['sourceHash'],'segments':u['segments']} for u in units]


def authenticate_readings(root,drafts,overlay):
    for p,digest in overlay['evidence'].items():require(sha(regular(root,p))==digest,'B14 reading evidence changed: '+p)
    evidence=read_json(root/E/'reading-lineage.json');rows=evidence['units'];chapters=evidence['chapters'];cumulative=evidence['cumulative']
    require(len(rows)==len(drafts)==224 and [c['chapter'] for c in chapters]==list(range(66,71)),'B14 genuine reading scope changed')
    require(sha(canonical(drafts))==overlay['orderedCorpusSHA256'],'B14 final reviewed corpus changed')
    require(cumulative['verdict']=='PASS_CUMULATIVE_LITERARY_CONTINUITY_REVIEW' and cumulative['completeFinalEnglishRead'] is True and cumulative['completeChineseContextsRead']==224 and cumulative['units']==224 and cumulative['segments']==911 and cumulative['words']==28602 and cumulative['requiredEnglishCorrections']==cumulative['optionalEnglishRewrites']==0,'B14 cumulative approval differs')
    changes=0
    for unit,row in zip(drafts,rows):
        require(unit['id']==row['id'] and unit['sourceHash']==row['sourceHash'] and sha(canonical(unit['segments']))==row['finalSegmentsSHA256'],'B14 reviewed unit differs')
        prior=copy.deepcopy(unit['segments']);a=row['historicalAssessment'];require(a.get('id',a.get('sourceID'))==unit['id'] and a.get('sourceHash',a.get('workingZhSHA256'))==unit['sourceHash'],'B14 historical review identity differs')
        for delta in row['exactSuccessorChanges']:
            i=delta['segmentIndex'];require(prior[i]['text']==delta['after'],'B14 bounded successor changed');prior[i]['text']=delta['before'];changes+=1
        require(sha(canonical(prior))==row['historicalSegmentsSHA256'],'B14 historical reading reconstruction differs')
    require(changes==9,'B14 bounded change scope differs')
    require(all(c['fullReviewInherited'] is True and c['boundedVerdict'].startswith('PASS') and c['finalDraftSHA256']==f['sha256'] for c,f in zip(chapters,overlay['draftFiles'])),'B14 final chapter approval differs')
    public=evidence['publicReview'];require(public['verdict']=='PASS_SCOPED_PUBLIC_PROJECTION' and public['requiredChanges']==[] and public['optionalChanges']==[] and public['subjectManifestSHA256']==overlay['publicProjectionManifestSHA256'] and public['publicSemanticSubjectSHA256']==overlay['publicSemanticSubjectSHA256'],'B14 independent public approval differs')


def validate_preparation(pipe,mapping,progress,*,exact_baseline=True,approved=False):
    root=pipe.ROOT;h,manifest=authenticate_history(root)
    raw=regular(root,OVERLAY_RELATIVE);require(sha(raw)==OVERLAY_SHA256,'B14 binding overlay changed');overlay=json.loads(raw)
    require(overlay['state']=='prospective_B14_current_binding_pending_independent_review' and overlay['publicationEnabled'] is False,'B14 fabricated projection approval')
    require(pipe.VERSION=='english-1-110-v0.15' and tuple(pipe.NORMATIVE_FILES)==tuple(manifest['normativeFiles'])+('english-batch-066-070.json','english-binding-066-070.json'),'B14 normative scope differs')
    require(pipe.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT==CURRENT_SNAPSHOT,'B14 merged normative snapshot changed')
    prior_hashes={n:(manifest['files'] if S+n in manifest['files'] else manifest['unchangedRootFiles'])[S+n] for n in manifest['normativeFiles']}
    require(sha(canonical(prior_hashes))==PREVIOUS_SNAPSHOT,'B14 predecessor normative identity differs')
    for p,digest in overlay['publicFiles'].items():require(sha(regular(root,p))==digest,'B14 exact public guidance changed: '+p)
    before=read_json(h/D/'progress.json');oldnotes=read_json(h/D/'reader-notes.json')
    require(mapping==pipe.source_map(pipe.load_source())==read_json(pipe.DATA/'source-map.json'),'B14 current source map differs')
    require(mapping['sourceHash']==overlay['sourceHash']==pipe.READING_SHA and sha(regular(root,D+'source-map.json'))==overlay['sourceMapSHA256']==pipe.SOURCE_MAP_SHA,'B14 current source binding differs')
    require(progress['sourceHash']==before['sourceHash']==mapping['sourceHash'] and progress['standardVersion']==pipe.VERSION,'B14 current progress metadata differs')
    batch=read_json(pipe.STANDARD/'english-batch-066-070.json');sources=[s for s in mapping['units'] if 66<=s['chapter']<=70]
    require(sources==overlay['currentSourceUnits'] and len(sources)==224,'B14 current source-unit scope differs')
    drafts=[]
    for row in overlay['draftFiles']:
        raw=regular(root,row['path']);require(sha(raw)==row['sha256'] and len(raw)==row['bytes'],'B14 exact draft changed');drafts.extend(json.loads(raw))
    require(len(drafts)==224 and sum(len(u['segments']) for u in drafts)==911 and pipe.batch_hash(drafts,progress['sourceIssues'])==overlay['currentCorpusHash'],'B14 draft corpus differs')
    for u,s in zip(drafts,sources):
        require(u['id']==s['id'] and u['sourceHash']==s['sourceHash'],'B14 projected source or English body differs')
        require(u['state']=='draft' and u['reviews']==[],'B14 original drafts were relabeled as fresh accepted reviews')
    authenticate_readings(root,drafts,overlay)
    require(regular(root,S+'english-standard.md').startswith(regular(h,S+'english-standard.md')),'B14 earlier standard text changed')
    terms=read_json(h/S/'english-terms.json');terms['version']=pipe.VERSION;terms['batch_glossaries'].append('english-batch-066-070.json')
    require(read_json(pipe.STANDARD/'english-terms.json')==terms,'B14 earlier terms changed')
    voices=read_json(h/S/'english-voices.json');voices['version']=pipe.VERSION;voices['batch_066_070_details']=batch['voices']
    require(read_json(pipe.STANDARD/'english-voices.json')==voices,'B14 earlier voices changed')
    source_by_id={s['id']:s for s in mapping['units']};new={u['id']:u for u in drafts}
    require(len(progress['units'])==len(before['units'])==len(mapping['units'])==4475,'B14 unit count changed')
    require(progress['sourceIssues'][:len(before['sourceIssues'])]==before['sourceIssues'] and all(source_by_id.get(i['unitId'],{}).get('chapter',0)>70 for i in progress['sourceIssues'][len(before['sourceIssues']):]),'B14 prior source issue changed')
    reviewref='EN-B066-070-CUMULATIVE-INDEPENDENT-R1-20261112; '+REFERENCE
    expected=copy.deepcopy(before);expected['standardVersion']=pipe.VERSION
    for a,z,s in zip(expected['units'],progress['units'],mapping['units']):
        if a['id'] in new:
            require(a['state']=='pending' and not a['segments'] and not a['reviews'],'B14 new acceptance overlaps old accepted content')
            a.update(copy.deepcopy(new[a['id']]));a['state']='accepted';a['reviews']=[{'type':t,'contentHash':pipe.content_hash(a,progress['sourceIssues']),'standardSnapshot':CURRENT_SNAPSHOT,'reference':reviewref} for t in pipe.REVIEW_TYPES]
        else:
            for r in a['reviews']:r['standardSnapshot']=CURRENT_SNAPSHOT;r['reference']+='; '+REFERENCE
        if s['chapter']<=70 or exact_baseline:require(z==a,'B14 body or review lineage changed: '+a['id'])
    for cp in expected['checkpoints'][:13]:cp['standardSnapshot']=CURRENT_SNAPSHOT;cp['reviewReference']+='; '+REFERENCE
    expected['checkpoints'][13].update(state='accepted',corpusHash=overlay['currentCorpusHash'],standardSnapshot=CURRENT_SNAPSHOT,reviewReference=reviewref)
    require(progress['checkpoints'][:14]==expected['checkpoints'][:14],'B14 checkpoint lineage changed')
    if exact_baseline:require(progress==expected,'B14 unexpected prospective progress delta')
    notes=read_json(pipe.DATA/'reader-notes.json');selected=batch['selectedReaderNotes']
    require([n['id'] for n in selected]==overlay['selectedReaderNoteIDs']==['B14-N03','B14-N04','B14-N05','B14-N08'] and sha(canonical(selected))==overlay['selectedReaderNotesSHA256'],'B14 selected note scope changed')
    expected_notes=oldnotes['notes']+[{'unitId':n['anchor']['unitId'],'sourceHash':new[n['anchor']['unitId']]['sourceHash'],'glossaryId':'english-batch-066-070.json#/selectedReaderNotes/'+str(i),'type':'translator_note','text':n['text'],'presentationStatus':'not_integrated_in_reading_presentation'} for i,n in enumerate(selected)]
    require(notes['sourceHash']==mapping['sourceHash'] and notes['notes'][:76]==expected_notes and len(oldnotes['notes'])==72,'B14 prior or selected note changed')
    require(all(source_by_id.get(n['unitId'],{}).get('chapter',0)>70 for n in notes['notes'][76:]),'B14 extra note overlaps protected prefix')
    for n in selected:
        a=n['anchor'];u=new[a['unitId']];text=u['segments'][a['segmentIndex']]['text']
        require(0<=a['start']<a['end']<=len(text) and a['text']==text[a['start']:a['end']] and a['position']=='after_anchor','B14 full-segment note binding changed')
    if exact_baseline:require(notes==dict(oldnotes,notes=expected_notes),'B14 unexpected note delta')
    tr=transition(overlay,approved)
    for name in ('provenance.json','CHECKPOINT.json'):
        require(read_json(pipe.STANDARD/name)=={'schemaVersion':1,'status':tr['state'],'previousSource6680':read_json(h/S/name),'b14Transition':tr},'B14 metadata or original context changed')
    stats=pipe.validate_progress(mapping,progress,CURRENT_SNAPSHOT);pipe.validate_reader_notes(mapping,notes)
    return {'status':'B14_PREPARATION_PASS_INDEPENDENT_CURRENT_BINDING_REQUIRED' if not approved else 'B14_RECEIPT_BOUND_CURRENT_BINDING_PASS','states':stats,'normativeSnapshot':CURRENT_SNAPSHOT,'newUnits':224,'newNotes':4,'acceptedBodiesChanged':0,'installationAuthorized':False,'publicationEnabled':False}


def validate_readiness(pipe,mapping,progress):
    overlay=read_json(pipe.ROOT/OVERLAY_RELATIVE)
    for kind,digest,ref in [('semantic',SEMANTIC_RECEIPT_SHA256,REFERENCE),('technical',TECHNICAL_RECEIPT_SHA256,TECHNICAL_REFERENCE)]:
        require(isinstance(digest,str) and len(digest)==64,'B14 independent '+kind+' current-binding review pending')
        raw=regular(pipe.ROOT,D+'b14-'+kind+'-review.json');require(sha(raw)==digest,'B14 unpinned '+kind+' receipt');receipt=json.loads(raw)
        expected={'status':'PASS_SCOPED_CURRENT_BINDING','reviewKind':kind,'reference':ref,'requiredFindings':[],
            'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,
            'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,'currentCorpusHash':overlay['currentCorpusHash'],'orderedCorpusSHA256':overlay['orderedCorpusSHA256'],
            'newUnits':224,'newSegments':911,'selectedReaderNotes':4,'preservedOldReaderNotes':72,'preservedSourceIssues':16,'preservedAcceptedBodies':3672,'acceptedBodiesChanged':0,
            'exactMergedNormApproved':True,'oldHistoricalContextsPreserved':True,'priorFullReviewAndFinalDeltaAuthenticated':True,'notFullCorpusReread':True,'publicationApproved':False}
        require(all(receipt.get(k)==v for k,v in expected.items()),'B14 incomplete '+kind+' current-binding receipt')
    validate_preparation(pipe,mapping,progress,exact_baseline=False,approved=True)
    return CURRENT_SNAPSHOT
