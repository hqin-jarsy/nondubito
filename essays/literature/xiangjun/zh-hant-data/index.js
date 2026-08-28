/* Generated offline from xiangjun/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"\n        《香君》（こうくん，2022）是《精灵守护者》《鹿王》作者上桥菜穗子睽违七年的长篇奇幻小说。故事的核心是一种叫做欧阿勒稻的神奇谷物——它能养活整个帝国，但种植过它的土地再也无法生长其他任何东西。三篇解读分别追问：这种不可退出的丰饶是什么？被封为活神的人是什么？以及，一个能听到植物声音的15岁少女，究竟意味着什么？\n      ":"\n        《香君》（こうくん，2022）是《精靈守護者》《鹿王》作者上橋菜穗子睽違七年的長篇奇幻小說。故事的核心是一種叫做歐阿勒稻的神奇穀物——它能養活整個帝國，但種植過它的土地再也無法生長其他任何東西。三篇解讀分別追問：這種不可退出的豐饒是什麼？被封為活神的人是什麼？以及，一個能聽到植物聲音的15歲少女，究竟意味著什麼？\n      ","\n        《香君》，上桥菜穗子著，王华懋译，繁体中文版由春光出版社出版。\n      ":"\n        《香君》，上橋菜穗子著，王華懋譯，繁體中文版由春光出版社出版。\n      ","\n        上桥菜穗子用一种虚构的稻米，写了一个关于我们所有人的故事。当一个系统通过给予而非剥夺来实现控制，当丰饶本身成为枷锁，人还能不能听到自己的声音？\n      ":"\n        上橋菜穗子用一種虛構的稻米，寫了一個關於我們所有人的故事。當一個系統透過給予而非剝奪來實現控制，當豐饒本身成為枷鎖，人還能不能聽到自己的聲音？\n      ","\n        关于原著\n      ":"\n        關於原著\n      ","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《香君》解读系列":"《香君》解讀系列","《香君》解读系列 — Non Dubito":"《香君》解讀系列 — Non Dubito","一个15岁的少女能听到植物的声音。这不是她的超能力，首先是她的诅咒——因为当她告诉别人\"稻米在呼喊\"的时候，没有人听得懂。上桥菜穗子的高明之处在于，她没有让爱夏变成一个拯救者。":"一個15歲的少女能聽到植物的聲音。這不是她的超能力，首先是她的詛咒——因為當她告訴別人\"稻米在呼喊\"的時候，沒有人聽得懂。上橋菜穗子的高明之處在於，她沒有讓愛夏變成一個拯救者。","一个国王拒绝让人民种一种稻米，结果人民推翻了他——不是因为那种稻米有毒，而是因为它太好了。丰饶是最高明的控制，因为它不让你痛苦到想反抗，而是让你舒适到忘记了自己曾经可以不依赖任何人而活着。":"一個國王拒絕讓人民種一種稻米，結果人民推翻了他——不是因為那種稻米有毒，而是因為它太好了。豐饒是最高明的控制，因為它不讓你痛苦到想反抗，而是讓你舒適到忘記了自己曾經可以不依賴任何人而活著。","一种不可退出的丰饶":"一種不可退出的豐饒","八种语言 · 上桥菜穗子":"八種語言 · 上橋菜穗子","八种语言 · 书评 · 制度分析":"八種語言 · 書評 · 制度分析","八种语言 · 书评 · 生态与哲学":"八種語言 · 書評 · 生態與哲學","八种语言 · 书评 · 系统分析":"八種語言 · 書評 · 系統分析","八语版本":"八語版本","孤独的光":"孤獨的光","帝国最尊贵的存在，也是帝国中被最彻底剥夺了自我的人。身份越高，枷锁越重。被给予得越多的人，被拿走的也越多。一个体制最害怕的，往往不是它的敌人，而是它自己的承诺被真正兑现的那一刻。":"帝國最尊貴的存在，也是帝國中被最徹底剝奪了自我的人。身份越高，枷鎖越重。被給予得越多的人，被拿走的也越多。一個體制最害怕的，往往不是它的敵人，而是它自己的承諾被真正兌現的那一刻。","系列 · 三篇解读 · 奇幻文学":"系列 · 三篇解讀 · 奇幻文學"};
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
