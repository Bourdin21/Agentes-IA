# Olvidata**Soft**

---

**Propuesta de desarrollo — Sistema de Gestión Comercial**
**OlvidataSoft · Julio 2026**

---

## Sobre el sistema

Desarrollamos un sistema de gestión comercial completo para tu negocio de decoración y hogar que reemplaza Contagram y cubre todo el ciclo del negocio, desde la captación de clientes hasta la facturación electrónica y la proyección financiera.

El sistema abarca:

- Un cliente ve tu anuncio en Instagram o Facebook, escribe al WhatsApp del negocio y el sistema identifica automáticamente el producto del anuncio
- El vendedor retoma con toda la información del cliente, arma un presupuesto en PDF y lo convierte en venta con un clic
- La venta descuenta el stock automáticamente, registra el pago y genera el movimiento en la cuenta corriente del local
- Las compras a proveedores se gestionan con órdenes de compra, los pagos con cheques a 30/60/90 días se acreditan solos cuando vencen, y la deuda con cada proveedor queda siempre visible
- La caja mensual, los gastos del negocio y una proyección de ingresos y egresos del próximo período te dan claridad financiera en todo momento
- El sistema emite la factura electrónica contra AFIP/ARCA con los ítems que elijas de cada venta

---

## Cómo funciona el bot de WhatsApp — paso a paso

**1. El cliente ve el anuncio y escribe.** Hace clic en tu publicación de un producto en Meta y escribe al WhatsApp del negocio.

**2. El sistema detecta el producto.** Gracias al link del anuncio, el sistema sabe exactamente qué producto vio. No le pregunta "¿qué te interesa?" — ya lo sabe.

**3. Preguntas de calificación por categoría.** En vez de eso, hace preguntas específicas según el producto:

| Categoría | Preguntas del bot |
|---|---|
| Muebles / Sillones | ¿Para qué ambiente? ¿Medidas disponibles? ¿Preferencia de color o material? |
| Iluminación | ¿Interior o exterior? ¿Ambiente? ¿Necesita instalación? |
| Textiles / Cortinas | ¿Medidas de la ventana? ¿Color o estilo? |

*Las categorías y preguntas se configuran una vez según tu catálogo antes de poner el sistema en marcha.*

**4. El vendedor retoma con todo el contexto.** Cuando entra al sistema, ya ve el producto consultado, el anuncio de origen y las respuestas del cliente. Solo tiene que armar el presupuesto.

**Casos especiales contemplados:**
- Si el cliente escribe sin venir de un anuncio, el bot hace una pregunta abierta de bienvenida
- Si el cliente no responde las preguntas de calificación, el lead queda registrado de todas formas para que el vendedor retome

---

## Roles de usuario

| Rol | Accesos |
|---|---|
| **Administrador** | Acceso total: catálogo, precios, stock, compras, proveedores, cheques, caja, gastos, proyección financiera, reportes, usuarios y configuración |
| **Vendedor** | Gestión de contactos, presupuestos, ventas, entregas y facturación. No accede a precios de costo, compras a proveedores, información financiera ni configuración |

*El alta de usuarios, la configuración inicial y las categorías del bot las gestionamos como parte del servicio.*

---

## Etapa 1 — El negocio operando en el sistema desde el primer día

Todo lo necesario para reemplazar Contagram y operar el negocio completo.

### Usuarios y accesos
Alta, edición y baja de usuarios con sus roles. Cada usuario accede únicamente a las funciones que le corresponden.

### Catálogo de productos
Alta, edición y baja de productos con nombre, descripción, precio de compra, precio de venta, marca, modelo, categoría, stock mínimo y hasta 5 fotos por producto.

### Control de stock
El stock se descuenta automáticamente con cada venta y se incrementa al recibir una compra. El Administrador también puede registrar ajustes manuales. Alerta visual cuando un producto cae por debajo del stock mínimo configurado.

### Presupuestos y cotizaciones
El vendedor elige productos y cantidades, el sistema calcula el total y genera un PDF listo para enviar al cliente. Una vez aprobado, se convierte en venta con un clic, sin volver a cargar datos.

### Gestión de ventas
Registro de ventas con sus productos, cantidades y formas de pago (efectivo, transferencia, MercadoPago, en cualquier combinación). Cada venta confirmada genera automáticamente un movimiento en la cuenta corriente del local.

### Entregas a domicilio
Programación de entregas con dirección, fecha y vendedor asignado. El vendedor registra el cobro y cierra la entrega desde el celular en el domicilio del cliente.

### Facturación electrónica AFIP/ARCA
El sistema emite facturas electrónicas directamente contra AFIP (Factura A o B). Seleccionás los ítems y cantidades que querés facturar de cada venta — podés facturar todo, parte o un solo ítem. Genera el CAE y el PDF del comprobante. La autenticación con AFIP se renueva automáticamente.

### Cuenta corriente del local
Balance interno del negocio: ingresos (ventas) menos egresos (compras, gastos). Siempre visible con el detalle de cada movimiento.

### Compras a proveedores
Órdenes de compra con líneas de producto, cantidades y precio de compra. La OC tiene estados (Borrador → Confirmada → Recibida). Al marcarla como recibida, el stock se actualiza automáticamente. Los pagos de la OC aceptan efectivo, transferencia, cheque o depósito, y actualizan la cuenta corriente del proveedor.

### Cuenta corriente de proveedores
Saldo adeudado por proveedor con historial de pagos y movimientos. Se actualiza automáticamente con cada pago registrado en las órdenes de compra.

