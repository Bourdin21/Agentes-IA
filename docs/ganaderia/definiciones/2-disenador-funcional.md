# Diseño Funcional — Sistema de Gestión Ganadera

Versión: **v3**
Agente: `2 - disenador-funcional`
Entrada: `docs/ganaderia/definiciones/1-analista-funcional.md` v12
Repositorio de v2/v3: **`C:\Sistemas\ganaderia - emo`** (exclusivo; NO aplica a `ganaderia - fausto`).
Proyecto: BlankProject (ASP.NET Core **MVC**, .NET 10, EF Core 10, MySQL 8, Identity, Serilog)
Alcance: diseño **funcional implementable** (flujos, ViewModels, contratos de servicios, requerimientos de datos por pantalla). **No** incluye código.

> Nota de nomenclatura: el diseño v1 usaba "Gasto"/`Gastos`; la implementación real ya renombró el módulo a **`Egreso`/`Egresos`** (`EgresosController`, `IEgresoService`, entidad `Egreso`). Desde v2 este documento usa la nomenclatura real del código.

---

## 0. Salida mínima del agente

### 0.1 Alcance funcional resumido

Se traduce el análisis funcional v11 a un diseño implementable en tres capas (Presentación MVC / Negocio Services / Datos EF Core) para los tres ejes del sistema (Ingresos, Egresos, Stock) + transversales (Caja, Dashboard, Novedades, Catálogos ABM). **v2** rediseña el módulo Egresos: el alta pasa de "1 forma de pago" a una **grilla de pagos múltiples** (`EgresoPago`), con ciclo de vida propio para cheques diferidos (Pendiente → Acreditado vía job diario) y acciones de rechazo/regularización simétricas a las de Cuota. El resto del diseño v1 (Ingresos, Stock, Caja, Dashboard, Catálogos) se mantiene sin cambios.

### 0.2 Impacto técnico por capa

- **Presentación (Controllers + Views MVC)**: `EgresosController.Create` pasa de formulario simple a formulario + **grilla dinámica de pagos** (agregar/quitar filas: FormaDePago, Importe, FechaEfectiva, FechaVencimiento condicional); `Egresos/Details` muestra la grilla de pagos con su estado y acciones; se agregan acciones `EgresoPagos/Rechazar/{id}` y `EgresoPagos/Regularizar/{id}` (mismo patrón que `Cuotas/Rechazar` y `Cuotas/Regularizar`).
- **Negocio (Application/Services)**: `IEgresoService.CrearAsync` pasa a recibir una lista de pagos y validar la suma exacta contra el importe; nuevo contrato `IEgresoPagoService` (rechazo/regularización, simétrico a `ICuotaService`); `IAcreditacionJobService`/hosted service existente se extiende para procesar también `EgresoPago` tipo Cheque vencidos.
- **Datos (Domain + Infrastructure)**: nueva entidad `EgresoPago` (FK a `Egreso`); `MovimientoCaja` gana FK nullable `EgresoPagoId` (reemplaza el uso directo de `EgresoId`); `Egreso` pierde el campo `FormaDePago`.

### 0.3 Riesgos y supuestos

Riesgos heredados: R13, R16, R18, R20/R24, R22, R23, R25, R26. Nuevos del diseño v2:
- **RD1** Concurrencia en generación de correlativo de Factura (dos usuarios emiten simultáneamente).
- **RD2** Atomicidad en venta multi-grupo: descuento de stock + creación de movimientos + factura + cuotas debe ser transaccional.
- **RD3** Reversión consistente al rechazar una cuota acreditada (mutar estado del movimiento sin crear contra-asiento).
- **RD4** Tamaño/formato del comprobante validado en cliente y servidor (doble validación).
- **RD5** Idempotencia del job diario: clave natural por `(CuotaId, FechaEjecución)` para evitar reacreditaciones.
- **RD6** (v2) Alta de Egreso con pagos: validación de suma exacta debe correr en cliente (UX) y servidor (autoridad), igual que RD4 para comprobantes.
- **RD7** (v2) El job diario extendido debe recorrer `EgresoPago` con la misma clave de idempotencia que RD5 (sin `MovimientoCaja` Acreditado vigente), evitando doble acreditación si se ejecuta más de una vez.
- **RD8** (v2) Rechazo/regularización de `EgresoPago` reutiliza la lógica ya probada de `CuotaService` (RD3); mantener el mismo patrón evita divergencia de comportamiento entre Ingresos y Egresos.

