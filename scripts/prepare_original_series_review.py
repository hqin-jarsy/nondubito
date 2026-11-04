#!/usr/bin/env python3
"""Seal completed independent rewrites only after separate cross-review."""
import argparse
import hashlib
import json
import re
import subprocess

from full_series_languages import ROOT, load_language, profile


def prepare(series):
    spec=profile(series)
    base=ROOT/'data'/series/'multilingual'
    reports=[]
    covered=[]
    for name in ('cross-review-de-fr.json','cross-review-ja-ko.json','cross-review-es.json'):
        report=json.loads((base/name).read_text())
        assert not report['remaining'], (series,name,'incomplete review')
        covered.extend(report['languages'])
        reports.append((name,report))
    assert sorted(covered)==sorted(spec['languages'])
    final_fr=base/'final-fr-language-review.json'
    if final_fr.exists():
        report=json.loads(final_fr.read_text())
        assert not report['remaining']
        reports.append((final_fr.name,report))
    resolved=[]
    for name,report in reports:
        for issue in report['issues']:
            issue=issue.copy()
            issue.setdefault('language',report.get('language'))
            _,data=load_language(series,issue['language'])
            a=next(a for a in data['articles'] if a['slug']==issue['slug'])
            assert issue['after'] in a['body'][issue['paragraph']], (name,issue)
            issue['review_report']=name
            resolved.append(issue)
    sources={}
    primary={}
    counts=[]
    for slug in spec['slugs']:
        path=ROOT/'data'/series/(slug+'.json')
        sources[slug]=hashlib.sha256(path.read_bytes()).hexdigest()
        counts.append(len(json.loads(path.read_text())['body_zh']))
        source=(ROOT/spec['directory']/(slug+'.html')).read_text()
        body=''.join(re.findall(r'<div class="essay-body[^>]*>.*?</div>',source,re.S))
        assert body, (series,slug)
        primary[slug]=hashlib.sha256(body.encode()).hexdigest()
    outputs={}
    snapshot=base/'preservation.json'
    if not snapshot.exists():
        outputs[snapshot]={'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                           'source_data':sources,'primary_bodies':primary}
    else:
        saved=json.loads(snapshot.read_text())
        assert saved['source_data']==sources and saved['primary_bodies']==primary, 'Primary content changed'
    outputs[base/'publication.json']={
        'date':spec['date'],'result':'passed',
        'scope':'Complete independent foreign rewrites of the published Chinese reader essays, not shortened translations of their academic sources.',
        'languages':spec['languages'],'slugs':spec['slugs'],'source_units':counts,
        'new_article_editions':len(spec['languages'])*len(spec['slugs']),
        'review_method':['Chinese originals read in full; every argument unit, example and qualification retained.',
                         'Each writer self-edited; a different agent independently read every foreign article against Chinese.',
                         'The lead editor checked the source arguments, reviewed findings and applied counted local corrections.'],
        'reports':[name for name,_ in reports],'resolved_issues':resolved,'unresolved':[],
        'limits':['AI-assisted writing and editorial cross-review, not certification by a human native speaker.'],
        'deployment':'Local commit only; author pushes.'}
    return {path:json.dumps(data,ensure_ascii=False,indent=2)+'\n' for path,data in outputs.items()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for path,text in prepare(args.series).items():
        if args.check:assert path.read_text()==text,path
        else:path.write_text(text)
    print(args.series+': independent writing, cross-review and primary preservation '+('checked' if args.check else 'sealed'))


if __name__=='__main__':main()
