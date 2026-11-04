#!/usr/bin/env python3
"""Normalize existing Chinese companions without changing their primary sources."""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def clean(text):
    text=re.sub(r'<em>(.*?)</em>',r'*\1*',text,flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>','',text)).strip()


def render():
    original=ROOT/'data/method-introduction/zh.json'
    source=json.loads(original.read_text())
    body=list(source['intro'])
    for section in source['sections']:
        body.extend(['## '+section['heading'],*section['paragraphs']])
        body.extend(f'{i}. {text}' for i,text in enumerate(section.get('items',[]),1))
        body.extend(section.get('after',[]))
    method={'slug':'00e','title_zh':source['title'],'deck_zh':source['subtitle'],
            'body_zh':body,'source_note_zh':source['reading_note'],
            'source_url':'https://self-as-an-end.net/papers/sae-methodology-00e.html',
            'source_input':{'path':str(original.relative_to(ROOT)),'sha256':hashlib.sha256(original.read_bytes()).hexdigest()}}
    path=ROOT/'essays/sae-foundations/remainder-and-subject.html'
    text=path.read_text()
    article=re.search(r'<article class="bridge-body lang-zh">(.*?)</article>',text,re.S)[1]
    units=[]
    pattern=r'<(?P<tag>h2|p|blockquote)\b[^>]*>(?P<text>.*?)</(?P=tag)>|<div class="bridge-rung"><strong>(?P<label>\d{2}DD)</strong><span>(?P<definition>.*?)</span></div>'
    for m in re.finditer(pattern,article,re.S):
        if m['label']:units.append('**'+m['label']+'** '+clean(m['definition']))
        else:units.append({'h2':'## ','blockquote':'> ','p':''}[m['tag']]+clean(m['text']))
    assert len(units)==19
    bridge={'slug':'remainder-and-subject','title_zh':clean(re.search(r'<h1 class="lang-zh">(.*?)</h1>',text,re.S)[1]),
            'deck_zh':clean(re.search(r'<p class="bridge-deck lang-zh">(.*?)</p>',text,re.S)[1]),
            'body_zh':units,
            'source_note_zh':'本篇是既有中文入门桥梁的其他语言独立重写，不是新写一套主体性定义。保留石头与软件的区别、作者位置不等于完全控制、囚犯仍是主体，以及13DD至16DD的原有范围。来源链接通向中文底本；完整论文可从原页的理论深潜入口继续阅读。',
            'source_url':'https://nondubito.net/essays/sae-foundations/remainder-and-subject.html?lang=zh',
            'source_input':{'path':str(path.relative_to(ROOT)),'chinese_body_sha256':hashlib.sha256(article.encode()).hexdigest()}}
    return {ROOT/'data/method-companion/00e.json':method,ROOT/'data/foundations-companion/remainder-and-subject.json':bridge}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for path,value in render().items():
        text=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
        if args.check:assert path.read_text()==text,path
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        print(path.relative_to(ROOT),len(value['body_zh']),'source units')


if __name__=='__main__':main()
