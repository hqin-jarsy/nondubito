#!/usr/bin/env python3
"""Build a reversible, source-faithful review edition. No publication or source rewriting."""
from __future__ import annotations
import argparse, hashlib, html, json, re, stat, os
from collections import Counter
from urllib.parse import unquote,urlsplit
from pathlib import Path
from web_analytics import tracked_html

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/hongloumeng/first80"
TARGET=DATA/"generated/private-review"
EXPECTED="f02f667fed2473a6294a6e505d245e6120943061fe3b5e321a519f1b8dcf3dc3"
TITLE="大知校正庚辰版"
LABELS={"庚辰双行夹批","甲戌侧批","庚辰侧批","蒙侧批","甲戌双行夹批","庚辰眉批","甲戌眉批","蒙双行夹批","蒙回末总批","蒙回前总批","甲夹批","该批","蒙回末总评","蒙回后总评","己卯侧批","靖眉批","庚讲批","蒙回前总评","蒙回前诗","甲戌夹批","蒙回前批","脂批","靖侧批","庚辰旁批","庚辰批","庚辰夹批","甲眉","己双行夹批","蒙侧批；放笔痛骂一回","甲戌墨笔眉批（似非脂批","靖本眉批","前庚辰双行夹批","己卯眉批","蒙夹批","蒙回前词","郊批","辰夹批","庚辰该批","甲夹?"}
E=html.escape
def jread(path):return json.loads(path.read_text())
def digest(raw):return hashlib.sha256(raw).hexdigest()
def locations(s):
    ms=list(re.finditer(r"###第(\d+)回#####",s))
    assert [int(m[1]) for m in ms]==list(range(1,81))
    return ms
def locate(s,n,exact,start=None,end=None,context=None):
    ms=locations(s)
    if type(n) is not int or not 1<=n<=len(ms):
        raise ValueError(f"Invalid decision chapter: {n!r}")
    a,b=ms[n-1].end(),(ms[n].start() if n<len(ms) else len(s))
    if not isinstance(exact,str) or not exact:
        raise ValueError(f"Empty or invalid decision text in chapter {n}")
    if start is not None or end is not None:
        if type(start) is not int or type(end) is not int or not a<=start<end<=b:
            raise ValueError(f"Decision range outside chapter {n}: {start!r}:{end!r}")
        if s[start:end]!=exact:
            raise ValueError(f"Decision text mismatch in chapter {n}: {start}:{end}")
        return start,end
    matches=[m.start()+a for m in re.finditer(re.escape(exact),s[a:b])]
    if len(matches)!=1: raise ValueError(f"Ambiguous decision {n}: {exact[:60]} {matches}")
    return matches[0],matches[0]+len(exact)


def adopted_body_text(change):
    """Only the approved diagram uses LF as display boundaries rather than body characters."""
    proposed=change["proposed"]
    if "body_proposed" in change:return change["body_proposed"]
    if change.get("mode")=="replace_with_layout":
        if change["id"]!="P019":raise ValueError("Unregistered author-controlled layout change")
        if "\r" in proposed:raise ValueError("Unapproved line ending in diagram")
        adopted=proposed.replace("\n","")
        if Counter(adopted)!=Counter(change["original"]):raise ValueError("Diagram character multiset changed")
        if "崇" not in adopted or "祟" in adopted:raise ValueError("Diagram must retain approved 崇")
        return adopted
    if "\n" in proposed or "\r" in proposed:raise ValueError("Unapproved newline in prose replacement")
    return proposed

def author_layout_ranges(changes):
    ranges=[]
    for change in changes:
        if change.get("mode")!="replace_with_layout":continue
        lines=change["proposed"].split("\n");nonempty=[];groups=[];pending_group=True
        for line in lines:
            if not line:pending_group=True;continue
            if pending_group:groups.append(len(nonempty))
            nonempty.append(line);pending_group=False
        offsets=[];offset=0
        for line in nonempty[:-1]:
            offset+=len(line);offsets.append(offset)
        ranges.append(dict(id="A-"+change["id"],chapter=change["chapter"],kind="verse",
            start_char=change["source_start_char"],end_char=change["source_end_char"],
            exact_text=change["original"],exact_body_text=adopted_body_text(change),
            line_break_after_body_offsets=offsets,display_lines=nonempty,group_start_lines=groups,
            author_emendation_id=change["id"],author_emendation_ids=[change["id"]],
            authority="author_approved_replace_with_layout",
            derivation="Only U+000A LF characters are omitted from approved proposed text for body storage; each nonempty approved line is an independent display block. Empty lines mark group spacing.",
            source_mapping="covering_source_span"))
    return ranges

def layout_blocks(body, chars, generic_blocks, ranges, replacement_ends):
    """Cut final-body code points, never use source offsets to split emendations."""
    resolved=[]
    for r in ranges:
        exact=r["exact_body_text"]
        if not exact or body.count(exact)!=1:
            raise ValueError(f"Layout anchor must occur exactly once: {r['id']}")
        start=body.index(exact);end=start+len(exact)
        breaks=r["line_break_after_body_offsets"]
        if (any(type(x) is not int or not 0<x<len(exact) for x in breaks)
                or breaks!=sorted(set(breaks))):
            raise ValueError(f"Invalid layout line breaks: {r['id']}")
        resolved.append(dict(r,body_start=start,body_end=end))
    resolved.sort(key=lambda r:r["body_start"])
    for left,right in zip(resolved,resolved[1:]):
        if left["body_end"]>right["body_start"]:
            raise ValueError("Overlapping layout ranges")
    # Retain the old reading boundaries only outside explicitly reviewed ranges.
    cuts={0,len(body)};offset=0
    for block in generic_blocks:
        offset+=len(block["text"])
        if not any(r["body_start"]<offset<r["body_end"] for r in resolved):
            cuts.add(offset)
    for r in resolved:
        cuts.update((r["body_start"],r["body_end"]))
        cuts.update(r["body_start"]+x for x in r["line_break_after_body_offsets"])
    cuts=sorted(cuts);blocks=[]
    for start,end in zip(cuts,cuts[1:]):
        layout=next((r for r in resolved if r["body_start"]<=start<r["body_end"]),None)
        firstpos=chars[start][1];lastpos=chars[end-1][1]
        block=dict(start_char=firstpos,end_char=replacement_ends.get(lastpos,lastpos+1),
                   body_start=start,body_end=end,text=body[start:end],kind="prose")
        if layout:
            block.update(kind=layout["kind"],layout_id=layout["id"],
                         layout_first=start==layout["body_start"],layout_last=end==layout["body_end"])
            if "author_emendation_id" in layout:
                line_index=[layout["body_start"]]+[layout["body_start"]+x for x in layout["line_break_after_body_offsets"]]
                line_index=line_index.index(start)
                block.update(author_layout_id=layout["author_emendation_id"],author_layout_line=line_index,
                    author_layout_group_start=line_index in layout["group_start_lines"],
                    author_layout_heading=line_index in layout["group_start_lines"])
        blocks.append(block)
    assert "".join(b["text"] for b in blocks)==body
    return blocks,resolved

def cover_review_issues(s,reviews,chapters,issues,retained,edits,layout_deferred):
    """Preserve every original issue and record its explicit disposition."""
    records=[];seen=set()
    for filename,review in reviews:
        pools=[("issues",review.get("issues",[]))]
        pools += [(f"batches[{i}].issues",batch.get("issues",[])) for i,batch in enumerate(review.get("batches",[]))]
        for location,items in pools:
            for index,item in enumerate(items):
                signature=json.dumps(item,ensure_ascii=False,sort_keys=True)
                if signature in seen:continue
                seen.add(signature)
                records.append(dict(review_source=filename,review_location=f"{location}[{index}]",raw_issue=item))
    coverage=[];context=[]
    multi={"I0120-0027":["L03-014","L03-015"],
           "I0120-0048":[f"L05-{i:03d}" for i in range(37,50)],
           "I0120-0113":[f"L18-{i:03d}" for i in range(61,66)],
           "I0120-0114":[f"L18-{i:03d}" for i in range(66,70)]}
    for record in records:
        q=record["raw_issue"];ident=q.get("id",q.get("decision_id",record["review_source"]+":"+record["review_location"]))
        result=dict(review_id=ident,**record)
        if "start_char" not in q or "end_char" not in q:
            context.append(record);result.update(disposition="context_unresolved",context_index=len(context)-1)
            coverage.append(result);continue
        n=q["chapter"];a=q["start_char"];b=q["end_char"]
        locate(s,n,q["exact_text"],a,b)
        def containing(items):return next((i for i,x in enumerate(items) if x["chapter"]==n and x["start_char"]<=a<b<=x["end_char"]),None)
        found=containing(issues)
        if found is not None:result.update(disposition="issue",issue_index=found)
        elif (found:=containing(retained)) is not None:result.update(disposition="retained",retained_index=found)
        elif (found:=containing(edits)) is not None:result.update(disposition="archived_edit",edit_id=edits[found]["id"])
        else:
            ranges=chapters[n-1]["layout_ranges"]
            whole=[r["id"] for r in ranges if r["start_char"]<=a<b<=r["end_char"]]
            if whole:result.update(disposition="layout",layout_ids=whole)
            elif ident in multi:
                wanted=multi[ident];assert set(wanted)<={r["id"] for r in ranges}
                result.update(disposition="layout_with_preserved_narration",layout_ids=wanted)
            elif ident in ("I0120-0003","I0120-0026"):
                assert chapters[n-1]["body"].count(q["exact_text"])==1
                result.update(disposition="preserved_body",reason="原建议为保留叙事，已逐字保留；不据此认定版本问题终结。")
            elif q.get("severity")=="layout" or q.get("kind")=="poem_or_special_layout":
                deferred=dict(q,status="deferred_layout",review_issue_id=ident)
                layout_deferred.append(deferred)
                result.update(disposition="deferred_layout",deferred_index=len(layout_deferred)-1)
            else:
                issues.append(dict(chapter=n,start_char=a,end_char=b,text=q["exact_text"],
                    kind=q.get("kind","原始审查待核"),severity=q.get("severity","review"),
                    reason=q.get("reason",q.get("description","原始审查疑点，保留原文待核。")),review_issue_id=ident))
                result.update(disposition="issue",issue_index=len(issues)-1,added_from_raw_review=True)
        coverage.append(result)
    return coverage,context



def author_change_spans(chars,changes):
    spans=[]
    for change in changes:
        indices=[i for i,(_,pos) in enumerate(chars) if change["source_start_char"]<=pos<change["source_end_char"]]
        if not indices or indices!=list(range(indices[0],indices[-1]+1)):
            raise ValueError("Approved replacement has no contiguous body mapping")
        adopted="".join(chars[i][0] for i in indices)
        if adopted!=adopted_body_text(change):raise ValueError("Approved replacement body mapping mismatch")
        spans.append(dict(id=change["id"],source_start_char=change["source_start_char"],
            source_end_char=change["source_end_char"],body_start=indices[0],body_end=indices[-1]+1,
            adopted_body_sha256=digest(adopted.encode()),source_mapping="covering_source_span"))
    return spans

def retain_resolved_source_issues(s,issues,changes):
    records=[];by_id={x["id"]:x for x in changes}
    for name in ("author-resolved-source-issues.json","author-resolved-source-issues-supplement.json"):
        path=DATA/name;archive=jread(path)
        if archive["source_sha256"]!=EXPECTED:raise ValueError("Historical issue source checksum mismatch")
        snapshot_path=DATA/archive["snapshot_file"]
        if digest(snapshot_path.read_bytes())!=archive["snapshot_sha256"]:raise ValueError("Historical issue checkpoint changed")
        snapshot=jread(snapshot_path)
        for item in archive["issues"]:
            q=item["issue"];locate(s,q["chapter"],q["text"],q["start_char"],q["end_char"])
            if q not in snapshot["issues"]:raise ValueError("Historical issue is absent from its checkpoint")
            for ident in item["author_change_ids"]:
                if ident not in by_id:raise ValueError("Historical issue is not linked to an approved change")
                change=by_id[ident]
                if not change["source_start_char"]<q["end_char"] or not q["start_char"]<change["source_end_char"]:
                    raise ValueError("Historical issue does not overlap approved change")
            key=lambda x:(x["chapter"],x["start_char"],x["end_char"],x["text"],x["kind"])
            if not any(key(x)==key(q) for x in issues):
                issues.append(dict(q,historical_source_issue=True,issue_checkpoint=archive["snapshot_file"]))
        records.append(dict(path=path.name,sha256=digest(path.read_bytes()),snapshot_sha256=archive["snapshot_sha256"],issue_count=len(archive["issues"])))
    return dict(records[0],supplements=records[1:],total_archived_issues=sum(r["issue_count"] for r in records))

def review_body_checkpoint(body,expected_sha256,author_changes,spans):
    """Reconcile read snapshots by exact adopted body ranges, including repeated phrases."""
    if digest(body.encode())==expected_sha256:return []
    by_id={x["id"]:x for x in author_changes}
    for cutoff in range(len(author_changes)-1,-1,-1):
        ids={x["id"] for x in author_changes[cutoff:]}
        restored=body
        for span in sorted((x for x in spans if x["id"] in ids),key=lambda x:x["body_start"],reverse=True):
            change=by_id[span["id"]];a,z=span["body_start"],span["body_end"]
            if restored[a:z]!=adopted_body_text(change):raise ValueError("Review snapshot body span mismatch")
            restored=restored[:a]+change["original"]+restored[z:]
        if digest(restored.encode())==expected_sha256:return [x["id"] for x in author_changes[cutoff:]]
    raise ValueError("Supplemental review body snapshot does not match approved history")

def supplemental_review_issues(s,chapters,issues):
    """Index source-bounded candidates separately from the four original reviews."""
    provenance=[];coverage=[];ids=set()
    names=("prose_supplement_01_20.json","prose_supplement_61_80.json")
    for filename in names:
        path=DATA/"reviews"/filename;review=jread(path)
        if review.get("source_sha256")!=EXPECTED:raise ValueError("Supplemental source checksum mismatch")
        early=filename==names[0]
        findings=review["findings" if early else "new_findings"]
        expected_chapters=list(range(1,21)) if early else list(range(61,81))
        if early and review["status"]!="supplementary_full_body_read_completed_not_facsimile_collation":
            raise ValueError("Supplemental review is not complete")
        logs=review["chapter_logs"] if early else [c for b in review["batches"] for c in b["chapters"]]
        if [q["chapter"] for q in logs]!=expected_chapters:raise ValueError("Incomplete supplemental chapter logs")
        chapter_logs=[]
        for q in logs:
            c=chapters[q["chapter"]-1]
            expected=q["body_sha256_at_dedup"] if early else q["body_sha256_at_final_validation"]
            reversed_ids=review_body_checkpoint(c["body"],expected,c["author_changes"],c["author_change_spans"])
            chapter_logs.append(dict(chapter=q["chapter"],verified_body_sha256=expected,
                reconciled_later_author_change_ids=reversed_ids,
                read_body_characters=q["read_body_end"] if early else q["unicode_characters_including_punctuation"],
                read_body_sha256=q.get("read_body_sha256"),
                original_source_range=[c["source_start"],c["source_end"]]))
        batches=[]
        for b in review["batches"]:
            nums=b["chapters"] if early else [c["chapter"] for c in b["chapters"]]
            batches.append(dict(batch_id=b["batch_id"],chapters=nums,
                body_characters_read=b["body_characters_read"] if early else b["total_unicode_characters"],
                method=b.get("coverage","逐回完整净正文通读，含叙事、对话、诗词与保留材料。"),
                limitations=b["limitations"]))
        limits=review["limitations"] if early else [
            "净正文通读及源坐标验证；没有逐字核对古抄影印，也不保证穷尽脱漏。",
            "初读模型未留字节快照，不能声称完成首尾结构差异核验或全程阅读单一冻结模型。",
            "终验逐回正文字符数及SHA256已记录并再次校验；单靠等长字符数不能排除读程中的字词变化。"]
        provenance.append(dict(review_source=filename,review_sha256=digest(path.read_bytes()),
            source_sha256=EXPECTED,review_type="supplemental_clean_body_readthrough",
            finding_count=len(findings),chapters=expected_chapters,batches=batches,chapter_logs=chapter_logs,
            limitations=limits,publication_ready=False,
            snapshot_scope=("早期通读快照与后续批准文字已用逐项逆替换及哈希核验。" if early else
                            "仅有记录的初读输出、最终逐回正文哈希及候选复核；无初读模型字节快照。")))
        for q in findings:
            ident=q["id"]
            if ident in ids:raise ValueError("Duplicate supplemental finding ID")
            ids.add(ident)
            a=q.get("source_start",q.get("source_start_char"));b=q.get("source_end",q.get("source_end_char"))
            n=q["chapter"];exact=q["exact_source_text"]
            locate(s,n,exact,a,b)
            if n not in expected_chapters:raise ValueError("Supplemental finding outside declared chapter scope")
            if q.get("applied",False) or q.get("proposed_replacement") is not None:
                raise ValueError("Supplemental findings are annotations, not approved replacements")
            confidence=q["confidence"]
            if confidence not in ("high","medium","low") and not (type(confidence) in (int,float) and 0<=confidence<=1):
                raise ValueError("Invalid supplemental confidence")
            existing=next((i for i,x in enumerate(issues) if (x["chapter"],x["start_char"],x["end_char"],x["text"])==(n,a,b,exact)),None)
            provenance_item=dict(id=ident,review_source=filename,review_sha256=provenance[-1]["review_sha256"],
                confidence=confidence,original_status=q["status"])
            if existing is None:
                issue=dict(chapter=n,start_char=a,end_char=b,text=exact,kind="待校",
                    severity="review",reason=q["reason"],confidence=confidence,
                    original_kind=q.get("kind"),status="pending_source_verification",applied=False,
                    review_issue_id=ident,review_source=filename,
                    clean_excerpt=q["clean_excerpt"],context_before=q["context_before"],context_after=q["context_after"],
                    recommendation=q["recommendation"],supplemental_reviews=[provenance_item])
                if confidence=="medium":
                    issue["reason"]="中置信待校，尚未认定为错字。"+issue["reason"]
                issues.append(issue);existing=len(issues)-1
                disposition="new_issue"
            else:
                issues[existing].setdefault("supplemental_reviews",[]).append(provenance_item)
                disposition="existing_exact_range_issue"
            overlaps=[i for i,x in enumerate(issues) if i!=existing and x["chapter"]==n and x["start_char"]<b and a<x["end_char"]]
            coverage.append(dict(**provenance_item,chapter=n,start_char=a,end_char=b,exact_source_text=exact,
                disposition=disposition,issue_index=existing,overlapping_issue_indices=overlaps))
    return provenance,coverage

def public_review_batches(m):
    """Summaries plus evidence hashes, not duplicate raw decision payloads."""
    summaries=[]
    methods={
        "review_01_20.json":("括注逐条审查及正文风险区域定向阅读。","初轮未完整通读所有普通正文；另有独立补充通读记录。"),
        "review_21_40.json":("去批候选正文逐回连续阅读；全部括注定位，截断段落补读。","未核独立古抄影印，疑点不作自动改字。"),
        "review_41_60.json":("全部括注逐项审查；41–60回候选正文通读并补足截断段落。","未核独立古抄影印或程高本，不保证穷尽OCR错误。"),
        "review_61_80.json":("全部括注和检索命中逐项审查，正文开中尾及诗词接缝定向抽读。","初轮未逐句通读所有普通正文；另有独立补充通读记录。")}
    decisions=jread(DATA/"review-decisions.json")
    for path in sorted((DATA/"reviews").glob("review_*.json")):
        review=jread(path);method,limits=methods[path.name]
        for batch in review["batches"]:
            ns=batch["chapters"];local=[d for d in decisions if d["chapter"] in ns]
            action_counts={action:sum(d["action"]==action for d in local) for action in sorted({d["action"] for d in local})}
            summaries.append(dict(batch_id=f"{min(ns):02d}-{max(ns):02d}",chapters=ns,
                review_source=path.name,review_sha256=digest(path.read_bytes()),method=method,limitations=limits,
                canonical_decision_count=len(local),canonical_decisions_by_action=action_counts,
                emitted_removal_count=sum(e["chapter"] in ns for e in m["edits"]),
                current_issue_count=sum(q["chapter"] in ns for q in m["issues"]),
                publication_ready=False))
    return summaries

def supplemental_note_provenance(q):
    refs=q.get("supplemental_reviews",[])
    if not refs:return ""
    return " 补充审读："+ "；".join(x["id"]+"（原置信度 "+str(x["confidence"])+"，待校）" for x in refs)

def public_provenance(value):
    """Project local evidence metadata into shareable source identities."""
    if isinstance(value,list):return [public_provenance(item) for item in value]
    if isinstance(value,dict):
        if "file_path" in value:
            return {"file_name":Path(value["file_path"]).name,"sha256":value["sha256"]}
        return {key:public_provenance(item) for key,item in value.items()}
    if isinstance(value,str):
        if value.startswith("file://"):
            u=urlsplit(value);return unquote(Path(u.path).name)+("#"+u.fragment if u.fragment else "")
        if value.startswith(("/Users/","/tmp/")):return Path(value).name
    return value

def correction_reference(change,batches):
    if change.get("authorization_type")=="explicit_author_edition_choice":return "作者明确指定本版回末收束句；原TXT保留，不宣称古本复原。"
    if change.get("authorization_type")=="delegated_public_transcription_selection":
        return change["reason"]+" 公开转录："+ "；".join(q["url"] for q in change["public_references"])+"；未核古本影印，不宣称唯一原稿。"
    if change.get("authorization_type") in ("author_explicit_six_source_decision","author_explicit_seven_source_decision","author_explicit_chapter24_source_decision","author_explicit_chapter28_source_decision"):
        return "作者明确同意，参考公开转录作可读性补校；非古本影印校勘。"
    if change.get("authorization_type")=="author_explicit_tail_lacuna_decision":
        return "作者明确选择；"+change["reason"]
    if change.get("authorization_type")=="user_delegated_readability_selection":
        q=change["decision_record"];pages=[]
        if "base_pdf_physical_page" in q:pages.append(f'底本PDF物理第{q["base_pdf_physical_page"]}页')
        if "comparison_pdf_physical_page" in q:pages.append(f'现代参校PDF物理第{q["comparison_pdf_physical_page"]}页')
        return "用户委托按可读性选择；"+q["classification"]+"。"+"；".join(pages)+"。具体来源与证据限制见绑定决定记录，不将本版推定称为原本复原。"

    batch=next(b for b in batches if change["id"] in b["change_ids"])
    if batch["id"]=="batch01":
        return f'第一批；对照：所存维基文库通行本PDF第{"/".join(map(str,change["pdf_pages"]))}页；不是已核程甲/程乙影印本。'
    label={"batch02":"第二批","batch03":"第三批","batch04":"第四批","batch05":"第五批","batch06":"第六批","batch07":"第七批","batch08":"第八批","batch09":"第九批","batch10":"第十批","batch11":"第十一批","batch12":"第十二批","batch13":"第十三批","batch14":"第十四批","batch15":"第十五批","batch16":"第十六批"}[batch["id"]]
    base_pages=change.get("base_pdf_physical_pages",[change["base_pdf_physical_page"]])
    common=(f'{label}；脂批汇校PDF物理第{"/".join(map(str,base_pages))}页；'
            f'所存维基文库通行本PDF物理第{change["comparison_pdf_physical_page"]}页。')
    if batch["id"]=="batch02":
        return common+f'程甲本对应页仅核转录，古本影印图像尚未目验：{change["chengjia_reference"]["page_url"]}。'
    if batch["id"]=="batch03":
        ref=change["chengjia_reference"]
        return common+f'本地PDF图像已目验；程甲本仅核章节转录，未核古本影印图像：{ref["chapter_url"]}。'+ref["page_note"]
    return common+'本批仅核两份本地PDF图像；未核程甲转录或古本影印，不将其列为本批已核证据。'

def correction_adopted_html(change):
    if change.get("mode")=="replace_with_layout":
        return E(change["proposed"]).replace("\n","<br>")+ '<p>仅按作者确认的字序横排分行，保留“崇”。换行是显示边界，不计入净正文字符数；不是古抄图像复原。</p>'
    return E(change["proposed"])


def reading_policy(s):
    path=DATA/"author-reading-policy.json";policy=jread(path)
    packet_path=DATA/policy["proposal_file"];packet=jread(packet_path)
    if policy["status"]!="author_confirmed" or policy["source_sha256"]!=EXPECTED:
        raise ValueError("Reading policy is not bound to approved source")
    if digest(packet_path.read_bytes())!=policy["proposal_sha256"]:raise ValueError("Reading boundary packet hash mismatch")
    reference=next(g["items"] for g in packet["groups"] if g["id"]=="VC")
    if [x["id"] for x in policy["exclusions"]]!=[x["id"] for x in reference]:
        raise ValueError("Reading policy does not match approved VC scope")
    for actual,original in zip(policy["exclusions"],reference):
        for key in ("id","chapter","source_start_char","source_end_char","exact_original"):
            if actual[key]!=original[key]:raise ValueError("Changed reading exclusion boundary")
        if actual["action"]!="exclude_prefatory_material":raise ValueError("Unexpected reading action")
        locate(s,actual["chapter"],actual["exact_original"],actual["source_start_char"],actual["source_end_char"])
    return policy

