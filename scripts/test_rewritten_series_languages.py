"""Portable checks for complete independently written language editions."""
import hashlib
import html
import json
import re
import unittest

from full_series_languages import ROOT, load_language, profile, render

SERIES=('accountability','long-consensus','relation')


class RewrittenSeriesLanguages(unittest.TestCase):
    def test_source_and_primary_prose_unchanged(self):
        for series in SERIES:
            spec=profile(series)
            p=json.loads((ROOT/'data'/series/'multilingual/preservation.json').read_text())
            for slug,digest in p['source_data'].items():
                self.assertEqual(hashlib.sha256((ROOT/'data'/series/(slug+'.json')).read_bytes()).hexdigest(),digest)
            hashes=p.get('primary_bodies') or {s:v['bodies'] for s,v in p['primary_prose'].items()}
            for slug,digest in hashes.items():
                text=(ROOT/spec['directory']/(slug+'.html')).read_text()
                body=''.join(re.findall(r'<div class="essay-body[^>]*>.*?</div>',text,re.S))
                self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),digest)

    def test_complete_foreign_outputs_and_reviewed_edits(self):
        for series in SERIES:
            spec=profile(series)
            pages=render(series)
            self.assertEqual(len(pages),(len(spec['slugs'])+1)*5)
            for path,text in pages.items():
                self.assertEqual(path.read_text(),text)
                self.assertEqual(text.count('<h1>'),1)
                self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)
                self.assertIn('family=EB+Garamond',text)
            receipt=json.loads((ROOT/'data'/series/'multilingual/publication.json').read_text())
            self.assertEqual(receipt['result'],'passed')
            self.assertEqual(receipt['unresolved'],[])
            for lang,digest in receipt.get('language_data_sha256',{}).items():
                self.assertEqual(hashlib.sha256((ROOT/'data'/series/'multilingual'/(lang+'.json')).read_bytes()).hexdigest(),digest)
            for fix in receipt['resolved_issues']:
                _,data=load_language(series,fix['language'])
                field=fix.get('field','body')
                if field.startswith(('ui.','series.')):
                    group,key=field.split('.',1)
                    value=data[group][key]
                else:
                    article=next(a for a in data['articles'] if a['slug']==fix['slug'])
                    value=article['body'][fix['paragraph']] if field=='body' else article[field]
                self.assertIn(fix['after'],value)
            for lang in spec['languages']:
                _,data=load_language(series,lang)
                for article in data['articles']:
                    original=json.loads((ROOT/'data'/series/(article['slug']+'.json')).read_text())
                    self.assertEqual(len(article['body']),len(original['body_zh']))
                    self.assertEqual(len(article['coverage']),len(original['body_zh']))
                    text='\n'.join(article['body'])
                    self.assertNotRegex(text,r'\b\d{2}DD\b|TODO|PLACEHOLDER|待翻译')
                    source_size=len(re.findall(r'[\u3400-\u9fff]', '\n'.join(original['body_zh'])))
                    self.assertGreater(len(text.split()) if lang in ('de','fr','es') else len(text),source_size*(.35 if lang in ('de','fr','es') else .8))

    def test_discovery(self):
        sitemap=(ROOT/'sitemap.xml').read_text()
        for series in SERIES:
            spec=profile(series)
            for lang in spec['languages']:
                records=json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']
                urls={r['u'] for r in records}
                for slug in ['index',*spec['slugs']]:
                    path=spec['directory']+'/'+lang+'/'+slug+'.html'
                    self.assertIn(path,urls)
                    self.assertIn('https://nondubito.net/'+path.removesuffix('index.html'),sitemap)


if __name__=='__main__':unittest.main()
