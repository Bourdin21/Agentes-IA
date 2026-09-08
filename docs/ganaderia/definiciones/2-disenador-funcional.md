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

## 8.3 Diseño v4 — Descuento comercial pre-impuestos + gráfico de IVA compras/ventas

A partir del análisis funcional **v13** (§3.9, §3.10, §4.8, §8.1).

### Escaneo de reutilización cross-proyecto (obligatorio, tarea 0)

| Qué se buscó | Dónde apareció | Decisión |
|---|---|---|
| Descuento **global** por comprobante | `ShowroomGriffin/2-disenador-funcional.md` §3.3 (`Descuento %` + línea "Descuento ( 0 %): $ 0" entre Subtotal y Total) y `5-implementador.md` (`total = subtotal - model.DescuentoMonto`, recálculo JS en vivo) | Se **reutiliza el layout** (fila de descuento intercalada entre Subtotal y Total, recálculo en vivo). **No** se reutiliza la mecánica: allí el descuento es sólo importe y se aplica al final, sin impuestos de por medio. |
| Descuento **por ítem** | `la-platense` (`ItemVenta.Descuento`/`Recargo` como importes) y `vinosefue` (`PedidoItem.DescuentoPorcentajeCosto`, sólo %) | **Descartado**: el análisis v13 P3:A definió descuento global por comprobante. Se toma sí el aprendizaje de `la-platense/5-implementador.md` §216 ("no quedó claro si Descuento es monto o porcentaje"): acá se persisten **los dos** campos, y la autoridad es el importe. |
| Doble campo **% ↔ importe** sincronizado | **Este mismo proyecto**: `Facturas/Create.cshtml` (`impState`, v13) y `Egresos/Create.cshtml` (`ivaDriver`, v15) | **Reutilización directa**. El descuento entra como un grupo más del driver existente. |
| Gráfico Chart.js barras + línea | **Este mismo proyecto**: `Dashboard/TableroAnual.cshtml` (`chartMensual`: 2 barras + línea de neto) | **Reutilización directa**: el gráfico de IVA es un clon con otras series. La advertencia de `koi/5-implementador.md` (Chart.js con colores viejos al togglear tema sin reload) **no aplica**: ganaderia no tiene toggle de tema. |

**Conclusión:** no se importa código de otros repositorios; el patrón exacto ya está resuelto y probado dentro de ganaderia. El aporte externo es el layout de ShowroomGriffin y una lección de modelado de la-platense.

### 8.3.1 `Facturas/Create` (y edición) — card "Descuento, impuestos y percepciones"

```
┌─ Descuento, impuestos y percepciones ───────────────────────────────┐
│  Subtotal                                          1.000.000,00     │
│                                                                      │
│  Descuento %  [ 10,00 ]   Descuento $ [ 100.000,00 ]                │
│               sobre Subtotal                    [ Sin descuento ]   │
│                                                                      │
│  Neto gravado                                        900.000,00     │
│                                                                      │
│  IVA %  [ 21,00 ]   IVA $ [ 189.000,00 ]                            │
│         sobre Neto gravado      [0%] [10,5%] [21%] [27%]            │
│  Ingresos Brutos % [ 3,00 ]  $ [ 32.670,00 ]  sobre Neto + IVA      │
│  Otras percepciones % [     ]  $ [        ]   sobre Neto + IVA      │
│  ──────────────────────────────────────────────────────────────     │
│  Total                                             1.121.670,00     │
└──────────────────────────────────────────────────────────────────────┘
```

**Mecánica (extensión mínima del driver existente).** El array `impGrupos` pasa de `['iva','iibb','percep']` a `['desc','iva','iibb','percep']` y `impState` gana la clave `desc` (`'pct'` por defecto). La **única** función que cambia es `base(grupo)`:

```js
const neto = () => subtotal - num(montoDe('desc'));
base('desc')            -> subtotal
base('iva')             -> neto()
base('iibb'|'percep')   -> neto() + num(montoDe('iva'))
Total                    = neto() + montoIva + montoIibb + montoPercep
```

