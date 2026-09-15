# Memoria - Disenador funcional

## Proyecto: crm-olvidata — CRM interno de OlvidataSoft
## Última actualización: 2026-09-14

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

**`Chats/Index`** (CU-16, HU navegación diaria principal según el cliente) — filtros por fecha/interacción (Todos/Se les envió/Respondieron alguna vez/Sin responder/Ventana por vencer/No leídos)/rubro/estado/búsqueda libre, persistidos en `Session`. Cada fila: nombre/negocio/rubro, badge de estado, ícono ✉️ de marcar-no-leído (fuera del área clicable, CU-17), último mensaje, fecha enviado/respondió, indicador de ventana ("Ventana cierra en Xh Ym", rojo si ≤3h). Polling cada 20s.

Distinción deliberada, no redundante, entre 2 filtros que se prestan a confusión (revisión 2026-08-31): **Interacción → "Respondieron alguna vez"** filtra por `FechaRespuesta != null` (marca de tiempo cruda, nunca se limpia — responde "¿alguna vez contestó?", tasa histórica). **Estado → "Respondió"** filtra por `EstadoEmbudo == Respondido` (etapa ACTUAL del embudo, se pierde en cuanto el contacto avanza a PresupuestoEnviado/Cerrado/Frío/Descartado/DerivadoManual — responde "¿está hoy trabado en esa etapa sin avanzar?"). Ambos tienen uso real; la etiqueta del primero se ajustó a "alguna vez" para dejar la diferencia explícita en pantalla.

**`Chats/Detail/{id}`** (CU-16/18/19/20/28) — navegación anterior/siguiente (click y flechas de teclado) dentro de la lista filtrada de origen; selector Cambiar estado (mismo que Contactos); hilo de mensajes con reproductor inline para audio/imagen/video y link de descarga para documentos (CU-19); textarea de respuesta con botón "Sugerir mensaje" (CU-28, prellena sin enviar) sujeto a ventana de 24hs; adjuntar presupuesto PDF (CU-20, pasa a `PresupuestoEnviado`). Abrir el chat marca como leído (limpia no-leído automático y manual). Polling cada 8s.

**`Industrias/Index` + `Create`/`Edit`** (CU-12) — DataTable (Nombre, Sistema ref., Plan, Precio USD, ¿Cotiza automático?, Orden). Form: Nombre*, SistemaReferencia, Plan (Select Starter/Pro/Premium/Scale), PrecioBaseUsd* (si CotizaAutomatico), CotizaAutomatico (switch), PainHook, Orden.

**`Bot/Index`** (panel principal) — **reestructurado el 2026-09-14** en 5 secciones numeradas con separador visible, porque los conceptos estaban mezclados: el costo vivia en 4 lugares distintos, los 3 interruptores del bot estaban sueltos como 6 botones al final de la pantalla, y las metricas de resultado se intercalaban con la operacion — o sea que la primera pregunta que uno le hace a la pantalla ("¿esta andando?") era la ultima que contestaba. Orden vigente: **1 Estado y control** (los 3 interruptores —envio de WhatsApp, busqueda de prospectos, conversacion con IA— en una tabla con QUE controla / COMO esta / COMO se cambia, mas proxima corrida, "Ejecutar ahora" y "Salud del pipeline") · **2 Hoy** (enviados/pendientes/respondieron + cupo diario con su derivacion) · **3 Costo del mes** (una card de tope y reparto arriba + detalle por herramienta abajo) · **4 Resultados** (tasas, evolucion diaria, breakdown de estados) · **5 Configuracion** (campañas, plantillas, carga de prospectos). Contenido heredado: stat-cards Enviados hoy/Pendientes; card Estado del scheduler (botón "Ejecutar ahora" — CU-10, encola en background, no bloquea el request, con indicador "Corrida en curso..." mientras corre); card resumen de Campañas (activas/pausadas + nombres, link a `Campanas/Index`); card búsqueda manual de prospectos (CU-11).

**Control de costos en `Bot/Index`** (2026-09-03/04, ampliado a 3 herramientas el 2026-09-13) — el detalle por herramienta va cada uno en la moneda en que factura su proveedor (Meta en ARS, Google y Anthropic en USD), **no convertidas**, para poder cruzarlas contra cada factura; solo el total se consolida. Arriba de los 3 detalles hay una card **"Tope de gasto y reparto entre las 3 herramientas"** con el gasto total, el % consumido, el costo por prospecto trabajado de punta a punta, la proyeccion a fin de mes, y la tabla del reparto (gasto, % del tope, costo unitario que aporta, share y techo derivado de cada herramienta). Cierra con el numero que antes no estaba en ninguna pantalla: cuantos **prospectos por dia sostiene** el tope con el reparto vigente. Las columnas Share y Techo son **calculadas, no editables**: el form tiene solo 3 campos (tope, cotizacion y factor de holgura). Las 2 cards originales:

- **"Costo de las consultas (Google Maps) — mes en curso"** (USD): gasto del mes, proyección a fin de mes, consultas de detalle, **ahorro acumulado por el caché de `place_id`**, y costo por prospecto nuevo. Badge de búsqueda activa/pausada.
- **"Costo de mensajería (Meta) — mes en curso"** (ARS): gasto del mes desglosado (mensajería + Google convertido), presupuesto y % consumido con barra de progreso, costo promedio por mensaje del mix real de países, límite de hoy indicando **cuál de los dos techos manda** (cupo por cantidad o presupuesto), proyección a fin de mes (en rojo si se pasaría del tope), tabla de desglose por país, y form para setear tope mensual + cotización del dólar.
- **Regla de negocio central**: el tope en ARS cubre el **costo total del bot** (mensajería + Maps). Sin cotización cargada solo cubre mensajería, y la pantalla lo avisa con un alert explícito en vez de simular que cubre todo. Desde 2026-09-03 **el volumen diario de envío lo fija el precio**, no la meta de cantidad: la card "Cupo de envío diario" muestra la cuenta que lo produce (`ARS que quedan ÷ días restantes ÷ costo promedio por mensaje`) y `MetaDiaria` quedó solo como respaldo para cuando no hay presupuesto.
- Botón **"Pausar/Reanudar búsqueda de Maps"**, independiente del pausado del outbound: frena las consultas a Google **sin** frenar el envío de WhatsApp a los prospectos ya encontrados. Persistido en base (sobrevive redeploy).

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

ChatFiltrosViewModel { Buscar, Fecha, FechaDesde, FechaHasta, Interaccion (todos/enviado/respondio/sinResponder/porVencer/noLeidos), Rubro, Estado }
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
| *(cualquiera)* | la IA responde (texto libre, IA disponible) | `ConversandoConIa` | IA habilitada, no pausada, presupuesto OK | El LLM conduce; ya no hay menu ni cuestionario fijo |
| `ConversandoConIa` | la IA deja de estar disponible | `AskingQuestions` o `Nuevo` | `Categoria` cargada → cuestionario; si no → guion | El arbol retoma **sin volver a presentarse** |
| `ConversandoConIa` | `finalizar_conversacion` | `Completed` | — | Brief al asesor, `EstadoEmbudo=DerivadoManual` |

