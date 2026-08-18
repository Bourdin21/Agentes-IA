---
description: Reglas de frontend y design system Olvidata para vistas MVC.
applyTo: "**/Web/**/*.{cshtml,css,js}"
---

# Librerias UI
- Bootstrap 5 (override en olvidata-theme.css)
- Font Awesome 6.5.1 — **self-hosted** desde `wwwroot/lib/fontawesome/` (vigente Agosto 2026, ver seccion "Fuentes e iconos self-hosted" abajo), no CDN
- jQuery local
- SweetAlert2 (CDN — no auto-hosteado, ver nota abajo)
- DataTables 1.13.8 + Bootstrap 5 theme (CDN)
- Select2 + Bootstrap 5 theme (CDN)
- DateRangePicker + Moment.js (CDN)

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

# Importes monetarios: sin salto de linea (obligatorio, vigente Agosto 2026)

Bug detectado en KOI (2026-08-12): en celdas de tabla angostas, el espacio HTML normal entre el signo ("$", "U$D") y el numero permite que el navegador corte la linea justo ahi, dejando el signo solo en una fila y el numero en la siguiente. Reproducido en varias pantallas (Dashboard, Mi Inversion, Reparto General) porque el codigo arma el importe concatenando el simbolo a mano (`$ @Helper.FormatMonto(v)`) sin ninguna regla CSS que lo proteja.

- Toda celda de tabla que muestre un importe monetario (signo + numero, cualquier moneda) debe tener una clase CSS con `white-space: nowrap` desde el arranque del proyecto (parte del design system base, `olvidata-theme.css`), no como parche reactivo por pantalla.
- Nombre de clase sugerido: `.ov-monto` (o equivalente del proyecto) aplicada explicitamente en el `<td>`/`<span>` del importe — no un selector generico por posicion de columna, para no romper el wrap de columnas de texto largo que si deben poder cortar linea.
- Si el proyecto ya tiene un helper de formato de moneda (`FormatoMoneda`, `MoneyHelper`, etc.), evaluar que la clase forme parte del propio helper (ej. un metodo que devuelva el HTML completo con el `<span class="ov-monto">`) en vez de depender de que cada vista se acuerde de aplicarla a mano.
- Este criterio es un estandar de desarrollo para todas las implementaciones futuras (no una decision puntual por proyecto) — mismo patron que el fix de tema oscuro de KOI (Etapa 9), que tambien paso de bug puntual a regla del design system compartido.

# Fuentes e iconos self-hosted (obligatorio, vigente Agosto 2026)

Aplicado sobre el template `blankproject` (repo base de todo proyecto nuevo) a partir de la actualizacion visual de olvidata.com.ar (Astro 4→7, fuentes self-hosted, iconos SVG en vez de CDN — "cero requests a CDNs externos"). Portado al baseline MVC con el mismo objetivo, adaptado a lo que es seguro y de bajo riesgo en un stack server-rendered con Bootstrap 5 + jQuery (no se adopto inline-SVG-por-icono ni un router client-side — ver justificacion abajo).

- **Inter (400/500/600/700)** self-hosted en `wwwroot/fonts/inter/*.woff2`, declarado via `@font-face` en `wwwroot/css/fonts.css` (linkeado antes de `olvidata-theme.css` en `_Layout.cshtml`). Reemplaza el `<link>` a `fonts.googleapis.com` + los `preconnect` — cero requests a Google Fonts.
- **Font Awesome 6.5.1** self-hosted en `wwwroot/lib/fontawesome/` (css + webfonts woff2 de solid/regular/brands, sin los .ttf de fallback ni v4compatibility — no se usan en el baseline). Reemplaza el `<link>` a `cdnjs.cloudflare.com`. Ningun `<i class="fas fa-...">` existente cambia de markup — es un swap de origen del archivo, no un cambio de icono.
- **Por que NO se migro a iconos SVG inline (a diferencia de olvidata.com.ar):** requeriria curar y verificar visualmente cada glyph usado (con el riesgo de mapear mal un alias FA5→FA6 sin poder confirmar el render), y tocar cada uso de `<i class="fas fa-X">` en todas las vistas de todo proyecto derivado del template. Self-hostear el paquete FA6 completo logra el mismo objetivo ("cero CDN externo") sin ese riesgo ni ese esfuerzo. Si un proyecto puntual necesita reducir aun mas el peso de assets, evaluar iconos SVG inline ahi como decision de ese proyecto, no como cambio de baseline.
- **SweetAlert2 / DataTables / Select2 / daterangepicker+Moment siguen via CDN** — no entraron en este alcance (son librerias de interaccion mas pesadas, self-hostearlas requiere gestion de version via libman u otro mecanismo, no es parte de la actualizacion de fuentes/iconos). Evaluar aparte si se vuelve prioridad.
- **GSAP / animaciones de scroll / fondo animado en canvas — deliberadamente NO portado.** Esos patrones de olvidata.com.ar son apropiados para un sitio de marketing; en pantallas de carga de datos y listados (el grueso de lo que se construye sobre este baseline) suman peso JS y ruido visual sin aportar valor — la app ya tiene microinteracciones sutiles en CSS puro (`.ov-card:hover`, `.ov-stat-card:hover { transform: translateY(-2px) }`, `.btn-ov-primary:hover { transform: translateY(-1px) }`) que cubren el nivel de polish apropiado para este tipo de sistema.

