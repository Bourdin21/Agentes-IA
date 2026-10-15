# Plan de implementación — el bot contesta los DM de Instagram

**Fecha:** 2026-10-15 · **Estado:** fases 1 a 5 implementadas (código). Falta la fase 0 (setup en
Meta, lo hace Joaquín) y la fase 6 (QA). El canal está deployable pero **apagado**:
`Features:InstagramDm = false`.
**Proyecto:** CRM Olvidata (`C:\Sistemas\olvidatasoft-crm`) · producción `https://portal.olvidata.com.ar/`

**Objetivo:** que un mensaje directo a `@olvidata.soft` entre por un webhook del CRM, lo conteste la
misma conversación agéntica con Claude que hoy atiende WhatsApp (`IConversacionIaService`), y quede
en el mismo hilo de `/Chats` con las mismas guardas de gasto y de pausa por contacto.

Referencias obligadas: [`plan-llm-conversacional-bot.md`](plan-llm-conversacional-bot.md) (la capa de
IA que se reutiliza tal cual), [`logica-negocio-bot.md`](logica-negocio-bot.md) y
[`arbol-comunicacion-bot.md`](arbol-comunicacion-bot.md) (§2, las guardas globales que **también**
valen para Instagram).

---

## 1. Lo que ya está resuelto y no hay que volver a hacer

El 80% del trabajo está hecho porque WhatsApp ya corre en este mismo proyecto:

| Pieza existente | Qué aporta a Instagram |
|---|---|
| Endpoint público HTTPS con webhook de Meta en producción (`Program.cs:260-273`) | El patrón exacto: GET de verificación + POST con ACK inmediato y procesamiento en background con `IServiceScopeFactory`. El bug del `ObjectDisposedException` ya está pagado — **copiar el patrón, no reinventarlo**. |
| `IConversacionIaService` / `ConversacionIaService` | La conversación con Claude completa: loop agéntico, herramientas, topes de gasto por contacto / día / mes, modo sombra. Recibe `Contacto` + texto; **no sabe ni le importa por qué canal entró**. |
| `IBotFlowService.HandleIncomingAsync(IncomingMessageDto, nombre)` | La máquina de estados, las guardas de descartado/cerrado/away-message, la pausa por contacto, el escalado al admin. |
| `Contacto` + `ContactoRespuesta` + `/Chats` | El hilo, el no-leído, la intervención manual del asesor, el PDF de presupuesto. |
| `ConfiguracionOutbound` (`ConversacionIaHabilitada`, `ConversacionIaPausada`, `ConversacionIaModoSombra`) | Las perillas de encendido ya persistidas y con pantalla en `/Bot`. |

Lo que falta es **un canal más de entrada y salida**, no un bot nuevo.

---

## 2. Alcance

### Entra
- Recibir y responder DM de Instagram (texto, respuestas a historias, adjuntos entrantes).
- Un `Contacto` por persona de Instagram, en el mismo CRM y el mismo embudo.
- La IA contesta con el mismo system prompt, consciente de que está en Instagram.
- Visibilidad del canal en `/Chats` y en el panel `/Bot`.

### NO entra (deliberado)
- **Outbound por Instagram.** No existe: la conversación la tiene que abrir la persona. No hay
  plantillas ni equivalente de la Marketing Messages API. Toda la maquinaria de
  `OutboundCampaignService`, campañas, ganchos y plantillas queda **fuera** de este canal.
- **Comentarios y menciones de posts.** Son otros campos de webhook (`comments`, `mentions`) y otra
  política de respuesta. Si después se quiere, es otro plan.
- **Unificar el contacto de Instagram con el de WhatsApp.** Si la misma persona escribe por los dos
  lados van a ser dos filas. El merge manual queda para un segundo paso (§5.4).
- Fusionar el gasto de IA en una línea nueva: Instagram consume **los mismos topes** que ya existen.

---

## 3. Prerrequisitos en Meta — bloqueantes, sin una línea de código

Esto se hace primero y se verifica en Graph API Explorer antes de tocar el repo. Si falla acá, el
código no se puede probar.

1. **Cuenta de Instagram profesional** (Business o Creator) y, en la app de Instagram,
   **Configuración → Mensajes → Herramientas conectadas → permitir acceso a los mensajes**
   activado. Sin ese toggle el webhook nunca dispara, sin error visible en ningún lado.
