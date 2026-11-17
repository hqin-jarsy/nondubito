#!/usr/bin/env python3
"""Build only Moon and Sixpence editions from reviewed, durable paragraph drafts."""
from pathlib import Path
import json,re
import moon_literary_render as r
R=Path(__file__).resolve().parents[1]
D=R/'data/the-moon-and-sixpence/multilingual'
directory='essays/literature/the-moon-and-sixpence'
meta={
'en':('Reading The Moon and Sixpence','Four essays on personal necessity, the damage it does not cancel, and a hand that stops before a painting.',['He Left Without a Reason','He Did Not Destroy the Painting','It Is Not an Excuse','Both Things Are True'],['A departure without a public justification.','Stroeve sees what his hatred cannot determine.','The account Strickland never submitted.','Two truths without a final balance.']),
'ja':('『月と六ペンス』を読む','自分だけの必然、それで消えない傷、絵の前で止まる手をたどる四篇。',['去った日に理由は残さなかった','彼は絵を壊さなかった','これは弁護ではない','両方とも本当だ'],['公的な正当化を伴わない出発。','憎しみによって決まらないものが見える瞬間。','ストリックランドが提出しなかった勘定。','相殺できない二つの真実。']),
'fr':('Lire La Lune et Six Pence','Quatre essais sur une nécessité personnelle, les blessures qu’elle n’annule pas et une main qui s’arrête devant un tableau.',['Il est parti sans donner de raison','Il n’a pas détruit le tableau','Ceci n’est pas une défense','Les deux sont vrais'],['Un départ sans justification publique.','Stroeve voit ce que sa haine ne détermine pas.','Le compte que Strickland n’a jamais présenté.','Deux vérités sans bilan final.']),
'de':('Der Mond und die sechs Pence lesen','Vier Essays über ein eigenes Müssen, den dadurch nicht aufgehobenen Schaden und eine Hand, die vor einem Bild innehält.',['Er ging, ohne einen Grund zu nennen','Er zerstörte das Bild nicht','Dies ist keine Verteidigung','Beides ist wahr'],['Ein Aufbruch ohne öffentliche Rechtfertigung.','Stroeve sieht, worüber sein Hass nicht entscheidet.','Die Rechnung, die Strickland nie einreichte.','Zwei Wahrheiten ohne Schlussbilanz.']),
'es':('Leer La luna y seis peniques','Cuatro ensayos sobre una necesidad propia, el daño que no cancela y una mano que se detiene ante un cuadro.',['Se fue sin dar una razón','No destruyó el cuadro','Esto no es una defensa','Ambas cosas son verdad'],['Una partida sin justificación pública.','Stroeve ve lo que su odio no determina.','La cuenta que Strickland nunca presentó.','Dos verdades sin un balance final.']),
'ko':('『달과 6펜스』 읽기','자기만의 필연, 그것으로 사라지지 않는 피해, 그림 앞에서 멈춘 손을 따라가는 네 편의 글.',['떠나던 날 이유를 남기지 않았다','그는 그림을 부수지 않았다','이것은 변호가 아니다','둘 다 참이다'],['공적 정당화가 없는 출발.','스트루브가 증오로 결정할 수 없는 것을 보는 순간.','스트릭랜드가 제출하지 않은 계산서.','마지막 결산 없이 남는 두 진실.'])}
notes={
'en':('A complete English rendering of the Chinese essay, restoring its scenes and argument with documented factual corrections and limited interpretive qualifications. Full-book spoilers.','Source: W. Somerset Maugham, The Moon and Sixpence. The Chinese essays use Fu Weici’s translated character names. Plot details checked against the English text, chapters XII, XXXIX, LVI–LVIII. Dialogue is paraphrased, not quoted from a published translation.'),
'ja':('中国語の随筆の場面と論旨を保った全訳。記録した事実訂正と限定的な解釈上の留保を含みます。結末に触れます。','出典：W・サマセット・モーム『月と六ペンス』。中国語原稿の人名は傅惟慈訳による。第12・39・56〜58章の英語本文で情節を確認。台詞は要約であり、既刊日本語訳の引用ではありません。'),
'fr':('Version intégrale de l’essai chinois, conservant ses scènes et son argument, avec corrections factuelles documentées et nuances interprétatives limitées. Révélations sur l’ensemble du roman.','Source : W. Somerset Maugham, The Moon and Sixpence. Les noms chinois suivent la traduction de Fu Weici. Vérification dans le texte anglais, chapitres XII, XXXIX et LVI–LVIII. Les dialogues sont reformulés, non cités d’une traduction française publiée.'),
'de':('Vollständige Übertragung des chinesischen Essays mit seinen Szenen und Argumenten, dokumentierten Sachkorrekturen und begrenzten interpretativen Einschränkungen. Enthält das Ende des Romans.','Quelle: W. Somerset Maugham, The Moon and Sixpence. Chinesische Namen nach Fu Weicis Übersetzung. Handlungsdetails anhand des englischen Textes, Kapitel XII, XXXIX und LVI–LVIII, geprüft. Dialoge sind sinngemäß wiedergegeben, nicht aus einer veröffentlichten deutschen Übersetzung zitiert.'),
'es':('Versión íntegra del ensayo chino que conserva escenas y argumento, con correcciones factuales documentadas y matices interpretativos limitados. Revela el desenlace.','Fuente: W. Somerset Maugham, The Moon and Sixpence. Los nombres chinos siguen la traducción de Fu Weici. Detalles contrastados con el texto inglés, capítulos XII, XXXIX y LVI–LVIII. Los diálogos se parafrasean; no son citas de una traducción española publicada.'),
'ko':('중국어 글의 장면과 논지를 보존한 전체 번역입니다. 기록된 사실 수정과 제한적인 해석상의 단서를 포함합니다. 결말을 다룹니다.','출처: 서머싯 모옴, The Moon and Sixpence. 중국어 원고의 인명은 傅惟慈 번역을 따릅니다. 영어 원문 12·39·56~58장으로 사건을 확인했습니다. 대사는 요약이며 출간된 한국어 번역의 인용이 아닙니다.')}
def parts(lang):
 result=[]
 for chunk in (D/(lang+'.txt')).read_text().split('@@')[1:]:
  slug,body=chunk.strip().split('\n',1)
  result.append((slug,[p.strip() for p in body.strip().split('\n\n') if p.strip()]))
 return result
