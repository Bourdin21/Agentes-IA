---
name: feedback-estandares-qa-implementador
description: "Standing library of implementation standards derived from a full sweep of the QA bug catalog, to stop the implementador from repeating the same known mistakes"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
---

The implementador agent has a dedicated standards file, `.github/instructions/32-estandares-qa-implementador.instructions.md`, built from a full sweep of `docs/qa/regresiones-manuales.yml` and every project's `6-qa.md` (ShowroomGriffin, KOI, delicias-naturales, ganaderia, vinosefue) as of 2026-07-03. It's referenced from `implementador-dotnet.agent.md`, `05-implementacion.prompt.md`, and the Cursor `capa-web.mdc` rule, so it loads automatically — no need to repeat these rules per project.

Key recurring bug patterns now codified as standing rules (see the file for full detail per pattern):
- **Edit-view combos not pre-populated** (the specific trigger for this sweep, 2026-07-03): any Select2/multi-select tied to an entity's configurable relation must initialize with the entity's already-assigned values on Editar, never empty.
- Select2 AJAX `processResults` must map real DTO field names (not invented ones); cascading combos use querystring params matching the action signature.
- MySQL RowVersion must be assigned manually in `SaveChanges` (no store-generated concurrency tokens like SQL Server).
- Conditional business fields (e.g. "Cuotas" needs count+%, "Cheque" needs a due date) need both client- and server-side validation, never just one side.
- State-machine action buttons must come from one shared transitions method used by both the view and the service — never a hardcoded per-state button map — and that transitions dictionary must be checked against the full approved state table (`2-disenador-funcional.md`), not just the happy path.
- Dynamic-row recalculation must patch only the affected DOM node, never re-render the whole `tbody` (destroys focus).
- Every sidebar link must be paired with a matching `[Authorize(Roles=...)]` on the target action (defense in depth) — verify each new/changed sidebar link actually resolves to a 200 before calling a module done.
- SweetAlert2 confirm handlers must resolve the target form via `data-form-id`/`data-form`/`data-action` fallback, not only `closest('form')`.
- DataTable listings with 2+ collection `Include`s + dynamic filter/order + Skip/Take must split into an ID-projection query then a full-Include query re-ordered in memory (avoids the EF6-MySQL provider crash pattern).
- "At least one item" guards on indexed dynamic lists (`Pagos[i]`) must check for real data, not `Count == 0` — MVC model binding preserves the ViewModel's constructor default when no indexed fields are posted.
- Never put Tag Helpers inside `<script type="text/x-template">` (Razor doesn't process them there); use `<template>` + `.innerHTML`.
- Prefer Select2 over native `<datalist>` for autocomplete (browser refresh quirks).
- Backfill scripts propagating FK/state to child rows must filter by the related entity's current state, not copy blindly.

**Why:** User (2026-07-03) explicitly asked for a full sweep of QA-found errors across all projects to turn the recurring root causes into standing implementation rules, starting from a specific complaint that edit-view combos were being initialized empty instead of pre-loaded with the entity's existing values.

**How to apply:** When reviewing or writing implementador output, check the diff against `32-estandares-qa-implementador.instructions.md` categories before considering a module done — these are exactly the mistake patterns that have recurred across projects. When a QA agent confirms a new bug with a generalizable root cause, add a new section to this file (not just the YAML catalog) per its own "Mantenimiento de este catalogo" note. Related: [[project-agentes-ia]], [[feedback-criterios-ui-implementador]].
