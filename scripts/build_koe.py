#!/usr/bin/env python3
"""Render the KOE artist hub from its public, English content file."""
import json
import re
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
IMAGES = json.loads((ROOT / 'data/koe-image-hosting.json').read_text(encoding='utf-8'))['images']


def image_url(filename):
    return escape(IMAGES[filename]['url'], quote=True)

def copy(value, tag='span', cls=''):
    attribute = f' class="{cls}"' if cls else ''
    return f'<{tag}{attribute}>{escape(value)}</{tag}>'


class EnglishShell(HTMLParser):
    """Keep the shared shell's English text, omitting language selectors."""
    OMIT = {'lang-zh', 'lang-hant', 'site-shell-language', 'site-shell-mobile-languages'}
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.stack = []
        self.parts = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        hidden = bool(self.stack and self.stack[-1]) or bool(self.OMIT.intersection(dict(attrs).get('class', '').split()))
        if not hidden:
            self.parts.append(self.get_starttag_text())
        if tag not in self.VOID:
            self.stack.append(hidden)

    def handle_startendtag(self, tag, attrs):
        if not self.stack or not self.stack[-1]:
            self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        hidden = self.stack.pop() if self.stack else False
        if not hidden:
            self.parts.append(f'</{tag}>')

    def handle_data(self, data):
        if not self.stack or not self.stack[-1]:
            self.parts.append(data)

    def handle_entityref(self, name):
        self.handle_data(f'&{name};')

    def handle_charref(self, name):
        self.handle_data(f'&#{name};')

    def html(self):
        return '\n'.join(line.rstrip() for line in ''.join(self.parts).splitlines())


def channel_link(data):
    url = data.get('channel_url')
    if not url:
        return ''
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname not in ('www.youtube.com', 'youtube.com'):
        raise ValueError('Use a verified HTTPS YouTube channel URL')
    return f'<a class="koe-button" href="{escape(url, quote=True)}">{copy("Watch on YouTube ↗")}</a>'

