// Cloudflare Pages Function: /api/views?path=/essays/xiangjun/1-abundance.html
//
// Looks up a real pageview count for one of a whitelisted set of essay pages
// by querying Cloudflare's GraphQL Analytics API against the RUM data that
// Cloudflare Web Analytics (the beacon script already on every page) has been
// collecting. Requires two Pages environment variables to actually work:
//
//   CF_API_TOKEN    - an Account API token, permission "Account Analytics: Read"
//   CF_ACCOUNT_TAG  - the Cloudflare account ID that token belongs to
//
// If those aren't configured yet (or the API call fails for any reason), this
// returns {"views": null} instead of an error, and the page's own script
// leaves whatever static number is already in the HTML untouched. So the
// feature fails safe: worst case is exactly today's behavior, not a broken
// page.

const ALLOWED_PATHS = new Set([
  '/essays/xiangjun/1-abundance.html',
  '/essays/xiangjun/2-idol.html',
  '/essays/xiangjun/3-light.html',
  '/essays/wwii/1-weimar.html',
  '/essays/wwii/2-institutions.html',
  '/essays/wwii/3-four-systems.html',
  '/essays/wwii/4-promise.html',
  '/essays/wwii/5-cracks.html',
]);

// The Web Analytics "site" token, taken from the <script data-cf-beacon>
// snippet already embedded in every page. Not a secret - it's already
// public in the page source - so it's fine hardcoded here.
const SITE_TAG = '1c920752456e42b5b5469641245a07c2';

// How far back to look. Web Analytics retention is limited on its own, so
// this is just a generously-early floor; Cloudflare returns whatever it
// actually still has within the window.
const SINCE = '2026-01-01T00:00:00Z';

const JSON_HEADERS = { 'content-type': 'application/json; charset=utf-8' };

function jsonResponse(body, extraHeaders) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: Object.assign({}, JSON_HEADERS, extraHeaders || {}),
  });
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const path = url.searchParams.get('path') || '';

  if (!ALLOWED_PATHS.has(path)) {
    return new Response(JSON.stringify({ error: 'unknown path' }), {
      status: 400,
      headers: JSON_HEADERS,
    });
  }

  // Serve from Cloudflare's edge cache when we've already answered for this
  // exact path recently, so a real reader loading the page never waits on
  // the GraphQL API, and we don't burn API quota per-pageview.
  const cache = caches.default;
  const cacheKey = new Request(url.toString(), request);
  const cached = await cache.match(cacheKey);
  if (cached) return cached;

  const token = env.CF_API_TOKEN;
  const accountTag = env.CF_ACCOUNT_TAG;

  if (!token || !accountTag) {
    // Not configured yet in the Pages dashboard - degrade quietly.
    return jsonResponse({ views: null, reason: 'not_configured' }, { 'cache-control': 'no-store' });
  }

  // Values are inlined directly into the query body (rather than passed as
  // typed GraphQL variables) because `path` is whitelist-checked above and
  // the rest come from trusted env vars/constants - and it sidesteps having
  // to match Cloudflare's exact internal scalar type names.
  const escapedPath = JSON.stringify(path);
  const now = new Date().toISOString();

  const query = `{
    viewer {
      accounts(filter: { accountTag: "${accountTag}" }) {
        rumPageloadEventsAdaptiveGroups(
          limit: 1000
          filter: {
            requestPath: ${escapedPath}
            siteTag: "${SITE_TAG}"
            datetime_geq: "${SINCE}"
            datetime_leq: "${now}"
          }
        ) {
          count
          avg { sampleInterval }
        }
      }
    }
  }`;

  try {
    const resp = await fetch('https://api.cloudflare.com/client/v4/graphql', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!resp.ok) {
      throw new Error('graphql http ' + resp.status);
    }

    const data = await resp.json();
    if (data.errors && data.errors.length) {
      throw new Error(JSON.stringify(data.errors));
    }

    const rows =
      (data.data &&
        data.data.viewer &&
        data.data.viewer.accounts &&
        data.data.viewer.accounts[0] &&
        data.data.viewer.accounts[0].rumPageloadEventsAdaptiveGroups) ||
      [];

    // Adaptive sampling: Cloudflare only logs roughly 1-in-N pageload
    // events and reports N as sampleInterval, so the real count is the
    // sampled count times that interval, summed across whatever rows
    // came back (defensive in case the API buckets the result).
    let views = 0;
    for (const row of rows) {
      const interval = (row.avg && row.avg.sampleInterval) || 1;
      views += Math.round((row.count || 0) * interval);
    }

    const response = jsonResponse({ views }, { 'cache-control': 'public, max-age=21600' });
    context.waitUntil(cache.put(cacheKey, response.clone()));
    return response;
  } catch (err) {
    return jsonResponse({ views: null, reason: 'fetch_failed' }, { 'cache-control': 'no-store' });
  }
}
