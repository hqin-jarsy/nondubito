#!/usr/bin/env python3
"""EP03 full-prose, reversible-edit, metadata and navigation regressions."""
import hashlib
import json
import re
import unittest
from urllib.parse import unquote, urlsplit

import build_ouya_ep03 as full
from test_ouya_full_editions import Page


class EP03Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.copies = full.manuscripts()
        cls.pages = full.outputs()
        cls.receipt = json.loads((full.DATA/'ep03-review.json').read_text())

    def test_complete_prose(self):
        for lang, copy in self.copies.items():
            body = full.body_html(lang, copy)
            path = full.SERIES/('ep03.html' if lang in ('zh-Hans', 'en') else f'{lang.lower()}/ep03.html')
            self.assertIn(body, self.pages[path])
            self.assertEqual(body.split('</div>')[0].count('<p>'), 128, lang)
            self.assertEqual(body.count('<h2 id='), 10, lang)

    def test_reversible_edits_and_untouched_languages(self):
        self.assertEqual(len(self.receipt['edits']), 28)
        for lang in full.LANGS:
            text = (full.DATA/f'ep03.{lang}.md').read_text()
            edits = [e for e in self.receipt['edits'] if e['language'] == lang]
            for e in reversed(edits):
                i = e['offset']
                self.assertEqual(text[i:i+len(e['new'])], e['new'])
                text = text[:i]+e['old']+text[i+len(e['new']):]
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), self.receipt['source_sha256'][lang])
            if lang in ('zh-Hans', 'zh-Hant', 'de', 'ko'):
                self.assertEqual(edits, [])
                self.assertEqual(self.receipt['source_sha256'][lang], self.receipt['published_sha256'][lang])

    def test_scope_and_idempotence(self):
        self.assertEqual(len(self.pages), 7)
        self.assertEqual({p.name for p in self.pages}, {'ep03.html'})
        for path, text in self.pages.items():
            self.assertEqual(path.read_text(), text, str(path))
            self.assertEqual(text.count('id="ouya-full-style"'), 1)
            self.assertEqual(text.count('language-select.js'), 1)
            self.assertEqual(text.count('class="ouya-full"'), 2 if path.parent == full.SERIES else 1)

    def test_links_metadata_and_structure(self):
        for path, text in self.pages.items():
            page = Page(text)
            self.assertFalse(page.duplicate_attributes, path)
            self.assertEqual(len(page.ids), len(set(page.ids)), path)
            self.assertEqual(page.canonicals, ['https://nondubito.net/'+path.relative_to(full.ROOT).as_posix()])
            for link in page.links:
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc: continue
                target = (full.ROOT/parsed.path.lstrip('/') if parsed.path.startswith('/') else path.parent/unquote(parsed.path)) if parsed.path else path
                self.assertTrue(target.exists(), (path, link))
                if parsed.fragment and target == path: self.assertIn(unquote(parsed.fragment), page.ids)
            menu = re.search(r'<div class="lang-toggle">(.*?)</div>', text, re.S)[1]
            self.assertEqual(menu.count('class="lang-btn'), 8)
            if path.parent == full.SERIES:
                self.assertEqual(menu.count('data-lang='), 2)
                self.assertIn('id="ouya-inline-language"', text)
            else:
                self.assertEqual(menu.count('aria-current="page"'), 1)
                self.assertIn('../ep03.html?lang=en', menu)
                self.assertIn('../ep03.html?lang=zh', menu)

    def test_traditional_neighbors(self):
        page = self.pages[full.SERIES/'zh-hant/ep03.html']
        self.assertIn('<html lang="zh-Hant">', page)
        self.assertIn('href="ep02.html"', page)
        self.assertIn('href="../ep04.html?lang=zh"', page)
        self.assertIn("localStorage.setItem('nd_lang','zh')", page)
        self.assertIn('下一篇（簡體）', page)
        self.assertNotIn('href="ep04.html"', page)
        self.assertIn('href="ep03.html"', (full.SERIES/'zh-hant/ep02.html').read_text())

    def test_targeted_copyedits_present(self):
        ja = (full.DATA/'ep03.ja.md').read_text()
        self.assertIn('官職には任期を設ける', ja)
        self.assertIn('複数の政務官の協力', ja)
        self.assertIn('ある者たちは実力行使に踏み切り', ja)
        self.assertIn('新しい政治連合が再び開いた', ja)
        self.assertNotIn('官職が聞き流せる', ja)
        es = (full.DATA/'ep03.es.md').read_text()
        self.assertIn('se disponía de ellos por separado', es)
        self.assertIn('sirvió para matar.', es)
        self.assertNotIn('sirvió para matarse', es)


if __name__ == '__main__':
    unittest.main()
