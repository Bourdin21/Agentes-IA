# Memoria - Implementador

## Proyecto: crm-olvidata
## Ultima actualizacion: 2026-08-16

## Definiciones vigentes

### Archivos y capas modificadas

Bootstrap técnico de `C:\Sistemas\olvidatasoft-crm` (solución/namespace `OlvidataCRM`), copiado de `C:\Sistemas\KoiDumplings` y saneado. Repo verde: build OK, 0 errores.

- **Domain**: quedaron `ApplicationUser`, `AuditLog`, `Notification`, `PreferenciaUsuario`, `SoftDestroyable`, enum `EstadoUsuario`. Eliminadas 11 entidades y 4 enums de KOI (Inversor, Rubro, Subgrupo, ParametroPorcentaje, PeriodoMensual, VentaMensual, ConceptoGasto, AsignacionPuntos, Liquidacion, ConfiguracionCamara, RegistroEnvioNotificacion + sus enums).
- **Application**: quedaron `DataTableDtos`, `ServiceResult`, `NotificationDtos`, `IEmailService`, `IErrorNotifier`, `IExportService`, `INotificationService`, `IRepository`, `FeatureFlags`. Eliminadas 5 DTOs y 8 interfaces de servicios de KOI.
- **Infrastructure**: quedaron `Repository`, `DatabaseHealthCheck`, `EmailService`, `ErrorNotifier`, `ExportService`, `NotificationService`, `SmtpHealthCheck`, `SmtpSettings`. Eliminados 8 servicios de KOI. `DependencyInjection.cs` y `AppDbContext.cs` (DbSets + `OnModelCreating`) editados para sacar todo lo de KOI, preservando intacto el override de `SaveChanges`/auditoría/soft-delete (100% genérico). `SeedData.cs` reescrito: solo roles + bootstrap de SuperUsuario, sin `SeedRubrosAsync`/`SeedDemoDataAsync` ni rol Inversor.
- **Web**: quedaron controllers `AccountController`, `AuditController`, `HomeController`, `NotificationsController`, `SystemController`, `UsersController` (y sus Views/Models). Eliminados 12 controllers de KOI + sus Views/Models. `UsersController`/`UserViewModels`/`Views/Users/Create,Edit` limpiados de toda referencia a `Inversor`/`InversorId` (rol y FK ya no existen). `_Layout.cshtml`: sidebar sin links de KOI, textos genéricos, cookie de tema `koi-tema` → `crm-tema` (también en `AccountController`). `HomeController.Index()` redirige a `Notifications` (antes a `Dashboard`, eliminado).
- **Config**: `appsettings.Production.json` sanitizado (tenía credenciales reales de KOI en texto plano — DB MySQL y SMTP). `appsettings.Development.json` sin el flag `Seed:Demo`. `UserSecretsId` regenerado. Corregidas rutas `ProjectReference`/`.slnx` que apuntaban a carpetas `KoiDumplings.*` inexistentes (arrastre de un rename previo a medio terminar).
- **Repo**: `git init` limpio, sin historial de KOI.

### Migraciones EF generadas

`InitialCreate` (`OlvidataCRM.Infrastructure/Data/Migrations/`, generada con `--output-dir Data/Migrations`) sobre el modelo trimeado: solo tablas Identity (`AspNetUsers`, `AspNetRoles`, etc.) + `AuditLogs` + `Notifications` + `PreferenciasUsuario`. No aplicada contra ninguna base real (no se corrió `database update`).

### Riesgos residuales

- El Dashboard real del CRM no existe todavía — `HomeController` redirige a `Notifications` como landing provisional hasta que Diseño/Arquitectura lo definan.
- Warnings preexistentes de la base KoiDumplings sin resolver (no forman parte de este alcance): `NU1902` (MailKit/MimeKit con vulnerabilidad moderada conocida) y `CS0114` (`HomeController.StatusCode` oculta miembro heredado sin `override`/`new`).
- Roles quedaron en SuperUsuario/Administrador/Vendedor/Empleado (Vendedor/Empleado heredados de KOI tal cual, sin validar todavía si aplican al CRM — a confirmar en Análisis).

### Proximos pasos pendientes

Análisis funcional del CRM (entidades Contacto/Lead, Cliente, Plan, Upsell, Proyecto/Pipeline — ver `1-analista-funcional.md`) seguido de Diseño, Arquitectura y Presupuesto antes de implementar funcionalidad de negocio sobre esta base.

## Implementación de la migración de BotPublicitario (2026-07-17)

### 0. Escaneo de reutilización

No se escaneó `docs/*/definiciones/5-implementador.md` porque la fuente de reutilización ya está explícitamente mapeada en `3-arquitecto-mvc.md` §1: `C:\Sistemas\BotPublicitario`. Se leyó y portó/migró código real de ese repo (`WhatsApp/WhatsAppClient.cs`, `WhatsApp/GoogleMapsService.cs`, `Webhook/BotFlowService.cs`, `WhatsApp/OutboundCampaignService.cs`, `Webhook/OutboundSchedulerService.cs`, `Webhook/Program.cs`) en vez de escribir desde cero. `MessageLogService`, `ExcelTrackerService`, `TemplateCreationService`, `CatalogService`, `MetaAdsClient` no se portaron (confirmado en Arquitectura).

### 1. Alcance funcional resumido

Migración completa de BotPublicitario (captación/calificación por WhatsApp, presupuesto automático, outbound diario, búsqueda por Google Maps, notificación in-app) a `OlvidataCRM`, con 3 pantallas de gestión (Contactos, Industrias, Bot/Outbound) — CU-01 a CU-06 y CU-10 a CU-12 del Análisis, 11 historias de usuario del Diseño.

### 2. Plan de ejecución técnica ejecutado (por etapas, según plan funcional del Diseño §7)

1. Datos base: entidades + migración EF + seed de 13 industrias — OK.
2. Servicios de negocio migrados: `BotFlowService`, `OutboundCampaignService`, `WhatsAppClient`, `GoogleMapsService` — OK.
3. Webhook + scheduler: endpoint Minimal API + `OutboundSchedulerService` (`IHostedService`) — OK.
4. Pantallas CRM: `Contactos`, `Industrias`, `Bot/Outbound` — OK.
5. Corte y migración de datos en tránsito de BotPublicitario — **NO ejecutado a propósito** (fuera de alcance de esta sesión, es un runbook operativo posterior, ver Arquitectura §5).

### 3. Cambios por capa

**Domain** (`OlvidataCRM.Domain`):
- `Enums/CanalOrigen.cs`, `Enums/FaseConversacion.cs`, `Enums/EstadoEmbudo.cs`, `Enums/PlanSistema.cs` — nuevos, exactamente como definidos en Arquitectura §2.
- `Entities/Contacto.cs`, `Entities/ContactoRespuesta.cs`, `Entities/IndustriaCatalogo.cs`, `Entities/GoogleMapsQueryUsada.cs` — nuevos, heredan `SoftDestroyable`.

**Application** (`OlvidataCRM.Application`):
- `Settings/WhatsAppSettings.cs`, `Settings/GoogleMapsSettings.cs`, `Settings/BotSettings.cs` — nuevos.
- `DTOs/WhatsAppDtos.cs` (`TemplateComponent`/`TemplateParameter`/`SendMessageResult`, contrato de wire de plantillas Meta expuesto a Negocio), `DTOs/IncomingMessageDto.cs`, `DTOs/ProspectoDto.cs`, `DTOs/OutboundStatsDto.cs`, `DTOs/ContactoListItemDto.cs` — nuevos.
- `Interfaces/IWhatsAppClient.cs`, `Interfaces/IGoogleMapsService.cs`, `Interfaces/IBotFlowService.cs`, `Interfaces/IOutboundCampaignService.cs` — nuevos. `IGoogleMapsService` agrega `RubrosDisponibles` (propiedad, no estaba en Arquitectura) y `SearchByRubroAsync` (método) respecto al mapa original, para soportar CU-11/HU-08 (búsqueda manual por rubro desde `Bot/Index`) sin que Web dependa de la clase concreta `GoogleMapsService` de Infrastructure — decisión de layering tomada en implementación, no cambia contrato funcional.

