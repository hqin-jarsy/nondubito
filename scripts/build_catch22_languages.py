#!/usr/bin/env python3
"""Compile reviewed paragraph drafts and render Catch-22 only, without discovery writes."""
from pathlib import Path
import json,re,hashlib
import catch22_literary_render as r
R=Path(__file__).resolve().parents[1];D=R/'data/catch-22/multilingual';directory='essays/literature/catch-22'
meta={
'ja':dict(series=dict(title='『キャッチ＝22』を読む',deck='見せられない規則、全員を数える帳簿、正しい処置の下に隠れる傷、そして人と経路を必要とする脱出。四つの随筆。'),titles=['誰も見たことのない規則','誰にでも持ち分がある','防弾服の下の傷','憲兵が階段を上がるとき'],decks=['論理の輪と、ローマで質問を終わらせる一語。同じ名の規則には、交渉する相手がいない。','卵も配当も本物だ。だが帳簿に書けない望みと、空になった救急箱はどこへ行くのか。','正しい処置が、致命傷を見えなくする。繰り返されるスノーデンの場面を読む。','通行証のない者が逮捕され、殺した者は残る。出るには、たどれる道と送り出す人が要る。']),
'de':dict(series=dict(title='Catch-22 lesen',deck='Vier Essays über eine unsichtbare Vorschrift, ein allumfassendes Kontobuch, die verdeckte Wunde und einen Ausweg, der Menschen ebenso braucht wie einen Weg.'),titles=['Die Vorschrift, die niemand gesehen hat','Jeder hat einen Anteil','Die Wunde unter dem Flakschutzanzug','Wenn die Militärpolizei heraufkommt'],decks=['Ein logischer Kreis und ein Wort, das jede Nachfrage beendet: Wer könnte eine Vorschrift ohne Urheber aufheben?','Milos Eier und Dividenden sind wirklich. Was geschieht mit dem, was in seinen Büchern keinen Platz findet?','Yossarian behandelt die falsche Stelle richtig. Der wiederkehrende Tod Snowdens verändert auch die Position des Lesers.','Verhaftet wird der Mann ohne Passierschein. Um fortzugehen, braucht Yossarian einen erprobten Weg und Menschen, die ihn gehen lassen.']),
'es':dict(series=dict(title='Leer Trampa-22',deck='Cuatro ensayos sobre un reglamento invisible, un libro de cuentas que incluye a todos, una herida oculta y una salida que necesita tanto un camino como personas.'),titles=['El reglamento que nadie ha visto','Todos tienen una participación','La herida bajo el chaleco antiesquirlas','Cuando sube la policía militar'],decks=['Un círculo lógico y una palabra que termina las preguntas: ¿con quién se negocia una regla sin autor?','Los huevos y dividendos de Milo son reales. Pero las personas tienen cosas que no caben en sus cuentas.','Yossarian trata correctamente el lugar equivocado. El relato vuelve a Snowden hasta mostrar lo que la ropa ocultaba.','Arrestan al hombre sin permiso, no al asesino. Salir exige una ruta recorrida y personas capaces de dejarlo partir.']),
'ko':dict(series=dict(title='『캐치-22』 읽기',deck='보이지 않는 규정, 모두를 포함하는 장부, 올바른 처치 아래 숨은 상처, 그리고 길과 사람을 함께 요구하는 탈출을 읽는 네 편의 글.'),titles=['아무도 본 적 없는 규정','모두에게 지분이 있다','방탄복 아래의 상처','헌병이 계단을 올라올 때'],decks=['논리적 원과 질문을 끝내는 단어. 작성자 없는 규정과는 누구를 통해 협상할 수 있을까.','달걀도 배당도 진짜다. 그러나 사람에게 속한 모든 것이 장부에 들어가는 것은 아니다.','요사리안은 엉뚱한 곳을 정확히 치료한다. 반복되는 스노든의 장면은 독자의 위치도 바꾼다.','통행증 없는 사람이 체포된다. 벗어나려면 이미 간 길과 그를 보내 줄 사람이 모두 필요하다.'])}
meta['fr']=json.loads((D/'fr-meta.json').read_text())
notes={
'en':('Complete English rendering of the Chinese essay, with factual corrections and cautious wording noted in the editorial report. Full-book spoilers.','Based on the Chinese essay, whose reading edition is Joseph Heller, Catch-22, translated by Nan Wen, Zhao Shouyin and Wang Deming, revised by Zhu Wan, Shanghai Translation Publishing House. Dialogue is rendered for this essay, not quoted from an identified English edition.'),
'ja':('中国語の随筆の場面と論旨を保った全訳です。事実の訂正と表現の調整は編集記録に記しています。結末に触れます。','原論考の参照版：ジョーゼフ・ヘラー『Catch-22』、南文・趙守垠・王徳明訳、主万校、上海訳文出版社。台詞は本論考に即した訳で、既刊日本語訳からの引用ではありません。'),
'fr':("Version intégrale de l'essai chinois, avec corrections factuelles et nuances consignées dans le rapport éditorial. Le dénouement est révélé.","L'essai chinois s'appuie sur Catch-22 de Joseph Heller, traduit par Nan Wen, Zhao Shouyin et Wang Deming, révisé par Zhu Wan, Shanghai Translation Publishing House. Les dialogues sont reformulés pour cet essai, non cités d'une traduction française publiée."),
'de':('Vollständige Übertragung des chinesischen Essays. Sachkorrekturen und vorsichtigere Formulierungen sind im redaktionellen Bericht dokumentiert. Einschließlich des Romanendes.','Grundlage des chinesischen Essays: Joseph Heller, Catch-22, übersetzt von Nan Wen, Zhao Shouyin und Wang Deming, durchgesehen von Zhu Wan, Shanghai Translation Publishing House. Dialoge sind für diesen Essay übertragen, nicht einer veröffentlichten deutschen Übersetzung entnommen.'),
'es':('Versión íntegra del ensayo chino, con correcciones y matices documentados en el informe editorial. Revela el desenlace.','El ensayo chino utiliza Catch-22 de Joseph Heller, traducción de Nan Wen, Zhao Shouyin y Wang Deming, revisada por Zhu Wan, Shanghai Translation Publishing House. Los diálogos se reformulan para este ensayo; no se citan de una traducción española publicada.'),
'ko':('중국어 글의 장면과 논지를 보존한 전체 번역입니다. 사실 수정과 표현 조정은 편집 기록에 남겼습니다. 결말을 다룹니다.','중국어 원문의 참조판: 조지프 헬러 『Catch-22』, 南文·赵守垠·王德明 번역, 主万 교열, 上海译文出版社. 대사는 이 글에 맞추어 옮겼으며 출간된 한국어 번역본에서 인용한 것이 아닙니다.')}
intros={
'ja':'ヘラーの不条理は、でたらめとは限らない。手続きは誤った対象の周囲で完璧に働き、規則は作者が見つからないために強くなる。ここでは、官僚制に収まらず、誤り、臆病、不在としてしか分類されない人々を追う。',
'fr':"L'absurdité de Heller est rarement arbitraire. Une procédure fonctionne parfaitement autour du mauvais objet ; une règle se renforce parce que personne ne peut en trouver l'auteur. Ces lectures suivent les personnes que la bureaucratie ne peut accueillir et ne classe que comme erreur, lâcheté ou absence.",
'de':'Hellers Absurdität ist selten beliebig. Verfahren funktionieren tadellos am falschen Gegenstand; Regeln werden stärker, weil niemand ihren Urheber findet. Diese Lektüren folgen den Menschen, für die die Bürokratie nur die Kategorien Fehler, Feigheit oder Abwesenheit kennt.',
'es':'El absurdo de Heller rara vez es arbitrario. Un procedimiento funciona perfectamente alrededor del objeto equivocado; una regla se fortalece porque nadie encuentra a su autor. Estas lecturas siguen a quienes la burocracia no puede acoger y solo clasifica como error, cobardía o ausencia.',
'ko':'헬러의 부조리는 대개 무작위가 아니다. 절차는 엉뚱한 대상을 두고 완벽하게 작동하고, 규칙은 작성자를 찾을 수 없어서 더 강해진다. 관료제가 받아들이지 못해 오류나 비겁함이나 부재로만 분류하는 사람들을 따라 읽는다.'}
for lang in meta:
 meta[lang]['series']['intro']=[intros[lang]]
 meta[lang]['series']['note']=notes[lang][1]
