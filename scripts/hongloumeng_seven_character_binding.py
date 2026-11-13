"""One bounded seven-character correction over authenticated predecessors.

Only module-local readers replay frozen earlier editions. The equal-length
producer correction preserves counts and every source/body coordinate.
"""
import copy
import json
from pathlib import Path
from hongloumeng_ch005_author_binding import sha, require, regular, load_module
ROOT = Path(__file__).resolve().parents[1]
D = 'data/hongloumeng/first80-english/'
HISTORY = D + 'history/seven-character-before'
BINDING = D + 'seven-character-binding.json'
BINDING_SHA256 = '45e599765c08229059710ee573d9f58f88812b19cdaeaa02afd3aa711f4d99a4'
REVIEW = D + 'seven-character-current-review.json'
REVIEW_SHA256 = '3c605a6a81e2e09c400deb9842c1ee23086e2b0c7cf1151449ef80061cf46e2d'
SEMANTIC = D + 'seven-character-semantic-review.json'
SEMANTIC_SHA256 = 'f1f1e6d846afad904290cf2866add68dd7618898f0f6f069b9046765aac6694d'
TARGET = 'hlm-c049-b0033'
REFERENCE = 'SEVEN-CHARACTER-CH049-INDEPENDENT-20261113'


def binding(root=ROOT):
    raw = regular(root, BINDING)
    require(BINDING_SHA256 and sha(raw) == BINDING_SHA256, 'Unpinned seven-character binding')
    value = json.loads(raw)
    for path,checksum in value['preservedDependencies'].items():
        require(sha(regular(root,path))==checksum,'Preserved predecessor dependency differs: '+path)
    c = value['change']
    require((c['chapter'],c['blockIndex'],c['unitId'],c['before'],c['after']) ==
            (49,32,TARGET,'这五个字','这七个字'), 'Correction scope changed')
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
    prior = load_module(root/'scripts/hongloumeng_rose_paste_binding.py','_hlm_seven_rose_predecessor')
    prior.regular = before
    pipe = load_module(history/'scripts/hongloumeng_english_pipeline.py','_hlm_rose_pipeline_predecessor')
    pipe.ROOT=root; pipe.SOURCE=history/'data/hongloumeng/first80-public'; pipe.DATA=history/D
    pipe.STANDARD=root/'docs/hongloumeng/translation'
    mapping=json.loads(before(root,D+'source-map.json')); progress=json.loads(before(root,D+'progress.json'))
    # Replay the original rose contract against its frozen Traditional builder.
    import sys
    from unittest.mock import patch
    trad = load_module(history/'scripts/build_hongloumeng_first80_traditional.py','_hlm_seven_prior_traditional')
    trad.DATA=history/'data/hongloumeng/first80-public'
    outputs=trad.outputs
    trad.outputs=lambda data=trad.DATA: outputs(trad.DATA if Path(data)==root/'data/hongloumeng/first80-public' else data)
    with patch.dict(sys.modules, {'build_hongloumeng_first80_traditional':trad}):
        prior.validate_preparation(pipe,mapping,progress,reviewed=True)
    return pipe,mapping,progress,json.loads(before(root,D+'reader-notes.json')),prior


