# 《古老故事里的结构》六语全文重译与整合验收

日期：2026-11-08
仓库：`/Users/hanqin/Documents/GitHub/nondubito`
基线提交：`f7b189c3f052dd2cc778758f23453d61875e93f1`

## 完成范围

19 篇文章的英文、日文、法文、德文、西班牙文和韩文均已按中文全文重新翻译，共 114 份译文、14,688 个对齐内容块。中文底稿共 2,448 块，含标题、2,267 个正文段落和 162 处分隔。叙事、短段落、提问、论证推进、反方限制、强调和篇末文本依据均保留，没有用摘要代替正文。

全文已整合到原有 120 个页面，包括文章页与系列入口。URL、语言入口、上下篇、搜索、页面元数据及统计脚本保留。8 种语言的搜索分片仅更新本系列既有的 160 条记录，未改变记录 URL、分片结构或其他系列记录。修复了本系列搜索结果选择英文／简体／繁体后，打开文章仍可能使用上次保存语言的问题。

审查按 01–05、06–10、11–15、16–19 四批完成，记录见 `data/ancient-full/reviews/`。逐块翻译及复核之外，另有覆盖全部 19 篇、344 个译文块的独立中文对照抽查。该抽查不等于由母语编辑独立逐句校订全部 114 篇译文，也不等于对每项古代史实重新进行原文版本校勘。

## 中文保留与已批准修订

40 个原有简繁中文区域均已核验，只应用两处有精确记录的小修：

- 第 15 篇“善待拒绝者”改为“善待被拒绝者”，繁体同步，以修正上下文中被拒绝者与拒绝者的指代倒置。精确前后文本见 `data/ancient-full/minor-source-correction.json`。
- 第 04 篇经作者明确批准，“伊邪那岐的悲剧，或许不只在于他回头看了。”改为“伊邪那岐的悲剧，或许不只在于他违约看了她。”繁体及六语同步，只修改该句，后续论证保留。精确授权与八语前后文本见 `data/ancient-full/approved-source-corrections.json`。

原始中文输入和 120 页原始快照保持不变；生成器通过有哈希保护的修订记录应用上述变化。第 04 篇先前待裁定的问题现已解决，其《古事记》情节依据仍保留在审查记录中：

- 国学院大学《古事记》研究第九章：https://kojiki.kokugakuin.ac.jp/wp-content/uploads/2025/07/09-Studies-on-the-Kojiki-Chapter-9-The-Land-of-Yomi-1.pdf
- Chamberlain 英译第九节：https://en.wikisource.org/wiki/Kojiki_(Chamberlain,_1882)/Section_9

第 07 篇“以第八至十一泥版为主”的限定保留，未扩大修改。第 17 篇的压缩表达与第 19 篇关于履约和胁迫的解释性张力，也未作为既定错误去改动中文；译文保留其上下文和限制条件。

## 可复现生成与保护

- 规范译文：`data/ancient-full/translations/NN.LANG.json`。
- 中文来源、快照和校验清单：`source/`、`source-snapshots/`、`source-manifest.json`、`chinese-baseline.json`。
- 全文生成器：`scripts/build_ancient_full_editions.py`。
- 原有合集生成器已接入全文覆盖步骤，普通重建不会重新退回简写版。
- `last-build.json` 记录已生成标题与正文。未纳入规范译文的人工 HTML 改动会被检测，避免静默覆盖。
- 专项单元测试与重建一致性检查已加入现有 CI。

重建与检查：

```sh
python3 -B scripts/build_ancient_full_editions.py --refresh-search
python3 -B -m unittest discover -s scripts -p test_ancient_full_editions.py
python3 -B scripts/build_ancient_full_editions.py --check
```

## 最终验证

- 专项 10 项测试全部通过，包括完整结构与强调、正文一致性、原文保护、可重复重建、人工改动保护、导航和搜索范围。
- 浏览器覆盖 1440、390、320 像素宽度，19 篇文章及系列入口、全部 8 种语言，共 480 个阅读视图。逐段 DOM 文本与规范输入一致，无横向溢出、无页面脚本错误。
- 连续语言切换、上下篇、返回系列入口、浏览器前进后退、无效保存语言回退、URL 参数与锚点保留，以及 8 种语言的实际搜索跳转全部通过。
- 德／日／韩 320 像素截图已逐张检查。调整仅限本系列的小屏标题字号、德语标题自动断词和韩语按词换行后，重新跑完浏览器全套检查；标题与正文均可正常阅读。
- 全站统计检查扫描 13,624 个公开页面，0 个统计脚本错误，0 个冲突副本。
- 现有工作流 19 条命令已全部运行。16 条通过；下列 3 条与整合前基线相同，均源于既有更新记录 `updates[1]` 至 `updates[4]` 的语言列表问题：
  - `scripts/check_site_updates.py`
  - `test_home_updates.py`
  - `test_method_introduction.py`
- 没有新增工作流失败。上述既有元数据问题未在本次翻译范围内改动，不能把全站 CI 描述为全部通过。
- `git diff --check` 通过。HEAD 与起始基线一致，未 commit、未 push；所有成果保留在本地工作区。

批准修订后的追加验收记录见 `data/ancient-full/validation-approved-04.json`，包括原始输入与未相关工作保护、单句变更范围、搜索刷新和浏览器回归。

机器可读证据位于 `data/ancient-full/validation-browser.json`、`validation-preservation.json`、`validation-baseline-workflow.json` 和 `validation-final-workflow.json`。
