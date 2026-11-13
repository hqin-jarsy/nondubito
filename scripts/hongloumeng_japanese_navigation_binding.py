"""Bounded reversible navigation over the authenticated chapter72 edition.

Historical literary reviews remain predecessor evidence only. This layer changes
no source or translation units and makes no claim that Japanese is unabridged.
"""
import json
from pathlib import Path
from hongloumeng_ch005_author_binding import sha, require, regular, load_module
from integrate_hongloumeng_japanese import TARGETS, transform, reverse
ROOT = Path(__file__).resolve().parents[1]
D = 'data/hongloumeng/first80-english/'
HISTORY = D + 'history/japanese-navigation-before'
BINDING = D + 'japanese-navigation-binding.json'
BINDING_SHA256 = '726c6e1879868a5473bca2294c44c27c6d865fccef6287c0c966e01ab5521e90'


def binding(root=ROOT):
    root = Path(root)
    raw = regular(root, BINDING)
    require(sha(raw) == BINDING_SHA256, 'Unpinned Japanese navigation binding')
    bound = json.loads(raw)
    require(bound['scope'] == 'bounded-japanese-navigation-local-generation'
            and bound['changedSourceUnits'] == bound['changedEnglishUnits'] == 0
            and bound['fullCorpusReread'] is False and bound['ownerPlaceholders'] == 11,
            'Navigation scope differs')
    require(set(bound['html']) == set(TARGETS), 'Navigation HTML scope differs')
    for name, checksum in bound['preserved'].items():
        require(sha(regular(root, name)) == checksum, 'Navigation dependency differs: '+name)
    for name, row in bound['scripts'].items():
        require(sha(regular(root, name)) == row['afterSHA256'], 'Navigation implementation differs: '+name)
        require(sha(regular(root/HISTORY, name)) == row['beforeSHA256'], 'Navigation predecessor script differs: '+name)
    for name, row in bound['html'].items():
        current = regular(root, name)
        require(sha(current) == row['afterSHA256'], 'Navigation current HTML differs: '+name)
        previous = reverse(name, current)
        require(sha(previous) == row['beforeSHA256'] and transform(name, previous) == current,
                'Navigation widened beyond exact insertions: '+name)
    require(sha(regular(root/HISTORY, D+'reading-publication.json')) == bound['priorApprovalSHA256'],
            'Predecessor publication record differs')
    return bound


def predecessor(root=ROOT):
    root = Path(root); bound = binding(root)
    def before(context, name):
        if Path(context).resolve() == root.resolve():
            if name in bound['html']:
                return reverse(name, regular(root, name))
            if name in bound['scripts']:
                return regular(root/HISTORY, name)
        return regular(context, name)
    prior = load_module(root/'scripts/hongloumeng_ch072_decisions_binding.py', '_japanese_navigation_ch072')
    prior.regular = before
    pipe = load_module(root/HISTORY/'scripts/hongloumeng_english_pipeline.py', '_japanese_navigation_pipeline')
    pipe.ROOT = root; pipe.SOURCE = root/'data/hongloumeng/first80-public'; pipe.DATA = root/D
    pipe.STANDARD = root/'docs/hongloumeng/translation'
    return prior, pipe


def validate_readiness(pipe, mapping, progress):
    prior, oldpipe = predecessor(pipe.ROOT)
    result = prior.validate_readiness(oldpipe, mapping, progress)
    require_japanese_reader(pipe.ROOT)
    require(result == pipe.EXPECTED_NORMATIVE_SNAPSHOT, 'Navigation changed translation standard')
    return result


def note_record(record, note, source, unit, root=ROOT):
    prior, _ = predecessor(root)
    return prior.note_record(record, note, source, unit, root)


def require_japanese_reader(root=ROOT):
    from hongloumeng_japanese_availability import japanese_publication
    require(japanese_publication(root) is not None, 'Japanese navigation requires a verified Japanese reader')


def navigation_outputs(prefix, pages):
    """Pure postprocessing; callers retain their independent publication gates."""
    return {name: (transform(prefix+name, value.encode() if isinstance(value, str) else value).decode()
                   if name.endswith('.html') else value) for name, value in pages.items()}
