"""Bounded B16 continuation over the genuine receipt-bound B14 context.

This authenticates prior readings without relabeling them as fresh reviews.
Preparation is mechanical only. Current readiness needs separate real semantic
and technical receipts. Historical runtime regression uses a finite fixture.
"""
import copy,json
from pathlib import Path
from hongloumeng_source4655_binding import sha,canonical,require,read_json
from hongloumeng_reading_presentation_binding import read_historical as regular
D='data/hongloumeng/first80-english/'
S='docs/hongloumeng/translation/'
E=D+'b16-evidence/'
HISTORY_RELATIVE=D+'history/v017-before'
HISTORY_SHA256='fb7958eacd04e40ee450b9c18bdb69ed0734f69720d025c08af6eb177341614d'
OVERLAY_RELATIVE=S+'english-binding-076-080.json'
OVERLAY_SHA256='fda936f7f4d7ebf5682e6a6c9a02926b56a6a9eade6c0a5c316c62060df57e9b'
PREVIOUS_SNAPSHOT='28d8ab933e211e1abbece60aa89789af37149e17ff58a4e4d4dcb4ac49c030ec'
CURRENT_SNAPSHOT='5693eba1a2b0fe7318ef59f0343de967e287086a916303a1facca4ff05a5a8d7'
REFERENCE='EN-076-080-CURRENT-BINDING-INDEPENDENT-R1-20261112'
TECHNICAL_REFERENCE='EN-076-080-TECHNICAL-INDEPENDENT-R1-20261112'
SEMANTIC_RECEIPT_SHA256='14892bab652dc25d42cffcaae27c6cfdca1a69b1a0269ee69641d9102ec1dabb'
TECHNICAL_RECEIPT_SHA256='629417474ab7492f1a19edc47e45bef1329135973dc8656ebe3980d819e0ce07'

HISTORICAL_NONRUNTIME_WITNESSES={'data/hongloumeng/first80-public/conversion.zh-hant 2.json': '409e6be081c1a58ea7c5ffa082b34316edd35a53cf10813e83d7977492542ec6', 'data/hongloumeng/first80-public/manifest 2.json': '57feaa65126cdada4056c1bb2165d7cec74f170373801b592fdee252c04046d6', 'data/hongloumeng/first80-public/manifest.zh-hant 2.json': '9de902737b438f4c5a7b45b19693855d8d25783e5af3abee4d6273e7432c575c', 'data/hongloumeng/first80-public/reading.zh 2.json': '564585568faa97b3b516443973c6c06a56493e5d91e81189b610c8606511dd4b', 'data/hongloumeng/first80-public/reading.zh-hant 2.json': '2edd282d9fbcc3000bf4adb2651f16e9d3a212606092a8d66430bf244e84a971', 'scripts/test_hongloumeng_first80.py': '34f950ea51caa527b545d24948cf31418de4369e143a8f5d25dc1a8aa17d94b6', 'classics/hongloumeng/ch038 2.html': '05b8923a015f50776fc05c20d846f6c467143955bc29df400637c0a0d0e36f66', 'classics/hongloumeng/ch042 2.html': '18bb1cf767fb48a21fdbca32de7e7cd1be981d3b52bd9d3709c91e0ce1ad41d1', 'classics/hongloumeng/ch045 2.html': '879be84bf1ca131f5fe17dedeb9987803eb886b7b6c551b2af1e4a0b23d7d031', 'classics/hongloumeng/index 2.html': 'd49197291dcdf1933745998e1cbc69d44c1a312057ebb807fb39654002a4bc7c', 'classics/hongloumeng/zh-hant/ch038 2.html': '844734bbcd92f7bed7f29c8c735625d9717635839b09986c615848e457ef2b84', 'classics/hongloumeng/zh-hant/ch042 2.html': '8e8ae791705e3ca4db60b51dc4fcbd3b642eef7c2f445f632396b43987e813ae', 'classics/hongloumeng/zh-hant/ch045 2.html': 'ea344bd4bc55473199b30922897857d14e46d635972260bcf857892090a5aac6', 'classics/hongloumeng/zh-hant/index 2.html': '13d8ce9c5bb01124959aef72c794c1ccc7b547d10dbfc52cc9cc07e7ac6fc548'}

