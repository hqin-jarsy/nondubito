/* Generated offline from essays/film/good-will-hunting/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《心灵捕手》不只写一份被发现的天才，也追问天才被看见以后，谁获得替他安排人生的权力。三篇文章区分涵育与代为规划、治疗中的在场与征服，以及真正选择与抢先拒绝的防御习惯。":"《心靈捕手》不只寫一份被發現的天才，也追問天才被看見以後，誰獲得替他安排人生的權力。三篇文章區分涵育與代為規劃、治療中的在場與征服，以及真正選擇與搶先拒絕的防禦習慣。","《心灵捕手》解读":"《心靈捕手》解讀","三篇解读：自发生长的天分、同时移动听者与说者的长椅谈话，以及任何导师都不能代为规定的两次出发。":"三篇解讀：自發生長的天分、同時移動聽者與說者的長椅談話，以及任何導師都不能代為規定的兩次出發。","他的本事自己长，他的安排别人给":"他的本事自己長，他的安排別人給","依据格斯·范·桑特执导的一九九七年电影《心灵捕手》；除少量辨识性短句外均为转述，心理判断只作为影片解读，不写成临床规律。":"依據格斯·範·桑特執導的一九九七年電影《心靈捕手》；除少量辨識性短句外均為轉述，心理判斷只作為影片解讀，不寫成臨床規律。","尚恩在长椅上的话既挑战威尔，也暴露自己；力量来自它同时是介入与自我讲述。":"尚恩在長椅上的話既挑戰威爾，也暴露自己；力量來自它同時是介入與自我講述。","查克盼望有一天门后无人，尚恩反复守住一句话，威尔终于走向一个人而不是抢先撤离。":"查克盼望有一天門後無人，尚恩反復守住一句話，威爾終於走向一個人而不是搶先撤離。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","蓝波看见罕见能力并把威尔从牢里带出，可这份援手同时带来一条已经替他选好的未来。":"藍波看見罕見能力並把威爾從牢裡帶出，可這份援手同時帶來一條已經替他選好的未來。","那天早上，两个人都走了":"那天早上，兩個人都走了","那段话同时说给两个人听":"那段話同時說給兩個人聽"};
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
