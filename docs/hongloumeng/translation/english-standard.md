# 《红楼梦》1–110回原创英文执行规范

Version: english-1-110-v0.9. Frozen scoped standards for chapters 36–40; chapters 1–35 are accepted. English acceptance of chapters 36–40 remains separate. Historical sections retain their as-of status. Original English composition, project continuity through chapter 110 and disabled publication remain unchanged.

## 1. 文件及权威顺序

- `source-v0.2/`：用户提供标准包七文件的逐字节存档，保留原始时间背景，包括当时“81回尚未开始”等陈述。该历史状态不代表今天尚无81–85译文。
- `provenance.json`：原ZIP及文件SHA-256、仓库基线、精确来源路径和本次核读范围。文件hash用于定位，不等于内容获得审定。
- `english-terms.json`：有限可执行词表。`inherited_project_rule` 是现有连续性表明确规则，`project_observed` 是实际项目文本实见，`pending` 无定稿译形。实见不是Hawkes原书重新核实，更不是作者逐项终签。
- `english-voices.json`：关系及场景相关的声口观察，不是固定人格模板。
- `baseline-audit.md`：实际81–85实例、差异及首批风险清单。

优先顺序：当前获确认的中文底本及后续明确订正；本项目最新明确决定；既有已发布项目用法及`data/originals/hongloumeng/translations/continuity.json`、`corrections.json`；有准确定位的参考译本先例；目标语自然表达。发现中文疑字只提查询，不能自行改义。1–80与81–110的作者与文本来源分别标识，不把前80说成Han Qin新作，也不把后30说成曹雪芹佚稿。

旧稿与现文冲突时，应读取生成器实际应用的corrections。received稿和其旧审读说明是历史记录，不覆盖当前明文订正；也不为统一而回写历史稿。声口、事件、称谓身份冲突不能用无上下文搜索替换解决。

## 2. 原创性与Hawkes兼容的边界

独立直接从中文译出。兼容的是可辨识的命名、文化对应以及高层文学要求：灵活叙述距离、自然人物对白、反语、停顿、诗文分层。不是复制某译者的句子，也不声称复刻个人文风。不主动摄入完整Hawkes译文，不借Minford后四十回的情节解释本项目。旧资料外链只是来源线索，本次没有重新核读外部原书。

v0.2仅6个英语种子人名，证据均为导读线索，不能据此冻结所有核心名。81–85已形成较丰富的项目基线，但它们也不能证明未出现的早期人物、神话专名、曲牌都已核定。对于缺项，保留候选和待核原因，不虚称“原版即如此”。普通新词可以依中文实义与既定命名原则设置`project_provisional`工作形式，登记首见源ID、理由和影响范围后用于draft，不必逐词停等作者。只有改变既有canon、实质改动中文含义或不同世界观方案才集中提问。新回中文若明确区分旧译曾合并的人物，保持原中文区分，例如媚人／秋纹、檀云／碧痕、紫绡／春燕；Winsome、Sandal、Purple Silk属于81回项目暂定，不是原版新核。

## 3. 名称与称谓

人名保留现有分词及连字符：Bao-yu、Dai-yu、Bao-chai、Xi-feng等；不是一律给所有两音节词加连字符，Jia Zheng、Jia Lian等沿项目实见。侍女义译不能泛化为全员义译。Grandmother Jia、Sunshine、Lotus Pavilion已有显式连续性决定，不能复活Lady Jia、Cai-ming、Lotus-scented Pavilion。

姓名、亲属关系、排行、主仆面称分层。Bao-yu叙述名与Master Bao面称并存；子向母说Mother，不机械用Lady Wang。Xi-feng／Mrs Lian／ma’am各自按场景。Your Ladyship为面称、Her Ladyship为他称；Her/Your Old Ladyship须核所指。姑娘、奶奶、姐姐、二爷不设全书唯一替换。84回扇子事件中的Second Master是贾琏，不是宝玉。

同名碰撞必检：Faithful鸳鸯／Parrot鹦鹉／Oriole莺儿；Silver玉钏／Jade翡翠／Emerald碧痕；Gem瑞珠／Jewel宝珠须在相关章另核证据。彩明Sunshine为男性。古文“他”按实际人物而非现代字面判断代词。

园林地名固定空间身份；House of Green Delights可语境简称Green Delights；Naiad's House、Sweet-rice Village、Amaryllis Eyot、Lotus Pavilion等不得重新逐字译名。人物Lotus不等于Lotus Pavilion。未覆盖地点不从汉字机械生成“已定名”。

## 4. 叙述、对白与人物

通常用自然的过去时文学英语。句法可拆合，信息顺序、否定、反问、传闻、转述层级不能改变。长段不能统统磨成短句，短促沉默也不能填成解释。保留笑、冷笑、叹、嗤笑、不答等差别，笑不默认真诚愉快。

可有说书人的轻度在场，如Now、Let us leave、Of this we need say no more；只在中文有转场/套语功能时使用。旁白不能新增动机、现代心理诊断或道德裁决。原文已写心理则应译出，不能误把“保留留白”执行为删去明写心理。

人物声口必须随年龄、关系、场合和情节阶段变化。早期宝玉不能直接套用81回离散后的声口，早期惜春也不能预写85回立场。长幼尊卑、亲昵与无奈必须可闻，而非人人仿古或人人现代聊天。粗口忠实控制强度，不软化84式原文明确辱骂，也不向普通争执添加粗鄙。

