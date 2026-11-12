"""Bounded B13 continuation over the genuine receipt-bound B12 context.

This authenticates prior readings without relabeling them as fresh reviews.
Preparation is mechanical only. Current readiness needs separate real semantic
and technical receipts. Historical runtime regression uses a finite fixture.
"""
import copy,json
from pathlib import Path
from hongloumeng_source4655_binding import regular,sha,canonical,require,read_json
D='data/hongloumeng/first80-english/'
S='docs/hongloumeng/translation/'
E=D+'b13-evidence/'
HISTORY_RELATIVE=D+'history/v014-before'
HISTORY_SHA256='2838cd7ae769e06d26340415d18e5b2b0eabe8b0176d146d7ed33ae3f7dadcf7'
OVERLAY_RELATIVE=S+'english-binding-061-065.json'
OVERLAY_SHA256='b936b97a67250f803390e76bbe6cc207d421d0d0ae7eb611ce8c8f0ae6a92575'
PREVIOUS_SNAPSHOT='cf0790b6191679fac2d5d2826b96d2d4ac7ce0966eb44592e1f0e3aa4be77c33'
CURRENT_SNAPSHOT='77478ba611615b9de857967893482789016bc5587726be1d412e5eba4f6b4201'
REFERENCE='EN-061-065-CURRENT-BINDING-INDEPENDENT-R1-20261112'
TECHNICAL_REFERENCE='EN-061-065-TECHNICAL-INDEPENDENT-R1-20261112'
SEMANTIC_RECEIPT_SHA256='a80bfffd5499420c7e3c3a99967ac92a01076f229b4f68b9d8f5c51922d1d4c3'
TECHNICAL_RECEIPT_SHA256='f12d8977d8728d417970da0735c5caf261a4568f8a02a472d8e36d0dba491e63'


def authenticate_history(root):
    h=root/HISTORY_RELATIVE
    raw=regular(h,'manifest.json');require(sha(raw)==HISTORY_SHA256,'B13 historical manifest changed')
    manifest=json.loads(raw)
    require(manifest['normativeSnapshot']==PREVIOUS_SNAPSHOT,'B13 prior normative snapshot changed')
    for p,digest in manifest['files'].items():require(sha(regular(h,p))==digest,'B13 archived predecessor changed: '+p)
    for p,digest in manifest['unchangedRootFiles'].items():require(sha(regular(root,p))==digest,'B13 unchanged predecessor changed: '+p)
    require(not set(manifest['files'])&set(manifest['unchangedRootFiles']),'B13 ambiguous predecessor paths')
    return h,manifest


def materialize_predecessor(root,destination):
    """Regression-only finite exact public B12 fixture, never a ROOT copy."""
    h,manifest=authenticate_history(root)
    destination=Path(destination)
    require(not destination.is_symlink(),'B13 symlink output')
    destination=destination.resolve();require(not destination.exists(),'B13 predecessor output exists')
    destination.mkdir()
    for p in sorted(set(manifest['files'])|set(manifest['unchangedRootFiles'])):
        raw=regular(h if p in manifest['files'] else root,p)
        target=destination/p;require(destination in target.parents,'B13 output escapes fixture')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    return destination


def transition(overlay,approved=False):
    return {'state':'independently_reviewed_B13_current_binding' if approved else 'pending_independent_B13_current_binding_review',
        'version':'english-1-110-v0.14','previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,
        'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,
        'sourceHash':overlay['sourceHash'],'sourceMapSHA256':overlay['sourceMapSHA256'],'currentCorpusHash':overlay['currentCorpusHash'],
        'semanticCurrentBindingReviewReference':REFERENCE,'technicalReviewReference':TECHNICAL_REFERENCE,
        'receiptStatus':'verified_genuine_independent_receipts' if approved else 'required_genuine_independent_receipts',
        'newUnits':284,'newSegments':1118,'newNotes':3,'acceptedBodiesChanged':0,'metadataKindChanges':14,'metadataReviewReference':overlay['metadataReviewReference'],'reviewedOrderedCorpusSHA256':overlay['reviewedOrderedCorpusSHA256'],'notFullCorpusReread':True,'publicationEnabled':False}


