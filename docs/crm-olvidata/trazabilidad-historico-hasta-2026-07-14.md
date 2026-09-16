# Trazabilidad - historico (archivo cerrado)

Archivo cerrado: entradas de 2026-07-14 a 2026-07-14. El log vigente sigue en `trazabilidad.md` (entradas desde 2026-07-15 en adelante).

## Entradas

### 2026-07-14 - analista-funcional
- Etapa: Discovery
- Cambio: Proyecto nuevo `crm-olvidata` inicializado desde template. Relevado el código real de `C:\Sistemas\BotPublicitario`: 4 proyectos .NET 9 (Webhook, WhatsApp, GoogleMaps, MetaAds-C#) + scripts Python marginales de setup one-off. Investigación solicitada por el cliente ("¿migrar a .NET?") resuelta: el código productivo ya es 100% .NET 9, no requiere migración de lenguaje. La brecha real es ausencia de base de datos (todo es JSON/txt/Excel), de capas Clean Architecture y de UI de administración. Se detectó solape con `docs/meta-ads/` (análisis ya cerrado del bot de calificación N1-N7) que debe resolverse antes de avanzar.
- Motivo: cliente pidió investigar viabilidad de migración a .NET y evaluar un CRM nuevo sobre `blankproject` para centralizar contactos/clientes/lógica del emprendimiento. Alcance de esta sesión: solo investigación, sin implementación.
- Impacto en capas: N/A (etapa de Discovery, sin diseño técnico).
- Riesgos/supuestos: BotPublicitario está en producción activa (outbound diario + webhook real) — cualquier migración de persistencia debe hacerse sin cortar el flujo de ventas en curso. Discovery queda abierto, bloqueado por 2 preguntas al cliente (alcance de "demás lógica del emprendimiento" y relación con el análisis ya cerrado de meta-ads) antes de poder cerrar y pasar a Análisis.

### 2026-07-14 - analista-funcional (cierre de Discovery)
- Etapa: Discovery — cierre
- Cambio: Cliente resolvió las 2 preguntas bloqueantes. (1) Alcance = CRM + gestión comercial (contactos/leads/clientes + planes contratados + upsells + recordatorios de renovación + pipeline de proyectos). (2) La lógica de calificación/presupuesto automático ya analizada en `docs/meta-ads/` (N1-N7) se absorbe dentro de este proyecto — el Webhook de Meta pasará a escribir contra las tablas del CRM en vez de JSON.
- Motivo: destrabar el pase a Análisis funcional evitando duplicar el trabajo ya analizado en meta-ads.
- Impacto en capas: N/A (aún sin diseño técnico). Amplía el alcance funcional que deberá cubrir Análisis: entidades Contacto/Lead, Cliente, Plan, Upsell, Proyecto/Pipeline.
- Riesgos/supuestos: Discovery cerrado, habilitado el pase a Análisis. Preguntas #3 (alcance exacto del endpoint webhook), #4 (carga inicial de clientes históricos) y #5 (prioridad vs. proyectos pagos) quedan abiertas para Análisis, no bloquean su inicio.

### 2026-07-14 - implementador (limpieza técnica base, previa a Análisis)
- Etapa: fuera de secuencia — bootstrap técnico a pedido explícito del cliente, antes de Análisis/Diseño/Arquitectura/Presupuesto formales
- Cambio: creado `C:\Sistemas\olvidatasoft-crm` (solución/namespace `OlvidataCRM`) como copia de `C:\Sistemas\KoiDumplings` — sistema .NET 10 real y probado del estudio, no el `blankproject` base — y saneado de toda la lógica de negocio específica de KOI Dumplings, conservando únicamente lo pedido: diseño gráfico (Design System `olvidata-theme.css`, layout, wwwroot completo), herramientas del sistema/superusuario (`SystemController`, health checks, exportación Excel/PDF), auditoría (`AuditLog` + trail automático en `AppDbContext.SaveChanges`), notificaciones in-app (`NotificationService`/`NotificationsController`) y usuarios (Identity, roles SuperUsuario/Administrador/Vendedor/Empleado, sin el rol Inversor). Eliminadas ~30 archivos de dominio/aplicación/infraestructura/web de KOI (Inversores, Liquidaciones, Puntos, Estado de Resultados, Rubros/Subgrupos, Cámaras, Reparto General, Importación Inicial, Tipo de Cambio, Notificación de Cierre). Regenerada migración EF `InitialCreate` limpia (solo Identity + AuditLog + Notification + PreferenciaUsuario). Corregidas rutas de `ProjectReference` rotas (arrastraban `KoiDumplings.*` de un rename anterior a medio hacer) y renombrada la cookie de tema `koi-tema` → `crm-tema`. Repo inicializado con `git init` sin historial de KOI.
- Motivo: el cliente pidió partir de "una base confiable funcionalmente" (un sistema real del estudio, no la plantilla vacía) para el nuevo CRM, y limpiar todo lo que fuera negocio específico de KOI que no aplica a un CRM.
- Impacto en capas: las 4 (Domain/Application/Infrastructure/Web) — ver detalle arriba. Sin migración a producción; solo se generó el archivo de migración inicial, sin `database update` contra ninguna base real.
- Riesgos/supuestos: se encontró `appsettings.Production.json` con credenciales reales de producción de KOI (DB MySQL y SMTP) en texto plano — sanitizado con placeholders `[COMPLETAR]`/vacíos (el archivo ya estaba en `.gitignore`, no se había commiteado, pero quedaba expuesto en disco). `HomeController.Index()` redirige temporalmente a `Notifications` (antes redirigía a `Dashboard`, controller eliminado) — el Dashboard real del CRM queda pendiente de Diseño/Arquitectura. Esta limpieza no reemplaza las etapas de Análisis/Diseño/Arquitectura/Presupuesto: las entidades propias del CRM (Contacto, Cliente, Plan, Upsell, Proyecto/Pipeline) todavía no existen y deben definirse ahí antes de implementarlas.

### 2026-07-14 - implementador (migración aplicada en dev)
- Etapa: fuera de secuencia — verificación técnica de la base
- Cambio: aplicada la migración `InitialCreate` contra la base de desarrollo local (`olvidatacrm_dev`, `localhost:3306`) con `dotnet ef database update`. Confirmado con `dotnet ef migrations list` que quedó aplicada sin pendientes.
- Motivo: validar que la base técnica saneada funciona de punta a punta (build + migración real) antes de empezar Análisis.
- Impacto en capas: Datos (solo entorno local de desarrollo).
- Riesgos/supuestos: ninguno — base local, sin datos reales.

### 2026-07-14 - analista-funcional (Análisis funcional)
- Etapa: Análisis
- Cambio: Análisis funcional cerrado. Resueltas las 3 preguntas pendientes de Discovery: (#3) el webhook de Meta se absorbe como endpoint dentro de `OlvidataCRM.Web`; (#4) el CRM arranca vacío, sin carga de clientes históricos; (#5) el desarrollo se planifica en ventana aparte de los proyectos pagos activos. Definidas 6 entidades nuevas (`Contacto`, `ContactoRespuesta`, `Cliente`, `Upsell`, `Proyecto`, `IndustriaCatalogo`), 12 casos de uso con criterios de aceptación, 3 máquinas de estados relacionadas (FaseConversacion del bot, EstadoEmbudo comercial, EstadoProyecto de pipeline) y el mapa de reutilización de código de BotPublicitario: `WhatsAppClient` y `GoogleMapsService` se reutilizan tal cual; `BotFlowService` y `OutboundCampaignService` se migran adaptados a persistencia en BD (dejan de depender de JSON/Excel).
- Motivo: traducir las decisiones de Discovery en alcance funcional verificable, listo para Diseño.
- Impacto en capas: Presentación (nuevos controllers/vistas + endpoint webhook), Negocio (BotFlowService/OutboundCampaignService migrados, cálculo de presupuesto, conversión Contacto→Cliente), Datos (6 entidades nuevas + migración EF).
- Riesgos/supuestos: pendiente definir en Arquitectura el "día D" de corte de BotPublicitario (dejar de escribir JSON, empezar a escribir en la BD del CRM) sin perder leads en tránsito, y el import único de datos en curso (`outbound_state.json`, `conversations/*.json`, `contactos.xlsx`) si los hubiera al momento del corte. Permisos exactos de Vendedor/Empleado quedan para Diseño, no bloquean su inicio.

### 2026-07-14 - analista-funcional (recorte de alcance)
- Etapa: Análisis — ajuste post-cierre
- Cambio: cliente pidió acotar el alcance — "por el momento solo voy a migrar lo que corresponde al bot publicitario". Se posponen a una iteración futura las entidades `Cliente`, `Upsell`, `Proyecto` (gestión comercial) y los casos de uso CU-07 (conversión a Cliente), CU-08 (Upsell), CU-09 (pipeline). El alcance de esta iteración queda en 3 entidades (`Contacto`, `ContactoRespuesta`, `IndustriaCatalogo`) y 9 casos de uso centrados en la migración funcional de BotPublicitario (captación, calificación, presupuesto automático, outbound, notificación).
- Motivo: priorización del cliente — enfocar primero en tener el bot funcionando sobre el CRM antes de sumar gestión comercial.
- Impacto en capas: reduce el impacto en Datos de 6 a 3 entidades nuevas; Presentación pierde los controllers/vistas de Clientes/Upsells/Proyectos de esta iteración.
- Riesgos/supuestos: ninguno nuevo — es una reducción de alcance, no un cambio de dirección. El análisis de `Cliente`/`Upsell`/`Proyecto` ya redactado se conserva en el documento como referencia para la iteración futura, no se descarta.

### 2026-07-14 - disenador-funcional
- Etapa: Diseño
- Cambio: Diseño funcional cerrado sobre el Análisis recortado. 5 pantallas (`Contactos` Index/Details/Create/Edit, `Industrias` CRUD, `Bot/Outbound` panel) con wireframe textual aplicando el Design System (`ov-card`, `ov-badge`, DataTables server-side con filtro por cada columna visible, panel de filtros con Select2/daterangepicker). ViewModels definidos por pantalla. 2 máquinas de estados detalladas evento a evento (`FaseConversacion` del bot, `EstadoEmbudo` comercial) en formato tabla (origen/evento/destino/guarda/acción/error). Matriz de permisos por rol y pantalla. 11 historias de usuario con criterios de aceptación. Plan funcional de 5 etapas para Arquitectura (datos base → servicios migrados → webhook+scheduler → pantallas → corte y migración de datos en tránsito).
- Motivo: convertir el Análisis aprobado en diseño implementable, listo para que Arquitectura evalúe impacto técnico.
- Impacto en capas: Presentación (5 pantallas nuevas), Negocio (contratos funcionales de `BotFlowService`/`OutboundCampaignService`/cálculo de presupuesto), Datos (requerimientos de `Contacto`/`ContactoRespuesta`/`IndustriaCatalogo` por pantalla).
- Riesgos/supuestos: el mecanismo exacto de corte de producción (DNS/proxy del webhook de Meta) y el importador de datos en tránsito quedan para Arquitectura, sin pantalla propia (tarea técnica de una sola vez). Permiso de Vendedor para cambiar estado manual de un Contacto queda marcado "a confirmar en Arquitectura" — por defecto no habilitado.

### 2026-07-14 - arquitecto-mvc
- Etapa: Arquitectura
- Cambio: Arquitectura técnica cerrada. Definidas 4 entidades Domain (`Contacto`, `ContactoRespuesta`, `IndustriaCatalogo`, `GoogleMapsQueryUsada`, esta última reemplaza `queries_used.txt`) + 4 enums (`CanalOrigen`, `FaseConversacion`, `EstadoEmbudo`, `PlanSistema`). Application: `IWhatsAppClient`, `IGoogleMapsService`, `IBotFlowService`, `IOutboundCampaignService` + 3 clases de Settings (`WhatsAppSettings`/`GoogleMapsSettings`/`BotSettings`, secciones `Olvidata_WhatsApp`/`Olvidata_GoogleMaps`/`Olvidata_Bot`). Mapa completo de reutilización de BotPublicitario: `WhatsAppClient`/`GoogleMapsService` se portan sin cambio de lógica (solo pasan de env vars a `IOptions<T>`); `BotFlowService`/`OutboundCampaignService`/`OutboundSchedulerService` se migran a operar contra `AppDbContext`; `MessageLogService`/`ExcelTrackerService` no se portan (su función la cubre `AuditLog` + la tabla `Contacto`); `TemplateCreationService`/`CatalogService`/`MetaAdsClient` quedan fuera. Web: 3 controllers nuevos reutilizando policies ya existentes (`RequireVendedor`, `RequireAdministracion`, sin policies nuevas), webhook de Meta como Minimal API en `Program.cs` sin autenticación de Identity. 1 migración EF (4 tablas nuevas, ninguna existente modificada), sin paquetes NuGet nuevos.
- Motivo: traducir el Diseño aprobado en componentes técnicos concretos, listos para Presupuesto.
- Impacto en capas: las 4 (Domain/Application/Infrastructure/Web) — detalle completo en el documento.
- Riesgos/supuestos: corte de producción resuelto con runbook operativo (QA en ventana aparte → cambiar URL de callback en Meta App Dashboard → decomisionar el proceso viejo), sin bloquear desarrollo. Deduplicación de webhooks por reintentos de Meta se mantiene con la misma limitación conocida de hoy (HashSet en memoria, no persistente) por decisión explícita de preservar comportamiento legacy — no se resuelve preventivamente (YAGNI). Concurrencia en alta de `Contacto` mitigada por índice único + patrón captura-de-duplicado-y-actualiza.

### 2026-07-14 - orquestador (gate de Presupuesto salteado)
- Etapa: Presupuesto — omitida a pedido explícito del cliente ("Saltear la etapa de presupuesto. vamos directo a la implementacion")
- Cambio: no se generó `4-presupuestador.md` para esta iteración. Se pasa directo de Arquitectura (aprobada) a Implementación.
- Motivo: proyecto interno del propio cliente (no hay una parte externa a la que cotizarle) — el cliente decide conscientemente saltear la estimación formal.
- Impacto en capas: N/A.
- Riesgos/supuestos: sin estimación de horas registrada, no hay banda de referencia para el cierre de calibración estimado vs. real de esta iteración. Queda como excepción documentada al flujo estándar del estudio, no como precedente general.
