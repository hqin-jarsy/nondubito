"""Publication checks requiring real full reviews, never mocked approvals."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote,urlsplit
from xml.etree import ElementTree

from full_series_languages import ROOT,load_language,original_article,profile,render,upgrade_primary
from prepare_original_series_review import prepare
from test_companion_languages import Node,Parsed,plain_markdown

SERIES='state-transitions'
BASE=ROOT/'data'/SERIES/'multilingual'
LANGS=('de','fr','es','ja','ko')


class HistoricalLanguages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # No unfinished draft is rendered to make a positive test pass.
        cls.pages=render(SERIES)
        cls.spec=profile(SERIES)
        cls.data={l:load_language(SERIES,l)[1] for l in LANGS}

    def test_genuine_complete_reviews_and_saved_output_identity(self):
        for p,t in prepare(SERIES).items():self.assertEqual(p.read_text(),t,p)
        self.assertEqual(len(self.pages),35)
        for p,t in self.pages.items():self.assertEqual(p.read_text(),t,p)
        seen=[]
        for name in ('cross-review-de-fr.json','cross-review-ja-ko.json','cross-review-es.json'):
            r=json.loads((BASE/name).read_text())
            self.assertIs(r['publication_ready'],True)
            self.assertEqual(r['remaining'],[])
            seen.extend((a['language'],a['slug']) for a in r['articles_reviewed'])
        self.assertEqual(len(seen),30)
        self.assertEqual(set(seen),{(l,s) for l in LANGS for s in self.spec['slugs']})
        receipt=json.loads((BASE/'publication.json').read_text())
        self.assertEqual(sum(receipt['source_units']),208)
        self.assertEqual(receipt['new_article_editions'],30)

    def test_all_body_units_full_source_notes_places_and_source_scope(self):
        for language,data in self.data.items():
            units=refs=0
            for a in data['articles']:
                page=Parsed(self.pages[ROOT/self.spec['directory']/language/(a['slug']+'.html')])
                nodes=[n for n in page.nodes('div','lw-prose')[0].children if isinstance(n,Node)]
                self.assertEqual(len(nodes),len(a['body']))
                for n,p in zip(nodes,a['body']):
                    self.assertEqual(n.tag,'h2' if p.startswith('## ') else 'p')
                    self.assertEqual(n.text(),plain_markdown(p[3:] if p.startswith('## ') else p))
                self.assertEqual(page.nodes('p','st-history-place')[0].text(),a['place'])
                original=original_article(SERIES,self.spec,a['slug'])
                self.assertEqual([(s['id'],s['url']) for s in a['sources']],[(s['id'],s['url']) for s in original['sources']])
                for p,q in zip(original['body_zh'],a['body']):self.assertEqual(re.findall(r'\[(\d+)\]',p),re.findall(r'\[(\d+)\]',q))
                lists=page.nodes('ol','st-source-list');self.assertEqual(len(lists),1)
                lis=[n for n in lists[0].children if isinstance(n,Node)]
                self.assertEqual(len(lis),len(a['sources']))
                for n,s in zip(lis,a['sources']):
                    links=[e for e in n.walk() if e.tag=='a'];notes=[e for e in n.walk() if e.tag=='p']
                    self.assertEqual([(e.text(),e.attrs['href']) for e in links],[(s['title'],s['url'])])
                    self.assertEqual([e.text() for e in notes],[plain_markdown(s['note'])])
                source=page.nodes('details','lw-sources')[0]
                self.assertNotIn('open',source.attrs)
                self.assertTrue(any(e.tag=='a' and e.attrs.get('href')==self.spec['source'] for e in source.walk()))
                units+=len(nodes);refs+=len(lis)
            self.assertEqual((units,refs),(208,44))

    def test_three_pairs_native_index_and_only_partner_article_navigation(self):
        for language,data in self.data.items():
            page=Parsed(self.pages[ROOT/self.spec['directory']/language/'index.html'])
            groups=page.nodes('section','lw-collection-group')
            self.assertEqual([n.attrs['id'] for n in groups],[g['id'] for g in self.spec['index_groups']])
            for node,g in zip(groups,self.spec['index_groups']):
                self.assertEqual([e.attrs['href'] for e in node.walk() if e.tag=='a' and e.has_class('lw-card')],[s+'.html' for s in g['slugs']])
            cards=page.nodes('a','lw-card');self.assertEqual(len(cards),6)
            self.assertEqual([next(e for e in n.walk() if e.tag=='p' and e.has_class('lw-kicker')).text() for n in cards],[a['place'] for a in data['articles']])
            self.assertIn(data['series']['subtitle'],page.root.text())
            for a in data['articles']:
                page=Parsed(self.pages[ROOT/self.spec['directory']/language/(a['slug']+'.html')])
                nav=page.nodes('nav','lw-series-nav')[0]
                links=[e for e in nav.walk() if e.tag=='a']
                self.assertEqual([e.attrs['href'] for e in links],['index.html',self.spec['article_pairs'][a['slug']]+'.html'])
                self.assertIn(data['ui']['read_alongside'],links[1].text())

    def test_metadata_precise_windows_analytics_and_local_destinations(self):
        for path,text in self.pages.items():
            page=Parsed(text);slug=path.stem;language=path.parent.name
            url='https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel')=='canonical'],[url])
            schema=[json.loads(n.text()) for n in page.nodes('script') if n.attrs.get('type')=='application/ld+json'][0]
            self.assertEqual(page.nodes('h1')[0].attrs.get('style'),'text-wrap:balance')
            self.assertEqual(schema['url'],url);self.assertEqual(schema['inLanguage'],language)
            if slug!='index':
                a=next(a for a in self.data[language]['articles'] if a['slug']==slug)
                self.assertEqual(schema['citation'],[s['url'] for s in a['sources']])
                old=json.loads((BASE/'primary-before-expansion.json').read_text())['original_schema'][slug]
                self.assertEqual(schema['temporalCoverage'],old['temporalCoverage'])
                self.assertEqual(schema['about']['name'],a['place'])
            options=page.nodes('div','site-shell-language-options')[0]
            self.assertEqual(len([n for n in options.walk() if n.tag=='a']),8)
            self.assertEqual(len([n for n in page.nodes('link') if n.attrs.get('rel')=='alternate']),7)
            self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)
            for n in page.root.walk():
                raw=n.attrs.get('href') or n.attrs.get('src')
                if not raw:continue
                u=urlsplit(raw)
                if u.scheme or u.netloc:continue
                target=(ROOT/unquote(u.path.lstrip('/')) if u.path.startswith('/') else path.parent/unquote(u.path)).resolve() if u.path else path
                if target.is_dir():target/='index.html'
                self.assertTrue(target.is_file(),(path,raw))
                if u.fragment:self.assertIn(unquote(u.fragment),{e.attrs.get('id') for e in Parsed(target.read_text()).root.walk()},(path,raw))

    def test_missing_full_source_or_approval_and_changed_historical_map_fail_closed(self):
        read_text=Path.read_text
        target=BASE/'de.json'
        for mode in ('source-note','source-url','body-citation','place','pair-group'):
            def corrupted(p,*args,**kwargs):
                text=read_text(p,*args,**kwargs)
                if p!=target:return text
                d=json.loads(text)
                if mode=='source-note':d['articles'][0]['sources'][0]['note']=''
                elif mode=='source-url':d['articles'][0]['sources'][0]['url']='https://example.invalid/'
                elif mode=='body-citation':d['articles'][0]['body'][1]=d['articles'][0]['body'][1].replace('[1]','')
                elif mode=='place':d['articles'][0]['place']=''
                else:d['series']['index_groups'][0]['id']='wrong'
                return json.dumps(d)
            with self.subTest(mode=mode),patch.object(Path,'read_text',corrupted),self.assertRaises(AssertionError):load_language(SERIES,'de')
        def bad_review(p,*args,**kwargs):
            text=read_text(p,*args,**kwargs)
            if p==BASE/'cross-review-de-fr.json':
                d=json.loads(text);d['articles_reviewed'].pop();return json.dumps(d)
            return text
        with patch.object(Path,'read_text',bad_review),self.assertRaises(AssertionError):prepare(SERIES)

    def test_discovery_search_and_sitemap_after_real_outputs(self):
        from connect_full_series_languages import render as connections
        for p,t in connections(SERIES).items():self.assertEqual(p.read_text(),t,p)
        locations=[n.text for n in ElementTree.fromstring((ROOT/'sitemap.xml').read_text()).iter() if n.tag.rsplit('}',1)[-1]=='loc']
        for l in LANGS:
            records=json.loads((ROOT/'data/search'/(l+'.json')).read_text())['records']
            for slug in ['index',*self.spec['slugs']]:
                url=self.spec['directory']+'/'+l+'/'+slug+'.html'
                self.assertEqual(sum(r['u']==url for r in records),1)
                self.assertEqual(locations.count('https://nondubito.net/'+url.removesuffix('index.html')),1)


if __name__=='__main__':unittest.main()
