# 图像登记 Image credits

R1文字更新说明：以下登记的是需从原图文包沿用的图片。本更新ZIP不含图片文件；图像字节、原图SHA和裁切范围未变。请合并到原同名目录并保留images。

Text-update R1: the images documented below must be retained from the original package. No image files are included in this update ZIP; original image bytes, hashes and crop bounds are unchanged.

## 作品 Work

John Constable / 约翰·康斯特布尔
Wivenhoe Park, Essex / 埃塞克斯维文霍公园
1816; oil on canvas / 布面油画; 56.1 × 101.2 cm
National Gallery of Art, Washington, Widener Collection
Accession / 藏品号: 1942.9.10

Object: https://www.nga.gov/artworks/1147-wivenhoe-park-essex
Official download: https://api.nga.gov/iiif/c49fa4a0-1e3a-4038-b7dd-ad9036146e73/full/full/0/default.jpg

## 许可 Rights

馆藏页明确标记本件媒体免费且属公版。馆方Open Access政策以CC0提供开放图像。本包全图和裁切均署名National Gallery of Art，CC0；此许可判断仅针对本件图像。

The object page explicitly identifies the media as free and in the public domain. The Gallery’s Open Access policy provides qualifying images under CC0. All images here are credited National Gallery of Art, CC0. This finding applies to this image, not indiscriminately to all Gallery content or research text.

Policy: https://www.nga.gov/terms-and-notices#open-access
CC0: https://creativecommons.org/publicdomain/zero/1.0/

## 全图 Master

images/constable_wivenhoe_park_full.jpg
- Actual dimensions / 实际像素: 4096 × 2218
- Bytes / 字节: 2,408,260
- SHA-256: e2e4af8534c70f0c6a37aecd89e10f691b36ff736991cd267a1f39ee85a976bc
- Embedded ICC profile / 内嵌ICC: preserved, 3,144 bytes
- Transformation / 改动: none; byte-for-byte copy of the official downloaded JPEG

IIIF元数据所列底图尺寸大于实际下载文件，本包不声称提供该大图。文件像素比例与实物尺寸比例略有不同，仍保留官方下载文件原比例；不据此推定作品本身遭到裁切。

The IIIF metadata lists a larger underlying image than the file returned by the download. This package does not claim to contain that larger image. The downloaded aspect ratio is preserved despite its small difference from the ratio of the recorded physical dimensions; this does not establish that the painting itself was cropped.

## 局部 Crops

Coordinates are source-pixel rectangles [left, top, right, bottom], with right and bottom exclusive. Origin is the upper-left corner. 坐标以原图左上角为原点，右与下界不含该像素。

- images/detail_fence_meadow.png
  Rectangle: [0, 1100, 2250, 2218]
  Dimensions: 2250 × 1118
  Purpose: foreground fence, cattle, grass and shadow, bridge and donkey cart at different distances / 木栅、牛、草地明暗及远处桥与驴车的尺度
- images/detail_house_trees.png
  Rectangle: [1250, 850, 2700, 1850]
  Dimensions: 1450 × 1000
  Purpose: house, opening among trees, illuminated slope and red reflection / 住宅、树隙、亮坡与红色反光
- images/detail_water_boat.png
  Rectangle: [2350, 1100, 4096, 2010]
  Dimensions: 1746 × 910
  Purpose: tree reflections, swans, fishing boat and net line / 树影、天鹅、渔船与网线

局部从JPEG一次解码的像素直接裁切，以PNG无损保存；不缩放、不调色、不锐化、不补绘。每张PNG保留与主图字节一致的ICC配置文件。PNG保存不改变源JPEG已经具有的压缩属性，亦不增加原图细节。

The crops are made directly from the once-decoded JPEG pixels and saved losslessly as PNG. No resizing, colour adjustment, sharpening or reconstruction is applied. Each PNG retains an ICC profile byte-identical to the master’s. Lossless PNG storage neither reverses existing JPEG compression nor creates additional detail.

每一局部均已实看，并与全图对照。各语图注和alt已在相应文章内提供，另汇总于captions_alt_8lang.json。

Every crop has been visually inspected against the full image. Local-language captions and alt text are supplied in each essay and collected in captions_alt_8lang.json.
