<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/1-analista-funcional.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 1-analista-funcional - M03 (19 bloques archivados)

- Casos de uso M3b
- Reglas funcionales M3b
- Permisos M3b
- Criterios de aceptacion M3b
- Riesgos M3b
- Banderas tempranas M3b
- Preguntas abiertas M3b (hipótesis)
- Reutilizacion relevada M3b
- Clasificacion de perfil de cliente M3b
- Casos de uso M3
- Reglas funcionales M3
- Permisos M3
- Criterios de aceptacion M3
- Supuestos M3
- Riesgos M3
- Banderas tempranas M3
- Preguntas M3 — respuestas de Joaquín (2026-09-14)
- Reutilizacion relevada M3
- Clasificacion de perfil de cliente M3

---

### Casos de uso M3b
| CU | Actor | Descripción |
|---|---|---|
| CU-M3b-01 | Autor de la tarea | Envía un mensaje de seguimiento sobre una tarea terminada |
| CU-M3b-02 | Autor | Sigue en vivo la respuesta del nuevo turno |
| CU-M3b-03 | Miembro con visibilidad | Lee la conversación completa en el detalle |
| CU-M3b-04 | Autor | Copia una respuesta |
| CU-M3b-05 | Miembro | Ubica en el listado las tareas con actividad reciente |
### Reglas funcionales M3b
- **RF-M3b-01** Se puede enviar un seguimiento solo si la tarea está `Completada` o `Fallida` (ver P3); nunca `Pendiente`, `EnCurso`, `EsperandoAprobacion` o `Cancelada`.
- **RF-M3b-02** Solo el autor de la tarea envía seguimientos (ver P1). El Director y el staff la leen según M2.
- **RF-M3b-03** Al enviar: se registra el mensaje como parte de la conversación, la tarea vuelve a `Pendiente`, se limpian `Resultado`/`Error` del turno anterior (quedan visibles en la conversación) y el worker la toma como cualquier tarea.
- **RF-M3b-04** El modelo recibe la conversación completa (pedido, respuestas, resultados de herramientas y seguimientos) con el mismo contexto de sistema de la tarea; con instantánea M3, se reconstruye y verifica el mismo hash.
- **RF-M3b-05** El máximo de pasos del motor se cuenta **por turno** (ver P5), no por conversación.
- **RF-M3b-06** Límites (ver P4): mensaje de hasta 10.000 caracteres; hasta 20 seguimientos por tarea; al llegar al límite se ofrece "Empezar una tarea nueva".
- **RF-M3b-07** El costo y los tokens de la tarea acumulan todos los turnos; cada turno registra su telemetría.
- **RF-M3b-08** No se permiten dos seguimientos simultáneos: un segundo envío mientras la tarea no terminó se rechaza con mensaje, sin duplicar.
- **RF-M3b-09** Cancelar una tarea con un seguimiento en curso cancela solo ese turno; la conversación anterior se conserva y la tarea queda `Cancelada` (ver P3 sobre si se puede seguir después).
- **RF-M3b-10** Aislamiento: ids de tareas ajenas o de otra organización → 404 (mismo criterio M2).
### Permisos M3b
| Acción | Autor | Director (tarea de otro) | Empleado (tarea de otro) | Staff |
|---|:---:|:---:|:---:|:---:|
| Leer conversación | ✅ | ✅ | ❌ (404) | ✅ |
| Enviar seguimiento | ✅ | ❌ (ver P1) | ❌ | ❌ |
| Cancelar turno en curso | ✅ | ✅ (como hoy) | ❌ | — |
| Copiar respuesta | ✅ | ✅ | ❌ | ✅ |
### Criterios de aceptacion M3b
- **CA-M3b-01** En una tarea Completada, el autor ve el cuadro "Seguir conversando"; al enviar, el mensaje aparece en la conversación, la tarea pasa a "En cola" y luego muestra la nueva respuesta debajo sin recargar.
- **CA-M3b-02** La nueva respuesta tiene en cuenta lo anterior: el modelo recibe pedido, respuestas previas y el seguimiento (verificable en test con modelo guionado).
- **CA-M3b-03** El seguimiento usa el mismo agente, cliente e instantánea de reglas; editar una regla después de crear la tarea no cambia el contexto del seguimiento (según P2).
- **CA-M3b-04** Mientras un turno está en curso, el cuadro está deshabilitado; un POST forzado recibe "La tarea todavía está trabajando. Esperá la respuesta para seguir."
- **CA-M3b-05** Un Director que abre la tarea de un empleado lee toda la conversación pero no ve el cuadro de seguimiento; un POST forzado → 403 (según P1).
- **CA-M3b-06** Un mensaje vacío o de más de 10.000 caracteres no se envía y muestra el límite; al llegar a 20 seguimientos se muestra "Esta conversación llegó al máximo. Empezá una tarea nueva." con acceso a Nueva tarea con el mismo agente y cliente.
- **CA-M3b-07** Tokens y costo mostrados en el detalle suman todos los turnos; el listado muestra el costo acumulado.
- **CA-M3b-08** Un turno que alcanza el máximo de pasos falla solo ese turno; la conversación previa sigue visible y (según P3) se puede reintentar con otro seguimiento.
- **CA-M3b-09** Los pasos de herramientas aparecen plegados dentro de la respuesta que los usó.
- **CA-M3b-10** "Copiar" copia el texto de la respuesta y confirma con un aviso breve.
- **CA-M3b-11** El listado de Tareas muestra "Última actividad" y cantidad de mensajes, con filtro por rango de última actividad.
- **CA-M3b-12** Una tarea M1/M2 sin instantánea admite seguimiento con el armado anterior.
- **CA-M3b-13** Tras reiniciar el portal a mitad de un turno de seguimiento, el turno se retoma sin duplicar el mensaje ni perder la conversación.
- **CA-M3b-14** Ids de tareas de otra organización en GET/POST de seguimiento → 404.
### Riesgos M3b
- R-M3b-01 (alto) **Costo creciente:** cada turno reenvía toda la conversación; con 20 seguimientos y resultados largos el costo por turno crece. Mitigación: límites, caché de la conversación previa, costo visible.
- R-M3b-02 (medio) **Reanudación:** un mensaje de seguimiento debe quedar persistido antes de encolar para que un reinicio no lo pierda ni lo duplique.
- R-M3b-03 (medio) **Bloques de thinking** de turnos anteriores deben reenviarse sin modificar (requisito de la API, ya contemplado en M1).
- R-M3b-04 (bajo) **Confusión con reglas cambiadas:** si las reglas quedan congeladas, un usuario que actualizó una regla puede esperar verla aplicada en el seguimiento (P2).
### Banderas tempranas M3b
- Migración EF: **probable, leve** (nuevo tipo de paso; última actividad y contador de seguimientos en la tarea).
- Integración externa: **no** nueva. Validación de calidad real: requiere corrida con costo (OK de Joaquín).
- Máquina de estados: **sí, leve** (re-apertura de tareas terminadas).
### Preguntas abiertas M3b (hipótesis)
- **P1 — ¿Quién puede seguir la conversación?** *A:* solo quien pidió la tarea. *B:* también el Director. *Hipótesis:* A (el costo, las preferencias personales y el hilo son del autor; el Director lee).
- **P2 — Reglas en el seguimiento.** *A:* las mismas que al crear la tarea (congeladas). *B:* se recalculan en cada seguimiento. *Hipótesis:* A, con aviso "Las reglas cambiaron desde que empezó esta conversación; para usarlas, empezá una tarea nueva" cuando corresponda.
- **P3 — ¿Sobre qué estados se puede seguir?** *A:* Completada y Fallida. *B:* también Cancelada. *Hipótesis:* A y B (una cancelada por error también se puede retomar), nunca mientras está en curso.
- **P4 — Límites.** 10.000 caracteres por mensaje y 20 seguimientos por tarea. *Hipótesis:* confirmar.
- **P5 — Máximo de pasos.** *A:* por turno (cada seguimiento tiene hasta 25 pasos). *B:* total de la conversación. *Hipótesis:* A.
- **P6 — (pendiente de M3, OBS-M3-1) Preferencias personales visibles al Director** en "Lo que el agente tuvo en cuenta" de una tarea ajena. *A:* ocultar el texto y mostrar solo "Preferencias de <nombre> (N)". *B:* dejarlo como está. *Hipótesis:* A; se implementa junto con M3b porque toca el mismo detalle de tarea.
- **P7 — Conversaciones largas.** *A:* solo límite de seguimientos (sin resumen automático) en M3b. *B:* compactar/resumir la conversación al superar cierto tamaño. *Hipótesis:* A; compactación como mejora posterior.
- **P8 — Nombre en pantalla.** *A:* "Seguir conversando". *B:* "Pedir un ajuste". *Hipótesis:* A, con placeholder "Pedile un ajuste: más corto, otro tono, agregá…".
### Reutilizacion relevada M3b
- Template propio: reconstrucción de conversación desde `PasoTarea` y reenvío de thinking (M1), SignalR + respaldo (M1), visibilidad por rol (M2), instantánea y verificación de hash (M3).
- century-21 A-04: historial de conversación de solo lectura (bot), sin iteración con modelo; referencia visual menor.
- Sin otro proyecto con conversación multi-turno contra un modelo persistida y reanudable.
### Clasificacion de perfil de cliente M3b
Producto propio (proyecto personal): presupuesto omitido.

