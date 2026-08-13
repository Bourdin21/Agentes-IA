# Memoria - Presupuestador

## Proyecto: yaghan-rental
## Ultima actualizacion: 2026-08-12

---

## Presupuesto inicial — Build completo (Etapa 1 + Etapa 2)

### Paso 0 — Anclaje histórico

Proyecto **nuevo desde cero**, sin rondas previas en el propio historial de Yaghan. Referencias usadas por tipo de módulo:

| Tipo de módulo | Referencia elegida | Horas base de la referencia | Motivo |
|---|---|---:|---|
| ABM intermedio (Catálogo, Ventas) | `27-presupuesto-parametros.md` tabla principal | 4–7h, mediana 6h | Sin precedente exacto en el estudio para indumentaria de alquiler; se usa el rango genérico de ABM intermedio. |
| Integración WhatsApp (transporte) | `crm-olvidata` — `WhatsAppClient`/webhook ya portado una vez desde `BotPublicitario` | banda "Integración webhook" 8–10h, reducida por reuso de código ya probado dos veces | Segundo port de la misma infraestructura (BotPublicitario→crm-olvidata→Yaghan) — mismo criterio de descuento por reuso que aplica el estudio a rondas repetidas. |
| Checklist diario / job idempotente | `ganaderia` — `AcreditacionCuotasHostedService`/Novedades | patrón completo, no una extensión — se toma el piso del rango "workflow con estados" (4h) por ser primera implementación del patrón en este proyecto, aunque el patrón en sí ya esté resuelto en otro repo | Es la primera vez que Yaghan tiene este job, pero el patrón (HostedService + bandeja) ya está resuelto y probado. |
| Caja diaria | `la-platense` — `CajaMovimiento`/`CierreCajaDiario` | entidad y lógica ya construidas y cerradas en Entrega 2 (61h totales del lote, caja fue una porción menor) | Reutilización directa de entidades y lógica de cierre, solo cambia `OrigenTipo`. |
| Workflow con estados (Reserva, OrdenTaller) | tabla principal "Módulo con workflow/estados" 4–6h | 4-6h como piso, ajustado al alza por drivers (QR, no-solapamiento de fechas) en Reserva | Sin precedente de máquina de estados de alquiler en el estudio — nueva. |
| Deploy inicial / bootstrap | `contadores-bma-conversor` (deploy 3h real) + precedente cualitativo de La Platense (copiar+sanear `olvidatasoft-crm`) | 2–3h deploy + bootstrap de repo | Se parte de copiar y sanear `la-platense` (decisión confirmada con Joaquín 2026-08-12), no de `blankproject` limpio — más barato que un bootstrap desde cero porque ya trae caja diaria integrada. |

**Verificación de rondas previas:** no aplica — primer presupuesto del proyecto.

### WBS — Etapa 1 (MVP)

