/* Generated offline from essays/games/celeste/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Game criticism":"English · 簡 / 繁 · Game criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與交互敘事","《蔚蓝》用一部高难度平台游戏，耐心地写焦虑：失败被如实记录，却没有终审权；帮助可以改变走法，却不替人规定标准；那个令人害怕的自己既不必服从，也无法靠消灭解决。四篇把机制与故事放在一起读，也保留作品不肯被一句漂亮道理收平的地方。":"《蔚藍》用一部高難度平台遊戲，耐心地寫焦慮：失敗被如實記錄，卻沒有終審權；幫助可以改變走法，卻不替人規定標準；那個令人害怕的自己既不必服從，也無法靠消滅解決。四篇把機制與故事放在一起讀，也保留作品不肯被一句漂亮道理收平的地方。","《蔚蓝》解读":"《蔚藍》解讀","四篇从一次说不清原因的登山、一个拿真实材料作出过度推论的声音，读到两种帮助，以及并不消灭分歧的自我接纳。":"四篇從一次說不清原因的登山、一個拿真實材料作出過度推論的聲音，讀到兩種幫助，以及並不消滅分歧的自我接納。","奥希罗和希欧":"奧希羅和希歐","她说不出为什么":"她說不出為什麼","她说的都是真的":"她說的都是真的","接纳没有让芭德琳闭嘴，也没有让山变矮；它让两个仍有分歧的声音把力气用在同一边。":"接納沒有讓芭德琳閉嘴，也沒有讓山變矮；它讓兩個仍有分歧的聲音把力氣用在同一邊。","替人打扫废墟可能加固他的房间；一片呼吸中的羽毛，却能成为对方自己带走的帮助。":"替人打掃廢墟可能加固他的房間；一片呼吸中的羽毛，卻能成為對方自己帶走的幫助。","玛德琳的行动走在解释前面；蔚蓝山显出她带来的东西，却不承诺替她治好。":"瑪德琳的行動走在解釋前面；蔚藍山顯出她帶來的東西，卻不承諾替她治好。","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","芭德琳用真实证据作出过度判决，而快速重来让每一次失败只能说明它自己。":"芭德琳用真實證據作出過度判決，而快速重來讓每一次失敗只能說明它自己。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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
