/* Generated offline from return-of-condor-heroes/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 武侠":"← 武俠","《神雕侠侣》解读":"《神鵰俠侶》解讀","《神雕侠侣》追问：当一个人的少年被旧债、恐惧与规矩安排之后，还有什么能够真正成为自己的？杨过得到的不是完整门派，而是扣下的教法、完整的交付、遗弃的兵器、不会说话的同伴与无法补回的损失。":"《神鵰俠侶》追問：當一個人的少年被舊債、恐懼與規矩安排之後，還有什麼能夠真正成為自己的？楊過得到的不是完整門派，而是扣下的教法、完整的交付、遺棄的兵器、不會說話的同伴與無法補回的損失。","两个人在全书最深的道德分歧上从未互相说服，最后却因不同理由站上了同一堵城墙。":"兩個人在全書最深的道德分歧上從未互相說服，最後卻因不同理由站上了同一堵城牆。","五篇从被别人旧账安排的孤儿、师徒之恋与一条断臂出发，读救命的谎言、自己长出的武功，以及两种互不认同的法如何站上同一堵城墙。":"五篇從被別人舊賬安排的孤兒、師徒之戀與一條斷臂出發，讀救命的謊言、自己長出的武功，以及兩種互不認同的法如何站上同一堵城牆。","孤儿":"孤兒","小龙女知道他不会为自己活，却会为一个约活；一次替他做主的欺骗，成为十六年无人监管的生命框架。":"小龍女知道他不會為自己活，卻會為一個約活；一次替他做主的欺騙，成為十六年無人監管的生命框架。","师徒":"師徒","断臂":"斷臂","旧债、恐惧、怜悯与临终承诺轮流决定孤儿该去哪里；在有人看见他之前，理由已经从别处写好。":"舊債、恐懼、憐憫與臨終承諾輪流決定孤兒該去哪裡；在有人看見他之前，理由已經從別處寫好。","祖师未走成的情路变成后人的门规；几代之后，一段关系只能在最正直的人也拒绝承认时自己活下去。":"祖師未走成的情路變成後人的門規；幾代之後，一段關係只能在最正直的人也拒絕承認時自己活下去。","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","襄阳":"襄陽","这五篇沿着他怎样用不均匀的继承拼成一生来读。结果不是摆脱一切关系，而是让关系与义务不再完全由制度预先写好。全文包含结局剧透。":"這五篇沿著他怎樣用不均勻的繼承拼成一生來讀。結果不是擺脫一切關係，而是讓關係與義務不再完全由制度預先寫好。全文包含結局劇透。","郭芙的一时冲动成为另一个人的永久损失；此后发生的不是补偿，而是杨过对剩余材料的重新排列。":"郭芙的一時衝動成為另一個人的永久損失；此後發生的不是補償，而是楊過對剩餘材料的重新排列。"};
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
