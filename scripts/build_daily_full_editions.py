#!/usr/bin/env python3
"""Publish explicitly reviewed daily-life batches at their existing URLs.

The primary page retains its English/Simplified/Traditional switch; the other
five languages retain their existing standalone URLs. Canonical complete prose
and precise review receipts live in data/daily-full. ZIPs are needed only for
an explicit additive import, never for an ordinary rebuild. No translation
service or supplier executable is used.
"""
from __future__ import annotations
import argparse,hashlib,html,json,re,subprocess
from pathlib import Path
from zipfile import ZipFile
from html.parser import HTMLParser
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/daily-full'
LANGS=('zh','hant','en','de','fr','es','ja','ko')
FOREIGN=('en','de','fr','es','ja','ko')
GROUPS=('work','parenting','conflict')
SERIES_EN={'work':'The Structure of Work','parenting':'The Structure of Parenting','conflict':'The Structure of Conflict'}

def digest(value):return hashlib.sha256(value if isinstance(value,bytes) else value.encode()).hexdigest()
def serialized(value):return json.dumps(value,ensure_ascii=False,indent=2)+'\n'
def plain(value):return html.unescape(re.sub(r'<[^>]+>','',value)).strip()
def paragraph(value):return '<p>'+html.escape(value,quote=False)+'</p>'
def clean_title(value):return re.sub(r'^\d{1,2}[.．、]\s*','',value).strip()

def source_slug(url,group,episode):
    """A Chinese-view query is provenance, never part of a local filename."""
    parsed=urlsplit(url);slug=parsed.path.rsplit('/',1)[-1]
    assert group in GROUPS and 1<=episode<=30
    assert parsed.scheme=='https' and parsed.netloc=='nondubito.net',('Unexpected source host',url)
    assert parsed.path==f'/essays/everyday/{group}/{slug}'
    assert parsed.query in ('','lang=zh') and not parsed.fragment,('Unexpected source view',url)
    assert re.fullmatch(f'{episode:02d}-[a-z0-9-]+\\.html',slug),('Unexpected source route',episode,url)
    return slug

def div_span(text,cls):
    start=None
    for candidate in re.finditer(r'<div\b[^>]*>',text):
        classes=re.search(r'\bclass="([^"]*)"',candidate[0])
        if classes and cls in classes[1].split():
            start=candidate;break
    assert start,('Missing div',cls)
    depth=1
    for tag in re.finditer(r'</?div\b[^>]*>',text[start.end():]):
        depth+=-1 if tag[0].startswith('</') else 1
        if not depth:
            close=start.end()+tag.start()
            return start.start(),start.end(),close,start.end()+tag.end()
    raise AssertionError(('Unclosed div',cls))

def within(text,cls,fn):
    a,b,c,d=div_span(text,cls)
    return text[:b]+fn(text[b:c])+text[c:]

def body_paragraphs(text,lang=None):
    if lang:text=text[slice(*div_span(text,'lang-'+lang)[1:3])]
    _,a,b,_=div_span(text,'article-body');body=text[a:b]
    ps=re.findall(r'<p\b[^>]*>(.*?)</p>',body,re.S)
    rest=re.sub(r'<p\b[^>]*>.*?</p>','',body,flags=re.S)
    assert not rest.strip(),('Unexpected non-paragraph body',rest[:100])
    return [plain(p) for p in ps]

