"""French publication availability, classification, and private-path boundaries."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build_content_registry as registry
from hongloumeng_discovery_scope import excluded, excluded_file, excluded_url
from hongloumeng_french_availability import NAMES, PREFIX, french_published
from refresh_hongloumeng_french_search import outputs


class FrenchDiscoveryTests(unittest.TestCase):
    def fixture(self, root):
        target = root / PREFIX
        target.mkdir(parents=True)
        for name in NAMES:
            body = '<html lang="fr"><head><title>Lecture</title></head><body>'
            if name.startswith('ch'):
                n = int(name[2:5])
                links = ['index.html']
                if n > 1:
                    links.append(f'ch{n-1:03d}.html')
                links.append(f'ch{n+1:03d}.html' if n < 80 else '/originals/hongloumeng/fr/ch081.html')
                body += '<article>Texte français.</article>' + ''.join(f'<a href="{link}">Lire</a>' for link in links)
            (target / name).write_text(body + '</body></html>')
        return target

    def test_exact_public_boundary_and_classification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            self.assertTrue(french_published(root))
            for name in ('index.html', 'edition.html', 'ch001.html', 'ch080.html'):
                relative = Path(PREFIX) / name
                self.assertFalse(excluded(relative, root=root))
                self.assertFalse(excluded_url('/' + str(relative), root=root))
            self.assertFalse(excluded_url('/' + PREFIX, root=root))
            for name in ('review.html', 'ch000.html', 'ch081.html', 'nested/index.html', 'ch001 2.html'):
                self.assertTrue(excluded(Path(PREFIX) / name, root=root))
            for name in ('data/hongloumeng/first80/fr/secret.html', PREFIX + '../ch001.html', PREFIX + '%2e%2e/ch001.html'):
                self.assertTrue(excluded_url('/' + name, root=root))
        self.assertEqual(registry.infer_record_type(Path(PREFIX + 'index.html')), 'series-index')
        self.assertEqual(registry.infer_record_type(Path(PREFIX + 'edition.html')), 'site-page')
        for n in range(1, 81):
            path = Path(PREFIX + f'ch{n:03d}.html')
            self.assertEqual(registry.infer_record_type(path), 'novel-chapter')
            self.assertEqual(registry.infer_sequence(path), n)

    def test_scoped_refresh_preserves_unrelated_records_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / 'data/search').mkdir(parents=True)
            manifest_path = root / 'data/search-index.json'
            chunk_path = root / 'data/search/fr.json'
            manifest = {'record_count': 10, 'languages': {'fr': {'count': 1}, 'en': {'count': 9}}, 'untouched': 'keep'}
            unrelated = {'u': 'essays/other/fr/index.html', 't': 'Unrelated', 'x': 'Keep exactly'}
            manifest_path.write_text(json.dumps(manifest))
            chunk_path.write_text(json.dumps({'version': 1, 'language': 'fr', 'records': [unrelated]}))
            result = outputs(root)
            self.assertEqual(set(result), {manifest_path, chunk_path})
            new_manifest = json.loads(result[manifest_path])
            self.assertEqual(new_manifest['record_count'], 92)
            self.assertEqual(new_manifest['languages']['en'], manifest['languages']['en'])
            self.assertEqual(new_manifest['untouched'], 'keep')
            records = json.loads(result[chunk_path])['records']
            self.assertEqual(records[0], unrelated)
            self.assertEqual(len(records), 83)
            for path, content in result.items():
                path.write_text(content)
            self.assertEqual(outputs(root), result)

    def test_absent_partial_and_alias_readers_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertFalse(french_published(root))
            target = self.fixture(root)
            path = target / 'ch001.html'
            original = path.read_text()
            path.write_text(original.replace('lang="fr"', 'lang="en"'))
            self.assertFalse(french_published(root))
            path.unlink()
            secret = root / 'secret.html'
            secret.write_text('PRIVATE_SENTINEL')
            path.symlink_to(secret)
            with patch.object(Path, 'read_text', side_effect=AssertionError('Alias must fail before any read')):
                self.assertFalse(french_published(root))
                self.assertTrue(excluded_file(root, path))


if __name__ == '__main__':
    unittest.main()
