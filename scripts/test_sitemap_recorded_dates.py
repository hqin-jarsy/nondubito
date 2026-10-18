"""Regression: regenerating discovery must not redate untouched pages."""
import unittest
import build_sitemap as sitemap


class RecordedDates(unittest.TestCase):
    def test_valid_dates_only(self):
        source = '''<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://nondubito.net/a.html</loc><lastmod>2026-09-10</lastmod></url>
        <url><loc>https://nondubito.net/b.html</loc><lastmod>not-a-date</lastmod></url>
        </urlset>'''
        self.assertEqual(sitemap.parse_recorded_dates(source), {'https://nondubito.net/a.html': '2026-09-10'})
        self.assertEqual(sitemap.parse_recorded_dates('broken'), {})

    def test_roundtrip(self):
        pairs = [('https://nondubito.net/', '2026-10-17'),
                 ('https://nondubito.net/essays/theatre/hamilton.html', '2026-10-13')]
        self.assertEqual(sitemap.parse_recorded_dates(sitemap.sitemap_xml(pairs)), dict(pairs))


if __name__ == '__main__':
    unittest.main()
