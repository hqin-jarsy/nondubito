# Published image provenance / 配图来源

[Collection record / 馆藏记录](https://www.dpm.org.cn/collection/impres/234635.html)

# Episode 12 — Image provenance / 图片处理说明

## Same physical album / 同一实体册页

All four figures reproduce the Palace Museum's Ming-dynasty rubbing album 《鲁相韩勅造孔庙礼器碑》, accession **新00044512**, from its public Digital Cultural Relics collection. The Han stone was erected in 156 CE; the paper rubbing is Ming, not Han. The depicted short columns are cut-mounted album strips, not the original stone's complete columns.

Collection record: https://digicol.dpm.org.cn/cultural/detail?id=f13cba4b1de349ca92bc1f3be913ecf3&source=6

## Actual acquisition, 2026-10-19 UTC

1. Read the public collection page and its linked image-list iframe. Its 39 entries provide the public image identifiers and thumbnail resources. The four selected entries are recorded in `IMAGE_MANIFEST.json`; the 39-page numbering below refers to that image list, not an asserted original leaf or stone-face number.
2. Open each public `culturalImage/detail/{imageId}` link in the **assistant's cloud Chromium browser**. The normal site navigation resolves to `/iView?id={imageId}&v=1` and displays its zoomable photographic image.
3. Wait for the actual image to render, inspect it, and save the browser screenshot at **1165 × 747 pixels**. Original captures were retained during preparation as `sources/viewer_25.png`, `viewer_39.png`, `viewer_23.png`, `viewer_10.png`.
4. Crop only exterior viewer interface/background using the exact boxes below. Save the result as JPEG, quality 94. The crop coordinates use Pillow's `(left, top, right, bottom)` convention, right and bottom exclusive. The four JPEGs contain the whole photographed album opening, including the paper borders and neighboring columns. No glyph-only cutout was made.

| Fig. | Public list index | Image ID | Saved source | Crop box | Embedded image | Dimensions |
|---|---:|---|---|---|---|---|
| 1 | 25 | 65d1005874754947bd37a041671d574c | sources/viewer_25.png | (197, 4, 953, 690) | images/page_25.jpg | 756 × 686 |
| 2 | 39 | eb72e8a6e6be4657b977b7e8a405c7b7 | sources/viewer_39.png | (182, 4, 968, 690) | images/page_39.jpg | 786 × 686 |
| 3 | 23 | 82977bf6cd644bfd904f5d33fe91d888 | sources/viewer_23.png | (182, 4, 968, 690) | images/page_23.jpg | 786 × 686 |
| 4 | 10 | 97f9220710314c8187c9536219eeab06 | sources/viewer_10.png | (179, 4, 972, 690) | images/page_10.jpg | 793 × 686 |

High-resolution viewers, respectively:
- https://digicol.dpm.org.cn/culturalImage/detail/65d1005874754947bd37a041671d574c
- https://digicol.dpm.org.cn/culturalImage/detail/eb72e8a6e6be4657b977b7e8a405c7b7
- https://digicol.dpm.org.cn/culturalImage/detail/82977bf6cd644bfd904f5d33fe91d888
- https://digicol.dpm.org.cn/culturalImage/detail/97f9220710314c8187c9536219eeab06

The embedded files are reading-size browser captures, **not downloaded full-resolution masters**. Use the official viewers for close examination beyond this resolution. The public thumbnails show a different overlaid display pattern; no watermark was removed from those thumbnails. The figures were captured separately from the normal public viewer's own rendered image. There was no generative processing, restoration, recoloring, mark or seal removal, inpainting, or synthetic drawing.

## Actual visual checks / 实际看图

The writer inspected the four rendered official images and the resulting local crops. A second source reviewer and the series editor independently inspected the four local figures. Specific checks:
- Fig.1: left opening middle column 宅 (third), 廟 (fourth), 更 (fifth); right opening far-right 造立禮器樂之; next column 音符鐘磬瑟鼓.
- Fig.2: right opening middle column 王 (third), preceded by 百 and followed by 不; left opening right column 王 (fourth), preceded by 天.
- Fig.3: right opening middle column 禮樂陵遲 (second–fifth); far-right 心念 (third–fourth).
- Fig.4: right opening left column 魯劉元達二百; adjacent middle column ends 二百. The exact original stone face is not assigned from this cut-mounted image alone.

## Reproduction and rights

The four embedded figures were independently reproduced from the unaltered original captures using the listed coordinates and JPEG quality 94; all four file hashes matched exactly. Research captures and thumbnail reference sets are not included in this reading release. The local `build.py` reproduces the reading pages from the included images and full Markdown files; it does not automate new browser captures or obtain high-resolution masters.

图像版权属于故宫博物院及相关权利人。**未取得再发布许可，不宣称开放授权。** 用户允许在研究包中使用并明确说明未获许可的图像；这不构成对外再出版授权。公开传播或商业出版须另行核权。 / Copyright remains with the Palace Museum and any other relevant rights holders. No republication license has been obtained; no open license is claimed. Further public or commercial redistribution requires separate rights clearance.
