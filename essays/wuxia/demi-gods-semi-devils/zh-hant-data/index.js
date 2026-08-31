/* Generated offline from demi-gods-semi-devils/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 武侠":"← 武俠","《天龙八部》把功力、姓名、父母、义务与敌人一并交给人物，而这些东西几乎都不是他们选的。知道真相并不等于脱离那条在别处写好的路。":"《天龍八部》把功力、姓名、父母、義務與敵人一併交給人物，而這些東西幾乎都不是他們選的。知道真相併不等於脫離那條在別處寫好的路。","《天龙八部》解读":"《天龍八部》解讀","一个拒绝学武的王子得到逃、吸与时灵时不灵的绝技；功夫不是他选的，功夫做什么仍由他决定。":"一個拒絕學武的王子得到逃、吸與時靈時不靈的絕技；功夫不是他選的，功夫做什麼仍由他決定。","一手自杀棋解开了三十年的死局；此后所有硬塞给虚竹的东西，都在他手里得到另一种处置。":"一手自殺棋解開了三十年的死局；此後所有硬塞給虛竹的東西，都在他手裡得到另一種處置。","一条假消息替一个婴儿安排了敌人、姓名与分裂的一生；此后每一边都只肯让萧峰成为一种人。":"一條假訊息替一個嬰兒安排了敵人、姓名與分裂的一生；此後每一邊都只肯讓蕭峰成為一種人。","五篇从雁门关、珍珑棋局与凌波微步出发，读出生前就被写好的身份、未经同意的继承，以及一笔血账如何在双方都不再索取时才真正结束。":"五篇從雁門關、珍瓏棋局與凌波微步出發，讀出生前就被寫好的身份、未經同意的繼承，以及一筆血賬如何在雙方都不再索取時才真正結束。","佛经里的八部众为全书定下眼光：没有一个人能被一个名目装完，而几乎每个人都活在出生前留下的账里。":"佛經裡的八部眾為全書定下眼光：沒有一個人能被一個名目裝完，而幾乎每個人都活在出生前留下的賬裡。","复国在慕容复会说话前就写进了姓名；朋友、爱情、谱系乃至现实本身，随后都变成可以折算的材料。":"復國在慕容復會說話前就寫進了姓名；朋友、愛情、譜系乃至現實本身，隨後都變成可以折算的材料。","珍珑":"珍瓏","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这五篇把小说读作一部关于继承目的的史诗：人未必能拒绝所有来路，却仍可能决定拿到手的材料用来做什么。全文包含结局剧透。":"這五篇把小說讀作一部關於繼承目的的史詩：人未必能拒絕所有來路，卻仍可能決定拿到手的材料用來做什麼。全文包含結局劇透。","释名":"釋名","雁门关":"雁門關"};
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
