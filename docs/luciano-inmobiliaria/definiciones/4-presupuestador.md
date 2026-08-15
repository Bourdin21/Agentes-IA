# Memoria - Presupuestador

## Proyecto: luciano-inmobiliaria
## Ultima actualizacion: 2026-08-14

---

## ⚠️ Segundo rediseño 2026-08-14 — etapa única, PDF+IA incluida, precios ajustados a mercado real

Joaquín pidió tres ajustes sobre la versión anterior (precio de lista USD 1.365, luego USD 1.197): (1) research de cómo se factura honorarios/sueldos — hecho, ver `1-analista-funcional.md` §0.10-4 y §0.12; (2) convención de certificado resuelta (nombre = CUIT); (3) **research de mercado para ajustar precios** — hecho, comparado contra AfipSDK (competidor real, mismo tipo de producto); y pidió **sumar la extracción de contratos por PDF+IA al presupuesto, en una única etapa** (se elimina el concepto de Etapa 1/Etapa 2 para este proyecto — todo lo confirmado va en un solo alcance).

### Paso 0 — Anclaje histórico (sin cambios respecto de la versión anterior, ver ahí el detalle completo)

Motor AFIP, API de emisión, autenticación, ingesta FTP, endpoints administrativos, control de uso: mismas referencias que la versión anterior de este documento. La única pieza que cambia de tratamiento es la extracción de contratos por PDF+IA, que pasa de "candidato de Etapa 2" a **incluida en el alcance único**.

### WBS — Alcance único (reemplaza Etapa 1 + Etapa 2)

| # | Módulo | Tipo | O (h) | M (h) | P (h) | Riesgo | Contingencia | Horas PERT |
|---|---|---|---:|---:|---:|---|---:|---:|
| 1 | Extensión multi-tenant del motor AFIP | Integración externa (reuso + extensión crítica) | 7.5 | 10.0 | 17.0 | Alto | 25% | 10.8 |
| 2 | API de emisión (individual + lote síncrono, tope 50 ítems) — **incluye resolver "por cuenta y orden de terceros" para alquileres (R11)** | Integración externa | 5.8 | 8.0 | 13.5 | Alto | 25% | 8.6 |
| 3 | Autenticación por API key (2 tipos) | Integración/seguridad | 3.5 | 5.0 | 8.5 | Medio | 15% | 5.4 |
| 4 | Ingesta de certificados por FTP (nombre de archivo = CUIT, confirmado) | Integración de archivos + job | 4.5 | 6.0 | 10.5 | Alto | 25% | 6.5 |
| 5 | Endpoints administrativos (alta Suscripción/CUIT/PuntoVenta + cálculo de pack) | ABM complejo sin UI | 3.0 | 4.0 | 6.5 | Medio | 15% | 4.3 |
| 6 | Control de uso anti-reventa + 4 señales técnicas | Workflow + reporte, vía API | 7.5 | 10.0 | 17.0 | Alto | 25% | 10.8 |
| 7 | Puesta en marcha (bootstrap Web API pura) | Deploy/bootstrap | 1.5 | 2.0 | 3.5 | Bajo | 8% | 2.1 |
| 8 | **Extracción de contratos por PDF+IA** (`POST /api/v1/contratos/extraer`, API de Claude) — pasa a alcance confirmado | Integración externa nueva | 4.5 | 6.0 | 10.5 | Alto | 25% | 6.5 |
| | **Total** | | | **37.8** | **51.0** | **86.5** | | | **55.0** |

*Módulo 2 sube de 7.0h a 8.0h M respecto de la versión anterior — driver nuevo: el mecanismo de "por cuenta y orden de terceros" (R11) exige investigar y mapear un campo de WSFEv1 no cubierto por el `AfipService.cs` ya portado.*

**Extras opcionales, no incluidos en este alcance (el cliente no los confirmó, se cotizan aparte si los pide)**: notas de crédito/débito (NC/ND), endpoint de historial/reportería de comprobantes, notificación automática de vencimiento de certificado — ver detalle y estimación en el historial de este documento (versión anterior), sin cambios.

### Cierre numérico

- Subtotal de lista: 51.0h × $16.80 = **USD 856,80**
- Ratio de reutilización: (módulo 1, 10h + módulo 3, 5h) = 15h / 51h = **29,4%** → Tier 3, sin descuento.
- Tokens IA (25%): 856,80 × 0.25 = **USD 214,20**
- **Precio de lista del desarrollo (alcance único): USD 1.071,00**

