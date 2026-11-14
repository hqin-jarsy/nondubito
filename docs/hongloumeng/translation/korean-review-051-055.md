# 韩译第51—55回复核记录

## 本次实际范围
- 已完整翻译并逐段对照自审：第51回88个正文区块，第52回54个正文区块，共142个区块。
- 第51回十首怀古绝句的十个题名与四十行诗文均逐行保留；第52回外国女子五言律诗八行均逐行保留。
- 第53—55回本次未翻译、未审阅、未修改，已交由主线程另行安排。本记录不是五回全部完成证明。
- 唯一底本为当前 classics/hongloumeng/ch051.html、ch052.html；译文为直接中文译韩，未用其他语言转译。
- 参照翻译标准、ko/ch031.html，以及originals/hongloumeng/ko/ch081—085.html现行译名语气。另核对前文뇌대、성성전写法。

## 全文自审
- 已把51回1—88、52回1—54逐段中韩对照检查叙事顺序、对话人物、人物称谓、衣料器物、药名、钱数、年龄、时辰和诗歌行次。
- 保留习人母病及临终消息、探病衣物安排、晴雯麝月夜间对话、两张药方区别和称银笑谈；保留平儿隐瞒虾须镯案的三层理由、坠儿受罚被逐及其母争辩、宝琴八岁与真真国女子十五岁的年龄、燕窝话头被赵姨娘打断、宝玉骑马礼数与晴雯补裘全部工序。
- 自审纠正：猩猩毡统一为성성전，不误认作猩猩毛；刻丝改为织入花纹的丝织物，不误写钢丝；八团天马皮褂区分团纹与天马皮；杨树改为백양나무；赖大统一뇌대；明确外国女子所写是她自己的诗，而非宝琴所作；纠正贾母担忧过慧的否定语气；獐、狍分别用고라니、노루；补明末段小牙刷为작은 칫솔。
- 主要译名保持희봉、보차、보옥、대옥、습인、평아、청문、사월、가모、왕부인、우씨、조 이낭。诗谜不额外揭谜，也不附加人物结局解读。
- 医疗内容仅忠实保留小说人物言论，不加入现代疗效判断。

## 结构与文件
- 保留源段落全部class与布局类，逐段data-kind和连续data-source-block；译出实际回目；可直接编辑HTML。
- 第51回下一回连接到已完成的韩文52回；52回下一回仍回退至中文53回，不虚列尚未完成的韩文入口。前回50仍使用已存在中文链接，后续整体接线由主线程负责。
- 本次仅写classics/hongloumeng/ko/ch051.html、ch052.html及本复核记录，不改中文、共享导航、索引、脚本或绑定文件。未commit、未push。

## 表达尺度
- 本两回未出现需要非露骨改写的未成年人具体性描写，未作安全性淡化或删节，也未插入占位。
- 夜间取暖、衣着、非性化西洋珐琅裸体人物图案等均按原文保留；辱骂及体罚保持叙事，不改写为同意或美化。
- 结构检查不等于独立文学终审；本次为译者全文对照自审，主线程仍可统一跨批专名和器物术语。

## 实际检查结果
- 最终运行 python3 scripts/check_hongloumeng_korean.py --through 52：中文及续作绑定校验通过，第1—52回结构和本地链接检查通过（其中本次负责51—52回，其他回仅随脚本检查，不冒称全文审阅）。
- git diff --check 对本次三文件通过。新文件也用脚本逐区块核验；无空段、占位或替换字符。
- 按当前检查器新增要求补齐本两回author、description和canonical元数据。

## Completed five-chapter batch

Chapters 53-55 are now complete: see korean-review-053-055.md for full translator source-by-source review of their145 blocks. Combined batch:287 blocks. The earlier partial-work statements above describe the51-52 translator scope, not remaining work. Coordinator independently sampled first/middle/final blocks in all five chapters and found no correction necessary. All five had full translator selfreview; this is not independent native-editor final review. No attenuation or placeholders in this batch.

Final integration: all3,100 blocks through55 pass source binding, order, kinds, metadata and local-link checks.43 discovery tests pass. Scoped search verified current; git diff --check passed. Missing reader navigation added without changing narrative. No push.