slugs=[s for s,_ in parts('en')]
assert len(slugs)==4
for lang,(title,deck,titles,decks) in meta.items():
 entries=parts(lang)
 assert [s for s,_ in entries]==slugs
 assert [len(b) for _,b in entries]==[len(b) for _,b in parts('en')],(lang,[len(b) for _,b in entries])
 payload=dict(language=lang,series=dict(title=title,deck=deck,intro=[],note=notes[lang][1]),ui=dict(series=title),articles=[dict(slug=s,title=titles[i],deck=decks[i],body=b,edition_note=notes[lang][0],source_note=notes[lang][1]) for i,(s,b) in enumerate(entries)],review=dict(report='editorial-review.md',method='Authoring AI editorial review; no claim of native-speaker or independent scholarly certification.'))
 (D/(lang+'.json')).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
profile=dict(id='the-moon-and-sixpence',directory=directory,date='2026-11-17',source_format='literary-html',slugs=slugs,languages=['ja','fr','de','es','ko'],primary_editions={'en':'','zh':'','zh-hant':''},builder='scripts/build_moon_languages.py',draft_format='@@slug followed by blank-line-separated paragraphs; ## section headings',source='W. Somerset Maugham, The Moon and Sixpence; Chinese essays in primary HTML')
(D/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n')
r.patch_primary(directory,{s:b+['*'+notes['en'][1]+'*'] for s,b in parts('en')})
for slug in slugs:
 p=R/directory/(slug+'.html');t=p.read_text().replace('A complete English rendering of the Chinese essay, preserving its scenes and argument. Full-book spoilers.',notes['en'][0]);p.write_text(t)
r.render(directory,'the-moon-and-sixpence')
print('Moon: restored 4 English essays; rendered 25 pages in 5 languages.')
