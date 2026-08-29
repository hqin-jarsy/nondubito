/* Generated offline from essays/literature/run-with-the-wind/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"← 文学与文化":"← 文學與文化","系列 · 五篇解读 · 动画评论":"系列 · 五篇解讀 · 動畫評論","《强风吹拂》解读":"《強風吹拂》解讀","Han Qin (秦汉)":"Han Qin (秦漢)","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","English · 简 / 繁 · Cultural analysis":"English · 簡 / 繁 · Cultural analysis","五篇从竹青庄没有先说的房租条件，读到王子的三个理由、走从高中带来的那把尺子、只有对手知道的灰二旧伤，以及一场需要每个人却无人能够代跑的驿传。":"五篇從竹青莊沒有先說的房租條件，讀到王子的三個理由、走從高中帶來的那把尺子、只有對手知道的灰二舊傷，以及一場需要每個人卻無人能夠代跑的驛傳。","《强风吹拂》从一次偷窃和一句邀请开始。藏原走偷了食物，清濑灰二骑车追上他，问“你喜欢跑步吗”，再把他带到房租便宜的竹青庄。走住进去以后才知道：这里名义上是田径部宿舍，灰二已经计划让十名住户一起挑战箱根驿传。":"《強風吹拂》從一次偷竊和一句邀請開始。藏原走偷了食物，清瀨灰二騎車追上他，問“你喜歡跑步嗎”，再把他帶到房租便宜的竹青莊。走住進去以後才知道：這裡名義上是田徑部宿舍，灰二已經計畫讓十名住戶一起挑戰箱根驛傳。","这部作品常被记成友情与奇迹的故事。五篇保留那份成就，也继续追问成就的条件。灰二对每个人的照料极其具体，他的招募方式却带着操纵；王子始终最慢，却成为不可替代的一棒；走没有放弃速度，只是学会速度不是让一个跑者出现的唯一尺度；驿传把十种生活接在一起，却没有把任何一个人溶掉。":"這部作品常被記成友情與奇跡的故事。五篇保留那份成就，也繼續追問成就的條件。灰二對每個人的照料極其具體，他的招募方式卻帶著操縱；王子始終最慢，卻成為不可替代的一棒；走沒有放棄速度，只是學會速度不是讓一個跑者出現的唯一尺度；驛傳把十種生活接在一起，卻沒有把任何一個人溶掉。","本系列以Production I.G制作、野村和也监督、喜安浩平编剧的二十三集电视动画为主要文本，并参考三浦紫苑二〇〇六年原作小说。全系列剧透。":"本系列以Production I.G製作、野村和也監督、喜安浩平編劇的二十三集電視動畫為主要文本，並參考三浦紫苑二〇〇六年原作小說。全系列劇透。","英文 · 简 / 繁 · 作品解读":"英文 · 簡 / 繁 · 作品解讀","房租便宜是有条件的":"房租便宜是有條件的","灰二先给走一个住处，随后才揭示竹青庄是田径部宿舍，而且十个人都被期待去跑箱根。":"灰二先給走一個住處，隨後才揭示竹青莊是田徑部宿舍，而且十個人都被期待去跑箱根。","英 · 简 · 繁":"英 · 簡 · 繁","三个理由":"三個理由","王子因为漫画受威胁、因为认出别人也有自己珍爱的东西，还因为灰二看见他早已拥有的一项能力而跑。":"王子因為漫畫受威脅、因為認出別人也有自己珍愛的東西，還因為灰二看見他早已擁有的一項能力而跑。","他带着那把尺子进了大学":"他帶著那把尺子進了大學","走离开了胜利至上的教练，却把那套只有“快”一个刻度的尺子带进一群初学者中间。":"走離開了勝利至上的教練，卻把那套只有“快”一個刻度的尺子帶進一群初學者中間。","知道那条腿的人在对面":"知道那條腿的人在對面","灰二了解每个队友的身体，却瞒着自己的坏膝；计划的大部分时间里，知道真相的是对面的藤冈。":"灰二了解每個隊友的身體，卻瞞著自己的壞膝；計畫的大部分時間裡，知道真相的是對面的藤岡。","没有人能替另一个人跑":"沒有人能替另一個人跑","驿传需要每一个人、记下一份集体成绩，却仍不允许任何队友替另一个人跑完他的区间。":"驛傳需要每一個人、記下一份集體成績，卻仍不允許任何隊友替另一個人跑完他的區間。","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · "};
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