## 5. 礼俗、宗教、物质文化

secondary wife、lawful wife、properly wedded wife、concubine按中文实际身份区别；死契保留卖身文书性质，不当现代雇佣合同。“出去”不自动等于脱籍自由；哭诉和指控仍是说话者的主张。

银两、吊钱、里、斤、月份和时辰保留源文数量关系，不折成现代币值。农历月份不误作公历月份。具体时刻已有83回half past six的项目实例，可记作该处例外，不扩为全书自动换算政策。

佛道并列及神话人物不混为一种宗教；僧、道、仙、道人、修行、带发修行、出家、还愿均先按场景分类。85回带发修行并非已剃度，不自动称全体宗教女性为nun。警幻、太虚幻境、神瑛、绛珠及第五回宗教/寓言语汇已在首批增量表分项记录工作译形及证据限制，不把早期核心表的空格当作当前无人裁定。

器物类别、色泽、数量及材质有别则保留；月白现项目采用浅蓝，不改成白色；qin和qilin不可译为普通钢琴或西方独角兽。不能把近似物名当该件文物已鉴定结论。注释只解理解障碍，不解释隐含动机或提前揭谶。

## 6. 诗词、回目、回末

回目先保人物、动作、两半关系，再求对称。诗、曲、谜、谶、对联、祭文、书信分开标注，保完整行序与篇数。优先语义、意象和后文回收关键词；不为押韵添加情节或新意象，不预设全书统一韵式。82回“共／随”采用join／follow的同句位可替换关系，是语义机关，不可仅把两句译得大意相近。

1–5的好了歌、注解、册页判词、曲文及真／假、有／无、情等双关单独评审。姓名双关可短注，不用注释揭露未到时点的命运。不得用现成受保护英译填补诗词。

回末有悬念则保悬念，有“正是”及收束联则保联；没有不能补。81的you must read the next chapter与83–85的listen to the next chapter是同类功能的可允许变体，无须强制全文一个句模。81唱、笑、忽然怔住的次序不能改成统一悲调。

## 7. 格式与每五回质量门

英文可拆对白段，但每个源文稳定ID必须完整映射到一个或多个目标段；不得以视觉段数证明完整。章节回目、诗行、引用、回末同样需ID及类型。记录中文底本SHA、规范版本、术语增量与未决查询。

新稿默认采用英式拼写，与81–85的colour、favour、grey等一致。排版建议统一弯单引号外层、弯双引号内层及弯撇号，章节标签统一Chapter N；这是新稿编辑默认，旧81–85混用标点的批量修改应另走渲染检查，本文不修改旧正文。不得显示Markdown控制符如标题中的##。

每5回做一次累计回顾，而非只验最后一回：
1. 源文逐段对照：事件、施受、数量、时间、否定、指代、缺漏和新增信息。
2. 连续性：名称、称谓矩阵、年龄/身份时间线、伏笔、同物复现；检查新词与全已译库碰撞。
3. 英文连续通读：叙述距离、声口区别、日常笑谈、讽刺、沉默、韵文是否自然；对照81–85的具体观察，不以字数或词频替代文学判断。
4. 文件检查：稳定ID全集、顺序、无空译、诗行数、引号、标题、链接、语言及版本。机器通过不等于语义通过。
5. 回顾记录：实际校审者及范围、发现问题、修订理由、影响回次、是否需回溯。未经过母语人工终审不得标“母语出版级终签”。

阻断项：漏译、误认人物、称谓消除权力/亲属关系、说破隐语、数字/否定错误、诗词缺项、错误作者署名、冒认参考译本核定。一般润色项与阻断项分开，不用平均分抵消硬错误。

## 8. 源文疑点与损坏

底本已确认不意味着毫无疑字。为疑字、异文、残缺分别建立`source_issue`：章节、稳定源ID、原字串、问题类型、语境、采用取义、是否影响事实、未决状态。能依上下文理解且不改变事实者，可记录保守取义继续draft；需要补字或实质校正者集中请作者决定。不得为了流畅虚构缺失情节，不反向修改中文，不将机器检测零占位符说成零文本疑点。第36回“奴几”等保守保留词和第76回缺文边界，后续到达时须专门复核。首5回诗词/判词与后续照应专门检查，此后每批回查全部已译词表，而非只对本批。

## 9. 首批1–5编辑检查点

`english-batch-001-005.json`为有范围限制的增量表；优先依中文身份、故事阶段和语境匹配，不按英文显示串合并人物。`editorial_stable`表示本批编辑选择，不声称作者个人逐条批准；`project_provisional`可继续draft，不单独阻断接受，语义缺漏或未解决源损坏则另行阻断。旧基线词表的pending是历史覆盖缺口，有本批工作形式时应一并读取。

实际改变：曹雪芹拼写统一Cao Xueqin；正式官署名沿Board of Works／Board of Revenue，不新造Ministry专名；泛称“部”可按句意用board或ministry，不为机械一致改动已审句；普通府邸用Rong/Ning mansion；鹦哥用Ying-ge，避免与另一个Parrot混同；斗在第1回指定酒器语境不作容量单位。茶酒双关保留正文器物名，简短读者注解释中文声音对应，不添加角色死亡预言。名字的词义注不一律塞进旁白；只有原文讨论名字或双关机关需要时才用局部短释。

任何此后词表或声口修改均升版本或追加明确变更记录，列影响的源ID与章节；已完成审阅不能自动视为审核过新版。历史首批词表检查点曾将第5回两处源损坏另列；其后底本及英文修订须按对应源ID与当前校审记录核验，不能用术语稳定替代源文验收。

