# Analista Funcional — contadores-bma-agentes-ia

Estado: **ANÁLISIS CERRADO 2026-09-23** — Discovery iniciado 2026-08-30, relevamiento estructural y research técnico incorporados el 2026-09-23, cuestionario de cierre respondido por Joaquín el mismo día.

---

## Contexto

Cliente: Contadores BMA (estudio contable). Ya es cliente de Olvidata Soft — ver proyecto previo `contadores-bma-conversor` (conversor Excel Bejerman Web/Onvio → planilla cliente, entregado 2026-06-25, en producción desde entonces).

## Alcance funcional propuesto (hipótesis inicial, a validar con el cliente)

El estudio quiere instalar una plataforma de agentes IA para automatizar tareas operativas diarias del estudio: impuestos, conciliaciones bancarias, balances, sueldos, y asistencia con manuales de uso de Bejerman Onvio (para no depender de soporte técnico). Objetivo final del cliente: agentes de punta a punta que avisen solo ante excepciones, con arranque gradual — modo asistido/supervisado por tarea antes de pasar a autónomo.

Mecanismo de "entrenamiento": cada empleado documenta paso a paso la tarea que quiere automatizar, y eso configura al agente correspondiente; el empleado puede seguir corrigiendo/entrenando al agente después.

Arquitectura propuesta (research inicial, ver Google Doc en metadata.md): servidor central del estudio como orquestador (Claude Agent SDK) + agente liviano en la PC de cada empleado, que es quien interactúa con Bejerman Onvio.

**Alcance refinado por el usuario (2026-08-31)** — acota la hipótesis inicial a algo más concreto: Bejerman Web sigue siendo la herramienta principal que usa el empleado, no se reemplaza ni se automatiza "por dentro". El sistema se construye alrededor de tres piezas:
1. Un bot que responde las consultas/dudas de uso de **Bejerman Web/Onvio y de SOS Contador** — segunda herramienta muy usada por el estudio, agregada por el usuario el 2026-08-31 (ver sección "SOS Contador" más abajo) — con la documentación de ambas cargada (100% agente, ver mapa de la sección "Stack: agente vs. script determinístico").
2. Scripts para las conversiones de archivos que hoy se hacen a mano (capa de adaptadores, script determinístico — mismo patrón que `contadores-bma-conversor`), incluyendo el traslado de datos entre Bejerman Web y SOS Contador si el relevamiento confirma que hoy se hace a mano.
3. Automatización de los procesos que el estudio ya tiene definidos y siguen siempre los mismos pasos.

Esto es compatible 100% con la Opción A y con el plan de acción de 5 fases ya definido — no cambia la arquitectura en capas, la acota a un alcance más manejable para la Fase 0-1.

## Research de integración con Bejerman Onvio (hallazgos, pendientes de confirmar con el cliente/proveedor)

- **CONFIRMADO (2026-08-30, cruzado con `contadores-bma-conversor/documento-funcional.md` §1.1):** Contadores BMA usa **Bejerman Web + Onvio**, que es 100% SaaS en la nube de Thomson Reuters — sin instalación, sin base de datos local, solo navegador. Esto es distinto de la línea **Bejerman ERP/Premium** (esa sí es on-premise con SQL Server) que se había asumido en el research inicial. **No hay una base de datos de Bejerman en la red del estudio a la que conectarse por VPN** para este cliente — corrige la Opción B original.
- No se encontró API pública documentada para la suite Bejerman Web/Onvio Argentina. Existe una Onvio BR Accounting API pública (Brasil/Domínio Contábil) con OAuth2, pero es un producto distinto — no aplica directamente.
- **BLOQUEO CONTRACTUAL (2026-08-30):** los "Onvio Full Terms" de Thomson Reuters (`tax.thomsonreuters.com/en/full-terms/onvio`, sección "Unauthorized Technology") prohíben explícitamente, salvo autorización previa de Thomson Reuters: (i) instalar o correr software/hardware sobre sus productos/servicios/red; (ii) usar tecnología para descargar/minar/scrapear/indexar sus datos automáticamente; (iii) conectar automáticamente (por API o cualquier otro medio) sus datos con otro software/servicio/red. Esto cubre tanto la automatización de interfaz (computer-use) como cualquier integración de datos automatizada — no es un tema de madurez/riesgo del agente, es una prohibición contractual directa. No se confirmó el texto exacto de la versión argentina del contrato (las URLs de Onvio AR redirigen a selección de región) — se asume cláusula equivalente hasta confirmar contra el contrato real firmado por Contadores BMA.
- 2FA obligatorio en Onvio (Thomson Reuters Authenticator/Auth0 Guardian — push, TOTP, SMS o hardware key) + reCAPTCHA en login + timeout de sesión de 30 min de inactividad — fricciones técnicas adicionales para cualquier automatización de login, independientes del bloqueo contractual.
- Camino que sigue abierto sin necesitar autorización: automatizar lo que pasa **después** de que el empleado exporta un archivo a mano desde Bejerman Web (acción humana, no acceso automatizado al sistema de Thomson Reuters) — es lo que ya hace `contadores-bma-conversor` en producción.

