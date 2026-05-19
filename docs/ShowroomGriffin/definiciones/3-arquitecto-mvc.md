# 3 — Arquitectura MVC v2
## Sistema de Gestión Comercial — ShowroomGriffin
**Versión:** 2.0  
**Estado:** En definición  
**Base:** `1-analista-funcional.md` v2 + `2-disenador-funcional.md` v2 (ambos aprobados)  
**Predecesor:** v1.0 (arquitectura base F0–F8 implementada y operativa)

> Este documento cubre exclusivamente el impacto arquitectónico de los 12 cambios v2 (C01–C12).  
> La arquitectura base (v1) permanece vigente y no se repite aquí.

---

## 1. Alcance funcional resumido

4 etapas de implementación (V1-E1 a V1-E4) sobre la base existente:

- **V1-E1 — Refactor estructural:** nueva jerarquía Categoría→Marca→Modelo + TalleConfig. Bloquea todo lo demás.
- **V1-E2 — Combos anidados en Ventas/Compras:** 5 combos AJAX + campo Anotaciones + autofill pago + precios editables.
- **V1-E3 — Modal cliente + Búsqueda rápida devoluciones:** CrearRapido cliente, búsqueda multi-criterio en Dev/Cambios.
- **V1-E4 — Rol Empleado + mejora visual Stock:** nueva policy + menú dinámico + indicadores visuales.

---

## 2. Stack y reutilización (delta v2)

Todo el stack base (EF Core 10, MySQL 8, Identity, Bootstrap 5, jQuery, Select2, SweetAlert2, Serilog, ServiceResult, DataTableRequest/Response, SoftDestroyable) se **reutiliza sin cambios**.

Piezas nuevas estrictamente necesarias:
| Componente | Justificación |
|---|---|
| 2 entidades nuevas (`Marca` renombrada de `Subgrupo`, `Modelo`, `TalleConfig`) | No existe equivalente en base |
| 2 nuevas interfaces de servicio (`IMarcaService`, `IModeloService`) | Nuevas entidades |
| 1 enum nuevo (`TipoTalle`) | Distingue catálogos de talles |
| 1 policy nueva (`RequireEmpleado`) | Nuevo rol |
| 3 controllers nuevos (`MarcasController`, `ModelosController`; `SubgruposController` reemplazado) | Nueva jerarquía |
| 3 migraciones EF (MR-1..MR-3) | Cambios estructurales en DB |

**No** se introducen nuevas librerías, paquetes NuGet, patrones ni pipelines.

---

## 3. Impacto técnico por capa

### 3.1 Domain (`ShowroomGriffin.Domain`)

#### Entidades RENOMBRADAS / REFACTORIZADAS

| Entidad | Cambio | Riesgo |
|---|---|---|
| `Subgrupo` | Renombrar clase a `Marca` y navegar con colección `Modelos` en lugar de solo `Productos`. Mantener nombre de tabla `Marcas` via `ToTable("Marcas")` en EF config. | Medio: todas las referencias a `Subgrupo` en servicios/controllers/vistas/configs deben actualizarse. |
| `Producto` | Agregar `MarcaId` (int, FK a `Marca`), `ModeloId` (int?, FK a `Modelo`). Quitar navegación a `Subgrupo`, agregar navegaciones a `Marca` y `Modelo`. | Medio: `ProductoConfiguration`, `ProductoService`, `ProductoViewModel` afectados. |
| `VarianteProducto` | Quitar propiedades `Marca` (string?) y `Modelo` (string?). Quitar `Talle` (string?) y `Numero` (string?). Agregar `TalleId` (int?, FK a `TalleConfig`). | **Alto**: config EF, service, ViewModel, combos en UI y script de migración de datos. |
| `Venta` | Renombrar `Observaciones` → `Anotaciones` (campo renombrado, mismo tipo string?). | Bajo: config EF + service + ViewModel + vistas. |

#### Entidades NUEVAS

| Entidad | Namespace | Propiedades clave | Hereda |
|---|---|---|---|
| `Modelo` | `Domain.Entities.Maestros` | `Id`, `Nombre` (string), `MarcaId` (int) | `SoftDestroyable` |
| `TalleConfig` | `Domain.Entities.Maestros` | `Id`, `Valor` (string), `Tipo` (enum `TipoTalle`) | `SoftDestroyable` |