def parts(lang):
 result=[]
 for x in (D/(lang+'.txt')).read_text().split('@@')[1:]:
  slug,*body=x.strip().splitlines();result.append((slug,body))
 assert [len(b) for _,b in result]==[29,28,32,36]
 return result
slugs=[s for s,_ in parts('en')]
profile=dict(id='catch-22',directory=directory,date='2026-11-17',source_format='literary-html',slugs=slugs,languages=['de','fr','es','ja','ko'],primary_editions={'en':'','zh':'','zh-hant':''},builder='scripts/build_catch22_languages.py',draft_format='@@slug followed by one complete paragraph per line',source='Joseph Heller, Catch-22; Chinese literary essays in the primary HTML')
(D/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n')
english={s:b+[ '*'+notes['en'][1]+'*'] for s,b in parts('en')}
(D/'en.json').write_text(json.dumps(dict(language='en',articles=[dict(slug=s,body=b,source_note=notes['en'][1]) for s,b in parts('en')]),ensure_ascii=False,indent=2)+'\n')
for lang,m in meta.items():
 articles=[]
 for i,(slug,body) in enumerate(parts(lang)):
  assert slug==slugs[i]
  articles.append(dict(slug=slug,title=m['titles'][i],deck=m['decks'][i],body=body,edition_note=notes[lang][0],source_note=notes[lang][1],coverage=[{'source_paragraph':j+1,'target_paragraph':j+1} for j in range(len(body))]))
 payload=dict(language=lang,series=m['series'],ui=dict(series=m['series']['title']),articles=articles,review=dict(method='Full source-scene and argument review by the authoring AI; French also read by a second AI worker. Not native-speaker or independent scholarly certification.',report='editorial-review.md'))
 (D/(lang+'.json')).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
# Narrow, authorized Chinese/Hant correction; all other Chinese prose is preserved.
p=R/directory/(slugs[2]+'.html');s=p.read_text().replace('一直拖到最后一章才写出来','一直拖到倒数第二章（第四十一章）才写出来').replace('最后一章掀开的时候','倒数第二章掀开的时候');p.write_text(s)
p=R/directory/'zh-hant-data'/(slugs[2]+'.js');s=p.read_text().replace('一直拖到最后一章才写出来','一直拖到倒数第二章（第四十一章）才写出来').replace('最后一章掀开的时候','倒数第二章掀开的时候').replace('一直拖到最後一章才寫出來','一直拖到倒數第二章（第四十一章）才寫出來').replace('最後一章掀開的時候','倒數第二章掀開的時候');p.write_text(s)
r.patch_primary(directory,english)
# Override the general template's shorter edition notice with the accurate scope notice.
for slug in slugs:
 p=R/directory/(slug+'.html');s=p.read_text().replace('A complete English rendering of the Chinese essay, preserving its scenes and argument. Full-book spoilers.',notes['en'][0]);p.write_text(s)
r.render(directory,'catch-22')
print('Catch-22: repaired 4 English essays and rendered 25 five-language pages.')
