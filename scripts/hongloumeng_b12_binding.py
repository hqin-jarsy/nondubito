"""Bounded B12 continuation over the genuine receipt-bound source5665 context.

This authenticates prior readings without relabeling them as fresh reviews.
Preparation is mechanical only. Current readiness needs separate real semantic
and technical receipts. Historical runtime regression uses a finite fixture.
"""
import copy,json
from pathlib import Path
from hongloumeng_source4655_binding import regular,sha,canonical,require,read_json
D='data/hongloumeng/first80-english/'
S='docs/hongloumeng/translation/'
E=D+'b12-evidence/'
HISTORY_RELATIVE=D+'history/v013-before'
HISTORY_SHA256='d8119a2638d7a2cb17ca053c1393c64c10b930f206d13f717cf547dad95c7183'
OVERLAY_RELATIVE=S+'english-binding-056-060.json'
OVERLAY_SHA256='2d91243680b964680da0acb2a626c5e7dd35e9ab671030ede15f9343d9d6f80d'
PREVIOUS_SNAPSHOT='cbcf8cd3d72957563db33c12c22ad04a8a8aaffd2345020ebc06a1af21370d5f'
CURRENT_SNAPSHOT='cf0790b6191679fac2d5d2826b96d2d4ac7ce0966eb44592e1f0e3aa4be77c33'
REFERENCE='EN-056-060-CURRENT-BINDING-INDEPENDENT-R1-20261112'
TECHNICAL_REFERENCE='EN-056-060-TECHNICAL-INDEPENDENT-R1-20261112'
SEMANTIC_RECEIPT_SHA256='d86d2ab238df867fb413def1a5df64e0625e2d50386a72fe493c6e99f55339cd'
TECHNICAL_RECEIPT_SHA256='ef49b8c2a9c35a3e8a815defa6f17c6d961afdf4e6dcb2de45ed3815d6de7b00'


def authenticate_history(root):
    h=root/HISTORY_RELATIVE
    raw=regular(h,'manifest.json');require(sha(raw)==HISTORY_SHA256,'B12 historical manifest changed')
    manifest=json.loads(raw)
    require(manifest['normativeSnapshot']==PREVIOUS_SNAPSHOT,'B12 prior normative snapshot changed')
    for p,digest in manifest['files'].items():require(sha(regular(h,p))==digest,'B12 archived predecessor changed: '+p)
    for p,digest in manifest['unchangedRootFiles'].items():require(sha(regular(root,p))==digest,'B12 unchanged predecessor changed: '+p)
    require(not set(manifest['files'])&set(manifest['unchangedRootFiles']),'B12 ambiguous predecessor paths')
    return h,manifest


def materialize_predecessor(root,destination):
    """Regression-only finite exact public source5665 fixture, never a ROOT copy."""
    h,manifest=authenticate_history(root)
    destination=Path(destination)
    require(not destination.is_symlink(),'B12 symlink output')
    destination=destination.resolve();require(not destination.exists(),'B12 predecessor output exists')
    destination.mkdir()
    for p in sorted(set(manifest['files'])|set(manifest['unchangedRootFiles'])):
        raw=regular(h if p in manifest['files'] else root,p)
        target=destination/p;require(destination in target.parents,'B12 output escapes fixture')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    return destination


def transition(overlay,approved=False):
    return {'state':'independently_reviewed_B12_current_binding' if approved else 'pending_independent_B12_current_binding_review',
        'version':'english-1-110-v0.13','previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,
        'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,
        'sourceHash':overlay['sourceHash'],'sourceMapSHA256':overlay['sourceMapSHA256'],'currentCorpusHash':overlay['currentCorpusHash'],
        'semanticCurrentBindingReviewReference':REFERENCE,'technicalReviewReference':TECHNICAL_REFERENCE,
        'receiptStatus':'verified_genuine_independent_receipts' if approved else 'required_genuine_independent_receipts',
        'newUnits':233,'newSegments':939,'newNotes':3,'acceptedBodiesChanged':0,'notFullCorpusReread':True,'publicationEnabled':False}


def corpus(units):
    return [{'id':u['id'],'sourceHash':u['sourceHash'],'segments':u['segments']} for u in units]


