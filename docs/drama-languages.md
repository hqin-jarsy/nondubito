# Structures in Drama: complete language editions

The 23 canonical Chinese articles and existing independent English editions remain in `data/drama/01.json` through `23.json`. Five complete translations live in `data/drama-full/{de,fr,es,ja,ko}/NN.json`. Each target body preserves the Chinese paragraph order and count. Work names, author names, titles, decks, source notes and source labels are localized; source destinations are retained.

The default full build also checks the reviewed batch receipts and refuses translations changed after acceptance. The original inputs are checked against `data/drama-full/source-manifest.json`. This protects Chinese and English content from accidental drift. Hashes of all 69 previously published Chinese, Traditional Chinese and English prose blocks additionally ensure their rendered bodies remain byte-identical. An intentional future source edit must receive editorial review and update the associated translations and baseline explicitly.

The public URLs remain unchanged. All eight editions are contained in the existing 24 HTML pages. `?lang=de` (and the other supported language codes) selects an edition; switching updates the copied URL, language attributes, title, controls, local navigation and stored preference. JavaScript-disabled visitors see the existing English fallback. The scoped drama shell does not change other collections' language behaviour.

## Rebuild and check

Run from the repository root with Python 3. Normal builds use the frozen Traditional Chinese dictionary and do not require macOS conversion frameworks:

```
python3 -B scripts/audit_drama_translations.py
python3 -B scripts/build_drama_series.py
python3 -B scripts/refresh_drama_discovery.py
python3 -B scripts/check_web_analytics.py --fix
python3 -B -m unittest discover -s scripts -p test_drama_series.py
python3 -B scripts/build_drama_series.py --check
python3 -B scripts/refresh_drama_discovery.py --check
python3 -B scripts/check_web_analytics.py
```

The recorded dictionary in `data/drama-full/traditional.json` preserves the existing conversion output. Its hash is checked against the source manifest. If Chinese source or interface text intentionally changes, explicitly refresh it on macOS with `python3 -B scripts/build_drama_series.py --refresh-traditional`, review the output, and update the corresponding editorial baselines. Ordinary builds never refresh it implicitly.

The discovery refresh updates only this series' ledger/latest entries, relevant shelf counts, five language-hub entries, its sitemap dates, the homepage digest and affected search records. It does not replace unrelated search records or historical launch metadata. The existing drama generator is upgraded in place, so running it cannot silently restore the previous three-edition layout.

For local browser checks, serve the repository on localhost and run `node scripts/test_drama_browser.cjs http://127.0.0.1:8796` with an available Playwright module and Chrome. The test blocks all off-origin requests. It covers all 24 pages in all eight languages at desktop and mobile widths, plus narrow layout, search entries, language hubs, repeated menu dismissal, history/reload and denied-storage navigation. Run actual checks against the final regenerated files; syntax checks alone are not a browser pass.

## Editorial verification

Five-article batches (01–05, 06–10, 11–15, 16–20 and 21–23) receive full translator self-review and independent paragraph-by-paragraph cross-review. Reports in `data/drama-full/review/` identify scope and corrections. Mechanical paragraph counts and hashes support, but do not replace, semantic reading. The existing English receives a documented targeted sample instead of being presumed to need replacement. This work translates the accepted articles; it does not claim a fresh scholarly verification of every assertion against every cited play edition.
