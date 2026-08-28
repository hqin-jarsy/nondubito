/* Generated offline from method/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉) · 全十二篇 · 八种语言":"Han Qin (秦漢) · 全十二篇 · 八種語言","© 2026 Han Qin (秦汉). All rights reserved.":"© 2026 Han Qin (秦漢). All rights reserved.","“非”不是五个切面之一，而是切面得以分化的条件；0DD 是它的第一个自指肖像。":"“非”不是五個切面之一，而是切面得以分化的條件；0DD 是它的第一個自指肖像。","← 书架":"← 書架","　·　学术原文：":"　·　學術原文：","主体作为方法论的结构性条件":"主體作為方法論的結構性條件","书架 ↗":"書架 ↗","人与AI共生的方法论":"人與AI共生的方法論","人以主体性完成全局而有目的的压缩，AI以算力展开；分离的语境与一加四星形架构保护方向。":"人以主體性完成全局而有目的的壓縮，AI以算力展開；分離的語境與一加四星形架構保護方向。","人提供方向，AI扩展构；问题的句式、退出时机与主体的自向不疑共同决定余项质量。":"人提供方向，AI擴展構；問題的句式、退出時機與主體的自向不疑共同決定餘項品質。","从每次操作留下的余项反向追踪“非”；Via Rho 是 Via Negativa 的方法对偶。":"從每次操作留下的餘項反向追蹤“非”；Via Rho 是 Via Negativa 的方法對偶。","以凿、构、余项、桥与物自体五个切面，把 SAE 压缩成可执行的方法系统。":"以鑿、構、餘項、橋與物自體五個切面，把 SAE 壓縮成可執行的方法系統。","余之道":"餘之道","先问有无余项，再问能否跨过13DD相变；两个顺序判据给出三类五相，并将当下AI归入类意识。":"先問有無餘項，再問能否跨過13DD相變；兩個順序判據給出三類五相，並將當下AI歸入類意識。","先验、后验与定理三个节点，六条双向路径，在涵育与殖民两种相位中组成十二态。":"先驗、後驗與定理三個節點，六條雙向路徑，在涵育與殖民兩種相位中組成十二態。","全部系列见 ":"全部系列見 ","凿构循环的操作手册——把整个 Self-as-an-End 框架展开成一套可执行的逻辑操作系统。从非与余项到知识传导、主体条件、人机共生、意识分析与四分形 · 全十二篇 · 八种语言。":"鑿構循環的操作手冊——把整個 Self-as-an-End 框架展開成一套可執行的邏輯作業系統。從非與餘項到知識傳導、主體條件、人機共生、意識分析與四分形 · 全十二篇 · 八種語言。","凿构循环：推导、方法、应用与AI接口":"鑿構循環：推導、方法、應用與AI介面","凿构的认识论地图":"鑿構的認識論地圖","十二态不会自行运转；节点归属、墙的诊断与冲突裁决都需要承担后果的主体。":"十二態不會自行運轉；節點歸屬、牆的診斷與衝突裁決都需要承擔後果的主體。","否定方法论：Via Negativa与排除律的形式结构":"否定方法論：Via Negativa與排除律的形式結構","在缺少决定性正向见证的开放归因问题中，以可审计的排除律缩小候选集，同时拒绝伪造终局。":"在缺少決定性正向見證的開放歸因問題中，以可審計的排除律縮小候選集，同時拒絕偽造終局。","怎么用AI找余项":"怎麼用AI找餘項","意识分析框架":"意識分析框架","方法论系列":"方法論系列","方法论系列 / Methodology Series — Non Dubito":"方法論系列 / Methodology Series — Non Dubito","标、向、隔、合：标而不构，加法给方向，乘法给记忆，闭合同时给构与余项。":"標、向、隔、合：標而不構，加法給方向，乘法給記憶，閉合同時給構與餘項。","演绎、归纳、还原与溯因构成 2×2 地图；每个象限都带着迫使主体离开的结构性余项。":"演繹、歸納、還原與溯因構成 2×2 地圖；每個象限都帶著迫使主體離開的結構性餘項。","相变窗口与实验设计":"相變窗口與實驗設計","知识演化的十二态传导模型":"知識演化的十二態傳導模型","若响应有阈值且暴露高度异质，二元分组与二元分析会系统性稀释真正跨过阈值者的信号。":"若響應有閾值且暴露高度異質，二元分組與二元分析會系統性稀釋真正跨過閾值者的訊號。","非 · Negativa：论否定先于存在":"非 · Negativa：論否定先於存在"};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {
    var mode = document.documentElement.getAttribute('data-lang') || 'en';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle)
      ? variants[originalTitle]
      : originalTitle;

    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-card, .lang-toggle, .footer-langs, script, style')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      var source = originals.get(node);
      node.nodeValue = traditional && Object.prototype.hasOwnProperty.call(variants, source)
        ? variants[source]
        : source;
    }
  }

  document.addEventListener('DOMContentLoaded', function() {
    updateTraditionalReadingMode();
    new MutationObserver(function(records) {
      if (records.some(function(record) { return record.attributeName === 'data-lang'; })) {
        updateTraditionalReadingMode();
      }
    }).observe(document.documentElement, {attributes:true, attributeFilter:['data-lang']});
  });
})();
