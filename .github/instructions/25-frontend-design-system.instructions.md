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
- Filtros de columnas de fecha usan daterangepicker (rango), nunca dos inputs de fecha sueltos sin el componente. El formato que produce (`dd/MM/yyyy - dd/MM/yyyy`) es el mismo que debe esperar el parseo de fecha de la búsqueda global (regla siguiente) — un solo convenio de fecha por pantalla, no dos.
- Filtros de columnas de catalogo/enum usan select con Select2 aplicado (ver regla general de combos mas abajo), no texto libre.
- **Búsqueda global (el "Search" propio del DataTable) matchea contra CUALQUIER columna visible, incluidas las de importe/moneda y las de fecha — no solo texto.** Un usuario que tipea "1500" tiene que encontrar filas con "$ 1.500,00"; uno que tipea "15/03/2026" tiene que encontrar la fila de esa fecha. Implementación de referencia real (proyecto delicias-naturales):
  - Importes: probar el texto ingresado como candidato decimal tanto en formato es-AR ("837.441,39") como invariante ("837441.39") — decidir cuál separador es el decimal según cuál aparece último en el texto — y comparar con `>= valor-0.005 && < valor+0.005` (no `==` exacto, por redondeo). Además, probar como substring numérico del importe (para que "500" encuentre también "$ 1.500,00"). Ver `Helper/BusquedaHelper.ParsearImportes` en delicias-naturales.
  - Fechas: probar el texto contra los formatos de fecha usados en pantalla (`dd/MM/yyyy` y variantes sin cero inicial) con `DateTime.TryParseExact`, comparando `Year`/`Month`/`Day` por separado — nunca el `DateTime` completo (falla por la hora). Ver el bloque de búsqueda por fecha en `Controllers/VentasController.ListarVentas` (delicias-naturales).
  - Patrón general: EF no resuelve bien un único `OR` gigante mezclando texto + número + fecha sobre columnas de tipos distintos en la misma expresión. Resolver cada tipo de dato por separado contra una lista de ids candidatos (`extraIds`), y combinar al final con `WHERE textoEnColumnaTexto OR Id IN (extraIds)` — mismo patrón que `VentasController.ListarVentas` en delicias-naturales.
- **Persistencia de filtros en sesión:** después de cada búsqueda/listado, guardar los valores de los filtros usados en `Session` (una key por filtro, prefijada con el nombre de la entidad — ej. `Session["Productos_CategoriaId"]`), y al volver a cargar la pantalla reponerlos como valor inicial de cada control — el usuario no debe perder sus filtros al navegar a otra pantalla y volver. Ver `ProductosController.Index` en delicias-naturales (guarda los filtros en `Session` en cada carga y los repone la próxima vez).
- **Botón "Limpiar filtros" obligatorio** en todo bloque de filtros: vacía todos los controles visibles Y borra los mismos valores guardados en `Session` — si no se borran de `Session`, reaparecen la próxima vez que se entra a la pantalla, contradiciendo lo que el usuario acaba de pedir. Ya era convención de facto (`#btnLimpiar` en varias pantallas de la-platense); pasa a ser obligatorio, no opcional.
- Este criterio es un estandar de desarrollo para todas las implementaciones futuras (no una decision puntual por proyecto).

# Combos: Select2 en TODO select/select-multiple + foco automatico al abrir (obligatorio, vigente Agosto 2026)

- **Todo `<select>` y `<select multiple>` de la aplicacion usa Select2 — no solo los que necesitan busqueda/autocomplete o listas largas.** Amplia la regla previa (antes acotada a "lista larga o requiere autocomplete"): un select de 2-3 opciones tambien lleva Select2, por consistencia visual y de interaccion en toda la app. Implementacion de referencia (la-platense): en vez de llamar `.select2(...)` a mano en cada vista, un auto-init global en `site.js` aplica Select2 a TODO `<select>` de la pagina que no lo tenga ya (`$('select').not('[data-select2-manual]').not('.select2-hidden-accessible').each(...)`) — cualquier select nuevo que se agregue despues queda cubierto sin que nadie tenga que acordarse de inicializarlo. Los combos que se inicializan a mano en su propia vista (autocomplete AJAX con `ajax: {...}`, por ejemplo) llevan el atributo `data-select2-manual` en el `<select>` para que el auto-init global los salte — si no, el auto-init "vacio" corre primero (site.js carga antes que el `@@section Scripts` de la vista) y pisa la configuracion real.
- **Al abrir CUALQUIER combo Select2 (click, teclado, o programatico), el foco tiene que quedar en el input de busqueda automaticamente**, para que el usuario pueda empezar a escribir sin un segundo click. Select2 no lo garantiza por su cuenta en todos los navegadores/casos (issue conocido de la libreria). Se resuelve una sola vez, de forma global (no por vista), escuchando el evento `select2:open`:
  ```js
  $(document).on('select2:open', function () {
      document.querySelector('.select2-container--open .select2-search__field')?.focus();
  });
  ```
  El selector busca el `.select2-container--open` (unico en el DOM en ese instante) en vez del `<select>` que disparo el evento, porque este handler es global y no conoce cual combo lo abrio.
- Ambas reglas se verifican en un navegador real antes de dar el cambio por terminado (no alcanza con revisar el codigo): confirmar que un `<select>` simple recibe la clase `select2-hidden-accessible`, que un combo AJAX ya inicializado a mano sigue funcionando (no se rompe por el auto-init global), y que hacer click en cualquier combo deja el foco en `.select2-search__field`.

## Bajas (individuales o en lote) dentro de un listado DataTables: siempre AJAX, nunca form-submit (obligatorio, vigente Agosto 2026)

