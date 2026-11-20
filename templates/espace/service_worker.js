{% load static %}/* Service worker de l'espace d'administration (PWA). */
const CACHE_NAME = "kcdelices-admin-v2";
const OFFLINE_URL = "/espace/hors-ligne/";
const PRECACHE_URLS = ["{{ offline_url|default:'/espace/hors-ligne/' }}", "{% static 'css/output.css' %}"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .catch(() => undefined)
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Navigation : le réseau d'abord, jamais de page d'administration en cache.
  // Seules les pages de l'espace admin ont une page de secours ; le site
  // public garde le comportement natif du navigateur.
  if (request.mode === "navigate") {
    if (!url.pathname.startsWith("/espace")) return;
    event.respondWith(
      fetch(request).catch(async () => {
        const cached = await caches.match(OFFLINE_URL);
        return (
          cached ||
          new Response("<h1>Hors ligne</h1>", {
            status: 503,
            headers: { "Content-Type": "text/html; charset=utf-8" },
          })
        );
      })
    );
    return;
  }

  // Ressources statiques : cache immédiat puis mise à jour silencieuse.
  if (url.pathname.startsWith("/static/") || url.pathname.startsWith("/media/")) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const network = fetch(request)
          .then((response) => {
            if (response && response.ok) {
              const copy = response.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
            }
            return response;
          })
          .catch(() => cached);
        return cached || network;
      })
    );
  }
});
