# 静态检查报告 · Static QA report

检查日期：2026年10月19日。状态：八语独立全文审读及静态检查通过；未进行浏览器渲染验收。All eight editions have passed independent full-text review and static checks; browser-rendered layout QA has not been performed.

## 文件与结构检查

| 语言 | Markdown UTF-8字节 | 古文汉字数 | 正文图片 | 主章节 | 静态结构 |
|---|---:|---:|---:|---:|---|
| zh-Hans | 14,597 | 151 | 4 | 5 | 通过 |
| zh-Hant | 14,597 | 151 | 4 | 5 | 通过 |
| en | 18,902 | 151 | 4 | 5 | 通过 |
| de | 19,666 | 151 | 4 | 5 | 通过 |
| fr | 20,545 | 151 | 4 | 5 | 通过 |
| es | 18,998 | 151 | 4 | 5 | 通过 |
| ja | 19,653 | 151 | 4 | 5 | 通过 |
| ko | 21,040 | 151 | 4 | 5 | 通过 |

每篇均有一段完整古文、四张有替代文字及来源图注的本地图片、五个主章节、一个默认折叠的校读说明和八语互链。六外语版保留完整中文引文，并附当地语言全文翻译。图序为局部1、局部2、局部3、全幅；并非五图模板。

自动检查包括每篇15项结构条件、所有HTML本地链接及锚点、四幅图像尺寸与SHA-256、来源图尺寸、占位符遗留、错误对象混入、图片可访问性和脚本缺席。各语言引文均为151字。简体中文与六外语中文引文逐字相同；繁体版已另作语义及常用字形校读。

All eight editions pass fifteen per-page structural checks, plus package-wide local-link, anchor, image-size and hash checks. Each has the full 151-character source passage, four illustrations, five main sections, one collapsed notes block and eight-language navigation. The six non-Chinese editions include complete translations rather than a story summary alone.

## 图证与人工自审

- 已实际查看整幅与三张最终局部图，核对所论“曰”“孔子”“观闻”“谦让”“明睿智”及邻列方向。
- 核对正文十列各十五字，另有末字“也”，共151字；题款不计入。
- 图1“子”属于“弟子”，图2“孔子”及图1左列“夫子”中的“子”才用先生、Master等释义；正文与图片说明已统一区分。
- 对象为故宫博物院《邓琰篆书荀子宥坐篇轴》；未借用白氏草堂六屏的馆藏、尺寸或1804年款。
- 本幅无年款，不将“早期”强定为某年或某个年龄。
- 简繁全文与六语译文已自读校核。可选附读已读完整散文，英文正式题名核为 Naming the Stars Does Not Finish the Sky。

The full image and three final details have been visually checked. The contextual meaning of 子 has been distinguished across the opening details. Source identity, dimensions and undated status follow the selected Palace Museum work. The optional ray essay was read in full. Independent review has now read all eight editions from title through sources, including every full translation, caption, character explanation and editorial note. It also inspected all four final images and the saved museum record and Chinese/English ray01 texts. Three local Korean wording issues were corrected: two renderings of 勇力振世 now use 뒤흔들다, and the explanation of self-conceit uses 자만심. No content blockers remain.

## 独立全文审读

八个Markdown均从标题读至最后一条来源，覆盖全文论证、151字原文及全译、四图图注、所论汉字位置与释义、SAE附读和对象／图像／权利边界。复核者另外逐张查看四图，读取本地保存的故宫藏品页主体及ray01中、英全文，未冒称本轮实时访问。图1“子”为“弟子”末字的六语修订已核实；图2“孔子”与图1左列“夫子”的敬称语义保留。韩语“勇力振世”两处改为自然的“뒤흔들다”，自恃释义“자부심”改为“자만심”，改后相关完整段落已重读。未按字数扩写，未要求补回无信息的防守句。

## 没有完成的检查

当前环境已知不能启动Chromium，本包未重试绕过，未生成或声称拥有桌面/手机渲染截图。CSS有窄屏、长文、图片最大宽度和打印规则，只能据静态代码确认其存在。未把静态链接检查当作视觉布局验收。

Chromium could not launch in this environment. No browser-rendered desktop or mobile screenshots have been produced, and browser layout QA is not claimed. Responsive and print rules have been inspected in the static CSS only.

## 权利与发布

仅制作本地文件。没有发布、上传Library或向馆方代申请许可。古书迹与现代摄影分别说明，未取得个案公开转载授权。详见[许可与署名](LICENSE_AND_CREDITS.html)。
