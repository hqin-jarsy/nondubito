#!/usr/bin/env python3
"""Render approved five-language film expansions without replacing source prose."""
from __future__ import annotations
import argparse
import datetime
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import markdown
import build_film_full_editions as film
import build_home_updates as home
import build_search_index as search
from build_sitemap import parse_page, sitemap_xml
from prepare_action_sources import Document, one

ROOT=film.ROOT
DATA=ROOT/'data/film-locale-expansions'
HUB=ROOT/'essays/film'
LANGS=('ja','fr','de','es','ko')
MAIN=('en','zh','zh-hant')
ORIGIN='https://nondubito.net/'
E=html.escape
TARGETS={
  '12-angry-men': (24, ('十二怒汉','十二怒漢','12 Angry Men'), ('1-one-vote-for-time','2-looking-again-at-the-evidence','3-the-son-in-the-room')),
  'the-lives-of-others': (38, ('窃听风暴','竊聽風暴','The Lives of Others'), ('1-the-systems-best-technician','2-nothing-to-do-with-state-security','3-no-its-for-me')),
  'yi-yi': (31, ('一一','一一','Yi Yi'), ('1-the-back-of-the-head','2-ota','3-grandmother')),
}
LANG_COUNT={'ja':'映画{n}作品 · 全{n3}篇','fr':'{n} films · {n3} essais complets','de':'{n} Filmreihen · {n3} vollständige Essays',
            'es':'{n} películas · {n3} ensayos completos','ko':'영화 {n}편 · 해설 {n3}편 전문'}
LEAD={'ja':'他人から与えられた役割だけでは語り尽くせない人々を、映画から読む。各篇は結末を含む。',
      'fr':'Des films sur des personnes que les rôles assignés ne suffisent pas à définir. Les essais dévoilent les intrigues, y compris les fins.',
      'de':'Filme über Menschen, die mehr sind als die Rollen, die andere ihnen zuweisen. Die Essays besprechen die Filme einschließlich ihrer Enden.',
      'es':'Películas sobre personas que no se agotan en los papeles que otros les asignan. Los ensayos revelan las tramas y sus desenlaces.',
      'ko':'다른 사람이 부여한 역할만으로는 다 설명할 수 없는 사람들을 영화에서 만난다. 각 글은 결말을 포함한다.'}
SLUGS=('ep01','ep02','ep03')
HERO_EN='Three essays · Eight languages'
HERO_ZH='三篇 · 八语全文'
HERO_HANT='三篇 · 八語全文'

def dump(data):return json.dumps(data,ensure_ascii=False,indent=2)+'\n'
def read(path):return json.loads(path.read_text())
def sha(text):return hashlib.sha256(text.encode()).hexdigest()
def source_signature(path):
    d=Document(path.read_text())
    bodies=[d.raw(n) for n in d.root.walk() if n.has('essay-body')]
    assert len(bodies)==2,path
    side=(path.parent/'zh-hant-data'/f'{path.stem}.js').read_text()
    return {'bodies':[sha(b) for b in bodies], 'traditional_script':sha(side)}

def text_value(s):
    return isinstance(s,str) and bool(s.strip()) and not re.search(r'<|\ufffd|\b(?:TODO|FIXME)\b',s)

