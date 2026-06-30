# Memoria - Presupuestador

## Proyecto: delicias-naturales
## Ultima actualizacion: 2026-06-03

## Datos de presupuesto

- Sistema: Gestion Comercial Delicias Naturales
- Modulos funcionales: 19
- Stack: ASP.NET MVC 5, .NET Framework 4.7.2, EF6, MySQL
- Horas estimadas base (sin contingencia): 95 h
- Horas totales con contingencia 15%: 110 h
- Costo total estimado: USD 1.540
- Tasa efectiva presupuesto original: USD 14 / hora
- Tasa vigente desde Junio 2026: USD 45 / hora
- Fecha de presupuesto: Junio 2025
- Estado: presupuestado. Estimacion retrospectiva validada por el cliente. Iteracion evolutiva Junio 2026 cerrada (4 h / USD 160).

## Perfil tecnico

- Entidades: 26
- Controladores: 19
- Migraciones EF evolutivas: 25
- Integraciones AFIP: 5
- Maquinas de estado: multiples
- Tecnologias adicionales: SignalR, reportes PDF, soft-delete

## Dataset de modulos reales (horas finales con 30% incluido)

| Modulo | Tipo | Horas finales (con 30%) |
|---|---|---|
| Notificaciones SignalR | Notificaciones | 4.5 h |
| Gestion de pedidos | Workflow | 10 h |
| ABM Pedidos | ABM complejo | 10.5 h |
| ABM Descuentos | ABM intermedio | 6.5 h |
| ABM Pagos | ABM intermedio | 5 h |
| ABM Compras | ABM complejo | 15 h |
| ABM Proveedores | ABM intermedio | 7 h |
| ABM Ventas | ABM complejo | 10 h |
| ABM Categorias | ABM simple | 2 h |
| Relevamiento de Stock | ABM intermedio | 5.5 h |

## Cierre de calibracion - Iteracion evolutiva Junio 2026

| Modulo | Tipo | Horas estimadas | Horas reales | Desvio | Motivo |
|---|---|---|---|---|---|
| Solicitudes Ingreso Stock (estados por item, verificacion deposito, filtro categoria, reemplazo stock) + Pedidos (estado Listo para Retirar + email cliente) | Workflow complejo con extensiones | 4 h | 4 h | 0% | Estimacion exacta. Alcance bien delimitado, sin sorpresas tecnicas. |

- Tasa cobrada: USD 40 / hora
- Total cobrado: USD 160
- Ratio calibracion estimado/real: 1.0

## Dataset de modulos reales - Actualizacion Junio 2026

| Modulo | Tipo | Horas reales | Tasa | USD |
|---|---|---|---|---|
| Mejoras evolutivas workflow Solicitudes + Pedidos | Extensiones sobre workflow existente | 4 h | USD 40/h | USD 160 |
| Relevamiento de Stock | ABM intermedio | 5.5 h | USD 40/h | USD 220 |

Nota: los modulos historicos anteriores (columna "Horas finales con 30%") mantienen su valor en horas como referencia de esfuerzo. El costo debe recalcularse a USD 45/h para presupuestos nuevos.

## Dataset de modulos reales - Iteracion evolutiva Junio 2026 (batch mejoras)

| Modulo | Tipo | M (h) | Horas PERT | Riesgo | USD cliente | Estado |
|---|---|---|---|---|---|---|
| F1 — Badge disponibilidad stock + SweetAlert en submit | Ajuste puntual + regla de negocio | 2 h | 2.25 h | Bajo +8% | USD 34 | Presupuestado |
| F2 — Rol Vendedor acceso Pedidos | Ajuste puntual (permisos) | 1 h | 1.08 h | Bajo +8% | USD 17 | Presupuestado |
| F3 — Totalizador Pagos (Efectivo + Transferencia + cards) | Modificacion modulo financiero + UI | 2 h | 2.16 h | Bajo +8% | USD 34 | Presupuestado |
| F4 — Layout Resumen Pedido integrado (2 col, panel expandido) | Rediseno layout vista compleja | 3 h | 3.64 h | Medio +15% | USD 50 | Presupuestado |
| **Total batch** | | **8 h** | **9.13 h** | | **USD 135** | |

- Cargo IA tokens: no aplica (facturables totales 3.84 h < 4 h umbral iteraciones evolutivas).
- Tasa vigente: USD 35/h. Formula: M x $16.80.
- Etapa 1 (operacionales): F2 + F3 = USD 51. Etapa 2 (UX): F1 + F4 = USD 84.

## Dataset de modulos reales - Iteracion Dashboard Ampliado (batch reportes)

