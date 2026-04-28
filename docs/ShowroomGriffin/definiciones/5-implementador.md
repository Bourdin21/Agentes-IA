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
| Etapas ejecutadas | ✅ 2 / 9 (E0, E1 cerradas) |

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
