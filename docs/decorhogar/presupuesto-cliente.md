# Propuesta de desarrollo — Sistema de Gestión y Ventas
**OlvidataSoft · Junio 2026**

---

## Sobre el sistema

Desarrollamos un sistema de gestión integral para tu negocio de decoración y hogar que reemplaza el proceso actual y automatiza el canal de ventas desde el primer contacto hasta la entrega.

El sistema cubre todo el ciclo:

- Un cliente ve tu publicación de un producto en Instagram o Facebook y escribe al WhatsApp del negocio
- El sistema identifica automáticamente qué producto vio en el anuncio y hace preguntas de calificación específicas (ambiente, medidas, color, etc.)
- El vendedor retoma desde el sistema con toda esa información, envía un presupuesto en PDF y convierte la consulta en venta
- La venta se registra con sus productos, formas de pago y estado
- Si hay entrega a domicilio, el vendedor la gestiona y cobra desde el celular
- El sistema emite la factura electrónica contra AFIP y genera el PDF del comprobante

---

## Roles de usuario

| Rol | Accesos |
|---|---|
| **Administrador** | Acceso total: catálogo, precios, stock, ventas, reportes, usuarios y configuración |
| **Vendedor** | Gestión de contactos, presupuestos, ventas y entregas. No accede a precios, reportes financieros ni configuración |

---

## Etapa 1 — El negocio operando en el sistema

Todo lo necesario para reemplazar el sistema actual y empezar a operar desde el día uno.

### Usuarios y accesos
Gestión de usuarios del sistema con sus roles (Administrador y Vendedor). Alta, edición, baja y restablecimiento de contraseña. Cada usuario accede únicamente a las funciones que le corresponden.

### Catálogo de productos
Alta, edición y baja de productos con nombre, descripción, precio, categoría y hasta 5 fotos por producto. El catálogo es la base de los presupuestos, las ventas y el bot de WhatsApp.

### Control de stock
El sistema descuenta el stock automáticamente con cada venta cerrada. El Administrador registra entradas de mercadería. Alerta visual cuando un producto cae por debajo del stock mínimo configurado.

### Presupuestos y cotizaciones
El vendedor elige productos y cantidades, el sistema calcula el total y genera un PDF con los datos del negocio. Una vez aprobado por el cliente, se convierte en venta con un clic, sin recargar datos.

### Gestión de ventas
Registro de ventas con líneas de productos y cantidades. Acepta múltiples formas de pago por venta (efectivo, transferencia, tarjeta o MercadoPago en cualquier combinación). El sistema valida que el total cobrado coincida antes de confirmar.

### Entregas a domicilio
Programación de entregas con dirección, fecha estimada y vendedor asignado. El vendedor registra el cobro y cierra la entrega desde el celular en el domicilio del cliente.

### Facturación electrónica AFIP
El sistema emite facturas electrónicas directamente contra AFIP (Factura A o B). Genera el CAE y produce el PDF del comprobante. Renueva la autenticación con AFIP automáticamente.

| Área funcional | USD |
|---|---:|
| Usuarios y accesos | USD 84 |
| Catálogo de productos | USD 118 |
| Control de stock | USD 134 |
| Presupuestos y cotizaciones | USD 151 |
| Gestión de ventas | USD 202 |
| Entregas a domicilio | USD 118 |
| Facturación electrónica AFIP | USD 118 |
| **Subtotal desarrollo Etapa 1** | **USD 925** |
| **Tokens IA** | **USD 100** |
| **Subtotal Etapa 1** | **USD 1.025** |

---

## Etapa 2 — Automatización por WhatsApp y métricas

### Atención automática por WhatsApp — reconocimiento de anuncio
Cuando un cliente hace clic en uno de tus anuncios de Meta y escribe al WhatsApp del negocio, el sistema detecta automáticamente qué producto vio en el anuncio. No necesita preguntarle qué le interesa — ya lo sabe.