2. **Elegir la vía de autenticación** y no mezclarlas:
   - **Instagram API con Instagram Login** (recomendada): token propio de la cuenta de IG, sin
     depender de la Página de Facebook. Permisos `instagram_business_basic` +
     `instagram_business_manage_messages`. Envío por `graph.instagram.com`.
   - *Instagram API con Facebook Login*: token de Página, permisos `instagram_manage_messages` +
     `pages_manage_metadata`, envío por `graph.facebook.com/{page-id}/messages`. Solo tiene sentido
     si se quiere reusar la app y el token de Página que ya se usan para WhatsApp/Ads.
   **Definición pendiente de Joaquín** (§13).
3. **Producto "Instagram" agregado a la app de Meta** y suscripción del webhook a los campos
   `messages`, `messaging_postbacks`, `messaging_reactions`, `messaging_referrals`, `messaging_seen`
   (los `message_echoes` **no** hacen falta y conviene no suscribirlos: son los mensajes que manda
   la propia cuenta y solo generan ruido).
4. **URL de callback**: `https://portal.olvidata.com.ar/webhook/instagram` + Verify Token. Puede ser
   el mismo `Bot:VerifyToken` de WhatsApp o uno propio (`Instagram:VerifyToken`) — propio, para poder
   rotarlo sin tirar abajo WhatsApp.
5. **App Review**: `instagram_business_manage_messages` requiere revisión y la app tiene que estar en
   modo Live. En modo desarrollo solo contesta a los usuarios con rol en la app — alcanza para probar
   de punta a punta con la cuenta de Joaquín, así que **el review no bloquea las fases 1 a 5**, solo
   el encendido público.
6. **Human Agent** (opcional, decidir después): permiso aparte, se pide en App Review → Permissions &
   Features. Habilita contestar hasta 7 días después del mensaje de la persona con la etiqueta
   `HUMAN_AGENT`. Sin esto, pasadas 24 h **no hay forma de reabrir la conversación** y el chat queda
   muerto. Recomendación: pedirlo en el mismo review, el caso de uso es exactamente el nuestro
   (un asesor que contesta al día siguiente).
7. **Token de larga vida**. Los tokens de IG vencen (60 días, renovables). Dejarlo en variable de
   entorno del sitio en IIS y anotar el vencimiento donde se anotan los SSL — un token vencido hace
   que el bot deje de responder sin tirar error en la pantalla.

---

## 4. El punto duro: un contacto de Instagram no tiene teléfono

`Contacto.Telefono` hoy es **requerido y único**, y es la clave de todo: la búsqueda, el envío, el
display, la deduplicación del webhook. Una persona de Instagram trae un **IGSID** (id numérico
scopeado a la app, no es el `@usuario`) y nada más. Esto es la decisión de diseño del plan.

**Decisión propuesta:** identidad por canal en la misma fila de `Contacto`, no una entidad nueva.

```csharp
// Domain/Enums/CanalMensajeria.cs  (nuevo)
public enum CanalMensajeria { WhatsApp = 1, InstagramDm = 2 }

// Domain/Entities/Contacto.cs  (campos nuevos)
public CanalMensajeria CanalMensajeria { get; set; } = CanalMensajeria.WhatsApp;
public string? IgScopedId { get; set; }   // IGSID, unico, index
public string? IgUsername { get; set; }   // @usuario, puede cambiar: es display, nunca clave
```

y `Telefono` pasa a **nullable**, con la regla "`Telefono` o `IgScopedId`, al menos uno" validada en
la entidad (no hay CHECK constraint en MySQL que convenga acá).

### 4.1 Por qué no una entidad `ContactoCanal` 1:N
Es más limpia en el papel y **mucho** más cara: toca todas las queries de `ContactosController`,
`ChatsController`, el pipeline de Maps y los 3 schedulers. Con un canal y medio de tráfico no se
justifica. Si algún día entran Messenger y Telegram, se migra entonces.

### 4.2 El riesgo real de hacer `Telefono` nullable
Hay que barrer el repo, no confiar en el compilador:
- `c.Telefono.Contains(term)` en `ChatsController:766` y en `ContactosController` → `NullReferenceException`
  en tiempo de ejecución o SQL raro. Revisar **todos** los `.Telefono` sin `?`.
- **Todas** las queries de outbound y de los schedulers (`OutboundCampaignService`,
  `MensajesProgramadosSchedulerService`, `AvisosRenovacionSchedulerService`,
  `VentanaExpiracionSchedulerService`) tienen que filtrar
  `CanalMensajeria == WhatsApp && Telefono != null`. Es la red de seguridad para que un contacto de
  Instagram **nunca** entre a un lote de envío de plantillas: hoy el filtro es por `EstadoEmbudo`, y
  alcanza por casualidad (un contacto de IG nace `Respondido`, no `Pendiente`), no por diseño.
