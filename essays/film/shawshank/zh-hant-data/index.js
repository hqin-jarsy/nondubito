/* Generated offline from essays/film/shawshank/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《肖申克的救赎》常被记成希望战胜囚禁的故事，最著名的画面也是安迪爬过污水管、在雨中张开双臂。但电影更难的问题从别处开始：当一套体制让人相信，自己在世界上唯一稳固的位置就是被别人使用，他离开高墙以后还剩下什么？":"《肖申克的救贖》常被記成希望戰勝囚禁的故事，最著名的畫面也是安迪爬過汙水管、在雨中張開雙臂。但電影更難的問題從別處開始：當一套體制讓人相信，自己在世界上唯一穩固的位置就是被別人使用，他離開高牆以後還剩下什麼？","《肖申克的救赎》解读":"《肖申克的救贖》解讀","三篇从布鲁克斯之死、安迪的有用与瑞德的假释，重读体制如何把人变成功能，以及一个人如何在用途之外重新出现。":"三篇從布魯克斯之死、安迪的有用與瑞德的假釋，重讀體制如何把人變成功能，以及一個人如何在用途之外重新出現。","他之所以安全，是因为他有用":"他之所以安全，是因為他有用","安迪得到的特殊待遇不是权力的例外，而是体制发现一项高价值资产后给出的有条件回报。":"安迪得到的特殊待遇不是權力的例外，而是體制發現一項高價值資產後給出的有條件回報。","布鲁克斯不是简单地“不适应自由”；被体制使用五十年后，他已经无法在岗位之外安放自己。":"布魯克斯不是簡單地“不適應自由”；被體制使用五十年後，他已經無法在崗位之外安放自己。","最后一次听证不证明官僚程序会奖励诚实；它呈现的是瑞德不再把自己做成案卷所要答案的时刻。":"最後一次聽證不證明官僚程序會獎勵誠實；它呈現的是瑞德不再把自己做成案卷所要答案的時刻。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这三篇从失去图书管理员位置便无法存活的布鲁克斯，读到凭借专业价值换来有条件安全的安迪，再读到被一项具体承诺拉出空白生活的瑞德。自由不只是墙的消失，也是在岗位、案卷与合格答案之外，重新成为一个不能被用途穷尽的人。":"這三篇從失去圖書管理員位置便無法存活的布魯克斯，讀到憑藉專業價值換來有條件安全的安迪，再讀到被一項具體承諾拉出空白生活的瑞德。自由不只是牆的消失，也是在崗位、案卷與合格答案之外，重新成為一個不能被用途窮盡的人。","那个死在监狱外的老人":"那個死在監獄外的老人"};
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
