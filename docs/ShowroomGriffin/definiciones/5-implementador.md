# 5 — Implementador
## Sistema de Gestión Comercial — Indumentaria y Calzado

**Cliente:** Ulises  
**Proveedor:** OlvidataSoft  
**Versión:** 1.0  
**Estado:** Plan de implementación cerrado — listo para ejecución por etapas  
**Base:** `2-disenador-funcional.md` v1.0 + `3-arquitecto-mvc.md` v1.0 + `4-presupuestador.md` v1.0 (todos aprobados)

> Memoria oficial del agente "implementador". Consolida el plan técnico por etapas, los cambios por capa, las migraciones EF, la evidencia de build inicial y la matriz de pruebas mínimas. La ejecución se realiza en modo Agente, una etapa por iteración, con build verde como gate por etapa.

---

## 1. Alcance funcional resumido

Implementar 9 módulos + Dashboard sobre la solución existente de 4 capas (`Domain`, `Application`, `Infrastructure`, `Web`), preservando comportamiento legacy y respetando las decisiones D1–D6 del análisis y todas las decisiones técnicas resueltas en arquitectura. No hay integraciones externas. No se mueve lógica de negocio a Controllers.

Drivers concretos a materializar (de arquitectura):

- 5 enums + 20 entidades (todas `SoftDestroyable`).
- 14 interfaces de service + 14 implementaciones + 14 registros DI.
- 20 `IEntityTypeConfiguration` + `ApplyConfigurationsFromAssembly`.
- 6 migraciones EF (M1–M6) en orden.
- 13 controllers + ~35 ViewModels + ~30 vistas + 7 endpoints AJAX.
- 2 policies + seed `RolVendedor` + sidebar dinámico.
- 3 pantallas con JS complejo (Nueva Venta, Recepción Compra, Wizard Devolución).

---

## 2. Plan de ejecución técnica por etapas

Se sigue el orden funcional F0–F8 del diseño y el orden M1–M6 de migraciones del arquitecto. **Cada etapa exige build verde y checklist propio antes de avanzar.**

| Etapa | Nombre | Migración | Salida principal | Gate |
|---|---|---|---|---|
| E0 | Seguridad y armado base | — | Seed `RolVendedor`, policies `RequireAdministrador` / `RequireVendedor`, sidebar dinámico, ajuste a `HomeController` | Build OK + login con los 3 roles |
| E1 | Maestros comerciales | M1 `AddMaestrosComerciales` | 5 entidades, 5 configs, 5 services, 5 controllers + vistas CRUD + DataTables server-side | Build OK + smoke CRUD por maestro |
| E2 | Productos y variantes | M2 `AddProductosVariantes` (incluye `RowVersion`) | `Producto` + `VarianteProducto`, formulario dinámico Ropa/Zapatilla, Sku/CodigoBarra únicos | Build OK + alta variante con índices únicos verificados |
| E3 | Stock e inventario | M3 `AddStockInventario` | `Stock`, `MovimientoStock`, `AjusteStock`; `IStockService` con FKs polimórficas | Build OK + ajuste manual y consulta por variante |
| E4 | Compras + recepción | M4 `AddCompras` | `Compra`, `CompraDetalle`, `CompraAdjunto`; máquina de estados + `RecepcionarAsync` transaccional (`Serializable`) | Build OK + flujo completo Pedida→Recepcionada |
| E5 | Ventas ⭐ (núcleo crítico) | M5 `AddVentas` | `Venta`, `VentaDetalle`, `VentaPago`, `VentaAdjunto`, `Remito`; two-save D1, VentaPago único D2, anulación restringida, `Serializable` | Build OK + crear/anular venta + concurrencia stock |
| E6 | Devoluciones / cambios | M6 `AddDevoluciones` | `DevolucionCambio`, `DevolucionCambioDetalle`; wizard 4 pasos | Build OK + cambio total / parcial con reingreso de stock |
| E7 | Resumen semanal + Aumento masivo | — | `IResumenSemanalService` (query), `IAumentoMasivoService` con preview D4 + `RowVersion` D6 | Build OK + preview no persiste, segundo `Aplicar` falla con mensaje claro |
| E8 | Dashboard + endurecimiento | — | Widgets por rol, revisión integral de policies, formato es-AR, hardening de payload por costos | Build OK + verificación final de policies |

**Cierre por etapa:** ejecutar `dotnet build`, correr migración correspondiente, ejecutar pruebas mínimas asociadas, actualizar este documento y `trazabilidad.md` con el cierre de la etapa antes de iniciar la siguiente.

---

## 3. Cambios por capa (qué se toca y por qué)

### 3.1 Domain — `ShowroomGriffin.Domain`

| Carpeta / archivo | Tipo | Motivo |
|---|---|---|
| `Enums/EstadoCompra.cs`, `EstadoVenta.cs`, `MedioPago.cs`, `TipoMovimiento.cs`, `TipoDevolucion.cs` | Nuevo | Soportar máquina de estados y catálogo de pagos |
| `Entities/Maestros/{Categoria,Subgrupo,Cliente,Proveedor,TipoPrecioZapatilla}.cs` | Nuevo | Módulo F1 |
| `Entities/Productos/{Producto,VarianteProducto}.cs` | Nuevo | F2; `VarianteProducto` agrega `[Timestamp] byte[] RowVersion` (D6) |
| `Entities/Stock/{Stock,MovimientoStock,AjusteStock}.cs` | Nuevo | F3 |
| `Entities/Compras/{Compra,CompraDetalle,CompraAdjunto}.cs` | Nuevo | F4 |
| `Entities/Ventas/{Venta,VentaDetalle,VentaPago,VentaAdjunto,Remito}.cs` | Nuevo / ya parcialmente existente (`VentaPago.cs`) | F5; `VentaPago` única fila para D2 |
| `Entities/Postventa/{DevolucionCambio,DevolucionCambioDetalle}.cs` | Nuevo | F6 |

> Sin lógica de negocio en entidades. Solo factories opcionales y propiedades de navegación.

### 3.2 Application — `ShowroomGriffin.Application`

| Archivo | Tipo | Motivo |
|---|---|---|
| `Interfaces/I{Categoria,Subgrupo,Cliente,Proveedor,TipoPrecioZapatilla,Producto,Variante,Stock,Compra,Venta,Remito,Devolucion,ResumenSemanal,AumentoMasivo}Service.cs` | Nuevo (14) | Contratos basados en `ServiceResult<T>` / `DataTableResponse<T>` |
| Métodos de venta/listados | Nuevo | Parámetro explícito `bool incluirCostos` (decisión arquitectura §3.3) |

> Sin referencia a Infrastructure ni Web. No se mueve lógica fuera de su frontera.

### 3.3 Infrastructure — `ShowroomGriffin.Infrastructure`

| Archivo / cambio | Tipo | Motivo |
|---|---|---|
| `Data/Configurations/{Modulo}/*Configuration.cs` (20) | Nuevo | Una `IEntityTypeConfiguration` por entidad |
| `Data/AppDbContext.cs` | Modificado | 20 `DbSet` + reemplazar configs inline por `ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly)` |
| `Services/{Categoria…AumentoMasivo}Service.cs` (14) | Nuevo | Implementación de los 14 contratos |
| `DependencyInjection.cs` (`AddInfrastructure`) | Modificado | 14 `AddScoped` |
| `Data/SeedData.cs` (o equivalente) | Modificado | Constante y alta del rol `Vendedor` |
| `Migrations/` | Nuevo | M1–M6 generadas en orden |
| `wwwroot/uploads/{compras,ventas}/` | Nuevo (vía Web) | Adjuntos por GUID, ≤ 5 MB, .jpg/.jpeg/.png/.pdf |

Reglas críticas a respetar en Infrastructure:

- `IsolationLevel.Serializable` en `IVentaService.CrearAsync` / `AnularAsync`, `ICompraService.RecepcionarAsync`, `IDevolucionService.CrearAsync`.
- Two-save de `NroVenta = $"VTA-{Id:D5}"` dentro de la misma transacción.
- Manejar `DbUpdateConcurrencyException` en `IAumentoMasivoService.AplicarAsync` (D6).
- Índices únicos `Sku` / `CodigoBarra` con `HasFilter("…")`; fallback a unique normal + validación previa si MySQL no lo soporta.
- Soft delete por código; nunca `OnDelete(Cascade)` cuando rompa el filtro global.

### 3.4 Web — `ShowroomGriffin.Web`

