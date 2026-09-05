/* Generated offline from essays/literature/les-miserables/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《悲惨世界》解读":"《悲慘世界》解讀","五篇文章，从仍需社会缝隙才能落地的宽恕、芳汀被一连串合理决定拆散，到把自己活成法律的沙威、开着出口的败局，以及冉阿让那次并非必要的自白。":"五篇文章，從仍需社會縫隙才能落地的寬恕、芳汀被一連串合理決定拆散，到把自己活成法律的沙威、開著出口的敗局，以及冉阿讓那次並非必要的自白。","他们知道自己会输":"他們知道自己會輸","安灼拉说出实情、打开出口，又赶走身后有人等待的人；败局不能把留下的守卫者变成他的材料。":"安灼拉說出實情、打開出口，又趕走身後有人等待的人；敗局不能把留下的守衛者變成他的材料。","沉默本来完全安全，冉阿让仍向马吕斯说出真相；此后，日常的谨慎一步一步把他从珂赛特身边挪开。":"沉默本來完全安全，冉阿讓仍向馬呂斯說出真相；此後，日常的謹慎一步一步把他從珂賽特身邊挪開。","沙威把整个人建在法律上，因此冉阿让的宽恕不只挑战一种观念，还撤掉了他唯一会站的位置。":"沙威把整個人建在法律上，因此冉阿讓的寬恕不只挑戰一種觀念，還撤掉了他唯一會站的位置。","没有一个人想害她":"沒有一個人想害她","米里哀主教的承认至关重要，但冉阿让还需要一座新城、一个新名字和档案的一道缝，才能长出另一种生活。":"米里哀主教的承認至關重要，但冉阿讓還需要一座新城、一個新名字和檔案的一道縫，才能長出另一種生活。","系列 · 五篇解读 · 文学评论":"系列 · 五篇解讀 · 文學評論","维克多·雨果《悲惨世界》，一八六二年出版。本文所据为李丹、方于译本。全书剧透。":"維克多·雨果《悲慘世界》，一八六二年出版。本文所據為李丹、方於譯本。全書劇透。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","那对烛台不够":"那對燭台不夠","除了德纳第夫妇，摧毁芳汀的多是作出局部合理选择的人；每一次决定的代价都向下传递。":"除了德納第夫婦，摧毀芳汀的多是作出局部合理選擇的人；每一次決定的代價都向下傳遞。","雨果关心的不只是孤立的恶，而是分类、职责、名声与日常谨慎如何叠加。这组文章追问，一个人凭什么能从判决里重新长出来，以及当承认到来却无处安放时，会发生什么。":"雨果關心的不只是孤立的惡，而是分類、職責、名聲與日常謹慎如何疊加。這組文章追問，一個人憑什麼能從判決裡重新長出來，以及當承認到來卻無處安放時，會發生什麼。"};
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
