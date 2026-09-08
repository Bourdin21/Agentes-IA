# Memoria - Arquitecto MVC

## Proyecto: delicias-naturales
## Ultima actualizacion: 2026-06-XX

---

# ITERACION 2: Devolucion cliente — Mejoras modulo Solicitudes de Ingreso de Stock

## Estado: APROBADO — listo para presupuesto

---

## Nota de arquitectura base

El proyecto DeliciasNaturales es ASP.NET MVC 5 / EF6 / .NET Framework 4.7.2, arquitectura monolitica en capas logicas (no proyectos separados). Las capas se mapean asi:

| Capa logica | Carpetas fisicas |
|---|---|
| Domain | `Models/` (entidades EF, enums, SoftDestroyable) |
| Application / Negocio | `Services/` (logica de negocio) |
| Infrastructure / Datos | `Models/` DbContext, `Migrations/` |
| Web / Presentacion | `Controllers/`, `ViewModels/`, `Views/`, `Helper/` |

---

## 1. Alcance funcional resumido

Seis mejoras sobre el modulo Solicitudes de Ingreso de Stock implementado en la iteracion 1:

| # | Mejora | Capa principal afectada |
|---|---|---|
| 1 | Modo de stock al aprobar ítem: PISAR o SUMAR | Services + Controllers + Views |
| 2 | Admin hace el flujo completo (crea con cantidades) | Controllers + Views + Services |
| 3 | Vendedor accede al modulo (crea sin cantidades) | Controllers + Views |
| 4 | Deposito crea en estado VerificadoDeposito con cantidades | Controllers + Views + Services |
| 5 | FechaActualizacionStock en Producto + badge desactualizado | Models + Migrations + Views |
| 6 | Tarjeta Ingreso de Stock en Home para Admin | Views |

---

## 2. Impacto tecnico por capa

### 2.1 Domain — Models

#### Entidad: `Producto` (modificacion)
- Agregar propiedad: `public DateTime? FechaActualizacionStock { get; set; }`
- Columna DB: `fecha_actualizacion_stock DATETIME NULL`
- No afecta logica existente (nullable, sin valor default).

#### Entidad: `SolicitudIngresoStock` (sin cambios estructurales)
- El estado inicial ya tiene los valores necesarios (`Pendiente`, `VerificadoDeposito`).
- No se agrega ninguna propiedad nueva al modelo.

#### Entidad: `SolicitudIngresoStockDetalle` (sin cambios estructurales)
- Los estados de item existentes cubren el flujo nuevo.
- No se agrega ninguna propiedad nueva al modelo.

#### Enums (sin cambios)
- `EstadoSolicitudIngreso` y `EstadoDetalleIngreso` ya contemplan todos los estados requeridos.

---

### 2.2 Application / Negocio — Services

#### `SolicitudIngresoStockService` — cambios en metodos existentes

**`CrearSolicitud` (firma extendida)**
- Parametros actuales: `SolicitudIngresoStock solicitud`
- Parametros nuevos: `bool esCreacionConCantidades`
- Logica nueva:
  - Si `esCreacionConCantidades == true`: cada item se crea con `EstadoDetalle = VerificadoDeposito`; la cabecera se inicia en `VerificadoDeposito`.
  - Si `esCreacionConCantidades == false` (Vendedor): cada item con `EstadoDetalle = Pendiente`; cabecera en `Pendiente` (comportamiento actual).
- Precondicion: si `esCreacionConCantidades == true`, todos los items deben tener `Cantidad > 0`. Validar en Service, no en Controller.

**`AprobarItem` (firma extendida)**
- Parametros actuales: `int detalleId`
- Parametros nuevos: `string modoStock` ("pisar" | "sumar")
- Logica nueva:
  - Si `modoStock == "pisar"`: `producto.StockActual = detalle.Cantidad` (comportamiento anterior)
  - Si `modoStock == "sumar"`: `producto.StockActual = (producto.StockActual ?? 0) + detalle.Cantidad`
  - Siempre: `producto.FechaActualizacionStock = DateTime.Now`
- Validacion: si `modoStock` no es "pisar" ni "sumar" → `InvalidOperationException`.

