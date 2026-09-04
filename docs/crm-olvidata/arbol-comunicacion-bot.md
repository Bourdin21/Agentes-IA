# Árbol de comunicación del bot — CRM Olvidata

Estado del código al **2026-09-03**. Derivado de `OlvidataCRM.Infrastructure/Services/BotFlowService.cs`
(máquina de estados y textos) y `OutboundCampaignService.cs` (envío frío, follow-up, frío).
Todo texto entre comillas es literal, tal como lo recibe el prospecto.

---

## 1. Las 3 puertas de entrada

| Puerta | Cómo llega | Estado inicial |
|---|---|---|
| **Outbound frío** | Campaña programada le manda la plantilla `olv_frio_v13` (274 campañas activas hoy) | `EstadoEmbudo=MensajeEnviado`, `FaseConversacion=ConfirmandoContinuar` |
| **Inbound orgánico** | Escribe al número sin que le hayamos escrito antes | `EstadoEmbudo=Respondido`, `FaseConversacion=Nuevo` |
| **Ads (click-to-WhatsApp)** | Toca el CTA de un anuncio de Instagram/Facebook | `CanalOrigen=AdsPagos`, `FaseConversacion=Nuevo` |

> El salto directo a `ConfirmandoContinuar` en la primera fila es porque `olv_frio_v10`+ traen los
> botones **dentro** de la propia plantilla. Las plantillas viejas sin botones dejan el contacto en
> `Nuevo` y el saludo con botones sale recién cuando el prospecto contesta cualquier cosa.

### 1.1 Plantilla del contacto frío (`olv_frio_v13`)

```
Hola! Vi tu negocio y pensé: {dolor del rubro}.

Soy Joaquín, de Olvidata Soft. Ayudamos a {rubro en plural} como el tuyo armando
sistemas a medida para ordenar {área del problema} de una vez por todas.

Básicamente, {mecanismo de la solución}.

Te sirve?

Un saludo,
Joaquín
Olvidata Soft

[ Sí, contame más ]  [ No me interesa ]
```

Los 4 huecos los completa `NarrativaByType(rubro)` / `Plural(rubro)` por rubro — no son genéricos.

---

## 2. Guardas globales (se evalúan ANTES del árbol, en este orden)

Cada mensaje entrante pasa por este embudo de cortes. El primero que matchea, corta.

```
Mensaje entrante
 │
 ├─ ¿Viene del número del admin? ─────────────────► IGNORAR (no activa nada)
 │
 ├─ ¿Es un away-message del propio comercio? ─────► Guardar en el hilo, NO avanzar el embudo
 │     (57%+ de los "Respondido" eran esto — ver FrasesAutoresponder)
 │     "gracias por comunicarte con...", "¿cómo podemos ayudarte?",
 │     "nuestro horario de atención...", "te responderemos a la brevedad"...
 │
 ├─ ¿Trae un email en el texto? ──────────────────► Guardarlo en Contacto.Email (si estaba vacío)
 │     y seguir con el flujo normal
 │
 ├─ ¿EstadoEmbudo = Descartado? ──────────────────► Guardar el mensaje y NUNCA responder
 │
 ├─ ¿EstadoEmbudo = Cerrado (ya es cliente)? ─────► Guardar + avisar al admin por WhatsApp.
 │     Sin respuesta automática al contacto
 │
 ├─ ¿Pide la baja en texto libre? ────────────────► BAJA (ver §5.1)
 │     "no me interesa", "no molesten", "dar de baja", "es spam",
 │     "número equivocado", "sáquenme", "no me escriban"... (~50 frases)
 │
 ├─ ¿Es imagen/audio/video/documento/sticker/ubicación/reacción?
 │                                        ────────► Guardar con su etiqueta ([Audio / nota de voz],
 │     [Imagen], etc.) y NO interpretarlo como respuesta del cuestionario
 │
 └─ ¿FaseConversacion = Completed? ───────────────► ver §5.3 (post-cierre)
       │
       └─ si no: entra al árbol (§3)
```

---

## 3. El árbol

> **Corrección 2026-09-03**: la primera versión de este diagrama dibujaba el saludo "Seguimos?"
> pegado a la caja `ConfirmandoContinuar` como si se mandara siempre — generó la duda real de si el
> bot repetía la confirmación después de que el prospecto ya tocara el botón de la plantilla frío.
> **No la repite.** Verificado contra producción (0 casos reales, solo un falso positivo por un
> mensaje manual de un asesor). El punto clave: **hay 2 caminos distintos hacia `ConfirmandoContinuar`**,
> y solo uno de ellos manda ese saludo — ver el diagrama corregido abajo.

