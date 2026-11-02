#!/usr/bin/env python3
"""Publication checks for real histories distinct from the fictional Interstate essays."""
import json
import hashlib
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

from build_cooperation_histories import ROOT, DATA, BASE, DATE, UPDATE_DATE, load_items, render
from connect_cooperation_histories import render as entrances
from build_content_registry import scan_page
from test_language_writing import Tags
from web_analytics import TOKEN


class CooperationHistories(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.pages = render()
        cls.receipt = json.loads((DATA/'publication.json').read_text())
        cls.batch2 = json.loads((DATA/'publication-batch02.json').read_text())
        cls.batch3 = json.loads((DATA/'publication-batch03.json').read_text())
        cls.batch4 = json.loads((DATA/'publication-batch04.json').read_text())
        cls.batch5 = json.loads((DATA/'publication-batch05.json').read_text())
        cls.batch6 = json.loads((DATA/'publication-batch06.json').read_text())
        cls.batch7 = json.loads((DATA/'publication-batch07.json').read_text())
        cls.counts = {**cls.receipt['counts'], **cls.batch2['counts'], **cls.batch3['counts'], **cls.batch4['counts'], **cls.batch5['counts'], **cls.batch6['counts'], **cls.batch7['counts']}

    def test_complete_rebuild(self):
        self.assertEqual(len(self.pages), 15)
        for path, text in {**self.pages, **entrances()}.items():
            self.assertEqual(path.read_text(), text)
            self.assertNotIn('TODO', text)

    def test_complete_three_reading_modes(self):
        for d in self.items:
            text = self.pages[ROOT/('essays/cooperation-histories/' + d['slug'] + '.html')]
            bodies = dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', text, re.S))
            self.assertEqual(set(bodies), {'en', 'zh', 'hant'})
            for body in bodies.values():
                self.assertGreaterEqual(body.count('<p>'), 25)
                self.assertEqual(body.count('<h2>'), 3)
                self.assertNotRegex(body, r'\b\d{2}DD\b|\bXZ\d+\b|\b[NGZ]\d+\b||turn\d+(?:view|search)')
            self.assertEqual(bodies['zh'].count('<p>'), bodies['hant'].count('<p>'))
            self.assertNotRegex(bodies['en'], r'[\u3400-\u9fff]')
            self.assertNotRegex(bodies['hant'], r'覈實|覈對|覈算|說准|失准|加納|余項|復核|限製|划定|開啓|寫准|稱贊|啓用|阿裡|一傢具體|索馬裡|巴塔查裡亞')
            self.assertEqual(self.counts[d['slug']]['zh_han'], len(re.findall(r'[\u3400-\u9fff]', ''.join(d['body_zh']))))
            self.assertEqual(self.counts[d['slug']]['en_words'], len(' '.join(d['body_en']).split()))

    def test_numbered_sources_in_both_editions(self):
        self.assertEqual([len(d['sources']) for d in self.items], [6, 8, 7, 7, 5, 9, 7, 5, 8, 6, 6, 8, 6, 8])
        for d in self.items:
            numbers = {s['id'] for s in d['sources']}
            text = self.pages[ROOT/('essays/cooperation-histories/' + d['slug'] + '.html')]
            for lang in ('en', 'zh'):
                self.assertEqual(set(map(int, re.findall(r'\[(\d+)\]', '\n'.join(d['body_' + lang])))), numbers)
            for source in d['sources']:
                self.assertIn('Source ' + str(source['id']), text)
                self.assertIn(source['url'].replace('&', '&amp;'), text)
                self.assertTrue(all(source[k].strip() for k in ('title_en', 'title_zh', 'note_en', 'note_zh')))

    def test_metadata_and_beacon(self):
        for path, text in self.pages.items():
            tags = Tags(text).items
            url = BASE + ('' if path.name == 'index.html' else path.name)
            self.assertEqual([a['href'] for t,a in tags if t == 'link' and a.get('rel') == 'canonical'], [url])
            self.assertEqual(len([a for t,a in tags if t == 'header']), 1)
            self.assertEqual({a['class'] for t,a in tags if t == 'h1'}, {'lang-en', 'lang-zh', 'lang-hant'})
            beacons = [a for t,a in tags if t == 'script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
            self.assertEqual(len(beacons), 1)
            self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'], TOKEN)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
            self.assertEqual(schema['inLanguage'], ['en', 'zh-Hans', 'zh-Hant'])
            if path.name == 'index.html':
                self.assertEqual(schema['datePublished'], DATE)
                self.assertEqual(schema['dateModified'], UPDATE_DATE)
                self.assertEqual(len(schema['hasPart']), 14)
            else:
                d = next(d for d in self.items if d['slug'] == path.stem)
                self.assertEqual(schema['datePublished'], d.get('date', DATE))
                self.assertEqual(schema['dateModified'], d.get('date', DATE))
                self.assertEqual(schema['citation'], [s['url'] for s in d['sources']])
                self.assertEqual(schema['isPartOf']['url'], BASE)
                self.assertEqual(schema['temporalCoverage'], d['coverage'])

    def test_local_links_and_unique_ids(self):
        for path, text in self.pages.items():
            tags = Tags(text).items
            ids = [a['id'] for t,a in tags if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)))
            for tag, attrs in tags:
                raw = attrs.get('href' if tag in ('a','link') else 'src', '')
                parts = urlsplit(raw)
                if not raw or parts.scheme or parts.netloc:
                    continue
                target = ROOT/unquote(parts.path.lstrip('/')) if parts.path.startswith('/') else path.parent/unquote(parts.path)
                if parts.path:
                    self.assertTrue(target.is_file(), str(path) + ': ' + raw)
                if parts.fragment:
                    self.assertRegex(target.read_text() if parts.path else text, r'\bid=["\']' + re.escape(parts.fragment) + r'["\']')

    def test_rhine_historical_and_legal_boundaries(self):
        d = self.items[0]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for phrase in ('不是一个国际组织制造的事故', '1963年', '1985至2000年', '多数', '点源排放', '第十一条', '1986年已经全部如此运作', '一条河的改善，不能替每一份个人请求写出结局'):
            self.assertIn(phrase, zh)
        self.assertIn('not a single percentage measuring every kind of pollution', en)
        self.assertIn('Article 11', en)
        self.assertIn('not a description to project backward', en)
        self.assertIn('Article 9 concerns plenary sessions', d['sources'][5]['note_en'])

    def test_haiti_distinctions_and_cutoff(self):
        d = self.items[1]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for phrase in ('2011年11月3日', '2013年2月', '2016年8月18日', '先决条件', '不是联合国在事实与实体责任上已经胜诉', '不是一份法院确定损害赔偿责任的判决', '调查可能揭示事实', '2016年底'):
            self.assertIn(phrase, zh)
        self.assertIn('not a judgment clearing the organization on the merits', en)
        self.assertIn('does not claim that every form of criticism', en)
        self.assertIn('later implementation needs later records', en)
        self.assertIn('not assert that this court found a Section 29 breach', d['sources'][5]['note_en'])

    def test_discovery_and_open_ended_shelf(self):
        for name in ('library.html','explore.html','index.html','latest.html','essays/sae/index.html'):
            self.assertIn('essays/cooperation-histories/index.html', (ROOT/name).read_text())
        fictional = (ROOT/'essays/interstate/index.html').read_text()
        self.assertIn('../cooperation-histories/index.html', fictional)
        self.assertEqual(fictional.count('class="lw-card"'), 9)
        landing = self.pages[ROOT/'essays/cooperation-histories/index.html']
        self.assertEqual(landing.count('class="lw-card"'), 14)
        self.assertEqual(landing.count('class="ch-group"'), 7)
        self.assertIn('id="reading-route"', landing)
        self.assertIn('href="#conditions-and-limits"', landing)
        self.assertIn('href="#capacity-and-evidence"', landing)
        self.assertIn('href="#allocation-and-choice"', landing)
        self.assertIn('href="#inspection-and-judgment"', landing)
        self.assertIn('An ongoing series', landing)
        self.assertIn('责任来源不同，不是两个相反的评分', landing)
        self.assertIn('制裁、名字与复审', landing)
        self.assertIn('水流、损害与请求', landing)
        self.assertIn('调查、退出与下一次追问', landing)
        self.assertNotIn('First two essays', landing)
        self.assertEqual(landing.count('<h3 class="lang-en">'), 14)
        library = (ROOT/'library.html').read_text()
        self.assertGreater(library.index('<!-- COOPERATION HISTORIES LIBRARY START -->'), library.index('Category 06'))
        self.assertLess(library.index('<!-- COOPERATION HISTORIES LIBRARY START -->'), library.index('Category 07'))

    def test_search_and_sitemap(self):
        for lang in ('en','zh-hans','zh-hant'):
            records = {r['u']:r for r in json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']}
            for path in self.pages:
                relative = path.relative_to(ROOT).as_posix()
                self.assertIn(relative, records)
                self.assertEqual(records[relative]['d'], 'history')
                self.assertEqual(scan_page(ROOT,path)['domain'], 'history')
            if lang != 'en':
                self.assertIn('道歉', records['essays/cooperation-histories/haiti-cholera.html']['x'])
            for slug, labels in (
                ('kunduz-hanan', ('Kunduz','Hanan','昆都士','哈南')),
                ('northern-ireland-windsor', ('Brexit','Northern Ireland','Windsor','北爱尔兰','北愛爾蘭','溫莎框架')),
                ('us-shrimp-turtle', ('WTO', 'DS58', '海龟', '海龜')),
                ('kishenganga-water', ('Indus Waters Treaty', 'Kishenganga', 'Neelum', '基申甘加', '印度河水條約')),
                ('montreal-fund', ('Montreal Protocol', 'Multilateral Fund', 'CFC', '蒙特利尔', '蒙特利爾', '多邊基金')),
                ('smallpox-eradication', ('smallpox', 'WHO', 'rumour register', '天花', '世界衛生組織')),
                ('covax-delivery', ('COVAX', 'Ghana', 'AMC', '疫苗', '迦納')),
                ('greece-bailout', ('Greece', 'OXI', 'Koufaki', '希腊', '希臘')),
                ('antarctic-inspections', ('Antarctic Treaty', 'Dumont', '南极', '南極', '排污')),
                ('jcpoa-verification', ('JCPOA', 'IAEA', '130.1', '伊朗', '核查')),
            ):
                record = records['essays/cooperation-histories/' + slug + '.html']
                for label in labels:
                    self.assertIn(label, record['q'])
        urls = {e.text for e in ET.fromstring((ROOT/'sitemap.xml').read_text()).findall('{*}url/{*}loc')}
        for path in self.pages:
            self.assertIn(BASE + ('' if path.name == 'index.html' else path.name), urls)
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        selected = [u for u in updates if u['id'] == '2026-10-30-cooperation-histories']
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]['domain'], 'history')
        new_update = [u for u in updates if u['id'] == '2026-10-30-cooperation-histories-batch02']
        self.assertEqual(len(new_update), 1)
        self.assertEqual(new_update[0]['kind'], 'expanded')
        newest = [u for u in updates if u['id'] == '2026-10-30-cooperation-histories-batch03']
        self.assertEqual(len(newest), 1)
        self.assertEqual(newest[0]['kind'], 'expanded')
        self.assertEqual(next(u for u in updates if u['id'].startswith('2026-10-30-cooperation-histories'))['id'], newest[0]['id'])
        fourth = [u for u in updates if u['id'] == '2026-10-31-cooperation-histories-batch04']
        self.assertEqual(len(fourth), 1)
        self.assertEqual(fourth[0]['kind'], 'expanded')
        fifth = [u for u in updates if u['id'] == '2026-10-31-cooperation-histories-batch05']
        self.assertEqual(len(fifth), 1)
        self.assertEqual(fifth[0]['kind'], 'expanded')
        sixth = [u for u in updates if u['id'] == '2026-10-31-cooperation-histories-batch06']
        self.assertEqual(len(sixth), 1)
        self.assertEqual(sixth[0]['kind'], 'expanded')
        seventh = [u for u in updates if u['id'] == '2026-11-01-cooperation-histories-batch07']
        self.assertEqual(len(seventh), 1)
        self.assertEqual(seventh[0]['kind'], 'expanded')
        self.assertEqual(next(u for u in updates if 'cooperation-histories' in u['id'])['id'], seventh[0]['id'])
        home = (ROOT/'index.html').read_text()
        self.assertLess(home.index('<!-- COOPERATION HISTORIES HOME START -->'), home.index('<!-- INTERSTATE HOME START -->'))

    def test_iraq_causation_implementation_and_access(self):
        d = self.items[2]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for phrase in ('伊拉克入侵科威特', '保留严格医疗用途物资的例外', '伊拉克政府没有接受', '2002年新程序', '2017年', '不是把外部捐来的粮食', '没有因此成为', '并非宣布世界上不存在其他声音'):
            self.assertIn(phrase, zh)
        self.assertNotRegex(zh, r'五十万|五十萬|50万|500,?000')
        self.assertIn('principally financed by the sale of Iraqi oil', en)
        self.assertIn('not a judicial finding', en)
        self.assertIn('not a collection of named entries', en)
        self.assertIn('repetition of 1999 mortality estimates is not adopted', d['sources'][3]['note_en'])

    def test_kadi_review_is_not_a_world_court_or_acquittal(self):
        d = self.items[3]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for phrase in ('不是一份已经由刑事法庭定罪', '2008年9月3日', '最多维持三个月', '2013年7月18日', '并未接受普通法院的全部分析', '保密的理由本身需要接受检查', '2012年10月5日', '这发生在2013年欧洲法院判决之前', '早在当年6月通过'):
            self.assertIn(phrase, zh)
        for phrase in ('not a criminal conviction', 'one sufficiently specific, substantiated ground', 'sixty days after the committee', 'A focal-point route had existed before', 'not a judge’s final order', 'preceded the 2013 European judgment'):
            self.assertIn(phrase, en)
        self.assertTrue(d['sources'][1]['url'].startswith('https://eur-lex.europa.eu/'))

    def test_first_pair_is_byte_preserved(self):
        self.assertEqual(self.receipt['published_essays'], 2)
        self.assertEqual(self.batch2['published_essays'], 4)
        self.assertEqual(self.batch2['new_essays'], ['iraq-sanctions', 'kadi-listing'])
        hashes = json.loads((ROOT/'reports/cooperation-histories-batch02-20261030.json').read_text())['preserved_first_pair_sha256']
        for slug, expected in hashes.items():
            self.assertEqual(hashlib.sha256((ROOT/'essays/cooperation-histories'/f'{slug}.html').read_bytes()).hexdigest(), expected)

    def test_hanan_investigation_is_not_a_substantive_airstrike_verdict(self):
        d = self.items[4]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for phrase in ('四天后', '没有违反', '特殊条件的结合', '不是一张可以盖在所有战争上的通行证', '文职检察机关', '未先听取哈南', '明显缺乏根据', '没有最终裁定', '不是同一种批评', '也没有借此完成有关空袭行为归属的全部判断', '不是同一层级的上诉法庭', '2021年'):
            self.assertIn(phrase, zh)
        for phrase in ('not a general rule', 'manifestly ill-founded', 'left open', 'not a guarantee of prosecution', 'did not thereby rule', 'including civilians', 'not an order to prosecute'):
            self.assertIn(phrase, en)
        self.assertNotRegex(zh, r'一百四十人|140人|第五条已被启动')
        self.assertIn('exhaustion was left open', d['sources'][0]['note_en'])

    def test_northern_ireland_exit_brake_consent_and_cutoff(self):
        d = self.items[5]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for phrase in ('不是某位司机的一段现场记录', '大不列颠', '英国议会制定的法律', '至少来自两个政党的30名议员', '不是对所有新欧盟法律的普遍否决权', '30个签名因此不是一份自动生效的停止令', '48票对36票', '不是跨社群支持', '不是决定北爱留在英国还是加入统一爱尔兰', '2025年底', '不提供2026年的通关操作指南'):
            self.assertIn(phrase, zh)
        for phrase in ('Thirty signatures therefore do not automatically stop a law', 'applicability motions', 'written reasons', 'simple majority but not cross-community support', 'not evidence that every recommendation has been implemented', 'not make Northern Ireland an EU member'):
            self.assertIn(phrase, en)
        self.assertEqual(d['coverage'], '2020/2025')

    def test_prior_two_pairs_and_receipts_are_preserved(self):
        self.assertEqual(self.batch3['published_essays'], 6)
        self.assertEqual(self.batch3['new_essays'], ['kunduz-hanan','northern-ireland-windsor'])
        report = json.loads((ROOT/'reports/cooperation-histories-batch03-20261030.json').read_text())
        hashes = report['preserved_prior_article_sha256']
        self.assertEqual(len(hashes), 4)
        for slug, expected in hashes.items():
            self.assertEqual(hashlib.sha256((ROOT/'essays/cooperation-histories'/f'{slug}.html').read_bytes()).hexdigest(), expected)

    def test_shrimp_goal_implementation_and_personal_access(self):
        d = self.items[6]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for term in ('初步的正当化', '三年的过渡', '四个月', '善意地谈判', '保证一定谈成', '保护效果可以比较', '不能直接启动', '不编出一位失业渔民', '1996至2001年'):
            self.assertIn(term, zh)
        for term in ('continuing effort', 'not a permanent certificate', 'nor an instruction to lower every standard', 'not a turtle’s lawsuit', 'not presented as a description of the WTO’s operation today'):
            self.assertIn(term, en)
        self.assertEqual(d['coverage'], '1996/2001')
        self.assertIn('Current performance percentages', d['sources'][0]['note_en'])

    def test_kishenganga_conditions_roles_review_and_cutoff(self):
        d = self.items[7]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for term in ('日平均', '全部放行', '不是从2013年裁决日', '不等于海牙', '国际法院', '不是叫全部工程立刻停止', '不是愿意听就听的建议', '没有另建', '没有因此自动获得', '停在2013年'):
            self.assertIn(term, zh)
        for term in ('all of that inflow', 'not simply start with the award in 2013', 'not the International Court of Justice', 'not automatically make the requirement expire', 'Absence of individual standing', 'not proof that every later day complied'):
            self.assertIn(term, en)
        self.assertEqual(d['coverage'], '1960/2013')
        self.assertIn('Seven years runs from diversion', d['sources'][2]['note_en'])

    def test_prior_six_articles_are_byte_preserved_and_new_pair_linked(self):
        self.assertEqual(self.batch4['published_essays'], 8)
        self.assertEqual(self.batch4['new_essays'], ['us-shrimp-turtle', 'kishenganga-water'])
        self.assertEqual(len(self.batch4['preserved_prior_article_sha256']), 6)
        for slug, expected in self.batch4['preserved_prior_article_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'essays/cooperation-histories'/f'{slug}.html').read_bytes()).hexdigest(), expected)
        for slug, partner in (('us-shrimp-turtle', 'kishenganga-water'), ('kishenganga-water', 'us-shrimp-turtle')):
            self.assertIn(f'href="{partner}.html"', self.pages[ROOT/f'essays/cooperation-histories/{slug}.html'])

    def test_montreal_funding_dates_conditions_and_outcomes(self):
        d = self.items[8]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for term in ('1992年8月', '1991年1月', '经议定的增量成本', '三分之二',
                     '四家CFC生产商', '十七个月', '药用吸入器', '不是多边基金每笔拨款',
                     '不是一条必须', '2012年', '不替后来每笔资金'):
            self.assertIn(term, zh)
        for term in ('not every expense', 'Two separate simple majorities alone',
                     'authorized essential production', 'not the fund’s procedure',
                     'does not invent the later settlement'):
            self.assertIn(term, en)
        self.assertEqual(d['coverage'], '1987/2012')
        self.assertIn('§§101–103', d['sources'][4]['title_en'])
        self.assertIn('not an independent adjudication', d['sources'][3]['note_en'])

    def test_smallpox_zero_certification_knowledge_and_methods(self):
        d = self.items[9]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for term in ('一百零四条传闻', '不是全世界所有地方报告的总数', '至少两年',
                     '1967年的操作手册', '尼日利亚东部', '伯明翰', '1980年5月8日',
                     '不能被扩大成所有地区', '国家间的合作文件替个人补一声赞成'):
            self.assertIn(term, zh)
        for term in ('neither 104 confirmed cases', 'Two calendar years were not an automatic certificate',
                     'Last naturally occurring case', 'selected episodes cannot establish how frequently',
                     'not an individual’s agreement'):
            self.assertIn(term, en)
        self.assertEqual(d['coverage'], '1967/1980')
        self.assertIn('mirror', d['sources'][0]['title_en'])
        self.assertIn('Accessible abstract', d['sources'][3]['note_en'])
        self.assertNotRegex(zh, r'超过一半|超過一半|百分之五十|52条')

    def test_prior_eight_articles_preserved_and_latest_pair_linked(self):
        self.assertEqual(self.batch5['published_essays'], 10)
        self.assertEqual(self.batch5['new_essays'], ['montreal-fund', 'smallpox-eradication'])
        self.assertEqual(len(self.batch5['preserved_prior_article_sha256']), 8)
        for slug, expected in self.batch5['preserved_prior_article_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'essays/cooperation-histories'/f'{slug}.html').read_bytes()).hexdigest(), expected)
        for slug, partner in (('montreal-fund', 'smallpox-eradication'), ('smallpox-eradication', 'montreal-fund')):
            self.assertIn(f'href="{partner}.html"', self.pages[ROOT/f'essays/cooperation-histories/{slug}.html'])
        self.assertIn('#inspection-and-judgment', entrances()[ROOT/'index.html'])
        self.assertIn('family=Noto+Serif+TC', entrances()[ROOT/'library.html'])

    def test_covax_allocations_forecasts_delivery_and_personal_redress(self):
        d = self.items[10]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for term in ('2021年2月24日', '六十万剂', '不是一个世界卫生政府', '3%', '20%',
                     '不是后来核算出的全年实际交付量', '不能精确结算，不是不用回答',
                     '2020年预想的第二阶段', '无过错补偿机制', '不是二十亿人已经完成接种'):
            self.assertIn(term, zh)
        for term in ('1.425 billion', 'not a permanent ceiling', 'not an adjudication',
                     'not a subsequently audited total', 'no-fault compensation',
                     'not two billion people', 'informed agreement'):
            self.assertIn(term, en)
        self.assertEqual(d['coverage'], '2020/2023')
        self.assertNotRegex(zh, r'避免了?270万|拯救了?270万')

    def test_greece_ballot_liquidity_lenders_and_court_remit(self):
        d = self.items[11]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for term in ('61.31%', '有效票', '不是一张直接询问是否退出欧元',
                     '6月30日到期', '7月8日', '8月19日', '维持上限与切断一切资金',
                     '双边贷款', '实际由欧洲稳定机制拨出的贷款为六百一十九亿',
                     '不是欧盟法院', '明显缺乏根据', '不是一份宣布所有损失只有一个原因的判决'):
            self.assertIn(term, zh)
        for term in ('not a direct vote on leaving the euro', 'not the same as withdrawing all',
                     '€61.9 billion', 'manifestly ill-founded', 'not a finding that all losses had a single cause',
                     'A signature records a decision'):
            self.assertIn(term, en)
        self.assertEqual(d['coverage'], '2010/2018')

    def test_prior_ten_preserved_and_sixth_pair_linked(self):
        self.assertEqual(self.batch6['published_essays'], 12)
        self.assertEqual(self.batch6['new_essays'], ['covax-delivery', 'greece-bailout'])
        self.assertEqual(len(self.batch6['preserved_prior_article_sha256']), 10)
        for slug, expected in self.batch6['preserved_prior_article_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'essays/cooperation-histories'/f'{slug}.html').read_bytes()).hexdigest(), expected)
        for slug, partner in (('covax-delivery', 'greece-bailout'), ('greece-bailout', 'covax-delivery')):
            self.assertIn(f'href="{partner}.html"', self.pages[ROOT/f'essays/cooperation-histories/{slug}.html'])


    def test_antarctic_access_findings_followup_and_limits(self):
        d = self.items[12]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for term in ('不符合', '附件III', '12日至15日', '1995年', '指定国国民',
                     '并未因此放弃全部主张', '不是强制性的', '独立准备报告',
                     '不是处理系统后来已经安装', '争端解决', '一些旧检查报告', '2024年'):
            self.assertIn(term, zh)
        for term in ('Macerated', 'did not comply', '12 to 15 December',
                     'not evidence of twenty-eight years of wrongdoing', 'non-mandatory',
                     'separate dispute-settlement', 'not an automatic conclusion'):
            self.assertIn(term, en)
        self.assertNotIn('三天', zh)
        self.assertEqual(d['coverage'], '1959/2024')

    def test_jcpoa_quantity_units_dates_and_policy_remit(self):
        d = self.items[13]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for term in ('130.1', '11月19日', '12月6日', '需求估计', '1月10日',
                     '2月19日', '六氟化铀等值', '评价仍在进行',
                     '不是所有制裁一齐消失', '不能代替判断', '2015至2018年'):
            self.assertIn(term, zh + '\n' + d['deck_zh'])
        for term in ('19 February', 'uranium hexafluoride', 'significant non-performance',
                     'not itself a discovery of secret activity', '2015–2018',
                     'not remove every sanction', 'not a technical judgment'):
            self.assertIn(term, en)
        self.assertNotIn('a supposedly subsequent January decision', en)
        hant = self.pages[ROOT/'essays/cooperation-histories/jcpoa-verification.html']
        self.assertIn('鈾的質量', hant)
        self.assertNotIn('鈾的品質', hant)
        self.assertEqual(d['coverage'], '2015/2018')

    def test_prior_twelve_preserved_and_seventh_pair_linked(self):
        self.assertEqual(self.batch7['published_essays'], 14)
        self.assertEqual(self.batch7['new_essays'], ['antarctic-inspections', 'jcpoa-verification'])
        self.assertEqual(len(self.batch7['preserved_prior_article_sha256']), 12)
        for slug, expected in self.batch7['preserved_prior_article_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'essays/cooperation-histories'/f'{slug}.html').read_bytes()).hexdigest(), expected)
        for slug, partner in (('antarctic-inspections', 'jcpoa-verification'), ('jcpoa-verification', 'antarctic-inspections')):
            self.assertIn(f'href="{partner}.html"', self.pages[ROOT/f'essays/cooperation-histories/{slug}.html'])
        latest = (ROOT/'latest.html').read_text()
        for number in (4, 5, 6):
            section = re.search(r'<!-- COOPERATION HISTORIES BATCH0' + str(number) + r' LATEST START -->(.*?)<!-- COOPERATION HISTORIES BATCH0' + str(number) + r' LATEST END -->', latest, re.S)[1]
            self.assertIn('datetime="2026-10-31"', section)
            self.assertNotIn('2026-11-01', section)


if __name__ == '__main__':
    unittest.main(verbosity=2)
