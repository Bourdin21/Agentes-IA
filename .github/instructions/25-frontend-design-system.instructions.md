---
description: Reglas de frontend y design system Olvidata para vistas MVC.
applyTo: "**/Web/**/*.{cshtml,css,js}"
---

# Librerias UI
- Bootstrap 5 (override en olvidata-theme.css)
- Font Awesome 6.5.1
- jQuery local
- SweetAlert2
- DataTables 1.13.8 + Bootstrap 5 theme
- Select2 + Bootstrap 5 theme
- DateRangePicker + Moment.js

# Tokens visuales clave
- Primary: #2b9de4
- Primary hover: #1f8ad0
- Background: #f0f4f8
- Sidebar gradient: #0c1222 -> #0f172a

# Convenciones
- Prefijo CSS: ov-
- BEM-like: ov-sidebar-link, ov-topbar-avatar, ov-brand-icon-img
- Tablas siempre dentro de div.table-responsive

# Archivos CSS
- olvidata-theme.css: tokens, layout, componentes, overrides.
- site.css: ajustes especificos del proyecto.

# Estructura de pantallas — criterio de diseñador grafico senior (obligatorio, vigente Julio 2026)

Toda vista nueva se disena aplicando criterio de diseñador grafico senior, no solo funcional:

- Jerarquia visual clara: titulo de pantalla + contexto (breadcrumb o subtitulo) arriba, acciones primarias diferenciadas de las secundarias (botones outline/ghost para secundarias, solidos para la accion principal).
- Agrupacion logica de campos relacionados (cards/fieldsets con encabezado propio), nunca un formulario plano con todos los campos al mismo nivel cuando hay mas de ~8 campos.
- Orden de lectura predecible: arriba->abajo, izquierda->derecha, priorizando lo que el usuario necesita decidir/completar primero.
- Espaciado y alineacion consistentes via grid de Bootstrap — nunca tablas HTML usadas como mecanismo de layout.
- Acciones destructivas o irreversibles (eliminar, anular, rechazar) siempre visualmente diferenciadas de las acciones neutras (color de alerta, icono distinto, confirmacion SweetAlert2 obligatoria).
- Prueba de aceptacion de diseño antes de dar por cerrada una vista: un usuario que nunca vio el sistema tiene que poder entender que hacer en esa pantalla sin instrucciones externas. Si no es evidente, reordenar/agrupar/renombrar antes de continuar.
- Este criterio es un estandar de desarrollo para todas las implementaciones futuras (no una decision puntual por proyecto) — aplica al implementador en toda vista Razor nueva o modificada.

# Listados: DataTables + filtros por columna (obligatorio, vigente Julio 2026)

- Todo listado de una entidad se renderiza con DataTables server-side (ver `23-web.instructions.md`, `DataTableRequest`/`DataTableResponse<T>`) — nunca una tabla HTML estatica ni paginacion manual armada a mano.
- Regla de filtros: **cada columna visible en el listado define un filtro disponible para el usuario.** Si el listado muestra una columna (estado, fecha, categoria, responsable, monto, etc.), tiene que existir un control de filtro equivalente que actue sobre esa columna en el server-side de DataTables — el usuario tiene que poder filtrar por cualquier dato que ve en la grilla.
- No agregar una columna al listado sin su filtro correspondiente, y no agregar un filtro que no corresponda a una columna visible (evitar filtros "ocultos" sin columna asociada), salvo un buscador de texto libre global explicitamente justificado.
- Filtros de columnas de fecha usan daterangepicker (rango), nunca dos inputs de fecha sueltos sin el componente.
- Filtros de columnas de catalogo/enum usan select (Select2 si la lista es larga o requiere autocomplete), no texto libre.
- Este criterio es un estandar de desarrollo para todas las implementaciones futuras (no una decision puntual por proyecto).
