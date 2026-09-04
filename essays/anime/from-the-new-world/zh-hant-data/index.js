/* Generated offline from essays/anime/from-the-new-world/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 日本动漫与漫画":"← 日本動漫與漫畫","《来自新世界》先让观众走进一个明亮、安静的田园社会，再一点点揭开它为何能够安静。那些制度并非毫无理由的恶意；它们解决过足以毁掉文明的真实问题，也因为太有效，逐渐藏住了代价由谁承担。":"《來自新世界》先讓觀眾走進一個明亮、安靜的田園社會，再一點點揭開它為何能夠安靜。那些制度並非毫無理由的惡意；它們解決過足以毀掉文明的真實問題，也因為太有效，逐漸藏住了代價由誰承擔。","《来自新世界》解读":"《來自新世界》解讀","一个孩子在没有指控与申辩的情况下消失，留下的人随后连“曾经失去过谁”也不再知道。":"一個孩子在沒有指控與申辯的情況下消失，留下的人隨後連“曾經失去過誰”也不再知道。","一个说得通的救急方案，借用的正是制造危机的那条可移动边界；后来得到的知识，不能倒放回当时的选择。":"一個說得通的救急方案，借用的正是製造危機的那條可移動邊界；後來得到的知識，不能倒放回當時的選擇。","五篇从被装进身体的和平，读到消失的孩子、被改动的“同族”边界、法庭上遭到嘲笑的一句真话，以及那个自愿死去、因而救下全町的人。":"五篇從被裝進身體的和平，讀到消失的孩子、被改動的“同族”邊界、法庭上遭到嘲笑的一句真話，以及那個自願死去、因而救下全町的人。","他们把底层装了进去":"他們把底層裝了進去","化鼠会说话、组织、战争与申诉；最后的基因揭示，让此前每一次“管理动物”都显出了另一层含义。":"化鼠會說話、組織、戰爭與申訴；最後的基因揭示，讓此前每一次“管理動物”都顯出了另一層含義。","同族这个词":"同族這個詞","她杀了一个自愿的人":"她殺了一個自願的人","当一个念头就足以杀人，社会把攻击抑制与愧死机构装进每个人的身体；和平是真的，选择却不再是它的来源。":"當一個念頭就足以殺人，社會把攻擊抑制與愧死機構裝進每個人的身體；和平是真的，選擇卻不再是它的來源。","我是人类":"我是人類","猫":"貓","系列 · 5 篇解读":"系列 · 5 篇解讀","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","要求族群不再被当作工具的人，把一个孩子养成武器，也把自己的族人送上战场；审判他的法庭则重复了造出这一切的分类。":"要求族群不再被當作工具的人，把一個孩子養成武器，也把自己的族人送上戰場；審判他的法庭則重複了造出這一切的分類。","这五篇按照动画揭示真相的顺序展开。重点不是替所有角色作终局判决，而是看一个社会掌握记忆、分类与申诉语言以后，保护人的规则怎样改变了覆盖范围。含全剧剧透。":"這五篇按照動畫揭示真相的順序展開。重點不是替所有角色作終局判決，而是看一個社會掌握記憶、分類與申訴語言以後，保護人的規則怎樣改變了覆蓋範圍。含全劇劇透。"};
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