def import_release(directory,slug,date):
    assert str(datetime.date.fromisoformat(date))==date
    number,names,chapters=TARGETS[slug]
    original={name:source_signature(HUB/slug/(name+'.html')) for name in chapters}
    editions={}
    for lang in LANGS:
        base=directory/lang
        meta=read(base/'meta.json')
        assert set(meta)=={'title','summary','spoiler','decks'},lang
        assert all(text_value(meta[x]) for x in ('title','summary','spoiler'))
        assert set(meta['decks'])==set(SLUGS) and all(map(text_value,meta['decks'].values()))
        articles={}
        for ep in SLUGS:
            raw=(base/(ep+'.md')).read_text()
            title,sep,body=raw.partition('\n')
            assert sep and title.startswith('# ') and text_value(title[2:]),(lang,ep)
            assert text_value(body) and '\n## ' in body and len(body.strip())>1500,(lang,ep,'incomplete or invalid body')
            assert not re.search(r'^# |^---\s*$',body,re.M),(lang,ep,'unexpected extra title or packaging note')
            articles[ep]={'title':title[2:].strip(),'deck':meta['decks'][ep],'markdown':body.strip(),'sha256':sha(raw)}
        editions[lang]={'title':meta['title'],'summary':meta['summary'],'spoiler':meta['spoiler'],'articles':articles}
    return {'slug':slug,'date':date,'number':number,'source':original,'editions':editions}

def releases():
    result={}
    if DATA.is_dir():
        for p in sorted(DATA.glob('*/release.json')):
            row=read(p); slug=row['slug']
            assert slug in TARGETS and p.parent.name==slug and row['number']==TARGETS[slug][0]
            result[slug]=row
    return result

def spec(slug):
    return {'slug':slug,'chapters':TARGETS[slug][2],'number':TARGETS[slug][0]}

def primary_alts(slug,name):
    base=ORIGIN+f'essays/film/{slug}/'
    suffix='' if name=='index.html' else name
    return ''.join(f'<link rel="alternate" hreflang="{lang}" href="{base+suffix}?lang={code}">' for lang,code in [('en','en'),('zh-Hans','zh'),('zh-Hant','zh-hant')])

def native(slug,row,lang,ep=None):
    data=row['editions'][lang]; f=spec(slug)
    note=f'<p class="ff-meta">{E(data["spoiler"])}</p>'
    if ep is not None:
        a=data['articles'][SLUGS[ep-1]]
        md=markdown.Markdown(extensions=['toc'])
        body=md.convert(a['markdown'])
        copy={'title':a['title'],'description':a['deck'],'toc':md.toc,'body':note+body}
    else:
        cards=''.join(f'<a class="ff-card" href="{chapter}.html"><span>{i+1:02d}</span><h2>{E(data["articles"][SLUGS[i]]["title"])}</h2><p>{E(data["articles"][SLUGS[i]]["deck"])}</p></a>'
                      for i,chapter in enumerate(f['chapters']))
        copy={'title':data['title'],'description':data['summary'],'body':f'<p>{E(data["summary"])}</p>'+note+f'<div class="ff-grid">{cards}</div>'}
    page=film.page(f,lang,copy,ep)
    filename=f['chapters'][ep-1]+'.html' if ep else 'index.html'
    # Shared EN/Hans/Hant use an explicit query, never fabricated path editions.
    a=film.alternate_links(slug,filename)
    assert page.count(a)==1
    page=page.replace(a,primary_alts(slug,filename)+a,1)
    for k in ('datePublished','dateModified'):
        page=page.replace(f'"{k}": "{film.DATE}"',f'"{k}": "{row["date"]}"',1)
    page=page.replace(E(film.UI[lang]['updated']),f'<time datetime="{row["date"]}">{row["date"]}</time>',1)
    return page

