# 3 — Arquitectura MVC
## Sistema de Gestión Comercial — Indumentaria y Calzado

**Cliente:** Ulises  
**Proveedor:** OlvidataSoft  
**Versión:** 1.0  
**Estado:** Arquitectura cerrada — listo para handoff a Presupuesto  
**Base:** `analisis-funcional.md` v1.1 + `2-disenador-funcional.md` v1.0 (aprobados)  
**Soporte extendido:** `arquitectura.md` v1.0 (catálogo técnico detallado de entidades, configs, rutas y archivos)

> Memoria oficial del agente "arquitecto-mvc". Consolida impacto por capa, modelo de permisos, decisión de migraciones EF, riesgos y gate de aprobación. Las decisiones técnicas que aquí se registran resuelven las cinco preguntas abiertas que el diseñador funcional dejó para esta etapa.

---

## 1. Alcance funcional resumido

Habilitar la solución para 9 módulos + Dashboard sobre la Clean Architecture de 4 capas existente:

- **Domain**: 20 entidades nuevas + 5 enums (todas heredan `SoftDestroyable`).
- **Application**: 14 interfaces de servicio con contratos basados en `ServiceResult<T>`.
- **Infrastructure**: 20 `IEntityTypeConfiguration`, 20 `DbSet`, 14 implementaciones de servicio, 6 migraciones EF (M1–M6), seed del rol `Vendedor`.
- **Web**: 13 controllers, ~30 vistas, ~35 ViewModels, 7 endpoints AJAX, sidebar dinámico por rol, 2 policies de autorización.

Las decisiones funcionales D1–D6 (análisis v1.1) están todas soportables por la arquitectura propuesta y la **máquina de estados** de Compra/Venta/Devoluciones/Aumento masivo se encapsula en services (sin lógica en controllers).

---

## 2. Stack y reutilización

Reutilizar todo lo ya provisto por la solución base. **No** introducir piezas nuevas si la solución ya las resuelve.

| Componente | Tecnología | Estado |
|---|---|---|
| Runtime / Framework | .NET 10, ASP.NET Core MVC 10 | Existente |
| ORM / Provider | EF Core 10 + `MySql.EntityFrameworkCore` 10.0.1 | Existente |
| Base de datos | MySQL 8 | Existente |
| Identidad / AuthZ | ASP.NET Core Identity + Policies | Existente (extender) |
| Resultados de service | `ServiceResult` / `ServiceResult<T>` | Existente — **reutilizar** |
| DataTables server-side | `DataTableRequest` / `DataTableResponse<T>` | Existente — **reutilizar** |
| Soft delete global | Filter en `AppDbContext` + base `SoftDestroyable` | Existente — **reutilizar** |
| Auditoría | `AuditLog` y interceptor existentes | Existente — **reutilizar** |
| PDF | QuestPDF | Disponible — librería local |
| Excel | ClosedXML | Disponible — librería local |
| Frontend | Bootstrap 5, jQuery, DataTables, Select2, SweetAlert2 | Existente — **reutilizar** |
| Logging | Serilog | Existente |
| Cultura | es-AR fija | Existente |

Solución: 4 proyectos (`Domain`, `Application`, `Infrastructure`, `Web`).

---

## 3. Impacto técnico por capa

### 3.1 Domain (`ShowroomGriffin.Domain`)

| Cambio | Cantidad | Detalle |
|---|---|---|
| Enums nuevos | 5 | `EstadoCompra`, `EstadoVenta`, `MedioPago`, `TipoMovimiento`, `TipoDevolucion` |
| Entidades nuevas | 20 | Maestros (5), Productos (2), Stock (3), Compras (3), Ventas (5), Postventa (2) — todas heredan `SoftDestroyable` |
| Reglas | — | Sin lógica de negocio en entidades. Métodos auxiliares mínimos (factories) opcionales. |
| Carpetas | 5 | `Maestros/`, `Productos/`, `Stock/`, `Compras/`, `Ventas/`, `Postventa/` (catálogo en `arquitectura.md` §3 y §12) |
| Concurrencia (D6) | 1 | Agregar `byte[] RowVersion` con `[Timestamp]` en `VarianteProducto` para bloqueo optimista del aumento masivo |

### 3.2 Application (`ShowroomGriffin.Application`)