def classify_excluded_layouts(ranges,exclusions):
    kept=[];excluded=[]
    for r in ranges:
        hits=[q for q in exclusions if q["source_start_char"]<r["end_char"] and r["start_char"]<q["source_end_char"]]
        if not hits:kept.append(r);continue
        if len(hits)!=1 or not hits[0]["source_start_char"]<=r["start_char"]<r["end_char"]<=hits[0]["source_end_char"]:
            raise ValueError("Partial reading-policy overlap with layout: "+r["id"])
        excluded.append(dict(r,excluded_by=hits[0]["id"],status="excluded_by_author_reading_scope"))
    return kept,excluded

def apply_reading_scope(m,s):
    policy=reading_policy(s);exclusions=policy["exclusions"];archived=[]
    original_retained={(q["start_char"],q["end_char"]):q for q in m["retained"]}
    for q in exclusions:
        a=q["source_start_char"];b=q["source_end_char"]
        if (a,b) not in original_retained:raise ValueError("Reading exclusion is not an intact retained unit")
        if any(e["start_char"]<b and a<e["end_char"] for e in m["edits"]):
            raise ValueError("Reading exclusion overlaps an existing removal")
        if any(x["source_start_char"]<b and a<x["source_end_char"] for x in m["author_emendations"]):
            raise ValueError("Reading exclusion overlaps approved changed text")
        archived.append(dict(id="READ-"+q["id"],reading_policy_id=q["id"],chapter=q["chapter"],
            start_char=a,end_char=b,exact_text=q["exact_original"],action=q["action"],reason=q["reason"]))
    excluded_layouts=[]
    for c in m["chapters"]:
        local=[q for q in exclusions if q["chapter"]==c["number"]]
        c["body_before_reading_exclusions_sha256"]=c["body_sha256"]
        c["reading_exclusions"]=[q["id"] for q in local]
        c["excluded_layout_ids"]=[]
        if not local:continue
        start,end=c["body_start"],c["source_end"]
        removed=set()
        for e in c["edits"]:removed.update(range(e["start_char"],e["end_char"]))
        chars=[(s[pos],pos) for pos in range(start,end) if pos not in removed]
        replacement_ends={}
        for change in sorted(c["author_changes"],key=lambda x:x["source_start_char"],reverse=True):
            a,b=change["source_start_char"],change["source_end_char"]
            indices=[i for i,(_,pos) in enumerate(chars) if a<=pos<b]
            if "".join(chars[i][0] for i in indices)!=change["original"]:raise ValueError("Reading replay lost original change")
            chars[indices[0]:indices[-1]+1]=[(ch,a) for ch in adopted_body_text(change)];replacement_ends[a]=b
        if "".join(ch for ch,pos in chars)!=c["body"]:raise ValueError("Reading replay differs from approved body")
        excluded_positions=set()
        for q in local:excluded_positions.update(range(q["source_start_char"],q["source_end_char"]))
        generic=[]
        for block in c["blocks"]:
            text="".join(ch for ch,pos in chars[block["body_start"]:block["body_end"]] if pos not in excluded_positions)
            if text:generic.append(dict(text=text))
        chars=[(ch,pos) for ch,pos in chars if pos not in excluded_positions]
        body="".join(ch for ch,pos in chars)
        c["author_change_spans"]=author_change_spans(chars,c["author_changes"])
        kept,removed_ranges=classify_excluded_layouts(c["layout_ranges"],local)
        excluded_layouts+=removed_ranges;c["excluded_layout_ids"]=[r["id"] for r in removed_ranges]
        blocks,resolved=layout_blocks(body,chars,generic,kept+c["author_layout_ranges"],replacement_ends)
        for block in blocks:
            block["source_mapping"]="covering_source_span"
            block["author_change_ids"]=[x["id"] for x in c["author_changes"] if block["start_char"]<x["source_end_char"] and x["source_start_char"]<block["end_char"]]
        for q in local:
            if c["base_body"].count(q["exact_original"])!=1:raise ValueError("Reading exclusion is not unique in chapter")
            c["base_body"]=c["base_body"].replace(q["exact_original"],"",1)
        c.update(body=body,body_sha256=digest(body.encode()),blocks=blocks,
            layout_ranges=[r for r in resolved if "author_emendation_id" not in r],
            author_layout_ranges=[r for r in resolved if "author_emendation_id" in r])
        c["edits"]=sorted(c["edits"]+[e for e in archived if e["chapter"]==c["number"]],key=lambda e:e["start_char"])
    m["edits"]=sorted(m["edits"]+archived,key=lambda e:e["start_char"])
    keys={(q["source_start_char"],q["source_end_char"]) for q in exclusions}
    m["retained"]=[q for q in m["retained"] if (q["start_char"],q["end_char"]) not in keys]
    for issue in m["issues"]:
        hits=[q for q in exclusions if q["source_start_char"]<issue["end_char"] and issue["start_char"]<q["source_end_char"]]
        if hits:
            issue["excluded_by_reading_policy"]=[q["id"] for q in hits]
            issue["reading_status"]="historical_source_material_excluded_from_reading"
            issue["reading_resolution_note"]="原审查记录留存；相关回前材料依作者阅读范围决定排除，不作当前正文缺陷。"
    for c in m["chapters"]:c["retained"]=[q for q in m["retained"] if q["chapter"]==c["number"]]
    m["reading_policy"]=dict(policy,path="author-reading-policy.json",sha256=digest((DATA/"author-reading-policy.json").read_bytes()))
    m["excluded_layouts"]=excluded_layouts;m["excluded_layout_ids"]=[r["id"] for r in excluded_layouts]
    m["layout_provenance"]["active_ranges"]=sum(len(c["layout_ranges"]) for c in m["chapters"])
    for record in m["raw_issue_coverage"]:
        if any(x in m["excluded_layout_ids"] for x in record.get("layout_ids",[])):
            record["original_disposition"]=record["disposition"]
            record["disposition"]="excluded_by_reading_policy"
    return m

def archive_previous_public_materials():
    """Move superseded generated attachments to local records, never delete evidence."""
    paths=[TARGET/"preface.html"]+sorted((TARGET/"audit").glob("*"))
    for p in paths:
        if not p.exists():continue
        if p.is_symlink() or not p.is_file():raise ValueError("Unexpected archive target")
        if p.parent.name=="audit" and not re.fullmatch(r"ch\d{3}\.json|edition-manifest\.json|raw-issue-coverage\.json|supplemental-issue-coverage\.json",p.name):
            raise ValueError("Unexpected file in generated audit folder: "+p.name)
        relative=p.relative_to(TARGET)
        dest=DATA/"archived-public/before-reading-policy"/relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        raw=p.read_bytes()
        if dest.exists() and dest.read_bytes()!=raw:raise ValueError("Archive checkpoint already differs")
        if not dest.exists():dest.write_bytes(raw)
        if dest.read_bytes()!=raw:raise ValueError("Archive copy verification failed")
        # A verified equivalent copy remains in the local evidence archive.
        p.unlink()

def verify_coverage_metadata_correction(batch,packet):
    """Bind a review-statistics correction without editing the approved literary packet."""
    binding=batch.get("coverage_metadata_correction")
    if batch["id"]=="batch11" and not binding:
        raise ValueError("Batch11 requires its separate coverage metadata correction")
    if not binding:return
    filename=binding["file"]
    if batch["id"]!="batch11" or filename!="author-review-batch11.metadata-correction.json":
        raise ValueError("Unexpected review coverage correction")
    path=DATA/filename;fix=jread(path)
    if digest(path.read_bytes())!=binding["sha256"] or binding["scope"]!="coverage_only":
        raise ValueError("Review coverage correction hash or scope mismatch")
    if fix["record_type"]!="review_coverage_metadata_correction" or fix["batch"]!=11:
        raise ValueError("Wrong review coverage correction identity")
    if fix["original_record"]["sha256"]!=batch["proposal_sha256"] or fix["original_coverage"]!=packet["coverage"]:
        raise ValueError("Review coverage correction is not bound to this original packet")
    if fix["evidence_source"]["normalized_source_sha256"]!=EXPECTED:
        raise ValueError("Review coverage correction source mismatch")
    if binding["effective_coverage"]!=fix["corrected_coverage"]:
        raise ValueError("Changed effective review coverage")
    if fix["corrected_coverage"]["proposed_loci"]!=len(packet["proposals"]):
        raise ValueError("Review coverage proposal count mismatch")
    attachment=DATA/Path(fix["original_author_attachment"]["path"]).name
    if digest(attachment.read_bytes())!=fix["original_author_attachment"]["sha256"]:
        raise ValueError("Original author attachment changed")


def verify_approval_delivery(batch,packet):
    if batch["id"] not in {"batch14","batch15","batch16"}:return
    binding=batch.get("delivery_evidence")
    if not binding or binding["manifest_file"]!="deliverables/review14-16/delivery-manifest.json":
        raise ValueError("Missing approved attachment delivery evidence")
    path=DATA/binding["manifest_file"]
    if digest(path.read_bytes())!=binding["manifest_sha256"]:
        raise ValueError("Approved attachment delivery manifest changed")
    manifest=jread(path);n=int(batch["id"][5:])
    entry=next(x for x in manifest["files"] if x["batch"]==n)
    if entry["original_json_sha256"]!=batch["proposal_sha256"] or binding["proposal_count"]!=len(packet["proposals"]):
        raise ValueError("Approved delivery proposal identity changed")
    for key,sha_key,entry_key in (("original_attachment","original_attachment_sha256","original_path"),("delivered_attachment","delivered_attachment_sha256","delivery_path")):
        name=binding[key]
        if name!=entry[entry_key] or digest((DATA/name).read_bytes())!=binding[sha_key]:
            raise ValueError("Approved author attachment changed")
    original=(DATA/entry["original_path"]).read_bytes();derived=original
    for change in sorted(entry["display_only_changes"],key=lambda x:x["original_byte_offset"],reverse=True):
        a=change["original_byte_offset"];before=change["old_text"].encode();after=change["new_text"].encode()
        if derived[a:a+len(before)]!=before:raise ValueError("Delivery presentation change has wrong source bytes")
        derived=derived[:a]+after+derived[a+len(before):]
    if derived!=(DATA/entry["delivery_path"]).read_bytes():
        raise ValueError("Delivery has changes beyond disclosed presentation edits")


def apply_author_layout_anchor_overrides(ranges,changes,s):
    path=DATA/"author-layout-anchor-overrides.json";config=jread(path)
    if config["source_sha256"]!=EXPECTED:raise ValueError("Author layout override source changed")
    result=[dict(r) for r in ranges];ids=set()
    for item in config["overrides"]:
        ident=item["id"]
        if ident in ids:raise ValueError("Duplicate author layout override")
        ids.add(ident)
        matches=[r for r in result if r["id"]==ident]
        if len(matches)!=1:raise ValueError("Unknown author layout override")
        r=matches[0];manifest_path=DATA/item["manifest_file"]
        if item["manifest_file"] not in {"layout-ranges.json","layout-supplement.json","layout-supplement02.json"} or digest(manifest_path.read_bytes())!=item["manifest_sha256"]:
            raise ValueError("Original layout manifest changed")
        original=next(x for x in jread(manifest_path)["ranges"] if x["id"]==ident)
        if original!=r:raise ValueError("Layout override applied to an already modified range")
        if (r["chapter"],r["start_char"],r["end_char"],r["exact_text"],r["exact_body_text"],r["line_break_after_body_offsets"])!=(item["chapter"],item["source_start_char"],item["source_end_char"],item["source_exact_text"],item["original_exact_body_text"],item["original_line_break_after_body_offsets"]):
            raise ValueError("Layout override anchor differs from its manifest")
        if r["exact_body_text"]!=r["exact_text"] or s[r["start_char"]:r["end_char"]]!=r["exact_text"]:
            raise ValueError("This override requires an unchanged source-to-body anchor")
        hits=[x for x in changes if x["source_start_char"]<r["end_char"] and r["start_char"]<x["source_end_char"]]
        if [x["id"] for x in hits]!=item["author_change_ids"]:
            raise ValueError("Layout override does not cover exactly its approved intersections")
        text=r["exact_body_text"];breaks=list(r["line_break_after_body_offsets"])
        for x in sorted(hits,key=lambda x:x["source_start_char"],reverse=True):
            if not r["start_char"]<=x["source_start_char"]<x["source_end_char"]<=r["end_char"]:
                raise ValueError("Partial author/layout source overlap")
            a,z=x["source_start_char"]-r["start_char"],x["source_end_char"]-r["start_char"]
            if text[a:z]!=x["original"]:raise ValueError("Layout override original mismatch")
            if any(a<b<z for b in breaks):raise ValueError("Author change crosses a controlled line break")
            adopted=adopted_body_text(x);delta=len(adopted)-(z-a)
            text=text[:a]+adopted+text[z:];breaks=[b+delta if b>=z else b for b in breaks]
        if text!=item["derived_exact_body_text"] or breaks!=item["derived_line_break_after_body_offsets"]:
            raise ValueError("Layout override contains unapproved text or line changes")
        r.update(exact_body_text=text,line_break_after_body_offsets=breaks,
            author_emendation_ids=sorted(set(r.get("author_emendation_ids",[])+item["author_change_ids"])),
            author_anchor_override=dict(file=path.name,sha256=digest(path.read_bytes()),author_change_ids=item["author_change_ids"],
                original_exact_body_text=item["original_exact_body_text"],original_line_break_after_body_offsets=item["original_line_break_after_body_offsets"],
                derivation=item["derivation"]),anchor_status="derived_from_author_approved_replacement")
    return result,dict(file=path.name,sha256=digest(path.read_bytes()),override_count=len(ids),overridden_ids=sorted(ids))


def editorial_note_policy(s):
    path=DATA/"author-reading-policy-editorial-notes.json";policy=jread(path)
    if policy["source_sha256"]!=EXPECTED or policy["status"]!="author_confirmed_principle_applied_after_individual_classification":
        raise ValueError("Unconfirmed editorial-note reading policy")
    if policy["action"]!="exclude_editorial_note":
        raise ValueError("Unexpected editorial-note action")
    if policy["classification_file"]!="editorial-note-classification.json":
        raise ValueError("Unexpected editorial-note classification file")
    classification_path=DATA/policy["classification_file"];classification=jread(classification_path)
    if digest(classification_path.read_bytes())!=policy["classification_sha256"]:
        raise ValueError("Editorial-note classification hash mismatch")
    if classification["source_sha256"]!=EXPECTED:
        raise ValueError("Editorial-note classification source mismatch")
    if policy["original_reading_policy_file"]!="author-reading-policy.json" or digest((DATA/"author-reading-policy.json").read_bytes())!=policy["original_reading_policy_sha256"]:
        raise ValueError("Original prefatory policy changed")
    baseline_path=DATA/classification["baseline_model_file"]
    if classification["baseline_model_file"]!="qa/before-editorial-note-policy.model.json" or digest(baseline_path.read_bytes())!=classification["baseline_model_sha256"]:
        raise ValueError("Editorial-note baseline changed")
    baseline=jread(baseline_path)
    exclusions=policy["exclusions"];records=classification["records"]
    if len(exclusions)!=policy["count"] or policy["count"]!=6 or len(records)!=6:
        raise ValueError("Editorial-note exclusion scope must contain six records")
    if [q["id"] for q in exclusions]!=[f"EN{i:02d}" for i in range(1,7)]:
        raise ValueError("Editorial-note exclusion identities changed")
    previous=-1
    for q,record in zip(exclusions,records):
        if {k:v for k,v in q.items() if k!="action"}!=record or q["action"]!="exclude_editorial_note":
            raise ValueError("Unreviewed editorial-note exclusion")
        if q["classification"]!="editorial_comment_on_text" or q["classification_basis"]!="wording_and_narrative_context_not_parentheses_alone":
            raise ValueError("Missing contextual editorial-note classification")
        a,b=locate(s,q["chapter"],q["exact_original"],q["source_start_char"],q["source_end_char"])
        if a<previous:raise ValueError("Overlapping editorial-note exclusions")
        previous=b
        if s[a-len(q["context_before"]):a]!=q["context_before"] or s[b:b+len(q["context_after"])]!=q["context_after"]:
            raise ValueError("Editorial-note source context mismatch")
        c=baseline["chapters"][q["chapter"]-1];x,y=q["baseline_body_start"],q["baseline_body_end"]
        if c["body"][x:y]!=q["exact_original"]:
            raise ValueError("Editorial-note baseline location mismatch")
    if sum(len(q["exact_original"]) for q in exclusions)!=policy["excluded_codepoints"] or policy["excluded_codepoints"]!=63:
        raise ValueError("Editorial-note removal length mismatch")
    return policy


def apply_editorial_note_scope(m,s):
    policy=editorial_note_policy(s);exclusions=policy["exclusions"];archived=[]
    for q in exclusions:
        a,b=q["source_start_char"],q["source_end_char"]
        if any(e["start_char"]<b and a<e["end_char"] for e in m["edits"]):
            raise ValueError("Editorial-note exclusion overlaps an existing removal")
        if any(x["source_start_char"]<b and a<x["source_end_char"] for x in m["author_emendations"]):
            raise ValueError("Editorial-note exclusion overlaps an approved word change")
        c=m["chapters"][q["chapter"]-1]
        if any(r["start_char"]<b and a<r["end_char"] for r in c["layout_ranges"]+c["author_layout_ranges"]):
            raise ValueError("Editorial-note exclusion overlaps a controlled layout range")
        archived.append(dict(id="READ-"+q["id"],reading_policy_id=q["id"],policy_source="author-reading-policy-editorial-notes.json",
            chapter=q["chapter"],start_char=a,end_char=b,exact_text=q["exact_original"],action=q["action"],reason=q["reason"]))
    for c in m["chapters"]:
        local=[q for q in exclusions if q["chapter"]==c["number"]]
        if not local:continue
        c["body_before_editorial_note_exclusions_sha256"]=c["body_sha256"]
        removed=set()
        for e in c["edits"]:removed.update(range(e["start_char"],e["end_char"]))
        base_chars=[(s[pos],pos) for pos in range(c["body_start"],c["source_end"]) if pos not in removed]
        if "".join(ch for ch,pos in base_chars)!=c["base_body"]:
            raise ValueError("Editorial-note replay lost the uncorrected body")
        chars=list(base_chars);replacement_ends={}
        for x in sorted(c["author_changes"],key=lambda x:x["source_start_char"],reverse=True):
            a,b=x["source_start_char"],x["source_end_char"];indices=[i for i,(_,pos) in enumerate(chars) if a<=pos<b]
            if not indices or "".join(chars[i][0] for i in indices)!=x["original"]:
                raise ValueError("Editorial-note replay lost an approved original")
            chars[indices[0]:indices[-1]+1]=[(ch,a) for ch in adopted_body_text(x)];replacement_ends[a]=b
        if "".join(ch for ch,pos in chars)!=c["body"]:
            raise ValueError("Editorial-note replay differs from the approved body")
        excluded_positions={pos for q in local for pos in range(q["source_start_char"],q["source_end_char"])}
        inverse=[]
        for q in local:
            a,b=q["source_start_char"],q["source_end_char"];indices=[i for i,(_,pos) in enumerate(chars) if a<=pos<b]
            if not indices or indices!=list(range(indices[0],indices[-1]+1)) or "".join(chars[i][0] for i in indices)!=q["exact_original"]:
                raise ValueError("Editorial-note source interval is not intact in reading text")
            inverse.append(dict(id=q["id"],source_start_char=a,source_end_char=b,
                body_start_before_exclusion=indices[0],body_end_before_exclusion=indices[-1]+1,
                body_insertion_offset=sum(pos<a and pos not in excluded_positions for ch,pos in chars),
                exact_original=q["exact_original"]))
        generic=[]
        for block in c["blocks"]:
            text="".join(ch for ch,pos in chars[block["body_start"]:block["body_end"]] if pos not in excluded_positions)
            if text:generic.append(dict(text=text))
        chars=[(ch,pos) for ch,pos in chars if pos not in excluded_positions]
        body="".join(ch for ch,pos in chars)
        blocks,resolved=layout_blocks(body,chars,generic,c["layout_ranges"]+c["author_layout_ranges"],replacement_ends)
        for block in blocks:
            block["source_mapping"]="covering_source_span"
            block["author_change_ids"]=[x["id"] for x in c["author_changes"] if block["start_char"]<x["source_end_char"] and x["source_start_char"]<block["end_char"]]
        c.update(body=body,base_body="".join(ch for ch,pos in base_chars if pos not in excluded_positions),
            body_sha256=digest(body.encode()),blocks=blocks,author_change_spans=author_change_spans(chars,c["author_changes"]),
            layout_ranges=[r for r in resolved if "author_emendation_id" not in r],
            author_layout_ranges=[r for r in resolved if "author_emendation_id" in r],
            editorial_note_exclusions=[q["id"] for q in local],editorial_note_exclusion_spans=inverse)
        c["edits"]=sorted(c["edits"]+[e for e in archived if e["chapter"]==c["number"]],key=lambda e:e["start_char"])
    m["edits"]=sorted(m["edits"]+archived,key=lambda e:e["start_char"])
    for issue in m["issues"]:
        hits=[q["id"] for q in exclusions if q["source_start_char"]<issue["end_char"] and issue["start_char"]<q["source_end_char"]]
        if hits:
            issue["excluded_by_editorial_note_policy"]=hits
            issue["reading_status"]="historical_editorial_note_excluded_from_reading"
            issue["reading_resolution_note"]="原编辑按语及既有疑缺判断保留为历史证据；按只留正文原则排除其阅读展示，不表示缺文已补、已证实或已消失。正文原有省略号、缺字符号及邻接标点不改。"
    for c in m["chapters"]:c["issues"]=[q for q in m["issues"] if q["chapter"]==c["number"]]
    m["editorial_note_policy"]=dict(policy,path="author-reading-policy-editorial-notes.json",sha256=digest((DATA/"author-reading-policy-editorial-notes.json").read_bytes()))
    m["reading_exclusion_summary"]=dict(prefatory_units=len(m["reading_policy"]["exclusions"]),editorial_notes=len(exclusions),
        total_units=len(m["reading_policy"]["exclusions"])+len(exclusions),
        excluded_codepoints=sum(len(q["exact_original"]) for q in m["reading_policy"]["exclusions"]+exclusions))
    return m



READABLE_DECISIONS_SHA256="4b1f42c2a44f550065948d31f14bc055a1f70d46f68ac8500f5afa86fe7d6559"
READABLE_BASELINE_SHA256="60f2d302438ea4ee82614dc726628825202d13bd315129fed35527a22579ba4c"

def readable_projected_text(text,start,excluded):
    """Remove only individually bound source intervals, never bracket-pattern stripping."""
    result=text
    for e in sorted(excluded,key=lambda x:x["start_char"],reverse=True):
        a,b=e["start_char"]-start,e["end_char"]-start
        if not 0<=a<b<=len(text) or text[a:b]!=e["exact_text"]:
            raise ValueError("Readable projection changed excluded source text")
        result=result[:a]+result[b:]
    return result

def readable_expected_operations(record,edits):
    """A semantic record can have several exact source operations without inflating its count."""
    ident=record["decision_id"];a,b=record["source_start_char"],record["source_end_char"]
    original,final=record["original"],record["final"]
    hits=[e for e in edits if e["start_char"]<b and a<e["end_char"]]
    if record["source_record_id"]=="B18-017":
        if len(original)!=439 or len(final)!=439 or len(hits)!=6:
            raise ValueError("B18-017 parent length or removal count changed")
        if [e["id"] for e in hits]!=["E2207","E2208","E2209","E2210","E2211","E2212"]:
            raise ValueError("Unregistered quote projection removals")
        if any(e["action"]!="remove_comment" or not a<=e["start_char"]<e["end_char"]<=b for e in hits):
            raise ValueError("Partial or non-comment quote projection")
        readable_projected_text(original,a,hits);readable_projected_text(final,a,hits)
        ops=[]
        for i,(old,new) in enumerate(zip(original,final)):
            if old==new:continue
            pos=a+i
            if old not in "‘’“”" or new not in "‘’“”" or any(e["start_char"]<=pos<e["end_char"] for e in hits):
                raise ValueError("B18-017 changes a comment or non-quote character")
            ops.append(dict(kind="replace_quote_codepoint",parent_decision_id=ident,
                source_start_char=pos,source_end_char=pos+1,original=old,final=new))
        if len(ops)!=14:raise ValueError("B18-017 must have exactly fourteen quote operations")
        minimal=[{k:o[k] for k in ("source_start_char","source_end_char","original","final")} for o in ops]
        if minimal!=record["minimal_change_operations"]:
            raise ValueError("Quote operations differ from decision packet")
    else:
        if hits:raise ValueError("Unregistered readable change overlaps a removal")
        ops=[dict(kind="replace_source_range",parent_decision_id=ident,source_start_char=a,
            source_end_char=b,original=original,final=final)]
    return [dict(o,id=ident+f":{i:02d}") for i,o in enumerate(ops,1)],hits

def validate_readable_operations(record,operations,edits):
    expected,hits=readable_expected_operations(record,edits)
    if operations!=expected:
        raise ValueError("Unknown, duplicate, out-of-range or unauthorized readable operation")
    # Reconstruct the full parent, including unchanged excluded comments.
    text=record["original"];start=record["source_start_char"]
    for op in reversed(operations):
        a,b=op["source_start_char"]-start,op["source_end_char"]-start
        if text[a:b]!=op["original"]:raise ValueError("Readable operation original mismatch")
        text=text[:a]+op["final"]+text[b:]
    if text!=record["final"]:raise ValueError("Readable operations do not reconstruct full parent")
    return hits

