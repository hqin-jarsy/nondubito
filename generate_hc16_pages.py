#!/usr/bin/env python3
"""
HC-16 Type Profile Page Generator
Generates 16 individual type pages + 1 index page for the Non Dubito HC-16 vulnerability profile system.
"""

import os
from pathlib import Path

# Type data with all 16 types
TYPES = {
  'DTAB': {
    'zh': '驱容专栖', 'en': 'Drive · Tolerant · Anchor · Base',
    'tagline': '往前冲，能忍，不挑路，扎得住。',
    'tagline_en': 'Always moving. Absorbs friction. Takes what\'s given. Stays put.',
    'dims': [
      ('驱', '求不得（高）：你的内在驱动力极强，目标受阻时会感到强烈的痛苦'),
      ('容', '不可忍（低）：你对基础层的侵蚀相对迟钝，能忍别人忍不了的'),
      ('专', '不可选（低）：你不太介意方向是谁定的，给你一条路就能冲'),
      ('栖', '不可逃（低）：你不焦虑退出通道，扎在一个地方很自然'),
    ],
    'dims_en': [
      ('D', 'Drive (High): Intense internal drive — blocked goals cause sharp pain'),
      ('T', 'Tolerant (Low): Less reactive to dignity violations — you absorb what others can\'t'),
      ('A', 'Anchor (Low): You don\'t need to choose the direction — give you a path and you\'ll run it'),
      ('B', 'Base (Low): No exit anxiety — settling into a place feels natural'),
    ],
    'pattern': '你永远有下一个目标，永远在往前走。"我很忙但很充实"是你最常说的话。你不太挑环境——给你一个方向你就能投入，给你一个位置你就能扎下来。你身边的人觉得你是"能扛事的人"。\n\n但你的"能扛"有一个隐藏成本：你的基础层报警系统是静音的。被工具化对待的时候你的反应是"忍一忍"，方向被限制的时候你的反应是"没关系"，退出通道被封堵的时候你的反应是"我在这里挺好的"。',
    'pattern_en': "You always have a next goal, always moving forward. 'I'm busy but fulfilled' is your most common refrain. You don't need to choose your environment — give you a direction and you commit, give you a position and you root.\n\nBut your 'can take it' has a hidden cost: your foundational alarm systems are on mute. When instrumentalized, your response is 'I'll manage.' Direction gets restricted: 'it's fine.' Exit gets sealed: 'I'm good here.'",
    'pitfall': '你最危险的处境不是失败——失败至少逼你停下来检查。你最危险的处境是"有意义的忙碌"。当工作有意义、目标在推进、成就在积累的时候，你的涌现层被喂得很饱，其他三个报警系统同时静音。你可以在一份"有意义的工作"中被系统性地透支十年而不自知。\n\n等你终于感受到痛苦的时候——因为长期积累的损害穿透了你的高阈值——爆发会极其猛烈。你会发现自己已经不知道"我是谁"了，只知道"我在做什么"。',
    'pitfall_en': "Your most dangerous state isn't failure — failure at least forces you to stop and check. It's 'meaningful busyness.' When work is meaningful, goals advancing, achievements accumulating — your drive layer is fully fed, and all three other alarm systems simultaneously mute.\n\nWhen you finally feel pain — long-accumulated damage breaching your high threshold — the explosion will be extreme. You'll find you no longer know 'who I am,' only 'what I do.'",
    'misunderstood': ['「他很坚强」→ 不是坚强，是基础层报警系统静音了', '「他很专注」→ 不是专注，是方向自由感被钝化了', '「他很忠诚」→ 不是忠诚，是退出焦虑被钝化了'],
    'misunderstood_en': ["'He's so resilient' → Not resilience — foundational alarm systems are muted", "'He's so focused' → Not focus — his sense of directional freedom has been dulled", "'He's so loyal' → Not loyalty — exit anxiety has been numbed"],
    'works_not': '「放松一下」「别那么拼」——这些话在涌现层里打转，根本碰不到你的基础层。你听了会说"好的"然后继续冲。',
    'works_not_en': "'Relax a little' / 'don't work so hard' — these orbit in the drive layer, never touching the foundation. You'll say 'okay' and keep running.",
    'works': '用你听得懂的语言翻译你听不到的信号。不是「你应该照顾自己」，而是「你继续这样下去，三年后你连冲的能力都没有了」。把基础层的需求翻译成涌现层的语言——这是唯一能穿透你感知屏障的方式。',
    'works_en': "Translate the signals you can't hear into language you can. Not 'you should take care of yourself' but 'if you keep this up, in three years you won't even have the capacity to run.' Convert foundational needs into drive-layer language — that's the only way through your perceptual barrier.",
  },
  'CTAB': {
    'zh': '泰容专栖', 'en': 'Composed · Tolerant · Anchor · Base',
    'tagline': '什么都行，哪儿都好。', 'tagline_en': 'Anything works. Anywhere is fine.',
    'dims': [('泰','求不得（低）：你的涌现层很安静，目标受阻时不太焦虑'),('容','不可忍（低）：你对基础层的侵蚀相对迟钝，能扛'),('专','不可选（低）：你不太介意方向是谁定的'),('栖','不可逃（低）：你不焦虑退出通道')],
    'dims_en': [('C','Composed (Low): Quiet drive layer — goal setbacks don\'t cause much anxiety'),('T','Tolerant (Low): Less reactive to violations — can absorb'),('A','Anchor (Low): Don\'t mind who sets the direction'),('B','Base (Low): No exit anxiety')],
    'pattern': '你给人的印象是随和、好相处、不折腾。你不急着赶路，不太计较方向，不焦虑退出，也不容易被基础层的侵蚀触发。你最常说的话可能是"都行""我没意见"。\n\n但这里有一个需要你自己诚实面对的问题：你的"都行"是因为你天性从容，还是因为你的四个报警系统都被长期校准到了静音？',
    'pattern_en': "You come across as easy-going, approachable, low-drama. Not rushing anywhere, don't care much about direction, no exit anxiety.\n\nBut there's a question you need to honestly face: Is your 'whatever' because you're genuinely easygoing — or because all four alarm systems have been calibrated to mute over time?",
    'pitfall': '如果你是天性从容型——你确实挺好的。你的风险是涌现层可能终身蛰伏，从来不问自己"我想要什么"。\n\n如果你是全面钝化型——你最大的风险是你不知道你有问题。所有报警系统同时静音，你在结构上可能已经被深度透支但主观上感觉"一切正常"。\n\n区分方法：问自己"我有没有过强烈的痛苦体验？"如果能回忆起来（只是不频繁），你可能是天性从容。如果连"那是什么感觉"都描述不出来，你可能需要认真想想。',
    'pitfall_en': "If you're naturally composed — you're genuinely okay. Your risk: the drive layer may remain dormant lifelong.\n\nIf you're fully-numbed — your biggest risk is not knowing you have a problem. All systems muted, you might be structurally depleted while feeling 'everything is normal.'\n\nDistinguishing test: 'Have I ever had intense pain — blocked goals, violated dignity, being trapped?' If yes (just infrequently), you may be naturally composed. If you can't even describe those feelings, think seriously.",
    'misunderstood': ['「他很好说话」→ 可能是好说话，也可能是报警系统静音了','「他很随和」→ 可能是真随和，也可能是从来没被催化过','「他没什么追求」→ 可能是不需要，也可能是不知道自己可以需要'],
    'misunderstood_en': ["'He's easy to get along with' → Maybe — or maybe alarm systems are muted","'He's so easygoing' → Could be genuine, or could be he's never been catalyzed","'He has no ambitions' → Could be he doesn't need them, or doesn't know he's allowed to"],
    'works_not': '所有温和的提醒都可能被你的系统过滤掉。',
    'works_not_en': 'All gentle reminders may get filtered out by your system.',
    'works': '异质经验。一次旅行，一段完全不同的关系，一个把你从原有环境中暂时拔出来的事件。不是为了"刺激"你，而是为了给你一个参照系——让你有机会发现"原来还有另一种活法"。',
    'works_en': "Heterogeneous experience. A trip, a completely different relationship, an event that temporarily pulls you out of your usual environment. Not to 'stimulate' you — but to give you a reference point, a chance to discover 'there's another way to live.'",
  },
  'DFAB': {
    'zh': '驱烈专栖', 'en': 'Drive · Fierce · Anchor · Base',
    'tagline': '有驱动力也有底线，专注且扎实。', 'tagline_en': 'Driven with hard limits. Focused and grounded.',
    'dims': [('驱','求不得（高）：内在驱动力强'),('烈','不可忍（高）：底线极硬，尊严被碰了立刻反应'),('专','不可选（低）：不太介意方向是给定的'),('栖','不可逃（低）：扎得住，不焦虑退出')],
    'dims_en': [('D','Drive (High): Strong internal drive'),('F','Fierce (High): Hard limits — dignity violations trigger immediate response'),('A','Anchor (Low): Fine with a given direction'),('B','Base (Low): Settled, no exit anxiety')],
    'pattern': '你是别人眼中"靠谱的人"。有驱动力又有底线，给你一个方向你就能冲，但不会为了目标践踏自己的原则。这种组合在任何环境中都被高度评价。\n\n但你的结构里藏着一个裂缝：驱和烈可能打架。当目标要求你越过底线时——你内部会撕裂。驱说"必须完成"，烈说"不能越线"。',
    'pattern_en': "You're the person others call 'reliable.' Driven and principled — give you a direction and you'll run it, but you won't cross your principles for the goal.\n\nBut there's a fault line in your structure: Drive and Dignity can conflict. When a goal requires crossing a line, you tear internally. Drive says 'must finish,' Dignity says 'can't cross the line.'",
    'pitfall': '忠诚陷阱。你对一个组织或关系高度忠诚（专+栖），同时你有底线（烈），但组织或关系逐渐偏移到你的底线之外。最终要么底线让步，要么某天突然爆发"我不干了"——所有人都震惊。',
    'pitfall_en': "The loyalty trap. You're deeply loyal (Anchor + Base), you have hard limits (Fierce), but the organization gradually drifts past your limits. Eventually either the limits give way, or one day you explode 'I'm done' — and everyone is shocked.",
    'misunderstood': ['「他很稳定」→ 稳定外表下可能是驱与烈的持续内战','「他没什么不满」→ 不是没有不满，是在底线被触及之前确实没有'],
    'misunderstood_en': ["'He's so stable' → A stable exterior may be the ongoing internal war between Drive and Dignity","'He has no complaints' → Not 'no complaints' — just hasn't been triggered until the line is crossed"],
    'works_not': '「放松」或「勇敢一点」。', 'works_not_en': "'Relax' or 'be braver.'",
    'works': '提前识别驱烈冲突的环境。在撕裂发生之前就看到"这个方向迟早逼我越线"，然后在还有余地的时候调整。你的修复是预防性的——一旦撕裂发生，修复成本极高。',
    'works_en': "Identify Drive-Dignity conflict environments in advance. See 'this direction will eventually force me across the line' before the tearing happens, and adjust while there's still room.",
  },
  'CFAB': {
    'zh': '泰烈专栖', 'en': 'Composed · Fierce · Anchor · Base',
    'tagline': '不急但底线硬，给定一条路就安稳守住。', 'tagline_en': 'Unhurried but hard-lined. Steady in a given path.',
    'dims': [('泰','求不得（低）：涌现层安静，不急'),('烈','不可忍（高）：底线极硬'),('专','不可选（低）：不挑方向'),('栖','不可逃（低）：扎得住')],
    'dims_en': [('C','Composed (Low): Quiet drive layer, unhurried'),('F','Fierce (High): Hard limits'),('A','Anchor (Low): Fine with a given direction'),('B','Base (Low): Settled')],
    'pattern': '你的核心关切不是"我要成为什么"，而是"我是否被当作一个人来对待"。你不急着赶路，不挑方向，扎得住——但你有一条极其清晰的底线。被工具化对待的时候，反应迅速且坚决。\n\n你经常是别人的"港湾"——跟你在一起很安全，不会突然要走，不会催你，不会用你。',
    'pattern_en': "Your core concern isn't 'what do I want to become' — it's 'am I being treated as a person.' You're not rushing, you settle well — but you have an extremely clear line.\n\nYou're often others' 'safe harbor.' Being with you feels safe — you won't suddenly leave, you won't rush them, you won't use them.",
    'pitfall': '涌现层的终身蛰伏。你的三个低敏感维度构成了一个极其厚实的惰性层，你可能一生都在守护一个位置而从未问过"我自己想要什么"。',
    'pitfall_en': "Lifelong dormancy of the drive layer. Three low-sensitivity dimensions create an extremely thick inertia layer. You might spend your whole life guarding a position without ever asking 'what do I myself want.'",
    'misunderstood': ['「他没什么追求」→ 不是没有涌现层，是涌现层从未被催化','「他很随和」→ 碰了底线就知道他一点都不随和'],
    'misunderstood_en': ["'He has no ambitions' → Not no drive — it was never catalyzed","'He's so easygoing' → Touch the line and you'll see he's not easygoing at all"],
    'works_not': '「你应该有自己的追求」——涌现层的重型语言对你不管用。', 'works_not_en': "'You should have your own pursuits' — heavy drive-layer language doesn't work on you.",
    'works': '在基础层完全安全的前提下，用好奇心微小催化涌现层。"你有没有好奇过，如果你试试X会怎样？"关键词是"好奇"不是"应该"。',
    'works_en': "In a fully safe foundation, use curiosity to gently catalyze the drive layer. 'Have you ever wondered what would happen if you tried X?' Key word: 'curious,' not 'should.'",
  },
  'DFER': {
    'zh': '驱烈拓游', 'en': 'Drive · Fierce · Explore · Roam',
    'tagline': '四个频道全开，什么信号都收。', 'tagline_en': 'All four channels open. Receives every signal.',
    'dims': [('驱','求不得（高）：内在驱动力极强'),('烈','不可忍（高）：底线极硬'),('拓','不可选（高）：方向自由是核心需求'),('游','不可逃（高）：对被困住极度警觉')],
    'dims_en': [('D','Drive (High): Intense internal drive'),('F','Fierce (High): Hard limits'),('E','Autonomy (High): Directional freedom is a core need'),('R','Exit (High): Extremely alert to being trapped')],
    'pattern': '你同时在四条线上运转——有强烈的驱动力要往前冲，有敏锐的底线意识随时监测，需要方向空间保持开放，还需要确认退出通道没被封堵。任何一种不被满足都会触发明显的痛苦。\n\n别人说你"太强烈了""活得太用力"。但从你的视角看，你只是什么都能感知到——四个维度的信号同时接收，不可能假装某个不存在。',
    'pattern_en': "You're running on all four channels simultaneously — intense drive, sharp boundary awareness, directional openness, and exit monitoring. Any one need unsatisfied triggers clear pain.\n\nPeople say you're 'too intense.' From your view, you're not living hard — you just perceive everything. Four dimensions of signals received simultaneously; you can't pretend any doesn't exist.",
    'pitfall': '不是某一个维度崩溃，而是四线作战导致的全面疲劳。所有维度在"轻度报警"，没有一个崩溃但全都不舒服——一种慢性的、弥漫性的疲劳。\n\n你的另一个风险是找不到能同时满足四种需求的环境。大多数环境满足一两种就不错了。',
    'pitfall_en': "Not one dimension collapsing, but comprehensive fatigue from fighting on four fronts. All dimensions in 'mild alert' — none collapsed but all uncomfortable. A chronic, diffuse exhaustion.\n\nYour other risk: not finding an environment that satisfies all four needs at once. Most environments do well to satisfy one or two.",
    'misunderstood': ['「他太挑剔了」→ 不是挑剔，是四个报警系统都在工作','「他永远不满足」→ 不是不满足，是四个维度的需求同时在线','「他为什么这么累」→ 因为四个频道全开，24小时不关机'],
    'misunderstood_en': ["'He's too demanding' → Not demanding — all four alarm systems are working","'He's never satisfied' → Not unsatisfied — four needs online simultaneously","'Why is he so exhausted' → Four channels open 24/7, never off"],
    'works_not': '「降低你的标准」「别想那么多」——这是让你变成另一种类型。', 'works_not_en': "'Lower your standards' / 'don't think so much' — this asks you to become a different type.",
    'works': '维度间的时序管理。不是四线同时作战，而是在不同时间段聚焦不同维度。管理带宽比降低敏感度更有效。',
    'works_en': "Temporal sequencing between dimensions. Not four-front simultaneous combat, but focusing on different dimensions at different times. Managing bandwidth is more effective than lowering sensitivity.",
  },
  'DTEB': {
    'zh': '驱容拓栖', 'en': 'Drive · Tolerant · Explore · Base',
    'tagline': '驱动力强，要方向自由，扎得住——基础层报警系统偏弱。', 'tagline_en': "Strong drive, needs directional freedom, can settle — foundation alarms are off.",
    'dims': [('驱','求不得（高）：内在驱动力强'),('容','不可忍（低）：基础层侵蚀能扛'),('拓','不可选（高）：方向自由是核心需求'),('栖','不可逃（低）：扎得住')],
    'dims_en': [('D','Drive (High): Strong internal drive'),('T','Tolerant (Low): Can absorb foundational violations'),('E','Autonomy (High): Directional freedom is core'),('B','Base (Low): Settled')],
    'pattern': '你的全部能量都在涌现层——强烈的驱动力加上对方向自由的渴望。你不会"给条路就冲"（那是DTAB），你需要自己选方向。同时你能扎得住，不会漂。\n\n但你的基础层两个报警系统都静音——被工具化了能忍，退出通道被封了不焦虑。',
    'pattern_en': "All your energy is in the drive layer — intense drive plus hunger for directional freedom. You won't 'run any path given to you' — you need to choose your own direction. You can also settle in.\n\nBut your foundational alarm systems are both muted — being instrumentalized is tolerable, exit channels being sealed doesn't cause anxiety.",
    'pitfall': '"自由地透支"。方向是你自己选的，目标在推进，所以你主观上完全觉得没问题。但你可能在一个"自己选择的事业"中持续自我工具化而不自知。"这是我自己选的"成了最强的防御叙事。',
    'pitfall_en': "'Freely depleting yourself.' The direction is self-chosen, goals advancing — subjectively you feel fine. But you might be continuously self-instrumentalizing within 'the career I chose' without knowing it. 'I chose this' becomes the strongest defensive narrative.",
    'misunderstood': ['「他很有主见」→ 有主见没错，但基础层保护是缺失的','「他不需要人照顾」→ 这是他告诉自己的故事，不一定是真的'],
    'misunderstood_en': ["'He has a strong sense of self' → True, but foundational protection is missing","'He doesn't need looking after' → That's the story he tells himself — not necessarily true"],
    'works_not': '任何绕开"方向选择权"的建议。', 'works_not_en': "Any advice that bypasses the right to choose direction.",
    'works': '你需要一个基础层敏感度高的人在身边——当你的"这是我选的"叙事阻止你看到基础层侵蚀时，他们的一句话可能是唯一穿透屏障的信号。',
    'works_en': "You need someone with high foundational sensitivity nearby — when your 'I chose this' narrative blocks you from seeing foundational erosion, their question might be the only signal that can breach your barrier.",
  },
  'CFAR': {
    'zh': '泰烈专游', 'en': 'Composed · Fierce · Anchor · Roam',
    'tagline': '不急但底线硬，专注但不被绑——有原则的自由人。', 'tagline_en': 'Unhurried but hard-lined. Focused but unbound — principled freedom.',
    'dims': [('泰','求不得（低）：涌现层安静'),('烈','不可忍（高）：底线极硬'),('专','不可选（低）：能在一个方向上深入'),('游','不可逃（高）：对被困住极度警觉')],
    'dims_en': [('C','Composed (Low): Quiet drive layer'),('F','Fierce (High): Hard limits'),('A','Anchor (Low): Can go deep in one direction'),('R','Exit (High): Extremely alert to being trapped')],
    'pattern': '你的全部能量在基础层。底线极其清晰，同时对被困住极度警觉。涌现层相对安静——不急着冲，方向有限也不焦虑。\n\n你看起来淡泊，但碰了底线反应坚决。看起来安定，但试图绑住你就立刻拉开距离。你的自由不是扩张型，而是防御型。',
    'pattern_en': "All your energy is in the foundation. Extremely clear limits, and extremely alert to being trapped. Drive layer quiet — not rushing, limited direction is fine.\n\nYou appear detached, but when the line is crossed you respond decisively. You appear stable, but try to bind you and you immediately create distance.",
    'pitfall': '基础层堡垒太坚固变成了封闭。"我不需要那些"可能不是真的不需要，是涌现层从未被催化。',
    'pitfall_en': "Foundational fortress too solid becomes closure. 'I don't need those things' might not be genuine — it might be that the drive layer was never catalyzed.",
    'misunderstood': ['「他很淡泊」→ 不是真的不在乎，是在乎不同的东西','「他很容易相处」→ 直到碰了底线或者试图限制他'],
    'misunderstood_en': ["'He's very detached' → Not indifferent — cares about different things","'He's easy to get along with' → Until you touch his limits or try to restrict him"],
    'works_not': '在基础层不安全时催化涌现层——这只会触发双重防御。', 'works_not_en': "Catalyzing the drive layer when the foundation isn't safe — this only triggers dual defense.",
    'works': '在基础层完全安全的前提下，才能接收涌现层的信号。安全感必须先于催化。',
    'works_en': "Only when the foundation is completely safe can drive-layer signals be received. Safety must precede catalysis.",
  },
  'DTAR': {
    'zh': '驱容专游', 'en': 'Drive · Tolerant · Anchor · Roam',
    'tagline': '往前冲，能忍，能专注，但随时准备走。', 'tagline_en': 'Runs hard, absorbs friction, stays focused — but always ready to leave.',
    'dims': [('驱','求不得（高）：内在驱动力强'),('容','不可忍（低）：基础层侵蚀能扛'),('专','不可选（低）：能在一个方向上深入'),('游','不可逃（高）：对被困住极度警觉')],
    'dims_en': [('D','Drive (High): Strong internal drive'),('T','Tolerant (Low): Can absorb foundational erosion'),('A','Anchor (Low): Can go deep in one direction'),('R','Exit (High): Extremely alert to being trapped')],
    'pattern': '你能全力投入（驱+专），但你的投入不是因为"走不了"，而是因为"我选择留下"。一旦"选择留下"变成"不得不留下"，驱动力可能瞬间消失。\n\n你的典型轨迹：全力投入→做到某个阶段→感到"该走了"→干脆利落地离开→投入下一个。',
    'pattern_en': "You can commit fully (Drive + Anchor), but your commitment isn't because 'you can't leave' — it's because 'I choose to stay.' The moment 'choosing to stay' becomes 'forced to stay,' your drive can instantly vanish.\n\nYour typical pattern: full commitment → reach a stage → feel 'time to go' → clean departure → commit to the next.",
    'pitfall': '连续创业者综合征——每一段都在透支基础层（因为容让你忍），然后用离开来逃避修复（因为游让你走）。生命轨迹变成：投入→透支→离开→投入→透支→离开。',
    'pitfall_en': "Serial founder syndrome — each period depletes the foundation (Tolerant lets you absorb), then you use leaving to avoid repair (Roam lets you go). Life trajectory becomes: commit → deplete → leave → commit → deplete → leave.",
    'misunderstood': ['「他很洒脱」→ 离开的代价他自己扛，外人看不见','「他很专注」→ 只到离开的那一刻为止'],
    'misunderstood_en': ["'He's so free-spirited' → The cost of leaving is his to carry — others don't see it","'He's so dedicated' → Until the moment he leaves"],
    'works_not': '「你应该安定下来」——直接触发游的防御。', 'works_not_en': "'You should settle down' — directly triggers Exit defenses.",
    'works': '不是要你安定，而是在每一段投入中加入基础层检查点。把游从逃跑机制升级为主动管理机制。',
    'works_en': "Not asking you to settle, but adding foundational checkpoints in each period of commitment. Upgrading Exit from an escape mechanism to an active management tool.",
  },
  'DFEB': {
    'zh': '驱烈拓栖', 'en': 'Drive · Fierce · Explore · Base',
    'tagline': '驱动力和底线都强，要方向自由但能安落——最完整的涌现型。', 'tagline_en': 'Driven and principled, needs directional freedom, can settle — the most complete emergent type.',
    'dims': [('驱','求不得（高）：内在驱动力强'),('烈','不可忍（高）：底线极硬'),('拓','不可选（高）：方向自由是核心需求'),('栖','不可逃（低）：能在一个地方深根')],
    'dims_en': [('D','Drive (High): Strong internal drive'),('F','Fierce (High): Hard limits'),('E','Autonomy (High): Directional freedom is core'),('B','Base (Low): Can root deeply in one place')],
    'pattern': '你是DFER去掉游的版本——不需要流动性，能在一个地方深入扎根，同时保持驱动力、底线和方向自由。你需要能同时满足"强烈推进""原则不被碰""我自己选方向"三种需求的环境，这样的环境不多，但一旦找到，你能发挥极致。',
    'pattern_en': "You're DFER minus the roaming — you can put down deep roots while maintaining drive, principles, and directional freedom.\n\nYou need an environment that simultaneously satisfies 'intense advancement,' 'principles aren't violated,' and 'I choose my direction.' These environments are rare — but once found, you can perform at your peak.",
    'pitfall': '栖的安稳慢慢吸收拓的能量——待久了，"探索新方向"从需求退化为念头。你可能在一个足够舒适的环境里，慢慢放弃了自己最核心的涌现层需求。',
    'pitfall_en': "Base's stability slowly absorbs Autonomy's energy — after a while, 'exploring new directions' degrades from a need to a passing thought. You might slowly abandon your most core drive-layer need inside a comfortable enough environment.",
    'misunderstood': ['「他要求太高」→ 他需要三种条件同时满足，不是挑剔是结构需求','「他很稳定」→ 稳定是因为栖，但内部驱动从未停'],
    'misunderstood_en': ["'He has high demands' → He needs three conditions simultaneously — not picky, a structural need","'He's so stable' → Stable because of Base, but internal drive never stops"],
    'works_not': '强迫在不满足方向自由时继续投入。', 'works_not_en': "Forcing continued commitment when directional freedom isn't met.",
    'works': '定期审视：三个高敏感维度是否同时被满足？哪一个在萎缩？及早调整比等待崩溃有效得多。',
    'works_en': "Regularly review: are all three high-sensitivity dimensions being simultaneously satisfied? Which one is atrophying? Early adjustment is far more effective than waiting for collapse.",
  },
  'DFAR': {
    'zh': '驱烈专游', 'en': 'Drive · Fierce · Anchor · Roam',
    'tagline': '驱动力和底线都强，专注但保持流动——有根的漫游者。', 'tagline_en': 'Driven and principled. Focused but in motion — a rooted wanderer.',
    'dims': [('驱','求不得（高）：内在驱动力强'),('烈','不可忍（高）：底线极硬'),('专','不可选（低）：能在一个方向上深入'),('游','不可逃（高）：对被困住极度警觉')],
    'dims_en': [('D','Drive (High): Strong internal drive'),('F','Fierce (High): Hard limits'),('A','Anchor (Low): Can go deep in one direction'),('R','Exit (High): Extremely alert to being trapped')],
    'pattern': '跟DTAR的区别在于烈——你不能忍，底线被碰了就走。每一段停留中基础层得到更好的保护（烈在工作），但也可能因为底线被触及而更频繁地离开。\n\n人们觉得你难以预测——其实你的离开都有原因，只是他们没看见那条线。',
    'pattern_en': "The difference from DTAR is Dignity — you can't absorb violations; when the line is crossed you leave. Foundation gets better protection in each stay.\n\nPeople find you unpredictable — actually your departures all have reasons; they just never saw the line.",
    'pitfall': '驱的推进需求和游的流动需求都很强，而烈让你在底线被触碰时快速离开。每一次离开都有正当理由，但离开的频率本身会成为一种结构性的损耗。',
    'pitfall_en': "Drive's advancement need and Exit's mobility need are both intense, while Dignity makes you leave quickly when crossed. Every departure has legitimate reason, but the frequency of departures itself becomes a structural drain.",
    'misunderstood': ['「他很难相处」→ 不是难相处，是他的底线很清晰','「他不稳定」→ 不是不稳定，是不接受底线被触碰后继续待'],
    'misunderstood_en': ["'He's difficult to work with' → Not difficult — his limits are clear","'He's unstable' → Not unstable — unwilling to continue after limits are crossed"],
    'works_not': '期待他为了"大局"忍受底线被碰。', 'works_not_en': "Expecting him to tolerate limits being crossed 'for the bigger picture.'",
    'works': '提前识别并明确说清楚你的底线在哪里。透明化你的边界，让环境有机会在触碰之前调整。',
    'works_en': "Identify and clearly articulate your limits in advance. Make your boundaries transparent — give the environment a chance to adjust before touching them.",
  },
  'DTER': {
    'zh': '驱容拓游', 'en': 'Drive · Tolerant · Explore · Roam',
    'tagline': '涌现层全高基础层全低——流星型。', 'tagline_en': 'Drive layer fully high, foundation fully low — the comet type.',
    'dims': [('驱','求不得（高）：驱动力强烈'),('容','不可忍（低）：基础层被侵蚀能扛'),('拓','不可选（高）：方向空间是核心需求'),('游','不可逃（高）：不能被困住')],
    'dims_en': [('D','Drive (High): Intense drive'),('T','Tolerant (Low): Can absorb foundational erosion'),('E','Autonomy (High): Directional space is core'),('R','Exit (High): Cannot be trapped')],
    'pattern': '驱动力强烈，方向空间无限，流动性完全。你的涌现层极度辉煌——几乎能在任何方向上点燃。但你的基础层完全暴露：被工具化了能忍，退出通道被封了反而不焦虑。\n\n你在别人眼里是"那种耀眼的人"。消耗极快。',
    'pattern_en': "Intense drive, unlimited directional space, complete mobility. Your drive layer is extraordinarily bright — you can ignite in almost any direction. But your foundation is fully exposed.\n\nTo others you're 'that brilliant person.' Extremely fast burn rate.",
    'pitfall': '你不需要更多涌现层的空间——你已经有了。你需要的是有人帮你的基础层兜底。你的基础层在你无声无息地被消耗时不报警，但损耗是真实的。',
    'pitfall_en': "You don't need more drive-layer space — you already have it. What you need is someone to backstop your foundation. Your foundational alarm systems don't fire when you're being silently depleted, but the depletion is real.",
    'misunderstood': ['「他好像不在乎自己」→ 他在乎，只是基础层的报警系统静音了','「他怎么能那么随意」→ 随意背后有很高的透支成本'],
    'misunderstood_en': ["'He seems not to care about himself' → He does — foundational alarms are just muted","'How can he be so casual' → Behind the casualness is a very high depletion cost"],
    'works_not': '让他降低涌现层的标准。', 'works_not_en': "Making him lower his drive-layer standards.",
    'works': '找到一个愿意为他的基础层"站岗"的人——不是控制，是监测。当基础层侵蚀开始时，需要有人能看见并说出来。',
    'works_en': "Find someone willing to 'stand watch' for his foundation — not control, but monitoring. When foundational erosion begins, someone needs to see it and name it.",
  },
  'CTEB': {
    'zh': '泰容拓栖', 'en': 'Composed · Tolerant · Explore · Base',
    'tagline': '不急能忍但要方向空间，扎得住——温和的探索者。', 'tagline_en': 'Calm and absorbing, but needs directional space, can settle — the gentle explorer.',
    'dims': [('泰','求不得（低）：不急'),('容','不可忍（低）：能扛'),('拓','不可选（高）：方向自由是唯一的底线'),('栖','不可逃（低）：扎得住')],
    'dims_en': [('C','Composed (Low): Not rushing'),('T','Tolerant (Low): Can absorb'),('E','Autonomy (High): Directional freedom is the one line'),('B','Base (Low): Can settle')],
    'pattern': '日常看起来极其随和——不急、不计较、不闹。但在"你只能走这条路"的时刻突然表现出强烈的抗拒。方向自由是你唯一的底线，其他三个维度都相对耐受。\n\n你是被低估的类型。别人觉得你好说话，但你有一条人们没意识到的红线。',
    'pattern_en': "Day-to-day you come across as extremely easy-going — not rushed, not fussy, no drama. But in the moment of 'you can only go this way,' you show sudden, strong resistance.\n\nYou're an underestimated type. Others think you're agreeable, but you have a line they haven't noticed.",
    'pitfall': '因为三个低敏感维度，你很容易被"拖进"一个固定轨道而不自觉。等你意识到方向已经被锁死，你的基础层报警系统早就静音了，反应会晚。',
    'pitfall_en': "With three low-sensitivity dimensions, you're easily 'pulled into' a fixed track without realizing it. By the time you notice the direction is locked, your alarm systems were already muted, and your response comes late.",
    'misunderstood': ['「他没什么要求」→ 有，只是那条线不明显','「他为什么突然不配合了」→ 他的方向自由触碰到了临界点'],
    'misunderstood_en': ["'He has no demands' → He does — that line just isn't obvious","'Why did he suddenly stop cooperating' → His directional freedom hit the threshold"],
    'works_not': '以为他"随便都行"而不给他方向选择权。', 'works_not_en': "Assuming he's 'fine with anything' and not giving him directional choice.",
    'works': '提前明确那条线在哪里。让环境知道"你可以在这里自己决定方向"——这比任何其他激励都有效。',
    'works_en': "Make that line explicit in advance. Let the environment know 'you can decide your own direction here' — more effective than any other kind of incentive.",
  },
  'CFER': {
    'zh': '泰烈拓游', 'en': 'Composed · Fierce · Explore · Roam',
    'tagline': '不急但底线硬，要空间不被绑——基础层主导的全面自由型。', 'tagline_en': "Unhurried but hard-lined. Needs space, won't be bound — full-spectrum foundational freedom.",
    'dims': [('泰','求不得（低）：不急着赶路'),('烈','不可忍（高）：底线极硬'),('拓','不可选（高）：要方向空间'),('游','不可逃（高）：对被困住极度警觉')],
    'dims_en': [('C','Composed (Low): Not rushing anywhere'),('F','Fierce (High): Hard limits'),('E','Autonomy (High): Needs directional space'),('R','Exit (High): Extremely alert to being trapped')],
    'pattern': '三高一低，只有求不得低。极度"自由"——不赶路，有原则，要空间，不被绑。你不需要驱动力来维持主体性，你只需要确保没有东西在侵蚀你。\n\n这个配置有巨大的防御力，但也有一个盲区：涌现层的驱动力从未被激活。',
    'pattern_en': "Three high, one low — only Drive is low. Extremely 'free' — not rushing, principled, needs space, won't be bound. You don't need drive to maintain subjectivity — you just need nothing to be eroding you.\n\nThis configuration has enormous defensive power — but also a blind spot: the drive layer's push has never been activated.",
    'pitfall': '防御体系太完美的结果是什么都不需要冒险。你保护得很好，但从来没有去追什么。涌现层的潜力可能终身未发。',
    'pitfall_en': "The result of a too-perfect defense system: nothing needs to be risked. You're very well-protected, but you've never chased anything. The potential of the drive layer may go unrealized lifelong.",
    'misunderstood': ['「他很淡定」→ 淡定不等于没有要求，碰了他的三条线就知道了','「他为什么不努力」→ 驱动力确实低，但这不是缺陷是配置'],
    'misunderstood_en': ["'He's very calm' → Calm doesn't mean no demands — touch his three lines and you'll see","'Why doesn't he work harder' → Drive genuinely is low — not a defect, a configuration"],
    'works_not': '用外部目标驱动他——没有内在驱动时，外部目标只是噪音。', 'works_not_en': "Motivating him with external goals — without internal drive, external goals are just noise.",
    'works': '先把三条线（烈、拓、游）都护好，然后才有空间问"你有没有想做什么"。顺序不能反。',
    'works_en': "First protect all three lines (Dignity, Autonomy, Exit), then there's space to ask 'is there anything you want to do?' The order cannot be reversed.",
  },
  'CFEB': {
    'zh': '泰烈拓栖', 'en': 'Composed · Fierce · Explore · Base',
    'tagline': '不急但底线硬，要空间但能安落——成熟的守护者。', 'tagline_en': 'Unhurried but principled. Needs space but can settle — the mature guardian.',
    'dims': [('泰','求不得（低）：不急'),('烈','不可忍（高）：底线极硬'),('拓','不可选（高）：要方向空间'),('栖','不可逃（低）：能扎得住')],
    'dims_en': [('C','Composed (Low): Not rushing'),('F','Fierce (High): Hard limits'),('E','Autonomy (High): Needs directional space'),('B','Base (Low): Can settle')],
    'pattern': '跟CFER的区别是栖vs游——你能扎住。成熟期的学者和手艺人常见这种配置：有原则，需要探索空间，找到了一个能安落的位置，不急。\n\n你不是在漂，你是在你自己选的地方扎根，同时守住底线和探索空间。',
    'pattern_en': "The difference from CFER is Base vs. Exit — you can settle. The scholar or craftsperson in their mature phase often shows this configuration: principled, needs exploratory space, found a place to land, unhurried.\n\nYou're not drifting — you're rooting in a place of your own choosing, while maintaining your principles and exploratory space.",
    'pitfall': '涌现层的驱动力缺席（泰）使得探索可能流于表面——有空间但不一定有动力去充分使用。',
    'pitfall_en': "The drive layer's absence (Composed) means exploration may stay superficial — there's space but not necessarily the energy to use it fully.",
    'misunderstood': ['「他很稳定」→ 稳定是真的，但内部的底线和探索需求也是真的','「他没什么野心」→ 没有求不得的驱动，但有方向探索的需求'],
    'misunderstood_en': ["'He's very stable' → Stable is true, but internal limits and exploration needs are also real","'He has no ambitions' → No drive-craving, but there is a need for directional exploration"],
    'works_not': '催他"更进取"。', 'works_not_en': "Pushing him to 'be more ambitious.'",
    'works': '给他足够的原则空间（不触碰烈）和方向空间（满足拓），他会自然地在稳定中深入。',
    'works_en': "Give him adequate principled space (don't touch Dignity) and directional space (satisfy Autonomy), and he'll naturally go deep within stability.",
  },
  'CTAR': {
    'zh': '泰容专游', 'en': 'Composed · Tolerant · Anchor · Roam',
    'tagline': '不急能忍能专注但不被绑——安静的流动者。', 'tagline_en': "Unhurried, absorbing, focused — but won't be pinned. The quiet mover.",
    'dims': [('泰','求不得（低）：不急'),('容','不可忍（低）：能扛'),('专','不可选（低）：能在一个方向上深入'),('游','不可逃（高）：唯一的高敏感维度')],
    'dims_en': [('C','Composed (Low): Not rushing'),('T','Tolerant (Low): Can absorb'),('A','Anchor (Low): Can go deep in one direction'),('R','Exit (High): The single high-sensitivity dimension')],
    'pattern': '在任何环境中都适应良好，但总在某个时刻悄悄离开。不是在逃避什么，是游需要定期被满足。你的三个低维度让你在任何地方都能活得不错，但游会定期提醒你"不要被锁死"。\n\n你很少跟别人解释为什么要走，因为你自己也说不清楚——只是感觉"该走了"。',
    'pattern_en': "Adapts well in any environment, but always quietly leaves at some point. Not running away — the Exit need requires periodic satisfaction.\n\nYou rarely explain to others why you're leaving — partly because you can't quite articulate it yourself. Just 'feels like it's time.'",
    'pitfall': '游的驱动可能让你在一个本来很好的位置上过早离开。不是位置不好，是游的信号误报了。',
    'pitfall_en': "Exit's drive might make you leave a genuinely good position too early. Not because the position is bad — the Exit signal was a false alarm.",
    'misunderstood': ['「他为什么要走」→ 问他自己他也说不清楚，但游的需求是真实的','「他不投入」→ 他投入，只是会走'],
    'misunderstood_en': ["'Why is he leaving' → Even if asked, he can't quite say — but the Exit need is real","'He's not committed' → He is — he just leaves"],
    'works_not': '试图用"这里很好"来说服他留下。', 'works_not_en': "Trying to convince him to stay with 'things are good here.'",
    'works': '给他明确的"可以离开"信号——哪怕他不会真的用。知道通道没有被堵，游的焦虑就会平息。',
    'works_en': "Give him a clear 'you can leave' signal — even if he never uses it. Knowing the channel isn't blocked is enough for Exit anxiety to settle.",
  },
  'CTER': {
    'zh': '泰容拓游', 'en': 'Composed · Tolerant · Explore · Roam',
    'tagline': '不急能忍要空间不被绑——潜力型自由。', 'tagline_en': 'Unhurried, absorbing, needs space and mobility — latent freedom.',
    'dims': [('泰','求不得（低）：不急着去哪里'),('容','不可忍（低）：基础层能扛'),('拓','不可选（高）：需要方向开放性'),('游','不可逃（高）：需要流动可能性')],
    'dims_en': [('C','Composed (Low): Not rushing anywhere'),('T','Tolerant (Low): Can absorb foundationally'),('E','Autonomy (High): Needs directional openness'),('R','Exit (High): Needs mobility as possibility')],
    'pattern': '不急着去哪里，但需要"可以去任何地方"的可能性存在。不是为了做什么而自由，是自由本身就是需求。两个低敏感维度让你很少因为外部原因崩溃，两个高敏感维度保持了一种结构性的开放性。\n\n你是一种罕见的平衡：不焦虑也不麻木，只是保持开放。',
    'pattern_en': "Not rushing anywhere, but needs the possibility of 'I could go anywhere' to exist. Not free to do something — freedom itself is the need.\n\nA rare equilibrium: not anxious but not numbed — just staying open.",
    'pitfall': '没有驱动力（泰）的情况下，拓和游的开放性可能流于姿态而非行动。你有方向自由，但没有特别想去哪里；你有流动可能，但不一定会移动。',
    'pitfall_en': "Without drive (Composed), the openness of Autonomy and Exit might remain gestural rather than enacted. You have directional freedom but nothing specific pulling you anywhere; mobility potential but not necessarily any movement.",
    'misunderstood': ['「他飘」→ 不是飘，是结构上的开放性','「他没目标」→ 有，只是目标不是外部成就'],
    'misunderstood_en': ["'He's adrift' → Not adrift — structurally open","'He has no goals' → He does — just not external achievement"],
    'works_not': '给他一个固定的目标方向然后期待全力投入。', 'works_not_en': "Giving him a fixed direction and expecting full commitment.",
    'works': '给他开放性——让他知道选项是存在的。这比任何具体目标都更能激活他。',
    'works_en': "Give him openness — let him know options exist. This activates him more than any specific goal.",
  },
}

