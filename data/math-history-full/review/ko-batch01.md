# Korean review: batch 01 (ep01–ep05)

## Scope and method
Read CLAUDE.md and SAE-TERMINOLOGY.md. Compared the complete current body_zh of source/ep01.json through source/ep05.json with ko/ep01.md through ko/ep05.md, in section-sized reads: all 40 body sections, five titles/decks/front matter blocks, all five source sections and their source-list URLs, and previous/next links. The ep01 section 7 output was partially truncated in one call; its Korean ending was reread separately. No sampling or paragraph-count substitute was used. The English text was not used to override the Chinese.

## Findings and repairs
- ep01: The distinctions between accounting evidence, literary school scenes and archaeological inference are preserved throughout. Numerical details (85 percent, 1425 tablets, 24 problems, 26/27 regnal years) and all Egypt/Uruk examples are present. Updated the next-essay link label to ep02’s actual title.
- ep02: The separate ancient testimony, later Hippasus legends and modern crisis reconstruction are preserved. Read the full parity proof and Eudoxan equimultiple explanation; no dropped logical step found. Standardized Høyrup’s Korean spelling to 호이루프, matching ep01.
- ep03: The five postulates, I.1 circle-intersection issue, Pasch/Hilbert discussion, diagrams and manuscript transmission are all present. Standardized the series strapline to 주기 법칙 and the adjacent essay titles. The Chinese-source issue below remains deliberately unresolved.
- ep04: Read all three legend histories, both reductio cases, X.1, 10/71 and 1/7 bounds, 4/3 and 2/3 results, discovery/proof distinction, infinity qualifications and the full palimpsest chain. Preserved the cautious distinction between material manuscript age and age of its text. Corrected ep05 link title to 판단 기준.
- ep05: Read all eight sections, including manuscript provenance, all nine chapter counts, Liu Hui’s argument and admitted gap, 157/50, 3.1415926–3.1415927, 355/113 and 22/7, Tang quotas versus admissions, and all five methodological objections. Added 術 on first deck use and explained 疏 at its first body use; standardized strapline and previous title. The existing Korean rendering of c.186 BCE is consistent with the opening dating caveat; it was not changed into a precise pre-186 claim.
- Added ko/ui.json with all requested keys and five group labels, translated in full.

## Source-level issue awaiting author decision
Chinese ep03 §4 now says 古代文本并没有宣布排除图示推理资源的完整形式契约, but the next paragraph says 不许再添别的……这才是这本书真正的发明. Section 6 also says 而这本书从第一页起就在宣称，后面的一切都从前面那几条推出来. These unqualified declarations conflict with the revised caveat and the later discussion of permitted diagrammatic reasoning. Recommend making the modern-formalization condition explicit in these claims. The Korean faithfully reflects the present source; no unauthorized argument rewrite was made. The issue was submitted for editorial review. Relevant source already listed by the author: https://arxiv.org/abs/1710.00787 (Proof-checking Euclid); fresh external verification was not performed in this translation pass.

## Limits and status
This report certifies complete translation comparison, not independent re-verification of every historical assertion against external scholarship. ep06–ep25 are not covered by this report. No Chinese, English, received manuscripts, shared files or rendered pages were edited. No commit or push was run.

## 补核：中文底本内部限定残留

- ep04§3：前后已表示精度存疑，中间仍写‘争议在于维特鲁威描述的那套操作，达不到王室金工鉴定所需要的精度。’韩文忠实保留断言。建议作者改为‘可能难以达到……，具体精度仍有争议’，待批准，不擅改。
- ep05§1：‘但至少可以看出，前186年以前，已经有一本实物算书’；§3：‘张家山那本书证明这种体裁在前186年以前就有了’仍与开篇约186年的限定冲突。建议作者把两处‘前186年以前’改为‘约前186年’。现成韩译两处均已写 기원전 186년 무렵，本审保留，非此次新改。