**Infrastructure** (`OlvidataCRM.Infrastructure`):
- `Services/WhatsAppApiException.cs`, `Services/WhatsAppClient.cs` — portado desde `BotPublicitario/WhatsApp/WhatsAppClient.cs` sin cambio de lógica de negocio; único cambio real: `IOptions<WhatsAppSettings>` en vez de `Environment.GetEnvironmentVariable`. Se portaron solo `SendTextAsync`/`SendTemplateAsync`/`SendListAsync` (los 3 métodos que consume el bot) — el resto de la superficie legacy (perfil de negocio, `GetTemplatesAsync`, `UploadMediaAsync`) no se portó por no tener consumidor en este alcance (YAGNI, documentado en el propio archivo).
- `Services/GoogleMapsService.cs` — portado desde `BotPublicitario/WhatsApp/GoogleMapsService.cs` (dictionarios `RubrosByDay`/`QueriesByRubro` tal cual). El tracking de queries usadas pasa de `queries_used.txt` a la tabla `GoogleMapsQueryUsada` (reset de rotación = soft-delete de las filas del rubro).
- `Services/BotFlowService.cs` — migrado desde `BotPublicitario/Webhook/BotFlowService.cs`. Misma máquina de estados (`FaseConversacion`) y textos de conversación. Cambios respecto al legacy, todos documentados en comentarios del propio archivo:
  - Persiste contra `Contacto`/`ContactoRespuesta` vía `AppDbContext` en vez de `ConversationStore` (JSON).
  - **Agrega el cálculo automático de presupuesto (CU-04)**, que el `BotFlowService` legacy real *no implementaba* (esa pieza estaba solo analizada en `docs/meta-ads/`, nunca escrita en código — se verificó leyendo el archivo fuente). Se agregó `ResolveIndustriaCatalogoAsync` + `UsuariosIncluidosPorPlan` (Starter=1/Pro=2/Premium=3/Scale=ilimitado, +USD100/año por usuario excedente, según la tabla de `docs/meta-ads/definiciones/1-analista-funcional.md`).
  - **Mapeo rubro-conversación → `IndustriaCatalogo`**: el menú de 8 rubros del bot (`IndustryNames`) y los `businessType` de outbound no coinciden textualmente con los nombres de las 13 industrias reconciliadas del seed. Se agregó un diccionario `IndustryToCatalogoNombre` documentado en el código con la decisión explícita: `"Farmacia"` y `"Contabilidad / Estudios contables"` (usados en el flujo outbound) no tienen fila propia en las 13 industrias reconciliadas → no cotizan automático, quedan `DerivadoManual` (mismo criterio que "a medida / rubro sin precedente" del análisis original). **Riesgo/supuesto a confirmar con el cliente, ver §6.**
- `Services/OutboundCampaignService.cs` — migrado desde `BotPublicitario/WhatsApp/OutboundCampaignService.cs`. Mismo cronograma (`RunDayByType`) y mismos textos/dolor por rubro (`Plural`/`PainByType`/`SocialProofByType`, portados tal cual). Opera sobre `IQueryable<Contacto>` en vez de `CampaignState` JSON; `contacted_phones.txt` desaparece (índice único `Contacto.Telefono`).
- `HostedServices/OutboundSchedulerService.cs` — portado desde `BotPublicitario/Webhook/OutboundSchedulerService.cs` como `IHostedService`, mismo horario (Mar/Mié/Jue 09:30 ART), arranca en standby (`IsStandby = true`) igual que legacy. Orquesta búsqueda Google Maps → alta de `Contacto` (con manejo de `DbUpdateException` por carrera en el índice único de teléfono) → `SendDailyBatchAsync`/`ProcessFollowUpsAsync`/`MarkColdAsync`.
- `Data/AppDbContext.cs` — agregados 4 `DbSet` + Fluent API (índice único `Contacto.Telefono`, FK cascade `ContactoRespuesta.ContactoId`, `HasPrecision(18,2)` en montos, `HasConversion<int>()` en los 3 enums nuevos + `Plan`).
- `Data/SeedData.cs` — agregado `SeedIndustriasCatalogoAsync` (idempotente, `IgnoreQueryFilters().AnyAsync()`), siembra las 13 industrias de `docs/meta-ads/definiciones/1-analista-funcional.md` ("Fuente de precios — reconciliada").
- `DependencyInjection.cs` — agregados `Configure<WhatsAppSettings/GoogleMapsSettings/BotSettings>`, `AddHttpClient<IWhatsAppClient,...>`/`AddHttpClient<IGoogleMapsService,...>`, `AddScoped<IBotFlowService,...>`/`AddScoped<IOutboundCampaignService,...>`, `AddHostedService<OutboundSchedulerService>()`.

**Web** (`OlvidataCRM.Web`):
- `Controllers/ContactosController.cs` (`RequireVendedor`) — Index/GetData (DataTable server-side, filtro por Rubro/Canal/Estado/rango de fecha = columnas visibles), Details, Create, Edit, `CambiarEstado` (acción con policy `RequireAdministracion` adicional — Vendedor no puede cambiar estado manual, según Diseño §4), `GuardarNotas`.
- `Controllers/IndustriasController.cs` (`RequireAdministracion`) — CRUD directo sobre `IRepository<IndustriaCatalogo>` (sin service intermedio, según Arquitectura), con `Delete` (soft-delete) agregado (no estaba explícito en Diseño pero es consistente con el patrón de catálogos del estudio y con `SoftDestroyable`).
- `Controllers/BotController.cs` (`RequireAdministracion`) — Index (stats + standby + rubros disponibles), `TogglePausa`, `BuscarProspectos` (CU-11/HU-08 — no estaba dibujado en el wireframe ASCII de Diseño pero es un criterio de aceptación explícito de HU-08, se agregó como formulario simple en `Bot/Index`).
- `Models/ContactoViewModels.cs`, `Models/IndustriaCatalogoViewModels.cs`, `Models/BotOutboundViewModels.cs` — ViewModels con DataAnnotations en español argentino.
- `Views/Contactos/{Index,Details,Create,Edit}.cshtml`, `Views/Industrias/{Index,Create,Edit}.cshtml`, `Views/Bot/Index.cshtml` — Design System (`ov-card`, `ov-badge` con color por `EstadoEmbudo`, DataTables server-side, Select2 con `tags:true` para Rubro en Create/Edit de Contacto, daterangepicker en filtro de fecha, SweetAlert2 para confirmación de `CambiarEstado`/`Delete`/`TogglePausa`).
- `Webhook/WebhookModels.cs` — modelos crudos del payload de Meta, portados desde `BotPublicitario/Webhook/Models.cs` (solo lo necesario para mensajes/estados, sin `referral` — no forma parte de este alcance).
- `Program.cs` — agregado el webhook de Meta como Minimal API (`GET`/`POST /webhook/whatsapp`), sin `[Authorize]` ni policy de rate limiting, ACK inmediato + procesamiento fire-and-forget con deduplicación en memoria por `message_id` (mismo `HashSet` en memoria que el legacy, limitación conocida y aceptada — ver Arquitectura §5).
- `Views/Shared/_Layout.cshtml` — sidebar: sección "Comercial" (Contactos, visible Vendedor+) y "Industrias"/"Bot / Outbound" bajo "Sistema" (visible Administrador+).
- `appsettings.json` — agregadas secciones `Olvidata_WhatsApp`, `Olvidata_GoogleMaps`, `Olvidata_Bot` (vacías/placeholder, mismo patrón que `Olvidata_Email`).

### 4. Migración EF aplicada

`AddContactosYCatalogoIndustrias` (`OlvidataCRM.Infrastructure/Data/Migrations/20260717141923_AddContactosYCatalogoIndustrias.cs`). Agrega 4 tablas (`Contactos`, `ContactoRespuestas`, `IndustriasCatalogo`, `GoogleMapsQueryUsadas`) con sus índices (único en `Contactos.Telefono`, `Contactos.EstadoEmbudo`, `Contactos.CanalOrigen`, `ContactoRespuestas.ContactoId`, `GoogleMapsQueryUsadas.Rubro`). No modifica ninguna tabla existente (verificado leyendo el archivo de migración generado). Aplicada contra `olvidatacrm_dev` (`localhost:3306`) con `dotnet ef database update`. Confirmado con `dotnet ef migrations list`:
```
20260715005143_InitialCreate
20260717141923_AddContactosYCatalogoIndustrias
```
Ambas sin marca `(Pending)` → aplicadas correctamente.

### 5. Evidencia de build

`dotnet build OlvidataCRM.slnx` (incluye compilación de Razor views): **Compilación correcta, 0 Errores**, 8 warnings — todos preexistentes y ajenos a este alcance (`NU1902` MailKit/MimeKit, `CS0114` `HomeController.StatusCode`, ya documentados en la entrada de bootstrap técnico). Build ejecutado también en checkpoints intermedios (tras Infrastructure, tras Web) durante la implementación, todos en verde.

### 6. Riesgos y supuestos (nuevos, específicos de esta implementación)

