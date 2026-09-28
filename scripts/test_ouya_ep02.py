#!/usr/bin/env python3
"""EP02 complete-prose, provenance, navigation and deterministic-build checks."""
import hashlib
import json
import re
import unittest
from urllib.parse import unquote, urlsplit

import build_ouya_ep02 as full
from test_ouya_full_editions import Page

class EP02Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.copies=full.manuscripts()
        cls.pages=full.outputs()
        cls.receipt=json.loads((full.DATA/'ep02-review.json').read_text())

    def test_complete_prose(self):
        for lang,copy in self.copies.items():
            body=full.body_html(lang,copy)
            path=full.SERIES/('ep02.html' if lang in ('zh-Hans','en') else f'{lang.lower()}/ep02.html')
            self.assertIn(body,self.pages[path])
            self.assertEqual(body.split('</div>')[0].count('<p>'),131,lang)
            self.assertEqual(body.count('<h2 id='),9,lang)

    def test_receipt_reverses_exactly(self):
        self.assertEqual(len(self.receipt['edits']),9)
        for lang in full.LANGS:
            text=(full.DATA/f'ep02.{lang}.md').read_text()
            local=[e for e in self.receipt['edits'] if e['language']==lang]
            self.assertIn('4.4-gradual-succession-seam',{e['reason'] for e in local})
            for edit in reversed(local):
                self.assertEqual(text.count(edit['new']),1)
                self.assertNotIn(edit['old'],text)
                text=text.replace(edit['new'],edit['old'],1)
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),self.receipt['source_sha256'][lang])

    def test_scope_and_idempotence(self):
        self.assertEqual(len(self.pages),7)
        self.assertEqual({p.name for p in self.pages},{'ep02.html'})
        for path,text in self.pages.items():
            self.assertEqual(path.read_text(),text,str(path))
            self.assertEqual(text.count('id="ouya-full-style"'),1)
            self.assertEqual(text.count('language-select.js'),1)

    def test_links_metadata_and_structure(self):
        for path,text in self.pages.items():
            page=Page(text)
            self.assertFalse(page.duplicate_attributes,path)
            self.assertEqual(len(page.ids),len(set(page.ids)),path)
            self.assertEqual(page.canonicals,['https://nondubito.net/'+path.relative_to(full.ROOT).as_posix()])
            for link in page.links:
                parsed=urlsplit(link)
                if parsed.scheme or parsed.netloc:continue
                target=(full.ROOT/parsed.path.lstrip('/') if parsed.path.startswith('/') else path.parent/unquote(parsed.path)) if parsed.path else path
                self.assertTrue(target.exists(),(path,link))
                if parsed.fragment and target==path:self.assertIn(unquote(parsed.fragment),page.ids)
            menu=re.search(r'<div class="lang-toggle">(.*?)</div>',text,re.S)[1]
            self.assertEqual(menu.count('class="lang-btn'),8)
            if path.parent==full.SERIES:
                self.assertEqual(menu.count('data-lang='),2)
                self.assertIn('id="ouya-inline-language"',text)
            else:
                self.assertEqual(menu.count('aria-current="page"'),1)
                self.assertIn('../ep02.html?lang=en',menu)
                self.assertIn('../ep02.html?lang=zh',menu)

    def test_traditional_neighbors(self):
        page=self.pages[full.SERIES/'zh-hant/ep02.html']
        self.assertIn('<html lang="zh-Hant">',page)
        self.assertIn('href="ep01.html"',page)
        self.assertIn('href="ep03.html"',page)
        self.assertIn('下一篇</span>',page)
        self.assertNotIn('href="../ep03.html?lang=zh"',page)
        self.assertIn('href="ep02.html"',(full.SERIES/'zh-hant/ep01.html').read_text())

if __name__=='__main__':unittest.main()
