# Arquitectura del Sistema
## Sistema de Gestión Comercial — Indumentaria y Calzado

**Cliente:** Ulises  
**Proveedor:** OlvidataSoft  
**Versión:** 1.0  
**Estado:** Arquitectura definida  
**Base:** Análisis funcional v1.0 + Diseño funcional v1.0  

---

## 1. Alcance Funcional Resumido

Definir entidades de dominio, configuraciones EF Core, DbSets, plan de migraciones, políticas de autorización y registros de DI para soportar los 9 módulos del sistema de gestión comercial, sobre la arquitectura Clean Architecture de 4 capas existente.

**Requiere migración EF:** Sí — 6 migraciones incrementales (M1–M6).

---

## 2. Stack Tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Runtime | .NET | 10 |
| Web Framework | ASP.NET Core MVC | 10 |
| ORM | Entity Framework Core | 10 |
| Base de datos | MySQL | 8 |
| Provider EF | MySql.EntityFrameworkCore | 10.0.1 |
| Identidad | ASP.NET Core Identity | 10 |
| PDF | QuestPDF | Community License |
| Excel | ClosedXML | Última estable |
| Frontend | Bootstrap 5 + jQuery + DataTables 1.13.8 + Select2 + SweetAlert2 | — |
| Logging | Serilog | Última estable |
| Email | MailKit (SMTP) | Última estable |
| Cultura | es-AR (fija) | — |

---

## 3. Entidades de Dominio

### 3.1 Enums

Ubicación: `ShowroomGriffin.Domain/Enums/`

```
EstadoCompra.cs
├── Borrador = 1
├── EnProceso = 2
├── Verificada = 3
└── Recibida = 4

EstadoVenta.cs
├── Confirmada = 1
├── Entregada = 2
└── Anulada = 3

MedioPago.cs
├── Efectivo = 1
├── Tarjeta = 2
├── Cuotas = 3
└── Transferencia = 4

TipoMovimiento.cs
├── CargaInicial = 1
├── Venta = 2
├── AnulacionVenta = 3
├── CompraRecepcion = 4
├── DevolucionCliente = 5
├── AjusteManual = 6
└── DevolucionProveedor = 7

TipoDevolucion.cs
├── DevolucionDinero = 1
├── CambioMismoValor = 2
└── CambioMayorValor = 3
```

### 3.2 Entidades

Todas heredan de `SoftDestroyable` (Id, CreatedAt, CreatedByUserId, UpdatedAt, UpdatedByUserId, DeletedAt, DeletedByUserId).

Ubicación: `ShowroomGriffin.Domain/Entities/` organizadas por carpetas de módulo.

#### Maestros (`Entities/Maestros/`)

```csharp
Categoria
├── Nombre: string (max 100, required, unique)
└── Descripcion: string? (max 500)
    // Nav: ICollection<Subgrupo>, ICollection<Producto>

Subgrupo
├── Nombre: string (max 100, required)
├── CategoriaId: int (FK → Categoria)
└── Categoria: Categoria (nav)
    // Nav: ICollection<Producto>

Cliente
├── Nombre: string (max 200, required)
├── Telefono: string? (max 20)
├── WhatsApp: string? (max 20)
├── Direccion: string? (max 300)
└── Cuit: string? (max 13)
    // Nav: ICollection<Venta>

Proveedor
├── RazonSocial: string (max 200, required)
├── Telefono: string? (max 20)
├── Email: string? (max 200)
└── Cuit: string? (max 13)
    // Nav: ICollection<Compra>

TipoPrecioZapatilla
├── Nombre: string (max 100, required)
└── MargenGanancia: decimal (precision 5,2)
    // Nav: ICollection<VarianteProducto>
```

#### Productos (`Entities/Productos/`)

```csharp
Producto
├── Nombre: string (max 200, required)
├── CategoriaId: int (FK → Categoria)
├── SubgrupoId: int? (FK → Subgrupo)
├── Categoria: Categoria (nav)
└── Subgrupo: Subgrupo? (nav)
    // Nav: ICollection<VarianteProducto>

VarianteProducto
├── ProductoId: int (FK → Producto)
├── PrecioVenta: decimal (precision 18,2)
├── UltimoPrecioCompra: decimal? (precision 18,2)
├── StockMinimo: int (default 0)
├── CodigoInterno: string? (max 50)
├── Sku: string? (max 50, unique when not null)
├── CodigoBarra: string? (max 50, unique when not null)
│
│   // Atributos Ropa
├── Talle: string? (max 20)
├── Color: string? (max 50)
├── Marca: string? (max 100)
├── Genero: string? (max 20)
├── Temporada: string? (max 50)
│
│   // Atributos Zapatillas
├── Numero: string? (max 10)
├── Modelo: string? (max 100)
├── TipoPrecioZapatillaId: int? (FK → TipoPrecioZapatilla)
│
├── Producto: Producto (nav)
├── TipoPrecioZapatilla: TipoPrecioZapatilla? (nav)
└── Stock: Stock (nav 1:1)
    // Nav: ICollection<CompraDetalle>, ICollection<VentaDetalle>
```

#### Stock (`Entities/Stock/`)

