# Memoria - Analista funcional

## Proyecto: decorhogar *(nombre provisional — confirmar con cliente)*
## Ultima actualizacion: 2026-06-29

---

## Análisis funcional cerrado — 2026-06-29

### Contexto del negocio
- Rubro: venta de productos de decoración y hogar
- Canal de captación: anuncios en Meta (Facebook / Instagram)
- Canal de contacto del lead: WhatsApp (clic en anuncio → mensaje al número del negocio)
- Cierre de venta: presencial en el local O con entrega y cobro a domicilio
- Proceso actual: manual, sin CRM, sin stock sistematizado, facturación en local
- Objetivo: maximizar y agilizar ventas — reducir fricción entre lead y cierre

---

### Proceso objetivo relevado
1. Meta Ads → lead hace clic → envía WhatsApp
2. **Bot automático** responde, captura nombre e interés → registra Lead en CRM
3. Vendedor retoma desde CRM, hace seguimiento, envía presupuesto en PDF por WhatsApp
4. Cliente aprueba presupuesto → vendedor convierte a Venta
5. Venta en local → pago registrado (múltiples medios) → descuento de stock → **factura electrónica AFIP (CAE)**
6. Venta con entrega → vendedor programa entrega, va al domicilio → cobra en destino → registra pago desde sistema → factura AFIP

---

### Módulos confirmados

| # | Módulo | Descripción | Complejidad |
|---|---|---|---|
| M1 | CRM de Leads | Registrar leads con máquina de estados, historial de contacto | Media |
| M2 | Catálogo de productos | Productos con fotos, precio, categorías | Baja |
| M3 | Control de stock | Movimientos entrada/salida, alertas de stock bajo | Media |
| M4 | Presupuestador | Armar cotización, generar PDF, enviar por WhatsApp | Media |
| M5 | Gestión de ventas | Líneas de producto, formas de pago múltiples, estados | Alta |
| M6 | Gestión de entregas | Dirección, fecha, estado, cobro en destino | Media |
| M7 | Facturación AFIP | Integración WSFE + WSAA, emisión de CAE, PDF de comprobante | **Muy alta** |
| M8 | Automatización WhatsApp | Webhook Meta, bot auto-respuesta, envío de mensajes/PDFs | **Muy alta** |
| M9 | Dashboard / reportes | Conversión de leads, ventas por período, stock crítico | Media |
| M10 | Gestión de usuarios | Roles: Administrador / Vendedor | Baja |

---

### Casos de uso principales

**CU-01: Lead entra por WhatsApp**
- Actor: lead (externo)
- Flujo: Meta Ad → WhatsApp → Bot responde automáticamente → captura nombre e interés → crea Lead en estado "Nuevo" → notifica al vendedor

**CU-02: Seguimiento de lead**
- Actor: Vendedor
- Flujo: Vendedor abre CRM → ve leads pendientes → contacta → avanza estado → registra nota

**CU-03: Generar y enviar presupuesto**
- Actor: Vendedor
- Flujo: Abre lead → selecciona productos y cantidades → sistema calcula totales → genera PDF (QuestPDF) → envía por WhatsApp al número del lead

**CU-04: Convertir presupuesto a venta**
- Actor: Vendedor
- Flujo: Lead aprueba → Vendedor convierte Presupuesto en Venta → stock reservado → estado Lead pasa a "Vendido"

**CU-05: Registrar venta en local**
- Actor: Vendedor
- Flujo: Selecciona productos → registra pago (uno o varios medios) → sistema descuenta stock → emite factura AFIP (CAE) → genera PDF de factura

**CU-06: Gestionar entrega a domicilio**
- Actor: Vendedor / Administrador
- Flujo: Venta con entrega → programa fecha + dirección → Vendedor va al domicilio → cobra → registra pago desde sistema → emite factura AFIP → estado Entrega = "Entregada"

**CU-07: Administrar catálogo y stock**
- Actor: Administrador
- Flujo: Alta/edición de producto → foto, precio, stock inicial → sistema controla movimientos

**CU-08: Ver dashboard**
- Actor: Administrador
- Flujo: Ver métricas de leads por período, tasa de conversión, ventas totales, productos con stock crítico