| # | Módulo | Tipo | Drivers | Ref. | O (h) | M (h) | P (h) | Riesgo | Contingencia | Horas PERT | Motivo M |
|---|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| 1 | Catálogo de artículos + tarifas por rango de días | ABM intermedio | Relación 1:N a TarifaPorDias, enum Tipo/EstadoFisico, validación de rangos | Mediana ABM intermedio (6h) | 4.5 | 6.0 | 9.5 | Medio | 15% | 6.9 | Sin precedente exacto — mediana estándar |
| 2 | CRM WhatsApp (bandeja + envío/recepción + integración Meta) — **se implementa en Etapa 1; facturación diferida, ver override abajo** | Integración + UI nueva | Port de `WhatsAppClient`/webhook (reuso) + entidades `Conversacion`/`Mensaje` + UI bandeja nueva | Integración webhook 8-10h, piso por reuso | 6.0 | 8.0 | 13.0 | Alto | 25% | 8.5 | Riesgo alto por R1 (migración del número existente) |
| 3 | Cotización | ABM simple con cálculo | Selección de artículos+días, cálculo server-side de tarifa | ABM simple (1-2h) + cálculo | 2.2 | 3.0 | 4.8 | Bajo | 8% | 3.2 | Cálculo simple sobre TarifaPorDias ya resuelta en módulo 1 |
| 4 | Reserva (workflow, QR, comprobante, no-solapamiento) | Workflow con estados | Cabecera+detalle, generación QR, validación de solapamiento de fechas, upload comprobante | Workflow 4-6h, ajustado +50% por 2 drivers extra (QR, solapamiento) | 6.5 | 9.0 | 15.0 | Alto | 25% | 9.6 | Por encima del rango base — justificado por QR + validación de concurrencia (R5) |
| 5 | Listado de reservas | ABM simple (grilla + filtros) | Filtros por estado y fecha | ABM simple (1-2h) | 1.5 | 2.0 | 3.2 | Bajo | 8% | 2.1 | Grilla estándar sobre entidad ya modelada |
| 6 | Devolución (QR + búsqueda manual) | Pantalla dedicada + integración cliente | Lectura de cámara del navegador, librería JS de QR, fallback de búsqueda manual | Workflow 4-6h, ajustado por driver de cámara/QR | 4.5 | 6.0 | 10.5 | Alto | 25% | 6.5 | Riesgo por R4 (soporte de cámara del dispositivo real) |
| 7 | Checklist diario + panel de vencimientos | Workflow/job diario | HostedService idempotente, agregación de 4 fuentes (pagos, ingresos, vencimientos, atrasos) | Piso de workflow (4h), reducido por patrón ya resuelto en ganaderia | 2.5 | 3.5 | 5.5 | Medio | 15% | 3.7 | Patrón ya resuelto, primera implementación en este repo |
| 8 | WhatsApp automático (reseña + aviso de atraso) — **se implementa en Etapa 1, facturación diferida junto con el módulo 2** | Extensión de reglas de negocio | Disparo condicional sobre transición de estado + flag de idempotencia | "Agregar regla de negocio" 1-2h, ajustado por 2 disparadores | 1.8 | 2.5 | 4.0 | Bajo | 8% | 2.6 | Reutiliza `IWhatsAppClient` del módulo 2, solo agrega lógica de disparo |
| 9 | Referentes + comisión por venta/alquiler | ABM simple + cálculo | % configurable por referente, snapshot al cierre de operación | ABM simple (1-2h) + cálculo | 2.2 | 3.0 | 4.8 | Bajo | 8% | 3.2 | Sin precedente de comisión en el estudio — nuevo pero acotado |
| 10 | Proveedores + Compras | 2 ABM simples encadenados | Impacto en stock del artículo comprado | ABM simple x2 (1-2h c/u) | 3.0 | 4.0 | 6.5 | Bajo | 8% | 4.3 | Dos ABM simples relacionados |
| 11 | Talleres (OrdenTaller) | Workflow simple (3 estados) | Bloqueo de stock disponible hasta retorno | Workflow acotado, piso 3h | 2.2 | 3.0 | 4.8 | Bajo | 8% | 3.2 | Máquina de estados simple, sin integraciones |
| 12 | Caja diaria | Módulo financiero — reuso directo | `CajaMovimiento`/`CierreCajaDiario` ya construidos en La Platense | Reuso directo — piso de "modificación sobre módulo existente" (1-1.5h) ajustado por adaptación de `OrigenTipo` | 2.2 | 3.0 | 4.5 | Bajo | 8% | 3.1 | Entidad y lógica ya probadas, solo cambia el enum de origen |
| 13 | Venta directa | ABM intermedio | Con comisión opcional de referente | Mediana ABM intermedio, reducido por reuso del cálculo de comisión (módulo 9) | 3.0 | 4.0 | 6.5 | Medio | 15% | 4.3 | Reutiliza cálculo de comisión ya resuelto |
| 14 | Puesta en marcha (bootstrap repo + deploy inicial) | Deploy/bootstrap | Copiar y sanear `la-platense`, portar módulo WhatsApp de `crm-olvidata` (se implementa en este build, ver módulo 2), deploy en subdominio SmarterASP ya provisionado | Deploy inicial 2-3h + bootstrap | 3.5 | 5.0 | 8.0 | Medio | 15% | 5.4 | Copy+sanitize (no blankproject limpio) reduce el bootstrap; deploy en cuenta ya existente reduce el riesgo de "primer deploy" |
| 17 | Garantía con tarjeta — integración Mercado Pago (autorizar/capturar/liberar) + pantalla de retiro | Integración externa | Tokenización client-side (Bricks/Secure Fields), 3 operaciones de API (autorizar/capturar/liberar) contra Advanced Payments, tie-in con máquina de estados de Reserva, alerta de vencimiento a 7 días en el checklist diario | Integración webhook 8-10h, ajustado al alza por múltiples drivers | 8.0 | 10.0 | 17.0 | Alto | 25% | 10.8 | Primera integración de hold/captura de pago del estudio — sin precedente, riesgo alto documentado (R7-R9) |
| 18 | Depósito alternativo (sin tarjeta compatible) | Registro simple | Alta manual de monto/medio, sin integración externa, mismo patrón que carga de comprobante de pago | "ABM manual reutilizando servicios existentes" 0.5-1h, ajustado por ser parte del flujo de retiro | 1.5 | 2.0 | 3.2 | Bajo | 8% | 2.1 | Registro simple, sin llamada a Mercado Pago |
| | **Subtotal Etapa 1 (implementado completo)** | | | | **55.1** | **74.0** | **120.8** | | | **79.5** | |
| | *de los cuales: módulos 2+8 (CRM WhatsApp), facturación diferida* | | | | *7.8* | *10.5* | *17.0* | | | *11.1* | |
| | *de los cuales: resto del núcleo, pago inicial* | | | | *47.3* | *63.5* | *103.8* | | | *68.4* | |