- **Reconciliación rubro-conversación ↔ catálogo de precios (el más relevante para QA/negocio):** el menú de calificación del bot (8 opciones + outbound) no mapea 1:1 con las 13 industrias reconciliadas de `docs/meta-ads`. Se documentó en código (`BotFlowService.IndustryToCatalogoNombre`) la decisión de que "Farmacia" y "Contabilidad/Estudios contables" (ambos alcanzables solo vía outbound, no vía el menú inbound) no cotizan automático en esta iteración. **Recomendado: validar con Joaquín si esos 2 rubros deberían mapear a alguna de las 13 filas existentes (ej. Farmacia→Retail) en vez de derivar siempre a manual.**
- **Presupuesto automático es funcionalidad nueva, no una migración 1:1:** el `BotFlowService` real de BotPublicitario nunca calculaba ni enviaba presupuesto por WhatsApp (solo calificaba y cerraba con "Joaquín te contacta"). Esa pieza se construyó en esta sesión siguiendo el Diseño (CU-04), no existía código previo que migrar. Requiere prueba funcional dedicada, no solo regresión.
- **CU-11/HU-08 (búsqueda manual Google Maps) no tenía wireframe dibujado en Diseño** — se implementó como formulario simple (select de rubro + botón) dentro de `Bot/Index`, siguiendo el criterio de aceptación de HU-08 pero sin wireframe previo a validar visualmente con el cliente.
- **Deduplicación de webhook por reintentos de Meta:** limitación conocida heredada (HashSet en memoria, no persistente, no sobrevive restart ni escala a múltiples instancias) — aceptada explícitamente en Arquitectura, no se resolvió preventivamente.
- **Credenciales reales de Meta/Google Maps no configuradas:** `Olvidata_WhatsApp`/`Olvidata_GoogleMaps`/`Olvidata_Bot` quedaron con placeholders vacíos en `appsettings.json`. Sin `AccessToken`/`ApiKey`/`VerifyToken` reales, el webhook, el bot y la búsqueda de prospectos no pueden probarse end-to-end contra la API real de Meta/Google — solo la UI/CRUD del CRM (Contactos, Industrias, Bot/Outbound) es testeable sin credenciales.
- **`OutboundSchedulerService` arranca en `Standby=true`** (mismo default que legacy) — no va a enviar mensajes reales hasta que un Administrador lo active manualmente desde `Bot/Index`.
- **Runbook de corte de producción de BotPublicitario NO ejecutado** (explícitamente fuera de alcance de esta sesión, según instrucción del orquestador) — BotPublicitario sigue operando en producción sin cambios.

### 7. Pruebas mínimas requeridas para QA (base: HU-01 a HU-11 del Diseño)

1. **HU-01/CU-01** — Crear contacto manual en `Contactos/Create`: validar teléfono único (rechazo con link al existente), al guardar aparece en Index con Estado=Pendiente, Canal=Manual.
2. **HU-02/CU-02** — `Contactos/Index`: cada filtro (Rubro, Canal, Estado, rango de fecha, buscador texto libre) filtra correctamente sobre las columnas visibles.
3. **HU-03 a HU-06 (bot de calificación)** — requiere `Olvidata_WhatsApp`/`Olvidata_Bot:VerifyToken` configurados. Simular `POST /webhook/whatsapp` con Postman/curl: mensaje nuevo (arranca `AwaitingCategory`), selección de categoría/rubro, respuestas de calificación, cierre con/sin presupuesto automático (probar un rubro que sí cotiza y uno "Otro rubro"/Farmacia que no), reintento con mismo `message_id` (debe ignorarse).
4. **HU-07/CU-10 (outbound)** — invocar manualmente `IOutboundCampaignService` (fuera del cronograma real) o esperar la ventana Mar/Mié/Jue 09:30 ART con Standby=false: verificar límite diario, follow-up a 7 días, marcado frío a 4 días post-follow-up.
5. **HU-08/CU-11** — `Bot/Index` → "Buscar prospectos por rubro": requiere `Olvidata_GoogleMaps:ApiKey` real; verificar que no duplica por teléfono.
6. **HU-09/CU-12** — `Industrias` CRUD: no permite `CotizaAutomatico=true` sin `PrecioBaseUsd>0`; el cambio de precio se refleja en el próximo cálculo sin redeploy.
7. **HU-10** — `Bot/Index`: Enviados hoy/Pendientes coinciden con los datos reales de `Contactos`; pausar/reanudar requiere confirmación SweetAlert2 y queda en `AuditLog` (verificar en `Audit/Index` como SuperUsuario).
8. **HU-11** — `Contactos/Details`: el selector de estado solo ofrece `DemoSolicitada/DemoRealizada/PropuestaEnviada/Cerrado/Descartado`; Vendedor no ve/puede ejecutar el cambio (solo Administrador+); `Descartado` pide confirmación explícita.
9. **Permisos** — Empleado no tiene acceso a `Contactos`/`Industrias`/`Bot` (ni link en sidebar ni acceso directo por URL); Vendedor accede a Contactos pero no a Industrias/Bot ni a `CambiarEstado`.
10. **Regresión** — Users/Audit/System/Notifications (módulos ya existentes) siguen funcionando igual; sidebar no rompe para roles sin las nuevas secciones.

### 8. Checklist de salida para merge

- [x] Domain/Application/Infrastructure/Web compilan sin errores (`dotnet build OlvidataCRM.slnx` → 0 errores).
- [x] Migración EF generada y aplicada en `olvidatacrm_dev`, confirmada con `migrations list`.
- [x] Seed de 13 industrias implementado (idempotente).
- [x] Sidebar actualizado con nuevos accesos, respaldados por policy en cada controller (defensa en profundidad, estándar 32).
- [x] Design System aplicado (DataTables server-side + filtro por columna visible, Select2, daterangepicker, SweetAlert2, `ov-badge`/`ov-card`).
- [ ] Credenciales reales de Meta WhatsApp/Google Maps — pendiente de configuración por Joaquín antes de QA end-to-end del bot/outbound (no bloquea QA de UI/CRUD).
- [ ] Validar con Joaquín el mapeo rubro→catálogo de precios (riesgo §6) antes de dar por cerrada la cotización automática.
- [ ] QA funcional (HU-01 a HU-11) — pendiente, éste es el hand-off para el agente QA.
- [ ] Runbook de corte de producción de BotPublicitario — explícitamente no ejecutado en esta sesión, queda como tarea operativa posterior.

## Fix de defectos QA major (CRM-001, CRM-004, CRM-006) — 2026-07-17

### 0. Escaneo de reutilización

No aplica (fix puntual sobre código ya existente en este mismo proyecto, no una entidad/flujo nuevo a reutilizar de otro proyecto). Los 3 fixes replican patrones ya resueltos y correctos dentro del propio `OlvidataCRM` (`OutboundSchedulerService.RunPipelineAsync` para CRM-004, `NotificationService`/rol-based lookup ya existente en el sistema para CRM-006).

### 1. Alcance funcional resumido

QA funcional (`docs/crm-olvidata/definiciones/6-qa.md`, catálogo `docs/qa/regresiones-manuales.yml`) detectó 6 defectos sobre la migración de BotPublicitario recién implementada. El cliente pidió resolver ahora los 3 de severidad `major`: **CRM-001** (TogglePausa no genera AuditLog, incumple HU-10 CA2), **CRM-004** (BuscarProspectos no maneja duplicados de teléfono dentro del mismo batch de Google Maps), **CRM-006** (falta el canal in-app/campanita al calificar un lead, HU-05 CA1). Los 3 defectos `minor` (CRM-002, CRM-003, CRM-005) quedan explícitamente fuera de esta pasada.

### 2. Plan de ejecución técnica ejecutado (por etapas)

1. CRM-001 — `BotController.TogglePausa` vuelto `async`, inserta `AuditLog` manual antes del redirect.
2. CRM-004 — `BotController.BuscarProspectos` guarda incrementalmente por prospecto con `try/catch(DbUpdateException)`, mismo patrón que `OutboundSchedulerService.RunPipelineAsync`.
3. CRM-006 — `BotFlowService` inyecta `INotificationService` + `UserManager<ApplicationUser>`, crea notificación in-app a todos los usuarios con rol SuperUsuario/Administrador en el mismo punto donde arma el brief de WhatsApp.
4. Build de la solución completa — OK, 0 errores.

### 3. Cambios por capa

