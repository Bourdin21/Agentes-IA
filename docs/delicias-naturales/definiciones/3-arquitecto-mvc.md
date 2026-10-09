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

# ITERACION 4: Agrupar por categoria en modal "Stock bajo"

## Estado: APROBADO — presupuesto salteado (deuda tecnica/UI menor, mismo criterio ya usado en iteraciones previas de este ciclo)

## 0. Escaneo de reutilizacion
Sin componente equivalente en otros proyectos (ver Diseño §0).

## 1-4. Mapa de componentes / capas / migraciones / riesgos
- Presentacion unicamente: `Views/Productos/Index.cshtml` (agrupado GroupBy + select de categoria + JS de filtrado combinado) y `Controllers/ProductosController.cs` (agregar `.Include(p => p.Categoria)` a la query de `productosBajoMinimo`, unico gap tecnico real).
- Datos: sin cambios, sin migracion.
- Negocio: sin cambios, no hay logica nueva (agrupar es presentacion pura sobre datos ya calculados).
- Riesgo: bajo, unico cuidado tecnico documentado en Diseño §5 (ocultar encabezados de grupo sin filas visibles al filtrar).

## 5. Pruebas funcionales
Cubre las 3 HU de Diseño: agrupado correcto (incluido "Sin categoria"), filtro por categoria aisla el grupo, combinacion buscador+categoria. Regresion: el conteo del boton/alert y el comportamiento existente (colores, boton editar Admin, buscador solo) no cambian.

---

## Sesion: Frente A recortado — higiene del circuito de Pagos (A1 + A3 + A5)

## Estado: EN ARQUITECTURA — pendiente aprobacion para pasar a Presupuesto

Entrada: Diseño cerrado el 2026-10-07 (`2-disenador-funcional.md`, seccion "Frente A recortado", lineas 415-604), 7 HU, sin migracion EF. Analisis: seccion 9 de `1-analista-funcional.md`.

## 0. Resultado del escaneo de reutilizacion cross-proyecto

Escaneo dirigido (`grep -ril` sobre `docs/*/definiciones/{3-arquitecto-mvc,5-implementador}.md`) con los terminos del alcance: `PagoService`, validacion de fecha, totalizador.

| Match | Que se evaluo | Decision |
|---|---|---|
| **delicias-naturales, iteracion 3** (`3-arquitecto-mvc.md:319-396`) — `PagoService` + PAT-023 | El punto unico por donde pasan alta y edicion de pago ya existe en este repo y es de esta misma iteracion anterior. | **Base de esta arquitectura.** No se crea ningun servicio nuevo: las 4 reglas de fecha entran en `PagoService`, que es el unico lugar desde donde se puede cubrir `RegistrarPago` y `EditarPago` a la vez. Ver AD-1. |
| **koi** (`3-arquitecto-mvc.md:40`) — `EstadoResultadosService` con totalizadores y snapshot de % por movimiento | Totalizadores agregados en un service dedicado. | **No se reutiliza.** Koi necesita un service porque sus totales son calculados con parametros versionados; los 3 grupos de A5 son una reagrupacion de un `GROUP BY` que ya se ejecuta. Montar un service para eso seria sobreingenieria. Ver AD-4. |
| **la-platense**, leccion LP-009 (ya tomada en Diseño) | `ArgentinaTime.Hoy` en vez de `DateTime.UtcNow` para rechazar fecha futura. | **Se reutiliza el criterio.** En este repo el equivalente ya existe: `Helper/DateTimeExtended.ToArgentinaTimeZone()`. Ver AD-6. |
| `estudio-contable-maribel-garcia`, `ganaderia` | Aparecieron por el termino `PagoService` pero son servicios de pago de otro dominio (honorarios, egresos ganaderos) sin validacion de fecha ni totalizadores por medio. | Sin reuso aplicable. |

Sin componentes nuevos que catalogar. El patron candidato de esta iteracion (**"el importe por defecto de un pago depende del medio"**) es de Diseño/UI y va como variante de PAT-019, no como entrada propia — se agrega al cerrar.

## 1. Mapa de componentes

