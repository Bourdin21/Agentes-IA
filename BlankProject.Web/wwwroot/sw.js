// Service Worker — VirtualWallet PWA
// Estrategia: Network-first (siempre intenta la red, fallback a cache)
// No cachea contenido dinámico agresivamente para evitar datos desactualizados.

const CACHE_NAME = 'vw-cache-v1';

// Assets estáticos que se pre-cachean en la instalación
const PRECACHE_URLS = [
    '/css/olvidata-theme.css',
    '/css/site.css',
    '/favicon.svg',
    '/icons/icon-192.png',
    '/icons/icon-512.png'
];

// Instalación: pre-cachear assets estáticos
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

// Activación: limpiar caches viejos
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(names =>
            Promise.all(
                names.filter(n => n !== CACHE_NAME).map(n => caches.delete(n))
            )
        ).then(() => self.clients.claim())
    );
});

// Fetch: network-first para navegación, cache-first para assets estáticos
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // Solo manejar requests del mismo origen
    if (url.origin !== location.origin) return;

    // No interceptar POST ni requests de API
    if (event.request.method !== 'GET') return;

    // Assets estáticos (css, js, imágenes): cache-first
    if (url.pathname.match(/\.(css|js|png|jpg|svg|ico|woff2?)$/)) {
        event.respondWith(
            caches.match(event.request).then(cached =>
                cached || fetch(event.request).then(response => {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    return response;
                })
            )
        );
        return;
    }

    // Navegación y demás: network-first (para tener datos frescos)
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Cachear páginas exitosas para offline básico
                if (response.ok && event.request.mode === 'navigate') {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                }
                return response;
            })
            .catch(() => caches.match(event.request))
    );
});