**`ObtenerSolicitud` — sin cambios en firma**
- El ViewModel que construye el Controller ya puede calcular `StockActual` desde el producto.

---

### 2.3 Infrastructure / Datos — DbContext y Migraciones

#### DbContext
- Sin cambios en `DbSet`. El `DbSet<Productos>` ya existe.
- La nueva columna se agrega via migracion EF (EF6 Code First).

#### Migracion EF requerida: **SI — 1 migracion**

| Migracion | Descripcion | Tabla | Operacion |
|---|---|---|---|
| `AddFechaActualizacionStockToProducto` | Agrega columna de fecha de actualizacion de stock | `productos` | `AddColumn("productos", "fecha_actualizacion_stock", c => c.DateTime(nullable: true))` |

- Migracion nullable → no rompe datos existentes.
- Los productos existentes quedan con `NULL` → aparecen como desactualizados hasta la primera solicitud aprobada. Comportamiento esperado y documentado.

---

### 2.4 Web / Presentacion — Controllers, ViewModels, Views

#### `SolicitudesIngresoStockController` — cambios

**Attribute `[Authorize]` en nivel de clase/acciones:**

| Accion | Autorizacion actual | Autorizacion nueva |
|---|---|---|
| `Index` | `AdministradorRol, DepositoRol` | `AdministradorRol, DepositoRol, VendedorRol` |
| `Create GET` | `AdministradorRol` | `AdministradorRol, DepositoRol, VendedorRol` |
| `Create POST` | `AdministradorRol` | `AdministradorRol, DepositoRol, VendedorRol` |
| `Details` | sin restriccion de rol | `AdministradorRol, DepositoRol, VendedorRol` (con validacion de propiedad para no-Admin) |
| `GuardarCantidad` | `AdministradorRol, DepositoRol` | `AdministradorRol, DepositoRol, VendedorRol` |
| `AprobarItem` | `AdministradorRol` | sin cambio |
| `RechazarItem` | `AdministradorRol` | sin cambio |
| `Cancelar` | `AdministradorRol` | sin cambio |

**Accion `Index`:**
- Si `User.IsInRole(AdministradorRol)`: sin filtro (ve todas las solicitudes).
- Si `User.IsInRole(DepositoRol)` o `User.IsInRole(VendedorRol)`: filtrar por `UsuarioId == currentUserId` (ven solo las propias).
- Reutilizar la query existente, agregar `.Where()` condicional.

**Accion `Create POST`:**
- `esCreacionConCantidades = true` para Admin, Deposito y Vendedor (los tres pueden crear con cantidades).
- Todos los roles crean en estado `VerificadoDeposito` con cantidades cargadas.
- Pasar flag al service.

**Accion `AprobarItem` (AJAX POST):**
- Recibir parametro adicional: `string modoStock`.
- Validar que no sea null/empty antes de invocar el service.
- Pasar al service.

**SetViewBag:**
- Sin cambios (los productos ya se pasan con categorias).
- No se necesita flag de rol para ocultar cantidad: todos los roles (Admin, Deposito, Vendedor) ven y cargan cantidad al crear.

#### ViewModels — cambios

**`SolicitudIngresoStockDetalleVM` (usado en Create)**
- Agregar `string NombreProducto` para mostrar en tabla de confirmacion (opcional, ya se puede resolver con ViewBag).

**`SolicitudIngresoStockDetalleDetalleVM` (usado en Details)**
- Agregar `decimal? StockActual` → pasado desde el producto para calcular el preview del modal.

**`SolicitudIngresoStockIndexViewModel`**
- Sin cambios estructurales. El filtro por usuario se aplica en el Controller antes de mapear.

#### Views — cambios

**`Create.cshtml`:**
- Agregar banner contextual por rol (texto diferenciado para Admin vs Deposito/Vendedor).
- Columna "Cantidad" visible para todos los roles (Admin, Deposito, Vendedor).
- Todos crean en estado `VerificadoDeposito`; el admin luego aprueba/rechaza cada item.

**`Details.cshtml`:**
- Reemplazar `confirm()` nativo del boton Aprobar por modal Bootstrap con:
  - Nombre del producto, cantidad ingresada, stock actual (desde `StockActual` del ViewModel).
  - Dos radio buttons: "Pisar stock" (default) / "Sumar al stock actual".
  - Calculo de preview en JS (sin llamada al servidor).
  - Boton confirmar envia AJAX con `{ detalleId, modoStock }`.