**Desde 2026-09-13 el camino normal ya no es el arbol** (ver `plan-llm-conversacional-bot.md`): con la IA
encendida desaparecen el menu de bienvenida, el menu de rubros y el cuestionario de 3 preguntas fijas. Lo
que se conserva intacto son las **7 guardas globales** (admin, descartado, cerrado, pedido de baja,
away-message, multimedia, corte de loop post-cierre), la deteccion de origen por anuncio, el vocabulario
de categorias, los estados del embudo y los mensajes automaticos fuera del arbol. El arbol queda como
**fallback** y por eso la tabla de arriba sigue vigente completa.

**Pausa del bot por contacto** (2026-09-13): cuando un asesor interviene a mano —mensaje libre,
presupuesto PDF o envio programado— el bot se calla **en ese chat** por 48hs y se reanuda solo. Visible
y togglable en `Chats/Detail` con un boton que muestra la hora de reactivacion. Un mensaje entrante con
el bot pausado se registra igual, no se pierde.

**Multimedia** (2026-09-14): un audio, imagen, video o documento ya no termina en silencio — se contesta
pidiendo que lo escriban. Medido antes del cambio: 9 audios e imagenes sin respuesta, 6 de ellos de leads
de ads pagos, el canal que convierte al 41%. Las reacciones y stickers siguen sin respuesta a proposito.

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

### 7. Diseño del sprint "corrección de bugs/gaps de auditoría + 3 mejoras" (2026-08-27)

Formato por item: **Diseño de la corrección** + **HU con criterio de aceptación**. Ver `1-analista-funcional.md` para el detalle del hallazgo original de cada uno.

**B1 — Truncado defensivo en `ContactoRespuesta.Respuesta`/escrituras relacionadas.**
Diseño: helper `Truncar(string, maxLen)` (mismo patrón ya usado en `NotificationService.Truncar`) aplicado en los 8 puntos de escritura de `ContactoRespuesta.Respuesta` antes del `Add`. Ampliar el `catch` de `SendDailyBatchAsync` (hoy solo `WhatsAppApiException`) para que también capture `DbUpdateException` puntual por contacto, sin abortar el resto del `foreach` de la campaña.
HU: *Como sistema, cuando un mensaje entrante o un template de catálogo supera el largo de columna, se guarda truncado (con un sufijo "…") en vez de tirar excepción — y si el error es de otro tipo, la campaña sigue procesando el resto de los contactos.*

**B2 — Rebalanceo por día individual, no por combinación de flags.**
Diseño: `RebalancearMatrizAsync` deja de agrupar por `c.Dias` crudo — expande cada campaña a los días individuales que tiene marcados (`DiasSemana` es `[Flags]`) y calcula el `targetPct` por día real, no por combinación. `DiaTexto` deja de necesitar el caso `_ => dias.ToString()` para combinaciones.
HU: *Como SuperUsuario, al rebalancear la matriz, una campaña Lunes+Miércoles pesa en el cálculo de AMBOS días — el resumen que veo después de rebalancear coincide con el volumen real que va a salir cada día.*

**B3 — El polling no pisa "última lectura" salvo que haya novedad real.**
Diseño: `HiloParcial` solo actualiza `FechaUltimaLecturaAgente`/`MarcadoNoLeidoManual` si hay mensajes nuevos desde la última carga (comparar contra el `Id` del último `ContactoRespuesta` ya renderizado, recibido como parámetro desde el JS) — no en cada tick del polling. `MensajesProgramadosSchedulerService` deja de tocar `FechaUltimaLecturaAgente` al disparar un envío (ese campo representa que UN HUMANO leyó, no que el sistema mandó algo).
HU: *Como asesor, si dejo abierto un chat en otra pestaña y el contacto me escribe de nuevo, ese chat se marca "No leído" en la lista — sin importar que el polling siga corriendo en background.*

**B4 — Sincronizar `EtiquetasDeEvento` con los literales reales del bot.**
Diseño: agregar los 6 literales faltantes a `ChatsController.EtiquetasDeEvento`. Ver mejora **M-A** para la solución de raíz (constante compartida) — este item es el fix inmediato mínimo, M-A es la prevención estructural.
HU: *Como asesor, al abrir el hilo de un contacto, nunca veo un mensaje de diagnóstico interno del bot mostrado como si se lo hubiéramos escrito nosotros.*

**B5 — Bloquear rename de template con campañas activas.**
Diseño: mismo patrón ya usado en `Delete` (`TemplatesController.Delete:228-234`) — `Edit` valida si `CampanaOutbound.TemplateWhatsApp == nombreViejo AND Activa` antes de aplicar el rename; si hay coincidencias, bloquea con mensaje explícito ("N campañas activas usan este nombre, no se puede renombrar") en vez de aplicar el cambio.
HU: *Como SuperUsuario, si intento renombrar un template que está en uso por una campaña activa, el sistema me avisa y no me deja — tengo que desactivar o reasignar la campaña primero.*

**B6 — Unificar la fórmula de "Respuesta → Presupuesto" en un solo lugar.**
Diseño: extraer la fórmula ya correcta de `OutboundCampaignService` (línea 441-445) a un método reutilizable (`Application`, ver M-A del mismo criterio de centralización) y que `ContactosController`/`CampanasController` lo consuman en vez de reimplementar `PresupuestoEnviado or Cerrado`. Alinear también el universo base de "Pipeline" para que filtre por canal outbound igual que `GetHistoricoAsync`.
HU: *Como SuperUsuario, el número de "Respuesta → Presupuesto" es el mismo sin importar si lo veo en Bot/Outbound, Contactos/Pipeline o Campañas/Dashboard.*

**B7 — Habilitar el canal Referido desde la UI.**
Diseño: agregar `ReferidoPor`/`MotivoReferido` a `ContactoCreateViewModel`/`ContactoEditViewModel` (Create y Edit, ver regla "todas las propiedades editables en Alta y Edición"), con un selector de `CanalOrigen` que incluya `Referido` como opción manual. No agrega flujo nuevo — conecta el ya existente (template, prioridad de cupo, cards de ficha) a un punto de carga real.
HU: *Como SuperUsuario, puedo cargar manualmente un contacto marcándolo como Referido, indicando quién lo refirió — ese contacto entra al circuito ya construido (template dedicado, prioridad de cupo, visible en la ficha del cliente si cierra).*

