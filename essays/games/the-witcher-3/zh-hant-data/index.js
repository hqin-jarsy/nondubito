/* Generated offline from essays/games/the-witcher-3/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Game criticism":"English · 簡 / 繁 · Game criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與交互敘事","《巫师3》以艰难选择闻名，但“难选”本身并不是它真正的成就。最好的任务会继续追问：谁在选择，谁在付账，一个听起来仁慈的目的是否仍会把另一个人当成材料。":"《巫師3》以艱難選擇聞名，但“難選”本身並不是它真正的成就。最好的任務會繼續追問：誰在選擇，誰在付賬，一個聽起來仁慈的目的是否仍會把另一個人當成材料。","《巫师3：狂猎》解读":"《巫師3：狂獵》解讀","他没有替她做":"他沒有替她做","他自己把话说准了":"他自己把話說准了","呢喃山丘的选择把死亡分给孩子、村民、安娜与男爵；少见的任务顺序会改变结果，却没有把决定变成没有代价的第三条路。":"呢喃山丘的選擇把死亡分給孩子、村民、安娜與男爵；少見的任務順序會改變結果，卻沒有把決定變成沒有代價的第三條路。","四篇从血腥男爵准确却无力的认账、威伦名题里被分配给别人的代价，读到围绕希里展开的计划，以及杰洛特五次没有替她生活。":"四篇從血腥男爵準確卻無力的認賬、威倫名題裡被分配給別人的代價，讀到圍繞希里展開的計劃，以及傑洛特五次沒有替她生活。","所有人都要她那样东西":"所有人都要她那樣東西","没有干净的选项":"沒有乾淨的選項","狂猎、阿瓦拉克、女术士集会与恩希尔各有目的；保护和爱也可能长成一份计划，让希里的力量比她自己的回答更重要。":"狂獵、阿瓦拉克、女術士集會與恩希爾各有目的；保護和愛也可能長成一份計劃，讓希里的力量比她自己的回答更重要。","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","血腥男爵最终没有用语法挪走责任，而是准确说出自己的暴力；准确不能撤销伤害，承认也不会自动变成改变。":"血腥男爵最終沒有用語法挪走責任，而是準確說出自己的暴力；準確不能撤銷傷害，承認也不會自動變成改變。","这四篇从威伦走到希里面前。杰洛特无法把所有后果洗干净，也不能替她面对白霜；他能做的，是让她最后的行动仍然属于她。":"這四篇從威倫走到希里面前。傑洛特無法把所有後果洗乾淨，也不能替她面對白霜；他能做的，是讓她最後的行動仍然屬於她。","雪仗、拒收的钱、门外的等待、被砸的实验室和史凯裘的坟，让希里知道杰洛特既相信她能行动，也没有把她独自丢下。":"雪仗、拒收的錢、門外的等待、被砸的實驗室和史凱裘的墳，讓希里知道傑洛特既相信她能行動，也沒有把她獨自丟下。"};
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
