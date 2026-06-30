# Memoria QA — KoiDumplings
# Última actualización: 2026-06-29 16:31

## Estado del sistema
- Build: PASS (0 errores, 4 warnings NuGet moderados — MailKit/MimeKit 4.14.x)
- EF migrations: sin cambios pendientes (last: AgregarCanalesMostradoPedidosYCantVentas)
- DB: actualizada y en sincronía con el modelo

## Refactor KPI / Canales de venta (sesión actual)
- VentasADelivery/VentasBDelivery → VentasAPedidos/VentasBPedidos + VentasAMostrador/VentasBMostrador + CantidadVentas
- Migración aplicada manualmente (renombrado + nuevas columnas)
- Dashboard, Indicadores, Mensual.cshtml, SeedData — todos actualizados
- Sin referencias residuales de "Delivery" en vistas activas (solo en migrations históricas)

## Bugs detectados — pendientes de fix

### KOI-001 [critical] — RESUELTO ✅
- Botones eliminar (btn-swal-confirm fuera del form) no ejecutaban delete
- Fix verificado: data-form + form oculto con AntiForgeryToken en Rubros, Parametros, Subgrupos
- Handler JS en site.js: data-form-id || data-form → form.submit()

### KOI-002 [major] — PENDIENTE ❌
- Falta botón y acción ExportarAnualExcel en Vista Anual ER
- No existe botón en Anual.cshtml ni acción en EstadoResultadosController
- Fix: agregar botón + acción GET con IExportService

### KOI-003 [major] — RESUELTO ✅
- Inversor no veía link 'Vista Anual ER' en sidebar
- Fix verificado: link presente en bloque @if (User.IsInRole("Inversor")) en _Layout.cshtml (líneas 176-179)

### KOI-004 [major] — RESUELTO ✅
- Consumos podían superar bruto sin validación bloqueante
- Fix verificado en PreviewCierre.cshtml: JS bloquea submit si consumo > bruto (línea 193-198)
- Fix verificado en EstadoResultadosService.cs: CerrarPeriodoAsync valida consumos <= bruto (líneas 260-267)

### KOI-005 [blocker] — NUEVO — PENDIENTE ❌
- CamarasController NO existe pero el sidebar referencia Camaras/Ver (todos los roles) y Camaras/Index (Admin)
- Las vistas Ver.cshtml, Index.cshtml, Create.cshtml, Edit.cshtml existen
- ICamaraService, CamaraService, CamaraNotificacionViewModels, ConfiguracionCamaraDto existen
- Impacto: cualquier usuario autenticado que haga click en "Cámaras" obtiene 404/500
- Fix: implementar CamarasController con acciones Ver, Index, Create, Edit, Delete

### KOI-006 [major] — NUEVO — PENDIENTE ❌
- NotificacionesConfigController NO existe pero el sidebar lo referencia (Admin/SuperUsuario)
- No existen vistas para ese controller
- El link en sidebar posiblemente era para configuración SMTP/email (SystemController ya tiene esa función)
- Fix: determinar si es un módulo pendiente o si el link en sidebar debe apuntar a SystemController
- Riesgo: Admin hace click en "Notificaciones" → 404

### KOI-007 [major] — NUEVO — PENDIENTE ❌
- Users/Index usa paginación manual Razor (no DataTables) — mezcla con el convenio del proyecto
- Tiene filtros por rol/estado/search procesados server-side via GET
- Riesgo: si la cantidad de usuarios crece, la paginación manual puede romper UX
- Acción recomendada: migrar a DataTables client-side (carga todos los usuarios vía Razor) dado que el volumen es bajo

### KOI-008 [minor] — NUEVO — PENDIENTE ❌
- TipoCambio/Index tiene id="tablaCotizaciones" pero no se inicializa como DataTable
- Tabla pequeña (~2-5 casas), posiblemente intencional
- No afecta funcionalidad; solo inconsistencia de convención
- Acción: revisar con equipo si debe inicializarse como DataTable

## Vulnerabilidades NuGet
- MailKit 4.14.1 → disponible 4.17.0 (GHSA-9j88-vvj5-vhgr, moderada)
- MimeKit 4.14.0 → disponible 4.17.0 (GHSA-g7hc-96xr-gvvx, moderada)
- Impacto: email (SMTP). No afecta datos ni autenticación.
- Acción: actualizar antes de release a producción

## Máquina de estados verificada

### EstadoPeriodo (PeriodoMensual)
- Abierto → Cerrado: vía CerrarPeriodoAsync (solo Admin/SuperUsuario)
- Cerrado → X: NO existe reapertura de periodo (correcto según spec P-A04)
- Guardar ventas/conceptos bloqueado si periodo Cerrado ✅
- Validación consumos > bruto bloqueante ✅

### EstadoLiquidacion
- Pendiente → Pagada: vía MarcarPagadasAsync (solo liquidaciones en estado Pendiente) ✅
- Pagada → Pendiente: vía ReabrirAsync (requiere motivo, solo Admin/SuperUsuario) ✅
- Guard: ReabrirAsync solo acepta liquidaciones en estado Pagada ✅

### EstadoUsuario
- Bloqueado: AccountController.Login verifica Estado == Bloqueado → mensaje "cuenta bloqueada" ✅

## Permisos verificados
- SuperUsuario: acceso total (System, Audit, ImportacionInicial, Users, Config, ER, Dashboard, Indicadores, Liquidaciones, Notif)
- Administrador: Config, ER, TipoCambio, Liquidaciones, Puntos, RepartoGeneral, Dashboard, Indicadores, Users (solo Inversores), Notif
- Inversor: Dashboard, MiInversion, Vista Anual ER
- Aislamiento Inversor: MiInversionController verifica que inversorId == userId del usuario logueado ✅
- RepartoGeneralController: solo RequireAdministracion ✅
- LiquidacionesController: solo RequireAdministracion ✅

## Backlogs anteriores aún pendientes
- Export Excel P-04 (KOI-002)
- CamarasController (KOI-005) — blocker
- NotificacionesConfigController (KOI-006) — major

## Checklist de liberación
- [x] Build verde
- [x] EF sin cambios pendientes
- [x] Soft-delete correcto en todas las entidades
- [x] Anti-forgery en todos los POST destructivos
- [x] KOI-001 resuelto
- [x] KOI-003 resuelto
- [x] KOI-004 resuelto
- [ ] KOI-002 — Export Excel ER Anual
- [ ] KOI-005 — CamarasController faltante (BLOCKER para producción)
- [ ] KOI-006 — NotificacionesConfigController faltante
- [ ] KOI-007 — Users/Index DataTables
- [ ] KOI-008 — TipoCambio/Index DataTables (minor)
- [ ] Actualizar MailKit/MimeKit a 4.17.0
