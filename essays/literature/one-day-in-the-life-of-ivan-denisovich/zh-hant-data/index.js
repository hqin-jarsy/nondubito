/* Generated offline from essays/literature/one-day-in-the-life-of-ivan-denisovich/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《伊凡·杰尼索维奇的一天》解读":"《伊凡·傑尼索維奇的一天》解讀","一份没有具体罪行的口供，让形式取代了调查；舒霍夫交出关于自己是谁的官方说法，换回继续活着的时间。":"一份沒有具體罪行的口供，讓形式取代了調查；舒霍夫交出關於自己是誰的官方說法，換回繼續活著的時間。","三篇文章，从那份被填出来的口供、舒霍夫不能放下的墙，到集中营里一笔一笔结清、却仍有东西不入账的生活。":"三篇文章，從那份被填出來的口供、舒霍夫不能放下的牆，到集中營裡一筆一筆結清、卻仍有東西不入賬的生活。","他签了字":"他簽了字","本文依据斯人译本（人民文学出版社）。另有姜明河译本（群众出版社，译林新版）通行。全书剧透。":"本文依據斯人譯本（人民文學出版社）。另有姜明河譯本（群眾出版社，譯林新版）通行。全書劇透。","系列 · 三篇解读 · 文学评论":"系列 · 三篇解讀 · 文學評論","索尔仁尼琴把十年的强制压进一个普通的冬日。小说的力量落在最小的尺度上：一个签名、一块砖、一块饼干、一个名字。这组文章顺着这些细节去读，也不把忍耐轻易改写成安慰。":"索爾仁尼琴把十年的強制壓進一個普通的冬日。小說的力量落在最小的尺度上：一個簽名、一塊磚、一塊餅乾、一個名字。這組文章順著這些細節去讀，也不把忍耐輕易改寫成安慰。","舒霍夫替囚禁自己的制度把墙砌好，因为手艺仍是他自己的尺度可以生效的一小块地方。":"舒霍夫替囚禁自己的制度把牆砌好，因為手藝仍是他自己的尺度可以生效的一小塊地方。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那块饼干不在账上":"那塊餅乾不在賬上","那堵墙":"那堵牆","集中营里的交换一笔不差，而舒霍夫给阿廖沙的那块饼干，却没有进入他睡前的日结。":"集中營裡的交換一筆不差，而舒霍夫給阿廖沙的那塊餅乾，卻沒有進入他睡前的日結。"};
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
