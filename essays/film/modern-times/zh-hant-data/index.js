/* Generated offline from essays/film/modern-times/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《摩登时代》解读":"《摩登時代》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","三篇从一条在工人崩溃后仍继续运转的流水线，读到流浪汉穿过的监狱、工厂、街道与商店，以及那个没有名字、却仍能说出自己想要什么的女孩。":"三篇從一條在工人崩潰後仍繼續運轉的流水線，讀到流浪漢穿過的監獄、工廠、街道與商店，以及那個沒有名字、卻仍能說出自己想要什麼的女孩。","《摩登时代》通过身体让系统显形。管理者出现在屏幕上，劳动则被拆成小到可以无损替换人的动作；流浪汉离开工厂后仍继续拧螺丝，因为工厂已经进入他的神经。":"《摩登時代》透過身體讓系統顯形。管理者出現在螢幕上，勞動則被拆成小到可以無損替換人的動作；流浪漢離開工廠後仍繼續擰螺絲，因為工廠已經進入他的神經。","卓别林却没有停在一个工作场所。他让人物穿过监狱、船厂、百货公司、餐厅、罢工与公路，带出一群共同面对“怎样撑到明天”的人。那个“街头女孩”则提出另一道题：生存以外，他们还能想要什么？":"卓別林卻沒有停在一個工作場所。他讓人物穿過監獄、船廠、百貨公司、餐廳、罷工與公路，帶出一群共同面對“怎樣撐到明天”的人。那個“街頭女孩”則提出另一道題：生存以外，他們還能想要什麼？","查理·卓别林一九三六年《摩登时代》。全片剧透。":"查理·卓別林一九三六年《摩登時代》。全片劇透。","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","他被抬走了，而那条线没有停":"他被抬走了，而那條線沒有停","流水线把劳动拆成可替换动作，侵入吃饭与休息，随后在动作吞掉工人以后仍继续运转。":"流水線把勞動拆成可替換動作，侵入吃飯與休息，隨後在動作吞掉工人以後仍繼續運轉。","英 · 简 · 繁":"英 · 簡 · 繁","他每换一个地方，就带出一批人":"他每換一個地方，就帶出一批人","一面掉落的旗、监狱优待、船厂事故、饥饿与罢工，让流浪汉成为穿过一群先分类后听人的机构之线。":"一面掉落的旗、監獄優待、船廠事故、飢餓與罷工，讓流浪漢成為穿過一群先分類後聽人的機構之線。","她在演职表上没有名字":"她在演職表上沒有名字","她只被归类为“街头女孩”，却说出一个家的愿望，为另一个人创造工作，也在公路上重新站起。":"她只被歸類為“街頭女孩”，卻說出一個家的願望，為另一個人創造工作，也在公路上重新站起。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