def primary(path,row):
    slug=row['slug']; s=path.read_text(); f=spec(slug)
    if path.stem!='index':
        assert source_signature(path)==row['source'][path.stem],(path,'source drift, do not overwrite')
    t=film.legacy(path,f)
    a=film.alternate_links(slug,path.name)
    assert t.count(a)==1
    t=t.replace(a,primary_alts(slug,path.name)+a,1)
    if path.stem=='index':
        t=t.replace('English · 简 / 繁 · Film criticism','Eight languages · Film criticism')
        t=t.replace('英文 · 简 / 繁 · 电影解读','八语全文 · 电影解读')
        t=t.replace('English · 简 / 繁','Eight languages')
        t=t.replace('英文 · 简 / 繁','八语全文')
        label_script=('<style id="film-expansion-card-language">html[data-lang="zh-hant"] .film-edition-zh-label,'
                      'html:not([data-lang="zh-hant"]) .film-edition-hant-label{display:none!important}</style>')
        t=t.replace(label_script,'').replace('</head>',label_script+'</head>',1)
        t=t.replace('>八语全文 · 电影解读</div>','><span class="film-edition-zh-label">八语全文 · 电影解读</span><span class="film-edition-hant-label">八語全文 · 電影解讀</span></div>')
    old=Document(s)
    new=Document(t)
    if path.stem!='index':
        def prose(d):return [d.raw(n) for n in d.root.walk() if n.has('essay-body')]
        assert prose(old)==prose(new),path
    return t

def catalog(path, rows, hub=False, source=None):
    text=path.read_text() if source is None else source
    for slug in rows:
        route=slug+'/index.html' if hub else 'essays/film/'+slug+'/index.html'
        doc=Document(text)
        card=one(doc.root.walk(),lambda n:n.tag=='a' and n.attrs.get('href')==route and n.has('series-card'),route)
        badge=one(card.walk(),lambda n:n.has('series-card-count'),route)
        number=TARGETS[slug][0]
        content=f'<span class="lang-en">No. {number} · {HERO_EN}</span><span class="lang-zh cl-zh">{HERO_ZH}</span><span class="lang-zh cl-hant">{HERO_HANT}</span>'
        text=text[:badge.open_end]+content+text[badge.close_start:]
    if hub:
        badge_style = ('<style id="film-expansion-badge-style">html:not([data-lang="zh-hant"]) .series-card-count .cl-hant,'
                       'html[data-lang="zh-hant"] .series-card-count .cl-zh{display:none!important}</style>')
        text=text.replace(badge_style,'').replace('</head>',badge_style+'</head>',1)
        count=len(film.FILMS)+len(rows)
        text=re.sub(r'(?<!\d)\d+ series in 8 languages',f'{count} series in 8 languages',text)
        text=re.sub(r'已有 \d+ 部作品八语齐备',f'已有 {count} 部作品八语齐备',text)
    return text

START='<!-- SCOPED FILM EXPANSIONS START -->'
END='<!-- SCOPED FILM EXPANSIONS END -->'
BLOCK=re.compile(re.escape(START)+r'.*?'+re.escape(END),re.S)
def native_hub(path,lang,rows,source=None):
    text=BLOCK.sub('',path.read_text() if source is None else source)
    d=Document(text)
    grid=one(d.root.walk(),lambda n:n.has('ff-grid'),path)
    cards=''.join(f'<a class="ff-card" href="../{slug}/{lang}/index.html"><span>{row["number"]:02d}</span><h2>{E(row["editions"][lang]["title"])}</h2><p>{E(row["editions"][lang]["summary"])}</p></a>'
                  for slug,row in sorted(rows.items(),key=lambda pair:pair[1]['number']))
    # Keep the legacy cards in their original order and add the reviewed group.
    text=text[:grid.close_start]+START+cards+END+text[grid.close_start:]
    heading=re.compile(r'(<div class="ff-body"><p>).*?(</p><p class="ff-meta">).*?(</p>)',re.S)
    count=len(film.FILMS)+len(rows)
    text,n=heading.subn(lambda m:m[1]+E(LEAD[lang])+m[2]+E(LANG_COUNT[lang].format(n=count,n3=count*3))+m[3],text,count=1)
    assert n==1,path
    return text

def site_outputs(rows):
    out={}
    for slug,row in rows.items():
        root=HUB/slug
        for ep,name in enumerate(('index',*spec(slug)['chapters'])):
            out[root/(name+'.html')]=primary(root/(name+'.html'),row)
            for lang in LANGS:
                out[root/lang/(name+'.html')]=native(slug,row,lang,ep or None)
    if rows:
        out[HUB/'index.html']=catalog(HUB/'index.html',rows,hub=True)
        out[ROOT/'library.html']=catalog(ROOT/'library.html',rows)
        for lang in LANGS:
            path=HUB/lang/'index.html'
            out[path]=native_hub(path,lang,rows)
    return out