#### Enum NUEVO

```csharp
// Domain/Enums/TipoTalle.cs
public enum TipoTalle
{
    ZapatillaAdulto = 1,
    ZapatillaNino   = 2,
    Indumentaria    = 3
}
```

#### Reglas de dominio (sin cambios de patrón)
- Sin lógica de negocio en entidades.
- `SoftDestroyable` heredada por todas las entidades nuevas.
- `RowVersion` en `VarianteProducto` se mantiene (sigue activo para D6).

#### Árbol de archivos afectados — Domain
```
Domain/
  Entities/
    Maestros/
      Subgrupo.cs           → RENOMBRAR a Marca.cs + agregar Modelos collection
      Modelo.cs             → NUEVO
      TalleConfig.cs        → NUEVO
    Productos/
      Producto.cs           → MODIFICAR (MarcaId + ModeloId, quitar SubgrupoId)
      VarianteProducto.cs   → MODIFICAR (quitar Marca/Modelo/Talle/Numero, agregar TalleId)
    Ventas/
      Venta.cs              → MODIFICAR (Observaciones → Anotaciones)
  Enums/
    TipoTalle.cs            → NUEVO
```

---

### 3.2 Application (`ShowroomGriffin.Application`)

#### Interfaces NUEVAS

```
Application/Interfaces/
  IMarcaService.cs          → NUEVO (renombrado de ISubgrupoService o nuevo paralelo)
  IModeloService.cs         → NUEVO
```

`ISubgrupoService` **se depreca** y es reemplazado por `IMarcaService`.  
El contrato de `IMarcaService` extiende el de `ISubgrupoService` con el método adicional `ObtenerPorCategoriaAsync`.

#### Interfaces MODIFICADAS

| Interface | Cambio |
|---|---|
| `IVarianteService` | Agregar: `ObtenerColoresPorModeloAsync(int modeloId)`, `ObtenerTallesPorModeloColorAsync(int modeloId, string? color)`, `ResolverVarianteAsync(VarianteSelectorRequest)` |
| `IClienteService` | Agregar: `CrearRapidoAsync(ClienteRapidoViewModel vm)` |
| `IDevolucionService` | Agregar: `BuscarVentasParaDevolucionAsync(BuscarVentaRequest req)` |
| `IStockService` | Modificar `ListarAsync` para aceptar filtros opcionales: `MarcaId`, `ModeloId` en `DataTableRequest` (vía `Filters` o parámetros adicionales) |

#### ViewModels NUEVOS (en `Application/DTOs/`)
```
DTOs/
  Maestros/
    MarcaViewModel.cs       → NUEVO (igual estructura que SubgrupoViewModel + CantidadModelos)
    ModeloViewModel.cs      → NUEVO
  Productos/
    TalleConfigViewModel.cs → NUEVO
    VarianteSelectorRequest.cs   → NUEVO
    VarianteSelectorResponse.cs  → NUEVO
  Maestros/
    ClienteRapidoViewModel.cs    → NUEVO
  Devoluciones/
    BuscarVentaRequest.cs        → NUEVO
```

#### ViewModels MODIFICADOS
| ViewModel | Cambio |
|---|---|
| `SubgrupoViewModel` | → Renombrar a `MarcaViewModel`; agregar `CantidadModelos` |
| `ProductoViewModel` | `SubgrupoId` → `MarcaId`; `SubgrupoNombre` → `MarcaNombre`; agregar `ModeloId`, `ModeloNombre` |
| `VarianteViewModel` | Quitar `Marca`, `Modelo`; `Talle`/`Numero` → `TalleId` (int?); agregar `EsAccesorio` |
| `VentaCreateViewModel` | `Observaciones` → `Anotaciones` |
| `VentaDetalleViewModel` | `Observaciones` → `Anotaciones` |

#### Convenciones (sin cambios)
- Todos los métodos retornan `ServiceResult` / `ServiceResult<T>`.
- Sin referencias a Infrastructure ni Web.
- Parámetro `bool incluirCostos` se mantiene donde aplica.

---

### 3.3 Infrastructure (`ShowroomGriffin.Infrastructure`)