Como el descuento es el primer elemento del array, queda resuelto antes que los impuestos en la misma pasada de `recalcImpuestos()`, y toda la cascada existente (editar un ítem → `recalcSubtotal` → `recalcImpuestos` → `actualizarResumenIngresos`) sigue funcionando sin tocarse. Esto materializa P4:A: **el descuento baja la base de IVA, IIBB y percepciones a la vez**, con un solo punto de cambio.

- **"Sin descuento"**: botón que pone ambos campos en 0 y `impState.desc = 'pct'`. Estado inicial de toda factura nueva (el descuento es opcional, PF70).
- **"Neto gravado"** es una línea calculada, no un input. Sólo se muestra cuando hay descuento > 0, para no ensuciar el caso normal.
- **Validación en vivo**: si `MontoDescuento >= Subtotal`, ambos inputs toman `is-invalid`, el Total muestra "El descuento no puede dejar el total en cero" y el submit se bloquea. El servidor repite el chequeo (PV20).

### 8.3.2 `Egresos/Create` — misma card, versión reducida

Idéntica estructura sin IIBB ni percepciones: `Subtotal → Descuento (% / $) → Neto gravado → IVA (% / $) → Importe total`. El total en vivo sigue escribiéndose en el hidden `#ImporteTotal` (que no postea; el servidor lo recalcula) y la grilla de pagos sigue validando contra él con **tolerancia cero** (RD6/S31 — divergencia deliberada respecto de la tolerancia de $0,01 de los ingresos de factura, ya documentada).

### 8.3.3 Reajuste de ingresos al editar (R1 del usuario)

Hoy `actualizarResumenIngresos(total)` ya muestra en verde/rojo si los ingresos cierran contra el Total. v4 agrega **dos** cosas y no cambia nada más:

1. Junto al mensaje rojo, botón **"Reajustar al nuevo total"**: redistribuye **proporcionalmente** a los importes actuales (`nuevo_i = viejo_i × total_nuevo / total_viejo`), **conservando las fechas de vencimiento**, con el ajuste de centavos en la última fila — misma mecánica de cierre que ya usa `btnGenerarSugerido` (que reparte parejo). Proporcional y no parejo porque conserva el patrón que el usuario armó a mano (S39; era la pregunta abierta menor del análisis y queda resuelta acá).
2. Al enviar una edición cuyo total cambió, confirmación previa SweetAlert2: *"El total pasó de $X a $Y. Los ingresos suman $Z (diferencia $D). ¿Continuar?"* — el "aviso previo" pedido. No se reajusta nunca en silencio (R29).

No existe caso mixto: `PuedeEditarAsync` ya impide editar la factura si algún ingreso está Acreditado o Rechazado, así que todos los ingresos editables son Pendientes. El servidor sigue siendo la autoridad y rechaza si no cierran (PV22).

### 8.3.4 `Dashboard/TableroAnual` — card "IVA de compras y ventas"

Nueva card debajo del gráfico de flujo existente, **clon estructural de `chartMensual`**:

- `chartIva`: 12 barras verdes (**IVA ventas**), 12 rojas (**IVA compras**), línea azul de **saldo IVA** (`ventas − compras`).
- KPI nuevo en la fila superior: **"Saldo IVA del período"**, color según signo, respetando el filtro Año (+ Mes).
- Tabla de desglose mes a mes debajo, mismo patrón que la tabla de flujo.
- **Rótulo obligatorio en la card** (R30/R31), no en un tooltip: *"Base devengado: se imputa por la fecha del comprobante, no por la fecha de cobro o pago — a diferencia del gráfico de arriba, que es caja. Informativo: no es un Libro IVA (no contempla notas de crédito ni percepciones)."*

### 8.3.5 ViewModels y DTOs (delta)

- `FacturaVentaCreateVm` += `PorcentajeDescuento` `[Range(0, 99.99)]`, `MontoDescuento` `[Range(0, double.MaxValue)]`.
- `EgresoCreateVm` += los mismos dos campos; `Total => Subtotal - MontoDescuento + MontoIva`.
- `FacturaVentaCreateInput` y `EgresoCreateInput` (records) += `PorcentajeDescuento`, `MontoDescuento`.
- `TableroAnualMesDto` += `IvaVentas`, `IvaCompras`, `SaldoIva => IvaVentas - IvaCompras`.
- `TableroAnualKpisDto` += `SaldoIvaPeriodo`.