### WBS — Etapa 2 (fuera del MVP)

| # | Módulo | Tipo | Drivers | Ref. | O (h) | M (h) | P (h) | Riesgo | Contingencia | Horas PERT | Motivo M |
|---|---|---|---:|---|---:|---:|---:|---|---:|---:|---|
| 15 | Cotización inteligente (sugerencia automática de combos) | Mejora sobre módulo existente | Motor de sugerencia por palabras clave sobre el módulo 3 ya construido | "Agregar regla de negocio" 1-2h, ajustado por complejidad del motor de sugerencia | 2.2 | 3.0 | 5.0 | Medio | 15% | 3.3 | Se construye sobre Cotización (módulo 3) ya resuelto, no es un módulo nuevo desde cero |
| 16 | Cobro online con Mercado Pago | Integración externa | Link de pago + confirmación automática por webhook con HMAC | Integración webhook 8-10h | 6.0 | 8.0 | 13.0 | Alto | 25% | 8.5 | Integración de pago sin precedente en el estudio |
| | **Subtotal Etapa 2** | | | | **8.2** | **11.0** | **18.0** | | | **11.8** | |

### Autocorrección por ítem (Paso 7)

Ratio = M / mediana histórica comparable. Umbral 0.85–1.15 mantener; fuera de rango, ajustar o justificar.

