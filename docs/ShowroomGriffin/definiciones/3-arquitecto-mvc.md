# Memoria - Arquitecto MVC

## Proyecto: ShowroomGriffin — Sistema de Gestión Comercial
## Ultima actualizacion: 2026-08-16

## Definiciones vigentes

> Nota de consolidación (2026-08-16): este archivo no seguía la plantilla estándar y mezclaba, fuera de orden cronológico, la arquitectura base v2.0 (C01-C12) con 2 arquitecturas de versión posteriores (V10 2026-07-30, V12 2026-08-16) — V10 aparecía primero en el archivo pese a ser posterior a la base v2. Se agregó la estructura estándar y se demovió cada encabezado un nivel para que todo quede bajo un único `## Definiciones vigentes`, **sin reordenar ni tocar el contenido técnico** (reordenar 700+ líneas de contenido interrelacionado tenía más riesgo de introducir un error que dejarlo en su orden original) — el orden cronológico correcto está en `## Historial de ajustes` al final.

### V10 — Arquitectura técnica: Carga masiva de stock por Marca + filtros completos en Consulta de Stock (2026-07-30)

**Input:** `1-analista-funcional.md` sección V10 (aprobado) + `2-disenador-funcional.md` sección V10 (CERRADO Y APROBADO, DD-1 resuelto).

#### 0. Escaneo de reutilización

Escaneado `docs/*/definiciones/{3-arquitecto-mvc,5-implementador}.md`. Coincidencia: **LabIPAC** — `IProduccionMensualService.AgregarLineasAsync(int, IEnumerable<Dto>)`, batch atómico con `AddRangeAsync` + único `SaveChangesAsync` (sin transacción explícita porque no había múltiples operaciones dependientes de servicios externos). Se toma como referencia de forma general, pero **no aplica igual acá**: ShowroomGriffin ya tiene servicios existentes (`AjusteManualAsync`, `CargaInicialAsync` vía `VarianteService.CrearAsync`) que abren **su propia transacción interna** — un caso más complejo que labipac porque implica orquestar servicios ya transaccionales, no solo un `AddRange` plano. Ver riesgo crítico R-V10-1 más abajo.

Dentro del propio ShowroomGriffin, se reutilizan directamente (sin reescribir):
- `IVarianteService.CrearAsync(VarianteViewModel)` — ya crea `VarianteProducto` + `Stock` (init 0) + carga inicial opcional. Es exactamente el mecanismo de alta que necesita cada fila nueva de la grilla masiva.
- `IStockService.AjusteManualAsync(AjusteStockViewModel)` — ya genera `AjusteStock` + `MovimientoStock` por variante. Es el mecanismo que necesita cada fila existente con cantidad modificada.

### 1. Alcance funcional resumido
Sin cambios respecto al Diseño V10 aprobado: pantalla `/Stock/CargaMasiva` (selección por Marca, grilla agrupada por Modelo, alta inline de variantes faltantes, guardado atómico con errores por fila) + filtros Talle/Estado en `/Stock/Index`.

### 2. Impacto técnico por capa

#### Domain
Sin entidades nuevas ni modificadas. Se reutilizan `VarianteProducto`, `Stock`, `AjusteStock`, `MovimientoStock`, `TalleConfig`, `Modelo`, `Producto`.

#### Application
| Elemento | Cambio |
|---|---|
| `IStockService` | + `ObtenerParaCargaMasivaAsync(int marcaId)` → `StockCargaMasivaViewModel` (arma grilla agrupada por Modelo con variantes existentes) |
| `IStockService` | + `GuardarCargaMasivaAsync(StockCargaMasivaViewModel vm, string usuarioId)` → `ServiceResult` (orquesta altas + ajustes en una única transacción, ver R-V10-1) |
| `IStockService.ListarAsync` / `ExportarExcelAsync` | + parámetros `int? talleConfigId`, `EstadoStockFiltro estado` |
| DTOs nuevos | `StockCargaMasivaViewModel`, `StockCargaMasivaModeloViewModel`, `StockCargaMasivaFilaViewModel` (en `Application/DTOs/Stock/StockViewModels.cs`, junto a los existentes) |
| Enum nuevo | `EstadoStockFiltro` (`Application` o `Domain.Enums`, a definir por convención existente — los enums del proyecto viven en `Domain.Enums`, se sigue ese criterio) |

