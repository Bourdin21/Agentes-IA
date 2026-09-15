# Plan de implementación — conversación fluida con LLM en el chatbot

**Fecha:** 2026-09-13 · **Estado original de este documento:** **fases 0, 1 y 2 implementadas y deployadas** (2026-09-13), IA apagada en modo sombra esperando API key. Fases 3 a 5 pendientes. Detalle abajo en §10.

> **ACTUALIZACIÓN 2026-09-14 — la IA ya está ENCENDIDA Y EN VIVO en producción**, no apagada ni en
> modo sombra: se creó y cargó la API key, y el cliente pidió activarla en vivo directamente (saltó
> la ventana de sombra previa). Detalle completo en `trazabilidad.md`, entradas del 2026-09-14
> ("El razonamiento de la IA vs el arbol diseñado" y "Bot LLM ACTIVADO EN VIVO en produccion"): tope
> de gasto subido a ARS 300.000, outbound y Places siguen pausados, fix de `FaseConversacion.ConversandoConIa`
> aplicado. El resto de este documento (§1 a §10) describe el plan y el estado **al 13/09**; no se
> reescribió entero para no perder el razonamiento original — para el estado real, priorizar
> `trazabilidad.md` sobre el §10 de acá.
**Proyecto:** CRM Olvidata (`C:\Sistemas\olvidatasoft-crm`) · producción `https://portal.olvidata.com.ar/`

Retoma la decisión ya tomada en esta misma sesión: **conversación 100% agéntica** (el LLM conduce el
diálogo y decide cuándo llamar herramientas), no una capa clasificadora sobre el árbol actual.

Referencias obligadas: [`arbol-comunicacion-bot.md`](arbol-comunicacion-bot.md) (el árbol que se
reemplaza, nodo por nodo) y [`logica-negocio-bot.md`](logica-negocio-bot.md).

---

## 1. Por qué — el número que justifica el trabajo

Medido en producción el 2026-09-13, cohorte de los **795 contactos con al menos un mensaje entrante
desde el 2026-08-01**:

| Fase en la que quedaron | Contactos | % |
|---|---|---|
| `ConfirmandoContinuar` (tocaron "Sí, contame más" y ahí murió) | 321 | 40,4% |
| `Nuevo` (escribieron pero nunca avanzaron — casi todos away-message) | 235 | 29,6% |
| `AskingQuestions` (abandonaron a mitad del cuestionario) | 197 | 24,8% |
| `AwaitingCategory` (recibieron el menú y no eligieron nada) | 9 | 1,1% |
| **`Completed`** | **33** | **4,2%** |

Y la distribución de mensajes por contacto en la misma ventana:

| Mensajes entrantes del contacto | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 14 | 17 | 22 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Contactos | 596 | 133 | 33 | 12 | 6 | 3 | 4 | 3 | 2 | 1 | 1 | 1 |

**75% de los contactos manda exactamente un mensaje.** La conversación no se pierde en la pregunta 3:
se pierde en el primer turno, donde hoy lo único que ofrecemos es un menú de botones. Eso es
precisamente lo que un LLM arregla y un árbol no: el que escribe "hola, cuánto sale un sistema para
mi ferretería" recibe hoy un menú de 3 opciones que no contesta su pregunta.

El cuestionario, además, **ya funciona como embudo de pérdida y no de calificación**: 4,2% de
completitud. No hay nada que preservar por rendimiento.

---

## 2. Alcance — qué reemplaza el LLM y qué NO toca

### Reemplaza (nodos de `arbol-comunicacion-bot.md`)

| Nodo actual | Qué pasa |
|---|---|
| §3.2 `AwaitingCategory` — menú de bienvenida (6 opciones) | Desaparece como menú. La categoría la infiere el LLM del texto y la fija con `set_categoria`. |
| §3.3 `AwaitingIndustry` — menú de rubros (10 opciones) | Ídem con `set_rubro`. |
| §3.4 `AskingQuestions` — cuestionario fijo por categoría | Desaparece como secuencia. El LLM pregunta lo que falta, en el orden que tenga sentido, y puede sacar 2 datos de una sola respuesta. |
| §3.5 Los 3 mecanismos de la pregunta 1 (botones de dolor / matriz MVP / texto libre) | Se unifican: el LLM consulta los módulos del rubro con `consultar_modulos_del_rubro` y conversa. |
| §3.6 El pitch va después del dolor | Pasa a ser **instrucción del system prompt**, no un `if` en código. |
| §3.1 Detección de origen por anuncio (Ads-CTWA) | Se mantiene el *matcher* determinístico (ya escribe `AdOrigenTag`), pero el acuse deja de ser un texto fijo: entra como contexto en el prompt. |
| §4 Cierre normal | Lo dispara `finalizar_conversacion`, no `QuestionIndex == n`. |

### NO toca (y es deliberado)

**Las 7 guardas globales de §2 se quedan en C#, antes de cualquier llamada al LLM.** Cada una es el
fix de un incidente real documentado en `trazabilidad.md`; ninguna se delega al criterio del modelo:

1. Admin no activa el flujo (`HandleIncomingAsync`, primera línea).
2. `EstadoEmbudo == Descartado` → registrar y callarse (incidente Kremia Moda, 2026-07-29).
3. `EstadoEmbudo == Cerrado` → registrar y avisar al admin, sin responder (bug 2026-08-08).
4. `EsSolicitudDeBaja(text)` → `ProcesarBajaAsync` (detección por frases, determinística).
5. `EsRespuestaAutomatica(text)` → away-message del comercio, no avanza embudo (hallazgo 2026-08-20).
6. Tipos no procesables (imagen/audio/video/documento/sticker/ubicación/reacción) → se registran.
7. Corte de loop post-cierre (2 mensajes sin intervención humana, bug del contacto 2319).

Razón de fondo: esas guardas existen porque el bot **no debe responder** en esos casos. Un LLM al que
le pasamos el mensaje siempre va a querer contestar algo. La forma barata de garantizar el silencio es
no llamarlo.

**Tampoco se toca:** el outbound (`OutboundCampaignService`, plantillas, presupuesto, cupos), la
búsqueda de Maps, `PropuestaMvpFullService` (el presupuesto lo sigue armando Joaquín a mano — ver §5),
ni la pantalla `/Chats`.

---

## 3. Arquitectura

```
Webhook (Program.cs:261)
   └─ BotFlowService.HandleIncomingAsync          ← las 7 guardas globales, SIN CAMBIOS
        ├─ ¿pausa por contacto? ──────── sí ─────► registrar y salir (nuevo, §4)
        ├─ ¿botón / list reply? ──────── sí ─────► ruta determinística actual (sin costo de LLM)
        ├─ ¿ConversacionIaHabilitada
        │   && !ConversacionIaPausada
        │   && presupuesto OK? ───────── no ─────► ProcessAsync (árbol actual, intacto)
        └─ sí ──► ConversacionIaService.ResponderAsync
                    ├─ arma historial desde ContactoMensajeIA
                    ├─ POST /v1/messages  (loop de tool use, máx. 4 iteraciones)
                    ├─ ejecuta tools contra AppDbContext
                    ├─ registra tokens + costo
                    └─ manda la respuesta por WhatsApp
                          └─ cualquier falla ──► fallback al árbol actual
```

El punto clave del diseño: **el árbol actual no se borra**. Queda como camino de fallback para
timeout, 429, `stop_reason: "refusal"`, presupuesto agotado, feature flag apagada y bug no previsto.
Eso hace el cambio reversible con un toggle, sin redeploy.

### 3.1 Piezas nuevas