**Nota sobre costo variable de PDF+IA**: sin cambios respecto de la versión anterior — cada extracción tiene costo de tokens de la API de Claude, no está incluido en el precio fijo de desarrollo. Pendiente definir con Joaquín si se cobra por PDF procesado, se incluye un tope mensual en la suscripción, o el cliente usa su propia cuenta de Anthropic.

## Modelo comercial — precios ajustados a mercado real (2026-08-14)

### Research de mercado (detalle en `1-analista-funcional.md` §0.12)

**AfipSDK** es el competidor más comparable (misma propuesta: API de conectividad a WSFEv1 cobrada por cantidad de CUIT). Precios reales relevados:

| Plan AfipSDK | CUIT | USD/mes | USD/año |
|---|---:|---:|---:|
| Free | 1 | 0 | 0 |
| Pro | 10 | 25 | 300 |
| Growth | 100 | 80 | 960 |
| Startup | 1.000 | 250 | 3.000 |

La tabla de packs anterior (Enterprise ~USD 2.700/año a 100 CUIT) quedaba **~2,8x por encima** del plan Growth de AfipSDK para la misma capacidad. No es una comparación 1:1 perfecta (Olvidata gestiona certificados por FTP en vez de carga manual, agrega control de uso/señales anti-reventa, y arma la lógica de negocio específica de inmobiliarias — AfipSDK es solo el tubo de conexión a ARCA, el resto lo construye el cliente por su cuenta), pero **Luciano tiene capacidad técnica real confirmada** — es una alternativa que evaluarían en serio si el precio de Olvidata se aleja demasiado del mercado.

### Tabla de packs revisada — ancla en AfipSDK + prima moderada (~40-45%) por el valor agregado real

| Pack | CUIT | USD/mes | USD/año | Prima vs. AfipSDK |
|---|---:|---:|---:|---:|
| Base | 1 | 20 | 240 | — (AfipSDK es gratis en este tramo, pero sin gestión ni soporte) |
| Estándar | 2 a 10 | 35 | 420 | +40% vs. Pro (300) |
| Enterprise (Luciano) | 11 a 100 | 115 | **1.380** | +44% vs. Growth (960) |

*Simplificado a 3 tramos (antes eran 6) porque el salto real de negocio está en 1 / hasta 10 / hasta 100 — más tramos no aportaban precisión, solo complejidad. Si Luciano crece más allá de 100 CUIT, próximo ancla de referencia: AfipSDK Startup (1.000 CUIT, USD 3.000/año) — definir ese tramo si/cuando haga falta, no ahora.*

**Luciano cae en Enterprise: USD 1.380/año de lista** (antes USD 2.700 — corrección real de -49% por el research de mercado, no un descuento comercial).

### ⚠️ Override comercial de Joaquín (2026-08-14) — baja 20% adicional sobre el ancla de mercado

`/olvidata-ceo` recomendó explícitamente **no** bajar el precio (el research de FacturaGratis "Multi-CUIT para administradores" — sin precio público, tratado como venta consultiva por ese competidor — refuerza la prima del 44%, no la debilita). Joaquín decidió bajar igual: **-20% sobre USD 1.380/año → USD 1.104/año**. Se registra como decisión explícita del dueño del estudio, no como error de cálculo ni como el resultado "correcto" del research — el research decía lo contrario.

**Nota de consistencia (no bloqueante, a tener presente)**: esta baja aplica solo al tramo Enterprise (el de Luciano). Con esto, la prima de Enterprise sobre AfipSDK Growth baja de +44% a **+15%** (USD 1.104 vs. USD 960), mientras que los tramos Base/Estándar quedan sin tocar en +40%. Es asimétrico a propósito o por decisión rápida — si Joaquín quiere consistencia entre tramos, definirlo en una próxima revisión; no bloquea presentarle la propuesta a Luciano.

### ⚠️ Segundo override comercial de Joaquín (2026-08-14) — otro 20% menos, ahora sobre todo el presupuesto

Joaquín pidió bajar el presupuesto un 20% adicional, esta vez sobre el total (desarrollo + suscripción), no solo la suscripción. Sin nueva recomendación de `/olvidata-ceo` consultada para este segundo tramo — se aplica directo por instrucción explícita, registrado igual que el anterior como decisión del dueño del estudio, no como recálculo técnico.

