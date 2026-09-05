/* Generated offline from essays/literature/don-quixote/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《堂吉诃德》解读":"《堂吉訶德》解讀","两本书":"兩本書","五篇文章，从堂吉诃德不再重复的试验、听不见拒绝的援助，到桑丘在假官位上作出的真判断、两本争夺他的书，以及无人愿意接受的最后清醒。":"五篇文章，從堂吉訶德不再重複的試驗、聽不見拒絕的援助，到桑丘在假官位上作出的真判斷、兩本爭奪他的書，以及無人願意接受的最後清醒。","他不再试了":"他不再試了","堂吉诃德知道怎样检验纸盔；真正奠定他身份的动作，是把决定性的检验从允许追问的问题里删掉。":"堂吉訶德知道怎樣檢驗紙盔；真正奠定他身份的動作，是把決定性的檢驗從允許追問的問題裡刪掉。","塞万提斯的喜剧不只是拿幻想对照现实。它追问幻想让什么成为可能、又伤害了谁，别人如何拒绝被分配的角色，以及为什么清醒有时也以失去的形式到来。这组文章从小说最小的检验处进入。":"塞萬提斯的喜劇不只是拿幻想對照現實。它追問幻想讓什麼成為可能、又傷害了誰，別人如何拒絕被分配的角色，以及為什麼清醒有時也以失去的形式到來。這組文章從小說最小的檢驗處進入。","巴拉塔里亚":"巴拉塔里亞","当所有人都读过关于他的书，堂吉诃德以改道使伪续成为谎言，又要求一份法律证词证明自己就是自己。":"當所有人都讀過關於他的書，堂吉訶德以改道使偽續成為謊言，又要求一份法律證詞證明自己就是自己。","当救助者把英雄动作当成完成，却不等被救者真正安全，救助便成了伤害；安德列斯最终只能请求他别再帮忙。":"當救助者把英雄動作當成完成，卻不等被救者真正安全，救助便成了傷害；安德列斯最終只能請求他別再幫忙。","最后那一觉":"最後那一覺","本文依据董燕生译本（湖南文艺出版社），人名地名从该本。另有杨绛、孙家孟、屠孟超等译本通行。全书剧透。":"本文依據董燕生譯本（湖南文藝出版社），人名地名從該本。另有楊絳、孫家孟、屠孟超等譯本通行。全書劇透。","桑丘在虚构官位上作出真实判断，又在不曾真正承认他的人撤回角色以前，选择把自己完整地带走。":"桑丘在虛構官位上作出真實判斷，又在不曾真正承認他的人撤回角色以前，選擇把自己完整地帶走。","清醒的阿隆索·基哈诺回来时，堂吉诃德也将死去；从未真正相信故事的桑丘，反而成了最后想把共同幻想留下的人。":"清醒的阿隆索·基哈諾回來時，堂吉訶德也將死去；從未真正相信故事的桑丘，反而成了最後想把共同幻想留下的人。","系列 · 五篇解读 · 文学评论":"系列 · 五篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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
