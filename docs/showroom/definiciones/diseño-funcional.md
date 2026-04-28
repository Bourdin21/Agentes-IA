# Diseño Funcional
## Sistema de Gestión Comercial — Indumentaria y Calzado

**Cliente:** Ulises  
**Proveedor:** OlvidataSoft  
**Versión:** 1.0  
**Estado:** Diseño funcional verificado  
**Base:** Análisis funcional v1.0 aprobado  

---

## 1. Alcance Funcional Resumido

Diseñar los flujos de pantallas, ViewModels con validaciones, contratos de servicio y requerimientos de datos para los 9 módulos + Dashboard del sistema de gestión comercial de indumentaria y calzado, sobre la arquitectura Clean Architecture de 4 capas existente (MVC con Controllers/Views).

---

## 2. Flujo de Pantallas por Módulo

### MÓDULO 1 — Seguridad y Acceso
*(ya implementado en ShowroomGriffin base: AccountController, UsersController)*

**Cambios requeridos:**
- Agregar rol "Vendedor" al seed.
- Sidebar: ocultar ítems según rol.

---

### MÓDULO 2 — Maestros Comerciales

#### 2.1 Categorías

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Listado | `GET /Categorias` | Index — DataTable server-side | Admin |
| Crear | `GET /Categorias/Crear` | Formulario modal o inline | Admin |
| Crear (post) | `POST /Categorias/Crear` | Guarda + redirect | Admin |
| Editar | `GET /Categorias/Editar/{id}` | Formulario prellenado | Admin |
| Editar (post) | `POST /Categorias/Editar/{id}` | Guarda + redirect | Admin |
| Inactivar | `POST /Categorias/Inactivar/{id}` | Soft delete (SweetAlert confirm) | Admin |

#### 2.2 Subgrupos

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Listado | `GET /Subgrupos` | DataTable con columna Categoría | Admin |
| Crear | `GET /Subgrupos/Crear` | Formulario con Select2 de Categoría | Admin |
| Editar | `GET /Subgrupos/Editar/{id}` | Formulario prellenado | Admin |
| Inactivar | `POST /Subgrupos/Inactivar/{id}` | Soft delete | Admin |
| **AJAX** | `GET /api/Subgrupos/PorCategoria/{categoriaId}` | JSON para cascada en otros forms | Admin |

#### 2.3 Clientes

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Listado | `GET /Clientes` | DataTable server-side | Admin, Vendedor (solo lectura) |
| Crear | `GET /Clientes/Crear` | Formulario completo | Admin |
| Editar | `GET /Clientes/Editar/{id}` | Formulario prellenado | Admin |
| Inactivar | `POST /Clientes/Inactivar/{id}` | Soft delete | Admin |
| **AJAX** | `GET /api/Clientes/Buscar?term=` | Select2 remote para ventas | Admin, Vendedor |

#### 2.4 Proveedores

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Listado | `GET /Proveedores` | DataTable server-side | Admin |
| Crear/Editar/Inactivar | Idem patrón Categorías | — | Admin |
| **AJAX** | `GET /api/Proveedores/Buscar?term=` | Select2 remote para compras | Admin |

#### 2.5 Tipos de Precio Zapatilla

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Listado | `GET /TiposPrecio` | DataTable server-side | Admin |
| Crear/Editar/Inactivar | Idem patrón Categorías | — | Admin |

---

### MÓDULO 3 — Productos y Variantes

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Listado productos | `GET /Productos` | DataTable con filtros: categoría, subgrupo | Admin (full), Vendedor (sin costo) |
| Crear producto | `GET /Productos/Crear` | Form: nombre + categoría + subgrupo (Select2 cascada) | Admin |
| Editar producto | `GET /Productos/Editar/{id}` | Form prellenado | Admin |
| Detalle producto | `GET /Productos/Detalle/{id}` | Info + listado de variantes embebido | Admin, Vendedor |
| Crear variante | `GET /Productos/{prodId}/Variantes/Crear` | Form dinámico según categoría (ropa vs zapatilla) | Admin |
| Editar variante | `GET /Productos/{prodId}/Variantes/Editar/{id}` | Form prellenado | Admin |
| Inactivar variante | `POST /Productos/{prodId}/Variantes/Inactivar/{id}` | Valida stock = 0 | Admin |
| **AJAX** | `GET /api/Variantes/Buscar?term=` | Búsqueda por nombre/SKU/código barras para ventas y compras | Admin, Vendedor |
| **AJAX** | `GET /api/Variantes/{id}/Stock` | Stock actual para validación en tiempo real | Admin, Vendedor |

**Comportamiento dinámico del formulario de variante:**
- Si categoría del producto = Ropa → mostrar: Talle, Color, Marca, Género, Temporada
- Si categoría = Zapatillas → mostrar: Color, Marca, Número, Modelo, TipoPrecioZapatilla
- Se resuelve con un `data-tipo-producto` en el producto y JS condicional.

---

