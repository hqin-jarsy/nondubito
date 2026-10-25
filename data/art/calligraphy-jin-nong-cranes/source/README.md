# 金农《相鹤经轴》 · 八语全文阅读包

入口：打开 READ.html，再选择语言。共八种完整语言：简体中文、繁體中文、English、Deutsch、Français、Español、日本語、한국어。每种都有 Markdown 和可离线阅读的 HTML，正文配四张局部图并链接整幅定位图；官方高清外链需要联网。

## 内容

- `20_jinnong_语言代码.md` 及同名 HTML：完整文章、诗文或古文全文与译义、款识说明、配图及默认折叠的校读注。
- `images/`：五张真实馆方摄影阅读图，包括一张全幅定位图、四张保留邻列的局部。
- `SOURCES.md`、`IMAGE_NOTES.md`、`IMAGE_MANIFEST.json`：作品身份、校读差异、来源、许可状态、像素、裁切坐标及图片 SHA-256。
- `MANIFEST.json`：语言和文件清单。`SOURCE_SHA256.txt`：八语 Markdown 源稿冻结值。`SHA256SUMS.txt`：阅读包文件校验值。
- `build.py`：用 Python 3 和 Markdown 库重建 HTML、入口、清单与校验值。标准运行方式为 `python build.py`。
- `source/`：研究过程使用的公开下载与摄影数据，不属于精简阅读包；重建 HTML 不依赖它。

## 图片使用

没有生成、补画、去印、调色或改变纵横比。古代文本为公版；馆方摄影另有使用条件。尚未取得馆方图像再发布许可，详见图片说明。八语完整性不意味着款识中已明确保留的未定读被猜填。未进行外部上传或发布。

校验：在本目录运行 `sha256sum -c SHA256SUMS.txt`。修改 Markdown 后应重建；源稿冻结值须在文本确认后另外更新。