def validate_preparation(pipe,mapping,progress,*,reviewed=False):
    bound=binding(pipe.ROOT);c=bound['change']
    for path,row in bound['files'].items():
        require(sha(regular(pipe.ROOT,path))==row['afterSHA256'],'Current successor bytes differ: '+path)
    old,oldmap,oldprogress,oldnotes,_=predecessor(pipe.ROOT)
    expected=copy.deepcopy(old.load_source());block=expected['chapters'][48]['blocks'][32]
    require(block['text']==c['beforeUnitText'],'Prior source unit differs')
    require(c['afterUnitText']==block['text'].replace(c['before'],c['after']), 'Source replacement differs')
    block['text']=c['afterUnitText']
    require(pipe.load_source()==expected,'Source delta widened')
    public='data/hongloumeng/first80-public/'
    history=Path(pipe.ROOT)/HISTORY
    source_manifest=json.loads(regular(history,public+'manifest.json'))
    source_manifest['reading_sha256']=mapping['sourceHash'];source_manifest['body_sha256']=mapping['bodyHash']
    require(len(c['beforeUnitText'])==len(c['afterUnitText'])==254,'Character count changed')
    cm=source_manifest['chapters'][48]
    cm['body_sha256']=sha(''.join(x['text'] for x in expected['chapters'][48]['blocks']))
    require(json.loads(regular(pipe.ROOT,public+'manifest.json'))==source_manifest,'Manifest delta widened')
    traditional=json.loads(regular(history,public+'reading.zh-hant.json'))
    tb=traditional['chapters'][48]['blocks'][32]
    require(tb['text'].count('這五個字')==1,'Prior Traditional reading differs')
    tb['text']=tb['text'].replace('這五個字','這七個字')
    require(json.loads(regular(pipe.ROOT,public+'reading.zh-hant.json'))==traditional,'Traditional delta widened')
    rules=json.loads(regular(history,public+'conversion.zh-hant.json'))
    rules['source_sha256']=mapping['sourceHash'];rules['source_manifest_sha256']=mapping['manifestHash']
    require(not [x for x in rules['exceptions'] if x['chapter']==49 and x['block']==32], 'Unexpected target Traditional exception')
    require(json.loads(regular(pipe.ROOT,public+'conversion.zh-hant.json'))==rules,'Conversion delta widened')
    import build_hongloumeng_first80_traditional as trad
    for name,text in trad.outputs(Path(pipe.ROOT)/public).items():
        require(regular(pipe.ROOT,public+name)==text.encode(),'Traditional regeneration differs')
    require(mapping==pipe.source_map(expected),'Current source map differs')
    expected_map=copy.deepcopy(oldmap)
    for k in ['sourceHash','manifestHash','bodyHash']:expected_map[k]=mapping[k]
    target_map=next(u for u in expected_map['units'] if u['id']==TARGET)
    target_map['sourceHash']=sha(c['afterUnitText'])
    require(mapping==expected_map,'Source map delta widened')
    snapshot=pipe.standard_snapshot()
    require(snapshot==old.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT,'Unchanged normative standard differs')
    expected=copy.deepcopy(oldprogress);expected['sourceHash']=mapping['sourceHash']
    unit=next(u for u in expected['units'] if u['id']==TARGET)
    unit['sourceHash']=sha(c['afterUnitText'])
    require(unit['segments'][0]['text'].count('Those five characters')==1,'Prior English wording differs')
    unit['segments'][0]['text']=unit['segments'][0]['text'].replace('Those five characters','Those seven characters')
    require(SEMANTIC_SHA256 and sha(regular(pipe.ROOT,SEMANTIC))==SEMANTIC_SHA256,'Independent semantic review pending')
    semantic=json.loads(regular(pipe.ROOT,SEMANTIC))
    require(semantic['status']=='PASS' and semantic['requiredFindings']==[] and semantic['fullCorpusReread'] is False,'Invalid semantic review')
    require(semantic['candidateSHA256']==sha(regular(pipe.ROOT,D+'seven-character-semantic-candidate.json')),'Frozen semantic candidate differs')
    require(semantic['afterSourceText']==c['afterUnitText'] and semantic['segments']==unit['segments'],'Semantic review candidate differs')
    require(set(semantic['reviewTypes'])=={'bilingual','literary','consistency'},'Missing semantic review type')
    require(semantic['readerNote']==json.loads(regular(pipe.ROOT,D+'seven-character-semantic-candidate.json'))['candidateReaderNote'],'Semantic reader note differs')
    for rev in unit['reviews']:
        rev['contentHash']=pipe.content_hash(unit,expected['sourceIssues'])
        rev['reference']=REFERENCE+'; '+semantic['reference']+' (complete target unit reread; earlier receipt retained in predecessor)'
    for check in expected['checkpoints']:
        if check['first']==46:
            check['corpusHash']=pipe.batch_hash([u for s,u in zip(mapping['units'],expected['units']) if 46<=s['chapter']<=50],expected['sourceIssues'])
            check['reviewReference']+='; '+REFERENCE+' (single-unit reread; other units unchanged; no batch reread)'
    require(progress==expected,'English delta widened')
    notes=copy.deepcopy(oldnotes);notes['sourceHash']=mapping['sourceHash']
    note=next(n for n in notes['notes'] if n['unitId']==TARGET)
    note['sourceHash']=sha(c['afterUnitText'])
    require(note['text'].count(', although the source calls them five')==1,'Prior note clause differs')
    note['text']=note['text'].replace(', although the source calls them five','')
    require(note==semantic['readerNote'],'Reviewed note differs')
    require(json.loads(regular(pipe.ROOT,D+'reader-notes.json'))==notes,'Reader note delta widened')
    validate_html(pipe.ROOT)
    pipe.validate_progress(mapping,progress,snapshot);pipe.validate_reader_notes(mapping,notes)
    if reviewed:
        require(REVIEW_SHA256 and sha(regular(pipe.ROOT,REVIEW))==REVIEW_SHA256,'Independent seven-character review pending')
        review=json.loads(regular(pipe.ROOT,REVIEW))
        require(review['bindingSHA256']==BINDING_SHA256 and review['fullCorpusReread'] is False and review['requiredFindings']==[] and review['status']=='PASS_BOUNDED_SEVEN_CHARACTER','Invalid independent review')
    return snapshot


