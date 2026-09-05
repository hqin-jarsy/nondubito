/* Generated offline from essays/literature/the-moon-and-the-bonfires/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《月亮和篝火》解读":"《月亮和篝火》解讀","一个人需要一个村子":"一個人需要一個村子","一个弃儿先成为孤儿院补贴，随后成为农场劳力；几十年后，金钱却买不回能为他绰号背后的生活作证的人。":"一個棄兒先成為孤兒院補貼，隨後成為農場勞力；幾十年後，金錢卻買不回能為他綽號背後的生活作證的人。","一场火让土地重生，一场烧毁无路可走的家庭，另一场则抹掉尸体，不让坟墓成为另一种记忆的起点。":"一場火讓土地重生，一場燒毀無路可走的家庭，另一場則抹掉屍體，不讓墳墓成為另一種記憶的起點。","他是一笔钱":"他是一筆錢","伊雷内服从，西尔维娅拒绝，桑塔进入战时政治；三条路显出的不是神秘命运，而是三种具体结构。":"伊雷內服從，西爾維婭拒絕，桑塔進入戰時政治；三條路顯出的不是神秘命運，而是三種具體結構。","切萨雷·帕韦泽《月亮和篝火》（La luna e i falò），一九五〇年出版。中文篇所用书名、人名、地名为作者自译。全书剧透。":"切薩雷·帕韋澤《月亮和篝火》（La luna e i falò），一九五〇年出版。中文篇所用書名、人名、地名為作者自譯。全書劇透。","四篇文章，从先被当成一笔钱、再被当成一双手的弃儿，到他需要却无法重新进入的村子、莫拉的三个女儿，以及三场意义完全不同的火。":"四篇文章，從先被當成一筆錢、再被當成一雙手的棄兒，到他需要卻無法重新進入的村子、莫拉的三個女兒，以及三場意義完全不同的火。","帕韦泽的最后一部长篇追问：当故乡主要活在那些会死亡、离散或沉默的人身上，回来意味着什么。这组文章追踪鳗鱼寻找见证的路，也追踪他还能递给另一个像自己的孩子的那点东西。":"帕韋澤的最後一部長篇追問：當故鄉主要活在那些會死亡、離散或沉默的人身上，回來意味著什麼。這組文章追蹤鰻魚尋找見證的路，也追蹤他還能遞給另一個像自己的孩子的那點東西。","最后一场篝火":"最後一場篝火","村子不是财产，而应在你不在时仍替你保存一点东西；鳗鱼回来才发现，完整保住任何东西都极其困难。":"村子不是財產，而應在你不在時仍替你保存一點東西；鰻魚回來才發現，完整保住任何東西都極其困難。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那三个女儿":"那三個女兒"};
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
