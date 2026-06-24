# Memoria Acumulativa — Implementador KOI

## Última actualización
2026-07 — E6 completada (Inversiones). E1-E6 OK.

## Estado actual
🟡 **EN CURSO** — E1, E2 y E3 completadas · E4–E9 pendientes.

---

## 0. Escaneo de reutilización

| Componente | Proyecto origen | Decisión |
|---|---|---|
| `CotizacionService` / `ICotizacionService` | VirtualWallet (`C:\Sistemas\virtualwallet`) | ✅ Reutilizado en E2 — copiado y adaptado a ns KOI |
| `UsersController` base | KoiDumplings template | ✅ Extendido con InversorId |
| `EmailService` / `IEmailService` | KoiDumplings template | ✅ Base para NotificacionService KOI (E8) |
| `IExportService` / `ExportService` | KoiDumplings template | ✅ Export anual (E3) |
| `SeedData` | KoiDumplings template | ✅ Extendido con RolInversor + seed catálogos (E2) |

---

## Etapas completadas

### E1 — Base (2026-07)

**Capas afectadas:** Domain · Infrastructure · Web

#### Domain
- `Inversor` : SoftDestroyable — Nombre(200), CapitalAportadoUsd(decimal 18,2), nav Usuarios
- `PreferenciaUsuario` : SoftDestroyable — UserId(string FK → ApplicationUser UNIQUE), TemaOscuro(bool)
- `ApplicationUser` — agregado `InversorId` (int?, FK → Inversor, SetNull) + nav `Inversor?`

#### Infrastructure
- `AppDbContext`: `DbSet<Inversor>`, `DbSet<PreferenciaUsuario>`, Fluent API + FK ApplicationUser.InversorId
- `SeedData`: `RolInversor = "Inversor"`, incluido en seed de roles
- Migración: `E1_BaseKOI`

#### Web
- `Program.cs`: policies `SoloAdministrador`, `ConsultaDashboard`, `MiInversion`
- `UsersController`: policy → `SoloAdministrador`; roles asignables por rol del creador; InversorId en Create/Edit
- `AccountController`: `ToggleTema` POST; cookie `koi-tema` en login
- `UserViewModels`: InversorId + NombreInversor + AvailableInversores
- `_Layout.cshtml`: brand "KOI", sidebar KOI por rol, dark/light toggle, Chart.js CDN, CSRF meta
- `olvidata-theme.css`: dark theme tokens `[data-theme="dark"]`
- `Views/Users/Create` y `Edit`: InversorId dropdown (visible cuando Rol = Inversor)

---

### E2 — Configuración y Períodos (2026-07)

**Capas afectadas:** Domain · Application · Infrastructure · Web

#### Domain (entidades nuevas)
- `Rubro` : SoftDestroyable — Nombre(150), Orden, nav Subgrupos
- `Subgrupo` : SoftDestroyable — RubroId(FK Restrict), Nombre(150), TipoConcepto(enum), Orden
- `ParametroPorcentaje` : SoftDestroyable — SubgrupoId(FK Restrict), Anio, Mes, Porcentaje(8,4), Observaciones(500). Índice único (SubgrupoId, Anio, Mes)
- `PeriodoMensual` : SoftDestroyable — Anio, Mes, EstadoPeriodo(enum), TipoCambio(18,4), FechaCierre, MontoAjuste(18,2), MotivoAjuste(500), Observaciones(1000). Índice único (Anio, Mes). NombrePeriodo computed
- `EstadoPeriodo` enum: Abierto(1) / Cerrado(2) — P-A04: sin Reabierto
- `TipoConcepto` enum: Manual(1) / PorcentajeVentasA(2) / PorcentajeVentasTotales(3)

#### Application
- `ICotizacionService` — contrato adaptado de VirtualWallet; tipos `CotizacionDia`, `CotizacionPorCasa`

