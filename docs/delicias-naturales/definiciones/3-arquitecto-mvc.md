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

## Historial de ajustes
- 2026-06-XX: Creacion. Arquitectura iteracion 2 modulo Solicitudes de Ingreso de Stock. Diseno aprobado, gate de presupuesto OK.