```
Views/Ventas/Details.cshtml  ─┐
Views/Ventas/Edit.cshtml     ─┴─> Views/Ventas/_ModalRegistrarPago.cshtml   (NUEVO, AD-7)
                                        │  markup del modal + su JS unificado
                                        ▼
                             PagosController.RegistrarPago(.., bool confirmaFecha = false)
Views/Ventas/_ModalEditarPago (existente) ─> PagosController.EditarPago(.., bool confirmaFecha = false)
                                        │
                                        ▼
                             PagoService.ValidarFechaPago(fecha, venta, confirmaFecha)   (NUEVO, AD-1)
                                        │   lanza PagoNegocioException (R1a, R2)
                                        │   lanza PagoConfirmacionRequeridaException (R1b, R3)  (NUEVO, AD-2)
                                        ▼
                             PagoService.RegistrarPagoInterno / EditarPago   (existentes, se les agrega la llamada)

Views/Pagos/Index.cshtml ──> PagosController.ListarPagos ──> totalesPorGrupo + totalSaldoFavor   (AD-4, AD-5)
```

Componentes **nuevos**: 1 partial (`_ModalRegistrarPago.cshtml`), 1 metodo de servicio (`ValidarFechaPago`), 1 excepcion (`PagoConfirmacionRequeridaException`).
Componentes **modificados**: `PagoService` (2 metodos), `PagosController` (3 acciones), 3 vistas.
Componentes **nuevos de datos**: **ninguno.**

## 2. Decisiones de arquitectura

### AD-1 — `ValidarFechaPago` se llama DOS veces, y temprano

Las 4 reglas van en un metodo publico `PagoService.ValidarFechaPago(DateTime fecha, Venta venta, bool confirmaFecha)`, invocado:
- al inicio de `RegistrarPagoInterno` (cubre el alta normal), y
- al inicio de `EditarPago`, **antes de la reversion**.

**Por que las dos y no solo la primera.** `EditarPago` (`PagoService.cs:274-290`) hace `ReversarPago` + `_db.Entry(pagoViejo).State = Deleted` + **`_db.SaveChanges()`** y solo despues llama a `RegistrarPagoInterno`. Si la validacion viviera unicamente ahi, cada confirmacion de R1b/R3 ejecutaria la reversion completa, la persistiria, lanzaria la excepcion y dependeria del `tx.Rollback()` del Controller para deshacerla. Es correcto —la transaccion esta verificada en `PagosController.cs:474-504`, con `Rollback()` en los dos `catch`— pero **innecesario**: R1b y R3 alcanzan ~1 de cada 50 pagos, no es un camino raro. Validar al entrar hace que la ida y vuelta de confirmacion no toque la base.

El metodo es **idempotente** (solo lee y compara), asi que llamarlo dos veces en el flujo de edicion no tiene efecto secundario.

Firma y orden de evaluacion (el orden importa: el primer rechazo gana):
1. R1a `fecha.Date > hoy.AddDays(90)` → `PagoNegocioException`
2. R2 `fecha.Date < venta.Fecha.Date` → `PagoNegocioException`
3. R1b `fecha.Date > hoy` → `PagoConfirmacionRequeridaException` si `!confirmaFecha`
4. R3 `fecha.Date < hoy.AddDays(-30)` → `PagoConfirmacionRequeridaException` si `!confirmaFecha`

R1a antes de R1b y R2 antes de R3: un rechazo nunca debe presentarse como un aviso que se puede confirmar.

Constantes del Service, no configurables (criterio P6): `DiasFuturoMaximo = 90`, `DiasAtrasAviso = 30`.

### AD-2 — `PagoConfirmacionRequeridaException : PagoNegocioException`, y el `catch` va PRIMERO

```csharp
public class PagoConfirmacionRequeridaException : PagoNegocioException
{
    public PagoConfirmacionRequeridaException(string mensaje) : base(mensaje) { }
}
```

Hereda de `PagoNegocioException` a proposito: cualquier `catch` existente que no se actualice sigue degradando a "error" en vez de tirar un 500.

**Trampa, y es la mas probable de toda la iteracion:** `PagosController` ya tiene `catch (PagoNegocioException ex)` en `RegistrarPago` (`:391`) y en `EditarPago` (`:493`). C# resuelve los `catch` **de arriba hacia abajo**, asi que el bloque de la excepcion **derivada tiene que ir ANTES** del de la base. Con el orden inverso compila, no falla ningun test obvio, y el aviso de confirmacion le llega al usuario como un error rojo que no lo deja guardar nunca — exactamente el sintoma que haria pensar que la regla esta mal calibrada.

