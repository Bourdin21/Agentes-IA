# 🛠️ Plan de Implementación Técnica - ShowroomGriffin
**Proyecto:** ShowroomGriffin  
**Agente:** Implementador  
**Fecha creación:** 2026-04-23  
**Última actualización:** 2026-04-23  

---

## 📋 ALCANCE FUNCIONAL RESUMIDO

| # | Funcionalidad | Tipo | Prioridad | Riesgo |
|---|---------------|------|-----------|--------|
| **R1** | Campo **Anotaciones** en Venta | Dato simple | 🟢 Alta | 🟢 Bajo |
| **R2** | **Modal Crear Cliente** desde Venta | Modal AJAX | 🟢 Alta | 🟢 Bajo |
| **R4** | **Autocompletar importe** en Agregar Pago | UX simple | 🟢 Media | 🟢 Bajo |
| **R11** | **Maestro Talles** predefinidos (Adultos/Niños) | Maestro | 🟢 Media | 🟢 Bajo |
| **R3** | **Combos anidados** en Ventas (Marca→Modelo→Color→Talle) | UX compleja | 🟡 Alta | 🟡 Medio |
| **R5** | **Combos anidados** en Compras | UX compleja | 🟡 Alta | 🟡 Medio |
| **R6** | **Consulta Stock** rápida | Nueva vista | 🟡 Media | 🟢 Bajo |
| **R8** | **Rol Empleado** (Ventas/Cambios/Stock) | Autorización | 🟡 Alta | 🟢 Bajo |
| **R9** | **Importes editables** en Venta | UX sensible | 🔴 Alta | 🔴 Alto |
| **R7** | **Cambio/Devolución** de Ventas | Flujo complejo | 🔴 Alta | 🔴 Alto |
| **R10+R12** | **Refactor Modelo** (Marca/Modelo→Producto) | Migración EF | 🔴 **CRÍTICA** | 🔴 **MUY ALTO** |

**Estrategia de implementación:**  
Dividir en **3 fases** por nivel de riesgo:

- **FASE 1 (Riesgo Bajo):** R1, R2, R4, R11 → 2-3 días.
- **FASE 2 (Riesgo Medio):** R3, R5, R6, R8 → 4-5 días.
- **FASE 3 (Riesgo Alto):** R9, R7, R10+R12 → 6-8 días.

**Total estimado:** 12-16 días de desarrollo (sin contar diseño/QA).

---

## 🚀 FASE 1: FUNCIONALIDADES SIMPLES (Riesgo Bajo)

### ✅ R1: Campo Anotaciones en Venta

**Objetivo:**  
Agregar campo de texto libre `Anotaciones` en la entidad `Venta`.

#### Cambios por Capa

**1. Domain** (`ShowroomGriffin.Domain`)
- Archivo: `Entities/Ventas/Venta.cs`
- Cambio:
  ```csharp
  public string? Anotaciones { get; set; }
  ```

**2. Infrastructure** (`ShowroomGriffin.Infrastructure`)
- **Migración:** crear `M2_AgregarAnotacionesVenta`
  ```bash
  dotnet ef migrations add M2_AgregarAnotacionesVenta --project ShowroomGriffin.Infrastructure --startup-project ShowroomGriffin.Web
  ```
- **Configuración (opcional):** en `VentaConfiguration.cs`:
  ```csharp
  builder.Property(v => v.Anotaciones)
         .HasMaxLength(500)
         .IsRequired(false);
  ```

**3. Application** (`ShowroomGriffin.Application`)
- Archivo: `DTOs/Ventas/VentasViewModels.cs`
- Cambio: agregar propiedad `Anotaciones` en:
  - `VentaCrearViewModel`
  - `VentaEditarViewModel`
  - `VentaDetalleViewModel`

**4. Web** (`ShowroomGriffin.Web`)
- **Vistas:**
  - `Views/Ventas/Crear.cshtml`: agregar `<textarea>` para Anotaciones.
  - `Views/Ventas/Editar.cshtml`: agregar `<textarea>` para Anotaciones.
  - `Views/Ventas/Detalle.cshtml`: mostrar Anotaciones si tiene valor.

**Código de vista (ejemplo):**
```html
<div class="mb-3">
    <label asp-for="Anotaciones" class="form-label">Anotaciones</label>
    <textarea asp-for="Anotaciones" class="form-control" rows="3" maxlength="500" 
              placeholder="Ej: Cliente pidió envío urgente"></textarea>
    <span asp-validation-for="Anotaciones" class="text-danger"></span>
</div>
```

**Validación:**
- Longitud máxima: 500 caracteres (validación client-side con `maxlength` y server-side en ViewModel).

**Pruebas mínimas:**
- [ ] Crear venta con anotaciones → guardar → verificar en BD.
- [ ] Editar anotaciones de venta existente → verificar actualización.
- [ ] Ver detalle de venta → verificar que se muestran las anotaciones.

**Estimación:** 2 horas.

---

### ✅ R2: Modal Crear Cliente desde Venta

**Objetivo:**  
Permitir crear cliente desde un modal en las vistas Crear/Editar Venta, sin salir de la pantalla.

#### Cambios por Capa

**1. Web** (`ShowroomGriffin.Web`)

**a) Crear Partial View `_CrearClienteModal.cshtml`**

Ubicación: `Views/Clientes/_CrearClienteModal.cshtml`

```html
@model ShowroomGriffin.Application.DTOs.Maestros.ClienteCrearViewModel

<div class="modal fade" id="crearClienteModal" tabindex="-1" aria-labelledby="crearClienteModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="crearClienteModalLabel">Crear Cliente</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <form id="formCrearCliente">
                    <div class="mb-3">
                        <label for="Nombre" class="form-label">Nombre *</label>
                        <input type="text" class="form-control" id="Nombre" name="Nombre" required />
                        <span class="text-danger" id="errorNombre"></span>
                    </div>
                    <div class="mb-3">
                        <label for="Telefono" class="form-label">Teléfono</label>
                        <input type="text" class="form-control" id="Telefono" name="Telefono" />
                    </div>
                    <div class="mb-3">
                        <label for="WhatsApp" class="form-label">WhatsApp</label>
                        <input type="text" class="form-control" id="WhatsApp" name="WhatsApp" />
                    </div>
                    <div class="mb-3">
                        <label for="Direccion" class="form-label">Dirección</label>
                        <input type="text" class="form-control" id="Direccion" name="Direccion" />
                    </div>
                    <div class="mb-3">
                        <label for="Cuit" class="form-label">CUIT</label>
                        <input type="text" class="form-control" id="Cuit" name="Cuit" />
                        <span class="text-danger" id="errorCuit"></span>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-primary" id="btnGuardarCliente">Guardar</button>
            </div>
        </div>
    </div>
</div>
```

**b) Agregar endpoint AJAX en `ClientesController`**

Archivo: `Controllers/ClientesController.cs`

```csharp
[HttpPost]
public async Task<IActionResult> CrearDesdeVenta([FromBody] ClienteCrearViewModel model)
{
    if (!ModelState.IsValid)
        return BadRequest(new { success = false, errors = ModelState.Values.SelectMany(v => v.Errors).Select(e => e.ErrorMessage) });

    try
    {
        var clienteId = await _clienteService.CrearAsync(model);
        var cliente = await _clienteService.ObtenerPorIdAsync(clienteId);

        return Ok(new { 
            success = true, 
            clienteId = clienteId,
            clienteNombre = cliente.Nombre 
        });
    }
    catch (Exception ex)
    {
        return BadRequest(new { success = false, errors = new[] { ex.Message } });
    }
}
```

**c) JavaScript en Ventas**

Archivo: `Views/Ventas/Crear.cshtml` (y `Editar.cshtml`)

```html
@section Scripts {
    <partial name="_ValidationScriptsPartial" />

    <script>
        // Abrir modal
        $('#btnAbrirCrearCliente').click(function() {
            $('#crearClienteModal').modal('show');
        });

        // Guardar cliente
        $('#btnGuardarCliente').click(function() {
            var data = {
                nombre: $('#Nombre').val(),
                telefono: $('#Telefono').val(),
                whatsApp: $('#WhatsApp').val(),
                direccion: $('#Direccion').val(),
                cuit: $('#Cuit').val()
            };

            $.ajax({
                url: '@Url.Action("CrearDesdeVenta", "Clientes")',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function(response) {
                    if (response.success) {
                        // Agregar nueva opción al combo
                        $('#ClienteId').append($('<option>', {
                            value: response.clienteId,
                            text: response.clienteNombre,
                            selected: true
                        }));

                        // Cerrar modal y limpiar form
                        $('#crearClienteModal').modal('hide');
                        $('#formCrearCliente')[0].reset();

                        // Notificación (opcional)
                        toastr.success('Cliente creado exitosamente');
                    }
                },
                error: function(xhr) {
                    var errors = xhr.responseJSON.errors;
                    if (errors) {
                        $('#errorNombre').text('');
                        $('#errorCuit').text('');
                        errors.forEach(function(err) {
                            if (err.includes('Nombre')) $('#errorNombre').text(err);
                            if (err.includes('CUIT')) $('#errorCuit').text(err);
                        });
                    }
                }
            });
        });
    </script>
}
```

**d) Botón en la vista de Venta**