## SOS Contador — research, complementariedad con Bejerman Web y puntos de dolor (agregado 2026-08-31)

### Qué es y qué hace

SOS Contador (`sos-contador.com`) es una suite contable-impositiva 100% en la nube, dirigida a estudios contables y profesionales independientes en Argentina. Módulos principales, por lo relevado en su base de ayuda pública:
- **Impositivo/ARCA**: liquidación de IVA (F2002/F2051), Libro IVA Digital, Ingresos Brutos Convenio Multilateral (CM03 mensual, CM05 anual), SIFERE, proyección de Ganancias, ajuste por inflación contable e impositivo.
- **Contabilidad**: generación automática de asientos y libro diario a partir de compras/ventas cargadas, estados contables, Sumas y Saldos, amortización de Bienes de Uso.
- **Gestión**: ventas, compras, cuenta corriente, cheques, clientes, proveedores, stock, cobros/pagos.
- **Sueldos v2**: liquidación de remuneraciones — módulo propio, superpuesto en función con el de Bejerman (ver pregunta abierta 7 más abajo).
- **Monotributo**, **Agro**, multimoneda, importación automática diaria de comprobantes desde AFIP/ARCA ("Mis Comprobantes").
- Integraciones ya existentes mencionadas por el proveedor: Mercado Libre, Mercado Pago, Tienda Nube, ARBA, LUA (no confirmado el alcance exacto de cada una).

### Documentación disponible para cargar en el bot

- Base de ayuda estructurada por módulo: `ayuda.sos-contador.com.ar` (organizada en menús — Inicio, Asistentes ARCA, Monotributo, Gestión, Contabilidad, Sueldos v2, Automatizaciones, Agro, Más funcionalidades — con secciones propias de Importar/Exportar datos y API).
- Blog con tutoriales (`sos-contador.com/blog`) y canal de YouTube con +30 videos tutoriales.

### Hallazgo clave — contraste directo con Bejerman/Onvio

**A diferencia de Bejerman/Onvio (bloqueado contractualmente sin autorización previa de Thomson Reuters), SOS Contador publica y ofrece activamente una API para integraciones de terceros**: documentación técnica pública vía Postman (`documenter.getpostman.com/view/1566360/SWTD6vnC`), pensada explícitamente para que estudios contables integren SOS con sus propias plataformas — hay un precedente citado por el propio proveedor (software "Mi Estudio Digital" integrado vía esta API para manejo de cartera de clientes) y hasta un grupo de WhatsApp de desarrolladores que la usan. Esto **reabre la puerta a integración automatizada real (equivalente a Opción B) para la porción del flujo que pasa por SOS Contador**, aunque Bejerman siga limitado a Opción A. En la arquitectura en capas ya definida, esto se traduce en un adaptador adicional ("API SOS Contador") en paralelo al adaptador de archivos exportados de Bejerman — ambos alimentando el mismo modelo canónico, sin tocar reglas de negocio ni orquestación.

*Nota de honestidad*: no se profundizó en el contenido técnico de la colección de Postman (alcance de endpoints, autenticación, límites) — es trabajo de la etapa de Arquitectura, no de Análisis. Tampoco se confirmó una referencia encontrada en el research sobre una posible suspensión de la integración AFIP/ARCA de SOS por una resolución "ARCA 74/2022" — es un dato de una sola fuente indirecta, no verificado, y no se lo debe dar por cierto sin confirmarlo directo con SOS Contador o con el estudio.

### Hipótesis de complementariedad con Bejerman Web — a validar con el cliente

**Variante A**: Bejerman Web es la herramienta de gestión/facturación/sueldos "puertas para adentro" de cada cliente que atiende el estudio (ya confirmado por `contadores-bma-conversor`: ahí se genera la liquidación de sueldos), y SOS Contador es la herramienta que el estudio usa específicamente para las presentaciones impositivas (IVA, IIBB, Ganancias) y los libros contables de esos mismos clientes — el flujo típico sería trasladar datos generados en Bejerman hacia SOS Contador para liquidar y presentar impuestos.

**Variante B**: ambos sistemas se usan en paralelo para distintos clientes/carteras del estudio (algunos clientes en Bejerman, otros en SOS Contador), sin traslado de datos entre uno y otro — cada sistema es autocontenido para el cliente que le corresponde.

La Variante A es la que generaría el mayor punto de dolor automatizable (carga manual repetida de los mismos datos en dos sistemas); la Variante B no tendría ese punto de dolor pero sí duplicaría el trabajo de construir el bot de consultas y los scripts para dos ecosistemas de documentación distintos sin sinergia entre ellos. Se agregó como pregunta abierta 6-7 (ver abajo) — debe confirmarse en la reunión de discovery o el cuestionario individual antes de diseñar el adaptador de SOS Contador.

### Puntos de dolor identificados que Olvidata podría atacar