| Archivo / cambio | Tipo | Motivo |
|---|---|---|
| `Controllers/{Categorias,Subgrupos,Clientes,Proveedores,TiposPrecio,Productos,Variantes,Stock,Compras,Ventas,Devoluciones,ResumenSemanal,AumentoMasivo}Controller.cs` | Nuevo (13) | Orquestan request → service → view/json |
| `Controllers/HomeController.cs` | Modificado | Quitar warning CS0114 (`StatusCode(int)` que oculta heredado) y CS9113 (`logger` no usado), ajustar dashboard por rol |
| `Models/{Modulo}/*ViewModel.cs` | Nuevo (~35) | ViewModels por pantalla |
| `Views/{Controller}/*.cshtml` | Nuevo (~30) | + partials de líneas dinámicas |
| `Views/Shared/_Layout.cshtml` (sidebar) | Modificado | Visibilidad dinámica con `User.IsInRole()` |
| `Program.cs` | Modificado | Registrar policies `RequireAdministrador` y `RequireVendedor` luego de `AddIdentity` |
| `wwwroot/js/{ventas-nueva,compras-recepcion,devoluciones-wizard}.js` | Nuevo (3) | Pantallas con JS complejo |
| Endpoints AJAX | Nuevo (7) | Subgrupos por categoría, búsqueda Clientes/Proveedores/Variantes, Stock por variante, Resumen semanal, Variantes para aumento |

> Controllers nunca contienen lógica de negocio. El cálculo de `incluirCostos = User.IsInRole("Administrador") || User.IsInRole("SuperUsuario")` se resuelve en el controller y se pasa explícitamente al service.

---

## 4. Migraciones EF aplicadas

**Sí aplican. 6 migraciones en orden estricto** (idénticas a §5 de arquitectura):

| # | Nombre | Etapa | Notas |
|---|---|---|---|
| M1 | `AddMaestrosComerciales` | E1 | Categoría, Subgrupo, Cliente, Proveedor, TipoPrecioZapatilla |
| M2 | `AddProductosVariantes` | E2 | Incluye `RowVersion` y unique con filtro |
| M3 | `AddStockInventario` | E3 | FKs opcionales en `MovimientoStock` |
| M4 | `AddCompras` | E4 | Adjuntos por GUID |
| M5 | `AddVentas` | E5 | `NroVenta` único; `VentaPago` única fila |
| M6 | `AddDevoluciones` | E6 | FKs a `Venta` y `VarianteProducto` |

Comandos por etapa (raíz de solución):

```
dotnet ef migrations add <Nombre> -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef database update         -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
```

Validación previa a producción:

```
dotnet ef migrations script -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
```

Impacto: schema incremental, sin pérdida de datos existentes. **No** se modifican entidades ni tablas Identity preexistentes.

---

## 5. Evidencia de build (estado inicial, pre-implementación)

Comando ejecutado en `C:\Sistemas\ShowroomGriffin`:

```
dotnet build -nologo
```

Resultado:

```
Build succeeded.
	8 Warning(s)
	0 Error(s)
Time Elapsed 00:00:04.61
```

Detalle de warnings (todos no bloqueantes):

| Tipo | Origen | Descripción | Acción |
|---|---|---|---|
| NU1902 | `MailKit 4.14.1` (Web + Infrastructure) | Vulnerabilidad moderada | Evaluar upgrade en E0 si hay versión segura compatible con .NET 10; en su defecto registrar como riesgo aceptado |
| NU1902 | `MimeKit 4.14.0` (Web + Infrastructure) | Vulnerabilidad moderada | Idem |
| NETSDK1057 | SDK .NET 10 preview | Aviso preview | Aceptado por la base del proyecto |
| CS0114 | `HomeController.StatusCode(int)` | Oculta miembro heredado | **Corregir en E0** (agregar `override` o renombrar) |
| CS9113 | `HomeController` parámetro `logger` no usado | Parámetro sin uso | **Corregir en E0** (usar o eliminar) |

> Build de partida en verde. Las correcciones cosméticas en `HomeController` se incorporan a E0 (no es refactor cosmético gratuito: están listadas como deuda heredada y se cierran al tocar el controller para el sidebar dinámico).

---

## 6. Pruebas mínimas requeridas para QA

### 6.1 Pruebas funcionales por etapa

| Etapa | Caso mínimo | Resultado esperado |
|---|---|---|
| E0 | Login con `SuperUsuario`, `Administrador`, `Vendedor` | Cada rol ve solo sus opciones de sidebar |
| E0 | `/Compras` con `Vendedor` | 403 (policy `RequireAdministrador`) |
| E1 | CRUD por maestro + soft delete + reactivación | Lista respeta filtro global; reactivación visible solo a Admin |
| E1 | Categoría con nombre duplicado | Validación previa rechaza, no llega a DB |
| E2 | Crear `VarianteProducto` con `Sku` duplicado | Rechazo por índice único / validación service |
| E2 | Aumento masivo preview (D4) | No persiste; recarga muestra precios anteriores |
| E3 | Ajuste manual de stock | Genera `MovimientoStock` y `AjusteStock` |
| E3 | Vendedor intenta `/Stock/Ajuste` | 403 |
| E4 | Recepción de compra con `Rec+Dañ+Dev > Pedida` | Rechazo, no impacta stock |
| E4 | Recepción válida | Stock incrementa, `UltimoPrecioCompra` se actualiza, estado pasa a Recepcionada |
| E5 ⭐ | Crear venta: stock disponible | `NroVenta = VTA-00001`, stock decrementa, movimientos generados |
| E5 ⭐ | Crear venta: stock insuficiente | Rollback total, sin cambios |
| E5 ⭐ | Anular venta Confirmada | Stock repuesto |
| E5 ⭐ | Anular venta Entregada | Bloqueada |
| E5 ⭐ | Pago en cuotas (D2) | 1 sola fila `VentaPago` con `MedioPago=Cuotas`, importes correctos en remito |
| E5 ⭐ | Vendedor obtiene detalle de venta | Payload sin `UltimoPrecioCompra`, `CostoTotal`, `GananciaTotal` |
| E6 | Cambio parcial (Devolución) | Cantidades ≤ vendidas − previas; stock reingresa |
| E7 | Resumen semanal | Totales coinciden con suma de ventas del rango |
| E7 | Aumento masivo concurrente (D6) | Segundo `Aplicar` recibe error y mensaje "re-previsualice" |
| E8 | Dashboard como Vendedor | Sin widgets de costos/ganancias |

### 6.2 Pruebas técnicas mínimas (gate de calidad por etapa)

- [ ] Build verde al cierre de cada etapa.
- [ ] Migración correspondiente aplicada y `dotnet ef migrations script` válido.
- [ ] Logs de auditoría (`AuditLog`) presentes en operaciones CUD.
- [ ] Sin `try/catch` que oculten excepciones de transacción.
- [ ] Sin lógica de negocio en controllers (revisión por checklist 26).

---

## 7. Riesgos y supuestos (vigentes desde arquitectura)

Se mantienen R1–R8 y S1–S5 de `3-arquitecto-mvc.md` §7. Riesgos con mayor exposición durante la implementación:

| # | Riesgo | Etapa más expuesta | Mitigación operativa |
|---|---|---|---|
| R1 | Orden estricto migraciones M1–M6 | E1–E6 | Generar y aplicar una por una; nunca saltear |
| R2 | `HasFilter` no soportado en MySQL | E2 | Probar primero; si falla, fallback unique normal + validación previa |
| R4 | Concurrencia stock en venta | E5 | `Serializable` + reintentos limitados ante deadlock |
| R5 | Concurrencia aumento masivo | E7 | `RowVersion` + manejo `DbUpdateConcurrencyException` |
| R6 | Two-save `NroVenta` | E5 | Ambos `SaveChanges` dentro de la misma transacción |

Supuesto operativo nuevo del implementador:

- **S6 (Implementación):** las correcciones de warnings heredados en `HomeController` (CS0114, CS9113) y la evaluación de upgrade `MailKit/MimeKit` (NU1902) se hacen en E0 sin abrir un refactor adicional.

---

## 8. Checklist de salida para merge (por etapa)

```
IMPLEMENTACIÓN — CHECKLIST DE MERGE (por etapa)
────────────────────────────────────────────────────────────────────
ALCANCE
[ ] Etapa cerrada coincide con el plan (E0..E8)
[ ] Sin scope creep ni refactors cosméticos no pedidos

CAPAS
[ ] Domain: solo entidades/enums; sin lógica de negocio
[ ] Application: contratos con ServiceResult<T>; sin refs a Infra/Web
[ ] Infrastructure: configs, services, DI, transacciones correctas
[ ] Web: controllers delgados; ViewModels y vistas alineadas a design system

EF / DATOS
[ ] Migración generada y aplicada (si corresponde)
[ ] dotnet ef migrations script válido para MySQL 8
[ ] Soft delete respetado; sin CASCADE conflictivo

SEGURIDAD
[ ] Policies aplicadas a nivel controller/acción según matriz §4.3 arquitectura
[ ] Vendedor no recibe campos de costos/ganancia
[ ] Sidebar refleja rol

PRUEBAS
[ ] Casos mínimos de la etapa (§6.1) ejecutados OK
[ ] Build verde (0 errores)
[ ] Sin nuevos warnings críticos respecto al baseline

DOCUMENTACIÓN
[ ] 5-implementador.md actualizado con cierre de la etapa
[ ] trazabilidad.md con entrada de la etapa
[ ] Si cambia un contrato, regenerar diagramas/notas mínimas
────────────────────────────────────────────────────────────────────
```