```html
<div class="mb-3">
    <label asp-for="ClienteId" class="form-label">Cliente</label>
    <div class="input-group">
        <select asp-for="ClienteId" class="form-select" asp-items="ViewBag.Clientes"></select>
        <button type="button" class="btn btn-outline-primary" id="btnAbrirCrearCliente">
            <i class="bi bi-plus-circle"></i> Crear Cliente
        </button>
    </div>
</div>

@await Html.PartialAsync("~/Views/Clientes/_CrearClienteModal.cshtml", new ClienteCrearViewModel())
```

**Pruebas mínimas:**
- [ ] Abrir modal desde Crear Venta → llenar form → guardar → verificar que cliente se agrega al combo y queda seleccionado.
- [ ] Validar error de CUIT duplicado → verificar que se muestra en modal sin cerrar.
- [ ] Verificar que el cliente se guarda en BD.

**Estimación:** 3 horas.

---

### ✅ R4: Autocompletar Importe de Pago

**Objetivo:**  
Al abrir el modal de "Agregar Pago", el campo "Importe" debe autocompletarse con el total pendiente de pago.

#### Cambios por Capa

**1. Web** (`ShowroomGriffin.Web`)

Archivo: `Views/Ventas/_AgregarPagoModal.cshtml` (o donde esté el modal de pago)

**JavaScript:**
```html
<script>
    $('#btnAgregarPago').click(function() {
        // Calcular total pendiente
        var totalVenta = parseFloat($('#Total').val()) || 0;
        var totalPagos = 0;

        // Sumar pagos ya registrados (si existen en la tabla)
        $('.pago-row').each(function() {
            totalPagos += parseFloat($(this).data('importe')) || 0;
        });

        var totalPendiente = totalVenta - totalPagos;

        // Autocompletar el campo Importe del modal
        $('#ImportePago').val(totalPendiente.toFixed(2));

        // Abrir modal
        $('#agregarPagoModal').modal('show');
    });
</script>
```

**Alternativa (si el valor viene del servidor):**

En `VentasController.Crear()` o `Editar()`, calcular el total pendiente:

```csharp
var totalPendiente = venta.Total - venta.Pagos.Sum(p => p.Importe);
ViewBag.TotalPendiente = totalPendiente;
```

En la vista:
```html
<script>
    $('#btnAbregarPago').click(function() {
        var totalPendiente = @ViewBag.TotalPendiente;
        $('#ImportePago').val(totalPendiente.toFixed(2));
        $('#agregarPagoModal').modal('show');
    });
</script>
```

**Pruebas mínimas:**
- [ ] Crear venta con total $10,000 → abrir modal de pago → verificar que Importe = $10,000.
- [ ] Agregar pago parcial de $5,000 → abrir modal de nuevo pago → verificar que Importe = $5,000.
- [ ] Venta totalmente paga → verificar que el botón "Agregar Pago" se deshabilita (opcional).

**Estimación:** 1 hora.

---

### ✅ R11: Maestro de Talles Predefinidos

**Objetivo:**  
Crear tabla `TalleZapatilla` con rangos predefinidos:
- Adultos: 34-46
- Niños: 22-33

#### Cambios por Capa

**1. Domain** (`ShowroomGriffin.Domain`)

Archivo: `Entities/Maestros/TalleZapatilla.cs` (nuevo)

```csharp
namespace ShowroomGriffin.Domain.Entities.Maestros;

public enum RangoTipoTalle
{
    Adulto = 1,
    Niño = 2
}

/// <summary>
/// Catálogo de talles de zapatillas predefinidos.
/// </summary>
public class TalleZapatilla : SoftDestroyable
{
    public RangoTipoTalle RangoTipo { get; set; }
    public int NumeroInicio { get; set; }
    public int NumeroFin { get; set; }
}
```

**2. Infrastructure** (`ShowroomGriffin.Infrastructure`)

**a) Configuración**

Archivo: `Data/Configurations/Maestros/TalleZapatillaConfiguration.cs` (nuevo)

```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using ShowroomGriffin.Domain.Entities.Maestros;

namespace ShowroomGriffin.Infrastructure.Data.Configurations.Maestros;

public class TalleZapatillaConfiguration : IEntityTypeConfiguration<TalleZapatilla>
{
    public void Configure(EntityTypeBuilder<TalleZapatilla> builder)
    {
        builder.ToTable("TallesZapatilla");

        builder.Property(t => t.RangoTipo)
               .HasConversion<int>()
               .IsRequired();

        builder.Property(t => t.NumeroInicio).IsRequired();
        builder.Property(t => t.NumeroFin).IsRequired();
    }
}
```

**b) Registrar en `AppDbContext`**

```csharp
public DbSet<TalleZapatilla> TallesZapatilla { get; set; } = null!;

protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    // ...
    modelBuilder.ApplyConfiguration(new TalleZapatillaConfiguration());
}
```

**c) Migración + Seed**

```bash
dotnet ef migrations add M3_AgregarTalleZapatilla --project ShowroomGriffin.Infrastructure --startup-project ShowroomGriffin.Web
```

En el método `Up()` de la migración, agregar seed manual (o en `SeedData.cs`):

```csharp
// En SeedData.cs
public static async Task SeedTallesZapatilla(AppDbContext context)
{
    if (await context.TallesZapatilla.AnyAsync()) return;

    var talles = new List<TalleZapatilla>
    {
        new() { RangoTipo = RangoTipoTalle.Adulto, NumeroInicio = 34, NumeroFin = 46, CreatedAt = DateTime.UtcNow },
        new() { RangoTipo = RangoTipoTalle.Niño, NumeroInicio = 22, NumeroFin = 33, CreatedAt = DateTime.UtcNow }
    };

    await context.TallesZapatilla.AddRangeAsync(talles);
    await context.SaveChangesAsync();
}

// Llamar en Program.cs (dentro del scope de seed):
await SeedData.SeedTallesZapatilla(context);
```

**3. Application** (opcional - si queremos CRUD)

Archivo: `Interfaces/ITalleZapatillaService.cs`

```csharp
public interface ITalleZapatillaService
{
    Task<List<TalleZapatillaViewModel>> ObtenerTodosAsync();
}
```

**4. Web** (opcional - CRUD para administrar talles)

Controller: `TallesZapatillaController.cs`

Vista: `Views/TallesZapatilla/Index.cshtml`

**Pruebas mínimas:**
- [ ] Ejecutar migración → verificar tabla `TallesZapatilla` creada.
- [ ] Ejecutar seed → verificar 2 registros insertados (Adulto 34-46, Niño 22-33).
- [ ] (Opcional) Acceder a `/TallesZapatilla` → verificar que se listan.

**Estimación:** 2 horas.

---

## 🎯 RESUMEN FASE 1

| Requerimiento | Estimación | Archivos Nuevos | Archivos Modificados | Migraciones |
|---------------|------------|-----------------|----------------------|-------------|
| **R1** | 2h | 0 | 4 (Venta.cs, VentasViewModels.cs, Crear/Editar/Detalle.cshtml) | M2_AgregarAnotacionesVenta |
| **R2** | 3h | 1 (_CrearClienteModal.cshtml) | 3 (ClientesController.cs, Crear/Editar.cshtml) | 0 |
| **R4** | 1h | 0 | 1 (_AgregarPagoModal.cshtml o JS en vista) | 0 |
| **R11** | 2h | 3 (TalleZapatilla.cs, Config, SeedData) | 2 (AppDbContext, Program.cs) | M3_AgregarTalleZapatilla |

**Total Fase 1:** 8 horas (~1 día de desarrollo).

**Bloqueadores:** Ninguno.

**Riesgo:** 🟢 Bajo.

---

## 🚀 FASE 2: FUNCIONALIDADES MEDIAS (Riesgo Medio)

### 🟡 R10+R12: REFACTOR DEL MODELO (Marca/Modelo a Producto)

**⚠️ ATENCIÓN:** Este es el cambio **MÁS CRÍTICO** y debe ejecutarse **ANTES** de R3 y R5 (combos anidados).

**Objetivo:**  
Mover las propiedades `Marca` y `Modelo` de `VarianteProducto` a `Producto`.

#### Por Qué Debe Ir Primero

Los combos anidados (R3, R5) dependen de la jerarquía: **Marca → Modelo → Color → Talle**.

Si `Marca` y `Modelo` están en `VarianteProducto`, el combo debe consultar:
- `SELECT DISTINCT Marca FROM VarianteProducto` → lento, redundante.
- `SELECT DISTINCT Modelo FROM VarianteProducto WHERE Marca = X` → idem.

Si `Marca` y `Modelo` están en `Producto`:
- `SELECT Marca FROM Producto GROUP BY Marca` → rápido, normalizado.
- `SELECT Modelo FROM Producto WHERE Marca = X` → idem.

**Decisión:** ejecutar R10+R12 al inicio de FASE 2, antes de R3/R5.

---

#### Cambios por Capa

**1. Domain** (`ShowroomGriffin.Domain`)

**a) Modificar `Producto.cs`**

```csharp
public class Producto : SoftDestroyable
{
    public string Nombre { get; set; } = string.Empty;
    public string Marca { get; set; } = string.Empty;        // NUEVO
    public string Modelo { get; set; } = string.Empty;       // NUEVO
    public int CategoriaId { get; set; }
    public int? SubgrupoId { get; set; }

    public Maestros.Categoria Categoria { get; set; } = null!;
    public Maestros.Subgrupo? Subgrupo { get; set; }
    public ICollection<VarianteProducto> Variantes { get; set; } = new List<VarianteProducto>();
}
```

