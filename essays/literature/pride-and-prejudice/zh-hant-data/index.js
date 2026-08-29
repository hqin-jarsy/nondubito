/* Generated offline from essays/literature/pride-and-prejudice/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","《傲慢与偏见》解读":"《傲慢與偏見》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","四篇文章，从五个女儿的经济处境、夏洛特的实际判断、莉迪亚的灾难链条，到两个人如何各自修正自己。":"四篇文章，從五個女兒的經濟處境、夏洛特的實際判斷、莉迪亞的災難鏈條，到兩個人如何各自修正自己。","奥斯汀的喜剧由不平等物质条件下作出的判断推动。浪搏恩不能由女儿继承；婚姻可以决定住房与收入；一个人的名誉灾难会蔓延到全家。机智并不能取消这套机器。":"奧斯汀的喜劇由不平等物質條件下作出的判斷推動。浪搏恩不能由女兒繼承；婚姻可以決定住房與收入；一個人的名譽災難會蔓延到全家。機智並不能取消這套機器。","四篇文章不把班纳特太太、夏洛特、莉迪亚、伊丽莎白与达西缩成爱情类型。小说的持久力量，正在于它让结构压力与个人责任同时留在画面里。":"四篇文章不把班納特太太、夏洛特、莉迪亞、伊麗莎白與達西縮成愛情類型。小說的持久力量，正在於它讓結構壓力與個人責任同時留在畫面裡。","简·奥斯汀《傲慢与偏见》。全书剧透。":"珍·奧斯汀《傲慢與偏見》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","五个女儿是一笔负债":"五個女兒是一筆負債","浪搏恩的限嗣继承把班纳特太太的喜剧性执念，变成对家庭经济危险的准确识别。":"浪搏恩的限嗣繼承把班納特太太的喜劇性執念，變成對家庭經濟危險的準確識別。","英 · 简 · 繁":"英 · 簡 · 繁","夏洛特不是软弱":"夏洛特不是軟弱","嫁给柯林斯是夏洛特在没有伊丽莎白的美貌、财产与风险承受力时作出的清醒而昂贵的选择。":"嫁給柯林斯是夏洛特在沒有伊麗莎白的美貌、財產與風險承受力時作出的清醒而昂貴的選擇。","毁掉她需要多少步":"毀掉她需要多少步","莉迪亚作出了鲁莽选择；她的私奔之所以成为灾难，却经过家庭、性别与名誉制度的一整条链。":"莉迪亞作出了魯莽選擇；她的私奔之所以成為災難，卻經過家庭、性別與名譽制度的一整條鏈。","两个人都改了，而且都是自己改的":"兩個人都改了，而且都是自己改的","伊丽莎白与达西能够结合，不是因为彼此直接改造，而是因为各自接受证据、修正判断。":"伊麗莎白與達西能夠結合，不是因為彼此直接改造，而是因為各自接受證據、修正判斷。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
