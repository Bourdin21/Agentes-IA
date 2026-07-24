# Memoria - Disenador funcional

## Proyecto: crm-olvidata — migración de BotPublicitario
## Última actualización: 2026-07-14

## Definiciones vigentes

### 0. Alcance funcional resumido (recap del Análisis aprobado)

3 entidades (`Contacto`, `ContactoRespuesta`, `IndustriaCatalogo`) y 9 casos de uso: alta manual y listado de contactos (CU-01/02), calificación automática por WhatsApp (CU-03/04), notificación a Joaquín (CU-05), derivación manual (CU-06), campaña outbound diaria (CU-10), búsqueda por Google Maps (CU-11) y mantenimiento del catálogo de industrias (CU-12). `Cliente`/`Upsell`/`Proyecto` quedan pospuestos.

### 1. Flujo de pantallas y wireframe textual

**Navegación:** se agrega una nueva sección al sidebar existente (`_Layout.cshtml`), debajo de "Sistema", visible para Vendedor+:

```
─ Comercial ──────────────
  📇 Contactos
─ Sistema ────────────────
  👥 Usuarios
  📧 Sistema / Email
  🤖 Bot / Outbound        (solo Administrador/SuperUsuario)
─ Super Usuario ──────────
  🕐 Auditoría
```

#### Pantalla 1 — `Contactos/Index` (CU-02)

```
┌─────────────────────────────────────────────────────────┐
│ Contactos                              [+ Nuevo contacto]│  ← título + acción primaria (btn-primary), a la derecha
├─────────────────────────────────────────────────────────┤
│ ov-card: Panel de filtros                                │
│  [Buscar teléfono/nombre] [Rubro▾] [Canal▾] [Estado▾]    │
│  [Rango de fecha 📅]                    [Filtrar][Limpiar]│
├─────────────────────────────────────────────────────────┤
│ DataTable server-side                                     │
│  Teléfono | Nombre | Negocio | Rubro | Canal | Estado |   │
│  Últ. actividad | Acciones (👁 Ver)                       │
└─────────────────────────────────────────────────────────┘
```
Cada columna visible tiene su filtro (regla obligatoria `25-frontend-design-system`): Teléfono/Nombre → buscador texto libre; Rubro/Canal/Estado → Select2; Última actividad → daterangepicker. Estado se muestra con `ov-badge` de color según `EstadoEmbudo` (ej. Pendiente=neutral, PresupuestoEnviado=info, Cerrado=success, Frio/Descartado=danger, DerivadoManual=warning).

#### Pantalla 2 — `Contactos/Details/{id}` (CU-02, soporte a CU-05/06)

```
┌─────────────────────────────────────────────────────────┐
│ Contacto: {NombreNegocio}                    [Editar]    │  ← breadcrumb Contactos > Detalle
├───────────────────────────┬───────────────────────────────┤
│ ov-card "Datos"           │ ov-card "Estado"               │
│  Teléfono, Nombre, Negocio│  EstadoEmbudo (badge)           │
│  Rubro, Zona, Canal       │  Fase conversación (badge)      │
│  Referido por (si aplica) │  Presupuesto cotizado (si hay)  │
│                           │  [Cambiar estado ▾] (manual)    │
├───────────────────────────┴───────────────────────────────┤
│ ov-card "Historial de calificación" (ContactoRespuesta)    │
│  Pregunta 1: ... → Respuesta: ...                          │
│  Pregunta 2: ... → Respuesta: ...                           │
├─────────────────────────────────────────────────────────────┤
│ ov-card "Notas"  [textarea + Guardar]                       │
└───────────────────────────────────────────────────────────┘
```
El selector "Cambiar estado" es la única vía manual para mover `EstadoEmbudo` a `DemoSolicitada`/`DemoRealizada`/`PropuestaEnviada`/`Cerrado`/`Descartado` (los estados automáticos del bot y del outbound no se tocan a mano). Requiere confirmación SweetAlert2 si el destino es `Descartado` (acción que saca al contacto del embudo activo).

#### Pantalla 3 — `Contactos/Create` (CU-01)

```
┌─────────────────────────────────────┐
│ Nuevo contacto                       │
├───────────────────────────────────────┤
│ ov-card "Datos del contacto"          │
│  Teléfono* [__________]               │
│  Nombre* [__________]                 │
│  Negocio [__________]                 │
│  Rubro [Select2 ▾, opciones = IndustriaCatalogo + "Otro"] │
│  Zona [__________]                    │
│  Notas [textarea]                     │
│                                        │
│  [Guardar]  [Cancelar]                │
└───────────────────────────────────────┘
```
`CanalOrigen` se fija en `Manual` sin mostrarlo (no aporta decisión al usuario en esta pantalla). Al guardar: `EstadoEmbudo = Pendiente`, `FaseConversacion = Nuevo`.

