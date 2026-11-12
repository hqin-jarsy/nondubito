# 《红楼梦》1–110回原创英文执行规范

Version: english-1-110-v0.10. Frozen scoped standards for chapters 41–45; chapters 1–40 are accepted. English acceptance of chapters 41–45 remains separate. Historical sections retain their as-of status. Original English composition, project continuity through chapter 110 and disabled publication remain unchanged.

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

The historical v0.9 source checkpoint at commit aadc6128e6e71615e2d785aabab104a7dec0bbb6 adopted hlm-c038-b0060 几霜痕→几痕霜 and hlm-c040-b0011 倚树→桃杏树. The author now explicitly chooses 几霜痕 for its imagery, superseding the earlier ch38 editorial preference while retaining 桃杏树 in ch40. The earlier preference favoured formal parallelism and the 陽 rhyme of 霜; it did not prove 几霜痕 damaged. Both readings occur in public transcriptions, with the same level-tone sequence but different rhyme groups (霜: 下平七陽; 痕: 上平十三元). Bind translation to the current author-selected source, without claiming a unique manuscript restoration. Historical decision records remain unchanged and the new override is recorded separately. 奴几、名攻利敌、一些山滴水、通用门 and铁锁练孤舟 are retained. Historical source records do not override the installed source or current acceptance status.

## Names, social status and knowledge
Aroma’s two taels and one string come from Lady Wang’s personal twenty-tael allowance. Comparable treatment is not a completed ceremony: the proposal to open her face and install her is refused. Bao-yu learns the arrangement at night. His gold/jade and wood/stone words are shouted in sleep and heard by Bao-chai after Dai-yu and Xiang-yun have left.

Use inherited narrative names and places. Literary bynames are new scoped choices. Preserve Tan-chun’s first proposal, Bao-yu’s discarded old name and two teasing alternatives, the later actual signatures, and the 湘→霞 revision performed by Bao-yu. English initials cannot replace the Chinese claim marks. The same display form can have a different type, such as Lotus Pavilion as Xi-chun’s byname; it must not merge person, residence and maid Lotus.

Ling-guan’s refusal is genuine. The bird is released and its cage broken; the doctor visit is proposed but stopped. Chapter30’s unrecognised girl and guessed poem become recognition and understanding only here.

## Literary execution
The inventory contains six begonia poems, twelve chrysanthemum poems and three crab poems, each eight Chinese lines, plus two two-line couplets, two letters, embedded quotations and twenty-five game replies. Metadata, signatures, poem lines and interrupted comments are separately bound. Untitled poems must not acquire inventory labels as source titles.

Translate verse directly and originally. Rhyme, allusion and recurring phrases must be considered together; counts and hashes do not assess literary quality. Preserve the full thematic movement and author’s distinct image choices. Do not turn a broad allusion into a spoiler or a biological identification. 38b0060 now follows the author-selected 几霜痕. The reviewed English a few traces of frost remains unchanged; its current source binding must follow that choice. The earlier 几痕霜 checkpoint is historical; b0078 and b0112’s previously restored wording is protected.

For the domino game preserve the three tiles, their order and full-hand name, the aptness of replies, rhyme demand and actual penalties. The prose-embedded line at40b0068 counts. Quote-only b0055/b0060 must retain mapping without invented prose. The accepted23b63 Peony Pavilion line is a continuity candidate, not proof that40’s Heaven/rhyme mechanism already works in English. Reuse the complete accepted23 line with N08-tian; the final note and full game English still need review. No silent earlier-text rewriting.

## Voices and narrated truth
Letters, domestic banter, poems, criticism, storytelling and game answers need distinct registers. Grannie Liu can improvise and knowingly cooperate without a comic imported dialect. The narrator expressly marks her invented stories; the fire and paid inquiry are separate real actions, and Tealeaf’s discovered statue remains his report. Account figures, crab-price arithmetic, silver-testing claims and forecast expenses retain their speakers. Contradictions in counts or relative days are not silently repaired.

At breakfast keep the private cue, public performance, separate bodily laughter and later assent. This is not proof Liu knew every device in advance. Gauze is misidentified then corrected; proposed window cloth, garden painting, room ornaments and curtains are not already delivered.

## Material and literary execution

Xi-feng accepts gifts readily and delays reporting the vacancy. Use Gossamer drifts in the clear air for the incipit; rhinoceros-horn mounts with the separate baixi note; linked-pearl vases with both shape/decoration explanations; coarse Ding-ware; and tang-wood pleasure boats. Evidence and explicit interpretation limits are embedded in the batch file.

Use the complete accepted23b63 line at40b81 with the separate Heaven/tian note. Display actual Chinese claim marks, not invented English initials. Preserve wrist-ornament/autumn-fragrance imagery in Painting Chrysanthemums and align all25 comment echoes to the actual translated poems, distinguishing two compressed restatements. Use Chrysanthemum Dreams consistently. Furong bamboo mats is a limited inheritance from actual accepted28b130, not the same gift. Three cun and one cun are source measures, not English inches.

Independent semantic-delta review covered these scoped rules and 41 complete earlier Chinese-English units; a separate follow-up verified the corrected public evidence locators. The current bindings preserve original references and append this limited review scope, not a new full-corpus reread. Each chapter then requires bilingual, literary and consistency review and a cumulative five-chapter review. No English publication is enabled.


## 当前人物命名覆盖：丰儿统一为 Felicity（2026-11-11）

丰儿（王熙凤的丫头）统一译作 **Felicity**，与本项目自有第85回现有英文保持一致。这一当前决定优先于 B02-056 的暂定 Feng-er 形式及其后续继承应用；旧条目、旧引文、旧草稿和旧审阅记录保留原样作为真实历史，不因现行用法变更而追改。

本覆盖按人物身份适用于第1–110回，只指在相关完整中英文上下文中核实为丰儿的此人，不指凤姐 Xi-feng、兴儿 Joker 或其他含 Feng 的姓名，不作字符串全局替换。自有第85回中 Patience 叫 Felicity 换热水的原文保持不变。

覆盖的既有规范定位共六处：english-batch-006-010.json#/entries/55（B02-056）、english-batch-011-015.json#/existing_form_reuse/32、english-batch-016-020.json#/inherited_applications/40、english-batch-021-025.json#/inherited_applications/68、english-batch-026-030.json#/inherited_applications/31、english-batch-036-040.json#/inheritedApplications/27。它们的历史对象及所引原形均原样保留；当前执行形式以本条为准。

既有已接受英文的修订仅限第7回 b0015/b0016、第14回 b0010、第20回 b0004/b0020、第24回 b0028、第25回 b0029、第29回 b0006 八个已逐完整双语单元复核的位置，共十次精确名称替换。旧正文、24条旧单元审阅和旧累计corpus须在认证前像中保留；新正文使用真正对应新内容的复验记录，不将旧内容hash改名冒充新审阅。其他1,877个既有接受单元正文不变。规范迁移和受影响五批的当前累计绑定另须真实、范围明确的复验，不声称全书或五批全文重读。

第40/41回的同名差异稿及第46回相关修订须在各自批次按真实源、规范、稿件与独审证据走正常门槛；本命名覆盖本身不接受这些章节，不放宽后续五回检查，也不限制未来已获审校的正常扩展或规范修订。英文部分发布继续禁用。


# v0.10 supplement: chapters 41–45

本节与 english-batch-041-045.json 记载第41–45回的有范围冻结规范，不替换旧章节、旧词表或旧人物声口。规范冻结与英文正文验收分别处理；最终状态字节及当前绑定仍须取得真实独审与技术核验。

## 连续性与叙事责任

沿既有项目用名与亲属、主仆称谓体系。省亲别墅沿 Villa for the Family Visit；栊翠庵沿 Green Bower Hermitage；六安茶、老君眉沿自有85回 Lu'an tea、Old Man's Eyebrows。词汇可继承，后期人物的知识、态度与情节不可提前搬入。蘅芜君沿 Lady of Allspice。42回目潇湘子与此前潇湘妃子原字不同，本批沿Naiad作为同人诗号的有范围延伸，不虚称与旧中文同字，也不混作地点Naiad's House。

大姐儿仍为女孩，42回命名巧哥儿暂作 Qiao-ge，不提前换巧姐。彩明/Sunshine为男性；45的彩哥儿用young Cai，未证同人也未证另一个新人物；彩霞/Cai-xia与彩云/Cai-yun不得因同一筹寿场景合并。茗烟、焙茗同为Tealeaf。王太医沿Doctor Wang，但不凭姓王等同王济仁，王君效是医生所说的叔祖。赖家祖母、儿媳、儿子、未具名孙子分别处理；周家儿子及44两位哨婢不补姓名。尤氏沿You-shi。

41回的成窑杯先经宝玉交给贾母房中小丫头，42回刘姥姥接过才完成赠予。妙玉不曾用这只杯，不等于没有别人用过；宝玉先得到她日用的绿玉斗，后用竹根大海，后者只倒约一杯茶。汲水洗地是提议与许可，正文未叙完成。

43回北静王爱妾之死是袭人的猜测及宝玉的遮掩，不是已确认消息。受祭者不提前命名；44回才明说当日为金钏生日，不能译成忌日。回目撮土为香照译，正文不补抓土动作。黛玉评戏不因此被写成知道宝玉私祭。

44回实听内容、凤姐猜测及她向贾母所说毒药谋害各守层次。平儿扶正只是鲍二妻的提议。伤害、威胁、逞醉、道歉、家内权力和压下诉讼均保留，不用现代诊断或公平调解的叙述替代。二百两葬费、分项入账与另给鲍二的私银分开。

## 器物、画材与钱数

稀见器名优先给可读英文，并用短注说明确有的不确定性。杏犀䀉保杏字；𤫫瓟斝保全三个铭字。器铭是小说中的铭文，不能据此认证文物年代、材质或收藏史。现代博物馆类比不证明小说器物的实物身份。老君眉不指定现代茶类或品种。

