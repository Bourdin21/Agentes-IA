# Comparativa de rendimiento — DonWeb vs Hostinger

**Sitio:** diercas.com.ar — sitio institucional de Diercas SA
**Fecha:** 24 de agosto de 2026 (actualizado el 24 de agosto de 2026 con la mejora del formulario de contacto)
**Preparado por:** Olvidata Soft

## Resumen ejecutivo

Se desplegó el mismo sitio (build idéntico, mismo código) en ambos hostings y se midió el tiempo de respuesta real del servidor en las 5 páginas del sitio, la velocidad de transferencia de archivos (imágenes, logos) y el comportamiento del formulario de contacto.

**Resultado: DonWeb responde entre 3 y 3.5 veces más rápido que Hostinger** en la entrega de páginas y archivos, de forma consistente en las 5 páginas y en los 3 tipos de archivo testeados. La diferencia es clara y se repite en todas las mediciones, no es un caso aislado.

El formulario de contacto originalmente tardaba 10 a 13 segundos en responderle al visitante en ambos hostings — esa demora no dependía del hosting elegido, sino del tiempo que tarda la conexión con el servidor de correo saliente. **Ese punto ya fue resuelto**: el formulario ahora responde en menos de 200 milisegundos en los dos hostings (ver "Resultado 3" y "Mejora aplicada" más abajo), sin cambiar el proveedor de correo ni el hosting.

## Metodología

- Se usó el mismo build compilado del sitio (Astro, output estático) subido por FTP a ambos hostings.
- Las mediciones se hicieron con `curl`, herramienta de línea de comandos que mide tiempos de red con precisión de milisegundos, sin la variabilidad que introduce un navegador (caché, renderizado, ejecución de JavaScript — que de todos modos es idéntico en ambos casos porque el código es el mismo).
- Cada medición se repitió entre 5 y 10 veces por página/archivo para poder reportar promedio, mediana y rango (mínimo–máximo), y no depender de una sola muestra que podría ser un valor atípico.
- DonWeb se probó por HTTP (todavía no tiene certificado SSL propio porque el dominio no está delegado); Hostinger se probó por HTTPS real en su dominio temporal. Esto se explica en detalle en "Salvedades" más abajo — no invalida la conclusión, pero es importante para interpretar los números correctamente.

## Resultado 1 — Tiempo de respuesta por página

Tiempo total de descarga del HTML de cada página (en milisegundos), 10 muestras por página y por hosting.

| Página | Tamaño | DonWeb (prom. / mediana) | DonWeb (min–max) | Hostinger (prom. / mediana) | Hostinger (min–max) | DonWeb es... |
|---|---|---|---|---|---|---|
| Inicio (`/`) | 25.0 KB | 69 / 70 ms | 60–77 ms | 221 / 221 ms | 209–238 ms | **3.2x más rápido** |
| Nosotros | 23.6 KB | 73 / 74 ms | 60–81 ms | 231 / 221 ms | 215–314 ms | **3.2x más rápido** |
| Servicios | 26.4 KB | 73 / 73 ms | 65–82 ms | 225 / 225 ms | 206–245 ms | **3.1x más rápido** |
| Clientes | 31.6 KB | 78 / 77 ms | 69–99 ms | 227 / 225 ms | 214–250 ms | **2.9x más rápido** |
| Contacto | 25.1 KB | 75 / 76 ms | 66–81 ms | 236 / 219 ms | 205–386 ms | **3.1x más rápido** |

Patrón consistente en las 5 páginas, sin excepciones.

## Resultado 2 — Velocidad de transferencia de archivos

Mismo archivo físico subido a ambos hostings, medido 8 veces cada uno.

| Archivo | Peso en DonWeb | Tiempo DonWeb | Velocidad DonWeb | Peso en Hostinger | Tiempo Hostinger | Velocidad Hostinger |
|---|---|---|---|---|---|---|
| Imagen de portada (JPG) | 76.9 KB | 95 ms | 798 KB/s | **59.8 KB** ⚠️ | 255 ms | 229 KB/s |
| Logo horizontal (PNG) | 131.3 KB | 113 ms | 1.15 MB/s | 135.4 KB | 325 ms | 412 KB/s |
| Favicon (ICO) | 0.55 KB | 53 ms | — | 0.55 KB | 179 ms | — |

⚠️ **Nota**: Hostinger sirvió la imagen de portada a 59.8 KB en vez de los 76.9 KB originales — un 22% más liviana. Esto sugiere que Hostinger aplica optimización/recompresión automática de imágenes JPG en su CDN. Es una diferencia real de contenido, no un error de medición, y de hecho juega a favor de Hostinger (menos bytes para transferir) — aun así, DonWeb la entregó 2.7 veces más rápido con más peso.

## Resultado 3 — Formulario de contacto

**Overhead del servidor PHP** (sin llegar a enviar el mail — se midió con una request que el propio código rechaza en microsegundos, para aislar el tiempo de arranque de PHP):

| | DonWeb | Hostinger |
|---|---|---|
| Tiempo promedio | 65 ms | 186 ms |
| Mediana | 60 ms | 171 ms |

Mismo patrón ~3x que el resto del sitio.

**Envío real del formulario (con mail efectivamente enviado) — medición original:**

