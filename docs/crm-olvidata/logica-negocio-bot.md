# Lógica de negocio del bot de WhatsApp — paso a paso

> Documento de referencia funcional, no de arquitectura. Complementa
> `definiciones/2-disenador-funcional.md` (diseño original) y `definiciones/3-arquitecto-mvc.md`
> (estructura de capas). Este documento describe **cómo se comporta el sistema hoy en producción**,
> verificado con una prueba funcional real el 2026-07-27 (ver `trazabilidad.md`, entrada de esa
> fecha). Rutas de archivo entre paréntesis para ubicar cada pieza en el código.

El bot tiene dos mitades que conviene pensar por separado: **(A)** cómo se generan y contactan
prospectos de forma proactiva (outbound), y **(B)** cómo se conversa con quien responde (inbound,
la máquina de estados). La outbound alimenta contactos a la inbound, pero la inbound también
recibe gente que escribe primero al número del bot sin haber sido contactada nunca (ads pagos,
boca a boca, etc.).

---

## Parte A — Prospección y envío outbound

Corre automáticamente vía `OutboundSchedulerService`
(`OlvidataCRM.Infrastructure/HostedServices/OutboundSchedulerService.cs`), un `BackgroundService`
in-process que espera hasta la próxima ventana horaria y dispara el pipeline.

### A.1 — Cuándo corre

- Días habilitados: **lunes, martes, miércoles, jueves**, 09:30 ART (`RunDays`/`RunAt`,
  `OutboundSchedulerService.cs:24-25`). Viernes a domingo no corre nada.
- Hay un interruptor manual "standby" (`IsStandby`, toggleable desde `Bot/Index` en la UI) que
  salta la corrida del día sin tocar el timer.
- **Limitación conocida**: el timer vive dentro del proceso de la app. Si IIS recicla el worker por
  inactividad de tráfico durante la madrugada (hosting compartido económico), el timer muere con él
  y la ventana de ese día se pierde por completo hasta el próximo día habilitado — no hay
  recuperación automática. Mitigado (no resuelto de raíz) con un ping externo de keep-alive cada
  5-10 min configurado por el cliente. Ver incidente 2026-07-23 en `trazabilidad.md`.

### A.2 — Qué hace el pipeline (`RunPipelineAsync`, `OutboundSchedulerService.cs:65-125`)

1. **Buscar prospectos nuevos en Google Maps** (`IGoogleMapsService.SearchDailyAsync`,
   `GoogleMapsService.cs:59-88`):
   - Toma las `CampanaOutbound` con `Activa=true` cuyo campo de bits `Dias` incluye el día de hoy.
   - Por cada campaña, reparte su `LimiteDiario` en partes iguales entre sus industrias
     (`CampanaOutboundIndustria`, cada una con una `ClaveRubro` como `"comercio-palermo"` o
     `"farmacia-uruguay"` — rubro + sufijo de región).
   - Por cada industria, recorre sus `CampanaQuery` (texto de búsqueda + zona) **rotando**: no
     repite una query hasta haber agotado todas las de ese rubro (`GoogleMapsQueryUsada` lleva el
     historial; al agotarse todas, se hace soft-delete del historial y se reinicia la rotación).
   - Cada resultado de Maps con teléfono se normaliza (`NormalizePhone` — Argentina/Uruguay
     explícitos, cualquier otro país cae a un fallback no del todo genérico, limitación conocida) y
     se heurística-reclasifica el tipo de negocio (`MapPlaceTypes`), preservando siempre el sufijo
     de región original.
2. **Insertar los prospectos nuevos** como `Contacto` con `CanalOrigen=OutboundFrio`,
   `EstadoEmbudo=Pendiente` — se descartan los que ya existen por teléfono (índice único,
   protegido también contra condición de carrera con `catch (DbUpdateException)`).
3. **Enviar el lote diario** (`IOutboundCampaignService.SendDailyBatchAsync`,
   `OutboundCampaignService.cs:66-148`):
   - Tope global: `BotSettings.DailyLimit` (200) menos lo ya enviado hoy
     (`Contacto.FechaPrimerEnvio` de hoy), repartido entre campañas **en orden de `CampanasOutbound.Id`**
     (primera campaña que corre se lleva su cupo completo primero — no es proporcional).
   - Candidatos: `Contacto` con `EstadoEmbudo=Pendiente`, `CanalOrigen` en {OutboundFrio, Referido},
     `Rubro` no nulo, cuyo `Rubro` (con sufijo) coincide con alguna `ClaveRubro` de la campaña.
   - Envía la plantilla configurada en la campaña (`CampanaOutbound.TemplateWhatsApp`, ej.
     `olv_frio_v3`) — salvo que el contacto sea `CanalOrigen=Referido`, en cuyo caso siempre usa
     `olv_referido_v2` sin importar la campaña.
   - Al enviar OK: `EstadoEmbudo → MensajeEnviado`, guarda `FechaPrimerEnvio` y `UltimoMensajeId`.
   - Si falla el envío (`WhatsAppApiException`): el contacto queda `Pendiente`, se reintenta en la
     próxima corrida — no hay reintento dentro de la misma corrida.
4. **Follow-up** (`ProcessFollowUpsAsync`, `OutboundCampaignService.cs:150-195`):
   - Candidatos: `EstadoEmbudo=MensajeEnviado` cuyo `FechaPrimerEnvio` tiene **3+ días**, y cuyo
     rubro sigue siendo parte de alguna campaña activa hoy.
   - Envía plantilla fija `olv_nurturing_v2` (no depende de la campaña). `EstadoEmbudo → FollowUpEnviado`.
5. **Marcar fríos** (`MarkColdAsync`, `OutboundCampaignService.cs:197-218`):
   - `EstadoEmbudo=FollowUpEnviado` con **4+ días** desde el follow-up → `EstadoEmbudo → Frio`.
   - A partir de acá el contacto ya no vuelve a aparecer en ningún envío automático (ni lote
     diario, que solo toma `Pendiente`, ni follow-up, que solo toma `MensajeEnviado`).

### A.3 — Por qué los contactos "Descartado" nunca reciben follow-up (verificado 2026-07-27)

`Descartado` es un estado **exclusivamente manual** — solo se setea a mano desde
`Contactos/Details` (`ContactosController.EstadosManualesPermitidos`,
`ContactosController.cs:22-26`), nunca por código automático. Como tanto `SendDailyBatchAsync`
(filtra `Pendiente`) como `ProcessFollowUpsAsync` (filtra `MensajeEnviado`) excluyen por
construcción cualquier otro valor de `EstadoEmbudo`, un contacto marcado `Descartado` deja de
aparecer en ambos pipelines automáticamente, sin necesidad de un filtro explícito adicional.
Tampoco puede "revivir" solo: el único lugar que reabre a `Respondido` cuando el contacto escribe
(`BotFlowService.cs:233`) excluye explícitamente `Descartado` de esa transición. **No se requirió
ningún cambio de código para este comportamiento — ya funciona así.**

---

## Parte B — Conversación entrante (webhook + máquina de estados)

### B.1 — Entrada: el webhook de Meta

`POST /webhook/whatsapp` (`OlvidataCRM.Web/Program.cs:247-330`), sin autenticación (Meta no manda
cookie de sesión). Responde `200 OK` **inmediatamente** y procesa en background
(`Task.Run` con su propio `IServiceScopeFactory` — nunca el `IServiceProvider` de la request, que
se dispone apenas responde el handler; bug real que perdió todos los mensajes entrantes entre
2026-07-21 y 2026-07-23, ver `trazabilidad.md`).

Por cada mensaje del payload:
- Deduplicación en memoria por `message.id` (`HashSet<string>`, se pierde si el proceso reinicia —
  limitación conocida y aceptada).