- Vistas que muestran `+{telefono}` o `wa.me/{telefono}` → mostrar `@usuario` cuando el canal es IG.

### 4.3 Deduplicación
`IgScopedId` con índice único. El IGSID es estable para la misma app+usuario, así que sirve igual que
el teléfono. El `@usuario` **no** es clave: se cambia.

---

## 5. Arquitectura

### 5.1 Piezas nuevas

| Archivo | Capa | Qué hace |
|---|---|---|
| `Web/Webhook/InstagramWebhookModels.cs` | Web | Records del payload crudo de IG (forma Messenger: `entry[].messaging[]`), separado de `WebhookModels.cs` porque **no comparten forma** con el de WhatsApp. |
| `Program.cs` → `/webhook/instagram` GET+POST | Web | Verificación + ACK inmediato + background, clonando el patrón de `/webhook/whatsapp`. |
| `Application/Interfaces/IInstagramClient.cs` | Application | `SendTextAsync(igsid, texto, bool comoHumanAgent)`, `SendAttachmentAsync(...)`, `GetPerfilAsync(igsid)`. |
| `Infrastructure/Services/InstagramClient.cs` | Infrastructure | Implementación con `HttpClient` tipado, misma forma que `WhatsAppClient` (incluida una `InstagramApiException` propia). |
| `Application/Interfaces/IMensajeriaSender.cs` | Application | **La pieza clave**: `EnviarTextoAsync(Contacto, string)` que rutea al cliente del canal del contacto. |
| `Infrastructure/Services/MensajeriaSender.cs` | Infrastructure | El ruteo: `contacto.CanalMensajeria` → `IWhatsAppClient` o `IInstagramClient`. |
| `Application/Settings/InstagramSettings.cs` | Application | `AccessToken`, `IgUserId`, `AppSecret`, `VerifyToken`, `ApiVersion = "v25.0"`. |
| Migración EF | Infrastructure | Los 4 campos nuevos + índice único en `IgScopedId` + `Telefono` nullable. |

### 5.2 `IMensajeriaSender` — por qué, y qué toca
`BotFlowService` llama **23 veces** a `_wa.Send*(contacto.Telefono, ...)`. Si Instagram se mete ahí con
un `if` por canal, son 23 `if`. La abstracción se paga sola:

```csharp
// antes
await _wa.SendTextAsync(contacto.Telefono, respuesta.Texto);
// despues
await _mensajeria.EnviarTextoAsync(contacto, respuesta.Texto);
```

Reglas del sender:
- `EnviarTextoAsync` funciona en los dos canales. Es el 90% de los llamados.
- `EnviarBotonesAsync` → WhatsApp: `reply_button` (máx. 3). Instagram: **quick replies** (hasta 13).
  Mapear, no inventar: la IA ya responde texto libre, los botones solo los usa el árbol de fallback.
- `EnviarListaAsync` (`SendListAsync`, el menú de rubros) → **no existe en Instagram**. El sender
  tiene que degradar a texto numerado, no tirar excepción. Es exactamente el nodo del árbol que la IA
  ya reemplazó, así que en IG se puede dejar sin menú.
- `EnviarPlantillaAsync` → **no existe en Instagram**. Que falle fuerte (`NotSupportedException`
  logueado + escalado al admin), no en silencio: si algo intenta mandar una plantilla a un contacto
  de IG, es un bug de filtro de los del §4.2 y hay que verlo.
- Los 3 llamados de `ChatsController` (`:484` texto manual, `:572` PDF, `ReactivarConversacion`) van
  por el sender. `ReactivarConversacion` manda plantilla → se deshabilita el botón para IG en la vista.
- Los avisos al admin (`_botSettings.AdminNotifyPhone`) **siguen saliendo por WhatsApp siempre**, sin
  importar el canal de origen del mensaje. Eso no se toca.

### 5.3 Normalización del entrante
`IncomingMessageDto` suma `CanalMensajeria Canal` y `string? IgUsername`; `From` pasa a ser
"teléfono **o** IGSID" según el canal, y `MessageId` toma el `mid` de IG. `HandleIncomingAsync` cambia
la búsqueda del contacto:

```csharp
var contacto = msg.Canal == CanalMensajeria.InstagramDm
    ? await _db.Contactos.Include(c => c.Respuestas).FirstOrDefaultAsync(c => c.IgScopedId == msg.From)
    : await _db.Contactos.Include(c => c.Respuestas).FirstOrDefaultAsync(c => c.Telefono == phone);
```