```csharp
Stock
├── VarianteProductoId: int (FK → VarianteProducto, unique)
├── StockActual: int (default 0)
└── VarianteProducto: VarianteProducto (nav 1:1)

MovimientoStock
├── VarianteProductoId: int (FK → VarianteProducto)
├── TipoMovimiento: TipoMovimiento (enum → int)
├── Cantidad: int
├── StockAnterior: int
├── StockResultante: int
├── Referencia: string? (max 100)
│
│   // FKs polimórficas (solo una poblada por movimiento)
├── CompraId: int? (FK → Compra)
├── VentaId: int? (FK → Venta)
├── DevolucionCambioId: int? (FK → DevolucionCambio)
├── AjusteStockId: int? (FK → AjusteStock)
│
└── VarianteProducto: VarianteProducto (nav)

AjusteStock
├── VarianteProductoId: int (FK → VarianteProducto)
├── CantidadAnterior: int
├── CantidadNueva: int
├── Motivo: string? (max 500)
├── UsuarioId: string (FK → ApplicationUser)
└── VarianteProducto: VarianteProducto (nav)
```

#### Compras (`Entities/Compras/`)

```csharp
Compra
├── ProveedorId: int (FK → Proveedor)
├── FechaCompra: DateTime
├── FechaRecepcion: DateTime?
├── Estado: EstadoCompra (enum → int, default Borrador)
├── Observaciones: string? (max 1000)
├── Proveedor: Proveedor (nav)
├── Detalles: ICollection<CompraDetalle> (nav)
└── Adjuntos: ICollection<CompraAdjunto> (nav)

CompraDetalle
├── CompraId: int (FK → Compra)
├── VarianteProductoId: int (FK → VarianteProducto)
├── Cantidad: int
├── CostoUnitario: decimal (precision 18,2)
├── CantidadRecibida: int (default 0)
├── CantidadDanada: int (default 0)
├── CantidadDevueltaProveedor: int (default 0)
├── Compra: Compra (nav)
└── VarianteProducto: VarianteProducto (nav)

CompraAdjunto
├── CompraId: int (FK → Compra)
├── NombreArchivo: string (max 200, required)
├── RutaArchivo: string (max 500, required)
├── ContentType: string (max 100, required)
├── Tamanio: long
└── Compra: Compra (nav)
```

#### Ventas (`Entities/Ventas/`)

```csharp
Venta
├── NroVenta: string (max 20, unique, required)  // VTA-00001
├── ClienteId: int? (FK → Cliente, nullable)
├── VendedorUserId: string (FK → ApplicationUser)
├── FechaVenta: DateTime
├── Subtotal: decimal (precision 18,2)
├── DescuentoPorcentaje: decimal (precision 5,2, default 0)
├── DescuentoMonto: decimal (precision 18,2, default 0)
├── Total: decimal (precision 18,2)
├── Estado: EstadoVenta (enum → int, default Confirmada)
├── Observaciones: string? (max 1000)
├── Cliente: Cliente? (nav)
├── Detalles: ICollection<VentaDetalle> (nav)
├── Pagos: ICollection<VentaPago> (nav)
├── Adjuntos: ICollection<VentaAdjunto> (nav)
└── Remito: Remito? (nav 1:1)

VentaDetalle
├── VentaId: int (FK → Venta)
├── VarianteProductoId: int (FK → VarianteProducto)
├── Cantidad: int
├── PrecioUnitario: decimal (precision 18,2)
├── Subtotal: decimal (precision 18,2)
├── Venta: Venta (nav)
└── VarianteProducto: VarianteProducto (nav)

VentaPago
├── VentaId: int (FK → Venta)
├── MedioPago: MedioPago (enum → int)
├── Importe: decimal (precision 18,2)
├── PorcentajeFinanciamiento: decimal? (precision 5,2)
└── Venta: Venta (nav)

VentaAdjunto
├── VentaId: int (FK → Venta)
├── NombreArchivo: string (max 200, required)
├── RutaArchivo: string (max 500, required)
├── ContentType: string (max 100, required)
├── Tamanio: long
└── Venta: Venta (nav)

Remito
├── VentaId: int (FK → Venta, unique)
├── FechaEmision: DateTime
├── RutaPdf: string? (max 500)
└── Venta: Venta (nav 1:1)
```

#### Postventa (`Entities/Postventa/`)

```csharp
DevolucionCambio
├── VentaId: int (FK → Venta)
├── Fecha: DateTime
├── TipoOperacion: TipoDevolucion (enum → int)
├── NuevaVarianteProductoId: int? (FK → VarianteProducto)
├── DiferenciaCobrar: decimal? (precision 18,2)
├── Observaciones: string? (max 1000)
├── Venta: Venta (nav)
├── NuevaVarianteProducto: VarianteProducto? (nav)
└── Detalles: ICollection<DevolucionCambioDetalle> (nav)

DevolucionCambioDetalle
├── DevolucionCambioId: int (FK → DevolucionCambio)
├── VentaDetalleId: int (FK → VentaDetalle)
├── VarianteProductoId: int (FK → VarianteProducto)
├── CantidadDevuelta: int
├── DevolucionCambio: DevolucionCambio (nav)
├── VentaDetalle: VentaDetalle (nav)
└── VarianteProducto: VarianteProducto (nav)
```

---

## 4. Diagrama Entidad-Relación