**b) Modificar `VarianteProducto.cs`**

```csharp
public class VarianteProducto : SoftDestroyable
{
    public int ProductoId { get; set; }
    public decimal PrecioVenta { get; set; }
    public decimal? UltimoPrecioCompra { get; set; }
    public int StockMinimo { get; set; }
    public string? CodigoInterno { get; set; }
    public string? Sku { get; set; }
    public string? CodigoBarra { get; set; }

    // Atributos Ropa
    public string? Talle { get; set; }
    public string? Color { get; set; }
    // ELIMINADOS: public string? Marca { get; set; }
    // ELIMINADOS: public string? Modelo { get; set; }
    public string? Genero { get; set; }
    public string? Temporada { get; set; }

    // Atributos Zapatillas
    public string? Numero { get; set; }
    // ELIMINADO: public int? TipoPrecioZapatillaId { get; set; }

    [System.ComponentModel.DataAnnotations.ConcurrencyCheck]
    public byte[] RowVersion { get; set; } = Guid.NewGuid().ToByteArray();

    public Producto Producto { get; set; } = null!;
    public Stock.Stock Stock { get; set; } = null!;
    public ICollection<Compras.CompraDetalle> CompraDetalles { get; set; } = new List<Compras.CompraDetalle>();
    public ICollection<Ventas.VentaDetalle> VentaDetalles { get; set; } = new List<Ventas.VentaDetalle>();
}
```

**2. Infrastructure** (`ShowroomGriffin.Infrastructure`)

**a) Migración de Datos (CRÍTICO)**

```bash
dotnet ef migrations add M4_RefactorProductoMarcaModelo --project ShowroomGriffin.Infrastructure --startup-project ShowroomGriffin.Web
```

**Contenido del método `Up()`:**

```csharp
protected override void Up(MigrationBuilder migrationBuilder)
{
    // 1. Agregar columnas temporales en Producto
    migrationBuilder.AddColumn<string>(
        name: "Marca",
        table: "Productos",
        type: "varchar(100)",
        maxLength: 100,
        nullable: true);

    migrationBuilder.AddColumn<string>(
        name: "Modelo",
        table: "Productos",
        type: "varchar(100)",
        maxLength: 100,
        nullable: true);

    // 2. Script de migración de datos: agrupar variantes por (Marca, Modelo) y actualizar/crear Productos
    migrationBuilder.Sql(@"
        -- Actualizar Productos existentes con la primera Marca/Modelo de sus variantes
        UPDATE p
        SET p.Marca = (SELECT v.Marca FROM VarianteProducto v WHERE v.ProductoId = p.Id AND v.IsDeleted = 0 LIMIT 1),
            p.Modelo = (SELECT v.Modelo FROM VarianteProducto v WHERE v.ProductoId = p.Id AND v.IsDeleted = 0 LIMIT 1)
        FROM Productos p
        WHERE EXISTS (SELECT 1 FROM VarianteProducto v WHERE v.ProductoId = p.Id AND v.IsDeleted = 0);

        -- Para variantes huérfanas o con combinaciones Marca+Modelo diferentes al Producto padre,
        -- crear nuevos Productos agrupadores (REVISAR MANUALMENTE EN PRODUCCIÓN)
        -- Este script es un ejemplo; debe ajustarse según la lógica de negocio real.
    ");

    // 3. Hacer NOT NULL las columnas (después de migrar datos)
    migrationBuilder.AlterColumn<string>(
        name: "Marca",
        table: "Productos",
        type: "varchar(100)",
        maxLength: 100,
        nullable: false);

    migrationBuilder.AlterColumn<string>(
        name: "Modelo",
        table: "Productos",
        type: "varchar(100)",
        maxLength: 100,
        nullable: false);

    // 4. Eliminar columnas de VarianteProducto
    migrationBuilder.DropColumn(name: "Marca", table: "VarianteProducto");
    migrationBuilder.DropColumn(name: "Modelo", table: "VarianteProducto");
    migrationBuilder.DropColumn(name: "TipoPrecioZapatillaId", table: "VarianteProducto");

    // 5. Actualizar índices (si existen)
    // Ejemplo: crear índice compuesto en Producto (Marca, Modelo)
    migrationBuilder.CreateIndex(
        name: "IX_Productos_Marca_Modelo",
        table: "Productos",
        columns: new[] { "Marca", "Modelo" });
}
```

**⚠️ IMPORTANTE - Script de Validación Previa (ejecutar ANTES de aplicar la migración en producción):**

```sql
-- Verificar que no hay variantes sin Marca o Modelo
SELECT COUNT(*) AS VariantesSinMarca FROM VarianteProducto WHERE Marca IS NULL OR Marca = '';
SELECT COUNT(*) AS VariantesSinModelo FROM VarianteProducto WHERE Modelo IS NULL OR Modelo = '';

-- Si el resultado es > 0, corregir manualmente antes de migrar.

-- Verificar agrupaciones: cuántos productos se crearían por cada combinación Marca+Modelo
SELECT Marca, Modelo, COUNT(*) AS CantidadVariantes
FROM VarianteProducto
WHERE IsDeleted = 0
GROUP BY Marca, Modelo
ORDER BY CantidadVariantes DESC;

-- Verificar productos actuales vs combinaciones en variantes
SELECT p.Id AS ProductoId, p.Nombre, 
       COUNT(DISTINCT CONCAT(v.Marca, '|', v.Modelo)) AS CombinacionesMarcaModelo
FROM Productos p
INNER JOIN VarianteProducto v ON v.ProductoId = p.Id
WHERE p.IsDeleted = 0 AND v.IsDeleted = 0
GROUP BY p.Id, p.Nombre
HAVING CombinacionesMarcaModelo > 1;

-- Si hay productos con más de 1 combinación Marca+Modelo, revisar manualmente.
```

**b) Actualizar Configurations**

`ProductoConfiguration.cs`:
```csharp
builder.Property(p => p.Marca)
       .HasMaxLength(100)
       .IsRequired();

builder.Property(p => p.Modelo)
       .HasMaxLength(100)
       .IsRequired();

builder.HasIndex(p => new { p.Marca, p.Modelo });
```

`VarianteProductoConfiguration.cs`:
```csharp
// ELIMINAR configuraciones de Marca, Modelo, TipoPrecioZapatillaId
```

**3. Application** (`ShowroomGriffin.Application`)

**a) Actualizar ViewModels**

`DTOs/Productos/ProductosViewModels.cs`:
```csharp
public class ProductoCrearViewModel
{
    [Required(ErrorMessage = "El nombre es obligatorio")]
    public string Nombre { get; set; } = string.Empty;

    [Required(ErrorMessage = "La marca es obligatoria")]  // NUEVO
    public string Marca { get; set; } = string.Empty;

    [Required(ErrorMessage = "El modelo es obligatorio")] // NUEVO
    public string Modelo { get; set; } = string.Empty;

    [Required(ErrorMessage = "La categoría es obligatoria")]
    public int CategoriaId { get; set; }

    public int? SubgrupoId { get; set; }
}

public class VarianteProductoCrearViewModel
{
    [Required]
    public int ProductoId { get; set; }

    // ELIMINADOS: Marca, Modelo

    public string? Talle { get; set; }
    public string? Color { get; set; }
    public string? Numero { get; set; }
    public string? Genero { get; set; }
    public string? Temporada { get; set; }

    [Required]
    public decimal PrecioVenta { get; set; }

    public int StockMinimo { get; set; }
    public string? CodigoInterno { get; set; }
    public string? Sku { get; set; }
    public string? CodigoBarra { get; set; }
}
```

**b) Actualizar Services**

`IProductoService.cs`:
```csharp
Task<List<string>> ObtenerMarcasAsync();                                          // NUEVO
Task<List<string>> ObtenerModelosPorMarcaAsync(string marca);                    // NUEVO
Task<List<ProductoListViewModel>> ObtenerPorMarcaModeloAsync(string marca, string modelo); // NUEVO
```

`ProductoService.cs`:
```csharp
public async Task<List<string>> ObtenerMarcasAsync()
{
    return await _context.Productos
        .Where(p => !p.IsDeleted)
        .Select(p => p.Marca)
        .Distinct()
        .OrderBy(m => m)
        .ToListAsync();
}

public async Task<List<string>> ObtenerModelosPorMarcaAsync(string marca)
{
    return await _context.Productos
        .Where(p => !p.IsDeleted && p.Marca == marca)
        .Select(p => p.Modelo)
        .Distinct()
        .OrderBy(m => m)
        .ToListAsync();
}
```

**4. Web** (`ShowroomGriffin.Web`)

**a) Actualizar vistas de Producto**

`Views/Productos/Crear.cshtml`:
```html
<div class="mb-3">
    <label asp-for="Marca" class="form-label">Marca</label>
    <input asp-for="Marca" class="form-control" />
    <span asp-validation-for="Marca" class="text-danger"></span>
</div>

<div class="mb-3">
    <label asp-for="Modelo" class="form-label">Modelo</label>
    <input asp-for="Modelo" class="form-control" />
    <span asp-validation-for="Modelo" class="text-danger"></span>
</div>
```

