---
name: feedback-no-smoke-test
description: El implementador (agente/subagente) nunca debe ejecutar smoke test funcional propio — el usuario siempre prueba manualmente.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b2b16dbd-9cb1-4a87-ba3b-eec8a3ba1c9d
  modified: 2026-07-24T18:19:31.747Z
---

Cuando se delega implementación de código (subagent implementador, o instrucciones directas de codificación), nunca pedir/ejecutar smoke test funcional propio: no levantar la app, no probar flujos por navegador ni por API/curl, no simular requests reales para "verificar que funciona". La evidencia de cierre técnico es build limpio + revisión de código propia (releer lo escrito). En vez de un resultado de smoke test ya ejecutado, dejar una guía de pasos concreta para que el usuario la pruebe manualmente él mismo.

**Why:** El usuario (Joaquín) prefiere probar manualmente el sistema él mismo — lo pidió explícitamente durante el desarrollo de marihogar ("no hacer smoke test funcional. lo voy a hacer manual" y luego "no hacer smoke test nunca, anotarlo en el Agentes IA"). Es una preferencia de proceso general, no específica de un módulo o proyecto puntual.

**How to apply:** Al briefear cualquier subagent implementador (agentes-ia-implementador u otro rol de codificación) en cualquier proyecto, nunca incluir "smoke test funcional" ni "probar el flujo end-to-end" como tarea del propio agente. Pedir en cambio: build limpio + migraciones aplicadas (si corresponde) + revisión de código + lista de pasos para que el usuario verifique manualmente. Esta regla ya quedó reflejada como estándar global del estudio en `C:/Sistemas/Agentes-IA/.github/instructions/00-operativa-global.instructions.md`, `.github/agents/implementador-dotnet.agent.md`, `.github/prompts/05-implementacion.prompt.md` y `.github/instructions/32-estandares-qa-implementador.instructions.md` — pero aplica también fuera de ese framework de agentes, a cualquier tarea de codificación delegada en cualquier proyecto.
