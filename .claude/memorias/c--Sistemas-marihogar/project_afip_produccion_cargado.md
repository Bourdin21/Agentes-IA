---
name: project-afip-produccion-cargado
description: "MariHogar ya tiene certificado AFIP real de producción cargado (28/07/2026), contradiciendo la documentación del estudio que dice que está pendiente."
metadata: 
  node_type: memory
  type: project
  originSessionId: b2b16dbd-9cb1-4a87-ba3b-eec8a3ba1c9d
  modified: 2026-08-16T21:42:40.988Z
---

`MariHogar.Web/appsettings.Production.json` tiene `Afip.Ambiente="Produccion"`, CUIT real (20331136132) y ruta a `Certificados/marihogarprod.p12` — y ese archivo `.p12` existe físicamente en el repo, con fecha de carga 28/07/2026. Ni el appsettings ni el `.p12` están versionados en git (ambos correctamente ignorados vía `.gitignore`), así que no hay exposición de secretos.

**Estado confirmado por el usuario (16/08/2026):** el certificado está cargado y disponible para que el cliente lo pruebe, pero todavía NO fue usado/probado — no es una discrepancia a resolver, es el estado esperado (pre-staged). La documentación del estudio (1-analista-funcional.md, 4-presupuestador.md, 5-implementador.md, 6-qa.md) sigue sin reflejar esto y debería actualizarse en la próxima pasada de documentación.

**Cómo aplicar:** cualquier "Facturar" real en producción a partir de ahora genera un comprobante fiscal real (no homologación) — tenerlo presente si se toca ese módulo o se coordina una prueba con el cliente.