def corpus(units):
    return [{'id':u['id'],'sourceHash':u['sourceHash'],'segments':u['segments']} for u in units]


def authenticate_readings(root,drafts,overlay):
    for p,digest in overlay['evidence'].items():require(sha(regular(root,p))==digest,'B13 reading evidence changed: '+p)
    evidence=lambda name:read_json(root/E/name)
    for row in overlay['evidenceProvenance']:
        manifest=evidence(row['manifest']);source=next(v for v in manifest['files'] if v['path']==row['originalPath'])
        require(sha(regular(root,E+row['export']))==source['sha256'],'B13 original evidence manifest binding differs')
    full=evidence('full-manifest.json');delta=evidence('delta-manifest.json');review=evidence('delta-review.json')
    require(full['verdict']=='REQUIRED_CUMULATIVE_CHANGES' and review['verdict']=='PASS_BOUNDED_CUMULATIVE_RECHECK','B13 historical review outcome changed')
    require(review['priorFullReviewManifestSHA256']==sha(regular(root,E+'full-manifest.json')) and review['remainingRequiredFindingIDs']==[],'B13 unresolved findings or full-review identity changed')
    require(review['subjectManifestSHA256']==sha(regular(root,E+'correction-manifest.json')),'B13 reviewed successor differs')
    kind_review=evidence('kind-review.json');kind_manifest=evidence('kind-manifest.json');kind_binding=evidence('kind-corpus-binding.json');kind_delta=evidence('kind-delta.json')['changes']
    require(kind_review['verdict']=='PASS_METADATA_KIND_NORMALIZATION' and kind_review['requiredCorrections']==[] and kind_review['subjectManifestSHA256']==sha(regular(root,E+'kind-manifest.json')),'B13 genuine metadata approval differs')
    require(kind_review['sourceSHA256']==overlay['sourceHash'] and kind_review['sourceMapSHA256']==overlay['sourceMapSHA256'] and kind_review['kindChanges']==14 and kind_review['textChanged'] is False and kind_review['segmentBoundariesChanged'] is False and kind_review['allLineBreaksPreserved'] is True and kind_review['selectedNoteAnchorsPreserved'] is True and kind_review['publicationApproved'] is False,'B13 metadata approval scope differs')
    normalized_hash=sha(canonical(drafts))
    require(normalized_hash==overlay['orderedCorpusSHA256']==kind_review['finalCorpusCanonicalSHA256']==kind_manifest['finalCorpusCanonicalSHA256']==kind_binding['finalOrderedCorpusSHA256'],'B13 normalized corpus changed')
    reviewed=copy.deepcopy(drafts);byid={u['id']:u for u in reviewed};source_by_id={u['id']:u for u in overlay['currentSourceUnits']}
    require(len(kind_delta)==14 and len({r['sourceID'] for r in kind_delta})==14 and overlay['metadataKindChanges']==14 and overlay['metadataReviewReference']==kind_review['reviewID'],'B13 finite kind delta scope differs')
    for row in kind_delta:
        unit=byid[row['sourceID']];segment=unit['segments'][row['segmentIndexZeroBased']];source=source_by_id[unit['id']]
        require(unit['sourceHash']==row['sourceHash']==source['sourceHash'] and source['layout']==row['sourceLayout'] and segment['kind']==row['afterKind']==source['layout']['kind'] and row['beforeKind']=='verse','B13 kind/source binding differs')
        require(sha(canonical(unit['segments']))==row['afterUnitSegmentsSHA256'] and sha(segment['text'])==row['completeTextSHA256'] and segment['text'].count('\n')==row['newlineCount'] and len(segment['text'].splitlines())==row['lineCount'],'B13 metadata changed text or lineation')
        segment['kind']=row['beforeKind']
        require(sha(canonical(unit['segments']))==row['beforeUnitSegmentsSHA256'],'B13 inverse kind transformation differs')
    current_hash=sha(canonical(reviewed))
    require(review['finalCorpusCanonicalSHA256']==overlay['reviewedOrderedCorpusSHA256']==kind_review['beforeCorpusCanonicalSHA256']==kind_manifest['beforeCorpusCanonicalSHA256']==kind_binding['beforeOrderedCorpusSHA256']==current_hash,'B13 historical reviewed corpus reconstruction differs')
    actions=evidence('exact-delta.json')['draftActions'];prior=copy.deepcopy(reviewed);byid={u['id']:u for u in prior}
    require(len(actions)==11 and len({(r['sourceID'],r['segmentIndex']) for r in actions})==11,'B13 final delta scope differs')
    for row in actions:
        unit=byid[row['sourceID']];seg=unit['segments'][row['segmentIndex']]
        require(unit['sourceHash']==row['sourceHash'] and seg['text']==row['after'] and sha(seg['text'])==row['afterTextSHA256'],'B13 exact changed segment differs')
        seg['text']=row['before']
    bindings=evidence('current-corpus-binding.json')
    require(sha(canonical(prior))==bindings['beforeOrderedCorpusSHA256'] and current_hash==bindings['finalOrderedCorpusSHA256'],'B13 preserved corpus reconstruction differs')
    assessments=[]
    for chapter in range(61,66):assessments.extend(evidence('full-ch%03d-assessments.json'%chapter))
    require(len(assessments)==len(drafts)==284,'B13 full reading coverage differs')
    for old,row in zip(prior,assessments):
        require(old['id']==row['sourceID'] and old['sourceHash']==row['sourceHash'] and sha(canonical(old['segments']))==row['segmentsSHA256'],'B13 authentic full-reading body differs')
        require(row['bilingualRead'] is True and row['separateEnglishRead'] is True and isinstance(row['assessment'],str) and row['assessment'].strip(),'B13 missing genuine full assessment')
    public=evidence('public-review.json');manifest=evidence('public-projection-manifest.json')
    require(public['verdict']=='PASS' and public['requiredCorrections']==[] and public['subject']['manifestSHA256']==sha(regular(root,E+'public-projection-manifest.json')) and public['subject']['publicSemanticSubjectSHA256']==overlay['publicSemanticSubjectSHA256']==manifest['publicSemanticSubjectSHA256'],'B13 independent public semantic review differs')
    require(overlay['publicFiles']=={S+Path(x['path']).name:x['sha256'] for x in manifest['publicFiles']},'B13 public four-file scope differs')


