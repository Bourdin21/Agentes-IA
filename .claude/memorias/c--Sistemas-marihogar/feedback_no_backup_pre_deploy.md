---
name: feedback-no-backup-pre-deploy
description: "No hacer backup automático de la base de producción antes de cada deploy — regla general, no solo para marihogar"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b2b16dbd-9cb1-4a87-ba3b-eec8a3ba1c9d
  modified: 2026-08-21T13:20:24.994Z
---

No ejecutar un backup (mysqldump u otro) de la base de datos de producción automáticamente antes de cada deploy. Ni en marihogar ni en otros proyectos.

**Why:** El usuario lo pidió explícitamente el 2026-08-21 durante una sesión de troubleshooting de AFIP en marihogar, después de varios backups consecutivos que ralentizaban el ciclo de iteración (cada uno ~1-2 minutos) en un contexto donde se estaban haciendo varios deploys seguidos de prueba y error. Lo marcó como "regla general del agente AI", no una excepción puntual.

**How to apply:** No asumir más que "backup antes de cualquier deploy a producción" es la política por defecto (a diferencia de lo que se venía haciendo antes de este feedback, ver [[user_marihogar_deploy_discipline]] si existe). Si el usuario quiere un backup en un caso puntual, lo va a pedir explícitamente. Esto no cambia otras prácticas de seguridad (confirmar antes de tocar producción, verificar el resultado real después de un deploy/migración) — solo elimina el paso de backup automático previo.