**G1 — Templates de catálogo con placeholders/botones variables.**
Diseño: en vez de switches hardcodeados por nombre de template, `BuildComponents` para un template NO reconocido en el diccionario fijo arma los parámetros dinámicamente a partir de `TemplateWhatsApp.Texto` (cuenta placeholders `{{N}}` reales) usando los mismos campos genéricos ya disponibles del contacto (Nombre/Negocio/Rubro), sin botones por default. Alcance acotado: soporta N placeholders de texto simple: NO agrega soporte genérico de botones QUICK_REPLY para templates de catálogo en este sprint (eso requiere UI para definir los payloads, ver nota de riesgo abajo) — un template de catálogo con botones sigue sin poder darse de alta hasta una ronda futura, pero al menos no reintenta para siempre en silencio: si el envío falla por mismatch de parámetros, el contacto se marca con un estado de error visible en vez de quedar `Pendiente` reintentando indefinidamente.
HU: *Como SuperUsuario, si doy de alta un template de catálogo con 4 o 5 placeholders de texto, se puede asignar a una campaña y el envío funciona sin tocar código. Si algo falla al mandarlo, lo veo reflejado en el contacto en vez de que reintente para siempre en silencio.*

**G2 — Corrida manual respeta shuffle de equidad y marca `UltimaCorridaUtc`.**
Diseño: `BotController.EjecutarAhora` pasa por el mismo shuffle por día del año que usa `OutboundSchedulerService` antes de llamar a `RunFullPipelineAsync`, y `SendDailyBatchAsync` marca `UltimaCorridaUtc` en cada campaña procesada sin importar si el disparador fue manual o automático.
HU: *Como SuperUsuario, si ejecuto el pipeline a mano a las 8am, el scheduler automático de las 9:30 no vuelve a procesar las mismas campañas — y las campañas con Id más alto no pierden cupo sistemáticamente en las corridas manuales.*

**G3 — `PrimerAnioGratis` disponible en el alta de Cliente.**
Diseño: agregar el campo a `ConvertirClienteViewModel`/`ConvertirDesdeContacto`, mismo checkbox que ya existe en Edit.
HU: *Como SuperUsuario, al convertir un contacto cerrado en Cliente, puedo marcar "primer año gratis" en el mismo formulario de alta — no tengo que acordarme de ir a Editar después.*

**G4 — Decisión sobre `PresupuestoCotizadoUsd`: editable a mano.**
Diseño (decisión tomada para este sprint, ver Arquitectura para alternativa descartada): se hace editable a mano en `Contactos/Create`/`Edit`, conservando las 5 lecturas existentes (incluida la card de `Chats/Detail`) — un campo de cotización manual sigue siendo útil aunque ya no lo llene el bot automáticamente.
HU: *Como SuperUsuario, puedo cargar a mano el presupuesto cotizado a un contacto desde su ficha — la card de referencia en Chats y los reportes que lo usan dejan de estar siempre vacíos.*

**G5 — Acciones AJAX de Chats devuelven JSON, no redirect.**
Diseño: `MarcarNoLeido`/`MarcarTodosLeidos` dejan de hacer `RedirectToAction`+`TempData` y devuelven `Json(new { ok, mensaje })`; el JS que las llama muestra el mensaje (toast, mismo componente ya usado por el layout global) y solo refresca la lista si `ok=true`. Ver mejora **M-A**-adyacente: este patrón (JSON en vez de redirect para llamadas AJAX) queda como convención a aplicar en el resto del sistema si se encuentran casos similares — no se auditan todas las pantallas en este sprint, solo se corrigen las 2 acciones detectadas.
HU: *Como asesor, cuando marco un chat como no leído o marco varios como leídos desde la lista, veo una confirmación (o un error real) en pantalla — no me quedo sin saber si funcionó.*

**G6 — `MarcarTodosLeidos` con `ExecuteUpdateAsync`.**
Diseño: reemplazar el `ToListAsync()` con tracking + loop por un `ExecuteUpdateAsync` (EF Core 7+) directo sobre la query filtrada — un solo `UPDATE` en SQL, sin traer filas a memoria.
HU: *Como SuperUsuario, "Marcar todos como leídos" con el filtro "Todos" no tarda ni consume memoria de forma proporcional al total de contactos del sistema.*

**G7 — Aviso + reclasificación al eliminar una industria con contactos asociados.**
Diseño: antes de soft-deletear una `IndustriaCatalogo` o sacarla de una campaña, contar cuántos `Contacto.Rubro` matchean esa clave y mostrar el número en el modal de confirmación (mismo patrón ya usado en otros `Delete` con impacto). Sin reclasificación automática en este item — el flujo de reclasificación de un clic es la mejora **M-B** (alcance mayor, se separa).
HU: *Como SuperUsuario, al eliminar una industria o sacarla de una campaña, el sistema me dice cuántos contactos van a quedar sin campaña que los alcance, antes de confirmar.*

**M-A — Constante de dominio compartida para "último mensaje entrante real" (mejora).**
Diseño: nuevo método estático en `Application` (ej. `MensajeriaHelpers.EsMensajeSaliente(string pregunta)` con la lista completa de etiquetas salientes como constantes públicas) referenciado desde `ChatsController`, `VentanaExpiracionSchedulerService`, `MensajesProgramadosSchedulerService` y `OutboundCampaignService` — reemplaza las 4 declaraciones locales duplicadas y las 8 repeticiones de la condición `Where`.
HU: *Como desarrollador, agregar una etiqueta de mensaje saliente nueva se hace en un solo lugar — no hay forma de que un archivo quede desincronizado del resto.*

**M-B — Reclasificación asistida de contactos huérfanos (mejora).**
Diseño: en el modal de confirmación de G7, si hay contactos afectados, ofrecer un select "Reasignar a: [otra industria activa]" — al confirmar, hace el `UPDATE` de `Contacto.Rubro` en la misma transacción del soft-delete, en vez de dejarlos huérfanos.
HU: *Como SuperUsuario, cuando elimino una industria con contactos asociados, puedo reasignarlos a otra categoría en el mismo paso, sin necesitar un script aparte.*

**M-C — Endpoint de salud del pipeline outbound (mejora).**
Diseño: nueva vista `Bot/Salud` (o card dentro de `Bot/Index`) que consulta y muestra: templates `Activo=true` sin ninguna `CampanaOutbound.Activa` que los use; campañas activas con `TemplateWhatsApp` no-Aprobado o inexistente en el catálogo; conteo de contactos huérfanos por rubro (sin `CampanaOutboundIndustria.ClaveRubro` activa que los alcance); y las 3 fórmulas de B6 evaluadas en paralelo con un aviso si alguna vez difieren de nuevo.
HU: *Como SuperUsuario, tengo una sola pantalla para confirmar que el pipeline outbound está sano — sin tener que pedir una auditoría completa cada vez que quiero chequearlo.*

### 8. Diseño de la feature "reorientar el bot de prospección a los 4 frentes" (2026-09-14) — COMBO CON GANCHO — DISEÑO APROBADO