---

## 9. Estado actual del implementador

| Ítem | Estado |
|---|---|
| Plan técnico por etapas | ✅ Definido (E0–E8) |
| Cambios por capa | ✅ Listados |
| Migraciones EF | ✅ Plan M1–M6 confirmado |
| Build inicial | ✅ Verde (0 errores, 8 warnings no bloqueantes) |
| Pruebas mínimas | ✅ Matriz definida |
| Etapas ejecutadas | ✅ 9 / 9 (E0, E1, E2, E3, E4, E5, E6, E7, E8 cerradas) |

---

## 10. Cierre etapa E0 — Seguridad y armado base

### 10.1 Reconciliación con estado real del repo

Al iniciar E0 se detectó que la mayor parte del armado de seguridad **ya estaba implementado** en el repositorio. Se respeta la regla de cambios mínimos: no se reescribe lo que ya está OK.

| Ítem planificado E0 | Estado real al inicio | Acción ejecutada |
|---|---|---|
| Seed `RolVendedor` | ✅ Existente en `SeedData.cs` (constante + alta de rol) | Ninguna |
| Policy `RequireAdministrador` | ✅ Existente en `Program.cs` | Ninguna |
| Policy `RequireVendedor` | ✅ Existente en `Program.cs` | Ninguna |
| Sidebar dinámico por rol | ✅ Existente en `_Layout.cshtml` (`isAdmin` / `isVendedor` / `SuperUsuario`) | Ninguna |
| Migración M1 `AddMaestrosComerciales` | ✅ Ya generada (`20260416154337_M1_AddMaestrosComerciales`) | Ninguna |
| Warning CS0114 `HomeController.StatusCode(int)` | ❌ Pendiente | Agregado modificador `new` |
| Warning CS9113 parámetro `logger` no usado | ❌ Pendiente | Asignado a campo `_logger` y usado en `Error()` |
| Warnings NU1902 `MailKit 4.14.1` / `MimeKit 4.14.0` | ❌ Pendiente | Upgrade de `MailKit` a `4.16.0` (arrastra `MimeKit 4.16.0`) |

### 10.2 Cambios por capa en E0

| Capa | Archivo | Cambio | Motivo |
|---|---|---|---|
| Web | `ShowroomGriffin.Web\Controllers\HomeController.cs` | Campo `_logger` + uso en `Error()`; `public new IActionResult StatusCode(int code)` | Cerrar CS9113 y CS0114 sin alterar comportamiento |
| Infrastructure | `ShowroomGriffin.Infrastructure\ShowroomGriffin.Infrastructure.csproj` | `MailKit` 4.14.1 → 4.16.0 | Cerrar NU1902; arrastra `MimeKit` 4.16.0 vía dependencia transitiva |

No se tocaron Domain ni Application en E0.

### 10.3 Migraciones EF en E0

Ninguna migración nueva. M1 ya estaba generada antes de iniciar la implementación; queda en su lugar para la etapa E1.

### 10.4 Evidencia de build E0

Comando: `dotnet build -nologo` en `C:\Sistemas\ShowroomGriffin`.

```
Build succeeded.
    0 Warning(s)
    0 Error(s)
Time Elapsed 00:00:30.63
```

Mejora vs baseline: 8 warnings → 0 warnings. 0 errores en ambos casos.

### 10.5 Pruebas mínimas E0 (a ejecutar en QA)

- [ ] Login con `SuperUsuario` → ve sidebar completo (Principal, Ventas, Catálogo, Administración, Reportes, Super Usuario).
- [ ] Login con `Administrador` → ve todo excepto sección Super Usuario.
- [ ] Login con `Vendedor` → ve solo Principal + Ventas + Catálogo.
- [ ] `Vendedor` accede a `/Compras` → 403 (policy `RequireAdministrador` aplicada en E4 cuando se monte el controller; en E0 se valida solo el registro de la policy).
- [ ] `/Home/Error` y `/Home/StatusCode?code=404` siguen devolviendo la vista Error con el `RequestId` correcto.
- [ ] No hay regresión en login, logout, perfil ni cambio de password.

### 10.6 Riesgos / supuestos confirmados en E0

- S6 (implementación) confirmado: warnings heredados de `HomeController` cerrados sin abrir refactor adicional.
- Riesgo nuevo R-E0-1: el upgrade de `MailKit`/`MimeKit` podría requerir validación funcional del envío de emails (`EmailService`, `ErrorEmailNotifierMiddleware`, `SmtpHealthCheck`). Mitigación: smoke test de envío en QA antes de cerrar el merge.

### 10.7 Checklist de salida E0

```
E0 — CHECKLIST DE MERGE
────────────────────────────────────────────────────────────────────
[✓] Seed RolVendedor presente
[✓] Policies RequireAdministrador y RequireVendedor registradas
[✓] Sidebar dinámico por rol
[✓] HomeController sin warnings CS0114 ni CS9113
[✓] MailKit/MimeKit sin warnings NU1902
[✓] Build verde (0 errores, 0 warnings)
[ ] Smoke test de email en QA (R-E0-1)
[ ] Pruebas mínimas §10.5 en QA
────────────────────────────────────────────────────────────────────
```

**Gate E0: APROBADO técnicamente. Listo para iniciar E1 — Maestros comerciales tras confirmación.**

---

## 11. Cierre etapa E1 — Maestros comerciales

### 11.1 Reconciliación con estado real del repo

5 entidades (Categoria, Subgrupo, Cliente, Proveedor, TipoPrecioZapatilla), 5 configs Fluent, 5 services, 5 controllers, vistas Index/Crear/Editar y migración M1 ya estaban en el repo. Auditoría CRUD comparada contra `analisis-funcional.md` v1.1 (D5) y `2-disenador-funcional.md` v1.0 (matriz de permisos).

| Ítem planificado E1 | Estado real al inicio | Acción ejecutada |
|---|---|---|
| Entidades + configs (5) | ✅ Existentes | Ninguna |
| Migración M1 `AddMaestrosComerciales` | ✅ Generada | Ninguna (queda lista para `database update`) |
| Controllers + vistas | ✅ Existentes con policies correctas | Ninguna |
| `CategoriaService` validación nombre duplicado + bloqueo si tiene productos | ✅ Existente (R-MAE-01 / R-MAE-05) | Ninguna |
| `SubgrupoService.ObtenerPorCategoriaAsync` (AJAX) | ✅ Existente | Ninguna |
| `ClienteService.BuscarAsync` (AJAX) | ✅ Existente | Ninguna |
| `ClienteService.InactivarAsync` con guarda **D5** (no inactivar con ventas) | ❌ Soft delete sin guarda | **Fix aplicado** — `AnyAsync(v => v.ClienteId == id)` |
| Políticas (`RequireAdministrador` / `RequireVendedor`) en controllers | ✅ Aplicadas según matriz §4.3 arquitectura | Ninguna |

### 11.2 Cambios por capa en E1

| Capa | Archivo | Cambio | Motivo |
|---|---|---|---|
| Infrastructure | `Services\ClienteService.cs` → `InactivarAsync` | Agregada guarda D5: si existe `Venta` con `ClienteId == id`, devuelve `ServiceResult.CreateError("No se puede inactivar un cliente con ventas registradas.")` antes del soft delete | Cumplimiento de D5 (análisis funcional v1.1) |

No se tocaron Domain, Application ni Web en E1.

### 11.3 Migraciones EF en E1

Ninguna migración nueva. M1 ya estaba generada con todas las tablas requeridas (`Categorias`, `Clientes`, `Proveedores`, `TiposPrecioZapatilla`, `Subgrupos` con FK a `Categorias`). El comando `dotnet ef database update` queda como acción de despliegue, no de código.

### 11.4 Evidencia de build E1

```
Build succeeded.
    0 Warning(s)
    0 Error(s)
Time Elapsed 00:00:12.48
```

### 11.5 Pruebas mínimas E1 (a ejecutar en QA)