def authenticate_readings(root,drafts,overlay):
    for p,digest in overlay['evidence'].items():require(sha(regular(root,p))==digest,'B12 reading evidence changed: '+p)
    evidence=lambda name:read_json(root/E/name)
    full=evidence('full-manifest.json');delta=evidence('delta-manifest.json');review=evidence('delta-review.json')
    require(full['status']=='REVISION_REQUIRED' and delta['status']==review['status']=='PASS','B12 historical review outcome changed')
    require(review['priorFullReviewManifestSHA256']==sha(regular(root,E+'full-manifest.json')) and review['remainingRequiredFixes']==[] and review['newReading']['fullFiveChapterReread'] is False,'B12 invented full reread or unresolved findings')
    exports={'full-unit-assessments.json':(full,'per-unit-review.json'),'full-continuous-reading.json':(full,'continuous-reading.json'),
             'full-corpus-binding.json':(full,'corpus-bindings.json'),'prior-ch057.draft.json':(full,'inputs/ch057.draft.json'),
             'delta-review.json':(delta,'review.json'),'current-unit-assessments.json':(delta,'current-unit-status.json'),
             'current-corpus-binding.json':(delta,'corpus-bindings.json'),'exact-delta.json':(delta,'exact-delta.json'),'delta-limited-reading.json':(delta,'limited-reading.json')}
    for target,(manifest,source) in exports.items():
        row=next(x for x in manifest['files'] if x['path']==source)
        require(sha(regular(root,E+target))==row['sha256'],'B12 original evidence manifest binding differs')
    current_hash=sha(canonical(corpus(drafts)))
    require(review['orderedCorpusSHA256']==delta['orderedCorpusSHA256']==overlay['orderedCorpusSHA256']==current_hash,'B12 exact cumulative corpus changed')
    prior57=evidence('prior-ch057.draft.json');prior=[]
    for row in overlay['draftFiles']:
        prior.extend(prior57 if row['chapter']==57 else read_json(root/row['path']))
    require(sha(canonical(corpus(prior)))==full['corpusSHA256']==evidence('full-corpus-binding.json')['orderedCorpusSHA256'],'B12 original full-reading corpus changed')
    current=evidence('current-unit-assessments.json')['items'];old=evidence('full-unit-assessments.json')['items']
    require(len(current)==len(old)==len(prior)==len(drafts)==233,'B12 reading coverage differs')
    differences=[]
    for a,z,ar,zr in zip(prior,drafts,old,current):
        require(a['id']==z['id']==ar['id']==zr['id'] and a['sourceHash']==z['sourceHash']==ar['sourceHash']==zr['sourceHash'],'B12 reading identity/source changed')
        require(sha(canonical(a['segments']))==ar['EnglishSegmentsSHA256'] and sha(canonical(z['segments']))==zr['EnglishSegmentsSHA256'] and zr['status']=='PASS','B12 current review content binding changed')
        require(isinstance(ar['assessment'],str) and ar['assessment'].strip() and isinstance(zr['assessment'],str) and zr['assessment'].strip(),'B12 missing genuine assessments')
        require({k:v for k,v in a.items() if k!='segments'}=={k:v for k,v in z.items() if k!='segments'} and len(a['segments'])==len(z['segments']),'B12 unexpected cumulative metadata delta')
        for i,(x,y) in enumerate(zip(a['segments'],z['segments'])):
            if x!=y:differences.append({'id':a['id'],'segmentOneBased':i+1,'before':x,'after':y})
    require(differences==evidence('exact-delta.json')['changes'] and len(differences)==2 and {x['id'] for x in differences}=={'hlm-c057-b0029'},'B12 cumulative delta scope changed')
    public=evidence('public-review.json');manifest=evidence('public-projection-manifest.json')
    require(public['verdict']=='PASS' and public['requiredCorrections']==[] and public['subject']['manifestSHA256']==sha(regular(root,E+'public-projection-manifest.json')) and public['subject']['publicSemanticSubjectSHA256']==overlay['publicSemanticSubjectSHA256']==manifest['publicSemanticSubjectSHA256'],'B12 public semantic approval differs')
    require(overlay['publicFiles']=={S+Path(x['path']).name:x['sha256'] for x in manifest['publicFiles']},'B12 public four-file scope differs')


