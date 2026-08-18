# Memoria - Disenador funcional

## Proyecto: ShowroomGriffin — Sistema de Gestión Comercial
## Ultima actualizacion: 2026-08-16

## Definiciones vigentes

> Nota de consolidación (2026-08-16): este archivo no seguía la plantilla estándar del estudio. Diseñaba los 12 cambios (C01-C12) sobre la base v1 ya implementada, y tenía 2 secciones de nivel 2 apiladas después (V10, V12). Se agregó la estructura estándar sin resumir ni tocar el contenido técnico; ver `## Historial de ajustes` al final. El diseño v1 original (`diseño-funcional.md`, archivo legacy fuera de este barrido) sigue siendo la referencia de los módulos base F0-F8.
>
> **Versión:** 2.0 — **Base:** `1-analista-funcional.md` v2 aprobado (decisiones P1–P15 + C11a cerradas) — **Predecesor:** v1.0 (F0–F8 implementados, base del sistema operativa). Este documento diseña exclusivamente los **12 cambios nuevos (C01–C12)** sobre la base ya implementada.

### 1. Alcance funcional resumido

#### Cambios agrupados por área de impacto

| Grupo | Cambios | Descripción |
|---|---|---|
| **G1 — Refactor estructural** | C10, C11, C12 | Nueva jerarquía Categoría→Marca→Modelo→Producto→Variante + TalleConfig |
| **G2 — Flujo de Venta** | C01, C02, C03, C04, C09 | Anotaciones, modal cliente, combos anidados, autofill pago, precios editables |
| **G3 — Flujo de Compra** | C05 | Combos anidados (reutiliza G2) |
| **G4 — Postventa** | C07 | Búsqueda rápida en Cambios/Devoluciones |
| **G5 — Roles y Stock** | C06, C08 | Rol Empleado + mejora visual de Stock |

#### Nuevo modelo conceptual (post-refactor)
```
Categoría  ──(1:N)──►  Marca  ──(1:N)──►  Modelo
                                              │
                                           (1:N)
                                              ▼
                                          Producto  ──(1:N)──►  VarianteProducto
                                                                  │
                                                              Color + TalleConfig
```

**Catálogo TalleConfig (seed definitivo):**
| Tipo | Valores |
|---|---|
| ZapatillaAdulto | 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46 |
| ZapatillaNino   | 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33 |
| Indumentaria    | XS, S, M, L, XL, XXL |

---

### 2. Lógica de distribución estándar (design system — herencia v1 + extensiones v2)

La lógica de distribución del sistema base se extiende con los siguientes patrones nuevos:

#### Patrón: Selector de variante anidado (combos cascadeados)
Usado en: Alta Venta, Alta Compra, modal de cambio en Devoluciones.

```
┌─ Selector de Producto ──────────────────────────────────────────────┐
│                                                                      │
│  [Categoría ▼]  →  [Marca ▼]  →  [Modelo ▼]                        │
│                                                                      │
│  [Color ▼]  →  [Talle ▼]                                            │
│                                                                      │
│  Al completar los 5 combos: muestra precio y stock disponible        │
│  [ + Agregar al detalle ]                                            │
└──────────────────────────────────────────────────────────────────────┘
```
- Cada combo se habilita solo cuando el anterior tiene valor seleccionado.
- Al cambiar un combo superior, los inferiores se resetean y deshabilitan.
- Solo se muestran opciones con stock > 0 en Color y Talle.
- Si no existe variante para la combinación → mensaje inline: "No hay stock disponible para esta combinación."
- Combos varían por categoría:
  - **Zapatillas:** Categoría → Marca → Modelo → Número (TalleConfig ZapatillaAdulto | ZapatillaNino)
  - **Indumentaria:** Categoría → Marca → Modelo → Color → Talle (TalleConfig Indumentaria)
  - **Accesorios:** Categoría → Marca → Modelo → Color (sin talle)

#### Patrón: Modal de alta rápida
Usado en: Crear cliente rápido desde Venta.

```
┌─ Modal ── Nuevo Cliente ────────────────────────────────────────────┐
│                                                                      │
│  Nombre *  [_________________________]                               │
│  Teléfono  [_________________________]                               │
│  WhatsApp  [_________________________]                               │
│                                                                      │
│  [ Cancelar ]                          [ Crear y Seleccionar ]       │
└──────────────────────────────────────────────────────────────────────┘
```
- El modal no navega; trabaja sobre la página actual.
- Al crear exitosamente: el nuevo cliente se inyecta en el Select2 de cliente de la venta y queda seleccionado.
- Toast de confirmación: "Cliente creado correctamente."

---

### 3. Flujo de pantallas por módulo (delta v2)

#### 3.1 Módulo Maestros — Marcas y Modelos (nuevo)

#### Pantalla: /Marcas/Index
**Rol:** Administrador  
**Descripción:** Listado ABM de marcas (reemplaza /Subgrupos/Index — misma estructura, nuevo nombre).

```
┌─ Maestros / Marcas ──────────────────────────────────────────────────┐
│  [ + Nueva Marca ]                                                   │
├─ DataTable ──────────────────────────────────────────────────────────┤
│  Nombre │ Categoría │ Cant. Modelos │ Estado │ Acciones              │
│  Nike   │ Zapatillas│      5        │ Activa │ [Editar] [Modelos] [✗]│
└──────────────────────────────────────────────────────────────────────┘
```

**Acciones:**
- **Nueva Marca:** abre formulario (Nombre + Categoría).
- **Modelos:** navega a `/Modelos/Index?marcaId=X` (drill-down).
- **[✗] Eliminar:** soft delete con guarda (sin productos activos asociados).

#### Pantalla: /Marcas/Crear — /Marcas/Editar
```
┌─ Maestros / Marcas / Nueva Marca ───────────────────────────────────┐
│  Nombre *  [_______________________]                                 │
│  Categoría * [Categoría ▼]                                          │
│                                                                      │
│  [ Cancelar ]                    [ Guardar ]                         │
└──────────────────────────────────────────────────────────────────────┘
```

#### Pantalla: /Modelos/Index?marcaId=X
**Rol:** Administrador  
**Descripción:** Listado de modelos de una marca. Breadcrumb: Marcas > Nike > Modelos.

```
┌─ Maestros / Marcas / Nike / Modelos ────────────────────────────────┐
│  [ + Nuevo Modelo ]                                                  │
├─ DataTable ──────────────────────────────────────────────────────────┤
│  Nombre       │ Marca │ Cant. Productos │ Estado │ Acciones          │
│  Air Max 90   │ Nike  │       3         │ Activo │ [Editar] [✗]      │
└──────────────────────────────────────────────────────────────────────┘
```

#### Pantalla: /Modelos/Crear — /Modelos/Editar
```
┌─ Nuevo Modelo ──────────────────────────────────────────────────────┐
│  Nombre *  [_______________________]                                 │
│  Marca *   [Marca ▼]  (filtrada por categoría si viene por URL)     │
│                                                                      │
│  [ Cancelar ]                    [ Guardar ]                         │
└──────────────────────────────────────────────────────────────────────┘
```

---

#### 3.2 Módulo Productos (modificado)

#### Pantalla: /Productos/Crear — /Productos/Editar (delta)
Se agrega la cascada Categoría → Marca → Modelo antes del campo Nombre.

```
┌─ Nuevo Producto ────────────────────────────────────────────────────┐
│  Categoría *  [Categoría ▼]                                         │
│  Marca *      [Marca ▼]        (carga al elegir Categoría, AJAX)    │
│  Modelo *     [Modelo ▼]       (carga al elegir Marca, AJAX)        │
│  Nombre *     [_______________________]                              │
│                                                                      │
│  [ Cancelar ]                    [ Guardar ]                         │
└──────────────────────────────────────────────────────────────────────┘
```

#### Pantalla: /Variantes/Crear — /Variantes/Editar (delta)
Se eliminan los campos Marca y Modelo del formulario.  
Se agrega selector de Talle desde TalleConfig (dropdown en lugar de texto libre).

```
┌─ Nueva Variante ────────────────────────────────────────────────────┐
│  [Producto: Nike Air Max 90 — Categoría: Zapatillas]                │
│                                                                      │
│  == Atributos (dinámicos por categoría) ==                          │
│  [ZAPATILLAS]                                                        │
│  Número *     [Talle ▼]  (ZapatillaAdulto: 34–46 / Niño: 22–33)    │
│  Tipo precio  [TipoPrecioZapatilla ▼]                               │
│                                                                      │
│  [INDUMENTARIA]                                                      │
│  Color        [_______________________]                              │
│  Talle        [XS ▼ S ▼ M ▼ L ▼ XL ▼ XXL ▼]                       │
│  Género       [_______________________]                              │
│  Temporada    [_______________________]                              │
│                                                                      │
│  == Precios y Stock ==                                               │
│  Precio venta *   [__________]                                       │
│  Stock mínimo     [__________]                                       │
│  Cód. Interno     [__________]                                       │
│                                                                      │
│  [ Cancelar ]                    [ Guardar ]                         │
└──────────────────────────────────────────────────────────────────────┘
```

