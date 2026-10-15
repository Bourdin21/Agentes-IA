---
name: entorno-sin-navegador
description: En este entorno ningún navegador (MCP playwright ni Chrome propio) alcanza el puerto de la app levantada por las herramientas — probar conectividad ANTES de planificar la corrida
metadata:
  type: project
---

Ningún navegador disponible desde las herramientas alcanza el puerto de una app levantada por esas
mismas herramientas: `ERR_CONNECTION_REFUSED` contra `localhost`, `127.0.0.1` y la IP de LAN, con el
listener confirmado por `netstat` y accesible por `curl` desde el mismo contexto. Medido el
2026-10-15 con el MCP `playwright` y con Chrome real lanzado dentro y fuera del sandbox, con y sin
`--no-sandbox` y `--disable-features=NetworkServiceSandbox`. La corrida del 2026-09-14 ya lo había
anotado como "Playwright MCP aislado del host"; ahora está medido también contra un navegador propio,
así que **no es el MCP, es la red del entorno**.

**Why:** gasté 3 reintentos probando combinaciones de flags antes de aceptarlo. El síntoma engaña
porque `curl` sí llega, así que parece un problema del navegador y no de la red.

**How to apply:** al arrancar una corrida que necesite navegador, levantar la app y hacer **un solo**
intento de `browser_navigate`. Si falla, declararlo de entrada, marcar como **NO VERIFICADO** (nunca
PASS) todo criterio que necesite un navegador real —service workers, push recibido, estados de un
botón, tema oscuro— y proponerle a Joaquín el chequeo manual corto. No reintentar con otra
combinación de flags.

El plan B que sí funciona para todo lo demás: HTTP autenticado con `requests` + SQL directo contra la
base + el log de la app. Para servicios externos salientes conviene un **doble local**: en CRM-028
puse un HTTP server propio como `Endpoint` de la suscripción push, lo que permitió ver el sobre real
que emite el servidor y devolver a voluntad 201/404/410/500/conexión rechazada. Ese patrón sirve para
cualquier integración saliente cuyo destino sea una URL guardada en la base.

Dos detalles de este CRM que me costaron un reintento cada uno: la app redirige a HTTPS (hay que
levantarla en `https://localhost:7201` y usar `verify=False`), y el webhook responde 200 al instante
y procesa en background — hay que esperar el final del procesamiento antes de leer la base, no el 200.

Relacionado: [[crm-028-estado]]
