#!/usr/bin/env python3
"""Import full reviewed drafts without changing published HTML."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];D=R/'data/rickshaw-boy/multilingual'
source=json.loads((D/'source.json').read_text())['articles']
titles=['He Wanted a Rickshaw','Huniu and Xiaofuzi','He Is Still Alive']
decks=['A rickshaw, the savings for another, and a funeral: three defeats of an ordinary hope.','Two constrained lives, the price imposed on another person, and care without a return.','Not simply becoming poor: a man learns to turn another person into a sum of money.']
arts=[]
for i,s in enumerate(source):
 body=(D/f'en-{i+1}.txt').read_text().splitlines();assert len(body)==len(s['body_zh']);assert [j for j,p in enumerate(body) if p.startswith('## ')]==[j for j,p in enumerate(s['body_zh']) if p.startswith('## ')]
 arts.append({'slug':s['slug'],'title':titles[i],'deck':decks[i],'body':body,'source_note':body[-1],'edition_note':'Complete English rendering of the Chinese essay, with documented original-text corrections. Quotations and dialogue are translated or paraphrased for this essay. Full-book spoilers.','coverage':[{'source_block':j+1,'target_block':j+1} for j in range(len(body))]})
payload={'language':'en','series':{'title':'Reading Rickshaw Boy','deck':'Three essays on defeated hopes, constrained choices, and a person who learns the calculation that has been used on him.','intro':[],'note':'Based on the Chinese essays on Lao She’s Rickshaw Boy. Full-book spoilers.'},'ui':{'series':'Reading Rickshaw Boy'},'articles':arts}
(D/'en.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');print('English JSON compiled: 399 complete aligned blocks.')