| Pieza | Capa | Qué hace |
|---|---|---|
| `IConversacionIaService` / `ConversacionIaService` | Application / Infrastructure | El loop agéntico. Único lugar que habla con la API de Anthropic. |
| `ContactoMensajeIA` (entidad) | Domain | Historial de la conversación **tal como lo ve el modelo** (la API es stateless: si no lo guardamos, no hay memoria). Una fila por bloque: `Rol`, `Contenido`, `ToolUseId`, `ToolName`, `ToolInputJson`, `ThinkingSignature`, `InputTokens`, `OutputTokens`, `CacheReadTokens`, `CostoUsd`, `Modelo`. |
| `IaSettings` | Application | Misma forma que el `AnthropicSettings` que ya existe en `Olvidata Agentes Multi-rubro` (§3.5): `ApiKey` (variable de entorno `Anthropic__ApiKey` o user-secrets, **nunca** en `appsettings.json` versionado), `Modelo`, `MaxTokens`, más lo propio del loop: `Effort`, `TimeoutSegundos`, `MaxIteracionesTool`, `MaxTurnosPorContacto`. |
| `ConfiguracionOutbound.ConversacionIaHabilitada` + `.ConversacionIaPausada` | Domain | Feature flag + kill switch persistidos en base (mismo criterio que `BusquedaMapsPausada`: tiene que sobrevivir un reciclo de IIS). |
| `Contacto.BotPausado` + `.FechaBotPausado` | Domain | Prerrequisito bloqueante — ver §4. |

**Por qué `ContactoMensajeIA` y no reutilizar `ContactoRespuestas`:** esa tabla es el hilo que ve el
asesor en `/Chats` y la fuente de verdad de la ventana de 24hs y del no-leído (12 queries dependen de
sus etiquetas, ver `MensajeriaHelpers`). Meterle bloques `tool_use`/`tool_result`/`thinking`
ensuciaría el hilo humano y arriesgaría exactamente la desincronización de etiquetas que ya pasó 2
veces. Van separadas: `ContactoRespuestas` sigue siendo el hilo humano (el LLM escribe ahí su
respuesta final, igual que hoy), `ContactoMensajeIA` es el transcript técnico.

**Por qué NO una tabla agregada diaria** (a diferencia de `ConsumoMapsDiario`): Maps hace ~1.200
llamadas/día, el LLM va a hacer ~15. Con ~470 filas/mes, sumar por mes es trivial y el detalle por
mensaje es justamente lo que hace falta para auditar costo y calidad.

### 3.2 El contrato con la API (verificado contra la referencia vigente hoy)

```csharp
using Anthropic;
using Anthropic.Models.Messages;

var resp = await client.Messages.Create(new MessageCreateParams
{
    Model        = "claude-opus-5",
    MaxTokens    = 2048,                                   // el thinking cuenta acá: no bajar a 256
    Thinking     = new ThinkingConfigAdaptive(),            // adaptive; budget_tokens da 400 en este modelo
    OutputConfig = new OutputConfig { Effort = Effort.Low }, // respuesta corta de WhatsApp, no razonamiento profundo
    System       = new List<TextBlockParam> {
        new() { Text = systemPrompt, CacheControl = new CacheControlEphemeral() },
    },
    Tools    = [ /* §3.3 */ ],
    Metadata = new Metadata { UserID = contacto.Id.ToString() },  // Commercial Terms, ver §3.5
    Messages = historial,
});
```

Detalles que importan y que son fáciles de errar:

- **Model id exacto:** `claude-opus-5`. Sin sufijo de fecha.
- **`thinking`**: `ThinkingConfigAdaptive`. El `budget_tokens` de los modelos viejos devuelve **400**
  en este modelo. `Effort` va **dentro de `OutputConfig`**, no top-level.
- **`stop_reason == "refusal"`** existe y hay que chequearlo **antes** de leer `Content`
  (`response.StopDetails.Category`). En ese caso: fallback al árbol + notificación al admin.
- **No hay prefill de assistant** (devuelve 400). Si en algún momento hace falta forzar formato, va
  por `OutputConfig.Format` (structured outputs).
- **No hay `.ToParam()` en C#**: para reenviar el turno del assistant hay que reconstruir bloque por
  bloque (`TextBlockParam`, `ToolUseBlockParam`, `ThinkingBlockParam` **preservando `Signature`**).
  Esto es la mitad del trabajo real de `ConversacionIaService` y es donde se van a ir los bugs.
- **`ToolUseBlock.Input` es `IReadOnlyDictionary<string, JsonElement>`** — se parsea con
  `.GetString()` / `.GetInt32()`, nunca con match de strings sobre el JSON serializado.
- **Telemetría:** `resp.Usage.InputTokens`, `.OutputTokens`, `.CacheReadInputTokens`,
  `.CacheCreationInputTokens`. Se persisten **siempre**, también en las corridas fallidas.

### 3.3 Las herramientas

Cerradas por enum donde se puede, porque un rubro inventado por el modelo rompe la clasificación
del CRM (que es exactamente el bug **CRM-016** que arreglamos esta semana).

| Tool | Input | Efecto |
|---|---|---|
| `set_categoria` | `categoria`: enum con las 6 claves de `CategoryNames` | `Contacto.Categoria` |
| `set_rubro` | `rubro`: enum con las 10 claves de `IndustryNames` | `Contacto.Rubro` + resuelve `IndustriaCatalogo` |
| `consultar_modulos_del_rubro` | `rubro` (mismo enum) | **Sólo lectura.** Devuelve los módulos MVP del rubro para que el LLM converse sobre el dolor sin tener toda la matriz en el prompt. |
| `guardar_datos_contacto` | `nombre_negocio?`, `nombre_contacto?`, `email?`, `zona?`, `cantidad_usuarios?` | Campos de `Contacto`. Nunca pisa un dato ya cargado a mano (mismo criterio que el parser de email actual). |
| `registrar_dolor` | `dolor` (texto), `modulo_relacionado?` | Fila en `ContactoRespuestas` con la etiqueta del dolor — lo que hoy alimenta el pitch. |
| `escalar_a_humano` | `motivo`, `urgencia`: enum `alta\|normal` | `EstadoEmbudo = DerivadoManual`, notificación in-app + WhatsApp al admin, y **corta la conversación con el LLM** para ese contacto. |
| `dar_de_baja` | `motivo` | Llama al `ProcesarBajaAsync` existente (mismo camino que el botón "No me interesa": descarta + marca leído). |
| `finalizar_conversacion` | `resumen` | `FaseConversacion = Completed`, `FechaCompletado`, brief al admin (reutiliza `SendBriefToAdminAsync`). |

**No hay tool para cotizar ni para mandar presupuesto.** Es una garantía estructural, no una
instrucción de prompt: si la herramienta no existe, el modelo no puede inventar un precio ni
disparar un PDF, por más que el prospecto insista. El presupuesto lo sigue armando Joaquín a mano con
`PropuestaMvpFullService`. Si el prospecto pide precio, el camino es `escalar_a_humano`.

Todas las tools de escritura llevan `strict: true` (`additionalProperties: false` + `required`), así
los argumentos validan contra el schema y no hay que defender cada campo a mano.

### 3.4 El system prompt se **genera**, no se escribe a mano

El prompt sale de `RubroHelpers` (`RubroBaseAIndustria`, `IndustriaACatalogoNombre`), de
`CategoryNames`/`IndustryNames` y de la matriz de módulos MVP en base — no de una lista copiada a mano
en un `const string`.

Esto no es elegancia: es la lección de **CRM-007 y CRM-016**. Ya tuvimos dos incidentes por tener el
mismo vocabulario de rubros escrito en dos lugares que se desincronizaron. Un prompt con una tercera
copia a mano sería el tercer incidente, con el agravante de que el modelo lo repetiría en voz alta al
prospecto.