```
                         ┌─────────────┐
                         │    Nuevo    │
                         └──────┬──────┘
                                │  primer mensaje real del contacto
            ┌───────────────────┴───────────────────┐
            │                                       │
   ¿Es outbound con rubro ya cargado?         Inbound / Ads
   (frío sin botones, vino, laboratorio,             │
    o un Referido que escribe orgánico)               │
            │ SÍ                              ¿El texto matchea un anuncio? (§3.1)
            ▼                                     │              │
  Resuelve rubro (clave → industria)            SÍ │              │ NO
  Categoría = "rent"                               ▼              ▼
            │                       (con rubro conocido)   ┌──────────────────┐
            ▼                       salta ambos menús →    │ AwaitingCategory │
  ┌──────────────────────┐          AskingQuestions        └────────┬─────────┘
  │ ConfirmandoContinuar │                                          │
  │   (vía OnNewAsync)   │                                          │
  └──────────┬───────────┘                                          │
             │                                                      │
   "Hola! Soy Joaquín, de Olvidata Soft.                            │
    Gracias por responder 🙌                                        │
    Seguimos?"                                                      │
    (si es Referido: sin repetir el nombre — ya se presentó         │
     en la plantilla olv_referido_v2)                               │
    [ Sí, contame más ] [ No me interesa ]                          │
             │                                                      │
      ┌──────┴───────┐                                              │
      │              │                                              │
"No me interesa"   cualquier otra cosa                              │
      │              │                                              │
      ▼              ▼                                              │
   BAJA (§5.1)   AskingQuestions ◄──────────────────────────────────┘
                                        (según la categoría elegida)
```

**El otro camino a `ConfirmandoContinuar`** — el que usa el 96% del tráfico real hoy — **no pasa por
acá arriba**: cuando la campaña manda `olv_frio_v13` (274 de 284 campañas activas), el botón "Sí,
contame más" / "No me interesa" ya viene **embebido en la propia plantilla de Meta**.
`OutboundCampaignService.SendDailyBatchAsync` pone `FaseConversacion = ConfirmandoContinuar`
**al momento del envío**, antes de que el prospecto conteste — así que cuando toca el botón, la
respuesta va directo a `OnConfirmarContinuarAsync` sin pasar nunca por `OnNewAsync` ni por el saludo
de arriba. Es el caso real de El Porteño Servicios (verificado en producción el 2026-09-02): mensaje
frío → toca "Sí, contame más" → directo a la Pregunta 1, sin ningún paso intermedio.

### 3.1 Detección de origen por anuncio (Ads-CTWA)

Si el primer mensaje trae el texto pre-cargado del CTA de un anuncio, se reconoce el posteo y se
saltean los menús. Meta además manda el `referral` real (ad id + headline), que se guarda para
atribución.

| Si el texto contiene | Rubro que asume | Reconocimiento que manda |
|---|---|---|
| `juani` | Inmuebles / Real estate | "Vi que te interesó el caso de Juani, el sistema para administrar inversores 🙌" |
| `conversor` | Contabilidad / Estudios contables | "Vi que te interesó cómo resolvimos el problema del conversor de un estudio contable 🙌" |
| `construyen operacion` | *(no lo sabe)* | "Vi que te interesó nuestro posteo: no vendemos software, construimos operación 🙌" |

Las dos primeras van directo a las preguntas. La tercera (posteo de marca) va al menú de categoría.

### 3.2 `AwaitingCategory` — menú de bienvenida

> "Hola! Soy Joaquín, de Olvidata Soft — armamos sistemas de gestión para PYMEs que se cansaron de
> perder horas en Excel o con datos sueltos.
> Con qué te damos una mano?"

| Opción | Categoría | Va a |
|---|---|---|
| 1 · Ordenar la gestión | `rent` | `AwaitingIndustry` (menú de rubros) |
| 2 · Algo 100% a medida | `build` | `AskingQuestions` |
| 3 · Web o landing | `landing` | `AskingQuestions` |
| *cualquier texto libre* | `other` | Cierra directo (§5.2) |

> **Gap pendiente de confirmación (2026-09-03):** este menú se manda como lista desplegable de
> WhatsApp (`SendListAsync`) — un elemento visualmente "de sistema". Con solo 3 opciones entraría
> perfecto en botones de respuesta rápida (máximo 3, 20 caracteres cada uno), como usa el resto del
> flujo. Cambiarlo es una mejora de UI real hacia "que no se note que es un bot", pero no se tocó
> todavía — pendiente de que el cliente confirme el cambio.

### 3.3 `AwaitingIndustry` — menú de rubros

> "A qué rubro pertenece tu negocio?"

