# 📖 Metadata del Proyecto - ShowroomGriffin
**Fecha creación:** 2026-04-23  
**Última actualización:** 2026-04-23  

---

## 🏢 Información General

| Campo | Valor |
|-------|-------|
| **Nombre del Proyecto** | ShowroomGriffin |
| **Tipo de Proyecto** | Sistema de Gestión Comercial (Showroom Indumentaria/Calzado) |
| **Tecnología** | ASP.NET Core MVC (.NET 10) |
| **Base de Datos** | MySQL |
| **ORM** | Entity Framework Core |
| **Autenticación** | ASP.NET Core Identity |
| **Logging** | Serilog |
| **PDF** | QuestPDF |
| **Arquitectura** | Clean Architecture (Domain, Application, Infrastructure, Web) |
| **ruta_repositorio** | C:\Sistemas\ShowroomGriffin |
| **Repositorio** | https://gitlab.com/olvidata/ShowroomGriffin |
| **Branch principal** | main |

---

## 🎯 Dominio del Negocio

**Rubro:** Showroom de Indumentaria y Calzado (venta minorista/mayorista).

**Entidades principales del dominio:**

1. **Producto:** Identidad comercial agrupadora (ej. "Zapatilla Nike Air Max Modelo X").
   - Atributos: Marca, Modelo, Categoría, Subgrupo.

2. **VarianteProducto:** SKU vendible (ej. "Nike Air Max Modelo X – Talle 39 – Negro").
   - Atributos: Color, Talle/Número, Género, Temporada, PrecioVenta, SKU, Código de Barra, Stock.

3. **Venta:** Transacción de venta a cliente.
   - Atributos: NroVenta, Cliente, Vendedor, Fecha, Subtotal, Descuento, Total, Estado, Observaciones, Anotaciones.

4. **Compra:** Orden de compra a proveedor.
   - Atributos: Proveedor, FechaCompra, FechaRecepción, Estado, Observaciones.

5. **Stock:** Inventario de variantes.
   - Atributos: VarianteProducto, Cantidad, StockMínimo, UbicaciónFísica.

6. **Cliente:** Cliente del showroom.
   - Atributos: Nombre, Teléfono, WhatsApp, Dirección, CUIT.

7. **Proveedor:** Proveedor de productos.
   - Atributos: Nombre, Teléfono, Email, Dirección, CUIT.

8. **Categoría:** Taxonomía de productos (ej. Indumentaria, Zapatillas, Accesorios).

9. **Subgrupo:** Subtaxonomía (ej. Marcas: Nike, Adidas, Puma).

10. **VentaCambio (nueva):** Registro de cambios/devoluciones de ventas.

11. **TalleZapatilla (nueva):** Catálogo de talles predefinidos.

---

## 🏗️ Arquitectura Actual

### Capas del Proyecto

```
ShowroomGriffin.sln
│
├── ShowroomGriffin.Domain
│   ├── Entities
│   │   ├── Productos (Producto, VarianteProducto)
│   │   ├── Ventas (Venta, VentaDetalle, VentaPago, VentaAdjunto, Remito)
│   │   ├── Compras (Compra, CompraDetalle, CompraAdjunto)
│   │   ├── Stock (Stock, MovimientoStock)
│   │   └── Maestros (Cliente, Proveedor, Categoria, Subgrupo, TipoPrecioZapatilla)
│   ├── Enums (EstadoVenta, EstadoCompra, MedioPago, TipoMovimiento)
│   └── Base (SoftDestroyable, ApplicationUser)
│
├── ShowroomGriffin.Application
│   ├── Interfaces (IProductoService, IVentaService, ICompraService, IStockService, etc.)
│   └── DTOs (ProductosViewModels, VentasViewModels, etc.)
│
├── ShowroomGriffin.Infrastructure
│   ├── Data
│   │   ├── AppDbContext
│   │   ├── Configurations (ProductoConfiguration, VentaConfiguration, etc.)
│   │   ├── Migrations
│   │   └── SeedData
│   └── Services (ProductoService, VentaService, CompraService, StockService, etc.)
│
└── ShowroomGriffin.Web
    ├── Controllers (ProductosController, VentasController, ComprasController, StockController, etc.)
    ├── Views
    ├── wwwroot (CSS, JS, libs)
    ├── Middleware (GlobalExceptionHandler, SoftDestroyMiddleware)
    └── Program.cs
```