```
┌──────────────┐     ┌───────────┐     ┌──────────┐
│  Categoria   │1───*│ Subgrupo  │     │ TipoPrec │
└──────┬───────┘     └─────┬─────┘     │ Zapatilla│
       │1                  │0..1        └────┬─────┘
       │                   │                 │0..1
       ▼*                  ▼*                │
┌──────────────┐                             │
│   Producto   │1───────────────────*┌───────▼────────┐
└──────────────┘                     │VarianteProducto │
                                     └───────┬────────┘
                                             │1
                              ┌──────────────┼──────────────┐
                              │              │              │
                              ▼1             ▼*             ▼*
                         ┌─────────┐  ┌───────────┐  ┌───────────┐
                         │  Stock  │  │Movimiento │  │  Compra   │
                         │  (1:1)  │  │  Stock    │  │  Detalle  │
                         └─────────┘  └───────────┘  └─────┬─────┘
                                                            │*
                                                            ▼1
┌──────────────┐     ┌──────────┐1──*┌──────────┐    ┌──────────┐
│  Proveedor   │1───*│  Compra  │───*│ Compra   │    │  Compra  │
└──────────────┘     └──────────┘    │ Adjunto  │    │ Detalle  │
                                     └──────────┘    └──────────┘

┌──────────────┐     ┌──────────┐1──*┌──────────┐
│   Cliente    │0..1─*│  Venta   │───*│  Venta   │
└──────────────┘     │          │    │ Detalle  │
                     │          │    └──────────┘
                     │          │1──*┌──────────┐
                     │          │───*│  Venta   │
                     │          │    │  Pago    │
                     │          │    └──────────┘
                     │          │1──*┌──────────┐
                     │          │───*│  Venta   │
                     │          │    │ Adjunto  │
                     │          │    └──────────┘
                     │          │1──1┌──────────┐
                     └──────────┘───1│  Remito  │
                          │          └──────────┘
                          │1
                          ▼*
                     ┌────────────┐1──*┌────────────────┐
                     │ Devolucion │───*│  Devolucion    │
                     │  Cambio    │    │ CambioDetalle  │
                     └────────────┘    └────────────────┘
```

---

## 5. Configuraciones Fluent API (EF Core)

Ubicación: `ShowroomGriffin.Infrastructure/Data/Configurations/`

Un archivo `IEntityTypeConfiguration<T>` por entidad. Se cargan automáticamente con `ApplyConfigurationsFromAssembly`.

### 5.1 Listado de archivos de configuración

```
Configurations/
├── Maestros/
│   ├── CategoriaConfiguration.cs
│   ├── SubgrupoConfiguration.cs
│   ├── ClienteConfiguration.cs
│   ├── ProveedorConfiguration.cs
│   └── TipoPrecioZapatillaConfiguration.cs
├── Productos/
│   ├── ProductoConfiguration.cs
│   └── VarianteProductoConfiguration.cs
├── Stock/
│   ├── StockConfiguration.cs
│   ├── MovimientoStockConfiguration.cs
│   └── AjusteStockConfiguration.cs
├── Compras/
│   ├── CompraConfiguration.cs
│   ├── CompraDetalleConfiguration.cs
│   └── CompraAdjuntoConfiguration.cs
├── Ventas/
│   ├── VentaConfiguration.cs
│   ├── VentaDetalleConfiguration.cs
│   ├── VentaPagoConfiguration.cs
│   ├── VentaAdjuntoConfiguration.cs
│   └── RemitoConfiguration.cs
└── Postventa/
    ├── DevolucionCambioConfiguration.cs
    └── DevolucionCambioDetalleConfiguration.cs
```

### 5.2 Configuraciones clave

**CategoriaConfiguration:**
- `Nombre`: MaxLength(100), IsRequired, HasIndex().IsUnique()

**VarianteProductoConfiguration:**
- `PrecioVenta`: HasPrecision(18, 2)
- `UltimoPrecioCompra`: HasPrecision(18, 2)
- `Sku`: MaxLength(50), HasIndex().IsUnique().HasFilter("Sku IS NOT NULL")
- `CodigoBarra`: MaxLength(50), HasIndex().IsUnique().HasFilter("CodigoBarra IS NOT NULL")
- FK a Producto: `.HasMany(p => p.Variantes).WithOne(v => v.Producto).HasForeignKey(v => v.ProductoId).OnDelete(DeleteBehavior.Restrict)`
- FK a TipoPrecioZapatilla: `.IsRequired(false).OnDelete(DeleteBehavior.SetNull)`

**StockConfiguration:**
- Relación 1:1 con VarianteProducto: `.HasOne(s => s.VarianteProducto).WithOne(v => v.Stock).HasForeignKey<Stock>(s => s.VarianteProductoId)`
- HasIndex(s => s.VarianteProductoId).IsUnique()

**MovimientoStockConfiguration:**
- `TipoMovimiento`: `.HasConversion<int>()`
- 4 FKs opcionales (CompraId, VentaId, DevolucionCambioId, AjusteStockId): todas `.IsRequired(false).OnDelete(DeleteBehavior.SetNull)`
- HasIndex(m => m.VarianteProductoId)

**VentaConfiguration:**
- `NroVenta`: MaxLength(20), IsRequired, HasIndex().IsUnique()
- `Estado`: `.HasConversion<int>().HasDefaultValue(EstadoVenta.Confirmada)`
- `Total`, `Subtotal`, `DescuentoMonto`: HasPrecision(18, 2)
- `DescuentoPorcentaje`: HasPrecision(5, 2)
- FK a Cliente: `.IsRequired(false).OnDelete(DeleteBehavior.SetNull)`
- FK a VendedorUserId: `.HasMaxLength(450)`
- HasIndex(v => v.FechaVenta)

**VentaPagoConfiguration:**
- `MedioPago`: `.HasConversion<int>()`
- `Importe`: HasPrecision(18, 2)
- `PorcentajeFinanciamiento`: HasPrecision(5, 2)
- HasIndex(p => p.MedioPago) — para resumen semanal

**CompraConfiguration:**
- `Estado`: `.HasConversion<int>().HasDefaultValue(EstadoCompra.Borrador)`
- FK a Proveedor: `.OnDelete(DeleteBehavior.Restrict)`