Contenido del prompt: identidad ("Soy Joaquín, de Olvidata Soft", igual que hoy — el prospecto no
debe notar que es un bot), qué vende el estudio, el vocabulario de rubros y categorías, los módulos
del rubro si ya se conoce, la regla del pitch después del dolor, **prohibido dar precios**, tono de
WhatsApp (corto, sin signos de apertura `¡`/`¿`, sin listas numeradas), y los datos del contacto que
ya tenemos (nombre del negocio, rubro detectado por la campaña, `AdOrigenTag` si vino de un anuncio).

**Sobre prompt caching — expectativa honesta:** al volumen actual (~15 mensajes/día) el TTL de 5
minutos casi nunca acierta, y el write cuesta 1,25× el input normal. Se deja `CacheControl` puesto
porque no molesta y sirve si el tráfico se concentra, pero **no hay que contarlo como ahorro en el
presupuesto**. La palanca real de costo acá es que el prompt sea corto (de ahí
`consultar_modulos_del_rubro` en vez de volcar la matriz entera).

### 3.5 Reutilización cross-proyecto: ya hay una integración con Claude en el estudio

Encontrado el 2026-09-13 al buscar la API key. **`Olvidata Agentes Multi-rubro`**
(`C:\Sistemas\Olvidata Agentes Multi-rubro`) ya tiene el SDK oficial integrado y en uso. Es la
referencia obligada: se reutiliza el patrón, no se reinventa.

| Pieza de ese proyecto | Qué se reutiliza en el CRM |
|---|---|
| `Anthropic` **12.47.0** (`OlvidataAgentes.Infrastructure.csproj`) | Misma versión o superior. No hace falta evaluar paquetes. |
| `AnthropicSettings` (`Application/Settings/AgentesSettings.cs`) | La forma exacta de `IaSettings`: `ApiKey` nullable + `ModeloPorDefecto` + `MaxTokens` + tabla de precios. Y el patrón de la key: **user-secrets en desarrollo, variable de entorno `Anthropic__ApiKey` en producción**, nunca en `appsettings.json` versionado (así está comentado en su `appsettings.json`). |
| `AnthropicClienteLlm.cs` (47 líneas) | La forma de la llamada: `AnthropicClient { ApiKey }`, `System` como `List<TextBlockParam>` con `CacheControlEphemeral`, lectura de `Usage`, `StopReason`. |
| `TelemetriaService.cs` | El patrón de registro por evento con `Modelo`/`TokensEntrada`/`TokensSalida`/`CostoUsd` — es el mismo que `ContactoMensajeIA`. |

Qué **no** transfiere, y por qué:

- **Es single-turn.** `CompletarAsync` manda un system prompt y un único mensaje de usuario: no hay
  historial, no hay tool use, no hay loop. Toda la §3 (el loop agéntico, la reconstrucción de bloques,
  `ContactoMensajeIA`) es extensión genuina, no copia.
- **Su cálculo de costo está mal para nuestro caso, no lo copiemos.** Suma
  `InputTokens + CacheCreation + CacheRead` y cobra todo a la tarifa de entrada; pero la lectura de
  caché cuesta ~10% de la base y la escritura ~125%. A su volumen el error es chico; con
  conversaciones largas y caché activa, no. Por eso `TarifaLlm` (§5.3) tiene **4 tarifas** y no 2.
  Vale proponer el mismo fix hacia ese proyecto.

**Y algo que hay que copiar y mi borrador no tenía:** ese cliente manda
`Metadata = new Metadata { UserID = ... }` en cada request — un identificador **opaco** del usuario
final, requisito de trazabilidad de los Commercial Terms de Anthropic. En el CRM el valor correcto es
el **`Contacto.Id`** (o un hash estable de él), **nunca el teléfono**: el teléfono es dato personal del
prospecto y no tiene por qué salir del sistema.

---

## 4. Prerrequisitos bloqueantes

### 4.1 Pausa del bot **por contacto**

Hoy `BotController.TogglePausa()` (`BotController.cs:115`) sólo pone
`OutboundSchedulerService.IsStandby` en memoria: **para el envío outbound, no el webhook**. O sea: no
existe forma de que un asesor tome una conversación y el bot se calle en ese chat. Con el árbol actual
el daño es acotado (el bot manda preguntas fijas). Con un LLM conversando en paralelo con un humano
sobre el mismo prospecto, el daño es la conversación entera.

Alcance mínimo:

- `Contacto.BotPausado` + `FechaBotPausado` (migración).
- Se activa **automáticamente** cuando un asesor manda un mensaje manual desde `/Chats` (ya existe el
  punto exacto: donde se escribe la etiqueta `[Mensaje manual del asesor]`).
- Toggle manual en el detalle del chat, **por AJAX, re-renderizando sólo la partial** (regla general
  vigente del proyecto: nunca re-renderizar la pantalla completa).
- `HandleIncomingAsync` corta antes del LLM si está pausado: registra el mensaje entrante y no
  responde.
- Se reanuda a mano, o **automáticamente a las 48hs** de silencio del asesor (definido por el cliente
  el 2026-09-13: sólo manual corre el riesgo de que un chat quede mudo para siempre porque nadie se
  acordó de destildarlo).

Esto entra **antes** de cualquier línea de integración con la API, y tiene valor propio incluso si el
LLM nunca se prende.

### 4.2 El tope de gasto tiene una fuga: los follow-ups no lo consultan

Encontrado el 2026-09-13 al verificar qué puede seguir gastando en septiembre.
**`OutboundCampaignService.ProcessFollowUpsAsync` (línea 423) no mira el presupuesto ni el cupo
diario.** Ni `GetCostoMensajeriaAsync`, ni `LimiteEfectivoHoy`, ni `CupoDiario`: le manda
`olv_nurturing_v2` a **todos** los contactos en `MensajeEnviado` con 3+ días de antigüedad cuyos
rubros correspondan a las campañas activas del día, sin techo de ninguna clase.
`ProcessFollowUpMenuAsync` está mejor pero tampoco consulta el presupuesto — sólo tiene su
`MaxReenganchesPorCorrida = 20`.

**Esto explica el 113% del mes**: septiembre lleva **2.201 follow-ups contra 889 mensajes fríos**. El
tope sólo controla el lote frío (`SendDailyBatchAsync:137`), o sea la punta chica del gasto. Y tiene
una consecuencia operativa inmediata: **frenar el envío no frena el gasto** — con el presupuesto ya
agotado, `SendDailyBatchAsync` devuelve 0 pero los follow-ups siguen saliendo y facturando.

Sin esto arreglado, todo el §5 es decorativo: no se puede repartir un tope que se puede evadir. El fix
es de pocas líneas (pasar el mismo `costo.LimiteEfectivoHoy` a las 2 funciones de follow-up y
descontar de ahí), pero es **condición previa** al reparto.

**Para pausar septiembre mientras tanto** hay una vía que sí funciona hoy: el botón "Pausar" de `/Bot`
pone `OutboundSchedulerService.IsStandby` y el scheduler saltea el tick **completo**
(`OutboundSchedulerService.cs:52`), follow-ups incluidos. El problema es que ese flag vive **en
memoria**: un reciclo del app pool o un deploy lo vuelve a `false` y el envío se reanuda solo, sin que
nadie lo pida. Por eso entra en la fase 0, junto con lo demás: **persistir `IsStandby` en
`ConfiguracionOutbound`**, igual que se hizo con `BusquedaMapsPausada` después de la factura de Places.

---

## 5. El tope único de gasto del bot y su reparto entre las tres herramientas

Pedido explícito del cliente (2026-09-13): que el costo de mensajería del LLM entre en el sistema
como una línea más, **para poder ponerle un límite de costo al bot completo**. El LLM no lleva un
contador aparte: entra en el tope único ya construido el 2026-09-03.

### 5.1 De dónde se parte — el tope ya está configurado y ya está agotado

Leído en producción hoy (`ConfiguracionesOutbound`):

