/* Generated offline from kafka-on-the-shore/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《海边的卡夫卡》解读":"《海邊的卡夫卡》解讀","《海边的卡夫卡》让许多对应彼此照亮，却不肯合成唯一答案：一场谋杀与一次昏迷、成年的佐伯与十五岁的幻影、以卡夫卡为名的少年与他心里的“乌鸦”。关系确实存在，小说却不把它们变成一张封闭的谜底表。":"《海邊的卡夫卡》讓許多對應彼此照亮，卻不肯合成唯一答案：一場謀殺與一次昏迷、成年的佐伯與十五歲的幻影、以卡夫卡為名的少年與他心裡的“烏鴉”。關係確實存在，小說卻不把它們變成一張封閉的謎底表。","一条可以开合的边界接通两个世界，却不解释它们；古老神话照亮其形状，却不是唯一钥匙。":"一條可以開合的邊界接通兩個世界，卻不解釋它們；古老神話照亮其形狀，卻不是唯一鑰匙。","五篇从占住孩子未来的父亲预言、中田被分开的生命与不先索取完整身份的图书馆，读到入口石，以及从无需再作选择的世界返回。":"五篇從佔住孩子未來的父親預言、中田被分開的生命與不先索取完整身份的圖書館，讀到入口石，以及從無需再作選擇的世界返回。","图书馆":"圖書館","小说里最温柔的地方没有替卡夫卡解开身份，而是在谜底出现以前先让他留下。":"小說裡最溫柔的地方沒有替卡夫卡解開身份，而是在謎底出現以前先讓他留下。","文学细读":"文學細讀","森林聚落提供无需再选择的安静；卡夫卡却回到伤口仍未解决、未来仍会发生的世界。":"森林聚落提供無需再選擇的安靜；卡夫卡卻回到傷口仍未解決、未來仍會發生的世界。","父亲预言弑父与乱伦；孩子即使反抗，也只能先围着别人塞给他的身份运转。":"父親預言弒父與亂倫；孩子即使反抗，也只能先圍著別人塞給他的身份運轉。","系列 · 五篇解读 · 文学评论":"系列 · 五篇解讀 · 文學評論","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","补助接住了中田的生活，却解释不了童年的灾变，也装不下灾变之后出现的能力。":"補助接住了中田的生活，卻解釋不了童年的災變，也裝不下災變之後出現的能力。","诅咒":"詛咒","这版解读因此把不确定视为作品伦理的一部分，而不是尚未做完的猜谜。它追问一段被指定的故事如何占据人生、照顾如何先于分类发生，以及为什么回到没有解决的问题之中，反而比逃离更困难。含全书剧透。":"這版解讀因此把不確定視為作品倫理的一部分，而不是尚未做完的猜謎。它追問一段被指定的故事如何佔據人生、照顧如何先於分類發生，以及為什麼回到沒有解決的問題之中，反而比逃離更困難。含全書劇透。","阅读全文":"閱讀全文"};
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
