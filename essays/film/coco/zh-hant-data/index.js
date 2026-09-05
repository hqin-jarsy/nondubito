/* Generated offline from essays/film/coco/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《寻梦环游记》从一个家庭应对抛弃的生存办法开始，以改写这套办法所依据的旧故事结束。三篇文章追问保护何时变成禁令、记忆怎样分配存在，以及修复传统为什么不同于抛弃传统。":"《尋夢環遊記》從一個家庭應對拋棄的生存辦法開始，以改寫這套辦法所依據的舊故事結束。三篇文章追問保護何時變成禁令、記憶怎樣分配存在，以及修復傳統為什麼不同於拋棄傳統。","《寻梦环游记》解读":"《尋夢環遊記》解讀","一个人还在不在，由活着的人说了算":"一個人還在不在，由活著的人說了算","一个家庭的禁令，执行了四代人":"一個家庭的禁令，執行了四代人","万寿菊桥把活人的记得变成一道关卡；埃克托想见可可的愿望，则让爱与对终极消失的恐惧无法彻底分开。":"萬壽菊橋把活人的記得變成一道關卡；埃克托想見可可的願望，則讓愛與對終極消失的恐懼無法徹底分開。","三篇解读：从保护延续成控制的家规、由记忆管理通行的亡灵世界，以及一首被偷走后重新回到最初听者的歌。":"三篇解讀：從保護延續成控制的家規、由記憶管理通行的亡靈世界，以及一首被偷走後重新回到最初聽者的歌。","伊梅尔达的禁令保存了被抛弃的教训，却逐渐听不见米格；被撕照片留下的沉默里，他秘密长成了音乐家。":"伊梅爾達的禁令保存了被拋棄的教訓，卻逐漸聽不見米格；被撕照片留下的沈默裡，他秘密長成了音樂家。","依据李·昂克里奇与阿德里安·莫利纳执导、皮克斯出品的二〇一七年动画长片《寻梦环游记》。文中区分影片明确给出的亡灵规则与由视觉和伦理结构作出的解读。":"依據李·昂克裡奇與阿德裡安·莫利納執導、皮克斯出品的二〇一七年動畫長片《尋夢環遊記》。文中區分影片明確給出的亡靈規則與由視覺和倫理結構作出的解讀。","德拉库斯把公共记忆变成占有；米格让一首私密的歌回到可可身边，恢复埃克托的位置，却不把一个记忆瞬间夸成对衰老的治愈。":"德拉庫斯把公共記憶變成佔有；米格讓一首私密的歌回到可可身邊，恢復埃克托的位置，卻不把一個記憶瞬間誇成對衰老的治癒。","照那套规则活的人被它埋了":"照那套規則活的人被它埋了","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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