Supuestos: los del análisis v11 (S1–S34) + SD1 Identity provee `Productor` y `SuperUsuario` como roles; SD2 todo timestamp se persiste en UTC y se muestra en hora local Argentina; SD3 el almacenamiento de comprobantes es filesystem local en v1; SD6 (v2) el job diario extendido sigue corriendo como una única ejecución por día (misma tabla `JobEjecucion`), no se separan en dos jobs.

### 0.4 Pruebas mínimas requeridas

Se mantienen PF1–PF61 + PV1–PV16 del análisis v11. Se agregan pruebas de diseño de integración UI↔Service:
- **PD1** Controller de Venta delega al Service y no contiene lógica de cálculo.
- **PD2** Service de Factura genera correlativo único bajo concurrencia simulada.
- **PD3** ViewModel de Egreso valida tamaño del comprobante antes de enviar al servidor.
- **PD4** Service de Compensación rechaza par inválido según matriz y Controller devuelve error al ViewModel.
- **PD5** Service de Job es re-ejecutable sin duplicar movimientos (Cuotas y EgresoPago).
- **PD8** (v2) `EgresoViewModel` rechaza el submit en cliente si la suma de pagos != importe total; `EgresoService.CrearAsync` repite la validación en servidor y no persiste nada si falla.
- **PD9** (v2) `EgresoPagoService.RegistrarPagoCheque` dentro del alta deja el pago en `Pendiente` sin crear `MovimientoCaja`; sólo el job lo crea al vencer.
- **PD10** (v2) `EgresosController` no contiene lógica de acreditación/rechazo/regularización (delega a `IEgresoPagoService`), verificable igual que PD1.

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
| Listado de Egresos | `Egresos/Index` | Productor | Grilla |
| Alta de Egreso | `Egresos/Create` | Productor | Formulario + **grilla dinámica de pagos** + upload + autocomplete |
| Detalle de Egreso | `Egresos/Details/{id}` | Productor | Sólo lectura + grilla de pagos con estado + link comprobante |
| Acción: Rechazar pago (cheque) | `EgresoPagos/Rechazar/{id}` (POST) | Productor | Confirmación (v2) |
| Acción: Regularizar pago (cheque) | `EgresoPagos/Regularizar/{id}` (POST) | Productor | Formulario Opción 3a/3b (v2) |

> No hay `Egresos/Edit`: se mantiene el comportamiento actual (sólo alta + anulación, análisis v11 §4.6).

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

### 2.6 Alta de Egreso con pagos múltiples (v2 — reemplaza alta con forma de pago única)

```
Egresos/Create
  ├── Fecha, Importe total, Rubro (ddl), Concepto (input con autocomplete via AJAX → EgresoService.SugerenciasDetalleAsync)
  ├── Descripción, Proveedor (ddl filtrado por Ámbito=Egresos/Ambos vía ProveedorService.ListarParaEgresos)
  ├── Comprobante (file opcional, 5MB, PDF/JPG/PNG)
  ├── Grilla de Pagos (mín. 1 fila, agregar/quitar dinámicamente):
  │     ├── FormaDePago (Efectivo/Transferencia/Cheque)
  │     ├── Importe (> 0)
  │     ├── FechaEfectiva (≤ hoy)
  │     └── FechaVencimiento (habilitada y **requerida** sólo si FormaDePago = Cheque; ≥ FechaEfectiva)
  ├── Validación cliente: extensión/tamaño comprobante (PV4/PV9) + Σ Pagos.Importe == Importe total (PV15/PF56) en vivo
  └── [Submit] → EgresoService.CrearAsync(viewModel)
		├── valida extensión/tamaño servidor
		├── valida Σ Pagos.Importe == Importe (servidor, autoridad — RD6); si falla, no persiste nada (transaccional)
		├── valida FechaVencimiento requerida y ≥ FechaEfectiva en cada pago Cheque (PV13/PV14)
		├── persiste Egreso + copia archivo a storage (ruta relativa)
		├── por cada pago Efectivo/Transferencia → crea el pago en Acreditado + su MovimientoCaja egreso Acreditado (PF53)
		└── por cada pago Cheque → crea el pago en Pendiente, SIN MovimientoCaja todavía (PF54)
```