def load_archive(path,group):
    """Normalize the three supplier schemas, checking every editable paragraph."""
    with ZipFile(path) as z:
        assert z.testzip() is None
        files={n.split('/',1)[1]:z.read(n) for n in z.namelist() if '/' in n and not n.endswith('/') and not n.startswith('__MACOSX/')}
    result={}
    for n,raw in files.items():
        if not re.fullmatch(r'batches/[^/]+/alignment/'+group+r'-\d{2}\.en\.json',n):continue
        source=json.loads(raw);ep=source['number'];slug=source_slug(source['url'],group,ep)
        assert ep not in result,('Duplicate source route',ep,slug)
        snapshot=files[next(k for k in files if '/sources/' in k and k.endswith(f'/{group}-{ep:02}.html'))].decode()
        assert body_paragraphs(snapshot,'zh')==source['zh']
        result[ep]=dict(slug=slug,source_url=source['url'],languages={})
        for lang in LANGS:
            suffix='zh-hant' if lang=='hant' else lang
            md_raw=files[f'essays/{group}-{ep:02}.{suffix}.md'];md=md_raw.decode('utf-8-sig')
            title=clean_title(md.splitlines()[0].removeprefix('# '))
            if lang in ('zh','hant'):ps=body_paragraphs(snapshot,lang)
            else:
                aligned=json.loads(files[n[:-len('en.json')]+lang+'.json'])
                if lang in aligned:ps=aligned[lang]
                else:
                    rows=aligned.get('paragraphs',aligned.get('rows'))
                    assert [r.get('zh',r.get('source')) for r in rows]==source['zh']
                    ps=[r.get(lang,r.get('translation')) for r in rows]
            assert len(ps)==len(source['zh']) and all(isinstance(p,str) and p.strip() and '\ufffd' not in p for p in ps)
            position=0
            for p in ps:
                at=md.find(p,position);assert at>=0,('Missing or reordered editable paragraph',group,ep,lang,p[:60]);position=at+len(p)
            result[ep]['languages'][lang]=dict(title=title,paragraphs=ps,received_md_sha256=digest(md_raw))
    assert set(result)==set(range(1,31))
    return result

def page_path(group,slug,lang):
    base=ROOT/'essays/everyday'/group
    return base/slug if lang in ('en','zh','hant') else base/lang/slug

def import_batch(folder,plan_path,report_paths):
    plan=json.loads(plan_path.read_text());group=plan['series'];episodes=plan['episodes']
    assert group in GROUPS and len(episodes)==5 and episodes==list(range(episodes[0],episodes[0]+5))
    assert 1<=episodes[0]<=26 and (episodes[0]-1)%5==0
    assert len(report_paths)==3
    reviews=[json.loads(p.read_text()) for p in report_paths]
    assert sorted(l for r in reviews for l in r['languages'])==sorted(FOREIGN)
    for r in reviews:
        assert r['series']==group and r['episodes']==episodes and r['review_scope']
        assert not r.get('source_suggestions'), 'Resolve source suggestions before importing'
        assert r['archive_sha256']==plan['archive_sha256']
        for e in r['edits']:
            assert e['episode'] in episodes and e['lang'] in r['languages'] and isinstance(e['paragraph'],int) and e['paragraph']>=1
        for e in r.get('metadata',[]):
            assert e['episode'] in episodes and e['lang'] in r['languages'] and clean_title(e['title'])
    archive=folder/plan['archive'];assert digest(archive.read_bytes())==plan['archive_sha256']
    incoming=load_archive(archive,group)
    root_edits=plan.get('edits',[]);edits=[]
    # Source corrections are authored in both Chinese scripts and English;
    # no context-insensitive script conversion is silently accepted.
    for e in root_edits:
        assert e['episode'] in episodes and isinstance(e['paragraph'],int) and e['paragraph']>=1
        for lang in ('zh','hant','en'):
            edits.append(dict(episode=e['episode'],lang=lang,paragraph=e['paragraph'],after=e[lang],reason=e['reason']))
    for r in reviews:edits.extend(r['edits'])
    keys=[(e['episode'],e['lang'],e['paragraph']) for e in edits]
    assert len(set(keys))==len(keys),'Duplicate review coordinate'
    for e in root_edits:
        assert {(e['episode'],l,e['paragraph']) for l in LANGS}<=set(keys),'Unsynchronized source correction'
    prepared={};baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for ep in episodes:
        path=DATA/group/f'{ep:02}.json';assert not path.exists(),('Refusing to overwrite reviewed edition',path)
        record=incoming[ep];record.update(series=group,episode=ep,archive=archive.name,archive_sha256=plan['archive_sha256'],baseline_commit=baseline,edits=[],review=dict(date=plan['date'],scope=plan['review_scope'],source_plan=plan_path.name,source_plan_sha256=digest(plan_path.read_bytes()),reports={p.name:digest(p.read_bytes()) for p in report_paths}))
        for lang,edition in record['languages'].items():
            page=page_path(group,record['slug'],lang).read_text()
            before=body_paragraphs(page,lang if lang in ('zh','hant','en') else None)
            if lang in ('zh','hant'):assert before==edition['paragraphs'],('Chinese source drift',group,ep,lang)
            edition['original_paragraphs']=before
            region=page[slice(*div_span(page,'lang-'+lang)[1:3])] if lang in ('zh','hant','en') else page
            edition['original_title']=plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',region,re.S)[1])
            for r in reviews:
                for meta in r.get('metadata',[]):
                    if (meta['episode'],meta['lang'])==(ep,lang):edition['title']=clean_title(meta['title'])
            for e in [e for e in edits if e['episode']==ep and e['lang']==lang]:
                at=e['paragraph']-1;old=edition['paragraphs'][at]
                assert 'before' not in e or e['before']==old,('Stale paragraph edit',e)
                assert e['after'].strip() and '\n' not in e['after']
                edition['paragraphs'][at]=e['after'];record['edits'].append(dict(e,before=old))
        prepared[path]=record
    audit=DATA/'batches';audit.mkdir(parents=True,exist_ok=True)
    for path in [plan_path,*report_paths]:
        target=audit/path.name;assert not target.exists(),target;target.write_bytes(path.read_bytes())
    for path,record in prepared.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_text(serialized(record))
    print(f'Imported {group} {episodes[0]:02}–{episodes[-1]:02}: five complete essays × eight languages')

