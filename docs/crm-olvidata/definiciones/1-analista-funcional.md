# Memoria - Analista funcional

## Proyecto: crm-olvidata — CRM interno de OlvidataSoft
## Última actualización: 2026-09-14

## Definiciones vigentes

### Resumen del sistema

CRM interno de OlvidataSoft, migrado desde `C:\Sistemas\BotPublicitario` (captación/calificación por WhatsApp, antes en archivos JSON/Excel sueltos, sin BD ni UI) y ampliado en 4 bloques funcionales:
1. **Captación y calificación automática** — bot de WhatsApp. Desde el 2026-09-14 el camino principal es la conversación con LLM (`ConversacionIaService`); el árbol de estados (`BotFlowService`) queda como fallback.
2. **Campañas de contacto frío configurables** — reemplaza el cronograma/límites/queries que antes vivían hardcodeados en código.
3. **Chats** — conversación directa con el contacto, ventana de 24hs de WhatsApp, multimedia.
4. **Gestión comercial y herramientas de canal/venta** — cartera de clientes, upsells, dashboards, templates editables, A/B testing, asistente de redacción, pipeline visual.

`Cliente`/`Upsell`/`Proyecto` (gestión comercial) estuvieron pospuestos desde el Discovery original (2026-07-14) hasta el 2026-08-14, cuando `Cliente`/`Upsell` se retomaron; `Proyecto` queda fuera definitivamente (ver Exclusiones).

### Entidades vigentes (Domain)

| Entidad | Origen | Campos clave |
|---|---|---|
| `Contacto` | Migración BotPublicitario (`Prospect`+`ConversationState` unificados) | Telefono (único), Email, NombreContacto, NombreNegocio, Rubro, Zona, PaginaWeb (desde 2026-08-20, viene de Google Places), CanalOrigen, ReferidoPor, FaseConversacion, Categoria (texto libre varchar 20: `rent`/`rent_other`/`build`/`merge`/`landing`/`other`), EstadoEmbudo, PresupuestoCotizadoUsd, FechaUltimaLecturaAgente, MarcadoNoLeidoManual, FechaUltimaAlertaVentana, BotPausado |
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
| CU-30 | Clasificar a un prospecto en uno de los frentes vigentes | Sistema (IA) | Feature "4 frentes" (2026-09-14), en Diseño |
| CU-31 | Asignar el gancho del primer contacto frío antes del envío | Sistema | Automático por contacto (web propia + rubro); todos reciben el combo |
| CU-32 | Enviar el primer contacto frío con la plantilla combo del gancho | Sistema | 4 plantillas combo; gancho Gestión cae a `v13` de la campaña |
| CU-33 | Conversación orientada al frente ofrecido, con cambio de frente | Sistema (IA) | Contenido desde módulos por frente |
| CU-34 | Ver y filtrar contactos por frente ofrecido y categoría | SuperUsuario | Contactos y Chats; dashboard fuera |
| CU-35 | Retirar Merge del vocabulario preservando históricos | Sistema | Históricos quedan como "discontinuado" |

*(`CU-07`/`CU-08`/`CU-09`, numeración original de "Conversión a Cliente"/"Registro de Upsell"/"Proyecto pospuesto" — reemplazados por `CU-21`/`CU-23`; `CU-09`/Proyecto queda excluido, ver más abajo.)*

### Máquinas de estado vigentes

**`FaseConversacion`** (conversación del bot, vida corta): `Nuevo → AwaitingCategory → AwaitingIndustry → AskingQuestions → Completed`, más `ConversandoConIa(7)` desde el 2026-09-14 para contactos atendidos por el LLM.

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
- El bot nunca cotiza: no existe herramienta de precio en la conversación con IA (garantía estructural, 2026-09-13).

### Supuestos y dependencias vigentes

- MySQL + EF Core, reutilización de `WhatsAppClient`/`GoogleMapsService` de BotPublicitario sin reescritura.
- Credenciales de Meta WhatsApp Business API, Google Maps Places API y Anthropic API configuradas en producción.
- Plantilla fría vigente para campañas: `olv_frio_v13` (desde 2026-08-28); `olv_referido_v2` (referidos) y `olv_nurturing_v2` (follow-up) fijas.
- NRR (dashboard de negocio) requiere datos históricos de `Upsell` — con la tabla vacía, el primer período muestra "datos insuficientes", no un número aproximado.

