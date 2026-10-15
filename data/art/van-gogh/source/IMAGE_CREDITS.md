# 图像登记与使用说明

R1文字更新说明：以下登记的是需从原图文包沿用的图片。本更新ZIP不含图片文件；图像字节、原图SHA和裁切范围未变。请合并到原同名目录并保留images。

Text-update R1: the images documented below must be retained from the original package. No image files are included in this update ZIP; original image bytes, hashes and crop bounds are unchanged.

Vincent van Gogh, Wheat Field with Cypresses, 1889. Oil on canvas, 73.2 × 93.4 cm. The Metropolitan Museum of Art, New York. Accession number 1993.132; catalogue number F717. Purchase, The Annenberg Foundation Gift, 1993.

- [馆藏记录 / Collection record](https://www.metmuseum.org/art/collection/search/436535)
- [官方图像 / Official image](https://images.metmuseum.org/CRDImages/ep/original/DP-42549-001.jpg)
- [馆方开放政策 / Open Access policy](https://www.metmuseum.org/hubs/open-access)
- [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)

## 全图

images/van_gogh_wheat_field_cypresses_full.jpg

4000×3184像素，RGB JPEG，8,291,194字节。下载文件按字节原样保留，包括窄黑外缘、画布实体边缘与原ICC色彩配置。

SHA-256: b46d02a42fd3bb13b022cefc5beaa997b1d7a28cd7b53e4413d940aa0dc4014d

## 局部图

以下坐标均相对上述4000×3184像素母图，左上角为(0,0)。采用半开区间(left, top, right, bottom)，右和下坐标不计入裁切。局部无缩放、无调色、无锐化、无补绘；RGB解码像素与对应母图区域逐像素一致，PNG保存为无损，保留原ICC配置。

1. images/detail_cypresses_sky.png
   - 框：(2660, 170, 3900, 2320)
   - 1240×2150像素
   - 用途：柏树内部短密笔触与邻接云层的宽弧、山带关系
   - 注意：较高柏树顶部轮廓有技术研究记录的损伤与修复补绘；切图不将其当前轮廓视为每笔皆原作
2. images/detail_olive_hills_wheat.png
   - 框：(380, 1700, 2650, 2830)
   - 2270×1130像素
   - 用途：橄榄树碎密叶丛、远山长曲线与麦田斜笔的同框比较

每种语言的图注与替代文本均置于正文，另汇总在caption_alt_localized.json。各文件大小、像素及哈希见image_manifest.json和SHA256SUMS.txt。

## Image treatment

The full JPEG is the unchanged museum file. The PNG details retain the exact decoded RGB pixels of their stated source regions and the source ICC profile. There has been no resizing, color grading, sharpening, reconstruction or generative image editing. The image can support close looking, but its photographic lighting, digital display and enlargement do not reproduce all conditions of viewing the physical painting.
