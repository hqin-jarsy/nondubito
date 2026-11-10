#!/usr/bin/env python3
"""Structural guards for War manuscripts, never a semantic certification."""
from __future__ import annotations
if not __debug__:
    raise RuntimeError('Optimized Python is not supported: manuscript checks require assertions')
import argparse,json,re
from prepare_war_sources import BASE,SLUGS,LANGS
from prepare_action_sources import Document,Node

def read(p):return json.loads(p.read_text())
def structure(unit):return [(n.tag,dict(n.attrs)) for n in Document(unit).root.walk() if n.tag not in ('strong','em')]
def unit_check(source,target,label):
    assert isinstance(target,str) and Document(target).root.text().strip(),(label,'empty text')
    assert structure(source)==structure(target),(label,'HTML tags/attributes differ')
    for tag in ('strong','em'):assert source.count('<'+tag+'>')==target.count('<'+tag+'>'),(label,'emphasis',tag)
    assert re.findall(r'\d{1,2}DD',source)==re.findall(r'\d{1,2}DD',target),(label,'DD references')
    assert source.count('Self-as-an-End')==target.count('Self-as-an-End'),(label,'canonical name')
    assert not re.search(r'\[VERIFY|TODO|TBD|PLACEHOLDER',target),(label,'placeholder')
def load(lang,slug):
    data=read(BASE/'translations'/lang/(slug+'.json'));source=read(BASE/'sources'/(slug+'.json'))
    assert data['language']==lang and data['slug']==slug,(lang,slug,'identity')
    assert data['source_sha256']==source['source_sha256'],(lang,slug,'source hash')
    assert data.get('title') and data.get('deck') and data.get('review'),(lang,slug,'metadata')
    assert len(data['body'])==len(source['body_zh']),(lang,slug,'unit coverage')
    for i,(s,t) in enumerate(zip(source['body_zh'],data['body']),1):unit_check(s,t,(lang,slug,i))
    return data

def load_index(lang):
    data=read(BASE/'translations'/lang/'index.json');source=read(BASE/'index-source.json')
    assert data['language']==lang and data['source_sha256']==source['source_sha256'],(lang,'index identity/source')
    assert data.get('title') and data.get('source_note') and data.get('review'),(lang,'index metadata')
    assert len(data['intro'])==len(source['intro_zh'])==5,(lang,'index intro coverage')
    for i,(s,t) in enumerate(zip(source['intro_zh'],data['intro']),1):unit_check(s,t,(lang,'index intro',i))
    assert len(data['groups'])==len(source['groups'])==2,(lang,'index groups')
    for i,(s,t) in enumerate(zip(source['groups'],data['groups']),1):
        for key in ('eyebrow','title','note'):
            unit_check(s['zh'][key],t[key],(lang,'index group',i,key))
    return data

def main():
    p=argparse.ArgumentParser();p.add_argument('--language',choices=LANGS);p.add_argument('--slug',choices=(*SLUGS,'index'));p.add_argument('--all',action='store_true');a=p.parse_args()
    checked=0
    for lang in ([a.language] if a.language else LANGS):
        for slug in ([a.slug] if a.slug else (*SLUGS,'index')):
            path=BASE/'translations'/lang/(slug+'.json')
            if not path.exists():
                if a.all or a.slug:raise FileNotFoundError(path)
                continue
            (load_index(lang) if slug=='index' else load(lang,slug));checked+=1
    print('Structural checks:',checked,'manuscripts; semantic review is separate.')
if __name__=='__main__':main()
