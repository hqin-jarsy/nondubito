"""Reversible German links for the currently reviewed chapter batches."""
import re
from hongloumeng_german_availability import german_publication
START='<!-- GERMAN-NAV:START -->'
END='<!-- GERMAN-NAV:END -->'

def addition(relative):
    name=relative.rsplit('/',1)[1]
    return START+f'<a lang="de" href="/classics/hongloumeng/de/{name}">Deutsch</a>'+END

def transform(relative,text):
    block=addition(relative)
    if START in text or END in text:
        if text.count(block)!=1 or text.count(START)!=1 or text.count(END)!=1:
            raise ValueError('Malformed German navigation')
        # Normalize earlier insertions without changing any non-German bytes.
        text=text.replace(block,'',1)
    pattern=r'(<nav\b[^>]*(?:class="language-switch"|aria-label="Langues?")[^>]*>)(.*?)(</nav>)'
    def insert(match):
        contents=match[2]
        # French regeneration inserts immediately before Japanese. Keep both
        # older bounded insertions and Japanese's closing-nav anchor intact.
        anchor=None
        if '<!-- JAPANESE-NAV:START -->' in contents:
            anchor=('<!-- FRENCH-NAV:START -->' if '<!-- FRENCH-NAV:START -->' in contents
                    else '<!-- JAPANESE-NAV:START -->')
        contents=contents.replace(anchor,block+anchor,1) if anchor else contents+block
        return match[1]+contents+match[3]
    result,count=re.subn(pattern,insert,text,count=1,flags=re.S)
    if count!=1:raise ValueError('Missing language navigation: '+relative)
    return result

def reverse(relative,text):
    block=addition(relative)
    if text.count(block)!=1:raise ValueError('Missing German navigation')
    return text.replace(block,'',1)

def navigation_outputs(prefix,pages):
    publication=german_publication()
    if publication is None:return pages
    names={p.name for p in publication['paths']}
    return {name:transform(prefix+name,value) if name in names else value for name,value in pages.items()}
