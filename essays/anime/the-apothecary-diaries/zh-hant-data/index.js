/* Generated offline from essays/anime/the-apothecary-diaries/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 日本动漫与漫画":"← 日本動漫與漫畫","系列 · 5 篇解读":"系列 · 5 篇解讀","《药屋少女的呢喃》解读":"《藥屋少女的呢喃》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","Independent English · 简 / 繁":"Independent English · 簡 / 繁","五篇沿着一个问题推进：人在位置由他人注意力决定的制度里，能否守住自己，取决于是否还有一个不由这套制度发放的去处；那个去处甚至不必是好地方。":"五篇沿著一個問題推進：人在位置由他人注意力決定的制度裡，能否守住自己，取決於是否還有一個不由這套制度發放的去處；那個去處甚至不必是好地方。","猫猫是这条论证的正面例子，壬氏是反面例子，后宫里几千个女人则是被它解释的多数。从她数着离宫的日子，到花街那个一点也不好的家，这五篇读的不是一个聪明女孩怎样闯过宫廷，而是一个人凭什么没有被宫廷全部换算掉。":"貓貓是這條論證的正面例子，壬氏是反面例子，後宮裡幾千個女人則是被它解釋的多數。從她數著離宮的日子，到花街那個一點也不好的家，這五篇讀的不是一個聰明女孩怎樣闖過宮廷，而是一個人憑什麼沒有被宮廷全部換算掉。","本系列以电视动画前四十八集为文本范围。故事仍未完结；以下包含第一、二季完整剧透。":"本系列以電視動畫前四十八集為文本範圍。故事仍未完結；以下包含第一、二季完整劇透。","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","她在数日子":"她在數日子","同样是让自己不被看见，对知道何时能走的人是自保，对没有终点的人却可能成为自弃；猫猫脸上的雀斑背后，一直有一个日期。":"同樣是讓自己不被看見，對知道何時能走的人是自保，對沒有終點的人卻可能成為自棄；貓貓臉上的雀斑背後，一直有一個日期。","英 · 简 · 繁":"英 · 簡 · 繁","没有别的地方去":"沒有別的地方去","当全部位置、资源与安全只有一个发放方，关系就会退化成依附；后宫真正强大的，不只是权力，而是它让许多人没有第二个去处。":"當全部位置、資源與安全只有一個發放方，關係就會退化成依附；後宮真正強大的，不只是權力，而是它讓許多人沒有第二個去處。","那件用不上的事是从外面带进来的":"那件用不上的事是從外面帶進來的","猫猫胳膊上的疤在后宫账本里价值为负，却正是她没有被后宫换算完的证据；这份兴趣也不是凭空长出的，而是有人从外面交给她的。":"貓貓胳膊上的疤在後宮賬本里價值為負，卻正是她沒有被後宮換算完的證據；這份興趣也不是憑空長出的，而是有人從外面交給她的。","他什么都有，除了外面":"他什麼都有，除了外面","壬氏的容貌、身份与权力都不是自己安排的；猫猫那份不受美貌与位置污染的反应，成了他唯一能够借来的外面。":"壬氏的容貌、身份與權力都不是自己安排的；貓貓那份不受美貌與位置汙染的反應，成了他唯一能夠借來的外面。","那个地方一点也不好":"那個地方一點也不好","花街买卖女人，也仍是猫猫不被后宫定义完的支点；它的作用不证明它正当，只说明自由有时来自两套制度之间留下的缝。":"花街買賣女人，也仍是貓貓不被後宮定義完的支點；它的作用不證明它正當，只說明自由有時來自兩套制度之間留下的縫。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {
    var mode = document.documentElement.getAttribute('data-lang') || 'en';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle) ? variants[originalTitle] : originalTitle;
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-card, .lang-toggle, .footer-langs, script, style')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      var source = originals.get(node);
      node.nodeValue = traditional && Object.prototype.hasOwnProperty.call(variants, source) ? variants[source] : source;
    }
  }
  document.addEventListener('DOMContentLoaded', function() {
    updateTraditionalReadingMode();
    new MutationObserver(function(records) { if (records.some(function(record) { return record.attributeName === 'data-lang'; })) updateTraditionalReadingMode(); }).observe(document.documentElement, {attributes:true, attributeFilter:['data-lang']});
  });
})();
