# Memoria - Disenador funcional

## Proyecto: peras-del-olmo
## Ultima actualizacion: 2026-08-27

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
Mismo precedente que FABINCO (mismo dia de diferencia): **ShowroomGriffin** (codigo real en produccion, indumentaria/calzado con variantes Color/Talle, PAT-003, PAT-004, PAT-005, PAT-008). A diferencia de FABINCO (perfil B2B, Cliente=empresa), Peras del Olmo es venta directa al consumidor — el diseño de `Cliente` puede ser el mas simple de ShowroomGriffin (persona, sin campos de empresa), calzando practicamente 1:1 con el precedente original.

**Diferencia de diseño real (no presente en ShowroomGriffin ni FABINCO):** 3 lineas de producto conviviendo en el mismo catalogo (ropa adultos, ropa niños, jugueteria), donde solo 2 de las 3 necesitan variante Color/Talle. `Producto` necesita un flag o una `Categoria.UsaVariantes` (bool) que determine si el alta pide Color/Talle o si el producto se vende como unidad simple (jugueteria) — ShowroomGriffin asume TODO el catalogo con variantes (ropa/calzado), esto es una extension real, no una reduccion de alcance.

### Historias de usuario (nucleo, anclado en ShowroomGriffin)
- **HU-01 — Categorias con o sin variantes**: como administrador, quiero marcar si una categoria de producto usa variantes de Color/Talle (ropa) o se vende como unidad simple (jugueteria), para que el alta de producto pida los campos correctos segun el tipo.
- **HU-02 — Productos y variantes**: alta de producto con variantes Color/Talle cuando la categoria lo requiere; alta simple (sin variantes) cuando no.
- **HU-03 — Stock**: descuento automatico al vender (por variante o por producto simple segun corresponda), alerta de stock bajo.
- **HU-04 — Clientes**: ficha simple de cliente consumidor final (nombre, telefono, email opcional) — sin campos de empresa.
- **HU-05 — Compras a proveedor**: registro de compra que repone stock y actualiza costo.
- **HU-06 — Venta con cobro multi-medio y cuotas** (PAT-003): carrito con productos de cualquiera de las 3 lineas en la misma venta, N lineas de pago.
- **HU-07 — Devolucion o cambio**: wizard con 3 tipos, igual patron que ShowroomGriffin.
- **HU-08 — Aumento masivo de precios**: filtros por categoria/linea de producto.
- **HU-09 — Usuarios y roles**: 4 personas — roles Administracion / Vendedor (a definir reparto exacto en demo, posible separacion por linea de producto si el negocio lo pide).
- **HU-10 — Dashboard**: ventas del dia, stock critico, desglose por linea de producto (ropa/niños/jugueteria).

### ViewModels, validaciones, contratos de Services
Estructura identica a ShowroomGriffin, con el agregado de `Categoria.UsaVariantes` condicionando el ViewModel/vista de alta de `Producto` (dos variantes de formulario: con Color/Talle o simple). Contratos de `IVentaService` (PAT-003), `IDevolucionService`, `IStockService` reutilizados tal cual.

## Historial de ajustes
- 2026-08-27: primera version. Diseño anclado en ShowroomGriffin (mismo precedente que FABINCO), con la extension real de categorias con/sin variantes para soportar las 3 lineas de producto (ropa adultos, ropa niños, jugueteria).
