/* Generated offline from essays/film/life-is-beautiful/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《美丽人生》解读":"《美麗人生》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从圭多一贯的喜剧想象力，读到集中营里的游戏如何成为临时的生存结构，以及发明游戏的人离开后，那辆真正到来的坦克。":"三篇從圭多一貫的喜劇想像力，讀到集中營裡的遊戲如何成為臨時的生存結構，以及發明遊戲的人離開後，那輛真正到來的坦克。","《美丽人生》作出了一个在伦理上极其危险的选择：它把寓言与喜剧的语法带进一个关于驱逐和灭绝的故事。它的辩护不可能是幽默让集中营变得不那么可怕。电影真正采用的是一种双层结构：乔舒亚听见的是一个教他如何多活一天的游戏；观众看见的则是孩子看不见的排犹标牌、锁死的车厢、筛选与尸体。":"《美麗人生》作出了一個在倫理上極其危險的選擇：它把寓言與喜劇的語法帶進一個關於驅逐和滅絕的故事。它的辯護不可能是幽默讓集中營變得不那麼可怕。電影真正採用的是一種雙層結構：喬舒亞聽見的是一個教他如何多活一天的遊戲；觀眾看見的則是孩子看不見的排猶標牌、鎖死的車廂、篩選與屍體。","因此，圭多的编造没有替观众覆盖现实。它只是在他无法击败的现实里面，凿出一小块还可以行动的空间。战前，这种想象力为别人打开选择，却不替别人作决定；进入集中营后，它成为一种不对称的照护——风险由父亲承担，眼前的好处给了孩子。成年后的旁白把它称作礼物。这不能证明创伤没有留下，也不能自动回答围绕这部电影的全部质疑；它说明的是，幸存者后来选择怎样命名父亲所做的事。":"因此，圭多的編造沒有替觀眾覆蓋現實。它只是在他無法擊敗的現實裡面，鑿出一小塊還可以行動的空間。戰前，這種想像力為別人打開選擇，卻不替別人作決定；進入集中營後，它成為一種不對稱的照護——風險由父親承擔，眼前的好處給了孩子。成年後的旁白把它稱作禮物。這不能證明創傷沒有留下，也不能自動回答圍繞這部電影的全部質疑；它說明的是，幸存者後來選擇怎樣命名父親所做的事。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他从一开始就在给别人打开空间":"他從一開始就在給別人打開空間","前半部的爱情喜剧并非灾难前可以拆掉的甜味；它建立了圭多一贯的方法：把别人写好的剧本变成一道可以自行走出的门。":"前半部的愛情喜劇並非災難前可以拆掉的甜味；它建立了圭多一貫的方法：把別人寫好的劇本變成一道可以自行走出的門。","英 · 简 · 繁":"英 · 簡 · 繁","那个谎言只有一个用途，就是让他活到明天":"那個謊言只有一個用途，就是讓他活到明天","游戏不解释世界，也不制造一套终身信条；它把安静、躲藏和等待，变成一个五岁孩子可以做到的生存动作。":"遊戲不解釋世界，也不製造一套終身信條；它把安靜、躲藏和等待，變成一個五歲孩子可以做到的生存動作。","那辆坦克是真的":"那輛坦克是真的","圭多至死没有让游戏破裂；孩子尚未识破编造时，承诺的坦克真的出现了，而成年后的幸存者把整件事称作父亲的礼物。":"圭多至死沒有讓遊戲破裂；孩子尚未識破編造時，承諾的坦克真的出現了，而成年後的幸存者把整件事稱作父親的禮物。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
