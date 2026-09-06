#!/usr/bin/env python3
"""Import the Simplified Chinese blockchain cycle essays as static pages.

The source files are editorial Markdown kept outside this repository.  This
script is intentionally narrow: it validates the 21-file series, applies a
small set of reviewed copy edits, and renders the published HTML pages.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "essays" / "blockchain"
SITE = "https://nondubito.net"
PUBLISHED = "2026-09-05"
CUTOFF = "2026 年 8 月"

ESSAYS = (
    (1, "披萨", "从一万枚比特币换两张披萨开始，追问价格、信任与链上结算之间从第一天就存在的距离。"),
    (2, "从 CPU 到矿场", "GPU、ASIC、矿池与预售矿机如何把人人可参与的计算，变成资本、能源与地理高度集中的产业。"),
    (3, "Mt. Gox", "Mt. Gox 的币如何在三年中持续外流：链验证了每一笔签名，却无法判断签名者是不是钥匙真正的主人。"),
    (4, "丝绸之路", "从托管、仲裁与评价机制重读丝绸之路：被排除在制度外的市场，如何重新造出一套私人制度。"),
    (5, "以太坊", "以太坊如何把世界计算机变成可以按 gas 计价的状态机，又把代码意图、治理和成本表留给人。"),
    (6, "The DAO", "The DAO 事件把代码执行、参与者意图、节点选择与市场命名拆成四套规则，也留下两条继续运行的链。"),
    (7, "ICO", "ERC-20 解决了代币怎样对接，却没有规定发行人为何可信；ICO 热潮把接口误当成了制度。"),
    (8, "稳定币的两条路", "法币储备与加密抵押两条稳定币路径，把一枚不生息的一美元背后的收益、风险与赎回权重新分配。"),
    (9, "AMM 与 DeFi Summer", "AMM 曲线、流动性挖矿与 DeFi Summer 如何创造自动交易，也把治理权、补贴和损失留在界面之外。"),
    (10, "预言机", "预言机让链接受外部价格，却无法让多数等于真实；数据源、节点与付费关系，把信任搬到了新的层次。"),
    (11, "清算", "从 Maker 的零出价拍卖到协议治理，追踪一次按规则完成的清算，如何让无法支付手续费的人承担全部损失。"),
    (12, "NFT", "NFT 精确记录谁持有代币，却不自动交付图像、版权、服务器或社群承诺；所有权因此被拆成多层。"),
    (13, "算力迁徙", "中国矿业整治之后，算力如何跨国迁徙；链能测量全网算力，却难以记录电价、岗位与地方承担的代价。"),
    (14, "萨尔瓦多", "萨尔瓦多的比特币实验，如何在法律、钱包、财政与实际使用之间产生四套不同的成功或失败口径。"),
    (15, "桥", "跨链桥没有让资产穿过链，而是让一条链接受另一条链的陈述；事故发生在两份可验证账本之间。"),
    (16, "Terra 与 Luna", "Terra 的铸销机制如何始终按规则兑现一美元名义价值，却在 LUNA 供应失控后失去实际赎回意义。"),
    (17, "FTX", "FTX 的权限、客户缺口、刑事损失与破产分配是四本不同的账；价格风险最终被固定在一个日期。"),
    (18, "The Merge", "The Merge 替换了共识机制并大幅降低链上能耗，同时把集中度、MEV 与审查问题搬到质押和区块构建层。"),
    (19, "L2", "L2 的正确性、控制权与现金流是三条彼此独立的轴；把它们合成“继承以太坊安全”会抹掉关键差异。"),
    (20, "真实世界资产", "真实世界资产把基金份额搬上链，也把身份、托管、更正与法律请求权重新请回了结算系统。"),
    (21, "今天", "资料截至 2026 年 8 月：用五套稳定币口径、跨境成本实验与三个赔付案例，盘点链能量到什么、仍量不到什么。"),
)

GROUPS = (
    ("账本进入世界", "从一笔披萨交易开始，技术第一次碰到价格、机器、托管与地下市场。", range(1, 5)),
    ("可编程金融", "代码开始承载组织、融资、货币、交易、价格、清算与所有权。", range(5, 13)),
    ("代价与崩塌", "算力、国家、跨链与中心化机构，让账本之外的承担者重新出现。", range(13, 18)),
    ("重新进入制度", "共识、扩容与现实资产，把问题带回能源、治理、法律与人的判断。", range(18, 22)),
)

COPY_EDITS = {
    "而这个涨幅落在破产财团那一侧;分给债权人的,是按低点固定下来的债权,再加上利息。而这个涨幅在破产的账上,归的是财团;分给债权人的,是按低点固定下来的债权,再加上利息。":
        "而这个涨幅落在破产财团那一侧；分给债权人的，是按低点固定下来的债权，再加上利息。",
    "同一段时间里,以太坊出了约 580 个时隙,一个也没有少,一个也没有错。":
        "同一段时间里，以太坊的一层仍持续产生时隙；约 580 个时隙没有解决二层无法出块的问题。",
    "那条链从 2009 年 1 月 3 日到今天,一个块也没有少出,一次也没有算错过。第五篇写的那一条,从 2015 年 7 月 30 日那个只有 5,000 gas 的区块开始,现在每 12 秒一个时隙,同样没有停过。":
        "从 2009 年 1 月 3 日到本文资料截点，比特币主链持续出块；第五篇写的那条链，从 2015 年 7 月 30 日那个只有 5,000 gas 的区块开始，在合并之后也继续运行。",
    "链记的是数量,地址,时间和签名。这四样它记得毫无差错,十六年一次也没有错过。":
        "链记的是数量、地址、时间和签名，并按协议验证这些记录。",
}


def normalize_text(value: str) -> str:
    for old, new in COPY_EDITS.items():
        value = value.replace(old, new)
    value = re.sub(
        r",",
        lambda match: ","
        if match.start() > 0
        and match.end() < len(value)
        and value[match.start() - 1].isdigit()
        and value[match.end()].isdigit()
        else "，",
        value,
    )
    value = value.replace(";", "；").replace(":", "：")
    value = value.replace("?", "？").replace("!", "！")
    value = re.sub(r"(?<=年) (?=\d)", "", value)
    value = re.sub(r"(?<=月) (?=\d)", "", value)
    return value.strip()


def inline_markup(value: str) -> str:
    escaped = html.escape(normalize_text(value), quote=False)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", escaped)
    escaped = re.sub(r"`([^`]+?)`", r"<code>\1</code>", escaped)
    return escaped


def parse_markdown(path: Path) -> tuple[str, list[tuple[str, list[str]]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"{path.name}: missing H1")
    h1 = normalize_text(lines[0][2:])
    sections: list[tuple[str, list[str]]] = []
    heading: str | None = None
    paragraphs: list[str] = []
    buffer: list[str] = []

    def flush_paragraph() -> None:
        nonlocal buffer
        if buffer:
            paragraphs.append(" ".join(part.strip() for part in buffer))
            buffer = []

    def flush_section() -> None:
        if heading is not None:
            flush_paragraph()
            sections.append((heading, list(paragraphs)))
            paragraphs.clear()

    for raw in lines[1:]:
        if raw.startswith("## "):
            flush_section()
            heading = normalize_text(raw[3:])
        elif not raw.strip():
            flush_paragraph()
        else:
            buffer.append(raw)
    flush_section()
    if len(sections) != 8:
        raise ValueError(f"{path.name}: expected 8 sections, found {len(sections)}")
    return h1, sections


def site_header(depth: int = 2) -> str:
    prefix = "../" * depth
    return f'''<a class="skip-link" href="#main-content">跳到正文</a>
  <header class="blockchain-site-header">
    <div class="blockchain-header-inner">
      <a class="blockchain-brand" href="{prefix}index.html" aria-label="Non Dubito 首页"><span>NON</span><span>DUBITO</span></a>
      <nav class="blockchain-primary-nav" aria-label="主导航">
        <a href="{prefix}start.html">从这里开始</a>
        <a href="{prefix}explore.html">探索</a>
        <a href="{prefix}latest.html">最近更新</a>
        <a href="{prefix}library.html">书库</a>
        <a href="{prefix}about.html">关于</a>
      </nav>
      <div class="blockchain-header-tools"><a href="{prefix}search.html">搜索</a><span>简体中文</span></div>
    </div>
  </header>'''


def head(*, title: str, description: str, canonical: str, page_type: str) -> str:
    title_full = f"{title} — Non Dubito"
    structured_type = "article" if page_type == "article" else "website"
    return f'''<meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title_full)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <meta name="author" content="Han Qin (秦汉)">
  <meta property="og:title" content="{html.escape(title, quote=True)}">
  <meta property="og:description" content="{html.escape(description, quote=True)}">
  <meta property="og:type" content="{structured_type}">
  <meta property="og:locale" content="zh_CN">
  <meta property="og:url" content="{canonical}">
  <meta name="twitter:card" content="summary">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../style.css">
  <link rel="stylesheet" href="../../reading-context.css?v=20260905a">
  <link rel="stylesheet" href="blockchain.css?v=20260905a">'''


def breadcrumbs(current: str) -> str:
    return f'''<nav class="reading-breadcrumbs" aria-label="面包屑导航">
      <a href="../../explore.html#history">历史、权力与文明</a><span aria-hidden="true">/</span>
      <a href="index.html">凿构周期律：区块链</a><span aria-hidden="true">/</span>
      <span aria-current="page">{html.escape(current)}</span>
    </nav>'''


def article_json_ld(number: int, title: str, description: str) -> str:
    url = f"{SITE}/essays/blockchain/ep{number:02d}.html"
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "inLanguage": "zh-Hans",
        "author": {"@type": "Person", "name": "Han Qin (秦汉)"},
        "datePublished": PUBLISHED,
        "dateModified": PUBLISHED,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "isPartOf": {
            "@type": "CreativeWorkSeries",
            "name": "凿构周期律：区块链",
            "url": f"{SITE}/essays/blockchain/",
        },
        "position": number,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def footer() -> str:
    return '''<footer class="blockchain-footer"><div><a href="../../index.html" class="blockchain-brand"><span>NON</span><span>DUBITO</span></a><p>Essays in the Self-as-an-End Tradition</p></div><nav aria-label="页脚导航"><a href="../../explore.html">探索</a><a href="../../latest.html">最近更新</a><a href="../../library.html">完整书库</a><a href="../../about.html">关于</a></nav></footer>'''


def render_article(source: Path, number: int, title: str, description: str) -> str:
    source_h1, sections = parse_markdown(source)
    if title not in source_h1:
        raise ValueError(f"{source.name}: title mismatch ({source_h1!r})")
    canonical = f"{SITE}/essays/blockchain/ep{number:02d}.html"
    toc = "\n".join(
        f'          <li><a href="#section-{index}">{inline_markup(section_title)}</a></li>'
        for index, (section_title, _) in enumerate(sections, 1)
    )
    body_parts: list[str] = []
    for index, (section_title, paragraphs) in enumerate(sections, 1):
        body_parts.append(f'        <h2 id="section-{index}">{inline_markup(section_title)}</h2>')
        for paragraph_index, paragraph in enumerate(paragraphs):
            css = ' class="opening"' if index == 1 and paragraph_index == 0 else ""
            body_parts.append(f"        <p{css}>{inline_markup(paragraph)}</p>")
    body = "\n".join(body_parts)

    previous_link = (
        f'<a class="page-turn previous" href="ep{number - 1:02d}.html"><span>上一篇</span><strong>{html.escape(ESSAYS[number - 2][1])}</strong></a>'
        if number > 1 else
        '<a class="page-turn previous" href="index.html"><span>返回</span><strong>系列首页</strong></a>'
    )
    next_link = (
        f'<a class="page-turn next" href="ep{number + 1:02d}.html"><span>下一篇</span><strong>{html.escape(ESSAYS[number][1])}</strong></a>'
        if number < len(ESSAYS) else
        '<a class="page-turn next" href="index.html"><span>读完以后</span><strong>返回系列首页</strong></a>'
    )
    cutoff_note = '<p class="article-cutoff">资料截至 2026 年 8 月</p>' if number == 21 else ""

    return f'''<!DOCTYPE html>
<html lang="zh-Hans">
<head>
  {head(title=f"{title}｜凿构周期律：区块链 {number:02d}", description=description, canonical=canonical, page_type="article")}
  <meta property="article:published_time" content="{PUBLISHED}">
  <meta property="article:modified_time" content="{PUBLISHED}">
  <script type="application/ld+json">{article_json_ld(number, title, description)}</script>
</head>
<body class="blockchain-page blockchain-article-page">
  {site_header()}
  <main id="main-content" class="blockchain-main">
    {breadcrumbs(f"{number:02d} · {title}")}
    <header class="blockchain-article-header">
      <p class="article-kicker">凿构周期律 · 区块链系列 <span class="article-number">{number:02d} / {len(ESSAYS):02d}</span></p>
      <h1>{html.escape(title)}</h1>
      <p class="article-deck">{html.escape(description)}</p>
      {cutoff_note}
      <p class="article-byline">秦汉 · 2026 年 9 月 5 日</p>
    </header>
    <div class="blockchain-article-layout">
      <aside class="chapter-aside">
        <nav aria-label="本篇目录"><p>本篇目录</p><ol>
{toc}
        </ol></nav>
      </aside>
      <article class="essay-body" data-search="区块链 比特币 以太坊 凿构周期律">
{body}
        <div class="source-note"><strong>资料说明</strong><p>本文依据公开协议文档、链上记录、法院文书、监管文件与同行评议研究写成；文中的数字均保留其统计口径。系列资料截至 {CUTOFF}。</p></div>
      </article>
    </div>
    <nav class="article-nav series-pagination" aria-label="系列篇章导航">{previous_link}<a class="page-turn series-home" href="index.html"><span>全部篇章</span><strong>21 篇目录</strong></a>{next_link}</nav>
    <section class="reading-routes" aria-labelledby="continue-reading"><p class="route-kicker">Where next</p><h2 id="continue-reading">沿着问题继续读</h2><div class="reading-next-grid"><a href="{f'ep{number + 1:02d}.html' if number < len(ESSAYS) else 'index.html'}"><span>沿本系列继续</span><strong>{html.escape(ESSAYS[number][1]) if number < len(ESSAYS) else '回看二十一篇的完整路径'}</strong><small>从这一处结算边界，走向下一次构成。</small></a><a href="../economy/index.html"><span>回到周期律</span><strong>凿构周期律：经济</strong><small>看扩张、固化、断裂与重构怎样在更长时间里发生。</small></a><a href="../../explore.html#history"><span>换一个入口</span><strong>历史、权力与文明</strong><small>从制度、人物与文明结构继续探索。</small></a></div></section>
  </main>
  {footer()}
</body>
</html>
'''


def index_json_ld() -> str:
    items = [
        {
            "@type": "ListItem",
            "position": number,
            "url": f"{SITE}/essays/blockchain/ep{number:02d}.html",
            "name": title,
        }
        for number, title, _ in ESSAYS
    ]
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "凿构周期律：区块链",
        "description": "二十一篇追踪区块链从比特币披萨、挖矿与交易所，走到稳定币、跨链桥、L2 与真实世界资产。",
        "url": f"{SITE}/essays/blockchain/",
        "inLanguage": "zh-Hans",
        "author": {"@type": "Person", "name": "Han Qin (秦汉)"},
        "datePublished": PUBLISHED,
        "dateModified": PUBLISHED,
        "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items},
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_index() -> str:
    description = "二十一篇从比特币披萨、挖矿与交易所，走到稳定币、跨链桥、L2 与真实世界资产，追问链能精确结算什么，又把什么留在账外。"
    groups: list[str] = []
    for group_number, (name, deck, numbers) in enumerate(GROUPS, 1):
        cards = []
        for number in numbers:
            _, title, essay_description = ESSAYS[number - 1]
            cards.append(f'''          <a class="blockchain-card" href="ep{number:02d}.html"><span class="card-number">{number:02d}</span><div><h3>{html.escape(title)}</h3><p>{html.escape(essay_description)}</p></div><span class="card-arrow" aria-hidden="true">→</span></a>''')
        groups.append(f'''      <section class="blockchain-group" aria-labelledby="group-{group_number}"><header><p>{group_number:02d}</p><div><h2 id="group-{group_number}">{name}</h2><p>{deck}</p></div></header><div class="blockchain-card-grid">
{chr(10).join(cards)}
        </div></section>''')
    canonical = f"{SITE}/essays/blockchain/"
    return f'''<!DOCTYPE html>
<html lang="zh-Hans">
<head>
  {head(title="凿构周期律：区块链", description=description, canonical=canonical, page_type="website")}
  <script type="application/ld+json">{index_json_ld()}</script>
</head>
<body class="blockchain-page blockchain-index-page">
  {site_header()}
  <main id="main-content" class="blockchain-main">
    <nav class="reading-breadcrumbs" aria-label="面包屑导航"><a href="../../explore.html#history">历史、权力与文明</a><span aria-hidden="true">/</span><span aria-current="page">凿构周期律：区块链</span></nav>
    <section class="blockchain-hero">
      <p class="article-kicker">The Chisel–Construct Cycle · 21 Essays</p>
      <h1>凿构周期律：区块链</h1>
      <p class="blockchain-refrain">链还在结算，而结算什么还没有共识。</p>
      <p class="blockchain-intro">{description}</p>
      <div class="blockchain-series-meta"><span>21 篇</span><span>168 节</span><span>资料截至 {CUTOFF}</span><span>简体中文</span></div>
      <a class="start-series" href="ep01.html"><span>从第一篇开始</span><strong>一万枚比特币与两张披萨 →</strong></a>
    </section>
    <section class="blockchain-reading-note"><p class="note-label">怎样进入这个系列</p><h2>不是一部技术编年史，而是一条不断移动的边界。</h2><div><p>每篇从一件可以核对的事件开始：一笔交易、一次故障、一项法律、一次清算。问题不只是技术有没有按规则工作，而是规则精确写下了什么，又把哪些代价、责任和判断留给了人。</p><p>你可以顺序阅读，看同一个循环在十六年里一次次重来；也可以从熟悉的节点进入。每一篇都有八节目录，并能回到完整路径。</p></div></section>
{chr(10).join(groups)}
    <section class="blockchain-language-note"><p>当前发布的是简体中文原版。未来若增加其他语言，将采用各自独立的 URL，不让同一地址随界面语言改变正文。</p></section>
    <section class="reading-routes" aria-labelledby="continue-reading"><p class="route-kicker">Continue exploring</p><h2 id="continue-reading">把账本放回更大的历史里</h2><div class="reading-next-grid"><a href="../economy/index.html"><span>相邻系列</span><strong>凿构周期律：经济</strong><small>把同一循环放回更长的制度时间。</small></a><a href="../athletics/index.html"><span>另一种测量</span><strong>凿构周期律：田径</strong><small>看数字怎样精确记录成绩，也改变人的训练与竞争。</small></a><a href="../../explore.html#history"><span>主题入口</span><strong>历史、权力与文明</strong><small>浏览制度、人物与文明结构。</small></a></div></section>
  </main>
  {footer()}
</body>
</html>
'''


def source_files(source_dir: Path) -> dict[int, Path]:
    found: dict[int, Path] = {}
    for path in source_dir.glob("*.md"):
        match = re.search(r"_(\d{2})_", path.name)
        if match:
            found[int(match.group(1))] = path
    expected = set(range(1, len(ESSAYS) + 1))
    if set(found) != expected:
        raise ValueError(f"source sequence mismatch: missing={sorted(expected - set(found))}, extra={sorted(set(found) - expected)}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="directory containing the 21 Markdown source files")
    args = parser.parse_args()
    files = source_files(args.source)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "index.html").write_text(render_index(), encoding="utf-8")
    for number, title, description in ESSAYS:
        output = OUTPUT / f"ep{number:02d}.html"
        output.write_text(render_article(files[number], number, title, description), encoding="utf-8")
    print(f"Wrote {len(ESSAYS) + 1} blockchain series pages to {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
