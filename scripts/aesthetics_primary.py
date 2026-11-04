"""Reversible language routes around, never inside, the original reading areas."""
import html
import re

NAMES={'de':'Deutsch','fr':'Français','es':'Español','ja':'日本語','ko':'한국어'}
MARKERS=('AESTHETICS LANGUAGE LINKS','AESTHETICS ALTERNATES','AESTHETICS EDITION SCOPE')


def strip_additions(text):
    for name in MARKERS:
        start,end=f'<!-- {name} START -->',f'<!-- {name} END -->'
        if start in text:
            assert text.count(start)==text.count(end)==1,name
            text=re.sub(re.escape(start)+r'.*?'+re.escape(end),'',text,flags=re.S)
    return text


def upgrade(text,spec,slug):
    assert spec['id']=='aesthetics'
    text=strip_additions(text)
    language=re.search(r'<html\b[^>]*data-lang="([^"]+)"',text)[1]
    assert language in spec['primary_editions']
    up='' if language=='zh' else '../'
    match=re.search(r'(<details class="language-menu">.*?<nav\b[^>]*>)(.*?)(</nav></details>)',text,re.S)
    assert match and len(re.findall(r'data-edition="',match[2]))==3
    links=''.join(f'<a href="{up}{code}/{slug}.html" lang="{code}">{NAMES[code]}</a>' for code in spec['languages'])
    mark=MARKERS[0]
    replacement=match[1]+match[2]+f'<!-- {mark} START -->'+links+f'<!-- {mark} END -->'+match[3]
    text=text[:match.start()]+replacement+text[match.end():]
    origin='https://nondubito.net/'+spec['directory']+'/'
    suffix='' if slug=='index' else slug+'.html'
    assert len(re.findall(r'<link\b[^>]*rel="alternate"',text))==3
    alts='<link rel="alternate" hreflang="x-default" href="'+origin+suffix+'">'
    alts+=''.join(f'<link rel="alternate" hreflang="{code}" href="{origin}{code}/{suffix}">' for code in spec['languages'])
    mark=MARKERS[1]
    text=text.replace('</head>',f'<!-- {mark} START -->'+alts+f'<!-- {mark} END --></head>',1)
    labels={
        'zh':'总导读与十三条射线现有八语全文，可用上方菜单切换同一篇。日常记录保留原有语言；新增五语目录也提供艺术作品细读入口。',
        'zh-hant':'總導讀與十三條射線現有八語全文，可用上方選單切換同一篇。日常記錄保留原有語言；新增五語目錄也提供藝術作品細讀入口。',
        'en':'The opening essay and all thirteen rays now have eight complete language editions. Use the menu above to stay with the same essay. Daily entries retain their existing editions; the five new directories also link to the art readings.'}
    mark=MARKERS[2]
    notice=f'<!-- {mark} START --><aside class="edition-note" style="max-width:1120px;margin:1rem auto;padding:0 1.5rem">'+html.escape(labels[language])+f'</aside><!-- {mark} END -->'
    assert '<header class="aesthetics-header">' in text
    return text.replace('</header>','</header>'+notice,1)
