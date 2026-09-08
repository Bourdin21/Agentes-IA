# 4 - Presupuestador — Proyecto KOI

> Memoria acumulativa del agente presupuestador.
> Etapa: Presupuesto inicial (Etapa 1). Estado: CERRADO (pendiente de aprobación del cliente). Presupuesto del módulo E2-02 (Fichador) en §16 — CERRADO. Presupuesto del Sprint UX/UI Inversor + fixes en §17 — CERRADO, USD 185. Presupuesto de Mi Inversión (pesos) en §18 — CERRADO, USD 12, pendiente de aprobación para pasar a Implementación.
> Fecha: 2026-06-11. Última actualización: 2026-08-13 — §18 Mi Inversión: dividendos/recupero en pesos. Inputs: definiciones 1 (§13), 2 (§12) y 3 (§10) aprobadas.
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
- Integración Ayres POS: etapa 2, requiere relevamiento técnico de la BD antes de cotizar. *(El ancla metodológica de 15–18 h que se citaba acá provenía de una estimación sin cierre real, dada de baja del dataset el 2026-09-08 — ver §20.)*

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
- 2026-08-10: presupuesto del módulo E2-02 "Fichador de empleados" (Etapa 2, post-entrega — ver §16). M 5.5 h, USD 92. Clasificado como Merge sobre sistema propio ya entregado: precio de lista, sin descuento de expansión agresiva (esa política es solo para Build inicial de cliente nuevo). Tokens IA no aplica (horas facturables 2.64 h, por debajo del piso de 4 h). Implementación bloqueada por token QuickPass pendiente — el presupuesto queda cerrado y aprobable igual.

---

- 2026-09-08: **cierre de calibración del módulo E2-01 Ayres** (ver §20). Estimado por ancla 15–18 h (USD 315–378); **real ≈ 2,6 h (USD 44)** → desvío **−82 %/−86 %**. El ancla "integración batch 15–18 h" tenía marca de *sin cierre real*: este es el primer cierre que la toca, pero **no la reemplaza** — se propone desdoblarla en REST documentada (M 3–5 h) vs. batch contra base de datos (se mantiene 15–18 h, aún sin cierre). Advertencia elevada: las anclas del estudio asumen ejecución humana; recalibrarlas hacia abajo es decisión de negocio y debe pasar por `olvidata-ceo`.

## 16. Presupuesto — Módulo E2-02 "Fichador de empleados" (Etapa 2, post-entrega)

### 16.1 Contexto

KOI ya está en producción (Etapa 1 entregada, ver trazabilidad.md). Este es un módulo nuevo post-entrega: se clasifica como **Merge sobre sistema propio ya entregado** (27-presupuesto-parametros) — precio de lista, sin el descuento de expansión agresiva (ese descuento aplica solo a Build inicial de cliente nuevo).

### 16.2 Paso 0 — Anclaje histórico

Referencia elegida: **"Integración WS simple (OAuth + mapeo)": 3–4 h base** (tabla de rangos, 27-presupuesto-parametros) — mediana **3.5 h**. Es la referencia más cercana disponible: integración REST con autenticación y mapeo de DTOs, sin migración EF. No hay ningún módulo de fichaje/asistencia en el dataset histórico (confirmado por el escaneo de arquitectura §8.0) — se declara explícitamente que esta referencia es aproximada, no un caso idéntico.

### 16.3 Estimación por ítem

| Ítem | Tipo | Drivers | Referencia | O | M base | M ajust. | P | PERT | Riesgo | Cont. | Hs finales (techo) | Hs fact. (M×0.48) | USD (M×16.80) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fichador de empleados (integración QuickPass + 3 pantallas: Hoy / Rango / Empleados) | Integración WS + UI de consulta | Bearer token estático, `HttpClient` tipado, 3 vistas de solo lectura con `daterangepicker`/DataTable, cálculo de horas trabajadas y turnos incompletos, manejo de errores de SaaS externo | Integración WS simple 3.5 h | 3.6 | 3.5 | 5.5 | 9.9 | 5.92 | Alto | 25 % | 7.40 | 2.64 | 92.40 |