**Web** (`OlvidataCRM.Web`):
- `Controllers/BotController.cs`:
  - `using System.Security.Claims;` y `using System.Text.Json;` agregados.
  - `TogglePausa()`: firma cambiada de `IActionResult` (síncrono) a `async Task<IActionResult>`. Antes de logear/redirect, inserta manualmente un `AuditLog` (`UserId` desde `ClaimTypes.NameIdentifier`, `UserName` desde `User.Identity.Name`, `Action="Update"`, `EntityName="OutboundScheduler"`, `NewValues` = JSON serializado de `{ IsStandby }`, `Timestamp=DateTime.UtcNow`, `IpAddress` desde `HttpContext.Connection.RemoteIpAddress`) y llama a `_db.SaveChangesAsync()`. El toggle en sí (`OutboundSchedulerService.IsStandby`) no cambió — fix aditivo, comportamiento externo ya validado por QA se preserva.
  - `BuscarProspectos(string rubro)`: el `foreach` ahora arma `nuevoContacto` en una variable, agrega a `_db.Contactos` y hace `try { await _db.SaveChangesAsync(); agregados++; } catch (DbUpdateException) { _db.Entry(nuevoContacto).State = EntityState.Detached; }` **dentro** del loop (antes había un único `SaveChangesAsync()` fuera del `foreach`, sin manejo de excepción). El mensaje final (`agregados` contactos nuevos) sigue reflejando correctamente solo los que se persistieron de verdad.

**Infrastructure** (`OlvidataCRM.Infrastructure`):
- `Services/BotFlowService.cs`:
  - `using Microsoft.AspNetCore.Identity;` agregado.
  - Constructor: agregados `INotificationService notifications` y `UserManager<ApplicationUser> userManager` como dependencias nuevas (además de las 4 existentes: `AppDbContext`, `IWhatsAppClient`, `IOptions<BotSettings>`, `ILogger`). Ambas ya estaban registradas en el contenedor DI (`INotificationService` en `DependencyInjection.cs` como Scoped, `UserManager<ApplicationUser>` vía `AddIdentity` en `Program.cs`), no requirió cambios de registro.
  - `SendBriefToAdminAsync`: el mensaje armado para WhatsApp se extrae a una variable `mensaje` y se reutiliza para ambos canales. Se agregó la llamada a `NotifyAdminsInAppAsync(contacto, mensaje)` **antes** del `try/catch` del envío de WhatsApp, para que un fallo de WhatsApp no afecte la notificación in-app y viceversa (canales independientes, según CU-05).
  - Método nuevo `NotifyAdminsInAppAsync(Contacto contacto, string mensaje)`: resuelve destinatarios con `_userManager.GetUsersInRoleAsync(SeedData.RolSuperUsuario)` + `GetUsersInRoleAsync(SeedData.RolAdministrador)`, deduplicados por `Id` (por si un usuario tuviera ambos roles), y llama `_notifications.CreateAsync(userId, "Nuevo lead calificado", mensaje, url: $"/Contactos/Details/{contacto.Id}", icon: "fas fa-user-plus")` una vez por destinatario. Envuelto en `try/catch(Exception)` con log de error — decisión de diseño: un fallo en la creación de la notificación in-app tampoco debe impedir el envío de WhatsApp (simetría con el criterio ya exigido por QA en el sentido inverso). **Decisión de resolución de destinatario** (no existía un "usuario admin único" en Identity, a diferencia de `BotSettings.AdminNotifyPhone` que es un teléfono): se notifica a todos los usuarios con rol `SuperUsuario` o `Administrador`, mismo criterio de alcance que ya usan las policies `RequireAdministracion` de `BotController`/`IndustriasController`.

No se tocó `Domain` ni `Application` — ninguno de los 3 fixes requería contrato/entidad nueva.

### 4. Migraciones EF

Ninguna. Los 3 fixes son de comportamiento (lógica de controller/service), no tocan el modelo de datos.

### 5. Evidencia de build

`dotnet build OlvidataCRM.slnx` desde `C:\Sistemas\olvidatasoft-crm`: **Compilación correcta, 0 Errores**, 9 warnings (los mismos preexistentes ya documentados — `NU1902` MailKit/MimeKit x4 y `CS0114` `HomeController.StatusCode` — ninguno nuevo introducido por estos cambios).

### 6. Riesgos y supuestos

- **CRM-001**: verificable 100% por código y por prueba manual UI (pausar/reanudar + revisar `Audit/Index` como SuperUsuario) — no depende de credenciales externas.
- **CRM-004**: el fix en sí es verificable por código (mismo patrón ya probado en `OutboundSchedulerService`), pero la prueba funcional end-to-end (forzar un duplicado real de teléfono dentro del mismo batch de resultados de Google Maps) sigue **BLOQUEADA** hasta contar con `Olvidata_GoogleMaps:ApiKey` real — mismo riesgo de credenciales ya señalado en la implementación original, QA lo marcó explícitamente como bloqueado en `regresiones-manuales.yml`.
- **CRM-006**: verificable 100% por código y por prueba funcional sin credenciales de WhatsApp reales, simulando `IWhatsAppClient` o inspeccionando directamente la tabla `Notifications`/`Notifications/Index` tras completar un flujo de calificación — la creación de la `Notification` in-app es un INSERT en base de datos, no depende de ninguna API externa (confirmado por QA en la propia entrada CRM-006).
- No se tocó nada de CRM-002/003/005 (fuera de alcance de este pedido) ni de otras partes del código.

### 7. Pruebas mínimas para QA

1. **CRM-001**: Pausar el outbound estando activo → verificar badge "En pausa" en `Bot/Index` + nuevo registro en `Audit/Index` (SuperUsuario) con `EntityName=OutboundScheduler` y `UserName` del usuario autenticado. Repetir para reanudar.
2. **CRM-004**: bloqueada end-to-end sin `Olvidata_GoogleMaps:ApiKey` real (mismo bloqueo que QA ya documentó). Cuando haya credenciales o un doble de prueba de `IGoogleMapsService`: forzar que dos resultados del mismo rubro compartan teléfono normalizado y verificar que la búsqueda completa igual (el duplicado se ignora, no revienta la operación) y que el contador de "agregados" del mensaje final es exacto.
3. **CRM-006**: completar un flujo de calificación del bot (real vía webhook, o simulando `IWhatsAppClient`/invocando `BotFlowService` directamente en un entorno de prueba) y verificar que aparece una `Notification` nueva en la campanita/`Notifications/Index` de cada usuario Administrador/SuperUsuario, con el mismo contenido que el brief de WhatsApp. Verificar también que si `IWhatsAppClient.SendTextAsync` lanza excepción, la notificación in-app igual se crea (canales independientes).

### 8. Checklist de salida para merge

- [x] Los 3 fixes major aplicados (CRM-001, CRM-004, CRM-006), aditivos, sin cambiar comportamiento externo ya validado por QA.
- [x] `dotnet build OlvidataCRM.slnx` → 0 errores.
- [x] Sin migración EF (no aplica).
- [x] CRM-002/003/005 y el resto del código fuera de este alcance, sin tocar.
- [ ] Prueba manual UI de CRM-001 (pausar/reanudar + Audit/Index) — pendiente, hand-off a QA.
- [ ] Prueba funcional de CRM-006 (notificación in-app tras calificación) — pendiente, hand-off a QA.
- [ ] Prueba end-to-end de CRM-004 — sigue bloqueada por falta de `Olvidata_GoogleMaps:ApiKey` real.

## Import de datos reales de BotPublicitario (2026-07-17)

Descargados por FTP (`win8232.site4now.net/whatsappwebhook`) los datos reales de producción y cargados en `olvidatacrm_dev`: 235 prospectos de `outbound_state.json` + 22 conversaciones inbound + 16 queries de Google Maps ya usadas → **238 `Contacto`** creados (19 fusionados entre ambas fuentes por teléfono), sin duplicados (verificado idempotente).

Importador de un solo uso (`LegacyImporter.cs` + branch temporal en `Program.cs`), corrido y **borrado inmediatamente después** — no quedó como funcionalidad permanente, tal como estaba previsto en `3-arquitecto-mvc.md` §5. Detalle completo del mapeo de campos/enums y del hallazgo de un bug real en el `BotFlowService` de producción (lectura de `status` como string cuando el JSON lo serializa como número, rompe silenciosamente el reconocimiento de prospectos outbound) en `trazabilidad.md`, entrada "import de datos reales de producción de BotPublicitario".

No se tocó ningún archivo de configuración con las credenciales de FTP — se usaron una sola vez, en memoria, para la descarga.

## Implementación de campañas de contacto frío configurables (2026-07-21)

### 0. Escaneo de reutilización

No aplica — funcionalidad nueva dentro del propio `OlvidataCRM`, no hay un ABM equivalente en otros proyectos del historial de `/docs/*/definiciones/5-implementador.md`. Se reutilizó el 100% de la infraestructura ya existente en este proyecto (`SoftDestroyable`, `AppDbContext` con auditoría/soft-delete automáticos, Design System, DataTables server-side, patrón de controller sin service intermedio ya usado en `IndustriasController`).

### 1. Alcance funcional resumido

