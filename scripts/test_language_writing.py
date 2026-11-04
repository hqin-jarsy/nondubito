#!/usr/bin/env python3
"""Publication and navigation-preservation checks for Language & Writing."""
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit

from build_language_writing import ROOT,render,load_items,WritingTraditionalConverter
from update_sae_navigation import CARD,library_block,render_library,render_explore
from build_content_registry import scan_page,parse_library_categories
from build_search_index import extract_recent_fiction_descriptions
from web_analytics import TOKEN
from prepare_action_sources import Document,one
from full_series_languages import (profile as language_profile, load_language,
                                   require_review_seal, render as render_languages)
from connect_full_series_languages import render as render_connections
from companion_languages import availability
from build_political_economy import (library_card as political_economy_card,
                                     published_library_count)
from publish_companion_languages import render as render_companion_connections


ORIGINAL_CARDS = ROOT/'data/language-writing/original-category02-cards.json'
METHOD_URL = 'essays/method/index.html'
# The already published 00E companion authorized these two precise availability
# changes, not arbitrary rewriting of the Methodology description.
METHOD_AVAILABILITY_EDITS = (
    ('00E 提供简体中文、英文与繁体中文','00E 同样提供八语全文'),
    ('Twelve original papers in eight languages, plus the new introduction 00E in Simplified Chinese, English, and Traditional Chinese.',
     'Twelve original papers and the introduction 00E, all in eight languages.'),
)


def separate_card_count(card):
    """Remove exactly one complete count element, including its nested spans."""
    doc=Document(card)
    anchor=one(doc.root.walk(),lambda n:n.tag=='a','One complete original card')
    count=one(anchor.walk(),lambda n:n.has('series-card-count'),'One card count')
    assert count.tag=='span' and count in anchor.children
    return card[:count.start]+card[count.end:],doc.raw(count)


def card_map(source):
    return {re.search(r'href="([^"]+)"',m[0])[1]:m[0]
            for m in CARD.finditer(library_block(source)[2])}


class Tags(HTMLParser):
    def __init__(self,text):
        super().__init__()
        self.items=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        self.items.append((tag,dict(attrs)))


class LanguageWritingPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=load_items()
        cls.all_pages=render()
        cls.pages={p:s for p,s in cls.all_pages.items() if p.parent.name not in ('de','fr','es','ja','ko')}
        cls.report=json.loads((ROOT/'data/language-writing/publication.json').read_text())
        cls.groups=json.loads((ROOT/'data/sae-reading-map.json').read_text())['groups']

    def test_complete_rebuild(self):
        self.assertEqual(len(self.items),3)
        self.assertEqual(len(self.pages),5)
        self.assertEqual(len(self.all_pages),25)
        for path,text in self.all_pages.items():
            self.assertEqual(path.read_text(),text)
            self.assertNotIn('TODO',text)

    def test_page_metadata_and_beacon(self):
        for path,text in self.pages.items():
            with self.subTest(page=str(path)):
                tags=Tags(text).items
                headers=[a for t,a in tags if t=='header']
                self.assertEqual(len(headers),1)
                self.assertIn('site-shell-header',headers[0]['class'])
                canonical='https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html')
                self.assertEqual([a['href'] for t,a in tags if t=='link' and a.get('rel')=='canonical'],[canonical])
                beacons=[a for t,a in tags if t=='script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
                self.assertEqual(len(beacons),1)
                self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'],TOKEN)
                schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
                self.assertEqual(schema['inLanguage'],['en','zh-Hans','zh-Hant'])
                if path.name!='index.html':
                    self.assertEqual(schema['datePublished'],'2026-10-26')
                    self.assertIn(schema['citation'],[i['source_url'] for i in self.items])

    def test_three_complete_reading_modes(self):
        for path,text in self.pages.items():
            with self.subTest(page=path.name):
                self.assertEqual({a['class'] for t,a in Tags(text).items if t=='h1'},{'lang-en','lang-zh','lang-hant'})
                record=scan_page(ROOT,path)
                self.assertEqual(set(record['languages']),{'en','zh-Hans','zh-Hant'})
                self.assertEqual(record['domain'],'sae-philosophy')
                self.assertEqual(set(extract_recent_fiction_descriptions(text)),{'en','zh-Hans','zh-Hant'})
                if path.name=='index.html':continue
                bodies=re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="([^"]+)">(.*?)</div>',text,re.S)
                self.assertEqual(len(bodies),3)
                for language,native,body in bodies:
                    self.assertEqual(body.count('<h2>'),3)
                    self.assertNotIn('<h3',body)
                    self.assertGreater(body.count('<p>'),18)
                    if language=='en':self.assertNotRegex(body,r'[\u3400-\u9fff]')
                hant=next(b for l,n,b in bodies if l=='hant')
                self.assertNotRegex(hant,r'余項|一髮過去|鄰裡|松了|說明瞭|深沈|贊美|兩只|調用的本領')

    def test_contextual_traditional_conversion(self):
        converter=WritingTraditionalConverter()
        try:
            self.assertEqual(converter.convert('默认这句成立，文件说明；余项、沉默、邻里互助，一发过去，松了口气，赞美父亲。'),'默認這句成立，文件說明；餘項、沉默、鄰里互助，一發過去，鬆了口氣，讚美父親。')
        finally:converter.close()

    def test_local_urls_and_fragments(self):
        for path,text in self.pages.items():
            for tag,attrs in Tags(text).items:
                url=attrs.get('href' if tag in ('a','link') else 'src','')
                parts=urlsplit(url)
                if not url or parts.scheme or parts.netloc:continue
                target=(ROOT/unquote(parts.path.lstrip('/'))) if parts.path.startswith('/') else path.parent/unquote(parts.path)
                if parts.path:self.assertTrue(target.is_file(),f'{path}: {url}')
                if parts.fragment:
                    source=target.read_text() if parts.path else text
                    self.assertRegex(source,r'\bid=["\']'+re.escape(parts.fragment)+r'["\']')

    def test_card_copy_preserved_and_groups_reproducible(self):
        source=(ROOT/'library.html').read_text()
        _,_,block=library_block(source)
        cards=card_map(source)
        self.assertGreaterEqual(len(cards),30)
        fixture=json.loads(ORIGINAL_CARDS.read_text())
        self.assertEqual(fixture['source_commit'],'dc74a14')
        self.assertEqual(fixture['source_path'],'library.html')
        self.assertEqual(fixture['receipt_path'],'data/language-writing/publication.json')
        self.assertEqual(set(fixture['cards']),set(self.report['navigation']['old_category02_card_sha256']))
        for url,digest in self.report['navigation']['old_category02_card_sha256'].items():
            original=fixture['cards'][url]
            # Never replace the old receipt with today's card hash. The full
            # recovered evidence must still match that immutable receipt.
            self.assertEqual(hashlib.sha256(original.encode()).hexdigest(),digest,url)
            expected,_=separate_card_count(original)
            if url==METHOD_URL:
                before=expected
                for old,new in METHOD_AVAILABILITY_EDITS:
                    self.assertEqual(expected.count(old),1)
                    expected=expected.replace(old,new)
                self.assertEqual(availability(before),expected)
            actual,_=separate_card_count(cards[url])
            # This compares every remaining byte: titles, descriptions, hrefs,
            # classes and whitespace. Only the count and the two explicit 00E
            # availability sentences above are allowed to differ.
            self.assertEqual(actual,expected,url)
        self.assertEqual(len(self.groups),6)
        self.assertEqual(block.count('class="sae-library-group"'),6)
        categories=parse_library_categories(ROOT/'library.html')
        self.assertEqual(len(categories),18)
        self.assertEqual(next(c for c in categories if c['number']==2)['series_count'],len(cards))
        conv=WritingTraditionalConverter()
        try:
            self.assertEqual(render_library(source,self.groups,conv),source)
            explore=(ROOT/'explore.html').read_text()
            self.assertEqual(render_explore(explore,self.groups,conv),explore)
        finally:conv.close()

    def test_current_card_counts_require_real_published_editions(self):
        source=(ROOT/'library.html').read_text()
        cards=card_map(source)
        fixture=json.loads(ORIGINAL_CARDS.read_text())['cards']
        authorized={}
        for path in sorted((ROOT/'data').glob('*/multilingual/profile.json')):
            base=path.parent
            # Draft profiles, including an unsealed Second Critique expansion,
            # do not authorize changing the preserved three-language count.
            if not (base/'publication.json').is_file():continue
            if not (base/'discovery.json').is_file():continue
            entry=json.loads((base/'discovery.json').read_text())
            url=entry.get('library_url',entry['url'])
            # This regression protects the recovered 29 cards and the one
            # separately regenerated PE card, not unrelated receipt formats.
            if url not in fixture and url!='essays/political-economy/index.html':continue
            series=path.parent.parent.name
            spec=language_profile(series)
            receipt=json.loads((base/'publication.json').read_text())
            self.assertEqual(receipt['result'],'passed',series)
            self.assertEqual(receipt['unresolved'],[],series)
            self.assertEqual(set(receipt['languages']),{'de','fr','es','ja','ko'},series)
            self.assertEqual(receipt['languages'],spec['languages'],series)
            self.assertEqual(receipt['slugs'],spec['slugs'],series)
            if 'new_article_editions' in receipt:
                self.assertEqual(receipt['new_article_editions'],5*len(spec['slugs']),series)
            else:
                # These two original package-review receipts predate the
                # generated edition-count field; do not invent a new receipt.
                self.assertIn(series,('government','institution'))
                self.assertEqual(receipt['package_name'],series+'-8-languages.zip')
                self.assertRegex(receipt['package_sha256'],r'^[0-9a-f]{64}$')
                self.assertTrue(receipt['received_files'])
            require_review_seal(series,spec)
            # A receipt/count string alone is insufficient: the actual sealed
            # reader editions must still be reproducible and present on disk.
            for language in spec['languages']:
                self.assertEqual(hashlib.sha256((base/(language+'.json')).read_bytes()).hexdigest(),
                                 receipt['language_data_sha256'][language],(series,language))
                load_language(series,language)
            for target,text in render_languages(series).items():
                self.assertEqual(target.read_text(),text,(series,target))
            connected=card_map(render_connections(series)[ROOT/'library.html'])
            expected=separate_card_count(connected[url])[1]
            self.assertEqual(separate_card_count(cards[url])[1],expected,(series,url))
            authorized.setdefault(url,[]).append(series)
        self.assertIn('method-companion',authorized.get(METHOD_URL,[]))
        # The only non-count exception in the preservation test must be backed
        # by the actual append-only companion, including its old-route checks.
        self.assertEqual(language_profile('method-companion')['slugs'],['00e'])
        for target,text in render_companion_connections('method-companion').items():
            self.assertEqual(target.read_text(),text,('method-companion',target))
        for url,original in fixture.items():
            if url not in authorized:
                self.assertEqual(separate_card_count(cards[url])[1],
                                 separate_card_count(original)[1],
                                 (url,'No published profile authorizes a count change'))

    def test_political_economy_builder_preserves_published_count(self):
        source=(ROOT/'library.html').read_text()
        url='essays/political-economy/index.html'
        conv=WritingTraditionalConverter()
        try:
            actual=political_economy_card(conv)
            # Full card equality, not just a count substring, protects the
            # unchanged title, description, links and surrounding markup.
            self.assertEqual(actual,card_map(source)[url])
            connected=card_map(render_connections('political-economy')[ROOT/'library.html'])
            self.assertEqual(separate_card_count(actual)[1],separate_card_count(connected[url])[1])
            with patch('build_political_economy.published_library_count',return_value=None):
                legacy=political_economy_card(conv)
            self.assertEqual(separate_card_count(legacy)[0],separate_card_count(actual)[0])
            self.assertIn('Theory &amp; real cases · EN / 简 / 繁',legacy)
            self.assertNotEqual(separate_card_count(legacy)[1],separate_card_count(actual)[1])
        finally:conv.close()

    def test_political_economy_count_cannot_bypass_publication(self):
        # Only negative guards are simulated. The positive path above uses
        # both real published receipts, real review hashes and saved editions.
        with patch.object(type(ROOT),'is_file',return_value=False):
            self.assertIsNone(published_library_count())
        with patch('build_political_economy.json.loads',
                   return_value={'result':'pending','unresolved':[]}):
            self.assertIsNone(published_library_count())
        with patch('full_series_languages.require_review_seal',
                   side_effect=AssertionError('review seal mismatch')):
            with self.assertRaisesRegex(AssertionError,'review seal mismatch'):
                published_library_count()

    def test_count_exception_does_not_hide_other_card_changes(self):
        original=json.loads(ORIGINAL_CARDS.read_text())['cards']['essays/sae-foundations/index.html']
        baseline,count=separate_card_count(original)
        changed=original.replace(count,'<span class="series-card-count">authorized-count-placeholder</span>',1)
        self.assertEqual(separate_card_count(changed)[0],baseline)
        for before,after in (
            ('href="essays/sae-foundations/index.html"','href="essays/changed/index.html"'),
            ('class="series-card"','class="series-card changed"'),
            ('series-card-title-zh','changed-title-class'),
            ('series-card-desc','changed-description-class'),
        ):
            self.assertIn(before,original)
            self.assertNotEqual(separate_card_count(original.replace(before,after,1))[0],baseline)

    def test_six_explore_routes_and_full_hub(self):
        explore=(ROOT/'explore.html').read_text()
        block=re.search(r'<section class="domain-section" id="sae">(.*?)</section>',explore,re.S)[1]
        self.assertEqual(block.count('class="shelf-link"'),6)
        hub=self.pages[ROOT/'essays/sae/index.html']
        self.assertEqual(hub.count('class="sae-group"'),6)
        self.assertLess(hub.index('class="sae-jump"'),hub.index('class="lw-opening"'))
        for group in self.groups:
            self.assertIn('href="essays/sae/index.html#'+group['id']+'"',block)
            for url,zh,en in group['items']:
                self.assertIn('href="../../'+url+'"',hub)
        self.assertIn('href="essays/sae/index.html"',(ROOT/'index.html').read_text())

    def test_search_sitemap_and_publication_receipts(self):
        for language in ('en','zh-hans','zh-hant'):
            records=json.loads((ROOT/f'data/search/{language}.json').read_text())['records']
            urls={r['u'] for r in records}
            self.assertTrue(all(p.relative_to(ROOT).as_posix() in urls for p in self.pages))
        root=ET.fromstring((ROOT/'sitemap.xml').read_text())
        urls={x.text for x in root.findall('{*}url/{*}loc')}
        for path in self.pages:
            self.assertIn('https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html'),urls)
        self.assertEqual({p['url'] for p in self.report['papers']},{i['source_url'] for i in self.items})
        for paper in self.report['papers']:
            self.assertTrue(paper['matches_author_local'])
            self.assertRegex(paper['sha256'],r'^[0-9a-f]{64}$')
        for name in ('library.html','latest.html'):
            self.assertIn('essays/language-writing/index.html',(ROOT/name).read_text())
        updates=json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        self.assertEqual(len([u for u in updates if u['id']=='2026-10-26-language-writing']),1)


if __name__=='__main__':
    unittest.main(verbosity=2)