| ID | Modulo | Naturaleza | O | M | P | PERT | Riesgo | H.Finales | USD PERT | USD cliente |
|---|---|---|---|---|---|---|---|---|---|---|
| RF-D01 | Detalle por Producto *(DT-01 incluida)* | Reporte nuevo | 1.7 | 2.5 | 4.0 | 2.62 | +8% Bajo | 2.83 | $42 | $30 |
| RF-D02 | Clientes + deuda historica | Reporte nuevo | 1.7 | 2.5 | 4.5 | 2.70 | +15% Medio | 3.11 | $42 | $30 |
| RF-D03 | Pedidos: estados y conversion | Reporte nuevo | 1.0 | 1.5 | 2.5 | 1.58 | +8% Bajo | 1.71 | $25 | $20 |
| RF-D04 | Rentabilidad: margen bruto real | Reporte financiero nuevo | 2.0 | 3.0 | 5.0 | 3.17 | +15% Medio | 3.64 | $50 | $35 |
| RF-D05 | Index Dashboard | Mejora modulo existente | 0.7 | 1.0 | 1.5 | 1.03 | +8% Bajo | 1.11 | $17 | $10 |
| **Total** | | | | **10.5h** | | **11.10h** | | **12.40h** | **$176** | **$100** |

- PERT base: USD 176. Precio de lista presentado al cliente: USD 125 (subtotal interno ajustado comercialmente).
- Descuento por fidelidad 15%: USD 25. Total cobrado al cliente: **USD 100**.
- Tokens IA: no facturado (decision comercial del cliente).
- Mantenimiento anual: no incluido (decision comercial del cliente).
- Facturables PERT: 5.04h > 4h (IA tokens aplicarian por regla, pero no se cobraron).
- Deuda tecnica DT-01 (`CantidadVendida` int→decimal): absorbida en RF-D01 sin costo adicional.
- No requiere migracion EF: todos los datos existen en el modelo actual.

### Referencias historicas usadas en este batch

| Referencia | Horas base | Motivo |
|---|---|---|
| DN batch F3 Totalizador Pagos (mismo proyecto) | M = 2h | Logica financiera + UI, mismo stack |
| ShowroomGriffin Resumen Semanal | M = 2h | Reporte con query + tabla + chart en MVC |
| Banda estandar "Nuevo reporte o exportacion" | 1-2h (med. 1.5h) | Base de partida para todos los modulos |

### Autocorreccion

| ID | PERT | Ref. base | Ratio | Decision |
|---|---|---|---|---|
| RF-D01 | 2.62h | 2.0h | 1.31 >1.15 | Justificado: selector dinamico + 2do nivel agregacion + DT-01 + UnidadMedida + grafico |
| RF-D02 | 2.70h | 2.0h | 1.35 >1.15 | Justificado: SaldoFavor + query historica + tabla ordenable 6 cols |
| RF-D03 | 1.58h | 1.5h | 1.05 OK | En rango. Sin ajuste. |
| RF-D04 | 3.17h | 2.0h | 1.59 >1.15 | Justificado: JOIN cross-entity + margen negativo + PrecioCompra=0 + grafico horizontal |
| RF-D05 | 1.03h | 0.75h | 1.37 >1.15 | Justificado: badge requiere query real en controller action |

Sanity check total: M promedio 2.1h/item vs batch anterior 2.0h/item. Ratio 1.05. OK.

---

## Historial de ajustes
- 2025-06-01: presupuesto inicial registrado
- 2026-04-22: datos de modulos incorporados al dataset de calibracion Abril 2026
- 2026-06-xx: cierre iteracion evolutiva. 4 h reales, USD 160. Tasa actualizada a USD 40/h en parametros globales.
- 2026-06-03: Modulo Relevamiento de Stock cerrado con 5.5 h reales (5h 30min). Incorporado al dataset de modulos reales como ABM intermedio. USD 220 a tasa USD 40/h.
- 2026-06-03: Tasa actualizada a USD 45/h. Las horas ya no se exponen al cliente en documentos de presupuesto.
- 2026-06-28: Batch de 4 mejoras evolutivas presupuestado. M total 8 h, USD 135. Tasa vigente USD 35/h. Sin cargo IA tokens (facturables < 4 h).
- 2026-06-28: Presupuesto standalone F1 + F2 (mejoras propuestas por usuario). M total 3 h, USD 51. Sin cargo IA tokens (facturables 1.44 h < 4 h).
- Sesion actual: Dashboard Ampliado. 5 items, M total 10.5h, PERT USD 176. Precio comercial acordado USD 100 (descuento fidelidad $25 sobre lista $125). DT-01 absorbida en RF-D01.
