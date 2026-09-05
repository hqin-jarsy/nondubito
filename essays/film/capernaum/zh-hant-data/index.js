/* Generated offline from essays/film/capernaum/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《何以为家》从一场听来近乎不可能的诉讼开始：一个孩子要因为父母生下自己而起诉他们。这三篇不把它当作一句口号，而是沿着身份文件、童工、童婚、移民处境与照料，追问一个人在能证明自己是谁以前，大人与制度已经欠他什么。":"《何以為家》從一場聽來近乎不可能的訴訟開始：一個孩子要因為父母生下自己而起訴他們。這三篇不把它當作一句口號，而是沿著身份文件、童工、童婚、移民處境與照料，追問一個人在能證明自己是誰以前，大人與制度已經欠他什麼。","《何以为家》解读":"《何以為家》解讀","三篇解读：没有纸面身份的人、绝境中仍需追问的那一寸，以及一个孩子替尚未出生者提出的要求。":"三篇解讀：沒有紙面身份的人、絕境中仍需追問的那一寸，以及一個孩子替尚未出生者提出的要求。","他要的是别人的事":"他要的是別人的事","他证明不了自己是谁":"他證明不了自己是誰","依据娜丁·拉巴基执导的二〇一八年电影《何以为家》；片名、人名、身份状态与关键情节已参照剧本及官方资料校订。":"依據娜丁·拉巴基執導的二〇一八年電影《何以為家》；片名、人名、身份狀態與關鍵情節已參照劇本及官方資料校訂。","当登记系统沉默，只能由牙齿替赞恩作证；而人之为人与制度看见一个人的文件，并不是同一件事。":"當登記系統沈默，只能由牙齒替贊恩作證；而人之為人與制度看見一個人的文件，並不是同一件事。","拉希尔、萨哈与约纳斯让我们看见：绝境能够解释伤害为何发生，却不会自动把伤害变成许可。":"拉希爾、薩哈與約納斯讓我們看見：絕境能夠解釋傷害為何發生，卻不會自動把傷害變成許可。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","赞恩无法拿回自己的童年，于是那句粗糙的要求转向了尚未进入循环的孩子。":"贊恩無法拿回自己的童年，於是那句粗糙的要求轉向了尚未進入循環的孩子。"};
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
