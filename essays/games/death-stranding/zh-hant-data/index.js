/* Generated offline from essays/games/death-stranding/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Game criticism":"English · 簡 / 繁 · Game criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 游戏与交互叙事":"← 遊戲與交互敘事","《死亡搁浅》先让连接变得困难，才谈连接的可贵。路要人修，货要人背，帮助常来自永远见不到的陌生人；可那张网络也把一些生命变成了基础设施。四篇文章沿着这条没有被轻易化解的张力往下读：绳可以把人留住，桥墩里也可能埋着人。":"《死亡擱淺》先讓連接變得困難，才談連接的可貴。路要人修，貨要人背，幫助常來自永遠見不到的陌生人；可那張網絡也把一些生命變成了基礎設施。四篇文章沿著這條沒有被輕易化解的張力往下讀：繩可以把人留住，橋墩裡也可能埋著人。","为什么一部送货游戏能把后果变成重量，也把陌生人的帮助变成可以亲手体验的连接。":"為什麼一部送貨遊戲能把後果變成重量，也把陌生人的幫助變成可以親手體驗的連接。","四篇解读：送货怎样成为承担，陌生人怎样互相留路，网络把谁藏进桥墩，以及山姆为何最终不肯把Lou当作失效设备。":"四篇解讀：送貨怎樣成為承擔，陌生人怎樣互相留路，網絡把誰藏進橋墩，以及山姆為何最終不肯把Lou當作失效設備。","山姆无法立刻废除把Lou变成编号的制度，却能拒绝它最后的命令，把一个人从火里抱走。":"山姆無法立刻廢除把Lou變成編號的制度，卻能拒絕它最後的命令，把一個人從火裡抱走。","布桥婴":"布橋嬰","死亡搁浅：绳、桥与被留下的人":"死亡擱淺：繩、橋與被留下的人","系列 · 四篇解读 · 游戏评论":"系列 · 四篇解讀 · 遊戲評論","绳":"繩","网络之所以能运转，是因为一个婴儿被归为设备，也因为使用者被训练成不去回答它的哭声。":"網絡之所以能運轉，是因為一個嬰兒被歸為設備，也因為使用者被訓練成不去回答它的哭聲。","芒姆、心人、克利福德、希格斯和亚美莉让我们看到：不丢弃一个生命，不等于把它困在自己需要的角色里。":"芒姆、心人、克利福德、希格斯和亞美莉讓我們看到：不丟棄一個生命，不等於把它困在自己需要的角色裡。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 游戏解读":"英文 · 簡 / 繁 · 遊戲解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體"};
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
