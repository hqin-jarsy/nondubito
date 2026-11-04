#!/usr/bin/env python3
"""Small, ordered reading routes for full-edition language indexes.

This does not publish or approve manuscripts. The parent renderer must retain
its full-prose review gate before calling it. Original primary indexes are not
read or changed here.
"""
from __future__ import annotations

import html
import re


def group_anchor(key):
    # The shared page owns #main and this component owns #reading-route.
    return 'reading-'+key if key in ('main','reading-route') else key


def validate_groups(spec, data):
    groups=spec.get('index_groups')
    if not groups:return
    assert not spec.get('standalone_slugs'),'Grouped main routes need an explicit standalone layout first'
    titles=data['series']['index_groups']
    assert [g['id'] for g in titles]==[g['id'] for g in groups]
    assert [slug for group in groups for slug in group['slugs']]==spec['slugs'], 'Groups must preserve the complete source route and order'
    assert len({g['id'] for g in groups})==len(groups)
    assert len({group_anchor(g['id']) for g in groups})==len(groups), 'Group anchors must not collide after reserving page landmarks'
    for group,title in zip(groups,titles):
        assert re.fullmatch(r'[a-z][a-z0-9-]*',group['id'])
        assert group['slugs']
        assert isinstance(title['title'],str) and title['title'].strip()


def grouped_index(spec, data, card_rows):
    """Return a compact jump route and all groups, or None for ordinary indexes."""
    if not spec.get('index_groups'):return None
    validate_groups(spec,data)
    assert [slug for slug,_ in card_rows]==spec['slugs']
    cards=dict(card_rows)
    labels={group['id']:group['title'] for group in data['series']['index_groups']}
    e=html.escape
    contents=e(data['ui']['contents'])
    links=''.join(f'<a href="#{group_anchor(group["id"])}">{e(labels[group["id"]])}</a>' for group in spec['index_groups'])
    route=f'<nav class="lw-crumb lw-group-links" id="reading-route" aria-label="{contents}" style="display:flex;flex-wrap:wrap;gap:1rem 1.5rem">{links}</nav>'
    sections=[]
    for group in spec['index_groups']:
        key=group['id']
        anchor=group_anchor(key)
        heading=f'<div class="lw-note"><h2 id="{anchor}-title">{e(labels[key])}</h2></div>'
        # Group headings remain h2; the original card titles become h3 without
        # changing the card content or its source order.
        grouped_cards=[cards[slug].replace('<h2>','<h3>',1).replace('</h2>','</h3>',1) for slug in group['slugs']]
        grid='<section class="lw-grid">'+''.join(grouped_cards)+'</section>'
        back=f'<a class="lw-read" href="#reading-route">↑ {contents}</a>'
        sections.append(f'<section class="lw-collection-group" id="{anchor}" aria-labelledby="{anchor}-title">{heading}{grid}{back}</section>')
    return route+''.join(sections)