Los dos `catch` nuevos hacen `tx.Rollback()` igual que los existentes, y devuelven:
```json
{ "mensaje": "<texto de R1b o R3>", "tipoMensaje": "confirmar" }
```

### AD-3 — `confirmaFecha` entra como parametro opcional

`bool confirmaFecha = false` en `RegistrarPago`, `EditarPago` (acciones) y en `RegistrarPagoInterno`, `EditarPago`, `ValidarFechaPago` (servicio). **Ninguna llamada existente se rompe** — relevante porque `RegistrarPagoInterno` se invoca desde `RegistrarPago`, desde `EditarPago` y (a verificar en implementacion) desde cualquier otro punto que lo consuma.

### AD-4 — Los 3 grupos se calculan en memoria: cero consultas nuevas

`ListarPagos` ya ejecuta un unico `GROUP BY` (`PagosController.cs:202-205`) que trae `{ MetodoPago, Total }`. Los 3 grupos de A5 se arman **sobre esa lista ya materializada**, en memoria:

- Efectivo = `MetodoPago.Efectivo`
- Transferencia = `MetodoPago.Transferencia` (+ `Cheque` cuando exista)
- Tarjetas y billeteras = `Debito` + `Credito` + `MercadoPago`
- `totalSaldoFavor` = `SaldoFavor`, aparte y fuera de los 3

**Impacto en performance: ninguno.** No se agrega ni una query. Importa decirlo porque `ListarPagos` ya es la accion mas cara del controller cuando hay `searchValue` (materializa una proyeccion completa para la busqueda por substring numerico, `:117-124`) y esta iteracion no debe empeorarla.

### AD-5 — `montoTotal` y `totalesPorMetodo` se REEMPLAZAN, no se mantienen

Diseño proponia conservarlos por compatibilidad (riesgo R-A5b). **Verificado: no hace falta.** El unico consumidor de los dos campos es `Views/Pagos/Index.cshtml` (`:111`, `:125-126`); los otros hits del grep estan en `obj/Release/...`, que son artefactos de build, no codigo fuente.

Decision: `montoTotal` se elimina (los 3 grupos lo reemplazan y ademas lo mejoran: hoy suma todo menos `SaldoFavor` en un numero que no se compara contra nada) y `totalesPorMetodo` se mantiene **solo** como detalle de la fila inferior, filtrando los metodos en $0 (HU7). Sin codigo muerto.

### AD-6 — Una sola fuente de "hoy"

`DeliciasNaturales.Helper.DateTimeExtended.ToArgentinaTimeZone().Date`, resuelto **una vez** al entrar a `ValidarFechaPago` y guardado en una variable local, para que las 4 reglas comparen contra el mismo instante (si se resolviera por regla, una validacion ejecutada a las 23:59:59.9 podria usar dos dias distintos).

**No se toca el helper.** Esta usado en mas de 20 lugares del repo, incluido el valor por defecto de los tres `<input type="date">` que esta iteracion modifica; agregarle metodos es un refactor que no pide nadie.

### AD-7 — Se extrae `_ModalRegistrarPago.cshtml` (markup + JS)

Diseño lo dejo como propuesta; **se aprueba y entra en esta iteracion.**

Verificado que la extraccion es limpia: las dos vistas declaran `@model DeliciasNaturales.Models.Venta` y calculan las mismas dos variables de la misma forma (`Details.cshtml:7,10` y `Edit.cshtml:12,15`), asi que la partial puede recibir el `Venta` y calcularlas internamente.

**Y las dos copias ya divergieron en dos lugares, no en uno.** Es la prueba de campo de por que hay que unificarlas:

1. **El reset del autocompletado:** `Details.cshtml:443` expone `window.resetMontoAutocompletado`, mientras `Edit.cshtml:462+` lo hace inline dentro del handler de `#agregar-pago-btn`.
2. **El disparador del modal:** `Details.cshtml:297` lo abre con un `onclick` inline (`if(window.resetMontoAutocompletado)window.resetMontoAutocompletado();$('#modalRegistrarPago').modal('show');return false;`) sobre un `<a>`; `Edit.cshtml` lo abre con un handler jQuery sobre `#agregar-pago-btn`. **Las dos pantallas no abren el modal de la misma forma.**

Consecuencia concreta para implementacion: **la partial tiene que soportar los dos disparadores**, o unificarlos a uno. Lo limpio es que la partial exponga `window.resetMontoAutocompletado()` (como ya hace Details) y que `Edit.cshtml` pase a llamarlo en vez de tener su copia; el `onclick` inline de Details se puede dejar como esta.

