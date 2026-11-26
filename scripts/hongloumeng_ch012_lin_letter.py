"""Chapter 12 reader correction: the letter arrives in the late eighth month.

Han Qin adopted the reading reported by Wu Xuancheng in 1924
(《小说世界》, 《红楼梦之误字》); the underlying source stays unchanged.
"""

PHRASES = {
    'zh-Hans': ('这年冬底，林如海的书信寄来', '这年八月底，林如海的书信寄来'),
    'zh-Hant': ('這年冬底，林如海的書信寄來', '這年八月底，林如海的書信寄來'),
    'en': ('at the end of that winter, a letter arrived from Lin Ru-hai',
           'at the end of the eighth month of that year, a letter arrived from Lin Ru-hai'),
    'fr': ('à la fin de cet hiver, une lettre arriva de Lin Ruhai',
           'à la fin du huitième mois de cette année-là, une lettre arriva de Lin Ruhai'),
    'de': ('Gegen Ende jenes Winters traf unerwartet ein Brief von Lin Ruhai ein',
           'Gegen Ende des achten Monats jenes Jahres traf unerwartet ein Brief von Lin Ruhai ein'),
    'es': ('a finales de aquel invierno, llegaría una carta de Lin Ruhai',
           'a finales del octavo mes de aquel año, llegaría una carta de Lin Ruhai'),
    'ja': ('この年の冬の終わり、林如海から手紙が届いた',
           'この年の八月末、林如海から手紙が届いた'),
    'ko': ('그해 겨울 끝 무렵 임여해의 편지가 왔다',
           '그해 팔월 말에 임여해의 편지가 왔다'),
}


def apply(text, language):
    old, new = PHRASES[language]
    counts = text.count(old), text.count(new)
    if counts == (0, 1):
        return text
    if counts != (1, 0):
        raise ValueError(f'Chapter 12 letter date mismatch in {language}: {counts}')
    return text.replace(old, new, 1)
