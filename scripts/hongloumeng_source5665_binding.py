"""Exact pending-source transition after accepted1-55 B11.

The predecessor inventory remains authenticated in its original context. Only
changed context files are archived, never another copy of the history tree.
Historical validators run against that exact finite context in regression tests.
Current readiness needs genuine separate semantic/current-binding and technical
receipts. This module does not create either receipt or grant English publication.
"""
import copy,json
from pathlib import Path
from hongloumeng_source4655_binding import regular,sha,canonical,require,read_json
D='data/hongloumeng/first80-english/'
S='docs/hongloumeng/translation/'
P='data/hongloumeng/first80-public/'
HISTORY_RELATIVE=D+'history/source-ch56-ch65-before'
HISTORY_SHA256='dd258a2a5789e4604b917be1853e25e78412bacf035ae9a7b8b7766a6e71fa5c'
OVERLAY_RELATIVE=S+'source-binding-ch56-ch65.json'
OVERLAY_SHA256='4d3182c614cf2040bc2c4aee5315bdaf57dc3759df02213fcbb145d250feed97'
PREVIOUS_SNAPSHOT='9e49d30c44c8dadcb22da5da3abb8e1762b66fdbb871e74797aaafcdf496fab1'
CURRENT_SNAPSHOT='cbcf8cd3d72957563db33c12c22ad04a8a8aaffd2345020ebc06a1af21370d5f'
SEMANTIC_RECEIPT_SHA256='ea269b96616ec700f4b21d6151151db62638c6244ab8573bde784b5172c48e62'
TECHNICAL_RECEIPT_SHA256='814316a4eaa7970c718ec69a99a1167b893fda61e0a75396803b8c94cf6c0807'
POLICY_PATH='data/hongloumeng/first80/author-ch56-ch65-source-policy.json'
POLICY_SHA256='42aae15b2f10a8e15fe53e1d12447c03d101c3643bbbbf99cf346af65cf117b0'


def authenticate_history(root):
    history=root/HISTORY_RELATIVE
    raw=regular(history,'manifest.json');require(sha(raw)==HISTORY_SHA256,'Source5665 historical manifest changed')
    manifest=json.loads(raw)
    require(manifest['normativeSnapshot']==PREVIOUS_SNAPSHOT,'Source5665 predecessor norm changed')
    for name,digest in manifest['files'].items():
        require(sha(regular(history,name))==digest,'Source5665 archived predecessor changed: '+name)
    for name,digest in manifest['unchangedRootFiles'].items():
        require(sha(regular(root,name))==digest,'Source5665 unchanged predecessor changed: '+name)
    return history,manifest


def materialize_predecessor(root,destination):
    """Regression-only finite B11 fixture, not used by normal runtime validation."""
    history,manifest=authenticate_history(root)
    destination=Path(destination).resolve();require(not destination.exists(),'Source5665 predecessor output exists')
    destination.mkdir()
    for name in sorted(set(manifest['files'])|set(manifest['unchangedRootFiles'])):
        base=history if name in manifest['files'] else root
        payload=regular(base,name)
        target=destination/name;require(destination in target.parents,'Source5665 predecessor output escapes root')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
    return destination


def transition(reference=None,technical_reference=None):
    require((reference is None)==(technical_reference is None),'Source5665 incomplete real approval references')
    return {'state':'pending_independent_source_binding_review' if reference is None else 'independently_reviewed_source_binding',
            'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,
            'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,
            'semanticCurrentBindingReviewReference':reference,'technicalReviewReference':technical_reference,
            'changedPendingUnits':13,'approvedSourceSpans':16,'acceptedBodiesChanged':0,
            'oldReviewObjectsRetainedInAuthenticContext':True,'notFullCorpusReread':True,
            'publicationEnabled':False}


