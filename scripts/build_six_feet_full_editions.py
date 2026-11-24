#!/usr/bin/env python3
"""Render the reviewed complete Six Feet Under editions over existing routes."""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re

from build_epic_full_editions import within
from build_content_registry import extract_localized_titles
from build_emperor_traditional import TextCollector, TraditionalConverter
from build_satc_full_editions import primary_body, replace_primary
from build_collection_languages import ROOT, LANGS

DATA = ROOT / "data/six-feet-under-full"
SERIES = ROOT / "essays/tv/six-feet-under"
SPEC = ROOT / "data/collection-languages/six-feet-under.json"
DATE = "2026-11-24"
ORIGIN = "https://nondubito.net/essays/tv/six-feet-under/"
SECTION_COUNTS = (6, 7, 6, 7, 7, 7, 7, 9, 7)
ZH_TITLE = ("每一集开头死一个人", "片头之前先死一个人")
EN_TITLE = ("A Death Before Every Opening", "A Death Before the Titles")
OLD_TITLES = {"ja":"毎回の冒頭で一人が死ぬ","fr":"Une mort avant chaque ouverture",
              "de":"Ein Tod vor jedem Anfang","es":"Una muerte antes de cada comienzo",
              "ko":"매회 시작 전에 한 사람이 죽는다"}
PHRASES = {
    "en": {
        "the death before every title sequence":"the death before the titles",
        "The series gives each stranger ninety seconds of life before a name and two dates.":"The series gives strangers a brief moment of ordinary life before a name and two dates.",
    },
    "zh": {
        "每集片头前的一次死亡":"多数集片头前的一次死亡",
        "每一集都先把一个普通时刻变成姓名与两个日期，然后把遗体送进菲舍":"多数集先把一个普通时刻变成姓名与两个日期，然后常把遗体送进菲舍",
        "每集片头前，先让一个人在普通生活里出现九十秒":"多数集片头前，先让一个人在普通生活里短暂出现",
    },
    "ja": {
        "毎回の冒頭で訪れる死":"冒頭で訪れる死",
        "見知らぬ人に九十秒の生活を与えてから、名前と二つの日付へ縮める。":"見知らぬ人の日常をひととき映したあと、名前と二つの日付へ縮める。",
    },
    "fr": {
        "La mort avant chaque générique":"La mort avant le générique",
        "La série donne à chaque inconnu quatre-vingt-dix secondes de vie avant de le réduire à un nom et deux dates.":"La série montre un bref moment de la vie ordinaire d’un inconnu avant de le réduire à un nom et deux dates.",
    },
    "de": {
        "Der Tod vor jedem Vorspann":"Der Tod vor dem Vorspann",
        "Jeder Fremde erhält neunzig Sekunden Leben, bevor Name und zwei Daten ihn verdichten.":"Die Serie zeigt einen kurzen Moment aus dem Alltag eines Fremden, bevor nur sein Name und zwei Daten bleiben.",
    },
    "es": {
        "La muerte antes de cada cabecera":"La muerte antes de la cabecera",
        "La serie da a cada desconocido noventa segundos de vida antes de reducirlo a nombre y dos fechas.":"La serie muestra un breve momento de la vida cotidiana de un desconocido antes de reducirlo a un nombre y dos fechas.",
    },
    "ko": {
        "매회 제목 전에 오는 죽음":"오프닝 크레디트 전에 오는 죽음",
        "낯선 사람에게 구십 초의 삶을 준 뒤 이름과 두 날짜로 줄인다.":"낯선 사람의 일상을 잠시 보여 준 뒤 이름과 두 날짜만 남긴다.",
    },
}
STYLE = """<style id="six-feet-full-style">
.collection-body p{margin:0 0 1.35em}
.collection-body h2{margin:2.6em 0 .8em}
.collection-body .edition-note,.essay-body .six-feet-note{font-size:.9rem;color:var(--ink-muted);margin:0 0 2.4em}
.essay-body .six-feet-note{border-bottom:1px solid var(--cream-border);padding-bottom:1.25em;font-family:var(--sans)}
.collection-page,.essay-page{overflow-wrap:anywhere}
html[lang="ja"] .collection-body,html[lang="ko"] .collection-body{font-family:var(--cjk),var(--serif),serif}
html[lang="ko"] .collection-body{word-break:keep-all}
</style>"""
LANG_OLD = "var saved=localStorage.getItem('nd_lang')"
LANG_NEW = ("var requested=new URLSearchParams(location.search).get('lang');\n"
            "  if(['en','zh','zh-hant'].indexOf(requested)!==-1) localStorage.setItem('nd_lang',requested);\n"
            "  var saved=localStorage.getItem('nd_lang')")