- Si viene un `status` (confirmación de entrega/lectura), solo se loguea — no dispara lógica de
  negocio. Los `errors` del status (ej. código 131026 "Message undeliverable") se registran como
  `LogWarning`.
- El nombre de perfil de Meta (`contacts[].profile.name`) es **opcional** — si falta, se sigue
  procesando con nombre nulo (antes tiraba `NullReferenceException` y abortaba todo el resto del
  payload; fix 2026-07-27, verificado con prueba funcional el mismo día).

### B.2 — Resolución del contacto (`HandleIncomingAsync`, `BotFlowService.cs:203-308`)

1. Si el remitente es el propio número admin (`BotSettings.AdminNotifyPhone`), se ignora — el
   admin no dispara el flujo del bot.
2. Busca `Contacto` por teléfono. Si no existe, lo crea con `CanalOrigen=AdsPagos`,
   `EstadoEmbudo=Respondido`, `FaseConversacion=Nuevo` (es decir: cualquiera que le escriba primero
   al bot sin haber sido contactado por outbound entra como lead "inbound directo").
3. Si el contacto **ya existía** y estaba en `Pendiente`/`MensajeEnviado`/`FollowUpEnviado` (es
   decir, venía de outbound y todavía no había respondido), pasa a `EstadoEmbudo=Respondido`.
4. **Si el contacto ya está `Descartado`** (baja voluntaria o corte automático, ver más abajo):
   el mensaje se guarda como `"Mensaje recibido (contacto ya descartado)"` y **no se dispara
   ninguna respuesta ni notificación** — corte total, no solo un mensaje menos. Fix 2026-07-29
   (incidente real, ver `trazabilidad.md`).
5. **Solicitud de baja voluntaria**: se chequea el texto libre contra `FrasesDeBaja` (~35
   fragmentos en español: "no me interesa", "dar de baja", "no nos contacten", "reportar este
   número", "atendemos únicamente", etc. — deliberadamente amplia, mejor un falso positivo que
   seguir insistiéndole a alguien que ya dijo que no) **en cualquier fase de la conversación**, no
   solo al final. Si matchea: `EstadoEmbudo → Descartado` (ya excluido por construcción de todo
   envío/follow-up outbound futuro), se loguea el motivo, se manda **una sola** confirmación
   ("Listo, no vas a recibir más mensajes...") y no se le vuelve a escribir nunca más.