*(Sprint "corrección de bugs/gaps de auditoría completa + 3 mejoras" del 2026-08-27: cerrado con QA, detalle en `trazabilidad.md` y `6-qa.md`.)*

### Feature: reorientar el bot de prospección a los 4 frentes (2026-09-14) — ANÁLISIS APROBADO

**Origen:** brief de negocio de `olvidata-ceo` (`trazabilidad.md`, entrada "2026-09-14 (5)"). Análisis aprobado por Joaquín el 2026-09-14, con las 8 preguntas respondidas (ver "Decisiones del cliente"). Habilitado Diseño.

**Problema de negocio:** el bot de prospección (plantilla de primer contacto frío + conversación con IA) solo vende sistemas de gestión. Olvidata vende hoy 4 frentes: **Landing** (2D USD 375/año, 3D USD 600/año), **Build** (gestión), **AI Agents** y **Chatbots** (precios de estos dos confirmados como promo de entrada hasta 2026-12-31). El bot no sabe clasificar ni ofrecer AI Agents/Chatbots, se presenta como "un estudio que desarrolla sistemas de gestión a medida" y sigue aceptando la categoría Merge, dada de baja el 2026-09-13.

**Hechos verificados en el código (2026-09-14):**
- **El dato "tiene web" ya existe:** `GoogleMapsService.GetProspectDetailsAsync` pide `website` en Place Details (mismo SKU "Details + Contact Data" que ya se paga, sin costo extra) y lo guarda en `Contacto.PaginaWeb` desde la migración `AddPaginaWebContacto` (2026-08-20). Los contactos anteriores a esa fecha, manuales o de ads lo tienen vacío.
- **`merge` vive en 3 lugares:** `ConversacionIaService.CategoriasValidas`, `BotFlowService.Questions["merge"]` y `BotFlowService.CategoryNames` (más el comentario de `Contacto.Categoria`). El menú de bienvenida del árbol no lo ofrece: hoy solo la IA puede asignarlo.
- **`Contacto.Categoria` es texto libre** (varchar 20, sin FK): sumar claves nuevas no requiere migración.
- **El árbol de fallback se rompe con categorías desconocidas:** `BotFlowService` indexa `Questions[contacto.Categoria!]` sin chequear si existe la clave.
- **Lo que la IA sabe de cada rubro sale del catálogo de Build** (`consultar_modulos_del_rubro` y los módulos MVP del prompt, desde `ModuloCatalogoIndustria`). El catálogo no tiene dimensión de frente.
- **Las plantillas frías arman sus parámetros 100% desde el rubro** (`Plural`, `NarrativaByType`, `PitchByType` en `OutboundCampaignService`).
- **`CampanaOutboundIndustria.ClaveRubro` es única entre campañas activas:** un mismo rubro no puede estar en 2 campañas activas a la vez (motivo técnico de la decisión P1).
- Outbound y Places están pausados (284 campañas): no hay presión operativa.

**Decisiones del cliente (2026-09-14):**

| # | Pregunta | Decisión |
|---|---|---|
| P1 | Dónde se decide el frente | **Automático por contacto.** Las campañas siguen por rubro/ciudad como hoy. Ajustado en Diseño (2026-09-14): todos reciben el **combo** (Landing 3D + AI Agents + Chatbots) y lo que el sistema asigna por contacto es el **gancho** (por qué dolor abre el mensaje), que define la plantilla. Build y Landing 2D siguen disponibles. |
| P2 | Contactos con web vacía (anteriores al 20/08, manuales, ads) | **Se tratan como "sin web"** → se les ofrece Landing. |
| P3 | Solo Instagram/Facebook/Linktree cargado como web | **No cuenta como web propia** → se les ofrece Landing. |
| P4 | Landing 2D vs 3D | **3D para rubros visuales** (inmobiliarias, indumentaria, showrooms); el resto 2D. Dos plantillas de Landing. |
| P5a | Contactos históricos con `merge` | **Se dejan**, mostrados como "Mejoras en sistema Olvidata (discontinuado)". |
| P5b | Cliente actual pide una mejora | **La IA escala a humano en el acto.** |
| P6 | Contenido de la IA para frentes nuevos | **Módulos por frente en el catálogo de módulos** (ej. Chatbot inmobiliaria → "responder disponibilidad", "agendar visitas"). |
| P7 | Medición por frente | **Filtro en Contactos y Chats**; dashboard por frente queda fuera de este trabajo. |
| P8 | Señal de alto volumen de consultas | **Solo rubro** (sin reseñas de Google). |

