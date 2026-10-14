# 戏剧与音乐剧栏目接入复核

日期：2026-10-13。状态：本地网站接入完成，未 commit、未 push；不据此声称公网已更新。

## 本次范围

- 新栏目：`essays/theatre/index.html`，与文学、电影、电视剧并列，归入 stories。
- 首篇：`essays/theatre/hamilton.html`，英、简、繁三种完整版本。
- 中文源稿：`data/theatre/hamilton.zh.md`，与用户确认的 `outputs/Hamilton_音乐剧介绍.md` 经 `cmp` 比对完全一致。
- 英文：`data/theatre/hamilton.en.md`，逐段完整翻译，保留四节结构、剧透边界、史实限定与资料归属，不改成摘要。
- 繁体：沿用现有 CoreFoundation 转换与站内校正规则，完整正文随语言切换。
- 正文不插入链接；页尾简述资料依据和接触范围，不声称现场观剧或完整观看影像。
- 使用 Article / CreativeWork 结构化信息，不把音乐剧误标为 Book。
- 首页、探索页、完整文库（Category 18）、最近更新、搜索三语索引、内容注册表与站点地图均已接入。
- 原有“故事里的结构”戏剧内容不迁移、不重复发布；其他栏目保持不变。

## 可复现检查

以下已运行通过：

- `python3 scripts/build_theatre.py --check`
- `python3 scripts/test_theatre.py`：完整语言内容、段落数量与四节一致、资料类型、站内链接、栏目、搜索和 sitemap。
- `python3 scripts/check_site_updates.py`
- `python3 scripts/build_content_registry.py --check`：18 类，1369 个样本 HTML、465 条 canonical 记录。
- `python3 scripts/build_search_index.py --check`：11363 条源记录，新栏目与文章在英简繁索引均可发现。
- `python3 scripts/build_sitemap.py --check`：11211 条 canonical URL。
- `git diff --check`
- `scripts/test_theatre_browser.cjs`：独立无头 Chrome，390 / 1440 宽度，16 个浏览器场景；三语可见性、完整正文、无横向溢出、切换及刷新保持、四个栏目入口、Hamilton 搜索。

人工检查了手机与桌面栏目的首页、正文首屏截图。首次截图发现正文使用 header 元素触发旧全站固定导航样式，已改用与现有导读一致的 section，并增加样式回归断言；随后全套浏览器测试通过。测试不使用用户浏览器个人资料，远程字体被屏蔽以验证回退字体下的排版。

构建：`python3 scripts/build_theatre.py`。发现层按既有脚本更新；下次新增作品时保留栏目独立，不修改书籍导读生成器。