def readable_adoptions(s,m):
    path=DATA/"author-readable-adoptions.json";config=jread(path)
    decision_path=DATA/"author-readable-decisions.json"
    if config["decision_file"]!=decision_path.name or config["decision_sha256"]!=READABLE_DECISIONS_SHA256 or digest(decision_path.read_bytes())!=READABLE_DECISIONS_SHA256:
        raise ValueError("Readable decision packet hash changed")
    packet=jread(decision_path)
    if packet["source_sha256"]!=EXPECTED or config["source_sha256"]!=EXPECTED:
        raise ValueError("Readable source changed")
    if config["authorization_type"]!="user_delegated_readability_selection" or config["authorization_evidence"]!=packet["authorization_evidence"]:
        raise ValueError("Readable delegation evidence changed")
    baseline=DATA/"qa/before-readable-final-decisions/model.json"
    if config["baseline_model_sha256"]!=READABLE_BASELINE_SHA256 or digest(baseline.read_bytes())!=READABLE_BASELINE_SHA256:
        raise ValueError("Readable baseline changed")
    for name,sha in config["preserved_inputs_sha256"].items():
        if Path(name).name!=name or digest((DATA/name).read_bytes())!=sha:
            raise ValueError("Readable preserved input changed")
    sources=packet["proposal_sources_sha256"]
    if config["proposal_sources_sha256"]!=sources:
        raise ValueError("Readable source packet inventory changed")
    packets={}
    for name,sha in sources.items():
        if Path(name).name!=name or digest((DATA/name).read_bytes())!=sha:
            raise ValueError("Readable original proposal file changed")
        packets[name]=jread(DATA/name)
    chosen=[q for q in packet["decisions"] if q["additional_patch_for_this_record"] is True]
    ids=[q["decision_id"] for q in chosen]
    if len(ids)!=40 or len(set(ids))!=40 or config["selected_decision_ids"]!=ids:
        raise ValueError("Unauthorized, missing or duplicate readable decision")
    if [x["decision_id"] for x in config["operation_groups"]]!=ids:
        raise ValueError("Readable operation groups differ from selected decisions")
    allowed_locator_resolutions=[dict(decision_id="READABLE-CRIT-007",file="author-review-critical-comparisons.json",
        record_id="CRIT-007",declared_section="proposals",resolved_section="deferred")]
    if config["explicit_source_locator_resolutions"]!=allowed_locator_resolutions:
        raise ValueError("Unregistered source locator exception")
    if config["semantic_change_count"]!=40 or config["source_operation_count"]!=53:
        raise ValueError("Readable semantic or operation counts changed")
    baseline_manifest_path=DATA/"qa/before-readable-final-decisions/manifest.json"
    if digest(baseline_manifest_path.read_bytes())!="2babf7a83bf2f88e682a342f551947ef7d3fb0dddc6f936cd5473a1168fff933":
        raise ValueError("Readable sealed baseline manifest changed")
    baseline_inputs=jread(baseline_manifest_path)["input_sha256"]
    preserved_names=["author-approved-emendations.json","author-reading-policy.json","author-reading-policy-editorial-notes.json","layout-ranges.json","layout-supplement.json","layout-supplement02.json","author-layout-anchor-overrides.json"]
    if config["preserved_inputs_sha256"]!={name:baseline_inputs[name] for name in preserved_names}:
        raise ValueError("Readable protected input inventory changed")
    changes=[]
    for q,group in zip(chosen,config["operation_groups"]):
        a,b=locate(s,q["chapter"],q["original"],q["source_start_char"],q["source_end_char"])
        if not isinstance(q["final"],str) or not q["final"] or q["authorization_basis"]["user_quote"]!=packet["authorization_evidence"]["user_quote"]:
            raise ValueError("Readable final text or authority missing")
        for field,exact in [("context_before",s[a-len(q["context_before"]):a]),("context_after",s[b:b+len(q["context_after"])])]:
            if q[field]!=exact:raise ValueError("Readable exact source context mismatch")
        resolved=[]
        for ref in q["proposal_sources"]:
            if ref["file"] not in packets or ref["sha256"]!=sources[ref["file"]]:
                raise ValueError("Readable proposal provenance mismatch")
            for ident in ref["ids"]:
                matches=[(section,x) for section in ("proposals","deferred") for x in packets[ref["file"]].get(section,[]) if x.get("id",x.get("issue_id"))==ident]
                if len(matches)!=1:raise ValueError("Readable source record is ambiguous")
                section,original=matches[0]
                key=dict(decision_id=q["decision_id"],file=ref["file"],record_id=ident,
                         declared_section=ref["section"],resolved_section=section)
                if section!=ref["section"] and key not in config["explicit_source_locator_resolutions"]:
                    raise ValueError("Unregistered source-section discrepancy")
                for field in ("chapter","source_start_char","source_end_char","original"):
                    if original[field]!=q[field]:raise ValueError("Readable source record coordinates changed")
                resolved.append(dict(key,record=original))
        if not resolved:raise ValueError("Readable decision has no original source record")
        text=q["original"]
        for op in reversed(q["minimal_change_operations"]):
            lo,hi=op["source_start_char"]-a,op["source_end_char"]-a
            if not 0<=lo<=hi<=len(q["original"]) or text[lo:hi]!=op["original"]:
                raise ValueError("Decision minimal operation lies outside source parent")
            text=text[:lo]+op["final"]+text[hi:]
        if text!=q["final"]:raise ValueError("Decision minimal operations fail reconstruction")
        hits=validate_readable_operations(q,group["operations"],m["edits"])
        original_body=readable_projected_text(q["original"],a,hits)
        proposed_body=readable_projected_text(q["final"],a,hits)
        change=dict(id=q["decision_id"],title=q["source_record_id"]+" 可读性选择",chapter=q["chapter"],
            source_start_char=a,source_end_char=b,original=q["original"],proposed=q["final"],
            body_original=original_body,body_proposed=proposed_body,
            mode="source_quote_substitutions" if hits else "replace",
            status="adopted_under_user_delegation",applied=True,
            authorization_type="user_delegated_readability_selection",
            classification=q["classification"],reason=q["reason"],
            context_before=q["context_before"],context_after=q["context_after"],
            decision_record=q,decision_file=decision_path.name,decision_sha256=READABLE_DECISIONS_SHA256,
            source_records=resolved,source_operations=group["operations"],
            excluded_source_intervals=[dict(e) for e in hits],
            body_text_derivation="remove_only_bound_unchanged_comment_intervals" if hits else "exact_decision_final")
        if hits and (len(original_body)!=263 or len(proposed_body)!=263 or sum(len(x["exact_text"]) for x in hits)!=176):
            raise ValueError("B18-017 projection size changed")
        changes.append(change)
    intervals=sorted(m["author_emendations"]+changes,key=lambda x:x["source_start_char"])
    if any(x["source_end_char"]>y["source_start_char"] for x,y in zip(intervals,intervals[1:])):
        raise ValueError("Readable semantic ranges overlap prior or new changes")
    for q in changes:
        if any(q["source_start_char"]<r["end_char"] and r["start_char"]<q["source_end_char"]
               for c in m["chapters"] for r in c["layout_ranges"]+c["author_layout_ranges"]):
            raise ValueError("Readable adoption has an unregistered layout intersection")
    provenance=dict(path=path.name,sha256=digest(path.read_bytes()),decision_file=decision_path.name,
        decision_sha256=READABLE_DECISIONS_SHA256,authorization_type=config["authorization_type"],
        authority_description="用户委托按可读性选择；并非每个拟字均由用户逐字逐项确认。",
        baseline_model_sha256=READABLE_BASELINE_SHA256,semantic_changes=len(changes),
        source_operations=sum(len(x["source_operations"]) for x in changes),
        preserved_inputs_sha256=config["preserved_inputs_sha256"],proposal_sources_sha256=sources,
        selected_decision_ids=ids,non_patch_decision_ids=[x["decision_id"] for x in packet["decisions"] if not x["additional_patch_for_this_record"]],
        explicit_source_locator_resolutions=config["explicit_source_locator_resolutions"],layout_intersections=[])
    return changes,provenance

def apply_readable_adoptions(m,s):
    changes,provenance=readable_adoptions(s,m)
    if m.get("reading_exclusion_summary",{}).get("total_units")==29:
        if digest((json.dumps(m,ensure_ascii=False,indent=2)+"\n").encode())!=READABLE_BASELINE_SHA256:
            raise ValueError("The pre-readable model no longer matches the sealed 138+29 baseline")
    for c in m["chapters"]:
        new=[q for q in changes if q["chapter"]==c["number"]]
        if not new:continue
        removed={pos for e in c["edits"] for pos in range(e["start_char"],e["end_char"])}
        chars=[(s[pos],pos) for pos in range(c["body_start"],c["source_end"]) if pos not in removed]
        replacement_ends={}
        for q in sorted(c["author_changes"],key=lambda x:x["source_start_char"],reverse=True):
            a,b=q["source_start_char"],q["source_end_char"]
            inds=[i for i,(_,pos) in enumerate(chars) if a<=pos<b]
            if not inds or "".join(chars[i][0] for i in inds)!=q["original"]:
                raise ValueError("Readable baseline source reconstruction failed")
            chars[inds[0]:inds[-1]+1]=[(ch,a) for ch in adopted_body_text(q)];replacement_ends[a]=b
        if "".join(ch for ch,pos in chars)!=c["body"]:raise ValueError("Readable source replay differs from baseline")
        old_body=c["body"];c["body_before_readable_adoptions_sha256"]=c["body_sha256"]
        operations=sorted([o for q in new for o in q["source_operations"]],key=lambda x:x["source_start_char"],reverse=True)
        for op in operations:
            a,b=op["source_start_char"],op["source_end_char"];inds=[i for i,(_,pos) in enumerate(chars) if a<=pos<b]
            if not inds or "".join(chars[i][0] for i in inds)!=op["original"]:
                raise ValueError("Readable source operation target no longer exact")
            chars[inds[0]:inds[-1]+1]=[(ch,a) for ch in op["final"]];replacement_ends[a]=b
        body="".join(ch for ch,pos in chars);c["author_changes"]+=new
        # Preserve the existing paragraph boundaries by their original source coverage.
        cuts={0,len(chars)}
        for block in c["blocks"]:
            edge=block["end_char"]
            cuts.add(sum(replacement_ends.get(pos,pos+1)<=edge for ch,pos in chars))
        cuts=sorted(cuts);generic=[dict(text=body[a:b]) for a,b in zip(cuts,cuts[1:]) if a<b]
        blocks,resolved=layout_blocks(body,chars,generic,c["layout_ranges"]+c["author_layout_ranges"],replacement_ends)
        for block in blocks:
            block["source_mapping"]="covering_source_span"
            block["author_change_ids"]=[q["id"] for q in c["author_changes"] if block["start_char"]<q["source_end_char"] and q["source_start_char"]<block["end_char"]]
        spans=author_change_spans(chars,c["author_changes"])
        operation_spans=[]
        for op in reversed(operations):
            inds=[i for i,(_,pos) in enumerate(chars) if op["source_start_char"]<=pos<op["source_end_char"]]
            if not inds or "".join(chars[i][0] for i in inds)!=op["final"]:raise ValueError("Readable operation body mapping failed")
            operation_spans.append(dict(op,body_start=inds[0],body_end=inds[-1]+1))
        reverse=body
        for q,span in sorted([(q,next(x for x in spans if x["id"]==q["id"])) for q in new],key=lambda pair:pair[1]["body_start"],reverse=True):
            a,b=span["body_start"],span["body_end"]
            if reverse[a:b]!=q["body_proposed"]:raise ValueError("Readable semantic reverse target mismatch")
            reverse=reverse[:a]+q["body_original"]+reverse[b:]
        if reverse!=old_body:raise ValueError("Readable inverse did not restore 138 checkpoint")
        c.update(body=body,body_sha256=digest(body.encode()),blocks=blocks,author_change_spans=spans,
            readable_operation_spans=operation_spans,
            layout_ranges=[r for r in resolved if "author_emendation_id" not in r],
            author_layout_ranges=[r for r in resolved if "author_emendation_id" in r])
        for q in c.get("editorial_note_exclusion_spans",[]):
            q["body_insertion_offset"]=sum(pos<q["source_start_char"] for ch,pos in chars)
    m["author_emendations"]+=changes;m["readable_adoption"]=provenance
    m["emendation_authority_counts"]=dict(individually_confirmed=138,user_delegated_readability_selection=40,total_semantic_changes=178)
    for issue in m["issues"]:
        hits=[q["id"] for q in changes if q["source_start_char"]<issue["end_char"] and issue["start_char"]<q["source_end_char"]]
        if hits:
            issue["related_author_emendations"]=list(dict.fromkeys(issue.get("related_author_emendations",[])+hits))
            issue["related_readability_decisions"]=hits
            issue["resolution_note"]="对应正文已依用户委托按可读性选择；原源摘录及旧判断保留为历史证据，不表示已恢复曹雪芹或庚辰原貌。"
    for c in m["chapters"]:c["issues"]=[q for q in m["issues"] if q["chapter"]==c["number"]]
    return m


OPENING_BASELINE_SHA256="39740da9f13fc3385d1e0f5809b352b3f72f1145a95c23448a3286e01e6c7d19"
OPENING_TEXT_SHA256="6c6efb1e302dd1da4aafa8388e3e9dcfdb23d0ca27a62e6d13c2358ad5bfd98d"
OPENING_MANIFEST_SHA256="234a6b5242546c5c8b4006ff9697fc83ff18668726d4fc382830a8e8ce1f3c40"

def opening_restoration_policy(s):
    policy=jread(DATA/"author-opening-restoration-policy.json")
    if digest((json.dumps(policy,ensure_ascii=False,indent=2)+"\n").encode())!="9cc465275f87792444746c2ad6005eb6345009767fa23b3bbe293d1e75157bc3":
        raise ValueError("Opening policy or its exact authorization evidence changed")
    if (policy.get("id")!="OPENING-SELFSTATEMENT-01" or policy.get("status")!="author_confirmed_reading_scope_restoration"
            or policy.get("action")!="restore_opening_selfstatement" or policy.get("chapter")!=1
            or policy.get("source_sha256")!=EXPECTED or digest(s.encode())!=EXPECTED):
        raise ValueError("Unconfirmed or rebased opening restoration")
    if policy.get("baseline_model_file")!="qa/before-opening-restoration/data/hongloumeng/first80/generated/model.json" or policy.get("baseline_model_sha256")!=OPENING_BASELINE_SHA256:
        raise ValueError("Opening baseline identity changed")
    if digest((DATA/policy["baseline_model_file"]).read_bytes())!=OPENING_BASELINE_SHA256:
        raise ValueError("Opening baseline bytes changed")
    if policy.get("baseline_manifest_file")!="qa/before-opening-restoration/manifest.json" or policy.get("baseline_manifest_sha256")!=OPENING_MANIFEST_SHA256:
        raise ValueError("Opening checkpoint identity changed")
    if digest((DATA/policy["baseline_manifest_file"]).read_bytes())!=OPENING_MANIFEST_SHA256:
        raise ValueError("Opening checkpoint bytes changed")
    expected=[(1045,1184),(1220,1356),(1370,1525)]
    ranges=policy.get("restored_ranges",[])
    if [(q.get("source_start_char"),q.get("source_end_char")) for q in ranges]!=expected:
        raise ValueError("Opening restore ranges exceed the approved scope")
    for i,(q,(a,b)) in enumerate(zip(ranges,expected),1):
        if q.get("id")!=f"OPENING-{i:02}" or q.get("exact_source_text")!=s[a:b] or q.get("source_text_sha256")!=digest(s[a:b].encode()):
            raise ValueError("Opening source slice mismatch")
    comments=policy.get("excluded_inline_comments",[])
    if [(q.get("source_start_char"),q.get("source_end_char")) for q in comments]!=[(1184,1220),(1356,1370)]:
        raise ValueError("Opening inline-comment boundaries changed")
    if any(q.get("exact_source_text")!=s[q["source_start_char"]:q["source_end_char"]] for q in comments):
        raise ValueError("Opening inline-comment source mismatch")
    expected_removed=[(30,1045,"move_frontmatter"),(1184,1220,"remove_comment"),(1356,1370,"remove_comment"),(1525,1601,"move_frontmatter")]
    remaining=policy.get("effective_removed_ranges",[])
    if [(q.get("source_start_char"),q.get("source_end_char"),q.get("action")) for q in remaining]!=expected_removed:
        raise ValueError("Opening effective removal scope changed")
    if any(q.get("exact_source_text")!=s[q["source_start_char"]:q["source_end_char"]] for q in remaining):
        raise ValueError("Opening effective removal source mismatch")
    if policy.get("insertion")!={"chapter":1,"body_offset":0,"before_exact_text":"列位看官：你道此书从何而来？"}:
        raise ValueError("Opening placement changed")
    if policy.get("preserve_original_quote_positions")!=[1092,1101,1436,1442] or any(s[i]!="’" for i in policy["preserve_original_quote_positions"]):
        raise ValueError("Opening original quote characters changed")
    if policy.get("pending_scope")!={"poetry_introduction":[1525,1528],"eight_opening_verses":[1529,1601],"variant_end_couplets":"not decided; current treatment unchanged"}:
        raise ValueError("Undecided opening poetry or variant material entered the restoration")
    text="".join(s[a:b] for a,b in expected)
    if policy.get("restored_codepoints")!=430 or len(text)!=430 or policy.get("restored_text_sha256")!=OPENING_TEXT_SHA256 or digest(text.encode())!=OPENING_TEXT_SHA256:
        raise ValueError("Opening exact 430-character hash mismatch")
    baseline=jread(DATA/policy["baseline_model_file"])
    if policy.get("original_covering_edit")!=baseline["edits"][0] or baseline["edits"][0]["id"]!="E0001":
        raise ValueError("Opening original covering removal not preserved")
    return policy

def apply_opening_restoration(m,s):
    policy=opening_restoration_policy(s)
    if digest((json.dumps(m,ensure_ascii=False,indent=2)+"\n").encode())!=OPENING_BASELINE_SHA256:
        raise ValueError("Opening restoration requires the sealed 178+29 model")
    c=m["chapters"][0];prefix="".join(s[q["source_start_char"]:q["source_end_char"]] for q in policy["restored_ranges"])
    if not c["body"].startswith(policy["insertion"]["before_exact_text"]):
        raise ValueError("Opening insertion target changed")
    old_body=c["body"];old_base=c["base_body"];original=policy["original_covering_edit"]
    if c["edits"][0]!=original or m["edits"][0]!=original:
        raise ValueError("Opening restoration covering removal mismatch")
    effective=[]
    for i,q in enumerate(policy["effective_removed_ranges"],1):
        a,b=q["source_start_char"],q["source_end_char"]
        effective.append(dict(chapter=1,start_char=a,end_char=b,action=q["action"],exact_text=s[a:b],
            reason="开卷自述已按作者决定恢复；此范围仍为原序例、明确夹批或未决卷首诗材料，仅保留本地追溯。",
            id=f"E0001-OPENING-{i:02}",parent_edit_id="E0001",opening_restoration_id=policy["id"],
            line=1,column_start=a-c["source_start"]+1,context_before=s[max(0,a-35):a],context_after=s[b:b+35]))
    m["edits"]=effective+m["edits"][1:];c["edits"]=effective+c["edits"][1:]
    # All current-body coordinates shift together. Source and historical hashes do not.
    for name in ("blocks","author_change_spans","readable_operation_spans","layout_ranges","author_layout_ranges"):
        for entry in c.get(name,[]):
            entry["body_start"]+=430;entry["body_end"]+=430
    for entry in c.get("editorial_note_exclusion_spans",[]):
        for key in ("body_insertion_offset","body_start_before_exclusion","body_end_before_exclusion"):entry[key]+=430
    blocks=[];offset=0
    for q in policy["restored_ranges"]:
        a,b=q["source_start_char"],q["source_end_char"];text=s[a:b]
        blocks.append(dict(start_char=a,end_char=b,body_start=offset,body_end=offset+len(text),text=text,kind="prose",
            source_mapping="exact_source_slice",author_change_ids=[],opening_restoration_id=q["id"]))
        offset+=len(text)
    c["body"]=prefix+old_body;c["base_body"]=prefix+old_base;c["body_sha256"]=digest(c["body"].encode());c["blocks"]=blocks+c["blocks"]
    c["opening_restoration"]=dict(policy_id=policy["id"],restored_codepoints=430,restored_text_sha256=OPENING_TEXT_SHA256,
        body_before_restoration_sha256=digest(old_body.encode()),restored_ranges=policy["restored_ranges"],
        former_covering_edit_id="E0001",note_coordinate_basis="Current opening included; before_exclusion coordinates retain their original word-emendation stage, shifted only by the exact opening prefix.")
    if c["body"][430:]!=old_body or "".join(b["text"] for b in c["blocks"])!=c["body"]:
        raise ValueError("Opening exact body inversion failed")
    removed={pos for e in c["edits"] for pos in range(e["start_char"],e["end_char"])}
    if "".join(s[pos] for pos in range(c["body_start"],c["source_end"]) if pos not in removed)!=c["base_body"]:
        raise ValueError("Opening source reconstruction failed")
    m["opening_restoration"]=dict(policy,path="author-opening-restoration-policy.json",sha256=digest((DATA/"author-opening-restoration-policy.json").read_bytes()))
    return m


def paragraph_boundary_policy(s):
    policy=jread(DATA/"paragraph-boundary-corrections.json")
    if digest((json.dumps(policy,ensure_ascii=False,indent=2)+"\n").encode())!="402b487fb4c7857360bc1db4147f93d3e22b15f0435cc8ed842dc858ad23fe4d":
        raise ValueError("Paragraph policy or its exact scope authorization changed")
    if (policy.get("id")!="CLOSING-QUOTE-BOUNDARIES-01" or policy.get("action")!="repair_display_boundaries_only"
            or policy.get("source_sha256")!=EXPECTED or digest(s.encode())!=EXPECTED
            or policy.get("count")!=3 or policy.get("semantic_change_count_delta")!=0):
        raise ValueError("Invalid paragraph-only correction policy")
    if policy.get("baseline_model_file")!="qa/before-opening-restoration/data/hongloumeng/first80/generated/model.json" or policy.get("baseline_model_sha256")!=OPENING_BASELINE_SHA256:
        raise ValueError("Paragraph correction baseline changed")
    raw=(DATA/policy["baseline_model_file"]).read_bytes()
    if digest(raw)!=OPENING_BASELINE_SHA256:raise ValueError("Paragraph baseline bytes changed")
    baseline=json.loads(raw);records=policy.get("records",[])
    if [(q.get("id"),q.get("chapter"),q.get("source_char"),q.get("displayed_quote")) for q in records]!=[("CLOSE-01",19,184269,"”"),("CLOSE-02",19,188910,"’"),("CLOSE-03",33,314872,"”")]:
        raise ValueError("Unapproved paragraph boundary repair")
    for q in records:
        c=baseline["chapters"][q["chapter"]-1];i=q["next_block_index"]
        if type(i) is not int or i<1 or i>=len(c["blocks"]) or q.get("previous_block_index")!=i-1:
            raise ValueError("Paragraph repair index is invalid")
        pair=c["blocks"][i-1:i+1];left,right=pair
        if q.get("original_blocks")!=pair or q.get("original_blocks_sha256")!=digest((json.dumps(pair,ensure_ascii=False,indent=2)+"\n").encode()):
            raise ValueError("Paragraph repair original blocks changed")
        if q.get("operation")!="move_one_closing_quote_to_previous_block" or q.get("codepoint_count")!=1:
            raise ValueError("Paragraph repair may move exactly one codepoint")
        if q.get("body_sha256")!=c["body_sha256"] or q.get("old_body_boundary")!=right["body_start"] or q.get("new_body_boundary")!=right["body_start"]+1:
            raise ValueError("Paragraph repair body boundary changed")
        if right["start_char"]!=q["source_char"] or q.get("source_original")!=s[q["source_char"]] or not right["text"].startswith(q["displayed_quote"]):
            raise ValueError("Paragraph closing quote source mismatch")
        if left.get("layout_id") or right.get("layout_id") or left["body_end"]!=right["body_start"]:
            raise ValueError("Paragraph repair cannot cross a controlled layout")
        expected_id="READABLE-B18-017" if q["source_char"]==188910 else None
        if q.get("author_change_id")!=expected_id:raise ValueError("Paragraph correction authority mismatch")
        if expected_id:
            change=next(x for x in c["author_changes"] if x["id"]==expected_id)
            ops=[op for op in change["source_operations"] if op["source_start_char"]==q["source_char"]]
            if len(ops)!=1 or ops[0]["original"]!=q["source_original"] or ops[0]["final"]!=q["displayed_quote"]:
                raise ValueError("Paragraph repair no longer matches the approved quote operation")
        elif q["displayed_quote"]!=q["source_original"]:raise ValueError("Paragraph repair attempted a word change")
    return policy

def apply_paragraph_boundary_fixes(m,s):
    policy=paragraph_boundary_policy(s)
    for q in policy["records"]:
        c=m["chapters"][q["chapter"]-1];i=q["next_block_index"]
        if c["body_sha256"]!=q["body_sha256"] or c["blocks"][i-1:i+1]!=q["original_blocks"]:
            raise ValueError("Paragraph repair requires the exact original block pair")
        left,right=c["blocks"][i-1:i+1];quote=q["displayed_quote"];original=left["text"]+right["text"]
        left["text"]+=quote;right["text"]=right["text"][1:]
        left["body_end"]+=1;right["body_start"]+=1
        left["end_char"]=q["source_char"]+1;right["start_char"]=q["source_char"]+1
        for block in (left,right):
            block["author_change_ids"]=[x["id"] for x in c["author_changes"] if block["start_char"]<x["source_end_char"] and x["source_start_char"]<block["end_char"]]
        if left["text"]+right["text"]!=original or "".join(x["text"] for x in c["blocks"])!=c["body"]:
            raise ValueError("Paragraph repair changed reading characters")
        c.setdefault("paragraph_boundary_fixes",[]).append(q["id"])
    m["paragraph_boundary_corrections"]=dict(policy,path="paragraph-boundary-corrections.json",sha256=digest((DATA/"paragraph-boundary-corrections.json").read_bytes()))
    return m




