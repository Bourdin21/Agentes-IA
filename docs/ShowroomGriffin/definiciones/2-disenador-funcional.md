# 2 — Diseño Funcional v2
## Sistema de Gestión Comercial — ShowroomGriffin
**Versión:** 2.0  
**Estado:** En diseño  
**Base:** `1-analista-funcional.md` v2 aprobado (decisiones P1–P15 + C11a cerradas)  
**Predecesor:** v1.0 (F0–F8 implementados — base del sistema operativa)

> Este documento diseña exclusivamente los **12 cambios nuevos (C01–C12)** sobre la base ya implementada.  
> El diseño v1 (`diseño-funcional.md`) permanece vigente para los módulos base.

---

## 1. Alcance funcional resumido

### Cambios agrupados por área de impacto

| Grupo | Cambios | Descripción |
|---|---|---|
| **G1 — Refactor estructural** | C10, C11, C12 | Nueva jerarquía Categoría→Marca→Modelo→Producto→Variante + TalleConfig |
| **G2 — Flujo de Venta** | C01, C02, C03, C04, C09 | Anotaciones, modal cliente, combos anidados, autofill pago, precios editables |
| **G3 — Flujo de Compra** | C05 | Combos anidados (reutiliza G2) |
| **G4 — Postventa** | C07 | Búsqueda rápida en Cambios/Devoluciones |
| **G5 — Roles y Stock** | C06, C08 | Rol Empleado + mejora visual de Stock |

### Nuevo modelo conceptual (post-refactor)
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

## 2. Lógica de distribución estándar (design system — herencia v1 + extensiones v2)

La lógica de distribución del sistema base se extiende con los siguientes patrones nuevos:

### Patrón: Selector de variante anidado (combos cascadeados)
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

### Patrón: Modal de alta rápida
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

## 3. Flujo de pantallas por módulo (delta v2)

### 3.1 Módulo Maestros — Marcas y Modelos (nuevo)

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

### 3.2 Módulo Productos (modificado)

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

### 3.3 Módulo Ventas (modificado — C01, C02, C03, C04, C09)

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

### 3.4 Módulo Compras (modificado — C05)

#### Pantalla: /Compras/Crear — /Compras/Editar (delta)
Reemplazar el Select2 de texto libre de variante por el selector anidado (mismo componente que Ventas).

```
│  ── Agregar Producto ────────────────────────────────────────────── │
│  [Categoría ▼] → [Marca ▼] → [Modelo ▼] → [Color ▼] → [Talle ▼]  │
│  Cantidad [__]   Costo unit. [________]    [ + Agregar ]            │
```

---

### 3.5 Módulo Devoluciones (modificado — C07)

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

### 3.6 Módulo Stock (modificado — C06, C08)

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

## 4. ViewModels propuestos — delta v2

### 4.1 Nuevos (G1 — Refactor estructural)

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

### 4.2 Modificados

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

### 4.3 Nuevos (G2 — Flujo de Venta)

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

### 4.4 Nuevos (G4 — Devoluciones)

#### `BuscarVentaRequest` (búsqueda multi-criterio C07)
| Campo | Tipo | Validación |
|---|---|---|
| FechaDesde | DateTime? | Opcional |
| FechaHasta | DateTime? | Opcional |
| ClienteId | int? | Opcional |
| TextoProducto | string? | MaxLength(100), búsqueda parcial |

---

## 5. Contratos funcionales por servicio (delta v2)

### 5.1 `IMarcaService` (nuevo)
```
CrearAsync(MarcaViewModel vm) → ServiceResult<int>
EditarAsync(MarcaViewModel vm) → ServiceResult
InactivarAsync(int id) → ServiceResult      // Guarda: sin productos activos
ObtenerAsync(int id) → ServiceResult<MarcaViewModel>
ListarAsync(DataTableRequest) → DataTableResponse<MarcaViewModel>
ObtenerPorCategoriaAsync(int categoriaId) → List<MarcaViewModel>  // Para cascada AJAX
```

### 5.2 `IModeloService` (nuevo)
```
CrearAsync(ModeloViewModel vm) → ServiceResult<int>
EditarAsync(ModeloViewModel vm) → ServiceResult
InactivarAsync(int id) → ServiceResult      // Guarda: sin productos activos
ObtenerAsync(int id) → ServiceResult<ModeloViewModel>
ListarAsync(DataTableRequest, int? marcaId) → DataTableResponse<ModeloViewModel>
ObtenerPorMarcaAsync(int marcaId) → List<ModeloViewModel>  // Para cascada AJAX
```

### 5.3 `IVarianteService` (delta — métodos nuevos)
```
// Endpoints AJAX para combos anidados (C03/C05)
ObtenerColoresPorModeloAsync(int modeloId) → List<string>
ObtenerTallesPorModeloColorAsync(int modeloId, string? color) → List<TalleConfigViewModel>
ResolverVarianteAsync(VarianteSelectorRequest req) → ServiceResult<VarianteSelectorResponse>
```

### 5.4 `IClienteService` (delta — método nuevo)
```
CrearRapidoAsync(ClienteRapidoViewModel vm) → ServiceResult<ClienteViewModel>
// Crea con datos mínimos; resto de campos quedan null para completar después
// Política: RequireVendedor (no solo Admin)
```

### 5.5 `IVentaService` (delta — ajuste naming)
```
// Sin cambios de firma; internamente: Observaciones → Anotaciones
// VentaCreateViewModel.Anotaciones se mapea a Venta.Anotaciones
```

