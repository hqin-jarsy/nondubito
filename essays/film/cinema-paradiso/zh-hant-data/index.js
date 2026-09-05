/* Generated offline from essays/film/cinema-paradiso/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《天堂电影院》常被称作写给电影的情书，而它的爱恰恰由“剪切”组成：神父剪掉吻，阿尔弗雷多把多多从故乡剪出去，最后又把失去上下文的片段重新接在一起。这三篇追问保存能够救回什么，又永远补不上什么。":"《天堂電影院》常被稱作寫給電影的情書，而它的愛恰恰由“剪切”組成：神父剪掉吻，阿爾弗雷多把多多從故鄉剪出去，最後又把失去上下文的片段重新接在一起。這三篇追問保存能夠救回什麼，又永遠補不上什麼。","《天堂电影院》解读":"《天堂電影院》解讀","三篇解读：被剪掉的画格、一道把爱变成三十年离乡的命令，以及保存了全镇不许观看之物的胶片。":"三篇解讀：被剪掉的畫格、一道把愛變成三十年離鄉的命令，以及保存了全鎮不許觀看之物的膠片。","他对他说，不要回来":"他對他說，不要回來","他把剪下来的东西全接在了一起":"他把剪下來的東西全接在了一起","依据朱塞佩·托纳多雷执导的一九八八年电影《天堂电影院》，以通行公映版为准；篇幅更长的导演剪辑版补回成年艾莲娜线，也会改变对阿尔弗雷多介入的判断。":"依據朱塞佩·托納多雷執導的一九八八年電影《天堂電影院》，以通行公映版為準；篇幅更長的導演剪輯版補回成年艾蓮娜線，也會改變對阿爾弗雷多介入的判斷。","最后的胶片补不回多多失去的年月，却保存了被审查的余项，也让阿尔弗雷多那道爱的命令继续悬着。":"最後的膠片補不回多多失去的年月，卻保存了被審查的余項，也讓阿爾弗雷多那道愛的命令繼續懸著。","神父的铃把欲望移出公共视野；阿尔弗雷多没有公开反抗，只是拒绝把余下的画格扔掉。":"神父的鈴把慾望移出公共視野；阿爾弗雷多沒有公開反抗，只是拒絕把余下的畫格扔掉。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那些被剪掉的部分，有人一格一格收着":"那些被剪掉的部分，有人一格一格收著","阿尔弗雷多用封住归路来打开未来；这份给予是真的，以它之名留下的三十年伤口也是真的。":"阿爾弗雷多用封住歸路來打開未來；這份給予是真的，以它之名留下的三十年傷口也是真的。"};
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