### MÓDULO 4 — Stock e Inventario

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Listado stock | `GET /Stock` | DataTable: variante, stock actual, mínimo, alerta visual | Admin, Vendedor |
| Alertas stock bajo | `GET /Stock?soloAlertas=true` | Filtro predefinido: `StockActual <= StockMinimo` | Admin, Vendedor |
| Carga inicial | `GET /Stock/CargaInicial` | Formulario: variante (Select2) + cantidad | Admin |
| Ajuste manual | `GET /Stock/Ajuste` | Formulario: variante + cantidad nueva + motivo opcional | Admin |
| Historial movimientos | `GET /Stock/Historial?varianteId=` | DataTable: tipo, cantidad, anterior, resultante, fecha, referencia | Admin, Vendedor |

---

### MÓDULO 5 — Compras a Proveedores

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Listado compras | `GET /Compras` | DataTable con filtros: proveedor, estado, rango fechas | Admin |
| Nueva compra | `GET /Compras/Crear` | Form: proveedor (Select2) + fecha + líneas dinámicas | Admin |
| Crear (post) | `POST /Compras/Crear` | Guarda en Borrador | Admin |
| Detalle compra | `GET /Compras/Detalle/{id}` | Info + líneas + adjuntos + botones de estado | Admin |
| Editar compra | `GET /Compras/Editar/{id}` | Solo si Borrador/EnProceso | Admin |
| Cambiar estado | `POST /Compras/CambiarEstado/{id}` | Avance lineal con SweetAlert confirm | Admin |
| **Recepcionar** | `GET /Compras/Recepcionar/{id}` | ⭐ Pantalla compleja — ver detalle abajo | Admin |
| Recepcionar (post) | `POST /Compras/Recepcionar/{id}` | Valida + impacta stock | Admin |
| Adjuntar | `POST /Compras/Adjuntar/{id}` | Upload archivo (imagen/PDF) | Admin |

**Pantalla de Recepción (compleja):**

```
┌──────────────────────────────────────────────────────────────────┐
│ RECEPCIÓN DE COMPRA #123 — Proveedor: XYZ                       │
│ Fecha recepción: [datepicker]                                    │
├──────────────────────────────────────────────────────────────────┤
│ Producto/Variante │ Pedida │ Recibida │ Dañada │ Devuelta │ OK  │
│ ─────────────────────────────────────────────────────────────── │
│ Remera Azul M     │   10   │ [input]  │ [input]│ [input]  │ [✓] │
│ Remera Azul L     │    5   │ [input]  │ [input]│ [input]  │ [✓] │
│ Zapatilla N42     │    8   │ [input]  │ [input]│ [input]  │ [✓] │
├──────────────────────────────────────────────────────────────────┤
│ Validación JS en tiempo real: Rec + Dañ + Dev <= Pedida          │
│                                                [Confirmar]       │
└──────────────────────────────────────────────────────────────────┘
```

---

### MÓDULO 6 — Ventas a Clientes ⭐ (más crítico)

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Listado ventas | `GET /Ventas` | DataTable con filtros: cliente, estado, fecha, vendedor | Admin, Vendedor |
| **Nueva venta** | `GET /Ventas/Crear` | ⭐ Pantalla compleja — ver detalle abajo | Admin, Vendedor |
| Crear (post) | `POST /Ventas/Crear` | Valida stock + pagos → confirma | Admin, Vendedor |
| Detalle venta | `GET /Ventas/Detalle/{id}` | Info + líneas + pagos + adjuntos + acciones | Admin, Vendedor |
| Anular | `POST /Ventas/Anular/{id}` | SweetAlert → repone stock | Admin, Vendedor |
| Marcar entregada | `POST /Ventas/Entregar/{id}` | Cambia estado | Admin, Vendedor |
| Remito PDF | `GET /Ventas/Remito/{id}` | Genera PDF con QuestPDF | Admin, Vendedor |
| Adjuntar | `POST /Ventas/Adjuntar/{id}` | Upload comprobante | Admin, Vendedor |

**Pantalla Nueva Venta (4 secciones, single-page):**

```
┌──────────────────────────────────────────────────────────────────┐
│ NUEVA VENTA                                                      │
├──────────────────────────────────────────────────────────────────┤
│ SECCIÓN 1 — CLIENTE (opcional)                                   │
│ [Select2 búsqueda remota] o "Sin cliente"                        │
├──────────────────────────────────────────────────────────────────┤
│ SECCIÓN 2 — CARRITO                                              │
│ Buscar producto: [Select2 búsqueda por nombre/SKU/barras]        │
│                                                                  │
│ Producto/Variante    │ Precio │ Cant │ Stock │ Subtotal │ [X]   │
│ ────────────────────────────────────────────────────────────────│
│ Remera Azul M        │ $5000  │ [2]  │  15   │ $10.000  │ [🗑]  │
│ Zapatilla N42 Blanca │ $45000 │ [1]  │   3   │ $45.000  │ [🗑]  │
│ ────────────────────────────────────────────────────────────────│
│                                           Subtotal: $55.000      │
│ Descuento: [__]%                          Descuento: -$0         │
│                                           TOTAL:     $55.000     │
├──────────────────────────────────────────────────────────────────┤
│ SECCIÓN 3 — MEDIOS DE PAGO                                       │
│ [+ Agregar pago]                                                 │
│                                                                  │
│ Medio      │ Importe  │ % Financ. │ [X]                         │
│ Efectivo   │ $30.000  │    —      │ [🗑]                         │
│ Cuotas     │ $25.000  │   15%     │ [🗑]                         │
│ ────────────────────────────────────────────────────────────────│
│ Total pagos: $55.000   Diferencia: $0.00 ✅                      │
├──────────────────────────────────────────────────────────────────┤
│ SECCIÓN 4 — CONFIRMACIÓN                                         │
│ Observaciones: [textarea]                                        │
│                                          [Confirmar Venta]       │
└──────────────────────────────────────────────────────────────────┘
```

