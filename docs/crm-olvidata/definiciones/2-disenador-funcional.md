# Memoria - Disenador funcional

## Proyecto: crm-olvidata — CRM interno de OlvidataSoft
## Última actualización: 2026-08-14

## Definiciones vigentes

### 0. Alcance funcional resumido (recap del Análisis vigente)

Ver `1-analista-funcional.md` — 4 bloques funcionales (captación/calificación, campañas configurables, Chats, gestión comercial), 12 entidades, 29 casos de uso. Único rol: `SuperUsuario`.

### 1. Navegación (sidebar vigente)

```
─ Comercial ──────────────
  📇 Contactos
  💬 Chats
─ Negocio ─────────────────
  🏆 Clientes
  📊 Dashboard de negocio
─ Sistema ────────────────
  📧 Sistema / Email
  🤖 Bot / Outbound
```
*(La sección "Super Usuario" con "Auditoría" que aparecía en el diseño original ya no existe — la funcionalidad de Auditoría se eliminó completa el 2026-07-28. Las pantallas de Campañas/Templates/A-B-testing cuelgan de "Bot / Outbound", no tienen entrada propia. El dashboard de campaña/rubro/país cuelga de `Campanas/Index`. El pipeline visual cuelga de "Contactos".)*

### 2. Pantallas vigentes

**`Contactos/Index`** (CU-02) — DataTable server-side (Teléfono, Nombre, Negocio, Rubro, Canal, Estado, Última actividad), filtro por columna visible (Rubro/Canal/Estado Select2, fecha daterangepicker, buscador libre por teléfono/nombre), orden por click de columna. `ov-badge` de color por `EstadoEmbudo`.

**`Contactos/Details/{id}`** (CU-02, soporte CU-05/06/21) — card Datos + card Estado (`EstadoEmbudo`/`FaseConversacion` badges, presupuesto cotizado si hay, selector "Cambiar estado" manual — solo `[Cerrado, Descartado]`, con confirmación SweetAlert2 si el destino es `Descartado`) + card Historial de calificación (`ContactoRespuesta`) + card Notas + botón "Convertir en Cliente" (CU-21, visible solo si `EstadoEmbudo=Cerrado`).

**`Contactos/Create`** (CU-01) — Teléfono* (cualquier país, formato `\d{10,15}`), Nombre*, Negocio, Email (opcional), Rubro (Select2 + libre), Zona, Notas. `CanalOrigen=Manual` fijo sin mostrar. Al guardar: `EstadoEmbudo=Pendiente`, `FaseConversacion=Nuevo`.

**`Contactos/Pipeline`** (CU-29) — kanban por `EstadoEmbudo` (Pendiente/MensajeEnviado/Respondido/PresupuestoEnviado/DerivadoManual/Cerrado; Frío/Descartado en contador aparte), columna = conteo + top-N tarjetas (nombre/negocio/días en la etapa) — con backlog real >600 en `Pendiente`/`MensajeEnviado`, es una vista de pulso, no una grilla completa. Debajo, tabla de conversión etapa→etapa (cantidad y % que avanza, sin desglose de motivo — dato no capturado).

**`Chats/Index`** (CU-16, HU navegación diaria principal según el cliente) — filtros por fecha/interacción (incluye "Ventana por vencer")/rubro/estado/búsqueda libre, persistidos en `Session`. Cada fila: nombre/negocio/rubro, badge de estado, ícono ✉️ de marcar-no-leído (fuera del área clicable, CU-17), último mensaje, fecha enviado/respondió, indicador de ventana ("Ventana cierra en Xh Ym", rojo si ≤3h). Polling cada 20s.

**`Chats/Detail/{id}`** (CU-16/18/19/20/28) — navegación anterior/siguiente (click y flechas de teclado) dentro de la lista filtrada de origen; selector Cambiar estado (mismo que Contactos); hilo de mensajes con reproductor inline para audio/imagen/video y link de descarga para documentos (CU-19); textarea de respuesta con botón "Sugerir mensaje" (CU-28, prellena sin enviar) sujeto a ventana de 24hs; adjuntar presupuesto PDF (CU-20, pasa a `PresupuestoEnviado`). Abrir el chat marca como leído (limpia no-leído automático y manual). Polling cada 8s.

**`Industrias/Index` + `Create`/`Edit`** (CU-12) — DataTable (Nombre, Sistema ref., Plan, Precio USD, ¿Cotiza automático?, Orden). Form: Nombre*, SistemaReferencia, Plan (Select Starter/Pro/Premium/Scale), PrecioBaseUsd* (si CotizaAutomatico), CotizaAutomatico (switch), PainHook, Orden.