def validate_readiness(pipe,mapping,progress):
    return validate_preparation(pipe,mapping,progress,reviewed=True)


def apply_model(model,raw_source):
    """Producer layer: one equal-length correction, with distinct authority."""
    from build_hongloumeng_first80 import author_change_spans,selection_source_chars,effective_author_changes
    for c in [binding()['change']]:
        chapter=model['chapters'][c['chapter']-1];block=chapter['blocks'][c['blockIndex']]
        require(block['text']==c['beforeUnitText'],'Producer source unit differs')
        old,new=c['before'],c['after'];require(len(old)==len(new),'Unexpected coordinate shift')
        require(raw_source.count(old)==1,"Producer original occurrence is not unique")
        start=raw_source.index(old);end=start+len(old);ident='PUBLIC-SEVEN-CHARACTER-049'
        change=dict(id=ident,chapter=c['chapter'],title='通行本支持的转写校正',status='adopted_editorial_choice',applied=True,mode='replace',source_start_char=start,source_end_char=end,original=old,proposed=new,context_before=raw_source[start-20:start],context_after=raw_source[end:end+20],reason='据虚阁第四十九回公开正文及其他通行文本校正字数；未声称影印核验。',authorization_type='delegated_public_transcription_selection',decision_file='seven-character-binding.json',decision_sha256=BINDING_SHA256,public_references=[{'url':c['reference']}])
        chapter['body']=chapter['body'].replace(old,new);block['text']=c['afterUnitText'];block['author_change_ids'].append(ident)
        for row in chapter['layout_ranges']+chapter['author_layout_ranges']:
            if 'exact_body_text' in row:row['exact_body_text']=row['exact_body_text'].replace(old,new)
        chapter['author_changes'].append(change);model['author_emendations'].append(change)
        chapter['body_sha256']=sha(chapter['body']);chapter['author_change_spans']=author_change_spans(selection_source_chars(chapter,raw_source),effective_author_changes(chapter))
        for name in ('user_delegated_readability_selection','total_semantic_changes','current_active_semantic_changes','applied_occurrence_records','current_active_occurrence_records'):model['emendation_authority_counts'][name]+=1
        for issue in chapter['issues']:
            if old in issue.get('text',''):
                issue['resolution_note']='此处已据公开通行本作转写校正；原摘录仅为历史，不再描述当前正文。'
        require(''.join(b['text'] for b in chapter['blocks'])==chapter['body'],'Producer block/body mismatch')
    return model


def note_record(record,note,source,unit,root=ROOT):
    """Exact bounded overlay; the normative placement record stays frozen."""
    bound=binding(root)
    require(record==bound['beforeReaderNoteRecord'],'Frozen reader-note placement differs')
    candidate=json.loads(regular(root,D+'seven-character-semantic-candidate.json'))
    require(note==candidate['candidateReaderNote'],'Bounded reader note differs')
    require(unit['id']==TARGET and unit['sourceHash']==candidate['candidateUnit']['sourceHash'] and unit['segments']==candidate['candidateUnit']['segments'],'Bounded reader-note unit differs')
    require(source['id']==TARGET and source['sourceHash']==unit['sourceHash'],'Bounded reader-note source differs')
    before=candidate['beforeUnit']['segments'][0]['text'];after=unit['segments'][0]['text']
    require(after==before.replace('Those five characters','Those seven characters') and len(after)==len(before)+1,'Bounded English anchor shift differs')
    result=copy.deepcopy(record);anchor=result['anchor']
    require(before[anchor['start']:anchor['end']]==anchor['text'],'Prior reader-note anchor differs')
    result['text']=note['text'];result['textSHA256']=sha(note['text']);anchor['sourceHash']=unit['sourceHash']
    anchor['start']+=1;anchor['end']+=1
    require(after[anchor['start']:anchor['end']]==anchor['text'],'Current reader-note anchor differs')
    return result


def validate_html(root=ROOT):
    pairs={
      'classics/hongloumeng/ch049.html':[('这五个字','这七个字')],
      'classics/hongloumeng/zh-hant/ch049.html':[('這五個字','這七個字')],
      'classics/hongloumeng/en/ch049.html':[('Those five characters','Those seven characters'),(', although the source calls them five','')],
    }
    for path,replacements in pairs.items():
        expected=regular(Path(root)/HISTORY,path).decode()
        for before,after in replacements:
            require(expected.count(before)==1,'Prior HTML occurrence differs')
            expected=expected.replace(before,after)
        require(regular(root,path)==expected.encode(),'HTML delta widened: '+path)
