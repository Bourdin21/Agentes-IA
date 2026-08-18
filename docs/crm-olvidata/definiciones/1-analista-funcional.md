# Memoria - Analista funcional

## Proyecto: crm-olvidata — CRM interno de OlvidataSoft
## Última actualización: 2026-08-14

## Definiciones vigentes

### Resumen del sistema

CRM interno de OlvidataSoft, migrado desde `C:\Sistemas\BotPublicitario` (captación/calificación por WhatsApp, antes en archivos JSON/Excel sueltos, sin BD ni UI) y ampliado en 4 bloques funcionales:
1. **Captación y calificación automática** — bot de WhatsApp con máquina de estados, presupuesto automático por industria.
2. **Campañas de contacto frío configurables** — reemplaza el cronograma/límites/queries que antes vivían hardcodeados en código.
3. **Chats** — conversación directa con el contacto, ventana de 24hs de WhatsApp, multimedia.
4. **Gestión comercial y herramientas de canal/venta** — cartera de clientes, upsells, dashboards, templates editables, A/B testing, asistente de redacción, pipeline visual (en curso de implementación al 2026-08-14).

`Cliente`/`Upsell`/`Proyecto` (gestión comercial) estuvieron pospuestos desde el Discovery original (2026-07-14) hasta el 2026-08-14, cuando `Cliente`/`Upsell` se retomaron; `Proyecto` queda fuera definitivamente (ver Exclusiones).

### Entidades vigentes (Domain)

| Entidad | Origen | Campos clave |
|---|---|---|
| `Contacto` | Migración BotPublicitario (`Prospect`+`ConversationState` unificados) | Telefono (único), Email, NombreContacto, NombreNegocio, Rubro, Zona, CanalOrigen, ReferidoPor, FaseConversacion, Categoria, EstadoEmbudo, PresupuestoCotizadoUsd, FechaUltimaLecturaAgente, MarcadoNoLeidoManual, FechaUltimaAlertaVentana |
| `ContactoRespuesta` | Migración (`QA` de calificación) | Pregunta, Respuesta, MediaId/MediaMimeType (adjuntos), VarianteExperimento (A/B) — 1:N con Contacto |
| `IndustriaCatalogo` | Migración (tabla hardcodeada) | Nombre, SistemaReferencia, Plan, PrecioBaseUsd, CotizaAutomatico, PainHook |
| `GoogleMapsQueryUsada` | Migración | Rubro, Query — rotación de búsquedas ya usadas |
| `CampanaOutbound` | 2026-07-21 (campañas configurables) | Nombre, Region, Dias (7 valores posibles), HoraEnvio, ZonaHoraria, LimiteDiario, TemplateWhatsApp, Activa |
| `CampanaOutboundIndustria` | 2026-07-21 | CampanaOutboundId, IndustriaCatalogoId (nullable), ClaveRubro (única entre campañas activas) |
| `CampanaQuery` | 2026-07-21 | CampanaOutboundIndustriaId, Query, Zona |
| `Cliente` | 2026-08-14 (gestión comercial) | ContactoId, Plan, TicketAnualUsd, FechaAlta, FechaProximaRenovacion, Activo |
| `Upsell` | 2026-08-14 | ClienteId, Tipo, MontoUsd, Fecha |
| `TemplateWhatsApp` | 2026-08-14 | Nombre, Texto, Rubro, Pais, EstadoAprobacionMeta, Activo |
| `CampanaExperimento` | 2026-08-14 | CampanaOutboundId, TemplateAId/TemplateBId, PorcentajeB, Activo |
| `SugerenciaSeguimiento` | 2026-08-14 | EstadoEmbudo, DiasMinimo/Maximo, Rubro, Texto |

### Casos de uso vigentes

