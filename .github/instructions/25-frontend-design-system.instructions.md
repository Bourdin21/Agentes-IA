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

# Ortografia y acentuacion en texto de UI (obligatorio, vigente Agosto 2026)

Pedido explicito de Joaquin (proyecto La Platense, 2026-08-10): ningun texto visible para el usuario final o el cliente puede tener errores de ortografia ni tildes faltantes/incorrectas. Aplica a **todo texto en espanol que ve una persona real**, no solo al cuerpo de las vistas Razor:

- Vistas `.cshtml`: titulos (`ViewData["Title"]`), labels, texto de botones, placeholders, texto de ayuda, encabezados de tabla, breadcrumbs.
- ViewModels (`Web/Models/*.cs`): `[Display(Name="...")]`, mensajes de `[Required(ErrorMessage="...")]`/`[StringLength(...)]`/etc. (ver `23-web.instructions.md`, seccion ViewModels).
- Mensajes de SweetAlert2, `TempData["SuccessMessage"]`/`TempData["ErrorMessage"]`, toasts.
- JS embebido con strings de UI (validaciones client-side, tooltips, textos de DataTables custom).
- Sidebar (`Views/Shared/_Layout.cshtml`), documentacion de alcance para cliente (etapa Documentacion, `07-documentacion.prompt.md`).

**No aplica** a este propio repositorio de instrucciones/prompts de Agentes-IA (`.github/**/*.instructions.md`, `.github/**/*.prompt.md`, `docs/**/*.md`) — esos archivos son documentacion tecnica interna del estudio, no texto de UI que vea un cliente final, y mantienen la convencion sin tildes ya usada historicamente para evitar problemas de encoding en el propio tooling.

**Errores tipicos a vigilar especialmente** (frecuentes en texto generado, por ser palabras que en el uso cotidiano informal a veces se escriben sin tilde): "gestión" (no "gestion"), "código" (no "codigo"), "categoría" (no "categoria"), "número" (no "numero"), "período" (no "periodo"), "administración" (no "administracion"), "descripción" (no "descripcion"), "configuración" (no "configuracion"), "atención" (no "atencion"), "días" (no "dias"), "además" (no "ademas"), "también" (no "tambien"), "según" (no "segun"), "único" (no "unico"), "válido"/"validación" (no "valido"/"validacion").

**Como aplicarlo:**
- Antes de dar por cerrada una vista o ViewModel nuevo/modificado, releer cada string visible al usuario y verificar tildes segun las reglas de acentuacion del espanol (no solo las palabras de la lista de arriba, esa es solo la lista de riesgo mas comun).
- Si hay duda sobre una palabra especifica, preferir la forma acentuada correcta de diccionario antes que la version mas comun en texto informal.
- El agente QA (`06-pruebas.prompt.md`) incluye una revision de ortografia/acentuacion como parte de su chequeo de UI, no solo funcionalidad — un texto con tilde faltante es un defecto reportable aunque el flujo funcional sea correcto.
- Este criterio es un estandar de desarrollo para todas las implementaciones futuras (no una decision puntual por proyecto).

# Listados: DataTables + filtros por columna (obligatorio, vigente Julio 2026)

- Todo listado de una entidad se renderiza con DataTables server-side (ver `23-web.instructions.md`, `DataTableRequest`/`DataTableResponse<T>`) — nunca una tabla HTML estatica ni paginacion manual armada a mano.
- Regla de filtros: **cada columna visible en el listado define un filtro disponible para el usuario.** Si el listado muestra una columna (estado, fecha, categoria, responsable, monto, etc.), tiene que existir un control de filtro equivalente que actue sobre esa columna en el server-side de DataTables — el usuario tiene que poder filtrar por cualquier dato que ve en la grilla.
- No agregar una columna al listado sin su filtro correspondiente, y no agregar un filtro que no corresponda a una columna visible (evitar filtros "ocultos" sin columna asociada), salvo un buscador de texto libre global explicitamente justificado.
- Filtros de columnas de fecha usan daterangepicker (rango), nunca dos inputs de fecha sueltos sin el componente.
- Filtros de columnas de catalogo/enum usan select (Select2 si la lista es larga o requiere autocomplete), no texto libre.
- Este criterio es un estandar de desarrollo para todas las implementaciones futuras (no una decision puntual por proyecto).