def authenticate_history(root):
    h=root/HISTORY_RELATIVE
    raw=regular(h,'manifest.json');require(sha(raw)==HISTORY_SHA256,'B16 historical manifest changed')
    manifest=json.loads(raw)
    require(manifest['normativeSnapshot']==PREVIOUS_SNAPSHOT,'B16 prior normative snapshot changed')
    for p,digest in manifest['files'].items():require(sha(regular(h,p))==digest,'B16 archived predecessor changed: '+p)
    for p,digest in manifest['unchangedRootFiles'].items():require(sha(regular(root,p))==digest,'B16 unchanged predecessor changed: '+p)
    require(not set(manifest['files'])&set(manifest['unchangedRootFiles']),'B16 ambiguous predecessor paths')
    return h,manifest


def authenticate_historical_classification(root,overlay):
    """Only fourteen exact historical manifest entries lack current-file obligations.

    Original validators/manifests are immutable evidence. This is not execution
    of those validators, and never invents missing historical witness bytes.
    """
    evidence=read_json(root/E/'historical-witness-classification.json')
    expected=HISTORICAL_NONRUNTIME_WITNESSES
    require(evidence['entries']==expected and evidence['historicalExactRuntimeReplayClaimed'] is False and evidence['currentReplayUsesTrackedFilesOnly'] is True,'B16 historical witness classification differs')
    require(evidence['historicalManifestPath']==D+'history/v015-before/manifest.json','B16 historical witness manifest target differs')
    raw=regular(root,evidence['historicalManifestPath'])
    require(sha(raw)==evidence['historicalManifestSHA256']=='351980e5bdf6fc814f99688d18e4e9998a5841ef55cfc3c5f7b409cab891002e','B16 historical witness manifest changed')
    old=json.loads(raw)
    require(all(old['unchangedRootFiles'].get(p)==digest for p,digest in expected.items()),'B16 original witness entries changed')
    h,manifest=authenticate_history(root)
    require(not set(expected)&(set(manifest['files'])|set(manifest['unchangedRootFiles'])),'B16 historical witnesses became current runtime dependencies')
    return {'historicalEvidence':'authenticated','exactHistoricalRuntimeReplay':False,'classifiedEntries':14}


def transition(overlay,approved=False):
    return {'state':'independently_reviewed_B16_current_binding' if approved else 'pending_independent_B16_current_binding_review',
        'version':'english-1-110-v0.17','previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,
        'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,'sourceHash':overlay['sourceHash'],
        'sourceMapSHA256':overlay['sourceMapSHA256'],'currentCorpusHash':overlay['currentCorpusHash'],
        'newUnits':342,'newSegments':975,'newNotes':2,'acceptedBodiesChanged':0,'notFullCorpusReread':True,'publicationEnabled':False}


def corpus(units):
    return [{'id':u['id'],'sourceHash':u['sourceHash'],'segments':u['segments']} for u in units]