**Alcance incluido:**
1. **Vocabulario de categorías:** agregar `ai_agents` y `chatbot`; ninguna alta nueva puede recibir `merge` (ni por IA ni por árbol). `landing` sigue siendo una sola categoría; la variante 2D/3D sale del rubro.
2. **Prompt de la IA:** presentación de Olvidata con los 4 frentes, descripción de cada categoría con ejemplos de dolor, la regla "abrir con el frente que se le ofreció pero cambiar si el prospecto trae otro dolor", y la regla "si es cliente actual pidiendo una mejora → escalar a humano". Sigue sin precios.
3. **Asignación automática del gancho por contacto** (ajuste de Diseño 2026-09-14, combo para todos): sin web propia (vacía, redes, plataformas o marketplaces — solo cuenta dominio propio) → gancho Presencia web; con web propia → según rubro: back-office intensivo → Administración, alto volumen de consultas → Consultas, resto → Gestión.
4. **Primer contacto frío con el combo:** 4 plantillas nuevas, una por gancho, todas ofreciendo Landing 3D + AI Agents + Chatbots (la de Gestión suma Build), con los mismos botones "Sí, contame más" / "No me interesa". Mientras la de Gestión no esté aprobada, ese gancho sigue con la plantilla de campaña (`v13`). Landing 2D no va en el primer mensaje: se ofrece en la propuesta. Los textos pasan por `olvidata-marketing` y por la aprobación de Meta.
5. **Envío con la plantilla del frente asignado**, dentro de las campañas existentes.
6. **Visibilidad:** frente ofrecido y categoría visibles en Contacto y Chat, y filtrables en los listados de Contactos y Chats.
7. **Módulos por frente en el catálogo de módulos**, para que `consultar_modulos_del_rubro` (y los módulos del prompt) sirvan también para Landing, AI Agents y Chatbots. La carga del contenido la define `olvidata-presupuesto-bot`.
8. **Fallback del árbol preparado** para las categorías nuevas (no rompe; escala a humano o hace una pregunta abierta).
9. **Merge histórico** mostrado con etiqueta "discontinuado".
10. **Documentación:** `arbol-comunicacion-bot.md` y `logica-negocio-bot.md` con el flujo de la IA y las categorías nuevas.

**No incluido:**
- Precios o cotización automática en el bot.
- Reactivar outbound o Places (decisión operativa de Joaquín, aparte).
- Dashboard de métricas por frente (P7).
- Cantidad de reseñas de Google como señal (P8).
- Reconsultar Places para contactos con web vacía (P2).
- Reclasificar contactos históricos con `merge` (P5a).
- `marcar_para_retomar` y la plantilla de reenganche para `ConversandoConIa` (pendientes independientes del 14/09).
- Evaluar la calidad de la web existente del prospecto (solo presencia o ausencia de web propia).
- Cambios en anuncios de Meta Ads.
- Gestión de `Cliente`/`Upsell` por frente.

**Dependencias:**
- Textos de las 4 plantillas aprobados por `olvidata-marketing`.
- Aprobación de Meta de las 4 plantillas (categoría MARKETING, puede tardar días o rechazarse).
- Listas de rubros por grupo (visual / back-office / alto volumen de consultas) validadas por Joaquín en Diseño.
- Contenido de módulos por frente definido con `olvidata-presupuesto-bot`.

**Criterios de aceptación:**

- **CU-30**
  - CA1: `set_categoria` acepta `ai_agents` y `chatbot`, y rechaza `merge` con el mensaje de categoría inválida.
  - CA2 (verificable con mensajes de prueba al webhook): "se nos pierden consultas de WhatsApp fuera de horario" → `chatbot`; "pierdo horas conciliando el banco con Mercado Pago" → `ai_agents`; "no tengo página" → `landing`; "el stock no me cierra" → `rent`/`rent_other`.
  - CA3: la IA no menciona precios ni plazos en ningún frente.
  - CA4: la IA no le ofrece "mejoras sobre un sistema Olvidata" a un prospecto frío; si un cliente actual pide una mejora, escala a humano en ese mismo mensaje.
