"""Canonical edited Markdown plus the complete original published apparatus.

No duplicate Chinese corpus. Fail on a changed renderer/block or source-note
layout rather than silently omitting a qualification or extra reference.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urljoin
from prepare_action_sources import Document, Node, one

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/aesthetics'
DIRECTORY=ROOT/'essays/aesthetics'
ORIGIN='https://nondubito.net/essays/aesthetics/'
SLUGS=['seeing-beauty',*[f'ray{n:02d}' for n in range(1,14)]]


def load_article(spec,slug):
    assert spec['directory']=='essays/aesthetics' and slug in SLUGS
    stem='guide' if slug=='seeing-beauty' else slug
    units=(BASE/(stem+'-zh.md')).read_text().strip().split('\n\n')
    assert all(p.strip() and not p.startswith(('# ', '### ', '> ', '- ')) for p in units)
    document=Document((DIRECTORY/(slug+'.html')).read_text())
    body=one(document.root.walk(),lambda n:n.tag=='article' and n.has('prose'),(slug,'body'))
    children=[n for n in body.children if isinstance(n,Node)]
    assert len(children)==len(units)
    for block,unit in zip(children,units):
        assert block.tag==('h2' if unit.startswith('## ') else 'p')
        assert all(isinstance(c,str) for c in block.children)
        assert block.text()==(unit[3:] if unit.startswith('## ') else unit)
    note=one(document.root.walk(),lambda n:n.tag=='aside' and n.has('source-note'),(slug,'apparatus'))
    blocks=[n for n in note.children if isinstance(n,Node)]
    assert blocks[0].tag=='h2' and all(n.tag=='p' for n in blocks[1:])
    first=blocks[1]
    assert all(isinstance(c,str) for c in first.children)
    notes=[first.text()]
    sources=[]
    for block in blocks[2:]:
        links=[n for n in block.children if isinstance(n,Node)]
        assert len(links)==1 and links[0].tag=='a'
        assert all(not c.strip() for c in block.children if isinstance(c,str))
        link=links[0];assert all(isinstance(c,str) for c in link.children)
        sources.append({'title':link.text(),'url':urljoin(ORIGIN,link.attrs['href'])})
    assert sources and all(s['title'].strip() and s['url'].startswith('https://') for s in sources)
    if slug!='seeing-beauty':
        metadata=json.loads((BASE/'rays.json').read_text())[int(slug[-2:])-1]
        assert metadata['slug']==slug and metadata['note_zh']==notes[0]
    title=one(document.root.walk(),lambda n:n.tag=='h1',(slug,'title')).text()
    deck=one(document.root.walk(),lambda n:n.tag=='p' and n.has('deck'),(slug,'deck')).text()
    return {'slug':slug,'title_zh':title,'deck_zh':deck,'body_zh':units,
            'aside_zh':None,'notes_zh':notes,'sources_zh':sources,
            'source_url':sources[0]['url']}


def source_digest(spec,slug):
    stem='guide' if slug=='seeing-beauty' else slug
    raw=(BASE/(stem+'-zh.md')).read_bytes()
    metadata=(BASE/'rays.json').read_bytes()
    bundle=json.dumps(load_article(spec,slug),ensure_ascii=False,sort_keys=True).encode()
    data=b'aesthetics-edited-source\0'+len(raw).to_bytes(8,'big')+raw
    data+=len(metadata).to_bytes(8,'big')+metadata+bundle
    return hashlib.sha256(data).hexdigest()
