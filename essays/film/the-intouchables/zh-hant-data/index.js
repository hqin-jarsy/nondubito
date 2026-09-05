/* Generated offline from essays/film/the-intouchables/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《触不可及》常被概括成一个人教另一个人重新生活。可当两个人都不被写成对方的药，这段关系才更有意思。三篇文章分别追问：普通的争吵恢复了什么，信任真正冒了什么风险，以及善意的介入从哪里开始威胁它想唤回的自由。":"《觸不可及》常被概括成一個人教另一個人重新生活。可當兩個人都不被寫成對方的藥，這段關係才更有意思。三篇文章分別追問：普通的爭吵恢復了什麼，信任真正冒了什麼風險，以及善意的介入從哪裡開始威脅它想喚回的自由。","《触不可及》解读":"《觸不可及》解讀","三篇解读：没有怜悯姿态的照护、越过社会定论的信任，以及替人打开门与把人推进去之间那条困难的边界。":"三篇解讀：沒有憐憫姿態的照護、越過社會定論的信任，以及替人打開門與把人推進去之間那條困難的邊界。","两个人与定死他们的事实":"兩個人與定死他們的事實","他把桌子摆好，然后走了":"他把桌子擺好，然後走了","他是唯一一个没有同情他的人":"他是唯一一個沒有同情他的人","依据奥利维埃·纳卡什与埃里克·托莱达诺执导的二〇一一年电影《触不可及》，故事取材于菲利普·波佐·迪博尔戈与阿卜杜勒·塞卢；关键情节已参照影片对白与片尾字幕校订。":"依據奧利維埃·納卡什與埃裡克·托萊達諾執導的二〇一一年電影《觸不可及》，故事取材於菲利普·波佐·迪博爾戈與阿卜杜勒·塞盧；關鍵情節已參照影片對白與片尾字幕校訂。","德瑞斯的无知会带来危险，却也把普通的玩笑、争执与反驳还给了一个总被人小心处理的人。":"德瑞斯的無知會帶來危險，卻也把普通的玩笑、爭執與反駁還給了一個總被人小心處理的人。","海边见面为菲利普重新造出选择，也因刻意隐瞒而逼近善意强迫的边界。":"海邊見面為菲利普重新造出選擇，也因刻意隱瞞而逼近善意強迫的邊界。","瘫痪与犯罪记录都是真实事实；关系从不让任何一个事实替人写完结论开始。":"癱瘓與犯罪記錄都是真實事實；關係從不讓任何一個事實替人寫完結論開始。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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
