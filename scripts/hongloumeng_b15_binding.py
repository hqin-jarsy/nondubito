"""Bounded B15 continuation over the genuine receipt-bound B14 context.

This authenticates prior readings without relabeling them as fresh reviews.
Preparation is mechanical only. Current readiness needs separate real semantic
and technical receipts. Historical runtime regression uses a finite fixture.
"""
import copy,json
from pathlib import Path
from hongloumeng_source4655_binding import regular,sha,canonical,require,read_json
D='data/hongloumeng/first80-english/'
S='docs/hongloumeng/translation/'
E=D+'b15-evidence/'
HISTORY_RELATIVE=D+'history/v016-before'
HISTORY_SHA256='2ab0298ef22a6d760c1e4f7eec7d4af4dc7c1ae314fc24f35a854a5b8028a812'
OVERLAY_RELATIVE=S+'english-binding-071-075.json'
OVERLAY_SHA256='906f344b6874831692117896e0154a1d458469a9cc3aeffcd80c2f7db4015047'
PREVIOUS_SNAPSHOT='fef2273f310025de1756b63868da4709122bac81800d07c92576bea52500c3a2'
CURRENT_SNAPSHOT='28d8ab933e211e1abbece60aa89789af37149e17ff58a4e4d4dcb4ac49c030ec'
REFERENCE='EN-071-075-CURRENT-BINDING-INDEPENDENT-R1-20261112'
TECHNICAL_REFERENCE='EN-071-075-TECHNICAL-INDEPENDENT-R1-20261112'
SEMANTIC_RECEIPT_SHA256='a40959aab3e3f80e7e039336034bd31f877327883c9d9bc666437785ba9e9638'
TECHNICAL_RECEIPT_SHA256='07e2f1c0ba5a45c5aac93a7ecb9a2af3a7d5e38bb2d160e321914e926e206554'

HISTORICAL_NONRUNTIME_WITNESSES={'data/hongloumeng/first80-public/conversion.zh-hant 2.json': '409e6be081c1a58ea7c5ffa082b34316edd35a53cf10813e83d7977492542ec6', 'data/hongloumeng/first80-public/manifest 2.json': '57feaa65126cdada4056c1bb2165d7cec74f170373801b592fdee252c04046d6', 'data/hongloumeng/first80-public/manifest.zh-hant 2.json': '9de902737b438f4c5a7b45b19693855d8d25783e5af3abee4d6273e7432c575c', 'data/hongloumeng/first80-public/reading.zh 2.json': '564585568faa97b3b516443973c6c06a56493e5d91e81189b610c8606511dd4b', 'data/hongloumeng/first80-public/reading.zh-hant 2.json': '2edd282d9fbcc3000bf4adb2651f16e9d3a212606092a8d66430bf244e84a971', 'scripts/test_hongloumeng_first80.py': '34f950ea51caa527b545d24948cf31418de4369e143a8f5d25dc1a8aa17d94b6', 'classics/hongloumeng/ch038 2.html': '05b8923a015f50776fc05c20d846f6c467143955bc29df400637c0a0d0e36f66', 'classics/hongloumeng/ch042 2.html': '18bb1cf767fb48a21fdbca32de7e7cd1be981d3b52bd9d3709c91e0ce1ad41d1', 'classics/hongloumeng/ch045 2.html': '879be84bf1ca131f5fe17dedeb9987803eb886b7b6c551b2af1e4a0b23d7d031', 'classics/hongloumeng/index 2.html': 'd49197291dcdf1933745998e1cbc69d44c1a312057ebb807fb39654002a4bc7c', 'classics/hongloumeng/zh-hant/ch038 2.html': '844734bbcd92f7bed7f29c8c735625d9717635839b09986c615848e457ef2b84', 'classics/hongloumeng/zh-hant/ch042 2.html': '8e8ae791705e3ca4db60b51dc4fcbd3b642eef7c2f445f632396b43987e813ae', 'classics/hongloumeng/zh-hant/ch045 2.html': 'ea344bd4bc55473199b30922897857d14e46d635972260bcf857892090a5aac6', 'classics/hongloumeng/zh-hant/index 2.html': '13d8ce9c5bb01124959aef72c794c1ccc7b547d10dbfc52cc9cc07e7ac6fc548'}

