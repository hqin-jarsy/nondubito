/* Generated offline from essays/literature/one-hundred-years-of-solitude/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Literary criticism":"English · 簡 / 繁 · Literary criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《百年孤独》解读":"《百年孤獨》解讀","上校做到二十五条小金鱼便全部熔掉，退守到一种不会被制度或继承者利用的手艺，因为他先毁掉了积累。":"上校做到二十五條小金魚便全部熔掉，退守到一種不會被制度或繼承者利用的手藝，因為他先毀掉了積累。","乌尔苏拉的眼睛":"烏爾蘇拉的眼睛","五篇文章，从对抗遗忘的标签、上校不断熔掉的小金鱼，到乌尔苏拉失明后的看见、梅梅一生的沉默，以及只在未来耗尽时才可读的完美记录。":"五篇文章，從對抗遺忘的標籤、上校不斷熔掉的小金魚，到烏爾蘇拉失明後的看見、梅梅一生的沈默，以及只在未來耗盡時才可讀的完美記錄。","失明让乌尔苏拉从模样转向反复发生的行动；她终于看清家人，却依然无法终止家族的重复。":"失明讓烏爾蘇拉從模樣轉向反復發生的行動；她終於看清家人，卻依然無法終止家族的重復。","失眠症留下的是可以用标签填入的空白；屠杀之后，那个位置已被否认事件的官方文书占满。":"失眠症留下的是可以用標籤填入的空白；屠殺之後，那個位置已被否認事件的官方文書佔滿。","家族完整记录在最后的读者与城镇被抹除时才可读：它作为描述完美，作为继承却彻底失败。":"家族完整記錄在最後的讀者與城鎮被抹除時才可讀：它作為描述完美，作為繼承卻徹底失敗。","小金鱼":"小金魚","本文依据范晔译本（南海出版公司，2011），人名地名从该本。另有黄锦炎等译本通行。全书剧透。":"本文依據範曄譯本（南海出版公司，2011），人名地名從該本。另有黃錦炎等譯本通行。全書劇透。","梅梅不再说话":"梅梅不再說話","爱人、路程、住所与故事都被替她决定之后，梅梅只守住最后一项：她的声音是否参与这套安排。":"愛人、路程、住所與故事都被替她決定之後，梅梅只守住最後一項：她的聲音是否參與這套安排。","牌子上写着“上帝存在”":"牌子上寫著“上帝存在”","系列 · 五篇解读 · 文学评论":"系列 · 五篇解讀 · 文學評論","羊皮纸":"羊皮紙","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","马尔克斯笔下的几代人，继承名字、恐惧、习惯与沉默，往往比继承真相更可靠。这组文章追问记忆能住在哪里，官方说法如何占据那个位置，以及一份完整档案为什么可能来得太晚。":"馬爾克斯筆下的幾代人，繼承名字、恐懼、習慣與沈默，往往比繼承真相更可靠。這組文章追問記憶能住在哪裡，官方說法如何佔據那個位置，以及一份完整檔案為什麼可能來得太晚。"};
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