CU-13 (crear campaña), CU-14 (editar/pausar/reanudar), CU-15 (gestionar queries de Google Maps por industria) y HU-12 a HU-16 del Diseño. Reemplazo completo de `OutboundCampaignService.RunDayByType`/`RubrosRetirados`, `GoogleMapsService.RubrosByDay`/`QueriesByRubro` y `BotSettings.DailyLimit` (único) por datos configurables desde el CRM (pantallas `Campanas/Index|Create|Edit`, accedidas desde `Bot/Index`).

### 2. Plan de ejecución técnica ejecutado (por etapas, según plan funcional de Arquitectura §2)

1. Domain: enum `DiasSemana` (flags) + entidades `CampanaOutbound`/`CampanaOutboundIndustria`/`CampanaQuery` — OK.
2. Infrastructure: `AppDbContext` (DbSets + Fluent API), `SeedData` (2 filas nuevas de `IndustriaCatalogo` + `SeedCampanasOutboundAsync`, migración automática de las 13 campañas desde el cronograma/queries anteriores) — OK.
3. Infrastructure: `OutboundCampaignService`/`GoogleMapsService`/`OutboundSchedulerService` migrados a leer de campañas en vez de diccionarios fijos — OK.
4. Web: `CampanasController` (CRUD + 4 endpoints AJAX para industrias/queries), `BotController` extendido, 3 vistas nuevas + extensión de `Bot/Index.cshtml` — OK.
5. Migración EF (`AddCampanasOutbound`) generada y aplicada contra `olvidatacrm_dev` — OK.

### 3. Cambios por capa

**Domain** (`OlvidataCRM.Domain`):
- `Enums/DiasSemana.cs` — nuevo, `[Flags]` (Martes=1, Miercoles=2, Jueves=4).
- `Entities/CampanaOutbound.cs`, `Entities/CampanaOutboundIndustria.cs`, `Entities/CampanaQuery.cs` — nuevos, heredan `SoftDestroyable`. `ClaveRubro` y las `Queries` viven en `CampanaOutboundIndustria` (no en `IndustriaCatalogo`), tal como resolvió Arquitectura §1.a-b.

**Application** (`OlvidataCRM.Application`):
- `IGoogleMapsService`: `RubrosDisponibles` (propiedad sync) → `GetRubrosDisponiblesAsync()` (método async); `SearchDailyAsync` pierde el parámetro `targetTotal`. Único cambio de contrato de esta implementación.

**Infrastructure** (`OlvidataCRM.Infrastructure`):
- `Data/AppDbContext.cs` — 3 `DbSet` nuevos + Fluent API (`Dias` con `HasConversion<int>()`, cascada campaña→industria→query, `Restrict` en industria→`IndustriaCatalogo`).
- `Data/SeedData.cs` — 2 filas nuevas en `SeedIndustriasCatalogoAsync` ("Farmacias", "Estudios contables / jurídicos", `CotizaAutomatico=false`); método nuevo `SeedCampanasOutboundAsync` (idempotente) que migra automáticamente las 13 campañas (Martes: Comercio/Farmacia/Dietéticas — límite 42 c/u; Miércoles: Consultorio/Clínica/Inmobiliaria/Indumentaria/Maquinaria — 25 c/u; Jueves: Estudio/Ganadería/Agro/Servicios/Residuos — 25 c/u), con sus queries de Google Maps migradas 1:1 desde el código anterior.
- `Services/OutboundCampaignService.cs` — eliminados `RunDayByType`/`RubrosRetirados`/`IsScheduledToday`; `SendDailyBatchAsync`/`ProcessFollowUpsAsync` ahora consultan `CampanasActivasHoyAsync()` (campañas con `Activa=true` y `Dias` incluye hoy) y agrupan candidatos por `ClaveRubro`. Template de envío frío = `campana.TemplateWhatsApp`; Referido (`olv_referido_v2`) y follow-up (`olv_nurturing_v2`) quedan fijos, sin depender de la campaña (Arquitectura §1.d). Agregado `TemplatesDisponibles` (lista estática pública, hoy solo `olv_frio_v3`) para que `CampanasController` valide/ofrezca el dropdown.
- `Services/GoogleMapsService.cs` — eliminados `RubrosByDay`/`QueriesByRubro` estáticos (~150 líneas de datos hardcodeados). `GetRubrosDisponiblesAsync` consulta `CampanaOutboundIndustrias` con al menos 1 query. `SearchByRubroAsync` resuelve queries por `ClaveRubro` contra la BD (prioriza campaña activa si hay varias coincidencias). `SearchDailyAsync` itera campañas activas del día y reparte `LimiteDiario` entre sus industrias.
- `HostedServices/OutboundSchedulerService.cs` — quitado `const int targetSends = 125`; llamada a `SearchDailyAsync` sin el parámetro.

**Web** (`OlvidataCRM.Web`):
- `Controllers/CampanasController.cs` — nuevo (`RequireSuperUsuario`). `Index`/`GetData` (DataTable server-side, mismo patrón que `IndustriasController`), `Create`/`Edit` (POST solo para los datos base de la campaña), `TogglePausa`, `Delete` (soft-delete en cascada manual a industrias/queries — necesario porque el query filter global no cascadea automáticamente entre entidades `SoftDestroyable` independientes), y 4 endpoints AJAX (`AgregarIndustria`/`EliminarIndustria`/`AgregarQuery`/`EliminarQuery`) que devuelven JSON `{success, message}` para edición inline sin recargar la página (Diseño §1 Pantalla 8).
- `Controllers/BotController.cs` — `Index` agrega `CampanasResumen`/`CampanasActivas`/`CampanasPausadas` al ViewModel; `RubrosDisponibles`/`BuscarProspectos` actualizados al nuevo `GetRubrosDisponiblesAsync()` async.
- `Models/CampanaOutboundViewModels.cs`, `Models/BotOutboundViewModels.cs` (extendido) — ViewModels con DataAnnotations en español.
- `Views/Campanas/{Index,Create,Edit}.cshtml` — Design System completo (DataTable server-side con filtro de texto libre, SweetAlert2 para pausar/reanudar/eliminar, acordeón Bootstrap para industrias con AJAX inline para queries). `Views/Bot/Index.cshtml` — card nueva "Campañas de contacto frío" con resumen y link a `Campanas/Index`.

**Desviación menor respecto al wireframe de Diseño (documentada, no bloqueante):** la Pantalla 7 (Create) del Diseño mostraba el selector de industrias ya en el alta. Se implementó Create solo con los datos base de la campaña (nombre/días/límite/template) — las industrias y sus queries se agregan en Edit vía AJAX inmediatamente después de crear. Motivo: una `CampanaOutboundIndustria` necesita un `CampanaOutboundId` real para persistirse (no se puede crear "en el aire" antes de guardar la campaña), y el propio Diseño ya preveía el flujo "Guardar y cargar queries →" con redirect a Edit — esta implementación simplemente mueve también la selección de industrias a ese mismo paso posterior, en vez de dividirlo en dos formularios distintos.

### 4. Migración EF aplicada

`AddCampanasOutbound` (`OlvidataCRM.Infrastructure/Data/Migrations/20260721155711_AddCampanasOutbound.cs`). Agrega 3 tablas (`CampanasOutbound`, `CampanaOutboundIndustrias`, `CampanaQueries`). No modifica tablas existentes. Aplicada contra `olvidatacrm_dev` con `dotnet ef database update`; confirmado con `dotnet ef migrations list` (3 migraciones, ninguna `(Pending)`).

### 5. Evidencia de build y seed

`dotnet build OlvidataCRM.slnx` → **Compilación correcta, 0 errores**, 4 warnings preexistentes (`NU1902` MailKit/MimeKit, ajenos a este alcance), confirmado en 2 corridas (antes y después de generar la migración). `dotnet run` (20 seg, `--no-build`) arrancó sin errores: scheduler inicializado en `Standby=True` (default legacy preservado), log confirma `"Campañas de contacto frío sembradas: 13"` en la primera corrida tras aplicar la migración — sin excepciones durante el seed (mapeo de rubros→industria, distribución del límite diario y migración de queries corrieron sin errores). Segunda corrida no vuelve a sembrar (idempotencia verificada, mismo patrón que `SeedIndustriasCatalogoAsync`).

### 6. Riesgos y supuestos

