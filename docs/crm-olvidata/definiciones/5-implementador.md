# Memoria - Implementador

## Proyecto: crm-olvidata
## Ultima actualizacion: 2026-10-15

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

## Sprints archivados

- **2026-07** (migración de BotPublicitario, fix de los 3 defectos QA major, import de datos reales, campañas de contacto frío configurables, ajuste UI de notificaciones) → `historial/5-implementador-2026-07.md`
- **2026-08** (gestión comercial y herramientas de canal/venta, corrección de bugs/gaps de la auditoría completa + 3 mejoras, matriz de módulos valorizados + borrador MVP/FULL) → `historial/5-implementador-2026-08.md`

## Feature "4 frentes — combo con gancho" (2026-09-14) — E1 a E7 IMPLEMENTADAS, pendiente QA

Entrada: `1-analista-funcional.md` (CU-30 a CU-35), `2-disenador-funcional.md` §8, `3-arquitecto-mvc.md` §7.2 (A1-a y A2), `4-presupuestador.md` (alcance completo aprobado). Sin deploy, sin commits, sin tocar Meta ni reactivar outbound/Maps/IA en produccion.

### 0. Escaneo de reutilizacion

- `catalogo.yml`: PAT-031 (nacido en el diseño de esta feature, sin codigo). Confirmado e implementado: se le agregaron las rutas reales de codigo y se saco `pendiente_verificar`.
- `docs/*/definiciones/5-implementador.md`: ningun proyecto clasifica web propia ni asigna oferta por perfil → construccion nueva.
- Reutilizacion literal intra-repo: `RubroHelpers` (vocabulario + `RubroBase`), `Plural`/`NarrativaByType` y el `BuildComponents` con botones de v13, `GetSaludAsync`/`SaludOutboundDto` (M-C), filtros en `Session` de Contactos/Chats, `ConfigParaEditarAsync`, `SendBriefToAdminAsync`/`NotifyAdminsInAppAsync`, guarda de rename/delete de B5, partial compartido Create/Edit (patron `_CamposCanalYPresupuesto`).
- **No existe auto-init global de Select2 en este repo** (el pedido lo asumia): cada combo nuevo se inicializa en su vista.

### 1. Alcance resumido

Todo contacto de outbound frio recibe el combo (pagina 3D + agentes de IA + asistente de WhatsApp) con un **gancho** determinístico (web propia + grupo de rubro) que elige la plantilla y la primera pregunta; la IA conoce los 4 frentes y hace venta cruzada una vez despues del dolor; `ai_agents`/`chatbot` entran al vocabulario y `merge` sale; el arbol no se rompe con categorias sin cuestionario; el catalogo de modulos tiene frente y Armar presupuesto arma el combo agrupado por frente.

### 2. Plan ejecutado por etapas

| Etapa | Estado | Nota |
|---|---|---|
| E1 Vocabulario y arbol | Hecha | `CategoriaHelpers` fuente unica (3 consumidores), cuestionarios `ai_agents`/`chatbot`, `TryGetValue` + escalada, `merge` solo historico |
| E2 Prompt | Hecha (codigo) | Identidad 4 frentes, 7 categorias con ejemplos, venta cruzada, web simple, cliente actual → escalar. **Verificacion con mensajes reales al webhook: QA** |
| E3 Gancho en contacto | Hecha | Enum + 5 props + `AsignarGancho`, `GanchoHelpers`, alta Maps (2 puntos), carga inicial, Contactos Index/Create/Edit/Details, Chats filtro/chip/card |
| E4 Conversacion por gancho | Hecha | `OnConfirmarContinuarAsync` por gancho, pregunta 1 por frente, oferta del contacto en el bloque NO cacheado del prompt |
| E5 Envio por gancho | Hecha | `ResolverPlantilla` antes del `Take(cupo)`, 4 casos `BuildComponents` + `TemplateBodies`, card `/Bot` + 2 acciones, `/Bot/Salud`, guardas Templates, A1-a follow-up/frio |
| E6 Modulos por frente | Hecha | `Frente`, `ModuloCatalogoQueries` compartida, Modulos Index/Create/Edit, Armar presupuesto multi-frente (pantalla + modal de Chats) |
| E7 Documentacion | Hecha | `arbol-comunicacion-bot.md` (§0, §1, §3.4, §6, §8) y `logica-negocio-bot.md` (A.3-A.5, B.3) |

### 3. Cambios por capa

- **Domain:** `Enums/GanchoContacto.cs` (nuevo), `Enums/FrenteComercial.cs` (nuevo); `Entities/Contacto.cs` (+`Gancho`, `MotivoGancho`, `FechaGancho`, `GanchoAMano`, `PlantillaPrimerContacto`, metodo `AsignarGancho`); `Entities/ModuloCatalogo.cs` (+`Frente`); `Entities/ConfiguracionOutbound.cs` (+4 `PlantillaGancho*`).
- **Application:** `Helpers/CategoriaHelpers.cs`, `Helpers/GanchoHelpers.cs`, `Helpers/PlantillasCombo.cs` (nuevos); `DTOs/ContactoListItemDto.cs` (+Gancho/Categoria/textos); `DTOs/SaludOutboundDto.cs` (+`GanchosSinEnvio`, `GanchoSinEnvioDto`, `EstadoPlantillaGancho`, `PlantillaGanchoEstadoDto`, `EstadoPlantillasGanchoDto`); `Interfaces/IOutboundCampaignService.cs` (+`GetEstadoPlantillasGanchoAsync`, `AsignarGanchosPendientesAsync`).
- **Infrastructure:** `Queries/ModuloCatalogoQueries.cs` (nuevo, try/catch CRM-020); `Data/AppDbContext.cs` (mapeos + indice + default Build); `Services/OutboundCampaignService.cs` (red de seguridad del gancho, catalogo/config y `ComboDisponible`, `ResolverPlantilla` antes del `Take`, `PlantillaPrimerContacto`, `PlantillasCombo.TieneBotonContinuar`, log de salteados, `AsignarGanchosFaltantes`, `AsignarGanchosPendientesAsync`, `GetEstadoPlantillasGanchoAsync` + `EvaluarPlantillaGancho` compartido con Salud, 4 casos `BuildComponents`, 4 `TemplateBodies`, A1-a en `ProcessFollowUpsAsync`/`MarkColdAsync`, gancho en `AgregarProspectosNuevosAsync`, `GetSaludAsync` con configuracion en `TemplatesSinCampana` + `GanchosSinEnvio`); `Services/BotFlowService.cs` (Questions desde `CategoriaHelpers` + 2 cuestionarios, `CategoryNames` retirado, `OnConfirmarContinuarAsync` por gancho, `TryGetValue` en `OnAnswerAsync`/`SendCurrentQuestionAsync`, pregunta 1 con modulos del frente, `EscalarPorCategoriaSinCuestionarioAsync`, consulta compartida); `Services/ConversacionIaService.cs` (`CategoriasValidas` desde `ClavesVigentes`, prompt estable con 4 frentes/venta cruzada/cliente actual, bloque del contacto con oferta y modulos del frente, tool `consultar_modulos_del_rubro` por frente, copia duplicada de la consulta retirada).
- **Migracion:** `Data/Migrations/20260915010357_AddGanchoYFrenteComercial` (+ Designer + snapshot).
- **Web — Controllers:** `ContactosController` (filtros gancho/interes con Session, proyeccion y orden de 2 columnas, Details Oferta, Create/Edit con `PaginaWeb` + `GanchoElegido`, `ValidarOferta`, `AplicarGanchoDesdeFormulario`); `ChatsController` (filtro gancho con Session, chip, card Oferta, frentes default del modal, etiqueta de evento nueva); `BotController` (card en Index, `GuardarPlantillasGancho`, `AsignarGanchos` JSON, gancho en `BuscarProspectos`); `TemplatesController` (guardas rename/delete + columna "usada por gancho", LP-002); `ModulosController` (Frente en Create/Edit, filtro/orden/Session en listado, `frentes` en Checklist/Calcular/GenerarMensaje, `ModulosDelRubroAsync` por frente, `NormalizarFrentes`, `ValidarFrente`).
- **Web — Models:** `ContactoViewModels`, `ChatViewModels`, `BotOutboundViewModels`, `ModuloCatalogoViewModels`, `TemplateWhatsAppViewModels`.
- **Web — Views/JS/CSS:** `Contactos/{Index,Create,Edit,Details,_CamposOferta (nuevo)}`, `Chats/{Index,_ChatListItems,Detail}`, `Bot/{Index,Salud}`, `Modulos/{Index,Create,Edit,Presupuesto,_ChecklistPresupuesto}`, `Templates/Index`, `wwwroot/js/presupuesto-modulos.js`, `wwwroot/css/site.css` (badges `violet`/`slate` con tema oscuro).

### 4. Migracion EF

`AddGanchoYFrenteComercial` — aditiva, **aplicada solo en `olvidatacrm_dev`** (verificado con `dotnet ef migrations list`; destino confirmado con `dbcontext info`: `olvidatacrm_dev@localhost`; user-secrets sin connection string).
- `Contactos`: `Gancho` int null + `IX_Contactos_Gancho`, `MotivoGancho` varchar(120) null, `FechaGancho` datetime(6) null, `GanchoAMano` tinyint(1) not null default 0, `PlantillaPrimerContacto` varchar(100) null.
- `ModulosCatalogo`: `Frente` int not null **default 1 (Build)** → todos los modulos existentes quedan en Build.
- `ConfiguracionesOutbound`: `PlantillaGanchoPresenciaWeb`/`Administracion`/`Consultas`/`Gestion` varchar(100) null.
- Sin SQL de datos: los contactos existentes quedan sin gancho hasta "Asignar ganchos pendientes" o el primer lote. `Down` elimina todo. **Produccion: NO aplicada.**

### 5. Evidencia de build