| Parámetro | Valor |
|---|---|
| `PresupuestoMensualArs` | **250.000** |
| `CotizacionUsdArs` | **1.540** |
| `CupoDiario` (techo de seguridad) | 300 |
| `MetaDiaria` (respaldo sin presupuesto) | 150 |
| `BusquedaMapsPausada` | sí |

Y el gasto real del mes en curso (13 días, 3.090 plantillas Marketing entregadas):

| Línea | Envíos | Tarifa ARS | Total ARS |
|---|---|---|---|
| Argentina | 2.883 | 89,56 | 258.201 |
| Chile | 129 | 128,84 | 16.620 |
| Uruguay | 60 | 107,24 | 6.434 |
| Other (fallback) | 18 | 87,53 | 1.576 |
| **Mensajería** | **3.090** | prom. **91,53** | **282.832** |
| Google Places | — | pausada desde 31/08 | **0** |
| **Total consumido** | | | **282.832 = 113% del tope** |

**Consecuencia que ya está corriendo hoy:** `CalcularVolumenDiario` devuelve `0` cuando el restante es
negativo, así que `SendDailyBatchAsync` **no manda nada más en lo que queda de septiembre**. El tope
está haciendo exactamente lo que se construyó para hacer. Esto es el contexto real en el que hay que
dimensionar el costo del LLM: no hay holgura, cada peso que consuma la IA sale del volumen de envío.

### 5.2 La fórmula única, y dónde entra el LLM

Hoy (`OutboundCampaignService.GetCostoMensajeriaAsync` + `CalcularVolumenDiario`):

```
GastoTotalArs   = GastoMensajeriaArs + GastoMapsUsd × CotizacionUsdArs
restante        = PresupuestoMensualArs − GastoTotalArs
cupoPorPrecio   = floor(restante / diasRestantes / costoPromedioPorMensaje)
LimiteEfectivo  = min(CupoDiario, cupoPorPrecio)
```

Con el LLM, cambia **un solo término**:

```
GastoTotalArs   = GastoMensajeriaArs
                + GastoMapsUsd × CotizacionUsdArs
                + GastoIaUsd   × CotizacionUsdArs      ← nuevo
```

Todo lo demás (el cupo derivado del precio, el corte en `SendDailyBatchAsync:137`, el rebalanceo de
la matriz en `RebalancearMatrizAsync`, la proyección a fin de mes, el `PorcentajeConsumido` de la
card) queda igual y hereda el tercer término sin tocarse. Ese es el punto de haber construido el tope
como "costo total del bot" y no como "costo de mensajería".

### 5.3 Piezas nuevas para medir el gasto de IA

| Pieza | Qué es |
|---|---|
| `TarifaLlm` (entidad) | `Modelo`, `InputUsdPorMTok`, `OutputUsdPorMTok`, `CacheReadUsdPorMTok`, `CacheWriteUsdPorMTok`, `Activo`. Una fila por modelo, seedeada y editable en `/Bot` sin redeploy — mismo criterio que `TarifaWhatsApp`. |
| `ContactoMensajeIA.CostoUsd` | **Snapshot** del costo de esa llamada, calculado al momento con la tarifa vigente y los `Usage` reales que devolvió la API. |
| `GetCostoIaAsync()` | Suma `CostoUsd` del mes calendario argentino. Lo consume `GetCostoMensajeriaAsync`, igual que hoy consume `IGoogleMapsService.GetCostoMapsAsync`. |

Por qué tabla y no constantes como en Maps: en Maps hay 2 SKU estables y una sola API. Acá el precio
depende del **modelo elegido en runtime** y son 4 tarifas por modelo (input, output, lectura de caché,
escritura de caché). Con una tabla, cambiar de modelo o corregir un precio no es un deploy.

Por qué **snapshot** de `CostoUsd` y no recalcular: la mensajería hoy recalcula el gasto histórico
contra la tarifa actual, así que si se edita una tarifa **cambia retroactivamente** el gasto de meses
pasados. Para la IA se guarda el costo al momento del envío, que es lo correcto para auditar. (Es una
diferencia deliberada respecto de `TarifaWhatsApp`, no un olvido.)

### 5.4 Cambios exactos en `CostoMensajeriaDto`

```csharp
public decimal  GastoIaUsd    { get; set; }                    // nuevo
public int      MensajesIaMes { get; set; }                    // nuevo — llamadas al LLM del mes
// Derivados, NO configurables — los calcula GetCostoMensajeriaAsync (§5.8 y §5.9)
public decimal  CostoUnitarioProspectoArs { get; set; }
public decimal  CostoMapsPorProspectoArs  { get; set; }
public decimal  CostoIaPorEnvioArs        { get; set; }         // RatioRespuesta × CostoIaPorMensajeArs
public decimal  TechoMapsArs { get; set; }
public decimal  TechoMetaArs { get; set; }
public decimal  TechoIaArs   { get; set; }

public decimal GastoIaArs => CotizacionUsdArs is > 0
    ? Math.Round(GastoIaUsd * CotizacionUsdArs.Value, 2) : 0m;

// cambia: pasa de 2 a 3 términos
public decimal GastoTotalArs => GastoMesArs + GastoMapsArs + GastoIaArs;

public decimal CostoIaPromedioArs => MensajesIaMes > 0
    ? Math.Round(GastoIaArs / MensajesIaMes, 2) : 0m;
```

`FaltaCotizacion` pasa a contemplar también el gasto de IA (si no hay cotización cargada, ni Maps ni
IA se pueden consolidar y el tope cubre sólo la mensajería — se informa, no se inventa un tipo de
cambio). Nada más cambia de firma: `RestanteMesArs`, `PorcentajeConsumido`,
`VolumenDiarioPorPresupuesto`, `LimiteEfectivoHoy` y `MandaElPresupuesto` ya se calculan sobre
`GastoTotalArs`.

### 5.5 Costo por mensaje, y cuánto volumen de envío cuesta

Por cada mensaje entrante que atiende el LLM (prompt ~2.500 tokens, historial ~700, respuesta corta,
con el ~35% de llamadas que hacen ida y vuelta de tool use ya promediado):

| Modelo | USD/MTok (in / out) | USD por mensaje | **ARS por mensaje** (@1.540) |
|---|---|---|---|
| `claude-opus-5` | 5 / 25 | 0,036 | **55** |
| `claude-sonnet-5` | 2 / 10 | 0,0145 | **22** |
| `claude-haiku-4-5` | 1 / 5 | 0,0072 | **11** |

> **Medido en producción el 2026-09-13, y el número real quedó MEJOR que la estimación.** Con el prompt
> partido en 2 bloques (prefijo estable cacheado + contexto del contacto sin cachear, ver
> `ConversacionIaService.ArmarSystemPromptAsync`) y el loop cortando en `NoEsProspecto`:
>
> | Caso | Llamadas | USD | ARS |
> |---|---|---|---|
> | Conversación completa, con caché caliente | 2 | 0,0157 | **24** |
> | Descarte por no-prospecto, con caché caliente | 1 | 0,0063 | **10** |
> | Conversación completa, caché fría (primera del período) | 2 | 0,0445 | 69 |
>
> El promedio real depende de cuánto acierte la caché, y eso depende del ritmo de tráfico: el TTL por
> defecto es de 5 minutos, así que con mensajes espaciados muchas primeras llamadas van a escribir caché
> en vez de leerla. **La banda honesta es USD 0,006 a 0,045 por mensaje entrante**; la primera semana en
> modo sombra la cierra. Y hay un factor que juega a favor y no estaba en la estimación: entre el 42% y
> el 60% del tráfico son máquinas que se descartan en UNA llamada (el caso más barato).

Referencia para tener escala: **una plantilla Marketing a Argentina cuesta ARS 89,56**. Un turno de
conversación con Opus 5 sale ARS 55 — el 61% de lo que cuesta mandar un mensaje frío.

