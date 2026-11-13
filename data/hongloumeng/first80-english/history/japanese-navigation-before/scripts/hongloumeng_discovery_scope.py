"""Path-only boundaries for Red Chamber discovery, checked before reading HTML."""
from pathlib import Path
from hongloumeng_english_availability import english_published
import posixpath
from urllib.parse import unquote, urlsplit

PUBLIC_HTML = frozenset(('index.html', 'edition.html', *(f'ch{n:03d}.html' for n in range(1, 81))))


def private_path(relative: Path) -> bool:
    return relative.parts[:3] == ('data', 'hongloumeng', 'first80')


def excluded(relative: Path, *, root=None, english=None) -> bool:
    if '..' in relative.parts or private_path(relative):
        return True
    if relative.parts[:2] == ('classics', 'hongloumeng'):
        return not (relative.name in PUBLIC_HTML and (len(relative.parts) == 3 or
                    len(relative.parts) == 4 and (relative.parts[2] == 'zh-hant' or relative.parts[2] == 'en' and (english_published(root) if english is None else english))))
    return False


def excluded_file(root: Path, path: Path) -> bool:
    """Check both names before opening a file; aliases cannot expose private data."""
    root, path = root.absolute(), path.absolute()
    try:
        relative = path.relative_to(root)
        if '..' in relative.parts or excluded(relative, root=root):
            return True
        if not path.is_file() or path.stat().st_nlink != 1:
            return True
        actual = path.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (OSError, RuntimeError, ValueError):
        return True
    return excluded(actual, root=root)


def site_url_path(value):
    """Decode an HTTP destination without discarding its original path boundary."""
    if not isinstance(value, str):
        raise ValueError('Invalid discovery URL')
    value = value.strip(''.join(chr(n) for n in range(33))).replace('\\', '/')
    value = value.replace('\t', '').replace('\r', '').replace('\n', '')
    parsed = urlsplit(value)
    if parsed.scheme and parsed.scheme.lower() not in ('http', 'https'):
        raise ValueError('Unsupported discovery URL scheme')
    if parsed.netloc and unquote(parsed.hostname or '').lower().rstrip('.') not in ('nondubito.net', 'www.nondubito.net'):
        return None
    path = parsed.path
    for _ in range(12):
        decoded = unquote(path)
        if decoded == path:
            break
        path = decoded
    else:
        raise ValueError('Overencoded discovery URL')
    return path.replace('\\', '/').lstrip('/')


def site_relative_url(value):
    path = site_url_path(value)
    return None if path is None else posixpath.normpath('/'+path).lstrip('/')


def excluded_url(value, *, root=None, english=None):
    """Check URL names before filesystem resolution can erase a private alias."""
    try:
        original = site_url_path(value)
    except ValueError:
        return True
    if original is None:
        return False
    normalized = posixpath.normpath('/'+original).lstrip('/')
    for name in (original, normalized):
        relative = Path(name)
        # Directory canonicals refer to the explicitly public contents page.
        if relative in (Path('classics/hongloumeng'), Path('classics/hongloumeng/zh-hant'), Path('classics/hongloumeng/en')):
            relative /= 'index.html'
        if excluded(relative, root=root, english=english):
            return True
    return False