En cambio, hace preguntas de calificación específicas según el producto:

- **Muebles / Sillones:** ¿Para qué ambiente? ¿Medidas disponibles? ¿Preferencia de color o material?
- **Iluminación:** ¿Interior o exterior? ¿Ambiente? ¿Necesita instalación?
- **Textiles / Cortinas:** ¿Medidas de la ventana? ¿Color o estilo?
- *(Se configura una vez por categoría según tu catálogo)*

Todas las respuestas quedan guardadas en el perfil del contacto. Cuando el vendedor retoma la conversación desde el panel, ya tiene el producto, la categoría y las necesidades del cliente sin haber intervenido.

El sistema también registra desde qué anuncio llegó cada contacto, lo que permite ver en el dashboard qué publicaciones generan más ventas.

### Seguimiento de contactos (CRM)
Panel con todos los contactos generados por WhatsApp. Cada uno muestra el producto consultado, el anuncio de origen, el estado de la conversación (nuevo, contactado, presupuesto enviado, vendido, perdido), historial y vendedor asignado.

### Panel de métricas
Contactos captados por período, tasa de conversión por producto y por anuncio, ventas totales, productos más vendidos y stock crítico. Con filtro de fechas.

| Área funcional | USD |
|---|---:|
| Atención automática por WhatsApp | USD 118 |
| Seguimiento de contactos (CRM) | USD 134 |
| Panel de métricas | USD 101 |
| **Subtotal Etapa 2** | **USD 353** |

---

## Total del proyecto

| Concepto | USD |
|---|---:|
| Etapa 1 | USD 1.025 |
| Etapa 2 | USD 353 |
| Subtotal | USD 1.378 |
| **Descuento por referido (15%)** | **− USD 207** |
| **Total proyecto** | **USD 1.171** |

---

## Mantenimiento anual

El mantenimiento cubre el servidor, las actualizaciones de seguridad y el soporte técnico. No incluye cambios funcionales nuevos (se cotizan por separado).

| Plan | Incluye | USD/año |
|---|---|---:|
| **PREMIUM** | Hasta 3 usuarios, soporte prioritario por WhatsApp, 2 rondas de ajuste al año | **USD 400** |

---

## Qué está incluido

- Desarrollo completo de los módulos detallados por etapa
- Pruebas funcionales internas antes de cada entrega
- Puesta en marcha y configuración inicial en el servidor
- Ajustes menores dentro del alcance durante la puesta en marcha
- Integración con AFIP para facturación electrónica (Factura A y B)
- Integración con WhatsApp Business Cloud API con reconocimiento de anuncio de origen
- PDF de presupuestos y comprobantes fiscales
- Sistema accesible desde computadora y celular

## Qué no está incluido

- Aplicación móvil nativa (iOS / Android)
- Tienda online o e-commerce con carrito de compras
- Integración con sistemas contables externos (Tango, Bejerman u otros)
- Coordinación de envíos con transportistas (OCA, Andreani u otros)
- Migración de datos desde el sistema anterior
- Múltiples locales o puntos de venta
- Cambios de alcance posteriores al inicio (se cotizan aparte)

---

## Lo que necesitamos de tu parte

**Antes de comenzar la Etapa 1:**

1. **Certificado digital AFIP** — se tramita en el portal de AFIP con el CUIT del negocio. Te guiamos en el proceso cuando acordemos el inicio.

**Antes de comenzar la Etapa 2:**

2. **Número de teléfono dedicado para el bot** — número exclusivo para el sistema, distinto del número personal del negocio. Puede ser una SIM adicional.
3. **Listado de categorías del catálogo** — para configurar las preguntas de calificación del bot por categoría.

---

## Condiciones comerciales

- **Forma de pago:** 50% al inicio y 50% a la entrega de cada etapa
- **Moneda:** USD
- Las etapas se pueden contratar de forma independiente
- Los cambios de alcance solicitados después del inicio se presupuestan y acuerdan por separado