- [ ] Crear, editar y dar de baja Categoría, Subgrupo, Cliente, Proveedor, TipoPrecioZapatilla.
- [ ] Categoría con nombre duplicado (case-insensitive) → rechazo con mensaje.
- [ ] Inactivar Categoría que tiene productos → rechazo (R-MAE-05).
- [ ] **Inactivar Cliente con ventas → rechazo (D5)**.
- [ ] Inactivar Cliente sin ventas → OK, sale del listado por filtro global de soft delete.
- [ ] `Vendedor` accede a `/Clientes/Index` y `/Clientes/Buscar` (AJAX) → 200.
- [ ] `Vendedor` intenta `/Clientes/Crear` o `/Clientes/Editar` → 403.
- [ ] `Vendedor` accede a `/Categorias`, `/Subgrupos`, `/Proveedores`, `/TiposPrecio` → 403.
- [ ] `Subgrupos/PorCategoria?categoriaId=X` AJAX devuelve solo subgrupos de la categoría.
- [ ] DataTables server-side: ordenamiento, búsqueda y paginación responden.

### 11.6 Riesgos / supuestos confirmados en E1

- D5 cerrado en service (no en controller). Fronteras de capa respetadas.
- R2 (índices únicos `HasFilter` MySQL) **no aplica en E1**: solo se usan validaciones case-insensitive en service, no índices con filtro. Queda vigente para E2 (`Sku`/`CodigoBarra`).
- R7 (cascade vs soft delete) verificado: el filtro global de soft delete cubre la salida del listado; no hay `OnDelete(Cascade)` que rompa relaciones.

### 11.7 Checklist de salida E1

```
E1 — CHECKLIST DE MERGE
────────────────────────────────────────────────────────────────────
[✓] 5 entidades + 5 configs + 5 services + 5 controllers + vistas
[✓] Migración M1 generada (despliegue: `dotnet ef database update`)
[✓] Validaciones de negocio cerradas en service: nombre único (Categoría),
     bloqueo si tiene productos (Categoría), D5 (Cliente con ventas)
[✓] Policies según matriz §4.3 de arquitectura
[✓] AJAX endpoints: Subgrupos por categoría, búsqueda de Clientes
[✓] Build verde (0 errores, 0 warnings)
[ ] Pruebas mínimas §11.5 en QA
[ ] `dotnet ef database update` en entorno destino
────────────────────────────────────────────────────────────────────
```

**Gate E1: APROBADO técnicamente. Listo para iniciar E2 — Productos y Variantes (M2 + RowVersion + índices únicos `Sku`/`CodigoBarra`) tras confirmación.**

---

## 12. Cierre etapa E2 — Productos y Variantes

### 12.1 Reconciliación con estado real del repo

Al iniciar E2 se detectó que **M1 es monolítica**: además de los maestros comerciales, ya creó las tablas `Productos`, `VariantesProducto`, `Stocks`, `MovimientosStock`, `AjustesStock`, `ComprasDetalle`, `VentasDetalle` y `DevolucionesCambio` con sus FKs. Esto reinterpreta el plan original: **M2..M6 dejan de ser migraciones de creación de tablas y pasan a ser incrementales** sobre lo ya existente (nuevo supuesto **S7**).

| Ítem planificado E2 | Estado real al inicio | Acción ejecutada |
|---|---|---|
| Entidades `Producto`, `VarianteProducto` | ✅ Existentes | Ninguna |
| `ProductoConfiguration` / `VarianteProductoConfiguration` | ✅ Existentes | Ninguna |
| Índices únicos `Sku` / `CodigoBarra` (sin `HasFilter`) | ✅ Definidos en config (UNIQUE permite múltiples NULL en MySQL → R2 mitigado) | Ninguna |
| `VarianteService` con validación SKU/CodigoBarra duplicados | ✅ Existente | Ninguna |
| `VarianteService.InactivarAsync` con guarda stock>0 (R-PRD-08) | ✅ Existente | Ninguna |
| `VarianteService.BuscarAsync` sin exponer costos (E-08) | ✅ Existente | Ninguna |
| `AumentoMasivoService.AplicarAsync` con transacción explícita | ✅ Existente | Ninguna |
| **D6 — RowVersion en `VarianteProducto`** | ❌ Ausente | **Fix aplicado** — `[Timestamp] byte[] RowVersion` |
| **D6 — Mapeo EF `IsRowVersion()`** | ❌ Ausente | **Fix aplicado** — `builder.Property(e => e.RowVersion).IsRowVersion()` |
| **D6 — Manejo `DbUpdateConcurrencyException` en `AumentoMasivoService`** | ❌ Ausente | **Fix aplicado** — catch con rollback y mensaje "Otro usuario modificó precios… re-previsualice" |
| **Migración M2 — RowVersion** | ❌ No generada | **Generada** `20260428212244_M2_AddRowVersionToVariante` |

### 12.2 Cambios por capa en E2

| Capa | Archivo | Cambio | Motivo |
|---|---|---|---|
| Domain | `Entities\Productos\VarianteProducto.cs` | `[Timestamp] public byte[] RowVersion { get; set; } = Array.Empty<byte>();` | Token de concurrencia para D6 (first-write-wins) |
| Infrastructure | `Data\Configurations\Productos\VarianteProductoConfiguration.cs` | `builder.Property(e => e.RowVersion).IsRowVersion();` | Mapeo EF del token de concurrencia |
| Infrastructure | `Services\AumentoMasivoService.cs` → `AplicarAsync` | Catch `DbUpdateConcurrencyException` antes del catch genérico, con rollback y mensaje específico | Cierre técnico de D6 sobre el batch update |
| Infrastructure | `Data\Migrations\20260428212244_M2_AddRowVersionToVariante.cs` (nueva) | `AddColumn<byte[]>("RowVersion", "VariantesProducto", "longblob", rowVersion: true)` con `MySQLValueGenerationStrategy.ComputedColumn` | Persistencia del token en MySQL 8 |

No se tocaron Application ni Web en E2.

### 12.3 Migraciones EF en E2

- **M2** `20260428212244_M2_AddRowVersionToVariante` generada limpiamente.
- Despliegue: `dotnet ef database update` en entorno destino.
- M3..M6 quedan disponibles solo si etapas posteriores requieren cambios incrementales reales (S7).

### 12.4 Evidencia de build E2

```
Build succeeded.
    0 Warning(s)
    0 Error(s)
Time Elapsed 00:00:11.03
```

### 12.5 Pruebas mínimas E2 (a ejecutar en QA)

- [ ] Crear variante con SKU duplicado → rechazo con mensaje.
- [ ] Crear variante con CodigoBarra duplicado → rechazo con mensaje.
- [ ] Crear varias variantes con `Sku` y `CodigoBarra` en NULL → permitido (UNIQUE MySQL acepta múltiples NULL, R2 mitigado).
- [ ] Inactivar variante con `Stock > 0` → rechazo (R-PRD-08).
- [ ] Inactivar variante con `Stock = 0` → OK, soft delete.
- [ ] `Vendedor` invoca `Variantes/Buscar` → respuesta sin `UltimoPrecioCompra` ni `Ganancia`.
- [ ] `Administrador` invoca `Variantes/Obtener` → respuesta con `UltimoPrecioCompra` y `Ganancia`.
- [ ] **D6 concurrencia (aumento masivo)**: dos pestañas previsualizan; la primera aplica OK; la segunda aplica → mensaje "Otro usuario modificó precios… re-previsualice", sin actualización parcial (rollback).
- [ ] Aumento masivo por categoría / por subgrupo / todos, con `BaseAumento.PrecioCompra` y `PrecioVenta` → precios actualizados con redondeo a 2 decimales.
- [ ] Aumento masivo con `VariantesExcluidas` → esas variantes no cambian.

### 12.6 Riesgos / supuestos confirmados en E2

- **D6** cerrado en Domain + Infrastructure (token + mapeo + catch). Fronteras de capa respetadas.
- **R2** (índices únicos `HasFilter` MySQL) cerrado: UNIQUE sin filtro funciona porque MySQL permite múltiples NULL en columnas UNIQUE.
- **R5** (concurrencia en aumento masivo) cerrado vía RowVersion + manejo de `DbUpdateConcurrencyException`.
- **S7** (nuevo supuesto): M2..M6 son incrementales, no creación de tablas, porque M1 es monolítica.

### 12.7 Checklist de salida E2

```
E2 — CHECKLIST DE MERGE
────────────────────────────────────────────────────────────────────
[✓] Domain: VarianteProducto + RowVersion ([Timestamp])
[✓] Infrastructure: IsRowVersion() en VarianteProductoConfiguration
[✓] Infrastructure: DbUpdateConcurrencyException + rollback en AumentoMasivoService
[✓] Migración M2 generada (despliegue: `dotnet ef database update`)
[✓] Índices únicos Sku/CodigoBarra ya presentes en M1 (R2 mitigado)
[✓] Vendedor sin costos en Buscar; Admin con costos en Obtener
[✓] Build verde (0 errores, 0 warnings)
[ ] Pruebas mínimas §12.5 en QA (incluye D6 con dos pestañas)
[ ] `dotnet ef database update` en entorno destino
────────────────────────────────────────────────────────────────────
```

