# Diseño Funcional — Sistema de Gestión Ganadera

Versión: **v1**
Agente: `2 - disenador-funcional`
Entrada: `docs/ganaderia/definiciones/1-analista-funcional.md` v10
Proyecto: BlankProject (ASP.NET Core **MVC**, .NET 10, EF Core 10, MySQL 8, Identity, Serilog)
Alcance: diseño **funcional implementable** (flujos, ViewModels, contratos de servicios, requerimientos de datos por pantalla). **No** incluye código.

---

## 0. Salida mínima del agente

### 0.1 Alcance funcional resumido

Se traduce el análisis funcional v10 a un diseño implementable en tres capas (Presentación MVC / Negocio Services / Datos EF Core) para los tres ejes del sistema (Ingresos, Egresos, Stock) + transversales (Caja, Dashboard, Novedades, Catálogos ABM). Se definen **26 pantallas**, **14 ViewModels principales**, **10 contratos de servicios de negocio** y los **requerimientos de datos por pantalla**. El diseño respeta la separación estricta de capas: los Controllers orquestan y delegan, los Services concentran las reglas, y el acceso a datos queda encapsulado en repositorios/DbContext.

### 0.2 Impacto técnico por capa

- **Presentación (Controllers + Views MVC)**: 11 áreas funcionales, ~26 vistas, ViewModels con DataAnnotations en español, validación cliente + servidor, filtros de autorización por rol (`[Authorize(Roles="Productor")]` / `[Authorize(Roles="SuperUsuario")]`), un `TempData`/`ViewBag` mínimo, layout con bandeja de novedades.
- **Negocio (Application/Services)**: 10 servicios con contratos explícitos (interfaces) que encapsulan reglas (ciclo de vida Venta/Factura/Cuota, cálculo IVA, generación de cuotas, matriz de transiciones, compensaciones, rechazo/regularización, numeración correlativa, job de acreditación, autocomplete normalizado, filtrado por ámbito). Controllers delegan; **cero lógica de negocio en Controllers**.
- **Datos (Domain + Infrastructure)**: 14 entidades bajo `Domain/Entities/Ganaderia`, snapshot `TasaImpuestoAplicada` en Factura, `Numero` correlativo en Factura, `MovimientoStock` con `TipoMovimientoStock.Inicial` y origen/destino nullables, `MovimientoCaja` con `Estado` y FK al documento de origen, comprobante almacenado fuera de DB (ruta relativa + metadata), baja lógica vía `SoftDestroyable`, índices para correlativo y búsquedas por fecha/estado.

### 0.3 Riesgos y supuestos

Riesgos heredados: R13, R16, R18, R20/R24, R22, R23. Nuevos del diseño:
- **RD1** Concurrencia en generación de correlativo de Factura (dos usuarios emiten simultáneamente).
- **RD2** Atomicidad en venta multi-grupo: descuento de stock + creación de movimientos + factura + cuotas debe ser transaccional.
- **RD3** Reversión consistente al rechazar una cuota acreditada (mutar estado del movimiento sin crear contra-asiento).
- **RD4** Tamaño/formato del comprobante validado en cliente y servidor (doble validación).
- **RD5** Idempotencia del job diario: clave natural por `(CuotaId, FechaEjecución)` para evitar reacreditaciones.

Supuestos: los del análisis v10 (S1–S30) + SD1 Identity provee `Productor` y `SuperUsuario` como roles; SD2 todo timestamp se persiste en UTC y se muestra en hora local Argentina; SD3 el almacenamiento de comprobantes es filesystem local en v1.

### 0.4 Pruebas mínimas requeridas

Se mantienen PF1–PF52 + PV1–PV12 del análisis. Se agregan pruebas de diseño de integración UI↔Service:
- **PD1** Controller de Venta delega al Service y no contiene lógica de cálculo.
- **PD2** Service de Factura genera correlativo único bajo concurrencia simulada.
- **PD3** ViewModel de Gasto valida tamaño del comprobante antes de enviar al servidor.
- **PD4** Service de Compensación rechaza par inválido según matriz y Controller devuelve error al ViewModel.
- **PD5** Service de Job es re-ejecutable sin duplicar movimientos.

