---
name: feedback-criterios-ui-implementador
description: Standing UI/UX development standards for the implementador agent — senior-designer screen structure and DataTables columns-define-filters rule
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
---

Two standing development criteria apply to **every future Razor view** the implementador agent builds, across all projects:

1. **Screen structure with senior graphic-designer judgment**: clear visual hierarchy (title/context up top, primary vs. secondary actions visually differentiated), logical grouping of related fields (cards/fieldsets, not one flat form once past ~8 fields), predictable top-to-bottom/left-to-right reading order, destructive actions always visually distinct with SweetAlert2 confirmation. Acceptance test: a first-time user must understand what to do on that screen without external instructions.
2. **Every listing renders with DataTables (server-side)**, and **the columns visible in the grid are exactly what defines the available filters** — the user must be able to filter by any data point they can see in the listing. No column without a matching filter, no hidden filter without a matching column (except an explicitly justified global text search).

**Why:** User (2026-07-03) stated explicitly these are standardized development criteria for future implementations, not one-off requests for a specific project.

**How to apply:** Encoded directly in `.github/instructions/25-frontend-design-system.instructions.md` (two new sections) and cross-referenced from `.github/agents/implementador-dotnet.agent.md` and `.github/instructions/26-checklists.instructions.md` (checklist items 10/10a for new entities, item 3 of the report/export checklist). These fire automatically whenever the implementador agent is invoked — no need to repeat the instruction per project. Related: [[project-agentes-ia]].