# Type codes in order
TYPE_CODES = ['DTAB', 'CTAB', 'DFAB', 'CFAB', 'DFER', 'DTEB', 'CFAR', 'DTAR', 
              'DFEB', 'DFAR', 'DTER', 'CTEB', 'CFER', 'CFEB', 'CTAR', 'CTER']

def escape_html(text):
    """Escape HTML special characters."""
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#39;'))

def format_paragraphs(text):
    """Convert double newlines to <p> tags."""
    paragraphs = text.split('\n\n')
    html_paragraphs = [f'<p>{escape_html(p.strip())}</p>' for p in paragraphs if p.strip()]
    return ''.join(html_paragraphs)

def get_dimension_indicator(dim_index):
    """Get HIGH or LOW indicator for dimension."""
    # All high-order dimensions: 驱(D), 烈(F), 拓(E), 游(R) are typically high
    # All low-order dimensions: 容(T), 专(A), 栖(B) are typically low
    high_dims = {'驱': 'HIGH', '烈': 'HIGH', '拓': 'HIGH', '游': 'HIGH',
                 'D': 'HIGH', 'F': 'HIGH', 'E': 'HIGH', 'R': 'HIGH'}
    low_dims = {'容': 'LOW', '专': 'LOW', '栖': 'LOW', '泰': 'LOW',
                'T': 'LOW', 'A': 'LOW', 'B': 'LOW', 'C': 'LOW'}
    
    # For each type, determine actual HIGH/LOW based on description
    # This is a simplification - in production you'd store this explicitly
    return None

