/* Generated offline from essays/literature/hard-boiled-wonderland-and-the-end-of-the-world/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《世界末日与冷酷异境》解读":"《世界末日與冷酷異境》解讀","体面的职业建在一次不知情的实验上；完整说明直到选择已不可能时才抵达。":"體面的職業建在一次不知情的實驗上；完整說明直到選擇已不可能時才抵達。","兽、头骨、梦读、森林与高墙组成完整系统，让被丢掉的心消失，也让居民对这一切满意。":"獸、頭骨、夢讀、森林與高牆組成完整系統，讓被丟掉的心消失，也讓居民對這一切滿意。","叙述者放走影子却自己留下；他既不选择恢复完整，也不选择无痛秩序，而走向仍有残心的森林。":"敘述者放走影子卻自己留下；他既不選擇恢復完整，也不選擇無痛秩序，而走向仍有殘心的森林。","四篇文章，从入场时必须交出的影子、在不知情中植入的职业，到小镇完整的清除生态，以及让一半离开、自己走向残余之地的最终选择。":"四篇文章，從入場時必須交出的影子、在不知情中植入的職業，到小鎮完整的清除生態，以及讓一半離開、自己走向殘餘之地的最終選擇。","小镇的入场手续既拿走心，也拿走日后判断损失的能力；只有被丢弃的影子还记得完整是什么。":"小鎮的入場手續既拿走心，也拿走日後判斷損失的能力；只有被丟棄的影子還記得完整是什麼。","村上春树《世界末日与冷酷异境》，中文篇依据赖明珠译本。林少华译本作《世界尽头与冷酷仙境》。全书剧透。":"村上春樹《世界末日與冷酷異境》，中文篇依據賴明珠譯本。林少華譯本作《世界盡頭與冷酷仙境》。全書劇透。","村上春树交替书写的两个世界追问：若连思念失去之物的能力也被拿走，安稳是否仍是安稳。这组文章顺着手续、职业与温和执行者，让这个问题逐渐变得具体。":"村上春樹交替書寫的兩個世界追問：若連思念失去之物的能力也被拿走，安穩是否仍是安穩。這組文章順著手續、職業與溫和執行者，讓這個問題逐漸變得具體。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","计算士":"計算士","镇":"鎮"};
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
