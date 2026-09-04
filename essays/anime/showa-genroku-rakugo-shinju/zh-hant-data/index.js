/* Generated offline from essays/anime/showa-genroku-rakugo-shinju/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《昭和元禄落语心中》没有把落语当成文化背景，而是把它写成一种只有在具体的人继续对具体的听众开口时才存在的东西。名跡可以完整地从一位表演者传给另一位；人、声音、愿望与伤害却不能。":"《昭和元祿落語心中》沒有把落語當成文化背景，而是把它寫成一種只有在具體的人繼續對具體的聽眾開口時才存在的東西。名跡可以完整地從一位表演者傳給另一位；人、聲音、願望與傷害卻不能。","《昭和元禄落语心中》解读":"《昭和元祿落語心中》解讀","一个出狱后什么都没有的人，先接过空了四十年的助六，再成为下一代八云；死者没有回来，传承却由不像他们的人继续。":"一個出獄後什麼都沒有的人，先接過空了四十年的助六，再成為下一代八雲；死者沒有回來，傳承卻由不像他們的人繼續。","一个被送来的人苦练出只属于自己的艺术，一个天生的表演者被逐出师门；八云与助六的名字越过了两条不相等的人生。":"一個被送來的人苦練出只屬於自己的藝術，一個天生的表演者被逐出師門；八雲與助六的名字越過了兩條不相等的人生。","五篇从一个打算关门的传人，读到两个袭名、被记起两次的死亡、始终没有向小夏打开的职业入口，以及最终越过传艺者本人意图的教学。":"五篇從一個打算關門的傳人，讀到兩個襲名、被記起兩次的死亡、始終沒有向小夏開啟的職業入口，以及最終越過傳藝者本人意圖的教學。","他打算把门关上":"他打算把門關上","八云第一次收徒时，也打算让手上的一部分落语随自己入土；权利、继承位置与十年里的日常行动并不整齐一致。":"八雲第一次收徒時，也打算讓手上的一部分落語隨自己入土；權利、繼承位置與十年裡的日常行動並不整齊一致。","同一个死亡之夜被讲述两次，作品始终没有交出外部的终审镜头；几十年的供养与几十年的恨住在同一个屋檐下。":"同一個死亡之夜被講述兩次，作品始終沒有交出外部的終審鏡頭；幾十年的供養與幾十年的恨住在同一個屋簷下。","同一天进门的两个人":"同一天進門的兩個人","小夏在没有观众、也没有职业入口的地方练父亲的段子；排除她的不是一个守门人，而是一套早于在场者的安排。":"小夏在沒有觀眾、也沒有職業入口的地方練父親的段子；排除她的不是一個守門人，而是一套早於在場者的安排。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这五篇追问继承究竟要求什么，又不要求什么。八云有权让自己手上的艺术失传，小夏可以深爱一门不让她进入的行业，与太郎也可以接过名字，却无法让死者回来。含两季完整剧透。":"這五篇追問繼承究竟要求什麼，又不要求什麼。八雲有權讓自己手上的藝術失傳，小夏可以深愛一門不讓她進入的行業，與太郎也可以接過名字，卻無法讓死者回來。含兩季完整劇透。"};
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