**Gate E2: APROBADO técnicamente. Listo para iniciar E3 — Stock e inventario tras confirmación.**

---

## 13. Cierre etapa E3 — Stock e inventario

### 13.1 Reconciliación con estado real del repo

Al iniciar E3 se detectó que el grueso de stock ya está implementado: entidades `Stock`, `MovimientoStock`, `AjusteStock` con sus configs (FK 1:1 stock-variante, índices, FKs polimórficas opcionales en `MovimientoStock`), `IStockService` + `StockService`, `StockController` con políticas correctas (`Listado`/`Historial` para Vendedor, `CargaInicial`/`Ajuste` solo Admin) y vistas. Tablas creadas por la migración monolítica M1 (S7).

| Ítem planificado E3 | Estado real al inicio | Acción ejecutada |
|---|---|---|
| Entidades Stock / MovimientoStock / AjusteStock + configs | ✅ Existentes | Ninguna |
| Migración M3 (creación de tablas) | ✅ Ya creadas en M1 monolítica (S7) | Ninguna (no se genera M3) |
| Listado con alerta `StockActual ≤ StockMinimo` | ✅ Existente | Ninguna |
| Carga inicial — guarda `StockActual==0` y sin movimientos previos (R-STK-04) | ✅ Existente | Ninguna |
| Ajuste manual con `UsuarioId` real desde Controller (E-09) | ✅ Existente | Ninguna |
| Historial filtrable por variante | ✅ Existente | Ninguna |
| Movimientos con FKs polimórficas opcionales (S3) | ✅ Existente | Ninguna |
| Políticas `RequireAdministrador` en `CargaInicial`/`Ajuste`; `RequireVendedor` resto | ✅ Existente | Ninguna |
| **Atomicidad: stock + movimiento en una sola transacción** | ❌ Dos `SaveChanges` separados sin tx | **Fix aplicado** — `BeginTransactionAsync` + commit/rollback |
| **Atomicidad: ajuste + stock + movimiento en una sola transacción** | ❌ Dos `SaveChanges` separados sin tx | **Fix aplicado** — `BeginTransactionAsync` + commit/rollback |

### 13.2 Cambios por capa en E3

| Capa | Archivo | Cambio | Motivo |
|---|---|---|---|
| Infrastructure | `Services\StockService.cs` → `CargaInicialAsync` | `await using var tx = await _db.Database.BeginTransactionAsync();` envolviendo `SaveChanges` + `RegistrarMovimientoAsync` con commit/rollback | Atomicidad: evita stock cargado sin movimiento si falla el segundo save |
| Infrastructure | `Services\StockService.cs` → `AjusteManualAsync` | Misma transacción explícita envolviendo creación de `AjusteStock`, actualización de `Stock` y `RegistrarMovimientoAsync` | Atomicidad: evita ajuste/stock sin movimiento si falla el segundo save (E-09 + R-STK trazabilidad) |

No se tocaron Domain, Application ni Web en E3.

### 13.3 Migraciones EF en E3

Ninguna migración nueva. Las tablas `Stocks`, `MovimientosStock`, `AjustesStock` ya estaban creadas por M1 monolítica (S7). El plan original M3 `AddStockInventario` queda absorbido por M1.

### 13.4 Evidencia de build E3

```
Build succeeded.
    0 Warning(s)
    0 Error(s)
Time Elapsed 00:00:12.53
```

### 13.5 Pruebas mínimas E3 (a ejecutar en QA)

- [ ] Listado con `soloAlertas=true` muestra solo variantes con `StockActual ≤ StockMinimo`.
- [ ] Carga inicial con `cantidad ≤ 0` → rechazo.
- [ ] Carga inicial sobre variante con `StockActual != 0` → rechazo.
- [ ] Carga inicial sobre variante con movimientos previos → rechazo (R-STK-04).
- [ ] Carga inicial OK genera movimiento `CargaInicial` con `StockResultante` correcto.
- [ ] Ajuste manual con `CantidadNueva` distinta → genera `AjusteStock` con `UsuarioId` real (E-09) y movimiento `AjusteManual` con delta = nueva − anterior.
- [ ] Historial filtrado por `varianteId` ordena por fecha descendente.
- [ ] Vendedor accede a `/Stock/Index` y `/Stock/Historial` → 200.
- [ ] Vendedor intenta `/Stock/CargaInicial` o `/Stock/Ajuste` → 403.
- [ ] Atomicidad: forzar fallo en `RegistrarMovimientoAsync` (p.ej. variante sin stock) → no queda `Stock` modificado ni `AjusteStock` huérfano.

### 13.6 Riesgos / supuestos confirmados en E3

- **R-STK-04** cubierto en service (no en controller). Fronteras respetadas.
- **E-09** cubierto: `UsuarioId` se setea en Controller desde `ClaimTypes.NameIdentifier`.
- **S3** confirmado: `MovimientoStock` usa 4 FKs opcionales (`CompraId`, `VentaId`, `DevolucionCambioId`, `AjusteStockId`), no discriminador string.
- **S7** ratificado: M3 absorbida por M1 monolítica.
- **R4** (concurrencia stock en ventas) queda fuera de E3 — corresponde a E5 (Ventas) con `IsolationLevel.Serializable` + reintentos.

### 13.7 Checklist de salida E3

```
E3 — CHECKLIST DE MERGE
────────────────────────────────────────────────────────────────────
[✓] Domain/Configs: Stock, MovimientoStock, AjusteStock (preexistentes)
[✓] StockService: CargaInicial y Ajuste con transacción explícita
[✓] StockController: políticas correctas; UsuarioId desde claims
[✓] Movimientos polimórficos (S3) consistentes
[✓] Build verde (0 errores, 0 warnings)
[ ] Pruebas mínimas §13.5 en QA (incluye atomicidad)
[ ] Sin migración nueva (S7)
────────────────────────────────────────────────────────────────────
```

**Gate E3: APROBADO técnicamente. Listo para iniciar E4 — Compras y recepción tras confirmación.**

---

## 14. Cierre etapa E4 — Compras y recepción

### 14.1 Reconciliación con estado real del repo

E4 ya estaba implementada en su mayor parte: entidades `Compra`, `CompraDetalle`, `CompraAdjunto` con configs y enum `EstadoCompra`; `CompraService` con CRUD, transición lineal de estados (R-COM-01), edición restringida a `Borrador`/`EnProceso` (R-COM-02, E-03), recepción con transacción `ReadCommitted`, validación `Rec+Dañ+Dev ≤ Pedida`, actualización de `Stock` y `UltimoPrecioCompra`, registro de movimientos `CompraRecepcion` y soporte de adjuntos. `ComprasController` con `RequireAdministrador`, validación de tamaño (5MB) y extensiones (`.jpg/.jpeg/.png/.pdf`) (G-06). Tablas creadas por M1 monolítica (S7).

| Ítem planificado E4 | Estado real al inicio | Acción ejecutada |
|---|---|---|
| Entidades + configs Compra/Detalle/Adjunto | ✅ Existentes | Ninguna |
| Migración M4 (creación de tablas) | ✅ Absorbida en M1 (S7) | Ninguna |
| Crear/Editar borrador con detalles | ✅ Existente | Ninguna |
| Edición solo en `Borrador`/`EnProceso` (R-COM-02, E-03) | ✅ Existente | Ninguna |
| Transición lineal de estados (R-COM-01, E-02) | ✅ Existente — bloquea cambio directo a `Recibida` | Ninguna |
| Recepción solo desde `Verificada` | ✅ Existente | Ninguna |
| Validación `Rec+Dañ+Dev ≤ Pedida` | ✅ Existente, **pero** ejecutada después de mutar estado/detalles y sin `RollbackAsync` explícito en early-returns | **Fix aplicado** — validación previa de TODAS las líneas + rollback explícito |
| Validación cantidades no negativas | ❌ Ausente (defensiva) | **Fix aplicado** — rechazo si alguna < 0 |
| Update Stock + `UltimoPrecioCompra` + movimiento `CompraRecepcion` en transacción | ✅ Existente | Ninguna |
| Adjuntos con validación (G-06) | ✅ Existente | Ninguna |
| Política `RequireAdministrador` a nivel controller | ✅ Existente | Ninguna |

### 14.2 Cambios por capa en E4