Medido en producción (agosto + septiembre: 6.930 plantillas enviadas → 700 mensajes entrantes
elegibles), **~10,1% de los envíos generan un mensaje entrante que amerita una llamada al LLM**. Con
eso, el costo por envío pasa a ser `91,53 + 0,101 × ARS por mensaje`, y contra el mismo tope de
ARS 250.000:

| Escenario | Costo efectivo por envío | Envíos/mes que entran en el tope | Diferencia |
|---|---|---|---|
| Sin IA (hoy) | 91,53 | **2.731** | — |
| Con `claude-haiku-4-5` | 92,64 | 2.699 | −32 (−1,2%) |
| Con `claude-sonnet-5` | 93,75 | 2.667 | −64 (−2,3%) |
| Con **`claude-opus-5`** | 97,09 | **2.575** | **−156 (−5,7%)** |

**Esa es la respuesta al pedido:** poner la conversación agéntica bajo el mismo tope de ARS 250.000
cuesta **~6% del volumen de envío** con el modelo más caro. No hace falta subir el tope; hace falta
que el tope lo contemple.

### 5.6 El acoplamiento en el otro sentido (y por qué no se descontrola)

El gasto de IA no es independiente: **depende del volumen de envío**, porque el 96% de los mensajes
entrantes elegibles vienen de gente que responde un outbound (medido: 664 de 700; sólo 36 son de ads
pagos). O sea que cuando el tope frena el envío, el gasto de IA se frena solo. Es un lazo
auto-estabilizante, no una fuga:

| Envíos/día | Envíos/mes | Entrantes elegibles/mes | IA Opus 5 ARS/mes | Sonnet 5 | Haiku 4.5 |
|---|---|---|---|---|---|
| 300 (`CupoDiario`) | 9.000 | ~900 | 49.500 | 19.800 | 9.900 |
| 150 (`MetaDiaria`) | 4.500 | ~450 | 24.750 | 9.900 | 4.950 |
| 100 | 3.000 | ~300 | 16.500 | 6.600 | 3.300 |
| **0 (hoy, tope agotado)** | 0 | **~20** (sólo ads y orgánico) | **~1.100** | ~440 | ~220 |

Dato que conviene tener presente para la fase 3: el inbound de **ads pagos es de 6-7 contactos y
12-24 mensajes por mes**. El piloto acotado a ads cuesta **~ARS 1.000/mes** — es gratis, pero también
aprende despacio. El volumen de aprendizaje real lo da el **modo sombra** de la fase 1, que cubre
todos los entrantes sin exponer a nadie.

### 5.7 Escalera de degradación de la línea de IA

El techo propio de la IA es el caso particular del mecanismo general de §5.9 (`TechoIaPct`), no un
parámetro aparte. Lo que sigue es qué hace el sistema en cada escalón, específicamente para el LLM:

| Condición | Qué hace el sistema |
|---|---|
| `GastoIaArs >= 80%` de su techo | Notificación in-app al SuperUsuario. Sigue funcionando. |
| `GastoIaArs >= 100%` de su techo | `ConversacionIaService` deja de llamar a la API → **fallback al árbol**. El bot sigue atendiendo, sin LLM. Notificación. |
| `PorcentajeConsumido >= 80%` del tope único | Notificación; aplica a las 3 líneas. |
| `PorcentajeConsumido >= 100%` del tope único | Se corta por orden de prioridad (§5.9): primero Places, después la IA, el envío al final. |
| `ConversacionIaPausada = true` | Kill switch manual, sin tocar el envío — mismo criterio que `BusquedaMapsPausada` tras la factura de USD 542,72. |

Los 5 cortes se evalúan **antes** de armar el request, no después: si el presupuesto está agotado no
se llama a la API. Y ninguno deja al prospecto sin respuesta — todos caen al árbol, que sigue en el
código exactamente por esto.

### 5.8 Un solo número de entrada, repartido por el sistema entre las tres herramientas

Pedido explícito del cliente (2026-09-13, segunda iteración): **fijar un costo de consumo único y que
el sistema lo distribuya** entre Google Places, Meta y el LLM.

El reparto **no se elige a dedo en porcentajes**, porque las tres herramientas no son independientes:
están **en cadena**. Places compra el prospecto, Meta le habla, el LLM lo conversa si contesta.
Trabajar un prospecto de punta a punta tiene un costo unitario que es la suma de los tres, y el
reparto sale de ahí solo:

```
CostoUnitarioProspectoArs =
      CostoMapsPorProspectoArs                 ← gasto Places del mes / prospectos nuevos del mes
    + CostoPromedioMensajeriaArs               ← ya existe: mix real por país
    + RatioRespuesta × CostoIaPorMensajeArs     ← entrantes elegibles/envíos × GastoIaArs/MensajesIaMes

VolumenDiarioPorPresupuesto = floor(restante / diasRestantes / CostoUnitarioProspectoArs)
LimiteEfectivoHoy           = min(CupoDiario, VolumenDiarioPorPresupuesto)
```

Es **la misma fórmula que ya corre hoy** (`CalcularVolumenDiario`), con el costo unitario ampliado de
una punta a tres. Un solo número de entrada (`PresupuestoMensualArs`), un solo volumen de salida, y
los tres cupos quedan implícitos y **siempre consistentes entre sí**: cada prospecto que entra al
pipeline arrastra su costo de Places, su plantilla y su probabilidad de conversación. No hay forma de
configurar un reparto incoherente porque no hay reparto que configurar.

Los 4 factores **se miden en producción**, no se hardcodean — el reparto se recalibra solo cuando
cambia un precio, la cotización, el mix de países o la tasa de respuesta:

| Factor | Fuente | Semilla mientras no haya datos |
|---|---|---|
| `CostoMapsPorProspectoArs` | `ConsumoMapsDiario` (Text Search + Place Details × cotización) / prospectos nuevos del mes | **ARS 84,5** = el costo real medido en la factura de agosto (USD 542,72 / 9.893 prospectos), **antes** del dedupe. Semilla conservadora a propósito: la caché de `place_id` está vacía porque Places está pausada, así que todavía no hay evidencia del ahorro. |
| `CostoPromedioMensajeriaArs` | ya implementado: `porPais.Sum(TotalArs) / mensajes` | tarifa del país dominante (ya implementado) |
| `RatioRespuesta` | entrantes elegibles / plantillas enviadas, del mes | **0,101** (medido ago+sep: 700 / 6.930) |
| `CostoIaPorMensajeArs` | `GastoIaArs / MensajesIaMes` | tarifa del modelo × perfil de tokens de §5.5 |

**Qué volumen sostiene el tope de ARS 250.000 según qué herramientas estén prendidas:**

| Escenario | Costo unitario por prospecto | Prospectos/mes | Por día |
|---|---|---|---|
| Hoy (Places pausada, sin IA) | 91,53 | 2.731 | 91 |
| Places pausada + IA Opus 5 | 97,09 | 2.575 | 86 |
| Places reactivada (costo medido pre-dedupe) + IA | 181,59 | 1.377 | **46** |
| Places reactivada (proyección post-dedupe ARS 38,5) + IA | 135,59 | 1.844 | **61** |

El salto grande no lo produce el LLM (5,7%): lo produce **reactivar Places**, que se lleva entre el
28% y el 47% del tope según cuánto rinda el dedupe. Ese es el dato importante del reparto y no se veía
hasta ponerlo en la misma fórmula.

Holgura real para decidir sin apuro: hay **3.709 prospectos Pendientes enviables en stock**, o sea
~1,4 meses de envío al ritmo sostenible. Places puede seguir pausada un mes y medio más sin que el
pipeline se quede sin a quién hablarle.

### 5.9 Techos por herramienta — proporcionales a la operatoria, no elegidos a mano