**CompraDetalleConfiguration:**
- `CostoUnitario`: HasPrecision(18, 2)
- FK a Compra: `.OnDelete(DeleteBehavior.Cascade)`
- FK a VarianteProducto: `.OnDelete(DeleteBehavior.Restrict)`

**RemitoConfiguration:**
- Relación 1:1: `.HasOne(r => r.Venta).WithOne(v => v.Remito).HasForeignKey<Remito>(r => r.VentaId)`
- HasIndex(r => r.VentaId).IsUnique()

**DevolucionCambioConfiguration:**
- FK a Venta: `.OnDelete(DeleteBehavior.Restrict)`
- FK a NuevaVarianteProducto: `.IsRequired(false).OnDelete(DeleteBehavior.SetNull)`

**Regla general OnDelete:**
- Relaciones maestro → detalle (Compra → CompraDetalle, Venta → VentaDetalle/Pago/Adjunto): `Cascade`
- Relaciones a entidades maestro (Proveedor, Categoría, VarianteProducto): `Restrict`
- Relaciones opcionales (Cliente en Venta, TipoPrecio en Variante): `SetNull`

---

## 6. Cambios en AppDbContext

### 6.1 Nuevos DbSets (20)

```csharp
// Maestros
public DbSet<Categoria> Categorias { get; set; }
public DbSet<Subgrupo> Subgrupos { get; set; }
public DbSet<Cliente> Clientes { get; set; }
public DbSet<Proveedor> Proveedores { get; set; }
public DbSet<TipoPrecioZapatilla> TiposPrecioZapatilla { get; set; }

// Productos
public DbSet<Producto> Productos { get; set; }
public DbSet<VarianteProducto> VariantesProducto { get; set; }

// Stock
public DbSet<Stock> Stocks { get; set; }
public DbSet<MovimientoStock> MovimientosStock { get; set; }
public DbSet<AjusteStock> AjustesStock { get; set; }

// Compras
public DbSet<Compra> Compras { get; set; }
public DbSet<CompraDetalle> ComprasDetalle { get; set; }
public DbSet<CompraAdjunto> ComprasAdjunto { get; set; }

// Ventas
public DbSet<Venta> Ventas { get; set; }
public DbSet<VentaDetalle> VentasDetalle { get; set; }
public DbSet<VentaPago> VentasPago { get; set; }
public DbSet<VentaAdjunto> VentasAdjunto { get; set; }
public DbSet<Remito> Remitos { get; set; }

// Postventa
public DbSet<DevolucionCambio> DevolucionesCambio { get; set; }
public DbSet<DevolucionCambioDetalle> DevolucionesCambioDetalle { get; set; }
```

### 6.2 Cambio en OnModelCreating

Agregar antes del cierre del método:

```csharp
modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
```

Esto reemplaza la necesidad de configurar entidad por entidad inline. Las configuraciones existentes de `AuditLog` y `Notification` se mantienen inline (ya funcionan) o se migran a archivos de configuración propios opcionalmente.

---

## 7. Plan de Migraciones EF

6 migraciones incrementales ordenadas por dependencias de FK.

| # | Migración | Entidades | Dependencias |
|---|---|---|---|
| M1 | `AddMaestrosComerciales` | Categoria, Subgrupo, Cliente, Proveedor, TipoPrecioZapatilla | Ninguna |
| M2 | `AddProductosVariantes` | Producto, VarianteProducto | M1 (Categoria, Subgrupo, TipoPrecio) |
| M3 | `AddStockInventario` | Stock, MovimientoStock, AjusteStock | M2 (VarianteProducto) |
| M4 | `AddCompras` | Compra, CompraDetalle, CompraAdjunto | M1 (Proveedor), M2 (VarianteProducto) |
| M5 | `AddVentas` | Venta, VentaDetalle, VentaPago, VentaAdjunto, Remito | M2 (VarianteProducto), M1 (Cliente) |
| M6 | `AddDevoluciones` | DevolucionCambio, DevolucionCambioDetalle | M5 (Venta, VentaDetalle), M2 (VarianteProducto) |

**Comandos:**

```bash
# Desde raíz de la solución
dotnet ef migrations add AddMaestrosComerciales -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add AddProductosVariantes -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add AddStockInventario -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add AddCompras -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add AddVentas -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
dotnet ef migrations add AddDevoluciones -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web

# Aplicar
dotnet ef database update -p ShowroomGriffin.Infrastructure -s ShowroomGriffin.Web
```

---

## 8. Cambios en SeedData

Agregar rol "Vendedor":

```
Actual:   string[] roles = [RolSuperUsuario, RolAdministrador];
Nuevo:    string[] roles = [RolSuperUsuario, RolAdministrador, RolVendedor];

Agregar constante:
public const string RolVendedor = "Vendedor";
```

---

## 9. Políticas de Autorización

Agregar en `Program.cs` después de `AddIdentity`:

```
RequireAdministrador → RequireRole("SuperUsuario", "Administrador")
RequireVendedor      → RequireRole("SuperUsuario", "Administrador", "Vendedor")
```

**Aplicación en Controllers:**