1. **Traslado manual de datos entre Bejerman Web y SOS Contador** (si se confirma la Variante A) — automatizable con script de parseo del export de Bejerman + la API oficial de SOS Contador para la carga, sin depender de ninguna autorización especial (a diferencia de lo que pasaría del lado Bejerman).
2. **Doble carga de sueldos** — ambos sistemas tienen módulo de liquidación de sueldos; si el estudio usa los dos para esto, hay una duplicación de trabajo evidente a resolver primero (definir cuál es la fuente de verdad).
3. **Presentaciones impositivas repetitivas** (IVA, IIBB CM03/CM05) armadas hoy revisando datos de Bejerman y cargando a mano en SOS — automatizable vía la API de SOS Contador, en la capa de adaptadores.
4. **Bot de consultas combinado**: la base de ayuda de SOS Contador está bien estructurada por módulo (a diferencia de la documentación de Bejerman/Onvio, más dispersa) — buen candidato a cargar primero en el bot de soporte, junto con los manuales de Bejerman ya contemplados.

## Relevamiento estructural del estudio (aportado por Joaquín, 2026-09-23)

Este bloque responde varias preguntas abiertas y **cambia el modelo de entrega del proyecto**. Es el aporte que le da
forma al estudio: hasta acá el proyecto era una hipótesis de plataforma a medida; con esto pasa a ser una configuración
del producto propio de Olvidata.

### Las tres ramas del estudio

El estudio se organiza en tres ramas de la contaduría. Todo está relacionado; el objetivo declarado es **estandarizar la
forma de trabajo para que todos trabajen igual y darle un lineamiento al estudio**.

| Rama | Qué hace | Sistema que usa | Contra qué corrobora |
|---|---|---|---|
| **Contabilidad** | Balances, conciliaciones | SOS Contador | ARCA |
| **Impuestos** | IVA, Ingresos Brutos, liquidaciones a empresas, retenciones, pagos | SOS Contador | ARCA |
| **Sueldos** | Liquidación de remuneraciones | **ONVIO de Bejerman** | Web de **ARBA** (convenio multilateral, locales y demás datos) |

### El circuito real de Contabilidad e Impuestos, y dónde está el dolor

SOS Contador **importa desde ARCA** todos los movimientos declarados de las empresas: pagos, facturas, todo. El usuario
después **corrobora esos datos contra ARCA** para constatar que la información quedó bien cargada, porque **el sistema
suele fallar**: facturas duplicadas, facturas que están en ARCA y no aparecen en SOS Contador, y casos equivalentes.

Esa corroboración manual, repetida por empresa y por período, es **el punto de dolor nuclear del proyecto** — y es la
tarea que más justifica todo lo demás. No es una tarea de criterio: es una comparación de dos conjuntos de comprobantes
que hoy se hace a ojo.

> **Camino de crecimiento identificado:** integrar ARCA por **web services**. Textual del relevamiento: *si se puede
> automatizar las consultas se resuelve la mayor parte de la operatoria*. Queda como evaluación técnica (ver preguntas
> abiertas 8 y 9), no como supuesto: el estudio tiene experiencia con ARCA en el lado de **emisión** (WSFEv1, ver
> `34-integracion-afip-arca.instructions.md` y los proyectos marihogar / delicias-naturales / la-platense), que **no es
> el mismo servicio** que consultar los comprobantes recibidos de un tercero.

### El modelo de entrega cambia: el usuario releva, Olvidata destraba

Definición de Joaquín, y es la que ordena todo el diseño:

- **Cada usuario es el encargado de hacer su propio análisis funcional** de lo que necesita resolver. No hay un
  relevamiento central de Olvidata tarea por tarea: la herramienta que lo hace posible es el **analista de
  automatizaciones** (M15 del producto, publicado 2026-09-23), que conversa con cada persona, encuentra lo que repite y
  le deja propuesto el instructivo, la regla, la tarea programada y el agente propio.
- **Olvidata queda como respaldo**, no como implementador de cada tarea: entra solo para las **implementaciones de
  configuración necesarias para destrabar un problema técnico de compatibilidad**, con scripts o código que resuelvan el
  problema puntual (un formato que no parsea, un conector que falta, un agente base nuevo).
- Para que ese autoservicio no sea "cada uno hace lo que quiere", **el sistema tiene que tener cargada la documentación
  de ARCA y ARBA**: es lo que acota hasta dónde llega el alcance de lo que cada usuario define, y lo que permite que la
  automatización de la operatoria diaria se construya en conjunto y no a los tumbos.

**Consecuencia directa:** el proyecto deja de ser una plataforma a medida (servidor central + Claude Agent SDK + agente
liviano por PC, hipótesis del research inicial) y pasa a ser **una configuración del producto `olvidata-agentes-multirubro`**
— multi-tenant .NET, ya construido, con M10 (conocimiento por rubro), M11 (conectores), M12 (programaciones), M14
(instructivos) y M15 (analista de automatizaciones). El trabajo de Olvidata se concentra en el **rubro contable del
núcleo** y en los conectores, no en construir una plataforma nueva. Esto **requiere confirmación explícita** antes de
cerrar Análisis (pregunta abierta 10): invalida buena parte del plan de 5 fases de arriba, que se escribió sobre la
hipótesis anterior.

### Qué queda resuelto de las preguntas abiertas

- **Pregunta 6 — RESUELTA, con una variante que no estaba prevista.** No es (A) traslado Bejerman→SOS ni (B) carteras
  separadas: la división es **por rama de trabajo**. Contabilidad e Impuestos viven en SOS Contador; Sueldos vive en
  ONVIO de Bejerman. Los dos sistemas conviven en el mismo cliente, sin traslado de datos entre ellos.
