"""Metadata for the eight published first-eighty-chapter reading editions."""
import re
LANGUAGES = [('zh-Hans', ''), ('zh-Hant', 'zh-hant/'), ('en', 'en/'), ('ja', 'ja/'), ('fr', 'fr/'), ('de', 'de/'), ('es', 'es/'), ('ko', 'ko/')]
def alternatives(filename):
    tail = '' if filename == 'index.html' else filename
    return ''.join(f'<link rel="alternate" hreflang="{code}" href="https://nondubito.net/classics/hongloumeng/{directory}{tail}">' for code, directory in LANGUAGES + [('x-default', '')])
def apply(source, filename):
    source = re.sub(r'<link\b[^>]*hreflang="[^"]*"[^>]*>', '', source)
    metadata = alternatives(filename)
    marker = '<!-- JAPANESE-NAV:START --><!-- JAPANESE-NAV:END -->'
    head, separator, body = source.partition('</head>')
    if marker in head:
        head = head.replace(marker, '')
        japanese = re.search(r'<link[^>]*hreflang="ja"[^>]*>', metadata).group()
        metadata = metadata.replace(japanese, '') + '<!-- JAPANESE-NAV:START -->' + japanese + '<!-- JAPANESE-NAV:END -->'
    return head + metadata + separator + body