### Patrón de Acceso a Datos

- **Repository Pattern:** No implementado explícitamente (servicios acceden directamente a `AppDbContext`).
- **Unit of Work:** `AppDbContext` actúa como UoW.
- **Inyección de Dependencias:** configurada en `Program.cs` vía `AddInfrastructure()`.

### Autenticación y Autorización

- **ASP.NET Core Identity** con `ApplicationUser` extendiendo `IdentityUser`.
- **Roles configurados:**
  - `SuperUsuario` (acceso total).
  - `Administrador` (acceso total excepto gestión de usuarios).
  - `Vendedor` (acceso a Ventas, sin acceso a Compras/Maestros).
  - `Empleado` (nuevo, pendiente de implementación: solo Ventas, Cambios, Stock).

- **Policies:**
  - `RequireSuperUsuario`: solo SuperUsuario.
  - `RequireAdministracion`: SuperUsuario + Administrador.
  - `RequireVendedor`: SuperUsuario + Administrador + Vendedor.
  - `RequireEmpleado` (pendiente): SuperUsuario + Administrador + Vendedor + Empleado.

### Soft Delete

- Implementado mediante clase base `SoftDestroyable` (propiedad `IsDeleted`).
- Middleware `SoftDestroyMiddleware` aplica filtro global en queries.

---

## 📊 Modelo Conceptual Vigente (Post-Refactor R10+R12)

```
Categoría (Indumentaria | Zapatillas | Accesorios)
   └── Subgrupo (Marca: Nike, Adidas, etc.)
         └── Producto (Marca + Modelo, ej. "Nike Air Max Modelo X")
               └── VarianteProducto (Color + Talle, ej. "Negro 39")
                     ├── Stock (Cantidad, StockMínimo)
                     ├── VentaDetalle (Venta → Variante)
                     └── CompraDetalle (Compra → Variante)
```

**Diferencias con el modelo original:**

| Campo | Modelo Original | Modelo Nuevo (R10+R12) |
|-------|-----------------|------------------------|
| **Marca** | En `VarianteProducto` | En `Producto` |
| **Modelo** | En `VarianteProducto` | En `Producto` |
| **Categoría** | String libre | Enum o validado (Indumentaria, Zapatillas, Accesorios) |
| **Subgrupo** | "Subgrupo de categoría" | "Marca" (reinterpretación semántica) |

---

## 🔑 Entidades Clave y Relaciones

### Producto (agrupador)

```csharp
public class Producto : SoftDestroyable
{
    public string Nombre { get; set; }       // Nombre comercial
    public string Marca { get; set; }        // NUEVO (R10)
    public string Modelo { get; set; }       // NUEVO (R10)
    public int CategoriaId { get; set; }
    public int? SubgrupoId { get; set; }     // Subgrupo = Marca

    public Categoria Categoria { get; set; }
    public Subgrupo? Subgrupo { get; set; }
    public ICollection<VarianteProducto> Variantes { get; set; }
}
```

### VarianteProducto (SKU vendible)

```csharp
public class VarianteProducto : SoftDestroyable
{
    public int ProductoId { get; set; }
    public decimal PrecioVenta { get; set; }
    public string? CodigoInterno { get; set; }
    public string? Sku { get; set; }
    public string? CodigoBarra { get; set; }

    // Atributos específicos de la variante
    public string? Talle { get; set; }
    public string? Color { get; set; }
    public string? Genero { get; set; }
    public string? Temporada { get; set; }
    public string? Numero { get; set; }

    // ELIMINADOS en R10: Marca, Modelo, TipoPrecioZapatillaId

    public byte[] RowVersion { get; set; }   // Concurrencia optimista

    public Producto Producto { get; set; }
    public Stock Stock { get; set; }
    public ICollection<VentaDetalle> VentaDetalles { get; set; }
    public ICollection<CompraDetalle> CompraDetalles { get; set; }
}
```

### Venta