**Interacciones AJAX en Nueva Venta:**
- `GET /api/Variantes/Buscar?term=` → Select2 remote
- `GET /api/Variantes/{id}/Stock` → validación stock en tiempo real
- `GET /api/Clientes/Buscar?term=` → Select2 remote
- Todo el carrito y pagos se gestionan en memoria JS (arrays) y se envían como JSON al POST.

---

### MÓDULO 7 — Devoluciones y Cambios

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Listado devoluciones | `GET /Devoluciones` | DataTable con filtros | Admin, Vendedor |
| **Nueva devolución** | `GET /Devoluciones/Crear` | ⭐ Wizard 4 pasos — ver abajo | Admin, Vendedor |
| Crear (post) | `POST /Devoluciones/Crear` | Valida + impacta stock | Admin, Vendedor |
| Detalle | `GET /Devoluciones/Detalle/{id}` | Info completa | Admin, Vendedor |

**Wizard de Nueva Devolución (4 pasos JS, single-page):**

```
Paso 1: Buscar venta original
 └─> [Buscar por nro VTA-XXXXX, cliente o fecha]
 └─> Sistema valida plazo de devolución
 └─> Muestra datos de la venta

Paso 2: Seleccionar ítems a devolver
 └─> Tabla con ítems de la venta
 └─> Columna "Disponible" = Vendida − Ya devuelta
 └─> Input cantidad a devolver (max = disponible)

Paso 3: Definir tipo de operación
 └─> Radio: Devolución dinero / Cambio mismo valor / Cambio mayor valor
 └─> Si Cambio → Select2 para buscar nueva variante
 └─> Si Cambio mayor valor → sistema muestra diferencia

Paso 4: Confirmar
 └─> Resumen de la operación
 └─> [Confirmar]
```

---

### MÓDULO 8 — Resumen Semanal

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Resumen | `GET /ResumenSemanal` | Vista con navegación semana anterior/siguiente | Admin |
| **AJAX** | `GET /api/ResumenSemanal?fecha=` | JSON con total, cantidad ops, detalle | Admin |

**Layout de la pantalla:**

```
┌──────────────────────────────────────────────────┐
│ ← Semana anterior    Lun 02/06 — Dom 08/06    → │
├──────────────────────────────────────────────────┤
│ Total cobrado por transferencia:    $1.250.000   │
│ Cantidad de operaciones:                    12   │
├──────────────────────────────────────────────────┤
│ Detalle (expandible):                            │
│ VTA-00045 │ 03/06 │ Cliente X │ $150.000        │
│ VTA-00047 │ 04/06 │ Sin cliente │ $80.000       │
│ ...                                              │
└──────────────────────────────────────────────────┘
```

---

### MÓDULO 9 — Aumento Masivo de Precios

| Pantalla | Ruta | Acción | Rol |
|---|---|---|---|
| Aumento masivo | `GET /AumentoMasivo` | Pantalla única | Admin |
| **AJAX** | `GET /api/AumentoMasivo/Variantes?categoriaId=&subgrupoId=` | Lista variantes para selección | Admin |
| Aplicar | `POST /AumentoMasivo/Aplicar` | SweetAlert confirm → ejecuta | Admin |

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│ AUMENTO MASIVO DE PRECIOS                                     │
├──────────────────────────────────────────────────────────────┤
│ Alcance: (●) Por categoría  (○) Por subgrupo  (○) Todos      │
│ Categoría: [Select2]    Subgrupo: [Select2 cascada]           │
│                                                               │
│ Aplicar sobre: (●) Precio de venta  (○) Precio de compra     │
│ Porcentaje: [___]%                                            │
│                                                [Cargar lista] │
├──────────────────────────────────────────────────────────────┤
│ [✓] Seleccionar todos                                         │
│ [✓] Remera Azul M — Actual: $5.000 → Nuevo: $5.500           │
│ [✓] Remera Azul L — Actual: $5.000 → Nuevo: $5.500           │
│ [ ] Zapatilla N42  — Actual: $45.000 → Nuevo: $49.500        │
│                                                               │
│                          [Aplicar aumento] (SweetAlert)       │
└──────────────────────────────────────────────────────────────┘
```

---

### MÓDULO HOME — Dashboard

| Widget | Datos | Rol |
|---|---|---|
| Resumen transferencias (semana actual) | Total + cantidad ops | Admin |
| Alertas stock bajo | Contador + enlace a `/Stock?soloAlertas=true` | Admin, Vendedor |
| Acceso rápido: Nueva Venta | Botón → `/Ventas/Crear` | Admin, Vendedor |
| Acceso rápido: Nueva Compra | Botón → `/Compras/Crear` | Admin |
| Acceso rápido: Productos | Botón → `/Productos` | Admin |

---

## 3. ViewModels con Validaciones (DataAnnotations es-AR)

### 3.1 Maestros

```
CategoriaViewModel
├── Id: int
├── [Required("El nombre es obligatorio")]
│   [MaxLength(100)] Nombre: string
└── [MaxLength(500)] Descripcion: string?

