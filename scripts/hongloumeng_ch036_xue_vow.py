"""Chapter 36 reader correction: Aunt Xue fulfills a vow for Bao-yu."""

PHRASES = {
    'zh-Hans': ('我才在舅母跟前听的明儿是薛姨妈的生日，叫我顺便来问你出去不出去。',
                '我才在舅母跟前听的，薛姨妈为你的伤许了愿，明儿还愿，叫我顺便来问你出去不出去。'),
    'zh-Hant': ('我才在舅母跟前聽的明兒是薛姨媽的生日，叫我順便來問你出去不出去。',
                '我才在舅母跟前聽的，薛姨媽為你的傷許了願，明兒還願，叫我順便來問你出去不出去。'),
    'en': ('I’ve just heard from Aunt Wang that tomorrow is Aunt Xue’s birthday,',
           'I’ve just heard from Aunt Wang that Aunt Xue made a vow for your recovery and is going to fulfil it tomorrow,'),
    'fr': ('Je viens d’entendre chez ma tante que demain est l’anniversaire de tante Xue.',
           'Je viens d’apprendre chez ma tante que tante Xue a fait un vœu pour ta guérison et qu’elle va l’accomplir demain.'),
    'de': ('Eben habe ich bei unserer Tante gehört, dass morgen Tante Xue Geburtstag hat.',
           'Eben habe ich bei unserer Tante gehört, dass Tante Xue für deine Genesung ein Gelübde abgelegt hat und es morgen erfüllen will.'),
    'es': ('Acabo de oír en los aposentos de mi tía que mañana es el cumpleaños de la tía Xue.',
           'Acabo de oír en los aposentos de mi tía que la tía Xue hizo una promesa por tu curación y que mañana va a cumplirla.'),
    'ja': ('さっき伯母さまのところで、明日は薛の叔母さまのお誕生日だと聞いたわ。',
           'さっき伯母さまのところで聞いたのだけれど、薛の叔母さまがあなたの傷が治るように願をかけてくださって、明日はその願ほどきだそうよ。'),
    'ko': ('방금 외숙모께 들었는데 내일이 설 이모 생신이래.',
           '방금 외숙모께 들었는데, 설 이모가 네 상처가 낫기를 빌며 서원하셨고 내일 그때 하신 약속을 지키신대.'),
}


def apply(text, language):
    old, new = PHRASES[language]
    counts = text.count(old), text.count(new)
    if counts == (0, 1):
        return text
    if counts != (1, 0):
        raise ValueError(f'Chapter 36 Aunt Xue passage mismatch in {language}: {counts}')
    return text.replace(old, new, 1)