#### Infrastructure
- `CotizacionService` — implementación adaptada de VirtualWallet; cache estático thread-safe; ArgentinaDatos (histórico) + DolarApi (hoy); `ObtenerPromedioBlue` como default P-A03
- `AppDbContext`: DbSets Rubros, Subgrupos, ParametrosPorcentaje, PeriodosMensuales + Fluent API completa
- `SeedData`: método `SeedRubrosAsync` — 6 rubros + 19 subgrupos + parámetros base 2024-01
- Migración: `E2_ConfiguracionYPeriodos`

#### Web
- `Program.cs`: named HttpClients `ArgentinaDatos` + `DolarApi`; `ICotizacionService` registrado como Singleton
- `ConfiguracionController` — Rubros CRUD + Subgrupos CRUD + Parámetros CRUD; policy `SoloAdministrador`
- `TipoCambioController` — Index (GET, tabla cotizaciones + form TC); Guardar (POST); RefrescarCotizaciones (AJAX POST); crea PeriodoMensual si no existe
- `ConfiguracionViewModels.cs` — 7 ViewModels (RubroList/Form, SubgrupoList/Form, ParametroList/Form, TipoCambio)
- Vistas: `Views/Configuracion/` (Rubros, RubroCreate, RubroEdit, Subgrupos, SubgrupoCreate, SubgrupoEdit, Parametros, ParametroCreate, ParametroEdit) + `Views/TipoCambio/Index`
- `_Layout.cshtml`: sidebar → Configuración apunta a `Configuracion/Rubros`; agregado link `TipoCambio/Index`

## Archivos tocados E2

| Archivo | Motivo |
|---|---|
| `KoiDumplings.Domain/Enums/EstadoPeriodo.cs` | NUEVO |
| `KoiDumplings.Domain/Enums/TipoConcepto.cs` | NUEVO |
| `KoiDumplings.Domain/Entities/Rubro.cs` | NUEVO |
| `KoiDumplings.Domain/Entities/Subgrupo.cs` | NUEVO |
| `KoiDumplings.Domain/Entities/ParametroPorcentaje.cs` | NUEVO |
| `KoiDumplings.Domain/Entities/PeriodoMensual.cs` | NUEVO |
| `KoiDumplings.Application/Interfaces/ICotizacionService.cs` | NUEVO (reutilizado VW) |
| `KoiDumplings.Infrastructure/Services/CotizacionService.cs` | NUEVO (reutilizado VW) |
| `KoiDumplings.Infrastructure/Data/AppDbContext.cs` | 4 DbSets + Fluent API E2 |
| `KoiDumplings.Infrastructure/Data/SeedData.cs` | SeedRubrosAsync + using EF |
| `KoiDumplings.Web/Program.cs` | HttpClients + Singleton ICotizacionService |
| `KoiDumplings.Web/Models/ConfiguracionViewModels.cs` | NUEVO — 7 VMs |
| `KoiDumplings.Web/Controllers/ConfiguracionController.cs` | NUEVO |
| `KoiDumplings.Web/Controllers/TipoCambioController.cs` | NUEVO |
| `KoiDumplings.Web/Views/Configuracion/*.cshtml` | NUEVAS (9 vistas) |
| `KoiDumplings.Web/Views/TipoCambio/Index.cshtml` | NUEVA |
| `KoiDumplings.Web/Views/Shared/_Layout.cshtml` | Sidebar: Configuracion → Rubros, + TipoCambio |

## Supuestos E2
- `CotizacionService` registrado como Singleton; cache estático compartido entre requests.
- Si DolarApi no responde al inicio, `TipoCambioViewModel.CotizacionesHoy` puede estar vacío — UI muestra aviso.
- Parámetros de porcentaje siguen vigencia "desde el período X en adelante hasta el próximo registro": la lógica de búsqueda del parámetro vigente se implementa en E3 al calcular el ER.
- `PeriodoMensual` se crea en `TipoCambioController.Guardar` si no existe todavía; también puede crearse desde el ER (E3).
- Soft delete en ParametroPorcentaje y Subgrupo: el query filter global los excluye automáticamente; las consultas de E3 solo verán registros activos.