| Ítem | Ref. mediana | Ratio M/mediana | Ajuste | Motivo |
|---|---:|---:|---|---|
| 1. Catálogo | 6h | 1.00 | Mantener | En banda |
| 2. WhatsApp | 9h (mediana 8-10) | 0.89 | Mantener | Reducido por reuso de transporte, dentro de banda amplia |
| 3. Cotización | 1.5h (mediana 1-2) | 2.00 | Ajuste documentado | Por encima del rango simple porque incluye cálculo server-side sobre tarifas escalonadas, no un ABM sin lógica |
| 4. Reserva | 5h (mediana workflow) | 1.80 | Ajuste documentado (>30%) | Excede 30% del techo por 2 drivers concretos: generación/validación de QR + validación de solapamiento de fechas (ver R5 en arquitectura) |
| 5. Listado reservas | 1.5h | 1.33 | Mantener | Grilla con más filtros que el ABM simple base |
| 6. Devolución | 5h (mediana workflow) | 1.20 | Mantener | Justificado por driver de cámara/QR, dentro de +30% |
| 7. Checklist diario | 4h (piso workflow) | 0.88 | Mantener | Reducido por patrón ya resuelto |
| 8. Avisos automáticos | 1.5h | 1.67 | Ajuste documentado | Dos disparadores (reseña + atraso) sobre la misma base, no un ajuste único |
| 9. Referentes+comisión | 1.5h | 2.00 | Ajuste documentado | Sin precedente de comisión en el estudio — banda simple no contempla el cálculo de %, se justifica el doble |
| 10. Proveedores+Compras | 1.5h | 2.67 | Ajuste documentado (>30%) | Son 2 ABM encadenados con impacto en stock, no uno solo — de ahí el M mayor a un ABM simple individual |
| 11. Talleres | 4h (piso workflow) | 0.75 | Mantener | Workflow acotado a 3 estados sin integraciones |
| 12. Caja diaria | 1.25h (modif. módulo existente) | 2.40 | Ajuste documentado | Aunque reutiliza la entidad de La Platense, requiere adaptar `OrigenTipo` a 4 valores nuevos y conectar 3 orígenes distintos (venta/alquiler/compra) — más que un ajuste de campo simple |
| 13. Venta directa | 6h (mediana ABM intermedio) | 0.67 | Mantener (reducción justificada) | Reduce por reuso del cálculo de comisión ya resuelto en módulo 9 |
| 14. Bootstrap+deploy | 2.5h (deploy) + bootstrap | 2.00 | Ajuste documentado | Incluye además portar el módulo WhatsApp completo desde `crm-olvidata`, no solo el deploy |
| 15. Combos automáticos | 1.5h | 2.00 | Ajuste documentado | Motor de sugerencia por palabras clave excede una regla de negocio simple |
| 16. Mercado Pago | 9h | 0.89 | Mantener | En banda |
| 17. Garantía con tarjeta | 9h (mediana 8-10) | 1.11 | Mantener | Justificado por 4 drivers (tokenización, 3 operaciones de API, tie-in con Reserva, alerta de vencimiento), dentro de banda amplia |
| 18. Depósito alternativo | 0.75h (mediana 0.5-1) | 2.67 | Ajuste documentado | Sin precedente exacto — se ancla en la fila más baja disponible (registro manual), el doble se justifica por ser parte obligatoria del flujo de retiro (no un ajuste aislado) |

### Sanity check del total del proyecto (Paso 8)

Total M base implementado (Etapa 1 completa, incluye CRM + Etapa 2) = 74.0 + 11.0 = **85.0h**. Proyecto comparable más cercano: **ganaderia** (8 módulos funcionales, 81.5h base / 101.0h PERT, cierre real 20h). Ratio total 85.0/81.5 = 1.04 — dentro del rango 0.80–1.20, sin ajuste global necesario en el cálculo de lista.

### Cierre numérico por fórmula (Paso A/B — valor de lista, referencia de calibración)

- Subtotal de lista resto del núcleo (sin CRM): 63.5h × $16.80 = **USD 1.066,80**
- Subtotal de lista CRM WhatsApp (módulos 2+8): 10.5h × $16.80 = **USD 176,40**
- Subtotal de lista Etapa 2: 11.0h × $16.80 = **USD 184,80**
- Ratio de reutilización (R) sobre el total implementado: ítems anclados en reuso (WhatsApp 8h + checklist 3.5h + caja 3h + bootstrap 5h) = 19.5h / 85.0h = **22.9%** → Tier 3, sin descuento de expansión.
- Tokens IA sobre el total de lista (25%): (1.066,80 + 176,40 + 184,80) × 0.25 = **USD 356,99 ≈ USD 357**
- **Precio de lista calculado (todo implementado): USD 1.785** (mismo total que el cálculo previo — implementar todo no cambia el costo de lista, solo cambia cómo se factura).