### 2.7 Rechazo y regularización de pago de Egreso — cheque diferido (v2, simétrico a §2.3/§2.4)

```
Egresos/Details/{id} → botón [Rechazar] por pago tipo Cheque en Pendiente o Acreditado
  └── POST EgresoPagos/Rechazar/{id}
		└── EgresoPagoService.RechazarAsync(id)
			  ├── pago → Rechazado (no permitido si ya está Rechazado → PV16)
			  └── si existía MovimientoCaja Acreditado → muta a Pendiente (NO borra, NO contramovimiento) (PF59)

Egresos/Details/{id} → botón [Regularizar] sobre pago Rechazado
  └── EgresoPagos/Regularizar/{id} (formulario modal o página)
		├── Radio: [Error de carga (3a)] | [Pago posterior (3b)]
		├── Si 3b: Fecha real + Forma de pago
		└── [Submit] → EgresoPagoService.RegularizarAsync(id, opcion, fechaReal?, formaPago?)
			  ├── 3a: pago → Acreditado; movimiento original → Acreditado (fecha original) (PF60)
			  └── 3b: pago queda Rechazado; movimiento original queda Pendiente; crea MovimientoCaja nuevo (Acreditado, fecha real) (PF61)
```

### 2.8 Job diario de acreditación (no es pantalla; se consume en Novedades) — v2 extendido

```
IHostedService (AcreditacionCuotasHostedService, ya existente) → corrida diaria 03:00 ART
  └── AcreditacionService.Ejecutar(fecha)
		├── Cuotas: obtiene cuotas Pendientes con Vencimiento <= hoy sin MovimientoCaja Acreditado vigente (idempotencia)
		│     └── por cada una: cuota → Acreditada + crea MovimientoCaja Acreditado
		├── (v2) EgresoPago: obtiene pagos tipo Cheque, Pendiente, con FechaVencimiento <= hoy sin MovimientoCaja Acreditado vigente (RD7)
		│     └── por cada uno: pago → Acreditado + crea MovimientoCaja egreso Acreditado (PF57, PF58)
		└── registra UN resumen consolidado en Novedades (persistente por día) para mostrar en bandeja: Cuotas + Pagos de Egreso acreditados
Login → Novedades/Index si hay novedades del día sin leer
```

### 2.9 Autorización

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

### 3.5 EgresoViewModel (v2 — reemplaza el campo `FormaDePago` único por `Pagos`)
- `Fecha` (≤ hoy)
- `Importe` (> 0) — importe total del Egreso
- `RubroId` (requerido)
- `Detalle` (string, requerido, 200 chars, con autocomplete)
- `ProveedorId` (requerido, filtrado por ámbito)
- `Comprobante: IFormFile?` (opcional, 5MB, `.pdf/.jpg/.jpeg/.png`)
- `Pagos: List<EgresoPagoViewModel>` (mín. 1)
- **Validación**: `Pagos.Sum(p => p.Importe) == Importe` (cliente en vivo + servidor autoritativo, RD6).

### 3.5.1 EgresoPagoViewModel (nuevo, v2)
- `FormaDePago` (enum: Efectivo/Transferencia/Cheque, requerido)
- `Importe` (> 0)
- `FechaEfectiva` (requerido, ≤ hoy)
- `FechaVencimiento` (nullable; **requerida y habilitada sólo si FormaDePago = Cheque**; debe ser ≥ FechaEfectiva)