---


---

### E3 — Estado de Resultados (2026-07)

**Capas afectadas:** Domain · Application · Infrastructure · Web

#### Domain (entidades nuevas)
- `VentaMensual` : SoftDestroyable — PeriodoMensualId(FK 1:1, Cascade), VentasASalon/BSalon/ADelivery/BDelivery(18,2), CantidadComensales. Derivados: VentasA, VentasB, VentasTotales, VentasSalon, VentasDelivery (no persistidos).
- `ConceptoGasto` : SoftDestroyable — PeriodoMensualId(FK Cascade), SubgrupoId(FK Restrict), ImporteManual(18,2), ImporteCalculado(18,2?), PorcentajeAplicado(8,4?). Indice único (PeriodoMensualId, SubgrupoId).
- `Liquidacion` : SoftDestroyable — E6 anticipado. PeriodoMensualId/InversorId, montos bruto/consumos/neto/USD, EstadoLiquidacion(enum), FechaPago, MotivoReapertura.
- `AsignacionPuntos` : SoftDestroyable — E6 anticipado. InversorId, Puntos(8,2), VigenteDesdeAnio, VigenteDesdesMes.
- `EstadoLiquidacion` enum: Pendiente(1) / Pagada(2).

#### Application
- `IEstadoResultadosService` — contrato completo: ObtenerAsync, GuardarVentasAsync, GuardarConceptoGastoAsync, RecalcularPorcentualesAsync, GenerarPreviewCierreAsync, CerrarPeriodoAsync, ObtenerResumenAnualAsync.
- DTOs: GuardarVentasDto, CerrarPeriodoDto, EstadoResultadosDto, RubroErDto, ConceptoErDto, ConceptoCalculadoDto, ResumenPeriodoDto, PreviewCierreDto, InversorPreviewDto, CierreResultadoDto.

#### Infrastructure
- `EstadoResultadosService` — busca parametro vigente (anio/mes <= periodo), recalcula porcentuales en cascada al guardar ventas, genera liquidaciones al cerrar, extrae emails para notificacion.
- `AppDbContext`: DbSets VentasMensuales, ConceptosGasto, AsignacionPuntos, Liquidaciones + Fluent API completa.
- `DependencyInjection`: `AddScoped<IEstadoResultadosService, EstadoResultadosService>()`.
- Migracion: `E3_EstadoResultados` (pending).

#### Web
- `EstadoResultadosController` — Mensual(GET), GuardarVentas(POST AJAX), GuardarConcepto(POST AJAX), Recalcular(POST AJAX), Anual(GET), PreviewCierre(GET), ConfirmarCierre(POST).
- `EstadoResultadosViewModels.cs` — ErMensualViewModel, ErAnualViewModel, PreviewCierreViewModel.
- Vistas: `Views/EstadoResultados/Mensual.cshtml` (P-03), `Anual.cshtml` (P-04), `PreviewCierre.cshtml` (P-08).
- `_Layout.cshtml`: sidebar EstadoResultados → Mensual + link Vista Anual ER.

## Archivos tocados E3

