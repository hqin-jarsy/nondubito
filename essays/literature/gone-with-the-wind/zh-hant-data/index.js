/* Generated offline from essays/literature/gone-with-the-wind/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《飘》解读":"《飄》解讀","四篇文章，从斯佳丽被培养成什么、塔拉的饥饿如何拆掉她那套算法的边界，到她为何始终看不懂玫兰妮。":"四篇文章，從斯佳麗被培養成什麼、塔拉的飢餓如何拆掉她那套演算法的邊界，到她為何始終看不懂玫蘭妮。","塔拉的饥饿没有发明斯佳丽使用他人的算法，而是拆掉了它原本只限于调情与婚姻的边界。":"塔拉的飢餓沒有發明斯佳麗使用他人的演算法，而是拆掉了它原本只限於調情與婚姻的邊界。","她一直看错了一个人":"她一直看錯了一個人","她的计算保住了塔拉、养活了一家人；同一种精确，也把妹妹、丈夫与囚犯劳工变成账目。":"她的計算保住了塔拉、養活了一家人；同一種精確，也把妹妹、丈夫與囚犯勞工變成賬目。","她算得没有错":"她算得沒有錯","她被养成什么":"她被養成什麼","她记住了那个饿":"她記住了那個餓","斯佳丽学会了婚姻市场的全部技术；小说写活了嬷嬷的温情，却从未追问嬷嬷自己的目的。":"斯佳麗學會了婚姻市場的全部技術；小說寫活了嬤嬤的溫情，卻從未追問嬤嬤自己的目的。","斯佳丽把玫兰妮不求回报的忠诚误认成愚蠢，直到最后才发现那个“弱者”一直撑着她的生活。":"斯佳麗把玫蘭妮不求回報的忠誠誤認成愚蠢，直到最後才發現那個“弱者”一直撐著她的生活。","玛格丽特·米切尔《飘》，一九三六年出版。全书剧透。":"瑪格麗特·米切爾《飄》，一九三六年出版。全書劇透。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这个系列把斯佳丽惊人的求生能力和她把他人工具化的方式放在同一画面里，也正面处理小说对种植园秩序、种族主义形象、重建时期与“失落事业”叙事的局限。":"這個系列把斯佳麗驚人的求生能力和她把他人工具化的方式放在同一畫面裡，也正面處理小說對種植園秩序、種族主義形象、重建時期與“失落事業”敘事的侷限。"};
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