#### Pantalla 4 — `Industrias/Index` + `Create`/`Edit` (CU-12, dentro de "Bot / Outbound")

```
┌─────────────────────────────────────────────────────────┐
│ Catálogo de industrias                  [+ Nueva industria]│
├─────────────────────────────────────────────────────────┤
│ DataTable: Nombre | Sistema ref. | Plan | Precio USD |     │
│            ¿Cotiza automático? | Orden | Acciones (✏️🗑️)   │
└─────────────────────────────────────────────────────────┘
```
Form Create/Edit (card única, 6 campos — no necesita agrupar en fieldsets por ser corto): Nombre*, SistemaReferencia, Plan (Select: Starter/Pro/Premium/Scale), PrecioBaseUsd* (obligatorio si CotizaAutomatico), CotizaAutomatico (switch), PainHook (textarea corto, ayuda: "frase de dolor usada en el primer mensaje outbound"), Orden.

#### Pantalla 5 — `Bot/Index` (panel de Sistema, reemplaza `/outbound/status` + `/outbound/standby`)

```
┌─────────────────────────────────────────────────────────┐
│ Bot / Outbound                                            │
├───────────────────────┬───────────────────────────────────┤
│ ov-stat-card           │ ov-stat-card                       │
│  Enviados hoy: 42       │  Pendientes: 118                   │
├───────────────────────┴───────────────────────────────────┤
│ ov-card "Estado del scheduler"                             │
│  Estado: 🟢 Activo   Próxima corrida: Mar/Mié/Jue 09:30      │
│  [Pausar outbound]  (con confirmación SweetAlert2)           │
└─────────────────────────────────────────────────────────────┘
```
Reemplaza los endpoints admin del `Olvidata.Webhook` actual (`/outbound/status`, `/outbound/standby/{on|off}`, protegidos hoy por header `X-Admin-Key`) por una pantalla dentro del CRM protegida por `Authorize(Policy="RequireAdministracion")` — coherente con que todo el sistema ya usa cookies de Identity, no hace falta un mecanismo de auth paralelo.

### 2. ViewModels propuestos

```
ContactoListViewModel        { Items: List<ContactoListItemVM>, filtros, paginación DataTables }
ContactoListItemVM           { Id, Telefono, NombreContacto, NombreNegocio, Rubro, CanalOrigen, EstadoEmbudo, FechaUltimaActividad }

ContactoDetailsVM             { todos los campos de Contacto, Respuestas: List<ContactoRespuestaVM>, EstadosDisponibles: List<SelectListItem> }
ContactoRespuestaVM           { Pregunta, Respuesta, Fecha }

ContactoCreateVM              { Telefono [Required, Phone-like regex 549...], NombreContacto [Required], NombreNegocio, RubroId [nullable, Select2], Zona, Notas }
ContactoEditVM                { igual a Create + EstadoEmbudo [solo lectura visual salvo por el selector de Details] }

IndustriaCatalogoListVM       { Items: List<IndustriaCatalogoItemVM> }
IndustriaCatalogoCreateVM     { Nombre [Required], SistemaReferencia, Plan [Required, enum Select], PrecioBaseUsd [Required if CotizaAutomatico, decimal > 0], CotizaAutomatico [bool], PainHook, Orden [int] }
IndustriaCatalogoEditVM       { igual a Create + Id }

BotOutboundStatusVM           { EnviadosHoy, PendientesHoy, Standby, ProximaCorridaTexto }
```

### 3. Máquina de estados

**`FaseConversacion`** (conversación del bot — vida corta, dentro de un `Contacto`):

| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| *(sin conversación previa)* | Llega 1er mensaje, teléfono con registro outbound activo | `AskingQuestions` | `Contacto` existente con `CanalOrigen=OutboundFrio` y `EstadoEmbudo` en `MensajeEnviado`/`FollowUpEnviado` | Enviar saludo + primera pregunta de la industria ya conocida | — |
| *(sin conversación previa)* | Llega 1er mensaje, sin registro outbound | `AwaitingCategory` | — | Enviar menú de categorías (rent/build/landing) | — |
| `AwaitingCategory` | Responde "1" (rent) | `AwaitingIndustry` | — | Enviar lista de rubros | — |
| `AwaitingCategory` | Responde "2"/"3" (build/landing) | `AskingQuestions` | — | Enviar 1ª pregunta de esa categoría | — |
| `AwaitingCategory` | Responde texto libre no reconocido | `Completed` | — | Registrar como consulta libre, cerrar flujo | Categoria=`other`, sin cálculo de presupuesto |
| `AwaitingIndustry` | Responde rubro (número o texto) | `AskingQuestions` | — | Mapear a `IndustriaCatalogo`, enviar 1ª pregunta | Rubro no reconocido → Categoria=`rent_other` |
| `AskingQuestions` | Responde pregunta N, quedan preguntas | `AskingQuestions` | `QuestionIndex + 1 < Questions.Count` | Guardar `ContactoRespuesta`, enviar siguiente pregunta | — |
| `AskingQuestions` | Responde última pregunta | `Completed` | `QuestionIndex + 1 == Questions.Count` | Calcular presupuesto (si aplica), enviar cierre, notificar Joaquín (CU-04/05) | Industria no cotiza automático → sin presupuesto, solo notificación |
| `Completed` | Escribe de nuevo, < 24 h desde cierre | `Completed` (sin cambio) | `ahora - CompletedAt < 24h` | "Ya registramos tu consulta" + reenvía mensaje extra a Joaquín | — |
| `Completed` | Escribe de nuevo, ≥ 24 h desde cierre | `Nuevo → AwaitingCategory` | `ahora - CompletedAt >= 24h` | Reinicia conversación desde cero | — |

**`EstadoEmbudo`** (embudo comercial — vida larga, persiste más allá de una conversación):

| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| `Pendiente` | Scheduler outbound corre en el día del rubro, dentro del límite diario | `MensajeEnviado` | día programado del rubro + cupo diario disponible | Enviar plantilla `olv_frio_v2`/`olv_referido_v2` | Error API Meta → queda `Pendiente`, se loguea, reintenta al día siguiente |
| `MensajeEnviado` | Pasaron ≥ 7 días sin respuesta, día programado | `FollowUpEnviado` | `NeedsFollowUp` | Enviar plantilla `olv_nurturing_v2` | — |
| `FollowUpEnviado` | Pasaron ≥ 4 días sin respuesta al follow-up | `Frio` | `NeedsMarkingCold` | Marcar frío | — |
| `MensajeEnviado` / `FollowUpEnviado` / `Pendiente` | El contacto responde por WhatsApp | `Respondido` | — | Dispara `FaseConversacion` (bot arranca calificación) | — |
| `Respondido` | `FaseConversacion` llega a `Completed` con industria que cotiza automático | `PresupuestoEnviado` | `IndustriaCatalogo.CotizaAutomatico = true` | Enviar presupuesto (CU-04) | — |
| `Respondido` | `FaseConversacion` llega a `Completed` sin cotización automática | `DerivadoManual` | industria no cotiza o fuera de guion | Notificar a Joaquín sin presupuesto | — |
| Cualquiera antes de `Cerrado`/`Descartado` | Administrador cambia manualmente desde `Contactos/Details` | `DemoSolicitada` / `DemoRealizada` / `PropuestaEnviada` / `Cerrado` / `Descartado` | acción manual, rol Administrador+ | Actualizar estado, log de auditoría automático (ya provisto por la base) | No se permite volver a `Pendiente` manualmente (evita romper el conteo del scheduler) |

### 4. Reglas de negocio y permisos por pantalla/acción

| Pantalla/Acción | SuperUsuario | Administrador | Vendedor | Empleado |
|---|---|---|---|---|
| Contactos — Index/Details | ✅ | ✅ | ✅ | 👁 solo lectura |
| Contactos — Create/Edit | ✅ | ✅ | ✅ | ❌ |
| Contactos — Cambiar estado manual | ✅ | ✅ | ❌ (a confirmar en Arquitectura si se habilita) | ❌ |
| Industrias — CRUD | ✅ | ✅ | ❌ | ❌ |
| Bot/Outbound — panel + pausar | ✅ | ✅ | ❌ | ❌ |
| Webhook (endpoint público) | N/A — sin autenticación de usuario, valida `hub.verify_token` de Meta | | | |

Reglas:
- `Contacto.Telefono` único — validación server-side en `Create`, mensaje "Ya existe un contacto con ese teléfono" con link al existente (evita el problema de identidad duplicada detectado en Discovery).
- El webhook deduplica por `message_id` de Meta (ya resuelto en `MessageLogService` actual, se porta igual).
- `IndustriaCatalogo` no se puede poner `CotizaAutomatico=true` sin `PrecioBaseUsd > 0` (validación de formulario + server-side).
- Baja de `IndustriaCatalogo` es soft-delete (ya provisto por `SoftDestroyable`); si tiene `Contacto`s con ese rubro asignado, se advierte pero no se bloquea (el texto del rubro queda igual en `Contacto.Rubro`, es un campo libre, no FK).

### 5. Impacto funcional por capa

