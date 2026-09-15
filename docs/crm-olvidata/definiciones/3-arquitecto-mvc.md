# Memoria - Arquitecto MVC

## Proyecto: crm-olvidata — migración de BotPublicitario + evolución continua
## Última actualización: 2026-09-14

## Definiciones vigentes

### 0. Alcance funcional resumido

`OlvidataCRM` (`C:\Sistemas\olvidatasoft-crm`) es la migración completa de `BotPublicitario` más todo lo construido después: captación/calificación automática por WhatsApp, presupuesto automático, outbound diario multi-campaña/multi-zona-horaria, búsqueda por Google Maps, pantalla de Chats con multimedia, notificaciones de ventana de 24hs, y el módulo de Gestión comercial (Clientes/Upsell/NRR/Templates/A-B testing/pipeline visual). Único rol de sistema: `SuperUsuario` (desde 2026-07-21). Sin `Proyecto`/pipeline de hitos de cobro (vive en VirtualWallet, fuera de alcance por decisión explícita del cliente).

### 1. Domain (`OlvidataCRM.Domain`)

Todas las entidades heredan `SoftDestroyable`.

```csharp
public class Contacto : SoftDestroyable
{
    public string Telefono { get; set; }                  // único, ^\d{10,15}$ — cualquier país con código, sin "+"
    public string? NombreContacto { get; set; }
    public string? NombreNegocio { get; set; }
    public string? Email { get; set; }
    public string? Rubro { get; set; }
    public string? Zona { get; set; }
    public string? Direccion { get; set; }
    public double? Lat { get; set; }
    public double? Lng { get; set; }
    public CanalOrigen CanalOrigen { get; set; }
    public string? ReferidoPor { get; set; }
    public string? MotivoReferido { get; set; }
    public FaseConversacion FaseConversacion { get; set; } = FaseConversacion.Nuevo;
    public string? Categoria { get; set; }
    public int QuestionIndex { get; set; }
    public int? CantidadUsuarios { get; set; }
    public EstadoEmbudo EstadoEmbudo { get; set; } = EstadoEmbudo.Pendiente;
    public decimal? PresupuestoCotizadoUsd { get; set; }
    public DateTime? FechaPrimerEnvio { get; set; }
    public DateTime? FechaFollowUp { get; set; }
    public DateTime? FechaRespuesta { get; set; }
    public DateTime? FechaCompletado { get; set; }
    public DateTime FechaUltimaActividad { get; set; }
    public DateTime? FechaUltimaLecturaAgente { get; set; }   // última vez que un asesor abrió el chat
    public bool MarcadoNoLeidoManual { get; set; }             // override manual del cálculo automático de NoLeido
    public DateTime? FechaUltimaAlertaVentana { get; set; }    // evita re-notificar la misma ventana de 24hs
    public string? UltimoMensajeId { get; set; }
    public string? Notas { get; set; }

    public ICollection<ContactoRespuesta> Respuestas { get; set; } = new List<ContactoRespuesta>();
}

public class ContactoRespuesta : SoftDestroyable
{
    public int ContactoId { get; set; }
    public string Pregunta { get; set; } = string.Empty;
    public string Respuesta { get; set; } = string.Empty;
    public string? MediaId { get; set; }              // id de media de la Graph API de Meta (no vence)
    public string? MediaMimeType { get; set; }
    public string? VarianteExperimento { get; set; }  // "A" | "B" | null — solo si CampanaExperimento estaba activo al enviar
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

// Reemplaza queries_used.txt de GoogleMapsService
public class GoogleMapsQueryUsada : SoftDestroyable
{
    public string Rubro { get; set; } = string.Empty;
    public string Query { get; set; } = string.Empty;
}

public class CampanaOutbound : SoftDestroyable
{
    public string Nombre { get; set; } = string.Empty;
    public DiasSemana Dias { get; set; }                        // 7 días reales, no solo Mar/Mié/Jue
    public TimeSpan HoraEnvio { get; set; }
    public string? ZonaHoraria { get; set; }                    // Id de TimeZoneInfo de Windows; null = Argentina
    public int LimiteDiario { get; set; }
    public string TemplateWhatsApp { get; set; } = string.Empty; // valida contra TemplateWhatsApp.Activo && Aprobado
    public bool Activa { get; set; }
    public bool Completa { get; set; }              // true cuando TODAS sus industrias quedan SinResultadosNuevos
    public DateTime? FechaCompletada { get; set; }
    public ICollection<CampanaOutboundIndustria> Industrias { get; set; } = new List<CampanaOutboundIndustria>();
}

public class CampanaOutboundIndustria : SoftDestroyable
{
    public int CampanaOutboundId { get; set; }
    public CampanaOutbound CampanaOutbound { get; set; } = null!;
    public int RachaSinResultadosNuevos { get; set; }   // corridas seguidas sin prospectos nuevos
    public bool SinResultadosNuevos { get; set; }        // true al llegar al umbral (5) — deja de buscarse sola
    public int? IndustriaCatalogoId { get; set; }               // opcional — ver Riesgos, gap Farmacia/Estudio
    public IndustriaCatalogo? IndustriaCatalogo { get; set; }
    public string ClaveRubro { get; set; } = string.Empty;       // granular: "comercio", "farmacia", etc. — único entre campañas ACTIVAS
    public ICollection<CampanaQuery> Queries { get; set; } = new List<CampanaQuery>();
}

public class CampanaQuery : SoftDestroyable
{
    public int CampanaOutboundIndustriaId { get; set; }
    public CampanaOutboundIndustria CampanaOutboundIndustria { get; set; } = null!;
    public string Query { get; set; } = string.Empty;
    public string Zona { get; set; } = string.Empty;
}

public class Cliente : SoftDestroyable
{
    public int ContactoId { get; set; }
    public Contacto Contacto { get; set; } = null!;
    public PlanSistema Plan { get; set; }
    public decimal TicketAnualUsd { get; set; }
    public DateTime FechaAlta { get; set; }
    public DateTime FechaProximaRenovacion { get; set; }
    public bool Activo { get; set; } = true;
    public string? Notas { get; set; }
    public ICollection<Upsell> Upsells { get; set; } = new List<Upsell>();
}

public class Upsell : SoftDestroyable
{
    public int ClienteId { get; set; }
    public Cliente Cliente { get; set; } = null!;
    public string Tipo { get; set; } = string.Empty;   // texto libre corto
    public decimal MontoUsd { get; set; }
    public DateTime Fecha { get; set; }
    public string? Notas { get; set; }
}

public class TemplateWhatsApp : SoftDestroyable
{
    public string Nombre { get; set; } = string.Empty;      // debe coincidir con el nombre aprobado en Meta si Aprobado
    public string Texto { get; set; } = string.Empty;       // copia local de referencia
    public string? Rubro { get; set; }                       // null = genérico
    public string? Pais { get; set; }                         // null = todos los países
    public EstadoAprobacionMeta EstadoAprobacionMeta { get; set; } = EstadoAprobacionMeta.Borrador;
    public bool Activo { get; set; } = true;
}

public class CampanaExperimento : SoftDestroyable
{
    public int CampanaOutboundId { get; set; }
    public CampanaOutbound CampanaOutbound { get; set; } = null!;
    public int TemplateAId { get; set; }
    public TemplateWhatsApp TemplateA { get; set; } = null!;
    public int TemplateBId { get; set; }
    public TemplateWhatsApp TemplateB { get; set; } = null!;
    public int PorcentajeB { get; set; }   // 1-99, el resto va a A
    public bool Activo { get; set; } = true;
}

public class SugerenciaSeguimiento : SoftDestroyable
{
    public EstadoEmbudo EstadoEmbudo { get; set; }
    public int? DiasMinimo { get; set; }
    public int? DiasMaximo { get; set; }   // null = sin techo
    public string? Rubro { get; set; }      // null = genérico
    public string Texto { get; set; } = string.Empty;
}
```

Enums (`Domain/Enums/`, persistidos con `HasConversion<int>()`):

```csharp
public enum CanalOrigen { AdsPagos = 1, OutboundFrio = 2, Referido = 3, Manual = 4 }

public enum FaseConversacion { Nuevo = 1, AwaitingCategory = 2, AwaitingIndustry = 3, AskingQuestions = 4, Completed = 5 }

public enum EstadoEmbudo
{
    Pendiente = 1, MensajeEnviado = 2, FollowUpEnviado = 3, Respondido = 4,
    PresupuestoEnviado = 5, Cerrado = 9, Frio = 10, Descartado = 11, DerivadoManual = 12
}
// Los valores 6-8 (DemoSolicitada/DemoRealizada/PropuestaEnviada) nunca se implementaron y fueron
// eliminados formalmente de las definiciones el 2026-08-14 por decisión del cliente — hoy la venta
// se maneja directo por WhatsApp vía Chats sin pasar por estados intermedios. Los valores numéricos
// 6-8 quedan deliberadamente sin reasignar, para no romper datos históricos si algún registro viejo
// los tuviera persistidos.

public enum PlanSistema { Starter = 1, Pro = 2, Premium = 3, Scale = 4 }

[Flags]
public enum DiasSemana { Lunes = 8, Martes = 1, Miercoles = 2, Jueves = 4, Viernes = 16, Sabado = 32, Domingo = 64 }
// Sábado/Domingo existen en el enum pero por política de negocio (sin outreach B2B en fin de
// semana) ninguna campaña activa los usa hoy.

public enum EstadoAprobacionMeta { Borrador = 1, PendienteRevision = 2, Aprobado = 3, Rechazado = 4 }
```

### 2. Application (`OlvidataCRM.Application`)

