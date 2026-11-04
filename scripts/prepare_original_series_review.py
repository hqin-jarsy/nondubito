#!/usr/bin/env python3
"""Seal completed independent rewrites only after separate cross-review."""
import argparse
import hashlib
import json
import re
import subprocess

from full_series_languages import (ROOT, load_language, profile, primary_bodies,
                                   source_digest, original_article)


def review_value_sha256(value):
    """Stable object identity used by the actual complete-reading reports."""
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()


def review_field(data, item):
    field=item.get('field','body')
    if field.startswith(('series.','ui.')):
        group,key=field.split('.',1)
        value=data[group][key]
        return value[item['paragraph']] if isinstance(value,list) and 'paragraph' in item else value
    article=next(a for a in data['articles'] if a['slug']==item['slug'])
    if field.startswith(('sources.','case_links.')):
        group,key=field.split('.',1)
        return article[group][item['paragraph']][key]
    value=article[field]
    return value[item['paragraph']] if field in ('body','notes','notes_coverage') else value


def saved_field_matches(value, digest):
    # Earlier genuine reports use raw UTF-8 for strings, later ones stable JSON.
    accepted={review_value_sha256(value)}
    if isinstance(value,str):accepted.add(hashlib.sha256(value.encode()).hexdigest())
    return digest in accepted


def verify_article_reading(article, record, current):
    """Bind a completed reading to this whole article, not only edited snippets."""
    original=record.get('reading_article_sha256',record.get('article_sha256'))
    assert isinstance(original,str) and re.fullmatch(r'[0-9a-f]{64}',original),'Missing reading-time fingerprint'
    assert record.get('units_read',record.get('body_units'))==len(article['body'])
    assert record.get('notes_read',record.get('writing_notes_read'))==len(article.get('notes',[]))
    assert record.get('source_links_read',record.get('sources_read'))==len(article.get('sources',[]))
    assert current==review_value_sha256(article),(record['slug'],'manuscript differs from final actual reading')


def verify_saved_readbacks(data, report):
    fields=[]
    for key in ('post_application','post_application_readback'):
        post=report.get(key,{})
        if post.get('passed') is True:
            assert post.get('reader') and post.get('scope'),'Unattributed saved-field readback'
            fields.extend(post.get('fields_read',[]))
            fields.extend(post.get('fields',[]))
    for issue in [*report.get('issues',[]),*report.get('metadata_issues',[])]:
        value=review_field(data,issue)
        assert isinstance(value,str) and issue['after'] in value,('Accepted correction missing',issue)
        assert any(f.get('slug')==issue.get('slug')
                   and f.get('field','body')==issue.get('field','body')
                   and f.get('paragraph')==issue.get('paragraph')
                   and saved_field_matches(value,f.get('saved_field_sha256'))
                   for f in fields),('Actual complete saved-field readback missing or stale',issue)


def verify_shared_reading(data, evidence):
    assert evidence['language']==data['language']
    for group in ('series','ui'):
        assert evidence[group+'_sha256']==review_value_sha256(data[group]),(group,'shared object changed since reading')
    fields=evidence['fields']
    expected={group+'.'+key for group in ('series','ui') for key in data[group]}
    assert len(fields)==len(expected) and {f['field'] for f in fields}==expected,'Incomplete shared-field reading record'
    for field in fields:
        value=review_field(data,field)
        assert field['value']==value and saved_field_matches(value,field['saved_field_sha256']),(field['field'],'shared field changed since reading')


def read_evidence_report(base, name, digest):
    assert isinstance(name,str) and name==name.rsplit('/',1)[-1] and '\\' not in name,'Evidence must be a local report filename'
    path=base/name
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,(name,'evidence report changed after consolidation')
    return json.loads(path.read_text())