#### Configuraciones EF — NUEVAS
```
Data/Configurations/Maestros/
  MarcaConfiguration.cs         → NUEVO (renombra SubgrupoConfiguration + ToTable("Marcas") + Modelos)
  ModeloConfiguration.cs        → NUEVO
  TalleConfigConfiguration.cs   → NUEVO
```

#### Configuraciones EF — MODIFICADAS
| Archivo | Cambio |
|---|---|
| `SubgrupoConfiguration.cs` | Renombrar clase a `MarcaConfiguration`; cambiar `ToTable("Marcas")`; agregar relación HasMany Modelos |
| `ProductoConfiguration.cs` | Cambiar FK `SubgrupoId` → `MarcaId`; agregar FK `ModeloId`; cambiar relación de navegación |
| `VarianteProductoConfiguration.cs` | Quitar `.Property(Marca)`, `.Property(Modelo)`, `.Property(Talle)`, `.Property(Numero)`; agregar FK `TalleId` con `IsRequired(false)` → `TalleConfig`; `OnDelete(SetNull)` |
| `VentaConfiguration.cs` | Renombrar columna: `.Property(e => e.Anotaciones).HasMaxLength(1000)` (era `Observaciones`) |

#### `AppDbContext` — MODIFICADO
```csharp
// Agregar DbSets nuevos
public DbSet<Marca> Marcas { get; set; }       // renombrado de Subgrupos (o coexistente en transición)
public DbSet<Modelo> Modelos { get; set; }
public DbSet<TalleConfig> TallesConfig { get; set; }
```
> `DbSet<Subgrupo> Subgrupos` se elimina o se reemplaza atómicamente junto con la migración.

#### `DependencyInjection.cs` — MODIFICADO
```csharp
// Quitar:
services.AddScoped<ISubgrupoService, SubgrupoService>();

// Agregar:
services.AddScoped<IMarcaService, MarcaService>();
services.AddScoped<IModeloService, ModeloService>();
```
Los demás registros existentes (`IProductoService`, `IVarianteService`, etc.) no cambian de nombre.

#### Services — NUEVOS
```
Services/
  MarcaService.cs           → NUEVO (port de SubgrupoService + ObtenerPorCategoriaAsync)
  ModeloService.cs          → NUEVO
```

#### Services — MODIFICADOS
| Service | Cambio |
|---|---|
| `VarianteService.cs` | Implementar 3 métodos nuevos de AJAX; adaptar queries para usar `Producto.MarcaId`/`ModeloId` en lugar de `VarianteProducto.Marca`/`Modelo` |
| `ClienteService.cs` | Implementar `CrearRapidoAsync` |
| `DevolucionService.cs` | Implementar `BuscarVentasParaDevolucionAsync` con filtro multi-criterio |
| `StockService.cs` | Aplicar filtros opcionales `MarcaId`/`ModeloId` en `ListarAsync` |
| `ProductoService.cs` | Adaptar queries para usar `MarcaId`/`ModeloId` |
| `SubgrupoService.cs` | → Se elimina o queda como stub deprecado |

#### `SeedData.cs` — MODIFICADO
```csharp
// Agregar:
public const string RolEmpleado = "Empleado";

// En InitializeAsync: crear rol Empleado + seed categorías + seed TalleConfig
string[] roles = [RolSuperUsuario, RolAdministrador, RolVendedor, RolEmpleado];

// Seed TalleConfig (solo si la tabla está vacía):
// ZapatillaAdulto: 34,35,...,46
// ZapatillaNino:   22,23,...,33
// Indumentaria:    XS,S,M,L,XL,XXL

// Seed Categorías (solo si la tabla está vacía):
// Indumentaria, Zapatillas, Accesorios
```

---

### 3.4 Web (`ShowroomGriffin.Web`)

#### Controllers — NUEVOS
| Controller | Política | Descripción |
|---|---|---|
| `MarcasController` | `RequireAdministrador` | Reemplaza `SubgruposController`; agrega endpoint AJAX `ObtenerPorCategoria` con `RequireEmpleado` |
| `ModelosController` | `RequireAdministrador` | ABM de modelos; endpoint AJAX `ObtenerPorMarca` con `RequireEmpleado` |