- Mantener SweetAlert2 existente para otras acciones (rechazar, cancelar).

**`Index.cshtml`:**
- Sin cambios estructurales. El filtro por Vendedor se aplica en el Controller.

**`Views/Home/Index.cshtml`:**
- Agregar tarjeta "Ingreso de Stock" dentro del bloque `@if (User.IsInRole(AdministradorRol))`.
- Icono: `fas fa-warehouse`, color: `text-secondary`, boton: `btn-outline-secondary`.

**`Views/Productos/Index.cshtml` (o equivalente):**
- Agregar columna "Stock" con badge `✅ Actualizado` / `⚠️ Desactualizado` segun `FechaActualizacionStock`.
- Logica de calculo: comparar en el Controller/ViewModel al mapear (no en la vista).
- Agregar propiedad calculada `EstaDesactualizado` al ViewModel de Productos si no existe.

---

## 3. Modelo de permisos (roles/claims/policies)

| Accion | AdministradorRol | DepositoRol | VendedorRol | ClienteRol |
|---|---|---|---|---|
| Ver listado de solicitudes | ✅ (todas) | ✅ (solo las propias) | ✅ (solo las propias) | ❌ |
| Crear solicitud (sin cantidades) | ✅ | ✅ | ✅ | ❌ |
| Crear solicitud (con cantidades) | ✅ | ✅ | ✅ | ❌ |
| Ver detalle de solicitud | ✅ | ✅ (solo las propias) | ✅ (solo las propias) | ❌ |
| Guardar cantidad de item | ✅ | ✅ | ✅ | ❌ |
| Aprobar item (con modoStock) | ✅ | ❌ | ❌ | ❌ |
| Rechazar item | ✅ | ❌ | ❌ | ❌ |
| Cancelar solicitud | ✅ | ❌ | ❌ | ❌ |

**Cambios respecto a la iteracion 1:**
- VendedorRol agregado a Create, Index, Details y GuardarCantidad con los mismos permisos que DepositoRol.
- Index filtra por UsuarioId para Deposito y Vendedor (ambos ven solo las propias).
- Deposito deja de ver TODAS las solicitudes: pasa a ver solo las propias, igual que Vendedor.
- No se crean roles nuevos; se reutilizan los existentes en `Constantes.cs`.

---

## 4. Migraciones EF requeridas

| # | Migracion | SI/NO | Detalle |
|---|---|---|---|
| 1 | `AddFechaActualizacionStockToProducto` | **SI** | ADD COLUMN `fecha_actualizacion_stock DATETIME NULL` en tabla `productos` |

- Una sola migracion. No hay cambios en tablas de solicitudes ni detalles.
- La columna es nullable: no requiere data migration ni default value.
- Riesgo de migracion: bajo.

---

## 5. Riesgos y supuestos

| # | Riesgo / Supuesto | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|---|
| R1 | Modo "sumar" genera stock incorrecto si el operador no entiende el contexto | Media | Alto (dato de negocio) | Modal con preview calculado antes de confirmar; default = pisar |
| R2 | Productos existentes con `FechaActualizacionStock = NULL` aparecen todos como desactualizados al deploy | Alta (certeza) | Bajo operativo | Comportamiento esperado y documentado; se normaliza con el uso |
| R3 | Deposito o Vendedor accede a Details de solicitudes ajenas (si conoce el ID) | Media | Medio seguridad | Agregar validacion en Details: si es Deposito o Vendedor y `solicitud.UsuarioId != currentUserId` → 403 |
| R4 | La firma extendida de `CrearSolicitud` puede romper si hay otras instancias de invocacion | Baja | Medio | Verificar todos los call sites antes de implementar; hay una sola invocacion en el Controller |
| R5 | La firma extendida de `AprobarItem` rompe el AJAX existente en Details | Baja | Medio | El parametro es nuevo; si no se envia retorna error descriptivo, no excepcion silenciosa |
| S1 | Se asume que `SweetAlert2` ya esta incluido en el bundle del proyecto | — | — | Verificado: se usa en otros modulos del proyecto |
| S2 | Se asume que `VendedorRol` ya existe como rol en la DB (ya esta en Constantes.cs) | — | — | Verificado: `Constantes.VendedorRol = "Vendedor"` existe |

