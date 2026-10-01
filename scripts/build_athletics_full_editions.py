#!/usr/bin/env python3
"""Publish the reviewed complete Athletics editions without touching the ZIPs.

Import is explicit and one-time. Subsequent builds use checked-in manuscripts
and hashes; no translation service or external manuscript is needed.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile

from build_emperor_full_editions import replace_div
from build_emperor_traditional import TraditionalConverter
from build_worldcup_full_editions import render, refresh_indexes

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT/'essays/athletics'
DATA = ROOT/'data/athletics-full'
RECEIPT = DATA/'review.json'
LANGS = ('de', 'fr', 'es', 'ja', 'ko')
TOC = dict(de='In diesem Essay', fr='Dans cet essai', es='En este ensayo', ja='この篇の目次', ko='이 글의 목차')
STYLE = '''<style id="athletics-full-style">
.essay-main{width:100%;min-width:0;max-width:820px;margin:0 auto;padding:96px 28px 70px;overflow-wrap:anywhere}
.essay-main .essay-body{max-width:none;margin:0;padding:0}
.essay-main .essay-header{height:auto;text-align:left;color:var(--ink)}
.essay-main .essay-header h1{font-size:clamp(1.8rem,4vw,2.7rem);line-height:1.35;color:var(--ink)}
.essay-main .essay-meta{color:var(--ink-muted)}
.essay-main .lang-toggle{margin-bottom:1.5rem}
@media(max-width:600px){.essay-main{padding:88px 22px 50px}}
.athletics-full p{overflow-wrap:break-word}
.athletics-full h2{line-height:1.55;margin-top:2.5rem;scroll-margin-top:100px;overflow-wrap:anywhere}
.athletics-toc{margin:1.5rem 0 2rem;padding:1rem 1.25rem;border:1px solid var(--cream-border)}
.athletics-toc summary{cursor:pointer;font-family:var(--sans);color:var(--ink-muted)}
.athletics-toc li{margin:.5rem 0;line-height:1.6;overflow-wrap:anywhere}
.athletics-toc a{color:var(--ink-light)}
.essay-header h1,.essay-subtitle,.entry-title,.entry-desc,.series-nav a{overflow-wrap:anywhere}
.essay-header{position:static;display:block;background:none;border:0;padding:0;margin:0 0 2rem;backdrop-filter:none}
.essay-subtitle{font-size:1.1rem;line-height:1.8;color:var(--ink-muted);margin:1rem 0}
.essay-body.ko p{word-break:keep-all;overflow-wrap:break-word}
</style>'''

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def plain(text):
    return html.unescape(re.sub('<[^>]*>', '', text)).strip()

def split_md(text):
    parts = re.split(r'^## (.+)\n', text, flags=re.M)
    return parts[0], [(parts[i], re.split(r'\n\s*\n', parts[i+1].strip())) for i in range(1,len(parts),2)]

def source_paragraph(text, lang, section, paragraph):
    body = re.search(r'<div class="essay-body lang-'+lang+r'"[^>]*>(.*?)</div>', text, re.S)
    assert body, lang
    sections = list(re.finditer(r'<h2[^>]*>.*?</h2>(.*?)(?=<h2|$)', body[1], re.S))
    s = sections[section-1]
    paras = list(re.finditer(r'<p\b[^>]*>(.*?)</p>', s[1], re.S))
    match = paras[paragraph-1 if paragraph>0 else paragraph]
    offset = body.start(1)+s.start(1)+match.start(1)
    return offset, offset+len(match[1]), match[1]

def import_archives(folder):
    assert not RECEIPT.exists(), 'Refusing to overwrite reviewed source import'
    plan = json.loads((DATA/'copyedits.json').read_text())
    extra = json.loads((DATA/'source-copyedits.json').read_text())
    protected = {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in [*SERIES.glob('*.html'), * (SERIES/'zh-hant-data').glob('*.js')]}
    receipt = dict(baseline_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                   protected_files=protected, archives={}, manuscripts={}, source_corrections=[],
                   scope='115 full editions; targeted editorial review, not a new exhaustive historical audit',
                   plans={p.name:sha(p.read_bytes()) for p in [DATA/'copyedits.json',DATA/'source-copyedits.json']})
    prepared = {}
    for ep in plan['episodes']:
        source = (SERIES/f'{ep}.html').read_text()
        body = re.search(r'<div class="essay-body lang-zh"[^>]*>(.*?)</div>',source,re.S)[1]
        expected = [len(re.findall(r'<p\b',s)) for s in re.split(r'<h2[^>]*>.*?</h2>',body,flags=re.S)[1:]]
        archive = folder/f'NonDubito_Athletics_{ep.upper()}_DE_FR_ES_JA_KO_v1.0.zip'
        with ZipFile(archive) as z:
            assert z.testzip() is None
            receipt['archives'][ep] = dict(name=archive.name,sha256=sha(archive.read_bytes()),
                notes={n:z.read(n).decode('utf-8-sig') for n in z.namelist() if n.endswith('notes.md')})
            for lang in LANGS:
                names=[n for n in z.namelist() if n.endswith('_'+lang+'.md')]
                assert len(names)==1
                raw=z.read(names[0]);original=raw.decode('utf-8-sig')
                preface,sections=split_md(original)
                assert [len(p) for _,p in sections]==expected,(ep,lang)
                edits=[]
                for edit in plan['edits']:
                    if (edit['ep'],edit['lang'])!=(ep,lang):continue
                    paras=sections[edit['section']-1][1]
                    pos=edit['paragraph']-1 if edit['paragraph']>0 else edit['paragraph']
                    before=paras[pos]
                    after=before+' '+edit['after'] if edit['mode']=='append' else edit['after']
                    paras[pos]=after
                    edits.append(dict(edit,before=before,after=after))
                title=re.search(r'^# (.+)$',preface,re.M)[1].strip()
                key=ep+'.'+lang
                deck=plan['decks'].get(key)
                if not deck:
                    candidates=[p.strip() for p in re.split(r'\n\s*\n',preface) if not p.startswith('#') and '](' not in p and 'Non Dubito' not in p]
                    deck=max(candidates,key=len)
                text='# '+title+'\n\n'+'\n\n'.join('## '+h+'\n\n'+'\n\n'.join(paras) for h,paras in sections)+'\n'
                assert [render('\n\n'.join(paras)).count('<p>') for _,paras in sections]==expected,key
                refs=[dict(label=a,url=b) for a,b in re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)',preface) if 'nondubito.net' not in b]
                receipt['manuscripts'][key]=dict(title=title,deck=deck,received_sha256=sha(raw),published_sha256=sha(text.encode()),
                    paragraphs_by_section=expected,edits=edits,removed_preface=preface.strip(),references=refs)
                prepared[DATA/f'{key}.md']=text
    all_source_edits=[e for e in plan['edits'] if e['lang']=='zh']+extra
    converter=TraditionalConverter()
    try:
        for ep in sorted({e['ep'] for e in all_source_edits}):
            path=SERIES/f'{ep}.html';original=path.read_text();text=original;edits=[];hant=[]
            for edit in all_source_edits:
                if edit['ep']!=ep:continue
                start,end,before=source_paragraph(text,edit['lang'],edit['section'],edit['paragraph'])
                after=(plain(before)+' ' if edit['mode']=='append' else '')+edit['after']
                text=text[:start]+html.escape(after,quote=False)+text[end:]
                edits.append(dict(edit,before=before,after=html.escape(after,quote=False)))
                if edit['lang']=='zh':hant.append((html.unescape(before),after,converter.convert(after)))
            prepared[path]=text
            receipt['source_corrections'].append(dict(path=path.relative_to(ROOT).as_posix(),before_sha256=sha(original.encode()),after_sha256=sha(text.encode()),edits=edits))
            hp=SERIES/'zh-hant-data'/f'{ep}.js';old=hp.read_text()
            match=re.search(r'var variants = (\{.*?\});\s*\n\s*var originals',old,re.S)
            assert match,hp
            variants=json.loads(match[1])
            for before,after,traditional in hant:
                variants.pop(before,None);variants[after]=traditional
            new=old[:match.start(1)]+json.dumps(variants,ensure_ascii=False,sort_keys=True,separators=(',',':'))+old[match.end(1):]
            if new!=old:
                prepared[hp]=new
                receipt['source_corrections'].append(dict(path=hp.relative_to(ROOT).as_posix(),before_sha256=sha(old.encode()),after_sha256=sha(new.encode()),traditional_pairs=hant))
    finally:converter.close()
    for path,text in prepared.items():path.write_text(text)
    RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('Imported 115 full manuscripts and their explicit editorial receipts')
    return {p for p in prepared if p.suffix=='.html'}

def copies():
    receipt=json.loads(RECEIPT.read_text());out={}
    for key,r in receipt['manuscripts'].items():
        raw=(DATA/f'{key}.md').read_bytes()
        assert sha(raw)==r['published_sha256'],(key,'unrecorded edit')
        preface,sections=split_md(raw.decode())
        assert preface.strip()=='# '+r['title']
        assert [len(p) for _,p in sections]==r['paragraphs_by_section']
        body='\n'.join(f'<section><h2 id="section-{i}">{html.escape(h)}</h2>\n'+render('\n\n'.join(paras))+'\n</section>' for i,(h,paras) in enumerate(sections,1))
        out[key]=dict(r,body=body,headings=[h for h,_ in sections])
    return out

def final_copyedits(pp):
    """Apply a recorded, one-time final pass; refuse unexpected text drift."""
    plan=json.loads(pp.read_text());r=json.loads(RECEIPT.read_text())
    assert pp.name not in r['plans'], 'Final pass already applied'
    prepared={}
    for key,edits in plan['manuscripts'].items():
        path=DATA/f'{key}.md';text=path.read_text()
        assert sha(text.encode())==r['manuscripts'][key]['published_sha256']
        for e in edits:
            assert text.count(e['before'])==1,(key,e)
            text=text.replace(e['before'],e['after'],1)
        prepared[path]=text
        r['manuscripts'][key]['edits'].extend(edits)
        r['manuscripts'][key]['published_sha256']=sha(text.encode())
    converter=TraditionalConverter()
    try:
        for ep,edits in plan['sources'].items():
            path=SERIES/f'{ep}.html';rel=path.relative_to(ROOT).as_posix();c=next((c for c in r['source_corrections'] if c['path']==rel),None)
            if c is None:
                c=dict(path=rel,before_sha256=r['protected_files'][rel],after_sha256=r['protected_files'][rel],edits=[])
                r['source_corrections'].append(c)
            text=path.read_text();assert sha(text.encode())==c['after_sha256']
            hp=SERIES/'zh-hant-data'/f'{ep}.js';hrel=hp.relative_to(ROOT).as_posix();hc=next((c for c in r['source_corrections'] if c['path']==hrel),None)
            if hc is None:
                hc=dict(path=hrel,before_sha256=r['protected_files'][hrel],after_sha256=r['protected_files'][hrel],traditional_pairs=[])
                r['source_corrections'].append(hc)
            hs=hp.read_text();m=re.search(r'var variants = (\{.*?\});\s*\n\s*var originals',hs,re.S);variants=json.loads(m[1])
            for e in edits:
                assert text.count(e['before'])==1,(ep,e)
                text=text.replace(e['before'],e['after'],1);c['edits'].append(e)
                if e['lang']=='zh' and e.get('scope')!='metadata':
                    # A phrase edit can sit inside a full text-node map key.
                    matches=[key for key in variants if e['before'] in key]
                    assert matches,(ep,e)
                    for old in matches:
                        new=old.replace(e['before'],e['after'],1);hant=converter.convert(new)
                        variants.pop(old);variants[new]=hant;hc['traditional_pairs'].append([old,new,hant])
            prepared[path]=text;c['after_sha256']=sha(text.encode())
            hs=hs[:m.start(1)]+json.dumps(variants,ensure_ascii=False,sort_keys=True,separators=(',',':'))+hs[m.end(1):]
            prepared[hp]=hs;hc['after_sha256']=sha(hs.encode())
    finally:converter.close()
    r['plans'][pp.name]=sha(pp.read_bytes())
    for path,text in prepared.items():path.write_text(text)
    RECEIPT.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')

def output_pages():
    all_copies=copies();out={}
    evidence=json.loads((DATA/'editorial-evidence.json').read_text())['sources']
    for lang in LANGS:
        titles={key.split('.')[0]:v for key,v in all_copies.items() if key.endswith('.'+lang)}
        for path in sorted((SERIES/lang).glob('*.html')):
            text=path.read_text()
            if path.stem in titles:
                r=titles[path.stem]
                text=replace_div(text,'essay-body '+lang,'<div class="athletics-full">\n'+r['body']+'\n</div>')
                text=re.sub(r'<header class="essay-header">(.*?)</header>',r'<section class="essay-header">\1</section>',text,flags=re.S)
                text=re.sub(r'(<h1[^>]*>).*?(</h1>)',lambda m:m[1]+html.escape(r['title'])+m[2],text,count=1,flags=re.S)
                text=re.sub(r'<p class="essay-subtitle">.*?</p>\s*','',text,flags=re.S)
                text=text.replace('</h1>','</h1><p class="essay-subtitle">'+html.escape(r['deck'])+'</p>',1)
                text=re.sub(r'<title>.*?</title>',lambda _:'<title>'+html.escape(r['title'])+' — Non Dubito</title>',text,count=1,flags=re.S)
                for attribute,name,value in [('property','og:title',r['title']+' — Non Dubito'),('name','description',r['deck']),('property','og:description',r['deck'])]:
                    text=re.sub('(<meta '+attribute+'="'+name+'" content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],text)
                text=re.sub(r'<details class="athletics-toc">.*?</details>\s*','',text,flags=re.S)
                toc='<details class="athletics-toc"><summary>'+TOC[lang]+'</summary><ul>'+''.join(f'<li><a href="#section-{i}">{html.escape(h)}</a></li>' for i,h in enumerate(r['headings'],1))+'</ul></details>\n'
                text=re.sub(r'(?=<div class="essay-body)',lambda _:toc,text,count=1)
                # Preserve existing factual-reference footer and expose any additional
                # links received in the prefatory source notes, without duplicating it.
                text=re.sub(r'<div class="essay-footer-note athletics-extra-sources">.*?</div>\s*','',text,flags=re.S)
                refs=[]
                for ref in r['references']+[e for e in evidence if int(path.stem[2:]) in e['episodes']]:
                    if ref['url'] not in html.unescape(text) and ref['url'] not in {a['url'] for a in refs}:refs.append(ref)
                if refs:
                    foot='<div class="essay-footer-note athletics-extra-sources">'+' · '.join('<a href="'+html.escape(a['url'],quote=True)+'" target="_blank" rel="noopener">'+html.escape(a['label'])+' ↗</a>' for a in refs)+'</div>\n'
                    text=text.replace('</article>',foot+'</article>')
            def anchor(m):
                a=m[0];target=re.search(r'href="(ep\d{2})\.html"',a)
                if not target or target[1] not in titles:return a
                r=titles[target[1]]
                a=re.sub(r'(<div class="entry-title">).*?(</div>)',lambda m:m[1]+html.escape(r['title'])+m[2],a,flags=re.S)
                a=re.sub(r'(<div class="entry-desc">).*?(</div>)',lambda m:m[1]+html.escape(r['deck'])+m[2],a,flags=re.S)
                if '<small>' in a:a=re.sub(r'(</small>).*?(</a>)',lambda m:m[1]+'<span class="athletics-nav-title">'+html.escape(r['title'])+'</span>'+m[2],a,flags=re.S)
                return a
            text=re.sub(r'<a\b[^>]*>.*?</a>',anchor,text,flags=re.S)
            text=re.sub(r'<style id="athletics-full-style">.*?</style>\s*','',text,flags=re.S)
            if 'src="../../../language-select.js"' not in text:text=text.replace('</head>','<script defer src="../../../language-select.js"></script>\n</head>',1)
            text=text.replace('</head>',STYLE+'\n</head>',1)
            out[path]=text
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--import-archives',type=Path);ap.add_argument('--check',action='store_true');ap.add_argument('--refresh-indexes',action='store_true')
    ap.add_argument('--final-copyedits',nargs='?',const=DATA/'final-copyedits.json',type=Path)
    args=ap.parse_args()
    assert not(args.check and (args.import_archives or args.refresh_indexes or args.final_copyedits))
    source_changes=import_archives(args.import_archives) if args.import_archives else set()
    if args.final_copyedits:final_copyedits(args.final_copyedits)
    out=output_pages();changed={p:t for p,t in out.items() if p.read_text()!=t}
    if args.check:
        assert not changed,'Stale outputs: '+str(list(changed))
        print('OK: 115 full editions, five indexes, metadata and neighbor titles')
    else:
        for p,t in changed.items():p.write_text(t)
        if args.refresh_indexes:
            source_changes |= {ROOT/c['path'] for c in json.loads(RECEIPT.read_text())['source_corrections'] if c['path'].endswith('.html')}
            refresh_indexes(set(changed)|source_changes)
        print(f'Updated {len(changed)} language pages and {len(source_changes)} source pages')

if __name__=='__main__':main()
