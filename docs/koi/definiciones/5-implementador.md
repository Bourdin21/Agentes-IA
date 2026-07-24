# Memoria Implementador — KoiDumplings
# Última actualización: 2026-07-13 (sesión actual)

## Módulos implementados

### Etapa 11 — Migraciones aplicadas en PRODUCCIÓN (sesión actual)
- Ver detalle completo en `trazabilidad.md` (entrada 2026-07-13, "migraciones aplicadas en PRODUCCIÓN"). Resumen: `dotnet ef database update` creó las 22 tablas en `db_a7251f_koidump` (site4now.net, estaba vacía — primer aprovisionamiento). Seed básico (roles/catálogo/SuperUsuario) y la migración histórica completa (misma plantilla validada en local) quedaron aplicados: 19 períodos, 373 gastos, 15 inversores, 16 asignaciones, 265 liquidaciones, capital USD 287.500 — idéntico a lo validado en local.
- **Nota operativa importante:** el hosting MySQL remoto cortó la conexión dos veces durante operaciones con muchas escrituras secuenciales chicas (el seed de catálogo, con un `SaveChangesAsync` por Rubro sin transacción envolvente, y el primer intento de import vía navegador). Si se vuelve a tocar esta base desde una herramienta con timeout corto, preferir sondeo directo a la base en vez de esperar la respuesta HTTP/navegación.
- SuperUsuario de producción quedó con las credenciales por defecto del código (decisión explícita del cliente) — pendiente cambiarlas antes de exponer el sitio públicamente.
- Sin cambios de código — solo despliegue de esquema (EF) y datos (mecanismo de importación ya existente).

### Etapa 10 — Migración histórica ejecutada en local
- Ver detalle completo en `trazabilidad.md` (entrada 2026-07-13, "migración histórica ejecutada"). Resumen: ambos Excel fuente transformados a la plantilla de `ImportacionInicialService` y cargados vía el endpoint real `/ImportacionInicial` (SuperUsuario), tras vaciar los datos de demo en la DB local. 19 períodos, 373 gastos, 15 inversores, 16 asignaciones, 265 liquidaciones — 0 advertencias. Total Gastos reconcilia al centavo contra el Excel en los 19 períodos; capital migrado = USD 287.500 (coincide con el análisis funcional).
- Sin cambios de código — solo datos, vía el mecanismo de importación ya existente.
- Ejecutado y validado en el **entorno local** únicamente (pendiente replicar en el entorno del cliente cuando corresponda).

### Etapa 9 — Fix sistémico tema oscuro
- Pedido del cliente: alinear el tema oscuro en la totalidad del sistema (no pantalla por pantalla) porque había elementos ilegibles.
- **Diagnóstico (Playwright headless contra la app corriendo local, login real + cookie `koi-tema=dark` para simular SSR fresco):**
  - **Causa raíz:** el proyecto usa Bootstrap **5.1.0** (no 5.3+), cuya `.table` fija `color: #212529` como literal — no vía variable CSS. El override existente `[data-theme="dark"] .table { --bs-table-color: ... }` seteaba una variable que Bootstrap 5.1 nunca lee, dejando el texto de **todas** las tablas/listados (DataTables incluidos) ilegible en oscuro en todo el sistema.
  - `.card-header`/`.card-footer` (y sus variantes `.ov-card-*`) usaban el token fijo `--ov-gray-50` (nunca redefinido en `[data-theme="dark"]`) → cabeceras de card blancas sobre fondo oscuro en toda la app.
  - Paginación de DataTables (`.page-link`, vía `dataTables.bootstrap5`) sin override de tema → botones "Anterior/Siguiente" blancos.
  - `#themeToggle` (botón, no link) sin `background:none` explícito → heredaba el fondo blanco por defecto del user-agent para `<button>`, visible como caja blanca en el topbar oscuro (bug independiente del tema, agravado en oscuro).
  - Alerts nativas de Bootstrap (`.alert-info/success/warning/danger`, usadas directo en varias vistas) sin override de tema.
  - Chart.js en sí NO tenía bug de renderizado (los `isDark` checks de cada vista funcionan bien en carga fresca), pero el toggle de tema es 100% client-side (solo cambia el atributo `data-theme`, sin reload) — los canvases ya creados quedan con los colores calculados en el load anterior hasta que el usuario navega a otra pantalla. Confirmado visualmente comparando toggle-en-vivo vs carga fresca con cookie ya seteada.
