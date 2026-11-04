#!/usr/bin/env python3
"""Seal completed independent rewrites only after separate cross-review."""
import argparse
import hashlib
import json
import re
import subprocess

from full_series_languages import ROOT, load_language, profile, primary_bodies


def primary_main_hashes(spec):
    """Protect all primary reading content, allowing only its language controls."""
    result={}
    for slug in ['index',*spec['slugs']]:
        path=ROOT/spec['directory']/(slug+'.html')
        match=re.search(r'<main\b[^>]*>.*?</main>',path.read_text(),re.S)
        assert match,(slug,'missing primary main')
        content=re.sub(r'<div class="lang-toggle"[^>]*>.*?</div>','',match[0],flags=re.S)
        for css in spec.get('main_mutable_classes',[]):
            assert re.fullmatch(r'[a-z][a-z0-9-]*',css)
            content=re.sub(r'<p\b(?=[^>]*class="[^"]*\b'+re.escape(css)+r'\b)[^>]*>.*?</p>','',content,flags=re.S)
        result[str(path.relative_to(ROOT))]=hashlib.sha256(content.encode()).hexdigest()
    return result


def require_rebuilt_primary_sources(spec):
    """Do not seal old HTML after approving a correction to its source JSON."""
    if not spec.get('source_corrections'):return
    receipt=json.loads((ROOT/spec['source_corrections']).read_text())
    proofs=[receipt['primary_body_change'],*receipt.get('additional_primary_body_changes',[])]
    for proof in proofs:
        source=(ROOT/proof['path']).read_text()
        bodies=dict(re.findall(r'<div class="essay-body [^"]*lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>',source,re.S))
        assert set(bodies)=={'en','zh','hant'},(proof['path'],'missing primary reading mode')
        for language,body in bodies.items():
            actual=hashlib.sha256(body.encode()).hexdigest()
            assert actual==proof['after_sha256'][language],(proof['path'],language,'approved source correction not rebuilt in primary modes')


def prepare(series):
    spec=profile(series)
    base=ROOT/'data'/series/'multilingual'
    reports=[]
    covered=[]
    for name in ('cross-review-de-fr.json','cross-review-ja-ko.json','cross-review-es.json'):
        report=json.loads((base/name).read_text())
        assert not report['remaining'], (series,name,'incomplete review')
        if spec.get('require_explicit_publication_approval'):
            assert report.get('publication_ready') is True,(series,name,'not approved for publication')
        if spec.get('require_review_seal'):
            expected={(language,slug) for language in report['languages'] for slug in spec['slugs']}
            reviewed=[(item['language'],item['slug']) for item in report['articles_reviewed']]
            assert len(reviewed)==len(expected) and set(reviewed)==expected,(series,name,'incomplete article reading record')
        covered.extend(report['languages'])
        reports.append((name,report))
    assert sorted(covered)==sorted(spec['languages'])
    for optional in ('final-de-language-review.json','final-fr-language-review.json','lead-final-review.json'):
        path=base/optional
        if path.exists():
            report=json.loads(path.read_text())
            assert not report['remaining']
            reports.append((path.name,report))
    resolved=[]
    for name,report in reports:
        for issue in [*report['issues'],*report.get('metadata_issues',[])]:
            issue=issue.copy()
            issue.setdefault('language',report.get('language'))
            _,data=load_language(series,issue['language'])
            field=issue.get('field','body')
            if field.startswith(('ui.','series.')):
                group,key=field.split('.',1)
                value=data[group][key]
                if isinstance(value,list):value=value[issue['paragraph']]
            else:
                a=next(a for a in data['articles'] if a['slug']==issue['slug'])
                assert field in ('body','title','deck','source_note'), (name,field)
                value=a['body'][issue['paragraph']] if field=='body' else a[field]
            assert issue['after'] in value, (name,issue)
            issue['review_report']=name
            resolved.append(issue)
    require_rebuilt_primary_sources(spec)
    sources={}
    primary={}
    counts=[]
    for slug in spec['slugs']:
        path=ROOT/'data'/series/(slug+'.json')
        sources[slug]=hashlib.sha256(path.read_bytes()).hexdigest()
        counts.append(len(json.loads(path.read_text())['body_zh']))
        source=(ROOT/spec['directory']/(slug+'.html')).read_text()
        body=primary_bodies(spec,source)
        assert body, (series,slug)
        primary[slug]=hashlib.sha256(body.encode()).hexdigest()
    outputs={}
    snapshot=base/'preservation.json'
    route_protection=None
    protected_files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                     for pattern in spec.get('protected_files',[]) for p in sorted(ROOT.glob(pattern))}
    primary_main=primary_main_hashes(spec) if spec.get('preserve_primary_main') else None
    if spec.get('append_only'):
        from companion_languages import route_snapshot
        route_protection=route_snapshot(series)
    if not snapshot.exists():
        outputs[snapshot]={'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                           'source_data':sources,'primary_bodies':primary}
        if route_protection:outputs[snapshot]['existing_route']=route_protection
        if protected_files:outputs[snapshot]['protected_files']=protected_files
        if primary_main:outputs[snapshot]['primary_main']=primary_main
    else:
        saved=json.loads(snapshot.read_text())
        assert saved['source_data']==sources and saved['primary_bodies']==primary, 'Primary content changed'
        if route_protection:assert saved['existing_route']==route_protection,'Existing route changed'
        if protected_files:assert saved['protected_files']==protected_files,'Protected primary files changed'
        if primary_main:assert saved['primary_main']==primary_main,'Primary reading content changed'
    outputs[base/'publication.json']={
        'date':spec['date'],'result':'passed',
        'scope':'Complete independent foreign rewrites of the published Chinese reader essays, not shortened translations of their academic sources.',
        'languages':spec['languages'],'slugs':spec['slugs'],'source_units':counts,
        'language_data_sha256':{code:hashlib.sha256((base/(code+'.json')).read_bytes()).hexdigest() for code in spec['languages']},
        'new_article_editions':len(spec['languages'])*len(spec['slugs']),
        'review_method':['Chinese originals read in full; every argument unit, example and qualification retained.',
                         'Each writer self-edited; a different agent independently read every foreign article against Chinese.',
                         'The lead editor checked the source arguments, reviewed findings and applied counted local corrections.'],
        'reports':[name for name,_ in reports],'resolved_issues':resolved,'unresolved':[],
        'limits':['AI-assisted writing and editorial cross-review, not certification by a human native speaker.'],
        'deployment':'Local commit only; author pushes.'}
    if spec.get('require_review_seal'):
        outputs[base/'publication.json']['review_report_sha256']={
            name:hashlib.sha256((base/name).read_bytes()).hexdigest() for name,_ in reports}
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