| # | Caso de uso | Actor | Nota |
|---|---|---|---|
| CU-01 | Alta manual de contacto | SuperUsuario | Teléfono único (cualquier país), Nombre, Negocio, Rubro, Email opcional |
| CU-02 | Listado/búsqueda de contactos | SuperUsuario | Filtros por EstadoEmbudo, CanalOrigen, Rubro, fecha; orden por columna |
| CU-03 | Lead inbound primer mensaje → bot inicia calificación | Sistema | Salta menú si viene de outbound ya identificado |
| CU-04 | Calificación completa → presupuesto automático | Sistema | Precio base + upsell por usuario excedente, vía `IndustriaCatalogo` |
| CU-05 | Notificación a Joaquín (in-app + WhatsApp) | Sistema | Al calificar o derivar manual |
| CU-06 | Fallback a derivación manual | Sistema | Texto fuera de guion → `EstadoEmbudo=DerivadoManual` |
| CU-10 | Campaña outbound diaria | Sistema | Por campaña: días/hora/zona horaria propios, límite diario propio, follow-up 7d, frío 4d |
| CU-11 | Búsqueda de prospectos por Google Maps | SuperUsuario | Manual, por rubro, sin duplicar por teléfono |
| CU-12 | Mantenimiento del catálogo de industrias/precios | SuperUsuario | CRUD, cambio de precio sin redeploy |
| CU-13 | Crear campaña de contacto frío | SuperUsuario | Industrias + días + límite + template; no activa sin queries cargadas |
| CU-14 | Editar/pausar/reanudar campaña | SuperUsuario | Pausar no afecta contactos en curso |
| CU-15 | Gestionar queries de Google Maps por industria/campaña | SuperUsuario | Reemplaza diccionario hardcodeado |
| CU-16 | Sostener conversación con un contacto desde `Chats` | SuperUsuario | Texto libre sujeto a ventana de 24hs |
| CU-17 | Marcar/desmarcar un chat como no leído | SuperUsuario | Manual, desde la lista, sin abrir el chat |
| CU-18 | Aviso antes de perder la ventana de respuesta | Sistema | Solo `DerivadoManual`, ventana ≤3hs, notificación in-app |
| CU-19 | Ver/escuchar un adjunto multimedia | SuperUsuario | Resuelto bajo demanda contra Meta |
| CU-20 | Enviar presupuesto en PDF desde el chat | SuperUsuario | Pasa el contacto a `PresupuestoEnviado` |
| CU-21 | Convertir un contacto cerrado en Cliente | SuperUsuario | Desde `Contactos`/`Chats`, solo si `EstadoEmbudo=Cerrado` |
| CU-22 | Ver cartera de clientes y próximas renovaciones | SuperUsuario | Semáforo por `FechaProximaRenovacion` |
| CU-23 | Registrar un upsell a un cliente | SuperUsuario | Alta rápida desde la ficha del cliente |
| CU-24 | Dashboard de métricas de negocio | SuperUsuario | NRR, ticket promedio real, avance hacia la meta |
| CU-25 | Dashboard de métricas por campaña/rubro/país | SuperUsuario | Tasa de respuesta/avance/cierre cruzada |
| CU-26 | Mantener catálogo de templates de WhatsApp | SuperUsuario | Reemplaza la lista fija hardcodeada |
| CU-27 | Configurar experimento A/B en una campaña | SuperUsuario | 2 templates + % de split |
| CU-28 | Sugerencia de mensaje de seguimiento | SuperUsuario | Prellena, no envía solo |
| CU-29 | Pipeline visual + conversión por etapa | SuperUsuario | Sin desglose de motivo (dato no capturado) |

*(`CU-07`/`CU-08`/`CU-09`, numeración original de "Conversión a Cliente"/"Registro de Upsell"/"Proyecto pospuesto" — reemplazados por `CU-21`/`CU-23`; `CU-09`/Proyecto queda excluido, ver más abajo.)*

### Máquinas de estado vigentes

**`FaseConversacion`** (conversación del bot, vida corta): `Nuevo → AwaitingCategory → AwaitingIndustry → AskingQuestions → Completed`.

**`EstadoEmbudo`** (embudo comercial, vida larga) — enum real, `OlvidataCRM.Domain/Enums/EstadoEmbudo.cs`:
`Pendiente(1) → MensajeEnviado(2) → FollowUpEnviado(3) → Respondido(4) → PresupuestoEnviado(5) → Cerrado(9) / Frio(10) / Descartado(11) / DerivadoManual(12)`.
Los valores 6-8 (`DemoSolicitada`/`DemoRealizada`/`PropuestaEnviada`) definidos en la primera versión de este documento (2026-07-14) **nunca se implementaron y se eliminaron formalmente de las definiciones el 2026-08-14** — el seguimiento de demo/propuesta se maneja directo por conversación en `Chats`, sin estado de embudo dedicado por etapa intermedia. Selector manual de estado (`ContactosController`/`ChatsController`): solo `[Cerrado, Descartado]`, no permite volver a `Pendiente`.

### Permisos vigentes

Único rol del sistema: `SuperUsuario` (policy `RequireSuperUsuario`), desde el 2026-07-21. `Administrador`/`Vendedor`/`Empleado` no existen en `SeedData` — cualquier mención a ellos en versiones anteriores de este documento queda obsoleta.

### Exclusiones confirmadas (vigente)

