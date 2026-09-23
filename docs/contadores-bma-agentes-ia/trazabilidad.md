# Trazabilidad - contadores-bma-agentes-ia

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-09-23 - implementacion (bloque B: alta y configuracion de la organizacion)
- Etapa: Implementacion
- Cambio: BMA queda dada de alta y configurada en el producto. **Tenant `bma`** con licencia del rubro `contable` por
  365 dias, etapa de entrega `TuFormaDeTrabajar` y tope de gasto USD 50/mes (respuesta E2). **6 miembros** creados, todos
  con la misma contrasena inicial `Olvidata2026!`: Marcial Bourdin, Maximiliano Mendy, Andrea Puglisi
  (`sueldos@contadoresbma.com.ar`) y Gaston Bourdin (`gastonbourdin@gmail.com`) como Directores; Marcela Videla y
  Daniela Videla como Empleadas. **3 areas**: Contabilidad, Impuestos, Sueldos. **2 reglas de toda la empresa**, ambas
  obligatorias: "Ningun calculo lo hace el modelo" (los importes salen de la fuente, nunca se deducen ni se recuerdan del
  periodo anterior) y "Nada se presenta, se paga ni se manda solo" (el ultimo paso siempre lo hace una persona).
  Para poder hacer todo esto sin pantalla por pantalla se agregaron a la consola de Olvidata los verbos `area-crear`,
  `regla-crear` y `cartera-importar` (CSV nombre,cuit, con pasada en seco), que pasan por los mismos services y las
  mismas validaciones que el portal actuando como un Director de la organizacion.
- Notas: **Dos cosas quedan pendientes y necesitan dato de BMA**: (1) la **cartera de ~100 empresas** — el comando esta
  listo, falta el listado; (2) **a que area va cada persona** — la respuesta B1 dice 2 por rama pero no dice quien, y
  solo Andrea esta atada a Sueldos en el analisis. Se asigna desde el portal o cuando llegue el mapeo.
  La contrasena compartida y sin cambio forzado en el primer ingreso es una **deuda conocida del producto**.

### 2026-09-23 - analista-funcional (via conversacion directa)
- Etapa: Relevamiento para configurar el portal
- Cambio: Guion de la reunion de relevamiento/configuracion armado (90 min, portal proyectado, se configura en vivo):
  encuadre, cartera, documentos con estado de lectura, criterios via "Configurar conversando", areas y miembros,
  un instructivo escrito en la reunion + tarea real corrida, una programacion, limites y aprobaciones, piloto y
  revision a 2 semanas. Incluye checklist previo, checklist de cierre y que no hay que prometer (Onvio, presentacion
  ante ARCA, opcionales sin aprobar).
- Notas: Ver guion-reunion-configuracion.md. Complementa cuestionario-configuracion-portal.md: si vuelve respondido,
  los bloques 1 a 3 se acortan y la reunion baja a 60 min.

### 2026-09-22 - presupuestador (vía /agentes-ia-presupuestador)
- Etapa: Presupuesto (excepción al gate documentada: precio de lista del portal, sin desarrollo)
- Cambio: Plan base Rubro estándar contable USD 1.500 + 90/mes; opcionales conciliación e Impuestos BMA (Intermedio) y balances (Básico): total USD 4.000 + 290/mes, primer año USD 2.580 (base) o 7.480 (completo). Bot de consultas no se cotiza aparte (ya incluido en el material del rubro).
- Notas: Ver definiciones/4-presupuestador.md y presupuesto-cliente.md. Pendiente aprobación del cliente.

### 2026-09-21 - analista-funcional (vía conversación directa)
- Etapa: Relevamiento para configurar el portal (BMA ya en producción en agentes.olvidata.com.ar, plan Rubro estándar contable)
- Cambio: Cuestionario nuevo orientado al portal: equipo y roles, áreas, cartera, reglas, instructivos, agentes a priorizar, material de referencia, programaciones, aprobaciones y piloto. Joaquín se lo manda a Gastón; con las respuestas se configura el portal de BMA en producción.
- Notas: Ver cuestionario-configuracion-portal.md

### 2026-08-30 - orquestador
- Etapa: Setup
- Cambio: Proyecto creado e incorporado al framework Agentes-IA. Cliente: Contadores BMA (mismo cliente de `contadores-bma-conversor`, alcance mucho mayor — plataforma de agentes IA, carpeta separada).
- Notas: Ver metadata.md

