#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Targeted companion routes; no case is treated as a proof of the framework."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_TO_THEORY = {
    'introduction': ('ep01', 'ep08'),
    'petsmart-training': ('ep03', 'ep07', 'ep06'),
    'amazon-marketplace': ('ep02', 'ep04'),
    'steward-hospitals': ('ep06', 'ep04', 'ep07'),
    'credit-ratings': ('ep05', 'ep02'),
    'google-adtech': ('ep04', 'ep02'),
    'thames-water': ('ep03', 'ep04', 'ep06'),
    'foxconn-wisconsin': ('ep07', 'ep06'),
    'apple-app-store': ('ep04', 'ep05'),
    'jimmy-johns': ('ep03',),
}


def theory_data(slug):
    return json.loads((ROOT / 'data/political-economy/theory' / (slug + '.json')).read_text())


def theory_companion(slug, conv, loc):
    links = ''.join('<a href="theory/' + guide + '.html">'
                    + loc(theory_data(guide)['title_en'], theory_data(guide)['title_zh'], conv)
                    + '</a>' for guide in CASE_TO_THEORY[slug])
    return ('<aside class="lw-related pe-theory-companion">'
            + loc('Understand the SAE argument', '读懂背后的 SAE 主张', conv, 'h2')
            + loc('Why usable exit, checks on decisions and support for a life of one’s own matter: read the corresponding arguments, not just the case. The theory does not replace the evidence or determine every legal outcome.',
                  '为什么要检查真实退出、决定的制衡与支持自己的路？到相应散文读清主张与理由，而不只停在案例。理论不代替证据，也不预定每一案的法律结论。', conv, 'p')
            + links + '<a href="theory/index.html">'
            + loc('The complete eight-essay reading path →', '八篇理论导读的完整路线 →', conv)
            + '</a></aside>')