| Archivo | Motivo |
|---|---|
| `KoiDumplings.Domain/Entities/VentaMensual.cs` | NUEVO |
| `KoiDumplings.Domain/Entities/ConceptoGasto.cs` | NUEVO |
| `KoiDumplings.Domain/Entities/Liquidacion.cs` | NUEVO (E6 anticipado) |
| `KoiDumplings.Domain/Entities/AsignacionPuntos.cs` | NUEVO (E6 anticipado) |
| `KoiDumplings.Domain/Enums/EstadoLiquidacion.cs` | NUEVO |
| `KoiDumplings.Application/Interfaces/IEstadoResultadosService.cs` | NUEVO — contrato + DTOs |
| `KoiDumplings.Infrastructure/Services/EstadoResultadosService.cs` | NUEVO |
| `KoiDumplings.Infrastructure/Data/AppDbContext.cs` | 4 DbSets nuevos + Fluent API E3/E6 |
| `KoiDumplings.Infrastructure/DependencyInjection.cs` | AddScoped EstadoResultadosService |
| `KoiDumplings.Web/Controllers/EstadoResultadosController.cs` | NUEVO |
| `KoiDumplings.Web/Models/EstadoResultadosViewModels.cs` | NUEVO |
| `KoiDumplings.Web/Views/EstadoResultados/Mensual.cshtml` | NUEVA |
| `KoiDumplings.Web/Views/EstadoResultados/Anual.cshtml` | NUEVA |
| `KoiDumplings.Web/Views/EstadoResultados/PreviewCierre.cshtml` | NUEVA |
| `KoiDumplings.Web/Views/Shared/_Layout.cshtml` | Sidebar: ER → Mensual + link Anual |

## Etapas pendientes

| Etapa | Módulos | Estado |
|---|---|---|
| E3 | Estado de Resultados (VentaMensual, ConceptoGasto, calc ER, vista anual, cierre) | ✅ |
| E4 | Indicadores de Venta | ⬜ |
| E5 | Dashboard (KPIs + gráficos + multi-año) | ⬜ |
| E6 | Inversiones: Puntos, Liquidaciones, Reparto General, Mi Inversión | ⬜ |
| E7 | Cámaras | ⬜ |
| E8 | Notificaciones de cierre (SMTP + plantilla + log) | ⬜ |
| E9 | Carga inicial históricos 2024–2026 | ⬜ |

## Próximos pasos E3
- Entidades: `VentaMensual` (PeriodoId, VentasA, VentasB, CantidadComensales, Delivery) + `ConceptoGasto` (PeriodoId, SubgrupoId, ImporteManual, ImporteCalculado)
- Lógica: `EstadoResultadosService` o cálculo en controller — busca parámetro vigente para subgrupos calculados
- Acción de cierre: valida TC cargado, genera notificación (E8), bloquea edición
- Vista anual: tabla de meses como columnas (similar a tabla pivote)
- Previsualización editable antes del cierre (P-A05)

---

### E3 — Estado de Resultados (2026-07)

**Capas afectadas:** Domain · Application · Infrastructure · Web

#### Domain (entidades nuevas)
- `VentaMensual` : SoftDestroyable — 4 campos ventas + CantidadComensales; derivados (VentasA, VentasTotales, VentasSalon, VentasDelivery) calculados al vuelo. Índice único PeriodoMensualId.
- `ConceptoGasto` : SoftDestroyable — PeriodoMensualId, SubgrupoId, ImporteManual, ImporteCalculado, PorcentajeAplicado. Índice único (PeriodoMensualId, SubgrupoId).
- `Liquidacion` : SoftDestroyable — PeriodoMensualId, InversorId, montos bruto/consumos/neto/TC, EstadoLiquidacion. Índice único (PeriodoMensualId, InversorId).
- `AsignacionPuntos` : SoftDestroyable — InversorId, Puntos, vigencia (Anio/Mes).
- `EstadoLiquidacion` enum: Pendiente(1) / Pagada(2).

#### Application
- `IEstadoResultadosService` — ObtenerAsync, GuardarVentasAsync, GuardarConceptoGastoAsync, RecalcularPorcentualesAsync, GenerarPreviewCierreAsync, CerrarPeriodoAsync, ObtenerResumenAnualAsync.
- DTOs completos: GuardarVentasDto, CerrarPeriodoDto, EstadoResultadosDto, RubroErDto, ConceptoErDto, ResumenPeriodoDto, PreviewCierreDto, InversorPreviewDto, CierreResultadoDto, ConceptoCalculadoDto.

