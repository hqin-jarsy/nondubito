#!/usr/bin/env python3
"""Regressions for the Foundation Paper 6 v2 reader-facing revision."""

import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "essays" / "sae-foundations"
FOREIGN = ("ja", "fr", "de", "es", "ko")
SOURCE = "https://self-as-an-end.net/papers/sae-institution.html"
PAGES = [SERIES / prefix / f"ep{n}.html"
         for prefix in ("", *FOREIGN) for n in (12, 13)]


class PageInfo(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.canonical = []
        self.texts = []
        self.language = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language = attrs.get("lang")
        if tag in ("a", "link", "script"):
            url = attrs.get("href") or attrs.get("src")
            if url:
                self.links.append(url)
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical.append(attrs.get("href"))

    def handle_data(self, data):
        self.texts.append(data)


def bodies(source):
    return re.findall(r'<div class="essay-body[^"]*"[^>]*>(.*?)</div>', source, re.S)


def traditional_map(stem):
    source = (SERIES / "zh-hant-data" / f"{stem}.js").read_text()
    return json.loads(re.search(r"var variants = (\{.*?\});\n", source, re.S).group(1))


class InstitutionRevisionTests(unittest.TestCase):
    def test_article_structure_and_languages(self):
        for page in PAGES:
            with self.subTest(page=str(page.relative_to(ROOT))):
                source = page.read_text()
                primary = page.parent == SERIES
                self.assertEqual(len(bodies(source)), 2 if primary else 1)
                self.assertEqual(PageInfo(source).language, "zh-Hans" if primary else page.parent.name)
                for body in bodies(source):
                    self.assertEqual(body.count("<h2>"), 4)
                    self.assertEqual(body.count("<p>"), body.count("</p>"))
                    self.assertGreaterEqual(body.count("<p>"), 8)

    def test_canonical_source_and_local_targets(self):
        for page in PAGES:
            info = PageInfo(page.read_text())
            with self.subTest(page=str(page.relative_to(ROOT))):
                self.assertEqual(info.canonical, ["https://nondubito.net/" + page.relative_to(ROOT).as_posix()])
                self.assertIn(SOURCE, info.links)
                for url in info.links:
                    parsed = urlsplit(url)
                    if parsed.scheme or parsed.netloc or not parsed.path:
                        continue
                    base = ROOT if parsed.path.startswith("/") else page.parent
                    self.assertTrue((base / unquote(parsed.path).lstrip("/")).resolve().exists(), url)

    def test_all_existing_language_routes_remain(self):
        for page in PAGES:
            targets = {(page.parent / urlsplit(url).path).resolve()
                       for url in PageInfo(page.read_text()).links
                       if not urlsplit(url).scheme and urlsplit(url).path}
            editions = {SERIES / prefix / page.name for prefix in ("", *FOREIGN)}
            self.assertTrue((editions - {page}).issubset(targets), page)

    def test_withdrawn_pairing_claims_do_not_return(self):
        old_phrases = {
            "": ("共同仲裁之所以可行，还因为权利与义务成对出现", "只有权利而没有义务，保护会成为", "Common arbitration also depends on the pairing", "Rights without obligations become promises"),
            "ja": ("権利と義務を対にする", "権利だけでは実現不能な約束"),
            "fr": ("L’arbitrage commun repose enfin sur l’association", "Des droits sans obligations deviennent"),
            "de": ("Gemeinsame Schlichtung trägt nur, wenn Rechte und Pflichten", "Rechte ohne Pflichten werden zu ungedeckten"),
            "es": ("El arbitraje común vincula derechos y obligaciones", "Derechos sin obligaciones son promesas vacías"),
            "ko": ("권리와 의무는 함께 생긴다",),
        }
        for prefix, phrases in old_phrases.items():
            source = (SERIES / prefix / "ep12.html").read_text()
            for phrase in phrases:
                self.assertNotIn(phrase, source, prefix)

    def test_role_accountability_and_exit_are_explicit(self):
        markers = {
            "": ("职责", "自己的法", "独立的追究或补救根据", "accountability", "independent grounds", "not something power does by itself"),
            "ja": ("職責", "義務", "別の根拠", "拒否", "予測"),
            "fr": ("responsabilités liées à sa fonction", "devoir", "autre fondement", "refuser", "prévision"),
            "de": ("Verantwortung aus einer Rolle", "Pflicht", "eigenständigen Grund", "Nein sagen", "Vorhersage"),
            "es": ("responsabilidades ligadas al puesto", "ley propia", "fundamento independiente", "negarse", "predice"),
            "ko": ("책무", "내적 의무", "별도의 근거", "거절", "예측"),
        }
        for prefix, phrases in markers.items():
            source = (SERIES / prefix / "ep12.html").read_text()
            for phrase in phrases:
                self.assertIn(phrase, source, prefix)

    def test_traditional_body_mapping_and_cache_version(self):
        # Identity text needs no mapping (e.g. 制度的目的不是制度).
        unchanged = {"制度的目的不是制度", "最小化不是越少越好"}
        for stem in ("ep12", "ep13"):
            source = (SERIES / f"{stem}.html").read_text()
            mapping = traditional_map(stem)
            body = bodies(source)[0]
            for text in PageInfo(body).texts:
                if re.search(r"[\u3400-\u9fff]", text) and text not in unchanged:
                    self.assertTrue(text in mapping, f"{stem}: missing Traditional Chinese mapping for {text}")
                    self.assertNotIn("职责", mapping[text])
            self.assertIn(f'zh-hant-data/{stem}.js?v=20260919-institution-v2', source)
        mapping = traditional_map("ep12")
        self.assertNotIn("权利与义务", mapping)
        self.assertEqual(mapping["承担一份职责，不是交出整个人"], "承擔一份職責，不是交出整個人")

    def test_search_and_sitemap_keep_all_editions(self):
        for lang in ("en", "zh-hans", "zh-hant", *FOREIGN):
            records = json.loads((ROOT / "data" / "search" / f"{lang}.json").read_text())["records"]
            urls = {record["u"] for record in records}
            prefix = f"{lang}/" if lang in FOREIGN else ""
            for n in (12, 13):
                self.assertIn(f"essays/sae-foundations/{prefix}ep{n}.html", urls)
        sitemap = ET.parse(ROOT / "sitemap.xml")
        urls = {node.text for node in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
        for page in PAGES:
            self.assertIn("https://nondubito.net/" + page.relative_to(ROOT).as_posix(), urls)


if __name__ == "__main__":
    unittest.main()