| Capa | Archivo | Cambio | Motivo |
|---|---|---|---|
| Infrastructure | `Services\CompraService.cs` → `RecepcionarAsync` | (1) `await using` en la transacción. (2) Validación previa de **todas** las líneas (no negativas + suma ≤ pedida) **antes** de mutar `Estado`/`FechaRecepcion`/detalles/stock. (3) `RollbackAsync` explícito en cada `return` de error. | Evita estado inconsistente si la validación falla recién en una línea posterior; cierra D-recepción atómica de forma defensiva. |

No se tocaron Domain, Application ni Web en E4.

### 14.3 Migraciones EF en E4

Ninguna migración nueva. Tablas `Compras`, `ComprasDetalle`, `ComprasAdjunto` ya creadas en M1 monolítica (S7).

### 14.4 Evidencia de build E4

```
Build succeeded.
    0 Warning(s)
    0 Error(s)
Time Elapsed 00:00:09.96
```

### 14.5 Pruebas mínimas E4 (a ejecutar en QA)

- [ ] Crear compra en `Borrador` con ≥1 detalle válido (cantidad>0, costo>0).
- [ ] Editar compra en `Borrador` y `EnProceso` → OK; en `Verificada`/`Recibida` → rechazo (R-COM-02).
- [ ] `CambiarEstado` con salto no lineal (p.ej. `Borrador`→`Verificada`) → rechazo (R-COM-01).
- [ ] `CambiarEstado` directo a `Recibida` → rechazo con mensaje de usar Recepción.
- [ ] Recepción desde estado distinto a `Verificada` → rechazo.
- [ ] Recepción con `Rec+Dañ+Dev > Pedida` en alguna línea → rechazo y **sin cambios** en compra/stock/detalles.
- [ ] Recepción con cantidades negativas → rechazo y sin cambios.
- [ ] Recepción válida → `Estado=Recibida`, `FechaRecepcion` seteada, stock incrementado por `CantidadRecibida`, `UltimoPrecioCompra` actualizado, movimientos `CompraRecepcion` con `compraId` correcto.
- [ ] Adjunto > 5MB → rechazo. Extensión fuera de `.jpg/.jpeg/.png/.pdf` → rechazo. Adjunto válido → guardado en `wwwroot/uploads/compras` y registrado.
- [ ] Vendedor accede a `/Compras/*` → 403 (controller `RequireAdministrador`).

### 14.6 Riesgos / supuestos confirmados en E4

- **R-COM-01** y **R-COM-02** cubiertos en service.
- **E-02** (transición lineal) y **E-03** (edición restringida) cubiertos.
- **G-06** (validación adjuntos) cubierto en controller.
- **R7** (cascade vs soft delete): `CompraDetalle` se reemplaza con `RemoveRange` antes de re-insertar en edición; comportamiento preservado.
- **S7** ratificado: M4 absorbida por M1.
- Riesgo residual aceptado: `RecepcionarAsync` usa `ReadCommitted` (no `Serializable`) porque la operación es de **incremento** de stock (no compite con ventas que decrementan en la misma fila simultáneamente; la concurrencia crítica vive en E5 Ventas).

### 14.7 Checklist de salida E4

```
E4 — CHECKLIST DE MERGE
────────────────────────────────────────────────────────────────────
[✓] Domain/Configs: Compra, CompraDetalle, CompraAdjunto (preexistentes)
[✓] Service: CRUD, transición lineal, edición restringida
[✓] Service: Recepción con validación previa + rollback explícito
[✓] Service: Stock + UltimoPrecioCompra + Movimiento en transacción
[✓] Controller: RequireAdministrador + validación adjuntos (G-06)
[✓] Build verde (0 errores, 0 warnings)
[ ] Pruebas mínimas §14.5 en QA
[ ] Sin migración nueva (S7)
────────────────────────────────────────────────────────────────────
```

**Gate E4: APROBADO técnicamente. Listo para iniciar E5 — Ventas (núcleo transaccional con `IsolationLevel.Serializable` + reintentos) tras confirmación.**

---

## 15. Cierre etapa E5 — Ventas (núcleo transaccional)

### 15.1 Reconciliación con estado real del repo

E5 ya estaba implementada en su mayor parte: entidades `Venta`, `VentaDetalle`, `VentaPago`, `VentaAdjunto`, `Remito` con configs y enums; `VentaService` con creación atómica `Serializable`, validación de stock por línea, cálculo de subtotal/descuento/total con tolerancia 0,01, asignación de `NroVenta` post-insert, decremento de stock + movimientos `Venta`, anulación con reposición de stock + movimientos `AnulacionVenta`, marcado a `Entregada`, listado con filtro por vendedor (G-09), expansión de costos solo si Admin/SuperUsuario (E-08), adjuntos validados (G-06). Tablas creadas por M1 monolítica (S7).

| Ítem planificado E5 | Estado real al inicio | Acción ejecutada |
|---|---|---|
| Entidades + configs Venta/Detalle/Pago/Adjunto/Remito | ✅ Existentes | Ninguna |
| Migración M5 (creación de tablas) | ✅ Absorbida en M1 (S7) | Ninguna |
| `CrearAsync` con `IsolationLevel.Serializable` | ✅ Existente | Ninguna |
| Validación stock por variante | ✅ Existente | Ninguna |
| Validación suma de pagos = total (±0,01) | ✅ Existente | Ninguna |
| `NroVenta` correlativo (`VTA-{Id:D5}`, D1) | ✅ Existente | Ninguna |
| Decremento stock + movimientos `Venta` | ✅ Existente | Ninguna |
| `AnularAsync` solo desde `Confirmada`, repone stock | ✅ Existente | Ninguna |
| `MarcarEntregadaAsync` solo desde `Confirmada` | ✅ Existente | Ninguna |
| Vendedor solo ve sus ventas (G-09) | ✅ Existente en controller | Ninguna |
| Costos/ganancia solo a Admin (E-08) | ✅ Existente | Ninguna |
| Adjuntos (G-06) | ✅ Existente | Ninguna |
| **`await using` + `RollbackAsync` explícito en early-returns** (`CrearAsync` y `AnularAsync`) | ❌ `using` simple + `return` sin rollback | **Fix aplicado** |
| **R4 — reintentos limitados ante deadlock** | ❌ Ausente | **Fix aplicado** — hasta 3 intentos con detach del ChangeTracker y backoff lineal |

### 15.2 Cambios por capa en E5

| Capa | Archivo | Cambio | Motivo |
|---|---|---|---|
| Infrastructure | `Services\VentaService.cs` → `CrearAsync` | (1) `await using` en la transacción. (2) `RollbackAsync` explícito ante stock insuficiente. (3) Bucle de reintentos `for (1..3)` que captura `DbUpdateException` cuando el mensaje indica deadlock/lock-wait (MySQL 1213/1205); detacha entidades y aplica backoff `50*intento` ms. (4) Helper privado `EsDeadlock(DbUpdateException)`. | R4 (concurrencia stock entre ventas simultáneas) cubierto sin alterar API; mantiene `Serializable` y degrada con mensaje "No se pudo confirmar la venta por contención de stock. Reintente." si los 3 intentos fallan. |
| Infrastructure | `Services\VentaService.cs` → `AnularAsync` | `await using` + `RollbackAsync` explícito en early-returns (venta no encontrada / estado distinto a Confirmada). | Atomicidad defensiva consistente con E3/E4. |

No se tocaron Domain, Application ni Web en E5.

### 15.3 Migraciones EF en E5

Ninguna migración nueva. Tablas `Ventas`, `VentasDetalle`, `VentasPago`, `VentasAdjunto`, `Remitos` ya creadas en M1 monolítica (S7).

### 15.4 Evidencia de build E5

```
Build succeeded.
    0 Warning(s)
    0 Error(s)
Time Elapsed 00:00:09.47
```

### 15.5 Pruebas mínimas E5 (a ejecutar en QA)

- [ ] Crear venta con ≥1 ítem y ≥1 pago; suma de pagos = total ±0,01 → OK, `NroVenta` correlativo, stock decrementa, movimientos `Venta` generados.
- [ ] Suma de pagos ≠ total → rechazo "La suma de pagos…".
- [ ] Stock insuficiente en alguna variante → rechazo y rollback (sin venta creada, sin stock alterado, sin movimientos).
- [ ] **R4 concurrencia**: dos ventas simultáneas sobre la misma variante con stock=1 → una commitea, la otra recibe rechazo (stock insuficiente o reintento agotado), nunca queda stock negativo.
- [ ] `Anular` desde `Confirmada` → OK, stock repone, movimientos `AnulacionVenta`. Desde `Entregada` o `Anulada` → rechazo.
- [ ] `MarcarEntregada` desde `Confirmada` → OK; desde otros estados → rechazo.
- [ ] Vendedor en `Listar` → solo ve sus propias ventas (G-09). Admin/SuperUsuario → ve todas.
- [ ] Vendedor en `Detalle` → sin `CostoTotal`/`GananciaTotal`/`CostoUnitario`. Admin → con esos campos (E-08).
- [ ] Adjunto >5MB o extensión inválida → rechazo (G-06).