POEM_COUPLET_BASELINE_SHA256="f459a311ca9ac2d093eab79d183f44a34c6d3cb72134a5d29dca75fee25aeba8"
POEM_COUPLET_POLICY_SHA256="7eebf1d47d84dcec7e03a2a6691a3e6b9c7c7b2fc5515015c17ffc8beb094352"

def poem_couplet_policy(s):
    """An exact, separately counted reading-scope decision; never a word emendation."""
    policy=jread(DATA/"author-poem-couplet-policy.json")
    if digest((json.dumps(policy,ensure_ascii=False,indent=2)+"\n").encode())!=POEM_COUPLET_POLICY_SHA256:
        raise ValueError("Poem/couplet policy or authorization changed")
    if digest(s.encode())!=EXPECTED or policy["source_sha256"]!=EXPECTED:
        raise ValueError("Poem/couplet source changed")
    if policy["baseline_model_file"]!="qa/before-poem-couplet-20261110/data/hongloumeng/first80/generated/model.json" or policy["baseline_model_sha256"]!=POEM_COUPLET_BASELINE_SHA256:
        raise ValueError("Poem/couplet checkpoint identity changed")
    if digest((DATA/policy["baseline_model_file"]).read_bytes())!=POEM_COUPLET_BASELINE_SHA256:
        raise ValueError("Poem/couplet checkpoint bytes changed")
    if digest((DATA/"qa/before-poem-couplet-20261110/manifest.json").read_bytes())!=policy["baseline_checkpoint_sha256"]:
        raise ValueError("Poem/couplet checkpoint manifest changed")
    for q in policy["records"]:
        a,z=q["source_start_char"],q["source_end_char"]
        if s[a:z]!=q["exact_source_text"] or digest(s[a:z].encode())!=q["source_text_sha256"]:
            raise ValueError("Poem/couplet source slice mismatch")
        all_positions=[i for x,y in q["kept_source_ranges"]+q["removed_source_ranges"] for i in range(x,y)]
        if sorted(all_positions)!=list(range(a,z)):
            raise ValueError("Poem/couplet source partition mismatch")
        if "".join(s[x:y] for x,y in q["kept_source_ranges"])!=q["adopted_text"]:
            raise ValueError("Poem/couplet adoption differs from exact source")
    return policy

def apply_poem_couplet_selections(m,s):
    policy=poem_couplet_policy(s)
    if digest((json.dumps(m,ensure_ascii=False,indent=2)+"\n").encode())!=POEM_COUPLET_BASELINE_SHA256:
        raise ValueError("Poem/couplet selection requires its exact sealed baseline")
    records=[]
    for q in policy["records"]:
        c=m["chapters"][q["chapter"]-1];old_body=c["body"]
        if q["chapter"]==1:
            start=end=430
            if not old_body[start:].startswith("列位看官：你道此书从何而来？") or not old_body[:start].endswith("阅者切记之。"):
                raise ValueError("Opening poem placement changed")
            base_start=base_end=430
            removed_edit=q["former_edit"]
            if c["edits"][3]!=removed_edit:raise ValueError("Opening poem covering edit changed")
            c["edits"].remove(removed_edit);m["edits"].remove(removed_edit)
        else:
            original=q["exact_source_text"]
            if not old_body.endswith(original) or not old_body[:-len(original)].endswith(q["preserved_narration_suffix"]):
                raise ValueError("Ending couplet or preceding narration changed")
            start=len(old_body)-len(original);end=len(old_body)
            if c["blocks"][-1]["text"]!=original:raise ValueError("Ending couplet block changed")
            base_start=len(c["base_body"])-len(original);base_end=len(c["base_body"])
            if c["base_body"][base_start:]!=original:raise ValueError("Ending couplet base changed")
            c["blocks"].pop()
            retained=q["former_retained"]
            if retained not in c["retained"] or retained not in m["retained"]:raise ValueError("Ending variant history changed")
            c["retained"].remove(retained);m["retained"].remove(retained)
        adopted=q["adopted_text"];delta=len(adopted)-(end-start)
        if delta!=q["body_codepoint_delta"]:raise ValueError("Wrong scope delta")
        # Current body coordinates shift, never historical or source coordinates.
        for name in ("blocks","author_change_spans","readable_operation_spans","layout_ranges","author_layout_ranges"):
            for entry in c.get(name,[]):
                if entry["body_start"]>=end:
                    entry["body_start"]+=delta;entry["body_end"]+=delta
                elif entry["body_end"]>start:
                    raise ValueError("Poem/couplet overlaps an existing controlled range")
        for entry in c.get("editorial_note_exclusion_spans",[]):
            for key in ("body_insertion_offset","body_start_before_exclusion","body_end_before_exclusion"):
                if entry[key]>=end:entry[key]+=delta
        new_blocks=[];offset=start
        ranges=([(1525,1528)]+q["display_line_source_ranges"]) if q["chapter"]==1 else q["display_line_source_ranges"]
        layout_id="SCOPE-"+q["id"]
        for i,(a,z) in enumerate(ranges):
            is_intro=q["chapter"]==1 and i==0
            block=dict(start_char=a,end_char=z,body_start=offset,body_end=offset+z-a,text=s[a:z],kind="prose" if is_intro else ("verse" if q["chapter"]==1 else "couplet"),source_mapping="exact_source_slice",author_change_ids=[],version_selection_id=q["id"])
            if not is_intro:block.update(layout_id=layout_id,layout_first=i==(1 if q["chapter"]==1 else 0),layout_last=i==len(ranges)-1)
            new_blocks.append(block);offset+=z-a
        if "".join(b["text"] for b in new_blocks)!=adopted:raise ValueError("New display lines changed text")
        c["blocks"]+=new_blocks;c["blocks"].sort(key=lambda b:b["body_start"])
        c["body"]=old_body[:start]+adopted+old_body[end:]
        c["base_body"]=c["base_body"][:base_start]+adopted+c["base_body"][base_end:]
        c["body_sha256"]=digest(c["body"].encode())
        verse=new_blocks[1:] if q["chapter"]==1 else new_blocks
        a,z=q["display_line_source_ranges"][0][0],q["display_line_source_ranges"][-1][1]
        c["layout_ranges"].append(dict(id=layout_id,chapter=q["chapter"],kind=verse[0]["kind"],start_char=a,end_char=z,exact_text=s[a:z],exact_body_text="".join(b["text"] for b in verse),line_break_after_body_offsets=list(range(8,8*len(verse),8)),body_start=verse[0]["body_start"],body_end=verse[-1]["body_end"],authority="author_confirmed_reading_scope",policy_id=policy["id"],source_mapping="explicit_exact_source_slices",source_line_ranges=q["display_line_source_ranges"]))
        c["layout_ranges"].sort(key=lambda r:r["body_start"])
        removals=[]
        for i,(a,z) in enumerate(q["removed_source_ranges"],1):
            removals.append(dict(chapter=q["chapter"],start_char=a,end_char=z,exact_text=s[a:z],action="remove_editorial_wrapper",reason="作者已批准保留诗联文字；去编者框、版本标签及重复引语，不改原叙事或诗联措辞。",id=f"SCOPE-{q['id']}-{i:02}",version_selection_id=q["id"],parent_edit_id=q["former_edit"]["id"] if "former_edit" in q else None))
        c["edits"]=sorted(c["edits"]+removals,key=lambda e:e["start_char"]);m["edits"]=sorted(m["edits"]+removals,key=lambda e:e["start_char"])
        record=dict(id=q["id"],chapter=q["chapter"],body_start=start,body_end=start+len(adopted),before_text=old_body[start:end],adopted_text=adopted,body_before_sha256=digest(old_body.encode()),body_after_sha256=c["body_sha256"],delta=delta,semantic_change_count_delta=0)
        c["version_selections"]=[record];records.append(record)
        if c["body"][:start]+record["before_text"]+c["body"][start+len(adopted):]!=old_body:raise ValueError("Exact selection inversion failed")
        if "".join(b["text"] for b in c["blocks"])!=c["body"]:raise ValueError("Selection block join changed body")
        removed={pos for e in c["edits"] for pos in range(e["start_char"],e["end_char"])}
        if "".join(s[pos] for pos in range(c["body_start"],c["source_end"]) if pos not in removed)!=c["base_body"]:raise ValueError("Selection base does not replay from source")
    m["layout_provenance"]["active_ranges"]=sum(len(c["layout_ranges"]) for c in m["chapters"])
    m["layout_provenance"]["reading_scope_additions"]=["SCOPE-"+q["id"] for q in policy["records"]]
    m["version_selections"]=dict(policy_id=policy["id"],path="author-poem-couplet-policy.json",sha256=POEM_COUPLET_POLICY_SHA256,baseline_model_sha256=POEM_COUPLET_BASELINE_SHA256,records=records,semantic_change_count_delta=0,layout_range_delta=2,body_codepoint_delta=60)
    if len(m["author_emendations"])!=178 or sum(len(c["body"]) for c in m["chapters"])!=586240:raise ValueError("Selection aggregate invariant failed")
    return m




TAIL_LACUNA_BASELINE_SHA256="43292d2a51d2072400c75ae7d883d75e404f99e0dfaeaa17bd997e968e0e1c26"
TAIL_LACUNA_POLICY_SHA256="7f781f73e7674bb001d91775679eed2e98aa6db5ebb68f233780bd781d2de17e"

def tail_lacuna_policy(s):
    policy=jread(DATA/"author-tail-lacuna-policy.json")
    if digest((json.dumps(policy,ensure_ascii=False,indent=2)+"\n").encode())!=TAIL_LACUNA_POLICY_SHA256:
        raise ValueError("Tail/lacuna policy or explicit authorization changed")
    if digest(s.encode())!=EXPECTED or policy["source_sha256"]!=EXPECTED:
        raise ValueError("Tail/lacuna source changed")
    if policy["baseline_model_file"]!="qa/before-tail-lacuna-20261110/data/hongloumeng/first80/generated/model.json" or policy["baseline_model_sha256"]!=TAIL_LACUNA_BASELINE_SHA256:
        raise ValueError("Tail/lacuna baseline identity changed")
    if digest((DATA/policy["baseline_model_file"]).read_bytes())!=TAIL_LACUNA_BASELINE_SHA256 or digest((DATA/"qa/before-tail-lacuna-20261110/manifest.json").read_bytes())!=policy["baseline_checkpoint_sha256"]:
        raise ValueError("Tail/lacuna baseline bytes changed")
    expected=[(4,45565,45586,""),(9,95562,95583,""),(24,237347,237348,"䰖"),(29,285446,285447,"㻞"),(58,520538,520539,"修"),(62,554977,554978,"巴")]
    if [(q["chapter"],q["source_start_char"],q["source_end_char"],q["proposed"]) for q in policy["records"]]!=expected:
        raise ValueError("Tail/lacuna scope changed")
    for q in policy["records"]:
        a,z=locate(s,q["chapter"],q["original"],q["source_start_char"],q["source_end_char"])
        if digest(s[a:z].encode())!=q["source_text_sha256"] or s[a-len(q["context_before"]):a]!=q["context_before"] or s[z:z+len(q["context_after"])]!=q["context_after"]:
            raise ValueError("Tail/lacuna exact source context changed")
    return policy

def selection_source_chars(c,s):
    """Replay current removals and prior emendations without guessing body positions."""
    removed={p for e in c["edits"] for p in range(e["start_char"],e["end_char"])}
    chars=[(s[p],p) for p in range(c["body_start"],c["source_end"]) if p not in removed]
    if "".join(ch for ch,p in chars)!=c["base_body"]:raise ValueError("Tail/lacuna source base differs")
    for q in sorted(effective_author_changes(c),key=lambda x:x["source_start_char"],reverse=True):
        indices=[i for i,(_,p) in enumerate(chars) if q["source_start_char"]<=p<q["source_end_char"]]
        if not indices or indices!=list(range(indices[0],indices[-1]+1)):raise ValueError("Prior emendation mapping is not contiguous")
        if "".join(chars[i][0] for i in indices)!=q.get("body_original",q["original"]):raise ValueError("Prior emendation source mismatch")
        chars[indices[0]:indices[-1]+1]=[(ch,q["source_start_char"]) for ch in adopted_body_text(q)]
    if "".join(ch for ch,p in chars)!=c["body"]:raise ValueError("Tail/lacuna current body differs")
    return chars

def apply_tail_lacuna_decisions(m,s):
    policy=tail_lacuna_policy(s)
    if digest((json.dumps(m,ensure_ascii=False,indent=2)+"\n").encode())!=TAIL_LACUNA_BASELINE_SHA256:
        raise ValueError("Tail/lacuna decisions require their exact baseline")
    records=[];new_changes=[]
    for q in policy["records"]:
        c=m["chapters"][q["chapter"]-1];a,z=q["source_start_char"],q["source_end_char"]
        chars=selection_source_chars(c,s);indices=[i for i,(_,p) in enumerate(chars) if a<=p<z]
        if not indices or indices!=list(range(indices[0],indices[-1]+1)):raise ValueError("Tail/lacuna range has no exact body mapping")
        lo,hi=indices[0],indices[-1]+1;before=c["body"]
        if before[lo:hi]!=q["original"]:raise ValueError("Tail/lacuna original body differs")
        if any(x["source_start_char"]<z and a<x["source_end_char"] for x in c["author_changes"]):raise ValueError("Tail/lacuna conflicts with an earlier word emendation")
        if any(r["start_char"]<z and a<r["end_char"] for r in c["layout_ranges"]+c["author_layout_ranges"]):raise ValueError("Tail/lacuna may not alter a controlled poem layout")
        if q["action"]=="exclude_variant_ending":
            if hi!=len(before) or not before[:lo].endswith(q["preserved_ending"]) or c["blocks"][-1]["text"]!=q["original"]:
                raise ValueError("Ending exclusion no longer has its exact final block")
            c["blocks"].pop();c["body"]=before[:lo]
            if not c["base_body"].endswith(q["original"]):raise ValueError("Ending source base changed")
            c["base_body"]=c["base_body"][:-len(q["original"])]
            edit=dict(chapter=q["chapter"],start_char=a,end_char=z,exact_text=q["original"],id=q["id"],action="exclude_variant_ending",reason="作者明确决定删除本回整块异本尾联，包含版本标签、引语与括号；原文完整保留在独立决策记录。",decision_policy_id=policy["id"])
            c["edits"]=sorted(c["edits"]+[edit],key=lambda x:x["start_char"]);m["edits"]=sorted(m["edits"]+[edit],key=lambda x:x["start_char"])
            for old in q["former_retained"]:
                if old not in c["retained"] or old not in m["retained"]:raise ValueError("Ending retained history changed")
                c["retained"].remove(old);m["retained"].remove(old)
        else:
            if not len(q["original"])==len(q["proposed"])==1:raise ValueError("Missing-character replacement must preserve one codepoint")
            change=dict(id=q["id"],chapter=q["chapter"],title=q["title"],status="author_approved",applied=True,mode="replace",source_start_char=a,source_end_char=z,original=q["original"],proposed=q["proposed"],context_before=q["context_before"],context_after=q["context_after"],reason=q["reason"],authorization_type="author_explicit_tail_lacuna_decision",decision_file="author-tail-lacuna-policy.json",decision_sha256=TAIL_LACUNA_POLICY_SHA256)
            c["body"]=before[:lo]+q["proposed"]+before[hi:];chars[lo:hi]=[(q["proposed"],a)]
            c["author_changes"].append(change);new_changes.append(change)
            c["author_change_spans"]=author_change_spans(chars,c["author_changes"])
            matches=[b for b in c["blocks"] if b["body_start"]<=lo<hi<=b["body_end"]]
            if len(matches)!=1:raise ValueError("Missing-character replacement crosses display blocks")
            block=matches[0];local=lo-block["body_start"]
            if block["text"][local:local+1]!=q["original"]:raise ValueError("Missing-character display anchor changed")
            block["text"]=block["text"][:local]+q["proposed"]+block["text"][local+1:];block["author_change_ids"].append(q["id"])
            for issue in m["issues"]:
                if issue["chapter"]==q["chapter"] and issue["start_char"]<z and a<issue["end_char"]:
                    issue["historical_source_issue"]=True;issue["current_resolution"]="author_explicitly_resolved";issue["current_resolution_id"]=q["id"];issue["current_reading_text"]=q["proposed"];issue["resolution_note"]=q["reason"]
            c["issues"]=[x for x in m["issues"] if x["chapter"]==q["chapter"]]
        c["body_sha256"]=digest(c["body"].encode())
        record=dict(id=q["id"],chapter=q["chapter"],source_start_char=a,source_end_char=z,body_start=lo,body_end=lo+len(q["proposed"]),original=q["original"],adopted=q["proposed"],body_before_sha256=digest(before.encode()),body_after_sha256=c["body_sha256"],semantic_change_count_delta=q["semantic_change_count_delta"])
        c["tail_lacuna_decisions"]=[record];records.append(record)
        if c["body"][:lo]+q["original"]+c["body"][lo+len(q["proposed"]):]!=before:raise ValueError("Tail/lacuna exact inverse failed")
        if "".join(x["text"] for x in c["blocks"])!=c["body"] or any(not x["text"] for x in c["blocks"]):raise ValueError("Tail/lacuna block output differs or contains an empty block")
        selection_source_chars(c,s)
    m["author_emendations"]+=new_changes
    m["emendation_authority_counts"]=dict(individually_confirmed=142,user_delegated_readability_selection=40,total_semantic_changes=182)
    m["tail_lacuna_decisions"]=dict(policy_id=policy["id"],path="author-tail-lacuna-policy.json",sha256=TAIL_LACUNA_POLICY_SHA256,baseline_model_sha256=TAIL_LACUNA_BASELINE_SHA256,records=records,semantic_change_count_delta=4,body_codepoint_delta=-42,layout_range_delta=0)
    body="".join(c["body"] for c in m["chapters"])
    if len(body)!=586198 or "□" in body or len(m["author_emendations"])!=182 or sum(len(c["layout_ranges"]) for c in m["chapters"])!=303:raise ValueError("Tail/lacuna aggregate invariants failed")
    return m


TITLE61_POLICY_SHA256="6e3a5bbc8a719b77b423f237197d4927c2408bda3bf367464779e82584654c2c"
TITLE61_BASELINE_SHA256="35918ca868a585b422adf63b61c5dd179173a386eb3dd8836e980f547d63aced"

def apply_title61_decision(m,s):
    """Apply the separately approved title-only change after the sealed 182 layer."""
    path=DATA/"author-title61-policy.json";raw=path.read_bytes()
    if digest(raw)!=TITLE61_POLICY_SHA256:raise ValueError("Title61 policy changed")
    policy=json.loads(raw);q=policy["change"]
    if policy["source_sha256"]!=EXPECTED or digest(s.encode())!=EXPECTED:raise ValueError("Title61 source changed")
    if policy["baseline_model_sha256"]!=TITLE61_BASELINE_SHA256 or digest((json.dumps(m,ensure_ascii=False,indent=2)+"\n").encode())!=TITLE61_BASELINE_SHA256:raise ValueError("Title61 baseline model changed")
    if policy["authorization"]["answer"]!="61回同意" or policy["status"]!="author_explicitly_confirmed":raise ValueError("Title61 authority missing")
    c=m["chapters"][60];a,z=q["source_start_char"],q["source_end_char"];i=q["title_offset"]
    if (q["id"],q["chapter"],q["source_section"],a,z,i,q["original"],q["proposed"],q["traditional_proposed"])!=("TITLE61-01",61,"title",538213,538214,13,"脏","赃","贓"):raise ValueError("Title61 permitted operation changed")
    if not c["source_start"]<=a<z<=c["body_start"] or s[a:z]!=q["original"]:raise ValueError("Title61 source is not in title")
    if s[a-len(q["context_before"]):a]!=q["context_before"] or s[z:z+len(q["context_after"])]!=q["context_after"]:raise ValueError("Title61 source context mismatch")
    before=c["title"]
    if before!=q["title_before"] or before[i:i+1]!=q["original"]:raise ValueError("Title61 current title mismatch")
    after=before[:i]+q["proposed"]+before[i+1:]
    if after!=q["title_after"] or after[:i]+q["original"]+after[i+1:]!=before:raise ValueError("Title61 inverse failed")
    change=dict(q,title="第61回回目赃物字校正",mode="replace",status="author_approved",applied=True,authorization_type="author_explicit_title_decision",decision_file=path.name,decision_sha256=TITLE61_POLICY_SHA256)
    c["title"]=after;c["title_changes"]=[change]
    # Body-specific author_changes and character spans remain untouched.
    m["author_emendations"].append(change)
    m["emendation_authority_counts"]=dict(individually_confirmed=143,user_delegated_readability_selection=40,total_semantic_changes=183)
    m["title61_decision"]=dict(policy_id=policy["id"],path=path.name,sha256=TITLE61_POLICY_SHA256,baseline_model_sha256=TITLE61_BASELINE_SHA256,semantic_change_count_delta=1,body_codepoint_delta=0,title_before=before,title_after=after)
    if len(m["author_emendations"])!=183 or sum(len(x["body"]) for x in m["chapters"])!=586198:raise ValueError("Title61 aggregate invariant failed")
    return m


SOURCE6_POLICY_SHA256="0d58adae41c0cdeac9202e18a301a40c3cdf8bb8391a66dd671533294ef280f7"
SOURCE6_BASELINE_SHA256="39ba020251b48c59bb48be0b06a78f26da6814a3f18f7b5e90e16530e30aa7c1"
SOURCE6_BODY_SHA256="c3ef39d0b18469c280eb7064c41b66f8d0aa10ff457f718e7601dbbc94f2b87a"

def apply_six_source_decisions(m,s):
    """Six explicitly approved readability corrections, after the frozen 183 layer.

    Raw-source coordinates and historical decisions stay immutable. Current body
    positions are rebased; no block, line or heading is inserted or removed.
    """
    path=DATA/"author-six-source-policy.json";raw=path.read_bytes()
    if digest(raw)!=SOURCE6_POLICY_SHA256:raise ValueError("Six-source policy changed")
    policy=json.loads(raw)
    if policy["source_sha256"]!=EXPECTED or digest(s.encode())!=EXPECTED:raise ValueError("Six-source original source changed")
    if policy["baseline_model_sha256"]!=SOURCE6_BASELINE_SHA256 or digest((json.dumps(m,ensure_ascii=False,indent=2)+"\n").encode())!=SOURCE6_BASELINE_SHA256:raise ValueError("Six-source baseline model changed")
    if policy["baseline_body_sha256"]!=SOURCE6_BODY_SHA256 or digest("".join(c["body"] for c in m["chapters"]).encode())!=SOURCE6_BODY_SHA256:raise ValueError("Six-source baseline body changed")
    if policy["authorization"]["answer"]!="不需要核古本，参考公开文本就行，以可读性为目标，都同意" or policy["status"]!="author_explicitly_confirmed":raise ValueError("Six-source authority missing")
    expected=[(1,35,"日以甘灌溉","日以甘露灌溉"),(4,13,"他们的跽遭遇","他们的孽障遭遇"),(4,24,"如今司正升了外省去","如今舅舅正升了外省去"),(4,25,"你司、姨娘两处","你舅舅、姨娘两处"),(5,16,"其艳若何？加澄塘。","其艳若何？霞映澄塘。"),(5,102,"浆满泛玻璃盏，玉号斟琥珀杯。","琼浆满泛玻璃盏，玉液浓斟琥珀杯。")]
    if [(q["chapter"],q["block_index"],q["original"],q["proposed"]) for q in policy["records"]]!=expected:raise ValueError("Six-source permitted scope changed")
    changes={}
    for q in reversed(policy["records"]):
        c=m["chapters"][q["chapter"]-1];block=c["blocks"][q["block_index"]];a,z=q["source_start_char"],q["source_end_char"];lo,hi=q["body_start"],q["body_end"]
        if s[a:z]!=q["original"] or s[a-20:a]!=q["context_before"] or s[z:z+20]!=q["context_after"]:raise ValueError("Six-source exact source anchor changed")
        if digest(block["text"].encode())!=q["block_sha256"] or c["body"][lo:hi]!=q["original"]:raise ValueError("Six-source exact body anchor changed")
        chars=selection_source_chars(c,s)
        if [p for ch,p in chars[lo:hi]]!=list(range(a,z)):raise ValueError("Six-source source/body mapping changed")
        if any(x["source_start_char"]<z and a<x["source_end_char"] for x in c["author_changes"]):raise ValueError("Six-source overlaps earlier emendation")
        before=c["body"];delta=len(q["proposed"])-len(q["original"]);local=lo-block["body_start"]
        block["text"]=block["text"][:local]+q["proposed"]+block["text"][local+len(q["original"]):];block["author_change_ids"].append(q["id"])
        c["body"]=before[:lo]+q["proposed"]+before[hi:];c["body_sha256"]=digest(c["body"].encode())
        # Current offsets only. Historical policy records retain their own hashes.
        for item in c["blocks"]+c["layout_ranges"]+c["author_layout_ranges"]+c.get("editorial_note_exclusion_spans",[])+c.get("readable_operation_spans",[]):
            for key in ("body_start","body_end"):
                if key in item and item[key]>=hi:item[key]+=delta
        for layout in c["layout_ranges"]:
            if layout["start_char"]<z and a<layout["end_char"]:
                if layout["id"]!="L05-018" or layout["line_break_after_body_offsets"]:raise ValueError("Six-source unexpected layout overlap")
                if layout["exact_body_text"].count(q["original"])!=1:raise ValueError("Six-source layout text anchor changed")
                layout["exact_body_text"]=layout["exact_body_text"].replace(q["original"],q["proposed"])
                layout["author_emendation_ids"].append(q["id"])
        change=dict(q,title="前五回可读性补校",status="author_approved",applied=True,mode="replace",authorization_type="author_explicit_six_source_decision",decision_file=path.name,decision_sha256=SOURCE6_POLICY_SHA256)
        c["author_changes"].append(change);changes[q["id"]]=change
        chars[lo:hi]=[(ch,a) for ch in q["proposed"]]
        c["author_change_spans"]=author_change_spans(chars,c["author_changes"])
        if c["body"][:lo]+q["original"]+c["body"][lo+len(q["proposed"]):]!=before:raise ValueError("Six-source inverse failed")
        if "".join(b["text"] for b in c["blocks"])!=c["body"]:raise ValueError("Six-source block/body mismatch")
        if any(c["body"][b["body_start"]:b["body_end"]]!=b["text"] for b in c["blocks"]):raise ValueError("Six-source block offsets differ")
        selection_source_chars(c,s)
    m["author_emendations"].extend(changes[q["id"]] for q in policy["records"])
    m["emendation_authority_counts"]=dict(individually_confirmed=149,user_delegated_readability_selection=40,total_semantic_changes=189)
    m["six_source_decisions"]=dict(policy_id=policy["id"],path=path.name,sha256=SOURCE6_POLICY_SHA256,baseline_model_sha256=SOURCE6_BASELINE_SHA256,baseline_body_sha256=SOURCE6_BODY_SHA256,records=policy["records"],semantic_change_count_delta=6,body_codepoint_delta=7,layout_range_delta=0)
    if len(m["author_emendations"])!=189 or sum(len(c["body"]) for c in m["chapters"])!=586205 or sum(len(c["blocks"]) for c in m["chapters"])!=4394:raise ValueError("Six-source aggregate invariant failed")
    return m


