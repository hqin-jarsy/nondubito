"""Focused reader checks for the approved 2026-11-15 continuation cleanup."""
import html
import re
import unittest
from urllib.parse import urlsplit, unquote
import build_hongloumeng_original as build
from hongloumeng_translations import edition

class ReadabilityTests(unittest.TestCase):
    def test_reproducible_pages(self):
        for path, expected in build.render().items():
            self.assertEqual(path.read_text(), expected, str(path))

    def test_headings_and_links(self):
        for path in build.TARGET.rglob('*.html'):
            if path.stem not in ['index']+[f'ch{n:03}' for n in range(81,87)]: continue
            text=path.read_text()
            self.assertNotIn('##', text, str(path))
            if path.stem!='index':
                heading=re.search(r'<h1>(.*?)</h1>',text)[1]
                self.assertIn('chapter-couplet',heading,str(path))
            for href in re.findall(r'href="([^"]+)"',text):
                u=urlsplit(html.unescape(href))
                if u.scheme or not u.path: continue
                target=build.ROOT/unquote(u.path.lstrip('/')) if u.path.startswith('/') else path.parent/unquote(u.path)
                self.assertTrue(target.resolve().exists(),str(target))

    def test_reader_corrections(self):
        checks={('ko',82):(['주서댁이','주서댁은'],['주서댁가','주서댁는']),
                ('ko',83):(['희봉이','희봉은','희봉을'],['희봉가','희봉는','희봉를']),
                ('fr',81):(['pierres de son jeu de go','Jia Lian'],['jeu d’échecs']),
                ('es',81):(['piedras de weiqi','Chunyan'],['ajedrez','Xiaoyan']),
                ('es',86):(['islote de las Castañas de Agua Púrpuras'],['Zilingzhou']),
                ('fr',85):(['Prudence dans les paroles, prudence dans les actes'],['agir prudemment']),
                ('ja',85):(['西洋のからくり船','林の妹'],['自走船','林妹妹']),
                ('en',84):(['Bao-chan'],['Moonbeam'])}
        for (lang,n),(wanted,absent) in checks.items():
            _,units,_=edition(f'ch{n:03}',lang);text=' '.join(v for _,v in units)
            for value in wanted:self.assertIn(value,text)
            for value in absent:self.assertNotIn(value,text)
        for directory in ('','zh-hant'):
            text=(build.TARGET/directory/'ch085.html').read_text()
            self.assertIn('爪哇',text);self.assertNotIn('爪洼',text);self.assertNotIn('爪窪',text)
        for path in (build.TARGET/'zh-hant').glob('*.html'):
            for wrong in ('幾上','束發','鉸發','口佔','米面','那只','兩只','只字','剪發'):
                self.assertNotIn(wrong,path.read_text(),str(path))

if __name__=='__main__':unittest.main()
