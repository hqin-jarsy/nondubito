"""Current HTML integration checks, without rewriting translation bodies."""
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from integrate_hongloumeng_french import TARGETS, transform, reverse

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('index.html', 'edition.html', *(f'ch{n:03}.html' for n in range(1,81)))
LANGS = ('', 'zh-hant/', 'en/', 'ja/', 'fr/')

class Navigation(unittest.TestCase):
    def test_reversible_language_additions(self):
        for name in TARGETS:
            raw = (ROOT/name).read_text()
            self.assertEqual(transform(name, reverse(name, raw)), raw, name)
            self.assertEqual(transform(name, raw), raw, name)

    def test_all_five_languages_roundtrip(self):
        for directory in LANGS:
            for name in NAMES:
                p = ROOT/'classics/hongloumeng'/directory/name
                raw = p.read_text()
                nav = next((m for m in re.finditer(r'<nav\b[^>]*>.*?</nav>', raw, re.S) if 'lang="zh-Hans"' in m.group()), None)
                self.assertIsNotNone(nav, str(p))
                hrefs = re.findall(r'href="([^"]+)"',nav.group())
                resolved = {(ROOT/h.lstrip('/') if h.startswith('/') else p.parent/h).resolve() for h in hrefs}
                resolved = {q / "index.html" if q.is_dir() else q for q in resolved}
                resolved.add(p.resolve())
                for target in LANGS:
                    self.assertIn((ROOT/'classics/hongloumeng'/target/name).resolve(),resolved,str(p))

    def test_french_sequence_and_continuation(self):
        for n in range(1,81):
            raw = (ROOT/f'classics/hongloumeng/fr/ch{n:03}.html').read_text()
            for neighbor in (n-1,n+1):
                if 1 <= neighbor <=80:
                    self.assertIn(f'href="ch{neighbor:03}.html"',raw)
            self.assertIn('href="index.html"',raw)
        self.assertIn('/originals/hongloumeng/fr/ch081.html',(ROOT/'classics/hongloumeng/fr/ch080.html').read_text())
        self.assertIn('/classics/hongloumeng/fr/ch080.html',(ROOT/'originals/hongloumeng/fr/ch081.html').read_text())

    def test_project_entrances(self):
        for directory in ('','en/','zh-hant/'):
            raw=(ROOT/'essays/literature/hlm'/directory/'index.html').read_text()
            section=re.search(r'<section id="first80">.*?</section>',raw,re.S).group()
            self.assertIn('/classics/hongloumeng/fr/index.html',section)
        self.assertIn('/classics/hongloumeng/fr/index.html',(ROOT/'originals/hongloumeng/fr/index.html').read_text())

if __name__ == '__main__': unittest.main()