y el alta del contacto nuevo setea `CanalMensajeria`, `IgScopedId`, `IgUsername` y
`CanalOrigen = AdsPagos`… que **miente**: un DM de Instagram no vino de un ad pago. Agregar
`CanalOrigen.InstagramOrganico = 5` o reutilizar `Referido`. Decisión en §13.

### 5.4 Merge con el contacto de WhatsApp (fase posterior, no bloqueante)
Cuando el mismo negocio escribe por los dos canales van a quedar dos filas. Lo mínimo útil: en
`/Chats/Detail` de un contacto de IG, si el `NombreNegocio` o el `@usuario` matchea otro contacto,
mostrar un aviso "posible duplicado de +549…" con link. El merge automático **no** — une historiales
de dos personas distintas con una heurística floja.

---

## 6. El webhook de Instagram

### 6.1 Forma del payload (distinta a la de WhatsApp)
```json
{
  "object": "instagram",
  "entry": [{
    "id": "<IG_USER_ID de la cuenta>",
    "time": 1520383571,
    "messaging": [{
      "sender":    { "id": "<IGSID de la persona>" },
      "recipient": { "id": "<IG_USER_ID de la cuenta>" },
      "timestamp": 1520383571,
      "message": {
        "mid": "<id del mensaje>",
        "text": "hola, cuánto sale un sistema",
        "attachments": [{ "type": "image", "payload": { "url": "..." } }],
        "is_echo": true,
        "quick_reply": { "payload": "<id del boton>" },
        "reply_to": { "story": { "id": "...", "url": "..." } }
      }
    }]
  }]
}
```
No hay `changes[].value.messages[]`, no hay `contacts[]` con el nombre, no hay `statuses[]`. **El
nombre de la persona no viene en el payload**: hay que pedirlo con un GET a
`/{igsid}?fields=name,username,profile_pic` (o guardar solo el `@usuario` del propio payload cuando
viene). Decisión: una llamada por contacto nuevo, cacheada en `IgUsername`/`NombreContacto`, nunca en
cada mensaje.

### 6.2 Guardas del handler, en este orden
1. **`X-Hub-Signature-256`**: HMAC-SHA256 del body crudo con el App Secret, comparación en tiempo
   constante. Si no valida → 403 y log. Hoy el webhook de WhatsApp **no valida firma**: aprovechar y
   dejar el helper compartido para los dos (deuda técnica vieja, el endpoint es público y anónimo).
2. **`is_echo == true` → descartar y salir.** Es el mensaje que mandó la propia cuenta (incluido lo
   que Joaquín escribe desde la app de Instagram en el celular). Sin este corte, el bot se contesta a
   sí mismo en loop. **Es el bug más probable de toda la implementación.**
3. **`sender.id == recipient.id`** o `sender.id` == el `IgUserId` propio → descartar.
4. **Dedup por `mid`** con el mismo `HashSet` en memoria que ya usa WhatsApp.
5. `messaging_seen` / `messaging_reactions` → loguear y salir, **nunca** llamar al LLM. Una reacción
   con un corazón no es una consulta comercial y pagarla con un turno de Claude es tirar plata.
6. **Respuesta a historia** (`reply_to.story`): sí se atiende, pero el texto que llega a la IA tiene
   que decir que es respuesta a una historia, o el modelo contesta cualquier cosa.
7. **Mensaje solo con adjunto y sin texto**: se registra en `ContactoRespuesta` con el `MediaId`/URL,
   se avisa al admin, **no** se le pasa a la IA (no tenemos visión conectada en el loop).
   ⚠️ A diferencia de WhatsApp, las URLs de adjuntos de IG que llegan en el webhook **vencen**: si se
   quiere poder verlo después desde el CRM, hay que descargar los bytes en el momento, no guardar la URL.

### 6.3 ACK inmediato
Igual que WhatsApp: `Results.Ok()` al toque y `Task.Run` con `IServiceScopeFactory.CreateScope()`.
**No** usar el `IServiceProvider` de la request — ver el comentario de `Program.cs:286`.

---

## 7. El envío

### 7.1 Endpoint y body
```
POST https://graph.instagram.com/v25.0/{IG_USER_ID}/messages
Authorization: Bearer {ACCESS_TOKEN}

{ "recipient": { "id": "<IGSID>" }, "message": { "text": "..." } }
```
Adjuntos: por **URL pública** o por `attachment_id` de la Attachment Upload API —
`{"message":{"attachment":{"type":"image","payload":{"url":"..."}}}}`. Tipos soportados: imagen
(PNG/JPEG ≤8 MB), audio, video (≤25 MB) y **PDF (≤25 MB)**, así que el presupuesto en PDF sí se puede
mandar por IG.
⚠️ **Verificar al implementar**: el PDF de presupuesto hoy vive en `ContactoRespuesta.ArchivoPdf`
(bytes en la base) y se manda como bytes a WhatsApp. Para IG hace falta o una URL pública temporal
firmada (el endpoint `ChatsController.PresupuestoPdf` está detrás de `[Authorize]`, no sirve) o
resolver el upload de bytes. **Esto se confirma contra la doc en la fase 3, no se asume.**

