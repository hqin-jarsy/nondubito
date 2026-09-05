/* Generated offline from essays/anime/revolutionary-girl-utena/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《少女革命》把隐喻做成了一套有日程、制服与操作规则的学园制度：一个学生可以在决斗中赢到另一个人，一把剑可以从身体里被抽出，一个王子可以把“最好的位置”交给女孩，却从不问她愿不愿意在那里生活。":"《少女革命》把隱喻做成了一套有日程、制服與操作規則的學園制度：一個學生可以在決鬥中贏到另一個人，一把劍可以從身體裡被抽出，一個王子可以把“最好的位置”交給女孩，卻從不問她願不願意在那裡生活。","《少女革命》解读":"《少女革命》解讀","五篇从“赢家可以带走她”的决斗规则出发，读沉默如何遮住而不是说明意愿、百万把剑怎样维持角色，以及欧蒂娜没能替安希完成、却为她打开的那道门。":"五篇從“贏家可以帶走她”的決鬥規則出發，讀沉默如何遮住而不是說明意願、百萬把劍怎樣維持角色，以及歐蒂娜沒能替安希完成、卻為她開啟的那道門。","他给她的那个位置":"他給她的那個位置","公主得到幸福，蔷薇新娘承受痛苦；两个位置高低不同，却同样没有给当事人留下回答的一栏。":"公主得到幸福，薔薇新娘承受痛苦；兩個位置高低不同，卻同樣沒有給當事人留下回答的一欄。","她为了保住哥哥而关上门；被拒绝的人群把她叫作魔女，让一次后果变成了她必须永远占据的位置。":"她為了保住哥哥而關上門；被拒絕的人群把她叫作魔女，讓一次後果變成了她必須永遠佔據的位置。","她对这件事没有意见":"她對這件事沒有意見","当命令与好意都得到同一种顺从的回应，外人便不能从“她答应了”推知她究竟选择了什么。":"當命令與好意都得到同一種順從的回應，外人便不能從“她答應了”推知她究竟選擇了什麼。","机器仍在、欧蒂娜消失了；安希却第一次明确拒绝哥哥给她的位置，换了衣服，自己迈出校门。":"機器仍在、歐蒂娜消失了；安希卻第一次明確拒絕哥哥給她的位置，換了衣服，自己邁出校門。","欧蒂娜为了阻止安希被当作东西而决斗，赢下之后却发现：胜利只是把这段所有权关系转到了自己手上。":"歐蒂娜為了阻止安希被當作東西而決鬥，贏下之後卻發現：勝利只是把這段所有權關係轉到了自己手上。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","赢的人可以带走她":"贏的人可以帶走她","这五篇紧跟电视版中可核查的动作，不替作品的意象规定唯一答案。蔷薇新娘既是被承受的位置，也是被反复表演的位置，最后才成为安希自己离开的地方。含全剧剧透；1999 年剧场版不在本系列范围内。":"這五篇緊跟電視版中可核查的動作，不替作品的意象規定唯一答案。薔薇新娘既是被承受的位置，也是被反覆表演的位置，最後才成為安希自己離開的地方。含全劇劇透；1999 年劇場版不在本系列範圍內。","那些剑":"那些劍"};
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