- **Pregunta 7 — RESUELTA.** Sueldos se liquida en **ONVIO de Bejerman**. No hay doble carga de sueldos en SOS Contador,
  así que el punto de dolor 2 de la sección anterior **queda descartado**.
- **Pregunta 4 — PARCIALMENTE RESUELTA.** Aparece la tarea nuclear (corroboración SOS ↔ ARCA) y el circuito de Sueldos
  (ONVIO ↔ ARBA). Sigue faltando el catálogo por persona, que ahora **lo produce el propio analista de automatizaciones**
  en vez de una reunión de relevamiento — ese es el cambio de modelo.
- **El bloqueo contractual de Thomson Reuters pierde centralidad.** Onvio queda acotado a Sueldos, y lo que hay que
  automatizar de esa rama es la **constatación contra ARBA**, no el acceso a Onvio. Las preguntas 2 y 3 siguen abiertas,
  pero ya no bloquean el grueso del proyecto.

## Preguntas abiertas — bloquean el cierre de Discovery/Análisis

1. ~~¿Qué línea de Bejerman tiene instalada Contadores BMA?~~ **RESUELTA 2026-08-30**: Bejerman Web (cloud), no Premium/ERP on-premise.
2. **¿Existe algún canal de integración autorizada de Thomson Reuters para Bejerman Web/Onvio Argentina** (equivalente a la Onvio BR Accounting API que sí existe para Brasil)? Preguntar directamente al ejecutivo de cuenta de Contadores BMA — la cláusula de "Unauthorized Technology" habilita autorización previa de Thomson Reuters, lo que sugiere que el canal para pedirla existe.
3. Confirmar el texto exacto de la cláusula de uso/automatización en el contrato argentino real firmado por Contadores BMA (no solo los "Onvio Full Terms" globales usados como proxy).
4. Catálogo real de tareas a automatizar: relevar con el equipo del estudio (no solo con el owner) cuáles son las tareas manuales más repetitivas y de mayor volumen hoy, priorizando las que dependen de archivos que el empleado ya exporta (compatible con Opción A sin pedir autorización).
5. Cantidad de empleados/puestos de trabajo reales que usarían el sistema.
6. **¿Cómo se complementan Bejerman Web y SOS Contador en el flujo real del estudio?** Dos variantes a confirmar (ver sección "SOS Contador" arriba, marcadas como **hipótesis a validar**): (A) Bejerman genera los datos de gestión/sueldos y el estudio los traslada a mano hacia SOS Contador para liquidar y presentar impuestos — ej. "cargo las ventas del mes en Bejerman, después las vuelvo a tipear/importar en SOS para armar el IVA"; o (B) cada sistema es autocontenido para una cartera de clientes distinta, sin traslado de datos entre uno y otro — ej. "los clientes con Bejerman quedan en Bejerman, los que están en SOS quedan en SOS, no se mezclan". La respuesta define si corresponde construir el adaptador de traslado Bejerman→SOS como parte de la Fase 0-1.
7. **¿El estudio usa el módulo de Sueldos de Bejerman, el de SOS Contador (Sueldos v2), o ambos para el mismo cliente?** Ej. variante 1: "todo sueldo se liquida en Bejerman, SOS Contador no se usa para esto" (sin duplicación); variante 2: "liquidamos en Bejerman y después cargamos de nuevo en SOS para que quede en la contabilidad" (duplicación de carga, candidato directo a automatizar).

8. ~~¿Qué web service de ARCA cubre la consulta de los comprobantes de un contribuyente?~~ **RESUELTA 2026-09-23: no existe.** Ver el research. Queda como estaba escrita, abajo, para que se vea qué se preguntó:
   ~~ El estudio necesita leer lo
   que ARCA tiene declarado (lo que SOS importa) para compararlo. La experiencia previa de Olvidata es de **emisión**
   (WSFEv1), que no sirve para esto. Hay que confirmar contra la documentación oficial de ARCA qué servicio expone los
   comprobantes recibidos/emitidos de un CUIT, con qué alcance y con qué límites, y **qué habilitación y qué delegación
   de clave fiscal** necesita el estudio para consultar por sus clientes. Es el dato que decide si la tarea nuclear se
   resuelve por conector o sigue dependiendo de un archivo exportado a mano.
9. **PARCIALMENTE RESUELTA 2026-09-23** (regímenes generales sí; Convenio Multilateral va por COMARB, a verificar). ¿Qué expone ARBA por servicio y qué solo por web? Para Sueldos hay que constatar convenio multilateral, locales y
   otros datos. Confirmar qué padrones tienen consulta automatizada y cuáles solo pantalla.
10. **¿Se confirma que el proyecto se entrega como configuración de `olvidata-agentes-multirubro`** y no como plataforma
    a medida? Es la decisión que reescribe el plan de fases y el presupuesto. (Ver "El modelo de entrega cambia".)
11. **¿Cuántas personas hay por rama y quién usa qué?** Sigue abierta la pregunta 5 (cantidad de puestos), ahora con la
    apertura por rama: define cuántas licencias y cuántos relevamientos propios se esperan.