### 8.3.6 Contratos de servicio (delta)

`IDashboardService.GetTableroAnualAsync` **no cambia de firma**. Su implementación agrega dos consultas independientes de caja: `FacturaVenta` no anuladas agrupadas por `Fecha.Month` (Σ `MontoIva`) y `Egreso` no anulados agrupados igual. `IFacturaVentaService` e `IEgresoService` tampoco cambian de firma: sólo crecen sus records de input.

### Aclaraciones v4.1 (bordes que la v4 no cubria, detectados en implementacion)

- **Estado inicial del driver en modo edicion.** §8.3.1 define `impState.desc = 'pct'` para el alta, pero no dice nada de reabrir un comprobante que ya tiene descuento. Ahi debe arrancar en **`'monto'`**: si arrancara en `'pct'`, recalcularia el importe desde un porcentaje redondeado a 4 decimales y podria correrlo unos centavos sin que el usuario toque nada — exactamente lo que RD14 quiere evitar (el importe es la autoridad, el % es derivado).
- **El mensaje rojo de desvio tambien aparece en el alta.** §8.3.3 dice "junto al mensaje rojo, boton Reajustar", lo que leido literal pone el boton tambien en el alta. La condicion correcta es **mensaje rojo Y modo edicion** (RD13/PD15).

### Riesgos de diseño v4

- **RD12** El descuento entra en la base de **todos** los impuestos. Cualquier punto que hoy recomponga totales fuera de la card (PDF del comprobante, `Details`, sumatorias de los listados) debe leer el total **persistido**, no recalcularlo — si recalcula, va a ignorar el descuento.
- **RD13** `Facturas` **no tiene `Edit.cshtml` propio**: la edición reusa `Create.cshtml`. El botón "Reajustar al nuevo total" y la confirmación de cambio de total deben condicionarse a un flag de modo edición en el ViewModel, o el alta va a mostrar un botón que no significa nada.
- **RD14** El % derivado de un importe (`monto / subtotal × 100`) puede dar decimales largos. Se persiste redondeado a 4 decimales, igual que los impuestos, y **la autoridad es el importe** (el % es informativo/derivado). Precisión: `decimal(18,4)` para porcentajes, `decimal(18,2)` para montos.
- **RD15** Facturas y egresos históricos deben quedar en descuento **0, no NULL**, para que sumatorias, PDF y detalle no cambien de comportamiento (PF70).
- **RD16** El gráfico de IVA lee comprobantes, no caja: un mes con facturas emitidas y sin cobrar igual muestra IVA. Es correcto — y es exactamente lo que se malinterpreta si falta el rótulo de §8.3.4.

### Pruebas de diseño v4

- **PD13** `base()` sigue siendo la única función que decide sobre qué base se aplica cada impuesto; el descuento no duplica la fórmula en ningún otro lado del JS.
- **PD14** Descuento ≥ Subtotal: bloqueado en cliente **y** rechazado ante un POST directo que saltee la UI.
- **PD15** El botón de reajuste y la confirmación de cambio de total **no** aparecen en el alta, sólo en edición (RD13).
- **PD16** `GetTableroAnualAsync` no consulta `MovimientosCaja` para las series de IVA (devengado, no caja).
- **PD17** Los `value=` de descuento se emiten con `CultureInfo.InvariantCulture` (LP-003, ya corregido en v13 para el resto de los decimales de estas pantallas).

### Historias de usuario v4

- **HU-D1** — Como Productor, quiero cargar un descuento en una factura de venta indistintamente en % o en importe, para no tener que hacer la cuenta a mano según cómo me lo pasó el comprador.
  *Criterios:* escribir el % completa el importe y viceversa; el último campo tocado manda; ambos se persisten; el detalle muestra los dos.
- **HU-D2** — Como Productor, quiero que el IVA y las percepciones se calculen sobre el total ya descontado, para que la factura refleje lo que realmente voy a cobrar.
  *Criterios:* con Subtotal 1.000.000 y descuento 10%, IVA 21% da 189.000 e IIBB 3% da 32.670 sobre 1.089.000; Total 1.121.670 (PF67, PF69).
