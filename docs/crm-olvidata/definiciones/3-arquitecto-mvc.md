# Memoria - Arquitecto MVC

## Proyecto: crm-olvidata — migración de BotPublicitario
## Última actualización: 2026-07-14

## Definiciones vigentes

### 0. Alcance funcional resumido (recap)

Migrar la funcionalidad de `C:\Sistemas\BotPublicitario` a `OlvidataCRM` (`C:\Sistemas\olvidatasoft-crm`, base ya saneada y compilando): captación/calificación automática por WhatsApp, presupuesto automático, outbound diario, búsqueda por Google Maps, notificación in-app, y 5 pantallas de gestión (Contactos, Industrias, Bot/Outbound). Sin `Cliente`/`Upsell`/`Proyecto` (pospuestos).

### 1. Mapa de componentes — reutilización vs. nuevo

**Regla aplicada:** reutilizar todo lo ya resuelto en `OlvidataCRM` (Identity, auditoría, soft delete, notificaciones, `IRepository<T>`, `DataTableRequest/Response`, `ServiceResult`, Design System, health checks, rate limiting, Serilog) y todo lo ya resuelto en `BotPublicitario` (clientes HTTP de Meta/Google ya probados en producción) — nada de esto se reescribe.

| Componente | Origen | Tratamiento |
|---|---|---|
| `WhatsAppClient` | `BotPublicitario/WhatsApp/WhatsAppClient.cs` | Se porta **sin cambios de lógica** a `OlvidataCRM.Infrastructure/Services/`. Único cambio: constructor recibe `IOptions<WhatsAppSettings>` en vez de leer `Environment.GetEnvironmentVariable` (consistente con `SmtpSettings` ya existente). |
| `GoogleMapsService` | `BotPublicitario/WhatsApp/GoogleMapsService.cs` | Se porta igual, mismo cambio de configuración (`IOptions<GoogleMapsSettings>`). El tracking de queries usadas (`queries_used.txt`) pasa a una tabla `GoogleMapsQueryUsada` simple (evita depender de un archivo en disco del servidor, que en hosting compartido puede no persistir entre deploys). |
| `BotFlowService` | `BotPublicitario/Webhook/BotFlowService.cs` | Se migra: misma máquina de estados (ver Diseño §3), pero lee/escribe `Contacto`/`ContactoRespuesta` vía `AppDbContext` en vez de `ConversationStore` (JSON por teléfono). El mapeo `OutboundTypeToIndustry`/`IndustryPainHook` se reemplaza por consulta a `IndustriaCatalogo`. |
| `OutboundCampaignService` | `BotPublicitario/WhatsApp/OutboundCampaignService.cs` | Se migra: mismo cronograma por rubro y límites, pero opera sobre `IQueryable<Contacto>` en vez de `CampaignState` (JSON). `contacted_phones.txt` desaparece — el índice único de `Contacto.Telefono` ya garantiza no duplicar. |
| `OutboundSchedulerService` | `BotPublicitario/Webhook/OutboundSchedulerService.cs` | Se porta como `IHostedService` de `OlvidataCRM.Web`, mismo disparador diario (Mar/Mié/Jue 09:30 ART). El toggle standby pasa de endpoint `X-Admin-Key` a la pantalla `Bot/Index` (Identity). |
| `MessageLogService` | `BotPublicitario/Webhook/MessageLogService.cs` | Su responsabilidad de logging a `.jsonl` desaparece (la traza ya la da `AuditLog`, automática). Su deduplicación por `message_id` de Meta (evita reprocesar reintentos) se conserva, migrada a un `HashSet` en memoria dentro del nuevo endpoint webhook — **limitación conocida y aceptada igual que hoy**: no sobrevive a un restart del proceso ni escala a múltiples instancias (ver Riesgos técnicos). |
| `ExcelTrackerService` | `BotPublicitario/WhatsApp/ExcelTrackerService.cs` | **No se porta.** Su función (historial de contactados) la cubre directamente la tabla `Contacto` + `AuditLog`. |
| `TemplateCreationService`, `CatalogService` | `BotPublicitario/WhatsApp/` | **No se portan** (confirmado en Diseño — sin UI de plantillas/catálogo Meta esta iteración). Siguen existiendo como utilitarios de consola en `BotPublicitario` si hace falta re-ejecutarlos manualmente. |
| `MetaAdsClient` y scripts Python | `BotPublicitario/MetaAds/` | **No se tocan**, fuera de alcance (confirmado en Discovery/Análisis). |

