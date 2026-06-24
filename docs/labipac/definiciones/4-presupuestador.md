# Memoria - Presupuestador

## Proyecto: labipac
## Ultima actualizacion: 2026-06-23 — PRESUPUESTO ACTUALIZADO + CIERRE REAL

## Items presupuestables

| Modulo | Tipo | M (h) | USD base (M×$16.80) |
|---|---|---|---|
| M1 Unidades Bioquimicas | ABM simple | 1.5 | $25.20 |
| M2 Practicas | ABM intermedio | 6.0 | $100.80 |
| M3 Produccion Mensual + Historial | ABM complejo cabecera/detalle | 8.5 | $142.80 |
| M4 Infra transversal | Ajustes puntuales | 1.5 | $25.20 |
| M5 Pacientes | ABM intermedio | 3.5 | $58.80 |
| M6 Integracion parcial FABA (analitos, mutuales, consulta pacientes) | Integracion externa parcial | 5.0 | $84.00 |
| **TOTAL DESARROLLO (sin Tokens IA)** | | **26.0** | **$436.80** |

## Resumen economico para cliente

| Concepto | USD |
|---|---:|
| Subtotal desarrollo (sin Tokens IA) | $436.80 |
| Tokens IA (item individual) | $132.20 |
| **TOTAL CLIENTE** | **$569.00** |

Factor cliente/desarrollo: 569/436.8 = 1.3027.

## Estimacion por esfuerzo

| Modulo | O | M | P | PERT | Riesgo | Cont. | Hs finales |
|---|---|---|---|---|---|---|---|
| M1 | 1.0 | 1.5 | 2.5 | 1.58 | Bajo | 8% | 1.71 |
| M2 | 4.0 | 6.0 | 9.0 | 6.17 | Medio | 15% | 7.09 |
| M3 | 6.0 | 8.5 | 13.0 | 8.83 | Medio | 15% | 10.16 |
| M4 | 1.0 | 1.5 | 2.5 | 1.58 | Bajo | 8% | 1.71 |
| M5 | 2.0 | 3.5 | 5.0 | 3.50 | Medio | 15% | 4.03 |
| M6 | 3.0 | 5.0 | 8.0 | 5.17 | Alto | 25% | 6.46 |
| TOTAL | 17.0 | 26.0 | 40.0 | 26.83 | | | 31.16 |

## Anclaje historico por modulo

| Modulo | Referencia | Mediana base | Ratio M/mediana | Decision |
|---|---|---|---|---|
| M1 | ABM Camiones/Categorias (1.5h) | 1.5h | 1.00 | Mantener |
| M2 | ABM intermedios Lumitrack/Delicias (5.0h) | 5.0h | 1.20 | Justificado: 5 drivers concretos (Select2 M:N, sumatoria JS, RN-01 server, IgnoreQueryFilters, Details) |
| M3 | ShowroomGriffin cabecera/detalle (9.6h) | 9.6h | 0.885 | Mantener: sin workflow (P4-A), drivers AJAX+P5-B sostienen |
| M4 | ShowroomGriffin infra (0.5h/migracion) | 0.5h/migracion | 1.00 | Mantener |
| M5 | ABM intermedio generico (3.0h) | 3.0h | 1.17 | Mantener: ABM con validaciones y busqueda |
| M6 | Integraciones parciales API (4.5h) | 4.5h | 1.11 | Mantener: mapeo externo + consumo parcial por catalogos |

## Sanity check del total

- Comparable: eleven-la-plata (50h, 27 modulos simples). labipac 6 modulos mix simple/intermedio/complejo/integracion parcial -> 4.33h/modulo coherente.
- ShowroomGriffin (7.87h/modulo): labipac por debajo, correcto (sin workflow complejo y con integracion parcial acotada).
- Rango esperado sistema pequenio-mediano 5-7 modulos: 18-32h -> labipac 26.0h dentro de rango. Sin correccion.

## Cierre

- Paso A = Paso B = 26.0h M base / $436.80 base / $569 cliente (con IA)
- Doble contingencia: NO aplicada (unica vez por item)
- Etapa 1: todo el alcance (USD 569). Etapa 2: sin modulos adicionales definidos.
- Mantenimiento anual: Plan PRO (14 tablas, 6-15) — USD 300/anio
- Condiciones: 50/50 por etapa.

## Cierre de calibracion estimado vs real

- Horas reales de desarrollo informadas: 12.0h
- Estimado base (M): 26.0h -> desvio: -53.85%
- Estimado con contingencia (Hs finales): 31.16h -> desvio: -61.49%
- Productividad real observada: 2.00h/modulo (6 modulos)
- Lectura de calibracion: sobreestimacion en M/P para modulos ABM e integracion parcial de baja profundidad.
- Accion de recalibracion sugerida: para proximos presupuestos similares, bajar banda M de integraciones parciales y usar P mas acotado si no hay workflow de estados ni sincronizacion bidireccional.

## Riesgos y contingencia

- M1: 8% (riesgo bajo — ABM estandar)
- M2: 15% (riesgo medio — logica JS + IgnoreQueryFilters + M:N)
- M3: 15% (riesgo medio — AJAX + snapshot + multiples validaciones)
- M4: 8% (riesgo bajo — ajustes tecnicos puros)
- M5: 15% (riesgo medio — ABM con validaciones de identidad y busqueda)
- M6: 25% (riesgo alto — integracion externa parcial FABA, posibles variaciones de contrato)

## Historial de ajustes
- 2026-06-13: Presupuesto inicial cerrado. 4 modulos, 17.5h M total, $294 base, $394 cliente (con IA implicit). Metodo PERT pasos 0-9 completo. Sanity check OK. Sin doble contingencia. Listo para presentar al cliente.
- 2026-06-23: Presupuesto actualizado por ampliacion de alcance implementado (ABM Pacientes + integracion parcial FABA para analitos, mutuales y consulta de pacientes). Nuevo total: 6 modulos, 26.0h M, $436.80 base, $569 cliente. Se registra cierre real con 12.0h ejecutadas y desvio de -53.85% vs M base para calibracion futura.
- 2026-06-23: Se ajusta formato para mostrar Tokens IA como item individual explicito en el resumen economico del presupuesto (sin prorrateo visible en modulos), manteniendo el total cliente en USD 569.00.
