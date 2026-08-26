# nondubito.net — working notes for Claude

Operational quirks discovered through trial and error on this repo, via the
device bridge (Han's Mac, folder `/Users/hanqin/Documents/GitHub/nondubito`).
Read this before doing git or file work here — it'll save rediscovering the
same failures.

## Never push

Local commits only. Never `git push`, even if asked to "publish" or "ship" —
confirm with Han first if a request seems to imply pushing to remote.

## Two different path systems on the device bridge

- `device_bash` runs inside a Linux VM where this repo is mounted at
  `~/mnt/nondubito`. Use this path style only inside `device_bash` commands.
- `device_stage_files` / `device_commit_files` / `device_list_dir` need the
  REAL macOS path instead: call `get_device_info()` and use the path from
  `connectedFolders` (currently `/Users/hanqin/Documents/GitHub/nondubito`).
  Passing the `~/mnt/...` style path to these tools fails with "not inside a
  folder connected to Cowork on this device".

## Git on this mount is lock-happy

`git add` and `git commit` reliably leave behind stale `.git/index.lock`
and/or `.git/HEAD.lock` (0 bytes), sometimes with a harmless
`unable to unlink .git/objects/XX/tmp_obj_YYYYYY: Operation not permitted`
warning during the operation itself — the object still gets written
correctly. `device_bash` cannot delete files (`rm`/`unlink` fails with
"Operation not permitted"), so clear locks by moving them aside instead,
before AND after each git operation:

```
mkdir -p _to_delete
mv .git/index.lock "_to_delete/index.lock.$(date +%s).$$" 2>/dev/null
mv .git/HEAD.lock "_to_delete/HEAD.lock.$(date +%s).$$" 2>/dev/null
```

Occasionally this also leaves duplicate loose-object files with a literal
" 2" suffix (e.g. `.git/objects/3f/9868b...700` and `...700 2`, identical
content) — cosmetic `git fsck` noise, not corruption. Same `mv`-to-
`_to_delete` treatment if it comes up again; the non-suffixed object is
always the real one.

Never use `git revert` or `git checkout <ref> -- <existing-path>` on this
mount — both reliably fail here. To restore a file from history instead:
`git show <ref>:<path> > /tmp/scratch && cp -f /tmp/scratch <path>`.

## Staging only your own changes in a shared file

Han often has his own unrelated edits sitting uncommitted in the same file
you need to touch (most often root `index.html`, since every essay series
adds a section there). Do not sweep those into your commit. Check
`git diff <file>` for hunk boundaries first; if your change and his are in
separate hunks, extract just yours into a patch and stage it with
`git apply --cached`, leaving his hunk untouched and unstaged:

```
git diff index.html > /tmp/full.patch     # find the @@ hunk header lines
sed -n '<your hunk's line range>p' /tmp/full.patch > /tmp/mine.patch  # + the 4-line diff header
git apply --cached --check /tmp/mine.patch   # dry run first
git apply --cached /tmp/mine.patch
```

## Site conventions

- Never translate "Self-as-an-End" into any other language, anywhere on the
  site.
- Section headings inside `.essay-body` must be `<h2>`, never `<h3>`.
  `style.css` defines `.essay-body h2` and has **no** `h3` rule at all, so an
  `<h3>` silently falls back to the browser default and looks wrong. (The
  older rights-series files used `h3`; they were converted in Aug 2026.)
- The language-toggle script in essay and series-index pages should use the
  hardened form — reject any stored value that isn't `zh`/`en`, and set both
  the `data-lang` and `lang` attributes on `<html>`:

  ```
  var saved = localStorage.getItem('nd_lang');
  if (saved !== 'zh' && saved !== 'en') saved = 'zh';
  document.documentElement.setAttribute('data-lang', saved);
  document.documentElement.setAttribute('lang', saved === 'en' ? 'en' : 'zh');
  ```
- Each essay series follows the same three-piece pattern: `essays/<name>/
  ep0N.html` per episode, `essays/<name>/index.html` as the series landing
  page, and a `<section class="essays-section" id="<name>">` block in the
  root `index.html` homepage (usually showing 3 of N episodes as cards,
  linking out to the series index for the rest). When adding a new series,
  the fastest way to get the exact house style right is reading an existing
  series' current files as the template rather than re-deriving the CSS.
- Homepage sections alternate `background:var(--cream-dark)` — check the
  section immediately before your insertion point to pick the right value,
  don't assume.
- SAE Rights Theory series (`essays/rights/`) is currently bilingual
  (zh/en) only, by Han's explicit choice — the episodes don't have
  zh-hant/ja/fr/de/es/ko versions yet, so its index page and homepage
  section intentionally use a 2-language toggle, not the site's usual
  8-language one. Other languages are a deferred future task, not an
  oversight.
