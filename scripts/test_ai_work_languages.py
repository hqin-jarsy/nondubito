#!/usr/bin/env python3
"""Loss/misrouting regressions; structural success is not a prose-quality score."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree

from full_series_languages import (ROOT, profile, source_file, original_article,
    primary_bodies, load_language, render, render_prose, upgrade_primary)
from prepare_original_series_review import prepare, primary_main_hashes
from test_companion_languages import Node, Parsed, plain_markdown
from web_analytics import TOKEN

SERIES = 'ai-work'
BASE = ROOT/'data'/SERIES/'multilingual'
FOREIGN = ('de','fr','es','ja','ko')
COUNTS = (20,23,27,25,25,30,23,36)


def read(path):
    return json.loads(path.read_text())


def digest(value):
    return hashlib.sha256(value if isinstance(value,bytes) else value.encode()).hexdigest()


def children(node):
    return [n for n in node.children if isinstance(n,Node)]


class AIWorkLanguages(unittest.TestCase):
    def test_canonical_markdown_and_all_original_reading_content_preserved(self):
        spec=profile(SERIES)
        before=read(BASE/'primary-before-expansion.json')
        for path,text in prepare(SERIES).items():self.assertEqual(path.read_text(),text)
        after=read(BASE/'preservation.json')
        for key in ('source_data','primary_bodies','primary_main'):
            self.assertEqual(before[key],after[key])
        self.assertEqual(primary_main_hashes(spec),before['primary_main'])
        self.assertEqual(len(before['primary_main']),9)
        for slug in spec['slugs']:
            source=source_file(SERIES,spec,slug)
            self.assertEqual(source.suffix,'.md')
            self.assertEqual(digest(source.read_bytes()),before['source_data'][slug])
            self.assertFalse(source.with_suffix('.json').exists())
            text=(ROOT/spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(digest(primary_bodies(spec,text)),before['primary_bodies'][slug])
            self.assertEqual(len(Parsed(text).nodes('article','essay-body')),3)
        from build_ai_work_series import render as primary_render
        for path,text in primary_render().items():self.assertEqual(path.read_text(),text)

    def test_adapter_preserves_lists_turning_points_emphasis_and_all_arguments(self):
        spec=profile(SERIES)
        units=[original_article(SERIES,spec,s)['body_zh'] for s in spec['slugs']]
        self.assertEqual(tuple(map(len,units)),COUNTS)
        self.assertEqual(sum(x.startswith('## ') for a in units for x in a),41)
        self.assertEqual(sum(x.startswith('> ') for a in units for x in a),8)
        self.assertEqual(sum(x.startswith('- ') for a in units for x in a),17)
        self.assertEqual(render_prose(['- a','- b','p','1. c','2. d']),
                         '<ul><li>a</li><li>b</li></ul>\n<p>p</p>\n<ol><li>c</li><li>d</li></ol>')
        pages=render(SERIES)
        self.assertEqual(len(pages),45)
        for code in FOREIGN:
            _,data=load_language(SERIES,code)
            counts={'h2':0,'blockquote':0,'li':0,'em':0}
            for a in data['articles']:
                path=ROOT/spec['directory']/code/(a['slug']+'.html')
                self.assertEqual(path.read_text(),pages[path])
                page=Parsed(pages[path]);body=page.nodes('div','lw-prose')[0]
                flat=[]
                for n in children(body):
                    flat.extend(children(n) if n.tag in ('ul','ol') else [n])
                self.assertEqual(len(flat),len(a['body']))
                for source,node in zip(a['body'],flat):
                    kind='h2' if source.startswith('## ') else 'blockquote' if source.startswith('> ') else 'li' if source.startswith('- ') else 'p'
                    stripped=source[3:] if kind=='h2' else source[2:] if kind in ('blockquote','li') else source
                    self.assertEqual(node.tag,kind)
                    self.assertEqual(node.text(),plain_markdown(stripped))
                for n in body.walk():
                    if n.tag in counts:counts[n.tag]+=1
                self.assertEqual(page.nodes('h1')[0].text(),a['title'])
                self.assertIn(plain_markdown(a['source_note']),page.nodes('details','lw-sources')[0].text())
            self.assertEqual(counts,{'h2':41,'blockquote':8,'li':17,'em':4})

    def test_publication_gate_rejects_incomplete_review_changed_source_and_draft(self):
        prepare(SERIES);render(SERIES)
        original_text=Path.read_text
        for mode in ('approval','missing-reading'):
            def changed(path,*args,**kwargs):
                text=original_text(path,*args,**kwargs)
                if path==BASE/'cross-review-de-fr.json':
                    data=json.loads(text)
                    if mode=='approval':data['publication_ready']=False
                    else:data['articles_reviewed']=data['articles_reviewed'][:-1]
                    return json.dumps(data)
                return text
            with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):prepare(SERIES)
        original_bytes=Path.read_bytes
        spec=profile(SERIES)
        for target in (BASE/'de.json',source_file(SERIES,spec,spec['slugs'][0])):
            def changed_bytes(path):return original_bytes(path)+(b'\n' if path==target else b'')
            with patch.object(Path,'read_bytes',changed_bytes),self.assertRaises(AssertionError):render(SERIES)

    def test_existing_alternates_normalized_only_when_exactly_recognized(self):
        spec=profile(SERIES)
        from build_ai_work_series import alternates
        for slug in ['index',*spec['slugs']]:
            text=(ROOT/spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(upgrade_primary(text,SERIES,slug),text)
            raw=re.sub(r'<!-- MIXED SERIES ALTERNATES START -->.*?<!-- MIXED SERIES ALTERNATES END -->','',text,flags=re.S)
            raw=raw.replace('</head>',alternates('index.html' if slug=='index' else slug+'.html')+'</head>',1)
            self.assertEqual(upgrade_primary(raw,SERIES,slug),text)
            bad=raw.replace('hreflang="en"','hreflang="unknown"',1)
            with self.assertRaisesRegex(AssertionError,'unexpected primary alternates'):upgrade_primary(bad,SERIES,slug)

    def test_routes_context_sources_metadata_and_all_targets(self):
        spec=profile(SERIES);pages=render(SERIES)
        pages.update({ROOT/spec['directory']/(s+'.html'):(ROOT/spec['directory']/(s+'.html')).read_text() for s in ['index',*spec['slugs']]})
        for code in FOREIGN:
            _,data=load_language(SERIES,code)
            index=Parsed(pages[ROOT/spec['directory']/code/'index.html'])
            self.assertEqual([n.attrs['href'] for n in index.nodes('a','lw-card')],[s+'.html' for s in spec['slugs']])
            self.assertEqual(len(data['series']['index_context']),3)
            for unit in data['series']['index_context']:self.assertIn(plain_markdown(unit),index.root.text())
            main=children(index.nodes('main')[0])
            grid=index.nodes('section','lw-grid')[0]
            lead=next(n for n in main if n.has_class('lw-note') and data['series']['index_context'][0] in n.text())
            afterword=next(n for n in main if n.has_class('lw-note') and data['series']['index_context'][2] in n.text())
            self.assertLess(main.index(lead),main.index(grid))
            self.assertGreater(main.index(afterword),main.index(grid))
        for path,text in pages.items():
            page=Parsed(text);primary=path.parent.name==SERIES;slug=path.stem
            canonical='https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel')=='canonical'],[canonical])
            schema=[json.loads(n.text()) for n in page.nodes('script') if n.attrs.get('type')=='application/ld+json']
            self.assertEqual(len(schema),1)
            self.assertEqual(schema[0]['url'],canonical)
            self.assertEqual(schema[0]['datePublished'],'2026-09-10' if primary else spec['date'])
            self.assertEqual(schema[0]['inLanguage'],['en','zh-Hans','zh-Hant'] if primary else path.parent.name)
            self.assertEqual(schema[0]['@type'],'CollectionPage' if slug=='index' else 'Article')
            if not primary:
                if slug=='index':
                    self.assertEqual([p['url'] for p in schema[0]['hasPart']],
                        ['https://nondubito.net/'+spec['directory']+'/'+path.parent.name+'/'+s+'.html' for s in spec['slugs']])
                    self.assertIn(spec['source'],[n.attrs.get('href') for n in page.nodes('details','lw-sources')[0].walk()])
                else:
                    self.assertEqual(schema[0]['citation'],spec['source'])
                options=page.nodes('div','site-shell-language-options')[0]
                options=[n for n in options.walk() if n.tag=='a']
                expected={code if code!='zh' else 'zh-Hans':('../'+slug+'.html?lang='+code if code in ('en','zh','zh-hant') else '../'+code+'/'+slug+'.html') for code in ('en','zh','zh-hant',*FOREIGN)}
                self.assertEqual(len(options),8)
                self.assertEqual({n.attrs['lang']:n.attrs['href'] for n in options},expected)
                self.assertEqual([n.attrs['lang'] for n in options if n.attrs.get('aria-current')=='page'],[path.parent.name])
            suffix='' if slug=='index' else slug+'.html'
            origin='https://nondubito.net/'+spec['directory']+'/'
            alts=[n for n in page.nodes('link') if n.attrs.get('rel')=='alternate']
            self.assertEqual(len(alts),7)
            self.assertEqual({n.attrs['hreflang']:n.attrs['href'] for n in alts},
                             {'x-default':origin+suffix,'zh-Hans':origin+suffix,**{code:origin+code+'/'+suffix for code in FOREIGN}})
            beacons=[n for n in page.nodes('script') if 'cloudflareinsights.com/beacon.min.js' in n.attrs.get('src','')]
            self.assertEqual(len(beacons),1)
            self.assertEqual(json.loads(beacons[0].attrs['data-cf-beacon'])['token'],TOKEN)
            ids=[n.attrs['id'] for n in page.root.walk() if 'id' in n.attrs]
            self.assertEqual(len(ids),len(set(ids)))
            for n in page.root.walk():
                raw=n.attrs.get('href') or n.attrs.get('src')
                if not raw:continue
                url=urlsplit(raw)
                if url.scheme or url.netloc:continue
                target=(ROOT/unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent/unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_file(),(path,raw))
                if url.fragment:self.assertIn(url.fragment,{n.attrs.get('id') for n in Parsed(target.read_text()).root.walk()})

    def test_discovery_and_no_primary_ledger_overwrite(self):
        spec=profile(SERIES);entry=read(BASE/'discovery.json')
        ledger=read(ROOT/'data/site-updates.json')['updates']
        self.assertEqual(sum(u['id']==entry['id'] for u in ledger),1)
        old=[u for u in ledger if u['id']=='2026-09-10-ai-work-flagship']
        self.assertEqual(len(old),1)
        self.assertEqual(digest(json.dumps(old[0],ensure_ascii=False,sort_keys=True,separators=(',',':'))),
                         'b5903c524fb57126f4f537d580e8233e20b350bc1615342ceeff7dd8dcb13da7')
        self.assertIn('href="essays/ai-work/index.html" class="series-card series-card-flagship"',(ROOT/'library.html').read_text())
        urls=[n.text for n in ElementTree.fromstring((ROOT/'sitemap.xml').read_text()).iter() if n.tag.rsplit('}',1)[-1]=='loc']
        for code in FOREIGN:
            records=read(ROOT/'data/search'/(code+'.json'))['records']
            native=[r for r in records if r['u'].startswith('essays/ai-work/'+code+'/')]
            self.assertEqual(len(native),9)
            self.assertEqual({r['d'] for r in native},{'mind-ai'})
            for slug in spec['slugs']:
                url='essays/ai-work/'+code+'/'+slug+'.html'
                self.assertEqual(sum(r['u']==url for r in records),1)
                self.assertEqual(urls.count('https://nondubito.net/'+url),1)


if __name__=='__main__':unittest.main(verbosity=2)