```csharp
public class Venta : SoftDestroyable
{
    public string NroVenta { get; set; }
    public int? ClienteId { get; set; }
    public string VendedorUserId { get; set; }
    public DateTime FechaVenta { get; set; }
    public decimal Subtotal { get; set; }
    public decimal DescuentoPorcentaje { get; set; }
    public decimal DescuentoMonto { get; set; }
    public decimal Total { get; set; }
    public EstadoVenta Estado { get; set; }
    public string? Observaciones { get; set; }
    public string? Anotaciones { get; set; }  // NUEVO (R1)

    public Cliente? Cliente { get; set; }
    public ICollection<VentaDetalle> Detalles { get; set; }
    public ICollection<VentaPago> Pagos { get; set; }
    public ICollection<VentaAdjunto> Adjuntos { get; set; }
    public Remito? Remito { get; set; }
}
```

### VentaCambio (nueva entidad - R7)

```csharp
public class VentaCambio : SoftDestroyable
{
    public int VentaOrigenId { get; set; }
    public int? VentaDestinoId { get; set; }   // null si es devolución
    public EstadoVentaCambio Estado { get; set; }
    public string Motivo { get; set; }
    public DateTime FechaCambio { get; set; }
    public decimal? DiferenciaMonto { get; set; }  // positivo = cobro adicional, negativo = nota de crédito

    public Venta VentaOrigen { get; set; }
    public Venta? VentaDestino { get; set; }
}
```

### TalleZapatilla (nueva entidad - R11)

```csharp
public class TalleZapatilla : SoftDestroyable
{
    public RangoTipoTalle RangoTipo { get; set; }  // Adulto | Niño
    public int NumeroInicio { get; set; }
    public int NumeroFin { get; set; }
}
```

---

## 🛠️ Tecnologías y Librerías

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **.NET** | 10 | Framework principal |
| **ASP.NET Core MVC** | 10 | Capa de presentación |
| **Entity Framework Core** | 10 | ORM |
| **MySQL** | 8.x | Base de datos |
| **Pomelo.EntityFrameworkCore.MySql** | Latest | Provider EF Core para MySQL |
| **ASP.NET Core Identity** | 10 | Autenticación y autorización |
| **Serilog** | Latest | Logging estructurado |
| **QuestPDF** | Latest | Generación de PDFs |
| **Bootstrap** | 5.x | Framework CSS |
| **jQuery** | 3.x | Manipulación DOM y AJAX |
| **jQuery Validation** | Latest | Validaciones client-side |

---

## 📁 Estructura de Documentación

```
docs/
├── ShowroomGriffin/
│   ├── definiciones/
│   │   ├── 1-analista-funcional.md      ✅ Creado (2026-04-23)
│   │   ├── 2-disenador-funcional.md     ⏳ Pendiente
│   │   ├── 3-arquitecto-mvc.md          ⏳ Pendiente
│   │   ├── 4-presupuestador.md          ⏳ Pendiente
│   │   ├── 5-implementador.md           ⏳ Pendiente
│   │   └── 6-qa.md                      ⏳ Pendiente
│   ├── trazabilidad.md                  ✅ Creado (2026-04-23)
│   └── metadata.md                      ✅ Creado (este archivo)
├── qa/
│   ├── README.md                        ✅ Existente
│   └── casos-prueba-refactor-modelo.md  ⏳ Pendiente
└── runbooks/
    ├── migraciones-produccion.md        ✅ Existente
    └── (otros runbooks)
```

---

## 🔄 Estado Actual del Proyecto

### Módulos Implementados

- ✅ **Autenticación y Autorización** (ASP.NET Core Identity).
- ✅ **Maestros:** Categorías, Subgrupos, Clientes, Proveedores, TipoPrecioZapatilla.
- ✅ **Productos:** CRUD de Productos y Variantes.
- ✅ **Ventas:** CRUD de Ventas, Detalles, Pagos, Adjuntos, Remitos.
- ✅ **Compras:** CRUD de Compras, Detalles, Adjuntos.
- ✅ **Stock:** Gestión de inventario, movimientos, ajustes.
- ✅ **Reportes básicos** (pendiente de validar alcance).
- ✅ **Logging con Serilog** (console + file).
- ✅ **Soft Delete** global.

### Módulos en Desarrollo (Feature Actual)

- 🚧 **R1:** Campo Anotaciones en Venta.
- 🚧 **R2:** Modal Crear Cliente desde Venta.
- 🚧 **R3:** Combos anidados en Ventas.
- 🚧 **R4:** Autocompletar importe de pago.
- 🚧 **R5:** Combos anidados en Compras.
- 🚧 **R6:** Pantalla Consulta Stock.
- 🚧 **R7:** Cambio/Devolución de Ventas.
- 🚧 **R8:** Rol Empleado.
- 🚧 **R9:** Importes editables en Venta.
- 🚧 **R10+R12:** Refactor del modelo (Marca/Modelo a Producto).
- 🚧 **R11:** Maestro de talles predefinidos.

---

## 🎯 Próximos Hitos

| Hito | Fecha Estimada | Estado |
|------|----------------|--------|
| **Análisis funcional aprobado** | 2026-04-23 | ✅ Completado |
| **Diseño funcional aprobado** | TBD | ⏳ Pendiente |
| **Arquitectura técnica aprobada** | TBD | ⏳ Pendiente |
| **Presupuesto aprobado** | TBD | ⏳ Pendiente |
| **ETAPA 1: Refactor Modelo (M2)** | TBD | ⏳ Pendiente |
| **ETAPA 2-8: Funcionalidades** | TBD | ⏳ Pendiente |
| **QA completo** | TBD | ⏳ Pendiente |
| **Deploy a producción** | TBD | ⏳ Pendiente |

---

## 📞 Contacto y Referencias

- **Repositorio:** https://gitlab.com/olvidata/ShowroomGriffin
- **Branch principal:** main
- **Workspace local:** `C:\Sistemas\ShowroomGriffin\`
- **IDE:** Visual Studio Community 2026 (18.7.0-insiders)
- **Terminal:** PowerShell

---

## 📝 Notas Adicionales

### Decisiones Técnicas Previas

1. **Uso de MySQL en lugar de SQL Server:**
   - Justificación: hosting compartido económico.
   - Impacto: `RowVersion` para concurrencia optimista se gestiona manualmente (MySQL no tiene rowversion auto-generado).

2. **Clean Architecture sin Repository Pattern explícito:**
   - Los servicios acceden directamente a `AppDbContext`.
   - Justificación: proyecto de tamaño medio, no se justifica la abstracción adicional.

3. **Soft Delete global:**
   - Implementado vía middleware `SoftDestroyMiddleware` que inyecta filtro `IsDeleted == false` en todos los queries.
   - Permite recuperación de datos sin borrado físico.

4. **Logging con Serilog:**
   - Configurado en `appsettings.{Environment}.json`.
   - Sinks: Console + File (carpeta `/Logs`).
   - Bootstrap logger para capturar errores de startup.

5. **QuestPDF para generación de PDFs:**
   - Licencia: Community (gratuita para uso no comercial o comercial de bajo volumen).
   - Uso: generación de remitos, reportes de ventas/compras.

---

## 🔧 Configuración de Entorno

### Variables de Entorno (appsettings.json)

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=showroomgriffin;User=root;Password=***;"
  },
  "Serilog": {
    "MinimumLevel": "Information",
    "WriteTo": [
      { "Name": "Console" },
      {
        "Name": "File",
        "Args": {
          "path": "Logs/log-.txt",
          "rollingInterval": "Day"
        }
      }
    ]
  },
  "RateLimiting": {
    "PermitLimit": 100,
    "Window": "00:01:00"
  }
}
```

### Migraciones Aplicadas

| # | Nombre | Fecha | Descripción |
|---|--------|-------|-------------|
| **M1** | `M1_AddMaestrosComerciales` | 2026-04-16 | Creación inicial de tablas (Productos, Ventas, Compras, Stock, Maestros) |

### Migraciones Pendientes (Feature Actual)

| # | Nombre | Estado | Riesgo |
|---|--------|--------|--------|
| **M2** | `RefactorProductoMarcaModelo` | ⏳ Pendiente | 🔴 Alto |
| **M3** | `AgregarAnotacionesVenta` | ⏳ Pendiente | 🟢 Bajo |
| **M4** | `AgregarVentaCambio` | ⏳ Pendiente | 🟡 Medio |
| **M5** | `AgregarTalleZapatilla` | ⏳ Pendiente | 🟢 Bajo |

---

**Fin del documento - Metadata**