`dotnet build OlvidataCRM.slnx -c Release --no-incremental` → **Compilacion correcta, 0 errores, 26 advertencias, todas preexistentes** (16 NU1902 MailKit/MimeKit, 4 CS8620 en `ChatsController` `RouteValueDictionary(filtros.AsRouteValues())`, 4 CS8524 `ToFlag(DayOfWeek)` en `GoogleMapsService`/`OutboundCampaignService`, 2 CS0114 `HomeController`). Vistas Razor compiladas en el mismo build. Sin smoke test propio (rol).

### 6. Desvios respecto de las definiciones (con motivo)

1. **Card "Oferta" con el patron `dl row` de la ficha** y no `.ov-detail-grid`/`.ov-detail-item__value--empty`: esas clases no existen en el CSS de este repo; se usa el mismo patron que las cards vecinas (Datos/Estado) y `text-muted fst-italic` para el vacio.
2. **Gancho elegido a mano solo para canal Outbound frio** (error de validacion si el canal es otro): la tabla 8.3 evalua la fila 1 (canal) antes que la fila 2 (a mano); la arquitectura no lo explicitaba. Se prefirio avisar en vez de descartar en silencio.
3. **"Automatico" en Editar no le asigna gancho a un contacto historico que ya recibio el primer mensaje sin gancho**: le cambiaria el follow-up (A1-a) por un combo que nunca recibio. Un gancho elegido a mano si se aplica (con aviso). Tambien solo reescribe si cambia algo, para no mover la fecha en cada guardado.
4. **`GetEstadoPlantillasGanchoAsync` devuelve `EstadoPlantillasGanchoDto`** (filas + pendientes sin gancho) en vez de una lista: el boton de carga inicial necesita el conteo.
5. **Categoria sin cuestionario**: el mensaje del prospecto se registra como entrante `"Mensaje recibido (categoría sin cuestionario)"` (evento en /Chats, deja el chat no leido), `DerivadoManual`, **bot pausado 48hs** y notificacion **una sola vez** (guard por etiqueta). La pausa y la idempotencia no estaban en el diseño; evitan re-notificar en cada mensaje.
6. **Modulos genericos de un frente distinto de Build en Armar presupuesto = imprescindibles (MVP)**: no tienen fila de rubro donde guardar el flag. Supuesto a validar con `olvidata-presupuesto-bot`.
7. **Pregunta 1 con modulos del frente**: formato de texto definido en implementacion (pregunta fija + "En *{industria}* esto es lo que más nos piden resolver:" + viñetas + "Si lo tuyo es otra cosa, contámelo igual 👇"); el diseño no lo fijaba.
8. **Contexto de la IA**: la linea de oferta aparece solo si `PlantillaPrimerContacto` esta cargado (combo → linea del gancho; otra → "plantilla de la campaña"). Contactos historicos anteriores al campo no llevan linea.
9. **/Bot/Salud**: un gancho sin plantilla se lista siempre, pero cuenta como "punto de atencion" solo si tiene contactos esperando.
10. **Selector de frentes del modal de Chats** va en un bloque propio arriba del checklist (el cuerpo del modal se reemplaza por AJAX).
11. **Modulos/Index**: se agrego solo el filtro de la columna nueva (Frente, con Session y Limpiar); las columnas preexistentes siguen sin filtro (deuda previa, fuera de alcance).

### 7. Riesgos y supuestos

- **Concordancia de genero en los borradores combo (para `olvidata-marketing`)**: "hoy muchos {{1}}" / "en muchos {{1}}" con `Plural(rubro)` produce "muchos clínicas / inmobiliarias / farmacias / dietéticas y comercios…". Hay que reescribir el marco (ej. "en muchos negocios como {{1}}") antes de mandar a Meta, y ajustar `TemplateBodies`/`BuildComponents` si cambian los placeholders.
- `TemplateBodies` de las combo son copia de exhibicion de los **borradores**; el envio real usa el texto aprobado en Meta.
- Mientras las 4 combo no esten aprobadas y asignadas en /Bot, Presencia web / Administración / Consultas **no salen**; con R3 (presencia web dominante) el volumen diario puede quedar muy por debajo del cupo (visible en /Bot y /Bot/Salud). Outbound sigue pausado (S4).
- Sin modulos cargados de Landing/AI Agents/Chatbots (contenido de `olvidata-presupuesto-bot`), el arbol y la IA usan la pregunta fija.
- `frentes[]` por jQuery depende del value provider jQuery de ASP.NET Core; si no bindea, `NormalizarFrentes` cae a Build (no rompe, pero ignora la seleccion) — QA lo verifica.
- `AsignarGanchosPendientesAsync` trae a memoria todos los Pendiente OutboundFrio sin gancho (miles, aceptable) y guarda en un solo SaveChanges.
- Cache del prompt: el bloque estable cambia una vez al desplegar (reescritura unica, ~USD 0,03).

### 8. Pruebas minimas para QA (obligatorias)

1. `ResolverGancho` (via Contactos/Create canal Outbound frio + Automatico): web vacia → Presencia web "Sin web"; `instagram.com/x` y `x.mitiendanube.com` → Presencia web con el dominio en el motivo; `modalu.com.ar` + `estudio` → Administración; `modalu.com.ar` + `consultorio-palermo` → Consultas; dominio propio + `comercio` → Gestión; canal Ads/Manual → sin gancho; gancho a mano con canal Manual → error de validacion.
2. **Lote (T1)**: cupo chico con los primeros candidatos de gancho sin plantilla → salen los elegibles que siguen hasta completar el cupo; los salteados quedan Pendiente, no aparecen en `PlantillasEnviadasHoy`, se ven en /Bot ("Esperando") y /Bot/Salud, y queda el log.
3. Regresion: gancho Gestion sin combo, y contactos sin gancho → sale `v13` con el A/B de la campaña intacto; Referido → `olv_referido_v2`.
4. Con una combo asignada (template de prueba Activo+Aprobado en dev): `PlantillaPrimerContacto` = combo, fase `ConfirmandoContinuar`, hilo con el texto combo, botones `seguir`/`no_interesa`.
5. Boton "Sí, contame más" por gancho (webhook de prueba en dev): Presencia web → `landing` + "Partís de cero…"; Administración → `ai_agents`; Consultas → `chatbot`; Gestión/sin gancho → `rent` identico a hoy (incluida la matriz de modulos de Build); "No me interesa" → baja.
6. IA no disponible con `ai_agents` en `ConversandoConIa` → sigue el cuestionario sin presentarse; categoria sin cuestionario en `AskingQuestions` → DerivadoManual + bot pausado + 1 notificacion, nada al prospecto, sin excepcion.
7. `set_categoria` con `merge` → rechazada; historicos con `merge` → "Mejoras en sistema Olvidata (discontinuado)". E2 contra el webhook: los 4 mensajes de CA2 de CU-30 y "soy cliente y quiero una mejora" → escalar.
8. Contactos/Index y Chats/Index: filtros Gancho e Interés detectado filtran, persisten en Session, "Limpiar" los borra; **probar con base vacia** (MH-001). Orden por las 2 columnas nuevas.
9. Contactos/Edit: combo de gancho pre-seleccionado cuando es a mano, "Automatico" cuando no; aviso si ya se envio; Página web editable y persistida (Create y Edit).
10. Templates: renombrar o borrar una combo configurada en /Bot → bloqueado; columna "Gancho …" en el listado. /Bot/Salud: la combo configurada no aparece como "template sin campaña".
11. /Bot: guardar plantillas con valor manipulado (otro nombre, no aprobada) → no guarda nada y avisa; "Asignar ganchos pendientes" → cuenta y es idempotente (segunda corrida 0).
12. A1-a: contacto Presencia web en MensajeEnviado con 3-6 dias → no recibe follow-up; con 7+ → Frio. Gestion/sin gancho → follow-up como siempre.
13. Modulos: existentes en Build tras migrar; Create/Edit con Frente (Edit pre-seleccionado); filtro Frente con Session. **Armar presupuesto solo Build → mismo checklist, rangos y mensaje que antes (R9)**; con Landing+AI Agents+Chatbots → agrupado por frente; modal de Chats con default combo (+Build si interes de gestion) y recarga al cambiar frentes; manipular un checkbox con un id de otro frente → ignorado en Calcular.
14. Tildes y textos de UI en todas las pantallas tocadas.

### 9. Checklist de salida para merge

- [x] `dotnet build -c Release` sin errores (0 errores, 26 advertencias preexistentes).
- [x] Migracion `AddGanchoYFrenteComercial` generada y aplicada en `olvidatacrm_dev`. [ ] Aplicar en produccion (owner, despues de QA).
- [ ] QA GO sobre §8 (incluye mensajes de prueba al webhook para E2/E4).
- [ ] Textos combo corregidos por `olvidata-marketing` (concordancia de genero) y aprobados en Meta; actualizar `TemplateBodies`/`BuildComponents` si cambian.
- [ ] Deploy verificado (sitio 200, `/Bot`, `/Bot/Salud`, `/Contactos`, `/Chats`, `/Modulos/Presupuesto` sin 500).
- [ ] Outbound sigue pausado hasta tener al menos una combo aprobada y asignada, y ganchos asignados.
- [x] `arbol-comunicacion-bot.md` y `logica-negocio-bot.md` actualizados (E7). [x] PAT-031 confirmado en catalogo. [x] Regla nueva en `32-estandares` (filtro antes del `Take(cupo)`).
- [ ] Commit (no realizado por instruccion).

## Canal nuevo: DM de Instagram (2026-10-15) — fases 1-5 EN PRODUCCIÓN, fase 6 (QA con credenciales) abierta

Plan: `plan-instagram-dm-bot.md` (§14 tiene el detalle y las decisiones que no estaban en el plan).
Vía de autenticación: **Instagram Login** (token `IGAA`, envío por `graph.instagram.com/{ver}/me/messages`).

### Piezas nuevas

