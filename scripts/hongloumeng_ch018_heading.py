"""Author-approved Chapter 18 heading for the Dazhi reading edition.

The manuscript and archival translation inputs remain unchanged.
"""
from html import escape
import re

# Each pair preserves the reading edition's own names and terminology.
HEADINGS = {
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


def replace_heading(text, lang, count, *, escaped=False):
    old, new = HEADINGS[lang]
    if escaped:
        old, new = tuple(map(escape, old)), tuple(map(escape, new))
    counts = tuple(text.count(part) for part in (*old, *new))
    if counts == (0, 0, count, count):
        return text
    if counts != (count, count, 0, 0):
        raise ValueError(f'Unexpected Chapter 18 heading surfaces in {lang}: {counts}')
    return text.replace(old[0], new[0]).replace(old[1], new[1])


def chapter(text, lang):
    for tag in ('title', 'h1'):
        text, count = re.subn(
            rf'<{tag}\b[^>]*>.*?</{tag}>',
            lambda m: replace_heading(m[0], lang, 1, escaped=True), text, flags=re.S)
        if count != 1:
            raise ValueError(f'Unexpected Chapter 18 {tag} in {lang}: {count}')
    return text


def catalog(text, lang):
    row = re.compile(r'<li\b[^>]*>(?:(?!</li>).)*?href="ch018\.html"(?:(?!</li>).)*?</li>', re.S)
    updated, count = row.subn(
        lambda m: replace_heading(m[0], lang, 2 if lang in ('zh-Hans', 'zh-Hant', 'de', 'es', 'ko') else 1, escaped=True), text)
    if count != 1:
        raise ValueError(f'Unexpected Chapter 18 directory rows in {lang}: {count}')
    return updated


def apply_pages(pages, lang):
    pages['ch018.html'] = chapter(pages['ch018.html'], lang)
    pages['index.html'] = catalog(pages['index.html'], lang)