Entrada: `1-analista-funcional.md`, sección "Feature: reorientar el bot de prospección a los 4 frentes" (análisis aprobado 2026-09-14). Primera versión del diseño (un frente por prospecto) revisada el mismo día por decisión de Joaquín: **a todo prospecto frío se le ofrece el combo** (Landing 3D + AI Agents + Chatbots) para que compre todo, con el mensaje abriendo por el dolor más probable de su perfil; Build y Landing 2D siguen disponibles. Diseño aprobado por Joaquín el 2026-09-14, con las interpretaciones de 8.16 confirmadas. Arquitectura habilitada.

#### 8.0 Reutilización

- `docs/patrones/catalogo.yml`: sin match previo. Escaneo de `docs/*/definiciones/`: sin coincidencias.
- Se reutilizan patrones del propio proyecto: `RubroHelpers` como fuente única de vocabulario (lección CRM-007/CRM-016), `/Bot/Salud` (M-C), filtros persistidos en `Session` de `Chats/Index`, catálogo de módulos MVP/FULL (2026-08-27) y el mecanismo de pregunta 1 con módulos (`MecanismoDolor.MatrizModulos`).
- Patrón nuevo agregado al catálogo: **PAT-031** (con la variante combo).

#### 8.1 Hallazgos de código que definen el diseño

- **El toque del botón "Sí, contame más" no pasa por la IA**: `IntentarResponderConIaAsync` solo atiende texto libre, y el toque cae en `OnConfirmarContinuarAsync`, que **fuerza `Categoria = "rent"`** y manda la pregunta 1 de gestión (con módulos de Build). Es el camino principal de todo contacto frío con botones (`olv_frio_v10` a `v13`), no un fallback. Si solo se cambiara la plantilla, a quien le abrimos por consultas de WhatsApp le preguntaríamos por su gestión. El primer mensaje después del botón tiene que salir del gancho (8.6).
- **Fallback desde `ConversandoConIa`**: sí chequea la clave (`Questions.ContainsKey`), pero si no la encuentra reinicia saludo y menú — repite la presentación (bug reportado en agosto). El `KeyNotFoundException` queda solo para un contacto en `AskingQuestions` con categoría sin cuestionario.

#### 8.2 Conceptos: oferta, gancho e interés detectado

- **Oferta del contacto frío (igual para todos):** combo **Landing 3D + AI Agents + Chatbots**. Build (sistema de gestión) y Landing 2D siguen disponibles: Build entra en el mensaje del gancho "Gestión" y en la conversación; Landing 2D no se ofrece en el primer mensaje (el combo lleva 3D) y se define en la propuesta si el prospecto pide algo más simple.
- **Gancho** (nuevo, lo asigna el sistema): por qué dolor abre el mensaje. Valores: **Presencia web**, **Administración** (abre con AI Agents), **Consultas** (abre con Chatbots), **Gestión** (abre con Build).
- **Interés detectado**: lo que el prospecto terminó pidiendo. Es el `Contacto.Categoria` existente, lo fija la conversación.

Etiqueta legible de `Categoria` ("Interés detectado"):

| Clave | Etiqueta | Frente |
|---|---|---|
| `rent` / `rent_other` | Sistema de gestión | Build |
| `build` | Desarrollo a medida | Build |
| `landing` | Página web | Landing |
| `ai_agents` | Agentes de IA | AI Agents |
| `chatbot` | Asistente de consultas | Chatbots |
| `other` | Otra consulta | — |
| `merge` | Mejoras en sistema Olvidata (discontinuado) | — |
| *(vacío)* | Sin clasificar | — |

#### 8.3 Regla de asignación del gancho (tabla de decisión, determinística, sin LLM)

Se evalúa en orden y gana la primera fila que aplica:

| # | Condición | Gancho | Motivo que se guarda |
|---|---|---|---|
| 1 | Canal distinto de Outbound frío (ads, manual, referido) | *sin gancho* | — (S3: solo outbound) |
| 2 | Gancho elegido a mano | el elegido | "Asignado a mano" |
| 3 | Sin web propia (8.4) | Presencia web | "Sin web" / "Web en plataforma o redes (instagram.com)" |
| 4 | Rubro del grupo Administración | Administración | "Rubro administrativo: estudio" |
| 5 | Rubro del grupo Consultas | Consultas | "Rubro con muchas consultas: consultorio" |
| 6 | Cualquier otro caso (incluye rubro no mapeado) | Gestión | "Rubro de gestión: comercio" |

La web tiene prioridad sobre el rubro (S5).

**Grupos por clave de rubro** (claves reales de `RubroHelpers.RubroBaseAIndustria`). Con el combo, el grupo solo decide por dónde abre el mensaje — todos reciben la misma oferta:

| Clave | Industria | Grupo (si tiene web propia) |
|---|---|---|
| `inmobiliaria` | Inmuebles / Real estate | Consultas |
| `consultorio`, `clinica` | Salud / Medicina | Consultas |
| `maquinaria` | Alquiler de maquinaria | Consultas |
| `vinos` | Vinos y bebidas | Consultas |
| `ski` | Alquiler de equipos de esquí | Consultas |
| `estudio` | Contabilidad / Estudios contables | Administración |
| `farmacia` | Farmacia | Administración |
| `residuos` | Recolección de residuos y logística | Administración |
| `comercio`, `indumentaria`, `dieteticas`, `mercado`, `agro`, `ganaderia`, `servicios` | (varias) | Gestión |
| *(no mapeada)* | — | Gestión |

Grupos y lista de dominios **fijos en código** en `Application/Helpers`, junto a `RubroHelpers` (decisión de Joaquín 2026-09-14): una sola fuente de verdad; cambiar un grupo implica redeploy.

**Cuándo se asigna:**
- Al crear el contacto desde Google Maps.
- Una vez, al desplegar, para los contactos outbound `Pendiente` existentes.
- En el lote de envío, como red de seguridad, si alguno sigue sin gancho — antes de elegir la plantilla.
- Una vez asignado **no se recalcula solo**; solo cambia si el usuario lo edita a mano o vuelve a "Automático".

#### 8.4 Qué cuenta como web propia (decisión: solo dominio propio)

- URL vacía → sin web propia.
- Se normaliza antes de comparar: minúsculas, sin `http(s)://`, sin `www.`, sin ruta.
- **Solo cuenta un dominio propio del negocio** (ej. `modalu.com.ar`), aunque esté alojado en una plataforma de tiendas o sitios.
- **No cuentan** (host o subdominio de):
  - Redes y mensajería: `instagram.com`, `facebook.com`, `fb.com`, `fb.me`, `wa.me`, `wa.link`, `whatsapp.com`, `tiktok.com`, `twitter.com`, `x.com`, `youtube.com`, `linkedin.com`.
  - Agregadores de links: `linktr.ee`, `beacons.ai`, `taplink.cc`, `bio.link`, `linkin.bio`.
  - Plataformas de tienda o sitio con subdominio: `mitiendanube.com`, `tiendanube.com`, `empretienda.com`, `wixsite.com`, `sites.google.com`, `blogspot.com`, `wordpress.com`, `godaddysites.com`, `business.site`, `g.page`.
  - Marketplaces y apps de delivery: `mercadolibre.com.ar`, `mercadoshops.com.ar`, `pedidosya.com`, `rappi.com.ar`.
  - Links de mapas: `goo.gl`, `maps.app.goo.gl`.