12. ~~¿SOS Contador expone por API los comprobantes ya importados?~~ **RESUELTA 2026-09-23: sí, los recibidos.** Si sí, la comparación contra ARCA se puede hacer
    entre dos conectores sin ningún archivo de por medio. La API existe y es pública (ver research arriba); falta
    confirmar que cubre este caso.

## Resultado del research de ARCA, ARBA y SOS (2026-09-23)

Detalle completo y fuentes: [research-arca-arba-sos-2026-09.md](../research-arca-arba-sos-2026-09.md).

**El hallazgo que explica todo:** la documentación oficial de SOS Contador dice que su importación automática
(**Autoimpo**) *"recupera comprobantes con una antigüedad máxima de 12 a 15 días hacia atrás"* y que los más viejos
*"no se volverán a importar automáticamente"*. **Los faltantes no son un bug: son una limitación documentada del
producto.** Todo comprobante que un proveedor carga tarde en ARCA nunca entra solo. El control contra ARCA que hace el
estudio es, con esta configuración, estructuralmente necesario.

La misma fuente dice que SOS **deduplica por CAE**, así que los duplicados probablemente vienen de mezclar Autoimpo con
importación manual, o de comprobantes sin CAE. **A confirmar con el estudio.**

- **Pregunta 8 (ARCA) — RESUELTA, y en contra de lo esperado.** **No existe** un web service de ARCA que devuelva la
  lista de comprobantes recibidos: el catálogo oficial (50+ servicios) no lo tiene. Lo más cercano es **WSCDC**
  (constatación: valida un comprobante puntual, no lista nada). **Mis Comprobantes es un servicio del portal web**, con
  clave fiscal, que exporta a Excel/CSV hasta 365 días por consulta. → **El conector de ARCA se cae del alcance.** El
  control se hace igual, con el archivo que la persona baja: acción humana, sin problema contractual ni credenciales de
  terceros. Lo único que no se puede es evitarle ese paso.
- **Pregunta 9 (ARBA) — RESUELTA A MEDIAS.** Las alícuotas de percepción/retención de **regímenes generales** y el
  padrón de IIBB **sí** tienen servicio web (consulta por CUIT y período, sin operador). Pero el **Convenio
  Multilateral** —justo lo que nombró el relevamiento— va por **COMARB**, que es otro organismo: **queda por verificar.**
- **Pregunta 12 (SOS) — RESUELTA A FAVOR.** La API existe, usa token y **sí lista los comprobantes recibidos**:
  `GET /compra/listado/:periodo` y `POST /compra/consulta`, más `/compra/detalle/:id` y `PUT`/`DELETE /compra/:id` para
  corregir. **Consecuencia: el cruce necesita UN solo archivo** (el export de ARCA), porque el lado SOS entra por API.
  **Límite:** no hay endpoint de **ventas** — los emitidos siguen necesitando export, pero no es donde está el dolor.
  Endpoints y autenticación en `.github/instructions/37-servicios-externos-fiscales.instructions.md`.

## Respuestas del cierre de Análisis (Joaquín, 2026-09-23)

Cuestionario completo en [cuestionario-cierre-analisis.md](../cuestionario-cierre-analisis.md).

### Modelo y alcance — CONFIRMADO

- **A1: SÍ.** Se entrega como **configuración del producto `olvidata-agentes-multirubro`**. Queda cerrada la pregunta 10
  y con ella el cambio de modelo: **el plan de 5 fases de agosto queda derogado** (estaba escrito sobre la hipótesis de
  plataforma a medida).
- **A2: las tres ramas** desde el arranque (Contabilidad, Impuestos, Sueldos).
- **A3:** el conversor de sueldos ya entregado **se absorbe más adelante**, no ahora. Sigue en producción como está.

### Gente — 6 personas, 4 de ellas Directores

| Persona | Usuario | Rama / rol |
|---|---|---|
| Marcial Bourdin | `mbourdin@contadoresbma.com.ar` | **Director** · piloto |
| Maximiliano Mendy | `mmendy@contadoresbma.com.ar` | **Director** |
| Andrea Puglisi | `sueldos@contadoresbma.com.ar` | **Director** · Sueldos |
| Gastón | (ya tiene usuario) | **Director** · piloto |
| Marcela Videla | `marcelavidela80@gmail.com` | Empleada |
| Daniela Videla | `danividela.91.21@gmail.com` | Empleada |

- **B1:** 2 personas por rama (Contabilidad, Impuestos, Sueldos). **Todos usan todos los agentes**, salvo los **agentes
  propios de los Directores**, que quedan personales. → En el producto esto sale solo: un agente de la organización con
  visibilidad **Personal** lo ve únicamente su creador; con visibilidad **Organización**, todos. No hace falta nada nuevo.
- **B2: ~100 empresas** en cartera, **20 de Convenio Multilateral**.
- **B4:** el piloto lo hacen **Marcial y Gastón**.