SubgrupoViewModel
├── Id: int
├── [Required("El nombre es obligatorio")]
│   [MaxLength(100)] Nombre: string
└── [Required("La categoría es obligatoria")]
    CategoriaId: int

ClienteViewModel
├── Id: int
├── [Required("El nombre es obligatorio")]
│   [MaxLength(200)] Nombre: string
├── [MaxLength(20)] Telefono: string?
├── [MaxLength(20)] WhatsApp: string?
├── [MaxLength(300)] Direccion: string?
└── [MaxLength(13)] Cuit: string?

ProveedorViewModel
├── Id: int
├── [Required("La razón social es obligatoria")]
│   [MaxLength(200)] RazonSocial: string
├── [MaxLength(20)] Telefono: string?
├── [EmailAddress] [MaxLength(200)] Email: string?
└── [MaxLength(13)] Cuit: string?

TipoPrecioZapatillaViewModel
├── Id: int
├── [Required("El nombre es obligatorio")]
│   [MaxLength(100)] Nombre: string
└── [Required("El margen es obligatorio")]
    [Range(0, 999.99)] MargenGanancia: decimal
```

### 3.2 Productos y Variantes

```
ProductoViewModel
├── Id: int
├── [Required] [MaxLength(200)] Nombre: string
├── [Required("La categoría es obligatoria")] CategoriaId: int
├── SubgrupoId: int?
├── CategoríaNombre: string           // display
├── SubgrupoNombre: string?           // display
└── CantidadVariantes: int            // display

VarianteViewModel
├── Id: int
├── ProductoId: int
├── [Required] [Range(0.01, double.MaxValue, "El precio debe ser mayor a 0")]
│   PrecioVenta: decimal
├── [Required] [Range(0, int.MaxValue)] StockMinimo: int
├── [MaxLength(50)] CodigoInterno: string?
├── [MaxLength(50)] Sku: string?
├── [MaxLength(50)] CodigoBarra: string?
│
│   // --- Atributos Ropa ---
├── [MaxLength(20)] Talle: string?
├── [MaxLength(50)] Color: string?
├── [MaxLength(100)] Marca: string?
├── [MaxLength(20)] Genero: string?
├── [MaxLength(50)] Temporada: string?
│
│   // --- Atributos Zapatillas ---
├── [MaxLength(10)] Numero: string?
├── [MaxLength(100)] Modelo: string?
├── TipoPrecioZapatillaId: int?
│
│   // --- Display (solo lectura) ---
├── StockActual: int
├── UltimoPrecioCompra: decimal?       // solo Admin
└── Ganancia: decimal?                 // solo Admin
```

### 3.3 Stock

```
StockListItemViewModel
├── VarianteId: int
├── ProductoNombre: string
├── VarianteDescripcion: string       // "Talle M - Azul" o "N42 - Blanco"
├── StockActual: int
├── StockMinimo: int
└── EnAlerta: bool                    // StockActual <= StockMinimo

AjusteStockViewModel
├── [Required] VarianteId: int
├── [Required] [Range(0, int.MaxValue)] CantidadNueva: int
└── [MaxLength(500)] Motivo: string?

MovimientoStockListItemViewModel
├── Fecha: DateTime
├── TipoMovimiento: string           // enum display
├── Cantidad: int
├── StockAnterior: int
├── StockResultante: int
└── Referencia: string                // "VTA-00001", "Compra #5", etc.
```

### 3.4 Compras

```
CompraCreateViewModel
├── [Required("El proveedor es obligatorio")] ProveedorId: int
├── [Required("La fecha es obligatoria")] FechaCompra: DateTime
├── Observaciones: string?
└── Detalles: List<CompraDetalleItemViewModel>

CompraDetalleItemViewModel
├── [Required] VarianteId: int
├── [Required] [Range(1, int.MaxValue)] Cantidad: int
└── [Required] [Range(0.01, double.MaxValue)] CostoUnitario: decimal

CompraRecepcionViewModel
├── CompraId: int
├── [Required("La fecha de recepción es obligatoria")] FechaRecepcion: DateTime
└── Lineas: List<CompraRecepcionLineaViewModel>