**Justificación del ajuste M 3.5→5.5 h (+57 %, fuera del umbral de 30 % sin documentar — documentado aquí):** la referencia histórica es solo el componente de integración/mapeo backend; este ítem agrega 3 pantallas de consulta (Hoy, Rango con filtro `daterangepicker`, Empleados) con lógica de presentación (turno incompleto, sin fichada hoy, resumen de horas) que la referencia no incluye. Riesgo clasificado **Alto** (no Bajo, a diferencia del módulo 3 de Etapa 1 que reutilizaba `CotizacionService` ya construido) porque es la primera integración de este tipo en el estudio, sin documentación formal de la API (Swagger no confirmado) y con dependencia externa (SaaS QuickPass).

### 16.4 Autocorrección (Paso 7)

Ratio = M ajustado / mediana histórica = 5.5 / 3.5 = **1.57** → fuera del umbral 0.85–1.15. Ajuste NO revertido: se documenta el driver concreto (3 pantallas UI adicionales sobre una referencia que solo cubre el backend de integración) como justificación explícita, según regla "ratio > 1.15: ajustar a la baja o justificar drivers adicionales concretos".

### 16.5 Sanity check

Comparable interno más cercano dentro del propio proyecto KOI: módulo "Notificación de cierre por correo" (Etapa 1, M 4.0 h — integración externa + 1 pantalla de config/historial) y "Cámaras" (M 2.5 h — 2 pantallas simples sin integración real de datos). El Fichador combina integración externa real (no solo SMTP saliente) con 3 pantallas de consulta con cálculo — M 5.5 h queda razonablemente por encima de ambos, consistente con mayor complejidad. Se mantiene sin recalibrar.

### 16.6 Cierre numérico

- **Paso A (preliminar):** USD 92.40 — 2.64 h facturables internas — techo interno 7.40 h PERT+contingencia.
- **Paso B (tras sanity check):** sin ajuste adicional. Ratio de proyecto no aplica (ítem único). **Tokens IA: NO aplica** — horas facturables (2.64 h) por debajo del piso de 4 h definido en 27-presupuesto-parametros para iteraciones evolutivas menores.
- **Número a comunicar al cliente: USD 92.** Sin impacto en el plan de mantenimiento anual (sin tablas nuevas, sigue en PREMIUM).

### 16.7 Tabla para el cliente

| Área funcional | USD |
|---|---:|
| Fichador de empleados (consulta de asistencia vía QuickPass) | 92 |
| **Total** | **92** |

### 16.8 Condiciones comerciales y exclusiones

- 50 % al confirmar el alcance / 50 % a la entrega — dado el monto bajo, a criterio del cliente puede pagarse 100 % a la entrega.
- **Bloqueante operativo (no comercial):** la Implementación no puede iniciarse hasta que el cliente entregue el token de API y las credenciales admin de QuickPass. El presupuesto queda aprobable y firme independientemente de esa fecha.
- Exclusiones: alta/edición de empleados o huellas (se gestiona en el panel QuickPass), persistencia histórica local, notificaciones de ausentismo — todas fuera de este ítem, se cotizarían aparte si se piden.
- Gatillo de reestimación: si al integrar contra el token real la API expone un contrato distinto al relevado (campos, paginación, límites de rate) que obligue a rediseñar el mapeo.

### 16.9 Riesgos y supuestos

- Riesgo Alto declarado íntegramente por ser la primera integración de este tipo — no se aplicó recargo de precio adicional (a diferencia del módulo 14 de Etapa 1, migración de datos) porque el riesgo acá es de **cronograma** (token pendiente), no de **rehacer trabajo** ya pagado.
- Supuesto: la API de QuickPass devuelve fichadas como pares entrada/salida simples (sin fichadas múltiples por pausas) — a confirmar en Implementación.

### 16.10 Pruebas mínimas requeridas (para cuando se implemente)

- Fichadas del día con al menos un turno completo, uno abierto y un empleado sin fichar.
- Rango de fechas con empleado específico y con "todos".
- Simulación de token inválido/expirado y de timeout → mensaje SweetAlert2 correcto, sin excepción visible al usuario.
- Verificación de que un Inversor no puede acceder a `/Fichador` (policy `RequireAdministracion`).

---

## 17. Presupuesto — Sprint UX/UI Inversor + fixes (Agosto 2026)

### 17.1 Contexto

