"""Apply the author-approved Chapter 62 birthday roll call to reader editions."""

PHRASES = {
    'zh-Hans': (
        '过了灯节，就是老太太和宝姐姐，他们娘儿两个遇的巧。三月初一日是太太，',
        '过了灯节，就是太太和宝姐姐，他们娘儿两个遇的巧。三月初一日是大太太，',
    ),
    'zh-Hant': (
        '過了燈節，就是老太太和寶姐姐，他們娘兒兩個遇的巧。三月初一日是太太，',
        '過了燈節，就是太太和寶姐姐，他們娘兒兩個遇的巧。三月初一日是大太太，',
    ),
    'en': (
        'After the Lantern Festival come Grandmother’s and Cousin Bao’s: a happy coincidence for the two of them, old and young. Mother’s is the first of the third month,',
        'After the Lantern Festival come Mother’s and Cousin Bao’s: a happy coincidence for aunt and niece. Lady Xing’s is the first of the third month,',
    ),
    'fr': (
        'Après la fête des Lanternes viennent l’Aïeule et Grande Sœur Joyau : elles se suivent heureusement, ces deux-là. Le premier du troisième mois, c’est Madame ;',
        'Après la fête des Lanternes viennent les anniversaires de Madame et de Grande Sœur Joyau : quel heureux hasard pour la tante et la nièce ! Le premier du troisième mois, c’est Madame Xing ;',
    ),
    'de': (
        'Nach dem Laternenfest kommen die Alte Fürstin und Schwester Pao. Die beiden treffen es ebenfalls glücklich. Am ersten Tag des dritten Monats hat die gnädige Frau Geburtstag,',
        'Nach dem Laternenfest sind die gnädige Frau und Schwester Pao an der Reihe. Wie sich das trifft: Tante und Nichte haben fast zur selben Zeit Geburtstag. Am ersten Tag des dritten Monats hat Frau Xing Geburtstag,',
    ),
    'es': (
        'Pasada la Fiesta de los Faroles vienen los de la Anciana Dama y la hermana Bao. ¡Qué casualidad la de esas dos, de dos generaciones distintas! El primero del tercer mes es el de la señora,',
        'Pasada la Fiesta de los Faroles vienen los de la señora y la hermana Bao. ¡Qué casualidad que tía y sobrina los tengan tan seguidos! El primero del tercer mes es el de la señora Xing,',
    ),
    'ja': (
        '灯節が過ぎると大奥さまと宝釵姉さんで、あのお二人も巧く重なっている。三月一日は奥さま、',
        '灯節が過ぎると奥さまと宝釵姉さん。叔母と姪で、誕生日が近いなんて面白いわね。三月一日は邢夫人、',
    ),
    'ko': (
        '등불 명절이 지나면 할머님과 보 언니 생일이야. 그 두 분도 참 절묘하게 겹쳤지. 삼월 초하루는 마님,',
        '등불 명절이 지나면 마님과 보 언니 생일이야. 이모와 조카가 생일도 참 가깝지. 삼월 초하루는 형부인,',
    ),
}


def apply(text, language):
    old, new = PHRASES[language]
    counts = text.count(old), text.count(new)
    if counts == (0, 1):
        return text
    if counts != (1, 0):
        raise ValueError(f'Chapter 62 birthday phrase mismatch in {language}: {counts}')
    return text.replace(old, new, 1)
