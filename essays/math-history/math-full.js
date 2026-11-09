(function(){
'use strict';
var root=document.documentElement, foreign=['de','fr','es','ja','ko'].indexOf(root.lang)>=0;
function update(){
 var lang=root.dataset.lang;
 if(!foreign){
  document.querySelectorAll('.math-series-nav a,.math-breadcrumbs a,.math-card[href]').forEach(function(a){var u=new URL(a.href);if(u.pathname.indexOf('/essays/math-history/')>=0){u.searchParams.set('lang',lang);a.href=u.pathname+u.search+u.hash;}});
 }
 document.querySelectorAll('[data-math-language]').forEach(function(a){if(a.dataset.mathLanguage===lang)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
}
document.addEventListener('DOMContentLoaded',update);document.addEventListener('nondubito:languagechange',update);
})();
