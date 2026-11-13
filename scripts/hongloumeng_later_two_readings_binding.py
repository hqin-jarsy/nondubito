"""Bounded chapter55/57 corrections with authenticated predecessor replay."""
import copy
import json
from pathlib import Path
from hongloumeng_ch005_author_binding import sha, require, regular, load_module
ROOT = Path(__file__).resolve().parents[1]
D = 'data/hongloumeng/first80-english/'
HISTORY = D + 'history/later-two-readings-before'
BINDING = D + 'later-two-readings-binding.json'
BINDING_SHA256 = 'e6699b8a534bc4b27d44d8bf2ae405bf8f231d46d7aafa97a56db975805b6480'
REVIEW = D + 'later-two-readings-current-review.json'
REVIEW_SHA256 = '4d2b66afbbef93df4a80808e2cf9ff29fcdfda01b6bfc9a59d7d1b1ac8607077'
SEMANTIC = D + 'later-two-readings-semantic-review.json'
SEMANTIC_SHA256 = '92a4219731c337a2262414760cc2f62c8891e39171a6b7d22f68032b6af0745c'
REFERENCE = 'CH055-057-KANG-MARRIAGE-INDEPENDENT-UNIT-REVIEW-20261113'
TARGETS = ('hlm-c055-b0039', 'hlm-c057-b0046')


def binding(root=ROOT):
    raw = regular(root, BINDING)
    require(BINDING_SHA256 and sha(raw) == BINDING_SHA256, 'Unpinned later-two-readings binding')
    value = json.loads(raw)
    require([(c['chapter'], c['blockIndex'], c['unitId'], c['before'], c['after'], c['englishBefore'], c['englishAfter']) for c in value['changes']] == [
        (55,38,TARGETS[0],'热灶火坑','热灶火炕','fire-pit','heated kang'),
        (57,45,TARGETS[1],'不先定了他妹妹的事','不先完了他妹妹的事','until his sister’s affairs are settled','until his sister is married')], 'Correction scope changed')
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
    prior=load_module(root/'scripts/hongloumeng_seven_character_binding.py','_later_seven_predecessor')
    prior.regular=before
    pipe=load_module(history/'scripts/hongloumeng_english_pipeline.py','_later_pipeline_predecessor')
    pipe.ROOT=root;pipe.SOURCE=history/'data/hongloumeng/first80-public';pipe.DATA=history/D
    pipe.STANDARD=root/'docs/hongloumeng/translation'
    mapping=json.loads(before(root,D+'source-map.json'));progress=json.loads(before(root,D+'progress.json'))
    import sys
    from unittest.mock import patch
    trad=load_module(history/'scripts/build_hongloumeng_first80_traditional.py','_later_prior_trad')
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
        require(len(c['beforeUnitText'])==len(c['afterUnitText']),'Character count changed')
        block['text']=c['afterUnitText']
    require(pipe.load_source()==expected,'Source delta widened')
    history=Path(pipe.ROOT)/HISTORY; public='data/hongloumeng/first80-public/'
    manifest=json.loads(regular(history,public+'manifest.json'))
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
    require(not [x for x in rules['exceptions'] if (x['chapter'],x['block']) in [(55,38),(57,45)]],'Unexpected target Traditional exception')
    require(json.loads(regular(pipe.ROOT,public+'conversion.zh-hant.json'))==rules,'Conversion delta widened')
    import build_hongloumeng_first80_traditional as trad
    for name,text in trad.outputs(Path(pipe.ROOT)/public).items():
        require(regular(pipe.ROOT,public+name)==text.encode(),'Traditional regeneration differs')
    require(mapping==pipe.source_map(expected),'Current source map differs')
    expected_map=copy.deepcopy(oldmap)
    for k in ['sourceHash','manifestHash','bodyHash']:expected_map[k]=mapping[k]
    for c in bound['changes']:
        next(u for u in expected_map['units'] if u['id']==c['unitId'])['sourceHash']=sha(c['afterUnitText'])
    require(mapping==expected_map,'Source map delta widened')
    snapshot=pipe.standard_snapshot()
    require(snapshot==old.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT,'Unchanged normative standard differs')
    require(SEMANTIC_SHA256 and sha(regular(pipe.ROOT,SEMANTIC))==SEMANTIC_SHA256,'Independent semantic review pending')
    semantic=json.loads(regular(pipe.ROOT,SEMANTIC))
    candidate=json.loads(regular(pipe.ROOT,D+'later-two-readings-semantic-candidate.json'))
    require(semantic['status']=='PASS' and semantic['requiredFindings']==[] and semantic['fullCorpusReread'] is False,'Invalid semantic review')
    require(semantic['candidateSHA256']==sha(regular(pipe.ROOT,D+'later-two-readings-semantic-candidate.json')),'Frozen semantic candidate differs')
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
        if check['first'] in (51,56):
            check['corpusHash']=pipe.batch_hash([u for s,u in zip(mapping['units'],expected['units']) if check['first']<=s['chapter']<=check['last']],expected['sourceIssues'])
            check['reviewReference']+='; '+REFERENCE+' (one target unit reread in this batch; other units unchanged; no batch reread)'
    require(progress==expected,'English delta widened')
    notes=copy.deepcopy(oldnotes);notes['sourceHash']=mapping['sourceHash']
    require(not [n for n in notes['notes'] if n['unitId'] in TARGETS],'Unexpected target reader note')
    require(json.loads(regular(pipe.ROOT,D+'reader-notes.json'))==notes,'Reader note delta widened')
    validate_html(pipe.ROOT)
    pipe.validate_progress(mapping,progress,snapshot);pipe.validate_reader_notes(mapping,notes)
    if reviewed:
        require(REVIEW_SHA256 and sha(regular(pipe.ROOT,REVIEW))==REVIEW_SHA256,'Independent later-two-readings review pending')
        review=json.loads(regular(pipe.ROOT,REVIEW))
        require(review['bindingSHA256']==BINDING_SHA256 and review['fullCorpusReread'] is False and review['requiredFindings']==[] and review['status']=='PASS_BOUNDED_LATER_TWO_READINGS','Invalid independent review')
    return snapshot


