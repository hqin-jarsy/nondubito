"""Bounded chapter72 corrections with authenticated predecessor replay."""
import copy
import json
from pathlib import Path
from hongloumeng_ch005_author_binding import sha, require, regular, load_module
ROOT = Path(__file__).resolve().parents[1]
D = 'data/hongloumeng/first80-english/'
HISTORY = D + 'history/ch072-decisions-before'
BINDING = D + 'ch072-decisions-binding.json'
BINDING_SHA256 = '5835072c00669bd7869adf7d63076dc8c60c64c9c014d332df79866085578a7f'
REVIEW = D + 'ch072-decisions-current-review.json'
REVIEW_SHA256 = 'e4ea3ebc8fc28d7268d1e4f538277ac781d5bb74cdc5dd0ac38738bc75891e26'
SEMANTIC = D + 'ch072-decisions-semantic-review.json'
SEMANTIC_SHA256 = '6d254a866e06b08a6cfd8a4c551cb715ca4fa582b06c60e74f7272194764fc7b'
REFERENCE = 'CH072-AUTHOR-DECISIONS-INDEPENDENT-UNIT-REVIEW-20261113'
TARGETS = ('hlm-c072-b0018', 'hlm-c072-b0022')


def binding(root=ROOT):
    raw = regular(root, BINDING)
    require(BINDING_SHA256 and sha(raw) == BINDING_SHA256, 'Unpinned ch072-decisions binding')
    value = json.loads(raw)
    require([(c['chapter'], c['blockIndex'], c['unitId'], c['before'], c['after'], c['englishBefore'], c['englishAfter']) for c in value['changes']] == [
        (72,17,TARGETS[0],'不上半年','不上半月','In less than half a year','In less than half a month'),
        (72,21,TARGETS[1],'也要‘前人撒土迷了后人的眼’才是','也不要‘前人撒土迷了后人的眼’才是','but we must remember that “The earth scattered by those who go before gets in the eyes of those who follow.”','but we must not let “those who go before scatter earth in the eyes of those who follow.”')], 'Correction scope changed')
    for path, checksum in value['preservedDependencies'].items():
        require(sha(regular(root,path)) == checksum, 'Preserved predecessor dependency differs: '+path)
    for path, checksum in value['archivedOnlyDependencies'].items():
        require(sha(regular(Path(root)/HISTORY,path)) == checksum, 'Predecessor-only archive differs: '+path)
    return value


def predecessor(root=ROOT):
    root=Path(root); bound=binding(root); history=root/HISTORY
    def before(context,path):
        if Path(context).resolve()==root.resolve() and path in bound['files']:
            row=bound['files'][path]
            require(sha(regular(root,path))==row['afterSHA256'],'Current successor bytes differ: '+path)
            raw=regular(history,path)
            require(sha(raw)==row['beforeSHA256'],'Predecessor archive differs: '+path)
            return raw
        return regular(context,path)
    prior=load_module(root/'scripts/hongloumeng_later_two_readings_binding.py','_ch072_later_predecessor')
    prior.regular=before
    pipe=load_module(history/'scripts/hongloumeng_english_pipeline.py','_ch072_pipeline_predecessor')
    pipe.ROOT=root;pipe.SOURCE=history/'data/hongloumeng/first80-public';pipe.DATA=history/D
    pipe.STANDARD=root/'docs/hongloumeng/translation'
    mapping=json.loads(before(root,D+'source-map.json'));progress=json.loads(before(root,D+'progress.json'))
    import sys
    from unittest.mock import patch
    trad=load_module(history/'scripts/build_hongloumeng_first80_traditional.py','_ch072_prior_trad')
    trad.DATA=history/'data/hongloumeng/first80-public';outputs=trad.outputs
    trad.outputs=lambda data=trad.DATA: outputs(trad.DATA if Path(data)==root/'data/hongloumeng/first80-public' else data)
    with patch.dict(sys.modules,{'build_hongloumeng_first80_traditional':trad}):
        prior.validate_preparation(pipe,mapping,progress,reviewed=True)
    return pipe,mapping,progress,json.loads(before(root,D+'reader-notes.json')),prior


