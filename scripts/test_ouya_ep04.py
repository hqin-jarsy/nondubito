#!/usr/bin/env python3
"""EP04 full-prose, reversible-edit, metadata and navigation regressions."""
import hashlib
import json
import re
import unittest
from urllib.parse import unquote, urlsplit

import build_ouya_ep04 as full
from test_ouya_full_editions import Page


class EP04Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.copies = full.manuscripts()
        cls.pages = full.outputs()
        cls.receipt = json.loads((full.DATA/'ep04-review.json').read_text())

    def test_complete_prose(self):
        for lang, copy in self.copies.items():
            body = full.body_html(lang, copy)
            path = full.SERIES/('ep04.html' if lang in ('zh-Hans', 'en') else f'{lang.lower()}/ep04.html')
            self.assertIn(body, self.pages[path])
            self.assertEqual(body.split('</div>')[0].count('<p>'), 132, lang)
            self.assertEqual(body.count('<h2 id='), 10, lang)

    def test_reversible_edits_and_untouched_languages(self):
        self.assertEqual(len(self.receipt['edits']), 5)
        for lang in full.LANGS:
            text = (full.DATA/f'ep04.{lang}.md').read_text()
            edits = [e for e in self.receipt['edits'] if e['language'] == lang]
            for e in reversed(edits):
                i = e['offset']
                self.assertEqual(text[i:i+len(e['new'])], e['new'])
                text = text[:i]+e['old']+text[i+len(e['new']):]
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), self.receipt['source_sha256'][lang])
            if lang in ('zh-Hans', 'zh-Hant', 'ja', 'es'):
                self.assertEqual(edits, [])
                self.assertEqual(self.receipt['source_sha256'][lang], self.receipt['published_sha256'][lang])

    def test_scope_and_idempotence(self):
        self.assertEqual(len(self.pages), 7)
        self.assertEqual({p.name for p in self.pages}, {'ep04.html'})
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
                self.assertIn('../ep04.html?lang=en', menu)
                self.assertIn('../ep04.html?lang=zh', menu)

    def test_traditional_neighbors(self):
        page = self.pages[full.SERIES/'zh-hant/ep04.html']
        self.assertIn('<html lang="zh-Hant">', page)
        self.assertIn('href="ep03.html"', page)
        self.assertIn('href="../ep05.html?lang=zh"', page)
        self.assertIn('下一篇（簡體）', page)
        self.assertNotIn('href="ep05.html"', page)
        self.assertIn('href="ep04.html"', (full.SERIES/'zh-hant/ep03.html').read_text())

    def test_targeted_copyedits_present(self):
        en = (full.DATA/'ep04.en.md').read_text()
        self.assertIn('the language of political legitimacy', en)
        self.assertIn('His building projects also left their mark on Rome.', en)
        self.assertNotIn('He also left construction in Rome.', en)
        de = (full.DATA/'ep04.de.md').read_text()
        self.assertIn('die Sprache politischer Legitimität', de)
        fr = (full.DATA/'ep04.fr.md').read_text()
        self.assertIn('Tandis que Tibère décline et que les sénateurs insistent', fr)
        ko = (full.DATA/'ep04.ko.md').read_text()
        self.assertIn('원로원 명부를 정비하는 과정에서 라베오가 레피두스를 추천', ko)
        self.assertNotIn('라베오가 원로원을 정비할 때', ko)


if __name__ == '__main__':
    unittest.main()
