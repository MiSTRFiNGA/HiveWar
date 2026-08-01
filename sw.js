// HiVE WAR — offline shell cache. Cache-first with runtime population: the
// first load fetches from network and stores a copy; every load after that
// (including offline) is served from cache. Bump CACHE_VERSION to force a
// refresh of the shell on the next visit.
// NOTE: the cache NAME prefix below stays 'hiveswarm-shell-' (a Cache Storage key, not a
// player-facing string) — only CACHE_VERSION needs bumping to bust stale caches; renaming
// the prefix would work too, but bumping the version is the documented mechanism and is
// sufficient on its own to force every returning tester to refetch the shell.
const CACHE_VERSION = 'v5';   // bumped 2026-08-01 for game v1.7 (paint undo/save fix, line tool, resize/crop, points-only barriers)
const CACHE_NAME = `hiveswarm-shell-${CACHE_VERSION}`;
const PRECACHE_URLS = ['./', './index.html', './manifest.webmanifest'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  let url;
  try { url = new URL(req.url); } catch (e) { return; }
  if (url.origin !== self.location.origin) return; // leave cross-origin (CDN/portal SDK) alone

  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((res) => {
        if (res && res.ok && res.type === 'basic') {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy)).catch(() => {});
        }
        return res;
      }).catch(() => cached);
    })
  );
});
