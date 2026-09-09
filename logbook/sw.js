/* Offline for the logbook.
 *
 * A field logbook that needs a working connection to produce a book is not a
 * field tool. Removing the CDN took the third party out of it; this takes the
 * network out of it. After one complete visit every piece the generator needs
 * is in the cache, and the page builds a book on a mountain with the phone in
 * aeroplane mode.
 *
 * Scope is this directory, so nothing here touches the rest of the site.
 *
 * Bump VERSION whenever anything in logbook/ changes, or returning visitors
 * keep the old copy. The activate step clears every older cache.
 */
const VERSION = "k4dia-logbook-v1";

/* The page itself and the small things it needs to open. */
const SHELL = [
  "./",
  "./index.html",
  "./app.js",
  "./worker.js",
  "./manifest.json",
  "./catalogue.json",
  "./fonts/IBMPlexSans-Regular.woff2",
  "./fonts/IBMPlexSans-SemiBold.woff2",
  "./fonts/IBMPlexMono-Regular.woff2",
  "./fonts/IBMPlexMono-SemiBold.woff2",
  "./fonts/IBMPlexSansCondensed-Bold.woff2",
  "./fonts/IBMPlexSansCondensed-SemiBold.woff2",
];

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(VERSION);
    // One miss must not fail the whole install, or a single renamed file
    // leaves the operator with no offline copy at all and no clue why.
    await Promise.all(SHELL.map((url) => cache.add(url).catch(() => null)));
    self.skipWaiting();
  })());
});

/* The heavy pieces: the Python runtime, the two wheels and the book payload.
 *
 * These are not an extra download. The generator boots as soon as the page
 * opens, so the browser pulls every one of them on every visit whether the
 * operator presses the button or not. Holding them here costs nothing beyond
 * what already happened, and it is the difference between an offline visit
 * that works because the HTTP cache happened to keep a copy and one that
 * works because we kept it deliberately.
 *
 * Warmed after activation rather than during install so a slow first load is
 * never held up waiting for 13 MB of wasm. */
const RUNTIME = [
  "./pyodide/pyodide.mjs",
  "./pyodide/pyodide.asm.mjs",
  "./pyodide/pyodide.asm.wasm",
  "./pyodide/python_stdlib.zip",
  "./pyodide/pyodide-lock.json",
  "./vendor/pillow-12.2.0-cp314-cp314-pyemscripten_2026_0_wasm32.whl",
  "./vendor/reportlab-5.0.1-py3-none-any.whl",
  "./fieldrecord.zip",
];

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names
      .filter((n) => n.startsWith("k4dia-logbook-") && n !== VERSION)
      .map((n) => caches.delete(n)));
    await self.clients.claim();

    const cache = await caches.open(VERSION);
    // One at a time. Eight parallel fetches, one of them 9 MB, competes with
    // the page for the connection on exactly the slow link this is meant to
    // help with.
    for (const url of RUNTIME) {
      if (await cache.match(url)) continue;
      try { await cache.add(url); } catch (err) { /* next visit will try again */ }
    }
  })());
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  /* The page itself comes from the network when there is one, so an update
     lands on the next visit rather than whenever the cache happens to turn
     over. Everything else is immutable in practice and comes from the cache
     first, which is also what makes the second build start in a second
     instead of thirty. */
  const isDocument = request.mode === "navigate"
    || (request.destination === "document");

  if (isDocument) {
    event.respondWith((async () => {
      try {
        const fresh = await fetch(request);
        const cache = await caches.open(VERSION);
        cache.put(request, fresh.clone());
        return fresh;
      } catch (err) {
        const hit = await caches.match(request, { ignoreSearch: true });
        return hit || caches.match("./index.html");
      }
    })());
    return;
  }

  event.respondWith((async () => {
    const hit = await caches.match(request, { ignoreSearch: true });
    if (hit) return hit;
    const fresh = await fetch(request);
    // Range requests answer 206 and must not be cached: a partial body
    // served back as a whole one corrupts the wasm.
    if (fresh && fresh.ok && fresh.status === 200) {
      const cache = await caches.open(VERSION);
      cache.put(request, fresh.clone());
    }
    return fresh;
  })());
});