## 10. 第二批6–10及累计规则

本批增量见english-batch-006-010.json。新增形式只在所列中文身份、源ID及场景生效；不回写较早阶段的称名，不据后期身份给早期人物加称号。普通暂定术语不自动阻断接受，源文缺损、误认人物或内容缺漏仍独立处理。

### 已形成的标题与复现规则

1–80新译的标题采用三行：Chapter N，第一半回目（sentence case，以分号收尾），第二半回目（sentence case，末尾无句号）。这记录首1–5已经实施的编辑格式，不借机重排81–85既有页面。

明确同文的诗句、门联或铭文跨回再现，沿已核英文；若中文实有异文，逐处登记并按原文区别，不为统一而改源。第一回与第五回同文门联保持一致。第八回玉与金锁的铭文，保留正反面、两半分句和相应祝辞的呼应；人物说“八字”指中文原铭，不要求英文硬凑八字或八词。题签、物名与正文复诵分别保留，不能把图式文字漏作装饰。

### 人物身份与关系

香菱在第七回原文使用该名处沿Caltrop，前期英莲仍Ying-lian；后期秋菱/Lily须待中文更名发生才使用。鹦哥与紫鹃的各回显示名沿Ying-ge与Nightingale，人物连续性依据既有身份记录及侍奉关系，不凭鸟名相似合并。所读第三回拨婢与第八回送炉两段没有直接叙述改名过程，不能补一场改名；Parrot始终保留给另一个鹦鹉。

刘姥姥用Grannie Liu，乡语可朴实、机敏、有谚语节奏，不用不相关英语地域口音或错误语法制造低智形象。连宗、陪房、通房、家塾与义学保持其社会关系，不默译成现代婚姻/雇佣/学校制度。宝玉与秦钟在第九回主动改论兄弟朋友，是面称变化，不是血缘关系变化。人物骂语、指控和旁人疑言不升格为叙述事实，不增加原文未确定的身份标签。

### 传统医学与处方叙述

第七回冷香丸、第八回冷酒议论、第十回脉诊与处方均为小说中的人物言说或记载，不转成现代诊断、医疗建议或疗效认证。保留角色自己的确定/迟疑、养生观和相互分歧，不能以现代病名解释秦氏。张友士正文的学者/医理身份不因回目“太医”而擅加宫廷任职履历。

钱、分、两等药量与加工方法逐项校读，不换算成现代克数。药名有可靠普通对应时使用，不能凭相似字猜定现代物种、化学成分或处方用途。原方连写或疑字导致分项不明时提source_issue，不默修中文或补成可实际执行的现代处方。三分/二分等愈病估计应清楚属于先生的说法，不写成旁白认可的精确临床成功率。春分、雨水、白露、霜降、小雪等为节气，不当公历同名日期或一般天气字词。

### 读者注与修订回归

茶酒双关等读者注独立于角色对白；保留对中文声音/意象的简明提示，不加结局解释。接受稿的源ID、正文和注释绑定分别核验。新增规范会改变全局review snapshot，但不自动要求改译旧章：先记录真实normdiff与受影响源ID，检查旧已接受正文确实符合新规则，再由负责整合的编辑重绑审阅记录。不得仅替换hash来冒充复核，也不得把一次增量审查说成重新全文终审。


## 11. 第三批11–15及有限并行边界

新增词与场景细则见english-batch-011-015.json及声口增量。源文书写身份、叙述显示名、说话关系、所袭爵位分别记录。同音英文名字不自动合并中文人物。六位国公沿Duke of Rong／Ning构式：Duke of Zhen／Li／Qi／Zhi／Xiu／Shan；这是项目编辑选择，不是外部译本核定或唯一历史译法。祖爵与后代现袭的伯、子、男及将军职衔不得平铺成同一爵。

长铭旌须整句复验八组意义及修饰层级，不能拿词表串接充作定稿。gongren保命妇封号，享强寿保礼仪寿辞，不据历史品级反改源文、不推年龄或新死因。第13回灵牌、门牌、榜文与第14回铭旌各按本身全文处理。潢海铁网山保复合地名边界，不认作现代黄海或另定海岸、海岛。第14回宁府点卯的卯正二刻可沿第83回同事件half past six in the morning；逐句按叙述、引语和时序调整，不能推广成全部时辰换算。

第6回金心绿闪缎保守作satin shimmering gold and green，填漆茶盘作a small tea tray decorated with filled-in lacquer；这是已用的局部译形，不是纺织或漆器工艺史定论。颜色、闪色、织物、衬里、器形与加工门类分别保留，不用近似物名补出未证材料和制法。

下一批隔离草稿可在前批全部可译单元完成独立及累计审查、只余明确待裁源文问题时，经指定范围的编辑决定继续。v0.4当时的指定范围仅11–15。第16–20回的新增执行范围见下节，不能由此推定21回以后已经完成批次准备。尚待实质补订、无法忠实表达的前批单元仍保持空pending，不得授予accepted；已决定保留的明示缺文依下节另行处理，不等于未知字句已恢复；前批最终验收及网站release门禁不因隔离草稿推进而解除。新回可用独立draft文件译写和审读，不据此绕过canonical导入门禁或修改检查点使测试通过。