| Archivo | Qué hace |
|---|---|
| `Domain/Enums/CanalMensajeria.cs` | WhatsApp=1 / InstagramDm=2. Decide cliente de envío, clave de búsqueda y elegibilidad para plantillas. |
| `Application/Settings/InstagramSettings.cs` | Config del canal. `EstaConfigurado` = AccessToken + IgUserId. |
| `Application/Interfaces/IInstagramClient.cs` + `Infrastructure/Services/InstagramClient.cs` | Texto, quick replies, perfil y descarga de adjuntos ENTRANTES. HttpClient tipado, timeout 30s. **No tiene envío de archivos**: ver abajo. |
| `Infrastructure/Services/InstagramApiException.cs` | Conserva el código de Meta: 190 token, 10/200 permiso, rate limit, ventana cerrada. |
| `Application/Interfaces/IMensajeriaSender.cs` + `Infrastructure/Services/MensajeriaSender.cs` | **Pieza clave**, catalogada como **PAT-068**. Rutea el envío por `contacto.CanalMensajeria`. |
| `Web/Webhook/InstagramWebhookModels.cs` | Payload crudo, forma Messenger (`entry[].messaging[]`). Aparte del de WhatsApp: no comparten forma. |
| `Web/Webhook/FirmaMetaWebhook.cs` | `X-Hub-Signature-256` compartida por los 2 webhooks. Sin App Secret cargado devuelve true (comportamiento histórico de WhatsApp). |

### Entidades tocadas

- `Contacto`: **`Telefono` pasa a nullable** + `CanalMensajeria`, `IgScopedId` (único), `IgUsername` (display). Métodos de dominio: `TieneIdentidad`, `DestinatarioDelCanal`, `IdentidadVisible` — los 3 existen para que la regla no se reimplemente en los ~20 sitios que hacían `NombreNegocio ?? NombreContacto ?? Telefono` (CRM-001).
- `ContactoRespuesta.ArchivoAdjunto` (longblob, tope 8 MB): bytes del adjunto entrante de Instagram, bajados en el momento porque **las URLs del webhook de IG vencen** (a diferencia del media id de WhatsApp). Columna aparte de `ArchivoPdf` a propósito: esa significa "presupuesto enviado" y la lee `MensajeriaHelpers.TuvoPresupuesto`.
- `ConfiguracionOutbound.ConversacionIaModoSombraInstagram` + `EnSombraParaCanal(canal)` (OR con el flag general).

### Migraciones

- `AddCanalInstagramDm` — **editada a mano en 2 puntos**: `CanalMensajeria` con `defaultValue: 1` (EF generaba 0, que no es un valor del enum → los 10.235 contactos en un canal inexistente y el outbound apagado en silencio; regla **CRM-026**), y el único de `IgScopedId` sobre columna generada `IgScopedIdVivo` por **LP-057** (query filter de soft-delete).
- `AddModoSombraIaInstagram` — **misma trampa con signo invertido**: `defaultValue: true`, no el `false` de EF, porque el canal arranca en sombra.

### Reglas del catálogo aplicadas

- **LP-002**: el barrido de `Telefono` lo dirigió el compilador (nullable reference types → 37 warnings). Búsqueda, listado y ficha actualizados en `/Chats`, `/Contactos`, `/Clientes` y `/Clientes/Nuevo` — los 4 buscan también por `@usuario`.
- **CRM-024**: los filtros de canal van **antes** del `Take(cupo)` en las 4 queries de outbound, nunca con un `continue` adentro del `foreach`.
- **MH-001 / CRM-019**: todos los filtros de canal por igualdad contra el int del enum; el "es entrante" de `/Bot` con `EF.Functions.Like`, no `StartsWith`.
- **CRM-020**: la captura del perfil de IG, la captura de teléfono y el procesamiento entero del mensaje van envueltos. Se encontró y corrigió una instancia vieja — ver `6-qa.md`.
- **CRM-022**: en modo sombra la tool de teléfono **no escribe**.
- **CRM-018**: la sombra por canal se persiste en base, no en un static.

### Lo que NO se puede hacer por Instagram, y por qué

**Mandar archivos.** La Attachment Upload API (`/message_attachments`) es de Messenger/Página y por la vía Instagram Login no existe; la alternativa por URL pública no aplica (el PDF vive como bytes y su endpoint está detrás de `[Authorize]`). `IInstagramClient` no expone ningún método de envío de archivos a propósito: el corte vive en `MensajeriaSender` con un mensaje que el asesor entiende. `/Chats` corta el upload del PDF **antes** de guardarlo, y el envío de imágenes del mismo día queda solo en WhatsApp (esa acción guarda el `MediaId` de Meta para poder volver a verla, y ese id no existe por esta vía).
Si alguna vez se quiere: hace falta un endpoint de descarga firmado y de vida corta, y recién entonces el adjunto por URL.

### Config y encendido

`Olvidata_Instagram` en `appsettings.json` (no secretos) y los 3 secretos + `Features:InstagramDm` + `TokenVenceEl` en **`appsettings.Secrets.json`** del directorio del sitio (gitignoreado, fuera del `.csproj`, sobrevive los deploys). Los 2 flags y el token se leen con **`IOptionsMonitor`**, no `IOptions`: con `IOptions` bindeaban una sola vez al arrancar y editar el archivo no tenía efecto hasta reciclar el app pool — que es exactamente el síntoma que hizo fallar la validación del webhook en Meta sin ninguna pista. Ver `6-qa.md`, CRM-027.

**OJO con la precedencia**: `Program.cs` agrega `appsettings.Secrets.json` *después* de `CreateBuilder`, así que queda **último** y le gana a las variables de entorno — al revés de lo que dice su propio comentario. Deuda: corregir el comentario.

## Web Push para chats derivados a mano (CRM-028, 2026-10-15) — QA pasado (19 PASS / 0 major), CRM-029 corregido, pendiente de re-verificación y de deploy

Diseño §9 / Arquitectura "Web Push para los chats derivados a mano". **Primera vez que el estudio
hace Web Push** — patrón nuevo **PAT-069** en el catálogo. Escaneo de reutilización: `cat_resumen.txt`
sin match (PAT-068 es lo más cercano y es ruteo de envío, no notificación), y el `grep -ril` dirigido
sobre `docs/*/definiciones/` por webpush / VAPID / service worker solo devuelve las definiciones de
este mismo CR. **Sin antecedente: se construyó nuevo.**

El problema: un contacto en `DerivadoManual` que escribe se guardaba, no se le contestaba (correcto,
lo lleva una persona) y quedaba "no leído" en `/Chats`. Nadie se enteraba hasta abrir el CRM, justo en
los chats donde alguien ya se comprometió a seguir la conversación.

### Piezas nuevas

| Archivo | Qué hace |
|---|---|
| `Domain/Entities/PushSubscription.cs` | Un dispositivo suscrito. `EndpointHash` (SHA-256 hexa) + `CalcularHash` como único punto de cálculo. `DispositivoVisible` para la lista. |
| `Application/Interfaces/IPushNotificationService.cs` | `SuscribirAsync` / `DesuscribirAsync` / `TieneSuscripcionAsync` / `EnviarAsync`. |
| `Application/DTOs/PushSubscriptionDto.cs` | La forma exacta de `PushSubscription.toJSON()` del navegador (`keys` anidado), para que el JS mande el objeto tal cual viene. |
| `Application/Settings/PushSettings.cs` | `PublicKey` / `PrivateKey` / `Subject` + `EstaConfigurado`. |
| `Infrastructure/Services/PushNotificationService.cs` | Envío sobre `Lib.Net.Http.WebPush` 3.3.1. Best-effort con 2 niveles de `try`. |
| `Web/wwwroot/push-sw.js` | Service worker: **solo** `push` y `notificationclick`. Ni un `fetch`, ni un `caches`. |
| `Web/wwwroot/js/push.js` | Botón con los 4 estados + conversión base64url→Uint8Array de la clave pública. |

### Entidades y capas tocadas

- `Contacto` + `FechaUltimoAvisoDerivado` y la propiedad de dominio **`EsperaAvisoDeChatDerivado`**
  (avisa si el aviso es null o si `FechaUltimaLecturaAgente > FechaUltimoAvisoDerivado`). La regla vive
  en la entidad y no en el servicio, por CRM-001. **No se tocó** la semántica de
  `FechaUltimaLecturaAgente` ni de `MarcadoNoLeidoManual`: ese flag es marca de gestión del asesor, no
  una lectura, y mezclarlo haría que marcar un chat como no leído dispare un push nuevo.
- `BotFlowService`: `AvisarChatDerivadoAsync` + `VistaPreviaDelMensaje`, y el disparo **en
  `HandleIncomingAsync`, el punto único de entrada**, con `eraDerivadoManual` capturado justo después
  del lookup del contacto. Enganchar en las 3 ramas de `return` (multimedia en `loAtiendeUnaPersona`,
  texto con el bot pausado, flujo normal con la pausa de 48hs vencida) garantizaba olvidarse de una,
  hoy o el día que alguien agregue la cuarta. Destinatarios por `SeedData.RolSuperUsuario`, el mismo
  criterio de `NotifyAdminsInAppAsync` — no se inventó otro.
- `NotificationsController`: `GET ClavePublica`, `GET EstadoPush`, `POST Suscribir`, `POST Desuscribir`
  (los 2 POST con `[ValidateAntiForgeryToken]`, token por el `meta[name=csrf-token]` que ya existía).
- `_Layout.cshtml`: el `unregister()` **global** pasa a **selectivo** (desregistra todo scope cuyo
  `scriptURL` no sea `/push-sw.js`) + botón en el dropdown de la campanita + `push.js`.
  `Notifications/Index`: card con el botón y la explicación del estado.

### Migración EF

`20261015230453_AddPushSubscriptions` — **aditiva**: tabla `PushSubscriptions` +
`Contactos.FechaUltimoAvisoDerivado`. **Editada a mano en 1 punto**: el único de `EndpointHash` va
sobre la columna generada `EndpointHashVivo` (`IF(DeletedAt IS NULL, EndpointHash, NULL)`), regla
**LP-057**, mismo patrón que `IgScopedIdVivo`. Con el único sobre la columna real, un dispositivo dado
de baja no podría volver a activarse nunca: el navegador devuelve el mismo endpoint, el query filter
esconde la fila, el INSERT muere contra el único y el botón falla para siempre en ese dispositivo y
solo en ése. Por eso además `SuscribirAsync` busca con `IgnoreQueryFilters()` y **revive** la fila en
vez de insertar otra. El hash existe porque el endpoint es varchar(500) y 2000 bytes utf8mb4 no entran
en una clave de InnoDB.