9 ítems sobre el sistema KOI ya en producción — clasificado como **Merge sobre sistema propio ya entregado** (27-presupuesto-parametros): precio de lista, sin descuento de expansión agresiva (ese descuento es exclusivo de Build inicial para cliente nuevo). Ningún ítem requiere migración EF.

### 17.2 Paso 0 — Anclaje histórico

Todos los ítems anclan en la sección **"Modificación sobre módulo existente"** de 27-presupuesto-parametros (ajuste puntual 0.5–1h, agregar regla de negocio 1–2h) por ser, en su totalidad, cambios sobre pantallas/servicios ya construidos en el propio KOI — ninguno es un módulo nuevo desde cero. Excepción: ítem 7 (Notificaciones), que aunque reutiliza servicios existentes (`INotificationService`, `IEmailService`) agrega una UI de composición con varias piezas (combo dinámico, chips removibles, dos toggles) — se ancla igual en "modificación sobre módulo existente" pero con M ajustado más alto, justificado por la cantidad de piezas de UI nuevas.

### 17.3 Tabla de estimación por ítem

| # | Ítem | Referencia | O | M | P | PERT | Riesgo | Cont. | Hs finales | USD (M×16.80) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Pantalla "Mes actual" (nueva, reutiliza cálculo de KPIs existente) | Nuevo reporte 1–2h | 1.0 | 1.5 | 2.5 | 1.58 | Bajo | 8% | 1.71 | 25.20 |
| 2 | "Dashboard Histórico" (relabel condicional por rol, sin tocar contenido) | Ajuste puntual | 0.35 | 0.5 | 0.8 | 0.53 | Bajo | 8% | 0.57 | 8.40 |
| 3 | Rol nuevo "Encargado" (seed + policy + sidebar exclusivo) | Ajuste puntual (alto del rango) | 0.7 | 1.0 | 1.6 | 1.05 | Bajo | 8% | 1.13 | 16.80 |
| 4 | Fix bug puntos vigentes (Wang) — 1 método, sin tocar datos | Ajuste puntual | 0.35 | 0.5 | 0.8 | 0.53 | Bajo | 8% | 0.57 | 8.40 |
| 5 | Reparto General — simplificar tabla (sacar columnas dinámicas) | Ajuste puntual | 0.35 | 0.5 | 0.8 | 0.53 | Bajo | 8% | 0.57 | 8.40 |
| 6 | Rename "Historial de Resultados" (2 lugares) | Ajuste puntual (mínimo) | 0.2 | 0.3 | 0.5 | 0.32 | Bajo | 8% | 0.34 | 5.04 |
| 7 | Notificaciones — composer + targeting por rol + 2 canales | Modificación c/regla de negocio, ajustado por UI multi-pieza | 1.7 | 2.5 | 4.3 | 2.67 | Medio | 15% | 3.07 | 42.00 |
| 8 | Mi Inversión — tabla historial reformateada (Año/Mes, sin TC/Puntos, orden fijo) | Ajuste puntual (alto) | 0.7 | 1.0 | 1.6 | 1.05 | Bajo | 8% | 1.13 | 16.80 |
| 9 | Fix global importes + regla CSS + documentación en Agentes-IA | Ajuste puntual, alcance "toda la solución" | 0.7 | 1.0 | 1.6 | 1.05 | Bajo | 8% | 1.13 | 16.80 |
| | **Totales** | | | **8.8** | | **9.29** | | | **10.22** | **147.84** |

### 17.4 Autocorrección (Paso 7)

Todos los ítems son "modificación sobre módulo existente" desde el arranque (no hay reconstrucción desde rangos de "módulo nuevo" que corregir a la baja) — ratio no aplica en el sentido clásico del Paso 7 porque no hay una mediana histórica de "sprint de 9 ítems" comparable; se valida cada ítem individualmente contra su fila de referencia en 27-presupuesto-parametros, todos dentro de rango sin ajuste adicional salvo el ítem 7 (justificación de M ajustado documentada en la tabla).

### 17.5 Sanity check

