---
description: Catálogo de servicios externos de ARCA, ARBA, COMARB, SOS Contador y Bejerman/Onvio — qué expone cada uno, qué tarea del estudio acorta y cómo se usa. Memoria reutilizable para todo proyecto contable/impositivo. Verificado contra documentación pública el 2026-09-23 (origen: contadores-bma-agentes-ia).
applyTo: "**/*.{cs,cshtml,md,yml,instructions.md}"
---

# 37 — Servicios externos fiscales (ARCA, ARBA, COMARB, SOS Contador, Onvio)

Memoria técnica reutilizable: **qué se puede automatizar de verdad** contra cada organismo y cada plataforma contable, y
qué no. Antes de este documento, cada proyecto volvía a buscar lo mismo y llegaba a la misma conclusión tarde, después
de haberla cotizado.

**Todo proyecto contable/impositivo nuevo arranca leyendo esto.** Y muy especialmente: **antes de cotizar un conector.**

> **La lección que motivó el archivo.** En `contadores-bma-agentes-ia` se diseñó un conector de ARCA para comparar
> comprobantes, se lo puso en el plan y casi se lo cotiza. **Ese servicio no existe.** El catálogo oficial de ARCA tiene
> más de 50 web services y ninguno devuelve la lista de comprobantes recibidos de un contribuyente. Se descubrió
> verificando, no suponiendo — y la verificación llevó veinte minutos.

## Regla de oro

**"La plataforma tiene API" no quiere decir que tenga *la* API que necesitás.** Tres preguntas, siempre, antes de
diseñar nada encima:

1. ¿Existe el servicio **para el dato puntual** que hace falta? (no "para ese sistema")
2. ¿Qué **habilitación, delegación o certificado** necesita quien consulta, y lo tiene el estudio?
3. Si no existe: **¿hay un export manual que resuelva lo mismo?** Casi siempre sí, y casi siempre alcanza — porque la
   parte cara de la tarea no es bajar el archivo, es compararlo.

---

## 1. ARCA (ex AFIP)

### Lo que sirve

| Servicio | Sigla | Qué hace | Qué tarea acorta |
|---|---|---|---|
| Factura electrónica | **WSFEv1** | Emite comprobantes y obtiene el CAE | Facturar desde el sistema. **Patrón completo en [34](34-integracion-afip-arca.instructions.md)** |
| Constatación de comprobantes | **WSCDCV1** | Le pasás un comprobante y dice si ARCA lo tiene autorizado | Validar de a uno un comprobante recibido (detectar facturas apócrifas o mal cargadas) |
| Constancia de inscripción | **ws_sr_constancia_inscripcion** | Datos del contribuyente y sus caracterizaciones | Alta de cliente: traer razón social, domicilio y condición sin tipearlos. Reemplaza al viejo `padron_a5` |
| Padrón alcance 4 | **ws_sr_padron_a4** | Datos tributarios y regímenes de inscripción | Saber en qué impuestos está inscripto un cliente |
| Padrón alcance 10 | **ws_sr_padron_a10** | Datos resumidos del contribuyente | Validación rápida de CUIT |
| Padrón alcance 13 | **ws_sr_padron_a13** | Consulta de padrón alcance 13 | Ídem, otro alcance |
| Padrón alcance 100 | **ws_sr_padron_a100** | Tablas de parámetros del Sistema Registral | Traer catálogos oficiales en vez de hardcodearlos |
| F931 | **TRABAJO_F931** | Consulta de declaraciones juradas F931 (remuneraciones y empleados) | **Sueldos**: controlar lo declarado sin entrar al portal |
| Pagos / VEP | **SETIWS-PAGO-API** | Crea VEPs, los envía a la entidad de pago y los consulta. Reemplaza a `WSCREATEVEP` | Generar el volante de pago desde el sistema |
| Bonos fiscales / Seguros | **WSBFE**, **WSSEG** | Comprobantes de esos regímenes | Solo si el cliente opera en ellos |
| Deuda | **sud_restricciones**, **sud_contrataciones** | Deuda por CUIT (el primero **restringido a bancos**) | Proveedores del Estado |