**Aplicada solo en dev** (`olvidatacrm_dev`), verificada en `information_schema`: columna
`VIRTUAL GENERATED` + `UX_PushSubscriptions_EndpointHash_Vivo`. **Producción sin tocar.**

### Decisiones que no estaban en las definiciones

1. **`Lib.Net.Http.WebPush` 3.3.1 NO trae `VapidHelper`** — solo sabe enviar, no generar claves
   (verificado contra el XML de documentación del paquete). El par VAPID se generó con un `ECDsa`
   P-256 aparte: pública = punto sin comprimir `0x04||X||Y` en base64url, privada = el escalar `D`. No
   buscar el helper en la librería, no está en esta versión.
2. **El `SaveChanges` de la marca anti-ruido va ANTES de los envíos.** Meta puede entregar 2 mensajes
   del mismo contacto en requests paralelos: con la marca guardada después de los envíos (cientos de ms
   contra el push service), los 2 leerían null y avisarían los 2, justo en el caso que motiva la regla.
3. **`EnviarAsync` abre su propio scope de `DbContext`** (riesgo R4). Corre dentro del webhook, donde el
   contexto compartido tiene cambios del contacto a medio aplicar: un `SaveChanges` de ahí —dar de baja
   una suscripción muerta, por ejemplo— los commitearía por el costado y a destiempo.
4. `PushServiceClient` por `AddHttpClient` con timeout explícito de 15s, y **un `VapidAuthentication`
   por aviso** (no por dispositivo): firmar el JWT es la parte cara y el mismo token sirve para los 3
   navegadores del usuario.
5. TTL 1800s + `Urgency.High`: el aviso dice "te escribieron AHORA"; entregarlo 6 horas después es
   ruido sobre algo que ya se vio en el CRM.
6. `404`/`410` → baja automática de la suscripción. Cualquier otro error solo incrementa
   `FallosConsecutivos`: un 500 ajeno del push service no significa que el navegador haya desaparecido.

### Configuración

`Push:PublicKey` y `Push:Subject` en el `appsettings.json` commiteado (la pública la ve cualquiera que
abra el CRM porque el JS la necesita; el subject es un mailto que los push services exigen).
**`Push:PrivateKey` solo en `dotnet user-secrets` en dev**; en producción va en
`appsettings.Secrets.json` del directorio del sitio —el mismo donde ya viven `Anthropic:ApiKey` y los
secretos de Instagram— o como variable de entorno `Push__PrivateKey` del sitio, que gana sobre el
archivo. Si el par rota, **todas las suscripciones vigentes mueren** y hay que reactivar dispositivo
por dispositivo.

### Verificado en dev

`dotnet build -c Release` **0 errores** (21 advertencias, todas preexistentes — el
`System.Security.Cryptography.Pkcs 8.0.1` vulnerable ya venía de MimeKit, no del paquete nuevo:
confirmado contra el nuspec). End-to-end real por el webhook de WhatsApp sin firma (dev no tiene
`AppSecret` cargado) contra un contacto en `DerivadoManual`:

- suscripción **real contra FCM** creada desde el navegador, fila en BD, `EstadoPush` consistente;
- **el push llegó**: `FechaUltimoEnvioOk` sellado y el globo presente en el service worker
  (`registration.getNotifications()` → título "Te escribió Kiosco de Prueba", cuerpo con los primeros
  120 caracteres, `tag: chat-524`, url `/Chats/Detail/524`);
- **R1 cerrado**: el SW sobrevive 3 cargas de página con el `unregister` selectivo;
- **anti-ruido**: 4 mensajes seguidos (3 de texto + 1 audio) → **1 solo aviso**, marca sin cambiar;
- **re-armado**: con `FechaUltimaLecturaAgente` posterior al aviso, el audio siguiente sí avisó, con la
  etiqueta "Te mandó un audio.";
- baja y re-alta del dispositivo desde el botón, con la fila vieja fuera del único
  (`EndpointHashVivo IS NULL`) — el LP-057 funcionando;
- datos de prueba borrados de dev al terminar.

### Lo que NO se probó

- **La rama de revivir una fila soft-deleted** (`IgnoreQueryFilters`): Chrome emitió un endpoint
  **nuevo** tras el `unsubscribe()`, así que se insertó otra fila en vez de revivir. La rama cubre el
  caso real distinto —fila dada de baja por un 410 mientras el navegador conserva su suscripción— y
  queda sin ejercitar.
- **iOS** (R3): necesita el CRM instalado en la pantalla de inicio y un iPhone real.
- **Firefox y Safari**: solo se probó Chromium.
- **El caso "el mensaje es el que deriva el chat"**: la lógica es explícita (`eraDerivadoManual` se
  captura antes de procesar) pero no se ejercitó con un payload.
- **Producción**: ni migración, ni deploy, ni commit — pendiente de autorización de Joaquín.

### CRM-029 (defecto de QA, minor) — aplicado, pendiente de re-verificación

QA pasó CRM-028 con 19 PASS y 0 major, y emitió un solo parte: el anti-ruido no se sostenía con la
pestaña del chat abierta. `Chats/HiloParcial` estampa `FechaUltimaLecturaAgente` cuando trae mensajes
nuevos, y el anti-ruido colgaba de esa fecha, así que el polling lo re-armaba solo cada 8 segundos:
3 mensajes → 3 avisos, reproducido 3/3.

**Lo que NO se podía hacer**: sacar el estampado de `HiloParcial`. De esa fecha depende el "no leído"
de la lista de Chats, y tiene su propio bug histórico documentado justo sobre esa semántica
(`ChatsController.cs`, la nota larga arriba de `HiloParcial`). Lo que tenía que cambiar era **de qué
depende el re-armado**.

**Fix**: campo nuevo `Contacto.FechaUltimaLecturaDeliberadaAgente` y
`EsperaAvisoDeChatDerivado` pasa a colgar de él. Las 2 fechas coexisten porque responden preguntas
distintas: `FechaUltimaLecturaAgente` = "¿se mostró en pantalla?" (la lista de no leídos),
`FechaUltimaLecturaDeliberadaAgente` = "¿alguien hizo algo?" (el anti-ruido del push).

De los **6 puntos** de lectura, **5 son deliberados** y pasan por el método de dominio nuevo
`Contacto.RegistrarLecturaDeliberada(ahora)`, que estampa las 2 fechas (CRM-001: quien agregue mañana
una sexta acción de lectura estampa las 2 sin tener que saber que la segunda existe, que es
exactamente lo que se rompió acá):

| Punto | Acción | Deliberado |
|---|---|---|
| `Detail` | abrir el chat | sí → método de dominio |
| `EnviarMensaje` / `EnviarPresupuestoPdf` / `EnviarImagen` | responder | sí → método de dominio |
| `MarcarTodosLeidos` | marcar leído desde la lista | sí → `.SetProperty` replicado (es `ExecuteUpdateAsync`, no materializa entidades) |
| **`HiloParcial`** | tick del polling | **no** — queda con el estampado inline y un comentario que dice que agregar ahí el método de dominio devuelve el defecto |

**Hay 3 estampados más de `FechaUltimaLecturaAgente` fuera de `ChatsController`** que el parte no
listaba y que quedan **deliberadamente sin tocar**: `BotFlowService.DescartarNoEsProspectoAsync`,
`BotFlowService.ProcesarBajaAsync` y `ContactosController.CambiarEstado`. Los 3 son el mismo
criterio ("todo lo que pasa a `Descartado` queda leído porque ya está resuelto"), no son lecturas
humanas, y sobre todo: un contacto `Descartado` ya salió de `DerivadoManual`, así que el aviso no
se evalúa nunca más para él. Anotados acá para que no parezcan un olvido.

`RegistrarLecturaDeliberada` **no** toca `MarcadoNoLeidoManual` a propósito: de los 5 puntos, solo 2
lo limpiaban y los 3 de envío nunca lo hicieron. Meterlo adentro cambiaría comportamiento legacy que
nadie pidió cambiar.

**Migración**: `20261016000404_AddLecturaDeliberadaChat` — aditiva, 1 columna nullable, **aplicada
solo en dev**. Lleva un `UPDATE` idempotente que siembra la columna nueva desde
`FechaUltimaLecturaAgente` para las filas que la tienen: sin él los ~10.000 contactos arrancan en
"nadie leyó nunca este chat" y la columna no significa nada hasta que cada chat se abra una vez. No
cambia ningún comportamiento observable hoy (`FechaUltimoAvisoDerivado` también arranca en NULL, así
que el primer mensaje avisa igual por la primera condición del guard). Verificado en dev: 20 de 20
filas con lectura quedaron sembradas.

**Las 2 observaciones cosméticas de QA, en la misma corrida**:
- `push.js`: `getRegistration('/push-sw.js')` toma una URL de **cliente**, no de script — funcionaba
  de casualidad porque el scope es la raíz. Reemplazado por `registracionDePush()`, que recorre
  `getRegistrations()` y matchea por `scriptURL`.
- `_Layout.cshtml`: el comentario decía que "dos SW pueden compartir scope". Corregido: un scope tiene
  una sola registración; lo que justifica filtrar por `scriptURL` es que el scope no identifica al
  archivo.

**Verificado en dev** (build Release **0 errores**, 21 advertencias preexistentes), reproduciendo el
escenario exacto del parte con la pantalla de detalle abierta en background y el polling corriendo
(6 llamadas a `HiloParcial` en el log):

- **3 mensajes seguidos → 1 aviso.** `FechaUltimaLecturaAgente` quedó en 00:06:24 (el polling siguió
  estampando, o sea que el guard viejo se habría re-armado) mientras la lectura deliberada quedó en
  00:05:51, anterior al aviso de 00:06:00. Las 2 mitades del criterio de QA, medidas.
