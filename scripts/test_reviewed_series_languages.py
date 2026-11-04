"""Checks for supplied long-form manuscripts after full editorial review."""
import hashlib
import html
import json
import re
import unittest
from urllib.parse import unquote, urlsplit

from full_series_languages import ROOT, load_language, profile, render
from prepare_reviewed_series_package import plain
from web_analytics import TOKEN

SERIES = ('marriage',)


class ReviewedSeriesLanguages(unittest.TestCase):
    def test_full_manuscripts_and_reviewed_corrections(self):
        for series in SERIES:
            spec=profile(series)
            base=ROOT/'data'/series/'multilingual'
            receipt=json.loads((base/'publication.json').read_text())
            self.assertEqual(receipt['result'],'passed')
            self.assertEqual(receipt['unresolved'],[])
            self.assertEqual(len(receipt['received_files']),len(spec['slugs'])*5)
            for path, expected in receipt['received_files'].items():
                self.assertEqual(hashlib.sha256((base/path).read_bytes()).hexdigest(),expected)
            pages=render(series)
            self.assertEqual(len(pages),(len(spec['slugs'])+1)*5)
            for language in spec['languages']:
                _,data=load_language(series,language)
                for a in data['articles']:
                    path=ROOT/spec['directory']/language/(a['slug']+'.html')
                    self.assertEqual(path.read_text(),pages[path])
                    prose=re.search(r'<div class="essay-body lw-prose"[^>]*>(.*?)</div>',pages[path],re.S)[1]
                    units=re.findall(r'<(?:p|h2)>(.*?)</(?:p|h2)>',prose,re.S)
                    self.assertEqual([plain(p) for p in units],[plain(p) for p in a['body']])
                    self.assertEqual(len(a['body']),len(a['coverage']))
            for fix in receipt['resolved_issues']:
                _,data=load_language(series,fix['language'])
                article=next(a for a in data['articles'] if a['slug']==fix['slug'])
                self.assertIn(fix['after'],'\n\n'.join(article['body'])+'\n\n'+article['deck']+'\n\n'+article['source_note'])

    def test_primary_prose_and_dictionary_bytes_preserved(self):
        for series in SERIES:
            spec=profile(series)
            receipt=json.loads((ROOT/'data'/series/'multilingual/preservation.json').read_text())
            for slug,expected in receipt['primary_bodies'].items():
                source=(ROOT/spec['directory']/(slug+'.html')).read_text()
                bodies=''.join(re.findall(r'<div class="essay-body[^>]*>.*?</div>',source,re.S))
                self.assertEqual(hashlib.sha256(bodies.encode()).hexdigest(),expected,(series,slug))
            for path,expected in receipt['primary_files'].items():
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected,path)

    def test_urls_navigation_markup_and_analytics(self):
        for series in SERIES:
            spec=profile(series)
            pages=render(series)
            for path,text in pages.items():
                lang=path.parent.name
                self.assertEqual(text.count('<h1>'),1)
                self.assertIn(f'data-editions="{lang}" data-foreign-edition="true"',text)
                self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)
                self.assertIn(TOKEN,text)
                canonical='https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html')
                self.assertIn(f'rel="canonical" href="{canonical}"',text)
                schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text)[1])
                self.assertEqual(schema['inLanguage'],lang)
                menu=re.search(r'<div class="site-shell-language-options">(.*?)</div>',text)[1]
                self.assertEqual(menu.count('<a '),8)
                self.assertEqual(menu.count('aria-current="page"'),1)
                for code in spec['languages']:self.assertIn(f'../{code}/{path.name}',menu)
                for href in re.findall(r'href="([^"]+)"',text):
                    url=urlsplit(html.unescape(href))
                    if url.scheme or not url.path:continue
                    target=(path.parent/unquote(url.path)).resolve()
                    self.assertTrue(target in pages or target.is_file(),(path,href))
                self.assertNotIn('**',re.search(r'<div class="essay-body.*?</div>',text,re.S)[0] if path.stem!='index' else '')

    def test_search_sitemap_language_channel_and_ledger(self):
        sitemap=(ROOT/'sitemap.xml').read_text()
        updates=json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        for series in SERIES:
            spec=profile(series)
            entry=json.loads((ROOT/'data'/series/'multilingual/discovery.json').read_text())
            self.assertEqual(sum(u['id']==entry['id'] for u in updates),1)
            for language in spec['languages']:
                records=json.loads((ROOT/f'data/search/{language}.json').read_text())['records']
                urls={r['u'] for r in records}
                for slug in ['index',*spec['slugs']]:
                    path=spec['directory']+'/'+language+'/'+slug+'.html'
                    self.assertIn(path,urls)
                    self.assertIn('https://nondubito.net/'+path.removesuffix('index.html'),sitemap)
                self.assertIn(f'../{series}/{language}/index.html',(ROOT/f'essays/{language}/index.html').read_text())


if __name__=='__main__':unittest.main()