def validate_preparation(pipe,mapping,progress,*,exact_baseline=True,approved=False):
    root=pipe.ROOT;h,manifest=authenticate_history(root)
    raw=regular(root,OVERLAY_RELATIVE);require(sha(raw)==OVERLAY_SHA256,'B13 binding overlay changed');overlay=json.loads(raw)
    require(overlay['state']=='prospective_B13_current_binding_pending_independent_review' and overlay['publicationEnabled'] is False,'B13 fabricated projection approval')
    require(pipe.VERSION=='english-1-110-v0.14' and tuple(pipe.NORMATIVE_FILES)==tuple(manifest['normativeFiles'])+('english-batch-061-065.json','english-binding-061-065.json'),'B13 normative scope differs')
    require(pipe.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT==CURRENT_SNAPSHOT,'B13 merged normative snapshot changed')
    prior_hashes={n:(manifest['files'] if S+n in manifest['files'] else manifest['unchangedRootFiles'])[S+n] for n in manifest['normativeFiles']}
    require(sha(canonical(prior_hashes))==PREVIOUS_SNAPSHOT,'B13 predecessor normative identity differs')
    for p,digest in overlay['publicFiles'].items():require(sha(regular(root,p))==digest,'B13 exact public guidance changed: '+p)
    before=read_json(h/D/'progress.json');oldnotes=read_json(h/D/'reader-notes.json')
    require(mapping==pipe.source_map(pipe.load_source())==read_json(pipe.DATA/'source-map.json'),'B13 current source map differs')
    require(mapping['sourceHash']==overlay['sourceHash']==pipe.READING_SHA and sha(regular(root,D+'source-map.json'))==overlay['sourceMapSHA256']==pipe.SOURCE_MAP_SHA,'B13 current source binding differs')
    require(progress['sourceHash']==before['sourceHash']==mapping['sourceHash'] and progress['standardVersion']==pipe.VERSION,'B13 current progress metadata differs')
    batch=read_json(pipe.STANDARD/'english-batch-061-065.json');sources=[s for s in mapping['units'] if 61<=s['chapter']<=65]
    require(sources==overlay['currentSourceUnits'] and len(sources)==284,'B13 current source-unit scope differs')
    drafts=[]
    for row in overlay['draftFiles']:
        raw=regular(root,row['path']);require(sha(raw)==row['sha256'] and len(raw)==row['bytes'],'B13 exact draft changed');drafts.extend(json.loads(raw))
    require(len(drafts)==284 and sum(len(u['segments']) for u in drafts)==1118 and pipe.batch_hash(drafts,progress['sourceIssues'])==overlay['currentCorpusHash'],'B13 draft corpus differs')
    for u,s in zip(drafts,sources):
        require(u['id']==s['id'] and u['sourceHash']==s['sourceHash'],'B13 projected source or English body differs')
        require(u['state']=='draft' and u['reviews']==[],'B13 original drafts were relabeled as fresh accepted reviews')
    authenticate_readings(root,drafts,overlay)
    require(regular(root,S+'english-standard.md').startswith(regular(h,S+'english-standard.md')),'B13 earlier standard text changed')
    terms=read_json(h/S/'english-terms.json');terms['version']=pipe.VERSION;terms['batch_glossaries'].append('english-batch-061-065.json')
    require(read_json(pipe.STANDARD/'english-terms.json')==terms,'B13 earlier terms changed')
    voices=read_json(h/S/'english-voices.json');voices['version']=pipe.VERSION;voices['batch_061_065_details']=batch['voices']
    require(read_json(pipe.STANDARD/'english-voices.json')==voices,'B13 earlier voices changed')
    source_by_id={s['id']:s for s in mapping['units']};new={u['id']:u for u in drafts}
    require(len(progress['units'])==len(before['units'])==len(mapping['units'])==4475,'B13 unit count changed')
    require(progress['sourceIssues'][:len(before['sourceIssues'])]==before['sourceIssues'] and all(source_by_id.get(i['unitId'],{}).get('chapter',0)>65 for i in progress['sourceIssues'][len(before['sourceIssues']):]),'B13 prior source issue changed')
    reviewref='EN-061-065-CUMULATIVE-REVIEW-R1-20261112; EN-B061-065-CUMULATIVE-REVIEW-R2; '+overlay['metadataReviewReference']+'; '+REFERENCE
    expected=copy.deepcopy(before);expected['standardVersion']=pipe.VERSION
    for a,z,s in zip(expected['units'],progress['units'],mapping['units']):
        if a['id'] in new:
            require(a['state']=='pending' and not a['segments'] and not a['reviews'],'B13 new acceptance overlaps old accepted content')
            a.update(copy.deepcopy(new[a['id']]));a['state']='accepted';a['reviews']=[{'type':t,'contentHash':pipe.content_hash(a,progress['sourceIssues']),'standardSnapshot':CURRENT_SNAPSHOT,'reference':reviewref} for t in pipe.REVIEW_TYPES]
        else:
            for r in a['reviews']:r['standardSnapshot']=CURRENT_SNAPSHOT;r['reference']+='; '+REFERENCE
        if s['chapter']<=65 or exact_baseline:require(z==a,'B13 body or review lineage changed: '+a['id'])
    for cp in expected['checkpoints'][:12]:cp['standardSnapshot']=CURRENT_SNAPSHOT;cp['reviewReference']+='; '+REFERENCE
    expected['checkpoints'][12].update(state='accepted',corpusHash=overlay['currentCorpusHash'],standardSnapshot=CURRENT_SNAPSHOT,reviewReference=reviewref)
    require(progress['checkpoints'][:13]==expected['checkpoints'][:13],'B13 checkpoint lineage changed')
    if exact_baseline:require(progress==expected,'B13 unexpected prospective progress delta')
    notes=read_json(pipe.DATA/'reader-notes.json');selected=batch['selectedReaderNotes']
    require([n['id'] for n in selected]==overlay['selectedReaderNoteIDs']==['B13-NOTE04','B13-NOTE05','B13-NOTE07'],'B13 selected note scope changed')
    selection=[x for x in read_json(root/E/'note-selection.json')['items'] if x['selected']]
    require(len(selection)==3 and all(n['id']==r['candidateID'] and n['text']==r['EnglishText'] and n['anchor']['unitId']==r['anchor']['sourceID'] and n['anchor']['segmentIndex']==r['anchor']['segmentIndex'] and n['anchor']['text']==r['anchor']['segmentText'] for n,r in zip(selected,selection)),'B13 genuine coordinator note selection changed')
    expected_notes=oldnotes['notes']+[{'unitId':n['anchor']['unitId'],'sourceHash':new[n['anchor']['unitId']]['sourceHash'],'glossaryId':'english-batch-061-065.json#/selectedReaderNotes/'+str(i),'type':'translator_note','text':n['text'],'presentationStatus':'not_integrated_in_reading_presentation'} for i,n in enumerate(selected)]
    require(notes['sourceHash']==mapping['sourceHash'] and notes['notes'][:72]==expected_notes and len(oldnotes['notes'])==69,'B13 prior or selected note changed')
    require(all(source_by_id.get(n['unitId'],{}).get('chapter',0)>65 for n in notes['notes'][72:]),'B13 extra note overlaps protected prefix')
    for n in selected:
        a=n['anchor'];u=new[a['unitId']];text=u['segments'][a['segmentIndex']]['text']
        require(a['start']==0 and a['end']==len(text) and a['text']==text and a['position']=='after_anchor' and u['sourceHash']==next(r['anchor']['sourceHash'] for r in selection if r['candidateID']==n['id']),'B13 full-segment note binding changed')
    if exact_baseline:require(notes==dict(oldnotes,notes=expected_notes),'B13 unexpected note delta')
    tr=transition(overlay,approved)
    for name in ('provenance.json','CHECKPOINT.json'):
        require(read_json(pipe.STANDARD/name)=={'schemaVersion':1,'status':tr['state'],'previousB12':read_json(h/S/name),'b13Transition':tr},'B13 metadata or original context changed')
    stats=pipe.validate_progress(mapping,progress,CURRENT_SNAPSHOT);pipe.validate_reader_notes(mapping,notes)
    return {'status':'B13_PREPARATION_PASS_INDEPENDENT_CURRENT_BINDING_REQUIRED' if not approved else 'B13_RECEIPT_BOUND_CURRENT_BINDING_PASS','states':stats,'normativeSnapshot':CURRENT_SNAPSHOT,'newUnits':284,'newNotes':3,'acceptedBodiesChanged':0,'installationAuthorized':False,'publicationEnabled':False}


