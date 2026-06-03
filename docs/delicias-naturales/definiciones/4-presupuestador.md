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

## Historial de ajustes
- 2025-06-01: presupuesto inicial registrado
- 2026-04-22: datos de modulos incorporados al dataset de calibracion Abril 2026
- 2026-06-xx: cierre iteracion evolutiva. 4 h reales, USD 160. Tasa actualizada a USD 40/h en parametros globales.
- 2026-06-03: Modulo Relevamiento de Stock cerrado con 5.5 h reales (5h 30min). Incorporado al dataset de modulos reales como ABM intermedio. USD 220 a tasa USD 40/h.
- 2026-06-03: Tasa actualizada a USD 45/h. Las horas ya no se exponen al cliente en documentos de presupuesto.
