/* Generated offline from essays/literature/the-wind-up-bird-chronicle/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《发条鸟年代记》解读":"《發條鳥年代記》解讀","五篇文章，从辞职后剩下的生活、绵谷升手续齐全的权力，到两口枯井、跨越四十年的印记，以及无法摆脱所反抗之暴力的胜利。":"五篇文章，從辭職後剩下的生活、綿谷升手續齊全的權力，到兩口枯井、跨越四十年的印記，以及無法擺脫所反抗之暴力的勝利。","冈田亨只能在所有正式场域之外触及绵谷升，也无法不用暴力击败暴力；最后的修复落在猫的新名字上。":"岡田亨只能在所有正式場域之外觸及綿谷升，也無法不用暴力擊敗暴力；最後的修復落在貓的新名字上。","冈田亨离开可识别的工作后，日常动作与名分之外的人，成了他寻找一个具体失踪者的全部材料。":"岡田亨離開可識別的工作後，日常動作與名分之外的人，成了他尋找一個具體失蹤者的全部材料。","别处制作的东西":"別處製作的東西","同一块面部印记连接战时兽医与冈田亨；肉桂则把失去的声音转化成对官方历史漏项的记录。":"同一塊面部印記連接戰時獸醫與岡田亨；肉桂則把失去的聲音轉化成對官方歷史漏項的記錄。","村上春树《发条鸟年代记》，中文篇依据赖明珠译本。林少华译本作《奇鸟行状录》。全书剧透。":"村上春樹《發條鳥年代記》，中文篇依據賴明珠譯本。林少華譯本作《奇鳥行狀錄》。全書劇透。","村上春树把满洲战争与八十年代东京的媒体政治放在一条线上，却不让前者简单解释后者。这组文章追踪制度拿走了什么、记录漏掉了什么，以及人们如何围绕那些空缺建立非正式关系。":"村上春樹把滿洲戰爭與八十年代東京的媒體政治放在一條線上，卻不讓前者簡單解釋後者。這組文章追蹤制度拿走了什麼、記錄漏掉了什麼，以及人們如何圍繞那些空缺建立非正式關係。","系列 · 五篇解读 · 文学评论":"系列 · 五篇解讀 · 文學評論","绵谷升":"綿谷升","绵谷升的权力由学界、媒体、选民与家庭合规授予，因此冈田亨找不到一套被承认的语言，说明它从人身上拿走了什么。":"綿谷升的權力由學界、媒體、選民與家庭合規授予，因此岡田亨找不到一套被承認的語言，說明它從人身上拿走了什麼。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","辞职":"辭職","间宫被丢进一口井而被掏空；冈田亨主动进入另一口，寻找公共权力没有造出的道路与印记。":"間宮被丟進一口井而被掏空；岡田亨主動進入另一口，尋找公共權力沒有造出的道路與印記。"};
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