### 7.2 La ventana de 24 h y por qué es más estricta que en WhatsApp
- La conversación **la abre siempre la persona**. No hay forma de escribir primero.
- 24 h para contestar libre. Después: **nada**, salvo `HUMAN_AGENT` (7 días, permiso aparte).
- No hay plantillas. El escape de WhatsApp ("mandá una plantilla aprobada y reabrís") **no existe**.

Impacto en el código existente:
- `MensajesProgramadosSchedulerService:109` chequea la ventana y, si cerró, deja el mensaje en error
  sugiriendo una plantilla. Para IG el mensaje de error es otro, y si hay `HUMAN_AGENT` aprobado se
  manda igual con la etiqueta. El chequeo pasa a ser **por canal**.
- `VentanaExpiracionSchedulerService` (avisa antes de que venza) sirve igual y vale más todavía acá,
  porque en IG no hay segunda oportunidad. Umbral propio para IG, más temprano.
- `/Chats`: el botón "Reactivar conversación" (plantilla) se oculta para contactos de IG y se
  reemplaza por el cartel de ventana cerrada.

### 7.3 Límites de ritmo
IG tiene sus propios rate limits por cuenta y conversación. Con el volumen de hoy no es un problema,
pero `InstagramClient` tiene que manejar el 429 con backoff y loguear el código de error de Meta como
ya hace `WhatsAppClient`, no tragarse la excepción.

---

## 8. La IA: lo poco que cambia

`ConversacionIaService.ResponderAsync(Contacto, texto, ct)` se usa **tal cual**. Los cambios son
chicos y todos en el prompt y en las guardas:

1. **El system prompt se genera** (§3.4 del plan de LLM) → agregar el canal: "estás contestando un DM
   de Instagram". Importa por tres cosas: no hay menús ni listas, los mensajes son más cortos y
   coloquiales, y el objetivo del turno es distinto — en IG conviene **pedir el WhatsApp o el mail**
   para seguir ahí, porque la ventana de 24 h sin plantillas hace que una conversación de varios días
   sea imposible. Ese es el embudo real: IG abre, WhatsApp cierra.
2. **Herramienta nueva o campo nuevo**: cuando la persona da su teléfono en el DM, hay que poder
   escribirlo en `Contacto.Telefono` (que ahora está vacío) y marcar el posible merge. El regex de
   email ya existe en `HandleIncomingAsync`; agregar el de teléfono argentino.
3. **Los topes de gasto son los mismos** (`MaxCostoUsdPorContacto` / `PorDia` / `PorMes`). IG suma
   tráfico sobre el mismo techo, así que el primer mes hay que mirar el gasto diario: el DM de IG
   trae más consultas no comerciales que el outbound de WhatsApp.
4. **Modo sombra**: `ConfiguracionOutbound.ConversacionIaModoSombra` ya existe. Encender Instagram
   **en modo sombra primero** (la IA calcula y loguea la respuesta, no la manda) y leer 20-30
   conversaciones reales antes de soltarla. En WhatsApp se saltó esa ventana; acá no conviene, porque
   el DM de Instagram tiene mucho más ruido (fans, spam, "hola", reacciones).
5. **Guarda nueva de no-prospecto**: `DescartarNoEsProspectoAsync` ya existe y la IA ya la puede
   llamar. En IG va a dispararse mucho más seguido. Verificar que un descarte no mande respuesta.

---

## 9. Pantalla

| Dónde | Cambio |
|---|---|
| `/Chats` lista | Ícono de canal por fila (WhatsApp / Instagram) y filtro por canal en `ChatFiltrosViewModel`. |
| `/Chats/Detail` | Encabezado con `@usuario` en vez de `+teléfono`; link al perfil de IG; cartel de ventana (24 h / cerrada / 7 días con human agent); botón "Reactivar" oculto. |
| `/Contactos` | Columna/filtro de canal; `Create` y `Edit` tienen que aceptar un contacto sin teléfono. |
| `/Bot` (panel) | Card de Instagram: webhook OK/falla, último mensaje recibido, vencimiento del token, DM de hoy. El estado del token es lo que evita el "el bot dejó de contestar y nadie sabe por qué". |

