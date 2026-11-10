# Japanese WWII translation: preliminary independent review

Status: preliminary, not a release certificate. This reviewer did not author the Japanese drafts and read every one of the 253 Japanese HTML units against the full Chinese source units, including the six explicit pending placeholders. This is a translation and prose review, not independent historical source verification. No Japanese translation or source file was edited. The active seven-item source-approval boundary remains in force.

## Exact reviewed snapshots

- 1-weimar.json: translation file SHA-256 `bdee7453eb62544c23c29a7f8f6c2f13b7b3e6649529341a09964cdb38a0a5a2`; source file SHA-256 `08fea660371aea84c7ce434558af78e985f439f8e48873f66dacc16430237f73`; declared source_sha256 `d581b71cf13148d04c6d7cb55acf3491831ed86a9a1fdbd134c3694e9ec738e7`; units 47/47; ordered tags match: True; declared source hash matches: True.
- 2-institutions.json: translation file SHA-256 `f50ab52cbe2bc92224c84d1f6a3e8a5bd42395adf479dbac99377132daa50c0f`; source file SHA-256 `e2e59645fb62b923c0c29c4720287d9ba5bed9cccd60b722dc3140eb264b93c6`; declared source_sha256 `af0f66f9f6462567135edf69a0d0038e45a40765c2d31b0076bef7e292b79973`; units 51/51; ordered tags match: True; declared source hash matches: True.
- 3-four-systems.json: translation file SHA-256 `aef5d4ecd0cc0fffc6cb11d93964f41a7eb255b96ac7748525a12f9806cef16e`; source file SHA-256 `ae7221e42aee80650387f37ac54cbd366354fd278fc64bbfaa3aa4ca90e93368`; declared source_sha256 `4f76a1cdbca540e0facb6bd210954bb373d39d6a38a968203dc1e3b1206aa117`; units 45/45; ordered tags match: True; declared source hash matches: True.
- 4-promise.json: translation file SHA-256 `e08247c80504da763ee34cb9d40fa811cfdee277a56558731a1527e3624c06fe`; source file SHA-256 `a92c6d6318480be6d3452fa3cef7f1141a627b2061d38737270acb2a2b57d957`; declared source_sha256 `3504fb5485ed951810cbd2d9f371163d3ac79bb6c08b6076ce0248653397be8c`; units 56/56; ordered tags match: True; declared source hash matches: True.
- 5-cracks.json: translation file SHA-256 `b7bda2112d0b0ca746209a0ae66d814b4d42d7a0244d14d961689c1deb124cb3`; source file SHA-256 `0f459b49f09a6998909eb2d25071b70d925ff1d7ffdafcff1599c768b6c4975d`; declared source_sha256 `d8baad185378fae7718083de3e15d2f56f120d4316eae3cd59a24907d967e226`; units 54/54; ordered tags match: True; declared source hash matches: True.

## Coverage and overall result

- Essay 1: 47/47 units; essay 2: 51/51; essay 3: 45/45; essay 4: 56 structural units with one withheld translation; essay 5: 54 structural units with five withheld translations. In total, 247 translated units and six explicit placeholders.
- All heading/paragraph sequences match their Chinese snapshots. No argument section, example, or concluding movement has been replaced by a summary in the translated units.
- Titles retain the source meanings. Decks are concise editorial introductions rather than replacements for the full text.
- The Compiegne wagon correction, Versailles reparations timing and Article 231 distinction, Enabling Act violence/coercion, Czechoslovak dissolution, railway billing, Ota telegram date, Dresden casualty range, Nuremberg attendance/personal responsibility, UDHR legal development/drafting committee, Welch censure account, and Berlin opening prehistory are represented in the applicable translated units. Fukuyama material remains withheld rather than certified.
- Nazi racist statements are clearly attributed to propaganda or the racist regime. The Japanese discussion repeatedly specifies the wartime system and national-polity ideology, rather than attributing characteristics to present-day Japanese people. This is appropriate and should be retained.
- Names and standard terms read consistently: コンピエーニュ, テューリンゲン, ヴァイマル, ズデーテン, 大田実, フレッド・コレマツ, エレノア・ルーズベルト, ジョセフ・ウェルチ, シャボフスキー. The source does not use the literal English label Self-as-an-End in these bodies; do not translate that label if added elsewhere.