def authenticate_history(root):
    h=root/HISTORY_RELATIVE
    raw=regular(h,'manifest.json');require(sha(raw)==HISTORY_SHA256,'B15 historical manifest changed')
    manifest=json.loads(raw)
    require(manifest['normativeSnapshot']==PREVIOUS_SNAPSHOT,'B15 prior normative snapshot changed')
    for p,digest in manifest['files'].items():require(sha(regular(h,p))==digest,'B15 archived predecessor changed: '+p)
    for p,digest in manifest['unchangedRootFiles'].items():require(sha(regular(root,p))==digest,'B15 unchanged predecessor changed: '+p)
    require(not set(manifest['files'])&set(manifest['unchangedRootFiles']),'B15 ambiguous predecessor paths')
    return h,manifest


def authenticate_historical_classification(root,overlay):
    """Only fourteen exact historical manifest entries lack current-file obligations.

    Original validators/manifests are immutable evidence. This is not execution
    of those validators, and never invents missing historical witness bytes.
    """
    evidence=read_json(root/E/'historical-witness-classification.json')
    expected=HISTORICAL_NONRUNTIME_WITNESSES
    require(evidence['entries']==expected and evidence['historicalExactRuntimeReplayClaimed'] is False and evidence['currentReplayUsesTrackedFilesOnly'] is True,'B15 historical witness classification differs')
    require(evidence['historicalManifestPath']==D+'history/v015-before/manifest.json','B15 historical witness manifest target differs')
    raw=regular(root,evidence['historicalManifestPath'])
    require(sha(raw)==evidence['historicalManifestSHA256']=='351980e5bdf6fc814f99688d18e4e9998a5841ef55cfc3c5f7b409cab891002e','B15 historical witness manifest changed')
    old=json.loads(raw)
    require(all(old['unchangedRootFiles'].get(p)==digest for p,digest in expected.items()),'B15 original witness entries changed')
    h,manifest=authenticate_history(root)
    require(not set(expected)&(set(manifest['files'])|set(manifest['unchangedRootFiles'])),'B15 historical witnesses became current runtime dependencies')
    return {'historicalEvidence':'authenticated','exactHistoricalRuntimeReplay':False,'classifiedEntries':14}


def transition(overlay,approved=False):
    return {'state':'independently_reviewed_B15_current_binding' if approved else 'pending_independent_B15_current_binding_review',
        'version':'english-1-110-v0.16','previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,
        'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,'sourceHash':overlay['sourceHash'],
        'sourceMapSHA256':overlay['sourceMapSHA256'],'currentCorpusHash':overlay['currentCorpusHash'],
        'newUnits':237,'newSegments':845,'newNotes':2,'acceptedBodiesChanged':0,'notFullCorpusReread':True,'publicationEnabled':False}


def corpus(units):
    return [{'id':u['id'],'sourceHash':u['sourceHash'],'segments':u['segments']} for u in units]


