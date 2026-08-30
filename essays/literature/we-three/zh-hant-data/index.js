/* Generated offline from essays/literature/we-three/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《我们仨》很薄，薄得容易被当成一本温情小书。它真正锋利的地方，在于它拒绝让公共成就、历史判词甚至丧失本身，挤掉那些没有用途的日常。":"《我們仨》很薄，薄得容易被當成一本溫情小書。它真正鋒利的地方，在於它拒絕讓公共成就、歷史判詞甚至喪失本身，擠掉那些沒有用途的日常。","《我们仨》解读":"《我們仨》解讀","一个长达万里的梦":"一個長達萬里的夢","丈夫和女儿走后，杨绛仍以“我们仨”为主语，记录那些已经发生、不会因死亡而失效的日常。":"丈夫和女兒走後，楊絳仍以“我們仨”為主語，記錄那些已經發生、不會因死亡而失效的日常。","他们做的那些没有用的事":"他們做的那些沒有用的事","剃头、下放与无房可住都被写下；杨绛只是不让历史判词接管自己记忆的比例。":"剃頭、下放與無房可住都被寫下；楊絳只是不讓歷史判詞接管自己記憶的比例。","古驿道不是虚幻修辞，而是杨绛在两家医院之间奔走、一天比一天接近两场丧失的准确日程。":"古驛道不是虛幻修辭，而是楊絳在兩家醫院之間奔走、一天比一天接近兩場喪失的準確日程。","四篇文章沿着这份轻重追问：没有用的事情为什么能保住一个人；而把共同生活记下来，为什么不等于把悲痛放在全书中央。":"四篇文章沿著這份輕重追問：沒有用的事情為什麼能保住一個人；而把共同生活記下來，為什麼不等於把悲痛放在全書中央。","四篇文章，从那场记录两年失散的万里长梦，到一家人用早饭、散步、外号与字条做成的家，再到杨绛如何分配记忆的比例，以及一个幸存者为什么仍用复数写作。":"四篇文章，從那場記錄兩年失散的萬里長夢，到一家人用早飯、散步、外號與字條做成的家，再到楊絳如何分配記憶的比例，以及一個倖存者為什麼仍用複數寫作。","我一个人思念我们仨":"我一個人思念我們仨","早饭、探险、外号与废话字条在任何账上都没有用，却正是三个高度自立的人彼此不作工具的共同生活。":"早飯、探險、外號與廢話字條在任何賬上都沒有用，卻正是三個高度自立的人彼此不作工具的共同生活。","杨绛《我们仨》。全书剧透。":"楊絳《我們仨》。全書劇透。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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