- **Presentación:** `ContactosController` (Index/Details/Create/Edit), `IndustriasController` (CRUD, dentro de Sistema), `BotController` (panel outbound), endpoint de Webhook de Meta (Minimal API o Controller, GET verificación + POST mensajes) — todo dentro de `OlvidataCRM.Web`.
- **Negocio:** `IBotFlowService`/`BotFlowService` (migrado desde `Webhook/BotFlowService.cs`, adaptado a leer/escribir `Contacto` vía `AppDbContext` en vez de JSON), `IOutboundCampaignService`/`OutboundCampaignService` (migrado desde `WhatsApp/OutboundCampaignService.cs`, adaptado igual), `IIndustriaCatalogoService` (cálculo de presupuesto), `IHostedService` para el scheduler diario (reemplaza `OutboundSchedulerService`).
- **Datos:** 3 entidades nuevas (`Contacto`, `ContactoRespuesta`, `IndustriaCatalogo`) + migración EF. Seed inicial de `IndustriaCatalogo` con las 13 industrias ya relevadas en `docs/meta-ads/definiciones/1-analista-funcional.md` (tabla "Fuente de precios — reconciliada").

### 6. Riesgos de implementación

- **Corte de BotPublicitario:** definir en Arquitectura el mecanismo exacto (¿DNS/reverse-proxy apunta el webhook de Meta al nuevo endpoint del CRM en un momento dado? ¿corren ambos en paralelo un tiempo?) — impacta cero pantallas de este diseño pero es crítico para no perder leads.
- **Migración de datos en tránsito:** si al momento del corte hay conversaciones/prospectos activos en los JSON/Excel actuales, hace falta un importador único (`Contacto` + `ContactoRespuesta`) — no hay pantalla de importación en este diseño porque es una tarea técnica de una sola vez, no una funcionalidad recurrente del CRM (se resuelve con un script/comando en Arquitectura, no con UI).
- **Reutilización de `WhatsAppClient`/`GoogleMapsService`:** ambos usan `Environment.GetEnvironmentVariable` para configuración (patrón .env de consola) — en el CRM deben pasar a `IOptions<T>` desde `appsettings`/user-secrets, consistente con `SmtpSettings` ya existente. Es un cambio de mecanismo de configuración, no de lógica.
- Botón "Cambiar estado" manual en `Contactos/Details` es la única superficie nueva de riesgo de uso indebido (ej. marcar `Cerrado` por error) — mitigado con confirmación SweetAlert2 + auditoría automática ya provista por la base (queda registro de quién y cuándo).

### 7. Plan funcional por etapas (para Arquitectura — no es plan de código)

1. **Datos base:** entidades `Contacto`/`ContactoRespuesta`/`IndustriaCatalogo` + migración + seed del catálogo de 13 industrias.
2. **Servicios de negocio migrados:** `BotFlowService`, `OutboundCampaignService`, cálculo de presupuesto — contra `AppDbContext`, sin UI todavía (verificable con pruebas funcionales directas al servicio).
3. **Webhook + scheduler:** endpoint de Meta absorbido en `OlvidataCRM.Web`, `IHostedService` outbound diario. Punto crítico del corte de producción.
4. **Pantallas CRM:** `Contactos` (Index/Details/Create/Edit), `Industrias` (CRUD), `Bot/Outbound` (panel).
5. **Corte y migración de datos en tránsito:** script de import único desde los archivos actuales de BotPublicitario, apagar el `Olvidata.Webhook` viejo.

### Historias de usuario

**HU-01** — Como Vendedor, quiero dar de alta un contacto manualmente para registrar un lead que surgió fuera del bot (ej. reunión presencial).
- CA1: el formulario exige Teléfono y Nombre; si el teléfono ya existe, se rechaza con mensaje claro y link al contacto existente.
- CA2: al guardar, el contacto aparece en el listado con Estado=Pendiente y Canal=Manual.

**HU-02** — Como Vendedor, quiero listar y filtrar contactos por estado, rubro, canal y fecha para encontrar rápido en qué situación está cada lead.
- CA1: cada columna visible (Rubro, Canal, Estado, Última actividad) tiene su filtro correspondiente.
- CA2: el buscador de texto libre encuentra por teléfono o nombre.

**HU-03** — Como prospecto que escribe por primera vez al WhatsApp de Olvidata (por ad o por respuesta a outbound), quiero que el bot me guíe con preguntas simples para no tener que explicar todo desde cero.
- CA1: si vengo de una campaña outbound ya identificada, el bot salta el menú y va directo a las preguntas de mi rubro.
- CA2: si escribo espontáneamente, el bot me pregunta primero qué tipo de ayuda busco (ordenar gestión / a medida / web).