- **Tras abrir el detalle deliberadamente, el mensaje siguiente sí avisó** (2º aviso).
- `MarcarTodosLeidos` escribe la columna nueva (verificado aparte: es la única implementación que no
  pasa por el método de dominio).
- Los 3 puntos de envío comparten el método de dominio con `Detail`, que sí se ejercitó; no se
  dispararon por separado para no mandar WhatsApp reales desde dev.
- Datos de prueba borrados.

**Fuera de alcance de esta corrida, por indicación**: pasar el envío de push a una cola (observación 1
de QA: ~8 s dentro del webhook con 3 dispositivos y uno inalcanzable) y el hallazgo incidental de
`OnNewAsync` con token roto, anotado como defecto aparte en `trazabilidad.md` sin tocarlo.

### Runbook de deploy de CRM-028 + CRM-029 (preparado 2026-10-16, SIN EJECUTAR)

Lo que viaja: `1005cd2` (feature), `fb45699` (fix de CRM-029) y `e5da865` (sesión de un mes para la
PWA, que esperaba justamente el web push). QA dio GO. **El deploy no lo ejecutó el implementador**:
es la única acción de la secuencia que Joaquín reservó para sí ("el deploy lo hago yo cuando QA
re-verifique"), y una autorización relevada por otro agente no la reemplaza. Queda esto, en orden:

1. **La privada de VAPID, ANTES del publish.** Va en `appsettings.Secrets.json` del directorio del
   sitio (el mecanismo de `c5a1a6d`: gitignoreado, fuera del `.csproj`, y sobrevive los deploys
   porque el perfil usa `DeleteExistingFiles=false` + `SkipExtraFilesOnServer=true`). Es el mismo
   archivo donde ya viven `Anthropic:ApiKey` y los secretos de Instagram, así que **hay que
   agregarle la clave, no reemplazarlo**. Bloque a sumar:
   `"Push": { "PrivateKey": "48mIHTEWGAJF04bf3RGdaaRlglJnB9d7c2O0OS4qY9g" }`.
   La pública y el subject ya viajan en el `appsettings.json` commiteado. Alternativa equivalente:
   la variable de entorno `Push__PrivateKey` del sitio, que gana sobre el archivo. **Ojo con la
   precedencia**: `Program.cs:39` agrega `appsettings.Secrets.json` *después* de `CreateBuilder`,
   así que queda último y le gana a las variables de entorno — al revés de lo que dice su propio
   comentario (deuda ya anotada). Sin la privada el canal **degrada bien pero no avisa nada**.
2. **Chequear gaps de migraciones antes de aplicar nada.** Precedente del estudio: comparar la
   última fila de `__EFMigrationsHistory` de producción contra la carpeta `Data/Migrations` del
   repo. En el repo, la última antes de este CR es `20261015160552_AddModoSombraIaInstagram`; si
   producción no la tiene, **hay gap y no se aplica nada hasta resolverlo**.
   `SELECT MigrationId FROM __EFMigrationsHistory ORDER BY MigrationId DESC LIMIT 5;`
3. **Las 2 migraciones, aditivas**: `AddPushSubscriptions` (tabla nueva + 1 columna en `Contactos`,
   más el `ALTER` a mano de la columna generada `EndpointHashVivo` y su único) y
   `AddLecturaDeliberadaChat` (1 columna + el `UPDATE` de siembra).
   **Confirmar el conteo real de la siembra, no asumirlo** — en dev fueron 20 de 20 filas con
   lectura, pero producción tiene ~10.000 contactos y el número va a ser otro:
   `SELECT COUNT(*) FROM Contactos WHERE FechaUltimaLecturaDeliberadaAgente IS NOT NULL;`
   contra `SELECT COUNT(*) FROM Contactos WHERE FechaUltimaLecturaAgente IS NOT NULL;` — tienen
   que dar **igual**. El `UPDATE` es idempotente (solo toca las filas en NULL), así que un
   reintento es seguro.
4. **Smoke test post-deploy, con evidencia**: `https://portal.olvidata.com.ar/` → 200; el login
   servido trae el campo `EsPwa` (es lo que confirma que viajó `e5da865`); `/push-sw.js` servido con
   `Content-Type` de JavaScript (si IIS lo devuelve como `text/plain` el navegador rechaza
   registrar el SW y el push no funciona, sin ningún error del lado del servidor);
   `/Notifications/ClavePublica` devolviendo la pública que está en `appsettings.json`;
   `/Notifications` → 302 al login sin sesión. Y mirar el log del sitio en la ventana del deploy.
5. **Verificación manual de 5 minutos que QA no pudo hacer** (R1 y la entrega real): activar los
   avisos en el navegador de Joaquín, recargar 3 veces, confirmar que el botón sigue en "activados",
   y que llega un globo con el CRM cerrado.

**No se toca el certificado.** Vence el 2026-10-19 y Joaquín decidió explícitamente no renovarlo
ahora. No bloquea el deploy (hoy es válido), pero **cuando venza, el push se cae con el sitio**:
Web Push exige HTTPS válido. Es el riesgo R2 y sigue siendo el dominante de esta funcionalidad.

## Cola de seguimiento (2026-10-15) — IMPLEMENTADA, pendiente de QA y de autorización de envío

### 0. Escaneo de reutilización

`docs/patrones/cat_resumen.txt`: sin match (lo más cercano, PAT-025, es cola de trabajo en segundo
plano, no de seguimiento comercial). `grep -ril` sobre `docs/*/definiciones/`: el antecedente real es
este mismo proyecto, y se reutilizó código vivo en vez de construir de nuevo:

- **El envío con la ventana cerrada** va por `OutboundCampaignService.ReactivarConversacionAsync`
  (la reactivación de un chat desde `/Chats`, 2026-09-18). Ya valida la plantilla contra el catálogo,
  revalida la ventana, chequea el tope de gasto, pausa el bot y registra la fila facturable en el
  hilo. **Un segundo camino de envío de plantillas sería exactamente CRM-017** (un tope que no topa
  porque hay un camino que no lo consulta), así que no se escribió.
- **Las opciones de plantilla** salen de `GetOpcionesReactivacionAsync` — la misma lista de texto fijo
  aprobado que ya ofrece `/Chats`, sin una segunda lista.
- **El texto libre** va por `IMensajeriaSender` (ruteo por canal del contacto).
- **La ventana** sale de `MensajeriaHelpers.VentanaCierra`, que es por canal desde el 2026-10-15.
- **La revalidación obligatoria** copia el criterio de `MensajesProgramadosSchedulerService`.
- **La referencia temporal y el match de sugerencia** son los de `ChatsController.SugerirMensaje`.
- **El listado** copia el patrón DataTable server-side + Session de `ContactosController`.

### 1. Alcance

La pantalla que decide **a quién le toca el próximo mensaje**, y el botón que lo manda. Cierra el
hueco medido en `diagnostico-seguimiento-2026-10-16.md`: 276 de 301 contactos que respondieron no
tenían ningún follow-up. **Sin automatismo**: el `SeguimientoSchedulerService` se construye después,
sobre un criterio ya validado a mano.

### 2. Cambios por capa (6 archivos nuevos, 2 tocados con 11 líneas en total)

**Application** (nuevos):
- `DTOs/SeguimientoColaDtos.cs` — `ColaSeguimientoDto`, `ContactoColaDto`, `OpcionRubroColaDto`,
  `OpcionesToqueDto`, `ToqueSeguimientoResultadoDto`, `ColaSeguimientoFiltros`.
- `Helpers/SugerenciasSeguimientoHelper.cs` — resolución del texto sugerido como función pura
  (sirve para 1 contacto y para 320 con un solo catálogo en memoria).
- `Interfaces/ISeguimientoColaService.cs`.

**Infrastructure** (nuevo):
- `Services/SeguimientoColaService.cs` — criterio de la cola, orden por valor, revalidación de la
  ventana y los 2 caminos de envío. `HorasMinimasSinToque = 48`.

**Web** (nuevos):
- `Controllers/SeguimientoController.cs` — `Index`, `GetData` (POST DataTables), `OpcionesToque`
  (GET), `Toque` (POST con antiforgery). **Cero reglas de negocio y cero acceso a datos**: ni el
  conteo de la cola se calcula acá.
- `Views/Seguimiento/Index.cshtml` — DataTable server-side, 10 columnas, **toda columna visible con
  su filtro**, SweetAlert2 para los 2 modales de envío, daterangepicker para "última señal",
  Select2 en rubro/zona/interés.

**Tocados, 1 bloque cada uno (el resto del archivo sin reformatear):**
- `Infrastructure/DependencyInjection.cs` — +6 líneas: `AddScoped<ISeguimientoColaService, …>`
  después del registro de `IOutboundCampaignService`, del que depende.
- `Web/Views/Shared/_Layout.cshtml` — +5 líneas: ítem de sidebar "Cola de seguimiento" en la sección
  Comercial, entre Chats y Clientes.

### 3. Migraciones EF

**Ninguna, y no hace falta.** La cola se calcula y la salida se marca con `Contacto.FechaFollowUp`,
que ya existe. No se agregó ni una columna.

### 4. El criterio, medido contra producción (no estimado)

`EstadoEmbudo` en (Respondido, PresupuestoEnviado, DerivadoManual) + sin follow-up posterior a la
referencia + referencia de más de 48 h. Referencia =
`FechaRespuesta ?? FechaPrimerEnvio ?? FechaUltimaActividad`.

| Hecho medido el 2026-10-15 | Valor |
|---|---:|
| **La cola** | **320** |
| Con matriz MVP/FULL cargada (van primero) | 208 |
| Con la ventana de 24 h abierta (texto libre gratis) | **0** |
| Ya tienen algún mensaje nuestro posterior a su respuesta | 50 |
| Costo real de una plantilla | ARS 89,55 |
| Lote de prueba de 30 del rubro con matriz más grande (Retail, 91 en cola) | ARS 2.686,50 |

**La cola son 320, no 276.** El 276 del diagnóstico es `EstadoEmbudo = Respondido AND FechaFollowUp
IS NULL` (nunca, jamás). El criterio aprobado es más amplio y más correcto: "sin follow-up
**posterior a su respuesta**". Los 28 contactos de estos 3 estados que tienen `FechaFollowUp` la
tienen **anterior** a su respuesta (les llegó el follow-up frío y después contestaron), así que
vuelven a la cola con razón. Más los 16 de PresupuestoEnviado y 4 de DerivadoManual.

**Y el filtro por `FechaFollowUp` no descarta a nadie hoy** (321 → 321 en producción). El campo lo
escribe un solo lugar, `ProcessFollowUpsAsync`, que solo corre sobre `MensajeEnviado`: **no detecta
los mensajes manuales que un asesor ya mandó desde `/Chats`**. Esos 50 contactos se calculan aparte
(`ToquePosteriorUtc`) y se **muestran y filtran por columna**, en vez de sacarlos de la cola en
silencio. El criterio de la cola queda el aprobado, y la decisión de pagarle una plantilla a alguien
a quien ya le escribieron queda a la vista de quien la toma. Si Joaquín prefiere excluirlos, es
tildar el filtro por defecto: 1 línea.

### 5. Riesgos y deuda declarada

- **R1 — el envío no se ejercitó.** Cero mensajes mandados: ninguna plantilla, ningún texto libre.
  Es el único camino sin evidencia de ejecución, y hace falta autorización explícita para probarlo.
- **R2 — la lista de plantillas incluye `olv_notif_respuesta`** (el aviso interno al admin) y las 3
  automáticas. Es **preexistente**: viene tal cual de `GetOpcionesReactivacionAsync` y `/Chats` ya la
  ofrece así hoy en producción. `olv_retomar_conversacion_v1` sale primera y marcada como sugerida.
  No se tocó por alcance, pero mandarle a un prospecto la plantilla de notificación interna sería un
  error caro y el filtro de texto fijo no lo evita.
- **R3 — duplicación declarada:** `ChatsController.SugerirMensaje` conserva su copia inline del
  algoritmo de match. No se la tocó para no modificar una acción de producción fuera de alcance, y
  está anotado en el XML-doc del helper: si se cambia el criterio hay que cambiar los dos. Es la
  forma de fallar de CRM-007/CRM-016 en este mismo proyecto.
- **R4 — la cola se materializa completa en memoria** (320 filas hoy) porque el orden por valor no se
  puede expresar en SQL: el mapeo rubro → industria vive en diccionarios de `RubroHelpers`. A miles
  de filas habría que precalcular la industria en la entidad.

### 6. Bug propio encontrado EJECUTANDO, no compilando

El filtro de rango de fechas tiraba `ArgumentException` (500 en la pantalla) por el `Kind` del
`DateTime`: `TimeZoneInfo.ConvertTimeToUtc` no acepta un `DateTime` con `Kind = Local` si la zona de
origen no es la local. El camino de la pantalla pasa por `DateTime.TryParse` de un string del
formulario, que devuelve `Unspecified` y no falla nunca — pero la firma del service acepta un
`DateTime` de cualquier llamador, y con `DateTime.Today` revienta. **El build lo daba por bueno.**
Corregido con `ArtCalendarioAUtc` (`SpecifyKind(…, Unspecified)` antes de convertir) y verificado con
los 3 `Kind`: Unspecified → 71 filas, Local → 87, Utc → 71, sin excepción.

### 7. Evidencia

- `dotnet build`: **Compilación correcta, 0 errores**, 21 advertencias **todas preexistentes**
  (NU1902/NU1903 de MailKit/MimeKit/Pkcs, CS8524 en GoogleMapsService y OutboundCampaignService,
  CS0114 en HomeController, CS8620 en ChatsController). Ninguna de los archivos nuevos.
- **Las vistas Razor se compilan en el build**, verificado a propósito inyectando un error
  deliberado en `Views/Seguimiento/Index.cshtml` (falló con CS0103 en la línea esperada) y
  revirtiéndolo. O sea: el build verde cubre el C# de la vista.
- **JS embebido**: `node --check` sobre el bloque `<script>` con las expresiones Razor sustituidas —
  sintaxis válida (307 líneas).
- **Sonda EF desechable** (scratchpad, ya borrada): resolvió `ISeguimientoColaService` por el
  contenedor de DI **real** (`AddInfrastructure`) y ejecutó `GetColaAsync` y `GetOpcionesToqueAsync`
  contra **producción en solo lectura**, con cero escrituras y sin levantar la app. Probó que el LINQ
  nuevo traduce a MySQL (el `COALESCE` de 3 términos en `Where` y en `Select`, las 2 subconsultas
  correlacionadas con `Max` + `EF.Functions.Like`, y el `Count` correlacionado por navegación), los
  16 filtros uno por uno incluido el que devuelve 0 filas, y el tope del lote. **Es lo que encontró
  el bug de la sección 6**: el build no lo veía.

### 8. Reglas del catálogo aplicadas

- **MH-001**: los 3 estados van como `==` contra el enum, nunca un `Contains` de colección local. La
  búsqueda de texto se evalúa en memoria. Verificado también con el filtro que devuelve 0 filas, que
  es donde MH-001 revienta igual.
- **CRM-019**: "mensaje entrante" se detecta con `EF.Functions.Like(r.Pregunta, "[%")` y no con
  `StartsWith`. Cubre las 14 etiquetas salientes (todas abren con corchete) y no queda desactualizado
  cuando se agregue la decimoquinta, a diferencia de la cadena de 14 `!=` que repiten los schedulers.
- **CRM-024**: el `Take(Tope)` del lote de prueba va **al final**, después de todos los filtros de
  elegibilidad. Verificado: la combinación de 4 filtros con tope 30 devuelve 30.
- **CRM-017**: el chequeo del tope de gasto **no se reimplementó** — el que bloquea es el que corre
  dentro de `ReactivarConversacionAsync`. Y el texto libre se registra con `EtiquetaMensajeManual` y
  **no** con `EtiquetaFollowUp`: esa segunda es una de las 4 que `GetCostoMensajeriaAsync` cuenta como
  plantilla facturable, y un texto libre dentro de la ventana no le cuesta nada a Meta — usarla
  inflaría el gasto medido del mes y recortaría el cupo del outbound por envíos que nadie pagó.
- **CRM-007**: el rubro se resuelve con `RubroHelpers.CatalogoNombreDeRubroContacto`, que cubre los 3
  vocabularios de `Contacto.Rubro`. Importa el segundo: el bot reescribe `Rubro` con el nombre de
  diálogo apenas el contacto responde, así que comparar solo contra la clave dejaría afuera justo a
  los contactos que llegaron a la demo. Medido: agrupa "indumentaria", "indumentaria-laplata" y
  "Indumentaria o calzado" en una sola opción de filtro de 91 contactos.
- **LP-002**: la identidad de la fila sale de `IdentidadVisible` (teléfono o @usuario según canal),
  no de `Telefono`, que es nullable desde el 2026-10-15.
- **CRM-023**: el único GET con parámetros manda un escalar, no un array.
- **REG-010**: el ítem de sidebar va dentro del `@if (User.IsInRole("SuperUsuario"))` existente, y el
  controller tiene `[Authorize(Policy = "RequireSuperUsuario")]`.

### 9. Pruebas mínimas para QA

1. `/Seguimiento` carga y el total de la card dice **320** (o menos, si se mandó algún toque).
2. **Cada uno de los 10 filtros** por separado y después combinados, incluido uno que deje la grilla
   vacía: ninguno puede dar 500 (es el escenario de MH-001).
3. El **rango de fechas** de "última señal", que es donde estaba el bug de la sección 6.
4. **Orden**: las primeras filas tienen ★ en Matriz y las últimas no. Dentro de cada grupo, los días
   van de menor a mayor.
5. "Lote de prueba → Primeros 30" **con** el filtro de rubro con matriz: tienen que salir 30, no
   menos (CRM-024).
6. Abrir el modal del toque: con toda la cola en ventana cerrada tiene que ofrecer **plantilla** y
   mostrar el costo en ARS, nunca un textarea libre.
7. **El envío NO se prueba sin autorización de Joaquín**: cada toque con ventana cerrada es una
   plantilla paga real a un prospecto real.
8. Que no haya regresión en `/Chats` ni en `/Contactos` (comparten `_Layout` y `MensajeriaHelpers`).

### 10. Checklist de merge

- [x] Build verde, 0 errores, sin advertencias nuevas
- [x] Vistas Razor compiladas (verificado inyectando un error)
- [x] JS embebido validado con `node --check`
- [x] LINQ nuevo ejecutado de verdad contra MySQL (solo lectura)
- [x] 0 migraciones EF
- [x] Lógica de negocio en el Service, controller sin reglas ni datos
- [x] Toda columna visible tiene filtro
- [x] Line endings CRLF, consistentes con el repo; los 2 archivos compartidos con +6 y +5 líneas y
      nada reformateado
- [ ] **Sin commit y sin deploy** (por instrucción explícita)
- [ ] QA funcional
- [ ] Autorización de Joaquín para mandar el primer lote de 30 (ARS 2.686,50)

### 11. Ajustes del coordinador (2026-10-16) — aplicados

**Ajuste 1 — lista blanca de plantillas de reenganche.** Nuevo
`Application/Helpers/PlantillasReenganche.cs`: criterio de INCLUSION, no de exclusión. El contacto de
esta cola ya respondió, así que una `olv_frio_*` le habla como si no nos conociera y una
`olv_renovacion_*` le habla de un plan que no tiene. Con lista negra, cada plantilla nueva dada de
alta en `/Templates` entraría sola a esta pantalla; con lista blanca, el default seguro es no
ofrecerla. Se aplica en dos lugares: filtra el combo en `GetOpcionesToqueAsync` **y** es guarda del
lado del servidor en `ToqueConPlantillaAsync` — `ReactivarConversacionAsync` valida contra todas las
aprobadas de texto fijo (correcto para `/Chats`), así que un POST armado a mano con `olv_frio_v13`
pasaría su validación. Si la lista queda vacía por datos, la pantalla lo dice con el nombre de las que
faltan; nunca un combo vacío. Deuda anotada en el XML-doc: lo correcto es un campo `Proposito` en
`TemplateWhatsApp`, sin migración en esta entrega.

**La lista quedó en 2, no en 3: `olv_nurturing_v2` no se puede mandar desde acá.** Es de reenganche y
debería estar, pero **pide 3 parámetros de body** (nombre, prueba social, dolor del rubro) que arma
`OutboundCampaignService.BuildFollowUpComponents`; su texto real es
`"Hola {0}, ... {1} tenía {2} y hoy tiene todo ordenado..."` (ver `TemplateBodies`). El camino de
envío de esta pantalla reusa `ReactivarConversacionAsync`, que manda `components = null`, y Meta
rechaza un envío con menos parámetros de los que el template declara. No es una exclusión de criterio
comercial: es una limitación técnica del envío actual, y queda anotada en el archivo para que se pueda
incluir cuando haya un camino que arme los components.

**Y la trampa que lo escondía, que es el argumento más fuerte para el campo `Proposito`:** el filtro
de "texto fijo" de `PlantillasTextoFijoAprobadasAsync` es `!Texto.Contains('{')` sobre la **copia
local** del texto, y la copia local de `olv_nurturing_v2` es el centinela
`"(el texto vive en Meta — el sistema manda esta plantilla ...)"`, que no tiene ninguna llave. O sea
que el filtro lee **"no sé cuál es el texto" como "no tiene parámetros"**. Le pasa igual a
`olv_referido_v2` y a `olv_notif_respuesta`: las tres están hoy en el combo de `/Chats` clasificadas
como texto fijo, y las tres llevan parámetros.

Corrección a la advertencia previa: **`olv_frio_combo_admin_v2` NO es interna** — "admin" es el gancho
Administración, uno de los 4 del combo. Es outbound legítimo. Queda afuera por ser de primer contacto,
no por interna. La única interna es `olv_notif_respuesta` (`CategoriaMeta = Utility`).

**Ajuste 2 — los ya contactados quedan fuera de la cola por defecto.** El riesgo de escribirle de
nuevo a alguien ya contactado es peor que el de perderlo: paga una plantilla y encima queda mal. El
filtro pasó de `SoloSinToquePosterior` a `IncluirConToquePosterior` (default `false`, porque el default
de un bool tiene que ser el seguro), la columna y el filtro se mantienen, y el encabezado dice cuántos
quedaron excluidos y cómo traerlos. Tres cosas que había que cuidar y están cubiertas:

- `GetOpcionesToqueAsync` consulta con `IncluirConToquePosterior = true`: un contacto traído con el
  filtro **sigue siendo elegible**. Con el default habría dicho "ya no está en la cola" justo para las
  filas que el usuario pidió ver.
- Los combos de rubro y zona se arman del **universo completo**, no de la cola: si no, tildar el
  filtro mostraría filas de un rubro que no está en la lista.
- El modal abre con un aviso rojo con la fecha en que se le escribió, **antes** del aviso de matriz.
  No bloquea: el usuario lo pidió a propósito, pero es lo primero que lee.

La exclusión vive en **un solo lugar** (el conjunto que `GetColaAsync` le pasa a `Filtrar`), no como un
`Where` adicional dentro del filtro: dos lugares que deciden lo mismo se desalinean.

**Los números, remedidos contra producción el 2026-10-16:**

| | |
|---|---:|
| Universo (criterio de 48 h) | 320 |
| **La cola de trabajo** | **270** |
| Excluidos porque ya les escribimos | **50** |
| Con matriz MVP/FULL, sobre la cola | 180 (eran 208 sobre el universo) |
| Con ventana de 24 h abierta | 0 |

El cambio no es cosmético: **el que era el primero de la cola** (#9954, Farina Balbi, 7 días, rubro con
matriz) **ya había recibido un mensaje el 2026-10-08** y hoy queda excluido. Era exactamente el contacto
al que se le iba a pagar una plantilla de más.

**Evidencia de los ajustes**: build 0 errores (21 advertencias, las mismas preexistentes);
`node --check` sobre el JS (320 líneas, válido); y una segunda sonda de solo lectura que verificó que
270 + 50 = 320, que ninguna fila del default está ya contactada, que el filtro trae las 320, que el
combo ofrece exactamente 2 plantillas con `olv_retomar_conversacion_v1` como sugerida, y que la guarda
del servidor **rechaza las 5** que se le pasaron a mano (`olv_frio_v13`,
`olv_renovacion_recordatorio_v1`, `olv_notif_respuesta`, `olv_nurturing_v2`, `olv_referido_v2`)
cortando antes de tocar la red. **Cero mensajes enviados.**

**Pruebas que QA tiene que agregar a las de §9:**
9. Que el combo de plantillas ofrezca **solo** `olv_retomar_conversacion_v1` y `olv_reenganche_menu_v1`,
   y que `olv_retomar_conversacion_v1` venga preseleccionada.
10. POST a `/Seguimiento/Toque` con `plantilla=olv_frio_v13` armado a mano: tiene que rechazarlo el
    servidor, no solo el combo.
11. Que la cola abra en **270** y el encabezado diga los 50 excluidos; tildar el filtro → 320, y las
    filas nuevas con badge en la columna "Posterior" y aviso rojo al abrir el modal.
12. Que `/Chats` siga ofreciendo **todas** las plantillas de texto fijo: la lista blanca es de esta
    pantalla, no de las dos.

### 12. CRM-032 (minor, defecto propio emitido por QA) — aplicado, pendiente de re-verificación

**El defecto.** El botón se rehabilitaba en el `always()` del `getJSON` de opciones, o sea **antes**
del POST de envío, y la marca de salida se escribía **después** del envío. Durante el vuelo del POST
pagado la fila aceptaba un segundo toque y los dos pasaban todos los guards. Escenario real: alguien
dando 30 clicks seguidos sobre la cola.

**Arreglo del cliente.** El botón de esa fila queda deshabilitado desde el click hasta que resuelve el
**POST de envío**. Se rehabilita en 5 puntos y sólo en esos: el servidor bloquea, falla la consulta de
opciones, se cancela cualquiera de los 2 modales, o no hay plantillas; y cuando el envío se dispara, lo
rehabilita el `always()` de `enviar()`. `$btn` se pasa como parámetro a los 2 modales y a `enviar()`.

**Arreglo del servidor — reserva atómica.** La protección del cliente no alcanza (un POST a mano la
saltea), así que el criterio exacto con el que el servidor rechaza, para que QA lo verifique:

> Antes de enviar, un **UPDATE condicional único** (`ExecuteUpdateAsync`) escribe `FechaFollowUp = ahora`
> con el `WHERE` **igual al criterio de la cola**:
> `Id = @id AND DeletedAt IS NULL AND (FechaFollowUp IS NULL OR FechaFollowUp < COALESCE(FechaRespuesta, FechaPrimerEnvio, FechaUltimaActividad))`.
> **Si afecta 1 fila, gana la reserva y envía. Si afecta 0, se rechaza sin enviar** con *"Este contacto
> ya tiene un toque en curso o ya enviado"*. La atomicidad la garantiza MySQL en una sentencia, no el
> orden en que corra el código, así que vale entre requests concurrentes y entre procesos.

Tres consecuencias de diseño que importan:

- **El modo de falla se invirtió a propósito.** Antes era "se envió y no se pudo marcar" (riesgo de
  pagar dos veces); ahora es "se marcó y no se pudo enviar", y entonces se **libera** la reserva
  (`UPDATE` con `WHERE FechaFollowUp = @ahora`, para no pisar lo que haya escrito otro) restaurando el
  valor anterior exacto — que puede no ser null: un follow-up frío viejo, anterior a la respuesta. Si
  la liberación tampoco se pudiera hacer, se avisa: el contacto quedaría fuera de la cola sin haber
  recibido nada. Sin plata gastada, y recuperable.
- **Se libera también cuando `ReactivarConversacionAsync` devuelve `!Ok`** (tope de gasto agotado,
  plantilla ya enviada sin respuesta, Instagram). Sin eso, un contacto saldría de la cola en silencio
  sin que nadie lo hubiera contactado.
- **El input se valida antes de reservar** (`ValidarTextoLibre` / `ValidarPlantilla`, extraídos de los
  2 caminos de envío): un pedido inválido no reserva ni libera de gusto. La lista blanca de plantillas
  sigue chequeándose del lado del servidor, ahora en `ValidarPlantilla`, **antes** de la reserva.
- `ToqueSeguimientoResultadoDto.EnviadoSinMarcar` quedó con el significado dado vuelta (ahora es
  "marcado y no enviado"); está documentado en el DTO y el único cambio en la vista por eso es el
  título del `Swal` de esa rama ("Revisá esto a mano"), que QA no podía haber ejercitado porque exige
  un fallo de base en el medio del envío.

**Evidencia — concurrencia medida, no supuesta.** Build 0 errores (21 advertencias, 0 en archivos
nuevos), `node --check` sobre el JS. Y una sonda desechable contra un **clon de dev**
(`olvidatacrm_crm032`, dropeado al terminar; dev verificada intacta en 444 contactos y 0
`FechaFollowUp`; el clon de QA `olvidatacrm_qacola` no se tocó) con `IMensajeriaSender` reemplazado
por un **fake sin red** — cero mensajes enviados:

| Escenario | Resultado |
|---|---|
| **8 toques CONCURRENTES** (8 scopes de DI = 8 conexiones, abiertas antes de la barrera) | **1 gana, 7 rechazados, 1 solo envío** |
| Un toque más, después, secuencial | rechazado por el pre-chequeo |
| Envío que falla, 4 concurrentes | 0 Ok, **1 solo envío intentado**, `FechaFollowUp` liberada a null |
| Después de liberar | **vuelve a la cola** y el reintento sale bien |
| `olv_frio_v13` por POST | rechazado, y `FechaFollowUp` **sigue null**: no reservó |

Una prueba **secuencial** de esto da falso verde: con un solo `DbContext` las sentencias se serializan
solas y el segundo intento siempre ve el valor ya escrito. Hicieron falta N scopes con una barrera.

**Nota de arnés, no del sistema:** la primera corrida dio "no vuelve a la cola" en el escenario de
liberación. Era contaminación propia: reusé el contacto del escenario concurrente, cuyo envío exitoso
le dejó un mensaje nuestro posterior a su respuesta — o sea que quedaba **correctamente** excluido por
el ajuste 2. Re-medido sobre un contacto limpio, da lo esperado.

**No se tocó CRM-031** (plantillas centinela en `/Chats`): preexistente, major, y su fix de fondo es
`Proposito` + `CantidadParametros` en `TemplateWhatsApp`, con migración. Otro ciclo.

**Para QA en la re-verificación de CRM-032:**
13. 2 pestañas sobre la misma fila, confirmar las dos lo más junto posible: una tiene que decir
    "ya tiene un toque en curso o ya enviado" y en el hilo del chat tiene que haber **un** mensaje.
14. POST a mano repetido a `/Seguimiento/Toque` con el mismo `contactoId` (sin pasar por la pantalla):
    el segundo tiene que ser rechazado igual.
15. Click → cancelar el modal: el botón tiene que volver a estar habilitado.
16. Click → confirmar: el botón tiene que estar deshabilitado **todo** el vuelo del POST.

## Historial de ajustes
- 2026-10-15: **Cola de seguimiento.** 6 archivos nuevos (3 Application, 1 Infrastructure, 1 controller, 1 vista) y 2 tocados con +6 y +5 lineas (`DependencyInjection`, `_Layout`). **0 migraciones EF.** Criterio medido contra produccion: la cola son **320**, no los 276 del diagnostico, y el filtro por `FechaFollowUp` no descarta a nadie hoy porque el campo no ve los mensajes manuales de `/Chats` (50 casos, expuestos por columna). 208 con matriz MVP/FULL, 0 con ventana de 24h abierta. Envio reutilizando `ReactivarConversacionAsync`, sin segundo camino de plantillas. Build 0 errores; LINQ ejecutado contra produccion en solo lectura con una sonda desechable, que encontro un bug propio de `Kind` de `DateTime` que el build no veia. **Cero mensajes enviados.** Pendiente: QA, autorizacion del primer lote de 30 (ARS 2.686,50), commit y deploy.
- 2026-10-16: **Cola de seguimiento, 2 ajustes del coordinador.** (1) Lista blanca de plantillas de reenganche en `PlantillasReenganche.cs`, aplicada al combo Y como guarda del servidor — quedo en **2** y no 3: `olv_nurturing_v2` pide 3 parametros de body que el camino de envio actual no arma. Destapo que el filtro de "texto fijo" lee el centinela "(el texto vive en Meta)" como "sin parametros", asi que 3 plantillas con parametros estan hoy mal clasificadas en el combo de `/Chats`. (2) Los ya contactados salen de la cola por defecto: **universo 320, cola 270, 50 excluidos**, con el filtro para traerlos y el conteo en el encabezado. El que era #1 de la cola ya habia sido contactado el 08/10. Build 0 errores; verificado con una segunda sonda de solo lectura. Cero mensajes enviados.
- 2026-10-16: **CRM-032 (defecto propio de QA) aplicado, pendiente de re-verificacion.** El boton se rehabilitaba antes del POST de envio y la marca se escribia despues, asi que durante el vuelo del envio pagado la fila aceptaba un segundo toque. Cliente: el boton queda deshabilitado hasta que resuelve el POST (5 puntos de liberacion). Servidor: **reserva atomica** con un UPDATE condicional unico antes de enviar (`WHERE` igual al criterio de la cola; 1 fila = gana, 0 = rechaza), con liberacion si el envio falla. El modo de falla se invirtio a proposito: de 'se envio y no se marco' (pagar dos veces) a 'se marco y no se envio' (recuperable, sin plata). Build 0 errores; **concurrencia medida** con 8 scopes de DI y barrera contra un clon de dev y un sender falso: 1 gana, 7 rechazados, 1 solo envio. Cero mensajes enviados. CRM-031 NO se toco (preexistente, major, necesita migracion).
- 2026-09-14: **Feature "4 frentes — combo con gancho", E1-E7.** 2 enums, 5 props + `AsignarGancho` en Contacto, `Frente` en ModuloCatalogo, 4 plantillas por gancho en configuracion; 3 helpers nuevos en Application y `ModuloCatalogoQueries` compartida; lote con plantilla por contacto antes del `Take(cupo)` y A1-a; arbol/IA por gancho y frente; Contactos/Chats/Bot/Salud/Templates/Modulos. Migracion aditiva `AddGanchoYFrenteComercial` aplicada **solo en dev**. Build Release 0 errores (26 advertencias preexistentes). 11 desvios documentados (§6). Pendiente: QA, textos de marketing (concordancia de genero), aprobacion de Meta, migracion en produccion y deploy.
- 2026-08-27: **Matriz de módulos valorizados + borrador de propuesta MVP/FULL** (feature nueva, reglas del agente `olvidata-presupuesto-bot`). 2 entidades nuevas + migración `20260828023654_AddModuloCatalogo` (2 tablas nuevas, 0 `ALTER`), aplicada **sólo en dev**; seed de la matriz real (**84 módulos / 88 asignaciones / 9 de 14 rubros**, los otros 5 sin datos a propósito); `IPropuestaMvpFullService` en Application con las 9 reglas de redacción, determinístico y sin IA en runtime; `ModulosController` + 5 vistas + 1 JS; wiring del botón "Sugerir" de `Chats/Detail` sin retirar la funcionalidad vieja; 5 cambios al cuestionario del bot. Build en Release **0 errores / 13 advertencias preexistentes**; app levantada y ejercitada por HTTP real (5 pantallas 200, 0 errores en Serilog); generador y resolver de rubro verificados contra datos reales de dev. **Sin deploy y sin tocar producción**, por instrucción explícita. Ver sección completa arriba. Pendiente: QA funcional, aplicar la migración en producción y deploy.
- 2026-08-27 (post-QA): Corrección de **CRM-007** (bloqueante), **CRM-010** y **CRM-012**. Se tomó la decisión de diseño que QA escaló: el vocabulario canónico de `Contacto.Rubro` es `CampanaOutboundIndustria.ClaveRubro`, no `IndustriaCatalogo.Nombre`. 1 archivo nuevo en `Application` (`RubroHelpers`, con los 2 mapeos movidos tal cual desde `BotFlowService`), 2 controllers, 2 DTOs/VMs, 4 vistas. **0 migraciones EF.** Build en Release con 0 errores; conteo de impacto verificado contra `olvidatacrm_dev` (deja de dar 0 para las 7 industrias con rubros asociados: 155/104/58/38/35/28/1). CRM-008 descartado por el cliente (falsa alarma: la migración sí está en producción, QA la midió contra dev). CRM-009/011/013 fuera de alcance por decisión explícita. Ver §9. Pendiente: re-test de QA y deploy.
- 2026-08-27: Implementacion del sprint “correccion de bugs/gaps de auditoria completa + 3 mejoras” — 17 items (7 bugs B1-B7, 7 gaps G1-G7, 3 mejoras M-A/M-B/M-C), **0 migraciones EF**. 2 archivos nuevos en `Application` (`MensajeriaHelpers`, `SaludOutboundDto`), 2 vistas nuevas (`Bot/Salud`, `Contactos/_CamposCanalYPresupuesto`), 8 controllers y 7 vistas modificados. Build en verde con compilacion de vistas Razor verificada explicitamente. La corrida se retomo tras un corte por watchdog a mitad de B3: la auditoria item-por-item contra el codigo en disco detecto que B3 estaba a medio hacer (servidor listo, JS sin escribir) y que el bug seguia reproduciendose pese al build verde. Ver seccion completa arriba. Pendiente: QA funcional y deploy.
- 2026-07-14: Bootstrap técnico inicial — copia de KoiDumplings saneada de lógica de negocio de KOI, a pedido explícito del cliente como base previa a Análisis. Ver detalle completo en `trazabilidad.md`.
- 2026-07-17: Implementación completa de la migración de BotPublicitario (Domain/Application/Infrastructure/Web + 1 migración EF aplicada). Build en verde. Ver sección completa arriba. Pendiente: QA funcional, configuración de credenciales reales de Meta/Google Maps, validación del mapeo rubro→catálogo de precios, y el runbook de corte de producción (fuera de alcance de esta sesión).
- 2026-07-17: Fix de los 3 defectos QA `major` detectados en la primera pasada de QA (CRM-001, CRM-004, CRM-006) — ver sección completa arriba. Build en verde. CRM-002/003/005 (minor) explícitamente fuera de esta pasada, quedan pendientes para una pasada futura si el cliente lo pide.
- 2026-07-17: Import de datos reales de producción de BotPublicitario (238 Contacto) a `olvidatacrm_dev`, vía importador de un solo uso ya descartado. Ver sección completa arriba.
- 2026-07-21: Implementación completa de "campañas de contacto frío configurables" (CU-13/14/15, HU-12 a HU-16) — 3 entidades nuevas, `CampanasController` + 3 vistas + 4 endpoints AJAX, migración EF (`AddCampanasOutbound`) aplicada, seed automático de 13 campañas + 2 industrias de catálogo. `OutboundCampaignService`/`GoogleMapsService`/`OutboundSchedulerService` migrados de diccionarios hardcodeados a lectura desde BD. Build en verde (2 corridas), seed verificado sin errores. Ver sección completa arriba. Pendiente: QA funcional.
- 2026-08-16: Implementación completa de "gestión comercial y herramientas de canal/venta" (CU-21 a CU-29) — 5 entidades nuevas + 1 enum + 1 campo, 3 controllers nuevos y 3 extendidos, 10 vistas nuevas y 7 modificadas, migración EF (`AddGestionComercial`) aplicada en dev y producción, deploy verificado en `https://portal.olvidata.com.ar/`. Ver sección completa arriba. 1 bug propio encontrado y corregido en el camino (día calendario UTC vs. ART en el churn del NRR). Pendiente: QA funcional, revisión de los textos de sugerencias y definición de la meta anual de negocio.