- **Riesgo heredado de Arquitectura, sin mitigar (por decisión del cliente):** sin tope global de límite diario — la suma de las campañas activas puede superar cualquier valor sin aviso.
- **Farmacia/Estudio dependen de las 2 filas nuevas de catálogo:** si en el futuro se edita/elimina "Farmacias" o "Estudios contables / jurídicos" desde `Industrias/Edit` sin saber que están ancladas a una campaña, esa campaña queda con `IndustriaCatalogoId` apuntando a una fila soft-deleted (no rompe nada — el campo es nullable y solo se usa para mostrar el nombre — pero el `Nombre` mostrado en `Campanas/Index` quedaría vacío para esa industria). No se agregó protección adicional (no estaba en el alcance aprobado).
- **No se probó end-to-end el envío real de WhatsApp ni la búsqueda real de Google Maps** — mismo bloqueo de siempre en este proyecto (credenciales reales configuradas por Joaquín, pero el scheduler sigue en `Standby=true`; no se activó). La lógica de selección de candidatos/campañas se verificó por revisión de código, no por ejecución real del pipeline.
- **Cambio de contrato en `IGoogleMapsService`:** `RubrosDisponibles` (sync) → `GetRubrosDisponiblesAsync()` (async). Único consumidor revisado y actualizado: `BotController`. Si existiera algún otro consumidor fuera de este repo (no lo hay), rompería en compilación, no en runtime.

### 7. Pruebas mínimas requeridas para QA

1. **CU-13** — `Campanas/Create`: crear campaña sin elegir ningún día → rechaza con mensaje. Crear una válida → redirige a Edit.
2. **CU-13 (industrias)** — En Edit, agregar una industria con una `ClaveRubro` ya usada por otra campaña **activa** → rechaza. Agregarla en una campaña pausada → permite (la regla es solo contra campañas activas).
3. **CU-15** — Agregar/quitar queries de una industria vía AJAX sin recargar la página; el contador de queries del acordeón se actualiza.
4. **CU-13 (activar)** — Intentar activar (`Activa=true`, vía Edit o `TogglePausa`) una campaña sin industrias, o con una industria sin queries → rechaza con mensaje explícito señalando qué falta.
5. **HU-12** — `Bot/Index` muestra el conteo de campañas activas/pausadas y el resumen; el link "Ver campañas" navega a `Campanas/Index`.
6. **Regresión CU-10/CU-11** — invocar manualmente `IOutboundCampaignService`/`IGoogleMapsService` (o esperar la ventana real con `Standby=false`) contra las 13 campañas migradas: verificar que el cronograma por día sigue siendo el mismo que antes de esta implementación (mismo comportamiento observable, aunque la fuente de datos cambió).
7. **Eliminar campaña** — soft-delete en cascada: verificar que sus industrias/queries también quedan con `DeletedAt` seteado (no solo la campaña) y que `GetRubrosDisponiblesAsync`/`SearchByRubroAsync` ya no las devuelven.

### 8. Checklist de salida para merge

- [x] Domain/Application/Infrastructure/Web compilan sin errores (`dotnet build` → 0 errores, 2 corridas).
- [x] Migración EF generada y aplicada en `olvidatacrm_dev`, confirmada con `migrations list`.
- [x] Seed de migración automática (13 campañas + 2 industrias nuevas) ejecutado sin errores, idempotencia verificada.
- [x] Design System aplicado (DataTables server-side, SweetAlert2, acordeón + AJAX inline, `ov-card`/`ov-badge`).
- [x] Policy `RequireSuperUsuario` aplicada al controller nuevo, consistente con el resto del sistema.
- [ ] QA funcional (CU-13/14/15, HU-12 a HU-16) — pendiente, éste es el hand-off para el agente QA.
- [ ] Prueba end-to-end real del pipeline outbound con campañas — sigue bloqueada mientras el scheduler esté en `Standby=true` (decisión operativa de Joaquín, no de esta implementación).

## Ajuste UI — ícono y confirmación SweetAlert2 en eliminar notificaciones (2026-07-25)

### 0. Escaneo de reutilización

No aplica desarrollo desde cero — es un ajuste puntual de presentación sobre una vista ya existente y funcionando (`Views/Notifications/Index.cshtml`), con el patrón de confirmación a copiar ya identificado explícitamente en el pedido y verificado en código real: `Views/Campanas/Index.cshtml` (`$('#campanasTable').on('click', '.btn-delete', ...)`, `Swal.fire({icon:'warning', showCancelButton:true, confirmButtonColor:'#ef4444'}).then(...)`). Se replicó ese mismo patrón textual (colores, textos de botones, estructura del `.then()`), adaptado a interceptar el `submit` de un `<form>` en vez de un click de botón dentro de una tabla, porque acá no hay DataTable de por medio, son 2 forms simples server-rendered.

### 1. Alcance funcional resumido

Ajuste 100% de Vista sobre `Notifications/Index.cshtml`, sin tocar Negocio ni Datos: (1) ícono `fas fa-trash` → `fas fa-xmark` en el botón de eliminar individual (dentro del `foreach` de notificaciones) y en el botón "Eliminar leídas" del header; (2) reemplazo del `confirm()` nativo (`onsubmit="return confirm(...)"` inline en ambos `<form>`) por un modal SweetAlert2, manejado desde una sección `Scripts` nueva (la vista no tenía ninguna hasta ahora). `NotificationsController.Delete(id)`/`DeleteAllRead()` (POST) no se tocaron — ya existían y funcionaban de una sesión anterior del mismo día.

### 2. Plan de ejecución técnica ejecutado

1. Cambio de clase del ícono en los 2 `<i>` (`fas fa-trash` → `fas fa-xmark`), sin tocar clases del `<button>` padre ni el texto de "Eliminar leídas" — OK.
2. Se sacó el `onsubmit="return confirm(...)"` de ambos `<form>` y se agregó `class="form-delete-notif"` al form individual y `class="form-delete-all-read"` al form de lote, para poder targetearlos por selector CSS desde JS — OK.
3. Se agregó `@section Scripts { ... }` al final del archivo (nueva, no existía) con 2 handlers `$(document).on('submit', '.form-delete-notif' / '.form-delete-all-read', function(e) {...})`: cada uno hace `e.preventDefault()`, captura `var form = this;` (el form nativo, no el wrapper jQuery, para poder llamar `form.submit()` sin volver a disparar el listener), muestra `Swal.fire({icon:'warning', title, [text], showCancelButton:true, confirmButtonText:'Sí, eliminar', cancelButtonText:'Cancelar', confirmButtonColor:'#ef4444'})` y en `.then(result => { if (result.isConfirmed) form.submit(); })` — mismo patrón exacto de `Campanas/Index.cshtml` — OK.
4. Build de la solución completa — OK, 0 errores.

### 3. Cambios por capa

**Web** (`OlvidataCRM.Web`) — único archivo tocado:
- `Views/Notifications/Index.cshtml`:
  - Línea del botón "Eliminar leídas": `<form>` pierde `onsubmit="..."`, gana `class="form-delete-all-read"`; ícono `fas fa-trash me-1` → `fas fa-xmark me-1`.
  - Línea del botón eliminar individual (dentro del `foreach`): `<form>` pierde `onsubmit="..."`, gana `class="form-delete-notif"`; ícono `fas fa-trash` → `fas fa-xmark`.
  - Nueva `@section Scripts { <script> $(function(){ ... }); </script> }` al final del archivo, con los 2 handlers de `submit` descriptos arriba.
- Nada tocado en Domain/Application/Infrastructure (`NotificationsController`, `INotificationService`/`NotificationService` intactos, sin cambios de firma ni de comportamiento).

### 4. Migración EF

Ninguna — no se tocó el modelo de datos ni el esquema.

### 5. Evidencia de build

`dotnet build OlvidataCRM.slnx` desde `C:\Sistemas\olvidatasoft-crm`: **Compilación correcta, 0 Errores**, 9 warnings — todos preexistentes (`NU1902` MailKit/MimeKit x4, `CS0114` `HomeController.StatusCode`), ninguno nuevo introducido por este cambio. Sin smoke test funcional propio (regla del estudio) — revisión de código línea por línea del archivo modificado hecha como evidencia de cierre (ver guía de prueba manual en la entrada de trazabilidad).

### 6. Riesgos y supuestos

- Cambio puramente cosmético/UX sobre una funcionalidad ya probada — el riesgo técnico es mínimo (no hay lógica de negocio nueva).
- Se usó `$(document).on('submit', '.clase', ...)` (delegado) en vez de `$('.clase').on('submit', ...)` directo — importa poco en esta vista porque los forms no se recrean dinámicamente (no hay DataTable acá), pero es el patrón más robusto y consistente con el resto del proyecto.
- Supuesto: SweetAlert2/jQuery/Font Awesome 6.5.1 ya cargados globalmente en `_Layout.cshtml` antes del `@RenderSectionAsync("Scripts", required: false)` (línea 258) — verificado leyendo el layout antes de escribir el script, no se agregó ningún script/CDN nuevo.

### 7. Pruebas mínimas requeridas para QA

