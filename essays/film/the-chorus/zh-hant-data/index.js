/* Generated offline from essays/film/the-chorus/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 电影":"← 電影","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","《放牛班的春天》解读":"《放牛班的春天》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","三篇从一所主要通过惩罚识认孩子的学校，读到克莱门特·马修怎样用尺度很小的行动为具体声音造出位置，以及那些不必等到日后成功便已构成回答的纸飞机。":"三篇從一所主要透過懲罰識認孩子的學校，讀到克萊門特·馬修怎樣用尺度很小的行動為具體聲音造出位置，以及那些不必等到日後成功便已構成回答的紙飛機。","《放牛班的春天》常被记成一个温暖故事：音乐来到以后，一群问题少年被拯救了。它的结构并没有这么安慰人。蒙丹遭到错判，后来又放火烧校；马修无法保护每一个人；他的工作也并非毫无制度后果——几位同事最终揭发校长——但电影从未保证一个合唱团可以修好整所学校。":"《放牛班的春天》常被記成一個溫暖故事：音樂來到以後，一群問題少年被拯救了。它的結構並沒有這麼安慰人。孟丹遭到錯判，後來又放火燒校；馬修無法保護每一個人；他的工作也並非毫無制度後果——幾位同事最終揭發校長——但電影從未保證一個合唱團可以修好整所學校。","三篇从“行动——反应”写到一名低阶学监有限而且并不完美的行动，再写到一场由不同字迹完成的告别。它们追问：当教育预先假定有罪，它会变成什么；改革尚未来临时，一名教师如何先创造不排除人的位置；以及为什么不能用皮埃尔后来的名声，替其他每一个孩子经历过的事情定价。":"三篇從“行動——反應”寫到一名低階學監有限而且並不完美的行動，再寫到一場由不同字跡完成的告別。它們追問：當教育預先假定有罪，它會變成什麼；改革尚未來臨時，一名教師如何先創造不排除人的位置；以及為什麼不能用皮耶後來的名聲，替其他每一個孩子經歷過的事情定價。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","这所学校只有四个字的管理办法":"這所學校只有四個字的管理辦法","哈善的规则用预先把每个孩子当成嫌疑对象的方式制造即时服从；蒙丹则显示，当类别比证据更强，制度会把什么做成事实。":"哈善的規則用預先把每個孩子當成嫌疑對象的方式製造即時服從；孟丹則顯示，當類別比證據更強，制度會把什麼做成事實。","英 · 简 · 繁":"英 · 簡 · 繁","马修改不了学校，却能取消一次连坐，把一次惩罚改成照护，并为一个不会唱歌的孩子造出仍能在合唱团里面的位置。":"馬修改不了學校，卻能取消一次連坐，把一次懲罰改成照護，並為一個不會唱歌的孩子造出仍能在合唱團裡面的位置。","他走的时候，以为什么都没留下":"他走的時候，以為什麼都沒留下","博尼法斯的字迹、贝比诺的错别字与莫昂治的音符，早在音乐学院、著名指挥家与所谓遗产出现以前，就已经回答了马修。":"博尼法斯的字跡、貝比諾的錯字與莫翰奇的音符，早在音樂學院、著名指揮家與所謂遺產出現以前，就已經回答了馬修。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