### 3.5.2 EgresoPagoAccionViewModel (rechazo / regularización — nuevo, v2)
- `EgresoPagoId`
- `Opcion` (enum: `Rechazar`, `Regularizar3a`, `Regularizar3b`)
- `FechaReal` (requerido si 3b)
- `FormaDePago` (requerido si 3b)

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

### 4.4 IEgresoService (v2 — reemplaza `IGastoService`)
- `Task<Resultado<int>> CrearAsync(EgresoViewModel vm, string userId)` — valida comprobante, valida Σ Pagos == Importe (RD6), persiste Egreso + N `EgresoPago` + archivo; crea MovCaja inmediato sólo para pagos Efectivo/Transferencia (PF53/PF55)
- `Task<Resultado> AnularAsync(int id, string userId)` — baja lógica de Egreso + todos sus `EgresoPago` + todos los `MovimientoCaja` asociados (análisis v11 §4.6)
- `Task<IReadOnlyList<string>> SugerenciasDetalleAsync(string prefijo, int top)` — autocomplete normalizado (trim + case-insensitive, distinct histórico) — ya existente, sin cambios

### 4.4.1 IEgresoPagoService (nuevo, v2 — simétrico a `ICuotaService`)
- `Task<Resultado> RechazarAsync(int egresoPagoId, string userId)` — sólo pagos tipo Cheque en Pendiente/Acreditado (PF59, PV16)
- `Task<Resultado> RegularizarAsync(int egresoPagoId, OpcionRegularizacion opcion, DateTime? fechaReal, FormaDePago? formaPago, string userId)` — PF60, PF61
- **Internos (invocados por el job diario extendido)**: `AcreditarChequesVencidosAsync(DateOnly hoy)` — mismo patrón que `ICuotaService.AcreditarCuotasVencidasAsync` (idempotente, RD7)

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

### 4.9 IAcreditacionJobService (invocado por `IHostedService`) — v2 extendido
- `Task<ResumenAcreditacionDto> EjecutarDiariaAsync(DateTime fecha)` — idempotente (RD5); orquesta `ICuotaService.AcreditarCuotasVencidasAsync` **y** (v2) `IEgresoPagoService.AcreditarChequesVencidosAsync`; genera UNA entrada consolidada en `Novedades` con ambos totales.
- **Clave de idempotencia**: `(CuotaId)` / `(EgresoPagoId)` ya resuelta por la invariante "no existe movimiento Acreditado asociado" (PF17, PV6, PF58).

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
| Egresos/Create | Rubros activos + Proveedores con ámbito Egresos/Ambos + historial Conceptos del usuario | Egreso + N EgresoPago + archivo comprobante + MovCaja (sólo pagos Efectivo/Transferencia) |
| Egresos/Details | Egreso + Pagos + MovimientosCaja vinculados | — |
| EgresoPagos/Rechazar | EgresoPago + MovCaja asociado | Muta EgresoPago + MovCaja |
| EgresoPagos/Regularizar | EgresoPago + MovCaja | Muta EgresoPago / MovCaja y/o crea nuevo MovCaja |
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
- Entidades: `Venta`, `DetalleVenta`, `Factura`, `Cuota`, `MovimientoCaja`, `Egreso`, **`EgresoPago` (nueva, v2)**, `Rubro`, `Proveedor`, `Grupo`, `MovimientoStock`, `OrganismoIntermediario`, `ComprobanteEgreso`, `Novedad`, `UsuarioProductor` (Identity).
- **Índices**:
  - `Factura.Numero` único.
  - `MovimientoCaja(Estado, Fecha)` para listados de Caja.
  - `Cuota(Estado, FechaVencimiento)` para job.
  - **(v2)** `EgresoPago(Estado, FormaDePago, FechaVencimiento)` para el job diario extendido (mismo patrón que `Cuota`).
  - `MovimientoStock(GrupoDestinoId, Tipo)` con filtro parcial para `Inicial` (unicidad por Grupo — regla validada en Service; a nivel DB queda como índice no único pero el Service garantiza unicidad).