### Lo que NO existe — no volver a buscarlo

- **No hay web service que liste los comprobantes emitidos/recibidos de un contribuyente.** Ni compras ni ventas.
- **"Mis Comprobantes" es un servicio del portal web**, con clave fiscal. Muestra emitidos y recibidos, filtra por
  período, tipo y emisor, y **exporta a Excel/CSV, hasta 365 días por consulta**. Es la fuente real para cualquier cruce.
- Existen productos de terceros que ofrecen "Mis Comprobantes por API". **Automatizan el portal por detrás y piden la
  clave fiscal del contribuyente.** No recomendarlos sin analizar términos de uso y manejo de credenciales de clientes.

### Cómo se resuelve entonces un cruce de comprobantes

La persona baja el export de Mis Comprobantes (acción humana: sin problema contractual, sin credenciales de terceros en
el sistema) y **el agente compara**. Lo caro de la tarea nunca fue bajar el archivo.

---

## 2. ARBA (Provincia de Buenos Aires)

| Servicio | Qué hace | Cómo | Qué tarea acorta |
|---|---|---|---|
| **Consulta de alícuotas** (DFE) | Alícuotas de percepción y retención de regímenes generales, por CUIT y período | SOAP/XML con usuario y contraseña de ARBA. Método `ConsultarContribuyentes(fecha_desde, fecha_hasta, cuit)`. Prod: `https://dfe.arba.gov.ar/DomicilioElectronico/SeguridadCliente/dfeServicioConsulta.do` · Test: `dfe.test.arba.gov.ar` | Saber qué alícuota corresponde aplicarle a cada contribuyente, sin entrar al portal |
| **Padrón de regímenes generales** (archivo) | Padrón mensual completo con las alícuotas por sujeto | ZIP `PadronRGSMMAAAA.zip` con dos .txt: `PadronRGSRetMMAAAA.txt` (retención) y `PadronRGSPerMMAAAA.txt` (percepción). Requiere **CIT** de agente de recaudación | Procesar el padrón entero de una vez en lugar de consultar CUIT por CUIT |
| Deducciones (retenciones/percepciones sufridas) | Consulta y descarga de lo que le retuvieron al cliente | Portal, con clave | Armar el crédito de IIBB del período |

**Ojo con la división de responsabilidades:** ARBA cubre lo **provincial de Buenos Aires**. El Convenio Multilateral es
otro organismo (abajo).

---

## 3. COMARB / SIFERE (Convenio Multilateral)

| Sistema | Qué hace | Acceso |
|---|---|---|
| **SIFERE WEB — DDJJ** | Presentación de DDJJ mensuales y anuales, y generación de pagos | Portal, con **clave fiscal de AFIP** |
| **SIFERE WEB — Consultas** | DDJJ presentadas, pagos hechos, datos de padrón y deducciones informadas por los agentes | Portal, con clave fiscal |
| **Padrón Web / Padrón Federal** | Consulta y modificación de los datos de padrón de CM (RG 3/2008-CACM) | `https://padronweb.comarb.gob.ar/padronweb/inicio.jsp` |

**No se encontró un web service de integración para Convenio Multilateral.** Son sistemas web con clave fiscal. Para
alícuotas de tarjetas, bancos e intermediarios de un contribuyente de CM, el camino documentado es COMARB, **no ARBA**.

> **Pendiente de verificar** si SIFERE expone alguna descarga masiva aprovechable. Si algún proyecto lo confirma,
> actualizar acá.

---

## 4. SOS Contador

Suite contable-impositiva cloud. **Es el caso amistoso**: el proveedor publica y promueve su API.

### API oficial

