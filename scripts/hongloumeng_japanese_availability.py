"""Validate the current hand-edited HTML, never compare it with archived JSON."""
from html.parser import HTMLParser
from pathlib import Path
import re
import stat
from build_hongloumeng_reading import checked_input_paths

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'classics/hongloumeng/ja/'
NAMES = frozenset(('index.html', 'edition.html', 'reader.css', 'reader.js',
                   *(f'ch{n:03d}.html' for n in range(1, 81))))


class ReaderHTML(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.links = set()
        self.ids = []
        self.markers = []
        self.articles = self.closed_articles = 0
        self.in_article = False
        self.body = []
        self.language = None
        self.feed(raw)
        self.close()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.language = a.get('lang')
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a':
            self.links.add(a.get('href', ''))
        if tag == 'mark':
            self.markers.append(a.get('id', ''))
        if tag == 'article':
            self.articles += 1
            self.in_article = True

    def handle_endtag(self, tag):
        if tag == 'article':
            self.closed_articles += 1
            self.in_article = False

    def handle_data(self, data):
        if self.in_article:
            self.body.append(data)


def japanese_publication(root=None):
    root = Path(root) if root is not None else ROOT
    target = root / PREFIX
    if not target.exists():
        return None
    checked_input_paths(target / name for name in NAMES)
    if target.is_symlink() or not target.is_dir():
        raise ValueError('Invalid Japanese reader directory')
    actual = set()
    for path in target.iterdir():
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('Japanese reader contains directory, alias or nonregular file')
        actual.add(path.name)
    if actual != NAMES:
        raise ValueError('Japanese reader inventory differs from expected files')
    partial = {}
    for name in sorted(NAMES):
        if not name.endswith('.html'):
            continue
        raw = (target / name).read_text(encoding='utf-8')
        doc = ReaderHTML(raw)
        if doc.language != 'ja' or len(doc.ids) != len(set(doc.ids)):
            raise ValueError('Invalid Japanese page language or duplicate IDs: ' + name)
        for directory in ('', 'zh-hant/', 'en/', 'ja/'):
            if '/classics/hongloumeng/' + directory + name not in doc.links:
                raise ValueError('Missing language navigation: ' + name)
        if not re.fullmatch(r'ch[0-9]{3}\.html', name):
            continue
        n = int(name[2:5])
        if doc.articles != 1 or doc.closed_articles != 1 or not ''.join(doc.body).strip():
            raise ValueError('Missing or invalid Japanese article: ' + name)
        # Stable IDs survive filling one slot; do not renumber the others.
        if any(not re.fullmatch(rf'CH{n:03}-P[0-9]{{2}}', marker) for marker in doc.markers):
            raise ValueError('Invalid incomplete markers: ' + name)
        for marker in doc.markers:
            if f'【日訳未完 {marker}】' not in raw or '#' + marker not in doc.links:
                raise ValueError('Missing incomplete label or link: ' + name)
        if doc.markers:
            partial[n] = len(doc.markers)
        required = {'index.html'}
        if n > 1:
            required.add(f'ch{n-1:03}.html')
        if n < 80:
            required.add(f'ch{n+1:03}.html')
        else:
            required.add('/originals/hongloumeng/ja/ch081.html')
            if '曹雪芹の失われた原稿ではありません' not in raw:
                raise ValueError('Missing original/continuation boundary')
        if not required <= doc.links:
            raise ValueError('Missing chapter navigation: ' + name)
    return dict(root=root.resolve(), paths=tuple(target / name for name in sorted(NAMES)
                                               if name.endswith('.html')),
                completeChapters=80-len(partial), partialChapters=len(partial),
                ownerPlaceholders=sum(partial.values()), partial=partial,
                literaryAcceptance=False)


def japanese_published(root=None):
    try:
        return japanese_publication(root) is not None
    except (ValueError, KeyError, TypeError, OSError):
        return False
