"""One independently reviewed rose-paste correction over authenticated predecessors.

Only module-local readers replay frozen earlier editions. The length-changing
producer correction preserves original-source coordinates and shifts body offsets.
"""
import copy
import json
from pathlib import Path
from hongloumeng_ch005_author_binding import sha, require, regular, load_module
ROOT = Path(__file__).resolve().parents[1]
D = 'data/hongloumeng/first80-english/'
HISTORY = D + 'history/rose-paste-before'
BINDING = D + 'rose-paste-binding.json'
BINDING_SHA256 = '9bc40365d0abfb3ff1fbe82bcb64ec3867dcb697942277afa7b22066c378f942'
REVIEW = D + 'rose-paste-current-review.json'
REVIEW_SHA256 = 'ffa8eea0b0b066eec28a627e8b131bc3a4f9a2c883437c395ec6cae2da782b62'
SEMANTIC = D + 'rose-paste-semantic-review.json'
SEMANTIC_SHA256 = 'edeabf3e5927b7e93625f2639fc8728dbca4dadc1bbc010811b3cfc1b4df727b'
TARGET = 'hlm-c044-b0024'
REFERENCE = 'ROSE-PASTE-CH044-INDEPENDENT-20261113'


def binding(root=ROOT):
    raw = regular(root, BINDING)
    require(BINDING_SHA256 and sha(raw) == BINDING_SHA256, 'Unpinned rose-paste binding')
    value = json.loads(raw)
    c = value['change']
    require((c['chapter'],c['blockIndex'],c['unitId'],c['before'],c['after']) ==
            (44,23,TARGET,'如倒膏子一样','如玫瑰膏子一样'), 'Correction scope changed')
    return value


def predecessor(root=ROOT):
    root = Path(root); bound = binding(root); history = root/HISTORY
    def before(context,path):
        if Path(context).resolve() == root.resolve() and path in bound['files']:
            row = bound['files'][path]
            require(sha(regular(root,path)) == row['afterSHA256'], 'Current successor bytes differ: '+path)
            raw = regular(history,path)
            require(sha(raw) == row['beforeSHA256'], 'Predecessor archive differs: '+path)
            return raw
        return regular(context,path)
    prior = load_module(root/'scripts/hongloumeng_two_readings_binding.py','_hlm_rose_two_predecessor')
    prior.regular = before
    pipe = load_module(history/'scripts/hongloumeng_english_pipeline.py','_hlm_rose_pipeline_predecessor')
    pipe.ROOT=root; pipe.SOURCE=history/'data/hongloumeng/first80-public'; pipe.DATA=history/D
    pipe.STANDARD=root/'docs/hongloumeng/translation'
    mapping=json.loads(before(root,D+'source-map.json')); progress=json.loads(before(root,D+'progress.json'))
    prior.validate_preparation(pipe,mapping,progress,reviewed=True)
    return pipe,mapping,progress,json.loads(before(root,D+'reader-notes.json')),prior


