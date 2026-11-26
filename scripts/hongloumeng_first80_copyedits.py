"""Han Qin's approved first-80 copyedits for the public reading editions.

The frozen source and its translation bindings remain unchanged. Each edit
is scoped to one reviewed passage and refuses ambiguous matches.
"""

import re

P = '</p><p class="prose">'
Q = '&quot;'
ZH_EDITS = (
    (2, '不能知也。&quot;子兴', '不能知也。&quot;子興', '不能知也。”子兴', '不能知也。”子興'),
    (6, '作官的朋友，做官的朋友，', '作官的朋友，做官的朋友，', '作官的朋友，', '作官的朋友，'),
    (8, '狼犺蠢大之物等语之谤', '狼犺蠢大之物等語之謗', '狼犺蠢大之物”等语之谤', '狼犺蠢大之物”等語之謗'),
    (16, '贾琏点头道：”这个主意好。“凤姐', '賈璉點頭道：”這個主意好。“鳳姐',
     '贾琏点头道：“这个主意好。”凤姐', '賈璉點頭道：“這個主意好。”鳳姐'),
    (18, '“大观园”园之名“有凤来仪”', '“大觀園”園之名“有鳳來儀”',
     '“大观园”园之名。“有凤来仪”', '“大觀園”園之名。“有鳳來儀”'),
    (24, '若要转买，不但卖不出原价来', '若要轉買，不但賣不出原價來',
     '若要转卖，不但卖不出原价来', '若要轉賣，不但賣不出原價來'),
    (25, '耳根底下嘁嘁喳喳喳说了几句话', '耳根底下嘁嘁喳喳喳說了幾句話',
     '耳根底下嘁嘁喳喳的说了几句话', '耳根底下嘁嘁喳喳的說了幾句話'),
    (25, f'只怕就好了。{P}“贾政', f'只怕就好了。{P}“賈政',
     f'只怕就好了。”{P}贾政', f'只怕就好了。”{P}賈政'),
    (25, f'冤孽偿清好散场！{P}”念毕', f'冤孽償清好散場！{P}”念畢',
     f'冤孽偿清好散场！”{P}念毕', f'冤孽償清好散場！”{P}念畢'),
    (51, '快进被来来渥渥罢。', '快進被來來渥渥罷。', '快进被来，来渥渥罢。', '快進被來，來渥渥罷。'),
    (62, '一一挨着，长的房中到过', '一一挨著，長的房中到過',
     '一一挨着所长的房中到过', '一一挨著所長的房中到過'),
    (71, f'也不留你吃茶去。{Q}说毕', f'也不留你吃茶去。{Q}說畢',
     '也不留你吃茶去。”说毕', '也不留你吃茶去。”說畢'),
    (71, f'我听见可不依。{P}{Q}婆子', f'我聽見可不依。{P}{Q}婆子',
     f'我听见可不依。”{P}婆子', f'我聽見可不依。”{P}婆子'),
    (72, f'沏一碗来。{Q}说着向鸳鸯道：{Q}这两日', f'沏一碗來。{Q}說著向鴛鴦道：{Q}這兩日',
     '沏一碗来。”说着向鸳鸯道：“这两日', '沏一碗來。”說著向鴛鴦道：“這兩日'),
    (74, f'跑来作什么？{P}{Q}宝玉', f'跑來作什麼？{P}{Q}寶玉',
     f'跑来作什么？”{P}宝玉', f'跑來作什麼？”{P}寶玉'),
    (74, '我先回过老太太太太，然后', '我先回過老太太太太，然後',
     '我先回过老太太、太太，然后', '我先回過老太太、太太，然後'),
    (80, f'越发蒸臭了。{P}{Q}李贵', f'越發蒸臭了。{P}{Q}李貴',
     f'越发蒸臭了。”{P}李贵', f'越發蒸臭了。”{P}李貴'),
)