ALT = "six-feet-alternates"

def reviewed():
    required = {}
    for row in (DATA / "MANIFEST.sha256").read_text().splitlines():
        digest, name = row.split()
        assert re.fullmatch(r"(edited-zh|en|ja|fr|de|es|ko)/[0-9]{2}-[a-z-]+\.[a-z]+\.md", name)
        path = DATA / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
        required[name] = path.read_text()
    assert len(required) == 63
    return required

def inline(s):
    def fmt(m):
        a = m[0]
        if a.startswith("**"):
            return "<strong>"+html.escape(a[2:-2], quote=False)+"</strong>"
        if a.startswith("*"):
            return "<em>"+html.escape(a[1:-1], quote=False)+"</em>"
        return html.escape(a, quote=False)
    return "".join(fmt(m) for m in re.finditer(r"\*\*[^*]+\*\*|\*[^*]+\*|[^*]+|\*", s)) if "*" in s else html.escape(s, quote=False)

def manuscript(source, lang, n):
    units = source.strip().split("\n\n")
    title = None if lang == "zh" else units.pop(0).removeprefix("# ")
    note = units.pop(0)
    if lang == "zh":
        assert note.startswith("版本说明：")
    else:
        assert title and note.startswith("*") and note.endswith("*"), (lang, n, note)
    headings = [re.match(r"## (\d+.\d+) ", x)[1] for x in units if x.startswith("## ")]
    assert headings == [f"{n}.{i}" for i in range(1, SECTION_COUNTS[n-1]+1)], (lang, n, headings)
    assert all("\n" not in x for x in units), (lang, n, "unexpected multiline block")
    body = []
    for x in units:
        if x.startswith("## "):
            body.append(f"<h2>{inline(x[3:])}</h2>")
        else:
            body.append(f"<p>{inline(x)}</p>")
    note_html = "<strong>版本说明：</strong>" + inline(note.removeprefix("版本说明：")) if lang == "zh" else inline(note)
    return title, note_html, "\n".join(body)

def escaped_change(s, old, new):
    s = s.replace(old, new)
    for quote in (True, False):
        s = s.replace(html.escape(old, quote=quote), html.escape(new, quote=quote))
    return s

def alt_tags(filename):
    suffix = "" if filename == "index.html" else filename
    urls = {"x-default": ORIGIN+suffix, "en": ORIGIN+filename+"?lang=en",
            "zh-Hans": ORIGIN+filename+"?lang=zh", "zh-Hant": ORIGIN+filename+"?lang=zh-hant",
            **{lang: ORIGIN+lang+"/"+suffix for lang in LANGS}}
    return "<!-- "+ALT+" -->"+"".join(
        f'<link rel="alternate" hreflang="{lang}" href="{url}">' for lang, url in urls.items()
    )