**`Bot/Index`** (panel principal) — stat-cards Enviados hoy/Pendientes; card Estado del scheduler (botón "Ejecutar ahora" — CU-10, encola en background, no bloquea el request, con indicador "Corrida en curso..." mientras corre); card resumen de Campañas (activas/pausadas + nombres, link a `Campanas/Index`); card búsqueda manual de prospectos (CU-11).

**`Campanas/Index`** (CU-13/14, HU-12) — DataTable (Nombre, Industrias, Días, Límite diario, Template, Estado, Acciones: Editar/Pausar-Reanudar/Eliminar). Filtros por Nombre/Industrias/Días/Estado.

**`Campanas/Create`** (CU-13) — Nombre*, Días* (7 checkboxes, ya no solo Mar/Mié/Jue), Hora de envío* (hora local del país), Zona horaria (Select — Argentina/Uruguay/Chile/Paraguay/Bolivia/Perú-Ecuador-Colombia/Venezuela), Límite diario*, Template* (Select desde `TemplateWhatsApp` activos y aprobados, CU-26), Industrias* (Select2 multi, valida no-duplicado entre campañas activas). Redirige a Edit para cargar queries — no puede activarse sin al menos 1 query por industria.

**`Campanas/Edit/{id}`** (CU-13/14/15/27) — mismos campos que Create precargados + acordeón "Industrias y queries de búsqueda" (AJAX inline, expandido si 0 queries) + card "Experimento A/B" (CU-27: 2 selects de template aprobado + % de split, 1 experimento activo máximo).

**`Campanas/Dashboard`** (CU-25) — tabla cruzada Campaña × Rubro × País, tasa de respuesta/avance a presupuesto/cierre.

**`Templates/Index` + `Create`/`Edit`** (CU-26) — CRUD (Nombre, Texto, Rubro, País, `EstadoAprobacionMeta`, Activo).

**`Clientes/Index`** (CU-22) — semáforo por `FechaProximaRenovacion` (rojo <30 días, ámbar <90). Columnas: Negocio, Plan, TicketAnualUsd, FechaAlta, FechaProximaRenovacion, Activo.

**`Clientes/Details/{id}`** (CU-23) — datos + card Upsells (alta rápida inline) + link al `Contacto` de origen.

**`Negocio/Dashboard`** (CU-24) — stat-cards Clientes activos / Ticket promedio real / NRR del período / Avance hacia la meta + tabla Próximas renovaciones. NRR muestra "Datos insuficientes" (no un número aproximado) si no hay período anterior con el que comparar.

### 3. ViewModels vigentes

