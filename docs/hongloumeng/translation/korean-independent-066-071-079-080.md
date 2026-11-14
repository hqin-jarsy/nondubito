# Independent Chinese–Korean literary review: chapters 66, 71, 79, 80

## Scope and method

Read every current Chinese source block against its Korean counterpart using scripts/check_hongloumeng_korean.py read(): chapter 66 blocks 1–27; chapter 71 blocks 1–46; chapter 79 blocks 1–29; chapter 80 blocks 1–33. Total: 135 paired blocks. This was full literary reading, including dialogue, speaker/kinship, plot detail, poems, euphemisms and coercion, not a structural spot-check. Read korean-standard.md and inspected current Korean continuation 81–85 naming/register samples directly (their div/p markup is outside this checker’s block selector).

No chapter HTML, source files, or shared tracking files were edited. No commit or push. This report records recommended changes, not applied corrections. No substantive omission, invented plot event, or gratuitous softening found in these four chapters. No required correction found in chapter 66 or 79; this is a limited review finding, not a claim of absolute perfection.

## Recommended corrections

### 1. Chapter 71, source block 6: female speaker and sister-in-law

- Original: 再只叫你三妹妹陪着来罢。
- Current Korean: 네 셋째 누이만 함께 오게 하렴.
- Replacement Korean: 네 셋째 시누이만 함께 오게 하렴.
- Reason: Jia Mu addresses Wang Xifeng about Tanchun, her husband’s younger female cousin, treated as a sister-in-law within this household. 누이 gives a male speaker/addressee relationship and conceals the marital kinship. 셋째 아가씨만 함께 오게 하렴 is also a safe natural rendering if the edition avoids expanded cousin-kinship terms.

### 2. Chapter 80, source block 19: historical illness name

- Original: 竟酿成干血之症
- Current Korean: 마침내 간혈증이 되었다.
- Replacement Korean: 마침내 건혈증이 되었다.
- Reason: 干 here simplifies 乾 (dry), read 건, not 간. Retain the historical illness category rather than introducing a modern diagnosis. Korean scholarly usage: [대한한의학원전학회지 25(1), 온병 혈증의 락맥병기에 대한 고찰: 주객교와 건혈 중심](https://kiss.kstudy.com/Detail/Jr?Ins=7057&Jur=29569&Num=1&Vol=25).

### 3. Chapter 80, source block 24: 面筋 is food, not a tendon

- Original: 哥儿别睡，仔细肚里面筋作怪。
- Current Korean: 도련님, 주무시면 배 속의 힘줄이 장난을 칠지도 몰라요.
- Replacement Korean: 도련님, 주무시지 마세요. 배 속의 면근(麵筋)이 심술을 부릴라요.
- Reason: Segment 肚里 / 面筋, not 肚里面 / 筋. 面筋 is the wheat-gluten food in the meal/sleep joke. The present rendering invents abdominal tendons as the subject. Preserve the joking personification; do not replace it with a medical diagnosis. A short glossary explanation of 면근 may be useful if the edition supports glosses. [Historical-text transcription with explicit 麺筋](https://www.shidianguji.com/book/SWX0005/chapter/1kzxy8glf2yw4); [food-history discussion of this exact joke](https://gs.ifeng.com/c/8DvBDdP6T31).

## Optional clarity adjustment

### Chapter 80, source block 30: accompanying servant women

- Original: 孙家的婆娘媳妇等人已待过晚饭，打发回家去了。
- Current Korean: 손씨 집안의 부인과 하녀들에게도 저녁밥을 먹여 돌려보낸 뒤였다.
- Replacement Korean: 손씨 집안에서 따라온 하녀들에게도 저녁밥을 먹여 돌려보낸 뒤였다.
- Reason: 婆娘媳妇 here denotes the attending household women/servants sent with Yingchun. 부인과 하녀 can misleadingly introduce a wife or mistress of the Sun family as an accompanying character. No need to create that distinction.

## Content and source-boundary notes

Chapter 66’s rejection of the marriage, You Sanjie’s suicide and visionary farewell remain intact. Chapter 71’s servant conflict, Xifeng’s public humiliation, and Siqi’s clandestine meeting retain their speakers and causal sequence. Chapter 79’s revised elegiac couplets and four-block Zilingzhou poem retain the source imagery and sequence. Chapter 80 retains Jin Gui’s manipulation, Baochan’s accusation of coercion, Xue Pan’s violence, Xiangling’s illness, and Yingchun’s report of marital abuse. Ordinary adult euphemisms were not flagged merely for being euphemistic. Apparent inconsistencies in the supplied Chinese were not silently replaced with another edition. Web checks above were lexical corroboration only, not a replacement translation source.

## Coordinator implementation

All three recommended corrections and the80/b30 clarity adjustment applied. The food at80/b24 is retained as 면근 with a brief in-line Korean flour-food gloss. Full135-block independent review now supplements translator selfreview.