# Each bounded local span lists its start/end fragments in both scripts and
# the exact quote glyph sequence to insert, beginning at its first marker.
ZH_SPANS = (
    (22, '这便丢开手不成？', '顽话罢了。', '這便丟開手不成？', '頑話罷了。', '”' + '“”' * 4, 'reversed'),
    (25, '撞客之灾。', '遇见僧道穷苦人好舍。', '撞客之災。', '遇見僧道窮苦人好捨。',
     '”' + '“”' * 8, 'reversed'),
    (25, '不知你们的脾胃是怎样？', '怎么还不给我们家作媳妇？',
     '不知你們的脾胃是怎樣？', '怎麼還不給我們家作媳婦？', '”' + '“”' * 6, 'reversed'),
    (71, '也不过打几下子就完了。', '赵姨娘道：', '也不過打幾下子就完了。', '趙姨娘道：', '”“', 'ascii'),
    (71, '婆子应了方要走时，鸳鸯道：', '他们那里听他的话。', '婆子應了方要走時，鴛鴦道：', '他們那裡聽他的話。', '“”', 'ascii'),
    (74, '宝玉不便说出讨情一事，只说：', '来看二姐姐。', '寶玉不便說出討情一事，只說：', '來看二姐姐。', '“”', 'ascii'),
    (74, '那王住儿媳妇紧跟在后，口内百般央求，只说：', '赶晚不来，可别怨我。',
     '那王住兒媳婦緊跟在後，口內百般央求，只說：', '趕晚不來，可別怨我。', '“”' * 4, 'ascii'),
    (77, '如丧魂魄一般，因忙拦住问道：', '那里去？', '如喪魂魄一般，因忙攔住問道：', '那裡去？', '“”', 'ascii'),
    (77, '司棋见了宝玉，因拉住哭道：', '都要去了，这却怎么的好。', '司棋見了寶玉，因拉住哭道：',
     '都要去了，這卻怎麼的好。', '“”' * 2, 'ascii'),
    (80, '金桂亦颇觉察其意，想着：', '那时宝蟾原是我的人，也就好处了。',
     '金桂亦頗覺察其意，想著：', '那時寶蟾原是我的人，也就好處了。', '“”', 'ascii'),
    (80, '看人听见笑话。', '该挤发我了！', '看人聽見笑話。', '該擠發我了！', '”“”', 'ascii'),
    (80, '倒有一种病可也贴的好么？', '宝玉命李贵等：',
     '倒有一種病可也貼的好麼？', '寶玉命李貴等：', '”“' * 4, 'ascii'),
)

TRANSLATIONS = {
    'en': ('no friends in office, no friends in office.', 'no friends in office.'),
    'ja': ('お役人の友達も、お役人の友達もいない', 'お役人の友達もいない'),
    'es': ('ni amigos con cargo, ni amigos que sean funcionarios.', 'ni amigos con cargo.'),
    'ko': ('벼슬하는 친구도, 관리 친구도 없는데', '벼슬하는 친구도 없는데'),
}

CHAPTERS = frozenset(n for n, *_ in ZH_EDITS + ZH_SPANS)


def _replace(text, old, new):
    if text.count(old) == 1:
        return text.replace(old, new, 1)
    if old not in text and text.count(new) == 1:
        return text
    raise ValueError(f'Copyedit anchor does not match uniquely: {old!r}')


def _quotes(text, start, end, expected, kind):
    if text.count(start) != 1:
        raise ValueError(f'Copyedit start does not match uniquely: {start!r}')
    left = text.index(start) + len(start)
    right = text.index(end, left) + len(end)
    # Ignore ASCII double quotes in tags. The rendered ASCII prose marks
    # are HTML entities, distinct from those in tag attribute delimiters.
    pattern = re.compile(r'&quot;|[“”]')
    match = pattern.match(text, right)
    if not match:
        raise ValueError(f'Expected a quote at the end of {end!r}')
    right = match.end()
    span = text[left:right]
    actual = ''.join(pattern.findall(span))
    if actual == expected:
        return text
    old = Q * len(expected) if kind == 'ascii' else expected.translate(str.maketrans('“”', '”“'))
    if actual != old:
        raise ValueError(f'Unexpected quote sequence at {start!r}: {actual!r}')
    replacements = iter(expected)
    return text[:left] + pattern.sub(lambda _: next(replacements), span) + text[right:]


def apply(text, chapter, language):
    if language in TRANSLATIONS:
        return _replace(text, *TRANSLATIONS[language]) if chapter == 6 else text
    index = ('zh-Hans', 'zh-Hant').index(language)
    for n, *phrases in ZH_EDITS:
        if n == chapter:
            text = _replace(text, phrases[index], phrases[index + 2])
    if chapter == 72:
        text = _replace(text, '`求人不如求己&#x27;', '‘求人不如求己’')
    for n, start_s, end_s, start_t, end_t, marks, kind in ZH_SPANS:
        if n == chapter:
            start, end = (start_s, end_s) if index == 0 else (start_t, end_t)
            text = _quotes(text, start, end, marks, kind)
    return text
