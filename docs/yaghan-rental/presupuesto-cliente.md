# Olvidata**Soft**

---

**Propuesta de desarrollo — Sistema de gestión de ventas y alquileres para Yaghan Rental**
**OlvidataSoft · Agosto 2026**

---

## Sobre el sistema

Un sistema para manejar todo el ciclo de tu local — desde que te escriben por WhatsApp hasta que devuelven el equipo — sin depender de planillas ni de memoria.

- Atendés todas las consultas de WhatsApp desde una sola bandeja dentro del sistema, sin cambiar de app.
- Armás la cotización eligiendo prendas y días de alquiler, y el sistema calcula el precio según tus promociones por cantidad de días.
- Cerrás la reserva con los datos del cliente y el comprobante de pago, y el sistema genera un código QR único para esa reserva.
- Al entregar el equipo, le tomás una garantía en la tarjeta de crédito del cliente por si hay un robo o una rotura — sin cobrarle nada por adelantado, y se libera sola si todo vuelve bien.
- Ves de un vistazo qué vence hoy, esta semana y qué está por vencer, además de un checklist diario con los pagos y devoluciones pendientes.
- Procesás la devolución escaneando el QR desde tu celular — o buscando al cliente a mano si no lo tiene a mano — y el sistema libera el stock automáticamente.
- Tus clientes reciben un WhatsApp pidiéndoles una reseña apenas devuelven todo en buen estado, y un aviso automático si se atrasan.
- Configurás el % de comisión de cada agencia, hotel o guía que te deriva clientes, y el sistema lo calcula solo en cada venta o alquiler.
- Registrás tus compras a proveedores y el seguimiento de la ropa que mandás a arreglar a un taller.
- Cerrás la caja de cada día con el balance de ingresos y egresos del local.

---

## Cómo funciona la garantía con tarjeta de crédito — paso a paso

**1. El cliente retira el equipo.** En ese momento, no antes — así evitamos que la garantía venza si la reserva se hizo con mucha anticipación.
**2. Pasa su tarjeta por un formulario seguro de Mercado Pago.** El sistema *reserva* un monto en su límite de crédito, igual que hacen las rentadoras de auto — **no le cobra nada todavía**. La tarjeta nunca pasa por tus sistemas, la maneja Mercado Pago directamente.
**3. Devuelve todo en buen estado.** El sistema libera la reserva de fondos automáticamente, sin que tengas que hacer nada.
**4. Si hay un daño o falta algo.** Vos decidís cuánto cobrar de esa garantía (hasta el monto que quedó reservado) y el sistema lo capturá.

**Casos especiales contemplados:**
- Si el cliente **no tiene una tarjeta Visa, Mastercard, Cabal o American Express** (las únicas compatibles con este mecanismo), le pedís un depósito por otro medio (efectivo o transferencia) como alternativa — el sistema lo registra igual.
- Si el alquiler dura **más de 7 días**, la reserva de fondos vence antes de la devolución (es un límite de la plataforma de pago, no del sistema) — el sistema te avisa con anticipación para volver a autorizar la tarjeta antes de que eso pase.

*El monto de la garantía es un valor fijo que vos configurás — no varía según qué artículos se lleve el cliente.*

---

## Cómo funciona el CRM de WhatsApp

**1. Llega una consulta.** Al mismo número de WhatsApp que ya usás hoy — aparece en tu bandeja dentro del sistema.
**2. Respondés desde el sistema.** Sin cambiar de app ni perder el historial de la conversación.
**3. Armás la cotización.** Elegís las prendas y los días directamente desde la conversación, y se la mandás al cliente con un clic.
**4. Confirmás la reserva.** Desde la misma pantalla, cuando el cliente acepta.

*Nota operativa importante: para que el CRM pueda mandar y recibir mensajes por tu número actual, Meta (WhatsApp) requiere migrarlo a su plataforma de negocio. Existe una función llamada "coexistencia" que permite seguir usando la app normal del celular en paralelo, pero su disponibilidad depende de la elegibilidad de tu cuenta — lo verificamos juntos antes de migrar en producción. Si tu cuenta no califica, a partir de la migración todo el envío y recepción de ese número pasaría a hacerse exclusivamente desde el sistema.*

---

## Rol de usuario