#### Controllers — MODIFICADOS
| Controller | Cambio |
|---|---|
| `SubgruposController` | Reemplazado por `MarcasController`. Agregar redirect `/Subgrupos` → `/Marcas` para compatibilidad. |
| `VariantesController` | Agregar 3 endpoints AJAX: `GET ObtenerColores(modeloId)`, `GET ObtenerTalles(modeloId, color)`, `GET ResolverVariante(...)` — todos con `RequireEmpleado` |
| `ProductosController` | Vista Crear/Editar usa cascada Categoría→Marca→Modelo; adaptar a nuevos ViewModels |
| `VentasController` | Agregar `POST CrearRapidoCliente` (AJAX, `RequireEmpleado`); adaptar vista a nuevos combos; renombrar campo Observaciones→Anotaciones |
| `ComprasController` | Adaptar vista Crear/Editar a nuevos combos anidados |
| `DevolucionesController` | Agregar `POST BuscarVentas` (AJAX, multi-criterio); adaptar paso-0 del wizard |
| `StockController` | Cambiar política de clase a `RequireEmpleado`; mantener `RequireAdministrador` en Ajuste/CargaInicial |
| `ClientesController` | Agregar `POST CrearRapido` (AJAX, `RequireEmpleado`) |

#### `Program.cs` — MODIFICADO
```csharp
// Agregar policy RequireEmpleado:
options.AddPolicy("RequireEmpleado",
    policy => policy.RequireRole(
        SeedData.RolSuperUsuario,
        SeedData.RolAdministrador,
        SeedData.RolVendedor,
        SeedData.RolEmpleado));
```

#### Vistas — NUEVAS (4)
```
Views/
  Marcas/
    Index.cshtml
    Crear.cshtml (= Editar.cshtml)
  Modelos/
    Index.cshtml
    Crear.cshtml (= Editar.cshtml)
```

#### Vistas — MODIFICADAS (6)
| Vista | Cambio |
|---|---|
| `Ventas/Crear.cshtml` | 5 combos anidados; campo Anotaciones; modal "Nuevo Cliente"; autofill importe pago |
| `Ventas/Detalle.cshtml` | Mostrar Anotaciones; botón "Iniciar Cambio/Devolución" si estado Confirmada o Entregada |
| `Compras/Crear.cshtml` | 5 combos anidados (reutiliza JS de ventas) |
| `Compras/Editar.cshtml` | Idem Crear |
| `Devoluciones/Crear.cshtml` | Paso-0 de búsqueda multi-criterio antes del wizard |
| `Stock/Index.cshtml` | Filtros por Marca/Modelo; indicadores visuales 🟢🟡🔴⚫ |

#### Partial y JS — NUEVOS / MODIFICADOS
| Artefacto | Tipo | Descripción |
|---|---|---|
| `_VarianteSelector.cshtml` (partial) | NUEVO | Componente de 5 combos reutilizable (Ventas + Compras + modal Cambio) |
| `variante-selector.js` | NUEVO | Lógica de cascada, reset, resolución de variante y precarga de precio |
| `venta-crear.js` | MODIFICAR | Integrar `variante-selector.js`; autofill importe pago; recálculo precios |
| `compra-crear.js` | MODIFICAR | Integrar `variante-selector.js` |
| `devolucion-crear.js` | MODIFICAR | Paso-0 búsqueda + integrar `variante-selector.js` en modal cambio |
| `stock-index.js` | MODIFICAR | Filtros dinámicos por Marca/Modelo vía AJAX |

#### Policies por controller (tabla actualizada completa v2)

| Controller | Policy clase | Excepciones por acción |
|---|---|---|
| `CategoriasController` | `RequireAdministrador` | — |
| `MarcasController` | `RequireAdministrador` | `ObtenerPorCategoria` (AJAX): `RequireEmpleado` |
| `ModelosController` | `RequireAdministrador` | `ObtenerPorMarca` (AJAX): `RequireEmpleado` |
| `ClientesController` | `RequireVendedor` | `CrearRapido` (AJAX): `RequireEmpleado`; CUD completo: `RequireAdministrador` |
| `ProveedoresController` | `RequireAdministrador` | — |
| `TiposPrecioController` | `RequireAdministrador` | — |
| `ProductosController` | `RequireVendedor` | CUD: `RequireAdministrador` |
| `VariantesController` | `RequireVendedor` | CUD: `RequireAdministrador`; AJAX combos: `RequireEmpleado` |
| `StockController` | `RequireEmpleado` | `CargaInicial`, `Ajuste`: `RequireAdministrador` |
| `ComprasController` | `RequireAdministrador` | — |
| `VentasController` | `RequireEmpleado` | — |
| `DevolucionesController` | `RequireEmpleado` | — |
| `ResumenSemanalController` | `RequireAdministrador` | — |
| `AumentoMasivoController` | `RequireAdministrador` | — |

