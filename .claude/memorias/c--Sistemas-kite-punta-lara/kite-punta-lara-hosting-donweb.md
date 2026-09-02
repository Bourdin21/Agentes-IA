---
name: kite-punta-lara-hosting-donweb
description: "Trampas del hosting DonWeb de club.olvidata.com.ar — descubiertas a los golpes, no volver a pisarlas."
metadata: 
  node_type: memory
  type: project
  originSessionId: aeabc362-0545-4e4d-b049-1f477db62add
  modified: 2026-09-02T21:33:18.669Z
---

Hallazgos del hosting de `club.olvidata.com.ar` (DonWeb, LiteSpeed, PHP 8.4).
Todos costaron tiempo de descubrir; están también en el README del repo.

- **La cuenta FTP `club@olvidata.com.ar` está enjaulada en el docroot del
  subdominio.** Su `/` YA ES la carpeta del sitio: no existe un
  `public_html/club` navegable desde ahí, aunque el panel lo muestre así.
- **`Require all denied` / `Deny from all` NO se aplican** — el `AllowOverride`
  del hosting no habilita esa categoría. Se descubrió con `vendor/autoload.php`
  quedando descargable en el primer deploy. Lo único que funciona para
  proteger carpetas es `mod_rewrite`: `RewriteRule ^ - [F,L]`.
- **No hay SSH ni cliente MySQL** contra la base de producción. Por eso
  `scripts/deploy.sh` sube un corredor de migraciones con token de un solo uso,
  lo ejecuta y lo borra verificando después que devuelva 404.
- **La caché hay que limpiarla en cada deploy.** Guarda la respuesta ya armada,
  así que al cambiar la forma de un dato el archivo viejo sigue vigente y el
  código nuevo lee una estructura vieja, **devolviendo nulls en silencio, sin
  error**. Ya está automatizado en el script.
- **El primer pedido después de un deploy va en frío** (caché recién borrada) y
  dispara todas las consultas externas sin valor viejo al que caer. Un blip de
  red ahí devolvía 500. Hay reintentos en las dos puntas.

**Fuentes externas:**
- **CARP / Pilote Norden** tiene endpoint real (`POST /ecsCommand.php`,
  `stationID=2`) pero su servidor tiene TLS roto: certificado incompleto y DH
  legacy. OpenSSL lo rechaza, Windows/Schannel no. Se desactivó la
  verificación **solo para ese host**, con aprobación explícita de Joaquín.
  Además su serie histórica va ~3 h atrasada respecto de su propia lectura
  actual, y tiene huecos reales.
- **SMN (`ws.smn.gob.ar`)** está detrás de un challenge de Cloudflare: 503 a
  cualquier request sin navegador real. Degrada a "no disponible".

Ver [[kite-punta-lara-decisiones-de-producto]].
