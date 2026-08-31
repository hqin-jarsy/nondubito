/* Generated offline from smiling-proud-wanderer/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 武侠":"← 武俠","《笑傲江湖》从一场无法获准的退出开始。门派、名号、盟旗、秘笈与世仇不只规定人该做什么，还规定人必须成为什么。":"《笑傲江湖》從一場無法獲准的退出開始。門派、名號、盟旗、秘笈與世仇不只規定人該做什麼，還規定人必須成為什麼。","《笑傲江湖》解读":"《笑傲江湖》解讀","一个喝酒的男人做了尼姑庵掌门，却没有改造她们；结尾同样是一副被锁住的样子，关键在谁伸出了手。":"一個喝酒的男人做了尼姑庵掌門，卻沒有改造她們；結尾同樣是一副被鎖住的樣子，關鍵在誰伸出了手。","一个由江湖授予的名号必须不断向江湖交作业；当维持“君子”比成为君子更重要，秘密便开始吞掉人。":"一個由江湖授予的名號必須不斷向江湖交作業；當維持“君子”比成為君子更重要，秘密便開始吞掉人。","一统":"一統","五岳并派与日月神教表面相反，位子却不断制造同一种语言、忠诚与姿势；换人并不等于换结构。":"五嶽並派與日月神教表面相反，位子卻不斷製造同一種語言、忠誠與姿勢；換人並不等於換結構。","五篇从无招、君子剑与一场合奏出发，读正邪和一统如何运转，也读同一把锁怎样分别成为强迫与自愿的关系。":"五篇從無招、君子劍與一場合奏出發，讀正邪和一統如何運轉，也讀同一把鎖怎樣分別成為強迫與自願的關係。","刘正风与曲洋被追究的不是行为，而是关系本身；他们交给后来人的不是立场，也不是复仇，而是一支曲子。":"劉正風與曲洋被追究的不是行為，而是關係本身；他們交給後來人的不是立場，也不是復仇，而是一支曲子。","君子剑":"君子劍","思过崖上的处罚把令狐冲送进了从未被考核的招式之间；无招不是空白，而是把已有之物长成自己的判断。":"思過崖上的處罰把令狐沖送進了從未被考核的招式之間；無招不是空白，而是把已有之物長成自己的判斷。","无招":"無招","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这五篇沿着小说的另一条暗线来读：无法被偷走的功夫、必须与另一个人合成的音乐、用来保护而不是吞并的位子，以及不以认同为条件的关系。全文包含结局剧透。":"這五篇沿著小說的另一條暗線來讀：無法被偷走的功夫、必須與另一個人合成的音樂、用來保護而不是吞併的位子，以及不以認同為條件的關係。全文包含結局劇透。","那把锁":"那把鎖"};
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