---

## 10. Configuración

`appsettings.json` (sin secretos):
```json
"Instagram": {
  "IgUserId": "17841400000000000",
  "ApiVersion": "v25.0",
  "HumanAgentHabilitado": false
}
```
Secretos por variable de entorno del sitio en IIS, igual que `Anthropic__ApiKey`:
`Instagram__AccessToken`, `Instagram__AppSecret`, `Instagram__VerifyToken`. En desarrollo,
`dotnet user-secrets`. **Nunca** en el `appsettings.json` versionado.

Feature flag en `FeatureFlags` (`Features:InstagramDm`, default `false`) para poder deployar todo
apagado y encender sin redeploy.

---

## 11. Fases

| # | Qué | Criterio de salida | Depende de |
|---|---|---|---|
| **0** | Setup en Meta: producto Instagram, permisos, token, toggle de la cuenta, webhook apuntado a producción | Graph API Explorer manda un DM a la cuenta de prueba y la verificación GET del webhook responde el challenge | §3, **bloqueante** |
| **1** | Modelo + migración: `CanalMensajeria`, `IgScopedId`, `IgUsername`, `Telefono` nullable + barrido del §4.2 | La app corre con WhatsApp **sin ninguna regresión**; outbound, schedulers y búsqueda filtran por canal | — |
| **2** | Webhook de entrada: modelos, firma, `is_echo`, dedup, normalización a `IncomingMessageDto`, alta del contacto | Un DM real queda guardado como `Contacto` + `ContactoRespuesta` y se ve en `/Chats`. **La IA todavía apagada para IG** | 0, 1 |
| **3** | `InstagramClient` + `IMensajeriaSender` + migrar los 23 llamados de `BotFlowService` y los 3 de `ChatsController` | Un asesor contesta un DM a mano desde `/Chats` y llega a Instagram. WhatsApp sigue intacto | 2 |
| **4** | IA: canal en el prompt, captura de teléfono, guardas de reacción/adjunto/historia — **en modo sombra** | 20-30 conversaciones reales con la respuesta de la IA logueada y revisada por Joaquín | 3 |
| **5** | Encendido en vivo + pantallas del §9 + card de monitoreo en `/Bot` | El bot contesta DM solo, con gasto diario dentro del tope | 4, App Review |
| **6** | QA con el catálogo de reglas (`definiciones/6-qa.md`) + regresión de WhatsApp | GO del QA | 5 |

Las fases 1 a 4 se pueden implementar con la app en modo desarrollo. El App Review solo bloquea la 5.

---

## 12. Riesgos

| Riesgo | Mitigación |
|---|---|
| **El bot se contesta a sí mismo** (`is_echo`) | Guarda explícita en el handler + test con un mensaje mandado desde el celular. Es el fallo más probable. |
| **Regresión en WhatsApp por el `Telefono` nullable** | La fase 1 se cierra sin tocar Instagram y con el outbound verificado. No mezclar las dos cosas en un deploy. |
| **Un contacto de IG entra a un lote de plantillas** | Filtro `CanalMensajeria == WhatsApp` en las queries de outbound y schedulers (§4.2), más el `NotSupportedException` del sender. Doble red. |
| **El token vence y el bot calla sin error** | Card en `/Bot` con el vencimiento + alerta cuando un envío a IG falla con error de auth. |
| **El gasto diario de IA se come el tope por el ruido del DM** | Modo sombra primero, guardas de reacción/adjunto, y mirar `MaxCostoUsdPorDia` la primera semana. |
| **La ventana de 24 h mata conversaciones a medias** | Pedir Human Agent en el review y diseñar el prompt para mover a WhatsApp temprano. |
| Nombres de permisos/versión de API cambiados por Meta | Verificar contra la doc **el día que se implementa**: lo de acá está chequeado al 2026-10-15 (`graph.instagram.com`, `v25.0`, `instagram_business_manage_messages`). |

---

## 13. Definiciones de Joaquín — RESUELTAS el 2026-10-15

1. **Autenticación: Instagram Login** (corregido el 2026-10-15, era Facebook Login). Al hacer la
   fase 0 se dio de alta una app de Instagram con su propio id y secret
   (`Olvidata Ads Manager-IG`, app id `1516384240104466`) y el token generado es de usuario de
   Instagram (prefijo `IGAA`), no de Página. Verificado contra las 2 APIs: `graph.instagram.com/me`
   lo acepta (`user_id 17841456625525075`, `olvidata.soft`, BUSINESS) y `graph.facebook.com` lo
   rechaza con error 190 "Cannot parse access token". Es además la vía que este plan recomendaba.
   Envío por `graph.instagram.com/{version}/me/messages`; no hace falta `PageId`; el `AppSecret` de
   la firma del webhook es **el de la app de Instagram**.
   **Consecuencia:** por esta vía no existe la Attachment Upload API (es de Messenger/Página) y la
   alternativa por URL pública no sirve, así que **el presupuesto PDF no se puede mandar por
   Instagram** — ver §14.