#### 8.5 Primer contacto frío: plantilla por gancho, siempre con el combo

**Selección de plantilla al enviar:**

| Caso | Plantilla |
|---|---|
| Canal Referido | `olv_referido_v2` (sin cambios) |
| Gancho Gestión con plantilla configurada, activa y aprobada | La plantilla combo de Gestión |
| Gancho Gestión sin plantilla combo disponible, o sin gancho | La de la campaña (`v13`, incluye A/B) — **comportamiento actual intacto** |
| Gancho Presencia web / Administración / Consultas | La configurada para ese gancho en `/Bot` (8.9). Sin A/B en esta entrega |
| Esos 3 ganchos sin plantilla configurada, o no aprobada / inactiva | **No se envía**: sigue `Pendiente`, no consume cupo ni presupuesto, se cuenta en `/Bot` y `/Bot/Salud`. Nunca cae a `v13` en silencio |

**Estructura común de las 4 plantillas:** dolor del gancho (con placeholder) → "Soy Joaquín, de Olvidata Soft." → producto del gancho en una frase → **"Y si te suma, también…"** con el resto del combo en una frase → "Te sirve?" → firma. Mismos 2 botones y payloads que `v13` (`seguir` / `no_interesa`); dejan al contacto en `ConfirmandoContinuar`. Placeholders siempre en medio de la frase (Meta rechaza variables al principio o al final).

**Borradores** — base aprobada para pasar a `olvidata-marketing` (que además decide la firma, ver R7) y después a Meta (categoría MARKETING):

- **`olv_frio_combo_web_v1`** — `{{1}}` = plural del rubro. No afirma que no tenga web (mitigación R2):
  > Hola! Vi tu negocio y pensé: hoy muchos {{1}} se eligen por lo que la gente encuentra en Google antes de llamar.
  >
  > Soy Joaquín, de Olvidata Soft. Armamos páginas con movimiento 3D que muestran lo tuyo con otra presencia. Y si te suma, también un asistente que contesta solo las consultas de WhatsApp y agentes de IA que se ocupan de la parte administrativa.
  >
  > Te sirve?
  >
  > Un saludo,
  > Joaquín
  > Olvidata Soft
- **`olv_frio_combo_admin_v1`** — `{{1}}` = plural del rubro:
  > Hola! Vi tu negocio y pensé: en muchos {{1}} se van horas por semana cargando planillas, armando reportes o conciliando pagos a mano.
  >
  > Soy Joaquín, de Olvidata Soft. Armamos agentes de IA que hacen ese trabajo administrativo solos. Y si te suma, también un asistente que responde las consultas de WhatsApp las 24 horas y una página 3D para que te encuentren.
  >
  > Te sirve?
  >
  > (firma)
- **`olv_frio_combo_consultas_v1`** — `{{1}}` = plural del rubro:
  > Hola! Vi tu negocio y pensé: en muchos {{1}} se pierden consultas por WhatsApp fuera de horario o mientras atienden a otro cliente.
  >
  > Soy Joaquín, de Olvidata Soft. Armamos un asistente que contesta, filtra y agenda esas consultas solo, las 24 horas. Y si te suma, también agentes de IA para la parte administrativa y una página 3D para que te encuentren.
  >
  > Te sirve?
  >
  > (firma)
- **`olv_frio_combo_gestion_v1`** — `{{1}}` = dolor y `{{2}}` = área, de la narrativa por rubro que ya usa `v13`:
  > Hola! Vi tu negocio y pensé: {{1}}.
  >
  > Soy Joaquín, de Olvidata Soft. Armamos sistemas a medida para ordenar {{2}} de una vez por todas. Y si te suma, también agentes de IA, un asistente de WhatsApp y una página 3D.
  >
  > Te sirve?
  >
  > (firma)

#### 8.6 Conversación después del botón

El toque de "Sí, contame más" lo sigue resolviendo el árbol (respuesta exacta, no se le paga a la IA por interpretarla), según el gancho:

| Gancho | Categoría que se fija | Primera pregunta |
|---|---|---|
| Gestión o sin gancho | `rent` (como hoy) | Pregunta 1 de gestión, con módulos de Build si hay matriz — **sin cambios** |
| Presencia web | `landing` | "Partís de cero o ya tenés algo online?" (pregunta vigente, no presupone que no tenga web) |
| Administración | `ai_agents` | "Qué tarea administrativa les consume más horas por semana hoy?" |
| Consultas | `chatbot` | "Por dónde les llegan más consultas hoy y qué es lo que más les preguntan?" |

- El rubro se resuelve igual que hoy (clave cruda → industria).
- Si hay módulos cargados para el frente de esa categoría y el rubro (8.10), la primera pregunta los nombra; si no, va la pregunta fija de la tabla.
- "No me interesa": sin cambios (baja).
- Lo que escriba después lo atiende la IA, con este contexto en el bloque del contacto: "Le escribimos ofreciendo página 3D, agentes de IA y asistente de WhatsApp (además de sistemas de gestión), abriendo por {gancho} ({motivo})."

**Cuestionarios del árbol para las categorías nuevas** (solo si la IA no está disponible):
- `ai_agents`: 1) "Qué tarea administrativa les consume más horas por semana hoy?" 2) "Con qué la hacen ahora? (Excel, un sistema, a mano)"
- `chatbot`: 1) "Por dónde les llegan más consultas hoy y qué es lo que más les preguntan?" 2) "Quién las contesta ahora y en qué horario?"

#### 8.7 Fallback del árbol (R1)

| Situación | Hoy | Diseño |
|---|---|---|
| IA cae con el contacto en `ConversandoConIa` y categoría `ai_agents`/`chatbot` | No encuentra la clave → reinicia con saludo y menú | La clave existe (8.6) → sigue el cuestionario, sin presentarse de nuevo |
| Contacto en `AskingQuestions` con categoría sin cuestionario | `KeyNotFoundException` | Escala a humano: `DerivadoManual`, nota interna "categoría sin cuestionario", notificación a Joaquín; al prospecto no le llega ningún error |
| Contacto histórico con `merge` en medio de un cuestionario | Usa `Questions["merge"]` | Se conserva esa entrada solo para no cortar conversaciones viejas; ninguna vía nueva asigna `merge` |
| Menú de bienvenida inbound (fallback de ads) | 3 botones | Sin cambios en esta entrega (el inbound lo atiende la IA con el vocabulario nuevo) |