A1 y A3 tocan 4 puntos de cada modal: mantenerlos duplicados obliga al implementador a 8 ediciones espejadas y a QA a verificar las dos pantallas por separado. La partial lleva su markup **y** su `<script>`.

Es el item de mayor riesgo de la iteracion (T1). Si en implementacion aparece cualquier divergencia de markup no detectada aca, **la salida es dejar los dos modales duplicados y hacer las 8 ediciones** — se pierde la limpieza, no la funcionalidad.

## 3. Cambios de datos y migraciones

**NINGUNA MIGRACION EF.** No se agregan entidades, columnas, indices ni valores de enum. `MetodoPago.Cheque` y `Pago.FechaAcreditacion` son de A4, fuera de este alcance.

Dato relevante para pruebas: la base de produccion tiene **14.131 pagos activos** y las reglas nuevas solo cambian el comportamiento de altas/ediciones futuras — **no se corre ningun backfill ni se valida nada retroactivamente.** Los 3 pagos con fecha futura que ya existen ($852.206,16, incluidos los 2 typos de año por $163.780,83) **siguen igual**: corregirlos es un script de datos aparte, no parte de esta iteracion.

## 4. Riesgos tecnicos

| # | Riesgo | Severidad | Mitigacion |
|---|---|---|---|
| **T1** | La extraccion de `_ModalRegistrarPago.cshtml` (AD-7) toca dos pantallas en produccion de alto uso. Una diferencia de markup no detectada rompe el alta de pagos en una de las dos. | **Alta** | Diffear los dos bloques de modal **antes** de extraer y dejar el resultado en `5-implementador.md`. Salida declarada: duplicar en vez de extraer. QA regresiona el alta de pago **desde las dos pantallas** por separado. |
| **T2** | Orden de los `catch` (AD-2). Compila igual y el sintoma es un error rojo en vez de un dialogo de confirmacion. | **Alta** | Escrito en AD-2 con el numero de linea de los dos `catch` existentes. Criterio de QA explicito en 5.3. |
| **T3** | El flujo de confirmacion re-envia el formulario. Si el re-envio no arrastra **todos** los campos (o los arrastra dos veces), se puede crear un pago duplicado o con datos distintos a los confirmados. | **Alta** | El re-envio agrega `confirmaFecha=true` al **mismo** `$(this).serialize()` que ya usa el submit (`Details.cshtml:464-470`), sin re-leer el DOM. QA prueba confirmar y verifica que se cree **un solo** pago con los valores tipeados. |
| **T4** | `EditarPago` ya tiene una secuencia delicada (reversion → `SaveChanges` → alta) con 2 fixes de QA encima (QA-DN-003, QA-DN-004). Agregarle una validacion al inicio puede alterar el orden de guards y volver inalcanzable alguno. | Media | `ValidarFechaPago` va **antes** de todos los guards existentes de `EditarPago` y no modifica ninguno. Los guards de monto y motivo (`:239-245`) se mantienen donde estan. QA re-corre las HU de la iteracion 3. |
| **T5** | Dejar el Monto vacio para metodos de terceros (HU4) se implementa sobre el handler existente con el flag `montoEditadoManualmente`. Tocar ese flag mal rompe el autocompletado de Efectivo, que es el 59,2 % de los pagos. | Media | El handler solo cambia la **rama else**: hoy siempre escribe `montoRestante`, pasa a escribir `''` para los 4 metodos de terceros. El flag y la rama de `SaldoFavor` no se tocan. |
| **T6** | `ExportarExcel` **no** extiende `fechaHasta` a fin de dia, a diferencia de `ListarPagos` (`:78` lo hace, `:275` no). El Excel puede informar menos que la pantalla para el ultimo dia del rango. | Baja **hoy** | **Medido: 2.565 de 14.132 pagos tienen hora distinta de 00:00:00, pero ninguno desde junio 2026** — los modales ya cargan fecha sin hora, asi que los meses que el cliente concilia no estan afectados. Se registra como deuda con esa salvedad; corregirlo es una linea, pero **fuera de alcance** para no inflar la iteracion. Decision de Joaquin si entra. |
| **T7** | Los 3 rotulos de A5 afirman contra que se compara cada numero. Si P12 se responde distinto de lo supuesto, los rotulos pasan a mentir — y el punto entero de A5 era dejar de mentir. | Media | La estructura de 3 cards no cambia con la respuesta: cambia **que metodo entra en cual**, que es un mapeo de 1 linea en AD-4. **No implementar A5 sin la respuesta a P12**, o implementarlo con los metodos cableados en una constante facil de mover. |

