/* Generated offline from essays/film/v-for-vendetta/index.html; no runtime service dependency. */
(function() {
  'use strict';
  var variants = {"English · 简 / 繁 · Film criticism":"English · 簡 / 繁 · Film criticism","Han Qin (秦汉)":"Han Qin (秦漢)","V 为了让艾薇摆脱恐惧复制了一座牢房；好的结果，能否倒过来替未经同意的手段授权？":"V 為了讓艾薇擺脫恐懼複製了一座牢房；好的結果，能否倒過來替未經同意的手段授權？","V 留下列车，艾薇作出决定，芬奇放下枪：革命的最后一步究竟属于谁？":"V 留下列車，艾薇作出決定，芬奇放下槍：革命的最後一步究竟屬於誰？","© 2026 Han Qin (秦汉) · ":"© 2026 Han Qin (秦漢) · ","← 电影":"← 電影","《V字仇杀队》解读":"《V字仇殺隊》解讀","一份名单，和一间没有名字的营地":"一份名單，和一間沒有名字的營地","三个动作，三种权力":"三個動作，三種權力","三篇解读：一个政权怎样先把人改写成类别，一场以自由为名却未经同意的改造，以及那根操作杆究竟属于谁的决定。":"三篇解讀：一個政權怎樣先把人改寫成類別，一場以自由為名卻未經同意的改造，以及那根操作桿究竟屬於誰的決定。","他用了同一套办法":"他用了同一套辦法","本系列以詹姆斯·麦克提格执导的电影版为文本，不把电影与阿兰·摩尔、大卫·劳埃德的漫画原作视为同一作品。":"本系列以詹姆斯·麥克提格執導的電影版為文本，不把電影與阿蘭·摩爾、大衛·勞埃德的漫畫原作視為同一作品。","系列 · 三篇解读 · 电影评论":"系列 · 三篇解讀 · 電影評論","英 · 简 · 繁":"英 · 簡 · 繁","英文 · 简 / 繁 · 电影解读":"英文 · 簡 / 繁 · 電影解讀","英文 · 简体 · 繁体":"英文 · 簡體 · 繁體","诺斯费尔列名单，V 建牢房，艾薇推下操作杆。三篇沿着这三个动作追问同一件事：当一个人确信自己代表正确，他是否仍愿意给别人留下拒绝、离开和自行决定的空间？":"諾斯費爾列名單，V 建牢房，艾薇推下操作桿。三篇沿著這三個動作追問同一件事：當一個人確信自己代表正確，他是否仍願意給別人留下拒絕、離開和自行決定的空間？","诺斯费尔怎样把具体的人改写成类别，以及瓦莱丽如何从名单内部把自己的名字写回来。":"諾斯費爾怎樣把具體的人改寫成類別，以及瓦萊麗如何從名單內部把自己的名字寫回來。","这不是要把独裁者与反抗者简单画上等号。恰恰相反，只有承认他们目的与后果的差异，我们才看得清另一条更隐蔽的边界：反抗支配的人，也可能在解放之名下替别人作主。":"這不是要把獨裁者與反抗者簡單畫上等號。恰恰相反，只有承認他們目的與後果的差異，我們才看得清另一條更隱蔽的邊界：反抗支配的人，也可能在解放之名下替別人作主。","那根操作杆是谁的决定":"那根操作桿是誰的決定"};
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
