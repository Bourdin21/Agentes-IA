# Memoria - Analista funcional

## Proyecto: marihogar *(nombre provisional — confirmar con cliente)*
## Ultima actualizacion: 2026-10-02 (CR-86 **Analisis CERRADO y corregido**: el gasto de $617.687 NO era un error -- carga deliberada de una compra en conjunto (procedimiento de CR-81), verificado contra la base (un solo egreso, ningun `Cheque`); se retiran el punto 17 y R-CR86.7. **Presupuesto salteado por pedido del cliente.**, gate pasado con las 4 decisiones del cliente; CR-85 absorbido por decision D4. La medicion contra produccion destapo $5.691.530,00 en 58 gastos bancarios cargados a mano que se solapan con lo que el sistema ya calcula, y el cheque de $617.687 cargado como gasto operativo **sigue vivo**. Entrada previa: Discovery CERRADO, Analisis BLOQUEADO: 4 preguntas al cliente + dependencia de CR-85. Alicuota Ley 25.413 medida sobre el extracto: 0,600% exacto en los 17 cheques de septiembre)

## Definiciones vigentes

> Nota de consolidación (2026-08-16): esta sección agrupa lo que antes eran 12 secciones de nivel 2 apiladas por fecha ("Análisis funcional v2" + "Discovery + Análisis v3" a "v14"). Se mantiene el contenido completo tal cual (sin resumir ni comprimir, dado su volumen y densidad de decisiones de negocio con cifras/CUIT/porcentajes exactos) bajo un único encabezado de nivel 2, ordenado cronológicamente — cada bloque documenta explícitamente cuándo corrige o amplía a uno anterior (ver especialmente CR-13 sobre CR-6, CR-23 sobre CR-6/CR-22, CR-27 sobre CR-19, CR-40 sobre CR-38). Ver `## Historial de ajustes` para el resumen de una línea por versión.

### Análisis funcional v2 — CERRADO 2026-07-06

### Contexto del negocio
- Rubro: venta de productos de decoración y hogar
- Sistema actual: Contagram (gestión de ventas y compras) — a reemplazar completamente
- Canal de captación: anuncios de producto específico en Meta (Facebook / Instagram)
- Canal de contacto del lead: WhatsApp (clic en anuncio → mensaje al número del negocio)
- Cierre de venta: presencial en el local O entrega y cobro a domicilio
- Formas de cobro: efectivo, transferencia, MercadoPago
- Objetivo: sistema de gestión comercial completo que reemplaza Contagram + automatiza captación de leads

### Escala del sistema post-relevamiento
El relevamiento v1 describía un sistema de captación y ventas (10 módulos).
El relevamiento v2 describe un sistema de gestión comercial completo (18 módulos), comparable a Delicias Naturales en alcance.

---

### Módulos confirmados — 18 módulos

### Grupo 1 — Captación y ventas
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M1 | CRM de Leads | Leads desde WhatsApp, máquina de estados, historial | Media |
| M4 | Presupuestador | Cotización multi-línea, PDF | Media |
| M5 | Gestión de ventas | Multi-pago, estados, impacto automático en CC del local, envío WhatsApp (CR-4) | Alta |
| M6 | Entregas a domicilio | Dirección, fecha, cobro en destino, mobile-friendly | Media |
| M8 | Bot WhatsApp | Inbound webhook, reconocimiento de anuncio (referral Meta), preguntas de calificación por producto | **Muy alta** |

### Grupo 2 — Catálogo y stock
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M2 | Catálogo de productos | Precio compra, precio venta, tipo, marca, modelo, categoría, fotos, stock mínimo | Media |
| M3 | Control de stock | Movimientos: compras (M12), ventas (M5), ajuste manual. Alerta stock mínimo | Media |
| M16 | Aumento masivo de precios | Por marca / categoría / modelo · sobre precio compra o venta · previsualización previa obligatoria | Media |

### Grupo 3 — Compras y proveedores
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M12 | Compras a proveedores | Órdenes de compra (estados), líneas de producto, recepción completa → actualiza stock | Alta |
| M13 | Cuenta corriente proveedores | Saldo por proveedor, historial de pagos, deuda pendiente | Media |
| M14 | Gestión de cheques | Cheques 30/60/90 días, acreditación automática (job diario), alertas dashboard | **Alta** |

### Grupo 4 — Financiero del local
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M11 | Cuenta corriente del local | Balance: ingresos (ventas) − egresos (compras + gastos). Sin clientes deudores. | Media |
| M15 | Caja mensual | Ingresos vs egresos del período con filtro y comparativo mes anterior | Media |
| M18 | Gastos varios | Alquiler, servicios, sueldos, fletes, otros. Con categoría e impacto en CC y caja. | Baja-Media |
| M17 | Proyección financiera | Promedio histórico (últimos 3 meses) + compromisos futuros (cheques + OCs pendientes). Alerta de déficit. | Alta |

### Grupo 5 — Facturación
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M7 | Facturación ARCA | Selección de ítems individuales y cantidades de la venta. Factura A/B. CAE + PDF. | **Muy alta** |

### Grupo 6 — Infraestructura y visibilidad
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M10 | Usuarios y roles | Administrador / Vendedor | Baja |
| M9 | Dashboard | KPIs financieros básicos + cheques por vencer + stock crítico + conversión leads | Media |

---

### Procesos principales confirmados

### Proceso de venta
1. Meta Ad (producto específico) → cliente escribe WhatsApp → bot detecta anuncio (referral) → captura nombre + preguntas de calificación → registra Lead
2. Vendedor retoma desde CRM → arma Presupuesto → genera PDF → envía al cliente
3. Cliente aprueba → convierte a Venta → descuenta stock → genera movimiento en CC del local
4. Pago registrado (efectivo/transferencia/MP) → emite factura ARCA con los ítems seleccionados

### Proceso de compra a proveedores
1. Admin crea Orden de Compra → selecciona proveedor + productos + cantidades
2. OC pasa a Confirmada → al recibir mercadería → Recibida → stock se actualiza
3. Admin registra pago: efectivo / transferencia / cheque 30-60-90 / depósito
4. Cheque queda en estado Pendiente → job diario al vencer → pasa a Acreditado → notificación in-app
5. Pago impacta CC del proveedor y CC del local

### Proceso de caja y proyección
1. Ventas → movimientos de ingreso en CC y caja mensual
2. Pagos a proveedores + gastos varios → movimientos de egreso
3. Proyección: promedio últimos 3 meses + cheques por vencer + OCs pendientes = ingresos/gastos estimados próximo mes
4. Si gastos comprometidos > ingresos proyectados → alerta de déficit en dashboard

---

### Máquinas de estados confirmadas (6)

**Lead:** Nuevo → Contactado → Presupuesto enviado → Vendido / Perdido
*(también: Contactado → Visita programada / Entrega programada)*

**Presupuesto:** Borrador → Enviado → [Aprobado → Convertido | Rechazado | Expirado]

**Venta:** Pendiente → Pagada parcialmente → Pagada → [Con entrega pendiente → Entregada] / Cancelada

**Entrega:** Pendiente → En camino → Entregada / No entregada (reagendar)

**Orden de compra:** Borrador → Confirmada → Recibida / Cancelada

**Cheque:** Pendiente → Acreditado *(automático, job diario)* / Rechazado *(manual)*

---

### Criterios de aceptación — módulos nuevos

**M11 — CC Local**
- CA-N1: Cada venta genera automáticamente un movimiento de ingreso en la CC
- CA-N2: Cada pago a proveedor y gasto genera un movimiento de egreso en la CC
- CA-N3: El saldo actual de la CC es visible en todo momento con detalle de movimientos

**M12 — Compras a proveedores**
- CA-N4: OC con múltiples líneas de producto, cantidad y precio de compra
- CA-N5: Al marcar OC como "Recibida", el stock de cada producto se incrementa automáticamente
- CA-N6: Los pagos de la OC soportan efectivo, transferencia, cheque y depósito
- CA-N7: El saldo pendiente de pago de la OC actualiza la CC del proveedor

**M13 — CC Proveedores**
- CA-N8: Saldo adeudado por proveedor con historial de movimientos y pagos
- CA-N9: Los pagos registrados en OCs actualizan automáticamente el saldo del proveedor

**M14 — Cheques**
- CA-N10: Cheque con monto, fecha de vencimiento y cuota (30/60/90 días)
- CA-N11: Cheques con vencimiento en los próximos 30 días aparecen en el dashboard como alerta
- CA-N12: Al pasar la fecha de vencimiento, el cheque pasa automáticamente a "Acreditado" con notificación in-app
- CA-N13: El Administrador puede registrar manualmente un cheque como "Rechazado"

**M15 — Caja mensual**
- CA-N14: Ingresos y egresos del período con filtro de fechas y totales
- CA-N15: Comparativo con el mes anterior visible en la misma vista

**M16 — Aumento masivo de precios**
- CA-N16: Selección de criterio: por marca, por categoría o por modelo
- CA-N17: Selección de precio objetivo: precio de compra, precio de venta, o ambos
- CA-N18: Previsualización obligatoria antes de confirmar — muestra precio actual y nuevo precio para cada producto afectado
- CA-N19: El aumento se aplica solo al confirmar explícitamente después de la previsualización

**M17 — Proyección financiera**
- CA-N20: Promedio de ingresos y gastos de los últimos 3 meses calculado automáticamente
- CA-N21: Compromisos futuros mostrados: cheques por vencer + OCs pendientes de pago en el período
- CA-N22: Alerta visible si gastos comprometidos > ingresos proyectados
- CA-N23: El Administrador puede cambiar el período base de la proyección (1, 3 o 6 meses)

**M18 — Gastos varios**
- CA-N24: Gasto con monto, categoría (alquiler / servicios / sueldos / flete / otro), descripción, forma de pago y fecha
- CA-N25: Cada gasto genera movimiento de egreso en CC del local y en la caja del período

---

### Permisos por rol — actualizados

| Acción | Administrador | Vendedor |
|---|---|---|
| Gestionar catálogo y precios | ✓ | ✗ |
| Aumento masivo de precios | ✓ | ✗ |
| Gestionar stock manual | ✓ | ✗ |
| Ver/gestionar leads | ✓ | ✓ |
| Crear presupuestos | ✓ | ✓ |
| Registrar ventas | ✓ | ✓ |
| Registrar entregas y cobros | ✓ | ✓ |
| Emitir facturas ARCA | ✓ | ✓ |
| Gestionar compras a proveedores | ✓ | ✗ |
| Ver CC proveedores | ✓ | ✗ |
| Gestionar cheques | ✓ | ✗ |
| Registrar gastos varios | ✓ | ✗ |
| Ver CC local y caja mensual | ✓ | ✗ |
| Ver proyección financiera | ✓ | ✗ |
| Ver dashboard completo | ✓ | Parcial (sin financiero) |
| Gestionar usuarios | ✓ | ✗ |
| Configurar bot WhatsApp | ✓ | ✗ |

---

### Supuestos confirmados

- Sistema web responsivo — mobile-friendly obligatorio para vistas de entrega y cobro
- Un único punto de venta AFIP (local)
- Responsable Inscripto — emite Factura A y B
- Ventas solo al contado — no hay clientes con deuda / fiado (P5-A)
- CC del local = balance interno, sin deudores de clientes (P1-A)
- Gastos operativos (alquiler, servicios, sueldos, fletes) se registran en el sistema (P2-B)
- Recepciones de OC siempre completas — sin entregas parciales de proveedores (P3-A)
- Proyección calculada con promedio histórico + compromisos futuros (P4-B)
- Un solo local / una sola caja

### Exclusiones confirmadas
- App móvil nativa
- E-commerce / carrito de compras
- Integración con sistemas contables externos
- Multi-sede / multi-punto de venta
- Transportistas externos (OCA, Andreani)
- Clientes con cuenta corriente / fiado (P5-A)
- Recepciones parciales de OC (P3-A)

---

### Banderas tempranas — v2

| Bandera | Estado |
|---|---|
| Migración EF | Sí — proyecto nuevo, ~22 entidades estimadas |
| Integración ARCA WSAA + WSFE | Confirmada — con selección de ítems parciales |
| Integración WhatsApp Cloud API | Confirmada — referral Meta + preguntas por producto |
| IHostedService — acreditación automática cheques | **Nueva — job diario crítico** |
| 6 máquinas de estado | Confirmadas |
| Módulos financieros con lógica sensible | CC local, caja, cheques, proyección |
| QuestPDF — presupuestos y facturas | Confirmada |

---

### Riesgos y supuestos

| Riesgo | Nivel | Detalle |
|---|---|---|
| Job acreditación cheques: idempotencia | Alto | Debe acreditar exactamente una vez por cheque. Patrón idéntico al job diario de ganadería. |
| Proyección financiera: precisión percibida | Medio | El cliente puede esperar más precisión de la que un promedio simple puede dar. Fijar expectativas en el documento al cliente. |
| Hosting SMARTEASP: job diario compatible | Bajo | Ganadería ya usa el mismo patrón. Compatible confirmado. |
| Certificado ARCA (.p12) del cliente | Medio | Solicitar al cliente antes de iniciar módulo M7. |
| Número WhatsApp dedicado | Medio | Solicitar antes de iniciar M8. |
| Alcance de M9 dashboard puede crecer | Medio | Definir KPIs fijos antes del diseño — no dejar abierto. |

---

### Componentes reutilizables identificados

| Componente | Fuente | Reutilización en marihogar |
|---|---|---|
| `WhatsAppClient.cs` + `MessagingService.cs` | BotPublicitario | M8 — portar a .NET 10 MVC |
| Patrón AFIP WSAA + WSFE (.p12, token 24h) | delicias-naturales | M7 — reimplementar en .NET 10 |
| Job diario idempotente + IHostedService | ganadería | M14 — acreditación automática de cheques |
| Patrón cheques 30/60/90 (cuotas con vencimiento) | ganadería | M14 — referencia directa de implementación |
| Aumento masivo de precios con previsualización | ShowroomGriffin | M16 — reutilizar patrón |
| Stock manual con ajuste | ShowroomGriffin | M3 — reutilizar patrón |

---

### Discovery + Análisis v3 — Feedback de la primera demo (2026-07-27)

Etapa 1 ya en producción. El cliente usó el sistema y trajo 7 pedidos de cambio + 2 tareas de análisis. Se trata como **change request sobre un sistema ya entregado**, no como alcance nuevo desde cero — impacta el presupuesto ya cerrado de Etapa 1 y requiere re-presupuesto propio (ver `4-presupuestador.md`).

### Fuente de reutilización obligatoria
`ganaderia - emo` (`C:\Sistemas\ganaderia - emo`, ver `ruta_repositorio` en su `metadata.md`):
- `Ganaderia.Domain/Entities/Ganaderia/FacturaVenta.cs` — patrón exacto de impuestos editables (Subtotal, `PorcentajeIva`/`MontoIva`, `PorcentajeIIBB`/`MontoIIBB`, `PorcentajeOtrasPercepciones`/`MontoOtrasPercepciones`, Total) a reutilizar para CR-1. No modela tipo de comprobante A/B/C ni "facturado/en negro" — eso es concepto nuevo de este proyecto (no tiene precedente en ganadería, se documenta como tal).
- `Ganaderia.Domain/Entities/Ganaderia/FacturaVentaIngreso.cs` + `Enums/Ganaderia/PlazoCuotas.cs` — patrón de cuota calculada a 30/60/90 días desde una fecha base. Marihogar ya lo reutilizó parcialmente en Sprint 4 (`Cheque.Cuota`), pero sin un campo de fecha base explícito (`FechaEmision`) separado de `FechaVencimiento` — ver CR-2.

### CR-81 — Beneficiario del cheque/echeq distinto del proveedor de la OC *(CERRADO SIN DESARROLLO 2026-09-25 — el caso se cubre con lo que ya existe)*

**Veredicto: no procede como desarrollo.** El caso se carga hoy con la funcionalidad existente, sin migración, sin campos nuevos y sin código. Lo que hacía falta era el **procedimiento de carga**, no una feature. Se documenta abajo porque el procedimiento no es obvio y el error de carga tiene consecuencias fiscales visibles en el Dashboard.

**Caso real que lo disparó** (25/09/2026). Mari Hogar compró mercadería a una fábrica **en conjunto con otra persona**: juntaron la plata entre los dos y pagaron partes distintas del mismo pedido. La **factura del proveedor quedó a nombre de la otra persona**, no de Mari Hogar. Mari Hogar paga su parte con un **echeq**.

**Respuestas del cliente que cerraron el análisis (25/09/2026):**

| # | Pregunta | Respuesta |
|---|---|---|
| P1 | ¿A nombre de quién se emite el echeq? | **A la fábrica** (no a la otra persona) |
| P2 | ¿Hace falta distinguir echeq de cheque físico en el listado? | **No** — "es un cheque más", lo único distinto sería a quién se lo das |
| P4 | ¿El pago se imputa a la OC de la fábrica? | **Sí** — cancela la parte de Mari Hogar, la CC de la fábrica cierra en cero |

Con P1 = "a la fábrica", el beneficiario del documento **coincide** con el proveedor de la OC, que es exactamente lo que el sistema ya asume. Desaparece el único dato que faltaba: `Cheque.Beneficiario` no tiene caso de uso, y `Cheque.EsEcheq` tampoco (P2). **Las tres opciones de alcance (A: beneficiario, B: A + instrumento, C: compra conjunta como concepto) quedan descartadas.**

**Reformulación que hizo caer el pedido original**: el requerimiento llegó como *"una opción nueva de echeq en el listado de formas de pago"*, con la justificación *"este echeq no tiene destinatario porque el proveedor no es nuestro"*. Dos cosas, verificadas en código antes de definir nada:
1. Un `MetodoPago.Echeq` nuevo obligaría a duplicar en `PagoOrdenCompraService` la validación de número/banco/fechas y la creación de la fila `Cheque`, **sin aportar nada**: `MetodoPago.Cheque` se referencia en 8 lugares / 3 archivos, y toda la lógica posterior — proyección financiera, cheques por vencer, acreditación, notificaciones, reversión por rechazo — trabaja sobre la **fila `Cheque`**, nunca sobre el método de pago. Un echeq se registra hoy con método Cheque: número, banco, emisión, vencimiento y días de plazo (libres desde CR-60), y se acredita o se rechaza igual.
2. La premisa "no tiene destinatario" resultó falsa para este caso: el echeq **sí** va al proveedor de la OC. Lo que no es de Mari Hogar es la **factura**, no el destinatario del pago — y la factura no se modela como destinatario de nada.

**Procedimiento de carga del caso (esto es el entregable del CR, va al manual de usuario):**

1. **OC a la fábrica real, con el producto real, y sólo las unidades de Mari Hogar.** La mercadería de la otra persona nunca entra al stock: no es de Mari Hogar. Confirmado por el cliente ("tengo que cargar el nombre de la fábrica y el producto").
2. **`Facturada = false`**, con IVA / IIBB / otros impuestos en **0**. Sin factura a nombre propio no hay crédito fiscal: Posición de IVA suma `OrdenCompra.MontoIva` sólo de las OC con `Facturada=true` en Confirmada/Recibida (`DashboardService.CalcularCreditoFiscalAsync`, CR-80). Marcarla facturada haría que el Dashboard cuente crédito fiscal que Mari Hogar **no puede usar**.
3. **`PrecioCompra` unitario con el IVA adentro.** Ese IVA es costo, no crédito. Cargado así, la rentabilidad real sale bien sin tocar nada: el costo de cada línea de venta se toma del `PrecioCompra` de la última `OrdenCompraItem` recibida antes de la venta (`RentabilidadService`, CR-80). `Total = Subtotal` = lo que realmente salió de la caja.
4. **Si el stock ya se había subido a mano antes de cargar la OC** (es lo que pasó en el caso real): al marcar la OC **Recibida** el stock se incrementa otra vez (`OrdenCompraService.RecibirAsync` postea un `MovimientoStock` de tipo Compra por cada línea), así que la mercadería queda contada **dos veces**. Hay que **revertir el ajuste manual** por la misma cantidad desde el listado de Stock (edición inline, CR-61) — el ajuste a mano era el workaround mientras la compra no estaba cargada, y la recepción de la OC lo reemplaza.
   - **Dejar la OC en Confirmada para no duplicar el stock: descartado.** El `Cargo` en la CC del proveedor se postea recién al Recibir, así que el pago con el echeq sobre una OC nunca recibida dejaría al proveedor con **saldo a favor** (anticipo) en vez de saldada; y el costo histórico de rentabilidad sale de la última `OrdenCompraItem` **recibida** antes de la venta (`RentabilidadService` proyecta `FechaRecepcion`), así que una OC en Confirmada no aporta costo a ninguna venta. La OC tiene que recibirse; lo que se corrige es el ajuste manual.
5. **Valuación de inventario**: si se quiere que también cierre, actualizar a mano el Precio de compra del producto — `InventarioService` valúa con `Producto.PrecioCompra` **actual**, y recibir una OC no lo pisa.
6. **Pago: una línea, método Cheque**, con los datos del echeq. Arranca `Pendiente` (CR-46) y el `MovimientoCCProveedor.Pago` se postea al **acreditar**, no al entregar. Cancela la parte de Mari Hogar y la CC de la fábrica queda en cero (P4).
7. **Nota interna** con el nombre de quién tiene la factura y qué parte puso cada uno — editable en cualquier estado (CR-50). Es el único registro de la compra conjunta, y es deliberado.

**Riesgo vigente (el único que sobrevive al cierre) — R-CR81.3**: los pasos 2, 3 y 4 son **procedimiento, no código**. El sistema no puede saber a nombre de quién está la factura del proveedor, así que no hay validación posible: si el usuario marca la OC como facturada y le carga el IVA, el Dashboard le informa crédito fiscal inexistente y el costo queda subvaluado (sin el IVA que igual pagó). Se cubre en el manual de usuario, no con una validación.

**Hallazgo colateral, no accionado**: el listado de Cheques (`Cheques/Index.cshtml`) muestra una columna "Proveedor" y filtra por proveedor, ambos derivados de `PagoOrdenCompra.OrdenCompra.Proveedor` — es decir, **asume que el beneficiario del cheque es el proveedor de la OC**. Hoy eso es siempre cierto (P1). Si en el futuro aparece un cheque entregado a un tercero, esa columna va a afirmar algo falso, y ahí el alcance a reabrir es la Opción A (`Cheque.Beneficiario` opcional, default = razón social del proveedor, 1 columna nullable, sin cambios en la máquina de estados Pendiente/Acreditado/Rechazado). Queda anotado como punto de reapertura, no como deuda técnica.

**Banderas tempranas**: migración EF **no**. Integración externa **no**. Máquina de estados **no**. Sin impacto en ninguna capa — no se toca código.

**Perfil de cliente**: B2C retail (casa de decoración y hogar), escala mediana — cliente establecido, sistema en producción desde 2026-07 con 80 CRs de recorrido, capacidad de pago demostrada. **Sin gate de presupuesto: no hay desarrollo que presupuestar.**

### CR-80 — Tres métricas de gestión nuevas (inventario, rentabilidad real, IVA) + reestructuración del Dashboard

Pedido explícito del cliente (24/09/2026), sobre una propuesta de 6 métricas candidatas derivadas de la estructura de datos existente. Confirmó 3 y descartó 3:

| # | Candidata | Decisión del cliente |
|---|---|---|
| 1 | Rotación de stock y capital inmovilizado | **Sí** — "implementar explicando al cliente para qué sirve esta métrica" |
| 2 | Margen real con costo histórico (sin migración) | **Sí** |
| 3 | Aging de cobros y pagos (0-30/31-60/61-90/+90) | No |
| 4 | Costo de los medios de pago (recargo de tarjeta) | No |
| 5 | Posición de IVA estimada | **Sí, con prioridad — "muy útil, incluirlo en el dashboard principal"** |
| 6 | Reposición sugerida con demora real por proveedor | No |

Más un cuarto pedido en el mismo mensaje: **"reestructurar información del dashboard con mejoras de UX/UI y reacomodar las cards en base a la info que muestra, en el rol de un diseñador gráfico"**.

### Parte 1 — Inventario: capital inmovilizado, rotación y clasificación ABC

Hoy el activo más grande del negocio (el stock) solo tiene la alerta de "stock crítico" (productos por debajo del mínimo). No existe ninguna métrica que responda cuánta plata está quieta ni qué productos la tienen quieta.

- **Capital inmovilizado** = Σ (`Producto.StockActual` × `Producto.PrecioCompra`) de los productos con stock > 0. Total, y desglosado por Categoría y por Marca.
- **Plata quieta** = el mismo cálculo restringido a los productos **sin ninguna venta en los últimos 90 días** (ventana configurable desde la pantalla: 60/90/180). Es el número que el cliente pidió poder explicar: capital comprado que todavía no volvió a caja.
- **Días de cobertura** por producto = `StockActual ÷ (unidades vendidas por día en los últimos 90 días)`. Responde "con lo que tengo, cuántos días me dura" — se eligió sobre el índice de rotación clásico (ventas ÷ stock promedio) porque es la forma en que el cliente ya razona su reposición, y porque no requiere reconstruir el stock promedio histórico (el sistema no lo versiona). Sin ventas en la ventana → cobertura "sin movimiento", nunca ∞ ni división por cero.
- **Clasificación ABC** (Pareto) sobre la facturación de los últimos 6 meses: A = los productos que acumulan hasta el 80% de las ventas, B = hasta el 95%, C = el resto. **Calculada, no cargada a mano**: es una decisión distinta a la de `la-platense`, donde `Producto.ClasificacionABC` es una columna que el usuario carga o sugiere el importador. Acá no se persiste nada — el dato sale de `MovimientoStock` cada vez que se abre la pantalla, así que nunca queda viejo.
- **Alerta cruzada A + stock crítico**: un producto clase A (explica ventas) por debajo del stock mínimo es la urgencia real de reposición, y hoy se pierde entre los demás productos críticos.

### Parte 2 — Margen real con costo histórico

CR-58 dejó documentada una limitación **aceptada explícitamente por el cliente**: el margen bruto valúa el costo al `Producto.PrecioCompra` **actual**, así que con inflación una venta de hace seis meses muestra un margen inflado (costo de hoy contra precio de entonces). Este CR la corrige sin agregar ninguna columna:

- El costo de cada `VentaItem` se reconstruye con el `PrecioCompra` de la **última `OrdenCompraItem` de ese producto en una OC Recibida con `FechaRecepcion` anterior o igual a la fecha de la venta**. Es el mismo criterio de "costo de la línea de recepción" que `ShowroomGriffin` persiste como `CostoUnitario`, reconstruido desde los datos que marihogar ya tiene en lugar de migrar.
- Si un producto no tiene ninguna recepción anterior a la venta, cae al `PrecioCompra` actual (comportamiento de hoy) y esa venta se cuenta como **no cubierta**. La pantalla informa siempre el **% de ventas valuadas con costo histórico**: sin ese porcentaje el número nuevo sería tan opaco como el viejo.
- Se agrega desglose por **Categoría** y por **Marca**, y el detalle de los productos que más margen aportan y los que lo destruyen (margen negativo o menor al 10%).
- El KPI "Margen bruto" del Dashboard pasa a usar el costo histórico. Se acepta explícitamente que el número del Dashboard **cambie** respecto de lo que mostraba antes: el anterior estaba sesgado, y la card lo aclara.

### Parte 3 — Posición de IVA estimada (prioridad, en el Dashboard)

- **Débito fiscal (IVA ventas)**: `ComprobanteAfip` con `Estado = Emitido` y tipo FacturaA/FacturaB del período, menos las Notas de Crédito (NotaCreditoA/B) Emitidas del período. El IVA de cada comprobante se obtiene con **exactamente la misma fórmula que se declaró a AFIP** (`AfipService.CalcularNetoIva`: neto = total ÷ (1 + tasa), IVA = total − neto, con la tasa de `Afip:PorcentajeIva`). No se inventa un segundo criterio: si la pantalla y lo declarado difirieran, el número no serviría para nada.
- **Crédito fiscal (IVA compras)**: `OrdenCompra.MontoIva` de las OC con `Facturada = true` no canceladas del período. Ese importe ya lo carga el Administrador al confirmar la OC con la factura del proveedor a la vista (CR-1/CR-10), así que es dato transcripto, no estimado.
- **Saldo de IVA** = débito − crédito. Positivo = a pagar; negativo = saldo técnico a favor.
- **Base devengado, por fecha del comprobante** — no por fecha de cobro. Criterio reutilizado de `ganaderia` (v13, PF74): una factura emitida en marzo y cobrada en mayo suma su IVA en **marzo**, que es lo que permite cruzar el número contra el Libro IVA.
- **Rótulo obligatorio en la card, no en un tooltip**: "estimación sobre base devengada, no reemplaza el Libro IVA ni la liquidación del contador" (regla R30 de ganaderia: la pantalla mezcla dos bases contables — caja para ingresos/egresos, devengado para el IVA — y sin rótulo explícito el usuario compara barras que no hablan del mismo período).
- Serie de los últimos 12 meses en gráfico (IVA ventas y compras + línea de saldo), en el Dashboard.

### Parte 4 — Reestructuración del Dashboard

Problema actual medido sobre la pantalla real: 10 cards visualmente **idénticas** en dos filas indistintas (6 + 4), todas del mismo tamaño y peso, mezclando operación del día (ventas de hoy, stock crítico) con finanzas (balance de caja, deuda a proveedores) y con compromisos (cheques, tarjetas). No hay jerarquía: el número más importante y el más accesorio se leen igual, y la única forma de encontrar algo es leer las 10.

Se reagrupa por **la pregunta que responde cada número**, no por el orden en que se fueron agregando. Detalle de layout, jerarquía y estados en `2-disenador-funcional.md`.

### Criterios de aceptación

