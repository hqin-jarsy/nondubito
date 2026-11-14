#!/usr/bin/env python3
"""Publish a reviewed five-chapter Korean batch locally; never rewrites prose."""
import argparse
import html
import json
import re
from pathlib import Path
from integrate_hongloumeng_korean import transform, reverse
from web_analytics import tracked_html, ensure_analytics
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'classics/hongloumeng/ko'
PROGRESS = ROOT / 'data/hongloumeng/first80-korean/progress.json'
LANGS = [('zh-Hans','../','简体中文'),('zh-Hant','../zh-hant/','繁體中文'),('en','../en/','English'),('ja','../ja/','日本語'),('fr','../fr/','Français'),('de','../de/','Deutsch'),('es','../es/','Español'),('ko','','한국어')]
@tracked_html
def shell(name,title,body):
    nav=''.join(f'<a lang="{lang}" href="{prefix}{name}"'+(' aria-current="page"' if lang=='ko' else '')+f'>{label}</a>' for lang,prefix,label in LANGS)
    text=f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — Non Dubito</title><meta name="description" content="홍루몽 전80회 · 이 프로젝트의 교정된 중국어 본문을 바탕으로 한 한국어 번역"><link rel="canonical" href="https://nondubito.net/classics/hongloumeng/ko/{name}"><link rel="stylesheet" href="reader.css"><script defer src="reader.js"></script></head><body><a class="skip" href="#main">본문으로 건너뛰기</a><header><a href="/">Non Dubito</a><nav><a href="index.html">목차</a><a href="edition.html">이 판본에 관하여</a><a href="/search.html?ui=ko&amp;in=ko">검색</a></nav><nav class="language-switch" aria-label="언어">{nav}</nav></header><main id="main">{body}</main><footer>홍루몽 · 한국어 번역</footer></body></html>'''
    return text
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--through',type=int,required=True);p.add_argument('--attenuated',type=int,nargs='*',default=[]);a=p.parse_args()
    last=a.through
    assert 5<=last<=80 and last%5==0
    previous=json.loads(PROGRESS.read_text())['reviewed_through'] if PROGRESS.exists() else 0
    assert last in (previous,previous+5), 'Only one reviewed batch at a time'
    assert (ROOT/f'docs/hongloumeng/translation/korean-review-{last-4:03}-{last:03}.md').is_file(), 'Review report missing'
    titles=[]
    for n in range(1,last+1):
        path=DEST/f'ch{n:03}.html';s=path.read_text();m=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S);assert m
        titles.append(html.unescape(re.sub('<[^>]+>','',m[1])))
    body=f'<h1>홍루몽</h1><p>조설근의 전80회 · 한국어 번역</p><p>현재 제1회부터 제{last}회까지 번역과 중한 대조 검토를 마쳤습니다.</p>'
    if a.attenuated:
        numbers='·'.join(map(str,a.attenuated));body+=f'<p>제{numbers}회의 일부 구체적인 성적 표현은 비노골적으로 옮겼습니다. 사건의 흐름과 인물 관계, 거부와 강압은 유지했습니다. 이 처리는 세부를 모두 그대로 옮긴 직역과는 다릅니다.</p>'
    body+='<label for="toc-search">회차 또는 제목 검색</label><input id="toc-search" type="search" placeholder="회차 또는 제목"><p id="search-count" role="status">'+str(last)+'개 회차 표시</p>'
    for start in range(1,last+1,5):
        body+=f'<section id="batch{(start-1)//5+1:02}"><h2>제{start}–{start+4}회</h2><ol class="toc">'
        for n in range(start,start+5):
            title=html.escape(titles[n-1]);badge=' <span class="badge">일부 비노골적 표현</span>' if n in a.attenuated else ''
            body+=f'<li data-search="{n} {title}"><a href="ch{n:03}.html">{title}</a>{badge}</li>'
        body+='</ol></section>'
    body+='<p><a href="edition.html">이 번역과 저본에 관하여</a></p><p><a href="/originals/hongloumeng/ko/index.html">진한(秦漢)의 창작 속편 제81–85회 읽기</a></p>'
    (DEST/'index.html').write_text(shell('index.html','홍루몽 · 목차',body))
    edition='''<h1>이 판본과 번역에 관하여</h1><p>이 한국어 번역은 이 프로젝트에서 교정하고 저자가 판정을 마친 중국어 전80회 본문을 직접 저본으로 삼았습니다. 다른 언어 번역을 다시 옮긴 것이 아닙니다.</p><p>인명과 호칭, 이야기의 문체는 이 사이트의 한국어 창작 속편 제81–85회 현행 본문을 기준으로 맞추었습니다. 시와 대련은 원문의 뜻과 이미지, 행 구분을 살리고 한국어에서 억지로 운을 맞추지 않았습니다. 옛 화폐와 날짜, 생활 풍속을 임의로 현대의 수치로 바꾸지 않았습니다.</p><p>다섯 회마다 중국어와 한국어를 대조하고 검토한 범위와 남은 사항을 기록합니다. 문단 번호와 구조 검사는 의미와 문체의 검토를 대신하지 않습니다. 번역 본문은 각 회차의 HTML에 직접 들어 있어 수정할 수 있습니다.</p><p>일부 구체적인 성적 표현을 비노골적으로 처리한 회차는 목차에서 따로 표시합니다. 사건과 인물 관계, 거부와 강압은 보존하되 세부를 완전히 그대로 옮겼다고 주장하지 않습니다. 일반적인 성인 서사와 비노골적인 내용은 생략하지 않습니다.</p><p>제1–80회는 조설근의 작품이며, 제81–85회는 진한(秦漢)의 창작 속편입니다. 두 부분의 저자를 혼동하지 않도록 나누어 싣습니다.</p><p><a href="index.html">목차로 돌아가기</a></p>'''
    (DEST/'edition.html').write_text(shell('edition.html','홍루몽 · 이 판본에 관하여',edition))
    for lang in ['', 'zh-hant','en','ja','fr','de','es']:
        base=ROOT/'classics/hongloumeng'/lang
        for name in ['index.html','edition.html']+[f'ch{n:03}.html' for n in range(1,last+1)]:
            path=base/name;old=path.read_text();relative=path.relative_to(ROOT).as_posix();new=transform(relative,old)
            assert reverse(relative,new)==(reverse(relative,old) if '<!-- KOREAN-NAV:START -->' in old else old)
            if new!=old:path.write_text(new)
    # Only completed Korean chapters receive adjacent-chapter links.
    for n in range(1,last+1):
        path=DEST/f'ch{n:03}.html';old=path.read_text()
        nav='<nav class="chapter-nav" aria-label="회차 이동">'
        if n>1:nav+=f'<a rel="prev" href="ch{n-1:03}.html">← 제{n-1}회</a>'
        nav+='<a href="index.html">목차</a>'
        if n<last:nav+=f'<a rel="next" href="ch{n+1:03}.html">제{n+1}회 →</a>'
        elif n==80:nav+='<a href="/originals/hongloumeng/ko/ch081.html">창작 속편 제81회 →</a>'
        nav+='</nav>'
        new,count=re.subn(r'<nav\b[^>]*class="chapter-nav"[^>]*>.*?</nav>',nav,old,flags=re.S)
        assert count>=1, ('Missing chapter navigation',n)
        # Unify only reader chrome, never the hand-edited article or its notes.
        heading=re.search(r'<h1[^>]*>(.*?)</h1>',new,re.S)[1]
        title=html.unescape(re.sub('<[^>]+>','',heading))
        new=re.sub(r'<title>.*?</title>', '<title>'+html.escape(title)+' — Non Dubito</title>',new,count=1,flags=re.S)
        # Copied chapter shells may retain another chapter's metadata.
        new=re.sub(r'<meta\b[^>]*name="description"[^>]*>', '', new, flags=re.I)
        new=re.sub(r'<link\b[^>]*rel="canonical"[^>]*>', '', new, flags=re.I)
        if 'name="description"' not in new:new=new.replace('</head>',f'<meta name="description" content="홍루몽 제{n}회 · 교정 중국어 본문에서 옮긴 한국어 번역"></head>',1)
        if 'rel="canonical"' not in new:new=new.replace('</head>',f'<link rel="canonical" href="https://nondubito.net/classics/hongloumeng/ko/ch{n:03}.html"></head>',1)
        if 'name="author"' not in new:new=new.replace('</head>','<meta name="author" content="조설근"></head>',1)
        language_nav='<nav class="language-switch" aria-label="언어">'+''.join(f'<a lang="{lang}" href="{prefix}ch{n:03}.html"'+(' aria-current="page"' if lang=='ko' else '')+f'>{label}</a>' for lang,prefix,label in LANGS)+'</nav>'
        new,count=re.subn(r'<nav\b[^>]*class="language-switch"[^>]*>.*?</nav>',language_nav,new,count=1,flags=re.S)
        if count==0:
            # Early drafts may have a bare single-language nav or no language bar.
            bare=r'<nav><a href="\.\./ch\d{3}\.html">.*?</a></nav>'
            new,count=re.subn(bare,lambda m:language_nav,new,count=1,flags=re.S)
            if count==0:new=new.replace('<body>','<body>'+language_nav,1)
        new=re.sub(r'href="(?:\.\./)?reader\.css"','href="reader.css"',new)
        new=re.sub(r'src="(?:\.\./)?reader\.js"','src="reader.js"',new)
        new=ensure_analytics(new)
        if 'class="skip"' not in new:new=new.replace('<body>','<body><a class="skip" href="#main">본문으로 건너뛰기</a>',1)
        if 'data-size=' not in new:
            new=re.sub(r'(<article\b[^>]*>)',lambda m:'<div aria-label="글자 크기"><button data-size="-1" aria-label="글자 줄이기">A−</button> <button data-size="reset" aria-label="기본 글자 크기">A</button> <button data-size="1" aria-label="글자 키우기">A+</button></div>'+m[1],new,count=1)
        if new.count('class="chapter-nav"')==1:new=new.replace('</main>',nav+'</main>',1)
        if n in a.attenuated and '<!-- KOREAN-ADAPTATION:START -->' not in new:
            note='<!-- KOREAN-ADAPTATION:START --><aside class="notice"><h2>번역에 관한 안내</h2><p>이 회의 일부 구체적인 성적 표현은 비노골적으로 옮겼습니다. 사건의 흐름, 인물 관계와 강압·거부는 유지했습니다. 세부까지 모두 그대로 옮긴 직역과는 다릅니다. <a href="edition.html">이 판본에 관하여</a></p></aside><!-- KOREAN-ADAPTATION:END -->'
            new=new.replace('</article>','</article>'+note,1)
        if new!=old:path.write_text(new)
    # Bounded entry links do not touch the Chinese, traditional or English copy.
    for relative in ['essays/literature/hlm/index.html','essays/literature/hlm/zh-hant/index.html','essays/literature/hlm/en/index.html']:
        path=ROOT/relative;old=path.read_text()
        block=f'<!-- KOREAN-ENTRY:START --><a href="/classics/hongloumeng/ko/index.html" lang="ko">한국어 · 1–{last}</a><!-- KOREAN-ENTRY:END -->'
        if '<!-- KOREAN-ENTRY:START -->' in old:new=re.sub(r'<!-- KOREAN-ENTRY:START -->.*?<!-- KOREAN-ENTRY:END -->',block,old,flags=re.S)
        else:
            assert '<!-- SPANISH-ENTRY:END -->' in old
            new=old.replace('<!-- SPANISH-ENTRY:END -->','<!-- SPANISH-ENTRY:END -->'+block,1)
        if new!=old:path.write_text(new)
    path=ROOT/'originals/hongloumeng/ko/index.html';old=path.read_text()
    if '<!-- KOREAN-FIRST80:START -->' not in old:
        block='<div><!-- KOREAN-FIRST80:START --><a href="/classics/hongloumeng/ko/index.html">조설근의 전80회 한국어 번역 읽기</a><!-- KOREAN-FIRST80:END --></div>'
        assert '</main>' in old
        path.write_text(old.replace('</main>',block+'</main>',1))
    PROGRESS.parent.mkdir(parents=True,exist_ok=True)
    PROGRESS.write_text(json.dumps(dict(reviewed_through=last,basis='Current edited Chinese HTML; independent Korean translation',format='Directly editable HTML',chapters_with_placeholders=[],chapters_with_attenuated_passages=a.attenuated),ensure_ascii=False,indent=2)+'\n')
    print(f'Korean reviewed batch through {last}; reversible navigation and contents updated. Search requires a separate refresh.')
if __name__=='__main__':main()
