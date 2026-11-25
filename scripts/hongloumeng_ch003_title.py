"""Author-approved title in the Chapter 3 inscription, applied to public text only.

Keep source witnesses and the hash-bound translation inputs intact.
"""

TITLES = {
    'zh-Hans': ('东安郡王穆莳', '东平郡王穆莳'),
    'zh-Hant': ('東安郡王穆蒔', '東平郡王穆蒔'),
    'en': ('hereditary Prince of Dong’an', 'hereditary Prince of Dongping'),
    'ja': ('東安郡王穆蒔', '東平郡王穆蒔'),
    'fr': ('prince de Dong’an', 'prince de la Paix de l’Est'),
    'de': ('Fürst von Dong’an', 'Fürst von Dongping'),
    'es': ('príncipe de Dong’an', 'príncipe de Dongping'),
    'ko': ('동안군왕 목시', '동평군왕 목시'),
}


def apply(text, language):
    old, new = TITLES[language]
    counts = text.count(old), text.count(new)
    if counts == (0, 1):
        return text
    if counts != (1, 0):
        raise ValueError(f'Chapter 3 inscription does not match in {language}: {counts}')
    return text.replace(old, new, 1)


if __name__ == '__main__':
    from pathlib import Path

    reader = Path(__file__).resolve().parents[1] / 'classics/hongloumeng'
    for language in TITLES:
        chapter = reader / ('' if language == 'zh-Hans' else language.lower()) / 'ch003.html'
        body = chapter.read_text(encoding='utf-8')
        if apply(body, language) != body:
            raise SystemExit(f'Chapter 3 title was not updated in {language}')
    print('Checked the Chapter 3 inscription in all eight editions.')
