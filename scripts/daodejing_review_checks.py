"""Follow explicitly reviewed page revisions without weakening old receipts."""
import json


def after_batch07(data, path, approved_digest):
    receipt = data / 'batch07-review.json'
    if not receipt.exists():
        return approved_digest
    edit = json.loads(receipt.read_text())['page_edits'].get(path)
    if not edit:
        return approved_digest
    if edit['before_sha256'] != approved_digest:
        raise ValueError(f'{path}: batch07 does not continue the approved digest')
    return edit['after_sha256']