```
ContactoListItemVM   { Id, Telefono, NombreContacto, NombreNegocio, Rubro, CanalOrigen, EstadoEmbudo, FechaUltimaActividad }
ContactoDetailsVM    { campos de Contacto, Respuestas: List<ContactoRespuestaVM>, EstadosDisponibles }
ContactoCreateVM     { Telefono [Required, regex \d{10,15}], NombreContacto [Required], NombreNegocio, Email, Rubro, Zona, Notas }
PipelineViewModel    { Columnas: List<PipelineColumnaVM> }; PipelineColumnaVM { Estado, Cantidad, Contactos (top-N) }
ConversionEtapaViewModel { Filas: List<{ EstadoOrigen, EstadoDestino, Cantidad, Porcentaje }> }

ChatFiltrosViewModel { Buscar, Fecha, FechaDesde, FechaHasta, Interaccion (incl. "porVencer"), Rubro, Estado }
ChatListItemViewModel { Id, Telefono, NombreContacto, NombreNegocio, Rubro, UltimoMensaje, FechaUltimaActividad, FechaEnviado, FechaRespondio, EstadoEmbudoTexto/Clase, NoLeido, VentanaTexto, VentanaClase }
ChatDetailViewModel  { datos del contacto, EstadoEmbudo, FaseConversacion, PresupuestoCotizadoUsd, Mensajes: List<ChatMensajeViewModel>, EstadosDisponibles, Filtros, PrevId/NextId, posición }
ChatMensajeViewModel { Id, EsSaliente, EsEvento, EsDocumento, Etiqueta, Texto, Fecha, MediaKind (audio|image|video|file) }

IndustriaCatalogoCreateVM { Nombre [Required], SistemaReferencia, Plan [Required], PrecioBaseUsd [Required si CotizaAutomatico], CotizaAutomatico, PainHook, Orden }
BotOutboundStatusVM  { EnviadosHoy, PendientesHoy, Standby, CorridaManualEnCurso, CampanasResumen }

CampanaOutboundCreateVM { Nombre [Required], Dias (7 valores), HoraEnvio, ZonaHoraria, LimiteDiario [Required, >0], Template [Required, desde TemplateWhatsApp], IndustriaIds [Required, min 1] }
CampanaOutboundEditVM { igual a Create + Id, IndustriasConQueries: List<CampanaIndustriaQueriesVM> }
CampanaIndustriaQueriesVM { IndustriaId, IndustriaNombre, Queries: List<{ Id, Query, Zona }> }
CampanaExperimentoViewModel { CampanaOutboundId, TemplateAId [Required], TemplateBId [Required, distinto de A], PorcentajeB [Range 1-99] }
CampanaDashboardItemVM { Campana, Rubro, Pais, Enviados, TasaRespuesta, TasaAvancePresupuesto, TasaCierre }

TemplateWhatsAppCreateVM { Nombre [Required], Texto [Required], Rubro, Pais, EstadoAprobacionMeta [Select], Activo }

ClienteListItemVM   { Id, NombreNegocio, Plan, TicketAnualUsd, FechaAlta, FechaProximaRenovacion, DiasParaVencer, Activo }
ClienteDetailsViewModel { datos completos, Upsells: List<{ Id, Tipo, MontoUsd, Fecha }> }
ConvertirClienteViewModel { ContactoId, Plan [Required], TicketAnualUsd [Required, >0], FechaAlta [Required], FechaProximaRenovacion [calculada, editable] }
NegocioDashboardViewModel { ClientesActivos, TicketPromedioReal, Nrr (nullable), AvanceMeta, ProximasRenovaciones }
```

### 4. Máquinas de estado vigentes

**`FaseConversacion`** (conversación del bot, vida corta):

| Origen | Evento | Destino | Guarda | Acción |
|---|---|---|---|---|
| *(sin conv.)* | 1er mensaje, outbound activo | `AskingQuestions` | `Contacto` existente con `MensajeEnviado`/`FollowUpEnviado` | Saludo + 1ª pregunta de la industria conocida |
| *(sin conv.)* | 1er mensaje, sin outbound | `AwaitingCategory` | — | Menú de categorías |
| `AwaitingCategory` | "1" (rent) | `AwaitingIndustry` | — | Lista de rubros |
| `AwaitingCategory` | "2"/"3" (build/landing) | `AskingQuestions` | — | 1ª pregunta de esa categoría |
| `AwaitingCategory` | texto libre no reconocido | `Completed` | — | Categoria=`other`, sin presupuesto |
| `AwaitingIndustry` | rubro (núm./texto) | `AskingQuestions` | — | Mapea a `IndustriaCatalogo`; no reconocido → Categoria=`rent_other` |
| `AskingQuestions` | responde, quedan preguntas | `AskingQuestions` | `QuestionIndex+1 < Count` | Guarda `ContactoRespuesta`, siguiente pregunta |
| `AskingQuestions` | última pregunta | `Completed` | `QuestionIndex+1 == Count` | Calcula presupuesto (si aplica), notifica (CU-04/05) |
| `Completed` | escribe, <24h | `Completed` | — | "Ya registramos tu consulta" + aviso extra a Joaquín |
| `Completed` | escribe, ≥24h | `Nuevo→AwaitingCategory` | — | Reinicia, conserva historial |

**`EstadoEmbudo`** (embudo comercial, vida larga) — ver enum real en `1-analista-funcional.md` (`Pendiente→MensajeEnviado→FollowUpEnviado→Respondido→PresupuestoEnviado→Cerrado/Frio/Descartado/DerivadoManual`, sin `DemoSolicitada`/`DemoRealizada`/`PropuestaEnviada`):

