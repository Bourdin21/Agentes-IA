# Memoria - QA

## Proyecto: vinosefue
## Ultima actualizacion: 2026-07-03

> Documento de referencia rapida. La memoria QA detallada por feature vive en:
> `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\6-qa.md`

---

## QA completado — Lote "Compras al proveedor — desacople y cuenta corriente" (2026-07-03)

**Build:** Succeeded (0 errores, mismos warnings preexistentes). **Migraciones:** 2 aplicadas y verificadas en local (conteos/sumas del backfill cuadran contra `VinoSeFue_dev`); pendientes en produccion (requiere aprobacion cliente).

Cobertura: 9 Historias de Usuario (HU-1..9) + 5 Criterios del analista (CU-1..5): **todos PASS** (1 observacion menor de copy en mensaje de concurrencia, no bloqueante). Maquina de estados de `Pedido` y `CompraProveedor` recorrida completa (validas e invalidas).

**2 defectos encontrados y corregidos con auto-fix** (catalogados en `docs/qa/regresiones-manuales.yml` antes del parche):
- **VSF-001** (menor): item vinculado a una Compra `Cancelada` (remanente historico pre-migracion) bloqueaba la cancelacion/eliminacion del Pedido igual que si la compra estuviera facturada, dejando al usuario sin ninguna accion posible (la UI no expone "Quitar item" en una compra Cancelada). Fix: el guard de bloqueo en `PedidoService` (`CambiarEstadoInternoAsync`/`EliminarItemAsync`) ahora excluye tambien `Estado == Cancelada` ademas de `Borrador`.
- **VSF-002** (menor): una `CompraProveedor` en `Borrador` no tenia forma de cancelarse (el diccionario de transiciones solo permitia Borrador→Generada), pese a que el diseno aprobado define Borrador/Generada/EnPreparacion→Cancelada. Fix: se agrego `Cancelada` a las transiciones permitidas desde `Borrador` en `CompraProveedorService` (la logica de cancelacion ya era agnostica al estado de origen).

**DEF-003 (heredado del QA de Concesion recibida)**: verificado **CERRADO** — doble guarda (service + UI, `puedeOperar` en `ConcesionesRecibidas/Detalle.cshtml`) ya presente en el codigo vigente.

Riesgos de liberacion principales: reportes `DeudaProveedor`/`Riesgo` con columna de pago degradada a $0 (decision pendiente del cliente); migraciones y scripts del 2026-07-03 pendientes en produccion (requiere aprobacion + backup); flujo de escritura completo (Crear compra, Pagos/NCR) sin ejercitar aun por navegador — pasos de smoke manual dejados para el usuario.