#### Infrastructure
| Elemento | Cambio |
|---|---|
| `StockService` | + `ObtenerParaCargaMasivaAsync`: query de `VarianteProducto` por `Producto.Modelo.MarcaId`, agrupado en memoria por `ModeloId` |
| `StockService` | + `GuardarCargaMasivaAsync`: ver diseño de transacción en R-V10-1 |
| `StockService.ListarAsync` | + `Where(s => s.VarianteProducto.TalleConfigId == talleConfigId)` y mapeo de `estado` a la misma expresión que ya usa `EnAlerta`/`Deficit` |
| `StockService.ExportarExcelAsync` | pasa los 2 parámetros nuevos a `ListarAsync` |

#### Web
| Elemento | Cambio |
|---|---|
| `StockController` | + `CargaMasiva` GET (arma vm vía `ObtenerParaCargaMasivaAsync`) y POST (`[Authorize(Policy = "RequireAdministrador")]`, mismo criterio que `Ajuste`) |
| `StockController.Listar` / `ExportarExcel` | + parámetros `talleConfigId`, `estado` |
| Vista nueva | `Views/Stock/CargaMasiva.cshtml` |
| Vista modificada | `Views/Stock/Index.cshtml` (combo Talle + combo Estado reemplazando botón) |
| JS | endpoint AJAX ya existente `/Variantes/api/Colores`-style reutilizado para poblar Talle por Modelo (o se reutiliza `ObtenerTallesPorModeloColorAsync` ya existente en `IVarianteService`, pasando `color: null`) |

### 3. Modelo de permisos
Sin cambios. `CargaMasiva` usa `RequireAdministrador` (idéntico a `Ajuste`/`CargaInicial` existentes). `/Stock/Index` con filtros nuevos sigue bajo `RequireEmpleado` (policy de clase ya vigente).

### 4. Migraciones EF
**NO.** Todas las entidades y columnas necesarias ya existen. Confirmado en Diseño y re-confirmado acá tras revisar el código real de `VarianteProducto`, `Stock`, `AjusteStock`, `MovimientoStock`.

### 5. Riesgos y supuestos

#### R-V10-1 (CRÍTICO — bloquea implementación tal cual, requiere resolución de diseño técnico)
`AjusteManualAsync` y (indirectamente, vía `CargaInicialAsync`) el alta de variante abren **cada uno su propia transacción** (`await using var tx = await _db.Database.BeginTransactionAsync()`) y hacen `commit`/`rollback` internamente. Si `GuardarCargaMasivaAsync` abre una transacción externa y dentro llama a estos métodos tal cual existen hoy, EF Core lanza `InvalidOperationException` ("ya hay una transacción activa en este contexto") en el segundo `BeginTransactionAsync` anidado sobre el mismo `DbContext`/conexión — la atomicidad total (DD-1) no se puede lograr con una llamada ingenua a los métodos existentes.

**Resolución propuesta (para que el Implementador la aplique, sin duplicar lógica):**
- Extraer la lógica interna de `AjusteManualAsync` (armar `AjusteStock` + actualizar `Stock.StockActual` + `RegistrarMovimientoAsync`) a un método privado `AplicarAjusteInternoAsync(...)` **sin** su propio `BeginTransactionAsync` — asume que ya corre dentro de una transacción externa.
- `AjusteManualAsync` (uso individual, sin cambios de comportamiento externo) pasa a ser: abrir transacción → llamar `AplicarAjusteInternoAsync` → commit/rollback. Mismo resultado que hoy.
- Igual tratamiento para la porción transaccional de `CargaInicialAsync` si se reutiliza dentro del lote (o se llama directo a `VarianteService.CrearAsync`, que hoy NO abre transacción explícita — solo hace 2 `SaveChangesAsync` secuenciales sobre el mismo `DbContext` sin `BeginTransactionAsync`, por lo que SÍ puede llamarse tal cual dentro de la transacción externa de `GuardarCargaMasivaAsync` sin conflicto).
- `GuardarCargaMasivaAsync`: abre 1 sola transacción externa, por cada fila nueva llama a `VarianteService.CrearAsync` (reutilizado sin cambios), por cada fila modificada llama a `AplicarAjusteInternoAsync` (nuevo método interno reutilizando la lógica de `AjusteManualAsync`), y al final hace un único commit (o rollback si cualquier paso falla) — esto cumple DD-1 (todo o nada) sin duplicar reglas de negocio.
- **Nota de preservación de comportamiento legacy:** este refactor no cambia la firma pública ni el comportamiento observable de `AjusteManualAsync`/`CargaInicialAsync` para sus usos actuales (ajuste individual, alta de variante individual) — solo separa "abrir transacción" de "aplicar la regla", cumpliendo la regla de "preservar comportamiento legacy salvo indicación contraria".

