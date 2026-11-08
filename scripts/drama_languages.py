"""Eight-language labels for the complete drama collection."""
LANGS=('en','zh','zh-hant','de','fr','es','ja','ko')
NATIVE={'zh':'zh-Hans','zh-hant':'zh-Hant',**{x:x for x in LANGS if not x.startswith('zh')}}
CSS={x:('hant' if x=='zh-hant' else x) for x in LANGS}
LABELS={'en':'English','zh':'简体中文','zh-hant':'繁體中文','de':'Deutsch','fr':'Français','es':'Español','ja':'日本語','ko':'한국어'}
# Keys are the existing English UI text. Chinese and English article prose are not altered.
UI={}
def row(key,de,fr,es,ja,ko):UI[key]=dict(zip(('de','fr','es','ja','ko'),(de,fr,es,ja,ko)))
row('Structures in Drama','Strukturen im Drama','Les structures dans le théâtre','Estructuras en el teatro','戯曲の中の構造','희곡 속의 구조')
row('Stories and Structures','Geschichten und Strukturen','Histoires et structures','Historias y estructuras','物語の中の構造','이야기 속의 구조')
row('Closeness & choice','Nähe und Entscheidung','Proximité et choix','Cercanía y elección','親密さと選択','친밀함과 선택')
row('Who gets to be heard?','Wer wird gehört?','Qui peut se faire entendre ?','¿Quién consigue ser escuchado?','誰が最後まで話せるのか','누가 끝까지 말할 수 있는가')
row('Who tells my story?','Wer erzählt meine Geschichte?','Qui raconte mon histoire ?','¿Quién cuenta mi historia?','私の物語を語るのは誰か','누가 내 이야기를 하는가')
row('Care & its costs','Fürsorge und ihre Kosten','L’aide et son prix','La ayuda y su precio','助けることとその代償','도움과 그 대가')
row('What reconciliation leaves open','Was nach der Versöhnung offenbleibt','Ce que la réconciliation laisse ouvert','Lo que la reconciliación deja abierto','和解のあとも、生活は続く','화해 뒤에도 삶은 계속된다')
row('Library','Bibliothek','Bibliothèque','Biblioteca','書架','서가')
row('Start Here','Hier beginnen','Commencer ici','Empieza aquí','ここから読む','여기서 시작')
row('Explore','Entdecken','Explorer','Explorar','探す','둘러보기')
row('Latest','Neuigkeiten','Nouveautés','Novedades','最近の更新','최근 업데이트')
row('About','Über uns','À propos','Acerca de','このサイトについて','소개')
row('Search','Suchen','Rechercher','Buscar','検索','검색')
row('Menu','Menü','Menu','Menú','メニュー','메뉴')
row('SAE Theory ↗','SAE-Theorie ↗','Théorie SAE ↗','Teoría SAE ↗','SAE 理論 ↗','SAE 이론 ↗')
row('Read essay →','Essay lesen →','Lire l’essai →','Leer el ensayo →','全文を読む →','전문 읽기 →')
row('Text & sources','Text und Quellen','Texte et sources','Texto y fuentes','テキストと出典','텍스트와 출처')
row('Previous essay','Voriger Essay','Essai précédent','Ensayo anterior','前の篇','이전 글')
row('Next essay','Nächster Essay','Essai suivant','Ensayo siguiente','次の篇','다음 글')
row('All twenty-three readings','Alle 23 Lektüren','Les vingt-trois lectures','Las veintitrés lecturas','全23篇','전체 23편')
row('Further reading','Weiterlesen','Pour poursuivre la lecture','Para seguir leyendo','続きを読む','더 읽기')
row('Five minutes to understand Non Dubito','Non Dubito in fünf Minuten','Comprendre Non Dubito en cinq minutes','Comprender Non Dubito en cinco minutos','5分でわかる Non Dubito','5분 만에 이해하는 Non Dubito')
row('← More stories and structures','← Weitere Geschichten und Strukturen','← Autres histoires et structures','← Más historias y estructuras','←「物語の中の構造」に戻る','← 이야기 속의 구조로 돌아가기')
row('These readings discuss key scenes and endings. They read the plays, not particular stage or screen productions.','Diese Lektüren besprechen Schlüsselszenen und Schlusswendungen. Ihr Gegenstand sind die Dramentexte, nicht einzelne Bühneninszenierungen oder Verfilmungen.','Ces lectures abordent des scènes clés et les dénouements. Elles portent sur les textes des pièces, non sur des mises en scène ou des adaptations à l’écran particulières.','Estas lecturas comentan escenas clave y desenlaces. Su objeto son los textos dramáticos, no montajes teatrales ni adaptaciones audiovisuales concretos.','本シリーズは重要な場面と結末に触れます。対象は戯曲のテキストであり、特定の舞台上演や映像化作品ではありません。','이 글들은 주요 장면과 결말을 다룹니다. 특정 무대 공연이나 영상 각색이 아니라 희곡 텍스트를 읽습니다.')
row('A door closes. A child is taken into someone’s arms. A letter waits to be sent. Twenty-three readings stay with the moments when care, judgment, and reconciliation still need another person’s answer.','Eine Tür fällt zu. Ein Kind wird in die Arme genommen. Ein Brief wartet darauf, abgeschickt zu werden. Dreiundzwanzig Lektüren gehen von solchen kleinen Gesten aus und fragen, warum Fürsorge, Urteil und Versöhnung noch immer auf die Antwort eines anderen Menschen warten müssen.','Une porte se ferme. Un enfant est pris dans les bras. Une lettre attend d’être envoyée. Vingt-trois lectures entrent dans le théâtre par ces petits gestes, pour voir pourquoi le soin, le jugement et la réconciliation doivent encore attendre la réponse d’autrui.','Una puerta se cierra. Alguien toma a un niño en brazos. Una carta espera a ser enviada. Veintitrés lecturas entran en el teatro por esos pequeños gestos para observar por qué el cuidado, el juicio y la reconciliación todavía necesitan la respuesta de otra persona.','扉が閉まり、子どもが腕に抱かれ、まだ出されていない手紙がある。23篇の文章が、こうした小さな動作から戯曲に入り、気遣いも判断も和解も、なぜなお相手の返事を待たなければならないのかを考えます。','문이 닫히고, 아이가 누군가의 품에 안기고, 편지는 아직 보내지지 않았다. 스물세 편의 글은 이런 작은 동작에서 희곡으로 들어가 돌봄과 판단, 화해가 왜 여전히 다른 사람의 답을 기다려야 하는지 살펴본다.')
row('Stories and Structures / 05','Geschichten und Strukturen / 05','Histoires et structures / 05','Historias y estructuras / 05','物語の中の構造 / 05','이야기 속의 구조 / 05')
row('23 essays · 8 languages','23 Essays · 8 Sprachen','23 essais · 8 langues','23 ensayos · 8 idiomas','全23篇・8言語','23편 · 8개 언어')
for n in (3,4,5):row(f'{n} essays',f'{n} Essays',f'{n} essais',f'{n} ensayos',f'{n}篇',f'{n}편')

