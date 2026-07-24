# Memoria - Analista funcional

## Proyecto: crm-olvidata — CRM interno de OlvidataSoft
## Última actualización: 2026-07-14

---

## Discovery (CERRADO — 2026-07-14)

**Decisiones del cliente (2026-07-14):**
1. Alcance = **Opción B, CRM + gestión comercial**: contactos/leads/clientes + planes contratados, upsells, recordatorios de renovación anual y pipeline de proyectos (hoy a mano en `plan_ventas_olvidata.md`).
2. Relación con `docs/meta-ads/` = **Opción A, absorción**: la máquina de estados de calificación (N1-N7) y el cálculo de presupuesto automático se construyen dentro de este CRM. El Webhook de Meta pasa a escribir contra las tablas del CRM. El análisis ya cerrado en `docs/meta-ads/definiciones/1-analista-funcional.md` (casos de uso, tabla de industrias/precios, máquina de estados) se reutiliza como insumo directo para el Análisis funcional de este proyecto — no se re-releva desde cero.

Preguntas #3 (alcance exacto del endpoint webhook), #4 (carga inicial de clientes históricos) y #5 (prioridad vs. proyectos pagos) quedan abiertas para resolverse en Análisis, sin bloquear su inicio.

### 1. Contexto y objetivo del requerimiento

OlvidataSoft ya opera `C:\Sistemas\BotPublicitario`, un conjunto de proyectos .NET que automatiza captación por WhatsApp (Ads pagos + outbound frío) y creación de campañas Meta Ads. Ese código funciona en producción hoy (envía outbound diario, recibe y logea respuestas), pero **no tiene ninguna base de datos ni pantalla**: toda la persistencia es archivos sueltos (JSON por contacto, `outbound_state.json`, `contacted_phones.txt`, `messages_log.jsonl`, `contactos.xlsx`). Joaquín no tiene visibilidad centralizada de sus leads/clientes — se entera de un lead nuevo por el mensaje de WhatsApp que el bot le manda, o abriendo archivos a mano.

El pedido: investigar si conviene migrar BotPublicitario a .NET (stack del estudio) y evaluar construir un nuevo proyecto **CRM Olvidata**, sobre la base `C:\Sistemas\blankproject`, para centralizar contactos, clientes y demás lógica del emprendimiento en un sistema con base de datos y UI real, igual que el resto de los sistemas del estudio.

### 2. Hallazgo clave de la investigación — no hace falta "migrar a .NET"

Se relevó el código real de `C:\Sistemas\BotPublicitario` (no la documentación previa, que no existía a este nivel de detalle):

| Proyecto | Stack real | Rol |
|---|---|---|
| `Olvidata.Webhook` | .NET 9, ASP.NET Core (`AspNetCoreHostingModel=OutOfProcess`) | Recibe el POST de Meta, corre `BotFlowService` (máquina de estados de calificación), logea a JSONL |
| `Olvidata.WhatsApp` | .NET 9, consola | `WhatsAppClient`, `MessagingService`, `OutboundCampaignService` (outbound frío/referido/nurturing con cronograma por rubro), `ExcelTrackerService`, `TemplateCreationService`, `CatalogService`, `GoogleMapsService` |
| `Olvidata.GoogleMaps` | .NET 9, consola | Geocoding/Places para relevar prospectos por zona |
| `MetaAds` | Mixto: cliente C# (`MetaAdsClient`, `OlvidataCampaignBuilder`) + **scripts Python sueltos** (`facebook-business` SDK) | El C# es el flujo productivo (creación de campañas). Los `.py` (`check_ig.py`, `discover_ig.py`, `raw_check.py`, etc.) son utilitarios de descubrimiento de tokens/IDs usados una vez al setup inicial, no corren en el flujo diario |

**Conclusión:** el código productivo ya es 100% .NET 9 — mismo lenguaje/runtime que recotrack, ganaderia, ShowroomGriffin, etc. (.NET 10). No hay nada que "migrar de lenguaje". El único ajuste real de alineación sería subir `TargetFramework` de `net9.0` a `net10.0`, que es un bump de versión, no una migración de stack. Los scripts Python son marginales (setup one-off) y no bloquean nada.

**La brecha real no es de lenguaje, es de arquitectura y persistencia:**
1. No hay base de datos relacional — todo vive en archivos JSON/txt/Excel sueltos por proceso.
2. No hay separación en capas (Domain/Application/Infrastructure/Web) — cada carpeta es un proyecto de consola independiente sin dominio compartido.
3. No hay UI de administración — cero pantallas, cero listados, cero filtros. Visibilidad = leer archivos o esperar el mensaje de WhatsApp que el bot le manda a Joaquín.

Por lo tanto, el pedido real no es "migrar BotPublicitario a .NET" (ya lo es), sino **construir el CRM que falta sobre `blankproject`, reutilizando los servicios .NET ya construidos de BotPublicitario** (`WhatsAppClient`, `MessagingService`, `GoogleMapsService`, `MetaAdsClient`) en vez de reescribirlos, y reemplazando la persistencia en archivos por entidades reales con EF Core + MySQL.

### 3. Modelo de datos actual relevado (candidato a convertirse en entidades)

