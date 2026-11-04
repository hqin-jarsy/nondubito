#!/usr/bin/env python3
"""Portable full-edition and primary-preservation checks for Action Theory."""
import hashlib
import html
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from full_series_languages import ROOT, load_language, profile, render, upgrade_primary, require_review_seal
from prepare_action_sources import EXPECTED_UNITS, EXPECTED_HEADINGS, render as sources
from prepare_original_series_review import prepare, primary_main_hashes
from test_companion_languages import Parsed, Node, plain_markdown
from web_analytics import TOKEN


class ActionLanguages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=profile('action')
        cls.pages=render('action')
        cls.base=ROOT/'data/action/multilingual'
        cls.receipt=json.loads((cls.base/'preservation.json').read_text())

    def test_normalized_sources_and_independent_review_are_current(self):
        for path,data in sources().items():
            self.assertEqual(json.loads(path.read_text()),data,path)
        for path,text in prepare('action').items():
            self.assertEqual(path.read_text(),text,path)
        receipt=json.loads((self.base/'publication.json').read_text())
        self.assertEqual(receipt['new_article_editions'],60)
        self.assertEqual(receipt['source_units'],list(EXPECTED_UNITS.values()))
        self.assertEqual(receipt['unresolved'],[])

    def test_generation_rejects_changed_drafts_and_unfinished_review(self):
        self.assertTrue(self.spec['require_review_seal'])
        original_bytes=Path.read_bytes
        for target,message in [(self.base/'de.json','draft changed after review'),
                               (self.base/'cross-review-es.json','review changed after seal'),
                               (ROOT/'essays/action/zh-hant-data/index.js','protected primary source changed after review'),
                               (ROOT/'data/action/prequel.json','source changed after review')]:
            def changed(path):
                value=original_bytes(path)
                return value+b'\n' if path==target else value
            with patch.object(Path,'read_bytes',changed):
                with self.assertRaisesRegex(AssertionError,message):
                    require_review_seal('action',self.spec)
        original_text=Path.read_text
        def unfinished(path,*args,**kwargs):
            text=original_text(path,*args,**kwargs)
            if path==self.base/'cross-review-ja-ko.json':
                data=json.loads(text);data['remaining']=['Still being reviewed']
                return json.dumps(data)
            return text
        with patch.object(Path,'read_text',unfinished):
            with self.assertRaisesRegex(AssertionError,'unfinished review'):
                require_review_seal('action',self.spec)

    def test_preserves_primary_reading_content_and_traditional_sources(self):
        self.assertEqual(primary_main_hashes(self.spec),self.receipt['primary_main'])
        self.assertEqual(len(self.receipt['protected_files']),13)
        for name,digest in self.receipt['protected_files'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
        for slug in ['index',*self.spec['slugs']]:
            path=ROOT/self.spec['directory']/(slug+'.html')
            current=path.read_text()
            self.assertEqual(upgrade_primary(current,'action',slug),current,path)
            self.assertNotIn('ep10.html',current)

    def test_all_sixty_editions_have_full_actual_prose(self):
        self.assertEqual(len(self.pages),65)
        for language in self.spec['languages']:
            _,data=load_language('action',language)
            self.assertEqual(len(data['articles']),12)
            self.assertEqual(sum(len(a['body']) for a in data['articles']),392)
            for article in data['articles']:
                slug=article['slug']
                path=ROOT/self.spec['directory']/language/(slug+'.html')
                text=self.pages[path]
                self.assertEqual(path.read_text(),text,path)
                page=Parsed(text)
                self.assertEqual(len(page.nodes('h1')),1)
                self.assertEqual(page.nodes('h1')[0].text(),article['title'])
                bodies=page.nodes('div','lw-prose')
                self.assertEqual(len(bodies),1)
                units=[n for n in bodies[0].children if isinstance(n,Node)]
                self.assertEqual(len(units),EXPECTED_UNITS[slug])
                self.assertEqual(sum(n.tag=='h2' for n in units),EXPECTED_HEADINGS[slug])
                for source,node in zip(article['body'],units):
                    tag,content=('h2',source[3:]) if source.startswith('## ') else ('p',source)
                    self.assertEqual(node.tag,tag)
                    self.assertEqual(node.text(),plain_markdown(content))

    def test_main_route_and_standalone_study_are_not_renumbered(self):
        main=self.spec['slugs'][:-1]
        for language in self.spec['languages']:
            base=ROOT/self.spec['directory']/language
            page=Parsed((base/'index.html').read_text())
            cards=page.nodes('a','lw-card')
            self.assertTrue(page.nodes('p','lw-meta')[0].text().startswith('11' if language!='ko' else '글 11'))
            self.assertEqual([n.attrs['href'] for n in cards],[s+'.html' for s in self.spec['slugs']])
            grids=page.nodes('section','lw-grid')
            self.assertEqual(len(grids),2)
            self.assertEqual(len([n for n in grids[0].walk() if n.has_class('lw-card')]),11)
            self.assertEqual(len([n for n in grids[1].walk() if n.has_class('lw-card')]),1)
            self.assertNotIn('12',cards[-1].text())
            for index,slug in enumerate(main):
                nav=Parsed((base/(slug+'.html')).read_text()).nodes('nav','lw-series-nav')[0]
                expected=[main[index-1]+'.html' if index else 'index.html',
                          main[index+1]+'.html' if index+1<len(main) else 'index.html']
                self.assertEqual([n.attrs['href'] for n in nav.walk() if n.tag=='a'],expected)
            nav=Parsed((base/'adversity.html').read_text()).nodes('nav','lw-series-nav')[0]
            self.assertEqual([n.attrs['href'] for n in nav.walk() if n.tag=='a'],['index.html'])
            study=Parsed((base/'adversity.html').read_text()).nodes('details','lw-sources')[0]
            urls={n.attrs.get('href') for n in study.walk() if n.tag=='a'}
            self.assertIn('https://www.gutenberg.org/cache/epub/23031/pg23031-images.html',urls)
            self.assertIn('https://www.gutenberg.org/files/2397/2397-h/2397-h.htm',urls)

    def test_metadata_language_targets_tracking_and_local_assets(self):
        for path,text in self.pages.items():
            page=Parsed(text)
            language=path.parent.name
            canonical='https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel')=='canonical'],[canonical])
            alternates=[n for n in page.nodes('link') if n.attrs.get('rel')=='alternate']
            self.assertEqual({n.attrs['hreflang'] for n in alternates},{'x-default','zh-Hans',*self.spec['languages']})
            options=page.nodes('div','site-shell-language-options')[0]
            choices=[n for n in options.walk() if n.tag=='a']
            self.assertEqual(len(choices),8)
            self.assertEqual([n.text() for n in choices if n.attrs.get('aria-current')=='page'],
                             [{'de':'Deutsch','fr':'Français','es':'Español','ja':'日本語','ko':'한국어'}[language]])
            beacons=[n for n in page.nodes('script') if 'cloudflareinsights.com/beacon.min.js' in n.attrs.get('src','')]
            self.assertEqual(len(beacons),1)
            self.assertEqual(json.loads(beacons[0].attrs['data-cf-beacon'])['token'],TOKEN)
            for node in page.root.walk():
                value=node.attrs.get('href') or node.attrs.get('src')
                if not value:continue
                url=urlsplit(html.unescape(value))
                if url.scheme or url.netloc or not url.path:continue
                target=(ROOT/unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent/unquote(url.path)).resolve()
                self.assertTrue(target.is_file(),(path,value))

    def test_all_new_articles_are_discoverable_without_duplicate_original_updates(self):
        sitemap=(ROOT/'sitemap.xml').read_text()
        for language in self.spec['languages']:
            records=json.loads((ROOT/'data/search'/(language+'.json')).read_text())['records']
            for slug in self.spec['slugs']:
                url=self.spec['directory']+'/'+language+'/'+slug+'.html'
                self.assertEqual(sum(r['u']==url for r in records),1,url)
                self.assertIn('https://nondubito.net/'+url,sitemap)
            self.assertIn('../action/'+language+'/index.html',(ROOT/'essays'/language/'index.html').read_text())
        updates=json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        self.assertEqual(sum(u['id']=='2026-11-03-action-eight-languages' for u in updates),1)
        self.assertEqual(sum(u['id']=='2026-10-26-action-adversity' for u in updates),1)


if __name__=='__main__':unittest.main()