def foreign_ui(key):
    """Also support explicit local previews with fewer than all 23 essays."""
    if key in UI:return UI[key]
    import re
    match=re.fullmatch(r'(\d+) essays',key)
    if match:
        n=int(match[1]);return dict(zip(('de','fr','es','ja','ko'),(f'{n} Essay'+('s' if n!=1 else ''),f'{n} essai'+('s' if n!=1 else ''),f'{n} ensayo'+('s' if n!=1 else ''),f'{n}篇',f'{n}편')))
    match=re.fullmatch(r'(\d+) essays · 8 languages',key)
    if match:
        n=match[1];return dict(zip(('de','fr','es','ja','ko'),(f'{n} Essays · 8 Sprachen',f'{n} essais · 8 langues',f'{n} ensayos · 8 idiomas',f'{n}篇・8言語',f'{n}편 · 8개 언어')))
    match=re.fullmatch(r'(\d+) completed readings from the forthcoming collection\.',key)
    if match:
        n=match[1];return dict(zip(('de','fr','es','ja','ko'),(f'{n} fertige Lektüren aus der kommenden Sammlung.',f'{n} lectures achevées de la collection à venir.',f'{n} lecturas completas de la próxima colección.',f'制作中のシリーズから、完成した{n}篇。',f'제작 중인 시리즈에서 완성된 {n}편.')))
    return None