### 5.6 `IDevolucionService` (delta — método nuevo)
```
BuscarVentasParaDevolucionAsync(BuscarVentaRequest req) 
    → List<VentaListItemViewModel>
// Solo ventas en estado Confirmada o Entregada
// Filtra por fecha, clienteId, texto parcial de producto/variante
```

### 5.7 `IStockService` (sin cambios de firma)
```
// ListarAsync ya existente; se agrega filtro por MarcaId y ModeloId en DataTableRequest
// Internamente el service aplica los nuevos filtros
```

---

## 6. Máquina de estados — delta v2

### 6.1 Venta (extensión)

| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| (∅) | `CrearVenta` | Confirmada | (igual v1) + `Anotaciones` opcional max 1000 chars | (igual v1) | (igual v1) |
| Confirmada / Entregada | `IniciarDevolucion` | (mismo) | Estado Confirmada **o** Entregada (ampliado desde v1 que solo era Entregada) | Redirige a `/Devoluciones/Crear?ventaId=X` | "Solo ventas Confirmadas o Entregadas admiten devolución" |

### 6.2 Soft delete — entidades nuevas

| Origen | Evento | Entidad | Guarda | Acción | Error |
|---|---|---|---|---|---|
| Activo | `Inactivar` | Marca | Sin productos activos ni modelos activos | Setear `DeletedAt` | "Marca con productos o modelos activos" |
| Activo | `Inactivar` | Modelo | Sin productos activos | Setear `DeletedAt` | "Modelo con productos activos" |
| Activo | `Inactivar` | TalleConfig | Sin variantes activas que lo referencien | Setear `DeletedAt` | "Talle en uso por variantes activas" |

---

## 7. Reglas de negocio y permisos por módulo/acción — delta v2

### 7.1 Matriz de permisos ampliada (rol Empleado nuevo)

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

### 7.2 Policy nueva: `RequireEmpleado`
```
RequireEmpleado = SuperUsuario | Administrador | Vendedor | Empleado
```
Se aplica en los controllers de: `VentasController`, `DevolucionesController`, `StockController` (Index).  
Las acciones de ajuste/admin dentro de esos controllers mantienen `RequireAdministrador`.

### 7.3 Menú de navegación por rol
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

## 8. Impacto funcional por capa

### 8.1 Presentación (Web)

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

### 8.2 Negocio (Application)

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

### 8.3 Datos (Infrastructure)

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

## 9. Riesgos y supuestos

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

## 10. Plan funcional por etapas para el arquitecto (delta v2)

> Las etapas originales F0–F8 ya están implementadas. Este plan cubre exclusivamente el trabajo nuevo.

### Etapa V1-E1 — Refactor estructural del modelo (BLOQUEA TODO LO DEMÁS)
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

### Etapa V1-E2 — Combos anidados en Ventas y Compras
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

### Etapa V1-E3 — Modal cliente + Búsqueda rápida devoluciones
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

### Etapa V1-E4 — Rol Empleado + mejora visual Stock
**Objetivo:** Nuevo rol operativo + interfaz de stock mejorada.  
**Dependencia:** V1-E1 (para que los filtros de stock ya usen Marca/Modelo).  
**Entregables funcionales:**
- Rol Empleado en SeedData + policy RequireEmpleado en Program.cs.
- Menú de navegación dinámico por rol (Empleado ve solo Ventas, Dev/Cambios, Stock).
- Vista /Stock/Index rediseñada: filtros Categoría/Marca/Modelo/Color/Talle; indicadores visuales 🟢🟡🔴⚫; precios de costo ocultos para Empleado/Vendedor.
**Criterio cierre:** Un usuario con rol Empleado puede operar sin ver módulos no autorizados; stock muestra indicadores visuales.

### Dependencias entre etapas v2

```
V1-E1 (Refactor estructural)
  └─► V1-E2 (Combos anidados — requiere nueva jerarquía)
        └─► V1-E3 (Modal cliente + búsqueda devoluciones — comparte vistas E2)
  └─► V1-E4 (Rol Empleado — puede ejecutarse en paralelo con E2/E3)
```

---

## 11. Checklist de salida — Diseño funcional v2

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

## 12. Handoff a Arquitectura

### Paquete entregado
1. `1-analista-funcional.md` v2 (decisiones P1–P15 + C11a cerradas).
2. Este documento `2-disenador-funcional.md` v2.

### Preguntas abiertas para el arquitecto

1. **Renombrado de tabla `Subgrupos` → `Marcas`:** ¿Renombrar físicamente la tabla EF o mantener nombre de tabla legacy y cambiar solo el nombre de clase/relación?
2. **TalleId en VarianteProducto:** ¿FK estricta a TalleConfig o campo string? con validación en service? Recomendado: FK estricta para integridad.
3. **Colores:** Actualmente texto libre (`VarianteProducto.Color`). ¿Se convierte en entidad también o queda texto libre? El analista recomienda mantenerlo texto libre en v2 (no fue solicitado).
4. **Combos AJAX — cantidad de endpoints:** 3 endpoints propuestos (colores, talles, resolver). ¿Se consolidan en uno solo parametrizado o quedan separados?
5. **Policy RequireEmpleado vs RequireVendedor:** Evaluar si conviene hacer RequireEmpleado inclusivo (Admin+Vendedor+Empleado) o agregar Empleado al RequireVendedor existente. Impacto: si se agrega al RequireVendedor, un Empleado podría acceder a acciones que hoy son solo-Vendedor y no son adecuadas para Empleado. Recomendado: policy separada.
