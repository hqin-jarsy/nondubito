/* Generated offline from essays/games/black-myth-wukong/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與互動敘事","《黑神话：悟空》从经典叙事的奖赏之后开始：孙悟空已经领受佛门能够给出的最高名分，又把它放下；一个无名的后来者被派去收集他的残余，而神、妖、引路人和档案都在替这趟路解释意义。":"《黑神話：悟空》從經典敘事的獎賞之後開始：孫悟空已經領受佛門能夠給出的最高名分，又把它放下；一個無名的後來者被派去收集他的殘餘，而神、妖、引路人和檔案都在替這趟路解釋意義。","《黑神话：悟空》解读":"《黑神話：悟空》解讀","他要的不是真相，是赢":"他要的不是真相，是贏","四篇从沉默的天命人、悟空散落的六根、黄眉制造出来的人性证据，读到那只在睁眼之前停住的金箍。":"四篇從沉默的天命人、悟空散落的六根、黃眉製造出來的人性證據，讀到那隻在睜眼之前停住的金箍。","天命人可以靠自己的行动挣到全部本事，却仍在最要紧的一问前等待另一个人的“意”。":"天命人可以靠自己的行動掙到全部本事，卻仍在最要緊的一問前等待另一個人的“意”。","所有人都在命名、排序、指路并解释那个沉默的主角；“天命人”只说清了他应当承接谁的目的。":"所有人都在命名、排序、指路並解釋那個沉默的主角；“天命人”只說清了他應當承接誰的目的。","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这个系列会区分游戏明确给出的情节与据此作出的解释。人物动机和阵营被有意留白，而这份未完成，正对应天命人究竟是在成为自己，还是被组装进一个角色的问题。":"這個系列會區分遊戲明確給出的情節與據此作出的解釋。人物動機和陣營被有意留白，而這份未完成，正對應天命人究竟是在成為自己，還是被組裝進一個角色的問題。","隐藏结局没有推翻天庭，也没有完成一个自我；它只让金箍没有落下，并给沉默的主角留下一个表态动作。":"隱藏結局沒有推翻天庭，也沒有完成一個自我；它只讓金箍沒有落下，並給沉默的主角留下一個表態動作。","黄眉先制造产生证据的处境，再把其中的反应称作人性，最后把自己放到“天”的位置。":"黃眉先製造產生證據的處境，再把其中的反應稱作人性，最後把自己放到“天”的位置。"};
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
