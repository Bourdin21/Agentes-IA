# 4 - Presupuestador — Proyecto KOI

> Memoria acumulativa del agente presupuestador.
> Etapa: Presupuesto inicial. Estado: CERRADO (pendiente de aprobación del cliente).
> Fecha: 2026-06-11. Inputs: definiciones 1, 2 y 3 aprobadas.
> Política de facturación vigente (27-presupuesto-parametros, Junio 2026): **USD por módulo = M × $16.80** (M/2.5 × 1.20 × $35). Las horas PERT con contingencia son techo interno, no base de precio. Tasa USD 35/h sobre horas reales con contingencia temporal 20 %.

## 1. Introducción y contexto de relevamiento

Franquicia gastronómica KOI con 15 inversores externos (esquema de 100 puntos, USD 287.500 aportados). El inversor principal administra hoy la operación con dos Excel: estado de resultados mensual del local y reparto de utilidades por puntos. Se presupuesta un sistema web (ASP.NET Core MVC .NET 10 + EF Core + MySQL 8, base blankproject OlvidataSoft) que reemplaza ambos Excel y entrega a cada inversor un dashboard profesional con métricas del local, resultado de la inversión, históricos y valores en USD, más visualización de cámaras (Hik-Connect embebido). Integración con Ayres POS declarada etapa 2 (fuera de este presupuesto).

## 2. Alcance funcional (módulos visibles para el cliente)

15 módulos, según definiciones 1–3: usuarios, rubros/subgrupos, parámetros % + TC, carga mensual del estado de resultados, vista anual + export, indicadores de venta, dashboard, tema dark/light, puntos de inversión, liquidaciones, reparto general, Mi inversión, cámaras, carga inicial de históricos 2024–2026, notificación de cierre por correo a inversores.

## 3. Especificaciones técnicas del servicio

| Ítem | Especificación |
|---|---|
| Tecnología | ASP.NET Core MVC (.NET 10), EF Core, MySQL 8, base blankproject OlvidataSoft |
| Frontend | Bootstrap 5 + olvidata-theme (extendido con dark/light), Chart.js, DataTables |
| Servidor / hosting | Provisto por OlvidataSoft (cubierto por plan de mantenimiento anual) |
| Despliegue | Web única instancia productiva, acceso por navegador (responsive) |
| Esquema de datos | ~23 tablas (17 entidades nuevas + Identity) → plan de mantenimiento PREMIUM |
| Accesos requeridos | Excel fuente actualizados, datos Hik-Connect, totalizadores Ayres, casilla/servicio SMTP emisor |

## 4. Roles y usuarios

| Rol | Acceso |
|---|---|
| Administrador (inversor principal) | Carga y configuración total, liquidaciones, usuarios, cámaras |
| Inversor (hasta 15) | Solo consulta: dashboard, Mi inversión, cámaras |

(Super usuario interno del proveedor: reservado, no se documenta al cliente.)

## 5. Paso 0 — Anclaje histórico (previo a estimar)

Referencias leídas: `eleven-la-plata` (50 h reales / 27 mód), `vinosefue` (30 h / 16 mód, workflows), `delicias-naturales` (95 h base / 19 mód, dataset por módulo), `recotrack` (ABM simple/intermedio), `lumitrack` (ABM intermedio/complejo), `piapartments` (ABM intermedio). Datasets con 30 % incluido normalizados a base (÷1.30) antes de comparar.

Medianas base usadas como ancla:
- ABM simple: **1.5 h** (recotrack: Camiones, Multas, Accidentes, Horas Extras).
- ABM intermedio: **5.0 h** (lumitrack: Reclamo/Cuadrilla/Usuarios/TipoServicio/Materiales; recotrack 4.6; piapartments 5.0).
- ABM complejo: **7.7–11.5 h** (lumitrack Relevamientos 7.7; delicias Compras 11.5, Pedidos 8.1).
- Workflow con estados: **7.7 h** (delicias Gestión de pedidos 10 h /1.30).
- Reporte/exportación nueva: **1.5 h** (regla "nuevo reporte: M 1–2 h", 27-parametros).
- Tablero/dashboard: **4.2 h** (ganaderia "Tablero anual" USD 70 ÷ 16.80; única referencia de dashboard, alcance menor al de KOI).
- UI personalizada/theming: **2.0 h** (extra "UI personalizada" USD 40, 27-parametros).
- Notificaciones acotadas: **3.5 h** (delicias Notificaciones SignalR 4.5 h final ÷ 1.30).
- Migración/carga inicial de datos: **sin referencia comparable** → incertidumbre declarada, riesgo alto.

