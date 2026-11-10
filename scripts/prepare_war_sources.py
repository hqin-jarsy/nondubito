#!/usr/bin/env python3
"""Freeze the locally checked War Theory originals without changing public pages."""
from __future__ import annotations
if not __debug__:
    raise RuntimeError("Optimized Python is not supported: source capture requires safety assertions")
import hashlib,json,re,subprocess
from pathlib import Path
from prepare_action_sources import Document,Node,one
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/war-full';DIRECTORY=ROOT/'essays/war'
SLUGS=(*(f'ep{i:02d}' for i in range(1,8)),*(f'if{i:02d}' for i in range(1,9)),'if-conclusion')
LANGS=('ja','de','fr','es','ko')
COUNTS=(60,54,61,70,98,102,84,69,85,79,66,62,68,66,57,40)
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def file_sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalized_legacy_head(text):
    # Nine interface originals contain eight consecutive closing head tags.
    # This bounded parsing repair changes no body bytes; retain raw page hashes.
    return re.sub(r'(?:</head>){2,}','</head>',text)
def main():
    index_raw=(DIRECTORY/'index.html').read_text();idx=Document(index_raw)
    cards={n.attrs['href'].removesuffix('.html'):n for n in idx.root.walk() if n.has('entry-row')}
    assert set(cards)==set(SLUGS)
    outputs={};pres={'series':'war','initial_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_bodies':{},'traditional_files':{},'legacy_head_closures':{}}
    english={};kinds={}
    for slug,count in zip(SLUGS,COUNTS):
        raw=(DIRECTORY/(slug+'.html')).read_text();doc=Document(normalized_legacy_head(raw));source={'slug':slug}
        for lang in ('zh','en'):
            node=one(doc.root.walk(),lambda n:n.has('essay-body','lang-'+lang),(slug,lang));body=doc.raw(node,inner=True)
            assert body in raw,(slug,lang,'body changed by parsing normalization')
            units=[doc.raw(n) for n in node.children if isinstance(n,Node)];assert len(units)==count
            source['body_'+lang]=units
            source['title_'+lang]=one(doc.root.walk(),lambda n:n.tag=='h1' and n.has('lang-'+lang),(slug,lang,'title')).text()
            source['deck_'+lang]=one(cards[slug].walk(),lambda n:n.has('entry-desc','lang-'+lang),(slug,lang,'deck')).text()
            source['source_sha256' if lang=='zh' else 'english_sha256']=sha(body)
            if lang=='en':english[slug]=body
            else:
                for n in node.children:
                    if isinstance(n,Node):kinds[n.tag]=kinds.get(n.tag,0)+1
        pres['source_bodies'][slug]={'sha256':source['source_sha256'],'units':count,'english_sha256':source['english_sha256'],'english_units':count}
        if raw.count('</head>')!=1:pres['legacy_head_closures'][slug]=raw.count('</head>')
        outputs[BASE/'sources'/(slug+'.json')]=source
    index={'source_sha256':sha(index_raw),'cards':{},'groups':[]}
    for lang in ('zh','en'):
        index['title_'+lang]=one(idx.root.walk(),lambda n:n.tag=='h1' and n.has('lang-'+lang),lang).text()
        intro=one(idx.root.walk(),lambda n:n.has('series-desc','lang-'+lang),lang)
        index['intro_'+lang]=[idx.raw(n) for n in intro.children if isinstance(n,Node)]
        index['source_notes_'+lang]=[idx.raw(n) for n in idx.root.walk() if n.tag=='span' and n.has('lang-'+lang) and any(n is x for parent in idx.root.walk() if parent.has('source-note') for x in parent.children)]
    for node in idx.root.walk():
        if node.has('group-head'):
            group={}
            for lang in ('zh','en'):
                group[lang]={key:idx.raw(one(node.walk(),lambda n:n.has(css,'lang-'+lang),(key,lang)),inner=True) for key,css in [('eyebrow','group-eyebrow'),('title','group-title'),('note','group-note')]}
            index['groups'].append(group)
    for slug,node in cards.items():index['cards'][slug]={lang:{'title':one(node.walk(),lambda n:n.has('entry-title-'+lang),(slug,lang)).text(),'deck':one(node.walk(),lambda n:n.has('entry-desc','lang-'+lang),(slug,lang)).text()} for lang in ('zh','en')}
    outputs[BASE/'index-source.json']=index
    pres['unit_total']=sum(COUNTS);pres['unit_types']=kinds
    pres['traditional_files']={str(p.relative_to(ROOT)):file_sha(p) for p in sorted((DIRECTORY/'zh-hant-data').glob('*.js'))}
    pages=list(DIRECTORY.rglob('*.html'));assert len(pages)==102
    outputs[BASE/'preservation.json']=pres;outputs[BASE/'baseline-pages.json']={str(p.relative_to(ROOT)):file_sha(p) for p in sorted(pages)};outputs[BASE/'english-baseline-bodies.json']=english
    serialized={p:json.dumps(d,ensure_ascii=False,indent=2)+'\n' for p,d in outputs.items()}
    for p,s in serialized.items():
        if p.exists():assert p.read_text()==s,('Existing source capture differs; do not overwrite',str(p))
    for p,s in serialized.items():
        p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():p.write_text(s)
    print('Captured 16 originals:',sum(COUNTS),'units;',kinds,'; 102 page baselines. No public page changed.')
if __name__=='__main__':main()