Interfaces (`Interfaces/`):

```csharp
public interface IWhatsAppClient
{
    // SendTextAsync, SendTemplateAsync, SendListAsync
    Task<MediaDownloadResult> DownloadMediaAsync(string mediaId); // 2 pasos Graph API: metadata (URL corta) → binario, no cacheable
}
public interface IGoogleMapsService
{
    Task<IReadOnlyList<string>> RubrosDisponiblesAsync();  // async — antes propiedad sincrónica sobre diccionario estático
    Task<int> SearchDailyAsync(DayOfWeek day, CancellationToken ct = default); // sin targetTotal — cada campaña define su LimiteDiario
    Task<int> SearchByRubroAsync(string claveRubro, int maxResults);
}
public interface IBotFlowService { Task HandleIncomingAsync(IncomingMessageDto msg, string? contactName); }
public interface IOutboundCampaignService
{
    Task<int> SendDailyBatchAsync(DayOfWeek? diaOverride = null, int? soloCampanaId = null, CancellationToken ct = default);
    Task<int> ProcessFollowUpsAsync(DayOfWeek? diaOverride = null, int? soloCampanaId = null, CancellationToken ct = default);
    Task<int> MarkColdAsync(CancellationToken ct = default);
    Task<OutboundStatsDto> GetStatsAsync();
}
```

DTOs (`DTOs/`): `IncomingMessageDto` (payload normalizado del webhook; `MediaId`/`MediaMimeType`/`MediaFileName` poblados solo si el mensaje es audio/imagen/video/documento/sticker), `OutboundStatsDto`, `ContactoListItemDto`, `MediaDownloadResult(byte[] Bytes, string MimeType)`, `NegocioStatsDto` (ClientesActivos, TicketPromedioReal, Nrr nullable, AvanceMeta), `CampanaStatsDto` (Campana/Rubro/Pais/Enviados/TasaRespuesta/TasaAvancePresupuesto/TasaCierre).

Settings (`Settings/`, mismo patrón que `SmtpSettings`):
```csharp
public class WhatsAppSettings { public string AccessToken; PhoneNumberId; BusinessAccountId; BusinessId; ApiVersion = "v21.0"; }
public class GoogleMapsSettings { public string ApiKey; }
public class BotSettings { public string AdminNotifyPhone; public string VerifyToken; }
```
Secciones de configuración (`appsettings.json`): `Olvidata_WhatsApp`, `Olvidata_GoogleMaps`, `Olvidata_Bot`.

**Sin capas de servicio por-entidad que no aporten:** `IndustriaCatalogo`, `Cliente`/`Upsell`/`TemplateWhatsApp`/`SugerenciaSeguimiento` usan `IRepository<T>`/`AppDbContext` directo desde su controller (catálogos simples, sin lógica propia). Excepción real: NRR y métricas de campaña son consultas agregadas no triviales — viven como métodos privados en `NegocioController`/`CampanasController` respectivamente, sin crear una capa de servicio nueva solo para esto. El cálculo de presupuesto vive dentro de `BotFlowService` (lógica de negocio del bot, no reutilizable aparte). `TemplatesDisponibles` ya no es una lista fija en código — se resuelve contra la tabla `TemplateWhatsApp`.

### 3. Infrastructure (`OlvidataCRM.Infrastructure`)

- **`AppDbContext`**: `DbSet<Contacto>`, `DbSet<ContactoRespuesta>`, `DbSet<IndustriaCatalogo>`, `DbSet<GoogleMapsQueryUsada>`, `DbSet<CampanaOutbound>`, `DbSet<CampanaOutboundIndustria>`, `DbSet<CampanaQuery>`, `DbSet<Cliente>`, `DbSet<Upsell>`, `DbSet<TemplateWhatsApp>`, `DbSet<CampanaExperimento>`, `DbSet<SugerenciaSeguimiento>`. Índice único en `Contacto.Telefono`. Cascadas: `ContactoRespuesta`→`Contacto`, `CampanaOutboundIndustria`→`CampanaOutbound`, `CampanaQuery`→`CampanaOutboundIndustria`, `Upsell`→`Cliente` (`OnDelete(Cascade)`); `CampanaOutboundIndustria`→`IndustriaCatalogo` y `CampanaExperimento`→`TemplateWhatsApp` (A/B) con `OnDelete(Restrict)` (evita múltiples rutas de cascada en MySQL / no se borra un template referenciado). `Cliente.ContactoId` sin índice único (un contacto podría tener más de un `Cliente` histórico). `Dias` con `HasConversion<int>()`. Precisiones `decimal` con `HasPrecision(18,2)` donde aplica.
- **`WhatsAppClient`** (`Services/`): porта de `BotPublicitario` sin cambios de lógica salvo config vía `IOptions<WhatsAppSettings>`. `DownloadMediaAsync` implementa los 2 pasos de la Graph API sobre el mismo `HttpClient` autenticado.
- **`GoogleMapsService`**: sin diccionarios estáticos `RubrosByDay`/`QueriesByRubro` — resuelve contra `CampanaOutboundIndustria`/`CampanaQuery` (activas o no, para permitir búsqueda manual fuera de campaña activa). Rotación contra `GoogleMapsQueryUsada` sin cambios (ya era tabla). `SearchDailyAsync` reparte `maxResults = Ceiling(campana.LimiteDiario / cantidadIndustriasDeEsaCampana)` por campaña activa del día. **Paginación (2026-08-16):** `SearchAsync` pide hasta 3 páginas de `textsearch` vía `next_page_token` (60 resultados en vez de 20 por query, con el delay de 2s que exige Google antes de que el token sea válido). **Detección de agotamiento:** al final de cada `SearchByRubroAsync` se cuenta cuántos prospectos son genuinamente nuevos (no ya un `Contacto`, mismo criterio de dedupe por teléfono); si 0, sube `CampanaOutboundIndustria.RachaSinResultadosNuevos`, si ≥1 la resetea. Al llegar a 5 (`UmbralRachaSinResultados`) marca `SinResultadosNuevos=true` y `SearchDailyAsync` deja de volver a buscar esa industria en el barrido automático (no afecta la búsqueda manual, CU-11). Cuando todas las industrias de una campaña quedan así, `CampanaOutbound.Completa` se marca automáticamente (sin tocar `Activa`) y dispara notificación in-app a `SuperUsuario` — requirió agregar `INotificationService`/`UserManager<ApplicationUser>` al constructor de `GoogleMapsService`.
- **`BotFlowService`**: máquina de estados sobre `Contacto`/`ContactoRespuesta` vía `AppDbContext` (no `ConversationStore` JSON). Mapeo rubro→industria contra `IndustriaCatalogo`. Protección de loop post-cierre: cuenta filas `"Mensaje adicional (post-cierre)"` solo si `Id > ultimoMensajeManualId` (Id de la última fila `"[Mensaje manual del asesor]"`) — evita descartar una respuesta genuina a una intervención humana.
- **`OutboundCampaignService`**: `SendDailyBatchAsync`/`ProcessFollowUpsAsync` consultan `CampanaOutbound` activas cuyo `Dias` incluye el día actual, agrupan por `ClaveRubro` de sus `CampanaOutboundIndustria`, límite por campaña (`campana.LimiteDiario`, no global). Selección de template: `Referido → "olv_referido_v2"` fijo / `follow-up → "olv_nurturing_v2"` fijo / envío frío → `campana.TemplateWhatsApp`, salvo que la campaña tenga un `CampanaExperimento` activo — en ese caso un split determinístico sembrado por `contacto.Id` (no `Random` global, para no cambiar de variante en reintentos) decide `TemplateA`/`TemplateB` según `PorcentajeB` y setea `ContactoRespuesta.VarianteExperimento`. `MarkColdAsync` sin gating por rubro/día. Etiqueta `"[Mensaje de contacto frío]"` como constante interna (`EtiquetaMensajeFrio`).
- **`OutboundSchedulerService`** (`HostedServices/`) — **reescrito de fondo**: tick cada 5 minutos, compara `HoraEnvio` de cada `CampanaOutbound` contra la hora **local** de su `ZonaHoraria` (`TimeZoneInfo.ConvertTimeFromUtc`, fallback a Argentina si es null/inválida) — ya no un disparador único fijo (Mar/Mié/Jue 09:30 ART para todas). Motivo: la expansión a 8 países (Uruguay, Chile, Paraguay, Bolivia, Perú, Ecuador, Colombia, Venezuela) hacía llegar mensajes 1-2hs antes de lo configurado fuera de Argentina. Toggle standby: `Bot/Index` (Identity), estado en memoria (no persistido — un recycle del app pool lo resetea al default).
- **`VentanaExpiracionSchedulerService`** (nuevo `HostedService`, `_sp.CreateScope()`): tick cada 15 minutos, notifica in-app a `SuperUsuario` cuando un contacto `DerivadoManual` está a ≤3hs de perder su ventana de 24hs de WhatsApp, usa `Contacto.FechaUltimaAlertaVentana` para no reavisar la misma ventana. Ventana calculada desde el último mensaje **entrante** real (excluye las etiquetas `"[Mensaje manual del asesor]"`/`"[Mensaje de contacto frío]"`/`"[Presupuesto PDF enviado]"`) + 24hs.
- **`ManualPipelineQueue`** (singleton, señal vía `SemaphoreSlim`) + **`ManualPipelineRunnerService`** (`HostedService`, propio scope de DI): el botón "Ejecutar ahora" de `Bot/Index` encola en vez de bloquear el request HTTP; la corrida real ocurre en el hosted service. Estado en memoria, no persistido (mismo riesgo que el standby).
- **Deduplicación de webhooks por reintentos de Meta**: `HashSet` en memoria por `message_id`, limitación conocida y aceptada (no sobrevive restart, no escala a múltiples instancias) — mejora futura (índice único sobre `UltimoMensajeId` procesado) no implementada preventivamente (YAGNI).
- **`SeedData.cs`**: seed idempotente de `IndustriaCatalogo` (13 industrias + "Farmacias"/"Estudios contables o jurídicos" con `CotizaAutomatico=false`, ancla de catálogo sin pricing propio), de `CampanaOutbound`/`CampanaOutboundIndustria`/`CampanaQuery` (una campaña por rubro migrado desde el barrido legacy), y una fila `TemplateWhatsApp` para `"olv_frio_v3"` (`Aprobado`) para que las campañas activas no queden sin template válido.
- **`DependencyInjection.cs`**: `Configure<WhatsAppSettings/GoogleMapsSettings/BotSettings>`, `AddHttpClient<IWhatsAppClient, WhatsAppClient>()`, `AddHttpClient<IGoogleMapsService, GoogleMapsService>()`, `AddScoped<IBotFlowService, BotFlowService>()`, `AddScoped<IOutboundCampaignService, OutboundCampaignService>()`, `AddHostedService<OutboundSchedulerService>()`, `AddHostedService<VentanaExpiracionSchedulerService>()`, `AddHostedService<ManualPipelineRunnerService>()`, singleton `ManualPipelineQueue`. Sin paquetes NuGet nuevos en todo el ciclo (`HttpClient` + `System.Text.Json` del framework).
- **Literal cross-capa duplicado (tech-debt conocido):** las etiquetas de evento (`"[Mensaje manual del asesor]"`, etc.) viven como constantes reales en `ChatsController`/`OutboundCampaignService` (Web/Infrastructure) pero se necesitan también en `VentanaExpiracionSchedulerService` (Infrastructure no puede referenciar una constante de Web) — quedan duplicadas como strings crudos con comentario cruzado. Mejora pendiente: extraer a una clase de constantes en `Application`.

