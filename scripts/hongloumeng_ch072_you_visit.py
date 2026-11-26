"""Chapter 72 reader correction: a grave visit, not a death anniversary."""

PHRASES = {
    'zh-Hans': ('后日是尤二姐的周年，我们好了一场', '后日该去瞧瞧尤二姐，我们好了一场'),
    'zh-Hant': ('後日是尤二姐的週年，我們好了一場', '後日該去瞧瞧尤二姐，我們好了一場'),
    'en': ('I was thinking that the day after tomorrow is the first anniversary of You Er-jie’s death.',
           'I was thinking I ought to go and see You Er-jie the day after tomorrow.'),
    'fr': ('Je pensais qu’après-demain serait l’anniversaire de la mort de la deuxième sœur You.',
           'Je pensais qu’il faudrait aller voir la deuxième sœur You après-demain.'),
    'de': ('Übermorgen ist der erste Todestag der Zweiten Schwester You.',
           'Ich dachte, ich sollte übermorgen die Zweite Schwester You besuchen.'),
    'es': ('Estaba pensando que pasado mañana se cumple el primer aniversario de la muerte de You Erjie.',
           'Estaba pensando que pasado mañana debería ir a ver a You Erjie.'),
    'ja': ('明後日は尤二姐の一周忌でしょう。', '明後日は尤二姐に会いに行かなくちゃと思ってね。'),
    'ko': ('모레면 우이저의 첫 제삿날이라 생각하고 있었어요.',
           '모레 우이저를 보러 가야겠다 싶었어요.'),
}


def apply(text, language):
    old, new = PHRASES[language]
    counts = text.count(old), text.count(new)
    if counts == (0, 1):
        return text
    if counts != (1, 0):
        raise ValueError(f'Chapter 72 grave visit mismatch in {language}: {counts}')
    return text.replace(old, new, 1)
