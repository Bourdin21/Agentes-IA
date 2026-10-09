# Olvidata**Soft**

---

**La Platense — Cómo habilitar la facturación electrónica**

**OlvidataSoft · Octubre 2026**

## Sobre este instructivo

El sistema ya tiene toda la facturación construida y probada. Para que las facturas salgan con número oficial de AFIP falta un trámite que **solo podés hacer vos**, porque requiere entrar con tu Clave Fiscal: nadie más puede hacerlo en tu nombre.

Son **cinco pasos en el sitio de AFIP** y me tenés que mandar tres cosas al final. Calculá entre 30 y 45 minutos si tenés la Clave Fiscal a mano. El trámite no tiene costo.

**El trabajo está repartido así:** yo preparo un archivo y te lo mando; vos lo subís a AFIP y descargás lo que AFIP te devuelve; me lo mandás y yo lo cargo en el sistema. **No necesitás entender ninguno de los archivos** — alcanza con subir el que te doy y bajar el que AFIP te da.

*Una aclaración de nombres: AFIP ahora se llama **ARCA**. Vas a ver los dos nombres mezclados en el sitio y en los mails que te lleguen. Es el mismo organismo y el mismo trámite.*

## Antes de empezar: lo que tenés que tener

- **Clave Fiscal con nivel de seguridad 3.** Es el nivel que se obtiene validando identidad (con huella en una dependencia, o por homebanking desde tu banco). Si entrás al sitio de AFIP y podés ver tus comprobantes, lo más probable es que ya lo tengas. Si no, ese trámite va primero.
- **El CUIT de la ferretería** y la clave con la que entrás al sitio.
- **Un archivo que te voy a mandar yo** por mail o WhatsApp, con extensión `.csr`. Es un pedido de certificado: no tiene información sensible y no sirve para nada fuera de este trámite.

**Esperá a que te mande ese archivo antes de arrancar el paso 2.** Avisame y te lo preparo en el momento.

## Paso a paso en el sitio de AFIP

**1. Entrá con tu Clave Fiscal.** Andá a `www.afip.gob.ar`, entrá con CUIT y clave, y vas a caer en el listado de servicios que tenés habilitados.

**2. Habilitá el servicio de certificados digitales.** Si no lo ves en tu lista de servicios, hay que agregarlo: buscá la opción para administrar o adherir servicios y agregá **"Administración de Certificados Digitales"**. Es gratis y queda disponible al instante.

*Si no encontrás ese nombre exacto, mandame una captura de pantalla de tu listado de servicios y te marco dónde está. El sitio cambió de nombres varias veces y no vale la pena que pierdas tiempo adivinando.*

**3. Subí el archivo que te mandé y descargá tu certificado.** Entrá a "Administración de Certificados Digitales" y elegí la opción de crear un certificado nuevo (suele decir "Agregar alias"). Te va a pedir dos cosas:

   - Un **alias**: es un nombre interno para identificar este certificado. Poné algo que reconozcas, por ejemplo `sistema-laplatense`. No importa cuál elijas, pero **anotá el que pusiste** y mandámelo.
   - El **archivo `.csr`** que te mandé: lo subís tal cual, sin abrirlo ni modificarlo.

   Al confirmar, AFIP te deja descargar un archivo con extensión **`.crt`** (o `.pem`). **Ese archivo es el certificado y es lo primero que necesito.** Guardalo y mandámelo.

**4. Autorizá al certificado a facturar.** Este paso es el que más se saltea, y sin él el certificado existe pero no sirve. Hay que decirle a AFIP que ese certificado tiene permiso para usar el servicio de facturación.

   Entrá a **"Administrador de Relaciones de Clave Fiscal"** y creá una relación nueva. Cuando te pida el servicio, buscá **"Facturación Electrónica"** (en algunos listados aparece como "Web Services" o "WSFE"). Cuando te pida quién va a usar ese servicio, elegí el **alias que creaste en el paso 3**.

**5. Dá de alta un punto de venta para el sistema — y acá hay una trampa.** AFIP distingue entre el punto de venta que usás para facturar a mano desde su propio sitio y el que usa un sistema externo. **Son cosas distintas aunque el número se vea igual en la factura impresa.**

   Entrá a **"Comprobantes en línea"** y buscá la administración de puntos de venta (suele estar como "ABM de Puntos de Venta"). Creá uno nuevo y, cuando te pida el tipo o el sistema, elegí:

   > **RECE para aplicativo y web services**

   **No elijas "Factura en Línea — Responsable Inscripto".** Es la opción que está al lado y la que parece correcta, pero es la del sitio de AFIP para facturar a mano. Es la confusión más común de este trámite y la vimos pasar en vivo.

   Anotá el **número de punto de venta** que te quedó asignado (puede ser 2, 5, 7… el que AFIP te dé) y mandámelo.

## Lo que necesito de tu parte al terminar

Tres cosas, y con eso cargo todo y probamos:

1. **El archivo `.crt`** que descargaste en el paso 3.
2. **El número de punto de venta** del paso 5, y el **alias** que usaste en el paso 3.
3. **Una foto o un PDF de una factura real tuya**, de las que ya emitís hoy. La necesito para copiar **exactamente** cómo figuran tu razón social, tu domicilio comercial, tu condición frente al IVA, tu número de Ingresos Brutos y tu fecha de inicio de actividades. Esos datos van impresos en cada factura que emita el sistema, y los quiero tomar de un comprobante real en vez de adivinarlos: si alguno sale distinto de lo que AFIP tiene registrado, la factura queda mal.

*El certificado tiene vencimiento, normalmente dos años. Cuando se acerque la fecha te aviso y repetimos los pasos 2 y 3 — los pasos 4 y 5 no hace falta rehacerlos.*

## Qué pasa después

**1. Cargo el certificado y configuro el sistema.** Es trabajo mío y no te toma tiempo.

**2. Emitimos una factura de prueba juntos.** Acá hay algo importante que quiero que sepas de antemano: **una factura electrónica con número oficial no se puede borrar.** Si sale mal, la forma de corregirla es emitir una nota de crédito, que el sistema ya tiene. Por eso la primera la hacemos juntos, sobre una venta real y chica, mirando los dos la pantalla.

**3. Verificamos contra el sitio de AFIP.** La factura que emita el sistema tiene que aparecer en tu listado de "Comprobantes en línea" con el mismo número. Si aparece ahí, está realmente emitida y el circuito quedó cerrado.

## Si algo no sale

No insistas ni pruebes opciones al azar, sobre todo en el paso 5: mandame una captura de la pantalla donde te trabaste y te digo qué tocar. La mayoría de los errores de este trámite son de configuración en AFIP y se resuelven en minutos **si se sabe cuál de los cinco pasos quedó a medias** — adivinando se pierden días.

---

**Olvidata Soft — bourdinjoaquin@gmail.com**