- **CU-31**
  - CA1: cada contacto elegible para envío tiene un frente asignado y visible antes del envío (no se decide sin dejar rastro).
  - CA2: web vacía, o URL de Instagram/Facebook/Linktree → Landing; 3D si el rubro está en el grupo visual, 2D si no.
  - CA3: web propia y rubro del grupo back-office → AI Agents; rubro del grupo de alto volumen de consultas → Chatbots; resto → Build.
  - CA4: el mismo contacto con los mismos datos siempre recibe el mismo frente (regla determinística, sin LLM).
- **CU-32**
  - CA1: el texto enviado corresponde al frente asignado, y Build sigue enviando `olv_frio_v13` idéntico a hoy.
  - CA2: si la plantilla de un frente no está aprobada en Meta, el contacto no se envía con otra plantilla sin aviso, y la situación queda visible en `/Bot` (misma regla que G1 del sprint 27/08).
  - CA3: los botones responden con los mismos payloads que `v13` (`seguir`/`no_interesa`).
  - CA4: el envío cuenta para el cupo diario y el tope de gasto igual que hoy.
- **CU-33**
  - CA1: cuando el prospecto toca "Sí, contame más", la IA sabe qué frente se le ofreció y arranca desde ahí.
  - CA2: si el prospecto trae un dolor de otro frente, la IA cambia la categoría y no insiste con el frente original.
  - CA3: siguen vigentes la detección de no-humano, la baja, la escalada ante pregunta de precio y las 7 guardas globales.
  - CA4: un contacto con categoría `ai_agents` o `chatbot` que cae al árbol de fallback no genera error.
  - CA5: `consultar_modulos_del_rubro` devuelve módulos del frente del contacto (ej. Chatbot + inmobiliaria) cuando existen cargados.
- **CU-34**
  - CA1: el detalle de Contacto y de Chat muestran el frente con nombre legible (nunca la clave cruda).
  - CA2: los listados de Contactos y Chats filtran por frente (columnas visibles = filtros disponibles, regla del estudio).
- **CU-35**
  - CA1: ningún alta ni reclasificación nueva recibe `merge`.
  - CA2: los contactos históricos con `merge` se muestran como "Mejoras en sistema Olvidata (discontinuado)".

**Permisos:** sin cambios (único rol `SuperUsuario`).

**Estados:** `FaseConversacion` y `EstadoEmbudo` sin cambios. Cambia el vocabulario de `Contacto.Categoria`, que no es máquina de estados. Dato nuevo "frente ofrecido" por contacto.

**Validaciones:**
- La categoría pertenece al vocabulario vigente: lista cerrada en la herramienta más validación en código, igual que hoy.
- Solo se envía con una plantilla de frente que tenga `EstadoAprobacionMeta = Aprobado`.
- La URL de web se considera "propia" solo si no es de redes sociales o agregadores de links (la lista exacta de dominios se define en Diseño).

**Capas afectadas:**
- **Presentación:** Contactos y Chats (mostrar y filtrar frente, etiqueta de Merge discontinuado); `/Bot` (aviso de plantilla de frente no aprobada); pantalla de catálogo de módulos (asignar frente).
- **Negocio:**
  - `ConversacionIaService`: vocabulario, prompt y módulos por frente.
  - `BotFlowService`: fallback de categorías nuevas y retiro de `merge`.
  - `OutboundCampaignService`: plantilla y parámetros por frente.
  - Regla nueva de asignación de frente (web + rubro).
- **Datos:**
  - `Contacto.Categoria`: sin migración.
  - Campo nuevo "frente ofrecido" en `Contacto`: con migración.
  - Dimensión de frente en el catálogo de módulos: con migración.
  - Filas nuevas en `TemplatesWhatsApp`.