### 2026-08-30 - analista-funcional (vía conversación directa)
- Etapa: Discovery/Análisis
- Cambio: Research inicial de integración con Bejerman Onvio (sin API pública documentada para AR; línea Premium/SQL Server como mejor camino de solo lectura vía queries/ODBC; Classic/Access sin ese camino; alternativa computer-use para lo que no tenga puente de datos) y propuesta de arquitectura (servidor central + agente liviano por PC), stack (Claude Agent SDK), catálogo de agentes hipotético por módulo y roadmap por fases. Documentado en Google Doc. 5 preguntas abiertas bloquean el cierre de Análisis.
- Notas: Ver definiciones/1-analista-funcional.md; Google Doc: https://docs.google.com/document/d/1i-S5TaQ19uJFRmHiE0iLp3neTrfLcwq_UcsqCRjqO0k/edit

### 2026-08-30 - analista-funcional (vía conversación directa)
- Etapa: Discovery/Análisis
- Cambio: 3 opciones de integración (stack + infraestructura) presentadas para la reunión de discovery: A) solo archivos exportados, 100% cloud, agentes asistentes; B) SQL Server de solo lectura + VPN a la red del estudio, recomendada como punto de partida; C) B + automatización de interfaz (computer-use) para escritura, capa a habilitar gradualmente. Recomendación: diseñar sobre B, A como contingencia si no hay acceso SQL/licencia lo prohíbe.
- Notas: Ver definiciones/1-analista-funcional.md §Opciones de integración

### 2026-08-30 - analista-funcional (vía conversación directa)
- Etapa: Discovery/Análisis
- Cambio: Guión de reunión de discovery armado: 5 bloques (canal Thomson Reuters, catálogo real de tareas con variantes de alcance por área, organización/volumen, priorización de agente piloto, restricciones/expectativas) + checklist de cierre para poder pasar a Diseño.
- Notas: Ver guion-discovery.md

### 2026-09-02 - analista-funcional (vía conversación directa)
- Etapa: Discovery/Análisis
- Cambio: El usuario creó un Proyecto de Claude.ai para que Gastón trabaje ahí, describiendo su proceso y contexto de trabajo, con la idea de exportar después esa información y las "propiedades de conversión" usadas para sistematizarlas e importarlas a este proyecto. Riesgo identificado: una charla libre puede salir desordenada y difícil de sistematizar (mismo problema que ya se resolvió en `contadores-bma-conversor` con `mapeo-archivos.md`, no con narrativa suelta). Se armó `plantilla-importacion-proceso.md` — una plantilla por proceso (identificación, pasos, tabla de reglas de conversión origen→destino mapeada a la capa de adaptador, reglas de juicio mapeadas a la capa de agente, casos borde, ejemplo real) para que lo que salga de esa charla ya llegue en formato importable directo a `definiciones/1-analista-funcional.md` o a un `mapeo-<proceso>.md` dedicado.
- Notas: Ver plantilla-importacion-proceso.md

### 2026-09-02 - analista-funcional (vía conversación directa)
- Etapa: Discovery/Análisis
- Cambio: Identificado un empleado real y concreto: **Gastón**, usa tanto Bejerman Web/Onvio como SOS Contador — primer caso confirmado de uso combinado en el estudio, candidato natural a usuario piloto de la Fase 0 (a confirmar, no decidido formalmente todavía). Armado `cuestionario-relevamiento-gaston.md`, personalizado: además del relevamiento estándar (tareas, procesos paso a paso, archivos a convertir, dudas frecuentes, prioridad), incluye un bloque específico sobre cómo se complementan Bejerman y SOS en su trabajo real (responde directo a las preguntas abiertas 6 y 7) y un bloque de disponibilidad para el piloto.
- Notas: Ver cuestionario-relevamiento-gaston.md

### 2026-09-23 - analista-funcional + disenador-funcional (vía `/agentes-ia-orquestador`)
- Etapa: Discovery/Análisis (actualizado) + Diseño (esquema de agentes, borrador)
- Cambio: **Relevamiento estructural del estudio aportado por Joaquín**, que reordena el proyecto. (1) El estudio se
  organiza en **tres ramas**: Contabilidad y Impuestos sobre **SOS Contador**, Sueldos sobre **ONVIO de Bejerman**.
  (2) SOS Contador **importa de ARCA** y el usuario **corrobora a mano contra ARCA** porque el sistema falla (facturas
  duplicadas, comprobantes que están en ARCA y no en SOS): ese control es **el punto de dolor nuclear**. (3) Sueldos
  constata datos en la **web de ARBA** (convenio multilateral, locales). (4) Camino de crecimiento: **integrar ARCA por
  web services** — con las consultas automatizadas se resuelve la mayor parte de la operatoria.
