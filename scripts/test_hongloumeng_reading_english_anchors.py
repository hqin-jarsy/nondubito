"""Current note-anchor tests. Synthetic rendering is not publication acceptance.

Full current checks: run test_hongloumeng_current_presentation.py --suite all,
then python3 -B -m unittest test_hongloumeng_reading_english_anchors -v.
Production resolution reads only committed glossary records, never QA ledgers.
"""
import copy
import json
import unittest
from html.parser import HTMLParser
import build_hongloumeng_reading_english as reader

class TextAndRefs(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True);self.depth=0;self.text='';self.positions=[];self.feed(source)
    def handle_starttag(self, tag, attrs):
        if tag=='sup':self.positions.append(len(self.text));self.depth+=1
    def handle_endtag(self,tag):
        if tag=='sup':self.depth-=1
    def handle_data(self,text):
        if not self.depth:self.text+=text

class AnchorTests(unittest.TestCase):
    def setUp(self):
        self.text='Before <&"雪𤫫\nanchor & tail > after.'
        self.source={'id':'hlm-c001-b0001','chapter':1,'index':1,'sourceHash':'a'*64,'layout':{'kind':'prose'}}
        self.unit={'id':self.source['id'],'sourceHash':'a'*64,'state':'accepted','segments':[{'kind':'prose','text':self.text},{'kind':'prose','text':'Untouched second segment.'}]}
        self.note={'unitId':self.unit['id'],'sourceHash':'a'*64,'glossaryId':'english-batch-001-005.json#/selectedReaderNotes/0','text':'Note <& text.'}
        start=self.text.index('anchor');end=start+len('anchor & tail')
        self.record={'text':self.note['text'],'textSHA256':reader.pipeline.sha(self.note['text'].encode()),'anchor':{'unitId':self.unit['id'],'sourceHash':'a'*64,'segmentIndex':0,'position':'after_anchor','start':start,'end':end,'text':self.text[start:end]}}
        self.documents={'english-batch-001-005.json':{'selectedReaderNotes':[self.record]}}
    def locate(self):return reader.note_location(self.note,self.source,self.unit,self.documents,{})
    def test_exact_range_raw_unicode_offset(self):self.assertEqual(self.locate(),(0,self.record['anchor']['end']))
    def test_segment_end_hash_not_unit_end(self):
        self.record.pop('anchor');self.record['placement']={'unitId':self.unit['id'],'segmentIndex':0,'segmentSHA256':reader.pipeline.sha(self.text.encode())};self.record['source']={'unitId':self.unit['id'],'sourceHash':'a'*64,'start':1,'end':3,'quote':'乙丙'}
        self.assertEqual(reader.note_location(self.note,self.source,self.unit,self.documents,{self.unit['id']:'甲乙丙丁'}),(0,len(self.text)))
        self.record['source']['quote']='wrong'
        with self.assertRaisesRegex(ValueError,'canonical source substring'):reader.note_location(self.note,self.source,self.unit,self.documents,{self.unit['id']:'甲乙丙丁'})
        self.record['source']['quote']='乙丙';self.record['placement']['segmentSHA256']='0'*64
        with self.assertRaisesRegex(ValueError,'segment hash'):reader.note_location(self.note,self.source,self.unit,self.documents,{self.unit['id']:'甲乙丙丁'})
    def test_no_explicit_placement_unit_end_default(self):
        self.note['glossaryId']='FIRST40-UNIT-NOTE'
        self.assertEqual(self.locate(),(1,len(self.unit['segments'][1]['text'])))
    def test_bad_explicit_fields_never_fall_back(self):
        mutations={'unitId':'wrong','sourceHash':'0'*64,'segmentIndex':3,'position':'before_anchor','start':-1,'end':999,'text':'wrong','offsetConvention':'UTF-16'}
        original=copy.deepcopy(self.record['anchor'])
        for key,value in mutations.items():
            with self.subTest(field=key):
                self.record['anchor']=dict(original,**{key:value})
                with self.assertRaises(ValueError):self.locate()
        self.record['anchor']=original
    def test_bool_and_empty_ranges_rejected(self):
        original=copy.deepcopy(self.record['anchor'])
        for changes in ({'segmentIndex':True},{'start':False},{'end':True},{'end':original['start']},{'start':original['end']+1}):
            with self.subTest(changes=changes):
                self.record['anchor']=dict(original,**changes)
                with self.assertRaises(ValueError):self.locate()
    def test_missing_ambiguous_and_wrong_record_rejected(self):
        original=copy.deepcopy(self.record)
        for change in ('missing','ambiguous','wording','wordingHash','noteSource','missingIndex','malformedPointer'):
            with self.subTest(change=change):
                self.record.clear();self.record.update(copy.deepcopy(original));note=copy.deepcopy(self.note)
                if change=='missing':self.record.pop('anchor')
                elif change=='ambiguous':self.record['placement']=self.record['anchor']
                elif change=='wording':self.record['text']='wrong'
                elif change=='wordingHash':self.record['textSHA256']='0'*64
                elif change=='noteSource':note['sourceHash']='0'*64
                elif change=='missingIndex':note['glossaryId']='english-batch-001-005.json#/selectedReaderNotes/1'
                else:note['glossaryId']='english-batch-001-005.json#/selectedReaderNote/0'
                with self.assertRaises(ValueError):reader.note_location(note,self.source,self.unit,self.documents,{})
    def test_inline_escaping_and_newline_body_reconstruction(self):
        offset=self.locate()[1]
        chapter={'number':1,'title':'Chapter 1\nFirst < line\nSecond & line','titleNote':None,'blocks':[dict(self.source['layout'],text=self.text,anchor=self.unit['id']+'-s1',note=self.note['text'],noteUnitId=self.unit['id'],noteOffset=offset)]}
        html=reader.render([chapter],preview=True)['ch001.html'];fragment=html.split('<div class="novel-text">',1)[1].split('</div>',1)[0];parsed=TextAndRefs(fragment)
        self.assertEqual(parsed.text,self.text);self.assertEqual(parsed.positions,[offset]);self.assertIn('&lt;&amp;&quot;雪𤫫\n',fragment);self.assertNotIn('<script',fragment)
    def test_title_full_newline_offsets(self):
        title='Chapter 1\nFirst <& line\nSecond 雪 line'
        for offset in (0,len('Chapter 1'),len('Chapter 1\n'),title.index('雪')+1,len(title)):
            with self.subTest(offset=offset):
                c={'number':1,'title':title,'titleNote':{'unitId':'hlm-c001-title','text':'Note','offset':offset},'blocks':[]};html=reader.render([c],preview=True)['ch001.html'];fragment=html.split('<h1>',1)[1].split('</h1>',1)[0];parsed=TextAndRefs(fragment);self.assertEqual(parsed.text,title);self.assertEqual(parsed.positions,[offset])
    def test_projected_offsets_reject_out_of_bounds_or_non_integer(self):
        for offset in (-1,999,True,1.5):
            for location in ('title','body'):
                with self.subTest(offset=offset,location=location):
                    c={'number':1,'title':'Chapter 1\nA\nB','titleNote':None,'blocks':[]}
                    if location=='title':c['titleNote']={'unitId':'hlm-c001-title','text':'Note','offset':offset}
                    else:c['blocks']=[{'kind':'verse','text':'A\nB','anchor':'hlm-c001-b0001-s1','note':'Note','noteOffset':offset}]
                    with self.assertRaisesRegex(ValueError,'Invalid projected'):reader.render([c],preview=True)
    def test_both_declared_segment_hashes_must_match(self):
        correct=reader.pipeline.sha(self.text.encode())
        self.record['anchor'].update(segmentSHA256=correct,segmentTextSHA256=correct)
        self.assertEqual(self.locate(),(0,self.record['anchor']['end']))
        for field in ('segmentSHA256','segmentTextSHA256'):
            with self.subTest(field=field):
                self.record['anchor'][field]='0'*64
                with self.assertRaisesRegex(ValueError,'segment hash differs: '+field):self.locate()
                self.record['anchor'][field]=correct
    def test_actual_declared_segment_text_hash_negatives(self):
        p=reader.pipeline;mapping=p.source_map(p.load_source());progress=json.loads((p.DATA/'progress.json').read_text());notes=json.loads((p.DATA/'reader-notes.json').read_text())
        sources={u['id']:u for u in mapping['units']};units={u['id']:u for u in progress['units']};by_note={n['unitId']:n for n in notes['notes']}
        filename='english-batch-056-060.json';original=json.loads((p.STANDARD/filename).read_text())
        for unit_id in ('hlm-c058-b0015','hlm-c058-b0017','hlm-c060-b0017'):
            with self.subTest(unit=unit_id):
                documents={filename:copy.deepcopy(original)};note=by_note[unit_id];index=int(note['glossaryId'].rsplit('/',1)[1]);anchor=documents[filename]['selectedReaderNotes'][index]['anchor']
                self.assertIn('segmentTextSHA256',anchor)
                self.assertEqual(anchor['segmentTextSHA256'],p.sha(units[unit_id]['segments'][anchor['segmentIndex']]['text'].encode()))
                self.assertEqual(reader.note_location(note,sources[unit_id],units[unit_id],documents,{}),(anchor['segmentIndex'],anchor['end']))
                anchor['segmentTextSHA256']='0'*64
                with self.assertRaisesRegex(ValueError,'segment hash differs: segmentTextSHA256'):reader.note_location(note,sources[unit_id],units[unit_id],documents,{})
    def test_actual80_public_projection_preserves_bodies_and_placements(self):
        p=reader.pipeline;mapping=p.source_map(p.load_source());progress=json.loads((p.DATA/'progress.json').read_text());notes=json.loads((p.DATA/'reader-notes.json').read_text());chapters=reader.project(mapping,progress,notes,range(1,81));by_unit={u['id']:u for u in progress['units']};note_lookup={n['unitId']:n for n in notes['notes']};found={};counts={'anchor':0,'placement':0,'default':0}
        for c in chapters:
            self.assertEqual(c['title'],by_unit[f"hlm-c{c['number']:03d}-title"]['segments'][0]['text'])
            if c['titleNote']:found[c['titleNote']['unitId']]=(0,c['titleNote']['offset'],c['titleNote']['text'])
            for b in c['blocks']:
                unit_id,i=b['anchor'].rsplit('-s',1);segment=by_unit[unit_id]['segments'][int(i)-1];self.assertEqual((b['text'],b['kind']),(segment['text'],segment['kind']))
                if 'note' in b:found[b['noteUnitId']]=(int(i)-1,b['noteOffset'],b['note'])
        self.assertEqual(set(found),set(note_lookup));self.assertEqual(len(found),80)
        for unit_id,note in note_lookup.items():
            unit=by_unit[unit_id];reference=note['glossaryId'];expected_index=len(unit['segments'])-1;expected_offset=len(unit['segments'][-1]['text'])
            if '#/selectedReaderNotes/' in reference:
                filename,index=reference.split('#/selectedReaderNotes/');record=json.loads((p.STANDARD/filename).read_text())['selectedReaderNotes'][int(index)];kind='anchor' if 'anchor' in record else 'placement';location=record[kind];expected_index=location['segmentIndex'];text=unit['segments'][expected_index]['text'];expected_offset=location['end'] if kind=='anchor' else len(text);counts[kind]+=1
                if kind=='anchor':self.assertEqual(text[location['start']:location['end']],location['text'])
                else:self.assertEqual(p.sha(text.encode()),location['segmentSHA256'])
            else:counts['default']+=1
            self.assertEqual(found[unit_id],(expected_index,expected_offset,note['text']))
        self.assertEqual(counts,{'anchor':37,'placement':9,'default':34})

if __name__=='__main__':unittest.main(verbosity=2)
