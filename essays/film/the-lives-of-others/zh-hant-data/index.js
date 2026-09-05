/* Generated offline from essays/film/the-lives-of-others/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《窃听风暴》没有从一个显眼的恶棍开始，而是从一名让压迫高效运转的优秀技术员开始。三篇文章追踪“听”改变方向的过程：它起初把一个人的生活抽取给国家，后来却开始替这个人挡住国家。":"《竊聽風暴》沒有從一個顯眼的惡棍開始，而是從一名讓壓迫高效運轉的優秀技術員開始。三篇文章追蹤“聽”改變方向的過程：它起初把一個人的生活抽取給國家，後來卻開始替這個人擋住國家。","《窃听风暴》解读":"《竊聽風暴》解讀","三篇解读：流程化的残酷、披上国家安全外衣的私人欲望，以及献给 HGW XX/7 的题词如何完成一次承认。":"三篇解讀：流程化的殘酷、披上國家安全外衣的私人慾望，以及獻給 HGW XX/7 的題詞如何完成一次承認。","不用包，这是给我的":"不用包，這是給我的","他是这套东西里最好的技术员":"他是這套東西裡最好的技術員","依据弗洛里安·亨克尔·冯·多纳斯马尔克执导的二〇〇六年电影《窃听风暴》；机构数据、时间线与关键对白已按成片校订，并区分格鲁比茨“二十年”的威胁与柏林墙开放前实际经过的四年七个月。":"依據弗洛裡安·亨克爾·馮·多納斯馬爾克執導的二〇〇六年電影《竊聽風暴》；機構數據、時間線與關鍵對白已按成片校訂，並區分格魯比茨“二十年”的威脅與柏林牆開放前實際經過的四年七個月。","假报告救下德莱曼，历史截断二十年的威胁；一行公开题词只对一个无名读者完整可见，却不要求偿还。":"假報告救下德萊曼，歷史截斷二十年的威脅；一行公開題詞只對一個無名讀者完整可見，卻不要求償還。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","维斯勒的方法把每种反应都读成有罪，让职业上的精确遮住目光本身的不正当。":"維斯勒的方法把每種反應都讀成有罪，讓職業上的精確遮住目光本身的不正當。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","这次行动跟国家安全没有关系":"這次行動跟國家安全沒有關係","部长的欲望以嫌疑之名进入档案；一首奏鸣曲则让维斯勒再也无法把已经知道的事实彼此隔开。":"部長的慾望以嫌疑之名進入檔案；一首奏鳴曲則讓維斯勒再也無法把已經知道的事實彼此隔開。"};
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