Definido por el cliente el 2026-09-13: *"tiene que ser proporcional a la operatoria. Calcular el
consumo de cada herramienta por prospecto y establecer los límites equitativamente."* Así que los
techos **tampoco se configuran**: se derivan del mismo costo unitario de §5.8, con un único factor de
holgura igual para las tres — eso es lo que los hace equitativos.

```
SharePct_i  = CostoUnitario_i / CostoUnitarioProspectoArs     ← peso real de la herramienta
TechoPct_i  = SharePct_i × FactorHolguraTechos                ← MISMO factor para las 3
TechoArs_i  = PresupuestoMensualArs × TechoPct_i
```

Un solo parámetro configurable en toda la §5 además del tope: `ConfiguracionOutbound.FactorHolguraTechos`
(default **1,30**). No hay tres porcentajes que se puedan poner incoherentes entre sí, y los techos se
recalibran solos todos los meses con el consumo real medido.

Con los números del escenario post-dedupe y un tope de ARS 250.000:

| Herramienta | Costo unitario que aporta | Share real | Techo (×1,30) | Techo en ARS |
|---|---|---|---|---|
| Google Places | 38,50 por prospecto | 28,4% | 36,9% | 92.250 |
| Meta (mensajería) | 91,53 por envío | 67,5% | 87,8% | 219.500 |
| LLM (conversación) | 5,56 por envío (esperado) | 4,1% | 5,3% | 13.250 |
| **Total** | **135,59** | **100%** | **130%** | — |

**La suma de techos da 130% a propósito** — es el factor de holgura, no un error de cuentas. Si diera
100%, una herramienta que gasta menos de su parte dejaría plata inmovilizada que ninguna otra podría
usar: exactamente el caso de hoy, donde Places está pausada y su parte tiene que poder ir al envío. El
límite real sigue siendo el **tope único**; el techo sólo actúa cuando una línea se desmadra respecto
de las otras dos.

**Caso borde que hay que resolver en el código:** una herramienta sin consumo en el mes tendría
`SharePct = 0` y por lo tanto techo 0 — y quedaría trabada para siempre justo cuando se la reactiva
(es literalmente la situación de Places hoy, y del LLM en modo sombra). Por eso el share se calcula
con las **semillas de §5.8** cuando no hay datos propios del mes, nunca con 0. Es el bug obvio de
esta fórmula y conviene que quede escrito antes de implementarla.

Los tres cortes se evalúan **antes** de gastar, cada uno en su propia puerta de entrada:

| Puerta | Archivo | Qué hace al llegar a su techo |
|---|---|---|
| Places | `GoogleMapsService.SearchByRubroAsync` (única entrada real a la API) | Se comporta como `BusquedaMapsPausada`: no consulta. El envío sigue con el stock ya cargado. |
| Meta | `SendDailyBatchAsync:137` **y las 2 funciones de follow-up** (ver §4.2) | El volumen diario se recorta a lo que queda de **su** techo. |
| LLM | `ConversacionIaService.ResponderAsync` | Fallback al árbol. El bot sigue atendiendo. |

Y cuando lo que se agota es el **tope único**, el orden de sacrificio —**confirmado por el cliente el
2026-09-13**— es:

1. **Places primero** — hay 1,4 meses de stock; dejar de comprar prospectos no se nota en el día.
2. **LLM segundo** — el árbol sigue contestando; se pierde calidad de conversación, no la conversación.
3. **Meta último** — es la única de las tres que **abre** conversaciones. Sin envío no hay embudo.

Queda asentado que ese orden asume que 100 mensajes con el árbol valen más que 60 con el LLM. La fase 5
lo mide; si el LLM levanta la conversión lo suficiente, la revisión del orden es un cambio de
configuración, no de diseño.

### 5.10 Pantalla

Dos cosas nuevas en `Bot/Index`.

**1) Card "Costo de la conversación con IA — mes en curso"**, tercera al lado de las 2 que ya existen,
con el mismo formato: gasto del mes en USD y ARS, cantidad de llamadas, costo promedio por mensaje,
modelo vigente, y su techo con barra de consumo.

**2) Card "Tope único y reparto"** — el panel que responde al pedido de fijar un solo número y ver
cómo se distribuye. Un campo (`PresupuestoMensualArs`) y debajo la tabla del reparto **calculado**:

| Herramienta | Gasto del mes | % del tope | Costo unitario que aporta | Share | Techo derivado |
|---|---|---|---|---|---|
| Google Places | ARS … | …% | ARS … por prospecto | …% | …% |
| Meta (mensajería) | ARS … | …% | ARS … por envío | …% | …% |
| LLM (conversación) | ARS … | …% | ARS … por envío (esperado) | …% | …% |
| **Total** | **ARS …** | **…%** | **ARS … por prospecto** | **100%** | **130%** |

Las columnas Share y Techo son **calculadas** (§5.9), no editables. El form de presupuesto tiene sólo
**dos** campos: el tope único y el `FactorHolguraTechos`.

Y el renglón que cierra la lectura: *"con ARS 250.000 y este reparto, el bot sostiene **61 prospectos
por día**"*. Es el número que el cliente necesita para decidir el tope, y hoy no está en ninguna
pantalla.

Las barras de las 3 líneas van sobre el **tope único**, no cada una sobre su techo, así se ve de dónde
sale cada peso del `PorcentajeConsumido`.

Reglas del proyecto que aplican a esta pantalla: `.ov-monto` (`white-space: nowrap`) en cada importe;
**LP-003** en los campos decimales del form de presupuesto (el tope y el factor de holgura), con
`InvariantCulture` al renderizar el `value=`, porque la app corre en `es-AR` y el
`InvariantDecimalModelBinder` sólo arregla la mitad de entrada; y los toggles de pausa por AJAX
re-renderizando sólo su partial.

---

## 6. Guardrails

| Riesgo | Control |
|---|---|
| Conversación infinita (costo + prospecto harto) | `MaxTurnosPorContacto` ~10 llamadas al LLM por contacto. Al llegar: `escalar_a_humano` automático. |
| Loop de tool use | Máximo 4 iteraciones por mensaje entrante. Al llegar: se manda lo que haya de texto y se escala. |
| Timeout / 429 / 5xx | Timeout de cliente 25s (el webhook ya ACKea a Meta al instante, pero el prospecto espera del otro lado). Un solo reintento con backoff; después, fallback al árbol. |
| `stop_reason: "refusal"` | Chequeado antes de leer `Content`. Fallback al árbol + notificación al admin con la categoría. |
| Modelo inventa un precio | No existe la tool. Además, regla explícita en el prompt y revisión manual de los primeros 50 diálogos. |
| Modelo inventa un rubro | Enums cerrados con `strict: true`, generados desde `RubroHelpers`. |
| Bot y humano pisándose | Pausa por contacto (§4). |
| Gasto descontrolado | Tope único + kill switch + card de costo (§5). |
| El prospecto nota que es un bot | Prompt con el tono ya afinado esta semana (sin `¡`/`¿` de apertura, sin listas, mensajes cortos). Los primeros diálogos se leen a mano. |
| Away-message ajeno → bot contra bot | Guarda `EsRespuestaAutomatica` intacta, **antes** del LLM. |
| Regresión total | Feature flag en base: apagarla devuelve el comportamiento exacto de hoy, sin deploy. |

Reglas del proyecto que el implementador tiene que respetar y que este plan ya contempla:
**MH-001** (nunca `Where(coleccionLocal.Contains(x))` contra este provider de MySQL, ni con colección
vacía — el historial se arma con `Where(m => m.ContactoId == id)`), **LP-003** (todo decimal que se
renderiza en un `value=` postable va con `InvariantCulture`; la app corre en `es-AR` y los importes de
la card nueva caen justo ahí), **AJAX por prioridad** (el toggle de pausa re-renderiza sólo su
partial) y `32-estandares-qa-implementador` leído antes de codificar.

