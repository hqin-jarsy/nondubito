/* Generated offline from essays/film/leon/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《这个杀手不太冷》解读":"《這個殺手不太冷》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一个被训练成工具的杀手，读到一个孩子如何寻找描述无条件照护的词，以及两个被辜负过的人如何在彼此不疑之中，短暂地有了一个家。":"三篇從一個被訓練成工具的殺手，讀到一個孩子如何尋找描述無條件照護的詞，以及兩個被辜負過的人如何在彼此不疑之中，短暫地有了一個家。","《这个杀手不太冷》把两个早已被成年人变成工具的人放到了一起。里昂替一个扣着他全部收入的中间人杀了十九年人，还以为自己一直受着照顾；十二岁的马蒂尔达则早已学会，在暴力家庭里活下去，要靠沉默、跑腿和有用。她走到他门前时，两个人都先认出了对方身上的某种东西，却都还没有语言去说明它。":"《這個殺手不太冷》把兩個早已被成年人變成工具的人放到了一起。里昂替一個扣著他全部收入的中間人殺了十九年人，還以為自己一直受著照顧；十二歲的馬蒂爾達則早已學會，在暴力家庭裡活下去，要靠沉默、跑腿和有用。她走到他門前時，兩個人都先認出了對方身上的某種東西，卻都還沒有語言去說明它。","这种识认并不能让电影的一切自动变得干净。必须把人物与摄影机分开判断：里昂一次次拒绝把孩子的依赖换成性接近，镜头却有时用爱情片的语法包装这种依赖。把两件事同时放在眼前，才看得见下面那段更少见的关系——它没有一个足够准确的社会名称，只发生在两个终于不再把对方当成可用之物的人之间。":"這種識認並不能讓電影的一切自動變得乾淨。必須把人物與攝影機分開判斷：里昂一次次拒絕把孩子的依賴換成性接近，鏡頭卻有時用愛情片的語法包裝這種依賴。把兩件事同時放在眼前，才看得見下面那段更少見的關係——它沒有一個足夠準確的社會名稱，只發生在兩個終於不再把對方當成可用之物的人之間。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","一个被养来杀人的人，自己不知道":"一個被養來殺人的人，自己不知道","里昂以为托尼一直在照顾他；被扣住的钱、不识字、没有根的植物，以及电影院里毫无防备的笑，讲的是另一回事。":"里昂以為托尼一直在照顧他；被扣住的錢、不識字、沒有根的植物，以及電影院裡毫無防備的笑，講的是另一回事。","英 · 简 · 繁":"英 · 簡 · 繁","她说错了那个词，可她想说的东西是对的":"她說錯了那個詞，可她想說的東西是對的","马蒂尔达把那种感受叫作爱，因为那是她知道的最大词；里昂的拒绝与摄影机的失守，共同说明了区分为何重要。":"馬蒂爾達把那種感受叫作愛，因為那是她知道的最大詞；里昂的拒絕與攝影機的失守，共同說明了區分為何重要。","两个被辜负过的人，对彼此不设防":"兩個被辜負過的人，對彼此不設防","他教她开枪，她教他认字；他们最后给对方的东西，不是替彼此安排未来，而是为未来打开一条路。":"他教她開槍，她教他認字；他們最後給對方的東西，不是替彼此安排未來，而是為未來打開一條路。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
  Object.assign(variants, {"这种识认并不能让电影的一切自动变得干净。必须把人物与摄影机分开判断：里昂一次次拒绝利用孩子的依赖换取性接近，镜头却有时用爱情片的语法包装这种依赖。把两件事同时放在眼前，才看得见下面那段更少见的关系——它没有一个足够准确的社会名称，只发生在两个终于不再把对方当成可用之物的人之间。":"這種識認並不能讓電影的一切自動變得乾淨。必須把人物與攝影機分開判斷：里昂一次次拒絕利用孩子的依賴換取性接近，鏡頭卻有時用愛情片的語法包裝這種依賴。把兩件事同時放在眼前，才看得見下面那段更少見的關係——它沒有一個足夠準確的社會名稱，只發生在兩個終於不再把對方當成可用之物的人之間。"});
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