| Controller | Política |
|---|---|
| CategoriasController | `[Authorize(Policy = "RequireAdministrador")]` |
| SubgruposController | `[Authorize(Policy = "RequireAdministrador")]` |
| ClientesController | `[Authorize(Policy = "RequireVendedor")]` (CUD solo Admin via service) |
| ProveedoresController | `[Authorize(Policy = "RequireAdministrador")]` |
| TiposPrecioController | `[Authorize(Policy = "RequireAdministrador")]` |
| ProductosController | `[Authorize(Policy = "RequireVendedor")]` (CUD solo Admin via service) |
| StockController | Index/Historial: `RequireVendedor`; CargaInicial/Ajuste: `RequireAdministrador` |
| ComprasController | `[Authorize(Policy = "RequireAdministrador")]` |
| VentasController | `[Authorize(Policy = "RequireVendedor")]` |
| DevolucionesController | `[Authorize(Policy = "RequireVendedor")]` |
| AumentoMasivoController | `[Authorize(Policy = "RequireAdministrador")]` |
| ResumenSemanalController | `[Authorize(Policy = "RequireAdministrador")]` |

---

## 10. Registro de Servicios (DependencyInjection.cs)

14 servicios nuevos a registrar en `AddInfrastructure`:

```csharp
// Maestros
services.AddScoped<ICategoriaService, CategoriaService>();
services.AddScoped<ISubgrupoService, SubgrupoService>();
services.AddScoped<IClienteService, ClienteService>();
services.AddScoped<IProveedorService, ProveedorService>();
services.AddScoped<ITipoPrecioZapatillaService, TipoPrecioZapatillaService>();

// Productos
services.AddScoped<IProductoService, ProductoService>();
services.AddScoped<IVarianteService, VarianteService>();

// Stock
services.AddScoped<IStockService, StockService>();

// Compras
services.AddScoped<ICompraService, CompraService>();

// Ventas
services.AddScoped<IVentaService, VentaService>();
services.AddScoped<IRemitoService, RemitoService>();

// Postventa
services.AddScoped<IDevolucionService, DevolucionService>();

// Consultas
services.AddScoped<IResumenSemanalService, ResumenSemanalService>();
services.AddScoped<IAumentoMasivoService, AumentoMasivoService>();
```

---

## 11. Tabla de Rutas Completa

| Módulo | Ruta | Método | Controller.Action |
|---|---|---|---|
| **Categorías** | `/Categorias` | GET | Categorias.Index |
| | `/Categorias/Crear` | GET/POST | Categorias.Crear |
| | `/Categorias/Editar/{id}` | GET/POST | Categorias.Editar |
| | `/Categorias/Inactivar/{id}` | POST | Categorias.Inactivar |
| **Subgrupos** | `/Subgrupos` | GET | Subgrupos.Index |
| | `/Subgrupos/Crear` | GET/POST | Subgrupos.Crear |
| | `/Subgrupos/Editar/{id}` | GET/POST | Subgrupos.Editar |
| | `/Subgrupos/Inactivar/{id}` | POST | Subgrupos.Inactivar |
| | `/api/Subgrupos/PorCategoria/{id}` | GET | Subgrupos.PorCategoria (JSON) |
| **Clientes** | `/Clientes` | GET | Clientes.Index |
| | `/Clientes/Crear` | GET/POST | Clientes.Crear |
| | `/Clientes/Editar/{id}` | GET/POST | Clientes.Editar |
| | `/Clientes/Inactivar/{id}` | POST | Clientes.Inactivar |
| | `/api/Clientes/Buscar?term=` | GET | Clientes.Buscar (JSON) |
| **Proveedores** | `/Proveedores` | GET | Proveedores.Index |
| | `/Proveedores/Crear` | GET/POST | Proveedores.Crear |
| | `/Proveedores/Editar/{id}` | GET/POST | Proveedores.Editar |
| | `/Proveedores/Inactivar/{id}` | POST | Proveedores.Inactivar |
| | `/api/Proveedores/Buscar?term=` | GET | Proveedores.Buscar (JSON) |
| **TiposPrecio** | `/TiposPrecio` | GET | TiposPrecio.Index |
| | `/TiposPrecio/Crear` | GET/POST | TiposPrecio.Crear |
| | `/TiposPrecio/Editar/{id}` | GET/POST | TiposPrecio.Editar |
| | `/TiposPrecio/Inactivar/{id}` | POST | TiposPrecio.Inactivar |
| **Productos** | `/Productos` | GET | Productos.Index |
| | `/Productos/Crear` | GET/POST | Productos.Crear |
| | `/Productos/Editar/{id}` | GET/POST | Productos.Editar |
| | `/Productos/Detalle/{id}` | GET | Productos.Detalle |
| | `/Productos/{prodId}/Variantes/Crear` | GET/POST | Variantes.Crear |
| | `/Productos/{prodId}/Variantes/Editar/{id}` | GET/POST | Variantes.Editar |
| | `/Productos/{prodId}/Variantes/Inactivar/{id}` | POST | Variantes.Inactivar |
| | `/api/Variantes/Buscar?term=` | GET | Variantes.Buscar (JSON) |
| | `/api/Variantes/{id}/Stock` | GET | Variantes.Stock (JSON) |
| **Stock** | `/Stock` | GET | Stock.Index |
| | `/Stock/CargaInicial` | GET/POST | Stock.CargaInicial |
| | `/Stock/Ajuste` | GET/POST | Stock.Ajuste |
| | `/Stock/Historial` | GET | Stock.Historial |
| **Compras** | `/Compras` | GET | Compras.Index |
| | `/Compras/Crear` | GET/POST | Compras.Crear |
| | `/Compras/Detalle/{id}` | GET | Compras.Detalle |
| | `/Compras/Editar/{id}` | GET/POST | Compras.Editar |
| | `/Compras/CambiarEstado/{id}` | POST | Compras.CambiarEstado |
| | `/Compras/Recepcionar/{id}` | GET/POST | Compras.Recepcionar |
| | `/Compras/Adjuntar/{id}` | POST | Compras.Adjuntar |
| **Ventas** | `/Ventas` | GET | Ventas.Index |
| | `/Ventas/Crear` | GET/POST | Ventas.Crear |
| | `/Ventas/Detalle/{id}` | GET | Ventas.Detalle |
| | `/Ventas/Anular/{id}` | POST | Ventas.Anular |
| | `/Ventas/Entregar/{id}` | POST | Ventas.Entregar |
| | `/Ventas/Remito/{id}` | GET | Ventas.Remito (PDF) |
| | `/Ventas/Adjuntar/{id}` | POST | Ventas.Adjuntar |
| **Devoluciones** | `/Devoluciones` | GET | Devoluciones.Index |
| | `/Devoluciones/Crear` | GET/POST | Devoluciones.Crear |
| | `/Devoluciones/Detalle/{id}` | GET | Devoluciones.Detalle |
| **Resumen** | `/ResumenSemanal` | GET | ResumenSemanal.Index |
| | `/api/ResumenSemanal?fecha=` | GET | ResumenSemanal.Obtener (JSON) |
| **Aumento** | `/AumentoMasivo` | GET | AumentoMasivo.Index |
| | `/api/AumentoMasivo/Variantes` | GET | AumentoMasivo.Variantes (JSON) |
| | `/AumentoMasivo/Aplicar` | POST | AumentoMasivo.Aplicar |

