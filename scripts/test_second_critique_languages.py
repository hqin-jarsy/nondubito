"""Final complete-edition regressions; run after genuine editorial sealing."""
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit,unquote
from xml.etree import ElementTree

from full_series_languages import (ROOT,profile,load_language,render,upgrade_primary,
    original_article,inline_markdown)
from prepare_original_series_review import prepare
from test_companion_languages import Node,Parsed,plain_markdown
from web_analytics import TOKEN

SERIES='sae-second-critique'
BASE=ROOT/'data'/SERIES/'multilingual'
FOREIGN=('de','fr','es','ja','ko')
DOI='https://doi.org/10.5281/zenodo.23250387'


def read(path):return json.loads(path.read_text())


class SecondCritiqueLanguages(unittest.TestCase):
    def test_genuine_full_review_and_original_preservation_receipts(self):
        spec=profile(SERIES)
        for path,text in prepare(SERIES).items():self.assertEqual(path.read_text(),text)
        before=read(BASE/'primary-before-expansion.json');after=read(BASE/'preservation.json')
        for key in ('source_data','primary_bodies','primary_main'):self.assertEqual(before[key],after[key])
        for name,digest in before['hant_dictionaries'].items():
            self.assertEqual(after['protected_files'][name],digest)
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
        receipt=read(BASE/'publication.json')
        self.assertEqual(receipt['new_article_editions'],60)
        self.assertEqual(receipt['source_units'],[21]+[20]*11)
        for language in FOREIGN:
            _,data=load_language(SERIES,language)
            self.assertEqual(len(data['articles']),12)
            self.assertEqual(sum(len(a['body']) for a in data['articles']),241)
        old_bytes=Path.read_bytes
        hant_path=ROOT/next(iter(before['hant_dictionaries']))
        def changed_hant(path):return old_bytes(path)+(b'\n' if path==hant_path else b'')
        with patch.object(Path,'read_bytes',changed_hant),self.assertRaisesRegex(AssertionError,'Traditional Chinese dictionary differs'):
            prepare(SERIES)
        prepare(SERIES);old_read=Path.read_text
        for mode in ('approval','reading'):
            def changed(path,*a,**kw):
                text=old_read(path,*a,**kw)
                if path==BASE/'cross-review-de-fr.json':
                    report=json.loads(text)
                    if mode=='approval':report['publication_ready']=False
                    else:report['articles_reviewed']=report['articles_reviewed'][:-1]
                    return json.dumps(report)
                return text
            with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):prepare(SERIES)
        render(SERIES);old_bytes=Path.read_bytes
        def changed_bytes(path):return old_bytes(path)+(b'\n' if path==BASE/'de.json' else b'')
        with patch.object(Path,'read_bytes',changed_bytes),self.assertRaisesRegex(AssertionError,'draft changed'):
            render(SERIES)

    def test_sixty_full_dom_bodies_keep_all_emphasis_and_source_notes(self):
        spec=profile(SERIES);pages=render(SERIES)
        self.assertEqual(len(pages),65)
        for language in FOREIGN:
            _,data=load_language(SERIES,language)
            totals={'h2':0,'strong':0,'em':0}
            for a in data['articles']:
                path=ROOT/spec['directory']/language/(a['slug']+'.html')
                self.assertEqual(path.read_text(),pages[path])
                page=Parsed(pages[path]);body=page.nodes('div','lw-prose')[0]
                children=[n for n in body.children if isinstance(n,Node)]
                self.assertEqual(len(children),len(a['body']))
                source=original_article(SERIES,spec,a['slug'])['body_zh']
                for src,unit,node in zip(source,a['body'],children):
                    heading=unit.startswith('## ')
                    self.assertEqual(node.tag,'h2' if heading else 'p')
                    self.assertEqual(node.text(),plain_markdown(unit[3:] if heading else unit))
                    for tag in ('strong','em'):
                        self.assertEqual(sum(n.tag==tag for n in node.walk()),inline_markdown(src).count('<'+tag+'>'))
                for node in body.walk():
                    if node.tag in totals:totals[node.tag]+=1
                self.assertEqual(page.nodes('h1')[0].text(),a['title'])
                sources=page.nodes('details','lw-sources')[0]
                self.assertIn(plain_markdown(a['source_note']),sources.text())
                hrefs=[n.attrs.get('href') for n in sources.walk()]
                self.assertIn(spec['source'],hrefs);self.assertIn(DOI,hrefs)
                self.assertFalse(page.nodes('aside','jg-pause'))
            self.assertEqual(totals,{'h2':60,'strong':254,'em':17})

    def test_lost_emphasis_and_block_changes_cannot_pass_loader(self):
        load_language(SERIES,'es');old=Path.read_text
        for mode in ('strong','em','heading'):
            def changed(path,*a,**kw):
                text=old(path,*a,**kw)
                if path==BASE/'es.json':
                    data=json.loads(text);body=data['articles'][0]['body']
                    marker='**' if mode=='strong' else '*' if mode=='em' else '## '
                    i=next(i for i,p in enumerate(body) if marker in p and (mode!='em' or '*' in p.replace('**','')))
                    body[i]=body[i].replace(marker,'',1)
                    return json.dumps(data)
                return text
            with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):load_language(SERIES,'es')

    def test_three_entry_choices_prerequisites_and_all_twelve_cards(self):
        spec=profile(SERIES)
        for language in FOREIGN:
            _,data=load_language(SERIES,language)
            page=Parsed((ROOT/spec['directory']/language/'index.html').read_text())
            self.assertEqual([n.attrs['href'] for n in page.nodes('a','lw-card')],[s+'.html' for s in spec['slugs']])
            entries=next(n for n in page.nodes('nav','lw-note'))
            self.assertEqual([(n.attrs['href'],n.text()) for n in entries.walk() if n.tag=='a'],
                list(zip(['ep01.html','ep05.html','ep11.html'],data['series']['entry_labels'])))
            main=[n for n in page.nodes('main')[0].children if isinstance(n,Node)]
            grid=page.nodes('section','lw-grid')[0]
            self.assertLess(main.index(entries),main.index(grid))
            for unit in data['series']['index_context']:self.assertIn(plain_markdown(unit),page.root.text())
            related=page.nodes('aside','lw-related')[0]
            hrefs=[n.attrs.get('href') for n in related.walk()]
            for target in ('sae-foundations','sae-first-critique','action'):
                self.assertIn('../../../essays/'+target+'/'+language+'/index.html',hrefs)

    def test_metadata_controls_analytics_and_local_routes(self):
        spec=profile(SERIES);pages=render(SERIES)
        pages.update({ROOT/spec['directory']/(s+'.html'):(ROOT/spec['directory']/(s+'.html')).read_text() for s in ['index',*spec['slugs']]})
        for path,text in pages.items():
            primary=path.parent.name==SERIES;slug=path.stem;page=Parsed(text)
            url='https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel')=='canonical'],[url])
            self.assertEqual([n.attrs['content'] for n in page.nodes('meta') if n.attrs.get('property')=='og:url'],[url])
            schemas=[json.loads(n.text()) for n in page.nodes('script') if n.attrs.get('type')=='application/ld+json']
            if primary:
                self.assertEqual(schemas,[])  # Preserve, do not invent historical metadata.
                self.assertEqual(upgrade_primary(text,SERIES,slug),text)
                self.assertIn("var requested=new URLSearchParams(location.search).get('lang');",text)
                for language in FOREIGN:self.assertIn('href="'+language+'/'+slug+'.html"',text)
            else:
                self.assertEqual(len(schemas),1);schema=schemas[0]
                self.assertEqual(schema['url'],url)
                self.assertEqual(schema['@type'],'CollectionPage' if slug=='index' else 'Article')
                self.assertEqual(schema['inLanguage'],path.parent.name)
                if slug=='index':self.assertEqual(len(schema['hasPart']),12)
                else:self.assertEqual(schema['citation'],spec['source'])
                links=[n for n in page.nodes('div','site-shell-language-options')[0].walk() if n.tag=='a']
                expected={code if code!='zh' else 'zh-Hans':('../'+slug+'.html?lang='+code if code in ('en','zh','zh-hant') else '../'+code+'/'+slug+'.html') for code in ('en','zh','zh-hant',*FOREIGN)}
                self.assertEqual({n.attrs['lang']:n.attrs['href'] for n in links},expected)
                self.assertEqual(len(links),8)
            alts=[n for n in page.nodes('link') if n.attrs.get('rel')=='alternate']
            suffix='' if slug=='index' else slug+'.html';origin='https://nondubito.net/'+spec['directory']+'/'
            self.assertEqual(len(alts),7)
            self.assertEqual({n.attrs['hreflang']:n.attrs['href'] for n in alts},{'x-default':origin+suffix,'zh-Hans':origin+suffix,**{code:origin+code+'/'+suffix for code in FOREIGN}})
            beacons=[n for n in page.nodes('script') if 'cloudflareinsights.com/beacon.min.js' in n.attrs.get('src','')]
            self.assertEqual(len(beacons),1)
            self.assertEqual(json.loads(beacons[0].attrs['data-cf-beacon'])['token'],TOKEN)
            ids=[n.attrs['id'] for n in page.root.walk() if 'id' in n.attrs];self.assertEqual(len(ids),len(set(ids)))
            for node in page.root.walk():
                raw=node.attrs.get('href') or node.attrs.get('src')
                if not raw:continue
                address=urlsplit(raw)
                if address.scheme or address.netloc:continue
                target=(ROOT/unquote(address.path.lstrip('/')) if address.path.startswith('/') else path.parent/unquote(address.path)).resolve() if address.path else path
                self.assertTrue(target.is_file(),(path,raw))
                if address.fragment:self.assertIn(address.fragment,{n.attrs.get('id') for n in Parsed(target.read_text()).root.walk()})

    def test_search_sitemap_and_single_complete_update(self):
        spec=profile(SERIES);entry=read(BASE/'discovery.json')
        ledger=read(ROOT/'data/site-updates.json')['updates'];self.assertEqual(sum(e['id']==entry['id'] for e in ledger),1)
        old=[e for e in ledger if e['id']=='2026-10-10-second-critique-series']
        self.assertEqual(len(old),1)
        self.assertEqual(hashlib.sha256(json.dumps(old[0],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            '056d304f043dbad6707a7b2fdb1d4d6c4bfda287030ef866e3eea753beb3cb6f')
        urls=[n.text for n in ElementTree.fromstring((ROOT/'sitemap.xml').read_text()).iter() if n.tag.rsplit('}',1)[-1]=='loc']
        for language in FOREIGN:
            records=read(ROOT/'data/search'/(language+'.json'))['records']
            native=[r for r in records if r['u'].startswith('essays/'+SERIES+'/'+language+'/')]
            self.assertEqual(len(native),13);self.assertEqual({r['d'] for r in native},{'sae-philosophy'})
            for slug in spec['slugs']:
                url='essays/'+SERIES+'/'+language+'/'+slug+'.html'
                self.assertEqual(sum(r['u']==url for r in records),1)
                self.assertEqual(urls.count('https://nondubito.net/'+url),1)


if __name__=='__main__':unittest.main(verbosity=2)