def validate_preparation(pipe,mapping,progress,*,exact_baseline=True,reference=None,technical_reference=None):
    root=pipe.ROOT;history,manifest=authenticate_history(root)
    raw=regular(root,OVERLAY_RELATIVE);require(sha(raw)==OVERLAY_SHA256,'Source5665 overlay changed');overlay=json.loads(raw)
    require(overlay['state']=='proposal_pending_independent_implementation_review' and overlay['publicationEnabled'] is False
            and overlay['reviewReferences']=={'semanticCurrentBinding':None,'technicalImplementation':None},'Source5665 manufactured approval')
    require(overlay['generationPolicySHA256']==POLICY_SHA256 and overlay['generationPolicyPath']==POLICY_PATH,'Source5665 policy identity changed')
    # Runtime authenticates the generation identity, never reads private policy/QA.
    for name,digest in overlay['currentArtifacts'].items():
        require(sha(regular(root,name))==digest,'Source5665 current artifact changed: '+name)
    require(pipe.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT==CURRENT_SNAPSHOT,'Source5665 current normative snapshot changed')
    require(tuple(pipe.NORMATIVE_FILES)==tuple(overlay['predecessorNormativeFiles'])+('source-binding-ch56-ch65.json',),'Source5665 norm scope expanded')
    require(sha(canonical({name:manifest['unchangedRootFiles'][S+name] for name in overlay['predecessorNormativeFiles']}))==PREVIOUS_SNAPSHOT,'Source5665 prior normative bytes changed')
    require(mapping==pipe.source_map(pipe.load_source())==read_json(pipe.DATA/'source-map.json'),'Source5665 current map differs')
    before_map=read_json(history/D/'source-map.json');before=read_json(history/D/'progress.json');before_notes=read_json(history/D/'reader-notes.json')
    require(len(mapping['units'])==len(before_map['units'])==len(progress['units'])==4475,'Source5665 unit count changed')
    changes=[]
    for a,z in zip(before_map['units'],mapping['units']):
        require((a['id'],a['chapter'],a['index'],a['layout'])==(z['id'],z['chapter'],z['index'],z['layout']),'Source5665 stable ID/layout/order changed')
        if a!=z:changes.append({'before':a,'after':z})
    require(changes==overlay['changedPendingUnits'] and len(changes)==13,'Source5665 pending source scope changed')
    changed={x['after']['id'] for x in changes};source_by_id={s['id']:s for s in mapping['units']}
    suffix='; '+reference if reference else ''
    for a,z,s in zip(before['units'],progress['units'],mapping['units']):
        expected=copy.deepcopy(a)
        for r in expected['reviews']:r['standardSnapshot']=CURRENT_SNAPSHOT;r['reference']+=suffix
        if a['id'] in changed:
            require(a['state']=='pending' and not a['segments'] and not a['reviews'],'Source5665 source change overlaps accepted work')
            expected['sourceHash']=s['sourceHash']
        if a['state']=='accepted' or exact_baseline:
            require(z==expected,'Source5665 accepted lineage or bounded unit delta changed: '+a['id'])
    require(progress['sourceIssues'][:len(before['sourceIssues'])]==before['sourceIssues'],'Source5665 historical source issue changed')
    require(all(source_by_id.get(i['unitId'],{}).get('chapter',0)>55 for i in progress['sourceIssues'][len(before['sourceIssues']):]),'Source5665 new issue affects accepted prefix')
    cps=copy.deepcopy(before['checkpoints'])
    for cp in cps[:11]:cp['standardSnapshot']=CURRENT_SNAPSHOT;cp['reviewReference']+=suffix
    require(progress['checkpoints'][:11]==cps[:11],'Source5665 accepted checkpoint lineage changed')
    notes=read_json(pipe.DATA/'reader-notes.json')
    require(notes['notes'][:len(before_notes['notes'])]==before_notes['notes'],'Source5665 historical reader note changed')
    require(all(source_by_id.get(n['unitId'],{}).get('chapter',0)>55 for n in notes['notes'][len(before_notes['notes']):]),'Source5665 extra note affects accepted prefix')
    if exact_baseline:
        expected=copy.deepcopy(before);expected['sourceHash']=mapping['sourceHash'];expected['checkpoints']=cps
        for u,s in zip(expected['units'],mapping['units']):
            if u['id'] in changed:u['sourceHash']=s['sourceHash']
            for r in u['reviews']:r['standardSnapshot']=CURRENT_SNAPSHOT;r['reference']+=suffix
        require(progress==expected,'Source5665 nonbounded progress delta')
        require(notes==dict(before_notes,sourceHash=mapping['sourceHash']),'Source5665 nonbounded note delta')
    for name in ('provenance.json','CHECKPOINT.json'):
        require(read_json(pipe.STANDARD/name)=={'schemaVersion':1,'status':transition(reference,technical_reference)['state'],
            'previousB11':read_json(history/S/name),'source5665Transition':transition(reference,technical_reference)},'Source5665 metadata or historical context changed')
    stats=pipe.validate_progress(mapping,progress,CURRENT_SNAPSHOT);pipe.validate_reader_notes(mapping,notes)
    return {'status':'SOURCE5665_PREPARATION_PASS_REVIEW_PENDING','states':stats,'normativeSnapshot':CURRENT_SNAPSHOT,
            'sourceChanges':13,'sourceSpans':16,'acceptedBodiesChanged':0,'installationReady':False,'publicationEnabled':False}


def validate_readiness(pipe,mapping,progress):
    refs={}
    for kind,digest in [('semantic',SEMANTIC_RECEIPT_SHA256),('technical',TECHNICAL_RECEIPT_SHA256)]:
        require(isinstance(digest,str) and len(digest)==64,'Source5665 independent '+kind+' review pending')
        raw=regular(pipe.ROOT,D+'source5665-'+kind+'-review.json');require(sha(raw)==digest,'Source5665 unpinned '+kind+' receipt')
        receipt=json.loads(raw)
        expected={'status':'PASS_SCOPED_CURRENT_BINDING','reviewKind':kind,'requiredFindings':[],
                  'overlaySHA256':OVERLAY_SHA256,'historyManifestSHA256':HISTORY_SHA256,
                  'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,
                  'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,
                  'changedPendingUnits':13,'approvedSourceSpans':16,'acceptedBodiesChanged':0,
                  'notFullCorpusReread':True,'publicationApproved':False}
        require(all(receipt.get(k)==v for k,v in expected.items()),'Source5665 incomplete '+kind+' receipt')
        require(isinstance(receipt.get('reference'),str) and receipt['reference'].strip(),'Source5665 missing genuine review reference')
        refs[kind]=receipt['reference']
    validate_preparation(pipe,mapping,progress,exact_baseline=False,reference=refs['semantic'],technical_reference=refs['technical'])
    return CURRENT_SNAPSHOT