- **Cambio de modelo de entrega (requiere confirmación, pregunta abierta 10):** el proyecto deja de ser una plataforma a
  medida (servidor central + Claude Agent SDK + agente liviano por PC) y pasa a ser **una configuración del producto
  `olvidata-agentes-multirubro`**. Cada usuario hace **su propio análisis funcional** con el analista de automatizaciones
  (M15, publicado el mismo día), y **Olvidata queda como respaldo** solo para destrabar problemas técnicos de
  compatibilidad con scripts o código. La documentación de ARCA y ARBA se carga en el sistema para **acotar el alcance de
  lo que cada usuario define**. Esto invalida buena parte del plan de 5 fases anterior.
- Preguntas abiertas **resueltas**: la 6 (la división es **por rama**, no por cartera ni por traslado Bejerman→SOS) y la
  7 (sueldos se liquida en ONVIO, **no hay doble carga** — el punto de dolor 2 queda descartado). La 4 queda parcial: el
  catálogo por persona ahora lo produce el propio analista de automatizaciones. El bloqueo contractual de Thomson Reuters
  **pierde centralidad**: Onvio queda acotado a Sueldos y lo automatizable de esa rama es la constatación contra ARBA.
- Preguntas abiertas **nuevas**: 8 (qué web service de ARCA expone los comprobantes de un contribuyente — la experiencia
  previa del estudio es de **emisión**, WSFEv1, que no sirve para esto, y falta la delegación de clave fiscal), 9 (qué
  expone ARBA por servicio y qué solo por pantalla), 10 (confirmar el modelo de entrega), 11 (personas por rama) y 12
  (si la API de SOS expone los comprobantes ya importados).
- **Esquema de agentes diseñado** en `definiciones/2-disenador-funcional.md`: 9 agentes base del rubro contable en tres
  ramas (Contabilidad: conciliación bancaria, balances · Impuestos: **control ARCA↔SOS**, IVA, IIBB/CM, vencimientos ·
  Sueldos: control de liquidación, constatación ARBA) más dos transversales (soporte de sistemas con la documentación de
  los cuatro sistemas cargada, y el analista de automatizaciones que ya existe). Dos reglas del estudio no negociables
  desde el día uno: **ningún cálculo lo hace el modelo** y **nada se presenta ni se paga solo**. Arranque propuesto:
  reglas + documentación → piloto de conciliación bancaria (hay material real cargado en `archivos/`) → control ARCA↔SOS
  sobre archivo exportado → conector de ARCA si las preguntas 8 y 12 dan verde.
- Notas: Sin código, sin presupuesto. **Gate abierto**: la pregunta 10 decide el plan de fases, la arquitectura y el
  presupuesto — no se abre Arquitectura hasta confirmarla. Ver `definiciones/1-analista-funcional.md` §Relevamiento
  estructural y `definiciones/2-disenador-funcional.md`.

### 2026-09-23 - PRESUPUESTO cerrado internamente (presupuestador + consulta a olvidata-ceo)
- Etapa: Presupuesto. **Pendiente de aprobación de Joaquín antes de armar la propuesta al cliente.**
- **WBS: 35 h M** en tres bloques — A núcleo del rubro (22 h: 3 agentes, 2 documentos de conocimiento, conector SOS),
  B configuración de la organización (7 h), C puesta en marcha con el piloto (6 h).
- **Categoría de calibración NUEVA: "Agente del núcleo"** (prompt + ficha + casos de evaluación + corridas reales hasta
  aprobar + publicación). No existía en el dataset; se abre anclada en el dato real de M15 del mismo día —4 versiones y
  5 corridas hasta aprobar, USD 4,1 de tokens— y **se cierra con el real de este proyecto**. Sub-tipos: comparación 6 h,
  constatación 4 h, consulta sobre conocimiento ya cargado 3 h.
- **Decisión de `olvidata-ceo` (consultado explícitamente por perfil atípico): SIN descuento**, override tipo FABINCO —
  BMA ya paga SOS y Onvio, 4 socios, capacidad de pago demostrada; descontarle al lead mejor capitalizado juega en contra
  del posicionamiento premium 2027. Precio de lista promo (vigente hasta 2026-12-31); la palanca es el **grandfathering**
  y **el testimonio se pide aparte, no se paga con descuento**.
