/* Generated offline from essays/literature/brave-new-world/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","《美丽新世界》解读":"《美麗新世界》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","四篇文章，从被制造的欲望、苏麻、两种异类与“不幸福的权利”，重读一个让人自愿安居其位的世界。":"四篇文章，從被製造的慾望、蘇麻、兩種異類與“不幸福的權利”，重讀一個讓人自願安居其位的世界。","世界国并非没有强制：它禁书、限制科学、设定儿童的反应，并把不合群者流放到岛上。它真正特殊的成就是让公开暴力退居次位；生物工程、消费、性、娱乐与苏麻共同运作，使大多数人主动喜欢被预先分配的位置。":"世界國並非沒有強制：它禁書、限制科學、設定兒童的反應，並把不合群者流放到島上。它真正特殊的成就是讓公開暴力退居次位；生物工程、消費、性、娛樂與蘇麻共同運作，使大多數人主動喜歡被預先分配的位置。","赫胥黎的问题因此不只是“幸福好不好”，而是：当一个人想要别种生活的能力已被提前设计，这种幸福还意味着什么？四篇文章从孵化中心一路读到约翰对困难、责任与未被安排之价值的要求。":"赫胥黎的問題因此不只是“幸福好不好”，而是：當一個人想要別種生活的能力已被提前設計，這種幸福還意味著什麼？四篇文章從孵化中心一路讀到約翰對困難、責任與未被安排之價值的要求。","奥尔德斯·赫胥黎《美丽新世界》。全书剧透。":"阿道斯·赫胥黎《美麗新世界》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他们被制造出来喜欢自己的位置":"他們被製造出來喜歡自己的位置","世界国不只分配等级，还制造让这种分配显得自然的偏好。":"世界國不只分配等級，還製造讓這種分配顯得自然的偏好。","英 · 简 · 繁":"英 · 簡 · 繁","吃一克苏麻，问题就消失了":"吃一克蘇麻，問題就消失了","苏麻不回答悲伤与冲突；它让那个本会追问答案的人暂时消失。":"蘇麻不回答悲傷與衝突；它讓那個本會追問答案的人暫時消失。","一个人想进去，一个人格格不入":"一個人想進去，一個人格格不入","伯纳德的怨恨要的是体制内地位；赫姆霍尔兹过剩的能力却把他推向体制语言之外。":"伯納德的怨恨要的是體制內地位；赫姆霍爾茲過剩的能力卻把他推向體制語言之外。","他要求拥有那些坏东西的权利":"他要求擁有那些壞東西的權利","约翰要求“不幸福的权利”，其实是在要求承担一段自己能够认领之生活的未规划代价。":"約翰要求“不幸福的權利”，其實是在要求承擔一段自己能夠認領之生活的未規劃代價。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
