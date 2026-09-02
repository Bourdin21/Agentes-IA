---
name: docs-locations
description: Where project documentation and QA plans live in the repo
metadata: 
  node_type: memory
  type: reference
  originSessionId: 11114fe4-9ddd-4d2a-b493-b6fa9769b26d
  modified: 2026-07-22T17:02:57.898Z
---

- `docs/ganaderia/definiciones/5-implementador.md` — memoria acumulativa cronológica de etapas de implementación (alcance, capas tocadas, migraciones EF, riesgos). Leer para conocer el estado más reciente del modelo antes de tocar código — es más actual que este archivo de memoria.
- `docs/ganaderia/manual-usuario.md` — manual de usuario funcional completo (todos los módulos, flujos, FAQ), útil para entender comportamiento esperado desde la perspectiva del cliente final.
- `docs/qa/plan-qa-etapa7.md` — plan de QA integral por módulo (Catálogos, Stock, Facturas, Cuotas, Caja, Egresos, Dashboard) con checklist de casos.
- `README.md` (raíz) — documentación de la plantilla base `BlankProject` de Olvidata Soft (arquitectura en capas, convenciones de nomenclatura, funcionalidades transversales: auditoría, soft delete, notificaciones, exportación, emails). Ganaderia se construyó sobre esta plantilla.
- `migration-prod-*.sql` en la raíz — scripts de migración aplicados manualmente en producción (ej. `migration-prod-20260702-1822.sql` para `EgresoPago_PagosMultiples`).

Ver [[project-overview]].