**HU-04** — Como prospecto que ya indicó su rubro y cantidad de usuarios, quiero recibir un presupuesto automático para saber el costo sin esperar.
- CA1: el presupuesto se calcula como precio base de la industria + upsell por usuario excedente sobre los incluidos del plan.
- CA2: si mi rubro no tiene cotización automática, no recibo un número — se me avisa que un representante me va a contactar.

**HU-05** — Como Joaquín (Administrador), quiero enterarme al instante cuando un lead califica o pide demo, para no perder el timing de cierre.
- CA1: recibo una notificación in-app (campanita) con el resumen completo.
- CA2: recibo el mismo resumen por WhatsApp al número admin configurado.

**HU-06** — Como prospecto cuya respuesta no matchea ninguna opción esperada, quiero que igual alguien de Olvidata me contacte, para no quedar en el aire.
- CA1: el bot responde "un representante te va a contactar" sin bloquear la conversación.
- CA2: Joaquín recibe la notificación igual que en un cierre exitoso.

**HU-07** — Como Administrador, quiero que la campaña outbound respete el cronograma por rubro y el límite diario sin que yo tenga que ejecutarla a mano, para sostener el ritmo de prospección sin dedicarle tiempo.
- CA1: cada rubro se contacta solo el día de la semana que le corresponde.
- CA2: nunca se supera el límite diario configurado.
- CA3: un prospecto que no respondió en 7 días recibe un único follow-up; si no responde en 4 días más, se marca frío automáticamente.

**HU-08** — Como SuperUsuario, quiero buscar nuevos prospectos por rubro/zona desde Google Maps sin salir del CRM, para no depender de un script de consola aparte.
- CA1: los resultados se cargan como `Contacto` nuevo, con Canal=OutboundFrio.
- CA2: un negocio ya cargado (mismo teléfono) no se duplica.

**HU-09** — Como SuperUsuario, quiero editar el catálogo de industrias y precios desde una pantalla, para ajustar tarifas sin pedirle un cambio de código a nadie.
- CA1: el cambio de precio se aplica al siguiente presupuesto calculado, sin redeploy.
- CA2: no puedo activar "cotiza automático" sin cargar un precio base.

**HU-10** — Como Administrador, quiero ver el estado del scheduler outbound (enviados hoy, pendientes, activo/pausado) y poder pausarlo, para tener control manual ante un problema (ej. plantilla rechazada por Meta).
- CA1: el panel muestra los mismos datos que hoy expone `/outbound/status`.
- CA2: pausar/reanudar requiere confirmación y queda registrado en auditoría (vía usuario autenticado, no header compartido).

**HU-11** — Como Administrador, quiero poder corregir manualmente el estado comercial de un contacto (demo agendada, cerrado, descartado), para reflejar cosas que pasan fuera del bot (ej. una demo presencial).
- CA1: el selector de estado en `Contactos/Details` solo ofrece los estados posteriores a `Respondido` (no permite volver a `Pendiente`).
- CA2: marcar `Descartado` pide confirmación explícita.

## Diseño funcional — Campañas de contacto frío configurables (CERRADO — 2026-07-21)

**Gate verificado:** `definiciones/1-analista-funcional.md` — sección "Campañas de contacto frío configurables" — Condición de paso a Diseño **Cumplida (2026-07-21)**, 5 decisiones del cliente ya registradas ahí (límite = solo suma sin tope global, días fijos Mar/Mié/Jue subconjunto, template de selección fija, queries de Maps en alcance, migración por seed automático incluyendo queries).

**Nota:** desde el 2026-07-21 el sistema opera con un único rol (`SuperUsuario`) — la tabla de permisos de este diseño ya no distingue Administrador/Vendedor/Empleado como en la sección anterior de este mismo documento (esa tabla queda como referencia histórica del diseño original, no vigente).

### 0. Alcance funcional resumido (recap del Análisis aprobado)

1 entidad nueva de campaña + su relación con `IndustriaCatalogo` + queries de búsqueda editables por industria dentro de cada campaña. 3 casos de uso (CU-13 crear, CU-14 editar/pausar, CU-15 gestionar queries) + 2 historias de sistema (HU-12 ver listado, HU-13 scheduler opera contra campañas). Reemplaza `OutboundCampaignService.RunDayByType`, `GoogleMapsService.RubrosByDay`/`QueriesByRubro`, `RubrosRetirados` y `BotSettings.DailyLimit` como límite único.

### 1. Flujo de pantallas y wireframe textual

**Navegación:** no se agrega entrada nueva al sidebar — las pantallas de Campañas cuelgan de la sección "Bot / Outbound" ya existente, accesibles desde un link dentro de `Bot/Index`.

