/* Generated offline from essays/literature/ordinary-world/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 五篇解读 · 文学评论":"系列 · 五篇解讀 · 文學評論","《平凡的世界》解读":"《平凡的世界》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","五篇文章，从“平凡”这把尺度、少安替润叶作决定、润叶的返回、晓霞不替少平分类，到他选择回去的煤矿。":"五篇文章，從“平凡”這把尺度、少安替潤葉作決定、潤葉的返回、曉霞不替少平分類，到他選擇回去的煤礦。","路遥的长篇把生活放在巨大的坐标里衡量：乡村与城市、贫困与机会、国家转型与私人愿望。“平凡”听来像描述，却很容易变成一把未经追问其权威的尺度所下的判词。":"路遙的長篇把生活放在巨大的坐標裡衡量：鄉村與城市、貧困與機會、國家轉型與私人願望。“平凡”聽來像描述，卻很容易變成一把未經追問其權威的尺度所下的判詞。","五篇文章跟随孙少安、孙少平、田润叶、贺秀莲与田晓霞，在物质压力中观察选择：牺牲何时仍有主体性，照料何时成为承认，返回是否也能像出走一样由自己书写。":"五篇文章跟隨孫少安、孫少平、田潤葉、賀秀蓮與田曉霞，在物質壓力中觀察選擇：犧牲何時仍有主體性，照料何時成為承認，返回是否也能像出走一樣由自己書寫。","路遥《平凡的世界》。全书剧透。":"路遙《平凡的世界》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","谁在说他们平凡":"誰在說他們平凡","“平凡”不是生命的中性尺寸，而是把生命放上某张地图之后得出的判断。":"“平凡”不是生命的中性尺寸，而是把生命放上某張地圖之後得出的判斷。","英 · 简 · 繁":"英 · 簡 · 繁","他替她做了决定":"他替她做了決定","少安拒绝润叶，却没有否认爱情；他认定债务与阶层让未来不可能，也替两个人一并作了决定。":"少安拒絕潤葉，卻沒有否認愛情；他認定債務與階層讓未來不可能，也替兩個人一並作了決定。","润叶为什么回去了":"潤葉為什麼回去了","润叶回到残疾的向前身边，既非简单屈服也非纯粹救赎；这选择经过了常见解读经常删掉的多年。":"潤葉回到殘疾的向前身邊，既非簡單屈服也非純粹救贖；這選擇經過了常見解讀經常刪掉的多年。","唯一一个不给他分类的人":"唯一一個不給他分類的人","晓霞把书与可能性带给少平，却不按自己的阶层与教育把他改造成一个项目。":"曉霞把書與可能性帶給少平，卻不按自己的階層與教育把他改造成一個項目。","忠于自己，算平凡吗":"忠於自己，算平凡嗎","少平回到煤矿、拒绝更体面的路线，也放下了最初用来衡量逃离的那把尺子。":"少平回到煤礦、拒絕更體面的路線，也放下了最初用來衡量逃離的那把尺子。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
