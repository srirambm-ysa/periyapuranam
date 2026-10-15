/* Periyapuranam offline reader — cache-first shell, network-first content.
 * Scope: registered from /sw.js so it controls the whole origin.
 * Shell (page/CSS/fonts/icons) is version-pinned: bump CACHE on shell edits.
 * Story JSONs + verse art go through the runtime cache so fresh content
 * always wins when online, and the last-read stories open when offline.
 * Version: periyapuranam-v1 (match CACHE below on every shell change).
 */
const CACHE = 'periyapuranam-v1';
const SHELL = [
    '/site/periya_puranam_index.html',
    '/site/ppreader.css',
    '/site/fonts.css',
    '/site/fa/all.min.css',
    '/site/manifest.webmanifest',
    '/site/images/lingam.svg',
    '/site/images/icon-192.png',
    '/site/images/icon-512.png',
    '/site/images/apple-touch-icon.png',
    '/site/images/sekkizhar_384.jpg'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE).then((cache) => cache.addAll(SHELL))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(
                keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))
            ))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const req = event.request;
    if (req.method !== 'GET') return;
    const url = new URL(req.url);
    if (url.origin !== self.location.origin) return; // analytics/CDN: let through

    // Navigations: network first (fresh shell wins), cache fallback offline.
    if (req.mode === 'navigate') {
        event.respondWith(
            fetch(req)
                .then((res) => {
                    const copy = res.clone();
                    caches.open(CACHE).then((c) => c.put(req, copy));
                    return res;
                })
                .catch(() => caches.match('/site/periya_puranam_index.html'))
        );
        return;
    }

    // Static + story JSON: cache first, populate on miss, error when offline.
    event.respondWith(
        caches.match(req).then((hit) => {
            const miss = fetch(req).then((res) => {
                if (res && (res.status === 200 || res.type === 'opaque')) {
                    const copy = res.clone();
                    caches.open(CACHE).then((c) => c.put(req, copy));
                }
                return res;
            }).catch(() => hit);
            return hit || miss;
        })
    );
});