SOURCE7_POLICY_SHA256="61adaaec1f4f493ea9b4d5ad303c32d2147bef64dd0ba882f73a8e91a09972cd"
SOURCE7_BASELINE_SHA256="d3f58a9413c625a1e7eab3e6b04f97ed62f4ae43bd378164fed556cf82d4eae5"
SOURCE7_BODY_SHA256="4da79146047e7ef3be8fbc75ef26a091e7e9673a5d7fe944dc6b390fd5e66e55"

def apply_seven_source_decisions(m,s):
    """Seven explicitly approved readability decisions (eight occurrences), after the frozen 189 layer.

    Raw-source coordinates and historical decisions stay immutable. Current body
    positions are rebased; no block, line or heading is inserted or removed.
    """
    path=DATA/"author-seven-source-policy.json";raw=path.read_bytes()
    if digest(raw)!=SOURCE7_POLICY_SHA256:raise ValueError("Seven-source policy changed")
    policy=json.loads(raw)
    if policy["source_sha256"]!=EXPECTED or digest(s.encode())!=EXPECTED:raise ValueError("Seven-source original source changed")
    if policy["baseline_model_sha256"]!=SOURCE7_BASELINE_SHA256 or digest((json.dumps(m,ensure_ascii=False,indent=2)+"\n").encode())!=SOURCE7_BASELINE_SHA256:raise ValueError("Seven-source baseline model changed")
    if policy["baseline_body_sha256"]!=SOURCE7_BODY_SHA256 or digest("".join(c["body"] for c in m["chapters"]).encode())!=SOURCE7_BODY_SHA256:raise ValueError("Seven-source baseline body changed")
    if policy["status"]!="author_explicitly_confirmed" or [a["answer"] for a in policy["authorizations"]]!=["以上几项都没问题，确认","这三处也可以"]:raise ValueError("Seven-source authority missing")
    expected=[(6, 24, '打柜筛面', '打箩柜筛面'), (6, 31, '面目清秀，身目俏', '面目清秀，身材俊俏'), (8, 37, '吃了半碗饭碧粳粥', '吃了半碗碧粳粥'), (10, 22, '右关需而无神', '右关虚而无神'), (10, 22, '右关需而无神', '右关虚而无神'), (17, 42, '此处短两植', '此处蕉棠两植'), (18, 21, '说不尽本虾须', '说不尽帘卷虾须'), (18, 124, '是统役、优伶、百戏、杂行人丁的', '是赐厨役、优伶、百戏、杂行人丁的')]
    if [(q["chapter"],q["block_index"],q["original"],q["proposed"]) for q in policy["records"]]!=expected:raise ValueError("Seven-source permitted scope changed")
    for q in policy["records"]:
        if digest(m["chapters"][q["chapter"]-1]["blocks"][q["block_index"]]["text"].encode())!=q["block_sha256"]:raise ValueError("Seven-source baseline block changed")
    changes={}
    for q in reversed(policy["records"]):
        c=m["chapters"][q["chapter"]-1];block=c["blocks"][q["block_index"]];a,z=q["source_start_char"],q["source_end_char"];lo,hi=q["body_start"],q["body_end"]
        if s[a:z]!=q["original"] or s[a-20:a]!=q["context_before"] or s[z:z+20]!=q["context_after"]:raise ValueError("Seven-source exact source anchor changed")
        if c["body"][lo:hi]!=q["original"]:raise ValueError("Seven-source exact body anchor changed")
        chars=selection_source_chars(c,s)
        if [p for ch,p in chars[lo:hi]]!=list(range(a,z)):raise ValueError("Seven-source source/body mapping changed")
        if any(x["source_start_char"]<z and a<x["source_end_char"] for x in c["author_changes"]):raise ValueError("Seven-source overlaps earlier emendation")
        before=c["body"];delta=len(q["proposed"])-len(q["original"]);local=lo-block["body_start"]
        block["text"]=block["text"][:local]+q["proposed"]+block["text"][local+len(q["original"]):];block["author_change_ids"].append(q["id"])
        c["body"]=before[:lo]+q["proposed"]+before[hi:];c["body_sha256"]=digest(c["body"].encode())
        # Current offsets only. Historical policy records retain their own hashes.
        for item in c["blocks"]+c["layout_ranges"]+c["author_layout_ranges"]+c.get("editorial_note_exclusion_spans",[])+c.get("readable_operation_spans",[]):
            for key in ("body_start","body_end"):
                if key in item and item[key]>=hi:item[key]+=delta
        if any(layout["start_char"]<z and a<layout["end_char"] for layout in c["layout_ranges"]+c["author_layout_ranges"]):raise ValueError("Seven-source unexpected controlled layout overlap")
        change=dict(q,title="第6至18回七项可读性补校",status="author_approved",applied=True,mode="replace",authorization_type="author_explicit_seven_source_decision",decision_file=path.name,decision_sha256=SOURCE7_POLICY_SHA256)
        c["author_changes"].append(change);changes[q["id"]]=change
        chars[lo:hi]=[(ch,a) for ch in q["proposed"]]
        c["author_change_spans"]=author_change_spans(chars,c["author_changes"])
        if c["body"][:lo]+q["original"]+c["body"][lo+len(q["proposed"]):]!=before:raise ValueError("Seven-source inverse failed")
        if "".join(b["text"] for b in c["blocks"])!=c["body"]:raise ValueError("Seven-source block/body mismatch")
        if any(c["body"][b["body_start"]:b["body_end"]]!=b["text"] for b in c["blocks"]):raise ValueError("Seven-source block offsets differ")
        selection_source_chars(c,s)
    m["author_emendations"].extend(changes[q["id"]] for q in policy["records"])
    m["emendation_authority_counts"]=dict(individually_confirmed=156,user_delegated_readability_selection=40,total_semantic_changes=196,applied_occurrence_records=197)
    m["seven_source_decisions"]=dict(policy_id=policy["id"],path=path.name,sha256=SOURCE7_POLICY_SHA256,baseline_model_sha256=SOURCE7_BASELINE_SHA256,baseline_body_sha256=SOURCE7_BODY_SHA256,records=policy["records"],semantic_change_count_delta=7,occurrence_count_delta=8,body_codepoint_delta=4,layout_range_delta=0)
    if len(m["author_emendations"])!=197 or sum(len(c["body"]) for c in m["chapters"])!=586209 or sum(len(c["blocks"]) for c in m["chapters"])!=4394:raise ValueError("Seven-source aggregate invariant failed")
    return m


SOURCE24_POLICY_SHA256='c34ba6b9861c0ac42c164031eb0835a2334f5c15bb879ba01c31ac798d0e0603'
SOURCE24_BASELINE_SHA256='43c26d620a6cab2221cd365cf88e67de19e265b32b51a62f69bdabf8c5b49808'
SOURCE24_BODY_SHA256='7a0d2f84ecc65f9e2b16c1c7c5aee746a6a5e78b63e5d4a042bd0909dd592bc2'

def apply_chapter24_source_decision(m,s):
    """One explicitly approved readability correction, after the frozen 196-decision layer.

    Raw-source coordinates and historical decisions stay immutable. Current body
    positions are rebased; no block, line or heading is inserted or removed.
    """
    path=DATA/"author-ch24-source-policy.json";raw=path.read_bytes()
    if digest(raw)!=SOURCE24_POLICY_SHA256:raise ValueError("Chapter24-source policy changed")
    policy=json.loads(raw)
    if policy["source_sha256"]!=EXPECTED or digest(s.encode())!=EXPECTED:raise ValueError("Chapter24-source original source changed")
    if policy["baseline_model_sha256"]!=SOURCE24_BASELINE_SHA256 or digest((json.dumps(m,ensure_ascii=False,indent=2)+"\n").encode())!=SOURCE24_BASELINE_SHA256:raise ValueError("Chapter24-source baseline model changed")
    if policy["baseline_body_sha256"]!=SOURCE24_BODY_SHA256 or digest("".join(c["body"] for c in m["chapters"]).encode())!=SOURCE24_BODY_SHA256:raise ValueError("Chapter24-source baseline body changed")
    if policy["status"]!="author_explicitly_confirmed" or policy["authorization"]["answer"]!="好，没问题":raise ValueError("Chapter24-source authority missing")
    expected=[(24,33,"恰当很走来","恰值焙茗走来")]
    if [(q["chapter"],q["block_index"],q["original"],q["proposed"]) for q in policy["records"]]!=expected:raise ValueError("Chapter24-source permitted scope changed")
    for q in policy["records"]:
        if digest(m["chapters"][q["chapter"]-1]["blocks"][q["block_index"]]["text"].encode())!=q["block_sha256"]:raise ValueError("Chapter24-source baseline block changed")
    changes={}
    for q in reversed(policy["records"]):
        c=m["chapters"][q["chapter"]-1];block=c["blocks"][q["block_index"]];a,z=q["source_start_char"],q["source_end_char"];lo,hi=q["body_start"],q["body_end"]
        if s[a:z]!=q["original"] or s[a-20:a]!=q["context_before"] or s[z:z+20]!=q["context_after"]:raise ValueError("Chapter24-source exact source anchor changed")
        if c["body"][lo:hi]!=q["original"]:raise ValueError("Chapter24-source exact body anchor changed")
        chars=selection_source_chars(c,s)
        if [p for ch,p in chars[lo:hi]]!=list(range(a,z)):raise ValueError("Chapter24-source source/body mapping changed")
        if any(x["source_start_char"]<z and a<x["source_end_char"] for x in c["author_changes"]):raise ValueError("Chapter24-source overlaps earlier emendation")
        before=c["body"];delta=len(q["proposed"])-len(q["original"]);local=lo-block["body_start"]
        block["text"]=block["text"][:local]+q["proposed"]+block["text"][local+len(q["original"]):];block["author_change_ids"].append(q["id"])
        c["body"]=before[:lo]+q["proposed"]+before[hi:];c["body_sha256"]=digest(c["body"].encode())
        # Current offsets only. Historical policy records retain their own hashes.
        for item in c["blocks"]+c["layout_ranges"]+c["author_layout_ranges"]+c.get("editorial_note_exclusion_spans",[])+c.get("readable_operation_spans",[]):
            for key in ("body_start","body_end"):
                if key in item and item[key]>=hi:item[key]+=delta
        if any(layout["start_char"]<z and a<layout["end_char"] for layout in c["layout_ranges"]+c["author_layout_ranges"]):raise ValueError("Chapter24-source unexpected controlled layout overlap")
        change=dict(q,title="第24回焙茗句可读性校正",status="author_approved",applied=True,mode="replace",authorization_type="author_explicit_chapter24_source_decision",decision_file=path.name,decision_sha256=SOURCE24_POLICY_SHA256)
        c["author_changes"].append(change);changes[q["id"]]=change
        chars[lo:hi]=[(ch,a) for ch in q["proposed"]]
        c["author_change_spans"]=author_change_spans(chars,c["author_changes"])
        if c["body"][:lo]+q["original"]+c["body"][lo+len(q["proposed"]):]!=before:raise ValueError("Chapter24-source inverse failed")
        if "".join(b["text"] for b in c["blocks"])!=c["body"]:raise ValueError("Chapter24-source block/body mismatch")
        if any(c["body"][b["body_start"]:b["body_end"]]!=b["text"] for b in c["blocks"]):raise ValueError("Chapter24-source block offsets differ")
        selection_source_chars(c,s)
    m["author_emendations"].extend(changes[q["id"]] for q in policy["records"])
    m["emendation_authority_counts"]=dict(individually_confirmed=157,user_delegated_readability_selection=40,total_semantic_changes=197,applied_occurrence_records=198)
    m["chapter24_source_decision"]=dict(policy_id=policy["id"],path=path.name,sha256=SOURCE24_POLICY_SHA256,baseline_model_sha256=SOURCE24_BASELINE_SHA256,baseline_body_sha256=SOURCE24_BODY_SHA256,records=policy["records"],semantic_change_count_delta=1,occurrence_count_delta=1,body_codepoint_delta=1,layout_range_delta=0)
    if len(m["author_emendations"])!=198 or sum(len(c["body"]) for c in m["chapters"])!=586210 or sum(len(c["blocks"]) for c in m["chapters"])!=4394:raise ValueError("Chapter24-source aggregate invariant failed")
    return m


SOURCE28_POLICY_SHA256='89931f67985055dbb5d54b585bf84e4d774d5380f7029c9239cc9f10b6bdcc9d'
SOURCE28_BASELINE_SHA256='cf2abb6fa37ffbf49e411608a79b89f0bf2d27f0dc69800d597ba70154ca2758'
SOURCE28_BODY_SHA256='858c647e253c66e28caea86251e7e397ddd6e366b9a421dbba324b756a9e24a1'

def apply_chapter28_source_decisions(m,s):
    """Add one independent verse and correct one glyph on a frozen baseline.

    Original-source coordinates remain immutable. The inserted display block has
    a zero-width original-source boundary and explicit external-text provenance.
    The anchor-replacement audit record replays the unchanged anchor plus the
    added verse; it never asserts the added line existed in the original TXT.
    """
    path=DATA/"author-ch28-source-policy.json";raw=path.read_bytes()
    if digest(raw)!=SOURCE28_POLICY_SHA256:raise ValueError("Chapter28-source policy changed")
    policy=json.loads(raw)
    if policy["source_sha256"]!=EXPECTED or digest(s.encode())!=EXPECTED:raise ValueError("Chapter28-source original source changed")
    if digest((json.dumps(m,ensure_ascii=False,indent=2)+"\n").encode())!=SOURCE28_BASELINE_SHA256:raise ValueError("Chapter28-source baseline model changed")
    if digest("".join(c["body"] for c in m["chapters"]).encode())!=SOURCE28_BODY_SHA256:raise ValueError("Chapter28-source baseline body changed")
    if policy["status"]!="author_explicitly_confirmed" or policy["authorization"]["answer"]!="同意，这两处都没问题":raise ValueError("Chapter28-source authority missing")
    q1,q2=policy["records"];c=m["chapters"][27];before=c["body"]
    if [(q["chapter"],q["block_index"],q["original"],q["proposed"]) for q in (q1,q2)]!=[(28,43,"滴不尽相思血泪抛红豆，","滴不尽相思血泪抛红豆，开不完春柳春花满画楼，"),(28,124,"玉诀扇坠","玉玦扇坠")]:raise ValueError("Chapter28-source permitted scope changed")
    if c["author_changes"] or c["author_change_spans"]:raise ValueError("Chapter28-source earlier changes require explicit migration")
    for q in (q1,q2):
        a,z=q["source_start_char"],q["source_end_char"]
        if s[a:z]!=q["original"] or s[a-20:a]!=q["context_before"] or s[z:z+20]!=q["context_after"]:raise ValueError("Chapter28-source original anchor changed")
        if digest(c["blocks"][q["block_index"]]["text"].encode())!=q["block_sha256"]:raise ValueError("Chapter28-source block changed")
        if before[q["body_start"]:q["body_end"]]!=q["original"]:raise ValueError("Chapter28-source body anchor changed")
    # First correct the later phrase, so the input positions still mean the frozen baseline.
    jade=c["blocks"][q2["block_index"]];jade["text"]=jade["text"].replace(q2["original"],q2["proposed"])
    jade["author_change_ids"].append(q2["id"])
    body=before[:q2["body_start"]]+q2["proposed"]+before[q2["body_end"]:]
    left,right=c["blocks"][43:45];at=q1["body_end"];addition=q1["inserted_text"];delta=len(addition)
    if right["text"]!="睡不稳纱窗风雨黄昏后，" or digest(right["text"].encode())!=q1["right_block_sha256"] or left["end_char"]!=right["start_char"] or left["body_end"]!=right["body_start"]:raise ValueError("Chapter28-source insertion boundary changed")
    layout=next(r for r in c["layout_ranges"] if r["id"]==left["layout_id"])
    if layout["id"]!="T28-003" or len([b for b in c["blocks"] if b.get("layout_id")==layout["id"]])!=9:raise ValueError("Chapter28-source song layout changed")
    for b in c["blocks"]:
        if b["body_start"]>=at:b["body_start"]+=delta;b["body_end"]+=delta
    for r in c["layout_ranges"]+c["author_layout_ranges"]:
        if r is layout:
            local=at-r["body_start"];r["exact_body_text"]=r["exact_body_text"][:local]+addition+r["exact_body_text"][local:];r["body_end"]+=delta
            r["line_break_after_body_offsets"]=[x if x<=local else x+delta for x in r["line_break_after_body_offsets"]]+[local+delta]
            r["line_break_after_body_offsets"].sort();r["author_emendation_ids"].append(q1["id"])
            r["editorial_insertion"]={"id":q1["id"],"text":addition,"source_insertion_char":q1["source_insertion_char"],"source_mapping":"editorial_addition_absent_from_original_source","public_references":policy["public_references"],"punctuation_note":q1["punctuation_note"]}
        elif r["body_start"]>=at:r["body_start"]+=delta;r["body_end"]+=delta
        elif r["body_end"]>at:raise ValueError("Chapter28-source unexpected overlapping layout")
    added=dict(start_char=q1["source_insertion_char"],end_char=q1["source_insertion_char"],body_start=at,body_end=at+delta,text=addition,kind="verse",layout_id=layout["id"],layout_first=False,layout_last=False,source_mapping="editorial_addition_absent_from_original_source",author_change_ids=[q1["id"]],public_references=policy["public_references"])
    left["author_change_ids"].append(q1["id"])
    c["blocks"].insert(44,added);c["body"]=body[:at]+addition+body[at:];c["body_sha256"]=digest(c["body"].encode())
    changes=[]
    for q,title in ((q1,"第28回《红豆曲》补一独立行"),(q2,"第28回玉玦扇坠字形校正")):
        changes.append(dict(q,title=title,status="author_approved",applied=True,mode="replace",authorization_type="author_explicit_chapter28_source_decision",decision_file=path.name,decision_sha256=SOURCE28_POLICY_SHA256))
    c["author_changes"]=changes
    chars=selection_source_chars(c,s);c["author_change_spans"]=author_change_spans(chars,changes)
    if c["body"].replace(addition,"",1).replace(q2["proposed"],q2["original"],1)!=before:raise ValueError("Chapter28-source inverse failed")
    if "".join(b["text"] for b in c["blocks"])!=c["body"] or any(c["body"][b["body_start"]:b["body_end"]]!=b["text"] for b in c["blocks"]):raise ValueError("Chapter28-source block offsets differ")
    m["author_emendations"].extend(changes)
    m["emendation_authority_counts"]=dict(individually_confirmed=159,user_delegated_readability_selection=40,total_semantic_changes=199,applied_occurrence_records=200)
    m["chapter28_source_decisions"]=dict(policy_id=policy["id"],path=path.name,sha256=SOURCE28_POLICY_SHA256,baseline_model_sha256=SOURCE28_BASELINE_SHA256,baseline_body_sha256=SOURCE28_BODY_SHA256,records=policy["records"],public_references=policy["public_references"],semantic_change_count_delta=2,occurrence_count_delta=2,body_codepoint_delta=11,block_count_delta=1,layout_range_delta=0)
    if len(m["author_emendations"])!=200 or sum(len(x["body"]) for x in m["chapters"])!=586221 or sum(len(x["blocks"]) for x in m["chapters"])!=4395:raise ValueError("Chapter28-source aggregate invariant failed")
    return m



SOURCE3840_POLICY_SHA256='230b9a60b8d3fc58bbf6c8b5f70c055753f80ffafca79b09a3b6800a992771d7'
SOURCE3840_BASELINE_SHA256='564b8c77b570dda5a988b35d6842397320acc736c9a01a97fa4d4ba98038783c'

def apply_chapter38_40_source_decisions(m,s):
    """Two bounded public-transcription choices; immutable source and prior history."""
    path=DATA/"author-ch38-ch40-source-policy.json";raw=path.read_bytes()
    if digest(raw)!=SOURCE3840_POLICY_SHA256:raise ValueError("Chapter38/40 policy changed")
    policy=json.loads(raw)
    if digest(s.encode())!=EXPECTED or policy["source_sha256"]!=EXPECTED:raise ValueError("Chapter38/40 original source changed")
    if digest((json.dumps(m,ensure_ascii=False,indent=2)+"\n").encode())!=SOURCE3840_BASELINE_SHA256:raise ValueError("Chapter38/40 baseline model changed")
    if digest("".join(c["body"] for c in m["chapters"]).encode())!=policy["baseline_body_sha256"]:raise ValueError("Chapter38/40 baseline body changed")
    if policy["status"]!="delegated_readability_selection":raise ValueError("Chapter38/40 scope status changed")
    if [(q["chapter"],q["block_index"],q["original"],q["proposed"]) for q in policy["records"]]!=[(38,59,"霜痕","痕霜"),(40,10,"倚树","桃杏树")]:raise ValueError("Chapter38/40 scope changed")
    changes=[]
    for q in policy["records"]:
        c=m["chapters"][q["chapter"]-1];b=c["blocks"][q["block_index"]]
        a,z=q["source_start_char"],q["source_end_char"];lo,hi=q["body_start"],q["body_end"]
        if digest(b["text"].encode())!=q["block_sha256"]:raise ValueError("Chapter38/40 unit changed")
        if s[a:z]!=q["original"] or s[a-20:a]!=q["context_before"] or s[z:z+20]!=q["context_after"]:raise ValueError("Chapter38/40 source anchor changed")
        chars=selection_source_chars(c,s)
        if c["body"][lo:hi]!=q["original"] or [p for ch,p in chars[lo:hi]]!=list(range(a,z)):raise ValueError("Chapter38/40 body anchor changed")
        if any(x["source_start_char"]<z and a<x["source_end_char"] for x in c["author_changes"]):raise ValueError("Chapter38/40 overlaps prior choice")
        before=c["body"];delta=len(q["proposed"])-len(q["original"]);off=q["unit_offset"]
        if lo-b["body_start"]!=off or b["text"][off:off+len(q["original"])]!=q["original"]:raise ValueError("Chapter38/40 block anchor changed")
        b["text"]=b["text"][:off]+q["proposed"]+b["text"][off+len(q["original"]):]
        b["author_change_ids"].append(q["id"])
        c["body"]=before[:lo]+q["proposed"]+before[hi:];c["body_sha256"]=digest(c["body"].encode())
        for r in c["layout_ranges"]:
            if r["body_start"]<hi and lo<r["body_end"]:
                if q["chapter"]!=38 or r["id"]!="L38-091" or delta:raise ValueError("Unexpected controlled layout overlap")
                at=lo-r["body_start"]
                if r["exact_body_text"][at:at+len(q["original"])]!=q["original"]:raise ValueError("Poem current text mismatch")
                r["exact_body_text"]=r["exact_body_text"][:at]+q["proposed"]+r["exact_body_text"][at+len(q["original"]):]
                r["author_emendation_ids"].append(q["id"])
        # Only current chapter-local display positions; historical records stay immutable.
        for r in c["blocks"]+c["layout_ranges"]+c["author_layout_ranges"]:
            for key in ("body_start","body_end"):
                if key in r and r[key]>=hi:r[key]+=delta
        if delta and any(c.get(k) for k in ("readable_operation_spans","editorial_note_exclusion_spans")):raise ValueError("Unreviewed derived coordinate class")
        change=dict(q,status="adopted_editorial_choice",applied=True,mode="replace",authorization_type="delegated_public_transcription_selection",decision_file=path.name,decision_sha256=SOURCE3840_POLICY_SHA256)
        c["author_changes"].append(change);changes.append(change)
        chars=selection_source_chars(c,s);c["author_change_spans"]=author_change_spans(chars,c["author_changes"])
        if c["body"][:lo]+q["original"]+c["body"][lo+len(q["proposed"]):]!=before:raise ValueError("Chapter38/40 inverse failed")
        if "".join(b["text"] for b in c["blocks"])!=c["body"] or any(c["body"][b["body_start"]:b["body_end"]]!=b["text"] for b in c["blocks"]):raise ValueError("Chapter38/40 block/body mismatch")
    m["author_emendations"].extend(changes)
    m["emendation_authority_counts"]=dict(individually_confirmed=159,user_delegated_readability_selection=42,total_semantic_changes=201,applied_occurrence_records=202)
    m["chapter38_40_source_decisions"]=dict(policy_id=policy["id"],path=path.name,sha256=SOURCE3840_POLICY_SHA256,baseline_model_sha256=SOURCE3840_BASELINE_SHA256,records=policy["records"],semantic_change_count_delta=2,occurrence_count_delta=2,body_codepoint_delta=1,block_count_delta=0,layout_range_delta=0)
    if len(m["author_emendations"])!=202 or sum(len(c["body"]) for c in m["chapters"])!=586222 or sum(len(c["blocks"]) for c in m["chapters"])!=4395:raise ValueError("Chapter38/40 aggregate mismatch")
    return m


