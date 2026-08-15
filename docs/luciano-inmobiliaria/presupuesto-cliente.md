# Olvidata**Soft**

---

**Propuesta de desarrollo — API de facturación electrónica multi-tenant para Luciano Inmobiliaria**
**OlvidataSoft · Agosto 2026**

---

## Sobre el sistema

Una API que tu SaaS consume para emitir comprobantes electrónicos ARCA en nombre de tus ~100 CUIT, sin que tengas que construir ni mantener vos la integración con ARCA.

- Tu plataforma le manda los datos del comprobante a nuestra API (individual o en lote), recibe la confirmación de que quedó en cola, y consulta el resultado (CAE o motivo de rechazo) cuando quiera — sin límite de tamaño de lote.
- Un mismo cliente puede tener varios CUIT bajo una sola cuenta, y cada CUIT puede tener varios puntos de venta, cada uno con su propia credencial de acceso.
- Vos administrás tus propios certificados de firma digital — los publicás en una carpeta compartida con nosotros (nombrada por CUIT) y el sistema los toma automáticamente, sin que tengas que subir nada por una pantalla.
- El sistema controla el volumen de facturación de cada punto de venta contra lo que declaraste al contratar, con señales adicionales para detectar patrones de uso fuera de lo esperado.
- Como rama aparte, sumamos la posibilidad de que tu equipo suba un PDF de contrato y la IA te devuelva los datos extraídos para autocompletar el formulario de tu propio sistema.

*Es un desarrollo exclusivamente de backend — no hay pantallas de nuestro lado, todo se integra por API contra tu SaaS.*

---

## Cómo funciona la ingesta de certificados

**1. Publicás el certificado.** Subís el archivo `.p12` a la carpeta compartida, nombrado con el CUIT correspondiente (ej. `30123456789.p12`).
**2. El sistema lo detecta solo.** Un proceso revisa la carpeta periódicamente, valida el certificado contra ARCA y lo deja listo para firmar — sin que tengas que avisarnos.
**3. Queda disponible para facturar.** Ese CUIT ya puede emitir comprobantes a través de la API.
**4. Si algo falla, te avisamos.** La vigencia del certificado es responsabilidad tuya — nosotros no hacemos seguimiento proactivo de vencimiento. Si en algún momento ARCA rechaza un certificado (vencido o inválido), te mandamos un mail automático con el CUIT afectado para que lo corrijas.

*Detalle a confirmar entre nuestros equipos: la forma exacta en que viaja la contraseña del certificado dentro de la misma carpeta — te la proponemos apenas arrancamos, no bloquea el resto del desarrollo.*

---

## Cómo funciona la extracción de contratos por IA

**1. Tu usuario carga el PDF.** Desde tu propio frontend, no el nuestro.
**2. Nuestra API lo procesa.** Lo analiza con inteligencia artificial y devuelve los datos del contrato en un formato estructurado (partes, inmueble, montos, fechas).
**3. Vos decidís cómo mostrarlo.** El resultado autocompleta el formulario de tu sistema — el usuario siempre revisa y confirma antes de guardar, la IA no carga nada sola.

*Este módulo tiene un costo de uso variable (según cantidad de PDFs procesados) además del desarrollo — lo conversamos para definir si se cobra por PDF o se incluye un tope dentro de tu plan, según cómo prefieras manejarlo.*

---

## Dos formas de trabajar juntos

Nos preguntaste si el código queda de nuestro lado (como servicio) o si te lo podemos entregar. Las dos son posibles — con una lógica de precio distinta cada una, según lo que implica para cada parte:

### Opción A — Nosotros alojamos y operamos la API (SaaS)

| Concepto | USD |
|---|---:|
| Desarrollo (pago único) | 950 |
| Suscripción anual (hasta 100 CUIT) | 750/año — **primer año incluido, sin cargo** |

Vos consumís la API, nosotros la mantenemos, la actualizamos y respondemos si algo falla. Es el modelo más simple operativamente de tu lado.

### Opción B — Te entregamos el código fuente

| Concepto | USD |
|---|---:|
| Desarrollo + transferencia completa del código | 2.250 |

Alojás y operás tu propia instancia, sin depender de nosotros después de la entrega. Este precio incluye la cesión del desarrollo completo — no es una suscripción recurrente, es pago único.

*Condiciones distintas de la Opción A: 70% al inicio / 30% a la entrega, y una cláusula de uso exclusivo por un período acordado antes de que el código quede completamente libre de restricciones — te la acercamos junto con la propuesta formal.*

---

## Rol de usuario

| Actor | Acceso |
|---|---|
| Tu SaaS (por punto de venta) | Emite y consulta comprobantes del punto de venta correspondiente a su credencial — no ve datos de otros CUIT. |
| Tu sistema (credencial administrativa) | Da de alta tus propios CUIT y puntos de venta por API, sin depender de que lo hagamos nosotros manualmente. |

*El control de uso (monitoreo de volumen de facturación) queda de nuestro lado como proveedor — es la única parte de la administración que no se expone a tu sistema.*

---

## Qué incluye el desarrollo (ambas opciones)

- Emisión de comprobantes ARCA individual y en lote, con manejo de honorarios/alquileres (incluida la facturación en nombre de terceros, que exige la normativa vigente para administración de alquileres).
- Multi-CUIT bajo una sola cuenta, con múltiples puntos de venta por CUIT.
- Ingesta automática de certificados desde carpeta compartida, sin pantalla de carga.
- Control de uso con detección de patrones de facturación fuera de lo esperado.
- Extracción de datos de contrato desde PDF con IA.
- Guía técnica de integración para tu equipo (incluye el contrato exacto de request/response de cada endpoint).

## Qué no está incluido

- Costo variable de uso de la extracción por IA (se conversa aparte, ver arriba).
- Notas de crédito/débito, historial de comprobantes como endpoint de reportería, y notificación automática de vencimiento de certificado — no confirmados en este alcance, se cotizan aparte si los necesitás.
- Desarrollo o modificación de tu propio SaaS — nuestra API se integra con lo que ya tenés.
- Migración de datos de facturación históricos.

---

## Lo que necesitamos de tu parte

- Confirmar a qué te referís exactamente con "sueldos" como tipo de comprobante — investigamos y no encontramos que sea parte de la facturación electrónica estándar (es un sistema distinto de ARCA, el de recibos de sueldo digital) — puede que te refieras a otra cosa, como honorarios de administración.
- Volumen esperado de facturas por mes, por punto de venta (para calibrar el control de uso sin que te quede corto).
- Confirmar el tamaño típico de un lote cuando facturás varios comprobantes juntos.
- Acceso/coordinación para definir la carpeta compartida de certificados con tu equipo técnico.
- Si avanzamos con la Opción B, coordinar con tu asesor legal la cláusula de uso exclusivo antes de la entrega.

---

## Condiciones comerciales

- **Opción A**: desarrollo 50% al inicio / 50% a la entrega; suscripción con el primer año incluido sin cargo adicional, facturada anualmente desde el segundo año.
- **Opción B**: 70% al inicio / 30% a la entrega; sin suscripción recurrente.
- Moneda: USD, pagadero en pesos al tipo de cambio del día.
- Cambio de alcance disponible en cualquier momento si el proyecto crece — se cotiza aparte.

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