> **Observación para tener presente, no es un bloqueo.** 4 Directores sobre 6 personas es una proporción alta. En el
> producto, Director habilita aplicar lo que alcanza a **toda la empresa** (instructivos y reglas de todos, programaciones
> a nombre de otro, publicar agentes para la empresa, topes de gasto). Con 4 personas pudiendo hacerlo, el lineamiento
> depende de que se pongan de acuerdo entre ellos — que es justamente lo que el proyecto quiere estandarizar. **Sugerencia:
> arrancar el piloto con Marcial y Gastón como Directores y sumar a los otros dos cuando el criterio esté asentado.**
> Es reversible en cualquier momento desde la consola.

### Accesos — todo disponible, con una alerta

- **C1: la delegación de clave fiscal ya la tiene el estudio.** → El camino de ARCA queda habilitado (para lo que ARCA
  expone, que no incluye listar comprobantes).
- **C2: sí**, tienen credenciales de ARBA.
- **C3: sí**, hay acceso de estudio a la cartera en SOS.
- **C4:** sería la **primera vez** que usan la API de SOS. → Prever una prueba de la API contra una CUIT real antes de
  construir encima: nunca se ejerció en este estudio.

> 🔴 **ALERTA — credenciales en archivos.** Tanto en C1 como en C2 la respuesta fue *"tienen archivos con las credenciales
> de cada usuario"*. Eso es un riesgo real y hay que tratarlo como parte del proyecto, no como un comentario al pasar:
> son claves fiscales de ~100 contribuyentes de terceros en archivos planos.
>
> **Lo que aporta el producto:** las credenciales de un conector se guardan **cifradas por organización**, con lista
> blanca de dominios por conexión y sin que ningún agente pueda elegir a dónde se conecta (M11, guardia de destinos).
> Migrar esas credenciales al sistema **es una mejora de seguridad concreta**, no solo una comodidad.
>
> **Lo que NO resuelve el producto:** los archivos que ya existen. Eso es una decisión del estudio y conviene plantearla
> explícitamente en la reunión de arranque.

### La tarea nuclear

- **D1: CONFIRMADO.** Los duplicados vienen de **mezclar Autoimpo con importación manual**. La hipótesis del research
  era correcta: SOS deduplica por CAE, así que el duplicado lo introduce el doble camino de carga. **Esto se puede
  atacar antes que cualquier agente**: ordenar el circuito de carga elimina una de las dos causas de diferencias.
- **D2 a D7: las releva el propio analista de automatizaciones con cada persona.** Decisión de Joaquín, y es exactamente
  el modelo del proyecto: la frecuencia del control, cuánto tarda, qué hacen con las diferencias, si miran emitidos y qué
  constatan en ARBA **no se releva en una reunión central** — sale de la conversación de cada usuario con el analista.

### Decisiones de Olvidata

- **E1: el agente remite a la fuente oficial.** **No se cargan** calendario, alícuotas ni escalas. Es la opción
  conservadora y la que evita el peor error posible: un vencimiento viejo dicho con seguridad. **Olvidata no queda
  comprometida a mantener datos que cambian todo el tiempo.**
- **E2: tope de USD 50/mes** para la organización.
- **E3: sí**, arrancar en etapa *"Tu forma de trabajar"*.
- **E4: sí**, versionar el repo `Agente Contable-IA` en git.

> **Sobre el tope de USD 50/mes.** Con Sonnet 5 (USD 2/10 por millón, verificado 2026-09-23) una tarea de agente con
> contexto típico ronda los **USD 0,05-0,06**. Para ~100 clientes con un control mensual cada uno, eso da unos **USD 6**;
> con varias tareas por cliente y por rama, entre **USD 25 y 40**. **El tope entra, pero sin mucho aire** — y las
> conversaciones de relevamiento con el analista suman aparte. Conviene **revisarlo después del primer mes real** con el
> consumo a la vista, que el producto muestra por miembro, por agente y por cliente. El tope no rompe nada: frena y avisa.

### Onvio

- **F1 y F2: sin respuesta.** Nadie preguntó todavía al ejecutivo de cuenta de Thomson Reuters y no está a mano el
  contrato firmado. **No bloquea**: Onvio queda acotado a Sueldos y lo que se automatiza de esa rama es la constatación
  contra ARBA, no el acceso a Onvio. Queda anotado por si en algún momento interesa.

## Opciones de integración (stack + infraestructura) — para llevar a la reunión de discovery

Tres paquetes, de menor a mayor autonomía/riesgo. Las tres comparten la arquitectura base (servidor central orquestador + agente liviano por PC); lo que cambia es cómo llega el agente a los datos de Bejerman Onvio.

> **Actualizado 2026-08-30 tras confirmar que Contadores BMA usa Bejerman Web (cloud, sin SQL Server local) y tras encontrar el bloqueo contractual de Thomson Reuters — ver sección de research arriba.** Se mantienen las 3 opciones mapeadas pero con su estado real corregido.