- `Prospect` (`WhatsApp/ProspectModels.cs`): lead de outbound — Phone, ContactName, BusinessName, BusinessType, Zone, Address/Lat/Lng, Source, ReferredBy/ReferredPain, `ProspectStatus` (Pending→MessageSent→FollowUpSent→Responded→Interested→DemoScheduled→DemoDone→ProposalSent→Closed / Cold / Discarded), timestamps, Notes.
- `ConversationState` (`Webhook/ConversationState.cs`): conversación inbound — Phone, Name, `ConversationPhase` (New→AwaitingCategory→AwaitingIndustry→AskingQuestions→Completed), Category, Industry, respuestas (`QA` pregunta/respuesta), IsOutbound, timestamps.
- `CampaignState`: contenedor de todos los `Prospect` de una campaña outbound + límites diarios.
- **Problema detectado:** un mismo contacto puede existir a la vez como `Prospect` (si vino de outbound) y como `ConversationState` (cuando responde), vinculados solo por comparar el string del teléfono entre dos archivos JSON distintos (`BotFlowService.GetOutboundIndustry`). No hay identidad unificada real.

### 4. Trabajo previo relacionado ya en `/docs` (relevante para no duplicar)

`docs/meta-ads/definiciones/1-analista-funcional.md` tiene un **Análisis funcional ya CERRADO (2026-07-01)** para una extensión de BotPublicitario llamada "Bot de respuesta automática WhatsApp": agrega parseo de `referral`, máquina de estados de calificación por rubro, motor de calificación, calculador de presupuesto automático (13 industrias reales mapeadas a Starter/Pro/Premium/Scale según `precios.astro`) y notificación a Joaquín. Ese análisis asume que la extensión se construye **dentro de BotPublicitario**, con el mismo patrón de persistencia en archivo (ver pregunta abierta #2 más abajo — es la decisión más importante antes de avanzar).

### 5. Alcance inicial — hipótesis a validar en Análisis

**Incluido (hipótesis):**
- Entidad `Contacto`/`Lead` unificada — reemplaza `Prospect` + `ConversationState` + las entradas de `outbound_state.json`, con Id propio, historial de conversación, canal de origen (Ads/Outbound/Referido), estado de embudo, rubro/industria, presupuesto cotizado.
- Entidad `Cliente` (contacto que cerró) — plan contratado, ticket, fecha de alta. Reemplaza el tracking manual que hoy vive en tablas a mano dentro de `plan_ventas_olvidata.md`.
- Pantalla de listado de contactos/clientes (DataTable) con filtros por estado, rubro y canal — la visibilidad que hoy no existe.
- Reutilización de los servicios de mensajería/GoogleMaps/MetaAds existentes (no se reescriben desde cero).

**No incluido inicialmente (hipótesis):**
- No reemplaza el endpoint público que recibe el webhook de Meta (sigue existiendo, solo cambiaría a qué persistencia escribe) — ver pregunta #3.
- No incluye facturación/cobros (hoy es manual, fuera de alcance salvo pedido explícito).
- No incluye tocar las campañas de Meta Ads (scripts Python) — son one-off, no forman parte de este alcance.

### 6. Riesgos tempranos

- **Duplicación con `docs/meta-ads/`**: si no se decide dónde vive la máquina de estados de calificación (N1-N7 ya analizados ahí), se puede terminar construyendo la misma lógica dos veces en dos proyectos distintos.
- **BotPublicitario está en producción activa** (outbound diario real + webhook recibiendo leads reales, fuente de ingresos actual) — cualquier cambio de persistencia (archivo→DB) tiene que hacerse sin cortar el flujo de ventas en curso.
- **Hosting del Webhook**: usa `OutOfProcess` + un proxy PHP (`Webhook/proxy/whatsapp.php`), lo que sugiere hosting compartido con restricciones (no IIS nativo con ANCM). Confirmar restricciones de infraestructura antes de Arquitectura.
- **Convivencia con Excel** (`contactos.xlsx` como fuente de carga de prospectos outbound): si el CRM pasa a ser fuente de verdad, hay que definir el mecanismo de alta de prospectos nuevos (¿se sigue subiendo Excel? ¿alta manual en el CRM? ¿importador?).

### 7. Supuestos

- Se reutiliza la infraestructura de mensajería existente (`WhatsAppClient`, `MessagingService`, `GoogleMapsService`) sin reescritura, portándola a una capa Infrastructure del nuevo proyecto.
- El nuevo proyecto es de uso interno exclusivo de Joaquín (no multi-tenant como century-21 SaaS) — a confirmar en pregunta #1.
- MySQL como motor, consistente con el resto del stack del estudio.
- No se toca la capa de negocio de las campañas de Meta Ads (scripts Python), quedan como están.

### 8. Preguntas abiertas (con ejemplos, hipótesis a validar — bloqueantes marcadas)

**#1 — BLOQUEANTE. Alcance de "demás lógica del emprendimiento":**
- *Opción A (CRM puro):* solo contactos/leads/clientes + historial de conversación + estado de embudo. Análogo a un HubSpot simplificado, sin más.
- *Opción B (CRM + gestión comercial):* todo lo de A, más planes contratados por cliente, upsells, recordatorios de renovación anual, pipeline de proyectos — lo que hoy Joaquín lleva a mano en `plan_ventas_olvidata.md` y en la cabeza (ej. la tabla de "Cliente/Pack/Funciones nuevas/Efectivo" de ese documento pasaría a ser una pantalla real).

**#2 — BLOQUEANTE. Relación con `docs/meta-ads/` (bot de calificación N1-N7, ya analizado y cerrado):**
- *Opción A (absorción):* la máquina de estados de calificación y el cálculo de presupuesto automático se construyen dentro de este nuevo CRM — el Webhook de Meta pasa a escribir contra las tablas del CRM en vez de JSON. El análisis ya cerrado en meta-ads se reutiliza como insumo (casos de uso, tabla de industrias/precios), pero la implementación se mueve acá.
- *Opción B (convivencia):* BotPublicitario sigue siendo el bot standalone tal cual está (con su propia persistencia en archivo), y el CRM solo importa/lee esos datos periódicamente para dar visibilidad, sin ser la fuente de verdad operativa del bot en tiempo real.

**#3 — Alcance del webhook público de Meta:**
- *Opción A:* el endpoint que recibe el POST de Meta se absorbe como un controller más dentro de `BlankProject.Web` del nuevo sistema.
- *Opción B:* el `Olvidata.Webhook` actual se mantiene standalone (por las restricciones de hosting ya resueltas con el proxy PHP), y solo se le cambia el destino de persistencia (llama a la base del CRM vía API o conexión directa en vez de escribir JSON).

**#4 — Carga inicial de clientes históricos:**
¿El CRM arranca con los clientes ya existentes cargados (vinosefue, ganaderia, ShowroomGriffin, Century 21, etc. — listados en `.github/copilot-instructions.md`) como carga inicial de datos, o arranca vacío y se carga solo a medida que entran leads/clientes nuevos desde el bot?

**#5 — Prioridad frente a proyectos pagos activos:**
Este es un proyecto interno sin ingreso directo de un cliente externo. ¿Compite por el tiempo de desarrollo con QA pendiente de ShowroomGriffin/ganaderia y trabajo activo de vinosefue, o se planifica como espacio aparte (ej. fines de semana, ventana muerta)? Relevante para el presupuestador más adelante, no bloquea Análisis.

### 9. Condición de paso a Análisis

**Cumplida (2026-07-14).** Preguntas #1 y #2 resueltas por el cliente (ver decisiones al inicio de este documento). Habilitado el pase a Análisis funcional.

## Análisis funcional (CERRADO — 2026-07-14)

**Decisiones del cliente que cierran las preguntas #3-#5 pendientes de Discovery:**
- **#3 Webhook:** se absorbe como controller/endpoint dentro de `OlvidataCRM.Web` (mismo proceso, misma BD vía `AppDbContext`). Se valida en Arquitectura si el hosting final del CRM soporta esto sin el proxy PHP que usa hoy BotPublicitario en su hosting compartido.
- **#4 Carga inicial:** el CRM arranca **vacío**. No se cargan como `Cliente` los sistemas ya construidos (vinosefue, ganaderia, ShowroomGriffin, etc.) — se cargan a mano más adelante si hace falta.
- **#5 Prioridad:** este desarrollo se planifica en una **ventana aparte**, sin competir por las horas ya comprometidas con QA pendiente de ShowroomGriffin/ganaderia ni con vinosefue. Dato para el Presupuestador, no cambia el alcance funcional.

### 1. Resumen del problema

Migrar a `OlvidataCRM` la funcionalidad de `BotPublicitario`: captación y calificación automática de leads por WhatsApp (ads pagos + outbound frío), hoy dispersa en archivos (JSON/Excel/txt), para que corra contra una base de datos real con visibilidad en el CRM. La lógica de calificación/presupuesto automático ya fue analizada y cerrada en `docs/meta-ads/` — se reutiliza como insumo.

**Recorte de alcance (2026-07-14, a pedido del cliente):** por ahora se migra únicamente lo que corresponde a BotPublicitario (captación, calificación, presupuesto automático, outbound, notificación). La capa de "gestión comercial" (`Cliente`, `Upsell`, `Proyecto`/pipeline) que se había definido en la primera pasada de este Análisis **se pospone a una iteración posterior** — no se descarta, pero no forma parte de esta implementación. Las secciones de este documento que las mencionan quedan como referencia para esa iteración futura, marcadas explícitamente.

### 2. Alcance incluido / excluido

**Incluido (esta iteración — migración de BotPublicitario):**
- Entidad `Contacto` unificada (reemplaza `Prospect` + `ConversationState`), con historial de conversación, canal de origen, estado de embudo, calificación y presupuesto cotizado.
- Máquina de estados de calificación del bot (idéntica en lógica a `BotFlowService` de BotPublicitario), ahora persistida en la BD del CRM.
- Cálculo de presupuesto automático por industria (catálogo de precios editable desde el CRM, no hardcodeado en código como hoy).
- Campaña outbound diaria (cronograma por rubro, límites, follow-up, marcado en frío) — misma lógica de `OutboundCampaignService`, ahora contra BD.
- Búsqueda de prospectos por Google Maps (`GoogleMapsService`, reutilizado tal cual) con carga directa como `Contacto`.
- Notificación in-app (`Notification`, ya existente en la base técnica) + WhatsApp a Joaquín cuando un lead califica o pide demo.
- Webhook de Meta absorbido como endpoint dentro de `OlvidataCRM.Web`.
- Listado/búsqueda de contactos con visibilidad de estado (lo que hoy no existe) y alta manual básica.

**Excluido de esta iteración (pospuesto, no descartado):**
- Gestión comercial: `Cliente` (contacto que cerró: plan, ticket, renovación), `Upsell` (historial de ventas adicionales), `Proyecto` (pipeline de propuestas). Queda para una iteración posterior — Discovery/Análisis futuro definirá cuándo.
- Facturación/cobros — sigue siendo manual.
- Campañas de Meta Ads (`MetaAdsClient`, scripts Python) — quedan como están, fuera de este alcance.
- Carga de clientes históricos — no aplica mientras no exista `Cliente` en esta iteración.
- Dashboards/reportes de KPIs (ticket efectivo, tasa demo→cierre, etc. de `plan_ventas_olvidata.md`) — dependen de `Cliente`/`Upsell`, quedan pospuestos junto con ellos.
- Gestión de plantillas de WhatsApp (`TemplateCreationService`) — se reutiliza el servicio existente sin UI propia en el CRM por ahora.

**Dependencias:**
- Credenciales Meta (WhatsApp Business API) y Google Maps API ya existentes y funcionando en BotPublicitario — se reconfiguran en el CRM (appsettings/user-secrets), no se regeneran.
- Plantillas de WhatsApp (`olv_frio_v2`, `olv_referido_v2`, `olv_nurturing_v2`) ya aprobadas por Meta — deben seguir funcionando igual tras la migración del cliente que las invoca.

### 3. Entidades — resumen funcional

**De esta iteración (Domain):**

| Entidad | Reemplaza / origen | Campos clave |
|---|---|---|
| `Contacto` | `Prospect` + `ConversationState` unificados | Telefono (único), NombreContacto, NombreNegocio, Rubro, Zona, CanalOrigen, ReferidoPor, FaseConversacion, Categoria, EstadoEmbudo, PresupuestoCotizadoUsd, fechas de seguimiento |
| `ContactoRespuesta` | `QA` (preguntas/respuestas de calificación) | Pregunta, Respuesta, Fecha — 1:N con Contacto |
| `IndustriaCatalogo` | tabla hardcodeada en `BotFlowService`/docs meta-ads | Nombre, SistemaReferencia, Plan, PrecioBaseUsd, CotizaAutomatico, PainHook |

**Pospuestas a iteración futura (gestión comercial — NO se implementan ahora):**

| Entidad | Reemplaza / origen | Campos clave |
|---|---|---|
| `Cliente` | tabla manual de `plan_ventas_olvidata.md` | Plan contratado, TicketAnualUsd, UsuariosIncluidos, FechaAlta, FechaProximaRenovacion, Estado |
| `Upsell` | catálogo de upsells de `plan_ventas_olvidata.md` §8 | Tipo, MontoUsd, Fecha — 1:N con Cliente |
| `Proyecto` | pipeline mental de Joaquín | Tipo (Build/Rent/Merge/Landing/AMedida), Estado, MontoPresupuestadoUsd, fechas |

**Simplificación relevante:** `CampaignState` (JSON con `TotalSent`/`CurrentMonth`/`DailyLimit`) desaparece como entidad propia — con BD real, esos números se calculan por consulta directa sobre `Contacto` (ej. `COUNT(*) WHERE EstadoEmbudo = MensajeEnviado AND fecha = hoy`), no hace falta mantener un contador aparte.

### 4. Casos de uso principales y criterios de aceptación

**De esta iteración:**

| # | Caso de uso | Actor | Criterio de aceptación |
|---|---|---|---|
| CU-01 | Alta manual de contacto | Vendedor+ | Formulario Create (Teléfono único, Nombre, Negocio, Rubro, CanalOrigen=Manual); al guardar aparece en el listado con EstadoEmbudo=Pendiente |
| CU-02 | Listado/búsqueda de contactos | Vendedor+ | DataTable con filtros por EstadoEmbudo, CanalOrigen, Rubro y rango de fecha |
| CU-03 | Lead inbound primer mensaje → bot inicia calificación | Sistema (Webhook) | Al llegar el primer webhook de un teléfono nuevo se crea el `Contacto`, arranca `FaseConversacion` correspondiente (salta menú si viene de outbound ya identificado) y se envía el mensaje de bienvenida |
| CU-04 | Calificación completa → presupuesto automático | Sistema | Al completar rubro + cantidad de usuarios, se mapea a `IndustriaCatalogo`, se calcula PrecioBase + upsell por usuario excedente, se envía por WhatsApp y se guarda en `Contacto.PresupuestoCotizadoUsd`; `EstadoEmbudo` pasa a PresupuestoEnviado |
| CU-05 | Notificación a Joaquín | Sistema | Al calificar o pedir demo se crea una `Notification` in-app (campanita) + WhatsApp a `ADMIN_NOTIFY_PHONE`, mismo contenido en ambos canales |
| CU-06 | Fallback a derivación manual | Sistema | Texto fuera de guion → `EstadoEmbudo=DerivadoManual`, mensaje al lead + notificación a Joaquín |
| CU-10 | Campaña outbound diaria | Sistema (hosted service) | Mismo comportamiento que `OutboundCampaignService` hoy (cronograma por rubro, límite diario, follow-up a 7 días, frío a 4 días sin respuesta), ahora contra `Contacto` en BD |
| CU-11 | Búsqueda de prospectos por Google Maps | SuperUsuario | Ejecuta búsqueda por rubro/zona y carga resultados como `Contacto` nuevo, sin duplicar por teléfono |
| CU-12 | Mantenimiento del catálogo de industrias/precios | SuperUsuario | CRUD sobre `IndustriaCatalogo` en Herramientas del sistema; un cambio de precio se refleja en el próximo cálculo sin tocar código |

**Pospuestos a iteración futura (gestión comercial — NO se implementan ahora):**

| # | Caso de uso | Actor | Nota |
|---|---|---|---|
| CU-07 | Conversión de Contacto a Cliente | Administrador/SuperUsuario | Requiere entidad `Cliente`, pospuesta |
| CU-08 | Registro de Upsell | Administrador/SuperUsuario | Requiere entidad `Upsell`, pospuesta |
| CU-09 | Alta/edición de Proyecto (pipeline) | Vendedor+ | Requiere entidad `Proyecto`, pospuesta |

### 5. Permisos, estados y validaciones

**Permisos (roles ya existentes en la base técnica: SuperUsuario, Administrador, Vendedor, Empleado) — solo lo de esta iteración:**
- SuperUsuario/Administrador: acceso completo (Contactos, catálogo de industrias, configuración del bot/outbound).
- Vendedor: Contactos (alta/edición/listado) — sin acceso al catálogo de industrias.
- Empleado: solo lectura de Contactos — alcance exacto a confirmar en Diseño.

**Máquinas de estados (de esta iteración):**
1. `FaseConversacion` (conversación del bot, vida corta): `Nuevo → AwaitingCategory → AwaitingIndustry → AskingQuestions → Completed`.
2. `EstadoEmbudo` (embudo comercial, vida larga, fusiona `ProspectStatus` + fallback): `Pendiente → MensajeEnviado → FollowUpEnviado → Respondido → PresupuestoEnviado → DemoSolicitada → DemoRealizada → PropuestaEnviada → Cerrado / Frio / Descartado / DerivadoManual`. Nota: los estados `Cerrado`/`DemoRealizada`/`PropuestaEnviada` quedan como marcas informativas en `Contacto` — sin `Cliente`/`Proyecto` (pospuestos) no disparan ninguna conversión automática esta iteración.

*(`EstadoProyecto` del pipeline queda pospuesto junto con la entidad `Proyecto`.)*

**Validaciones:**
- `Contacto.Telefono` único (resuelve el problema de identidad duplicada detectado en Discovery entre outbound e inbound).
- `IndustriaCatalogo.PrecioBaseUsd` obligatorio (>0) si `CotizaAutomatico = true`.

### 6. Impacto por capa (preliminar)

- **Presentación:** nuevos controllers/vistas Contactos, Catálogo de Industrias (Herramientas del sistema); nuevo endpoint de Webhook de Meta dentro de `OlvidataCRM.Web`.
- **Negocio:** `BotFlowService` (migrado y adaptado a BD), `OutboundCampaignService` (adaptado, como `IHostedService`), cálculo de presupuesto.
- **Datos:** 3 entidades nuevas + migración EF (`Contacto`, `ContactoRespuesta`, `IndustriaCatalogo`), todas heredando `SoftDestroyable` para auditoría/soft-delete automáticos (ya presentes en la base).

### 7. Riesgos y supuestos

- **Corte de producción:** BotPublicitario sigue operando (outbound diario + webhook real) mientras se construye el CRM — hay que definir en Arquitectura un "día D" de corte donde el Webhook deja de escribir JSON y pasa a escribir en la BD del CRM, sin perder leads en tránsito ni duplicar envíos.
- **Migración de datos en tránsito:** si al momento del corte hay prospectos/conversaciones activos en los archivos actuales (`outbound_state.json`, `conversations/*.json`, `contactos.xlsx`), hace falta un import único a `Contacto` — a definir en Arquitectura.
- **Plantillas de Meta:** siguen aprobadas a nombre del mismo WABA; el cliente `WhatsAppClient` se reutiliza sin cambios de configuración de Meta.
- Se asume MySQL + EF Core (ya definido en la base técnica del repo).
- Se asume que el scheduler outbound se implementa como `IHostedService` dentro de `OlvidataCRM.Web` (consistente con la decisión de absorber también el Webhook en el mismo proceso).

### 8. Banderas tempranas

- **Migración EF:** Sí — 3 entidades nuevas (`Contacto`, `ContactoRespuesta`, `IndustriaCatalogo`).
- **Integración externa:** Sí — Meta WhatsApp Graph API y Google Maps Places API (ambas ya resueltas y en producción en BotPublicitario, se reutilizan los clientes existentes).
- **Máquina de estados:** Sí — dos máquinas de estados relacionadas (ver punto 5).

### Condición de paso a Diseño

**Cumplida (2026-07-14).** Preguntas #3-#5 resueltas por el cliente. Alcance recortado a la migración de BotPublicitario (`Cliente`/`Upsell`/`Proyecto` pospuestos). Queda abierta para Diseño la definición exacta de permisos por rol (Vendedor/Empleado) y el mecanismo de corte/migración de datos en tránsito de BotPublicitario — no bloquean el inicio de Diseño.

## Discovery + Análisis — Campañas de contacto frío configurables (CERRADO — 2026-07-21)

**Decisiones del cliente (2026-07-21) que cierran las 5 preguntas bloqueantes:**
1. **Límite diario:** solo suma de campañas — *sin* tope global de seguridad aparte. `BotSettings.DailyLimit` desaparece como límite único; el total diario real es la suma de `LimiteDiario` de las campañas activas programadas ese día. **Riesgo aceptado explícitamente:** no queda ningún freno automático si la suma de límites configurados es alta — la responsabilidad de no sobrecargar el envío diario pasa a quien configura las campañas.
2. **Días de la semana:** quedan fijos Martes/Miércoles/Jueves (`OutboundSchedulerService.RunDays` no cambia) — la campaña solo elige un subconjunto de esos 3 días, igual que la Opción A planteada.
3. **Template de WhatsApp:** selección fija entre los templates ya aprobados y configurados en Meta (`olv_frio_v3`, `olv_referido_v2`, `olv_nurturing_v2`) — sin campo de texto libre. Sumar un template nuevo en el futuro sigue requiriendo un cambio de código (agregarlo a la lista fija), igual que hoy.
4. **Queries de Google Maps:** **entran en el alcance**, editables desde el CRM — esto amplía el alcance original (ver §2 y el CU-15 nuevo más abajo).
5. **Migración:** seed automático — se genera una campaña por cada rubro que hoy tiene entrada en `OutboundCampaignService.RunDayByType`, preservando el día de envío que ya tiene asignado. Como consecuencia directa de la decisión #4 (queries en alcance), **el seed también migra las queries hardcodeadas de `GoogleMapsService.QueriesByRubro`** a filas editables para cada campaña generada — si no se migraran también las queries, las campañas recién creadas arrancarían sin poder buscar prospectos nuevos, una regresión funcional real (viola la regla de "preservar comportamiento legacy" de la operativa global).

**Nota de contexto previa al pedido:** el 2026-07-21 el cliente simplificó los roles del sistema a un único rol (`SuperUsuario`) — se eliminaron `Administrador`/`Vendedor`/`Empleado` de `SeedData`, las policies asociadas y la lógica de permisos diferenciados en `UsersController`. Esto vuelve obsoleta la nota de "permisos exactos de Vendedor/Empleado" que quedaba abierta en la Condición de paso a Diseño de la sección anterior — ya no aplica, todo el sistema opera con un solo nivel de acceso.

### Pedido del cliente

En la pantalla **Bot / Outbound** (`BotController` + `Views/Bot/Index.cshtml`), agregar la posibilidad de **configurar las campañas de contacto frío del bot** en vez de tener el comportamiento hardcodeado en código como está hoy.

### 1. Contexto y estado actual (relevado en código real, no en documentación previa)

Hoy no existe el concepto de "Campaña" como dato — todo vive hardcodeado y disperso en tres servicios, que hay que tocar y **redeployar** para cualquier cambio:

| Qué | Dónde (archivo real) | Contenido |
|---|---|---|
| Cronograma por rubro (envío outbound) | `OutboundCampaignService.RunDayByType` | dict rubro → día (Mar/Mié/Jue) |
| Cronograma por rubro (búsqueda Maps) | `GoogleMapsService.RubrosByDay` | dict día → array de rubros — **duplica** la info de arriba con un set de rubros ligeramente distinto, sincronizados a mano hoy |
| Rubros retirados del barrido | `OutboundCampaignService.RubrosRetirados` | HashSet fijo (`restaurant`, `eventos`) |
| Queries de búsqueda por rubro | `GoogleMapsService.QueriesByRubro` | 13 rubros × 8-15 queries de texto libre + zona |
| Límite diario global | `BotSettings.DailyLimit` | 125, un único valor para todo el pipeline, sin discriminar por rubro |
| Horario de corrida | `OutboundSchedulerService.RunDays` / `RunAt` | Mar/Mié/Jue 09:30 ART, fijo en código |
| Templates de WhatsApp | `OutboundCampaignService` (switch hardcodeado) | `olv_frio_v3` (frío), `olv_referido_v2` (referido), `olv_nurturing_v2` (follow-up) — nombres de templates ya aprobados por Meta |
| Textos por rubro (pain hook, plural, social proof) | `OutboundCampaignService.Plural/PainByType/SocialProofByType` | switch por rubro con fallback genérico |

Ya existe `IndustriaCatalogo` (entidad editable desde el CRM, con `Nombre`, `PainHook`, `PrecioBaseUsd`, `Plan`, `Orden`, `CotizaAutomatico`) pero **no está vinculada** a nada de lo anterior — `Contacto.Rubro` y las claves de los diccionarios de arriba (`"comercio"`, `"farmacia"`, etc.) son strings sueltos, sin FK a `IndustriaCatalogo`.

La pantalla `Bot/Index.cshtml` hoy solo muestra: stats (enviados/pendientes hoy), toggle standby global del scheduler, y búsqueda manual de prospectos por rubro (CU-11).

### 2. Alcance funcional resumido

**Incluido:**
- CRUD de "Campaña de contacto frío": qué industrias barre, qué subconjunto de Mar/Mié/Jue corre, límite diario propio, qué template de WhatsApp usa (de una lista fija), activa/pausada.
- Reemplazo de `OutboundCampaignService.RunDayByType` + `GoogleMapsService.RubrosByDay` + `RubrosRetirados` + `BotSettings.DailyLimit` por datos configurables leídos de la campaña.
- Vínculo real entre campaña e `IndustriaCatalogo` (hoy solo existe el string suelto de rubro).
- **Gestión de queries de búsqueda de Google Maps por industria dentro de una campaña** (texto de búsqueda + zona) — reemplaza `GoogleMapsService.QueriesByRubro` hardcodeado. Cada industria de una campaña mantiene su propia rotación de queries, igual que hoy pero editable sin deploy.

**No incluido:**
- No se edita el *texto* de los templates de WhatsApp ni se crean templates nuevos desde el CRM — la campaña selecciona entre los ya aprobados y configurados en Meta (`olv_frio_v3`, `olv_referido_v2`, `olv_nurturing_v2`).
- No se toca el horario global del scheduler (Mar/Mié/Jue 09:30 ART fijo) ni el toggle standby global existente — la campaña define *qué* se manda esos días (subconjunto de esos 3), no *cuándo* corre el proceso en sí.
- No se agrega ningún tope de seguridad global sobre el total diario — es una decisión explícita del cliente (ver Riesgos §5).

**Dependencias:**
- `IndustriaCatalogo` ya existe y es la base para vincular campañas — necesita un campo nuevo que la cruce con las claves de rubro usadas hoy en `QueriesByRubro` (ej. `"comercio"`, `"dieteticas"`) — a resolver en Diseño/Arquitectura, no es una decisión funcional.
- Los 3 templates de WhatsApp ya están aprobados y en uso — la campaña selecciona entre ellos, no depende de aprobaciones nuevas de Meta.

### 3. Casos de uso principales (numeración correlativa — último usado en el proyecto: CU-12/HU-11)

| # | Caso de uso | Actor | Criterio de aceptación |
|---|---|---|---|
| CU-13 | Crear campaña de contacto frío | SuperUsuario | Define nombre, industrias (1 o más de `IndustriaCatalogo`), subconjunto de días (Mar/Mié/Jue), límite diario, template (lista fija). Falla con mensaje claro si alguna industria ya está asignada a otra campaña activa, o si no se seleccionó ninguna industria. No se puede activar una industria dentro de la campaña sin al menos 1 query de búsqueda cargada (ver CU-15) |
| CU-14 | Editar / pausar / reanudar campaña | SuperUsuario | Misma validación que CU-13. Pausar (`Activa=false`) no reprocesa ni descarta contactos ya en curso (`EstadoEmbudo != Pendiente`) — solo deja de sumarlos al próximo batch y de buscar prospectos nuevos para esas industrias |
| CU-15 | Gestionar queries de búsqueda de Google Maps por industria dentro de una campaña | SuperUsuario | Agregar/editar/quitar pares (texto de búsqueda, zona) para la industria de una campaña, ej. agregar "farmacia Tolosa" / "La Plata GBA Norte" a la rotación de Farmacia. Reemplaza `GoogleMapsService.QueriesByRubro` hardcodeado; la rotación de queries ya usadas (`GoogleMapsQueryUsada`) sigue funcionando igual, solo cambia el origen de la lista |
| HU-12 | Ver estado de campañas en Bot/Outbound | SuperUsuario | Listado (nombre, industrias, días, límite diario, template, estado activa/pausada) visible desde la pantalla principal del bot, con acciones de editar/pausar/eliminar |
| HU-13 | El scheduler outbound opera contra campañas, no contra diccionarios fijos | Sistema | `OutboundSchedulerService`, `OutboundCampaignService` y `GoogleMapsService` leen las campañas activas (industrias, días, límite, template, queries) programadas para el día en vez de `RunDayByType`/`RubrosByDay`/`QueriesByRubro`/`BotSettings.DailyLimit` fijos |

### 4. Permisos, estados y validaciones

- **Permisos:** único rol del sistema (`SuperUsuario`) — sin matices de acceso parcial, coherente con el cambio de roles del 2026-07-21.
- **Validación clave:** una industria/rubro no puede pertenecer a dos campañas activas simultáneamente (evita doble envío el mismo día por campañas superpuestas).
- **Estado de campaña:** `Activa` (bool) — no es una máquina de estados con transiciones encadenadas, es un flag simple con guarda de validación al activar (no se puede activar sin al menos una industria asociada).
- **No hay impacto** sobre las máquinas de estados ya existentes (`FaseConversacion`, `EstadoEmbudo`) — la campaña decide *a quién* y *cuándo* se le envía el primer contacto, no cambia el ciclo de vida del `Contacto` una vez que ya está en curso.

### 5. Riesgos y supuestos

- **Riesgo aceptado — sin tope global de seguridad:** por decisión explícita del cliente (#1), el total diario real de envíos pasa a ser la suma sin control de los límites de cada campaña activa. Si se activan muchas campañas con límites altos el mismo día, no hay ningún mecanismo que lo frene automáticamente — queda a criterio de quien las configura.
- **Riesgo de doble mantenimiento si la migración es parcial:** la migración a campañas debe ser completa en los tres puntos de lectura (`OutboundSchedulerService`, `OutboundCampaignService`, `GoogleMapsService`) — dejar alguno de los diccionarios viejos vivo "por las dudas" reintroduce el problema de desincronización que ya existe hoy entre `RunDayByType` y `RubrosByDay`.
- **Riesgo de regresión si el seed de migración no incluye las queries:** dado que las queries de Maps ahora son parte del dato de la campaña (decisión #4), el seed automático (decisión #5) tiene que migrar también `GoogleMapsService.QueriesByRubro` — si solo migrara el cronograma sin las queries, las campañas nuevas arrancarían sin poder buscar prospectos, cortando la búsqueda real de leads el día del corte.
- **Riesgo de negocio en producción real:** el pipeline outbound ya corre en producción (aunque hoy en `Standby=true` según el último estado registrado en trazabilidad) — cualquier cambio de origen de datos debe probarse contra `Standby=true` primero, sin arriesgar un envío real accidental durante el desarrollo.
- **Supuesto:** se asume que "contacto frío" en el pedido del cliente se refiere específicamente al pipeline de `OutboundCampaignService`/`OutboundSchedulerService` (`CanalOrigen.OutboundFrio` y `Referido`), no a la búsqueda manual por rubro de CU-11 (que seguiría funcionando igual, disparada a mano, no por campaña programada) — a confirmar en Diseño si hace falta.
- **Supuesto:** `IndustriaCatalogo` es la entidad correcta para vincular campañas (ya es editable, ya tiene `PainHook`/`Plan`/`Precio`) en vez de crear un catálogo de "rubros" paralelo.

### 6. Banderas tempranas

- **Migración EF:** Sí — entidades nuevas para campaña, la relación campaña↔industria y las queries de búsqueda por industria/campaña, más un campo nuevo en `IndustriaCatalogo` para cruzar con las claves de rubro (detalle exacto de tablas/claves a definir en Diseño/Arquitectura, no en Análisis).
- **Integración externa:** No nueva — reutiliza las integraciones ya existentes (WhatsApp Business API, Google Maps Places API), solo cambia de dónde lee la configuración.
- **Máquina de estados:** No — `Activa`/`Pausada` es un flag simple, no una máquina de estados con transiciones múltiples.

### Condición de paso a Diseño

**Cumplida (2026-07-21).** Las 5 preguntas fueron resueltas por el cliente (ver decisiones al inicio de esta sección). Habilitado el pase a `2-disenador-funcional.md`.

## Historial de ajustes

- 2026-07-14: Discovery abierto. Relevado el código real de `C:\Sistemas\BotPublicitario` (4 proyectos .NET 9 + scripts Python marginales de setup). Confirmado que no hace falta migración de lenguaje — el gap real es ausencia de base de datos, capas y UI. Detectado solape con análisis ya cerrado en `docs/meta-ads/` (bot de calificación N1-N7). Discovery bloqueado por 2 preguntas al cliente antes de pasar a Análisis.
- 2026-07-14: Análisis funcional cerrado (primera versión). Resueltas preguntas #3-#5 (webhook absorbido en OlvidataCRM.Web, CRM arranca vacío sin carga de clientes históricos, desarrollo en ventana aparte de proyectos pagos). Definidas 6 entidades nuevas, 12 casos de uso, 3 máquinas de estados relacionadas y el mapa de reutilización de servicios de BotPublicitario.
- 2026-07-14: Análisis recortado a pedido del cliente — "por el momento solo voy a migrar lo que corresponde al bot publicitario". Se posponen `Cliente`, `Upsell`, `Proyecto` (gestión comercial) y sus casos de uso (CU-07/08/09) a una iteración futura. Alcance de esta iteración queda en 3 entidades (`Contacto`, `ContactoRespuesta`, `IndustriaCatalogo`) y 9 casos de uso (CU-01 a CU-06, CU-10 a CU-12).
- 2026-07-21: Discovery + Análisis de "campañas de contacto frío configurables" abierto y cerrado en la misma sesión. Relevados los 3 puntos hoy hardcodeados (`OutboundCampaignService.RunDayByType`, `GoogleMapsService.RubrosByDay`/`QueriesByRubro`, `BotSettings.DailyLimit`). Cliente resolvió las 5 preguntas bloqueantes: límite diario = solo suma de campañas (sin tope global), días fijos Mar/Mié/Jue (campaña elige subconjunto), template de selección fija ya aprobado en Meta, queries de Maps SÍ entran en alcance (editables por industria/campaña, amplía el alcance original), migración por seed automático desde `RunDayByType` (incluyendo las queries existentes, para no cortar la búsqueda de prospectos el día del corte). Definidos 3 casos de uso nuevos (CU-13, CU-14, CU-15) + 2 historias (HU-12, HU-13). Condición de paso a Diseño: **cumplida**.