---

## 6. Componentes reutilizados (sin crear piezas nuevas)

| Componente | Reutilizacion |
|---|---|
| `SolicitudIngresoStockService` | Extender metodos existentes, no crear un nuevo service |
| `Constantes.VendedorRol` | Ya existe, solo agregarlo a los atributos `[Authorize]` |
| SweetAlert2 | Ya esta en el bundle; usar para el modal de aprobacion |
| `NotificationService.NotifySolicitudIngresoCreada` | Ya existe; reutilizar para notificar al admin cuando crea un Vendedor |
| `SetViewBag()` en el Controller | Extender con flags de rol, no duplicar |
| `AvanzarASiCorresponde` en Service | Sin cambios; la logica de avance de cabecera no cambia |

---

## 7. Validacion de maquina de estados

La arquitectura propuesta es soportable por la maquina de estados definida en el diseño:

| Transicion | Soportada | Mecanismo |
|---|---|---|
| (nueva) → Pendiente (Vendedor) | ✅ | `esCreacionConCantidades = false` → `EstadoDetalle.Pendiente` |
| (nueva) → VerificadoDeposito (Admin/Deposito) | ✅ | `esCreacionConCantidades = true` → `EstadoDetalle.VerificadoDeposito` + cabecera `VerificadoDeposito` |
| Pendiente → VerificadoDeposito via GuardarCantidad | ✅ | Sin cambios respecto a iteracion 1 |
| VerificadoDeposito → Aprobado/Rechazado con modoStock | ✅ | Parametro `modoStock` en `AprobarItem` |
| Cualquier estado → Cancelada (Admin) | ✅ | Sin cambios |
| Verificada → (terminal) | ✅ | Sin cambios |

---

## 8. Plan de implementacion por etapas

| Etapa | Descripcion | Archivos afectados | Migracion EF | Riesgo |
|---|---|---|---|---|
| 1 | Agregar `FechaActualizacionStock` a `Producto` + migracion | `Producto.cs`, nueva migracion | **SI** | Bajo |
| 2 | Extender `AprobarItem` en Service con `modoStock` + actualizar fecha | `SolicitudIngresoStockService.cs` | No | Bajo |
| 3 | Extender `AprobarItem` en Controller (parametro AJAX) + `StockActual` en ViewModel | `SolicitudesIngresoStockController.cs`, `SolicitudIngresoStockViewModels.cs` | No | Bajo |
| 4 | Modal de aprobacion en Details (reemplazar confirm nativo) | `Details.cshtml` | No | Medio (UI) |
| 5 | Extender `CrearSolicitud` en Service con `esCreacionConCantidades` | `SolicitudIngresoStockService.cs` | No | Bajo |
| 6 | Extender Create (Controller + View) para todos los roles con cantidades; banner contextual | `SolicitudesIngresoStockController.cs`, `Create.cshtml`, ViewModels | No | Medio (UI) |
| 7 | Habilitar VendedorRol en Index, Create, Details y GuardarCantidad; filtrar Index por usuario para Deposito y Vendedor | `SolicitudesIngresoStockController.cs`, `Index.cshtml` | No | Bajo |
| 8 | Badge desactualizado en Productos | ViewModel Productos, `Productos/Index.cshtml` o equivalente | No | Bajo |
| 9 | Tarjeta Ingreso de Stock en Home para Admin | `Home/Index.cshtml` | No | Bajo |

---

## 9. Gate de aprobacion para pasar a presupuesto

Prerequisitos para avanzar a la etapa de presupuesto:

- [x] Diseño funcional aprobado (2-disenador-funcional.md)
- [x] Maquina de estados validada por arquitectura
- [x] Una sola migracion EF identificada (bajo riesgo)
- [x] Cero roles nuevos requeridos (reutiliza VendedorRol existente)
- [x] Cero servicios nuevos requeridos (extiende los existentes)
- [x] Riesgos identificados y con mitigacion definida
- [x] Componentes reutilizados documentados
- [x] Plan de implementacion por etapas definido