Comparable más cercano en el dataset: vinosefue "compras al proveedor" (8 ítems, 28.27h PERT-contingencia, CIERRE REAL 4h, ratio 7.07x) y labipac SESIÓN 3 (3 mejoras + 3 fixes, 13.69h PERT-contingencia, CIERRE REAL 2h, ratio 6.84x) — ambos son el mismo patrón de "lote de ítems chicos, evolutivo, sobre sistema propio". Este sprint (9 ítems, 10.22h PERT-contingencia) queda en la misma familia de magnitud, más chico que ambos comparables — razonable dado que la mayoría de los ítems son ajustes de UI/relabel, no features nuevas. Se mantiene sin recalibrar.

### 17.6 Cierre numérico

- **Paso A (preliminar):** USD 147.84 — 4.22h facturables internas (M/2.5×1.20 = 8.8/2.5×1.20) — techo interno 10.22h PERT+contingencia.
- **Paso B:** sin ajuste adicional tras el sanity check. **Tokens IA SÍ aplica** (a diferencia del módulo Fichador): horas facturables 4.22h ≥ piso de 4h → Tokens IA = 147.84 × 0.25 = 36.96.
- **Número a comunicar: USD 185** (148 desarrollo + 37 tokens IA, redondeado). Sin impacto en el plan de mantenimiento anual (sin tablas nuevas).

### 17.7 Tabla para el cliente

| Área funcional | USD |
|---|---:|
| Pantallas del Inversor (Mes actual + Dashboard Histórico) | 34 |
| Rol "Encargado" para el fichador | 17 |
| Fix de cálculo de puntos de inversión | 8 |
| Reparto General simplificado | 8 |
| Historial de Resultados (rename) | 5 |
| Notificaciones — composición y envío por rol | 42 |
| Mi Inversión — tabla de historial reformateada | 17 |
| Fix global de importes en tablas | 17 |
| Uso de infraestructura IA (tokens) | 37 |
| **Total** | **185** |

### 17.8 Condiciones comerciales y exclusiones

- 100% a la entrega (monto bajo, no amerita split 50/50).
- No hay dependencias del cliente pendientes — todos los datos necesarios (rol Encargado, criterio de canal de notificación, etc.) ya quedaron definidos en el Análisis. Único punto abierto: quién es puntualmente el usuario/los usuarios con rol "Encargado" (dato operativo, no bloquea la implementación).
- Excluye: persistencia histórica de fichadas/notificaciones más allá de lo ya modelado; cualquier ítem no listado en `1-analista-funcional.md` §12.

### 17.9 Riesgos y supuestos

- Ítem 7 es el único con riesgo Medio — por ser la pieza de UI más nueva del lote (combo dinámico + chips), aunque reutiliza servicios ya construidos al 100%.
- El fix del ítem 4 se valida contra producción antes de dar por cerrado el ítem (`TotalAsignado = 95` para el período actual) — criterio de aceptación ya validado manualmente en el chat antes de presupuestar (ver `trazabilidad.md`).

### 17.10 Pruebas mínimas requeridas

- Ver criterios de aceptación por ítem en `1-analista-funcional.md` §12.3 — son la base de las pruebas funcionales de este sprint.

---

## 18. Presupuesto — Mi Inversión: dividendos y recupero en pesos (Agosto 2026)

### 18.1 Contexto y Paso 0

Ítem único, Merge sobre sistema propio ya entregado. Ancla en "Modificación sobre módulo existente / agregar regla de negocio" (27-presupuesto-parametros, 1–2h) — 2 campos nuevos en un DTO ya existente, cálculo derivado de datos ya existentes, 2 cards en una vista ya existente. No hay entidad ni pantalla nueva.

### 18.2 Estimación

| Ítem | Referencia | O | M | P | PERT | Riesgo | Cont. | Hs finales | USD (M×16.80) |
|---|---|---|---|---|---|---|---|---|---|
| Dividendos/Recupero en pesos en Mi Inversión (DTO + cálculo + 2 cards) | Agregar regla de negocio 1–2h | 0.5 | 0.7 | 1.3 | 0.73 | Bajo | 8% | 0.79 | 11.76 |

### 18.3 Cierre numérico

- **USD 12** (redondeado). Horas facturables = 0.7/2.5×1.20 = 0.34h — muy por debajo del piso de 4h: **Tokens IA no aplica**.
- Sin impacto en plan de mantenimiento (sin tablas nuevas).

### 18.4 Riesgos y supuestos