- **HU-D3** — Como Productor, quiero que el descuento sea opcional, para que las facturas sin descuento sigan cargándose exactamente igual que antes.
  *Criterios:* el formulario abre con descuento en 0; una factura sin descuento da los mismos totales que antes de v4 (PF70).
- **HU-D4** — Como Productor, quiero que el sistema no me deje dejar el total en cero con un descuento, para no emitir un comprobante sin valor por error de tipeo.
  *Criterios:* descuento ≥ subtotal, % fuera de [0,100) o valores negativos quedan bloqueados en cliente y servidor (PV19–PV21).
- **HU-D5** — Como Productor, quiero cargar un descuento también en las compras a proveedor, para registrar la bonificación que me hace el proveedor antes del IVA.
  *Criterios:* Subtotal 100.000 con 5% da neto 95.000, IVA 19.950 e Importe 114.950; los pagos deben sumar 114.950 (PF71, PV23).
- **HU-D6** — Como Productor, quiero que al editar una factura y cambiar el total el sistema me avise y me ofrezca reajustar las cuotas, para no tener que recalcularlas una por una ni descubrir el desvío recién al guardar.
  *Criterios:* aviso previo con total viejo, total nuevo y diferencia; botón que redistribuye proporcionalmente conservando vencimientos; nunca reajusta solo; el servidor bloquea si no cierran (PF72, PV22).
- **HU-D7** — Como Productor, quiero ver en el Tablero Anual cuánto IVA generaron mis ventas y cuánto mis compras mes a mes, para anticipar mi posición de IVA antes de que me la informe el contador.
  *Criterios:* dos barras por mes más línea de saldo; imputación por fecha de comprobante (una factura de marzo cobrada en mayo suma en marzo); excluye anulados; muestra sólo el IVA de la factura, no el de los pagos; KPI de saldo del período; rótulo visible de base devengado y de "no es un Libro IVA" (PF73–PF76).

---

## 8.4 Diseño v5 — Deducciones de liquidación + compra de hacienda con costo

Sobre el análisis **v14** (§3.11, §3.12, §5.9).

### Escaneo de reutilización cross-proyecto

| Buscado | Dónde | Decisión |
|---|---|---|
| Catálogo de conceptos que **precarga** líneas en un comprobante | `marihogar` (`OrdenCompra` con impuestos por comprobante) y `la-platense` (`ItemVenta` con IVA/descuento por línea) | Ninguno precarga desde catálogo: en los dos el usuario carga el valor a mano. **Patrón nuevo.** |
| Grilla dinámica con recálculo en vivo | **Este proyecto**: `Facturas/Create.cshtml` (ítems, ingresos) y `Egresos/Create.cshtml` (pagos, con el auto-completado de v17.1) | **Reutilización directa**: misma mecánica de agregar/quitar/reindexar `Campo[i]` + driver "último tocado manda". |
| Movimiento de stock vinculado a un comprobante | **Este proyecto**: `MovimientoStock.FacturaVentaId` (venta) | **Reutilización directa y simétrica**: se agrega `EgresoId` con el mismo criterio. |
| Compra que impacta stock y caja a la vez | `marihogar` (`OrdenCompra` → stock + cuenta corriente), `la-platense` (compras con actualización de stock) | Patrón conocido; acá es más simple porque el egreso ya existe y solo falta el vínculo. No se importa código. |

### 8.4.1 Catálogo `Conceptos de deducción` (ABM nuevo, dentro de Catálogos)

Columnas del listado: Nombre · Tipo (Porcentaje / Importe fijo) · Valor · Aplica por defecto · Orden. Alta/edición con las mismas convenciones que los otros ABM (Rubros, Grupos).

Semillas de la migración, tomadas de la liquidación real: **Derecho de Registro 0,350%**, **Imp. Sellos Pcia Bs As 1,050%**, **Ing. Brutos Nómina 42/12 0,750%**, **Guía Municipal** (importe fijo, arranca en 0), las cuatro con *aplica por defecto* activo.

### 8.4.2 `Facturas/Create` — la card de impuestos cambia de forma