Bug real reportado por un cliente en producción (la-platense, ver `docs/patrones/catalogo.yml` `PAT-015`): la acción "Eliminar" de un listado hacía `submit` de un `<form>` dinámico contra el endpoint de baja, lo que provoca una recarga completa de página — si el usuario estaba en una página distinta de la 1 del DataTable, la recarga siempre lo devolvía a la página 1, perdiendo su lugar en el listado.

- El endpoint de baja (individual y en lote) **devuelve JSON** (`{ success, message }`), nunca un `RedirectToAction`.
- El JS confirma con SweetAlert2, hace la baja por `$.post`/`$.ajax` (no `<form>.submit()`), y al confirmar éxito refresca la grilla con `tabla.ajax.reload(null, false)` — **el segundo argumento `false` es lo que mantiene la página actual**; sin él (o con `tabla.ajax.reload()` a secas) el DataTable vuelve a la página 1 igual que con un form-submit.
- Selección múltiple (checkbox por fila + "seleccionar todos" acotado a la página visible) + baja en lote: un solo endpoint que reciba la lista de ids y aplique la baja con una sola operación masiva (`ExecuteUpdateAsync` sobre el `Where(ids.Contains(...))`, no un loop de N llamadas individuales al service).
- Implementación de referencia completa (Controller + Service + vista): `FerreteriaLaPlatense.Web/Controllers/ProductosController.cs` (`Delete`, `EliminarLote`), `FerreteriaLaPlatense.Infrastructure/Services/ProductoService.cs` (`EliminarLoteAsync`), `FerreteriaLaPlatense.Web/Views/Productos/Index.cshtml` — proyecto la-platense.
- Este criterio es un estandar de desarrollo para todas las implementaciones futuras — cualquier listado DataTables con acción de baja debe seguir este patrón desde el arranque, no esperar a que un cliente lo reporte como bug.

## Formularios de alta / edicion / detalle: diseño grafico obligatorio, no solo campos funcionales (obligatorio, vigente Septiembre 2026)

Pedido explicito de Joaquin (2026-09-03, la-platense): "definir una regla nueva en implementacion que tenga en cuenta el diseño grafico a la hora de crear formularios". El problema real: las pantallas de alta/edicion nacian funcionalmente correctas pero visualmente crudas — un `<h3>` suelto, los campos estirados de punta a punta en un monitor ancho, el boton Guardar perdido al final de un scroll largo, y ningun indicio de que campo es obligatorio ni por que existe un campo raro.

**Una pantalla de formulario no esta terminada cuando guarda bien: esta terminada cuando ademas se entiende y se ve como el resto del sistema.** Checklist obligatorio para toda pantalla de alta, edicion y detalle:

1. **Encabezado de pantalla, nunca un `<h3>` suelto.** Titulo + una linea de descripcion que explique para que sirve la pantalla, y a la derecha las acciones de navegacion (Volver, y accion secundaria si aplica). Clases: `.ov-page-head`, `.ov-page-head__title`, `.ov-page-head__desc`, `.ov-page-head__actions`.
2. **Ancho de lectura acotado.** Un formulario estirado a 2500px en un monitor ancho deja los labels a la izquierda y los inputs perdidos a la derecha. Envolver en `.ov-form-page` (max 1080px) o `.ov-form-page--wide` (max 1500px, solo si la pantalla tiene grillas internas tipo carrito de venta).
3. **Campos agrupados en `card` con header e icono**, por bloque semantico ("Datos del cliente", "Datos fiscales", "Datos adicionales (opcionales)"). Nunca 15 inputs sueltos uno abajo del otro.
4. **Grid responsive real** (`row g-3` + `col-md-*`/`col-lg-*` por campo), con anchos proporcionales al dato: un CUIT no ocupa lo mismo que un nombre, y un campo de notas va a `col-12`.
5. **Campos obligatorios marcados visualmente** con `.ov-required` en el `<label>` (no alcanza con que falle la validacion al enviar).
6. **Texto de ayuda (`.ov-field-hint`) en todo campo cuyo efecto no sea obvio** — que formato espera, que consecuencia tiene, cuando dejarlo vacio. Ej. "Dejar vacio para Consumidor Final".
7. **Barra de acciones sticky (`.ov-form-actions`)** al pie del formulario: accion primaria primero, `Cancelar`/`Volver` como `btn-outline-secondary`, y las acciones destructivas separadas a la derecha con `.ov-form-actions__spacer`. En un formulario largo el boton Guardar tiene que estar siempre a la vista.
8. **`autofocus` en el primer campo editable** de una pantalla de alta.
9. **Pantallas de Detalle (solo lectura) usan `.ov-detail-grid`** con pares `.ov-detail-item__label` / `.ov-detail-item__value` — no una tabla de 2 columnas improvisada por pantalla, y no dejar una celda en blanco cuando no hay dato: usar `.ov-detail-item__value--empty` con un texto explicito ("Sin nota", "No informado").
10. **Validacion visible arriba**: `asp-validation-summary="ModelOnly"` renderizado como `alert alert-danger` (no como un `<div class="text-danger">` suelto que se pierde), mas el `asp-validation-for` de cada campo.

Las clases `.ov-*` de arriba viven en `wwwroot/css/site.css` del proyecto (implementacion de referencia completa: la-platense, seccion "Sistema de formularios"). Copiarlas al arrancar un proyecto nuevo — no reinventar el naming por proyecto.

**Verificacion**: igual que la regla de combos, el resultado se mira en un navegador real antes de darlo por terminado — al menos una pantalla de alta, una de edicion y una de detalle, en ancho de escritorio y en mobile.
