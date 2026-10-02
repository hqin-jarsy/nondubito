"""Follow explicitly reviewed page revisions without weakening old receipts."""
import json


def _after_batch(data, path, approved_digest, batch):
    receipt = data / f'{batch}-review.json'
    if not receipt.exists():
        return approved_digest
    edit = json.loads(receipt.read_text())['page_edits'].get(path)
    if not edit:
        return approved_digest
    if edit['before_sha256'] != approved_digest:
        raise ValueError(f'{path}: {batch} does not continue the approved digest')
    return edit['after_sha256']


def after_batch12(data, path, approved_digest):
    return _after_batch(data, path, approved_digest, 'batch12')


def after_batch11(data, path, approved_digest):
    return after_batch12(data, path, _after_batch(data, path, approved_digest, 'batch11'))


def after_batch10(data, path, approved_digest):
    return after_batch11(data, path, _after_batch(data, path, approved_digest, 'batch10'))


def after_batch09(data, path, approved_digest):
    return after_batch10(data, path, _after_batch(data, path, approved_digest, 'batch09'))


def after_batch08(data, path, approved_digest):
    return after_batch09(data, path, _after_batch(data, path, approved_digest, 'batch08'))


def after_batch07(data, path, approved_digest):
    return after_batch08(data, path, _after_batch(data, path, approved_digest, 'batch07'))