- Desarrollo: USD 1.071 × 0.8 = **USD 857**
- Suscripción Enterprise: USD 1.104 × 0.8 = **USD 883/año**

**Efecto acumulado de las dos bajas sobre el ancla de mercado**: la suscripción pasó de USD 1.380 (ancla con prima del 44% sobre AfipSDK) a USD 883/año — **8% POR DEBAJO** del plan Growth de AfipSDK (USD 960/año) que es solo conectividad cruda, sin gestión de certificados, sin control de uso, sin lógica de negocio de inmobiliarias. Se registra explícitamente: a este precio, el valor agregado de Olvidata sobre la alternativa de mercado más comparable se está regalando, no cobrando. Si Joaquín quiere revisar esto en el futuro (ej. si el volumen de clientes de este tipo crece y el margen agregado importa), este es el punto de partida para renegociar hacia arriba, no hacia abajo.

### Opción A — SaaS (Olvidata aloja, el cliente nunca recibe el código)

| Concepto | USD |
|---|---:|
| Desarrollo (precio fijo, alcance único, PDF+IA incluida) | **857** |
| Suscripción anual (Enterprise, ~100 CUIT) | **883/año** |

### Opción B — Entrega del código fuente

- 3 años × USD 883 = USD 2.649
- + prima 50-100% = USD 3.974 a USD 5.299
- + desarrollo USD 857
- **Rango: USD 4.831 – 6.156 → ancla conservadora propuesta: USD 5.000**

Condiciones sin cambios: 70% al inicio / 30% a la entrega, cláusula de no-reventa/no-competencia recomendada (24-36 meses, a redactar con asesoría legal).

## Riesgos y supuestos

- R1-R11 heredados de `1-analista-funcional.md` y `3-arquitecto-mvc.md`. Los más relevantes para cerrar esta propuesta:
  - **"Sueldos"**: research indica que probablemente no pertenece a esta API (sistema distinto de ARCA) — confirmar con el cliente antes de dar por cerrado el alcance de tipos de comprobante.
  - **R11**: "por cuenta y orden de terceros" (alquileres) — el módulo 2 ya incorpora esfuerzo para resolverlo, pero el campo exacto de WSFEv1 sigue sin confirmar contra el manual completo.
  - Contraseña del certificado (complemento de R8): convención propuesta (archivo hermano `{cuit}.txt`), no confirmada.
- Riesgo comercial: la tabla de packs y ambas opciones (A y B) son propuestas, no precios cerrados — corregidas una vez con datos reales de mercado, pueden volver a ajustarse si Joaquín tiene más información (ej. el cliente menciona qué paga hoy por algo similar).

## Pruebas mínimas requeridas

Sin cambios respecto de la versión anterior — aislamiento multi-tenant a escala real (R5), ingesta FTP con errores parciales, rechazo con motivo real, lote mixto, bloqueos por certificado vencido/suscripción bloqueada, cálculo de pack al alta/baja de CUIT. Se agrega: prueba específica del caso "por cuenta y orden de terceros" (R11) con un CUIT de propietario real distinto del receptor.

## Checklist de salida para merge

Sin cambios respecto de la versión anterior, se agrega: convención de contraseña de certificado confirmada antes de dar por cerrado el módulo 4.

## Condiciones comerciales

- **Opción A (SaaS)**: desarrollo 50% al inicio / 50% a la entrega; suscripción Enterprise facturación anual desde la entrega.
- **Opción B (código fuente)**: 70% al inicio / 30% a la entrega; cláusula de no-reventa/no-competencia recomendada.
- Sin cláusula de validez de oferta.

## ⚠️ Tercer rediseño 2026-08-14 — consolidación final (certificados reactivos, admin del lado del cliente, async con polling)

Joaquín simplificó/ajustó tres puntos más tras la consolidación de alcance (ver `1-analista-funcional.md` y `2-disenador-funcional.md`): certificados sin seguimiento proactivo de vencimiento (solo mail reactivo si ARCA rechaza), alta de CUIT/puntos de venta consumida por el propio sistema del cliente (no Joaquín manual), e individual+lote pasan de síncrono a **asíncrono con polling** (confirmado, sin webhook).