# Tema oscuro (dark/light toggle) — obligatorio en todo proyecto nuevo (vigente Agosto 2026)

Portado desde `la-platense` (Ferreteria La Platense, en produccion real) al template `blankproject`, tras detectar que el template base no tenia el toggle de tema aunque ya proyectos derivados si lo habian construido — ver `docs/patrones/catalogo.yml` PAT-009.

- Preferencia persistida por usuario en `PreferenciaUsuario` (1:1 con `ApplicationUser`, campo `TemaOscuro`) + cookie `crm-tema` (para que el SSR renderice el tema correcto antes de que el JS corra).
- `<html data-theme="@(Context.Request.Cookies["crm-tema"] ?? "light")">` en `_Layout.cshtml`; toda la paleta oscura se define como override de tokens CSS via `[data-theme="dark"]` en `olvidata-theme.css` — nunca duplicar reglas de componente, solo redefinir `--ov-*`.
- Boton de toggle en el topbar (icono sol/luna), `POST /Account/ToggleTema` (`[Authorize][ValidateAntiForgeryToken]`) actualiza la DB y renueva la cookie; el JS hace `location.reload()` tras el toggle (no solo cambia el atributo en vivo) para que todo — incluidos componentes que fijan color una sola vez al crearse (ej. Chart.js si el proyecto lo usa) — se re-renderice ya con el tema correcto desde el SSR.
- El login tambien aplica la preferencia guardada seteando la cookie `crm-tema` al autenticar (no solo el toggle la setea).
- Requiere `@inject Microsoft.AspNetCore.Antiforgery.IAntiforgery _antiForgery` + `<meta name="csrf-token" content="@_antiForgery.GetAndStoreTokens(Context).RequestToken" />` en el layout para que el fetch del toggle pueda mandar el token.
- Este criterio es un estandar de desarrollo para todas las implementaciones futuras — el template ya lo trae, no hay que reconstruirlo por proyecto.

# Listados: DataTables + filtros por columna (obligatorio, vigente Julio 2026)

- Todo listado de una entidad se renderiza con DataTables server-side (ver `23-web.instructions.md`, `DataTableRequest`/`DataTableResponse<T>`) — nunca una tabla HTML estatica ni paginacion manual armada a mano.
- Regla de filtros: **cada columna visible en el listado define un filtro disponible para el usuario.** Si el listado muestra una columna (estado, fecha, categoria, responsable, monto, etc.), tiene que existir un control de filtro equivalente que actue sobre esa columna en el server-side de DataTables — el usuario tiene que poder filtrar por cualquier dato que ve en la grilla.
- No agregar una columna al listado sin su filtro correspondiente, y no agregar un filtro que no corresponda a una columna visible (evitar filtros "ocultos" sin columna asociada), salvo un buscador de texto libre global explicitamente justificado.
- Filtros de columnas de fecha usan daterangepicker (rango), nunca dos inputs de fecha sueltos sin el componente.
- Filtros de columnas de catalogo/enum usan select (Select2 si la lista es larga o requiere autocomplete), no texto libre.
- Este criterio es un estandar de desarrollo para todas las implementaciones futuras (no una decision puntual por proyecto).