---

**M3 — Reglas por alcance** (Discovery + Análisis, 2026-09-14). Estado: **aprobado por Joaquín el 2026-09-14** (P1–P9 respondidas; N-01/N-02 fuera de M3).

Contexto: con M2 cada organización tiene Director/Empleado, áreas y cartera de clientes, pero el motor sigue armando el prompt solo con el agente base y las instrucciones del rubro (`ProcesadorTareas.ArmarSystemPromptAsync`, reconstruido en cada ejecución). El diseño de producto aprobado (`docs/diseno-organizacion-roles-reglas.md` §3, §5, §6, decisiones 2026-09-14) define reglas de texto con alcance, modo obligatoria/por defecto y precedencia de 9 niveles.

Objetivo de negocio: que cada organización adapte el comportamiento de los agentes a su forma de trabajar (tono, prohibiciones, procedimientos, preferencias por cliente y por persona) sin tocar el núcleo de Olvidata, con control del Director sobre lo que es obligatorio y trazabilidad de qué reglas se usaron en cada tarea.

#### Alcance incluido (M3)
1. **Reglas por alcance** con ABM, activación/desactivación (sin borrar) e historial de versiones: Organización, Área, Usuario, Cliente de cartera (general), Cliente de cartera + agente base, Agente base (a nivel organización).
2. **Modo** `Obligatoria` / `Por defecto` (Organización y Área) y **tipo** `Regla` / `Procedimiento` (paso a paso).
3. **Reglas de plataforma** (Olvidata, sin organización), primeras en el contexto e imposibles de pisar.
4. **Constructor de contexto** determinístico: arma el prompt de sistema por secciones en el orden aprobado (plataforma → agente base + instrucciones → organización → área → [agente de la organización: M4] → cliente → usuario → declaración de precedencia).
5. **Nueva tarea con cliente de cartera opcional** y **vista previa de reglas efectivas** (qué reglas aplican para ese agente y ese cliente) antes de enviar.
6. **Instantánea auditable** en la tarea: reglas y versiones aplicadas + hash del contexto; visible en el detalle de la tarea.
7. **Límites de tamaño** por regla y por alcance.
8. **Efectos de bajas de M2:** área dada de baja o cliente de cartera dado de baja → sus reglas dejan de aplicarse (quedan inactivas, no se borran).

