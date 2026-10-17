# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

> Entradas anteriores al 2026-07-15: ver `trazabilidad-historico-hasta-2026-07-14.md` (archivo cerrado, 2026-07-14 a 2026-07-14).

## Entradas

### 2026-10-16 - implementador (CRM-032: el toque se podia pagar dos veces durante el vuelo del envio)

- **Defecto propio, emitido por QA (minor).** El boton se rehabilitaba en el `always()` del `getJSON`
  de opciones —antes del POST de envio— y la marca de salida se escribia despues del envio. Durante el
  vuelo del POST pagado la fila aceptaba un segundo toque y los dos pasaban todos los guards.
- **Cliente**: el boton de la fila queda deshabilitado desde el click hasta que resuelve el POST de
  envio. 5 puntos de liberacion y solo esos (servidor bloquea, falla la consulta, cancelar cualquiera
  de los 2 modales, sin plantillas) mas el `always()` de `enviar()`.
- **Servidor — reserva atomica, que es el arreglo de fondo.** Antes de enviar, un UPDATE condicional
  unico (`ExecuteUpdateAsync`, ya usado en el repo) escribe `FechaFollowUp = ahora` con el `WHERE`
  **igual al criterio de la cola**. 1 fila afectada = gana y envia; 0 = rechaza sin enviar. La
  atomicidad la da MySQL en una sentencia, asi que vale entre requests concurrentes y no depende del
  orden en que corra el codigo. La proteccion del cliente sola no servia: un POST a mano la saltea.
- **El modo de falla se invirtio a proposito**: de "se envio y no se pudo marcar" (riesgo de pagar dos
  veces) a "se marco y no se pudo enviar", con liberacion de la reserva restaurando el valor anterior
  EXACTO (puede no ser null: un follow-up frio viejo). Si tampoco se puede liberar, se avisa — el
  contacto queda fuera de la cola sin mensaje, sin plata gastada y recuperable. Tambien se libera
  cuando `ReactivarConversacionAsync` devuelve `!Ok` (tope de gasto, plantilla ya enviada): sin eso el
  contacto salia de la cola en silencio sin que nadie lo hubiera contactado.
- **Concurrencia MEDIDA, no supuesta.** Sonda desechable contra un clon de dev con el sender
  reemplazado por un fake sin red: **8 toques concurrentes (8 scopes de DI = 8 conexiones, abiertas
  antes de la barrera) -> 1 gana, 7 rechazados, 1 solo envio**; con el envio fallando, 4 concurrentes
  dan 0 Ok, 1 solo intento y la marca liberada; despues de liberar vuelve a la cola y el reintento
  sale. Una prueba secuencial habria dado **falso verde**: con un solo DbContext las sentencias se
  serializan solas.
- **Nota de arnes**: la primera corrida dijo "no vuelve a la cola". Era contaminacion mia — reuse el
  contacto del escenario concurrente, cuyo envio exitoso le dejo un mensaje posterior, asi que quedaba
  **correctamente** excluido por el ajuste del 2026-10-16. Re-medido sobre un contacto limpio, bien.
- dev quedo intacta (444 contactos, 0 `FechaFollowUp`, 0 filas de fixture), el clon desechable se
  dropeo y el clon de QA (`olvidatacrm_qacola`) no se toco. **Cero mensajes enviados, sin commit y sin
  deploy.**
- **CRM-031 NO se arreglo** (plantillas centinela clasificadas como texto fijo en `/Chats`):
  preexistente, major, y su fix de fondo es `Proposito` + `CantidadParametros` en `TemplateWhatsApp`
  con migracion. Es otro ciclo.
- **El defecto queda "aplicado, pendiente de re-verificacion"** — el cierre lo declara QA.

### Traza de corrida -- 2026-10-16 / etapa implementacion (CRM-032)
- Reintentos: 1
- Criterios fallados: 1, y era del arnes y no del sistema (ver la nota de arnes de arriba): el
  escenario de liberacion reciclaba el contacto del escenario anterior.
- Reglas releidas: ninguna del catalogo. Si se releyo la memoria propia sobre probar concurrencia (N
  scopes de DI + barrera, abrir las conexiones antes, contar FILAS y no respuestas) y sobre clonar dev
  en vez de respaldarla cuando la sonda escribe — las dos aplicaron tal cual.

### 2026-10-16 - implementador (cola de seguimiento: 2 ajustes del coordinador antes de QA)

- **Lista blanca de plantillas de reenganche** (`Application/Helpers/PlantillasReenganche.cs`, nuevo).
  Criterio de inclusión y no de exclusión: el contacto ya respondió, así que una plantilla de primer
  contacto le habla como si no nos conociera y una de renovación le habla de un plan que no tiene. Con
  lista negra, cada plantilla nueva dada de alta en `/Templates` entraría sola. Se aplica al combo
  **y como guarda del servidor**, porque `ReactivarConversacionAsync` valida contra todas las
  aprobadas de texto fijo y un POST a mano pasaría. Deuda anotada: lo correcto es un campo `Proposito`
  en `TemplateWhatsApp`, sin migración ahora.
- **La lista quedó en 2, no en 3.** `olv_nurturing_v2` es de reenganche pero **pide 3 parámetros de
  body** (los arma `BuildFollowUpComponents`) y el camino de envío de esta pantalla manda
  `components = null`: Meta rechaza un envío con menos parámetros de los que el template declara. Es
  limitación técnica, no criterio comercial, y quedó anotada para cuando haya un camino que los arme.
- **Hallazgo que vale más que el ajuste**: el filtro de "texto fijo" de
  `PlantillasTextoFijoAprobadasAsync` es `!Texto.Contains('{')` sobre la **copia local** del texto, y
  la copia local de 3 plantillas es el centinela `"(el texto vive en Meta — ...)"`, que no tiene
  llaves. O sea que lee **"no sé cuál es el texto" como "no tiene parámetros"**. `olv_nurturing_v2`,
  `olv_referido_v2` y `olv_notif_respuesta` están hoy en el combo de `/Chats` clasificadas como texto
  fijo y las tres llevan parámetros. No se tocó `/Chats` (fuera de alcance), pero es un defecto
  preexistente para QA y el argumento más fuerte para el campo `Proposito`.
- **Corrección a mi advertencia anterior**: `olv_frio_combo_admin_v2` **no es interna** — "admin" es el
  gancho Administración, uno de los 4 del combo. Queda afuera por ser de primer contacto. La única
  interna es `olv_notif_respuesta`.
- **Los ya contactados salen de la cola por defecto** (decisión del cliente): volver a escribirle a
  alguien ya contactado paga una plantilla y encima queda mal. El filtro pasó a
  `IncluirConToquePosterior` (default false), la columna y el filtro se mantienen, y el encabezado dice
  cuántos quedaron afuera. La exclusión vive en un solo lugar; `GetOpcionesToqueAsync` consulta
  incluyéndolos para que un contacto traído con el filtro siga siendo elegible, y el modal abre con un
  aviso rojo con la fecha.