- `Proyecto`/pipeline de Build con hitos de cobro — el cliente lo lleva en otro proyecto propio (VirtualWallet), decisión explícita de no duplicar carga entre 2 sistemas (2026-08-14).
- Facturación/cobros — manual, fuera de alcance.
- Motivo estructurado al marcar Frío/Descartado, tareas/recordatorios automáticos de seguimiento, tracking sistemático de fuente de referido — evaluados junto con la propuesta de los agentes de negocio y descartados explícitamente por el cliente (2026-08-14).
- Campañas de Meta Ads (`MetaAdsClient`, scripts Python) — fuera de alcance siempre, no se tocan.
- Carga de clientes históricos (sistemas ya construidos antes del CRM) — el CRM arranca vacío, no se cargan retroactivamente.
- Integración automática con la API de creación de templates de Meta — la gestión de templates (CU-26) es local; la aprobación real sigue siendo un paso manual en Meta Business Manager.

### Supuestos y dependencias vigentes

- MySQL + EF Core, reutilización de `WhatsAppClient`/`GoogleMapsService` de BotPublicitario sin reescritura.
- Credenciales de Meta WhatsApp Business API y Google Maps Places API ya configuradas en producción.
- Templates de WhatsApp aprobados hoy: `olv_frio_v3` (único usado en campañas activas), `olv_referido_v2` (fijo para referidos), `olv_nurturing_v2` (fijo para follow-up).
- NRR (dashboard de negocio) requiere datos históricos de `Upsell` — con la tabla vacía, el primer período muestra "datos insuficientes", no un número aproximado.

## Historial de ajustes

- 2026-07-14: Discovery + Análisis cerrados. Migración de BotPublicitario — 3 entidades (`Contacto`, `ContactoRespuesta`, `IndustriaCatalogo`), 9 casos de uso (CU-01 a CU-06, CU-10 a CU-12). `Cliente`/`Upsell`/`Proyecto` (gestión comercial) pospuestos a pedido del cliente. Webhook absorbido en `OlvidataCRM.Web`, CRM arranca vacío, desarrollo en ventana aparte de proyectos pagos.
- 2026-07-21: Discovery + Análisis de "campañas de contacto frío configurables" — reemplaza `RunDayByType`/`RubrosByDay`/`QueriesByRubro`/`BotSettings.DailyLimit` hardcodeados por 3 entidades nuevas (`CampanaOutbound`, `CampanaOutboundIndustria`, `CampanaQuery`) + 3 CU (CU-13/14/15) + 2 HU. Límite diario = solo suma de campañas activas, sin tope global (riesgo aceptado). Mismo día: cliente simplifica el sistema a un único rol (`SuperUsuario`).
- 2026-07-24: Análisis exprés de un ajuste cosmético en Notificaciones (ícono + modal de confirmación) — sin CU nuevo.
- 2026-08-14: Auditoría de proyecto detectó que todo lo construido desde el 2026-07-29 (pantalla `Chats`, scheduler multi-zona horaria, 6 campos nuevos, reestructuración de campañas) nunca pasó por Análisis formal, y que los estados `DemoSolicitada`/`DemoRealizada`/`PropuestaEnviada` prometidos en 2026-07-14 nunca se implementaron. Cerrada la sección "Chats" retroactiva (5 CU nuevos, CU-16 a CU-20) y eliminados formalmente los 3 estados no implementados. Detectado y corregido `CRM-001` del catálogo de QA como obsoleto (no pendiente) — el cliente había eliminado toda la funcionalidad de Auditoría el 2026-07-28.
- 2026-08-14: Discovery + Análisis de "Gestión comercial y herramientas de canal/venta" — consulta paralela a `olvidata-ceo`/`olvidata-marketing`/`olvidata-sales`, selección del cliente sobre las 3 listas priorizadas. 5 entidades nuevas (`Cliente`, `Upsell`, `TemplateWhatsApp`, `CampanaExperimento`, `SugerenciaSeguimiento`), 9 CU nuevos (CU-21 a CU-29). Excluidos: `Proyecto` (vive en VirtualWallet), motivo estructurado de pérdida, tareas/recordatorios automáticos, tracking de fuente de referido.
- 2026-08-14: Reestructuración documental — este archivo tenía 5 secciones fechadas acumuladas (una por ronda de Discovery/Análisis desde 2026-07-14) con correcciones parcheadas al lado de datos viejos en vez de reemplazarlos. Consolidado en una única sección "Definiciones vigentes" (editada in-place de ahora en más, ver `.github/instructions/29-trazabilidad-conversacion.instructions.md` para la regla) + este historial, que es la única zona que sigue creciendo por append. Ningún dato funcional se perdió en la consolidación — mismo contenido, presentado como estado actual en vez de capas superpuestas.
