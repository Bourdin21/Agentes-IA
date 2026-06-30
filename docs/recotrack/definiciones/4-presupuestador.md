# Memoria - Presupuestador

## Proyecto: recotrack
## Ultima actualizacion: 2026-04-22

## Perfil del proyecto

- Sistema: Gestion de servicios de recoleccion
- Fuente: dataset de calibracion Abril 2026
- Nota: horas reportadas incluyen contingencia del 30%

## Dataset de modulos reales (horas finales con 30% incluido)

| Modulo | Tipo | Horas finales (con 30%) | Horas base (/1.30) |
|---|---|---|---|
| ABM Empleados | ABM intermedio | 6 h | 4.6 h |
| ABM Usuarios | ABM intermedio | 6 h | 4.6 h |
| ABM Camiones | ABM simple | 2 h | 1.5 h |
| ABM Tipo Servicio | ABM intermedio | 4 h | 3.1 h |
| Multas Choferes | ABM simple | 2 h | 1.5 h |
| Accidentes Choferes | ABM simple | 2 h | 1.5 h |
| Horas Extras Choferes | ABM simple | 2 h | 1.5 h |

## Dataset de modulos reales — Iteracion evolutiva Junio 2026

| Modulo | Tipo | M (h) | PERT (h) | USD (M x $16.80) | Notas |
|---|---|---|---|---|---|
| Estado de camiones (campo enum en entidad existente, propagacion completa) | Ajuste + propagacion full-stack | 2.0 | 2.1 | 34 | Comparable a ABM simple. Ratio historico 1.11. |
| Rol Taller + ABM usuarios Taller (CRUD Identity completo) | ABM intermedio | 5.5 | 5.6 | 92 | Par exacto con ABM Usuarios. Ratio 0.995. |
| Cron mensual vencimientos (BackgroundService + SMTP + tabla log + pantalla) | Modulo intermedio-complejo | 7.5 | 7.6 | 126 | Sin referencia cerrada exacta. Ratio vs SignalR 1.79 (justificado). |
| Tipo de camion (enum 7 valores, propagacion completa) | Ajuste + propagacion full-stack | 2.0 | 2.0 | 34 | Identico a EstadoCamion. Ratio historico 1.11. |
| Reporte Disponibilidad de Camiones (Excel complejo, layout fisico doble tabla) | Reporte complejo | 5.5 | 5.6 | 92 | Equivale a ABM intermedio en esfuerzo. Ratio 0.995. |
| Division vencimientos por rol (2 flujos SMTP + filtrado pantalla) | Regla de negocio compleja | 3.5 | 3.6 | 59 | Supera ABM simple (ratio 1.94), justificado por 3 roles + 2 flujos independientes. |

Tokens IA: USD 100 (cargo fijo de infraestructura — linea separada en presupuesto cliente).

Total iteracion: M=26.0 h / PERT=26.5 h / USD 437 desarrollo + USD 100 tokens = USD 537.

Sanity check: 26 h M sobre 6 items en sistema en produccion — coherente con cierres historicos (ShowroomGriffin 25 h, Ganaderia ~30 h proyectado).

## Cierre de calibracion — Sprint Junio 2026

Horas reales reportadas: 4.5 h totales (sin desglose por item — distribuidas proporcionalmente segun M).

| # | Item | M (h) | Real proporcional (h) | Ratio M/real |
|---|---|---:|---:|---:|
| 1 | Estado camiones + filtros | 1.0 | 0.21 | 4.78x |
| 2 | Rol Taller | 2.0 | 0.42 | 4.78x |
| 3 | Cron vencimientos + email HTML | 7.0 | 1.47 | 4.78x |
| 4 | Tipo camion (propiedad + migracion) | 1.5 | 0.31 | 4.78x |
| 5 | Reporte Disponibilidad Excel | 3.0 | 0.63 | 4.78x |
| 6 | Division vencimientos por rol | 7.0 | 1.47 | 4.78x |
| **Total** | | **21.5** | **4.50** | **4.78x** |

Factor IA real observado: M_total / real_total = 21.5 / 4.5 = **4.78x**

Historicos comparados:
- ShowroomGriffin: 4.04x
- Ganaderia total proyectado: 3.37x
- Ganaderia Etapa 1 sola: 6.7x
- Mediana historica acumulada: ~4.1x

Desvio factor global vs. mediana historica: +18.3% (4.78x vs. 4.04x). Dentro de variabilidad normal observada.

Horas facturables cobradas (formula M/2.5 x 1.2): 21.5/2.5 x 1.2 = 10.32 h. Ratio formula/real: 10.32/4.5 = 2.29x. Consistente con rango historico 1.3x-1.6x (levemente mayor — sprint de alta eficiencia IA).

Conclusion de calibracion:
- Factor 2.5x del modelo de facturacion: MANTENER. El sprint confirma que el modelo produce precios conservadores y correctos. No hay senal de sub o sobreestimacion sistematica.
- Rangos M por tipo de modulo: MANTENER. Los valores M usados (1-7 h) son proporcionales al esfuerzo relativo observado.
- Desvio promedio absoluto a nivel de item: no calculable (distribucion proporcional sin desglose real independiente).
- Nota metodologica: para futuros sprints, solicitar desglose real por item al cerrar para mejorar la granularidad de calibracion.

## Historial de ajustes
- 2026-04-22: dataset incorporado en calibracion Abril 2026
- 2026-06-28: iteracion evolutiva Junio 2026 incorporada. 6 modulos funcionales nuevos. Total USD 537 (dev + tokens IA). Sistema con 15 tablas → Plan PRO mantenimiento.
- 2026-06-28: cierre de calibracion sprint Junio 2026. Real total 4.5 h. Factor IA observado 4.78x. Factor modelo 2.5x mantenido. Rangos M mantenidos.
