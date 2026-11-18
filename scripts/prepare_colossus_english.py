#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local corrections to the original independent English essays; preserve all blocks."""
import json
from pathlib import Path
from prepare_action_sources import Document
R=Path(__file__).resolve().parents[1];D=R/'data/shadow-of-the-colossus';M=D/'multilingual'
s=json.loads((M/'source-original.json').read_text())['articles']
changes={
(1,4):'Before entering the forbidden land, Wander has stolen an ancient sword, carried away Mono’s body, and violated a strict prohibition. These are not separate offenses. Together they reject the authority that classified her death as necessary.',
(1,17):'But the impossibility of asking her does not authorize every substitute judgment. Wander never seeks another witness, investigates the colossi, or asks whether anything besides Dormin’s proposal could answer the wrong done to her. Dormin provides the tasks and route. Even Mono’s gradually audible voice does not become a conversation in which the two decide together.',
(1,24):'After each colossus falls, shadowy tendrils pierce Wander and return him to the shrine. Mono’s voice becomes clearer in his visions, calling to hold him back. White doves accumulate near the altar. Signs of her return accompany the destruction elsewhere.',
(2,1):'A vast shadow crosses the desert. Above it, the thirteenth colossus, commonly called Phalanx, circles in the sky. It does not hunt Wander or guard a village from him. Unless attacked and boarded, it has no interest in him at all.',
(2,30):'By the time fifteen colossi have fallen, Mono seems closer to waking, and white doves gather near the altar. Wander no longer resembles the person who crossed the bridge. The final colossus waits at the far edge of the land.',
(3,9):'The player can still make Wander fight the pull, claw at the stone, and try to move toward Mono’s altar rather than the exit. The game never reveals his love as a sham. It lets devotion and violation remain true together. Love explains his refusal to stop; it does not authorize him to sign for sixteen others.',
(3,15):'Her restored life arrives attached to decisions she did not make: her original sacrifice, the removal of her body, Wander’s bargain, sixteen deaths, and Wander’s drastic bodily transformation. She was absent from the deliberation. The story does not specify everything she comes to understand, but none of that can make her a consenting participant after the fact.',
(3,21):'Agro enters the shrine alive but injured. The game does not establish whether Mono knew the horse before her death; it simply shows her receiving Agro without fear and following the animal to the drained pool. There she finds a horned infant: Wander, now in a radically changed form.',
(3,22):'Mono lifts the child. No prophecy directs her, no exchange requires it, and no practical reward follows. She has just returned to life in an isolated land. She does not first demand an account of this infant’s identity or first classify him through the suspicion those horns can invite.',
(3,29):'The first containment left sixteen embodied fragments that acquired territories and perhaps lives of their own. The second leaves Wander as a horned infant. The body is no longer in its former shape; Mono nevertheless lifts him. Containment has not assigned the whole life that follows.',
(3,32):'High above the shrine is a garden with water, fruit, animals, and sunlight. Players can reach it through exploration, but it is not an objective on Wander’s assigned list. That objective sends him outward across the land and back to the altar below.',
(3,33):'The final movement belongs to Mono, the infant Wander, and the injured horse ascending toward it. The bridge is gone. The young man who did everything for her no longer stands beside her in his former shape. Nobody explains the debt or promises rescue. The ending does not call this happiness.'}
arts=[];records=[]
for i,a in enumerate(s,1):
 body=[changes.get((i,j),b) for j,b in enumerate(a['body_en'],1)]
 d=Document((R/a['source_html']).read_text());title=next(n.text().strip() for n in d.root.walk() if n.has('essay-page-title','lang-en'));deck=next(n.attrs['content'] for n in d.root.walk() if n.tag=='meta' and n.attrs.get('name')=='description')
 arts.append(dict(slug=a['slug'],title=title,deck=deck,body=body,edition_note='An independently structured English essay, retained with local factual and dependent-interpretation corrections. Full-game spoilers.'))
 records.append(dict(slug=a['slug'],original_body=a['body_en'],revised_body=body,block_mapping=[dict(target_block=j,original_block=j,kind='local-correction' if (i,j) in changes else 'retained') for j in range(1,len(body)+1)]))
(M/'en.json').write_text(json.dumps(dict(language='en',series=dict(title='Reading Shadow of the Colossus',deck='A rescue, its unchosen costs, and care outside the bargain.',intro=[]),ui=dict(series='Reading Shadow of the Colossus'),articles=arts),ensure_ascii=False,indent=2)+'\n')
(D/'english-corrections.json').write_text(json.dumps(dict(policy='Retain all 101 original independent English blocks; local factual and direct dependent corrections only.',articles=records),ensure_ascii=False,indent=2)+'\n')
print(len(changes),'local corrections; counts',[len(a['body']) for a in arts])