### 2. Desglose por capa

#### Domain (`OlvidataCRM.Domain`)

Entidades nuevas, todas heredan `SoftDestroyable`:

```csharp
public class Contacto : SoftDestroyable
{
    public string Telefono { get; set; }                  // requerido, único, formato 549...
    public string? NombreContacto { get; set; }
    public string? NombreNegocio { get; set; }
    public string? Rubro { get; set; }                     // texto libre, resultado de calificación
    public string? Zona { get; set; }
    public string? Direccion { get; set; }
    public double? Lat { get; set; }
    public double? Lng { get; set; }
    public CanalOrigen CanalOrigen { get; set; }
    public string? ReferidoPor { get; set; }
    public string? MotivoReferido { get; set; }
    public FaseConversacion FaseConversacion { get; set; } = FaseConversacion.Nuevo;
    public string? Categoria { get; set; }                 // rent | rent_other | build | merge | landing | other
    public int QuestionIndex { get; set; }                 // progreso dentro de AskingQuestions
    public int? CantidadUsuarios { get; set; }              // input de calificación usado en el cálculo de presupuesto
    public EstadoEmbudo EstadoEmbudo { get; set; } = EstadoEmbudo.Pendiente;
    public decimal? PresupuestoCotizadoUsd { get; set; }
    public DateTime? FechaPrimerEnvio { get; set; }
    public DateTime? FechaFollowUp { get; set; }
    public DateTime? FechaRespuesta { get; set; }
    public DateTime? FechaCompletado { get; set; }
    public DateTime FechaUltimaActividad { get; set; }
    public string? UltimoMensajeId { get; set; }
    public string? Notas { get; set; }

    public ICollection<ContactoRespuesta> Respuestas { get; set; } = new List<ContactoRespuesta>();
}

public class ContactoRespuesta : SoftDestroyable
{
    public int ContactoId { get; set; }
    public string Pregunta { get; set; } = string.Empty;
    public string Respuesta { get; set; } = string.Empty;
    public Contacto Contacto { get; set; } = null!;
}

public class IndustriaCatalogo : SoftDestroyable
{
    public string Nombre { get; set; } = string.Empty;
    public string? SistemaReferencia { get; set; }
    public PlanSistema Plan { get; set; }
    public decimal? PrecioBaseUsd { get; set; }
    public bool CotizaAutomatico { get; set; }
    public string? PainHook { get; set; }
    public int Orden { get; set; }
}

// Tabla de apoyo — reemplaza queries_used.txt de GoogleMapsService
public class GoogleMapsQueryUsada : SoftDestroyable
{
    public string Rubro { get; set; } = string.Empty;
    public string Query { get; set; } = string.Empty;
}
```

Enums nuevos (`Domain/Enums/`, persistidos con `HasConversion<int>()` — convención ya vigente):

```csharp
public enum CanalOrigen { AdsPagos = 1, OutboundFrio = 2, Referido = 3, Manual = 4 }

public enum FaseConversacion { Nuevo = 1, AwaitingCategory = 2, AwaitingIndustry = 3, AskingQuestions = 4, Completed = 5 }

public enum EstadoEmbudo
{
    Pendiente = 1, MensajeEnviado = 2, FollowUpEnviado = 3, Respondido = 4,
    PresupuestoEnviado = 5, DemoSolicitada = 6, DemoRealizada = 7, PropuestaEnviada = 8,
    Cerrado = 9, Frio = 10, Descartado = 11, DerivadoManual = 12
}

public enum PlanSistema { Starter = 1, Pro = 2, Premium = 3, Scale = 4 }
```

#### Application (`OlvidataCRM.Application`)

Interfaces nuevas (`Interfaces/`):

```csharp
public interface IWhatsAppClient { /* SendTextAsync, SendTemplateAsync, SendListAsync — misma firma que hoy */ }
public interface IGoogleMapsService { /* SearchDailyAsync, SearchAsync */ }
public interface IBotFlowService { Task HandleIncomingAsync(IncomingMessageDto msg, string? contactName); }
public interface IOutboundCampaignService
{
    Task<int> SendDailyBatchAsync(CancellationToken ct = default);
    Task<int> ProcessFollowUpsAsync(CancellationToken ct = default);
    Task<int> MarkColdAsync(CancellationToken ct = default);
    Task<OutboundStatsDto> GetStatsAsync();
}
```