| Cambio | Cantidad | Detalle |
|---|---|---|
| Interfaces de servicio | 14 | Catálogo en `diseño-funcional.md` §4. Incluye `ICategoriaService`, `ISubgrupoService`, `IClienteService`, `IProveedorService`, `ITipoPrecioZapatillaService`, `IProductoService`, `IVarianteService`, `IStockService`, `ICompraService`, `IVentaService`, `IRemitoService`, `IDevolucionService`, `IResumenSemanalService`, `IAumentoMasivoService` |
| Convenciones | — | Todos los métodos retornan `ServiceResult` o `ServiceResult<T>`. Sin referencia a Infrastructure ni Web. |
| Política de costos | 1 | Parámetro explícito `bool incluirCostos` en métodos de venta/listados. El controller resuelve el valor a partir del rol del usuario (`User.IsInRole("Administrador")` o `"SuperUsuario"`). Decisión: se evita un segundo DTO. |

### 3.3 Infrastructure (`ShowroomGriffin.Infrastructure`)

| Cambio | Cantidad | Detalle |
|---|---|---|
| `IEntityTypeConfiguration` | 20 | Un archivo por entidad bajo `Data/Configurations/{Modulo}/` |
| `ApplyConfigurationsFromAssembly` | 1 | Reemplaza configs inline en `OnModelCreating` |
| `DbSet` en `AppDbContext` | 20 | Catálogo en `arquitectura.md` §6.1 |
| Implementaciones de servicio | 14 | En `Infrastructure/Services/` |
| Registros DI | 14 | `AddScoped` en `DependencyInjection.cs` (`AddInfrastructure`) |
| Seed | 1 | Agregar `RolVendedor = "Vendedor"` |
| Migraciones EF | 6 | M1–M6 (ver §5) |
| Adjuntos | — | `wwwroot/uploads/{compras\|ventas}/{guid}.{ext}` (≤ 5 MB; .jpg/.jpeg/.png/.pdf) |

#### Decisiones técnicas resueltas en esta etapa

| Pregunta abierta del diseñador | Decisión arquitectónica |
|---|---|
| Bloqueo optimista (D6) | `byte[] RowVersion` con `[Timestamp]` en `VarianteProducto`. EF detecta `DbUpdateConcurrencyException`; el segundo actor recibe error y debe re-previsualizar. **No** se usa lock pesimista. |
| Persistencia del redondeo de cuotas (D2) | Una **única fila** `VentaPago` con `MedioPago = Cuotas`, `Importe` total con recargo, `CantidadCuotas` y `PorcentajeFinanciamiento`. La distribución de cada cuota (con ajuste en última por redondeo) se calcula en presentación/remito. No se persisten N filas por cuota en v1. |
| Índices únicos | `Sku` y `CodigoBarra` en `VarianteProducto` (filtro `IS NOT NULL`); `NroVenta` único en `Venta`; `Email` único de Identity (existente); `Nombre` único en `Categoria`. Si el provider MySQL no soporta `HasFilter`, fallback a índice único normal + validación previa en service. |
| Política de transacciones | `IsolationLevel.Serializable` para: `IVentaService.CrearAsync`, `IVentaService.AnularAsync`, `ICompraService.RecepcionarAsync`, `IDevolucionService.CrearAsync`. Resto de operaciones: `ReadCommitted` por defecto. |
| Filtrado de payload por rol | Controller resuelve `bool incluirCostos = User.IsInRole("Administrador") \|\| User.IsInRole("SuperUsuario")` y lo pasa al service. Vendedor nunca recibe `UltimoPrecioCompra`, `CostoTotal`, `GananciaTotal` ni `MargenGanancia`. |

#### Numeración de venta (D1)
Patrón **two-save** en `IVentaService.CrearAsync`:
1. Persistir cabecera con `NroVenta = null` para obtener `Id` autogenerado.
2. Asignar `NroVenta = $"VTA-{Id:D5}"` y `SaveChanges` final.
Todo dentro de la misma transacción serializable junto con detalles, pagos y movimientos de stock.

### 3.4 Web (`ShowroomGriffin.Web`)

| Cambio | Cantidad | Detalle |
|---|---|---|
| Controllers nuevos | 13 | `Categorias`, `Subgrupos`, `Clientes`, `Proveedores`, `TiposPrecio`, `Productos`, `Variantes`, `Stock`, `Compras`, `Ventas`, `Devoluciones`, `ResumenSemanal`, `AumentoMasivo` (+ ajuste a `HomeController`) |
| ViewModels | ~35 | En `Web/Models/{Modulo}/` |
| Vistas | ~30 | En `Web/Views/{Controller}/` + partials para líneas dinámicas |
| Endpoints AJAX | 7 | Subgrupos por categoría, búsqueda Clientes/Proveedores/Variantes, Stock por variante, Resumen semanal, Variantes para aumento |
| Policies | 2 | `RequireAdministrador`, `RequireVendedor` (ver §4) |
| Sidebar | 1 | Visibilidad condicional por rol con `User.IsInRole()` |
| JS de pantallas complejas | 3 | Nueva Venta (carrito + pagos), Recepción Compra (validación por línea), Wizard Devolución (4 pasos) |
| Reglas | — | Controllers solo orquestan request → service → view/json. **Nunca** lógica de negocio. |