---

### Máquinas de estados confirmadas

**Lead:**
Nuevo → Contactado → Presupuesto enviado → [Vendido | Perdido]
También: Contactado → Visita programada → [Vendido | Perdido]
También: Contactado → Entrega programada → [Vendido | Perdido]

**Presupuesto:**
Borrador → Enviado → [Aprobado → Convertido | Rechazado | Expirado]

**Venta:**
Pendiente → Pagada parcialmente → Pagada → [Con entrega pendiente → Entregada | Completada]
También: Pagada → Cancelada (con reposición de stock)

**Entrega:**
Pendiente → En camino → [Entregada | No entregada (reagendar)]

---

### Criterios de aceptación (por módulo)

**M1 - CRM Leads**
- CA-01: Un lead nuevo creado por el bot aparece en la lista de leads del vendedor en menos de 30 segundos
- CA-02: El vendedor puede avanzar el estado del lead y la transición queda registrada con fecha y responsable
- CA-03: Se puede filtrar leads por estado, fecha y vendedor asignado

**M2 - Catálogo**
- CA-04: Se puede cargar producto con hasta 5 fotos, precio, categoría y descripción
- CA-05: El catálogo es compartible (link o PDF) para enviar al cliente por WhatsApp

**M3 - Stock**
- CA-06: Cada venta o entrega descuenta automáticamente el stock
- CA-07: El sistema muestra alerta visual cuando un producto cae por debajo del stock mínimo configurado
- CA-08: El Administrador puede registrar entradas de stock (compras/reposición)

**M4 - Presupuestador**
- CA-09: El presupuesto incluye listado de productos, cantidades, precios y total
- CA-10: Se genera PDF del presupuesto con datos del negocio (logo, CUIT, datos de contacto)
- CA-11: El presupuesto se puede enviar directamente al número de WhatsApp del lead desde el sistema

**M5 - Ventas**
- CA-12: Se pueden registrar múltiples formas de pago en una sola venta (efectivo + transferencia, etc.)
- CA-13: El total de la venta debe cuadrar con la suma de los pagos registrados para cerrar la transacción
- CA-14: Una venta convertida desde presupuesto hereda todos los ítems del presupuesto

**M6 - Entregas**
- CA-15: La entrega registra dirección, fecha estimada y vendedor asignado
- CA-16: El vendedor puede registrar el cobro desde el sistema al momento de la entrega (mobile-friendly)
- CA-17: La factura AFIP se puede emitir en el momento del cobro en domicilio

**M7 - AFIP**
- CA-18: El sistema se autentica contra WSAA y renueva el token automáticamente (24h de validez)
- CA-19: Se puede emitir Factura B (consumidor final) y Factura A (responsable inscripto)
- CA-20: El CAE y fecha de vencimiento quedan registrados en la Venta
- CA-21: Se genera PDF del comprobante emitido (con QR AFIP si aplica)

**M8 - WhatsApp Bot**
- CA-22: El bot responde el primer mensaje del lead en menos de 60 segundos
- CA-23: El bot captura al menos nombre e interés (producto consultado)
- CA-24: El sistema puede enviar PDFs (presupuesto, factura) al número del lead directamente

**M9 - Dashboard**
- CA-25: Se puede ver cantidad de leads por período con filtro de fechas
- CA-26: Se muestra tasa de conversión Lead → Venta
- CA-27: Se muestran los 5 productos más vendidos y los productos con stock crítico

**M10 - Usuarios**
- CA-28: El Vendedor puede: crear/editar leads, crear presupuestos, registrar ventas y entregas
- CA-29: El Vendedor NO puede: modificar precios, ver reportes financieros completos, administrar usuarios
- CA-30: El Administrador tiene acceso total

---

### Permisos por rol

| Acción | Administrador | Vendedor |
|---|---|---|
| Gestionar catálogo y precios | ✓ | ✗ |
| Gestionar stock (entradas) | ✓ | ✗ |
| Ver/gestionar leads | ✓ | ✓ |
| Crear presupuestos | ✓ | ✓ |
| Registrar ventas | ✓ | ✓ |
| Registrar entregas y cobros | ✓ | ✓ |
| Emitir facturas AFIP | ✓ | ✓ |
| Ver dashboard completo | ✓ | ✗ |
| Gestionar usuarios | ✓ | ✗ |
| Configurar bot WhatsApp | ✓ | ✗ |