DTOs nuevos (`DTOs/`): `IncomingMessageDto` (payload normalizado del webhook, para no filtrar el modelo crudo de Meta hasta Negocio), `OutboundStatsDto` (EnviadosHoy, PendientesHoy — calculados con `COUNT` sobre `Contacto`, reemplaza `CampaignStats`), `ContactoListItemDto`.

Settings nuevos (`Settings/`, mismo patrón que `FeatureFlags`):
```csharp
public class WhatsAppSettings { public string AccessToken; PhoneNumberId; BusinessAccountId; BusinessId; ApiVersion = "v21.0"; }
public class GoogleMapsSettings { public string ApiKey; }
public class BotSettings { public string AdminNotifyPhone; public string VerifyToken; public int DailyLimit = 125; }
```
Secciones de configuración (`appsettings.json`, mismo patrón que `Olvidata_Email`): `Olvidata_WhatsApp`, `Olvidata_GoogleMaps`, `Olvidata_Bot`.

**No se agrega** `IIndustriaCatalogoService` como capa aparte — el CRUD de `IndustriaCatalogo` usa `IRepository<IndustriaCatalogo>` directo desde `IndustriasController` (catálogo simple, mismo patrón que `ConfiguracionController` de la base KOI original para Rubros/Subgrupos, sin necesidad de service intermedio). El cálculo de presupuesto vive dentro de `BotFlowService` (es lógica de negocio del bot, no un servicio reutilizable aparte).

#### Infrastructure (`OlvidataCRM.Infrastructure`)

- `AppDbContext`: agrega `DbSet<Contacto>`, `DbSet<ContactoRespuesta>`, `DbSet<IndustriaCatalogo>`, `DbSet<GoogleMapsQueryUsada>`. `OnModelCreating`: índice único en `Contacto.Telefono`; `ContactoRespuesta.ContactoId` FK `OnDelete(Cascade)`; `IndustriaCatalogo.PrecioBaseUsd` con `HasPrecision(18,2)`; conversión de enums a `int` (mismo patrón que `EstadoUsuario`).
- `Services/`: `WhatsAppClient`, `GoogleMapsService`, `BotFlowService`, `OutboundCampaignService` (implementaciones, ver §1).
- `HostedServices/OutboundSchedulerService.cs`: `IHostedService`, dispara `OutboundCampaignService` diariamente, con flag `Standby` estático leído/escrito desde `BotController`.
- `DependencyInjection.cs`: agrega `Configure<WhatsAppSettings>`, `Configure<GoogleMapsSettings>`, `Configure<BotSettings>`, `AddHttpClient<IWhatsAppClient, WhatsAppClient>()`, `AddHttpClient<IGoogleMapsService, GoogleMapsService>()`, `AddScoped<IBotFlowService, BotFlowService>()`, `AddScoped<IOutboundCampaignService, OutboundCampaignService>()`, `AddHostedService<OutboundSchedulerService>()`.
- **Paquetes NuGet:** ninguno nuevo. `WhatsAppClient`/`GoogleMapsService` usan `HttpClient` + `System.Text.Json` (ya en el framework). No se porta `ClosedXML` para esto (ya está en Infrastructure para `ExportService`, pero no se necesita para el bot).

#### Web (`OlvidataCRM.Web`)

- **Controllers nuevos:** `ContactosController` (`[Authorize(Policy="RequireVendedor")]` — reutiliza policy ya definida en `Program.cs`), `IndustriasController` (`[Authorize(Policy="RequireAdministracion")]`), `BotController` (`[Authorize(Policy="RequireAdministracion")]`).
- **Webhook de Meta:** se mapea como Minimal API en `Program.cs` (igual patrón que `BotPublicitario/Webhook/Program.cs`, sin forzarlo a un Controller MVC — es la forma más directa de portar `GET/POST /webhook/whatsapp` con verificación de `hub.verify_token`). Sin `[Authorize]` (Meta no manda cookie de sesión) y sin la policy `general` de rate limiting (Meta ya controla su propio ritmo de entrega). Delega inmediatamente a `IBotFlowService` tras el ACK 200 (mismo patrón fire-and-forget que hoy, para evitar timeout/reintentos de Meta).
- **Vistas:** `Views/Contactos/{Index,Details,Create,Edit}.cshtml`, `Views/Industrias/{Index,Create,Edit}.cshtml`, `Views/Bot/Index.cshtml` — Design System (`ov-card`, `ov-badge`, DataTables server-side), según wireframes de Diseño §1.
- **Sidebar (`_Layout.cshtml`):** agrega sección "Comercial" (Contactos, visible Vendedor+) y entrada "Bot / Outbound" bajo "Sistema" (visible Administrador+), según Diseño.

