"""The homepage is a short digest; Latest remains the complete archive."""
import copy
import json
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit

from build_home_updates import ROOT, START, END, RECENT_LIMIT, render_home, render_section, replace_section, select_updates, series_key
from check_site_updates import check


class Tags(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class HomeUpdates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        cls.config = json.loads((ROOT/'data/home-updates.json').read_text())

    def test_static_bounded_digest_is_current(self):
        source = (ROOT/'index.html').read_text()
        self.assertEqual(source, render_home(source))
        self.assertEqual(source.count('class="home-update-feature"'), 1)
        self.assertEqual(source.count('class="home-update-row"'), RECENT_LIMIT)
        section = render_section(self.updates, self.config)
        for css in ('lang-en', 'lang-zh', 'lang-hant'):
            self.assertIn(f'<h2 class="{css}">', section)
            self.assertEqual(section.count(f'<h3 class="{css}">'), 5)
        self.assertNotIn('<script', section)
        self.assertIn('href="latest.html"', section)

    def test_latest_keeps_the_whole_ledger(self):
        self.assertEqual(check(), [])
        latest = (ROOT/'latest.html').read_text()
        self.assertEqual(re.findall(r'data-update-id="([^"]+)"', latest), [u['id'] for u in self.updates])
        self.assertGreater(len(self.updates), RECENT_LIMIT)

    def test_grouping_feature_and_recent(self):
        feature, recent = select_updates(self.updates, self.config)
        self.assertEqual(feature['id'], self.config['feature_id'])
        keys = [series_key(u) for u in [feature, *recent]]
        self.assertEqual(len(set(keys)), 5)
        newest_other_series = next(u for u in sorted(self.updates, key=lambda u:u['date'], reverse=True)
                                   if series_key(u) != series_key(feature))
        self.assertEqual(recent[0]['id'], newest_other_series['id'])
        self.assertEqual([u['date'] for u in recent], sorted([u['date'] for u in recent], reverse=True))

    def test_hundreds_of_updates_cannot_expand_home(self):
        items = []
        for n in range(200):
            item = copy.deepcopy(self.updates[0])
            item.update(id=f'future-{n}', date='2026-12-01', url=f'essays/future/ep{n}.html')
            items.append(item)
        feature, recent = select_updates(items + self.updates, self.config)
        self.assertEqual(len(recent), 4)
        self.assertEqual(recent[0]['id'], 'future-0')
        self.assertEqual(sum(series_key(u) == 'essays/future' for u in recent), 1)
        self.assertEqual(render_section(items + self.updates, self.config).count('class="home-update-row"'), 4)

    def test_newest_translation_of_featured_series_does_not_repeat_its_card(self):
        feature, _ = select_updates(self.updates, self.config)
        newer = copy.deepcopy(feature)
        newer.update(id='future-feature-translation', date='2026-12-02')
        selected, recent = select_updates([newer, *self.updates], self.config)
        self.assertEqual(selected['id'], feature['id'])
        self.assertNotIn(newer['id'], [u['id'] for u in recent])
        self.assertTrue(all(series_key(u) != series_key(feature) for u in recent))
        self.assertEqual(len(recent), RECENT_LIMIT)

    def test_series_boundaries(self):
        key = lambda url: series_key({'url': url})
        self.assertEqual(key('essays/political-economy/theory/index.html'), key('essays/political-economy/ep01.html?lang=zh#reading'))
        self.assertEqual(key('originals/hongloumeng/ch081.html'), key('originals/hongloumeng/en/ch084.html'))
        self.assertEqual(key('essays/everyday/work/en/ep01.html'), key('essays/everyday/work/ep02.html'))
        self.assertNotEqual(key('essays/everyday/work/index.html'), key('essays/everyday/time/index.html'))
        self.assertNotEqual(key('essays/literature/alive/index.html'), key('essays/literature/crime-punishment/index.html'))
        self.assertEqual(series_key({'url': 'unusual/a.html', 'series_key': 'shared'}), 'shared')

    def test_dates_links_escaping_and_missing_feature(self):
        tags = Tags(render_section(self.updates, self.config)).tags
        ids = [a['data-update-id'] for _, a in tags if 'data-update-id' in a]
        self.assertEqual(len(ids), len(set(ids)))
        for tag, attrs in tags:
            if tag == 'a':
                self.assertTrue((ROOT/urlsplit(attrs['href']).path).is_file())
            if tag == 'time':
                self.assertRegex(attrs['datetime'], r'^\d{4}-\d{2}-\d{2}$')
        config = copy.deepcopy(self.config)
        config['feature_deck']['en'] = '<not markup> & "quote"'
        self.assertIn('&lt;not markup&gt; &amp; &quot;quote&quot;', render_section(self.updates, config))
        config['feature_id'] = 'missing'
        with self.assertRaises(ValueError):
            select_updates(self.updates, config)

    def test_no_mutation_outside_section_or_ledger(self):
        before = copy.deepcopy(self.updates)
        source = 'unchanged before\n' + START + '\nold\n' + END + '\nunchanged after'
        section = render_section(self.updates, self.config)
        self.assertEqual(replace_section(source, section), 'unchanged before\n' + section + '\nunchanged after')
        self.assertEqual(self.updates, before)
        with self.assertRaises(ValueError):
            replace_section(source + START, section)


if __name__ == '__main__':
    unittest.main()