- **Fix aplicado (single-file, sin tocar vistas individuales):**
  - `KoiDumplings.Web/wwwroot/css/olvidata-theme.css`: dentro de `[data-theme="dark"]` se agregó `color: var(--ov-text)` directo en `.table`/`.table-light` (más `--bs-table-striped-color/--active-color/--hover-color`), override de `.card-header`/`.card-footer`/`.ov-card-header`/`.ov-card-footer` (fondo `rgba(255,255,255,.03)`), override de `.page-link`/`.page-item.active/.disabled` (paginación DataTables), y override de `.alert-info/success/warning/danger` + `.alert-link`. Fuera del bloque dark: `.ov-topbar-icon-btn` ahora fija `background:none; border:none` (fix general, no solo oscuro).
  - `Views/Shared/_Layout.cshtml`: el click de `#themeToggle` ya no togglea el atributo `data-theme` en vivo — espera la respuesta de `POST /Account/ToggleTema` (que ya persistía la cookie server-side) y hace `location.reload()`. Esto elimina de raíz toda la clase de bugs "toggle sin reload" (Chart.js con colores viejos, y cualquier futuro widget JS que lea el tema solo al cargar) sin necesitar un sistema de re-theming en vivo.
- **Validación:** recompilado (`dotnet build` OK) y verificado visualmente con Playwright headless (login real, click real en el botón de tema, screenshots antes/después) en Dashboard, Estado de Resultados Mensual, Vista Anual ER, Tipo de Cambio, Configuración/Rubros, Inversores — 0 errores de consola, todas las tablas/cards/paginación/alerts legibles en oscuro tanto en carga fresca como en toggle en vivo.
- **Sin migración EF** — cambio 100% de presentación (CSS + un handler JS).
- **Impacto cross-proyecto:** `olvidata-theme.css` es el design system compartido por todos los proyectos del estudio sobre el mismo blankproject base — si otro proyecto activo (ShowroomGriffin, vinosefue, virtualwallet, etc.) usa Bootstrap 5.1 con el mismo archivo de tema, probablemente tenga el mismo bug de tablas/card-headers en oscuro y valga la pena portar el mismo fix.