def validate_readiness(pipe,mapping,progress):
    return validate_preparation(pipe,mapping,progress,reviewed=True)


def note_record(record,note,source,unit,root=ROOT):
    # The chapter49 frozen overlay is unchanged, but its binding must read its
    # authenticated predecessor bytes rather than the new chapter55/57 edition.
    return predecessor(root)[4].note_record(record,note,source,unit,root)


def validate_html(root=ROOT):
    for c in binding(root)['changes']:
        for lang,before,after in [('',c['before'],c['after']),('zh-hant/',c['traditionalBefore'],c['traditionalAfter']),('en/',c['englishBefore'],c['englishAfter'])]:
            path=f"classics/hongloumeng/{lang}ch{c['chapter']:03}.html"
            expected=regular(Path(root)/HISTORY,path).decode()
            require(expected.count(before)==1,'Prior HTML occurrence differs')
            require(regular(root,path)==expected.replace(before,after).encode(),'HTML delta widened: '+path)


def apply_model(model,raw_source):
    """Optional private producer; never imported by public readiness."""
    from build_hongloumeng_first80 import author_change_spans,selection_source_chars,effective_author_changes
    for c in binding()['changes']:
        chapter=model['chapters'][c['chapter']-1];block=chapter['blocks'][c['blockIndex']]
        require(block['text']==c['beforeUnitText'],'Producer source unit differs')
        old,new=c['before'],c['after'];require(len(old)==len(new),'Unexpected coordinate shift')
        require(raw_source.count(old)==1,'Producer original occurrence is not unique')
        start=raw_source.index(old);end=start+len(old);ident=f"PUBLIC-LATER-TWO-{c['chapter']:03}"
        change=dict(id=ident,chapter=c['chapter'],title='有据上下文校订',status='adopted_editorial_choice',applied=True,mode='replace',source_start_char=start,source_end_char=end,original=old,proposed=new,context_before=raw_source[start-20:start],context_after=raw_source[end:end+20],reason=c['evidenceLimit'],authorization_type='delegated_public_transcription_selection',decision_file='later-two-readings-binding.json',decision_sha256=BINDING_SHA256,public_references=c['references'])
        chapter['body']=chapter['body'].replace(old,new);block['text']=c['afterUnitText'];block['author_change_ids'].append(ident)
        for row in chapter['layout_ranges']+chapter['author_layout_ranges']:
            if 'exact_body_text' in row:row['exact_body_text']=row['exact_body_text'].replace(old,new)
        chapter['author_changes'].append(change);model['author_emendations'].append(change)
        chapter['body_sha256']=sha(chapter['body']);chapter['author_change_spans']=author_change_spans(selection_source_chars(chapter,raw_source),effective_author_changes(chapter))
        for name in ('user_delegated_readability_selection','total_semantic_changes','current_active_semantic_changes','applied_occurrence_records','current_active_occurrence_records'):model['emendation_authority_counts'][name]+=1
        for issue in chapter['issues']:
            if old in issue.get('text',''):issue['resolution_note']='此处已据公开文本及上下文作有据校订；原摘录仅为历史，不再描述当前正文。'
        require(''.join(b['text'] for b in chapter['blocks'])==chapter['body'],'Producer block/body mismatch')
    return model