### ⚠️ Precio comercial final — override explícito de Joaquín (cerrado 2026-08-13, tercera versión)

Recorrido de esta decisión en la misma sesión: (1) precio de lista completo ≈USD 1.785 → (2) override a USD 850 núcleo + USD 176 CRM facturado aparte, diferido → (3) **versión final**: Joaquín simplificó todo a un **único precio total**, CRM incluido, sin líneas de pago separadas ni cobro diferido.

| Concepto | Se implementa en Etapa 1 | Precio de lista | **Precio comercial final** |
|---|---|---:|---:|
| Desarrollo completo (núcleo + garantía + CRM de WhatsApp) | Sí, todo | USD 1.785 | **USD 850 — pago único, 50/50 arranque/entrega** |
| Mantenimiento anual | — | USD 500/año | **USD 600/año — primer año sin cargo** |

El riesgo de crédito comercial de la versión anterior (entregar el CRM sin cobro asegurado en fecha cierta) queda **sin efecto** — todo se cobra en el mismo pago 50/50 del resto del proyecto, no hay cobro diferido.

**Efecto en tasa efectiva:** USD 850 sobre 74.0h M totales (horas facturables internas 74/2.5×1.2 = 35.5h) ≈ **USD 23,9/h efectivo** — el descuento más agresivo aplicado a un Build en el dataset del estudio, bien por debajo del piso de referencia de USD 30/h (`27-presupuesto-parametros.md`). Registrado como excepción explícita y puntual autorizada por Joaquín (dueño de la política de precios), no como precedente automático. El mantenimiento compensa parcialmente subiendo de lista (600 vs. 500/año, primer año regalado igual que el precedente de Ganadería/La Platense).

**Piso absoluto de USD 280 (regla de expansión agresiva):** no aplica como bloqueo — es para el descuento *calculado* por tier, no para un override manual directo del dueño del estudio. USD 850 sigue muy por encima de ese piso.

## Riesgos y supuestos

- R1–R9 y S1–S3 heredados de `1-analista-funcional.md` y `3-arquitecto-mvc.md` (número de WhatsApp/coexistencia, sin política de seña publicada, deduplicación no persistente, cámara del navegador, no-solapamiento de fechas a nivel Service, máquina de estados no configurable desde UI, vencimiento de 7 días del hold de Mercado Pago, restricción de tarjetas compatibles, tokenización obligatoria).
- Riesgo comercial: es la primera cotización a un prospecto nuevo (Yaghan aún no es cliente confirmado) — el precio no incluye ningún descuento por referido ni promoción de mantenimiento gratis; si Joaquín necesita una palanca de cierre, la política vigente (`27-presupuesto-parametros.md`) es regalar el primer año de mantenimiento caso por caso, no bajar el precio del Build.

## Pruebas mínimas requeridas

Cobertura de las 16 historias de usuario de `2-disenador-funcional.md`, con foco en: no-solapamiento de fechas (creación concurrente simulada), ciclo completo de Reserva→Devolución con y sin daño, disparo único de reseña/aviso de atraso (no reenvío), cálculo correcto de comisión con % variable por referente, cierre de caja único por fecha, lectura de QR en un dispositivo móvil real (no solo mock).

## Checklist de salida para merge

- [ ] Build limpio, 0 errores.
- [ ] Migración EF aplicada y verificada contra base de desarrollo.
- [ ] Smoke test manual de lectura de QR en un celular real (Android e iOS si es posible).
- [ ] Verificación de elegibilidad de "coexistencia" de WhatsApp en Meta Business Manager antes de migrar el número en producción (R1).
- [ ] Pruebas de autorización/captura/liberación de garantía contra el ambiente de pruebas (sandbox) de Mercado Pago antes de ir a producción — nunca probar con tarjetas reales.
- [ ] Guía de pruebas manuales entregada al cliente (el Implementador no ejecuta smoke test funcional, ver `00-operativa-global`).