- **Baja lógica** vía propiedad `Activo`/`SoftDestroyable` (Grupo, Rubro, Proveedor, Organismo, Usuario, Egreso, EgresoPago). Sin borrado físico.
- **Almacenamiento de comprobante**: filesystem bajo `App_Data/comprobantes/{yyyy}/{mm}/{guid}.{ext}` + registro `ComprobanteEgreso(EgresoId, NombreAlmacenado, ContentType, TamanoBytes)` (ya existente, sin cambios).
- **(v2)** `MovimientoCaja` gana FK nullable `EgresoPagoId`; se evalúa en capa arquitecto si se conserva `EgresoId` como acceso rápido o se resuelve por navegación `EgresoPago.Egreso`.

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

Se mantienen PF1–PF61 + PV1–PV16.

Agrega al diseño:
- **PD1** `VentasController.Create` no contiene aritmética ni chequeo de matriz (todo vía `IVentaService`).
- **PD2** `FacturaService.EmitirAsync` bajo concurrencia simulada (2 hilos) produce correlativos distintos y contiguos.
- **PD3** `EgresoViewModel` rechaza archivos > 5MB o extensiones no permitidas antes del POST (cliente) y en `EgresoService` (servidor).
- **PD4** `MovimientoStockService.RegistrarAsync` devuelve `Resultado.Error` con mensaje claro cuando el par de categorías no está en la matriz; Controller retorna a la vista con `ModelState` poblado.
- **PD5** Segunda ejecución del `AcreditacionJobService.EjecutarDiariaAsync` el mismo día no crea movimientos nuevos ni duplica novedades (Cuotas y EgresoPago).
- **PD6** `Grupos/Delete` con stock > 0 → `IStockQueryService.TieneStockAsync` devuelve true → bloqueo (PF33).
- **PD7** `Usuarios/Create` intentando crear un sexto Productor activo → `IUsuarioProductorService` rechaza con error claro.
- **PD8** (v2) `EgresoViewModel` rechaza el submit en cliente si Σ Pagos != Importe; `EgresoService.CrearAsync` repite la validación en servidor sin persistir nada si falla.
- **PD9** (v2) `EgresoService.CrearAsync` deja un pago Cheque en `Pendiente` sin `MovimientoCaja`; sólo el job lo crea al vencer.
- **PD10** (v2) `EgresosController` no contiene lógica de acreditación/rechazo/regularización (delega a `IEgresoPagoService`).
- **PD11** (v3) `Egresos/Create` y `Facturas/Create` inicializan Select2 sobre el input de Concepto/Motivo con `ajax.url` apuntando al endpoint de sugerencias existente/nuevo; no se duplica lógica de fetch manual (se retira el `fetch` + `<datalist>` custom de v1/v2).
- **PD12** (v3) `FacturaVentaService.CrearAsync`/`ActualizarAsync` no valida `Motivo` contra un enum; sólo aplica `[Required, StringLength(200)]` a nivel ViewModel + Service.

---

## 8.1 Diseño v3 — Autocomplete Select2 (Concepto de Egreso, Motivo de Factura de venta)

### Motivación
El `<datalist>` nativo usado en v1/v2 para Concepto de Egreso tiene un defecto de UX conocido (no siempre refresca el desplegable visible tras poblarse de forma asíncrona — ver `6-qa.md` §12/GAN-004, mitigado con un workaround best-effort). El cliente pidió reemplazarlo por un widget confiable, y extender el mismo patrón (texto libre + sugerencias del servidor) al campo `Motivo` de Factura de venta, que hoy es un enum cerrado de 3 valores.

### Pantallas afectadas
- `Egresos/Create` — el input de Concepto pasa de `<input list="DetalleSugerencias"> + <datalist>` a `<input type="hidden">` (o `<select>` vacío) inicializado como Select2 con `tags: true` + fuente AJAX.
- `Facturas/Create` (y `Facturas/Edit` si existiera edición previa a emisión) — el `<select asp-for="Motivo" asp-items="Html.GetEnumSelectList<MotivoVenta>()">` se reemplaza por el mismo patrón Select2 de texto libre + sugerencias.