### 4. Web (`OlvidataCRM.Web`)

- **Controllers** (todos `[Authorize(Policy = "RequireSuperUsuario")]` — único rol del sistema desde 2026-07-21): `ContactosController` (CRUD, filtros persistidos en `Session`, acción `Pipeline` con `PipelineViewModel`/`ConversionEtapaViewModel` agrupando por `EstadoEmbudo`), `IndustriasController`, `BotController` (`Index`, `EjecutarAhora` — sincrónico, solo encola en `ManualPipelineQueue`), `CampanasController` (`Index`/`GetData`, `Create`/`Edit`, `TogglePausa`, `Delete`, `AgregarQuery`/`EliminarQuery` AJAX, `Dashboard` con `CampanaStatsDto`, `ConfigurarExperimento`, `ReabrirBusqueda` — resetea `Completa`/`SinResultadosNuevos`/`RachaSinResultadosNuevos` tras cargar zonas/queries nuevas, 2026-08-16), `ChatsController` (`Index`/`ListaParcial`, `Detail`/`HiloParcial`, `EnviarMensaje`, `EnviarPresupuestoPdf`, `MarcarNoLeido`, `Media` — proxy de descarga bajo demanda, no público, `SugerirMensaje` AJAX resolviendo `SugerenciaSeguimiento` por `EstadoEmbudo`+`Rubro`+días desde `FechaRespuesta`), `ClientesController` (`Index`/`GetData`, `Details`, `ConvertirDesdeContacto` POST desde `Contactos/Details`/`Chats/Detail`, `AgregarUpsell` AJAX inline), `NegocioController` (`Dashboard` con `NegocioStatsDto` + próximas renovaciones), `TemplatesController` (CRUD estándar).
- **Webhook de Meta**: Minimal API en `Program.cs` (`GET/POST /webhook/whatsapp`, verificación `hub.verify_token`). Sin `[Authorize]` ni rate limiting general (Meta controla su propio ritmo). Delega a `IBotFlowService` tras ACK 200 (fire-and-forget, evita timeout/reintentos de Meta).
- **Vistas**: `Contactos/{Index,Details,Create,Edit,Pipeline}`, `Industrias/{Index,Create,Edit}`, `Bot/Index`, `Campanas/{Index,Create,Edit,Dashboard}`, `Chats/{Index,Detail,_ChatThread,_ChatListItems}`, `Clientes/{Index,Details}`, `Negocio/Dashboard`, `Templates/{Index,Create,Edit}` — Design System (`ov-card`, `ov-badge`, DataTables server-side).
- **Sidebar (`_Layout.cshtml`)**: secciones "Comercial" (Contactos), "Chats", "Negocio" (Clientes, Dashboard de negocio), y "Sistema" (Industrias, Bot/Outbound, Campañas, Templates) — todo visible solo para `SuperUsuario`.

### 5. Modelo de permisos

Único rol de sistema desde el 2026-07-21: `SuperUsuario`. Todos los controllers de esta iteración usan `[Authorize(Policy = "RequireSuperUsuario")]` sin matices — las policies históricas `RequireVendedor`/`RequireAdministracion` no existen en el código actual (confirmado por grep, cero referencias). Excepción única: el webhook de Meta, autenticado solo con `hub.verify_token` (sin cookie de sesión posible). `Chats/Media` está protegido por la policy del controller igual que el resto — no es un endpoint público pese a servir binarios.

### 6. Migraciones EF aplicadas (histórico acumulado, todas aditivas salvo la indicada)

`AddContactosYCatalogoIndustrias` (4 tablas base) → `AddCampanasOutbound` (3 tablas + 2 filas seed `IndustriaCatalogo`) → `AddZonaHorariaCampana` → `AddMediaFieldsToContactoRespuesta` → `AddEmailToContacto` → `AddFechaUltimaAlertaVentana` → `AddMarcadoNoLeidoManual` → `RemoveAuditLog` (**única no aditiva** — elimina la tabla `AuditLogs` completa, 2026-07-28, decisión explícita del cliente) → `AddGestionComercial` (5 tablas: `Clientes`, `Upsells`, `TemplatesWhatsApp`, `CampanasExperimento`, `SugerenciasSeguimiento` + columna `ContactoRespuestas.VarianteExperimento`) → `AddCampanaBusquedaCompleta` (4 columnas aditivas: `CampanaOutbound.Completa`/`FechaCompletada`, `CampanaOutboundIndustria.RachaSinResultadosNuevos`/`SinResultadosNuevos`) → `AddModuloCatalogo` (2 tablas: `ModulosCatalogo`, `ModuloCatalogoIndustrias` — matriz MVP/FULL) → `AddContactoAdOrigen` (3 columnas: `AdOrigenTag`/`AdReferralSourceId`/`AdReferralHeadline`, origen de anuncios click-to-WhatsApp) → `AddBusquedaMapsPausada` (1 columna: pausa persistente de la API de Maps) → `AddTarifasYPresupuestoMensajeria` (tabla `TarifasWhatsApp` + `ConfiguracionOutbound.PresupuestoMensualArs`) → `AddCacheYConsumoMaps` (2 tablas: `GoogleMapsPlacesVistos` con indice unico por `PlaceId`, `ConsumosMapsDiarios`) → `AddCotizacionUsdArs` (1 columna: cotizacion para consolidar el gasto de Google dentro del presupuesto en ARS) → `AddPausaBotPorContacto` (3 columnas: `Contacto.BotPausado`/`FechaBotPausado` + `ConfiguracionOutbound.OutboundPausado`) → `AddConversacionIa` (2 tablas: `ContactoMensajesIA` con indice por `(ContactoId, Id)` y `TarifasLlm` con indice unico por `Modelo`; + 4 columnas en `ConfiguracionOutbound`: `ConversacionIaHabilitada`, `ConversacionIaPausada`, `ConversacionIaModoSombra` con **default TRUE**, `FactorHolguraTechos` con default 1,30). Todas aditivas. Todas aplicadas primero en `olvidatacrm_dev`.

**Precision de los decimales de IA**: `ContactoMensajeIA.CostoUsd` va en `decimal(18,8)` y las tarifas por millon de tokens en `(18,4)`. NO es un detalle: con el `(18,2)` que genera el scaffold por defecto, una llamada de USD 0,036 se guardaba como 0,04 o 0,00 y el gasto del mes quedaba inservible — que es justo la metrica que motiva toda la seccion de costos.

### 6.1 Control de costos del bot (2026-09-03/04)

El bot tiene **3** costos externos reales (el tercero desde 2026-09-13) y se miden por separado porque facturan distinto:

- **Mensajeria de Meta (ARS)** — desde 2025-07-01 se cobra por PLANTILLA ENTREGADA, no por conversacion. Marketing (frio + follow-up) se cobra SIEMPRE y **no tiene descuento por volumen**. Tarifas por pais del DESTINATARIO en `TarifaWhatsApp` (Argentina 89,56 / Chile 128,84 / Uruguay 107,24 "Rest of LatAm" / fallback 87,53), sembradas por fila desde la rate card oficial. El pais se resuelve por el **prefijo de `Contacto.Telefono`**, no por `CampanaOutbound.Region` (texto libre, y Meta factura por el numero al que entrega).
- **Google Places API (USD)** — el Text Search es GRATIS; el 97% del gasto es el Place Details de cada lugar encontrado (Details + Contact Data ≈ USD 0,0171). `ConsumoMapsDiario` cuenta requests facturables por dia (incluidas las paginas extra de `next_page_token`, que se facturan aparte) y los Details EVITADOS por cache.
- **Cache `GoogleMapsPlaceVisto`** (indice unico por `PlaceId`): el `place_id` viene gratis en el Text Search, el telefono solo con el Details pago. Antes se pagaba el Details de TODOS los lugares y recien despues se descartaba por telefono duplicado — sobre la factura real de agosto 2026, 72,5% de las llamadas no produjeron ningun contacto nuevo. Se guarda tambien el caso "sin telefono". El dedupe es GLOBAL (el place_id identifica al negocio, no a la busqueda). **OJO MH-001**: el chequeo es por `AnyAsync(p => p.PlaceId == id)` uno por uno, NO `Where(listaLocal.Contains(...))` — una lista local de string no traduce a SQL contra el provider MySQL.
- **Tope unico en ARS** (`ConfiguracionOutbound.PresupuestoMensualArs`) sobre el COSTO TOTAL: mensajeria + Maps convertido con `CotizacionUsdArs` (cargada a mano a proposito — en Argentina no hay una unica cotizacion "correcta"). Sin cotizacion cargada el tope cubre solo la mensajeria y la pantalla lo avisa. El tope diario efectivo es `min(CupoDiario, presupuestoRestante / diasRestantes / costoPromedioPorMensaje)`.
- **Conversacion con IA / API de Anthropic (USD)** — tercera linea desde 2026-09-13. `TarifaLlm` guarda **4 tarifas por modelo** (entrada, salida, lectura de cache, escritura de cache): la lectura vale ~10% de la entrada y la escritura ~125%, asi que sumar los 3 tipos de token de entrada y cobrarlos a la misma tarifa —como hace hoy el proyecto `Olvidata Agentes Multi-rubro`— sobrecobra lecturas y subcobra escrituras. `ContactoMensajeIA.CostoUsd` es un **snapshot** calculado al momento, NO se recalcula contra la tarifa vigente: a diferencia de la mensajeria, editar una tarifa no debe cambiar retroactivamente el gasto de meses cerrados.
- **El volumen diario lo fija el PRECIO, no una meta de cantidad** (2026-09-03): `MetaDiaria` quedo solo como respaldo para cuando no hay presupuesto. `RebalancearMatrizAsync` escala contra la meta derivada del presupuesto.
- **El tope unico se REPARTE entre las 3 herramientas, y el reparto se DERIVA** (2026-09-13, pedido explicito del cliente). No se configuran porcentajes: las 3 estan en cadena (Places compra el prospecto, Meta le habla, el LLM lo conversa si contesta), asi que se calcula el costo unitario de trabajar un prospecto de punta a punta —`CostoMapsPorProspecto + CostoPromedioMensajeria + RatioRespuesta × CostoIaPorMensaje`— y el volumen diario sale de dividir el restante por ese costo. Es la MISMA formula de `CalcularVolumenDiario` con el costo unitario ampliado de una punta a tres. Los 4 factores se **miden** en produccion, con semillas documentadas mientras no haya datos (Maps USD 0,0549/prospecto de la factura real de agosto pre-dedupe; ratio de respuesta 0,101 medido ago+sep; IA USD 0,036/mensaje). **Cada termino vale 0 cuando su herramienta esta apagada**, asi el reparto se ajusta solo a lo que este prendido.
- **Techos por herramienta, tambien derivados**: `TechoPct_i = SharePct_i × FactorHolguraTechos`, con el MISMO factor para las 3 (eso es lo que los hace equitativos). Suman mas de 100% a proposito: si sumaran 100%, una herramienta que gasta menos de su parte inmovilizaria plata que ninguna otra podria usar. El limite real sigue siendo el tope unico; el techo solo actua cuando una linea se desmadra. **Caso borde resuelto**: una herramienta sin consumo en el mes daria share 0 y techo 0, y quedaria trabada justo al reactivarla — el share usa las semillas cuando no hay datos propios, nunca 0.
- **Orden de sacrificio cuando se agota el tope unico** (confirmado por el cliente): Places → LLM → Meta. Places tiene stock para ~1,4 meses; con el LLM apagado el arbol sigue contestando; Meta es la unica que ABRE conversaciones. Es una decision de negocio, revisable si la fase 5 mide que el LLM levanta la conversion.
- **5 cortes de gasto de la IA**, de mas fino a mas grueso: 4 iteraciones de tool use por mensaje → 10 turnos y USD 0,50 por contacto → USD 2 por dia calendario argentino → techo derivado de la linea de IA → tope unico. Todos se evaluan ANTES de armar el request, y ninguno deja al prospecto sin respuesta: todos caen al arbol.

### 6.2 Conversacion agentica con LLM (2026-09-13/14)

Reemplaza los nodos de menu y el cuestionario fijo del arbol; NO reemplaza las guardas globales. Plan
completo en `plan-llm-conversacional-bot.md`, evidencia en `analisis-historial-conversaciones.md`.

- **Piezas**: `IConversacionIaService`/`ConversacionIaService` (unico punto que habla con la API),
  `ContactoMensajeIA` (transcript + telemetria), `TarifaLlm`, `IaSettings` (seccion `Anthropic`), y 3
  flags en `ConfiguracionOutbound`. SDK oficial **`Anthropic` 12.47.0** — la misma version que ya corre
  en `Olvidata Agentes Multi-rubro`, de donde se reutiliza el patron de llamada y el de la API key
  (user-secrets en desarrollo, `Anthropic__ApiKey` en produccion; **nunca** en appsettings versionado).
  La key debe estar scoped a un **workspace**: una de alcance Organizacion exige el header
  `anthropic-workspace-id` en cada request.
- **Por que `ContactoMensajeIA` y no `ContactoRespuestas`**: esa tabla es el hilo humano de /Chats y la
  fuente de verdad de la ventana de 24hs y del no-leido (11 queries dependen de sus etiquetas).
  Meterle bloques `tool_use`/`tool_result` la ensuciaria y arriesgaria la desincronizacion de etiquetas
  que ya paso 2 veces. La IA escribe en el hilo humano solo su respuesta final (`[Respuesta IA]`) y sus
  notas derivadas (`[Nota IA]`, `[Corte IA]`, `[No es prospecto]`) — **todas SALIENTES**: si contaran
  como entrantes marcarian el chat no leido y correrian la ventana de 24hs sin que nadie escriba.
- **9 herramientas**, con enums CERRADOS generados desde `RubroHelpers` (nunca una copia a mano del
  vocabulario — leccion de CRM-007 y CRM-016) y **validados ademas en codigo**, porque no se confia en
  que el modelo respete el schema: `set_categoria`, `set_rubro`, `consultar_modulos_del_rubro`,
  `guardar_datos_contacto`, `registrar_dolor`, `escalar_a_humano`, `dar_de_baja`,
  `descartar_no_es_prospecto`, `finalizar_conversacion`.
- **No existe herramienta para cotizar**. Es una garantia ESTRUCTURAL, no una instruccion de prompt:
  sin funcion que llamar, el modelo no puede inventar un precio por mas que le insistan.
- **Las acciones de negocio las ejecuta `BotFlowService`**, no el servicio de IA: este devuelve la
  accion y aquel reutiliza `ProcesarBajaAsync`, `SendBriefToAdminAsync` y `NotifyAdminsInAppAsync`, que
  ya tienen encima los fixes de incidentes reales.
- **El system prompt se GENERA y va en 2 bloques**: prefijo estable (reglas, rubros con descripcion,
  ejemplos) con `CacheControl`, y contexto del contacto despues, sin cachear. Con un bloque unico que
  incluia los datos del contacto la cache no cruzaba entre contactos — medido: escribia 5.091 tokens en
  cada contacto nuevo y leia 0. Partido, el prefijo se escribe una vez y se lee al 10% para todos los
  siguientes: de USD 0,044 a USD 0,016 la conversacion completa.
- **El arbol NO se borra**: es el fallback de timeout, 429, `refusal`, presupuesto agotado, flag apagada
  y bug no previsto. `FaseConversacion.ConversandoConIa` existe para que ese fallback retome donde
  estaba en vez de volver a presentarse.
- **`DisponibilidadAsync` devuelve el MOTIVO**, no un bool (`SinApiKey`, `Deshabilitada`, `Pausada`,
  `PresupuestoMensualAgotado`, `TechoDeIaAgotado`, `TopeDiarioAgotado`, `ErrorAlEvaluar` + detalle), y
  se registra una vez por contacto: el diseño manda caer al arbol en silencio, lo que es bueno para el
  prospecto y pesimo para diagnosticar — sin el motivo, una IA mal configurada se ve identica a una IA
  sin trafico.
- **Modo sombra sin efectos**: corre y se mide, pero las herramientas NO escriben en el CRM. Si
  escribieran, la sombra alteraria `Contacto.Rubro`, que el arbol LEE para elegir su camino — y dejaria
  de ser una comparacion valida entre los dos.
- **Pausa del bot POR CONTACTO** (`Contacto.BotPausado`, 48hs): se activa sola en los 3 puntos de
  intervencion manual y se evalua en el webhook, no por un scheduler — el unico momento en que importa
  es cuando el contacto vuelve a escribir.

### 7. Riesgos y supuestos vigentes

