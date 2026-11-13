#!/usr/bin/env python3
import copy
import hashlib
import unittest
from hongloumeng_japanese_pipeline import source_hash, validate, validate_partial, render

class JapaneseDraftTests(unittest.TestCase):
    def setUp(self):
        self.source = {'number': 1, 'title': '第一回', 'blocks': [{'kind':'verse','text':'诗行','first':True,'last':True}]}
        self.draft = {'schemaVersion':1,'language':'ja','number':1,'title':'第一回', 'sourceTitle':'第一回',
                      'sourceSha256':source_hash(self.source), 'blocks':[{'kind':'verse','sourceText':'诗行','text':'歌の一行','first':True,'last':True}], 'notes':[]}
    def test_valid(self):
        self.assertEqual(validate(self.source,self.draft)['blocks'],1)
    def test_stale_source(self):
        self.source['blocks'][0]['text']='別字'
        with self.assertRaises(ValueError):validate(self.source,self.draft)
    def test_missing_block(self):
        self.draft['blocks']=[]
        with self.assertRaises(ValueError):validate(self.source,self.draft)
    def test_blank(self):
        self.draft['blocks'][0]['text']=' '
        with self.assertRaises(ValueError):validate(self.source,self.draft)
    def test_wrong_verse_boundary(self):
        self.draft['blocks'][0]['last']=False
        with self.assertRaises(ValueError):validate(self.source,self.draft)
    def test_escaped_private_reader(self):
        self.draft['blocks'][0]['text']='<script>\n歌'
        output=render(self.draft)
        self.assertIn('&lt;script&gt;<br>歌',output)
        self.assertIn('noindex,nofollow',output)
        self.assertNotIn('<script>',output)


class UnchangedBylineTests(unittest.TestCase):
    def setUp(self):
        self.source = {'number': 38, 'title': '第三十八回', 'blocks': [
            {'kind': 'verse', 'text': '诗行', 'first': False, 'last': False}
            for _ in range(90)]}
        for index, name, heading in [
            (39, '枕霞旧友', '对菊'), (45, '枕霞旧友', '供菊'),
            (69, '蕉下客', '簪菊'), (75, '枕霞旧友', '菊影'),
            (87, '蕉下客', '残菊'),
        ]:
            self.source['blocks'][index]['text'] = name
            self.source['blocks'][index - 1].update(text=heading, first=True)
        self.draft = {'schemaVersion': 1, 'language': 'ja', 'number': 38,
                      'title': '第三十八回', 'sourceTitle': '第三十八回',
                      'blocks': [dict(b, sourceText=b['text'], text='歌の一行')
                                 for b in self.source['blocks']]}
        for index in (39, 45, 69, 75, 87):
            self.draft['blocks'][index]['text'] = self.source['blocks'][index]['text']
        self.rebind()

    def rebind(self):
        self.draft['sourceSha256'] = source_hash(self.source)

    def assert_untranslated(self):
        self.rebind()
        with self.assertRaisesRegex(ValueError, 'untranslated source copy'):
            validate(self.source, self.draft)

    def test_all_five_exact_bylines_allowed(self):
        self.assertEqual(validate(self.source, self.draft)['blocks'], 90)

    def test_other_chapter_rejected(self):
        self.source['number'] = self.draft['number'] = 37
        self.assert_untranslated()

    def test_same_name_at_other_position_rejected(self):
        self.source['blocks'][40]['text'] = '枕霞旧友'
        self.draft['blocks'][40].update(sourceText='枕霞旧友', text='枕霞旧友')
        self.assert_untranslated()

    def test_different_name_at_allowed_position_rejected(self):
        self.source['blocks'][39]['text'] = '蕉下客'
        self.draft['blocks'][39].update(sourceText='蕉下客', text='蕉下客')
        self.assert_untranslated()

    def test_changed_byline_structure_rejected(self):
        for field, value in [('kind', 'prose'), ('first', True), ('last', True),
                             ('extra', 'unexpected')]:
            with self.subTest(field=field):
                self.setUp()
                self.source['blocks'][39][field] = value
                self.draft['blocks'][39][field] = value
                self.assert_untranslated()

    def test_changed_heading_structure_or_text_rejected(self):
        for field, value in [('kind', 'prose'), ('first', False), ('last', True),
                             ('text', '另一诗题')]:
            with self.subTest(field=field):
                self.setUp()
                self.source['blocks'][38][field] = value
                if field == 'text':
                    self.draft['blocks'][38]['sourceText'] = value
                else:
                    self.draft['blocks'][38][field] = value
                self.assert_untranslated()

    def test_copied_verse_rejected(self):
        self.draft['blocks'][40]['text'] = self.source['blocks'][40]['text']
        self.assert_untranslated()

    def test_copied_prose_rejected(self):
        self.source['blocks'][0] = {'kind': 'prose', 'text': '正文'}
        self.draft['blocks'][0] = {'kind': 'prose', 'sourceText': '正文', 'text': '正文'}
        self.assert_untranslated()

    def test_copied_heading_rejected(self):
        self.draft['blocks'][38]['text'] = self.source['blocks'][38]['text']
        self.assert_untranslated()