def generate_type_page(type_code, type_data):
    """Generate HTML for a single type profile page."""
    
    # Determine which dimensions are HIGH
    high_indicators = []
    if 'D' in type_code or '驱' in [d[0] for d in type_data['dims']]:
        # Check if it says (高) in the description
        for char, desc in type_data['dims']:
            if '（高）' in desc:
                high_indicators.append(char)
    
    # Build high indicators from descriptions
    high_indicators = set()
    for char, desc in type_data['dims']:
        if '（高）' in desc:
            high_indicators.add(char)
    
    html = f"""<!DOCTYPE html>
<html lang="zh" data-lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{escape_html(type_data['tagline'])} — {escape_html(type_data['en'])} | HC-16 Vulnerability Profile">
    <meta property="og:title" content="{type_code} · {type_data['zh']} — HC-16">
    <meta property="og:description" content="{escape_html(type_data['tagline'])}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://nondubito.net/hc16/{type_code}.html">
    <meta name="canonical" href="https://nondubito.net/hc16/{type_code}.html">
    <title>{type_code} · {type_data['zh']} — HC-16 Vulnerability Profile</title>
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital@0;1&family=Inter:wght@400;500;600&family=Noto+Serif+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{
            background: #0f0f0e;
            color: #f5f0e8;
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
        }}
        
        [data-lang="en"] .lang-zh {{ display: none; }}
        [data-lang="zh"] .lang-en {{ display: none; }}
        
        body {{
            background: #0f0f0e;
            color: #f5f0e8;
        }}
        
        header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 70px;
            background: rgba(15, 15, 14, 0.95);
            border-bottom: 1px solid rgba(196, 157, 97, 0.2);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 40px;
            z-index: 100;
            backdrop-filter: blur(10px);
        }}
        
        .header-left {{
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.05em;
        }}
        
        .header-left a {{
            color: #c49d61;
            text-decoration: none;
            transition: color 0.3s;
        }}
        
        .header-left a:hover {{
            color: #e5c194;
        }}
        
        .header-center {{
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            font-size: 16px;
            font-weight: 600;
            letter-spacing: 0.15em;
            color: #c49d61;
        }}
        
        .header-right {{
            font-size: 12px;
            letter-spacing: 0.05em;
        }}
        
        .lang-toggle {{
            cursor: pointer;
            color: #999;
            transition: color 0.3s;
        }}
        
        .lang-toggle:hover {{
            color: #c49d61;
        }}
        
        .lang-toggle.active {{
            color: #c49d61;
        }}
        
        main {{
            margin-top: 70px;
            padding: 80px 40px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .hero {{
            margin-bottom: 60px;
        }}
        
        .type-code {{
            font-size: 5rem;
            font-weight: 700;
            letter-spacing: 0.15em;
            color: #c49d61;
            margin-bottom: 20px;
            font-family: 'Inter', monospace;
        }}
        
        .type-name-zh {{
            font-size: 3rem;
            font-weight: 700;
            font-family: 'Noto Serif SC', serif;
            margin-bottom: 15px;
            color: #f5f0e8;
        }}
        
        .type-name-en {{
            font-size: 1.1rem;
            color: #999;
            letter-spacing: 0.05em;
            margin-bottom: 30px;
            font-weight: 400;
        }}
        
        .tagline {{
            font-size: 1.4rem;
            font-family: 'EB Garamond', serif;
            font-style: italic;
            color: #e5c194;
            margin-bottom: 40px;
            line-height: 1.8;
        }}
        
        .dimensions {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 60px;
            padding: 30px;
            background: rgba(196, 157, 97, 0.05);
            border: 1px solid rgba(196, 157, 97, 0.1);
        }}
        
        .dimension {{
            display: flex;
            gap: 15px;
        }}
        
        .dim-char {{
            font-size: 1.8rem;
            font-weight: 700;
            font-family: 'Noto Serif SC', serif;
            min-width: 40px;
            text-align: center;
            color: #c49d61;
        }}
        
        .dimension.low .dim-char {{
            color: #666;
            opacity: 0.6;
        }}
        
        .dim-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #c49d61;
            margin-right: 8px;
            margin-top: 2px;
        }}
        
        .dimension.low .dim-indicator {{
            background: transparent;
            border: 2px solid #666;
        }}
        
        .dim-content {{
            flex: 1;
        }}
        
        .dim-label {{
            font-size: 0.95rem;
            font-weight: 500;
            color: #f5f0e8;
            margin-bottom: 5px;
        }}
        
        .dim-label .en {{
            display: block;
            font-size: 0.85rem;
            color: #999;
            font-weight: 400;
            margin-top: 3px;
        }}
        
        .dim-desc {{
            font-size: 0.9rem;
            color: #ccc;
            line-height: 1.5;
        }}
        
        section {{
            margin-bottom: 50px;
        }}
        
        h2 {{
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: #c49d61;
            letter-spacing: 0.05em;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(196, 157, 97, 0.2);
        }}
        
        p {{
            font-size: 1rem;
            margin-bottom: 15px;
            line-height: 1.8;
            color: #d4cfc2;
        }}
        
        .misunderstood-list {{
            list-style: none;
            margin: 0;
            padding: 0;
        }}
        
        .misunderstood-list li {{
            padding: 15px 20px;
            margin-bottom: 10px;
            background: rgba(196, 157, 97, 0.03);
            border-left: 3px solid #c49d61;
            font-size: 0.95rem;
        }}
        
        .misunderstood-list li .en {{
            display: block;
            margin-top: 5px;
            color: #999;
            font-size: 0.9rem;
        }}
        
        .two-column {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }}
        
        .works-box {{
            padding: 20px;
            background: rgba(196, 157, 97, 0.05);
            border: 1px solid rgba(196, 157, 97, 0.1);
        }}
        
        .works-box h3 {{
            font-size: 0.95rem;
            font-weight: 600;
            color: #c49d61;
            margin-bottom: 15px;
            letter-spacing: 0.05em;
        }}
        
        .works-box p {{
            font-size: 0.95rem;
            margin-bottom: 0;
        }}
        
        .cta {{
            text-align: center;
            padding: 40px 0;
            border-top: 1px solid rgba(196, 157, 97, 0.2);
            margin-top: 60px;
        }}
        
        .cta-button {{
            display: inline-block;
            padding: 15px 40px;
            background: #c49d61;
            color: #0f0f0e;
            text-decoration: none;
            font-weight: 600;
            letter-spacing: 0.05em;
            transition: background 0.3s;
            margin: 0 10px;
        }}
        
        .cta-button:hover {{
            background: #e5c194;
        }}
        
        .cta-button.secondary {{
            background: transparent;
            color: #c49d61;
            border: 1px solid #c49d61;
        }}
        
        .cta-button.secondary:hover {{
            background: rgba(196, 157, 97, 0.1);
        }}
        
        @media (max-width: 768px) {{
            header {{
                padding: 0 20px;
            }}
            
            main {{
                padding: 70px 20px 40px 20px;
            }}
            
            .type-code {{
                font-size: 3rem;
            }}
            
            .type-name-zh {{
                font-size: 2rem;
            }}
            
            .dimensions {{
                grid-template-columns: 1fr;
            }}
            
            .two-column {{
                grid-template-columns: 1fr;
            }}
            
            header {{
                flex-direction: column;
                height: auto;
                padding: 15px 20px;
                gap: 10px;
            }}
            
            .header-center {{
                position: static;
                transform: none;
                font-size: 14px;
            }}
            
            main {{
                margin-top: 0;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-left">
            <a href="/hc16/">← HC-16</a>
        </div>
        <div class="header-center">{type_code}</div>
        <div class="header-right">
            <span class="lang-toggle active" data-lang="zh" onclick="setLang('zh')">中文</span>
            <span style="margin: 0 8px; color: #666;">|</span>
            <span class="lang-toggle" data-lang="en" onclick="setLang('en')">EN</span>
        </div>
    </header>
    
    <main>
        <section class="hero">
            <div class="type-code">{type_code}</div>
            <div class="type-name-zh lang-zh">{type_data['zh']}</div>
            <div class="type-name-en lang-en">{type_data['en']}</div>
            <div class="tagline lang-zh">{escape_html(type_data['tagline'])}</div>
            <div class="tagline lang-en">{escape_html(type_data['tagline_en'])}</div>
        </section>
        
        <section class="dimensions">
"""
    
    # Add dimension display
    for i, (char_zh, desc_zh) in enumerate(type_data['dims']):
        char_en, desc_en = type_data['dims_en'][i]
        is_high = '（高）' in desc_zh
        dim_class = 'dimension' + (' high' if is_high else ' low')
        
        html += f"""            <div class="{dim_class}">
                <div class="dim-char">{char_zh}</div>
                <div class="dim-content">
                    <div class="lang-zh">
                        <div class="dim-label">
                            <span class="dim-indicator"></span>{char_zh}
                        </div>
                        <div class="dim-desc">{escape_html(desc_zh)}</div>
                    </div>
                    <div class="lang-en">
                        <div class="dim-label">
                            <span class="dim-indicator"></span>{char_en}
                        </div>
                        <div class="dim-desc">{escape_html(desc_en)}</div>
                    </div>
                </div>
            </div>
"""
    
    html += """        </section>
        
        <section>
            <h2><span class="lang-zh">结构模式</span><span class="lang-en">Pattern</span></h2>
            <div class="lang-zh">"""
    html += format_paragraphs(type_data['pattern'])
    html += """</div>
            <div class="lang-en">"""
    html += format_paragraphs(type_data['pattern_en'])
    html += """</div>
        </section>
        
        <section>
            <h2><span class="lang-zh">危险地形</span><span class="lang-en">Blind Spots</span></h2>
            <div class="lang-zh">"""
    html += format_paragraphs(type_data['pitfall'])
    html += """</div>
            <div class="lang-en">"""
    html += format_paragraphs(type_data['pitfall_en'])
    html += """</div>
        </section>
        
        <section>
            <h2><span class="lang-zh">常见误读</span><span class="lang-en">Misread As</span></h2>
            <ul class="misunderstood-list">
"""
    
    for i, item_zh in enumerate(type_data['misunderstood']):
        item_en = type_data['misunderstood_en'][i]
        html += f"""                <li>
                    <span class="lang-zh">{escape_html(item_zh)}</span>
                    <span class="lang-en">{escape_html(item_en)}</span>
                </li>
"""
    
    html += f"""            </ul>
        </section>
        
        <section>
            <h2><span class="lang-zh">修复逻辑</span><span class="lang-en">What Helps</span></h2>
            <div class="two-column">
                <div class="works-box">
                    <h3><span class="lang-zh">❌ 不起作用</span><span class="lang-en">❌ Doesn't Work</span></h3>
                    <p class="lang-zh">{escape_html(type_data['works_not'])}</p>
                    <p class="lang-en">{escape_html(type_data['works_not_en'])}</p>
                </div>
                <div class="works-box">
                    <h3><span class="lang-zh">✓ 真正有效</span><span class="lang-en">✓ Actually Works</span></h3>
                    <p class="lang-zh">{escape_html(type_data['works'])}</p>
                    <p class="lang-en">{escape_html(type_data['works_en'])}</p>
                </div>
            </div>
        </section>
        
        <section class="cta">
            <p style="margin-bottom: 25px; color: #999;">
                <span class="lang-zh">了解你的HC-16类型</span>
                <span class="lang-en">Discover your HC-16 type</span>
            </p>
            <a href="https://nondubito.net/" class="cta-button">
                <span class="lang-zh">→ 做一个测试</span>
                <span class="lang-en">→ Take the test</span>
            </a>
            <a href="/hc16/" class="cta-button secondary">
                <span class="lang-zh">→ 浏览所有类型</span>
                <span class="lang-en">→ Browse all types</span>
            </a>
        </section>
    </main>
    
    <script>
        function setLang(lang) {{
            document.documentElement.setAttribute('data-lang', lang);
            document.querySelectorAll('.lang-toggle').forEach(el => {{
                el.classList.remove('active');
                if (el.getAttribute('data-lang') === lang) {{
                    el.classList.add('active');
                }}
            }});
            localStorage.setItem('hc16_lang', lang);
        }}
        
        // Load saved language preference
        const saved = localStorage.getItem('hc16_lang');
        if (saved) {{
            setLang(saved);
        }}
        
        // Update active toggle on load
        document.querySelectorAll('.lang-toggle').forEach(el => {{
            if (el.getAttribute('data-lang') === (document.documentElement.getAttribute('data-lang') || 'zh')) {{
                el.classList.add('active');
            }}
        }});
    </script>
</body>
</html>
"""
    return html

