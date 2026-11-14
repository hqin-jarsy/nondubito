#!/usr/bin/env python3
"""Publication checks for individually reviewed three-language reader series."""
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote,urlsplit
from build_reader_series import ROOT,registry,load_items,render,ReaderTraditionalConverter
from build_content_registry import scan_page
from test_language_writing import Tags
from update_sae_navigation import CARD,library_block
from web_analytics import TOKEN


class ReaderSeriesPublication(unittest.TestCase):
    def test_traditional_context(self):
        converter = ReaderTraditionalConverter()
        try:
            for source, expected in (
                ('量得准不准；量得很准；校准记录', '量得準不準；量得很準；校準記錄'),
                ('钢制储罐；划明范围；划窄；划出边界', '鋼製儲罐；劃明範圍；劃窄；劃出邊界'),
                ('咨询答复；发明了规则；发布者', '諮詢答覆；發明了規則；發佈者'),
                ('注明来源；标注范围；获准发问', '註明來源；標註範圍；獲准發問'),
            ):
                self.assertEqual(converter.convert(source),expected)
        finally:
            converter.close()

    def test_manuscripts_and_rendering(self):
        for s in registry():
            items = load_items(s)
            self.assertEqual(len({i['title_zh'] for i in items}),len(items))
            self.assertEqual(len({i['title_en'] for i in items}),len(items))
            receipt = json.loads((ROOT/f'data/{s["slug"]}/publication.json').read_text())
            for i in items:
                self.assertEqual(receipt['counts'][i['slug']],{'zh_han':len(re.findall(r'[\u3400-\u9fff]',''.join(i['body_zh']))),'en_words':len(' '.join(i['body_en']).split())})
                for lang in ('zh','en'):
                    self.assertNotRegex('\n'.join(i['body_'+lang]),r'https?://|\]\(')
            pages = render(s['slug'])
            self.assertEqual(len(pages),len(items)+1)
            for path,text in pages.items():
                self.assertEqual(text,path.read_text(),str(path))
                self.assertNotRegex(text,r'TODO|\b\d{2}DD\b|ψ|ρ')
                tags = Tags(text).items
                self.assertEqual(len([1 for t,a in tags if t=='header' and a.get('class')=='site-shell-header']),1)
                self.assertEqual({a.get('class') for t,a in tags if t=='h1'},{'lang-en','lang-zh','lang-hant'})
                canonical = 'https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html')
                self.assertEqual([a['href'] for t,a in tags if t=='link' and a.get('rel')=='canonical'],[canonical])
                beacon = [a for t,a in tags if t=='script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
                self.assertEqual(len(beacon),1)
                self.assertEqual(json.loads(beacon[0]['data-cf-beacon'])['token'],TOKEN)
                record = scan_page(ROOT,path)
                self.assertEqual(record['domain'],'sae-philosophy')
                self.assertEqual(set(record['languages']),{'en','zh-Hans','zh-Hant'})
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
                self.assertEqual(schema['inLanguage'],['en','zh-Hans','zh-Hant'])
                if path.name != 'index.html':
                    item = items[int(path.stem[2:])-1]
                    self.assertEqual(schema['citation'],item['source_url'])
                    self.assertEqual(schema['datePublished'],s['date'])
                    self.assertEqual(schema['isPartOf']['url'],f'https://nondubito.net/essays/{s["slug"]}/')
                    self.assertEqual(len(item['body_hant']),len(item['body_zh']))
                    self.assertNotRegex(''.join(item['body_hant']),r'余項|覈實|覈對|鏈接|沈重')

    def test_local_targets(self):
        for path,text in render().items():
            for tag,a in Tags(text).items:
                raw = a.get('href' if tag in ('a','link') else 'src','')
                parts = urlsplit(raw)
                if not raw or parts.scheme or parts.netloc:continue
                target = ROOT/unquote(parts.path.lstrip('/')) if parts.path.startswith('/') else path.parent/unquote(parts.path)
                if parts.path:self.assertTrue(target.is_file(),f'{path}: {raw}')
                if parts.fragment:
                    content = target.read_text() if parts.path else text
                    self.assertRegex(content,r'\bid=["\']'+re.escape(parts.fragment)+r'["\']')

    def test_discovery_and_preservation(self):
        library = (ROOT/'library.html').read_text()
        _,_,block = library_block(library)
        cards = {re.search(r'href="([^"]+)"',m[0])[1]:m[0] for m in CARD.finditer(block)}
        groups = json.loads((ROOT/'data/sae-reading-map.json').read_text())['groups']
        self.assertEqual(len(groups),6)
        for s in registry():
            receipt = json.loads((ROOT/f'data/{s["slug"]}/publication.json').read_text())
            for url,digest in receipt['preceding_library_cards'].items():
                self.assertEqual(hashlib.sha256(cards[url].encode()).hexdigest(),digest,url)
            url = f'essays/{s["slug"]}/index.html'
            self.assertEqual(sum(i[0]==url for g in groups for i in g['items']),1)
            self.assertIn(url,cards)
            self.assertIn(url,(ROOT/'latest.html').read_text())
            updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
            update = [u for u in updates if u['id']==f'{s["date"]}-{s["slug"]}-reader-series']
            self.assertEqual(len(update),1)
            self.assertEqual(set(update[0]['languages']),{'en','zh','zh-hant'})
        for lang in ('en','zh-hans','zh-hant'):
            records = json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']
            urls = {r['u'] for r in records}
            for path in render():self.assertTrue(path.relative_to(ROOT).as_posix() in urls,f'Missing search entry ({lang}): {path}')
        sitemap = {e.text for e in ET.fromstring((ROOT/'sitemap.xml').read_text()).findall('{*}url/{*}loc')}
        for path in render():
            self.assertTrue('https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html') in sitemap,f'Missing sitemap URL: {path}')


if __name__ == '__main__':unittest.main(verbosity=2)