6. **Mensajes no procesables** (imagen, audio, video, documento, ubicación, sticker, reacción): se
   registran igual como `ContactoRespuesta` (pedido explícito del cliente: "guardar todas las
   respuestas") con una etiqueta tipo `[Imagen]`, y **no avanzan la máquina de estados** — el
   contacto sigue esperando una respuesta de texto/interactiva válida en la misma fase en que
   estaba. Esto se guarda con su propio `SaveChangesAsync` independiente, antes de tocar el resto
   del flujo. (Hasta 2026-07-29 esto también disparaba una notificación in-app — ver nota al final
   de §B.3, se sacó a pedido del cliente.)
7. Si la conversación ya estaba `Completed`:
   - **Menos de 24hs** desde que se completó: responde "ya registramos tu consulta", loguea el
     mensaje como "Mensaje adicional (post-cierre)" y se lo reenvía al admin por texto libre
     (best-effort, en `try/catch` para no perder el registro recién guardado si falla el envío).
     **Corte automático**: si ya hay 2+ mensajes "post-cierre" previos de este contacto, el
     siguiente ya no repite este ciclo — dispara directo el mismo corte de baja voluntaria del
     punto 5 (`Descartado` + única confirmación), sin importar si el texto matchea alguna frase.
     Pensado para el caso de un auto-responder del otro lado con texto impredecible: sin este
     corte, un incidente real (Kremia Moda, 2026-07-29) generó un loop de 30 mensajes en 18
     minutos, con 26 reenvíos no deseados al WhatsApp personal del admin, hasta que alguien lo
     descartó a mano.
   - **Más de 24hs**: se **reabre** la conversación (`FaseConversacion → Nuevo`, se resetea
     `Categoria`/`QuestionIndex`), conservando el historial de respuestas previo.

### B.3 — La máquina de estados (`FaseConversacion`)

```
Nuevo ──(1er mensaje, cualquier tipo)──▶ AwaitingCategory ──(elige categoría)──▶ AwaitingIndustry*
                                                                                       │
                                                          (*solo si categoría = "rent")│
                                                                                       ▼
                                          AskingQuestions ◀───────────────────────────┘
                                                │
                                    (responde las N preguntas de la categoría)
                                                ▼
                                            Completed
```

- **`Nuevo`** (`OnNewAsync`, `BotFlowService.cs:348-...`): el texto del primer mensaje real del
  contacto (el que dispara esta fase) se registra primero como `ContactoRespuesta` con la etiqueta
  "Primer contacto" (fix 2026-07-28 — antes se descartaba sin guardar en ningún lado; no recuperable
  para conversaciones anteriores a esa fecha). Si el contacto es un **prospecto outbound ya
  identificado** (`CanalOrigen` outbound + `Rubro` cargado por la campaña), se saltea todo el menú —
  arranca directo en `AskingQuestions` con un saludo personalizado por rubro (pela el sufijo de
  región del `ClaveRubro`, ej. `"comercio-uruguay"` → `"comercio"`, antes de buscar en el
  diccionario `OutboundTypeToIndustry`; bug real corregido 2026-07-25, cualquier contacto de
  campaña regional caía siempre en el genérico "Otro rubro" hasta ese fix). Si no es outbound
  conocido (inbound directo), manda el menú de bienvenida con 3 opciones (lista interactiva).
- **`AwaitingCategory`** (`OnCategoryInputAsync`, `:373-407`): mapea la opción elegida a una
  categoría interna (`rent`=Ordenar la gestión, `build`=Algo a medida, `landing`=Web/landing;
  cualquier otra entrada cae a `other` y **cierra la conversación de una** sin pasar por preguntas).
  Si la categoría es `rent`, pasa a `AwaitingIndustry` (pregunta el rubro); si no, va directo a
  `AskingQuestions`.
- **`AwaitingIndustry`** (`OnIndustryInputAsync`, `:409-417`): guarda el rubro elegido, decide si la
  categoría es `rent` u `rent_other` (rubro "Otro rubro"), pasa a `AskingQuestions`.
- **`AskingQuestions`** (`OnAnswerAsync`, `:419-439`): cada categoría tiene su propia lista fija de
  preguntas (`Questions`, `:63-99`; entre 1 y 3 preguntas según la categoría). Si la pregunta actual
  es la de "cuántas personas lo van a usar", intenta parsear un número del texto libre y lo guarda
  en `Contacto.CantidadUsuarios`. Al responder la última pregunta de la categoría, dispara
  `CompleteAsync`.
- Cada transición (categoría, rubro, cada pregunta respondida) pasa por `LogRespuesta` (renombrada
  desde `LogRespuestaYNotificarAsync` el 2026-07-30): guarda un `ContactoRespuesta`. **Ya no
  dispara notificación in-app** — hasta el 2026-07-29 lo hacía en cada paso ("{Nombre} respondió"),
  el cliente pidió explícitamente reducir el ruido a "notificación solo cuando es lead confirmado".
  La única notificación in-app que queda en todo el bot es "Nuevo lead calificado", disparada una
  sola vez desde `SendBriefToAdminAsync` al completar la calificación (§B.4) — el historial paso a
  paso sigue completo en `ContactoRespuesta`, ahora se revisa desde la pantalla **Chats**
  (`/Chats`, agregada 2026-07-29, rediseñada con filtros/polling/navegación 2026-07-30) en vez de
  desde una notificación por mensaje.

### B.4 — Cierre y cotización automática (`CompleteAsync`, `BotFlowService.cs:443-472`)

1. `FaseConversacion → Completed`, guarda `FechaCompletado`.
2. Resuelve una fila de `IndustriaCatalogo` para el rubro calificado
   (`ResolveIndustriaCatalogoAsync`, `:474-484` — mapeo fijo `IndustryToCatalogoNombre`; algunos
   rubros del diálogo no tienen fila propia en el catálogo a propósito, ej. "Farmacia",
   "Contabilidad / Estudios contables").
3. **Si la industria existe, tiene `CotizaAutomatico=true` y `PrecioBaseUsd` cargado**: calcula el
   precio (`PrecioBaseUsd` + USD 100 por cada usuario que exceda los incluidos en el plan —
   `UsuariosIncluidosPorPlan`: Starter=1, Pro=2, Premium=3, Scale=ilimitado), lo guarda en
   `Contacto.PresupuestoCotizadoUsd`, `EstadoEmbudo → PresupuestoEnviado`, y se lo manda al contacto
   por WhatsApp junto con el mensaje de cierre.
4. **Si no** (industria sin fila, o `CotizaAutomatico=false`, o sin precio base — ej. rubro
   "Alquiler de maquinaria" tiene `CotizaAutomatico=0` a propósito): `EstadoEmbudo → DerivadoManual`,
   solo se manda el mensaje de cierre sin monto.
5. `SendBriefToAdminAsync` (`:495-561`) — dos canales independientes, uno no bloquea al otro:
   - **Notificación in-app** ("Nuevo lead calificado") a **todos** los usuarios con rol
     `SuperUsuario` (no existe un "admin único" en Identity — se resuelve por rol). Incluye el
     brief completo: nombre, negocio, teléfono, interés, presupuesto si cotizó, y **todas** las
     preguntas/respuestas registradas durante la conversación.
   - **WhatsApp al admin** (`BotSettings.AdminNotifyPhone`) vía la plantilla ya aprobada
     `olv_notif_respuesta` (UTILITY, 3 parámetros: nombre/teléfono/resumen corto) — **no** texto
     libre, porque el admin nunca le escribió primero al bot y un mensaje de texto libre fuera de la
     ventana de 24hs falla con error 131047. El detalle completo queda solo en la notificación
     in-app. Envuelto en `try/catch` — un fallo acá no debe tirar abajo el resto del cierre.

---

## Reglas transversales / edge cases a tener en cuenta

- **`EstadoEmbudo` no es lineal**: hay una vía 100% manual (`DemoSolicitada`, `DemoRealizada`,
  `PropuestaEnviada`, `Cerrado`, `Descartado` — solo se cambian a mano desde `Contactos/Details`,
  nunca por el bot ni por outbound) superpuesta a la vía automática (`Pendiente → MensajeEnviado →
  FollowUpEnviado → Frio`, o `Respondido → PresupuestoEnviado/DerivadoManual` vía el bot).
- **`Referido` es un canal separado de `OutboundFrio`** pero comparte pipeline de envío diario y
  follow-up — la única diferencia es que siempre usa las plantillas `olv_referido_v2`/mensaje de
  cierre normal, nunca la plantilla configurada en la campaña.
- **Charset de producción**: la conexión a MySQL requiere `CharSet=utf8mb4` explícito en el
  connection string además de que las tablas estén en `utf8mb4` — si falta cualquiera de los dos,
  cualquier emoji en el brief (📋 en `SendBriefToAdminAsync`) revierte **toda** la transacción de
  `SaveChangesAsync`, incluida la respuesta que el contacto acababa de dar, sin ningún síntoma
  visible del lado del chat (bug real, resuelto 2026-07-23).
- **Ninguna excepción dentro de `HandleIncomingAsync` es visible para Meta** — el ACK `200 OK` ya
  se mandó antes del `Task.Run`. Cualquier error silencioso solo aparece en
  `Logs/OlvidataCRM-errors-YYYYMMDD.log` (nivel `Warning`+ en producción) — no hay alerta activa,
  hay que ir a mirar el archivo.
- **Prueba funcional de referencia**: 2026-07-27, contacto sintético `5491100009999` llevado de
  punta a punta (mensaje no-procesable → categoría → rubro → 3 preguntas → cierre con
  `DerivadoManual`), verificado en base de producción y en el log de errores, sin excepciones.
  Datos de prueba borrados al finalizar. Ver `trazabilidad.md`, entrada 2026-07-27.

---

## Límites de Meta/WhatsApp — dos sistemas independientes (definición a tener en cuenta)

Investigado 2026-07-28 a raíz de una duda real del cliente ("por qué me tira 131049 si en el panel
de Meta veo margen de sobra"). Importante para cualquier decisión futura de volumen de campañas —
**son dos mecanismos separados, con ejes distintos, y confundirlos lleva a conclusiones erróneas**:

1. **Límite de cuenta (Messaging Limits / tier)** — cuántas conversaciones **nuevas** puede
   *iniciar* el número de negocio en una ventana móvil de 24hs. Es lo que se ve en el panel de Meta
   ("Current: 2000", "182 conversaciones con clientes únicos en los últimos 7 días" vs. el umbral de
   1.000/7 días para subir de tier). Estado real verificado el 28/7: **muchísimo margen**, muy lejos
   de ambos números. Este límite **no tiene nada que ver** con el error 131049.

2. **Límite por destinatario (frecuencia de plantillas Marketing)** — el que dispara el error
   **131049** ("this message was not delivered to maintain healthy ecosystem engagement"). Cada
   persona en WhatsApp tiene un tope propio de cuántos mensajes de plantilla *Marketing* puede
   recibir en total, **sumando todas las empresas que le escriben**, no solo Olvidata. Si ese
   contacto puntual ya viene saturado de marketing de otros negocios, WhatsApp le bloquea el mensaje
   a él específicamente — sin importar cuánto margen tenga la cuenta de Olvidata en el punto 1.
   Confirmado 16 ocurrencias reales en los logs de producción entre el 22/7 y el 28/7 (agrupadas
   exactamente en las ventanas de las corridas de envío: 3 el 24/7, 10 el 25/7 — ambas corridas
   manuales de prueba —, 3 el 28/7 en el envío automático real de hoy, ~5% de los 59 enviados). No es
   evitable del todo — es estructural al outbound frío en WhatsApp (Meta exige categoría MARKETING
   para el primer contacto a un desconocido, no hay plantilla alternativa). El código ya se comporta
   bien ante esto: un contacto que falla por este error queda `EstadoEmbudo=Pendiente` y recién se
   reintenta en la próxima corrida programada de esa campaña (días después, nunca el mismo día),
   que es justamente lo que recomienda Meta (no reintentar antes de 24hs).

3. **El cuestionario de calificación (las preguntas que manda el bot después de que el contacto
   responde) NO consume ninguno de los dos límites.** Confirmado contra la documentación oficial de
   WhatsApp Business Platform: apenas el contacto responde, se abre una ventana de 24hs de
   "conversación iniciada por el usuario" — todo lo que se manda ahí es **texto libre** (no
   plantilla, `SendCurrentQuestionAsync`/`SendTextAsync` en `BotFlowService`), y los mensajes de
   texto libre dentro de esa ventana quedan **exentos** tanto del límite de cuenta (punto 1, que solo
   cuenta conversaciones *business-initiated*) como del límite por destinatario (punto 2, que solo
   aplica a plantillas Marketing). En la práctica: no hace falta "dejar margen" para el cuestionario
   al planificar volumen de campañas — es efectivamente gratis en términos de estos límites, siempre
   que la respuesta a cada pregunta llegue dentro de las 24hs de la última actividad del contacto
   (si pasan más de 24hs sin que el contacto escriba, `HandleIncomingAsync` ya maneja el reinicio de
   conversación, ver §B.2 arriba — en ese caso cualquier mensaje *nuevo* que la empresa quiera
   iniciar sí volvería a necesitar plantilla).
