"""Han Qin's one-child reading: Dajie before the naming, Qiaojie after it."""

EDITS = {
    27: {
        'zh-Hans': (('凤姐等并巧姐、大姐、香菱', '凤姐等并大姐、香菱'),),
        'zh-Hant': (('鳳姐等並巧姐、大姐、香菱', '鳳姐等並大姐、香菱'),),
        'en': (
            ('with Qiao-jie, Da-jie, Caltrop', 'with Da-jie, Caltrop'),
            ('The Chinese text lists both Qiao-jie and Da-jie. Both names are retained without deciding whether they refer to separate children.',
             'The source lists both Qiao-jie and Da-jie here. This edition treats them as the same girl and uses Da-jie until Grannie Liu names her in Chapter 42.'),
        ),
        'fr': (
            ('avec Qiaojie, Dajie, Parfum', 'avec Dajie, Parfum'),
            ('La liste du début conserve Qiaojie et Dajie côte à côte, comme le texte chinois édité du projet.',
             'Le texte de base mentionne Qiaojie et Dajie dans la liste du début. Cette édition y reconnaît une seule enfant, appelée Dajie jusqu’à ce que grand-mère Liu lui donne un nom au chapitre 42.'),
        ),
        'de': (('mit Qiaojie, Dajie, Xiangling', 'mit Dajie, Xiangling'),),
        'es': (('con Qiaojie, Dajie, Xiangling', 'con Dajie, Xiangling'),),
        'ja': (('鳳姐たちは、巧姐、大姐、香菱や侍女', '鳳姐たちは、大姐、香菱や侍女'),),
        'ko': (('희봉을 비롯하여 교저와 대저, 향릉', '희봉을 비롯하여 대저, 향릉'),),
    },
    29: {
        'zh-Hans': (('奶子抱着大姐儿带着巧姐儿另在一车', '奶子抱着大姐儿另在一车'),),
        'zh-Hant': (('奶子抱著大姐兒帶著巧姐兒另在一車', '奶子抱著大姐兒另在一車'),),
        'en': (('The wet-nurse, holding Da-jie and bringing Qiao-jie along,',
                'The wet-nurse, holding Da-jie in her arms,'),),
        'fr': (
            ('tenait Dajie dans ses bras et emmenait Qiaojie, avec', 'tenait Dajie dans ses bras, avec'),
            ('Dajie et Qiaojie sont conservées côte à côte dans la liste du cortège, comme dans le texte chinois édité du projet.',
             'Dans le texte de base, la nourrice porte Dajie et emmène Qiaojie. Cette édition ne retient qu’une enfant, Dajie, qui n’a pas encore reçu son nom.'),
        ),
        'de': (("mit Dajie'er auf dem Arm und Qiaojie'er bei sich in einem eigenen Wagen",
                "mit Dajie'er auf dem Arm in einem eigenen Wagen"),),
        'es': (('con Dajie en brazos y Qiaojie a su lado, acompañada', 'con Dajie en brazos, acompañada'),),
        'ja': (('乳母は大姐児を抱き、巧姐児を連れて、別の車に乗り', '乳母は大姐児を抱いて別の車に乗り'),),
        'ko': (('유모는 대저를 안고 교저를 데리고 따로 한 수레에 탔으며', '유모는 대저를 안고 따로 한 수레에 탔으며'),),
    },
    42: {
        'zh-Hans': (('奶子抱了大姐儿出来', '奶子抱了巧姐儿出来'),
                    ('左手托着大姐儿的手', '左手托着巧姐儿的手')),
        'zh-Hant': (('奶子抱了大姐兒出來', '奶子抱了巧姐兒出來'),
                    ('左手托著大姐兒的手', '左手托著巧姐兒的手')),
        'en': (('the wet-nurse appeared carrying Da-jie.', 'the wet-nurse appeared carrying Qiao-jie.'),),
        'de': (('als die Amme mit Dajie im Arm kam', 'als die Amme mit Qiaojie im Arm kam'),),
        'es': (('la nodriza salió con Dajie en brazos', 'la nodriza salió con Qiaojie en brazos'),
               ('Sin sacar a Dajie de los brazos de la nodriza', 'Sin sacar a Qiaojie de los brazos de la nodriza')),
        'ko': (('막 작별하려는데 유모가 큰아기를 안고 와서', '막 작별하려는데 유모가 교저아를 안고 와서'),),
    },
}


def apply(text, chapter, language):
    for old, new in EDITS.get(chapter, {}).get(language, ()):
        counts = text.count(old), text.count(new)
        if counts == (0, 1):
            continue
        if counts != (1, 0):
            raise ValueError(f'Qiaojie name mismatch in Chapter {chapter} ({language}): {old!r}, {counts!r}')
        text = text.replace(old, new, 1)
    return text
