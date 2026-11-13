"""Two public-edition-supported corrections, over the preserved author choice.

Only changed files have predecessor copies. Explicit module-local readers replay
old contracts; no global reader, existing historical archive or receipt changes.
English and Japanese wording already represented the supported readings.
"""
import copy
import json
from pathlib import Path
from hongloumeng_ch005_author_binding import sha, encoded, require, regular, load_module
ROOT = Path(__file__).resolve().parents[1]
D = 'data/hongloumeng/first80-english/'
HISTORY = D + 'history/two-readings-before'
BINDING = D + 'two-readings-binding.json'
BINDING_SHA256 = 'cef40a7df51ee94448408d8e0410fdb0117cc7d31e3f7418ffc4e24c8570ebf9'
REVIEW = D + 'two-readings-current-review.json'
REVIEW_SHA256 = 'fd2458fc57f051e165260fa547ce0124e89a8c8e2110be253e8fd0a205f04a30'
REFERENCE = 'TWO-READINGS-20261112'


def binding(root=ROOT):
    raw = regular(root, BINDING)
    require(BINDING_SHA256 and sha(raw) == BINDING_SHA256, 'Unpinned two-reading binding')
    value = json.loads(raw)
    require([(c['chapter'], c['blockIndex'], c['before'], c['after']) for c in value['changes']] ==
            [(5,131,'锈帐鸳衾','绣帐鸳衾'),(12,2,'只因素人闻得人说','只因素日闻得人说')], 'Correction scope changed')
    return value


def predecessor(root=ROOT):
    root = Path(root); bound = binding(root); history = root/HISTORY
    def before(context, path):
        if Path(context).resolve() == root.resolve() and path in bound['files']:
            row = bound['files'][path]
            require(sha(regular(root,path)) == row['afterSHA256'], 'Current successor bytes differ: '+path)
            raw = regular(history,path)
            require(sha(raw) == row['beforeSHA256'], 'Predecessor archive differs: '+path)
            return raw
        return regular(context,path)
    old = load_module(root/'scripts/hongloumeng_ch005_author_binding.py','_hlm_two_readings_author_predecessor')
    old.regular = before
    pipe = load_module(history/'scripts/hongloumeng_english_pipeline.py','_hlm_two_readings_pipeline_predecessor')
    pipe.ROOT=root;pipe.SOURCE=history/'data/hongloumeng/first80-public';pipe.DATA=history/D
    pipe.STANDARD=root/'docs/hongloumeng/translation'
    mapping=json.loads(before(root,D+'source-map.json')); progress=json.loads(before(root,D+'progress.json'))
    old.validate_preparation(pipe,mapping,progress,reviewed=True)
    return pipe,mapping,progress,json.loads(before(root,D+'reader-notes.json'))


def validate_preparation(pipe,mapping,progress,*,reviewed=False):
    bound=binding(pipe.ROOT)
    for path,row in bound['files'].items():
        require(sha(regular(pipe.ROOT,path))==row['afterSHA256'],'Current successor bytes differ: '+path)
    old,oldmap,oldprogress,oldnotes=predecessor(pipe.ROOT)
    expected=copy.deepcopy(old.load_source())
    for c in bound['changes']:
        b=expected['chapters'][c['chapter']-1]['blocks'][c['blockIndex']]
        require(b['text']==c['beforeUnitText'],'Prior source unit differs')
        require(c['afterUnitText']==b['text'].replace(c['before'],c['after']), 'Source replacement differs')
        b['text']=c['afterUnitText']
    require(pipe.load_source()==expected,'Source delta widened')
    require(mapping==pipe.source_map(expected),'Current source map differs')
    expected_map=copy.deepcopy(oldmap)
    for k in ['sourceHash','manifestHash','bodyHash']:expected_map[k]=mapping[k]
    for c in bound['changes']:next(u for u in expected_map['units'] if u['id']==c['unitId'])['sourceHash']=sha(c['afterUnitText'])
    require(mapping==expected_map,'Source map delta widened')
    snapshot=pipe.standard_snapshot()
    require(snapshot==old.standard_snapshot()==pipe.EXPECTED_NORMATIVE_SNAPSHOT,'Unchanged normative standard differs')
    expected=copy.deepcopy(oldprogress);expected['sourceHash']=mapping['sourceHash']
    for c in bound['changes']:
        u=next(u for u in expected['units'] if u['id']==c['unitId']);u['sourceHash']=sha(c['afterUnitText'])
        for rev in u['reviews']:
            rev['contentHash']=pipe.content_hash(u,expected['sourceIssues'])
            rev['reference']+='; '+REFERENCE+' (source-only correction; English unchanged)'
    for check in expected['checkpoints']:
        if check['first'] in [1,11]:
            check['corpusHash']=pipe.batch_hash([u for s,u in zip(mapping['units'],expected['units']) if check['first']<=s['chapter']<=check['last']],expected['sourceIssues'])
            check['reviewReference']+='; '+REFERENCE+' (two source-only corrections; no corpus reread)'
    require(progress==expected,'English delta widened')
    notes=copy.deepcopy(oldnotes);notes['sourceHash']=mapping['sourceHash']
    require(json.loads(regular(pipe.ROOT,D+'reader-notes.json'))==notes,'Reader note delta widened')
    pipe.validate_progress(mapping,progress,snapshot);pipe.validate_reader_notes(mapping,notes)
    if reviewed:
        require(REVIEW_SHA256 and sha(regular(pipe.ROOT,REVIEW))==REVIEW_SHA256,'Independent two-reading review pending')
        review=json.loads(regular(pipe.ROOT,REVIEW))
        require(review['bindingSHA256']==BINDING_SHA256 and review['fullCorpusReread'] is False and review['requiredFindings']==[] and review['status']=='PASS_BOUNDED_TWO_READINGS','Invalid independent review')
    return snapshot


def validate_readiness(pipe,mapping,progress):
    return validate_preparation(pipe,mapping,progress,reviewed=True)


def apply_model(model,raw_source):
    """Producer layer: two equal-length corrections, with distinct authority."""
    from build_hongloumeng_first80 import author_change_spans,selection_source_chars,effective_author_changes
    for c in binding()['changes']:
        chapter=model['chapters'][c['chapter']-1];block=chapter['blocks'][c['blockIndex']]
        require(block['text']==c['beforeUnitText'],'Producer source unit differs')
        old,new=c['before'],c['after'];require(len(old)==len(new),'Unexpected coordinate shift')
        require(raw_source.count(old)==1,"Producer original occurrence is not unique")
        start=raw_source.index(old);end=start+len(old);ident=f"PUBLIC-TWO-{c['chapter']:03}"
        change=dict(id=ident,chapter=c['chapter'],title='通行本支持的转写校正',status='adopted_editorial_choice',applied=True,mode='replace',source_start_char=start,source_end_char=end,original=old,proposed=new,context_before=raw_source[start-20:start],context_after=raw_source[end:end+20],reason='据程甲本等公开文本校正转写。旧疑字记录仅留作历史，不是作者保留裁决。',authorization_type='delegated_public_transcription_selection',decision_file='two-readings-binding.json',decision_sha256=BINDING_SHA256,public_references=[{'url':c['reference']}])
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
