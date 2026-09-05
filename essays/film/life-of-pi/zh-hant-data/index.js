/* Generated offline from essays/film/life-of-pi/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《少年派的奇幻漂流》解读":"《少年派的奇幻漂流》解讀","三篇解读：一个由自己认领的名字、一条与老虎共同维持的边界，以及把叙事责任与事实证明分开的两个故事。":"三篇解讀：一個由自己認領的名字、一條與老虎共同維持的邊界，以及把敘事責任與事實證明分開的兩個故事。","人的版本不能证明老虎为假，偏爱也不能建立事实；叙述最终成为幸存者与听者共同承担的责任。":"人的版本不能證明老虎為假，偏愛也不能建立事實；敘述最終成為幸存者與聽者共同承擔的責任。","他把两个故事都讲了，然后问了一句":"他把兩個故事都講了，然後問了一句","他没有驯服它，他给它划了一条线":"他沒有馴服它，他給它划了一條線","依据李安执导的二〇一二年电影《少年派的奇幻漂流》，改编自扬·马特尔同名小说。文中情节以电影为准，也不把派讲述的任何一个版本当作已经得到最终证实的事实。":"依據李安執導的二〇一二年電影《少年派的奇幻漂流》，改編自揚·馬特爾同名小說。文中情節以電影為準，也不把派講述的任何一個版本當作已經得到最終證實的事實。","李安的电影追问：当经历无法被整理成唯一连贯的版本，人怎样活下来。三篇文章从派为自己命名，写到他与理查德·帕克不对称的共处，再写到一份报告如何替无法核验的经历选择形式。":"李安的電影追問：當經歷無法被整理成唯一連貫的版本，人怎樣活下來。三篇文章從派為自己命名，寫到他與理查德·帕克不對稱的共處，再寫到一份報告如何替無法核驗的經歷選擇形式。","派回应被嘲弄强加的名字、同时活在几种信仰里，并学会尊重另一种生命首先意味着不把人的自我投射给它。":"派回應被嘲弄強加的名字、同時活在幾種信仰裡，並學會尊重另一種生命首先意味著不把人的自我投射給它。","派靠维持距离而不放弃照料活下来；老虎没有回头，让这段共处的意义有意保持不对称。":"派靠維持距離而不放棄照料活下來；老虎沒有回頭，讓這段共處的意義有意保持不對稱。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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