#### R-V10-2 (a resolver antes de implementar)
La grilla se agrupa por `Modelo`, pero `VarianteProducto.ProductoId` apunta a `Producto`, y el esquema permite (sin restricción de unicidad verificada en `ProductoService`) que un `Modelo` tenga más de un `Producto` — aunque en la práctica documentada (`Producto.cs`: "Nombre derivado de Modelo.Nombre") el sistema se usa como 1 Producto por Modelo. **Se requiere definición:** si al momento de dar de alta una variante nueva para un Modelo no existe ningún `Producto` asociado, o existe más de uno, ¿qué hace la pantalla? Recomendado: si no existe `Producto`, no ofrecer la fila "+ Agregar variante nueva" para ese Modelo y mostrar mensaje "Este modelo no tiene un Producto asociado — crear uno primero desde Productos"; si existe más de uno (caso no contemplado en el uso real actual), tomar el primero y loguear advertencia (caso borde, no bloquea).

#### R-V10-3 (heredado del Diseño)
Concurrencia por fila: cada `VarianteProducto.RowVersion` debe seguir chequeándose individualmente dentro del lote (EF Core lo hace automáticamente vía `ConcurrencyCheck` en cada `SaveChangesAsync`); si una fila del lote tiene conflicto de concurrencia, la transacción completa hace rollback (consistente con DD-1) y el mensaje de error debe indicar qué variante cambió entretanto.

#### R-V10-4
`ExportarExcelAsync` y `ListarAsync` deben recibir los mismos 2 parámetros nuevos — cambio de firma que impacta `StockController` (ya identificado en Diseño y confirmado acá).

### 6. Gate de aprobación para pasar a Presupuesto

Arquitectura V10 lista para aprobación. Antes de presupuestar, requiere que el cliente (o el propio flujo, si se resuelve por criterio técnico estándar) confirme R-V10-2 (comportamiento si falta el Producto del Modelo) — R-V10-1 es una decisión técnica interna (no requiere validación de negocio, solo ejecución correcta) y ya tiene resolución propuesta.

**R-V10-2 — Resuelto por el cliente (2026-07-30):** se bloquea la fila "+ Agregar variante nueva" para un Modelo sin `Producto` asociado, mostrando el mensaje "Este modelo no tiene un Producto asociado — crear uno primero desde Productos". El resto del lote (otros Modelos con Producto existente) sigue operando normalmente — no bloquea el submit completo, solo deshabilita esa opción puntual para ese Modelo.

#### Estado
ARQUITECTURA V10 CERRADA Y APROBADA. R-V10-1 con resolución técnica aplicable directamente por el Implementador (sin validación de negocio pendiente). R-V10-2 resuelto por el cliente. Lista para Presupuesto.

---

# 3 — Arquitectura MVC v2
### Sistema de Gestión Comercial — ShowroomGriffin
**Versión:** 2.0  
**Estado:** En definición  
**Base:** `1-analista-funcional.md` v2 + `2-disenador-funcional.md` v2 (ambos aprobados)  
**Predecesor:** v1.0 (arquitectura base F0–F8 implementada y operativa)

> Este documento cubre exclusivamente el impacto arquitectónico de los 12 cambios v2 (C01–C12).  
> La arquitectura base (v1) permanece vigente y no se repite aquí.

---

### 1. Alcance funcional resumido

4 etapas de implementación (V1-E1 a V1-E4) sobre la base existente:

- **V1-E1 — Refactor estructural:** nueva jerarquía Categoría→Marca→Modelo + TalleConfig. Bloquea todo lo demás.
- **V1-E2 — Combos anidados en Ventas/Compras:** 5 combos AJAX + campo Anotaciones + autofill pago + precios editables.
- **V1-E3 — Modal cliente + Búsqueda rápida devoluciones:** CrearRapido cliente, búsqueda multi-criterio en Dev/Cambios.
- **V1-E4 — Rol Empleado + mejora visual Stock:** nueva policy + menú dinámico + indicadores visuales.