**Opción A — Solo archivos exportados (mínimo riesgo) — ÚNICA VIABLE HOY SIN AUTORIZACIÓN DE THOMSON REUTERS**
- Integración: el agente nunca toca Bejerman/Onvio directamente. El empleado exporta a mano (acción humana, no un acceso automatizado al sistema de TR) y el agente procesa ese archivo después — mismo patrón que `contadores-bma-conversor`, extendido a más tareas.
- Infraestructura: 100% en la nube (VPS chico o hosting compartido tipo Ferozo), sin tocar la red del estudio ni el VPN.
- Stack: Claude Agent SDK (Node/TS) como servicio web; sin agente local instalado.
- Contras: el empleado sigue exportando a mano, no sirve para tareas que requieren escribir en Bejerman/Onvio. Se queda en agentes asistentes, no autónomos de punta a punta.
- Es el único camino que no depende de ningún permiso adicional de Thomson Reuters.

**Opción B — Acceso automatizado a datos (vía SQL local o vía integración a Bejerman Web/Onvio) — BLOQUEADA hasta autorización de Thomson Reuters**
- Ya no aplica como "SQL Server local vía VPN": Contadores BMA usa Bejerman Web (cloud), no hay base local a la que conectarse.
- Cualquier variante de acceso automatizado a los datos de Bejerman Web/Onvio (API no documentada, integración directa, etc.) cae bajo la cláusula de "Unauthorized Technology" de los términos de Onvio — requiere autorización previa explícita de Thomson Reuters (pregunta abierta 2).
- Si Thomson Reuters confirma un canal de integración autorizado (como existe para Onvio Brasil), esta opción se rediseña sobre esa API oficial en vez de sobre un acceso SQL directo.

**Opción C — Punta a punta con automatización de interfaz (computer-use) — BLOQUEADA contractualmente, no solo por riesgo/madurez**
- Un agente local controlando la interfaz web de Onvio (login, clicks, carga de datos) es técnicamente viable (es una app web, más automatizable que un desktop legacy) pero cae de lleno en la prohibición de "Unauthorized Technology" de los Términos de Onvio — no es un tema de madurez del agente, es un incumplimiento contractual que puede derivar en suspensión de la cuenta.
- Fricciones técnicas adicionales incluso si se autorizara: 2FA obligatorio (push/TOTP/SMS/hardware key), reCAPTCHA en login, timeout de sesión de 30 min.
- Solo queda habilitada si Thomson Reuters la autoriza explícitamente.

**Recomendación actualizada**: diseñar y presupuestar la Fase 1 completa sobre la Opción A (sin dependencias de autorización de terceros), en paralelo a que Contadores BMA le pregunte a su ejecutivo de cuenta de Thomson Reuters si existe un canal de integración autorizada. Si la respuesta es positiva, B y C se rediseñan sobre esa vía oficial — nunca sobre acceso no autorizado.

## Arquitectura en capas propuesta — insumo para Diseño/Arquitectura (Análisis aún no cerrado)

Pregunta del usuario: si se implementa la Opción A con arquitectura en capas, y sobre esa base se desarrollan las reglas de los agentes, ¿se puede migrar a futuro a B/C sin perder la infraestructura construida? Respuesta: sí, siempre que se construya como puertos y adaptadores (hexagonal), no como una implementación ad-hoc.

**Capas:**
1. **Orquestación** (Claude Agent SDK, chat web, memoria/entrenamiento, auditoría) — independiente del mecanismo de integración, no cambia entre A/B/C.
2. **Reglas de negocio / agentes** — escritas en términos de un **modelo de datos canónico** (movimientos bancarios, asientos, liquidaciones de sueldo, comprobantes) y de *tools de intención* ("obtener_movimientos_banco", "obtener_liquidacion_sueldos"), nunca en términos del mecanismo concreto ("leer_excel_grilla", "query_sql"). Es lo que el empleado "entrena" con su documento paso a paso.
3. **Adaptadores** — única capa que cambia según A/B/C: en A parsea el archivo exportado (reutiliza el mapeo de `contadores-bma-conversor`) y lo transforma al modelo canónico; en B reemplaza el parseo por la API/base que Thomson Reuters autorice, entregando el mismo modelo canónico; en C opera la interfaz (computer-use) traduciendo hacia/desde ese mismo modelo.

Si el contrato de salida del adaptador no cambia, agregar o reemplazar uno no obliga a tocar reglas de negocio ni orquestación.

**Matiz**: la migración es limpia para tareas de **lectura** (conciliaciones, balances, reportes) — en A ya hay algo que migrar. Para tareas de **escritura** (cargar un asiento, presentar una DDJJ) no existe hoy una "versión A" real — en A eso lo sigue haciendo el empleado a mano. Cuando C se habilite, esas reglas se escriben de cero, pero nacen conectadas al mismo modelo canónico y al mismo agente constructor — no hay arquitectura que reescribir, solo reglas nuevas que agregar.

## Plan de acción — proceso progresivo de integración

