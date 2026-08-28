# Memoria - Arquitecto MVC

## Proyecto: peras-del-olmo
## Ultima actualizacion: 2026-08-27

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
`ShowroomGriffin` como precedente directo (codigo real en produccion) — mismo criterio que FABINCO. Reutilizables: `VentaPago` (PAT-003), `RowVersion` manual MySQL (PAT-004), maquina de estados de Devoluciones si aplica (PAT-005), DataTables+filtros (PAT-008).

### Componentes por capa
- **Domain**: `Categoria` (con flag `UsaVariantes`), `Producto`, `VarianteProducto` (Color/Talle, solo si `Categoria.UsaVariantes=true`), `Stock`, `MovimientoStock`, `Cliente` (persona, simple), `Proveedor`, `Compra`/`CompraItem`, `Venta`/`VentaItem`/`VentaPago`, `Devolucion`.
- **Application/Infrastructure/Web**: mismo patron de ShowroomGriffin. `IProductoService.CrearAsync` ramifica segun `Categoria.UsaVariantes` (con o sin alta de `VarianteProducto`), resto de services identicos en contrato.

### Diferencias de arquitectura frente a ShowroomGriffin/FABINCO
- `Cliente` es la version simple (persona, sin RazonSocial/CUIT) — mas cercano al ShowroomGriffin original que a la adaptacion B2B de FABINCO.
- `Categoria.UsaVariantes` es la unica pieza sin precedente exacto en ninguno de los dos proyectos anteriores — condiciona el formulario de alta de `Producto` y la logica de `IProductoService`/`IStockService` (decrementar `Stock` de la variante vs. `Stock` del producto simple).
- **[2026-08-27]** `AfipService`/`AfipTokenCache` (PAT-006, `marihogar`) se agrega en la Propuesta Full a pedido explicito de Joaquin — no estaba en el pain point original del lead. Mismo circuito documentado en `34-integracion-afip-arca.instructions.md` que en las dietéticas/FABINCO. `Comprobante`/`ComprobanteItem` como entidades nuevas en la Propuesta Full.

### Riesgos tecnicos activos
- **Volumen real de catalogo desconocido** — con 3 lineas de producto y presencia fuerte en redes (27K+21K+18K seguidores combinados), el catalogo podria ser mas grande que un local tipico — a confirmar en demo antes de descartar necesidad de importacion inicial (PAT-012, si aplica).
- **Reparto de roles entre 4 personas** no confirmado — podria requerir permisos diferenciados por linea de producto (ej. alguien solo gestiona jugueteria) — no incluido en el alcance base salvo que se confirme.

## Historial de ajustes
- 2026-08-27: primera version. Arquitectura calcada de ShowroomGriffin (mas cercana al original que la adaptacion B2B de FABINCO), con `Categoria.UsaVariantes` como unica pieza nueva sin precedente exacto.