---

## 12. Estructura de Archivos Nuevos

```
ShowroomGriffin.Domain/
├── Enums/
│   ├── EstadoCompra.cs
│   ├── EstadoVenta.cs
│   ├── MedioPago.cs
│   ├── TipoMovimiento.cs
│   └── TipoDevolucion.cs
└── Entities/
    ├── Maestros/
    │   ├── Categoria.cs
    │   ├── Subgrupo.cs
    │   ├── Cliente.cs
    │   ├── Proveedor.cs
    │   └── TipoPrecioZapatilla.cs
    ├── Productos/
    │   ├── Producto.cs
    │   └── VarianteProducto.cs
    ├── Stock/
    │   ├── Stock.cs
    │   ├── MovimientoStock.cs
    │   └── AjusteStock.cs
    ├── Compras/
    │   ├── Compra.cs
    │   ├── CompraDetalle.cs
    │   └── CompraAdjunto.cs
    ├── Ventas/
    │   ├── Venta.cs
    │   ├── VentaDetalle.cs
    │   ├── VentaPago.cs
    │   ├── VentaAdjunto.cs
    │   └── Remito.cs
    └── Postventa/
        ├── DevolucionCambio.cs
        └── DevolucionCambioDetalle.cs

ShowroomGriffin.Application/
├── Interfaces/
│   ├── ICategoriaService.cs
│   ├── ISubgrupoService.cs
│   ├── IClienteService.cs
│   ├── IProveedorService.cs
│   ├── ITipoPrecioZapatillaService.cs
│   ├── IProductoService.cs
│   ├── IVarianteService.cs
│   ├── IStockService.cs
│   ├── ICompraService.cs
│   ├── IVentaService.cs
│   ├── IRemitoService.cs
│   ├── IDevolucionService.cs
│   ├── IResumenSemanalService.cs
│   └── IAumentoMasivoService.cs
└── DTOs/
    (los ViewModels se definen en Web/Models por convención del proyecto)

ShowroomGriffin.Infrastructure/
├── Data/
│   ├── Configurations/
│   │   ├── Maestros/
│   │   │   ├── CategoriaConfiguration.cs
│   │   │   ├── SubgrupoConfiguration.cs
│   │   │   ├── ClienteConfiguration.cs
│   │   │   ├── ProveedorConfiguration.cs
│   │   │   └── TipoPrecioZapatillaConfiguration.cs
│   │   ├── Productos/
│   │   │   ├── ProductoConfiguration.cs
│   │   │   └── VarianteProductoConfiguration.cs
│   │   ├── Stock/
│   │   │   ├── StockConfiguration.cs
│   │   │   ├── MovimientoStockConfiguration.cs
│   │   │   └── AjusteStockConfiguration.cs
│   │   ├── Compras/
│   │   │   ├── CompraConfiguration.cs
│   │   │   ├── CompraDetalleConfiguration.cs
│   │   │   └── CompraAdjuntoConfiguration.cs
│   │   ├── Ventas/
│   │   │   ├── VentaConfiguration.cs
│   │   │   ├── VentaDetalleConfiguration.cs
│   │   │   ├── VentaPagoConfiguration.cs
│   │   │   ├── VentaAdjuntoConfiguration.cs
│   │   │   └── RemitoConfiguration.cs
│   │   └── Postventa/
│   │       ├── DevolucionCambioConfiguration.cs
│   │       └── DevolucionCambioDetalleConfiguration.cs
│   └── Migrations/
│       ├── (existentes)
│       ├── YYYYMMDD_AddMaestrosComerciales.cs
│       ├── YYYYMMDD_AddProductosVariantes.cs
│       ├── YYYYMMDD_AddStockInventario.cs
│       ├── YYYYMMDD_AddCompras.cs
│       ├── YYYYMMDD_AddVentas.cs
│       └── YYYYMMDD_AddDevoluciones.cs
└── Services/
    ├── CategoriaService.cs
    ├── SubgrupoService.cs
    ├── ClienteService.cs
    ├── ProveedorService.cs
    ├── TipoPrecioZapatillaService.cs
    ├── ProductoService.cs
    ├── VarianteService.cs
    ├── StockService.cs
    ├── CompraService.cs
    ├── VentaService.cs
    ├── RemitoService.cs
    ├── DevolucionService.cs
    ├── ResumenSemanalService.cs
    └── AumentoMasivoService.cs

ShowroomGriffin.Web/
├── Controllers/
│   ├── CategoriasController.cs
│   ├── SubgruposController.cs
│   ├── ClientesController.cs
│   ├── ProveedoresController.cs
│   ├── TiposPrecioController.cs
│   ├── ProductosController.cs
│   ├── VariantesController.cs       (acciones anidadas bajo Productos)
│   ├── StockController.cs
│   ├── ComprasController.cs
│   ├── VentasController.cs
│   ├── DevolucionesController.cs
│   ├── ResumenSemanalController.cs
│   └── AumentoMasivoController.cs
├── Models/
│   ├── Maestros/
│   │   ├── CategoriaViewModel.cs
│   │   ├── SubgrupoViewModel.cs
│   │   ├── ClienteViewModel.cs
│   │   ├── ProveedorViewModel.cs
│   │   └── TipoPrecioZapatillaViewModel.cs
│   ├── Productos/
│   │   ├── ProductoViewModel.cs
│   │   └── VarianteViewModel.cs
│   ├── Stock/
│   │   ├── StockListItemViewModel.cs
│   │   ├── AjusteStockViewModel.cs
│   │   └── MovimientoStockListItemViewModel.cs
│   ├── Compras/
│   │   ├── CompraCreateViewModel.cs
│   │   ├── CompraDetalleViewModel.cs
│   │   ├── CompraListItemViewModel.cs
│   │   └── CompraRecepcionViewModel.cs
│   ├── Ventas/
│   │   ├── VentaCreateViewModel.cs
│   │   ├── VentaDetalleViewModel.cs
│   │   ├── VentaListItemViewModel.cs
│   │   └── VentaPagoItemViewModel.cs
│   ├── Devoluciones/
│   │   ├── DevolucionCreateViewModel.cs
│   │   ├── DevolucionDetalleViewModel.cs
│   │   └── DevolucionListItemViewModel.cs
│   ├── ResumenSemanalViewModel.cs
│   └── AumentoMasivoViewModel.cs
└── Views/
    ├── Categorias/
    │   ├── Index.cshtml
    │   ├── Crear.cshtml
    │   └── Editar.cshtml
    ├── Subgrupos/
    │   ├── Index.cshtml
    │   ├── Crear.cshtml
    │   └── Editar.cshtml
    ├── Clientes/
    │   ├── Index.cshtml
    │   ├── Crear.cshtml
    │   └── Editar.cshtml
    ├── Proveedores/
    │   ├── Index.cshtml
    │   ├── Crear.cshtml
    │   └── Editar.cshtml
    ├── TiposPrecio/
    │   ├── Index.cshtml
    │   ├── Crear.cshtml
    │   └── Editar.cshtml
    ├── Productos/
    │   ├── Index.cshtml
    │   ├── Crear.cshtml
    │   ├── Editar.cshtml
    │   ├── Detalle.cshtml
    │   ├── _VarianteCrear.cshtml      (partial)
    │   └── _VarianteEditar.cshtml     (partial)
    ├── Stock/
    │   ├── Index.cshtml
    │   ├── CargaInicial.cshtml
    │   ├── Ajuste.cshtml
    │   └── Historial.cshtml
    ├── Compras/
    │   ├── Index.cshtml
    │   ├── Crear.cshtml
    │   ├── Detalle.cshtml
    │   ├── Editar.cshtml
    │   └── Recepcionar.cshtml
    ├── Ventas/
    │   ├── Index.cshtml
    │   ├── Crear.cshtml
    │   └── Detalle.cshtml
    ├── Devoluciones/
    │   ├── Index.cshtml
    │   ├── Crear.cshtml
    │   └── Detalle.cshtml
    ├── ResumenSemanal/
    │   └── Index.cshtml
    ├── AumentoMasivo/
    │   └── Index.cshtml
    └── Shared/
        └── _Layout.cshtml             (modificar sidebar)
```