class PartialDraftTests(unittest.TestCase):
    def setUp(self):
        self.source = {'number': 1, 'title': '一', 'blocks': [{'kind':'prose','text':'甲'}, {'kind':'prose','text':'乙'}]}
        self.draft = {'schemaVersion':1,'language':'ja','number':1,'status':'partial','sourceSha256':source_hash(self.source),
                      'omittedSourceBlockIndices':[1], 'blocks':[{'sourceIndex':0,'kind':'prose','sourceText':'甲','text':'第一の文'}, {'sourceIndex':1,'kind':'prose','omitted':True}]}
    def test_partial_explicit(self):
        self.assertEqual(validate_partial(self.source,self.draft)['status'],'partial_alignment_validated_not_complete')
    def test_partial_cannot_claim_complete(self):
        self.draft['complete']=True
        with self.assertRaises(ValueError):validate_partial(self.source,self.draft)
    def test_partial_cannot_hide_another_missing_block(self):
        self.draft['blocks']=self.draft['blocks'][1:]
        with self.assertRaises(ValueError):validate_partial(self.source,self.draft)
    def test_partial_no_duplicate_index(self):
        self.draft['blocks'].append(self.draft['blocks'][0])
        with self.assertRaises(ValueError):validate_partial(self.source,self.draft)
    def test_withheld_must_not_contain_source_copy(self):
        self.draft['blocks'][1]['sourceText']='乙'
        with self.assertRaises(ValueError):validate_partial(self.source,self.draft)
    def test_full_validation_rejects_partial(self):
        with self.assertRaises(ValueError):validate(self.source,self.draft)

class SegmentedDraftTests(unittest.TestCase):
    def setUp(self):
        self.source={'number':1,'title':'一','blocks':[{'kind':'prose','text':'甲乙丙'}]}
        self.draft={'schemaVersion':1,'language':'ja','number':1,'status':'partial','sourceSha256':source_hash(self.source),
                    'omittedSourceBlockIndices':[],'partialSourceBlockIndices':[0],'blocks':[{'kind':'prose','sourceIndex':0,'sourceSegments':[
                        {'start':0,'end':1,'sourceText':'甲','text':'初め'},
                        {'start':1,'end':2,'sourceTextSha256':hashlib.sha256('乙'.encode()).hexdigest(),'status':'owner_translation_needed'},
                        {'start':2,'end':3,'sourceText':'丙','text':'終わり'}]}]}
    def test_valid_segmentation(self):
        result=validate_partial(self.source,self.draft)
        self.assertEqual(result['partiallyTranslatedBlocks'],1)
        self.assertEqual(result['ownerTranslationRanges'],[{'sourceBlockIndex':0,'start':1,'end':2}])
    def test_no_missing_character(self):
        self.draft['blocks'][0]['sourceSegments'][2]['start']=3
        with self.assertRaises(ValueError):validate_partial(self.source,self.draft)
    def test_no_unbound_gap(self):
        self.draft['blocks'][0]['sourceSegments'][1]['sourceTextSha256']='wrong'
        with self.assertRaises(ValueError):validate_partial(self.source,self.draft)
    def test_preserve_segmented_kind(self):
        self.draft['blocks'][0]['kind']='verse'
        with self.assertRaises(ValueError):validate_partial(self.source,self.draft)

if __name__=='__main__':unittest.main()