- **Modelo: setup + suscripción**, esquema "Rubro estándar" + 1 addon. **Nada por usuario ni por cliente de cartera.**
  **Setup USD 2.500** (base 1.500 + addon 1.000) · **USD 170/mes = USD 2.040/año**. Tokens los paga el cliente, con tope
  de USD 50/mes ya acordado.
- **Cuánto del núcleo se le carga a BMA: solo el conector de SOS.** Los agentes de ARBA y soporte quedan en la tarifa
  plana como **inversión de producto** — el núcleo se amortiza contra los próximos estudios contables, no se le cobra
  completo al primero (mismo criterio que la reutilización cross-proyecto en Build).
- **Registrado explícitamente: el precio NO sale de las horas.** Las 35 h M por fórmula de Build darían USD 367; el
  precio es casi 7× eso porque **no se vende esfuerzo, se vende el producto ya construido** (M1–M15 + el rubro contable
  ya escrito). La fórmula de Build no aplica a este modelo. El WBS sirve para dimensionar trabajo, riesgo y calibración,
  **no para fijar precio** — no mezclarlos al explicarlo internamente.
- 🔴 **Corrección a un supuesto del CEO, a decidir antes de presentar.** El CEO clasificó `cont-arba` como "sin conector"
  y advirtió que si requiere scraping sube de categoría. **El research dice algo distinto y mejor: ARBA SÍ tiene web
  service oficial** (consulta de alícuotas DFE + padrón mensual `.txt`), no hace falta scraping. Dos caminos: **A** (como
  está cotizado, el agente trabaja sobre el padrón que se baja una vez por mes — sin cambio de precio) o **B** (conector
  ARBA, segundo addon Intermedio: +USD 1.000 setup y +USD 80/mes). **Recomendación: arrancar con A**; B se suma después
  sin reescribir el agente, que es justamente lo que permite la arquitectura en capas.
- **No cotizado**: migrar las claves fiscales de ~100 clientes al almacenamiento cifrado (hace falta definir alcance),
  conector de ARBA (camino B), Convenio Multilateral por COMARB (A7), absorber el conversor (A3: más adelante) y el
  conector de ARCA (**no existe el servicio**).
- Notas: **gate del cliente** antes de Implementación.

### 2026-09-23 - ANÁLISIS CERRADO (cuestionario respondido por Joaquín)
- Etapa: cierre de Análisis. Respuestas completas en `cuestionario-cierre-analisis.md` y volcadas en
  `definiciones/1-analista-funcional.md` §Respuestas del cierre.
- **A1 CONFIRMADO**: se entrega como **configuración del producto**. Con eso queda cerrada la pregunta 10 y **el plan de
  5 fases de agosto queda derogado** (estaba escrito sobre la hipótesis de plataforma a medida). Alcance: **las tres
  ramas**. El conversor ya entregado se absorbe más adelante, no ahora.
- **Gente: 6 personas, 4 Directores** (Marcial Bourdin, Maximiliano Mendy, Andrea Puglisi y Gastón; Marcela y Daniela
  Videla como empleadas). 2 por rama. **Todos usan todos los agentes salvo los propios de los Directores** → sale solo
  con la visibilidad Personal/Organización de M4, sin nada nuevo. **~100 empresas en cartera, 20 de Convenio
  Multilateral.** Piloto: **Marcial y Gastón**. *Observación registrada: 4 Directores sobre 6 es proporción alta y el
  lineamiento pasa a depender de que se pongan de acuerdo entre ellos; se sugiere arrancar el piloto con 2 y sumar
  después — reversible desde la consola.*
- **Accesos: todos disponibles.** Delegación de clave fiscal **ya la tiene el estudio**; credenciales de ARBA también;
  acceso de estudio a la cartera en SOS. **Primera vez** que usarían la API de SOS → prever una prueba contra una CUIT
  real antes de construir encima.
- 🔴 **ALERTA DE SEGURIDAD REGISTRADA**: las credenciales (clave fiscal de ~100 contribuyentes y ARBA) están hoy en
  **archivos planos con las credenciales de cada usuario**. El producto las guarda **cifradas por organización**, con
  lista blanca de dominios y sin que ningún agente elija destino (M11): migrarlas **es una mejora de seguridad concreta**.
  Lo que el producto no resuelve son los archivos que ya existen — decisión del estudio, a plantear en el arranque.