`Views/Productos/Index.cshtml`:
```html
<table class="table">
    <thead>
        <tr>
            <th>Nombre</th>
            <th>Marca</th>        <!-- NUEVO -->
            <th>Modelo</th>       <!-- NUEVO -->
            <th>Categoría</th>
            <th>Acciones</th>
        </tr>
    </thead>
    <tbody>
        @foreach (var item in Model)
        {
            <tr>
                <td>@item.Nombre</td>
                <td>@item.Marca</td>
                <td>@item.Modelo</td>
                <td>@item.CategoriaNombre</td>
                <td>...</td>
            </tr>
        }
    </tbody>
</table>
```

**b) Actualizar vistas de Variante**

`Views/Variantes/Crear.cshtml`:
```html
<!-- ELIMINAR campos Marca y Modelo -->

<div class="mb-3">
    <label asp-for="ProductoId" class="form-label">Producto (Marca + Modelo)</label>
    <select asp-for="ProductoId" class="form-select" asp-items="ViewBag.Productos">
        <option value="">-- Seleccionar Producto --</option>
    </select>
    <span asp-validation-for="ProductoId" class="text-danger"></span>
    <small class="text-muted">
        Seleccionar el producto base. La marca y modelo ya están definidos en el producto.
    </small>
</div>
```

En el controller `VariantesController.Crear()`:
```csharp
ViewBag.Productos = await _context.Productos
    .Where(p => !p.IsDeleted)
    .Select(p => new SelectListItem
    {
        Value = p.Id.ToString(),
        Text = $"{p.Marca} - {p.Modelo} ({p.Categoria.Nombre})"
    })
    .ToListAsync();
```

**Pruebas mínimas:**
- [ ] **CRÍTICO:** Ejecutar script de validación previa en base de datos de desarrollo.
- [ ] **CRÍTICO:** Hacer backup de la base de datos antes de aplicar la migración.
- [ ] Aplicar migración M4 → verificar que no hay errores.
- [ ] Verificar que todos los productos tienen Marca y Modelo (ninguno NULL).
- [ ] Crear nuevo Producto con Marca/Modelo → verificar que se guarda.
- [ ] Crear nueva Variante vinculada al producto → verificar que NO tiene campos Marca/Modelo.
- [ ] Verificar que grilla de Productos muestra Marca y Modelo.
- [ ] Verificar que filtros funcionan correctamente.

**Estimación:** 8 horas (incluye validaciones, backup, rollback plan).

**Riesgo:** 🔴 **MUY ALTO** (migración de datos).

**Plan de Rollback:**
1. Backup de BD antes de migración.
2. Script `Down()` de la migración debe revertir cambios:
   - Re-agregar columnas Marca/Modelo en VarianteProducto.
   - Copiar valores desde Producto a cada Variante.
   - Eliminar columnas de Producto.

---

### 🟡 R3 + R5: Combos Anidados en Ventas y Compras

**Objetivo:**  
Reemplazar selector de variantes por combos en cascada: **Marca → Modelo → Color → Talle**.

**Prerrequisito:** R10+R12 (Refactor Modelo) debe estar aplicado.

#### Flujo de Usuario

1. Usuario selecciona **Marca** (ej. "Nike").
2. Se cargan dinámicamente los **Modelos** de Nike (ej. "Air Max", "Revolution").
3. Usuario selecciona **Modelo** (ej. "Air Max").
4. Se cargan dinámicamente los **Colores** disponibles para "Nike Air Max" (ej. "Negro", "Blanco").
5. Usuario selecciona **Color** (ej. "Negro").
6. Se cargan dinámicamente los **Talles** disponibles para "Nike Air Max Negro" **con stock > 0** (solo en Ventas).
7. Usuario selecciona **Talle** (ej. "39") → se identifica la `VarianteProducto` y se agrega al detalle.

#### Cambios por Capa

**1. Application** (`ShowroomGriffin.Application`)

**Nuevos métodos en `IProductoService`:**

```csharp
Task<List<string>> ObtenerMarcasAsync();
Task<List<string>> ObtenerModelosPorMarcaAsync(string marca);
Task<List<VarianteCombosViewModel>> ObtenerColoresPorMarcaModeloAsync(string marca, string modelo);
Task<List<VarianteCombosViewModel>> ObtenerTallesPorMarcaModeloColorAsync(string marca, string modelo, string color, bool soloConStock = false);
```

**DTO:**
```csharp
public class VarianteCombosViewModel
{
    public int VarianteId { get; set; }
    public string? Color { get; set; }
    public string? Talle { get; set; }
    public string? Numero { get; set; }
    public int Stock { get; set; }
    public decimal PrecioVenta { get; set; }
}
```

**Implementación en `ProductoService.cs`:**

```csharp
public async Task<List<VarianteCombosViewModel>> ObtenerColoresPorMarcaModeloAsync(string marca, string modelo)
{
    return await _context.Variantes
        .Include(v => v.Producto)
        .Include(v => v.Stock)
        .Where(v => !v.IsDeleted 
                 && v.Producto.Marca == marca 
                 && v.Producto.Modelo == modelo
                 && v.Color != null)
        .Select(v => new VarianteCombosViewModel
        {
            VarianteId = v.Id,
            Color = v.Color,
            Stock = v.Stock.Cantidad,
            PrecioVenta = v.PrecioVenta
        })
        .Distinct()
        .OrderBy(v => v.Color)
        .ToListAsync();
}

public async Task<List<VarianteCombosViewModel>> ObtenerTallesPorMarcaModeloColorAsync(
    string marca, string modelo, string color, bool soloConStock = false)
{
    var query = _context.Variantes
        .Include(v => v.Producto)
        .Include(v => v.Stock)
        .Where(v => !v.IsDeleted 
                 && v.Producto.Marca == marca 
                 && v.Producto.Modelo == modelo
                 && v.Color == color);

    if (soloConStock)
        query = query.Where(v => v.Stock.Cantidad > 0);

    return await query
        .Select(v => new VarianteCombosViewModel
        {
            VarianteId = v.Id,
            Talle = v.Talle,
            Numero = v.Numero,
            Stock = v.Stock.Cantidad,
            PrecioVenta = v.PrecioVenta
        })
        .OrderBy(v => v.Talle ?? v.Numero)
        .ToListAsync();
}
```

**2. Web** (`ShowroomGriffin.Web`)

**a) Endpoints AJAX en `ProductosController`:**

```csharp
[HttpGet]
public async Task<IActionResult> GetMarcas()
{
    var marcas = await _productoService.ObtenerMarcasAsync();
    return Json(marcas);
}

[HttpGet]
public async Task<IActionResult> GetModelosPorMarca(string marca)
{
    var modelos = await _productoService.ObtenerModelosPorMarcaAsync(marca);
    return Json(modelos);
}

[HttpGet]
public async Task<IActionResult> GetColoresPorMarcaModelo(string marca, string modelo)
{
    var colores = await _productoService.ObtenerColoresPorMarcaModeloAsync(marca, modelo);
    return Json(colores);
}

[HttpGet]
public async Task<IActionResult> GetTallesPorMarcaModeloColor(string marca, string modelo, string color, bool soloConStock = false)
{
    var talles = await _productoService.ObtenerTallesPorMarcaModeloColorAsync(marca, modelo, color, soloConStock);
    return Json(talles);
}
```

**b) HTML en `Views/Ventas/Crear.cshtml`:**

```html
<div class="row">
    <div class="col-md-3">
        <label class="form-label">Marca</label>
        <select id="cboMarca" class="form-select">
            <option value="">-- Seleccionar --</option>
        </select>
    </div>
    <div class="col-md-3">
        <label class="form-label">Modelo</label>
        <select id="cboModelo" class="form-select" disabled>
            <option value="">-- Seleccionar Marca --</option>
        </select>
    </div>
    <div class="col-md-3">
        <label class="form-label">Color</label>
        <select id="cboColor" class="form-select" disabled>
            <option value="">-- Seleccionar Modelo --</option>
        </select>
    </div>
    <div class="col-md-3">
        <label class="form-label">Talle/Número</label>
        <select id="cboTalle" class="form-select" disabled>
            <option value="">-- Seleccionar Color --</option>
        </select>
    </div>
</div>
<div class="mt-2">
    <button type="button" id="btnAgregarDetalle" class="btn btn-primary" disabled>
        <i class="bi bi-plus-circle"></i> Agregar Producto
    </button>
</div>
```

**c) JavaScript (en la misma vista o archivo separado):**

```javascript
// Cargar marcas al iniciar
$(document).ready(function() {
    cargarMarcas();
});

function cargarMarcas() {
    $.get('@Url.Action("GetMarcas", "Productos")', function(data) {
        $('#cboMarca').empty().append('<option value="">-- Seleccionar --</option>');
        data.forEach(function(marca) {
            $('#cboMarca').append($('<option>', { value: marca, text: marca }));
        });
    });
}

// Al cambiar Marca → cargar Modelos
$('#cboMarca').change(function() {
    var marca = $(this).val();
    $('#cboModelo, #cboColor, #cboTalle').prop('disabled', true).empty();
    $('#btnAgregarDetalle').prop('disabled', true);

    if (!marca) return;

    $.get('@Url.Action("GetModelosPorMarca", "Productos")', { marca: marca }, function(data) {
        $('#cboModelo').prop('disabled', false).append('<option value="">-- Seleccionar --</option>');
        data.forEach(function(modelo) {
            $('#cboModelo').append($('<option>', { value: modelo, text: modelo }));
        });
    });
});

// Al cambiar Modelo → cargar Colores
$('#cboModelo').change(function() {
    var marca = $('#cboMarca').val();
    var modelo = $(this).val();
    $('#cboColor, #cboTalle').prop('disabled', true).empty();
    $('#btnAgregarDetalle').prop('disabled', true);

    if (!modelo) return;

    $.get('@Url.Action("GetColoresPorMarcaModelo", "Productos")', 
        { marca: marca, modelo: modelo }, 
        function(data) {
            $('#cboColor').prop('disabled', false).append('<option value="">-- Seleccionar --</option>');

            // Agrupar por color (sin duplicados)
            var coloresUnicos = [...new Set(data.map(item => item.color))];
            coloresUnicos.forEach(function(color) {
                $('#cboColor').append($('<option>', { value: color, text: color }));
            });
        });
});

// Al cambiar Color → cargar Talles (solo con stock en Ventas)
$('#cboColor').change(function() {
    var marca = $('#cboMarca').val();
    var modelo = $('#cboModelo').val();
    var color = $(this).val();
    $('#cboTalle').prop('disabled', true).empty();
    $('#btnAgregarDetalle').prop('disabled', true);

    if (!color) return;

    $.get('@Url.Action("GetTallesPorMarcaModeloColor", "Productos")', 
        { marca: marca, modelo: modelo, color: color, soloConStock: true }, 
        function(data) {
            if (data.length === 0) {
                $('#cboTalle').append('<option value="">Sin stock disponible</option>');
                return;
            }

            $('#cboTalle').prop('disabled', false).append('<option value="">-- Seleccionar --</option>');
            data.forEach(function(item) {
                var displayText = (item.talle || item.numero) + ' (Stock: ' + item.stock + ')';
                $('#cboTalle').append($('<option>', { 
                    value: item.varianteId, 
                    text: displayText,
                    'data-precio': item.precioVenta
                }));
            });
        });
});

// Al seleccionar Talle → habilitar botón Agregar
$('#cboTalle').change(function() {
    $('#btnAgregarDetalle').prop('disabled', $(this).val() === '');
});

// Al hacer clic en Agregar Producto
$('#btnAgregarDetalle').click(function() {
    var varianteId = $('#cboTalle').val();
    var precio = $('#cboTalle option:selected').data('precio');
    var marca = $('#cboMarca').val();
    var modelo = $('#cboModelo').val();
    var color = $('#cboColor').val();
    var talle = $('#cboTalle option:selected').text().split(' (Stock')[0];

    // Aquí agregar a la tabla de detalles (lógica existente de tu proyecto)
    agregarDetalleATabla(varianteId, marca, modelo, color, talle, precio);

    // Reset de combos
    $('#cboMarca, #cboModelo, #cboColor, #cboTalle').val('');
    $('#cboModelo, #cboColor, #cboTalle').prop('disabled', true);
    $('#btnAgregarDetalle').prop('disabled', true);
});

function agregarDetalleATabla(varianteId, marca, modelo, color, talle, precio) {
    // Implementar según la lógica actual del proyecto
    // Ejemplo:
    var row = `
        <tr>
            <td>${marca} ${modelo} - ${color} ${talle}</td>
            <td><input type="number" class="form-control cantidad" value="1" min="1" /></td>
            <td><input type="number" class="form-control precio" value="${precio}" step="0.01" /></td>
            <td class="subtotal">${precio}</td>
            <td><button type="button" class="btn btn-sm btn-danger eliminar-detalle">Eliminar</button></td>
            <input type="hidden" name="Detalles[].VarianteProductoId" value="${varianteId}" />
        </tr>
    `;
    $('#tbodyDetalles').append(row);
    calcularTotales();
}
```

**d) Para Compras:** exactamente igual, pero en `CompraCrear.cshtml` y con `soloConStock: false`.

**Pruebas mínimas:**
- [ ] Seleccionar Marca → verificar que se cargan Modelos.
- [ ] Seleccionar Modelo → verificar que se cargan Colores.
- [ ] Seleccionar Color → verificar que se cargan Talles con stock > 0 (en Ventas).
- [ ] Seleccionar Talle → verificar que se habilita botón Agregar.
- [ ] Agregar producto → verificar que se agrega a la tabla de detalles con datos correctos.
- [ ] Verificar que en Compras se muestran todos los talles (sin filtro de stock).

**Estimación:** 6 horas (R3 + R5 juntos).

---

### 🟡 R6: Pantalla Consulta Stock Rápida

**Objetivo:**  
Vista de solo lectura para consultar stock con filtros por Marca/Modelo/Talle.

#### Cambios por Capa

**1. Web** (`ShowroomGriffin.Web`)

**a) Controller:**

```csharp
public class StockController : Controller
{
    private readonly IStockService _stockService;

    [Authorize(Policy = "RequireVendedor")] // Cambiar a RequireEmpleado después de R8
    public async Task<IActionResult> ConsultaRapida(string? marca, string? modelo, string? talle)
    {
        var filtro = new StockFiltroViewModel
        {
            Marca = marca,
            Modelo = modelo,
            Talle = talle
        };

        var stock = await _stockService.ObtenerStockConFiltroAsync(filtro);

        ViewBag.Marcas = await _stockService.ObtenerMarcasAsync();

        return View(stock);
    }
}
```

**b) Vista `Views/Stock/ConsultaRapida.cshtml`:**

```html
@model List<ShowroomGriffin.Application.DTOs.Stock.StockViewModel>

<div class="container mt-4">
    <h2>Consulta Rápida de Stock</h2>

    <form method="get" class="row g-3 mb-4">
        <div class="col-md-3">
            <label class="form-label">Marca</label>
            <select name="marca" class="form-select">
                <option value="">-- Todas --</option>
                @foreach (var marca in ViewBag.Marcas)
                {
                    <option value="@marca" selected="@(marca == ViewBag.MarcaSeleccionada)">@marca</option>
                }
            </select>
        </div>
        <div class="col-md-3">
            <label class="form-label">Modelo</label>
            <input type="text" name="modelo" class="form-control" value="@ViewBag.ModeloSeleccionado" />
        </div>
        <div class="col-md-3">
            <label class="form-label">Talle/Número</label>
            <input type="text" name="talle" class="form-control" value="@ViewBag.TalleSeleccionado" />
        </div>
        <div class="col-md-3 d-flex align-items-end">
            <button type="submit" class="btn btn-primary w-100">
                <i class="bi bi-search"></i> Buscar
            </button>
        </div>
    </form>

    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>Marca</th>
                <th>Modelo</th>
                <th>Color</th>
                <th>Talle/Número</th>
                <th>Stock Actual</th>
                <th>Stock Mínimo</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
            @foreach (var item in Model)
            {
                var cssClass = item.Cantidad < item.StockMinimo ? "table-danger" : "";
                <tr class="@cssClass">
                    <td>@item.Marca</td>
                    <td>@item.Modelo</td>
                    <td>@item.Color</td>
                    <td>@item.Talle</td>
                    <td><strong>@item.Cantidad</strong></td>
                    <td>@item.StockMinimo</td>
                    <td>
                        @if (item.Cantidad < item.StockMinimo)
                        {
                            <span class="badge bg-danger">Bajo Stock</span>
                        }
                        else if (item.Cantidad == 0)
                        {
                            <span class="badge bg-secondary">Sin Stock</span>
                        }
                        else
                        {
                            <span class="badge bg-success">OK</span>
                        }
                    </td>
                </tr>
            }
        </tbody>
    </table>

    @if (!Model.Any())
    {
        <div class="alert alert-info">
            No se encontraron resultados con los filtros aplicados.
        </div>
    }
</div>
```

**Pruebas mínimas:**
- [ ] Acceder sin filtros → verificar que muestra todo el stock.
- [ ] Filtrar por Marca → verificar resultados.
- [ ] Filtrar por Modelo → verificar resultados.
- [ ] Verificar que filas con stock < mínimo se resaltan en rojo.

**Estimación:** 3 horas.

---

### 🟡 R8: Rol Empleado

**Objetivo:**  
Crear rol `Empleado` con acceso solo a Ventas, Cambios y Stock (consulta).

#### Cambios por Capa

**1. Infrastructure** (`ShowroomGriffin.Infrastructure`)

Archivo: `Data/SeedData.cs`

```csharp
public const string RolEmpleado = "Empleado";

public static async Task SeedRoles(RoleManager<IdentityRole> roleManager)
{
    string[] roles = { RolSuperUsuario, RolAdministrador, RolVendedor, RolEmpleado };

    foreach (var roleName in roles)
    {
        if (!await roleManager.RoleExistsAsync(roleName))
        {
            await roleManager.CreateAsync(new IdentityRole(roleName));
        }
    }
}
```

**2. Web** (`ShowroomGriffin.Web`)

**a) Program.cs:**

```csharp
builder.Services.AddAuthorization(options =>
{
    // ... policies existentes

    options.AddPolicy("RequireEmpleado",
        policy => policy.RequireRole(
            SeedData.RolSuperUsuario, 
            SeedData.RolAdministrador, 
            SeedData.RolVendedor, 
            SeedData.RolEmpleado));
});
```

**b) Decorar Controllers:**

```csharp
// VentasController
[Authorize(Policy = "RequireEmpleado")]
public class VentasController : Controller { ... }

// VentaCambiosController (cuando se implemente R7)
[Authorize(Policy = "RequireEmpleado")]
public class VentaCambiosController : Controller { ... }

// StockController (solo ConsultaRapida)
[Authorize(Policy = "RequireEmpleado")]
public IActionResult ConsultaRapida(...) { ... }

// Ajustar los métodos de ajuste de stock para RequireAdministracion
[Authorize(Policy = "RequireAdministracion")]
public IActionResult Ajustar(...) { ... }
```