- **Deduplicación de webhooks no persistente** (`HashSet` en memoria) — aceptado, ver Infrastructure §3.
- **Concurrencia en alta de `Contacto`**: dos flujos pueden intentar crear el mismo teléfono a la vez (webhook vs. outbound). El índice único de `Telefono` actúa como red de seguridad — el flujo que llega segundo captura la excepción de duplicado y hace `UPDATE` en vez de `INSERT`.
- **Retención de media no garantizada**: `Chats/Media` puede devolver 404 en un adjunto viejo si Meta ya lo purgó — caso esperado, no una excepción sin manejar. Captura de multimedia no es retroactiva (solo mensajes recibidos después del deploy del 2026-08-13 tienen `MediaId`).
- **Literal cross-capa duplicado** (etiquetas de evento) — ver Infrastructure §3. Centralizado en `MensajeriaHelpers`, pero cada etiqueta nueva sigue exigiendo propagacion manual a las 11 queries que las enumeran (ya paso 3 veces).
- **`StartsWith`/`EndsWith` no traducen a SQL contra este proveedor de MySQL** (CRM-019): EF emite un `COLLATE utf8mb4_bin` sin type mapping. Misma familia que MH-001. Usar `EF.Functions.Like`.
- **Estado en memoria no persistido**: `ManualPipelineQueue` se resetea en cada recycle del app pool. El standby del scheduler **ya no**: desde 2026-09-13 se persiste en `ConfiguracionOutbound.OutboundPausado` y se lee en cada tick (ver CRM-018 del catalogo de QA — un flag que representa una decision de negocio no puede vivir solo en un `static`, porque un deploy reanudaba el envio solo).
- **Split A/B sembrado por contacto**: obligatorio para que un reintento del pipeline no cambie de variante a un contacto ya asignado.
- **NRR calculado en memoria (C#), no en SQL**: volumen bajo de `Cliente` (decenas, no miles) — revisar si la cartera crece mucho. Sin período anterior con datos, `NRR = null` → UI muestra "Datos insuficientes", nunca un número inventado.
- **Campo `Pais` de campaña es inferido por texto** (`Region`/`ZonaHoraria`), no un campo estructurado — suficiente para 8 países bien diferenciados en el texto; si la cantidad crece mucho valdría un campo `Pais` real en `CampanaOutbound`.
- **Gap de pricing conocido**: "Farmacias" y "Estudios contables/jurídicos" no tienen `PrecioBaseUsd`/cotización automática — quedan siempre `DerivadoManual`, comportamiento heredado y aceptado, no una regresión.

### 7.1 Arquitectura del sprint "corrección de bugs/gaps de auditoría + 3 mejoras" (2026-08-27)

**Hallazgo principal: 0 migraciones EF nuevas.** Los 17 items (7 bugs + 7 gaps + 3 mejoras) son correcciones de lógica/queries/exposición de campos que **ya existen** en el esquema — `Contacto.ReferidoPor`/`MotivoReferido`/`PresupuestoCotizadoUsd` y `Cliente.PrimerAnioGratis` ya son columnas reales (sembradas en migraciones previas), solo faltaba exponerlas en ViewModels/Views. Ninguna migración pendiente para este sprint.

Mapa por capa:

| Item | Domain | Application | Infrastructure | Web |
|---|---|---|---|---|
| B1 (truncado) | — | helper `Truncar` (o mover a Application si no existe ya) | `OutboundCampaignService` (8 call sites + catch) | — |
| B2 (rebalanceo por día) | — | — | `OutboundCampaignService.RebalancearMatrizAsync` | — |
| B3 (polling no pisa lectura) | — | — | `MensajesProgramadosSchedulerService` | `ChatsController.HiloParcial` + JS de `Chats/Detail.cshtml` |
| B4 (etiquetas de evento) | — | — | — | `ChatsController.EtiquetasDeEvento` |
| B5 (bloquear rename) | — | — | — | `TemplatesController.Edit` |
| B6 (fórmula única) | — | nuevo método compartido | `OutboundCampaignService` (fuente) | `ContactosController`, `CampanasController` (consumidores) |
| B7 (canal Referido) | — | ViewModels | — | `ContactosController` Create/Edit + vistas |
| G1 (templates dinámicos) | — | — | `OutboundCampaignService.BuildComponents` | — |
| G2 (shuffle + `UltimaCorridaUtc` en manual) | — | — | `OutboundCampaignService`/`OutboundSchedulerService` | `BotController.EjecutarAhora` |
| G3 (`PrimerAnioGratis` en alta) | — | `ConvertirClienteViewModel` | — | `ClientesController.ConvertirDesdeContacto` + vista |
| G4 (`PresupuestoCotizadoUsd` editable) | — | ViewModels | — | `ContactosController` Create/Edit + vistas |
| G5 (AJAX → JSON) | — | — | — | `ChatsController` (2 acciones) + JS de `Chats/Index.cshtml` |
| G6 (`ExecuteUpdateAsync`) | — | — | — | `ChatsController.MarcarTodosLeidos` |
| G7 (aviso + conteo huérfanos) | — | — | — | `IndustriasController.Delete`, `CampanasController.EliminarIndustria` |
| M-A (constante compartida) | — | nuevo `MensajeriaHelpers` | 3 archivos consumen | `ChatsController` consume |
| M-B (reclasificación asistida) | — | — | — | mismo alcance que G7 + modal nuevo |
| M-C (`/Bot/Salud`) | — | — | nuevo método de diagnóstico (o en `OutboundCampaignService`) | `BotController` (o controller nuevo) + vista nueva |

**Riesgos técnicos identificados:**
- **B3**: cambia el contrato de `HiloParcial` (necesita saber cuál fue el último mensaje ya renderizado en el cliente para decidir si hay novedad real) — requiere mandar un parámetro nuevo desde el JS (`últimoIdRenderizado`). Retrocompatible: si no llega el parámetro, se puede mantener el comportamiento actual como fallback, pero el objetivo es que el JS de `Chats/Detail.cshtml` siempre lo mande.
- **G1**: alcance reducido a propósito (ver Diseño) — templates de catálogo con botones QUICK_REPLY siguen sin poder darse de alta por UI en este sprint. Aceptado como deuda declarada, no bug nuevo.
- **G6**: `ExecuteUpdateAsync` requiere EF Core 7+; este proyecto corre EF Core sobre .NET 10, sin incompatibilidad.
- **M-C**: es la única pieza genuinamente nueva (no fix) — página de solo lectura, sin riesgo de escritura; el cálculo de "contactos huérfanos por rubro" reutiliza la misma query que ya usa el `Delete` de industrias (G7), no se reinventa.
- Ninguno de los 17 items toca `AppDbContext.SaveChanges` (auditoría automática) ni el esquema de Identity/roles — impacto de seguridad nulo.

### 7.2 Arquitectura de la feature "4 frentes — combo con gancho" (2026-09-14) — APROBADA

Entrada: `1-analista-funcional.md` (CU-30 a CU-35) y `2-disenador-funcional.md` §8 (aprobado 2026-09-14). Arquitectura aprobada por Joaquín el 2026-09-14 con A1-a y A2 (ver 7.2.8). Presupuesto habilitado.

#### 7.2.0 Reutilización

- **Catálogo:** PAT-031 nació en el diseño de esta misma feature (sin código todavía) → **patrón de diseño sin código portable**; sigue `pendiente_verificar: true` hasta implementar. Se le agrega la nota de arquitectura.
- **Escaneo `docs/*/definiciones/{3-arquitecto-mvc,5-implementador}.md`:** ningún proyecto clasifica sitios web ni asigna oferta por perfil. Construcción nueva.
- **Reutilización literal dentro del repo** (código ya en producción, adaptable con cambios menores): `RubroHelpers` (vocabulario), `Plural`/`NarrativaByType` (parámetros de plantilla), estructura de `BuildComponents` con botones de `olv_frio_v13`, `GetSaludAsync`/`SaludOutboundDto` (M-C), filtros persistidos en `Session` de Contactos/Chats, `ConfigParaEditarAsync` de `BotController`, `ModulosMvpDelRubroAsync` + `MecanismoDolor.MatrizModulos`, `SendBriefToAdminAsync`/`NotifyAdminsInAppAsync`, patrón de guarda de rename/delete de B5.
- **Para el presupuestador:** es una **iteración evolutiva sobre módulos existentes** del mismo repo, no un módulo nuevo (ver feedback de calibración "iteración evolutiva vs. módulo nuevo"). Nada se reutiliza de otro proyecto.

#### 7.2.1 Domain

**Enums nuevos** (`Domain/Enums/`, persistidos con `HasConversion<int>()`):
```csharp
public enum GanchoContacto { PresenciaWeb = 1, Administracion = 2, Consultas = 3, Gestion = 4 }
public enum FrenteComercial { Build = 1, Landing = 2, AiAgents = 3, Chatbots = 4 }
```

**`Contacto`** — 5 propiedades nuevas + 1 método de dominio:
```csharp
public GanchoContacto? Gancho { get; set; }            // null = sin gancho (no es contacto frío)
public string? MotivoGancho { get; set; }              // "Web en plataforma o redes (instagram.com)" — max 120
public DateTime? FechaGancho { get; set; }             // UTC
public bool GanchoAMano { get; set; }
public string? PlantillaPrimerContacto { get; set; }   // nombre de la plantilla EFECTIVAMENTE enviada — max 100
public void AsignarGancho(GanchoContacto? gancho, string? motivo, bool aMano, DateTime ahoraUtc);
```
- `AsignarGancho` vive en la entidad por la regla **CRM-001** (campo nuevo con varios puntos de alta: Maps, Create/Edit manual, carga inicial, red de seguridad en el envío). Mismo criterio que `PausarBotPorIntervencionDeAsesor`.
- `PlantillaPrimerContacto` hace falta para mostrar "Se le ofreció" sin inferirlo: un contacto con gancho Gestión puede haber salido con la combo de gestión o con `v13` de la campaña.

**`ModuloCatalogo`**: `public FrenteComercial Frente { get; set; } = FrenteComercial.Build;`

**`ConfiguracionOutbound`**: `PlantillaGanchoPresenciaWeb`, `PlantillaGanchoAdministracion`, `PlantillaGanchoConsultas`, `PlantillaGanchoGestion` (`string?`, max 100). Se descarta una tabla aparte: son 4 valores fijos y la fila única de configuración ya es el patrón del proyecto (YAGNI).

#### 7.2.2 Application

**`Helpers/CategoriaHelpers.cs`** (nuevo) — **fuente única del vocabulario de `Contacto.Categoria`** (lección CRM-007/CRM-016: hoy las claves están escritas a mano en `ConversacionIaService.CategoriasValidas`, `BotFlowService.Questions` y `BotFlowService.CategoryNames`):
- Constantes `Rent`, `RentOther`, `Build`, `Landing`, `AiAgents = "ai_agents"`, `Chatbot`, `Other`, `MergeLegado = "merge"`.
- `ClavesVigentes` (sin `merge`).
- `Etiqueta(clave)` (tabla de 8.2 del diseño, `merge` → "Mejoras en sistema Olvidata (discontinuado)").
- `FrenteDeCategoria(clave) → FrenteComercial?`.

**`Helpers/GanchoHelpers.cs`** (nuevo, junto a `RubroHelpers`; estático y puro, no toca base):
- `RubroBaseAGrupo` — clave de rubro → `Administracion`/`Consultas` (tabla 8.3); ausente = `Gestion`.
- `DominiosSinWebPropia` (`HashSet<string>`, lista 8.4) + `TieneWebPropia(string? url)`: normaliza con `Uri.TryCreate` (anteponiendo `http://` si falta esquema), host en minúsculas sin `www.`, y compara `host == d || host.EndsWith("." + d)` **en memoria C#** — nunca dentro de una query EF (familia MH-001/CRM-019).
- `ResolverGancho(CanalOrigen canal, string? rubro, string? paginaWeb) → (GanchoContacto? Gancho, string? Motivo)` — filas 1 y 3-6 de la tabla de decisión (la fila 2, "a mano", la resuelve quien llama).
- `CategoriaDeGancho(gancho)` → `landing` / `ai_agents` / `chatbot` / `rent`.
- `Etiqueta(gancho)`, `ClaseBadge(gancho)`, `TextoOferta(gancho, plantillaEnviada)`.

**`Helpers/PlantillasCombo.cs`** (nuevo): los 4 nombres de plantilla combo como constantes + a qué gancho pertenece cada una. Motivo: las plantillas combo llevan botones QUICK_REPLY, que la rama genérica de catálogo (G1) **no soporta**; necesitan casos explícitos en `BuildComponents`, así que el nombre queda fijado en código. El selector de `/Bot` solo ofrece estos nombres (si además están activos y aprobados). Una versión nueva de una plantilla requiere deploy — ya era así para `v10`-`v13` (decisión A2).

**DTOs:**
- `ContactoListItemDto` + `Gancho`, `Categoria`.
- `SaludOutboundDto` + `List<GanchoSinEnvioDto> GanchosSinEnvio` (`Gancho`, `Motivo`, `ContactosEsperando`).
- `PlantillaGanchoEstadoDto` (`Gancho`, `Plantilla`, `Estado` lista / sin plantilla / no aprobada / inactiva / usa la de campaña, `ContactosEsperando`).

**`IOutboundCampaignService`** + `GetEstadoPlantillasGanchoAsync(ct)` y `AsignarGanchosPendientesAsync(ct)` (idempotente: solo `OutboundFrio` + `Pendiente` + `Gancho == null` + no asignado a mano). Sin interfaces nuevas.

#### 7.2.3 Infrastructure

**`AppDbContext`:**
- `Contacto`: `Gancho` `HasConversion<int>()` + `HasIndex(Gancho)`; `MotivoGancho` `HasMaxLength(120)`; `PlantillaPrimerContacto` `HasMaxLength(100)`.
- `ModuloCatalogo`: `Frente` `HasConversion<int>().HasDefaultValue(FrenteComercial.Build)` — las filas existentes nacen en Build (mismo criterio que el default de `ConversacionIaModoSombra`: la columna nueva no puede nacer en 0).
- `ConfiguracionOutbound`: 4 strings `HasMaxLength(100)`.
- `Categoria` sigue en varchar(20): `ai_agents` (9) y `chatbot` (7) entran.

**`Queries/ModuloCatalogoQueries.cs`** (nuevo, extensión estática sobre `AppDbContext`): `ModulosDestacadosAsync(industriaBot, frente, ct)`. Hoy la misma consulta está **duplicada** en `BotFlowService.ModulosMvpDelRubroAsync` y `ConversacionIaService.ModulosMvpDelRubroAsync`; agregarle el frente a las dos copias es exactamente el escenario de desincronización CRM-007. Regla de lectura (diseño 8.10):
- `Build`: igual que hoy (industria + `EsImprescindible` + no borrado) **más `Frente == Build` explícito**, así los módulos de otros frentes nunca se cuelan en la matriz MVP.
- Otro frente: `m.Frente == f && (m.Industrias.Any(i => industria) || !m.Industrias.Any())`, orden por `PrecioMaxUsd`, `Take(4)`.
- Envuelta en `try/catch` que devuelve lista vacía: se ejecuta dentro del webhook (**CRM-020**).

**`OutboundCampaignService`:**
1. **`AgregarProspectosNuevosAsync`**: `nuevoContacto.AsignarGancho(GanchoHelpers.ResolverGancho(...))` antes del `Add`.
2. **`SendDailyBatchAsync`:**
   - Sobre los `candidatos` ya materializados: asigna gancho a los que no tienen (red de seguridad, en memoria, se guarda con el mismo `SaveChanges`).
   - Carga una vez la configuración y el catálogo de plantillas (`Nombre`, `Texto`, `EstadoAprobacionMeta`, `Activo` — la tabla ya se trae entera hoy).
   - Función local `ResolverPlantilla(contacto, campana, experimento) → (nombre, variante)?`:

     | Caso | Resultado |
     |---|---|
     | Referido | `olv_referido_v2` (sin cambios) |
     | Gancho PresenciaWeb / Administración / Consultas con plantilla configurada, activa y aprobada | esa plantilla, sin A/B |
     | Esos 3 ganchos sin plantilla disponible | `null` → **no se envía** |
     | Gancho Gestión con plantilla combo disponible | la combo de gestión, sin A/B |
     | Gestión sin combo, o sin gancho | `campana.TemplateWhatsApp` + split A/B **por el mismo código de hoy** |

   - **Trampa resuelta:** el filtro de "no se envía" va **antes** del `.Take(cupo)` (`pendientes = candidatos.Where(claves).Where(fallidos).Where(tiene plantilla).OrderBy(...).Take(cupo)`). Si fuera después, un contacto salteado ocuparía un lugar del cupo y la campaña mandaría menos de lo que puede. Los salteados se cuentan por gancho para el log y para `/Bot/Salud`.
   - Tras un envío exitoso: `contacto.PlantillaPrimerContacto = templateName` (también por el camino de `v13`).
   - `FaseConversacion.ConfirmandoContinuar`: la condición literal `templateName is "olv_frio_v10" or ... "olv_frio_v13"` se reemplaza por `EsPlantillaConBotonContinuar(templateName)` = v10-v13 + `PlantillasCombo`.
3. **`BuildComponents`**: 4 casos nuevos con los 2 botones `seguir`/`no_interesa`. Web/Admin/Consultas: `{{1}} = Plural(RubroBase)`. Gestión: `{{1}} = NarrativaByType.Dolor`, `{{2}} = NarrativaByType.Area`. `TemplateBodies` + 4 textos, para que `/Chats` muestre el mensaje real.
4. **`ProcessFollowUpsAsync` / `MarkColdAsync`**: hueco no cubierto por el diseño — ver **decisión A1**.
5. **`GetSaludAsync`**:
   - Suma `GanchosSinEnvio` (conteo de `Pendiente` + `OutboundFrio` agrupado por `Gancho` en SQL — agrupar por int no tiene el problema MH-001).
   - **Corrige un falso positivo:** `TemplatesSinCampana` tiene que contar como "en uso" también las 4 plantillas de `ConfiguracionOutbound`.
6. **`GetEstadoPlantillasGanchoAsync`**: filas de la card de `/Bot`.

**`BotFlowService`:**
- `Questions`: claves desde `CategoriaHelpers`, + `ai_agents` y `chatbot` (cuestionarios de 8.6). `merge` se conserva solo para conversaciones históricas en curso.
- `CategoryNames` → reemplazado por `CategoriaHelpers.Etiqueta`.
- **`OnConfirmarContinuarAsync`**: hoy `if (contacto.Categoria != "rent") { resuelve rubro; Categoria = "rent"; }`. Pasa a:
  - `Categoria == null` (camino de plantilla con botón) → resuelve el rubro igual que hoy y fija `Categoria = GanchoHelpers.CategoriaDeGancho(contacto.Gancho)` (sin gancho → `rent`, idéntico a hoy).
  - `Categoria == "rent"` ya resuelta por `OnNewAsync` (legado) → no se toca.
- **`SendCurrentQuestionAsync` / `MecanismoPregunta1Async`**: para `landing`/`ai_agents`/`chatbot` usa `ModulosDestacadosAsync(industria, frente)`; con módulos, pregunta con módulos; sin módulos, pregunta fija. La rama `rent` queda intacta.
- **Acceso seguro**: `Questions[contacto.Categoria!]` (2 sitios: `OnAnswerAsync`, `SendCurrentQuestionAsync`) → `TryGetValue`. Si no existe → `EscalarPorCategoriaSinCuestionarioAsync`: `EstadoEmbudo = DerivadoManual`, nota interna, `NotifyAdminsInAppAsync`; al prospecto no se le manda nada.
- El fallback desde `ConversandoConIa` ya chequea la clave: con las entradas nuevas deja de reiniciar el guion para `ai_agents`/`chatbot`. Sin cambio de código ahí.

**`ConversacionIaService`:**
- `CategoriasValidas`: se arma recorriendo `CategoriaHelpers.ClavesVigentes` + un diccionario local de descripciones con ejemplos de dolor. Sin `merge` → el enum de `set_categoria` y la validación en código lo rechazan solos. Una clave sin descripción cae a `CategoriaHelpers.Etiqueta` (nunca excepción en el inicializador estático: tiraría el tipo entero).
- **Bloque estable (cacheado)**: identidad con los 4 frentes, categorías con ejemplos, reglas de venta cruzada, "web simple → landing" y "cliente actual → escalar". Todo es igual para todos los contactos, así que **no rompe el cruce de cache entre contactos**. Costo: el prefijo cambia una vez y la primera conversación después del deploy reescribe la cache (orden de USD 0,03, una vez).
- **Bloque del contacto (sin cache)**: línea del gancho y la oferta ("Le escribimos ofreciendo … abriendo por {gancho} ({motivo})", o "sistema de gestión con la plantilla de la campaña" si `PlantillaPrimerContacto` no es combo), y módulos del frente de la categoría actual (o del gancho si la categoría está vacía). Nunca en el bloque estable: rompería la cache (medido 2026-09-13).
- `consultar_modulos_del_rubro`: mismo schema (solo rubro) → la definición de la tool no cambia salvo el enum de categorías de `set_categoria`. Internamente usa `ModulosDestacadosAsync` con `FrenteDeCategoria(contacto.Categoria) ?? frente del gancho ?? Build`.
- Modo sombra: no hay escrituras nuevas (`set_categoria` ya está guardado por `!modoSombra`) → cumple **CRM-022**.

#### 7.2.4 Web

- **`ContactosController`:**
  - `GetData`: filtros `gancho` (enum; `"sin"` → `Gancho == null`) e `interes` (clave; `"sin_clasificar"` → `Categoria == null`), por **igualdad**, nunca `Contains` sobre lista de string (MH-001). Session keys `SessionGancho`/`SessionInteres`, repuestas en `Index` y borradas por "Limpiar filtros". Proyección + `AplicarOrden` con las 2 columnas.
  - `Create`/`Edit`: `PaginaWeb` + `GanchoElegido`. Al guardar: elegido → `AsignarGancho(..., aMano: true)`; "Automático" + canal `OutboundFrio` → `ResolverGancho`. Aviso si `FechaPrimerEnvio != null`.
  - `Details`: card "Oferta".
- **`ChatsController`**: `ChatFiltrosViewModel.Gancho` + session key + `QueryFiltrada` (`c.Gancho == g`). Como `MarcarTodosLeidos` (G6) reutiliza `QueryFiltrada`, el filtro nuevo se respeta solo. `ProyectarLista` + chip; `Detail` + card.
- **`BotController`:**
  - `Index` carga `GetEstadoPlantillasGanchoAsync`.
  - `POST GuardarPlantillasGancho` (`[ValidateAntiForgeryToken]`): valida del lado del servidor que cada valor no vacío esté en `PlantillasCombo`, que sea del gancho correcto y que esté activa y aprobada.
  - `POST AsignarGanchos` (AJAX, JSON) para ejecutar la carga inicial desde la card sin esperar el scheduler.
  - `Salud`: bloque nuevo.
- **`TemplatesController`**: la guarda de **B5** (rename bloqueado si hay campañas activas usándola) y la de `Delete` tienen que chequear **también** las 4 plantillas de `ConfiguracionOutbound`. Si no, renombrar una combo deja el gancho apuntando a un nombre inexistente y sus contactos dejan de enviarse (**LP-002**: extender todos los usos del concepto "plantilla en uso", no solo el nuevo).
- **`ModulosController`:**
  - `Create`/`Edit` + `Frente`; `GetData` columna + filtro.
  - Build sin rubros se muestra con badge "sin rubros" en el listado, **no** como validación: los rubros se agregan por AJAX después de crear el módulo, así que no se pueden exigir en el alta.
  - `Presupuesto`/`Checklist`/`Calcular`/`GenerarMensaje`: parámetro `int[] frentes` (default `[Build]`); checklist agrupado por frente; con solo Build la consulta y el resultado son idénticos a hoy.
- **Vistas**: `Contactos/{Index,Create,Edit,Details}`, `Chats/{Index,_ChatListItems,Detail}`, `Bot/{Index,Salud}`, `Modulos/{Index,Create,Edit,Presupuesto,_Checklist}`. Todo combo con Select2 (auto-init global); textos con tildes (regla 25).

#### 7.2.5 Permisos, estados y validaciones

- **Permisos**: sin cambios. Todo bajo `RequireSuperUsuario`; POST nuevos con antiforgery. Webhook sin cambios de autenticación.
- **Máquina de estados**: `FaseConversacion` y `EstadoEmbudo` sin valores nuevos; el diseño es soportable tal cual. Cambian qué categoría y qué pregunta se usan en `ConfirmandoContinuar → AskingQuestions`, y (según A1) quizás la regla de paso a `Frio`.
- **Validaciones server-side**: categoría ∈ `ClavesVigentes` (tool + código); plantilla por gancho ∈ `PlantillasCombo`, del gancho correcto, activa y aprobada; `GanchoElegido` ∈ enum o vacío; `Frente` ∈ enum; `frentes` de Armar presupuesto con al menos 1.

#### 7.2.6 Migración EF

**Sí — 1 migración aditiva: `AddGanchoYFrenteComercial`.**
- `Contactos`: `Gancho` int null + índice, `MotivoGancho` varchar(120) null, `FechaGancho` datetime null, `GanchoAMano` bool not null default 0, `PlantillaPrimerContacto` varchar(100) null.
- `ModulosCatalogo`: `Frente` int not null default 1 (Build).
- `ConfiguracionesOutbound`: 4 × varchar(100) null.
- Sin SQL de datos: la carga inicial de ganchos necesita las reglas en C# (dominios, grupos), así que la hace `AsignarGanchosPendientesAsync` (botón en `/Bot` + red de seguridad en cada lote).
- `Down` elimina las columnas.
- Aplicar primero en `olvidatacrm_dev`.

#### 7.2.7 Riesgos técnicos

| # | Riesgo | Mitigación |
|---|---|---|
| T1 | Contacto salteado ocupa lugar del `Take(cupo)` | Filtro antes del `Take` (7.2.3) |
| T2 | Nombres de plantilla combo fijos en código | Selector restringido a `PlantillasCombo`; nueva versión = deploy (A2) |
| T3 | Guarda de rename/delete de plantillas y `TemplatesSinCampana` ignoran la configuración | Extender las 3 (LP-002) |
| T4 | MH-001 / CRM-019 | Dominios en memoria; filtros por igualdad de enum/clave; sin `StartsWith`/`Contains` de string en queries nuevas. QA ejercita los endpoints con base vacía |
| T5 | CRM-001: gancho escrito distinto en cada alta | `Contacto.AsignarGancho` único + `grep "new Contacto"` en la implementación |
| T6 | CRM-007/016: vocabulario de categorías en 3 lugares | `CategoriaHelpers` como fuente única |
| T7 | Consulta de módulos duplicada en 2 servicios | `ModuloCatalogoQueries` compartida |
| T8 | CRM-020: código nuevo en el camino del webhook | Consulta de módulos y escalada envueltas; cualquier falla degrada a pregunta fija |
| T9 | Follow-up de gestión a prospectos del combo | Decisión A1 |
| T10 | Cache del prompt reescrita una vez al desplegar E2 | Esperado, costo despreciable |
| T11 | Contactos sin plantilla dejan el volumen diario por debajo del cupo | Visible en `/Bot` y `/Bot/Salud` |
| T12 | Gancho asignado con rubro crudo con sufijo de región (`consultorio-palermo`) | `ResolverGancho` usa `RubroHelpers.RubroBase` |

#### 7.2.8 Decisiones del gate — RESUELTAS 2026-09-14: A1-a y A2

**Vigente:** los ganchos PresenciaWeb/Administración/Consultas no reciben `olv_nurturing_v2`; `MarkColdAsync` los pasa a `Frio` desde `MensajeEnviado` a los 7 días de `FechaPrimerEnvio`. Gestión y sin gancho sin cambios. `ProcessFollowUpsAsync` excluye esos 3 ganchos por igualdad de enum (no `Contains` de lista). Nombres de plantilla combo fijos en `PlantillasCombo`. Opciones evaluadas:

- **A1 — Follow-up de los ganchos combo.** Hoy `ProcessFollowUpsAsync` le manda a **todo** `MensajeEnviado` con 3 días `olv_nurturing_v2` ("{negocio} tenía {dolor} y hoy tiene todo ordenado desde el sistema"), y `MarkColdAsync` solo pasa a `Frio` desde `FollowUpEnviado`. Opciones:
  - **A1-a (recomendada):** PresenciaWeb/Administración/Consultas no reciben `nurturing_v2`. `MarkColdAsync` los pasa a `Frio` directo desde `MensajeEnviado` a los 7 días (3 + 4, mismo plazo total que hoy). Gestión y sin gancho siguen igual. Sin plantilla nueva ni gasto de un mensaje incoherente.
  - **A1-b:** mantener `nurturing_v2` para todos (mensaje de gestión a quien abrimos por web o consultas).
  - **A1-c:** plantilla de follow-up combo por gancho (4 plantillas más, marketing y Meta) — alcance nuevo.
- **A2 — Nombres de plantilla combo en código.** Recomendado aceptar: ya es así para `v10`-`v13`, porque los botones exigen un caso explícito.

#### 7.2.9 Mapa por etapa del plan funcional

| Etapa | Domain | Application | Infrastructure | Web | Migración |
|---|---|---|---|---|---|
| E1 Vocabulario y árbol | — | `CategoriaHelpers` | `BotFlowService` (Questions, etiquetas, TryGetValue + escalada), `ConversacionIaService` (CategoriasValidas) | Etiquetas de categoría en vistas existentes | No |
| E2 Prompt | — | — | `ConversacionIaService` (bloque estable) | — | No |
| E3 Gancho en contacto | Enum + 5 props + `AsignarGancho` | `GanchoHelpers`, DTO | `AppDbContext`, alta Maps, `AsignarGanchosPendientesAsync` | Contactos (Index/Create/Edit/Details), Chats (filtro/chip/card) | **Sí** |
| E4 Conversación por gancho | — | — | `OnConfirmarContinuarAsync`, contexto del contacto en la IA | — | No |
| E5 Envío por gancho | 4 props config | `PlantillasCombo`, DTOs | `SendDailyBatchAsync`, `BuildComponents`, `TemplateBodies`, salud, A1 | `/Bot` card + acciones, `/Bot/Salud`, guardas de Templates | (en la misma) |
| E6 Módulos por frente | Enum + prop | — | `ModuloCatalogoQueries` (+ consumo en los 2 servicios) | `ModulosController` + vistas | (en la misma) |
| E7 Documentación | — | — | — | `arbol-comunicacion-bot.md`, `logica-negocio-bot.md` | No |

Se propone **una sola migración** con todas las columnas (E3, E5 y E6) para no generar 3 migraciones seguidas sobre el mismo deploy. Si E6 se posterga, se separa su columna en otra migración.

#### 7.2.10 Pruebas funcionales mínimas (para QA)

1. `ResolverGancho`: web vacía → PresenciaWeb; `instagram.com/x` y `x.mitiendanube.com` → PresenciaWeb; `modalu.com.ar` + `estudio` → Administración; `modalu.com.ar` + `consultorio-palermo` → Consultas; dominio propio + `comercio` → Gestión; canal Ads → sin gancho.
2. Lote: gancho sin plantilla → no se envía, no descuenta cupo ni presupuesto, aparece en `/Bot` y `/Bot/Salud`, y el resto de la campaña completa su cupo.
3. Gestión sin combo → sale `v13` con el A/B de la campaña intacto (regresión).
4. Botón "Sí, contame más" por cada gancho → categoría y primera pregunta correctas; sin gancho → idéntico a hoy.
5. IA caída con `ai_agents` → sigue el cuestionario, no repite la presentación; categoría sin cuestionario → `DerivadoManual` + notificación, sin error al prospecto.
6. `set_categoria` con `merge` → rechazada; históricos con `merge` → etiqueta "discontinuado".
7. Filtros de gancho e interés en Contactos y Chats: filtran, persisten en `Session`, "Limpiar filtros" los borra. Probarlos también con base sin contactos (MH-001).
8. Renombrar o borrar una plantilla combo configurada → bloqueado.
9. Armar presupuesto con solo Build → mismo checklist y mismo mensaje que antes del cambio (regresión R9).
10. Tras migrar: módulos existentes en Build; contactos existentes sin gancho hasta "Asignar ganchos".

### 8. Estrategia de pruebas

QA manual (sin automatización de navegador, preferencia ya establecida del estudio): validar cada historia de usuario contra la base de desarrollo — webhook simulado con curl/Postman (mensaje nuevo, respuesta de calificación, reintento con mismo `message_id`), verificación de datos persistidos en `Contacto`/`ContactoRespuesta`, prueba manual del scheduler fuera de horario (invocar el `IHostedService` sin esperar el cronograma real).

## Historial de ajustes
- 2026-07-14: Arquitectura técnica cerrada (migración base de BotPublicitario). 4 entidades Domain + 4 enums, 4 interfaces Application, mapa completo de reutilización (WhatsAppClient/GoogleMapsService portados sin cambio de lógica; BotFlowService/OutboundCampaignService migrados a BD). 1 migración EF. Runbook de corte de producción definido y ejecutado.
- 2026-07-21: Arquitectura de "campañas de contacto frío configurables" cerrada. Resueltas 2 ambigüedades: `ClaveRubro`/queries cuelgan de `CampanaOutboundIndustria` (no de `IndustriaCatalogo`, varios rubros comparten precio); `TemplateWhatsApp` de campaña gobierna solo el primer contacto frío (Referido/follow-up mantienen template fijo). 3 entidades + 1 enum, 1 migración EF, `CampanasController` nuevo, 2 filas de seed para Farmacia/Estudio.
- 2026-07-24: Ajuste exprés de UI de Notificaciones — solo capa Presentación (ícono + `Swal.fire` en vez de `confirm()` nativo), sin migración ni paquetes nuevos.
- 2026-08-14: Corrección de `EstadoEmbudo` (se retiran 6-8, nunca implementados) y `DiasSemana` (de 3 a 7 días reales). Corrección del modelo de permisos: las policies `RequireVendedor`/`RequireAdministracion` no existen, todo el sistema usa `RequireSuperUsuario` desde el 2026-07-21. Arquitectura retroactiva de Chats/scheduler multi-zona/multimedia: 3 campos nuevos en Domain, `IWhatsAppClient` extendida, 3 hosted services nuevos, `ChatsController` nuevo, 5 migraciones EF + `RemoveAuditLog` (ya aplicada el 2026-07-28).
- 2026-08-14: Arquitectura de "Gestión comercial y herramientas de canal/venta" cerrada. 5 entidades Domain (`Cliente`, `Upsell`, `TemplateWhatsApp`, `CampanaExperimento`, `SugerenciaSeguimiento`) + 1 enum + 1 campo en `ContactoRespuesta`, 5 controllers nuevos/extendidos, migración `AddGestionComercial`. Split A/B sembrado por contacto, NRR con "datos insuficientes" explícito.
- 2026-08-27: Arquitectura del sprint "corrección de bugs/gaps de auditoría + 3 mejoras" cerrada. **0 migraciones EF nuevas** — todos los campos necesarios (`ReferidoPor`/`MotivoReferido`/`PresupuestoCotizadoUsd` de `Contacto`, `PrimerAnioGratis` de `Cliente`) ya existían en el esquema, solo faltaba exponerlos. 17 items mapeados por capa, ningún cambio toca Domain ni Identity/permisos.
- 2026-08-16: Reestructuración documental — este archivo tenía 4 secciones fechadas acumuladas (Arquitectura base 2026-07-14, Campañas 2026-07-21, Notificaciones 2026-07-24, Chats retroactiva + Gestión comercial 2026-08-14) con correcciones en notas al pie sobre contenido ya obsoleto. Consolidado en una única sección "Definiciones vigentes" (Domain/Application/Infrastructure/Web/Permisos/Migraciones/Riesgos, editada in-place de ahora en más) + este historial cronológico de una línea por cambio. Ningún dato funcional se perdió en la consolidación (verificado contra las 4 secciones originales: entidades, enums, servicios, hosted services, controllers, migraciones y riesgos técnicos).
- 2026-08-16: Mejora del barrido de Google Maps + detección de campaña "Completa". Paginación real en `SearchAsync` (hasta 3 páginas/60 resultados por query, antes solo la primera). Tracking de rendimiento por industria (`CampanaOutboundIndustria.RachaSinResultadosNuevos`/`SinResultadosNuevos`, umbral 5 corridas seguidas sin prospectos nuevos) y marca automática de campaña `Completa` (`CampanaOutbound.Completa`/`FechaCompletada`) cuando todas sus industrias se agotan, con notificación in-app a `SuperUsuario` — sin tocar `Activa`, el backlog ya encontrado sigue enviándose. Acción nueva `CampanasController.ReabrirBusqueda`. Migración `AddCampanaBusquedaCompleta` (4 columnas aditivas).
- 2026-09-14: agregadas las migraciones `AddPausaBotPorContacto` y `AddConversacionIa`, la seccion 6.2 (conversacion agentica con LLM: piezas, 9 herramientas con enums cerrados, prompt en 2 bloques por la cache, fallback al arbol, modo sombra sin efectos, pausa por contacto) y la ampliacion de 6.1 a 3 lineas de costo con reparto y techos derivados. Actualizados 2 riesgos: el standby ya se persiste, y se suma `StartsWith` a la familia MH-001.
- 2026-09-04: agregadas las 6 migraciones posteriores a `AddCampanaBusquedaCompleta` y la sección 6.1 (control de costos del bot: tarifas Meta por país, caché de `place_id` de Maps, tope único en ARS, volumen diario derivado del precio).
- 2026-09-14: Arquitectura de "4 frentes — combo con gancho" (§7.2, pendiente de aprobación). 2 enums, 5 props en `Contacto` + `AsignarGancho`, `Frente` en `ModuloCatalogo`, 4 plantillas en `ConfiguracionOutbound`; helpers `CategoriaHelpers`/`GanchoHelpers`/`PlantillasCombo`; consulta de módulos compartida; 1 migración aditiva `AddGanchoYFrenteComercial`. Hallazgos: filtro de no-envío antes del `Take(cupo)`, guardas de plantillas y `TemplatesSinCampana` a extender (LP-002), follow-up `nurturing_v2` incoherente con el combo (decisión A1).
