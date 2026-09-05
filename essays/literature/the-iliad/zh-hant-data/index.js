/* Generated offline from essays/literature/the-iliad/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《伊利亚特》不是披着古代外衣的现代道德课。它把彼此不相容的要求并排放着：荣誉与生存、复仇与裁断、英雄之名与只能在盾牌上看见的日常生活。这组文章停留在这些碰撞里。":"《伊利亞特》不是披著古代外衣的現代道德課。它把彼此不相容的要求並排放著：榮譽與生存、復仇與裁斷、英雄之名與只能在盾牌上看見的日常生活。這組文章停留在這些碰撞裡。","《伊利亚特》解读":"《伊利亞特》解讀","四篇文章，从无法为生命定价的礼单、赫克托尔所依赖的目光，到阿基琉斯盾牌上的法庭，以及普里阿摩斯为悲痛争取到的十二天。":"四篇文章，從無法為生命定價的禮單、赫克托爾所依賴的目光，到阿基琉斯盾牌上的法庭，以及普里阿摩斯為悲痛爭取到的十二天。","城门外的那双眼睛":"城門外的那雙眼睛","普里阿摩斯亲吻杀死儿子的手；史诗抵达的不是宽恕，而是一顿饭、一具归还的尸体和十二天葬期。":"普里阿摩斯親吻殺死兒子的手；史詩抵達的不是寬恕，而是一頓飯、一具歸還的屍體和十二天葬期。","本文依据罗念生、王焕生译本（人民文学出版社），人名地名从该本。另有陈中梅译本通行。全诗剧透。":"本文依據羅念生、王煥生譯本（人民文學出版社），人名地名從該本。另有陳中梅譯本通行。全詩劇透。","杀人之后仍可不再杀人的法庭，被打在最不愿走这条路的阿基琉斯所持的盾牌上。":"殺人之後仍可不再殺人的法庭，被打在最不願走這條路的阿基琉斯所持的盾牌上。","盾牌上的那场官司":"盾牌上的那場官司","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","赫克托尔的法确实属于他自己，却需要一群目光才能成立；最后让他停止逃跑的目光，偏偏是神造出的假象。":"赫克托爾的法確實屬於他自己，卻需要一群目光才能成立；最後讓他停止逃跑的目光，偏偏是神造出的假象。","那份礼单":"那份禮單","阿伽门农的厚礼之所以失败，是因为阿基琉斯已经从分配公平，走到了生命根本不能进入价目表。":"阿伽門農的厚禮之所以失敗，是因為阿基琉斯已經從分配公平，走到了生命根本不能進入價目表。"};
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
