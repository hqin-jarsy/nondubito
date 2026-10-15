# 图像登记 Image credits

R1文字更新说明：以下登记的是需从原图文包沿用的图片。本更新ZIP不含图片文件；图像字节、原图SHA和裁切范围未变。请合并到原同名目录并保留images。

Text-update R1: the images documented below must be retained from the original package. No image files are included in this update ZIP; original image bytes, hashes and crop bounds are unchanged.

## 作品 Artwork

Camille Pissarro, The Boulevard Montmartre on a Winter Morning, 1897. Oil on canvas, 64.8 × 81.3 cm.

The Metropolitan Museum of Art, New York. Gift of Katrin S. Vietor, in loving memory of Ernest G. Vietor, 1960. Accession 60.174.

[Object record](https://www.metmuseum.org/art/collection/search/437310) · [Collection API](https://collectionapi.metmuseum.org/public/collection/v1/objects/437310) · [Official original-size public image](https://images.metmuseum.org/CRDImages/ep/original/DP-21959-001.jpg) · [Met Open Access policy](https://www.metmuseum.org/hubs/open-access)

Image status: Public Domain. Met's Open Access image release: CC0. Downloaded and checked 2026-10-15.

## 文件与处理 Files and processing

Coordinate convention: (left, top, right, bottom), measured in pixels from the top-left corner of the complete 4000 × 3230 source. The right and bottom edges are exclusive. PNGs preserve the decoded source pixels exactly; no resizing or resampling has taken place.

| File | Figure | Dimensions | Source coordinates | Processing |
|---|---|---:|---|---|
| images/pissarro_boulevard_winter_full.jpg | 1 | 4000 × 3230 | Full file | Byte-for-byte copy of official download |
| images/detail_distant_convergence.png | 2 | 1400 × 1000 | (800, 850, 2200, 1850) | Crop only, lossless PNG |
| images/detail_traffic_intervals.png | 3 | 1650 × 1200 | (1050, 1900, 2700, 3100) | Crop only, lossless PNG |
| images/detail_facade_branches.png | 4 | 1500 × 1620 | (2350, 80, 3850, 1700) | Crop only, lossless PNG |

原JPEG含3136字节嵌入ICC色彩配置，描述为sRGB.icc，名称IEC 61966-2.1 Default RGB colour space - sRGB。三个PNG原样保留同一配置；未转换色彩空间、调色、改变对比、锐化、去噪、修复、去背景或生成内容。全图的窄黑边是摄影记录的一部分，非画内构图；全图保留左下签名与作品边缘。

The source JPEG contains a 3136-byte embedded ICC profile, described as sRGB.icc and named IEC 61966-2.1 Default RGB colour space - sRGB. All three PNGs retain the identical profile. No color conversion, adjustment, contrast change, sharpening, denoising, restoration, background removal, or generation has been applied. The narrow black surround belongs to the photographic record, not the depicted scene. The full image preserves the signature at lower left and the painted edges.

每语种文件中的alt与图注均已本地化。裁切旨在保留论证需要的相邻关系：近车与间隔、窗列与枝杈、远处汇聚。将局部单独使用时，仍应标为原作局部并保留来源信用。

Alt text and captions are localized in each essay. The crops retain neighboring forms needed for checking the argument: foreground vehicles and intervals, windows and branches, and distant convergence. When using a detail separately, identify it as a crop and retain the source credit.

机器可读坐标、字节大小、ICC与SHA-256校验值见[image_manifest.json](image_manifest.json)。文件完整性以[SHA256SUMS.txt](SHA256SUMS.txt)核验。

Machine-readable coordinates, file sizes, ICC information, and SHA-256 values are recorded in [image_manifest.json](image_manifest.json). Use [SHA256SUMS.txt](SHA256SUMS.txt) to check file integrity.