版本变化必须记录实际normdiff、既有已译单元的实际内容绑定和受影响源ID；内容未变的hash核验不是重新全文读审。经实际增量回归后才可由整合编辑迁移规范绑定，保留旧审阅来源及本轮增量审阅范围。不能把批次准备通过等同于新回完成，不能把四处sourceIssue降格成四个字已经译完。

第83回历史连续性订正：旧英文将“东府蓉大奶奶出殡”写成was buried over at the Ning mansion，已由订正层及当前页面改为the funeral procession for Master Rong’s wife left the Ning mansion。记录保留以防复活旧误；新回继续分别处理发引、寄灵与下葬。第13回停灵、第14回踏看寄灵处并出殡、第15回抵寺安灵，不能把抵寺提前。本项仅核实这一句的订正，不构成对第81–85回全部语义无误的声明。


## 12. 第四批16–20：题名层次、整篇诗文与文本缺口

v0.5本节及english-batch-016-020.json提供第16–20回的执行选择；该规范冻结本身不代表这五回英文已完成、已验收或已出版。正文后来的验收以canonical检查点为准。沿用旧核心表、三个旧批次表与既有声口；本批新增词形按中文身份、故事时点及具体源段生效。历史表中的待核格不覆盖已有明确的当前项目用法。

### 园林命名与诗句回收

第17回的提议、驳回、暂题与第18回的赐名是不同动作。曲径通幽处、杏花村、杏帘在望等不能预写成最终地名。杏帘在望先赐浣葛山庄，读诗后才改稻香村；Sweet-rice Village可在宝玉先提议该名时出现，但须保住提议身份。大观园沿Prospect Garden，蘅芜苑/院沿Allspice Court；潇湘馆、怡红院、藕香榭、紫菱洲分别沿Naiad’s House、House of Green Delights、Lotus Pavilion、Amaryllis Eyot。清芬/清芳及苑/院保各处源字，英语不得据近音新合人物或误建另一地点。

红香绿玉→怡红快绿与怡红院之名分层；绿玉春犹卷→绿蜡春犹卷在同一句位只换jade/wax，保留周围英文语词一致。钱珝引诗独立译出，19回芭蕉诗与20回绿蜡的回指连同核读，不提前把草稿中的jade改成wax。第17回蕉棠两植须保两种植物及红绿论证；文学草木名和人物对异草的猜辨不升级成现代物种鉴定。

### 整篇、题额与作者

第18回实际载十首完整诗、六十八正文诗行；题额、题名和署名另列，不能以连续排版组数冒充诗数。元春首诗无独立题名，不补题。臣宝玉谨题是署名而非诗行；杏帘在望是黛玉代作、宝玉呈稿，保叙事知情差别。不补惜春未载诗、仅提及的赋颂记正文或戏目唱词。十首的完整行序与17开篇四行、内嵌联句及19结尾联均见增量表；词表不是诗译的替代品。

16回护官符复引与4回不是完全同文：少了/缺少可沿同义英句，江南王须为Wangs of Jiangnan，不沿Wangs of Jinling，更不另造一位王。原话仍由赵嬷嬷说出。

### 官称、家庭关系与声音机关

Secretary of the Phoenix Splendour Palace是凤藻宫尚书的有范围文学职称，不是历史部院鉴定，亦不与Consort of Worthy Virtue合并。Honoured Lady Zhou与Noble Consort Wu区分贵人/贵妃；国舅老爷的夫妻戏称不证成真实兄妹关系。带发修行沿项目既用practising the religious life without taking the tonsure，不把未剃发改成已受戒。

万儿的命名对白以wan motif与Wan-er作最小语音连接。黛山、林子洞和香芋/香玉须完整保现编、反驳、鼠精领令、变形与揭底；揭底前保持taro，揭底后才jade，局部短释xiangyu，不新造永久昵称。湘云一场保二/爱、数数与爱/厄回敬，必要时短释er/ai/e，不移植无关英语地域口音或永久幼儿腔。亲不间疏、先不僭后的工作译随宝玉下一段的姑舅/两姨、先来/后来自释，但短注须承认格言字面方向与自释的张力；不暗校中文，不用注释吞掉双方“心”的回应。

### 已订正读法与保留的缺文

本批中文已采用此处蕉棠两植、说不尽帘卷虾须、是赐厨役；这三项不再当作等待改字的旧疑点。叶渚按现名作Leafy Islet，不补荇或柳；我一燥依脱披风的语境保热急义，不替人物诊断。

第19回hlm-c019-b0005两处缺文是底本明示的缺口。可译出全部存文，在原来的两个位置分别清楚标[text missing]并配简短文本说明；不补书房名、不补“无人”、不以戏剧停顿代替缺文。此处完整映射是对现存底本及其缺口的忠实呈现，绝非失传字句已经译出。历史疑点记录本身不必阻断可理解的其余存文，但整单元验收仍须确认两处缺口均明示、全部存文无漏、相关记录如实，并完成实际校读；本规范不自动赋予任何稿件accepted状态，也不改动源文。

6回箩柜沿该处实译flour-sifting chest，不臆造器械结构；6回一面问/容身、8回悄悄的及半碗碧粳粥按已订正文保动作关系与汤两碗/粥半碗的区别；10回虚而无神两处同作deficient and lacking vitality，保持医者的话语层级。补充见english-terms.json，历史冻结批次表不回写。旧疑点记录不是再次要求作者决定这些读法的理由。

