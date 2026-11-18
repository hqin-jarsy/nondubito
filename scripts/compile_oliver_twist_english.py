#!/usr/bin/env python3
"""Import reviewed complete English drafts, without writing published HTML."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];D=R/'data/oliver-twist/multilingual'
source=json.loads((D/'source.json').read_text())['articles']
titles=['He Asked for More','Fagin’s Lesson','She Is an Accomplice','She Went Back']
decks=['A bowl of gruel, a five-pound offer, and the hunger missing from an institution’s account.','Food, shelter, companions and praise are real. So are deception, confinement and the price of belonging.','Nancy helps recapture the child. Her history and her later intervention do not cancel that participation.','Compassion, attachment, a refused payment, and an act that does not wait to be settled by a new position.']
arts=[]
for i,s in enumerate(source):
 body=(D/f'en-{i+1}.txt').read_text().splitlines();assert len(body)==len(s['body_zh'])
 arts.append({'slug':s['slug'],'title':titles[i],'deck':decks[i],'body':body,'source_note':body[-1],'edition_note':'Complete English rendering of the Chinese essay, with documented factual corrections. Dialogue is translated or paraphrased for this essay. Full-book spoilers.','coverage':[{'source_block':j+1,'target_block':j+1} for j in range(len(body))]})
payload={'language':'en','series':{'title':'Reading Oliver Twist','deck':'Four essays on institutional accounting, the price of belonging, complicity and an act not offered in exchange.','intro':[],'note':'Charles Dickens, Oliver Twist (1837–1839). Based on the Chinese essays and their documented original-text corrections.'},'ui':{'series':'Reading Oliver Twist'},'articles':arts}
(D/'en.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print('English JSON compiled: 502 source-aligned blocks.')
