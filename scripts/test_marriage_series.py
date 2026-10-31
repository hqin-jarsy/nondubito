#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publication, reading-path and editorial checks for the marriage essays."""
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote,urlsplit

from build_marriage_series import ROOT,DATA,BASE,DATE,MarriageTraditionalConverter,load_items,render
from build_content_registry import scan_page
from build_search_index import extract_recent_fiction_descriptions
from connect_marriage import render as entrances
from test_language_writing import Tags
from web_analytics import TOKEN


class MarriagePublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=load_items()
        cls.pages=render()
        cls.receipt=json.loads((DATA/'publication.json').read_text())

    def test_reproducible_nine_pages_and_entrances(self):
        self.assertEqual(len(self.items),8)
        self.assertEqual(len(self.pages),9)
        for path,text in {**self.pages,**entrances()}.items():
            self.assertEqual(path.read_text(),text)
            self.assertNotIn('TODO',text)

    def test_complete_three_reading_modes_and_recorded_lengths(self):
        for d in self.items:
            text=self.pages[ROOT/('essays/marriage/'+d['slug']+'.html')]
            bodies=dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>',text,re.S))
            self.assertEqual(set(bodies),{'en','zh','hant'})
            for body in bodies.values():
                self.assertGreaterEqual(body.count('<p>'),15 if not d['id'] else 24)
                self.assertEqual(body.count('<h2>'),2 if not d['id'] else 3)
                self.assertNotRegex(body,r'\b\d{2}DD\b|\bMA\d+\b|对象层|操作层|归属端点')
            self.assertNotRegex(bodies['en'],r'[\u3400-\u9fff]')
            self.assertEqual(bodies['zh'].count('<p>'),bodies['hant'].count('<p>'))
            self.assertEqual(self.receipt['counts'][d['slug']]['zh_han'],len(re.findall(r'[\u3400-\u9fff]',''.join(d['body_zh']))))
            self.assertEqual(self.receipt['counts'][d['slug']]['en_words'],len(' '.join(d['body_en']).split()))

    def test_canonical_schema_and_single_analytics_beacon(self):
        for path,text in self.pages.items():
            tags=Tags(text).items
            self.assertEqual([a['href'] for t,a in tags if t=='link' and a.get('rel')=='canonical'],[BASE+('' if path.name=='index.html' else path.name)])
            self.assertEqual(len([a for t,a in tags if t=='header']),1)
            self.assertEqual({a['class'] for t,a in tags if t=='h1'},{'lang-en','lang-zh','lang-hant'})
            self.assertEqual({a['data-set-language'] for t,a in tags if 'data-set-language' in a},{'en','zh','zh-hant'})
            beacons=[a for t,a in tags if t=='script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
            self.assertEqual(len(beacons),1)
            self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'],TOKEN)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
            self.assertEqual(schema['datePublished'],DATE)
            self.assertEqual(schema['inLanguage'],['en','zh-Hans','zh-Hant'])
            if path.name=='index.html':self.assertEqual(len(schema['hasPart']),8)
            else:
                d=next(d for d in self.items if d['slug']==path.stem)
                self.assertEqual(schema['citation'],d['source_url'])
                self.assertEqual(schema['isPartOf']['url'],BASE)

    def test_local_targets_fragments_and_unique_ids(self):
        for path,text in self.pages.items():
            tags=Tags(text).items
            ids=[a['id'] for t,a in tags if 'id' in a]
            self.assertEqual(len(ids),len(set(ids)))
            for tag,attrs in tags:
                raw=attrs.get('href' if tag in ('a','link') else 'src','')
                parts=urlsplit(raw)
                if not raw or parts.scheme or parts.netloc:continue
                target=ROOT/unquote(parts.path.lstrip('/')) if parts.path.startswith('/') else path.parent/unquote(parts.path)
                if parts.path:self.assertTrue(target.is_file(),f'{path}: {raw}')
                if parts.fragment:self.assertRegex(target.read_text() if parts.path else text,r'\bid=["\']'+re.escape(parts.fragment)+r'["\']')

    def test_sources_fiction_disclosure_and_safety(self):
        self.assertEqual({p['url'] for p in self.receipt['papers']},{d['source_url'] for d in self.items})
        for p in self.receipt['papers']:
            self.assertRegex(p['sha256'],r'^[0-9a-f]{64}$')
            self.assertTrue(p['matches_author_local'] and p['verified_https'])
        for text in self.pages.values():
            self.assertIn('fictional illustrations',text)
            self.assertIn('not a current-law guide',text)
            self.assertIn('not an entrance condition',text)
            self.assertIn('必要的安全与保护',text)

    def test_immediately_follows_love_without_a_compulsory_life_course(self):
        groups=json.loads((ROOT/'data/sae-reading-map.json').read_text())['groups']
        living=next(g for g in groups if g['id']=='living')
        urls=[d[0] for d in living['items']]
        self.assertEqual(urls[urls.index('essays/love/index.html')+1],'essays/marriage/index.html')
        for filename in ('library.html','essays/sae/index.html'):
            source=(ROOT/filename).read_text()
            self.assertLess(source.index('essays/love/index.html'),source.index('essays/marriage/index.html'))
        love=(ROOT/'essays/love/index.html').read_text()
        self.assertIn('../marriage/index.html',love)
        self.assertIn('不是爱情必须升级的下一站',love)
        landing=self.pages[ROOT/'essays/marriage/index.html']
        self.assertEqual(landing.count('class="lw-card"'),8)
        self.assertIn('不是每段婚姻必须走完的路线',landing)
        self.assertIn('有孩子不是义务',landing)
        for text in self.pages.values():
            for url in ('../love/index.html','../relation/index.html','../everyday/relationships/index.html','../everyday/parenting/index.html'):
                self.assertIn(url,text)

    def test_previous_next_navigation(self):
        for i,d in enumerate(self.items):
            text=self.pages[ROOT/('essays/marriage/'+d['slug']+'.html')]
            nav=re.search(r'<nav class="lw-series-nav".*?</nav>',text,re.S)[0]
            for n in (i-1,i+1):
                self.assertIn('href="'+(self.items[n]['slug']+'.html' if 0<=n<8 else 'index.html')+'"',nav)

    def test_search_sitemap_and_update_membership(self):
        expected={'essays/marriage/'+p.name for p in self.pages}
        for lang in ('en','zh-hans','zh-hant'):
            records=json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']
            rows=[r for r in records if r['u'].startswith('essays/marriage/')]
            self.assertEqual({r['u'] for r in rows},expected)
            self.assertTrue(all(r['d']=='sae-philosophy' for r in rows))
            for r in rows:
                self.assertIn('婚姻论',r['q'])
                if lang=='en':self.assertNotRegex(r['x'],r'[\u3400-\u9fff]')
                if r['u'].endswith('ep07.html'):self.assertIn('bereavement',r['q'])
                elif not r['u'].endswith('index.html'):self.assertNotIn('bereavement',r['q'])
        for path,text in self.pages.items():
            self.assertEqual(scan_page(ROOT,path)['domain'],'sae-philosophy')
            self.assertEqual(set(extract_recent_fiction_descriptions(text)),{'en','zh-Hans','zh-Hant'})
        urls={e.text for e in ET.parse(ROOT/'sitemap.xml').findall('{*}url/{*}loc')}
        self.assertTrue({BASE+('' if p.name=='index.html' else p.name) for p in self.pages}<=urls)
        updates=json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        matching=[u for u in updates if u['id']=='2026-10-30-marriage-series']
        self.assertEqual(len(matching),1)
        self.assertEqual(matching[0]['languages'],['zh','zh-hant','en'])

    def test_commitments_support_and_privacy_boundaries(self):
        zh=['\n'.join(d['body_zh']) for d in self.items]
        en=['\n'.join(d['body_en']) for d in self.items]
        for phrase in ('不是昨天的话每天作废','不替规则本身作正当性证明','不等于把一个人交给另一个人所有'):
            self.assertIn(phrase,zh[1])
        for phrase in ('不等于从此把这些地方的钥匙交出','人的地位','最后同意，不能倒过来'):
            self.assertIn(phrase,zh[2])
        for phrase in ('不是让所有的账从此看不见','决定还要学下去','不以未来拿到等额回报为成立条件'):
            self.assertIn(phrase,zh[3])
        self.assertIn('My fidelity does not purchase an authority over your feelings',en[1])
        self.assertIn('not a reason to make all accounting disappear',en[3])

    def test_years_newcomers_and_endings_keep_their_distinctions(self):
        zh=['\n'.join(d['body_zh']) for d in self.items]
        en=['\n'.join(d['body_en']) for d in self.items]
        for phrase in ('不要求两个人先变成同一种人','许多年没有冲突，也不能拿来作自动的好评','后来一个礼拜的客气'):
            self.assertIn(phrase,zh[4])
        for phrase in ('没有孩子到来','也不一定是还不存在','有没有孩子，不是婚姻的毕业证'):
            self.assertIn(phrase,zh[5])
        for phrase in ('婚姻结束，不自动让共同养育也结束','忘记的也是他','不要求孩子事实上搬走'):
            self.assertIn(phrase,zh[6])
        for phrase in ('理解不等于同意','不是要求一场指定形式的告别','制度中的婚姻解除','丧偶没有一个人收回自己的那一侧'):
            self.assertIn(phrase,zh[7])
        self.assertIn('Their grief need not match',en[5])
        self.assertIn('Dangerous contact is not an entrance fee for honesty',en[7])
        self.assertIn('date of death',en[7])

    def test_contextual_traditional(self):
        conv=MarriageTraditionalConverter()
        try:
            self.assertEqual(conv.convert('沈川沉默，周远发来文件；咨询与反复追问。'),'沈川沉默，周遠發來文件；諮詢與反覆追問。')
            self.assertEqual(conv.convert('吃碗面，再去面馆；复查、共同账户；天生干这个。'),'吃碗麵，再去麵館；複查、共同帳戶；天生幹這個。')
            for d in self.items:
                hant=''.join(conv.convert(p) for p in d['body_zh'])
                self.assertNotRegex(hant,r'沈默|沈積|公裡|咨詢|開啓|髮現|余項')
        finally:conv.close()

    def test_prior_love_and_relation_articles_unchanged(self):
        report=json.loads((ROOT/'reports/marriage-publication-20261030.json').read_text())
        hashes=report['preserved_article_sha256']
        self.assertEqual(len(hashes),16)
        for path,expected in hashes.items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected)


if __name__=='__main__':
    unittest.main(verbosity=2)