def validate_preparation(pipe,mapping,progress,*,reviewed=False):
    bound=binding(pipe.ROOT)
    for path,row in bound['files'].items():
        require(sha(regular(pipe.ROOT,path))==row['afterSHA256'],'Current successor bytes differ: '+path)
    old,oldmap,oldprogress,oldnotes,_=predecessor(pipe.ROOT)
    expected=copy.deepcopy(old.load_source())
    for c in bound['changes']:
        block=expected['chapters'][c['chapter']-1]['blocks'][c['blockIndex']]
        require(block['text']==c['beforeUnitText'] and block['text'].count(c['before'])==1,'Prior source unit differs')
        require(c['afterUnitText']==block['text'].replace(c['before'],c['after']),'Source replacement differs')
        block['text']=c['afterUnitText']
    require(pipe.load_source()==expected,'Source delta widened')
    history=Path(pipe.ROOT)/HISTORY; public='data/hongloumeng/first80-public/'
    manifest=json.loads(regular(history,public+'manifest.json'))
    manifest['character_count'] += 1
    manifest['chapters'][71]['character_count'] += 1
    manifest['reading_sha256']=mapping['sourceHash'];manifest['body_sha256']=mapping['bodyHash']
    traditional=json.loads(regular(history,public+'reading.zh-hant.json'))
    for c in bound['changes']:
        i=c['chapter']-1
        manifest['chapters'][i]['body_sha256']=sha(''.join(x['text'] for x in expected['chapters'][i]['blocks']))
        block=traditional['chapters'][i]['blocks'][c['blockIndex']]
        require(block['text'].count(c['traditionalBefore'])==1,'Prior Traditional reading differs')
        block['text']=block['text'].replace(c['traditionalBefore'],c['traditionalAfter'])
    require(json.loads(regular(pipe.ROOT,public+'manifest.json'))==manifest,'Manifest delta widened')
    require(json.loads(regular(pipe.ROOT,public+'reading.zh-hant.json'))==traditional,'Traditional delta widened')
    rules=json.loads(regular(history,public+'conversion.zh-hant.json'))
    rules['source_sha256']=mapping['sourceHash'];rules['source_manifest_sha256']=mapping['manifestHash']
    for exception in rules['exceptions']:
        if exception['chapter']==72 and exception['block'] in (17,21):
            exception['unit_sha256']=sha(expected['chapters'][71]['blocks'][exception['block']]['text'])
    require(json.loads(regular(pipe.ROOT,public+'conversion.zh-hant.json'))==rules,'Conversion delta widened')
    import build_hongloumeng_first80_traditional as trad
    for name,text in trad.outputs(Path(pipe.ROOT)/public).items():
        require(regular(pipe.ROOT,public+name)==text.encode(),'Traditional regeneration differs')
    require(mapping==pipe.source_map(expected),'Current source map differs')
    expected_map=copy.deepcopy(oldmap)
    for k in ['sourceHash','manifestHash','bodyHash']:expected_map[k]=mapping[k]
    for c in bound['changes']:
        unit=next(u for u in expected_map['units'] if u['id']==c['unitId'])
        unit['sourceHash']=sha(c['afterUnitText'])
        unit['characterCount'] += len(c['afterUnitText'])-len(c['beforeUnitText'])
    require(mapping==expected_map,'Source map delta widened')
    snapshot=pipe.standard_snapshot()
    require(snapshot==old.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT,'Unchanged normative standard differs')
    require(SEMANTIC_SHA256 and sha(regular(pipe.ROOT,SEMANTIC))==SEMANTIC_SHA256,'Independent semantic review pending')
    semantic=json.loads(regular(pipe.ROOT,SEMANTIC))
    candidate=json.loads(regular(pipe.ROOT,D+'ch072-decisions-semantic-candidate.json'))
    require(semantic['status']=='PASS' and semantic['requiredFindings']==[] and semantic['fullCorpusReread'] is False,'Invalid semantic review')
    require(semantic['candidateSHA256']==sha(regular(pipe.ROOT,D+'ch072-decisions-semantic-candidate.json')),'Frozen semantic candidate differs')
    require(set(semantic['reviewTypes'])=={'bilingual','literary','consistency'} and semantic['reference']==REFERENCE,'Missing semantic review type')
    expected=copy.deepcopy(oldprogress);expected['sourceHash']=mapping['sourceHash']
    for c,reviewed_unit,frozen in zip(bound['changes'],semantic['units'],candidate['units']):
        unit=next(u for u in expected['units'] if u['id']==c['unitId'])
        require(frozen['beforeUnit']==unit and frozen['beforeSourceText']==c['beforeUnitText'],'Frozen prior candidate differs')
        unit['sourceHash']=sha(c['afterUnitText'])
        require(unit['segments'][0]['text'].count(c['englishBefore'])==1,'Prior English wording differs')
        unit['segments'][0]['text']=unit['segments'][0]['text'].replace(c['englishBefore'],c['englishAfter'])
        require(frozen['afterSourceText']==c['afterUnitText'] and frozen['candidateUnit']==unit,'Frozen successor candidate differs')
        require(reviewed_unit==dict(unitId=c['unitId'],afterSourceText=c['afterUnitText'],segments=unit['segments'],readerNotes=[]),'Semantic review candidate differs')
        for rev in unit['reviews']:
            rev['contentHash']=pipe.content_hash(unit,expected['sourceIssues'])
            rev['reference']=REFERENCE+' (complete target unit reread; earlier receipt retained in predecessor)'
    require(len(semantic['units'])==len(candidate['units'])==2,'Semantic scope differs')
    for check in expected['checkpoints']:
        if check['first']==71:
            check['corpusHash']=pipe.batch_hash([u for s,u in zip(mapping['units'],expected['units']) if check['first']<=s['chapter']<=check['last']],expected['sourceIssues'])
            check['reviewReference']+='; '+REFERENCE+' (two target units reread in this batch; other units unchanged; no batch reread)'
    require(progress==expected,'English delta widened')
    notes=copy.deepcopy(oldnotes);notes['sourceHash']=mapping['sourceHash']
    require(not [n for n in notes['notes'] if n['unitId'] in TARGETS],'Unexpected target reader note')
    require(json.loads(regular(pipe.ROOT,D+'reader-notes.json'))==notes,'Reader note delta widened')
    validate_html(pipe.ROOT)
    pipe.validate_progress(mapping,progress,snapshot);pipe.validate_reader_notes(mapping,notes)
    if reviewed:
        require(REVIEW_SHA256 and sha(regular(pipe.ROOT,REVIEW))==REVIEW_SHA256,'Independent ch072-decisions review pending')
        review=json.loads(regular(pipe.ROOT,REVIEW))
        require(review['bindingSHA256']==BINDING_SHA256 and review['fullCorpusReread'] is False and review['requiredFindings']==[] and review['status']=='PASS_BOUNDED_CH072_DECISIONS','Invalid independent review')
    return snapshot


def validate_readiness(pipe,mapping,progress):
    return validate_preparation(pipe,mapping,progress,reviewed=True)


def note_record(record,note,source,unit,root=ROOT):
    # The chapter49 frozen overlay is unchanged, but its binding must read its
    # authenticated predecessor bytes rather than the new chapter72 edition.
    return predecessor(root)[4].note_record(record,note,source,unit,root)


def validate_html(root=ROOT):
    changes=binding(root)['changes']
    for lang,before,after in [('', 'before','after'),('zh-hant/','traditionalBefore','traditionalAfter'),('en/','englishBefore','englishAfter')]:
        path=f"classics/hongloumeng/{lang}ch072.html"
        expected=regular(Path(root)/HISTORY,path).decode()
        for c in changes:
            require(expected.count(c[before])==1,'Prior HTML occurrence differs')
            expected=expected.replace(c[before],c[after])
        require(regular(root,path)==expected.encode(),'HTML delta widened: '+path)