- Validado contra datos reales de producción antes de presupuestar: las 264 liquidaciones "Pagada" existentes tienen TC cargado, así que el cálculo es aplicable de punta a punta sin casos borde pendientes.
- Expectativa ya gestionada con el cliente (ver Arquitectura §10.5): el número en pesos va a salir muy similar al de dólares con los datos actuales — no es un defecto de la implementación.

### 18.5 Condiciones comerciales

100% a la entrega (monto mínimo, no amerita split 50/50).

---

## 19. Presupuesto — Sprint de correcciones y catálogo real (Agosto 2026)

### 19.1 Contexto y Paso 0

6 ítems sobre el sistema en producción. Merge sobre sistema propio ya entregado → precio de lista, sin descuento de expansión agresiva. Anclajes: "Ajuste puntual" y "Modificación sobre módulo existente" (27-presupuesto-parametros) para los ítems 1, 2 y 6; "Migración de datos" (sin referencia comparable directa, riesgo alto declarado, mismo criterio que el módulo 14 de Etapa 1) para el ítem 4; "Agregar regla de negocio" con drivers de cálculo financiero para los ítems 3 y 5.

### 19.2 Tabla de estimación

| # | Ítem | Referencia | O | M | P | PERT | Riesgo | Cont. | Hs finales | USD (M×16.80) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FromName del remitente de correos | Ajuste puntual (mínimo) | 0.15 | 0.2 | 0.35 | 0.21 | Bajo | 8% | 0.23 | 3.36 |
| 2 | Mi Inversión — recupero acumulado + gráfico de evolución | Nuevo reporte/tablero 1.5–2h | 1.4 | 2.0 | 3.5 | 2.15 | Bajo | 8% | 2.32 | 33.60 |
| 3 | Editar meses cerrados + recálculo de liquidaciones pendientes + auditoría | Regla de negocio con cálculo financiero + auditoría | 2.4 | 3.5 | 6.0 | 3.73 | **Alto** | 25% | 4.66 | 58.80 |
| 4 | Catálogo real de rubros + remapeo de 373 gastos históricos | Migración de datos (sin comparable directo) | 2.8 | 4.0 | 7.0 | 4.30 | **Alto** | 25% | 5.38 | 67.20 |
| 5 | Importación de Excel recurrente (actualizar en vez de omitir) | Modificación sobre módulo existente | 1.7 | 2.5 | 4.3 | 2.67 | Medio | 15% | 3.07 | 42.00 |
| 6 | Reparto General — orden por año/mes | Ajuste puntual (idéntico a fix ya hecho) | 0.2 | 0.3 | 0.5 | 0.32 | Bajo | 8% | 0.34 | 5.04 |
| | **Totales** | | | **12.5** | | **13.38** | | | **16.00** | **210.00** |

### 19.3 Autocorrección y sanity check

- Ítems 1, 2 y 6 anclados en sus filas de referencia sin desvío. Ítem 6 se estima igual que el fix de orden ya ejecutado en Historial de Resultados (mismo código, misma solución) — coherente con el histórico inmediato.
- Ítems 3 y 4 son los únicos de riesgo Alto del lote y concentran el 60 % del precio: uno toca el cálculo de liquidaciones (plata de inversores), el otro migra datos financieros históricos ya conciliados. La contingencia del 25 % está aplicada solo a esos dos ítems, no al total (evita inflar el lote entero por el riesgo de dos ítems).
- Sanity check: el lote (12.5 h M) es comparable en magnitud al sprint de 9 ítems de §17 (8.8 h M) pero con más peso por ítem — razonable, porque acá dos ítems son de migración/cálculo y no de UI.

### 19.4 Cierre numérico

- **Paso A:** USD 210.00 — 6.0 h facturables (12.5/2.5×1.20) — techo interno 16.00 h PERT+contingencia.
- **Paso B:** sin ajuste. **Tokens IA aplica** (6.0 h facturables ≥ piso de 4 h): 210 × 0.25 = 52.50.
- **Número a comunicar: USD 263** (210 desarrollo + 53 tokens IA). Sin impacto en el plan de mantenimiento (sin tablas nuevas).

### 19.5 Tabla para el cliente