### Etapa 8 — Refactor UI/UX: fusión Dashboard + Indicadores
- Autorizado directamente por el cliente/dueño del estudio como refactor puntual de UI sobre dos pantallas ya aprobadas (sin ciclo completo Análisis→Diseño→Arquitectura→Presupuesto): sin entidades nuevas, sin migración EF, mismos DTOs/servicios reutilizados.
- **Escaneo de reutilización:** no aplica búsqueda cross-proyecto (no es una entidad/flujo nuevo) — el propio proyecto KOI ya tenía ambas piezas (`IIndicadoresService`/`IndicadoresService`/`IndicadoresDto` como fuente de verdad de KPIs de venta) y se reutilizaron tal cual desde `DashboardService`.
- **Cambio funcional:** pantallas `Dashboard` e `Indicadores` (KPIs de venta) se fusionan en una sola pantalla `Dashboard` con 3 secciones diferenciadas (Ventas / Gastos / Evolución Histórica) + hero de KPIs de resultado global (Ventas Totales, Total Gastos, Resultado, Resultado USD, Rentabilidad %). Todo el contenido —incluido el desglose Facturado(A)/Informal(B) antes solo-Admin— queda visible para todos los roles autenticados (Admin, SuperUsuario, Inversor) bajo `[Authorize]` simple.
- **Domain/Application:** `DashboardDto` (KoiDumplings.Application/DTOs/DashboardDtos.cs) se simplifica — se quitan los campos duplicados que ya calculaba `IndicadoresDto` (VentasA, VentasSalon, VentasPedidos, VentasMostrador, CantidadComensales, CantidadVentas, TicketPromedioA, TicketPromedio, CubiertoProm) y se agrega `public IndicadoresDto? Ventas { get; set; }` como fuente única para la sección "Ventas". Se mantienen los campos propios del hero (VentasTotales, TotalGastos, ResultadoEjercicio, Rentabilidad, TipoCambio, ResultadoUsd, TieneTipoCambio).
- **Infrastructure:** `DashboardService` (KoiDumplings.Infrastructure/Services/DashboardService.cs) inyecta `IIndicadoresService` y delega en él el cálculo de todos los KPIs de venta (`ObtenerAsync(anio, mes)` reutilizado tal cual); ya no recalcula manualmente ticket promedio, cubierto promedio, ventas por canal, etc. Solo conserva lógica propia: existencia de ventas del período (`AnyAsync`, no recalcula KPIs — solo determina `TieneDatos`), gastos por rubro, total de gastos, resultado del ejercicio, rentabilidad %, TC y resultado en USD. `DependencyInjection.cs` no requirió cambios (`IIndicadoresService` ya estaba registrado como Scoped).
- **Web:**
  - `Views/Dashboard/Index.cshtml` reescrita completa: header + selector (sin cambios), hero de 5 KPIs con el estilo de card de Indicadores (icon badge circular, `border-0 shadow-sm`), sección "Ventas" (todo el contenido de la ex-pantalla Indicadores: KPIs, torta canal + barras ticket, tabla desglose por canal, tabla A/B + torta + barras apiladas), sección "Gastos" (tabla Gastos por Rubro existente + nuevo gráfico de barras horizontales por rubro + torta Resultado-vs-Gastos reubicada desde el Dashboard viejo), sección "Evolución Histórica" (gráfico de líneas sin cambios funcionales, reubicado al cierre). Cada sección tiene encabezado diferenciado (icon badge + accent de color: azul=Ventas, rojo=Gastos, verde=Histórico).
  - `IndicadoresController.cs`, `Views/Indicadores/Index.cshtml` e `IndicadoresIndexViewModel` (en `IndicadoresViewModels.cs`) eliminados — sin otras referencias en el repo (verificado por grep antes de borrar).
  - `Views/Shared/_Layout.cshtml`: eliminado el link "Indicadores de Venta" del sidebar (sección "Gestión"). El link "Dashboard" ya era visible para todos los roles, sin cambios.
- **Permisos:** `DashboardController` sigue `[Authorize]` simple (Admin/SuperUsuario/Inversor), sin cambios. El contenido antes restringido a `RequireAdministracion` (Facturado vs Informal) ahora es visible para todos los roles autenticados dentro del Dashboard fusionado — cambio de negocio explícito del cliente, no un descuido de permisos. La policy `RequireAdministracion` sigue vigente y en uso en otros controllers (NotificacionCierre, RepartoGeneral, Liquidaciones, Puntos, Audit) — no se tocó.
- **Sin migración EF** — no se tocaron entidades de dominio ni `VentasMensuales`/`ConceptosGasto`.
- **Build:** `dotnet build` desde la raíz del repo → Compilación correcta, 0 errores (9 warnings preexistentes: NU1902 MailKit/MimeKit — ver VUL-001 pendiente — y CS0114 HomeController.StatusCode, ninguno introducido por este cambio).
- **No hay proyecto de tests automatizados en el repo** (`**/*Tests*.csproj` → sin resultados); validación queda a cargo de QA manual.

### Etapa 7 — ABM Inversores
- InversoresController.cs creado en KoiDumplings.Web/Controllers
- Acciones: Index, Create (GET/POST), Edit (GET/POST), Delete (POST, soft-delete vía IRepository<Inversor>)
- Guard en Delete: bloquea si el inversor tiene usuario vinculado (ApplicationUser.InversorId)
- ViewModels: InversorListViewModel, InversorListItemViewModel, InversorFormViewModel (en ConfiguracionViewModels.cs)
- Vistas: Views/Inversores/Index.cshtml, Create.cshtml, Edit.cshtml
- Sidebar: link 'Inversores' agregado en sección 'Inversiones' (antes de Puntos)
- Sin migración EF (entidad Inversor ya existía)
- Build: PASS

### Bugs resueltos en sesión anterior
- KOI-002: Export Excel ER Anual
- KOI-005: CamarasController
- KOI-006: Link Notificaciones → System

## Pendientes
- KOI-007: Users/Index DataTables
- KOI-008: TipoCambio/Index DataTable init
- VUL-001: MailKit/MimeKit → 4.17.0