### 0.5 Checklist de salida para merge

Ver **§10**.

---

## 1. Mapa de pantallas por módulo

### 1.1 Ingresos

| Pantalla | Ruta MVC | Acceso | Tipo |
|---|---|---|---|
| Listado de Ventas | `Ventas/Index` | Productor | Grilla con filtros |
| Detalle/Alta/Edición de Venta | `Ventas/Create`, `Ventas/Edit/{id}`, `Ventas/Details/{id}` | Productor | Formulario multi-línea |
| Listado de Facturas | `Facturas/Index` | Productor | Grilla |
| Alta/Edición de Factura | `Facturas/Create/{ventaId}`, `Facturas/Edit/{id}` | Productor | Formulario con cálculo IVA |
| Detalle de Factura + Cuotas | `Facturas/Details/{id}` | Productor | Vista de sólo lectura + acciones |
| Acción: Rechazar cuota | `Cuotas/Rechazar/{id}` (POST) | Productor | Confirmación |
| Acción: Regularizar cuota | `Cuotas/Regularizar/{id}` (POST) | Productor | Formulario Opción 3a/3b |

### 1.2 Egresos

| Pantalla | Ruta MVC | Acceso | Tipo |
|---|---|---|---|
| Listado de Gastos | `Gastos/Index` | Productor | Grilla |
| Alta/Edición de Gasto | `Gastos/Create`, `Gastos/Edit/{id}` | Productor | Formulario + upload + autocomplete |
| Detalle de Gasto | `Gastos/Details/{id}` | Productor | Sólo lectura + link comprobante |

### 1.3 Stock

| Pantalla | Ruta MVC | Acceso | Tipo |
|---|---|---|---|
| Stock actual (por Grupo, totalizado por Categoría) | `Stock/Index` | Productor | Grilla agrupada |
| Listado de Movimientos de Stock | `MovimientosStock/Index` | Productor | Grilla con filtros |
| Alta de Movimiento de Stock | `MovimientosStock/Create` | Productor | Formulario dinámico por tipo |
| Detalle de Movimiento de Stock | `MovimientosStock/Details/{id}` | Productor | Sólo lectura |

### 1.4 Caja / Cuenta Corriente

| Pantalla | Ruta MVC | Acceso | Tipo |
|---|---|---|---|
| Movimientos de Caja | `Caja/Index` | Productor | Grilla con filtros por estado/fecha/tipo |
| Detalle (navegación al documento origen) | `Caja/Details/{id}` | Productor | Sólo lectura con link |

### 1.5 Dashboard

| Pantalla | Ruta MVC | Acceso | Tipo |
|---|---|---|---|
| Dashboard anual mensualizado | `Dashboard/Index` | Productor | Selector año + filtros Categoría/Grupo |

### 1.6 Catálogos ABM

| Pantalla | Ruta MVC | Acceso | Tipo |
|---|---|---|---|
| ABM Grupo | `Grupos/Index,Create,Edit,Delete` | Productor | ABM con baja lógica (stock==0) |
| ABM Rubro | `Rubros/Index,Create,Edit,Delete` | Productor | ABM |
| ABM Proveedor | `Proveedores/Index,Create,Edit,Delete` | Productor | ABM con campo Ámbito |
| ABM Organismo intermediario | `Organismos/Index,Create,Edit,Delete` | Productor | ABM |
| ABM Usuarios Productor | `Usuarios/Index,Create,Edit,Delete,Reset` | **SuperUsuario** | ABM restringido |

### 1.7 Novedades

| Pantalla | Ruta MVC | Acceso | Tipo |
|---|---|---|---|
| Bandeja de novedades al iniciar sesión | `Novedades/Index` | Productor | Listado de acreditaciones del día |

---

## 2. Flujo de pantallas (casos de uso principales)

### 2.1 Registrar una Venta → Factura → Cuotas

