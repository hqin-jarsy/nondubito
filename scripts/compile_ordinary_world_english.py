#!/usr/bin/env python3
"""Import reviewed English paragraph drafts without writing published HTML."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];D=R/'data/ordinary-world/multilingual'
source=json.loads((D/'source.json').read_text())['articles']
titles=['Who calls them ordinary?','He decided for her','Why Runye went back','The Only One Who Did Not Classify Him','Is fidelity to oneself ordinary?']
decks=['Three kinds of steamed bun, a boy waiting in the rain, and a scale he has learned to use on himself.','Refusing love is a right. Claiming to know another person’s future is something else.','Giving, indebtedness, and a return that does not vindicate an imposed marriage.','Books, practical help, a promise beneath a tree, and a woman with a vocation of her own.','A scarred miner returns. Must that choice be scored as ascent or defeat?']
arts=[]
for i,s in enumerate(source):
 body=(D/f'en-{i+1}.txt').read_text().splitlines();assert len(body)==len(s['body_zh'])
 arts.append({'slug':s['slug'],'title':titles[i],'deck':decks[i],'body':body,'source_note':body[-1],'edition_note':'Complete English rendering of the Chinese essay, with documented factual corrections. Dialogue is rendered for this essay, not quoted from an identified English edition. Full-book spoilers.','coverage':[{'source_block':j+1,'target_block':j+1} for j in range(len(body))]})
payload={'language':'en','series':{'title':'Reading Ordinary World','deck':'Five essays on inherited rank, decisions made for others, care, recognition, and fidelity to oneself.','intro':[],'note':'Lu Yao, Ordinary World (1986–1988). Based on the Chinese essays and their documented factual corrections.'},'ui':{'series':'Reading Ordinary World'},'articles':arts}
(D/'en.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print('English JSON compiled: 571 source-aligned blocks.')