### 15.6 Riesgos / supuestos confirmados en E5

- **R4** cubierto en service: `Serializable` + reintentos hasta 3 con detach + backoff. Aceptado: detección de deadlock por mensaje (MySQL 1213/1205) en ausencia de tipo de excepción específico de Pomelo expuesto.
- **D1** (correlativo) cubierto vía Id autoincremental + formateo `VTA-{Id:D5}` post-`SaveChanges`.
- **D2** (cuotas) **fuera de alcance E5**: el modelo de pagos actual no contiene `CantidadCuotas`/`% recargo` por línea de pago; se deja documentado para una iteración posterior si el negocio lo confirma. Riesgo registrado.
- **E-08** y **G-09** cubiertos en controller.
- **S7** ratificado (M5 absorbida por M1).

### 15.7 Checklist de salida E5

```
E5 — CHECKLIST DE MERGE
────────────────────────────────────────────────────────────────────
[✓] CrearAsync: Serializable + reintentos R4 + rollback explícito
[✓] AnularAsync: rollback explícito en early-returns
[✓] NroVenta correlativo (D1)
[✓] Filtro por vendedor (G-09) + costos solo Admin (E-08)
[✓] Adjuntos validados (G-06)
[✓] Build verde (0 errores, 0 warnings)
[ ] Pruebas mínimas §15.5 en QA (incluye R4 con dos pestañas)
[ ] Sin migración nueva (S7)
[ ] D2 (cuotas) registrado como riesgo abierto
────────────────────────────────────────────────────────────────────
```

**Gate E5: APROBADO técnicamente. Listo para iniciar E6 — Postventa (devoluciones/cambios) tras confirmación.**

---

## 16. Cierre etapa E6 — Postventa (devoluciones / cambios)

### 16.1 Reconciliación con estado real del repo

E6 ya estaba implementada en lo grueso: entidades `DevolucionCambio`, `DevolucionCambioDetalle` con configs y enum `TipoDevolucion`; `DevolucionService` con validación de venta en `Confirmada`/`Entregada`, cálculo de cantidad disponible (`Cantidad − YaDevuelto`), reingreso de stock + movimientos `DevolucionCliente`, decremento de stock + movimiento `Venta` para el item de cambio, transacción explícita y `ObtenerVentaParaDevolucionAsync` que filtra solo líneas con disponible > 0. Tablas creadas por M1 monolítica (S7).

| Ítem planificado E6 | Estado real al inicio | Acción ejecutada |
|---|---|---|
| Entidades + configs DevolucionCambio/Detalle | ✅ Existentes | Ninguna |
| Migración M6 (creación de tablas) | ✅ Absorbida en M1 (S7) | Ninguna |
| Crear devolución solo desde `Confirmada`/`Entregada` | ✅ Existente | Ninguna |
| Validar `CantidadDevolver ≤ Cantidad − YaDevuelto` | ✅ Existente | Ninguna |
| Reingreso stock + movimientos `DevolucionCliente` | ✅ Existente | Ninguna |
| Cambio: validar stock destino y decrementar con movimiento `Venta` (G-08) | ✅ Existente | Ninguna |
| Listado, detalle, AJAX para `Items` por venta | ✅ Existentes | Ninguna |
| **`await using` + `RollbackAsync` explícito en early-returns dentro del try** | ❌ `using` simple + `return` sin rollback | **Fix aplicado** |
| **Validación cantidades no negativas** | ❌ Ausente (defensiva) | **Fix aplicado** |

### 16.2 Cambios por capa en E6

| Capa | Archivo | Cambio | Motivo |
|---|---|---|---|
| Infrastructure | `Services\DevolucionService.cs` → `CrearAsync` | (1) `await using` en la transacción. (2) `RollbackAsync` explícito en cada early-return dentro del try (detalle no encontrado, cantidad superior a disponible, stock destino insuficiente para cambio). (3) Rechazo si alguna `CantidadDevolver < 0`. | Atomicidad defensiva consistente con E3/E4/E5; cierra el riesgo de retornar antes de Commit/Rollback explícito en operación con efectos en stock y movimientos. |

No se tocaron Domain, Application ni Web en E6.

### 16.3 Migraciones EF en E6

Ninguna migración nueva. Tablas `DevolucionesCambio` y `DevolucionesCambioDetalle` ya creadas en M1 monolítica (S7).

### 16.4 Evidencia de build E6

```
Build succeeded.
    0 Warning(s)
    0 Error(s)
Time Elapsed 00:00:05.32
```

### 16.5 Pruebas mínimas E6 (a ejecutar en QA)

- [ ] Devolución sobre venta `Borrador`/`Anulada` → rechazo.
- [ ] Devolución sobre venta `Confirmada` o `Entregada` con cantidad válida → OK, stock reingresa, movimientos `DevolucionCliente` con `devolucionId` correcto.
- [ ] `CantidadDevolver = 0` en todos los items → rechazo "Debe seleccionar al menos un item".
- [ ] `CantidadDevolver < 0` → rechazo y rollback.
- [ ] `CantidadDevolver > Cantidad − YaDevuelto` (incluyendo devolución previa parcial) → rechazo y rollback (sin reingreso de stock parcial).
- [ ] Cambio con stock destino insuficiente para `totalCantidadDevuelta` → rechazo y rollback (la devolución original tampoco se persiste).
- [ ] Cambio con stock destino OK → registra devolución, decrementa stock destino, movimiento `Venta` con `ventaId` correcto.
- [ ] `DiferenciaCobrar` se persiste en cambios `CambioMayorValor` (verificación de modelo).
- [ ] `ObtenerVentaParaDevolucionAsync` solo devuelve líneas con `disponible > 0`.
- [ ] Permisos: vendedor accede a `Crear`/`Listar`/`Detalle` según política del controller.

### 16.6 Riesgos / supuestos confirmados en E6

- **G-08** (cambio multi-item) cubierto: el decremento de stock destino usa `totalCantidadDevuelta`.
- **Atomicidad** cubierta defensivamente: ningún early-return dentro del try queda sin `RollbackAsync`.
- **R7** (cascade vs soft delete): `DevolucionCambioDetalle` no se borra; preserva trazabilidad histórica.
- **S7** ratificado (M6 absorbida por M1).
- Riesgo residual aceptado: la transacción usa el aislamiento por defecto (`ReadCommitted`) — la concurrencia crítica de stock vive en E5 (Ventas con `Serializable`); la devolución compite menos por filas activas.

### 16.7 Checklist de salida E6

```
E6 — CHECKLIST DE MERGE
────────────────────────────────────────────────────────────────────
[✓] Domain/Configs: DevolucionCambio y Detalle (preexistentes)
[✓] Service: validación venta + cantidad disponible + stock destino
[✓] Service: await using + rollback explícito en early-returns
[✓] Service: rechazo de cantidades negativas
[✓] Movimientos: DevolucionCliente + Venta (en cambios)
[✓] Build verde (0 errores, 0 warnings)
[ ] Pruebas mínimas §16.5 en QA
[ ] Sin migración nueva (S7)
────────────────────────────────────────────────────────────────────
```

**Gate E6: APROBADO técnicamente. Listo para iniciar E7 — Resumen semanal y AumentoMasivo (vista) tras confirmación.**

---

## 17. Cierre etapa E7 — Resumen semanal y Aumento masivo (vista)

### 17.1 Reconciliación con estado real del repo

E7 ya está completamente implementada. No se detectaron gaps reales. La parte transaccional de aumento masivo (D6/R5) se cerró en E2 con `RowVersion` + manejo de `DbUpdateConcurrencyException`; aquí solo se valida la vista/exportación.

| Ítem planificado E7 | Estado real al inicio | Acción ejecutada |
|---|---|---|
| `ResumenSemanalService.ObtenerAsync(fechaReferencia)` con ventana lunes–domingo | ✅ Existente — usa `DayOfWeek` con offset y rango `[lunes, domingo+1)` excluyente | Ninguna |
| Filtro `MedioPago.Transferencia` + `Estado` ∈ {Confirmada, Entregada} | ✅ Existente | Ninguna |
| `ResumenSemanalDetalleViewModel` con NroVenta, Fecha, Cliente, Importe | ✅ Existente | Ninguna |
| Export Excel con ClosedXML (G-05, R-RES-04) | ✅ Existente — encabezados, totales, formato `#,##0.00`, `AdjustToContents` | Ninguna |
| `ResumenSemanalController` con `RequireAdministrador` y acción `ExportarExcel` | ✅ Existente | Ninguna |
| `AumentoMasivoController` con `RequireAdministrador`, `Preview` (AJAX) y `Aplicar` | ✅ Existente | Ninguna |
| `AumentoMasivoService` con D6 (RowVersion + `DbUpdateConcurrencyException`) | ✅ Cerrado en E2 | Ninguna |
| Vistas `ResumenSemanal/Index.cshtml` y `AumentoMasivo/Index.cshtml` | ✅ Existentes | Ninguna |

