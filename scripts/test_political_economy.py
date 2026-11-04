#!/usr/bin/env python3
"""Check complete editions, evidence boundaries and durable discovery routes."""
import html
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

from build_political_economy import ROOT, DATA, BASE, DATE, load_items, render
from connect_political_economy import render as entrances
from build_content_registry import scan_page
from test_language_writing import Tags
from web_analytics import TOKEN


class PoliticalEconomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.pages = render()
        cls.receipt = json.loads((DATA/'publication-batch01.json').read_text())
        cls.receipt['counts'].update(json.loads((DATA/'publication-batch02.json').read_text())['counts'])
        cls.receipt['counts'].update(json.loads((DATA/'publication-batch03.json').read_text())['counts'])
        cls.receipt['counts'].update(json.loads((DATA/'publication-batch04.json').read_text())['counts'])
        cls.receipt['counts'].update(json.loads((DATA/'publication-batch05.json').read_text())['counts'])

    def test_reproducible_pages_and_entrances(self):
        self.assertEqual(len(self.pages), 11)
        for p, text in {**self.pages, **entrances()}.items():
            self.assertEqual(p.read_text(), text)
            self.assertNotIn('TODO', text)

    def test_complete_three_reading_modes(self):
        for d in self.items:
            self.assertEqual(self.receipt['counts'][d['slug']]['zh_han'], len(re.findall(r'[\u3400-\u9fff]', ''.join(d['body_zh']))))
            self.assertEqual(self.receipt['counts'][d['slug']]['en_words'], len(' '.join(d['body_en']).split()))
            text = self.pages[ROOT / ('essays/political-economy/' + d['slug'] + '.html')]
            bodies = dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', text, re.S))
            self.assertEqual(set(bodies), {'en', 'zh', 'hant'})
            self.assertEqual(bodies['zh'].count('<p>'), bodies['hant'].count('<p>'))
            for body in bodies.values():
                self.assertGreaterEqual(body.count('<p>'), {'introduction':16, 'interlude':18, 'case':22}[d['kind']])
                self.assertEqual(body.count('<h2>'), 3 if d['kind'] == 'case' else 2)
                self.assertNotRegex(body, r'\b\d{2}DD\b|\b[EFGZ]\d+\b||turn\d+(?:view|search)')
            self.assertNotRegex(bodies['en'], r'[\u3400-\u9fff]')
            self.assertNotRegex(bodies['hant'], r'覈實|覈對|復核|標簽|髮款|被系在|余項|籤償還|籤下|籤了和解|看准|失准|准入')

    def test_intro_stays_short_and_distinguishes_voice_from_exit(self):
        d = self.items[0]
        self.assertLess(len(re.findall(r'[\u3400-\u9fff]', ''.join(d['body_zh']))), 1800)
        self.assertLess(len(' '.join(d['body_en']).split()), 1100)
        self.assertIn('不只问能不能走', ''.join(d['body_zh']))
        self.assertIn('stay and challenge', ''.join(d['body_en']))
        self.assertNotIn('青窑', ''.join(d['body_zh']))
        self.assertNotIn('Crossways', ''.join(d['body_en']))

    def test_numbered_original_sources(self):
        self.assertEqual([len(d['sources']) for d in self.items], [5, 3, 6, 4, 4, 4, 5, 4, 4, 3])
        for d in self.items:
            for lang in ('en', 'zh'):
                self.assertEqual(set(map(int, re.findall(r'\[(\d+)\]', '\n'.join(d['body_' + lang])))), {s['id'] for s in d['sources']})
            page = self.pages[ROOT/('essays/political-economy/' + d['slug'] + '.html')]
            for s in d['sources']:
                self.assertIn(s['url'].replace('&', '&amp;'), page)

    def test_petsmart_dates_amounts_and_evidence_status(self):
        d = self.items[1]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('五千五百', '两千七百五十', '培训开始', '三十天', '被公司解雇', '州方的调查主张', '生效前数年', '2026年2月17日', '否认不当行为'):
            self.assertIn(phrase, zh)
        for phrase in ('$5,500', '$2,750', 'Dismissal', 'within thirty days', 'years before', '17 February 2026', 'not findings after a trial'):
            self.assertIn(phrase, en)
        self.assertIn('not independent proof of the date of judicial entry', d['sources'][1]['note_en'])

    def test_amazon_distinguishes_services_and_proceedings(self):
        d = self.items[2]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('三者相关，却不是同一个东西', '原告提出的机制', '2026年11月1日', '2026年10月30日', '不作违反欧盟竞争规则的认定', 'Amazon 的答辩'):
            self.assertIn(phrase, zh)
        for phrase in ('not the same thing', 'alleged mechanism', 'must not be presented as an adjudication of liability', 'separate European proceeding', 'Those explanations should not be treated merely as camouflage'):
            self.assertIn(phrase, en)
        self.assertIn('redacted numbers are not reconstructed', d['sources'][0]['note_en'])

    def test_metadata_and_analytics(self):
        for p, text in self.pages.items():
            tags = Tags(text).items
            url = BASE + ('' if p.name == 'index.html' else p.name)
            self.assertEqual([a['href'] for t,a in tags if t == 'link' and a.get('rel') == 'canonical'], [url])
            self.assertEqual(len([a for t,a in tags if t == 'header']), 1)
            self.assertEqual({a['class'] for t,a in tags if t == 'h1'}, {'lang-en', 'lang-zh', 'lang-hant'})
            beacons = [a for t,a in tags if t == 'script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
            self.assertEqual(len(beacons), 1)
            self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'], TOKEN)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
            self.assertEqual(schema['inLanguage'], ['en', 'zh-Hans', 'zh-Hant'])
            if p.name == 'index.html':
                self.assertEqual(schema['datePublished'], self.items[0]['date'])
                self.assertEqual(schema['dateModified'], DATE)
                self.assertEqual(len(schema['hasPart']), 10)
            else:
                d = next(d for d in self.items if d['slug'] == p.stem)
                self.assertEqual(schema['datePublished'], d['date'])
                self.assertEqual(schema['dateModified'], DATE)  # New theory companion links; publication unchanged.
                self.assertEqual(schema['citation'], [s['url'] for s in d['sources']])
                self.assertEqual(schema['isPartOf']['url'], BASE)

    def test_local_links_and_unique_ids(self):
        for p, text in self.pages.items():
            tags = Tags(text).items
            ids = [a['id'] for t,a in tags if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)))
            for tag, attrs in tags:
                raw = attrs.get('href' if tag in ('a','link') else 'src', '')
                u = urlsplit(raw)
                if not raw or u.scheme or u.netloc:
                    continue
                target = ROOT/unquote(u.path.lstrip('/')) if u.path.startswith('/') else p.parent/unquote(u.path)
                if u.path:
                    self.assertTrue(target.is_file(), str(p) + ': ' + raw)
                if u.fragment:
                    self.assertRegex(target.read_text() if u.path else text, r'\bid=["\']' + re.escape(u.fragment) + r'["\']')

    def test_open_ended_landing_and_navigation(self):
        text = self.pages[ROOT/'essays/political-economy/index.html']
        self.assertEqual(text.count('class="lw-card"'), 8)
        self.assertIn('href="introduction.html"', text)
        self.assertIn('An ongoing series', text)
        for name in ('library.html','explore.html','latest.html','essays/sae/index.html'):
            self.assertIn('essays/political-economy/index.html', (ROOT/name).read_text())
        groups = json.loads((ROOT/'data/sae-reading-map.json').read_text())['groups']
        self.assertEqual(len(groups), 6)
        shared = next(g for g in groups if g['id'] == 'shared-life')
        self.assertEqual(sum(x[0] == 'essays/political-economy/index.html' for x in shared['items']), 1)

    def test_search_taxonomy_and_localized_descriptions(self):
        for lang in ('en','zh-hans','zh-hant'):
            records = {r['u']:r for r in json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']}
            for p in self.pages:
                rel = p.relative_to(ROOT).as_posix()
                self.assertEqual(records[rel]['d'], 'sae-philosophy')
                self.assertEqual(scan_page(ROOT, p)['domain'], 'sae-philosophy')
                if lang != 'en':
                    self.assertRegex(records[rel]['x'], r'[\u3400-\u9fff]')
            case = records['essays/political-economy/petsmart-training.html']
            self.assertIn('PetSmart', case['q'])
            self.assertIn('PetSmart', case['x']) if lang == 'en' else self.assertIn('培训' if lang == 'zh-hans' else '培訓', case['x'])

    def test_sitemap_and_update_ledger(self):
        root = ET.fromstring((ROOT/'sitemap.xml').read_text())
        urls = {x.find('{*}loc').text:x.find('{*}lastmod').text for x in root.findall('{*}url')}
        for p in self.pages:
            expected = DATE  # All case pages gained theory companion navigation, not new publication dates.
            self.assertEqual(urls[BASE + ('' if p.name == 'index.html' else p.name)], expected)
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        u = next(u for u in updates if u['id'] == '2026-11-01-political-economy-batch01')
        self.assertEqual(set(u['languages']), {'en','zh','zh-hant'})
        self.assertEqual(u['kind'], 'new')
        expansion = next(u for u in updates if u['id'] == '2026-11-01-political-economy-batch02')
        self.assertEqual(expansion['kind'], 'expanded')
        self.assertEqual(set(expansion['languages']), {'en','zh','zh-hant'})
        newest = next(u for u in updates if u['id'] == '2026-11-02-political-economy-batch03')
        self.assertEqual(newest['kind'], 'expanded')
        self.assertEqual(newest['date'], '2026-11-02')
        newest = next(u for u in updates if u['id'] == '2026-11-03-political-economy-batch04')
        self.assertEqual(newest['kind'], 'expanded')
        self.assertEqual(newest['date'], DATE)
        self.assertEqual(set(newest['languages']), {'en','zh','zh-hant'})
        ending = next(u for u in updates if u['id'] == '2026-11-03-political-economy-batch05')
        self.assertEqual(ending['url'], 'essays/political-economy/jimmy-johns.html')
        self.assertEqual(ending['date'], DATE)
        self.assertEqual(set(ending['languages']), {'en','zh','zh-hant'})

    def test_hospital_financing_and_historical_boundaries(self):
        d = self.items[3]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('五家医院的房产', '四家医院房产', '4.9%', '经营管理权', '10月3日', '十五年', '五年的监测', '八年', '2024年5月6日', '不是保证所有医院此后都一直开着'):
            self.assertIn(phrase, zh)
        for phrase in ('fifteen-year', 'first-mortgage', '4.9%', '3 October', 'five years of monitoring', 'not a claim that every facility subsequently stayed open', 'not a judicial determination'):
            self.assertIn(phrase, en)
        self.assertEqual(d['coverage'], '2010/2024-05-06')
        self.assertIn('subsequent sales', d['historical_note_en'])

    def test_ratings_units_actions_and_settlement(self):
        d = self.items[4]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('三十笔', '二十笔', '十一笔交易中的十八个', '负面观察不等于已经降级', '612个', '7月12日', '2015年2月3日', '不能被叫作刑事定罪'):
            self.assertIn(phrase, zh)
        for phrase in ('thirty RMBS transactions', 'twenty more', 'eighteen tranches from eleven transactions', '10 July', '12 July', '$1.375 billion', 'nineteen states', 'not an admission by Moody', 'not a criminal conviction'):
            self.assertIn(phrase, en)
        self.assertEqual(d['coverage'], '2007/2015-02-03')
        self.assertIn('2017 SEC', d['historical_note_en'])

    def test_new_cases_do_not_claim_current_proceedings(self):
        for d in self.items[3:]:
            page = self.pages[ROOT/('essays/political-economy/' + d['slug'] + '.html')]
            self.assertIn(d['historical_note_en'], html.unescape(page))
            self.assertNotIn('Case status is checked to 1 November 2026', page)
            self.assertIn('English independently written', page)

    def test_google_markets_historical_practice_and_remedy_scope(self):
        d = self.items[5]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('Last Look', '不同位置', '原告没有证明', '不是另一起 Google 搜索案', '2026年9月2日', '六年', '不等于所要求的接口当天全部建好'):
            self.assertIn(phrase, zh)
        for phrase in ('after trial', 'advertiser-ad-network claim failed', 'separate Google Search case', 'six-year', 'not evidence that every integration already worked'):
            self.assertIn(phrase, en)
        self.assertIn('Historical Last Look', d['historical_note_en'])
        self.assertIn('reproduced by FindLaw', d['sources'][2]['title_en'])

    def test_thames_value_cash_and_payment_triggers(self):
        d = self.items[6]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('没有现金净流出', '养老金', '不能像更换电力或手机服务', '2023年5月17日', '不是一笔股息招来了全部罚款', '2030年3月31日', '不是本篇已经核实收到款项'):
            self.assertIn(phrase, zh)
        for phrase in ('£131.3 million', '£37.5 million', '£104.5 million', '£18.2 million', 'earliest of three events', '31 March 2030', 'not evidence reviewed here that the money had arrived'):
            self.assertIn(phrase, en)
        self.assertEqual(d['coverage'], '2023/2025-08-27')
        self.assertIn('final-decision PDF', d['sources'][0]['note_en'])

    def test_earlier_publication_and_update_dates_are_not_rewritten(self):
        self.assertEqual([d['date'] for d in self.items[:5]], ['2026-11-01'] * 5)
        self.assertEqual([d['date'] for d in self.items[5:7]], ['2026-11-02'] * 2)
        self.assertEqual([d['date'] for d in self.items[7:]], [DATE] * 3)
        for d in self.items:
            page = self.pages[ROOT/('essays/political-economy/' + d['slug'] + '.html')]
            self.assertIn('<time datetime="' + d['date'] + '">' + d['date'] + '</time>', page)
        latest = (ROOT/'latest.html').read_text()
        for batch in ('BATCH01', 'BATCH02'):
            marker = 'POLITICAL ECONOMY ' + batch + ' LATEST'
            text = re.search('<!-- ' + marker + ' START -->(.*?)<!-- ' + marker + ' END -->', latest, re.S)[1]
            self.assertIn('<time datetime="2026-11-01">2026-11-01</time>', text)
            self.assertNotIn('<time datetime="' + DATE, text)
        text = re.search('<!-- POLITICAL ECONOMY BATCH03 LATEST START -->(.*?)<!-- POLITICAL ECONOMY BATCH03 LATEST END -->', latest, re.S)[1]
        self.assertIn('<time datetime="2026-11-02">2026-11-02</time>', text)
        self.assertNotIn('<time datetime="' + DATE, text)

    def test_foxconn_commitments_verification_and_time_boundaries(self):
        d = self.items[7]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('最高二十八点五亿美元', '改的是政策', '一千二百四十二', '相差一年的两个时点', '不等于本文已经核实同额现金全部支付', '不能单独回答整项政策是否划算'):
            self.assertIn(phrase, zh)
        for phrase in ('$2.85 billion', 'final year', 'alter its policies to match the contract', 'not evidence that an equivalent sum', '1,242', 'year-end 2025 result', 'statewide net gain', '2,616'):
            self.assertIn(phrase, en)
        self.assertEqual(d['coverage'], '2017/2025-11-25')
        self.assertIn('printed pages', d['historical_note_en'])

    def test_apple_communication_service_value_and_rule_versions(self):
        d = self.items[8]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('五亿欧元', '必要性和相称性', '七天', '2025年6月26日', '10月1日生效', '不把类别取消说成所有外部交易都不再收费', '美国 Epic 诉讼'):
            self.assertIn(phrase, zh)
        for phrase in ('€500 million', 'initial acquisition', 'not a final court judgment', 'seven days', '1 October', 'every later provision has received regulatory approval', 'customer support'):
            self.assertIn(phrase, en)
        self.assertIn('direct PDF retrieval was blocked', d['historical_note_en'])
        self.assertIn('not represented as elimination of every service commission', d['sources'][3]['note_en'])

    def test_closing_interlude_is_short_complete_and_separate(self):
        d = self.items[9]
        self.assertEqual(d['kind'], 'interlude')
        self.assertTrue(1700 <= len(re.findall(r'[\u3400-\u9fff]', ''.join(d['body_zh']))) < 2300)
        self.assertTrue(950 <= len(' '.join(d['body_en']).split()) < 1450)
        self.assertEqual(sum(x['kind'] == 'case' for x in self.items), 8)
        self.assertEqual(sum(x['kind'] == 'interlude' for x in self.items), 1)
        for case in (x for x in self.items if x['kind'] == 'case'):
            self.assertGreaterEqual(len(re.findall(r'[\u3400-\u9fff]', ''.join(case['body_zh']))), 2300)
            self.assertGreaterEqual(len(' '.join(case['body_en']).split()), 1450)
        landing = self.pages[ROOT/'essays/political-economy/index.html']
        self.assertEqual(landing.count('class="lw-card"'), 8)
        self.assertIn('id="group-one-ending"', landing)
        self.assertIn('href="jimmy-johns.html"', landing)
        page = self.pages[ROOT/'essays/political-economy/jimmy-johns.html']
        self.assertIn('Closing interlude · English independently written', page)
        self.assertIn('href="petsmart-training.html"', page)
        self.assertIn('href="introduction.html"', page)

    def test_jimmy_johns_scope_allegations_notice_and_response(self):
        d = self.items[9]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('三英里', '两英里', '全国任一家', '超过百分之十', '实际试图执行', '不是本篇已经逐个调查', '请他们撤销', '十万美元赔偿', '每一份通知'):
            self.assertIn(phrase, zh)
        for phrase in ('three-mile', 'two miles', 'nationwide', 'more than ten per cent', "state's allegations", 'Associated Press', 'not findings from an employee survey', 'asking them to rescind', 'not an announcement of $100,000 in employee compensation'):
            self.assertIn(phrase, en)
        self.assertEqual(d['coverage'], '2007/2016-12-07')
        self.assertIn('not an independently obtained full consent decree', d['historical_note_en'])
        self.assertIn('2023 header is a print date', d['sources'][1]['note_en'])
        self.assertIn('indexed article text was readable', d['sources'][2]['note_en'])
        page = self.pages[ROOT/'essays/political-economy/jimmy-johns.html']
        self.assertNotIn('John」s', page)
        self.assertNotIn('英裡', page)


if __name__ == '__main__':
    unittest.main()
