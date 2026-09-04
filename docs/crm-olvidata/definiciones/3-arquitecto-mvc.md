# Memoria - Arquitecto MVC

## Proyecto: crm-olvidata — migración de BotPublicitario + evolución continua
## Última actualización: 2026-09-04

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

`AddContactosYCatalogoIndustrias` (4 tablas base) → `AddCampanasOutbound` (3 tablas + 2 filas seed `IndustriaCatalogo`) → `AddZonaHorariaCampana` → `AddMediaFieldsToContactoRespuesta` → `AddEmailToContacto` → `AddFechaUltimaAlertaVentana` → `AddMarcadoNoLeidoManual` → `RemoveAuditLog` (**única no aditiva** — elimina la tabla `AuditLogs` completa, 2026-07-28, decisión explícita del cliente) → `AddGestionComercial` (5 tablas: `Clientes`, `Upsells`, `TemplatesWhatsApp`, `CampanasExperimento`, `SugerenciasSeguimiento` + columna `ContactoRespuestas.VarianteExperimento`) → `AddCampanaBusquedaCompleta` (4 columnas aditivas: `CampanaOutbound.Completa`/`FechaCompletada`, `CampanaOutboundIndustria.RachaSinResultadosNuevos`/`SinResultadosNuevos`) → `AddModuloCatalogo` (2 tablas: `ModulosCatalogo`, `ModuloCatalogoIndustrias` — matriz MVP/FULL) → `AddContactoAdOrigen` (3 columnas: `AdOrigenTag`/`AdReferralSourceId`/`AdReferralHeadline`, origen de anuncios click-to-WhatsApp) → `AddBusquedaMapsPausada` (1 columna: pausa persistente de la API de Maps) → `AddTarifasYPresupuestoMensajeria` (tabla `TarifasWhatsApp` + `ConfiguracionOutbound.PresupuestoMensualArs`) → `AddCacheYConsumoMaps` (2 tablas: `GoogleMapsPlacesVistos` con indice unico por `PlaceId`, `ConsumosMapsDiarios`) → `AddCotizacionUsdArs` (1 columna: cotizacion para consolidar el gasto de Google dentro del presupuesto en ARS). Todas aditivas. Todas aplicadas primero en `olvidatacrm_dev`.

### 6.1 Control de costos del bot (2026-09-03/04)

El bot tiene 2 costos externos reales y se miden por separado porque facturan distinto:

- **Mensajeria de Meta (ARS)** — desde 2025-07-01 se cobra por PLANTILLA ENTREGADA, no por conversacion. Marketing (frio + follow-up) se cobra SIEMPRE y **no tiene descuento por volumen**. Tarifas por pais del DESTINATARIO en `TarifaWhatsApp` (Argentina 89,56 / Chile 128,84 / Uruguay 107,24 "Rest of LatAm" / fallback 87,53), sembradas por fila desde la rate card oficial. El pais se resuelve por el **prefijo de `Contacto.Telefono`**, no por `CampanaOutbound.Region` (texto libre, y Meta factura por el numero al que entrega).
- **Google Places API (USD)** — el Text Search es GRATIS; el 97% del gasto es el Place Details de cada lugar encontrado (Details + Contact Data ≈ USD 0,0171). `ConsumoMapsDiario` cuenta requests facturables por dia (incluidas las paginas extra de `next_page_token`, que se facturan aparte) y los Details EVITADOS por cache.
- **Cache `GoogleMapsPlaceVisto`** (indice unico por `PlaceId`): el `place_id` viene gratis en el Text Search, el telefono solo con el Details pago. Antes se pagaba el Details de TODOS los lugares y recien despues se descartaba por telefono duplicado — sobre la factura real de agosto 2026, 72,5% de las llamadas no produjeron ningun contacto nuevo. Se guarda tambien el caso "sin telefono". El dedupe es GLOBAL (el place_id identifica al negocio, no a la busqueda). **OJO MH-001**: el chequeo es por `AnyAsync(p => p.PlaceId == id)` uno por uno, NO `Where(listaLocal.Contains(...))` — una lista local de string no traduce a SQL contra el provider MySQL.
- **Tope unico en ARS** (`ConfiguracionOutbound.PresupuestoMensualArs`) sobre el COSTO TOTAL: mensajeria + Maps convertido con `CotizacionUsdArs` (cargada a mano a proposito — en Argentina no hay una unica cotizacion "correcta"). Sin cotizacion cargada el tope cubre solo la mensajeria y la pantalla lo avisa. El tope diario efectivo es `min(CupoDiario, presupuestoRestante / diasRestantes / costoPromedioPorMensaje)`.
- **El volumen diario lo fija el PRECIO, no una meta de cantidad** (2026-09-03): `MetaDiaria` quedo solo como respaldo para cuando no hay presupuesto. `RebalancearMatrizAsync` escala contra la meta derivada del presupuesto.

### 7. Riesgos y supuestos vigentes

- **Deduplicación de webhooks no persistente** (`HashSet` en memoria) — aceptado, ver Infrastructure §3.
- **Concurrencia en alta de `Contacto`**: dos flujos pueden intentar crear el mismo teléfono a la vez (webhook vs. outbound). El índice único de `Telefono` actúa como red de seguridad — el flujo que llega segundo captura la excepción de duplicado y hace `UPDATE` en vez de `INSERT`.
- **Retención de media no garantizada**: `Chats/Media` puede devolver 404 en un adjunto viejo si Meta ya lo purgó — caso esperado, no una excepción sin manejar. Captura de multimedia no es retroactiva (solo mensajes recibidos después del deploy del 2026-08-13 tienen `MediaId`).
- **Literal cross-capa duplicado** (etiquetas de evento) — ver Infrastructure §3, mejora pendiente no resuelta todavía.
- **Estado en memoria no persistido**: standby del scheduler y `ManualPipelineQueue` se resetean en cada recycle del app pool (cualquier deploy) — riesgo aceptado desde el diseño original.
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
- 2026-09-04: agregadas las 6 migraciones posteriores a `AddCampanaBusquedaCompleta` y la sección 6.1 (control de costos del bot: tarifas Meta por país, caché de `place_id` de Maps, tope único en ARS, volumen diario derivado del precio).