### 3. Modelo de permisos

No se crean policies nuevas — se reutilizan las ya definidas en `Program.cs`:
- `RequireVendedor` (SuperUsuario, Administrador, Vendedor) → Contactos.
- `RequireAdministracion` (SuperUsuario, Administrador) → Industrias, Bot/Outbound.
- Webhook público: sin policy de Identity, se autentica solo con `hub.verify_token` de Meta (igual que hoy).

Empleado queda sin acceso a estas pantallas por ahora (Diseño lo dejó "a confirmar"; no se define policy nueva hasta que haya un caso de uso concreto — evita crear una policy sin uso).

### 4. Migraciones EF

**Sí, requerida.** Una migración (`dotnet ef migrations add AddContactosYCatalogoIndustrias`) que agrega 4 tablas: `Contactos`, `ContactoRespuestas`, `IndustriaCatalogos`, `GoogleMapsQueryUsadas`. No modifica ninguna tabla existente (Identity/AuditLog/Notification/PreferenciaUsuario quedan intactas). Se aplica primero en dev (`olvidatacrm_dev`, ya verificado que el flujo `dotnet ef database update` funciona en esta base).

**Seed adicional:** las 13 industrias ya relevadas en `docs/meta-ads/definiciones/1-analista-funcional.md` (tabla "Fuente de precios — reconciliada") se cargan en `SeedData.cs` como `IndustriaCatalogo` inicial, mismo patrón que el seed de roles/SuperUsuario ya existente (idempotente, `if (await db.IndustriasCatalogo.AnyAsync()) return;`).

### 5. Riesgos técnicos

- **Corte de producción (el más crítico):** BotPublicitario sigue operando mientras se construye esto. Runbook propuesto para el "día D": (1) QA funcional completo del nuevo webhook en la ventana de desarrollo aparte, sin tráfico real; (2) importar datos en tránsito (ver siguiente punto); (3) cambiar en el Meta App Dashboard la URL de callback del webhook de WhatsApp de la del `Olvidata.Webhook` actual a la del nuevo endpoint del CRM; (4) mantener el proceso viejo apagado pero no borrado por unos días de respaldo antes de decomisionarlo. Esto es un paso operativo, no requiere código nuevo más allá de lo ya diseñado.
- **Importación de datos en tránsito:** si al momento del corte hay conversaciones/prospectos activos en `outbound_state.json`, `conversations/*.json`, `contactos.xlsx`, se resuelve con un comando de consola de un solo uso (`dotnet run --project OlvidataCRM.Web -- import-legacy-botpublicitario <ruta>`), no una pantalla del CRM — se descarta después de usarlo una vez.
- **Deduplicación de webhooks por reintentos de Meta:** se mantiene la limitación actual (HashSet en memoria, no persistente) por decisión de preservar comportamiento legacy. Si se detectan duplicados reales en producción, la mejora futura es un índice único sobre un campo `UltimoMensajeId` procesado — no se implementa preventivamente (YAGNI).
- **Concurrencia en alta de `Contacto`:** dos flujos pueden intentar crear el mismo teléfono a la vez (webhook responde justo cuando el outbound lo está cargando). El índice único de `Telefono` en MySQL actúa como red de seguridad — el flujo que llega segundo debe capturar la excepción de duplicado y hacer `UPDATE` en vez de `INSERT` (patrón ya usado en el estudio para numeradores/correlativos, ver `27-presupuesto-parametros`/patrones cross-proyecto de `ContadorFactura`).
- **Cronograma outbound hardcodeado:** el mapeo rubro→día de la semana sigue siendo una constante en código (como hoy), no editable desde la pantalla `Bot/Index` — Diseño no pidió esa edición, se preserva así por alcance.

### 6. Estrategia de pruebas funcionales

QA manual (no automatización de navegador, según preferencia ya establecida del estudio): validar cada historia de usuario de Diseño (HU-01 a HU-11) con pasos concretos contra la base de desarrollo, incluyendo:
- Webhook simulado con `curl`/Postman contra `/webhook/whatsapp` con payloads de ejemplo (mensaje nuevo, respuesta de calificación, reintento con mismo `message_id`).
- Verificación de que `AuditLog` registra los cambios de `Contacto` automáticamente (ya provisto por la base, sin código adicional).
- Prueba de carga del outbound scheduler en modo manual (invocar el `IHostedService` fuera de horario para no esperar al cronograma real).