def discovery_outputs(rows, reading_pages):
    if not rows:return {}
    scope=set(reading_pages)|{ROOT/'index.html', ROOT/'latest.html'}
    with patch.object(search,'collect_pages',lambda:sorted(scope)):
        _,fresh=search.build()
    manifest=read(search.OUTPUT)
    unique=set()
    result={}
    for lang,replacements in fresh.items():
        path=search.CHUNKS_DIR/f'{lang.lower()}.json'
        chunk=read(path)
        updates={r['u']:r for r in replacements}
        chunk['records']=[updates.pop(r['u'],r) for r in chunk['records']]
        chunk['records'].extend(updates.values())
        assert len(chunk['records'])==len({r['u'] for r in chunk['records']}),(lang,'duplicate search records')
        unique.update(r['u'] for r in chunk['records'])
        manifest['languages'][lang]['count']=len(chunk['records'])
        result[path]=search.serialized(chunk)
    manifest['record_count']=len(unique)
    result[search.OUTPUT]=search.serialized(manifest)
    p=ROOT/'sitemap.xml'
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    entries={u.findtext(ns+'loc'):u.findtext(ns+'lastmod') for u in ET.parse(p).getroot()}
    newest=max(row['date'] for row in rows.values())
    for path in scope:
        rel=path.relative_to(ROOT).as_posix()
        date=next((row['date'] for slug,row in rows.items() if rel.startswith(f'essays/film/{slug}/')),newest)
        url=parse_page(path).canonical
        assert url.startswith(ORIGIN),path
        entries[url]=max(entries.get(url,date),date)
    result[p]=sitemap_xml(list(entries.items()))
    return result

