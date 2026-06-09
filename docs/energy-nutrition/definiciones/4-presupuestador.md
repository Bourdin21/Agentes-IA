# Memoria - Presupuestador

## Proyecto: energy-nutrition
## Ultima actualizacion: 2026-06-08

## Perfil del proyecto

- Sistema: Gestion de Ventas de Suplementos Dietarios (Energy Nutrition)
- Modulos funcionales: 14 + 4 integraciones externas + INF + DEP
- Stack: ASP.NET Core MVC, Clean Architecture, EF, MySQL
- Horas estimadas base (PERT, sin contingencia): 117.3 h
- Horas finales estimadas (con contingencia variable): 138 h
- Tasa v4.0: USD 30/h (excepcion documentada). Tasa v5.0: USD 35/h (sin contingencia). Tasa v6.1: USD 35/h con contingencia temporal 20% (formula M/2.5×1.20).
- Total v4.0: USD 4,340 (138h PERT × $30 + $200 tokens IA)
- Total v5.0: USD 1,790 (45.5h reales × $35 + $200 tokens IA) — reduccion −59% vs v4.0
- Total v6.1: USD 2,108 (54.5h reales × $35 con contingencia 20% + $200 tokens IA) — version vigente
- Mantenimiento: USD 750/ano (Plan SCALE, sin cambio)
- Tablas BD: ~35 (28 DbSets negocio + Identity/Migrations) → Plan SCALE
- Fecha de presupuesto: Junio 2026
- Estado: BORRADOR pendiente aprobacion. Sin horas reales disponibles.
- Documento fuente completo: C:\Sistemas\1Presupuesto Energy Nutrition\docs\blankproject\definiciones\4-presupuestador.md

## Valor como referencia de calibracion

- Referencia para: proyectos con integraciones externas (webhooks, API batch, OAuth, ARCA), modulos de catalogo complejos con AJAX
- Metodologia: v4.0 con anclaje historico estricto (Paso 0), ratios documentados, justificacion para cada ratio >1.15
- NO usar para calibrar horas reales hasta tener cierre confirmado
- Usar como referencia de METODO y rangos estimados de integraciones externas

## Dataset de modulos estimados (horas base PERT, sin contingencia)

Comparable principal usado: ShowroomGriffin (25h real / 11 modulos) + Delicias Naturales (95h base / 19 modulos).

| Modulo | Tipo | Horas base PERT | Cont. | Horas finales | Ratio | Estado |
|---|---|---:|---:|---:|---|---|
| Sucursales | ABM simple | 2.4 h | 8% | 3 h | 1.04 ✅ | Dentro de rango |
| Sync MP (OAuth + mapeo) | Integracion WS simple | 3.2 h | 15% | 4 h | 1.07 ✅ | Dentro de rango |
| CC Proveedores | Financiero simple | 6.2 h | 8% | 7 h | 1.11 ✅ | Dentro de rango |
| Stock + Transferencias | ABM complejo | 7.2 h | 15% | 8 h | 0.94 ✅ | Dentro de rango |
| ARCA (migracion + homologacion) | Integracion critica | 7.3 h | 25% | 9 h | 2.09 — justificado | cert .p12 + ciclo homologacion AFIP, fuera del control del desarrollo |
| Sync TN (webhooks + creacion ventas) | Integracion webhook | 8.3 h | 15% | 10 h | 2.77 — justificado | BackgroundService + HMAC + receive-then-fetch + Named HTTP Client |
| Compras (5 estados + stock + adjunto) | ABM complejo | 9.8 h | 8% | 11 h | 1.27 — justificado | 5 estados + impacto stock al ConfirmarRecepcion + adjunto |
| Devoluciones + NC fiscal | ABM complejo | 10.3 h | 25% | 13 h | 1.34 — justificado | 6 entidades + 2 tipos resolucion + NC ARCA |
| Ventas wizard + 7 estados | Workflow complejo | 14.5 h | 15% | 17 h | 1.88 — justificado | 7 estados + wizard AJAX 3 pasos + autorizacion precio < costo |
| Catalogo TN + ML (batch sync) | Doble integracion batch | 16.7 h | 25% | 21 h | 2.78 — justificado | throttling batch TN + token refresh ML + polling hub AJAX |

## Rangos de integraciones externas derivados de EN (sin precedente en dataset anterior)

Estas referencias cubren tipos de modulo que no existian en el dataset historico previo.
Son estimaciones, no cierres reales. Usar con precaucion hasta tener cierre confirmado.

| Tipo de integracion | Horas base PERT | Referencia |
|---|---:|---|
| WS simple (OAuth + mapeo de datos) | 3 – 4 h | M06 Sync MP (3.2 h) |
| Webhook con BackgroundService (async, HMAC) | 8 – 10 h | M07 Sync TN (8.3 h) |
| Batch doble con rate limit + token refresh | 15 – 18 h | M08 Catalogo TN+ML (16.7 h) |
| ARCA / AFIP (migracion codigo + cert + homologacion) | 7 – 9 h | M05 ARCA (7.3 h) |

## Historial de ajustes

- 2026-06-08: referencia incorporada al dataset global. Estado: estimacion sin cierre real. Documento fuente: C:\Sistemas\1Presupuesto Energy Nutrition (v4.0).
- 2026-06-08: v5.0 generada con nueva parametrizacion USD 35/h sobre horas reales (M÷2.5). Total: 45.5h / $1.790. Comparativa: −59% vs v4.0 ($4.340 → $1.790).
- 2026-06-08: v6.0 con contingencia temporal 20% a USD 40/h. Total: 54.5h / $2.380. Luego ajustada tasa a USD 35/h.
- 2026-06-08: v6.1 vigente. Tasa USD 35/h + contingencia 20%. Formula M×$16.80. Total: 54.5h / $2.108. Documento cliente actualizado a v6.1.