### Cheques 30 / 60 / 90 días
Los cheques registrados como pago quedan en estado Pendiente hasta su fecha de vencimiento. Al vencer, el sistema los acredita automáticamente y te notifica. Si un cheque se rechaza, el Administrador lo marca manualmente. Los cheques próximos a vencer aparecen como alerta en el panel de inicio.

### Caja mensual
Ingresos y egresos del período con filtro de fechas, totales y comparativo con el mes anterior.

### Gastos del negocio
Registro de gastos operativos (alquiler, servicios, sueldos, fletes y otros) con categoría, forma de pago y fecha. Cada gasto genera el movimiento correspondiente en la cuenta corriente del local y en la caja del período.

### Panel de métricas y dashboard
KPIs del negocio en tiempo real: ventas del período, stock crítico, cheques por vencer, conversión de leads, productos más vendidos y balance de caja. Con filtro de fechas.

### Aumento masivo de precios
Herramienta para actualizar precios en lote: seleccionás si querés aplicar el cambio por marca, por categoría o por modelo, sobre el precio de compra o de venta, y definís el porcentaje de aumento. El sistema muestra una previsualización con el precio actual y el nuevo precio de cada producto antes de confirmar.

### Proyección financiera
El sistema calcula el promedio de ingresos y gastos de los últimos 3 meses y lo combina con los compromisos ya conocidos: cheques por vencer y órdenes de compra pendientes de pago. Si los gastos comprometidos superan los ingresos proyectados, muestra una alerta de déficit. El período base de la proyección se puede ajustar entre 1, 3 y 6 meses.

| Área funcional | USD |
|---|---:|
| Usuarios y accesos | USD 30 |
| Catálogo de productos | USD 55 |
| Control de stock | USD 40 |
| Presupuestos y cotizaciones | USD 55 |
| Gestión de ventas | USD 85 |
| Entregas a domicilio | USD 40 |
| Facturación electrónica AFIP/ARCA | USD 50 |
| Cuenta corriente del local | USD 35 |
| Compras a proveedores | USD 65 |
| Cuenta corriente de proveedores | USD 30 |
| Cheques 30/60/90 días | USD 40 |
| Caja mensual | USD 30 |
| Gastos del negocio | USD 20 |
| Panel de métricas y dashboard | USD 40 |
| Aumento masivo de precios | USD 30 |
| Proyección financiera | USD 55 |
| **Subtotal Etapa 1** | **USD 700** |

---

## Etapa 2 — Captación automática por WhatsApp y CRM

### Atención automática por WhatsApp
El bot identifica el producto del anuncio y hace preguntas de calificación específicas por categoría. Todas las respuestas quedan en el perfil del contacto para que el vendedor retome sin perder contexto.

### Seguimiento de contactos (CRM)
Panel con todos los contactos generados por WhatsApp. Cada uno muestra el producto consultado, el anuncio de origen, el estado de la conversación (nuevo, contactado, presupuesto enviado, vendido, perdido), el historial de interacciones y el vendedor asignado.

| Área funcional | USD |
|---|---:|
| Seguimiento de contactos (CRM) | USD 110 |
| Atención automática por WhatsApp | USD 90 |
| **Subtotal Etapa 2** | **USD 200** |

---

## Total del proyecto

| Concepto | USD |
|---|---:|
| Subtotal Etapa 1 | USD 700 |
| Subtotal Etapa 2 | USD 200 |
| Primer año de mantenimiento (Plan PREMIUM) | incluido |
| **Total proyecto** | **USD 900** |

---

## Mantenimiento anual

El primer año de mantenimiento está incluido en el total del proyecto.

| Plan | Incluye | USD/año |
|---|---|---:|
| **PREMIUM** — desde el 2do año | Hasta 3 usuarios, soporte prioritario por WhatsApp, actualizaciones de seguridad, 2 rondas de ajuste al año | **USD 400** |

*El mantenimiento cubre el servidor, las actualizaciones de seguridad y el soporte técnico. No incluye cambios funcionales nuevos (se cotizan por separado).*

---

## Qué incluye el proyecto

- Desarrollo completo de los módulos detallados por etapa
- Pruebas funcionales internas antes de cada entrega
- Puesta en marcha y configuración inicial en el servidor
- Ajustes menores dentro del alcance durante la puesta en marcha
- Integración con AFIP/ARCA para facturación electrónica (Factura A y B)
- Integración con WhatsApp Business Cloud API con reconocimiento del anuncio de origen
- PDF de presupuestos y comprobantes fiscales
- Sistema accesible desde computadora y celular

## Qué no está incluido

- Aplicación móvil nativa (iOS / Android)
- Tienda online o e-commerce con carrito de compras
- Integración con sistemas contables externos (Tango, Bejerman u otros)
- Coordinación de envíos con transportistas (OCA, Andreani u otros)
- Migración de datos desde Contagram u otro sistema anterior
- Múltiples locales o puntos de venta
- Cambios de alcance posteriores al inicio (se cotizan aparte)

---

## Lo que necesitamos de tu parte

**Antes de comenzar la Etapa 1:**

1. **Certificado digital AFIP/ARCA** — se tramita en el portal de AFIP con el CUIT del negocio. Te guiamos en el proceso cuando acordemos el inicio.

**Antes de comenzar la Etapa 2:**

2. **Número de teléfono dedicado para el bot** — número exclusivo para el sistema, distinto del número personal del negocio. Puede ser una SIM adicional.
3. **Listado de categorías del catálogo** — para configurar las preguntas de calificación del bot por categoría.

---

## Condiciones comerciales

- Forma de pago: 50% al inicio y 50% a la entrega de cada etapa
- Moneda: USD
- Cambio de alcance disponible en cualquier momento si el proyecto crece (se cotiza aparte)

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
