# 怀素《自叙帖》八语图文包 · Read me

中国书法细读04 · v1.0 · 2026-10-19

## 阅读

先完整解压，再打开 **READ.html** 或 **index.html**。八个语言入口对应完整文章，不是摘要：简体中文、繁體中文、English、Deutsch、Français、Español、日本語、한국어。

每篇都有四组完整相关引文语境、五幅正文配图、传统书法细读与可选SAE附读。六个外语版本保留汉字并给出引文全文翻译、释义及图中位置。默认折叠的技术说明可点击展开。正文图可单独打开；分段摄影索引为第六张本地图。

图片、样式、语言切换和Markdown原稿全部本地可用，无外部字体、脚本、追踪或联网加载。故宫官方原图、藏品页、高清下载入口和参考文章需要联网；馆藏数据库可能因站点限制返回403，包内图文不受影响。

## 文件

- `04_zixu_zh-Hans/zh-Hant/en/de/fr/es/ja/ko.md`及相应HTML，共16篇文件。
- `READ.html`、`index.html`、`styles.css`：入口与离线样式。
- `images/`：5幅细读图与1幅32图索引。
- `IMAGE_NOTES`、`SOURCES`、`LICENSE_AND_CREDITS`、`README`：各有MD和HTML。
- `IMAGE_MANIFEST.json`：原图来源、裁切与尺寸、图像校验。
- `PACKAGE_MANIFEST.json`：语言、文件及校验信息。
- `SHA256SUMS.txt`：包内文件校验和，不含其自身。

## 研究与图像边界

具体藏本为台北故宫故書000062、记录14901。文章交代唐代著录与亲笔/年代争论，不把777题年当作纸墨年代的独立证明。前六列补写为题跋中记录的说法。32图索引按实物文字顺序而非数字文件名顺序排列，重叠未消除。

没有AI改写书迹。正文基于实际看过的官方摄影，不声称亲见原作。没有获得个别图像授权函，不声称馆方认可；公开使用条款及例外另见许可文件。没有上传Library、发信、发布网站或更改外部服务。

## English

Extract the whole archive and open **READ.html**. All eight editions are full-length essays. The six non-Chinese editions retain the Chinese passages alongside complete translations and explain the characters and positions used in the visual readings. Five illustrated details and one shared photograph index are included. Technical notes expand near the end of each essay.

The package works offline without remote fonts, scripts or image dependencies. Museum originals, alternative high-resolution downloads and references require internet access. Some museum database requests may return 403; local reading remains available.

The exact object is National Palace Museum record 14901, accession 故書000062. Attribution and dating remain qualified. All image transformations are documented, with no generated or retouched calligraphy. No individual museum permission letter or endorsement is claimed. This package has not been published or uploaded to an external service.

## 校验 / Verification

在解压目录运行 `sha256sum -c SHA256SUMS.txt` 可核对文件是否完整。SHA文件不含自身，PACKAGE_MANIFEST不含自身及SHA文件，避免循环哈希。后续文字修订后须重新生成HTML、清单、校验及ZIP。

Run `sha256sum -c SHA256SUMS.txt` from the extracted directory. The checksum file excludes itself; the package manifest excludes itself and the checksum file to avoid circular hashes. Rebuild HTML, manifests, checksums and archive after any revision.

## 本次验收范围 / QA scope

已完成八语全文对照与独立语言复核、实际配图核对、32图顺序复核、14个HTML的静态链接与结构检查、6个JPEG解码与尺寸检查；正文每页5图均有替代文字，技术说明默认折叠。浏览器在当前执行环境启动失败，因此**尚未完成浏览器渲染、移动端溢出及折叠交互的实机视觉测试**。样式沿用已认可的第一期版式，但不把静态检查称作浏览器验收。

Full-text comparison and independent language review, actual image inspection, gallery-order verification, static checks of all 14 HTML files, and decoding/dimension checks of all six JPEGs are complete. Each essay has five images with alt text and one initially closed notes section. Browser startup failed in the execution environment, so **browser rendering, mobile overflow and interactive toggling have not been visually tested**. The layout follows the approved first episode; static checks are not represented as browser testing.