## 6. Tabla de estimación por módulo

Distribución interna estándar del esfuerzo de cada módulo (trazabilidad, no aditiva): 70 % implementación, 15 % pruebas, 10 % documentación, 5 % riesgo ordinario.

| # | Módulo | Tipo | Drivers | Referencia (Paso 0) | O | M base | M ajust. | P | PERT | Riesgo | Cont. | Hs finales (techo) | Hs fact. (M×0.48) | USD (M×16.80) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Gestión de usuarios inversores | ABM intermedio | vínculo a ficha inversor, blanqueo, activación; reutiliza Identity base | lumitrack ABM Usuarios 5.0 | 3.5 | 5.0 | 5.0 | 7.0 | 5.08 | Bajo | 8 % | 5.49 | 2.40 | 84.00 |
| 2 | Rubros y subgrupos de gasto | ABM intermedio | jerarquía padre-hijo, baja lógica, orden, seed del Excel | lumitrack ABM intermedio 5.0 | 3.5 | 5.0 | 5.0 | 7.0 | 5.08 | Bajo | 8 % | 5.49 | 2.40 | 84.00 |
| 3 | Parámetros porcentuales + tipo de cambio | 2× ABM simple con drivers | vigencia temporal de %, base de cálculo (A/total), TC único por mes | recotrack ABM simple 1.5 ×2 = 3.0 | 2.5 | 3.0 | 3.5 | 5.5 | 3.67 | Bajo | 8 % | 3.96 | 1.68 | 58.80 |
| 4 | Estado de resultados — carga mensual y cálculos | Financiero / ABM complejo cabecera+detalle | ventas A/B, ~30 subgrupos, conceptos % con snapshot, totalizadores, USD, cierre de período | delicias ABM Compras 11.5 base | 7.0 | 11.5 | 10.0 | 15.0 | 10.33 | Medio | 15 % | 11.88 | 4.80 | 168.00 |
| 5 | Estado de resultados — vista anual + export Excel | Reporte/exportación | matriz rubro×12 meses, export | regla nuevo reporte 1.5 | 1.5 | 1.5 | 2.0 | 3.5 | 2.17 | Bajo | 8 % | 2.34 | 0.96 | 33.60 |
| 6 | Indicadores de venta (Ayres, manual) | ABM simple | 3 indicadores por mes | recotrack ABM simple 1.5 | 1.0 | 1.5 | 1.5 | 2.5 | 1.58 | Bajo | 8 % | 1.71 | 0.72 | 25.20 |
| 7 | Dashboard de métricas (core) | Reporte complejo / tablero | 6 cards KPI, 5 gráficos, multi-año, bloque USD, indicadores, estados vacíos | ganaderia Tablero anual 4.2 | 4.5 | 4.2 | 6.0 | 10.0 | 6.42 | Medio | 15 % | 7.38 | 2.88 | 100.80 |
| 8 | Tema dark/light persistido | UI personalizada | doble set de tokens CSS, preferencia por usuario | extra UI personalizada 2.0 | 1.5 | 2.0 | 2.0 | 3.5 | 2.17 | Bajo | 8 % | 2.34 | 0.96 | 33.60 |
| 9 | Puntos de inversión | ABM intermedio con drivers | 100 puntos, valor de aporte variable, bonificados, asignación con vigencia, Σ≤100 | lumitrack ABM intermedio 5.0 | 4.5 | 5.0 | 6.0 | 9.0 | 6.25 | Medio | 15 % | 7.19 | 2.88 | 100.80 |
| 10 | Liquidaciones mensuales | Workflow con estados + financiero | generación al cierre, consumos, Pendiente/Pagada, reapertura auditada, USD/renta | delicias Gestión pedidos 7.7 base | 6.0 | 7.7 | 8.0 | 13.0 | 8.50 | Medio | 15 % | 9.78 | 3.84 | 134.40 |
| 11 | Reparto general histórico | Reporte | serie mensual tipo hoja GENERAL + gráfico | regla nuevo reporte 1.5 | 1.5 | 1.5 | 2.0 | 3.0 | 2.08 | Bajo | 8 % | 2.25 | 0.96 | 33.60 |
| 12 | Mi inversión (vista inversor) | Reporte complejo / tablero | cards, 2 gráficos, historial, aislamiento por inversor | ganaderia Tablero anual 4.2 | 3.0 | 4.2 | 4.0 | 6.5 | 4.25 | Medio | 15 % | 4.89 | 1.92 | 67.20 |
| 13 | Cámaras (config + visualización embebida) | ABM simple + pantalla embed | config Hik-Connect, iframe con fallback a pestaña nueva | recotrack ABM simple 1.5 ×2 = 3.0 | 1.8 | 3.0 | 2.5 | 4.0 | 2.63 | Bajo | 8 % | 2.84 | 1.20 | 42.00 |
| 14 | Carga inicial históricos 2024–2026 | Migración de datos | normalización 2 Excel (3 hojas EERR + 17 hojas reparto), importador, validación de totales | **sin referencia** — incertidumbre declarada | 5.5 | 8.0 | 8.0 | 14.0 | 8.58 | **Alto** | 25 % | 10.73 | 4.80 | **168.00** (incluye +25 % riesgo migración) |
| 15 | Notificación de cierre por correo | Integración SMTP / notificaciones acotadas | config SMTP + prueba, plantilla HTML con resumen del mes + liquidación personalizada, envío a 15 inversores al cierre (no bloqueante), log de envíos + reenvío, idempotencia por período | delicias Notificaciones SignalR 3.5 base | 3.0 | 3.5 | 4.0 | 7.0 | 4.33 | Medio | 15 % | 4.98 | 1.92 | 67.20 |
| | **Totales** | | | | | | **69.5** | | **73.12** | | | **83.25** | **34.32** | **1.201,20** |

