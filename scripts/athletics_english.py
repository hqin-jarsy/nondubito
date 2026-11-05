"""Render only explicitly approved complete English Athletics manuscripts.

The earlier five-language provenance receipt remains authoritative. Authorized
primary-page changes are appended to that receipt, never silently rebaselined.
This module has no ZIP dependency and does not confer editorial approval.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

from build_emperor_full_editions import replace_div
from build_worldcup_full_editions import render as markdown_html

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/athletics-english'
SERIES=ROOT/'essays/athletics'
STYLE='''<style id="athletics-english-style">
.essay-main{min-width:0;overflow-wrap:break-word}
.essay-main header.essay-header{position:static;display:block;height:auto;backdrop-filter:none}
.athletics-english h2{scroll-margin-top:100px;line-height:1.5}
.athletics-english p{overflow-wrap:break-word}
.athletics-english-toc{margin:0 0 2rem;padding:1rem 1.2rem;border:1px solid var(--cream-border)}
.athletics-english-toc summary{cursor:pointer;font-family:var(--sans);font-size:.85rem}
.athletics-english-toc li{margin:.5rem 0;line-height:1.65}
</style>'''


def sha(value):
    return hashlib.sha256(value if isinstance(value,bytes) else value.encode()).hexdigest()


def body_inner(text,language):
    marker=re.search(r'<div\b[^>]*class="essay-body lang-'+re.escape(language)+r'"[^>]*>',text)
    assert marker,language
    depth=1
    for tag in re.finditer(r'</?div\b[^>]*>',text[marker.end():]):
        depth+=-1 if tag[0].startswith('</') else 1
        if not depth:return text[marker.end():marker.end()+tag.start()]
    raise AssertionError('Unclosed reading body')


def section_counts(text):
    parts=re.split(r'^## (.+)\n',text,flags=re.M)
    assert len(parts)>1 and len(parts)%2==1
    return [len(re.split(r'\n\s*\n',s.strip())) for s in parts[2::2]]


def clean_received(text,title):
    """Keep every source prose paragraph; separate clearly marked editor notes."""
    assert '\n## ' in text
    first=text.index('\n## ')
    prose=text[first:].strip()
    notes=''
    marker=re.search(r'\n---\s*\n\s*### Translation|\n## References linked on the Chinese source page',prose)
    if marker:
        notes=prose[marker.start():].strip()
        prose=prose[:marker.start()].rstrip()
    # These callouts refer only to the explicitly separated translator notes.
    note_ids=re.findall(r'^\[(\d+)\]',notes,re.M)
    if note_ids:prose=re.sub(r'\[('+'|'.join(note_ids)+r')\]','',prose)
    return '# '+title+'\n\n'+prose+'\n',notes


def read_manuscript(ep):
    record=json.loads((DATA/'publication.json').read_text())['articles'][ep]
    text=(DATA/(ep+'.md')).read_text()
    assert sha(text)==record['published_sha256'],(ep,'unreviewed English change')
    assert record['publication_ready'] is True and not record['remaining']
    assert section_counts(text)==record['paragraphs_by_section']
    review_path=ROOT/record['review_report']
    assert sha(review_path.read_bytes())==record['review_report_sha256'],(ep,'review changed after approval')
    return record,text


def saved_value(edit,language=None):
    language=language or edit['language'];ep=edit['episode']
    field=edit.get('field','paragraph')
    if field=='deck':
        return json.loads((ROOT/'data/athletics-full/review.json').read_text())['manuscripts'][ep+'.'+language]['deck']
    if language=='zh-hant':
        text=(SERIES/'zh-hant-data'/(ep+'.js')).read_text()
        variants=json.loads(re.search(r'var variants = (\{.*?\});\s*\n\s*var originals',text,re.S)[1])
        return variants[edit['after']]
    if language=='zh':
        text=body_inner((SERIES/(ep+'.html')).read_text(),'zh')
        if field=='heading':return html.unescape(re.sub(r'<[^>]*>','',re.findall(r'<h2[^>]*>(.*?)</h2>',text,re.S)[edit['section']-1]))
        section=re.split(r'<h2[^>]*>.*?</h2>',text,flags=re.S)[edit['section']]
        return html.unescape(re.sub(r'<[^>]*>','',re.findall(r'<p[^>]*>(.*?)</p>',section,re.S)[edit['paragraph']-1]))
    path=DATA/(ep+'.md') if language=='en' else ROOT/'data/athletics-full'/(ep+'.'+language+'.md')
    if field=='heading':return re.split(r'^## (.+)\n',path.read_text(),flags=re.M)[edit['section']*2-1]
    section=re.split(r'^## (.+)\n',path.read_text(),flags=re.M)[edit['section']*2]
    return re.split(r'\n\s*\n',section.strip())[edit['paragraph']-1]


def validate_review(path):
    """Bind actual completed readings and saved-field checks, not prose quality."""
    review=json.loads(path.read_text())
    assert review['publication_ready'] is True and review['remaining']==[]
    for name,digest in review.get('additional_plans_sha256',{}).items():
        assert sha((ROOT/name).read_bytes())==digest
    for name,digest in review.get('surface_reading_report_sha256',{}).items():
        proof_path=ROOT/name
        assert sha(proof_path.read_bytes())==digest
        surface_proof=json.loads(proof_path.read_text());assert surface_proof['passed'] is True
        for f in surface_proof['fields']:
            assert sha(f['saved_field'])==f['saved_field_sha256']
            text=(ROOT/f['path']).read_text()
            if 'source_key' in f:
                variants=json.loads(re.search(r'var variants = (\{.*?\});\s*\n\s*var originals',text,re.S)[1])
                assert variants[f['source_key']]==f['saved_field']
            elif not f['saved_field'].startswith('<'):
                descriptions=[html.unescape(s) for s in re.findall(r'<p class="entry-desc">(.*?)</p>',text,re.S)]
                assert descriptions.count(html.unescape(f['saved_field']))==1,('Changed reviewed card',f['path'])
            else:assert text.count(f['saved_field'])==1,('Changed reviewed summary',f['path'])
    superseding={}
    for name,digest in review.get('supplementary_reviews',{}).items():
        assert sha((ROOT/name).read_bytes())==digest
        supplement=validate_review(ROOT/name)
        for e in json.loads((ROOT/supplement['copyedit_plan']).read_text())['edits']:
            key=tuple(e[k] for k in ('episode','language','section','paragraph'))
            assert key not in superseding
            superseding[key]=e
    for name,digest in review['full_reading_report_sha256'].items():
        assert sha((ROOT/name).read_bytes())==digest,('Changed original reading report',name)
    plan_path=ROOT/review['copyedit_plan'];raw=plan_path.read_bytes()
    assert sha(raw)==review['copyedit_plan_sha256']
    plan=json.loads(raw);fields={}
    for name,digest in review['saved_reading_report_sha256'].items():
        path=ROOT/name;assert sha(path.read_bytes())==digest,('Changed saved reading',name)
        proof=json.loads(path.read_text())
        if proof['passed'] is not True:
            resolution=review.get('resolved_saved_readings',{}).get(name)
            assert resolution,('Unresolved saved-reading finding',name)
            resolved_path=ROOT/resolution['resolution_report']
            assert sha(resolved_path.read_bytes())==resolution['resolution_sha256']
            final_reading=json.loads(resolved_path.read_text())
            assert final_reading['passed'] is True and final_reading['plan_sha256']==sha(raw)
        assert proof['plan_sha256']==sha(raw)
        for field in proof['fields']:
            key=tuple(field[k] for k in ('episode','language','section','paragraph'))
            digest=field.get('saved_field_sha256',field.get('saved_sha256'))
            assert digest
            fields.setdefault(key,[]).append(digest)
    polishes={tuple(e[k] for k in ('episode','language','section','paragraph')):e for e in review.get('final_polish',[])}
    for e in plan['edits']:
        key=tuple(e[k] for k in ('episode','language','section','paragraph'))
        polish=polishes.get(key)
        if polish:assert polish['before']==e['after']
        if key in superseding:
            later=superseding[key]
            assert later['before']==(polish['after'] if polish else e['after'])
            assert sha(later['before']) in fields.get(key,[])
            if e['language']=='zh':assert fields.get((e['episode'],'zh-hant',e['section'],e['paragraph']))
            continue
        assert saved_value(e)==(polish['after'] if polish else e['after']),('Unapplied source correction',e['issue'],e['language'])
        for language in [e['language'],*(['zh-hant'] if e['language']=='zh' else [])]:
            key=(e['episode'],language,e['section'],e['paragraph'])
            assert sha(saved_value(e,language)) in fields.get(key,[]),('Missing actual full saved-field reading',key)
    return review


def render_primary(ep,text,record,manuscript):
    parts=re.split(r'^## (.+)\n',manuscript,flags=re.M)
    headings=parts[1::2]
    blocks=[]
    for i,(heading,prose) in enumerate(zip(headings,parts[2::2]),1):
        rendered=markdown_html(prose.strip())
        assert rendered.count('<p>')==record['paragraphs_by_section'][i-1],(ep,i)
        blocks.append('<section><h2 id="en-section-'+str(i)+'">'+html.escape(heading)+'</h2>\n'+rendered+'\n</section>')
    toc='<details class="athletics-english-toc"><summary>In this essay</summary><ol>'+''.join('<li><a href="#en-section-'+str(i)+'">'+html.escape(h)+'</a></li>' for i,h in enumerate(headings,1))+'</ol></details>'
    content=toc+'\n<div class="athletics-english">\n'+'\n'.join(blocks)+'\n</div>'
    text=replace_div(text,'essay-body lang-en',content)
    text=re.sub(r'<style id="athletics-english-style">.*?</style>\s*','',text,flags=re.S)
    for src in ('athletics-language.js','../../language-select.js'):
        text=re.sub(r'<script defer src="'+re.escape(src)+r'"></script>\s*','',text)
    text=text.replace('</head>',STYLE+'\n<script defer src="athletics-language.js"></script>\n<script defer src="../../language-select.js"></script>\n</head>',1)
    return text


def outputs():
    if not (DATA/'publication.json').exists():return {}
    publication=json.loads((DATA/'publication.json').read_text())
    out={};validated=set()
    for ep in publication['articles']:
        record,md=read_manuscript(ep)
        if record['review_report'] not in validated:
            validate_review(ROOT/record['review_report'])
            validated.add(record['review_report'])
        path=SERIES/(ep+'.html')
        source=path.read_text()
        assert sha(body_inner(source,'zh'))==record['final_chinese_body_sha256'],(ep,'Chinese changed after English review')
        out[path]=render_primary(ep,source,record,md)
    return out


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    for path,text in outputs().items():
        if args.check:assert path.read_text()==text,('Stale complete English',path)
        else:path.write_text(text)
    print('Complete Athletics English '+('checked' if args.check else 'rendered')+' for '+str(len(outputs()))+' approved articles')