#### Alcance no incluido
- Agentes de la organización y sus instrucciones (nivel 6 de la precedencia) → **M4**; en M3 el nivel queda reservado en el orden del contexto.
- Reglas propuestas por agentes (`Origen = PropuestaAgente`) → **M7**.
- Detección automática de conflictos con IA (mejora posterior; nunca bloqueante).
- Aprobaciones y límites de gasto → **M6**. Workspace/documentos por cliente → **M5**.
- Reglas que otorguen capacidades: **una regla es texto, nunca permiso** (herramientas, clientes, gasto y aprobaciones siguen en código).

#### Dependencias
- M1 (motor) y M2 (rol, área, cartera, `IPermisosOrganizacion`, `IContextoUsuario`) implementadas.
- Núcleo versionado del template (patrón de versiones de `ArtefactoVersion`).
### Casos de uso M3
| CU | Actor | Descripción |
|---|---|---|
| CU-M3-01 | Director | Gestiona reglas de la organización (obligatorias y por defecto) |
| CU-M3-02 | Director | Gestiona reglas de cada área |
| CU-M3-03 | Director (ver P1) | Gestiona reglas de la organización para un agente base |
| CU-M3-04 | Miembro | Gestiona reglas de un cliente de cartera (generales o para un agente base) |
| CU-M3-05 | Miembro | Gestiona sus reglas propias |
| CU-M3-06 | Empleado | Consulta las reglas de organización y de su área que le aplican |
| CU-M3-07 | Miembro | Pide una tarea eligiendo cliente de cartera opcional y ve la vista previa de reglas efectivas |
| CU-M3-08 | Miembro | Consulta en el detalle de una tarea qué reglas y versiones se aplicaron |
| CU-M3-09 | Miembro | Consulta el historial de versiones de una regla |
| CU-M3-10 | SuperUsuario (ver P5) | Gestiona reglas de plataforma |
### Reglas funcionales M3
- **RF-M3-01** Una regla tiene: alcance, tipo, modo (solo Organización/Área; el resto se comporta como "por defecto" dentro de su nivel), título, texto, etiquetas opcionales, activa/inactiva, versión actual.
- **RF-M3-02** Alcance `Area` exige área vigente de la organización; `Usuario` pertenece al miembro que la crea; `ClienteCartera` exige cliente vigente; `ClienteCarteraAgente` exige cliente + agente base habilitado en la suscripción; `Agente` exige agente base habilitado.
- **RF-M3-03** Precedencia al construir el contexto: 1 Plataforma · 2 Agente base · 3 Organización obligatoria · 4 Área obligatoria · 5 Cliente (cliente + agente antes que cliente general) · 6 Agente de la organización (M4) / Agente base a nivel organización · 7 Área por defecto · 8 Organización por defecto · 9 Usuario. Lo obligatorio de más arriba gana siempre; entre "por defecto" gana la más específica; las reglas de usuario solo ganan en preferencias personales (formato, idioma, extensión).
- **RF-M3-04** Aplicabilidad: organización → todos los miembros; área → solo miembros de esa área en el momento de crear la tarea; usuario → solo las tareas de su autor; cliente → solo tareas sobre ese cliente (de cualquier miembro); agente → solo tareas de ese agente base.
- **RF-M3-05** Las reglas inactivas, las de un área o cliente dado de baja y las de un usuario bloqueado no se aplican.
- **RF-M3-06** Todo cambio de texto, título, modo o tipo genera una nueva versión (quién, cuándo, texto anterior conservado). Activar/desactivar queda registrado.
- **RF-M3-07** La tarea guarda la instantánea al **crearse** (ver P3): lista de reglas con id, versión, alcance y modo + hash del contexto. Una tarea reanudada usa siempre su instantánea, aunque las reglas cambien después.
- **RF-M3-08** La vista previa muestra exactamente lo que se aplicaría si se envía en ese momento (mismas reglas y orden que la instantánea), agrupado por nivel.
- **RF-M3-09** El texto de las reglas del agente base y de plataforma **no** se muestra a la organización (IP de Olvidata): la vista previa y el detalle muestran solo "Reglas de Olvidata aplicadas" sin contenido.
- **RF-M3-10** Límites (ver P7): 4.000 caracteres por regla; 20.000 caracteres sumando las reglas activas de la organización; 20.000 por área; 8.000 por usuario; 8.000 por cliente. Superado el límite no se guarda/activa.
- **RF-M3-11** Una regla nunca otorga permisos: su texto no cambia herramientas, clientes accesibles ni aprobaciones. El contexto declara que el contenido de archivos y resultados de herramientas no son instrucciones.
- **RF-M3-12** Aislamiento: reglas de una organización nunca se leen, aplican ni modifican desde otra (mismo criterio que M2, CA-T.1).
### Permisos M3
| Acción | Director | Empleado | Staff Olvidata |
|---|:---:|:---:|:---:|
| Reglas de organización: ver | ✅ | 👁 todas las activas (le aplican, ver P8) | — |
| Reglas de organización: crear/editar/activar | ✅ | ❌ | — |
| Reglas de área: ver | ✅ todas | 👁 las de su área | — |
| Reglas de área: crear/editar/activar | ✅ | ❌ | — |
| Reglas por agente base (organización) | ✅ | 👁 (ver P1) | — |
| Reglas por cliente (general y cliente + agente) | ✅ | ✅ crear/editar/activar, incluidas las de otros (ver P2) | — |
| Reglas propias | ✅ las suyas | ✅ las suyas | — |
| Reglas propias de otro miembro | ❌ (ni el Director las ve) | ❌ | — |
| Vista previa y detalle de reglas aplicadas en tareas | ✅ tareas visibles | ✅ sus tareas | ✅ todas, con texto (P9) |
| Ver texto de reglas de cualquier alcance de una organización (solo lectura) | — | — | ✅ staff (P9) |
| Reglas de plataforma | — | — | ✅ SuperUsuario (ver P5) |
### Criterios de aceptacion M3
- **CA-M3-01** El Director crea una regla de organización obligatoria y otra por defecto; ambas aparecen en la vista previa de cualquier miembro en ese orden (obligatoria antes).
- **CA-M3-02** Un Empleado ve las reglas de organización y de su área, sin acciones de edición; por URL/POST a crear o editar recibe 403.
- **CA-M3-03** Una regla del área Marketing aplica a Laura (Marketing) y no a Martín (Contable); si Laura cambia de área, la próxima vista previa refleja el cambio.
- **CA-M3-04** Una regla del cliente "Panadería Norte" aplica a cualquier miembro que elija ese cliente y a ninguna tarea sin cliente o con otro cliente.
- **CA-M3-05** Una regla de cliente + agente CM aplica solo a tareas del CM sobre ese cliente y aparece antes que la regla general del cliente.
- **CA-M3-06** Las reglas propias de un miembro solo aparecen en sus tareas; otro miembro (incluido el Director) no las ve en ningún listado.
- **CA-M3-07** Editar el texto de una regla crea la versión N+1; el historial muestra autor, fecha y texto de cada versión.
- **CA-M3-08** Desactivar una regla la saca de la vista previa y de las tareas nuevas; una tarea creada antes conserva en su detalle la versión que usó.
- **CA-M3-09** Dar de baja un área o un cliente saca sus reglas de la vista previa sin borrarlas.
- **CA-M3-10** Una regla de más de 4.000 caracteres o que haga superar el total del alcance no se guarda y muestra el límite.
- **CA-M3-11** El detalle de una tarea lista las reglas aplicadas (título, nivel, versión) y muestra "Reglas de Olvidata aplicadas" sin su texto.
- **CA-M3-12** Nueva tarea: el combo de cliente de cartera es opcional; la vista previa se actualiza al cambiar el cliente.
- **CA-M3-13** Una tarea que se reanuda tras un reinicio usa la instantánea original aunque una regla se haya editado en el medio.
- **CA-M3-14** Ids de reglas, áreas o clientes de otra organización en URL o POST → 404, sin datos ajenos (RF-M3-12).
- **CA-M3-15** El texto de una regla que contenga etiquetas o marcadores de sección no rompe la estructura del contexto (se escapa).
### Supuestos M3
- S-M3-01 El agente base elegido es uno de la suscripción vigente (como hoy).
- S-M3-02 Las reglas son texto libre en castellano; no se valida semánticamente su contenido.
- S-M3-03 El costo extra de tokens por reglas se controla con los límites y con caché de prompt (prefijo estable).
### Riesgos M3
- R-M3-01 (alto) **Inyección de instrucciones** desde el texto de reglas de miembros (intentar pisar plataforma u obtener el prompt del agente base) → plataforma primero, declaración de precedencia, escape de marcadores, regla nunca otorga permisos; no es garantía total.
- R-M3-02 (medio) **Costo y calidad** con muchas reglas → límites + orden estable para caché.
- R-M3-03 (medio) **Deriva** entre vista previa, instantánea y lo que usa el motor si se calculan por caminos distintos → un único constructor.
- R-M3-04 (medio) **Datos sensibles** cargados en reglas (contraseñas, datos bancarios) → aviso en pantalla; no se cifra.
- R-M3-05 (bajo) **Contradicciones** entre reglas → resueltas por precedencia; ayuda por etiquetas (P4).
### Banderas tempranas M3
- Migración EF: **sí** (reglas, versiones, reglas de plataforma, cliente e instantánea en la tarea).
- Integración externa: **no** nueva (usa la API de Anthropic existente; sin corridas pagas en QA).
- Máquina de estados: **no**.
### Preguntas M3 — respuestas de Joaquín (2026-09-14)
- **P1 — Reglas de organización para un agente base:** **solo el Director** (confirmado).
- **P2 — Reglas de cliente creadas por otro miembro:** **cualquier miembro** las edita y desactiva, con historial de autor.
- **P3 — Momento de la instantánea:** **al crear la tarea**.
- **P4 — Etiquetas + aviso de reglas del mismo tema en alcances superiores:** **sí, en M3**.
- **P5 — Reglas de plataforma:** **archivo del núcleo** (re-explicada): se escriben junto a los agentes base, se importan con la consola Admin y se publican con la evaluación obligatoria (`IVersionadoService`), igual que los prompts. Sin pantalla de edición en el backoffice (solo lectura para staff).
- **P6 — Procedimientos:** **en M3**.
- **P7 — Límites:** **confirmados** (4.000 por regla; 20.000 por organización y por área; 8.000 por usuario y por cliente).
- **P8 — Empleado ve también las reglas por defecto de organización y de su área:** **sí**.
- **P9 — Staff de Olvidata ve el texto de las reglas de las organizaciones:** **sí**, para controlar cómo configuran los prompts. Ajusta la matriz de permisos: el staff ve el texto de todas las reglas de organización, área, cliente y usuario (solo lectura) en backoffice y en el detalle de tareas. RF-M3-09 no cambia: la organización sigue sin ver el texto de reglas de plataforma ni del agente base.
### Reutilizacion relevada M3
- **crm-olvidata** (`docs/crm-olvidata/definiciones/3-arquitecto-mvc.md`): system prompt generado en 2 bloques — prefijo estable con `CacheControl` y contexto variable sin cachear; medido: de USD 0,044 a 0,016 por conversación. Aplica al orden del contexto de M3.
- **Template propio:** versionado de `ArtefactoVersion` (núcleo) como patrón de historial; `IVersionadoService` si se elige P5-B.
- Sin otro proyecto con reglas por alcance y precedencia.
### Clasificacion de perfil de cliente M3
Producto propio (proyecto personal): presupuesto omitido (ver `feedback` de Joaquín 2026-09-14).

