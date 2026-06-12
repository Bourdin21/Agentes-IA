# 4 - Presupuestador — Proyecto Yoga

> Memoria acumulativa del agente presupuestador.
> Etapa: Presupuesto inicial. Estado: CERRADO (pendiente de aprobación del cliente).
> Fecha: 2026-06-11. Actualizado: 2026-06-12 (v2 — división en Etapa 1 MVP / Etapa 2, sin cláusula de validez). Inputs: definiciones 1, 2 y 3 aprobadas.
> Política de facturación vigente (27-presupuesto-parametros, Junio 2026): **USD por módulo = M × $16.80** (M/2.5 × 1.20 × $35). Las horas PERT con contingencia son techo interno, no base de precio. Tasa USD 35/h sobre horas reales con contingencia temporal 20 %.

## 1. Introducción y contexto de relevamiento

Escuela de yoga sin sistema de gestión. Se presupuesta un sistema web (ASP.NET Core MVC .NET 10 + EF Core + MySQL 8, base blankproject OlvidataSoft) para un único rol Administrador: planes de entrenamiento de 1 a 5 hs semanales con precio propio, suscripciones de alumnos, cuotas mensuales con estados y control de deudores, registro de clases dictadas y liquidación de profesores por hora, cuenta corriente de ingresos/egresos y dashboard de inicio con KPIs financieros. Sin integraciones externas, sin migración de datos, moneda única ARS.

## 2. Alcance funcional (módulos visibles para el cliente)

9 módulos, según definiciones 1–3, divididos en dos etapas de entrega (regla vigente de formato comercial):

- **Etapa 1 — MVP (operación de suscripciones y cobranza)**: acceso del administrador, planes, alumnos, suscripciones, cuotas y pagos con deudores. Es el mínimo que permite a la escuela operar el negocio: registrar alumnos, suscribirlos y cobrar las cuotas.
- **Etapa 2 — Profesores, caja y dashboard**: profesores y clases dictadas, liquidación de profesores, cuenta corriente, dashboard de KPIs. El dashboard se entrega en esta etapa porque sus KPIs financieros dependen de la cuenta corriente.

## 3. Especificaciones técnicas del servicio

| Ítem | Especificación |
|---|---|
| Tecnología | ASP.NET Core MVC (.NET 10), EF Core, MySQL 8, base blankproject OlvidataSoft |
| Frontend | Bootstrap 5 + olvidata-theme, charts JS, DataTables |
| Servidor / hosting | Provisto por OlvidataSoft (cubierto por plan de mantenimiento anual) |
| Despliegue | Web única instancia productiva, acceso por navegador (responsive) |
| Esquema de datos | ~14–15 tablas (8 entidades nuevas + Identity) → plan de mantenimiento PRO |
| Accesos requeridos | Nombres y precios de los 5 planes, día de vencimiento de cuotas, listado de profesores con tarifas |

## 4. Roles y usuarios

| Rol | Acceso |
|---|---|
| Administrador | Acceso total: planes, alumnos, suscripciones, cuotas, profesores, liquidaciones, caja, dashboard |

(Super usuario interno del proveedor: reservado, no se documenta al cliente.)

## 5. Paso 0 — Anclaje histórico (previo a estimar)

Referencias leídas: `koi` (15 mód, M total 69.5 h, mismo método y fórmula vigente), `ganaderia` (8 mód financiero/workflow), `delicias-naturales` (95 h base / 19 mód), `lumitrack` / `recotrack` / `piapartments` (datasets ABM con 30 % incluido, normalizados ÷1.30), rangos por tipo de 27-parametros.

Medianas base usadas como ancla:
- ABM simple: **1.5 h** (recotrack).
- ABM intermedio: **5.0 h** (lumitrack/recotrack/piapartments).
- Workflow con estados: **5.0 h** (rango 4–6 h de 27-parametros, mediana; las referencias delicias 7.7 corresponden a workflows con detalle editable, más pesados que una suscripción).
- Módulo financiero: **6.5 h** (rango 5–8 h de 27-parametros, mediana).
- Caja / cuenta corriente: **5.0 h** (ganaderia "Caja y cuenta corriente", base 5.1 h — referencia directa del mismo módulo).
- Tablero/dashboard: **4.2 h** (ganaderia "Tablero anual"; KOI usó la misma ancla con ajuste +43 % para un dashboard mucho mayor).

