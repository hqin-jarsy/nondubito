/* Generated offline from essays/film/forrest-gump/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《阿甘正传》把三十年的美国历史装进一个很少理解事件官方意义的人口中。制度不断给阿甘分类，又不断使用分类没能看见的能力。他的字面理解有时能让身份与偏见暂时失效，但电影也让他免于许多落在其他角色身上的后果。":"《阿甘正傳》把三十年的美國歷史裝進一個很少理解事件官方意義的人口中。制度不斷給阿甘分類，又不斷使用分類沒能看見的能力。他的字面理解有時能讓身份與偏見暫時失效，但電影也讓他免於許多落在其他角色身上的後果。","《阿甘正传》解读":"《阿甘正傳》解讀","一个不断被判定的人":"一個不斷被判定的人","三篇从不断被规格判定的阿甘，读到丹中尉如何重领自己的生命，以及电影怎样既看见珍妮的痛，又把她压进别人的故事。":"三篇從不斷被規格判定的阿甘，讀到丹中尉如何重領自己的生命，以及電影怎樣既看見珍妮的痛，又把她壓進別人的故事。","丹中尉把这条命重新拿了回来":"丹中尉把這條命重新拿了回來","丹中尉活过了家族替他写好的英雄结局；真正的恢复始于活着不再需要向那份失落剧本证明自己。":"丹中尉活過了家族替他寫好的英雄結局；真正的恢復始於活著不再需要向那份失落劇本證明自己。","学校、球队、军队与人群不断给阿甘估价；他最有力的回答不是证明自己合格，而是始终看一个人实际做了什么。":"學校、球隊、軍隊與人群不斷給阿甘估價；他最有力的回答不是證明自己合格，而是始終看一個人實際做了什麼。","珍妮与电影没有给她的生活":"珍妮與電影沒有給她的生活","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这三篇沿着这组张力展开。阿甘不轻易用标签穷尽别人，具有真实的道德意义，却不必因此被写成普遍无瑕的天真者。丹中尉的故事不只是走出绝望，而是谁有权在继承来的结局崩塌后重写一生。珍妮的故事确实拍下了虐待、愤怒与逃离，却大多仍由别人叙述。电影的温暖与限度，需要放在一起看。":"這三篇沿著這組張力展開。阿甘不輕易用標籤窮盡別人，具有真實的道德意義，卻不必因此被寫成普遍無瑕的天真者。丹中尉的故事不只是走出絕望，而是誰有權在繼承來的結局崩塌後重寫一生。珍妮的故事確實拍下了虐待、憤怒與逃離，卻大多仍由別人敘述。電影的溫暖與限度，需要放在一起看。","阿甘常常不附带道德条件地接住珍妮；电影却更吝啬：它准确拍下她的痛，却很少让她从内部持续讲述自己的一生。":"阿甘常常不附帶道德條件地接住珍妮；電影卻更吝嗇：它準確拍下她的痛，卻很少讓她從內部持續講述自己的一生。"};
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
