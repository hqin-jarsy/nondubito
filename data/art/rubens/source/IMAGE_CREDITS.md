# 图像来源与许可

R1文字更新说明：以下登记的是需从原图文包沿用的图片。本更新ZIP不含图片文件；图像字节、原图SHA和裁切范围未变。请合并到原同名目录并保留images。

Text-update R1: the images documented below must be retained from the original package. No image files are included in this update ZIP; original image bytes, hashes and crop bounds are unchanged.

## 作品

Peter Paul Rubens and Workshop／彼得·保罗·鲁本斯及工作室

Wolf and Fox Hunt／《猎狼与猎狐》，ca. 1616／约1616年。

布面油画，245.4×376.2厘米。The Metropolitan Museum of Art，New York；John Stewart Kennedy Fund，1910；藏品号10.73。

- 对象页：https://www.metmuseum.org/art/collection/search/437536
- API：https://collectionapi.metmuseum.org/public/collection/v1/objects/437536
- 原始图像：https://images.metmuseum.org/CRDImages/ep/original/DP-27136-001.jpg
- 权利状态：Public Domain；API的isPublicDomain=true
- 开放政策：https://www.metmuseum.org/hubs/open-access
- 许可：https://creativecommons.org/publicdomain/zero/1.0/

## 本包图片

### 图1 官方全图

文件：images/rubens_wolf_fox_hunt_full.jpg

4000×2672像素，3,602,471字节。JPEG按下载文件原样保存，没有重编码；黑色外缘、画边及左下数字均保留。

SHA-256：de30e3169b7dfaa7ce7c3be6d7bc335ea538dc9ea30bc63280e363c117895256

### 图2 左侧相遇

文件：images/detail_left_encounter.png

裁切坐标：(120, 430, 2070, 2470)，输出1950×2040像素。坐标以官方4000×2672图像左上角为原点，按left, top, right, bottom记录，右与下边界不包含在内。

保留迎面马体、从左伸入的长杆、狼口与刃的接触、狼爪旁红色流苏，以及下方相缠动物。局部没有保留左侧骑者完整头顶，不用于单独判断其肖像或完整姿态。

### 图3 右侧灰马

文件：images/detail_right_horse.png

裁切坐标：(1850, 100, 3900, 2490)，输出2050×2390像素。保留灰马头、弯颈、缰绳、抬起前腿、骑者转身及下方犬与狐狸，供读者核对亮面内部的方向关系。

## 处理方法

两张局部从官方JPEG解码后的RGB像素直接裁切，以无损PNG保存，没有缩放、插值、调色、锐化、修复、补绘或生成内容。原图的3136字节ICC配置逐字节嵌入两张PNG。局部输出像素与原图相应矩形的解码像素逐一比对一致；这不意味着JPEG本身原来没有有损压缩。

所有图均以The Metropolitan Museum of Art为图像来源，按CC0使用。各语正文含对应语言的替代文字与图注，另集中列于image_texts.json。完整尺寸、文件摘要、像素和ICC校验记录见image_manifest.json。

数字图像可支持本包的视觉描述，不能代替对原作材料、笔触作者、制作顺序或准确原始画幅的技术鉴定。