## 6. Tabla de estimación por módulo

Distribución interna estándar del esfuerzo de cada módulo (trazabilidad, no aditiva): 70 % implementación, 15 % pruebas, 10 % documentación, 5 % riesgo ordinario.

| # | Etapa | Módulo | Tipo | Drivers | Referencia (Paso 0) | O | M base | M ajust. | P | PERT | Riesgo | Cont. | Hs finales (techo) | Hs fact. (M×0.48) | USD (M×16.80) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | Acceso y cuenta del administrador | ABM simple | login/recuperación reutilizan Identity base; seed usuario admin | recotrack ABM simple 1.5 | 1.0 | 1.5 | 1.5 | 2.5 | 1.58 | Bajo | 8 % | 1.71 | 0.72 | 25.20 |
| 2 | 1 | Planes de entrenamiento (1–5 hs/sem) | ABM simple con drivers | 5 planes seed, precio editable con efecto solo hacia adelante (snapshot en cuotas), unicidad hs/semana | recotrack ABM simple 1.5 | 1.5 | 1.5 | 2.0 | 3.5 | 2.17 | Bajo | 8 % | 2.34 | 0.96 | 33.60 |
| 3 | 1 | Gestión de alumnos | ABM intermedio | ficha + contacto, baja lógica, buscador, historial de suscripciones/cuotas en la ficha | lumitrack ABM intermedio 5.0 | 3.0 | 5.0 | 4.5 | 6.5 | 4.58 | Bajo | 8 % | 4.95 | 2.16 | 75.60 |
| 4 | 1 | Suscripciones a planes | Workflow con estados | estados Activa/Pausada/Finalizada, única activa por alumno, cambio de plan transaccional con historial | rango workflow 27-params 5.0 | 3.5 | 5.0 | 5.0 | 8.0 | 5.25 | Medio | 15 % | 6.04 | 2.40 | 84.00 |
| 5 | 1 | Cuotas mensuales y pagos | Financiero | generación idempotente por período, snapshot de precio, Vencida derivada, anulación con reversión, deudores; registro del pago (el asiento en caja se activa en Etapa 2) | rango financiero 27-params 6.5 | 5.0 | 6.5 | 7.0 | 11.5 | 7.42 | Medio | 15 % | 8.53 | 3.36 | 117.60 |
| | | **Subtotal Etapa 1 — MVP** | | | | | | **20.0** | | **21.00** | | | **23.57** | **9.60** | **336.00** |
| 6 | 2 | Profesores y clases dictadas | ABM intermedio + ABM simple | profesor con tarifa/hora, carga de clases, bloqueo de clases liquidadas, totales por profesor | lumitrack 5.0 + recotrack 1.5 = 6.5 | 4.0 | 6.5 | 6.0 | 9.0 | 6.17 | Bajo | 8 % | 6.66 | 2.88 | 100.80 |
| 7 | 2 | Liquidación de profesores | Financiero / workflow | única por profesor+período, Σ horas × tarifa con snapshot, Pendiente/Pagada, egreso en caja transaccional, reapertura auditada | rango financiero 27-params 6.5 | 4.0 | 6.5 | 6.0 | 10.0 | 6.33 | Medio | 15 % | 7.28 | 2.88 | 100.80 |
| 8 | 2 | Cuenta corriente (caja) | Financiero | ingresos/egresos automáticos referenciados, egresos manuales tipificados, saldo acumulado, filtros, navegación al origen, backfill de ingresos de cuotas pagadas durante la Etapa 1 | ganaderia Caja 5.0 | 3.5 | 5.0 | 5.0 | 7.5 | 5.17 | Medio | 15 % | 5.94 | 2.40 | 84.00 |
| 9 | 2 | Dashboard de inicio (KPIs financieros) | Reporte complejo / tablero | 6 cards KPI, 4 gráficos (12 meses, saldo acumulado, comparativo anual, distribución por plan), tabla de últimos movimientos, estados vacíos | ganaderia Tablero anual 4.2 | 3.5 | 4.2 | 5.0 | 8.0 | 5.25 | Medio | 15 % | 6.04 | 2.40 | 84.00 |
| | | **Subtotal Etapa 2** | | | | | | **22.0** | | **22.92** | | | **25.92** | **10.56** | **369.60** |
| | | **Totales** | | | | | | **42.0** | | **43.92** | | | **49.49** | **20.16** | **705.60** |