- **D1 CONFIRMADO: los duplicados vienen de mezclar Autoimpo con importación manual.** La hipótesis del research era
  correcta. **Hay una acción inmediata que no necesita ningún agente**: ordenar el circuito de carga elimina una de las
  dos causas de diferencias.
- **D2–D7 las releva el propio analista de automatizaciones con cada persona** (decisión de Joaquín, coherente con el
  modelo): frecuencia del control, tiempo que lleva, qué hacen con las diferencias, si miran emitidos y qué constatan en
  ARBA no se relevan en reunión central.
- **E1: el agente remite a la fuente oficial** — no se cargan calendario, alícuotas ni escalas. Olvidata **no** queda
  comprometida a mantener datos que caducan. Fijado en el conocimiento del rubro (`40-calendario-alicuotas-escalas.md`).
- **E2: tope USD 50/mes.** *Advertencia registrada: con Sonnet 5 (USD 2/10 por millón, verificado 2026-09-23) una tarea
  ronda USD 0,05-0,06; ~100 clientes con un control mensual dan ~USD 6, y con varias tareas por cliente y rama, entre USD
  25 y 40. Entra, pero sin mucho aire, y las conversaciones de relevamiento suman aparte. Revisar tras el primer mes real.*
- **E3: sí**, etapa "Tu forma de trabajar". **E4: sí** → repo `Agente Contable-IA` **versionado en git** (2 commits) con
  README y .gitignore que excluye credenciales y certificados.
- **F1/F2: sin respuesta.** Onvio queda acotado a Sueldos; no bloquea nada.
- Notas: **Análisis CERRADO.** Lo único técnico abierto es el riesgo A7 (Convenio Multilateral por COMARB). Listo para
  abrir Presupuesto.

### 2026-09-23 - verificación final: la API de SOS sí lista los comprobantes recibidos
- Etapa: Arquitectura (cierre de la última pregunta abierta técnica).
- **Pregunta 12 RESUELTA A FAVOR.** La colección de Postman no renderiza para lectura automática, pero **el JSON sí**:
  `https://documenter.gw.postman.com/api/collections/1566360/SWTD6vnC`. Endpoints verificados:
  **`GET /compra/listado/:periodo`** (lista los comprobantes RECIBIDOS del período), `POST /compra/consulta` (por
  parámetros), `GET /compra/detalle/:id`, `PUT`/`DELETE /compra/:id`, `GET /cobro/listado/:periodo`,
  `GET /asiento/listado/:periodo`, `GET /cuentacorriente/listado`, `GET /cae/status/:id` y —hallazgo lateral—
  **`GET /afip/eventanilla`** (comunicaciones de e-ventanilla de ARCA de toda la cartera). Autenticación:
  `POST /login` → token de usuario → `GET /cuit/credentials/{idcuit}` → token de CUIT en `Authorization: Bearer`.
- **Lo que habilita:** el control ARCA↔SOS necesita **un solo archivo** (el export de Mis Comprobantes de ARCA); el lado
  SOS entra por API. Y como existen `PUT`/`DELETE /compra/:id`, **lo que el cruce detecte se puede corregir por API**,
  con la aprobación humana que el producto exige para toda acción que escribe.
- **Dos límites reales:** (1) **no hay endpoint de ventas** — la colección tiene `/compra`, `/cobro` y `/asiento`, ninguna
  ruta `venta`; para cruzar **emitidos** hay que exportar de SOS, aunque no es donde está el dolor. (2) El `:periodo` del
  listado toma valores relativos (`hoy`, `ayer`, `semana`, `mes`, `mes anterior`), no un rango arbitrario: para eso,
  `POST /compra/consulta`, cuyos parámetros hay que verificar al implementar.
- Notas: endpoints incorporados a la memoria del estudio (instrucción 37) y a la Arquitectura. **Queda abierto solo el
  riesgo A7** (Convenio Multilateral por COMARB) y las preguntas de negocio (10, 11). El tramo técnico está cerrado.