---

### 2. Stack y reutilización (delta v2)

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

### 3. Impacto técnico por capa

#### 3.1 Domain (`ShowroomGriffin.Domain`)

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

#### 3.2 Application (`ShowroomGriffin.Application`)

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

#### 3.3 Infrastructure (`ShowroomGriffin.Infrastructure`)

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

#### 3.4 Web (`ShowroomGriffin.Web`)

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

### 4. Modelo de permisos — delta v2

#### 4.1 Rol nuevo

| Rol | Constante | Descripción |
|---|---|---|
| `Empleado` | `SeedData.RolEmpleado = "Empleado"` | Operativa diaria: ventas, cambios/devoluciones, stock consulta. Sin administración. |

#### 4.2 Policy nueva

```csharp
// Program.cs
options.AddPolicy("RequireEmpleado",
    policy => policy.RequireRole(
        SeedData.RolSuperUsuario,
        SeedData.RolAdministrador,
        SeedData.RolVendedor,
        SeedData.RolEmpleado));
```

#### 4.3 Jerarquía de policies (de más a menos restrictiva)

```
RequireSuperUsuario  → solo SuperUsuario
RequireAdministrador → SuperUsuario + Administrador
RequireAdministracion→ alias de RequireAdministrador (existente)
RequireVendedor      → SuperUsuario + Administrador + Vendedor
RequireEmpleado      → SuperUsuario + Administrador + Vendedor + Empleado  ← NUEVA
```

#### 4.4 Visibilidad de costos — sin cambios
El parámetro `incluirCostos` continúa resuelto en controller.  
Un Empleado **nunca** recibe `UltimoPrecioCompra`, `CostoTotal`, `GananciaTotal`.

---

### 5. Migraciones EF — requeridas

**Sí. 3 migraciones nuevas (MR-1 a MR-3).** Las migraciones M1–M6 de la v1 ya están aplicadas.

#### Detalle de migraciones

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

#### Comandos EF
```bash
dotnet ef migrations add V2_RefactorMarcaModelo -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add V2_TalleConfig         -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add V2_VentaAnotaciones    -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef database update                       -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
```

---

### 6. Soporte arquitectónico de la máquina de estados — delta v2

| Aspecto | Soporte |
|---|---|
| **C07: Devolución desde Confirmada** | `IDevolucionService.CrearAsync` ya valida estado de venta; extender guarda de `Confirmada \| Entregada` (era solo `Entregada` en v1). Cambio de 1 línea en el service. |
| **C02: CrearRapidoCliente** | Transacción simple; no afecta máquina de estados de venta. |
| **C08: Rol Empleado — anular venta** | Empleado **no puede** anular (`RequireAdministrador` o `RequireVendedor` en la acción `Anular`). Se protege con `[Authorize(Policy = "RequireVendedor")]` en la acción específica. |
| **C10: Refactor Marca/Modelo** | No cambia ninguna máquina de estados; es puramente estructural. |
| **C11: TalleConfig** | No cambia máquina de estados; afecta validación en `IVarianteService.CrearAsync` (TalleId debe existir en catálogo). |

---

### 7. Riesgos y supuestos

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

### 8. Plan técnico por etapas (alineado a V1-E1..E4 del diseño)

| Etapa | Migraciones EF | Entidades/Configs | Services | Controllers/Vistas |
|---|---|---|---|---|
| **V1-E1** Refactor estructural | MR-1 + MR-2 + MR-3 | Marca, Modelo, TalleConfig + 3 configs nuevas + 4 configs modificadas | MarcaService, ModeloService + VarianteService mod + SeedData | MarcasController, ModelosController, SubgruposController→deprecated, ProductosController mod, VariantesController mod |
| **V1-E2** Combos + Ventas/Compras | — | — | IVarianteService 3 métodos nuevos | VentasController mod (Anotaciones+modal-cliente AJAX), ComprasController mod; JS: variante-selector.js, venta-crear.js mod, compra-crear.js mod |
| **V1-E3** Modal cliente + Dev búsqueda | — | — | ClienteService.CrearRapidoAsync, DevolucionService.BuscarVentasAsync | ClientesController (CrearRapido), DevolucionesController mod; vistas Devoluciones/Crear mod |
| **V1-E4** Rol Empleado + Stock visual | — | — | SeedData (RolEmpleado ya en E1) | Program.cs (policy), StockController mod, sidebar nav update, Stock/Index.cshtml rediseño |