**Estado del gate: ✅ APROBADO para presupuesto**

---

## Componentes por capa — resumen

### Models (Domain)
- `Producto`: agregar `FechaActualizacionStock DateTime?`

### Services (Application/Negocio)
- `SolicitudIngresoStockService.CrearSolicitud`: agregar parametro `bool esCreacionConCantidades`
- `SolicitudIngresoStockService.AprobarItem`: agregar parametro `string modoStock`; actualizar `FechaActualizacionStock`

### Migrations (Infrastructure)
- Nueva migracion: `AddFechaActualizacionStockToProducto`

### Controllers (Web)
- `SolicitudesIngresoStockController`: ampliar `[Authorize]` en Index/Create; filtrar Index por Vendedor; pasar `modoStock` a AprobarItem; pasar `esCreacionConCantidades` a CrearSolicitud; agregar flags al ViewBag

### ViewModels (Web)
- `SolicitudIngresoStockDetalleDetalleVM`: agregar `StockActual decimal?`

### Views (Web)
- `Create.cshtml`: banner contextual + columna cantidad condicional
- `Details.cshtml`: modal Bootstrap con selector pisar/sumar + preview JS
- `Home/Index.cshtml`: tarjeta Ingreso de Stock en bloque Admin
- `Productos/Index.cshtml` (o equivalente): badge stock desactualizado

---

# ITERACION 3: Editar Pago (ex "Ajuste directo de un Pago")

## Estado: DEPLOYADO A PRODUCCION (2026-09-07) — iteracion cerrada

## 0. Resultado del escaneo de reutilizacion cross-proyecto
- `docs/*/definiciones/{3-arquitecto-mvc,5-implementador}.md`: no hay un componente identico ("editar pago con reversion+alta") ya construido en otro proyecto, pero SI hay un patron arquitectonico directamente trasladable: **marihogar** (`VentaService.CancelarAsync`/`EliminarPagoAsync`) y **ganaderia** (`EgresoService.AnularAsync`, `EgresoPagoService`) implementan la logica de reversion de movimientos financieros **en un Service dedicado**, nunca en el Controller — arquitectura por capas real (Domain/Application/Infrastructure/Web separados).
- **Decision de arquitectura:** delicias-naturales es un monolito MVC5/EF6 SIN esa separacion formal (no hay proyectos Domain/Application/Infrastructure, solo carpetas logicas — ver "Nota de arquitectura base" arriba). Controllers como `PagosController`/`VentasController`/`FacturasController` hoy tienen la logica de negocio directamente en el Controller (viola la regla global "logica de negocio en Services", pero es el patron establecido en TODO el modulo de Ventas/Pagos/Facturas de este proyecto). Ya existe, sin embargo, un `Services/` folder usado por otros modulos (`StockService`, `SolicitudIngresoStockService`, `RecetaService`). **Se decide crear `Services/PagoService.cs`** para esta feature — es la logica nueva mas compleja que va a tener `PagosController` hasta ahora (reversion + alta atomica, reutilizada 2 veces), y es el punto exacto donde alinear el proyecto con el patron cross-proyecto (PagoService ~ VentaService/EgresoPagoService) sin tener que refactorizar TODO el controller de una vez.
- **Alcance del refactor, acotado a proposito:** `PagoService` va a exponer 2 metodos extraidos, verbatim (sin cambiar su logica), de lo que hoy vive inline en `PagosController`:
  - `ReversarPago(Pago pago)` — el bloque de reversion que hoy esta duplicado conceptualmente entre `EliminarPago` y (lo que seria) el ajuste: buscar/eliminar `MovimientoCaja` y `MovimientoCuentaCorriente` vinculados.
  - `RegistrarPagoInterno(Venta venta, decimal monto, MetodoPago metodoPago, DateTime fecha, string usuarioId, string observacion, int? pagoAnteriorId)` — el bloque de alta que hoy esta en `RegistrarPago` (validaciones de sobrepago/SaldoFavor, creacion de `Pago`+`MovimientoCaja`+`MovimientoCuentaCorriente` segun corresponda).
  - `EliminarPago`/`RegistrarPago` (Controller, ya existentes) se refactorizan para LLAMAR a estos metodos en vez de duplicar la logica — mismo comportamiento, codigo compartido real, no una copia paralela para el caso nuevo. `EditarPago` (nuevo) los invoca en secuencia.
  - Fuera de alcance: extraer TODO `PagosController` a Services (permisos, guardas de estado de Venta, manejo de `TempData`/`Json` quedan en el Controller, como en el resto del proyecto).