def authenticate_readings(root,drafts,overlay):
    for p,digest in overlay['evidence'].items():require(sha(regular(root,p))==digest,'B15 reading evidence changed: '+p)
    evidence=read_json(root/E/'reading-lineage.json');rows=evidence['units']
    require(len(rows)==len(drafts)==237 and evidence['words']==35117,'B15 genuine reading scope changed')
    require(sha(canonical(drafts))==overlay['orderedCorpusSHA256'],'B15 final reviewed corpus changed')
    require(evidence['cumulativeManifestSHA256']=='94d34b75e0f8265e095ff8bb9ddb082262a82b632765b259690b19038728d306' and evidence['originalReadingReceiptSHA256']=='537282fe273ad4a79037dbe6a341d2305ef84dfd3fcc830b1ec2176701cef074','B15 original cumulative reading identity changed')
    review=evidence['review'];require(review['verdict']=='PASS_CUMULATIVE_BILINGUAL_LITERARY_CONSISTENCY' and review['requiredFindings']==review['optionalTextFindings']==[],'B15 cumulative approval differs')
    for unit,row in zip(drafts,rows):
        require(unit['id']==row['id'] and unit['sourceHash']==row['sourceHash'] and sha(canonical(unit['segments']))==row['EnglishSegmentsSHA256'] and row['fullEnglishRead'] is True and row['fullChineseContextRead'] is True,'B15 reviewed unit differs')
    public=evidence['publicReview'];require(public['verdict']=='PASS_SCOPED_PUBLIC_PROJECTION' and public['requiredChanges']==[] and public['optionalChanges']==[] and public['subjectManifestSHA256']==overlay['publicProjectionManifestSHA256'] and public['publicSemanticSubjectSHA256']==overlay['publicSemanticSubjectSHA256'],'B15 independent public approval differs')
    err=read_json(root/E/'historical-report-erratum.json');batch=read_json(root/S/'english-batch-071-075.json')
    require(err['id']=='PUBLIC-R1-001' and err['sourcePointer']=='/1/result' and err['targetPointer']=='/interpretiveLimits/1/result' and err['before'].startswith('Maternal cousin') and err['after'].startswith('Paternal-aunt cousin') and batch['interpretiveLimits'][1]['result']==err['after'] and err['noProseOrSourceChange'] is True,'B15 effective paternal-aunt erratum changed')
    authenticate_historical_classification(root,overlay)


