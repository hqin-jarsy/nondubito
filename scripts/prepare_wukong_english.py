#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Locally correct the original independent English essays without block expansion."""
import json,sys
from pathlib import Path
from prepare_action_sources import Document
R=Path(__file__).resolve().parents[1];D=R/'data/black-myth-wukong';M=D/'multilingual'
s=json.loads((M/'source-original.json').read_text())['articles']
changes={
(1,4):'The Destined One’s journey begins with an old monkey recounting what happened to Sun Wukong: rebellion, submission, withdrawal, defeat, and the scattering of six relics. The younger generation receives the story; the traveler sets out to recover what was lost.',
(1,18):'The Journal records many defeated enemies and other encountered figures in a series often translated as portraits. Its entries supply origins, histories, anecdotes, and verse. During combat, the creature is an obstacle. In the archive, it becomes a being who had a life before the player entered it.',
(2,13):'The Destined One travels through different regions, families, sects, and old disasters to recover them. Those places have their own histories and connections, rather than forming a single continuous political conflict. Wukong’s scattered components provide the line that converts their different lives into stations on one route.',
(2,14):'Five roots answer what a body can perceive and do. In the reading developed here, the sixth raises the question of why, whether, and in whose name action occurs.',
(2,16):'The game supports two rival readings of the collection. A successor with Wukong’s capacities but without his remembered defiance may still be subjected to the circlet. The hidden route, involving Erlang’s release of Wukong’s memories, opens another possibility: restoration or succession without the completed gesture of restraint. Neither possibility means the Destined One has no will of his own.',
(2,28):'The old monkey tells the story that launches the journey, indicates the route, appears at decisive moments, and explains the final relics. His manner is patient and protective. At the end of the ordinary route, the same hand that guided the journey lifts the circlet.',
(2,31):'## The walker receives only part of the story',
(2,32):'Local spirits, bosses, Erlang, Zhu Bajie, and the old monkey each understand pieces of the route. The Destined One receives instructions and partial disclosures but never gives his own account. Hearing about the missing root is not the same as learning every arrangement behind the road.',
(3,1):'Yellowbrow intervenes in a group of people’s circumstances, placing temptation before them. Their greed and struggle are real. He points to the result as proof: this is what human beings are.',
(3,5):'These are not empty villain speeches. They challenge the serene claim that beings possess fixed capacities and must remain in their assigned order. Yellowbrow also builds Little Leiyin Temple, gathers believers, brings Kang-Jin under his control, and defeats other celestial opponents. Dissent becomes an alternative religious project backed by coercive power.',
(3,8):'Yellowbrow’s experiments do not need fake events. People really choose what he predicts. The manipulation occurs one step earlier: he intervenes in the setting and supplies the lure, then treats behavior inside the designed environment as evidence of unchanging nature.',
(3,27):'Yellowbrow is Maitreya’s disciple and uses stolen religious artifacts to stage his alternative order. At the end, the master intervenes again. Revolt has not severed Yellowbrow’s dependence on the powers of the world he challenges.',
(4,1):'At the end of the ordinary route, after the final trial within the stone egg, the Destined One sits before the old monkey. The elder approaches holding a golden circlet and places it on his head. The protagonist does not resist. The procedure concludes.',
(4,2):'In the secret route, reached after the optional encounters culminating in Erlang and the return of Wukong’s memories, the old monkey lifts the circlet, but the scene does not show it being placed. The Destined One opens his eyes. The difference between the endings is small enough to fit inside one gesture and large enough to reorganize the journey.',
(4,5):'The secret ending does not show the protagonist overpowering the circlet. It leaves the gesture incomplete. In one reading, memory has entered the place where an external purpose might otherwise be installed.',
(4,9):'Black Myth permits another reading. The circlet is not only pressure applied against a developed will. It also suggests an external command occupying the place from which purpose should be chosen. The old monkey acknowledges the strong will the Destined One has forged through hardship: missing Wukong’s memory does not make him an empty shell. A body with immense ability can nevertheless have its purpose prescribed by someone else.',
(4,12):'Erlang appears as one of Heaven’s most authoritative enforcers and the warrior who helps break Wukong apart in the opening. The secret route reveals him preserving and releasing Wukong’s memories. After the battle he explains parts of the trials and what he came to understand; other figures associated with established powers participate in ways the game leaves partly unexplained.',
(4,20):'The secret ending’s animation moves backward through Wukong’s remembered history. It reaches the Water Curtain Cave, where allies feast and speak of challenging Heaven, in contrast with the emptied cave. Wukong takes up his staff and walks out.',
(4,21):'This is not a forecast of victory. It is memory of loss returning alongside memory of defiance. The old gathering has dispersed; Heaven and the Buddhist order remain; the hierarchies criticized throughout the game have not been abolished.',
(4,29):'One event is different: the circlet is raised, but the scene does not show it descending onto his head. The negative form matters. The game does not tell us who the Destined One becomes; it leaves one answer uninstalled and his next step open.'}
arts=[];records=[]
for i,a in enumerate(s,1):
 body=[changes.get((i,j),b) for j,b in enumerate(a['body_en'],1)]
 d=Document((R/a['source_html']).read_text()); title=next(n.text().strip() for n in d.root.walk() if n.has('essay-page-title','lang-en'));deck=next(n.attrs['content'] for n in d.root.walk() if n.tag=='meta' and n.attrs.get('name')=='description')
 arts.append(dict(slug=a['slug'],title=title,deck=deck,body=body,edition_note='An independently structured English essay, retained with local factual and interpretive-boundary corrections. Full-game spoilers.'))
 records.append(dict(slug=a['slug'],original_body=a['body_en'],revised_body=body,block_mapping=[dict(target_block=j,original_block=j,kind='local-correction' if (i,j) in changes else 'retained') for j in range(1,len(body)+1)]))
(M/'en.json').write_text(json.dumps(dict(language='en',series=dict(title='Reading Black Myth: Wukong',deck='Mandate, inheritance, manufactured proof, and an unfinished refusal.',intro=[]),ui=dict(series='Reading Black Myth: Wukong'),articles=arts),ensure_ascii=False,indent=2)+'\n')
(D/'english-corrections.json').write_text(json.dumps(dict(policy='Original independent English arguments and all 134 blocks preserved. Local factual corrections only; no forced Chinese alignment or narrative expansion.',articles=records),ensure_ascii=False,indent=2)+'\n')
print(len(changes),'local edits; counts',[len(a['body']) for a in arts])