LATEST_START='<!-- SCOPED FILM LOCALE LATEST START -->'
LATEST_END='<!-- SCOPED FILM LOCALE LATEST END -->'
LATEST_BLOCK=re.compile(re.escape(LATEST_START)+r'.*?'+re.escape(LATEST_END)+r'\\n?',re.S)
UI_LANGS=(('en','en'),('zh','zh'),('zh-hant','hant'))
def update_out(rows):
    path=ROOT/'data/site-updates.json'
    ledger=read(path)
    entries=[]
    for slug,row in rows.items():
        zh,hant,en=TARGETS[slug][1]
        entries.append({'id':f'{row["date"]}-film-{slug}-eight-languages','date':row['date'],'kind':'expanded',
                        'domain':'stories','series_key':f'essays/film/{slug}','url':f'essays/film/{slug}/index.html',
                        'languages':[*MAIN,*LANGS],'title':{'en':en+' · Three Essays in Eight Languages','zh':f'《{zh}》：三篇八语全文','zh-hant':f'《{hant}》：三篇八語全文'},
                        'summary':{'en':'Three film essays now also have complete Japanese, French, German, Spanish and Korean editions. The existing Chinese and English prose remains available.',
                        'zh':'三篇电影解读新增日、法、德、西、韩全文，原有简繁中文与英文正文保留。',
                        'zh-hant':'三篇電影解讀新增日、法、德、西、韓全文，原有簡繁中文與英文正文保留。'}})
    keys={e['id'] for e in entries}
    ledger['updates']=sorted([*entries,*(u for u in ledger['updates'] if u['id'] not in keys)],key=lambda u:u['date'],reverse=True)
    result={path:dump(ledger)}
    latest=ROOT/'latest.html'
    source=LATEST_BLOCK.sub('',latest.read_text())
    anchor=re.search(r'(?:<!--[^>]*-->\\s*)?<section class="updates-section">',source)
    assert anchor
    blocks=[]
    for e in entries:
        tag=e['id']+'-title'
        title=''.join(f'<h3 class="lang-{css}">{E(e["title"][l])}</h3>' for l,css in UI_LANGS)
        summary=''.join(f'<p class="lang-{css}">{E(e["summary"][l])}</p>' for l,css in UI_LANGS)
        blocks.append(f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="{tag}"><header class="updates-date"><h2 id="{tag}"><time datetime="{e["date"]}">{e["date"]}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{e["id"]}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Expanded</span><span class="lang-zh">拓展</span><span class="lang-hant">拓展</span></span><span>简 · 繁 · EN · JA · FR · DE · ES · KO</span></div>{title}{summary}<a href="{e["url"]}"><span class="lang-en">Read the series →</span><span class="lang-zh">进入系列 →</span><span class="lang-hant">進入系列 →</span></a></article></div></section></div></section>')
    pos=anchor.start()
    result[latest]=source[:pos]+LATEST_START+''.join(blocks)+LATEST_END+'\\n'+source[pos:]
    index=ROOT/'index.html'
    config=read(ROOT/'data/home-updates.json')
    result[index]=home.replace_section(index.read_text(),home.render_section(ledger['updates'],config))
    return result

def verify_pages(rows,pages):
    for slug,row in rows.items():
        chapter_names=spec(slug)['chapters']
        for name in ('index',*chapter_names):
            shared=HUB/slug/(name+'.html')
            s=pages[shared]
            assert all(f'href="{lang}/{name}.html"' in s for lang in LANGS),shared
            for lang in LANGS:
                native=shared.parent/lang/shared.name
                text=pages[native]
                doc=Document(text)
                main=one(doc.root.walk(),lambda n:n.tag=='main',str(native))
                assert sum(n.tag=='h1' for n in main.walk())==1,native
                hreflang=[n.attrs['hreflang'] for n in doc.root.walk() if n.tag=='link' and n.attrs.get('rel')=='alternate']
                assert set(hreflang)=={'en','zh-Hans','zh-Hant',*LANGS,'x-default'} and len(hreflang)==9,native
                assert E(row['editions'][lang]['spoiler']) in text,native
                if name!='index':
                    assert f'href="../{name}.html?lang=zh-hant"' in text,native
                    links=[n.attrs['href'] for n in main.walk() if n.tag=='a' and n.attrs.get('href','').startswith('#')]
                    ids={n.attrs.get('id') for n in main.walk()}
                    assert all(h[1:] in ids for h in links),native


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--slug',choices=TARGETS)
    p.add_argument('--import-dir',type=Path)
    p.add_argument('--date')
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--check-inputs',action='store_true')
    mode.add_argument('--check',action='store_true')
    args=p.parse_args()
    if args.check_inputs and not args.import_dir:p.error('--check-inputs requires --import-dir')
    if args.check and args.import_dir:p.error('--check checks existing local release data')
    rows=releases()
    if args.import_dir:
        if not args.slug or not args.date:p.error('--import-dir requires --slug and --date')
        rows[args.slug]=import_release(args.import_dir,args.slug,args.date)
    if not rows:p.error('no reviewed film data')
    pages=site_outputs(rows)
    verify_pages(rows,pages)
    if args.check_inputs:
        print(f'Inputs render successfully for {args.slug}; no files written.')
        return
    if args.import_dir:
        p=DATA/args.slug/'release.json'
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(dump(rows[args.slug]))
    def write(outputs):
        for path,value in outputs.items():
            if args.check:assert path.read_text()==value,path
            elif not path.is_file() or path.read_text()!=value:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(value)
    write(pages)
    write(update_out(rows))
    write(discovery_outputs(rows,pages))
    print(f'{len(rows)} film series; {len(pages)} scoped reading and catalog outputs. No existing source prose changed.')

if __name__=='__main__':main()