---

## 7. Fases

**Septiembre queda pausado** (definición del cliente, 2026-09-13): no se manda nada más este mes, y
la versión nueva arranca en **octubre**. Eso da la ventana para hacer las fases 0 a 2 sin presión y
con el gasto del mes congelado.

| # | Fase | Cuándo | Qué entra | ¿LLM prendido en producción? |
|---|---|---|---|---|
| **0** ✅ | Prerrequisitos (§4) | **hecho 13/09** | **4.1** `Contacto.BotPausado` + migración + auto-pausa al mensaje manual + reanudación automática a las 48hs + toggle AJAX + corte en `HandleIncomingAsync`. **4.2** cerrar la fuga del tope en las 2 funciones de follow-up. | No hay LLM todavía |
| **1** ✅ | Infra + **modo sombra** | **hecho 13/09** | NuGet `Anthropic`, `IaSettings`, `ContactoMensajeIA`, `TarifaLlm`, `ConversacionIaService`, telemetría de tokens/costo, reparto y techos derivados (§5.8/§5.9), cards de `Bot/Index`, flag **apagada**. El servicio se invoca y **loguea lo que habría contestado, sin mandar nada**. | No — el prospecto sigue viendo el árbol |
| **2** ✅ | Herramientas | **hecho 13/09** | Las 8 tools, `strict: true`, prompt generado desde `RubroHelpers`, loop de tool use completo. Sigue en sombra. | No |
| **3** ✅ | Encendido para **todos los inbound** | **hecho 14/09** (adelantado, decisión del cliente) | Flag on para todo mensaje entrante de texto, sin acotar por canal (decisión del cliente: el piloto de ads solo serían 6-7 conversaciones/mes, no alcanza para aprender). Las 7 guardas siguen determinísticas. | **Sí** |
| **4** ✅ | Ajuste de outbound | **hecho y deployado 15/09** | El toque de **"Sí, contame más"** lo contesta la IA (antes disparaba la pregunta fija y la IA tomaba la charla a mitad de camino). "No me interesa" y los menús siguen determinísticos. Los botones y textos del frío se rehicieron por gancho en la feature **4 frentes — combo con gancho** (commit `382ad19`), sobre la que se construyó esto. | Sí |
| **5** | Medición y ajuste | octubre-noviembre | Completitud IA vs árbol, costo por conversación, calificaciones mal clasificadas, ajuste de prompt, revisión del orden de sacrificio de §5.9; `/Chats` marca qué mensajes los generó la IA. | Sí |

**Antes de prender la fase 3 hay que releer a mano los diálogos que el modo sombra generó.** Con
"todos los inbound" desde el día uno, el modo sombra es la única red que queda antes de exponer
prospectos reales — no es una etapa que se pueda saltear por apuro.

El **modo sombra de la fase 1 es el punto más importante del plan**: mide costo real, latencia real y
calidad real de las respuestas sobre conversaciones reales, con riesgo cero para el prospecto. Es lo
que convierte la estimación de la §5 en un número medido antes de exponer un solo cliente.

Migraciones previstas: `AddBotPausadoPorContacto` (fase 0) y `AddConversacionIa` (fase 1:
`ContactoMensajeIA` + `TarifaLlm` con su seed de precios + `ConversacionIaHabilitada`,
`ConversacionIaPausada` y `FactorHolguraTechos` en `ConfiguracionOutbound`). El reparto de §5.8 y los
techos de §5.9 no agregan más columnas: son cálculo sobre datos que ya se miden.

---

## 8. Definiciones cerradas por el cliente (2026-09-13)

Los 7 puntos que estaban abiertos quedaron resueltos. Esta es la definición vigente: no volver a
preguntar, y si algo cambia, cambiarlo acá con su fecha.

| # | Punto | Definición |
|---|---|---|
| 1 | Tope de gasto | **Septiembre pausado**: no se manda nada más este mes. La versión nueva arranca en **octubre**, y el tope de octubre se fija con el reparto de §5.8 a la vista. |
| 2 | Modelo | **`claude-opus-5`**. |
| 3 | Techos por herramienta | **Proporcionales a la operatoria**: se calcula el consumo por prospecto de cada herramienta y el techo sale de ahí, con el mismo factor de holgura para las tres (§5.9). Nada elegido a mano. |
| 4 | Orden de sacrificio | **Places → LLM → Meta**, confirmado. |
| 5 | Pausa por contacto | **Automática a las 48hs** de silencio del asesor, además del toggle manual. |
| 6 | Alcance del encendido | **Todos los inbound**, no sólo ads. El piloto acotado se descarta por falta de volumen de aprendizaje. |
| 7 | Cuestionario actual | **Se mantiene** como red de fallback. Es lo que hace el cambio reversible con un toggle. |

---

## 9. Dependencias y pendientes del proyecto que lo cruzan

- **El tope ya está configurado y ya está agotado**: `PresupuestoMensualArs` = ARS 250.000,
  `CotizacionUsdArs` = 1.540, y la mensajería de septiembre lleva **ARS 282.832 (113% del tope)** al
  día 13 — o sea que `CalcularVolumenDiario` devuelve 0 y **el outbound está detenido por precio en
  este momento**. No es un pendiente de este plan, pero define el contexto: no hay holgura, y cada
  peso de IA sale del volumen de envío (§5.1). Antes de prender la fase 3 conviene decidir si el tope
  de ARS 250.000 es el número correcto para octubre.
- `olv_reenganche_menu_v1` está **PENDING** en Meta; si se aprueba y el reenganche se activa, esos
  contactos van a volver a escribir. Conviene que lo hagan cuando ya haya decisión sobre el LLM.
- Búsqueda de Maps **pausada** (`BusquedaMapsPausada = 1`): el volumen de inbound va a bajar mientras
  siga así, y con él el costo estimado de la §5 (a la baja).
- **La API key no existe todavía en ninguna parte — hay que crearla.** Buscada el 2026-09-13 en los
  53 proyectos de `C:\Sistemas`, en los archivos de configuración y `.env`, en los 9 almacenes de
  user-secrets de la máquina y en las variables de entorno: **no hay ninguna `sk-ant-`**.
  `Olvidata Agentes Multi-rubro` tiene el código listo pero espera la key de una variable de entorno
  `Anthropic__ApiKey` / user-secrets que en esta máquina no está creada (no existe su store). O sea que
  ese proyecto tampoco está corriendo contra la API todavía.
  **Primer paso real de la fase 1**: crear la organización/key en la consola de Anthropic con
  facturación activa, cargarla por `dotnet user-secrets` para desarrollo y como variable de entorno del
  sitio en IIS (`olvidatasoft-002-site12`) para producción. Nunca en `appsettings.json` versionado.
- Conviene usar la **misma key para los 2 proyectos** (CRM y Agentes Multi-rubro) para tener un solo
  tablero de gasto en la consola de Anthropic, pero entonces el gasto del otro proyecto **no** va a
  estar reflejado en el tope del bot — el tope de §5 sólo mide lo que factura `ContactoMensajeIA`. Si
  eso llega a molestar, la separación correcta es una key por proyecto (o dos workspaces).

---

## 10. Estado de la implementación (2026-09-13)

Fases 0, 1 y 2 implementadas, build limpio (0 errores), 2 migraciones aplicadas a producción y
deploy OK (`portal.olvidata.com.ar` 200).

**Fase 0 — prerrequisitos**
- `Contacto.BotPausado` + `FechaBotPausado` + `PausarBotPorIntervencionDeAsesor()` +
  `PausaBotVencida()` (reanudación automática a las 48hs, evaluada en el webhook y no por un
  scheduler: el único momento en que la pausa importa es cuando el contacto vuelve a escribir).