#### Pantalla 5 (extendida) — `Bot/Index`

Se agrega una tercera card a la fila existente (Enviados hoy / Pendientes se mantienen igual):

```
┌─────────────────────────────────────────────────────────────┐
│ Bot / Outbound                                                │
├───────────────────────┬───────────────────────────────────────┤
│ ov-stat-card            │ ov-stat-card                          │
│  Enviados hoy: 42        │  Pendientes: 118                      │
├───────────────────────┴───────────────────────────────────────┤
│ ov-card "Estado del scheduler"  (sin cambios)                  │
├─────────────────────────────────────────────────────────────────┤
│ ov-card "Campañas de contacto frío"                             │
│  3 activas · 1 pausada                     [Ver campañas →]     │
│  Comercio (Mar) · Farmacia (Mar) · Consultorios (Mié) · ...      │
├─────────────────────────────────────────────────────────────────┤
│ ov-card "Buscar prospectos por rubro (Google Maps)" (sin cambios)│
└─────────────────────────────────────────────────────────────────┘
```
El resumen es de solo lectura (nombres + día entre paréntesis, chips truncados si son muchas); el link "Ver campañas" lleva a la Pantalla 6.

#### Pantalla 6 — `Bot/Campanas` (CU-13/14, HU-12)

```
┌─────────────────────────────────────────────────────────────┐
│ ← Bot / Outbound                                              │
│ Campañas de contacto frío           [+ Nueva campaña]         │
├─────────────────────────────────────────────────────────────┤
│ DataTable server-side                                          │
│  Nombre | Industrias | Días | Límite diario | Template |       │
│  Estado | Acciones (✏️ Editar · ⏸/▶ Pausar/Reanudar · 🗑️)      │
└─────────────────────────────────────────────────────────────┘
```
Filtros (regla obligatoria, una columna visible = un filtro): Nombre → texto libre; Industrias → Select2 multi (filtra campañas que incluyan esa industria); Días → Select2 (Mar/Mié/Jue); Estado → Select2 (Activa/Pausada). Límite diario y Template no llevan filtro dedicado por ser de baja cardinalidad/poco valor de búsqueda — visibles en la grilla igual. Estado se muestra con `ov-badge` (Activa=success, Pausada=neutral). Acción "Pausar/Reanudar" es un toggle con confirmación SweetAlert2 (mismo patrón que el standby global de `Bot/Index`). "Eliminar" es soft-delete con confirmación `btn-swal-confirm`.

#### Pantalla 7 — `Bot/Campanas/Create` (CU-13)

```
┌───────────────────────────────────────────┐
│ Nueva campaña de contacto frío              │
├───────────────────────────────────────────┤
│ ov-card "Datos de la campaña"               │
│  Nombre* [__________]                       │
│  Días de envío*  ☐ Martes ☐ Miércoles ☐ Jueves │
│  Límite diario* [___] mensajes/día           │
│  Template de WhatsApp* [Select ▾ — 3 opciones]│
│  Activa desde el alta [switch, default ON]   │
├───────────────────────────────────────────┤
│ ov-card "Industrias"                         │
│  Industrias* [Select2 multi ▾, opciones =     │
│   IndustriaCatalogo]                          │
│  ⚠ si una industria ya está en otra campaña   │
│    activa, se marca en el combo y no se puede │
│    confirmar hasta sacarla                    │
├───────────────────────────────────────────┤
│  [Guardar y cargar queries →]  [Cancelar]    │
└───────────────────────────────────────────┘
```
Al guardar, redirige directo a la Pantalla 8 (Edit) para cargar las queries de búsqueda de cada industria elegida — una campaña recién creada queda con industrias sin queries todavía, por lo que **no puede estar Activa** hasta que cada industria tenga al menos 1 query (guarda de negocio, ver §4). El switch "Activa" del alta queda deshabilitado/forzado a OFF si no hay queries cargadas aún; se explica con un texto de ayuda corto bajo el switch.

#### Pantalla 8 — `Bot/Campanas/Edit/{id}` (CU-13/14/15)

