/* Generated offline from essays/literature/rickshaw-boy/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 三篇解读 · 文学评论":"系列 · 三篇解讀 · 文學評論","《骆驼祥子》解读":"《駱駝祥子》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇文章，从一辆三次失去的车、虎妞与小福子的受限选择，到一个仍活着却发生了不止贫困之变化的人。":"三篇文章，從一輛三次失去的車、虎妞與小福子的受限選擇，到一個仍活著卻發生了不止貧困之變化的人。","祥子要的东西很小也很清楚：拥有自己拉的车，让劳动所得属于自己。他强壮、自律、肯积攒，几乎是个人奋斗叙事最有利的候选人。那个计划一次次被毁，检验的是“努力能够保住独立自我”的承诺。":"祥子要的東西很小也很清楚：擁有自己拉的車，讓勞動所得屬於自己。他強壯、自律、肯積攢，幾乎是個人奮鬥敘事最有利的候選人。那個計畫一次次被毀，檢驗的是“努力能夠保住獨立自我”的承諾。","三篇文章同时拒绝简单的受害者故事与道德堕落故事。结构反复剥夺祥子劳动的结果；他也学会了这套逻辑，并开始把成本转给别人。结尾之所以黑暗，是因为肉身仍然生存，而组织这个人的判断已经受损。":"三篇文章同時拒絕簡單的受害者故事與道德墮落故事。結構反覆剝奪祥子勞動的結果；他也學會了這套邏輯，並開始把成本轉給別人。結尾之所以黑暗，是因為肉身仍然生存，而組織這個人的判斷已經受損。","老舍《骆驼祥子》。全书剧透。":"老舍《駱駝祥子》。全書劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他要的是一辆车":"他要的是一輛車","祥子那项朴素计划三次被毁，检验了自律能否把劳动转换成独立所有。":"祥子那項樸素計畫三次被毀，檢驗了自律能否把勞動轉換成獨立所有。","英 · 简 · 繁":"英 · 簡 · 繁","两个女人在强制条件中行动——一个夺取婚姻，一个出卖自身——而祥子的选择参与塑造了她们的命运。":"兩個女人在強制條件中行動——一個奪取婚姻，一個出賣自身——而祥子的選擇參與塑造了她們的命運。","他还活着":"他還活著","祥子的喝酒、偷懒、欺骗与出卖不只是更穷，而是他开始采用城市把成本转给别人的规则。":"祥子的喝酒、偷懶、欺騙與出賣不只是更窮，而是他開始採用城市把成本轉給別人的規則。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