## 5. Estrategia de pruebas funcionales

### 5.1 Validacion de fecha (HU1-HU3), en las 3 entradas: Details, Edit y Editar pago
1. Fecha de hoy → guarda sin aviso.
2. Fecha de hoy, ejecutado despues de las 21:00 ART → guarda sin aviso (regresion de LP-009; es el caso que se rompe si alguien usa `DateTime.UtcNow`).
3. Fecha de mañana → dialogo de confirmacion R1b. Confirmar guarda; cancelar no guarda y conserva lo tipeado.
4. Fecha de hoy + 91 dias → **error**, no dialogo. No se crea el pago.
5. Fecha anterior a la fecha de la venta → **error** con la fecha de la venta en el mensaje.
6. Fecha igual al dia de la venta → guarda sin error (limite inclusivo).
7. Fecha de hoy - 31 dias → dialogo R3. Fecha de hoy - 30 → sin dialogo (limite).
8. Fecha futura **y** anterior a la venta a la vez → gana el rechazo, nunca el aviso (orden de AD-1).

### 5.2 Importe por medio (HU4-HU5)
9. Elegir `Efectivo` → Monto se precarga con el saldo restante (regresion).
10. Elegir `SaldoFavor` → Monto se precarga con `min(saldoFavor, restante)` (regresion).
11. Elegir `Transferencia`/`Debito`/`Credito`/`MercadoPago` → Monto queda **vacio** con el placeholder.
12. Tipear un importe y despues cambiar el metodo → **no se borra** lo tipeado (regresion del flag `montoEditadoManualmente`).
13. Boton "usar el saldo" → copia el restante al input.
14. Las 4 variantes de la linea de consecuencia (menor / igual / mayor con cliente / mayor sin cliente).
15. Cobrar de mas una venta ya cubierta sigue permitido y sigue generando el credito en cuenta corriente (regresion de la iteracion de cuenta corriente).

### 5.3 Confirmacion y transaccion (T2, T3)
16. Disparar R1b en `EditarPago`: verificar que **no quedo nada escrito** antes de la confirmacion — el pago viejo sigue vigente y sus movimientos de caja y cuenta corriente intactos (es el punto de AD-1).
17. Confirmar un R1b en `EditarPago`: se crea **un solo** pago nuevo, el viejo queda soft-deleted y enlazado, y los movimientos cuadran.
18. Verificar que el dialogo aparece como **confirmacion** y no como error rojo (es el sintoma de T2 invertido).

### 5.4 Totalizadores (HU6-HU7)
19. Sin filtro de metodo: los 3 grupos suman el total de pagos del rango menos `SaldoFavor`.
20. **Contra septiembre 2026, con el dato ya conciliado:** la card "Cobrado por transferencia" debe dar **$36.019.758,88** y "Tarjetas y billeteras" **$4.768.320,49** (Debito 3.922.955,34 + Credito 845.365,15 + MercadoPago 0). Es la prueba de aceptacion mas fuerte de A5 porque los numeros estan verificados contra la base en el relevamiento.
21. Filtro de metodo en uno solo → su grupo muestra el importe, los otros dos $0.
22. `MercadoPago` (siempre $0) **no** aparece como card en la fila inferior.
23. Filtro sin resultados → las 3 cards en $0 y la fila inferior vacia, sin romper el layout.
24. Los 3 totales respetan rango de fechas, metodo y busqueda igual que el total actual.

### 5.5 Regresion de la partial (T1)
25. Alta de pago completa **desde `Ventas/Details`** y **desde `Ventas/Edit`**, por separado: abrir el modal, los 3 campos, guardar, y el reset al reabrir.
26. Build con `MvcBuildViews=true` (regla del proyecto: el build normal no compila `.cshtml`).

## 6. Gate de aprobacion para pasar a presupuesto

Habilitado, con una condicion: **T7 pide la respuesta de P12 antes de implementar A5.** A1 y A3 no dependen de nada. Si P12 demora, A5 se puede presupuestar igual y implementar con el mapeo de metodos en una constante.