#### 8.8 Contrato funcional del prompt de la IA

- **Identidad:** "Sos Joaquín, de Olvidata Soft, un estudio argentino que arma páginas web con 3D, sistemas de gestión a medida, agentes de IA para tareas administrativas y asistentes que atienden consultas por WhatsApp."
- **Categorías:** las 7 vigentes, cada una con descripción y 2 ejemplos de dolor. `merge` sale de la lista y de la validación de `set_categoria`.
- **Venta cruzada (combo):** primero entender el dolor concreto del gancho (regla vigente "dolor antes que pitch"). Recién con el dolor registrado, mencionar **en una sola línea** que eso se puede combinar con los otros frentes del combo (ej. "y eso lo podemos sumar con un asistente que te conteste WhatsApp"). Sin listas, sin precios, una sola vez por conversación.
- **Web simple:** si pide "algo simple" o "barato" para la web, registrar `landing`; la variante 2D la define Joaquín en la propuesta (la IA no habla de 2D/3D ni de precios).
- **Cliente actual pidiendo una mejora:** `escalar_a_humano` en ese mismo mensaje (P5b).
- **`consultar_modulos_del_rubro`:** módulos del frente de la categoría actual (8.10).
- **Sin cambios:** no da precios ni plazos, detección de no-humano primero, objeciones, 7 guardas globales.

#### 8.9 Pantallas

**`Contactos/Index`** — 2 columnas nuevas con su filtro (regla columnas = filtros), persistidas en `Session` y limpiadas por "Limpiar filtros":

```
Contactos                                                    [+ Nuevo contacto] [Pipeline]
Listado de prospectos, con el gancho con que se les escribió y lo que terminaron pidiendo.
┌ Filtros ───────────────────────────────────────────────────────────────────────────┐
│ [Estado ▾] [Canal ▾] [Rubro ▾] [Gancho ▾] [Interés detectado ▾] [📅 Última act.]    │
│                                                              [Limpiar filtros]      │
└─────────────────────────────────────────────────────────────────────────────────────┘
Teléfono  │ Nombre │ Negocio        │ Rubro        │ Canal    │ Gancho          │ Interés detectado │ Estado          │ Últ. actividad
549221... │ Equipo │ Inmob. Del Sur │ Inmuebles    │ Outbound │ [Consultas]     │ Sin clasificar    │ Mensaje enviado │ 14/09/2026
549351... │ Equipo │ Moda Lu        │ Indumentaria │ Outbound │ [Presencia web] │ Página web        │ Respondido      │ 14/09/2026
549223... │ Ana    │ Estudio Pérez  │ Contabilidad │ Ads      │ —               │ Agentes de IA     │ Derivado manual │ 13/09/2026
```

- Filtro "Gancho" (Select2): Sin gancho · Presencia web · Administración · Consultas · Gestión.
- Filtro "Interés detectado" (Select2): las 8 etiquetas de 8.2.
- Badge por gancho (`ov-badge`): Presencia web = primario `#2b9de4`, Administración = violeta, Consultas = verde, Gestión = gris azulado; "discontinuado" en gris.

**`Chats/Index`** — filtro "Gancho" en la barra existente (Select2, en `Session`) y chip al lado del rubro en cada fila:

```
Juan · Inmob. Del Sur · Inmuebles [Consultas]          Respondido     ✉️
"Sí, contame más"                                       Ventana cierra en 21h 10m
```

**`Contactos/Details` y ficha desplegable de `Chats/Detail`** — card "Oferta" con `.ov-detail-grid`:

```
┌ 🎯 Oferta ───────────────────────────────────────────────────────────┐
│ Se le ofreció         Página 3D + agentes de IA + asistente de WhatsApp │
│ Gancho                [Presencia web]                                  │
│ Por qué               Web en plataforma o redes (instagram.com)        │
│ Asignado              14/09/2026 · automático                          │
│ Interés detectado     Página web                                       │
└────────────────────────────────────────────────────────────────────────┘
```

- Con gancho Gestión: "Se le ofreció: Sistema de gestión + agentes de IA + asistente de WhatsApp + página 3D" (o "Plantilla de la campaña" si salió con `v13`).
- Sin gancho: "Sin oferta en frío (no es un contacto frío)", con `.ov-detail-item__value--empty`.

**`Contactos/Create` y `Contactos/Edit`** — card "Oferta":

```
┌ 🎯 Oferta ───────────────────────────────────────────────────────────────┐
│ Página web            [https://modalu.mitiendanube.com         ]           │
│                       Solo cuenta un dominio propio; redes, plataformas    │
│                       y marketplaces cuentan como sin web propia.          │
│ Gancho del mensaje    [Automático (lo decide el sistema) ▾]                │
│                       Automático: sin web propia → Presencia web; con web, │
│                       según el rubro. Elegilo a mano solo para forzar otro │
│                       gancho antes del primer envío.                       │
└────────────────────────────────────────────────────────────────────────────┘
```

- "Gancho del mensaje" (Select2): Automático · Presencia web · Administración · Consultas · Gestión. Volver a "Automático" recalcula al guardar.
- "Página web" se agrega a Create/Edit si hoy no está (regla 10b-bis).
- **Excepción documentada a 10b-bis:** "Interés detectado", "Por qué" y "Asignado" son solo lectura.
- Cambiar el gancho de un contacto que ya recibió el primer mensaje: se permite, con aviso ("Ya se le escribió abriendo por {gancho}; el cambio solo afecta a la conversación de ahora en más").

**`Bot/Index`, sección 5 "Configuración"** — card "Plantillas de primer contacto (combo)":