**c) Menú de navegación (`_Layout.cshtml`):**

```html
@if (User.IsInRole(SeedData.RolEmpleado) || User.IsInRole(SeedData.RolVendedor))
{
    <li class="nav-item">
        <a class="nav-link" asp-controller="Ventas" asp-action="Index">Ventas</a>
    </li>
    <li class="nav-item">
        <a class="nav-link" asp-controller="Stock" asp-action="ConsultaRapida">Consulta Stock</a>
    </li>
}

@if (User.IsInRole(SeedData.RolAdministrador) || User.IsInRole(SeedData.RolSuperUsuario))
{
    <!-- Menús de Compras, Productos, Maestros, etc. -->
}
```

**Pruebas mínimas:**
- [ ] Crear usuario con rol Empleado.
- [ ] Loguear como Empleado → verificar acceso a Ventas.
- [ ] Verificar acceso a Consulta Stock.
- [ ] Verificar denegación de acceso a Compras.
- [ ] Verificar denegación de acceso a Productos/Variantes.
- [ ] Verificar denegación de acceso a Maestros.

**Estimación:** 2 horas.

---

## 🎯 RESUMEN FASE 2

| Requerimiento | Estimación | Riesgo | Bloqueantes |
|---------------|------------|--------|-------------|
| **R10+R12** | 8h | 🔴 Muy Alto | Ninguno (DEBE IR PRIMERO) |
| **R3+R5** | 6h | 🟡 Medio | R10+R12 |
| **R6** | 3h | 🟢 Bajo | Ninguno |
| **R8** | 2h | 🟢 Bajo | Ninguno |

**Total Fase 2:** 19 horas (~2.5 días).

**Orden de ejecución:**
1. R10+R12 (CRÍTICO, bloquea R3/R5).
2. R3+R5 (en paralelo después de R10+R12).
3. R6 (en paralelo).
4. R8 (al final).

---

## 🚀 FASE 3: FUNCIONALIDADES COMPLEJAS (Riesgo Alto)

### 🔴 R9: Importes Editables en Venta

**Objetivo:**  
Permitir edición manual de `PrecioUnitario`, `Subtotal` y `Total`, aunque se calculen automáticamente.

#### Cambios por Capa

**1. Application** (`ShowroomGriffin.Application`)

**a) ViewModel:**

```csharp
public class VentaDetalleViewModel
{
    public int VarianteProductoId { get; set; }
    public int Cantidad { get; set; }
    public decimal PrecioUnitario { get; set; }
    public decimal Subtotal { get; set; }

    // Nuevo flag para indicar si el precio fue editado manualmente
    public bool PrecioEditadoManualmente { get; set; }
}

public class VentaCrearViewModel
{
    // ...
    public decimal Subtotal { get; set; }
    public decimal Total { get; set; }

    // Flag para indicar si los importes fueron editados manualmente
    public bool ImportesEditadosManualmente { get; set; }
}
```

**b) Service:**

```csharp
public async Task<int> CrearAsync(VentaCrearViewModel model)
{
    // Validar coherencia de importes
    if (!ValidarCoherenciaImportes(model))
    {
        _logger.LogWarning("Usuario {UserId} creó venta con importes editados manualmente. Total: {Total}",
            model.VendedorUserId, model.Total);
    }

    // ... resto de la lógica
}

private bool ValidarCoherenciaImportes(VentaCrearViewModel model)
{
    var subtotalCalculado = model.Detalles.Sum(d => d.Cantidad * d.PrecioUnitario);
    var totalCalculado = subtotalCalculado - model.DescuentoMonto;

    // Tolerancia de 0.01 por redondeos
    return Math.Abs(model.Subtotal - subtotalCalculado) < 0.01 &&
           Math.Abs(model.Total - totalCalculado) < 0.01;
}
```

**2. Web** (`ShowroomGriffin.Web`)

**a) Vista `Crear/Editar.cshtml`:**

```html
<div class="mb-3">
    <label class="form-label">Subtotal</label>
    <div class="input-group">
        <span class="input-group-text">$</span>
        <input type="number" id="txtSubtotal" asp-for="Subtotal" class="form-control" step="0.01" />
        <button type="button" class="btn btn-outline-secondary" id="btnRecalcularSubtotal">
            <i class="bi bi-arrow-clockwise"></i> Recalcular
        </button>
    </div>
    <div id="alertaSubtotal" class="alert alert-warning mt-2" style="display: none;">
        ⚠️ Has editado manualmente el subtotal. Puede haber inconsistencias.
    </div>
</div>

<div class="mb-3">
    <label class="form-label">Total</label>
    <div class="input-group">
        <span class="input-group-text">$</span>
        <input type="number" id="txtTotal" asp-for="Total" class="form-control" step="0.01" />
        <button type="button" class="btn btn-outline-secondary" id="btnRecalcularTotal">
            <i class="bi bi-arrow-clockwise"></i> Recalcular
        </button>
    </div>
    <div id="alertaTotal" class="alert alert-warning mt-2" style="display: none;">
        ⚠️ Has editado manualmente el total. Puede haber inconsistencias.
    </div>
</div>

<input type="hidden" asp-for="ImportesEditadosManualmente" id="hdnImportesEditados" />
```

**b) JavaScript:**

```javascript
var subtotalAutomatico = true;
var totalAutomatico = true;

// Detectar edición manual de Subtotal
$('#txtSubtotal').on('input', function() {
    subtotalAutomatico = false;
    $('#alertaSubtotal').show();
    $('#hdnImportesEditados').val('true');
});

// Detectar edición manual de Total
$('#txtTotal').on('input', function() {
    totalAutomatico = false;
    $('#alertaTotal').show();
    $('#hdnImportesEditados').val('true');
});

// Recalcular Subtotal automáticamente
$('#btnRecalcularSubtotal').click(function() {
    calcularSubtotal();
    subtotalAutomatico = true;
    $('#alertaSubtotal').hide();
});

// Recalcular Total automáticamente
$('#btnRecalcularTotal').click(function() {
    calcularTotal();
    totalAutomatico = true;
    $('#alertaTotal').hide();
});

// Función de cálculo automático
function calcularSubtotal() {
    var subtotal = 0;
    $('.detalle-row').each(function() {
        var cantidad = parseFloat($(this).find('.cantidad').val()) || 0;
        var precio = parseFloat($(this).find('.precio').val()) || 0;
        subtotal += cantidad * precio;
    });
    $('#txtSubtotal').val(subtotal.toFixed(2));
    calcularTotal();
}

function calcularTotal() {
    var subtotal = parseFloat($('#txtSubtotal').val()) || 0;
    var descuento = parseFloat($('#txtDescuento').val()) || 0;
    var total = subtotal - descuento;
    $('#txtTotal').val(total.toFixed(2));
}

// Recalcular automáticamente si los flags están activados
$('.cantidad, .precio, #txtDescuento').on('input', function() {
    if (subtotalAutomatico) calcularSubtotal();
    if (totalAutomatico) calcularTotal();
});
```

**Pruebas mínimas:**
- [ ] Crear venta con cálculo automático → verificar que Subtotal y Total se calculan correctamente.
- [ ] Editar manualmente el Precio Unitario → verificar advertencia.
- [ ] Editar manualmente el Subtotal → verificar advertencia.
- [ ] Hacer clic en "Recalcular" → verificar que se restauran valores automáticos.
- [ ] Guardar venta con importes editados → verificar que se registra en log de Serilog.

**Estimación:** 4 horas.

**Riesgo:** 🔴 Alto (errores contables).

---

### 🔴 R7: Cambio/Devolución de Ventas

**Objetivo:**  
Buscar venta por fecha/cliente/producto y realizar cambio o devolución con ajuste de stock.

#### Cambios por Capa

**1. Domain** (`ShowroomGriffin.Domain`)

**a) Nueva entidad:**

```csharp
public enum EstadoVentaCambio
{
    Pendiente = 1,
    Confirmado = 2,
    Cancelado = 3
}

/// <summary>
/// Registro de cambio o devolución de una venta.
/// </summary>
public class VentaCambio : SoftDestroyable
{
    public int VentaOrigenId { get; set; }
    public int? VentaDestinoId { get; set; }   // null si es devolución pura
    public EstadoVentaCambio Estado { get; set; } = EstadoVentaCambio.Confirmado;
    public string Motivo { get; set; } = string.Empty;
    public DateTime FechaCambio { get; set; }
    public decimal? DiferenciaMonto { get; set; }  // positivo = cobro adicional, negativo = nota de crédito

    // Navegación
    public Venta VentaOrigen { get; set; } = null!;
    public Venta? VentaDestino { get; set; }
}
```

**b) Agregar estados a `EstadoVenta`:**

```csharp
public enum EstadoVenta
{
    Borrador = 1,
    Confirmada = 2,
    Cancelada = 3,
    Devuelta = 4,      // NUEVO
    Cambiada = 5       // NUEVO
}
```

**2. Infrastructure** (`ShowroomGriffin.Infrastructure`)

**a) Migración:**

```bash
dotnet ef migrations add M5_AgregarVentaCambio --project ShowroomGriffin.Infrastructure --startup-project ShowroomGriffin.Web
```

**b) Service:**

