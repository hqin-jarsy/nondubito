# 赵孟頫《胆巴碑》八语图文正式版 v1.0

日期：2026年10月19日。对象为故宫博物院藏《赵孟頫楷书帝师胆巴碑卷》，纸本墨迹。本包是供作者审阅的八语全文与本地图文包，尚未发布到网站。

## 直接阅读

1. 将ZIP完整解压，保留各文件和images文件夹的相对位置。
2. 打开 [READ.html](READ.html)，选择语言；[index.html](index.html)为相同入口。
3. 正文五张局部图均可点击单独打开。文末校读、尺寸和图像处理说明默认折叠，点击展开。
4. 全文、本地图像和样式无需网络。馆方高清浏览器、作品页和其他外部链接需要网络。

八语正文文件均以05_danba_开头，语言后缀为zh-Hans、zh-Hant、en、de、fr、es、ja、ko。每种语言都有可编辑Markdown原稿与HTML全文阅读版。

## 本包内容

- 八篇完整Markdown与八个对应HTML全文页。
- READ.html、index.html语言入口与styles.css共用样式。
- images内七张共用JPEG：一张全卷定位图、五张正文局部、一个六段顺序索引；不按语言重复存图。
- [IMAGE_NOTES](IMAGE_NOTES.html)：逐图出处、坐标、加工边界和阅读指引；同附Markdown版。
- [SOURCES](SOURCES.html)：作品资料、原文校读及可选附读来源；同附Markdown版。
- [LICENSE_AND_CREDITS](LICENSE_AND_CREDITS.html)：馆方使用条件、许可状态、署名建议；同附Markdown版。
- IMAGE_MANIFEST.json：七图尺寸、源影像信息、五张局部坐标、处理说明和图像SHA-256。
- PACKAGE_MANIFEST.json：语言文件、共用图像和版本信息。
- SHA256SUMS.txt：除校验清单自身外，包内全部文件的SHA-256。

简体正文经逐图核对后定稿；繁体为完整对应稿，并校正有词义差别的繁简字。六个外语版本保留全部正文、两段所讨论的中文原文及完整译文、题署和关键汉字、本语释义、位置指引、五幅本语图注、可选Self-as-an-End附读及折叠说明。译文不是摘要，古文的语句分行不被当作墨迹的实际分列。

## 图像及使用条件

图像来自故宫博物院的公开数字影像。本包没有取得另行公开发布、出版或商业使用这些图像的馆方书面许可；署名、提供外链和本地保存都不等于获得该许可。实际发布前须核实拟用平台和用途下的权利，详见许可文件及[馆方条款](https://www.dpm.org.cn/bottom/privacy/254.html)。

五张细部保留邻列，从馆方影像作矩形裁切；没有生成、描改、锐化或修补书迹，没有移除收藏印。全卷定位图只供方位识别。六段索引是按原卷先后排列的六条，不是另一个无缝长卷；编号从上向下，各条内由右向左读，第六条左边的空白画布不是历史纸面。精细笔画请对照[官方高清浏览器](https://www.dpm.org.cn/dyx.html?path=/Uploads/tilegenerator/dest/files/image/8831/2017/0027/img0007.xml)。

## 完整性与验证

可在解压目录运行sha256sum -c SHA256SUMS.txt；macOS可用shasum -a 256 -c SHA256SUMS.txt。仅重新压缩ZIP不会改变内部文件校验值；编辑正文后应同步更新对应HTML和清单。

已完成八语结构、段落和全文对应检查，HTML与Markdown正文一致性检查，包内相对链接及图片路径检查，默认折叠的details结构、每篇五图与七图导览检查，以及图像尺寸和SHA-256核验。全部七张本地图像已实际查看，细读所用字形、邻列与位置经过核对。

本次执行环境限制了浏览器自动化所需的本地socket，未能完成实际浏览器截图与点击交互测试。这里的HTML核验是静态文档和文本检查，不代表已经在所有浏览器中实测显示效果。正式使用前请在目标浏览器检查窄屏换行、图片打开、语言切换及文末折叠交互。

本包无服务端接口、外部脚本、远程字体、账户或发布脚本。获得必要权限后，如整合至网站，可使用Markdown原稿或HTML的article正文；应一起调整相对图片路径、八语导航和来源链接，保留署名、裁切说明与许可边界。

## English quick start

Extract the complete ZIP and open [READ.html](READ.html). The eight full essays, seven shared images and stylesheet work offline. Select a figure to open its local image; expand the textual and image notes near the end of each essay. Official museum and other external links require internet access.

The object is an ink-on-paper handscroll in the Palace Museum, Beijing. All six non-Chinese versions retain the full essay, the two Chinese passages discussed with complete translations, Chinese characters with local-language glosses and positions, localized figure captions, the optional Self-as-an-End reading, and the technical notes. Traditional Chinese is a complete counterpart with contextual character conversion checked.

Five rectangular details preserve neighboring columns. No strokes, seals or paper traces have been generated, redrawn, sharpened or repaired. The overview is for orientation; the numbered six-band index preserves the scroll's sequence but is not a seamless image. Read bands from top to bottom, each band from right to left, and each column downward. The empty canvas to the left of band 6 is not historical paper.

No separate written museum permission has been obtained for public publication, print publication or commercial reuse of the images. This local review package has not been published online. Check the intended use against the museum's terms and licensing requirements before publication.

Validation covers full article structure, Markdown/HTML text agreement, local links, image paths, disclosure markup, the seven-image guide, image dimensions and checksums. All seven local images have been visually inspected. Browser screenshots and click interactions could not be tested because the execution environment blocked the local socket needed by browser automation; verify display and controls in the destination browser before use.

The package has no server API, external script or remote-font dependency. Preserve relative paths when moving the folder. To check integrity, run sha256sum -c SHA256SUMS.txt, or shasum -a 256 -c SHA256SUMS.txt on macOS. If an essay is edited, regenerate its HTML and the checksums together.