```
Ventas/Create
  ├── Selecciona Motivo (Faena/Vacía/Enfermedad)
  ├── Agrega N líneas (Grupo + Cantidad)
  ├── [Submit] → VentaService.Crear(viewModel)
  │       └── valida stock por grupo, crea Venta + DetalleVenta + MovimientoStock (tipo Venta) por línea (transaccional)
  ├── Redirige a Facturas/Create/{ventaId}
Facturas/Create/{ventaId}
  ├── Ingresa Organismo intermediario, kilos totales, precio/kg, fecha, plazo (30/60/90), tasa IVA
  ├── Calcula en vivo: Total, TotalConImpuestos, Cuotas (N, importes, fechas)
  ├── [Submit] → FacturaService.Emitir(viewModel)
  │       ├── asigna Numero correlativo (F-000123) bajo bloqueo/secuencia
  │       ├── persiste TasaImpuestoAplicada (snapshot)
  │       └── genera N cuotas (Pendiente) con redondeo (última absorbe diferencia)
  └── Redirige a Facturas/Details/{id}
```

### 2.2 Editar Factura (si todas las cuotas están Pendientes)

```
Facturas/Edit/{id}
  ├── FacturaService.VerificarEditable(id)  →  bloquea si hay cuota Acreditada/Rechazada (PV5)
  ├── Formulario permite cambiar plazo, precio, fecha, etc. (NO la tasa: es histórica)
  ├── [Submit] → FacturaService.Actualizar(viewModel)
  │       └── si cambió plazo o monto → regenera cuotas (elimina pendientes y crea nuevas)
  └── Redirige a Details
```

### 2.3 Rechazo de cuota

```
Facturas/Details/{id}  → botón [Rechazar] por cuota
  └── POST Cuotas/Rechazar/{id}
		└── CuotaService.Rechazar(id)
			  ├── cuota → Rechazada (desde Pendiente o Acreditada; no desde Rechazada → PV8)
			  └── si existía MovimientoCaja Acreditado → muta a Pendiente (NO borra, NO contramovimiento)
```

### 2.4 Regularización (Opción 3a / 3b)

```
Facturas/Details/{id} → botón [Regularizar] sobre cuota Rechazada
  └── Cuotas/Regularizar/{id}  (formulario modal o página)
		├── Radio: [Error de carga (3a)] | [Cobro posterior (3b)]
		├── Si 3b: Fecha real + Forma de pago
		└── [Submit] → CuotaService.Regularizar(id, opcion, fechaReal?, formaPago?)
			  ├── 3a: cuota → Acreditada; movimiento original → Acreditado (fecha original)
			  └── 3b: cuota queda Rechazada; movimiento original queda Pendiente; crea MovimientoCaja nuevo (Acreditado, fecha real)
```

### 2.5 Alta de Movimiento de Stock (dinámico por tipo)

```
MovimientosStock/Create
  ├── Selector Tipo: Inicial | Nacimiento | Compra | Muerte | Compensación
  │   (el tipo Venta no se elige aquí; se crea automáticamente desde Venta)
  ├── Campos dinámicos:
  │     ├── Inicial/Nacimiento/Compra   → GrupoDestino + Cantidad
  │     ├── Muerte                       → GrupoOrigen + Cantidad
  │     └── Compensación                 → GrupoOrigen + GrupoDestino + Cantidad
  ├── Validación cliente (dinámica por tipo) + servidor
  └── [Submit] → MovimientoStockService.Registrar(viewModel)
		├── Inicial: rechaza si ya existe Inicial para el Grupo (PF50)
		├── Compensación: si categorías distintas → valida matriz (PF37); origen==destino → PV11
		├── Muerte/Venta/Compensación: valida stock suficiente en origen
		└── Persiste + actualiza stock (EF Core transaccional)
```

### 2.6 Alta de Gasto con comprobante

```
Gastos/Create
  ├── Fecha, Importe, Rubro (ddl), Concepto (input con autocomplete via AJAX → RubroService.SugerirConceptos)
  ├── Descripción, Proveedor (ddl filtrado por Ámbito=Egresos/Ambos vía ProveedorService.ListarParaEgresos)
  ├── Forma de pago (enum), Comprobante (file opcional, 5MB, PDF/JPG/PNG)
  ├── Validación cliente: extensión + tamaño
  └── [Submit] → GastoService.Crear(viewModel)
		├── valida extensión/tamaño servidor (PV4, PV9)
		├── persiste Gasto + copia archivo a storage (ruta relativa)
		└── crea MovimientoCaja egreso (Acreditado, inmediato)
```

