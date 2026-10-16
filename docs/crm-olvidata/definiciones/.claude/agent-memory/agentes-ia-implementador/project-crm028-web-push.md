---
name: project-crm028-web-push
description: CRM-028 (Web Push) y CRM-029 quedaron commiteados con GO de QA pero SIN deployar; el deploy lo ejecuta Joaquín y el cert de portal.olvidata.com.ar vence 2026-10-19 sin renovar
metadata:
  type: project
---

CRM-028 (Web Push para chats derivados a mano) y CRM-029 (su fix de anti-ruido) están **commiteados
con GO de QA pero sin deployar** al 2026-10-16: `1005cd2` + `fb45699`, más `e5da865` (sesión de un mes
para la PWA) que viaja con ellos. El runbook completo de deploy está en `5-implementador.md`.

**Why:** el deploy es la única acción de la secuencia que Joaquín se reservó ("el deploy lo hago yo
cuando QA re-verifique"). Ver [[feedback-no-commit-no-deploy]].

**How to apply:** dos cosas que condicionan cualquier trabajo futuro sobre esta funcionalidad:

1. **El certificado de `portal.olvidata.com.ar` vence el 2026-10-19 y Joaquín decidió explícitamente
   no renovarlo ahora.** Web Push exige HTTPS válido, así que cuando venza el push se cae junto con el
   sitio. No es una decisión a revisar por iniciativa propia, pero sí el primer dato a mencionar si
   alguien reporta que "los avisos dejaron de llegar" después de esa fecha.
2. **La privada de VAPID todavía no está cargada en producción.** Sin ella el canal degrada bien
   (no tira, no avisa) — o sea que un deploy sin ese paso se ve sano y no notifica nada. Es el primer
   chequeo si el push no llega en producción.

Defecto abierto que NO se arregló: **CRM-030** (minor) — cualquier estado del embudo es asignable a
mano, y el viaje `DerivadoManual` → `Descartado` → `DerivadoManual` sin abrir el chat deja el aviso
mudo. Hipótesis de fix de QA: limpiar `FechaUltimoAvisoDerivado` al salir de `DerivadoManual`.
