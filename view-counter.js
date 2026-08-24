// Swaps the static "N views" number on a handful of essay pages for a real
// count from a Cloudflare Worker, if it has one. Fails silently and keeps
// whatever number is already in the HTML if anything goes wrong - this is
// decorative, never worth showing an error over.
//
// The Worker is deployed separately (nondubito.net is on GitHub Pages, which
// can't run server code) - see cloudflare-worker/views-worker.js in this
// repo. WORKER_URL below needs to point at wherever that Worker actually
// ends up living (its *.workers.dev URL).
var WORKER_URL = 'https://REPLACE-WITH-YOUR-WORKER-URL.workers.dev';

(function () {
  function localize(n) {
    try {
      return n.toLocaleString('en-US');
    } catch (e) {
      return String(n);
    }
  }

  if (!WORKER_URL || WORKER_URL.indexOf('REPLACE-WITH') !== -1) return;

  document.querySelectorAll('.view-count[data-path]').forEach(function (el) {
    var path = el.getAttribute('data-path');
    if (!path) return;

    fetch(WORKER_URL + '?path=' + encodeURIComponent(path))
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (data) {
        if (data && typeof data.views === 'number') {
          el.textContent = localize(data.views) + ' views';
        }
        // data.views === null (not configured yet, or the API call failed
        // upstream) -> leave the existing static fallback text as-is.
      })
      .catch(function () {
        // network error, CORS not set up yet, etc. -> same, leave it.
      });
  });
})();
