/* Generated offline from essays/film/schindlers-list/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《辛德勒的名单》解读":"《辛德勒的名單》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一个投机商可以被移作他用的本事，读到一份名单如何借采购语言救人，以及那些最终走出电影、亲手在辛德勒墓前放下石头的幸存者。":"三篇從一個投機商可以被移作他用的本事，讀到一份名單如何藉由採購語言救人，以及那些最終走出電影、親手在辛德勒墓前放下石頭的倖存者。","《辛德勒的名单》没有从圣人开始，而是从一个把纳粹党徽别上翻领的推销者开始：因为那枚徽章能打开房门。他的钱、魅力、礼物，以及把陌生人迅速变成人脉的能力，最初都服务于利润。电影最困难也最准确的地方，是不要求这些能力先变得纯洁，才允许它们被用于不同目的。":"《辛德勒的名單》沒有從聖人開始，而是從一個把納粹黨徽別上翻領的推銷者開始：因為那枚徽章能打開房門。他的錢、魅力、禮物，以及把陌生人迅速變成人脈的能力，最初都服務於利潤。電影最困難也最準確的地方，是不要求這些能力先變得純潔，才允許它們被用於不同目的。","这三篇沿着这次反转前进，却不把它写成一份简单的赎罪故事。它追问同一笔钱从购买优势转向购买保护时究竟改变了什么；为什么身处杀戮官僚体系的救援者，有时只能先把人登记成有用财产；以及最后的彩色段落如何拒绝把一千多段生命压成衡量一个人伟大的数字。":"這三篇沿著這次反轉前進，卻不把它寫成一份簡單的贖罪故事。它追問同一筆錢從購買優勢轉向購買保護時究竟改變了什麼；為什麼身處殺戮官僚體系的救援者，有時只能先把人登記成有用財產；以及最後的彩色段落如何拒絕把一千多段生命壓成衡量一個人偉大的數字。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他一开始要的就是钱":"他一開始要的就是錢","辛德勒以战争投机商开始；最初把占领变成机会的社交本事，后来成为他保护具体生命的手段。":"辛德勒以戰爭投機商開始；最初把佔領變成機會的社交本事，後來成為他保護具體生命的手段。","英 · 简 · 繁":"英 · 簡 · 繁","那份名单是一张采购清单":"那份名單是一張採購清單","电影里的名单用纳粹行政唯一肯处理的范畴救人：价格、技能、产量与文书；名字必须先被翻译成用途。":"電影裡的名單用納粹行政唯一肯處理的範疇救人：價格、技能、產量與文書；名字必須先被翻譯成用途。","那些放石头的人":"那些放石頭的人","辛德勒最后的算术不只是愧疚。电影让幸存者走进画面，把英雄功绩的总数重新展开为一段段完整人生。":"辛德勒最後的算術不只是愧疚。電影讓倖存者走進畫面，把英雄功績的總數重新展開為一段段完整人生。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
