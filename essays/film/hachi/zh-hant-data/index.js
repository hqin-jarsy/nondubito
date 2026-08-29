/* Generated offline from essays/film/hachi/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《忠犬八公的故事》解读":"《忠犬小八》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一段不以交换为条件的关系，读到车站众人如何把最初不算数的存在纳入照料，以及当一个生命无法为自己辩说时，人如何决定它的分量。":"三篇從一段不以交換為條件的關係，讀到車站眾人如何把最初不算數的存在納入照料，以及當一個生命無法為自己辯說時，人如何決定它的分量。","《忠犬八公的故事》通常被记作一个关于忠诚的故事，但它更不寻常的部分其实发生在等待周围：帕克不要求八公先证明有用才爱它，车站众人也不是得到确证以后才开始照料。八公无法解释自己的每日返回究竟意味着什么，而解释的缺席，并不能让看见它的人免于回应。":"《忠犬小八》通常被記作一個關於忠誠的故事，但它更不尋常的部分其實發生在等待周圍：帕克不要求八公先證明有用才愛它，車站眾人也不是得到確證以後才開始照料。八公無法解釋自己的每日返回究竟意味著什麼，而解釋的缺席，並不能讓看見它的人免於回應。","这三篇从关系写到识认，再写到解释。它们追问：当感情不是一笔交易时，关系里还剩下什么；持续观看如何改变观看者；以及电影即使让我们短暂透过八公的眼睛看世界，为什么也没有把它的内心交给我们占有。":"這三篇從關係寫到識認，再寫到解釋。它們追問：當感情不是一筆交易時，關係裡還剩下什麼；持續觀看如何改變觀看者；以及電影即使讓我們短暫透過八公的眼睛看世界，為什麼也沒有把它的內心交給我們佔有。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他们之间没有一件事是交换":"他們之間沒有一件事是交換","帕克与八公都得到陪伴，却没有谁把照料建立在表现之上；连不肯捡球，也可以是被爱的这条狗本身。":"帕克與八公都得到陪伴，卻沒有誰把照料建立在表現之上；連不肯撿球，也可以是被愛的這條狗本身。","英 · 简 · 繁":"英 · 簡 · 繁","狗一点没变，是人变了":"狗一點沒變，是人變了","八公重复的是同一个动作；改变的是车站共同体，它把一个最初不该在场的存在，慢慢变成共同照料的生命。":"八公重複的是同一個動作；改變的是車站共同體，它把一個最初不該在場的存在，慢慢變成共同照料的生命。","这件事有多重，是人定的":"這件事有多重，是人定的","电影让我们分享八公的视野，却不替它翻译内心；等待的分量来自那些看见以后没有转身离开的人。":"電影讓我們分享八公的視野，卻不替它翻譯內心；等待的分量來自那些看見以後沒有轉身離開的人。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
