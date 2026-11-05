"""Accept only real complete six-language readings and their saved editions."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote,urlsplit
from xml.etree import ElementTree

from full_series_languages import ROOT,load_language,profile,render,upgrade_primary
from prepare_original_series_review import prepare
from fairy_tales_primary import english_body,search_decks
from test_companion_languages import Node,Parsed,plain_markdown

BASE=ROOT/'data/fairy-tales/multilingual'


def plain_note(value,sources):
    # Independent exact-URL expectation; never use the renderer's link parser.
    for source in sources:
        value=re.sub(r'\[([^\]]+)\]\('+re.escape(source['url'])+r'\)',r'\1',value)
    assert '](' not in value,'Unknown or truncated link in expected note'
    return value.replace('**','').replace('*','')


class FairyTalesRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=profile('fairy-tales')
        cls.pages=render('fairy-tales')
        cls.data={l:load_language('fairy-tales',l)[1] for l in [*cls.spec['languages'],'en']}

    def test_genuine_complete_reviews_include_english_not_only_five_new_languages(self):
        self.assertEqual(len(self.pages),155)
        for p,t in prepare('fairy-tales').items():self.assertEqual(p.read_text(),t,p)
        seen=[]
        for name in ['cross-review-de-fr.json','cross-review-ja-ko.json','cross-review-es.json','cross-review-en.json']:
            r=json.loads((BASE/name).read_text())
            self.assertIs(r['publication_ready'],True)
            self.assertEqual(r['remaining'],[])
            seen.extend((a['language'],a['slug']) for a in r['articles_reviewed'])
        expected={(l,s) for l in self.data for s in self.spec['slugs']}
        self.assertEqual(len(seen),180)
        self.assertEqual(set(seen),expected)
        receipt=json.loads((BASE/'publication.json').read_text())
        self.assertEqual(sum(receipt['source_units']),595)
        self.assertEqual(receipt['new_article_editions'],150)
        self.assertEqual(receipt['upgraded_primary_article_editions'],30)
        self.assertEqual(set(receipt['language_data_sha256']),set(self.data))

    def test_all_foreign_prose_full_notes_exact_sources_and_six_groups(self):
        for language in self.spec['languages']:
            data=self.data[language];units=notes=refs=0
            for a in data['articles']:
                path=ROOT/self.spec['directory']/language/(a['slug']+'.html')
                page=Parsed(self.pages[path])
                nodes=[n for n in page.nodes('div','lw-prose')[0].children if isinstance(n,Node)]
                self.assertEqual([n.tag for n in nodes],['p']*len(a['body']))
                self.assertEqual([n.text() for n in nodes],[plain_markdown(v) for v in a['body']])
                source=page.nodes('details','lw-sources')[0]
                self.assertNotIn('open',source.attrs)
                paragraphs=[n.text() for n in source.children if isinstance(n,Node) and n.tag=='p']
                self.assertEqual(paragraphs,[plain_note(v,a['sources']) for v in [a['source_note'],*a['notes']]])
                refs_node=next(n for n in source.children if isinstance(n,Node) and n.tag=='ul')
                self.assertEqual([n.attrs['href'] for n in refs_node.walk() if n.tag=='a'],[s['url'] for s in a['sources']])
                self.assertTrue(all(n.attrs['href'] in {s['url'] for s in a['sources']} for n in source.walk() if n.tag=='a'))
                units+=len(nodes);notes+=len(a['notes']);refs+=len(a['sources'])
            self.assertEqual((units,notes,refs),(595,30,46))
            index=Parsed(self.pages[ROOT/self.spec['directory']/language/'index.html'])
            self.assertEqual(len(index.nodes('a','lw-card')),30)
            self.assertEqual(len(index.nodes('section','lw-collection-group')),6)
            for p in data['series']['index_context']:self.assertIn(plain_markdown(p),index.root.text())
            for slug in self.spec['entry_slugs']:
                self.assertGreaterEqual(sum(n.attrs.get('href')==slug+'.html' for n in index.nodes('a')),2)
            labels=data['series']['entry_labels']
            if isinstance(labels,dict):labels=[labels[s] for s in self.spec['entry_slugs']]
            route=next(n for n in index.nodes('nav','lw-note') if any(c.tag=='h2' and c.text()==data['ui']['entry_routes'] for c in n.children if isinstance(c,Node)))
            self.assertEqual([n.text() for n in route.walk() if n.tag=='a'],labels)

    def test_authorized_complete_english_is_actually_in_saved_primary_html(self):
        for slug in ['index',*self.spec['slugs']]:
            path=ROOT/self.spec['directory']/(slug+'.html')
            self.assertEqual(path.read_text(),upgrade_primary(path.read_text(),'fairy-tales',slug),path)
        index=Parsed((ROOT/self.spec['directory']/'index.html').read_text())
        english_index=next(n for n in index.nodes('div','local') if 'lang-en' in n.attrs.get('class','').split())
        archive=json.loads((BASE/'original-english-bodies.json').read_text())
        for a in self.data['en']['articles']:
            card=next(n for n in english_index.walk() if n.tag=='a' and n.attrs.get('href')==a['slug']+'.html' and 'essay-card' in n.attrs.get('class','').split())
            self.assertEqual([n.text() for n in card.walk() if n.tag=='p'],[archive['original_index_english_card_decks'][a['slug']]['prefix']+a['deck']])
        units=notes=refs=0
        for a in self.data['en']['articles']:
            path=ROOT/self.spec['directory']/(a['slug']+'.html')
            full_page=Parsed(path.read_text())
            descriptions=[n.attrs['content'] for n in full_page.nodes('meta') if n.attrs.get('name')=='description' or n.attrs.get('property')=='og:description']
            self.assertEqual(descriptions,[a['deck'],a['deck']])
            page=Parsed('<div>'+english_body(path.read_text())+'</div>')
            container=page.nodes('div')[0]
            paragraphs=[n.text() for n in container.children if isinstance(n,Node) and n.tag=='p']
            self.assertEqual(paragraphs,[plain_markdown(v) for v in a['body']]+[plain_note(v,a['sources']) for v in [*a['notes'],a['source_note']]])
            refs_node=page.nodes('ul','fairy-source-links')[0]
            self.assertEqual([n.attrs['href'] for n in refs_node.walk() if n.tag=='a'],[s['url'] for s in a['sources']])
            self.assertTrue(all(n.attrs['href'] in {s['url'] for s in a['sources']} for n in page.nodes('a')))
            units+=len(a['body']);notes+=len(a['notes']);refs+=len(a['sources'])
        self.assertEqual((units,notes,refs),(595,30,46))

    def test_native_metadata_destinations_eight_options_and_one_beacon(self):
        for path,text in self.pages.items():
            self.assertEqual(path.read_text(),text,path)
            page=Parsed(text)
            canonical='https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel')=='canonical'],[canonical])
            schema=next(json.loads(n.text()) for n in page.nodes('script') if n.attrs.get('type')=='application/ld+json')
            self.assertEqual(schema['url'],canonical)
            self.assertEqual(schema['inLanguage'],path.parent.name)
            self.assertEqual(len(page.nodes('div','site-shell-language-options')[0].children),8)
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

    def test_unreviewed_same_shape_english_or_other_language_is_not_resealed(self):
        original=Path.read_text
        for language in ['en','de']:
            target=BASE/(language+'.json')
            def corrupted(path,*args,**kwargs):
                text=original(path,*args,**kwargs)
                if path==target:
                    data=json.loads(text);body=data['articles'][0]['body']
                    body[0]=body[0][:-1]+('!' if body[0][-1]!='!' else '?')
                    return json.dumps(data,ensure_ascii=False)
                return text
            with self.subTest(language=language),patch.object(Path,'read_text',corrupted),self.assertRaises(AssertionError):prepare('fairy-tales')

    def test_discovery_search_sitemap_and_preexisting_updates(self):
        from connect_fairy_tales_languages import render as connections
        for p,t in connections().items():self.assertEqual(p.read_text(),t,p)
        locations=[n.text for n in ElementTree.fromstring((ROOT/'sitemap.xml').read_text()).iter() if n.tag.rsplit('}',1)[-1]=='loc']
        for language in self.data:
            records=json.loads((ROOT/'data/search'/(language+'.json')).read_text())['records']
            for slug in ['index',*self.spec['slugs']]:
                url=self.spec['directory']+('/'+language if language!='en' else '')+'/'+slug+'.html'
                self.assertEqual(sum(r['u']==url for r in records),1,(language,url))
                self.assertEqual(locations.count('https://nondubito.net/'+url.removesuffix('index.html')),1)
        english={a['slug']:a for a in self.data['en']['articles']}
        localized={l:json.loads((ROOT/'data/search'/(l.lower()+'.json')).read_text())['records'] for l in ('en','zh-Hans','zh-Hant')}
        for slug in ['index',*self.spec['slugs']]:
            decks=search_decks(self.spec,slug,english[slug]['deck'] if slug!='index' else None)
            url=self.spec['directory']+'/'+slug+'.html'
            for language,deck in decks.items():
                matches=[r for r in localized[language] if r['u']==url]
                self.assertEqual(len(matches),1,(language,url))
                self.assertEqual(matches[0]['x'],deck,(language,url,'localized search description'))
        before=json.loads((BASE/'primary-before-expansion.json').read_text())
        ledger=json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        ids=set(before['preexisting_update_ids'])
        old=[u for u in ledger if u['id'] in ids]
        self.assertEqual(len(old),len(ids))
        self.assertEqual(hashlib.sha256(json.dumps(old,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),before['preexisting_update_entries_sha256'])


if __name__=='__main__':unittest.main()