### 2026-09-23 - memoria del estudio: catálogo de servicios externos fiscales
- Etapa: transversal (no es del proyecto: es memoria reutilizable del estudio).
- Cambio: el research de ARCA/ARBA/SOS se generalizó a **`.github/instructions/37-servicios-externos-fiscales.instructions.md`**
  y se registró en el README de instrucciones. Cataloga, con fuentes verificadas, **qué expone cada servicio externo, qué
  tarea del estudio acorta y cómo se usa**: ARCA (WSFEv1, WSCDCV1, constancia de inscripción, padrones A4/A10/A13/A100,
  TRABAJO_F931, SETIWS-PAGO-API, WSBFE/WSSEG, sud_*), ARBA (consulta de alícuotas DFE con endpoints de prod y test, padrón
  mensual de regímenes generales en .txt, deducciones), COMARB/SIFERE (DDJJ, consultas y Padrón Web — **sin API**),
  SOS Contador (API con token, endpoints confirmados, Autoimpo y su límite de 12-15 días) y Bejerman/Onvio (**bloqueado
  por contrato**, solo sobre archivo exportado por una persona).
- Incluye: **la lista de lo que NO existe** (para que nadie lo vuelva a buscar), un **mapa tarea → servicio → cómo**, la
  división de quién configura qué (**Olvidata configura; el estudio consigue la delegación de clave fiscal**, que es
  trámite suyo y sin ella ningún servicio de ARCA sirve para consultar por terceros) y un **checklist previo a cotizar
  un conector**.
- Motivo: en este mismo proyecto se diseñó y casi se cotiza un conector de ARCA que **no existe**. Veinte minutos de
  verificación lo evitaron; el archivo existe para que la próxima vez sean cero.
- Notas: es de lectura obligatoria antes de cotizar cualquier conector en un proyecto contable/impositivo.

### 2026-09-23 - arquitecto (research + A3 aplicado, vía `/agentes-ia-orquestador`)
- Etapa: Arquitectura — verificación técnica de las preguntas 8, 9 y 12 contra documentación pública, y ejecución de A3.
- **HALLAZGO QUE EXPLICA EL PROBLEMA DEL ESTUDIO.** La documentación oficial de SOS Contador dice que su importación
  automática (**Autoimpo**) *"recupera comprobantes con una antigüedad máxima de 12 a 15 días hacia atrás"* y que los más
  viejos *"no se volverán a importar automáticamente"*. **Los faltantes no son un bug: son una limitación documentada del
  producto.** Todo comprobante cargado tarde en ARCA nunca entra solo a SOS. La misma fuente dice que SOS **deduplica por
  CAE**, así que los duplicados probablemente vienen de mezclar Autoimpo con importación manual, o de comprobantes sin
  CAE — **a confirmar con el estudio**.
- **Pregunta 8 (ARCA) — RESUELTA EN CONTRA DE LO ESPERADO: el web service NO existe.** El catálogo oficial de ARCA (50+
  servicios SOAP) no tiene ninguno que liste los comprobantes recibidos de un contribuyente. Lo más cercano es **WSCDC**
  (constatación: valida un comprobante puntual, no lista). **"Mis Comprobantes" es un servicio del portal web** con clave
  fiscal, que exporta a Excel/CSV hasta 365 días por consulta. → **El conector de ARCA se cae del alcance y no se cotiza.**
  El control ARCA↔SOS **se hace igual** con el export que baja la persona: acción humana, sin problema contractual ni
  credenciales de terceros. Lo único que no se puede es ahorrarle ese paso.
- **Pregunta 9 (ARBA) — RESUELTA A MEDIAS.** Alícuotas de percepción/retención de **regímenes generales** y padrón de
  IIBB: **sí** hay servicio web (consulta por CUIT y período, sin operador). **Convenio Multilateral** —justo lo que
  nombró el relevamiento— va por **COMARB**, otro organismo: **queda por verificar** (riesgo A7).
- **Pregunta 12 (SOS) — ACOTADA.** La API existe, es oficial y usa token (`api.sos-contador.com/api-comunidad/`).
  Confirmado: crear clientes y comprobantes, obtener CAE, listar clientes, saldos de cuenta corriente. **Falta confirmar
  si lista los comprobantes ya importados** — la documentación está en una colección de Postman que no se pudo leer
  automáticamente. Es la única verificación abierta y define si hace falta exportar de SOS o no.