---

## 13. Impacto Técnico por Capa

### Domain

| Cambio | Cantidad | Requiere migración |
|---|---|---|
| Enums nuevos | 5 | No |
| Entidades nuevas (SoftDestroyable) | 20 | Sí |
| Carpetas nuevas | 5 | No |

### Application

| Cambio | Cantidad | Requiere migración |
|---|---|---|
| Interfaces de servicio nuevas | 14 | No |

### Infrastructure

| Cambio | Cantidad | Requiere migración |
|---|---|---|
| IEntityTypeConfiguration nuevos | 20 | No (definen el schema) |
| DbSets en AppDbContext | 20 | Sí |
| ApplyConfigurationsFromAssembly | 1 línea | Sí |
| Servicios nuevos | 14 | No |
| Registros DI | 14 | No |
| SeedData: agregar RolVendedor | 1 | No |
| Migraciones | 6 | Sí |

### Web

| Cambio | Cantidad | Requiere migración |
|---|---|---|
| Controllers nuevos | 13 | No |
| ViewModels nuevos | ~35 | No |
| Views nuevas | ~30 | No |
| Políticas autorización (Program.cs) | 2 | No |
| Sidebar update (_Layout.cshtml) | 1 | No |

---

## 14. Riesgos y Supuestos

| # | Tipo | Descripción | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | Riesgo | 6 migraciones incrementales requieren orden estricto | Alto | Ejecutar secuencialmente; validar con `dotnet ef migrations script` antes de producción |
| R2 | Riesgo | Índices únicos condicionales (SKU, CodigoBarra WHERE NOT NULL) dependen del provider MySQL | Medio | Verificar soporte de `.HasFilter()` en MySql.EntityFrameworkCore; si no soporta, usar índice único normal + validación en service |
| R3 | Riesgo | `ApplyConfigurationsFromAssembly` puede cargar configs de test si se mezclan assemblies | Bajo | Solo usar en assembly de Infrastructure |
| R4 | Riesgo | Transacciones explícitas en VentaService y CompraService requieren nivel de aislamiento adecuado | Alto | Usar `IsolationLevel.ReadCommitted` como mínimo; evaluar Serializable para decrementos de stock concurrentes |
| R5 | Riesgo | Relaciones Cascade en detalle de compra/venta pueden generar cascadas largas en soft delete | Medio | El soft delete se maneja vía código (SoftDestroyable), no vía CASCADE de BD; CASCADE solo aplica a hard delete |
| S1 | Supuesto | El proyecto es MVC (Controllers/Views), no Razor Pages | — | Confirmado por codebase existente |
| S2 | Supuesto | `NroVenta` se genera post-SaveChanges usando el Id autogenerado | — | Patrón two-save: 1° save genera Id, 2° save asigna NroVenta = $"VTA-{Id:D5}" |
| S3 | Supuesto | MovimientoStock usa 4 FKs opcionales (no discriminador string) | — | Patrón preferido por la instrucción de dominio |
| S4 | Supuesto | Los adjuntos se almacenan en `wwwroot/uploads/{entidad}/{GUID}.ext` | — | Migrar a blob storage en v2 |