def authenticate_readings(root,drafts,overlay):
    for p,digest in overlay['evidence'].items():require(sha(regular(root,p))==digest,'B16 reading evidence changed: '+p)
    evidence=read_json(root/E/'reading-lineage.json');rows=evidence['units']
    require(len(rows)==len(drafts)==342 and evidence['words']==33449,'B16 genuine reading scope changed')
    require(sha(canonical(drafts))==overlay['orderedCorpusSHA256']=='ebdc5767f87866c07f0dc2acf63df0a827fbd02d1192e7343492580c9868b836','B16 final reviewed corpus changed')
    require(evidence['cumulativeManifestSHA256']=='cdf39fef3ca4385f95a4a3282eb24e258cb713f0fd163fcec603a882cdc5de6f' and evidence['originalReadingReceiptSHA256']=='e75d9f2edbba136c17f36823a96e6c75c748adf044e95708bcf6b4b6975eafd5','B16 original cumulative reading identity changed')
    require(evidence['review']['verdict']=='PASS' and evidence['review']['remainingChapterProseFindings']==0 and evidence['review']['newFullReadClaim'] is False,'B16 cumulative closure differs')
    for unit,row in zip(drafts,rows):
        require(unit['id']==row['id'] and unit['sourceHash']==row['sourceHash'] and sha(canonical(unit['segments']))==row['EnglishSegmentsSHA256'] and row['fullEnglishUnitRead'] is True and row['fullChineseUnitRead'] is True and row['verdict']=='PASS' and bool(row['assessment']),'B16 reviewed unit differs')
    public=evidence['publicReview']
    require(public==overlay['approvedPublicReview'],'B16 independent public approval differs')
    require(evidence['publicReviewManifestSHA256']==overlay['publicReviewManifestSHA256'],'B16 public review identity differs')
    require(evidence['noFreshFullReadClaim'] is True,'B16 falsely relabeled cumulative reading')
    err=read_json(root/E/'effective-guidance-errata.json');batch=read_json(root/S/'english-batch-076-080.json')
    require(err['publicProjectionManifestSHA256']==overlay['publicProjectionManifestSHA256'],'B16 erratum subject differs')
    for row in err['changes']:
        value=batch
        try:
            for key in row['pointer'].strip('/').split('/'):
                value=value[int(key)] if isinstance(value,list) else value[key]
        except (KeyError,IndexError):
            value=None
        require(value==row['after'],'B16 effective guidance erratum differs: '+row['pointer'])
    require(err['standard']['after'] in regular(root,S+'english-standard.md').decode(),'B16 effective standard erratum differs')
    authenticate_historical_classification(root,overlay)