```csharp
public interface IVentaCambioService
{
    Task<int> RegistrarDevolucionAsync(int ventaId, List<int> variantesIds, string motivo);
    Task<int> RegistrarCambioAsync(int ventaId, List<CambioDetalleDto> cambios, string motivo);
}

public class VentaCambioService : IVentaCambioService
{
    public async Task<int> RegistrarDevolucionAsync(int ventaId, List<int> variantesIds, string motivo)
    {
        using var transaction = await _context.Database.BeginTransactionAsync();

        try
        {
            var venta = await _context.Ventas
                .Include(v => v.Detalles)
                .ThenInclude(d => d.VarianteProducto)
                .ThenInclude(vp => vp.Stock)
                .FirstOrDefaultAsync(v => v.Id == ventaId);

            if (venta == null) throw new InvalidOperationException("Venta no encontrada");
            if (venta.Estado != EstadoVenta.Confirmada) 
                throw new InvalidOperationException("Solo se pueden devolver ventas confirmadas");

            // 1. Reingresar stock de variantes devueltas
            foreach (var varianteId in variantesIds)
            {
                var detalle = venta.Detalles.FirstOrDefault(d => d.VarianteProductoId == varianteId);
                if (detalle == null) continue;

                detalle.VarianteProducto.Stock.Cantidad += detalle.Cantidad;

                // Registrar movimiento de stock
                await _stockService.RegistrarMovimientoAsync(new MovimientoStock
                {
                    VarianteProductoId = varianteId,
                    TipoMovimiento = TipoMovimiento.DevolucionVenta,
                    Cantidad = detalle.Cantidad,
                    Fecha = DateTime.UtcNow,
                    Observaciones = $"Devolución de Venta #{venta.NroVenta}"
                });
            }

            // 2. Crear registro de cambio
            var cambio = new VentaCambio
            {
                VentaOrigenId = ventaId,
                VentaDestinoId = null,
                Estado = EstadoVentaCambio.Confirmado,
                Motivo = motivo,
                FechaCambio = DateTime.UtcNow,
                DiferenciaMonto = 0,
                CreatedAt = DateTime.UtcNow
            };

            _context.VentaCambios.Add(cambio);

            // 3. Actualizar estado de venta
            venta.Estado = EstadoVenta.Devuelta;

            await _context.SaveChangesAsync();
            await transaction.CommitAsync();

            _logger.LogInformation("Devolución registrada: Venta {VentaId}, Variantes: {VariantesIds}", 
                ventaId, string.Join(",", variantesIds));

            return cambio.Id;
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }

    public async Task<int> RegistrarCambioAsync(int ventaId, List<CambioDetalleDto> cambios, string motivo)
    {
        using var transaction = await _context.Database.BeginTransactionAsync();

        try
        {
            var ventaOrigen = await _context.Ventas
                .Include(v => v.Detalles)
                .ThenInclude(d => d.VarianteProducto)
                .ThenInclude(vp => vp.Stock)
                .FirstOrDefaultAsync(v => v.Id == ventaId);

            if (ventaOrigen == null) throw new InvalidOperationException("Venta no encontrada");

            decimal diferenciaMonto = 0;

            // 1. Procesar cada cambio
            foreach (var cambio in cambios)
            {
                // Reingresar producto devuelto
                var detalleOrigen = ventaOrigen.Detalles.FirstOrDefault(d => d.VarianteProductoId == cambio.VarianteOrigenId);
                if (detalleOrigen != null)
                {
                    detalleOrigen.VarianteProducto.Stock.Cantidad += cambio.Cantidad;
                    await _stockService.RegistrarMovimientoAsync(new MovimientoStock
                    {
                        VarianteProductoId = cambio.VarianteOrigenId,
                        TipoMovimiento = TipoMovimiento.Cambio,
                        Cantidad = cambio.Cantidad,
                        Fecha = DateTime.UtcNow
                    });
                }

                // Egresar nuevo producto
                var varianteNueva = await _context.Variantes
                    .Include(v => v.Stock)
                    .FirstOrDefaultAsync(v => v.Id == cambio.VarianteDestinoId);

                if (varianteNueva == null) throw new InvalidOperationException("Variante destino no encontrada");
                if (varianteNueva.Stock.Cantidad < cambio.Cantidad) 
                    throw new InvalidOperationException("Stock insuficiente para el cambio");

                varianteNueva.Stock.Cantidad -= cambio.Cantidad;

                // Calcular diferencia de monto
                diferenciaMonto += (varianteNueva.PrecioVenta - (detalleOrigen?.PrecioUnitario ?? 0)) * cambio.Cantidad;
            }

            // 2. Crear registro de cambio
            var registroCambio = new VentaCambio
            {
                VentaOrigenId = ventaId,
                VentaDestinoId = null,  // TODO: crear nueva venta si es un cambio completo
                Estado = EstadoVentaCambio.Confirmado,
                Motivo = motivo,
                FechaCambio = DateTime.UtcNow,
                DiferenciaMonto = diferenciaMonto,
                CreatedAt = DateTime.UtcNow
            };

            _context.VentaCambios.Add(registroCambio);

            // 3. Actualizar estado de venta
            ventaOrigen.Estado = EstadoVenta.Cambiada;

            await _context.SaveChangesAsync();
            await transaction.CommitAsync();

            _logger.LogInformation("Cambio registrado: Venta {VentaId}, Diferencia: {Diferencia}", 
                ventaId, diferenciaMonto);

            return registroCambio.Id;
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }
}
```

**3. Web** (`ShowroomGriffin.Web`)

**a) Controller:**

```csharp
[Authorize(Policy = "RequireEmpleado")]
public class VentaCambiosController : Controller
{
    [HttpGet]
    public IActionResult BuscarVenta()
    {
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> BuscarVenta(DateTime? fechaDesde, DateTime? fechaHasta, string? cliente, string? producto)
    {
        var ventas = await _ventaService.BuscarParaCambioAsync(fechaDesde, fechaHasta, cliente, producto);
        return View("ResultadosBusqueda", ventas);
    }

    [HttpGet]
    public async Task<IActionResult> RegistrarDevolucion(int ventaId)
    {
        var venta = await _ventaService.ObtenerDetalleAsync(ventaId);
        return View(venta);
    }

    [HttpPost]
    public async Task<IActionResult> RegistrarDevolucion(int ventaId, List<int> variantesIds, string motivo)
    {
        try
        {
            await _ventaCambioService.RegistrarDevolucionAsync(ventaId, variantesIds, motivo);
            TempData["Success"] = "Devolución registrada exitosamente";
            return RedirectToAction("Index", "Ventas");
        }
        catch (Exception ex)
        {
            ModelState.AddModelError("", ex.Message);
            return View();
        }
    }
}
```

**b) Vistas:**

`Views/VentaCambios/BuscarVenta.cshtml`:
```html
<form method="post">
    <div class="row g-3">
        <div class="col-md-3">
            <label class="form-label">Fecha Desde</label>
            <input type="date" name="fechaDesde" class="form-control" />
        </div>
        <div class="col-md-3">
            <label class="form-label">Fecha Hasta</label>
            <input type="date" name="fechaHasta" class="form-control" />
        </div>
        <div class="col-md-3">
            <label class="form-label">Cliente</label>
            <input type="text" name="cliente" class="form-control" placeholder="Nombre del cliente" />
        </div>
        <div class="col-md-3">
            <label class="form-label">Producto</label>
            <input type="text" name="producto" class="form-control" placeholder="Marca o Modelo" />
        </div>
    </div>
    <button type="submit" class="btn btn-primary mt-3">Buscar</button>
</form>
```

**Pruebas mínimas:**
- [ ] Buscar venta por fecha → verificar resultados.
- [ ] Registrar devolución total → verificar que stock se reingresa.
- [ ] Registrar cambio parcial → verificar swap de stock.
- [ ] Verificar que estado de venta cambia a "Devuelta" o "Cambiada".
- [ ] Verificar que se registra en tabla `VentaCambios`.
- [ ] Verificar que la diferencia de monto se calcula correctamente.

**Estimación:** 10 horas.

**Riesgo:** 🔴 Muy Alto (lógica de negocio crítica, transacciones).

---

## 🎯 RESUMEN FASE 3

| Requerimiento | Estimación | Riesgo | Bloqueantes |
|---------------|------------|--------|-------------|
| **R9** | 4h | 🔴 Alto | Ninguno |
| **R7** | 10h | 🔴 Muy Alto | R8 (para policy RequireEmpleado) |

**Total Fase 3:** 14 horas (~2 días).

---

## 📊 RESUMEN GENERAL DEL PLAN

### Tiempos Estimados

| Fase | Requerimientos | Estimación | Riesgo |
|------|----------------|------------|--------|
| **FASE 1** | R1, R2, R4, R11 | 8h (~1 día) | 🟢 Bajo |
| **FASE 2** | R10+R12, R3+R5, R6, R8 | 19h (~2.5 días) | 🟡 Medio-Alto |
| **FASE 3** | R9, R7 | 14h (~2 días) | 🔴 Alto |
| **QA + Ajustes** | Pruebas, regresiones, bugs | 8h (~1 día) | - |

**Total:** 49 horas (~6.5 días de desarrollo).

---

### Migraciones EF