SOURCE384245_POLICY_SHA256='34304ee16c1be84f145b4fb41776e086deafe03bf38a58d9817b60dc9cf0a2d6'
SOURCE384245_BASELINE_SHA256='251c0a0421cb9a10b8fedc5444692879da74f451318012b90b430c374e886b82'

def apply_chapter38_42_45_source_decisions(m,s):
    """Three bounded public-transcription repairs; raw source/history stay immutable."""
    path=DATA/'author-ch38-ch42-ch45-source-policy.json';raw=path.read_bytes()
    if digest(raw)!=SOURCE384245_POLICY_SHA256:raise ValueError('Chapter38/42/45 policy changed')
    policy=json.loads(raw)
    if digest(s.encode())!=EXPECTED or policy['source_sha256']!=EXPECTED:raise ValueError('Chapter38/42/45 original source changed')
    if digest((json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode())!=SOURCE384245_BASELINE_SHA256:raise ValueError('Chapter38/42/45 baseline model changed')
    if policy['baseline_model_sha256']!=SOURCE384245_BASELINE_SHA256:raise ValueError('Chapter38/42/45 policy baseline changed')
    if digest(''.join(c['body'] for c in m['chapters']).encode())!=policy['baseline_body_sha256']:raise ValueError('Chapter38/42/45 baseline body changed')
    if policy['status']!='author_choice_and_delegated_readability_selection':raise ValueError('Chapter38/42/45 scope status changed')
    expected=[('hlm-c042-title','雅谬','雅谑'),('hlm-c042-b0032','顶绢箩四个，志箩四个','顶细绢箩四个，粗绢箩四个'),('hlm-c045-b0035','蓺','爇')]
    if [(q['unit_id'],q['original'],q['proposed']) for q in policy['records']]!=expected:raise ValueError('Chapter38/42/45 scope changed')
    changes=[]
    for q in policy['records']:
        c=m['chapters'][q['chapter']-1];a,z=q['source_start_char'],q['source_end_char'];off=q['unit_offset']
        if s[a:z]!=q['original'] or s[a-20:a]!=q['context_before'] or s[z:z+20]!=q['context_after']:raise ValueError('Chapter38/42/45 source anchor changed')
        change=dict(q,status='adopted_editorial_choice',applied=True,mode='replace',authorization_type='delegated_public_transcription_selection',decision_file=path.name,decision_sha256=SOURCE384245_POLICY_SHA256)
        if q['source_section']=='title':
            before=c['title']
            if digest(before.encode())!=q['unit_sha256'] or before[off:off+len(q['original'])]!=q['original']:raise ValueError('Chapter38/42/45 title changed')
            if not c['source_start']<=a<z<=c['body_start'] or c.get('title_changes'):raise ValueError('Chapter38/42/45 title overlaps prior choice')
            c['title']=before[:off]+q['proposed']+before[off+len(q['original']):]
            if c['title'][:off]+q['original']+c['title'][off+len(q['proposed']):]!=before:raise ValueError('Chapter38/42/45 title inverse failed')
            if digest(c['title'].encode())!=q['unit_sha256_after']:raise ValueError('Chapter38/42/45 title result changed')
            c['title_changes']=[change];changes.append(change)
            continue
        b=c['blocks'][q['block_index']];lo,hi=q['body_start'],q['body_end'];before=c['body']
        if digest(b['text'].encode())!=q['unit_sha256']:raise ValueError('Chapter38/42/45 unit changed')
        chars=selection_source_chars(c,s)
        if before[lo:hi]!=q['original'] or [p for ch,p in chars[lo:hi]]!=list(range(a,z)):raise ValueError('Chapter38/42/45 body anchor changed')
        if any(x['source_start_char']<z and a<x['source_end_char'] for x in c['author_changes']):raise ValueError('Chapter38/42/45 overlaps prior choice')
        if lo-b['body_start']!=off or b['text'][off:off+len(q['original'])]!=q['original']:raise ValueError('Chapter38/42/45 block anchor changed')
        delta=len(q['proposed'])-len(q['original'])
        b['text']=b['text'][:off]+q['proposed']+b['text'][off+len(q['original']):]
        b['author_change_ids'].append(q['id']);c['body']=before[:lo]+q['proposed']+before[hi:];c['body_sha256']=digest(c['body'].encode())
        for r in c['layout_ranges']:
            if r['body_start']<hi and lo<r['body_end']:
                if q['chapter']!=45 or r['id']!='L45-101' or delta:raise ValueError('Unexpected controlled layout overlap')
                at=lo-r['body_start']
                if r['exact_body_text'][at:at+len(q['original'])]!=q['original']:raise ValueError('Poem current text mismatch')
                r['exact_body_text']=r['exact_body_text'][:at]+q['proposed']+r['exact_body_text'][at+len(q['original']):]
                r['author_emendation_ids'].append(q['id'])
        # Only current chapter-local positions shift. Original-source coordinates and all historical policy records do not.
        for r in c['blocks']+c['layout_ranges']+c['author_layout_ranges']:
            for key in ('body_start','body_end'):
                if key in r and r[key]>=hi:r[key]+=delta
        if delta and any(c.get(k) for k in ('readable_operation_spans','editorial_note_exclusion_spans')):raise ValueError('Unreviewed derived coordinate class')
        c['author_changes'].append(change);changes.append(change)
        chars=selection_source_chars(c,s);c['author_change_spans']=author_change_spans(chars,c['author_changes'])
        if c['body'][:lo]+q['original']+c['body'][lo+len(q['proposed']):]!=before:raise ValueError('Chapter38/42/45 inverse failed')
        if ''.join(b['text'] for b in c['blocks'])!=c['body'] or any(c['body'][b['body_start']:b['body_end']]!=b['text'] for b in c['blocks']):raise ValueError('Chapter38/42/45 block/body mismatch')
        if digest(b['text'].encode())!=q['unit_sha256_after']:raise ValueError('Chapter38/42/45 unit result changed')
    m['author_emendations'].extend(changes)
    m['emendation_authority_counts']=dict(individually_confirmed=159,user_delegated_readability_selection=45,total_semantic_changes=204,applied_occurrence_records=205)
    m['chapter38_42_45_source_decisions']=dict(policy_id=policy['id'],path=path.name,sha256=SOURCE384245_POLICY_SHA256,baseline_model_sha256=SOURCE384245_BASELINE_SHA256,records=policy['records'],semantic_change_count_delta=3,occurrence_count_delta=3,body_codepoint_delta=2,title_codepoint_delta=0,block_count_delta=0,layout_range_delta=0)
    if len(m['author_emendations'])!=205 or sum(len(c['body']) for c in m['chapters'])!=586224 or sum(len(c['blocks']) for c in m['chapters'])!=4395:raise ValueError('Chapter38/42/45 aggregate mismatch')
    apply_chapter38_author_override(m,s,policy,path)
    return m


def effective_author_changes(c):
    """Replay active operations while leaving exact historical records untouched."""
    overrides=c.get('author_choice_overrides',[])
    if not overrides:return c['author_changes']
    if len(overrides)!=1 or c['number']!=38:raise ValueError('Unrecognized source override scope')
    q=overrides[0]
    if (q['id'],q['supersedes'],q['raw_source_text'],q['previous_reading'],q['adopted'])!=('SOURCE38-AUTHOR-OVERRIDE','SOURCE38-01','霜痕','痕霜','霜痕'):raise ValueError('Unrecognized source override decision')
    matches=[x for x in c['author_changes'] if x['id']==q['supersedes']]
    if len(matches)!=1:raise ValueError('Source override historical record missing')
    previous=matches[0]
    if any(previous[k]!=q[k] for k in ('source_start_char','source_end_char','body_start','body_end','unit_offset')) or previous['original']!=q['raw_source_text'] or previous['proposed']!=q['previous_reading']:raise ValueError('Source override historical anchor changed')
    if previous['decision_sha256']!=q['historical_policy']['sha256'] or q['historical_policy']['sha256']!=SOURCE3840_POLICY_SHA256:raise ValueError('Source override historical policy changed')
    return [x for x in c['author_changes'] if x['id']!=q['supersedes']]

def apply_chapter38_author_override(m,s,policy,path):
    q=policy['author_override'];c=m['chapters'][37];b=c['blocks'][59]
    if q['authorization']!={'type':'explicit_author_aesthetic_choice','quote':'我觉得“几霜痕”意境更好，算我的选择吧'}:raise ValueError('Author override authorization changed')
    if c.get('author_choice_overrides') or digest(b['text'].encode())!=q['unit_sha256']:raise ValueError('Author override baseline unit changed')
    old=next(x for x in c['author_changes'] if x['id']=='SOURCE38-01')
    if any(old[k]!=v for k,v in q['historical_record'].items()):raise ValueError('Author override historical record changed')
    a,z=q['source_start_char'],q['source_end_char'];lo,hi=q['body_start'],q['body_end'];off=q['unit_offset']
    if (a,z,lo,hi,off)!=(357025,357027,3895,3897,13):raise ValueError('Author override exact coordinates changed')
    if s[a:z]!=q['raw_source_text'] or s[a-20:a]!=q['context_before'] or s[z:z+20]!=q['context_after']:raise ValueError('Author override raw anchor changed')
    if c['body'][lo:hi]!=q['previous_reading'] or b['text'][off:off+2]!=q['previous_reading']:raise ValueError('Author override current anchor changed')
    previous_body=c['body'];previous_unit=b['text']
    c['body']=previous_body[:lo]+q['adopted']+previous_body[hi:];c['body_sha256']=digest(c['body'].encode())
    b['text']=previous_unit[:off]+q['adopted']+previous_unit[off+2:]
    b['author_change_ids'].remove(q['supersedes']);b['author_choice_override_ids']=[q['id']]
    layout=next(x for x in c['layout_ranges'] if x['id']=='L38-091');at=lo-layout['body_start']
    if layout['exact_body_text'][at:at+2]!=q['previous_reading']:raise ValueError('Author override poem anchor changed')
    layout['exact_body_text']=layout['exact_body_text'][:at]+q['adopted']+layout['exact_body_text'][at+2:]
    layout['author_emendation_ids'].remove(q['supersedes']);layout['author_choice_override_ids']=[q['id']]
    c['author_choice_overrides']=[q]
    chars=selection_source_chars(c,s)
    if [p for ch,p in chars[lo:hi]]!=[a,a+1]:raise ValueError('Author override raw mapping lost')
    c['author_change_spans']=author_change_spans(chars,effective_author_changes(c))
    c['author_choice_override_spans']=[dict(id=q['id'],supersedes=q['supersedes'],body_start=lo,body_end=hi,source_start_char=a,source_end_char=z,source_mapping='exact_original_source_restored')]
    if digest(b['text'].encode())!=q['unit_sha256_after'] or c['body'][:lo]+q['previous_reading']+c['body'][hi:]!=previous_body:raise ValueError('Author override inverse/result failed')
    if ''.join(x['text'] for x in c['blocks'])!=c['body'] or any(c['body'][x['body_start']:x['body_end']]!=x['text'] for x in c['blocks']):raise ValueError('Author override block/body mismatch')
    m['author_choice_overrides']=[q]
    m['emendation_authority_counts'].update(count_scope='historical_emendation_decisions_retained',superseded_semantic_changes=1,superseded_occurrence_records=1,current_active_semantic_changes=203,current_active_occurrence_records=204,additional_author_choice_overrides=1)
    m['chapter38_42_45_source_decisions']['author_override']=q
    m['chapter38_42_45_source_decisions']['current_effective_scope_note']='SOURCE38-01 remains immutable historical evidence; the explicit author choice supersedes its current application. Other historical decisions remain active.'

SOURCE4655_POLICY_SHA256 = '0d8322004725fc3d9ed92f38fb441d4450b69bd5a08f13863f3c7dec6524ec40'
SOURCE4655_BASELINE_SHA256 = '851e9e8885654fbdf2f63902007a4e011431726ba4ab1a1f3b0a7f89200c936c'

def apply_chapter46_55_source_decisions(m, s):
    """Append fifteen reviewed choices; preserve raw coordinates and historical layers."""
    policy_path = DATA / 'author-ch46-ch55-source-policy.json'
    raw_policy = policy_path.read_bytes()
    if digest(raw_policy) != SOURCE4655_POLICY_SHA256:
        raise ValueError('Chapter46-55 policy changed')
    policy = json.loads(raw_policy)
    if digest(s.encode()) != EXPECTED or policy['source_sha256'] != EXPECTED:
        raise ValueError('Chapter46-55 raw source changed')
    if digest((json.dumps(m, ensure_ascii=False, indent=2)+'\n').encode()) != SOURCE4655_BASELINE_SHA256:
        raise ValueError('Chapter46-55 prior model changed')
    if policy['baseline_model_sha256'] != SOURCE4655_BASELINE_SHA256:
        raise ValueError('Chapter46-55 baseline binding changed')
    if policy['status'] != 'delegated_public_transcription_selection':
        raise ValueError('Chapter46-55 choice authority changed')
    records = policy['records']
    expected = [('hlm-c046-b0006', '凤儿姐', '凤姐儿'), ('hlm-c047-b0033', '湘涟道', '湘莲道'), ('hlm-c049-b0035', '大红尚烧昭君套', '大红猩猩毡昭君套'), ('hlm-c050-b0046', '拗垤审夷险', '坳垤审夷险'), ('hlm-c051-b0059', '半旧大红尚毡的', '半旧大红猩猩毡的'), ('hlm-c051-b0060', '袭道：', '袭人道：'), ('hlm-c051-b0060', '你拿这尚毡的', '你拿这猩猩毡的'), ('hlm-c051-b0060', '不是尚烧就是', '不是猩猩毡就是'), ('hlm-c053-b0001', '非同小可。一面说', '非同小可。”一面说'), ('hlm-c053-b0001', '（口害）', '嗐'), ('hlm-c053-b0040', '又吩咐他：”', '又吩咐他：“'), ('hlm-c053-b0046', '几席洒', '几席酒'), ('hlm-c053-b0053', '游日棚', '游廊罩棚'), ('hlm-c053-b0054', '带了贾蓝', '带了贾菌'), ('hlm-c055-b0038', '风姐儿笑道', '凤姐儿笑道')]
    if [(q['unit_id'], q['original'], q['proposed']) for q in records] != expected:
        raise ValueError('Chapter46-55 exact scope changed')
    groups = {}
    for q in records:
        groups.setdefault(q['chapter'], []).append(q)
    changes = []
    for n, selected in groups.items():
        c = m['chapters'][n-1]
        before_body = c['body']
        chars = selection_source_chars(c, s)
        old_units = {q['block_index']: c['blocks'][q['block_index']]['text'] for q in selected}
        selected = sorted(selected, key=lambda q: q['body_start'])
        for left, right in zip(selected, selected[1:]):
            if left['body_end'] > right['body_start']:
                raise ValueError('Chapter46-55 overlapping choices')
        for q in selected:
            a, z = q['source_start_char'], q['source_end_char']
            lo, hi = q['body_start'], q['body_end']
            block = c['blocks'][q['block_index']]
            if s[a:z] != q['original'] or s[a-20:a] != q['context_before'] or s[z:z+20] != q['context_after']:
                raise ValueError('Chapter46-55 raw anchor changed')
            if before_body[lo:hi] != q['original'] or [p for ch,p in chars[lo:hi]] != list(range(a,z)):
                raise ValueError('Chapter46-55 body/raw mapping changed')
            if digest(old_units[q['block_index']].encode()) != q['unit_sha256']:
                raise ValueError('Chapter46-55 full before unit changed')
            if lo-block['body_start'] != q['unit_offset']:
                raise ValueError('Chapter46-55 unit offset changed')
            if any(x['source_start_char'] < z and a < x['source_end_char'] for x in effective_author_changes(c)):
                raise ValueError('Chapter46-55 overlaps historical choice')
        # These current coordinate classes are the only ones present in affected chapters.
        if any(c.get(key) for key in ('readable_operation_spans','editorial_note_exclusion_spans','author_choice_override_spans')):
            raise ValueError('Chapter46-55 unreviewed coordinate class')
        def translate(pos):
            if any(q['body_start'] < pos < q['body_end'] for q in selected):
                raise ValueError('Chapter46-55 structural boundary inside replacement')
            return pos + sum(len(q['proposed'])-len(q['original']) for q in selected if q['body_end'] <= pos)
        after_body = before_body
        for q in reversed(selected):
            lo, hi = q['body_start'], q['body_end']
            after_body = after_body[:lo]+q['proposed']+after_body[hi:]
            block = c['blocks'][q['block_index']]
            at = q['unit_offset']
            if block['text'][at:at+len(q['original'])] != q['original']:
                raise ValueError('Chapter46-55 descending unit application failed')
            block['text'] = block['text'][:at]+q['proposed']+block['text'][at+len(q['original']):]
        for block in c['blocks']:
            block['body_start'] = translate(block['body_start'])
            block['body_end'] = translate(block['body_end'])
        for r in c['layout_ranges'] + c['author_layout_ranges']:
            lo, hi = r['body_start'], r['body_end']
            overlapping = [q for q in selected if q['body_start'] < hi and lo < q['body_end']]
            if overlapping:
                if n != 50 or r['id'] != 'T50-015' or [q['id'] for q in overlapping] != ['SOURCE4655-B10-Q04']:
                    raise ValueError('Chapter46-55 unreviewed layout overlap')
                q = overlapping[0]
                if len(q['original']) != len(q['proposed']):
                    raise ValueError('Chapter46-55 verse length changed')
                r['author_emendation_ids'].append(q['id'])
            r['body_start'], r['body_end'] = translate(lo), translate(hi)
            if 'exact_body_text' in r:
                r['exact_body_text'] = after_body[r['body_start']:r['body_end']]
        c['body'] = after_body
        c['body_sha256'] = digest(after_body.encode())
        for q in selected:
            block = c['blocks'][q['block_index']]
            if digest(block['text'].encode()) != q['unit_sha256_after']:
                raise ValueError('Chapter46-55 combined full-unit result changed')
            change = dict(q, status='adopted_editorial_choice', applied=True, mode='replace',
                authorization_type='delegated_public_transcription_selection',
                decision_file=policy_path.name, decision_sha256=SOURCE4655_POLICY_SHA256)
            c['author_changes'].append(change)
            block['author_change_ids'].append(q['id'])
            changes.append(change)
        # Replay every old and new operation against raw coordinates, not guessed deltas.
        chars = selection_source_chars(c, s)
        c['author_change_spans'] = author_change_spans(chars, effective_author_changes(c))
        if ''.join(b['text'] for b in c['blocks']) != c['body']:
            raise ValueError('Chapter46-55 body/block concatenation differs')
        if any(c['body'][b['body_start']:b['body_end']] != b['text'] for b in c['blocks']):
            raise ValueError('Chapter46-55 body-derived block offsets differ')
        for r in c['layout_ranges']:
            if ''.join(b['text'] for b in c['blocks'] if b.get('layout_id')==r['id']) != r['exact_body_text']:
                raise ValueError('Chapter46-55 current layout reference differs')
    # Keep the exact historical issue objects; record their current resolution separately.
    issue_overlays = []
    for index, issue in enumerate(m['issues']):
        related = [q for q in records if q['chapter'] == issue.get('chapter')
            and issue['start_char'] < q['source_end_char'] and q['source_start_char'] < issue['end_char']]
        if related:
            issue_overlays.append(dict(historical_issue_index=index,
                historical_issue_sha256=digest((json.dumps(issue,ensure_ascii=False,indent=2)+'\n').encode()),
                chapter=issue['chapter'],source_start_char=issue['start_char'],source_end_char=issue['end_char'],
                choice_ids=[q['id'] for q in related],status='addressed_by_current_editorial_choice',
                note='原疑点对象及原先猜测原样保留为历史；本轮已按公开中文证据采用窄幅读法，不把原疑OCR等措辞当成已证实的形成机制。'))
    if len(issue_overlays) != 11:
        raise ValueError('Chapter46-55 historical issue overlay scope changed')
    m['author_emendations'].extend(changes)
    # Prior counts are embedded unchanged in this new transition, not rewritten in old policies.
    prior_counts = dict(m['emendation_authority_counts'])
    expected_counts = {'individually_confirmed':159,'user_delegated_readability_selection':45,
        'total_semantic_changes':204,'applied_occurrence_records':205,
        'current_active_semantic_changes':203,'current_active_occurrence_records':204}
    if any(prior_counts.get(k)!=v for k,v in expected_counts.items()):
        raise ValueError('Chapter46-55 prior authority counts changed')
    m['emendation_authority_counts'].update(user_delegated_readability_selection=60,
        total_semantic_changes=219,applied_occurrence_records=220,
        current_active_semantic_changes=218,current_active_occurrence_records=219)
    m['chapter46_55_source_decisions'] = dict(policy_id=policy['id'], path=policy_path.name,
        sha256=SOURCE4655_POLICY_SHA256, baseline_model_sha256=SOURCE4655_BASELINE_SHA256,
        records=records, historical_issue_resolution_overlay=issue_overlays, prior_authority_counts=prior_counts, choice_record_count_delta=15,
        affected_unit_count=12, body_codepoint_delta=4, block_count_delta=0, layout_range_delta=0,
        evidence_scope=policy['evidence_scope'], independent_proposal_review=policy['independent_proposal_review'],
        scope_note='The fifteen context-specific choices are counted separately. Earlier records, raw coordinates and author override remain historical and unchanged.')
    if len(m['author_emendations']) != 220 or sum(len(c['body']) for c in m['chapters']) != 586228:
        raise ValueError('Chapter46-55 totals differ')
    return m


CH002_POLICY_SHA256 = '74b1601c004b4c4297b76e3b62f7b1673894926f58c5b859b637c3193abe8eb9'
CH002_PARENT_MODEL_SHA256 = '90cadb9bb5a30ba194b97020a09bd570cab420d0b3e913ba7ccfefb059574331'

def apply_chapter2_author_ending(m, s):
    """One exact author-directed edition amendment, after the intact source4655 layer."""
    raw=(DATA/'author-ch002-ending-policy.json').read_bytes()
    if digest(raw)!=CH002_POLICY_SHA256:raise ValueError('Chapter2 author policy changed')
    policy=json.loads(raw)
    if digest((json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode())!=CH002_PARENT_MODEL_SHA256:raise ValueError('Chapter2 predecessor model changed')
    if policy['baseline_model_sha256']!=CH002_PARENT_MODEL_SHA256 or digest(s.encode())!=EXPECTED:raise ValueError('Chapter2 predecessor source changed')
    q=policy['record'];c=m['chapters'][1];b=c['blocks'][38]
    if (q['unit_id'],q['original'],q['proposed'])!=('hlm-c002-b0039','雨村忙回头看时——','雨村忙回头看时，要知是何人，且听下回分解。'):raise ValueError('Chapter2 author exact wording changed')
    if policy['authority']['type']!='explicit_author_edition_choice' or policy['authority']['not_ancient_restoration'] is not True:raise ValueError('Chapter2 authority changed')
    if len(c['blocks'])!=39 or b['text']!=q['original'] or b['kind']!='prose':raise ValueError('Chapter2 final block changed')
    if (b['body_start'],b['body_end'],b['start_char'],b['end_char'])!=(5964,5973,23190,23199):raise ValueError('Chapter2 paragraph boundary changed')
    if s[23190:23199]!=q['original'] or s[23170:23190]!=q['context_before'] or s[23199:23219]!=q['context_after']:raise ValueError('Chapter2 raw anchor changed')
    chars=selection_source_chars(c,s)
    if [p for ch,p in chars[5964:5973]]!=list(range(23190,23199)):raise ValueError('Chapter2 raw mapping changed')
    if any(x['source_start_char']<23199 and 23190<x['source_end_char'] for x in effective_author_changes(c)):raise ValueError('Chapter2 historical overlap')
    before_body=c['body'];prior_counts=dict(m['emendation_authority_counts'])
    if (len(m['author_emendations']),sum(len(x['body']) for x in m['chapters']))!=(220,586228):raise ValueError('Chapter2 parent aggregates changed')
    change=dict(q,status='author_approved',applied=True,mode='replace',authorization_type='explicit_author_edition_choice',decision_file='author-ch002-ending-policy.json',decision_sha256=CH002_POLICY_SHA256)
    b['text']=q['proposed'];b['body_end']=5985;b['author_change_ids'].append(q['id'])
    c['body']=before_body[:5964]+q['proposed'];c['body_sha256']=digest(c['body'].encode());c['author_changes'].append(change)
    chars=selection_source_chars(c,s);c['author_change_spans']=author_change_spans(chars,effective_author_changes(c))
    if ''.join(x['text'] for x in c['blocks'])!=c['body'] or c['body'][:5964]+q['original']!=before_body:raise ValueError('Chapter2 reversible body mapping failed')
    if any(c['body'][x['body_start']:x['body_end']]!=x['text'] for x in c['blocks']):raise ValueError('Chapter2 current block offsets differ')
    m['author_emendations'].append(change)
    for key in ('individually_confirmed','total_semantic_changes','applied_occurrence_records','current_active_semantic_changes','current_active_occurrence_records'):m['emendation_authority_counts'][key]+=1
    m['chapter2_author_ending']=dict(policy_id=policy['id'],path='author-ch002-ending-policy.json',sha256=CH002_POLICY_SHA256,baseline_model_sha256=CH002_PARENT_MODEL_SHA256,authority=policy['authority'],record=q,prior_authority_counts=prior_counts,body_codepoint_delta=12,block_count_delta=0,layout_range_delta=0)
    if (len(m['author_emendations']),sum(len(x['body']) for x in m['chapters']))!=(221,586240):raise ValueError('Chapter2 final aggregates differ')
    return m


SOURCE5665_POLICY_SHA256 = '42aae15b2f10a8e15fe53e1d12447c03d101c3643bbbbf99cf346af65cf117b0'
SOURCE5665_BASELINE_SHA256 = '57f230974dbc6737fb011c5722076f1ddd2e3ea36fa12e5acac85510b8a29241'


def apply_chapter56_65_source_decisions(m, s):
    """Sixteen approved source spans; no English acceptance or raw-source edits."""
    path = DATA / 'author-ch56-ch65-source-policy.json'
    raw = path.read_bytes()
    if digest(raw) != SOURCE5665_POLICY_SHA256:
        raise ValueError('Chapter56-65 policy changed')
    policy = json.loads(raw)
    if digest(s.encode()) != EXPECTED or policy['source_sha256'] != EXPECTED:
        raise ValueError('Chapter56-65 raw source changed')
    if digest((json.dumps(m, ensure_ascii=False, indent=2)+'\n').encode()) != SOURCE5665_BASELINE_SHA256 or policy['baseline_model_sha256'] != SOURCE5665_BASELINE_SHA256:
        raise ValueError('Chapter56-65 predecessor model changed')
    if policy['status'] != 'delegated_public_transcription_selection':
        raise ValueError('Chapter56-65 authority changed')
    records = policy['records']
    if len(records) != 16 or len({r['proposal_id'] for r in records}) != 14 or len({r['unit_id'] for r in records}) != 13:
        raise ValueError('Chapter56-65 bounded scope changed')
    changes = []
    for n in sorted({q['chapter'] for q in records}):
        c = m['chapters'][n-1]
        selected = [q for q in records if q['chapter'] == n]
        body_rows = sorted([q for q in selected if q['source_section'] == 'body'], key=lambda q:q['body_start'])
        title_rows = [q for q in selected if q['source_section'] == 'title']
        before_body = c['body'];before_title = c['title']
        chars = selection_source_chars(c, s)
        if any(c.get(key) for key in ('readable_operation_spans', 'editorial_note_exclusion_spans', 'author_choice_override_spans')):
            raise ValueError('Chapter56-65 unreviewed coordinate class')
        for a,z in zip(body_rows,body_rows[1:]):
            if a['body_end'] > z['body_start']:raise ValueError('Chapter56-65 overlapping choices')
        for q in selected:
            a,z=q['source_start_char'],q['source_end_char']
            if s[a:z] != q['original'] or s[a-20:a] != q['context_before'] or s[z:z+20] != q['context_after']:
                raise ValueError('Chapter56-65 raw anchor changed')
            if q['source_section'] == 'title':
                unit=before_title
                if not c['source_start'] <= a < z <= c['body_start']:raise ValueError('Chapter56-65 title outside raw heading')
            else:
                b=c['blocks'][q['block_index']];unit=b['text'];lo,hi=q['body_start'],q['body_end']
                if before_body[lo:hi] != q['original'] or [p for ch,p in chars[lo:hi]] != list(range(a,z)) or lo-b['body_start'] != q['unit_offset']:
                    raise ValueError('Chapter56-65 exact body/raw coordinates changed')
                if any(x['source_start_char'] < z and a < x['source_end_char'] for x in effective_author_changes(c)):
                    raise ValueError('Chapter56-65 overlaps historical choice')
            if digest(unit.encode()) != q['unit_sha256'] or unit[q['unit_offset']:q['unit_offset']+len(q['original'])] != q['original']:
                raise ValueError('Chapter56-65 full before unit changed')
        def translate(pos):
            if any(q['body_start'] < pos < q['body_end'] for q in body_rows):raise ValueError('Chapter56-65 boundary inside change')
            return pos + sum(len(q['proposed'])-len(q['original']) for q in body_rows if q['body_end'] <= pos)
        for q in reversed(body_rows):
            lo,hi=q['body_start'],q['body_end'];c['body']=c['body'][:lo]+q['proposed']+c['body'][hi:]
            b=c['blocks'][q['block_index']];a=q['unit_offset'];b['text']=b['text'][:a]+q['proposed']+b['text'][a+len(q['original']):]
        for q in sorted(title_rows,key=lambda q:q['unit_offset'],reverse=True):
            a=q['unit_offset'];c['title']=c['title'][:a]+q['proposed']+c['title'][a+len(q['original']):]
        for b in c['blocks']:b['body_start'],b['body_end']=translate(b['body_start']),translate(b['body_end'])
        for r in c['layout_ranges']+c['author_layout_ranges']:
            lo,hi=r['body_start'],r['body_end']
            if any(q['body_start'] < hi and lo < q['body_end'] for q in body_rows):raise ValueError('Chapter56-65 unexpected literary layout overlap')
            r['body_start'],r['body_end']=translate(lo),translate(hi)
            if 'exact_body_text' in r and c['body'][r['body_start']:r['body_end']] != r['exact_body_text']:raise ValueError('Chapter56-65 literary layout changed')
        c['body_sha256']=digest(c['body'].encode())
        for q in selected:
            unit=c['title'] if q['source_section']=='title' else c['blocks'][q['block_index']]['text']
            if digest(unit.encode()) != q['unit_sha256_after']:raise ValueError('Chapter56-65 combined result differs')
            change=dict(q,title='第%d回既审源文补校'%n,reason='既有独立中文审阅原样通过的最小可读性修复。',public_references=[q['public_reference']],status='adopted_editorial_choice',applied=True,mode='replace',authorization_type='delegated_public_transcription_selection',decision_file=path.name,decision_sha256=SOURCE5665_POLICY_SHA256)
            if q['source_section']=='title':c.setdefault('title_changes',[]).append(change)
            else:c['author_changes'].append(change);c['blocks'][q['block_index']]['author_change_ids'].append(q['id'])
            changes.append(change)
        if body_rows:c['author_change_spans']=author_change_spans(selection_source_chars(c,s),effective_author_changes(c))
        if ''.join(b['text'] for b in c['blocks']) != c['body'] or any(c['body'][b['body_start']:b['body_end']] != b['text'] for b in c['blocks']):raise ValueError('Chapter56-65 producer offsets differ')
    overlays=[]
    for i,issue in enumerate(m['issues']):
        related=[q for q in records if q['chapter']==issue.get('chapter') and issue['start_char'] < q['source_end_char'] and q['source_start_char'] < issue['end_char']]
        if related:overlays.append(dict(historical_issue_index=i,historical_issue_sha256=digest((json.dumps(issue,ensure_ascii=False,indent=2)+'\n').encode()),choice_ids=[q['id'] for q in related],status='addressed_by_current_editorial_choice'))
    prior=dict(m['emendation_authority_counts']);m['author_emendations'].extend(changes)
    for key in ('user_delegated_readability_selection','total_semantic_changes','current_active_semantic_changes'):m['emendation_authority_counts'][key]+=14
    for key in ('applied_occurrence_records','current_active_occurrence_records'):m['emendation_authority_counts'][key]+=16
    m['chapter56_65_source_decisions']=dict(policy_id=policy['id'],path=path.name,sha256=SOURCE5665_POLICY_SHA256,baseline_model_sha256=SOURCE5665_BASELINE_SHA256,records=records,prior_authority_counts=prior,historical_issue_resolution_overlay=overlays,scope=policy['scope'],evidence_scope=policy['evidence_scope'],independent_proposal_reviews=policy['independent_proposal_reviews'])
    if len(m['author_emendations']) != 237 or sum(len(c['body']) for c in m['chapters']) != 586232:raise ValueError('Chapter56-65 aggregate totals differ')
    return m


def model(apply_reading_policy=True,apply_editorial_notes=True,apply_readable=True,apply_opening=True,apply_display_fixes=True,apply_selections=True,apply_tail_lacuna=True,apply_title61=True,apply_six_source=True,apply_seven_source=True,apply_chapter24_source=True,apply_chapter28_source=True,apply_chapter38_40_source=True,apply_chapter38_42_45_source=True,apply_chapter46_55_source=True,apply_chapter2_ending=True,apply_chapter56_65_source=True):
    raw=(DATA/"sources/normalized.txt").read_bytes()
    assert digest(raw)==EXPECTED,"Source changed: do not silently rebase editorial decisions."
    s=raw.decode(); md=(DATA/"sources/layout.md").read_text()
    layout={"ranges":[],"deferred":[]};layout_sources=[]
    for filename in ["layout-ranges.json"]+[p.name for p in sorted(DATA.glob("layout-supplement*.json"))]:
        layout_path=DATA/filename;part=jread(layout_path)
        assert part["source_sha256"]==EXPECTED
        assert part["layout_source_sha256"]==digest((DATA/"sources/layout.md").read_bytes())
        provenance={k:v for k,v in part.items() if k not in ("ranges","deferred")}
        provenance.update(path=filename,sha256=digest(layout_path.read_bytes()),
                          verified_range_count=len(part["ranges"]),
                          verified_chapters=sorted({r["chapter"] for r in part["ranges"]}))
        layout_sources.append(provenance)
        layout["ranges"]+=part["ranges"];layout["deferred"]+=part.get("deferred",[])
    assert len({r["id"] for r in layout["ranges"]})==len(layout["ranges"])
    for r in layout["ranges"]:
        locate(s,r["chapter"],r["exact_text"],r["start_char"],r["end_char"])
        if r["kind"] not in {"verse","couplet","letter"}:
            raise ValueError(f"Unknown layout kind: {r['kind']}")
    layout_provenance=dict(layout_sources[0],sources=layout_sources,
        total_ranges=len(layout["ranges"]),mapping="Exact final-body anchors; source coordinates are covering spans.")

    ms=locations(s); mh=list(re.finditer(r"^## (第.+)$",md,re.M));assert len(mh)==80
    review_paths=sorted((DATA/"reviews").glob("review_*.json"))
    reviews=[jread(p) for p in review_paths]
    decisions=[];review_issues=[];batches=[]
    for r in reviews:
        assert r.get("source_sha256")==EXPECTED
        decisions+=r.get("decisions",[])
        review_issues+=r.get("issues",[])
        batches+=r.get("batches",[])
    # Canonical normalization is deliberately separate from raw reviewer records.
    canonical_path=DATA/"review-decisions.json"
    if not canonical_path.is_file():
        raise ValueError("Missing canonical review-decisions.json; do not fall back to automatic deletion.")
    normalized=jread(canonical_path)
    if not isinstance(normalized,list) or not normalized:
        raise ValueError("Canonical review decisions must be a nonempty list.")
    decisionmap={}
    allowed_actions={"remove_comment","move_metadata","move_frontmatter","keep_and_flag","keep_variant"}
    for d in normalized:
        a,b=locate(s,d["chapter"],d["exact_text"],d.get("start_char"),d.get("end_char"))
        if d["action"] not in allowed_actions:
            raise ValueError(f"Unknown decision action: {d['action']!r}")
        if (a,b) in decisionmap:
            raise ValueError(f"Duplicate decision range: {a}:{b}")
        decisionmap[(a,b)]=d
    approved=jread(DATA/"author-approved-emendations.json")
    emendations=approved["changes"];approval_batches=approved["batches"]
    assert approved["source_sha256"]==EXPECTED
    assert len({x["id"] for x in emendations})==len(emendations)
    changes_by_id={x["id"]:x for x in emendations};seen=set()
    for batch in approval_batches:
        filename=batch["proposal_file"]
        assert Path(filename).name==filename and filename.endswith(".json")
        proposal_path=DATA/filename;packet=jread(proposal_path)
        assert batch["source_sha256"]==packet["source_sha256"]==EXPECTED
        assert digest(proposal_path.read_bytes())==batch["proposal_sha256"]
        assert batch["references"]==packet.get("reference",packet.get("references",{}))
        assert batch["change_ids"]==[x["id"] for x in packet["proposals"]]
        verify_coverage_metadata_correction(batch,packet)
        verify_approval_delivery(batch,packet)
        for proposal in packet["proposals"]:
            ident=proposal["id"];assert ident not in seen;seen.add(ident)
            change=changes_by_id[ident]
            assert change["status"]=="author_approved" and change["applied"] is True
            substantive=lambda item:{k:v for k,v in item.items() if k not in ("status","status_zh","applied")}
            assert substantive(change)==substantive(proposal),("Unapproved change to proposal",ident)
            locate(s,change["chapter"],change["original"],change["source_start_char"],change["source_end_char"])
    assert seen==set(changes_by_id)
    emendations=[dict(x,adopted_body_text=adopted_body_text(x),body_text_derivation="omit_U+000A_only") if x.get("mode")=="replace_with_layout" else x for x in emendations]
    layout["ranges"],layout_provenance["author_anchor_overrides"]=apply_author_layout_anchor_overrides(layout["ranges"],emendations,s)
    author_layouts=author_layout_ranges(emendations)
    for left,right in zip(sorted(emendations,key=lambda x:x["source_start_char"]),sorted(emendations,key=lambda x:x["source_start_char"])[1:]):
        assert left["source_end_char"]<=right["source_start_char"],"Overlapping approved emendations"
    edits=[];issues=[];chapters=[];retained=[]
    def add(a,b,n,action,reason):
        assert a<b
        edits.append(dict(chapter=n,start_char=a,end_char=b,action=action,exact_text=s[a:b],reason=reason))
    front_start=ms[0].end()+len(re.sub(r"\s+","",mh[0][1]))
    front_end=s.index("列位看官：",front_start)
    add(front_start,front_end,1,"move_frontmatter","序、凡例、开卷自述及卷首诗完整另存；归位待作者决定。")
    for i,m in enumerate(ms):
        n=i+1;a=m.end();b=(ms[i+1].start() if n<80 else len(s));original=s[a:b].rstrip("\n")
        mdpart=md[mh[i].start():mh[i+1].start() if n<80 else len(md)]
        compact=re.sub(r"\s+","",mdpart.removeprefix("## "))
        assert compact==original,f"MD mismatch {n}"
        # Chapter 21's MD heading wraps mid-couplet and contains an inline comment.
        number_text=re.match(r"第[^回]+回",original)[0]
        cursor=len(number_text);visible=[]
        while len(visible)<16:
            if original[cursor]=="【":
                cursor=original.index("】",cursor)+1
            else:
                visible.append(original[cursor]);cursor+=1
        title=number_text+" "+"".join(visible[:8])+" "+"".join(visible[8:])
        titlecompact=number_text+"".join(visible)
        if n!=21:assert re.sub(r"\s+","",mh[i][1])==titlecompact
        body_start=a+cursor;body_end=a+len(original)
        for hit in re.finditer(r"【[^【】]*】",original):
            x,y=a+hit.start(),a+hit.end()
            if front_start<=x<front_end:continue
            d=decisionmap.get((x,y))
            label=re.split(r"[:：]",hit[0][1:-1],maxsplit=1)[0]
            if d:
                action=d["action"];reason=d["reason"]
            elif label in LABELS:
                action="remove_comment";reason="明确署名/位置标签的评语；全文原样进入移出记录。"
            else:
                action="keep_and_flag";reason="非标准括注尚待逐条审定，保守留在正文。"
            if action in ("remove_comment","move_metadata","move_frontmatter"):
                add(x,y,n,action,reason)
            else:
                retained.append(dict(chapter=n,start_char=x,end_char=y,text=hit[0],reason=reason,action=action))
        # Only bounded, known non-narrative materials are default removed.
        footer=re.search(r"[—-]+脂砚斋重评石头记[—-]+曹雪芹[—-]+$",original);assert footer
        add(a+footer.start(),a+footer.end(),n,"remove_footer","逐回重复页脚，原样留审计。")
        if n in (19,80):
            x=original.index("庚辰本此回无题。")+a
            add(x,x+len("庚辰本此回无题。"),n,"move_metadata","回目有无的版本说明，保留于校记。")
        chapters.append(dict(number=n,title=title,source_start=a,source_end=body_end,body_start=body_start,mdpart=mdpart))
    # Non-bracket reviewer decisions. Overlapping metadata decisions cannot eat body.
    known={(e["start_char"],e["end_char"]) for e in edits}
    bracket_ranges={(m.start(),m.end()) for m in re.finditer(r"【[^【】]*】",s)}
    for (a,b),d in decisionmap.items():
        if (a,b) in bracket_ranges or (a,b) in known or front_start<=a<b<=front_end:continue
        if d["action"] in ("remove_comment","move_metadata","move_frontmatter"):
            if "此处有缺文" in d["exact_text"]:
                issues.append(dict(chapter=d["chapter"],start_char=a,end_char=b,text=s[a:b],kind="缺文",severity="preserve",reason="正文缺文标记继续原样保留。"))
            else:add(a,b,d["chapter"],d["action"],d["reason"])
    for n,literal,reason in [(24,"笏叟。】","重复批署残片及孤立右括号。"),(62,"庚辰双行夹批：又下此四字。","无方括号但标签与边界明确的夹批。")]:
        c=chapters[n-1]
        if n==24:
            a=s.index("亥夏。畸笏叟。】笏叟。】",c["source_start"])+len("亥夏。畸笏叟。】")
        else:a=s.index(literal,c["source_start"],c["source_end"])
        if (a,a+len(literal)) not in {(e["start_char"],e["end_char"]) for e in edits}:
            add(a,a+len(literal),n,"remove_comment",reason)
    # Remove exact duplicate operations; nested intervals favor a reviewed covering move.
    unique={}
    for e in edits:unique[(e["start_char"],e["end_char"])]=e
    sorted_edits=sorted(unique.values(),key=lambda e:(e["start_char"],-e["end_char"]))
    edits=[]
    for e in sorted_edits:
        if edits and e["start_char"]<edits[-1]["end_char"]:
            if e["end_char"]<=edits[-1]["end_char"]:continue
            raise AssertionError(("overlapping decisions",edits[-1],e))
        edits.append(e)
    for i,e in enumerate(edits,1):
        e["id"]=f"E{i:04d}";e["line"]=e["chapter"];e["column_start"]=e["start_char"]-ms[e["chapter"]-1].start()+1
        e["context_before"]=s[max(0,e["start_char"]-35):e["start_char"]]
        e["context_after"]=s[e["end_char"]:e["end_char"]+35]
    for d in normalized:
        if d["action"]=="keep_and_flag":
            a,b=locate(s,d["chapter"],d["exact_text"],d.get("start_char"),d.get("end_char"))
            issues.append(dict(chapter=d["chapter"],start_char=a,end_char=b,text=d["exact_text"],kind=d.get("kind","待校"),severity=d.get("severity","review"),reason=d["reason"]))
    for n,c in enumerate(chapters,1):
        a,b=c["body_start"],c["source_end"]
        local=[e for e in edits if e["chapter"]==n]
        mask=[True]*(b-a)
        for e in local:
            for p in range(max(a,e["start_char"]),min(b,e["end_char"])):mask[p-a]=False
        chars=[(s[p],p) for p in range(a,b) if mask[p-a]]
        base_body="".join(ch for ch,p in chars)
        author_changes=[x for x in emendations if x["chapter"]==n]
        replacement_ends={}
        for change in sorted(author_changes,key=lambda x:x["source_start_char"],reverse=True):
            x,y=change["source_start_char"],change["source_end_char"]
            indices=[i for i,(_,pos) in enumerate(chars) if x<=pos<y]
            assert indices and indices==list(range(indices[0],indices[-1]+1))
            assert "".join(chars[i][0] for i in indices)==change["original"]
            chars[indices[0]:indices[-1]+1]=[(ch,x) for ch in adopted_body_text(change)]
            replacement_ends[x]=y
        body="".join(ch for ch,p in chars)
        c["author_change_spans"]=author_change_spans(chars,author_changes)
        # PDF hard-wrap boundaries that end a complete sentence can be reading breaks.
        boundaries=set();offset=c["source_start"];lines=c["mdpart"].splitlines()
        for line in lines:
            txt=re.sub(r"\s+","",line.removeprefix("## "))
            offset+=len(txt)
            if txt.endswith(("。","！","？","。”","！”","？”","。’","！’","？’")):boundaries.add(offset)
        blocks=[];buf=[];start=None;last=0
        for idx,(ch,pos) in enumerate(chars):
            if start is None:start=pos
            buf.append(ch);last=replacement_ends.get(pos,pos+1)
            nextpos=chars[idx+1][1] if idx+1<len(chars) else b
            eol=any(last<=edge<=nextpos for edge in boundaries)
            # Subdivide long display blocks at sentence ends only; not a textual emendation.
            terminal=ch in "。！？" and (idx+1==len(chars) or chars[idx+1][0] not in "”’」』")
            if (eol and len(buf)>=55) or (len(buf)>=250 and terminal) or idx+1==len(chars):
                blocks.append(dict(start_char=start,end_char=last,text="".join(buf),kind="prose"));buf=[];start=None
        blocks,resolved_layout=layout_blocks(body,chars,blocks,
            [r for r in layout["ranges"]+author_layouts if r["chapter"]==n],replacement_ends)
        c["layout_ranges"]=[r for r in resolved_layout if "author_emendation_id" not in r]
        c["author_layout_ranges"]=[r for r in resolved_layout if "author_emendation_id" in r]
        for block in blocks:
            block["source_mapping"]="covering_source_span"
            block["author_change_ids"]=[x["id"] for x in author_changes if block["start_char"]<x["source_end_char"] and x["source_start_char"]<block["end_char"]]
        assert "".join(x["text"] for x in blocks)==body
        assert not any(e["exact_text"]=="青板姊妹" for e in local)
        assert body.count("□")==sum(ch=="□" for ch,p in chars)
        c.update(body=body,base_body=base_body,author_changes=author_changes,blocks=blocks,edits=local,retained=[r for r in retained if r["chapter"]==n])
        # Flags stay separate from main text, with exact source coordinates.
        for match in re.finditer(r"□|（按：[^）]*缺[^）]*）|[^\u0000-\u007f]{0,14}\?/?font[^。！？]{0,100}",body):
            word=match[0];p=chars[match.start()][1];end=replacement_ends.get(chars[match.end()-1][1],chars[match.end()-1][1]+1)
            issue=dict(chapter=n,start_char=p,end_char=end,text=s[p:end],kind="缺损或异常字符",severity="review",reason="底本原样保留，未经作者确认不猜补。")
            if issue["text"]!=word:
                issue["clean_excerpt"]=word
                issue["reason"]+="此源范围跨过已移出批语；此处显示精确源摘录，去批后摘录另存clean_excerpt，不将批语放回正文。"
            issues.append(issue)
        c["body_sha256"]=digest(body.encode())
        # Replay clean text and removals to recover source chapter byte-for-byte after UTF-8 decoding.
        check=s[c["source_start"]:c["source_end"]]
        for e in reversed(local):
            x=e["start_char"]-c["source_start"];y=e["end_char"]-c["source_start"]
            assert check[x:y]==e["exact_text"];check=check[:x]+check[y:]
        assert check==re.sub(r"\s+","",c["title"])+base_body
        for change in author_changes:
            assert check.count(change["original"])==1
            check=check.replace(change["original"],adopted_body_text(change),1)
        assert check==re.sub(r"\s+","",c["title"])+body
        c.pop("mdpart")
    resolved_issue_archive=retain_resolved_source_issues(s,issues,emendations)
    raw_issue_coverage,review_context=cover_review_issues(s,list(zip([p.name for p in review_paths],reviews)),chapters,issues,retained,edits,layout["deferred"])
    supplemental_reviews,supplemental_issue_coverage=supplemental_review_issues(s,chapters,issues)
    for q in layout["deferred"]:
        if "start_char" in q and "end_char" in q:
            related=[x["id"] for x in emendations if x["chapter"]==q.get("chapter") and x["source_start_char"]<q["end_char"] and q["start_char"]<x["source_end_char"]]
            if related:
                q["related_author_emendations"]=related
                q["resolution_note"]="相关文字已按作者批准补校；此处仍保留原版式审查说明，不再描述当前字形。"
                q["original_status"]=q.get("status")
                q["status"]="author_layout_applied" if any(x["id"] in related and x.get("mode")=="replace_with_layout" for x in emendations) else "text_emended_layout_review_pending"
    for q in issues:
        related=[x for x in emendations if x["chapter"]==q["chapter"] and x["source_start_char"]<q["end_char"] and q["start_char"]<x["source_end_char"]]
        if related:
            q["related_author_emendations"]=[x["id"] for x in related]
            q["resolution_note"]="本源摘录对应的相关位置已按作者批准补校；原摘录留存供对照，不再作为正文现状。"
    for c in chapters:
        c["issues"]=[q for q in issues if q["chapter"]==c["number"]]
    result=dict(source_sha256=EXPECTED,title=TITLE,chapters=chapters,edits=edits,issues=issues,retained=retained,frontmatter=s[front_start:front_end],review_files=len(reviews),batches=batches,author_emendations=emendations,approval_batches=approval_batches,raw_issue_coverage=raw_issue_coverage,resolved_issue_archive=resolved_issue_archive,review_context=review_context,supplemental_reviews=supplemental_reviews,supplemental_issue_coverage=supplemental_issue_coverage,layout_provenance=layout_provenance,layout_deferred=layout["deferred"])
    if apply_reading_policy:
        result=apply_reading_scope(result,s)
        if apply_editorial_notes:result=apply_editorial_note_scope(result,s)
    if apply_readable:result=apply_readable_adoptions(result,s)
    if apply_opening and apply_readable and apply_reading_policy and apply_editorial_notes:result=apply_opening_restoration(result,s)
    if apply_display_fixes and apply_readable and apply_reading_policy and apply_editorial_notes:result=apply_paragraph_boundary_fixes(result,s)
    if apply_selections and apply_opening and apply_display_fixes and apply_readable and apply_reading_policy and apply_editorial_notes:result=apply_poem_couplet_selections(result,s)
    if apply_tail_lacuna and apply_selections and apply_opening and apply_display_fixes and apply_readable and apply_reading_policy and apply_editorial_notes:result=apply_tail_lacuna_decisions(result,s)
    if apply_title61 and apply_tail_lacuna and apply_selections and apply_opening and apply_display_fixes and apply_readable and apply_reading_policy and apply_editorial_notes:result=apply_title61_decision(result,s)
    if apply_six_source and apply_title61 and apply_tail_lacuna and apply_selections and apply_opening and apply_display_fixes and apply_readable and apply_reading_policy and apply_editorial_notes:result=apply_six_source_decisions(result,s)
    if apply_seven_source and "six_source_decisions" in result:result=apply_seven_source_decisions(result,s)
    if apply_chapter24_source and "seven_source_decisions" in result:result=apply_chapter24_source_decision(result,s)
    if apply_chapter28_source and "chapter24_source_decision" in result:result=apply_chapter28_source_decisions(result,s)
    if apply_chapter38_40_source and "chapter28_source_decisions" in result:result=apply_chapter38_40_source_decisions(result,s)
    if apply_chapter38_42_45_source and "chapter38_40_source_decisions" in result:result=apply_chapter38_42_45_source_decisions(result,s)
    if apply_chapter46_55_source and "chapter38_42_45_source_decisions" in result:result=apply_chapter46_55_source_decisions(result,s)
    if apply_chapter2_ending and "chapter46_55_source_decisions" in result:result=apply_chapter2_author_ending(result,s)
    if apply_chapter56_65_source and "chapter2_author_ending" in result:result=apply_chapter56_65_source_decisions(result,s)
    return result

def shell(title,description,content,filename="index.html"):
    return f'''<!doctype html>
<html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{E(title)} — Non Dubito</title><meta name="description" content="{E(description)}"><link rel="icon" href="../../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="reader.css"><script defer src="reader.js"></script></head><body><a class="skip" href="#main">跳到正文</a><header class="site-header"><a class="brand" href="../../index.html">Non <span>Dubito</span></a><nav aria-label="网站导航"><a href="../../essays/literature/hlm/index.html">红楼梦专题</a><a href="index.html">前八十回</a><a href="edition.html">版本说明</a></nav><span class="review-badge">中文审读稿 · 未发布</span></header><main id="main">{content}</main><footer><p>{E(TITLE)} · 据用户所供脂批汇校文本整理。此处保留底本缺损和待定异文，不冒称已校定原稿。</p><a href="../../originals/hongloumeng/index.html">另读秦汉原创续写（第八十一回起，并非曹雪芹原作）</a></footer></body></html>'''

@tracked_html
def render(m):
    pages={};cs=m["chapters"]
    metadata_notes=[]
    for c in cs:
        n=c["number"];stem=f"ch{n:03d}"
        noteitems=c["issues"]+c["retained"]
        notes="".join(f'<li><strong>{E(q.get("kind","保留异文"))}</strong>：{E(q.get("reason","")+supplemental_note_provenance(q)+(" "+q["resolution_note"] if "resolution_note" in q else ""))}<span class="source-loc">原文字符 {q["start_char"]}–{q["end_char"]}</span><q>{E(q.get("text",q.get("exact_text","")))}</q></li>' for q in noteitems)
        localmeta=[e for e in c["edits"] if e["action"] in ("move_metadata","move_frontmatter")]
        metatext="".join(f'<li>{E(e["exact_text"])}<span class="source-loc">{E(e["reason"])}</span></li>' for e in localmeta)
        corrections="".join(f'<li><strong>{E(x["id"]+" "+x["title"])}</strong><p>{E("依用户委托选择。" if x.get("authorization_type")=="user_delegated_readability_selection" else ("本版编辑选择。" if x.get("authorization_type")=="delegated_public_transcription_selection" else "作者已确认采用。"))}{E(correction_reference(x,m["approval_batches"]))}</p><p>原底本上下文，可能含批语。上文：</p><q>{E(x["context_before"])}</q><p>底本：</p><q>{E(x["original"])}</q><p>采用：</p><q>{correction_adopted_html(x)}</q><p>原底本下文：</p><q>{E(x["context_after"])}</q><p class="source-loc">源范围 {x["source_start_char"]}–{x["source_end_char"]}{E("（本版作者指定改写范围）" if x.get("authorization_type")=="explicit_author_edition_choice" else "（原损坏或缺文位置）")}。补校段落的坐标表示覆盖的原源范围，不是补入文字与底本逐字符对齐；同一补校分成两个显示段时，可共享这段源范围和补校编号。</p></li>' for x in c["author_changes"]+[q for q in c.get("title_changes",[]) if q.get("decision_file") in ("author-ch38-ch42-ch45-source-policy.json","author-ch56-ch65-source-policy.json")])
        if c.get("author_choice_overrides"):
            q=c["author_choice_overrides"][0]
            corrections=corrections.replace("SOURCE38-01 ","SOURCE38-01（历史选读，现已由作者覆盖） ").replace("（原损坏或缺文位置）","（历史选读范围，不据此认定原文讹误）")
            corrections+='<li><strong>'+E(q["id"]+' 作者现行选择')+'</strong><p>'+E(q["reason"])+'</p><p>作者原话：'+E(q["authorization"]["quote"])+'</p><p>当前采用：'+E(q["adopted"])+'；此前读法：'+E(q["previous_reading"])+'。旧 SOURCE38-01 只保留为历史。</p></li>'
        paragraphs=[]
        for i,block in enumerate(c["blocks"],1):
            flags=[q for q in c["issues"] if block["start_char"]<=q["start_char"]<block["end_char"]]
            classes=[block["kind"]]
            if "author_layout_id" in block:
                classes.append("author-diagram")
                if block["author_layout_heading"]:classes.append("diagram-heading")
                if block["author_layout_group_start"] and block["author_layout_line"]:classes.append("diagram-group-start")
            if block.get("layout_first"):classes.append("layout-first")
            if block.get("layout_last"):classes.append("layout-last")
            cls=' class="'+" ".join(classes)+'"'
            layout_attrs=(f' data-layout-id="{E(block["layout_id"])}"'
                          f' data-layout-first="{str(block["layout_first"]).lower()}"'
                          f' data-layout-last="{str(block["layout_last"]).lower()}"') if "layout_id" in block else ""
            if "author_layout_id" in block:
                layout_attrs+=f' data-author-layout-id="{E(block["author_layout_id"])}" data-author-layout-line="{block["author_layout_line"]}" data-author-layout-group-start="{str(block["author_layout_group_start"]).lower()}"'
            if "opening_restoration_id" in block:layout_attrs+=f' data-opening-restoration-id="{E(block["opening_restoration_id"])}"'
            paragraphs.append(f'<p id="p{i:03d}" data-body-start="{block["body_start"]}" data-body-end="{block["body_end"]}" data-kind="{block["kind"]}" data-source-start="{block["start_char"]}" data-source-end="{block["end_char"]}" data-source-mapping="{block["source_mapping"]}" data-author-change-ids="{E(" ".join(block["author_change_ids"]))}"{layout_attrs}{cls}>{E(block["text"])}</p>')
        previous=f'<a rel="prev" href="ch{n-1:03d}.html">← 第{n-1}回</a>' if n>1 else '<span>第一回</span>'
        following=f'<a rel="next" href="ch{n+1:03d}.html">第{n+1}回 →</a>' if n<80 else '<a href="../../originals/hongloumeng/index.html">转入原创续写目录 →</a>'
        notesblock=(f'<details class="reading-notes" id="notes"><summary>本回底本疑点与保留材料 · {len(noteitems)}项</summary><ul>{notes}</ul></details>' if notes else '')
        if metatext:notesblock+=f'<details class="reading-notes"><summary>版本校记及附录材料 · {len(localmeta)}项</summary><ul>{metatext}</ul></details>'
        if corrections and any(x.get("authorization_type")=="delegated_public_transcription_selection" for x in c["author_changes"]):notesblock='<details class="reading-notes" id="corrections"><summary>本版补校 · '+str(len(c["author_changes"])+sum(q.get("decision_file")=="author-ch38-ch42-ch45-source-policy.json" for q in c.get("title_changes",[])))+'项</summary><ul>'+corrections+'</ul></details>'+notesblock
        elif corrections:notesblock='<details class="reading-notes" id="corrections"><summary>作者已确认的补校 · '+str(len(c["author_changes"])+sum(q.get("decision_file")=="author-ch38-ch42-ch45-source-policy.json" for q in c.get("title_changes",[])))+'项</summary><ul>'+corrections+'</ul></details>'+notesblock
        alert=f'<p class="chapter-alert">本回有 {len(noteitems)} 项底本疑点或待定材料，原文未擅改。<a href="#notes">查看审查记录</a></p>' if noteitems else '<p class="edition-note">本回已去除有明确边界的批语；去批审查不等于逐字校定。</p>'
        heading=" ".join('<span class="'+("chapter-number" if i==0 else "chapter-couplet")+'">'+E(part)+'</span>' for i,part in enumerate(c["title"].split(" ")))
        content=f'<article><header class="chapter-head"><p class="eyebrow">红楼梦 · 前八十回</p><p class="edition-name">{TITLE}</p><h1>{heading}</h1><div class="reader-tools"><button type="button" data-font="minus" aria-label="缩小正文字号">字 −</button><button type="button" data-font="reset" aria-label="恢复正文字号">默认字号</button><button type="button" data-font="plus" aria-label="放大正文字号">字 ＋</button><a href="#chapter-nav">至回末</a></div></header><div class="novel-text">{"".join(paragraphs)}</div></article><nav class="chapter-nav" id="chapter-nav" aria-label="章回翻页">{previous}<a href="index.html#batch{(n-1)//5+1:02d}">回目目录</a>{following}</nav>'
        pages[TARGET/(stem+".html")]=shell(c["title"]+" · "+TITLE,"前八十回中文去批审读稿，保留缺文和待定版本材料。",content,stem+".html")
        pages[DATA/"generated/audit"/(stem+".json")]=json.dumps({k:v for k,v in c.items() if k not in ("body","base_body","blocks")},ensure_ascii=False,indent=2)+"\n"
    batchhtml=[]
    for start in range(1,81,5):
        cards=[]
        for c in cs[start-1:start+4]:
            count=len(c["issues"])+len(c["retained"])
            cards.append(f'<li data-chapter="{c["number"]}" data-title="{E(c["title"],quote=True)}"><a href="ch{c["number"]:03d}.html"><span class="chapter-index">{c["number"]:02d}</span><span>{E(c["title"])}</span></a><small>{"中文审读稿"}</small></li>')
        batchhtml.append(f'<section class="chapter-batch" id="batch{(start-1)//5+1:02d}"><h2>第{start}—{start+4}回</h2><ol>{"".join(cards)}</ol></section>')
    intro=f'<header class="book-head"><p class="eyebrow">NON DUBITO · 中文古典阅读</p><p class="book-title">红楼梦</p><h1>{TITLE}</h1><p class="deck">前八十回 · 去脂批审读稿</p><p class="edition-note">这个版本名称表示大知的编辑项目。当前所据为用户提供、含甲戌、庚辰、蒙府等批语的汇校文本，不能据此称作庚辰抄本的完整复刻。</p><p class="chapter-alert">底本存在缺字、缺诗及部分编码损坏，正逐项核查。已去除边界明确的批语；未经作者审定的改字不进入正文。本稿仅供本地审读，尚未发布。</p><div class="book-actions"><a class="primary-link" href="ch001.html">从第一回开始</a><a href="edition.html">查看版本与校正原则</a></div></header><section class="catalog"><div class="catalog-head"><h2>八十回回目</h2><label>查找回目<input type="search" id="chapter-search" placeholder="回数或题名" autocomplete="off"></label></div><p id="search-status" class="edition-note" aria-live="polite">按每五回分组。只呈现章节正文。</p>{"".join(batchhtml)}</section><section class="continuation"><h2>八十回以后</h2><p>秦汉原创第八十一至第一百一十回另设目录。那是当代续写，不是曹雪芹佚稿，也不与本版前八十回混作同一作者的原作。</p><a href="../../originals/hongloumeng/index.html">进入原创续写目录</a></section>'
    pages[TARGET/"index.html"]=shell("红楼梦 · "+TITLE,"前八十回去脂批中文审读稿，明确区分古典原著与当代原创续写。",intro)
    preface="<header class='chapter-head'><p class='eyebrow'>底本附录 · 位置待定</p><h1>序例与卷首诗</h1><p class='edition-note'>以下完整保留第一回之前的原材料，包含凡例内嵌的批语。此页是原样存档，不是已经去批的正文；开卷自述正文已按作者决定恢复；此处只保留原始整段作为历史底本，不代表当前阅读范围。</p></header><div class='archive-text'>"+E(m["frontmatter"])+"</div><nav class='chapter-nav'><a href='index.html'>回到目录</a><a href='ch001.html'>读第一回</a></nav>"
    pages[DATA/"generated/audit/preface.html"]=shell("序例与卷首诗 · "+TITLE,"序例原样历史存档；当前正文范围以独立阅读政策为准。",preface)
    authority_sentence=(f'当前累计采用{len(m["author_emendations"])}项字词或图式顺序修订，其中138项经作者逐项确认，另40项依用户委托按可读性选择。' if "readable_adoption" in m else f'当前采用作者逐项确认的{len(m["author_emendations"])}项字词或图式顺序修订。')
    if "tail_lacuna_decisions" in m:authority_sentence="当前累计采用182项字词或图式顺序修订，其中142项经作者明确确认（含本轮四处补字），另40项依用户委托按可读性选择。第四、九回整块异本尾联依作者决定删除；第58回采用修树，第62回采用汗巴，均为本版选择，不宣称唯一古本原文。"
    if "title61_decision" in m:authority_sentence=authority_sentence.replace("182项", "183项").replace("142项", "143项")+"另依作者明确同意，将第61回回目瞒脏校为瞒赃；本次只改标题一字。"
    if "six_source_decisions" in m:authority_sentence=authority_sentence.replace("183项", "189项").replace("143项", "149项")+"另依作者明确同意，参考公开转录作前五回六处可读性补校；不作古本影印认证。"
    if "seven_source_decisions" in m:authority_sentence="当前累计采用196项语义修订（197处操作记录），其中156项经作者明确确认，另40项依用户委托按可读性选择；本轮新增七项八处，第10回同一读法出现两次。仅据公开中文转录作本版可读性选择，不作古本影印认证。"
    if "chapter24_source_decision" in m:authority_sentence="当前累计采用197项语义修订（198处操作记录），其中157项经作者明确确认，另40项依用户委托按可读性选择；本轮仅校正第24回焙茗一句。仅据公开中文转录作本版可读性选择，不作古本影印认证。"
    if "chapter28_source_decisions" in m:authority_sentence="当前累计采用199项语义修订（200处操作记录），其中159项经作者明确确认，另40项依用户委托按可读性选择；本轮第28回《红豆曲》补一独立行，并校正玉玦扇坠。仅据公开中文转录作本版可读性选择，不作古本影印认证。补句不来自原始TXT或PDF。"
    if "chapter38_40_source_decisions" in m:authority_sentence="本版累计201项语义修订（202处操作记录）。第38回几霜痕改几痕霜，第40回倚树改桃杏树，参考固定公开转录作可读性选择，未核古本影印。此前各项选择保留。"
    if "chapter38_42_45_source_decisions" in m:authority_sentence="本版保留累计204项历史语义修订（205处操作记录），另记1项作者覆盖选择：第38回恢复“几霜痕”，取其意境。旧“几痕霜”是偏重对仗与霜韵的编辑选读，不证明“几霜痕”为讹文。现行有效修订为203项（204处操作记录），历史SOURCE38-01不再控制正文。第40回桃杏树保持；第42回雅谑及粗细绢箩、第45回爇字依据固定公开转录及字典作可读性修订，未核古本影印，不主张唯一原稿。"
    if "chapter46_55_source_decisions" in m:authority_sentence+=" 第46至55回另按既经独立复核的15项具体语境选择作窄幅补校，涉及12单元；简繁同步，原始TXT及既有选择原记录不变。累计保留219项历史选择（220处操作），其中1项已被作者覆盖，现行有效218项（219处操作）。这些是本版可读性选择，不证明唯一原稿或错误形成机制。"
    if "chapter2_author_ending" in m:authority_sentence+=" 在上述来源层之后，第二回回末依作者明确选择改为完整收束句，原TXT及旧文保留。累计220项历史选择（221处操作），现行有效219项（220处操作）。本句是本版作者选择，不宣称古本复原。"
    if "chapter56_65_source_decisions" in m:authority_sentence+=" 第56至65回另依已独审的14项提案作16处窄修，涉及13个待译单元。累计保留234项历史选择（237处操作），现行有效233项（236处操作）；原TXT、既有异文选择和英文验收状态不变。"
    edition=f'<header class="chapter-head"><p class="eyebrow">编辑范围</p><h1>{TITLE}</h1></header><section class="editorial"><h2>阅读正文</h2><p>前八十回据作者所供脂批汇校文本整理，已依明确决定排除批注与其他回前题诗；第一回开卷自述后的八句诗为唯一例外，按作者决定保留。第十九回回末联去版本标签与重复引语后保留原联文。故事叙事中的诗词照常保留。原始资料、逐项补校与移出记录保存在本地工程档案，不作为阅读页附录展示。</p><p>{authority_sentence}此项目名不构成庚辰单一抄本认证，尚未完成古抄影印逐字校勘。</p><h2>作者边界</h2><p>前八十回与秦汉原创的第八十一至第一百一十回分别编排；后者是当代续写，并非曹雪芹佚稿。本稿为中文审读稿，仍有待校文字，尚未发布。</p></section>'
    pages[TARGET/"edition.html"]=shell("编辑范围 · "+TITLE,"正文呈现范围与古典原著、当代续写的作者边界。",edition)
    manifest=dict(title=TITLE,source_sha256=EXPECTED,chapter_count=80,publication_ready=False,review_status="中文去批审读稿，待作者校正决策",edits=len(m["edits"]),retained_brackets=len(m["retained"]),issues=len(m["issues"]),review_files=m["review_files"],batches=public_review_batches(m),coordinate_system="Unicode code points, zero-based start, exclusive end",translation_status="标准准备，尚未批量翻译",author_choices_applied=[x["id"] for x in m["author_emendations"]],author_retention_decisions=[{"chapter":6,"text":"青板姊妹","decision":"作者确认保留，不改为青板兄妹","status":"confirmed"}])
    if m.get("author_choice_overrides"):
        manifest["historical_author_choices_applied"]=manifest["author_choices_applied"]
        superseded={q["supersedes"] for q in m["author_choice_overrides"]}
        manifest["author_choices_applied"]=[ident for ident in manifest["author_choices_applied"] if ident not in superseded]
        manifest["author_choice_overrides"]=public_provenance(m["author_choice_overrides"])
    manifest["approval_batches"]=public_provenance(m["approval_batches"]);manifest["layout_sources"]=m["layout_provenance"]["sources"]
    if "readable_adoption" in m:
        manifest["readable_adoption"]=public_provenance(m["readable_adoption"])
        manifest["emendation_authority_counts"]=m["emendation_authority_counts"]
    manifest["supplemental_reviews"]=m["supplemental_reviews"]
    manifest["reading_policy"]=public_provenance(m.get("reading_policy",{}))
    manifest["editorial_note_policy"]=public_provenance(m.get("editorial_note_policy",{}))
    if "tail_lacuna_decisions" in m:manifest["tail_lacuna_decisions"]=public_provenance(m["tail_lacuna_decisions"])
    if "title61_decision" in m:manifest["title61_decision"]=public_provenance(m["title61_decision"])
    if "six_source_decisions" in m:manifest["six_source_decisions"]=public_provenance(m["six_source_decisions"])
    if "seven_source_decisions" in m:manifest["seven_source_decisions"]=public_provenance(m["seven_source_decisions"])
    if "chapter24_source_decision" in m:manifest["chapter24_source_decision"]=public_provenance(m["chapter24_source_decision"])
    if "chapter28_source_decisions" in m:manifest["chapter28_source_decisions"]=public_provenance(m["chapter28_source_decisions"])
    if "chapter38_40_source_decisions" in m:manifest["chapter38_40_source_decisions"]=public_provenance(m["chapter38_40_source_decisions"])
    if "chapter38_42_45_source_decisions" in m:manifest["chapter38_42_45_source_decisions"]=public_provenance(m["chapter38_42_45_source_decisions"])
    if "chapter46_55_source_decisions" in m:manifest["chapter46_55_source_decisions"]=public_provenance(m["chapter46_55_source_decisions"])
    if "chapter2_author_ending" in m:manifest["chapter2_author_ending"]=public_provenance(m["chapter2_author_ending"])
    if "chapter56_65_source_decisions" in m:manifest["chapter56_65_source_decisions"]=public_provenance(m["chapter56_65_source_decisions"])
    if "version_selections" in m:manifest["version_selections"]=public_provenance(m["version_selections"])
    if "opening_restoration" in m:manifest["opening_restoration"]=public_provenance(m["opening_restoration"])
    if "paragraph_boundary_corrections" in m:manifest["paragraph_boundary_corrections"]=public_provenance(m["paragraph_boundary_corrections"])
    manifest["reading_exclusion_summary"]=m.get("reading_exclusion_summary",{})
    manifest["excluded_layout_ids"]=m.get("excluded_layout_ids",[])
    manifest["author_controlled_layouts"]=[r for c in cs for r in c["author_layout_ranges"]]
    pages[DATA/"generated/audit/edition-manifest.json"]=json.dumps(manifest,ensure_ascii=False,indent=2)+"\n"
    pages[DATA/"generated/audit/raw-issue-coverage.json"]=json.dumps(dict(coverage=m["raw_issue_coverage"],context=m["review_context"],layout_deferred=m["layout_deferred"]),ensure_ascii=False,indent=2)+"\n"
    pages[DATA/"generated/audit/supplemental-issue-coverage.json"]=json.dumps(m["supplemental_issue_coverage"],ensure_ascii=False,indent=2)+"\n"
    pages[DATA/"author-review-all-issues.json"]=json.dumps(m["issues"],ensure_ascii=False,indent=2)+"\n"
    pages[DATA/"generated/model.json"]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
    pages[DATA/"generated/edits.json"]=json.dumps(m["edits"],ensure_ascii=False,indent=2)+"\n"
    pages[DATA/"generated/first80.zh.txt"]="\n\n".join(c["title"]+"\n\n"+"\n\n".join(b["text"] for b in c["blocks"]) for c in cs)+"\n"
    # Private review HTML has its own location; public files are read-only assets.
    prefix=Path(os.path.relpath(ROOT,TARGET)).as_posix()+"/"
    for path in list(pages):
        if path.parent==TARGET and path.suffix==".html":pages[path]=pages[path].replace('href="../../','href="'+prefix)
    for name in ("reader.css","reader.js"):
        value=(ROOT/"classics/hongloumeng"/name).read_text()
        if name.endswith(".css"):value=value.replace("fonts/",prefix+"classics/hongloumeng/fonts/")
        pages[TARGET/name]=value
    return pages

def validate_private_outputs(paths):
    """Preflight every destination; this builder cannot write public website paths."""
    private=DATA.absolute()
    if private.resolve()!=private:raise ValueError("Private data root must not be aliased")
    for path in paths:
        path=Path(path).absolute()
        if ".." in path.parts or private not in path.parents:raise ValueError("Private build output outside private data root")
        for parent in (path,*path.parents):
            if parent.is_symlink():raise ValueError("Private output must not be a symlink")
            if parent.exists():
                info=parent.lstat()
                if parent==path:
                    if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1:raise ValueError("Private output must be a single-link regular file")
                elif not stat.S_ISDIR(info.st_mode):raise ValueError("Private output parent must be a directory")
        if private not in path.resolve().parents:raise ValueError("Private output escapes private data root")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");args=ap.parse_args()
    pages=render(model());stale=[]
    validate_private_outputs(pages)
    if (TARGET/"preface.html").exists() or any((TARGET/"audit").glob("*")):
        stale.append("Superseded public prefatory/audit files remain")
    for path,text in pages.items():
        if args.check:
            if not path.exists() or path.read_text()!=text:stale.append(str(path.relative_to(ROOT)))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    if stale:raise SystemExit("Stale generated files: "+", ".join(stale))
    print(f"PASS: {len(pages)} generated files; immutable source and reversible edits verified.")
if __name__=="__main__":main()