```
┌ ✉️ Plantillas de primer contacto (combo) ────────────────────────────────────────────┐
│ Todos reciben el combo; la plantilla cambia según el gancho que asignó el sistema.     │
│                                                                                        │
│ Gancho         │ Plantilla                          │ Estado                 │ Esperando │
│ Presencia web  │ [olv_frio_combo_web_v1 ▾]          │ ✅ Lista               │ 140       │
│ Administración │ [Sin asignar ▾]                    │ ⚠️ No se envían        │ 22        │
│ Consultas      │ [olv_frio_combo_consultas_v1 ▾]    │ ✅ Lista               │ 95        │
│ Gestión        │ [Sin asignar ▾]                    │ ↩️ Usa la de la campaña │ 312       │
│                                                                   [Guardar plantillas] │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

- Los selects ofrecen solo plantillas activas y aprobadas (regla vigente de selectores de envío).
- "Esperando" = contactos outbound `Pendiente` con ese gancho.

**`Bot/Salud`** — bloque "Ganchos que no se están enviando": gancho, motivo (sin plantilla / no aprobada / inactiva) y contactos esperando. Gestión nunca aparece (cae a la plantilla de campaña).

**Catálogo de módulos (`Modulos/Index`, `Create`, `Edit`)** — sin alterar la matriz de Build (R9):
- `Index`: columna "Frente" con su filtro.
- `Create`/`Edit`: campo "Frente" obligatorio (Select2: Build · Landing · AI Agents · Chatbots), default Build. Hint: "Build usa la matriz MVP/FULL por rubro. En los demás frentes, dejar los rubros vacíos significa que el módulo aplica a todos los rubros".
- Todos los módulos existentes quedan en Build.

**Armar presupuesto (`/Modulos/Presupuesto` y modal de `Chats/Detail`)** — selector **múltiple** "Frentes" arriba del rubro, para armar la propuesta del combo en un solo checklist agrupado por frente. Default desde un chat: Landing + AI Agents + Chatbots, más Build si el interés detectado es de gestión; desde `/Modulos`: Build. Con solo Build el checklist es idéntico al de hoy.

#### 8.10 Módulos por frente (regla de lectura)

- **Build**: igual que hoy (rubro + flag MVP/FULL).
- **Otros frentes**: módulos asignados al rubro del contacto + módulos del frente sin ningún rubro (genéricos).
- `consultar_modulos_del_rubro` y la pregunta 1 con módulos usan el frente de la categoría actual (`landing` → Landing, `ai_agents` → AI Agents, `chatbot` → Chatbots, `rent`/`rent_other`/`build` → Build).
- Contenido (qué módulos, qué precio) lo define `olvidata-presupuesto-bot`; sin carga, se usa la pregunta fija de 8.6.

#### 8.11 ViewModels (cambios)

```
ContactoListItemVM     + GanchoTexto, GanchoClase, InteresDetectadoTexto
ContactoFiltros        + Gancho (PresenciaWeb|Administracion|Consultas|Gestion|SinGancho), InteresDetectado (clave de Categoria | "sin_clasificar")
ContactoDetailsVM      + OfertaTexto, GanchoTexto, MotivoGancho, FechaAsignacionGancho, GanchoAsignadoAMano, InteresDetectadoTexto
ContactoCreateVM/EditVM + PaginaWeb [StringLength 500, URL o dominio opcional], GanchoElegido (null = Automático), AvisoGanchoYaEnviado (solo Edit, calculado)
ChatFiltrosViewModel   + Gancho
ChatListItemViewModel  + GanchoTexto, GanchoClase
ChatDetailViewModel    + OfertaTexto, GanchoTexto, MotivoGancho, FechaAsignacionGancho, InteresDetectadoTexto
PlantillasPorGanchoVM  { PlantillaPresenciaWeb, PlantillaAdministracion, PlantillaConsultas, PlantillaGestion [cada una opcional; si viene, activa y aprobada],
                         Filas: List<{ Gancho, Plantilla, EstadoTexto, EstadoClase, ContactosEsperando }> }