### 2.7 Job diario de acreditación (no es pantalla; se consume en Novedades)

```
IHostedService → AcreditacionJob (diario)
  └── AcreditacionService.Ejecutar(fecha)
		├── obtiene cuotas Pendientes con Vencimiento <= hoy que no tengan MovimientoCaja Acreditado (idempotencia)
		├── por cada una: cuota → Acreditada + crea MovimientoCaja Acreditado
		└── registra resumen en Novedades (persistente por día) para mostrar en bandeja
Login → Novedades/Index si hay novedades del día sin leer
```

### 2.8 Autorización

- Todas las pantallas operativas: `[Authorize(Roles="Productor,SuperUsuario")]`.
- `Usuarios/*`: `[Authorize(Roles="SuperUsuario")]` (PF13, PF24, PF25).

---

## 3. ViewModels (capa Presentación)

> Todos los VM residen en `Web/Models/ViewModels/Ganaderia/`. Validación con DataAnnotations en español.

### 3.1 VentaViewModel
- `Motivo` (enum, requerido)
- `Fecha` (requerido, ≤ hoy)
- `Lineas: List<LineaVentaViewModel>` (mín. 1)
  - `GrupoId` (requerido)
  - `Cantidad` (> 0)
- **Validaciones**: suma de cantidades por grupo ≤ stock actual del grupo (servidor, delegada a `VentaService`).

### 3.2 FacturaViewModel
- `VentaId` (requerido, read-only en edición)
- `OrganismoIntermediarioId` (requerido)
- `Categoria` (derivada o seleccionable según UI)
- `KilosTotales` (> 0)
- `PesoPromedio` (calculado read-only = Kilos/Unidades)
- `PrecioPorKg` (> 0)
- `Total` (calculado read-only)
- `TasaImpuesto` (enum; default IVA21; **read-only en edición**)
- `TotalConImpuestos` (calculado read-only)
- `Fecha` (requerido)
- `PlazoDias` (30/60/90)
- `Numero` (read-only; asignado por el sistema en alta)
- `Cuotas: List<CuotaPreviewViewModel>` (preview calculada, no editable)

### 3.3 CuotaPreviewViewModel
- `NumeroCuota` (1..N)
- `FechaVencimiento`
- `Importe`

### 3.4 CuotaAccionViewModel (rechazo / regularización)
- `CuotaId`
- `Opcion` (enum: `Rechazar`, `Regularizar3a`, `Regularizar3b`)
- `FechaReal` (requerido si 3b)
- `FormaDePago` (requerido si 3b)

### 3.5 GastoViewModel
- `Fecha` (≤ hoy)
- `Importe` (> 0)
- `RubroId` (requerido)
- `Concepto` (string, requerido, 200 chars, con autocomplete)
- `Descripcion` (string, opcional)
- `ProveedorId` (requerido, filtrado por ámbito)
- `FormaDePago` (enum)
- `Comprobante: IFormFile?` (opcional, 5MB, `.pdf/.jpg/.jpeg/.png`)

### 3.6 MovimientoStockViewModel
- `Tipo` (enum `TipoMovimientoStock` excepto `Venta`)
- `GrupoOrigenId` (nullable; requerido si Muerte/Compensación)
- `GrupoDestinoId` (nullable; requerido si Inicial/Nacimiento/Compra/Compensación)
- `Cantidad` (> 0)
- `Fecha` (≤ hoy)
- `Observaciones` (opcional)

### 3.7 GrupoViewModel (ABM)
- `Nombre` (requerido, único por categoría)
- `Categoria` (enum requerido)
- `StockMinimo` (≥ 0)
- `Activo` (bool)

### 3.8 RubroViewModel (ABM)
- `Nombre` (requerido, único)
- `Activo` (bool)

### 3.9 ProveedorViewModel (ABM)
- `RazonSocial` (requerido)
- `Cuit` (requerido, formato AR)
- `Contacto` (opcional)
- `Ambito` (enum)
- `Activo` (bool)

### 3.10 OrganismoIntermediarioViewModel (ABM)
- `RazonSocial` (requerido)
- `Cuit` (requerido)
- `Contacto` (opcional)
- `Activo` (bool)