| Rol | Accesos |
|---|---|
| Administrador | Acceso completo: WhatsApp, cotizaciones, reservas, devoluciones, catálogo, referentes, proveedores, compras, talleres, caja diaria y ventas. |

*Un solo perfil de usuario para el equipo del local, tal como lo pediste. Si más adelante necesitás roles distintos (por ejemplo, un perfil de Atención sin acceso a Caja), se puede sumar como extensión sin romper lo ya construido.*

---

## Inversión

**Desarrollo: USD 850**

*Tokens IA y eficiencia de desarrollo ya están contemplados dentro de este valor — no hay costos ocultos ni adicionales por fuera de esta cifra.*

Cubre el sistema completo: CRM de WhatsApp, catálogo con tarifas por cantidad de días, cotización, reservas con QR, garantía con tarjeta de crédito, devoluciones, checklist diario y vencimientos, referentes y comisiones, proveedores, compras, talleres, caja diaria y ventas.

---

## Mejoras opcionales (Etapa 2)

| Área | USD |
|---|---:|
| Cotización inteligente (sugerencia automática de combos según lo que pide el cliente) | 50 |
| Cobro online integrado con Mercado Pago | 134 |
| **Subtotal** | **185** |

---

## Mantenimiento anual

| Plan | USD/año | Incluye |
|---|---:|---|
| Yaghan Rental | 600 | Hosting, SSL, dominio, hasta 3 usuarios, soporte prioritario, 2 rondas de ajuste al año |

***Primer año sin cargo*** *— se factura desde el segundo año de uso.*

---

## Qué incluye el proyecto

- Diseño e implementación completa del sistema, incluido el CRM de WhatsApp (bandeja, envío/recepción, avisos automáticos de reseña y atraso), dentro de la misma inversión.
- Generación de código QR por reserva y lectura desde el navegador del celular, sin apps adicionales.
- Garantía con tarjeta de crédito vía Mercado Pago (reserva de fondos sin cobro, liberación o captura según el estado de la devolución), con registro de depósito alternativo para quien no tenga tarjeta compatible.
- Configuración de comisiones por referente, con porcentaje editable por vos en cualquier momento.
- Caja diaria con cierre de balance del local.
- Guía de pruebas para que valides el sistema antes de la puesta en marcha.
- Primer año de mantenimiento sin cargo.

## Qué no está incluido

- Sugerencia automática de combos en la cotización y cobro online con Mercado Pago (Etapa 2, opcional).
- Migración de datos desde un sistema anterior.
- Costo del servidor/hosting (se cotiza en el plan de mantenimiento anual de arriba).
- Facturación electrónica AFIP/ARCA.
- Aplicación móvil (iOS/Android) — el sistema funciona desde el navegador del celular, sin necesidad de instalar nada.
- Integración con hardware externo.
- Cambios de alcance posteriores al inicio — se cotizan por separado.

---

## Lo que necesitamos de tu parte

- Acceso al Meta Business Manager de tu cuenta de WhatsApp (o autorización para gestionarlo) para verificar la elegibilidad de "coexistencia" antes de migrar el número +5492901652524.
- Una cuenta de Mercado Pago del negocio (si todavía no tenés credenciales de desarrollador habilitadas, te guiamos para sacarlas) para la garantía con tarjeta.
- Definir el monto fijo de la garantía a autorizar por reserva.
- Confirmar la política de seña/depósito para la reserva (no la vimos publicada en tu web) — ¿se cobra un adelanto parcial o el pago se registra completo al reservar?
- Listado de tus referentes actuales (agencias, hoteles, guías) con el % de comisión de cada uno, si ya tenés acuerdos definidos.
- Confirmar si hay más de un dispositivo móvil en el local para usar la función de escaneo de QR, y que tenga cámara y navegador actualizado.
- Catálogo actualizado de artículos con tallas, stock y las tarifas por 1/3/7 días (o los rangos que uses) para la carga inicial.

---

## Condiciones comerciales

- Forma de pago: 50% al inicio y 50% a la entrega.
- Moneda: USD, pagadero en pesos al tipo de cambio del día.
- Mantenimiento anual: USD 600/año desde el segundo año de uso — el primero va sin cargo.
- Cambio de alcance disponible en cualquier momento si el proyecto crece — se cotiza aparte.

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
