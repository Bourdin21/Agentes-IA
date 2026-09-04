# Memoria - Disenador funcional

## Proyecto: crm-olvidata — CRM interno de OlvidataSoft
## Última actualización: 2026-08-27

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

**`Bot/Index`** (panel principal) — stat-cards Enviados hoy/Pendientes; card Estado del scheduler (botón "Ejecutar ahora" — CU-10, encola en background, no bloquea el request, con indicador "Corrida en curso..." mientras corre); card resumen de Campañas (activas/pausadas + nombres, link a `Campanas/Index`); card búsqueda manual de prospectos (CU-11).

**Control de costos en `Bot/Index`** (2026-09-03/04) — el panel suma 2 cards de gasto real, cada una en la moneda en que factura su proveedor (no convertidas, para poder cruzarlas contra cada factura):

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

## Historial de ajustes
- 2026-07-14: Diseño funcional cerrado sobre el alcance recortado (solo migración de BotPublicitario). 5 pantallas, 2 máquinas de estados, 11 HU, plan funcional de 5 etapas.
- 2026-08-27: Diseño del sprint "corrección de bugs/gaps de auditoría + 3 mejoras" — 17 HU (7 bugs + 7 gaps + 3 mejoras), cada una con criterio de aceptación explícito. Decisión tomada: `PresupuestoCotizadoUsd` (G4) se hace editable a mano en vez de sacar las lecturas muertas — conserva valor funcional del campo.
- 2026-07-21: Diseño de "campañas de contacto frío configurables" — 4 pantallas, sin máquina de estados (flag `Activa`), 5 ViewModels, HU-14/15/16.
- 2026-07-24: Ajuste cosmético en Notificaciones (ícono + modal).
- 2026-08-14: Auditoría de proyecto — corregida la tabla de `EstadoEmbudo` (se retiran los 3 estados nunca implementados), corregida HU-11, cerrado el diseño retroactivo de `Chats` (CU-16 a CU-20, 2 pantallas).
- 2026-08-14: Diseño de "Gestión comercial y herramientas de canal/venta" — 9 pantallas nuevas/extendidas, sidebar "Negocio", 13 ViewModels, CU-21 a CU-29.
- 2026-08-14: Reestructuración documental — este archivo tenía 5 secciones fechadas acumuladas con wireframes/ViewModels/reglas repetidos y corregidos por nota al lado, en vez de una vista única del estado actual. Consolidado en una sola "Definiciones vigentes" (editada in-place de ahora en más) + este historial. Ningún dato funcional se perdió — mismo contenido, sin capas superpuestas.
- 2026-09-04: documentadas las 2 cards de control de costos de `Bot/Index` (Maps en USD, mensajería en ARS), el tope único sobre el costo total, el volumen diario derivado del precio y el pausado independiente de Maps.
