/* Generated offline from geass/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《反叛的鲁路修》先让支配显得痛快，再让观众看见支配真正拿走的东西：不是行动能力，而是那个使行动仍属于行动者的停止能力。":"《反叛的魯路修》先讓支配顯得痛快，再讓觀眾看見支配真正拿走的東西：不是行動能力，而是那個使行動仍屬於行動者的停止能力。","《反叛的鲁路修》解读":"《反叛的魯路修》解讀","一个反派也没有":"一個反派也沒有","三种政治方案分别取消谎言、拒绝或一个被憎恨的统治者；共同错误发生在计算之前的人之换算。":"三種政治方案分別取消謊言、拒絕或一個被憎恨的統治者；共同錯誤發生在計算之前的人之換算。","五篇从Geass拿走的“不”出发，读到保护、政治方案、无法验证的同意，以及一场成功牺牲留下的道德余项。":"五篇從Geass拿走的“不”出發，讀到保護、政治方案、無法驗證的同意，以及一場成功犧牲留下的道德餘項。","五篇把这个问题从超自然命令推到爱、保护与政治设计，最后追问自愿牺牲一旦需要第二个人永久承担，是否仍只是“牺牲自己”。简体中文保留作者底稿并校正少量设定与过强措辞；繁体中文按台湾读者习惯编辑；英文为独立重写。":"五篇把這個問題從超自然命令推到愛、保護與政治設計，最後追問自願犧牲一旦需要第二個人永久承擔，是否仍只是“犧牲自己”。簡體中文保留作者底稿並校正少量設定與過強措辭；繁體中文按臺灣讀者習慣編輯；英文為獨立重寫。","他从来没有问过她":"他從來沒有問過她","他们无法确认自己":"他們無法確認自己","她说了不，然后照做了":"她說了不，然後照做了","尤菲米娅的灾难揭示Geass真正拿走的不是人格，而是让判断转化为停止的能力。":"尤菲米婭的災難揭示Geass真正拿走的不是人格，而是讓判斷轉化為停止的能力。","系列 · 五篇解读 · 文化评论":"系列 · 五篇解讀 · 文化評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那道命令从来没有解除":"那道命令從來沒有解除","鲁路修可以决定耗尽自己；道德余项出现在方案需要朱雀受限的同意与娜娜莉未经选择的未来之处。":"魯路修可以決定耗盡自己；道德餘項出現在方案需要朱雀受限的同意與娜娜莉未經選擇的未來之處。","鲁路修听见娜娜莉的愿望却判定它们不作数，于是保护滑成替代，她的名字则支撑了一场她未曾要求的战争。":"魯路修聽見娜娜莉的願望卻判定它們不作數，於是保護滑成替代，她的名字則支撐了一場她未曾要求的戰爭。","黑色骑士团面对的不只是鲁路修的人品，而是再也没有可靠方法确认过去的忠诚是否属于自己。":"黑色騎士團面對的不只是魯路修的人品，而是再也沒有可靠方法確認過去的忠誠是否屬於自己。"};
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