Notas de cálculo:
- PERT = (O + 4M + P)/6 sobre M ajustado. Contingencia variable (8/15/25 %) aplicada **una sola vez**, solo al techo interno de esfuerzo.
- USD = M ajustado × $16.80 en todos los módulos. Excepción documentada (política vigente, riesgo extremo): módulo 14 = 8.0 × 16.80 × 1.25 = USD 168.00 (migración de datos, +25 % declarado solo en ese ítem; equivale al rango 20–30 % de 27-parametros aplicado al ítem y no al total).
- Login/layout/base no se cobran como módulo: reutilización blankproject (absorbidos en módulo 1).
- **Cargo fijo por uso de tokens IA: USD 100** (regla vigente 27-parametros, Junio 2026) — línea separada, no se prorratea por módulo. Total desarrollo: 1.201,20 + 100,00 = **USD 1.301,20 → se comunica USD 1.301**.

## 7. Autocorrección por ítem (Paso 7)

Ratio = PERT base / mediana histórica base comparable. Umbral 0.85–1.15.

| # | Referencia | Ratio | Ajuste aplicado | Motivo |
|---|---|---|---|---|
| 1 | ABM intermedio 5.0 | 1.02 | mantener | dentro de umbral |
| 2 | ABM intermedio 5.0 | 1.02 | mantener | dentro de umbral |
| 3 | 2× ABM simple 3.0 | 1.22 | M 3.0→3.5 justificado | drivers reales: vigencia temporal de % y base de cálculo parametrizada (no es un ABM plano) |
| 4 | ABM complejo 11.5 | 0.90 | M 11.5→10.0 a la baja | simplificación real: detalle repetitivo (30 subgrupos con el mismo patrón), sin relaciones cruzadas como Compras |
| 5 | Reporte 1.5 | 1.45 | M 1.5→2.0 justificado | grilla densa 12 meses × ~40 filas + export Excel; sigue dentro del rango 1–2 h de la regla |
| 6 | ABM simple 1.5 | 1.05 | mantener | dentro de umbral |
| 7 | Tablero 4.2 | 1.53 | M 4.2→6.0 justificado (>30 % documentado) | causa puntual: el dashboard KOI es el core de la app — 5 gráficos vs 1 comparativo de la referencia, multi-año, bloque USD, indicadores; el theming se separó al módulo 8 para no inflar este ítem |
| 8 | UI personalizada 2.0 | 1.09 | mantener | dentro de umbral |
| 9 | ABM intermedio 5.0 | 1.25 | M 5.0→6.0 justificado | driver real: asignación con vigencia temporal e historial (reconstrucción de cambios de puntos por mes) + validación Σ≤100 |
| 10 | Workflow 7.7 | 1.10 | mantener (M 7.7→8.0) | dentro de umbral; redondeo por consumos + reapertura auditada |
| 11 | Reporte 1.5 | 1.39 | M 1.5→2.0 justificado | serie multi-año + gráfico de evolución; dentro del rango 1–2 h |
| 12 | Tablero 4.2 | 1.01 | M 4.2→4.0 a la baja | reutiliza componentes de charts del módulo 7 |
| 13 | 2× ABM simple 3.0 | 0.88 | M 3.0→2.5 a la baja | simplificación real: la segunda pieza es solo un iframe con fallback, sin lógica |
| 14 | sin referencia | n/a | incertidumbre declarada | rango interno 5.5–14 h; riesgo alto 25 % declarado; gatillo de reestimación si los Excel llegan con estructura distinta a la relevada |
| 15 | Notificaciones acotadas 3.5 | 1.24 | M 3.5→4.0 justificado | drivers reales vs la referencia (notificación SignalR puntual): plantilla HTML con bloque personalizado por inversor, envío masivo con log/reenvío e idempotencia por período |