| Origen | Evento | Destino | Acción |
|---|---|---|---|
| `Pendiente` | scheduler corre, día/hora local de la campaña, cupo disponible | `MensajeEnviado` | Envía template de la campaña (o A/B si hay experimento activo) |
| `MensajeEnviado` | ≥7 días sin respuesta, día programado | `FollowUpEnviado` | Envía `olv_nurturing_v2` |
| `FollowUpEnviado` | ≥4 días sin respuesta | `Frio` | Marca frío |
| `Pendiente`/`MensajeEnviado`/`FollowUpEnviado` | contacto responde | `Respondido` | Dispara `FaseConversacion` |
| `Respondido` | `Completed` con industria que cotiza | `PresupuestoEnviado` | Envía presupuesto |
| `Respondido` | `Completed` sin cotización | `DerivadoManual` | Notifica sin presupuesto |
| cualquiera antes de `Cerrado`/`Descartado` | manual (`Contactos/Details`, `Chats/Detail`) | `Cerrado`/`Descartado` | Único destino manual permitido, no se puede volver a `Pendiente` |
| `Cerrado` | manual (CU-21) | — | Puede convertirse en `Cliente` |

### 5. Reglas de negocio y permisos

Único rol (`SuperUsuario`), sin matices, desde 2026-07-21 — todas las pantallas de este documento.

- `Contacto.Telefono` único, cualquier código de país (`\d{10,15}`) — validación server-side, mensaje con Id/nombre del existente.
- El webhook deduplica por `message_id` de Meta.
- `IndustriaCatalogo.CotizaAutomatico=true` exige `PrecioBaseUsd>0`.
- Baja de `IndustriaCatalogo`/`CampanaOutbound`/`Cliente` es soft-delete.
- `CampanaOutbound`: una `ClaveRubro` no puede estar en 2 campañas **activas** a la vez; no se puede activar sin industrias o con alguna industria sin queries.
- No leído en `Chats`: `MarcadoNoLeidoManual==true` **o** (`FaseConversacion>=AskingQuestions` **y** `FechaRespuesta!=null` **y** actividad más nueva que la última lectura).
- Ventana por vencer: desde el último mensaje **entrante** real (nunca actividad saliente) + 24hs. Notificación in-app solo para `DerivadoManual`.
- `Cliente` solo se crea desde un `Contacto` con `EstadoEmbudo=Cerrado`. `FechaProximaRenovacion` default `FechaAlta.AddYears(1)`, editable.
- `CampanaExperimento`: 1 activo máximo por campaña, A≠B.
- `TemplateWhatsApp` con `EstadoAprobacionMeta != Aprobado` no aparece en selectores de envío real.
- `SugerenciaSeguimiento`: matchea `EstadoEmbudo`+`Rubro` exacto, si no hay, cae a genérica (`Rubro=null`) antes de "sin sugerencia".

### 6. Riesgos y supuestos vigentes

- Sin persistencia propia de multimedia — riesgo de indisponibilidad en adjuntos viejos si Meta purga el archivo (ver `1-analista-funcional.md`).
- Sin plantilla de "reenganche" aprobada en Meta — ventana cerrada sin respuesta no se puede reabrir salvo que el contacto escriba.
- Pipeline kanban es vista de pulso (top-N), no reemplaza `Contactos/Index` con filtros para el detalle completo.
- Dashboard de negocio con datos iniciales pobres hasta acumular 2-3 períodos reales de `Cliente`/`Upsell`.
- "Período" de NRR = anual (coherente con `TicketAnualUsd`); cambiarlo a mensual/trimestral es cambio de cálculo, no de modelo de datos.

## Historial de ajustes
- 2026-07-14: Diseño funcional cerrado sobre el alcance recortado (solo migración de BotPublicitario). 5 pantallas, 2 máquinas de estados, 11 HU, plan funcional de 5 etapas.
- 2026-07-21: Diseño de "campañas de contacto frío configurables" — 4 pantallas, sin máquina de estados (flag `Activa`), 5 ViewModels, HU-14/15/16.
- 2026-07-24: Ajuste cosmético en Notificaciones (ícono + modal).
- 2026-08-14: Auditoría de proyecto — corregida la tabla de `EstadoEmbudo` (se retiran los 3 estados nunca implementados), corregida HU-11, cerrado el diseño retroactivo de `Chats` (CU-16 a CU-20, 2 pantallas).
- 2026-08-14: Diseño de "Gestión comercial y herramientas de canal/venta" — 9 pantallas nuevas/extendidas, sidebar "Negocio", 13 ViewModels, CU-21 a CU-29.
- 2026-08-14: Reestructuración documental — este archivo tenía 5 secciones fechadas acumuladas con wireframes/ViewModels/reglas repetidos y corregidos por nota al lado, en vez de una vista única del estado actual. Consolidado en una sola "Definiciones vigentes" (editada in-place de ahora en más) + este historial. Ningún dato funcional se perdió — mismo contenido, sin capas superpuestas.