### 3.11 UsuarioProductorViewModel (ABM — solo SuperUsuario)
- `UserName`, `Email`, `Password` (alta), `Activo`, `Rol` (fijo `Productor` en este ABM)

### 3.12 DashboardFiltroViewModel
- `Anio` (actual / anterior)
- `CategoriaFiltro` (nullable)
- `GrupoFiltro` (nullable)

### 3.13 DashboardResultadoViewModel
- `IngresosPorMes[12]`, `EgresosPorMes[12]`, `SaldoAcumulado[12]`
- `ComparativoAnioAnterior` (bool)
- Placeholder para indicadores de fase 2.

### 3.14 NovedadViewModel
- `Fecha`, `Titulo`, `Detalle`, `LinkOrigen`, `Leida`.

---

## 4. Contratos de servicios (capa Negocio)

> Residen en `Application/Services/Ganaderia/` con interfaces en `Application/Abstractions/Ganaderia/`. Controllers **sólo invocan servicios** y mapean VM↔DTO/Entity.

### 4.1 IVentaService
- `Task<Resultado<int>> CrearAsync(VentaViewModel vm, string userId)`
- `Task<Resultado> ActualizarAsync(int id, VentaViewModel vm, string userId)`
- `Task<Resultado> AnularAsync(int id, string userId)` — bloquea si tiene Factura (PF2)
- `Task<VentaDetalleDto> ObtenerAsync(int id)`
- `Task<IReadOnlyList<VentaListadoDto>> ListarAsync(FiltroVentas filtro)`

### 4.2 IFacturaService
- `Task<Resultado<string>> EmitirAsync(FacturaViewModel vm, string userId)` — devuelve `Numero` asignado (`F-000123`)
- `Task<Resultado> ActualizarAsync(int id, FacturaViewModel vm, string userId)` — valida PF20/PF21
- `Task<bool> EsEditableAsync(int id)`
- `Task<FacturaDetalleDto> ObtenerConCuotasAsync(int id)`
- **Internos**: `CalcularTotalesAsync`, `GenerarCuotasAsync`, `RegenerarCuotasAsync`, `AsignarNumeroCorrelativoAsync` (bajo lock/secuencia; RD1).

### 4.3 ICuotaService
- `Task<Resultado> RechazarAsync(int cuotaId, string userId)` — PF9, PV8
- `Task<Resultado> RegularizarAsync(int cuotaId, OpcionRegularizacion opcion, DateTime? fechaReal, FormaDePago? formaPago, string userId)` — PF45, PF46

### 4.4 IGastoService
- `Task<Resultado<int>> CrearAsync(GastoViewModel vm, string userId)` — valida comprobante, persiste archivo, crea MovCaja
- `Task<Resultado> ActualizarAsync(int id, GastoViewModel vm, string userId)`
- `Task<Resultado> AnularAsync(int id, string userId)` — revierte MovCaja (política a confirmar con analista si se requiere; v1: no se anulan gastos con movimiento acreditado de forma automática)
- `Task<IReadOnlyList<string>> SugerirConceptosAsync(string prefijo, string userId)` — autocomplete normalizado (trim + case-insensitive, distinct histórico)

### 4.5 IMovimientoStockService
- `Task<Resultado<int>> RegistrarAsync(MovimientoStockViewModel vm, string userId)` — aplica reglas PF28–PF38, PF49–PF50, PV11, PV12
- `Task<IReadOnlyList<MovimientoStockDto>> ListarAsync(FiltroMovimientosStock filtro)`
- **Internos**: `ValidarInicialUnicoAsync(grupoId)`, `ValidarMatrizTransicionAsync(origen, destino)`, `ValidarStockSuficienteAsync(grupoId, cantidad)`.

### 4.6 IStockQueryService (consulta)
- `Task<IReadOnlyList<StockPorGrupoDto>> ObtenerStockActualAsync()` — derivado desde movimientos
- `Task<IReadOnlyList<StockPorCategoriaDto>> ObtenerTotalesPorCategoriaAsync()`
- `Task<bool> TieneStockAsync(int grupoId)` — usado por baja lógica (PF33)

