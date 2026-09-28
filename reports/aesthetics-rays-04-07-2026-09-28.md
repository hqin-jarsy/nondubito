# 美学射线散文第二批：04—07

日期：2026-09-28。范围：简体、繁体与独立英文；本地提交，未推送。

## 本批内容

| 射线 | 散文标题 | 中文汉字数 | 英文词数 |
| --- | --- | ---: | ---: |
| 04 物理 | 再漂亮的想法，也要等世界回答 | 1,769 | 1,109 |
| 05 因果 | 木头里留着那一年的旱 | 1,839 | 1,154 |
| 06 生物 | 它一直在换，却没有散掉 | 1,842 | 1,114 |
| 07 繁殖 | 下一代，不是一个缩小的它 | 1,943 | 1,158 |

计数含小标题，中文只计汉字，英文按空白分词。以文章完成为准，不为达到整数下限填字；自动完整性检查的中文最低值由 1,800 调整为 1,700，另外逐段核对渲染结果，英文下限仍为 1,100。篇幅阈值不是质量判断。

四篇分别从独立测量、年轮与磨损、细胞维持与分裂、团藻发育翻转进入。并非论文章节摘要；保留原文哲学方向，同时明确观察、解释与比喻之间的界线。生命两篇不将可观察的变异说成已经证明了哲学意义的不可穷尽，不借细胞分工替人的角色、生育或牺牲立法。

## 来源与核验

本批读取对应 SAE 原论文全文/相关段落，并通过 HTTPS 核对线上四篇与本地理论仓库版本一致（均 HTTP 200）；未修改理论仓库。

- [物理之美](https://self-as-an-end.net/papers/sae-aesthetics-ray-4.html)：麦克斯韦使用的历史速度值与独立光速测量约为每秒 31 万公里，不冒充现代精确值。不把 1865 年摆脱某种机械图景写成已放弃以太。
  - [On Physical Lines of Force, Part III (1862)](https://doi.org/10.1080/14786446208643207)
  - [A Dynamical Theory of the Electromagnetic Field (1865)](https://doi.org/10.1098/rstl.1865.0008)
  - 查阅 1865 原文的数字及以太表述时，使用[原文转录](https://jovanaeducation.com/library/maxwell-1865)的论文部分，不采用其现代概述代替原文。
- [因果之美](https://self-as-an-end.net/papers/sae-aesthetics-ray-5.html)：窄轮与干旱关系限于相应生长条件；不能机械地逐圈计年。HH-39 在 1929 年于 Show Low 的发现连接年轮序列，木材年代与建筑年代仍须区分。
  - [NOAA 树轮与气候](https://www.ncei.noaa.gov/news/how-can-tree-rings-teach-us-about-climate)
  - [亚利桑那大学树轮研究史](https://www.ltrr.arizona.edu/~grissino/history.htm)
- [生物之美](https://self-as-an-end.net/papers/sae-aesthetics-ray-6.html)：采用 Schizosaccharomyces pombe 的末端生长与中部分裂，不加入有争议的细胞衰老推断；不声称所有生物材料按同一周期整体替换。
  - [Hoffman、Wood、Fantes，Genetics (2015)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4596657/)
- [繁殖之美](https://self-as-an-end.net/papers/sae-aesthetics-ray-7.html)：范围限于 Volvox carteri 无性周期，体细胞与生殖细胞分化、胚胎翻转、后代释放；不是所有团藻或所有繁殖方式的定义。不把翻转前胚胎写成已经长有完整向内鞭毛的成体。
  - [Matt 与 Umen，Developmental Biology (2016)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5101179/)
  - [Haas 与 Goldstein，Embryonic Inversion in Volvox carteri (2018)](https://arxiv.org/abs/1808.00828)

PMC 部分页面直接打开受验证码/限流影响，使用可检索的论文文本与作者预印本核对，不将访问受限页面描述为完整直接抓取成功。可追溯外链放在每篇末尾的写作说明中；通俗场景不伪装成作者亲历或特定录像的观察记录。

## 接入与保护范围

- 新增 12 个独立页面；美学三语入口现为 7 / 13，余下六篇不生成空卡片或下一篇死链。
- 03 接 04，04—07 连续互链，07 返回射线目录。保留无 JavaScript 阅读路径与带章节锚点的语言切换。
- 更新首页、Library、latest、发布记录、搜索与 sitemap。首批更新记录改成历史描述，避免仍声称“其余十篇尚未发布”。
- 英文、简体、繁体搜索各新增四条，仅本系列三个索引页的已有记录有变化，无删除和跨系列变更。
- 搜索总记录：10,169；sitemap 规范 URL：10,017。
- 对 HEAD 逐字节比较 160 个原有文件：150 篇日常文章、log、artist_dead、两份导读稿与六份首批稿全部不变。另比较三语导读及 01—03 的 12 个已发布正文，全部不变；03 仅更新后篇导航。
- 繁体全文终校，纠正公里、帳、算不準、證明了、奇蹟、影印本、重複等转换语境问题。

## 验证

- `scripts/test_aesthetics_hub.py`：7 项通过，覆盖 27 页、完整正文、规范链接、hreflang、JSON-LD、来源、章节互链、目录状态、存档、搜索与 sitemap。
- `scripts/test_aesthetics_hub_browser.cjs`：108 组页面/语言/视口检查通过（1440、768、390、320 px），无横向溢出，无页面脚本错误；语言下拉、目录、论文折叠区、旧页面回退、03—07 连续阅读及无 JS 阅读通过。
- 人工查看桌面入口全页、英文 04 手机页、繁体 07 手机页截图；未见重叠、截断或切换栏错位。临时截图位于 `/tmp/aesthetics-rays-04-07-qa/`，不提交仓库。
- 构建新鲜度、更新记录一致性及 `git diff --check` 均在提交前核验。

下一批：08—10（感知、认知、自我）。