| Fase | Objetivo | Gate de salida |
|---|---|---|
| Fase 0 — Fundación | Definir modelo canónico + tools de intención; construir adaptador A (reutilizando mapeo de `contadores-bma-conversor`); levantar orquestación + auditoría; 1 agente piloto end-to-end sobre archivos exportados. En paralelo: consulta formal a Thomson Reuters sobre canal de integración autorizado (no bloquea esta fase). | Agente piloto validado por al menos un empleado real, con feedback incorporado. |
| Fase 1 — Expansión sobre A | Sumar 2-4 agentes más del catálogo priorizado, todos sobre el adaptador A. Formalizar el proceso de entrenamiento (documento del empleado → agente constructor → modo supervisado → feedback). Panel de auditoría básico. | 4-5 agentes en modo supervisado real; los de menor riesgo empiezan a graduarse a "avisa después". |
| Fase 2 — Adaptador B (condicional a autorización de TR) | Si Thomson Reuters confirma canal autorizado: construir adaptador B que alimenta el mismo modelo canónico. Agentes de Fase 0-1 no se reescriben. Si TR no autoriza: el estudio sigue operando estable en A, sin bloqueo. | Agentes de lectura graduados a autónomos de punta a punta para el tramo de lectura. |
| Fase 3 — Adaptador C (condicional a autorización de TR para escritura) | Construir adaptador de escritura (computer-use u otro mecanismo autorizado). Arranca con aprobación humana obligatoria por tarea. | Cada tarea se gradúa individualmente a autónomo con reporte posterior, según track record — nunca en bloque. |
| Fase 4 — Todo el estudio, punta a punta | Rollout a todos los empleados/roles. Revisión periódica de costo de tokens vs. ahorro real. | Objetivo final del cliente: agentes autónomos con aviso solo ante excepciones. |

Las Fases 2 y 3 quedan condicionadas a la respuesta de Thomson Reuters. Si nunca llega autorización, el sistema no queda a mitad de camino: la arquitectura en capas hace que B y C sean una mejora incremental sobre un producto ya completo en Fase 1, no una migración obligatoria.

## Stack: agente vs. script determinístico, por tarea

Pregunta del usuario: ¿hay un mejor stack que "un grupo de agentes" para este proyecto? Respuesta: sí — el mejor stack no es "agentes para todo", es un **híbrido**. Código determinístico tradicional (scripts/ETL, la capa de adaptadores ya definida) para todo lo que sea reglas fijas y estables, y agentes LLM reservados para lo que requiere lenguaje natural o juicio.

**Regla transversal, no negociable**: todo cálculo numérico, impositivo o legal (alícuotas, retenciones, fórmulas de sueldo, totales de balance) va siempre en código determinístico — nunca "calculado" por el LLM dentro del agente. El agente invoca ese cálculo como tool y explica el resultado, pero no hace la aritmética él mismo. Un número mal calculado por alucinación es el peor escenario posible en un estudio contable.

| Tarea | Script determinístico | Agente | Nota |
|---|---|---|---|
| Conciliación bancaria | Parseo/normalización de archivos + matching automático por monto/fecha/número de operación | Resolver y explicar diferencias que no calzan solas; aprender patrones que el empleado corrige | El grueso del volumen se resuelve con reglas; el agente entra solo en la cola de excepciones |
| Manuales / soporte Bejerman Onvio y SOS Contador | — | 100% agente (manuales + base de ayuda de ambas herramientas como contexto/RAG) | Es una tarea de lenguaje natural por definición |
| Traslado de datos Bejerman → SOS Contador (si se confirma pregunta abierta 6) | Parseo del export de Bejerman + carga vía API oficial de SOS Contador | Resolver casos que no matchean automáticamente entre ambos sistemas | Único adaptador candidato a nivel "Opción B" desde el arranque, porque SOS sí tiene API autorizada — no depende de Thomson Reuters |
| Carga de comprobantes/facturas | Extracción de campos si el formato es estructurado y estable | Extracción de entradas no estructuradas (PDF/foto variable) + clasificación de cuenta contable | Evaluar primero si conviene apoyarse en la IA que ya trae Bejerman antes de reconstruirlo |
| Balances / papeles de trabajo | Totales, ratios, cruces período a período | Señalar inconsistencias que no siguen una regla fija; redactar la explicación para el contador | El cálculo nunca sale del agente, solo la narrativa |
| Liquidación de impuestos (IVA, Ganancias) | El cálculo impositivo en sí | Armar el borrador explicativo, detectar datos faltantes, interpretar casos particulares | Máximo riesgo si se invierte el rol |
| Sueldos / RRHH | Cálculo de la liquidación (conceptos, aportes, contribuciones) | Detectar anomalías vs. mes anterior; responder preguntas del empleado | Mismo criterio que impuestos |

En la arquitectura en capas de la sección anterior, los scripts determinísticos viven en la capa de **adaptadores** (y en funciones de negocio fijas invocadas como tools), y el agente vive en la capa de **reglas/juicio**, consumiendo esas tools en vez de reimplementar la lógica.

## Próximo paso

1. **Confirmar la pregunta 10** (entrega como configuración del producto vs. plataforma a medida). Es el gate: cambia el
   plan de fases, la arquitectura y el presupuesto.
2. Con eso confirmado, el **esquema de agentes** del estudio está diseñado en
   [2-disenador-funcional.md](2-disenador-funcional.md) (2026-09-23).
3. Verificar las preguntas 8, 9 y 12 (servicios de ARCA, ARBA y SOS) — son las que deciden cuánta operatoria se
   automatiza de verdad y cuánta sigue dependiendo de un archivo exportado a mano.
4. Reunión con el equipo del estudio para la cantidad de puestos por rama (pregunta 11) y el arranque del piloto.
