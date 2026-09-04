/* Generated offline from essays/anime/super-dimension-fortress-macross/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"Han Qin (秦汉)":"Han Qin (秦漢)","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","“Macross小姐”在军事上没有用途，却能让许多人投入注意；对只有一种功能的社会，这个组合几乎无法识别。":"“Macross小姐”在軍事上沒有用途，卻能讓許多人投入注意；對只有一種功能的社會，這個組合幾乎無法識別。","← 日本动漫与漫画":"← 日本動漫與漫畫","《超时空要塞 Macross》常因变形战机、偶像歌手与三角关系被记住。它更奇特的地方，是把一座要过日子的城市塞进一艘战争机器，再让只为单一功能而造的士兵，看见吃饭、玩具、恋爱与歌。":"《超時空要塞 Macross》常因變形戰機、偶像歌手與三角關係被記住。它更奇特的地方，是把一座要過日子的城市塞進一艘戰爭機器，再讓只為單一功能而造的士兵，看見吃飯、玩具、戀愛與歌。","《超时空要塞 Macross》解读":"《超時空要塞 Macross》解讀","一个量产的明美人偶没有携带任何主张，却把“玩具”这个从未存在的类别带进了舰队。":"一個量產的明美人偶沒有攜帶任何主張，卻把“玩具”這個從未存在的類別帶進了艦隊。","三个逃兵和一个人偶":"三個逃兵和一個人偶","两年后":"兩年後","五篇从一个只为战争而造的种族，读到被误认成武器的选美、三个间谍与一个人偶、为维持自身而清除变化者的体系，以及两年后并不整齐的和平。":"五篇從一個只為戰爭而造的種族，讀到被誤認成武器的選美、三個間諜與一個人偶、為維持自身而清除變化者的體系，以及兩年後並不整齊的和平。","他们截获的是一场选美":"他們截獲的是一場選美","他们没有“不打仗”这个选项":"他們沒有“不打仗”這個選項","他几乎消灭了地球上的生命":"他幾乎消滅了地球上的生命","数以百万计的战舰为保住既有军事秩序而毁灭地球，也准备清除已经接触文化的己方舰队。":"數以百萬計的戰艦為保住既有軍事秩序而毀滅地球，也準備清除已經接觸文化的己方艦隊。","男女舰队彼此隔绝，没有家庭、孩子、故事与平民职业；一个战斗功能被做成了整个社会。":"男女艦隊彼此隔絕，沒有家庭、孩子、故事與平民職業；一個戰鬥功能被做成了整個社會。","系列 · 5 篇解读":"系列 · 5 篇解讀","结束战争的歌没有自动给歌手一个未来；明美最后走向陌生的城市，只决定再试着唱一次。":"結束戰爭的歌沒有自動給歌手一個未來；明美最後走向陌生的城市，只決定再試著唱一次。","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","英文重写 · 简 / 繁":"英文重寫 · 簡 / 繁","这五篇只以三十六集电视版为主要文本。1984年剧场版重写了许多关键情节，后续系列也扩展了世界观；这里不会把那些设定无声地倒放回原作。含全剧剧透。":"這五篇只以三十六集電視版為主要文字。1984年劇場版重寫了許多關鍵情節，後續系列也擴展了世界觀；這裡不會把那些設定無聲地倒放回原作。含全劇劇透。"};
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