每五回仍须源文对照、连续性及完整英文通读，并累计检查此前用名与回收关系。新增规范与已译内容的关系须写明真实语义差异及受影响源ID；只换版本号或hash不等于复验，准备材料通过不等于章节译稿通过。历史v0.5规范经实际规范审查及既有内容增量核对，冻结为正式执行检查点batch-016-020-editorial-r2-2026-11-11；增量审查记录为EN-V05-R2-DELTA-20261111，不宣称重新全文审阅751个已接受单元。规范冻结不等于第16–20回正文完成、验收或发布。


## 13. 第五批21–25：引文归属、人物改称与知情边界

本节及english-batch-021-025.json为第21–25回新增的有范围执行规范；本轮规范冻结为batch-021-025-editorial-r4-2026-11-11，不代表这五回英文已译出或通过审阅。旧四批增量表逐字节保留，旧核心术语、人物声口和已有场景字段不改。第1–110回继续使用同一连续性体系：以后每五回均累计回查此前实际译文及第81–85回已形成的项目用法；第86–110回不得另起命名体系。人名兼容、文化对应及文学要求不构成摄入或复制受保护英文译本的许可。

### 既有用法、别名与误命中

第23回会真记／西厢记是同一阅读事件中的不同中文称名，英文主显示名承接第82回回忆此事时的The Western Chamber；可在简短说明中保中文别名，不把它们造为两部书。点绛唇、文官、中庸、大学、蓬莱承接已核项目用法；中庸与第82回简称《庸》的对应须按该段实际读书语境说明，不反改中文或新造另一书。飞燕、武则天沿早已出现的历史人物译名；合德暂用He-de，不增源文未载的姓氏；杨贵妃与早期Tai-zhen为同一人的不同称号层，不误造两人。兴邑为本处地名，保源字，不凭近字改名或定位现代地点。

红玉／小红对应既有Crimson；原名在解释避讳的场景可保Hong-yu及red jade的最小词义连接，不另建新人物。茗烟／焙茗沿同一小厮Tealeaf，未叙改名过程便不补改名场面。芸香→蕙香→四儿保先后称名与改名施事；四儿五儿气话不引入柳五儿。秋爽斋承接Autumn Studio，缀锦楼与早期缀锦阁沿共有词根而保楼／阁字别，不凭近名裁定建筑必然相同或不同。

只在确为同一指称时复用词表。一时飞灾不是时飞，四颗珍珠不是侍女Pearl，正出汗不是嫡出身份，绮霰斋不是侍女Mackerel，周瑞家的不是男性周瑞。通灵宝玉不机械作Bao-yu，金笼鹦鹉、琥珀杯、诗中鸳鸯与花木香料不能按字串改成人名。檀云Sandal、碧痕Emerald、麝月Musk分别保身份；彩云与彩霞、绣凤人名与绣凤纹样亦不得合并。

### 整段引文、曲诗与谜语

第21回庄子原引、宝玉拟续与黛玉题诗分别保完整边界和作者。花、麝、钗、玉同时牵动字面意象和姓名，不能只留其中一层。保《庄子因》源字及书名问题，不为押韵改因作文，不把一种训释写成唯一事实。跨prose块的四句题诗仍须完整校对，不因布局标作prose而吞掉诗句。

第22回戏中寄生草与宝玉自作寄生草分别成篇；七句唱词虽嵌在prose中，也须逐句完整。原曲赤条条句和后文复诵须回收同句。宝玉六行偈、黛玉所续两句与宝钗转述的神秀、惠能两偈保作者层次、否定关系及反复词：同一立足境须在续偈中被否定，不能将两人立场译成同义。小说中的禅史叙述仍属宝钗，不用外部史料改写人物言说。

灯谜保谜面、物类提示、猜答、故意猜错及谁已知答案的先后。贾环本来不通的谜不修成漂亮新谜；荔枝／立枝音桥可作局部短释，不增加原谜句。宝钗八行谜在本底本未明载谜底，不提前添加；贾政的不祥联想属于贾政，不升格为旁白预告结局。篇数不能由连续版式组数代替。

第23回四首即事诗各八正文行，共三十二行，题名、行序与宝玉署作关系分别保留。麝月／檀云两行的姓名和月镜、香云意象须同联复验。花气袭人知昼暖回收第3回已译的花气袭人片段，并译出新增的知昼暖，不能以旧片段替代整句。实际唱出的牡丹亭片段、黛玉心中复诵、回忆旧诗词及刚读过的西厢句分别标明，不合成一支舞台唱段，不补省略号后的未载曲文。

第25回四组各四行，共十六行，原文均无正式题名；审查标签不当原题。两篇肖像赞与和尚对玉的两段诗不合成一首。引语跨诗行延续到下一prose块的闭引号，须保住前后对白。第24回无收束诗便不补诗，第23回末悬念不能提前揭开，第24回末尚未明说的梦须到第25回明示时才揭示。

### 身份、关系、钱物与话语责任

多官／多浑虫为同一男性，多姑娘儿是其妻的称号；性关系、威胁、拒绝与猜疑须按实际叙述表达，不净化明确内容，也不添未载行为或把拒绝改成同意。贾芸与宝玉的叔侄及认儿玩笑涉及宗族辈分，不据年龄改为真实父子。红玉的避讳、接近主人的愿望、受责与情动分层；未具名的出场处不提前抖出身世。人物财产判断、恋爱指控、药效和宗教功德宣传仍归原说话人。

