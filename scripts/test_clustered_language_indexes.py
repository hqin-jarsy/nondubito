#!/usr/bin/env python3
"""Read-only structural checks for grouped language reading routes."""
import copy
import unittest

from clustered_language_indexes import grouped_index
from test_companion_languages import Parsed


class GroupedLanguageIndexes(unittest.TestCase):
    def setUp(self):
        self.spec={'slugs':[f'ep{i:02d}' for i in range(1,10)],'index_groups':[
            {'id':'agreements','slugs':[f'ep{i:02d}' for i in range(1,5)]},
            {'id':'protection','slugs':[f'ep{i:02d}' for i in range(5,8)]},
            {'id':'afterwards','slugs':['ep08','ep09']}]}
        self.data={'series':{'index_groups':[{'id':'agreements','title':'约定、追问与信任'},
            {'id':'protection','title':'牵制、防御与接纳'},{'id':'afterwards','title':'去留与共同生活'}]},
            'ui':{'contents':'全部九篇'}}
        self.cards=[(slug,f'<a class="lw-card" href="{slug}.html"><h2>{slug}</h2></a>') for slug in self.spec['slugs']]

    def test_all_nine_cards_are_preserved_in_order_in_three_groups(self):
        page=Parsed(grouped_index(self.spec,self.data,self.cards))
        self.assertEqual([n.attrs['href'] for n in page.nodes('a','lw-card')],
                         [slug+'.html' for slug in self.spec['slugs']])
        self.assertEqual([len([n for n in grid.walk() if n.has_class('lw-card')]) for grid in page.nodes('section','lw-grid')],[4,3,2])
        self.assertEqual(len(page.nodes('h2')),3)
        self.assertEqual([n.text() for n in page.nodes('h3')],self.spec['slugs'])
        ids={n.attrs['id'] for n in page.root.walk() if 'id' in n.attrs}
        for link in page.nodes('a'):
            if link.attrs['href'].startswith('#'):self.assertIn(link.attrs['href'][1:],ids)

    def test_labels_are_escaped_and_ordinary_indexes_are_untouched(self):
        self.data['series']['index_groups'][0]['title']='<script>not markup</script>'
        text=grouped_index(self.spec,self.data,self.cards)
        self.assertNotIn('<script>',text)
        self.assertIn('&lt;script&gt;',text)
        self.assertIsNone(grouped_index({'slugs':self.spec['slugs']},self.data,self.cards))

    def test_omitted_duplicate_reordered_and_mismatched_routes_are_rejected(self):
        cases=[]
        for field,value in [('slugs',['ep01']),('slugs',['ep01','ep01']),('id','not-a-group')]:
            spec=copy.deepcopy(self.spec);spec['index_groups'][0][field]=value;cases.append(spec)
        spec=copy.deepcopy(self.spec);spec['index_groups'][0]['slugs'].reverse();cases.append(spec)
        for spec in cases:
            with self.assertRaises(AssertionError):grouped_index(spec,self.data,self.cards)


if __name__=='__main__':unittest.main()