#### Infrastructure
- `EstadoResultadosService` — implementa IEstadoResultadosService; recalculo porcentual con parámetro vigente (búsqueda ≤ anio/mes), cierre genera Liquidaciones y registra FechaCierre.
- `AppDbContext`: DbSets VentasMensuales, ConceptosGasto, AsignacionPuntos, Liquidaciones + Fluent API completa.
- `DependencyInjection`: IEstadoResultadosService registrado como Scoped.
- Migración: `E3_EstadoResultados`.

#### Web
- `EstadoResultadosController` — Index (P-03 carga), Anual (P-04), PreviewCierre (P-08 GET), ConfirmarCierre (P-08 POST), GuardarVentas (AJAX), GuardarConcepto (AJAX), RecalcularPorcentuales (AJAX), ExportarExcel (CSV stub).
- `EstadoResultadosViewModels.cs` — 8 ViewModels.
- Vistas: `Views/EstadoResultados/Index.cshtml` (carga + edición AJAX inline), `Anual.cshtml` (grilla 12 meses), `PreviewCierre.cshtml` (P-08 con consumos editables y SweetAlert2 confirmación).

## Archivos tocados E3

| Archivo | Motivo |
|---|---|
| `KoiDumplings.Domain/Enums/EstadoLiquidacion.cs` | NUEVO |
| `KoiDumplings.Domain/Entities/VentaMensual.cs` | NUEVO |
| `KoiDumplings.Domain/Entities/ConceptoGasto.cs` | NUEVO |
| `KoiDumplings.Domain/Entities/Liquidacion.cs` | NUEVO (E6 anticipado) |
| `KoiDumplings.Domain/Entities/AsignacionPuntos.cs` | NUEVO (E6 anticipado) |
| `KoiDumplings.Application/Interfaces/IEstadoResultadosService.cs` | NUEVO |
| `KoiDumplings.Infrastructure/Services/EstadoResultadosService.cs` | NUEVO |
| `KoiDumplings.Infrastructure/Data/AppDbContext.cs` | 4 DbSets E3/E6 + Fluent API |
| `KoiDumplings.Infrastructure/DependencyInjection.cs` | Registro IEstadoResultadosService |
| `KoiDumplings.Web/Models/EstadoResultadosViewModels.cs` | NUEVO — 8 VMs |
| `KoiDumplings.Web/Controllers/EstadoResultadosController.cs` | NUEVO |
| `KoiDumplings.Web/Views/EstadoResultados/Index.cshtml` | NUEVA |
| `KoiDumplings.Web/Views/EstadoResultados/Anual.cshtml` | NUEVA |
| `KoiDumplings.Web/Views/EstadoResultados/PreviewCierre.cshtml` | NUEVA |

## Supuestos E3
- ExportarExcel devuelve CSV (stub); Excel real con ClosedXML se implementa en E4/final.
- Notificación email post-cierre marcada con TODO E8; no bloquea el cierre (P-A04/R-A4).
- Liquidaciones y AsignacionPuntos anticipados en Domain/Infrastructure para que E3 compile sin dependencias rotas hacia E6.
- El recalculo de porcentuales se dispara automáticamente al guardar ventas (AJAX).

---

### E4 — Indicadores de Venta (2026-07)

**Capas:** Application / Infrastructure / Web. Sin migración EF.
- `IIndicadoresService` + `IndicadoresDtos.cs` (IndicadoresDto, PeriodoSelectorDto)
- `IndicadoresService` — calcula ticket A/B, cubierto, pct canal/tipo sobre VentaMensual
- `IndicadoresController` — Index(anio, mes); policy RequireAdministracion
- `IndicadoresViewModels.cs` — IndicadoresIndexViewModel
- `Views/Indicadores/Index.cshtml` — 6 cards KPI + 2 tablas desglose + 2 doughnut Chart.js

---

### E5 — Dashboard (2026-07)