## Historial de ajustes
- 2026-10-07: **Arquitectura abierta del "Frente A recortado — higiene del circuito de Pagos (A1 + A3 + A5)"**. **Sin migracion EF.** Componentes nuevos: 1 partial (`Views/Ventas/_ModalRegistrarPago.cshtml`), 1 metodo (`PagoService.ValidarFechaPago`) y 1 excepcion (`PagoConfirmacionRequeridaException : PagoNegocioException`). 7 decisiones de arquitectura (AD-1 a AD-7), 7 riesgos tecnicos (T1-T7), estrategia de pruebas de 26 puntos. **AD-1**: `ValidarFechaPago` se llama DOS veces —en `RegistrarPagoInterno` y al inicio de `EditarPago`, antes de la reversion— porque `EditarPago` reversa y hace `SaveChanges()` antes de llamar al alta, y R1b/R3 alcanzan ~1 de cada 50 pagos: validar tarde obligaria a un rollback en un camino que no es raro. El metodo es idempotente. **AD-2**: el `catch` de la excepcion derivada **va antes** del de `PagoNegocioException` ya existente (`PagosController.cs:391` y `:493`) — C# resuelve top-down y con el orden inverso compila igual, pero el aviso de confirmacion le llega al usuario como error rojo. Es T2, la trampa mas probable de la iteracion. **AD-4/AD-5**: los 3 grupos de A5 se calculan en memoria sobre el `GROUP BY` que `ListarPagos` ya ejecuta — **cero consultas nuevas**, relevante porque esa accion ya es la mas cara del controller con busqueda activa; y `montoTotal`/`totalesPorMetodo` se **reemplazan** en vez de mantenerse (verificado que el unico consumidor es `Views/Pagos/Index.cshtml:111,125-126`; los hits en `obj/Release/` son artefactos de build), lo que corrige el riesgo R-A5b que Diseño habia dejado abierto. **AD-7**: se aprueba extraer la partial del modal. Verificado que las dos vistas declaran el mismo `@model Venta` y calculan las mismas variables igual (`Details.cshtml:7,10`, `Edit.cshtml:12,15`), y que **las dos copias ya divergieron en dos lugares**: el reset del autocompletado y el disparador del modal (Details usa un `onclick` inline en `:297`, Edit un handler sobre `#agregar-pago-btn`). Salida declarada si aparece una divergencia no detectada: duplicar en vez de extraer. Se corrigio un error de suma propio arrastrado desde Diseño: el total de "Tarjetas y billeteras" de septiembre es **$4.768.320,49**, no $4.787.536,49 (verificado contra la base); corregido tambien en `2-disenador-funcional.md` y en la entrada de Diseño de este archivo. Deuda registrada sin entrar al alcance (T6): `ExportarExcel` no extiende `fechaHasta` a fin de dia como si hace `ListarPagos` (`:78` vs `:275`) — medido que afecta a 2.565 de 14.132 pagos pero **ninguno desde junio 2026**, asi que los meses que el cliente concilia estan limpios. **Gate de presupuesto habilitado**, con la condicion de T7: A5 no se implementa sin la respuesta a P12 (donde se acreditan Debito/Credito/MercadoPago), o se implementa con el mapeo de metodos en una constante.
- 2026-06-XX: Creacion. Arquitectura iteracion 2 modulo Solicitudes de Ingreso de Stock. Diseno aprobado, gate de presupuesto OK.
- 2026-09-23: Arquitectura iteracion 4 "Agrupar por categoria en modal Stock bajo" — 100% Presentacion, sin migracion. Presupuesto salteado (mejora de UI menor, deuda tecnica). Gate de Implementacion habilitado.
- 2026-09-07: Arquitectura iteracion 3 "Editar Pago" — se decide extraer `Services/PagoService.cs` (alineado con el patron cross-proyecto VentaService/EgresoPagoService de marihogar/ganaderia, refactor acotado: solo la logica de reversion+alta de Pago, no todo el Controller). Se decide ademas agregar `MovimientoCaja.PagoId` (cierra el riesgo #1 marcado en Diseño, ahora mas relevante porque toda edicion de pago pasa por reversion). 2 migraciones EF (o 1 combinada), 5 riesgos tecnicos identificados (T1 regresion por refactor es el de mayor cuidado), estrategia de pruebas de 9 puntos. Gate de presupuesto habilitado.