- **Remedido contra producción**: universo **320**, cola de trabajo **270**, **50 excluidos**, 180 con
  matriz (eran 208 sobre el universo), 0 con ventana abierta. El cambio no es cosmético: **el que era
  el primero de la cola** (#9954, 7 días, rubro con matriz) **ya había recibido un mensaje el
  2026-10-08**. Era justo el contacto al que se le iba a pagar una plantilla de más.
- **Evidencia**: build 0 errores (mismas 21 advertencias preexistentes), `node --check` sobre el JS, y
  una segunda sonda de solo lectura que verificó la aritmética de la exclusión, el combo de 2 con la
  sugerida preseleccionada, y que la guarda del servidor rechaza las 5 plantillas no permitidas que se
  le pasaron a mano, cortando antes de tocar la red. **Cero mensajes enviados, sin commit y sin deploy.**

### Traza de corrida -- 2026-10-16 / etapa implementacion (ajustes)
- Reintentos: 0
- Criterios fallados: ninguno propio. 1 instrucción del brief corregida con evidencia:
  `olv_nurturing_v2` no podía entrar en la lista blanca (3 parámetros de body contra un envío que
  manda `components = null`).
- Reglas releidas: ninguna. La decisión de poner la guarda también del lado del servidor sale del
  criterio general de "no confiar en el combo", ya aplicado en `ReactivarConversacionAsync`.
- Nota: verificar los DATOS de las 23 plantillas (categoría, aprobación, si el texto tiene `{`) antes
  de escribir la lista fue lo que destapó el centinela. Con los nombres y el criterio comercial
  solamente, `olv_nurturing_v2` habría entrado y el primer envío real habría fallado contra Meta.

### 2026-10-15 - implementador (cola de seguimiento: la pieza que decide a quién le toca el próximo mensaje)

- **Qué se hizo**: pantalla `/Seguimiento` con la cola calculada, ordenada por valor y con el botón
  del toque. 6 archivos nuevos (`SeguimientoColaDtos`, `SugerenciasSeguimientoHelper`,
  `ISeguimientoColaService` en Application; `SeguimientoColaService` en Infrastructure;
  `SeguimientoController` y `Views/Seguimiento/Index.cshtml` en Web) y 2 tocados con un bloque cada
  uno: `DependencyInjection.cs` (+6) y `_Layout.cshtml` (+5). **0 migraciones EF.**
- **Por qué existe**: el hueco del `diagnostico-seguimiento-2026-10-16.md`. El motor de envío, el
  modelo de la cadencia y las plantillas para reabrir ya estaban; faltaba **el que decide a quién
  escribirle**, que era un botón que alguien tenía que apretar contacto por contacto.
- **Decisión de alcance sostenida**: sin scheduler. El `SeguimientoSchedulerService` se construye
  cuando el criterio esté validado a mano contra prospectos reales, no antes.
- **El número no coincide con el diagnóstico, y está bien**: con el criterio aprobado ("sin
  follow-up **posterior a su respuesta**") la cola son **320**, no 276. El 276 era
  `EstadoEmbudo = Respondido AND FechaFollowUp IS NULL`, o sea "nunca jamás". Los 28 contactos con
  `FechaFollowUp` de estos 3 estados la tienen **anterior** a su respuesta (follow-up frío, y después
  contestaron), así que vuelven a la cola con razón; más 16 de PresupuestoEnviado y 4 de
  DerivadoManual. **208 tienen matriz MVP/FULL** y van primero; **0 tienen la ventana de 24 h
  abierta**, o sea que hoy toda la cola necesita plantilla paga (ARS 89,55 cada una).
- **Hallazgo que hay que decidir**: `Contacto.FechaFollowUp` **no detecta los mensajes manuales** que
  un asesor ya mandó desde `/Chats` — lo escribe un solo lugar (`ProcessFollowUpsAsync`), que solo
  corre sobre `MensajeEnviado`. Son **50 contactos** a los que alguien ya les escribió después de que
  respondieron. No se los sacó de la cola en silencio: se calculan aparte, se muestran en su propia
  columna y tienen filtro. Si Joaquín quiere excluirlos por defecto, es 1 línea.
- **Reutilización, no construcción**: el envío con la ventana cerrada va por
  `OutboundCampaignService.ReactivarConversacionAsync` (la reactivación de `/Chats`), que ya valida la
  plantilla contra el catálogo, revalida la ventana y **chequea el tope de gasto**. Escribir un
  segundo camino de envío de plantillas habría sido exactamente CRM-017.
- **Bug propio encontrado ejecutando, no compilando**: el filtro de rango de fechas tiraba
  `ArgumentException` (500) según el `Kind` del `DateTime` que recibiera
  (`TimeZoneInfo.ConvertTimeToUtc` rechaza `Kind = Local` con una zona de origen que no es la local).
  El camino de la pantalla pasa por `TryParse` y nunca falla; la firma del service acepta cualquier
  llamador y con `DateTime.Today` revienta. El build lo daba por bueno. Corregido y verificado con los
  3 `Kind`.
- **Wart preexistente que conviene mirar**: el selector de plantillas de reactivación (el de
  `/Chats`, reusado acá) ofrece `olv_notif_respuesta`, que es el **aviso interno al admin**. El filtro
  de "texto fijo sin placeholders" no lo descarta. No se tocó por alcance, pero mandársela a un
  prospecto sería un error caro.
- **Evidencia**: build 0 errores (21 advertencias, todas preexistentes); vistas Razor verificadas
  como compilables inyectando un error deliberado; JS embebido con `node --check`; y una **sonda EF
  desechable** que resolvió el service por el contenedor de DI real y ejecutó la cola **contra
  producción en solo lectura**, probando que el LINQ nuevo traduce a MySQL (COALESCE de 3 términos,
  2 subconsultas correlacionadas con `Max` + `EF.Functions.Like`, `Count` por navegación) y los 16
  filtros uno por uno. Es lo que encontró el bug del `Kind`.
- **Cero mensajes enviados.** Ninguna plantilla, ningún texto libre. **Sin commit y sin deploy**, por
  instrucción explícita.
- **Pendiente**: QA funcional, y autorización de Joaquín para el primer lote de 30 del rubro Retail
  (ARS 2.686,50).

### Traza de corrida -- 2026-10-15 / etapa implementacion
- Reintentos: 1
- Criterios fallados: 1 — el filtro de rango de fechas tiraba `ArgumentException` (500) por el `Kind`
  del `DateTime`. No lo detectó el build: lo detectó ejecutar el filtro de verdad con la sonda.
- Reglas releidas: MH-001 y CRM-019 (ambas de la familia "no traduce contra MySQL" y ambas con
  antecedente en ESTE proyecto), CRM-024 (tope después de los filtros), CRM-017 (un tope tiene que
  chequearse en todos los caminos que lo gastan — fue lo que decidió reusar
  `ReactivarConversacionAsync` en vez de escribir un segundo camino de envío, y lo que decidió NO
  registrar el texto libre con `EtiquetaFollowUp`, que el contador de gasto cuenta como facturable).
- Nota: el brief avisaba de trabajo sin commitear en el repo (web push). **Era información vencida**:
  el working tree estaba limpio y esos cambios ya estaban commiteados (4 commits sin pushear). No
  hubo riesgo de pisar nada, pero el aviso costó una verificación previa.
- Nota: `5-implementador.md` llegó a 156 KB al escribir esta etapa y `archivar_memoria.py` no pudo
  detectar bloques archivables ("revisar a mano la estructura de headings"). Se archivó a mano
  (2026-07 y 2026-08 a `historial/`, con puntero de una línea por grupo) y quedó en 61 KB.

### 2026-10-16 - defecto abierto CRM-030 (minor, emitido por QA) - NO se arregla en esta corrida

- **Qué pasa**: `EstadosManualesPermitidos` es `Enum.GetValues<EstadoEmbudo>()`, o sea que **cualquier**
  estado del embudo es asignable a mano desde `/Contactos`. La secuencia que rompe el aviso:
  contacto avisado → pasa a `Descartado` desde `/Contactos` (ese camino estampa la lectura **común** y
  deja `FechaUltimaLecturaDeliberadaAgente` en NULL, ver CRM-029) → se lo vuelve a poner en
  `DerivadoManual` a mano. El chat queda sin avisar cuando el contacto escribe, porque
  `FechaUltimoAvisoDerivado` sobrevivió al viaje de ida y vuelta y la lectura deliberada nunca se
  escribió.
- **Severidad real**: minor. Solo se da cambiando el estado **sin abrir el chat**, y el chat sigue
  visible en la bandeja de no leídos de `/Chats`, así que no hay pérdida silenciosa de información:
  lo que se pierde es el aviso proactivo.
- **Hipótesis de fix de QA** (no implementada): limpiar `FechaUltimoAvisoDerivado` cuando el contacto
  **sale** de `DerivadoManual`. Es coherente con el resto del diseño —el marcador es estado del
  anti-ruido de *ese* tramo de conversación, no un histórico— y es aditivo, sin migración. Cuando se
  tome, conviene revisar de paso si `EstadosManualesPermitidos` debería ser una lista explícita en vez
  de todo el enum: es la causa de fondo que habilita transiciones que la máquina de estados no prevé.
- **Estado**: abierto, documentado, **sin tocar** por indicación explícita. No entra en el alcance de
  CRM-028 ni de CRM-029.

### 2026-10-16 - implementador (CRM-029: el anti-ruido del aviso push no sobrevivía a la pestaña abierta)

- **Disparador**: parte de defecto de QA sobre CRM-028 (minor, 19 PASS / 0 major en la corrida). El anti-ruido colgaba de `Contacto.FechaUltimaLecturaAgente`, y `Chats/HiloParcial` estampa esa fecha cada vez que el polling trae mensajes nuevos. Con la pestaña del chat abierta —el escenario más común: el asesor la deja abierta toda la jornada— el tick re-armaba el guard justo antes del mensaje siguiente: **3 mensajes, 3 avisos**, reproducido 3/3 por QA. Y en el peor caso sonaba mientras el asesor estaba mirando ese mismo chat.
- **La restricción que define el fix**: sacar el estampado de `HiloParcial` no era opción. De `FechaUltimaLecturaAgente` depende el "no leído" de la lista de Chats, y esa semántica ya tiene su propio bug histórico documentado arriba de `HiloParcial` (el tick pisaba el `MarcadoNoLeidoManual` que el asesor ponía a mano). Lo que tenía que cambiar era **de qué depende el re-armado**, no quién estampa qué.
- **Fix**: campo nuevo `Contacto.FechaUltimaLecturaDeliberadaAgente` y `EsperaAvisoDeChatDerivado` pasa a colgar de él. Las 2 fechas coexisten porque responden preguntas distintas: la vieja es "¿se mostró en pantalla?" (lista de no leídos), la nueva es "¿alguien hizo algo?" (anti-ruido del push). De los **6 puntos** de lectura, los **5 deliberados** (abrir el detalle, los 3 envíos, el marcado masivo) pasan por el método de dominio nuevo `RegistrarLecturaDeliberada(ahora)`, que estampa las 2 — CRM-001, para que quien agregue mañana una sexta acción de lectura no tenga que saber que la segunda fecha existe, que es exactamente lo que se rompió acá. `HiloParcial` es el único que **no** lo llama, con un comentario que dice que agregarlo ahí devuelve el defecto. `MarcarTodosLeidos` lo replica con `.SetProperty` porque es `ExecuteUpdateAsync` y no materializa entidades (mismo motivo por el que ya replicaba el stamping de `UpdatedAt`).
- **Decisión de alcance**: `RegistrarLecturaDeliberada` **no** toca `MarcadoNoLeidoManual`. De los 5 puntos que lo llaman, solo 2 limpiaban ese flag y los 3 de envío nunca lo hicieron; meterlo adentro cambiaría comportamiento legacy que nadie pidió cambiar.
- **Migración**: `AddLecturaDeliberadaChat`, **aditiva** (1 columna nullable), aplicada **solo en dev**. Lleva un `UPDATE` idempotente que siembra la columna nueva desde `FechaUltimaLecturaAgente`: sin él los ~10.000 contactos arrancan en "nadie leyó nunca este chat" y la columna no significa nada hasta que cada chat se abra una vez. Sin efecto observable hoy, porque `FechaUltimoAvisoDerivado` también arranca en NULL.
- **Observaciones cosméticas de QA, misma corrida**: `push.js` usaba `getRegistration('/push-sw.js')`, que toma una URL de **cliente** y no de script (funcionaba de casualidad porque el scope es la raíz) → ahora recorre `getRegistrations()` y matchea por `scriptURL`. Y el comentario del `_Layout` que decía "dos SW pueden compartir scope" quedó corregido: un scope tiene una sola registración, lo que justifica el filtro es que el scope no identifica al archivo.
- **Verificado**: build Release **0 errores** (21 advertencias preexistentes). Reproducido el escenario exacto del parte en dev, con el detalle abierto en background y el polling corriendo (6 llamadas a `HiloParcial` en el log): **3 mensajes → 1 aviso**, con `FechaUltimaLecturaAgente` en 00:06:24 (el polling siguió estampando, o sea que el guard viejo se habría re-armado) y la lectura deliberada en 00:05:51, anterior al aviso de 00:06:00. Y tras abrir el detalle deliberadamente, el mensaje siguiente **sí** avisó. Las 2 mitades del criterio de re-verificación de QA, medidas. `MarcarTodosLeidos` escribe la columna nueva (verificado aparte, es la única implementación que no pasa por el método de dominio). Datos de prueba borrados.
- **No probado**: los 3 puntos de envío por separado (comparten el método de dominio con `Detail`, que sí se ejercitó; dispararlos mandaría WhatsApp reales desde dev).
- **Estado**: el defecto queda **aplicado, pendiente de re-verificación**. El cierre lo declara QA, no esta corrida. Sin deploy y sin tocar producción.
- **Fuera de alcance por indicación**: pasar el envío de push a una cola (observación 1 de QA: ~8 s dentro del webhook con 3 dispositivos y uno inalcanzable).

### 2026-10-16 - defecto abierto, preexistente (no lo introduce CRM-028): OnNewAsync pierde el ContactoRespuesta si falla el envío

- **Origen**: hallazgo incidental de la corrida de QA de CRM-028, con el token de WhatsApp de dev inválido. **No lo introduce ese CR** y solo se manifiesta con credenciales rotas, así que se anota y no se toca.
- **Síntomas, los 2 del mismo origen**: (1) una notificación in-app apuntando a `/Contactos/Details/0` —el contacto es nuevo y todavía no tiene Id asignado cuando se arma la URL—, y (2) la pérdida del `ContactoRespuesta` del mensaje entrante: la excepción del envío sube hasta el `catch` del webhook y se pierde el `SaveChangesAsync` que iba a persistirlo.
- **Por qué importa igual**: el punto 2 es exactamente el modo de falla que la regla CRM-020 existe para evitar (que una falla de entrega haga perder el registro de lo que el contacto sí mandó). Que hoy solo se dispare con el token roto no lo hace inofensivo: un token vencido es un escenario real y recurrente en este sistema (los de Meta vencen a los 60 días).
- **Pendiente**: asignarle id de defecto y alcance propio. No entra en la corrida de CRM-029 por decisión explícita.

### 2026-10-15 - implementador-dotnet — sesion de la app instalada (PWA): 30 dias renovables
- Etapa: Implementacion (cambio cross-proyecto, pedido del owner: "en todas las versiones PWA el token de sesion dure un mes activo").
- Alcance: 14 sistemas con PWA tocados de una vez con el mismo parche. Solo cambia la sesion que arranca desde la app instalada; la del navegador queda igual que estaba.
- Que hace: `Views/Account/Login.cshtml` manda `EsPwa=true` cuando corre en `display-mode: standalone` (o `navigator.standalone` en iOS), y en `ConfigureApplicationCookie` dos eventos nuevos hacen el trabajo — `OnSigningIn` marca el ticket y le pone 30 dias propios, `OnValidatePrincipal` los vuelve a correr cuando queda menos de la mitad.
- Decision de diseno: NO se subio `ExpireTimeSpan`. Subirlo habria alargado tambien la sesion de una PC de mostrador compartida, que es justo lo que no se quiere.
- Lo que no es obvio (quedo en `PAT-070` y en la instruction `23-web`): la renovacion mueve `IssuedUtc` junto con `ExpiresUtc`, porque el handler de cookies no copia el vencimiento que se le deja — recalcula la vida como la diferencia entre ambos y la suma a ahora (medido con una duracion de prueba de 20 s: renovaba a 36 s). Y `OnValidatePrincipal` se chainea, no se reemplaza: ahi vive el `SecurityStampValidator` que revoca la sesion al cambiar la password o bloquear al usuario.
- Impacto en capas: Web (`Program.cs`, `Views/Account/Login.cshtml`). Sin cambios en Application/Domain/Infrastructure, sin migracion EF, sin tocar permisos ni estados. No se toco el AccountController ni el LoginViewModel: el flag se lee del form en el evento.
- Verificacion (en local sobre blankproject, MySQL de dev, con una duracion de prueba de 20 s): navegador 8 h sin cambios; PWA 30 dias; sin renovar antes de la mitad de la ventana; renovacion exacta pasada la mitad; y 302 al login cuando la ventana vence sin uso. Build OK en los 14 (0 errores).
- Estado: COMMITEADO Y **DEPLOYADO A PRODUCCION** el 2026-10-15, junto con CRM-028/029 (que era justamente lo que lo bloqueaba). Verificado en vivo: el login de `portal.olvidata.com.ar` sirve el campo `EsPwa` y la deteccion de `display-mode: standalone`. **Correccion sobre la verificacion original de esta entrada**: decia "navegador 8 h sin cambios" como si valiera para los 14 sistemas, y no era cierto — en 5 el navegador estaba en 90 dias, con lo que la PWA quedaba con sesion MAS CORTA que el escritorio y el patron no aportaba nada. Corregido el 2026-10-15 bajando esos 5 a 8 h por decision de Joaquin (ver la trazabilidad de cada uno).
- El deploy sigue pendiente de que lo **ejecute Joaquín**: es la única acción de esta secuencia que no delegó (ver el runbook en `5-implementador.md`, sección de CRM-028). Al subirlo, cambiar este estado a DEPLOYADO con la fecha.


### 2026-10-15 - orquestador (deploy de CRM-028 + CRM-029 a produccion, con un incidente de secretos)

- Etapa: Implementacion / liberacion. Autorizacion explicita de Joaquin en la conversacion ("si a
  todo menos al certificado", y despues eligio "arreglar CRM-029 y deployar junto"). **El
  implementador se nego a deployar** y tenia razon: la autorizacion le llegaba relevada por el
  orquestador, no del owner, y es la accion que Joaquin se habia reservado. El deploy lo ejecuto el
  orquestador siguiendo el runbook que el implementador dejo escrito en `5-implementador.md`.
- Que subio: `1005cd2` (CRM-028, web push), `fb45699` (fix de CRM-029), `e5da865` (la sesion de un
  mes para la PWA, que esperaba justamente a que el web push se liberara) y `d3f5013` (el fix del
  incidente de abajo).
- **Correccion a la nota de credenciales**: el puerto 8172 (Web Deploy) **no** estaba bloqueado hoy
  desde la red de casa — `docs/credenciales.local.md` lo daba por bloqueado y a FTPS como unico
  camino. Se verifico abierto y el deploy salio por MSDeploy al primer intento (23 cambios: 8
  agregados, 0 eliminados, 15 actualizados).
- Migraciones: sin gap previo (produccion estaba en `AddModoSombraIaInstagram`).
  `AddPushSubscriptions` y `AddLecturaDeliberadaChat` aplicadas con `dotnet ef database update`
  contra produccion. **Siembra verificada con el numero real: 2769 = 2769 = 2769** (filas con
  `FechaUltimaLecturaDeliberadaAgente`, filas con `FechaUltimaLecturaAgente`, y el conteo medido
  antes de migrar). Los 10.235 contactos tienen `FechaUltimoAvisoDerivado` en NULL, asi que nadie
  arranca con el guard armado. Columna generada `EndpointHashVivo` y el unico
  `UX_PushSubscriptions_EndpointHash_Vivo` verificados en el esquema real.
- Backup previo: `C:/Sistemas/_backups/crm-olvidata/Contactos-20261015-2137.csv` (10.235 filas,
  4 MB) + el DDL de la tabla. El MCP de SmarterASP no pudo hacerlo (`database_create_backup`,
  `website_restart` y `website_list_environment_secrets` fallan en esta cuenta), asi que se hizo por
  pymysql.
- **INCIDENTE REAL, con la causa ya corregida.** El publish **sobreescribio
  `appsettings.Secrets.json` en el servidor**: produccion tenia 4 bloques (`Anthropic`, `Features`,
  `Olvidata_Instagram` y la privada de VAPID recien cargada) y la copia local de desarrollo —que
  solo tiene `Anthropic`— los piso. **Instagram, Features y la clave de push desaparecieron del
  servidor por unos minutos**, entre el publish y la restauracion. Se restauro por FTPS desde la
  copia bajada antes del deploy, y se verifico bloque por bloque que los 3 quedaron **identicos al
  original** mas `Push`. `appsettings.Production.json` tambien viajo pero su contenido local es
  identico al del servidor (hash verificado): sin daño ahi.
  - La causa **no** es `SkipExtraFilesOnServer` (eso solo evita borrar lo que no esta en el origen):
    el SDK web incluye el archivo en el publish por el glob `appsettings*.json` aunque este
    gitignoreado. Fix en `d3f5013`: `CopyToPublishDirectory="Never"`, verificado con un publish a
    carpeta. El riesgo estaba latente desde que existe el mecanismo y se materializo ahora porque
    los bloques de Instagram y Features se cargaron a mano **despues** del ultimo deploy exitoso.
  - Se chequearon los otros 12 sistemas del estudio: **ninguno tiene `appsettings.Secrets.json`**,
    el mecanismo es exclusivo de este CRM, asi que el riesgo no se repite en otro repo.
- Smoke test: `/` 200, `/Account/Login` 200 **con el campo `EsPwa` presente** (confirma que viajo
  `e5da865`), `/push-sw.js` 200 y servido como `text/javascript` (el riesgo de que IIS lo diera como
  `text/plain` y el navegador rechazara el service worker no se materializo), `/js/push.js` 200,
  `/Notifications` 302. `/Notifications/ClavePublica` pide sesion (302), asi que **`EstaConfigurado`
  no se pudo verificar sin login** — queda en el chequeo manual.
- Pendiente para Joaquin (5 minutos, con sesion): activar los avisos en su Chrome, recargar 3 veces,
  confirmar que el boton sigue en "activados" y que llega un globo con el CRM cerrado. Es R1 + la
  unica confirmacion de que la app lee la privada de VAPID.
- Defecto abierto: **CRM-030** (minor), sin fix, ver la entrada del implementador.
- **R2 sin cambios y sigue siendo el riesgo dominante**: el certificado vence el **2026-10-19** y
  Joaquin decidio explicitamente no renovarlo ahora. Cuando venza, el push se cae con el sitio.

### 2026-10-15 - implementador (CRM-028: Web Push para los chats derivados a mano)

- **Disparador**: un contacto en `DerivadoManual` que vuelve a escribir se guardaba, no recibía respuesta automática (correcto, lo lleva una persona) y quedaba "no leído" en `/Chats`. Nadie se enteraba hasta abrir el CRM — en los chats más caros del embudo, donde alguien ya se comprometió a seguir la conversación a mano.
- **Alcance implementado**: Web Push real (notificación del sistema operativo, sirve con el CRM cerrado) **+** la campanita in-app con el mismo texto, a los usuarios con rol `SuperUsuario`. Anti-ruido: **un aviso por chat hasta que alguien lo lea**. Activación explícita por dispositivo, con los 4 estados visibles. **Primera vez que el estudio hace Web Push** → patrón nuevo **PAT-069** en el catálogo.
- **El punto de enganche fue la decisión técnica central**: el disparo va en `BotFlowService.HandleIncomingAsync` —el punto único de entrada del mensaje entrante— con el estado del embudo capturado **antes** de procesar (`eraDerivadoManual`). Un `DerivadoManual` que escribe sale hoy por 3 caminos distintos, cada uno con su propio `return`: multimedia en la rama `loAtiendeUnaPersona`, texto con el bot pausado, y el flujo normal si la pausa de 48hs ya venció. Enganchar en las ramas garantizaba olvidarse de una, hoy o el día que alguien agregue la cuarta.
- **Anti-ruido sin campo nuevo de lectura**: `Contacto.FechaUltimoAvisoDerivado` (nueva) contra `FechaUltimaLecturaAgente`, que ya escriben los 6 puntos de `/Chats` donde un asesor toca el chat. La regla vive en la entidad (`EsperaAvisoDeChatDerivado`, CRM-001). **No se tocó** la semántica de `FechaUltimaLecturaAgente` ni de `MarcadoNoLeidoManual`: ese flag es marca de gestión del asesor, no una lectura, y mezclarlo haría que marcar un chat como no leído dispare un push nuevo.
- **Unicidad sobre columna generada (LP-057)**: el único de `PushSubscription.EndpointHash` va sobre `EndpointHashVivo`, no sobre la columna real. El modo de falla que evita es específico y difícil de reproducir: la entidad tiene query filter de soft-delete, el navegador devuelve **el mismo endpoint** al resuscribirse, así que una fila dada de baja esconde el SELECT, el INSERT muere contra el único, y el botón "Activar avisos" falla para siempre **en ese dispositivo y solo en ése**. `SuscribirAsync` además revive la fila con `IgnoreQueryFilters()` en vez de insertar otra. El hash existe porque el endpoint es varchar(500) y 2000 bytes utf8mb4 no entran en una clave de InnoDB.
- **Riesgo R1 resuelto y verificado**: el `unregister()` **global** de service workers del layout (puesto para barrer un `sw.js` heredado de VirtualWallet que cacheaba un CRM en vivo) pasa a **selectivo** por `scriptURL`. Si quedaba global, el SW nuevo se suicidaba en cada carga de página sin que nada avisara. Probado con 3 cargas seguidas: sobrevive. El `push-sw.js` nuevo no tiene ni un `fetch` ni un `caches`, por el mismo incidente.
- **Hallazgo sobre la librería**: `Lib.Net.Http.WebPush` 3.3.1 **no trae ningún `VapidHelper`** — solo sabe enviar, no generar claves. El par VAPID se generó aparte con un `ECDsa` P-256 (pública = punto sin comprimir `0x04||X||Y` en base64url, privada = el escalar `D`). Queda anotado para no volver a buscarlo en la librería.
- **Best-effort, regla CRM-020**: todo el envío va envuelto en 2 niveles de `try`, y `EnviarAsync` abre **su propio scope de `DbContext`** (riesgo R4) para no commitear por el costado los cambios del contacto que el webhook tiene a medio aplicar. Una falla de push no puede hacer perder el mensaje que el contacto sí mandó. `404`/`410` = suscripción muerta y se da de baja sola; el resto de los errores solo cuenta `FallosConsecutivos`.
- **Migración**: `AddPushSubscriptions`, **aditiva** (tabla nueva + 1 columna en `Contactos`), **aplicada solo en dev**. Producción sin tocar.
- **Secreto**: `Push:PublicKey` y `Push:Subject` en el `appsettings.json` commiteado; `Push:PrivateKey` **solo** en user-secrets de dev. En producción va en `appsettings.Secrets.json` o como variable de entorno `Push__PrivateKey`. Si el par rota, todas las suscripciones vigentes mueren y hay que reactivar dispositivo por dispositivo.
- **Verificado**: build Release **0 errores** (21 advertencias preexistentes). End-to-end real en dev: suscripción contra FCM, **push efectivamente entregado y mostrado por el service worker**, anti-ruido (4 mensajes → 1 aviso), re-armado tras la lectura, etiqueta de multimedia, y baja/re-alta del dispositivo. Datos de prueba borrados.
- **No probado**: la rama de revivir una fila soft-deleted (Chrome emitió un endpoint nuevo tras el `unsubscribe()`, así que se insertó otra fila), iOS (R3: necesita el CRM en la pantalla de inicio y un iPhone real), Firefox y Safari.
- **Riesgo abierto y con fecha**: **R2 — el certificado Let's Encrypt de `portal.olvidata.com.ar` vence el 2026-10-19 y no renueva solo**. Web Push exige HTTPS válido: si el cert vence, el push se cae junto con el sitio. Es anterior a este CR pero ahora tiene una consecuencia más.
- **Pendiente**: QA funcional, migración en producción, deploy y commit — todo a la espera de autorización explícita de Joaquín.

### 2026-10-15 - orquestador - webhook de Instagram: el endpoint esta OK, el bloqueo es el estado de la app de Meta
- Etapa: verificacion puntual a pedido (no es una etapa del flujo). Meta rechazaba la configuracion con
  "The callback URL or verify token couldn't be validated" sobre `https://portal.olvidata.com.ar/webhook/instagram`.
- **Resultado: el endpoint de produccion esta correcto y no hay nada que arreglar en el codigo.** Medido desde
  fuera, replicando exactamente el GET de verificacion de Meta:
  - token correcto -> `200` devolviendo **el challenge exacto** en el cuerpo (`hub.challenge` ecoado tal cual);
  - token incorrecto -> `403`.
  Es el comportamiento que Meta exige, con el certificado valido y la cadena completa (no hizo falta `-k`).
- **Causa real: el estado de la app de Meta, no el callback.** El propio panel lo dice arriba del formulario —
  *"To receive webhooks, your app must be in published state"*. Mientras la app siga sin publicar, el validador
  de Meta falla con ese mensaje aunque la URL responda bien. El codigo de error que acompaña (`#N/A:WBxP-...`)
  es del lado de Meta, no del sitio.
- Riesgo a vigilar, no causa de esto: el SSL de `portal.olvidata.com.ar` vence el **19/10/2026**. Es Let's Encrypt
  y renueva automatico server-side, pero Meta es estricta con la cadena: si la renovacion fallara, el webhook
  dejaria de validar y el sintoma se pareceria a este. Ver `docs/referencia/runbook-urgencias-viaje.md` seccion 2.
- No se toco nada: ni codigo, ni configuracion, ni la app de Meta. Solo lectura.
- Impacto en capas: ninguno.

- **2026-08-01 a 2026-08-14** (22 entradas del implementador: campañas de ski/mercados, envío de mensajes y PDF desde Chats, máquina de estados de EstadoEmbudo, cierre de CRM-002/003/005, race conditions de no-leído y de campañas, multimedia entrante, mitigación de la ventana de 24hs) → `historial/trazabilidad-2026-08-2.md`

### 1. A quien apuntar y que ofrecer primero — segmentacion por perfil, no solo por rubro

Hoy la segmentacion de outbound es 100% por rubro (via `CampanaOutboundIndustria`/`ClaveRubro`) y el pitch es siempre "sistema a medida para tu rubro" (`olv_frio_v13` + `NarrativaByType`). Eso alcanza para vender Build, pero no decide cuando conviene abrir con Landing o con AI Agents/Chatbots. Propuesta de matriz (a validar en Analisis):

| Perfil detectado | Señal disponible | Oferta primaria a abrir | Oferta secundaria/upsell despues |
|---|---|---|---|
| Sin web / sin presencia digital | Campo `website` vacio en Google Places (Place Details) | **Landing** — 2D como entrada, 3D si el rubro es visual (real estate, showroom, indumentaria) | Build, una vez que ya confia |
| Operativo transaccional (indumentaria, alimentos/bebidas, agro, servicios urbanos) | Rubro + ya tiene web/redes basicas | **Build** (gestion, sin cambios respecto de hoy) | Chatbot si vende mucho por WhatsApp directo |
| Back-office intensivo (contadores/estudios, administracion real estate/consorcios, salud administrativo, comercio multirubro con mucha facturacion) | Rubro | **AI Agents** (automatizar reportes/conciliacion/carga de planillas) | Build si ademas no tiene sistema propio |
| Alto volumen de consultas entrantes de clientes (real estate/alquileres, salud/turnos, gastronomia, indumentaria) | Rubro + volumen de reseñas/actividad en Maps | **Chatbots** (usando de prueba social el propio bot de ventas de Olvidata, ya en vivo) | Build/AI Agents como combo |

La señal "tiene web o no" es la mas barata y mas accionable para decidir Landing vs. el resto — a confirmar en Arquitectura si `GoogleMapsService` ya trae/persiste el campo `website` del Place Details de hoy o si hay que sumarlo (con su costo asociado por campo extra en la API de Places).

### 2. Gancho y mensaje de primer contacto (borrador — pasar por `olvidata-marketing` antes de shippear)

Mismo formato y tono que `olv_frio_v13` (pain-first, primera persona de Joaquin, botones "Si, contame mas"/"No me interesa"), pero con el gancho segun el perfil de arriba en vez de ir siempre a gestion:

- **Sin web (Landing):** "Hola! Vi tu negocio en Maps y no encontre una pagina propia — hoy quien te busca por ahi se termina yendo a otro que si aparece. Soy Joaquin, de Olvidata Soft. Armamos paginas para negocios como el tuyo, con presencia real online en pocos dias. Te sirve verla?"
- **Back-office intensivo (AI Agents):** "Hola! Vi tu negocio y pense: seguro se van horas armando reportes o cargando planillas a mano. Soy Joaquin, de Olvidata Soft. Armamos agentes de IA que hacen ese trabajo administrativo solos, para que tu equipo no lo pierda. Te sirve?"
- **Alto volumen de consultas (Chatbots):** "Hola! Vi tu negocio y pense: seguro se pierden consultas por WhatsApp fuera de horario o mientras atendes en el local. Soy Joaquin, de Olvidata Soft. Armamos un asistente que contesta y filtra esas consultas solo, 24/7. Te sirve?"
- **Operativo transaccional (Build):** sin cambios — el pitch actual ya funciona.

### 3. Cambios concretos identificados en el CRM/bot (para que Analisis/Diseño/Arquitectura los tomen, no implementados)

- **El punto de cambio real ya no es el arbol de menus fijos, es la conversacion agentica.** Desde el 2026-09-14 el LLM (`ConversacionIaService.cs`) reemplazo el camino principal; el arbol (`BotFlowService.cs`, `AwaitingCategory`/`Questions`) quedo de fallback. Por eso el vocabulario a extender vive en `ConversacionIaService.CategoriasValidas` (hoy 6 claves: `rent`/`rent_other`/`build`/`merge`/`landing`/`other`) y en el system prompt generado (§3.4 de `plan-llm-conversacional-bot.md`), no en el menu viejo de `BotFlowService`.
- **Categorias nuevas a evaluar en Analisis:** `ai_agents` (automatizacion/back-office) y `chatbot` (ventas/consultas automaticas) como claves nuevas de `Contacto.Categoria`, mas separar `landing` en 2D/3D si conviene que el LLM lo distinga solo o si alcanza con preguntarlo (la categoria `landing` ya tiene su propio cuestionario de 3 preguntas en `BotFlowService.Questions["landing"]`, habria que revisar si ahi mismo se agrega la pregunta 2D/3D o si el LLM ya lo puede inferir del rubro).
- **Bug/inconsistencia encontrada de paso (no corregida, solo flagged):** `merge` sigue siendo una categoria valida en `ConversacionIaService.CategoriasValidas` y en `BotFlowService.CategoryNames` pese a que el negocio dio de baja Merge el 2026-09-13 — el bot podria seguir clasificando u ofreciendo Merge a un prospecto. Sacarlo del vocabulario es parte de este mismo trabajo de Analisis, no un tema aparte.
- **Señal de "tiene web o no"**: si `GoogleMapsService`/Place Details no persiste hoy el campo `website`, es un dato nuevo a capturar en `Contacto` — a dimensionar en Arquitectura (incluye costo: Place Details cobra por campo solicitado).
- **Plantilla outbound**: `olv_frio_v13` y `RubroHelpers.NarrativaByType`/`Plural` estan anclados 100% a rubro → dolor de gestion. Ofrecer distinto segun perfil implica una dimension de seleccion de plantilla/narrativa nueva (no solo rubro) — cambio de alcance real, no un ajuste de texto.
- **Documentacion a actualizar en el mismo trabajo** (ya señalado como pendiente en la entrada del 2026-09-14 de mas arriba): `arbol-comunicacion-bot.md` y `logica-negocio-bot.md` siguen describiendo el arbol como si fuera el camino principal — hay que sumarles el flujo de la IA con las categorias nuevas al lado.

**Proximo paso:** que `analista-funcional` tome este brief como entrada de Discovery para `crm-olvidata` (o un sub-alcance nuevo dentro del mismo proyecto) y lo cierre en `1-analista-funcional.md` antes de pasar a Diseño.

## 2026-09-14 (7) — olvidata-ceo: precios de AI Agents y Chatbots CONFIRMADOS por Joaquin como promo de entrada

**Nota de puntero, no de implementacion** (decision de negocio/pricing, no de codigo del CRM — la fuente de verdad completa vive en `.claude/agents/olvidata-ceo.md`, seccion "Planes AI Agents y Chatbots", y en la memoria `olvidata-cuatro-frentes-2026-09-13.md`). Se deja constancia aca porque el caso de uso que motiva el pricing de Chatbots es el bot de ventas de este mismo proyecto (`ConversacionIaService`, ya en vivo).

- Joaquin confirmo el 2026-09-14 la propuesta de `olvidata-ceo` del mismo dia para AI Agents y Chatbots, con una condicion: son **PROMO de entrada, validos solo para clientes que cierren hasta el 2026-12-31**. Desde 2027-01-01 rige una lista post-promo, todavia sin confirmar.
- AI Agents: setup USD 300-1.500 segun complejidad (Basico/Intermedio/Avanzado) + recurrente USD 400/650/1.000 por año. Chatbots: setup USD 400-700 + recurrente USD 350/550/900 por año segun volumen de conversaciones (Starter/Pro/Scale).
- El costo real medido del bot propio (USD 0,006-0,045 por conversacion con Opus 5, ver `plan-llm-conversacional-bot.md` §5.5) es el dato de costo interno usado para justificar el margen de estos dos frentes — queda como referencia de calibracion para cuando se venda esto a terceros via `Olvidata Agentes Multi-rubro`.
- Renovacion: el cliente que cierra con la promo mantiene ese precio en renovaciones sucesivas (grandfathereado), no pasa a lista automaticamente.
- Sin impacto en codigo ni en el alcance tecnico definido en la entrada anterior (2026-09-14 (5)) — ese brief de segmentacion del bot de prospeccion sigue en pie tal cual, sin cambios por esta confirmacion de precio.

## 2026-10-15 — Canal nuevo: el bot atiende los DM de Instagram (plan completo, fases 1-5, en producción apagado→encendido)

- Pedido del cliente: *"implementar `plan-instagram-dm-bot.md`"*. El plan estaba escrito ese mismo día y sin una línea de código. Fases 1 a 5 implementadas en una pasada; la fase 0 (setup en Meta) la hizo Joaquín en paralelo y la fase 6 (QA funcional con credenciales) sigue abierta.
- **Las 5 definiciones pendientes del §13 se resolvieron antes de codificar** (sin eso, 3 de ellas cambiaban el código): Instagram Login para la autenticación (corregida sobre la marcha, ver abajo), `CanalOrigen.InstagramOrganico = 5` como valor nuevo (no reutilizar `Referido` ni `AdsPagos`: contar un DM orgánico como conversión de ads diluye el 41% de ads pagos), Human Agent detrás de una perilla apagada, **la IA califica igual que en WhatsApp** (no es un puente para conseguir el teléfono), y modo sombra sí.
- **La decisión de diseño que define el canal**: identidad por canal en la MISMA fila de `Contacto`, no una entidad `ContactoCanal` 1:N. `Telefono` pasa a nullable y aparecen `CanalMensajeria`, `IgScopedId` (único) e `IgUsername` (display, nunca clave). La entidad 1:N es más limpia en el papel y toca todas las queries de 3 controllers, el pipeline de Maps y los 4 schedulers: con un canal y medio de tráfico no se justifica.
- **`IMensajeriaSender`** es la pieza que hace que esto sea "un canal más de entrada y salida" y no un bot nuevo: `BotFlowService` llamaba 17 veces a `_wa.Send*(contacto.Telefono, ...)`, y con un `if` por canal eran 17 `if`. Ahora el llamador pasa el `Contacto` y no decide nada. Los avisos al admin siguen saliendo **siempre** por WhatsApp: el admin es un teléfono, no un contacto del CRM.
- **El barrido de `Telefono` nullable lo dirigió el compilador**, no un grep: con nullable reference types activado, los 37 sitios que lo leían aparecieron como warnings. Cubiertos los 3 tipos de sitio de LP-002: búsqueda/filtro (`/Chats`, `/Contactos`, `/Clientes`, `/Clientes/Nuevo` ahora buscan también por `@usuario`), listado (ícono de canal por fila) y ficha (identidad del canal + link al perfil de IG).
- **Red de seguridad del §4.2, por diseño y no por casualidad**: las 4 queries de elegibilidad del outbound (lote frío, follow-up, reenganche, recuperación) filtran `CanalMensajeria == WhatsApp && Telefono != null` **antes** del corte de cupo (CRM-024), el aviso de renovación saltea con aviso ruidoso al admin, y `MensajeriaSender.EnviarPlantillaAsync` tira `NotSupportedException` + mail al admin si algo intenta mandarle una plantilla a un contacto de Instagram. Hasta hoy el filtro por `EstadoEmbudo` alcanzaba **por casualidad** (un contacto de IG nace `Respondido`, no `Pendiente`).
- **La ventana de respuesta pasa a ser por canal** (`MensajeriaHelpers.HorasVentana` / `UmbralAvisoVentanaHoras`): el literal "24" estaba escrito en 5 lugares. En Instagram el umbral de aviso es más temprano (6hs contra 3hs) porque allá una ventana perdida **no se reabre con nada**: no hay plantillas. El botón "Reactivar conversación" se oculta y se reemplaza por "Seguir por WhatsApp" si el contacto dejó su número.

### Corrección de la vía de autenticación, con la fase 0 ya empezada

- El §13.1 se había definido **Facebook Login** (token de Página) y se implementó así. Al hacer la fase 0, Joaquín dio de alta una **app de Instagram** con su propio id y secret y generó un token `IGAA` — que es **Instagram Login**, la vía que el plan recomendaba. Verificado contra las 2 APIs antes de tocar nada: `graph.instagram.com/me` lo acepta (`user_id 17841456625525075`, `olvidata.soft`, BUSINESS) y `graph.facebook.com` lo rechaza con error 190 *"Cannot parse access token"*.
- Cambió: host `graph.instagram.com`, envío a `me/messages` (se usa `me` y no el `IgUserId` a propósito: la cuenta la determina el token, así que un id mal cargado no puede romper el envío), se cae `PageId`, el `AppSecret` de la firma pasa a ser **el de la app de Instagram**, y el webhook se suscribe desde el producto Instagram sin el `POST /{page-id}/subscribed_apps`.
- **Consecuencia que cambia el alcance**: la Attachment Upload API es un endpoint de Messenger/Página y por esta vía no existe. La alternativa documentada —adjunto por URL pública— no aplica: el PDF vive como bytes en la base y su endpoint está detrás de `[Authorize]`. **Por Instagram se manda texto y quick replies, no archivos.** `/Chats` corta el upload antes de guardar el PDF (no se guarda un `ArchivoPdf` que nunca salió: esa columna significa "presupuesto enviado" y la lee `MensajeriaHelpers.TuvoPresupuesto`) y dice "mandáselo por WhatsApp al +…". El envío de imágenes del mismo día queda solo en WhatsApp por el mismo motivo.
- **No verificado**: si la edge de upload existe por esta vía. Un GET sobre ella devuelve el mismo error que sobre `/me/messages`, que sí existe para POST, así que el sondeo no distingue. La decisión se apoya en la documentación y en no tener URL pública.

### Prueba real de la mitad de ingreso, sin Meta y sin deployar

- Migraciones aplicadas a `olvidatacrm_dev`, app levantada en local y **19 chequeos contra el webhook con firma HMAC real: 19/19 OK**. Verificación GET (200 + challenge / 403 con token erróneo), firma inválida → 403 sin escribir, DM real → contacto con `CanalMensajeria=2`, `CanalOrigen=5`, `Telefono=NULL`, dedup por `mid`, `is_echo` descartado, evento de la propia cuenta descartado, reacción que no llega al LLM, evento vacío descartado. Detalle en `6-qa.md`.
- **2 defectos encontrados por esa prueba**, los dos corregidos — ver `6-qa.md` (CRM-020 reincidente y CRM-027).

### Deploy a producción

- Backup de la base primero (`/db/db_a7251f_olvidat.sql`), después migraciones, después código. Ese orden importa: el código nuevo contra el esquema viejo rompe cualquier query que toque las columnas nuevas, mientras que el esquema nuevo contra el código viejo es inocuo (columnas extra + ningún `Telefono` en null todavía).
- **Verificado en producción**: los **10.235 contactos** quedaron todos en `CanalMensajeria = 1`. El `defaultValue` que generó EF era 0 — que no es un valor del enum — y habría apagado el outbound entero en silencio el día del deploy (regla **CRM-026** nueva en el catálogo 32, reincidente el mismo día con signo invertido en la segunda migración).
- `UX_Contactos_IgScopedId_Vivo` sobre columna generada, no un único global (**LP-057**): `Contacto` tiene query filter de soft-delete, y con un único sobre la tabla completa dar de baja un contacto de Instagram y que esa persona vuelva a escribir reventaba el `SaveChanges` del webhook y se perdía el mensaje. **El hueco equivalente del único preexistente de `Telefono` queda abierto**: arreglarlo exige dropear y recrear un índice en producción y merece su propia migración.
- 2 publicaciones: la primera con el canal apagado, la segunda para pasar la lectura de la config a `IOptionsMonitor` (ver abajo). El resumen de MSDeploy ("1 archivo actualizado") engañaba; la verificación real fue `/webhook/instagram` pasando de **404 a 403**.
- **WhatsApp intacto**: la validación de firma que se agregó a su webhook queda inerte mientras `Olvidata_WhatsApp:AppSecret` esté vacío (lo está en producción). Era el riesgo de regresión más concreto del deploy. Hacerla obligatoria de golpe habría dejado de recibir mensajes reales hasta cargar el secreto.

### Dos cosas del entorno que se descubrieron operando, no leyendo

- **El `user-secrets` de desarrollo tiene las credenciales de Meta de PRODUCCIÓN.** Al levantar la app en local para la prueba, el `AvisosRenovacionSchedulerService` mandó un template real (`olv_renovacion_notificacion_v3`) al `5490000770005` de los datos sembrados. Nadie lo recibió (número inexistente) pero Meta aceptó la llamada. El guard quedó marcado, así que esa notificación no se repite; el recordatorio del mismo cliente vence el 18/10 y volvería a salir en cada corrida local. **Error de criterio**: se asumió que "base de desarrollo" implicaba credenciales de desarrollo, sin verificar el `user-secrets` antes de arrancar. La prueba siguiente se hizo apagando los switches del propio sistema en la base de dev (`AvisoRenovacionHabilitado`, IA, outbound, Maps, cobro) y restaurándolos después, sin tocar `user-secrets`.
- **`appsettings.Secrets.json` le gana a las variables de entorno**, al revés de lo que afirma su propio comentario en `Program.cs`: se agrega *después* de `CreateBuilder`, así que queda último en la cadena. Lo que esté en ese archivo no se puede sobreescribir con una variable de entorno — y por eso el intento de neutralizar la IA en local con `Anthropic__ApiKey=""` no tuvo efecto. **El comentario de `Program.cs` sigue siendo incorrecto: corregirlo es deuda abierta.**

### Modo sombra por canal (no estaba en el plan como código)

- El plan pedía sombra primero para Instagram (§8.4), pero `ConversacionIaModoSombra` es **global**: con la IA ya en vivo para WhatsApp, la única forma de mirar Instagram en sombra era poner todo en sombra — apagar el canal que funciona para estrenar el que no. Se agregó `ConfiguracionOutbound.ConversacionIaModoSombraInstagram` (default `true`, migración `AddModoSombraIaInstagram`), `EnSombraParaCanal(canal)` en la entidad, su toggle en `/Bot` y una fila de estado "IA en Instagram". El OR es deliberado: el flag general sigue siendo el maestro.
- **El cliente decidió salir de sombra sin esperar las 20-30 conversaciones** y encendió el canal el mismo día. Riesgo nombrado y aceptado: el tope diario de IA (USD 2) es **compartido con WhatsApp**, así que una ráfaga de DM basura se lo come y WhatsApp también cae al árbol ese día (~68 turnos/día entre los dos canales, a USD 0,026 por turno). **Separar el tope por canal quedó ofrecido y sin decidir.**

### Estado al cierre

- En producción: canal abierto (`Features:InstagramDm = true`), IA en vivo para los dos canales (`habilitada=1 pausada=0 sombraGeneral=0 sombraInstagram=0`), webhook validado contra Meta (GET con token → 200 + challenge; firma inválida → 403; firma válida → 200; 0 contactos de Instagram creados por las pruebas).
- Gasto de IA al cierre: USD 0,57 de 15 en el mes, 0,22 de 2 en el día.
- `appsettings.Secrets.json` del servidor lo cargó el agente por FTPS preservando `Anthropic:ApiKey` (backup previo + `json.dumps` para que no pueda quedar mal formado: un JSON roto ahí tira la app al arrancar), verificado releyéndolo. El archivo tenía solo el bloque de Anthropic: el de Instagram nunca se había subido, y **eso era la causa real** de que Meta no validara el webhook.
- **Sin commitear.** El working tree tiene este cambio y el envío de imágenes por WhatsApp del mismo día mezclados en los mismos archivos, y los dos están en producción. Decisión del cliente pendiente.
- **Secretos expuestos en el hilo de trabajo** (app secret y token de Instagram): regenerarlos es pendiente del cliente.

### Pendientes

1. **Fase 6 — QA funcional con credenciales**: todo el lado de ENVÍO (texto, quick replies, perfil, descarga de adjuntos, ventana), que la prueba local no pudo cubrir. Ver `6-qa.md`.
2. **App Review de `instagram_manage_messages`** y suscripción de los campos del webhook (`messages`, `messaging_postbacks`, `messaging_reactions`, `messaging_referrals`, `messaging_seen` — **no** `message_echoes`). Sin la suscripción el webhook queda validado y no llega ningún evento.
3. **Confirmar el `entry[].id` del primer DM real**: Instagram Login expone 2 formas del id de la cuenta (`user_id` 17841… y uno scopeado a la app, 27077…) y no son el mismo número. La guarda anti-eco ya compara contra `entry[].id` del propio payload además del configurado, justamente para no depender de cuál sea.
4. **Confirmar el vencimiento real del token** y corregir `TokenVenceEl` (hoy estimado al 14/12), que es lo que alimenta el aviso de la card de `/Bot`.
5. Merge Instagram ↔ WhatsApp sigue **manual** (§5.4): lo implementado es el aviso de posible duplicado cuando la persona da por DM un número ya cargado — no se escribe y se notifica.
6. Deuda abierta: el único de `Telefono` sin el patrón `_Vivo`, el comentario de precedencia de `Program.cs`, y el `Results.Forbid()` del GET de `/webhook/whatsapp` (se dejó como está: funciona en producción y no se toca por cosmética).

### Hueco de documentación detectado

Esta entrada cierra el canal de Instagram, pero `trazabilidad.md` **no tiene entradas entre el 2026-09-15 y el 2026-10-14**. Quedó sin registrar el trabajo de octubre que el agente no hizo y no puede reconstruir sin inventar: avisos de renovación por anticipación (`4d0901f`), un contacto con varios sistemas (`09c4814`), el perfil de Web Deploy invocable por línea de comandos (`9e27277`), la reescritura de las 4 plantillas de primer contacto (`aca2184`), el ruteo y la sincronización de plantillas con Meta (`467571e`) y el envío de imágenes desde `/Chats` (sin commitear). **Se puede reconstruir desde los commits si el cliente lo pide.**

## Historial de ajustes

### Bloques archivados (2026-10-15)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 1 bloques (2026-09-14 a 2026-09-14) → [`trazabilidad-2026-09-7.md`](historial/trazabilidad-2026-09-7.md)


### Bloques archivados (2026-10-15)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 1 bloques (2026-09-14 a 2026-09-14) → [`trazabilidad-2026-09-6.md`](historial/trazabilidad-2026-09-6.md)


### Bloques archivados (2026-10-15)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 1 bloques (2026-09-14 a 2026-09-14) → [`trazabilidad-2026-09-5.md`](historial/trazabilidad-2026-09-5.md)


### Bloques archivados (2026-10-15)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 1 bloques (2026-09-14 a 2026-09-14) → [`trazabilidad-2026-09-4.md`](historial/trazabilidad-2026-09-4.md)


### Bloques archivados (2026-10-15)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 2 bloques (2026-09-14 a 2026-09-14) → [`trazabilidad-2026-09-3.md`](historial/trazabilidad-2026-09-3.md)


### Bloques archivados (2026-10-15)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 2 bloques (2026-09-15 a 2026-09-15) → [`trazabilidad-2026-09-2.md`](historial/trazabilidad-2026-09-2.md)


### Bloques archivados (2026-10-15)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 1 bloques (2026-09-16 a 2026-09-16) → [`trazabilidad-2026-09.md`](historial/trazabilidad-2026-09.md)


### 2026-10-13 - implementador (ruteo de envios por categoria de Meta: Marketing Messages API)

- **Disparador**: comunicado de Meta del 2026-10-13. El **2027-10-13** la Cloud API deja de aceptar plantillas **MARKETING**: pasan obligatoriamente por la **Marketing Messages API** (`POST /{phone-number-id}/marketing_messages`). Utility y Authentication siguen por `/messages`. El body del request es identico en los dos endpoints — lo unico que cambia es el path. Argentina no figura en ninguna restriccion geografica de la MM API (los excluidos son Cuba, Iran, Corea del Norte, Siria, Venezuela, regiones de Ucrania; EE.UU. no recibe marketing desde abril 2025; Rusia/Bielorrusia sin optimizaciones).
- **Lo que faltaba**: `TemplateWhatsApp` no guardaba la categoria, asi que no habia por donde decidir el endpoint. Y Meta pide explicitamente mantener el mapeo nombre→categoria **al dia**, porque reclasifica despues de aprobar (LP-004, ya nos paso el 2026-10-07 con la notificacion de renovacion).
- **Cambio**: (1) enum `CategoriaMeta` + columna `TemplateWhatsApp.CategoriaMeta` (migracion `RuteoTemplatesPorCategoriaMeta`, default Marketing, `olv_renovacion%` → Utility). (2) `IRuteoTemplatesService` resuelve la categoria en cada envio y `WhatsAppClient.SendTemplateAsync` elige el path — ningun call site decide nada, a proposito: un ruteo hardcodeado al lado del envio queda mal en silencio el dia que Meta reclasifica. Si la consulta falla, degrada a Cloud API (CRM-020). (3) `ISincronizacionTemplatesMetaService` trae estado + categoria de `GET /{waba-id}/message_templates` (paginado); lo usan el boton por fila, un boton nuevo "Sincronizar con Meta" de todo el catalogo, y `TemplatesMetaSyncSchedulerService` cada 12hs. Cada reclasificacion queda logueada como **warning**. (4) Un unico metodo escribe estado y categoria desde Meta (CRM-001), compartido por el boton y el scheduler. (5) Interruptor `ConfiguracionOutbound.MarketingMessagesApiHabilitada`, en base y no en appsettings (CRM-018), editable desde /Templates: arranca **apagado** porque hasta aceptar los terminos de la MM API en Meta Business Manager el endpoint nuevo rechaza los envios — y lo que sale por ahi es todo el outbound frio. (6) `CategoriaMeta` en Alta y Edicion (REG-012) y columna nueva en el listado. (7) `TempData["WarningMessage"]` en el layout, que no existia.
- **Propagacion (LP-002), el hallazgo real del relevamiento**: 5 plantillas se mandaban por nombre **hardcodeado** y no estaban en el catalogo, asi que no tenian categoria y hubieran salido por el endpoint equivocado: `olv_nurturing_v2` (follow-up), `olv_reenganche_menu_v1`, `olv_referido_v2`, `olv_retomar_conversacion_v1` (las 4 Marketing) y `olv_notif_respuesta` (Utility). Se centralizaron en `PlantillasAutomaticas`, los 5 call sites pasan a referenciar la constante, y un seed idempotente las deja en el catalogo — con eso rutean bien, se ven en /Templates y entran en la sincronizacion. Las frias y las combo ya estaban en el catalogo porque las valida el selector de campañas y de ganchos.
- **Pendiente deliberado, fuera de este alcance**: `GetCostoMensajeriaAsync` sigue valorizando por el tipo de envio (etiqueta de `ContactoRespuesta`) y no por la categoria real del template — los avisos de renovacion se cuentan a tarifa Utility siempre. Si Meta reclasifica uno a Marketing, el gasto del mes queda **subestimado** (2,4x en Argentina). Para arreglarlo bien hace falta guardar el nombre del template en cada fila de `ContactoRespuesta`, que hoy no se guarda. LP-004 lo pide explicitamente, asi que queda anotado y no olvidado.
- **Verificado**: compila (incluidas las vistas Razor — confirmado forzando un error en `Views/Templates/Index.cshtml` y viendo que el build lo levanta). **No se probo contra Meta**: el endpoint nuevo requiere aceptar los terminos primero, y el interruptor esta apagado, asi que el comportamiento hasta que se prenda es exactamente el de antes.

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-08** — 85 bloques (2026-08-14 a 2026-08-28) → [`trazabilidad-2026-08.md`](historial/trazabilidad-2026-08.md)
- **2026-07** — 65 bloques (2026-07-17 a 2026-07-31) → [`trazabilidad-2026-07.md`](historial/trazabilidad-2026-07.md)

### Traza de corrida -- 2026-10-15 / etapa implementacion
- Reintentos: 2
- Criterios fallados: ninguno
- Reglas releidas: LP-057
- Nota: CRM-028 Web Push. 2 reintentos sin reescribir logica: (a) el using del paquete quedo antes del BOM de DependencyInjection.cs, (b) build Debug fallido 2 veces por lock del exe de la app corriendo. Hallazgo para el arranque del rol: Lib.Net.Http.WebPush 3.3.1 NO trae VapidHelper, el par VAPID se genera con ECDsa P-256 aparte. LP-057 se releyo desde la migracion AddCanalInstagramDm del propio repo, no desde el catalogo: la migracion previa es mejor fuente que la regla porque trae el SQL.


### 2026-10-15 — QA de CRM-028 (Web Push de chats derivados a mano), lote unico

- **Veredicto: NO-GO para produccion hoy.** El codigo esta sano en lo observable (19 criterios PASS,
  1 defecto minor, 0 major); lo que bloquea es el entorno: el certificado de `portal.olvidata.com.ar`
  vence el **2026-10-19** y sin HTTPS valido el push no existe, y `Push:PrivateKey` no esta cargada
  en el sitio. GO condicionado a esas 2 + el chequeo manual de R1/globo real + decision sobre CRM-029.
- **Repo del sistema intacto:** `git status --porcelain` identico al del arranque, verificado al
  cerrar. Ningun fix aplicado por QA. Datos de prueba de dev borrados (444 contactos, 7
  notificaciones, 0 suscripciones — los mismos numeros del arranque).
- **Limite de entorno que hay que anotar para las proximas corridas:** ni el MCP `playwright` ni un
  Chrome propio (lanzado dentro o fuera del sandbox, con y sin `--no-sandbox` y
  `--disable-features=NetworkServiceSandbox`) alcanzan el puerto de la app levantada por las
  herramientas: `ERR_CONNECTION_REFUSED` contra `localhost`, `127.0.0.1` y la IP de LAN, con el
  listener confirmado por `netstat` y accesible por `curl` desde el mismo contexto. Es el mismo
  sintoma que la corrida del 2026-09-14 anoto como "Playwright MCP aislado del host", pero ahora
  medido tambien contra un navegador propio: **no es el MCP, es la red del entorno.** Consecuencia:
  todo criterio que necesite un navegador real queda NO VERIFICADO, no PASS.
- **Metodo que si funciono y conviene reusar:** un **push service falso** propio (HTTP local) puesto
  como `Endpoint` de la suscripcion. Recibe el sobre real que emite `PushNotificationService` —se
  puede inspeccionar el header VAPID, el `Content-Encoding`, el TTL y el tamanio— y devuelve a
  voluntad 201/404/410/500/conexion rechazada. Con eso se probaron los 5 modos de falla del
  best-effort del webhook sin depender de FCM ni de un navegador.
- **Se cerro un hueco que el Implementador declaro abierto:** la rama de revivir una fila
  soft-deleted (`IgnoreQueryFilters` de `SuscribirAsync`, regla LP-057) quedo ejercitada y pasa.
  Chrome emite un endpoint nuevo tras el `unsubscribe()`, por eso el Implementador no pudo llegar;
  con el endpoint controlado por la prueba se reproduce el caso real (fila dada de baja por un 410 y
  el navegador conservando su suscripcion) y la fila se revive en su lugar, sin duplicar.
- **Defecto nuevo: CRM-029 (minor), catalogado y con parte emitido, sin fix.** El anti-ruido "un
  aviso por chat hasta que alguien lo lea" se degrada a "un aviso por mensaje" cuando la pestania del
  chat queda abierta: `Chats/HiloParcial` estampa `FechaUltimaLecturaAgente` en cada tick que trae
  mensajes nuevos, y eso re-arma el guard justo antes del mensaje siguiente. La leccion general vale
  para cualquier guard futuro: antes de reusar un campo existente como estado de un guard, listar
  todos los puntos que lo escriben y preguntarse si alguno lo escribe como **efecto del mismo evento**
  que el guard quiere limitar.
- **Ultima validacion de reglas cross-proyecto movida a 2026-10-15.** LP-057 y CRM-025 ejecutadas
  retroactivamente (PASS); CRM-026 y CRM-027 verificadas como no aplicables a esta superficie.
  PAT-069 validado salvo la ultima milla.

### Traza de corrida -- 2026-10-15 / etapa qa (lote 1 de 1)
- Reintentos: 4
- Criterios fallados: ninguno del sistema. Los 4 reintentos son del arnes de prueba, no del CRM.
- Reglas releidas: LP-057, CRM-020, CRM-027
- Nota: los 4 reintentos valen como dato de arranque del rol. (a) El login se probo contra
  `/Identity/Account/Login` (Razor Pages) y este CRM usa `/Account/Login` con un
  `AccountController` propio y campos `Email`/`Password`/`EsPwa` sin prefijo `Input.` — conviene
  mirar `Views/Account/Login.cshtml` antes de escribir el helper de login. (b) El primer intento fue
  por HTTP y la app redirige a HTTPS: hay que levantarla con `https://localhost:7201` y `verify=False`.
  (c) 3 intentos perdidos peleando con el aislamiento de red del navegador antes de aceptarlo y caer
  al arnes HTTP+SQL; la proxima corrida de este proyecto deberia **probar la conectividad del
  navegador antes de planificar** y, si falla, no reintentar con otra combinacion de flags.
  (d) Dos lecturas de la BD dieron falsos negativos por carrera: el webhook responde 200 al instante
  y procesa en background, asi que con un endpoint inalcanzable en el lote el `SaveChanges` del push
  tarda ~8 s — hay que esperar el final del procesamiento, no el 200.

### Traza de corrida -- 2026-10-15 / etapa qa / lote 1
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna


### 2026-10-16 — QA: re-verificacion de CRM-029 (fix fb45699)

- **CRM-029 cerrado.** El criterio lo declaro QA, no el Implementador, y se midio en contexto nuevo
  con el criterio de vuelta en FAIL: pestania de detalle abierta en background + 3 mensajes seguidos
  → **1** aviso (la lectura comun se mueve en cada tick del polling, el aviso no se mueve), y despues
  de `GET /Chats/Detail` el mensaje siguiente **si** avisa. Antes del fix: 3 mensajes, 3 avisos.
- **Veredicto: GO para subir en lo que depende del codigo.** Certificado del 19/10 y privada VAPID
  quedan fuera: decision del owner y tarea del coordinador en el deploy.
- **Defecto nuevo CRM-030 (minor), parte emitido, sin fix.** El argumento del Implementador sobre los
  3 estampados de `Descartado` se chequeo y es **correcto en la direccion que se temia**: ninguno
  escribe el campo nuevo, asi que no pueden re-armar el guard de mentira. Falla en la vuelta:
  `ContactosController.EstadosManualesPermitidos` es `Enum.GetValues<EstadoEmbudo>()`, o sea que
  **todos** los estados son asignables a mano, y la secuencia avisado → Descartado → DerivadoManual a
  mano deja el guard con el aviso viejo puesto y 0 avisos para el mensaje siguiente. Degrada sin
  perder nada (el chat sigue visible en la bandeja de no leidos). La leccion generalizable que quedo
  en el catalogo: **un guard de "avisar una sola vez" tiene dos entradas** —la marca de que ya se
  aviso y la senal que la levanta— y revisar solo la senal deja la marca pegada; lo barato es
  resetear la marca cuando la entidad sale del estado que habilita el aviso.
- **Limite nuevo que conviene anotar para el arranque del rol:** los 3 puntos de lectura deliberada
  que son envios (`EnviarMensaje`, `EnviarPresupuestoPdf`, `EnviarImagen`) **no son ejecutables** en
  un arnes de QA: estampan recien despues de un envio exitoso a Meta y la URL de la Graph API esta
  hardcodeada en `WhatsAppClient`, asi que no se puede sustituir por un doble local ni hay
  destinatario seguro. Se cubrieron con un invariante mecanico (una sola escritura directa de
  `FechaUltimaLecturaAgente` en `ChatsController`, el tick; las otras 4 por
  `RegistrarLecturaDeliberada`) y se declararon como no ejecutados, no como PASS. Si alguna vez se
  quiere poder probarlos, lo que habilita eso es hacer configurable la base URL de la Graph API.
- **Leccion de metodo propia:** 2 lecturas intermedias dieron falso negativo por mi propio flood (12
  mensajes al mismo contacto en 2 minutos dispararon el corte anti-loop, y un `MarcarTodosLeidos`
  masivo toco un contacto de otra prueba). Hay que usar **un contacto nuevo por escenario** y no
  reciclar, y no correr acciones masivas entre dos mediciones de escenarios distintos.

### Traza de corrida -- 2026-10-16 / etapa qa (re-verificacion CRM-029)
- Reintentos: 2
- Criterios fallados: ninguno del criterio de cierre. CRM-029 PASS en las 2 mitades.
- Reglas releidas: CRM-029 (el criterio de re-verificacion que habia escrito), CRM-020
- Nota: los 2 reintentos son del arnes. (a) El helper de "no leido" uso un parametro de filtro
  inventado (`soloNoLeidos`) y `ListaParcial` devolvia todo: el filtro real es
  `Interaccion=noLeidos` y vive en `ChatFiltrosViewModel.Interaccion`. (b) Contaminacion cruzada por
  reciclar contactos entre escenarios y por correr un `MarcarTodosLeidos` masivo en el medio — se
  re-midio sobre contactos nuevos. Las 2 son del tipo "el arnes miente antes que el sistema": ante un
  resultado inesperado, chequear primero el arnes contra la base.

### Traza de corrida -- 2026-10-15 / etapa qa / lote 1
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna


### Traza de corrida -- 2026-10-15 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna


### Traza de corrida -- 2026-10-16 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna


### Traza de corrida -- 2026-10-16 / etapa qa / lote 1
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna


### Traza de corrida -- 2026-10-16 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna


### Traza de corrida -- 2026-10-16 / etapa qa / lote 2
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna

