"""Exact pending-source transition after accepted1-65 B13.

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
HISTORY_RELATIVE=D+'history/source-ch66-ch80-before'
HISTORY_SHA256='1c88036e858ab4ffe66087113b1660555b47412860910b1b54fca2998004dc31'
OVERLAY_RELATIVE=S+'source-binding-ch66-ch80.json'
OVERLAY_SHA256='7a6cb719dbe5a739bb6274e1bff389de413353248ce5c0b13271138b967580ff'
PREVIOUS_SNAPSHOT='77478ba611615b9de857967893482789016bc5587726be1d412e5eba4f6b4201'
CURRENT_SNAPSHOT='f665d4fa0a3c1816ffbfd408f4143007f96b74a80aa429ebbfbfd61eb46f45c7'
SEMANTIC_RECEIPT_SHA256='92031af91984daadb06b114fcbe9d01456acec608ea4a4444042d1a0d8d0a745'
TECHNICAL_RECEIPT_SHA256='a8a39f6b3adda2fc49ce8352b731ea4d349fac8cedfdd13f31514779ecdd444b'
POLICY_PATH='data/hongloumeng/first80/author-ch66-ch80-source-policy.json'
POLICY_SHA256='53cb906e1328fb6def86b00bdc7bbe951c86be9bbc7aef0668e9d3211bd96232'
BUILDER_PATH='scripts/build_hongloumeng_first80.py'
BUILDER_SHA256='d3b59f79d446830a3eba6237bfbcbfa290aed15c013c92091e3562c7dc9f7cf0'


def authenticate_history(root):
    history=root/HISTORY_RELATIVE
    raw=regular(history,'manifest.json');require(sha(raw)==HISTORY_SHA256,'Source6680 historical manifest changed')
    manifest=json.loads(raw)
    require(manifest['normativeSnapshot']==PREVIOUS_SNAPSHOT,'Source6680 predecessor norm changed')
    for name,digest in manifest['files'].items():
        require(sha(regular(history,name))==digest,'Source6680 archived predecessor changed: '+name)
    for name,digest in manifest['unchangedRootFiles'].items():
        require(sha(regular(root,name))==digest,'Source6680 unchanged predecessor changed: '+name)
    return history,manifest


def materialize_predecessor(root,destination):
    """Regression-only finite B13 fixture, not used by normal runtime validation."""
    history,manifest=authenticate_history(root)
    destination=Path(destination).resolve();require(not destination.exists(),'Source6680 predecessor output exists')
    destination.mkdir()
    for name in sorted(set(manifest['files'])|set(manifest['unchangedRootFiles'])):
        base=history if name in manifest['files'] else root
        payload=regular(base,name)
        target=destination/name;require(destination in target.parents,'Source6680 predecessor output escapes root')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
    return destination


def transition(reference=None,technical_reference=None):
    require((reference is None)==(technical_reference is None),'Source6680 incomplete real approval references')
    return {'state':'pending_independent_source_binding_review' if reference is None else 'independently_reviewed_source_binding',
            'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,
            'historyManifestSHA256':HISTORY_SHA256,'overlaySHA256':OVERLAY_SHA256,
            'semanticCurrentBindingReviewReference':reference,'technicalReviewReference':technical_reference,
            'changedPendingUnits':25,'approvedSourceSpans':30,'acceptedBodiesChanged':0,
            'oldReviewObjectsRetainedInAuthenticContext':True,'notFullCorpusReread':True,
            'publicationEnabled':False}


def validate_preparation(pipe,mapping,progress,*,exact_baseline=True,reference=None,technical_reference=None):
    root=pipe.ROOT;history,manifest=authenticate_history(root)
    raw=regular(root,OVERLAY_RELATIVE);require(sha(raw)==OVERLAY_SHA256,'Source6680 overlay changed');overlay=json.loads(raw)
    require(overlay['state']=='proposal_pending_independent_implementation_review' and overlay['publicationEnabled'] is False
            and overlay['reviewReferences']=={'semanticCurrentBinding':None,'technicalImplementation':None},'Source6680 manufactured approval')
    require(overlay['generationPolicySHA256']==POLICY_SHA256 and overlay['generationPolicyPath']==POLICY_PATH,'Source6680 policy identity changed')
    require(overlay['generationBuilderPath']==BUILDER_PATH and overlay['generationBuilderSHA256']==BUILDER_SHA256,'Source6680 generation builder identity changed')
    require(BUILDER_PATH not in overlay['currentArtifacts'] and not any(n.startswith('data/hongloumeng/first80/') for n in overlay['currentArtifacts']),'Source6680 private generation input in public artifacts')
    # Runtime authenticates the generation identity, never reads private policy/QA.
    for name,digest in overlay['currentArtifacts'].items():
        require(sha(regular(root,name))==digest,'Source6680 current artifact changed: '+name)
    require(pipe.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT==CURRENT_SNAPSHOT,'Source6680 current normative snapshot changed')
    require(tuple(pipe.NORMATIVE_FILES)==tuple(overlay['predecessorNormativeFiles'])+('source-binding-ch66-ch80.json',),'Source6680 norm scope expanded')
    require(sha(canonical({name:manifest['unchangedRootFiles'][S+name] for name in overlay['predecessorNormativeFiles']}))==PREVIOUS_SNAPSHOT,'Source6680 prior normative bytes changed')
    require(mapping==pipe.source_map(pipe.load_source())==read_json(pipe.DATA/'source-map.json'),'Source6680 current map differs')
    before_map=read_json(history/D/'source-map.json');before=read_json(history/D/'progress.json');before_notes=read_json(history/D/'reader-notes.json')
    require(len(mapping['units'])==len(before_map['units'])==len(progress['units'])==4475,'Source6680 unit count changed')
    changes=[]
    for a,z in zip(before_map['units'],mapping['units']):
        require((a['id'],a['chapter'],a['index'],a['layout'])==(z['id'],z['chapter'],z['index'],z['layout']),'Source6680 stable ID/layout/order changed')
        if a!=z:changes.append({'before':a,'after':z})
    require(changes==overlay['changedPendingUnits'] and len(changes)==25,'Source6680 pending source scope changed')
    changed={x['after']['id'] for x in changes};source_by_id={s['id']:s for s in mapping['units']}
    suffix='; '+reference if reference else ''
    for a,z,s in zip(before['units'],progress['units'],mapping['units']):
        expected=copy.deepcopy(a)
        for r in expected['reviews']:r['standardSnapshot']=CURRENT_SNAPSHOT;r['reference']+=suffix
        if a['id'] in changed:
            require(a['state']=='pending' and not a['segments'] and not a['reviews'],'Source6680 source change overlaps accepted work')
            expected['sourceHash']=s['sourceHash']
        if a['state']=='accepted' or exact_baseline:
            require(z==expected,'Source6680 accepted lineage or bounded unit delta changed: '+a['id'])
    require(progress['sourceIssues'][:len(before['sourceIssues'])]==before['sourceIssues'],'Source6680 historical source issue changed')
    require(all(source_by_id.get(i['unitId'],{}).get('chapter',0)>65 for i in progress['sourceIssues'][len(before['sourceIssues']):]),'Source6680 new issue affects accepted prefix')
    cps=copy.deepcopy(before['checkpoints'])
    for cp in cps[:13]:cp['standardSnapshot']=CURRENT_SNAPSHOT;cp['reviewReference']+=suffix
    require(progress['checkpoints'][:13]==cps[:13],'Source6680 accepted checkpoint lineage changed')
    notes=read_json(pipe.DATA/'reader-notes.json')
    require(notes['notes'][:len(before_notes['notes'])]==before_notes['notes'],'Source6680 historical reader note changed')
    require(all(source_by_id.get(n['unitId'],{}).get('chapter',0)>65 for n in notes['notes'][len(before_notes['notes']):]),'Source6680 extra note affects accepted prefix')
    if exact_baseline:
        expected=copy.deepcopy(before);expected['sourceHash']=mapping['sourceHash'];expected['checkpoints']=cps
        for u,s in zip(expected['units'],mapping['units']):
            if u['id'] in changed:u['sourceHash']=s['sourceHash']
            for r in u['reviews']:r['standardSnapshot']=CURRENT_SNAPSHOT;r['reference']+=suffix
        require(progress==expected,'Source6680 nonbounded progress delta')
        require(notes==dict(before_notes,sourceHash=mapping['sourceHash']),'Source6680 nonbounded note delta')
    for name in ('provenance.json','CHECKPOINT.json'):
        require(read_json(pipe.STANDARD/name)=={'schemaVersion':1,'status':transition(reference,technical_reference)['state'],
            'previousB13':read_json(history/S/name),'source6680Transition':transition(reference,technical_reference)},'Source6680 metadata or historical context changed')
    stats=pipe.validate_progress(mapping,progress,CURRENT_SNAPSHOT);pipe.validate_reader_notes(mapping,notes)
    return {'status':'SOURCE6680_PREPARATION_PASS_REVIEW_PENDING','states':stats,'normativeSnapshot':CURRENT_SNAPSHOT,
            'sourceChanges':25,'sourceSpans':30,'acceptedBodiesChanged':0,'installationReady':False,'publicationEnabled':False}


def validate_readiness(pipe,mapping,progress):
    for kind,digest in [('semantic',SEMANTIC_RECEIPT_SHA256),('technical',TECHNICAL_RECEIPT_SHA256)]:
        require(isinstance(digest,str) and len(digest)==64,'Source6680 independent '+kind+' review pending')
    refs={}
    for kind,digest in [('semantic',SEMANTIC_RECEIPT_SHA256),('technical',TECHNICAL_RECEIPT_SHA256)]:
        require(isinstance(digest,str) and len(digest)==64,'Source6680 independent '+kind+' review pending')
        raw=regular(pipe.ROOT,D+'source6680-'+kind+'-review.json');require(sha(raw)==digest,'Source6680 unpinned '+kind+' receipt')
        receipt=json.loads(raw)
        expected={'status':'PASS_SCOPED_CURRENT_BINDING','reviewKind':kind,'requiredFindings':[],
                  'overlaySHA256':OVERLAY_SHA256,'historyManifestSHA256':HISTORY_SHA256,
                  'previousNormativeSnapshot':PREVIOUS_SNAPSHOT,'normativeSnapshot':CURRENT_SNAPSHOT,
                  'sourceHash':pipe.READING_SHA,'sourceMapSHA256':pipe.SOURCE_MAP_SHA,
                  'changedPendingUnits':25,'approvedSourceSpans':30,'acceptedBodiesChanged':0,
                  'notFullCorpusReread':True,'publicationApproved':False}
        require(all(receipt.get(k)==v for k,v in expected.items()),'Source6680 incomplete '+kind+' receipt')
        require(isinstance(receipt.get('reference'),str) and receipt['reference'].strip(),'Source6680 missing genuine review reference')
        refs[kind]=receipt['reference']
    validate_preparation(pipe,mapping,progress,exact_baseline=False,reference=refs['semantic'],technical_reference=refs['technical'])
    return CURRENT_SNAPSHOT