def render(outputs=None):
    outputs = {} if outputs is None else dict(outputs)
    data = reviewed()
    spec = json.loads(SPEC.read_text())
    slugs = [item["slug"] for item in spec["items"]]
    chapter_one = {l: manuscript(data[f"{l}/{slugs[0]}.{l}.md"], l, 1)[0] for l in LANGS}
    converter = TraditionalConverter()
    result = {}
    try:
        for relative in ("", *LANGS):
            folder = SERIES / relative
            for filename in ["index.html", *(s+".html" for s in slugs)]:
                path = folder / filename
                original = path.read_text()
                s = outputs.get(path, original)
                slug = path.stem
                if relative:
                    # Compact cards/nav contain the old title; all other titles stay put.
                    s = escaped_change(s, OLD_TITLES[relative], chapter_one[relative])
                    for a,b in PHRASES[relative].items(): s = escaped_change(s,a,b)
                else:
                    # Keep queries meaningful when the corresponding page has this shared selector.
                    if LANG_NEW not in s:
                        assert LANG_OLD in s, path
                        s = s.replace(LANG_OLD, LANG_NEW, 1)
                    for a,b in [EN_TITLE, ZH_TITLE, *PHRASES["en"].items(), *PHRASES["zh"].items()]:
                        s = escaped_change(s,a,b)
                if slug != "index":
                    n = slugs.index(slug)+1
                    if relative:
                        title, note, body = manuscript(data[f"{relative}/{slug}.{relative}.md"],relative,n)
                        actual = re.search(r"<h1>(.*?)</h1>",s,re.S)[1]
                        # Old storefront and prose editions can spell some titles differently.
                        # Preserve storefront copy for all chapters except the approved ch. 1 fix.
                        assert n != 1 or html.unescape(actual) == title, (path,actual,title)
                        s = within(s,"collection-body",lambda _: f'<p class="edition-note">{note}</p>\n{body}')
                        s, num = re.subn(r"</div><p class=\"edition-note\"><em>.*?</em></p>(?=<nav class=\"collection-nav\">)", "</div>",s,count=1,flags=re.S)
                    else:
                        for lang, directory in (("en","en"), ("zh","edited-zh")):
                            title,note,body = manuscript(data[f"{directory}/{slug}.{lang}.md"],lang,n)
                            if lang=="en" and n == 1:
                                assert title==EN_TITLE[1]
                            s = replace_primary(s,lang,f'<p class="six-feet-note">{note}</p>\n{body}')
                s = re.sub(r'<!-- six-feet-alternates -->(?:<link rel="alternate" [^>]+>)+\n?', "", s)
                s = re.sub(r'<style id="six-feet-full-style">.*?</style>\n?', "", s, flags=re.S)
                s = s.replace("</head>",STYLE+"\n"+alt_tags(filename)+"\n</head>",1)
                result[path] = s
                if not relative:
                    # Preserve existing approved mappings for unchanged text; add mappings
                    # for new/edited text using the repository’s offline converter.
                    dest = SERIES/"zh-hant-data"/(slug+".js")
                    old = dest.read_text()
                    m = re.search(r"(?m)^  var variants = (.*);$",old)
                    variants = json.loads(m[1])
                    collector = TextCollector()
                    collector.feed(s)
                    used = set(collector.text)
                    # Do not keep obsolete title or draft-body nodes in the public dictionary.
                    variants = {k:v for k,v in variants.items() if k in used}
                    for t in used:
                        if t not in variants:
                            tc = converter.convert(t)
                            if t != tc: variants[t] = tc
                    localized = extract_localized_titles(s).get("zh-Hans")
                    if localized:
                        variants.setdefault(localized, converter.convert(localized))
                    if ZH_TITLE[1] in used: variants[ZH_TITLE[1]] = "片頭之前先死一個人"
                    result[dest] = old[:m.start(1)]+json.dumps(variants,ensure_ascii=False,sort_keys=True,separators=(",",":"))+old[m.end(1):]
    finally:
        converter.close()
    return result

def upgrade_outputs(outputs):
    outputs.update(render(outputs))
    return outputs

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    check = ap.parse_args().check
    output = render()
    for path, value in output.items():
        if check: assert path.read_text() == value, path
        else: path.write_text(value)
    print(("Verified" if check else "Built"), "60 existing pages and 10 Traditional dictionaries")

if __name__ == "__main__":
    main()
