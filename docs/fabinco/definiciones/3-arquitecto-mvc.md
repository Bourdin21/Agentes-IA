# Memoria - Arquitecto MVC

## Proyecto: fabinco
## Ultima actualizacion: 2026-08-26

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
`ShowroomGriffin` es el match de dominio y de codigo mas fuerte del historial completo — mismo tipo de negocio (indumentaria/calzado con variantes), codigo real en produccion. Reutilizables directos: `VentaPago`/logica de pago multi-medio+cuotas (PAT-003), `RowVersion` manual MySQL (PAT-004), maquina de estados de Compras si aplica (PAT-005), DataTables+filtros (PAT-008). Estructura de entidades (`Producto`, `VarianteProducto`, `Stock`, `MovimientoStock`, `Compra`, `Venta`/`VentaItem`/`VentaPago`, `Devolucion`) portada casi 1:1 desde ShowroomGriffin, adaptando `Cliente` a perfil empresa (B2B).

### Componentes por capa
- **Domain**: `Producto`, `VarianteProducto` (Color/Talle), `Stock` (1:1 variante), `MovimientoStock`, `Cliente` (RazonSocial, CUIT, CondicionIVA — B2B), `Proveedor`, `Categoria`/`Subgrupo`, `Compra`/`CompraItem`, `Venta`/`VentaItem`/`VentaPago`, `Devolucion` (con tipo: dinero/cambio mismo valor/cambio mayor valor).
- **Application/Infrastructure/Web**: mismo patron de capas que ShowroomGriffin — `IVentaService` (multi-pago+cuotas), `IDevolucionService` (wizard), `IStockService`, `ICompraService`, `IAumentoMasivoService`.

### Diferencias de arquitectura frente a ShowroomGriffin
- `Cliente` gana campos de empresa; sin `AfipService` en el alcance base (a confirmar en demo si hace falta — si FABINCO ya emite factura electronica en su "otro sistema" actual, no se duplica esa integracion aca salvo que el cliente pida migrar tambien la facturacion).
- Compras: se evalua si necesita la maquina de 4 estados completa de ShowroomGriffin (Borrador→EnProceso→Verificada→Recibida) o una version mas simple — a definir con datos reales de volumen de compra en la demo. Presupuestado con workflow (mas robusto, dado el perfil de empresa establecida) pero marcado como ajustable.
- **Modulos NO incluidos en el alcance base** (ver `1-analista-funcional.md`/`2-disenador-funcional.md`): presupuestos/cotizaciones B2B, trazabilidad de produccion propia. Si se confirman, son entidades nuevas sin precedente en el catalogo del estudio — requieren diseño desde cero, no reutilizacion directa.

### Riesgos tecnicos activos
- **Migracion desde el "otro sistema" actual**: mayor probabilidad que en las dietéticas de que haya datos reales cargados (empresa de 50 años) — exclusion fija del estudio salvo acuerdo aparte, pero a confirmar explicitamente en la demo (impacto de negociacion, no solo tecnico).
- **Volumen real de catalogo/variantes desconocido** — FABINCO maneja multiples marcas (ATT, Grafa70, Funcional) y 9 sectores; si el catalogo es mucho mas grande que ShowroomGriffin, el modulo de Productos/Variantes y el Aumento Masivo pueden requerir ajuste (paginacion, importacion inicial).
- **Rol de la facturacion electronica**: si en la demo se confirma que SI hace falta (no resuelto en su sistema actual), agregar PAT-006 (AFIP/ARCA, ya documentado y reutilizable desde marihogar) como alcance adicional — no incluido en el presupuesto base.

## Historial de ajustes
- 2026-08-26: primera version. Arquitectura portada casi 1:1 desde ShowroomGriffin (codigo real), con Cliente adaptado a B2B y dos modulos candidatos explicitamente fuera del alcance base.