- **CA-CR80.1** — El capital inmovilizado de la pantalla coincide con Σ (StockActual × PrecioCompra) de los productos con stock positivo, y su desglose por categoría suma exactamente el total.
- **CA-CR80.2** — "Plata quieta" solo incluye productos sin ventas en la ventana elegida; cambiar la ventana de 90 a 180 días nunca aumenta el monto.
- **CA-CR80.3** — Los días de cobertura de un producto sin ventas en la ventana se muestran como "sin movimiento", nunca como 0, ∞ ni error.
- **CA-CR80.4** — Las unidades vendidas de un producto excluyen las ventas canceladas (la reversión de stock las compensa) y los ajustes manuales (`TipoMovimientoStock.Ajuste` nunca cuenta como venta).
- **CA-CR80.5** — La suma de las ventas de las clases A + B + C es igual al total de ventas de la ventana; ningún producto queda sin clase.
- **CA-CR80.6** — El margen con costo histórico usa, para cada línea, el costo de la última recepción **anterior a la fecha de esa venta**; una recepción posterior no cambia el margen de una venta ya ocurrida (invariante verificable: recalcular dos veces con una OC nueva en el medio da el mismo margen histórico).
- **CA-CR80.7** — La pantalla informa el % de ventas valuadas con costo histórico; si es 0% lo dice explícitamente en vez de mostrar el margen como si fuera exacto.
- **CA-CR80.8** — El IVA de un comprobante calculado por la pantalla coincide, peso por peso, con el que se declaró a AFIP para ese comprobante (misma fórmula, misma tasa de configuración).
- **CA-CR80.9** — Una Nota de Crédito Emitida resta del débito fiscal de su mes de emisión.
- **CA-CR80.10** — El IVA se imputa al mes del comprobante (devengado), no al mes del cobro: una factura de un mes cobrada al siguiente no mueve el saldo del segundo.
- **CA-CR80.11** — La card de IVA y el gráfico llevan visible el rótulo de base devengada y la aclaración de que no reemplazan el Libro IVA.
- **CA-CR80.12** — Cada card del Dashboard indica la ventana temporal de su número (período filtrado, últimos 30 días, saldo a hoy, histórico completo). Ninguna cifra queda sin base declarada (KOI-017).
- **CA-CR80.13** — El Vendedor no ve ninguna de las métricas nuevas, y los endpoints nuevos devuelven 403 aunque se los invoque directo (regla REG-010, mismo criterio que los KPI financieros de CR-58).
- **CA-CR80.14** — Ninguna pantalla nueva rompe con base vacía o sin movimientos en la ventana (estado vacío explícito, sin error de consola — KOI-B02).

### Riesgos y supuestos

- **R-CR80.1** — El margen del Dashboard va a **cambiar de valor** el día del deploy (pasa de costo actual a costo histórico). Es una corrección, no un bug, pero el cliente tiene que saberlo de antemano para no leerlo como un error: va en el resumen de entrega y en el texto de la card.
- **R-CR80.2** — La cobertura de costo histórico depende de que las compras estén cargadas como OC recibidas. Productos comprados antes de que el sistema existiera (o cargados por el importador sin OC) caen al costo actual; el % de cobertura hace visible ese límite en vez de esconderlo.
- **R-CR80.3** — La posición de IVA es una **estimación de gestión**: no contempla percepciones, retenciones, notas de débito, ni compras sin factura. Riesgo de que se lea como liquidación fiscal → mitigado con el rótulo obligatorio de CA-CR80.11 (misma mitigación que ganaderia).
- **R-CR80.4** — El IVA de ventas se deriva del total del comprobante porque `ComprobanteAfip` no persiste neto ni IVA desglosados (solo `Total`). Si el día de mañana cambia la tasa configurada en `Afip:PorcentajeIva`, los comprobantes viejos se recalcularían con la tasa nueva. Aceptado por ahora (una sola tasa vigente en todo el historial); si el negocio pasa a manejar varias alícuotas, el desglose hay que persistirlo al emitir.
- **S-CR80.1** — Todas las métricas son de **solo lectura** sobre datos existentes: ninguna columna nueva, ninguna migración EF.
- **S-CR80.2** — El `PrecioCompra` de `OrdenCompraItem` está cargado sin IVA (Subtotal de la OC es "suma de líneas sin impuestos"), igual que `Producto.PrecioCompra`, así que costo y precio de venta se comparan sobre la misma base.

## CR-87 - El aviso de doble conteo del costo de cobranza es casi ciego

**Estado:** levantado 2026-10-02 durante el QA de CR-86, con impacto medido. Pendiente de Discovery. **No es de CR-86: es un defecto ya deployado de CR-83.**

`CostoCobranzaService.PrevisualizarRecalculoAsync` incluye los gastos manuales del rango para avisar del riesgo de doble conteo, filtrando por `Categoria == CategoriaGasto.ComisionesBancarias`. Medido en produccion (2026-10-02), los gastos manuales de comisiones/bancarios vigentes:

| Categoria | Gastos | Monto |
|---|---|---|
| `Otro = 6` | **120** | **$11.479.487,00** |
| `ComisionesBancarias = 7` | **1** | $50.000,00 |

**El aviso ve 1 de 121 gastos, el 0,4% del monto.** El cliente nunca uso la categoria que CR-62 creo para esto: carga en `Otro` y distingue por **subcategoria** de texto libre ("Gastos Bancarios PCIA y payway", "COMISIONES BANCO GALICIA", "cobro cheque").

**Reinterpreta MH-039.** QA habia registrado que en el recalculo *"la pantalla avisaba en rojo con el monto y se cumplio al 93%"*. Ese 93% es sobre el universo que la pantalla **podia** ver, que era de 1 gasto; el universo real era de 121. **El aviso no fallo por poco: no estaba mirando.**

Ratifica por contraste la decision de CR-86 de agrupar el reporte de saneamiento **por subcategoria y no por categoria**: era la unica forma de ver el universo real.

**Candidato a sumar al mismo CR:** los pagos 58, 201 y 203 siguen con `Estado = Pagado` aunque su neto en el ledger sea 0 (hallazgo colateral de MH-053).

## CR-86 - Comision de cobranza cobrada por periodo + impuesto al cheque (Ley 25.413) en compras

**Estado:** Discovery CERRADO 2026-10-01. **Analisis BLOQUEADO**: 4 preguntas al cliente (P-CR86.1 a P-CR86.4), ninguna respondible desde el codigo. El frente B ademas **depende de CR-85** (abierto).

Pedido del cliente, textual (01/10/2026), dos frentes:
1. «la pantalla ConfiguracionCostosCobranza debe poder seleccionar un periodo de dias y se debe mostrar una columna mas en la tabla que calcule el total de comision cobrado en el periodo por plataforma»
2. «hacer lo mismo pero calculando el impuesto al cheque en compras. revisar el archivo consultaMovimientos para saber cuanto es el impuesto al cheque y que cada vez que se haga una compra con cheque que debite como gasto el valor del impuesto al cheque»

---

### Frente A - Total de comision cobrada por periodo en la pantalla de tasas

**Que hay hoy.** `ConfiguracionCostosCobranza/Index` es un **catalogo de configuracion**: 19 filas de `TasaCostoCobranza` (Procesador x Metodo x Cuotas x vigencia) con los porcentajes, filtros por Plataforma/Medio/Cuotas/Vigencia, y ninguna nocion de periodo ni de montos reales. El buscador nativo de DataTables ya estaba apagado a proposito.

**El dato ya existe, no hay que calcularlo de nuevo.** Desde CR-83, cada `PagoVenta` persiste el costo **congelado** al momento del calculo: `CostoComision`, `CostoIva`, `CostoImpuestosBancarios`, `CostoTotalCobranza`, mas `Procesador` y `TasaCostoCobranzaId` (la fila de tasa que se le aplico). Linea base verificada por QA en produccion: 23 movimientos `CostoCobranza` por **$1.301.077,43**; `SUM(CostoIva) = 0,00` sobre esos 23 pagos (ninguna tasa tiene IVA distinto de 0).

**Lo que convierte esto en una pantalla distinta.** Hoy la pantalla responde "cuanto me cobran?" (configuracion). Con la columna nueva pasa a responder tambien "cuanto me cobraron?" (hecho consumado). Son dos naturalezas en una grilla: una fila de tasa **cerrada** antes del periodo va a mostrar comision $0, y eso se lee como error cuando en realidad significa "esta tasa no estuvo vigente". El rotulo tiene que nombrar lo que el numero mide (corolario de MH-033 / CA-84.10, el mismo problema que origino el cambio de rotulo de la CC Local).

**Hallazgos que condicionan el alcance:**
- **H-CR86.1 - "por plataforma" no es la granularidad de la tabla.** El pedido dice «por plataforma»; la tabla es por **tasa** (plataforma + medio + cuotas). Son dos entregables distintos: una columna por fila, o un resumen agrupado por plataforma arriba de la grilla. -> **P-CR86.1**.
- **H-CR86.2 - "comision" es ambiguo y el rango es de ~3x.** `CostoComision` sola no es lo que el banco cobra: `CostoTotalCobranza` = comision + IVA + IIBB + Ley 25413, y en Payway los impuestos bancarios son 1,80% ARBA + 0,60% Ley 25413 sobre una comision de base. Mostrar una u otra cambia el numero que el cliente va a conciliar contra el extracto. -> **P-CR86.2**.
- **H-CR86.3 - pagos sin tasa atribuida.** Los `PagoVenta` anteriores a CR-83 tienen `TasaCostoCobranzaId` nulo y `CostoComision = 0`: no se atribuyen a ninguna fila. El total por filas **no va a cerrar** contra el total del periodo si se los cuenta aparte. Hay que decidir si la pantalla declara el residuo o lo esconde.
- **H-CR86.4 - que fecha imputa.** Rentabilidad ya fijo el criterio y lo rotula: "costo de cobranza **por fecha de acreditacion**" (`PagoVenta.FechaAcreditacionEfectiva`), no por fecha de venta. El frente A tiene que usar el mismo criterio o la pantalla nueva va a dar distinto que Rentabilidad para el mismo mes. **Se adopta como supuesto S-CR86.1, no como pregunta.**
- **H-CR86.5 - ya existe una pantalla con filtro de periodo sobre este mismo dato.** `ConfiguracionCostosCobranza/Recalcular` recorre un periodo y recalcula. El filtro de rango de dias del frente A es el mismo patron de `daterangepicker` + filtro persistido en sesion que ya usan CC Local, Rentabilidad, Gastos y Ordenes de compra. **Reutilizacion directa, no hay diseno nuevo de filtro.**

---

### Frente B - Impuesto al cheque (Ley 25.413) en compras

#### La alicuota, medida (no supuesta)

`docs/consultaMovimientos.xls` es el extracto del **Banco Provincia, cuenta 5020-50461/8, 31/08/2026 al 30/09/2026**, 190 movimientos, emitido 30/09/2026 11:17. El impuesto aparece con dos leyendas: `IMPUESTO DEBITO - LEY 25413` (60 movimientos, **-$46.823,49**) e `IMPUESTO CREDITO -LEY 25413` (25 movimientos, **-$45.064,72**).

**La alicuota es 0,600%, y en los cheques es exacta sin una sola excepcion.** Los 17 `CHEQUE DE CAMARA` del periodo suman **$7.412.930,03** y su impuesto al debito suma **$44.477,57**: tasa efectiva **0,600000**. Cada cheque, uno por uno, da 0,006000 contra su propio impuesto (el movimiento de impuesto aparece inmediatamente antes del cheque en el extracto).

Verificacion cruzada sobre el resto del extracto: de los 85 pares impuesto-movimiento, **73 dan 0,6% exacto** y los 12 restantes se desvian solo por redondeo a 2 decimales sobre importes de centavos (ej.: $11,00 de comision de clearing -> $0,07, que es 0,6364% por el redondeo, no por otra alicuota). **No hay una segunda alicuota en los datos.**

> El sistema ya conoce este impuesto: `TasaCostoCobranza.PorcentajeLey25413` esta en **0,60%** para Payway. Lo que falta no es el concepto, es aplicarlo del lado de las **compras**.

#### Lo que el extracto dice ademas, y que el pedido no cubre

El impuesto al debito del mes es **$46.823,49**, de los cuales solo **$44.477,57 (95%)** son cheques. El resto son otros debitos que tambien pagan 0,6%: `PAGO VISA` ($255.501,70), `RETENCION ARBA` ($135.193,70), una transferencia de $150.000, comision de paquete $65.000. **Y hay $45.064,72 mas de impuesto al credito** (0,6% sobre cada acreditacion: cobros de tarjeta, transferencias de los socios, depositos). Si el objetivo de fondo es que la caja del sistema cuadre contra el extracto, limitar el alcance a cheques deja **$47.410,64 del mes** afuera - mas que lo que entra. -> **R-CR86.3**.

#### Hallazgos que condicionan el alcance

- **H-CR86.6 - "cada vez que se haga una compra con cheque" no es cuando el banco lo cobra.** El banco debita el impuesto el dia del **debito en camara**, que es cuando el cheque se cobra, no cuando se emite. En el sistema eso es `Cheque.FechaAcreditacion` (`ChequeService.AcreditarAsync`), y los cheques de MariHogar son a 30/60/90 dias: entre emitir y cobrar hay hasta **90 dias** y el gasto cambia de mes. Si el gasto se postea al emitir, se le imputa a un periodo en el que el banco todavia no cobro nada. -> **P-CR86.3**, y **S-CR86.2** como recomendacion.
- **H-CR86.7 - depende de CR-85, que esta abierto.** `AcreditarAsync` hoy postea el movimiento del proveedor **y** el egreso de caja con `cheque.FechaVencimiento`, bajo un supuesto que QA ya refuto con datos: **27 de 29 cheques acreditados ($9.745.379,65, 92% del monto)** tienen vencimiento distinto del dia de acreditacion, y 3 por $1.452.133,30 cruzan de mes. Si el impuesto se cuelga de esa misma fecha, nace con el defecto de CR-85 adentro. Si usa `FechaAcreditacion`, el impuesto y el egreso del cheque que lo origina quedan en fechas distintas. **No hay opcion limpia hasta que CR-85 cierre.** -> bloqueo tecnico, no comercial.
- **H-CR86.8 - CR-82 permite revertir la acreditacion, asi que el gasto tiene que poder anularse.** Un cheque Acreditado puede volver a Pendiente. Si el impuesto queda posteado, se duplica exactamente como MH-040 (el egreso futuro sobrevive, la reversion se fecha hoy, y el monto se cuenta dos veces). El flujo de reversion es parte del alcance, no un agregado.
- **H-CR86.9 - "que debite como gasto" tiene un destino ya construido y un riesgo conocido.** `CategoriaGasto.ComisionesBancarias = 7` existe desde CR-62 y un `Gasto` ya postea egreso a la CC Local. Pero MH-039 es exactamente el accidente que esto puede repetir: un gasto cargado a mano **mas** el costo automatico = el mismo costo contado dos veces en Caja, Gastos operativos, CC Local y en el promedio que proyecta los meses futuros. Hoy el cliente carga estos impuestos a mano o no los carga (la conciliacion de septiembre encontro **$222.244,68 de impuestos bancarios sin registrar**). Al automatizar, hay que decidir que pasa con los ya cargados a mano. -> **P-CR86.4**.
- **H-CR86.10 - alicuota parametrizable o constante?** La Ley 25.413 cambio de alicuota por decreto varias veces. Hardcodear 0,6% obliga a un deploy el dia que cambie; parametrizarla con vigencia (mismo patron que `TasaCostoCobranza`, que ya resuelve "una tasa no se borra, se le cierra la vigencia") hace explicable el costo de los cheques viejos. **Se recomienda parametrizar: S-CR86.3.** No es pregunta al cliente, es decision de diseno.
- **H-CR86.11 - retroactividad.** Hay **29 cheques acreditados historicos**; ninguno tiene su impuesto registrado. Backfillearlos es un trabajo de la naturaleza de CR-84 (que necesito 4 corridas de QA y 4 defectos para cerrar), no un efecto colateral de este CR. **Fuera del alcance inicial salvo pedido explicito.**

---

### Alcance inicial

**Incluido**
1. Filtro de rango de dias en `ConfiguracionCostosCobranza/Index`, persistido en sesion (patron ya existente).
2. Columna nueva en la grilla de tasas con el monto real cobrado en el periodo, atribuido por `PagoVenta.TasaCostoCobranzaId`, imputado por fecha de acreditacion.
3. Rotulo que diga que mide el numero y que significa un $0.
4. Calculo y posteo automatico del impuesto Ley 25.413 (0,600%) sobre cada cheque de compra, como gasto, en el momento que defina P-CR86.3.
5. Anulacion del gasto del impuesto al revertir la acreditacion (CR-82).
6. Totalizado del impuesto al cheque por periodo, en pantalla.

**No incluido (declarado, no omitido)**
- Impuesto al **credito** (0,6% sobre acreditaciones): $45.064,72 en septiembre.
- Impuesto al debito de los **no-cheques** (transferencias, pagos de tarjeta, retenciones): $2.345,92 en septiembre.
- Retencion ARBA de compras ($135.193,70 en septiembre) e Impuesto de Sellos.
- Backfill de los 29 cheques acreditados historicos.
- Computar como credito fiscal el IVA del costo de cobranza (alcance ya declarado y abierto por QA en CR-83).
- Conciliacion automatica contra el extracto bancario.

### Supuestos
- **S-CR86.1** - El frente A imputa por `PagoVenta.FechaAcreditacionEfectiva`, mismo criterio y mismo rotulo que Rentabilidad. Si no, las dos pantallas dan distinto para el mismo mes.
- **S-CR86.2** - El impuesto al cheque se devenga al **acreditarse** el cheque, no al emitirlo, porque es cuando el banco lo cobra. Sujeto a P-CR86.3.
- **S-CR86.3** - La alicuota se parametriza con vigencia, no se hardcodea.
- **S-CR86.4** - El impuesto se postea como `Gasto` (no como egreso directo al ledger), para que lo vean Caja, Gastos y la CC Local por el camino ya construido.
- **S-CR86.5** - El frente A es **solo lectura**: ninguna columna nueva, ninguna migracion. El frente B **si** necesita migracion (alicuota parametrizable + trazabilidad del gasto hacia el cheque que lo origino).

### Riesgos tempranos
- **R-CR86.1** - **Doble conteo** del impuesto si el cliente ya cargo alguno a mano. Es MH-039 otra vez, y MH-039 paso con el 93% de los casos bien resueltos: alcanzo 1 de 14 para romper 4 pantallas.
- **R-CR86.2** - El frente B hereda el defecto de CR-85 si se cuelga de `FechaVencimiento`. **Recomendacion: no implementar el frente B antes de CR-85**, o implementarlo con `FechaAcreditacion` y aceptar que el impuesto y el egreso del cheque quedan en fechas distintas hasta que CR-85 cierre.
- **R-CR86.3** - El cliente puede leer "ya esta cubierto el impuesto al cheque" y esperar que la caja cuadre con el extracto. Con el alcance pedido se cubre el 95% del impuesto al debito y **0%** del impuesto al credito. El rotulo tiene que decirlo.
- **R-CR86.4** - La columna nueva puede no cerrar contra Rentabilidad por H-CR86.3 (pagos sin tasa atribuida). Hay que medir el residuo en produccion **antes** de disenar, no despues de que el cliente lo encuentre.
- **R-CR86.5** - Mezclar configuracion y hechos consumados en una grilla es el patron que ya genero CA-84.10. Riesgo de comunicacion, no de calculo.

### Preguntas abiertas (bloquean Analisis)
- **P-CR86.1** - El total, va como **columna por fila de tasa** (plataforma + medio + cuotas, 19 filas) o como **resumen agrupado por plataforma** (2-3 numeros) arriba de la grilla? El pedido dice «una columna mas» y tambien «por plataforma», que en esta tabla son cosas distintas.
- **P-CR86.2** - "Total de comision cobrado": solo la **comision** de la plataforma, o el **costo total** (comision + IVA + IIBB + Ley 25413), que es lo que efectivamente sale del bolsillo? Pueden diferir ~3x en Payway.
- **P-CR86.3** - El impuesto al cheque, se registra cuando se **entrega** el cheque al proveedor, o cuando el cheque se **acredita** (que es cuando el banco lo cobra)? Con cheques a 30/60/90 dias la diferencia es de hasta 3 meses y cambia el mes al que se le imputa el gasto. *(Recomendacion del estudio: al acreditarse.)*
- **P-CR86.4** - Hay impuestos bancarios ya cargados a mano como gasto en el sistema? Si los hay, se dan de baja, se dejan y el automatico arranca desde una fecha de corte, o se revisan uno por uno? Sin esto, el impuesto se cuenta dos veces.

### Condicion de paso a Analisis
Las 4 preguntas respondidas, **y** una decision explicita sobre R-CR86.2 (si el frente B espera a CR-85 o arranca con `FechaAcreditacion`). El frente A puede avanzar a Analisis con solo P-CR86.1 y P-CR86.2 respondidas: **los dos frentes se pueden desacoplar y el A no tiene bloqueo tecnico.**


### Analisis CR-86 - CERRADO 2026-10-02

**Decisiones del cliente (01/10/2026), gate de Analisis pasado:**
- **D1** - El monto que se muestra es el **costo total** (comision + IVA + IIBB + Ley 25413), no la comision sola. Resuelve P-CR86.2.
- **D2** - **Columna por fila de tasa + totales por plataforma** arriba de la grilla. Resuelve P-CR86.1.
- **D3** - El impuesto al cheque se devenga **al acreditarse el cheque**. Resuelve P-CR86.3 y confirma S-CR86.2.
- **D4** - **CR-85 entra adentro de este CR.** Resuelve R-CR86.2 por la via mas grande: el sprint arregla la fecha de asiento de los cheques y recien sobre esa base agrega el impuesto. Consecuencia: CR-86 toca codigo en vivo ya deployado (`ChequeService.AcreditarAsync`) y absorbe el alcance de CR-85, que se cierra por fusion.

#### Medicion contra produccion (2026-10-02, solo lectura)

Todo lo que sigue sale de consultas directas a `db_a7251f_marihog`, no de supuestos.

**Frente A - el universo real es chico y hay que decirlo en pantalla**

| Medicion | Valor |
|---|---|
| `PagoVenta` **con** tasa atribuida | **26** (costo total $1.301.077,43) |
| `PagoVenta` **sin** tasa atribuida (`TasaCostoCobranzaId` nulo, costo $0) | **730** |
| Comision sola vs costo total | $1.230.378,52 vs $1.301.077,43 |
| Meses con costo posteado | **uno solo: 2026-09** |
| Pagos con costo pero **sin** `FechaAcreditacionEfectiva` | **11, $85.742,36** (6,6% del total) |

Costo total por plataforma, 2026-09: **Mercado Pago $768.568,20** (11 pagos, impuestos bancarios $0), **Payway $517.869,27** (8 pagos, de los cuales $56.058,95 son impuestos bancarios), **Banco Directo $14.639,96** (4 pagos, comision $0 -- todo su costo son impuestos bancarios).

- **Correccion a H-CR86.2:** el Discovery estimo que comision y costo total podian diferir "~3x en Payway". **Con los datos reales difieren 5,7% en el agregado** ($1.230.378,52 vs $1.301.077,43), porque hoy ninguna tasa tiene IVA cargado y los impuestos bancarios solo pegan en Payway y Banco Directo. El 3x era teorico y los datos lo desmienten. **D1 sigue siendo la decision correcta** (es el numero conciliable contra el banco, y el dia que se cargue IVA la brecha se abre), pero el argumento es otro: no es magnitud, es que el costo total no depende de como esten cargadas las tasas.
- **H-CR86.3 confirmado y cuantificado:** 730 de 756 pagos no se atribuyen a ninguna fila. La columna nueva describe 26 pagos de un mes. **Sin un rotulo que lo diga, la pantalla parece decir que el negocio pago $1,3M de comision en toda su historia.**
- **H-CR86.12 (nuevo):** los 11 pagos sin `FechaAcreditacionEfectiva` caen fuera del filtro si se imputa solo por ese campo. Hay que hacer `COALESCE(FechaAcreditacionEfectiva, Fecha)`, que es lo que hace la medicion de arriba, o el periodo pierde $85.742,36.

**Frente B - dimension del impuesto**

| Medicion | Cheques | Monto | Impuesto 0,6% |
|---|---|---|---|
| Acreditados (historico, impuesto **nunca** registrado) | 29 | $10.578.712,98 | **$63.472,28** |
| Pendientes (van a devengar entre 02/10 y 25/11/2026) | 16 | $6.920.424,74 | **$41.522,55** |
| Rechazados | 2 | -- | no devengan |

**CR-85, revalidado con datos de hoy:** de los 29 cheques acreditados, **27 tienen vencimiento distinto del dia de acreditacion** y **3 cruzan de mes por $1.452.133,30**. El numero no se movio desde que QA lo midio el 30/09.

#### El hallazgo que cambia el alcance: P-CR86.4 se responde SI, y es grande

El Discovery preguntaba si habia impuestos bancarios cargados a mano. **Los hay, y no son un residuo: son el vehiculo de un doble conteo de millones.**

| Subcategoria cargada a mano | Gastos | Monto | Rango | Nota |
|---|---|---|---|---|
| `Gastos Bancarios PCIA y payway` | **58** | **$5.691.530,00** | 30/05/2025 - **06/08/2026** | |
| `cobro cheque` | 14 | $3.076.045,00 | 09/06/2025 - 04/10/2025 | |
| `COMISIONES BANCO GALICIA` | 6 | $247.851,00 | 14/10/2025 - 22/04/2026 | |
| `gastos bancarios payway pcia` | 2 | $98.000,00 | 12/08/2026 - 19/08/2026 | |
| `cheque` | 1 | $617.687,00 | 28/09/2026 | *(carga deliberada, ver correccion abajo)* |

Tres consecuencias:

1. **`Gastos Bancarios PCIA y payway` es exactamente lo que el sistema ahora calcula solo.** 58 gastos por $5.691.530,00 de cargas agregadas que mezclan comision de Payway y gastos del Banco Provincia -- o sea comision de cobranza **e** impuestos bancarios, los dos conceptos que CR-83 automatizo y que CR-86 va a extender a los cheques. Llegan hasta **agosto de 2026**, no son historia vieja. Encender el automatismo sin fecha de corte apila el calculo sobre estas cargas. **Es MH-039 otra vez, pero con dos ordenes de magnitud mas de plata**: MH-039 fue $50.000 en 1 gasto de 14 y alcanzo para romper 4 pantallas.
2. **CORRECCION (2026-10-02, tras verificacion y respuesta del cliente): el gasto de $617.687,00 NO es un error.** El analisis lo habia reportado como cheque cargado como gasto operativo y contado dos veces. **Es falso, y se verifico contra la base:** no existe ninguna fila en `Cheques` con ese numero ni con ese monto, no existe `PagoOrdenCompra` asociado, y el unico asiento en el ledger es el gasto id 531 (`MovimientosCCLocal` 1274, 28/09/2026, origen `Gasto`, descripcion "Otro - cheque compra factura colomar cannon"). **Un solo egreso, no dos.** El cliente confirmo que la carga es deliberada: fue una **compra en conjunto con un tercero** cuya factura quedo a nombre del tercero, y se quiere registrar asi. Es exactamente el procedimiento de carga que **CR-81 cerro sin desarrollo** el 25/09 (los 7 pasos para el manual). **Queda fuera del alcance de CR-86 por decision del cliente: la logica de este cheque se desestima** y el gasto no se toca ni se reporta.
3. **MH-039 sigue abierto:** la categoria `ComisionesBancarias` tiene **1 gasto de $50.000 en todo 2026**, que es el "COMISION MP" del 14/09 que QA reporto sin anular.

#### Alcance cerrado

**A. Comision cobrada por periodo (`ConfiguracionCostosCobranza/Index`)**
1. Filtro de rango de dias persistido en sesion, `daterangepicker`, default **mes actual** -- mismo patron que CC Local, Rentabilidad y Gastos. Reutilizacion directa, sin diseno nuevo.
2. Columna nueva **"Cobrado en el periodo"** por fila de tasa, con `SUM(PagoVenta.CostoTotalCobranza)` de los pagos cuya `TasaCostoCobranzaId` es esa fila (D1).
3. Tarjetas de total **por plataforma** arriba de la grilla (D2), sobre el mismo periodo.
4. Imputacion por `COALESCE(FechaAcreditacionEfectiva, Fecha)` (H-CR86.12), con el rotulo de Rentabilidad: "por fecha de acreditacion".
5. Rotulo obligatorio del residuo: la pantalla declara cuantos pagos del periodo **no** tienen tasa atribuida y por cuanto, para que el total por filas sea explicable (H-CR86.3).
6. Solo lectura: ninguna columna nueva, ninguna migracion.

**B. Fecha de asiento de los cheques (CR-85 absorbido, D4) -- va PRIMERO**
7. `ChequeService.AcreditarAsync` asienta el movimiento de CC Proveedor y el egreso de caja con **`Cheque.FechaAcreditacion`**, no con `FechaVencimiento`. Los dos ledgers con la misma fecha, que es el dia real de salida.
8. Correccion de fecha de un pago ya registrado extendida a **todos** los metodos, no solo Transferencia (`ActualizarFechaPagoTransferenciaAsync` cubre hoy un solo metodo; el pago 441 de Mercado Pago quedo sin camino de correccion).
9. ~~Backfill de los 29 cheques acreditados para reasentar las fechas.~~ **FUERA DE ALCANCE por decision del cliente (2026-10-02):** *"dejar los datos de los cheques en produccion como estan, estan cargados por el usuario"*. Las fechas historicas no se tocan. Lo que queda de CR-85 es el camino **en vivo** (punto 7): de aca en adelante cada acreditacion asienta los dos ledgers con la fecha del extracto.

**C. Impuesto al cheque (Ley 25.413)**
10. Alicuota **parametrizable con vigencia** (S-CR86.3), sembrada en **0,600%** -- medida sobre el extracto, no supuesta. Misma semantica que `TasaCostoCobranza`: no se borra, se le cierra la vigencia.
11. Al acreditar un cheque (D3), se postea un `Gasto` por `Monto x alicuota`, fecha = `Cheque.FechaAcreditacion`, en la misma transaccion que el egreso del punto 7.
12. Trazabilidad del gasto hacia el cheque que lo origino (campo nuevo, migracion), para que sea anulable e idempotente.
13. Al revertir la acreditacion (CR-82), el gasto del impuesto se **anula**. Sin esto es MH-040.
14. **Fecha de corte** configurable: el automatismo no postea impuesto para cheques acreditados antes de la fecha de corte, para no apilarse sobre los $5.691.530,00 de cargas manuales (hallazgo 1 de arriba).
15. Totalizado del impuesto del periodo en pantalla, con el mismo filtro del frente A.