## 8. Sanity check del total del proyecto (Paso 8)

- Comparable elegido: **delicias-naturales** (19 módulos, 95 h base, tipo dominante ABM/financiero, incluye notificaciones) — mismo perfil dominante que KOI (15 módulos, financiero + ABM + workflows + notificaciones).
- Horas base por módulo: KOI 73.12/15 = **4.87 h/mód** vs delicias 95/19 = **5.0 h/mód** → ratio **0.97** ✔ (dentro de 0.80–1.20).
- Control adicional contra cierres reales (alerta de sobreestimación, 27-parametros): horas reales proyectadas = M total / 2.5 = 69.5/2.5 = **27.8 h**, consistente con el patrón "proyectos de 8–11 módulos de complejidad media-alta cierran en 25–30 h reales" (KOI: 15 módulos, varios de ellos chicos).
- Decisión: **mantener el total sin recalibrar**.

## 9. Cierre numérico por dos pasos (Paso 9)

- **Paso A (preliminar, suma directa de módulos):** USD 1.201,20 — 34.32 h facturables internas — techo interno de esfuerzo 83.25 h PERT+contingencia.
- **Paso B (tras sanity check del total y validación de contingencia única):** sin ajuste de módulos — ratios por ítem justificados, ratio de proyecto 0.97, contingencia aplicada una sola vez (8/15/25 % solo al techo interno; el precio usa la fórmula M × $16.80 cuyo 20 % temporal ya absorbe la contingencia comercial; única excepción documentada: +25 % del módulo 14). Se suma el cargo fijo de USD 100 por uso de tokens IA (regla vigente).
- **Número a comunicar al cliente: USD 1.301 (desarrollo: 1.201 módulos + 100 tokens IA) + USD 400/año (mantenimiento PREMIUM).**

## 10. Riesgos y supuestos

- Migración de históricos (módulo 14): único ítem con riesgo alto; gatillo de reestimación si los Excel finales difieren de los analizados (estructura de hojas/rubros).
- Hik-Connect: si Hikvision bloquea el embebido por iframe, se entrega la variante "abrir en pestaña dedicada" sin costo adicional (prevista en diseño).
- Notificación por correo: la entregabilidad (spam, reputación de la casilla emisora) depende del servicio SMTP que provea el cliente; mitigada con correo de prueba, log de envíos y reenvío manual. El envío nunca bloquea el cierre del período.
- Supuestos heredados del análisis: un solo local; reparto = Resultado Ejercicio del mes sin ajustes manuales; consumos como monto mensual por inversor; ventas B visibles discriminadas.
- Integración Ayres POS: etapa 2, requiere relevamiento técnico de la BD antes de cotizar (referencia metodológica disponible: integración batch 15–18 h base, Energy Nutrition — sin cierre real).