def validate_preparation(pipe,mapping,progress,*,exact_baseline=True,approved=False):
    root=pipe.ROOT;h,manifest=authenticate_history(root)
    raw=regular(root,OVERLAY_RELATIVE);require(sha(raw)==OVERLAY_SHA256,'B15 binding overlay changed');overlay=json.loads(raw)
    require(overlay['state']=='prospective_B15_current_binding_pending_independent_review' and overlay['publicationEnabled'] is False,'B15 fabricated projection approval')
    require(pipe.VERSION=='english-1-110-v0.16' and tuple(pipe.NORMATIVE_FILES)==tuple(manifest['normativeFiles'])+('english-batch-071-075.json','english-binding-071-075.json'),'B15 normative scope differs')
    require(pipe.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT==CURRENT_SNAPSHOT,'B15 merged normative snapshot changed')
    prior_hashes={n:(manifest['files'] if S+n in manifest['files'] else manifest['unchangedRootFiles'])[S+n] for n in manifest['normativeFiles']}
    require(sha(canonical(prior_hashes))==PREVIOUS_SNAPSHOT,'B15 predecessor normative identity differs')
    for p,digest in overlay['publicFiles'].items():require(sha(regular(root,p))==digest,'B15 exact public guidance changed: '+p)
    before=read_json(h/D/'progress.json');oldnotes=read_json(h/D/'reader-notes.json')
    require(mapping==pipe.source_map(pipe.load_source())==read_json(pipe.DATA/'source-map.json'),'B15 current source map differs')
    require(mapping['sourceHash']==overlay['sourceHash']==pipe.READING_SHA and sha(regular(root,D+'source-map.json'))==overlay['sourceMapSHA256']==pipe.SOURCE_MAP_SHA,'B15 current source binding differs')
    require(progress['sourceHash']==before['sourceHash']==mapping['sourceHash'] and progress['standardVersion']==pipe.VERSION,'B15 current progress metadata differs')
    batch=read_json(pipe.STANDARD/'english-batch-071-075.json');sources=[s for s in mapping['units'] if 71<=s['chapter']<=75]
    require(sources==overlay['currentSourceUnits'] and len(sources)==237,'B15 current source-unit scope differs')
    drafts=[]
    for row in overlay['draftFiles']:
        raw=regular(root,row['path']);require(sha(raw)==row['sha256'] and len(raw)==row['bytes'],'B15 exact draft changed');drafts.extend(json.loads(raw))
    require(len(drafts)==237 and sum(len(u['segments']) for u in drafts)==845 and pipe.batch_hash(drafts,progress['sourceIssues'])==overlay['currentCorpusHash'],'B15 draft corpus differs')
    for u,s in zip(drafts,sources):
        require(u['id']==s['id'] and u['sourceHash']==s['sourceHash'],'B15 projected source or English body differs')
        require(all(seg['kind']==s['layout']['kind'] for seg in u['segments']) and (s['layout']['kind'] in ('prose','letter') or len(u['segments'])==1),'B15 source layout differs')
        require(u['state']=='draft' and u['reviews']==[],'B15 original drafts were relabeled as fresh accepted reviews')
    authenticate_readings(root,drafts,overlay)
    require(regular(root,S+'english-standard.md').startswith(regular(h,S+'english-standard.md')),'B15 earlier standard text changed')
    terms=read_json(h/S/'english-terms.json');terms['version']=pipe.VERSION;terms['batch_glossaries'].append('english-batch-071-075.json')
    require(read_json(pipe.STANDARD/'english-terms.json')==terms,'B15 earlier terms changed')
    voices=read_json(h/S/'english-voices.json');voices['version']=pipe.VERSION;voices['batch_071_075_details']=batch['voices']
    require(read_json(pipe.STANDARD/'english-voices.json')==voices,'B15 earlier voices changed')
    source_by_id={s['id']:s for s in mapping['units']};new={u['id']:u for u in drafts}
    require(len(progress['units'])==len(before['units'])==len(mapping['units'])==4475,'B15 unit count changed')
    require(progress['sourceIssues'][:len(before['sourceIssues'])]==before['sourceIssues'] and all(source_by_id.get(i['unitId'],{}).get('chapter',0)>75 for i in progress['sourceIssues'][len(before['sourceIssues']):]),'B15 prior source issue changed')
    reviewref='EN-B071-075-CUMULATIVE-INDEPENDENT-R1-20261112; '+REFERENCE
    expected=copy.deepcopy(before);expected['standardVersion']=pipe.VERSION
    for a,z,s in zip(expected['units'],progress['units'],mapping['units']):
        if a['id'] in new:
            require(a['state']=='pending' and not a['segments'] and not a['reviews'],'B15 new acceptance overlaps old accepted content')
            a.update(copy.deepcopy(new[a['id']]));a['state']='accepted';a['reviews']=[{'type':t,'contentHash':pipe.content_hash(a,progress['sourceIssues']),'standardSnapshot':CURRENT_SNAPSHOT,'reference':reviewref} for t in pipe.REVIEW_TYPES]
        else:
            for r in a['reviews']:r['standardSnapshot']=CURRENT_SNAPSHOT;r['reference']+='; '+REFERENCE
        if s['chapter']<=75 or exact_baseline:require(z==a,'B15 body or review lineage changed: '+a['id'])
    for cp in expected['checkpoints'][:14]:cp['standardSnapshot']=CURRENT_SNAPSHOT;cp['reviewReference']+='; '+REFERENCE
    expected['checkpoints'][14].update(state='accepted',corpusHash=overlay['currentCorpusHash'],standardSnapshot=CURRENT_SNAPSHOT,reviewReference=reviewref)
    require(progress['checkpoints'][:15]==expected['checkpoints'][:15],'B15 checkpoint lineage changed')
    if exact_baseline:require(progress==expected,'B15 unexpected prospective progress delta')
    notes=read_json(pipe.DATA/'reader-notes.json');selected=batch['selectedReaderNotes']
    require([n['id'] for n in selected]==overlay['selectedReaderNoteIDs']==['B15-NOTE-01','B15-NOTE-08'] and sha(canonical(selected))==overlay['selectedReaderNotesSHA256'],'B15 selected note scope changed')
    expected_notes=oldnotes['notes']+[{'unitId':n['anchor']['unitId'],'sourceHash':new[n['anchor']['unitId']]['sourceHash'],'glossaryId':'english-batch-071-075.json#/selectedReaderNotes/'+str(i),'type':'translator_note','text':n['text'],'presentationStatus':'not_integrated_in_reading_presentation'} for i,n in enumerate(selected)]
    require(notes['sourceHash']==mapping['sourceHash'] and notes['notes'][:78]==expected_notes and len(oldnotes['notes'])==76,'B15 prior or selected note changed')
    require(all(source_by_id.get(n['unitId'],{}).get('chapter',0)>75 for n in notes['notes'][78:]),'B15 extra note overlaps protected prefix')
    for n in selected:
        a=n['anchor'];u=new[a['unitId']];text=u['segments'][a['segmentIndex']]['text']
        require(0<=a['start']<a['end']<=len(text) and a['text']==text[a['start']:a['end']] and a['position']=='after_anchor','B15 full-segment note binding changed')
    if exact_baseline:require(notes==dict(oldnotes,notes=expected_notes),'B15 unexpected note delta')
    tr=transition(overlay,approved)
    for name in ('provenance.json','CHECKPOINT.json'):
        require(read_json(pipe.STANDARD/name)=={'schemaVersion':1,'status':tr['state'],'previousB14':read_json(h/S/name),'b15Transition':tr},'B15 metadata or original context changed')
    stats=pipe.validate_progress(mapping,progress,CURRENT_SNAPSHOT);pipe.validate_reader_notes(mapping,notes)
    return {'status':'B15_PREPARATION_PASS_INDEPENDENT_CURRENT_BINDING_REQUIRED' if not approved else 'B15_RECEIPT_BOUND_CURRENT_BINDING_PASS','states':stats,'normativeSnapshot':CURRENT_SNAPSHOT,'newUnits':237,'newNotes':2,'acceptedBodiesChanged':0,'installationAuthorized':False,'publicationEnabled':False}