**Capas:** Application / Infrastructure / Web. Sin migración EF.
- `IDashboardService` + `DashboardDtos.cs` (DashboardDto, DashboardRubroDto, DashboardHistoricoDto)
- `DashboardService` — ObtenerAsync, ObtenerHistoricoAsync, ObtenerPeriodosAsync; reutiliza PeriodoMensual + VentaMensual + ConceptosGasto
- `DashboardController` — Index(anio, mes) [Authorize]; Historico(meses) endpoint JSON para Chart.js
- `DashboardViewModels.cs` — DashboardIndexViewModel
- `Views/Dashboard/Index.cshtml` — selector período; 6 cards (Ventas, VentasA, Gastos, Resultado+rent, USD, CubiertoProm); tabla gastos por rubro; torta Canal (Salón/Delivery); torta Ventas vs Gastos; gráfico histórico multi-línea (12/24 meses) con fetch AJAX
- `HomeController.Index` redirige al Dashboard si el usuario está autenticado
- Build OK / arranque limpio confirmado


---

## E8 — Notificaciones de cierre mensual ✅
**Fecha:** 2026-06-18
**Capas:** Domain, Application, Infrastructure, Web

### Entidades
- EstadoEnvioNotificacion enum (Enviado=1, Fallido=2)
- RegistroEnvioNotificacion : SoftDestroyable (PeriodoMensualId, InversorId, Email, FechaEnvio, Estado, DetalleError)

### Application
- INotificacionCierreService: EnviarNotificacionCierreAsync, ObtenerHistorialAsync, ReenviarAsync, PeriodoTieneEnviosAsync
- DTO: NotificacionEnvioDto, ResumenEnvioDto en NotificacionCierreDtos.cs

### Infrastructure
- NotificacionCierreService: envío masivo con registro por inversor, HTML email branding KOI, forzar reenvío, historial

### Web
- NotificacionCierreController: Historial (GET), Reenviar (POST AJAX), EnviarCierre (POST interno)
- ViewModels: NotificacionHistorialViewModel, NotificacionEnvioRowViewModel
- Vistas: NotificacionCierre/Historial.cshtml (DataTables + SweetAlert2 reenvío)
- Sidebar: link "Envíos de cierre" (Admin)
- EstadoResultadosController.ConfirmarCierre → dispara envío masivo fire-and-forget al cerrar período

