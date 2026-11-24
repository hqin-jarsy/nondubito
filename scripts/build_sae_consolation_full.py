#!/usr/bin/env python3
"""Restore the five complete Boethius editions without touching shared originals."""
import argparse
import hashlib
import html
import re

from build_collection_languages import ROOT
from build_epic_full_editions import within

SERIES = ROOT / "essays/sae-consolation"
DATA = ROOT / "data/sae-consolation-full"
LANGS = ("ja", "fr", "de", "es", "ko")
DATE = "2026-11-24"
EXPECTED = {f"{l}/ep{i:02}.{l}.md" for l in LANGS for i in range(1, 7)}

def inline(text):
    # The accepted plain Markdown sources use only asterisks for inline emphasis.
    pattern = re.compile(r"\*\*([^*]+)\*\*|\*([^*]+)\*")
    out = []
    end = 0
    for m in pattern.finditer(text):
        out.append(html.escape(text[end:m.start()], quote=False))
        tag = "strong" if m[1] else "em"
        out.append(f"<{tag}>{html.escape(m[1] or m[2], quote=False)}</{tag}>")
        end = m.end()
    out.append(html.escape(text[end:], quote=False))
    return "".join(out)

def shared_query(source):
    old = "  var saved=localStorage.getItem('nd_lang')"
    guard = "  var requested=new URLSearchParams(location.search).get('lang');"
    if guard in source:
        return source
    assert source.count(old)==1
    return source.replace(old, guard + "\n"
         "  if(['en','zh','zh-hant'].indexOf(requested)!==-1) localStorage.setItem('nd_lang',requested);\n"
         + old, 1)

def native_queries(source):
    # Onclick keeps the traditional same-tab behavior; explicit URLs also
    # select the intended edition for a new tab or a copied link.
    pattern = r"""(href="\.\./(?:index|ep0[1-6])\.html)(?:\?lang=(?:en|zh|zh-hant))?(" onclick="localStorage.setItem\('nd_lang','(en|zh|zh-hant)'\))"""
    output,n = re.subn(pattern, lambda m: m[1]+"?lang="+m[3]+m[2], source)
    assert n==3, n
    return output

def outputs():
    hashes = {name:digest for digest,name in (l.split() for l in
              (DATA/"MANIFEST.sha256").read_text().splitlines())}
    assert set(hashes)==EXPECTED
    result = {}
    for p in [SERIES/"index.html",*(SERIES/f"ep{i:02}.html" for i in range(1,7))]:
        result[p] = shared_query(p.read_text())
    for lang in LANGS:
        index = SERIES/lang/"index.html"
        result[index] = native_queries(index.read_text())
        for i in range(1,7):
            slug = f"ep{i:02}"
            relative = f"{lang}/{slug}.{lang}.md"
            data = (DATA/relative).read_bytes()
            assert hashlib.sha256(data).hexdigest()==hashes[relative], relative
            title, note, *pieces = data.decode().strip().split("\n\n")
            assert title.startswith("# ") and note.startswith("*") and note.endswith("*")
            assert sum(x.startswith("## ") for x in pieces)>=4 and len(pieces)>=34, relative
            assert all("\n" not in x and (not x.startswith("#") or x.startswith("## ")) for x in pieces), relative
            body = "\n".join(f"<h2>{inline(x[3:])}</h2>" if x.startswith("## ")
                             else f"<p>{inline(x)}</p>" for x in pieces)
            path = SERIES/lang/(slug+".html")
            source = path.read_text()
            current_title = html.unescape(re.search(r"<h1>(.*?)</h1>",source,re.S)[1])
            assert title[2:] == current_title, (relative,title,current_title)
            output = within(source,"essay-body",lambda _: "\n"+body+"\n")
            output = within(output,"essay-footer-note",lambda _:inline(note))
            result[path] = native_queries(output)
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check",action="store_true")
    check=ap.parse_args().check
    for path,text in outputs().items():
        if check: assert path.read_text()==text,path
        elif path.read_text()!=text: path.write_text(text)
    print(("Verified" if check else "Rendered"),"30 complete Boethius editions and 12 scoped route shells; original reading bodies untouched")

if __name__=="__main__": main()