```
┌─ Descuento, IVA y deducciones ──────────────────────────────────────┐
│  Subtotal                                        136.253.250,00     │
│  Descuento %  [ 4,00 ]  $ [ 5.450.130,00 ]      [ Sin descuento ]   │
│  Neto gravado                                    130.803.120,00     │
│                                                                      │
│  IVA %  [ 10,50 ]   $ [ 13.734.327,60 ]   sobre Neto gravado        │
│                                                                      │
│  Deducciones (sobre el Subtotal)      [ Agregar deducción  ▼ ]      │
│  ┌────────────────────────────────┬─────────┬──────────────┬───┐    │
│  │ Derecho de Registro            │ 0,3500 %│   476.886,37 │ ✗ │    │
│  │ Imp. Sellos Pcia Bs As         │ 1,0500 %│ 1.430.659,13 │ ✗ │    │
│  │ Ing. Brutos Nómina 42/12       │ 0,7500 %│ 1.021.899,38 │ ✗ │    │
│  │ Guía Municipal                 │       — │   262.000,00 │ ✗ │    │
│  └────────────────────────────────┴─────────┴──────────────┴───┘    │
│                       Total deducciones:      − 3.191.444,88        │
│  ──────────────────────────────────────────────────────────────     │
│  Total                                          141.346.002,72      │
└──────────────────────────────────────────────────────────────────────┘
```

**Base de cálculo (v14.1):** las deducciones porcentuales se aplican sobre el **Subtotal**, no sobre el neto gravado — el IVA es el único que va sobre el neto. Con estos números el total coincide **exactamente** con el importe neto de la liquidación real del cliente.

- La grilla **ya viene cargada** al abrir el alta (conceptos con *aplica por defecto*), con el importe calculado. El usuario no escribe nada en el caso normal.
- El nombre es **texto de solo lectura** en la fila: viene del catálogo. No es un input.
- `%` e importe editables por línea, último tocado manda, igual que IVA y descuento. Una línea de importe fijo tiene el `%` deshabilitado y no se recalcula al cambiar el neto.
- **"Agregar deducción"** es un `<select>` con los conceptos del catálogo que todavía no están en la grilla — no un campo de texto libre.
- El botón de quitar saca la línea; la grilla puede quedar vacía.
- El bloque completo se recalcula cuando cambia el **Subtotal o el descuento**, en la misma pasada de `recalcImpuestos()` (el descuento no entra en la base de las deducciones, pero sí en la del IVA, así que la pasada es una sola).

### 8.4.3 `Stock/Compra` — sección de costo opcional

La pantalla actual (grupo, cantidad, fecha, detalle) gana un bloque **"Costo de la compra (opcional)"** con un check que lo despliega:

```
☑ Registrar el costo de esta compra
   Rubro [ ▼ ]   Proveedor [ ▼ ]
   Subtotal [ ]  Descuento % [ ] $ [ ]  IVA % [ 21 ] $ [ ]
   Total: $ 0,00
   Pagos  [ + Agregar pago ]      (misma grilla que Egresos/Create)
```

Se reutiliza tal cual la partial `_FilaPago.cshtml` y el driver de descuento/IVA/auto-importe ya probado en `Egresos/Create` — **extraído a una partial compartida** para no tener dos copias del mismo JS divergiendo (que es exactamente cómo nació el bug de v15).

Con el check apagado, el POST es idéntico al de hoy y el comportamiento no cambia (PF85).

### 8.4.4 ViewModels y DTOs (delta)

- `ConceptoDeduccionVm` (ABM): `Nombre`, `EsImporteFijo`, `Porcentaje`, `ImporteFijo`, `AplicaPorDefecto`, `Orden`.
- `FacturaVentaCreateVm`: **se quitan** `PorcentajeIIBB`/`MontoIIBB`/`PorcentajeOtrasPercepciones`/`MontoOtrasPercepciones`; **se agrega** `List<DeduccionInputVm> Deducciones` (`ConceptoDeduccionId`, `Nombre`, `Porcentaje`, `Monto`, `EsImporteFijo`).
- `MovimientoStockInputVm` (compra): `+ bool RegistrarCosto`, `+ CostoCompraVm Costo` (rubro, proveedor, subtotal, descuento, IVA, `List<EgresoPagoViewModel> Pagos`).
- `TableroAnualKpisDto` += `ReinvertidoEnHacienda`.