def records():
    result={}
    for group in GROUPS:
        for path in sorted((DATA/group).glob('[0-9][0-9].json')):
            record=json.loads(path.read_text());assert set(record['languages'])==set(LANGS)
            counts={len(e['paragraphs']) for e in record['languages'].values()};assert len(counts)==1
            result[group,record['slug']]=record
    return result

def replace_body(region,edition,native_chinese=False):
    actual=body_paragraphs(region);desired=edition['paragraphs'];original=edition['original_paragraphs']
    if native_chinese:
        assert len(actual)==len(desired)==len(original)
        assert all(a in (b,c) for a,b,c in zip(actual,desired,original)),'Unreviewed Chinese prose change'
        def change(body):
            nodes=list(re.finditer(r'<p\b[^>]*>(.*?)</p>',body,re.S))
            for node,before,after in reversed(list(zip(nodes,actual,desired))):
                if before!=after:body=body[:node.start()]+paragraph(after)+body[node.end():]
            return body
        return within(region,'article-body',change)
    assert actual in (original,desired),'Unreviewed foreign prose change'
    region=within(region,'article-body',lambda body:'\n'+'\n'.join(paragraph(p) for p in desired)+'\n')
    node=re.search(r'(<h1\b[^>]*>)(.*?)(</h1>)',region,re.S)
    assert node and plain(node[2]) in (edition['original_title'],edition['title']),'Unreviewed title change'
    return region[:node.start(2)]+html.escape(edition['title'])+region[node.end(2):]

def update_article(text,record,lang):
    if lang=='primary':
        for l in ('en','zh','hant'):
            text=within(text,'lang-'+l,lambda region,l=l:replace_body(region,record['languages'][l],l!='en'))
        title=record['languages']['en']['title']+' · '+SERIES_EN[record['series']]+' — Non Dubito'
    else:
        text=replace_body(text,record['languages'][lang]);title=record['languages'][lang]['title']+' — Non Dubito'
    text=re.sub(r'<title>.*?</title>',lambda m:'<title>'+html.escape(title)+'</title>',text,count=1,flags=re.S)
    text=re.sub(r'(<meta property="og:title" content=")[^"]*(")',lambda m:m[1]+html.escape(title,quote=True)+m[2],text)
    return text