@tracked_html
def render(data):
    source = (ROOT / 'index.html').read_text(encoding='utf-8')
    shell = source[source.index('  <header'):source.index('  <main')]
    shell = re.sub(r'href="(?!https?:|#)([^"]+)"', r'href="../\1"', shell)
    footer = source[source.index('  <footer'):source.index('</body>')]
    footer = re.sub(r'href="(?!https?:|#)([^"]+)"', r'href="../\1"', footer)
    shell = EnglishShell(shell).html()
    footer = EnglishShell(footer).html()
    member_label = 'Meet the members'
    stories = 'A little more of the story'
    songs_label = 'Songs so far'
    meeting = 'How they came together'
    sections = []
    for group in data['groups']:
        gid = group['id']
        cards = []
        for member in group['members']:
            cards.append(f'''<article class="koe-member" id="{member['id']}">
              <img src="{image_url(member['id'] + '.webp')}" width="600" height="720" alt="{member['name']} — {group['name']}" loading="lazy" decoding="async">
              <div class="koe-member-name"><h3>{member['name']}</h3>{copy(member['role'], 'p', 'koe-role')}</div>
              {copy(member['intro'], 'p', 'koe-member-intro')}{copy(member['story'], 'p')}
              <details class="koe-story"><summary>{copy(stories)}<span aria-hidden="true">+</span></summary><div>{copy(member['detail'], 'p')}{copy(member['quote'], 'blockquote')}</div></details>
            </article>''')
        tracks = ''.join(f'<li><span class="koe-track-number">{i:02}</span><div><h4>{escape(song[0])}</h4>{copy(song[1], "p")}</div></li>' for i, song in enumerate(group['songs'], 1))
        meeting_label = meeting
        sections.append(f'''<section id="{gid}" class="koe-group koe-{gid}"><div class="koe-inner">
          <div class="koe-group-top"><div><p class="koe-eyebrow">0{1 if gid == 'bloom' else 2} / {group['sound']}</p><h2>{group['name']}</h2>{copy(group['headline'], 'p', 'koe-group-headline')}{copy(group['description'], 'p', 'koe-group-copy')}<a class="koe-text-link" href="#{gid}-members">{copy(member_label)} ↓</a></div>
          <figure class="koe-release-art"><img src="{image_url(gid + '-release.webp')}" width="1280" height="720" alt="{group['name']} — {'Unfinished Sunday' if gid == 'bloom' else 'Who Wrote the Rules?'}" loading="lazy" decoding="async"><figcaption>{'Unfinished Sunday' if gid == 'bloom' else 'Who Wrote the Rules?'}</figcaption></figure></div>
          <div class="koe-members" id="{gid}-members">{''.join(cards)}</div>
          <div class="koe-group-bottom"><div class="koe-formation"><p class="koe-eyebrow">{copy(meeting_label)}</p>{copy(group['formation'], 'p')}</div><div class="koe-discography"><h3>{copy(songs_label)}</h3><ol>{tracks}</ol>{channel_link(data)}</div></div>
        </div></section>''')
    hero_title = 'A life of your own.\nA world to share.'
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>KOE — Bloom &amp; Pulse · Non Dubito</title>
<meta name="description" content="Meet KOE Bloom and KOE Pulse: two original virtual music trios, six distinct lives, and songs about selfhood, relationships, and the rules we share.">
<meta name="author" content="Han Qin">
<link rel="canonical" href="https://nondubito.net/koe/">
<meta property="og:title" content="KOE — Bloom &amp; Pulse"><meta property="og:description" content="A life of your own. A world to share. Meet six original virtual performers in the Self-as-an-End tradition.">
<meta property="og:type" content="website"><meta property="og:url" content="https://nondubito.net/koe/"><meta property="og:image" content="{image_url('koe-social.jpg')}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="KOE Bloom and KOE Pulse — six original virtual performers">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="../favicon.svg"><link rel="apple-touch-icon" href="../apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="../site-shell.css?v=20260905b"><link rel="stylesheet" href="koe.css"><script defer src="koe.js"></script>
</head><body class="site-shell-page koe-page">
<a class="koe-skip" href="#main">{copy('Skip to content')}</a>
{shell}
<main id="main" class="site-shell-main">
<section class="koe-hero"><div class="koe-inner"><div class="koe-hero-top"><p class="koe-eyebrow">Non Dubito / Original virtual music</p><p class="koe-wordmark">KOE<span>Kingdom of Ends</span></p></div>
<div class="koe-hero-copy"><div>{copy(hero_title, 'h1')}</div><div>{copy('Two trios. Six distinct lives. Songs that begin with what matters to a person—and follow it into the world we make together.', 'p')}<div class="koe-actions"><a class="koe-button" href="#bloom">KOE Bloom ↓</a><a class="koe-button" href="#pulse">KOE Pulse ↓</a></div>{channel_link(data)}</div></div>
<div class="koe-faces" aria-label="KOE members">{''.join(f'<a href="#{m["id"]}" aria-label="{m["name"]}, {g["name"]}"><img src="{image_url(m["id"] + ".webp")}" width="600" height="720" alt="" decoding="async" fetchpriority="{"high" if m["id"] == "nari" else "auto"}"><span>{m["name"]}</span></a>' for g in data['groups'] for m in g['members'])}</div>
<nav class="koe-section-nav" aria-label="KOE sections"><a href="#bloom">Bloom</a><a href="#pulse">Pulse</a><a href="#idea">{copy('The idea behind KOE')}</a></nav>
</div></section>
{''.join(sections)}
<section class="koe-idea" id="idea"><div class="koe-inner koe-idea-grid"><div><p class="koe-eyebrow">Kingdom of Ends</p>{copy('Each person has ends of their own.', 'h2')}</div><div>{copy('KOE takes its name from the Kingdom of Ends. In the Self-as-an-End tradition, each person has purposes, judgments, and a life of their own. Shared life asks us to make room for those purposes—and to question arrangements that turn people into instruments.', 'p')}{copy('Bloom begins with everyday feelings and relationships. Pulse follows the question into systems, power, and institutional change. Their members can be mistaken, ambitious, jealous, caring, or uncertain. Their stories continue because there is more to a person than the point a song makes.', 'p')}
<div class="koe-reading"><a href="../explore.html#everyday">{copy('Explore everyday life ↗')}</a><a href="../essays/sae/index.html">{copy('Read the philosophy ↗')}</a></div>
<div class="koe-colophon">{copy('An original virtual music project by Han Qin. All six performers and their biographies are fictional. Music and visuals are made with AI tools, alongside human-led character development, lyric writing, creative direction, selection, and editing. The shared 3D visual language stays consistent; styling changes with each song.', 'p')}</div>
</div></div></section>
</main>{footer}</body></html>'''

if __name__ == '__main__':
    data = json.loads((ROOT / 'data/koe.json').read_text(encoding='utf-8'))
    (ROOT / 'koe/index.html').write_text(render(data), encoding='utf-8')
    print('Wrote koe/index.html')