CompraRecepcionLineaViewModel
├── CompraDetalleId: int
├── VarianteDescripcion: string       // display
├── CantidadPedida: int               // display
├── [Range(0, int.MaxValue)] CantidadRecibida: int
├── [Range(0, int.MaxValue)] CantidadDanada: int
└── [Range(0, int.MaxValue)] CantidadDevueltaProveedor: int
    // Validación custom: Recibida + Dañada + Devuelta <= Pedida
```

### 3.5 Ventas ⭐

```
VentaCreateViewModel
├── ClienteId: int?                   // opcional
├── [Range(0, 100)] DescuentoPorcentaje: decimal
├── Observaciones: string?
├── Detalles: List<VentaDetalleItemViewModel>
└── Pagos: List<VentaPagoItemViewModel>

VentaDetalleItemViewModel
├── [Required] VarianteId: int
├── [Required] [Range(1, int.MaxValue)] Cantidad: int
└── PrecioUnitario: decimal           // se toma del maestro al confirmar

VentaPagoItemViewModel
├── [Required] MedioPago: MedioPago   // enum
├── [Required] [Range(0.01, double.MaxValue)] Importe: decimal
└── [Range(0, 100)] PorcentajeFinanciamiento: decimal?  // solo si Cuotas

VentaDetalleViewModel                 // para pantalla Detalle (lectura)
├── NroVenta: string                  // VTA-00001
├── Fecha: DateTime
├── ClienteNombre: string?
├── VendedorNombre: string
├── Estado: EstadoVenta
├── Subtotal: decimal
├── DescuentoPorcentaje: decimal
├── DescuentoMonto: decimal
├── Total: decimal
├── Observaciones: string?
├── Detalles: List<VentaDetalleLineaViewModel>
├── Pagos: List<VentaPagoLineaViewModel>
├── Adjuntos: List<AdjuntoViewModel>
├── PuedeAnular: bool
├── PuedeEntregar: bool
├── PuedeEmitirRemito: bool
├── CostoTotal: decimal?              // SOLO Admin
└── GananciaTotal: decimal?           // SOLO Admin
```

### 3.6 Devoluciones

```
DevolucionCreateViewModel
├── [Required] VentaId: int
├── [Required] TipoOperacion: TipoDevolucion  // enum
├── Items: List<DevolucionItemViewModel>
├── NuevaVarianteId: int?             // si es cambio
└── DiferenciaCobrar: decimal?        // si cambio mayor valor

DevolucionItemViewModel
├── VentaDetalleId: int
├── VarianteDescripcion: string       // display
├── CantidadDisponible: int           // display: vendida − ya devuelta
└── [Range(1, int.MaxValue)] CantidadDevolver: int
    // Validación custom: CantidadDevolver <= CantidadDisponible
```

### 3.7 Resumen Semanal

```
ResumenSemanalViewModel
├── FechaDesde: DateTime              // lunes
├── FechaHasta: DateTime              // domingo
├── TotalCobrado: decimal
├── CantidadOperaciones: int
└── Detalle: List<ResumenSemanalDetalleViewModel>

ResumenSemanalDetalleViewModel
├── NroVenta: string
├── Fecha: DateTime
├── ClienteNombre: string?
└── ImporteTransferencia: decimal
```

### 3.8 Aumento Masivo

```
AumentoMasivoViewModel
├── Alcance: AlcanceAumento           // enum: PorCategoria, PorSubgrupo, Todos
├── CategoriaId: int?
├── SubgrupoId: int?
├── [Required] [Range(0.01, double.MaxValue)] Porcentaje: decimal
├── [Required] AplicarSobre: BaseAumento  // enum: PrecioVenta, PrecioCompra
└── VariantesExcluidas: List<int>     // IDs a excluir