马道婆为寄名干娘及民间宗教从业者，不自动认证为受戒尼僧。符水、端公、巫婆、跳神与僧道各别，不改成现代诊断、疗法或实际操作建议。五鬼仪式的两纸人及每人五鬼、每样香料四两、欠银与报酬、购茶和回礼数量分别校对；阴人禁忌及妻母例外保为角色命令。和尚对掌中玉所说的十三载不强算宝玉年龄，不提前把石、玉、神瑛与人间人物各层合一。

### 当前底本与质量门

hlm-c024-b0034现底本为恰值焙茗走来；此处只按已订正中文译写。对应English alignment issue仍须等完整英文翻译和实际审阅后才能关闭，中文改字已完成不等于英文验收。可理解的古字、俗语、引号错向和底本未载谜底分别登记，不能顺手校中文、补剧情或把普通省略号当已证缺文。章节标题、prose内嵌诗曲和回末均属于稳定源ID覆盖范围。

前四批检查点已经接受，因而第21–25回可以推进；第26回继续受第五检查点约束。英文发布门始终关闭。新规范必须先经真实语义差异阅读及所涉旧译的针对性回归，再单独核对冻结状态的最终字节，才能迁移既有审阅绑定。既有1,056单元的正文、sourceHash、状态、3,168个review的contentHash和原reference、四个corpusHash、五条译注及十四项source issue保持不变；不得仅换hash冒充重读。第11–15回的474条保存审阅同步新绑定时，须保留历史provenance并追加本次实际增量审阅的中立引用，不重写原审阅内容。本轮实际规范增量审阅记录为EN-V06-R4-DELTA-20261111；既有审阅保留原始证据，仅更新规范绑定并追加该中立引用。此项不是重新全文审阅1,056单元，不声称任何新增英文已接受。


## 14. 第六批26–30：有范围规范与完整场景执行

本节及english-batch-026-030.json为v0.7有范围执行规范，本轮冻结标识为batch-026-030-editorial-r3-2026-11-11。第1–25回的五份批次表、既有核心术语和声口字段完整保留。第26–30回的用名、声口、整篇诗曲、引文、角色归属、钱物数量、关系与物件流转，以新批次表中完整的当前范围和源文为准。source_ids是证据锚点，不能代替完整执行范围；历史规范证据不能把旧场景中的年龄、职务、关系、知情状态或态度搬入新场景。词面命中不是语义审读。

新批次表逐项保留经审阅的分类、译形、当前scope、来源片段、既有规范证据、复用指示与排除项；声口见english-voices.json的batch_026_030_details。新词与文学译法已作为本批有范围工作译形接受规范审读，不自动升格为全书核心规范。文学意象锚点不是完整诗句，最终英文须独立创作并在完整场景中检验。

本批所绑定中文底本共4,475单元，本批328单元，其中5个标题、224个prose块、97个verse块、2个couplet块。第28回红豆曲包含补入的一独立verse块；玉玦按所绑定中文身份处理。全部完整边界、重引、prose内嵌诗曲和实际排除项仍须审读，不由版式或字符串扫描替代。

规范冻结前，须核实已安装中文及源ID映射，取得实际规范增量审读和所涉旧译的针对性回归证据，再核验最终冻结字节。旧审阅保持原引用与内容hash，只有在真实增量审读后方可追加中立引用及更新当前规范绑定。不得声称重新全文审读1–25回。第11–15回历史canonicalIntegration和历史source provenance完整保留，新绑定另记。

第25回检查点仍已接受；已实际审读的规范语义及相符中文底本可用于隔离起稿；canonical导入及验收仍须冻结规范和当前审阅绑定全部就绪，并对最终冻结版本重新核对。第31回须待26–30回实际全文审读和第六累计检查点通过。规范冻结不接受任何新译稿，英文发布门始终关闭。

本轮实际规范增量及所涉旧译审读引用为EN-V07-PROJECTION-R3-V1-DELTA-20261111。原有英文正文和审阅内容hash保持不变，原引用完整保留；通过最终冻结字节复核后，当前规范绑定可追加真实增量引用。这不是重新全文审阅1–25回，不是第26–30回正文验收，也不开放英文发布。


## 15. 第七批31–35：误听、传言与物件复现

This section and english-batch-031-035.json contain the reviewed seventh-batch execution rules. Earlier six batch tables, core terms and voice fields remain unchanged. Source IDs are evidence anchors, not exhaustive scopes. Apply each rule to the complete scene, speaker, listener, object and exclusions. Chapters 1-110 continue to use one naming and continuity system.

### 用名与关系

佳蕙沿 Melilot，春纤沿 Chun-xian，琪官／蒋玉菡沿 Bijou／Jiang Yu-han，紫檀堡沿第81回实见的 Zitan Fort。佳蕙在31回拾破扇；次日匿名来报湘云到的人不能指作佳蕙。鹦哥在35回是鸟，不是第3回的侍女 Ying-ge，也不是后文的侍女 Parrot；鸳鸯在32回才子佳人玩物的例子中是鸟纹。蔷薇架不触发蔷字笔画机关，香坠儿不触发侍女 Zhui-er。

李宫裁／宫裁保 Li Gong-cai／Gong-cai 的字称层，与 Li Wan 为同一人。周瑞媳妇、吴新登媳妇和郑好时媳妇是三位女性，不能套丈夫身份。傅二爷家的主人为 Fu Shi，不是宝玉；傅秋芳此时二十三、未许人，宝玉尚未亲见。王太医沿 Doctor Wang；王济仁暂定 Wang Ji-ren，只由本场紧接叙事识别，不等同全书所有王姓医生。

