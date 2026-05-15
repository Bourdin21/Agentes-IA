# Memoria - QA

## Proyecto: vinosefue
## Ultima actualizacion: 2026-05-13

> Documento de referencia rapida. La memoria QA detallada por feature vive en:
> `C:\Sistemas\vino-y-se-fue\docs\vino-y-se-fue\definiciones\6-qa.md`

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
| DEF-003 | menor | Boton "Registrar pago" no se bloquea en `/Compras/Detalle` para compra espejo de concesion `CerradaManual` | pendiente |

---

## Estado go/no-go

- Feature Concesion recibida del proveedor: **GO** (DEF-003 no bloquea). Deployado a produccion el 2026-05-14.
- Feature Reversion estados pedido: **pendiente QA manual** (build OK, pendiente migracion en produccion).
- Feature Stock propio: **pendiente QA manual** (build OK, pendiente migracion en produccion).
