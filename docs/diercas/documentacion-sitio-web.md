# Documentación del sitio web — diercas.com.ar

**Cliente:** Diercas SA
**Desarrollo:** Olvidata Soft
**Fecha:** 24 de agosto de 2026
**Estado:** Etapa 1 completa y en producción

---

## 1. Qué es el sitio

Sitio institucional de Diercas SA, con 5 páginas: Inicio, Nosotros, Servicios, Clientes y Contacto. Presenta a la empresa, sus tres ramas de servicio y su cartera de clientes (organismos públicos y empresas privadas), con un formulario para que un visitante inicie el contacto comercial.

Es un sitio **estático**: no tiene panel de administración ni base de datos. El contenido (textos, servicios, lista de clientes) vive en el código del sitio; cualquier cambio de contenido lo aplica Olvidata Soft y se publica con un nuevo despliegue. La única parte "viva" del sitio es el formulario de contacto, que envía un mail real por SMTP a `administracion@diercas.com.ar`.

## 2. Páginas del sitio

| Página | URL | Contenido |
|---|---|---|
| Inicio | `/` | Presentación general de Diercas, las tres ramas de servicio y llamado a la acción |
| Nosotros | `/nosotros` | Quiénes son, sectores en los que trabajan, certificaciones |
| Servicios | `/servicios` | Las tres ramas: Infraestructura (destacada como principal), Provisión de equipos e insumos, e Infraestructura de eventos |
| Clientes | `/clientes` | Cartera de clientes agrupada en Sector Público y Sector Privado |
| Contacto | `/contacto` | Formulario de consulta + datos de contacto directo (teléfono, WhatsApp, email) |

## 3. Formulario de contacto — cómo funciona

Cuando un visitante completa y envía el formulario de `/contacto`:

1. Los datos viajan al servidor por una conexión cifrada.
2. El servidor arma un mail con el detalle de la consulta y lo envía por SMTP a **administracion@diercas.com.ar**, con el email del visitante como "responder a" — así se le puede contestar directo desde el mismo hilo de correo.
3. El visitante ve la confirmación de "consulta enviada" **de forma prácticamente instantánea** (menos de 200 milisegundos). Esto es el resultado de una mejora aplicada específicamente para este formulario: el envío de mail en sí (la conversación con el servidor de correo) puede demorar varios segundos por medidas de seguridad antispam propias de ese servidor — el sitio ya no hace esperar al visitante ese tiempo, responde al instante y el envío se completa por detrás. El detalle técnico completo de esta mejora está en `comparativa-hosting-donweb-vs-hostinger.md`, Resultado 3.

**Seguridad de las credenciales**: la contraseña de la casilla SMTP que usa el formulario está cifrada en el servidor (AES-256-GCM) y la clave de cifrado no es accesible públicamente ni desde el navegador — solo el código del servidor puede leerla, en el momento de enviar el mail.

## 4. Hosting y dominio

- **Decisión final (2026-08-25): el hosting es Hostinger, administrado directamente por Diercas** — no se usa DonWeb en este proyecto. Se había probado DonWeb en paralelo para comparar rendimiento (detalle en `comparativa-hosting-donweb-vs-hostinger.md`, DonWeb resultaba ~3x más rápido en esas pruebas), pero la decisión de negocio del cliente fue quedarse con Hostinger.
- El formulario de contacto ya envía desde una casilla propia de Diercas (`no-reply@diercas.com.ar`, vía el SMTP de Hostinger) — ya no depende de ninguna credencial de Olvidata.
- **Pendiente del lado del cliente**: el dominio `diercas.com.ar` todavía apunta al sitio anterior (WordPress). Para que el sitio nuevo quede visible en `https://diercas.com.ar` hace falta delegar el DNS del dominio hacia el hosting de Hostinger — este paso lo tiene que ejecutar Diercas desde su propio panel de Hostinger (hPanel), ya no es una tarea de Olvidata. Una vez delegado, Hostinger emite el certificado SSL (candado/https) automáticamente.

## 5. Actualización de contenido

Como el sitio es estático, actualizar contenido (textos, agregar un cliente nuevo, cambiar un logo, sumar una rama de servicio) es un cambio de código que hace Olvidata Soft y se vuelve a publicar — no hay un panel donde el cliente edite directamente. Algunos puntos a tener en cuenta:

- **Clientes / logos**: cada cliente de la sección "Nuestros clientes" es un registro independiente (nombre, logo, si es sector público o privado). Agregar, sacar o reordenar un cliente es un cambio simple y rápido de pedir.
- **Servicios**: las tres ramas actuales (Infraestructura, Provisión de equipos, Infraestructura de eventos) corresponden a lo confirmado para esta primera etapa. El dossier de marca contempla además Ciberseguridad y Audio/Video como posibles ramas futuras — quedaron **fuera de esta etapa a pedido explícito del cliente**, para sumarlas más adelante si se decide.

## 6. Pendientes (Etapa 2 / a cargo del cliente)

Estos puntos no bloquean el sitio actual, pero están anotados para una próxima etapa:

- **Logos reales de clientes** que todavía no se recibieron (se muestran con el nombre en texto mientras tanto).
- ~~QR de Data Fiscal (ARCA/AFIP)~~ — recibido y ya publicado en la sección de Certificaciones de `/nosotros`.
- **Delegación de DNS** de `diercas.com.ar` hacia DonWeb (ver punto 4).
- **Página "Trabajos realizados"** — contenido todavía no definido por el cliente.
- Bloques de **Ciberseguridad** y **Audio y Video** en `/servicios`, si se confirma sumarlos.

## 7. Soporte

Cualquier cambio de contenido, incidente o consulta técnica sobre el sitio se canaliza a través de **Olvidata Soft** (desarrollador del sitio, crédito visible en el pie de página).