| # | Nombre | Descripción | Riesgo | Rollback |
|---|--------|-------------|--------|----------|
| **M2** | `AgregarAnotacionesVenta` | Agregar columna Anotaciones (nullable) | 🟢 Bajo | Drop column |
| **M3** | `AgregarTalleZapatilla` | Crear tabla + seed | 🟢 Bajo | Drop table |
| **M4** | `RefactorProductoMarcaModelo` | Mover Marca/Modelo + migrar datos | 🔴 **MUY ALTO** | Script manual |
| **M5** | `AgregarVentaCambio` | Crear tabla + FK | 🟡 Medio | Drop table |

**CRÍTICO:** M4 requiere backup de BD antes de aplicar.

---

### Archivos Nuevos

| Archivo | Capa | Tipo |
|---------|------|------|
| `TalleZapatilla.cs` | Domain | Entidad |
| `VentaCambio.cs` | Domain | Entidad |
| `_CrearClienteModal.cshtml` | Web | Vista parcial |
| `TallesZapatillaConfiguration.cs` | Infrastructure | EF Config |
| `VentaCambioConfiguration.cs` | Infrastructure | EF Config |
| `IVentaCambioService.cs` | Application | Interface |
| `VentaCambioService.cs` | Infrastructure | Service |
| `StockController.cs` | Web | Controller |
| `VentaCambiosController.cs` | Web | Controller |
| `Stock/ConsultaRapida.cshtml` | Web | Vista |
| `VentaCambios/BuscarVenta.cshtml` | Web | Vista |
| `VentaCambios/RegistrarDevolucion.cshtml` | Web | Vista |

**Total:** 12 archivos nuevos.

---

### Archivos Modificados (estimado)

- **Domain:** 3 archivos (Producto, VarianteProducto, Venta, enums).
- **Infrastructure:** 6 archivos (Configurations, SeedData, Services).
- **Application:** 4 archivos (ViewModels, Services).
- **Web:** 15 archivos (Controllers, Vistas, Program.cs).

**Total:** ~28 archivos modificados.

---

## ✅ CHECKLIST DE SALIDA

### Pre-implementación

- [ ] Backup de base de datos de producción.
- [ ] Crear branch `feature/refactor-modelo-combos-cambios`.
- [ ] Validar que `1-analista-funcional.md` está aprobado.

### Post-implementación (por fase)

**FASE 1:**
- [ ] Build exitoso (0 errores).
- [ ] Migraciones M2, M3 aplicadas.
- [ ] Pruebas mínimas de R1, R2, R4, R11 ejecutadas.
- [ ] Commit con mensaje: "FASE 1: Anotaciones, Modal Cliente, Autocompletar Pago, Talles".

**FASE 2:**
- [ ] **CRÍTICO:** Script de validación de M4 ejecutado.
- [ ] **CRÍTICO:** Backup pre-M4 realizado.
- [ ] Migración M4 aplicada exitosamente.
- [ ] Pruebas mínimas de R10+R12, R3, R5, R6, R8 ejecutadas.
- [ ] Verificar que NO hay regresiones en módulos existentes.
- [ ] Commit con mensaje: "FASE 2: Refactor Modelo, Combos Anidados, Consulta Stock, Rol Empleado".

**FASE 3:**
- [ ] Migración M5 aplicada.
- [ ] Pruebas mínimas de R9, R7 ejecutadas.
- [ ] Verificar logs de Serilog para edición manual de importes.
- [ ] Verificar transacciones de cambios/devoluciones (rollback en caso de error).
- [ ] Commit con mensaje: "FASE 3: Importes Editables, Cambios/Devoluciones".

**QA:**
- [ ] Suite de regresiones ejecutada (si existe en `/docs/qa/regresiones-manuales.yml`).
- [ ] Casos de prueba de R7 (cambios/devoluciones) ejecutados exhaustivamente.
- [ ] Build de Release exitoso.

**Merge:**
- [ ] Code review aprobado.
- [ ] Merge Request a `main` aprobado.
- [ ] Documentación actualizada en `/docs/ShowroomGriffin/definiciones/5-implementador.md`.

---

## 🚨 RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|-----------|
| **Migración M4 falla** por datos inconsistentes | Media | 🔴 Crítico | Script de validación previo + backup + rollback plan |
| **Performance** de combos anidados con >1000 variantes | Media | 🟡 Medio | Caché de marcas/modelos + índices en BD |
| **Edición manual de importes** genera errores contables | Alta | 🔴 Alto | Auditoría obligatoria (Serilog) + validaciones + advertencias UI |
| **Lógica de cambios/devoluciones** descuadra stock | Media | 🔴 Crítico | Transacciones atómicas + casos de prueba exhaustivos + validación de stock antes de cambio |
| **Autorización Empleado** incorrecta (acceso a módulos restringidos) | Baja | 🟡 Medio | Auditoría de todos los controllers + pruebas de roles |

---

## 📝 PRÓXIMOS PASOS

1. **Usuario valida** este plan de implementación.
2. **Crear branch** `feature/refactor-modelo-combos-cambios`.
3. **Ejecutar FASE 1** (8 horas).
4. **Ejecutar FASE 2** (19 horas) - **CRÍTICO: M4 requiere validación previa**.
5. **Ejecutar FASE 3** (14 horas).
6. **QA completo** (8 horas).
7. **Merge a main** y deploy a staging.
8. **Deploy a producción** (con runbook de `/docs/runbooks/migraciones-produccion.md`).

---

**¿Querés que inicie la FASE 1 inmediatamente o preferís validar primero este plan?** 🚀

---

## 📍 V1-E1.A — Bases aditivas (cerrada)
**Fecha:** 2026-05-18 11:12  
**Estado:** ✅ Implementada y compilando (migración no aplicada a DB todavía).

### Alcance funcional resumido
Bases estructurales sin breaking changes: nuevas entidades catálogo (Modelo, TalleConfig), enum TipoTalle, rol Empleado + policy RequireEmpleado, seed de talles.

### Cambios por capa
**Domain**
- `Enums/TipoTalle.cs` (NUEVO): ZapatillaAdulto=1, ZapatillaNino=2, Indumentaria=3.
- `Entities/Maestros/Modelo.cs` (NUEVO): SoftDestroyable + Nombre + MarcaId + nav Marca→Subgrupo.
- `Entities/Maestros/TalleConfig.cs` (NUEVO): SoftDestroyable + Valor + Tipo.
- `Entities/Maestros/Subgrupo.cs` (MOD): agregada colección Modelos (preparación para renombre a Marca en V1-E1.B).

**Infrastructure**
- `Data/Configurations/Maestros/ModeloConfiguration.cs` (NUEVO): tabla Modelos, FK Marca→Subgrupos (Restrict), índice único (MarcaId, Nombre).
- `Data/Configurations/Maestros/TalleConfigConfiguration.cs` (NUEVO): tabla TallesConfig, índice único (Tipo, Valor).
- `Data/AppDbContext.cs` (MOD): DbSets Modelos y TallesConfig.
- `Data/SeedData.cs` (MOD): constante RolEmpleado + rol agregado al array de seed + método SeedTallesConfigAsync idempotente (31 registros: 13 adulto + 12 niño + 6 indumentaria).

**Web**
- `Program.cs` (MOD): policy `RequireEmpleado` (SuperUsuario + Administrador + Vendedor + Empleado).

### Migración EF aplicada
- `20260518141125_V2A_ModeloYTalleConfig` — **aditiva pura**, sin tocar tablas existentes.  
  - CREATE TABLE Modelos (con FK a Subgrupos, índice único por marca+nombre).
  - CREATE TABLE TallesConfig (índice único por tipo+valor).
- **No aplicada a DB todavía**: se aplicará junto al seed automático al levantar la app.

### Evidencia
- `dotnet build` → **Build successful** (sin warnings nuevos).
- `dotnet ef migrations add V2A_ModeloYTalleConfig` → OK.
- Migración auditada: solo CREATE TABLE + índices, sin DROP/ALTER de tablas existentes. ✅

### Riesgos y supuestos
- 🟢 R1 (refactor Subgrupo→Marca y eliminación Marca/Modelo/Talle de VarianteProducto) NO se ejecutó en esta sub-etapa; se difiere a V1-E1.B/C donde se aplica refactor coordinado con script de datos y backup obligatorio.
- 🟢 Migración reversible: `dotnet ef migrations remove` permite rollback sin pérdida de datos.

### Pruebas mínimas requeridas (QA al aplicar migración)
- [ ] Levantar app → migración aplicada automáticamente → tablas `Modelos` y `TallesConfig` creadas.
- [ ] Seed automático crea rol `Empleado` + 31 registros en `TallesConfig`.
- [ ] Re-ejecutar seed no duplica talles (idempotencia).
- [ ] Asignar rol Empleado a un usuario y acceder a un controller con `[Authorize(Policy = "RequireEmpleado")]` debería retornar 200; un usuario sin rol Empleado/Vendedor/Admin debería retornar 403.

### Checklist de salida para merge
- [x] Compila sin errores.
- [x] Migración generada y revisada (aditiva pura).
- [x] Sin cambios en entidades preexistentes salvo agregar navegación opcional (Subgrupo.Modelos).
- [x] Seed idempotente.
- [x] Sin impacto en controllers/vistas existentes.
- [x] Policy `RequireEmpleado` agregada sin afectar las demás.

### Próximo paso (V1-E1.B)
Renombre Subgrupo→Marca a nivel CLR + tabla (`ToTable("Marcas")` o RenameTable) + actualización de DI/Controller/Vista + redirect `/Subgrupos` → `/Marcas`. Pendiente decisión de implementación: refactor en bloque vs alias coexistente.