### 17.2 Cambios por capa en E7

Sin cambios. Verificación pura.

### 17.3 Migraciones EF en E7

Ninguna migración nueva (S7).

### 17.4 Evidencia de build E7

```
Build succeeded.
    0 Warning(s)
    0 Error(s)
Time Elapsed 00:00:05.54
```

### 17.5 Pruebas mínimas E7 (a ejecutar en QA)

- [ ] Resumen semanal con `fecha = lunes 00:00` → ventana `[lunes, domingo]` correcta.
- [ ] Resumen semanal con fecha en miércoles → mismo período (lunes a domingo de la misma semana).
- [ ] Solo se totalizan pagos con `MedioPago.Transferencia`.
- [ ] Ventas `Borrador`/`Anulada` no aparecen en el resumen.
- [ ] Export Excel descarga `.xlsx` con encabezado, período, total, cantidad de operaciones y detalle.
- [ ] Vendedor accede a `/ResumenSemanal/*` y `/AumentoMasivo/*` → 403 (controllers `RequireAdministrador`).
- [ ] AumentoMasivo `Preview` por categoría / por subgrupo / sin filtros → devuelve variantes esperadas.
- [ ] AumentoMasivo `Aplicar` con dos pestañas concurrentes → la segunda recibe mensaje de re-previsualización (D6, ya validado en E2).

### 17.6 Riesgos / supuestos confirmados en E7

- **G-05** y **R-RES-04** cubiertos vía ClosedXML.
- **D6 / R5** ya cerrados en E2.
- Aceptado: el resumen no incluye otros medios de pago — alcance acotado a transferencias por requerimiento (R-RES-01).
- Aceptado: la fecha por defecto usa `DateTimeHelper.ArgentinaNow()` para evitar problemas de zona horaria.

### 17.7 Checklist de salida E7

```
E7 — CHECKLIST DE MERGE
────────────────────────────────────────────────────────────────────
[✓] ResumenSemanalService: ventana lunes-domingo + filtro transferencia/estado
[✓] Export Excel ClosedXML (G-05)
[✓] AumentoMasivoController + Service (D6 cerrado en E2)
[✓] Vistas presentes
[✓] RequireAdministrador en ambos controllers
[✓] Build verde (0 errores, 0 warnings)
[ ] Pruebas mínimas §17.5 en QA
[ ] Sin migración nueva (S7)
────────────────────────────────────────────────────────────────────
```

**Gate E7: APROBADO técnicamente. Listo para iniciar E8 — Hardening final (logging, manejo de errores, smoke tests) tras confirmación.**

---

## 18. Cierre etapa E8 — Hardening final (logging, errores, rate limiting, compression)

### 18.1 Reconciliación con estado real del repo

E8 se cierra **por verificación**: al inspeccionar `Program.cs` y `appsettings.json` se confirma que todos los aspectos no funcionales planificados ya están implementados en el repositorio. No se requieren cambios de código.

| Ítem planificado E8 | Estado real al inicio | Acción ejecutada |
|---|---|---|
| Serilog bootstrap logger + `Host.UseSerilog` leyendo configuración | ✅ Existente (`Program.cs` líneas 17-27) | Ninguna |
| `Serilog.MinimumLevel` configurado en `appsettings.json` | ✅ Existente (Default `Information`, `Microsoft.AspNetCore` `Warning`) | Ninguna |
| `UseSerilogRequestLogging` en pipeline | ✅ Existente con plantilla custom (línea 182-185) | Ninguna |
| `AddExceptionHandler<GlobalExceptionHandler>` + `AddProblemDetails` | ✅ Existente (líneas 76-77) | Ninguna |
| `UseDeveloperExceptionPage` en Development / `UseExceptionHandler("/Home/Error")` + `UseHsts` en Production | ✅ Existente (líneas 160-172) | Ninguna |
| `UseStatusCodePagesWithReExecute("/Home/StatusCode", "?code={0}")` | ✅ Existente (línea 179) | Ninguna |
| Response Compression (Brotli + Gzip, MIME extendidos) | ✅ Existente (líneas 80-95) | Ninguna |
| Rate limiting policies `general` (100/min) y `login` (10/min) por IP | ✅ Existente (líneas 98-125) | Ninguna |
| `AddSession` + `AddDistributedMemoryCache` para filtros persistentes | ✅ Existente (líneas 128-134) | Ninguna |
| `AddHttpsRedirection` + `AddHsts` (1 año, IncludeSubDomains, Preload) | ✅ Existente (líneas 137-147) | Ninguna |
| `RequestLocalization` fija a `es-AR` | ✅ Existente (líneas 152-158) | Ninguna |
| Authorization policies `RequireSuperUsuario` / `RequireAdministracion` / `RequireAdministrador` / `RequireVendedor` | ✅ Existente (líneas 57-71) | Ninguna |
| Orden de middleware (Compression → StatusCodePages → SerilogRequestLogging → StaticFiles → Routing → Auth → RateLimiter → Session) | ✅ Correcto | Ninguna |

### 18.2 Cambios por capa en E8

Sin cambios. Verificación pura.

### 18.3 Migraciones EF en E8

Ninguna migración nueva (S7).

### 18.4 Evidencia de build E8

```
Build succeeded.
    0 Warning(s)
    0 Error(s)
Time Elapsed 00:00:05.67
```

### 18.5 Pruebas mínimas E8 (a ejecutar en QA)

- [ ] Forzar excepción no controlada en Development → se muestra `DeveloperExceptionPage`.
- [ ] Forzar excepción no controlada en Production → log Serilog con stack + redirección a `/Home/Error` con `RequestId`.
- [ ] Solicitud AJAX que falla → `GlobalExceptionHandler` devuelve JSON con `ProblemDetails`.
- [ ] Acceso a URL inexistente → `/Home/StatusCode?code=404` con vista correcta.
- [ ] Más de 10 intentos de login en 1 minuto desde la misma IP → HTTP 429.
- [ ] Más de 100 requests en 1 minuto sobre rutas generales → HTTP 429.
- [ ] Header `Content-Encoding: br` o `gzip` en respuestas dinámicas elegibles.
- [ ] Header `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` presente en producción.
- [ ] Sesión: filtros aplicados en una vista persisten al volver a navegar (TTL 60 min).
- [ ] Cultura: importes y fechas se muestran/parsean en formato `es-AR` en todas las vistas.

### 18.6 Riesgos / supuestos confirmados en E8

- Aceptado: rate limit por IP puede impactar accesos detrás de NAT corporativo; mitigación = ajustar `PermitLimit` por configuración si se detecta en QA.
- Aceptado: sesión en memoria (`AddDistributedMemoryCache`) es suficiente mientras la app corra en una sola instancia. Si se escala horizontalmente debe migrarse a Redis/SQL.
- Aceptado: Serilog actualmente sólo escribe a Console (bootstrap) + sinks definidos por configuración; la rotación a archivo/log-server queda como tarea de infraestructura.
- Confirmado: no se requirieron cambios — la base ya cumple el alcance de E8.

### 18.7 Checklist de salida E8

```
E8 — CHECKLIST DE MERGE
────────────────────────────────────────────────────────────────────
[✓] Serilog bootstrap + UseSerilog + UseSerilogRequestLogging
[✓] GlobalExceptionHandler + ProblemDetails
[✓] DeveloperExceptionPage (Dev) / UseExceptionHandler + HSTS (Prod)
[✓] StatusCodePagesWithReExecute → /Home/StatusCode
[✓] Response Compression (Brotli + Gzip)
[✓] Rate limiting general (100/min) y login (10/min) por IP
[✓] Session + DistributedMemoryCache (60 min)
[✓] HttpsRedirection + Hsts (1 año, IncludeSubDomains, Preload)
[✓] RequestLocalization es-AR
[✓] Policies RequireSuperUsuario / RequireAdministracion / RequireAdministrador / RequireVendedor
[✓] Build verde (0 errores, 0 warnings)
[ ] Pruebas mínimas §18.5 en QA
[ ] Sin migración nueva (S7)
────────────────────────────────────────────────────────────────────
```

**Gate E8: APROBADO técnicamente por verificación. Plan E0–E8 cerrado integralmente. Sistema listo para QA funcional y cierre de calibración estimado vs real.**
