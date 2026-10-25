# Episode 11 — Image provenance / 图片处理说明

All four figures show the **same Palace Museum album, 新00045355**, an early post-excavation Ming rubbing of the Cao Quan Stele, taken before the stone broke. Original stone: 185 CE; paper: Ming. All are whole photographed album openings, preserving three short columns per half. The cut-mounted short columns are not claimed to reproduce original stone-column adjacency.

## Acquisition and processing, 2026-10-19 UTC

The public museum collection page links directly to the four official viewers. Each viewer's public Deep Zoom metadata specifies its image bundle, full dimensions, 510-pixel tiles and one-pixel overlap. The acquisition script fetches the highest pyramid level (12), places each tile at its published coordinates and removes **only prescribed tile overlap**. It saves the assembled master as JPEG quality 96, then makes a proportional reading-size reduction fitting 1400 × 1400 pixels at JPEG quality 92. No image content was cut out of these four openings.

| Figure | Viewer | Assembled dimensions | Reading file |
|---|---|---|---|
| 1 | https://www.dpm.org.cn/bigimg/32/11 | 3794 × 3684 | images/page_11.jpg |
| 2 | https://www.dpm.org.cn/bigimg/32/23 | 3782 × 3694 | images/page_23.jpg |
| 3 | https://www.dpm.org.cn/bigimg/32/21 | 3788 × 3690 | images/page_21.jpg |
| 4 | https://www.dpm.org.cn/bigimg/32/3 | 3778 × 3696 | images/page_3.jpg |

`IMAGE_MANIFEST.json` records exact public tile roots and operations. The reading release does not include the assembled masters or source-page downloads. The first and sixth thumbnails of the museum's older gallery link to the same image; the essay does not label figure 1 as the original beginning of the inscription.

No AI generation, inpainting, handwriting reconstruction, restoration, recoloring, watermark removal or seal removal was performed. Tears, joins, paper edges, dark areas and collection marks remain. The embedded figures are smaller reading copies, not a basis for precise measurement of the stone.

## What was actually inspected

The writer viewed all four assembled/reduced images and checked the individual characters against neighboring columns. The source reviewer and the series editor independently viewed the four 1400-pixel images. Verified positions:
- Figure 1: 孝 at top of left half's middle column; 季 fourth in its far-left column, with 禾 above 子. Neighbors 之, 性, 養, 祖 remain.
- Figure 2: four 或 in the right half, far-right column fifth; middle column third; left column first and fifth. Left half's right column reads 敦煌枝分葉布.
- Figure 3: two 于, right half far-right column bottom and left half far-left column top. 曹 and 國 in right half middle column; damage/repair/red seal below 國 are separated from normal writing.
- Figure 4: right half left column 合七首藥神明, 七 second. The next displayed column, at the right of the left half, begins 膏親至離亭部. 神明 continues across the mounted columns to 膏 as the medicinal name 神明膏. 王 is the second character in the left half’s middle column; the character directly below 親 is 至.

These are actual local image inspections, not claims of final HTML browser inspection. Final article browser checks, if performed, are documented separately in README.

## Rights

图像版权归故宫博物院及其他相关权利人。**未取得再发布许可，不宣称开放授权。** 用户允许在研究包中使用并注明未获许可；这不授予对外传播权。 / Copyright remains with the Palace Museum and any other rights holders. No republication license has been obtained and no open license is claimed. Further public or commercial redistribution requires separate rights clearance.
