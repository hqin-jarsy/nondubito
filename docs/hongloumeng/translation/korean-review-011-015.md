# 韩语第11—15回翻译与自审记录

日期：2026-11-14。状态：五回译文已写入，完成译者逐段对照及批次自审；尚待主任务整合与独立复核，不代表全站发布或原生韩语编辑终审。

## 底本与范围

唯一中文底本为当前 classics/hongloumeng/ch011.html 至 ch015.html 的 article 正文。没有用其他语言译文替换中文底本，也没有改动中文。韩语连续性参照当前 originals/hongloumeng/ko/ch081.html 至 ch085.html，尤其当前 HTML 的 희봉、보차，不采用 received 旧稿中的 보채。实际本批正文未出现宝钗称名。

回目已逐一核对当前中文 HTML 的 h1，并同步核对译页 title/h1：
- 11：庆寿辰宁府排家宴／见熙凤贾瑞起淫心。
- 12：王熙凤毒设相思局／贾天祥正照风月鉴。
- 13：秦可卿死封龙禁尉／王熙凤协理宁国府。
- 14：林如海捐馆扬州城／贾宝玉路谒北静王。
- 15：王凤姐弄权铁槛寺／秦鲸卿得趣馒头庵。

正文段数：第11回32，第12回27，第13回34，第14回33，第15回27，共153段。每段均保留源 class、连续 data-source-block 与 data-kind。诗联包括第13回第6—7段、33—34段；正文引用诗句、对白、文书及官职名单一并翻译。没有以概要补齐篇幅，没有占位。

## 对读与修正

逐段翻译时核对叙事顺序、说话人、人物关系、否定、数字、礼俗及诗句；完成后按整批复查回目、主要名称和容易误读的细节。主任务另对第11回进行了独立全文对读，其反馈已采纳：
- 第11回第4段“你大妹妹”改作明确指称 희봉，避免译成尤氏亲妹。
- 第11回“媳妇婆子”的不自然组合改为 기혼 하녀／늙은 하녀，旺儿媳妇记作 왕아네。
- 第11回三百银子的利银保留为三百两本金的利息，不误成三百两利息；人参二钱／二斤、冬至十一月三十日等照底本。
- 第12回保留两张各五十两欠契、二十来岁、求参二两而实送几钱的区别；风月镜正反面、三日约定、失效与死亡过程均在。
- 第13回回目初稿误写了“封龙禁”含义，已按当前“死封龙禁尉”改正为因秦可卿之死而有龙禁尉封授；正文明确购买的是贾蓉的官职，不说秦氏本人任侍卫。108僧／99道／50僧50道、1500两／1200两、49日等分别保留。
- 第14回人员分组、20板递增至40／60、扣一月银米、对牌交还与回押核验均保留。旧式时刻用韩语汉字音，不自作现代时间换算。林如海九月初三日的日期即使与前文时序令人疑惑也按底本保留，未擅改。铭旌“享强寿”译为 한창 나이에 세상을 떠난，避免机械“强健寿命”措辞。
- 第15回保留先定婚约、李公子强求、守备家辱骂并诉讼、张家求退婚的因果；凤姐3000两索款与声称自己不要钱的反差、假托贾琏写信、100里／两日及三日后讨信均在。不给凤姐增添悔意或道德辩护。

本批称名采用韩语汉字音：가경（贾敬）、가진（贾珍）、가용、가련、가장、가서／가천상、진씨／진가경、진종／진경경、임여해、수용、정허、지능、지선、내승、내왕／내왕아、왕아等。不同汉字同音者在原文名单中保留次序，不通过虚构称谓区分。跨批次统一称名仍需主任务复核。

## 含蓄处理的确切位置

- 第12回 data-source-block=12：不逐字展开性器官、脱衣与侵入动作。保留贾瑞误认对方、未得回应而强行亲近、企图进一步侵犯、灯亮发现贾蓉、羞惭与贾蔷勒索的全部事件关系。没有将其写成双方自愿。
- 第15回 data-source-block=23：开头老尼奉承完整保留；秦钟与智能段落保留拒绝、要离开寺院才答应的条件、秦钟以死相逼、灭灯、她反抗而不能脱身及难以求救。具体亲吻、床上动作改为非露骨叙述，明确写“진종은 그녀의 거절을 무시하고 제 욕심을 강요했다”。不以“终于同意”掩盖强迫。
- 第15回24—25段保留宝玉闯入、以声张相胁、智能离开、晚间住宿及叙述者不敢编造“算账”疑案的留白，不扩大露骨内容。
- 第12回成人贾瑞的病症、梦镜情欲与死亡叙事没有因普通成人内容而另设占位；第11回非露骨觊觎、第13回丧礼和自尽事实、第15回普通恋慕均正常翻译。

因此无占位不等于逐字无淡化。两处具体改写如上；其余未另作内容删节。

## 结构检查与剩余局限

读取生成的 UTF-8 HTML 后确认：
- 153/153 段数、顺序、源 class 一致，每段非空并有韩文。
- 每页 lang=ko、一个闭合 article、无重复 id、无 U+FFFD 替换字符。
- 回目 title/h1 已按当前底本核对。
- 全部正文的首尾齐全。初次长 Unicode heredoc 写入报编码错误，没有生成目标文件；随后用 ASCII 转义运输后还原 UTF-8，成功写入并读取验证。
- reader.css 和 reader.js 已存在；本批本地链接仅 index.html 尚缺，交由主任务生成目录。上下回暂明确链接中文页，避免链接尚未完成的韩语回次。未修改全站发现入口、搜索或进度文件。
- 未运行浏览器视觉测试；未把结构检查当成文学准确性的证明。
- 未 git add、commit 或 push。本记录与五篇 HTML 留给主任务按五回审查后本地提交。

源 HTML SHA-256：
11 49d2e8cc7a8ef906fb94552525141fcf6b5fc6a75617766c9601fe1aa07f1715
12 68da7718a755b2dc773e92f794b7dc82f49e6c71c5d86970e30a1be5a223f004
13 5c448876fbb3770896932a0fe4bdf8f9cd7f788f52c12449475f5ba9b2e6218c
14 c2ea1fb8f3006bfd0ca20fc7c6f658fa919e51f899b09e2e3a49b0fa28225b62
15 1f27fd90b8c0552a9e367a732aec3251ac48ff0b5ce056a7f55fa23562304ebe

协调复核补记：第11回“上月中秋”统一为 지난달 중추절，与第1回节名一致，避免无必要改称韩国节日名。其余正文未因此改动。

## Integration verification

Reader and reversible navigation integrated through chapter 15; scoped Korean search updated and verified current. Chinese and Korean continuation article bindings unchanged; all 736 source blocks through chapter 15 passed structure/link checks. Discovery tests: 43 passed; git diff --check passed. Additional non-graphic adaptation is marked for chapters 12 and 15. No separate browser or native-speaker final review is claimed.

Follow-up content-scale audit: chapter15 P23 restores the source kiss and movement to the bed, and states coerced intercourse non-graphically rather than merely imposing desire. Resistance and refusal remain explicit; no erotic detail was added.
