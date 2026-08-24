// Swaps the static "N views" number on a handful of essay pages for a real
// count from /api/views, if that endpoint has one. Fails silently and keeps
// whatever number is already in the HTML if anything goes wrong - this is
// decorative, never worth showing an error over.
(function () {
  function localize(n) {
    try {
      return n.toLocaleString('en-US');
    } catch (e) {
      return String(n);
    }
  }

  document.querySelectorAll('.view-count[data-path]').forEach(function (el) {
    var path = el.getAttribute('data-path');
    if (!path) return;

    fetch('/api/views?path=' + encodeURIComponent(path))
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
        // network error, endpoint doesn't exist yet, etc. -> same, leave it.
      });
  });
})();