---

#### 3.3 Módulo Ventas (modificado — C01, C02, C03, C04, C09)

#### Pantalla: /Ventas/Crear (delta)

```
┌─ Ventas / Nueva Venta ──────────────────────────────────────────────┐
│                                                                      │
│  ── Sección 1: Encabezado ─────────────────────────────────────────│
│  Fecha *         [Hoy ▼]                                            │
│  Cliente         [Select2 buscar cliente...]  [ + Nuevo Cliente ]   │
│  Anotaciones     [_________________________________] (nota interna) │
│  Descuento %     [____]                                              │
│                                                                      │
│  ── Sección 2: Productos ──────────────────────────────────────────│
│  [Categoría ▼] → [Marca ▼] → [Modelo ▼] → [Color ▼] → [Talle ▼]  │
│  Precio unit. [________] (editable)   Cant. [__]   [ + Agregar ]   │
│                                                                      │
│  ┌─ Tabla detalle ──────────────────────────────────────────────┐   │
│  │ Producto       │ Cant │ Precio Unit. │ Subtotal │ [✗]        │   │
│  │ Air Max 90 #42 │  2   │  $ 45.000    │ $ 90.000 │ [✗]        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                            Subtotal:  $ 90.000                      │
│                  Descuento (  0 %):  $      0                       │
│                               Total: $ 90.000                       │
│                                                                      │
│  ── Sección 3: Pagos ──────────────────────────────────────────────│
│  ┌─ Lista pagos ────────────────────────────────────────────────┐   │
│  │ Medio            │ Importe    │ [✗]                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  Saldo pendiente: $ 90.000                                          │
│  [ + Agregar Pago ]  → abre modal con importe = saldo pendiente     │
│                                                                      │
│  ── Sección 4: Confirmación ───────────────────────────────────────│
│  [ Cancelar ]                          [ Confirmar Venta ]          │
└──────────────────────────────────────────────────────────────────────┘
```

**Modal Agregar Pago (C04):**
```
┌─ Modal ── Agregar Pago ─────────────────────────────────────────────┐
│  Medio de pago *      [Efectivo ▼]                                  │
│  Importe *            [$ 90.000]  ← precargado con saldo restante   │
│  % Financiamiento     [____]  (visible solo si Cuotas)              │
│  Cantidad cuotas      [____]  (visible solo si Cuotas)              │
│  [ Cancelar ]                    [ Agregar ]                         │
└──────────────────────────────────────────────────────────────────────┘
```

**Modal Nuevo Cliente (C02):**
```
┌─ Modal ── Nuevo Cliente ────────────────────────────────────────────┐
│  Nombre *   [_______________________]                               │
│  Teléfono   [_______________________]                               │
│  WhatsApp   [_______________________]                               │
│  [ Cancelar ]              [ Crear y Seleccionar ]                  │
└──────────────────────────────────────────────────────────────────────┘
```

#### Pantalla: /Ventas/Detalle (delta — C01)
Agregar fila "Anotaciones" en el bloque de encabezado de la venta:
```
│  Anotaciones:  [texto de la nota interna]   (solo visible en pantalla, no en remito PDF) │
```

---

#### 3.4 Módulo Compras (modificado — C05)

#### Pantalla: /Compras/Crear — /Compras/Editar (delta)
Reemplazar el Select2 de texto libre de variante por el selector anidado (mismo componente que Ventas).

```
│  ── Agregar Producto ────────────────────────────────────────────── │
│  [Categoría ▼] → [Marca ▼] → [Modelo ▼] → [Color ▼] → [Talle ▼]  │
│  Cantidad [__]   Costo unit. [________]    [ + Agregar ]            │
```

---

#### 3.5 Módulo Devoluciones (modificado — C07)

#### Pantalla: /Devoluciones/Crear (delta)
Se reemplaza el campo "Número de venta" por un buscador multi-criterio antes de iniciar el wizard.

```
┌─ Devoluciones / Nuevo Cambio o Devolución ─────────────────────────┐
│                                                                      │
│  ── Paso 0: Buscar Venta ──────────────────────────────────────────│
│  Fecha          [Desde ▼] [Hasta ▼]                                 │
│  Cliente        [Select2 buscar cliente...]                         │
│  Producto       [_______________________] (texto libre, parcial)    │
│                                           [ Buscar ]                │
│                                                                      │
│  ┌─ Resultados ──────────────────────────────────────────────────┐  │
│  │ Nro Venta │ Fecha     │ Cliente  │ Estado     │ Acciones      │  │
│  │ V-0042    │ 15/06/25  │ García   │ Entregada  │ [Seleccionar] │  │
│  │ V-0038    │02/06/25   │ García   │ Confirmada │ [Seleccionar] │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ── (Al seleccionar, continúa el wizard existente) ────────────────│
└──────────────────────────────────────────────────────────────────────┘
```

**Regla:** Solo se muestran ventas en estado `Confirmada` o `Entregada`.  
**Botón directo:** En `/Ventas/Detalle`, cuando la venta es Confirmada o Entregada, se agrega el botón `[ Iniciar Cambio / Devolución ]` que redirige a `/Devoluciones/Crear?ventaId=X` pre-seleccionando la venta.

**Selección de nueva variante en Cambio (C09):**
El paso "Elegir nuevo producto" del wizard usa el mismo selector anidado de 5 combos.

---

#### 3.6 Módulo Stock (modificado — C06, C08)

#### Pantalla: /Stock/Index (delta)
Mejora visual: reorganización de filtros, indicadores claros de alerta, acceso habilitado para rol Empleado.

```
┌─ Stock / Consulta de Stock ─────────────────────────────────────────┐
│                                                                      │
│  ── Filtros ───────────────────────────────────────────────────────│
│  [Categoría ▼] [Marca ▼] [Modelo ▼] [Color ▼] [Talle ▼]           │
│  [ Solo alertas ] (toggle)              [ Aplicar ] [ Limpiar ]     │
│                                                                      │
├─ DataTable ──────────────────────────────────────────────────────────┤
│  Producto       │ Color │ Talle │ Stock │ Mín. │ Estado             │
│  Air Max 90 #42 │  --   │  42   │  5    │  2   │ 🟢 OK             │
│  Remera M       │ Negro │   M   │  1    │  3   │ 🔴 Bajo mínimo    │
│  Air Max 90 #40 │  --   │  40   │  0    │  2   │ ⚫ Sin stock      │
├──────────────────────────────────────────────────────────────────────┤
│  (Para Admin/SuperUsuario: botones Ajuste y Carga Inicial visibles) │
└──────────────────────────────────────────────────────────────────────┘
```

**Reglas de visibilidad:**
- Precio de costo: visible solo para Admin/SuperUsuario.
- Botones Ajuste / Carga Inicial: visibles solo para Admin/SuperUsuario.
- Empleado y Vendedor: solo consulta (read-only).

**Indicadores de estado visual:**
| Estado | Condición | Color |
|---|---|---|
| 🟢 OK | Stock > StockMinimo | Verde |
| 🟡 Atención | Stock = StockMinimo | Amarillo |
| 🔴 Bajo mínimo | 0 < Stock < StockMinimo | Rojo |
| ⚫ Sin stock | Stock = 0 | Gris oscuro |

---

### 4. ViewModels propuestos — delta v2

#### 4.1 Nuevos (G1 — Refactor estructural)

#### `MarcaViewModel`
| Campo | Tipo | Validación |
|---|---|---|
| Id | int | — |
| Nombre | string | Required, MaxLength(100) |
| CategoriaId | int | Required |
| CategoriaNombre | string? | Solo lectura (display) |
| CantidadModelos | int | Solo lectura |

#### `ModeloViewModel`
| Campo | Tipo | Validación |
|---|---|---|
| Id | int | — |
| Nombre | string | Required, MaxLength(100) |
| MarcaId | int | Required |
| MarcaNombre | string? | Solo lectura |
| CategoriaNombre | string? | Solo lectura |
| CantidadProductos | int | Solo lectura |

#### `TalleConfigViewModel`
| Campo | Tipo | Validación |
|---|---|---|
| Id | int | — |
| Valor | string | Required, MaxLength(10) |
| Tipo | TipoTalle (enum) | Required |
| TipoNombre | string? | Solo lectura (display) |

---

#### 4.2 Modificados

#### `ProductoViewModel` (delta)
| Campo | Cambio |
|---|---|
| SubgrupoId | ➡ Renombrar a `MarcaId` |
| SubgrupoNombre | ➡ Renombrar a `MarcaNombre` |
| ModeloId (nuevo) | int?, FK a Modelo |
| ModeloNombre (nuevo) | string?, solo display |

#### `VarianteViewModel` (delta)
| Campo | Cambio |
|---|---|
| Marca | ❌ Eliminar |
| Modelo | ❌ Eliminar |
| Talle | ➡ Cambiar a `TalleId` (int?) para categorías con TalleConfig |
| Numero | ➡ Cambiar a `TalleId` para Zapatillas |
| EsCalzado | Sin cambio (sigue siendo heurística por categoría) |
| EsAccesorio (nuevo) | bool — heurística para ocultar combos de talle |

