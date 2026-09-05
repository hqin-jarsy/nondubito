/* Generated offline from essays/anime/puella-magi-madoka-magica/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《魔法少女小圆》解读":"《魔法少女小圓》解讀","《魔法少女小圆》让每一个愿望都真的实现。它最冷的地方不在奇迹失灵，而在愿望实现以后仍未解决的东西：签约者不知道自己该问什么，另一个人仍会按自己的生活行动，希望本身还会成为一套系统的原料。":"《魔法少女小圓》讓每一個願望都真的實現。它最冷的地方不在奇蹟失靈，而在願望實現以後仍未解決的東西：簽約者不知道自己該問什麼，另一個人仍會按自己的生活行動，希望本身還會成為一套系統的原料。","丘比把灵魂抽取称作效率改进；女孩们却发现，被归为可替换外壳的部分，正是她们一直生活其中的身体。":"丘比把靈魂抽取稱作效率改進；女孩們卻發現，被歸為可替換外殼的部分，正是她們一直生活其中的身體。","五篇从丘比那份“有问必答”的契约出发，读替别人许下的愿、被改造成战斗装置的灵魂、困在重复里的保护，以及小圆为什么最后改掉规则而不是赢下一次结果。":"五篇從丘比那份“有問必答”的契約出發，讀替別人許下的願、被改造成戰鬥裝置的靈魂、困在重複裡的保護，以及小圓為什麼最後改掉規則而不是贏下一次結果。","关键信息并非永远问不到；真正的不对称是，只有一方知道灵魂、魔女与契约终点这些问题本来就该被问。":"關鍵資訊並非永遠問不到；真正的不對稱是，只有一方知道靈魂、魔女與契約終點這些問題本來就該被問。","她一次次回到同一个月":"她一次次回到同一個月","她为别人许的":"她為別人許的","她改的是规则":"她改的是規則","她的灵魂在一块石头里":"她的靈魂在一塊石頭裡","手治好了，小提琴重新响起；愿望买不到另一个人的爱，也没有替付出者准备好付出之后的生活。":"手治好了，小提琴重新響起；願望買不到另一個人的愛，也沒有替付出者準備好付出之後的生活。","最后的愿望改掉的是希望坠成魔女的那一步，而不是悲痛、战斗、死亡或丘比本身。":"最後的願望改掉的是希望墜成魔女的那一步，而不是悲痛、戰鬥、死亡或丘比本身。","有问必答":"有問必答","焰记住事件、武器与路线，越来越能干；但每次尝试都会增加小圆的因果，让保护工程反过来放大它要阻止的危险。":"焰記住事件、武器與路線，越來越能幹；但每次嘗試都會增加小圓的因果，讓保護工程反過來放大它要阻止的危險。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这五篇沿着五份契约，辨认它们各自留下的责任。本系列只处理十二集电视动画；总集篇、《叛逆的物语》与后续作品不参与论证。含全剧剧透。":"這五篇沿著五份契約，辨認它們各自留下的責任。本系列只處理十二集電視動畫；總集篇、《叛逆的物語》與後續作品不參與論證。含全劇劇透。"};
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