二哥哥等按实际亲属关系取称，不把堂表亲的 Cousin 扩给探春称父系半兄宝玉。妈妈在宝钗向薛姨妈哭诉处为 Mother，不沿用妓院 madam。姨娘可为姨母或妾室；贾母向宝钗说你姨娘指王夫人，薛姨娘在35回指薛姨妈。晴雯讥刺袭人未挣上姑娘、黛玉叫嫂子、王夫人的待遇托付、宝钗暗示受菜须各保言语层，不补正式纳妾。

莺儿常名 Oriole；黄姓保 Huang，可局部解释 yellow；旧名金莺暂用 Golden Oriole。35回目完整名层候选为 Silver Bai 与 Golden Oriole Huang，须在编辑审查中核定英文标题的自然度，不反改普通姓名。金、玉单字不能覆盖姓名、金线、金麒麟等长表达。

### 知情、传言与时序

32回宝玉先当面对黛玉说放心；较长告白仍意指黛玉，却误向袭人说，直到随后才认出她。放心在32与34可用同一英语词根呼应，其他普通安慰不强制逐句相同。黛玉的喜、惊、叹、悲及送帕后的多层心理是原文明叙，不应以避免解释为由删除。

32回王夫人所说损物、宝钗的失足推测，以及33回贾环转述其母的强奸未遂、殴打指控，都不能取代30回实际场面。焙茗猜薛蟠告密并非事实；34回旁白明确说这一次不是他所为，不能漏掉纠错。宝玉梦见琪官被拿和金钏哭诉不是新增现实消息。34回王夫人看见房内无人，不是袭人屏退旁人。

33回贾环四顾、贾政以眼示意、小厮退后是三个施事阶段，不简化成贾环屏人。34回宝钗劝兄少惹事并保留是否他告密的疑问，不替她补道歉或旁白已经掌握的事实。贾母扬言回南京沿既有 Nanjing，不写成实际成行。王夫人吩咐请僧念经是安排，不补僧人到场或仪式完成。

35回5–9段回头补叙薛家早晨，10段接合2段黛玉所见母女入院，不能改成两次来访。薛蟠反复道歉、宝钗哭笑、玉钏怒色渐和及贾母席上逗笑都按本场表达，不套永久人格或把笑解释为完全原谅。

### 诗、戏与回收

34回三首帕上绝句共十二正文行、六个正文 verse 块；其二、其三另作序标，不计诗行。两块旧帕如何承载三首诗并未交代，不补分帕方案。保泪珠、鲛鮹、枕袖、彩线、湘江与竹痕的相互牵连，独立创作诗译，不从受保护英译取句。

首行眼空蓄泪泪空垂中的两个空都保徒然：蓄泪徒然，垂泪亦徒然；不能换成空眼睛，也不省去重复的徒劳感。

35回《西厢记》只引两句；白露为露水，不是节气。双文保 Shuang-wen，可最简说明它与既见 Ying-ying 的别名关系，不换成源文未载名字或续述戏剧情节。鸟复诵六句葬花诗，首尾两联与27回同文，另有一行春残变春尽。须在27回实际最终接受字节核定后复用五句，第三行保 spring wanes／spring ends 差异；现有两不知的 neither knowing of the other 是可辩护的选择，不宣称唯一正确或保尽歧义。

34回君子防不然与自有82回明示复引用同句 A gentleman guards against trouble before it comes.；31回几把扇子能值几何与自有84回回响用 How much could a few fans be worth?。只回收同义语句，不输入后文婚议、悲情或另一场扇子事件。

33回要紧／跳井保原有急语、近音误听与聋婆子的答话，可作局部 yaojin／tiaojing 说明，不另造改变事件的英文笑话。31回阴阳问答保完整推论、反问和主仆笑谑，不修成现代科学或哲学摘要。

### 钱物、工艺与保守读法

白日跌坏扇骨、晚间首把供撕、再夺麝月扇另撕是三段动作。晚间两把明确不同；白日跌扇和首把撕扇同异未明，不补三把总数。四枚戒指后包三枚不补未载交付；两麒麟不定雌雄或未来配偶。汗巾沿 sash，不与手帕混用；35回同色不证明就是28回交换的那件。

松花沿 pine-pollen green，石青沿 dark blue；葱绿沿自有81回 spring green，桃红在本场选该回 peach-pink，保留早译 peach-red 的可容颜色范围，不机械回写。络子先用于汗巾，后改议络玉；只打半截不等于玉络已成。七种花样名与最终所选攒心梅花分开，黑珠儿线保描述，不增材质、颗数或制法。荷叶汤保模印面食、荷香和好汤，不当作仅有荷叶的汤。

端阳虎符是系臂节令护符，不套调兵凭证。山羊血黎洞丸暂以完整源串的 Shanyangxue Lidong Pills 保留药名，断词、配方未证，不自行分为两药，也不认定后文匿名丸药相同。警他的好处取语境中的使对方惊动、留下印象；警通惊的证据不等于词典已证 admire 义。正裁疑间仍在思量如何处置，不是疑虑已解，不冒称固定旧词。现无已证实的本批中文损坏；公开转录同文不排除共承讹误。

气的范围分层：31回湘云阴阳论述可用 vital energy；32回黛玉回想医生所言气弱血亏承接已接受第10回医家用语 qi 和 deficient blood，可作 weak or deficient qi and deficient blood。后者不是怒气或普通心情，也不是经旁白认证的现代诊断。荷叶汤银模花样为 thirty or forty shapes，凤姐命做 ten or so bowls，保两处约数与吩咐层。

