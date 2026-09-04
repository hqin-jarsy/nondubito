/* Generated offline from essays/wuxia/sentimental-swordsman-ruthless-sword/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 武侠":"← 武俠","系列 · 4 篇解读":"系列 · 4 篇解讀","《多情剑客无情剑》解读":"《多情劍客無情劍》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","Independent English · 简 / 繁":"Independent English · 簡 / 繁","四篇从一场没有问过当事人的“成全”、一张先排除再排名的兵器谱与被接管的判断出发，读到一个人怎样把自我牺牲也变成了处理自己的办法。":"四篇從一場沒有問過當事人的“成全”、一張先排除再排名的兵器譜與被接管的判斷出發，讀到一個人怎樣把自我犧牲也變成了處理自己的辦法。","古龙在这部小说里把几种熟悉的武侠美德翻到了背面：报恩可能替受益者作决定，排名可能制造它声称只是在记录的厮杀，爱情可以占住一个人的判断，自我牺牲也可能沿用支配他人的同一种办法。":"古龍在這部小說裡把幾種熟悉的武俠美德翻到了背面：報恩可能替受益者作決定，排名可能製造它聲稱只是在記錄的廝殺，愛情可以佔住一個人的判斷，自我犧牲也可能沿用支配他人的同一種辦法。","这四篇不把后台框架摆到台前，而是留在人物实际经历的关系里细读。全文包含结局剧透。":"這四篇不把後臺框架擺到臺前，而是留在人物實際經歷的關係裡細讀。全文包含結局劇透。","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","让":"讓","李寻欢把爱人、家业与真相一并“让”给义兄；只有没有被问过的林诗音，看见了这段佳话里被拿走的决定。":"李尋歡把愛人、家業與真相一併“讓”給義兄；只有沒有被問過的林詩音，看見了這段佳話裡被拿走的決定。","英 · 简 · 繁":"英 · 簡 · 繁","兵器谱":"兵器譜","百晓生把四十三名高手排成一列，却先规定女人与“魔道”不算；榜上的人此后不只活自己的命，也活那个号码。":"百曉生把四十三名高手排成一列，卻先規定女人與“魔道”不算；榜上的人此後不只活自己的命，也活那個號碼。","林仙儿":"林仙兒","阿飞失去的不是一个恋人，而是自己的判断必须先经过另一个人的许可；书反复数她的情欲，却很少数这种占有。":"阿飛失去的不是一個戀人，而是自己的判斷必須先經過另一個人的許可；書反覆數她的情慾，卻很少數這種佔有。","李寻欢把牺牲朝外做成了义，朝内做成了深情；只有孙小红不赞美他的咳血，而是要求他活下去。":"李尋歡把犧牲朝外做成了義，朝內做成了深情；只有孫小紅不讚美他的咳血，而是要求他活下去。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