42回画材第一单26项，第二单18项，顺序、数量与单位不省；第一单13种笔共124支，第二单另有四支担笔，作dusting brushes。矾绢胶矾另计。铁锅、锅铲是黛玉的笑加，不列作宝钗已要求的器具。41–45的斤沿catty/catties，钱的重量qian与铜钱cash分开；不作现代重量或币值换算。青金用qingjin painting colour，大赤飞金用dachi gold leaf，各为two hundred packets。[《绘事琐言》卷四公开转录](https://www.shidianguji.com/book/CADAL02094550/chapter/1lb3e1mas9mw4)记过十张一帖的包装，可支持packets这一类别，但不能认证小说该批每包十片或改算二千叶。青金的蓝色画料与金叶词义并存，painting colour不认证矿物、金属或纯度。

42只议构图、请假与清单；45才取旧器、发现一半可用、另开补单、矾绢起稿。宝玉负责向外请教与帮忙，不被升格为教画先生。旧图所在由45凤姐更正为贾珍处。后来园图未完成的叙事不能预写成此处失败。

实地纱用solid-ground gauze，不按字面误作无纹素纱。一斗珠指卷毛如珠的羔羊皮，不附着到青绉绸花纹；绵纱袜子用stockings of spun yarn，纤维仍未定，不加fine、knitted或径译丝袜、棉袜，掐金也不擅限在袜口。皴搜取纹理笔法的保守意思；淘澄飞跌按颜料加工的上下文表达，不把旧词自动判坏或写成经验证可操作配方。紫茉莉种粉不是铅粉；玉簪花棒是盛粉花蕾，不是玉簪针。植物与香料不凭近字确定现代物种。

鸡瓜在菜谱末道用stir-fried chicken pieces，[汉典鸡瓜条](https://zdic.net/hans/鸡瓜)支持鸡肉类别，刀法及部位不硬定；不能漏去取出储菜后另加炒鸡肉的工序。灰条菜拼写huitiaocai，正文可用dried huitiaocai greens，不认证具体植物种。非离了按完整构图语境自然顺译，表达画者胸中先有山水布局，不改中文。45多两倍局部取twice what we get，作为凤姐旧口语中的二倍读法，不倒算他人月例；10加10、四五百、一二百均保留。43老公们用rich old fellows，[汉典老公条](https://zdic.net/hans/老公)所列多义不让译文认证宦官或丈夫身份。

## 诗文、口吻与私密知识

《秋窗风雨夕》拟题An Evening of Wind and Rain at the Autumn Window，保夕字；十个显示块、二十个七言句逐行保全。保十五处秋字的反复、绿色的梦、泪烛、短檠、罗衾、残漏、竹窗与离情，不为押韵增景或改意。残漏的语义导引保水钟／漏刻的声音，仍不是已接受诗句。《代别离》、拟《春江花月夜》之格和正式篇名分层；所读书中仅提及的篇文不补。焦叶译作withered leaves是解释，不是把源字改为枯叶或蕉叶。诗前后读书、来访、焚稿、灯笼、燕窝送达及最终难眠的完整散文不可略去。

41开头大倭瓜答句回收40已审原句，待40最终字节确认后沿用词句，仅调整引号边界。全部器铭、题额、拟画题、祝词、训孙话与prose内嵌引语均在文学清单中检查，不以verse块计数替代。

刘姥姥的乡语朴实而机敏，不用错语法装低智。妙玉的精细、好客、挑剔与不同笑意各随场景。宝钗既能严肃劝诫也能亲密取笑，其医论仍是人物话语。黛玉明写的自责、依赖感与羡意不删，也不升格为全书财产权定论。渔翁／渔婆的羞意只有黛玉意识到，宝玉没有领会。玻璃灯虽被建议由宝玉自持，实际交给小丫头，他扶其肩走。

## 每五回质量门

完整规范语义审查提出的修改落实后，仍须做真实增量复验、对所涉旧译的针对性回归与最终冻结字节核验，不能以版本号或hash替代读审。已有五回累计候选审查的结论只绑定当时的实际稿件；最终41回Felicity差异、当前中文与规范绑定仍须依各自真实证据复验。后续必须保留完整双语逐单元对照、连续英文通读和每五回累计审查门，回查既有接受正文、最终36–40及自有81–85。英文公开发布门不因此打开。

当前绑定的正式中文已安装三处有据修复：42回目雅谑、42画单顶细绢箩／粗绢箩、45诗爇。本增量不修改中文。非离了、皴搜、淘澄飞跌、竹梢焦叶、43奶奶过去及彩霞／彩云差别继续保留，不凭通顺需要再改源。


丰儿沿当前项目明确覆盖使用 Felicity，包括41b0002；旧表中的 Feng-er 原对象及历史审查保留，不作为现行形式，也不改凤姐 Xi-feng。

本规范仅携带累计候选审查最终选定的九条读者注。十九条早期拟注不自动全选；正文及注位的当前最终绑定仍须复验。本补充不接受41–45正文，不自动迁移旧审阅，也不启用英文发布。


## v0.11 supplement: chapters 46–50

This supplement is a scoped internal editorial checkpoint. The earlier standard and nine earlier batch files retain their historical text and review references. The current source and map bindings in english-batch-046-050.json include the separately reviewed chapter 2 author ending and chapters 46–55 source repairs. The two source-binding records and their authentic prior validation contexts remain unchanged. Normative readiness does not publish English or replace content-bound chapter and cumulative review gates.

### Original English and continuity

Translate complete Chinese directly into original literary English. Preserve the established names and material vocabulary used in the project's own chapters 81–85 and carry that discipline into 86–110, without importing later events, knowledge, relationships or tones. The 38 scoped terms and 12 voice records are contextual instructions, not global substitutions. Felicity remains the current name of Xi-feng's maid 丰儿; all six old Feng-er records remain historical, and Xi-feng is a different identity.

### Meaning, voice and sequence

Keep Faithful's withdrawal and silence as resistance. Xi-feng's shift from warning to ingratiating agreement is not sincere endorsement. Promised bridal grooming and acknowledged concubine status differ from prior intimacy. Preserve the exact escalation and coarse force of angry speech without inventing insults. The pox comparison concerns a historically auspicious eruption grade, not an examination champion or modern prognosis.

At cards, preserve the order of first draw, signalling and deliberate card transfer without importing modern mahjong rules. Xue Pan's assumption, cries about injury and Aunt Xue's cover story remain attributed claims. Patience's fan report does not certify Stony's death from chapter 84. Retain all 25 relationship, knowledge, chronology, object and cash guards: offers, forecasts, jokes, purchases and actual payments must not be conflated.

### Poetry, quoted language and riddles

Preserve the three moon poems' development and chapter boundary. Reuse straight/round, white/blue-green, remains/rises and lingering in their precise poem/commentary relations. Keep all 70 linked-poem lines with their actual speakers, interruptions and competitive actions. The inventory comprises 15 verse works, 146 displayed lines, three heading/author metadata blocks, 41 embedded expressions and a separate prose character riddle, not 15 lyric poems.

Retain the five chapter headings and actual short endings. Repeat the spoken and written first snow-poem line exactly. Preserve the seven-character quotation called five without repairing Chinese. Keep snow-drenched bamboo's figurative tipsiness and fragrance floating through immortal realms on the Crimson River raft as bounded readings, not certified unique interpretations. The phrase rain-cape and hat does not add straw as a material. The forms of address sisters and Fourth Sister do not identify an otherwise unspecified listener. Eight riddles are present; the final three remain unanswered. Do not supply absent poems or move explanations ahead of the characters' discoveries.

### Materials, quantities and evidence limits

Keep all 37 material descriptions and their limits, including facing, lining, colour, cut and Xiu-yan's lack of snow protection. 猩猩毡 is broadcloth; scarlet is used only where red is explicit, including no added scarlet to Bao-yu's cloak at hlm-c049-b0035. 银鼠 uses established historical ermine, without modern species identification. 盘金 uses couched gold, without invented stitch spacing or fibre ratios. Sand-fox fur is limited to the garment group discussed in chapter 51 and the project’s own chapter 81; it is not inserted into chapter 49. Other 毡, fabrics, dress names and uncertain milu retain their own contexts. In hlm-c050-b0172, the shortened 猩毡 is also broadcloth, while 大红 supplies scarlet without implying size or grandeur. The selected sentence is “Just then, from behind Bao-qin stepped someone in a scarlet broadcloth cloak.” Preserve the anonymous introduction until hlm-c050-b0173. This local decision does not change the red felt cloth in hlm-c047-b0007 or the scarlet felt curtain in hlm-c050-b0169.

Preserve sums, units, alternatives, approximate dates and counts without reconciling textual tensions into new facts. The four separately reviewed source repairs for this batch are 凤儿姐→凤姐儿, 湘涟道→湘莲道, the damaged Zhaojun-hood material→猩猩毡, and 拗垤→坳垤. They belong to the separately integrated source amendment and are not changes made by this supplement. Retain the other 27 scoped reading choices and do not add an outside opening sentence to chapter 50.

### Notes and review gates

Carry only the 18 selected exact reader-note texts and anchors in the batch file. No new notes, early riddle answers or age-repair note are selected. Historical full review and later limited deltas apply only to their recorded bytes and scope. The exact historical r3 public projection has its own independent semantic review. A separate current-binding review authenticates the final-state delta, exact current source and map, all 16 normative inputs, five final drafts and 18 selected notes. Scoped applicability to the unchanged accepted chapters 1–45 preserves their original review references and corpus hashes with the new review reference appended. Neither metadata nor candidate approval substitutes for actual reading evidence.

The exact r2 projection received a genuine full 402-unit independent bilingual reading and a CHANGES REQUIRED verdict. A later limited review read eight complete units and 40 English segments, including the changed chapter 50 r4 unit, and rechecked the 18 unchanged notes. That earlier binding combined 401 unchanged units with the actual chapter 50 changed-unit recheck. A subsequent limited review actually read complete before and after English with Chinese for chapter 48 blocks 23–25 and verified the use of catties in the deliberately impossible heavy-olive simile. The latest corpus binding preserves 400 units unchanged from the original full reading and uses actual limited reviews for the two changed units. Neither limited review is a second full reading. The independent r3 normative approval remains bound to its historical prospective snapshot; the current binding separately includes the chapter 2 author amendment without changing its accepted ending. No new full reading of chapters 1–50 is claimed.

Use catty or catties for numeric 斤 in the chapter 48 heavy-olive simile, retaining its approximate thousands and deliberate exaggeration without modern conversion. The selected chapter 48 r4 application changes only the mass-unit word and does not alter the poetic quotations or commentary.

In chapter 46, Xi-feng compares the dangerous approach to poking a straw up a tiger’s nostril. Her private calculation allows that Faithful might yet agree and weighs both outcomes. In chapter 48, Caltrop correctly assigns xian to shan but mistakes the invitation to rest for a suggested rhyme unsuitable for her han poem; do not make her rhyme classification itself wrong.


## v0.12 English translation guidance for chapters 51–55

This is the proposed scoped editorial checkpoint after the exact B10 final payload. It does not assert installation, bypass the independent current-binding receipt, or publish English. The companion english-batch-051-055.json supplies stable IDs, exact source and draft locators, complete inventories, voice guidance and five selected reader notes.

The exact prospective B10 predecessor has its genuine independent review. Earlier immutable normative objects remain in their original files. The current merged normative fingerprint is checked separately from historical prospective public approvals.

## Original English and continuity

Translate directly from the complete project Chinese. Use the project's own chapters 81–85 for established identities, voices and relevant objects, and continue this cumulative standard through chapters 86–110. Do not borrow external copyrighted English prose or import later events, status or knowledge. A shared material term does not prove that two passages describe the same object.

Read complete units in context. At each five-chapter checkpoint, review bilingual units and then continuous English, including names, address, voice, verse, objects, numbers and knowledge boundaries. After changes, reread the complete affected units and necessary context. A limited review does not become a new complete-corpus reading through a hash check.

## People, institutions and address

Distinguish people before choosing an address. Zhuan-er and Zhui-er are different maids. The unnamed woman reporting school business in hlm-c055-b0021 is not Mrs Zhu. Under the selected source proposal, Lou-shi is Jia Jun's mother, not Jia Lan's. Preserve both Tan-chun's formal parentage and Aunt Zhao's biological maternity.

Use Parfumée for 芳官 in hlm-c054-b0029, supported by the project's own chapter 81 paragraph 12. This carries the name only. Felicity remains the installed form for Xi-feng's maid 丰儿; historical Feng-er records are preserved.

Use Sacrificial Bureau of the Board of Rites for 礼部祠祭司 and Board of Rites for 礼部 in the adjoining report. Minister of War is a separate officeholder title. The Court of Imperial Entertainments is a separate institution.

## Voice, verse and performance

Keep Bao-yu's affection and naive judgement, Skybright's courage and cruelty, Musk's care and enforcement of rank, Patience's tact and service, and Xi-feng's wit and self-interest together. Tan-chun's measured questioning, anger and subsequent restraint belong to one continuous voice. Characters' social prejudices, medical beliefs and financial reports are not automatically the narrator's conclusions.

The ten historical poem-riddles retain ten titles and forty poetic lines without answers. The foreign girl's poem retains eight lines, its contrasts and Bao-qin's remembered attribution. Preserve three shrine couplets and their separate attributions. Do not invent unquoted poems, opera lyrics, calendars or inscriptions, or finish an interrupted story.

Distinguish whole plays, scenes, tunes and recollections. Eight scenes from The Eight Righteous Men does not mean its eighth scene. Preserve the actual 'just now' in hlm-c054-b0030 and the earlier performance in hlm-c053-b0055 rather than categorically denying an earlier performance. Keep the subsequent recollections separate. Retain the unresolved source 至 and the limited tiqin-and-pipe accompaniment without certifying a modern violin or importing another version's orchestration.

## Clothes, furnishings and illness

The coat shared by chapters 51 and 81 is lined with sand-fox fur. The separate coat in hlm-c052-b0035 is with sand-fox fur; no lining or edging is inferred. Use broadcloth for 猩猩毡, adding scarlet only when red is explicit. Ermine and couched gold follow scoped historical decisions, not modern species or manufacturing certificates. Keep outer material, padding, lining, colour, pattern, edging and recipient separate.

Preserve Hui embroidery becoming Hui patterns. Keep the sixteen screen panels separate from the flower-filled vases, and the several tables around Grandmother Jia's couch in their actual positions. Inner third gate does not mean three inner gates. Retain counter game in its earlier project sense and embroidered gauze rather than pierced gauze.

Medical terminology belongs to the period setting. Do not certify modern diseases, doses, ingredients or efficacy. Preserve Xi-feng's miscarriage, bleeding and lack of needed rest and care, and the explicit anticipation of her later recovery. Keep the management gap in the main house and Ripple's imagined nose covered in ashes in their received meanings.

## Money and quantities

Keep thirty-seven tribute rows and five extra gifts complete. Live chickens, ducks and geese are two hundred each; wind-dried chickens, ducks and geese are two hundred in all. Mixed-fineness gold and the ingot count do not establish pure-gold weight per ingot.

In hlm-c051-b0082, retain the five-tael ingot, the remaining piece of at least two taels, the balance-reading joke and the woman's taking the silver to deal with the matter. The surplus may be intended for her, but the text does not fix its final division or establish that the doctor receives the whole piece.

Preserve the twenty- and forty-tael ordinary funeral grants and the separate additions of sixty and twenty taels. Keep annual school expenditure distinct from monthly allowances; Jia Lan's monthly amount is not supplied. Each of three maids carries three covered tea bowls.

Retain 一万, the three-thousand-tael wedding estimate and the three-to-five-thousand-tael miscellaneous funeral estimate. These are Xi-feng's plans, not an audited balance sheet or proof of a Bao-yu–Dai-yu engagement. Private savings and household funds remain distinct.

## Bounded numerical-mass rule

For quantified mass in hlm-c025-b0012, hlm-c025-b0013 and hlm-c053-b0014, use catty after one or half a and catties for the plural quantities. Preserve Chinese quantities, names containing Jin or jin, idioms and all other wording. Do not convert to modern weights or extend this choice automatically to other contexts.

The eight chapter 53 tokens and eight quantity-table entries are represented in the exact reviewed draft. The two chapter 25 units are a separately bounded eight-token accepted-content amendment in this proposed payload, requiring fresh current-content review and a limited batch 21–25 delta. Old reviews remain bound only to their original bodies in the B10 historical context. Historical jin is not intrinsically wrong.

## Notes, evidence and remaining gates

Carry exactly five selected texts after complete segments: the zither bridges at hlm-c051-b0053, segment 0; the First xian rhyme group at hlm-c052-b0018, segment 5; Golden Flower at hlm-c054-b0011, segment 5; the child in motley at hlm-c054-b0024, segment 0; and the disputed uncle at hlm-c055-b0018, segment 0, after the full answer. Keep original selection proof separate from current draft proof. Do not expand notes, reveal riddles or add future knowledge.

Three other substantial note proposals remain deferred. The eighteen B10 selections and forty-three installed earlier notes remain unchanged. The historical complete 292-unit bilingual and continuous-English review is supplemented by the genuine later limited review of two changed units. This projection claims no new full 292-unit reading.

The exact historical public r2 delta has an independent review. This subsequent merged final state requires its own semantic current-binding and technical review, covering the current source and map including the chapter 2 author amendment, exact drafts and selected notes, the unchanged earlier bodies, and the separate chapter 25 delta. Actual installation additionally requires observed predecessor commits and exact before-images. No new full 292-unit or earlier-corpus reread is claimed. English publication remains disabled.


## v0.13 English translation guidance for chapters 56–60

### Scope and continuity

This supplement and english-batch-056-060.json extend the existing project in specific scenes and senses. Earlier chapters, terms, voices and historical evidence remain unchanged. Translate directly from the complete Chinese into original literary English. Use the project’s own chapters 81–85 for established names, diction and explicit recollections, and carry the same continuity into chapters 86–110 without importing later events or knowledge. Do not borrow protected external English prose.

Use Parfumée for 芳官, Swallow for 春燕, Mamma He for 何婆, Chan-jie for 蝉姐儿 and the other established names. Felicity remains Xi-feng’s maid 丰儿. Preserve the distinctions among Jia Bao-yu, the reported Zhen boy and the dream counterpart. Shared names, stage roles, respectful addresses and literal character matches do not decide identity. Apply household funds to money, household staff to people, and news to the inquiry after Bao-yu. The servant-origin contrast applies to the reported release plan, not to household custom, outside powder or family money.

### Source and narrative boundaries

The selected working source projects only three changes: 窃 before 尧舜 in chapter 56 block 8, 莽玉 in the chapter 57 title, and 玫瑰 in the chapter 60 title, retaining 引来. Keep the other recorded uncertainties and the author’s 修树 reading. Early breakfast and breakfast at chapter 58 block 10 remain meals, distinct from the noon and evening sacrifices. 奴几 retains the servant-status sense. Do not harmonize the wake, Qingming, mourning journey, illness or narrative backfill into a newly invented calendar.

Nightingale’s Suzhou story is a test. Bao-yu’s initial collapse differs from his later conscious pretence. At chapter 57 block 29 her recollection begins ‘Before the New Year I heard’; the engaged family is ‘Academician Mei’s family’. Preserve the actual Xue Ke–Xiu-yan engagement and distinguish Aunt Xue’s later Bao-yu–Dai-yu suggestion. Keep the pawn ticket’s public cover story separate from the private explanation. You-shi’s reported childbirth is an excuse, and Aunt Xue’s care for the girls is not an assumption of household management.

Swallow’s mother Mamma He, her maternal aunt Mamma Xia and her unnamed paternal aunt are three women. Mamma He is Parfumée’s godmother. Mamma Xia is Ou-guan’s godmother and Chan-jie’s maternal grandmother. Xiao-jiu is Swallow’s younger sister. Wu-er’s sick maternal cousin is not the unwanted suitor Qian Huai. The deceased imperial consort and the two consorts of the Prince of Beijing’s household are different people.

Both Swallow and Mamma He apologize to Oriole at Allspice Court, away from Bao-chai. Swallow enters alone only after returning to Bao-yu’s rooms. Preserve the silent exchange with Bao-yu and the private transfer of Rui-guan’s packet. Do not assign a separate concealment action to Oriole. Plans for release, offers of help, ordered punishments and hoped-for appointments are not completed events.

### Voices and literary form

Keep Tan-chun’s questioning, anger and restraint distinct from Bao-chai’s learned teasing and practical generosity. Patience’s tact, Aroma’s mediation, Musk’s authority and Skybright’s sharp or feigned interventions have different purposes. Oriole’s skill and joking, Swallow’s fear, the older women’s dependence on household income, Parfumée’s pride and Aunt Zhao’s status grievance retain their individual audiences and motives. Their claims do not become the narrator’s verdict.

All eight named former actresses are girls. Male and female stage roles explain the husband-and-wife language without changing their sex. Preserve Ou-guan’s love and grief without reducing it to ordinary friendship or imposing a modern identity label. Di-guan’s identity is disclosed through Parfumée’s private account. Bao-yu’s religious theory remains his message, and Ai-guan’s accusation remains partly inference.

Translate titles, embedded quotations, proverbs, reported documents and gift lists as carefully as displayed verse. Leave the Jizi quotation incomplete where the speaker withholds the next line. Repeat the apricot line in exactly the same original English, preserving leaves, shade, fruit and the children association. Keep the stage phoenix imagery, Oriole and Swallow’s bird-name play, the mock military language and the maid-name saying. Do not invent missing lyrics, letters, edicts or closing poems.

Reuse the exact core recalled in the author’s chapter 84: “There, I've settled another matter. I wonder how much I'll get in matchmaker's fees.” Also translate the preceding statement about meddling in other people’s affairs. Carry the Western gold mechanical boat and the dead-pearl and fish’s-eye images without importing later ownership, departures, mourning or marriage-card exchanges.

### Materials and quantities

Preserve every allowance, gift-list category, contribution, vacancy, assignment and approximation with its speaker and status. The first twelve bolts in chapter 56 cover two kinds of satin together. Chapter 57’s needlework gifts are of two kinds; the total number of individual pieces is unstated. This corrects the older summary’s misleading two-gift wording. Keep the three or four days of birthday activity separate. Do not reconcile twelve actresses, four or five departures and eight named assignments by altering the source.

Use catty or catties for quantified mass in its applicable sense; the two catties of cake are a future promise. Four or five hundred cash is the surplus Swallow reports after her placement, not a stated flower profit. Preserve two or three mirrors as approximate. Distinguish the large fitted mirror, the small portable mirrors and the display boat. Use the flower-patterned mirror root without claiming its outline or material.

Keep rose medicinal powder, jasmine powder, rose essence and fuling frost distinct. Preserve the approximately five-cun glass bottle, its red contents, the authorized gift and the subsequent sharing. The smaller bottle in chapter 34 is not silently resized or identified as the same object. A mistaken comparison with Western grape wine does not establish alcohol. Medical terms and claims remain historical character speech, not modern diagnoses, formulas or evidence of efficacy.

### Reader notes and review

Carry exactly three reader notes: the fruit and children association after chapter 58 block 15, segment 4; Gongye Chang after the complete internal utterance in chapter 58 block 17, segment 1; and the Mei-xiang saying after chapter 60 block 17, segment 1. These segment numbers are one-based; the companion file supplies zero-based anchors and exact text. The other three proposals are not selected. Do not add a Du Mu attribution, pregnancy prediction, spoiler or medical claim.

Continue complete bilingual review and continuous English reading at every five-chapter checkpoint, with targeted rereading after changes. A limited review remains limited. This isolated semantic projection neither installs source or norms nor accepts prose, migrates prior reviews or enables English publication. Actual current source and norm bindings require a separate verified step.


## Chapters 61–65 supplement

This proposed supplement covers chapters 61–65. It extends the installed v0.13 standard while preserving every earlier rule, term and voice object. It does not state that these chapters or their notes have been accepted or installed.

### How to use this supplement

Read this appendix together with the complete chapter and the scene, voice, relationship, quantity, material and literary records. The 38 scene records cover all 284 units, including the five titles. The glossary contains bounded choices, not automatic replacements. Use each entry's source anchors and exclusions; raw substring matches do not establish identity or sense.

Write natural, original English. Use Hawkes-compatible project naming, not borrowed Hawkes prose. Preserve the narrative's shifts between comedy, intimate conversation, administrative argument, lyric play and sexual exploitation. Avoid invented dialect, compressed shorthand, modern diagnoses and explanatory narration the Chinese does not supply.

### Inheritance and current authority

Current names include Parfumée, Felicity, Aroma, Skybright, Musk, Patience, Faithful, Caltrop, Nightingale and Oriole. Preserve established pinyin names and hyphenation. Jia Bin is already used for 贾㻞 in accepted 13.12 and 29.13; the new glyph restoration does not authorize Bian. New romanized forms that lack an earlier verified occurrence remain proposals, visibly marked in the glossary. Ordinary forms of address still depend on speaker and relationship. Joker names Jia Lian's page at 65.25–39, continuing the same identity in the project's own 84.39. Preserve Lady Xing and Xing Xiu-yan; the page's name is not a generic Xing replacement.

Use catty/catties for the bounded quantified weight sense of 斤, not a global replacement of every jin in the repository. Preserve historical silver, copper-cash, distance, volume and time units where their distinctions matter. Current institution forms are Board of Rites and Court of Imperial Entertainments.

### Chapters 61–62: responsibility, gifts and birthdays

Continue the gate scene from the end of chapter 60 rather than reintroducing its people. Mrs Liu's coarse sexual insults, domestic accounting and flattery belong to one forceful voice. Lotus embellishes a report. Chess orders destruction, but threats and orders must not become acts that never happened.

Keep the two gift chains separate. The rose essence given through Bao-yu, Aroma and Parfumée is not Lady Wang's stolen essence. The fuling frost comes through Wu-er's uncle's share and Mrs Liu. Wu-er wraps half the frost separately in paper for Parfumée; the quantity is not half of a packet. Patience's alternative Bao-yu provenance is a cover story. Cai-yun admits the theft; suspicion about Silver must not turn into her confession. Bao-yu's accepted blame and Patience's protection of Tan-chun are deliberate social choices.

Preserve overnight detention and its discomforts. The forty blows, disposal of Wu-er and later proposed torture remain unexecuted. Xi-feng's exhaustion and punitive reasoning coexist with Patience's tactical mercy. The later six-or-seven-month pregnancy statement must not be erased to harmonize it with chapter 55's unspecific miscarriage.

Four people share the birthday: Bao-yu, Bao-qin, Xiu-yan and Patience. Xiang-yun is not a fifth celebrant. Two additional tables for Patience lead to four final tables for the whole party. Aunt Xue is elsewhere. Daoist Zhang's gifts of four kinds and Xue Ke's four kinds do not establish exact counts of individual objects. Keep every food, vessel and transfer count separate, including the two fresh tea cups and Parfumée's delivered meal.

Translate the concealed-word game through its actual connecting words and quotations. Do not invent a missing explanation for 瓢/绿. Each composite drinking answer has five different kinds of source, not one continuous ancient poem. Preserve the duck-head/maid joke, the girls' objection, the plant-name pairings and the loquat/pipa echo. A small note may assist a necessary sound joke, but must not replace the actual objects.

The author explicitly confirms 汗巴 as the Beijing sound for 胡掰. Render the dismissal as talking nonsense or making things up while retaining the Chinese. The go scene is not chess; two eyes are secure, while 官着 remains a cautious working interpretation rather than a reconstructed board position.

### Chapter 63: private celebration and abrupt mourning

The eight named contributors provide two taels plus one tael two qian, a total of three taels two qian. The parenthesis 他们有假的不算 is best read as excluding staff on leave or absent from the pool. The dictionary supports 假 jià, and the arithmetic still includes all eight named contributors. Do not invent counterfeit coins, a named absentee or a ninth contributor. This is a strong working preference, not proof of an archetypal text.

Keep every flower lot complete: image, heading, verse, instruction, drinkers and reaction. There are eight lots and none for Bao-yu. The peony line must repeat identically when he repeats it. Preserve the actual lottery sequence and dice totals. Do not turn a lot's flattering prediction or the party's princess joke into certified future history. Under Musk's lot, everyone takes three mouthfuls in place of three cups. Hibiscus remains the working choice for Dai-yu's 芙蓉, not a uniquely demonstrated botanical identification.

Parfumée first begins one birthday line, then sings the complete quoted tune and continuation. The public Handan play establishes its dramatic speaker and addressee, but local wording controls. Adamantina's complete card and Bao-yu's complete reply require coherent threshold language. Xiu-yan's explanation also establishes a separate contrast between the outsider and the person in the world. Do not invent a meeting with Adamantina.

The actresses remain girls while wearing male costumes and receiving male names. Preserve the sequence Xiong-nu, Yelü Xiong-nu, Wild Ass, Wen-du-li-na and Glass without creating new people. Parfumée's Glass is not the actual maid Glass in the author's chapter 83. Bao-yu's ethnic, imperial and foreign-material claims remain his claims; neither endorse them nor sanitize the hierarchy and the captured-servant background. Preserve Parfumée's reply.

The festivities turn suddenly to Jia Jing's death. The death announcement's inflated register does not make him an emperor. Distinguish physicians' observations, Daoist explanations, You-shi's practical decisions, the official memorial and the imperial edict. Keep the edict's full quoted scope through 钦此. Neither a modern poisoning diagnosis nor a falsely precise modern conversion of 子初初刻十分 belongs in the narration.

### Chapters 64–65: withheld knowledge and coercive relationships

At 64.3, the funeral context favours a completed morning meal offering. The ordinary-breakfast interpretation used elsewhere is not a blanket rule for 供. This remains a reviewable contextual choice.

Dai-yu's private offering has no securely identified recipient. Snowgoose does not know, Bao-yu speculates and later evidence establishes only that an offering took place. Do not settle the question by invoking parents, the Five Beauties or later events.

The Five Beauties require five headings and twenty complete seven-character lines. Preserve each poem's argument against an expected judgment, not merely its tragic atmosphere. Historical and literary sources help identify Xiang Yu, Qing Bu/Ying Bu, Peng Yue, Shi Chong, Yang Su and Li Jing. They do not certify every legendary event. Bao-chai's subsequent four quoted lines remain complete and properly attributed.

You-shi's stepmother brought the two younger sisters from a previous marriage. Do not invent a shared biological mother or father. Jia Rong's kinship addresses follow the household relationship. At 64.43, 尤氏姐妹 means You Er-jie and You San-jie, not You-shi. At 65.5, 65.31 and 65.36 the repeated 尤氏 forms do not mean the absent You-shi; read the mother and younger daughter, You Er-jie, and the two sisters respectively.

The secret marriage, pressure on the earlier betrothed, harassment, sexual bargaining and obscene servant speech retain their force. Keep source assertions, implications, accusations and narrator judgments separate. Do not romanticize coercion or expand innuendo into a described act. You Er-jie's accommodating hope and You San-jie's combative demand for choice must remain distinct.

Bao Er's earlier wife died in chapter 44, but the current local text does not include the public composite edition's remarriage story. Do not import it. Bao Er and his wife are separately counted identities. The male page Xi-er is not the female Xi-er of chapter 35. Joker's account is partial, performative speech, not an authoritative family register. Later continuity may guard against overstatement but supplies no wording to insert early.

### Materials, quantities and uncertainty

Maintain the distinction between essence and medicinal frost; damask, satin, gauze and patchwork; huali wood and a named botanical species; gold-flecked glass and a person's nickname. The compressed 玉色红青酡绒三色缎子 phrase remains uncertain in segmentation. Do not assert that 酡绒 is a separate fabric or finish, substitute 驼绒, or replace the uncertainty with a definite colour claim. Translate what can be securely understood without inventing a modern textile specification.

Keep funeral debt, incoming gifts, money sent home, betrothal estimates, actual compensation, monthly support and private savings separate. Distinguish the elapsed 三日后 interval from lunar month-days 初二, 初三 and 初四; no month is supplied and these episodes cannot be forced into one month. Keep the approximate two months separate. 回籍 identifies removal of the coffin to the family's native place after the hundred days, not an unspecified return home. Historical remedy claims remain character beliefs rather than medical advice.

Retain the negative in 他也不是好意的. Retain 如胶授漆 and give it a natural contextual English sense without claiming a Chinese correction. Source sameness in a public transcription is evidence of a reading, not evidence of autograph authority, an OCR mechanism or a unique pronunciation.

### Notes and review

At 64.52, reading Er-jie as the person who sits beside the eastern partition is contextually defensible with moderate confidence, not a uniquely established parse. Keep the contrary possibility visible. The plums-and-sweat complaint and plant classifications remain colloquial or character-level claims, not objective physiology or taxonomy.

Use exactly three reader notes: the song's dramatic source and speaker after 63.17; a restrained tumi identification after the verse in 63.21; and the names behind the Five Beauties after Bao-chai's criticism in 64.37. Keep the selected texts and complete-segment anchors unchanged. Do not add the four declined notes, identify the private offering's recipient or reveal later plot.

Keep the chapter title's parallel halves divided by a semicolon. In Joker's complaint at 65.28, Lady Xing names Xi-feng's mother-in-law without turning his report into narrator fact. At each five-chapter checkpoint, read the complete bilingual text and then the continuous English; after narrow changes, reread complete affected contexts. Mechanical checks alone do not supply semantic approval.


## Chapters 66–70 supplement

### Scope, authority and method

This supplement extends the established chapters 1–65 standard with bounded guidance for chapters 66–70. Read it with the complete Chinese and the scene, relationship, voice, literary, quantity and material inventories. A glossary hit is not an identity verdict. This candidate does not assert installation or acceptance.

Compose original literary English directly from the Chinese. Continue the project's existing names and high-level register through 81–85 and the later 86–110 work without borrowing copyrighted third-party English sentences or importing later events. British spelling, natural dialogue, lightly audible storytelling, complete stable-ID mapping and separate verse treatment remain inherited defaults. Direct address follows relationship and audience rather than a fixed name substitution.

The chapter source has 224 complete units: five titles and 219 body units. Fourteen narrow reading repairs affect fifteen spans in each script and twelve units. Preserve the complete author-approved chapter 66 proposal-and-sword passage, the eleven prior author-selected repairs, the deliberate chapter 69 ending gap and all retained readings. Modern public Chinese transcriptions and dictionaries provide limited comparison, not proof of a unique manuscript or of how corruption arose. The modern chapter 67 comparison page deliberately adjusts travel and the ending; never import it wholesale.

Use current established names ahead of superseded forms. Joker is the existing English name of Jia Lian's page 兴儿. Chapter 53 and the project's own complete 84.39 support it, the latter twice in the same explicit inquiry about Er-jie and Doctor Hu. Autumn for 秋桐, Shan-jie and Hu Jun-rong / Doctor Hu are also established by complete author 84.39. Felicity, Parfumée, Bi-yue, Tong-xi, Kingfisher and Ebony keep their existing identities and spellings. Si-er was already introduced as 'Si-er, Number Four' in chapter 21; it is not a new naming error.

### Identity, kinship and status

You Er-jie, You San-jie, Old Mrs You and You-shi are four identities. Old Mrs You is You-shi's stepmother and the mother of the two younger sisters. Do not manufacture shared biological parentage. 尤氏 denotes Er-jie in 66.12, 68.9/11/14/15 and 69.27/39, but You-shi in the Ning-house confrontation and the other identified passages. The glossary records each occurrence. 姐姐, 妹子, 姨娘, 二爷 and 大奶奶 remain contextual addresses.

You San-jie's chosen husband is Liu Xiang-lian. 柳二郎 and 冷二郎 retain the Second-Liu epithet, not another man. In 66.13 his 姑娘 is his aunt, not a young woman he intends to marry. The birthday in 66.7 took place at the older maternal relative's home, with the mother bringing the girls; do not collapse that older relative into the mother then present. The men’s brotherly addresses and Xue Pan's sworn brotherhood do not establish biological kinship.

Joker's account of Bao-yu's schooling and future marriage is his partial, performative report. It neither abolishes earlier school attendance nor certifies a Bao-yu–Dai-yu engagement. You San-jie's counterexamples are her remembered observations. Preserve the nesting of Bao-yu's quoted words within hers.

In chapter 68 Xi-feng and Er-jie exchange ceremonious self-deprecation. 奴家 is a polite first-person form here, not a declaration of enslavement. Xi-feng offers sisterly equality while insisting that Patience is their maid. Secondary wife, concubine and lawful wife remain distinct. Jia Rong's 'son' and 'aunt' language is relational and tactical, not a change of parents. The dead mother Xi-feng invokes is not the living You-shi.

The current wife of Bao Er is not silently identified with the woman who died in chapter 44. No imported remarriage account is allowed. The male page Xi-er is distinct from chapter 35's maid. Old Mamma Zhu preserves the accepted name root for 祝; the recurring household role supports continuity, but a shared surname alone cannot establish a biography. 小燕 in 70.5 is a provisional contextual application of Swallow, based on the maid serving in Bao-yu's rooms; there is no narrated renaming. The identification remains provisional.

Parfumée's Xiong-nu and Wen-du-li-na are aliases of the same girl in 70.4, not new male servants. Preserve the 那/纳 source difference without rewriting Chinese. The temporary Glass in chapter 63 is not the actual maid Glass in author 83.10. The poetic cuckoos, swallows, orioles, mandarin ducks and butterflies are not automatically maids with bird names. 鸳鸯剑 and 鸳鸯锦 do not refer to Faithful.

### Chapters 66–67: trust, knowledge and conflicting accounts

The road meeting contains Xue Pan's report of the rescue, the sworn brotherhood and Jia Lian's proposal. Jia Lian conceals that San-jie chose Xiang-lian herself. Xiang-lian keeps his ordinary defensive sword and offers a different heirloom pair. Do not insert a transfer action from another edition into the approved passage.

The paired swords fit together, bear 鸳 and 鸯 separately and have dragon/kui ornament and jewels. Their clear blades are compared to autumn water. San-jie hides the female blade, offers the other blade with its scabbard in her left hand and kills herself with the right. Xiang-lian later uses the male blade to cut his hair. The jade hairpin broken earlier as an oath is not thereby the damaged hairpin in Er-jie's later chest.

Xiang-lian's contemptuous allegation about Ning mansion is his allegation. The aunt's earlier engagement is his stated reason for withdrawing, not independently narrated fact. Er-jie's claim that he did not force San-jie to die is her intervention, not a legal acquittal. Xiang-lian's late reverence and grief must coexist with his earlier suspicion. Preserve the narrator's elegiac couplet without converting it to clinical description.

At first the apparent new house, Xue servant and returning San-jie are presented as experienced. Reveal the ruined temple when the text does. Her account of Disenchantment, the register and spirits of love remains in that encounter. Keep the repeated 情 roots and the repudiation, not a renewed offer of marriage. The unnamed louse-catching Taoist is not identified as an earlier named figure. Buddhist tonsure imagery and the title's religious language coexist with this Taoist; do not force one religion on the episode.

In chapter 67 Bao-chai's 'not taking it to heart' is expressly narrated. Translate it, but do not turn it into a universal diagnosis of cruelty. Xue Pan's real grief and the partners' speculative explanation of Xiang-lian's disappearance retain their different authority. Bao-yu knows the cause of Dai-yu's homesickness and distracts her deliberately. Nightingale also knows, but avoids saying it directly.

The two trunks contain private purchases outside the trading accounts. Aunt Xue and Bao-chai distribute their shares through different servants. Dai-yu's portion is doubled. Aunt Zhao's claim of equal treatment is her impression. Oriole reports the recipients' thanks and the reward money she received; she does not return or surrender that money. Retain every listed toy and material without inventing a mechanism for the walking figure, sand lamp or drinking-game object.

Aroma's visit is narrative backfill. She advises breathable fruit bags but no implementation is narrated. Unripe fruit and the first offering to the seniors are separate reasons not to eat. Do not turn 上头 into an identified Buddhist altar. Her tactful arrival and withdrawal do not make her a witness to the subsequent interrogation.

Keep the chain of disclosure: two pages, overhearing maid, Patience, Xi-feng. Oriole and Crimson see indications of anger without knowing the secret's details. Joker strikes his own face; Wang-er is stopped from striking him. Retain the involuntary 'Second Mistress' and its correction. Xi-feng asks about betrothal, withdrawal, wedding, house and attendants, not a marriage document. The earlier chapter 64 withdrawal document remains separate background. Her invitation to tell Jia Lian is a threat in sarcastic form.

### Chapters 68–69: coercion, rhetoric and action

Xi-feng's long courteous speech is a performance. Preserve its sustained rhythm, repetitions, tears and the specific promises. Do not shorten it into a plot explanation. The narrator's explicit account of motives may be translated; do not add motives where the narrator withholds them.

Er-jie enters through the garden's back gate, stays temporarily with Li Wan and loses her own maids. Xi-feng assigns her own maid, later named Shan-jie, and orders the women to prevent escape. The subsequent mistreatment starts after three days, not necessarily on the third day. Food, hair oil, missed visits and threats carry the coercion.

The petition, coached testimony, bribed judgment, threats to Zhang Hua and the family's cover story remain distinct speech acts. The Censorate is a period institution, not a modern civil court. Preserve the four separately stated grounds: national mourning, family mourning, marrying secretly against parents' knowledge, and taking another wife while the first remains. Do not invent the full petition or statutory citations.

Xi-feng's claim to have stolen five hundred taels from Lady Wang is not an audited explanation of the actual separate three-hundred and two-hundred bribes. Her script that Er-jie's parents and sisters have all died is false cover, not new narrator information. Grandmother Jia's permission to consummate after a year does not undo the prior secret marriage.

Zhang Hua and his father leave with approximately a hundred in silver. Wang-er refuses in practice to execute the killing order and invents their deaths. Never narrate them as actually murdered. Autumn is granted as a concubine with a hundred taels and is seventeen. Xi-feng's intention to use her against Er-jie and later destroy her is a plan, not a completed second killing.

Preserve the distinction between flirtation/old acquaintance and sexual consummation in 69.18: the narrative says Jia Lian and Autumn had not previously consummated it. Keep the narrator's gendered moral judgments, the women's accusations, Xi-feng's feigned kindness and the cruel servants' conduct at their stated levels. Patience's secret food and money and Er-jie's defense of her are substantive actions, not decorative sympathy.

San-jie's severe moral indictment in Er-jie's dream is dream speech, including the incestuous animal comparison. Do not sanitize it or certify heavenly judgment. Er-jie refuses the proposed revenge. Her six months refer to living here; she separately says she is pregnant. Jia Lian separately reports three months without menstruation. Do not infer six months' gestation or reconcile it with other chronology.

Doctor Hu's diagnosis, sexual distraction, treatment, loss of the formed male foetus and flight follow the local narrative. Doctor Wang is absent on military service seeking favour. No bribe to Doctor Hu is stated in this source. The later author's investigation must not be imported as proof of one. Preserve period medical vocabulary, reported prognosis and divination as historical speech, not modern diagnostic truth or useful medical instructions. The prescription's ingredients and quantities are absent and stay absent.

The raw-gold death remains a tragic literary episode. Preserve the unknown weight, attribution of the belief and the narrated sequence without practical elaboration or a claim of physiological efficacy. Nobody is identified as the person who emptied the savings chest. The retained broken-hairpin reading has bounded support, with 拆 variants acknowledged.

Funeral plans change. Five days is rejected; Jia Lian chooses seven, proposes further rites and burial south the next year, and is then forbidden the family temple in chapter 70. The actual burial is near and above San-jie's grave, not in the same grave or necessarily at the originally planned temple. The diviner's reported death hour is not an eyewitness timestamp. Distinguish five sevens from five or seven days. The five-hundred-tael coffin boards are bought on credit; Patience's two hundred do not become payment of the entire bill. Preserve the skirt kept as a remembrance and the chapter 69 uncompleted 'As the saying goes' ending without supplying a couplet.

### Chapter 70: renewal, poetry and play

Do not kill Wu-er: the source says she fell ill. Preserve Cai-yun, not Cai-xia. Faithful's refusal and silence toward Bao-yu remain as written, even when the wider chronology seems awkward. Eight twenty-five-year-old pages need wives, but no complete pairing list is supplied. The two 'aunts' in Bi-yue's report are the Li-family girls in household kinship usage, not two concubines. Springtime play among the girls and Bao-yu must remain lively without sexual elaboration.

The Peach-blossom Society replaces the Begonia Society as a proposal and then an arrangement. Naiad, Lady of Allspice, Old Farmer of Sweet-rice Village, Guest beneath the Plantain and Old Friend of Rosy Clouds retain their person identities. Abbreviated bynames do not create people or locations. Bao-qin's teasing claim to the poem and Bao-yu's reference to the Allspice manner must keep their awkward local association; do not change Bao-qin into Bao-chai to resolve it.

The Song of Peach Blossom has thirty-four seven-character lines across seventeen display blocks. Preserve curtain inside/outside, person/flower, wind, tears, colour, flame-like brocade, pillow, basin and cuckoo, and the final empty moonlit trace. No new prophecy of a specific character's death belongs in a note. Bao-yu's recognition and concealed tears are narrated after he reads.

Bao-chai quotes three brief Du Fu passages to show variety of voice, not to endorse one unvarying emotional style. Translate all three independently from the exact novel text; do not substitute another collected-poem variant or provide unquoted lines. 一百韵 is a rejected proposal, not a missing composition.

The proposed second day of the third month conflicts with Tan-chun's birthday and shifts to the fifth. The father's letter says the middle of the sixth month, the family's response says the sixth or seventh, and the disaster relief assignment later delays him to winter's end. Preserve those layers and the initial/middle/late-spring wording without harmonizing a calendar. Reading lessons and calligraphy are separate. The girls can copy handwriting for Bao-yu but cannot learn his books for him. Dai-yu's apparently impatient suspension of the society is considerate camouflage, explicitly explained. Keep his real work and subsequent renewed idleness.

There are five complete willow-catkin lyrics, plus the earlier peach-blossom poem: six works, seventy-nine punctuation-defined verse lines, twenty-four displayed verse units. Xiang-yun writes before the lots are drawn. Five subsequent lots include Bao-yu's Butterfly Loves Flowers, which he erases and does not submit. His later completion of Tan-chun's Nan ke zi is one jointly authored work, not his assigned entry. Do not invent a sixth catkin lyric.

Keep each tune name distinct from the common subject. Ru meng ling repeats its short plea; Nan ke zi has separate four-line halves; Tang duo ling holds the drifting/poor-fated sound association, the question of who rejects or receives, and the indifferent east wind; Xi jiang yue retains Han garden/Sui embankment and north/south; Lin jiang xian turns weightlessness into ascent. These are characters' poems and judgments, not certified forecasts. Keep the interruption after Bao-chai's first two lines, and repeat the second line exactly when Xiang-yun praises it. Preserve 好风频借力, not a familiar alternative. Semantic units and poetic momentum outrank obligatory rhyme.

Track the kites individually. Bao-yu guesses that the butterfly belongs to Jiao-hong; Nightingale challenges that inference, and it goes to the gatekeeper to await a claimant. Dai-yu's beauty and Bao-yu's later beauty are different kites. The fish has already been released and the crab given to Jia Huan. After the failed beauty is sent for a bridle repair, Bao-yu takes another kite whose form is not supplied. Bao-qin has the red bat, Bao-chai seven linked geese and Tan-chun the soft-winged phoenix. The other phoenix and joy-character kite have unidentified owners.

Nightingale takes the small Western silver scissors from Snowgoose and cuts Dai-yu's line. Bao-yu cuts his own to accompany it. Tan-chun's intended cut is interrupted: three entangled lines subsequently snap. Keep deliberate release distinct from breakage, and the bad-luck/illness custom as the characters' belief. Do not translate the entanglement into a prophecy about Tan-chun's later marriage. The chapter returns quietly to Dai-yu resting.

### Review gates and later continuity

Use exactly the four selected reader notes: the fifth seven-day observance, Zhong and Wang as calligraphic models, the lyric patterns drawn by lot, and the absent closing couplet at chapter 69. Preserve their selected wording and exact English anchors. Do not add the four unselected notes or new ke/youzhu explanations.

After every chapter, review complete bilingual units and literary flow; after each five-chapter group, reread continuously and compare cumulatively with the established earlier chapters and the project's own 81–85. Preserve identity exclusions, the provisional 小燕 alias, verse boundaries, claims versus events and source choices. Hash checks prove identity of bytes, not literary or semantic correctness. At chapter 80, collect all repairs and retained variants for global Chinese review without claiming absolute freedom from error.


## Chapters 71–75 supplement

### Authority, continuity and readable English

This supplement extends the established translation standard to chapters 71–75. Its 46 scene records cover all 232 body units; five titles bring the source total to 237. Eleven earlier author-selected textual choices remain in force. Four additional narrow reading repairs are documented. No other source spelling, missing passage or ending is silently repaired.

Compose original, readable literary English directly from this Chinese. Hawkes-compatible means continuity of names and broad literary standards, not borrowing protected English sentences or imitating an individual translator. The project's own accepted bilingual excerpts and author-written 81–85 passages are the English comparators here. No third-party English was consulted. British spelling, natural past-tense narration, differentiated voices, unforced humour and unobtrusive storytelling remain the default. Preserve the full long speeches, their evasions, repeated appeals and changes of temperature. Do not replace them with plot summaries.

Read this supplement with the preceding chapters 1–70 guidance and the project’s own 81–85. Historical statements in earlier supplements remain historical. Technical checks and earlier reviews do not replace complete bilingual and continuous-English review of each new five-chapter group. Future 86–110 follows the same naming and evidence discipline. This document does not claim production installation or acceptance.

Use the glossary as a scoped guide, not a substitution dictionary. A surface count does not prove identity. Faithful, Patience, Aroma, Skybright, Nightingale, Chess, Scribe, Picture, Xiu-ju, Su-yun, Musk, Ripple, Amber and Felicity retain their established forms. Joker for 兴儿 and Autumn for 秋桐 remain protected even though neither occurs here. Do not revive Xing-er, Qiu-tong, Feng-er, Lady Jia for Grandmother Jia, Cai-ming for Sunshine or Lotus-scented Pavilion for Lotus Pavilion. None of these protections licenses alteration of historical evidence.

The most important new application is Parfumée's nickname. Complete 63.46–47 establishes the material phrase gold-flecked glass and the nickname Glass. In 73.8 and 74.1, Gold-flecked Glass names Parfumée, one girl; 73.9 Glass is the same girl. It is not the separate maid Glass attending Grandmother Jia in 59.2. In 71.33 glass is the material of a screen. Preserve the source's act of naming without replacing every nickname by Parfumée or inventing an extra maid. 待书 is Scribe in the present Tan-chun scenes; it does not require rewriting the Chinese to 侍书.

Kinship and rank must remain audible. Mrs Lian, Second Mistress, ma'am and Xi-feng do not function identically. Mother in a child's direct address is not automatically Lady Wang. 二爷 can refer to Jia Lian or Bao-yu; 大老爷 is Jia She, while 外头老爷 at 75.13 is Jia Zheng. You-shi is Jia Zhen's wife and Xi-chun's sister-in-law. Li氏 here is Li Wan. Lady Xing is Ying-chun's stepmother, not her biological mother; Ying-chun and Jia Lian share a father but not a mother. Married servants named through their husbands remain women. Wang-er's wife solicits the marriage in 72.23–26 and receives the festival money. Her husband is not the woman in that conversation.

### Chapter 71: ceremony, mischief and secrecy

Jia Zheng receives one month's leave, not retirement. Grandmother's eightieth birthday falls on the third of the eighth month. The banquets run from the twenty-eighth of the seventh month through the fifth of the eighth. Keep the ordered guest and host days; do not invent a Gregorian date or a nine-day calculation. The Ning and Rong houses separately entertain men and women. Rank, seating, standing attendants, curtains and the chain by which the playbill reaches You-shi all matter. Do not flatten these into a modern mixed party.

Keep the imperial gifts and Yuan-chun's gifts distinct, with their quantities and materials. Four bolts, four rings and five hundred taels belong to the first list; a gold Longevity figure, an aloeswood staff, a bead string, incense, two gold ingots, eight silver ingots, twelve bolts and four jade cups belong to the second. The five young women presented are Bao-chai, Bao-qin, Dai-yu, Tan-chun and Xiang-yun. Ying-chun's absence is part of Lady Xing's later resentment. The Princess of Beijing is not the Dowager Princess of Beijing. The Nan'an dowager and the male Prince of Nan'an are different people. The source's 国君 within the ceremonial list remains an unusual received reading; do not turn the gathering into a visit by sovereign heads of state or silently amend it to 郡君.

You-shi is hungry before the altercation and eats snacks at Green Delights. Her concern is unsecured gates and lamps with strangers about, not a punishment by starvation. The two women refuse the maid's request and use the division between the houses to insult her. The maid's retaliation, the nuns' conciliatory talk and Aroma's tact should sound different. Zhou Rui's wife uses the dispute to settle her own grievances: Xi-feng's order is to record the names and deal with the women after the festivities, whereas Zhou Rui's wife has them bound immediately. Do not make her intensified transmission Xi-feng's verbatim instruction.

The relay in 71.25–27 is exact: Mrs Lin instructs the two young daughters; one tells her elder sister and Mrs Fei; Mrs Fei petitions Lady Xing. There is no direct Mrs Lin–Mrs Fei conversation. The children are seven or eight. Mrs Fei's claim that her relation is seventy or eighty is speech in an interested appeal, not an independently checked age. Lady Xing's public plea is outwardly charitable but humiliates Xi-feng. Lady Wang orders the women released. Xi-feng answers courteously and later cries in private. Faithful learns the cause from Amber and Patience before explaining it to Grandmother. Grandmother's later defence does not mean she knew all this beforehand.

Sixteen donors sent screens: twelve large screens and four small kang screens. The Zhen family's large screen has twelve panels, with tapestry-work on red satin on one side and gold-painted Hundred Longevities on the other. The Wu family's screen is glass. Two screens are reserved to give away, not already given. A sheng of beans is picked over with a Buddha invocation for each bean and cooked for distribution the next day. No liturgical text is supplied; do not write one.

Grandmother insists the poorer visiting girls Xi-luan and Si-jie be treated like her own granddaughters. Their households and generation must not be converted into an invented close-sister relationship. Faithful's candid account of household resentment and Tan-chun's discontent coexist with Bao-yu's refusal to think beyond another day with his companions. His remarks about dying are his speech, not a narrator's forecast. Xi-luan's promise to keep him company is a child's embarrassed offer, not a betrothal.

At the chapter's close Faithful first thinks Chess is playing with another girl. Recognition of a male figure and the confidential question come later. Chess identifies him only as a cousin; Pan You-an's name is withheld until chapter 74. Preserve the threatening stakes of exposure and Faithful's promise, without adding a sexual act. The title balances deliberate ill will against an unwitting encounter. Its first 鸳鸯 is Faithful; the second evokes a pair of lovers and mandarin ducks. A concise title solution must carry that distinction, not two appearances of Faithful.

### Chapter 72: trust, illness, money and a coerced match

The retrospective explanation gives childhood promises, bribed gatekeepers and an interrupted first opportunity. 虽未成双 must not become consummation. The cousin's flight is reported; Chess's anger at abandonment and Faithful's inference about fear remain their own. Faithful offers secrecy, friendship and admonition, not judicial acquittal. The two separation sayings in 72.7 carry real sorrow. Preserve both, including the two duckweed lines, without importing the lovers' later fate from chapter 82.

Patience describes month-long menstrual bleeding and Xi-feng's refusal to acknowledge illness. Faithful's alarming term and her memory of her sister's death are imperfect personal medical knowledge. Do not supply a modern diagnosis, pregnancy or a recommended treatment. The medical report in chapter 74 remains period medicine, with only the named ingredients and no invented dosage.

The official matchmaker Mrs Zhu is 朱, not the earlier garden worker 祝. A Sun household seeks a marriage, but the bride is not named in this conversation. Do not identify her prematurely from later events. Jia Lian's oily courtesy to Faithful precedes his request. His inquiry about the Buddha's-hand ornament is an inventory dispute: it had already gone to Xi-feng and is upstairs. 油冻 is a stone/material designation with an oily translucence, not frozen food, fresh fruit, amber or authenticated jade.

Keep the financing layers separate. Jia Lian says birthday spending has exhausted several thousand taels; rent and land income arrive in the ninth month. He anticipates another two or three thousand for the Nan'an gift, the Double Ninth gift and weddings and funerals. He asks Faithful for a chest of Grandmother's gold and silver vessels to pawn for about a thousand, promising redemption within half a year. In chapter 72 this is still a request. Patience's proposed one or two hundred is for Xi-feng, not a fee to Faithful. Xi-feng's dowry defence and her figures about wealth are heated rhetoric, not a verified balance sheet. Her stated plan to mark Er-jie's first death anniversary remains 周年 despite chronological strain.

Wang-er's wife seeks Cai-xia for her seventeen-year-old son. Her claim that the girl has no objection is interested testimony. Cai-xia is not Cai-yun. The mother's eventual compliance is expressly against her own wishes, while Xi-feng later describes it as delighted agreement. Retain that contradiction. Lin Zhi-xiao warns that the son drinks and gambles; Jia Lian briefly proposes punishment but yields once Xi-feng says the match is arranged. Cai-xia sends her sister Xiao-xia to Aunt Zhao; Jia Huan's indifference must not become a reciprocal engagement. Jia Zheng's plan to give each boy a maid in a year or two is future intention; the conversation is interrupted before Aunt Zhao answers his question about Bao-yu.

Xi-feng orders the outside loans collected by year's end. Her one-or-two-dozen-tael household allowances, the three hundred from old copper and pewter, and the five hundred and sixty from a gold striking clock are separate reported sums. The dream's hundred bolts of brocade are not real inventory, and its unnamed lady is not automatically Yuan-chun. Eunuch Xia asks for two hundred now, while the previous twelve hundred remains unpaid. Two gold neck-rings are actually pawned for four hundred: one is filigree with pearls, the other kingfisher-feather work and gems. Half goes to the eunuch and half, through Wang-er's wife, to the Mid-Autumn arrangements. Eunuch Zhou's thousand and Jia Lian's wish for two or three million are further distinct statements. Preserve the coercive courtesy without inventing an explicit repayment guarantee by the narrator.

The report that Yu-cun has been demoted is unconfirmed, and Jia Lian asks for verification. Reducing staffs from eight to six and four to two is a proposal, not a completed dismissal list. The final noise is unexplained here. Chapter 73, not chapter 72, reveals the fallen window fastening.

### Chapter 73: fright, punishment and the gold phoenix

Xiao-que's warning follows the separate window incident. Her report is summarized by the source, not transcribed. Do not invent a full speech naming the subject as certain. Bao-yu panics about an examination. He can recite the Great Learning, the Doctrine of the Mean and both parts of the Analects with commentaries; the first Mencius is half uncertain, much of the second forgotten. The Book of Poetry is relatively familiar through his verse-making; his classical prose has been neglected, and he has only sampled passages of examination essays. Preserve these degrees, not a caricature of total illiteracy. 谷粱 refers to the Guliang Commentary but the Chinese spelling stays untouched.

Skybright's impatience with the sleepy little maids contrasts with Bao-yu's concern and Aroma's and Musk's practical insistence that he study. Gold-flecked Glass reports a figure jumping the wall. No intruder is found. Skybright seizes the chance to suggest feigned illness and invents the claim that Bao-yu and the others saw the figure. The narrator does not certify that claim. The repaired 73.9 names Skybright and Glass as the two who go for medicine. Grandmother's resulting investigation reaches real gambling without retroactively proving a burglar.

The three principal and eight lesser organizers are included within the total of more than twenty gamblers; do not add three plus eight plus twenty. Preserve stakes of thirty, fifty or three hundred strings of cash. Leaders receive forty strokes and expulsion; followers twenty strokes, three months' lost wages and reassignment to the privies. The main organizers include Mrs Lin's relation by marriage, the kitchen woman's sister and Ying-chun's wet-nurse. Grandmother refuses the girls' appeal because she wishes to make an example. Her fears about sex, reputation and unlocked gates are part of her stated reasoning, not neutral forensic findings.

Simpleton is a fourteen- or fifteen-year-old maid newly selected for rough work. Her several foolish-girl names identify one person; retain the distinction between a nickname and an insult. Translate the narrator's description without adding a modern diagnosis. She misunderstands the scent-bag's embrace as a fight. Preserve the limited description of its two faces; the words on the reverse are not supplied. Lady Xing frightens her into silence and hides the bag in her sleeve. The owner is not established. The object is not automatically either of the two scent-bags in Pan You-an's later letter.

Lady Xing's attack on Ying-chun rests on family rank and comparison with Tan-chun. Her attendant's praise of Ying-chun is a partisan intervention. Xiu-ju identifies the missing pearl-set filigree gold phoenix and challenges the wet-nurse's daughter-in-law, Wang Zhu-er's wife. The latter admits the pawn while trying to make redemption depend on intercession. Her claim of thirty taels spent is contested. The one tael diverted each month is for Xing Xiu-yan's mother, not Xiu-yan's own allowance; the girl's additional expenses are a separate burden. Do not certify a debt or invent a settlement.

Ying-chun retreats into the Treatise on Response and Retribution. Tan-chun sees a threat to all the sisters' dignity, secretly sends Scribe for Patience and speaks with pointed logic. Dai-yu's military analogy is her witty quotation, with its actual 守 and 脱 wording. Patience uses household etiquette to remove the woman and eventually gives her a deadline to redeem the phoenix. No recovery is narrated yet. Preserve Ying-chun's willingness to conceal what she can without promising to lie to the senior women. The chapter ends before naming the next arrival.

### Chapter 74: accusation, search and separation

Bao-yu arrives to seek help for the kitchen woman, whose alleged partnership with her sister is reported by enemies. Patience conceals the phoenix dispute from Xi-feng. Xi-feng's professed decision to stop managing everything is a response to exhaustion, not a permanent abandonment certified by the narrator.

The new pawn is two hundred taels for Lady Xing. Jia Lian's request to raise another two hundred is rejected. Do not join it to the earlier four-hundred-tael transaction, infer that the old neck-rings were redeemed, or invent a single continuous collateral ledger. Suspicion falls on Simpleton's mother as a possible leak, but the maids deny speaking and no culprit is established. Patience now reveals that Faithful had privately obtained Grandmother's consent to the vessel loan. This new explanation must not be narrated in advance in chapter 72. Xi-feng's anxiety about Faithful's sexual reputation is explicit; no actual illicit relation follows from it.

Lady Wang assumes the embroidered bag is Xi-feng's. Xi-feng kneels and gives five distinct arguments: inferior outside workmanship; the risk of carrying it among the girls; younger married servants; other young concubines; and possible maid–page exchanges. These are defences and hypotheses, not a solution. She guarantees Patience, proposes discreet inquiry and suggests dismissing troublesome older maids partly to save expense. Lady Wang objects to further reducing the girls' small staffs. The five dowry-servant households called in are Zhou Rui, Wu Xing, Zheng Hua, Lai Wang and Lai Xi, represented by their wives. Wu Xing is not silently corrected to Wu Xin-deng, nor Zheng Hua to Zheng Hao-shi.

Wang Shan-bao's wife resents the maids and denounces Skybright. Lady Wang supplies her own remembered resemblance to Dai-yu. The narrator's account of Lady Wang's unmasked anger is explicit and must be translated, but the accusations remain accusations. Skybright strategically understates her closeness to Bao-yu; do not treat her whole defence as documentary fact. Her disordered dress follows illness and sleep, while Lady Wang reads it as sexual display. Keep the painful disparity. Threats of dismissal are not an already completed expulsion.

The night searches begin only after Grandmother sleeps and the gates are locked. Xi-feng gives a cover explanation about stolen property. Skybright overturns her chest; nothing improper is found. Bao-chai's quarters are exempt because she is a guest. Nightingale's stored charms, sash attachment, two purses and fan case with its fan are Bao-yu's old things, not proof of a sexual offence. Preserve the inventory and Xi-feng's dismissal of suspicion.

Tan-chun has candles and doors ready. She offers her own possessions while refusing a separate search of her maids, forces an explicit acknowledgement of the search and invokes the Zhen confiscation. Reuse the accepted chapter 2 wording, ‘A hundred-footed creature does not fall stiff even when dead,’ for the same maxim; her new emphasis is destruction from within. Wang Shan-bao's wife lifts her clothing before Tan-chun slaps her. Tan-chun's subsequent challenge to search her body is fury at humiliation, not consent to the earlier handling. Preserve her willingness to answer to the senior women and the servants' evasive efforts to end the confrontation.

Li Wan is still ill. The comma in 74.38 separates that fact from the neighbouring quarters; no pronoun is amended in Chinese. Picture's chest holds some thirty or forty small gold and silver ingots, not thirty or forty taels, plus jade belt plaques and a bundle of boots and stockings. She says her brother stored his rewards with her to keep them from their drinking, gambling uncle and aunt. Xi-feng distinguishes lawful origin from unauthorized transmission and postpones verification. Xi-chun identifies Mamma Zhang as the likely intermediary; suspicion is not a completed investigation.

Chess's discovered shoes, stockings, love-knot ruyi and letter are a different case. The letter says she sent Pan You-an two scent-bags, while he sent her a string of scented beads. Preserve both directions and the distinction between items mentioned and items found. His name first appears in the signature. Mrs Wang Shan-bao is Chess's maternal grandmother; the aunt married into the Pan family is Chess's paternal aunt, not a daughter whose marriage would make the cousin surnamed Wang. The local awkward grandmother/cousin conversation should stay intact, not be rewritten into a different pedigree. Xi-feng reads the letter aloud; others had not been able to read it. Her laughter and the women's mockery target the accuser's hypocrisy. The guard set over Chess is to prevent self-harm, not evidence she has already attempted it.

Xi-feng's bleeding worsens and delays disposal of the cases. You-shi confirms that Picture's brother received the goods as rewards, but Xi-chun still refuses to keep her. Picture's plea to remain together is not free agreement to leave. You-shi's salt metaphor concerns lawful goods made illicit by their transmission, not stolen salt found in the chest. Xi-chun's self-protective moral maxims and You-shi's wounded sarcasm remain distinct. Do not import chapter 85's actions as the settled meaning of every present phrase. The received ending is only ‘Not knowing what followed’ in function; do not add the missing full storyteller formula.

### Chapter 75: daily dignity, gambling and Mid-Autumn

The Zhen household's confiscation is reported; the frightened visitors' business is still unknown. Do not state what their packages contain. You-shi diverts to Li Wan, uses Su-yun's cosmetics without offence and lets a maid hold the washing basin casually until rebuked. Silver Butterfly's scolding and You-shi's attack on empty appearances expose different attitudes to hierarchy. Bao-chai says she is going out because her mother is ill. Li Wan and You-shi exchange looks; Tan-chun comments sharply. Preserve suggestion without supplying a narrator-certified motive or permanent departure.

The dinner scene remains convivial despite shortage. Lady Wang's repaired dish is water-shield relish with pepper oil, a bounded food rendering, not a certified recipe. Jia She's two dishes are returned; Jia Zheng's chicken-marrow bamboo shoots are accepted. Grandmother sends red-rice gruel to Xi-feng, the shoots and air-cured civet to Dai-yu and Bao-yu, and meat to Jia Lan. Her permission for Faithful, Amber and Silver Butterfly to share the meal temporarily relaxes service rules. The shortfall is in particular fine rice, not the disappearance of all food. Preserve Lady Wang's explanation of droughts and floods and Faithful's dry humour.

You-shi's short carriage journey uses seven or eight boys and no draught animal. She sees four or five visiting carriages but does not know how many riders there are. The gambling narrative then looks back over three or four months: archery is the respectable cover, Jia Rong nominally hosts, and Jia She and Jia Zheng unwittingly send four boys to practise. Do not force this duration to fit a newly calculated calendar.

The attendants under fifteen and the two sixteen- or seventeen-year-old boy favourites serving wine are distinct groups. Render the historical sexual exploitation and the coarse speech plainly but without erotic elaboration. The boys' trained apologetic performance is not free affection for their patrons. Keep Xue Pan's reversals in gambling fortune, Xing De-quan's drunken grievance and the young guest's vulgar joke at their actual levels. Xing De-quan's claims about Lady Xing withholding family property are not audited facts. You-shi hears and comments from outside; her own coarse disgust should not be polished into genteel silence. No new sexual action is to be supplied.

The gambling night ends at the fourth watch. The private Ning feast on the fourteenth is another night, chosen because mourning prevents a proper festival on the fifteenth. Pei-feng plays the vertical bamboo flute and Wen-hua sings; no title or lyrics are given. The sigh, wind and apparent movement of shrine doors are heard or perceived; their cause remains unknown. Jia Zhen's inspection next morning finds no anomaly. Do not name a ghost or declare the whole episode imaginary.

At Rong the family worships the moon and climbs to the Green Crest Lodge. The round furniture embodies reunion while the empty half of the space makes absence felt. Preserve the seating: Grandmother central, Jia She/Zhen/Lian/Rong on one side and Jia Zheng/Bao-yu/Huan/Lan on the other; then Ying-chun, Tan-chun and Xi-chun join. Do not insert Dai-yu or Bao-chai into this group. The flower passed to the drum is an osmanthus sprig.

Jia Zheng's henpecked-husband joke is a performance for his mother, not a confession. Preserve its whole setup, foot-licking, sour wine-and-mooncake excuse, and Grandmother's answering joke about spirits. Jia She's acupuncture story turns the physical off-centre heart into parental partiality; Grandmother recognizes the sting and he tries to retreat. Do not turn either joke into practical medical advice.

Bao-yu is assigned autumn as his rhyme, forbidden the eight conventional words in their source order, and composes four lines which the source does not supply. Keep the ellipsis after the introduction. Jia Lan likewise presents a poem with an ellipsis and no recorded lines; his reward is unspecified. Bao-yu receives two Hainan fans. Jia Huan writes a quatrain, but no text or ellipsis is supplied, so add neither. Preserve the twofold 二难 joke: two distinguished brothers and two boys difficult to teach. Wen Fei-qing and Cao Tang remain literary comparisons, not reincarnation asserted by the narrator. Jia She's encouragement about an hereditary office is a boast, not an appointment or guaranteed inheritance. The men leave well into the second watch and the chapter closes without importing the next chapter's poems.

### Literary form, notes and review gates

Each title is exactly three lines: Chapter N; first half in sentence case ending in a semicolon; second half in sentence case with no final full stop. The first line itself has no semicolon. The ten source title clauses require independent title review, especially the Faithful/lovers wordplay, Xi-feng's proud concealment of illness, coercion by Wang-er's wife, Xi-chun's isolation and the title's omen language. Do not draft these titles by borrowing a published translation.

This batch has no displayed verse block, no supplied independent poem and no supplied song lyric. Its 34 literary records nevertheless require complete review. Two embedded verse-like proverbial pairs, at 72.7 and 74.51, retain both lines and their line break inside prose segments. Ordinary maxims and the full jokes remain prose. A segment's kind must match source.layout.kind: prose stays prose even with line breaks, and any actual couplet stays couplet. Do not weaken the pipeline or invent an exception to accommodate verse-like text.

The two source ellipses in 75.47–48 remain; the excluded editorial annotations do not return as narrative. Do not invent an ellipsis for Jia Huan or lyrics for Wen-hua. Same-source quotations reuse accepted project wording where exactly identical, while received variants such as 齿竭唇亡, 守如处女 and 雪窗荧火 remain distinguishable. Translate the novel's quoted wording, not a corrected external classical text.

Use exactly the selected notes explaining Parfumée’s Glass nickname and the absent feast poems, preserving their wording and exact English anchors. The other seven proposals remain unselected. Notes may not identify the scent-bag’s owner, disclose later deaths, turn accusations into truth or insert source criticism into the story. Review complete bilingual units and continuous English after each chapter and cumulatively after each five-chapter group. Technical identity checks are not literary or semantic approval.