---

### 9. Pruebas técnicas mínimas (gate de calidad v2)

#### Migraciones
- [ ] MR-1 aplicada sin errores; todos los `Productos` tienen `MarcaId` poblado.
- [ ] MR-2 aplicada; `TallesConfig` con 31 registros (13+12+6); variantes existentes con `TalleId` mapeado o NULL.
- [ ] MR-3 aplicada; columna `Anotaciones` existe y datos anteriores de `Observaciones` preservados.
- [ ] `dotnet ef migrations script` genera SQL válido para MySQL 8.

#### Refactor estructural
- [ ] Crear un producto con cascada Categoría→Marca→Modelo funciona end-to-end.
- [ ] Crear una variante con TalleId desde el catálogo (no texto libre).
- [ ] `SubgrupoService`/`SubgruposController` deprecados no producen errores 500.

#### Combos anidados
- [ ] AJAX `ObtenerColores(modeloId)` devuelve solo colores con stock > 0.
- [ ] AJAX `ObtenerTalles(modeloId, color)` devuelve solo talles con stock > 0.
- [ ] `ResolverVariante(...)` devuelve `VarianteId` + precio + stock para combinación válida.
- [ ] Combinación inválida devuelve mensaje claro (no 500).
- [ ] Al cambiar Categoría se resetean Marca, Modelo, Color, Talle.

#### Autorización
- [ ] Empleado → 403 en `/Compras`, `/AumentoMasivo`, `/ResumenSemanal`, `/Stock/Ajuste`.
- [ ] Empleado → 200 en `/Ventas`, `/Devoluciones`, `/Stock/Index`.
- [ ] Empleado → puede crear venta end-to-end.
- [ ] Empleado → NO puede anular venta (403).
- [ ] Empleado → NO ve precio de costo en stock ni en venta.
- [ ] Vendedor → acceso idéntico al que tenía antes (no regresión).

#### Lógica transaccional
- [ ] `DevolucionService.CrearAsync` acepta ventas en estado `Confirmada` (nueva extensión).
- [ ] `ClienteService.CrearRapidoAsync` retorna el cliente creado con Id para inyectar en Select2.

---

### 10. Checklist de salida — Arquitectura v2

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

### 11. Gate de aprobación para pasar a implementación

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

#### Insumos para el implementador

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

---

### V9 — Redirect post-ajuste de stock (2026-07-02) — Fast-path

**Capa afectada:** Web (Controllers) únicamente.

**Cambio:** `StockController.Ajuste(AjusteStockViewModel vm)` [POST] — línea `return RedirectToAction(nameof(Index));` pasa a `return RedirectToAction(nameof(Ajuste));`. El `TempData["Success"]` ya existente se preserva y se muestra en la vista `Ajuste.cshtml` tras el redirect.

**Sin impacto en:** Domain, Application, Infrastructure, migraciones EF, permisos (`RequireAdministrador` se mantiene), ni en el GET `Ajuste(int? varianteId)` que ya soporta pre-cargar variante.

**Riesgo:** bajo — cambio de una línea, sin efectos secundarios en otras pantallas (Index sigue accesible por su propio link de navegación).

**Gate: APROBADO (fast-path) — habilitado handoff directo a implementación.**

---

### V12 — Arquitectura: extensión de Matriz (accesorios + alta de Color nuevo) y retiro de Carga Masiva/Ajuste (2026-08-16)

**Input:** `2-disenador-funcional.md` sección "V12", cerrado y aprobado (D1–D4 confirmados).

#### 0. Escaneo de reutilización

Sin match cross-proyecto (confirmado ya en Diseño). Reutilización dentro del proyecto: se extienden los componentes de la Etapa 3.1 (`StockMatrizAltaGuardarViewModel`, `StockService.GuardarMatrizAsync`, `IVarianteService.CrearAsync`) — no se crean componentes nuevos de negocio, solo se amplía el alcance de los existentes.

#### 1. Mapa de componentes