def validate_readiness(pipe,mapping,progress):
    overlay=read_json(pipe.ROOT/OVERLAY_RELATIVE)
    for kind,digest,ref in [('semantic',SEMANTIC_RECEIPT_SHA256,REFERENCE),('technical',TECHNICAL_RECEIPT_SHA256,TECHNICAL_REFERENCE)]:
        require(isinstance(digest,str) and len(digest)==64,'B13 independent '+kind+' current-binding review pending')
        raw=regular(pipe.ROOT,D+'b13-'+kind+'-review.json');require(sha(raw)==digest,'B13 unpinned '+kind+' receipt');receipt=json.loads(raw)
        expected={'status':'PASS_SCOPED_CURRENT_BINDING','reviewKind':kind,'reference':ref,'requiredFindings':[],
            'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,
            'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,'currentCorpusHash':overlay['currentCorpusHash'],'orderedCorpusSHA256':overlay['orderedCorpusSHA256'],
            'newUnits':284,'newSegments':1118,'selectedReaderNotes':3,'preservedOldReaderNotes':69,'preservedSourceIssues':16,'preservedAcceptedBodies':3388,'acceptedBodiesChanged':0,
            'exactMergedNormApproved':True,'oldHistoricalContextsPreserved':True,'priorFullReviewAndFinalDeltaAuthenticated':True,'metadataKindChanges':14,'metadataReviewAuthenticated':True,'reviewedOrderedCorpusSHA256':overlay['reviewedOrderedCorpusSHA256'],'notFullCorpusReread':True,'publicationApproved':False}
        require(all(receipt.get(k)==v for k,v in expected.items()),'B13 incomplete '+kind+' current-binding receipt')
    validate_preparation(pipe,mapping,progress,exact_baseline=False,approved=True)
    return CURRENT_SNAPSHOT