Indumentaria o calzado · Alimentos y bebidas · Agro / Ganadería · Inmuebles / Real estate ·
Servicios técnicos · Comercio / Maquinaria · Salud / Medicina · Otro rubro

"Otro rubro" (o un texto que no matchea ninguna opción) cambia la categoría a `rent_other`, que usa
un cuestionario distinto — arranca preguntando a qué se dedica el negocio, porque en ese caso no lo
sabemos.

### 3.4 `AskingQuestions` — el cuestionario, por categoría

| Categoría | Preguntas (en orden) |
|---|---|
| **rent** | 1️⃣ Qué es lo que más te complica hoy en el día a día del negocio? *(ver §3.5)*<br>2️⃣ Con qué lo manejás ahora? (Excel, papel, cuaderno, otro sistema) |
| **rent_other** | 1️⃣ A qué se dedica exactamente tu negocio?<br>2️⃣ Qué es lo que más te complica hoy en la gestión? |
| **build** | 1️⃣ Contame en una línea: qué necesitás que haga el sistema?<br>2️⃣ Tenés una fecha en la que lo necesitás listo? |
| **landing** | 1️⃣ Partís de cero o ya tenés algo online?<br>2️⃣ Qué buscás? (institucional, tienda online o landing para captar clientes)<br>3️⃣ Vas a cargar contenido propio seguido? (tipo blog o novedades) |
| **merge** | Cuál de tus sistemas de Olvidata querés extender? · Qué función nueva necesitás? · Es urgente o lo planificamos? |
| **other** | Contame qué necesitás y te respondo a la brevedad 👍 |

> Nota (2026-09-03): se sacaron los signos de apertura (¡¿) de las 10 preguntas y de todos los
> mensajes de texto libre del flujo — mismo criterio ya aprobado por Meta en `olv_frio_v13`
> ("Hola!"/"Te sirve?", sin apertura). Se mantiene el signo de cierre (!/?).

> La pregunta "¿cuántas personas lo van a usar?" se sacó de **todas** las categorías el 2026-08-27
> (pedido explícito: se charla en la demo).

### 3.5 La pregunta 1 tiene 3 mecanismos posibles

Los decide `MecanismoPregunta1Async` — **la misma función** resuelve qué mandar y cómo interpretar
lo que vuelve, para que no se puedan desincronizar.

| Mecanismo | Cuándo | Qué manda |
|---|---|---|
| **Matriz de módulos** | El rubro tiene matriz MVP cargada (9 rubros hoy) | Texto libre listando los **4 módulos imprescindibles más caros** de ese rubro |
| **Menú fijo** | Rubro con sistema real pero sin matriz (hoy solo "Vinos y bebidas") | Lista interactiva de 3 opciones de dolor |
| **Texto libre genérico** | Todo el resto | La pregunta tal cual de la tabla de §3.4 |

Forma del mensaje con matriz:

```
1️⃣ En *{industria}* lo que más nos piden resolver es esto:

• {módulo 1}
• {módulo 2}
• {módulo 3}
• {módulo 4}

Contame cuáles de estos te complican hoy 👇 (y si lo tuyo es otra cosa, contámela igual)
```

> Es texto libre y no una lista interactiva a propósito: la lista de WhatsApp deja elegir **una
> sola** opción, y acá hace falta que pueda decir "estos dos" o "ninguno, lo mío es otra cosa".

### 3.6 El pitch va DESPUÉS del dolor, nunca antes

Solo para outbound en categoría `rent`, apenas contesta la pregunta 1:

> "¡Te entiendo totalmente! 🙌 Es de las cosas que más tiempo y plata se llevan sin que uno lo note,
> hasta que te toca {dolor del rubro}. Para *{industria}* ya tenemos un sistema armado y funcionando
> —lo usa {cliente de referencia}—, así que no lo hacemos desde cero para cada cliente."

Si el rubro no tiene sistema de referencia, cae a una versión sin prueba social. El orden
**gancho → dolor propio → solución** es deliberado: antes el pitch salía en el saludo, o sea vendía
antes de que el prospecto pusiera su problema en palabras.

---

## 4. Cierre normal

Al contestar la última pregunta:

> "Listo, gracias! 🙌 Con esto ya tengo todo.
> En las próximas horas te escribo por acá para mostrarte en una demo de 15 min cómo quedaría el
> tuyo funcionando. Sin compromiso: lo ves antes de decidir nada.
> Dejá el WhatsApp a mano 👀"

Y en paralelo, del lado interno:

- `EstadoEmbudo` → **DerivadoManual**, `FaseConversacion` → **Completed**
- Notificación in-app (campanita) a todos los SuperUsuarios con el brief completo
- WhatsApp al admin con la plantilla `olv_notif_respuesta`

