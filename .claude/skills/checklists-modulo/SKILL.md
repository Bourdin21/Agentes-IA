---
name: checklists-modulo
description: Checklists de salida por tipo de trabajo (entidad nueva, servicio, workflow con estados, reporte, integracion externa, modificacion sobre modulo existente) con su smoke-check automatizado de QA. Usar al cerrar una implementacion, antes de dar por terminado.
paths:
  - "**/*.cs"
  - "**/*.cshtml"
---

# Checklists por tipo de modulo

Fuente: `.github/instructions/26-checklists.instructions.md` (corto, ~10 KB: se puede leer entero si hace falta).

Elegi el checklist que corresponde:

- **Entidad nueva** — 13 pasos, de Domain a migracion y sidebar. Ojo con el 10a (DataTable + filtro por columna + Session), 10b (combos precargados en Editar), 10b-bis (toda propiedad de negocio editable en Crear y Editar) y 10c (baja por AJAX).
- **Servicio nuevo** — interfaz en Application, implementacion en Infrastructure, registro Scoped.
- **Workflow con estados** — enum en Domain, transiciones en el Service, guardas antes de persistir, ViewModel con las acciones validas del estado actual.
- **Reporte o exportacion** — DTO sin exponer entidades, consulta sin N+1, un filtro por columna visible, permiso explicito.
- **Integracion externa** — contrato en Application, timeouts y reintentos, logging sin secretos, casos OK / error / timeout.
- **Modificacion sobre modulo existente** — el paso 6 es el que mas se olvida: si cambias el modelo de datos, greppear TODOS los sitios que ya leen ese campo (LP-002).

Cada checklist cierra con su **smoke-check automatizado** para QA (ver `33-verificacion-automatizada-qa.instructions.md`).