| Área funcional | USD |
|---|---:|
| Remitente de los correos del sistema | 3 |
| Mi Inversión — evolución del recupero mes a mes | 34 |
| Corrección de meses ya cerrados | 59 |
| Carga del catálogo real de rubros y gastos | 67 |
| Importación de Excel recurrente | 42 |
| Orden de los períodos en Reparto General | 5 |
| Uso de infraestructura IA (tokens) | 53 |
| **Total** | **263** |

### 19.6 Riesgos, supuestos y dependencias

- **Ítem 4 no puede ejecutarse sin dos cosas del cliente**: (a) revisión del mapeo de los subgrupos sin equivalencia clara (ver Arquitectura §11.5, filas marcadas ⚠️), y (b) ventana para hacer backup de producción antes de correr la migración.
- **Ítem 5 queda parcialmente bloqueado**: la funcionalidad se puede construir, pero no se puede probar de punta a punta sin los archivos Excel reales, que hoy no están en ningún lado (ni repo ni memoria del proyecto). Se implementa contra la plantilla que el propio sistema genera.
- Ítem 3 revierte una decisión de diseño previa (D-04/P-A04) por pedido explícito del cliente — documentado en Análisis §14.1.
- Supuesto del ítem 2 a validar: el recupero acumulado cuenta solo liquidaciones Pagada, no todas las de meses cerrados.

### 19.7 Condiciones comerciales

50 % al inicio / 50 % a la entrega. Los ítems 1 y 6 (correcciones menores, USD 8 combinados) pueden entregarse por adelantado sin esperar el resto del lote si el cliente los necesita ya.

---

## 20. Cierre de calibración — Módulo E2-01 "Integración Ayres POS" (2026-09-08)

### 20.1 Qué había presupuestado (rectificación)

Se registró primero que "no había estimado contra el cual medir". **Es incorrecto y queda rectificado.** Sí hay dos cifras en el presupuesto original, y ninguna es una cotización cerrada del módulo:

| Origen | Cifra | Qué cubría |
|---|---|---|
| §6, ítem 6 — *"Indicadores de venta (Ayres, manual)"* | M **1,5 h** → **USD 25,20** | La carga **a mano** de los indicadores desde los totalizadores de Ayres. Es lo que el módulo nuevo **reemplaza**. |
| §10, riesgos — ancla metodológica | **15–18 h base** | *"Integración batch, 15–18 h base"* — ancla heredada de una estimación **sin cierre real**, dada de baja del dataset el 2026-09-08 (ver 20.4). Era la única base de comparación disponible al momento de este cierre. |

O sea: la integración estaba **declarada, anclada y explícitamente excluida** del precio ("etapa 2, se cotiza tras relevamiento"). El ancla de 15–18 h es la única base de comparación, y venía marcada como **sin cierre real** — este cierre es el primero que la valida.

### 20.2 Presupuestado vs. real

**Estimado según el ancla** (fórmula vigente `USD = M × 16,80`):

| | M | Horas facturables (M×0,48) | USD lista | + Tokens IA 25 % |
|---|---|---|---|---|
| Piso del ancla | 15,0 h | 7,20 h | 252,00 | **315** |
| Techo del ancla | 18,0 h | 8,64 h | 302,40 | **378** |

**Real medido.** Base de medición: *timestamps de commits* de la sesión (evidencia, no estimación a posteriori) + duración informada por los subagentes. Arranque del flujo tras el commit `87c47d2` (13:43); entrega implementada en `612c623` (14:48); QA y Documentación cerradas ~16:20.

| Concepto | Real |
|---|---|
| Duración total del flujo de 9 etapas | **≈ 2,6 h** |
| — de las cuales, subagente implementador | 21,0 min |
| — de las cuales, subagente QA | 23,5 min |
| — resto (Discovery, Análisis, Diseño, Arquitectura, revisión, deploys, Documentación) | ≈ 1,9 h |
| Horas facturables equivalentes (real × 0,48) | **1,25 h** |
| USD por fórmula (2,6 × 16,80) | **USD 43,68 ≈ 44** |

**Desvío: −82 % contra el piso del ancla, −86 % contra el techo.** El módulo se entregó en aproximadamente **1/6 del tiempo anclado**.

