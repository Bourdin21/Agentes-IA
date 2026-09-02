---
name: feedback-qa-no-browser-tests
description: REVERSED 2026-08-14 — QA agent now DOES automate browser verification for objectively-checkable cases; manual-only applied 2026-07-02 to 2026-08-14
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-08-15T16:46:53.473Z
---

**Superseded 2026-08-14.** From 2026-07-02 to 2026-08-14, the QA agent/subagent (`agentes-ia-qa`) was instructed to never run or automate UI tests in a browser — only describe manual test steps. The user reversed this explicitly on 2026-08-14 after diagnosing that recurring functional bugs reaching client delivery traced back to this exact gap: neither the Implementador (by design) nor QA (by this now-reversed rule) ever executed the app, so verification depended entirely on manual human testing that wasn't always rigorous.

**Current rule (2026-08-14 onward):** QA **does** automate browser verification for objectively-checkable cases: items in `docs/qa/regresiones-manuales.yml` with `deteccion_qa.tipo: ui`, the pattern checks in `32-estandares-qa-implementador.instructions.md` (combo pre-population on Edit, state-machine-derived action buttons, DataTable 500 errors, sidebar-vs-authorization consistency, dynamic-form focus loss), and UI-verifiable acceptance criteria from the functional analysis. Manual testing is retained only for: production-credential-dependent cases (e.g., real ARCA/AFIP emission), subjective UX judgment, and business-data validation only the client can confirm. Full methodology in `.github/instructions/33-verificacion-automatizada-qa.instructions.md`. The Implementador still never smoke-tests (role separation preserved).

Also on 2026-08-14: both `agentes-ia-implementador` and `agentes-ia-qa` subagent definitions (`.claude/agents/*.md`) were given `model: opus` in frontmatter as the default model for all future projects — user's explicit choice to prioritize implementation/verification quality over speed/cost for these two Agent-mode roles, while Ask-mode roles (analista/diseñador/arquitecto/presupuestador) keep inheriting the session's default model (typically Sonnet).

**Why the original 2026-07-02 rule existed:** at the time, the user wanted to avoid the cost/reliability overhead of agent-driven browser automation. That tradeoff changed once a concrete pattern of client-facing functional bugs was traced back to this gap — reliability now outweighs the original cost/speed concern for this specific pair of roles.

**How to apply:** if a future QA agent run reverts to only describing manual steps for a case that's in the automatable scope above, that's a regression from the 2026-08-14 policy — flag it. Related: [[project-agentes-ia]].