1. Ver `Notifications/Index` con al menos 1 notificación leída y 1 no leída: confirmar que el ícono de "Eliminar" (individual) y de "Eliminar leídas" (header) se ve como una X (`fa-xmark`), no una papelera.
2. Click en "Eliminar" de una notificación individual → aparece modal SweetAlert2 (`warning`, título "¿Eliminar esta notificación?", botones "Sí, eliminar"/"Cancelar"). Cancelar no elimina nada (recargar y verificar que sigue la notificación). Confirmar sí la elimina (recarga y desaparece de la lista).
3. Con al menos 1 notificación leída, click en "Eliminar leídas" → modal con título "¿Eliminar todas las notificaciones leídas?" y texto "Esta acción no se puede deshacer.". Cancelar no elimina nada. Confirmar elimina todas las leídas (las no leídas quedan intactas).
4. Verificar que no aparece ningún `confirm()` nativo del navegador (el gris feo de Chrome/Edge) en ninguno de los 2 flujos.
5. Regresión: "Marcar todas leídas" y "Marcar leída" (individual) siguen funcionando igual que antes (no se tocaron, pero comparten la misma vista).

### 8. Checklist de salida para merge

- [x] Único archivo tocado: `Views/Notifications/Index.cshtml` (Presentación).
- [x] Sin cambios en Controllers/Services/Domain.
- [x] `dotnet build OlvidataCRM.slnx` → 0 errores, sin warnings nuevos.
- [x] Sin migración EF (no aplica).
- [x] Patrón SweetAlert2 replicado de `Campanas/Index.cshtml` (mismo `confirmButtonColor`, mismos textos de botones).
- [ ] Prueba manual de usuario (ícono + modal, ver guía de QA arriba) — pendiente, hand-off al usuario/cliente.

## Implementación de gestión comercial y herramientas de canal/venta (2026-08-16)

### 0. Escaneo de reutilización

Se escanearon los `5-implementador.md` de los 20 proyectos de `docs/`. Resultado: **nada reutilizable a nivel entidad/servicio para el núcleo de este alcance.** Existe una entidad `Cliente` en `ShowroomGriffin`, `la-platense`, `marihogar` y `vino-y-se-fue`, pero es un cliente de venta de mostrador (cuenta corriente, condición de IVA, facturación AFIP) — dominio distinto del `Cliente` de este CRM (contacto que cerró, con plan, ticket anual, renovación y NRR). No hay en ningún proyecto `Upsell`, cálculo de NRR, catálogo de templates de WhatsApp, experimento A/B ni pipeline kanban. Sí se reutilizaron **patrones internos del propio proyecto** (criterio de "no desarrollar desde cero" aplicado hacia adentro): DataTables server-side con whitelist de orden por índice de columna (`IndustriasController`/`ContactosController`), acciones AJAX con respuesta JSON (`CampanasController`), confirmación SweetAlert2 (`Industrias/Index`), `ov-stat-card` (`Bot/Index`), y el modal Bootstrap + partial compartido para no duplicar el alta de cliente entre `Contactos/Details` y `Chats/Detail`.

### 1. Alcance funcional resumido

CU-21 a CU-29 (`1-analista-funcional.md`), 8 piezas: `Cliente`, `Upsell`, dashboard de negocio, dashboard de campañas, catálogo de templates, A/B testing, asistente de redacción y pipeline visual. 5 entidades nuevas + 1 enum + 1 campo en `ContactoRespuesta`, 1 migración EF, 3 controllers nuevos y 3 extendidos.

### 2. Plan de ejecución técnica ejecutado (por etapas)

1. Domain: 5 entidades + `EstadoAprobacionMeta` + `ContactoRespuesta.VarianteExperimento`.
2. Application: `NegocioStatsDto`, `CampanaStatsDto`, `NegocioSettings`.
3. Infrastructure: `AppDbContext` (5 `DbSet` + configuración), split A/B en `OutboundCampaignService`, registro de `NegocioSettings` en DI.
4. Web: 5 grupos de ViewModels, `ClientesController`/`NegocioController`/`TemplatesController` nuevos, `CampanasController`/`ContactosController`/`ChatsController` extendidos, 9 vistas nuevas y 7 modificadas.
5. Build → migración `AddGestionComercial` → aplicación en dev → smoke test autenticado local → aplicación en producción por SQL directo → deploy.

### 3. Cambios por capa

- **Domain**: `Cliente.cs`, `Upsell.cs`, `TemplateWhatsApp.cs`, `CampanaExperimento.cs`, `SugerenciaSeguimiento.cs`, `Enums/EstadoAprobacionMeta.cs` (nuevos); `ContactoRespuesta.cs` (+`VarianteExperimento`).
- **Application**: `DTOs/NegocioStatsDto.cs`, `DTOs/CampanaStatsDto.cs`, `Settings/NegocioSettings.cs` (nuevos). Sin interfaces nuevas ni cambios de firma en las existentes (`IWhatsAppClient`/`IOutboundCampaignService` intactas), según Arquitectura §2.
- **Infrastructure**: `AppDbContext.cs` (5 `DbSet` + configuración de precisión/longitudes/FK: `Cascade` en `Upsell`→`Cliente` y `CampanaExperimento`→`CampanaOutbound`, `Restrict` en los 2 FK a `TemplateWhatsApp` y en `Cliente`→`Contacto`); `OutboundCampaignService.cs` (split A/B con semilla determinística por contacto + baja de la lista fija `TemplatesDisponibles`); `DependencyInjection.cs` (`NegocioSettings`).
- **Web**: controllers `ClientesController.cs`, `NegocioController.cs`, `TemplatesController.cs` (nuevos); `CampanasController.cs` (+`Dashboard`, +`ConfigurarExperimento`, selector de template desde BD), `ContactosController.cs` (+`Pipeline`, +`ClienteId` en `Details`), `ChatsController.cs` (+`SugerirMensaje`, +`ClienteId` en `Detail`). ViewModels: `ClienteViewModels.cs`, `NegocioViewModels.cs`, `TemplateWhatsAppViewModels.cs`, `CampanaDashboardViewModels.cs`, `PipelineViewModels.cs` (nuevos) + campos en `ContactoViewModels`/`ChatViewModels`/`CampanaOutboundViewModels`. Vistas nuevas: `Clientes/Index|Details|Edit`, `Negocio/Dashboard`, `Templates/Index|Create|Edit`, `Campanas/Dashboard`, `Contactos/Pipeline`, `Shared/_ConvertirClienteModal`. Vistas modificadas: `Shared/_Layout` (sección "Negocio"), `Contactos/Details`, `Contactos/Index`, `Chats/Detail`, `Campanas/Edit`, `Campanas/Index`, `Bot/Index`.
- **Config**: `appsettings.json` → `Olvidata_Negocio:MetaAnualUsd` (default 0 = "meta no configurada").

### 4. Migración EF aplicada

`20260817003040_AddGestionComercial` — 5 tablas (`Clientes`, `Upsells`, `TemplatesWhatsApp`, `CampanasExperimento`, `SugerenciasSeguimiento`) + 1 columna aditiva (`ContactoRespuestas.VarianteExperimento varchar(1) NULL`). Sin `defaultValue` en ninguna columna de fecha/hora (problema conocido de DDL inválido con este proveedor MySQL). Aplicada en dev con `dotnet ef database update`; en producción por SQL directo generado con `dotnet ef migrations script` + su `INSERT` en `__EFMigrationsHistory`, sin correr `database update` contra la base productiva.

Migración de **datos** (no de código, según Arquitectura §3): 1 fila en `TemplatesWhatsApp` (`olv_frio_v3`, `EstadoAprobacionMeta=Aprobado`, `Activo=1`) en dev y producción, para que las campañas ya cargadas (85 activas en producción, todas con `olv_frio_v3`) no queden sin template válido el día del corte. Además, 6 filas de `SugerenciasSeguimiento` — ver riesgos.

### 5. Evidencia de build y pruebas

- `dotnet build -c Release` → **0 errores** (13 warnings, todos preexistentes). Las vistas Razor compilan en build en este proyecto (verificado a propósito introduciendo un error deliberado en una vista y confirmando que la compilación falla).
- Smoke test **autenticado** local (dev, HTTPS, sesión real por cookie): 200 en `/Clientes`, `/Negocio/Dashboard`, `/Templates`, `/Templates/Create`, `/Campanas/Dashboard`, `/Contactos/Pipeline`, `/Contactos/Details/{id}`, `/Chats/Detail/{id}`, `/Campanas/Edit/{id}`, `/Campanas/Create`, más los flujos POST reales: conversión Contacto→Cliente (302 a la ficha del cliente), alta de upsell (JSON OK), alta de template, alta de experimento A/B y su validación de A=B (rechazada, base sin cambios), y `SugerirMensaje` devolviendo el texto correcto con placeholders resueltos.
- Verificación numérica del NRR contra datos de prueba: base 1200 + upsell 300 → 125%; con el cliente dado de baja → 25%; sin período anterior → "Datos insuficientes". Los datos de prueba se borraron de dev al terminar.
- Producción: deploy Web Deploy exitoso al primer intento, `https://portal.olvidata.com.ar/` → 200, y las 5 rutas nuevas → 302 (redirect a login, rutas vivas).