def generate_index_page():
    """Generate the index page showing all 16 types."""
    html = """<!DOCTYPE html>
<html lang="zh" data-lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="HC-16 脆弱性图谱 — Non Dubito | 了解你的四个维度：驱动、尊严、自由、根基">
    <meta property="og:title" content="HC-16 · 脆弱性图谱 | Non Dubito">
    <meta property="og:description" content="16种人格脆弱性模式 — 驱动·尊严·自由·根基的交织">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://nondubito.net/hc16/">
    <meta name="canonical" href="https://nondubito.net/hc16/">
    <title>HC-16 脆弱性图谱 — Non Dubito</title>
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital@0;1&family=Inter:wght@400;500;600&family=Noto+Serif+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html {
            background: #0f0f0e;
            color: #f5f0e8;
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
        }
        
        [data-lang="en"] .lang-zh { display: none; }
        [data-lang="zh"] .lang-en { display: none; }
        
        body {
            background: #0f0f0e;
            color: #f5f0e8;
        }
        
        header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 70px;
            background: rgba(15, 15, 14, 0.95);
            border-bottom: 1px solid rgba(196, 157, 97, 0.2);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 40px;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        .header-logo {
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.1em;
            color: #c49d61;
        }
        
        .header-right {
            font-size: 12px;
            letter-spacing: 0.05em;
        }
        
        .lang-toggle {
            cursor: pointer;
            color: #999;
            transition: color 0.3s;
        }
        
        .lang-toggle:hover {
            color: #c49d61;
        }
        
        .lang-toggle.active {
            color: #c49d61;
        }
        
        main {
            margin-top: 70px;
            padding: 80px 40px;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .intro {
            max-width: 700px;
            margin-bottom: 60px;
        }
        
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 20px;
            color: #c49d61;
            letter-spacing: 0.05em;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: #999;
            margin-bottom: 20px;
            letter-spacing: 0.05em;
        }
        
        .intro-text {
            font-size: 1rem;
            line-height: 1.8;
            color: #d4cfc2;
            margin-bottom: 20px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 25px;
            margin-bottom: 60px;
        }
        
        .type-card {
            padding: 25px;
            background: rgba(196, 157, 97, 0.03);
            border: 1px solid rgba(196, 157, 97, 0.15);
            transition: all 0.3s ease;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            cursor: pointer;
        }
        
        .type-card:hover {
            background: rgba(196, 157, 97, 0.08);
            border-color: rgba(196, 157, 97, 0.4);
            transform: translateY(-3px);
        }
        
        .card-code {
            font-size: 1.8rem;
            font-weight: 700;
            color: #c49d61;
            margin-bottom: 10px;
            letter-spacing: 0.1em;
            font-family: 'Inter', monospace;
        }
        
        .card-name-zh {
            font-size: 1.3rem;
            font-weight: 700;
            font-family: 'Noto Serif SC', serif;
            margin-bottom: 8px;
            color: #f5f0e8;
        }
        
        .card-dims {
            font-size: 0.75rem;
            color: #999;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
            line-height: 1.4;
        }
        
        .card-tagline {
            font-size: 0.9rem;
            color: #ccc;
            line-height: 1.5;
            font-style: italic;
            margin-top: auto;
        }
        
        .cta {
            text-align: center;
            padding: 40px 0;
            border-top: 1px solid rgba(196, 157, 97, 0.2);
        }
        
        .cta-button {
            display: inline-block;
            padding: 15px 40px;
            background: #c49d61;
            color: #0f0f0e;
            text-decoration: none;
            font-weight: 600;
            letter-spacing: 0.05em;
            transition: background 0.3s;
        }
        
        .cta-button:hover {
            background: #e5c194;
        }
        
        @media (max-width: 1024px) {
            .grid {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            header {
                padding: 0 20px;
            }
            
            main {
                padding: 70px 20px 40px 20px;
            }
            
            h1 {
                font-size: 1.8rem;
            }
            
            .grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
            }
            
            .type-card {
                padding: 15px;
            }
            
            .card-code {
                font-size: 1.3rem;
            }
            
            .card-name-zh {
                font-size: 1rem;
            }
        }
        
        @media (max-width: 480px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-logo">HC-16</div>
        <div class="header-right">
            <span class="lang-toggle active" data-lang="zh" onclick="setLang('zh')">中文</span>
            <span style="margin: 0 8px; color: #666;">|</span>
            <span class="lang-toggle" data-lang="en" onclick="setLang('en')">EN</span>
        </div>
    </header>
    
    <main>
        <section class="intro">
            <h1 class="lang-zh">HC-16 脆弱性图谱</h1>
            <h1 class="lang-en">HC-16 Vulnerability Profile</h1>
            <p class="subtitle lang-zh">四个维度，十六种脆弱</p>
            <p class="subtitle lang-en">Four Dimensions, Sixteen Vulnerabilities</p>
            <p class="intro-text lang-zh">HC-16是一个人格脆弱性图谱系统，基于四个核心维度的组合：<strong>驱动·尊严·自由·根基</strong>。不是性格优劣的判断，而是对你感知模式和需求结构的深度理解。</p>
            <p class="intro-text lang-en">HC-16 is a vulnerability profile system based on the interplay of four core dimensions: <strong>Drive · Dignity · Autonomy · Base</strong>. Not a judgment of character, but a deep understanding of your perceptual patterns and need structure.</p>
        </section>
        
        <section class="grid">
"""
    
    # Add type cards
    for type_code in TYPE_CODES:
        type_data = TYPES[type_code]
        html += f"""            <a href="/hc16/{type_code}.html" class="type-card">
                <div class="card-code">{type_code}</div>
                <div class="card-name-zh lang-zh">{type_data['zh']}</div>
                <div class="card-dims">{type_data['en']}</div>
                <div class="card-tagline lang-zh">{type_data['tagline']}</div>
                <div class="card-tagline lang-en">{type_data['tagline_en']}</div>
            </a>
"""
    
    html += """        </section>
        
        <section class="cta">
            <p style="margin-bottom: 25px; color: #999;">
                <span class="lang-zh">发现你的脆弱性模式</span>
                <span class="lang-en">Discover your vulnerability pattern</span>
            </p>
            <a href="https://nondubito.net/" class="cta-button">
                <span class="lang-zh">→ 做一个测试</span>
                <span class="lang-en">→ Take the test</span>
            </a>
        </section>
    </main>
    
    <script>
        function setLang(lang) {
            document.documentElement.setAttribute('data-lang', lang);
            document.querySelectorAll('.lang-toggle').forEach(el => {
                el.classList.remove('active');
                if (el.getAttribute('data-lang') === lang) {
                    el.classList.add('active');
                }
            });
            localStorage.setItem('hc16_lang', lang);
        }
        
        // Load saved language preference
        const saved = localStorage.getItem('hc16_lang');
        if (saved) {
            setLang(saved);
        }
        
        // Update active toggle on load
        document.querySelectorAll('.lang-toggle').forEach(el => {
            if (el.getAttribute('data-lang') === (document.documentElement.getAttribute('data-lang') || 'zh')) {
                el.classList.add('active');
            }
        });
    </script>
</body>
</html>
"""
    return html

def main():
    """Main function to generate all pages."""
    output_dir = Path('/sessions/gracious-laughing-gates/mnt/nondubito/hc16')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate type pages
    for type_code in TYPE_CODES:
        type_data = TYPES[type_code]
        html = generate_type_page(type_code, type_data)
        output_file = output_dir / f'{type_code}.html'
        output_file.write_text(html, encoding='utf-8')
        print(f'Generated {type_code}.html')
    
    # Generate index page
    index_html = generate_index_page()
    index_file = output_dir / 'index.html'
    index_file.write_text(index_html, encoding='utf-8')
    print(f'Generated index.html')
    
    print(f'\nAll {len(TYPE_CODES) + 1} pages generated successfully!')

if __name__ == '__main__':
    main()