#### `VentaCreateViewModel` (delta)
| Campo | Cambio |
|---|---|
| Observaciones | ➡ Renombrar a `Anotaciones` |

#### `VentaDetalleViewModel` (delta)
| Campo | Cambio |
|---|---|
| Observaciones | ➡ Renombrar a `Anotaciones` |

---

#### 4.3 Nuevos (G2 — Flujo de Venta)

#### `ClienteRapidoViewModel` (para modal C02)
| Campo | Tipo | Validación |
|---|---|---|
| Nombre | string | Required, MaxLength(200) |
| Telefono | string? | MaxLength(20) |
| WhatsApp | string? | MaxLength(20) |

#### `VarianteSelectorRequest` (para endpoints AJAX de combos C03/C05)
| Campo | Tipo | Descripción |
|---|---|---|
| CategoriaId | int? | Filtrar marcas por categoría |
| MarcaId | int? | Filtrar modelos por marca |
| ModeloId | int? | Filtrar colores disponibles |
| Color | string? | Filtrar talles disponibles |
| TalleId | int? | Resolver VarianteProductoId final |

#### `VarianteSelectorResponse` (resultado de resolución)
| Campo | Tipo | Descripción |
|---|---|---|
| VarianteId | int | ID de la variante resuelta |
| Descripcion | string | Texto descriptivo para la tabla de detalle |
| PrecioVenta | decimal | Precio sugerido (editable en UI) |
| StockDisponible | int | Para mostrar disponibilidad |

---

#### 4.4 Nuevos (G4 — Devoluciones)

#### `BuscarVentaRequest` (búsqueda multi-criterio C07)
| Campo | Tipo | Validación |
|---|---|---|
| FechaDesde | DateTime? | Opcional |
| FechaHasta | DateTime? | Opcional |
| ClienteId | int? | Opcional |
| TextoProducto | string? | MaxLength(100), búsqueda parcial |

---

### 5. Contratos funcionales por servicio (delta v2)

#### 5.1 `IMarcaService` (nuevo)
```
CrearAsync(MarcaViewModel vm) → ServiceResult<int>
EditarAsync(MarcaViewModel vm) → ServiceResult
InactivarAsync(int id) → ServiceResult      // Guarda: sin productos activos
ObtenerAsync(int id) → ServiceResult<MarcaViewModel>
ListarAsync(DataTableRequest) → DataTableResponse<MarcaViewModel>
ObtenerPorCategoriaAsync(int categoriaId) → List<MarcaViewModel>  // Para cascada AJAX
```

#### 5.2 `IModeloService` (nuevo)
```
CrearAsync(ModeloViewModel vm) → ServiceResult<int>
EditarAsync(ModeloViewModel vm) → ServiceResult
InactivarAsync(int id) → ServiceResult      // Guarda: sin productos activos
ObtenerAsync(int id) → ServiceResult<ModeloViewModel>
ListarAsync(DataTableRequest, int? marcaId) → DataTableResponse<ModeloViewModel>
ObtenerPorMarcaAsync(int marcaId) → List<ModeloViewModel>  // Para cascada AJAX
```

#### 5.3 `IVarianteService` (delta — métodos nuevos)
```
// Endpoints AJAX para combos anidados (C03/C05)
ObtenerColoresPorModeloAsync(int modeloId) → List<string>
ObtenerTallesPorModeloColorAsync(int modeloId, string? color) → List<TalleConfigViewModel>
ResolverVarianteAsync(VarianteSelectorRequest req) → ServiceResult<VarianteSelectorResponse>
```

#### 5.4 `IClienteService` (delta — método nuevo)
```
CrearRapidoAsync(ClienteRapidoViewModel vm) → ServiceResult<ClienteViewModel>
// Crea con datos mínimos; resto de campos quedan null para completar después
// Política: RequireVendedor (no solo Admin)
```

#### 5.5 `IVentaService` (delta — ajuste naming)
```
// Sin cambios de firma; internamente: Observaciones → Anotaciones
// VentaCreateViewModel.Anotaciones se mapea a Venta.Anotaciones
```

#### 5.6 `IDevolucionService` (delta — método nuevo)
```
BuscarVentasParaDevolucionAsync(BuscarVentaRequest req) 
    → List<VentaListItemViewModel>
// Solo ventas en estado Confirmada o Entregada
// Filtra por fecha, clienteId, texto parcial de producto/variante
```

#### 5.7 `IStockService` (sin cambios de firma)
```
// ListarAsync ya existente; se agrega filtro por MarcaId y ModeloId en DataTableRequest
// Internamente el service aplica los nuevos filtros
```

---

### 6. Máquina de estados — delta v2

#### 6.1 Venta (extensión)

| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| (∅) | `CrearVenta` | Confirmada | (igual v1) + `Anotaciones` opcional max 1000 chars | (igual v1) | (igual v1) |
| Confirmada / Entregada | `IniciarDevolucion` | (mismo) | Estado Confirmada **o** Entregada (ampliado desde v1 que solo era Entregada) | Redirige a `/Devoluciones/Crear?ventaId=X` | "Solo ventas Confirmadas o Entregadas admiten devolución" |

#### 6.2 Soft delete — entidades nuevas

| Origen | Evento | Entidad | Guarda | Acción | Error |
|---|---|---|---|---|---|
| Activo | `Inactivar` | Marca | Sin productos activos ni modelos activos | Setear `DeletedAt` | "Marca con productos o modelos activos" |
| Activo | `Inactivar` | Modelo | Sin productos activos | Setear `DeletedAt` | "Modelo con productos activos" |
| Activo | `Inactivar` | TalleConfig | Sin variantes activas que lo referencien | Setear `DeletedAt` | "Talle en uso por variantes activas" |

---

### 7. Reglas de negocio y permisos por módulo/acción — delta v2

#### 7.1 Matriz de permisos ampliada (rol Empleado nuevo)

| Acción | SuperUsuario | Admin | Vendedor | **Empleado** |
|---|---|---|---|---|
| Login / Perfil propio | ✅ | ✅ | ✅ | ✅ |
| ABM Marcas / Modelos / TalleConfig | ✅ | ✅ | ❌ | ❌ |
| ABM Categorías / Proveedores | ✅ | ✅ | ❌ | ❌ |
| ABM Clientes (completo) | ✅ | ✅ | ❌ | ❌ |
| Crear cliente rápido (modal venta) | ✅ | ✅ | ✅ | ✅ |
| ABM Productos / Variantes | ✅ | ✅ | 👁️ | ❌ |
| Crear Venta | ✅ | ✅ | ✅ | ✅ |
| Ver ventas (propias) | ✅ todas | ✅ todas | ✅ propias | ✅ propias |
| Anular Venta | ✅ | ✅ | ✅ | ❌ |
| Marcar Entregada | ✅ | ✅ | ✅ | ✅ |
| Crear Cambio / Devolución | ✅ | ✅ | ✅ | ✅ |
| Consultar Stock | ✅ | ✅ | ✅ | ✅ |
| Ajuste manual / Carga inicial stock | ✅ | ✅ | ❌ | ❌ |
| Compras (cualquier acción) | ✅ | ✅ | ❌ | ❌ |
| Aumento Masivo | ✅ | ✅ | ❌ | ❌ |
| Resumen Semanal | ✅ | ✅ | ❌ | ❌ |
| Dashboard | ✅ full | ✅ full | ✅ limitado | ✅ mínimo |
| Gestión Usuarios | ✅ | ✅ | ❌ | ❌ |
| Auditoría | ✅ | ✅ | ❌ | ❌ |

#### 7.2 Policy nueva: `RequireEmpleado`
```
RequireEmpleado = SuperUsuario | Administrador | Vendedor | Empleado
```
Se aplica en los controllers de: `VentasController`, `DevolucionesController`, `StockController` (Index).  
Las acciones de ajuste/admin dentro de esos controllers mantienen `RequireAdministrador`.

#### 7.3 Menú de navegación por rol
| Ítem de menú | Admin | Vendedor | Empleado |
|---|---|---|---|
| Dashboard | ✅ | ✅ | ✅ (versión mínima) |
| Ventas | ✅ | ✅ | ✅ |
| Cambios y Devoluciones | ✅ | ✅ | ✅ |
| Stock | ✅ | ✅ | ✅ |
| Compras | ✅ | ❌ | ❌ |
| Productos | ✅ | ✅ (solo ver) | ❌ |
| Maestros (Categorías, Marcas, Modelos) | ✅ | ❌ | ❌ |
| Clientes | ✅ | ❌ (solo Select2) | ❌ |
| Resumen Semanal | ✅ | ❌ | ❌ |
| Aumento Masivo | ✅ | ❌ | ❌ |
| Usuarios / Auditoría | ✅ | ❌ | ❌ |

---

### 8. Impacto funcional por capa

#### 8.1 Presentación (Web)

