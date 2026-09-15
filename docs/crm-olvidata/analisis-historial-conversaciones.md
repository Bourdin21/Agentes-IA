# Análisis del historial de conversaciones del bot

**Fecha:** 2026-09-13 · **Estado:** análisis cerrado y **§7 y §8 aplicadas y deployadas** el mismo día,
verificadas contra producción. Queda pendiente solo `marcar_para_retomar` (§8, opcional): implica
decidir quién retoma y eso es proceso comercial, no técnico.

Origen: la pregunta "¿este LLM puede aprender de todas las conversaciones ya generadas?". El modelo
no se entrena con nuestros datos y Claude no tiene fine-tuning propio, así que "aprender" acá significa
otra cosa: **destilar el historial real y escribirlo en el prompt y en las herramientas**. Eso queda
auditable y reversible — se puede leer exactamente qué se le está diciendo al agente — en vez de una
caja negra entrenada.

## 1. Qué se analizó

Todo el historial de `ContactoRespuestas` y `Contactos` en producción, leído el 2026-09-13. Universo
útil: **701 mensajes entrantes** de más de 25 caracteres que el sistema clasificó como respuestas
reales de personas (ya excluidos los que el filtro `EsRespuestaAutomatica` había marcado como
away-message). Cero costo de API: es lectura de base.

---

## 2. Hallazgo principal: al menos el 42% de las "respuestas humanas" son otros bots

De esos 701 mensajes, **292 (41,7%) son contestadores automáticos, asistentes virtuales o difusiones
comerciales** que el filtro de away-messages no atrapó. Y la muestra manual dice que el número real es
más alto todavía —cerca del 55-60%— porque el heurístico no detecta las difusiones de marketing ni las
firmas enlatadas.

Evidencia textual, todo esto guardado en el CRM como si fuera un prospecto contándonos su dolor:

> *"Soy ZentraBot, el asistente de Zentra, y estamos acá para ayudarte con todo lo relacionado a sillas..."*
> *"Soy Coni, la asistente de greendeco. Acá te ayudamos con revestimientos, pisos, césped sintético..."*
> *"Soy una asistente virtual de Clínica Terradonna, mi función es ayudarte con información y turnos."*
> *"❗ Seleccione una opción válida."* · *"Elija el número de una opción"* · *"No comprendí la opción ingresada."*
> *"Como soy un agente encargado de la atención a clientes para la venta de neumáticos, no puedo ayudarte con propuestas de software."*

Las tres del medio son especialmente claras: son **los menús de validación de otros bots**. Nuestro bot
le mandó su cuestionario a un bot ajeno, el otro no entendió, y contestó con su propio error de menú.
Eso quedó registrado como el "dolor principal" del prospecto.

**Tres consecuencias concretas:**

1. **Las métricas del embudo están infladas.** La tasa de respuesta que muestra `/Bot` cuenta como
   "respondió" a números que nunca leyó una persona.
2. **Los datos de calificación están contaminados.** Hay rubros, dolores y categorías cargados a partir
   de conversaciones con máquinas.
3. **Con el LLM encendido, cada vuelta de esas cuesta tokens.** Hoy cuesta un mensaje de WhatsApp;
   mañana cuesta ~ARS 55 por turno.

**Por qué esto solo lo puede resolver el LLM:** `EsRespuestaAutomatica` funciona con una lista de
frases típicas, y no hay lista que cubra "Soy Coni, la asistente de greendeco". Un modelo que lee ese
texto lo sabe al instante. **Este es el argumento más fuerte a favor del LLM que encontré, y no es
vender mejor: es dejar de hablarle a máquinas.**

---

## 3. El embudo real, por canal

Contactos con al menos un mensaje entrante real (excluidos away-messages):

| Canal | Completaron | Total | Tasa |
|---|---|---|---|
| **Ads pagos** | 7 | 17 | **41%** |
| Outbound frío | 36 | 594 | **6%** |
| Alta manual | 2 | 2 | — |

Los que llegaron a presupuesto o cierre en toda la historia: **13 con presupuesto enviado, 16 cerrados,
8 derivados a mano**.

La lectura: **el inbound de ads convierte 7 veces mejor que el outbound frío**, con 35 veces menos
volumen. Es el segmento donde el LLM rinde más por peso gastado, y coincide con lo que ya habíamos
decidido para la fase 3 del plan.

Y se corrige un número que te di antes en la sesión: los "trabados en ¿Seguimos?" no son 321 sino
**103**. La diferencia eran away-messages, no personas.

---

## 4. Las objeciones reales, con sus palabras

Conteo sobre los entrantes reales:

| Objeción | Veces | Cómo lo dicen textualmente |
|---|---|---|
| **No me interesa** | 73 | *"Hola Joaquín te agradezco pero no me interesa"* · *"por el momento no estoy interesada, gracias"* · *"Muchas gracias por su tiempo. No lo necesitamos."* |
| **Enojado / pedido de baja** | 21 | *"No me escriban nunca más por favor"* · *"Solo encontré una puerta llame y me quedó el num ay LPM ..me llaman a cada rato"* |
| **Rubro equivocado** | 18 | *"Tengo un estudio jurídico no contable!!"* · *"Hola! No administramos alquileres."* · *"No quiero hablar con su máquina que además no sabe leer que NO tengo un estudio contable"* |
| **Ya tengo sistema** | 5 | *"Buen día Joaquín! Contamos con un sistema, muchas gracias!"* · *"ya tenemos sistema por el momento nos sirve bastante"* |
| **Cortesía que es un no** | 3 | *"la voy a tener en cuenta"* · *"en caso de necesitar, le solicitaremos información"* · *"Si pienso que algo, te ubico"* |

Dos cosas que cambian el diseño:

**El rubro mal clasificado es un problema real y visible, no teórico.** 18 personas nos lo dijeron en
la cara, y una explícitamente se quejó de estar hablando con una máquina que "no sabe leer". Hoy el
árbol no tiene forma de aceptar una corrección: sigue con su cuestionario.

**La cortesía argentina es un no.** *"Lo voy a tener en cuenta"* y *"si necesito te ubico"* no son
leads tibios: son negativas educadas. El bot tiene que leerlas como cierre amable, no como oportunidad
de insistir.

---

## 5. El canal de ads trae cuatro tipos de no-prospecto

Los mensajes de entrada reales de ads pagos (el segmento que mejor convierte) incluyen:

- **Prospectos de verdad**: *"¡Hola! Quiero más información"* (texto pre-cargado del anuncio),
  *"¿realizan desarrollos para integración con ARCA para facturar?"*, *"tengo una idea basándome en
  aplicaciones que ya están hechas"*.
- **Postulantes de trabajo**: *"soy programador full stack y me encuentro en búsqueda..."*.
- **Proveedores vendiéndonos**: *"soy Ernesto, consultor en sistemas, marketing y automatización. Vi
  que trabajan en desarrollo de software..."*, *"trabajo para una consultora de calidad"*.
- **Competencia prospectándonos**: *"soy Jonatan de NexoIArg. Vi que en su web no hay sistema de
  turnos. ¿Les pasa que pierden consultas...?"*.

El árbol le corre el mismo cuestionario de calificación a los cuatro. El LLM puede distinguirlos en el
primer mensaje — pero hoy **no tiene dónde registrar "esto no es un prospecto"** sin mentir en el dato
(usar `dar_de_baja` para un postulante ensucia la estadística de bajas). Ver §8.

---

## 6. Cómo son las conversaciones que SÍ cerraron

Esto es el material para los ejemplos del prompt. Los que llegaron a presupuesto o cierre:

| Contacto | Rubro | Lo que dijeron |
|---|---|---|
| 3151 | Salud | *"hola los turnos y digitalizar la documentación de los pacientes para subir en la historia clínica"* + *"tenemos un sistema de turnos con historias clínicas de cada paciente"* |
| 2256 | Contabilidad | *"Me interesa IA para conciliar Banco y Mercado Pago"* → *"¿Me podrían enviar costos?"* |
| 842 | Comercio | *"Y la actualización de precios constante"* + *"Lo manejo con excel y solo lo uso yo"* |
| 1296 | Alquiler de esquí | *"Contestás las reservas anticipadas con el stock"* |

**La firma del que compra**: nombra un dolor operativo **concreto y específico**, en sus propias
palabras, y casi siempre menciona con qué lo maneja hoy (Excel, cuaderno, un sistema que no hace X).
Nadie que cerró dijo algo genérico tipo "quiero ordenarme".

Y dos hallazgos que contradicen suposiciones nuestras:

**"Ya tenemos sistema" NO es un no.** El contacto 3151 dijo textualmente que tiene un sistema de turnos
con historias clínicas **y cerró igual**, porque nombró un hueco puntual (digitalizar la documentación).
La pregunta correcta ante esa objeción no es insistir ni retirarse: es *qué es lo que el sistema actual
no te resuelve*.

**"Ahora no" tampoco es un no.** El primer mensaje del contacto 2256 fue *"Gracias por el contacto,
justo estoy saliendo de vacaciones"* — y terminó pidiendo costos y cerrando. Hoy el sistema no tiene
ningún concepto de "retomar más adelante": o sigue el cuestionario o lo descarta.

---

## 7. Qué cambia en el prompt (propuesto)

Todo esto se agrega a `ConversacionIaService.ArmarSystemPromptAsync`, que ya se genera y no se escribe
a mano.

1. **Detección de interlocutor no humano, primera prioridad.** Si el mensaje parece un contestador
   automático, un asistente virtual de otro negocio, un menú de otro bot o una difusión comercial, no
   conversar: cerrar con `descartar_no_es_prospecto`. Se le dan los marcadores reales encontrados
   ("soy el asistente de", "seleccione una opción válida", "gracias por comunicarse con", una firma
   institucional, un menú con emojis numerados).