### WBS — Alcance único, consolidado

| # | Módulo | Ajuste vs. versión anterior | M (h) |
|---|---|---|---:|
| 1 | Extensión multi-tenant del motor AFIP | Sin cambios | 10.0 |
| 2 | API de emisión (individual + lote, incluye R11 "por cuenta y orden de terceros") | Sin cambios (la lógica de negocio de emitir no cambia, solo cuándo se dispara — ver módulo 2b) | 8.0 |
| 2b | **Infraestructura de procesamiento asíncrono** (cola/worker tipo Hangfire, endpoints de consulta de estado por polling para individual y lote) | **Nuevo** — reemplaza el tope de 50 ítems síncrono (R6 sin efecto) | 4.0 |
| 3 | Autenticación por API key (2 tipos) | Sin cambios | 5.0 |
| 4 | Ingesta de certificados por FTP | **Reducido** (-1h): sin job de vencimiento proactivo, solo detección reactiva + mail al fallar | 5.0 |
| 5 | Endpoints administrativos (alta Suscripción/CUIT/PuntoVenta) | **Aumentado** (+1h): ahora los consume el sistema del cliente en producción, no uso manual interno — sube la vara de validación/errores | 5.0 |
| 6 | Control de uso anti-reventa + 4 señales técnicas (exclusivo Joaquín) | Sin cambios | 10.0 |
| 7 | Puesta en marcha | Sin cambios | 2.0 |
| 8 | Extracción de contratos por PDF+IA | Sin cambios | 6.0 |
| | **Total** | | **55.0** |

### Cierre numérico

- Subtotal de lista: 55.0h × $16.80 = **USD 924,00**
- Ratio de reutilización: 15h (módulos 1+3) / 55h = 27,3% → Tier 3, sin descuento de expansión.
- Tokens IA (25%): 924,00 × 0.25 = **USD 231,00**
- **Precio de lista del desarrollo (antes de aplicar el descuento comercial vigente): USD 1.155,00**

### Aplicación del descuento comercial ya vigente (dos rondas del 20%, acumulado -36%, ver entradas anteriores)

El descuento fue una decisión de **precio/estrategia comercial** de Joaquín (no atado a una cantidad de horas puntual) — se reaplica sobre el nuevo precio de lista, igual criterio que las rondas anteriores:

- USD 1.155,00 × 0.64 (0.8 × 0.8) = **USD 739,20 → USD 739**

La suscripción **no se recalcula** — su ancla es de mercado (AfipSDK), no de horas de desarrollo, y el pase a asíncrono no cambia el valor percibido por el cliente del lado de la suscripción. Se mantiene: **USD 883/año**.

### ⚠️ Cierre final v1 — números fijados por Joaquín (2026-08-14), superado por v2 abajo

~~Opción A: USD 850 desarrollo + USD 800/año (año 1 incluido). Opción B: USD 2.000.~~ — ajustado por Joaquín en el mismo intercambio, ver v2.

### ⚠️ Cierre final v2 — ajuste final (2026-08-14)

| Concepto | USD |
|---|---:|
| **Opción A** — Desarrollo (pago único) | **950** |
| **Opción A** — Suscripción anual (Enterprise, ~100 CUIT) | **750/año — primer año incluido sin cargo adicional** |
| **Opción B** — Código fuente completo (pago único) | **2.250** |

**Comparación contra mercado real (research de esta misma sesión, ver `1-analista-funcional.md` §0.12)**:
- **Desarrollo (USD 950)**: sobre 55h M, horas facturables ≈26,4h → **≈USD 36/h efectivo** — por primera vez en todo este proceso de ajustes, queda *por encima* del target de USD 35/h del estudio, no por debajo. Es el único de los tres números que terminó más caro que el estándar interno, no más barato que el mercado externo.
- **Suscripción (USD 750/año)**: comparada con AfipSDK Growth (100 CUIT, USD 960/año, solo conectividad cruda sin nada del valor agregado de Olvidata) queda **21,9% por debajo** — se profundiza el descuento respecto de la ronda anterior (que ya estaba 8-15% debajo según el momento). Sigue siendo el número más alejado del ancla de mercado de los tres.
- **Opción B (USD 2.250)**: sigue muy por debajo de cualquiera de los cálculos de NPV+prima hechos en esta sesión (rangos que fueron de USD 6.000 a USD 17.000 según la ronda) — ~54% por debajo del ancla más reciente (≈USD 4.900) y ~85% por debajo del primer rango calculado por `/olvidata-ceo` (USD 9.300-17.400).

