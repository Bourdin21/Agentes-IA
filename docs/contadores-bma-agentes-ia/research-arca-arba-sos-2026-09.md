# Research — cómo se puede comunicar con ARCA, ARBA y SOS Contador

**Fecha:** 2026-09-23 · **Para:** responder las preguntas abiertas 8, 9 y 12 del
[Análisis](definiciones/1-analista-funcional.md), antes de diseñar conectores o cotizar nada.

Todo lo que sigue sale de documentación pública de los organismos y del proveedor. Lo que **no** se pudo confirmar está
marcado como tal: no se da nada por cierto para poder cotizarlo.

> **Este research se generalizó como memoria del estudio.** El catálogo completo de servicios externos —ARCA, ARBA,
> COMARB, SOS Contador y Onvio, con qué tarea acorta cada uno y qué NO existe— vive en
> `.github/instructions/37-servicios-externos-fiscales.instructions.md`, y es de lectura obligatoria **antes de cotizar
> cualquier conector** en cualquier proyecto contable. Este archivo queda como el detalle del caso BMA.

---

## 1. El hallazgo que explica el problema de BMA

La documentación oficial de SOS Contador dice, sobre su importación automática desde ARCA (**Autoimpo**):

> *"Autoimpo recupera comprobantes con una antigüedad máxima de **12 a 15 días hacia atrás**. Si los comprobantes son
> más antiguos, no se volverán a importar automáticamente."*
> *"Se recomienda cargarlos manualmente o por importación manual en caso de que los comprobantes sean más antiguos a ese
> límite."*
> — [ayuda.sos-contador.com.ar/autoimportaciones/autoimpo](https://ayuda.sos-contador.com.ar/autoimportaciones/autoimpo)

**Eso es la causa raíz de los "faltantes", y no es un bug: es una limitación conocida y documentada del producto.** Todo
comprobante que un proveedor carga en ARCA con más de 12-15 días de atraso **nunca entra solo** a SOS. Por eso el
control contra ARCA no es una manía del estudio: con esta configuración es estructuralmente necesario.

La misma página agrega dos datos que ordenan el diseño del agente:

- *"Sólo se importan comprobantes emitidos y recibidos cuyos **CAE no se encuentren** en la base de tu cliente"* → SOS
  **ya deduplica por CAE**. Entonces los duplicados que ve BMA no vienen de Autoimpo repitiendo: lo más probable es que
  vengan de **mezclar Autoimpo con importación manual** del XLS, o de comprobantes sin CAE (controladores fiscales
  viejos). **A confirmar con el estudio** — es una hipótesis con fundamento, no un hecho.
- Desde el 01/01/26 también entran los comprobantes de controladores fiscales de nueva tecnología reportados por el
  emisor.

## 2. ARCA — pregunta abierta 8

### Lo que NO existe

**No hay un web service oficial de ARCA que devuelva la lista de comprobantes recibidos de un contribuyente.** El
catálogo oficial de servicios SOAP (50+ servicios: facturación, padrones A4/A10/A13/A100, liquidaciones sectoriales,
remitos, aduana, F931, VEPs) no tiene ninguno que haga eso.
— [Catálogo de web services de ARCA](https://www.afip.gob.ar/ws/documentacion/catalogo.asp)

**Consecuencia directa: el conector de ARCA que se había imaginado para la tarea nuclear no se puede construir.** Hay
que sacarlo del alcance y del presupuesto.

### Lo que sí existe

| Servicio | Qué hace | Sirve para |
|---|---|---|
| **Mis Comprobantes** (portal web, clave fiscal) | Muestra emitidos y recibidos. Filtra por período, tipo y emisor. **Exporta a Excel/CSV**, hasta **365 días** por consulta | **Es la fuente del control.** La persona lo baja (acción humana) y el agente compara |
| **WSCDC — Constatación de Comprobantes** | Le pasás un comprobante y responde si está autorizado por ARCA | Validar de a uno. **No lista nada** |
| **WSFEv1** | Emisión de comprobantes y CAE | Ya lo usa el estudio en otros proyectos. **No sirve para esto** |
| Padrón A4 / A10 / A13 / A100 | Datos del contribuyente | Constancia de inscripción, condición frente al IVA |

### Lo que esto significa para el agente `cont-control-arca`

| Diferencia a detectar | ¿Se puede? | Cómo |
|---|---|---|
| **Duplicados en SOS** | **Sí** | Comparando SOS contra sí mismo. No hace falta ARCA |
| **Comprobantes en SOS que ARCA no tiene autorizados** | **Sí** | Con el export de Mis Comprobantes, o de a uno con WSCDC |
| **Comprobantes que están en ARCA y faltan en SOS** ⭐ | **Sí, pero solo con el archivo** | Export de Mis Comprobantes contra lo que tiene SOS. **No hay forma por web service** |

La tercera es la más dolorosa y la más frecuente (es la que produce el límite de 12-15 días de Autoimpo). **Se resuelve
igual**, pero con el archivo que la persona baja, no con un conector.

> **Nota sobre servicios de terceros.** Existen productos que ofrecen "descargar Mis Comprobantes por API"
> (ej. afipsdk.com). Automatizan el portal por detrás y piden la clave fiscal del contribuyente. **No se recomiendan
> sin analizar antes** los términos de uso de ARCA y el manejo de credenciales de clientes del estudio. No es un camino
> a cotizar hoy.

## 3. ARBA — pregunta abierta 9

| Qué | Cómo se consulta | Estado |
|---|---|---|
| **Alícuotas de percepción/retención de regímenes generales**, por CUIT y período | **Sí hay servicio web** ("Sistema de recaudación por sujeto" / DFE): la aplicación cliente consulta por HTTPS sin intervención de un operador y recibe un XML | **Automatizable** |
| Padrón de contribuyentes de IIBB (condición: activo, exento, suspendido; régimen; actividad) | Consulta de padrón de ARBA | Automatizable por el mismo camino |
| **Convenio Multilateral** — alícuotas de tarjetas, bancos e intermediarios | **Por COMARB, no por ARBA** | **Hay que verificar aparte**: COMARB/SIFERE es otro organismo y otro trámite |

**Para BMA esto parte la pregunta en dos.** Lo de regímenes generales de Provincia de Buenos Aires se puede automatizar;
**lo de Convenio Multilateral —que es justo lo que el relevamiento nombró— va por COMARB y todavía no está verificado.**

## 4. SOS Contador — pregunta abierta 12

| Qué | Estado |
|---|---|
| **La API existe y es oficial** | Confirmado. Base: `https://api.sos-contador.com/api-comunidad/` |
| **Autenticación** | Token: POST a `/login` con credenciales → token de usuario → segundo token por CUIT elegido |
| **Operaciones confirmadas** | Crear clientes, crear comprobantes, obtener CAE, listar clientes (`/cliente/listado`), consultar saldos de cuenta corriente |
| **¿Lista los comprobantes ya importados?** ⭐ | **SÍ, los recibidos — VERIFICADO 2026-09-23** |

### Verificado: la API sí trae los comprobantes recibidos

La página de la colección no renderiza, pero **el JSON sí se puede leer**:
`https://documenter.gw.postman.com/api/collections/1566360/SWTD6vnC`. De ahí salieron los endpoints reales:

| Método | Path | Para el cruce |
|---|---|---|
| **GET** | `/compra/listado/:periodo` | ⭐ **Lista las compras (recibidos) del período** |
| **POST** | `/compra/consulta` | Consulta por parámetros, para rangos propios |
| GET | `/compra/detalle/:id` | Detalle de un comprobante |
| PUT / DELETE | `/compra/:id` | **Corregir lo que el cruce detecte, por API** |
| GET | `/afip/eventanilla` | Comunicaciones de e-ventanilla de ARCA (hallazgo lateral, útil aparte) |

Autenticación: `POST /login` → token de usuario → `GET /cuit/credentials/{idcuit}` → token de CUIT, que va en
`Authorization: Bearer` en todos los demás requests.

**Dos límites reales:**

1. **No hay endpoint de ventas.** La colección tiene `/compra`, `/cobro` y `/asiento`, ninguna ruta `venta`. Para cruzar
   **emitidos** hay que exportar de SOS a mano. **Los recibidos —donde está el dolor, porque son los que llegan tarde—
   sí salen por API.**
2. **El `:periodo` toma valores relativos** (`hoy`, `ayer`, `semana`, `mes`, `mes anterior`), no un rango arbitrario.
   Para un rango propio, `POST /compra/consulta` (verificar sus parámetros al implementar).

### Lo que esto habilita

El control ARCA↔SOS de comprobantes recibidos queda así: **la persona baja un solo archivo** (Mis Comprobantes de ARCA)
y el agente trae el otro lado por API. Y como `PUT`/`DELETE /compra/:id` existen, lo que el cruce detecte **se puede
corregir por API** en vez de a mano — con aprobación humana, que es como el producto maneja toda acción que escribe.

## 5. Lo que cambia en el proyecto

1. **Se cae el conector de ARCA.** No existe el servicio. Sacarlo del alcance, del plan y del presupuesto.
2. **El control ARCA↔SOS se hace igual**, con el export de Mis Comprobantes (hasta 365 días por consulta). Es una acción
   humana, sin problema contractual ni credenciales de por medio. **Y era el paso 5 del plan, que no dependía de nadie.**
3. **El proyecto no pierde su tarea nuclear** — pierde una forma de hacerla que resultó no existir.
4. **ARBA queda partido**: regímenes generales sí; Convenio Multilateral por COMARB, a verificar.
5. ~~Queda una sola verificación abierta (API de SOS)~~ **CERRADA 2026-09-23: la API sí lista los recibidos.** El cruce
   necesita **un solo archivo** (el de ARCA), no dos. Ventas queda por export, pero no es donde está el dolor.
6. **Hay material nuevo para el conocimiento del rubro**: el límite de 12-15 días de Autoimpo y la deduplicación por CAE
   son exactamente el tipo de dato que hace que el agente entienda qué está buscando y por qué.

## Fuentes

- [Catálogo de web services SOAP de ARCA](https://www.afip.gob.ar/ws/documentacion/catalogo.asp)
- [Documentación de web services de factura electrónica](https://www.afip.gob.ar/ws/documentacion/ws-factura-electronica.asp)
- [Ayuda de ARCA — web services](https://www.afip.gob.ar/fe/ayuda/webservice.asp)
- [SOS Contador — Autoimpo Mis Comprobantes](https://ayuda.sos-contador.com.ar/autoimportaciones/autoimpo)
- [SOS Contador — Importación múltiple desde Mis Comprobantes / Portal IVA](https://ayuda.sos-contador.com.ar/menu-inicio/importar-datos/desde-arca/Importacion-Multiple)
- [SOS Contador tiene API](https://ayuda.sos-contador.com.ar/mas-funcionalidades-de-sos/SOS-Contador-tiene-API) y su [colección de Postman](https://documenter.getpostman.com/view/1566360/SWTD6vnC)
- [ARBA — Ingresos Brutos](https://web.arba.gov.ar/ingresos-brutos) y [especificación del web service de alícuotas (DFE)](https://www.sistemasagiles.com.ar/trac/wiki/IngresosBrutosArba)
- [Mis Comprobantes permite consultar y descargar en Excel períodos de hasta 365 días](https://contadoresenred.com/mis-comprobantes-permite-consultar-y-descargar-en-excel-periodos-de-hasta-365-dias/)
