/* Generated offline from essays/film/dying-to-survive/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《我不是药神》最有力量之处，是不让我们靠找出一个坏人获得轻松答案。创新、药品安全、执法、可负担性与病人想活下去的愿望，都提出了不能随手取消的要求。这三篇留在它们的碰撞中，也会把电影改编与真实案件、当时法律和后续变化分开。":"《我不是藥神》最有力量之處，是不讓我們靠找出一個壞人獲得輕鬆答案。創新、藥品安全、執法、可負擔性與病人想活下去的願望，都提出了不能隨手取消的要求。這三篇留在它們的碰撞中，也會把電影改編與真實案件、當時法律和後續變化分開。","《我不是药神》解读":"《我不是藥神》解讀","三篇解读：有正当理由却合成绝境的规则、一个逐利者的第二次返回，以及从未成为圣人的人做出的微小拒绝。":"三篇解讀：有正當理由卻合成絕境的規則、一個逐利者的第二次返回，以及從未成為聖人的人做出的微小拒絕。","专利、审批与执法各自保护真实利益，却仍可能在合流后让病人无路可活。":"專利、審批與執法各自保護真實利益，卻仍可能在合流後讓病人無路可活。","他们没有一个是圣人":"他們沒有一個是聖人","他第一次去，是为了钱":"他第一次去，是為了錢","依据文牧野执导的二〇一八年电影《我不是药神》，故事部分取材于陆勇案但人物与结局均经改编；药品法律表述已按影片时代背景及后续修法校订。":"依據文牧野執導的二〇一八年電影《我不是藥神》，故事部分取材於陸勇案但人物與結局均經改編；藥品法律表述已按影片時代背景及後續修法校訂。","吕受益死后，程勇的返回并非成圣，而是远方的病人变成了一个他再也无法假装没看见的人。":"呂受益死後，程勇的返回並非成聖，而是遠方的病人變成了一個他再也無法假裝沒看見的人。","每一条规定都有理由":"每一條規定都有理由","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","警察、骗子、舞者、牧师与年轻病人，都遇到一个原有角色再也给不出足够指令的瞬间。":"警察、騙子、舞者、牧師與年輕病人，都遇到一個原有角色再也給不出足夠指令的瞬間。"};
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