## 1. Mapa de componentes
| Componente | Tipo | Accion |
|---|---|---|
| `Services/PagoService.cs` | Nuevo | `ReversarPago`, `RegistrarPagoInterno`, `EditarPago` (orquesta los 2 anteriores + guardas) |
| `Controllers/PagosController.cs` | Modificado | Nueva accion `EditarPago` (thin, delega a `PagoService`); `RegistrarPago`/`EliminarPago` refactorizados para usar `PagoService`; **se elimina** `ActualizarFechaPago` |
| `Models/Pago.cs` | Modificado | + `UsuarioId` (string?, FK `AspNetUsers`), `Observacion` (string?), `PagoAnteriorId` (int?, self-FK) |
| `Models/MovimientoCaja.cs` | Modificado | + `PagoId` (int?, FK `pagos.Id`) — cierra el riesgo #1 de Diseño |
| Migracion EF | Nueva | `AddCamposEdicionAPago` (o 2 migraciones separadas, ver seccion 3) |
| `Views/Ventas/Details.cshtml` / `Edit.cshtml` | Modificado | Boton unico "Editar pago" (reemplaza "Editar fecha"); modal; render de cadena de pagos reemplazados |
| `Scripts/js/ventas.js` o script inline | Modificado | Handler del modal, AJAX a `EditarPago`, se retira el handler de `editarFechaPago` |

## 2. Desglose por capa

### Datos (Models + Migrations)
- `Pago`: 3 columnas nuevas, todas nullable — no rompe los ~15.000+ pagos historicos.
- `MovimientoCaja`: 1 columna nueva `PagoId` (int?, nullable) — tambien sin impacto en historicos (quedan `NULL`, la busqueda por `VentaId+Monto` se mantiene como fallback exclusivamente para movimientos con `PagoId == null`).
- `RegistrarPagoInterno` (nuevo, dentro de `PagoService`) setea `MovimientoCaja.PagoId = pago.Id` en toda alta nueva a partir de esta iteracion (incluye pagos creados por `RegistrarPago` normal, no solo por `EditarPago`) — asi el fix cubre TODOS los pagos nuevos, no solo los editados.
- Migracion EF: **2 ADD COLUMN nullable**, sin backfill de datos, sin default value. Riesgo bajo.

### Negocio (Services)
- `PagoService.ReversarPago(Pago pago)`:
  1. Buscar `MovimientoCaja` por `PagoId == pago.Id` (nuevo, exacto); si no hay ninguno con esa FK (pago historico anterior a la migracion), fallback a la busqueda actual por `VentaId+Monto+no eliminado` (comportamiento preexistente, sin cambios).
  2. Soft-delete el/los movimiento(s) de caja encontrados.
  3. Soft-delete todos los `MovimientoCuentaCorriente` con `PagoId == pago.Id` (esto YA es exacto hoy, `MovimientoCuentaCorriente.PagoId` existe desde antes).
- `PagoService.RegistrarPagoInterno(...)`: el cuerpo de `RegistrarPago` extraido tal cual (mismas validaciones de sobrepago/SaldoFavor), parametrizado para aceptar `UsuarioId`/`Observacion`/`PagoAnteriorId` opcionales (null en el alta normal via `RegistrarPago`, seteados en el alta via `EditarPago`).
- `PagoService.EditarPago(pagoId, nuevaFecha, nuevoMonto, nuevoMetodoPago, motivo, usuarioId)`:
  1. Cargar el pago viejo (`Include(Venta)`); si no existe, esta eliminado, o ya fue reemplazado (`db.Pagos.Any(p => p.PagoAnteriorId == pagoId)`) → excepcion de negocio explicita.
  2. `ReversarPago(pagoViejo)`.
  3. Soft-delete `pagoViejo`.
  4. `RegistrarPagoInterno(venta, nuevoMonto, nuevoMetodoPago, nuevaFecha, usuarioId, motivo, pagoAnteriorId: pagoId)` — la relectura de `montoRestante`/`saldoDisponible` ocurre DENTRO de este metodo, ya sobre el estado post-reversion.