### Notas
- El envío es fire-and-forget: no bloquea el redirect de cierre. Errores se loguean con _logger.LogError.
- Reenvío individual desde historial vía AJAX + SweetAlert2.
- Email HTML con branding KOI (colores #2b9de4), grilla de KPIs del período + tabla de liquidación personal.
---

## E7 — Cámaras IP (Hik-Connect) ✅ IMPLEMENTADO REAL
**Fecha:** 2026-06-18  
**Capas:** Domain, Infrastructure, Web

### Entidades
- ConfiguracionCamara : SoftDestroyable (UrlWebClient, CuentaReferencia, Notas, Activo)

### Application
- ICamaraService en Application/Interfaces/ICamaraService.cs
- ConfiguracionCamaraDto en Application/DTOs/CamaraNotificacionDtos.cs

### Infrastructure
- CamaraService en Infrastructure/Services/CamaraService.cs
- Fluent API en AppDbContext: UrlWebClient 500, CuentaReferencia 200, Notas 2000 (alineado con migración E4)
- Registrado en DependencyInjection.cs como ICamaraService

### Web
- CamarasController: Ver (todos autenticados), Index/Create/Edit/Delete (Admin)
- ViewModels: CamaraConfigListViewModel, CamaraConfigFormViewModel
- Vistas: Camaras/Ver.cshtml, Index.cshtml, Create.cshtml, Edit.cshtml
- Sidebar: "Cámaras" → Camaras/Ver (todos); "Config. cámaras" → Camaras/Index (solo Admin)

### DB
- Sin nueva migración. Reutiliza tablas de E4_CamarasYNotificaciones (ya aplicada).
- Modelo alineado: dotnet ef migrations has-pending-model-changes → sin cambios.

---

## E8 — Notificaciones de cierre mensual ✅ IMPLEMENTADO REAL
**Fecha:** 2026-06-18  
**Capas:** Domain, Application, Infrastructure, Web

### Entidades
- EstadoEnvioNotificacion enum en Domain/Enums/ (Enviado=1, Fallido=2)
- RegistroEnvioNotificacion : SoftDestroyable (PeriodoMensualId, InversorId, Email, FechaEnvio, Estado, DetalleError)

### Application
- INotificacionCierreService: EnviarNotificacionCierreAsync, ReenviarAsync, ObtenerHistorialAsync, PeriodoTieneEnviosAsync
- DTOs: NotificacionEnvioDto, ResumenEnvioDto en Application/DTOs/CamaraNotificacionDtos.cs

### Infrastructure
- NotificacionCierreService: envío masivo fire-and-forget por inversor, HTML branding KOI, reenvío individual, historial
- Registrado en DependencyInjection.cs como INotificacionCierreService

### Web
- NotificacionCierreController: Index (historial + filtro período), Reenviar (POST AJAX), EnviarMasivo (POST)
- ViewModel: NotificacionCierreListViewModel
- Vista: NotificacionCierre/Index.cshtml (DataTables + filtro período + SweetAlert2 para confirmar envío)
- Sidebar: "Hist. notif. cierre" → NotificacionCierre/Index (Admin)

### Notas
- Envío masivo es fire-and-forget (Task.Run) — no bloquea cierre del período.
- Reenvío individual vía AJAX + SweetAlert2 question.
- Email HTML responsive con branding KOI (#2b9de4), tabla de liquidación personal con neto ARS/USD.
- Build OK / modelo alineado sin nueva migración.


---

## E9 — Carga inicial de históricos 2024–2026 ✅ IMPLEMENTADO REAL
**Fecha:** 2026-06-18  
**Capas:** Application, Infrastructure, Web

### Application
- IImportacionInicialService en Application/Interfaces/IImportacionInicialService.cs
  - ValidarAsync(Stream) — dry-run, sin persistir
  - ImportarAsync(Stream, userId) — transaccional idempotente
  - GenerarPlantillaAsync() — descarga XLSX con 6 hojas y fila ejemplo
- DTOs en Application/DTOs/ImportacionDtos.cs: ImportacionResultadoDto, ImportacionContadoresDto, filas por hoja

### Infrastructure
- ImportacionInicialService en Infrastructure/Services/ImportacionInicialService.cs
  - Lee XLSX con ClosedXML (6 hojas: Periodos, Ventas, Gastos, Inversores, Asignaciones, Liquidaciones)
  - Importa en orden: Inversores → Períodos → Ventas → Gastos → Asignaciones → Liquidaciones
  - Idempotente: registros existentes se omiten con advertencia (no error)
  - Transacción completa con rollback ante error
- Registrado en DependencyInjection.cs como IImportacionInicialService
- **Sin nueva migración** — usa entidades y tablas ya existentes

### Web
- ImportacionInicialController: Index (GET), DescargarPlantilla (GET), Validar (POST), Importar (POST)
- ViewModel: ImportacionInicialViewModel en Web/Models/
- Vista: ImportacionInicial/Index.cshtml (instrucciones, upload, resultado con contadores y advertencias)
- Sidebar: "Importación histórica" → ImportacionInicial/Index (solo SuperUsuario)

### Integración E8 completada
- EstadoResultadosController.ConfirmarCierre ahora inyecta INotificacionCierreService y dispara
  EnviarNotificacionCierreAsync(periodoId) como fire-and-forget (Task.Run) al cerrar el período.

### Notas
- IFormFile se convierte a MemoryStream en el controller antes de llamar al servicio (frontera capa Web/Infrastructure).
- Build OK / sin cambios de modelo EF.