### 4.7 ICajaService
- `Task<IReadOnlyList<MovimientoCajaDto>> ListarAsync(FiltroCaja filtro)`
- `Task<decimal> ObtenerSaldoAsync()` — Σ movimientos Acreditados
- `Task<MovimientoCajaDetalleDto> ObtenerConOrigenAsync(int id)` — incluye navegación al documento origen

### 4.8 IDashboardService
- `Task<DashboardResultadoViewModel> CalcularAsync(DashboardFiltroViewModel filtro)`

### 4.9 IAcreditacionJobService (invocado por `IHostedService`)
- `Task<ResumenAcreditacionDto> EjecutarDiariaAsync(DateTime fecha)` — idempotente (RD5); genera entradas en `Novedades`
- **Clave de idempotencia**: `(CuotaId)` ya resuelta por la invariante "no existe movimiento Acreditado asociado" (PF17, PV6).

### 4.10 ICatalogoService (genérico por entidad: Grupo, Rubro, Proveedor, Organismo)
- `Task<Resultado<int>> CrearAsync(TViewModel vm)`
- `Task<Resultado> ActualizarAsync(int id, TViewModel vm)`
- `Task<Resultado> DarDeBajaAsync(int id)` — en Grupo exige `stock == 0` (PF33, PF39)
- `Task<IReadOnlyList<TDto>> ListarActivosAsync()`
- Para Proveedor: `Task<IReadOnlyList<ProveedorDto>> ListarPorAmbitoAsync(AmbitoProveedor ambito)` (PF41, PF42).

### 4.11 IUsuarioProductorService (solo SuperUsuario)
- `CrearAsync`, `ActualizarAsync`, `ActivarDesactivarAsync`, `ResetPasswordAsync`, `ListarAsync`
- Valida **máximo 5 activos** con rol `Productor`.

### 4.12 INovedadesService
- `Task<IReadOnlyList<NovedadViewModel>> ObtenerDelDiaAsync(string userId, DateTime fecha)`
- `Task MarcarLeidasAsync(IEnumerable<int> ids, string userId)`

---

## 5. Requerimientos de datos por pantalla

