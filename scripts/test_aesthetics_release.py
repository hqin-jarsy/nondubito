"""Release checks need actual completed review seals and saved public outputs."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit,unquote
from xml.etree import ElementTree
from full_series_languages import ROOT,load_language,profile,render,alternatives
from prepare_original_series_review import prepare
from aesthetics_primary import strip_additions
from test_companion_languages import Parsed,Node,plain_markdown

SERIES='aesthetics'
BASE=ROOT/'data/aesthetics/multilingual'
LANGS=('de','fr','es','ja','ko')


class AestheticsRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=render(SERIES)  # Genuine real reviews required; no mock seal.
        cls.spec=profile(SERIES)
        cls.data={l:load_language(SERIES,l)[1] for l in LANGS}

    def test_genuine_seal_seventy_full_reading_records_and_output_identity(self):
        self.assertEqual(len(self.pages),75)
        for p,t in self.pages.items():self.assertEqual(p.read_text(),t,p)
        for p,t in prepare(SERIES).items():self.assertEqual(p.read_text(),t,p)
        records=[]
        for name in ('cross-review-de-fr.json','cross-review-ja-ko.json','cross-review-es.json'):
            review=json.loads((BASE/name).read_text())
            self.assertIs(review['publication_ready'],True)
            self.assertEqual(review['remaining'],[])
            records.extend((a['language'],a['slug']) for a in review['articles_reviewed'])
        self.assertEqual(len(records),70)
        self.assertEqual(set(records),{(l,s) for l in LANGS for s in self.spec['slugs']})
        receipt=json.loads((BASE/'publication.json').read_text())
        self.assertEqual(receipt['new_article_editions'],70)
        self.assertEqual(sum(receipt['source_units']),602)

    def test_each_full_body_note_and_reference_is_actually_rendered(self):
        for language,data in self.data.items():
            counts=[0,0,0,0]
            for article in data['articles']:
                page=Parsed(self.pages[ROOT/self.spec['directory']/language/(article['slug']+'.html')])
                body=page.nodes('div','lw-prose')[0]
                blocks=[n for n in body.children if isinstance(n,Node)]
                self.assertEqual(len(blocks),len(article['body']))
                self.assertNotRegex(body.text(),r'\b(?:13|14|15|16)DD\b')
                for block,p in zip(blocks,article['body']):
                    self.assertEqual(block.tag,'h2' if p.startswith('## ') else 'p')
                    self.assertEqual(block.text(),plain_markdown(p[3:] if p.startswith('## ') else p))
                sources=page.nodes('details','lw-sources')[0]
                self.assertNotIn('open',sources.attrs)
                paragraphs=[n for n in sources.children if isinstance(n,Node) and n.tag=='p']
                self.assertEqual([n.text() for n in paragraphs[-len(article['notes']):]],[plain_markdown(n) for n in article['notes']])
                links=[n for n in sources.walk() if n.tag=='li']
                self.assertEqual(len(links),len(article['sources']))
                for item,source in zip(links,article['sources']):
                    a=[n for n in item.walk() if n.tag=='a']
                    self.assertEqual([(n.text(),n.attrs['href']) for n in a],[(source['title'],source['url'])])
                counts=[counts[0]+len(blocks),counts[1]+sum(n.tag=='h2' for n in blocks),counts[2]+len(article['notes']),counts[3]+len(links)]
            self.assertEqual(counts,[602,65,14,24])

    def test_complete_equal_direction_routes_and_honest_existing_collection_links(self):
        for language,data in self.data.items():
            index=Parsed(self.pages[ROOT/self.spec['directory']/language/'index.html'])
            groups=index.nodes('section','lw-collection-group')
            self.assertEqual([g.attrs['id'] for g in groups],['begin','rays'])
            for group,spec in zip(groups,self.spec['index_groups']):
                self.assertEqual([n.attrs['href'] for n in group.walk() if n.tag=='a' and n.has_class('lw-card')],[s+'.html' for s in spec['slugs']])
            related=index.nodes('aside','lw-related')[0]
            actual={a.attrs['href']:a.text() for a in related.walk() if a.tag=='a'}
            root='../../../'
            for route in self.spec['reader_routes']:
                self.assertEqual(actual[root+route['path'].format(language=language)],data['ui'][route['label_key']])
            self.assertIn(root+'essays/art/'+language+'/index.html',actual)
            self.assertIn(root+'essays/aesthetics/en/index.html#feed',actual)
            self.assertIn(root+'essays/artist_dead.html?lang=en',actual)

    def test_true_separate_primary_urls_metadata_analytics_and_local_destinations(self):
        expected_primary={'en':('../en/','en'),'zh-Hans':('../','zh'),'zh-hant':('../zh-hant/','zh-hant')}
        for path,text in self.pages.items():
            page=Parsed(text);slug=path.stem;language=path.parent.name
            canonical='https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel')=='canonical'],[canonical])
            alts=[n for n in page.nodes('link') if n.attrs.get('rel')=='alternate']
            self.assertEqual(len(alts),9)
            self.assertEqual({n.attrs['hreflang'] for n in alts},{'x-default','en','zh-Hans','zh-Hant',*LANGS})
            options=page.nodes('div','site-shell-language-options')[0]
            choices=[n for n in options.walk() if n.tag=='a']
            self.assertEqual(len(choices),8)
            for code,(prefix,query) in expected_primary.items():
                self.assertEqual([n.attrs['href'] for n in choices if n.attrs['lang']==code],[prefix+slug+'.html?lang='+query])
            schema=json.loads([n.text() for n in page.nodes('script') if n.attrs.get('type')=='application/ld+json'][0])
            self.assertEqual(schema['url'],canonical)
            if slug!='index':
                article=next(a for a in self.data[language]['articles'] if a['slug']==slug)
                self.assertEqual(schema['citation'],[s['url'] for s in article['sources']])
            self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)
            for n in page.root.walk():
                raw=n.attrs.get('href') or n.attrs.get('src')
                if not raw:continue
                u=urlsplit(raw)
                if u.scheme or u.netloc:continue
                target=((ROOT/unquote(u.path.lstrip('/'))) if u.path.startswith('/') else path.parent/unquote(u.path)).resolve() if u.path else path
                if target.is_dir():target/='index.html'
                self.assertTrue(target.is_file(),(path,raw))
                if u.fragment:self.assertIn(unquote(u.fragment),{e.attrs.get('id') for e in Parsed(target.read_text()).root.walk()},(path,raw))

    def test_full_note_reference_and_genuine_reading_record_fail_closed(self):
        read=Path.read_text;target=BASE/'de.json'
        for mode in ('body','note','reference','group'):
            def corrupted(path,*args,**kwargs):
                text=read(path,*args,**kwargs)
                if path==target:
                    d=json.loads(text)
                    if mode=='body':d['articles'][0]['body'].pop()
                    elif mode=='note':d['articles'][0]['notes']=[]
                    elif mode=='reference':d['articles'][3]['sources'].pop()
                    else:d['series']['index_groups'][0]['id']='wrong'
                    return json.dumps(d)
                return text
            with self.subTest(mode=mode),patch.object(Path,'read_text',corrupted),self.assertRaises(AssertionError):load_language(SERIES,'de')
        def bad_review(path,*args,**kwargs):
            text=read(path,*args,**kwargs)
            if path==BASE/'cross-review-de-fr.json':
                d=json.loads(text);d['articles_reviewed'].pop();return json.dumps(d)
            return text
        with patch.object(Path,'read_text',bad_review),self.assertRaises(AssertionError):prepare(SERIES)
        # Coverage is an internal editorial mapping, never a substitute for
        # reading. Its accepted correction is nevertheless bound to the actual
        # saved field, just like reader-visible corrections.
        def bad_note_mapping(path,*args,**kwargs):
            text=read(path,*args,**kwargs)
            if path==BASE/'ko.json':
                d=json.loads(text);d['articles'][0]['notes_coverage'][0]='Unrelated source-note mapping';return json.dumps(d)
            return text
        with patch.object(Path,'read_text',bad_note_mapping),self.assertRaises(AssertionError):prepare(SERIES)

    def test_discovery_search_and_sitemap_only_after_real_publication(self):
        from connect_full_series_languages import render as connections
        for p,t in connections(SERIES).items():self.assertEqual(p.read_text(),t,p)
        sitemap=[n.text for n in ElementTree.fromstring((ROOT/'sitemap.xml').read_text()).iter() if n.tag.rsplit('}',1)[-1]=='loc']
        for language in LANGS:
            records=json.loads((ROOT/'data/search'/(language+'.json')).read_text())['records']
            for slug in ['index',*self.spec['slugs']]:
                url=self.spec['directory']+'/'+language+'/'+slug+'.html'
                self.assertEqual(sum(r['u']==url for r in records),1)
                self.assertEqual(sitemap.count('https://nondubito.net/'+url.removesuffix('index.html')),1)

    def test_bounded_ui_reapproval_preserves_the_original_primary_baseline(self):
        amendment=json.loads((BASE/'editorial-amendment-01.json').read_text())
        self.assertEqual(amendment['result'],'passed')
        self.assertEqual(amendment['remaining'],[])
        self.assertEqual(set(amendment['approved_review_record_changes']),{
            'data/aesthetics/multilingual/cross-review-ja-batch02.json',
            'data/aesthetics/multilingual/cross-review-ja-ko.json'})
        manuscript=json.loads((BASE/'ja.json').read_text())
        issue=amendment['finding']
        article=next(a for a in manuscript['articles'] if a['slug']==issue['slug'])
        self.assertEqual(article['body'][issue['paragraph']],amendment['saved_japanese_complete_field'])
        self.assertEqual(article['body'][issue['paragraph']],issue['after'])
        article['body'][issue['paragraph']]=issue['before']
        prior=(json.dumps(manuscript,ensure_ascii=False,indent=2)+'\n').encode()
        self.assertEqual(hashlib.sha256(prior).hexdigest(),amendment['prior_ja_manuscript_sha256'])
        preservation=json.loads((BASE/'preservation.json').read_text())
        original=json.loads((ROOT/self.spec['primary_baseline']).read_text())
        for key in ('source_data','primary_bodies','primary_main'):
            self.assertEqual(preservation[key],original[key])


if __name__=='__main__':unittest.main()
