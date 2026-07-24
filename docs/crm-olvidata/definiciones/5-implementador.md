# Memoria - Implementador

## Proyecto: crm-olvidata
## Ultima actualizacion: 2026-07-14

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

## Historial de ajustes
- 2026-07-14: Bootstrap técnico inicial — copia de KoiDumplings saneada de lógica de negocio de KOI, a pedido explícito del cliente como base previa a Análisis. Ver detalle completo en `trazabilidad.md`.
- 2026-07-17: Implementación completa de la migración de BotPublicitario (Domain/Application/Infrastructure/Web + 1 migración EF aplicada). Build en verde. Ver sección completa arriba. Pendiente: QA funcional, configuración de credenciales reales de Meta/Google Maps, validación del mapeo rubro→catálogo de precios, y el runbook de corte de producción (fuera de alcance de esta sesión).
- 2026-07-17: Fix de los 3 defectos QA `major` detectados en la primera pasada de QA (CRM-001, CRM-004, CRM-006) — ver sección completa arriba. Build en verde. CRM-002/003/005 (minor) explícitamente fuera de esta pasada, quedan pendientes para una pasada futura si el cliente lo pide.
- 2026-07-17: Import de datos reales de producción de BotPublicitario (238 Contacto) a `olvidatacrm_dev`, vía importador de un solo uso ya descartado. Ver sección completa arriba.
- 2026-07-21: Implementación completa de "campañas de contacto frío configurables" (CU-13/14/15, HU-12 a HU-16) — 3 entidades nuevas, `CampanasController` + 3 vistas + 4 endpoints AJAX, migración EF (`AddCampanasOutbound`) aplicada, seed automático de 13 campañas + 2 industrias de catálogo. `OutboundCampaignService`/`GoogleMapsService`/`OutboundSchedulerService` migrados de diccionarios hardcodeados a lectura desde BD. Build en verde (2 corridas), seed verificado sin errores. Ver sección completa arriba. Pendiente: QA funcional.