| Elemento | Tipo de cambio | Detalle |
|---|---|---|
| `MarcasController` | NUEVO | Reemplaza/renombra SubgruposController |
| `ModelosController` | NUEVO | ABM de modelos anidados en marca |
| `SubgruposController` | RENOMBRAR o DEPRECAR | Pasa a ser MarcasController |
| `VentasController` | MODIFICAR | Agregar endpoint `CrearRapidoCliente` (AJAX); adaptar vista Crear |
| `DevolucionesController` | MODIFICAR | Agregar `BuscarVentasMulticriterio` (AJAX) |
| `StockController` | MODIFICAR | Habilitar acceso RequireEmpleado; mejorar vista Index |
| `VariantesController` | MODIFICAR | Agregar 3 endpoints AJAX: colores, talles, resolver variante |
| `ProductosController` | MODIFICAR | Vista Crear/Editar con cascada Categoría→Marca→Modelo |
| `Program.cs` | MODIFICAR | Agregar policy `RequireEmpleado`; agregar `RolEmpleado` en SeedData |
| Vistas nuevas | 4 | `/Marcas/Index`, `/Marcas/Crear`, `/Modelos/Index`, `/Modelos/Crear` |
| Vistas modificadas | 6 | Ventas/Crear, Ventas/Detalle, Compras/Crear, Devoluciones/Crear, Stock/Index, Variantes/Crear |
| JS | NUEVO/MODIFICAR | Componente de 5 combos anidados (reutilizable); autofill pago; recálculo automático precios |

#### 8.2 Negocio (Application)

| Elemento | Tipo | Detalle |
|---|---|---|
| `IMarcaService` | NUEVO | CRUD + `ObtenerPorCategoriaAsync` para AJAX |
| `IModeloService` | NUEVO | CRUD + `ObtenerPorMarcaAsync` para AJAX |
| `IVarianteService` | MODIFICAR | 3 métodos nuevos: colores, talles, resolver variante |
| `IClienteService` | MODIFICAR | Agregar `CrearRapidoAsync` |
| `IDevolucionService` | MODIFICAR | Agregar `BuscarVentasParaDevolucionAsync` |
| `IVentaService` | AJUSTE MÍNIMO | Renombrar Observaciones→Anotaciones internamente |
| `IStockService` | AJUSTE MÍNIMO | Soporte de filtros MarcaId/ModeloId en ListarAsync |
| ViewModels nuevos | 5 | MarcaViewModel, ModeloViewModel, TalleConfigViewModel, ClienteRapidoViewModel, VarianteSelectorRequest/Response, BuscarVentaRequest |
| ViewModels modificados | 3 | ProductoViewModel, VarianteViewModel, VentaCreateViewModel |

#### 8.3 Datos (Infrastructure)

| Elemento | Tipo | Detalle |
|---|---|---|
| `Subgrupo` entity | RENOMBRAR → `Marca` | Tabla renombrada; FK en Producto actualizada |
| `Modelo` entity | NUEVA | Id, Nombre, MarcaId — hija de Marca |
| `TalleConfig` entity | NUEVA | Id, Valor, Tipo (enum TipoTalle) |
| `Producto` entity | MODIFICAR | Agregar ModeloId (FK a Modelo); SubgrupoId → MarcaId |
| `VarianteProducto` entity | MODIFICAR | Quitar Marca y Modelo; Talle/Numero → TalleId (FK a TalleConfig) |
| `Venta` entity | MODIFICAR | Observaciones → Anotaciones (renombrar o mantener nombre interno + label UI) |
| `SeedData` | MODIFICAR | Agregar RolEmpleado; seed categorías; seed TalleConfig |
| Migraciones EF | 3 nuevas | M-R1: Marca/Modelo entidades; M-R2: TalleConfig + Variante; M-R3: Venta.Anotaciones |
| `AppDbContext` | MODIFICAR | Agregar DbSets de Marca, Modelo, TalleConfig; actualizar configs y relaciones |
| Script de migración de datos | CRÍTICO | Mover Marca/Modelo de Variante → Producto al aplicar M-R1 |

---

### 9. Riesgos y supuestos

| # | Tipo | Descripción | Mitigación |
|---|---|---|---|
| R1 | Riesgo | M-R1 es destructivo: quita Marca/Modelo de VarianteProducto | Migración en 2 pasos: agregar columnas en Producto, copiar datos, luego quitar de Variante. Backup obligatorio. |
| R2 | Riesgo | Combos anidados pueden no resolver variante si hay datos incompletos (Color/Talle null) | Mostrar solo opciones con datos completos; mensaje claro si no hay combinación disponible |
| R3 | Riesgo | Rol Empleado puede confundirse con Vendedor en policies | Policy `RequireEmpleado` inclusiva (Admin+Vendedor+Empleado). Acciones específicas siguen usando RequireAdministrador |
| R4 | Riesgo | SubgruposController renombrado puede romper links/bookmarks existentes | Agregar redirect `/Subgrupos` → `/Marcas` por compatibilidad |
| R5 | Supuesto | Los combos de Accesorios no tienen talle (solo Marca→Modelo→Color) | Validar que haya variantes de accesorios en producción con esta estructura |
| R6 | Supuesto | `Venta.Observaciones` renombrado a `Anotaciones` es un campo de datos (no solo UI) | Se renombra la columna en DB; migración requerida |
| R7 | Supuesto | Un Empleado no puede anular ventas (solo Vendedor+ puede anular) | Confirmado en matriz de permisos §7.1 |

---

### 10. Plan funcional por etapas para el arquitecto (delta v2)

> Las etapas originales F0–F8 ya están implementadas. Este plan cubre exclusivamente el trabajo nuevo.

#### Etapa V1-E1 — Refactor estructural del modelo (BLOQUEA TODO LO DEMÁS)
**Objetivo:** Nuevo árbol Categoría→Marca→Modelo + TalleConfig + seed.  
**Entregables funcionales:**
- Entidades Marca, Modelo, TalleConfig creadas y migraciones aplicadas.
- Producto con MarcaId + ModeloId.
- VarianteProducto sin Marca/Modelo, con TalleId.
- Seed: 3 categorías, talles predefinidos, rol Empleado.
- ABMs /Marcas y /Modelos operativos.
- Formulario de Producto con cascada Categoría→Marca→Modelo.
- Formulario de Variante con selector de talle predefinido.
**Criterio cierre:** Se puede crear un producto completo con la nueva jerarquía; las variantes existentes no se rompieron.

#### Etapa V1-E2 — Combos anidados en Ventas y Compras
**Objetivo:** Reemplazar Select2 libre por selector de 5 combos anidados.  
**Dependencia:** V1-E1 completa.  
**Entregables funcionales:**
- Endpoints AJAX en VariantesController (colores, talles, resolver variante).
- Componente JS de combos anidados (reutilizable).
- Vista `/Ventas/Crear` con el nuevo selector.
- Vista `/Compras/Crear` y `/Compras/Editar` con el mismo selector.
- Campo Anotaciones en formulario de venta.
- Autofill importe de pago (saldo restante).
- PrecioUnitario editable con recálculo automático de subtotal/total.
**Criterio cierre:** Se puede completar una venta y una compra end-to-end con combos anidados.

#### Etapa V1-E3 — Modal cliente + Búsqueda rápida devoluciones
**Objetivo:** Flujos de UX rápidos para operatoria diaria.  
**Dependencia:** V1-E2 completa (comparte vistas de venta).  
**Entregables funcionales:**
- Modal "Nuevo Cliente" accesible para Vendedor en /Ventas/Crear.
- Endpoint `POST /Clientes/CrearRapido` con policy RequireVendedor.
- Buscador multi-criterio en /Devoluciones/Crear (fecha, cliente, producto).
- Endpoint `POST /Devoluciones/BuscarVentas` con filtros ampliados.
- Botón "Iniciar Cambio/Devolución" en /Ventas/Detalle para estados Confirmada y Entregada.
- Combos anidados en modal de cambio de variante (wizard devoluciones).
**Criterio cierre:** Vendedor puede crear cliente y devolver producto sin salir del flujo de venta/devolución.

#### Etapa V1-E4 — Rol Empleado + mejora visual Stock
**Objetivo:** Nuevo rol operativo + interfaz de stock mejorada.  
**Dependencia:** V1-E1 (para que los filtros de stock ya usen Marca/Modelo).  
**Entregables funcionales:**
- Rol Empleado en SeedData + policy RequireEmpleado en Program.cs.
- Menú de navegación dinámico por rol (Empleado ve solo Ventas, Dev/Cambios, Stock).
- Vista /Stock/Index rediseñada: filtros Categoría/Marca/Modelo/Color/Talle; indicadores visuales 🟢🟡🔴⚫; precios de costo ocultos para Empleado/Vendedor.
**Criterio cierre:** Un usuario con rol Empleado puede operar sin ver módulos no autorizados; stock muestra indicadores visuales.

#### Dependencias entre etapas v2

```
V1-E1 (Refactor estructural)
  └─► V1-E2 (Combos anidados — requiere nueva jerarquía)
        └─► V1-E3 (Modal cliente + búsqueda devoluciones — comparte vistas E2)
  └─► V1-E4 (Rol Empleado — puede ejecutarse en paralelo con E2/E3)
```

