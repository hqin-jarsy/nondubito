#!/usr/bin/env python3
"""Public Japanese reader; projects Japanese fields only, never source fallback."""
import argparse
import html
import json
from pathlib import Path
from hongloumeng_partial_private import inspect_partial
from web_analytics import tracked_html
from build_hongloumeng_reading import checked_input_paths

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/hongloumeng/first80-japanese'
SOURCE = ROOT / 'data/hongloumeng/first80-public/reading.zh.json'
BASE = '/classics/hongloumeng/'
PARTIAL = {6:3,9:2,12:1,65:4,75:1}
E = html.escape
OWNER_SLOTS = sum(PARTIAL.values())
NOTICE = (f'前八十回の日本語訳。{80-len(PARTIAL)}回は翻訳済み、{len(PARTIAL)}回の計{OWNER_SLOTS}か所は作者による補訳待ちです。未完の位置には検索できる固有の印を残しています。'
          if PARTIAL else '前八十回の日本語訳。全八十回を翻訳済みです。')
BOUNDARY = 'ここまでが曹雪芹の原著前八十回です。第八十一〜八十五回は秦漢による独自の続編であり、曹雪芹の失われた原稿ではありません。第八十六〜百十回は未公開です。'
CSS = '''*{box-sizing:border-box}html{background:#faf8f3;color:#292722}body{margin:0;font:18px/1.95 "Hiragino Mincho ProN","Yu Mincho",serif}header,main,footer{max-width:48rem;margin:auto;padding:1.2rem}a{color:#795831;text-underline-offset:.2em}nav{display:flex;flex-wrap:wrap;gap:.5rem 1rem;margin:1rem 0}header,footer{font-family:system-ui,sans-serif;font-size:.9rem}h1{font-size:1.7em;line-height:1.6}article p{margin:1.1em 0;white-space:pre-line;overflow-wrap:anywhere}article .verse,article .couplet{padding-left:1.4em;border-left:2px solid #d5c5ad}article .letter{padding:1em;background:#f0ece3}.notice{padding:1rem;background:#f0e9d9;border-left:3px solid #967446;font-size:.92em}mark{background:#ffe6a0;overflow-wrap:anywhere}button,input{font:inherit;max-width:100%;padding:.4em .7em}button{cursor:pointer}input{width:100%}.toc{padding-left:0;list-style:none}.toc li{margin:.6em 0}.badge{font-size:.8em;color:#88501a}.skip{position:absolute;left:-9999px}.skip:focus{left:0;background:white}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #967446;outline-offset:3px}@media(max-width:600px){body{font-size:17px}header,main,footer{padding:1rem}h1{font-size:1.4em}article .verse{padding-left:.8em}}'''
JS = '''(()=>{const article=document.querySelector('article');let size=18;try{size=Number(localStorage.getItem('hlm-ja-size'))||18}catch(e){}const apply=()=>{size=Math.max(14,Math.min(28,size));if(article)article.style.fontSize=size+'px';try{localStorage.setItem('hlm-ja-size',size)}catch(e){}};apply();document.querySelectorAll('[data-size]').forEach(b=>b.addEventListener('click',()=>{size=b.dataset.size==='reset'?18:size+Number(b.dataset.size);apply()}));const q=document.querySelector('#toc-search');if(q)q.addEventListener('input',()=>{let count=0;document.querySelectorAll('.toc li').forEach(li=>{li.hidden=!li.textContent.toLowerCase().includes(q.value.trim().toLowerCase());if(!li.hidden)count++});document.querySelector('#search-count').textContent=count+'回を表示';});})();'''

def load_chapters(data=DATA, *, source=None):
    source_chapters = None
    if source is not None:
        from hongloumeng_japanese_pipeline import validate, validate_partial
        checked_input_paths([source])
        source_chapters = json.loads(Path(source).read_text()).get('chapters')
        if (not isinstance(source_chapters, list) or len(source_chapters) != 80
                or any(not isinstance(c, dict) or type(c.get('number')) is not int
                       or c['number'] != n for n, c in enumerate(source_chapters, 1))):
            raise ValueError('Exactly eighty ordered source chapters required')
    out=[]
    for n in range(1,81):
        path=data/'chapters'/f'ch{n:03}.{"partial" if n in PARTIAL else "draft"}.json'
        checked_input_paths([path])
        if path.is_symlink() or path.stat().st_nlink != 1:
            raise ValueError('Unsafe draft path')
        d=json.loads(path.read_text())
        if d.get('schemaVersion')!=1 or d.get('language')!='ja' or d.get('number')!=n or not isinstance(d.get('title'),str) or not d['title'].strip() or not isinstance(d.get('blocks'),list) or not d['blocks']:
            raise ValueError('Japanese chapter identity required')
        if source_chapters is not None:
            (validate_partial if n in PARTIAL else validate)(source_chapters[n-1], d)
        entries=inspect_partial(d) if n in PARTIAL else []
        if len(entries)!=PARTIAL.get(n,0): raise ValueError('Unexpected placeholder count')
        blocks=[]
        for b in d['blocks']:
            if n not in PARTIAL and ('sourceSegments' in b or b.get('status')=='owner_translation_needed'):
                raise ValueError('Unexpected partial content in complete chapter')
            parts=[]
            for s in b.get('sourceSegments',[b]):
                if s.get('status')=='owner_translation_needed':
                    label=s['label']; marker=label.split(' ')[1][:-1]
                    parts.append(f'<mark id="{marker}">{E(label)}</mark>')
                else:
                    text=s.get('text')
                    if not isinstance(text,str) or not text.strip(): raise ValueError('Missing Japanese; source fallback forbidden')
                    parts.append(E(text))
            kind=b.get('kind','prose')
            kind=kind if kind in {'verse','couplet','letter','diagram'} else 'prose'
            blocks.append(f'<p class="{kind}">'+''.join(parts)+'</p>')
        out.append({'number':n,'title':d['title'],'body':''.join(blocks),'markers':[e['id'] for e in entries]})
    return out