**D. Saneamiento de datos (nuevo, derivado del hallazgo)**
16. Reporte de los gastos cargados a mano que se solapan con lo que el sistema ya calcula: 4 subcategorias, **$9.113.426,00 en 80 gastos** (sale el de $617.687,00 por la correccion de arriba). **El reporte se entrega; que se anule o no lo decide el cliente, gasto por gasto.** No se anula nada automaticamente.
17. ~~El cheque de $617.687,00 del 28/09/2026 se corrige antes del backfill.~~ **ELIMINADO 2026-10-02**: la carga es deliberada (compra en conjunto, procedimiento de CR-81) y el cliente pidio desestimar la logica de este cheque. No hay doble conteo que corregir. El backfill del punto 9 **no lo alcanza**, porque no existe como `Cheque` en el sistema.

**Fuera de alcance (declarado)**
- **El gasto de $617.687,00 del 28/09/2026 y la logica de ese cheque** (decision del cliente, 02/10/2026): compra en conjunto con un tercero, factura a nombre del tercero, procedimiento de CR-81. No se corrige, no se reporta, no entra en el backfill.
- **Presupuesto (etapa 4): SALTEADO por pedido explicito del cliente** (02/10/2026). Se pasa de Arquitectura directo a Implementacion. Misma excepcion que ya se aplico en kite-punta-lara.
- Impuesto al **credito** ($45.064,72 en septiembre) e impuesto al debito de no-cheques ($2.345,92).
- Retencion ARBA de compras ($135.193,70 en septiembre), Impuesto de Sellos, comisiones de clearing.
- Impuesto sobre los 29 cheques historicos ($63.472,28): el punto 14 los deja fuera por fecha de corte. Si el cliente lo quiere, es un backfill aparte con su propio QA.
- IVA del costo de cobranza como credito fiscal (abierto desde CR-83).
- Conciliacion automatica contra el extracto.

#### Criterios de aceptacion

**Frente A**
- **CA-86.1** - Con un rango de fechas seleccionado, cada fila de tasa muestra el costo total de cobranza imputado a esa tasa en ese rango. Verificable: con 01/09 al 30/09/2026 la suma de la columna da **$1.301.077,43**.
- **CA-86.2** - Las tarjetas por plataforma dan **Mercado Pago $768.568,20 / Payway $517.869,27 / Banco Directo $14.639,96** para 2026-09, y su suma coincide con la suma de la columna.
- **CA-86.3** - El total de la pantalla para un mes coincide **exactamente** con el costo de cobranza que informa Rentabilidad para el mismo mes. Si difiere, una de las dos esta mal.
- **CA-86.4** - Los 11 pagos sin `FechaAcreditacionEfectiva` ($85.742,36) quedan **dentro** del periodo que les corresponde por `Fecha`. Un periodo que los excluya falla el criterio.
- **CA-86.5** - La pantalla declara en texto cuantos pagos del periodo no tienen tasa atribuida. Sobre todo el historial son **723** = 730 crudos − 6 pagos dados de baja (filtro global de EF, `PagoVenta : SoftDestroyable`) − 1 pago vivo de venta cancelada (`NOT EXISTS`, MH-029). Los universos no se solapan: de los 4 pagos sin tasa de ventas canceladas (675, 681, 714, 748), 3 ya estan soft-deleted y vivo queda solo el 675 ($678.905,78, venta 656).
- **CA-86.6** - Una tasa con vigencia cerrada antes del periodo muestra $0 **y** el rotulo explica que significa (no se lee como error).

**Frente B / CR-85**
- **CA-86.7** - Acreditar un cheque postea el movimiento de CC Proveedor y el egreso de caja con **la misma fecha**, y esa fecha es `FechaAcreditacion`. Es el criterio que CA-84.1 no podia alcanzar.
- **CA-86.8** - **NO APLICA al historico por decision del cliente (2026-10-02).** El backfill de fechas salio del alcance, asi que los cheques ya acreditados **siguen asentados por vencimiento** en la cuenta corriente del proveedor y los **3 casos que cruzan de mes ($1.452.133,30: pagos 362, 407 y 339) quedan asi**. Es un estado **conocido y aceptado**, no un defecto pendiente. Para los cheques que se acrediten de aca en adelante el criterio lo cubre CA-86.7.
  El original medi­a **caja vs proveedor** y el backfill mide **proveedor vs acreditacion**: el pago 339 solo aparece en el segundo, y por eso se habia perdido. Dato que cierra la cuenta: de los 29 cheques acreditados, **24 tienen egreso de caja y los 24 ya lo tienen con `DATE(caja) = DATE(FechaAcreditacion)`** (cero excepciones, es herencia de CR-84); los **5 restantes no tienen egreso en absoluto** ($2.224.700,00, las exclusiones MH-036). O sea **el backfill alinea un solo ledger, el de proveedores**, y la afirmacion del implementador de que "no toca la caja" es **correcta y medida** — para 24 porque ya estan bien, para 5 porque no hay caja que tocar.
- **CA-86.9** - La fecha de un pago ya registrado se puede corregir desde la UI para **todos** los metodos. Verificable sobre el pago 441 (Mercado Pago), que hoy no tiene camino.
- **CA-86.10** - Acreditar un cheque de $100.000 genera un gasto de **$600,00** exactos, fechado el dia de la acreditacion.
- **CA-86.11** - Revertir la acreditacion deja el gasto del impuesto **anulado** y el total del periodo baja $600,00. Re-acreditar deja **a lo sumo un gasto VIGENTE por cheque**: puede existir una fila `Gasto` nueva con la anterior anulada, porque el ledger es inmutable y PAT-020 prohibe borrar. Lo que no puede pasar es que haya dos gastos de impuesto vigentes para el mismo cheque, ni que el total del periodo los cuente dos veces.
- **CA-86.12** - Cambiar la alicuota a 1,2% con vigencia desde una fecha no altera el impuesto ya calculado de los cheques anteriores.
- **CA-86.13** - Ningun cheque acreditado **antes del 01/09/2026** (la `VigenteDesde` de la alicuota) genera gasto de impuesto. Verificable: los **10** cheques acreditados en agosto ($3.958.765,39) no generan impuesto.
- **CA-86.14** - Los 16 cheques pendientes ($6.920.424,74), al acreditarse, generan **$41.522,56** en total. El redondeo es **por cheque**, igual que el banco (verificado 17 de 17 en el extracto), no sobre la suma: por eso se verifica cheque por cheque y no contra el total.
- **CA-86.17** - Los **19 cheques ya acreditados con fecha >= 01/09/2026** ($6.619.947,59) **si** generan su impuesto: **$39.719,67**, cada uno fechado en su propia `FechaAcreditacion`, visible en el gasto y en el movimiento de caja. Se verifica cheque por cheque.
- **CA-86.18** - Un pago cuyo neto en el ledger de proveedores es 0 queda **excluido** de la correccion de fecha, con un mensaje que diga por que ("este pago fue reversado; su fecha es historica"). Verificable: los pagos **58**, **201** y **203** no son corregibles. En produccion hay 5 grupos con neto total 0.

**Saneamiento**
- **CA-86.15** - El reporte lista los **80** gastos solapados por **$9.113.426,00**, agrupados por subcategoria, y **no anula ninguno**.
- **CA-86.16** - El reporte de saneamiento **excluye** el gasto de $617.687,00 del 28/09/2026 y cualquier otro gasto de la subcategoria `cheque` que corresponda a una compra en conjunto con un tercero. Son cargas deliberadas del procedimiento de CR-81, no solapamientos. Verificable: el gasto id 531 no aparece en el reporte.

#### Vigencia de la alicuota y universo del impuesto (estado vigente)

`VigenteDesde` = **01/09/2026** (decision del cliente). La `VigenteDesde` **es** la fecha de corte: no hay parametro aparte (AC-86.4).

| | Cheques | Monto | Impuesto 0,6% |
|---|---|---|---|
| Acreditados antes del 01/09 — no generan (CA-86.13) | 10 | $3.958.765,39 | — |
| Acreditados desde el 01/09 — backfill **del impuesto** (CA-86.17) | 19 | $6.619.947,59 | **$39.719,67** |
| Pendientes — al acreditarse (CA-86.14) | 16 | $6.920.424,74 | **$41.522,56** |

**Riesgo de doble conteo del tramo nuevo: nulo, verificado.** Los gastos manuales de comisiones/bancarios terminan el **19/08/2026**; desde el 01/09 hay un solo gasto de esa familia ($50.000,00 del 14/09, "COMISION PERCEPCION MP"), que es comision de Mercado Pago y no impuesto al cheque (MH-039, abierto, otro concepto).

**El backfill del impuesto sigue en alcance; el de fechas no.** Son dos pasos independientes y hubo que **desacoplarlos**: el posteo del impuesto vivia dentro del recorrido del reasiento, detras de un `continue` que saltea cheques omitidos, asi que con el reasiento fuera el impuesto tiene recorrido propio sobre los 19. El impuesto se fecha con la `FechaAcreditacion` **ya guardada**, que no se modifica en ninguno de los dos escenarios, asi que no depende del reasiento para quedar bien fechado.

**El impuesto se cuenta solo en todo el sistema y no hay que tocar pantallas:** ninguna filtra gastos por una lista explicita de categorias (las vistas enumeran con `Enum.GetValues<CategoriaGasto>()`), asi que al ser un `Gasto` con su egreso ya entra en Caja, Cuenta corriente del local, Gastos operativos y el promedio que proyecta los meses futuros. **Limite:** el impuesto **no** va a la cuenta corriente del proveedor — es cargo del banco, no deuda con el proveedor.

#### Reglas de negocio
- **RN-86.1** - El impuesto de la Ley 25.413 lo cobra el banco el dia del debito en camara. En el sistema, ese dia es `Cheque.FechaAcreditacion`. Ninguna otra fecha describe el hecho.
- **RN-86.2** - Un gasto de impuesto no existe sin el cheque que lo origina: se crea con el, se anula con el, y nunca se duplica.
- **RN-86.3** - La alicuota con la que se calculo un impuesto no se reescribe. El costo de un cheque viejo tiene que seguir siendo explicable con la tasa que estaba vigente ese dia.
- **RN-86.4** - Una pantalla de configuracion que empieza a mostrar hechos consumados tiene que rotular los dos planos. El numero dice que midio y de que universo (corolario de MH-033 / CA-84.10).
- **RN-86.5** - Lo que tiene neto 0 en un ledger inmutable esta cerrado: no se refecha, no se edita, no se vuelve a abrir. Si hay que rehacerlo, se postea un hecho nuevo.

#### Riesgos actualizados
- **R-CR86.1 (elevado a ALTO, con monto)** - Doble conteo contra $5.691.530,00 en 58 gastos de "Gastos Bancarios PCIA y payway" que llegan hasta agosto 2026. Mitigacion: fecha de corte (punto 14) + reporte de saneamiento (punto 16). **Sin la fecha de corte este CR empeora los numeros del cliente.**
- **R-CR86.2 - CERRADO por D4.** CR-85 entra adentro; el frente B se construye sobre la fecha corregida.
- **R-CR86.6 (nuevo)** - El punto 9 (backfill de 29 cheques) reescribe fechas de un ledger que se declaro inmutable. Es la misma naturaleza que CR-84, que necesito **4 corridas de QA y 4 defectos** para cerrar. Es la parte cara del sprint y la que decide el presupuesto, no el frente A.
- ~~**R-CR86.7**~~ - **RETIRADO 2026-10-02.** Se habia declarado un error de datos activo por el gasto de $617.687; la verificacion contra la base lo desmiente (un solo egreso, ningun `Cheque` asociado) y el cliente confirmo que la carga es intencional. **Leccion para el metodo: un gasto que "parece" un cheque mal cargado puede ser el procedimiento documentado de CR-81. Verificar contra `Cheques` antes de llamarlo doble conteo.**
- **R-CR86.3** - Se mantiene: el alcance cubre el 95% del impuesto al debito y 0% del impuesto al credito. El rotulo lo tiene que decir.

#### Condicion de paso a Diseno
Cerrado. Las 4 preguntas estan respondidas, P-CR86.4 se respondio con datos de produccion, y el alcance incorpora lo que esa medicion destapo (puntos 14, 16 y 17). **Diseno arranca por el frente B/CR-85** (es el que condiciona al resto) y debe escanear `docs/patrones/cat_resumen.txt` antes de proponer pantalla nueva: el filtro de periodo y el totalizador por grupo ya existen en cuatro pantallas del propio proyecto.


## CR-85 — El ledger asienta los cheques por vencimiento, no por el día en que salió el dinero

**Estado:** Discovery CERRADO 2026-09-30, con impacto medido por QA contra producción y **levantado formalmente** como condición del GO de CR-84. **No entra en el sprint de CR-84**: toca el camino en vivo que ya está deployado. Pendiente de Diseño, Arquitectura y presupuesto.

Evidencia adicional de la verificación independiente de QA (corrida 4): los **2 únicos** pagos que el backfill de CR-84 deja imputados a un mes distinto al del ledger hermano son precisamente los dos que este CR explica — pago **407** ($564.799,96: caja 25/09 por la acreditación, proveedor 23/10 por el vencimiento, acreditado 28 días *antes* de vencer) y pago **362** ($354.000,01: caja 01/09, proveedor 31/08). En los dos, el egreso de caja queda en el mes **correcto** y es el movimiento de proveedor el mal fechado, lo que aísla el problema en este CR y no en CR-84.

### El supuesto que resultó falso
`ChequeService.AcreditarAsync` postea el movimiento de la cuenta corriente del proveedor con `cheque.FechaVencimiento`, y el comentario del código lo justifica así: *"Fecha = vencimiento del cheque (cuando realmente salio el dinero)"*. El supuesto es falso en la práctica, porque el Administrador acredita el cheque cuando lo ve debitado en el extracto, que no es el día del vencimiento.

### Impacto medido (QA, contra la base de producción, 30/09/2026)
- **27 de los 29 cheques acreditados** tienen vencimiento distinto al día de acreditación: **$9.745.379,65, el 92% del monto**. Desvío promedio 2,56 días, máximo 17.
- **3 cheques por $1.452.133,30 cruzan de mes**, así que quedan imputados a un período que no es el suyo.
- El pago **407** se acreditó **28 días antes** de vencer: el ledger asienta en octubre plata que salió en septiembre.
- Caso que lo destapó: pago **364**, cheque #30, $495.200,00 — venció el 05/08 y se acreditó el 22/08, doce días después del ajuste de apertura que supuestamente lo contenía.

### Dónde duele
1. **Conciliación por fecha.** Es el punto 4 del alcance de CR-84 (comparar el flujo mensual del ledger contra el extracto de una cuenta). Con el 92% del monto de cheques asentado en una fecha aproximada, el mes no cierra contra el banco por construcción.
2. **`ProyeccionFinancieraService`.** Proyecta los cheques por vencimiento y después los asienta por vencimiento, así que el sistema **nunca registra cuándo salió la plata**: no hay forma de medir el desvío entre lo proyectado y lo real, que es justamente para lo que sirve una proyección.
3. **La regularización de CR-84** tuvo que resolverlo por su cuenta (ver la excepción de CA-84.1 y el defecto MH-038): el egreso de caja va a llevar la fecha correcta, `Cheque.FechaAcreditacion`, y el movimiento de proveedor va a seguir con el vencimiento. El resultado es que los dos ledgers difieren en esos casos — no por un defecto de CR-84, sino como síntoma de este problema.

### Alcance inicial propuesto
1. El movimiento de proveedor de un cheque se postea con **`Cheque.FechaAcreditacion`** (el dato ya existe y ya se guarda), no con el vencimiento.
2. Corrección retroactiva de los 27 movimientos ya posteados, con el criterio de inmutabilidad del ledger que corresponda — probablemente corrección en el lugar de la fecha, como ya hace `ActualizarFechaPagoAsync`, y no un par de contramovimientos, porque no cambia ningún importe.
3. Revisar `ProyeccionFinancieraService` para que el desvío entre el vencimiento proyectado y la acreditación real sea medible.
4. Revisar el comentario del código que afirma lo contrario, para que no vuelva a inducir el error.
5. **`GastoService.AnularAsync` no pasa fecha** al contramovimiento, así que usa el default `DateTime.UtcNow`. Encontrado en vivo el 2026-09-30 durante la regularización: la corrida se hizo a las 21:55 de Argentina, que en UTC ya es 00:55 del día siguiente, y los 12 contramovimientos quedaron fechados **01/10/2026** mientras los gastos que revierten eran de septiembre — el mes quedaba con el costo contado dos veces y octubre con un crédito ajeno. Se corrigieron a mano. La reversión de un hecho se fechea con el hecho que revierte, no con el momento de la acción, y el proyecto tiene `HorarioArgentino` (PAT-010) sin usar en este método. Impacto histórico medido: ninguno, porque ventas y gastos se cargan con fecha elegida por el usuario; el riesgo está en todo lo que postea con el default.

### Riesgo
Toca el ledger financiero en vivo y mueve de mes $1.452.133,30 ya asentados, así que cambia números que el cliente ya vio. Requiere QA sobre la corrección retroactiva con el mismo cuidado que el backfill de CR-84 — que en tres corridas acumuló un defecto crítico y dos de alta severidad, todos de fecha o de alcance de filtro.

### Observaciones declaradas al cerrar el backfill (QA corrida 4, 0 casos en producción hoy)
Dos asimetrías que no cambian comportamiento hoy pero que conviene tener escritas, porque el día que aparezca un caso van a ser difíciles de encontrar:

1. **Navegación a entidad soft-deletable en el camino del backfill.** Las acreditaciones se traen con `IgnoreQueryFilters` (correcto: `Cheque` hereda `SoftDestroyable` y una navegación habría hecho un INNER JOIN filtrado que saca del backfill los pagos con cheque dado de baja), pero `p.OrdenCompra!.Estado` sigue siendo una navegación con filtro global, así que los pagos de una OC dada de baja **se caen en silencio**. Probablemente deban quedar afuera, pero es una decisión y el código tiene que declararla. Medido: 0 cheques dados de baja, 0 OC dadas de baja con pagos Pagado, 0 proveedores dados de baja — o sea que hoy `IgnoreQueryFilters` rescata 0 pagos y no hay que confiar en la corrida por ese motivo.
2. **`ActualizarFechaPagoTransferenciaAsync` no mantiene `FechaPagoTentativa`.** Corrige el documento y los dos ledgers, pero no ese campo, que es el que el backfill prefiere para un pago programado confirmado. Con 0 casos hoy, pero si aparece uno el backfill va a usar una fecha vieja. Corolario generalizable, que quedó en el catálogo con MH-038: un campo que *es* la fecha del hecho deja de serlo si otro camino de escritura no lo mantiene.

### Decisión pendiente del cliente antes de correr la regularización
**El pago 441** (Mercado Pago, $581.358,96, OC 80) es la excepción de MH-037: forma parte de los lotes cargados el 30/09 con fecha del día, y **Mercado Pago no tiene camino de corrección de fecha en la UI** (`ActualizarFechaPagoTransferenciaAsync` sólo cubre Transferencia). Su fecha del 30/09 quedaría congelada en los dos ledgers. Los otros 14 pagos del lote sí son corregibles después, y desde CR-84 la corrección cascadea a los dos ledgers, así que para ellos la advertencia en pantalla alcanza. Para el 441 hay tres caminos: corregirlo a mano antes de correr, aceptar la fecha explícitamente, o que CR-85 extienda la corrección de fecha a los demás métodos de pago.

### Regla cross-proyecto asociada
**MH-038**, propuesta por QA para `32-estandares-qa-implementador.instructions.md`: la fecha con la que un ledger asienta un hecho no siempre es la fecha del hecho. Chequeo barato antes de elegir el campo: `AVG(DATEDIFF)` de cada fecha candidata contra la que representa el hecho real, más el conteo de los registros que cruzan el fin de mes.


## CR-84 — La caja del local pasa a ser tesorería real: pagos a proveedores dentro, saldo agrupado y cuenta como atributo

**Estado:** Discovery CERRADO 2026-09-30. Las dos decisiones de fondo ya las tomó el cliente. Diseño, Arquitectura y Presupuesto pendientes.

### Las dos decisiones del cliente (2026-09-30)
1. **Los pagos a proveedores impactan en la cuenta corriente del local.** Decisión textual del cliente, pedida además como regla de desarrollo para todos los sistemas del estudio — quedó registrada como **MH-033** en `32-estandares-qa-implementador.instructions.md` y en `docs/qa/regresiones-manuales.yml`.
2. **Hay que crear las distintas cuentas.** El cliente preguntó si del extracto se podía concluir que todo el dinero termina en la cuenta bancaria principal, y planteó que si no, había que separar cuentas. La verificación con datos dice que **no consolida** (evidencia abajo), así que se crean. Regla derivada: **MH-034**.

### Por qué: el saldo actual no es un saldo de caja
`MovimientoCCLocal.OrigenTipo` sólo admite `"Venta"` y `"Gasto"`. Los `PagoOrdenCompra` van únicamente a `MovimientoCCProveedor`, así que las compras pagadas no bajan el saldo de la caja. Medido en producción al 30/09/2026:

| | |
|---|---|
| Saldo que muestra la CC Local | **$16.250.558,95** |
| Pagos a proveedores desde el ajuste de apertura del 10/08/2026, ausentes del ledger | **−$23.750.495,09** |
| Saldo real descontando las compras pagadas | **−$7.499.936,14** |

Desglose de esos pagos: cheque $10.578.712,98 · transferencia $9.797.494,07 · Mercado Pago $2.954.356,72 · efectivo $419.931,32 (74 pagos). El saldo da negativo porque en esas siete semanas el negocio compró más de lo que vendió y lo financió con aportes de los socios y con el capital de trabajo que el ajuste de apertura del 10/08 borró al llevar el saldo a $0.

El riesgo concreto que esto ya produjo: el cliente leyó los $16.250.558,95 como plata disponible y pidió cuadrarlos contra el extracto bancario, lo que habría significado postear un egreso de **$16.201.179,73** sin causa económica, destruyendo la información de la caja en efectivo, de Mercado Pago y de lo que Banco Carrefour todavía no liquidó.

### Por qué: el negocio NO consolida en una cuenta principal
Antes de modelar la dimensión cuenta se verificó con el extracto real si el negocio barre todo al Banco Provincia. **No lo hace**, con tres evidencias independientes:

1. **La cuenta estuvo 14 de 30 días en descubierto** en septiembre, con un mínimo de **−$148.518,32** y $182,65 de intereses cobrados. Una cuenta que concentrara los cobros de un negocio que mueve $23,7M no opera en descubierto la mitad del mes.
2. **Brecha de $4.196.000,06.** En septiembre se cobraron **$9.129.000,06** por canales que no son el Provincia (Mercado Pago $1.574.000 · tarjeta a 9 y 12 cuotas que liquida por MP $3.271.000 · Banco Carrefour $3.245.002,09 · transferencias de clientes $609.997,97 · débito $429.000) y sólo entraron **$4.933.000,00** de transferencias y depósitos.
3. **Saldo máximo del mes: $1.022.746,16.** La cuenta no acumula: se fondea justo para cubrir el cheque que vence y vuelve a cero.

Nota de honestidad sobre la lectura de las entradas: las 19 transferencias y depósitos que entran al Provincia figuran a nombre de Marcos Valentín Mari (CUIT 20331136132) y María Belén Cali (CUIT 27393358705). **Del extracto no se puede distinguir si son aportes de capital o barridos de la cuenta de Mercado Pago del titular** — una transferencia de MP a una cuenta bancaria propia aparece con el nombre del titular, no con el de Mercado Pago. En el análisis previo se las llamó "aportes de socios"; la lectura correcta es "entradas de fondos del titular, de origen no determinable desde el extracto". No cambia la conclusión (no alcanzan a cubrir lo cobrado por fuera), pero sí cambia lo que se puede afirmar. **A confirmar con el cliente**: es el dato que decide si la cuenta de Mercado Pago se fondea y se barre, o acumula.

### Mapa de cuentas (respuestas del cliente, 2026-09-30)
El cliente confirmó: **cada cuenta acumula su propio saldo y de ahí se pagan los gastos**; no hay barrido automático al banco. Y la cuenta de cada movimiento **se deriva de la forma de pago**, no de una regla fija por tipo de documento — lo confirmó explícitamente para las compras: las pagadas por Mercado Pago ($2.954.356,72 en el período) salen del saldo de MP, no del banco. La frase "las compras siempre salen de la cuenta bancaria" describe el caso mayoritario (cheque $10.578.712,98 + transferencia $9.797.494,07 = 86%), no una invariante.

| Cuenta | Qué entra | Qué sale |
|---|---|---|
| **Caja (efectivo)** | cobros en efectivo | gastos y compras en efectivo · depósitos al Provincia |
| **Mercado Pago** | cobros por MP · tarjeta de crédito procesada por MP (9 y 12 cuotas) | gastos y compras pagados por MP |
| **Banco Provincia** 5020-50461/8 | liquidaciones de Payway · transferencias de fondeo · depósitos de efectivo | cheques y transferencias a proveedores · débitos automáticos · impuestos y cargos bancarios · pago del resumen de la tarjeta propia |
| **Banco Carrefour** | liquidaciones de Banco Carrefour (confirmado: liquida a su propia cuenta) | a relevar |
| **Tarjeta de crédito VISA propia** | — | consumos cargados hoy como gasto con forma de pago "Débito automático" ($347.000 en septiembre); se cancela con el pago del resumen desde el Provincia ($255.501,70 en septiembre, hoy sin cargar) |

### La única pregunta abierta del mapa: dónde entran las transferencias de clientes
El cliente respondió "Banco Provincia", pero **el extracto lo desmiente**: las 4 transferencias de clientes de septiembre ($119.998,99 · $290.000,00 · $79.999,99 · $119.998,99, total $609.997,97) **no aparecen en ninguna de las 19 entradas del mes**. Y las 19 entradas son todas de importes redondos a nombre de Marcos Valentín Mari o María Belén Cali, mientras dos de esos cobros tienen centavos ($119.998,99, $79.999,99) — la firma de una venta con descuento, no de una transferencia armada a mano.

Hipótesis a confirmar con el cliente: **los clientes transfieren a una cuenta personal** (de Marcos o de María Belén) y desde ahí el dinero se pasa al Provincia en montos redondos consolidados. Eso explicaría de una vez las 19 entradas, el que ninguna coincida con un cobro individual, y el que la cuenta se fondee justo para cubrir el cheque que vence. Si es así, el catálogo necesita una **cuenta de tránsito personal** o la decisión explícita de no modelarla y registrar esos cobros directo en el Provincia, aceptando que no se van a poder conciliar contra su extracto.

Mientras no se resuelva, el saldo por cuenta del Banco Provincia va a quedar sobrestimado en el monto de las transferencias de clientes, y el de la cuenta de tránsito no va a existir.

### Alcance, después de la decisión del cliente (2026-09-30): saldo agrupado, sin cajas separadas
El cliente descartó partir la caja por cuenta, con este argumento textual: *"no sé si haría división por caja de tipo de cuenta porque después esa plata se mueve para algún lado sin contabilizarla en el sistema, prefiero que esté todo agrupado"*. **Es la decisión correcta y el argumento es más fuerte de lo que él lo planteó:** con un saldo agrupado los traspasos entre cuentas propias se anulan (sale de una, entra a la otra, neto cero), así que el hecho de que nadie los cargue deja de ser un problema. Partirlo en cajas con saldo propio haría que cada traspaso no registrado descuadre dos cajas a la vez. Esto refinó la regla cross-proyecto **MH-034**, escrita unas horas antes en la dirección opuesta.

Consecuencia sobre el alcance: se cae el punto de las cajas separadas y el de los movimientos de traspaso, y el CR queda considerablemente más chico.

1. `MovimientoCCLocal.OrigenTipo` gana **`"PagoOC"`**, y los pagos de orden de compra postean **en los dos ledgers en la misma transacción**: `Pago` en la CC del proveedor (baja la deuda) y `Egreso` en la caja (sale la plata). Es el núcleo del CR y la decisión de negocio ya tomada.
2. La **cuenta** queda como **atributo del movimiento para filtrar y conciliar**, nunca como caja con saldo propio. Para gastos y compras se deriva de la forma de pago, que ya existe; para las ventas con tarjeta, del procesador que agrega CR-83. El campo nuevo es chico o directamente innecesario: hay que evaluar si conviene persistirlo o derivarlo en la consulta.
3. **Saldo inicial por cuenta, cargado una vez.** Es el paso que convierte el número en tesorería real y no estaba en el alcance original. El ajuste de apertura del 10/08/2026 llevó el saldo a $0 y borró el capital de trabajo de ese día: con las compras y los gastos faltantes ya cargados el saldo agrupado daría **−$7.846.236,79**, negativo por el punto de partida y no por el negocio.
4. Conciliación **por flujo, no por saldo**: filtrando el período por una cuenta, comparar el flujo contra el extracto de esa cuenta. Con saldo agrupado el saldo no es comparable contra ningún extracto, y el reflejo de compararlo es el error a evitar.
5. Backfill de los datos históricos. **Punto delicado**: 655 de los 1.273 movimientos del ledger no tienen `PagoVentaId` (posteo único por el total de la venta, previo a CR-36), así que para esos la cuenta no se puede derivar. Con la decisión de saldo agrupado esto pierde gravedad: afecta el filtro por cuenta, no el saldo.

### Inventario de salidas de dinero — cerrado
Confirmado con el cliente que **los retiros para uso personal se cargan como gasto**. Con eso el inventario de salidas está completo y no queda ninguna categoría de egreso fuera del sistema: ventas (entrada), compras de mercadería, gastos operativos, retiros personales, costo de cobranza (CR-83) e impuestos y cargos bancarios. La única pieza faltante para que el saldo agrupado sea tesorería real es el saldo inicial del punto 3.