2. **Descripción de cada rubro, no solo el nombre.** El error de hoy con la ferretería
   (clasificada como "Comercios de venta por peso o unidad" en vez de "Comercio o alquiler de
   maquinaria") pasó porque los 16 valores del enum son nombres de diálogo que no dicen qué cae en cada
   uno. Se agrega una línea por rubro con ejemplos concretos de negocios.
3. **Aceptar la corrección de rubro sin pelear.** Si el prospecto dice que su rubro no es el que
   asumimos, pedir disculpas en una línea, corregirlo con `set_rubro` y seguir. Los 18 casos medidos
   son la razón.
4. **Leer la cortesía como negativa.** "Lo voy a tener en cuenta", "si necesito te ubico", "muchas
   gracias por la info" = cierre amable con `finalizar_conversacion`, sin insistir.
5. **Ante "ya tengo sistema", una sola repregunta.** *"¿Qué es lo que el sistema que usás hoy no te
   resuelve?"* — y si la respuesta es "nada, estamos bien", cerrar. Es el caso 3151.
6. **Distinguir "no" de "no ahora".** Si el prospecto dice que está de vacaciones, cerrando el mes o
   sin tiempo, no descartar: registrar el momento para retomar y cerrar amable.
7. **Cuatro ejemplos reales de diálogo que cerraron** (los de §6), con el dolor en las palabras del
   prospecto. Es lo que fija el tono mejor que cualquier instrucción.

Costo de esto: el prompt pasa de ~2.500 a unos ~3.400 tokens. Con caché activo el impacto por mensaje
es de centavos; igual conviene medirlo en la primera semana en sombra.

---

## 8. Qué cambia en las herramientas (propuesto)

**Una herramienta nueva: `descartar_no_es_prospecto(tipo, motivo)`**, con `tipo` cerrado en:

`otro_bot` · `difusion_comercial` · `vende_servicios` · `busca_trabajo` · `competidor` ·
`numero_equivocado` · `rubro_no_aplica`

Por qué una nueva y no reusar `dar_de_baja`: son dos cosas distintas y mezclarlas arruina el dato. Una
baja es *"me pidieron que no los contacte más"* (21 casos, hay que respetarla para siempre). Un
postulante de trabajo o un bot ajeno es *"esto nunca fue un prospecto"* — no es una baja, es un
descarte de origen, y conviene poder contarlos por separado para saber cuánto del outbound se está
desperdiciando.

**Una segunda, opcional: `marcar_para_retomar(cuando, motivo)`** para el "no ahora" del punto 6. La
dejo marcada como opcional porque implica decidir quién y cómo retoma después — es una decisión de
proceso comercial, no técnica, y no quiero resolverla por defecto.

---

## 9. Qué NO cambia

- **No hay fine-tuning ni entrenamiento con nuestros datos.** No existe en esta API y no hace falta.
- **No se agrega recuperación dinámica de conversaciones parecidas (RAG).** A ~40 mensajes entrantes
  por mes con el envío pausado, cuesta más mantenerlo que lo que aporta contra 4 ejemplos fijos bien
  elegidos.
- **No se toca la garantía estructural del precio.** Sigue sin existir herramienta para cotizar, y
  varios de los que cerraron pidieron costos explícitamente: ese es el momento de `escalar_a_humano`,
  no de que el bot improvise un número.
- **No se tocan las 7 guardas globales.** Cada una es el arreglo de un incidente real.

---

## 10. Lo que este análisis deja para el negocio, más allá del bot

Dos números que valen por sí mismos, independientes del LLM:

1. **Entre el 42% y el 60% del esfuerzo de calificación se está gastando contra máquinas.** Eso
   relativiza toda la tasa de respuesta histórica del outbound frío, y explica parte del 6% de
   completitud.
2. **Ads pagos convierte al 41% contra el 6% del frío**, con 17 contactos contra 594. Si el objetivo es
   cerrar ventas y no mandar mensajes, el presupuesto de ARS 250.000 rinde muy distinto según a qué
   canal se lo asigne. Vale llevarlo a `olvidata-ceo` como decisión de inversión.

---

## Historial de ajustes

| Fecha | Cambio |
|---|---|
| 2026-09-13 (2) | §7 y §8 aplicadas y verificadas: ferretería y corralón ahora clasifican en "Comercio o alquiler de maquinaria" y la verdulería en "Comercios de venta por peso o unidad"; los bots ajenos y un postulante de trabajo salen por `descartar_no_es_prospecto`; ante "contamos con un sistema" el agente hizo la única repregunta prevista. Dos optimizaciones de costo encontradas al medir: cortar el loop en `NoEsProspecto` (el camino más frecuente gastaba una segunda llamada inútil) y partir el system prompt en 2 bloques para que la caché cruce entre contactos (de USD 0,044 a USD 0,016 la conversación completa; USD 0,006 el descarte). |
| 2026-09-13 | Versión inicial. Análisis de los 701 mensajes entrantes reales del historial; 6 hallazgos, cambios de prompt y herramientas propuestos sin aplicar. |
