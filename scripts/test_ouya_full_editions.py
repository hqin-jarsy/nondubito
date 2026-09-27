#!/usr/bin/env python3
"""EP01 integrity/navigation tests; not a substitute for visual or editorial QA."""
import hashlib
import json
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

import build_ouya_full_editions as full


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.links, self.canonicals = [], [], []
        self.duplicate_attributes = []
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        keys = [k for k, _ in attributes]
        self.duplicate_attributes.extend(k for k, n in Counter(keys).items() if n > 1)
        attrs = dict(attributes)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs['href'])


class OuyaFullEditionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.copies = full.manuscripts()
        cls.pages = full.outputs()
        cls.receipt = json.loads((full.DATA / 'ep01-review.json').read_text())

    def test_complete_manuscripts_and_rendered_paragraphs(self):
        total = 0
        for lang, copy in self.copies.items():
            path = full.SERIES / ('ep01.html' if lang in ('en', 'zh-Hans') else f'{lang.lower()}/ep01.html')
            body = full.body_html(lang, copy)
            self.assertIn(body, self.pages[path], lang)
            prose = body.split('</div>')[0]
            count = len(re.findall(r'<p>', prose))
            self.assertEqual(count, full.COUNTS[lang], lang)
            self.assertEqual(len(re.findall(r'<h2 ', prose)), 7, lang)
            total += count
        self.assertEqual(total, 1007)

    def test_every_edit_reverses_to_received_v013(self):
        for lang in full.LANGS:
            text = (full.DATA / f'ep01.{lang}.md').read_text()
            for edit in reversed(self.receipt['edits']):
                if edit['language'] == lang:
                    self.assertEqual(text.count(edit['new']), 1, (lang, edit['reason']))
                    text = text.replace(edit['new'], edit['old'], 1)
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), self.receipt['source_sha256'][lang], lang)

    def test_exact_scope_and_idempotence(self):
        self.assertEqual(len(self.pages), 7)
        self.assertEqual({p.name for p in self.pages}, {'ep01.html'})
        for path, source in self.pages.items():
            self.assertEqual(path.read_text(), source, str(path))
            self.assertEqual(source.count('id="ouya-full-style"'), 1)
            self.assertEqual(source.count('language-select.js'), 1)

    def test_navigation_canonicals_and_ids(self):
        for path, source in self.pages.items():
            with self.subTest(page=str(path)):
                page = Page(source)
                self.assertFalse(page.duplicate_attributes)
                self.assertEqual(len(page.ids), len(set(page.ids)))
                self.assertEqual(page.canonicals, ['https://nondubito.net/' + path.relative_to(full.ROOT).as_posix()])
                for link in page.links:
                    parsed = urlsplit(link)
                    if parsed.scheme or parsed.netloc:
                        continue
                    target = ((full.ROOT / parsed.path.lstrip('/')) if parsed.path.startswith('/') else (path.parent / unquote(parsed.path))) if parsed.path else path
                    self.assertTrue(target.exists(), (path, link))
                    if parsed.fragment and target == path:
                        self.assertIn(unquote(parsed.fragment), page.ids)
                menu = re.search(r'<div class="lang-toggle">(.*?)</div>', source, re.S)[1]
                self.assertEqual(menu.count('class="lang-btn'), 8)
                if path.parent == full.SERIES:
                    self.assertEqual(menu.count('data-lang='), 2)
                    self.assertIn("q==='en'||q==='zh'", source)
                else:
                    self.assertEqual(menu.count('aria-current="page"'), 1)
                    self.assertIn('../ep01.html?lang=en', menu)
                    self.assertIn('../ep01.html?lang=zh', menu)

    def test_traditional_navigation_does_not_invent_editions(self):
        source = self.pages[full.SERIES / 'zh-hant/ep01.html']
        self.assertIn('<html lang="zh-Hant">', source)
        self.assertIn('href="ep02.html"', source)
        self.assertIn('下一篇</span>', source)
        self.assertIn('系列目錄（簡體／English）', source)
        self.assertNotIn('href="../ep02.html"', source)

    def test_historical_corrections_present_in_all_editions(self):
        for lang in full.LANGS:
            reasons = {e['reason'] for e in self.receipt['edits'] if e['language'] == lang}
            self.assertIn('citizenship-range', reasons)
            # The complete reversible ledger guards the paired replacements;
            # published notes distinguish our interpretation from ancient testimony.
            path = full.SERIES / ('ep01.html' if lang in ('en','zh-Hans') else f'{lang.lower()}/ep01.html')
            self.assertIn('class="ouya-sources"', self.pages[path])


if __name__ == '__main__':
    unittest.main()