## Plan de mantenimiento anual

18 tablas (incluye `ConversacionWhatsApp`/`MensajeWhatsApp`, ya que el CRM se implementa en Etapa 1) → rango de lista PREMIUM USD 500/año. **Precio comercial final fijado por Joaquín: USD 600/año, primer año sin cargo** (se cobra desde el año 2) — ver override en la sección anterior.

## Condiciones comerciales

- 50% al inicio / 50% a la entrega de cada etapa.
- Sin cláusula de validez de oferta.
- Tokens IA (25%) y Mantenimiento anual se muestran como líneas separadas, no prorrateadas.

## Historial de ajustes
- 2026-08-12: presupuesto inicial. 16 módulos (14 Etapa 1 + 2 Etapa 2), 73h M base, Tier 3 (sin descuento de expansión, R=26.7%), precio final USD 1.533 (Etapa 1 USD 1.042 + Etapa 2 USD 185 + Tokens IA USD 307), mantenimiento PREMIUM USD 500/año.
- 2026-08-12 (post-presupuesto): agregada la garantía con tarjeta de crédito (pedido del cliente, no estaba en el pedido original). 2 módulos nuevos en Etapa 1 (17. integración Mercado Pago Advanced Payments, 18. depósito alternativo) = +12h M. Nuevo total: 18 módulos, 85h M base, Tier 3 (R=22.9%, sigue sin descuento), precio de lista USD 1.785 (Etapa 1 USD 1.243 + Etapa 2 USD 185 + Tokens IA USD 357), mantenimiento PREMIUM USD 500/año sin cambios (18 tablas, mismo rango).
- 2026-08-12 (segundo ajuste — override comercial, interpretación inicial incorrecta): Joaquín reestructuró la propuesta: (1) fijó el precio final de desarrollo del núcleo en **USD 850**; (2) CRM de WhatsApp facturado aparte; (3) mantenimiento anual **USD 600/año con el primer año sin cargo**. En este paso se interpretó (incorrectamente) que el CRM también salía del alcance técnico de Etapa 1, no solo de la facturación.
- 2026-08-12 (corrección inmediata): Joaquín aclaró que el CRM **sí se implementa en Etapa 1** junto con el resto del sistema — lo único diferido es la facturación de ese módulo (USD 176, sin fecha fija de cobro), no el desarrollo. Revertidos los recortes de scope en `1-analista-funcional.md`, `2-disenador-funcional.md` y `3-arquitecto-mvc.md`; WBS de este documento restaurado a 74h M en Etapa 1 (implementación completa, 85h con Etapa 2). Se agregó nota de riesgo de negocio: el estudio entrega el módulo CRM sin cobro asegurado en fecha cierta, extensión de crédito comercial a un prospecto aún no confirmado. Precio en este paso: pago inicial USD 850 (núcleo) + CRM USD 176 (diferido, sin fecha fija) + mantenimiento USD 600/año (año 1 gratis) + Etapa 2 opcional USD 185.
- 2026-08-13 (cierre final): Joaquín simplificó a un único precio total — **USD 850 cubre todo el desarrollo (núcleo + garantía + CRM de WhatsApp), un solo pago 50/50, sin cobro diferido**. Mantenimiento sin cambios (USD 600/año, primer año sin cargo). Etapa 2 sigue opcional aparte (USD 185, no tocada). Tasa efectiva baja a ≈USD 23,9/h — la excepción de precio más agresiva del dataset del estudio a la fecha, registrada explícitamente como decisión puntual de Joaquín. `presupuesto-cliente.md` reescrito con una sola línea de inversión.
