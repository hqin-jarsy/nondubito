/* Generated offline from essays/meaning/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"SAE Meaning Theory 意义论系列 — Non Dubito": "SAE Meaning Theory 意義論系列 — Non Dubito", "SAE 意义论": "SAE 意義論", "© 2026 Han Qin (秦汉) · ": "© 2026 Han Qin (秦漢) · ", "“人生之外”也不是说，必须对别人有用，活着才算数。我们可以关心别人，而不把自己交出去；也可以独自生活，不因此比谁少了什么。": "“人生之外”也不是說，必須對別人有用，活著才算數。我們可以關心別人，而不把自己交出去；也可以獨自生活，不因此比誰少了什麼。", "← 书架": "← 書架", "不在前，也不在后": "不在前，也不在後", "人不在了，本子还在。后来打开它的人，接过了什么，又没有接过什么？": "人不在了，本子還在。後來打開它的人，接過了什麼，又沒有接過什麼？", "人生的意义在人生之外": "人生的意義在人生之外", "什么停下，什么继续": "什麼停下，什麼繼續", "今天可以改主意，但不必把昨天的自己赶出这一生。": "今天可以改主意，但不必把昨天的自己趕出這一生。", "从那个旧本子开始 →": "從那個舊本子開始 →", "他以为那是自己要的": "他以為那是自己要的", "别人是怎么谈的": "別人是怎麼談的", "前面被关掉了": "前面被關掉了", "可以从第一篇顺着读，也可以先挑一个你正在想的问题。前七篇讲完主线；第八篇是与其他哲学家的对话，想再往里走时读。不需要先读论文。": "可以從第一篇順著讀，也可以先挑一個你正在想的問題。前七篇講完主線；第八篇是與其他哲學家的對話，想再往里走時讀。不需要先讀論文。", "可这样的一生，究竟值不值得？一个故事能把它讲完整吗？让其他哲学家把问题继续问下去。": "可這樣的一生，究竟值不值得？一個故事能把它講完整嗎？讓其他哲學家把問題繼續問下去。", "四十岁那年，一个人翻出二十岁时写的本子。想做的事，有些做成了，有些再也没提起。有一件，他看了半天，已经想不起当初为什么那么想要。": "四十歲那年，一個人翻出二十歲時寫的本子。想做的事，有些做成了，有些再也沒提起。有一件，他看了半天，已經想不起當初為什麼那麼想要。", "放下别人的期待以后，里面真的有一个完整的自己，在等着被找回来吗？": "放下別人的期待以後，裡面真的有一個完整的自己，在等著被找回來嗎？", "明年的安排里有一个人": "明年的安排里有一個人", "有人问过去二十年算不算白过，得到的回答却是一张成绩单。": "有人問過去二十年算不算白過，得到的回答卻是一張成績單。", "有的机会还能重来，有的不能。后来过得好，也不必把每一次失去都说成值得。": "有的機會還能重來，有的不能。後來過得好，也不必把每一次失去都說成值得。", "本系列改写自《SAE 意义论》五篇论文。每篇文末保留学术原文链接；如果想看完整论证，可以从那里继续。": "本系列改寫自《SAE 意義論》五篇論文。每篇文末保留學術原文鏈接；如果想看完整論證，可以從那裡繼續。", "没有那个数": "沒有那個數", "父亲选的专业，他一直以为自己也想要。做了二十年以后，才开始重新问这件事。": "父親選的專業，他一直以為自己也想要。做了二十年以後，才開始重新問這件事。", "秦汉 · 八篇散文 · 简体、繁体与独立英文版": "秦漢 · 八篇散文 · 簡體、繁體與獨立英文版", "第八篇 · 延伸阅读": "第八篇 · 延伸閱讀", "远方的朋友、还没遇见的读者、走向别处的学生：关心一个人，不等于拥有他的人生。": "遠方的朋友、還沒遇見的讀者、走向別處的學生：關心一個人，不等於擁有他的人生。", "那些年是不是白过了？现在改主意，还来不来得及？这八篇从这些问题开始，写过去、遗憾、成长，也写我们如何把另一个人放进自己的生活。它们不替人生打分。": "那些年是不是白過了？現在改主意，還來不來得及？這八篇從這些問題開始，寫過去、遺憾、成長，也寫我們如何把另一個人放進自己的生活。它們不替人生打分。"};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {
    var mode = document.documentElement.getAttribute('data-lang') || 'zh';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle)
      ? variants[originalTitle]
      : originalTitle;
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-toggle, script, style')) continue;
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
      if (records.some(function(record) { return record.attributeName === 'data-lang'; })) updateTraditionalReadingMode();
    }).observe(document.documentElement, {attributes:true, attributeFilter:['data-lang']});
  });
})();