- **A3 EJECUTADO** (aprobado por Joaquín): el rubro `contable` pasó a rubro de producción. Su contenido se mudó a
  `C:/Sistemas/Agente Contable-IA` y en el núcleo quedó solo el manifiesto con `raiz: ../../../../Agente Contable-IA`,
  igual que `inmobiliario`. **Reimportación: 0 versiones nuevas, 24 sin cambios** — los hashes son idénticos, ninguna
  tarea guardada se ve afectada. Efecto colateral atendido: `FichaImportadaTests` importaba ese manifiesto y ahora
  depende de un repo externo; el test detecta si el repo fuente está clonado (leyendo la `raiz:` del propio manifiesto) y
  avisa con un mensaje claro en vez de fallar con "archivo no encontrado". 712/712 tests.
- Notas: research completo con fuentes en `research-arca-arba-sos-2026-09.md`. Arquitectura y Análisis actualizados.
  **Presupuesto sigue sin abrirse**, pero ahora el tramo cotizable es mayor: los pasos 1 a 5 ya no dependen de nadie.

### 2026-09-23 - arquitecto (vía `/agentes-ia-orquestador`)
- Etapa: Arquitectura (borrador) + corrección del Diseño por reutilización cross-proyecto
- **Hallazgo que cambia la estimación:** antes de proponer agentes se revisó `nucleo/rubros/contable/` del producto. **El
  rubro ya está construido**: 10 agentes, 8 etapas, capas, coordinador, y conocimiento de SOS Contador y Bejerman Onvio
  ya cargado. De los 9 agentes del esquema de Diseño, **6 ya existen** (`cont-registracion` incluso ya concilia bancos,
  `cont-balance`, `cont-impuestos`, `cont-iibb`, `cont-vencimientos`, `cont-sueldos`+`cont-cargas-sociales`). **El trabajo
  real son 3 agentes nuevos**: `cont-control-arca` (el dolor nuclear, no hay nada que lo cubra), `cont-arba`
  (constatación de padrones — `cont-iibb` liquida, no constata) y `cont-soporte-sistemas` (dudas de uso del empleado;
  `cont-atencion` es para escribirle al cliente). Ver `definiciones/2-disenador-funcional.md` §3 bis.
- **Segundo hallazgo:** hoy **ningún agente del rubro tiene conectores** — los diez usan solo documentos + conocimiento.
  El salto a conectores (ARCA, ARBA, SOS) es desarrollo nuevo, no configuración.
- Arquitectura decidida: **no hay repositorio nuevo**. BMA es una **organización (tenant)** del producto con licencia del
  rubro `contable`; lo que se construye va al núcleo y sirve para cualquier estudio contable. Lo específico de BMA vive en
  su organización (reglas, instructivos, agentes derivados, programaciones), cargado por el estudio.
  `contadores-bma-conversor` queda como está, no se migra.
- **Riesgos abiertos** (ver `definiciones/3-arquitecto-mvc.md` §5): A1 el conector de ARCA puede no existir para consultar
  comprobantes de terceros (la experiencia previa es de **emisión**/WSFEv1); A2 hace falta delegación de clave fiscal de
  cada cliente al estudio; **A3 el rubro `contable` es "modelo de pruebas" y su propio manifiesto dice que al pasar a
  producción se muda al repo fuente `C:/Sistemas/Agente Contable-IA` — hay que decidirlo ANTES de escribir los tres
  agentes**; A4 el calendario y las alícuotas están omitidos a propósito y alguien los tiene que mantener; A5 topes de
  gasto; A6 adopción.
- Orden de construcción propuesto: los pasos 1 a 5 (mudanza del rubro, alta del tenant, soporte + conocimiento ARCA/ARBA,
  piloto de conciliación, `cont-control-arca` sobre archivo exportado) **no dependen de ninguna respuesta de terceros**.
- Notas: Sin código. **Presupuesto NO abierto**: presupuestar el conector de ARCA sin confirmar las preguntas 8 y 12
  sería cotizar algo que puede no existir. Ver `definiciones/3-arquitecto-mvc.md`.