BotSaludVM             + GanchosSinEnvio: List<{ Gancho, Motivo, ContactosEsperando }>
ModuloCatalogoCreateViewModel + Frente [Required, default Build]
ModuloCatalogoIndexItem       + FrenteTexto (con filtro)
ArmarPresupuestoViewModel     + Frentes: List (min 1; default según 8.9)
```

Validaciones funcionales:
- `GanchoElegido` ∈ opciones válidas, o vacío.
- `PaginaWeb` opcional; si viene, tiene que parecer una URL o un dominio.
- Plantilla por gancho no activa o no aprobada → error de validación en la card, no se guarda.
- `Frente` del módulo obligatorio; con Build, al menos un rubro (como hoy); con otro frente, rubros opcionales.
- Armar presupuesto: al menos un frente seleccionado.

#### 8.12 Reglas de negocio y permisos

- Único rol `SuperUsuario` (sin cambios).
- Todo contacto frío con gancho recibe el combo; el gancho solo cambia por dónde abre el mensaje.
- La asignación del gancho es determinística (8.3), se guarda con motivo y fecha, y nunca la decide la IA.
- Presencia web / Administración / Consultas sin plantilla disponible → no se envía ni consume cupo o tope.
- Gestión sin plantilla combo → usa la de la campaña: Build (plantilla, A/B, pregunta 1, matriz MVP/FULL) sigue funcionando igual que hoy.
- La IA menciona el combo una sola vez, después del dolor, sin precios.
- Ninguna vía nueva escribe `Categoria = "merge"`; los históricos se muestran como discontinuados.
- El gancho es dato interno; nunca se muestra al prospecto.

#### 8.13 Datos esperados (requerimiento funcional; el diseño técnico lo decide Arquitectura)

- `Contacto`: gancho (vacío = sin gancho), motivo (texto corto), fecha de asignación, marca "asignado a mano", y cuál plantilla salió efectivamente (combo o de campaña) para poder mostrar "Se le ofreció".
- `ModuloCatalogo`: frente (existentes = Build).
- `ConfiguracionOutbound`: plantilla por cada uno de los 4 ganchos (vacía = sin asignar).
- Vocabulario en `Application/Helpers`: grupos de rubro (Administración / Consultas) y dominios que no cuentan como web propia.
- Carga inicial: asignar gancho a los contactos outbound `Pendiente` existentes.
- Máquina de estados: **no cambia** (cambia qué categoría y qué pregunta se usan en `ConfirmandoContinuar → AskingQuestions`).

#### 8.14 Riesgos y supuestos

Heredados de `1-analista-funcional.md` y asumidos por este diseño:
- **R2 (aceptado):** web vacía = sin web. Mitigado con una plantilla que no afirma "no tenés web" y una primera pregunta que no lo presupone.
- **R3 — Presencia web dominante, más fuerte con "solo dominio propio":** Tiendanube, Wix, redes y marketplaces también caen ahí. Probablemente la mayoría del outbound abra por Presencia web. Se mide con el filtro por gancho desde la primera tanda.
- **R4 — Aprobación de Meta:** hasta que se aprueben, esos ganchos no se envían (visible en `/Bot`); Gestión sigue con la plantilla de campaña.
- **R7 — Marca:** firma igual a `v13` en los borradores; la decide `olvidata-marketing` (regla de marca personal "con el respaldo de Olvidata").
- **S3:** gancho automático solo para outbound.
- **S5:** la web tiene prioridad sobre el rubro.

Nuevos de esta etapa:
- **D-R1 — Botón de continuar:** resuelto por diseño (8.6).
- **D-R2 — Grupos por rubro y dominios:** con el combo el impacto de un error baja (todos reciben la misma oferta, solo cambia el gancho), pero sigue siendo una hipótesis a medir.
- **D-R3 — Grupos en código:** cambiar un rubro de grupo requiere redeploy (decisión de Joaquín).
- **D-R4 — Sin A/B por gancho** en esta entrega.
- **D-R5 — Gancho cambiado después del envío:** el prospecto ya leyó otro mensaje; el aviso en Edit lo hace explícito.
- **D-R6 — El combo alarga el mensaje y reparte el foco:** el aprendizaje del historial es que cierra quien nombra UN dolor concreto. Un mensaje con 3 productos puede bajar la tasa de respuesta frente a uno de un solo dolor. Mitigación: el combo va en una sola frase después del dolor, y la tasa se mide por gancho contra la línea base de `v13`.
- **D-R7 — Precio del combo no definido:** la propuesta post-demo necesita un precio de paquete (setup + recurrente de Landing 3D + AI Agents + Chatbots). Lo define `olvidata-ceo`; no bloquea Arquitectura, sí la primera propuesta real.

#### 8.15 Plan funcional por etapas (para Arquitectura)

| Etapa | Contenido | Migración | Depende de |
|---|---|---|---|
| E1 — Vocabulario y árbol | Categorías `ai_agents`/`chatbot` (IA + árbol + etiquetas), cuestionarios de 8.6, `merge` fuera de la IA y "discontinuado", fallback de categoría sin cuestionario (8.7) | No | — |
| E2 — Prompt de la IA | Identidad, descripciones y ejemplos, venta cruzada del combo, web simple, cliente actual (8.8) | No | E1 |
| E3 — Gancho en el contacto | Datos de 8.13, helpers de grupos y web propia, asignación al crear + carga inicial, card "Oferta", columnas y filtros en Contactos/Chats, campo en Create/Edit | Sí | E1 |
| E4 — Conversación por gancho | Botón "Sí, contame más" según gancho (8.6) + gancho y combo en el contexto de la IA | No | E2, E3 |
| E5 — Envío por gancho | Plantillas por gancho en configuración, card en `/Bot`, no-envío sin plantilla, fallback de Gestión a la campaña, bloque en `/Bot/Salud` | Sí | E3, E4. Para enviar: textos de marketing + aprobación de Meta |
| E6 — Módulos por frente | Frente en módulos, pantallas del catálogo, selector múltiple en Armar presupuesto, lectura de 8.10 | Sí | E1. Contenido: `olvidata-presupuesto-bot` |
| E7 — Documentación | `arbol-comunicacion-bot.md` y `logica-negocio-bot.md` | No | E1-E6 |

El outbound se reactiva con E1-E5 en producción (S4). E1-E2 se pueden desplegar antes: mejoran el inbound de ads sin tocar el envío.

#### 8.16 Estado de aprobación

**Decidido por Joaquín (2026-09-14):**
- Oferta en frío: combo Landing 3D + AI Agents + Chatbots para todos, con gancho según perfil.
- Build y Landing 2D siguen disponibles.
- Web propia: solo dominio propio.
- Grupos de rubro y lista de dominios fijos en código.
- Borradores de plantilla: pasan a `olvidata-marketing` antes de Meta.

**Interpretaciones confirmadas por Joaquín (2026-09-14):**
1. La tabla de grupos por rubro (8.3) se conserva, pero solo para elegir el gancho.
2. "Build sigue": Build entra como gancho Gestión (plantilla combo de gestión) y, mientras esa plantilla no esté aprobada, con la plantilla de campaña actual.
3. "Landing 2D sigue": no va en el primer mensaje (el combo lleva 3D); se ofrece en la propuesta si el prospecto pide algo más simple.
4. La IA menciona el combo una sola vez, después del dolor.

**Dependencias abiertas que no bloquean Arquitectura:** textos finales de `olvidata-marketing`; precio del combo (`olvidata-ceo`).

## Historial de ajustes
- 2026-07-14: Diseño funcional cerrado sobre el alcance recortado (solo migración de BotPublicitario). 5 pantallas, 2 máquinas de estados, 11 HU, plan funcional de 5 etapas.
- 2026-08-27: Diseño del sprint "corrección de bugs/gaps de auditoría + 3 mejoras" — 17 HU (7 bugs + 7 gaps + 3 mejoras), cada una con criterio de aceptación explícito. Decisión tomada: `PresupuestoCotizadoUsd` (G4) se hace editable a mano en vez de sacar las lecturas muertas — conserva valor funcional del campo.
- 2026-07-21: Diseño de "campañas de contacto frío configurables" — 4 pantallas, sin máquina de estados (flag `Activa`), 5 ViewModels, HU-14/15/16.
- 2026-07-24: Ajuste cosmético en Notificaciones (ícono + modal).
- 2026-08-14: Auditoría de proyecto — corregida la tabla de `EstadoEmbudo` (se retiran los 3 estados nunca implementados), corregida HU-11, cerrado el diseño retroactivo de `Chats` (CU-16 a CU-20, 2 pantallas).
- 2026-08-14: Diseño de "Gestión comercial y herramientas de canal/venta" — 9 pantallas nuevas/extendidas, sidebar "Negocio", 13 ViewModels, CU-21 a CU-29.
- 2026-08-14: Reestructuración documental — este archivo tenía 5 secciones fechadas acumuladas con wireframes/ViewModels/reglas repetidos y corregidos por nota al lado, en vez de una vista única del estado actual. Consolidado en una sola "Definiciones vigentes" (editada in-place de ahora en más) + este historial. Ningún dato funcional se perdió — mismo contenido, sin capas superpuestas.
- 2026-09-04: documentadas las 2 cards de control de costos de `Bot/Index` (Maps en USD, mensajería en ARS), el tope único sobre el costo total, el volumen diario derivado del precio y el pausado independiente de Maps.
- 2026-09-14: conversacion agentica con LLM como camino normal (el arbol pasa a fallback), fase `ConversandoConIa`, pausa del bot por contacto a 48hs, respuesta a multimedia en vez de silencio, reestructuracion de `Bot/Index` en 5 secciones y ampliacion del control de costos a 3 herramientas con reparto y techos derivados.
- 2026-09-14: Diseño de "reorientar el bot de prospección a los 4 frentes" (seccion 8, pendiente de aprobacion) — tabla de decision de frente (web propia + grupo de rubro), lista de dominios, 4 borradores de plantilla, conversacion post-boton por frente (hallazgo: el boton lo resuelve el arbol forzando `rent`), fallback de categorias nuevas, card "Oferta" + filtros en Contactos/Chats, plantillas por frente en `/Bot`, modulos por frente sin alterar Build, plan en 7 etapas. Patron nuevo PAT-031 en el catalogo.
- 2026-09-14: Seccion 8 rediseñada tras respuestas de Joaquin — combo Landing 3D + AI Agents + Chatbots para todos con gancho segun perfil (el dato por contacto pasa de "frente ofrecido" a "gancho"), Build y Landing 2D siguen, web propia = solo dominio propio, grupos/dominios en codigo, 4 plantillas combo por gancho (Gestion cae a la plantilla de campaña), venta cruzada en el prompt, selector multiple de frentes en Armar presupuesto. Pendiente confirmar 4 interpretaciones (8.16).