### Riesgos de diseño v5

- **RD17** El nombre de la deducción es snapshot en la factura, no una referencia viva al catálogo. Editar el catálogo no debe tocar facturas emitidas (R33) — y el detalle tiene que leer el snapshot, no el catálogo.
- **RD18** El JS de descuento/IVA/pagos pasa a vivir en dos pantallas (`Egresos/Create` y `Stock/Compra`). Si se copia y pega en vez de compartirse, se repite el bug de v15. **Extraer a partial/JS compartido es parte del alcance, no una mejora opcional.**
- **RD19** Con el check de costo apagado, el binder igual recibe el sub-objeto `Costo` vacío: las validaciones `[Required]` de rubro/proveedor no pueden ser de atributo, tienen que ser condicionales en servidor (PV28).
- **RD20** La grilla de deducciones se precarga en el **GET**. Si el POST falla por validación, la vista se re-renderiza con lo que mandó el usuario, **no** con la precarga del catálogo, o se le pisan las líneas que había quitado.

### Pruebas de diseño v5

- **PD18** El nombre de la deducción se renderiza como texto, nunca como input editable.
- **PD19** El JS de costo/pagos existe una sola vez en el repositorio y lo consumen las dos pantallas (RD18).
- **PD20** Con el check de costo apagado no se emite ningún campo `Costo.*` que el servidor deba ignorar a mano.
- **PD21** Al volver de una validación fallida, la grilla de deducciones conserva exactamente las líneas que el usuario tenía (RD20).

### Historias de usuario v5

- **HU-D8** — Como Productor, quiero que las deducciones de la liquidación se resten del total, para no tener que cargar importes negativos para que la cuenta cierre.
- **HU-D9** — Como Productor, quiero que las deducciones habituales ya vengan cargadas con su porcentaje, para no escribir el mismo nombre y el mismo importe en cada factura.
- **HU-D10** — Como Productor, quiero configurar una vez los conceptos de deducción, para que el sistema se adapte cuando cambie una alícuota.
- **HU-D11** — Como Productor, quiero registrar la compra de terneras con su costo en un solo paso, para que quede el stock y el egreso sin cargarlos dos veces.
- **HU-D12** — Como Productor, quiero ver cuánto reinvertí en hacienda en el año, para saber cuánta plata volvió al rodeo.

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
- [ ] **(v4)** Riesgos RD12–RD16 y pruebas PD13–PD17 agregados al plan; escaneo de reutilización cross-proyecto documentado (§8.3).

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
- **v4** — A partir del análisis funcional v13 (§8.3): **descuento comercial opcional** en Facturas de venta y Egresos, cargable en % o importe, aplicado sobre el Subtotal para dar un **neto gravado** sobre el que se calculan todos los impuestos (IVA, IIBB y percepciones en ventas; IVA en egresos) — resuelto extendiendo el driver `impState` ya existente con un grupo `desc` y cambiando **una sola función** (`base()`). **Reajuste proporcional de ingresos** al editar una factura cuyo total cambia, con aviso previo (resuelve la pregunta abierta S39: proporcional, no parejo). **Gráfico de IVA compras vs. ventas** en el Tablero Anual, clon estructural de `chartMensual`, base devengado por fecha de comprobante, con rótulo explícito de base contable y de "no es un Libro IVA". Escaneo de reutilización cross-proyecto: layout tomado de ShowroomGriffin, lección de modelado de la-platense, mecánica reutilizada del propio proyecto (v13/v15). Agregados RD12–RD16, PD13–PD17, HU-D1–HU-D7.
- **v5** — A partir del análisis v14 (§8.4): **catálogo de conceptos de deducción** + grilla que se **precarga sola** en la factura con los importes ya calculados (el usuario no escribe nombre ni importe), reemplazando los campos `IIBB` y `Otras percepciones`, que en este negocio son deducciones y no percepciones. **`Stock/Compra` con costo opcional** que genera el egreso real con pagos, vinculado al movimiento, reutilizando el bloque de descuento/IVA/pagos de `Egresos/Create` **extraído a una partial compartida** (RD18: copiarlo es repetir el bug de v15). Agregados RD17–RD20, PD18–PD21, HU-D8–HU-D12.