def validate_preparation(pipe,mapping,progress,*,exact_baseline=True,approved=False):
    root=pipe.ROOT;h,manifest=authenticate_history(root)
    raw=regular(root,OVERLAY_RELATIVE);require(sha(raw)==OVERLAY_SHA256,'B12 binding overlay changed');overlay=json.loads(raw)
    require(overlay['state']=='prospective_B12_current_binding_pending_independent_review' and overlay['publicationEnabled'] is False,'B12 fabricated projection approval')
    require(pipe.VERSION=='english-1-110-v0.13' and tuple(pipe.NORMATIVE_FILES)==tuple(manifest['normativeFiles'])+('english-batch-056-060.json','english-binding-056-060.json'),'B12 normative scope differs')
    require(pipe.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT==CURRENT_SNAPSHOT,'B12 merged normative snapshot changed')
    prior_hashes={n:(manifest['files'] if S+n in manifest['files'] else manifest['unchangedRootFiles'])[S+n] for n in manifest['normativeFiles']}
    require(sha(canonical(prior_hashes))==PREVIOUS_SNAPSHOT,'B12 predecessor normative identity differs')
    for p,digest in overlay['publicFiles'].items():require(sha(regular(root,p))==digest,'B12 exact public guidance changed: '+p)
    before=read_json(h/D/'progress.json');oldnotes=read_json(h/D/'reader-notes.json')
    require(mapping==pipe.source_map(pipe.load_source())==read_json(pipe.DATA/'source-map.json'),'B12 current source map differs')
    require(mapping['sourceHash']==overlay['sourceHash']==pipe.READING_SHA and sha(regular(root,D+'source-map.json'))==overlay['sourceMapSHA256']==pipe.SOURCE_MAP_SHA,'B12 current source binding differs')
    require(progress['sourceHash']==before['sourceHash']==mapping['sourceHash'] and progress['standardVersion']==pipe.VERSION,'B12 current progress metadata differs')
    batch=read_json(pipe.STANDARD/'english-batch-056-060.json');sources=[s for s in mapping['units'] if 56<=s['chapter']<=60]
    require(sources==overlay['currentSourceUnits'] and len(sources)==233,'B12 current source-unit scope differs')
    drafts=[]
    for row in overlay['draftFiles']:
        raw=regular(root,row['path']);require(sha(raw)==row['sha256'] and len(raw)==row['bytes'],'B12 exact draft changed');drafts.extend(json.loads(raw))
    require(len(drafts)==233 and sum(len(u['segments']) for u in drafts)==939 and pipe.batch_hash(drafts,progress['sourceIssues'])==overlay['currentCorpusHash'],'B12 draft corpus differs')
    for u,s,r in zip(drafts,sources,batch['source_units']):
        require(u['id']==s['id']==r['id'] and u['sourceHash']==s['sourceHash']==r['selectedSourceHash'] and sha(canonical(u['segments']))==r['englishSegmentsSHA256'],'B12 projected source or English body differs')
        require(u['state']=='draft' and u['reviews']==[],'B12 original drafts were relabeled as fresh accepted reviews')
    authenticate_readings(root,drafts,overlay)
    require(regular(root,S+'english-standard.md').startswith(regular(h,S+'english-standard.md')),'B12 earlier standard text changed')
    terms=read_json(h/S/'english-terms.json');terms['version']=pipe.VERSION;terms['batch_glossaries'].append('english-batch-056-060.json')
    require(read_json(pipe.STANDARD/'english-terms.json')==terms,'B12 earlier terms changed')
    voices=read_json(h/S/'english-voices.json');voices['version']=pipe.VERSION;voices['batch_056_060_details']=batch['voices']
    require(read_json(pipe.STANDARD/'english-voices.json')==voices,'B12 earlier voices changed')
    source_by_id={s['id']:s for s in mapping['units']};new={u['id']:u for u in drafts}
    require(len(progress['units'])==len(before['units'])==len(mapping['units'])==4475,'B12 unit count changed')
    require(progress['sourceIssues'][:len(before['sourceIssues'])]==before['sourceIssues'] and all(source_by_id.get(i['unitId'],{}).get('chapter',0)>60 for i in progress['sourceIssues'][len(before['sourceIssues']):]),'B12 prior source issue changed')
    reviewref='EN-B056-060-CUMULATIVE-20261112; EN-B056-060-CUMULATIVE-R2-DELTA-20261112; '+REFERENCE
    expected=copy.deepcopy(before);expected['standardVersion']=pipe.VERSION
    for a,z,s in zip(expected['units'],progress['units'],mapping['units']):
        if a['id'] in new:
            require(a['state']=='pending' and not a['segments'] and not a['reviews'],'B12 new acceptance overlaps old accepted content')
            a.update(copy.deepcopy(new[a['id']]));a['state']='accepted';a['reviews']=[{'type':t,'contentHash':pipe.content_hash(a,progress['sourceIssues']),'standardSnapshot':CURRENT_SNAPSHOT,'reference':reviewref} for t in pipe.REVIEW_TYPES]
        else:
            for r in a['reviews']:r['standardSnapshot']=CURRENT_SNAPSHOT;r['reference']+='; '+REFERENCE
        if s['chapter']<=60 or exact_baseline:require(z==a,'B12 body or review lineage changed: '+a['id'])
    for cp in expected['checkpoints'][:11]:cp['standardSnapshot']=CURRENT_SNAPSHOT;cp['reviewReference']+='; '+REFERENCE
    expected['checkpoints'][11].update(state='accepted',corpusHash=overlay['currentCorpusHash'],standardSnapshot=CURRENT_SNAPSHOT,reviewReference=reviewref)
    require(progress['checkpoints'][:12]==expected['checkpoints'][:12],'B12 checkpoint lineage changed')
    if exact_baseline:require(progress==expected,'B12 unexpected prospective progress delta')
    notes=read_json(pipe.DATA/'reader-notes.json');selected=batch['selectedReaderNotes']
    require([n['id'] for n in selected]==overlay['selectedReaderNoteIDs']==['B12-NOTE01','B12-NOTE02','B12-NOTE05'],'B12 selected note scope changed')
    selection=read_json(root/E/'note-selection.json')['selected']
    require(len(selection)==3 and all(n['id']==r['id'] and sha(canonical(n))==r['selectedPublicObjectSHA256'] for n,r in zip(selected,selection)),'B12 genuine coordinator note selection changed')
    expected_notes=oldnotes['notes']+[{'unitId':n['anchor']['unitId'],'sourceHash':n['anchor']['sourceHash'],'glossaryId':'english-batch-056-060.json#/selectedReaderNotes/'+str(i),'type':'translator_note','text':n['text'],'presentationStatus':'not_integrated_in_reading_presentation'} for i,n in enumerate(selected)]
    require(notes['sourceHash']==mapping['sourceHash'] and notes['notes'][:69]==expected_notes and len(oldnotes['notes'])==66,'B12 prior or selected note changed')
    require(all(source_by_id.get(n['unitId'],{}).get('chapter',0)>60 for n in notes['notes'][69:]),'B12 extra note overlaps protected prefix')
    for n in selected:
        a=n['anchor'];u=new[a['unitId']];text=u['segments'][a['segmentIndex']]['text']
        require(a['start']==0 and a['end']==len(text) and a['text']==text and a['position']=='after_anchor' and a['sourceHash']==u['sourceHash'] and sha(n['text'])==n['textSHA256'] and sha(text)==a['segmentTextSHA256'],'B12 full-segment note binding changed')
    if exact_baseline:require(notes==dict(oldnotes,notes=expected_notes),'B12 unexpected note delta')
    tr=transition(overlay,approved)
    for name in ('provenance.json','CHECKPOINT.json'):
        require(read_json(pipe.STANDARD/name)=={'schemaVersion':1,'status':tr['state'],'previousSource5665':read_json(h/S/name),'b12Transition':tr},'B12 metadata or original context changed')
    stats=pipe.validate_progress(mapping,progress,CURRENT_SNAPSHOT);pipe.validate_reader_notes(mapping,notes)
    return {'status':'B12_PREPARATION_PASS_INDEPENDENT_CURRENT_BINDING_REQUIRED' if not approved else 'B12_RECEIPT_BOUND_CURRENT_BINDING_PASS','states':stats,'normativeSnapshot':CURRENT_SNAPSHOT,'newUnits':233,'newNotes':3,'acceptedBodiesChanged':0,'installationAuthorized':False,'publicationEnabled':False}