### Criterios de aceptación
Escritos el 2026-09-30 **después** de la implementación del punto 1, a pedido de QA, que marcó su ausencia como bloqueo de proceso en la primera corrida ("CR-84 no tiene criterios de aceptación escritos"). Tenía razón: el Discovery se cerró y se delegó la implementación sin pasar por acá, apurando el pedido del cliente de "implementar todo". Queda registrado como desvío del flujo, no como olvido silencioso.

**CA-84.1 — Un pago a proveedor postea en los dos ledgers, con la misma fecha y el mismo monto.**
Todo `PagoOrdenCompra` que represente una salida real de dinero genera, **en la misma transacción**, un `Pago` en `MovimientoCCProveedor` (baja la deuda) y un `Egreso` en `MovimientoCCLocal` (sale la plata), con `OrigenTipo="PagoOC"` y `OrigenId = pago.Id`. Los dos movimientos comparten fecha e importe, y el importe es **el del documento** (`pago.Monto`), nunca la suma de lo que haya en el ledger hermano — que puede tener más de un movimiento por razones históricas. La invariante vale en los cuatro caminos de fecha que existen: pago al contado, pago programado confirmado (fecha real de la acción, MH-021), cheque acreditado (fecha de vencimiento del cheque) y corrección posterior de fecha.

**Excepción acotada, declarada 2026-09-30:** en la regularización retroactiva (CA-84.8) el egreso de un **cheque histórico cuyo vencimiento difiere de la fecha de pago** queda con fecha distinta a la del movimiento de proveedor, porque el piso y la fecha del egreso salen los dos de `PagoOrdenCompra.Fecha`. Se privilegia la coherencia interna del backfill sobre espejar una fecha que en el origen es el vencimiento y no el hecho: con el vencimiento, el egreso quedaría fechado antes del piso que dice contenerlo. El camino en vivo no tiene esta excepción. **Detrás de esto hay un problema de fondo que NO es de este CR:** `ChequeService.AcreditarAsync` postea el movimiento de proveedor con `cheque.FechaVencimiento` bajo el supuesto de que ahí "realmente salió el dinero", y el pago 364 lo desmiente — venció el 05/08 y se acreditó el 22/08, así que el dinero salió doce días después de la fecha con la que quedó asentado. Afecta cualquier conciliación por fecha y la proyección financiera. QA lo midió y **amerita CR propio: es CR-85**, más arriba en este documento. Consecuencia para este criterio: con MH-038 corregido, el egreso de caja va a llevar la fecha **correcta** (`Cheque.FechaAcreditacion`) y el movimiento de proveedor va a seguir con una **aproximada** (el vencimiento), así que CA-84.1 **no es alcanzable en el backfill** mientras CR-85 no se implemente. No es defecto de CR-84: es el síntoma. El criterio se cumple íntegro en el camino en vivo.

**CA-84.2 — Un solo método de dominio escribe el egreso.**
Los tres puntos de alta (`PagoOrdenCompraService.RegistrarPagosAsync`, `ConfirmarPagoAsync`, `ChequeService.AcreditarAsync`) delegan en un único servicio (CRM-001). Ningún punto arma el movimiento por su cuenta.

**CA-84.3 — Recibir mercadería no mueve la caja.**
El `Cargo` que se postea al recibir una OC registra una deuda, no una salida de dinero: no genera ningún movimiento en la CC Local. Sólo los pagos lo hacen.

**CA-84.4 — Un pago que nunca salió no postea, y la reversión se acota a lo posteado.**
Un pago Pendiente (programado a futuro, o con cheque sin acreditar) no genera egreso. Al cancelar una OC o revertir un cheque acreditado (CR-82), el contramovimiento va por `Σ Egreso no-reversión − Σ Ingreso reversión` de los movimientos `PagoOC` de ese `OrigenId` (MH-020), nunca por el monto recalculado, y no se duplica si las dos acciones ocurren en cualquier orden.

**CA-84.5 — Un cheque rechazado no toca la caja.**
`ChequeService.RechazarAsync` no postea ni revierte nada: un cheque sólo se rechaza desde Pendiente y un cheque Pendiente nunca posteó el pago real (CR-46).

**CA-84.6 — Corregir la fecha de un pago corrige los dos ledgers.**
La corrección de la fecha real de un pago actualiza el movimiento de CC Proveedor **y** el egreso de caja en la misma operación. El mismo hecho no puede quedar imputado a dos meses distintos según el ledger que se mire.

**CA-84.7 — Un pago de un documento cancelado no aparece en la CC Local.**
La exclusión de documentos cancelados del listado de CC Local cubre `PagoOC` igual que `Venta` y `CostoCobranza`. Cancelar una OC no puede ocultar el movimiento de un lado y dejarlo visible del otro. Ojo con la diferencia estructural: en `PagoOC` el `OrigenId` es el id del **pago**, no del documento, a diferencia de `"Venta"`.

