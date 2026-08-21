# Olvidata**Soft**
---

**marihogar — Cómo habilitar un Punto de Venta para Facturación Electrónica (Web Service)**
**OlvidataSoft · Agosto 2026**

## Por qué hace falta esto

El sistema ya se conecta correctamente con AFIP (certificado, login y firma digital funcionando). Al intentar facturar, AFIP respondió que **no tenés ningún Punto de Venta habilitado para el Web Service de Facturación Electrónica** — el Punto de Venta 4 que ves en tus facturas es el que usás para facturar manualmente desde la web de AFIP, pero eso es un tipo de punto de venta distinto al que necesita un sistema externo (como MariHogar) para facturar automáticamente. Hay que dar de alta uno nuevo, específicamente del tipo "Web Service".

## Paso a paso

**1. Entrá a AFIP con tu Clave Fiscal.** Andá a [www.afip.gob.ar](https://www.afip.gob.ar) (o [www.arca.gob.ar](https://www.arca.gob.ar), el nuevo nombre del organismo) e iniciá sesión con tu CUIT y Clave Fiscal.

**2. Buscá el servicio "Administrador de Puntos de Venta y Domicilios".** En la pantalla principal, usá el buscador de servicios (lupa o "Todos los servicios") y escribí "Puntos de Venta". Si no lo tenés adherido a tu usuario, primero hay que adherirlo desde "Administrador de Relaciones de Clave Fiscal" (buscalo de la misma forma) — ahí se agregan servicios nuevos a tu usuario.

**3. Entrá a "ABM de Puntos de Venta y Domicilios".** Dentro del administrador, vas a ver el o los puntos de venta que ya tenés (entre ellos el 4, que usás para facturar manual). Buscá la opción para **agregar uno nuevo**.

**4. Completá el alta con estos datos:**
   - **Número de punto de venta:** el sistema suele sugerir el siguiente disponible (probablemente el 5, pero puede variar).
   - **Sistema:** elegí la opción de **"Factura Electrónica" / "Web Services"** (a veces aparece como "WSFE" o "Comprobantes en línea (Web Service)") — es importante que sea la variante para conexión automática por sistema, **no** "Manual", "Preimpreso" ni "Facturador Móvil".
   - **Domicilio:** el que corresponda a tu local (el mismo que ya tenés registrado para el punto de venta 4 sirve).

**5. Confirmá el alta.** Puede tardar unos minutos en quedar activo del lado de AFIP.

**6. Avisanos el número que te asignó AFIP.** Una vez que tengas el número nuevo (o si AFIP te permite habilitar el 4 para este uso, ese mismo), decinos cuál es — nosotros actualizamos la configuración del sistema con ese número y volvemos a probar la emisión de una factura real.

## Importante

*Los nombres exactos de las opciones pueden variar levemente según la versión actual del portal de AFIP/ARCA (están migrando gradualmente el sitio a la marca "ARCA") — la idea general (dar de alta un punto de venta nuevo, tipo Web Service, para uso de un sistema externo) es la que hay que seguir. Si en algún paso no encontrás la opción exacta, decinos qué ves en pantalla y te ayudamos a ubicarla.*

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