def languages(filename):
    return '<nav class="language-switch" aria-label="言語">'+''.join(f'<a lang="{lang}" href="{BASE}{directory}{filename}"'+(' aria-current="page"' if lang=='ja' else '')+f'>{label}</a>' for lang,directory,label in [('zh-Hans','','简体中文'),('zh-Hant','zh-hant/','繁體中文'),('en','en/','English'),('ja','ja/','日本語')])+'</nav>'

@tracked_html
def shell(title,filename,body):
    path='' if filename=='index.html' else filename
    alternates=''.join(f'<link rel="alternate" hreflang="{lang}" href="https://nondubito.net{BASE}{directory}{path}">' for lang,directory in [('zh-Hans',''),('zh-Hant','zh-hant/'),('en','en/'),('ja','ja/'),('x-default','')])
    return f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} — Non Dubito</title><meta name="description" content="{NOTICE}"><link rel="canonical" href="https://nondubito.net{BASE}ja/{path}">{alternates}<link rel="stylesheet" href="reader.css"><script defer src="reader.js"></script></head><body><a class="skip" href="#main">本文へ</a><header><a href="/">Non Dubito</a> · 紅楼夢{languages(filename)}<nav><a href="index.html">回目一覧</a><a href="edition.html">版について</a></nav></header><main id="main">{body}</main><footer>曹雪芹 原著 · 大知校訂庚辰本に基づく日本語訳<nav><a href="index.html">前八十回の回目一覧</a><a href="/originals/hongloumeng/ja/">秦漢の独自続編（第81〜85回）</a></nav></footer></body></html>'

def render(chapters):
    if [c['number'] for c in chapters]!=list(range(1,81)):raise ValueError('Exactly eighty ordered chapters required')
    result={'reader.css':CSS,'reader.js':JS}
    items=''.join(f'<li><a href="ch{c["number"]:03}.html">{c["number"]}. {E(c["title"])}</a>'+(' <span class="badge">未訳箇所あり</span>' if c['markers'] else '')+'</li>' for c in chapters)
    result['index.html']=shell('紅楼夢・前八十回 日本語','index.html',f'<h1>紅楼夢・前八十回</h1><p class="notice">{NOTICE}</p><label for="toc-search">回番号・回目を検索</label><input id="toc-search" type="search"><p id="search-count" role="status">80回を表示</p><ol class="toc">{items}</ol>')
    gaps=(f'<p>未訳箇所のある回は、第{"・".join(str(n) for n in sorted(PARTIAL))}回です。印のある位置の本文は未収録です。本版は無削除の完訳ではありません。</p>' if PARTIAL else '')
    result['edition.html']=shell('日本語版について','edition.html',f'<h1>日本語版について</h1><p>{NOTICE}</p>{gaps}<p>{BOUNDARY}</p>')
    for c in chapters:
        n=c['number']; filename=f'ch{n:03}.html'
        nav='<nav class="chapter-nav" aria-label="回の移動">'+(f'<a href="ch{n-1:03}.html">← 第{n-1}回</a>' if n>1 else '')+'<a href="index.html">回目一覧</a>'+(f'<a href="ch{n+1:03}.html">第{n+1}回 →</a>' if n<80 else '<a href="/originals/hongloumeng/ja/ch081.html">独自続編・第81回 →</a>')+'</nav>'
        notice='<aside class="notice">この回には作者の補訳待ちの箇所があります。 '+ ' '.join(f'<a href="#{m}">{m}</a>' for m in c['markers'])+'</aside>' if c['markers'] else ''
        controls='<div aria-label="文字サイズ"><button data-size="-1" aria-label="文字を小さく">小</button> <button data-size="reset" aria-label="文字サイズを戻す">標準</button> <button data-size="1" aria-label="文字を大きく">大</button></div>'
        result[filename]=shell(c['title'],filename,f'<h1>{E(c["title"])}</h1>{nav}{notice}{controls}<article>{c["body"]}</article>'+ (f'<aside class="notice">{BOUNDARY}</aside>' if n==80 else '')+nav)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'classics/hongloumeng/ja');a=p.parse_args()
    plan=render(load_chapters(source=SOURCE))
    output=a.output.absolute()
    if any(p.is_symlink() for p in (output,*output.parents)):raise ValueError('Symlink output directory')
    a.output.mkdir(parents=True,exist_ok=True)
    for name,body in plan.items():
        dest=a.output/name
        if dest.is_symlink() or (dest.exists() and dest.stat().st_nlink!=1):raise ValueError('Unsafe output')
        dest.write_text(body)
    print(f'Wrote {len(plan)} Japanese reader files; {OWNER_SLOTS} explicit incomplete placeholders retained')
if __name__=='__main__':main()