Notas de cálculo:
- PERT = (O + 4M + P)/6 sobre M ajustado. Contingencia variable (8/15 %) aplicada **una sola vez**, solo al techo interno de esfuerzo. Ningún ítem con riesgo alto (sin migraciones de datos ni integraciones).
- USD = M ajustado × $16.80 en todos los módulos, sin excepciones.
- Spreads validados: O ≥ M × 0.65 y P ≤ M × 1.80 en los 9 ítems.
- Login/layout/base no se cobran como módulo independiente: reutilización blankproject (absorbidos en módulo 1).
- **Cargo fijo por uso de tokens IA: USD 100, implícito** (regla vigente 27-parametros, actualizada 2026-06-12): se prorratea proporcionalmente dentro de los precios de los módulos de la Etapa 1 con factor 436/336 ≈ 1,2976 — no se muestra como línea ni concepto al cliente. Prorrateo: acceso 25,20→32,70 · planes 33,60→43,60 · alumnos 75,60→98,10 · suscripciones 84,00→109,00 · cuotas 117,60→152,60 (suma exacta 436,00).
- Totales por etapa: **Etapa 1 (MVP) = 336,00 módulos + 100 tokens implícitos = USD 436,00 → se comunica USD 436**; **Etapa 2 = 369,60 → se comunica USD 370**. Total proyecto: 805,60 → **se comunica USD 806** (436 + 370).
- En la Etapa 1 el pago de cuota registra fecha/medio y deja la cuota Pagada; el movimiento de caja correspondiente se genera al activar la cuenta corriente en Etapa 2, con backfill de los pagos ya registrados (incluido en el módulo 8).

## 7. Autocorrección por ítem (Paso 7)

Ratio = PERT base / mediana histórica base comparable. Umbral 0.85–1.15.

| # | Referencia | Ratio | Ajuste aplicado | Motivo |
|---|---|---|---|---|
| 1 | ABM simple 1.5 | 1.06 | mantener | dentro de umbral |
| 2 | ABM simple 1.5 | 1.44 | M 1.5→2.0 justificado (+33 %, causa documentada) | driver real: el precio del plan tiene efecto temporal (snapshot en cuotas) y validación de unicidad 1–5 hs; sigue dentro del techo del rango "ABM simple 1–2 h" de 27-parametros |
| 3 | ABM intermedio 5.0 | 0.92 | M 5.0→4.5 a la baja | simplificación real: ABM directo sin jerarquías, sin adjuntos ni relaciones cruzadas; la ficha consume consultas de otros módulos |
| 4 | Workflow 5.0 | 1.05 | mantener | dentro de umbral; la transición con historial queda cubierta por la mediana del rango |
| 5 | Financiero 6.5 | 1.14 | M 6.5→7.0 justificado | drivers reales: generación idempotente + anulación con reversión + vista de deudores (tres operaciones sobre la misma entidad); en el límite del umbral |
| 6 | ABM int. 5.0 + ABM simple 1.5 = 6.5 | 0.95 | M 6.5→6.0 a la baja | sinergia: ambas piezas comparten patrón ABM y pantalla de carga rápida sin workflow |
| 7 | Financiero 6.5 | 0.97 | M 6.5→6.0 a la baja | simplificación real: cálculo directo Σ horas × tarifa, sin detalle multilínea ni multimoneda (vs liquidaciones KOI con consumos y USD) |
| 8 | ganaderia Caja 5.0 | 1.03 | mantener | referencia directa del mismo módulo en ganaderia (base 5.1 h) |
| 9 | Tablero 4.2 | 1.25 | M 4.2→5.0 justificado (>1.15 documentado) | causa puntual: es la pantalla de inicio pedida explícitamente con "todos los KPI importantes" — 6 cards + 4 gráficos + tabla vs 1 comparativo anual de la referencia; ajuste +19 % < 30 %, menor al aplicado en KOI (4.2→6.0) por tener menos gráficos |

## 8. Sanity check del total del proyecto (Paso 8)