def validate_readiness(pipe,mapping,progress):
    overlay=read_json(pipe.ROOT/OVERLAY_RELATIVE)
    for kind,digest,ref in [('semantic',SEMANTIC_RECEIPT_SHA256,REFERENCE),('technical',TECHNICAL_RECEIPT_SHA256,TECHNICAL_REFERENCE)]:
        require(isinstance(digest,str) and len(digest)==64,'B12 independent '+kind+' current-binding review pending')
        raw=regular(pipe.ROOT,D+'b12-'+kind+'-review.json');require(sha(raw)==digest,'B12 unpinned '+kind+' receipt');receipt=json.loads(raw)
        expected={'status':'PASS_SCOPED_CURRENT_BINDING','reviewKind':kind,'reference':ref,'requiredFindings':[],
            'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,
            'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,'currentCorpusHash':overlay['currentCorpusHash'],'orderedCorpusSHA256':overlay['orderedCorpusSHA256'],
            'newUnits':233,'newSegments':939,'selectedReaderNotes':3,'preservedOldReaderNotes':66,'preservedSourceIssues':16,'preservedAcceptedBodies':3155,'acceptedBodiesChanged':0,
            'exactMergedNormApproved':True,'oldHistoricalContextsPreserved':True,'priorFullReviewAndFinalDeltaAuthenticated':True,'notFullCorpusReread':True,'publicationApproved':False}
        require(all(receipt.get(k)==v for k,v in expected.items()),'B12 incomplete '+kind+' current-binding receipt')
    validate_preparation(pipe,mapping,progress,exact_baseline=False,approved=True)
    return CURRENT_SNAPSHOT