def validate_preparation(pipe,mapping,progress,*,exact_baseline=True,approved=False):
    root=pipe.ROOT;h,manifest=authenticate_history(root)
    raw=regular(root,OVERLAY_RELATIVE);require(sha(raw)==OVERLAY_SHA256,'B16 binding overlay changed');overlay=json.loads(raw)
    require(overlay['state']=='prospective_B16_current_binding_pending_independent_review' and overlay['publicationEnabled'] is False,'B16 fabricated projection approval')
    require(pipe.VERSION=='english-1-110-v0.17' and tuple(pipe.NORMATIVE_FILES)==tuple(manifest['normativeFiles'])+('english-batch-076-080.json','english-binding-076-080.json'),'B16 normative scope differs')
    require(pipe.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT==CURRENT_SNAPSHOT,'B16 merged normative snapshot changed')
    prior_hashes={n:(manifest['files'] if S+n in manifest['files'] else manifest['unchangedRootFiles'])[S+n] for n in manifest['normativeFiles']}
    require(sha(canonical(prior_hashes))==PREVIOUS_SNAPSHOT,'B16 predecessor normative identity differs')
    for p,digest in overlay['publicFiles'].items():require(sha(regular(root,p))==digest,'B16 exact public guidance changed: '+p)
    before=read_json(h/D/'progress.json');oldnotes=read_json(h/D/'reader-notes.json')
    require(mapping==pipe.source_map(pipe.load_source())==read_json(pipe.DATA/'source-map.json'),'B16 current source map differs')
    require(mapping['sourceHash']==overlay['sourceHash']==pipe.READING_SHA and sha(regular(root,D+'source-map.json'))==overlay['sourceMapSHA256']==pipe.SOURCE_MAP_SHA,'B16 current source binding differs')
    require(progress['sourceHash']==before['sourceHash']==mapping['sourceHash'] and progress['standardVersion']==pipe.VERSION,'B16 current progress metadata differs')
    batch=read_json(pipe.STANDARD/'english-batch-076-080.json');sources=[s for s in mapping['units'] if 76<=s['chapter']<=80]
    require(sources==overlay['currentSourceUnits'] and len(sources)==342,'B16 current source-unit scope differs')
    drafts=[]
    for row in overlay['draftFiles']:
        raw=regular(root,row['path']);require(sha(raw)==row['sha256'] and len(raw)==row['bytes'],'B16 exact draft changed');drafts.extend(json.loads(raw))
    require(len(drafts)==342 and sum(len(u['segments']) for u in drafts)==975 and pipe.batch_hash(drafts,progress['sourceIssues'])==overlay['currentCorpusHash'],'B16 draft corpus differs')
    for u,s in zip(drafts,sources):
        require(u['id']==s['id'] and u['sourceHash']==s['sourceHash'],'B16 projected source or English body differs')
        require(all(seg['kind']==s['layout']['kind'] for seg in u['segments']) and (s['layout']['kind'] in ('prose','letter') or len(u['segments'])==1),'B16 source layout differs')
        require(u['state']=='draft' and u['reviews']==[],'B16 original drafts were relabeled as fresh accepted reviews')
    authenticate_readings(root,drafts,overlay)
    require(regular(root,S+'english-standard.md').startswith(regular(h,S+'english-standard.md')),'B16 earlier standard text changed')
    terms=read_json(h/S/'english-terms.json');terms['version']=pipe.VERSION;terms['batch_glossaries'].append('english-batch-076-080.json')
    require(read_json(pipe.STANDARD/'english-terms.json')==terms,'B16 earlier terms changed')
    voices=read_json(h/S/'english-voices.json');voices['version']=pipe.VERSION;voices['batch_076_080_details']=batch['voices']
    require(read_json(pipe.STANDARD/'english-voices.json')==voices,'B16 earlier voices changed')
    source_by_id={s['id']:s for s in mapping['units']};new={u['id']:u for u in drafts}
    require(len(progress['units'])==len(before['units'])==len(mapping['units'])==4475,'B16 unit count changed')
    require(progress['sourceIssues'][:len(before['sourceIssues'])]==before['sourceIssues'] and all(source_by_id.get(i['unitId'],{}).get('chapter',0)>80 for i in progress['sourceIssues'][len(before['sourceIssues']):]),'B16 prior source issue changed')
    reviewref='EN-B076-080-CUMULATIVE-INDEPENDENT-R1-WITH-R2-R3-CLOSURES-20261112; '+REFERENCE
    expected=copy.deepcopy(before);expected['standardVersion']=pipe.VERSION
    for a,z,s in zip(expected['units'],progress['units'],mapping['units']):
        if a['id'] in new:
            require(a['state']=='pending' and not a['segments'] and not a['reviews'],'B16 new acceptance overlaps old accepted content')
            a.update(copy.deepcopy(new[a['id']]));a['state']='accepted';a['reviews']=[{'type':t,'contentHash':pipe.content_hash(a,progress['sourceIssues']),'standardSnapshot':CURRENT_SNAPSHOT,'reference':reviewref} for t in pipe.REVIEW_TYPES]
        else:
            for r in a['reviews']:r['standardSnapshot']=CURRENT_SNAPSHOT;r['reference']+='; '+REFERENCE
        if s['chapter']<=80 or exact_baseline:require(z==a,'B16 body or review lineage changed: '+a['id'])
    for cp in expected['checkpoints'][:15]:cp['standardSnapshot']=CURRENT_SNAPSHOT;cp['reviewReference']+='; '+REFERENCE
    expected['checkpoints'][15].update(state='accepted',corpusHash=overlay['currentCorpusHash'],standardSnapshot=CURRENT_SNAPSHOT,reviewReference=reviewref)
    require(progress['checkpoints'][:16]==expected['checkpoints'][:16],'B16 checkpoint lineage changed')
    if exact_baseline:require(progress==expected,'B16 unexpected prospective progress delta')
    notes=read_json(pipe.DATA/'reader-notes.json');selected=batch['selectedReaderNotes']
    require([n['id'] for n in selected]==overlay['selectedReaderNoteIDs']==['B16-N06','B16-N07'] and sha(canonical(selected))==overlay['selectedReaderNotesSHA256'],'B16 selected note scope changed')
    expected_notes=oldnotes['notes']+[{'unitId':n['anchor']['unitId'],'sourceHash':new[n['anchor']['unitId']]['sourceHash'],'glossaryId':'english-batch-076-080.json#/selectedReaderNotes/'+str(i),'type':'translator_note','text':n['text'],'presentationStatus':'not_integrated_in_reading_presentation'} for i,n in enumerate(selected)]
    require(notes['sourceHash']==mapping['sourceHash'] and notes['notes'][:80]==expected_notes and len(oldnotes['notes'])==78,'B16 prior or selected note changed')
    require(all(source_by_id.get(n['unitId'],{}).get('chapter',0)>80 for n in notes['notes'][80:]),'B16 extra note overlaps protected prefix')
    for n in selected:
        a=n['anchor'];u=new[a['unitId']];text=u['segments'][a['segmentIndex']]['text']
        require(0<=a['start']<a['end']<=len(text) and a['text']==text[a['start']:a['end']] and a['position']=='after_anchor','B16 full-segment note binding changed')
    if exact_baseline:require(notes==dict(oldnotes,notes=expected_notes),'B16 unexpected note delta')
    tr=transition(overlay,approved)
    for name in ('provenance.json','CHECKPOINT.json'):
        require(read_json(pipe.STANDARD/name)=={'schemaVersion':1,'status':tr['state'],'previousB15':read_json(h/S/name),'b16Transition':tr},'B16 metadata or original context changed')
    stats=pipe.validate_progress(mapping,progress,CURRENT_SNAPSHOT);pipe.validate_reader_notes(mapping,notes)
    return {'status':'B16_PREPARATION_PASS_INDEPENDENT_CURRENT_BINDING_REQUIRED' if not approved else 'B16_RECEIPT_BOUND_CURRENT_BINDING_PASS','states':stats,'normativeSnapshot':CURRENT_SNAPSHOT,'newUnits':342,'newNotes':2,'acceptedBodiesChanged':0,'installationAuthorized':False,'publicationEnabled':False}