| Componente | Tipo | Cambio |
|---|---|---|
| `StockMatrizAltaGuardarViewModel` | DTO (Application) | `TalleConfigId`: `int` `[Required]` → `int?` sin `[Required]` |
| `StockService.ObtenerMatrizAsync` | Service (Infrastructure) | Ya no descarta `grupoSeccion.Key == null` — arma sección con `Talles = []` para Modelos sin `TipoTalle` |
| `StockService.GuardarMatrizAsync` | Service (Infrastructure) | Loop de `Altas` incorpora validación condicional de Talle obligatorio según `TipoTalle` del Modelo del `ProductoId` de cada alta |
| `Matriz.cshtml` / `MatrizEditar.cshtml` | Vista (Web) | Layout de accesorios (Color+Cantidad) + fila "+ Nuevo color" por sección |
| `Stock/Index.cshtml` | Vista (Web) | Quita botones "Ajuste manual" y "Carga masiva" |
| `StockController` | Controller (Web) | Sin acciones nuevas — reutiliza `Matriz`/`MatrizEditar` |

#### 2. Desglose por capa

**Application:**
- Único cambio de contrato: `StockMatrizAltaGuardarViewModel.TalleConfigId` nullable. No rompe compatibilidad — el binding actual ya tolera el campo vacío (mismo mecanismo que ya corrige `CantidadNueva`/`PrecioVenta`/`StockMinimo` desde el hotfix SG-001 del mismo día).
- `IStockService`/`IVarianteService`: sin cambios de firma.

**Infrastructure:**
- `ObtenerMatrizAsync`: el filtro `if (grupoSeccion.Key == null) continue;` se reemplaza por la construcción de una `StockMatrizSeccionViewModel` con `EtiquetaSistemaTalle = null` y `Talles = []`. Sin cambio de query (los accesorios ya se traían del `_db.Stocks` original — el `Include(v => v.TalleConfig)` simplemente resuelve `null`, que ya soporta hoy).
- `GuardarMatrizAsync`, loop de `Altas`: **requiere una consulta adicional** para resolver `TipoTalle` por `ProductoId` (los `Altas` llegan en lista plana sin ese dato, a diferencia de `GuardarCargaMasivaAsync` que lo recibe agrupado por Modelo desde el origen). Diseño técnico: `var tipoTallePorProducto = await _db.Productos.Where(p => productoIds.Contains(p.Id)).Select(p => new { p.Id, p.Modelo.TipoTalle }).ToDictionaryAsync(...)`, resuelto una sola vez antes del loop (no por fila), mismo patrón ya usado para `combinacionesExistentes`.
- Sin migración EF. `VarianteProducto.TalleConfigId` ya es `int?` en el modelo de datos desde su diseño original — no requiere ningún cambio de esquema para soportar la alta de accesorios.

**Web:**
- La fila "+ Nuevo color" (con Talle) necesita, por cada columna de Talle de la sección, un input de cantidad **cuyo `name` indexe una entrada distinta de `Altas[]`** (una por Talle con cantidad cargada), todas comprimidas en una sola fila visual. El JS debe: (a) generar los índices de `Altas[]` en el momento del submit (no en el render, porque no se sabe de antemano cuántas de las N columnas de Talle el usuario va a completar) — mismo mecanismo de "renumerado antes de submit" que ya usa `CargaMasiva.cshtml` para sus filas dinámicas (`renumerarFilasNuevas`, referenciado en `6-qa.md` como el punto más fragil de esa vista); (b) propagar el Color tipeado a cada una de esas entradas; (c) aplicar el mismo criterio SG-001 de hoy: ningún input queda con tipo de valor no-nullable en el lado del ViewModel, y todo decimal se formatea con `CultureInfo.InvariantCulture`.
- La fila de accesorio (sin Talle) es más simple: un solo `Altas[i]` por fila, sin el paso de renumerado dinámico por columnas.

**Datos:** sin cambios.

#### 3. Cambios de datos y migraciones

Ninguno. Confirmado: `VarianteProducto.TalleConfigId` ya es nullable desde el diseño original (V4, `TalleConfigId` FK opcional). El índice único `(ProductoId, Color, TalleConfigId)` agregado el 2026-08-16 (OBS-V10-02) ya soporta `TalleConfigId IS NULL` como parte de la clave (la columna generada usa `COALESCE(TalleConfigId, -1)`, así que dos accesorios del mismo Producto con el mismo Color sin Talle también quedan bloqueados por duplicado — comportamiento correcto y ya cubierto sin cambios).

#### 4. Riesgos técnicos