> **Nota:** `VentasController` y `StockController` cambian de `RequireVendedor` a `RequireEmpleado` (más inclusivo). Esto no rompe acceso a Vendedor ni Admin porque `RequireEmpleado` los incluye.

---

## 4. Modelo de permisos — delta v2

### 4.1 Rol nuevo

| Rol | Constante | Descripción |
|---|---|---|
| `Empleado` | `SeedData.RolEmpleado = "Empleado"` | Operativa diaria: ventas, cambios/devoluciones, stock consulta. Sin administración. |

### 4.2 Policy nueva

```csharp
// Program.cs
options.AddPolicy("RequireEmpleado",
    policy => policy.RequireRole(
        SeedData.RolSuperUsuario,
        SeedData.RolAdministrador,
        SeedData.RolVendedor,
        SeedData.RolEmpleado));
```

### 4.3 Jerarquía de policies (de más a menos restrictiva)

```
RequireSuperUsuario  → solo SuperUsuario
RequireAdministrador → SuperUsuario + Administrador
RequireAdministracion→ alias de RequireAdministrador (existente)
RequireVendedor      → SuperUsuario + Administrador + Vendedor
RequireEmpleado      → SuperUsuario + Administrador + Vendedor + Empleado  ← NUEVA
```

### 4.4 Visibilidad de costos — sin cambios
El parámetro `incluirCostos` continúa resuelto en controller.  
Un Empleado **nunca** recibe `UltimoPrecioCompra`, `CostoTotal`, `GananciaTotal`.

---

## 5. Migraciones EF — requeridas

**Sí. 3 migraciones nuevas (MR-1 a MR-3).** Las migraciones M1–M6 de la v1 ya están aplicadas.

### Detalle de migraciones

#### MR-1: `V2_RefactorMarcaModelo`
**Propósito:** Reestructuración central del modelo de productos.

**DDL net:**
- Renombrar tabla `Subgrupos` → `Marcas` (o crear `Marcas` y migrar datos).
- Crear tabla `Modelos` (`Id`, `Nombre`, `MarcaId`, `DeletedAt`...).
- Agregar columnas en `Productos`: `MarcaId INT NULL`, `ModeloId INT NULL`.
- Quitar columnas de `VariantesProducto`: `Marca`, `Modelo`.

**Script de datos (crítico — dentro de la misma migración):**
```sql
-- 1. Poblar Producto.MarcaId desde VarianteProducto.Marca (via SubgrupoId existente)
--    Si Producto.SubgrupoId ya está correctamente cargado, simplemente:
UPDATE Productos p SET p.MarcaId = p.SubgrupoId WHERE p.SubgrupoId IS NOT NULL;

-- 2. Poblar Producto.ModeloId requiere crear registros en Modelos primero
--    Por cada valor distinto de VarianteProducto.Modelo agrupado por Producto:
--    (Script a generar por el implementador según datos reales)

-- 3. Quitar columna SubgrupoId de Productos (reemplazada por MarcaId)
ALTER TABLE Productos DROP FOREIGN KEY FK_Productos_Subgrupos;
ALTER TABLE Productos DROP COLUMN SubgrupoId;
```

**Dependencias:** Ninguna migración previa nueva (opera sobre M1–M2 ya aplicadas).  
**Riesgo:** Alto. Requiere backup antes de aplicar y validación de datos post-migración.  
**Estrategia:** Ejecutar en 2 pasos: primero agregar columnas y migrar datos (sin quitar las viejas), validar, luego quitar columnas viejas en MR-1b si se prefiere.

#### MR-2: `V2_TalleConfig`
**Propósito:** Catálogo de talles predefinidos + FK en VarianteProducto.

**DDL net:**
- Crear tabla `TallesConfig` (`Id`, `Valor`, `Tipo` int, `DeletedAt`...).
- Agregar columna `TalleId INT NULL` en `VariantesProducto` con FK a `TallesConfig`.
- Quitar columnas `Talle` (string) y `Numero` (string) de `VariantesProducto`.