def validate_readiness(pipe,mapping,progress):
    overlay=read_json(pipe.ROOT/OVERLAY_RELATIVE)
    for kind,digest,ref in [('semantic',SEMANTIC_RECEIPT_SHA256,REFERENCE),('technical',TECHNICAL_RECEIPT_SHA256,TECHNICAL_REFERENCE)]:
        require(isinstance(digest,str) and len(digest)==64,'B15 independent '+kind+' current-binding review pending')
        raw=regular(pipe.ROOT,D+'b15-'+kind+'-review.json');require(sha(raw)==digest,'B15 unpinned '+kind+' receipt');receipt=json.loads(raw)
        expected={'status':'PASS_SCOPED_CURRENT_BINDING','reviewKind':kind,'reference':ref,'requiredFindings':[],
            'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,
            'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,'currentCorpusHash':overlay['currentCorpusHash'],'orderedCorpusSHA256':overlay['orderedCorpusSHA256'],
            'newUnits':237,'newSegments':845,'selectedReaderNotes':2,'preservedOldReaderNotes':76,'preservedSourceIssues':16,'preservedAcceptedBodies':3896,'acceptedBodiesChanged':0,
            'exactMergedNormApproved':True,'oldHistoricalContextsPreserved':True,'originalCumulativeReadingAuthenticated':True,'historicalWitnessClassificationAudited':True,'currentTrackedReplayAudited':True,'historicalExactRuntimeReplayClaimed':False,'notFullCorpusReread':True,'publicationApproved':False}
        require(all(receipt.get(k)==v for k,v in expected.items()),'B15 incomplete '+kind+' current-binding receipt')
    validate_preparation(pipe,mapping,progress,exact_baseline=False,approved=True)
    return CURRENT_SNAPSHOT