### 6. Riesgos y supuestos

- **Bug encontrado y corregido durante la propia implementación:** el churn del NRR se comparaba tomando `.Date` directo sobre `UpdatedAt` (UTC) contra días calendario argentinos — una baja cargada después de las 21hs ART caía en el día UTC siguiente, quedaba fuera del período y el NRR salía inflado (125% en vez de 25% en la prueba). Corregido pasando por `ArgentinaTime.From()` antes de truncar. Es el mismo tipo de bug ya documentado en `ArgentinaTime`, reaparecido en código nuevo.
- **No hay campo de fecha de churn en el modelo aprobado.** El churn se marca con `Activo=false` y se fecha con el stamping de auditoría (`UpdatedAt`) como proxy: si un cliente dado de baja se edita después por otro motivo, su fecha de churn se corre a esa edición. Con la cartera actual (decenas de filas) es aceptable; si se vuelve un problema, hace falta un campo propio y una migración.
- **`SugerenciaSeguimiento` no tiene pantalla de mantenimiento** — ni el Diseño ni la Arquitectura definen una, y tampoco definen el contenido del catálogo. Se cargaron 6 filas genéricas como borrador para que el botón "Sugerir" no nazca inerte; hoy solo son editables por SQL. Los textos necesitan revisión del cliente (o de `olvidata-marketing`) antes de considerarse definitivos.
- **`AvanceMeta` no tiene valor definido en ninguna definición.** Se implementó como setting (`Olvidata_Negocio:MetaAnualUsd`), default 0 → la card muestra "Meta no configurada" en vez de inventar un porcentaje.
- **El split A/B no se probó con envíos reales** (implicaría mandar WhatsApp de verdad a contactos reales). La lógica está verificada por lectura: `new Random(contacto.Id)` es determinístico por contacto, así que un reintento no cambia de variante.
- **`Pais` del dashboard de campañas** se infiere de `ZonaHoraria` (mapa fijo de 7 zonas) y cae a `Region` si no matchea — riesgo ya asumido en Arquitectura §7.
- Todos los cruces contacto↔campaña y el cálculo de NRR se resuelven **en memoria** (`ToListAsync()` primero), nunca con `Contains()` sobre una colección local dentro de una query — el proveedor MySQL de este proyecto no lo traduce.

### 7. Pruebas mínimas requeridas para QA

1. `Contactos/Details` de un contacto en estado distinto de Cerrado: **no** debe verse el botón "Convertir en Cliente". Cambiar el estado a Cerrado → aparece.
2. Convertir un contacto Cerrado: el modal precarga fecha de alta = hoy y renovación = hoy + 1 año; cambiar la fecha de alta debe mover la renovación sola, salvo que ya se haya editado a mano. Al guardar redirige a `Clientes/Details`. Volver a `Contactos/Details` → ahora muestra "Ver cliente".
3. Intentar convertir dos veces el mismo contacto → error "ya tiene un cliente activo asociado" y redirección al cliente existente.
4. `Clientes/Index`: filtros por plan, estado y vencimiento; semáforo rojo (<30 días), ámbar (<90) y verde. Ordenar por cada columna.
5. `Clientes/Details`: alta de upsell sin recargar la página, actualización de "Upsells acumulados" y "Valor total"; eliminar un upsell con confirmación y ver que los totales bajan.
6. `Negocio/Dashboard`: con cartera vacía, NRR = "Datos insuficientes" (no 0%). Con clientes de más de un año y upsells, verificar el porcentaje a mano. Dar de baja un cliente y confirmar que el NRR baja.
7. `Templates`: alta de un template Borrador → **no** debe aparecer en el selector de `Campanas/Create`. Pasarlo a Aprobado + Activo → aparece. Intentar borrar un template usado por una campaña activa → bloqueado con mensaje.
8. `Campanas/Edit`: con menos de 2 templates aprobados, la card A/B avisa que faltan templates. Con 2, guardar un experimento 70/30, verificar el badge del header. Intentar A = B → rechazado.
9. `Campanas/Dashboard`: contrastar la tasa de respuesta de alguna campaña contra el mismo dato filtrado en `Contactos/Index`.
10. `Contactos/Pipeline`: los conteos por columna deben coincidir con el resumen de embudo de `Contactos/Index`; el link "Ver los N" de una columna debe abrir el listado ya filtrado por ese estado.
11. `Chats/Detail`: botón "Sugerir" prellena el textarea sin enviar nada; con texto ya escrito pide confirmación antes de pisarlo; en un contacto sin sugerencia aplicable avisa "Sin sugerencia disponible".
12. Regresión del outbound: con una campaña **sin** experimento activo, el envío diario debe comportarse igual que antes (mismo template configurado, `VarianteExperimento` nulo en `ContactoRespuestas`).

### 8. Checklist de salida para merge

- [x] `dotnet build -c Release` → 0 errores, sin warnings nuevos.
- [x] Migración `AddGestionComercial` generada, aplicada en dev y en producción (producción por SQL directo + `INSERT` manual en `__EFMigrationsHistory`).
- [x] Datos de arranque cargados en ambas bases (`olv_frio_v3` + 6 sugerencias), verificados con acentos correctos (utf8mb4).
- [x] Lógica de negocio en controllers/servicios, no en vistas; sin lógica nueva en Controllers que corresponda a un Service (se siguió el criterio explícito de Arquitectura §2 de no crear una capa de servicio para NRR/métricas).
- [x] Design system aplicado: DataTables server-side, SweetAlert2 en todas las confirmaciones, `ov-card`/`ov-stat-card`/`ov-badge`, sin CDNs nuevos.
- [x] Smoke test autenticado de las 11 pantallas/endpoints nuevos en dev + verificación de rutas en producción.
- [x] Deploy a producción por Web Deploy (nunca FTP), `https://portal.olvidata.com.ar/` → 200.
- [ ] QA funcional completo (ver guía arriba) — pendiente, hand-off al cliente.
- [ ] Revisión de los textos de `SugerenciasSeguimiento` con el cliente/`olvidata-marketing` — pendiente.
- [ ] Definir `Olvidata_Negocio:MetaAnualUsd` con el cliente — pendiente.

## Historial de ajustes
- 2026-07-14: Bootstrap técnico inicial — copia de KoiDumplings saneada de lógica de negocio de KOI, a pedido explícito del cliente como base previa a Análisis. Ver detalle completo en `trazabilidad.md`.
- 2026-07-17: Implementación completa de la migración de BotPublicitario (Domain/Application/Infrastructure/Web + 1 migración EF aplicada). Build en verde. Ver sección completa arriba. Pendiente: QA funcional, configuración de credenciales reales de Meta/Google Maps, validación del mapeo rubro→catálogo de precios, y el runbook de corte de producción (fuera de alcance de esta sesión).
- 2026-07-17: Fix de los 3 defectos QA `major` detectados en la primera pasada de QA (CRM-001, CRM-004, CRM-006) — ver sección completa arriba. Build en verde. CRM-002/003/005 (minor) explícitamente fuera de esta pasada, quedan pendientes para una pasada futura si el cliente lo pide.
- 2026-07-17: Import de datos reales de producción de BotPublicitario (238 Contacto) a `olvidatacrm_dev`, vía importador de un solo uso ya descartado. Ver sección completa arriba.
- 2026-07-21: Implementación completa de "campañas de contacto frío configurables" (CU-13/14/15, HU-12 a HU-16) — 3 entidades nuevas, `CampanasController` + 3 vistas + 4 endpoints AJAX, migración EF (`AddCampanasOutbound`) aplicada, seed automático de 13 campañas + 2 industrias de catálogo. `OutboundCampaignService`/`GoogleMapsService`/`OutboundSchedulerService` migrados de diccionarios hardcodeados a lectura desde BD. Build en verde (2 corridas), seed verificado sin errores. Ver sección completa arriba. Pendiente: QA funcional.
- 2026-08-16: Implementación completa de "gestión comercial y herramientas de canal/venta" (CU-21 a CU-29) — 5 entidades nuevas + 1 enum + 1 campo, 3 controllers nuevos y 3 extendidos, 10 vistas nuevas y 7 modificadas, migración EF (`AddGestionComercial`) aplicada en dev y producción, deploy verificado en `https://portal.olvidata.com.ar/`. Ver sección completa arriba. 1 bug propio encontrado y corregido en el camino (día calendario UTC vs. ART en el churn del NRR). Pendiente: QA funcional, revisión de los textos de sugerencias y definición de la meta anual de negocio.
