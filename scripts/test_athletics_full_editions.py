#!/usr/bin/env python3
"""Verify full text, provenance, targeted source changes and stable URLs."""
import html
import json
import re
import subprocess
from urllib.parse import urlsplit, unquote
from build_athletics_full_editions import ROOT, SERIES, DATA, RECEIPT, LANGS, sha, copies, output_pages, plain

r=json.loads(RECEIPT.read_text())
assert len(r['archives'])==23 and len(r['manuscripts'])==115
for name,digest in r['plans'].items():assert sha((DATA/name).read_bytes())==digest,name
corrections={c['path']:c for c in r['source_corrections']}
for rel,digest in r['protected_files'].items():
    path=ROOT/rel
    baseline=subprocess.check_output(['git','show',r['baseline_commit']+':'+rel],cwd=ROOT)
    assert sha(baseline)==digest
    if rel not in corrections:assert sha(path.read_bytes())==digest,rel
    else:
        c=corrections[rel];assert sha(path.read_bytes())==c['after_sha256']
        assert digest==c['before_sha256']
        old=baseline.decode()
        if 'edits' in c:
            for e in c['edits']:
                assert old.count(e['before'])==1,(rel,e)
                old=old.replace(e['before'],e['after'],1)
            assert old==path.read_text(),rel
        else:
            extract=lambda t:json.loads(re.search(r'var variants = (\{.*?\});\s*\n\s*var originals',t,re.S)[1])
            pairs=extract(old)
            for before,after,hant in c['traditional_pairs']:pairs.pop(before,None);pairs[after]=hant
            assert pairs==extract(path.read_text()),rel
            assert all(after!=hant or not re.search('[这为个体]',after) for _,after,hant in c['traditional_pairs'])
all_copies=copies();sitemap=(ROOT/'sitemap.xml').read_text()
search={l:{e['u']:e for e in json.loads((ROOT/f'data/search/{l}.json').read_text())['records']} for l in LANGS}
for path,expected in output_pages().items():
    text=path.read_text();assert text==expected,path
    assert text.count('id="athletics-full-style"')==1
    assert text.count('src="../../../language-select.js"')==1
    assert '<header class="essay-header">' not in text
    ids=re.findall(r'\bid="([^"]+)"',text);assert len(ids)==len(set(ids)),path
    for href in re.findall(r'href="([^"]+)"',text):
        u=urlsplit(html.unescape(href))
        if u.scheme or u.netloc:continue
        if u.path:
            target=(ROOT/u.path.lstrip('/')) if u.path.startswith('/') else path.parent/unquote(u.path)
            assert target.exists(),(path,href)
        elif u.fragment:assert u.fragment in ids,(path,href)
    lang=path.parent.name
    if path.stem=='index':
        assert len(re.findall(r'class="entry-row"',text))==23
        continue
    copy=all_copies[path.stem+'.'+lang]
    assert plain(re.search(r'<h1[^>]*>(.*?)</h1>',text,re.S)[1])==copy['title']
    assert plain(re.search(r'<p class="essay-subtitle">(.*?)</p>',text,re.S)[1])==copy['deck']
    assert copy['body'] in text
    assert text.count('class="athletics-toc"')==1
    assert text.count('<p>')>=sum(copy['paragraphs_by_section'])
    assert len(re.findall(r'<h2 id="section-',text))==len(copy['paragraphs_by_section'])
    assert 'rel="canonical" href="https://nondubito.net/'+path.relative_to(ROOT).as_posix()+'"' in text
    assert 'https://nondubito.net/'+path.relative_to(ROOT).as_posix() in sitemap
    record=search[lang][path.relative_to(ROOT).as_posix()]
    assert copy['title'] in json.dumps(record,ensure_ascii=False)
assert sum(sum(c['paragraphs_by_section']) for c in all_copies.values())==2145*5
print('OK: 115 complete texts; 10,725 paragraphs; protected sources, Hant, metadata, local links, search and sitemap')