### Componente Select2 (JS, patrón único reutilizable en ambas pantallas)
```js
$('#Detalle').select2({
    theme: 'bootstrap-5',
    tags: true,                 // permite valor libre no presente en las sugerencias
    ajax: {
        url: '/Egresos/SugerenciasDetalle',   // o /Facturas/SugerenciasMotivo
        dataType: 'json',
        delay: 200,
        data: params => ({ term: params.term, top: 10 }),
        processResults: data => ({ results: data.map(v => ({ id: v, text: v })) })
    },
    minimumInputLength: 0,
    placeholder: 'Escriba para buscar o cargue un valor nuevo'
});
```
Mismo snippet, mismo endpoint-shape (`term`, `top` → `List<string>` JSON) para ambas pantallas — sólo cambia la URL. No requiere cambios en el contrato de `IEgresoService.SugerenciasDetalleAsync` (ya devuelve `List<string>`); requiere un contrato **nuevo simétrico** en `IFacturaVentaService` para Motivo (§8.2).

### ViewModels
- `EgresoCreateVm.Detalle`: sin cambio de tipo (sigue `string`), sólo cambia el widget de carga en la vista.
- `FacturaVentaCreateVm.Motivo`: cambia de `MotivoVenta` (enum) a `string` — `[Required, StringLength(200)]`, `[Display(Name = "Motivo")]`.

### 8.2 Contrato de servicio nuevo — sugerencias de Motivo
```
Task<List<string>> SugerenciasMotivoAsync(string? term, int top = 10);
```
En `IFacturaVentaService` (o interfaz nueva `IFacturaVentaSugerenciasService` si el diseño arquitectónico prefiere separarlo) — mismo patrón que `IEgresoService.SugerenciasDetalleAsync`: histórico distinct de `FacturaVenta.Motivo` no anulada, normalizado (trim + case-insensitive), a nivel organización.

### Riesgos de diseño v3
- **RD9** Retirar el `<datalist>`/fetch manual de v1/v2 sin dejar código muerto (JS viejo conviviendo con Select2 nuevo).
- **RD10** `Motivo` como texto libre pierde la garantía de "lista cerrada" — si en el futuro se necesita agrupar/reportar por motivo, requerirá normalización adicional (ya advertido en análisis v12 R28).
- **RD11** Migración del dato `FacturaVenta.Motivo` de `int` a `string` sobre producción (ver arquitectura v3 para el plan concreto).

---

## 9. Trazabilidad a requisitos

