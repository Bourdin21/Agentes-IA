---
name: project-agentes-ia-mejoras-2026-08-15
description: Tres mejoras estructurales agregadas al sistema Agentes-IA el 2026-08-15 (catalogo de patrones, dataset de calibracion estructurado, Playwright MCP para QA)
metadata:
  type: project
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-08-15T17:13:43.405Z
---

Tras una pregunta exploratoria del usuario ("entendes la estructura del modelo... que le agregarias?"), se implementaron 3 gaps identificados en la arquitectura del sistema de agentes:

**1. `docs/patrones/catalogo.yml`** — catalogo estructurado de patrones reutilizables cross-proyecto (mismo espiritu que `docs/qa/regresiones-manuales.yml` pero para diseño/codigo reutilizable, no bugs). Antes, la reutilizacion cross-proyecto dependia de que disenador-funcional/arquitecto-mvc/implementador leyeran manualmente ~147 archivos `definiciones/*.md` de ~26 proyectos (honor system, sin indice). Ahora consultan el catalogo primero (lookup rapido), y el escaneo completo queda como fallback. Sembrado con 8 patrones conocidos (PAT-001 a PAT-008: ledger/CuentaCorriente, AdjuntoService, MetodoPago, RowVersion manual MySQL, maquina de estados, integracion AFIP/ARCA WSFEv1, sitio Astro+contacto PHP, DataTables+filtros) — varios marcados `pendiente_verificar: true` porque no tengo las rutas de archivo exactas confirmadas (deben completarse cuando un agente con acceso real al repo los use). Obligacion agregada a los 3 agentes: registrar patrones nuevos en el catalogo antes de cerrar la etapa, igual que QA con bugs.

**2. `docs/calibracion/dataset.yml`** — version estructurada (YAML) de las tablas de calibracion que vivian solo como prosa acumulada en `27-presupuesto-parametros.instructions.md` (ya un archivo enorme de notas historicas). Contiene: `cierres_reales` (6 proyectos con ratio PERT/real medido), `rangos_por_tipo_modulo` (13 tipos), `modificacion_modulo_existente` (7 tipos). El presupuestador ahora lee este YAML primero (Paso 0) para medianas/rangos; la prosa de 27-presupuesto-parametros sigue siendo la fuente de "por que paso X" pero ya no hace falta releerla entera para sacar un numero. Obligacion: al cerrar un proyecto con datos reales, agregar la entrada tanto al YAML como a la prosa (no deben desincronizarse).

**3. Servidor MCP Playwright (`.mcp.json` + `.claude/settings.json`)** — se descubrio que la automatizacion de QA por navegador (`33-verificacion-automatizada-qa.instructions.md`, vigente desde 2026-08-14) NO tenia ninguna herramienta de automatizacion de navegador realmente configurada (no habia `.mcp.json` en el repo, ni MCP de browser en `settings.json`) — es decir, probablemente estaba cayendo siempre al fallback manual sin que se notara. Se agrego `.mcp.json` con el servidor `@playwright/mcp` (via `npx`, node/npx confirmados disponibles en el entorno) y se permitieron sus herramientas (`mcp__playwright__*`) en `.claude/settings.json`. Se actualizo `agentes-ia-qa.md` y `33-verificacion-automatizada-qa.instructions.md` para nombrar la herramienta concreta en vez de "la herramienta disponible" generico.

**Como aplicar:** verificar en el proximo proyecto que use QA en modo Agent que el servidor Playwright efectivamente conecta (primera ejecucion hace `npx -y @playwright/mcp@latest`, puede tardar por la descarga). Si falla la conexion, revisar `.mcp.json` y que Node/npx sigan en el PATH. Relacionado: [[project-agentes-ia]], [[feedback-qa-no-browser-tests]], [[feedback-costo-ia-interno-presupuesto]].
