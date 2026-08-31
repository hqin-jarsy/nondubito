/* Generated offline from my-name-is-red/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 文学与文化":"← 文學與文化","《我的名字叫红》解读":"《我的名字叫紅》解讀","一个死人在井底说话":"一個死人在井底說話","一个死者先说“我”，而五十九章不断更换讲述的位置：小说用形式回答绘画中那场关于个人视角的争论。":"一個死者先說“我”，而五十九章不斷更換講述的位置：小說用形式回答繪畫中那場關於個人視角的爭論。","传统并非只是在压制个人，它保存着累积数代的技艺与美；真正困难的是，学艺时的自我克制为何变成大师也不该留下痕迹。":"傳統並非只是在壓制個人，它儲存著累積數代的技藝與美；真正困難的是，學藝時的自我剋制為何變成大師也不該留下痕跡。","凶手藏进共同传统，仍被一个无意识的鼻孔画法暴露；审美体系靠它最想抹掉的东西破了案。":"凶手藏進共同傳統，仍被一個無意識的鼻孔畫法暴露；審美體系靠它最想抹掉的東西破了案。","四篇文章，从井底开口的死人、把风格视为瑕疵的传统、暴露凶手的马鼻孔，到谢库瑞想要却不存在的那幅画。":"四篇文章，從井底開口的死人、把風格視為瑕疵的傳統、暴露凶手的馬鼻孔，到謝庫瑞想要卻不存在的那幅畫。","帕慕克把一场谋杀放在两套观看方式的交界处：奥斯曼细密画追求不属于任何个人的神圣视野，威尼斯肖像则承认画家、模特与观者各自所在的位置。":"帕慕克把一場謀殺放在兩套觀看方式的交界處：奧斯曼細密畫追求不屬於任何個人的神聖視野，威尼斯肖像則承認畫家、模特與觀者各自所在的位置。","系列 · 四篇解读 · 文学评论":"系列 · 四篇解讀 · 文學評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","谢库瑞想保存两个最幸福的时刻，却发现两套绘画传统都容不下它；于是她选择讲述，并承认讲述也会失真。":"謝庫瑞想儲存兩個最幸福的時刻，卻發現兩套繪畫傳統都容不下它；於是她選擇講述，並承認講述也會失真。","这组解读追问的不是哪一种画法更先进，而是一个人的痕迹如何被训练、抹去、辨认并重新讲述。":"這組解讀追問的不是哪一種畫法更先進，而是一個人的痕跡如何被訓練、抹去、辨認並重新講述。","那匹马的鼻子":"那匹馬的鼻子","那幅画不存在":"那幅畫不存在","风格是一种瑕疵":"風格是一種瑕疵"};
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