**Detalle de pricing:** con el esfuerzo real, las horas facturables (1,25 h) quedan **por debajo del piso de 4 h**, así que **Tokens IA no aplicaría**. Con el esfuerzo estimado (7,2–8,64 h) sí aplicaba. El propio desvío cambia la estructura del precio, no solo su magnitud.

### 20.3 Por qué el desvío es tan grande — y qué de esto es repetible

**Repetible (reutilización real, no genérica):**
- 3 de 3 coincidencias del escaneo se aplicaron. `AfipTokenCache` de marihogar resolvió el problema más delicado —token que vence, sin logins duplicados— sin escribirlo de cero.
- La estructura de integración de QuickPass ya existía **en el mismo proyecto**: no hubo que decidir convenciones.
- **Cero Domain, cero migración EF.** La escritura se delegó a `GuardarVentasAsync`, o sea que no se tocó lógica financiera.

**No repetible / suerte:**
- El ancla de 15–18 h describía una **integración batch contra una base de datos**, no un consumo REST documentado. La API de Ayres tiene documentación pública y un solo endpoint relevante. Comparar contra ella era, en parte, comparar contra otra cosa — motivo por el cual el ancla terminó dándose de baja.

**Lo que sí consumió tiempo, y no era código:**
- El diagnóstico de conectividad (puerto saliente) y una conclusión errónea del propio orquestador sobre la política del hosting: **un ciclo completo perdido**, resuelto por el dueño desde el panel.
- Dos deploys perdidos rastreando un `400` causado por una placa de atributos cortada al insertar un método.

### 20.4 Ajustes para próximas estimaciones

1. **El ancla "integración batch 15–18 h" deja de estar sin cierre real, pero NO se puede bajar sin más.** Este cierre corresponde a una **API REST documentada con un endpoint**, no a una integración batch contra base de datos. Se propone **desdoblar el ancla**:
   - *Integración REST documentada, 1–2 endpoints, sin persistencia nueva*: **M 3–5 h** (este cierre: 2,6 h real, con reutilización fuerte disponible).
   - *Integración batch / base de datos de terceros*: se mantiene **15–18 h**, todavía sin cierre real.
2. **Al estimar integraciones, el riesgo dominante no es el mapeo de endpoints sino conectividad y credenciales.** En este caso el módulo estuvo bloqueado 26 días por credenciales, y la conectividad saliente consumió más tiempo que escribir el cliente HTTP. **Sugerido: ítem de riesgo separado y explícito de "habilitación de acceso (red + credenciales)" en toda integración con un tercero**, en vez de diluirlo en la contingencia.
3. **Los defectos de datos aparecen contra producción real, no en diseño.** Los dos hallazgos de peso —ventas anuladas que distorsionaban comensales y ticket promedio, y KOI-009— salieron recién al contrastar con datos reales. **Presupuestar explícitamente la verificación contra datos reales** en integraciones que alimentan cálculos financieros.
4. **Advertencia metodológica de fondo (excede este módulo).** Las anclas históricas del estudio están construidas sobre **ejecución humana**, y este flujo se ejecuta con agentes. Si se sigue estimando con anclas humanas y ejecutando así, **todo presupuesto de este tipo va a quedar sobrestimado en un orden de magnitud**. Eso es una decisión de negocio, no de estimación: define si el desvío se captura como margen o se traslada al precio. **Corresponde elevarlo a `olvidata-ceo` antes de recalibrar las anclas hacia abajo** — bajarlas mecánicamente destruiría margen sin que el cliente lo haya pedido.

### 20.5 Cifra a considerar si se factura el módulo

- **Por fórmula sobre el real:** USD 44 (sin Tokens IA, por quedar bajo el piso de 4 h).
- **Por el ancla presupuestada:** USD 315–378.
- **Criterio del estudio aplicable:** "Merge sobre sistema propio ya entregado" → precio de lista, sin descuento de expansión (misma clasificación que E2-02 Fichador, §16).
- **Recomendación:** **no facturar por el real.** El valor entregado no es proporcional al tiempo: el módulo elimina carga manual mensual y, verificado con datos, **corrige indicadores que hoy están mal** (ticket promedio mostrado a menos de la mitad del real). El desvío es margen del estudio por reutilización propia, no un ahorro que corresponda trasladar. Cifra sugerida a comunicar: **en el rango del ancla, USD 315**, decisión final del dueño.