2. **`CanalOrigen.InstagramOrganico = 5`**, valor nuevo. No se reutiliza `Referido` ni `AdsPagos`:
   contar un DM orgánico como conversión de ads diluiría el 41% de ads pagos con tráfico que no se
   pagó. Hay que revisar los filtros publicados del panel que listan los valores del enum.
3. **Human Agent: se implementó detrás de la perilla** `Olvidata_Instagram:HumanAgentHabilitado`
   (default `false`). Se prende recién cuando Meta lo apruebe — mandar la etiqueta sin el permiso
   hace fallar el envío. Pedirlo o no en el App Review sigue siendo decisión de Joaquín, pero el
   código ya lo soporta sin tocar nada más.
4. **Objetivo en IG: califica igual que en WhatsApp.** Mismo embudo completo dentro del DM. El prompt
   agrega solo lo que cambia: mensajes más cortos, sin menús, y que pida el WhatsApp o el mail cuando
   la charla ya tiene sustancia — no como objetivo en lugar de calificar, sino porque la ventana de
   24hs sin plantillas hace imposible una conversación de varios días.
5. **Modo sombra: sí**, con la perilla que ya existía (`ConversacionIaModoSombra`). No hizo falta
   código nuevo.

---

## 14. Lo que quedó implementado (2026-10-15)

### Piezas nuevas
| Archivo | Qué hace |
|---|---|
| `Domain/Enums/CanalMensajeria.cs` | WhatsApp / InstagramDm. La bandera que decide cliente de envío, clave de búsqueda y elegibilidad para plantillas. |
| `Application/Settings/InstagramSettings.cs` | Config del canal. Los 3 secretos por variable de entorno (`Olvidata_Instagram__AccessToken`, `__AppSecret`, `__VerifyToken`). |
| `Application/Interfaces/IInstagramClient.cs` + `Infrastructure/Services/InstagramClient.cs` | Envío (texto, quick replies, documento), perfil y descarga de adjuntos. HttpClient tipado con timeout de 30s. |
| `Infrastructure/Services/InstagramApiException.cs` | Conserva el código de error de Meta: token vencido (190), permiso, rate limit, ventana cerrada. |
| `Application/Interfaces/IMensajeriaSender.cs` + `Infrastructure/Services/MensajeriaSender.cs` | **La pieza clave.** Rutea el envío por el canal del contacto. |
| `Web/Webhook/InstagramWebhookModels.cs` | Payload crudo (forma Messenger), separado del de WhatsApp. |
| `Web/Webhook/FirmaMetaWebhook.cs` | `X-Hub-Signature-256` compartida por los 2 webhooks. |
| Migración `AddCanalInstagramDm` | 4 campos nuevos, `Telefono` nullable, índice único de `IgScopedId` por columna generada. |

### Decisiones de implementación que no estaban en el plan
- **El índice único de `IgScopedId` va sobre una columna generada `IgScopedIdVivo`**, no sobre la
  columna real (regla LP-057). `Contacto` tiene query filter de soft-delete: con un único global, dar
  de baja un contacto de Instagram y que esa persona vuelva a escribir reventaría el `SaveChanges`
  del webhook y se perdería el mensaje entero. El hueco equivalente del único **preexistente** de
  `Telefono` queda como está: arreglarlo exige dropear y recrear un índice en producción y merece su
  propia migración. **Deuda anotada.**
- **`CanalMensajeria` se migra con `defaultValue: 1`**, no 0. EF genera 0, que no es un valor del
  enum: los ~3.000 contactos existentes habrían quedado en un canal inexistente y toda query que
  filtra `== WhatsApp` (lote frío, follow-ups, reenganche, recuperación) habría devuelto cero filas.
  El outbound se apagaba entero, en silencio, el día del deploy.
- **Bytes del adjunto en una columna nueva** (`ContactoRespuesta.ArchivoAdjunto`, tope 8 MB), no en
  `ArchivoPdf`: esa columna significa "presupuesto enviado" y la lee
  `MensajeriaHelpers.TuvoPresupuesto` — una foto de un prospecto habría contado como un presupuesto
  que nunca existió.