---

### Supuestos confirmados

- Sistema web responsivo (no app nativa, pero debe funcionar desde celular para el vendedor en domicilio)
- Un único punto de venta AFIP (local)
- La empresa es Responsable Inscripto (emite Factura A y B)
- Las fotos de productos las provee el cliente
- El bot de WhatsApp es el primer contacto; el vendedor retoma desde ahí
- Pago puede suceder en el local O al momento de la entrega en domicilio

### Exclusiones confirmadas (fuera de v1)
- App móvil nativa (iOS/Android)
- E-commerce / tienda online con carrito
- Integración con sistemas contables externos (Tango, Contaplus)
- Multi-sede / multi-punto de venta
- Envíos con transportistas externos (OCA, Andreani)

---

### Banderas tempranas

| Bandera | Estado | Impacto |
|---|---|---|
| Migración EF | Sí — proyecto nuevo | Bajo |
| Integración AFIP WSFE + WSAA | **Confirmada** | Muy alto |
| Integración WhatsApp Business Cloud API | **Confirmada** | Muy alto |
| Máquina de estados (Leads, Presupuestos, Ventas, Entregas) | **Confirmada** | Alto |
| Responsive / mobile-friendly obligatorio | **Confirmado** | Medio |
| QuestPDF para presupuestos y facturas | Confirmada | Bajo |

---

### Riesgos y supuestos — ACTUALIZADOS 2026-06-29

| Riesgo | Nivel actualizado | Detalle |
|---|---|---|
| Hosting incompatible con WhatsApp webhook o AFIP | ~~Alto~~ → **ELIMINADO** | SMARTEASP (olvidatasoft) ya corre BotPublicitario (webhook Meta) y delicias-naturales (AFIP WSFE). Infraestructura confirmada compatible. |
| Aprobación Meta Business / número WhatsApp | ~~Medio~~ → **ELIMINADO** | Cliente ya tiene Meta Business Manager activo (confirmado 2026-06-29). Solo requiere asociar número WhatsApp Business dedicado al Business Manager existente. |
| Certificado digital AFIP | Medio | Requiere CUIT del cliente, gestión en portal AFIP, y subida del .p12 al servidor. Patrón conocido (delicias-naturales). Solicitar al cliente desde el inicio. |
| Sistema mobile-friendly para cobros en domicilio | Medio | Definir vistas críticas para mobile en etapa de diseño. |
| Bot v1 con mensajes no estructurados | Medio | En v1 flujo guiado (preguntas cerradas); fallback "un representante te contactará pronto". |

### Componentes reutilizables identificados

| Componente | Fuente | Reutilización |
|---|---|---|
| `WhatsAppClient.cs` (HTTP client Meta Graph API) | `C:\Sistemas\BotPublicitario\WhatsApp\` | Portar a .NET 10 MVC, adaptar para inbound + outbound |
| `MessagingService.cs` (envío de templates, mensajes, PDFs) | `C:\Sistemas\BotPublicitario\WhatsApp\` | Adaptar y embeber en el nuevo sistema |
| Patrón AFIP WSAA + WSFE (.p12, token 24h, FECAESolicitar) | `C:\Sistemas\delicias-naturales\` | Reimplementar en .NET 10 (delicias usa .NET 4.7.2 — SOAP client distinto, pero patrón idéntico) |
| Infraestructura de hosting SMARTEASP | olvidatasoft-002 | Mismo servidor, sin cambios de infraestructura |

---

## Historial de ajustes
- 2026-06-29: Discovery inicial. Proceso actual relevado. Preguntas enviadas al cliente.
- 2026-06-29: Análisis cerrado. Cliente confirmó todas las opciones de mayor alcance (P1-P7 opción B). 10 módulos confirmados. 4 máquinas de estados. 30 criterios de aceptación. Banderas: integración AFIP + WhatsApp (muy alto impacto).