---

## 4. Modelo de permisos (roles / claims / policies)

### 4.1 Roles

| Rol | Origen | Notas |
|---|---|---|
| `SuperUsuario` | Existente | Acceso técnico total, incluida auditoría y configuración. |
| `Administrador` | Existente | Operación comercial completa. No puede crear `SuperUsuario`. |
| `Vendedor` | **Nuevo (M1 seed)** | Operativa de ventas/devoluciones. Sin costos ni ganancias. |

Constante a agregar en `SeedData`:

```
public const string RolVendedor = "Vendedor";
```

### 4.2 Policies

A registrar en `Program.cs` luego de `AddIdentity`:

| Policy | Roles autorizados |
|---|---|
| `RequireAdministrador` | `SuperUsuario`, `Administrador` |
| `RequireVendedor` | `SuperUsuario`, `Administrador`, `Vendedor` |

> No se utilizan claims granulares; las policies por rol cubren el alcance v1.

### 4.3 Aplicación de policies por controller

| Controller | Policy a nivel clase | Excepciones por acción |
|---|---|---|
| `CategoriasController` | `RequireAdministrador` | — |
| `SubgruposController` | `RequireAdministrador` | `PorCategoria` (AJAX): `RequireVendedor` |
| `ClientesController` | `RequireVendedor` | CUD reforzado en service: solo Admin |
| `ProveedoresController` | `RequireAdministrador` | — |
| `TiposPrecioController` | `RequireAdministrador` | — |
| `ProductosController` | `RequireVendedor` | CUD reforzado en service: solo Admin |
| `VariantesController` | `RequireVendedor` | CUD reforzado en service: solo Admin |
| `StockController` | `RequireVendedor` | `CargaInicial`, `Ajuste`: `RequireAdministrador` |
| `ComprasController` | `RequireAdministrador` | — |
| `VentasController` | `RequireVendedor` | — |
| `DevolucionesController` | `RequireVendedor` | — |
| `ResumenSemanalController` | `RequireAdministrador` | — |
| `AumentoMasivoController` | `RequireAdministrador` | — |

### 4.4 Visibilidad de costos

- **Filtrado server-side** del payload según rol. El controller calcula `incluirCostos` y lo pasa al service. Esto cubre R1 de "no exponer datos sensibles" y queda probado por los tests de autorización.
- Sidebar y vistas no muestran columnas/widgets que requieran costos para Vendedor.

---

## 5. Migraciones EF — ¿requeridas?

**Sí. 6 migraciones incrementales (M1–M6).** Justificación: 20 entidades nuevas, 5 enums (`HasConversion<int>`), índices únicos y `RowVersion` para D6. Se requiere preservar el orden por dependencias de FK.

| # | Nombre | Entidades | Dependencias |
|---|---|---|---|
| M1 | `AddMaestrosComerciales` | Categoria, Subgrupo, Cliente, Proveedor, TipoPrecioZapatilla | — |
| M2 | `AddProductosVariantes` | Producto, VarianteProducto (incluye `RowVersion`) | M1 |
| M3 | `AddStockInventario` | Stock, MovimientoStock, AjusteStock | M2 |
| M4 | `AddCompras` | Compra, CompraDetalle, CompraAdjunto | M1, M2 |
| M5 | `AddVentas` | Venta, VentaDetalle, VentaPago, VentaAdjunto, Remito | M1, M2 |
| M6 | `AddDevoluciones` | DevolucionCambio, DevolucionCambioDetalle | M2, M5 |

Comandos (raíz de solución):

```
dotnet ef migrations add AddMaestrosComerciales -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add AddProductosVariantes  -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add AddStockInventario     -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add AddCompras             -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add AddVentas              -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add AddDevoluciones        -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef database update -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
```

---

## 6. Soporte arquitectónico de la máquina de estados

Validación de que la máquina de estados del diseño funcional (§4 de `2-disenador-funcional.md`) es soportable:

| Aspecto | Soporte arquitectónico |
|---|---|
| Transiciones encapsuladas en service | ✅ `ICompraService.CambiarEstadoAsync` / `RecepcionarAsync` y `IVentaService.AnularAsync` / `MarcarEntregadaAsync` validan estado origen y aplican guardas. |
| Atomicidad de efectos colaterales | ✅ Transacciones serializables en venta/recepción/devolución. |
| D1 numeración correlativa | ✅ Two-save dentro de la transacción de creación de venta. |
| D2 redondeo cuotas | ✅ Persistencia simple en `VentaPago`; cómputo de cuotas en presentación. |
| D3 dañadas pre-recepción | ✅ Lógica en `RecepcionarAsync`: si no hubo recepción previa, ignora `DevueltaProveedor`. |
| D4 preview no persiste | ✅ `IAumentoMasivoService.ObtenerVariantesAsync` calcula en memoria; solo `AplicarAsync` escribe. |
| D5 cliente con ventas | ✅ Guarda en `IClienteService.InactivarAsync`: query a `Ventas` por `ClienteId`. |
| D6 first-write-wins | ✅ `RowVersion` + manejo de `DbUpdateConcurrencyException` en `IAumentoMasivoService.AplicarAsync`. |

---

## 7. Riesgos y supuestos

| # | Tipo | Descripción | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | Riesgo | Orden estricto de 6 migraciones | Alto | Generar y aplicar en orden M1→M6; validar con `dotnet ef migrations script` antes de producción |
| R2 | Riesgo | Índices únicos condicionales (`HasFilter`) en MySQL | Medio | Verificar soporte del provider; fallback: índice único normal + validación previa en service |
| R3 | Riesgo | `ApplyConfigurationsFromAssembly` puede capturar configs de tests | Bajo | Limitar al assembly `Infrastructure` |
| R4 | Riesgo | Concurrencia en stock entre ventas simultáneas | Alto | `IsolationLevel.Serializable` + reintentos limitados ante deadlock |
| R5 | Riesgo | Concurrencia en aumento masivo (D6) | Medio | `RowVersion` + manejo `DbUpdateConcurrencyException`; mensaje "re-previsualice" |
| R6 | Riesgo | Two-save de `NroVenta` puede romperse si el segundo `SaveChanges` falla | Medio | Ambos `SaveChanges` en la misma transacción; rollback completo en error |
| R7 | Riesgo | Cascade en detalles vs soft delete del padre | Medio | Soft delete por código (no por DB CASCADE); CASCADE solo aplica a hard delete |
| R8 | Riesgo | Adjuntos en disco sin backup | Medio | GUID + plan de migración a blob storage en v2 |
| S1 | Supuesto | Proyecto MVC clásico (Controllers/Views) | — | Confirmado por estructura de la solución |
| S2 | Supuesto | `ServiceResult<T>` y `DataTableRequest/Response` cubren todos los retornos | — | Verificado |
| S3 | Supuesto | `MovimientoStock` con 4 FKs opcionales (no discriminador string) | — | Patrón preferido |
| S4 | Supuesto | Identity ya existe con `SuperUsuario` y `Administrador` | — | Confirmado en seed actual |
| S5 | Supuesto | QuestPDF y ClosedXML disponibles localmente | — | Sin integración externa |

---

## 8. Plan técnico por etapas (alineado a F0–F8 del diseño)

| Etapa funcional | Migración EF | Componentes técnicos clave |
|---|---|---|
| F0 — Seguridad/policies | — | Seed `RolVendedor`, policies, sidebar dinámico |
| F1 — Maestros | M1 | 5 entidades, 5 configs, 5 services, 5 controllers |
| F2 — Productos | M2 | 2 entidades + `RowVersion`, 2 configs, 2 services, 2 controllers, formulario dinámico Ropa/Zapatilla |
| F3 — Stock | M3 | 3 entidades, 3 configs, `IStockService` con FKs polimórficas |
| F4 — Compras | M4 | 3 entidades, 3 configs, `ICompraService` con máquina de estados + recepción transaccional |
| F5 — Ventas ⭐ | M5 | 5 entidades, 5 configs, `IVentaService` transaccional + two-save D1 + D2 + D5 reforzado |
| F6 — Devoluciones | M6 | 2 entidades, 2 configs, `IDevolucionService` transaccional |
| F7 — Resumen + Aumento | — | `IResumenSemanalService` (query directo), `IAumentoMasivoService` con D4 + D6 |
| F8 — Dashboard / endurecimiento | — | Widgets por rol, revisión integral de policies y formato es-AR |

---

## 9. Pruebas técnicas mínimas (gate de calidad)