## 11. Pruebas mínimas requeridas

- Cálculo del estado de resultados contra 3 meses reales del Excel (bases A/total correctas, totales, rentabilidad, USD).
- Cierre de período: generación de liquidaciones con puntos vigentes; reapertura no toca liquidaciones pagadas.
- Aislamiento del inversor: un inversor nunca accede a datos de otro (prueba negativa por URL directa).
- Validación Σ puntos vigentes ≤ 100 y consumos ≤ liquidación bruta.
- Migración: totales anuales 2024/2025 y acumulados por inversor coinciden con los Excel fuente.
- Dashboard con período vacío: sin errores de división por cero.
- Notificación de cierre: al cerrar un mes, cada inversor activo recibe el correo con su liquidación correcta; un envío fallido queda logueado sin revertir el cierre; el re-cierre no duplica correos sin confirmación.

## 12. Checklist de salida para merge

- [ ] Build OK y migración EF inicial aplicada sobre MySQL 8.
- [ ] Seed de catálogos (rubros/subgrupos/parámetros/roles) ejecutado.
- [ ] Pruebas mínimas del §11 en verde, evidenciadas en 6-qa.md.
- [ ] Theme dark/light verificado en las 13 pantallas.
- [ ] Trazabilidad actualizada y aprobación del cliente registrada antes de implementar.

## 13. Tabla para el cliente (Área | USD — horas internas no expuestas)

| Área funcional | USD |
|---|---:|
| Acceso y gestión de usuarios inversores | 84 |
| Configuración del sistema (rubros, porcentajes, tipo de cambio) | 143 |
| Estado de resultados mensual y anual | 202 |
| Indicadores de venta del local | 25 |
| Dashboard de métricas con tema claro/oscuro | 134 |
| Inversiones: puntos, liquidaciones y reparto | 269 |
| Mi inversión (vista del inversor) | 67 |
| Cámaras del local | 42 |
| Carga inicial de datos históricos 2024–2026 | 168 |
| Notificación por correo al cierre del mes | 67 |
| Uso de infraestructura IA (tokens) | 100 |
| **Total desarrollo** | **1.301** |
| Mantenimiento anual — Plan PREMIUM (hosting, seguridad, soporte) | 400/año |

## 14. Plan de mantenimiento anual

Esquema entregado ≈ 23 tablas → rango 16–30 → **Plan PREMIUM: USD 400/año** (hasta 3 usuarios de soporte, soporte prioritario, 2 rondas de ajuste). Se presenta como línea separada post-desarrollo; cubre hosting, seguridad y soporte, no cambios funcionales nuevos.

## 15. Condiciones comerciales y exclusiones

- 50 % al inicio / 50 % a la entrega. Validez de la oferta: 30 días. Moneda: USD.
- Exclusiones: facturación electrónica AFIP/ARCA; aplicación móvil; integración con la BD de Ayres POS (etapa 2, se cotiza tras relevamiento); streaming nativo RTSP de cámaras; otros envíos de correo/notificaciones distintos de la notificación de cierre mensual; cambios de alcance posteriores al inicio.
- Excepción a exclusión estándar (acordada): la carga inicial de históricos 2024–2026 SÍ está incluida (módulo 14).

## Historial de ajustes
- 2026-06-11: presupuesto inicial v1. 14 módulos, M total 65.5 h, USD 1.134 + USD 400/año. Fórmula vigente M × $16.80. Pendiente: aprobación del cliente; cierre de calibración estimado vs real al finalizar el sprint.
- 2026-06-11: v2 — se incorpora el cargo fijo de USD 100 por uso de tokens IA (regla nueva en 27-parametros). Total desarrollo: USD 1.234. Documento cliente rehecho con especificación funcional detallada para envío.
- 2026-06-11: v3 — nuevo módulo 15 "Notificación de cierre por correo" (pedido del cliente): M 4.0 h, USD 67.20, referencia delicias Notificaciones 3.5 base, ratio 1.24 justificado. M total 69.5 h, total desarrollo USD 1.301 (1.201 módulos + 100 tokens IA). Sanity total recalculado: 0.97 vs delicias. Cascada aplicada en definiciones 1–3 y documento cliente.