---

## 15. Pruebas Mínimas Requeridas

### Migraciones

- [ ] M1–M6 se generan sin errores.
- [ ] `dotnet ef database update` aplica las 6 migraciones limpiamente.
- [ ] `dotnet ef migrations script` genera SQL válido para MySQL 8.
- [ ] Índice único condicional en SKU/CodigoBarra funciona correctamente.

### Entidades y Configuraciones

- [ ] Soft delete filter aplica a las 20 entidades nuevas.
- [ ] AuditLog registra Create/Update/Delete para todas las entidades.
- [ ] Relación 1:1 Stock ↔ VarianteProducto funciona (insert/query).
- [ ] FKs con OnDelete Restrict impiden borrar entidad padre con hijos.

### Seed y Autorización

- [ ] Rol "Vendedor" se crea en seed.
- [ ] Policy "RequireAdministrador" rechaza Vendedor (403).
- [ ] Policy "RequireVendedor" permite Administrador y Vendedor.

### Servicios (integración)

- [ ] CRUD completo de cada maestro via service.
- [ ] Crear variante → Stock inicializado en 0.
- [ ] Recepción compra → Stock incrementado + UltimoPrecioCompra actualizado.
- [ ] Crear venta → Stock decrementado + NroVenta generado + MovimientoStock creado.
- [ ] Anular venta → Stock repuesto.
- [ ] Devolución → Stock reingresado + validación cantidad disponible.
- [ ] Aumento masivo → Precios actualizados excluyendo variantes excluidas.
- [ ] Resumen semanal → Solo transferencias de ventas Confirmada/Entregada.

### Autorización (E2E)

- [ ] Vendedor: 403 en /Compras, /Stock/Ajuste, /AumentoMasivo, /ResumenSemanal.
- [ ] Vendedor: no recibe UltimoPrecioCompra ni Ganancia en ningún response.

---

## 16. Checklist de Salida para Merge

```
ARQUITECTURA — CHECKLIST DE SALIDA
────────────────────────────────────────────────────────────────────────
DOMAIN
[ ] 5 enums creados en Domain/Enums/
[ ] 20 entidades creadas en Domain/Entities/ con carpetas por módulo
[ ] Todas heredan de SoftDestroyable
[ ] Propiedades de navegación definidas (no circular sin JsonIgnore)
[ ] No hay lógica de negocio en entidades

APPLICATION
[ ] 14 interfaces de servicio en Application/Interfaces/
[ ] Todos los métodos retornan ServiceResult o ServiceResult<T>
[ ] No hay referencia a Infrastructure ni Web

INFRASTRUCTURE — DATOS
[ ] 20 IEntityTypeConfiguration creados
[ ] ApplyConfigurationsFromAssembly agregado en OnModelCreating
[ ] 20 DbSets agregados en AppDbContext
[ ] 6 migraciones generadas y aplicadas sin errores
[ ] Índices de performance creados (FechaVenta, MedioPago, SKU, CodigoBarra)
[ ] Índices únicos condicionales verificados en MySQL

INFRASTRUCTURE — SERVICIOS
[ ] 14 servicios implementados en Infrastructure/Services/
[ ] 14 registros en DependencyInjection.cs (AddScoped)
[ ] RolVendedor agregado en SeedData.cs
[ ] Transacciones explícitas en VentaService y CompraService

WEB
[ ] 13 controllers nuevos con policies correctas
[ ] 2 políticas de autorización en Program.cs
[ ] ~35 ViewModels en Web/Models/
[ ] ~30 Views en Web/Views/
[ ] Sidebar actualizado con visibilidad por rol
[ ] Build exitoso sin warnings

GENERAL
[ ] dotnet build sin errores
[ ] dotnet ef database update exitoso
[ ] Seed ejecuta sin errores (3 roles)
────────────────────────────────────────────────────────────────────────
```