---

### 11. Checklist de salida — Diseño funcional v2

```
DISEÑO FUNCIONAL v2 — CHECKLIST
─────────────────────────────────────────────────
[✓] Alcance funcional v2 resumido (12 cambios)
[✓] Decisiones P1–P15 + C11a consolidadas
[✓] Nuevo modelo conceptual Categoría→Marca→Modelo→Producto→Variante
[✓] Flujo de pantallas (delta) con wireframes textuales
[✓] ViewModels nuevos y modificados
[✓] Contratos funcionales por servicio (delta)
[✓] Máquina de estados — extensiones v2
[✓] Reglas de negocio y permisos — rol Empleado incluido
[✓] Impacto funcional por capa (Presentación / Negocio / Datos)
[✓] Riesgos y supuestos actualizados
[✓] Plan funcional V1-E1..E4 para el arquitecto
[✓] Sin pendientes funcionales bloqueantes
─────────────────────────────────────────────────
```

---

### 12. Handoff a Arquitectura

#### Paquete entregado
1. `1-analista-funcional.md` v2 (decisiones P1–P15 + C11a cerradas).
2. Este documento `2-disenador-funcional.md` v2.

#### Preguntas abiertas para el arquitecto

1. **Renombrado de tabla `Subgrupos` → `Marcas`:** ¿Renombrar físicamente la tabla EF o mantener nombre de tabla legacy y cambiar solo el nombre de clase/relación?
2. **TalleId en VarianteProducto:** ¿FK estricta a TalleConfig o campo string? con validación en service? Recomendado: FK estricta para integridad.
3. **Colores:** Actualmente texto libre (`VarianteProducto.Color`). ¿Se convierte en entidad también o queda texto libre? El analista recomienda mantenerlo texto libre en v2 (no fue solicitado).
4. **Combos AJAX — cantidad de endpoints:** 3 endpoints propuestos (colores, talles, resolver). ¿Se consolidan en uno solo parametrizado o quedan separados?
5. **Policy RequireEmpleado vs RequireVendedor:** Evaluar si conviene hacer RequireEmpleado inclusivo (Admin+Vendedor+Empleado) o agregar Empleado al RequireVendedor existente. Impacto: si se agrega al RequireVendedor, un Empleado podría acceder a acciones que hoy son solo-Vendedor y no son adecuadas para Empleado. Recomendado: policy separada.

---

### V10 — Diseño funcional: Carga masiva de stock por Marca + filtros completos en Consulta de Stock (2026-07-30)

**Input:** `1-analista-funcional.md` sección "V10", decisiones Q1–Q6 confirmadas por el cliente. Analisis cerrado y aprobado.

#### 0. Escaneo de reutilización cross-proyecto (obligatorio antes de diseñar)

Se escaneó `C:/Sistemas/Agentes-IA/docs/*/definiciones/{2-disenador-funcional,5-implementador}.md` de todos los proyectos del historial buscando "carga masiva" / "alta rápida inline" / "filas dinámicas + un submit".

**Coincidencia encontrada: LabIPAC — Sesión 2/3 (2026-07-08), feature "Producción Mensual — Carga Masiva + alta rápida"** (`docs/labipac/definiciones/2-disenador-funcional.md` y `5-implementador.md`). Patrón ya diseñado, implementado y **cerrado con QA real** (build OK, migración aplicada, ratio de sobreestimación PERT/real más bajo del dataset):

- Pantalla dedicada (no un modal) con **filas dinámicas manejadas por JS, sin DataTables** (es un formulario, no un listado): cada fila es un ítem a cargar, con botón "+ Agregar fila" y botón de fila "Quitar".
- **Un único submit guarda todo el lote** (`AgregarLineasAsync`), en **una sola transacción atómica: todo o nada** — si una fila es inválida, no se guarda ninguna y se marcan los errores puntuales por fila (RN-12/RN-13 de labipac).
- **Alta rápida inline de ítems faltantes** desde la propia fila: opción "+ Crear nuevo…" al final del select de la fila, abre un modal chico (Nombre + los campos mínimos obligatorios de esa entidad), guarda por AJAX y el nuevo ítem queda insertado y seleccionado en esa fila sin recargar la pantalla.
- Motivo/contexto único aplicado a todo el lote (en labipac: el período de Producción Mensual ya lo daba el contexto de la pantalla).

**Decisión: reutilizar este patrón adaptado al dominio de Stock**, en vez de diseñar desde cero. Esto resuelve además una inconsistencia detectada contra el Análisis (ver punto de atención más abajo).

**Punto de atención — ajuste sobre lo definido en Análisis:** en `1-analista-funcional.md` se había dejado como criterio de aceptación "si una fila falla, el resto del lote no se pierde (parcial)". El patrón de referencia (labipac RN-12) usa **atomicidad total: todo el lote o nada**, que es más simple, más segura para trazabilidad de stock (evita estados intermedios confusos: "algunas variantes con stock nuevo, otras no") y ya está probada en producción. **Se propone adoptar atomicidad total** para la carga masiva de stock, reemplazando el criterio parcial del Análisis. Queda marcado como decisión de Diseño a confirmar en el gate (no se aplica todavía sin esa confirmación).

#### 1. Alcance funcional resumido

Sin cambios de alcance respecto a lo aprobado en Análisis (Q1 absoluto, Q2 scope Marca completa, Q3 crea variante al vuelo con Precio de Venta + Stock Mínimo en la grilla, Q6 Estado reemplaza botón). Este diseño instancia ese alcance en pantallas, ViewModels y reglas concretas, reutilizando el patrón de labipac.

#### 2. Flujo de pantallas y wireframes textuales

#### WF-A1: Stock — Carga Masiva (pantalla nueva)
**Ruta:** `GET /Stock/CargaMasiva?marcaId={id}` (selección) · `POST /Stock/CargaMasiva` (guardado del lote)
**Rol:** `RequireAdministrador` (mismo permiso que `/Stock/Ajuste` hoy)
**Se accede desde:** botón "Carga masiva" (btn-primary) junto a "Ajuste manual" en `/Stock/Index`, visible solo para Admin/SuperUsuario.

```
┌─ Stock / Carga Masiva ──────────────────────────────────────────────┐
│  Marca *  [Select2 buscar marca...]  (mismo patron AJAX de Ajuste)   │
│  [ Cargar variantes ]                                                 │
├────────────────────────────────────────────────────────────────────┤
│  (al elegir Marca, recarga la pantalla agrupada por Modelo)          │
│                                                                        │
│  ── Modelo: Air Max 90 ──────────────────────────────────────────────│
│  Color   │ Talle │ Código   │ Stock actual │ Cantidad nueva │ [Quitar]│
│  Negro   │  42   │ AM90-N42 │     5        │  [___]         │         │
│  Blanco  │  40   │ AM90-B40 │     0        │  [___]         │         │
│  [ + Agregar variante nueva ]  ← abre fila editable: Color, Talle     │
│    (Select ▼ filtrado por TipoTalle del Modelo), Precio Venta,        │
│    Stock Mínimo, Cantidad inicial                                     │
│                                                                        │
│  ── Modelo: Air Force 1 ─────────────────────────────────────────────│
│  ... (misma estructura, una sección por Modelo de la Marca) ...       │
│                                                                        │
│  ── Motivo del lote ──────────────────────────────────────────────── │
│  Motivo * [_________________________________]                        │
│                                                                        │
│  [ Cancelar ]                    [ Guardar todo el lote ]            │
└────────────────────────────────────────────────────────────────────────┘
```
- Filas de variantes existentes: Color/Talle/Código/Stock actual son solo lectura; solo "Cantidad nueva" es editable. Fila sin cambio (igual al stock actual) no se envía como modificación.
- Fila de variante nueva: Color y Talle **no** pueden repetir una combinación ya existente en ese Producto (validación cliente + servidor, análoga a RN-13 de labipac); Talle se ofrece como select acotado al `TipoTalle` del Modelo (mismo catálogo que ya usa `/Variantes/Crear`).
- "Guardar todo el lote": un solo submit, todo o nada (ver punto de atención §0).
- Tras guardar: vuelve a la misma pantalla con la Marca ya cargada y los stocks actualizados (continuidad, mismo criterio que V9), mensaje de éxito con cantidad de variantes actualizadas/creadas.

#### WF-A2 (ajuste): `/Stock/Index` — botón nuevo
Se agrega botón "Carga masiva" (btn-outline-primary) junto al botón "Ajuste manual" existente, mismo criterio de visibilidad (solo Admin/SuperUsuario).

