---
name: design-system
description: Design system Olvidata para vistas MVC (DataTables con filtro por columna, Select2, SweetAlert2, maskMoney, tema oscuro, formularios, ortografia de UI). Usar al crear o modificar cualquier vista Razor, CSS o JS del front.
paths:
  - "**/Views/**/*.cshtml"
  - "**/wwwroot/**/*.css"
  - "**/wwwroot/**/*.js"
---

# Design system (vistas MVC)

Fuente completa: `.github/instructions/25-frontend-design-system.instructions.md`. Ubicar la seccion con `grep -n "^# \|^## " .github/instructions/25-frontend-design-system.instructions.md` y leer solo esa.

## Reglas que se verifican en QA

- **Listados**: DataTables server-side. **Cada columna visible tiene su filtro**; la busqueda global matchea importes y fechas; filtros persistidos en `Session` y boton "Limpiar filtros" que tambien los borra de `Session`.
- **Bajas dentro de un listado**: endpoint devuelve JSON, baja por AJAX, refresco con `tabla.ajax.reload(null, false)` — el `false` mantiene la pagina.
- **Combos**: Select2 en TODO select, con foco automatico en el buscador al abrir.
- **Importes**: maskMoney (nunca `type=number`), sin salto de linea entre signo y numero, ordenables por valor.
- **Formularios**: encabezado con titulo y descripcion, ancho acotado, campos agrupados en cards, obligatorios marcados, barra de acciones sticky, `autofocus` en el primer campo.
- **Texto**: tildes correctas en TODO lo visible (labels, botones, mensajes, validaciones).
- **Tema oscuro**: tokens `--ov-*` redefinidos por `[data-theme="dark"]`, nunca duplicar reglas de componente.

## Indice de la fuente

`python scripts/contexto.py indice 25` lista sus secciones con el numero de linea: leer solo la que aplica (`sed -n '<desde>,<hasta>p'`), nunca el archivo completo (`39-presupuesto-contexto.instructions.md`).