| Pantalla | Lectura requerida | Escritura |
|---|---|---|
| Ventas/Index | Ventas + estado factura (agregado) | — |
| Ventas/Create | Grupos activos con stock > 0 | Venta + DetalleVenta + MovimientoStock×N (tx) |
| Facturas/Create | Venta + Organismos activos + tasas vigentes | Factura + N Cuotas + asigna `Numero` |
| Facturas/Details | Factura + Cuotas + Movimientos de Caja vinculados | — |
| Cuotas/Rechazar | Cuota + MovCaja asociado | Muta Cuota + MovCaja |
| Cuotas/Regularizar | Cuota + MovCaja | Muta Cuota / MovCaja y/o crea nuevo MovCaja |
| Gastos/Create | Rubros activos + Proveedores con ámbito Egresos/Ambos + historial Conceptos del usuario | Gasto + archivo comprobante + MovCaja |
| MovimientosStock/Create | Grupos activos + stock por grupo | MovimientoStock (+ ajuste de stock derivado) |
| Stock/Index | Movimientos agregados por Grupo → stock actual; Grupos activos | — |
| Caja/Index | MovimientosCaja + joins a origen (Cuota/Gasto) | — |
| Dashboard/Index | MovimientosCaja + MovimientosStock + filtros | — |
| Grupos/* | Grupo + stock actual (para validar baja) | Grupo (baja lógica) |
| Rubros/* | Rubro | Rubro |
| Proveedores/* | Proveedor | Proveedor |
| Organismos/* | OrganismoIntermediario | OrganismoIntermediario |
| Usuarios/* (Super) | AspNetUsers + roles | AspNetUsers |
| Novedades/Index | Novedad (tabla persistente) por usuario/día | Marca `Leida` |

---

## 6. Impacto técnico por capa (resumen fino)

### 6.1 Presentación
- 11 carpetas de Controllers: `VentasController`, `FacturasController`, `CuotasController`, `GastosController`, `StockController`, `MovimientosStockController`, `CajaController`, `DashboardController`, `GruposController`, `RubrosController`, `ProveedoresController`, `OrganismosController`, `UsuariosController`, `NovedadesController`.
- Layout con componente `_NovedadesBadge` que consulta `INovedadesService` vía ViewComponent.
- Validación cliente con jQuery Validate + server-side con `ModelState`. Mensajes en español.
- Filtro de autorización por rol a nivel de Controller/Action.
- **Prohibido** meter lógica de cálculo en Controllers (se delega a Services).

### 6.2 Negocio
- Patrón `Resultado`/`Resultado<T>` para comunicar éxito/errores funcionales al Controller sin excepciones.
- Reglas encapsuladas:
  - `FacturaService` es el único que asigna `Numero` y persiste `TasaImpuestoAplicada`.
  - `MovimientoStockService` es el único que muta stock (derivado) y valida matriz.
  - `CuotaService` es el único que muta estados de cuota y movimientos de caja por rechazo/regularización.
  - `AcreditacionJobService` es el único que acredita cuotas automáticamente.
- **Transacciones**: `CrearVenta`, `EmitirFactura`, `RegistrarMovimientoStock`, `Regularizar3b` abren transacción EF.

### 6.3 Datos
- Entidades: `Venta`, `DetalleVenta`, `Factura`, `Cuota`, `MovimientoCaja`, `Gasto`, `Rubro`, `Proveedor`, `Grupo`, `MovimientoStock`, `OrganismoIntermediario`, `ComprobanteGasto`, `Novedad`, `UsuarioProductor` (Identity).
- **Índices**:
  - `Factura.Numero` único.
  - `MovimientoCaja(Estado, Fecha)` para listados de Caja.
  - `Cuota(Estado, FechaVencimiento)` para job.
  - `MovimientoStock(GrupoDestinoId, Tipo)` con filtro parcial para `Inicial` (unicidad por Grupo — regla validada en Service; a nivel DB queda como índice no único pero el Service garantiza unicidad).
- **Baja lógica** vía propiedad `Activo` (Grupo, Rubro, Proveedor, Organismo, Usuario). Sin borrado físico.
- **Almacenamiento de comprobante**: filesystem bajo `App_Data/comprobantes/{yyyy}/{mm}/{guid}.{ext}` + registro `ComprobanteGasto(GastoId, RutaRelativa, MimeType, TamañoBytes)`.

---

## 7. Riesgos y supuestos

### 7.1 Riesgos de diseño
- **RD1** Concurrencia en numeración de Factura → usar secuencia MySQL o tabla `ContadorFactura` con `UPDATE ... RETURNING` dentro de la transacción (decisión final en capa arquitecto).
- **RD2** Transaccionalidad en venta multi-grupo → todo en una única `SaveChangesAsync` con transacción explícita.
- **RD3** Rechazo de cuota → mutación de estado del movimiento, no contramovimiento; verificar que reportes de Caja ignoren `Pendiente`.
- **RD4** Validación del comprobante en cliente (UX) + servidor (seguridad).
- **RD5** Idempotencia del job diario vía query: sólo acredita cuotas sin movimiento `Acreditado` vigente.

### 7.2 Supuestos de diseño
- **SD1** Identity con dos roles (`Productor`, `SuperUsuario`) preconfigurados en seed.
- **SD2** Timestamps en UTC en DB; presentación en `America/Argentina/Buenos_Aires`.
- **SD3** Comprobantes en filesystem local (no cloud storage en v1).
- **SD4** Enums se persisten como `int` (con `HasConversion<string>` opcional para legibilidad — decisión arquitecto).
- **SD5** Moneda única ARS, sin tipo de cambio.

---

## 8. Pruebas mínimas (suma al set del análisis)

Se mantienen PF1–PF52 + PV1–PV12.

Agrega al diseño:
- **PD1** `VentasController.Create` no contiene aritmética ni chequeo de matriz (todo vía `IVentaService`).
- **PD2** `FacturaService.EmitirAsync` bajo concurrencia simulada (2 hilos) produce correlativos distintos y contiguos.
- **PD3** `GastoViewModel` rechaza archivos > 5MB o extensiones no permitidas antes del POST (cliente) y en `GastoService` (servidor).
- **PD4** `MovimientoStockService.RegistrarAsync` devuelve `Resultado.Error` con mensaje claro cuando el par de categorías no está en la matriz; Controller retorna a la vista con `ModelState` poblado.
- **PD5** Segunda ejecución del `AcreditacionJobService.EjecutarDiariaAsync` el mismo día no crea movimientos nuevos ni duplica novedades.
- **PD6** `Grupos/Delete` con stock > 0 → `IStockQueryService.TieneStockAsync` devuelve true → bloqueo (PF33).
- **PD7** `Usuarios/Create` intentando crear un sexto Productor activo → `IUsuarioProductorService` rechaza con error claro.

---

## 9. Trazabilidad a requisitos

| Requisito (v10) | Pantalla | Servicio | ViewModel |
|---|---|---|---|
| §3.1–§3.3 Venta/Factura/Cuotas | Ventas/*, Facturas/* | IVentaService, IFacturaService | VentaVM, FacturaVM |
| §3.2 Numeración F-000123 | Facturas/Create | IFacturaService.AsignarNumero | FacturaVM.Numero (read-only) |
| §3.5 Job diario + Novedades | Novedades/Index | IAcreditacionJobService, INovedadesService | NovedadVM |
| §3.6–§3.7 Rechazo/Regularización | Cuotas/* | ICuotaService | CuotaAccionVM |
| §4 Gastos + comprobante + autocomplete | Gastos/* | IGastoService | GastoVM |
| §5.5–§5.7 Movimientos + Inicial + matriz | MovimientosStock/*, Stock/Index | IMovimientoStockService, IStockQueryService | MovimientoStockVM |
| §6 Proveedores con ámbito | Proveedores/*, Gastos/Create | ICatalogoService (Proveedor) | ProveedorVM |
| §7 Caja/CtaCte | Caja/* | ICajaService | — |
| §8 Dashboard | Dashboard/Index | IDashboardService | DashboardFiltroVM / DashboardResultadoVM |
| §11 ABM Organismo | Organismos/* | ICatalogoService | OrganismoVM |
| §2 Usuarios (5 Productores + 1 Super) | Usuarios/* | IUsuarioProductorService | UsuarioProductorVM |

---

## 10. Checklist de salida para merge

- [ ] 26 pantallas mapeadas con ruta MVC y rol de acceso.
- [ ] 14 ViewModels definidos con validaciones en español.
- [ ] 10+ contratos de servicio con firmas asincrónicas y resultados tipados.
- [ ] Cero lógica de negocio en Controllers (verificable por PD1).
- [ ] Flujos de alta/edición/rechazo/regularización documentados (§2).
- [ ] Requerimientos de datos por pantalla (§5).
- [ ] Reglas clave delegadas a servicios: numeración, matriz, stock inicial, rechazo, regularización, job diario.
- [ ] Transacciones explícitas en operaciones multi-entidad (Venta, Factura, MovimientoStock, Regularización 3b).
- [ ] Índices y estrategia de almacenamiento de comprobante definidos (§6.3).
- [ ] Riesgos de diseño RD1–RD5 registrados con mitigación esbozada.
- [ ] Pruebas de diseño PD1–PD7 agregadas al plan.
- [ ] Trazabilidad a requisitos del análisis v10 (§9).
- [ ] Listo para handoff al agente arquitecto/desarrollador.

---

## 11. Handoff siguiente

Entregar a los próximos agentes:

- **Arquitecto técnico**: elegir mecanismo de correlativo (secuencia MySQL vs tabla contador), estrategia de transacciones, serialización de enums, estrategia de almacenamiento (local vs futuro cloud), DI y registro de servicios/jobs, mapping EF Core (fluent API) para las 14 entidades.
- **Desarrollador**: implementar en el orden sugerido 1) ABMs catálogos → 2) Stock + MovimientosStock → 3) Ventas/Facturas/Cuotas → 4) Gastos → 5) Caja → 6) Job + Novedades → 7) Dashboard.
- **Tester funcional**: scripts de PF1–PF52 + PV1–PV12 + PD1–PD7.

---

## 12. Historial de versiones

- **v1** — Primera consolidación del diseño funcional a partir del análisis funcional v10. Define pantallas, ViewModels, contratos de servicios, requerimientos de datos, riesgos de diseño y pruebas de diseño. Listo para handoff al agente arquitecto.
