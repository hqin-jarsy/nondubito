/* Generated offline from essays/wuxia/the-legendary-siblings/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 武侠":"← 武俠","系列 · 5 篇解读":"系列 · 5 篇解讀","《绝代双骄》解读":"《絕代雙驕》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","Independent English · 简 / 繁":"Independent English · 簡 / 繁","五篇从一个为救人而编出的复仇计划出发，细读恶人谷与移花宫的两种教育、被经营出来的大侠名声，以及一场双方都准备替对方死去的决斗。":"五篇從一個為救人而編出的復仇計劃出發，細讀惡人谷與移花宮的兩種教育、被經營出來的大俠名聲，以及一場雙方都準備替對方死去的決鬥。","《绝代双骄》里，几乎每个人都想替另一个人把一生预先写完：邀月替两个婴儿写下二十年后的结局，十大恶人想造出一件最完美的凶器，移花宫把服从做成无缺的人格，江别鹤则造出一个让整个江湖替他维护的自己。":"《絕代雙驕》裡，幾乎每個人都想替另一個人把一生預先寫完：邀月替兩個嬰兒寫下二十年後的結局，十大惡人想造出一件最完美的兇器，移花宮把服從做成無缺的人格，江別鶴則造出一個讓整個江湖替他維護的自己。","小说一次次让人学会别人教给他的东西，又把它用向别处。这五篇细读的，正是教育与一生之间那一点始终无法被写完的距离。全文包含结局剧透。":"小說一次次讓人學會別人教給他的東西，又把它用向別處。這五篇細讀的，正是教育與一生之間那一點始終無法被寫完的距離。全文包含結局劇透。","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","一个计划":"一個計劃","怜星为救两个婴儿，临时编出一场二十年后的兄弟相残；计划救下了当天的生命，也试图占有他们尚未开始的一生。":"憐星為救兩個嬰兒，臨時編出一場二十年後的兄弟相殘；計劃救下了當天的生命，也試圖佔有他們尚未開始的一生。","英 · 简 · 繁":"英 · 簡 · 繁","恶人谷":"惡人谷","五个恶人把最拿手的本事毫无保留地教给小鱼儿，想造出天下最恶的人；他学会了一切，却把本事用向了他们没有规定的地方。":"五個惡人把最拿手的本事毫無保留地教給小魚兒，想造出天下最惡的人；他學會了一切，卻把本事用向了他們沒有規定的地方。","移花宫":"移花宮","花无缺得到最好的武功、礼法与品性，却始终得不到杀人的理由；他无法不赴约，只能决定让自己死在朋友手里。":"花無缺得到最好的武功、禮法與品性，卻始終得不到殺人的理由；他無法不赴約，只能決定讓自己死在朋友手裡。","卖掉主人消息的书僮，二十年后成了人人敬仰的江南大侠；江别鹤最厉害的武功，是让整个江湖替他解释。":"賣掉主人消息的書僮，二十年後成了人人敬仰的江南大俠；江別鶴最厲害的武功，是讓整個江湖替他解釋。","那一战":"那一戰","邀月的计划每一步都成功了，却在最后一剑前失去效力：她能安排兄弟的一切，唯独不能替他们决定那一剑落向谁。":"邀月的計劃每一步都成功了，卻在最後一劍前失去效力：她能安排兄弟的一切，唯獨不能替他們決定那一劍落向誰。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {
    var mode = document.documentElement.getAttribute('data-lang') || 'en';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle) ? variants[originalTitle] : originalTitle;
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-card, .lang-toggle, .footer-langs, script, style')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      var source = originals.get(node);
      node.nodeValue = traditional && Object.prototype.hasOwnProperty.call(variants, source) ? variants[source] : source;
    }
  }
  document.addEventListener('DOMContentLoaded', function() {
    updateTraditionalReadingMode();
    new MutationObserver(function(records) { if (records.some(function(record) { return record.attributeName === 'data-lang'; })) updateTraditionalReadingMode(); }).observe(document.documentElement, {attributes:true, attributeFilter:['data-lang']});
  });
})();
