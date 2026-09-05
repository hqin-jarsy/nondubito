/* Generated offline from essays/literature/catch-22/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《第二十二条军规》解读":"《第二十二條軍規》解讀","四篇文章，从无人见过的军规、米洛把人人纳入的完美账本，到正确处理下被遮住的致命伤，以及约塞连既需要出路、也需要让他走的人。":"四篇文章，從無人見過的軍規、米洛把人人納入的完美賬本，到正確處理下被遮住的致命傷，以及約塞連既需要出路、也需要讓他走的人。","宪兵上楼的时候":"憲兵上樓的時候","宪兵走过米凯拉的尸体，上楼逮捕没有通行证的约塞连；奥尔的路线与两位朋友的承认相遇后，逃离才真正可能。":"憲兵走過米凱拉的屍體，上樓逮捕沒有通行證的約塞連；奧爾的路線與兩位朋友的承認相遇後，逃離才真正可能。","本文依据上海译文出版社南文、赵守垠、王德明译本（主万校），人名地名从该本。全书剧透。":"本文依據上海譯文出版社南文、趙守垠、王德明譯本（主萬校），人名地名從該本。全書劇透。","每个人都有一份":"每個人都有一份","海勒的荒诞很少是随机的：程序总在错误对象周围完美运转，规则也因找不到作者而变得更强。这组文章追踪那些无法被官僚系统容纳、只能被归入错误、怯懦或不存在的人。":"海勒的荒誕很少是隨機的：程序總在錯誤對象周圍完美運轉，規則也因找不到作者而變得更強。這組文章追蹤那些無法被官僚系統容納、只能被歸入錯誤、怯懦或不存在的人。","第二十二条军规不需要固定条文，它的名字就是为了终止“凭什么”；合理的局部规则合成了没有作者、也无人能撤销的结构。":"第二十二條軍規不需要固定條文，它的名字就是為了終止“憑什麼”；合理的局部規則合成了沒有作者、也無人能撤銷的結構。","米洛通过把每个人都换算成股东来包容所有人；他无懈可击的账本里，没有一栏留给无法定价之物。":"米洛通過把每個人都換算成股東來包容所有人；他無懈可擊的賬本裡，沒有一欄留給無法定價之物。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","约塞连把看得见的伤处理得每一步都正确，隐藏的伤却杀死斯诺登；小说反复重讲，直到读者自己的遮蔽物也被掀开。":"約塞連把看得見的傷處理得每一步都正確，隱藏的傷卻殺死斯諾登；小說反覆重講，直到讀者自己的遮蔽物也被掀開。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那条谁也没见过的军规":"那條誰也沒見過的軍規","防弹衣底下那处伤":"防彈衣底下那處傷"};
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