def update_links(text,editions,lang):
    def anchor(match):
        node=match[0];target=re.search(r'href="([^"/?#]+\.html)"',node)
        if not target or target[1] not in editions:return node
        title=html.escape(editions[target[1]]['languages'][lang]['title'])
        if re.search(r'<h[23]\b',node):
            return re.sub(r'(<h[23]\b[^>]*>).*?(</h[23]>)',lambda m:m[1]+title+m[2],node,count=1,flags=re.S)
        label=r'(<span\b[^>]*class="lang-'+re.escape(lang)+r'"[^>]*>)[^<]*(</span>)'
        if re.search(label,node):
            return re.sub(label,lambda m:m[1]+title+m[2],node,count=1)
        if '<small>' in node:
            return re.sub(r'(</small>)[^<]*(</span>)',lambda m:m[1]+title+m[2],node,count=1)
        return re.sub(r'(<span[^>]*>\d{1,2}</span>)[^<]*(</a>)',lambda m:m[1]+title+m[2],node,count=1)
    return re.sub(r'<a\b[^>]*>.*?</a>',anchor,text,flags=re.S)

def apply_corrections(outputs):
    for path in sorted((DATA/'corrections').glob('*.json')):
        correction=json.loads(path.read_text());page=ROOT/correction['path'];text=outputs.get(page,page.read_text())
        for change in correction['edits']:
            lang=change['lang']
            def update(region):
                ps=body_paragraphs(region);at=change['paragraph']-1
                assert ps[at] in (change['before'],change['after']),'Unreviewed correction drift'
                if ps[at]==change['after']:return region
                def body_update(body):
                    nodes=list(re.finditer(r'<p\b[^>]*>.*?</p>',body,re.S));node=nodes[at]
                    return body[:node.start()]+paragraph(change['after'])+body[node.end():]
                return within(region,'article-body',body_update)
            text=within(text,'lang-'+lang,update)
        outputs[page]=text

def upgrade_outputs(outputs):
    reviewed=records()
    for (group,slug),record in reviewed.items():
        for lang in ('primary',*FOREIGN[1:]):
            path=page_path(group,slug,'en' if lang=='primary' else lang)
            outputs[path]=update_article(outputs.get(path,path.read_text()),record,lang)
    for group in GROUPS:
        editions={slug:r for (g,slug),r in reviewed.items() if g==group}
        if not editions:continue
        base=ROOT/'essays/everyday'/group
        for lang in ('primary',*FOREIGN[1:]):
            directory=base if lang=='primary' else base/lang
            for path in directory.glob('*.html'):
                text=outputs.get(path,path.read_text())
                new=within(text,'lang-en',lambda r:update_links(r,editions,'en')) if lang=='primary' else update_links(text,editions,lang)
                if new!=text or path in outputs:outputs[path]=new
    apply_corrections(outputs)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-folder',type=Path);parser.add_argument('--plan',type=Path)
    parser.add_argument('--reports',type=Path,nargs=3);parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.import_folder:assert args.plan and args.reports;import_batch(args.import_folder,args.plan,args.reports)
    outputs={};upgrade_outputs(outputs);changed=[p for p,t in outputs.items() if p.read_text()!=t]
    if args.check:
        assert not changed,('Outdated complete daily editions',[str(p.relative_to(ROOT)) for p in changed])
        print(f'OK: {len(records())} complete daily essays × eight languages are current')
    else:
        for p in changed:p.write_text(outputs[p])
        print(f'Updated {len(changed)} daily pages')
if __name__=='__main__':main()