### Gate de aprobación para pasar a Presupuesto

**Pendiente de confirmación del cliente.** Arquitectura no introduce paquetes NuGet nuevos, no crea policies nuevas, reutiliza el 90% de la lógica de negocio ya escrita y probada en `BotPublicitario`, y requiere 1 migración EF con 4 tablas nuevas sin tocar las existentes. El riesgo principal (corte de producción) tiene un runbook operativo definido, no bloquea el desarrollo.

## Arquitectura técnica — Campañas de contacto frío configurables (CERRADO — 2026-07-21)

**Gate verificado:** Análisis (`1-analista-funcional.md`) y Diseño (`2-disenador-funcional.md`) cerrados y aprobados. Orquestador saltea Presupuesto a pedido explícito del cliente (mismo precedente que la migración original de BotPublicitario, 2026-07-17) — pasa directo a Implementación.

### 0. Alcance funcional resumido (recap)

Reemplazar `OutboundCampaignService.RunDayByType`, `GoogleMapsService.RubrosByDay`/`QueriesByRubro`/`RubrosRetirados` y `BotSettings.DailyLimit` (único) por campañas configurables desde el CRM. 3 entidades nuevas + 1 enum. CU-13/14/15, HU-12 a HU-16.

### 1. Clarificaciones técnicas sobre el Diseño (decisiones de Arquitectura, no cambian lo funcional aprobado)

Dos puntos que el Diseño dejó explícitamente "a definir en Arquitectura" y que al traducirlos a datos reales requieren una decisión técnica:

**a) Granularidad real: "rubro" ≠ "industria del catálogo de precios".** Los ~13 rubros operativos de hoy (`comercio`, `farmacia`, `dieteticas`, `consultorio`, `clinica`, `inmobiliaria`, `indumentaria`, `estudio`, `ganaderia`, `agro`, `servicios`, `maquinaria`, `residuos`) no mapean 1:1 contra las filas de `IndustriaCatalogo` (varios rubros comparten una misma fila de precio — ej. `ganaderia` y `agro` → misma fila "Ganadería / producción agropecuaria"; `consultorio` y `clinica` → misma fila "Laboratorios / consultorios médicos"). Por eso `ClaveRubro` (la clave granular que hoy vive en `Contacto.Rubro` y en las claves de `QueriesByRubro`) se modela en **`CampanaOutboundIndustria`** (la relación campaña↔industria), no en `IndustriaCatalogo` — permite que "Ganadería" y "Agro" sean dos campañas-industria distintas (cada una con su propio cronograma/queries) aunque coticen con el mismo precio base. La regla de negocio "una industria no puede estar en 2 campañas activas" del Diseño se implementa correctamente como **"una `ClaveRubro` no puede estar en 2 campañas activas"** — es la granularidad real del conflicto operativo (dos campañas por igual rubro sí duplicarían contacto; dos campañas con el mismo precio de catálogo pero rubro distinto no).

**b) Queries de búsqueda cuelgan de `CampanaOutboundIndustria`, no de `IndustriaCatalogo`.** Consecuencia directa de (a): si las queries fueran de `IndustriaCatalogo`, "Ganadería" y "Agro" no podrían tener listas de queries independientes pese a ser rubros de búsqueda distintos. Cuelgan de la relación campaña-industria — coincide exactamente con la UI ya diseñada (Pantalla 8, acordeón por industria dentro de la campaña), solo cambia la clave técnica de destino.

