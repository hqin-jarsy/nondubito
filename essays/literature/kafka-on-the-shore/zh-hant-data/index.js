/* Generated offline from essays/literature/kafka-on-the-shore/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《海边的卡夫卡》解读":"《海邊的卡夫卡》解讀","卡夫卡的父亲不是命令一个动作，而是定义未来身份；孩子的反抗也只能围绕想逃离的描述运转。":"卡夫卡的父親不是命令一個動作，而是定義未來身份；孩子的反抗也只能圍繞想逃離的描述運轉。","卡夫卡离开无时间的森林，不是因为预言被破解，而是因为自由仍需要一个还能发生下一次选择的世界。":"卡夫卡離開無時間的森林，不是因為預言被破解，而是因為自由仍需要一個還能發生下一次選擇的世界。","四篇文章，从让反抗也围着它运转的父亲预言、中田无法解释的空缺，到先接纳后分类的图书馆，以及从不再需要选择的世界返回。":"四篇文章，從讓反抗也圍著它運轉的父親預言、中田無法解釋的空缺，到先接納後分類的圖書館，以及從不再需要選擇的世界返回。","图书馆":"圖書館","大岛先给卡夫卡空间，再谈身份；最照顾他的人，也都不需要先证明彼此究竟是什么关系。":"大島先給卡夫卡空間，再談身份；最照顧他的人，也都不需要先證明彼此究竟是什麼關係。","小说布满缺失的部分、不能确认的亲缘、敞开的入口，以及不能用“只是梦”卸掉责任的行动。这组文章追问，当过去无法修复、被指定的未来也已发生，人还剩下什么可能。":"小說布滿缺失的部分、不能確認的親緣、敞開的入口，以及不能用“只是夢”卸掉責任的行動。這組文章追問，當過去無法修復、被指定的未來也已發生，人還剩下什麼可能。","无法解释的事件掏空一个聪明孩子；公共补助让成年人活下去，也把灾难改写成一个已经处理的案子。":"無法解釋的事件掏空一個聰明孩子；公共補助讓成年人活下去，也把災難改寫成一個已經處理的案子。","村上春树《海边的卡夫卡》，中文篇依据赖明珠译本。全书剧透。":"村上春樹《海邊的卡夫卡》，中文篇依據賴明珠譯本。全書劇透。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","诅咒":"詛咒"};
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