AumentoMasivoPreviewItemViewModel
├── VarianteId: int
├── Descripcion: string
├── PrecioActual: decimal
├── PrecioNuevo: decimal
└── Seleccionado: bool
```

---

## 4. Contratos de Servicio (Application Layer)

Todos retornan `ServiceResult` o `ServiceResult<T>`. Ubicación: `ShowroomGriffin.Application/Interfaces/`.

### 4.1 ICategoriaService

```
Task<ServiceResult<int>> CrearAsync(CategoriaViewModel vm)
Task<ServiceResult> EditarAsync(CategoriaViewModel vm)
Task<ServiceResult> InactivarAsync(int id)
Task<ServiceResult<CategoriaViewModel>> ObtenerAsync(int id)
Task<DataTableResponse<CategoriaViewModel>> ListarAsync(DataTableRequest request)
```

### 4.2 ISubgrupoService

```
Task<ServiceResult<int>> CrearAsync(SubgrupoViewModel vm)
Task<ServiceResult> EditarAsync(SubgrupoViewModel vm)
Task<ServiceResult> InactivarAsync(int id)
Task<ServiceResult<SubgrupoViewModel>> ObtenerAsync(int id)
Task<DataTableResponse<SubgrupoViewModel>> ListarAsync(DataTableRequest request)
Task<List<SubgrupoViewModel>> ObtenerPorCategoriaAsync(int categoriaId)
```

### 4.3 IClienteService

```
Task<ServiceResult<int>> CrearAsync(ClienteViewModel vm)
Task<ServiceResult> EditarAsync(ClienteViewModel vm)
Task<ServiceResult> InactivarAsync(int id)
Task<ServiceResult<ClienteViewModel>> ObtenerAsync(int id)
Task<DataTableResponse<ClienteViewModel>> ListarAsync(DataTableRequest request)
Task<List<ClienteViewModel>> BuscarAsync(string term)   // Select2
```

### 4.4 IProveedorService

```
Task<ServiceResult<int>> CrearAsync(ProveedorViewModel vm)
Task<ServiceResult> EditarAsync(ProveedorViewModel vm)
Task<ServiceResult> InactivarAsync(int id)
Task<ServiceResult<ProveedorViewModel>> ObtenerAsync(int id)
Task<DataTableResponse<ProveedorViewModel>> ListarAsync(DataTableRequest request)
Task<List<ProveedorViewModel>> BuscarAsync(string term)
```

### 4.5 ITipoPrecioZapatillaService

```
Task<ServiceResult<int>> CrearAsync(TipoPrecioZapatillaViewModel vm)
Task<ServiceResult> EditarAsync(TipoPrecioZapatillaViewModel vm)
Task<ServiceResult> InactivarAsync(int id)
Task<DataTableResponse<TipoPrecioZapatillaViewModel>> ListarAsync(DataTableRequest request)
```

### 4.6 IProductoService

```
Task<ServiceResult<int>> CrearAsync(ProductoViewModel vm)
Task<ServiceResult> EditarAsync(ProductoViewModel vm)
Task<ServiceResult> InactivarAsync(int id)
Task<ServiceResult<ProductoViewModel>> ObtenerAsync(int id)
Task<DataTableResponse<ProductoViewModel>> ListarAsync(DataTableRequest request)
```

### 4.7 IVarianteService

```
Task<ServiceResult<int>> CrearAsync(VarianteViewModel vm)
Task<ServiceResult> EditarAsync(VarianteViewModel vm)
Task<ServiceResult> InactivarAsync(int id)
Task<ServiceResult<VarianteViewModel>> ObtenerAsync(int id)
Task<List<VarianteViewModel>> ObtenerPorProductoAsync(int productoId)
Task<List<VarianteViewModel>> BuscarAsync(string term)    // Select2
Task<ServiceResult<int>> ObtenerStockAsync(int varianteId)
```

### 4.8 IStockService

```
Task<DataTableResponse<StockListItemViewModel>> ListarAsync(DataTableRequest request, bool soloAlertas)
Task<ServiceResult> CargaInicialAsync(int varianteId, int cantidad)
Task<ServiceResult> AjusteManualAsync(AjusteStockViewModel vm)
Task<DataTableResponse<MovimientoStockListItemViewModel>> HistorialAsync(DataTableRequest request, int? varianteId)
// Métodos internos (llamados por otros services, no por Controller):
Task RegistrarMovimientoAsync(int varianteId, TipoMovimiento tipo, int cantidad, int? compraId, int? ventaId, int? devolucionId, int? ajusteId)
```

### 4.9 ICompraService

```
Task<ServiceResult<int>> CrearAsync(CompraCreateViewModel vm)
Task<ServiceResult> EditarAsync(int id, CompraCreateViewModel vm)
Task<ServiceResult> CambiarEstadoAsync(int id, EstadoCompra nuevoEstado)
Task<ServiceResult> RecepcionarAsync(CompraRecepcionViewModel vm)
Task<ServiceResult<CompraDetalleViewModel>> ObtenerAsync(int id)
Task<DataTableResponse<CompraListItemViewModel>> ListarAsync(DataTableRequest request)
Task<ServiceResult> AdjuntarAsync(int id, IFormFile archivo)
```

### 4.10 IVentaService ⭐

```
Task<ServiceResult<int>> CrearAsync(VentaCreateViewModel vm, string vendedorUserId)
Task<ServiceResult> AnularAsync(int id)
Task<ServiceResult> MarcarEntregadaAsync(int id)
Task<ServiceResult<VentaDetalleViewModel>> ObtenerAsync(int id, bool incluirCostos)
Task<DataTableResponse<VentaListItemViewModel>> ListarAsync(DataTableRequest request)
Task<ServiceResult> AdjuntarAsync(int id, IFormFile archivo)
```

### 4.11 IRemitoService

```
Task<ServiceResult<byte[]>> GenerarPdfAsync(int ventaId)
```

### 4.12 IDevolucionService

```
Task<ServiceResult<int>> CrearAsync(DevolucionCreateViewModel vm)
Task<ServiceResult<DevolucionDetalleViewModel>> ObtenerAsync(int id)
Task<DataTableResponse<DevolucionListItemViewModel>> ListarAsync(DataTableRequest request)
Task<ServiceResult<VentaParaDevolucionViewModel>> ObtenerVentaParaDevolucionAsync(int ventaId)
// Retorna ítems con cantidad disponible (vendida − ya devuelta)
```

### 4.13 IResumenSemanalService

```
Task<ServiceResult<ResumenSemanalViewModel>> ObtenerAsync(DateTime fechaReferencia)
```

### 4.14 IAumentoMasivoService

```
Task<List<AumentoMasivoPreviewItemViewModel>> ObtenerVariantesAsync(int? categoriaId, int? subgrupoId)
Task<ServiceResult<int>> AplicarAsync(AumentoMasivoViewModel vm)
// Retorna cantidad de variantes actualizadas
```

---

## 5. Requerimientos de Datos por Pantalla

| Pantalla | Datos requeridos |
|---|---|
| Dashboard | Stock en alerta (count), total transferencias semana actual, cantidad ops |
| Listado Productos | Producto + categoría nombre + cantidad variantes (JOIN) |
| Detalle Producto | Producto + variantes con stock actual (JOIN variante ↔ stock) |
| Nueva Venta | Clientes (AJAX), Variantes con stock (AJAX), precios vigentes |
| Detalle Venta | Venta + detalles + pagos + adjuntos + remito + datos vendedor + cliente |
| Detalle Venta (Admin) | Idem + UltimoPrecioCompra por línea + ganancia calculada |
| Recepción Compra | Compra + detalles con CantidadPedida + variante descripción |
| Nueva Devolución Paso 1 | Búsqueda de venta + validación plazo |
| Nueva Devolución Paso 2 | VentaDetalles con CantidadVendida − SUM(CantidadYaDevuelta) |
| Resumen Semanal | VentaPago WHERE MedioPago = Transferencia AND estado IN (Confirmada, Entregada) GROUP BY semana |
| Aumento Masivo | Variantes con PrecioVenta y UltimoPrecioCompra, filtradas por categoría/subgrupo |

---

## 6. Enums Requeridos

```
EstadoCompra      = Borrador(1), EnProceso(2), Verificada(3), Recibida(4)
EstadoVenta       = Confirmada(1), Entregada(2), Anulada(3)
MedioPago         = Efectivo(1), Tarjeta(2), Cuotas(3), Transferencia(4)
TipoMovimiento    = CargaInicial(1), Venta(2), AnulacionVenta(3), CompraRecepcion(4),
                     DevolucionCliente(5), AjusteManual(6), DevolucionProveedor(7)
