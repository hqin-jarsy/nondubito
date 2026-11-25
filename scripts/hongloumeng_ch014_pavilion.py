"""Han Qin's Chapter 14 correction: remove the duplicated 王府 in the pavilion list."""

PHRASES = {
    'zh-Hans': ('第一座是王府东平王府祭棚', '第一座是东平王府祭棚'),
    'zh-Hant': ('第一座是王府東平王府祭棚', '第一座是東平王府祭棚'),
}


def apply(html, language):
    old, new = PHRASES[language]
    counts = html.count(old), html.count(new)
    if counts == (0, 1):
        return html
    if counts != (1, 0):
        raise ValueError(f'Chapter 14 pavilion does not match in {language}: {counts}')
    return html.replace(old, new, 1)