#### WF-B1 (delta): `/Stock/Index` — filtros completos
```
┌─ Filtros ────────────────────────────────────────────────────────────┐
│ [Categoría ▼] [Marca ▼] [Modelo ▼] [Talle ▼] [Color ▼] [Estado ▼]   │
│                                                    [ Limpiar ]        │
└────────────────────────────────────────────────────────────────────────┘
```
- Se agrega el combo **Talle**, dependiente de Modelo (mismo patrón que Color: deshabilitado hasta elegir Modelo, se puebla vía AJAX con los talles usados por ese Modelo).
- El botón "Solo alertas" **se reemplaza** por el combo **Estado** (Todos / OK / Límite / Bajo), integrado a la misma barra, recargando la tabla vía AJAX igual que el resto de los filtros (sin recargar la página).
- El link `/Stock/Index?soloAlertas=true` (usado desde Dashboard) se preserva: al llegar con ese querystring, la pantalla precarga el combo Estado en "Bajo".
- `ExportarExcelAsync` recibe los mismos filtros nuevos (`talleConfigId`, `estado`) para mantener consistencia grilla/export (regla de filtros de `25-frontend-design-system.instructions.md`: cada columna visible tiene su filtro).

#### 3. ViewModels propuestos

| VM | Campos | Validación |
|---|---|---|
| `StockCargaMasivaViewModel` | MarcaId, MarcaNombre, Motivo, List\<`StockCargaMasivaModeloViewModel`\> Modelos | Motivo requerido (MaxLength 500); al menos 1 fila modificada o nueva en todo el lote |
| `StockCargaMasivaModeloViewModel` | ModeloId, ModeloNombre, TipoTalle, List\<`StockCargaMasivaFilaViewModel`\> Filas | — |
| `StockCargaMasivaFilaViewModel` | VarianteId (null si es nueva), Color, TalleConfigId, CodigoInterno (solo lectura si existente), StockActual (solo lectura), CantidadNueva, PrecioVenta (solo si es nueva), StockMinimo (solo si es nueva) | CantidadNueva >= 0; si VarianteId es null (fila nueva): Color y TalleConfigId requeridos y sin duplicar combinación dentro del ProductoId; PrecioVenta >= 0 requerido; StockMinimo >= 0 requerido |
| `StockFiltroViewModel` (delta, uso interno en `/Stock/Index`) | + TalleConfigId (int?), Estado (enum `EstadoStockFiltro`: Todos/OK/Limite/Bajo) | — |

`EstadoStockFiltro` (nuevo enum, Web o Application): `Todos = 0, OK = 1, Limite = 2, Bajo = 3`. Mapea a la misma lógica que hoy ya calcula `EnAlerta`/`Deficit` en `StockListItemViewModel` (Bajo = `StockActual <= StockMinimo`; Límite = `0 < Deficit <= 5`; OK = resto).

#### 4. Máquina de estados
No aplica. Se reutilizan los flujos existentes de `AjusteStock`/`MovimientoStock` (sin estados propios) y el alta de `VarianteProducto` no tiene máquina de estados (entidad simple con soft delete).

#### 5. Reglas de negocio y permisos

| Ref | Regla | Capa |
|---|---|---|
| RN-M1 | Guardado del lote es atómico: todas las filas (modificadas + nuevas) se persisten en una única transacción, o ninguna | Service |
| RN-M2 | No se permite la misma combinación Color+TalleConfigId repetida para el mismo Producto dentro del mismo submit, ni contra variantes ya existentes | Service + validación cliente |
| RN-M3 | Fila de variante nueva exige PrecioVenta >= 0 y StockMinimo >= 0 (mismos mínimos que `/Variantes/Crear` hoy); CodigoInterno/CodigoBarra quedan `null`, completables después desde Productos/Variantes | DataAnnotation + Service |
| RN-M4 | Cada variante con `CantidadNueva` distinta de su stock actual genera su propio `AjusteStock` + `MovimientoStock` (mismo mecanismo que `AjusteManualAsync`, dentro de la transacción del lote) | Service |
| RN-M5 | El campo Motivo es único por lote y se replica igual en cada `AjusteStock` generado por ese submit | Service |
| RN-M6 | Permiso `RequireAdministrador` para toda la pantalla de Carga Masiva (mismo criterio que Ajuste individual y que el alta de variantes en Productos/Variantes) | Web |
| RN-B1 | Filtro Talle en `/Stock/Index`: dependiente de Modelo, deshabilitado hasta elegir Modelo (mismo patrón que Color) | Web |
| RN-B2 | Filtro Estado reemplaza al botón "Solo alertas"; el deep-link `?soloAlertas=true` sigue funcionando preseleccionando Estado=Bajo | Web |

#### 6. Impacto funcional por capa

**Presentación (Web):**
- `StockController`: + acciones `CargaMasiva` (GET/POST) y endpoint AJAX de validación de duplicado si se decide validar antes del submit.
- Vista nueva: `Views/Stock/CargaMasiva.cshtml` (secciones por Modelo, filas JS dinámicas, sin DataTables — mismo patrón visual que `CargaMasiva.cshtml` de labipac).
- `Views/Stock/Index.cshtml`: + combo Talle, reemplazo del botón "Solo alertas" por combo Estado.
- JS: componente de fila dinámica (agregar/quitar variante nueva), reutilizable del patrón ya construido en labipac (adaptado, no es el mismo repo así que se reimplementa el patrón, no el código).

**Negocio (Application/Infrastructure):**
- `IStockService`: + `ObtenerParaCargaMasivaAsync(int marcaId)` (arma la grilla agrupada por Modelo) y + `GuardarCargaMasivaAsync(StockCargaMasivaViewModel vm, string usuarioId)` (transacción atómica, crea variantes faltantes + AjusteStock/MovimientoStock por fila modificada).
- `IVarianteService` o el propio `StockService`: alta de `VarianteProducto` reutilizando la misma validación de unicidad Color+TalleConfigId que ya aplica (implícitamente) en `/Variantes/Crear`.
- `IStockService.ListarAsync`/`ExportarExcelAsync`: + parámetros `talleConfigId` y `estado`.

**Datos (Infrastructure):**
- Sin migración EF: `VarianteProducto`, `Stock`, `AjusteStock`, `MovimientoStock`, `TalleConfig` ya existen con todos los campos necesarios.
- Alta de `VarianteProducto` + su fila `Stock` asociada (hoy cada variante ya tiene 1:1 `Stock` — confirmar en Arquitectura cómo se crea ese registro relacionado al dar de alta desde este flujo, mismo mecanismo que usa hoy `/Variantes/Crear`).

#### 7. Riesgos y supuestos

- **DD-1 (decisión a confirmar en el gate):** atomicidad total del lote (todo o nada) en vez del criterio parcial documentado en Análisis — ver §0.
- **DD-2:** volumen de filas por Marca (varios Modelos × Color × Talle) puede ser grande; a diferencia de labipac (filas sueltas sin agrupar), acá se agrupa visualmente por Modelo con `<details>`/acordeón colapsable para no saturar la pantalla — validar con el cliente si el volumen típico lo requiere.
- **DD-3:** el alta de `VarianteProducto` desde Stock es una fila embebida en la misma grilla (no un modal separado como en labipac), porque acá el dato que falta es estructural (Color+Talle, no solo Nombre) — se mantiene el espíritu de "alta rápida sin salir de la pantalla" pero con layout distinto al de labipac.
- Riesgo heredado de Análisis: concurrencia por fila vía `RowVersion` de `VarianteProducto` debe seguir chequeándose aunque el guardado sea atómico a nivel de lote (cada fila igual valida su propia versión antes de aplicar).
- Riesgo heredado: `ExportarExcelAsync` debe sumar `talleConfigId`/`estado` para no quedar inconsistente con los filtros nuevos de la grilla.

#### 8. Historias de usuario

**HU-M1** — Como Administrador, quiero cargar el stock de todas las variantes de una Marca en una sola pantalla, para no tener que repetir el ajuste manual variante por variante.
- AC: al elegir una Marca, veo todas sus variantes existentes agrupadas por Modelo, con su stock actual y un campo editable de cantidad nueva.
- AC: puedo editar cualquier subconjunto de filas sin completar todas.
- AC: un único botón guarda todas las filas modificadas en una sola operación.

**HU-M2** — Como Administrador, quiero dar de alta una combinación de Color y Talle que todavía no existe mientras cargo stock, para no tener que ir primero a Productos/Variantes y volver.
- AC: cada sección de Modelo tiene una opción "+ Agregar variante nueva" que pide Color, Talle, Precio de Venta, Stock Mínimo y Cantidad inicial.
- AC: no puedo crear una combinación Color+Talle que ya existe para ese Modelo/Producto.
- AC: al guardar el lote, la variante nueva queda creada con esos datos y con el stock inicial cargado.

**HU-M3** — Como Administrador, quiero que si algo falla en la carga masiva no se guarde nada a medias, para no terminar con stock inconsistente entre variantes de un mismo lote.
- AC: si alguna fila tiene un error de validación, no se persiste ninguna fila del lote y se muestran los errores puntuales por fila.

**HU-B1** — Como usuario con acceso a Stock, quiero filtrar la consulta de stock por Talle, para encontrar rápido una variante puntual.
- AC: el combo Talle se habilita al elegir Modelo y filtra la grilla server-side sin recargar la página.

**HU-B2** — Como usuario con acceso a Stock, quiero filtrar por Estado (OK/Límite/Bajo) desde la misma barra de filtros, para no depender de un botón aparte que recarga toda la pantalla.
- AC: el combo Estado reemplaza al botón "Solo alertas" y se combina con el resto de los filtros.
- AC: el link directo `?soloAlertas=true` sigue funcionando, precargando Estado=Bajo.