### 2026-08-31 - analista-funcional (vía `/agentes-ia-analista-funcional`)
- Etapa: Discovery/Análisis
- Cambio: Agregada segunda herramienta usada por el estudio: **SOS Contador** (`sos-contador.com`). Research: suite impositivo-contable 100% cloud, módulos IVA/IIBB/Ganancias/contabilidad/sueldos/gestión, base de ayuda pública estructurada por módulo (`ayuda.sos-contador.com.ar`). **Hallazgo clave**: a diferencia de Bejerman/Onvio (bloqueado sin autorización de TR), SOS Contador publica una **API oficial documentada** (Postman) para integraciones de terceros, con precedente real de otro software integrado — reabre la puerta a integración automatizada (equivalente a Opción B) para la porción del flujo que pasa por SOS, vía un adaptador adicional en la misma arquitectura en capas. 2 hipótesis de complementariedad con Bejerman a validar (traslado manual de datos vs. carteras de clientes separadas) y posible duplicación del módulo de Sueldos entre ambos sistemas — nuevas preguntas abiertas 6 y 7. Actualizados `guion-discovery.md` (nuevo Bloque 2 dedicado, renumeración de bloques 3-6) y `cuestionario-discovery-empleados.md` (tabla de tareas y sección de dudas ahora cubren ambas herramientas) para relevar esto en la reunión y el cuestionario individual. Nota de honestidad: no se confirmó una mención aislada sobre una posible suspensión de la integración AFIP/ARCA de SOS por "ARCA 74/2022" — dato de una sola fuente indirecta, no verificado.
- Notas: Ver definiciones/1-analista-funcional.md §SOS Contador; guion-discovery.md Bloque 2; cuestionario-discovery-empleados.md

### 2026-08-31 - analista-funcional (vía conversación directa)
- Etapa: Discovery/Análisis
- Cambio: Alcance refinado por el usuario: Bejerman Web sigue siendo la herramienta principal (no se reemplaza), el sistema se acota a 3 piezas — bot de consultas sobre Bejerman/Onvio, scripts de conversión de archivos, y automatización de procesos ya definidos. Compatible 100% con Opción A y el plan de 5 fases, sin cambiar la arquitectura en capas. Se armó `cuestionario-discovery-empleados.md` (relevamiento individual tarea por tarea, complementa al guión grupal) para levantar el catálogo real de tareas, procesos paso a paso y archivos a convertir directamente de cada empleado que usa Bejerman.
- Notas: Ver definiciones/1-analista-funcional.md §Alcance refinado; cuestionario-discovery-empleados.md

### 2026-08-30 - analista-funcional (vía conversación directa)
- Etapa: Diseño (insumo, Análisis aún no cerrado)
- Cambio: Arquitectura en capas propuesta (puertos y adaptadores: orquestación / reglas de negocio sobre modelo canónico / adaptadores) para que la Opción A migre a B/C sin reescribir agentes ni orquestación — solo se reemplaza el adaptador. Matiz: migración limpia para tareas de lectura, no para escritura (sin equivalente en A). Plan de acción de 5 fases (Fundación → Expansión sobre A → Adaptador B condicional → Adaptador C condicional → todo el estudio punta a punta), con Fases 2-3 condicionadas a autorización de Thomson Reuters y sin bloquear el producto si esa autorización no llega.
- Notas: Ver definiciones/1-analista-funcional.md §Arquitectura en capas y §Plan de acción

### 2026-08-30 - analista-funcional (vía conversación directa)
- Etapa: Discovery/Análisis
- Cambio: **Corrección importante tras research puntual pedido por el usuario** (verificar viabilidad de computer-use sobre Onvio y permisos de la web): (1) Contadores BMA usa Bejerman Web (100% cloud), no la línea Premium/ERP on-premise — no existe SQL Server local, la Opción B tal como estaba planteada no aplica a este cliente. (2) Los "Onvio Full Terms" de Thomson Reuters (sección "Unauthorized Technology") prohíben explícitamente, salvo autorización previa de TR, instalar software sobre sus productos, automatizar la descarga/scraping de sus datos, o conectar automáticamente sus datos con otro software/servicio — esto bloquea contractualmente tanto la Opción C (computer-use) como cualquier variante de acceso automatizado a datos (Opción B), no solo por riesgo técnico sino por incumplimiento de contrato. Fricciones técnicas adicionales: 2FA obligatorio + reCAPTCHA en login + timeout de sesión 30 min. Recomendación actualizada: diseñar Fase 1 completa sobre Opción A (sin dependencias de autorización de terceros) y, en paralelo, consultar al ejecutivo de cuenta de Thomson Reuters si existe un canal de integración autorizada para Bejerman Web/Onvio AR (existe precedente: Onvio BR Accounting API pública para Brasil). Pendiente confirmar el texto exacto de la cláusula en el contrato argentino real de Contadores BMA (se usó como proxy la versión global de los Onvio Full Terms).
- Notas: Ver definiciones/1-analista-funcional.md §Research de integración y §Opciones de integración (actualizado)
