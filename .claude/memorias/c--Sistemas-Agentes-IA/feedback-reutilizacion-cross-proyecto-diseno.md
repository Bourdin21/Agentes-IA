---
name: feedback-reutilizacion-cross-proyecto-diseno
description: "Diseño funcional and arquitectura stages must scan all projects' history for reusable code before designing from scratch, not just the implementador stage"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-07-25T15:11:21.007Z
---

The cross-project reuse scan that already existed only for the **implementador** agent (scan `/docs/*/definiciones/5-implementador.md` across all projects before building an ABM/feature from scratch, copy+adapt code from the origin repo if a match exists) must now also happen earlier, during **Diseño funcional** and **Arquitectura técnica** — not just at implementation time.

**Why:** User (2026-07-24) asked explicitly that `/agentes-ia-orquestador` always evaluate, during system design, whether functionality is already implemented in another project, to maximize code reuse. Doing the reuse check only at implementation time meant the design/architecture stages could design something from scratch that later got overridden by a reuse decision at implementation, causing rework/inconsistency between the documented design and the actually-reused code.

**How to apply:** Encoded directly in the repo so it fires automatically:
- `disenador-funcional.agent.md` / `.github/prompts/02-diseno.prompt.md`: scan `docs/*/definiciones/{2-disenador-funcional,5-implementador}.md`, new "salida mínima" item 0 reporting the scan result.
- `arquitecto-mvc.agent.md` / `.github/prompts/03-arquitectura.prompt.md`: scan `docs/*/definiciones/{3-arquitecto-mvc,5-implementador}.md`, same pattern, referencing the origin project's `ruta_repositorio` (in its `metadata.md`) as the concrete reuse target.
- `09-orquestador-flujo-completo.prompt.md` and `.claude/commands/agentes-ia-orquestador.md`: added an explicit orchestration rule requiring this scan during Diseño/Arquitectura.
- `CLAUDE.md` "Reglas base": added as a top-level always-applies rule for visibility.

Now all three stages (Diseño → Arquitectura → Implementación) progressively scan for and build on prior cross-project work, instead of only the last one. Related: [[project-agentes-ia]].
