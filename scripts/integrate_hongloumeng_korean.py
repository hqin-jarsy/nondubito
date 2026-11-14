"""Reversible Korean navigation; never rewrites chapter prose."""
import re
from hongloumeng_korean_availability import korean_publication
START = '<!-- KOREAN-NAV:START -->'
END = '<!-- KOREAN-NAV:END -->'

def addition(relative):
    name = relative.rsplit('/', 1)[1]
    return START + f'<a lang="ko" href="/classics/hongloumeng/ko/{name}">한국어</a>' + END

def transform(relative, text):
    block = addition(relative)
    if START in text or END in text:
        if text.count(block) != 1 or text.count(START) != 1 or text.count(END) != 1:
            raise ValueError('Malformed Korean navigation')
        text = text.replace(block, '', 1)
    pattern = r'(<nav\b[^>]*(?:class="language-switch"|aria-label="Langues?")[^>]*>)(.*?)(</nav>)'
    def insert(match):
        contents = match[2]
        # Keep every older bounded insertion intact, including Japanese's
        # closing-nav anchor and the German-before-French ordering.
        anchors = [m for m in ('<!-- SPANISH-NAV:START -->', '<!-- GERMAN-NAV:START -->', '<!-- FRENCH-NAV:START -->', '<!-- JAPANESE-NAV:START -->') if m in contents]
        if anchors:
            anchor = min(anchors, key=contents.index)
            contents = contents.replace(anchor, block + anchor, 1)
        else:
            contents += block
        return match[1] + contents + match[3]
    result, count = re.subn(pattern, insert, text, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Missing language navigation: ' + relative)
    return result

def reverse(relative, text):
    block = addition(relative)
    if text.count(block) != 1:
        raise ValueError('Missing Korean navigation')
    return text.replace(block, '', 1)

def navigation_outputs(prefix, pages):
    publication = korean_publication()
    if publication is None:
        return pages
    names = {p.name for p in publication['paths']}
    return {name: transform(prefix + name, value) if name in names else value for name, value in pages.items()}
