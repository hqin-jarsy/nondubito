# 非虚构二十篇：本地发布接入检查

日期：2026-10-10。基线提交：`3a7f559a65cfa470e16fe858b47fbd9c8f47f50b`。

范围为用户批准发布的10月8日、10月10日四批共二十篇复核稿。已接入本地网站；没有 commit、push 或确认远端部署，不以本报告声称已公开上线。

## 接入内容

每篇增加一份 `data/nonfiction` 数据和一个 `essays/nonfiction` 页面，包含英文、简体、繁体阅读版本。非虚构由32部增至52部，与原有43部近年小说合计95部。更新书籍总入口、非虚构目录、Library、首页提示、Explore、Latest 与更新账本、内容注册表、搜索、站点地图及读者上下文审计。

| 稿件 | 页面 slug |
| --- | --- |
| 一汁一菜就好 | ichiju-issai |
| 孤独的城市 | the-lonely-city |
| 章鱼的心灵 | other-minds |
| How to Say Babylon | how-to-say-babylon |
| 西伯利亚失落的钢琴（暂译） | the-lost-pianos-of-siberia |
| 地址的故事 | the-address-book |
| The Art of Repair | the-art-of-repair |
| 东京八平米 | tokyo-eight-square-meters |
| 看不见的女性 | invisible-women |
| 时光列车 | m-train |
| 我在北京送快递 | i-deliver-parcels-in-beijing |
| 看不见的森林 | the-forest-unseen |
| 生活的代价 | the-cost-of-living |
| 日常生活中的自我呈现 | the-presentation-of-self-in-everyday-life |
| A Paradise Built in Hell | a-paradise-built-in-hell |
| 漫游在雨中池塘 | a-swim-in-a-pond-in-the-rain |
| Taste | taste |
| 她所承载的一切 | all-that-she-carried |
| 鳗鱼的旅行 | the-book-of-eels |
| 新机器的灵魂 | the-soul-of-a-new-machine |

## 正文与资料边界

中文正文逐篇与写作工作区复核版匹配：主标题放入标题字段，开头独立书目信息按网站元数据处理，其余正文不缩写。二十篇正文 SHA-256、章节数、出版年、原作语言和英文词数固化在 `scripts/fixtures/nonfiction-2026-10-10-approved.json`，以便后续回归检查。

英文合计25,728词，逐篇涵盖中文对应小节，不以摘要充当译文。繁体沿用现有转换器。原作语言补入瑞典语标签，不新增瑞典语阅读版本。

保留上一轮质量复核对材料归属、真实人物心理推断、历史日期和研究边界的修订。特别区分章鱼独立研究与书中论述、鳗鱼2022年追踪与2019年原作、戈夫曼1956年初版与1959年修订版、《新机器的灵魂》1981年出版与1982年获奖。公开资料、试读、访谈和书评没有伪装为通读原书；网页保留阅读依据提示，正文不插入外链，资料链接集中在既有资料区。

相对于基线，原有32份非虚构 JSON 完全相同，原有32篇共96个语言正文块逐字相同。旧文章 HTML 的变化仅为相关导航更新。

## 生成和检索检查

- `PYTHONPATH=scripts python3 -m unittest test_book_introductions test_recent_fiction`：35项通过。
- 非虚构生成器 `--check`：52部通过；近年小说生成器 `--check`：43部通过。
- 更新账本与 Latest 一致性、canonical 规范及 `git diff --check` 通过。
- 内容注册表：443条 canonical 记录、1,347个扫描页面、17个 Library 分类。
- 读者上下文审计当前：11,469个页面。此为生成结果一致性，不表示人工重读全部站点。
- 站点地图：11,063个 canonical URL。
- 搜索重建曾暴露 `data/anime-full/templates` 被误当发布入口的问题。本次在搜索生成器排除此源模板目录，并加入回归断言；没有改动模板或动画文章正文。
- 校正后搜索共11,215条来源记录。相对基线，英文、简体、繁体各只新增本批20个页面 URL，其他五种语言页面清单不变；所有语言均没有移除旧 URL。

## 浏览器与视觉检查

`scripts/test_book_introductions_browser.cjs`：845项检查通过，包含486个页面／语言／视口组合、语言刷新与锚点、栏目导航、300次书名或作者检索、手机菜单；未发现 JavaScript 异常或本地资源加载失败。

视口宽度为1440、390和320像素。截图保存在写作工作区 `work/nonfiction-oct10/screenshots/`。人工检查了桌面非虚构目录、320像素英文《漫游在雨中池塘》正文、390像素繁体《我在北京送快递》正文、桌面简体《新机器的灵魂》正文；标题换行、段落宽度和语言显示正常，未见横向溢出。正文截图为滚动中间位置，不将画面上下边缘截取当作正文缺失。

最终搜索 `--check` 通过（11,215条来源记录）。交接文档与二十篇复核索引同步标注“已接入本地网站，未 commit / push”；旧稿件 ZIP 不覆盖。