**Seed dentro de la migración:**
```sql
INSERT INTO TallesConfig (Valor, Tipo) VALUES
-- ZapatillaAdulto (Tipo=1)
('34',1),('35',1),('36',1),('37',1),('38',1),('39',1),('40',1),
('41',1),('42',1),('43',1),('44',1),('45',1),('46',1),
-- ZapatillaNino (Tipo=2)
('22',2),('23',2),('24',2),('25',2),('26',2),('27',2),('28',2),
('29',2),('30',2),('31',2),('32',2),('33',2),
-- Indumentaria (Tipo=3)
('XS',3),('S',3),('M',3),('L',3),('XL',3),('XXL',3);
```

**Script de datos:** Mapear valores de texto libre de `Talle`/`Numero` actuales a `TalleId` por valor.  
**Dependencia:** MR-1 aplicada.

#### MR-3: `V2_VentaAnotaciones`
**Propósito:** Renombrar columna `Observaciones` → `Anotaciones` en tabla `Ventas`.

**DDL net:**
```sql
ALTER TABLE Ventas CHANGE COLUMN Observaciones Anotaciones VARCHAR(1000);
```

**Dependencia:** Ninguna (independiente, puede aplicarse en cualquier momento).  
**Riesgo:** Bajo.

### Comandos EF
```bash
dotnet ef migrations add V2_RefactorMarcaModelo -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add V2_TalleConfig         -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add V2_VentaAnotaciones    -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef database update                       -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
```

---

## 6. Soporte arquitectónico de la máquina de estados — delta v2

| Aspecto | Soporte |
|---|---|
| **C07: Devolución desde Confirmada** | `IDevolucionService.CrearAsync` ya valida estado de venta; extender guarda de `Confirmada \| Entregada` (era solo `Entregada` en v1). Cambio de 1 línea en el service. |
| **C02: CrearRapidoCliente** | Transacción simple; no afecta máquina de estados de venta. |
| **C08: Rol Empleado — anular venta** | Empleado **no puede** anular (`RequireAdministrador` o `RequireVendedor` en la acción `Anular`). Se protege con `[Authorize(Policy = "RequireVendedor")]` en la acción específica. |
| **C10: Refactor Marca/Modelo** | No cambia ninguna máquina de estados; es puramente estructural. |
| **C11: TalleConfig** | No cambia máquina de estados; afecta validación en `IVarianteService.CrearAsync` (TalleId debe existir en catálogo). |

---

## 7. Riesgos y supuestos

| # | Tipo | Descripción | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | **Riesgo alto** | MR-1 quita columnas `Marca`/`Modelo`/`SubgrupoId` de tablas. Si hay datos no migrados correctamente, pérdida irrecuperable. | Alto | Ejecutar MR-1 en 2 fases: fase A (agregar columnas nuevas + migrar datos) + fase B (quitar columnas viejas). Backup obligatorio. |
| R2 | Riesgo medio | `SubgrupoService` referenciado en `DependencyInjection` y en controllers AJAX. Requiere renombrado limpio. | Medio | Reemplazar atómicamente: un único commit cambia Service + DI + Controller + todas las referencias. |
| R3 | Riesgo medio | `VarianteProducto.Talle` y `Numero` son texto libre con datos existentes. Mapping a `TalleId` puede fallar si los valores no coinciden exactamente con el catálogo seed. | Medio | Script de migración hace ILIKE case-insensitive; valores no mapeables quedan con `TalleId = NULL` (campo es nullable). |
| R4 | Riesgo bajo | `VentasController` cambia de `RequireVendedor` → `RequireEmpleado`. Debe verificarse que el Empleado no acceda a la acción `Anular`. | Bajo | La acción `Anular` se marca explícitamente con `[Authorize(Policy = "RequireVendedor")]`. |
| R5 | Riesgo bajo | `_VarianteSelector.cshtml` partial debe comportarse igual en Ventas, Compras y modal de Cambio. | Bajo | Parametrizar el partial con un prefijo de campo JS para no colisionar IDs en la misma página. |
| R6 | Riesgo bajo | Color sigue siendo texto libre en VarianteProducto. Si hay variaciones de case ("negro" vs "Negro"), el combo mostrará duplicados. | Bajo | Normalizar a Title Case en service al guardar. |
| S1 | Supuesto | Los datos actuales en DB tienen `SubgrupoId` correctamente asignado en todos los `Productos`. | — | Confirmado por el cliente (P13-A). |
| S2 | Supuesto | Los valores de `VarianteProducto.Talle`/`Numero` son cadenas limpias que coinciden con el catálogo. | — | Validar con query previo a MR-2. |
| S3 | Supuesto | El partial `_VarianteSelector` puede ser compartido entre Ventas y Compras sin ambigüedad de IDs. | — | Implementar con prefijo de namespacing JS. |
| S4 | Supuesto | `RequireEmpleado` como policy inclusiva (Admin+Vendedor+Empleado) no rompe accesos existentes de Vendedor ni Admin. | — | Verificado: política más amplia, no más restrictiva. |