#### 9. Plan funcional por etapas para Arquitectura

- **Etapa V10-A — Filtros completos en Consulta de Stock:** combo Talle + combo Estado (reemplaza botón), ajuste de `ListarAsync`/`ExportarExcelAsync`. Sin dependencias, menor esfuerzo — puede hacerse primero o en paralelo.
- **Etapa V10-B — Carga masiva de stock por Marca:** pantalla `CargaMasiva`, `ObtenerParaCargaMasivaAsync`, `GuardarCargaMasivaAsync` (atómico), alta de `VarianteProducto` inline. Depende de que la Arquitectura confirme el mecanismo exacto de alta de `VarianteProducto`+`Stock` asociado dentro de la misma transacción del lote.

#### DD-1 — Resuelto por el cliente (2026-07-30)

**Decisión confirmada:** persistencia **atómica (todo o nada)** — si una fila falla, no se guarda ninguna del lote — **pero** la pantalla debe: (a) mostrar los errores puntuales por fila (qué falló y en qué fila), y (b) **no perder los datos ya tipeados** en el resto de las filas al re-renderizar tras el error (el usuario corrige solo lo que falló, sin tener que volver a cargar todo el lote de cero).

**Impacto en diseño:** `POST /Stock/CargaMasiva` que falla en validación de servidor devuelve la misma vista (`return View(vm)`) con el `StockCargaMasivaViewModel` completo tal como fue enviado (todas las filas con sus valores ingeridos) + `ModelState` con los errores puntuales anclados a cada fila (mismo patrón MVC estándar de `asp-validation-for` por campo, ya usado en todo el proyecto — no requiere mecanismo nuevo). No se transaccionan filas parciales en ningún caso.

#### Estado
DISEÑO FUNCIONAL V10 CERRADO Y APROBADO. DD-1 resuelto (atómico + errores por fila + no pérdida de datos tipeados). Listo para Arquitectura.

#### Corrección post-cierre (2026-08-11) — Reversión de DD-1

**El comportamiento real desplegado ya NO es el de DD-1 arriba.** El cliente pidió explícitamente invertir el criterio: *"guardar todos los productos que están OK e informar los que tienen errores"*, en vez de descartar el lote completo si una fila falla. Cambio aplicado como fix directo (fuera de gates, mismo criterio ya usado en este proyecto para correcciones sobre funcionalidad recién entregada) — commit `74a115f`, documentado en `trazabilidad.md` entrada "2026-08-11 — Reversión de DD-1".

- **HU-M3 queda obsoleta tal como está escrita arriba** ("si algo falla no se guarda nada a medias"). Reemplazada en la práctica por: *"Como Administrador, quiero que si algo falla en una fila de la carga masiva, esa fila puntual no se guarde pero el resto del lote sí, para no perder el trabajo de las filas que estaban bien."*
- **Mecanismo real:** `StockService.GuardarCargaMasivaAsync` abre una transacción propia **por fila** (no una única transacción para todo el lote). Si una fila falla, rollback solo de esa fila; el resto sigue procesándose y se persiste.
- El mismo criterio de guardado parcial (transacción por fila/celda) se reutilizó después en la Vista Matriz editable (`StockService.GuardarMatrizAsync`, ver sección nueva más abajo) — quedó establecido como el patrón estándar de este proyecto para guardados en lote, reemplazando la atomicidad total como default.

#### V10.1 — Vista Matriz de Stock (Marca → Modelo → Color × Talle) (2026-08-11, retroactivo)

No se generó un diseño funcional formal previo para esta feature (se hizo con `EnterPlanMode` + preguntas directas al cliente en el chat, no por el flujo de agentes). Se deja este resumen para que el historial de diseño no quede con un vacío entre V10 y lo que hoy es la pantalla principal de Stock:

- **Pedido:** que la pantalla de Stock se vea como la planilla Excel real del cliente — pivot Marca→Modelo→Color (filas) × Talle (columnas), con la cantidad en cada celda.
- **Decisiones del cliente:** (1) la Matriz **convive** con la Consulta de Stock plana existente (no la reemplaza); (2) es **editable por celda**, no solo lectura; (3) el caso "mismo Modelo con dos sistemas de talle a la vez" (Talle Brasilero + Talle Argentino) se modela como distinción real; (4) solo se muestran celdas con stock > 0 en la vista de lectura (fiel al Excel).
- **Etapa 1 (022bd07):** `IStockService.ObtenerMatrizAsync` + `StockController.Matriz` + `Views/Stock/Matriz.cshtml`, solo lectura.
- **Etapa 2 (06bb253):** nuevo valor de enum `TipoTalle.ZapatillaAdultoArgentino` — sin migración EF (persiste como int), sin seed hardcodeado (el cliente carga los valores reales vía el ABM genérico `/TallesConfig` ya existente).
- **Etapa 3 (0eba0fc):** `StockController.MatrizEditar` (GET/POST) + `StockService.GuardarMatrizAsync`, mismo patrón de guardado parcial fila-por-fila que Carga Masiva. Acotado a una Marca por vez para no repetir el problema de formularios gigantes (mismo motivo que el incidente de 500 de Carga Masiva, ver `trazabilidad.md`).
- **Ampliaciones post-Etapa 3, todas fast-path (sin gates):**
  - `9e43229`/`42b7f19` — Matriz pasa a ser la pantalla principal del menú Stock; la edición admite variantes en stock 0 (parámetro `soloConStock`).
  - `1122c3c` — errores de guardado ahora disparan el toast global de SweetAlert2 (antes solo se veían en un `<div>` pasivo, fácil de no notar).
  - `f400671` — las celdas "—" (Color existente sin variante para ese Talle) pasan a ser editables: cargar una cantidad ahí da de alta la variante nueva (`StockMatrizAltaGuardarViewModel`, mismo patrón de transacción por fila + Precio/Stock Mínimo sugeridos por fila de Color).
- **Limitación de alcance conocida:** la Matriz solo permite completar un Talle faltante para un Color que **ya existe**. No permite dar de alta un Color completamente nuevo para un Modelo (las filas solo se arman a partir de colores con al menos una variante existente) — eso sigue siendo exclusivo de Carga Masiva. Tampoco cubre Modelos sin sistema de Talle (accesorios): `ObtenerMatrizAsync` descarta esas secciones (`TalleConfig == null`) — pendiente de evaluación, ver `trazabilidad.md`.

---

### V12 — Diseño: extensión de Matriz (accesorios + alta de Color nuevo) y retiro de Carga Masiva/Ajuste (2026-08-16)

**Input:** `1-analista-funcional.md` sección "V12", decisiones D1–D4 confirmadas por el cliente. Análisis cerrado y aprobado.

#### 0. Escaneo de reutilización

- **Dentro del proyecto (match directo):** `CargaMasiva.cshtml` ya resuelve, con otro layout, exactamente los dos problemas de esta feature — fila de alta con Color+Talle+Precio+StockMinimo+Cantidad (para Color nuevo), y Talle opcional según `Modelo.TipoTalle` (para accesorios). Se toma como base funcional para las reglas de validación; el layout se adapta a la tabla pivot en vez de copiarse literal (la tabla de la Matriz es más angosta por columna que la grilla de Carga Masiva).
- **Cross-proyecto:** `docs/patrones/catalogo.yml` no tiene ningún patrón de grilla pivot Talle×Color — es original de ShowroomGriffin. No hay match para portar. Se deja nota para catalogar esta feature como patrón reutilizable (candidato PAT-009) una vez cerrada, dado que cualquier proyecto con variantes por Talle×Color podría necesitarla.
- **Decisión:** no se reutiliza código ajeno; se extiende el propio `StockMatrizAltaGuardarViewModel`/`GuardarMatrizAsync` ya construidos el mismo día para la alta-desde-celda-vacía, en vez de crear un mecanismo paralelo.

#### 1. Flujo de pantalla y navegación

**Sin cambios de navegación:** sigue siendo `/Stock/Matriz` (lectura) → botón "Editar" → `/Stock/MatrizEditar?marcaId=` (edición), acotado a una Marca por vez, igual que hoy.

**Dentro de `MatrizEditar`, por cada Modelo:**
- Si el Modelo tiene sistema de Talle (como hoy): tabla pivot Color × Talle, con las celdas existentes editables y las celdas "—" editables para alta de Talle faltante (sin cambios, ya construido) **+ una fila nueva al final: "+ Nuevo color"**, con un input de texto para Color y un input de cantidad por cada columna de Talle (D2), colapsada/vacía por defecto (no ocupa espacio visual si el usuario no la usa).
- Si el Modelo NO tiene sistema de Talle (accesorio, `TipoTalle == null`): tabla de 2 columnas, Color | Cantidad (D1), una fila por Color existente (editable, mismo criterio que hoy: precarga `StockActual`, guarda solo si cambia) **+ una fila "+ Nuevo color"** al final con input de Color + Cantidad + Precio + Stock Mínimo (sin columnas de Talle que llenar, todo en la misma fila).