| Requisito (v10) | Pantalla | Servicio | ViewModel |
|---|---|---|---|
| §3.1–§3.3 Venta/Factura/Cuotas | Ventas/*, Facturas/* | IVentaService, IFacturaService | VentaVM, FacturaVM |
| §3.2 Numeración F-000123 | Facturas/Create | IFacturaService.AsignarNumero | FacturaVM.Numero (read-only) |
| §3.5 Job diario + Novedades | Novedades/Index | IAcreditacionJobService, INovedadesService | NovedadVM |
| §3.6–§3.7 Rechazo/Regularización | Cuotas/* | ICuotaService | CuotaAccionVM |
| §4 Egresos + pagos múltiples + comprobante + autocomplete | Egresos/* | IEgresoService | EgresoVM |
| §4.2–§4.5 Pagos de Egreso, cheque diferido, rechazo/regularización (v11) | EgresoPagos/* | IEgresoPagoService | EgresoPagoVM, EgresoPagoAccionVM |
| §5.5–§5.7 Movimientos + Inicial + matriz | MovimientosStock/*, Stock/Index | IMovimientoStockService, IStockQueryService | MovimientoStockVM |
| §6 Proveedores con ámbito | Proveedores/*, Gastos/Create | ICatalogoService (Proveedor) | ProveedorVM |
| §7 Caja/CtaCte | Caja/* | ICajaService | — |
| §8 Dashboard | Dashboard/Index | IDashboardService | DashboardFiltroVM / DashboardResultadoVM |
| §11 ABM Organismo | Organismos/* | ICatalogoService | OrganismoVM |
| §2 Usuarios (5 Productores + 1 Super) | Usuarios/* | IUsuarioProductorService | UsuarioProductorVM |
| §3.1/§4.1 Autocomplete Select2 Concepto/Motivo (v12) | Egresos/Create, Facturas/Create | IEgresoService.SugerenciasDetalleAsync, IFacturaVentaService.SugerenciasMotivoAsync | EgresoVM, FacturaVentaCreateVm |

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
- [ ] **(v2)** Grilla dinámica de pagos en `Egresos/Create` documentada con validación de suma exacta cliente + servidor.
- [ ] **(v2)** `IEgresoPagoService` y pantallas `EgresoPagos/Rechazar`, `EgresoPagos/Regularizar` documentadas, simétricas a `ICuotaService`/`Cuotas/*`.
- [ ] **(v2)** Extensión del job diario a `EgresoPago` documentada (RD7) sin duplicar la ejecución existente de Cuotas.
- [ ] **(v2)** Riesgos RD6–RD8 y pruebas PD8–PD10 agregados al plan.
- [ ] **(v3)** Select2 reemplaza `<datalist>` en `Egresos/Create` (Concepto), sin código muerto del widget viejo.
- [ ] **(v3)** Select2 aplicado a `Motivo` en `Facturas/Create`, con endpoint `SugerenciasMotivoAsync` simétrico a `SugerenciasDetalleAsync`.
- [ ] **(v3)** Riesgos RD9–RD11 y pruebas PD11–PD12 agregados al plan.

---

## 11. Handoff siguiente

Entregar a los próximos agentes:

- **Arquitecto técnico**: elegir mecanismo de correlativo (secuencia MySQL vs tabla contador), estrategia de transacciones, serialización de enums, estrategia de almacenamiento (local vs futuro cloud), DI y registro de servicios/jobs, mapping EF Core (fluent API) para las entidades, **incluida `EgresoPago` y el cambio de FK en `MovimientoCaja` (v2)**, y diseño de la(s) migración(es) para eliminar `Egreso.FormaDePago` y crear `EgresoPago`.
- **Desarrollador**: implementar en el orden sugerido 1) ABMs catálogos → 2) Stock + MovimientosStock → 3) Ventas/Facturas/Cuotas → 4) Egresos con pagos múltiples (v2) → 5) Caja → 6) Job + Novedades (extendido, v2) → 7) Dashboard.
- **Tester funcional**: scripts de PF1–PF61 + PV1–PV16 + PD1–PD10.

---

## 12. Historial de versiones

- **v1** — Primera consolidación del diseño funcional a partir del análisis funcional v10. Define pantallas, ViewModels, contratos de servicios, requerimientos de datos, riesgos de diseño y pruebas de diseño. Listo para handoff al agente arquitecto.
- **v2** — A partir del análisis funcional v11 (proyecto `ganaderia - emo` únicamente): rediseño del módulo Egresos con pagos múltiples (`EgresoPago`), grilla dinámica en el alta, ciclo Pendiente→Acreditado de cheque diferido vía extensión del job diario existente, y acciones de rechazo/regularización (`IEgresoPagoService`) simétricas a `ICuotaService`. Se alinea la nomenclatura del documento a la del código real (`Egreso`, no `Gasto`). Agregados RD6–RD8, PD8–PD10.
- **v3** — A partir del análisis funcional v12 (proyecto `ganaderia - emo` únicamente, §8.1/§8.2): autocomplete de Concepto (Egresos) migra de `<datalist>` a **Select2**; `Motivo` de Factura de venta pasa de enum cerrado a texto libre con autocomplete Select2, nuevo contrato `IFacturaVentaService.SugerenciasMotivoAsync` simétrico a `SugerenciasDetalleAsync`. Agregados RD9–RD11, PD11–PD12.