---

**M2 — Organización del portal** (Discovery + Análisis, 2026-09-14). Estado: **aprobado por Joaquín el 2026-09-14** (respuestas P1–P5 incorporadas).

Contexto: el template (portal ASP.NET Core MVC multi-tenant, repo `C:\Sistemas\Olvidata Agentes Multi-rubro`) hoy distingue solo staff de Olvidata (`SuperUsuario`/`Administrador`) y "usuario de cliente" (`UsuarioCliente` + `TenantId`). Todos los usuarios de una organización tienen los mismos permisos. El diseño de producto aprobado por Joaquín (`docs/diseno-organizacion-roles-reglas.md`, decisiones 2026-09-14) requiere jerarquía dentro de cada organización y agrupación por áreas, base de las etapas siguientes (reglas por nivel M3, agentes de la organización M4).

Objetivo de negocio: que cada organización cliente administre su estructura (áreas, rol y área de cada miembro, clientes que atiende) y que los permisos del portal respeten esa jerarquía. El alta de personas queda controlada por Olvidata.

#### Alcance incluido
1. **Rol de organización** por miembro: `Director` o `Empleado`, disponible en la sesión (login) y usado por todo el portal.
2. **ABM de Áreas** (solo Director): listado, alta, edición, baja lógica.
3. **Gestión de miembros**: el **alta** de miembros (nombre, email, contraseña inicial, rol y área) la hace **solo el SuperUsuario de Olvidata** desde el backoffice (P3). El Director ve el listado de miembros de su organización y edita rol, área y bloqueo/desbloqueo.
4. **Cartera de clientes de la organización**: listado, alta, edición (Director y Empleado); baja lógica solo Director. Todos los miembros ven todos los clientes. Sin estado Activo/Inactivo (P4).
5. **Servicio de permisos por rol** consultado por los servicios de negocio (no por controllers ni vistas), con la matriz del §Permisos.
6. **Visibilidad de tareas por rol** (ajuste sobre M1): Director ve todas las tareas de la organización; Empleado solo las propias.
7. **Backoffice de Olvidata**: el SuperUsuario da de alta miembros de cualquier organización eligiendo rol y área; el staff sigue viendo todo.
8. **Menú lateral** según rol: "Mi organización" (Miembros, Áreas) solo Director; "Cartera de clientes" para todos los miembros.

#### Alcance no incluido
- Reglas/prompts por organización, área, usuario, cliente o agente → **M3**. En M2 el área existe como agrupador, sin reglas.
- Agentes de la organización → **M4**. Workspace por cliente → **M5**. Límites de gasto por miembro y aprobaciones por rol → **M6**.
- Asignación de empleados a clientes (decisión 4: todos ven todos).
- Roles configurables distintos de Director/Empleado (decisión 1).
- Un usuario en más de una organización.
- Alta de miembros por el Director o invitación por email (P3).
- Estado Activo/Inactivo de clientes de cartera (P4).
- Migración de usuarios existentes: no hay clientes; la base de desarrollo se puede regenerar (P1).
- Alta autoservicio de organizaciones (sigue siendo el staff de Olvidata).
- Filtros de Tareas por área o por cliente (llegan con M3/M5).

#### Dependencias
- M1 (motor de agentes y pantalla Tareas) implementada.
- Identity, `TenantMiddleware`/`ITenantContext`, `TenantClaimsPrincipalFactory` y backoffice existentes en el template.