- `PagosController.EditarPago` (Web): `[Authorize(Roles = "Administrador,Vendedor")]`, `[HttpPost]`, abre `lock (_registrarPagoLock)` + `using (var tx = db.Database.BeginTransaction())` (mismo patron que las acciones existentes) y llama a `PagoService.EditarPago(...)` adentro; traduce excepciones de negocio a la respuesta JSON `{ mensaje, tipoMensaje }` ya estandar del controller.
- `RegistrarPago`/`EliminarPago` (Web, refactorizados): pasan a llamar `PagoService.RegistrarPagoInterno`/`PagoService.ReversarPago` respectivamente, conservando el resto de su cuerpo (guardas de estado de Venta, lock, transaccion, JSON) sin cambios de comportamiento.

### Presentacion (Web)
- `Views/Ventas/Details.cshtml`/`Edit.cshtml`: quitar boton+JS de "Editar fecha"; agregar boton "Editar pago" + modal (Fecha/Monto/Metodo/Motivo) sobre cada fila de pago vigente (no reemplazado); render de la cadena de pagos (`PagoAnteriorId`) tachados con tooltip de motivo.
- ViewModel de pagos de la Venta (proyeccion usada en la vista, hoy inline en el controller de Ventas o en un ViewModel dedicado — verificar en Implementacion): agregar `Observacion`, nombre de usuario editor, y el pago enlazado (`PagoAnteriorId` resuelto a objeto o al menos a Id+datos minimos para el tooltip).

## 3. Cambios de datos y migraciones
| # | Migracion | Tabla | Operacion | Riesgo |
|---|---|---|---|---|
| 1 | `AddCamposEdicionAPago` | `pagos` | `AddColumn("UsuarioId", string, nullable)`, `AddColumn("Observacion", string, nullable)`, `AddColumn("PagoAnteriorId", int, nullable)` + FK a `pagos.Id` (self) y a `AspNetUsers.Id` | Bajo — todas nullable, sin backfill |
| 2 | `AddPagoIdAMovimientoCaja` | `movimientoscaja` | `AddColumn("PagoId", int, nullable)` + FK a `pagos.Id` | Bajo — nullable, sin backfill; los movimientos historicos quedan `NULL` y siguen resolviendose por el fallback `VentaId+Monto` |

Ambas se pueden aplicar como una sola migracion EF si el Implementador lo prefiere (mismo commit, mismo riesgo) — se separan aca solo para dejar explicito que son 2 tablas distintas.