def validate_preparation(pipe,mapping,progress,*,reviewed=False):
    bound=binding(pipe.ROOT);c=bound['change']
    for path,row in bound['files'].items():
        require(sha(regular(pipe.ROOT,path))==row['afterSHA256'],'Current successor bytes differ: '+path)
    old,oldmap,oldprogress,oldnotes,_=predecessor(pipe.ROOT)
    expected=copy.deepcopy(old.load_source());block=expected['chapters'][43]['blocks'][23]
    require(block['text']==c['beforeUnitText'],'Prior source unit differs')
    require(c['afterUnitText']==block['text'].replace(c['before'],c['after']), 'Source replacement differs')
    block['text']=c['afterUnitText']
    require(pipe.load_source()==expected,'Source delta widened')
    public='data/hongloumeng/first80-public/'
    history=Path(pipe.ROOT)/HISTORY
    source_manifest=json.loads(regular(history,public+'manifest.json'))
    source_manifest['reading_sha256']=mapping['sourceHash'];source_manifest['body_sha256']=mapping['bodyHash']
    source_manifest['character_count']+=1
    cm=source_manifest['chapters'][43];cm['character_count']+=1
    cm['body_sha256']=sha(''.join(x['text'] for x in expected['chapters'][43]['blocks']))
    require(json.loads(regular(pipe.ROOT,public+'manifest.json'))==source_manifest,'Manifest delta widened')
    traditional=json.loads(regular(history,public+'reading.zh-hant.json'))
    tb=traditional['chapters'][43]['blocks'][23]
    require(tb['text'].count('如倒膏子一樣')==1,'Prior Traditional reading differs')
    tb['text']=tb['text'].replace('如倒膏子一樣','如玫瑰膏子一樣')
    require(json.loads(regular(pipe.ROOT,public+'reading.zh-hant.json'))==traditional,'Traditional delta widened')
    rules=json.loads(regular(history,public+'conversion.zh-hant.json'))
    rules['source_sha256']=mapping['sourceHash'];rules['source_manifest_sha256']=mapping['manifestHash']
    exceptions=[x for x in rules['exceptions'] if x['chapter']==44 and x['block']==23]
    require(len(exceptions)==1 and exceptions[0]['offset']==101 and exceptions[0]['source']=='干' and exceptions[0]['target']=='乾','Prior Traditional exception differs')
    exceptions[0]['offset']=102;exceptions[0]['unit_sha256']=sha(c['afterUnitText'])
    require(json.loads(regular(pipe.ROOT,public+'conversion.zh-hant.json'))==rules,'Conversion delta widened')
    import build_hongloumeng_first80_traditional as trad
    for name,text in trad.outputs(Path(pipe.ROOT)/public).items():
        require(regular(pipe.ROOT,public+name)==text.encode(),'Traditional regeneration differs')
    require(mapping==pipe.source_map(expected),'Current source map differs')
    expected_map=copy.deepcopy(oldmap)
    for k in ['sourceHash','manifestHash','bodyHash']:expected_map[k]=mapping[k]
    target_map=next(u for u in expected_map['units'] if u['id']==TARGET)
    target_map['sourceHash']=sha(c['afterUnitText']);target_map['characterCount']+=1
    require(mapping==expected_map,'Source map delta widened')
    snapshot=pipe.standard_snapshot()
    require(snapshot==old.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT,'Unchanged normative standard differs')
    expected=copy.deepcopy(oldprogress);expected['sourceHash']=mapping['sourceHash']
    unit=next(u for u in expected['units'] if u['id']==TARGET)
    unit['sourceHash']=sha(c['afterUnitText'])
    require(unit['segments'][0]['text'].count('looked like a poured ointment.')==1,'Prior English wording differs')
    unit['segments'][0]['text']=unit['segments'][0]['text'].replace('looked like a poured ointment.','looked like rose paste.')
    require(SEMANTIC_SHA256 and sha(regular(pipe.ROOT,SEMANTIC))==SEMANTIC_SHA256,'Independent semantic review pending')
    semantic=json.loads(regular(pipe.ROOT,SEMANTIC))
    require(semantic['status']=='PASS' and semantic['requiredFindings']==[] and semantic['fullCorpusReread'] is False,'Invalid semantic review')
    require(semantic['candidateSHA256']==sha(regular(pipe.ROOT,D+'rose-paste-semantic-candidate.json')),'Frozen semantic candidate differs')
    require(semantic['afterSourceText']==c['afterUnitText'] and semantic['segments']==unit['segments'],'Semantic review candidate differs')
    require(set(semantic['reviewTypes'])=={'bilingual','literary','consistency'},'Missing semantic review type')
    for rev in unit['reviews']:
        rev['contentHash']=pipe.content_hash(unit,expected['sourceIssues'])
        rev['reference']=REFERENCE+'; '+semantic['reference']+' (complete target unit reread; earlier receipt retained in predecessor)'
    for check in expected['checkpoints']:
        if check['first']==41:
            check['corpusHash']=pipe.batch_hash([u for s,u in zip(mapping['units'],expected['units']) if 41<=s['chapter']<=45],expected['sourceIssues'])
            check['reviewReference']+='; '+REFERENCE+' (single-unit reread; other units unchanged; no batch reread)'
    require(progress==expected,'English delta widened')
    notes=copy.deepcopy(oldnotes);notes['sourceHash']=mapping['sourceHash']
    require(json.loads(regular(pipe.ROOT,D+'reader-notes.json'))==notes,'Reader note delta widened')
    pipe.validate_progress(mapping,progress,snapshot);pipe.validate_reader_notes(mapping,notes)
    if reviewed:
        require(REVIEW_SHA256 and sha(regular(pipe.ROOT,REVIEW))==REVIEW_SHA256,'Independent rose-paste review pending')
        review=json.loads(regular(pipe.ROOT,REVIEW))
        require(review['bindingSHA256']==BINDING_SHA256 and review['fullCorpusReread'] is False and review['requiredFindings']==[] and review['status']=='PASS_BOUNDED_ROSE_PASTE','Invalid independent review')
    return snapshot


def validate_readiness(pipe,mapping,progress):
    return validate_preparation(pipe,mapping,progress,reviewed=True)


def apply_model(model,raw_source):
    from build_hongloumeng_first80 import author_change_spans,selection_source_chars,effective_author_changes
    c=binding()['change'];chapter=model['chapters'][43];block=chapter['blocks'][23]
    require(block['text']==c['beforeUnitText'],'Producer source unit differs')
    old,new=c['before'],c['after'];delta=len(new)-len(old)
    require(delta==1,'Unexpected rose-paste coordinate shift')
    require(not chapter['layout_ranges'] and not chapter['author_layout_ranges'],'Unexpected chapter44 layout ranges')
    require(raw_source.count(old)==1,'Producer original occurrence is not unique')
    start=raw_source.index(old);end=start+len(old);ident='PUBLIC-ROSE-PASTE-044'
    change=dict(id=ident,chapter=44,title='玫瑰膏子转写校正',status='adopted_editorial_choice',applied=True,mode='replace',source_start_char=start,source_end_char=end,original=old,proposed=new,context_before=raw_source[start-20:start],context_after=raw_source[end:end+20],reason='据本机所供正文与程甲本公开文本搜索摘录校正；未冒称核对影印。',authorization_type='delegated_public_transcription_selection',decision_file='rose-paste-binding.json',decision_sha256=BINDING_SHA256,public_references=[{'url':c['reference']}])
    chapter['body']=chapter['body'].replace(old,new);block['text']=c['afterUnitText'];block['author_change_ids'].append(ident)
    block['body_end']+=delta
    for row in chapter['blocks'][24:]:
        row['body_start']+=delta;row['body_end']+=delta
    chapter['author_changes'].append(change);model['author_emendations'].append(change)
    chapter['body_sha256']=sha(chapter['body']);chapter['author_change_spans']=author_change_spans(selection_source_chars(chapter,raw_source),effective_author_changes(chapter))
    for name in ('user_delegated_readability_selection','total_semantic_changes','current_active_semantic_changes','applied_occurrence_records','current_active_occurrence_records'):model['emendation_authority_counts'][name]+=1
    require(''.join(b['text'] for b in chapter['blocks'])==chapter['body'],'Producer block/body mismatch')
    for b in chapter['blocks']:
        require(chapter['body'][b['body_start']:b['body_end']]==b['text'],'Producer body coordinates differ')
    return model
