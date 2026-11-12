"""Exact status/presentation successor. No writes or fabricated approval.

The original B16 validator is preserved. Its copied current successor reads only
explicit reversible predecessor witnesses, while genuine accepted prose/source/
norm/receipt checks remain unchanged. Historical hash reconstruction is not a
claim that current HTML still equals historical bytes.
"""
import json
from pathlib import Path
from hongloumeng_source4655_binding import regular as actual_regular, sha, require

BINDING_PATH='data/hongloumeng/first80-english/reading-presentation-binding.json'
BINDING_SHA256='49f2c564325dda2565da801cc7b95176f2464bca0f6a13e1fbedc98ec8c3d57a'
REVIEW_PATH='data/hongloumeng/first80-english/reading-presentation-review.json'
# Must be pinned only to a genuine independently issued implementation review.
REVIEW_SHA256='9cc64fa0cc797b0099c4ec62768e8283ecace1a5afb15bc65236520a7bb28f90'


def binding(root):
    raw=actual_regular(root,BINDING_PATH)
    require(sha(raw)==BINDING_SHA256,'Presentation binding bytes changed')
    value=json.loads(raw)
    require(value['schemaVersion']==1 and value['b16Commit']=='45449fd050f8c9ec414c14fecdba570529e2ae7f','Presentation predecessor differs')
    require(value['historicalReplayClaim']=='exact bounded predecessor reconstruction, not unchanged current HTML','Presentation historical claim differs')
    return value


def historical_bytes(root,relative,raw,row):
    digest=sha(raw)
    if digest==row['beforeSHA256']:
        return raw
    require(digest==row['afterSHA256'],'Unapproved current presentation bytes: '+relative)
    if row['kind']=='html':
        text=raw.decode('utf-8')
        for insertion in row['insertions']:
            require(text.count(insertion)==1,'Missing/duplicate exact presentation insertion')
            text=text.replace(insertion,'',1)
        before=text.encode('utf-8')
    elif row['kind']=='status':
        require(raw.count(b'"status": "finalized"')==1,'Missing/duplicate exact finalized status')
        before=raw.replace(b'"status": "finalized"',b'"status": "draft"',1)
        old=json.loads(before);new=json.loads(raw)
        require(new==dict(old,status='finalized'),'Non-status canonical manifest change')
    elif row['kind']=='script':
        before=actual_regular(root,row['archivePath'])
    else:
        raise ValueError('Unknown presentation witness kind')
    require(sha(before)==row['beforeSHA256'],'Exact historical witness reconstruction differs: '+relative)
    return before


def read_historical(root,relative):
    """B16 history reads only. All unlisted paths retain strict actual hashes."""
    raw=actual_regular(root,relative)
    if not (root/BINDING_PATH).is_file():
        return raw  # An actual immutable archive root, not the current root.
    row=binding(root)['changedRootWitnesses'].get(relative)
    return historical_bytes(root,relative,raw,row) if row else raw


def authenticate_final_manifest(root,relative,raw,historical_sha):
    value=binding(root);row=value['changedRootWitnesses'].get(relative)
    require(row and row['kind']=='status' and row['beforeSHA256']==historical_sha,'Unknown finalized manifest context')
    require(sha(raw)==row['afterSHA256'],'Unknown current finalized manifest hash')
    historical_bytes(root,relative,raw,row)


def validate_state(root):
    """Exactly prepared or generated; reject mixed data states and unrelated edits."""
    value=binding(root);states=set()
    for relative,row in value['changedRootWitnesses'].items():
        raw=actual_regular(root,relative);historical_bytes(root,relative,raw,row)
        if row['kind']!='script':
            states.add('prepared' if sha(raw)==row['beforeSHA256'] else 'generated')
    require(len(states)==1,'Mixed Chinese status/presentation state')
    phase=next(iter(states))
    for relative,digest in value['implementationHashes'].items():
        require(sha(actual_regular(root,relative))==digest,'Current presentation implementation changed: '+relative)
    for relative,digest in value['unchangedContentHashes'].items():
        require(sha(actual_regular(root,relative))==digest,'Canonical/accepted content changed: '+relative)
    for relative,digest in value['publicRetrospectiveHashes'].items():
        require(sha(actual_regular(root,relative))==digest,'Public retrospective changed')
    for relative,digest in value['continuationUnchangedHashes'].items():
        require(sha(actual_regular(root,relative))==digest,'Unrelated continuation file changed: '+relative)
    row=value['continuationDirectoryDisplay']
    expected=row['beforeSHA256'] if phase=='prepared' else row['afterSHA256']
    require(sha(actual_regular(root,row['path']))==expected,'Unexpected continuation directory display state')
    return {'state':phase,'acceptedBodiesChanged':0,'sourceMapBytesChanged':False,'historicalPresentationReconstructed':True,'publicationAuthorized':False}


def require_review(root):
    require(isinstance(REVIEW_SHA256,str) and len(REVIEW_SHA256)==64,'Independent presentation implementation review pending')
    raw=actual_regular(root,REVIEW_PATH)
    require(sha(raw)==REVIEW_SHA256,'Unpinned presentation review')
    review=json.loads(raw)
    expected={'status':'PASS_CURRENT_PRESENTATION_IMPLEMENTATION','bindingSHA256':BINDING_SHA256,
              'b16Commit':'45449fd050f8c9ec414c14fecdba570529e2ae7f','acceptedUnits':4475,'notes':80,
              'sourceMapBytesChanged':False,'acceptedBodiesChanged':0,'requiredFindings':[],
              'scope':'implementation-and-local-generation-gates','generatedSiteAudited':False,'publicDeploymentAuthorized':False}
    require(all(review.get(k)==v for k,v in expected.items()),'Incomplete independent presentation review')
    require(isinstance(review.get('reference'),str) and review['reference'].strip(),'Genuine independent review reference required')
