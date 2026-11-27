"""Author-approved chapter headings for the Dazhi reading edition.

The manuscript and archival translation inputs remain unchanged.
"""
from html import escape
import re

# Each pair preserves the reading edition's own names and terminology.
HEADINGS_18 = {
    'zh-Hans': (
        ('皇恩重元妃省父母', '天伦乐宝玉呈才藻'),
        ('林黛玉误剪香囊袋', '贾元春强笑辞骨肉'),
    ),
    'zh-Hant': (
        ('皇恩重元妃省父母', '天倫樂寶玉呈才藻'),
        ('林黛玉誤剪香囊袋', '賈元春強笑辭骨肉'),
    ),
    'en': (
        ('Imperial grace allows Consort Yuan to visit her parents',
         'Amid the joys of family reunion, Bao-yu presents his verse'),
        ('Mistaken in her suspicions, Lin Dai-yu cuts the scent-bag',
         'Jia Yuan-chun forces a smile as she parts from her family'),
    ),
    'de': (
        ('Aus großer kaiserlicher Gnade besucht die Gemahlin Yuan ihre Eltern',
         'im Familienglück zeigt Pao Yü seine dichterische Kunst'),
        ('Lin Blaujuwel verkennt die Lage und zerschneidet den Duftbeutel',
         'Jia Yuanchun zwingt sich beim Abschied von den Ihren zu einem Lächeln'),
    ),
    'es': (
        ('Por la profunda gracia imperial, la consorte Yuan visita a sus padres',
         'en la dicha familiar, Baoyu muestra su talento literario'),
        ('Lin Daiyu corta el saquito de perfume por un malentendido',
         'Jia Yuanchun se despide de los suyos forzando una sonrisa'),
    ),
    'fr': (
        ('Par grâce impériale, Première-née rend visite à ses parents',
         'dans la joie familiale, Jade magique présente ses talents littéraires'),
        ('Lin Jade sombre se méprend et coupe le sachet de parfum',
         'Printemps Première-née se force à sourire en quittant les siens'),
    ),
    'ja': (
        ('皇恩厚く元妃は父母を訪ね', '親子の楽しみに宝玉は詩才を示す'),
        ('林黛玉、早合点して香袋に鋏を入れ', '賈元春、無理に笑みを作り身内に別れを告げる'),
    ),
    'ko': (
        ('황은이 두터워 원비가 부모를 찾아뵙고', '천륜의 즐거움 속에 보옥이 재주를 보이다'),
        ('임대옥은 오해 끝에 향낭을 잘라 버리고', '가원춘은 억지로 웃으며 가족과 작별하다'),
    ),
}


HEADINGS_64 = {
    'zh-Hans': (
        ('幽淑女悲题五美吟', '浪荡子情遗九龙珮'),
        ('潇湘女翻案咏五美', '浪荡子暗系九龙珮'),
    ),
    'zh-Hant': (
        ('幽淑女悲題五美吟', '浪蕩子情遺九龍珮'),
        ('瀟湘女翻案詠五美', '浪蕩子暗繫九龍珮'),
    ),
    'en': (
        ('A secluded maiden writes her grief in Songs of Five Beauties',
         'A libertine pledges love with a nine-dragon pendant'),
        ('The Naiad overturns old judgments in her Songs of Five Beauties',
         'A libertine secretly ties a nine-dragon jade pendant to a handkerchief'),
    ),
    'de': (
        ('Die stille, edle Jungfrau dichtet traurig über fünf Schönheiten',
         'der Wüstling verschenkt aus Verlangen einen Neundrachen-Anhänger'),
        ('Die junge Frau vom Xiaoxiang-Gehöft besingt fünf Schönheiten und verwirft alte Urteile',
         'der Wüstling bindet heimlich einen Jadeanhänger mit neun Drachen ans Tuch'),
    ),
    'es': (
        ('Una doncella recatada vierte su tristeza en los Cantos de las cinco bellezas',
         'Un libertino entrega, en prenda de amor, un colgante de nueve dragones'),
        ('La joven de Xiaoxiang canta a cinco bellezas y rebate los juicios de antaño',
         'Un libertino ata a escondidas al pañuelo un colgante de jade con nueve dragones'),
    ),
    'fr': (
        ('Une jeune femme retirée chante avec tristesse les Cinq Beautés',
         'un libertin offre en gage d’amour un pendant aux Neuf Dragons'),
        ('La demoiselle de Xiaoxiang renverse les jugements d’autrefois en chantant les Cinq Beautés',
         'un libertin noue en cachette au mouchoir un pendentif de jade aux neuf dragons'),
    ),
    'ja': (
        ('奥ゆかしき乙女は悲しみを五美吟に託し', '放蕩の男は九竜の佩玉に思いを贈る'),
        ('瀟湘の乙女は五美を詠んで古説を覆し', '放蕩者はひそかに九竜の佩玉を手巾に結ぶ'),
    ),
    'ko': (
        ('그윽한 숙녀는 슬피 오미음을 짓고', '방탕한 사내는 정을 담아 구룡패를 주다'),
        ('소상관의 처녀는 다섯 미인을 읊어 옛 평을 뒤집고', '방탕한 사내는 몰래 손수건에 구룡패를 묶다'),
    ),
}

