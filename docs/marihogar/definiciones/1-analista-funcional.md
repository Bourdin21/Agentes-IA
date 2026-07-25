# Memoria - Analista funcional

## Proyecto: decorhogar *(nombre provisional — confirmar con cliente)*
## Ultima actualizacion: 2026-07-06

---

## Análisis funcional v2 — CERRADO 2026-07-06

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

## Módulos confirmados — 18 módulos

### Grupo 1 — Captación y ventas
| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M1 | CRM de Leads | Leads desde WhatsApp, máquina de estados, historial | Media |
| M4 | Presupuestador | Cotización multi-línea, PDF, envío WhatsApp | Media |
| M5 | Gestión de ventas | Multi-pago, estados, impacto automático en CC del local | Alta |
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

## Procesos principales confirmados

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

## Máquinas de estados confirmadas (6)

**Lead:** Nuevo → Contactado → Presupuesto enviado → Vendido / Perdido
*(también: Contactado → Visita programada / Entrega programada)*

**Presupuesto:** Borrador → Enviado → [Aprobado → Convertido | Rechazado | Expirado]

**Venta:** Pendiente → Pagada parcialmente → Pagada → [Con entrega pendiente → Entregada] / Cancelada

**Entrega:** Pendiente → En camino → Entregada / No entregada (reagendar)

**Orden de compra:** Borrador → Confirmada → Recibida / Cancelada

**Cheque:** Pendiente → Acreditado *(automático, job diario)* / Rechazado *(manual)*

---

## Criterios de aceptación — módulos nuevos

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

## Permisos por rol — actualizados

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

## Supuestos confirmados

- Sistema web responsivo — mobile-friendly obligatorio para vistas de entrega y cobro
- Un único punto de venta AFIP (local)
- Responsable Inscripto — emite Factura A y B
- Ventas solo al contado — no hay clientes con deuda / fiado (P5-A)
- CC del local = balance interno, sin deudores de clientes (P1-A)
- Gastos operativos (alquiler, servicios, sueldos, fletes) se registran en el sistema (P2-B)
- Recepciones de OC siempre completas — sin entregas parciales de proveedores (P3-A)
- Proyección calculada con promedio histórico + compromisos futuros (P4-B)
- Un solo local / una sola caja

## Exclusiones confirmadas
- App móvil nativa
- E-commerce / carrito de compras
- Integración con sistemas contables externos
- Multi-sede / multi-punto de venta
- Transportistas externos (OCA, Andreani)
- Clientes con cuenta corriente / fiado (P5-A)
- Recepciones parciales de OC (P3-A)

---

## Banderas tempranas — v2

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

## Riesgos y supuestos

| Riesgo | Nivel | Detalle |
|---|---|---|
| Job acreditación cheques: idempotencia | Alto | Debe acreditar exactamente una vez por cheque. Patrón idéntico al job diario de ganadería. |
| Proyección financiera: precisión percibida | Medio | El cliente puede esperar más precisión de la que un promedio simple puede dar. Fijar expectativas en el documento al cliente. |
| Hosting SMARTEASP: job diario compatible | Bajo | Ganadería ya usa el mismo patrón. Compatible confirmado. |
| Certificado ARCA (.p12) del cliente | Medio | Solicitar al cliente antes de iniciar módulo M7. |
| Número WhatsApp dedicado | Medio | Solicitar antes de iniciar M8. |
| Alcance de M9 dashboard puede crecer | Medio | Definir KPIs fijos antes del diseño — no dejar abierto. |

---

## Componentes reutilizables identificados

| Componente | Fuente | Reutilización en decorhogar |
|---|---|---|
| `WhatsAppClient.cs` + `MessagingService.cs` | BotPublicitario | M8 — portar a .NET 10 MVC |
| Patrón AFIP WSAA + WSFE (.p12, token 24h) | delicias-naturales | M7 — reimplementar en .NET 10 |
| Job diario idempotente + IHostedService | ganadería | M14 — acreditación automática de cheques |
| Patrón cheques 30/60/90 (cuotas con vencimiento) | ganadería | M14 — referencia directa de implementación |
| Aumento masivo de precios con previsualización | ShowroomGriffin | M16 — reutilizar patrón |
| Stock manual con ajuste | ShowroomGriffin | M3 — reutilizar patrón |

---

## Historial de ajustes
- 2026-06-29: Discovery v1. 10 módulos. Sistema de captación y ventas.
- 2026-06-29: Análisis v1 cerrado. Presupuesto: $1,171 (con descuento 15% referido).
- 2026-07-06: Discovery v2. Relevamiento del sistema actual (Contagram). Alcance ampliado a 18 módulos — sistema de gestión comercial completo. Presupuesto v1 invalidado. P1-A/P2-B/P3-A/P4-B/P5-A confirmados. Análisis v2 cerrado. Pendiente: nuevo presupuesto.