**Riesgos:**
- **R1 — Fallback del árbol:** error con categorías nuevas, verificado en código (`Questions[contacto.Categoria!]`). Si no se cubre, la caída de la IA rompe la conversación.
- **R2 — Web vacía = sin web (riesgo aceptado por el cliente, P2):** los contactos anteriores al 20/08 que sí tienen web van a recibir "no encontré tu página", la misma queja de "hablo con una máquina que no sabe leer" (18 casos medidos de rubro errado). Mitigación a evaluar en Diseño: que el texto de la plantilla de Landing no afirme que no tiene web.
- **R3 — Landing dominante:** con P2 + P3, una gran parte de las pymes de Maps va a caer en Landing, y el pitch de Build/AI Agents/Chatbots queda para una minoría. Medirlo con el filtro por frente en las primeras tandas.
- **R4 — Aprobación de Meta:** 4 plantillas nuevas implican tiempo y posible rechazo. Sin plantilla aprobada, el frente no sale.
- **R5 — Clasificación gruesa por rubro:** un mismo rubro (salud) cae en 2 perfiles (turnos → Chatbots; administración → AI Agents).
- **R6 — Sin línea base por frente:** la tasa de respuesta del frío (6%) se midió solo con Build.
- **R7 — Marca:** los borradores del CEO dicen "Soy Joaquín, de Olvidata Soft". La regla vigente es "Joaquín, con el respaldo de Olvidata" (2026-09-02). Validar con marketing.
- **R8 — Tamaño del prompt:** hoy ~5.100 tokens; crece. Va en el bloque cacheado, así que el impacto de costo es bajo, pero hay que medirlo.
- **R9 — Catálogo de módulos compartido:** agregarle la dimensión de frente toca una tabla que también usa la matriz MVP/FULL de `olvidata-presupuesto-bot`; los módulos de Build existentes no pueden cambiar de comportamiento.

**Supuestos:**
- S1: los precios no entran al bot.
- S2: Build sigue con `v13` sin cambios.
- S3: el inbound de ads usa el mismo vocabulario nuevo, porque la IA es una sola para ambos canales. La asignación automática de frente aplica solo al outbound.
- S4: el outbound se reactiva recién después de implementar.
- S5: la señal de web tiene prioridad sobre el rubro (sin web propia → Landing aunque el rubro sea de Chatbots). Sigue el orden de la matriz del CEO; confirmar en Diseño.

**Banderas tempranas:**
- Migración EF: **sí** (frente ofrecido en `Contacto` + dimensión de frente en el catálogo de módulos).
- Integración externa: **sí** (4 plantillas nuevas en Meta). Places y Anthropic ya integrados, sin cambio de contrato.
- Máquina de estados: **no**.

**Clasificación de perfil de cliente:**
- **Cliente del proyecto:** interno (Olvidata Soft / Joaquín). No hay precio al cliente, así que Presupuesto aplica como estimación interna de horas y costo de IA, sin estrategia de precio.
- **Público al que apunta el bot:** B2B, pymes chicas argentinas (comercios, estudios profesionales, inmobiliarias y consultorios encontrados en Google Maps). Escala chica, según el ticket promedio de Olvidata y el tipo de venta 1 a 1 por WhatsApp.

**Gate:** análisis aprobado; Diseño habilitado.

## Historial de ajustes

