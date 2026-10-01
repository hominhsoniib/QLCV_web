const CACHE_NAME = 'qlcv-mobile-v2';
const APP_CACHE_NAME = /^qlcv-mobile-v[0-9]+$/;
const ASSETS_TO_CACHE = ['/static/css/mobile.css', '/manifest.json'];

function isPrivateUpload(url) {
  if (url.origin !== self.location.origin) return false;
  let path = url.pathname;
  // Catch encoded separators/aliases also refused by the parent static mount.
  for (let i = 0; i < 3; i++) {
    try {
      const decoded = decodeURIComponent(path);
      if (decoded === path) break;
      path = decoded;
    } catch (_) { break; }
  }
  path = path.replace(/\\/g, '/').replace(/\/+/g, '/').toLowerCase();
  return path === '/static/uploads' || path.startsWith('/static/uploads/');
}

function isPublicAsset(url) {
  return url.origin === self.location.origin && !isPrivateUpload(url) &&
    (url.pathname.startsWith('/static/') || url.pathname === '/manifest.json');
}

function safePublicResponse(response, url) {
  if (response.status !== 200 || response.redirected || !isPublicAsset(url)) return false;
  if (/\b(private|no-store)\b/i.test(response.headers.get('Cache-Control') || '')) return false;
  if (/text\/html/i.test(response.headers.get('Content-Type') || '')) return false;
  return !response.url || isPublicAsset(new URL(response.url));
}

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await Promise.all(ASSETS_TO_CACHE.map(async (path) => {
      const url = new URL(path, self.location.origin);
      try {
        const response = await fetch(url.href);
        if (safePublicResponse(response, url)) await cache.put(url.href, response);
      } catch (_) { /* Public precache failure must not cache an error/login page. */ }
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const current = await caches.open(CACHE_NAME);
    for (const name of await caches.keys()) {
      if (!APP_CACHE_NAME.test(name)) continue;
      const old = await caches.open(name);
      for (const request of await old.keys()) {
        const url = new URL(request.url);
        // Never read private bytes even during purge. Remove old authenticated
        // HTML/API/cross-origin entries from QLCV-owned caches as well.
        if (request.method !== 'GET' || !isPublicAsset(url)) {
          await old.delete(request);
          continue;
        }
        const response = await old.match(request);
        if (!response || !safePublicResponse(response, url)) {
          await old.delete(request);
        } else if (name !== CACHE_NAME && !(await current.match(request))) {
          await current.put(request, response);
        }
      }
      if (name !== CACHE_NAME) await caches.delete(name);
    }
    // Do not claim existing clients until private entry invalidation completes.
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  // Private upload and authenticated dynamic/API requests never touch Cache API.
  // All methods, including HEAD/Range/conditional requests, reach the gateway.
  if (isPrivateUpload(url) || !isPublicAsset(url)) {
    event.respondWith(fetch(request, { cache: 'no-store' }));
    return;
  }
  if (request.method !== 'GET') return;
  event.respondWith((async () => {
    try {
      const response = await fetch(request);
      if (safePublicResponse(response, url)) {
        const copy = response.clone();
        try {
          const cache = await caches.open(CACHE_NAME);
          await cache.put(request, copy);
        } catch (_) { /* Cache storage failure must not replace a valid network response. */ }
      }
      return response;
    } catch (_) {
      const cache = await caches.open(CACHE_NAME);
      const cached = await cache.match(request);
      if (cached && safePublicResponse(cached, url)) return cached;
      return new Response('Offline', { status: 503, headers: { 'Content-Type': 'text/plain', 'Cache-Control': 'no-store' } });
    }
  })());
});