# Chapter 67 retains its first half in every edition.
HEADINGS_67 = {
    'zh-Hans': ('闻秘事凤姐讯家童', '闻秘事凤姐问新房'),
    'zh-Hant': ('聞秘事鳳姐訊家童', '聞秘事鳳姐問新房'),
    'en': (
        'On hearing a secret, Xi-feng questions a household page',
        'On hearing a secret, Xi-feng asks where the bridal quarters are',
    ),
    'de': (
        'Ein Geheimnis dringt zu Phönix, und sie verhört die Dienerburschen',
        'Ein Geheimnis dringt zu Phönix, und sie fragt, wo das Haus für die neue Frau liegt',
    ),
    'es': (
        'Al enterarse de un secreto, Xifeng interroga a un criado',
        'Al enterarse de un secreto, Xifeng pregunta dónde está la casa de los recién casados',
    ),
    'fr': (
        'informée d’un secret, Phénix interroge un domestique',
        'informée d’un secret, Phénix demande où se trouve le logis des nouveaux mariés',
    ),
    'ja': (
        '秘め事を聞いて鳳姐は家僕を問い詰める',
        '秘め事を聞いて鳳姐は新所帯の家はどこかと問い詰める',
    ),
    'ko': (
        '비밀을 들은 희봉은 집안 종을 심문하다',
        '비밀을 들은 희봉은 신방이 어디인지 캐묻다',
    ),
}

HEADINGS = {18: HEADINGS_18, 64: HEADINGS_64,
            67: {lang: ((old,), (new,)) for lang, (old, new) in HEADINGS_67.items()}}


def replace_heading(text, lang, count, *, number=18, escaped=False):
    old, new = HEADINGS[number][lang]
    if escaped:
        old, new = tuple(map(escape, old)), tuple(map(escape, new))
    counts = tuple(text.count(part) for part in (*old, *new))
    if counts == (0,) * len(old) + (count,) * len(new):
        return text
    if counts != (count,) * len(old) + (0,) * len(new):
        raise ValueError(f'Unexpected Chapter {number} heading surfaces in {lang}: {counts}')
    for before, after in zip(old, new):
        text = text.replace(before, after)
    return text


def chapter(text, lang, number=18):
    for tag in ('title', 'h1'):
        text, count = re.subn(
            rf'<{tag}\b[^>]*>.*?</{tag}>',
            lambda m: replace_heading(m[0], lang, 1, number=number, escaped=True), text, flags=re.S)
        if count != 1:
            raise ValueError(f'Unexpected Chapter {number} {tag} in {lang}: {count}')
    return text


def catalog(text, lang, number=18):
    row = re.compile(rf'<li\b[^>]*>(?:(?!</li>).)*?href="ch{number:03d}\.html"(?:(?!</li>).)*?</li>', re.S)
    updated, count = row.subn(
        lambda m: replace_heading(m[0], lang, 2 if lang in ('zh-Hans', 'zh-Hant', 'de', 'es', 'ko') else 1, number=number, escaped=True), text)
    if count != 1:
        raise ValueError(f'Unexpected Chapter {number} directory rows in {lang}: {count}')
    return updated


def apply_pages(pages, lang):
    for number in HEADINGS:
        filename = f'ch{number:03d}.html'
        pages[filename] = chapter(pages[filename], lang, number)
        pages['index.html'] = catalog(pages['index.html'], lang, number)