---

## 8. Plan técnico por etapas (alineado a V1-E1..E4 del diseño)

| Etapa | Migraciones EF | Entidades/Configs | Services | Controllers/Vistas |
|---|---|---|---|---|
| **V1-E1** Refactor estructural | MR-1 + MR-2 + MR-3 | Marca, Modelo, TalleConfig + 3 configs nuevas + 4 configs modificadas | MarcaService, ModeloService + VarianteService mod + SeedData | MarcasController, ModelosController, SubgruposController→deprecated, ProductosController mod, VariantesController mod |
| **V1-E2** Combos + Ventas/Compras | — | — | IVarianteService 3 métodos nuevos | VentasController mod (Anotaciones+modal-cliente AJAX), ComprasController mod; JS: variante-selector.js, venta-crear.js mod, compra-crear.js mod |
| **V1-E3** Modal cliente + Dev búsqueda | — | — | ClienteService.CrearRapidoAsync, DevolucionService.BuscarVentasAsync | ClientesController (CrearRapido), DevolucionesController mod; vistas Devoluciones/Crear mod |
| **V1-E4** Rol Empleado + Stock visual | — | — | SeedData (RolEmpleado ya en E1) | Program.cs (policy), StockController mod, sidebar nav update, Stock/Index.cshtml rediseño |

---

## 9. Pruebas técnicas mínimas (gate de calidad v2)

### Migraciones
- [ ] MR-1 aplicada sin errores; todos los `Productos` tienen `MarcaId` poblado.
- [ ] MR-2 aplicada; `TallesConfig` con 31 registros (13+12+6); variantes existentes con `TalleId` mapeado o NULL.
- [ ] MR-3 aplicada; columna `Anotaciones` existe y datos anteriores de `Observaciones` preservados.
- [ ] `dotnet ef migrations script` genera SQL válido para MySQL 8.

### Refactor estructural
- [ ] Crear un producto con cascada Categoría→Marca→Modelo funciona end-to-end.
- [ ] Crear una variante con TalleId desde el catálogo (no texto libre).
- [ ] `SubgrupoService`/`SubgruposController` deprecados no producen errores 500.

### Combos anidados
- [ ] AJAX `ObtenerColores(modeloId)` devuelve solo colores con stock > 0.
- [ ] AJAX `ObtenerTalles(modeloId, color)` devuelve solo talles con stock > 0.
- [ ] `ResolverVariante(...)` devuelve `VarianteId` + precio + stock para combinación válida.
- [ ] Combinación inválida devuelve mensaje claro (no 500).
- [ ] Al cambiar Categoría se resetean Marca, Modelo, Color, Talle.

### Autorización
- [ ] Empleado → 403 en `/Compras`, `/AumentoMasivo`, `/ResumenSemanal`, `/Stock/Ajuste`.
- [ ] Empleado → 200 en `/Ventas`, `/Devoluciones`, `/Stock/Index`.
- [ ] Empleado → puede crear venta end-to-end.
- [ ] Empleado → NO puede anular venta (403).
- [ ] Empleado → NO ve precio de costo en stock ni en venta.
- [ ] Vendedor → acceso idéntico al que tenía antes (no regresión).

### Lógica transaccional
- [ ] `DevolucionService.CrearAsync` acepta ventas en estado `Confirmada` (nueva extensión).
- [ ] `ClienteService.CrearRapidoAsync` retorna el cliente creado con Id para inyectar en Select2.

---

## 10. Checklist de salida — Arquitectura v2

