/* Generated offline from index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"SAE Value Theory 价值论系列 — Non Dubito": "SAE Value Theory 價值論系列 — Non Dubito", "SAE 价值论": "SAE 價值論", "© 2026 Han Qin (秦汉) · ": "© 2026 Han Qin (秦漢) · ", "← 书架": "← 書架", "一条发生轴：显现，然后第一人称认可。社会承认是横穿过来的另一根轴，能给出公共位置也能收回，唯独不能替谁认领。": "一條發生軸：顯現，然後第一人稱認可。社會承認是橫穿過來的另一根軸，能給出公共位置也能收回，唯獨不能替誰認領。", "三种阅读模式：英文、简体、繁體。其他语言以后按系列陆续补。": "三種閱讀模式：英文、簡體、繁體。其他語言以後按系列陸續補。", "不可通约的价值构相遇时，行动如何裁断。": "不可通約的價值構相遇時，行動如何裁斷。", "与既有价值理论的接口，以及价值如何走向行动。": "與既有價值理論的介面，以及價值如何走向行動。", "他者的价值为何不可穷尽读取、不可外尺比较、不可统合，而共鸣又如何恰在这三条限界之内发生。": "他者的價值為何不可窮盡讀取、不可外尺比較、不可統合，而共鳴又如何恰在這三條限界之內發生。", "价值不是什么": "價值不是什麼", "价值是 SAE 各系列反复调用而一直没有归处的最后一个大词。权力论说价在方向，经济学量目的价值被编码为价格时的损耗，权利论把份位与利害切开，道德律立他者为目的。同一个词在四处各驮一义，从未被并进一张图。": "價值是 SAE 各系列反覆調用而一直沒有歸處的最後一個大詞。權力論說價在方向，經濟學量目的價值被編碼為價格時的損耗，權利論把份位與利害切開，道德律立他者為目的。同一個詞在四處各馱一義，從未被並進一張圖。", "传统理论对接与展望": "傳統理論對接與展望", "八篇补的就是这个洞。先清场——价值不是的五样东西——再立正面的机器：价值从哪里来，如何发生与被承认，如何被外来目的殖民，如何移动，两个价值构相撞时怎么办，以及他者的价值为什么可以共鸣却不能被量。": "八篇補的就是這個洞。先清場——價值不是的五樣東西——再立正面的機器：價值從哪裡來，如何發生與被承認，如何被外來目的殖民，如何移動，兩個價值構相撞時怎麼辦，以及他者的價值為什麼可以共鳴卻不能被量。", "可达、内容与重心在时间中的读数。这里没有一台马达，而所有读数在外面都是欠定的。": "可達、內容與重心在時間中的讀數。這裡沒有一臺馬達，而所有讀數在外面都是欠定的。", "撰写中": "撰寫中", "正面机器：源图、两轴、承担域，以及 14DD 到 15DD 那道桥。有结构，不排序的完整陈述在这里。": "正面機器：源圖、兩軸、承擔域，以及 14DD 到 15DD 那道橋。有結構，不排序的完整陳述在這裡。", "殖民不是外来影响的加深，是构成位被一个外来目的占着。三项签名，两支，以及审计不可越过的那道上界。": "殖民不是外來影響的加深，是構成位被一個外來目的佔著。三項簽名，兩支，以及審計不可越過的那道上界。", "清场。五只椟：价格、方向、给余项标价、阶梯、各说各话。全篇只带一件工具——孤独主体：价值只需要一个主体和它自己的法，价格至少需要两个主体和一把公共尺。": "清場。五隻櫝：價格、方向、給餘項標價、階梯、各說各話。全篇只帶一件工具——孤獨主體：價值只需要一個主體和它自己的法，價格至少需要兩個主體和一把公共尺。", "秦汉 · 2026 · 八篇 · 英文／中文／繁體": "秦漢 · 2026 · 八篇 · 英文／中文／繁體", "论价值与他者": "論價值與他者", "论价值的冲突": "論價值的衝突", "论价值的动力学": "論價值的動力學", "论价值的发生与承认": "論價值的發生與承認", "论价值的殖民": "論價值的殖民", "论价值的源": "論價值的源", "论目的价值": "論目的價值"};
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