### Migraciones
- [ ] M1–M6 generadas y aplicadas sin errores.
- [ ] `dotnet ef migrations script` produce SQL válido para MySQL 8.
- [ ] Índices únicos condicionales verificados.

### Concurrencia
- [ ] Venta: dos creaciones concurrentes sobre mismo stock → solo una tiene éxito (R4).
- [ ] Aumento masivo: dos `Aplicar` sobre la misma variante → segundo recibe `DbUpdateConcurrencyException` (D6/R5).

### Autorización
- [ ] Vendedor → 403 en `/Compras`, `/Stock/Ajuste`, `/Stock/CargaInicial`, `/AumentoMasivo`, `/ResumenSemanal`.
- [ ] Vendedor nunca recibe `UltimoPrecioCompra`, `CostoTotal` ni `GananciaTotal` en payload.

### Lógica transaccional
- [ ] `CrearVenta`: stock decrementa, `NroVenta` se asigna, movimientos generados; rollback total ante error.
- [ ] `AnularVenta`: solo desde Confirmada; repone stock; bloqueada desde Entregada.
- [ ] `RecepcionarCompra`: valida `Rec+Dañ+Dev ≤ Pedida`; impacta stock con `CantidadRecibida`; actualiza `UltimoPrecioCompra`.
- [ ] `Devolucion`: cantidades respetan vendidas − previas; stock reingresa.

---

## 10. Checklist de salida — Arquitectura

```
ARQUITECTURA — CHECKLIST DE SALIDA
────────────────────────────────────────────────────────────────────
DOMAIN
[✓] 5 enums + 20 entidades planificadas, todas SoftDestroyable
[✓] RowVersion en VarianteProducto para D6
[✓] Sin lógica de negocio en entidades

APPLICATION
[✓] 14 interfaces de service definidas, retornan ServiceResult<T>
[✓] Política de costos por parámetro explícito
[✓] Sin referencia a Infrastructure ni Web

INFRASTRUCTURE
[✓] 20 IEntityTypeConfiguration + ApplyConfigurationsFromAssembly
[✓] 20 DbSets en AppDbContext
[✓] 6 migraciones EF planificadas (M1..M6)
[✓] 14 services + 14 registros DI
[✓] Seed RolVendedor
[✓] Política de transacciones (Serializable en venta/compra/devolución)
[✓] Adjuntos en wwwroot/uploads/{modulo}/{guid}

WEB
[✓] 13 controllers + 2 policies (RequireAdministrador / RequireVendedor)
[✓] ~35 ViewModels + ~30 vistas + sidebar dinámico
[✓] 7 endpoints AJAX
[✓] Visibilidad de costos resuelta en controller

DECISIONES D1..D6
[✓] D1 Two-save NroVenta dentro de transacción
[✓] D2 VentaPago único; cuotas en presentación
[✓] D3 Dañadas pre-recepción ignoradas en RecepcionarAsync
[✓] D4 Preview de aumento sin persistencia
[✓] D5 Bloqueo de inactivación de Cliente con ventas
[✓] D6 RowVersion + DbUpdateConcurrencyException

RIESGOS
[✓] R1..R8 documentados y mitigados

PRUEBAS
[✓] Plan de pruebas técnico mínimo definido
────────────────────────────────────────────────────────────────────
```

---

## 11. Gate de aprobación para pasar a Presupuesto

| Criterio | Estado |
|---|---|
| Análisis funcional v1.1 aprobado | ✅ |
| Diseño funcional v1.0 aprobado | ✅ |
| Impacto por capa cuantificado | ✅ |
| Modelo de permisos definido (roles + 2 policies) | ✅ |
| Decisión sobre migraciones EF | ✅ Sí — 6 migraciones M1–M6 |
| Máquina de estados soportable verificada | ✅ |
| Decisiones D1–D6 con solución técnica | ✅ |
| Riesgos identificados y mitigados | ✅ |
| Sin bloqueantes técnicos abiertos | ✅ |

**Gate: APROBADO — habilitado handoff a Presupuesto.**

### Insumos para presupuestador

- Cantidades concretas para estimación: 5 enums, 20 entidades, 20 configs Fluent, 14 services, 14 DIs, 6 migraciones EF, 13 controllers, ~35 ViewModels, ~30 vistas, 7 endpoints AJAX, 3 pantallas con JS complejo, 2 policies, 1 actualización de seed y sidebar.
- Riesgos R1, R2, R4, R5 son drivers de horas (testing de concurrencia y migraciones).
- Sin integraciones externas: no hay esfuerzo de adaptadores ni configuraciones de terceros.