def validate_b16_readiness(pipe,mapping,progress):
    overlay=read_json(pipe.ROOT/OVERLAY_RELATIVE)
    for kind,digest,ref in [('semantic',SEMANTIC_RECEIPT_SHA256,REFERENCE),('technical',TECHNICAL_RECEIPT_SHA256,TECHNICAL_REFERENCE)]:
        require(isinstance(digest,str) and len(digest)==64,'B16 independent '+kind+' current-binding review pending')
        raw=regular(pipe.ROOT,D+'b16-'+kind+'-review.json');require(sha(raw)==digest,'B16 unpinned '+kind+' receipt');receipt=json.loads(raw)
        expected={'status':'PASS_SCOPED_CURRENT_BINDING','reviewKind':kind,'reference':ref,'requiredFindings':[],
            'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,
            'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,'currentCorpusHash':overlay['currentCorpusHash'],'orderedCorpusSHA256':overlay['orderedCorpusSHA256'],
            'newUnits':342,'newSegments':975,'selectedReaderNotes':2,'preservedOldReaderNotes':78,'preservedSourceIssues':16,'preservedAcceptedBodies':4133,'acceptedBodiesChanged':0,
            'exactMergedNormApproved':True,'oldHistoricalContextsPreserved':True,'originalCumulativeReadingAuthenticated':True,'historicalWitnessClassificationAudited':True,'currentTrackedReplayAudited':True,'historicalExactRuntimeReplayClaimed':False,'notFullCorpusReread':True,'publicationApproved':False}
        require(all(receipt.get(k)==v for k,v in expected.items()),'B16 incomplete '+kind+' current-binding receipt')
    validate_preparation(pipe,mapping,progress,exact_baseline=False,approved=True)
    return CURRENT_SNAPSHOT


def validate_readiness(pipe,mapping,progress):
    """Original B16 acceptance plus separately audited current presentation."""
    from hongloumeng_reading_presentation_binding import validate_state, require_review
    snapshot=validate_b16_readiness(pipe,mapping,progress)
    validate_state(pipe.ROOT)
    require_review(pipe.ROOT)
    return snapshot