```
┌───────────────────────────────────────────────┐
│ Editar campaña: Comercio                        │
├───────────────────────────────────────────────┤
│ ov-card "Datos de la campaña"  (mismos campos    │
│  que Create, precargados)                         │
├───────────────────────────────────────────────┤
│ ov-card "Industrias y queries de búsqueda"        │
│  Industrias* [Select2 multi ▾, precargado]         │
│                                                     │
│  ▾ Comercio  (4 queries)                [+ Agregar]│
│     "ferretería La Plata centro" — La Plata Centro │ [🗑️]
│     "librería La Plata centro" — La Plata Centro   │ [🗑️]
│     ...                                             │
│  ▸ Farmacia  (0 queries) ⚠ sin queries — no busca  │
│     prospectos nuevos hasta cargar al menos 1       │
├───────────────────────────────────────────────┤
│  [Guardar]  [Cancelar]                             │
└───────────────────────────────────────────────┘
```
Cada industria seleccionada es un panel colapsable (acordeón, expandido si tiene 0 queries para llamar la atención). Agregar/quitar queries es AJAX inline (mismo patrón que `Contactos/GuardarNotas`: POST sin recargar página, respuesta JSON `{success, message}` + SweetAlert2 toast), evita perder el resto del formulario al ajustar una sola query. Quitar la última query de una industria activa muestra advertencia (SweetAlert2 `warning`, no bloqueante) de que esa industria deja de encontrar prospectos nuevos hasta cargar otra — no impide guardar, es una campaña ya creada, distinto del alta.

### 2. ViewModels propuestos

```
BotOutboundStatusVM (existente)     { ..., CampanasResumen: List<CampanaResumenVM> }
CampanaResumenVM                    { Nombre, DiaCorto } // para la card resumen de Bot/Index

CampanaOutboundListVM               { Items: List<CampanaOutboundListItemVM>, filtros DataTables }
CampanaOutboundListItemVM           { Id, Nombre, Industrias: string (concatenado), Dias: string, LimiteDiario, Template, Activa }

CampanaOutboundCreateVM             { Nombre [Required, max 200], Dias: List<DayOfWeek> [Required, min 1, subset {Tue,Wed,Thu}], LimiteDiario [Required, int > 0], Template [Required, Select fijo 3 opciones], IndustriaIds: List<int> [Required, min 1], Activa [bool, default true] }
CampanaOutboundEditVM               { igual a Create + Id, IndustriasConQueries: List<CampanaIndustriaQueriesVM> }

CampanaIndustriaQueriesVM           { IndustriaId, IndustriaNombre, Queries: List<CampanaQueryItemVM> }
CampanaQueryItemVM                  { Id, Query [Required, max 300], Zona [Required, max 100] }

CampanaQueryAgregarVM               { CampanaId, IndustriaId, Query [Required], Zona [Required] } // POST AJAX inline
```

### 3. Máquina de estados

**No aplica** — confirmado en el Análisis (banderas tempranas: "Máquina de estados: No"). `Activa` es un flag booleano simple con una única guarda de negocio al querer ponerlo en `true`: la campaña debe tener al menos 1 industria y cada industria al menos 1 query. No hay transiciones encadenadas ni estados intermedios.

### 4. Reglas de negocio y permisos por pantalla/acción

Único rol del sistema (`SuperUsuario`) — acceso completo a las 3 pantallas nuevas, sin matices.