**c) `IndustriaCatalogoId` en `CampanaOutboundIndustria` es opcional (nullable).** Dos de los rubros existentes (`farmacia`, `estudio`) **no tienen fila propia en el catálogo de 13 industrias** (gap ya documentado en `5-implementador.md` del ciclo anterior: "Farmacia" y "Contabilidad/Estudios contables" quedan `DerivadoManual`, sin cotización automática). Para preservar el comportamiento legacy completo del seed de migración (decisión de Análisis #5: "una campaña por cada rubro que ya está en `RunDayByType` hoy" — farmacia y estudio están ahí), se agregan **2 filas nuevas a `IndustriaCatalogo`** como parte de esta implementación: "Farmacias" y "Estudios contables / jurídicos", ambas con `CotizaAutomatico=false` (mismo comportamiento de hoy — sin cotización automática, sin cambiar esa lógica) — solo para tener un ancla de catálogo y poder mostrarlas en el Select2 de industrias de la pantalla de campañas. Esto evita dejar 2 rubros del barrido actual sin poder migrarse.

**d) El campo `TemplateWhatsApp` de la campaña gobierna únicamente el primer contacto de `CanalOrigen.OutboundFrio`.** El mensaje de **Referido** sigue fijo en `"olv_referido_v2"` (un contacto Referido no "pertenece" a la campaña de la misma manera — su `Rubro` solo define día/límite de envío vía la campaña que contenga esa `ClaveRubro`, no el template) y el de **follow-up** sigue fijo en `"olv_nurturing_v2"` (etapa distinta del pipeline, no del alta). Motivo: la Pantalla 7/8 del Diseño ofrece "3 opciones" de template en el dropdown, pero mezclar las 3 en un solo campo de campaña rompería el envío de referidos/follow-ups (dejarían de usar su template fijo ya aprobado) — preserva comportamiento legacy salvo indicación contraria (regla obligatoria de la operativa global). En la práctica, hoy el dropdown de campaña solo tiene sentido real con 1 opción (`olv_frio_v3`); las otras 2 quedan listadas para cuando Meta apruebe una variante nueva de mensaje frío en el futuro.

### 2. Impacto técnico por capa

#### Domain (`OlvidataCRM.Domain`)

```csharp
// Enums/DiasSemana.cs
[Flags]
public enum DiasSemana { Martes = 1, Miercoles = 2, Jueves = 4 }

// Entities/CampanaOutbound.cs
public class CampanaOutbound : SoftDestroyable
{
    public string Nombre { get; set; } = string.Empty;
    public DiasSemana Dias { get; set; }
    public int LimiteDiario { get; set; }
    public string TemplateWhatsApp { get; set; } = string.Empty; // validado contra lista fija en el controller
    public bool Activa { get; set; }
    public ICollection<CampanaOutboundIndustria> Industrias { get; set; } = new List<CampanaOutboundIndustria>();
}

// Entities/CampanaOutboundIndustria.cs
public class CampanaOutboundIndustria : SoftDestroyable
{
    public int CampanaOutboundId { get; set; }
    public CampanaOutbound CampanaOutbound { get; set; } = null!;
    public int? IndustriaCatalogoId { get; set; }              // opcional, ver §1.c
    public IndustriaCatalogo? IndustriaCatalogo { get; set; }
    public string ClaveRubro { get; set; } = string.Empty;      // granular: "comercio", "farmacia", etc. — único entre campañas ACTIVAS
    public ICollection<CampanaQuery> Queries { get; set; } = new List<CampanaQuery>();
}

// Entities/CampanaQuery.cs
public class CampanaQuery : SoftDestroyable
{
    public int CampanaOutboundIndustriaId { get; set; }
    public CampanaOutboundIndustria CampanaOutboundIndustria { get; set; } = null!;
    public string Query { get; set; } = string.Empty;
    public string Zona { get; set; } = string.Empty;
}
```

