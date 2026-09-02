---
name: reference-la-platense-docs
description: Ubicación de la documentación funcional/arquitectura/presupuesto del proyecto La Platense y del proceso de orquestación del estudio
metadata: 
  node_type: memory
  type: reference
  originSessionId: bc755a3e-0b32-4b42-9695-956808c26af7
  modified: 2026-08-10T16:07:37.677Z
---

Toda la documentación de definiciones del proyecto La Platense vive fuera de este repo, en `C:\Sistemas\Agentes-IA\docs\la-platense\`:
- `metadata.md` — datos generales, estado, ruta del repo real.
- `trazabilidad.md` — registro cronológico de decisiones por etapa/agente (fuente de verdad histórica, más confiable que la memoria de cada agente para entender "por qué" se llegó a un estado).
- `definiciones/1-analista-funcional.md` — 16+ módulos, reglas funcionales (R1-R11), criterios de aceptación (PF1-PF15), preguntas abiertas (§9).
- `definiciones/2-disenador-funcional.md` — flujos de UI no triviales (conversión de unidades, venta Borrador→Facturada, importación de listas, CC empleados).
- `definiciones/3-arquitecto-mvc.md` — entidades EF, Services, mapa de reutilización cross-proyecto, riesgos técnicos.
- `definiciones/4-presupuestador.md` — WBS, horas, tier de descuento, precio.
- `definiciones/5-implementador.md`, `6-qa.md`, `7-documentador.md` — plantillas vacías, se completan durante Implementación/QA/cierre.
- `presupuesto-cliente.md` — documento final entregado al cliente.

El proceso de orquestación (gates obligatorios Discovery→Diseño→Arquitectura→Presupuesto→Implementación, regla de reutilización cross-proyecto) está definido en `C:\Sistemas\Agentes-IA\CLAUDE.md`.

**How to apply:** cuando el usuario pida implementar un módulo de La Platense, leer primero la sección correspondiente en `3-arquitecto-mvc.md` (entidades/servicios) y `1-analista-funcional.md` (reglas/criterios de aceptación) antes de escribir código — son la fuente de verdad del alcance acordado con el cliente, no derivarlo del código todavía inexistente. Ver también [[project_la_platense_status]] para el estado y la pregunta abierta pendiente.