def require_strict_reading_evidence(series, spec, base, reports):
    """Opt-in mechanical binding, not a claim to automate prose quality.

    No report, reading or approval is synthesized. Only already completed,
    independently recorded readings can authorize the exact current payload.
    """
    if not spec.get('strict_reading_evidence'):return
    raw={language:json.loads((base/(language+'.json')).read_text()) for language in spec['languages']}
    # Validate every manuscript even if that language has no listed corrections.
    for language in spec['languages']:load_language(series,language)
    for name,report in reports:
        if not name.startswith('cross-review-'):continue
        evidence_names=report['evidence_reports']
        manifest=report['evidence_report_sha256']
        assert len(evidence_names)==len(set(evidence_names)) and set(evidence_names)==set(manifest),'Incomplete evidence manifest'
        evidence={n:read_evidence_report(base,n,manifest[n]) for n in evidence_names}
        expected={(language,slug) for language in report['languages'] for slug in spec['slugs']}
        seen=set()
        for record in report['articles_reviewed']:
            language,slug=record['language'],record['slug']
            assert (language,slug) in expected and (language,slug) not in seen
            seen.add((language,slug))
            data=raw[language]
            article=next(a for a in data['articles'] if a['slug']==slug)
            verify_article_reading(article,record,record['current_article_sha256'])
            individual=evidence[record['reading_report']]
            assert individual['batch_ready'] is True and individual.get('batch_remaining',[])==[],'Unfinished reading batch'
            originals=[a for a in individual['articles_reviewed'] if a['language']==language and a['slug']==slug]
            assert len(originals)==1,'Missing unique original reading record'
            original=originals[0]
            verify_article_reading(article,original,individual['current_batch_article_sha256'][slug])
            assert record.get('reading_article_sha256',record.get('article_sha256'))==original.get('reading_article_sha256',original.get('article_sha256')),'Reading-time fingerprint changed during consolidation'
            verify_saved_readbacks(data,individual)
        assert seen==expected,'Incomplete actual article evidence'
        shared=report['complete_shared_metadata_evidence']
        assert set(shared)==set(report['languages']),'Missing full shared metadata evidence'
        for language in report['languages']:
            individual=evidence['cross-review-'+language+'-shared.json']
            assert individual['metadata_ready'] is True and individual.get('metadata_remaining',[])==[] and individual.get('remaining',[])==[],'Unfinished shared reading'
            current=individual.get('current_objects_read',individual['objects_read'])
            matches=[item for item in current if item['language']==language]
            assert len(matches)==1 and shared[language]==matches[0],'Shared evidence differs from actual final reading'
            verify_shared_reading(raw[language],shared[language])
            verify_saved_readbacks(raw[language],individual)


def primary_main_hashes(spec):
    """Protect all primary reading content, allowing only its language controls."""
    result={}
    for sub in spec.get('primary_editions',{'zh':''}).values():
        for slug in ['index',*spec['slugs']]:
            path=ROOT/spec['directory']/sub/(slug+'.html')
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
    require_strict_reading_evidence(series,spec,base,reports)
    # Keep validated manuscripts local to this preparation call. A large series
    # can have hundreds of resolved findings; rereading and revalidating all of
    # its articles once per finding adds no protection. Never cache across calls,
    # so later edits and the negative-corruption checks still receive fresh data.
    manuscripts={}
    resolved=[]
    for name,report in reports:
        for issue in [*report['issues'],*report.get('metadata_issues',[])]:
            issue=issue.copy()
            issue.setdefault('language',report.get('language'))
            language=issue['language']
            if language not in manuscripts:
                manuscripts[language]=load_language(series,language)[1]
            data=manuscripts[language]
            field=issue.get('field','body')
            if field.startswith(('ui.','series.')):
                group,key=field.split('.',1)
                value=data[group][key]
                if isinstance(value,list):value=value[issue['paragraph']]
            else:
                a=next(a for a in data['articles'] if a['slug']==issue['slug'])
                if field.startswith(('sources.','case_links.')):
                    group,key=field.split('.',1)
                    assert key in ('title','note'),(name,field)
                    value=a[group][issue['paragraph']][key]
                else:
                    assert field in ('body','notes','notes_coverage','aside','title','deck','source_note','takeaway','kicker','pause'), (name,field)
                    value=a[field][issue['paragraph']] if field in ('body','notes','notes_coverage') else a[field]
            assert issue['after'] in value, (name,issue)
            issue['review_report']=name
            resolved.append(issue)
    require_rebuilt_primary_sources(spec)
    sources={}
    primary={}
    counts=[]
    for slug in spec['slugs']:
        sources[slug]=source_digest(series,spec,slug)
        counts.append(len(original_article(series,spec,slug)['body_zh']))
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
    if spec.get('primary_baseline'):
        before=json.loads((ROOT/spec['primary_baseline']).read_text())
        assert before['source_data']==sources, 'Primary source differs from pre-expansion baseline'
        assert before['primary_bodies']==primary, 'Primary bodies differ from pre-expansion baseline'
        assert before['primary_main']==primary_main, 'Primary reading content differs from pre-expansion baseline'
        for name,digest in before.get('hant_dictionaries',{}).items():
            assert protected_files.get(name)==digest, 'Traditional Chinese dictionary differs from pre-expansion baseline: '+name
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
