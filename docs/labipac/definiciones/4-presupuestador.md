# Memoria - Presupuestador

## Proyecto: labipac
## Ultima actualizacion: 2026-06-13 — PRESUPUESTO CERRADO

## Items presupuestables

| Modulo | Tipo | M (h) | USD base (M×$16.80) | USD cliente (con IA) |
|---|---|---|---|---|
| M1 Unidades Bioquimicas | ABM simple | 1.5 | $25.20 | $34 |
| M2 Practicas | ABM intermedio | 6.0 | $100.80 | $135 |
| M3 Produccion Mensual + Historial | ABM complejo cabecera/detalle | 8.5 | $142.80 | $191 |
| M4 Infra transversal | Ajustes puntuales | 1.5 | $25.20 | $34 |
| **TOTAL** | | **17.5** | **$294.00** | **$394** |

Tokens IA: USD 100 (implicito, prorrateado en Etapa 1). Factor: 394/294 = 1.3401.

## Estimacion por esfuerzo

| Modulo | O | M | P | PERT | Riesgo | Cont. | Hs finales |
|---|---|---|---|---|---|---|---|
| M1 | 1.0 | 1.5 | 2.5 | 1.58 | Bajo | 8% | 1.71 |
| M2 | 4.0 | 6.0 | 9.0 | 6.17 | Medio | 15% | 7.09 |
| M3 | 6.0 | 8.5 | 13.0 | 8.83 | Medio | 15% | 10.16 |
| M4 | 1.0 | 1.5 | 2.5 | 1.58 | Bajo | 8% | 1.71 |
| TOTAL | 12.0 | 17.5 | 27.0 | 18.17 | | | 20.67 |

## Anclaje historico por modulo

| Modulo | Referencia | Mediana base | Ratio M/mediana | Decision |
|---|---|---|---|---|
| M1 | ABM Camiones/Categorias (1.5h) | 1.5h | 1.00 | Mantener |
| M2 | ABM intermedios Lumitrack/Delicias (5.0h) | 5.0h | 1.20 | Justificado: 5 drivers concretos (Select2 M:N, sumatoria JS, RN-01 server, IgnoreQueryFilters, Details) |
| M3 | ShowroomGriffin cabecera/detalle (9.6h) | 9.6h | 0.885 | Mantener: sin workflow (P4-A), drivers AJAX+P5-B sostienen |
| M4 | ShowroomGriffin infra (0.5h/migracion) | 0.5h/migracion | 1.00 | Mantener |

## Sanity check del total

- Comparable: eleven-la-plata (50h, 27 modulos simples). labipac 4 modulos mix simple/intermedio/complejo → 4.38h/modulo coherente.
- ShowroomGriffin (7.87h/modulo): labipac por debajo, correcto (modulos menos complejos).
- Rango esperado sistema pequenio 3-5 modulos: 12-22h → labipac 17.5h en centro. Sin correccion.

## Cierre

- Paso A = Paso B = 17.5h M base / $294.00 base / $394 cliente (con IA)
- Doble contingencia: NO aplicada (unica vez por item)
- Etapa 1: todo el alcance (USD 394). Etapa 2: sin modulos adicionales definidos.
- Mantenimiento anual: Plan PRO (14 tablas, 6-15) — USD 300/anio
- Condiciones: 50/50 por etapa.

## Riesgos y contingencia

- M1: 8% (riesgo bajo — ABM estandar)
- M2: 15% (riesgo medio — logica JS + IgnoreQueryFilters + M:N)
- M3: 15% (riesgo medio — AJAX + snapshot + multiples validaciones)
- M4: 8% (riesgo bajo — ajustes tecnicos puros)

## Historial de ajustes
- 2026-06-13: Presupuesto inicial cerrado. 4 modulos, 17.5h M total, $294 base, $394 cliente (con IA implicit). Metodo PERT pasos 0-9 completo. Sanity check OK. Sin doble contingencia. Listo para presentar al cliente.
