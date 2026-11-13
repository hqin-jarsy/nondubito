#!/usr/bin/env python3
import copy
import unittest
from pathlib import Path
from build_hongloumeng_reading_japanese import load_chapters,render,ROOT
from integrate_hongloumeng_japanese import TARGETS,transform,reverse

class JapaneseReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chapters=load_chapters();cls.plan=render(cls.chapters)
    def test_inventory(self):
        self.assertEqual(len(self.plan),84)
        for n in range(1,81):self.assertIn(f'ch{n:03}.html',self.plan)
    def test_unique_placeholders(self):
        import re
        markers=[]
        for name,body in self.plan.items():
            markers.extend(re.findall(r'<mark id="([^"]+)"',body))
        self.assertEqual(len(markers),11);self.assertEqual(len(set(markers)),11)
    def test_no_internal_fields(self):
        for name,body in self.plan.items():
            for word in ('sourceText','sourceSha256','sourceBlockIndex','sourceSegments','private-review','/Users/'):
                self.assertNotIn(word,body,name)
    def test_continuation_boundary(self):
        self.assertIn('/originals/hongloumeng/ja/ch081.html',self.plan['ch080.html'])
        self.assertIn('曹雪芹の失われた原稿ではありません',self.plan['ch080.html'])
    def test_reversible_navigation(self):
        for relative in TARGETS:
            data=(ROOT/relative).read_bytes()
            if b'<!-- JAPANESE-NAV:START -->' in data:data=reverse(relative,data)
            transformed=transform(relative,data)
            self.assertEqual(reverse(relative,transformed),data)
            with self.assertRaises(ValueError):transform(relative,transformed)
    def test_incomplete_inventory_rejected(self):
        with self.assertRaises(ValueError):render(self.chapters[:-1])
    def test_partial_metadata_rejects_hidden_text(self):
        from hongloumeng_partial_private import inspect_partial
        import json
        d=json.loads((ROOT/'data/hongloumeng/first80-japanese/chapters/ch006.partial.json').read_text())
        for block in d['blocks']:
            for segment in block.get('sourceSegments',[]):
                if segment.get('status')=='owner_translation_needed':
                    segment['text']='FORBIDDEN FALLBACK SENTINEL'
                    with self.assertRaises(ValueError):inspect_partial(d)
                    return
        self.fail('Expected placeholder')
    def test_local_links_and_fragments(self):
        from html.parser import HTMLParser
        from urllib.parse import urlsplit
        class Links(HTMLParser):
            def __init__(self):super().__init__();self.links=[];self.ids=set()
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if 'id' in a:self.ids.add(a['id'])
                if tag=='a' and 'href' in a:self.links.append(a['href'])
        base=ROOT/'classics/hongloumeng/ja'
        for name,body in self.plan.items():
            if not name.endswith('.html'):continue
            doc=Links();doc.feed(body)
            for link in doc.links:
                u=urlsplit(link)
                if u.scheme or u.netloc:continue
                target=(ROOT/u.path.lstrip('/')) if u.path.startswith('/') else base/(u.path or name)
                if target.is_dir():target=target/'index.html'
                self.assertTrue(target.is_file(),f'{name}: {link}')
                if u.fragment:
                    other=doc
                    if u.path:
                        other=Links();other.feed(target.read_text())
                    self.assertIn(u.fragment,other.ids,f'{name}: {link}')
    def test_missing_translation_never_falls_back(self):
        import json,tempfile
        with tempfile.TemporaryDirectory() as directory:
            data=Path(directory);(data/'chapters').mkdir()
            fixture={'schemaVersion':1,'language':'ja','number':1,'title':'第一回','blocks':[{'kind':'prose','sourceText':'SOURCE ONLY SENTINEL'}]}
            (data/'chapters/ch001.draft.json').write_text(json.dumps(fixture))
            with self.assertRaisesRegex(ValueError,'source fallback forbidden'):load_chapters(data)
    def test_exact_output(self):
        for name,body in self.plan.items():self.assertEqual((ROOT/'classics/hongloumeng/ja'/name).read_text(),body)

    def _release_fixtures(self):
        import hashlib
        from build_hongloumeng_reading_japanese import PARTIAL
        from hongloumeng_japanese_pipeline import source_hash
        chapters, drafts = [], {}
        for n in range(1, 81):
            count = PARTIAL.get(n)
            texts = ['X' * count + 'TAIL'] if count else ['SOURCE SENTINEL'] * (2 if n == 1 else 1)
            chapter = {'number': n, 'title': f'Safe source {n}',
                       'blocks': [{'kind': 'prose', 'text': text} for text in texts]}
            draft = {'schemaVersion': 1, 'language': 'ja', 'number': n,
                     'title': f'第{n}回', 'sourceTitle': chapter['title'],
                     'sourceSha256': source_hash(chapter)}
            if count:
                segments = [{'start': i, 'end': i + 1,
                             'sourceTextSha256': hashlib.sha256(b'X').hexdigest(),
                             'status': 'owner_translation_needed',
                             'label': f'【日訳未完 CH{n:03}-P{i+1:02}】'} for i in range(count)]
                segments.append({'start': count, 'end': count + 4,
                                 'sourceText': 'TAIL', 'text': '訳文'})
                draft.update(complete=False, status='partial_owner_translation_needed',
                             partialSourceBlockIndices=[0],
                             blocks=[{'kind': 'prose', 'sourceSegments': segments}])
            else:
                draft['blocks'] = [{'kind': 'prose', 'sourceText': text, 'text': '訳文'}
                                   for text in texts]
            chapters.append(chapter)
            drafts[f'ch{n:03}.{"partial" if count else "draft"}.json'] = draft
        return {'chapters': chapters}, drafts

    def _assert_release_rejected(self, mutate, message):
        import json, sys
        from types import SimpleNamespace
        from unittest.mock import patch
        import build_hongloumeng_reading_japanese as builder
        source, drafts = self._release_fixtures()
        mutate(source, drafts)
        def safe_read(path, *args, **kwargs):
            return json.dumps(source if path == builder.SOURCE else drafts[path.name])
        with patch.object(builder, 'checked_input_paths'),              patch.object(Path, 'read_text', safe_read),              patch.object(Path, 'is_symlink', return_value=False),              patch.object(Path, 'stat', return_value=SimpleNamespace(st_nlink=1)),              patch.object(Path, 'mkdir') as mkdir,              patch.object(Path, 'write_text') as write,              patch.object(sys, 'argv', ['build_hongloumeng_reading_japanese.py']):
            with self.assertRaisesRegex(ValueError, message):
                builder.main()
            mkdir.assert_not_called()
            write.assert_not_called()

    def test_release_rejects_missing_block_before_writes(self):
        self._assert_release_rejected(
            lambda source, drafts: drafts['ch001.draft.json']['blocks'].pop(),
            'block count differs')

    def test_release_rejects_late_source_hash_before_writes(self):
        self._assert_release_rejected(
            lambda source, drafts: drafts['ch080.draft.json'].update(sourceSha256='0' * 64),
            'source changed')

    def test_release_rejects_partial_coverage_before_writes(self):
        self._assert_release_rejected(
            lambda source, drafts: drafts['ch075.partial.json']['blocks'][0]['sourceSegments'].pop(),
            'incomplete or falsely partial segmentation')

    def test_edition_name(self):
        for name, body in self.plan.items():
            if name.endswith('.html'):
                self.assertIn('大知校訂庚辰本', body)
                self.assertNotIn('大治校訂庚辰本', body)

if __name__=='__main__':unittest.main()