- **Riesgo alto histórico, ya materializado hoy (D-01/D-02, SG-001):** la fila "+ Nuevo color" con Talle es, en términos de superficie de binding, más compleja que la celda "—" que ya causó el rechazo de QA (un input dinámico por Color existente vs. potencialmente N inputs por fila nueva). **Mitigación obligatoria:** el Implementador debe verificar explícitamente, antes de cerrar la etapa, la checklist: (a) todo campo de `Altas` sigue siendo nullable en el ViewModel, (b) todo `value` de tipo `number` con decimales usa `CultureInfo.InvariantCulture`, (c) build + `dotnet publish` + revisión manual del submit con la fila vacía (caso más común) y con la fila parcialmente completada.
- **Riesgo medio:** el renumerado dinámico de índices de `Altas[]` en JS para la fila con Talle es la pieza más frágil de esta entrega — si falla silenciosamente, el model binder de ASP.NET Core deja de bindear esa fila sin lanzar error visible (mismo patrón de riesgo ya señalado por QA para `CargaMasiva.cshtml`). Mitigación: smoke test manual explícito de este caso puntual antes de dar la etapa por cerrada, no solo revisión de código.
- **Riesgo bajo:** ocultar botones sin eliminar rutas (D3) dejó explícitamente vivas `/Stock/CargaMasiva` y `/Stock/Ajuste` — verificar que no haya otros puntos de entrada (Dashboard, breadcrumbs, favoritos guardados por el cliente) que las referencien fuera de los dos botones ya identificados en `Stock/Index.cshtml`.

#### 5. Estrategia de pruebas funcionales

- Reutiliza el catálogo de pruebas mínimas ya dejado por Carga Masiva/Matriz Etapa 3 (guardado parcial, duplicados, permisos) — sin duplicar aquí, referenciar `5-implementador.md`/`6-qa.md` de las etapas anteriores como base.
- Casos nuevos específicos de V12: (1) alta de Color nuevo en Modelo con Talle, con cantidad en 2+ columnas a la vez; (2) alta de Color nuevo en Modelo con Talle, dejando la fila vacía (no debe generar ningún alta ni error); (3) alta de Color nuevo de un accesorio; (4) edición de Cantidad de un accesorio existente; (5) confirmar que `/Stock/CargaMasiva` y `/Stock/Ajuste` siguen respondiendo por URL directa aunque no tengan botón de acceso.
- **Regla de proceso agregada tras el rechazo de QA del mismo día:** esta etapa NO se cierra como fast-path. El QA de V12 debe incluir, explícitamente, verificación por navegador de la fila "+ Nuevo color" (no solo inspección de código) antes de emitir veredicto — dado que el defecto D-01/D-02 de hoy fue indetectable por build + lectura de diff aislado.

#### Gate de aprobación para pasar a Presupuesto

Arquitectura V12 lista para Presupuesto (agente 4). Sin puntos abiertos — D1–D4 ya resueltos en Análisis, sin decisiones técnicas adicionales pendientes del cliente.

## Historial de ajustes
- v2.0 (base, predecesora de V9/V10/V12): Arquitectura de los 12 cambios (C01-C12) sobre la base v1 (F0-F8) ya implementada y operativa — impacto por capa, modelo de permisos, migraciones EF, riesgos, plan técnico por etapas, pruebas técnicas mínimas.
- 2026-07-02: V9 — Arquitectura del redirect post-ajuste de stock (fast-path).
- 2026-07-30: V10 — Arquitectura de carga masiva de stock por Marca + filtros completos en Consulta de Stock. Riesgo crítico R-V10-1 (transacciones anidadas de EF Core al reutilizar `AjusteManualAsync`/`CargaInicialAsync` dentro de una transacción externa) resuelto con extracción de lógica interna sin transacción propia.
- 2026-08-16: V12 — Arquitectura de extensión de Matriz (accesorios + alta de Color nuevo) y retiro (oculto) de Carga Masiva/Ajuste.
- 2026-08-16: Reestructuración documental — se agregó el encabezado estándar `## Proyecto:`/`## Ultima actualizacion:`/`## Definiciones vigentes` y este historial. El contenido técnico y su orden original (V10 antes que la base v2.0 en el archivo, pese a ser posterior cronológicamente) se preservaron sin cambios — ver nota al inicio de `## Definiciones vigentes`.