El brief incluye: nombre, negocio, número, interés (categoría · rubro · canal), el Ad ID si vino de
un anuncio, y **todas** las respuestas del cuestionario.

> El bot **no cotiza**. La cotización automática se eliminó el 2026-08-24: un número seco sin
> anclaje contradecía el manual de pricing. El precio se da en la demo.

---

## 5. Ramas de salida

### 5.1 Baja (botón "No me interesa" o pedido en texto libre)

> "Listo, no vas a recibir más mensajes de nuestra parte. Disculpá las molestias 🙏"

- `EstadoEmbudo` → **Descartado** (queda excluido de todo envío y follow-up futuro por construcción)
- Se marca **leído automáticamente** y queda oculto del listado de Chats salvo que se tilde
  "Mostrar descartados"
- Si vuelve a escribir, se guarda el mensaje pero **nunca** se le responde

### 5.2 Consulta suelta (`other`)

Texto libre en el menú de bienvenida → se registra la consulta y cierra igual que §4, sin
cuestionario.

### 5.3 Escribe después del cierre

| Cuándo | Qué pasa |
|---|---|
| **Menos de 24 hs** | "Ya registramos tu consulta! 👍 Te escribo a la brevedad." + se le reenvía el mensaje al admin |
| **Menos de 24 hs, y ya van 2+ mensajes post-cierre** sin que un asesor haya intervenido | Corte automático → BAJA. Protege del loop bot-contra-bot (incidente real: 30 mensajes en 18 minutos) |
| **Más de 24 hs** | Se reinicia la conversación desde `Nuevo`, conservando todo el historial anterior |

> El corte de loop solo cuenta los mensajes posteriores a la última intervención manual de un
> asesor — si un humano ya contestó, lo que sigue es una conversación real, no un loop.

---

## 6. Mensajes automáticos fuera del árbol

| Disparo | Cuándo | Qué manda |
|---|---|---|
| **Follow-up** | 3 días desde el mensaje frío sin respuesta | Plantilla `olv_nurturing_v2` (caso de un negocio similar) → `EstadoEmbudo=FollowUpEnviado` |
| **Archivado en frío** | 4 días desde el follow-up sin respuesta | *Nada al contacto* → `EstadoEmbudo=Frio` |
| **Aviso de ventana** | La ventana de 24 hs de WhatsApp está por cerrarse | Notificación in-app al asesor (no al contacto) |
| **Mensaje programado** | Fecha/hora que fijó el asesor, dentro de la ventana de 24 hs | El texto o el PDF que dejó cargado |

Si el contacto responde en cualquier momento, deja de ser candidato a follow-up y frío.

> **Gap pendiente de confirmación (2026-09-03):** `olv_vino_v1` y `olv_laboratorio_v1` (10 campañas activas) todavía tienen "¿" de apertura ("¿se pierden en las cuentas corrientes...?", "¿saben si están vendiendo...?"). Corregirlas requiere el mismo proceso que `olv_frio_v13`: nueva versión del template, aprobación de Meta, reasignar las 10 campañas — no se tocó todavía.

---

## 7. Estados del embudo

```
Pendiente ──envío──► MensajeEnviado ──3 días──► FollowUpEnviado ──4 días──► Frio
                            │                          │
                            └──── responde ────────────┘
                                       │
                                       ▼
                                  Respondido ──termina el cuestionario──► DerivadoManual
                                       │                                        │
                                       │                                   (manual)
                                       │                                        ▼
                                       │                              PresupuestoEnviado
                                       │                                        │
                                       ▼                                        ▼
                                  Descartado                                 Cerrado
                            (baja, en cualquier                        (cliente ganado)
                             momento del flujo)
```

Los únicos estados asignables **a mano** desde el CRM son `Cerrado` y `Descartado`.

---

## 8. Dónde vive cada cosa

| Pieza | Archivo |
|---|---|
| Máquina de estados, todos los textos del diálogo | `OlvidataCRM.Infrastructure/Services/BotFlowService.cs` |
| Envío frío, follow-up, archivado en frío, armado de plantillas | `OlvidataCRM.Infrastructure/Services/OutboundCampaignService.cs` |
| Disparo por día/hora de cada campaña | `OlvidataCRM.Infrastructure/HostedServices/OutboundSchedulerService.cs` |
| Recepción de mensajes de Meta (`/webhook/whatsapp`) | `OlvidataCRM.Web/Program.cs` |
| Vocabulario de rubros (clave → industria → catálogo) | `OlvidataCRM.Application/Helpers/RubroHelpers.cs` |
| Alta/edición de las plantillas en Meta | `C:\Sistemas\BotPublicitario\WhatsApp` (CLI aparte) |