- Comparable elegido: **delicias-naturales** (19 módulos, 95 h base, tipo dominante ABM/financiero) — mismo perfil dominante que Yoga (9 módulos ABM + financiero + workflows).
- Horas base por módulo: Yoga 43.92/9 = **4.88 h/mód** vs delicias 95/19 = **5.0 h/mód** → ratio **0.98** ✔ (dentro de 0.80–1.20).
- Control adicional contra cierres reales (alerta de sobreestimación, 27-parametros): horas reales proyectadas = M total / 2.5 = 42.0/2.5 = **16.8 h**. El patrón "8–11 módulos de complejidad media-alta cierran en 25–30 h reales" da un techo coherente: Yoga tiene 9 módulos pero de complejidad media-baja (dos ABM simples, sin integraciones ni migración de datos), por lo que quedar por debajo del rango es consistente y no indica omisión de alcance.
- Cruce con ganaderia (8 módulos financiero/workflow, M base 80.5 h): ganaderia incluía facturación con correlativo, IVA, cuotas 30/60/90, rechazos y job diario — drivers ausentes en Yoga; la diferencia de escala está explicada por drivers concretos.
- Decisión: **mantener el total sin recalibrar**.

## 9. Cierre numérico por dos pasos (Paso 9)

- **Paso A (preliminar, suma directa de módulos):** USD 705,60 — 20.16 h facturables internas — techo interno de esfuerzo 49.49 h PERT+contingencia.
- **Paso B (tras sanity check del total y validación de contingencia única):** sin ajuste de módulos — ratios por ítem dentro de umbral o justificados, ratio de proyecto 0.98, contingencia aplicada una sola vez (8/15 % solo al techo interno; el precio usa la fórmula M × $16.80 cuyo 20 % temporal ya absorbe la contingencia comercial). Se suma el cargo fijo de USD 100 por uso de tokens IA, implícito y prorrateado en los precios de la Etapa 1 (sin línea visible al cliente).
- **Números a comunicar al cliente: Etapa 1 (MVP) USD 436 (336 módulos + 100 tokens IA) · Etapa 2 USD 370 · Total proyecto USD 806 + USD 300/año (mantenimiento PRO, desde la puesta en producción de la Etapa 1).**
- Horas reales proyectadas por etapa (M/2.5): Etapa 1 = 8.0 h; Etapa 2 = 8.8 h.

## 10. Riesgos y supuestos

- Sin ítems de riesgo alto: no hay migración de datos, integraciones externas ni multimoneda.
- Riesgo medio concentrado en los módulos financieros (cuotas, liquidaciones, caja): transaccionalidad documento + movimiento y reversiones por anulación/reapertura.
- Supuestos de alcance: pago total único por cuota (sin pagos parciales); generación de cuotas manual por período (sin job nocturno); clases dictadas cargadas por el administrador (sin agenda ni asistencia); moneda única ARS.
- Supuestos de la división en etapas: durante la operación del MVP la pantalla de inicio es el listado de cuotas del período; el dashboard llega con la Etapa 2. La cuenta corriente de la Etapa 2 incorpora retroactivamente (backfill) los ingresos de las cuotas pagadas durante la Etapa 1, por lo que la caja nace completa.
- Gatillos de reestimación: pagos parciales, recordatorios a alumnos (email/WhatsApp), acceso de alumnos/profesores al sistema, pasarela de pagos — cualquiera de ellos es cambio de alcance y se cotiza aparte.

## 11. Pruebas mínimas requeridas

- Generación de cuotas: una por suscripción activa, idempotente, monto = precio vigente; suscripciones pausadas/finalizadas no generan.
- Cambio de precio de plan: cuotas existentes inalteradas, cuotas nuevas con precio nuevo.
- Pago de cuota: cuota Pagada + un único ingreso en caja por el mismo monto; doble pago bloqueado; anulación con motivo revierte el movimiento.
- Estado Vencida derivado: cuota Pendiente con vencimiento pasado aparece en Vencidas y en Deudores sin proceso manual.
- Liquidación: Σ horas × tarifa congelada; única por profesor+período; al pagar genera el egreso y bloquea las clases; clase liquidada no editable.
- Cuenta corriente: saldo = Σ ingresos − Σ egresos en todo filtro; navegación al origen desde movimientos automáticos.
- Dashboard: KPIs del mes coinciden con caja; mes sin datos sin errores.

## 12. Checklist de salida para merge

