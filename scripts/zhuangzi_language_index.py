"""Keep the published non-linear reading map in approved native editions.

This helper does not approve or publish drafts. The caller must first enforce
the complete independent-reading publication seal.
"""
import html
import json

from build_zhuangzi import DATA, GROUPS, RESEARCH


def apparatus_inline(text, references):
    """Keep real reference URLs with parentheses intact in narrow Markdown.

    The shared legacy formatter intentionally stops at a closing parenthesis.
    Encode parentheses only in exact known source destinations for these new
    editions, without changing source data or older published output.
    """
    from full_series_languages import inline_markdown
    for source in references:
        url = source['url']
        if '(' in url or ')' in url:
            encoded = url.replace('(', '%28').replace(')', '%29')
            text = text.replace(']('+url+')', ']('+encoded+')')
    return inline_markdown(text)


def routes():
    manifest = json.loads((DATA/'manifest.json').read_text())
    return [(key, numbers, [f'{a["number"]:02d}' for a in manifest['items']
                            if a['group'] == key]) for key, numbers, _ in GROUPS]


def validate_index(spec, data):
    assert spec['source_adapter'] == 'zhuangzi-markdown'
    expected = routes()
    assert [a['slug'] for a in data['articles']] == ['guide']+[f'{n:02d}' for n in range(1, 68)]
    title = data['series']
    assert [g['id'] for g in title['reading_groups']] == [g[0] for g in expected]
    assert [g[2][0] for g in expected] == ['01', '11', '30', '42', '66']
    assert spec['entry_slugs'] == ['guide', '01', '11', '30', '42', '66']
    assert len(title['entry_labels']) == 6
    assert len(title['route_notes']) == 5
    for group in title['reading_groups']:
        assert isinstance(group['title'], str) and group['title'].strip()
    for value in [*title['entry_labels'], *title['route_notes'], title['map_note'],
                  title['sequence_label'], data['ui']['research']]:
        assert isinstance(value, str) and value.strip() and '<' not in value
    guide = data['articles'][0]
    assert len(guide['notes']) == 1
    assert [s['url'] for s in guide['sources']] == [
        'https://doi.org/10.5281/zenodo.'+r[3] for r in RESEARCH]
    grouped = [slug for _, _, slugs in expected for slug in slugs]
    assert len(grouped) == 67 and set(grouped) == set(spec['slugs'][1:])


def reading_index(spec, data, card_rows):
    validate_index(spec, data)
    from full_series_languages import inline_markdown
    e = html.escape
    title, ui = data['series'], data['ui']
    articles = {a['slug']: a for a in data['articles']}
    cards = dict(card_rows)
    assert list(cards) == spec['slugs']
    marker = '<span class="lw-read">'+e(ui['read'])+' →</span>'
    assert cards['guide'].count(marker) == 1
    guide_card = cards['guide'].replace(marker, '<span class="lw-read">'+e(title['entry_labels'][0])+' →</span>', 1)
    groups = routes()
    labels = {g['id']: g['title'] for g in title['reading_groups']}
    entries = ''.join('<a href="'+slug+'.html">'+e(label)+'<small>'+e(note)+'</small></a>'
                      for slug, label, note in zip(spec['entry_slugs'][1:],
                                                  title['entry_labels'][1:], title['route_notes']))
    navigation = ''.join('<a href="#'+key+'">'+e(labels[key])+'</a>' for key, _, _ in groups)
    def row(slug):
        return '<li><a href="'+slug+'.html"><span>'+slug+'</span>'+e(articles[slug]['title'])+'</a></li>'
    sections = ''.join('<section class="zz-native-group" id="'+key+'"><p class="lw-kicker">'
                       +e(numbers)+'</p><h2>'+e(labels[key])+'</h2><ol class="zz-native-toc">'
                       +''.join(row(slug) for slug in slugs)+'</ol><a href="#contents" class="lw-read">↑ '
                       +e(ui['contents'])+'</a></section>' for key, numbers, slugs in groups)
    sequence = '<details class="zz-native-sequence"><summary>'+e(title['sequence_label'])+'</summary><ol class="zz-native-toc">'
    sequence += ''.join(row(slug) for slug in spec['slugs'][1:])+'</ol></details>'
    guide = articles['guide']
    research = '<aside class="lw-note" id="research"><h2>'+e(ui['research'])+'</h2><p>'+inline_markdown(guide['notes'][0])+'</p><ul>'
    research += ''.join('<li><a href="'+e(s['url'])+'">'+e(s['title'])+'</a></li>' for s in guide['sources'])+'</ul></aside>'
    return ('<div class="lw-zhuangzi-index"><section class="lw-grid">'+guide_card+'</section>'
            +'<section class="lw-note"><h2>'+e(ui['entry_routes'])+'</h2><div class="zz-native-routes">'+entries+'</div></section>'
            +'<section id="contents"><h2>'+e(ui['contents'])+'</h2><p>'+e(title['map_note'])+'</p>'
            +'<nav class="zz-native-group-nav" aria-label="'+e(ui['contents'])+'">'+navigation+'</nav>'
            +sections+sequence+'</section>'+research+'</div>')