- **La ventana pasa a ser por canal** en un solo lugar (`MensajeriaHelpers.HorasVentana` /
  `UmbralAvisoVentanaHoras`). El "24" estaba escrito como literal en 5 sitios.
- **La captura automática de teléfono solo acepta formas reconocibles** (10 dígitos, 12/13 con 54, o
  11-15 con "+" explícito). La regla laxa dejaba pasar un CUIT de 11 dígitos como teléfono del
  contacto.
- **El envío de imágenes desde `/Chats` queda solo en WhatsApp.** Esa acción guarda el `MediaId` de
  Meta para poder volver a ver la imagen en el hilo, y en Instagram ese id no existe. Se corta con un
  mensaje explícito en vez de mandar a un destinatario vacío.
- **La firma del webhook de WhatsApp se activa sola** cuando se cargue `Olvidata_WhatsApp:AppSecret`.
  Vacío = comportamiento idéntico al de siempre, para no dejar de recibir mensajes reales el día del
  deploy.

### Lo que falta y por qué
1. **Fase 0 — setup en Meta (bloqueante, lo hace Joaquín).** Producto Instagram en la app, permisos,
   token de Página, el toggle de "permitir acceso a los mensajes" en la app de Instagram, webhook
   apuntado a `https://portal.olvidata.com.ar/webhook/instagram` con su Verify Token, y los 3
   secretos cargados como variables de entorno del sitio.
2. **El presupuesto PDF no se manda por Instagram** (resuelto el 2026-10-15 al pasar a Instagram
   Login). La Attachment Upload API (`/message_attachments`) es un endpoint de Messenger/Página, y la
   única alternativa documentada —adjunto por URL pública— no aplica: el PDF vive como bytes en
   `ContactoRespuesta.ArchivoPdf` y su endpoint está detrás de `[Authorize]`.
   Cómo quedó: `/Chats` corta el upload **antes** de guardar el archivo y dice "mandáselo por
   WhatsApp al +…" (si el contacto dio el teléfono). No se guarda un `ArchivoPdf` que nunca salió,
   porque esa columna significa "presupuesto enviado" y la lee
   `MensajeriaHelpers.TuvoPresupuesto`. Un envío programado de PDF a un contacto de Instagram queda
   `Fallido` con ese mismo texto en `ErrorMensaje`.
   Si alguna vez se quiere: hace falta un endpoint de descarga firmado y de vida corta, y recién
   entonces el adjunto por URL. **No está verificado** si la edge de upload existe por esta vía — un
   GET sobre ella devuelve el mismo error que sobre `/me/messages`, que sí existe para POST, así que
   el sondeo no distingue. La decisión se apoya en la documentación y en no tener URL pública.
3. **Fase 6 — QA.** Lo mínimo a probar, más allá del catálogo: (a) regresión completa de WhatsApp
   —outbound, follow-ups, avisos de renovación— sobre la base ya migrada, no solo registros nuevos;
   (b) un mensaje mandado desde la app de Instagram en el celular **no** tiene que disparar al bot
   (`is_echo`); (c) la búsqueda global de `/Chats`, `/Contactos`, `/Clientes` y `/Clientes/Nuevo` con
   un `@usuario` que solo existe en un contacto de Instagram (LP-002); (d) editar un contacto de
   Instagram sin teléfono y guardar.
4. **El merge Instagram ↔ WhatsApp sigue siendo manual** (§5.4). Lo implementado es el aviso: si la
   persona da por DM un número que ya está cargado en otro contacto, **no** se escribe y se notifica
   el posible duplicado.

---

## Historial de ajustes

- **2026-10-15** — plan creado. Datos de la API de Instagram verificados contra la documentación de
  Meta ese día. Nada implementado.
- **2026-10-15** — vía de autenticación corregida a **Instagram Login** (§13.1) al hacer la fase 0: el
  token generado es `IGAA` y no de Página. Cambió `InstagramClient` (host `graph.instagram.com`, envío
  a `me/messages`), `InstagramSettings` (se cae `PageId`, el `AppSecret` es el de la app de Instagram)
  y se dio de baja el envío de adjuntos. La guarda anti-eco pasa a comparar contra `entry[].id` del
  propio payload además del `IgUserId` configurado: Instagram Login expone 2 formas del id de la
  cuenta (`user_id` 17841… y uno scopeado a la app, 27077…) y no son el mismo número.
- **2026-10-15** — las 5 definiciones de §13 resueltas por Joaquín y fases 1 a 5 implementadas. Ver
  §14 por lo que quedó, las decisiones que no estaban en el plan y lo que falta. El canal se deploya
  apagado (`Features:InstagramDm = false`).
