/* Generated offline from essays/film/interstellar/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《星际穿越》解读":"《星際穿越》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一句有具体债权人的承诺，读到一个没有归处的英雄如何被抽象目标掏空，以及墨菲怎样在接受跨越时间的帮助时，仍然成为拯救行动真正的作者。":"三篇從一句有具體債權人的承諾，讀到一個沒有歸處的英雄如何被抽象目標掏空，以及墨菲怎樣在接受跨越時間的幫助時，仍然成為拯救行動真正的作者。","《星际穿越》常常以物种的尺度被讲述：地球正在死去，一支队伍穿过虫洞，人类必须寻找新的家园。但电影真正起作用的机关都落在更小的尺度上：一个父亲向一个孩子许诺；一个孤独的探险者发现“人类”不会回望自己；一个科学家用几十年把方程推进到只缺一份数据的位置。":"《星際穿越》常常以物種的尺度被講述：地球正在死去，一支隊伍穿過蟲洞，人類必須尋找新的家園。但電影真正起作用的機關都落在更小的尺度上：一個父親向一個孩子許諾；一個孤獨的探險者發現“人類”不會回望自己；一個科學家用幾十年把方程推進到只缺一份數據的位置。","这三篇用这些具体关系重读电影的宇宙结构。它区分一笔可以被追讨的责任与一个无人能够核验的宏大事业；承认曼恩的恐惧是真的，却不让恐惧替他的行为免责；也不把墨菲缩成等待父亲的女儿，或者不需要任何人的孤独天才。拯救是共同完成的，而共同完成并不等于抹去她的主体性。":"這三篇用這些具體關係重讀電影的宇宙結構。它區分一筆可以被追討的責任與一個無人能夠核驗的宏大事業；承認曼恩的恐懼是真的，卻不讓恐懼替他的行為免責；也不把墨菲縮成等待父親的女兒，或者不需要任何人的孤獨天才。拯救是共同完成的，而共同完成並不等於抹去她的主體性。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","他留下的是一句可以被追讨的承诺":"他留下的是一句可以被追討的承諾","“我会回来”给出一个具体的债权人、一个被记住的到期日，以及一种不能消散在“拯救人类”里的责任。":"“我會回來”給出一個具體的債權人、一個被記住的到期日，以及一種不能消散在“拯救人類”裡的責任。","英 · 简 · 繁":"英 · 簡 · 繁","曼恩博士没有一个可以回去的人":"曼恩博士沒有一個可以回去的人","最受敬仰的拉撒路探险者把恐惧说成抽象人类的声音，最后险些毁掉他声称要拯救的具体的人。":"最受敬仰的拉撒路探險者把恐懼說成抽象人類的聲音，最後險些毀掉他聲稱要拯救的具體的人。","墨菲既不是只会等待父亲的人，也不是独自解决一切的天才；她把自己活成了能够识别、使用并回应那份数据的人。":"墨菲既不是只會等待父親的人，也不是獨自解決一切的天才；她把自己活成了能夠識別、使用並回應那份數據的人。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