- Auto-pausa en los **3** puntos de intervención manual (mensaje libre, presupuesto PDF, envío
  programado) — la regla vive en Domain para que los 3 compartan implementación (regla CRM-001).
- Corte en `BotFlowService.HandleIncomingAsync`, ubicado **después** de las guardas de baja y
  multimedia y **antes** de todo lo que responde: pausado significa "no le contestes", no "no lo
  escuches".
- Toggle AJAX en el detalle del chat (`Chats/TogglePausaBot`), re-renderizando el botón en su lugar.
- **Fuga del tope cerrada** (§4.2): `PlantillasEnviadasHoyAsync` cuenta los 3 caminos de envío, y
  `ProcessFollowUpsAsync` + `ProcessFollowUpMenuAsync` ahora consultan presupuesto y cupo.
- **`IsStandby` persistido** en `ConfiguracionOutbound.OutboundPausado`, leído en cada tick.

**Fases 1 y 2 — infraestructura, costo y herramientas**
- NuGet `Anthropic` 12.47.0 (la misma versión que ya usa `Olvidata Agentes Multi-rubro`).
- `ContactoMensajeIA` (transcript + telemetría, `CostoUsd` con precisión **decimal(18,8)** — con
  (18,2) cada llamada de USD 0,036 se habría guardado como 0,04 o 0,00) y `TarifaLlm` con las 4
  tarifas por modelo, sembrada con los 3 modelos.
- `ConversacionIaService`: loop de tool use, las **8 herramientas** con vocabulario generado desde
  `RubroHelpers`, system prompt generado, `Metadata.UserID` opaco, validación de los enums en código
  (no se confía en el schema), chequeo de `refusal` antes de leer el contenido, y fallback al árbol
  en toda falla.
- Reparto derivado de §5.8 y techos de §5.9 calculados en `GetCostoMensajeriaAsync`; card
  "Reparto del tope entre las 3 herramientas" en `Bot/Index` + la línea de IA en el desglose del
  gasto + campo del factor de holgura.
- 3 toggles en `/Bot`: encender/apagar IA, entrar/salir de modo sombra, pausar IA.

**Corregido durante la implementación** (encontrado al revisar, antes de deployar): el modo sombra
armaba el historial con sus propias respuestas, que el prospecto nunca vio — el modelo habría
razonado sobre una conversación inexistente y la medición de calidad no habría valido nada. Ahora las
filas de sombra quedan marcadas y excluidas, y mientras no haya conversación real con IA el historial
se reconstruye desde el hilo verdadero de `/Chats`. El mismo arreglo hace que pasar de sombra a vivo
en medio de una conversación ya empezada por el árbol sea continuo en vez de arrancar sin contexto.

**Septiembre pausado**: `OutboundPausado = 1` en producción (más Places ya pausada y la IA apagada).

### Lo único que falta para arrancar

1. **Crear la API key** en la consola de Anthropic con facturación activa. No existe ninguna en el
   estudio (§9).
2. Cargarla como variable de entorno del sitio en IIS: `Anthropic__ApiKey`. En desarrollo,
   `dotnet user-secrets set "Anthropic:ApiKey" "sk-ant-..."` sobre `OlvidataCRM.Web`.
3. Encender la IA desde `/Bot` (queda en **modo sombra**: mide sin responderle a nadie).
4. Leer a mano los diálogos que el modo sombra genere, y sólo entonces salir de sombra (fase 3).

Sin la key, `DisponibleAsync` devuelve false y el bot atiende con el árbol exactamente como hoy: no
hay que apagar ningún flag ni revertir nada.

---

## Historial de ajustes

| Fecha | Cambio |
|---|---|
| 2026-09-15 | **Fase 4 implementada** (commit `2f021b3`): el toque de "Sí, contame más" pasa a la IA con rubro y categoría (por gancho) resueltos antes, regla nueva en el prompt estable, y el cuestionario retoma sin duplicar el toque si la IA no está disponible. Probado con harness (servicios reales, WhatsApp falso, rollback, IA real): 25/25 PASS, USD 0,086. Construida encima de **4 frentes** (commit `382ad19`, migración `AddGanchoYFrenteComercial` aplicada a producción). **Deploy de las 2 bloqueado**: el puerto 8172 de Web Deploy de site4now no responde; producción sigue con `2ad3830`, compatible con las columnas nuevas. Medido desde el encendido: 5 conversaciones, USD 0,17, 3 bots descartados bien, 2 leads de ads sin segunda respuesta — la fase 5 todavía no tiene volumen para medir. |
| 2026-09-13 (5) | **Implementadas y deployadas las fases 0, 1 y 2** (ver §10): pausa del bot por contacto con reanudación a 48hs, fuga del tope cerrada en los 2 caminos de follow-up, `IsStandby` persistido, SDK `Anthropic` 12.47.0, `ContactoMensajeIA` + `TarifaLlm`, `ConversacionIaService` con las 8 tools y el prompt generado, reparto y techos derivados calculados, cards y 3 toggles en `/Bot`. 2 migraciones aplicadas a producción, deploy OK. Septiembre pausado. Corregido antes de deployar un bug de diseño del modo sombra (el historial divergía de la conversación real). Falta sólo la API key. |
| 2026-09-13 (4) | El cliente cerró los 7 puntos abiertos (§8, ahora "definiciones cerradas"): septiembre pausado y arranque en octubre, `claude-opus-5`, techos **proporcionales a la operatoria** con un único factor de holgura (§5.9 reescrita, `FactorHolguraTechos` como único parámetro), orden de sacrificio confirmado, pausa por contacto automática a las 48hs, encendido para **todos los inbound**, y el árbol se mantiene como fallback. Fases reancladas a septiembre (0-2) / octubre (3-5). Agregado §4.2: **fuga del tope por los follow-ups** (no consultan presupuesto ni cupo — explica el 113% del mes). Agregado §3.5: **reutilización de la integración con Claude que ya existe en `Olvidata Agentes Multi-rubro`** (SDK 12.47.0, patrón de settings, `Metadata.UserID` por Commercial Terms) y qué de ahí **no** copiar. §9: la API key no existe en ninguna parte, hay que crearla. |
| 2026-09-13 (3) | Pedido del cliente: fijar un costo de consumo único y que el sistema lo reparta entre las 3 herramientas (Places, Meta, LLM). Agregados §5.8 (reparto **derivado del costo unitario del pipeline**, no porcentajes a dedo: los 4 factores se miden en producción y el volumen diario sale de un solo número de entrada) y §5.9 (techos por herramienta como guardarraíl, suma 130% a propósito, + orden de sacrificio Places → IA → Meta). §5.4, §5.7 y §5.10 reconciliadas con el mecanismo general (el sub-tope de IA pasa a ser `TechoIaPct`); §8 reescrita. Medido: con Places reactivada el tope de ARS 250.000 sostiene 46-61 prospectos/día, y hay 3.709 prospectos en stock = 1,4 meses de envío. |
| 2026-09-13 (2) | Pedido del cliente: agregar el costo de mensajería del LLM para poder ponerle un límite de costo al bot. §5 reescrita completa como especificación de la tercera línea de costo (`TarifaLlm`, `GastoIaUsd`/`GastoIaArs`, snapshot de `CostoUsd`, sub-tope `TopeIaMensualArs`, escalera de degradación, card en `Bot/Index`), con el estado real del tope leído en producción (ARS 250.000 configurados, 113% consumido, envío detenido por precio) y el costo medido en ARS por mensaje y en volumen de envío perdido. Corregidos §8 y §9, que decían que el presupuesto seguía sin configurar. |
| 2026-09-13 | Versión inicial. Plan de implementación de la conversación agéntica con LLM, con volumen y embudo medidos en producción el mismo día. Pendiente de aprobación. |