## Corrections for the Japanese author

All unit numbers below are 1-based positions in the body array, counting h2 as units.

### Material semantic correction

1. Essay 3, unit 22 (body[21]): source says “不是因为他们会被枪毙（虽然拒绝确实会有严重后果）”. Draft says “銃殺されるからというだけではない。拒否に深刻な不利益があったにせよ”. The added “だけ” changes a denied causal explanation into an admitted partial cause, potentially asserting a firing-squad threat not asserted by the source. Suggested replacement for this portion: “銃殺されるからではない（ただし、拒否には深刻な不利益が伴った）。彼らが教え込まれた世界観では、天皇のために死ぬことは犠牲ではなく、完成だったからだ。” Preserve the remaining paragraph.

### Clarity / natural Japanese

2. Essay 4, unit 29 (body[28]): “連盟は、大国が集団の意思に従うふりをし” has an unclear subject for the pretense and can make it sound as though the great powers merely pretended to obey. The source says the League pretended the great powers would obey. Use “連盟は、大国が集団の意思に従うかのように装い、大国が従わないと見なかったふりをした。”
3. Essay 4, unit 27 (body[26]): “一人ひとりのもとへはるかに届いていない” is unnatural. Use “しかし、すべての人のもとに届くには、まだほど遠い。” This also makes the source’s universal scope explicit.
4. Essay 2, unit 11 (body[10]): replace the stiff/Chinese-influenced “この方案” with “この方策” or “この構想”.
5. Essay 2, unit 19 (body[18]): “制裁を採決した” states a vote occurred but does not clearly retain the source’s passage of sanctions. Use “制裁を採決で可決した” or “投票で制裁を承認した”.
6. Essay 4, unit 20 (body[19]): replace “各者” with the idiomatic “各国の代表” or “関係者”.
7. Essay 4, unit 43 (body[42]): source says most colonies (“大多数”), draft says “多く”. For closer quantifier fidelity, use “大半の植民地”. This is a translation precision suggestion, not fresh historical verification.
8. Essay 3, unit 42 (body[41]): “しかも” makes the final item sound simply additive, while the source continues its qualified-concession structure. Consider “『誰を人に数えるか』は名目上は普遍的にすぎないが、その普遍性を根拠として異議を申し立てることはできる”. This also keeps the next unit’s reference to qualifications coherent.

### Small fidelity observations, not release-blocking on their own

- Essay 3, unit 2 neutralizes the Chinese description of survivors “standing” on bunks to “寝台の上にいる”. That is a posture detail omitted, not an omitted scene. Do not call this a checked historical correction; if strict word-for-word fidelity is required, have the source editor resolve the photo-description wording first.
- Essay 1, unit 19 renders “the most lively city in all Europe” as “ヨーロッパでもひときわ活気のある都市”. The superlative is softened, but the recovery/cultural-life argument and all three examples survive.
- Some generalizations and deterministic transitions in Chinese remain strong in Japanese. They are source-level claims, not proof of translation failure. This review does not authorize silently rewriting them.

## Seven known source questions: separate from translation errors

1. Hans clockmaker fictional/illustrative status: essay 1 unit 31 remains source-based and unresolved.
2. Rhineland deterministic counterfactual: essay 2 unit 4 remains source-based and unresolved.
3. Rapid denazification/comparative postwar transition: essay 3 unit 25 remains source-based and unresolved.
4. Bengal famine single-cause framing: essay 3 unit 29 remains source-based and unresolved. Connected references in unit 30/32 and essay 4 unit 14 should be checked for consistency after approved amendments; this is not approval to rewrite them now.
5. Goering/Dresden courtroom attribution: essay 4 unit 15 is an explicit placeholder, not translated testimony.
6. GDR emigrant total and statistical scope: essay 5 unit 4 is an explicit placeholder.
7. Fukuyama characterization and connected conclusions: essay 5 units 33, 34, 38, 40 are explicit placeholders.

## Next step

Await authorized source amendments. The Japanese author should implement the independent translation/prose corrections, replace only the authorized pending/affected units, update source hashes to the actual amended baseline, and submit fresh file hashes for a final full read. No final completeness or historical-accuracy certificate can be issued on the current drafts.