Se documenta sin objeción adicional — decisión final de Joaquín, ya con dos consultas previas a `/olvidata-ceo` sobre esta misma tensión (precio vs. velocidad de cierre).

## Historial de ajustes
- 2026-08-13: presupuesto inicial. Precio de lista USD 1.239, luego USD 1.365 (con señales técnicas).
- 2026-08-14 (rediseño mayor — primera reunión real): alcance pivotado a Web API pura. 57h M base (Etapa1+2), precio de lista USD 1.197. Packs con tramo Enterprise (~USD 2.700/año a 100 CUIT, sin research de mercado todavía). Dos opciones comerciales propuestas (SaaS vs. código) tras consulta a `/olvidata-ceo`.
- 2026-08-14 (override comercial): pese a la recomendación de `/olvidata-ceo` de no bajar el precio (research de FacturaGratis refuerza la prima, no la debilita), Joaquín decidió bajar la suscripción Enterprise un 20% adicional: **USD 1.380 → USD 1.104/año**. Opción B recalculada con el nuevo ancla: **≈USD 6.200** (antes ≈USD 7.500). Registrado como decisión explícita del dueño del estudio. `presupuesto-cliente.md` armado con ambas opciones para revisión de Joaquín.
- 2026-08-14 (segundo override comercial): Joaquín pidió otra baja del 20%, esta vez sobre desarrollo + suscripción completos, sin nueva consulta a `/olvidata-ceo`. Desarrollo: USD 1.071 → **USD 857**. Suscripción: USD 1.104 → **USD 883/año** — queda **8% por debajo** del plan Growth de AfipSDK (conectividad cruda, sin ningún valor agregado de Olvidata), registrado explícitamente como punto a revisar si el volumen de este tipo de cliente crece. Opción B recalculada: **≈USD 5.000** (antes ≈USD 6.200). `presupuesto-cliente.md` actualizado con los números finales.
- 2026-08-14 (tercer rediseño — consolidación final): certificados sin seguimiento proactivo (solo mail reactivo), administración consumida por el sistema del cliente (no Joaquín manual), individual+lote pasan a **asíncrono con polling** (confirmado, sin webhook). WBS sube a 55h M (nuevo módulo 2b de infraestructura async +4h, módulo 4 -1h, módulo 5 +1h). Precio de lista recalculado a USD 1.155, con el descuento comercial acumulado del 36% reaplicado (es una decisión de estrategia de precio, no atada a horas puntuales): **desarrollo final USD 739**. Suscripción sin cambios, USD 883/año (su ancla es de mercado, no de horas). Opción B: **≈USD 4.900**. `presupuesto-cliente.md` actualizado.
- 2026-08-14 (cierre comercial definitivo): Joaquín fijó los tres números finales directamente — **Opción A: USD 850 desarrollo + USD 800/año suscripción (primer año incluido)**; **Opción B: USD 2.000** (código fuente completo). Opción B queda 59% por debajo de la última ancla calculada (≈USD 4.900) — decisión final del dueño del estudio, priorizando cierre de venta sobre margen de esta operación puntual, ya consultada dos veces con `/olvidata-ceo`. `presupuesto-cliente.md` actualizado con estos números — presupuesto listo para enviar.
- 2026-08-14 (segundo rediseño — research + etapa única): (1) research confirma que "sueldos" no pertenece a esta API y que honorarios/alquileres requiere resolver "por cuenta y orden de terceros" (R11, sube el módulo 2 de 7h a 8h M); (2) convención de certificado resuelta (nombre=CUIT); (3) **research de mercado (AfipSDK) corrige la tabla de packs -49%** (Enterprise pasa de USD 2.700 a USD 1.380/año) — la versión anterior no tenía anclaje de mercado real; (4) extracción PDF+IA pasa de "candidato Etapa 2" a **incluida en el alcance único** (ya no hay Etapa 1/Etapa 2 para este proyecto). Precio de lista del desarrollo: **USD 1.071** (51h M). Opción A (SaaS): USD 1.071 + USD 1.380/año. Opción B (código): **≈USD 7.500**, pago 70/30.