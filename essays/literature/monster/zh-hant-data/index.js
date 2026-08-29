/* Generated offline from essays/literature/monster/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 五篇解读 · 作品评论":"系列 · 五篇解讀 · 作品評論","《怪物》解读":"《怪物》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","五篇从医院里的生命排序，读到五一一号儿童院的人类工程、被拿走又留下的名字、无法互相解释的双胞胎，以及天马为什么第二次救下约翰。":"五篇從醫院裡的生命排序，讀到五一一號兒童院的人類工程、被拿走又留下的名字、無法互相解釋的雙胞胎，以及天馬為什麼第二次救下約翰。","《怪物》从一个看上去几乎不需要讨论的决定开始：天马贤三继续为先到院的孩子做手术，没有为了后来送到的市长中断救治。孩子活了。九年以后，天马才知道自己救下的是约翰·利贝特，而约翰的来路穿过五一一号儿童院、红玫瑰宅邸、一本没有名字的怪物绘本，以及一整套试图生产“有用之人”的程序。":"《怪物》從一個看上去幾乎不需要討論的決定開始：天馬賢三繼續為先到院的孩子做手術，沒有為了後來送到的市長中斷救治。孩子活了。九年以後，天馬才知道自己救下的是約翰·利貝特，而約翰的來路穿過五一一號兒童院、紅玫瑰宅邸、一本沒有名字的怪物繪本，以及一整套試圖生產“有用之人”的程序。","作品始终拒绝把约翰交给一个单独原因。不是一本书、一栋楼、一个母亲、一次救命或一个决定就能解释全部。五篇沿着这份拒绝往下读：平等什么时候是一条界线，而不是一道算式；照护什么时候又变成设计；名字能够替一个人留下什么；以及当天马已经知道全部后果，他为什么仍然拿起手术刀。":"作品始終拒絕把約翰交給一個單獨原因。不是一本書、一棟樓、一個母親、一次救命或一個決定就能解釋全部。五篇沿著這份拒絕往下讀：平等什麼時候是一條界線，而不是一道算式；照護什麼時候又變成設計；名字能夠替一個人留下什麼；以及當天馬已經知道全部後果，他為什麼仍然拿起手術刀。","本系列以浦泽直树《怪物》漫画为主要文本，并参考Madhouse制作的七十四集电视动画。全系列剧透。":"本系列以浦澤直樹《怪物》漫畫為主要文本，並參考Madhouse製作的七十四集電視動畫。全系列劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","后来的病人先做手术":"後來的病人先做手術","天马用医院自己的常规顺序对抗权势排序，随后却从几桩并非他所为的死亡中拿回全部前途。":"天馬用醫院自己的常規順序對抗權勢排序，隨後卻從幾樁並非他所為的死亡中拿回全部前途。","英 · 简 · 繁":"英 · 簡 · 繁","教育就是实验":"教育就是實驗","五一一号拿走名字、设计环境；佩德罗夫后来加入“爱”，却没有改变孩子作为预定产物的位置。":"五一一號拿走名字、設計環境；佩德羅夫後來加入“愛”，卻沒有改變孩子作為預定產物的位置。","编号可以取代名字，格里马临终想起阿道夫·莱因哈特，却说明抹除始终没有完成。":"編號可以取代名字，格里馬臨終想起阿道夫·萊因哈特，卻說明抹除始終沒有完成。","另一个":"另一個","尼娜和约翰共享来路，却没有走上同一条路；作品拒绝把家庭、记忆与后来关系压成一条因果公式。":"尼娜和約翰共享來路，卻沒有走上同一條路；作品拒絕把家庭、記憶與後來關係壓成一條因果公式。","约翰安排好的死亡被意外打断后，天马先救治、再开颅；最后的空床收回了这次决定的结果。":"約翰安排好的死亡被意外打斷後，天馬先救治、再開顱；最後的空床收回了這次決定的結果。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
