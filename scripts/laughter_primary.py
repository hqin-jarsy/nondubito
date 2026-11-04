"""Reversible controls only: leave the original three-mode reader intact."""
import re


def strip_additions(text):
    for kind in ('LINKS', 'HEAD'):
        text = re.sub(r'<!-- LAUGHTER LANGUAGE ' + kind + r' START -->.*?<!-- LAUGHTER LANGUAGE '
                      + kind + r' END -->', '', text, flags=re.S)
    return text


def upgrade(text, spec, slug):
    from full_series_languages import LABELS, alternatives
    text = strip_additions(text)
    assert "var requested=new URLSearchParams(location.search).get('lang');" in text
    links = ''.join('<span class="lang-sep">|</span><a class="lang-btn" href="'
                    + code + '/' + slug + '.html" lang="' + code + '">' + LABELS[code] + '</a>'
                    for code in spec['languages'])
    text, count = re.subn(r'(<div class="lang-toggle"[^>]*>)(.*?)(</div>)',
                         lambda m: m[1] + m[2] + '<!-- LAUGHTER LANGUAGE LINKS START -->'
                         + links + '<!-- LAUGHTER LANGUAGE LINKS END -->' + m[3], text, flags=re.S)
    assert count == 1
    head = alternatives(spec, slug) + '<script defer src="../../language-select.js?v=20261103"></script>'
    head += '<style>body .lang-toggle.lang-select-menu{display:inline-flex;width:max-content;max-width:100%;}</style>'
    # Keep explicit same-essay query state in step with the existing inline mode.
    head += '''<script>document.addEventListener('change',function(event){var select=event.target;if(!select.matches('.lang-select'))return;var option=select.options[select.selectedIndex];var lang=option&&option.dataset.inlineLanguage;if(!lang)return;var url=new URL(location.href);url.searchParams.set('lang',lang);history.replaceState(null,'',url);localStorage.setItem('nondubito-lang',lang);});</script>'''
    return text.replace('</head>', '<!-- LAUGHTER LANGUAGE HEAD START -->' + head
                        + '<!-- LAUGHTER LANGUAGE HEAD END --></head>', 1)
