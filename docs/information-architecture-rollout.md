# Non Dubito 信息架构实施记录

状态：公开版本已稳定上线

日期：2026-09-05

设计基准：[`information-architecture-v1.md`](information-architecture-v1.md)

## 1. 结果

本轮把 Non Dubito 从“首页兼任全部目录”的网站，整理为具有三种明确找路方式的多语言阅读站：

- 不熟悉本站的读者，从 Home、Start Here 或策划阅读路径进入；
- 想浏览的读者，从 Explore 的五个方向进入，并可继续到完整 Library；
- 带着题目、人物、作品或问题来的读者，使用八种语言的站内 Search；
- 回访读者通过 Latest 区分新作、实质修订和语言扩展；
- 从重点理论文章进入的读者，可借助面包屑、系列位置和三条不同职责的后续路线继续阅读。

所有已公开的文章 URL 与既有目录结构均保留；本轮没有为了展示分类而移动正文页面。

## 2. 分批状态

| 批次 | 状态 | 已上线内容 |
| --- | --- | --- |
| 0. 蓝图与冻结线 | 完成 | 页面职责、五扇门、URL 稳定与多语言原则形成设计基准 |
| 1. 内容注册表 | 原型完成 | 扫描 548 个代表页面，生成 199 个 canonical 记录；异常保留为审计项，不猜测缺失日期 |
| 2. 导航与首页原型 | 完成并归档 | 桌面、平板、手机层级和语言工具完成原型验证，随后进入公开实现 |
| 3. Explore 与新 Home | 完成 | 首页成为接待厅；Explore 以五个读者兴趣方向组织内容；Library 保持完整目录职责 |
| 4. Latest | 完成 | 编辑事件清单驱动 Latest 与首页更新区；语言扩展不会被重复算作多篇新作 |
| 5. Search | 完成 | 八种语言分别建立索引；英／简／繁同页可正确进入对应模式；日／法／德／西／韩拥有本地化搜索界面 |
| 6. 系列页与文章上下文 | 编辑试点稳定 | 在 SAE Foundations、First Critique、Republic、Nicomachean Ethics、Consolation、Buddhist Thought 和意识路线等高价值路径部署；没有对 7,000 多页机械批量生成推荐 |
| 7. 多语言频道 | 入口层完成 | 六个独立语言频道接入本语言 Foundations、搜索、读者导览、sitemap 与互相回指的 hreflang；英／简／繁继续共用主站入口 |

## 3. 当前公开结构

一级阅读入口保持为：

`Start Here · Explore · Latest · Search · About · Language`

Logo 返回 Home；完整 Library 仍可从 Explore、首页与页脚到达，但不再要求新读者先理解全站分类。

Explore 的五扇门为：

1. SAE 与哲学；
2. 日常生活；
3. 心灵、AI 与技术；
4. 历史、权力与文明；
5. 文学、影视与叙事。

这些是展示路径，不改变文章的 canonical 身份或物理目录。

## 4. 多语言边界

当前搜索索引覆盖 English、简体中文、繁體中文、日本語、Français、Deutsch、Español 与 한국어。搜索默认只查当前阅读语言，读者可以主动改为其他语言或全部语言。

日、法、德、西、韩频道使用本语言的频道首页、SAE Foundations 入口与搜索界面。Explore、Latest、About 和完整 Library 目前仍是英／简／繁共用的全站地图；频道链接会明确进入这张全站地图，而不会伪装成尚不存在的完整本地化页面。这是分阶段的产品边界，不是 URL 缺口。

如果未来要继续本地化，优先顺序应是：

1. 为五个语言频道编辑各自的 Explore 策展文案；
2. 为 Latest 增加按阅读语言生成的摘要；
3. 最后才考虑本地化完整 Library，因为它的维护面最大。

## 5. 移动端与语言保持

- 新站点壳在窄屏隐藏长导航，保留搜索按钮和菜单按钮；
- 菜单中的八语言入口横向滚动，不挤压页面宽度；
- 旧式语言频道的导航保持单行，空间不足时只在导航内部滚动；
- 四张频道导读卡在平板变两列、手机变单列；
- Search 使用 `ui` 保存界面语言、`in` 保存索引语言，结果链接继续进入同一语言版本；
- 尊重 `prefers-reduced-motion`，关闭非必要动效。

## 6. 可重复维护

本轮建立或固化了以下事实源与检查：

- `data/content-registry-prototype.json`：canonical 内容身份的代表样本；
- `data/site-updates.json`：公开更新事件；
- `data/search-index.json` 与 `data/search/*.json`：八语言搜索索引；
- `scripts/build_content_registry.py`：注册表原型与异常报告；
- `scripts/check_site_updates.py`：Latest 与事件清单一致性；
- `scripts/build_search_index.py`：搜索索引生成与陈旧检查；
- `scripts/audit_reader_context.py`：文章定位与继续阅读结构覆盖；
- `scripts/audit_language_channels.py`：频道入口、搜索语言、公开元数据、canonical、hreflang 与 sitemap 完整性。

当前公开快照包含 7,281 个 HTML 文件，其中 7,252 个位于 `essays/`。sitemap 有 4,609 个唯一 URL：没有重复条目，也没有指向不存在文件的条目。

## 7. 刻意保留的后续工作

以下事项不应以“覆盖率”名义批量完成：

- 全站每篇文章的三路线推荐，需要编辑确认关系，而不是按词频生成；
- 原型注册表中缺少的历史发布日期继续留空，除非找到可靠来源；
- 日／法／德／西／韩的 Explore 与 Latest 需要真正的本语言策展，不做字面替换；
- 超大型书架继续按具体媒介和读者问题分组，不强迫所有类别复制同一模板。

因此，本轮信息架构整理已完成；之后可以恢复内容发布，同时把新系列登记、Latest 事件和搜索索引更新纳入每次上线流程。