```
ARQUITECTURA v2 — CHECKLIST DE SALIDA
─────────────────────────────────────────────────────────────────────
DOMAIN
[✓] 2 entidades nuevas (Modelo, TalleConfig) — SoftDestroyable
[✓] 1 enum nuevo (TipoTalle)
[✓] Subgrupo renombrado a Marca — cambio confirmado en entidad + config + service
[✓] Producto: SubgrupoId → MarcaId + ModeloId
[✓] VarianteProducto: quitar Marca/Modelo/Talle/Numero; agregar TalleId
[✓] Venta: Observaciones → Anotaciones
[✓] Sin lógica de negocio en entidades

APPLICATION
[✓] IMarcaService + IModeloService nuevos
[✓] ISubgrupoService deprecado
[✓] IVarianteService: 3 métodos AJAX nuevos
[✓] IClienteService: CrearRapidoAsync
[✓] IDevolucionService: BuscarVentasParaDevolucionAsync
[✓] ViewModels nuevos y modificados catalogados

INFRASTRUCTURE
[✓] 3 configs nuevas (Marca, Modelo, TalleConfig)
[✓] 4 configs modificadas (Producto, VarianteProducto, Venta, Subgrupo→Marca)
[✓] 2 services nuevos (MarcaService, ModeloService)
[✓] 4 services modificados (Variante, Cliente, Devolucion, Stock)
[✓] DependencyInjection actualizado (quitar Subgrupo, agregar Marca+Modelo)
[✓] SeedData: RolEmpleado + seed TalleConfig + seed Categorías
[✓] 3 migraciones EF planificadas (MR-1, MR-2, MR-3)
[✓] Script de datos en MR-1 y MR-2 documentado

WEB
[✓] 2 controllers nuevos (Marcas, Modelos)
[✓] 6 controllers modificados (Variantes, Productos, Ventas, Compras, Devoluciones, Stock, Clientes)
[✓] Program.cs: policy RequireEmpleado
[✓] 4 vistas nuevas (Marcas Index/Crear, Modelos Index/Crear)
[✓] 6 vistas modificadas documentadas
[✓] Partial _VarianteSelector.cshtml reutilizable
[✓] JS: variante-selector.js nuevo; 3 JS modificados

PERMISOS
[✓] Rol Empleado + policy RequireEmpleado definidos
[✓] Jerarquía de 5 policies documentada
[✓] Tabla completa de policies por controller/acción actualizada
[✓] Visibilidad de costos sin cambios

RIESGOS
[✓] R1–R6 + S1–S4 documentados y mitigados

PRUEBAS
[✓] Plan de pruebas técnico mínimo v2 definido
─────────────────────────────────────────────────────────────────────
```

---

## 11. Gate de aprobación para pasar a implementación

| Criterio | Estado |
|---|---|
| Análisis funcional v2 aprobado (todas las decisiones P1–P15 + C11a) | ✅ |
| Diseño funcional v2 aprobado | ✅ |
| Impacto por capa cuantificado (Domain/Application/Infrastructure/Web) | ✅ |
| Modelo de permisos definido (5 policies, 4 roles) | ✅ |
| Decisión sobre migraciones EF (3 migraciones MR-1..MR-3) | ✅ |
| Máquina de estados extensión v2 soportable verificada | ✅ |
| Riesgos identificados y mitigados | ✅ |
| Sin bloqueantes técnicos abiertos | ✅ |

**Gate: APROBADO — habilitado handoff a implementación.**

### Insumos para el implementador

**Etapa V1-E1 (crítica — implementar primero):**
- 3 entidades nuevas, 1 enum nuevo, 4 entidades modificadas.
- 3 configs EF nuevas, 4 modificadas.
- 2 services nuevos, 1 deprecado, 4 modificados.
- 3 migraciones con scripts de datos.
- 2 controllers nuevos, 1 deprecado.

**Etapas V1-E2 a V1-E4 (paralelas luego de E1):**
- 3 métodos AJAX nuevos en VarianteService.
- 1 partial reutilizable + 1 JS nuevo + 3 JS modificados.
- 4 vistas nuevas + 6 vistas modificadas.
- 1 policy nueva en Program.cs.
- SeedData con rol + talles + categorías.

**Riesgo principal:** MR-1 con script de datos (R1). Validar con query previo antes de ejecutar.