- 2026-07-14: Discovery + Análisis cerrados. Migración de BotPublicitario — 3 entidades (`Contacto`, `ContactoRespuesta`, `IndustriaCatalogo`), 9 casos de uso (CU-01 a CU-06, CU-10 a CU-12). `Cliente`/`Upsell`/`Proyecto` (gestión comercial) pospuestos a pedido del cliente. Webhook absorbido en `OlvidataCRM.Web`, CRM arranca vacío, desarrollo en ventana aparte de proyectos pagos.
- 2026-07-21: Discovery + Análisis de "campañas de contacto frío configurables" — reemplaza `RunDayByType`/`RubrosByDay`/`QueriesByRubro`/`BotSettings.DailyLimit` hardcodeados por 3 entidades nuevas (`CampanaOutbound`, `CampanaOutboundIndustria`, `CampanaQuery`) + 3 CU (CU-13/14/15) + 2 HU. Límite diario = solo suma de campañas activas, sin tope global (riesgo aceptado). Mismo día: cliente simplifica el sistema a un único rol (`SuperUsuario`).
- 2026-07-24: Análisis exprés de un ajuste cosmético en Notificaciones (ícono + modal de confirmación) — sin CU nuevo.
- 2026-08-14: Auditoría de proyecto detectó que todo lo construido desde el 2026-07-29 (pantalla `Chats`, scheduler multi-zona horaria, 6 campos nuevos, reestructuración de campañas) nunca pasó por Análisis formal, y que los estados `DemoSolicitada`/`DemoRealizada`/`PropuestaEnviada` prometidos en 2026-07-14 nunca se implementaron. Cerrada la sección "Chats" retroactiva (5 CU nuevos, CU-16 a CU-20) y eliminados formalmente los 3 estados no implementados. Detectado y corregido `CRM-001` del catálogo de QA como obsoleto (no pendiente) — el cliente había eliminado toda la funcionalidad de Auditoría el 2026-07-28.
- 2026-08-14: Discovery + Análisis de "Gestión comercial y herramientas de canal/venta" — consulta paralela a `olvidata-ceo`/`olvidata-marketing`/`olvidata-sales`, selección del cliente sobre las 3 listas priorizadas. 5 entidades nuevas (`Cliente`, `Upsell`, `TemplateWhatsApp`, `CampanaExperimento`, `SugerenciaSeguimiento`), 9 CU nuevos (CU-21 a CU-29). Excluidos: `Proyecto` (vive en VirtualWallet), motivo estructurado de pérdida, tareas/recordatorios automáticos, tracking de fuente de referido.
- 2026-08-14: Reestructuración documental — este archivo tenía 5 secciones fechadas acumuladas (una por ronda de Discovery/Análisis desde 2026-07-14) con correcciones parcheadas al lado de datos viejos en vez de reemplazarlos. Consolidado en una única sección "Definiciones vigentes" (editada in-place de ahora en más, ver `.github/instructions/29-trazabilidad-conversacion.instructions.md` para la regla) + este historial, que es la única zona que sigue creciendo por append. Ningún dato funcional se perdió en la consolidación — mismo contenido, presentado como estado actual en vez de capas superpuestas.
- 2026-08-27: Discovery + Análisis del sprint "corrección de bugs/gaps de auditoría completa + 3 mejoras" — primera vez que el flujo formal de orquestador se ejecuta sobre este proyecto (todo el trabajo previo desde el 14/08 se hizo directo en sesión de chat, sin pasar por Discovery/Análisis/Diseño/Arquitectura/Presupuesto formales). Alcance: 7 bugs reales + 7 gaps funcionales detectados por auditoría de `agentes-ia-qa`, más 3 mejoras propuestas. 17 inconsistencias menores del mismo reporte quedan fuera de este sprint.
- 2026-09-14: Discovery + Análisis de "reorientar el bot de prospección a los 4 frentes" (brief de `olvidata-ceo`). 6 CU propuestos (CU-30 a CU-35), 8 preguntas abiertas. Verificado en código: `website` de Places ya se guarda en `Contacto.PaginaWeb`, `merge` vive en 3 lugares, y el fallback del árbol se rompe con categorías nuevas. Detalle del sprint 27/08 retirado de la sección vigente (cerrado con QA). Actualizados de paso datos vigentes desfasados: `ConversandoConIa`, plantilla fría `v13`, Anthropic en credenciales, exclusión "el bot nunca cotiza".
- 2026-09-14: Análisis aprobado por Joaquín con P1-P8 respondidas. Cambios de alcance: frente asignado automático por contacto; web vacía y solo-redes → Landing (riesgo R2 aceptado); 4 plantillas en vez de 3 (Landing 2D y 3D por rubro visual); módulos por frente en el catálogo (nueva dependencia de `olvidata-presupuesto-bot`, riesgo R9); dashboard por frente y reseñas de Google fuera. Migración EF pasa de "probable" a "sí". CU-30 a CU-35 pasan a la tabla vigente.
- 2026-09-14: Ajuste desde Diseño por decisión de Joaquín — combo Landing 3D + AI Agents + Chatbots para todo prospecto frío con gancho según perfil; Build y Landing 2D siguen; web propia = solo dominio propio. Actualizados P1, alcance 3-4 y CU-31/CU-32.
