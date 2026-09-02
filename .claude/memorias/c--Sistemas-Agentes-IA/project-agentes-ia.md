---
name: project-agentes-ia
description: "Repositorio Agentes-IA: sistema de agentes MVC para proyectos .NET 10. Define workflow, instrucciones modulares y agentes especializados."
metadata: 
  node_type: memory
  type: project
  originSessionId: b323fd2c-8257-46a5-a3fa-122f927a885a
  modified: 2026-08-30T14:07:50.132Z
---

Este repositorio centraliza memoria de trabajo, instrucciones y agentes para todos los proyectos .NET del estudio.

**Why:** Es el repositorio de operativa del estudio: define cómo se trabaja en todos los proyectos (workflow, estimación, documentación).

**How to apply:** Al trabajar en cualquier proyecto (.NET, MVC), siempre referenciar las instrucciones de este repo. Seguir la secuencia obligatoria de etapas.

## Estructura clave

- `.github/copilot-instructions.md` — orquestador principal, inventario de proyectos, patrones cross-proyecto
- `.github/agents/` — definición de agentes (1-analista, 2-diseñador, 3-arquitecto, 4-presupuestador, 5-implementador [.NET y Astro-front], 6-qa, 7-documentador)
- `.github/instructions/` — instrucciones modulares por capa y etapa (00-operativa-global hasta 34-integracion-afip-arca); `27-presupuesto-parametros.instructions.md` es la mas volatil, cambia de regla seguido — siempre revisar notas `Superseded` antes de aplicar una regla de precio de memoria
- `.github/prompts/` — prompts por etapa del workflow
- `docs/patrones/catalogo.yml` — catalogo de patrones reutilizables cross-proyecto (lookup rapido antes de escanear todo `docs/*/definiciones/`)
- `docs/calibracion/dataset.yml` — dataset estructurado de rangos por tipo de modulo y cierres reales
- `docs/<proyecto>/definiciones/` — memoria acumulativa de cada agente por proyecto
- `docs/indice.md` — **fuente de verdad viva del estado de cada proyecto** (no duplicar esta lista en memoria — cambia demasiado seguido, leer el archivo directo)
- Agentes de negocio del estudio (`olvidata-ceo`, `olvidata-marketing`, `olvidata-sales`, `olvidata-infra`) — no viven en este repo, son agentes de cuenta separados para estrategia/pricing/venta/infraestructura del estudio, distintos de los agentes tecnicos de proyecto de cliente

## Secuencia operativa

Discovery → Análisis → Diseño → Arquitectura → Presupuesto → Implementación → Pruebas → Documentación → Cierre calibración

## Proyectos activos

Ver `docs/indice.md` en el repo — no mantener una copia de esta lista en memoria, queda desactualizada rapido (esta memoria estuvo 67 dias sin tocarse con una lista de 4 proyectos que ya no refleja el pipeline real).

## CLAUDE.md creado

Se creó `C:\Sistemas\Agentes-IA\CLAUDE.md` como punto de entrada para Claude Code, referenciando todos los agentes e instrucciones.
