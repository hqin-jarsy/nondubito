#!/usr/bin/env python3
"""Read-only preservation, full-body, route and receipt checks, not semantic proof."""
import html,json,re,unittest
from pathlib import Path
from urllib.parse import urlsplit,unquote
import build_daily_full_editions as build
from test_companion_languages import Parsed

class DailyFullEditions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=build.records()
        assert cls.records,'No reviewed daily batches'

    def test_source_view_queries_are_not_local_filenames(self):
        url='https://nondubito.net/essays/everyday/conflict/21-when-reasons-become-attitude-problems.html'
        expected='21-when-reasons-become-attitude-problems.html'
        self.assertEqual(build.source_slug(url,'conflict',21),expected)
        self.assertEqual(build.source_slug(url+'?lang=zh','conflict',21),expected)
        for invalid in (url+'?lang=en',url+'#other',url.replace('nondubito.net','example.org'),url.replace('/conflict/','/work/'),url.replace('/21-','/22-')):
            with self.subTest(url=invalid),self.assertRaises(AssertionError):
                build.source_slug(invalid,'conflict',21)

    def test_multi_class_regions_and_mixed_language_nav_labels(self):
        region='<div class="lang-en local"><div>inner</div></div>'
        a,b=build.div_span(region,'lang-en')[1:3]
        self.assertEqual(region[a:b],'<div>inner</div>')
        with self.assertRaises(AssertionError):build.div_span('<div class="lang-en-other">x</div>','lang-en')
        link='<a href="01-example.html"><small class="lang-en">Next</small><span class="lang-en">Old</span><span class="lang-zh">原题</span><span class="lang-hant">原題</span></a>'
        editions={'01-example.html':{'languages':{'en':{'title':'New & Complete'}}}}
        rendered=build.update_links(link,editions,'en')
        self.assertIn('<span class="lang-en">New &amp; Complete</span>',rendered)
        self.assertIn('<span class="lang-zh">原题</span>',rendered)
        self.assertIn('<span class="lang-hant">原題</span>',rendered)

    def test_all_eight_complete_editions_and_preserved_reading_doors(self):
        for (group,slug),r in self.records.items():
            for lang,e in r['languages'].items():
                with self.subTest(series=group,essay=slug,language=lang):
                    path=build.page_path(group,slug,lang);source=path.read_text()
                    actual=build.body_paragraphs(source,lang if lang in ('zh','hant','en') else None)
                    self.assertEqual(actual,e['paragraphs'])
                    region=source[slice(*build.div_span(source,'lang-'+lang)[1:3])] if lang in ('zh','hant','en') else source
                    title=build.plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',region,re.S)[1])
                    self.assertEqual(title,e['title'])
                    tree=Parsed(region);self.assertEqual(len(tree.nodes('div','entry-door')),1)
                    self.assertNotIn('\ufffd',source)
                    self.assertEqual(source.count('static.cloudflareinsights.com/beacon.min.js'),1)

    def test_chinese_preservation_and_eight_way_source_corrections(self):
        for (group,slug),r in self.records.items():
            counts={len(e['paragraphs']) for e in r['languages'].values()}
            self.assertEqual(len(counts),1)
            for lang in ('zh','hant'):
                e=r['languages'][lang];expected=list(e['original_paragraphs'])
                for change in r['edits']:
                    if change['lang']!=lang:continue
                    self.assertEqual(expected[change['paragraph']-1],change['before'])
                    expected[change['paragraph']-1]=change['after']
                self.assertEqual(expected,e['paragraphs'])
            for change in [e for e in r['edits'] if e['lang']=='zh']:
                languages=[e['lang'] for e in r['edits'] if e['paragraph']==change['paragraph']]
                self.assertEqual(sorted(languages),sorted(build.LANGS))

    def test_language_switches_local_routes_and_current_titles(self):
        for (group,slug),r in self.records.items():
            for lang in ('en','de','fr','es','ja','ko'):
                path=build.page_path(group,slug,lang);source=path.read_text();tree=Parsed(source)
                toggles=tree.nodes('div','lang-toggle');self.assertEqual(len(toggles),1)
                buttons=[n for n in toggles[0].walk() if n.tag=='button']
                links=[n for n in toggles[0].walk() if n.tag=='a']
                if lang=='en':
                    self.assertEqual({n.attrs.get('data-lang-button') for n in buttons},{'en','zh','zh-hant'})
                    self.assertEqual(len(links),5)
                else:
                    self.assertEqual(len(links),7)
                    self.assertEqual(sum(n.tag=='span' and n.has_class('lang-btn') and n.has_class('active') for n in toggles[0].walk()),1)
                for n in links:
                    url=urlsplit(n.attrs['href'])
                    self.assertFalse(url.scheme)
                    self.assertTrue((path.parent/unquote(url.path)).resolve().is_file(),(path,n.attrs['href']))
                regions=[(code,source[slice(*build.div_span(source,'lang-'+code)[1:3])]) for code in ('en','zh','hant')] if lang=='en' else [(lang,source)]
                for code,region in regions:
                    for n in Parsed(region).nodes('nav','series-nav'):
                        for a in [n for n in n.walk() if n.tag=='a']:
                            url=urlsplit(a.attrs['href']);target=self.records.get((group,url.path))
                            if target:self.assertIn(target['languages'][code]['title'],a.text())
                index=(path.parent/'index.html').read_text()
                regions=[(code,index[slice(*build.div_span(index,'lang-'+code)[1:3])]) for code in ('en','zh','hant')] if lang=='en' else [(lang,index)]
                for code,region in regions:
                    links=[n for n in Parsed(region).nodes('a') if n.attrs.get('href')==slug
                           and any(c.tag=='span' and re.fullmatch(r'\d{1,2}',c.text()) for c in n.walk())]
                    self.assertGreaterEqual(len(links),1)
                    for link in links:self.assertIn(r['languages'][code]['title'],link.text())

    def test_receipts_and_idempotent_rebuild(self):
        for r in self.records.values():
            review=r['review']
            self.assertEqual(build.digest((build.DATA/'batches'/review['source_plan']).read_bytes()),review['source_plan_sha256'])
            for name,value in review['reports'].items():
                self.assertEqual(build.digest((build.DATA/'batches'/name).read_bytes()),value)
            for e in r.get('inherited_corrections',[]):
                self.assertEqual(build.digest((build.DATA/'corrections'/e['receipt']).read_bytes()),e['receipt_sha256'])
                edition=r['languages'][e['lang']]
                self.assertIn(edition['received_paragraphs'][e['paragraph']-1],(e['before'],e['after']))
                self.assertEqual(edition['paragraphs'][e['paragraph']-1],e['after'])
        outputs={};build.upgrade_outputs(outputs)
        for p,t in outputs.items():self.assertEqual(p.read_text(),t,str(p))
        for path in (build.DATA/'corrections').glob('*.json'):
            d=json.loads(path.read_text());source=(build.ROOT/d['path']).read_text()
            for e in d['edits']:
                self.assertEqual(build.body_paragraphs(source,e['lang'])[e['paragraph']-1],e['after'])

if __name__=='__main__':unittest.main()
