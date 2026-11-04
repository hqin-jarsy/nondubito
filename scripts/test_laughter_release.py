"""Publication acceptance uses genuine completed reviews, never dummy approval."""
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from full_series_languages import ROOT, load_language, original_article, profile, render
from prepare_original_series_review import prepare
from test_companion_languages import Node, Parsed, plain_markdown

SERIES = 'laughter'
BASE = ROOT/'data/laughter/multilingual'


class LaughterRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = profile(SERIES)
        cls.pages = render(SERIES)
        cls.data = {l:load_language(SERIES,l)[1] for l in cls.spec['languages']}

    def test_real_complete_nonauthor_reviews_and_saved_pages(self):
        self.assertEqual(len(self.pages), 35)
        for p,t in prepare(SERIES).items(): self.assertEqual(p.read_text(),t,p)
        for p,t in self.pages.items(): self.assertEqual(p.read_text(),t,p)
        seen=[]
        for name in ('cross-review-de-fr.json','cross-review-es.json','cross-review-ja-ko.json'):
            r=json.loads((BASE/name).read_text())
            self.assertIs(r['publication_ready'],True)
            self.assertEqual(r['remaining'],[])
            seen += [(a['language'],a['slug']) for a in r['articles_reviewed']]
        self.assertEqual(len(seen),30)
        self.assertEqual(set(seen),{(l,s) for l in self.spec['languages'] for s in self.spec['slugs']})
        receipt=json.loads((BASE/'publication.json').read_text())
        self.assertEqual(receipt['source_units'],[52,34,38,43,60,83])
        self.assertEqual(receipt['new_article_editions'],30)

    def test_all_full_body_units_notes_source_links_and_relax_route(self):
        for language,data in self.data.items():
            units=headings=notes=links=0
            for a in data['articles']:
                page=Parsed(self.pages[ROOT/self.spec['directory']/language/(a['slug']+'.html')])
                nodes=[n for n in page.nodes('div','lw-prose')[0].children if isinstance(n,Node)]
                self.assertEqual(len(nodes),len(a['body']))
                for n,p in zip(nodes,a['body']):
                    self.assertEqual(n.tag,'h2' if p.startswith('## ') else 'p')
                    self.assertEqual(n.text(),plain_markdown(p[3:] if p.startswith('## ') else p))
                source=page.nodes('details','lw-sources')[0]
                self.assertNotIn('open',source.attrs)
                paragraphs=[n.text() for n in source.children if isinstance(n,Node) and n.tag=='p']
                self.assertEqual(paragraphs,[plain_markdown(p) for p in [a['source_note'],*a['notes']]])
                original=original_article(SERIES,self.spec,a['slug'])
                self.assertEqual([s['url'] for s in a['sources']],[s['url'] for s in original['sources_zh']])
                invitation=page.nodes('aside','jg-pause')[0]
                self.assertIn(a['pause'],invitation.text())
                self.assertIn(data['ui']['pause_note'],invitation.text())
                self.assertEqual([n.attrs['href'] for n in invitation.walk() if n.tag=='a'],['../../../essays/humor/index.html?lang=zh'])
                units+=len(nodes);headings+=sum(n.tag=='h2' for n in nodes)
                notes+=len(a['notes']);links+=len(a['sources'])
            self.assertEqual((units,headings,notes,links),(310,56,9,12))
            index=Parsed(self.pages[ROOT/self.spec['directory']/language/'index.html'])
            self.assertEqual(len(index.nodes('a','lw-card')),6)
            self.assertIn(data['series']['notice'],index.root.text())
            for p in data['series']['index_context']:self.assertIn(plain_markdown(p),index.root.text())

    def test_metadata_language_menus_local_destinations_and_analytics(self):
        for path,text in self.pages.items():
            page=Parsed(text);language=path.parent.name
            url='https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel')=='canonical'],[url])
            schema=next(json.loads(n.text()) for n in page.nodes('script') if n.attrs.get('type')=='application/ld+json')
            self.assertEqual(schema['url'],url);self.assertEqual(schema['inLanguage'],language)
            if path.stem!='index':
                a=next(a for a in self.data[language]['articles'] if a['slug']==path.stem)
                self.assertEqual(schema['citation'],[s['url'] for s in a['sources']])
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

    def test_missing_prose_notes_sources_or_real_approval_fail_closed(self):
        read_text=Path.read_text;target=BASE/'de.json'
        for mode in ('body','note','source','context','source-note'):
            def corrupted(p,*args,**kwargs):
                text=read_text(p,*args,**kwargs)
                if p!=target:return text
                data=json.loads(text)
                if mode=='body':data['articles'][0]['body'].pop()
                elif mode=='note':data['articles'][0]['notes'].pop()
                elif mode=='source':data['articles'][0]['sources'][0]['url']='https://example.invalid/'
                elif mode=='source-note':data['articles'][0]['source_note']=''
                else:data['series']['index_context'].pop()
                return json.dumps(data)
            with self.subTest(mode=mode),patch.object(Path,'read_text',corrupted),self.assertRaises(AssertionError):load_language(SERIES,'de')
        def bad_review(p,*args,**kwargs):
            text=read_text(p,*args,**kwargs)
            if p==BASE/'cross-review-de-fr.json':
                d=json.loads(text);d['articles_reviewed'].pop();return json.dumps(d)
            return text
        with patch.object(Path,'read_text',bad_review),self.assertRaises(AssertionError):prepare(SERIES)

    def test_discovery_search_sitemap_and_original_update_entries(self):
        from connect_full_series_languages import render as connections
        for p,t in connections(SERIES).items():self.assertEqual(p.read_text(),t,p)
        locations=[n.text for n in ElementTree.fromstring((ROOT/'sitemap.xml').read_text()).iter() if n.tag.rsplit('}',1)[-1]=='loc']
        for l in self.spec['languages']:
            records=json.loads((ROOT/'data/search'/(l+'.json')).read_text())['records']
            for slug in ['index',*self.spec['slugs']]:
                url=self.spec['directory']+'/'+l+'/'+slug+'.html'
                self.assertEqual(sum(r['u']==url for r in records),1)
                self.assertEqual(locations.count('https://nondubito.net/'+url.removesuffix('index.html')),1)


if __name__=='__main__':unittest.main()
