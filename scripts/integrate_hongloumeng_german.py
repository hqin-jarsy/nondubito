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
        if text.count(block)==text.count(START)==text.count(END)==1:return text
        raise ValueError('Malformed German navigation')
    pattern=r'(<nav\b[^>]*(?:class="language-switch"|aria-label="Langues?")[^>]*>)(.*?)(</nav>)'
    result,count=re.subn(pattern,lambda m:m[1]+m[2]+block+m[3],text,count=1,flags=re.S)
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