**`Matriz.cshtml` (solo lectura):** agrega las secciones de accesorios con el mismo layout de 2 columnas (D1), sin fila de alta (la vista de lectura no edita, igual que hoy con las secciones de Talle).

**`Stock/Index.cshtml`:** se quitan los botones "Ajuste manual" y "Carga masiva" (D3 — solo se ocultan, el código de `StockController.Ajuste`/`CargaMasiva` y sus vistas queda intacto, sin ruta de acceso desde el menú ni desde esta pantalla).

#### 2. Validaciones de UI y mensajes

- Fila "+ Nuevo color" (con Talle): el Color es obligatorio si se cargó alguna cantidad en cualquiera de sus columnas de Talle — mismo criterio de "silencio si no se tocó nada" que ya usa `CargaMasiva` para sus filas nuevas. Si se cargó Color pero ninguna cantidad, se ignora la fila completa (nada que dar de alta).
- Fila "+ Nuevo color" (sin Talle, accesorios): Color obligatorio si se cargó una Cantidad > 0; Precio de Venta obligatorio y > 0; Stock Mínimo obligatorio y ≥ 0 — mismos mensajes ya usados en la alta-desde-celda-vacía actual.
- Duplicados: mismo mecanismo ya construido (`combosEnEsteLote` + chequeo contra `VariantesProducto` existentes, respaldado ahora también por el índice único de BD agregado el 2026-08-16) — un Color nuevo que coincide con uno ya existente en el mismo Producto se informa como error puntual de esa fila, sin descartar el resto del guardado.
- Precio de Venta y Stock Mínimo de la fila "+ Nuevo color" (con Talle): un único par de inputs por fila que aplica a **todos** los Talles cargados en esa fila (mismo criterio "sugerido por fila" ya usado en la alta-desde-celda-vacía, no un precio distinto por Talle).

#### 3. ViewModels propuestos (extienden, no reemplazan, los de la Etapa 3.1)

- `StockMatrizAltaGuardarViewModel.TalleConfigId`: pasa de `int` (`[Required]`) a `int?` **sin** `[Required]` — necesario para que una alta de accesorio (sin sistema de Talle) pueda postear sin Talle. Mismo patrón ya usado en `StockCargaMasivaFilaViewModel.TalleConfigId`, donde la obligatoriedad se valida condicionalmente en el Service según si el Modelo tiene `TipoTalle` configurado.
- `StockMatrizSeccionViewModel`: sin cambios de forma — cuando el Modelo no tiene Talle, se arma con `Talles = []` (lista vacía) y cada `StockMatrizFilaViewModel.Celdas` tiene una única entrada con una clave sentinel reservada (`0`, ya que los `TalleConfigId` reales son siempre positivos por ser autoincrementales) para la celda "Cantidad" única. La vista distingue el layout por `seccion.Talles.Count == 0`.
- Sin ViewModels nuevos — todo se resuelve extendiendo los 4 ya existentes de la Etapa 3.1 (`StockMatrizCeldaViewModel`, `StockMatrizFilaViewModel`, `StockMatrizAltaGuardarViewModel`, `StockMatrizGuardarViewModel`).

#### 4. Eventos de negocio relevantes

- Alta de Color nuevo con múltiples Talles a la vez: se traduce en **N registros de `Altas`** (uno por Talle con cantidad cargada), todos con el mismo Color tipeado por el usuario — no requiere una entidad "Color" propia en el modelo de datos (sigue sin existir, `Color` es y sigue siendo un campo de texto en `VarianteProducto`, sin catálogo). Cada uno se procesa como alta independiente en su propia transacción, mismo patrón ya vigente.
- Alta de Color nuevo en accesorio: un único registro de `Altas` con `TalleConfigId = null`.

#### 5. Impacto por capa

- **Application:** `StockMatrizAltaGuardarViewModel.TalleConfigId` → nullable. Sin DTOs nuevos.
- **Infrastructure:** `StockService.ObtenerMatrizAsync` deja de descartar secciones con `TalleConfig == null` (arma una `StockMatrizSeccionViewModel` con `Talles = []` en su lugar). `StockService.GuardarMatrizAsync`: el loop de `Altas` incorpora la validación condicional de Talle obligatorio (según si el `Modelo` del `ProductoId` de esa alta tiene `TipoTalle` configurado) — mismo criterio que ya usa `GuardarCargaMasivaAsync`.
- **Web:** `Matriz.cshtml`/`MatrizEditar.cshtml` con el nuevo layout de accesorios + fila "+ Nuevo color" (JS de sincronización análogo al ya construido para Precio/Stock Mínimo sugeridos, extendido para propagar el Color tipeado a cada `Altas[i].Color` de la fila). `Stock/Index.cshtml`: quita 2 botones. `StockController`: sin acciones nuevas — reutiliza `Matriz`/`MatrizEditar` ya existentes.
- **Datos:** sin migración EF. `TalleConfigId` en `VarianteProducto` ya es nullable (soporta accesorios desde el modelo original).

#### 6. Riesgos de implementación

- **Fila "+ Nuevo color" con Talle es la pieza de UI nueva de mayor riesgo** (mismo perfil que causó D-01/D-02): requiere que TODOS sus inputs (incluida la cantidad por cada columna de Talle) sean opcionales/nullable en el binding, y que cualquier valor decimal (Precio) se renderice con `CultureInfo.InvariantCulture` — checklist explícito a verificar antes de cerrar Implementación, no solo al final.
- Índices `filaIdx`/`altaIdx` de la vista ya existente crecen con una fila más por sección — sin riesgo nuevo (el contador ya es global y no se reinicia, confirmado por QA el mismo día).
- Ocultar los botones de `Stock/Index.cshtml` sin eliminar las rutas: verificar que ningún otro lugar del sistema (Dashboard, otros menús) siga linkeando a `/Stock/CargaMasiva` o `/Stock/Ajuste` de forma directa, para no dejar accesos huérfanos sin el contexto de los botones removidos.

#### 7. Historias de usuario

**HU-12.1** — Como Administrador, quiero ver y editar el stock de mis accesorios (sin talle) en la misma Matriz que uso para calzado, para no tener que ir a otra pantalla.
- AC: al elegir una Marca con Modelos de accesorios, la Matriz muestra una sección por Modelo con una tabla Color | Cantidad.
- AC: editar la Cantidad de un Color existente guarda igual que en las secciones con Talle (solo si cambió, con Motivo obligatorio).

**HU-12.2** — Como Administrador, quiero dar de alta un Color completamente nuevo para un Modelo con Talle directamente desde la Matriz, para no depender de Carga Masiva.
- AC: la fila "+ Nuevo color" al final de cada sección con Talle permite tipear un Color y cargar cantidad en una o más columnas de Talle a la vez.
- AC: si cargo Color pero ninguna cantidad, no se crea nada (silencio, sin error).
- AC: si el Color+Talle ya existe para ese Producto, se informa el error puntual de esa combinación sin perder el resto del guardado.

**HU-12.3** — Como Administrador, quiero dar de alta un Color nuevo de un accesorio directamente desde la Matriz, con su Precio y Stock Mínimo.
- AC: la fila "+ Nuevo color" de una sección sin Talle pide Color, Cantidad, Precio de Venta y Stock Mínimo en una sola fila.
- AC: mismas validaciones de obligatoriedad que la alta con Talle, sin pedir ningún dato de Talle.

**HU-12.4** — Como Administrador, quiero dejar de ver los accesos a "Ajuste manual" y "Carga masiva" en Stock, para no confundirme sobre cuál pantalla usar.
- AC: `Stock/Index.cshtml` no muestra los botones "Ajuste manual" ni "Carga masiva".
- AC: las rutas `/Stock/Ajuste` y `/Stock/CargaMasiva` siguen respondiendo si se accede directamente por URL (no se eliminan, solo se ocultan los accesos) — decisión D3, revertible sin deploy de emergencia si hiciera falta.

#### Estado
DISEÑO FUNCIONAL V12 CERRADO Y APROBADO (decisiones D1–D4 ya confirmadas por el cliente en el gate de Análisis, sin puntos nuevos abiertos en Diseño). Listo para Arquitectura.

## Historial de ajustes
- 2026-07 (v2.0): Diseño funcional de los 12 cambios (C01-C12) sobre la base v1 (F0-F8) ya implementada — alcance, distribución estándar, flujo de pantallas, ViewModels, contratos por servicio, máquina de estados, reglas de negocio/permisos, impacto por capa, riesgos, plan por etapas.
- 2026-07-30: V10 — Diseño de carga masiva de stock por Marca + filtros completos en Consulta de Stock.
- 2026-08-16: V12 — Diseño de extensión de Matriz (accesorios + alta de Color nuevo) y retiro (oculto) de Carga Masiva/Ajuste.
- 2026-08-16: Reestructuración documental — se agregó el encabezado estándar `## Proyecto:`/`## Ultima actualizacion:`/`## Definiciones vigentes` y este historial, sin tocar el contenido técnico existente.