| Qué | Detalle |
|---|---|
| Base | `https://api.sos-contador.com/api-comunidad/` |
| Autenticación | Dos pasos: `POST /login` con credenciales → token de usuario → `GET /cuit/credentials/{idcuit}` → **token por CUIT**. Todos los demás requests van con `Authorization: Bearer {token de CUIT}` |
| Documentación | [Colección de Postman](https://documenter.getpostman.com/view/1566360/SWTD6vnC). **Truco: la página no renderiza para leer automáticamente, pero el JSON sí** — `https://documenter.gw.postman.com/api/collections/1566360/SWTD6vnC` |

**Endpoints verificados (2026-09-23)** — leídos del JSON de la colección:

| Método | Path | Qué hace | Qué tarea acorta |
|---|---|---|---|
| **GET** | `/compra/listado/:periodo` | **Lista las compras (comprobantes recibidos) del período** | ⭐ **El cruce contra ARCA**: se traen los recibidos por API, sin que nadie exporte de SOS |
| **POST** | `/compra/consulta` | Consulta compras por parámetros | Cruce con filtros más finos que el `:periodo` fijo |
| GET | `/compra/detalle/:id` | Detalle de una compra | Ver un comprobante puntual |
| PUT / DELETE | `/compra/:id` | Alta, modificación y baja de compra | Corregir lo que el cruce detecte |
| GET | `/cobro/listado/:periodo` · `/cobro/detalle/:id` | Cobros | Conciliación de cobranzas |
| GET | `/asiento/listado/:periodo` · `/asiento/detalle/:id` | Asientos contables | Revisión de la registración |
| GET | `/cuentacorriente/listado` | Cuentas corrientes de clientes y proveedores | Saldos sin entrar al portal |
| GET | `/cliente/listado` | Clientes y proveedores, con paginación (`?proveedor=true&cliente=true&registros=16&pagina=1`) | Sincronizar la cartera |
| GET | `/cae/status/:id` | Estado de obtención del CAE | Seguimiento de una emisión |
| **GET** | `/afip/eventanilla` | **Comunicaciones de e-ventanilla de ARCA** | Revisar la e-ventanilla de toda la cartera sin entrar cliente por cliente |
| POST | `/email/enviar` | Envía comprobantes por email | — |

**Dos límites que hay que conocer:**

1. **No hay endpoint de ventas.** La colección publicada tiene `/compra`, `/cobro` y `/asiento`, pero **ninguna ruta
   `venta`**. Para cruzar **comprobantes emitidos** hay que exportar de SOS a mano. Los **recibidos** —que es donde está
   el dolor real, porque son los que llegan tarde— sí salen por API.
2. **El `:periodo` del listado toma valores relativos** (`hoy`, `ayer`, `semana`, `mes`, `mes anterior`), no un rango de
   fechas arbitrario. Para un rango propio hay que ir por `POST /compra/consulta` (verificar sus parámetros al
   implementar).

### Importación desde ARCA — y el límite que hay que conocer

| Vía | Cómo | Límite |
|---|---|---|
| **Autoimpo** (automática) | Trae solos los comprobantes emitidos y recibidos; reporte diario por cliente | **Solo los de los últimos 12 a 15 días.** Los más viejos *"no se volverán a importar automáticamente"* |
| **Importación múltiple** (manual) | XLS/XLSX de Mis Comprobantes, CSV de Portal IVA, PEM de controladores fiscales | Sin ese límite |

**Este límite es la causa estructural de los "faltantes" en cualquier estudio que use SOS**: todo comprobante que un
proveedor carga tarde en ARCA nunca entra solo. No es un bug, está documentado por el proveedor, y obliga a un control
periódico contra el export de Mis Comprobantes.

**SOS deduplica por CAE** (*"sólo se importan comprobantes cuyos CAE no se encuentren en la base"*). Por eso, cuando
aparecen duplicados, la primera hipótesis es **mezcla de Autoimpo con importación manual**, o comprobantes sin CAE
(controladores fiscales viejos) — no que Autoimpo esté repitiendo.

Fuente: [ayuda.sos-contador.com.ar/autoimportaciones/autoimpo](https://ayuda.sos-contador.com.ar/autoimportaciones/autoimpo)

---

## 5. Bejerman Web / Onvio (Thomson Reuters) — **bloqueado por contrato**

**No automatizar nada contra Onvio sin autorización previa y escrita de Thomson Reuters.**

Los "Onvio Full Terms" (sección *Unauthorized Technology*) prohíben, salvo autorización previa: instalar o correr
software sobre sus productos, usar tecnología para descargar/scrapear/indexar sus datos, y conectar automáticamente sus
datos con otro software por API o cualquier otro medio. **Cubre tanto el computer-use como cualquier integración de
datos.** No es un tema de madurez técnica: es incumplimiento contractual, con riesgo de suspensión de la cuenta.

Fricciones adicionales aunque se autorizara: 2FA obligatorio, reCAPTCHA en login, sesión que expira a los 30 minutos.

**Lo que sí se puede:** automatizar lo que pasa **después** de que una persona exporta un archivo a mano. Eso es una
acción humana, no un acceso automatizado a su sistema. Es el patrón de `contadores-bma-conversor`, en producción.

> Existe una *Onvio BR Accounting API* pública (Brasil, OAuth2), pero es **otro producto**: no aplica a la línea
> argentina. Si un cliente necesita integración real, el camino es pedirle el canal autorizado a su ejecutivo de cuenta.

---

## 6. Mapa rápido: tarea del estudio → cómo se acorta

| Tarea | Cómo se acorta | Vía |
|---|---|---|
| Alta de cliente nuevo | Traer razón social, domicilio y condición frente al IVA por CUIT | **ws_sr_constancia_inscripcion** |
| Validar que una factura recibida sea legítima | Constatar el comprobante contra ARCA | **WSCDCV1** |
| **Cruzar lo que el sistema tiene contra lo que ARCA declaró** | Export de Mis Comprobantes + comparación automática | **Archivo** (no hay servicio) |
| Emitir facturas desde el sistema | Circuito WSAA + CAE | **WSFEv1** ([34](34-integracion-afip-arca.instructions.md)) |
| Saber qué alícuota de IIBB aplicar a un cliente | Consulta por CUIT y período, o el padrón mensual entero | **ARBA DFE** / padrón `.txt` |
| Controlar lo declarado en sueldos | Traer el F931 presentado | **TRABAJO_F931** |
| Generar el pago de una obligación | Crear el VEP desde el sistema | **SETIWS-PAGO-API** |
| Cargar comprobantes en SOS | Alta por API, o importación del XLS | **API de SOS** / importación múltiple |
| **Traer los comprobantes recibidos que SOS ya tiene** | Listado por período, por API | **`GET /compra/listado/:periodo`** |
| Revisar la e-ventanilla de ARCA de toda la cartera | Traer las comunicaciones por API | **`GET /afip/eventanilla`** de SOS |
| Cruzar comprobantes **emitidos** | No hay endpoint de ventas: export de SOS | Archivo |
| Traer datos de Convenio Multilateral | Portal, con clave fiscal | **SIFERE / Padrón Web** (sin API) |
| Cualquier cosa contra Onvio | **Solo sobre un archivo que exportó una persona** | Export manual |

## 7. Quién configura qué

**Olvidata se encarga de la configuración.** El cliente no toca credenciales, certificados ni endpoints.

| Pieza | Responsable |
|---|---|
| Certificado y clave privada de ARCA, alta del Punto de Venta tipo Web Service | **Olvidata** (ver gotchas del certificado en [34](34-integracion-afip-arca.instructions.md)) |
| Alta y prueba del conector, lista blanca de dominios, credenciales cifradas | **Olvidata** |
| Endpoints, versiones y adaptaciones cuando el organismo cambia algo | **Olvidata** |
| **Delegación de clave fiscal** de cada cliente al estudio | **El estudio** — es un trámite suyo con cada cliente, no técnico. Sin eso, ningún servicio de ARCA sirve para consultar por terceros |
| Usuario y contraseña de ARBA, CIT de agente de recaudación | **El estudio** los provee, Olvidata los carga |
| Decidir qué se automatiza | **Cada usuario**, con el analista de automatizaciones |

## 7 bis. Gotcha de YAML que costó dos veces el mismo día

Los manifiestos del núcleo (frontmatter de agentes, casos de evaluación) se leen con **YamlDotNet**, que es más estricto
que el parser de Python: **un escalar sin comillas que contiene `: ` (dos puntos y espacio) se interpreta como un mapa**,
no como texto, y la importación falla con un opaco *"Exception during deserialization"* que no dice ni la línea.

```yaml
# MAL — YAML lo lee como un mapa {clave: valor} y el importador revienta
  criterios:
    - Ofrece el camino que sí está permitido: automatizar lo que pasa después.
  description: Releva el día a día y propone cómo automatizarlo: los pasos, las reglas y el pedido.

# BIEN — entrecomillado, o reescrito sin ": "
  criterios:
    - "Ofrece el camino que sí está permitido: automatizar lo que pasa después."
  description: "Releva el día a día y propone cómo automatizarlo: los pasos, las reglas y el pedido."
```

Pasó dos veces el 2026-09-23: en el `description:` del frontmatter de un agente y en un `criterios:` de un caso.
**Cómo detectarlo en segundos**, sin bisección, porque el parser de Python lo acepta en silencio:

```python
import yaml, io, glob
for f in glob.glob('evaluaciones/*.yml'):
    d = yaml.safe_load(io.open(f, encoding='utf-8').read())
    for c in d['casos']:
        for v in c.get('criterios') or []:
            if not isinstance(v, str):
                print('PROBLEMA', f, c['clave'], type(v).__name__)
```

## 8. Antes de cotizar un conector — checklist

1. ¿Está en la tabla de arriba? Si no está, **verificar antes de prometer**.
2. ¿El catálogo oficial del organismo lo tiene? ([catálogo de ARCA](https://www.afip.gob.ar/ws/documentacion/catalogo.asp))
3. ¿Qué habilitación necesita, y la tiene el cliente **hoy**?
4. Si no existe: ¿hay export manual? Cotizar **la comparación**, que es lo que agrega valor, y decir con todas las letras
   que la persona sigue bajando el archivo.
5. Si la plataforma es de un tercero con contrato (Onvio), **leer la cláusula de uso antes que la documentación técnica**.

## Fuentes verificadas (2026-09-23)

- [Catálogo de web services SOAP de ARCA](https://www.afip.gob.ar/ws/documentacion/catalogo.asp)
- [Documentación de web services de factura electrónica](https://www.afip.gob.ar/ws/documentacion/ws-factura-electronica.asp)
- [SOS Contador — Autoimpo](https://ayuda.sos-contador.com.ar/autoimportaciones/autoimpo) · [Importación múltiple](https://ayuda.sos-contador.com.ar/menu-inicio/importar-datos/desde-arca/Importacion-Multiple) · [SOS Contador tiene API](https://ayuda.sos-contador.com.ar/mas-funcionalidades-de-sos/SOS-Contador-tiene-API)
- [ARBA — web service de consulta de alícuotas (DFE)](https://www.sistemasagiles.com.ar/trac/wiki/IngresosBrutosArba) · [Régimen de recaudación por sujeto](https://web.arba.gov.ar/regimen-de-recaudacion-por-sujeto)
- [COMARB — SIFERE](https://www.ca.gob.ar/sifere) · [Padrón Web / Padrón Federal](https://www.ca.gob.ar/preguntas-frecuentes/sistemas/padron-web-padron-federal)
- Onvio Full Terms, sección *Unauthorized Technology* (`tax.thomsonreuters.com/en/full-terms/onvio`)
