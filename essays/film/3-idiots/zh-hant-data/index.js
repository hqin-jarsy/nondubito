/* Generated offline from essays/film/3-idiots/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《三傻大闹宝莱坞》解读":"《三個傻瓜》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一所把学习改造成排名的学校，读到法尔汉与拉朱必须亲自承担的不同风险，以及为什么不能用兰彻后来的成功，倒过来替他当年所有没有把握的行动作证。":"三篇從一所把學習改造成排名的學校，讀到法罕與拉加必須親自承擔的不同風險，以及為什麼不能用藍丘後來的成功，倒過來替他當年所有沒有把握的行動作證。","《三傻大闹宝莱坞》常被压缩成一句安慰人的指令：追随热爱，成功自然会来。电影其实比这句话复杂。乔伊做出了优秀的东西，却没有等到认可；查图尔按照制度的标准取得了成功；法尔汉与拉朱面对的代价，兰彻无法替他们承担；兰彻本人也会帮助、越界、犯错，并在不知道结果时行动。":"《三個傻瓜》常被壓縮成一句安慰人的指令：追隨熱愛，成功自然會來。電影其實比這句話複雜。喬伊做出了優秀的東西，卻沒有等到認可；查托按照制度的標準取得了成功；法罕與拉加面對的代價，藍丘無法替他們承擔；藍丘本人也會幫助、越界、犯錯，並在不知道結果時行動。","三篇从制度设计写到个人署名，再写到后见之明。它们追问：一所学校奖励规定说法而不是理解时，究竟在生产什么；朋友可以指出什么，又该在哪里停止成为新的生活导演；以及当后来的成功既未知也无保证时，一项行动是否仍能在当下成立。":"三篇從制度設計寫到個人署名，再寫到後見之明。它們追問：一所學校獎勵規定說法而不是理解時，究竟在生產什麼；朋友可以指出什麼，又該在哪裡停止成為新的生活導演；以及當後來的成功既未知也無保證時，一項行動是否仍能在當下成立。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","这所学校在生产什么":"這所學校在生產什麼","ICE 不只教授工程，也把理解翻译成规定表述，把人翻译成排名，再把可以预防的痛苦翻译成个人失败。":"ICE 不只教授工程，也把理解翻譯成規定表述，把人翻譯成排名，再把可以預防的痛苦翻譯成個人失敗。","英 · 简 · 繁":"英 · 簡 · 繁","他们各自的那笔账，是自己去结的":"他們各自的那筆帳，是自己去結的","兰彻让选项显形，也有越界的时候；法尔汉与拉朱只有在自己开口、拒绝并接受代价之处，才真正成为行动的作者。":"藍丘讓選項顯形，也有越界的時候；法罕與拉加只有在自己開口、拒絕並接受代價之處，才真正成為行動的作者。","他做那些事的时候，并不知道结果":"他做那些事的時候，並不知道結果","四百项专利让兰彻在回望中赢得太轻易；真正需要判断的，是他行动时的未知，而不只是结尾补上的胜利。":"四百項專利讓藍丘在回望中贏得太輕易；真正需要判斷的，是他行動時的未知，而不只是結尾補上的勝利。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
