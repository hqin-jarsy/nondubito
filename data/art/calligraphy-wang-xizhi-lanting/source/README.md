# 《兰亭序》神龙本八语图文包 · 阅读说明

中国书法细读 02 · 正式版 v1.0 · 2026年10月19日

## 开始阅读

解压整个文件夹后，打开 [READ.html](READ.html)。也可从 [index.html](index.html) 进入。选择简体中文、繁體中文、English、Deutsch、Français、Español、日本語或한국어。八篇均为完整文章，不是摘要；每篇附《兰亭序》全文与现代语译文，六个外语版本还保留汉字原文、字义及看图位置说明。

所读对象为北京故宫博物院藏《兰亭序》唐摹神龙本。传统归于冯承素，摹者归属不可靠；不是王羲之亲笔原迹。正文从两处“之”字和邻字的关系出发，经过开头、跨列、感慨段落与结尾，再附一段可选的SAE（Self-as-an-End）阅读。

五张局部图嵌入各语言正文；一张完整正文本幅定位图在折叠说明与入口中链接。全部六张图共用一套文件。小图离线可看；点图可单独打开。官方资料、公开高清原图及射线散文链接需要联网。

## 文件内容

- `02_lanting_[语言].md`：八份完整Markdown稿，语言代码为 `zh-Hans`、`zh-Hant`、`en`、`de`、`fr`、`es`、`ja`、`ko`。
- 同名 `.html`：八份适合电脑及手机阅读的静态页面，正文与Markdown一致。校读及图片权利说明默认折叠。
- `READ.html`、`index.html`：八语入口。
- `styles.css`：本地共用样式，无在线字体、脚本、追踪或第三方嵌入依赖。
- `images/`：六张JPEG，保留相邻字列，不是AI生成或重绘书迹。
- [IMAGE_NOTES.html](IMAGE_NOTES.html)：图片位置、出处、处理方式及英文导览；附同名Markdown。
- [SOURCES.html](SOURCES.html)：官方藏品说明、官方图版、实际下载来源与SAE散文记录；附同名Markdown。
- [LICENSE_AND_CREDITS.html](LICENSE_AND_CREDITS.html)：图片权利状态与建议署名；附同名Markdown。
- `IMAGE_MANIFEST.json`：源图网址、裁切坐标、尺寸、处理方式及图片SHA-256。
- `PACKAGE_MANIFEST.json`：版本、语言与文件概况。
- `SHA256SUMS.txt`：除校验表本身之外的全部包内文件SHA-256。

## 看图和图片权利

从右向左读列，每列从上到下读。定位图只含28列正文本幅，不含装裱后的引首与题跋；不能称为整件手卷的完整照片。局部图保留相关前后字和左右列，边缘可见毗邻列的少量残部。

六张图的直接来源是Wikimedia Commons的File:LantingXu.jpg，已与故宫藏品图及官方刊物图版核对。Commons页面标注PD-Art/Public Domain Mark；本包未取得故宫或其他相关权利人的个别图片授权。署名不等于授权，不构成对任何地区和用途均可再用的保证。进一步发布前请阅读随附权利说明并核对适用要求。

这是本地阅读与静态部署准备包，没有上传网站或Cloudflare，也没有替作者决定对外发表、图像授权或许可条款。要离线使用，请保留目录结构，不要只单独移动HTML文件。

## English guide

Extract the complete folder, then open [READ.html](READ.html). All eight editions contain the full essay, the complete classical Chinese preface and a complete modern-language translation. The six non-Chinese editions retain the Chinese original and explain the characters, positions and reading direction used in the close readings. Technical notes and image-rights information are initially collapsed.

The object is the Tang-dynasty Shenlong copy in the Palace Museum, Beijing, traditionally attributed to Feng Chengsu. Its copyist is not securely identified. It is not Wang Xizhi’s autograph. The essay follows repeated instances of 之 in their local relationships, then offers an optional reading through SAE, Self-as-an-End.

Five details are embedded in each essay; a sixth image shows the entire main text. This overview excludes the mounted title material and later colophons. Read columns from right to left and characters downwards. Images and navigation work offline. External museum, high-resolution and reference links require internet access.

The direct image source is Wikimedia Commons, File:LantingXu.jpg, visually checked against official museum illustrations. Commons labels the source PD-Art/Public Domain Mark. No individual permission has been obtained from the Palace Museum or other relevant rights holders. That platform statement is not a licence granted by the museum to this package, and attribution is not a legal guarantee of reuse. Read the accompanying image notes and permissions document before further publication.

The package is local and ready for reading or later static deployment. It has not been published to a website or Cloudflare. Keep all files and folders together.

## 校验范围 · Validation scope

八份Markdown已作独立全文审读，改动已复核。程序检查了八语HTML与Markdown正文一致、所有本地链接及锚点可定位、每篇五图和一个默认折叠说明、图片尺寸与清单哈希相符。实际查看了六张图片，并用官方图版核对主要字位。

本次未完成浏览器渲染验收：Playwright配套浏览器不可用，尝试系统Chromium时又遇到运行环境的socket限制。不能把上述静态检查称为浏览器显示测试通过。

All eight Markdown editions received independent full-text review and correction checks. Programmatic validation covers Markdown/HTML text equality, local links and anchors, five images and one initially collapsed notes section per article, and image dimensions and hashes. All six images were visually inspected against their stated positions. Browser rendering was not validated: the bundled Playwright executable was unavailable, and system Chromium could not initialise its socket in this runtime. Static checks are not presented as a successful browser test.