Reglas:
- Una industria no puede pertenecer a 2 campañas **activas** simultáneamente — validación server-side al guardar Create/Edit y al reactivar una campaña pausada; mensaje explícito con el nombre de la campaña que ya la tiene (ej. "Farmacia ya está asignada a la campaña 'Comercio y Farmacia'").
- No se puede poner `Activa=true` si la campaña no tiene industrias, o si alguna industria asociada tiene 0 queries cargadas — mensaje explícito señalando qué industria falta completar.
- Pausar (`Activa=false`) no descarta contactos en curso ni las queries/industrias ya configuradas — es reversible sin pérdida de datos.
- Eliminar campaña es soft-delete (`SoftDestroyable`) — no afecta contactos ya generados por ella (`Contacto.CanalOrigen` no depende de la campaña).
- El límite diario efectivo del pipeline es la suma de `LimiteDiario` de las campañas activas programadas para el día — sin tope global (decisión de Análisis #1), no hay validación que lo impida ni lo recorte.

### 5. Impacto funcional por capa

- **Presentación:** nuevas vistas dentro del área Bot/Outbound (`Bot/Campanas` Index/Create/Edit) — mismo controller (`BotController`) o uno dedicado, a definir en Arquitectura; no es una decisión funcional. Extensión de `Bot/Index` con la card resumen.
- **Negocio:** `OutboundCampaignService` deja de leer `RunDayByType`/`RubrosByDay`/`RubrosRetirados`/`BotSettings.DailyLimit` y pasa a consultar las campañas activas; `GoogleMapsService` deja de leer `QueriesByRubro` hardcodeado y pasa a leer las queries configuradas por industria/campaña; validación de industria-no-duplicada-entre-campañas-activas como regla de negocio nueva.
- **Datos:** entidad de campaña + relación con `IndustriaCatalogo` + queries de búsqueda por industria/campaña (entidades y claves exactas a definir en Arquitectura), más un campo de cruce en `IndustriaCatalogo` con las claves de rubro usadas hoy en código. Migración EF + seed de migración automática (campañas y queries generadas desde los diccionarios actuales, decisión de Análisis #5).

### 6. Riesgos y supuestos

- **Riesgo de UI sobrecargada:** la Pantalla 8 (Edit) combina datos de campaña + gestión de queries por industria en una sola vista — mitigado con acordeón colapsable por industria (expandido solo si tiene 0 queries) para no mostrar todo a la vez.
- **Riesgo heredado del Análisis:** sin tope global de seguridad sobre el límite diario total (decisión del cliente) — este diseño no agrega ninguna validación que lo compense, tal como fue decidido.
- **Supuesto:** el resumen de campañas en `Bot/Index` alcanza con nombre + día corto (sin límite/template) para no saturar la pantalla principal — el detalle completo vive en Pantalla 6. A confirmar si el cliente prefiere más datos ahí mismo.
- **Supuesto:** "Guardar y cargar queries" como paso obligatorio tras crear (redirect automático a Edit) es aceptable — alternativa sería permitir cargar queries inline ya en el formulario de Create, pero complica esa pantalla; a validar con el cliente si prefiere todo en un solo paso.

### 7. Plan funcional por etapas (para Arquitectura — no es plan de código)

1. **Datos base:** entidad de campaña + relación con `IndustriaCatalogo` + entidad de queries por industria/campaña + campo de cruce en `IndustriaCatalogo`, migración EF, seed de migración automática (campañas y queries desde `RunDayByType`/`QueriesByRubro` actuales).
2. **Servicios de negocio migrados:** `OutboundCampaignService`, `GoogleMapsService`, `OutboundSchedulerService` leyendo de las campañas en BD en vez de los diccionarios fijos — verificable con pruebas funcionales directas al servicio, sin UI todavía, y con `Standby=true` para no arriesgar envíos reales durante la validación.
3. **Pantallas:** `Bot/Campanas` (Index/Create/Edit) + extensión de la card resumen en `Bot/Index`.
4. **Apagado de los diccionarios hardcodeados:** una vez verificado que el pipeline funciona igual leyendo de BD, se retiran `RunDayByType`/`RubrosByDay`/`QueriesByRubro`/`RubrosRetirados` del código.

### Historias de usuario (continúan la numeración del diseño original — último HU usado: HU-11; y de este mismo análisis — HU-12/13 ya asignados)

**HU-14** — Como SuperUsuario, quiero crear una campaña de contacto frío eligiendo industrias, días y límite diario, para lanzar un nuevo frente de prospección sin pedir un cambio de código.
- CA1: no puedo guardar sin elegir al menos una industria y al menos un día de envío.
- CA2: si una industria ya está en otra campaña activa, me avisa cuál es y no me deja guardar hasta sacarla de una de las dos.

**HU-15** — Como SuperUsuario, quiero cargar y editar las queries de búsqueda de Google Maps de cada industria dentro de una campaña, para ajustar dónde buscamos prospectos sin depender de un deploy.
- CA1: puedo agregar una query nueva (texto de búsqueda + zona) a una industria de la campaña sin perder el resto del formulario (guardado inline).
- CA2: si intento activar la campaña con alguna industria sin queries cargadas, me avisa cuál falta completar y no me deja activarla.

**HU-16** — Como SuperUsuario, quiero pausar o reanudar una campaña puntual (no todo el outbound), para poder frenar una industria problemática sin cortar las demás.
- CA1: pausar una campaña no afecta contactos ya en curso ni borra su configuración (industrias/queries quedan intactas).
- CA2: el toggle global de standby (ya existente en `Bot/Index`) sigue siendo la pausa de emergencia de todo el pipeline; pausar una campaña puntual es más quirúrgico y no requiere tocar el standby global.

## Historial de ajustes
- 2026-07-14: Diseño funcional cerrado sobre el alcance recortado (solo migración de BotPublicitario). 5 pantallas, 2 máquinas de estados detalladas evento a evento, 11 historias de usuario con criterios de aceptación, plan funcional de 5 etapas para Arquitectura.
- 2026-07-21: Diseño funcional de "campañas de contacto frío configurables" cerrado. 4 pantallas (extensión de `Bot/Index` + `Bot/Campanas` Index/Create/Edit), sin máquina de estados (flag simple `Activa` con guarda de negocio), 5 ViewModels nuevos, 3 historias de usuario nuevas (HU-14/15/16) sobre las ya definidas en Análisis (HU-12/13), plan funcional de 4 etapas para Arquitectura. Condición de paso a Arquitectura: cumplida.
