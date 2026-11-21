#!/usr/bin/env python3
"""Publication checks for individually reviewed three-language reader series."""
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote,urlsplit
from build_reader_series import ROOT,registry,load_items,render,ReaderTraditionalConverter,multilingual,library_card
from build_content_registry import scan_page
from test_language_writing import Tags
from update_sae_navigation import CARD,library_block
from web_analytics import TOKEN
from reader_supplements import is_standalone,parent_spec,parent_discovery_paths,START,END,SCOPED_STYLE


class ReaderSeriesPublication(unittest.TestCase):
    def test_traditional_context(self):
        converter = ReaderTraditionalConverter()
        try:
            for source, expected in (
                ('量得准不准；量得很准；校准记录', '量得準不準；量得很準；校準記錄'),
                ('钢制储罐；划明范围；划窄；划出边界', '鋼製儲罐；劃明範圍；劃窄；劃出邊界'),
                ('咨询答复；发明了规则；发布者', '諮詢答覆；發明了規則；發佈者'),
                ('注明来源；标注范围；获准发问', '註明來源；標註範圍；獲准發問'),
                ('心智能力法；心智能力评估', '心智能力法；心智能力評估'),
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
                translated = next((item for item in registry() if url==f'essays/{item["slug"]}/index.html' and multilingual(item['slug'])),None)
                if translated:
                    # Later approved language editions update only their own card.
                    self.assertEqual(cards[url],library_card(translated,None),url)
                else:
                    self.assertEqual(hashlib.sha256(cards[url].encode()).hexdigest(),digest,url)
            url = f'essays/{s["slug"]}/index.html'
            if is_standalone(s):
                self.assertEqual(sum(i[0]==url for g in groups for i in g['items']),1)
                self.assertIn(url,cards)
            else:
                self.assertEqual(sum(i[0]==url for g in groups for i in g['items']),0)
                self.assertNotIn(url,cards)
                parent = parent_spec(s)
                text = (ROOT/parent[0]).read_text()
                self.assertEqual(text.count(START),1)
                self.assertEqual(text.count(END),1)
                block = text.split(START)[1].split(END)[0]
                self.assertIn(SCOPED_STYLE,block)
                for css,mode in (('en','en'),('zh','zh'),('hant','zh-hant')):
                    section = re.search(r'<aside class="[^"]*reader-extensions lang-'+css+r'".*?</aside>',block,re.S)[0]
                    self.assertEqual(section.count('<a href='),s['count'])
                    for i in load_items(s):
                        self.assertIn(f'/{s["slug"]}/{i["slug"]}.html?lang={mode}',section)
                for page_text in render(s['slug']).values():
                    for mode in ('en','zh','zh-hant'):
                        self.assertIn('data-edition-'+mode+'=',page_text)
                        self.assertIn(parent[0].removeprefix('essays/')+'?lang='+mode,page_text)
            self.assertIn(url,(ROOT/'latest.html').read_text())
            updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
            update = [u for u in updates if u['id']==f'{s["date"]}-{s["slug"]}-reader-series']
            self.assertEqual(len(update),1)
            expected_languages = {'en','zh','zh-hant'}
            # Most older translations have a separate expansion announcement.
            # If discovery explicitly updates the original listing instead,
            # its published languages must also match the profile.
            translation_root = ROOT/f'data/{s["slug"]}/multilingual'
            discovery = translation_root/'discovery.json'
            if discovery.is_file() and json.loads(discovery.read_text())['id'] == update[0]['id']:
                expected_languages.update(json.loads((translation_root/'profile.json').read_text())['languages'])
            self.assertEqual(set(update[0]['languages']),expected_languages)
        for lang in ('en','zh-hans','zh-hant'):
            records = json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']
            urls = {r['u'] for r in records}
            for path in render():self.assertTrue(path.relative_to(ROOT).as_posix() in urls,f'Missing search entry ({lang}): {path}')
            for s in registry():
                for path in parent_discovery_paths(s,ROOT):
                    self.assertIn(path.relative_to(ROOT).as_posix(),urls)
        sitemap = {e.text for e in ET.fromstring((ROOT/'sitemap.xml').read_text()).findall('{*}url/{*}loc')}
        for path in render():
            self.assertTrue('https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html') in sitemap,f'Missing sitemap URL: {path}')


if __name__ == '__main__':unittest.main(verbosity=2)