### 审查门

The actual chapter 26-30 cumulative checkpoint is accepted. Independent semantic review and targeted accepted-text alignment support these rules. Final-status review and the controlled installation contract authenticate the final frozen bytes and current review bindings. Chapter and cumulative review gates remain mandatory. Norm freeze does not accept new prose or enable English publication. These scoped delta reviews do not claim a full reread of all earlier English chapters.


## v0.9 supplement: chapters 36–40

This supplement and english-batch-036-040.json record frozen scoped standards. Chapter acceptance and publication remain separate.

## Source authority and readable repairs
A readable repair supported by a specified common Chinese edition must record the chosen text, original text, fixed source/version, exact stable ID and rationale; keep historical evidence and synchronise Simplified/Traditional text and bindings, then report the repair. This does not authorise guessing, modernising archaic language, back-translating English into Chinese, or silently selecting a materially different version without supporting evidence. Unsupported substantive variants or added content remain for author decision. The two chapter19 authored [text missing] positions remain unchanged.

The installed Chinese source at commit aadc6128e6e71615e2d785aabab104a7dec0bbb6 includes hlm-c038-b0060 几霜痕→几痕霜 and hlm-c040-b0011 倚树→桃杏树. No translated verse may bind itself to the unrepaired historical Chinese. 奴几、名攻利敌、一些山滴水、通用门 and铁锁练孤舟 are retained. Historical source records do not override the installed source or current acceptance status.

## Names, social status and knowledge
Aroma’s two taels and one string come from Lady Wang’s personal twenty-tael allowance. Comparable treatment is not a completed ceremony: the proposal to open her face and install her is refused. Bao-yu learns the arrangement at night. His gold/jade and wood/stone words are shouted in sleep and heard by Bao-chai after Dai-yu and Xiang-yun have left.

Use inherited narrative names and places. Literary bynames are new scoped choices. Preserve Tan-chun’s first proposal, Bao-yu’s discarded old name and two teasing alternatives, the later actual signatures, and the 湘→霞 revision performed by Bao-yu. English initials cannot replace the Chinese claim marks. The same display form can have a different type, such as Lotus Pavilion as Xi-chun’s byname; it must not merge person, residence and maid Lotus.

Ling-guan’s refusal is genuine. The bird is released and its cage broken; the doctor visit is proposed but stopped. Chapter30’s unrecognised girl and guessed poem become recognition and understanding only here.

## Literary execution
The inventory contains six begonia poems, twelve chrysanthemum poems and three crab poems, each eight Chinese lines, plus two two-line couplets, two letters, embedded quotations and twenty-five game replies. Metadata, signatures, poem lines and interrupted comments are separately bound. Untitled poems must not acquire inventory labels as source titles.

Translate verse directly and originally. Rhyme, allusion and recurring phrases must be considered together; counts and hashes do not assess literary quality. Preserve the full thematic movement and author’s distinct image choices. Do not turn a broad allusion into a spoiler or a biological identification. 38b0060 is rebound to the actual repaired reading; b0078 and b0112’s previously restored wording is protected.

For the domino game preserve the three tiles, their order and full-hand name, the aptness of replies, rhyme demand and actual penalties. The prose-embedded line at40b0068 counts. Quote-only b0055/b0060 must retain mapping without invented prose. The accepted23b63 Peony Pavilion line is a continuity candidate, not proof that40’s Heaven/rhyme mechanism already works in English. Reuse the complete accepted23 line with N08-tian; the final note and full game English still need review. No silent earlier-text rewriting.

## Voices and narrated truth
Letters, domestic banter, poems, criticism, storytelling and game answers need distinct registers. Grannie Liu can improvise and knowingly cooperate without a comic imported dialect. The narrator expressly marks her invented stories; the fire and paid inquiry are separate real actions, and Tealeaf’s discovered statue remains his report. Account figures, crab-price arithmetic, silver-testing claims and forecast expenses retain their speakers. Contradictions in counts or relative days are not silently repaired.

At breakfast keep the private cue, public performance, separate bodily laughter and later assent. This is not proof Liu knew every device in advance. Gauze is misidentified then corrected; proposed window cloth, garden painting, room ornaments and curtains are not already delivered.

## Material and literary execution

Xi-feng accepts gifts readily and delays reporting the vacancy. Use Gossamer drifts in the clear air for the incipit; rhinoceros-horn mounts with the separate baixi note; linked-pearl vases with both shape/decoration explanations; coarse Ding-ware; and tang-wood pleasure boats. Evidence and explicit interpretation limits are embedded in the batch file.

Use the complete accepted23b63 line at40b81 with the separate Heaven/tian note. Display actual Chinese claim marks, not invented English initials. Preserve wrist-ornament/autumn-fragrance imagery in Painting Chrysanthemums and align all25 comment echoes to the actual translated poems, distinguishing two compressed restatements. Use Chrysanthemum Dreams consistently. Furong bamboo mats is a limited inheritance from actual accepted28b130, not the same gift. Three cun and one cun are source measures, not English inches.

Independent semantic-delta review covered these scoped rules and 41 complete earlier Chinese-English units; a separate follow-up verified the corrected public evidence locators. The current bindings preserve original references and append this limited review scope, not a new full-corpus reread. Each chapter then requires bilingual, literary and consistency review and a cumulative five-chapter review. No English publication is enabled.