TipoDevolucion    = DevolucionDinero(1), CambioMismoValor(2), CambioMayorValor(3)
AlcanceAumento    = PorCategoria(1), PorSubgrupo(2), Todos(3)
BaseAumento       = PrecioVenta(1), PrecioCompra(2)
```

---

## 7. Endpoints AJAX Consolidados

| Endpoint | Método | Uso | Rol |
|---|---|---|---|
| `/api/Subgrupos/PorCategoria/{id}` | GET | Cascada subgrupos | Admin |
| `/api/Clientes/Buscar?term=` | GET | Select2 en ventas | Admin, Vendedor |
| `/api/Proveedores/Buscar?term=` | GET | Select2 en compras | Admin |
| `/api/Variantes/Buscar?term=` | GET | Select2 en ventas/compras | Admin, Vendedor |
| `/api/Variantes/{id}/Stock` | GET | Validación stock en tiempo real | Admin, Vendedor |
| `/api/ResumenSemanal?fecha=` | GET | Navegación semanal | Admin |
| `/api/AumentoMasivo/Variantes?catId=&subId=` | GET | Lista para selección | Admin |

---

## 8. Impacto Técnico por Capa

### Presentación (Web)

- **11 Controllers** nuevos (Categorias, Subgrupos, Clientes, Proveedores, TiposPrecio, Productos, Stock, Compras, Ventas, Devoluciones, AumentoMasivo) + modificación de HomeController.
- **~35 ViewModels** en `Models/`.
- **~30 Views** (.cshtml) + partials para líneas dinámicas.
- **JS complejo**: Nueva Venta (carrito AJAX + pagos dinámicos), Recepción Compra (validación por línea), Wizard Devolución (4 pasos).
- **Sidebar update**: visibilidad por rol con `User.IsInRole()`.
- **Autorización**: `[Authorize(Policy = "RequireAdministrador")]` en controllers de compras, ajustes, aumentos, maestros (excepto clientes lectura).

### Negocio (Application)

- **14 interfaces** de servicio (§4).
- **0 lógica en Controllers**: cada acción delega a un service que retorna `ServiceResult<T>`.
- **Validaciones cruzadas** en services: stock suficiente (venta), suma pagos = total (venta), cantidades recepción (compra), plazo devolución, cantidad disponible devolución.
- **Transaccionalidad**: `IVentaService.CrearAsync` y `ICompraService.RecepcionarAsync` requieren transacción explícita (descuento stock + movimientos + actualización precios en un solo commit).

### Datos (Infrastructure)

- **14 services** implementados en `Services/`.
- **20 DbSets** nuevos en AppDbContext.
- **20 IEntityTypeConfiguration** en `Data/Configurations/`.
- **Índices de performance**: FechaVenta, MedioPago, SKU, CodigoBarra, VarianteId en MovimientoStock.
- **6 migraciones** incrementales (M1: maestros, M2: productos+variantes, M3: stock, M4: compras, M5: ventas, M6: devoluciones).
- `ApplyConfigurationsFromAssembly` en `OnModelCreating` para cargar configs automáticamente.

### Dependencias entre servicios

```
IVentaService → IStockService (decrementar/reponer stock)
ICompraService → IStockService (registrar recepción)
IDevolucionService → IStockService (reingresar/decrementar stock)
IAumentoMasivoService → IRepository<VarianteProducto> (batch update)
IRemitoService → IVentaService (obtener datos venta)
IResumenSemanalService → (query directo a VentaPago)
```

---

## 9. Riesgos y Supuestos

| # | Tipo | Descripción | Mitigación |
|---|---|---|---|
| R1 | Riesgo | Concurrencia en stock (2 vendedores simultáneos) | Transacción serializable en `CrearVentaAsync` |
| R2 | Riesgo | Carrito en memoria JS se pierde si el navegador se cierra | Aceptado en v1; no se persiste borrador de venta |
| R3 | Riesgo | Adjuntos en disco local sin backup | Almacenar en `wwwroot/uploads/` con nombre GUID; migrar a blob storage en v2 |
| R4 | Riesgo | Wizard devolución con estado en JS | Validación server-side completa al POST; JS es solo UX |
| S1 | Supuesto | El proyecto sigue MVC (Controllers/Views) según instrucciones, no Razor Pages | Confirmado por estructura existente |
| S2 | Supuesto | `ServiceResult<T>` existente cubre todos los casos de retorno | Verificado en codebase |
| S3 | Supuesto | DataTables server-side ya tiene patrón implementado (`DataTableRequest/Response`) | Verificado en codebase |

---

## 10. Pruebas Mínimas Requeridas

### Integración (por service)

- [ ] `IVentaService.CrearAsync` → stock decrementado + movimientos generados + nro correlativo.
- [ ] `IVentaService.CrearAsync` con stock insuficiente → `ServiceResult.Failure`.
- [ ] `IVentaService.CrearAsync` con suma pagos ≠ total → `ServiceResult.Failure`.
- [ ] `ICompraService.RecepcionarAsync` → stock solo de recibidas + UltimoPrecioCompra actualizado.
- [ ] `ICompraService.RecepcionarAsync` con Rec+Dañ+Dev > Pedida → `ServiceResult.Failure`.
- [ ] `IDevolucionService.CrearAsync` → stock reingresado + validación cantidad disponible.
- [ ] `IAumentoMasivoService.AplicarAsync` → precios actualizados excluyendo variantes excluidas.
- [ ] `IResumenSemanalService.ObtenerAsync` → solo transferencias de ventas Confirmada/Entregada.

### Autorización

- [ ] Vendedor → 403 en `/Compras`, `/Stock/Ajuste`, `/AumentoMasivo`, `/ResumenSemanal`.
- [ ] Vendedor → no recibe `UltimoPrecioCompra` ni `Ganancia` en ningún endpoint.

### UI/Funcional

- [ ] Nueva Venta: agregar/quitar productos del carrito, validación stock JS.
- [ ] Nueva Venta: agregar múltiples medios de pago, validación suma = total.
- [ ] Recepción: validación JS por línea Rec+Dañ+Dev <= Pedida.
- [ ] Wizard Devolución: los 4 pasos completan sin errores.

---

## 11. Checklist de Salida para Merge

```
DISEÑO FUNCIONAL — CHECKLIST DE SALIDA
────────────────────────────────────────────────────────────────────────
PANTALLAS
[ ] Todas las pantallas identificadas con ruta y rol
[ ] Pantallas complejas detalladas (Nueva Venta, Recepción, Wizard Devolución)
[ ] Endpoints AJAX documentados

VIEWMODELS
[ ] Un ViewModel por pantalla/acción
[ ] DataAnnotations en español (es-AR)
[ ] Validaciones cruzadas documentadas (custom validation)
[ ] Datos sensibles (costos/ganancias) condicionados a rol

CONTRATOS DE SERVICIO
[ ] Una interfaz por módulo funcional
[ ] Todos los métodos retornan ServiceResult o ServiceResult<T>
[ ] Validaciones de negocio delegadas a Services, no a Controllers
[ ] Dependencias entre services documentadas

DATOS
[ ] Requerimientos de datos por pantalla documentados
[ ] JOINs y queries complejas identificadas
[ ] Índices de performance definidos

SEPARACIÓN DE CAPAS
[ ] Controllers solo: recibir request → llamar service → retornar view/json
[ ] Services: toda lógica de negocio y validación
[ ] ViewModels: no exponen entidades de dominio directamente
[ ] Enums en Domain, interfaces en Application, implementaciones en Infrastructure
────────────────────────────────────────────────────────────────────────
```