**Recomendacion: GO condicionado** (pendientes son de coordinacion/produccion y decision de negocio sobre reportes, no de codigo). Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\6-qa.md` (seccion "QA — Lote 'Compras al proveedor...'").

---

## QA completado — Feature Concesion recibida del proveedor (2026-05-13)

**Build:** Succeeded (0 errores, 8 warnings preexistentes).
**Migracion:** `AddConcesionesRecibidasProveedor` aplicada localmente.

### Criterios de aceptacion (10/10)

| # | Criterio | Resultado |
|---|---|---|
| CA-1 | Alta de concesion N items, compra espejo, totales correctos | PASS |
| CA-2 | Compra espejo en reporte DeudaProveedor con badge Concesion | PASS |
| CA-3 | Venta sobre producto concesionado: descuenta stock y FIFO | PASS |
| CA-4 | Cancelacion pedido: restituye stock + devolucion LIFO | PASS |
| CA-5 | Multiples concesiones: FIFO mas antigua, LIFO al revertir | PASS |
| CA-6 | Pago parcial baja saldo; estado sigue Abierta | PASS |
| CA-7 | Pago total + deposito=0 -> Liquidada automatico | PASS |
| CA-8 | Cierre manual bloquea operaciones | PASS parcial (DEF-003 pendiente) |
| CA-9 | Validaciones server-side (cantidades, importe, motivo) | PASS |
| CA-10 | Vistas existentes toleran concesion sin pedidos | PASS |

### Maquina de estados — ConcesionRecibidaProveedor

| Transicion | Resultado |
|---|---|
| (inexistente) -> Abierta | PASS |
| Abierta -> Abierta (pago parcial) | PASS |
| Abierta -> Liquidada (pago total) | PASS |
| Abierta -> CerradaManual | PASS |
| Liquidada -> CerrarManual (debe rechazar) | PASS |
| CerradaManual -> RecalcularEstado (no transiciona) | PASS |

### Cobertura catalogo cross-proyecto

| id | aplica | resultado |
|---|---|---|
| REG-001 | si | PASS (AntiForgery en POST) |
| REG-002 | si | PASS (RequireAdministracion) |
| REG-003 | si | PASS (RowVersion + DbUpdateConcurrencyException) |
| REG-004 | si | PASS (transacciones en CrearAsync y RegistrarPagoProveedorAsync) |
| REG-005 | si | PASS (soft delete global + Activo en ProductosPropios) |
| REG-006 | si | PASS (alerta de origen en Compras/Detalle) |
| REG-007 | si | PASS (validaciones de alta) |
| REG-008 | si | PASS con observacion (ver DEF-001) |
| REG-009 | si | PASS (numero secuencial CON-###### en misma tx) |
| REG-010 | si | PASS (FIFO en confirmar, LIFO en cancelar) |

---

## Defectos activos

| id | severidad | descripcion | estado |
|---|---|---|---|
| DEF-001 | info | Transicion `MarcarLiquidada` manual no implementada como endpoint; solo ocurre automaticamente al pagar total | pendiente |
| DEF-003 | menor | Boton "Registrar pago" no se bloquea en `/Compras/Detalle` para compra espejo de concesion `CerradaManual` | **cerrado 2026-07-03** (doble guarda service+UI verificada vigente) |
| VSF-001 | menor | Item vinculado a Compra `Cancelada` (remanente historico) bloqueaba cancelacion/eliminacion de Pedido igual que Generada+ | **corregido 2026-07-03 (auto-fix)** |
| VSF-002 | menor | Compra `Borrador` sin transicion posible a `Cancelada` (diccionario de estados incompleto) | **corregido 2026-07-03 (auto-fix)** |

---

## Estado go/no-go

- Feature Concesion recibida del proveedor: **GO** (DEF-003 no bloquea, y ahora verificado cerrado). Deployado a produccion el 2026-05-14.
- Feature Reversion estados pedido: **pendiente QA manual** (build OK, pendiente migracion en produccion).
- Feature Stock propio: **pendiente QA manual** (build OK, pendiente migracion en produccion).
- Lote "Compras al proveedor — desacople y cuenta corriente" (2026-07-03): **GO condicionado** — build OK, 9 HU + 5 CU PASS, maquina de estados cubierta, 2 defectos encontrados y corregidos (VSF-001, VSF-002). Pendiente: aplicar migraciones/scripts en produccion (aprobacion cliente), smoke manual en navegador, decision sobre reportes DeudaProveedor/Riesgo degradados. Detalle completo en `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\6-qa.md`.

---

## Anexo historico (mergeado 2026-07-23 desde `docs/vino-y-se-fue/definiciones/6-qa.md` — carpeta stale con este unico archivo, encontrada durante el barrido cross-proyecto de memorias)

### Sesion 2026-05-29/30 — Reconciliacion deuda proveedor Area 520

**Punto cero:** 12/05/2026, saldo = $0 (confirmado por Rec.16431 que cierra el periodo anterior).

**Base de comparacion:**
- Sistema (PROD): $4.151.951,50 de deuda total.
- Ledger proveedor (al 29/05): $3.233.878.
- Diferencia: $918.073,50 (el sistema sobreestima).

**CMPs reconciliadas:**
- CMP-000003 (pre-12/5): pagada $3.499.456 efectivo. Saldo 0. Fuera de scope del punto cero.
- CMP-000005: match exacto. FAC R4-14535 − NCR R4-14536 = $3.085.008. Pago Rec.16729 = $1.655.879. Saldo $1.429.129 = proveedor.

**CMPs con discrepancia:**
- CMP-000004: Snapshot $1.473.290 / Real $1.520.120 / Proveedor FAC aprox. $1.419.105 (R4-14539+14540+14617+14618) → diff $101.015.
- CMP-000006+007 (sin pedidos vinculados): sistema $793.964 vs FAC R4-14760+14761 ($385.644) → diff $408.320.
- CMP-000009 (Borrador): $399.720 sin correlato en el ledger de proveedor provisto (post-29/05 o pendiente de facturacion).

**Anomalias detectadas:**
- CMP-000006 y CMP-000007 no tienen pedidos vinculados (creadas manualmente).
- PED-000013: `PrecioUnitCostoSnapshot × Cantidad ≠ SubtotalCosto` en 2 items (posible aplicacion de descuento no reflejada).
- "corona 330 cc porron" (cerveza) incluida en CMP-000004 (proveedor de vinos Area 520) → $142.560 de productos de proveedores mixtos.

**Preguntas que quedaron abiertas en esa sesion (no se encontro resolucion registrada en memoria posterior — verificar con el cliente/analista si siguen vigentes):**
1. ¿Como se crearon CMP-000006 y CMP-000007? ¿Son correctos los importes?
2. ¿"corona 330 cc porron" corresponde a Area 520 o a otro proveedor?
3. ¿CMP-000009 tiene FAC del proveedor posterior al 29/05?
4. ¿El pago de CMP-000003 ($3.499.456) cubre deuda pre-27/03 no incluida en el extracto?

> Nota: la carpeta `docs/vino-y-se-fue/` (con guiones, distinta de `docs/vinosefue/` que es la carpeta vigente) quedo con este unico archivo residual tras la migracion de nomenclatura del proyecto. Contenido ya mergeado aca; la carpeta vieja puede eliminarse para evitar confusion futura sobre cual es la carpeta autoritativa (no se elimina en este barrido sin confirmacion explicita).