## 4. Riesgos tecnicos
| # | Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|---|
| T1 | Refactorizar `RegistrarPago`/`EliminarPago` para llamar a `PagoService` en vez de su logica inline puede introducir una regresion sutil en codigo YA hardeneado este mismo ciclo (`_registrarPagoLock`, fixes de cuenta corriente) | Media | Alto (es codigo financiero en produccion, ya tuvo 2 incidentes reales este ciclo — venta 9444 y la carrera de `montoRestante`) | Extraer el codigo LITERAL (copy-paste a un metodo, no reescribir "mejorandolo" de paso) y correr los mismos escenarios que ya se verificaron manualmente para `RegistrarPago`/`EliminarPago` en QA antes de dar por cerrado el refactor |
| T2 | El lock `_registrarPagoLock` debe envolver **todo** `EditarPago` (reversion + alta), no solo la llamada a `RegistrarPagoInterno` — si el Controller abre el lock DESPUES de `ReversarPago`, se reintroduce la carrera que motivo el lock originalmente | Baja si se sigue el diseño; Alta si se omite | Alto | El lock se abre en el Controller ANTES de llamar a `PagoService.EditarPago` completo (reversion+alta adentro), igual que ya lo hace `RegistrarPago` hoy |
| T3 | `MovimientoCaja.PagoId` nuevo requiere que `RegistrarPagoInterno` lo setee en TODA alta (no solo en ediciones) para que el fallback por Monto deje de ser necesario con el tiempo — si se omite en algun call site nuevo a futuro, el problema persiste silenciosamente | Baja | Medio | Centralizado en un unico metodo (`RegistrarPagoInterno`) que es el UNICO lugar donde se crea un `Pago`+`MovimientoCaja` de aca en adelante — no hay otro call site que pueda "olvidarlo" |
| T4 | Migracion EF con 2 FKs nuevas (self-FK en `pagos`, FK en `movimientoscaja`) sobre tablas con miles de filas historicas en produccion (MySQL, EF6, provider ya conocido como fragil con operaciones complejas) | Baja (son ADD COLUMN simples, no joins ni recalculos) | Medio si falla en produccion | Probar la migracion contra una copia/dump de produccion antes de aplicarla en vivo (mismo criterio ya usado en otras migraciones de este proyecto este ciclo) |
| T5 | Impacto en otros lugares que leen `Pago` y no conocen los campos nuevos (regla `26-checklists` #6, LP-002): `PagosController.Index`/`ListarPagos`/`ExportarExcel`, Dashboard, y cualquier reporte que ya liste pagos, deben decidir si muestran o no `Observacion`/el vinculo de edicion — al menos no deben romperse por los campos nuevos | Media (facil de olvidar un listado) | Bajo (visual, no funcional) | Grep de todos los usos de `Pago` en Controllers/Views antes de cerrar Implementacion; si se decide no mostrarlo en algun listado, dejarlo explicito como pendiente en `trazabilidad.md` (no un olvido silencioso) |

## 5. Estrategia de pruebas funcionales
1. **Regresion de lo existente** (critico dado T1): `RegistrarPago` normal (todos los metodos de pago incluido SaldoFavor con sobrepago/subpago) y `EliminarPago` (con y sin movimiento de cuenta corriente asociado) deben comportarse EXACTAMENTE igual que hoy despues del refactor a `PagoService`.
2. **HU1/HU6/HU7 (`EditarPago`)**: editar solo fecha, solo monto, solo metodo, y combinaciones, verificando en cada caso: pago viejo soft-deleted, pago nuevo con `PagoAnteriorId` correcto, `MovimientoCaja` referenciando el pago nuevo via `PagoId`, `MovimientoCuentaCorriente` reversado/recreado si aplicaba.
3. **HU2**: UI muestra la cadena completa (probar 2+ ediciones sucesivas sobre el mismo pago original).
4. **HU3**: intento sin motivo (UI y request directo) rechazado.
5. **HU4**: editar un pago de una Venta Facturada no dispara cambios en `Factura`/`ProductosVenta`/`Venta.Estado`.
6. **HU5**: intento de editar un pago ya reemplazado (via UI oculta el boton; via request directo al Controller) rechazado con error explicito.
7. **Concurrencia (T2)**: 2 requests simultaneas de `EditarPago`/`RegistrarPago` sobre la misma venta no deben poder leer el mismo `montoRestante` "viejo" (mismo test que ya se penso para el lock original).
8. **Caso SaldoFavor cruzado**: editar el Metodo de un pago normal HACIA SaldoFavor (debe validar `saldoDisponible`) y editar un pago SaldoFavor HACIA otro metodo (debe re-acreditar el debito original).
9. **Migracion**: aplicar contra copia de produccion, verificar que pagos/movimientos historicos siguen visibles y sin cambios de valor tras la migracion (solo columnas nuevas en `NULL`).

## Historial de ajustes
- 2026-06-XX: Creacion. Arquitectura iteracion 2 modulo Solicitudes de Ingreso de Stock. Diseno aprobado, gate de presupuesto OK.
- 2026-09-07: Arquitectura iteracion 3 "Editar Pago" — se decide extraer `Services/PagoService.cs` (alineado con el patron cross-proyecto VentaService/EgresoPagoService de marihogar/ganaderia, refactor acotado: solo la logica de reversion+alta de Pago, no todo el Controller). Se decide ademas agregar `MovimientoCaja.PagoId` (cierra el riesgo #1 marcado en Diseño, ahora mas relevante porque toda edicion de pago pasa por reversion). 2 migraciones EF (o 1 combinada), 5 riesgos tecnicos identificados (T1 regresion por refactor es el de mayor cuidado), estrategia de pruebas de 9 puntos. Gate de presupuesto habilitado.
