# 苏轼《寒食帖》八语图文正式版 v1.0

日期：2026年10月18日。交付形式：一个总ZIP，内含八语全文、静态HTML阅读页、共用七图与来源许可资料。未上传网站或Cloudflare。

## 直接阅读

1. 将ZIP完整解压，保留文件夹内的相对位置。
2. 打开 [READ.html](READ.html)，选择语言；[index.html](index.html)是相同入口，适合静态托管的默认首页。
3. 各语言页面可相互切换，图片可单独打开。文末校读说明默认折叠，点击即可展开。
4. 全文与本地图片无需网络；故宫高清原图、典故原文和射线09等外部链接需要网络。

八语正文文件均以01_hanshi_开头，语言后缀分别为zh-Hans、zh-Hant、en、de、fr、es、ja、ko。每种语言同时提供.md可编辑原稿与.html阅读版。

## 文件组成

- 8份完整文章Markdown：简体、繁体、英语、德语、法语、西班牙语、日语、韩语。
- 8个对应HTML全文页、READ.html及index.html两份同内容入口、styles.css共用样式。资料说明也提供HTML便于阅读。
- images/：7张共用JPEG，包括5张正文局部、苏轼正文定位图、全卷分段摄影索引。不按语言重复图片文件。
- IMAGE_NOTES.md / .html：逐图来源、裁切范围、加工边界、中文说明和英文导览。
- SOURCES.md / .html：史实、异文、典故和可选附读的来源记录。
- LICENSE_AND_CREDITS.md / .html：图像许可边界、建议署名与文章作者身份。
- IMAGE_MANIFEST.json：七图来源与尺寸、五张局部裁切坐标、图像SHA-256。
- PACKAGE_MANIFEST.json：语言文件、共用图像和版本信息。
- SHA256SUMS.txt：除校验清单自身外，包内所有文件的SHA-256。

简体正文完整沿用已认可v0.2，仅更新版本标。繁体为全文对应稿。六个外语版本保留两首中文诗文及完整译文、全部细读、可选SAE附读与校读说明，并为讨论的汉字提供本语释义和看图指引。六外语不以摘要代替全文；中文诗句的五言分行也不被误当作墨迹的实际分列。

## 静态部署说明

1. 先在本地打开READ.html检查。确认页面、图片与语言链接正常，再把本目录完整复制到拟部署的静态目录。
2. 保留HTML、Markdown、CSS与images/的相对结构。没有构建步骤、服务端接口、外部脚本或远程字体依赖；默认首页为index.html。
3. 若整合到既有网站，可采用.md正文或.html中的article内容，按网站结构调整相对图片路径和语言导航。若改变语言URL，请同步修改所有导航链接，勿直接猜测站点其他文章的语言路径。
4. 保留每张图的馆方署名、官方来源、裁切说明及许可边界。不要把索引图冒称无缝全卷图，也不要为这些展览JPEG自动套用Open Data另一下载来源的CC BY标签。
5. 部署前检查UTF-8编码、移动端换行、图像载入、details折叠、外部来源链接。此包不含账户、密钥或自动发布脚本；实际发布由用户另行完成或授权。

如需校验完整性，可在包内运行sha256sum -c SHA256SUMS.txt；macOS可用shasum -a 256 -c SHA256SUMS.txt。仅重新压缩ZIP不会改变内部文件校验值；编辑正文后需重新生成对应HTML与清单。

## English quick start

Extract the entire ZIP and open [READ.html](READ.html). All eight full essays, seven shared images and the stylesheet work offline. Click an image to open it separately. Expand the reading notes near the end of each essay. Museum and other external links require internet access.

For static hosting, copy the complete folder while preserving its relative paths; index.html is the entry page. No build step, server API, external script or web-font download is required. If integrating into an existing site, use the editable Markdown or the article element in each HTML file, then update image paths and all language links together. Retain museum credits, cropping notes and permission distinctions. This delivery does not publish or upload anything.

The Chinese source and its full Traditional Chinese counterpart are accompanied by six complete language editions. Every non-Chinese edition keeps the Chinese poems, full translations and the original visual argument, with local-language glosses for the characters being examined. The shared navigation images retain Chinese labels; the essays and image guide explain them.


## 验证范围

已核八语正文的结构与完整性、HTML与Markdown正文一致性、全部包内相对链接、默认折叠的details结构、每篇五张正文图、六外语七图导览，以及七图与已认可v0.2图像的逐字节一致性和SHA-256。简体原稿的改动仅为版本标记。实际浏览器截图与点击交互未能在本次执行环境中完成自动化实测；部署前仍应按上述清单在目标浏览器中检查显示和折叠交互。

Validation covers article structure, HTML/Markdown text agreement, local links, disclosure markup, image counts and image checksums. Browser screenshots and click interactions could not be automatically tested in this execution environment; verify the display and disclosure controls in the destination browser before publication.