**CA-84.8 — La regularización es idempotente, acotada, y aplica exactamente lo que muestra.**
La carga retroactiva de los egresos históricos (a) se acota al período **posterior al ajuste de apertura**, cuyo Egreso ya contiene el neto de todo lo anterior — derivando el piso del propio movimiento `AjusteApertura`, no de una fecha hardcodeada, y aplicándolo sobre **`PagoOrdenCompra.Fecha`, la fecha del documento, nunca la del movimiento del ledger hermano**. Motivo, medido en producción: el movimiento de un pago con cheque lleva la fecha de **vencimiento** del cheque, que puede ser anterior al ajuste aunque el cheque se haya acreditado después (caso real: pago 364, cheque #30, $495.200,00, movimiento fechado 05/08 y acreditación el 22/08). Con el piso sobre el movimiento el backfill da 73 pagos / $23.255.295,09 y no reproduce el rubro cheque; sobre la fecha del documento da los 74 / $23.750.495,09 correctos. Por la misma razón, el egreso de esos pagos se postea con la **fecha de pago** y no con la del movimiento, para que no quede fechado antes del piso que dice contenerlo; (b) es idempotente por saldo neto y no por un flag; y (c) usa **la misma consulta** en la previsualización y en la confirmación, para que el número que se muestra sea el que se aplica por construcción. Objetivo de contraste al 30/09/2026: **74 pagos y $23.750.495,09 del período reconstruido**, que no es el monto a postear — de ahí salen 69 pagos por $21.525.795,09 incorporados más 5 por $2.224.700,00 excluidos por tener el ledger hermano sucio. Por eso el panel "por método" muestra el rubro cheque en $8.354.012,98 y no en $10.578.712,98: los 5 excluidos son todos cheques, y las dos cifras son correctas ($8.354.012,98 + $2.224.700,00 = $10.578.712,98). La identidad que la pantalla debe imprimir y que tiene que cerrar en cualquier momento, incluso tras una corrida parcial, es **ya posteado + pendiente + excluido = total del período**. Saldo resultante esperado −$7.499.936,14.

**CA-84.9 — La previsualización advierte los lotes con fecha dudosa.**
Antes de confirmar, la pantalla lista los pagos cargados en lote con fecha igual al día de carga (varios con el mismo `CreatedAt` al microsegundo), con su monto, porque la regularización congela esa fecha en los dos ledgers y después corregirla es más caro. Caso que originó el criterio (cifras corregidas por QA en la corrida 2; la primera versión de este criterio decía "14 transferencias por $6.382.868,96", que salía de agrupar por día y método en vez de por sesión de carga): **13 pagos por $6.382.868,84** con `CreatedAt = 2026-09-30 15:02:43.059807` y **2 pagos por $581.359,08** con `CreatedAt = 2026-09-30 15:27:28.346518`, sobre órdenes de compra viejas. El agrupamiento correcto es por sesión de carga (mismo `CreatedAt` al microsegundo), no por día. El sistema no puede inferir la fecha real: es un dato de negocio, así que advierte y no bloquea.

**CA-84.10 — El rótulo del saldo dice lo que el saldo mide.**
Mientras el saldo inicial no esté cargado (punto 3 del alcance), ninguna pantalla llama "Saldo actual" ni "disponible" a un número que no es la plata que hay. Es el corolario de MH-033: la ambigüedad se resuelve en el rótulo, no en la cabeza del usuario. Se levanta cuando se cargue el saldo inicial.


### Dependencias y riesgos
- **Depende de CR-83**, que aporta el procesador por línea de pago: la cuenta donde cae una venta con tarjeta se deriva de ahí (Payway → Banco Provincia, Mercado Pago → cuenta de MP). Sin eso la cuenta de destino de la mitad de los ingresos es indeterminable.
- El backfill es el punto delicado: **655 de los 1.273 movimientos históricos del ledger no tienen `PagoVentaId`** (posteo único por el total de la venta, previo a CR-36), así que para esos no hay forma de derivar la cuenta. Hay que decidir si se les asigna una cuenta "sin determinar" o se los deja fuera del saldo por cuenta.
- Es el CR más grande de la etapa 2 y toca el ledger de caja, que es el núcleo financiero del sistema. No conviene meterlo en el mismo sprint que CR-83.

### Fuera de alcance (propuesto)
- Importación automática de extractos bancarios.
- Conciliación automática; este CR habilita la conciliación manual por cuenta, que hoy es imposible.

## CR-83 — Comisiones de plataformas de pago e impuestos bancarios calculados por venta

**Estado:** Discovery + Análisis CERRADOS 2026-09-30 (las 3 decisiones de negocio resueltas por el cliente, ver abajo). Diseño y Arquitectura cerrados. Presupuesto pendiente de aprobación del cliente antes de Implementación.

### Pedido del cliente (2026-09-30)
Que el sistema calcule, por cada venta, la comisión de la plataforma de pago y los impuestos bancarios que esa cobranza genera, con las tasas reales en vez de un gasto redondo cargado a mano. Recalcular septiembre 2026 con los valores calculados e insertar el ajuste retroactivo si es viable. El objetivo declarado es automatizarlo de ahí en adelante: "la idea es automatizar esto por cada venta que se hace".

### Origen: la conciliación del extracto del Banco Provincia de septiembre 2026
El pedido sale del cruce del extracto `docs/consultaMovimientos.xls` (cuenta 5020-50461/8, 183 movimientos del 01/09 al 30/09) contra la base de producción. Lo que mostró ese cruce:

- El costo de cobranza **no está en el sistema con importes reales**. Hay 14 gastos de categoría `ComisionesBancarias` en septiembre por **$1.561.000** cargados a mano en montos redondos ($3.000, $138.000, $112.000, $25.000, $85.000, $18.000, $40.000, $100.000 con subcategoría "gastos payway pcia" = $521.000; y $380.000, $333.000, $17.000, $50.000, $260.000 con "gastos y comisiones mp" = $1.040.000).
- Los **impuestos bancarios reales** del mes no están cargados en ninguna forma: retención ARBA $124.028,60 · Ley 25413 débitos $43.756,50 · Ley 25413 créditos $41.342,99 · contracargos VISA $24.326,84 · intereses $182,65 · clearing $101,00 · sellos $4,24. Menos la compensación de saldos a favor ($11.498,14), **$222.244,68 netos**.
- La **comisión de la plataforma no es observable en el extracto**: el banco acredita "PAGOS A COMERCIOS VISA/MASTERCARD" ya neto de comisión, IVA y retenciones, sin desglosar. Los $2.553.499,76 acreditados en septiembre son netos. Por eso la comisión hay que *calcularla* con las tasas, que es exactamente lo que pide este CR — no se puede extraer del extracto.
- La rentabilidad del sistema (`IRentabilidadService`, CR-80) es Ventas − Costo de mercadería. **No descuenta el costo de cobranza**, así que una venta en 12 cuotas por Mercado Pago muestra hoy el mismo margen que una en efectivo, cuando la diferencia real es del 23,58%.

### Tasas de referencia disponibles
De la memoria del proyecto (`project-costos-mercadopago`, tasas especiales negociadas por el cliente, vigentes al 30/09/2026):

| Medio | Mercado Pago | Payway |
|---|---|---|
| Crédito 1 pago | 4,08% (acred. 21 días) | 2,0% presencial/QR · 3,0% e-commerce |
| Crédito 2 cuotas | 8,48% | 2,0% + costo financiero |
| Crédito 3 cuotas | 10,28% | 2,0% + costo financiero |
| Crédito 6 cuotas | 14,38% | 2,0% + costo financiero |
| Crédito 9 cuotas | 19,38% | 2,0% + costo financiero |
| Crédito 12 cuotas | 23,58% | 2,0% + costo financiero |
| Crédito 18 cuotas | 30,18% | 2,0% + costo financiero |
| Débito | 2,88% (2 días) | 1,2–1,4% |
| Prepaga | 3,68% (3 días) | — |
| Pix / transferencia | 3,40% al instante | 0,8% |

Del extracto, los impuestos bancarios sobre cada acreditación, verificados línea por línea (ej. 30/09: transferencia de $130.000 genera ARBA $2.340 + Ley 25413 $780):
- **Retención ARBA (IIBB): 1,8%** sobre el crédito.
- **Impuesto Ley 25413: 0,6%** sobre el crédito (y otro 0,6% sobre cada débito).

Nota de la memoria, a respetar: las tasas de MP "cambian seguido" y "el arancel sube si se acorta el plazo de acreditación; los cargos varían por provincia". Implica que los porcentajes van a base de datos configurable, nunca hardcodeados — mismo criterio que ya fijó CR-40 con `ConfiguracionCuotaTarjeta`.

### Hallazgo bloqueante: el sistema no sabe por qué plataforma se cobró
`PagoVenta.Metodo` distingue el *medio* (TarjetaCredito, TarjetaDebito, MercadoPago, Transferencia, Efectivo, BancoCarrefour) pero **no el procesador**. Un pago con TarjetaCredito puede haber pasado por el Point de Mercado Pago o por la terminal Payway del Banco Provincia, y la tasa difiere en un factor de 8,7x. Calculado sobre los $5.210.600 de tarjeta de crédito de septiembre (11 pagos: 1 cuota $33.000 · 3 cuotas $614.000 · 6 cuotas $2.150.600 · 9 cuotas $900.000 · 12 cuotas $1.513.000):

| Escenario | Comisión calculada |
|---|---|
| Todo por Mercado Pago | **$904.907,28** |
| Todo por Payway | **$104.212,00** (más el costo financiero de cuotas, coeficiente no público) |

Hay evidencia de que en la práctica se usan **las dos**: los $1.040.000 que el cliente cargó a mano como "comisiones mp" se parecen mucho a los $904.907 que da el cálculo de MP para toda la tarjeta de crédito, pero al mismo tiempo el extracto del Provincia muestra 9 liquidaciones "PAGOS A COMERCIOS VISA/MASTERCARD" por $2.553.499,76, que sólo existen si hay volumen real por Payway. Sin el dato del procesador por pago, cualquier cálculo automático es una adivinanza con un error potencial de $800.000 en un mes.

### Alcance inicial propuesto (a confirmar en Análisis)
1. Catálogo configurable de tasas por procesador/medio/cuotas (pantalla admin, mismo patrón que `ConfiguracionCuotaTarjeta` de CR-40), con vigencia por fecha para no reescribir el pasado cuando MP cambie los aranceles.
2. Dato de procesador en la línea de pago de la venta, para poder aplicar la tasa correcta.
3. Cálculo del costo de cobranza por línea de pago: comisión de plataforma + IVA sobre comisión + impuestos bancarios sobre la acreditación.
4. Registro del costo calculado, con impacto contable a definir (ver pregunta 2).
5. Recálculo retroactivo de septiembre 2026 y carga del ajuste.
6. Costo de cobranza descontado en la rentabilidad (`IRentabilidadService`), para que el margen por venta sea el real.

### Supuestos
- Las tasas de la memoria son las vigentes y las confirma el cliente antes de sembrarlas.
- El IVA sobre la comisión (21%) es computable como crédito fiscal, así que el costo de caja es la comisión con IVA pero el costo de resultado es la comisión sin IVA. A confirmar con el contador en Análisis.
- La retención de IIBB de ARBA es a cuenta del impuesto anual, no un costo definitivo. A confirmar: si se computa, el costo real es menor que el flujo de caja.

### Dependencias
- Tasa de **BancoCarrefour**: **RESUELTA 2026-09-30, es 0%** (respuesta textual del cliente: "el arancel del bco carrefour es 0"). No es un pendiente ni un valor provisorio: ese medio no tiene costo de cobranza, y el 0,00 que ya tenía el seed queda confirmado. Los impuestos bancarios también quedan en 0 porque liquida a su propia cuenta en Banco Carrefour y no se tiene ese extracto para verificar si le retienen ARBA/Ley 25413 sobre la acreditación. Con $3.245.002,09 cobrados en septiembre, es el segundo volumen del mes y no aporta costo.
- Para conciliar la comisión calculada contra la real hace falta la **liquidación de Payway** (el extracto no la desglosa). Es la única forma de calibrar si las tasas configuradas son las que efectivamente cobran.

### Fuera de alcance (propuesto)
- Importar automáticamente el extracto bancario o las liquidaciones de las plataformas. Este CR calcula el costo con tasas configuradas; no lee archivos del banco.
- Conciliación automática venta ↔ acreditación (requiere número de lote/cupón, que el extracto no trae).
- Retenciones de IVA y Ganancias que practica la plataforma sobre la liquidación: no son costo, son pagos a cuenta. Se mencionan para no confundirlas con la comisión.

### Decisiones del cliente (2026-09-30, cierran el Discovery)
1. **Procesador: siempre lo elige el vendedor.** Campo obligatorio en cada línea de pago cuyo medio tenga costo de cobranza. Se descartó la regla fija por medio: el cliente confirmó que las dos terminales (Point de Mercado Pago y Payway del Banco Provincia) se usan en paralelo, así que ninguna regla automática acierta.
2. **El egreso se postea al acreditarse el pago**, con la misma fecha que el ingreso — que es cuando la plataforma efectivamente descuenta la comisión. Para los medios que nacen `Acreditado` (Efectivo, Transferencia, MercadoPago, TarjetaDebito, BancoCarrefour) eso ocurre al confirmar la venta; para `TarjetaCredito`, en `AcreditarPagoAsync`. Los dos caminos usan el mismo método de dominio (CRM-001).
3. **Retroactivo de septiembre 2026: calcular e insertar.** Anular los 14 gastos manuales de $1.561.000 y cargar el costo calculado más los $222.244,68 de impuestos bancarios reales del extracto.

El arancel de BancoCarrefour deja de ser bloqueante por la decisión 1: es un procesador más del catálogo y su tasa se configura en pantalla. Arranca en 0% hasta que el cliente cargue el valor real, y mientras esté en 0 el medio no genera costo (no se inventa un número).

### Criterios de aceptación

**CA-83.1 — Catálogo de tasas configurable, con vigencia por fecha.**
El Administrador configura, en Configuración, una tasa por combinación de procesador + medio de pago + cantidad de cuotas, con su % de comisión, su % de IVA sobre la comisión, su % de retención de IIBB y su % de impuesto Ley 25413. Cada fila tiene `VigenteDesde` y `VigenteHasta`: cargar una tasa nueva no reescribe el costo ya calculado de las ventas viejas. Ningún porcentaje queda hardcodeado en el código (la memoria del proyecto advierte que las tasas de MP "cambian seguido").

**CA-83.2 — El vendedor elige el procesador en la línea de pago.**
Al registrar un pago cuyo medio tiene costo (TarjetaCredito, TarjetaDebito, MercadoPago, BancoCarrefour, Transferencia), el selector de procesador es obligatorio y no tiene valor por defecto que se pueda confirmar sin mirar. Con Efectivo el selector no se muestra y el procesador queda en `Ninguno`. Si para la combinación elegida no hay tasa vigente, la pantalla lo dice antes de guardar y el pago se registra con costo 0 (nunca se bloquea la venta por una tasa sin cargar — CRM-020: una función opcional no rompe el flujo que la hospeda).

**CA-83.3 — El costo se calcula sobre el monto realmente cobrado.**
Base de cálculo: `PagoVenta.Monto` (el dinero que la plataforma liquida, con recargo de tarjeta incluido), nunca `MontoBase`. Desglose persistido por pago: comisión, IVA sobre la comisión, impuestos bancarios y total. Se guarda también el id de la tasa aplicada, para poder auditar después con qué porcentaje se calculó.

**CA-83.4 — El egreso se postea junto con el ingreso, con la misma fecha.**
Cuando un pago pasa a Acreditado se postea un `MovimientoCCLocal` de Egreso por el costo total, con `OrigenTipo="CostoCobranza"`, `PagoVentaId` de ese pago y la misma `Fecha` del Ingreso que lo acompaña. Un pago Pendiente (tarjeta de crédito sin acreditar) no postea ningún egreso: el costo todavía no ocurrió. Mismo criterio de MH-021 sobre la fecha real de la acción.

**CA-83.5 — Reversión acotada a lo posteado.**
Al cancelar una venta o eliminar un pago, el egreso de costo de cobranza se revierte con un contramovimiento (`EsReversion=true`) por lo efectivamente posteado para ese pago, nunca por el costo recalculado ni por el total de la venta (PAT-020 / MH-020). Un pago que nunca se acreditó no genera contramovimiento porque nunca posteó egreso.

**CA-83.6 — La rentabilidad descuenta el costo de cobranza.**
`IRentabilidadService` informa el costo de cobranza del período y un margen neto (Ventas − Costo de mercadería − Costo de cobranza) además del margen bruto actual. Una venta en 12 cuotas por Mercado Pago deja de mostrar el mismo margen que una en efectivo. El KPI del Dashboard sigue saliendo de este único servicio, sin recalcular nada propio (criterio ya fijado en CR-80).

**CA-83.7 — Asignación del procesador a los pagos históricos.**
En el listado de Ingresos, el Administrador puede asignar el procesador de un pago ya registrado con edición inline (mismo patrón AJAX de CR-69), y ver el costo calculado de cada línea. Es la vía para los pagos anteriores a este CR, que nacieron sin procesador.

**CA-83.8 — Recálculo retroactivo por período.**
Una acción de administración recalcula el costo de cobranza de un rango de fechas y postea los egresos faltantes de los pagos ya acreditados que tengan procesador asignado, de forma idempotente: correrla dos veces no duplica movimientos (se verifica contra los egresos ya existentes de ese `PagoVentaId`, mismo criterio de saldo neto que usa `ChequeService.RevertirEstadoAsync`). Los pagos sin procesador quedan listados como pendientes de asignar, no se les inventa uno.

**CA-83.9 — Los impuestos bancarios del extracto que no nacen de una venta se cargan como gasto.**
El impuesto Ley 25413 sobre los débitos, los contracargos, los intereses por descubierto, la comisión de clearing y los sellos no son atribuibles a una venta: se siguen cargando como Gasto. Este CR no los automatiza. Lo que sí queda automatizado es la parte que cada cobranza genera: comisión, IVA y los impuestos sobre la acreditación.

### Alcance excluido (confirmado)
- Importar el extracto bancario o las liquidaciones de las plataformas. El costo se calcula con tasas configuradas.
- Conciliación automática venta ↔ acreditación por número de lote/cupón.
- Tratar las retenciones de IVA y Ganancias de la plataforma como costo: son pagos a cuenta.
- Prorratear el costo entre las líneas de producto de la venta. El costo es de la línea de pago, no del producto.

### Riesgo declarado
El cálculo es tan bueno como las tasas configuradas, y no hay forma de validarlo contra la realidad sin la liquidación de Payway (el extracto acredita neto, sin desglose). Mitigación propuesta: la pantalla de conciliación compara, por período, el costo calculado contra los gastos de comisión realmente cargados, para que la desviación sea visible. La calibración fina queda pendiente de que el cliente consiga una liquidación de Payway.

## CR-78 — La pantalla de Venta bloqueaba cancelar una venta cuya factura ya estaba anulada por Nota de Crédito

Detectado en producción el 23/09/2026, probando CR-77 sobre la Venta #724: el servidor permitía cancelarla (su única factura estaba anulada por la NC #337) pero la pantalla mostraba "Esta venta tiene un comprobante AFIP emitido y no se puede cancelar" y ni siquiera ofrecía el botón.

**Causa**: `Ventas/Details.cshtml` tenía **su propia copia del criterio**, distinta de la del servicio: miraba `ComprobanteAfipEstado`, que es el estado del **último** comprobante de la venta — y después de emitir una NC, el último comprobante es la NC misma (Emitida). El guard real de `VentaService.CancelarAsync` (`TieneComprobanteAsociadoAsync`) sí está bien: exige Factura A/B Emitida **y** que no tenga una NC Emitida asociada (CR-55/MH-013). Es exactamente el patrón que REG-004 previene: un botón derivado de una copia del criterio en la vista, que se desincroniza del servicio.

**Fix**: `VentaDetailDto.TieneFacturaVigente`, poblado en `GetByIdAsync` llamando al mismo `TieneComprobanteAsociadoAsync` que usa el guard — una sola fuente de verdad. La vista pasa a usar ese flag. El mensaje además ahora explica la salida: si la factura se anula con una NC, la venta vuelve a poder cancelarse.

**Impacto en capas**: Application (`VentaDtos.cs`), Infrastructure (`VentaService.cs`), Web (`Ventas/Details.cshtml`). Sin migración EF.

## CR-76 — Quitar el filtro "Vendedor" del listado de Ventas

Pedido explícito del cliente (03/09/2026): "en el listado de Ventas quitar filtro Vendedor".

**Alcance**: se retira el filtro **completo**, no solo el control visible — combo, wiring de JS, `VentaIndexViewModel.Vendedores`, la carga del combo en el controller, el parseo del form, `VentaFiltro.VendedorId` y el `Where` de `VentaService.ListarAsync`. Motivo de retirarlo end-to-end: los filtros de esta pantalla se persisten en sesión, así que dejar la propiedad en `VentaFiltro` haría que una sesión con un `VendedorId` ya guardado siguiera filtrando en silencio, sin ningún control visible que lo muestre ni que lo limpie. Se retira también `IVentaService.ListarVendedoresParaComboAsync` (y su implementación), que quedaba sin ningún consumidor — Presupuestos y Entregas tienen su propia copia en sus respectivos services, así que no se ven afectados. Efecto colateral positivo: una consulta menos por cada carga del listado.

**La columna "Vendedor" de la grilla se mantiene** (el pedido es sobre el filtro). **Desvío consciente de PAT-008** ("todo listado tiene un filtro funcional por cada columna visible"), a pedido explícito del cliente y anotado acá para que un QA futuro no lo reporte como bug: si más adelante se prefiere alinear con la regla, la alternativa es quitar también la columna.

**Impacto en capas**: Application (`VentaDtos.cs`, `IVentaService.cs`), Infrastructure (`VentaService.cs`), Web (`VentasController.cs`, `VentaViewModels.cs`, `Ventas/Index.cshtml`). Sin migración EF.

## CR-75 — Control de ventas con pagos todavía no acreditados

Pedido explícito del cliente (03/09/2026), sobre un caso concreto en producción (Venta #699, https://marihogar.com.ar/Ventas/Details/699): "en el detalle de esta venta, en la parte del resumen, figura la venta como pagada, con saldo pendiente 0, pero el pago de la venta todavía no está acreditado, el usuario quiere tener control de las ventas que todavía no están acreditadas".

**Diagnóstico (no es un bug, es falta de visibilidad)**: `Venta.Estado` y `SaldoPendiente` miden **la deuda del cliente**, no la disponibilidad del dinero — apenas los pagos cubren el total, la venta pasa a Pagada con saldo $0, sin importar el `EstadoAcreditacion` de esos pagos. Eso es correcto y no se toca (el cliente efectivamente ya pagó; la acreditación es un tema bancario que se sigue aparte en Ingresos y en Cuenta corriente del local, y `Estado = Pagada` es además lo que habilita remito y facturación AFIP). El problema real es que el Resumen se lee como "esta plata ya entró" cuando todavía no entró. Verificado contra producción: la Venta #699 tiene un único pago con Tarjeta de crédito en 12 cuotas por $948.000 en estado Pendiente hasta el 25/09/2026; hoy hay 3 ventas no canceladas en esa situación.

**Alcance confirmado con el cliente (1 pregunta resuelta antes de implementar)**: visibilidad en el detalle **+ filtro en el listado**, sin cambiar el Estado ni el Saldo pendiente. Se descartó explícitamente la alternativa de que la venta no figure Pagada hasta acreditar: hoy `Estado = Pagada` habilita remito y facturación AFIP y lo usan varios reportes — con ese cambio una venta cobrada con tarjeta quedaría sin poder facturarse hasta que el banco acredite.

**Diseño**:
- `Ventas/Details`, card Resumen: nueva línea **"Sin acreditar: $X"** (solo cuando hay pagos pendientes), debajo de Pagado / Saldo pendiente. No modifica ninguno de los dos valores existentes.
- `Ventas/Index`: checkbox **"Solo ventas con pagos pendientes de acreditación"** (persistido en sesión con el resto de los filtros) + badge **"Sin acreditar"** junto al badge de Estado en las filas afectadas, para que se distingan también sin filtrar.

**Arquitectura**:
- `VentaDetailDto.MontoPendienteAcreditacion` (calculado sobre `Pagos`, sin consulta nueva), `VentaListItemDto.TienePagosPendientesAcreditacion`, `VentaFiltro.SoloPendientesAcreditacion`.
- `VentaService.ListarAsync`: filtro nuevo con la misma forma que el de forma de pago (`v.Pagos.Any(...)`, subquery correlacionada). El indicador por fila se resuelve **dentro de la consulta de pagos por fila que ya existía** para `FormasPago` (se le agrega `EstadoAcreditacion` al `Select`) — sin consultas nuevas y sin `Include` de colección sobre la query paginada (riesgo DN-001/DN-002), respetando el patrón ya establecido en el método.

**Impacto en capas**: Application (`VentaDtos.cs`), Infrastructure (`VentaService.cs`), Web (`VentasController.cs`, `Ventas/Index.cshtml`, `Ventas/Details.cshtml`). Sin migración EF.

## CR-74 — Tarjeta de crédito: agregar la opción "1 pago"

Pedido explícito del cliente (03/09/2026): "agregar formas de pago con tarjeta de crédito falta la opción 1 pago".

**Diseño**: la cantidad de cuotas de Tarjeta de crédito estaba acotada a 3/6/9/12 (CR-40) y no contemplaba la venta en un solo pago, que es un caso real y frecuente. Se agrega `1` al conjunto válido, mostrado como **"1 pago"** (no "1 cuotas") en todas las pantallas donde aparece. El circuito no cambia en nada más: un pago en 1 cuota con tarjeta sigue siendo un pago de acreditación diferida (el banco liquida igual), con su fecha efectiva y su estado Pendiente/Acreditado como cualquier otro.

**Arquitectura**: `1` se suma a los 2 conjuntos de validación server-side (`VentaService.CuotasValidasTarjeta` y `PagoVentaService.CuotasValidasTarjeta`) y a las 2 listas client-side (`Ventas/Create.cshtml`, `Ventas/Details.cshtml`), más la semilla de `ConfiguracionCuotaTarjeta` en `SeedData` — que pasa de 4 a 5 filas fijas (1/3/6/9/12), así el Administrador puede configurar el % de interés de "1 pago" desde Configuración > Cuotas de tarjeta igual que el resto. La semilla es idempotente y corre al iniciar la app: la fila nueva se crea sola al deployar, en 0%, sin migración ni script de datos. Etiqueta "1 pago" aplicada en los 2 selectores de cuotas, en el detalle de la venta, en la pantalla Ingresos y en la pantalla de configuración.

**Impacto en capas**: Domain (comentarios), Application (comentarios de DTOs), Infrastructure (`VentaService.cs`, `PagoVentaService.cs`, `SeedData.cs`), Web (`Ventas/Create.cshtml`, `Ventas/Details.cshtml`, `PagosTarjeta/Index.cshtml`, `ConfiguracionCuotas/Index.cshtml`). **Sin migración EF** (la fila nueva la siembra `SeedData`).

## CR-73 — "Pagos con tarjeta" pasa a llamarse "Ingresos"

Pedido explícito del cliente (03/09/2026), como cierre de la decisión que CR-71 había dejado abierta ("queda anotado como decisión abierta para el cliente si más adelante prefiere un label genérico"): "La pantalla Pagos con tarjeta ahora debe llamarse Ingresos".

**Alcance confirmado con el cliente**: solo el label visible (menú, título de la pantalla) — la URL (`/PagosTarjeta`), el controller, el servicio (`IVentaService.ListarPagosTarjetaAsync`) y los DTOs (`PagoTarjetaFiltro`, `PagoTarjetaListItemDto`) no se renombran, para no tocar más archivos de los necesarios sin beneficio funcional.

**Cambio**: `_Layout.cshtml` (label del menú "Pagos con tarjeta" → "Ingresos", ícono `fa-credit-card` → `fa-money-bill-trend-up` — decisión propia, un ícono de tarjeta ya no representaba bien una pantalla que desde CR-71 lista todos los métodos de pago) y `PagosTarjeta/Index.cshtml` (`ViewData["Title"]` y `<h3>` → "Ingresos"). El KPI del Dashboard "Pagos con tarjeta por acreditar" **no se tocó**: es una métrica más específica (solo tarjeta de crédito pendiente de acreditar), no el nombre de la pantalla.

**Impacto en capas**: Web únicamente (2 archivos `.cshtml`). Sin cambios en Application/Infrastructure/Domain, sin migración EF.

## CR-72 — Renombres en Gastos/Gasto recurrente + reorden visual de Gastos/Create

Pedido explícito del cliente (03/09/2026): en `Gastos/Index` el botón "Gestionar plantillas de gasto recurrente" debe decir solo "Nuevo gasto recurrente"; en `Gastos/Create` el selector "Cargar desde plantilla" debe decir "Seleccionar gasto recurrente"; y mejorar el orden visual de `Gastos/Create` ("se ve desprolijo/desordenado").

**Alcance confirmado con el cliente (3 preguntas resueltas antes de implementar)**: (1) el botón renombrado en `Gastos/Index` **solo cambia el texto**, sigue llevando al listado CRUD completo de plantillas (`GastosRecurrentesController.Index`) — no pasa a ir directo a un alta; (2) la mejora pedida es sobre `Gastos/Create`, no sobre las pantallas de `GastosRecurrentes`; (3) el problema puntual es que "el formulario en general se ve desprolijo/desordenado" — no un control específico.

**Diseño**: cambio puramente de presentación, sin tocar controllers, services ni DTOs.
- `Gastos/Index.cshtml`: el link a `GastosRecurrentesController.Index` cambia su texto de "Gestionar plantillas de gasto recurrente" a "Nuevo gasto recurrente" — mismo destino, mismo ícono.
- `Gastos/Create.cshtml`: reestructurado de un único `<div class="card">` con todos los campos apilados en una sola columna, a 3 bloques separados dentro del mismo `<form>` (sin cambiar ids ni el JS que ya manejaba `#listaPagos`/`#totalPagos`/`#pagosJson`/`#btnAgregarPago`, que sigue funcionando sin modificaciones):
  1. Card "Seleccionar gasto recurrente" (antes "Cargar desde plantilla") — solo visible si hay plantillas, igual que antes.
  2. Card "Datos del gasto" — Categoría y Fecha ahora en la misma fila (2 columnas), Subcategoría y Descripción debajo a ancho completo.
  3. Card "Formas de pago" — el botón "Agregar forma de pago" pasa al `card-header` (antes compartía fila con el label "Formas de pago" dentro del body); se agrega una fila de encabezados de columna ("Forma de pago" / "Monto") sobre la lista de líneas, ausente hasta ahora.
- El ancho de la columna del formulario pasa de `col-lg-6` a `col-lg-8` para acomodar la fila de 2 columnas de Categoría/Fecha sin apretar los controles.

**Impacto en capas**: Web únicamente (`Views/Gastos/Index.cshtml`, `Views/Gastos/Create.cshtml`). Sin cambios en Application/Infrastructure/Domain, sin migración EF.

## CR-71 — "Pagos con tarjeta" pasa a listar todos los pagos de ventas, filtrables por forma de pago

Pedido explícito del cliente (03/09/2026): "la pantalla Pagos con tarjeta ahora debe mostrar un listado con todos los pagos del sistema, con la posibilidad de filtrarlos por tipo de pago, y de mostrar solo pendientes".

**Alcance confirmado con el cliente (2 preguntas resueltas antes de implementar)**: (1) es **solo pagos de Ventas** — los pagos a proveedores / Órdenes de compra quedan explícitamente fuera (arquitectura distinta, `EstadoPagoOrdenCompra` propio, se evaluará como CR aparte); (2) el combo de forma de pago lista **todos** los métodos usados en Ventas, incluidos Efectivo y Tarjeta de débito: como esos nacen `EstadoAcreditacion = Acreditado`, combinarlos con "solo pendientes" devuelve 0 filas, que es el resultado correcto y no un caso a excluir del combo.

**Diseño**: la pantalla de CR-59 (`PagosTarjeta/Index`, Administrador-only) deja de estar acotada a Tarjeta de crédito. Se agrega un filtro "Forma de pago" (mismas opciones y mismas etiquetas legibles que el combo ya existente en `Ventas/Index`) y una columna "Forma de pago" en la grilla, respetando la regla de que todo dato visible en el listado tiene su filtro. El requisito "mostrar solo pendientes" ya lo cubre el filtro de Estado existente (Pendiente / Acreditado / Todos) — no se agregó un control nuevo. La acción "Acreditar" no cambia: sigue apareciendo solo en filas Pendiente y `AcreditarPagoAsync` conserva su guard de estado, así que en la práctica solo se ofrece sobre Tarjeta de crédito / Banco Carrefour.

**Decisión de nomenclatura**: no se renombró nada — controller, ruta, `ListarPagosTarjetaAsync` y el ítem de menú "Pagos con tarjeta" siguen igual. El cliente pidió ampliar la pantalla que ya usa, no crear una nueva; renombrar la ruta/menú rompería la referencia que el cliente tiene de ella. Solo se actualizó el texto descriptivo bajo el título y la etiqueta del filtro de Estado ("Estado de acreditación"). Queda anotado como decisión abierta para el cliente si más adelante prefiere un label genérico ("Pagos" / "Conciliación de pagos").

**Arquitectura**:
- `PagoTarjetaFiltro` gana `MetodoPago? Metodo` (nulo = todos los métodos); se persiste en sesión con el resto de los filtros, sin cambios de mecanismo.
- `PagoTarjetaListItemDto` gana `Metodo` (nombre del enum, traducido a etiqueta legible en el cliente).
- `VentaService.ListarPagosTarjetaAsync`: se retira el `Where(p => p.Metodo == MetodoPago.TarjetaCredito)` fijo de CR-59 y pasa a ser un filtro opcional. Se agrega ordenamiento por `metodo` (columna nueva, mismo patrón que el resto).
- Orden por defecto **sin cambios** (`FechaAcreditacionEfectiva` desc): como solo Tarjeta de crédito tiene fecha de acreditación, los pagos de los demás métodos (que la tienen nula) quedan al final en la vista sin filtros. Se preserva a propósito el comportamiento de CR-59 — con el filtro Estado=Pendiente, que es el uso principal, todas las filas tienen fecha y el orden es el correcto.

**Impacto en capas**: Application (`PagoTarjetaDtos.cs`, `IVentaService.cs`), Infrastructure (`VentaService.cs`), Web (`PagosTarjetaController.cs`, `PagosTarjeta/Index.cshtml`). **Sin migración EF** — no se toca ninguna entidad ni columna.

## CR-70 — Gasto con varias líneas de pago (ej. sueldo pagado mitad efectivo, mitad transferencia)

Pedido explícito del cliente (02/09/2026): "el usuario tiene que reflejar un gasto que paga un sueldo mitad en efectivo y mitad transferencia" → confirmado "un solo gasto con varias líneas de pago" (se descartó la alternativa de cargar 2 Gastos separados, que ya funcionaba sin cambios de código).

**Diseño**: mismo patrón exacto que `PagoVenta`/`PagoOrdenCompra` — un `Gasto` (Categoría/Subcategoría/Descripción/Fecha, sigue siendo un único registro) pasa a tener una colección de `GastoPago` (cada línea: Forma de pago + Monto). `Gasto.Monto` deja de cargarse a mano y pasa a ser la suma de las líneas (igual criterio que `Venta.Total`). `Gasto.FormaPago` (campo único) se retira — no tiene sentido una vez que puede haber más de una forma de pago por gasto.

**Arquitectura**:
- Nueva entidad `GastoPago { Id, GastoId, FormaPago, Monto }` (sin `SoftDestroyable` — no hay plan de eliminar una línea suelta, el Gasto completo se anula como siempre).
- `Gasto` pierde `FormaPago`, gana `ICollection<GastoPago> Pagos`.
- `GastoService.CrearAsync` recibe `List<GastoPagoInput>` en vez de `Monto`/`FormaPago` sueltos — valida al menos 1 línea con Monto > 0, calcula el total, crea el `Gasto` + sus `GastoPago`, y postea **un único** movimiento de Egreso en CC Local por el total (sin cambios respecto de hoy — Gasto no tiene el concepto de acreditación diferida de Venta/OC, no hace falta un movimiento por línea).
- `GastoService.AnularAsync` sin cambios de lógica (sigue revirtiendo `Gasto.Monto`, ahora el total ya calculado).
- **Migración con backfill**: nueva tabla `GastosPago`, `INSERT... SELECT` de cada `Gasto` existente como su propia línea única (mismo `FormaPago`/`Monto` que ya tenía), después se elimina la columna `Gastos.FormaPago`. Mismo criterio de migración con corrección de datos ya usado en CR-5 (`UPDATE...CASE`) — acá es un `INSERT...SELECT`, sin pérdida de información (cada Gasto viejo queda con exactamente 1 línea, idéntica a como estaba).
- `GastoListItemDto`/`GastoDetailDto`: `FormaPago` (string único) pasa a listar todas las líneas — mismo patrón que `VentaListItemDto.FormasPago` (post-proceso por fila, sin `Include` en la query paginada, `string.Join(", ", ...)`).
- `GastoFiltro.FormaPago`: sigue filtrando gastos que tengan **al menos una** línea con esa forma de pago (`g.Pagos.Any(...)`, mismo criterio que `VentaFiltro.Metodo`).
- `GastoRecurrente` (plantilla, CR-62) no cambia de forma — sigue prellenando una sola Forma de pago (la de la primera línea); si el gasto real termina con más de una línea, las demás se cargan a mano. No se amplía a plantillas multi-línea en este alcance.
- `Gastos/Create.cshtml`: el bloque de Monto/Forma de pago pasa a una lista de líneas repetible (agregar/quitar, mismo patrón visual que `Ventas/Create.cshtml`), con un total en vivo. `Gastos/Details.cshtml`: muestra la tabla de líneas en vez de una Forma de pago/Monto únicos.

**Impacto en capas**: Domain (`GastoPago` nueva, `Gasto` sin `FormaPago`), Application (`GastoPagoInput`, `GastoInput`, `GastoListItemDto`, `GastoDetailDto`, `GastoFiltro` sin cambio de forma pero de semántica), Infrastructure (`GastoService.cs`, `AppDbContext.cs`), Web (`GastosController.cs`, `GastoViewModels.cs`, `Gastos/Create.cshtml`, `Gastos/Details.cshtml`). **1 migración EF con backfill de datos** (~500 `Gasto` existentes, sin pérdida de información).

## CR-69 — Edición inline (on-demand, AJAX) de la nota de un pago desde Ventas/Details

Pedido explícito del cliente (02/09/2026): "el usuario quiere poder editar la nota del pago o detalle on demand en la pantalla vía AJAX dentro del detalle de la venta" — extensión directa de CR-68.

Nuevo `IVentaService.ActualizarNotaPagoAsync(pagoVentaId, nota)` — sin restricción de estado (Nota es solo texto de referencia, sin impacto en Caja/Estado de la Venta, editable en cualquier momento). En `Ventas/Details.cshtml`, la celda de nota de cada pago pasa de texto estático a un patrón click-to-edit: click en el texto (o "+ Agregar nota" si está vacío) lo convierte en un `<input>`, que guarda solo al perder el foco o con Enter — sin recargar la pantalla, mismo nivel de permiso que "Registrar pago" (`RequireVentas`, no restringido a Administrador).

**Impacto en capas**: Application (`IVentaService`), Infrastructure (`VentaService.cs`), Web (`VentasController.cs` — acción `ActualizarNotaPago` nueva, endpoint JSON puro, `Ventas/Details.cshtml`). Sin migración EF (reutiliza la columna de CR-68).

## CR-68 — Nota opcional al registrar un pago de Venta

Pedido explícito del cliente (02/09/2026): "al registrar un pago de una venta se solicita una nota opcional de referencia del pago."

`PagoVenta` gana `Nota` (`string?`, max 500) — igual criterio que `Venta.NotaInterna`: texto libre, nunca aparece en ningún comprobante/PDF. Disponible en los 2 puntos donde se crea un `PagoVenta`: al confirmar la Venta (`Ventas/Create.cshtml`, un input "Nota (opcional)" por línea de pago) y al registrar un pago sobre una Venta ya creada (`Ventas/Details.cshtml`, card "Registrar pago"). Se muestra en la tabla de Pagos de `Ventas/Details` (debajo de cuotas/monto base, en cursiva).

**Impacto en capas**: Domain (`PagoVenta.Nota`), Application (`PagoVentaDto`/`PagoVentaInput`/`PagoVentaLineaInput`), Infrastructure (`VentaService.cs`, `PagoVentaService.cs`), Web (`VentasController.cs`, `Ventas/Create.cshtml`, `Ventas/Details.cshtml`). **1 migración EF** (`AddPagoVentaNota`, columna nullable, sin backfill).

## CR-67 — Ventas/Compras/pagos cancelados ocultos de informes por defecto + integridad de Cuenta Corriente de Proveedores al cancelar OC

Pedido explícito del cliente (02/09/2026): "tanto las ventas y pagos cancelados como las compras y pagos a proveedores cancelados no se deben mostrar en ningún informe [...] para no prestar a confusión." Disparado por una auditoría de infraestructura del mismo día que encontró 3 gaps preexistentes del lado Compras, espejo de los bugs ya corregidos en Ventas (CR-64/65).

**Decisiones confirmadas por el cliente (`AskUserQuestion`)**: (1) ocultas de los listados principales por defecto, pero auditables vía filtro explícito — **no** baja lógica real (hubiera roto el link "Origen" de CC Local armado en CR-62, y la posibilidad de investigar un caso puntual como se hizo hoy con la Venta #694); (2) también ocultar del ledger de Cuenta Corriente (Local y Proveedores) los movimientos de origen cancelado, con un checkbox "Mostrar cancelados" para verlos igual.

**Parte A — cierre de los 3 gaps de Compras** (mismo patrón que CR-64/65, del lado OrdenCompra/Cheque):
- `OrdenCompraService.CancelarAsync`: un `PagoOrdenCompra` `Pendiente` sin cheque asociado se soft-deletea al cancelar (nada que revertir); uno ya `Pagado` (pago anticipado antes de Recibida) se revierte con un Cargo de reversión en `MovimientosCCProveedor` — antes quedaba un Pago sin su contra-Cargo, subestimando la "Deuda total a proveedores" del Dashboard.
- `ChequeService.AcreditarAsync`: nuevo guard — no se puede acreditar un cheque de una OC ya Cancelada.
- Jobs de notificación de Cheques y de pagos programados: excluyen items de una OC Cancelada.

**Parte B — ocultar por defecto**:
- `VentaService.ListarAsync`/`OrdenCompraService.ListarAsync`: cuando no se elige un Estado explícito, excluyen Cancelada (el `<select>` de Estado ya tenía "Cancelada" como opción — sigue disponible eligiéndola a mano).
- `MovimientoCCLocalFiltro`/`MovimientoCCProveedorFiltro` ganan `IncluirCanceladas` (default `false`); `CCLocalService.ListarAsync`/`CCProveedorService.ListarMovimientosAsync` excluyen movimientos de origen cancelado salvo que se tilde el nuevo checkbox. Los saldos/totales (`ObtenerSaldoFiltradoAsync`, `ObtenerSaldoTotalAsync`) no se tocan — ya son correctos gracias a la Parte A, ocultar filas no cambia ningún número.

**Hallazgo de QA (MH-019, corregido antes de deploy)**: el guard nuevo de `AcreditarAsync` cerraba la única salida de un cheque de OC cancelada, pero el Dashboard ("Cheques por vencer") y la Proyección Financiera (cheques + pagos programados) no lo excluían — hubiera quedado colgado para siempre en esos 2 informes. Corregido con el mismo filtro en los 3 lugares.

**Impacto en capas**: Infrastructure (`OrdenCompraService.cs`, `ChequeService.cs`, `PagoOrdenCompraService.cs`, `VentaService.cs`, `DashboardService.cs`, `ProyeccionFinancieraService.cs`, `CCLocalService.cs`, `CCProveedorService.cs`), Application (`MovimientoCCLocalFiltro`/`MovimientoCCProveedorFiltro`), Web (`CCLocalController.cs`, `ProveedoresController.cs`, `CCLocal/Index.cshtml`, `Proveedores/CuentaCorriente.cshtml`). Sin migración EF.

## CR-66 — Fix: "Saldo actual del período filtrado" daba números sin sentido de negocio al filtrar por un mes con un ajuste puntual grande

Reporte directo del cliente (02/09/2026): "Saldo actual del período filtrado $ -90.041.783,05 esta muy mal creo. hay que hacer un punto de partida con saldo 0."

**Investigación**: el número era matemáticamente correcto — filtrando agosto completo, la suma de Ingresos menos Egresos de ESE MES da exactamente -$90.041.783,05, porque en agosto cayó el movimiento "Ajuste de apertura — saldo migrado a $0 para inicio de operación real" (Egreso $96.986.104,22, 10/08/2026) — **el "punto de partida con saldo 0" que pedía el cliente ya existía**, se hizo al arrancar el sistema real. El saldo real total, acumulado desde siempre, era correcto: $8.337.562,99.

**Causa raíz real**: `ObtenerSaldoFiltradoAsync` (CR-62) sumaba los movimientos **dentro** de la ventana de fechas elegida — un criterio que da un número sin sentido de negocio cada vez que la ventana contiene un ajuste puntual grande (apertura, corrección). Un "saldo" real siempre es un valor **acumulado a una fecha** (igual que "saldo al 31/08" de un resumen bancario), nunca la suma de lo que pasó solo dentro de un rango arbitrario.

**Fix**: `ObtenerSaldoFiltradoAsync` pasa a ignorar `Tipo`/`FechaDesde` del filtro y calcula el saldo real acumulado (Ingresos−Egresos de **toda** la cuenta) hasta `FechaHasta` — sin fecha, es el saldo actual completo. La lista de movimientos de abajo sigue filtrada igual que siempre (Tipo/FechaDesde/FechaHasta, sin cambios) — solo cambió el número de la cabecera. La etiqueta pasa de "del período filtrado" a "al {fecha}" para reflejar el nuevo significado.

**Impacto en capas**: Infrastructure (`CCLocalService.cs`), Web (`CCLocal/Index.cshtml`). Sin migración EF.

## CR-65 — Fix: cancelar una Venta con pago pendiente reversaba dinero que nunca entró a Caja

Reporte directo del cliente (02/09/2026), sobre el mismo caso de CR-64 (Venta #694): en Cuenta Corriente Local seguía apareciendo el movimiento "Egreso $318.999,56 — Reversión por cancelación de venta #694", distorsionando el saldo del período. "Si una venta está cancelada, el pago está cancelado y no debe influir en el estado de cuenta."

**Causa raíz**: `VentaService.CancelarAsync` reversaba siempre `venta.Total` completo como Egreso, sin importar cuánto de ese total realmente se había posteado como Ingreso en Caja. Un pago con tarjeta `Pendiente` nunca postea su Ingreso (CA-CR32.3/34.2, diferido hasta `AcreditarPagoAsync`) — la Venta #694 tenía **un único** pago, todavía Pendiente al cancelarse, así que nunca entró un solo peso a Caja por esta venta. Aun así, `CancelarAsync` reversaba el total completo, restando dinero que jamás había entrado.

**Fix**: el monto a reversar pasa a ser la suma de `Monto` de los pagos que **sí** llegaron a postear su Ingreso (`EstadoAcreditacion != Pendiente`) — no `venta.Total`. Si esa suma da 0 (como en #694), no se postea ningún movimiento de reversión: no hay nada que revertir.

**Corrección de datos**: el movimiento erróneo (#1201, Egreso $318.999,56) **no se editó ni se borró** (el ledger es inmutable, mismo criterio de todo el proyecto) — se posteó un contramovimiento (Ingreso $318.999,56, mismo origen, `EsReversion=true`) que neutraliza su efecto, dejando el saldo correcto y ambos movimientos visibles para auditoría.

**Impacto en capas**: Infrastructure (`VentaService.cs`). Sin migración EF.

## CR-64 — Fix: cancelar una Venta con pago pendiente dejaba un pago "colgado" que revertía la cancelación

Reporte directo del cliente (02/09/2026), con evidencia concreta: Venta #694, en estado Cancelada, tenía un pago con tarjeta que seguía `EstadoAcreditacion=Pendiente` (nunca llegó a acreditarse antes de cancelar). El cliente entró a la Venta, eliminó ese pago (`EliminarPagoAsync`), y la Venta pasó de `Cancelada` a `Pendiente` sola. Pedido explícito: "al cancelar la venta se tienen que cancelar los pagos asociados, aunque estén pendientes."

**Causa raíz**: un pago con tarjeta `Pendiente` nunca postea su Ingreso (CA-CR32.3/34.2 difiere el posteo hasta `AcreditarPagoAsync`) — al cancelar la Venta, `CancelarAsync` no hacía nada con esos pagos, quedaban "colgados" en Pendiente indefinidamente. `EliminarPagoAsync` (CR-36), al borrar cualquier pago, **siempre** recalculaba `Venta.Estado` en base a los pagos restantes — sin verificar si la Venta ya estaba Cancelada, revirtiendo la cancelación por accidente.

**Fix** (2 partes, mismo método que ya usa el soft-delete de `EliminarPagoAsync`):
1. `VentaService.CancelarAsync`: cualquier pago que siga `EstadoAcreditacion=Pendiente` al momento de cancelar se soft-deletea en la misma transacción (no hay nada que revertir en Caja, nunca se posteó). Así, una Venta recién cancelada nunca vuelve a tener un pago Pendiente colgando.
2. `VentaService.EliminarPagoAsync`: guard nuevo — si la Venta ya está `Cancelada`, no se recalcula su `Estado` (queda como está). Protege los casos ya existentes en producción (cancelados antes de este fix, con pagos pendientes todavía sin eliminar).

**Corrección de datos**: Venta #694 tenía `Estado=Pendiente` con `MotivoCancelacion`/`FechaCancelacion` todavía intactos (evidencia de que la cancelación fue real, solo el `Estado` quedó mal por la eliminación manual del pago) — corregido directamente a `Cancelada` en producción, sin tocar el resto de los campos.

**Impacto en capas**: Infrastructure (`VentaService.cs`). Sin migración EF.

## CR-63 — Fix: la fecha de acreditación manual no se actualizaba a la fecha real de la acción

Reporte directo del cliente (02/09/2026), con evidencia concreta: "Venta #000687... Venta #000681... los pagos de las ventas se liquidaron el mes pasado, el usuario los marcó como acreditados hace unos días y el movimiento sigue estando con fecha de acreditación posterior... cuando se acredita un pago manualmente se debe pisar la fecha de acreditación a la fecha en que se realizó la acción."

**Causa raíz**: `PagoVenta.FechaAcreditacionEfectiva` se carga como fecha *sugerida* al registrar el pago (CR-34, ej. la fecha estimada de acreditación de una tarjeta a 6 cuotas) — pero `VentaService.AcreditarPagoAsync` (la acción manual del Administrador) nunca la actualizaba al confirmar: seguía usando la fecha sugerida original, sin importar cuándo ocurriera realmente el click. Mismo defecto exacto, mismo mecanismo, en `PagoOrdenCompraService.ConfirmarPagoAsync` (`PagoOrdenCompra.FechaPagoTentativa`, lado Compras) — corregido en el mismo paso aunque no fue reportado explícitamente, porque el principio que pidió el cliente aplica idéntico ahí.

**Fix**: en ambos métodos, justo antes de postear el movimiento de Cuenta Corriente, se pisa la fecha (`FechaAcreditacionEfectiva`/`FechaPagoTentativa`) con `HorarioArgentino.Ahora.Date` (hoy, hora Argentina) — el movimiento posteado usa esa fecha ya actualizada, así que el Ingreso/Pago cae en el período contable real de la acción, no en la fecha estimada original.

**Corrección retroactiva investigada** (vía `AuditLog`, que registra automáticamente cada cambio de `EstadoAcreditacion`): de 157 `PagoVenta` con tarjeta ya `Acreditado`, 151 no tienen registro en `AuditLog` (corresponden a la migración del histórico previo a esta funcionalidad, no al bug — no se tocan). **5 sí tienen evidencia real de discrepancia** entre la fecha guardada y la fecha real del click (confirmada por `AuditLog.Timestamp`): Pago #9 (18/08→21/08), #678 (19/08→27/08), #700/Venta #681 (11/09→26/08, el caso citado por el cliente), #704 (14/08→26/08), #707/Venta #687 (15/09→31/08, el otro caso citado). Investigación de solo lectura, sin escribir nada — pendiente de confirmación del cliente antes de corregir estas 5 filas (y su `MovimientoCCLocal` asociado) contra producción.

**Impacto en capas**: Infrastructure (`VentaService.cs`, `PagoOrdenCompraService.cs`). Sin migración EF.

## CR-62 — Gastos (categoría/forma de pago/recurrentes) + Cuenta Corriente Local (usuario/origen clickeable/saldo filtrado)

Pedido explícito del cliente vía `/agentes-ia-orquestador` (31/08/2026), disparado por una consulta real sobre cómo cargar la comisión de mantenimiento del Banco Provincia (débito automático, monto variable mes a mes, ej. $65.000). 6 puntos en el mismo mensaje:

**Discovery**: `CategoriaGasto`/`FormaPagoGasto` son enums simples, sin lógica condicionada a ningún valor puntual (a diferencia de `MetodoPago`) — las vistas ya generan sus `<select>` dinámicamente desde el enum (`Enum.GetValues<T>()`), así que agregar un valor nuevo no requiere tocar ninguna vista. No existe hoy ningún concepto de "gasto recurrente"/plantilla en el sistema. `MovimientoCCLocal` no tiene columna `UsuarioId` — el nombre (hoy el GUID crudo) está concatenado dentro del string libre `Descripcion` en 2 lugares (`VentaService.AcreditarPagoAsync`/`EliminarPagoAsync`), no en un campo estructurado. La columna "Origen" de `CCLocal/Index.cshtml` es texto plano, sin precedente en el proyecto de un link condicional por tipo de origen (los 2 casos de link clickeable que existen — Cheques→OC, PagosTarjeta→Venta — apuntan siempre al mismo tipo fijo). `Gasto` no tiene pantalla `Details` (solo `Index`/`Create`, es inmutable). `ObtenerSaldoActualAsync()` es el saldo TOTAL histórico sin filtro, usado en 2 lugares: `CCLocalController.Index` (el que hay que cambiar) y `DashboardController.GetBalanceCaja` (que debe seguir mostrando el saldo real completo, no tocar).

**Decisiones confirmadas por el cliente (`AskUserQuestion`)** sobre el punto de gastos recurrentes (el único con forks genuinos):
1. **Solo prellenar el formulario, sin crear el gasto solo.** Una plantilla guarda Categoría/Subcategoría/Forma de pago/Descripción — el usuario elige la plantilla al cargar un gasto y esos campos se completan solos, pero Monto y Fecha siempre los tipea y confirma a mano (el monto real varía mes a mes, según el resumen bancario).
2. **Sin recordatorio automático.** Las plantillas quedan disponibles para elegir manualmente al cargar un gasto — sin job diario ni notificación in-app (a diferencia de Cheques/PagoOC).

**Los 6 puntos**:
1. Nueva categoría `ComisionesBancarias` en `CategoriaGasto` — agregado puro (valor nuevo al final, sin reordenar existentes, no requiere remapeo de datos como sí necesitó CR-5).
2. Nueva forma de pago `DebitoAutomatico` en `FormaPagoGasto` — agregado puro, mismo criterio.
3. Flujo de gastos recurrentes: nueva entidad `GastoRecurrente` (plantilla reutilizable), CRUD propio, integrado como selector de autocompletado en `Gastos/Create`.
4. `MovimientoCCLocal` gana `UsuarioId` estructurado — el nombre de usuario se resuelve en el listado (mismo patrón ya usado por `StockService.ListarMovimientosAsync`), en vez de quedar embebido como GUID crudo en el texto libre de `Descripcion`. Corrección retroactiva de los movimientos históricos ya afectados (script dedicado, dry-run + apply).
5. Columna "Origen" de `CCLocal/Index.cshtml` pasa a ser un link — a `Ventas/Details/{id}` si el origen es una Venta, a la nueva `Gastos/Details/{id}` (pantalla que no existía, se agrega) si es un Gasto.
6. `CCLocal/Index` arranca con el filtro de fecha en el mes actual por defecto (si no hay filtro guardado en sesión), y el "Saldo actual" de la cabecera pasa a ser el total (Ingresos−Egresos) del rango filtrado, no el saldo histórico completo — nuevo método aparte, sin tocar `ObtenerSaldoActualAsync()` (que sigue siendo el saldo real completo, usado por el Dashboard).

**Impacto en capas**: Domain (`CategoriaGasto`, `FormaPagoGasto`, nueva entidad `GastoRecurrente`, `MovimientoCCLocal.UsuarioId`), Application (`IGastoRecurrenteService` nuevo, `ICCLocalService` con método nuevo, DTOs), Infrastructure (`GastoRecurrenteService` nuevo, `CCLocalService.cs`, `VentaService.cs` — 2 call sites), Web (`GastosRecurrentesController` nuevo, `GastosController.cs`/`Gastos/Create.cshtml`/`Gastos/Details.cshtml` nueva, `CCLocalController.cs`/`CCLocal/Index.cshtml`). **2 migraciones EF** (tabla `GastosRecurrentes` nueva; columna `UsuarioId` nullable en `MovimientosCCLocal`, sin backfill de esquema — la corrección de los textos históricos es un script de datos aparte, no parte de la migración).

## CR-61 — Stock: listado de productos con edición inline reemplaza Ajuste manual

Pedido explícito del cliente vía `/agentes-ia-orquestador` (27/08/2026): "quiero refactorizar la pantalla Ajuste manual de stock y Movimientos de stock. quiero reemplazar la pantalla principal de stock, en vez que tenga listado de movimientos, tenga un listado de los productos con la opción de editar la cantidad de stock de cada fila on demand, o sea que se actualice el stock desde el listado. esto reemplazaría el ajuste manual por producto y sería más simple para la carga masiva de stock de productos."

**Discovery**: `StockController` hoy tiene 3 pantallas — `Index` (listado de movimientos, ledger `MovimientoStock`), `Ajuste` (formulario: elegir producto con Select2, cargar un delta +/- con Motivo obligatorio, doble confirmación si el resultado da negativo). `Producto.StockActual` es una columna real (no calculada), escrita únicamente por `IStockService` — invariante que se mantiene sin cambios. `MovimientoStock` es un ledger inmutable — tampoco cambia. `ProductosController` ya tiene un listado (`Productos/Index.cshtml`, patrón `ProductoService.ListarAsync`, DataTable server-side con filtros Nombre/Marca/Categoría/Modelo/rango de Stock, columna Stock con badge "Bajo mínimo") — 100% de solo lectura hoy, sin edición inline. Es la base directa a reutilizar para el listado nuevo.

**Escaneo de reutilización (obligatorio)**: encontrado un precedente conceptual real en ShowroomGriffin (`Stock/MatrizEditar.cshtml` + `StockService.cs`) — grilla editable donde cada celda reemplaza el stock (no un delta), sin la doble confirmación por negativo que tiene `AjustarAsync` porque el input tiene `min="0"` (no se puede escribir un valor negativo). Se reutiliza esa idea de "reemplaza, no delta" y "min=0 elimina la necesidad de confirmar negativo". El mecanismo de guardado de ShowroomGriffin es un **form completo con submit en lote** (`Celdas[i].CantidadNueva`, un solo POST con todas las filas) — no aplica acá: el cliente eligió guardado por fila al instante (AJAX on-demand por celda), un patrón de transporte distinto que no tiene precedente directo en ningún proyecto del estudio y se diseña de cero.

**Decisiones confirmadas por el cliente (`AskUserQuestion`)**:
1. **Semántica de edición: reemplaza, no delta.** Se escribe el stock real (ej. resultado de un conteo físico) — el sistema calcula la diferencia contra `Producto.StockActual` y postea esa diferencia como `MovimientoStock.Cantidad` (con signo), igual que hoy internamente, pero sin pedirle al usuario que haga la cuenta.
2. **Guardado por fila al instante.** Cada celda se guarda apenas se edita (blur/Enter), sin un paso de revisión en lote — coincide con "on demand" tal como lo pidió el cliente.
3. **Sin motivo.** A diferencia de `Ajuste manual` (Motivo obligatorio, validado), la edición inline **no le pide nada al usuario** — decisión explícita del cliente ("sin motivo"), priorizando velocidad de carga masiva. El ledger sigue recibiendo un `MovimientoStock.Motivo` no vacío (texto fijo "Ajuste desde listado de Stock", generado por el sistema, no tipeado por el usuario) para no romper la invariante ya documentada de que un `MovimientoStock.Tipo=Ajuste` siempre tiene motivo — el cliente pidió no ser interrumpido con el campo, no que el ledger quede sin contexto.
4. **Retirar Ajuste manual del menú; Movimientos pasa a link secundario.** `Stock/Index` deja de ser el listado de movimientos y pasa a ser el listado de productos editable. El listado de movimientos (ledger, ya existente, sin cambios funcionales) se mueve a una ruta secundaria (`Stock/Movimientos`), accesible con un link desde la pantalla nueva, no como ítem de menú aparte. La pantalla `Ajuste` (formulario) se **retira completamente** — código incluido, no solo oculto del menú (criterio del proyecto: no dejar pantallas muertas alcanzables por URL directa una vez reemplazadas, mismo criterio ya aplicado al retirar `OrdenesCompraController.GetResumenFacturacion` cuando se sacó su badge).

**Qué NO cambia** (invariantes a preservar, confirmadas en el Discovery): `Producto.StockActual` sigue siendo columna real, no calculada. `MovimientoStock` sigue siendo ledger inmutable. `IStockService.RegistrarMovimientoAsync` (usado por Venta/OrdenCompra, nunca bloquea por negativo) no se toca. La alerta de "stock bajo mínimo" (Dashboard + badge de `Productos/Index`) sigue funcionando igual, sin cambios — sigue leyendo `StockActual` directo.

**Impacto en capas**: Web (`StockController.cs` reescrito, vistas `Stock/Index.cshtml` nueva, `Stock/Movimientos.cshtml` — renombre del `Index.cshtml` viejo, `Stock/Ajuste.cshtml` eliminada, `ProductosController.cs`/`Productos/Index.cshtml` — botón "Ajustar stock" actualizado), Application (`IStockService` — método nuevo, método viejo `AjustarAsync` retirado junto con `AjusteStockInput`), Infrastructure (`StockService.cs`). Sin migración EF (ningún cambio de esquema, `MovimientoStock`/`Producto` ya tienen todos los campos necesarios).

**Extensión del mismo día (31/08/2026)**: pedido explícito del cliente ("hacer lo mismo con la columna de stockminimo") — la columna Stock mínimo del mismo listado pasa a ser editable inline, mismo mecanismo (AJAX al blur/Enter, sin motivo). A diferencia de Stock, esto **no pasa por `IStockService`** ni genera `MovimientoStock`: `StockMinimo` es un umbral de alerta de `Producto`, no una cantidad de inventario — nuevo `IProductoService.ActualizarStockMinimoAsync(productoId, nuevoStockMinimo)`, mismo dueño que ya escribe ese campo desde el formulario de Editar. Al guardar, el input de Stock de la misma fila actualiza su `data-stock-minimo` y recalcula el badge "Bajo mínimo" sin recargar la tabla, para que quede correcto si el usuario edita ambas celdas de una fila en la misma sesión. Sin migración EF.

## CR-60 — Cheques de compra: plazo de días editable a mano (deja de ser fijo 30/60/90)

Pedido explícito del cliente (27/08/2026): "en Orden de compra al agregar pagos con cheque el usuario quiere completar a mano la cantidad de días, y que en base a eso se calcule la fecha efectiva de cobro (en vez de 30/60/90 que la cantidad de días sea configurable a mano)."

**Investigación**: `Cheque.Cuota` (el campo real, "días de plazo") nunca tuvo una restricción de valores a nivel de `Domain`/`Service` — el único lugar donde el plazo quedaba limitado a 30/60/90 era el `<select>` de `OrdenesCompra/Details.cshtml` (3 `<option>` fijas). El autocálculo de vencimiento (`autocalcularVencimientoCheque`, CR-2) ya era genérico (`FechaVencimiento = FechaEmision + cuota días` con cualquier entero), así que no hizo falta tocarlo.

**Fix**: el `<select>` se reemplaza por un `<input type="number" min="1">` de días libre, con el mismo default sugerido de 30 días al pasar el método a Cheque (CR-15, sin cambios) — el autocálculo de vencimiento sigue disparando en cada cambio, ahora con `input` en vez de `change` para recalcular mientras el usuario escribe. Sin cambios en `Domain`, `Service` ni migración — el campo ya aceptaba cualquier entero.

**Impacto en capas**: Web (`OrdenesCompra/Details.cshtml`, solo JS/markup). Sin migración EF.

## CR-59 — Pagos con tarjeta de crédito a liquidar (listado dedicado + card Dashboard)

Pedido del cliente vía `/agentes-ia-orquestador` (27/08/2026), planteado como pregunta abierta: "el cliente quiere integrar en alguna pantalla un listado de pagos con tarjeta de crédito a liquidar, ¿o se necesita una pantalla nueva? ¿o podríamos ponerla en el dashboard?"

**Discovery**: el modelo ya tiene todo lo necesario, construido en CR-32/33/34/35 — `PagoVenta.EstadoAcreditacion` (Pendiente/Acreditado, solo aplica a `Metodo=TarjetaCredito`), `FechaAcreditacionEfectiva`, `IVentaService.AcreditarPagoAsync` (acción manual, Administrador-only) y el job diario `PagoVentaAcreditacionHostedService` (notifica cuando llega la fecha, nunca acredita solo — mismo patrón que `ChequeAcreditacionHostedService`). Hoy esos pagos solo son visibles uno por uno, adentro de cada `Ventas/Details` — no existe ningún lugar donde verlos todos juntos.

**Decisión de ubicación** (recomendada por el analista, confirmada por el cliente: "sí, implementar"): pantalla nueva dedicada, análoga a `Cheques/Index.cshtml` (mismo patrón exacto: listado filtrable + acción "Acreditar" inline) — no el Dashboard solo. El Dashboard tiene una regla fija (HU-9.1): cada card es un KPI numérico que carga solo, nunca una tabla con acciones (por eso "Cheques por vencer" es una card chica que linkea a su propia pantalla completa). Se agregan **las dos cosas**: pantalla nueva (el listado real, con el botón Acreditar) + una card en el Dashboard que linkea a ella (mismo patrón que ya usan "Cheques por vencer" y "Balance de caja").

**Alcance confirmado**:
- Pantalla nueva `PagosTarjeta/Index.cshtml` (Administrador-only, mismo criterio que `AcreditarPagoAsync`), clon del patrón `Cheques/Index.cshtml`: filtro por Estado (Pendiente/Acreditado — sin Rechazado, `PagoVenta` no tiene ese estado) y por rango de fecha de acreditación, columnas Venta (link a Details)/Cliente/Cuotas/Monto/Fecha de pago/Fecha de acreditación/Estado, resaltado de fila "vence próximo" (≤7 días, mismo criterio que Cheques), botón "Acreditar" (solo si Pendiente) que reutiliza `AcreditarPagoAsync` sin tocarlo.
- Nuevo método de solo lectura `IVentaService.ListarPagosTarjetaAsync(request, filtro)` — filtra `PagosVenta` por `Metodo=TarjetaCredito`, mismo patrón DataTable server-side que `ChequeService.ListarAsync`.
- Nueva entrada de menú lateral (`_Layout.cshtml`, junto a "Cheques").
- Nueva card "Pagos con tarjeta por acreditar" en `Dashboard/Admin.cshtml` (Administrador-only, mismo patrón AJAX independiente que "Cheques por vencer") — cantidad + monto de `PagosVenta` con `EstadoAcreditacion=Pendiente`, link a la pantalla nueva.

**Fuera de alcance**: no se toca `AcreditarPagoAsync`, `PagoVentaAcreditacionHostedService` ni ningún cálculo existente (Caja, Proyección financiera) — es una superficie de lectura + 1 acción ya existente, sin lógica de negocio nueva.

**Impacto en capas**: Application (`IVentaService` +1 método, DTOs nuevos `PagoTarjetaListItemDto`/`PagoTarjetaFiltro`/`PagosTarjetaPendientesDto`), Infrastructure (`VentaService.cs`), Web (`PagosTarjetaController` nuevo, `Views/PagosTarjeta/Index.cshtml` nuevo, `DashboardController.cs` +1 acción, `Dashboard/Admin.cshtml` +1 card, `_Layout.cshtml` +1 link de menú). **Sin migración EF** (todos los campos ya existen).

## CR-58 — Órdenes de compra: tag de facturación + Dashboard "vista CEO" (4 métricas nuevas)

Pedido explícito del cliente (26/08/2026), 3 partes en un mismo mensaje: "Órdenes de compra: agregar un tag para saber cuántas órdenes de compra están facturadas y cuántas no facturadas. Agregar mismo indicador en pantalla dashboard. Hacer un análisis de la estructura de datos del proyecto hasta el día de la fecha (ventas, compras, pagos, cheques) y sumar datos útiles para CEO del negocio en la pantalla dashboard del sistema".

**Parte 1 — Tag de facturación de OC**: `OrdenCompra.Facturada` ya existía (bool simple, cargado a mano al confirmar si el proveedor entregó su propia factura — sin relación con AFIP, que es exclusivamente del lado Ventas). Nuevo `IOrdenCompraService.ObtenerResumenFacturacionAsync(desde?, hasta?)` agrega cantidad/monto facturado y no facturado sobre las OC no canceladas, con un rango de fecha opcional. Consumido por la card "Compras del período" en `Dashboard/Admin.cshtml` — pedido explícito de ajuste del cliente (26/08/2026: "igualar el formato que tiene la card de ventas") para que se vea idéntica a "Ventas del período" (título, total grande, "xx compra(s)", badges Facturado/No facturado), filtrada por el mismo `desde`/`hasta` del Dashboard. El badge original en `OrdenesCompra/Index.cshtml` (histórico completo, sin fecha) se agregó primero y **se eliminó a pedido explícito del cliente el mismo día** (27/08/2026: "eliminar Facturadas/No facturadas... de la pantalla /OrdenesCompra") — junto con la acción `GetResumenFacturacion` de `OrdenesCompraController`, que quedó sin uso. El dato sigue disponible únicamente en la card del Dashboard.

**Parte 2 — 4 métricas nuevas "vista CEO" en el Dashboard**: se investigó la estructura de datos existente (Ventas, OC, CC Proveedor, Gastos, Cheques) y se propusieron 5 candidatas; el cliente confirmó 4 vía 2 `AskUserQuestion` (quedó afuera "Tasa de conversión Presupuesto→Venta"):
1. **Deuda total a proveedores**: nuevo `ICCProveedorService.ObtenerSaldoTotalAsync()` (Cargo − Pago de `MovimientoCCProveedor`, sin filtrar por proveedor — mismo cálculo que `ObtenerSaldoActualAsync` sin el `Where` por Id).
2. **Margen bruto del período**: nuevo `IDashboardService.ObtenerMargenBrutoAsync(desde, hasta)` — Subtotal de `VentaItem` (ventas no canceladas del período) menos `Cantidad × Producto.PrecioCompra` **actual**. Limitación aceptada explícitamente por el cliente al confirmar la métrica: el sistema no versiona el precio de compra histórico por ítem, así que un producto que cambió de costo distorsiona el margen de ventas pasadas.
3. **Gastos operativos del período**: nuevo `IGastoService.ObtenerTotalPeriodoAsync(desde, hasta)` — suma de `Gasto.Monto` no anulado en el rango.
4. **Ticket promedio de venta**: agregado directo a `VentasPeriodoDto.TicketPromedio` (Total/Cantidad del período) — sin endpoint nuevo, reutiliza el mismo fetch de la card "Ventas del período" ya existente.

Las 3 métricas nuevas con endpoint propio (Deuda, Margen bruto, Gastos operativos) siguen el mismo criterio de protección que Cheques/Balance de caja: `[Authorize(Policy = "RequireAdministracion")]` explícito en el endpoint, más allá de que la UI ya las oculte al Vendedor (regla REG-010).

**Impacto en capas**: Application (`OrdenCompraDtos.cs`, `DashboardDtos.cs`, `IOrdenCompraService`, `IDashboardService`, `ICCProveedorService`, `IGastoService`), Infrastructure (`OrdenCompraService.cs`, `DashboardService.cs`, `CCProveedorService.cs`, `GastoService.cs`), Web (`DashboardController.cs`, `OrdenesCompraController.cs`, `OrdenesCompra/Index.cshtml`, `Dashboard/Admin.cshtml`). Sin migración EF (todo agregados/consultas, sin columnas nuevas).

## CR-57 — Método de pago "Tarjeta de débito" en Ventas y Compras

Pedido explícito del cliente (21/08/2026): "agregar método de pago débito en las ventas y en las compras".

**Decisiones confirmadas con el cliente** (2 `AskUserQuestion` antes de implementar, porque contradicen a primera vista la regla ya vigente de "Modelo de precios"):
1. **Precio**: Débito cobra precio **"Efectivo"**, no "Transferencia (+21%)" — a diferencia de Tarjeta de Crédito/Transferencia/MercadoPago/Banco Carrefour (que siempre exigen precio de lista desde CR-40). Actualiza el "Modelo de precios": el precio efectivo ya no es exclusivo del método Efectivo, ahora lo comparten Efectivo y Débito.
2. **Acreditación**: Débito se acredita al instante (como Efectivo/Transferencia/MercadoPago), **nunca** el circuito de acreditación diferida de CR-34 (fecha efectiva, badge Pendiente, "Marcar acreditado") que sí tiene Tarjeta de Crédito.

**Alcance**: `MetodoPago` gana `TarjetaDebito = 8`, habilitado en **ambos** contextos — Ventas (`VentaService.MetodosPermitidosVenta`, `PagoVentaService.MetodosPermitidosVenta`) y Compras (`PagoOrdenCompraService.MetodosPermitidosOC`) — a diferencia de Tarjeta de Crédito/Banco Carrefour, que siguen exclusivos de Ventas. Como Débito **no** se agrega a `metodosRequierenConIva` (el array que exige precio "de lista"), automáticamente queda en el mismo grupo flexible que Efectivo para la validación de CR-40 (CA-CR40.3) — sin tocar esa validación. Como ningún chequeo de cuotas/acreditación diferida está keyado a `TarjetaDebito` (todos son `== TarjetaCredito` explícito), Débito no dispara ninguno — se comporta exactamente como un pago simple (igual que Efectivo/Transferencia/MercadoPago), sin cuotas ni fecha de acreditación.

**Impacto en capas**: Domain (`MetodoPago` enum), Infrastructure (3 archivos: `VentaService.cs`, `PagoVentaService.cs`, `PagoOrdenCompraService.cs` — solo agregar a las listas de métodos permitidos, sin lógica nueva), Web (`Ventas/Create.cshtml`, `Ventas/Details.cshtml`, `Ventas/Index.cshtml` — filtro, `OrdenesCompra/Details.cshtml` — mapas de métodos y opción de filtro). Sin migración EF (cambio de enum puro, sin columna nueva).

**Nota — no incluido en Entregas**: la pantalla de cobro en la entrega (`Entregas/Details.cshtml`) ya ofrece un subconjunto reducido de métodos (Efectivo/Transferencia/MercadoPago, sin Tarjeta de Crédito ni Banco Carrefour tampoco) — no se tocó, fuera del alcance pedido explícitamente ("en las ventas y en las compras").

## CR-56 — Venta con Factura anulada por Nota de Crédito ya no bloquea Cancelar (MH-013)

Pregunta directa del cliente (21/08/2026): "¿qué condiciones tiene el usuario para poder eliminar la venta? Si se generó una factura de una venta, una nota de crédito de esa factura, y se quiere eliminar la venta, ¿cuál es el proceso correcto?".

**Hallazgo al responder**: el guard de `VentaService.CancelarAsync`/`EditarAsync` (`TieneComprobanteAsociadoAsync`) contaba CUALQUIER `ComprobanteAfip.Estado=Emitido` asociado a la Venta — sin distinguir una Factura vigente de una Factura ya anulada por una Nota de Crédito, ni excluir a la propia NC (que tampoco debería bloquear, no es una obligación fiscal pendiente). Resultado real: una Venta con Factura + NC de esa factura (exactamente el caso "se corrigió una factura mal cargada") quedaba **bloqueada para cancelar**, contradiciendo el propio sentido de CR-55 (poder corregir y seguir operando la venta). Esto era el límite conocido ya documentado como riesgo abierto en el cierre de CR-55/MH-013 (QA lo había catalogado como "minor" al no ser bloqueante para ese release, pero la pregunta del cliente confirmó que sí importa en la práctica).

**Fix**: el criterio de "tiene comprobante que bloquea" pasa a exigir: `TipoComprobante` sea Factura A/B (no Nota de Crédito) **y** que no exista una Nota de Crédito `Emitido` con `ComprobanteAsociadoId` apuntando a esa factura. Aplicado de forma consistente en los 5 lugares donde se repetía el criterio viejo: `VentaService.TieneComprobanteAsociadoAsync` (guard de Cancelar/Editar), `VentaService` listado (`TieneComprobante`), `DashboardService`, `CajaService`, `ProyeccionFinancieraService` — cierra también MH-013 (catalogado en `docs/qa/regresiones-manuales.yml`).

**Condiciones vigentes para cancelar una Venta (documentado, no solo implícito)**:
1. No tiene ninguna Entrega asociada (en ningún estado).
2. No tiene ninguna Factura `Emitido` vigente (una Factura ya anulada por una NC `Emitido`, o un intento en `Estado=Error`, no bloquean).

**Proceso correcto para el escenario del cliente** (Factura + NC de esa factura, se quiere cancelar la Venta): ya no hace falta ningún paso adicional — una vez que la NC quedó `Emitido`, la Venta se puede cancelar directo desde "Cancelar venta", igual que cualquier venta sin facturar.

**Impacto en capas**: Infrastructure (5 archivos, ver arriba). Sin migración EF.

## CR-55 — Nota de Crédito para anular una Factura AFIP emitida por error

Pedido explícito del cliente vía `/agentes-ia-orquestador` (21/08/2026): "el usuario hizo la factura mal, por lo tanto tiene que generar una nota de crédito de la factura emitida para poder anularla, por definición de AFIP".

**Contexto y objetivo**: una factura electrónica con CAE real ya emitida no se puede corregir ni borrar — AFIP exige un documento fiscal separado (Nota de Crédito) que la anule formalmente. Sin esto, un error de carga (CUIT mal, monto mal, cliente equivocado) en la primera factura real recién emitida (CAE 86349291101930, hoy) queda sin forma de corregirse dentro del sistema.

**Decisiones confirmadas con el cliente** (3 `AskUserQuestion` antes de diseñar):
1. **Alcance: Nota de Crédito siempre TOTAL** (nunca parcial) — replica el 100% de ítems/montos/cliente de la factura original. Una NC parcial queda fuera de este alcance (ampliación futura si hace falta).
2. **Reabre la posibilidad de refacturar**: al emitirse con éxito la NC, se revierte `VentaItem.CantidadFacturada` de cada ítem por la cantidad que cubría la factura original — la Venta vuelve a estar disponible para facturarse de nuevo, ya con los datos correctos.
3. **Mismo acceso que Facturar**: Administrador y Vendedor por igual (policy `RequireVentas`, ya vigente en `ComprobantesAfipController` — no se agrega restricción nueva).

**Alcance incluido**:
- Acción "Generar Nota de Crédito" disponible únicamente desde un `ComprobanteAfip` en `Estado=Emitido` (Factura A o B) que todavía no tenga una NC asociada.
- Motivo obligatorio (texto libre, trazabilidad interna — nunca se envía a AFIP), mismo criterio que `Cancelar` de OrdenCompra/Cheque.
- Emisión real contra AFIP vía WSFEv1 (mismo circuito que Facturar), incluyendo el bloque `CbtesAsoc` (tipo/punto de venta/número de la factura original) — requisito de AFIP para vincular la NC a la factura que anula. Mismo Punto de Venta que la original (ya habilitado, Punto de Venta 7).
- Tipo de comprobante derivado automáticamente de la factura original: Factura A (1) → NC A (3); Factura B (6) → NC B (8) — códigos reales de AFIP, mismo criterio que `TipoComprobanteAfip` ya usa hoy (el valor del enum ES el CbteTipo de AFIP, sin mapeo intermedio).
- PDF de la NC reutilizando el diseño de Factura (CR-43), con el encabezado y código de comprobante correspondientes.
- Mismo patrón de reintento (`Estado=Error`, reintentable) que ya tiene `ComprobanteAfip` — si falla la emisión de la NC, la factura original sigue vigente (no se marca anulada hasta que la NC se emita con éxito de verdad).

**Alcance NO incluido (este sprint)**:
- Nota de Crédito parcial.
- Nota de Débito (documento inverso).
- Anular una Nota de Crédito ya emitida.
- Generar una NC sobre un comprobante que no esté `Estado=Emitido` (no tiene CAE real que asociar).

**Reglas funcionales**:
1. Un `ComprobanteAfip` (factura) puede tener a lo sumo 1 Nota de Crédito asociada — si ya la tiene, la acción deja de estar disponible.
2. La factura original queda "anulada" (inferido por tener una NC asociada con `Estado=Emitido`, no un campo booleano nuevo) recién cuando la NC se emite con éxito — no antes.
3. La Nota de Crédito es un `ComprobanteAfip` más (mismo modelo/tabla), no una entidad nueva — se distingue por `TipoComprobante` (NotaCreditoA/B) y por tener `ComprobanteAsociadoId` apuntando a la factura que anula.

**Impacto por capa (preliminar)**:
- Domain: `TipoComprobanteAfip` gana `NotaCreditoA=3`/`NotaCreditoB=8`; `ComprobanteAfip` gana `ComprobanteAsociadoId` (nullable, auto-FK) y `Motivo` (nullable).
- Application: `AfipComprobanteRequestDto` gana el bloque `CbteAsociado` (tipo/puntoventa/número); nuevo Input para "Generar Nota de Crédito" (comprobanteId + motivo).
- Infrastructure: `AfipService.ArmarFecaeSolicitarEnvelope` arma `CbtesAsoc` cuando corresponde; `ComprobanteAfipService` gana `GenerarNotaCreditoAsync` (crea la NC replicando ítems/montos/cliente de la original, emite, revierte `CantidadFacturada` si tiene éxito).
- Web: nueva acción + botón en `ComprobantesAfip/Details`, formulario de motivo (SweetAlert2, mismo patrón que Cancelar OC).
- 1 migración EF (2 columnas nuevas en `ComprobantesAfip`).

**Riesgos y supuestos**:
- Riesgo: el flujo de emisión real recién se validó hoy por primera vez (1 factura real con CAE) — la Nota de Crédito es un `CbteTipo`/bloque `CbtesAsoc` distinto, todavía sin probar contra AFIP real en este sistema. Recomendado probar con un monto bajo antes de confiar el flujo a un caso real de corrección.
- Supuesto: el Punto de Venta 7 (tipo "Web Services", ya habilitado y validado) cubre también la emisión de Notas de Crédito — AFIP no exige un alta separada por tipo de comprobante dentro del mismo punto de venta.

## CR-52 — Bug crítico: AFIP no podía emitir ningún comprobante real ("The system cannot find the file specified")

Reportado por el cliente en producción (20/08/2026): intento real de facturar la Venta #676 (Comprobante AFIP #304, Factura B) falló con "No se pudo emitir el comprobante: The system cannot find the file specified."

**Causa raíz**: `AfipSettings.CertificadoPath` en `appsettings.Production.json` es una ruta relativa (`"Certificados/marihogarprod.p12"`), pasada tal cual a `X509CertificateLoader.LoadPkcs12FromFile` en `AfipService.FirmarCms` — que la resuelve contra el directorio de trabajo ACTUAL del proceso (`Directory.GetCurrentDirectory()`), no necesariamente el `ContentRootPath` del sitio (depende del modelo de hosting IIS/ANCM). Ante cualquier discrepancia entre ambos, .NET lanza el error genérico "The system cannot find the file specified" aunque el archivo exista en el lugar correcto del servidor. Es probable que esta sea la **primera vez que se ejecutó de verdad** el camino real de emisión contra AFIP con el certificado de producción — las 6 facturas reales de CR-42/43 se cargaron directo en la base de datos, sin pasar por `AfipService.EmitirAsync`, así que el bug nunca se había disparado antes.

**Fix**: `AfipService` gana `IWebHostEnvironment` inyectado y resuelve siempre `CertificadoPath` contra `ContentRootPath` (`Path.Combine`, o respeta la ruta tal cual si ya viniera absoluta) — mismo patrón ya usado por `LocalFileStorageService` (con `WebRootPath`) para nunca depender del directorio de trabajo del proceso. Se agrega además un chequeo temprano (`File.Exists`) con un mensaje claro indicando la ruta resuelta exacta, para que un futuro problema de archivo faltante/permisos se diagnostique directo en el mensaje de error en vez de un "file not found" genérico.

**Sin pérdida de datos**: el Comprobante AFIP #304 quedó en estado `Error` (con `DetalleError` guardado, sin CAE — la falla ocurre localmente al cargar el certificado, antes de siquiera llamar al webservice de AFIP), estado ya diseñado para ser reintentable sin necesidad de ninguna corrección de datos — una vez deployado el fix, el Administrador puede reintentar la emisión directo desde la pantalla del comprobante ("Reintentar").

**2do hallazgo (mismo día, mismo comprobante #304 reintentado tras el primer fix)**: el error persistió **idéntico** — confirmado directo contra la base de producción (`ComprobanteAfip.DetalleError`), no solo por lo que reportó el cliente. Esto descarta que el 1er fix no se hubiera aplicado (un redeploy posterior confirmó, por diff de `msdeploy`, que los binarios ya estaban al día) y apunta a la causa real: `X509CertificateLoader.LoadPkcs12FromFile` sin flags usa `X509KeyStorageFlags.DefaultKeySet`, que en Windows intenta persistir la clave privada en el perfil de usuario del proceso (`%USERPROFILE%\AppData\...`). En hosting compartido (IIS), si el Application Pool no tiene "Load User Profile" habilitado, esa carpeta no existe — y CryptoAPI devuelve el mismo error genérico "The system cannot find the file specified", aunque el .p12 esté presente y bien ubicado.

**3er hallazgo (mismo día)**: el fix con `X509KeyStorageFlags.EphemeralKeySet` **tampoco** resolvió el problema (mismo error, reintentado por el cliente). El cliente aportó el dato decisivo: `delicias-naturales` — sistema hermano que factura contra AFIP producción de verdad, en **este mismo servidor** — sirvió de referencia real ya probada. Revisando su código (`Models/Afip/LoginTicket.cs`, `CertificadosX509Lib.ObtieneCertificadoDesdeArchivo`, proyecto .NET Framework 4.7.2 ya en producción) confirmó que usa `X509KeyStorageFlags.MachineKeySet`, no `Ephemeral`. Fix final: se cambia a `MachineKeySet` — la clave privada se guarda en el almacén de certificados de la máquina (no del perfil de usuario), evitando la misma dependencia sin necesitar que el Application Pool cargue un perfil, con la garantía adicional de ser el flag que **ya funciona de verdad en este servidor** para otro sistema.

**Impacto en capas**: Infrastructure (`AfipService.cs`). Sin migración EF, sin script de corrección de datos.

## CR-50 — Cheques de compra: fecha de emisión futura permitida + nota interna editable en cualquier estado

Pedido explícito del cliente (19/08/2026), 2 puntos en el mismo mensaje, en respuesta directa a CR-49:

**CA-CR50.1**: "Cheques con fecha de emisión futura también tienen que estar contemplados." Simétrico a CR-49 (que sacó el piso de fecha de vencimiento): se saca también el techo "no puede ser futura" de la fecha de emisión — tanto el `max=hoy` del datepicker (`OrdenesCompra/Details.cshtml`, `.inp-cheque-emision`) como la validación server-side equivalente en `PagoOrdenCompraService.RegistrarPagoAsync` (que además estaba catalogada como fix de bug en `docs/qa/regresiones-manuales.yml`, MH-003 — marcada ahí como `superseded_por` este CR, no una regresión). Permite cargar un cheque diferido con fecha de emisión futura (todavía no entregado, pero ya conocido de antemano). Se mantiene la única validación que sigue teniendo sentido pase lo que pase: emisión nunca posterior a vencimiento.

**CA-CR50.2**: "Las compras también deben tener un campo nota para cargar comentarios." Investigación: `OrdenCompra.NotaInterna` ya existía desde CR-27, pero solo era editable a través del formulario de Crear/Editar (`OrdenCompraService.UpdateAsync`), que a su vez solo funciona mientras la OC está en Borrador (`EstadosEditables`) — una vez Confirmada/Recibida/Cancelada, no había forma de cargar o corregir la nota. Nuevo método `IOrdenCompraService.ActualizarNotaInternaAsync(id, nota)`, independiente de la máquina de estados de la OC (a diferencia de Items/Proveedor/Comprobante/Impuestos, la nota es solo un comentario libre que nunca afecta stock ni Cuenta Corriente, así que no tiene sentido bloquearla junto con el resto). En `OrdenesCompra/Details.cshtml` (visible en cualquier estado, a diferencia de la pantalla de Editar) la nota pasa de mostrarse solo si no está vacía a ser siempre un campo editable con botón "Guardar nota" — acción propia (`ActualizarNotaInterna`), independiente del botón "Editar".

**Impacto en capas**: Application (`IOrdenCompraService.ActualizarNotaInternaAsync` nuevo), Infrastructure (`PagoOrdenCompraService.cs`, `OrdenCompraService.cs`), Web (`OrdenesCompraController.cs`, `OrdenesCompra/Details.cshtml`). Sin migración EF.

## CR-49 — Cheques de compra: fecha de vencimiento pasada permitida (cargar cheques ya vencidos)

Pedido explícito del cliente (19/08/2026): "al cargar los cheques, el usuario quiere poder seleccionar fechas anteriores dentro del datepicker, para poder cargar cheques ya emitidos días antes."

**Investigación**: la fecha de emisión del cheque (`inp-cheque-emision`) ya permitía cualquier fecha pasada (solo tenía `max=hoy`, tanto en el cliente como revalidado en el server). El bloqueo real estaba en la **fecha de vencimiento**: `PagoOrdenCompraService.RegistrarPagoAsync` rechazaba con "La fecha de vencimiento del cheque no puede ser anterior a hoy" — y el datepicker del cliente tenía `min=hoy`. Esto impedía cargar un cheque real emitido hace tiempo cuyo plazo de 30/60/90 días ya se cumplió (un cheque vencido pero todavía no acreditado es, desde CR-46, un estado perfectamente válido: sigue `Pendiente` hasta que se acredita, sin importar si ya pasó su fecha de vencimiento).

**Fix**: se saca el piso de "no anterior a hoy" tanto del datepicker (`OrdenesCompra/Details.cshtml`, ya no tiene `min`) como de la validación server-side (`PagoOrdenCompraService.RegistrarPagoAsync`) — se mantienen las otras 2 validaciones intactas (emisión nunca posterior a vencimiento, emisión nunca futura). Sin migración EF (cambio de validación puro).

## CR-48 — Precio de lista editable en Producto (dejó de ser calculado)

Pedido explícito del cliente (19/08/2026), corrigiendo el texto "(calculado automático, +21%)" que se mostraba junto a Precio de lista en `Productos/Create.cshtml`/`Edit.cshtml`: quiere poder editarlo directamente en la ficha del producto, no que dependa siempre y exclusivamente de Precio efectivo ×1,21.

**Decisión de implementación**: `Producto.PrecioLista` era `[NotMapped]` (propiedad calculada, `PrecioEfectivo × 1,21` vía `PorcentajeHelper.AplicarRecargo`, documentada explícitamente en CR-21 como "nunca un campo propio editable"). Pasa a ser una columna real editable — mismo patrón "sugerido pero editable" ya usado por `VentaItem.PrecioTarjeta` (CR-37/38): la UI sigue sugiriendo `PrecioEfectivo × 1,21` en vivo, pero el valor que se guarda es el que quede en el campo.

- **Alta de producto** (`Create.cshtml`): el campo se autocompleta con la sugerencia mientras el usuario no lo haya tocado a mano — apenas lo edita, deja de autocompletarse.
- **Edición de producto** (`Edit.cshtml`): el campo arranca con el valor ya guardado (nunca se pisa solo, para no perder un ajuste manual previo) — se muestra la sugerencia al lado con un link "usar sugerido" para copiarla si el usuario lo pide.
- **Aumento masivo de precios (M16)**: sigue ajustando únicamente `PrecioEfectivo` — `PrecioLista` **ya no lo sigue automáticamente**, queda tal como esté configurado por producto (consecuencia directa de que ahora es un valor independiente; si el aumento masivo también lo recalculara solo, dejaría de ser realmente editable).

**Impacto en capas**: Domain (`Producto.PrecioLista` deja de ser `[NotMapped]`), Infrastructure (`AppDbContext` — precisión de columna, `ProductoService.CreateAsync`/`UpdateAsync`/`ListarAsync`), Application (`ProductoInput.PrecioLista` nuevo), Web (`ProductoFormViewModel`, `ProductosController`, `Productos/Create.cshtml`/`Edit.cshtml`). **1 migración EF** (`AddPrecioListaColumn`) con backfill `PrecioEfectivo × 1,21` para los productos existentes — verificada contra `marihogar_dev` (221 productos, 0 diferencias contra el valor que se calculaba antes) antes de aplicar en producción.

## CR-46 — Producto: % descuento/recargo opcionales + Cheque de compra no cuenta como pagado hasta acreditarse

Pedido explícito del cliente (19/08/2026), 2 reportes en el mismo mensaje:

**CA-CR46.1 (Producto)**: "al crear y editar producto: % de descuento % de recargo deben ser campos opcionales." `ProductoFormViewModel.PorcentajeDescuento`/`PorcentajeRecargo` eran `decimal` no-nullable — ASP.NET Core exige un valor aunque no tengan `[Required]` explícito (un `decimal` no-nullable no admite bindear un campo vacío). Cambiados a `decimal?`; el controller (`ProductosController.MapInput`) coalesce a 0 antes de pasar al Service (mismo comportamiento final que si el usuario hubiera tipeado 0 — sin cambio de esquema ni de Domain).

**CA-CR46.2 (Cheque de compra)**: "se agregan pagos de tipo cheque a 30 días y el estado del pago de la compra es Pagado, no debería ser estado pendiente? [...] total saldo pendiente es 0 pero el cliente no pagó nada todavía" — reportado sobre OC #30 en producción. Investigación confirmó: el Estado Pendiente/Pagado de CR-44 dependía únicamente del campo "fecha tentativa de pago", que nadie completa en un pago con Cheque (ya tiene su propia fecha de vencimiento) — el pago quedaba `Pagado` y el `MovimientoCCProveedor.Pago` se posteaba de inmediato al entregar el cheque, sin importar si el banco ya lo había cobrado (diseño original de CR-7).

**Decisión confirmada con el cliente** (`AskUserQuestion`, opción recomendada elegida): un pago con Cheque a proveedor ahora **siempre** arranca `Estado=Pendiente` (independiente de la fecha tentativa, que ya no aplica a Cheque) y el `Pago` real en la Cuenta Corriente del proveedor recién se postea cuando el Administrador marca el cheque como **Acreditado** en la pantalla de Cheques (`ChequeService.AcreditarAsync`, ya existía como acción manual desde CR-7) — con `Fecha = Cheque.FechaVencimiento` (cuándo realmente salió el dinero, no el momento del click), mismo criterio que `ConfirmarPagoAsync` (CA-CR44.4). `ChequeService.RechazarAsync` deja de postear el contramovimiento de reversión que tenía: un cheque solo se puede rechazar desde Pendiente, y bajo el nuevo diseño un cheque Pendiente nunca llegó a postear el Pago real, así que no hay nada que revertir. El botón "Confirmar pago" genérico de `OrdenesCompra/Details.cshtml` se oculta para pagos con Cheque (con guard también server-side en `ConfirmarPagoAsync`) — un cheque se confirma exclusivamente acreditándolo.

**Bug de consistencia encontrado y corregido en el mismo paso**: `ProyeccionFinancieraDto.GastosComprometidos` sumaba `ChequesPorVencer + SaldoPendienteOrdenesCompra` — antes de CR-46 esto era seguro porque un cheque nunca quedaba en el saldo pendiente de la OC (se pagaba al entregarlo), pero ahora un cheque no acreditado queda en AMBOS lados (su OC lo cuenta en `SaldoPendienteOrdenesCompra` Y la consulta de cheques lo vuelve a contar en `ChequesPorVencer`), duplicando el monto. Corregido: `GastosComprometidos` pasa a ser solo `SaldoPendienteOrdenesCompra` (ya incluye los cheques no acreditados); `ChequesPorVencer` se mantiene como dato informativo (mismo criterio que `PagosCompraProgramados`/`PagosVentaPorAcreditar`), mostrando cuánto de ese saldo son cheques con vencimiento dentro del horizonte.

**Corrección retroactiva en producción** (confirmada con el cliente): 6 pagos con cheque ya cargados (OC #16, #20 ×3, #30 ×2 — proveedores Cardozo y Espumas Pilar SRL, cheques con vencimiento entre 28/08 y 12/10/2026, todos con `Cheque.Estado=Pendiente`) tenían el `Pago` real ya posteado. Corregidos con un script dedicado (dry-run primero, verificado, luego aplicado): cada uno vuelve a `Estado=Pendiente` y se postea un `Cargo` de reversión por el mismo importe (nunca se borra el movimiento original, mismo criterio ya usado por `MovimientoCCProveedor`) — el saldo pendiente de esas 3 órdenes de compra vuelve a reflejar la realidad.

**Impacto en capas**: Web (`ProductoFormViewModel`, `ProductosController.MapInput`, `OrdenesCompra/Details.cshtml`, `Cheques/Index.cshtml`, `ProyeccionFinanciera/Index.cshtml`), Application (`IChequeService` doc, `ProyeccionFinancieraDto.GastosComprometidos`), Infrastructure (`PagoOrdenCompraService.RegistrarPagoAsync`/`ConfirmarPagoAsync`, `ChequeService.AcreditarAsync`/`RechazarAsync`, `ProyeccionFinancieraService`). Sin migración EF (sin cambio de esquema). Corrección de datos en producción vía script dedicado, con backup previo y verificación posterior.

## CR-44 — Pagos de Orden de Compra programables con fecha tentativa + notificación de vencimiento

Pedido explícito del cliente vía `/agentes-ia-orquestador` (19/08/2026): "todos los métodos de pago de las compras deben tener una fecha tentativa de pago, donde el usuario puede cargar el pago para días próximos, y que cuando ingrese al sistema ese día, se informe a través de una notificación que tiene pagos por vencer el día de la fecha."

**Decisión de diseño confirmada con el cliente antes de implementar** (`AskUserQuestion`): al investigar el código existente se encontró que, hoy, un `PagoOrdenCompra` (cualquier método, incluido Cheque) impacta la Cuenta Corriente del proveedor **apenas se carga**, sin importar la fecha — el pedido del cliente habla de "pagos por vencer", que sugiere una obligación todavía no saldada. Se preguntó explícitamente si programar un pago debía descontar el saldo del proveedor ya mismo o recién al confirmarse — el cliente eligió **recién cuando se confirma**. Esto define el diseño: no es simplemente hacer editable `PagoOrdenCompra.Fecha` (como CR-29 hizo en Ventas), sino un estado propio con confirmación manual — mismo patrón arquitectónico ya usado por `Cheque` (Pendiente→Acreditado) y por `PagoVenta` con Tarjeta de crédito (CR-34, `EstadoAcreditacionPago` Pendiente→Acreditado, CC posteada recién al confirmar).

**CA-CR44.1**: `PagoOrdenCompra` gana `Estado` (`EstadoPagoOrdenCompra`: Pendiente=1/Pagado=2, default Pagado — no rompe los ~330 pagos históricos, todos pagos reales ya hechos), `FechaPagoTentativa` (nullable, obligatoria solo si Estado=Pendiente) y `Notificado` (bool, mismo patrón que `Cheque.Notificado`).

**CA-CR44.2**: al registrar un pago (`PagoOrdenCompraService.RegistrarPagoAsync`), una línea con `FechaPagoTentativa` estrictamente futura (comparada contra la fecha real de Argentina, `HorarioArgentino.Ahora`) queda `Estado=Pendiente` y **NO** postea el movimiento de `MovimientoCCProveedor` — el `Cheque` (si el método es Cheque) sí se crea igual en ese momento, con todos sus datos, porque es un documento físico ya decidido, independiente de si la CC ya lo contabiliza. Sin fecha, o con una fecha de hoy/pasada, el pago se registra exactamente igual que siempre (Estado=Pagado, CC posteada de inmediato) — comportamiento histórico intacto.

**CA-CR44.3**: `OrdenCompraDetailDto.MontoPagado`/`SaldoPendiente` excluyen los pagos `Estado=Pendiente` (además del criterio ya existente de excluir Cheque Rechazado) — el saldo que le debés al proveedor no baja hasta que el pago programado se confirme de verdad, consistente con la decisión del cliente.

**CA-CR44.4**: nuevo `IPagoOrdenCompraService.ConfirmarPagoAsync` (Administrador-only, mismo criterio que `Cheque.AcreditarAsync`/`Venta.AcreditarPagoAsync`) — recién ahí se postea el `MovimientoCCProveedor.Pago` real, con `Fecha = FechaPagoTentativa` (no el momento en que el Administrador confirma), mismo criterio que `CA-CR34.2`.

**CA-CR44.5**: nuevo job diario `PagoOrdenCompraVencimientoHostedService` (patrón idéntico a `ChequeAcreditacionHostedService`/`PagoVentaAcreditacionHostedService`, corrida a las 03:10 ART — 5 min después del de Ventas, para no competir por el mismo instante) que **solo notifica**, nunca cambia `Estado` — busca pagos `Pendiente` con `FechaPagoTentativa <= hoy` sin notificar todavía, marca `Notificado=true` y dispara una notificación in-app por pago a SuperUsuario + Administrador, con link directo a la Orden de Compra. Se mantiene como job separado de los otros 2 a propósito (mismo razonamiento ya documentado en `PagoVentaAcreditacionHostedService`: son 3 dominios distintos que conviene no acoplar).

**Impacto en capas**: Domain (`EstadoPagoOrdenCompra` nuevo, `PagoOrdenCompra` +3 propiedades), Application (`ICCProveedorService`/`IPagoOrdenCompraService` ampliados, `PagoOrdenCompraVencidoDto` nuevo), Infrastructure (`CCProveedorService`, `PagoOrdenCompraService`, `PagoOrdenCompraVencimientoHostedService` nuevo, `DependencyInjection.cs`), Web (`OrdenesCompraController` +1 acción, `OrdenesCompra/Details.cshtml` — fecha tentativa por línea de pago, badge Pendiente/Pagado + botón "Confirmar pago" en el historial). 1 migración EF (`AddPagoOrdenCompraFechaTentativa` — 3 columnas, `Estado` con default explícito a nivel de columna, verificada contra `marihogar_dev`: los 333 pagos existentes quedaron `Pagado` sin script de datos aparte).

**CA-CR44.6** (agregado el mismo día, pedido del cliente): `ProyeccionFinancieraService` gana `PagosCompraProgramados`/`PagosCompraProgramadosCantidad` — dato informativo, mismo criterio ya establecido por `PagosVentaPorAcreditar` (CR-29/34): **no** se suma a `GastosComprometidos`/`TieneDeficit`. Motivo explícito: ese monto ya está completo en `SaldoPendienteOrdenesCompra` (la OC sigue "debiendo" ese pago hasta que se confirme de verdad) — sumarlo aparte lo hubiera contado dos veces. **Bug de consistencia encontrado en el mismo paso**: el cálculo de `SaldoPendienteOrdenesCompra` (`ocsConSaldo` en `ProyeccionFinancieraService`) tenía su propia copia del criterio de exclusión de `OrdenCompraDetailDto.MontoPagado` (excluye Cheque Rechazado) pero **no** había sido actualizada con la exclusión nueva de `Estado=Pendiente` de CA-CR44.3 — corregido para que ambos cálculos nunca diverjan.

## CR-45 — Fecha de compra editable + fecha de recepción de mercadería

Pedido explícito del cliente, en paralelo al deploy de CR-44 (19/08/2026): "se solicita poder editar la fecha de la compra, o que se permitan cargar compras con fecha pasada. que sea fecha de compra y fecha de recepción de mercadería."

`OrdenCompra.Fecha` y `OrdenCompra.FechaRecepcion` ya existían en el modelo (cargados en producción desde el sprint original) pero ambos estaban hardcodeados a `DateTime.UtcNow` en el Service — sin campo de UI ni parámetro para elegirlos. No hizo falta migración EF, solo dejar de hardcodear ambos valores.

**CA-CR45.1**: `OrdenCompraInput` gana `Fecha` (nullable, solo día calendario) — mismo patrón ya usado por `VentaInput.Fecha` (CR-42): se combina el día elegido con la hora actual de Argentina y se convierte a UTC real vía `HorarioArgentino.ConvertirAUtc`. A diferencia de Venta, acá se permite explícitamente cualquier fecha pasada (es el pedido literal del cliente — "cargar compras con fecha pasada"), pero nunca futura. Sin fecha explícita, cae al comportamiento histórico (ahora mismo). Editable tanto al crear como al editar (mientras la OC sigue en Borrador, mismo guard `EstadosEditables` ya existente). Como el `OrdenesCompraController` completo ya exige la policy `RequireAdministracion` a nivel de clase, no hizo falta ningún gating adicional de rol (a diferencia de CR-42 en Ventas, donde sí hubo que distinguir Administrador de Vendedor).

**CA-CR45.2**: `IOrdenCompraService.RecibirAsync` gana un parámetro opcional `fechaRecepcion` (mismo criterio de validación: nunca futura). Al marcar una OC como Recibida, la fecha elegida se cascadea de forma consistente a `OrdenCompra.FechaRecepcion`, al movimiento de stock de cada línea (`IStockService.RegistrarMovimientoAsync`, que ya tenía el parámetro opcional `fecha` desde CR-42) y al Cargo posteado en la Cuenta Corriente del proveedor (`ICCProveedorService.RegistrarMovimientoAsync`, que ya tenía el parámetro opcional `fecha` desde CR-44) — para que una recepción backdateada no quede con fecha de hoy en el stock/CC y la fecha real solo en la OC (mismo criterio de consistencia ya aplicado en CR-42 sobre Ventas). En la UI (`OrdenesCompra/Details.cshtml`), el botón "Marcar recibida" pasó de un simple confirm a un SweetAlert2 con selector de fecha (vacío = hoy), mismo patrón visual ya usado por "Cancelar orden de compra" (motivo obligatorio).

**Impacto en capas**: Application (`OrdenCompraInput.Fecha` nuevo, `IOrdenCompraService.RecibirAsync` con parámetro opcional nuevo), Infrastructure (`OrdenCompraService.CreateAsync`/`UpdateAsync`/`RecibirAsync`, helper privado `CalcularFecha` compartido), Web (`OrdenCompraFormViewModel.Fecha`, `OrdenesCompraController.MapInput`/`Edit` GET/`Recibir`, `OrdenesCompra/Create.cshtml` — input de fecha junto al selector de Proveedor, `OrdenesCompra/Details.cshtml` — SweetAlert de fecha en "Marcar recibida"). **Sin migración EF** (ambas columnas ya existían en el esquema desde el sprint original, solo se dejó de hardcodear `DateTime.UtcNow`).

## Historial de ajustes
- 2026-10-02: CR-86 — **el backfill de fechas (punto 9) sale del alcance por decision del cliente** ("dejar los datos de los cheques en produccion como estan, estan cargados por el usuario"). **CA-86.8 pasa a NO APLICA al historico**: los 3 cheques que cruzan de mes ($1.452.133,30) quedan asi, como estado conocido y aceptado. El backfill **del impuesto** (CA-86.17, $39.719,67) **si se mantiene** y hubo que desacoplarlo del reasiento, porque el posteo del impuesto vivia detras del `continue` de los cheques omitidos. De CR-85 queda entregado el camino en vivo, no la correccion retroactiva.
- 2026-10-02: CR-86 — **CA-86.5 ratificado en 723** (el 730 original incluia 6 pagos dados de baja), **CA-86.8 reenunciado en 3 cheques / $1.452.133,30** (el enunciado viejo media caja-vs-proveedor cuando el backfill mide proveedor-vs-acreditacion, y perdia el pago 339), **CA-86.11 reenunciado** ("a lo sumo un gasto vigente"; el viejo contradecia PAT-020) y **CA-86.14 corregido a $41.522,56** (redondeaba el total una vez en vez de por cheque). Los cuatro eran defectos de criterio, no de implementacion; causa comun: derivar el numero en SQL crudo sin replicar los filtros globales de EF, la exclusion de ventas canceladas ni el redondeo por fila. Detalle de cada uno en `trazabilidad.md`.
- 2026-10-02: CR-86 — **CA-86.13 reenunciado y CA-86.17 agregado** por la decision del cliente de fijar `VigenteDesde` = 01/09/2026 (septiembre tambien se postea: 19 cheques, $39.719,67).
- 2026-10-02: CR-86 — **CA-86.18 y RN-86.5 agregados** al resolver MH-053: un pago con neto 0 en el ledger no se ofrece para correccion de fecha.
- 2026-10-02: CR-86 — se retiro el punto 17 del alcance y el riesgo R-CR86.7 (el gasto de $617.687 del 28/09 **no** era un error: compra en conjunto con un tercero, procedimiento de CR-81, verificado contra la base).
- 2026-10-02: **CR-87 levantado** con el hallazgo de que el aviso de doble conteo de CR-83 ve 1 de 121 gastos.

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **historico** — 3 bloques → [`1-analista-funcional-historico-2.md`](historial/1-analista-funcional-historico-2.md)


### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **historico** — 1 bloques → [`1-analista-funcional-historico.md`](historial/1-analista-funcional-historico.md)

- 2026-09-23 — CR-78: ver sección "CR-78" más arriba. La vista de Venta bloqueaba la cancelación tras anular la factura con una NC porque miraba el último comprobante (la NC) en vez del criterio real del guard. Nuevo `VentaDetailDto.TieneFacturaVigente` resuelto con el mismo método del servicio. Sin migración EF.
- 2026-09-23 — CR-77: ver sección completa "CR-77 — Nota de Crédito: elegir si se corrige la factura o se anula la venta" más arriba. Al generar la NC el usuario elige entre "Corregir la factura" (default, comportamiento CR-55 intacto) y "Anular la venta", que encadena `VentaService.CancelarAsync`. Orquestado en el controller para no cerrar un ciclo de DI con VentaService. Dos transacciones separadas a propósito (la NC en AFIP es irreversible). Guards de cancelación sin tocar. Solo Web, sin migración EF.
- 2026-09-03 — CR-76: ver sección completa "CR-76 — Quitar el filtro 'Vendedor' del listado de Ventas" más arriba. Se retira end-to-end (no solo el control: también `VentaFiltro.VendedorId`, porque persiste en sesión y habría seguido filtrando invisible) más el combo ya sin consumidores. La columna Vendedor se mantiene — desvío consciente de PAT-008, a pedido del cliente. Sin migración EF.
- 2026-09-03 — CR-75: ver sección completa "CR-75 — Control de ventas con pagos todavía no acreditados" más arriba. Nueva línea "Sin acreditar" en el Resumen del detalle + checkbox "Solo ventas con pagos pendientes de acreditación" y badge en el listado. NO cambia Estado ni Saldo pendiente (se descartó explícitamente con el cliente: rompería remito y facturación AFIP). Sin migración EF.
- 2026-09-03 — CR-74: ver sección completa "CR-74 — Tarjeta de crédito: agregar la opción '1 pago'" más arriba. Se suma 1 al conjunto de cuotas válidas (server y cliente) y a la semilla de Configuración > Cuotas de tarjeta (5 filas fijas: 1/3/6/9/12), mostrado como "1 pago" en todas las pantallas. Sin migración EF — la fila la siembra SeedData al iniciar.
- 2026-09-03 — CR-73: ver sección completa "CR-73 — 'Pagos con tarjeta' pasa a llamarse 'Ingresos'" más arriba. Cierra la decisión abierta que CR-71 había dejado pendiente. Solo label de menú + título de pantalla; URL, controller, servicio y DTOs sin renombrar. Ícono del menú cambiado de tarjeta a uno de ingresos. Sin migración EF.
- 2026-09-03 — CR-72: ver sección completa "CR-72 — Renombres en Gastos/Gasto recurrente + reorden visual de Gastos/Create" más arriba. "Gestionar plantillas de gasto recurrente" → "Nuevo gasto recurrente" (mismo destino); "Cargar desde plantilla" → "Seleccionar gasto recurrente"; `Gastos/Create` reordenado en 3 cards (Seleccionar gasto recurrente / Datos del gasto / Formas de pago) sin tocar ids ni JS. Solo Web, sin migración EF.
- 2026-09-03 — CR-71: ver sección completa "CR-71 — 'Pagos con tarjeta' pasa a listar todos los pagos de ventas" más arriba. Se retira el filtro fijo por Tarjeta de crédito de CR-59; la pantalla suma filtro y columna "Forma de pago" y "solo pendientes" queda cubierto por el filtro de Estado ya existente. Solo pagos de Ventas (pagos a proveedores fuera de alcance, confirmado con el cliente). Sin renombrar controller/ruta/menú. Sin migración EF.
- 2026-09-02 — CR-70: ver sección completa "CR-70 — Gasto con varias líneas de pago" más arriba. `GastoPago` nueva entidad (mismo patrón que PagoVenta/PagoOrdenCompra), `Gasto.FormaPago` retirado. Migración con backfill (cada Gasto existente pasa a tener 1 línea idéntica a como estaba). Un solo movimiento de Egreso por gasto (sin cambios respecto de hoy). **Implementado y deployado a producción** — cliente pidió saltear el gate de presupuesto explícitamente; migración aplicada contra producción con backup previo de `Gastos` y backfill verificado (503/503 filas, montos idénticos).
- 2026-09-02 — CR-69: ver sección completa "CR-69 — Edición inline (on-demand, AJAX) de la nota de un pago desde Ventas/Details" más arriba. Click-to-edit sobre la nota de cada pago, guarda solo al perder el foco, sin recargar la pantalla. Sin migración EF (reutiliza `PagoVenta.Nota` de CR-68). Deployado.
- 2026-09-02 — CR-68: ver sección completa "CR-68 — Nota opcional al registrar un pago de Venta" más arriba. `PagoVenta.Nota` (texto libre, nunca en comprobantes), disponible al confirmar la Venta y al registrar un pago posterior. 1 migración EF sin backfill. Deployado.
- 2026-09-02 — CR-67: ver sección completa "CR-67 — Ventas/Compras/pagos cancelados ocultos de informes por defecto + integridad de Cuenta Corriente de Proveedores al cancelar OC" más arriba. Cierra los 3 gaps de la auditoría de infraestructura del mismo día (contramovimiento faltante, cheque acreditable sobre OC cancelada, jobs sin filtrar). Ventas/OC canceladas ocultas por defecto de los listados (filtro explícito para verlas); movimientos de CC Local/Proveedores de origen cancelado ocultos del ledger (checkbox "Mostrar cancelados"). QA encontró MH-019 (Dashboard/Proyección Financiera no excluían cheques de OC cancelada) — corregido antes de deploy. Sin migración EF.
- 2026-09-02 — CR-66: ver sección completa "CR-66 — Fix: 'Saldo actual del período filtrado' daba números sin sentido de negocio..." más arriba. El -$90M de agosto era matemáticamente correcto (arrastraba el Ajuste de apertura de $96,98M posteado el 10/08) pero semánticamente sin sentido — `ObtenerSaldoFiltradoAsync` pasa de sumar dentro de la ventana a calcular el saldo real acumulado hasta `FechaHasta`, ignorando `Tipo`/`FechaDesde`. Sin migración EF.
- 2026-09-02 — CR-65: ver sección completa "CR-65 — Fix: cancelar una Venta con pago pendiente reversaba dinero que nunca entró a Caja" más arriba. Mismo caso que CR-64 (Venta #694). `CancelarAsync` reversaba `venta.Total` completo sin importar cuánto se posteó realmente — corregido a sumar solo los pagos no-Pendiente. Corrección de datos: contramovimiento de Ingreso $318.999,56 para neutralizar el Egreso erróneo #1201, sin editar el ledger. Sin migración EF.
- 2026-09-02 — CR-64: ver sección completa "CR-64 — Fix: cancelar una Venta con pago pendiente dejaba un pago 'colgado' que revertía la cancelación" más arriba. Reporte directo sobre Venta #694. Fix en `CancelarAsync` (soft-delete de pagos Pendiente al cancelar) + `EliminarPagoAsync` (guard: no tocar Estado si la Venta ya es Cancelada). Corrección de datos aplicada sobre Venta #694 en producción. Sin migración EF.
- 2026-09-02 — CR-63: ver sección completa "CR-63 — Fix: la fecha de acreditación manual no se actualizaba a la fecha real de la acción" más arriba. Reporte directo del cliente sobre Venta #687/#681. Fix en `VentaService.AcreditarPagoAsync` y `PagoOrdenCompraService.ConfirmarPagoAsync` (mismo defecto en Compras, corregido en el mismo paso). Sin migración EF. Deployado. Investigación vía AuditLog encontró 5 filas históricas con discrepancia real confirmable (incluidas las 2 citadas) — pendiente confirmación del cliente antes de corregirlas retroactivamente.
- 2026-08-31 — CR-62 (Discovery + Análisis + Diseño + Arquitectura + Presupuesto, gate pendiente): ver sección completa "CR-62 — Gastos (categoría/forma de pago/recurrentes) + Cuenta Corriente Local (usuario/origen clickeable/saldo filtrado)" más arriba. 6 puntos: categoría Comisiones bancarias, forma de pago Débito automático, plantillas de gasto recurrente (solo prellenan el formulario, sin crear ni recordar automáticamente — confirmado con el cliente), nombre de usuario resuelto en CC Local (antes GUID crudo), Origen clickeable (Venta/Gasto), filtro de mes actual por defecto + saldo filtrado por búsqueda. 2 migraciones EF. Presupuesto: ítem único, PERT 7.53h, horas finales 9.0h (riesgo Medio-Alto, contingencia 20%), **USD 118**. Pendiente aprobación explícita del cliente sobre el presupuesto antes de Implementación.
- 2026-08-27 — CR-61 (Discovery + Análisis + Diseño + Arquitectura + Presupuesto, gate pendiente): ver sección completa "CR-61 — Stock: listado de productos con edición inline reemplaza Ajuste manual" más arriba. Reemplaza `Stock/Index` (listado de movimientos) por un listado de productos con Stock editable inline (reemplaza el valor, no delta), guardado por fila al instante, sin motivo pedido al usuario (el ledger igual queda con motivo fijo generado por el sistema). Retira `Ajuste manual` (código incluido); Movimientos pasa a `Stock/Movimientos`, link secundario. Sin migración EF. Presupuesto: ítem único, PERT 6.45h, horas finales 7.4h (riesgo Medio, contingencia 15%), **USD 101**. Pendiente aprobación explícita del cliente sobre el presupuesto antes de Implementación.
- 2026-08-27 — CR-60: ver sección completa "CR-60 — Cheques de compra: plazo de días editable a mano" más arriba. El `<select>` fijo de 30/60/90 días pasa a un número libre — el autocálculo de vencimiento y el modelo ya lo soportaban sin cambios. Sin migración EF.
- 2026-08-27 — CR-59 (Diseño + Arquitectura + Presupuesto, gate pendiente): ver sección completa "CR-59 — Pagos con tarjeta de crédito a liquidar" más arriba. Pedido vía orquestador, planteado como pregunta abierta sobre dónde ubicar el listado — resuelto con pantalla dedicada (clon de Cheques) + card de Dashboard. Sin migración EF. Presupuesto: ítem único, PERT 2.37h, horas finales 2.6h (riesgo Bajo, contingencia 10%), **USD 37**. Pendiente aprobación explícita del cliente sobre el presupuesto antes de Implementación.
- 2026-08-26 — CR-58: ver sección completa "CR-58 — Órdenes de compra: tag de facturación + Dashboard 'vista CEO' (4 métricas nuevas)" más arriba. Tag de OC facturadas/no facturadas (Index + Dashboard). 4 métricas CEO confirmadas por el cliente vía 2 `AskUserQuestion`: Deuda total a proveedores, Margen bruto del período (costo al precio de compra actual, limitación aceptada), Gastos operativos del período, Ticket promedio de venta. Sin migración EF.
- 2026-08-21 — CR-57: ver sección completa "CR-57 — Método de pago 'Tarjeta de débito' en Ventas y Compras" más arriba. `MetodoPago.TarjetaDebito=8`, habilitado en Ventas y Compras (no en Entregas). 2 decisiones confirmadas: cobra precio Efectivo (no transferencia) y se acredita al instante (no acreditación diferida como Tarjeta de Crédito) — se logra sin lógica nueva, solo agregándolo a las listas de métodos permitidos sin sumarlo a `metodosRequierenConIva` ni a ningún chequeo `== TarjetaCredito`. Sin migración EF.
- 2026-08-21 — CR-56: ver sección completa "CR-56 — Venta con Factura anulada por Nota de Crédito ya no bloquea Cancelar (MH-013)" más arriba. El cliente preguntó por el proceso correcto para eliminar una venta con Factura+NC y encontramos que hoy bloqueaba — corregido en 5 archivos (mismo criterio: Factura vigente sin NC asociada). Cierra MH-013. Sin migración EF.
- 2026-08-21 — CR-55 (Discovery + Análisis): ver sección completa "CR-55 — Nota de Crédito para anular una Factura AFIP emitida por error" más arriba. Pedido explícito del cliente vía orquestador. 3 decisiones confirmadas: NC siempre total (no parcial), reabre `CantidadFacturada` para refacturar, mismo acceso que Facturar (Administrador + Vendedor). Pendiente: Diseño, Arquitectura y Presupuesto (gate cliente) antes de implementar.
- 2026-08-20 — CR-52: ver sección completa "CR-52 — Bug crítico: AFIP no podía emitir ningún comprobante real" más arriba. Resumen: `AfipService` resolvía el certificado .p12 con una ruta relativa dependiente del directorio de trabajo del proceso — corregido para resolver siempre contra `IWebHostEnvironment.ContentRootPath`. Comprobante #304 queda reintentable sin corrección de datos. Sin migración EF.
- 2026-08-19 — CR-51: ver sección completa "CR-51" en "Modelo de precios" más arriba. Resumen: renombre "Precio de lista" → "Precio transferencia" en todo el proyecto (Producto, Ventas), y eliminación del autocompletado/sugerencia "+21%" que CR-48 había agregado — el campo se completa siempre a mano. Sin migración EF.
- 2026-08-19 — CR-50: ver sección completa "CR-50 — Cheques de compra: fecha de emisión futura permitida + nota interna editable en cualquier estado" más arriba. Resumen: se saca el techo "no puede ser futura" de la fecha de emisión del cheque (simétrico a CR-49), y `OrdenCompra.NotaInterna` gana una acción propia (`ActualizarNotaInterna`) que la hace editable sin importar el estado de la OC, no solo en Borrador. Sin migración EF.
- 2026-08-19 — CR-49: ver sección completa "CR-49 — Cheques de compra: fecha de vencimiento pasada permitida" más arriba. Resumen: se saca el piso "vencimiento no puede ser anterior a hoy" (datepicker + validación server) para poder cargar cheques ya emitidos que vencieron hace días — estado válido desde CR-46 (sigue Pendiente hasta acreditarse). También se investigó y confirmó de paso que `OrdenCompra.NotaInterna` ya existe desde CR-27 (campo colapsable "+ Agregar nota interna" en `Create.cshtml`/`Edit.cshtml`) — el cliente pidió lo mismo sin saber que ya estaba, no hizo falta ningún cambio de código para eso. Sin migración EF.
- 2026-08-19 — CR-48: ver sección completa "CR-48 — Precio de lista editable en Producto (dejó de ser calculado)" más arriba. Resumen: `Producto.PrecioLista` dejó de ser `[NotMapped]`/calculado — ahora es una columna real editable, con la sugerencia `PrecioEfectivo×1,21` precargada en la UI (Create autocompleta hasta que se toca a mano, Edit nunca pisa el valor guardado, solo sugiere). Aumento masivo de precios ya no actualiza PrecioLista automáticamente. 1 migración EF con backfill, verificada contra `marihogar_dev` (221 productos, 0 diferencias).
- 2026-08-19 — CR-46: ver sección completa "CR-46 — Producto: % descuento/recargo opcionales + Cheque de compra no cuenta como pagado hasta acreditarse" más arriba. Resumen: % descuento/recargo de Producto ahora opcionales (nullable). Un pago con Cheque a proveedor ya no cuenta como pagado al entregarlo — recién cuenta cuando se acredita en la pantalla de Cheques (decisión confirmada con el cliente). Bug de doble conteo encontrado y corregido en Proyección Financiera (`ChequesPorVencer` ya no se suma aparte de `SaldoPendienteOrdenesCompra`). Corrección retroactiva de 6 pagos con cheque ya cargados en producción (OC #16/#20/#30), con backup previo y verificación posterior. Sin migración EF.
- 2026-08-19 — CR-45: ver sección completa "CR-45 — Fecha de compra editable + fecha de recepción de mercadería" más arriba. Resumen: `OrdenCompraInput.Fecha` (nunca futura, permite pasada) editable en Create/Edit; `RecibirAsync` gana `fechaRecepcion` opcional, cascadeado a stock y a la CC del proveedor. Sin migración EF (columnas ya existían, solo se dejó de hardcodear `DateTime.UtcNow`).
- 2026-08-19 — CR-44: ver sección completa "CR-44 — Pagos de Orden de Compra programables con fecha tentativa + notificación de vencimiento" más arriba en este mismo archivo. Resumen: pagos de OC ahora se pueden programar con una fecha tentativa futura (cualquier método) — decisión confirmada con el cliente de que un pago programado NO impacta la CC del proveedor hasta confirmarse manualmente, mismo patrón ya usado por Cheque/PagoVenta-Tarjeta. Nuevo job diario notifica cuando un pago programado vence. 1 migración EF, verificada contra `marihogar_dev` (333 pagos históricos sin cambio de comportamiento).
- 2026-08-19 — CR-43: pedido explícito del cliente ("generar un reporte de factura lo más parecido a las facturas que se cargaron hoy... usar datos oficiales de ARCA como fuente de verdad"), comparado directamente contra las 6 facturas reales descargadas de la página de AFIP (mismo CUIT). **Hallazgo crítico no relacionado con el diseño**: `Afip:PuntoVenta` en `appsettings.Production.json` estaba en `1`, pero las 6 facturas reales muestran Punto de Venta **4** — si el sistema llegara a emitir un comprobante real antes de este fix, habría numerado con un punto de venta que no es el que el cliente usa de verdad en AFIP. Corregido a `4`. `AfipSettings` gana 5 campos nuevos de solo-impresión (nunca se envían al webservice WSFE, que solo necesita CUIT/PuntoVenta): `RazonSocial`, `DomicilioComercial`, `CondicionIva`, `IngresosBrutos`, `FechaInicioActividades` — cargados con los datos reales tal como figuran en las facturas ("MARI MARCOS VALENTIN", domicilio real, "IVA Responsable Inscripto", "20-33113613-2", 01/09/2011). `ComprobanteAfipService.GenerarPdfAsync` rediseñado por completo para replicar el formato oficial (reemplaza el diseño de marca propia "MariHogar" del rediseño anterior): caja "ORIGINAL", letra de tipo + "COD. 00X" en un box central, bloque de emisor/numeración/CUIT/IIBB/inicio de actividades, bloque de cliente con Condición frente al IVA ("IVA Responsable Inscripto" si Factura A, "Consumidor Final" si B) y Condición de venta (derivada: "Contado" si todos los pagos son Efectivo, "Otra" en cualquier otro caso), tabla de ítems con las mismas 8 columnas del formulario oficial, y la leyenda "Régimen de Transparencia Fiscal al Consumidor (Ley 27.743)" + "IVA Contenido" (obligatoria en Factura B desde 2024, presente en las 6 facturas reales, no existía en el diseño anterior). Verificado generando un PDF real (ComprobanteAfip Id=298, Gasparín) y comparándolo visualmente contra el original — 1 bug encontrado y corregido en el propio proceso: el CUIT del emisor se imprimía con guiones (mal, copiado por error de otro campo) en vez de sin guiones como muestra la factura real.
- Datos de "Domicilio" del cliente (no del emisor) NO se agregaron — el sistema no captura ese dato hoy y no fue parte del pedido explícito (que hablaba de los datos del emisor: razón social/domicilio/CUIT/condición IVA propios). Si se necesita a futuro, es una ampliación de alcance nueva (nuevo campo en `ComprobanteAfip` + UI de carga).
- Motivo: Pedido explícito del cliente, con los datos oficiales de ARCA como fuente de verdad.
- Impacto en capas: Application (`AfipSettings.cs`), Infrastructure (`ComprobanteAfipService.GenerarPdfAsync`), configuración (`appsettings.json`, `appsettings.Production.json`). Sin migración EF (settings + PDF, ningún cambio de esquema).
- Riesgos/supuestos: Sin smoke test por navegador (regla de proceso vigente) — verificado generando el PDF real y visualizándolo directamente. No deployado a producción todavía en este ciclo.
- 2026-08-19 — CR-42: el cliente está cargando ventas reales de la semana anterior que ya facturó por fuera del sistema (directo desde la página oficial de AFIP, con CAE real). 2 necesidades: (1) que la Venta quede con la fecha real en que ocurrió, no la fecha de carga; (2) cómo cargarlas sin duplicar la factura ante AFIP (el botón "Facturar" de `Ventas/Details` siempre solicita un CAE nuevo — usarlo para estas ventas emitiría una segunda factura real). **Decisión confirmada con el cliente**: dado que son pocas ventas puntuales (no un flujo que se vaya a repetir seguido) y el cliente tiene el CAE real a mano, no se construye una pantalla nueva — se registra directo en la base con un script de una sola vez, mismo patrón ya usado por `tools/ImportarHistorico/Program.cs` (CR-13): crea el `ComprobanteAfip` con `Estado=Emitido` y los datos reales (Tipo, PuntoVenta, NumeroComprobante, CAE, VencimientoCAE, Fecha) sin llamar al webservice de AFIP, y marca `VentaItem.CantidadFacturada = Cantidad`. La Venta en sí se carga por la pantalla normal (`Ventas/Create`, ahora con fecha elegible, ver más abajo) — el Administrador NO debe pasar por "Facturar" para estas ventas puntuales, evitando la re-emisión.
- 2026-08-19 — CR-42 (fecha de la venta editable): agregado `VentaInput.Fecha` (nullable, solo día) a `Ventas/Create.cshtml` — Administrador-only (mismo criterio que el resto de los overrides financieros/de fecha sensibles de la pantalla, para que un Vendedor no pueda alterar en qué día impacta una venta en Caja/reportes sin supervisión), nunca futura. Sin fecha explícita, cae al comportamiento histórico (hoy). Mismo patrón ya usado por `PagoVentaInput.Fecha` (CR-29): se combina el día elegido con la hora actual de Argentina y se convierte a UTC real vía `HorarioArgentino.ConvertirAUtc`. La fecha elegida se propaga de forma consistente a `Venta.Fecha`, `PagoVenta.Fecha` (de los pagos cargados junto con la venta), el movimiento de stock (`IStockService.RegistrarMovimientoAsync` gana parámetro opcional `fecha`) y el ingreso en Caja (`ICCLocalService.RegistrarMovimientoAsync`, que ya tenía el parámetro desde CR-29) — para que una venta backdateada no quede con fecha de hoy en unos lugares y la fecha real en otros. Sin migración EF (no hay columna nueva, solo deja de hardcodear `DateTime.UtcNow`).
- 2026-08-16 — CR-41: pedido explícito del cliente, ítems de Venta con 100% de descuento (ej. bonificación/regalo) deben poder cargarse y confirmarse igual. El guard server-side de `VentaService.ConfirmarAsync`/`EditarAsync` (Administrador-only) exigía `Subtotal > 0` sin excepción, bloqueando con "Precio o subtotal inválido" justo el caso de un ítem 100% bonificado (Subtotal calculado en $0 por diseño, `Cantidad × PrecioActivo × (1-100/100)`). Corregido a `Subtotal >= 0` (solo se bloquea negativo) — `PrecioUnitario` sigue exigiendo ser mayor a cero sin excepción (el precio base del producto nunca es $0, lo que puede llegar a 0 es el resultado después del descuento). El campo `% Descuento` ya admitía 100 en el cliente (`max="100"`) desde CR-40, así que no hizo falta cambio de UI — solo el guard del servidor. Sin migración EF (cambio de validación, sin cambio de esquema).
- 2026-08-15: Bug reportado por el cliente tras la auditoría — "al crear la venta con los pagos configurados, estos se guardan en un solo pago". Causa raíz real encontrada (no el sospechoso inicial de los botones "Todo efectivo/transferencia", descartado por el cliente): `jquery.maskMoney.js` intercepta cada tecla con `preventDefault()` y escribe el valor a mano, sin disparar nunca el evento `input` nativo del browser — el único evento que dispara es `change`, y solo al perder el foco. Los handlers de Precio contado/tarjeta, Subtotal, Monto de pago y Total editable en `Ventas/Create.cshtml` y `Ventas/Edit.cshtml` escuchaban únicamente `'input'`, así que el array JS que arma el payload de guardado quedaba "congelado" en el valor inicial de cada campo mientras el usuario tipeaba, aunque la pantalla mostrara el número correcto — si el usuario clickeaba "Confirmar"/"Agregar" sin que el campo llegara a perder el foco antes, se enviaba el valor viejo (o vacío) en vez del tipeado. Corregido escuchando también `'change'` en los 6 campos afectados, más una relectura defensiva de todos los campos `.money` justo antes de armar el payload final (por si algún campo no llega a hacer blur). Documentado también como estándar genérico del estudio en `23-web.instructions.md` para cualquier proyecto que reutilice este plugin vendored.
- 2026-08-15: Auditoría completa de los 18 módulos de Etapa 1 (código vs. documentación), pedida por el cliente. Corregidos: precarga de precio equivocada en Facturación AFIP (usaba precio Negro aun en líneas "Con IVA"); bug de terceros en `jquery.maskMoney.js` que pisaba montos de pago ya cargados; botón "Todo transferencia" de Ventas sin contemplar el tope "Con IVA" de CR-40 (ahora fuerza esa opción de precio en todas las líneas antes de armar el pago); falta de traza en el ledger de stock del script de reconciliación del 14/08 (ahora genera `MovimientoStock` tipo Ajuste); `ProductoService.UpdateAsync` sin capturar conflicto de concurrencia con Aumento masivo; fila de la tabla resumen de módulos que prometía envío WhatsApp desde Presupuesto (en realidad es de Venta, CR-4); fila de criterios de aceptación de Sprint 4 desactualizada respecto de CR-7 (acreditación de cheques). También, con confirmación explícita del cliente: unificado el Proveedor duplicado "CARDOZO, JUAN CRUZ" (Id=15 sobrevive, Id=22 se soft-deletea) pendiente desde la auditoría de CR-27 — verificado primero que ambos registros son byte-idénticos en todos los campos fiscales (mismo CUIT 20-38325877-5, mismo domicilio fiscal completo, mismo criterio de verificación que CR-17) y que Id=22 no tiene ninguna OrdenCompra ni MovimientoCCProveedor asociado (0/0), por lo que no hizo falta reasignar FKs como en CR-17, solo el soft-delete. **Aplicado en `marihogar_dev`, pendiente replicar en producción en el próximo despliegue** (no se toca producción sin autorización explícita separada). Hallazgo pendiente de confirmación del cliente, no auto-corregido: certificado AFIP de producción real ya cargado (28/07/2026) contradice la documentación vigente en varios documentos del agente, que sigue describiendo el certificado como pendiente. Detalle completo en el reporte de auditoría entregado al cliente.
- 2026-08-15: Discovery + Análisis v14 — CR-40, regla de negocio permanente pedida explícitamente por el cliente para quedar documentada (no solo implementada): modelo de precios en negro (solo efectivo sin factura) vs. con IVA/21% (efectivo con factura, transferencia, MercadoPago, Banco Carrefour, o tarjeta — decidido con el cliente que estos 3 métodos van siempre "con IVA"); % descuento/recargo configurable por Producto (precarga el default editable por línea que ya existía desde CR-38); pantalla admin nueva de % interés por cantidad de cuotas (3/6/9/12); y la matemática correcta de porcentajes invertibles (`PorcentajeHelper`, dividir para revertir un recargo, nunca restar el mismo %) aplicada retroactivamente y documentada también como estándar de código del estudio. **Mismo día, revisión de consistencia pedida por el cliente** ("revisar la lógica de ventas y pagos en base a las últimas definiciones"): encontrado y cerrado un hueco real (CA-CR40.3) — la regla "tarjeta siempre con IVA" no tenía candado server-side desde que CR-38 sacó el recargo automático del pago, se agregó la validación que lo garantiza de verdad.
- 2026-08-11: Discovery + Análisis v13 — CR-32 (precio contado/tarjeta visible para ambos roles + recargo real del 21% aplicado al monto cubierto por cada línea de pago, no por ítem fijo — mecánica fijada con un ejemplo numérico real del cliente), CR-33 (edición completa de Venta ya creada, bloqueada únicamente si ya tiene un Comprobante AFIP con CAE real emitido) y CR-34 (acreditación diferida de pagos con tarjeta — fecha efectiva + Estado Pendiente/Acreditado, el ingreso en CC Local se difiere hasta acreditar, a diferencia del precedente de Cheque que postea inmediato). 4 decisiones de diseño confirmadas con el cliente vía `AskUserQuestion` antes de diseñar. Los 3 comparten cambios de modelo en `PagoVenta` (`MontoBase`, `EstadoAcreditacion`, `FechaAcreditacionEfectiva`) — 1 migración EF combinada.
- 2026-07-30: Discovery + Análisis v12 — CR-27, disparado por un archivo nuevo del cliente (ledger real de Cuenta Corriente de Proveedores). 3 hallazgos: (1) el Total de las 239 OC históricas no incluía impuestos (subvaluado ~$19,4M); (2) CR-19 había marcado todo como pagado de forma ficticia, el archivo nuevo trae el pago real de 333 movimientos; (3) Mercado Pago se usa realmente para pagar a proveedores (excluido hasta ahora por decisión de diseño de CR-3). 2 decisiones confirmadas con el cliente (corregir el Total con impuestos reales; habilitar Mercado Pago también hacia adelante). Corrección del histórico (hallazgos 1/2, mismo criterio que CR-23 — dato ya migrado incorrecto) + 2 capacidades nuevas menores (Mercado Pago para OC, NotaInterna en OrdenCompra).
- 2026-07-30: Discovery + Análisis v11 — CR-25 (comprobante AFIP totalmente editable, venta como referencia no como fuente de verdad — 2 decisiones de diseño confirmadas con el cliente) y CR-26 (rediseño visual de remito/factura PDF + hallazgo de cumplimiento no solicitado: falta el código QR obligatorio de AFIP desde 2019, se suma al mismo alcance). Sin gate de presupuesto nuevo.
- 2026-07-30: Discovery + Análisis v10 — CR-24, 4 sub-ítems sobre Ventas ya en producción: (1) bug real del toggle de IVA que descartaba precios editados a mano; (2) layout de 4 elementos en la columna de precio; (3) Total editable con reparto proporcional (confirmado con el cliente); (4) nueva capacidad de registrar pagos sobre una Venta ya creada, mirror exacto de Compras — incluye redirect a Details tras crear. Sin gate de presupuesto nuevo, corrección + extensión de bajo-medio esfuerzo sobre CR-22 ya aprobado.
- 2026-07-29: Discovery + Análisis v9 — CR-23, corrección exhaustiva de Ventas históricas tras reporte del cliente de que el precio y la forma de pago migrados no coincidían con la realidad. 3 hallazgos: (1) el monto usado no incluía IVA (Precio Unitario es neto, Total Venta = neto×1,21); (2) el campo Descuento ya queda absorbido al usar Total Venta directo, sin necesitar modelarlo aparte; (3) la forma de pago real está en Nota Interna en 68% de las ventas, parseable con un catálogo de patrones (eft/mpo/visa/master/naranja/transf carre/debito), incluyendo 8 ventas con múltiples formas de pago y 2 con saldo pendiente real. Sin gate de presupuesto nuevo — corrección de un dato ya migrado, mismo criterio que MH-006/MH-007.
- 2026-07-28: Discovery + Análisis v8 — CR-21 (Producto: Precio Efectivo + Precio de Lista +21%, derivado) y CR-22 (Ventas: precio unitario/subtotal editables solo para Administrador, selector de IVA por línea, Total on-demand). Resueltas 2 decisiones de diseño con el cliente antes de tocar código: alcance del toggle de IVA (por línea) y naturaleza del subtotal editable (override manual real). Identificado y resuelto con el cliente un punto de seguridad real (el server hoy nunca confía en el precio del cliente) antes de implementar. Pendiente: Diseño, Arquitectura y Presupuesto.
- 2026-07-28: CR-19 — a pedido del cliente, el importador registra pago total (Efectivo) por cada Orden de Compra histórica. Verificado con la re-corrida real contra `marihogar_dev`: 239/239 OC con saldo pendiente $0, CC Proveedores en $0 sin necesitar ajuste de apertura (0 ajustes posteados, la lógica de CR-18 se auto-desactiva porque ya no hace falta), CC Local sin cambio (1 ajuste de apertura, sigue siendo necesario). Sin gate de presupuesto nuevo.
- 2026-07-28: Discovery + Análisis v7 — CR-14 (saldo calculado en CC Local/Proveedores), CR-15 (fecha de emisión de cheque por defecto en OC), CR-16 (mayúsculas Proveedor/Producto), CR-17 (unificación de Proveedor duplicado, resuelta directamente como dato), CR-18 (ajuste de apertura para saldo $0 post-import) y refinamiento de CR-13 (ClienteCUIT). CR-16 y CR-17 con componente de datos ya ejecutado en `marihogar_dev`. Sin gate de presupuesto nuevo — mismo criterio que CR-8/CR-9/CR-13 (adenda de bajo esfuerzo sobre el Change Request #1 ya aprobado).
- 2026-07-27: Discovery + Análisis v6 — CR-13, corrección del cliente sobre la conclusión de CR-6: ~45% de las Ventas históricas (286/634) sí tienen factura real (Punto de Venta + Nº de Factura), dato que estaba en el Excel pero no se había separado del análisis de la columna "ARCA" (que resultó no ser un indicador válido). Se crea `ComprobanteAfip` real para esas Ventas al importar — sin cambio de modelo, solo ajuste del importador. Corrige también la precisión futura de CR-9. Sin gate de presupuesto nuevo, se implementa junto a CR-10/11/12.
- 2026-07-27: Discovery + Análisis v5 — auditoría columna por columna de los 4 Excel de `/Importacion` (más allá de lo ya usado por CR-6), pedida explícitamente por el cliente. 3 gaps nuevos identificados y aceptados para presupuestar (CR-10 Nº de comprobante en OC, CR-11 Subcategoría de Gasto, CR-12 Nota interna de Venta), varios gaps documentados y descartados con motivo (IVA discriminado, Proveedor por línea de Venta, Descuento aparte). Independiente de la decisión pendiente de ejecutar CR-6 en producción. Pendiente: Diseño, Arquitectura y Presupuesto de esta ampliación.
- 2026-07-27: Discovery + Análisis v4 — CR-8 (sugerir total como monto de pago por defecto) y CR-9 (reportes de ventas/ingresos distinguen facturado vs. no facturado) agregados durante la ejecución del Sprint CR-A. Se presupuestan como adenda del Change Request #1, se implementan en Sprint CR-B.
- 2026-06-29: Discovery v1. 10 módulos. Sistema de captación y ventas.
- 2026-06-29: Análisis v1 cerrado. Presupuesto: $1,171 (con descuento 15% referido).
- 2026-07-06: Discovery v2. Relevamiento del sistema actual (Contagram). Alcance ampliado a 18 módulos — sistema de gestión comercial completo. Presupuesto v1 invalidado. P1-A/P2-B/P3-A/P4-B/P5-A confirmados. Análisis v2 cerrado. Pendiente: nuevo presupuesto.
- 2026-07-27: Discovery + Análisis v3 cerrado — feedback de la primera demo post-Etapa 1. 7 change requests (CR-1 a CR-7) + análisis de importación de datos históricos (`/Importacion`, 4 archivos Excel reales: 32 proveedores, 239 compras, 634 ventas, 481 gastos). 3 preguntas críticas resueltas con el cliente (mecanismo de envío WhatsApp, categoría "Otro" de resguardo en Gastos, ampliación de campos de Proveedor). Pendiente: Diseño, Arquitectura y Presupuesto de este change request.