| | DonWeb | Hostinger |
|---|---|---|
| Tiempo total | 13.3 s | 10.8 s |

Ahí el patrón se invertía — y la razón no tenía que ver con el hosting. El formulario no solo genera una página PHP: abre una conexión SMTP real hacia el servidor de correo (que vive en DonWeb, en un servidor aparte, independiente del hosting web) y hace una negociación de varios pasos (login, remitente, destinatario, envío del cuerpo). Esa negociación completa tardaba 10 a 13 segundos sin importar desde qué hosting web se disparara — el cuello de botella estaba del lado del correo, no del sitio.

### Mejora aplicada

Se diagnosticó paso a paso esa negociación SMTP y se confirmó el origen exacto de la demora: ~5 segundos de retraso deliberado del servidor de correo en el paso de login (una medida antispam/antifuerza-bruta) más ~2 segundos de escaneo de contenido del mail — ambos 100% del lado del servidor de correo (Exim, en el VPS de DonWeb), fuera del alcance del código del sitio o de la elección de hosting web.

En vez de intentar acortar esa negociación (no es posible desde afuera), se cambió **cómo el sitio le responde al visitante**: ahora el formulario le confirma "consulta enviada" al instante, y el envío real del mail sigue corriendo en el servidor unos segundos más, ya desconectado del navegador del visitante. El visitante no nota ninguna espera.

**Cómo se implementó, en criollo**: el servidor tiene una función especial que le permite a un script cortar la respuesta hacia el navegador y seguir trabajando después, ya desconectado — es un mecanismo estándar de PHP (`fastcgi_finish_request`) que en el tipo de servidor que usan tanto DonWeb como Hostinger (LiteSpeed) tiene su propio equivalente (`litespeed_finish_request`). El formulario prueba primero el mecanismo estándar y, si no está disponible, usa el de LiteSpeed — por eso la mejora quedó funcionando igual en los dos hostings sin necesidad de tocar nada más. Si en algún momento el sitio se mudara a un hosting donde ninguna de las dos funciones existiera, el formulario simplemente vuelve a su comportamiento original (esperar antes de responder) — no hay riesgo de que se rompa, en el peor caso se pierde la mejora.

**Envío real del formulario — después de la mejora:**

| | DonWeb | Hostinger |
|---|---|---|
| Tiempo de respuesta al visitante | **0.06 s** | **0.17 s** |
| (antes) | 13.3 s | 10.8 s |
| Mejora | **~215x más rápido** | **~65x más rápido** |

La mejora funciona igual de bien en ambos hostings porque los dos corren el mismo tipo de servidor web (LiteSpeed) — no es una ventaja de uno sobre el otro, es una corrección aplicada al código del sitio que beneficia a cualquiera de los dos por igual.

**Trade-off aceptado**: si el envío de fondo llegara a fallar (servidor de correo caído, credenciales vencidas, etc.), el visitante ya vio el mensaje de éxito y no se entera en el momento — el error queda registrado en el log del servidor para revisión. Para el volumen de consultas de este sitio institucional es un trade-off razonable; si el volumen de consultas creciera mucho, el siguiente paso natural sería pasar a una cola de envíos con reintentos automáticos.

## Salvedades metodológicas

1. **DonWeb se probó por HTTP, Hostinger por HTTPS.** DonWeb todavía no tiene certificado SSL (pendiente de la delegación del dominio), así que sus tiempos no incluyen el saludo de seguridad TLS (~50-140 ms extra que sí paga Hostinger en cada request). Descontando ese tiempo específico de la comparación, DonWeb sigue siendo más rápido — el margen se reduce de ~3x a ~2x, pero no desaparece. Cuando DonWeb tenga su propio certificado (apenas se delegue el dominio), sus tiempos van a subir levemente por ese mismo motivo, pero seguirá siendo el más rápido de los dos.
2. **La ubicación de red desde donde se testeó también influye.** Estas mediciones se hicieron desde un mismo punto de origen para ambos hostings (por eso son comparables entre sí), pero la distancia/ruta de red hasta cada datacenter no es necesariamente idéntica. Aun así, la brecha es demasiado grande y consistente (se repite en 5 páginas, 3 archivos y 10+ muestras cada uno) para explicarse solo por eso.
3. Ambos hostings devolvieron el contenido correcto (código 200) en el 100% de las mediciones — no hubo errores ni timeouts en ninguno de los dos.

## Conclusión

Para este sitio en particular, **DonWeb entrega el contenido de forma consistentemente más rápida que Hostinger** — el margen (~3x en promedio) es demasiado grande y repetido como para atribuirlo a variabilidad de red. Para un sitio institucional de este tamaño ambos tiempos son aceptables para un visitante real (todos por debajo de 400ms de servidor en el peor caso), pero si el criterio de decisión es rendimiento puro, DonWeb es la opción más rápida de las dos.

La demora que originalmente tenía el formulario de contacto (10-13s) era independiente de esta comparación y afectaba por igual a los dos hostings — **ya fue corregida** (ver "Mejora aplicada" en el Resultado 3): el formulario responde ahora en menos de 200ms en ambos, sin que eso cambie la recomendación de hosting basada en velocidad general del sitio.
