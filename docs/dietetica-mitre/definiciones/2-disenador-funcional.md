# Memoria - Disenador funcional

## Proyecto: dietetica-mitre
## Ultima actualizacion: 2026-08-26

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
Revisado `docs/patrones/catalogo.yml` y `docs/*/definiciones/`. **Precedente directo de diseño: `desborder-sin-gluten`** (mismo rubro, mismo pain point "facturo todo a mano", mismo pitch outbound) — mismo dia habil anterior, sigue en etapa de propuesta sin implementar (no hay codigo entregado todavia, solo diseño validado). Se reutiliza integramente el diseño de esa memoria, con un unico ajuste: **1 sola persona confirmada** (sin la ambiguedad "1 o 2" de desborder-sin-gluten) simplifica Usuarios y roles a un unico rol Administracion, dejando el rol Vendedor preparado pero no obligatorio desde el arranque.

Reutilizables por codigo real (igual que desborder-sin-gluten): PAT-006 (AFIP/ARCA, `marihogar`), PAT-003 (MetodoPago, `ShowroomGriffin`), PAT-004 (RowVersion MySQL), PAT-008 (DataTables+filtros).

### Historias de usuario
Identicas a `docs/desborder-sin-gluten/definiciones/2-disenador-funcional.md` (HU-01 a HU-10), con el ajuste de HU-04 (Usuarios y roles): con 1 sola persona, alcanza con el rol Administracion unico — el rol Vendedor se deja definido en el modelo de Identity pero no es obligatorio asignarlo desde la puesta en marcha.

### Flujos de pantalla, ViewModels, validaciones, contratos de Services
Identicos a desborder-sin-gluten — mismo nucleo Comprobante/AFIP (B) y Producto/Stock/Venta/Compra/CierreCaja (A adicional). No se repite el detalle aca para evitar duplicacion — ver el proyecto hermano como fuente de verdad del diseño compartido.

## Historial de ajustes
- 2026-08-26: primera version. Diseño identico a desborder-sin-gluten (mismo concepto, mismo rubro), con simplificacion de roles a 1 solo (Administracion) por tener 1 sola persona confirmada sin ambiguedad.
