#!/usr/bin/env python3
"""Read-only checks for hand-edited French HTML; never regenerates prose."""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
class Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks=[]; self.current=None; self.meta={}; self.links=[]; self.lang=None
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='html': self.lang=a.get('lang')
        if tag=='meta' and a.get('name'): self.meta[a['name']]=a.get('content')
        if tag in ('a','link') and a.get('href'): self.links.append(a['href'])
        if tag=='script' and a.get('src'): self.links.append(a['src'])
        if tag=='p' and 'data-source-block' in a:
            assert self.current is None, 'nested source blocks'
            self.current={'id':int(a['data-source-block']),'kind':a.get('class',''),'text':''}
    def handle_data(self,text):
        if self.current is not None:self.current['text']+=text
    def handle_endtag(self,tag):
        if tag=='p' and self.current is not None:
            self.blocks.append(self.current);self.current=None

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--through',type=int,required=True)
    a=p.parse_args()
    source=json.loads((ROOT/'data/hongloumeng/first80-public/reading.zh.json').read_text())
    total=0
    for n in range(1,a.through+1):
        path=ROOT/f'classics/hongloumeng/fr/ch{n:03d}.html'
        raw=path.read_text(encoding='utf-8');doc=Reader();doc.feed(raw)
        c=source['chapters'][n-1]
        assert doc.lang=='fr',(n,'lang')
        assert len(doc.blocks)==len(c['blocks']),(n,'block count',len(doc.blocks),len(c['blocks']))
        assert [b['id'] for b in doc.blocks]==list(range(1,len(c['blocks'])+1)),(n,'block order')
        for b,s in zip(doc.blocks,c['blocks']):
            assert b['text'].strip(),(n,b['id'],'empty')
            if s['kind']=='verse':assert 'verse' in b['kind'],(n,b['id'],'verse boundary')
        for link in doc.links:
            if link.startswith(('https:','http:','mailto:','#')):continue
            target=link.split('#')[0].split('?')[0]
            if not target:continue
            dest=ROOT/target.lstrip('/') if target.startswith('/') else path.parent/target
            assert dest.exists(),(n,'broken local link',link)
        assert '\ufffd' not in raw,(n,'replacement character')
        total+=len(doc.blocks)
        print(f'Chapter {n}: {len(doc.blocks)} source blocks; structure and local links PASS')
    print(f'PASS: {a.through} chapters, {total} blocks. Structural checks are not literary review.')
if __name__=='__main__':main()