- [ ] Build OK y migración EF inicial aplicada sobre MySQL 8.
- [ ] Seed ejecutado: 5 planes, roles, usuario administrador.
- [ ] Índices únicos verificados (plan por hs/semana, cuota por suscripción+período, liquidación por profesor+período).
- [ ] Pruebas mínimas del §11 en verde, evidenciadas en 6-qa.md.
- [ ] Trazabilidad actualizada y aprobación del cliente registrada antes de implementar.

## 13. Tabla para el cliente (Área | USD — horas internas no expuestas)

**Etapa 1 — MVP (suscripciones y cobranza)** — precios con el cargo de tokens IA ya prorrateado (implícito)

| Área funcional | USD |
|---|---:|
| Acceso y cuenta del administrador | 33 |
| Planes de entrenamiento (1 a 5 horas semanales) | 44 |
| Gestión de alumnos | 98 |
| Suscripciones a planes | 109 |
| Cuotas mensuales, pagos y deudores | 152 |
| **Subtotal Etapa 1** | **436** |

**Etapa 2 — Profesores, caja y dashboard**

| Área funcional | USD |
|---|---:|
| Profesores y registro de clases dictadas | 101 |
| Liquidación de pagos a profesores | 101 |
| Cuenta corriente (ingresos y egresos) | 84 |
| Dashboard de indicadores | 84 |
| **Subtotal Etapa 2** | **370** |

| | |
|---|---:|
| **Total del proyecto (Etapa 1 + Etapa 2)** | **806** |
| Mantenimiento anual — Plan PRO (hosting, seguridad, soporte) | 300/año |

Nota de redondeo: líneas redondeadas al entero sobre los precios prorrateados (Etapa 1: 32,70 / 43,60 / 98,10 / 109,00 / 152,60); la línea "Cuotas mensuales, pagos y deudores" se redondea a 152 (exacto 152,60) para que la suma coincida con el subtotal exacto (436,00). Etapa 2: 369,60 → 370. Total 805,60 → 806.

## 14. Plan de mantenimiento anual

Esquema entregado ≈ 14–15 tablas → rango 6–15 → **Plan PRO: USD 300/año** (hasta 2 usuarios, soporte WhatsApp, 1 ronda de ajuste). Se presenta como línea separada post-desarrollo; rige desde la puesta en producción de la Etapa 1; cubre hosting, seguridad y soporte, no cambios funcionales nuevos.

## 15. Condiciones comerciales y exclusiones

- Cada etapa se abona 50 % al inicio / 50 % a la entrega de esa etapa. La Etapa 2 puede contratarse junto con la Etapa 1 o al finalizar el MVP. Moneda: USD. Sin cláusula de validez de la oferta (regla vigente Junio 2026).
- Exclusiones: pasarela de pagos online; reserva/agenda de clases y control de asistencia; notificaciones por correo/WhatsApp a alumnos; acceso de alumnos o profesores al sistema; migración de datos desde planillas anteriores; facturación electrónica AFIP/ARCA; aplicación móvil; cambios de alcance posteriores al inicio.

## Historial de ajustes
- 2026-06-11: presupuesto inicial v1. 9 módulos, M total 42.0 h, PERT base 43.92 h, techo interno 49.49 h, fórmula vigente M × $16.80 → USD 705,60 + USD 100 tokens IA = USD 806 + USD 300/año (PRO). Sanity total vs delicias-naturales: ratio 0.98, sin recalibrar. Sin ítems de riesgo alto. Pendiente: aprobación del cliente; cierre de calibración estimado vs real al finalizar el sprint.
- 2026-06-12: v2 — nuevas reglas globales de formato comercial (27-parametros): (1) todo presupuesto se divide en Etapa 1 (MVP) y Etapa 2 (resto), (2) se elimina la cláusula de validez de 30 días. Yoga: Etapa 1 (módulos 1–5 + tokens IA) USD 436; Etapa 2 (módulos 6–9) USD 370; total sin cambios USD 806. Sin cambios en horas ni módulos; el módulo 8 documenta el backfill de ingresos de cuotas pagadas durante la Etapa 1. Documento cliente rehecho por etapas.
- 2026-06-12: v3 — regla global actualizada (27-parametros): el cargo de tokens IA (USD 100) pasa a ser implícito — prorrateado proporcionalmente en los precios de la Etapa 1 (factor 436/336 ≈ 1,2976), sin línea visible al cliente. Subtotales y total sin cambios (436 / 370 / 806). Tabla cliente de Etapa 1 reexpresada: 33 / 44 / 98 / 109 / 152.
