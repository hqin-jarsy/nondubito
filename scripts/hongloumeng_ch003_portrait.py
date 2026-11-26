"""Apply Han Qin's approved character in Daiyu's Chapter 3 portrait."""

PHRASES = {
    'zh-Hans': ('两弯似蹙非蹙笼烟眉，一双似喜非喜含露目',
                '两弯似蹙非蹙罥烟眉，一双似喜非喜含露目'),
    'zh-Hant': ('兩彎似蹙非蹙籠煙眉，一雙似喜非喜含露目',
                '兩彎似蹙非蹙罥煙眉，一雙似喜非喜含露目'),
}


def apply(text, language):
    old, new = PHRASES[language]
    if (text.count(old), text.count(new)) == (0, 1):
        return text
    if (text.count(old), text.count(new)) != (1, 0):
        raise ValueError(f'Chapter 3 portrait does not match in {language}')
    return text.replace(old, new, 1)