`TemplatesDisponibles` (lista fija, no entidad): constante estática `["olv_frio_v3"]` hoy — se deja como `List<string>` estático en `OutboundCampaignService` o `CampanaOutbound` (Application, no Domain) para no crear una tabla de catálogo por 1 solo valor útil; agregar una variante nueva sigue siendo un cambio de código (consistente con la decisión #3 del Análisis).

#### Application (`OlvidataCRM.Application`)

- `IOutboundCampaignService`: sin cambios de firma (`SendDailyBatchAsync`/`ProcessFollowUpsAsync`/`MarkColdAsync`/`GetStatsAsync`) — la implementación cambia de fuente de datos, el contrato no.
- `IGoogleMapsService.SearchDailyAsync`: cambia de firma — se elimina el parámetro `targetTotal` (antes global, ahora cada campaña define su propio `LimiteDiario`, ver §1). Único caller es `OutboundSchedulerService`, cambio seguro.
- Nuevo DTO `CampanaOutboundListItemDto` no es necesario — el listado usa un ViewModel directo desde `AppDbContext` (patrón ya usado en `IndustriasController`, sin capa de servicio intermedia).

#### Infrastructure (`OlvidataCRM.Infrastructure`)

- `AppDbContext`: `DbSet<CampanaOutbound>`, `DbSet<CampanaOutboundIndustria>`, `DbSet<CampanaQuery>`. Fluent API: `Dias` con `HasConversion<int>()`; `CampanaOutbound` 1:N `CampanaOutboundIndustria` con `OnDelete(Cascade)`; `CampanaOutboundIndustria` 1:N `CampanaQuery` con `OnDelete(Cascade)`; `CampanaOutboundIndustria` → `IndustriaCatalogo` con `OnDelete(Restrict)` (evita múltiples rutas de cascada en MySQL, `IndustriaCatalogo` nunca se borra físicamente de todas formas).
- `OutboundCampaignService.SendDailyBatchAsync`/`ProcessFollowUpsAsync`: dejan de leer `RunDayByType`/`RubrosRetirados`; consultan `CampanaOutbound` activas cuyo `Dias` incluye el día actual (`(Dias & flagHoy) == flagHoy`), agrupan candidatos por `ClaveRubro` de sus `CampanaOutboundIndustria`, límite = `campana.LimiteDiario` (por campaña, no global — decisión #1). Selección de template: `contacto.CanalOrigen == Referido ? "olv_referido_v2" : campana.TemplateWhatsApp` (envío frío) / siempre `"olv_nurturing_v2"` (follow-up) — ver §1.d. `MarkColdAsync` no cambia (no tenía gating por rubro/día).
- `GoogleMapsService`: se eliminan `RubrosByDay`/`QueriesByRubro` estáticos. `RubrosDisponibles` pasa a ser `ClaveRubro` distintos entre las `CampanaOutboundIndustria` con al menos 1 `CampanaQuery` (consulta async — cambia de propiedad sincrónica a método, único ajuste de firma pública, revisar el único consumidor `BotController.Index`). `SearchByRubroAsync(rubro, maxResults)` resuelve queries buscando `CampanaOutboundIndustria` por `ClaveRubro` (entre campañas activas o no — la búsqueda manual de CU-11 no depende de que la campaña esté activa) en vez del diccionario estático; mismo mecanismo de rotación contra `GoogleMapsQueryUsada` (sin cambios, ya es DB). `SearchDailyAsync(DayOfWeek day, ct)`: nueva firma sin `targetTotal`; itera campañas activas de ese día, por cada `CampanaOutboundIndustria` busca con `maxResults = Ceiling(campana.LimiteDiario / cantidadIndustriasDeEsaCampana)` (mismo criterio de reparto que el código legacy).
- `OutboundSchedulerService.RunPipelineAsync`: elimina `const int targetSends = 125`; llama `maps.SearchDailyAsync(dayOfWeek, ct)` sin el parámetro.
- `SeedData.cs`: 
  - Agrega 2 filas a `IndustriaCatalogo` ("Farmacias", "Estudios contables / jurídicos", ambas `CotizaAutomatico=false`) — ver §1.c.
  - Nuevo `SeedCampanasOutboundAsync` (idempotente, mismo patrón `if (await db.CampanasOutbound.AnyAsync()) return;`): genera 1 `CampanaOutbound` por cada uno de los ~13 rubros que hoy tiene entrada en `RunDayByType`/`RubrosByDay` (excluye `restaurant`/`eventos`, ya retirados del barrido — ver trazabilidad 2026-07-17), con `Dias` = el día que le corresponde hoy, `LimiteDiario = Ceiling(125 / cantidadDeRubrosDeEseDia)` (Martes: 3 rubros → 42 c/u; Miércoles: 5 → 25 c/u; Jueves: 5 → 25 c/u — mismo criterio de reparto que ya usa `GoogleMapsService.SearchDailyAsync` hoy), `TemplateWhatsApp = "olv_frio_v3"`, `Activa = true`, y una `CampanaOutboundIndustria` con el `ClaveRubro` correspondiente + `IndustriaCatalogoId` de la fila que mejor matchea (mapeo manual documentado en el propio código) + todas las `CampanaQuery` migradas 1:1 desde `QueriesByRubro[rubro]`.
- `DependencyInjection.cs`: sin cambios (no hay servicios/paquetes nuevos).

#### Web (`OlvidataCRM.Web`)

- **Controller nuevo:** `CampanasController` (`[Authorize(Policy="RequireSuperUsuario")]`) — `Index`/`GetData` (DataTable server-side), `Create` (GET/POST), `Edit` (GET/POST), `TogglePausa` (POST), `Delete` (POST, soft-delete), más 2 endpoints AJAX para queries (`AgregarQuery`/`EliminarQuery`, POST, devuelven JSON `{success, message}`). Se optó por un controller propio (no anidar en `BotController`) — consistente con el patrón ya establecido del proyecto (`IndustriasController` separado de `BotController` pese a estar relacionados).
- `BotController.Index`: agrega `CampanasResumen` al ViewModel (nombre + día corto de las campañas, para la card nueva de `Bot/Index`).
- **ViewModels:** los 6 definidos en Diseño §2, sin cambios respecto a lo ya aprobado.
- **Vistas:** `Views/Campanas/{Index,Create,Edit}.cshtml` + extensión de `Views/Bot/Index.cshtml` (card resumen), según wireframes de Diseño §1.
- **Sidebar:** sin cambios (las pantallas de Campañas no llevan entrada propia, se accede desde `Bot/Index`, según Diseño).

### 3. Modelo de permisos

Sin cambios — único rol del sistema (`RequireSuperUsuario`), ya vigente desde el ajuste de roles del 2026-07-21. `CampanasController` usa la misma policy que `BotController`/`IndustriasController`.

### 4. Migraciones EF requeridas

**Sí.** Una migración (`AddCampanasOutbound`) agrega 3 tablas (`CampanasOutbound`, `CampanaOutboundIndustrias`, `CampanaQueries`) + 2 filas nuevas al seed de `IndustriaCatalogo` (aplicadas por `SeedData`, no por la migración en sí). No modifica ninguna tabla existente. Se aplica primero contra `olvidatacrm_dev`.

### 5. Riesgos y supuestos

- **Riesgo aceptado y heredado del Análisis:** sin tope global de límite diario (decisión #1) — ver `1-analista-funcional.md` §5.
- **Riesgo de reconciliación catálogo↔rubro:** las 2 filas nuevas de `IndustriaCatalogo` ("Farmacias", "Estudios contables/jurídicos") son solo anclas de catálogo sin cotización automática — no resuelven el gap de pricing ya conocido (documentado desde la implementación original), solo permiten que esos 2 rubros tengan campaña de contacto frío igual que los demás.
- **Riesgo de regresión en `RubrosDisponibles`:** pasa de propiedad sincrónica a consulta async — el único consumidor (`BotController.Index`, búsqueda manual CU-11) debe actualizarse a `await`; revisar que no haya otro caller antes de mergear (grep obligatorio en Implementación).
- **Supuesto:** el reparto de `LimiteDiario` en el seed (125 ÷ rubros del día) es un valor de arranque razonable, no una decisión de negocio del cliente — queda 100% editable desde la pantalla de Campañas apenas esté disponible, no requiere aprobación previa.

### 6. Gate de aprobación para pasar a Implementación

**Cumplido — Presupuesto salteado a pedido explícito del cliente.** Arquitectura no agrega paquetes NuGet nuevos, no crea policies nuevas, reutiliza el patrón de controller/vista ya establecido en `IndustriasController`. Requiere 1 migración EF con 3 tablas nuevas + 2 filas de seed adicionales en `IndustriaCatalogo`, sin tocar tablas existentes. Pasa directo a Implementación.

## Historial de ajustes
- 2026-07-14: Arquitectura técnica cerrada. Definidas 4 entidades Domain (`Contacto`, `ContactoRespuesta`, `IndustriaCatalogo`, `GoogleMapsQueryUsada`) + 4 enums, 4 interfaces Application nuevas, mapa completo de reutilización de BotPublicitario (WhatsAppClient/GoogleMapsService portados sin cambio de lógica; BotFlowService/OutboundCampaignService migrados a BD; ExcelTrackerService/TemplateCreationService/CatalogService no se portan). 1 migración EF. Sin paquetes NuGet ni policies nuevas. Runbook de corte de producción definido como paso operativo.
- 2026-07-21: Arquitectura técnica de "campañas de contacto frío configurables" cerrada. Resueltas 2 ambigüedades técnicas que el Diseño dejó abiertas: (a) `ClaveRubro`/queries cuelgan de `CampanaOutboundIndustria` (no de `IndustriaCatalogo`) porque varios rubros operativos comparten una misma fila de precio; (b) el campo `TemplateWhatsApp` de la campaña gobierna solo el primer contacto frío, Referido/follow-up mantienen su template fijo (preserva comportamiento legacy). 3 entidades nuevas + 1 enum, 1 migración EF, controller nuevo (`CampanasController`), 2 filas nuevas de `IndustriaCatalogo` para cubrir Farmacia/Estudio en el seed de migración. Presupuesto salteado a pedido explícito del cliente — pasa directo a Implementación.
