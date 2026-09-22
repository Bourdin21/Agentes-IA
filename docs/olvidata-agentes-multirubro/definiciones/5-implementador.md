# Memoria - Implementador

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-09-21 (PA-05: backoffice del SuperUsuario y organización pausada que frena al motor)

## Definiciones vigentes

# PA-05 — Backoffice del SuperUsuario: administrar organizaciones desde `Organizaciones y licencias`

Estado: **implementado 2026-09-21; pendiente de QA; sin commit ni deploy (los hace Joaquín)**. Pedido textual de Joaquín:
*«no-reply@olvidata.com.ar debería poder configurar todo el portal, incluidas organizaciones, plan, consumo, pausar plan.
Cada organización tiene un listado de usuarios, con distintos roles.»* Cierra el pendiente **PA-05** de `metadata.md`
(staff sin UI para editar miembros + la tarea encolada de una organización suspendida que igual ejecutaba el worker).
Repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `fe6c03e` (producto **en producción**). Gate: no hay
definiciones 2/3 propias; es un pendiente registrado desde M2 y pedido directo de Joaquín, como las correcciones de M16.

### Escaneo de reutilizacion
- Sin match en otros proyectos del estudio: se reutilizó lo del propio repo. Núcleo del bloqueo/desbloqueo y la regla del
  último Director (M2, `MiembroService` + `Tenant.VersionMiembros`), invalidación por `IResolvedorSesion.Invalidar`
  (M2 RF-11), "se muestra una sola vez" por TempData (clave de activación), `NucleoTextos.EstadoLicencia` (M15) para los
  badges con ícono, `btn-swal-confirm` para las confirmaciones.

### Plan por etapas (el orden en que se hizo)
1. Línea base: `dotnet test` **625/625**.
2. Contrato: permiso `PuedeAdministrarOrganizaciones` (SuperUsuario), `IOrganizacionBackofficeService`, 4 métodos nuevos en `IMiembroService`, DTOs.
3. Services: `OrganizacionBackofficeService` (editar, impacto, estado, extender licencia), métodos de backoffice en `MiembroService`, `GeneradorContrasena`.
4. Worker: reclamo de tareas, bucle de la tarea y reclamo de programaciones miran `Tenant.Estado`.
5. Web: 6 acciones en `ClientesController` con `RequireSuperUsuario`, 2 vistas nuevas, ficha e índice ajustados.
6. Tests (16 nuevos + 1 reescrito), suite completa, smoke contra el portal local con MySQL y modelo simulado.

### Archivos y capas modificadas
- **Application:** `Interfaces/IOrganizacionBackofficeService.cs` (nuevo), `Interfaces/IMiembroService.cs`, `Interfaces/IPermisosOrganizacion.cs`, `DTOs/OrganizacionDtos.cs` (`MiembroBackofficeEditarDto`, `OrganizacionEditarDto`, `ImpactoEstadoOrganizacionDto`).
- **Infrastructure:** `Services/Organizacion/OrganizacionBackofficeService.cs` y `GeneradorContrasena.cs` (nuevos), `MiembroService.cs` (el bloqueo pasó a un núcleo privado `AlternarEstadoAsync` compartido por Director y SuperUsuario), `PermisosOrganizacion.cs`, `DependencyInjection.cs`, `Services/Motor/ProcesadorTareas.cs`, `Services/Programaciones/EjecutorProgramaciones.cs`.
- **Web:** `Controllers/ClientesController.cs` (Editar GET/POST, CambiarEstado, ExtenderLicencia, EditarMiembro GET/POST, CambiarEstadoMiembro, GenerarContrasena), `Views/Clientes/Editar.cshtml` y `EditarMiembro.cshtml` (nuevas), `Details.cshtml` (card Organización con estado y acciones, aviso de organización no activa, botón y modal de vencimiento, columna Editar en miembros, badges con ícono), `Index.cshtml` (estado con ícono), `Helpers/OrganizacionTextos.cs` (nuevo), `Models/AgentesViewModels.cs`.
- **Tests:** `BackofficeSuperUsuarioTests.cs` (nuevo), `ProgramacionesTests.cs` (1 test reescrito + 1 nuevo).
- **Datos: sin tocar. Ni una entidad, ni una columna, ni una migración EF.** `Mcp` y `Cli` sin tocar.

### Decisiones de implementacion
- **DI-PA05-1 — "Pausar" es `EstadoTenant.Suspendido`.** No se agregó un estado nuevo: el enum ya tenía Activo/Suspendido/Baja y el login ya lo respetaba (M9). En pantalla se dice **Pausada** (la palabra del pedido); en código y base sigue `Suspendido`.
- **DI-PA05-2 — Cómo frena al motor una organización pausada (lo que dejó abierto PA-05).** Nada se cancela ni se borra: pausar es reversible con un clic, así que el trabajo **se retiene**. Tres puntos del worker miran `Tenant.Estado`:
  1. **`ProcesadorTareas.ReclamarSiguienteAsync`**: las organizaciones no activas se suman a la lista de excluidas (misma técnica que los clientes saturados). Sus tareas Pendientes — y las EnCurso con lease vencido — quedan en la cola y la cola de los demás clientes sigue. Al reactivar, las toma el próximo ciclo.
  2. **Bucle de `ProcesadorTareas.EjecutarAsync`**, al principio de cada vuelta (antes de ejecutar herramientas y antes de llamar al modelo): si la organización ya no está activa, la tarea **vuelve a Pendiente** sin worker ni lease, y **no cuenta como intento** (`Intentos - 1`), así una pausa larga no la acerca al máximo que la da por fallida. Los pasos guardados quedan: al reactivar sigue exactamente donde estaba, sin repetir la llamada ni el efecto de la herramienta (test). **Límite aceptado:** una llamada al modelo que ya estaba en vuelo termina y se cobra; la siguiente no sale.
  3. **`EjecutorProgramaciones.ReclamarAsync`**: no reserva vueltas de organizaciones no activas (ni retoma sus Reservadas). La programación queda Activa, **sin sumar fallas**, con la próxima ejecución vencida; al reactivar dispara **una** vuelta (la regla de siempre de M12: se recalcula desde ahora) y sigue su calendario.
  - Las tareas que esperan aprobación o partes (M6/M7a) no gastan; cuando se despiertan pasan a Pendiente y las frena el punto 1.
  - **Suspendido y Baja frenan igual.** La baja se diferencia en el texto y en la intención, no en el efecto: los datos se conservan y se puede reactivar. Las licencias no se revocan solas; la API de licencias ya rechazaba emitir tokens a un "cliente no activo".
- **DI-PA05-3 — Cambio deliberado de comportamiento en programaciones (criterio vs. código).** El test `Con_la_empresa_suspendida_ninguna_vuelta_crea_tareas` esperaba que la vuelta de una empresa suspendida se **reservara y se cerrara Bloqueada** con una falla. Con eso, cinco barridos (cinco días de una diaria) alcanzaban para **terminar la programación sola**: el cliente pausado la encontraba muerta al volver. Se cambió el código y se reescribió el test (`..._y_la_programacion_espera_intacta`). El cierre Bloqueado de la fase 2 **se conserva** para la carrera "pausaron entre la reserva y la creación de la tarea" (test nuevo).
- **DI-PA05-4 — Sesiones.** Pausar/reactivar invalida la sesión cacheada de **todos** los miembros de la organización (`IResolvedorSesion.Invalidar` uno por uno): el corte rige en su próxima request, no a los 60 s del TTL. Mismo límite de M2 (RT-01): la invalidación es por proceso.
- **DI-PA05-5 — Miembros desde el backoffice.** El SuperUsuario **sí** cambia nombre y email (el Director no). Mismo núcleo que el Director para bloquear (`AlternarEstadoAsync`) y la misma regla del último Director con `VersionMiembros` y reintento. Al cambiar el email se mueve también el `UserName` **solo si era igual al email anterior** (alta estándar), para no romper un usuario legado. Email duplicado se valida contra `NormalizedEmail` y `NormalizedUserName` de todos los usuarios.
- **DI-PA05-6 — Contraseña generada.** Formato `Abcd-efgh-2345` (sin I/l/O/0/1, fácil de dictar), `RandomNumberGenerator`, validada contra los `PasswordValidators` de Identity antes de guardar. Se guarda el hash, se rota el `SecurityStamp` (cierra las sesiones abiertas con la contraseña anterior en la revalidación de Identity), se limpia el lockout y se invalida la sesión. Viaja por TempData (cookie cifrada) y se muestra **una sola vez**, como la clave de activación. Nunca se loguea; el audit trail excluye `PasswordHash` y `SecurityStamp` (M2) y hay un test que lo verifica. **No obliga a cambiarla en el próximo ingreso**: no existe ese mecanismo en el portal.
- **DI-PA05-7 — Editar organización.** El slug se muestra y no se edita. Pasar a "Propia de la organización" exige una clave si no había una; vacía conserva la cargada; **pasar a "Olvidata" borra la clave del cliente** (no se guarda un secreto que no se usa). El límite de gasto no se toca desde acá (ya tiene su card).
- **DI-PA05-8 — Extender licencia.** Cualquier fecha futura (también sirve para adelantar el vencimiento; el mensaje lo dice). Misma clave de activación: no se emite otra. Una revocada no se extiende. La fecha es día argentino y vence al final del día, igual que el alta. **Arreglo de paso:** la columna "Vigente hasta" mostraba el día **siguiente** al elegido (el alta guarda las 00:00 del día siguiente); ahora muestra el día elegido (`OrganizacionTextos.DiaDeVencimiento`).
- **DI-PA05-9 — Permisos en dos capas.** Las 6 acciones nuevas llevan `[Authorize(Policy = "RequireSuperUsuario")]` y cada service vuelve a verificar `PuedeAdministrarOrganizaciones`. El Administrador sigue viendo la ficha (controller en `RequireAdministracion`) **sin ningún botón nuevo**. Un test lee `ClientesController.cs` y falla si una acción nueva pierde la policy. **No se tocaron** `CrearLicencia`, `RevocarLicencia` ni `CambiarLimiteGasto`: el Administrador los sigue pudiendo usar como antes (fuera del pedido; si Joaquín quiere que sean solo del SuperUsuario, es cambiar la policy).
- **DI-PA05-10 — Consultas cruzadas.** `Licencias`, `TareasAgente`, `ProgramacionesTarea` y `Areas` se leen con `IgnoreQueryFilters([AppDbContext.FiltroTenant])` y acotadas explícitamente al `TenantId` de la ficha, con comentario. `Users` y `Tenants` no tienen filtro de tenant. La organización interna (`EsInterna`) no se puede editar ni pausar (404).
- **DI-PA05-11 — Confirmaciones con números reales.** `ImpactoAsync` cuenta miembros activos, tareas en cola, tareas en curso y programaciones activas, y `OrganizacionTextos` arma el texto: quién queda afuera, qué pasa con el motor y qué pasa al volver.

### Migraciones EF
**Ninguna.** No se tocó el modelo. El deploy es solo código: `scripts/deploy-prod.ps1` no tiene nada que aplicar en la base.

### Evidencia de build y tests (medida SIN pipe, leyendo el resumen impreso)
- Línea base: **Con error: 0, Superado: 625, Omitido: 0, Total: 625**.
- Final: **Con error: 0, Superado: 641, Omitido: 0, Total: 641** (625 + 16 nuevos; 1 reescrito), medido dos veces. `BackofficeSuperUsuarioTests` + `ProgramacionesTests`: 55/55.
- `dotnet build OlvidataAgentes.slnx`: **0 errores, 0 advertencias**.
- **Los 5 goldens intactos**: `git status tests/OlvidataAgentes.Tests/Goldens` vacío; el prompt de sistema no se tocó.
- Costo cero: tests con modelo guionado; el portal local se levantó con `Anthropic__Simulado=true` y la línea *MODELO SIMULADO* confirmada en el log de arranque.

### Verificación contra el portal local (MySQL dev, modelo simulado)
Sin navegador: el MCP de Playwright no conectó (timeout), así que **no hubo verificación visual** (tema oscuro, 390 px). Se hizo un
smoke con `curl` contra `https://localhost:7200` sobre una organización descartable `smoke-pa05` creada con la consola
Admin: como SuperUsuario, alta de Directora → editar organización → confirmación de pausa con números → pausar
(Estado 2, aviso "Organización pausada.") → reactivar → emitir licencia (la columna muestra el día elegido) → extender
(vence 2027-04-01 03:00 UTC = fin del 31/03) → degradar a la única Directora (rechazado con el mensaje) → bloquearla
(rechazado, sigue Activa) → cambiar nombre y email (el `UserName` se movió) → generar contraseña (se mostró una vez; al
recargar, 0 apariciones). Como `adminqa@qa.test` (Administrador): la ficha abre **sin botones nuevos** y las 4 acciones
probadas van a AccessDenied. Como `dira@qa.test` (Directora de otra organización): todo AccessDenied, incluida la ficha. Log
sin errores. **La organización, la usuaria, la licencia y sus filas de auditoría se borraron**; el tenant 19 y el 20 no se tocaron.
Se detuvo un portal que había quedado prendido desde el 2026-09-20 (bloqueaba el build) y el que se levantó para el smoke.

### Riesgos residuales
- La llamada al modelo que ya estaba en vuelo al pausar se completa y se cobra (una, como máximo, por tarea en curso).
- Invalidación de sesión por proceso (RT-01 de M2): con más de una instancia, las demás toman la pausa al vencer el TTL de 60 s. Hoy SmarterASP corre una.
- Al reactivar, todo lo retenido arranca junto (limitado por `MaxTareasPorCliente`) y cada programación vencida dispara una vuelta.
- La contraseña generada no se fuerza a cambiar en el primer ingreso.
- Sin verificación visual (ver arriba): QA tiene que mirar la ficha a 390 px y en tema oscuro.

### Pruebas mínimas para QA
1. SuperUsuario: editar nombre/CUIT/email/quién paga; pasar a "Propia" sin clave → error; con clave → OK; volver a Olvidata → la clave se borra. El slug no se puede cambiar.
2. Pausar una organización con una sesión de un miembro abierta: el miembro queda afuera en su próxima acción, con el mensaje de organización suspendida. Reactivar: vuelve a entrar.
3. **Worker:** con el modelo simulado, crear una tarea de una organización, pausarla antes de que corra → queda Pendiente y no se ejecuta; la de otra organización sí. Reactivar → corre y termina. Una programación vencida de la organización pausada no crea vuelta; al reactivar crea una.
4. Extender una licencia: el modal trae el vencimiento actual; guardar otra fecha; la columna muestra el día elegido. Una revocada no muestra el botón.
5. Miembros: editar nombre/email/rol/área; con un solo Director activo, la pantalla lo avisa, no ofrece Bloquear y el cambio a Empleado se rechaza. Con dos Directores, sí. Bloquear/desbloquear. Generar contraseña: se ve una vez, la anterior deja de servir.
6. Administrador (`adminqa@qa.test`): ve la ficha sin Editar datos, Pausar, Dar de baja, vencimiento ni editar miembro; por URL directa → acceso denegado. Miembro de una organización → acceso denegado en todo `/Clientes`.
7. Mobile 390 y tema oscuro de la ficha, Editar y Editar miembro; confirmaciones legibles.

### Checklist de merge
- [x] Build 0/0 · [x] 641/641 · [x] goldens intactos · [x] sin migración · [x] `Mcp`/`Cli` sin tocar · [x] permisos en policy y service · [x] consultas cruzadas justificadas · [x] auditoría automática (sin hash ni stamps)
- [ ] QA funcional · [ ] verificación visual 390 / oscuro · [ ] commit y deploy (Joaquín)


# M16 — Tablero de actividad al iniciar sesión

Estado: **implementada 2026-09-19; el gráfico rehecho por niveles el 2026-09-20; pendiente de QA**. Entrada:
`1-analista-funcional.md` M16 (RF-M16-01..06), `2-disenador-funcional.md` M16 (D-M16-1..7) y `3-arquitecto-mvc.md` M16
(RT-M16-01..03), las tres aprobadas. Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `9bb5f93`, línea base
**601/601**. **Sin migración EF: es todo lectura sobre lo que ya existe. Ni una llamada al modelo. Sin commits.** `Mcp` y
`Cli` sin tocar. Los 5 goldens de contexto, intactos (nada de M16 se acerca al armado del contexto).

> **2026-09-20 — el gráfico se rehízo entero.** Joaquín lo pidió así: *«El mapa de la actividad se tiene que ver de una
> manera más organizada: personas, agentes, tareas y clientes tienen que ser niveles.»* Lo que había era una nube de
> fuerzas donde todo flotaba junto; lo que hay ahora son **cuatro columnas con su rótulo** que se leen de un lado al
> otro. El detalle está más abajo, en **DI-M16-13..19**; lo de arriba de esa lista sigue valiendo tal cual, salvo lo que
> esas decisiones corrigen explícitamente. Línea base de esta vuelta: commit `83c057f`, **621/621**.

### Escaneo de reutilizacion

Se revisaron los `5-implementador.md` de los demás proyectos del estudio: **ninguno tiene un tablero de actividad ni un
gráfico de nodos**, así que no hubo código para traer de otro repo. Lo que sí se reusó, todo del propio portal:

| Fuente | Qué se tomó | Grado |
|---|---|---|
| `ServicioTareas.Visibles()` (M2/RF-12) | La regla de visibilidad por rol tal cual: Director todas, Empleado solo las suyas | Literal |
| `ProgramacionTareaService.BaseListado()` (M12) | Qué programaciones ve cada uno, para las vueltas recientes | Literal |
| `IAprobacionService.ContarPendientesParaMiAsync`, `IProgramacionTareaService.ResultadosSinVerAsync`, `IControlGasto.AvisoParaMiAsync` | **Se llaman, no se reimplementan.** Es la única forma de garantizar el criterio "el contador del tablero coincide con el del menú" | Literal |
| `Views/Tareas/Detalle.cshtml` (M3b) | El patrón de refresco: SignalR más sondeo de respaldo que recarga HTML del servidor, no una aplicación de página única | Patrón |
| `Helpers/SubtareasTextos.cs` (M7a) | Forma del helper de estado, tupla `(Texto, Icono, Clase)` siempre con texto; y el vocabulario «le pidió ayuda a» | Patrón |
| `Views/Shared/_AvisoGasto.cshtml` (M6) | El aviso de gasto del bloque *Te espera*, sin una línea nueva | Literal |
| `site.css` → `.ov-alert`, `.ov-badge`, `.card`, `.ov-page-head` | Todo el armazón visual de los bloques | Literal |

### Plan por etapas (el orden en que se hizo)

1. DTOs, contrato y opciones en Application.
2. `TableroService` en Infrastructure, con la visibilidad de M2 copiada de `ServicioTareas`.
3. Tiempo real: grupo por organización en `TareasHub` y emisión en `NotificadorTareasSignalR`.
4. `HomeController` decide tablero o portada; parcial de los tres bloques renderizado por el servidor.
5. El gráfico: CSS, isla de datos JSON y `tablero.js`.
6. Tests, build, y recién ahí la verificación en el navegador.

### Archivos y capas modificadas

**Application**

- Nuevo `DTOs/TableroDtos.cs`: `TableroDto` (con `Vacio`), `TableroAhoraDto` / `TareaVivaDto` / `VueltaRecienteDto`,
  `TableroEsperaDto` / `AsignacionEsperaDto`, `TableroPasadoDto` / `ActividadTableroDto`, `GrafoTableroDto` /
  `NodoTableroDto` / `AristaTableroDto`, `AlcanceGrafo`, `TiposNodoTablero`, `RelacionesTablero`.
- Nuevo `Interfaces/ITableroService.cs` (un solo método, `ObtenerAsync`).
- Nuevo `Settings/TableroOptions.cs` (sección `Tablero` de `appsettings.json`): topes de filas, tope de nodos y
  segundos de sondeo.

**Infrastructure**

- Nuevo `Services/Tablero/TableroService.cs`. Consultas acotadas por código al tenant y a la visibilidad de M2, todas
  con tope; el grafo sale de **la misma consulta** que las listas, no de una segunda vuelta más abierta. Registrado en
  `DependencyInjection.cs`.

**Web**

- `Hubs/TareasHub.cs`: grupo por organización (`GrupoOrganizacion`) y `SeguirOrganizacion()` **sin parámetros**.
- `Services/NotificadorTareasSignalR.cs`: además del grupo por tarea, emite al grupo de la organización.
- `Controllers/HomeController.cs`: `Index` decide tablero o portada; nuevo `Actividad` devuelve el parcial.
- Nuevos `Models/TableroViewModel.cs`, `Helpers/TableroTextos.cs`, `Views/Home/Tablero.cshtml`,
  `Views/Home/_TableroBloques.cshtml`, `wwwroot/js/tablero.js`.
- `Views/Shared/_Layout.cshtml`: "Inicio" pasa a "Tablero" (con `fa-gauge-high`) **solo para miembros**; el staff sigue
  viendo "Inicio".
- `Middleware/SecurityHeadersMiddleware.cs`: **solo comentario** — queda escrito que d3 y SignalR salen de jsdelivr,
  que ya estaba permitido, y por qué se eligió un origen ya permitido.
- `wwwroot/css/site.css`: bloque `ov-tablero-*` / `ov-grafo-*` y los tres colores del gráfico.

**Tests**: nuevo `tests/OlvidataAgentes.Tests/TableroTests.cs` (20 tests).

### Decisiones de implementacion

- **DI-M16-1 — d3 v7 desde jsdelivr, que YA estaba en el CSP.** RT-M16-02 avisaba que un CDN nuevo no da error: no
  carga y nadie se entera. En vez de agregar un origen se eligió una librería del origen que ya estaba. d3 además
  dibuja **SVG**, que es lo único que permite que los nodos tomen los tokens `--ov-*` y cambien solos con el tema
  oscuro; una librería de canvas (vis-network) habría necesitado su propia paleta duplicada. Hay un **test** que
  compara los `<script src>` de la vista contra el `script-src` del middleware: si alguien cambia de CDN sin tocar el
  CSP, falla en el build y no en silencio.
- **DI-M16-2 — El respaldo del gráfico está en el HTML y se oculta cuando el dibujo existe.** El lienzo arranca
  `hidden` y el script lo muestra recién cuando terminó de dibujar. Si d3 no cargó, lo que queda a la vista es la lista
  de vínculos en palabras que el servidor ya mandó. Cuando el gráfico sí aparece, esa lista pasa a `visually-hidden`
  — **sigue en el DOM**, porque un SVG de nodos no se lee con un lector de pantalla.
- **DI-M16-3 — El aviso al grupo de la organización va vacío.** Al grupo lo escuchan también los Empleados, que no ven
  las tareas de sus compañeros: mandarles el número de tarea ya sería contarles que existe. Reciben "algo se movió" y
  releen `/Home/Actividad`, que aplica la visibilidad del lado del servidor.
- **DI-M16-4 — `SeguirOrganizacion()` no recibe el tenant.** Sale de la sesión resuelta en el servidor (RT-M16-03). Hay
  un test que falla si alguien le agrega un parámetro.
- **DI-M16-5 — El gráfico baja de vivo a hoy, y de hoy a la semana.** El diseño pedía vivo → día. Con la organización
  real (Contadores BMA) apareció el caso aburrido: *Lo que pasó* decía "4 en 7 días" y el gráfico, al lado, mostraba un
  recuadro vacío porque ninguna era de hoy. Se agregó el tercer escalón y el badge dice cuál está mostrando: "En vivo",
  "Hoy" o "Esta semana". Es el mismo motivo que sostiene R-M16-01.
- **DI-M16-6 — El refresco no toca el DOM si el HTML no cambió.** El sondeo corre cada 15 s con socket o sin él, pero
  compara el HTML recibido con el anterior: la vuelta sin novedades no parpadea, no rearma el dibujo y no le borra a
  nadie el nodo que había elegido. Tampoco refresca con la pestaña de fondo ni mientras el foco está adentro del
  gráfico.
- **DI-M16-7 — Solo tareas de tipo `Trabajo`, también para el Director.** Las conversaciones de plataforma
  (configurador de reglas, asistente de reparto) son la persona configurando el sistema, no trabajo para un cliente:
  incluirlas pondría "Asistente para repartir trabajo" como un nodo más al lado de los agentes del rubro.
- **DI-M16-8 — Los ids del grafo son opacos (`p1`, `a2`, `c3`).** No viaja ningún id de usuario, de agente ni de
  cliente. Lo único con id real es el salto del nodo, que apunta a **una tarea que ya es visible para quien mira** por
  construcción: sale de la misma consulta que las listas.
- **DI-M16-9 — Los tres colores del gráfico se verificaron con el validador de paletas**, contra las dos superficies
  (`#ffffff` y `#1e293b`): banda de luminosidad, piso de croma, separación para daltonismo y contraste. El ámbar del
  cliente baja un paso en tema oscuro (`#f59e0b` → `#d97706`) porque el claro se sale de la banda sobre `#1e293b`. La
  identidad **nunca es solo color**: cada tipo tiene su forma (círculo, cuadrado, rombo) y su entrada en la leyenda, y
  lo vivo lleva el anillo que late **más la etiqueta "en curso"** (D-M16-3). El anillo se queda quieto con
  `prefers-reduced-motion` (R-M16-06).
- **DI-M16-10 — `_TableroBloques` es el mismo parcial que renderiza la pantalla y que devuelve el refresco.** Una sola
  forma de dibujar el tablero; el JavaScript no arma ni un `<li>`.
- **DI-M16-11 — Sin DataTables.** La regla de la instrucción 25 es para los listados de una entidad; acá hay resúmenes
  con tope de 5 a 8 filas que enlazan a las pantallas reales (Tareas, Aprobaciones, Asignaciones, Resultados), que sí
  tienen su grilla con filtros.
- **DI-M16-12 — *Lo que pasó* no tiene, ni puede tener, una lista de personas** (R-M16-07). Hay un test que recorre las
  propiedades de `TableroPasadoDto` y falla si alguna se llama Persona, Miembro o Usuario: el día que alguien quiera
  agregar el ranking, se va a topar con el test antes que con la pantalla.

### El gráfico por niveles (2026-09-20)

Lo que cambió de capa a capa: **Application** — `TiposNodoTablero` suma `Tarea` y la lista `Niveles` (que *es* el orden
de las columnas); `RelacionesTablero` reemplaza `TrabajaSobre` por `Ejecuta` (agente → tarea) y `EsPara` (tarea →
cliente); `NodoTableroDto` suma `Nivel`, `Orden` y `Estado`; nuevo `NivelGrafoDto`; `TableroOptions.MaxNodosGrafo` pasa
a `MaxNodosPorNivel`. **Infrastructure** — `ArmadorGrafo` reescrito. **Web** — `TableroTextos.Nivel()`, la isla de datos
manda niveles y orden, la leyenda suma Tareas y «le pidió ayuda a», la lista de respaldo se agrupa por nivel, y
`tablero.js` pasa de simulación de fuerzas a disposición calculada. **Sin migración EF, otra vez: no hay ni una columna
nueva.**

- **DI-M16-13 — La tarea es el nodo del medio, y de él cuelga la cadena entera.** El recorrido se lee
  `persona → agente → tarea → cliente`; una tarea sin cliente termina en su nivel, sin arista de salida. Como
  consecuencia, **si una tarea no entra en el tope de su nivel, la fila entera se saltea**: media cadena dibujada (un
  cliente suelto, un agente sin tarea) confunde más de lo que muestra. El nodo lleva `#218` como etiqueta y su estado
  como detalle, así que el gráfico dice además *en qué anda* cada trabajo sin mostrar una línea de su texto (RF-M16-06
  sigue en pie).
- **DI-M16-14 — Las partes de M7a se quedan DENTRO del nivel de los agentes, como un arco punteado.** Era la decisión
  fina del pedido. Sacarlas del nivel (poner al ayudante en una quinta columna) rompía la lectura, y dejarlas como una
  flecha entre columnas obligaba a que alguna volviera hacia atrás. Van como **un arco al costado de la columna, del
  coordinador al ayudante**, punteado para que se lea como un desvío y no como el camino, con su entrada propia en la
  leyenda. La dirección la garantiza el orden del nivel (DI-M16-15), no el dibujo. Y el ayudante igual tiene su propia
  tarea en la columna de al lado: la parte también es un nodo.
- **DI-M16-15 — Los agentes se ordenan por topología, no por nombre.** Es lo que hace imposible la flecha hacia atrás:
  un Kahn sobre las aristas «le pidió ayuda a» deja al coordinador **siempre por delante** del que ayudó, con desempate
  por nombre para todo lo demás. Determinístico igual, y si alguna vez llegara un ciclo (no puede: el padre de una tarea
  siempre es anterior) lo que quedó sin ubicar se agrega por nombre en vez de desaparecer del dibujo. Hay un test con el
  ayudante renombrado para que, por orden alfabético, fuera primero: si alguien saca la topología, falla.
- **DI-M16-16 — El lugar de cada nodo lo decide el servidor; el navegador solo lo pasa a píxeles.** `Nivel` y `Orden`
  viajan en el DTO. Personas y clientes por nombre, tareas de la más nueva a la más vieja (el número ya es la línea de
  tiempo), agentes por topología. **Cuidado con no confundir dos órdenes distintos**: los nodos *entran* por recencia
  (las filas llegan ordenadas, así que el tope deja afuera lo viejo) y *se dibujan* por la regla determinística. Hay un
  test que pide el tablero dos veces y compara `nivel:orden:etiqueta`, y otro que falla si alguien vuelve a meter
  `forceSimulation` en el JS — que es la forma silenciosa de deshacer todo esto.
- **DI-M16-17 — El tope es por nivel, no global.** El nivel que se llena primero es siempre el de tareas; un tope global
  dejaba columnas enteras sin dibujar por culpa de él. Cada columna cuenta su propio «y N más» al pie, y el `Omitidos`
  del DTO es la suma. El navegador suma a ese número **lo que no entra por espacio**: si en una columna no caben los 8,
  muestra los que caben y el resto va al mismo cartel. El alto del dibujo reserva ese renglón — sin la reserva el cartel
  se dibujaba por debajo del borde del SVG, que es justo el aviso que no se puede perder.
- **DI-M16-18 — Columnas si entran, filas apiladas si no; y el SVG se mide en píxeles reales.** Se sacó el `viewBox`:
  ahora el script mide la tarjeta y dimensiona el SVG, así que el texto mide lo que dice que mide y desapareció la media
  query que inflaba las etiquetas para compensar la escala. Por debajo de **416 px** cuatro columnas dejan ~80 px para
  cada nombre, así que ahí el dibujo da vuelta los niveles y los apila como filas — un teléfono cae siempre de ese lado.
  Las etiquetas **se recortan midiéndolas** (`getComputedTextLength`), no contando letras: calcular por cantidad de
  letras fallaba apenas cambiaba el tamaño de fuente y el nombre se salía del dibujo por el costado.
- **DI-M16-19 — Dos arreglos de legibilidad que no estaban pedidos pero se veían feos.** (a) Las columnas cortas van
  **centradas** contra la más larga: si no, los clientes quedan todos arriba y las flechas trepan en diagonal desde
  abajo. (b) Las etiquetas llevan un **halo del color de la tarjeta** (`paint-order: stroke fill`): en un dibujo de
  cuatro columnas siempre hay una línea que pasa por donde está un nombre, y sin el halo la línea se le mete entre las
  letras. El contorno va debajo del relleno, así que el texto se lee igual y lo que cambia es lo que pasa por atrás.
- **Lo que NO cambió, a propósito:** los tres colores (y por lo tanto no hubo que revalidar nada — se volvió a correr el
  validador contra `#ffffff` y `#1e293b` y sigue pasando); la forma por tipo; la etiqueta «en curso» además del anillo;
  el escalón vivo → hoy → semana con su badge; `prefers-reduced-motion`; la visibilidad de M2 dentro del gráfico; el
  respaldo en palabras sin JavaScript; d3 desde jsdelivr y su test de CSP. **La tarea es el único nodo sin color propio
  —es el eslabón, no una categoría más—**: va en tinta neutra con su hexágono, que es lo que permitió sumar un cuarto
  tipo sin tocar la paleta validada. Se sacó el arrastre de nodos: con los niveles fijos, mover un nodo a mano solo
  podía romper la disposición.

### Migraciones EF

Ninguna. Ni una columna nueva: todo sale de datos que ya estaban.

### Evidencia de build y tests (medida SIN pipe, leyendo el resumen impreso)

- `dotnet build OlvidataAgentes.slnx`: **0 errores, 0 advertencias**. La advertencia preexistente CS0114 de
  `HomeController.StatusCode` desapareció porque se le puso `new` al reescribir el archivo (mismo comportamiento: la
  declaración ya ocultaba el método base). La de `ReglasPropuestasAgentesTests` (xUnit2013) sigue estando y aparece
  cuando recompila ese proyecto.
- `dotnet test tests/OlvidataAgentes.Tests`: **621 OK de 621** (601 de línea base + 20 nuevos).
- `LectorDocumentosTests` falló una vez en cada una de dos corridas intermedias, siempre un test distinto de esa clase
  y siempre verde al correrla sola (31/31): es la flojera conocida bajo carga, no una regresión de M16.

**Del gráfico por niveles (2026-09-20):** `dotnet build OlvidataAgentes.slnx` **0 errores, 0 advertencias**. (En una
corrida intermedia apareció 1 advertencia: la xUnit2013 preexistente de `ReglasPropuestasAgentesTests`, que se muestra
solo en el build en el que recompila ese proyecto. No es de M16 y ya estaba anotada arriba.) `dotnet test`:
**Con error: 0, Superado: 625, Omitido: 0, Total: 625** (621 de línea base + 4 nuevos), medido dos veces y sin una sola
vuelta roja. `TableroTests` sola: **24/24**. Los 47 tests de contexto y goldens, verdes y con los `.txt` sin tocar.

Los 4 tests nuevos son los que sostienen el pedido: el recorrido de cuatro niveles con toda arista avanzando un nivel;
la tarea sin cliente que termina en su nivel; el orden determinístico (dos llamadas seguidas, mismo `nivel:orden`); y el
coordinador por delante del ayudante con el nombre en contra. Se reescribieron otros tres: el de M7a (ahora comprueba
que la ayuda no salga del nivel), el del tope (ahora por nivel) y el de ids opacos (ahora con la `t` de tarea).

### Verificación en el navegador (dev, MODELO SIMULADO confirmado en el log de arranque)

`https://localhost:7200`, organización **Contadores BMA** (tenant 20), con datos reales.

- **Director (`direccion@bma.test`), sin actividad viva**: los tres bloques presentes. *Ahora* dice "No hay nada
  corriendo en este momento." con el botón *Pedir una tarea*; *Te espera* dice "No tenés nada pendiente. Todo al día.";
  *Lo que pasó* muestra 4 agentes y 2 clientes, "0 hoy · 4 en 7 días". El gráfico dibuja los 8 nodos de la semana
  (2 personas, 4 agentes, 2 clientes) con badge "Esta semana". Al tocar el nodo *Gastón*: "Persona · Gastón / 3
  trabajos / Gastón le pidió a …" y el enlace *Ver la tarea*.
- **Empleado (`gaston@bma.test`)**: ve **3 agentes, él mismo y su cliente**. No aparecen "Dirección BMA", "Cierre y
  balance" ni "SERVICIO TERAPIA RENAL S.A.": la tarea de la Directora no está ni en las listas ni en el gráfico.
- **Con actividad**: con una tarea creada con el modelo simulado, *Ahora* muestra «Gastón le pidió a «Ingresos
  Brutos»» · Trabajando · Paso 1 de hasta 25 · recién, con su barra de avance, y el gráfico pasa a "En vivo" con el
  anillo que late y la etiqueta "en curso". **Sin recargar**, el bloque se llenó a los ~2,5 s de crear la tarea y se
  vació solo cuando terminó. Las dos tareas de prueba (#218 y #219) y sus 4 filas de `EventosUso` **se borraron**:
  Contadores BMA quedó con sus 4 tareas originales y Gastón con su preferencia de tema como estaba.
- **Consola del navegador: 0 errores, ninguna violación de CSP.** El único warning es el de
  `apple-mobile-web-app-capable`, preexistente del layout.
- **Tema oscuro** verificado (tarjetas, tablas y los tres colores del gráfico). **Mobile 390**: los tres bloques
  apilados y el gráfico abajo; `scrollWidth` 388 contra `clientWidth` 385 — los 3 px los aporta el dropdown de usuario
  del topbar, **preexistente**; nada de `ov-tablero-*` ni `ov-grafo-*` se pasa del ancho. En teléfono las etiquetas del
  gráfico se agrandan por media query, porque el SVG se escala al ancho de la tarjeta.

**Del gráfico por niveles (2026-09-20)**, mismo portal y mismo modelo simulado (confirmado en el log de arranque):

- **Director, sin actividad viva**: cuatro columnas rotuladas PERSONAS · AGENTES · TAREAS · CLIENTES, y la semana de
  Contadores BMA se lee entera de izquierda a derecha — Dirección BMA y Gastón, sus 4 agentes, las tareas #205 a #202 y
  los 2 clientes. Tocando el nodo `#204`: *«Tarea · #204 / Completada / Comunicación con el cliente trabaja en #204 /
  #204 es para Cliente CUIT 30-70823732-5»* y el enlace *Ver la tarea*.
- **Con actividad**: se creó una tarea con el modelo simulado (#220, coordinador del estudio sobre SERVICIO TERAPIA
  RENAL) y la cadena apareció completa. El anillo que late, la etiqueta «en curso», las aristas vivas en color primario
  y **el arco punteado de M7a dentro de la columna de agentes**, del coordinador al ayudante, se verificaron dibujados.
- **Empleado (`gaston@bma.test`)**: ve **solo su cadena** — él, sus 3 agentes, sus 3 tareas y su cliente. Se buscó en el
  HTML del tablero «Dirección BMA», «Cierre y balance», «SERVICIO TERAPIA», «#220», «#205», «Coordinador del estudio» y
  el texto del pedido de prueba: **ninguno aparece**. La visibilidad de M2 sigue intacta dentro del gráfico.
- **Sin actividad ninguna**: se comprobó el estado vacío real (los tres bloques con sus mensajes y el gráfico diciendo
  «Cuando haya trabajo, acá se dibuja quién le pidió qué a quién»).
- **Sin JavaScript**: el respaldo del servidor ahora se lee nivel por nivel — *«Personas · Gastón le pidió a … | Agentes
  · Comunicación con el cliente trabaja en #204 | Tareas · #204 · Completada es para Cliente CUIT… | Clientes · …»*.
- **Mobile 390**: los niveles se apilan como filas, flujo de arriba hacia abajo, con su rótulo cada una. `scrollWidth`
  **385 contra `clientWidth` 385**: desapareció incluso el desborde de 3 px que quedaba, porque el SVG ya no se escala.
  Se verificó además por `getBBox` que **ninguna etiqueta se sale del lienzo**.
- **Tema oscuro** verificado: el hexágono de la tarea toma la superficie de la tarjeta y el halo de las etiquetas cambia
  con el tema, igual que el resto.
- **Consola: 0 errores, ninguna violación de CSP.** El único warning sigue siendo el de `apple-mobile-web-app-capable`.
- **Datos de prueba borrados**: la tarea #220, su paso y sus 2 filas de `EventosUso`. Contadores BMA quedó con sus 4
  tareas originales (#202–#205) y `eventosuso` con su máximo anterior (550). Para ver el estado vacío se corrió hacia
  atrás la fecha de la tarea #201 del tenant 19 y **se restauró al valor exacto** (`2026-09-19 20:41:52.381619`).

### Pruebas mínimas para QA

1. Entrar como Director y como Empleado de la misma organización: el Empleado no puede ver en el gráfico ni en las
   listas una tarea que no pidió él.
2. Entrar como staff de Olvidata: tiene que seguir viendo la portada del backoffice, no un tablero vacío.
3. Con una tarea corriendo, mirar el tablero sin recargar: tiene que aparecer y después desaparecer sola.
4. Apagar JavaScript: los tres bloques y la lista de vínculos del gráfico tienen que seguir estando.
5. Comparar el número de *Aprobaciones* del tablero con el contador del menú.
6. Buscar el texto de un pedido dentro del HTML del tablero: no tiene que estar.
7. Mobile 390 y tema oscuro.
8. Una organización sin ninguna actividad todavía: los tres bloques tienen que estar igual, con sus mensajes.

Del gráfico por niveles:

9. Mirar el gráfico y leerlo en voz alta de izquierda a derecha: tiene que dar una frase («Gastón le pidió a Ingresos
   Brutos, que trabaja en la #203, que es para tal cliente»). Los cuatro rótulos tienen que estar a la vista.
10. Refrescar la pantalla varias veces: **ningún nodo se mueve de lugar**. Es el criterio central del pedido.
11. Buscar una arista que apunte hacia la izquierda (o hacia arriba en mobile): **no tiene que haber ninguna**. La única
    que no cruza de columna es la punteada de «le pidió ayuda a», y va siempre del coordinador al que ayudó.
12. Una tarea sin cliente: la cadena tiene que cortarse en la columna de Tareas, sin flecha de salida.
13. Una organización con muchas tareas: cada columna corta en 8 y dice «y N más» al pie, y ese cartel **tiene que
    verse** (no quedar debajo del borde del dibujo).
14. Achicar la ventana de a poco: al pasar por ~416 px el dibujo da vuelta los niveles de columnas a filas sin recargar
    y **sin scroll horizontal**.
15. Un nombre largo de cliente: la etiqueta se recorta con «…» y no se sale del recuadro, en escritorio y en teléfono.

### Checklist de merge

- [x] Build **0 errores, 0 advertencias**.
- [x] Suite completa **625/625**, medida sin pipe (621 de línea base + 4 nuevos).
- [x] Los 5 goldens de contexto, verdes y sin tocar.
- [x] Sin migración EF.
- [x] `Mcp` y `Cli` sin tocar.
- [x] Sin commits; `git status` solo con los 9 archivos de M16.
- [x] Datos de prueba creados en dev, borrados al terminar; la fecha que se movió, restaurada al valor exacto.
- [x] Verificado en el navegador con los dos roles, en los dos temas y a 390 px.
- [x] d3 sigue saliendo de jsdelivr; el test que compara los `<script src>` contra el `script-src` del CSP, verde.
- [x] Los tres colores del gráfico, sin tocar y revalidados contra las dos superficies.
- [ ] QA funcional (pendiente).

### Riesgos y supuestos

- El sondeo cada 15 s por pestaña abierta es el costo que acepta RT-M16-01. Si pesa, lo que corresponde es cachear por
  organización unos segundos (no por usuario) o subir `Tablero:SegundosSondeo`.
- El gráfico corta en **8 nodos por nivel** y cuenta "y N más" en cada columna. Con una organización grande el corte va
  a ser lo normal: lo que entra es lo más reciente, así que se ve lo último y no una muestra al azar.
- `NodoTableroDto.Trabajos` cuenta **participaciones** en las tareas dibujadas (un agente coordinador suma por cada
  parte que pidió). Es el tamaño de la figura, no una métrica para leer.
- **La disposición por niveles no minimiza cruces.** Con varias tareas sobre pocos clientes, las curvas que llegan a la
  columna de clientes se cruzan. Se decidió no tocarlo: cualquier reacomodo por baricentro entra en tensión con el
  criterio de Joaquín de que los nodos no se muevan, y el cruce de una curva molesta bastante menos que un nodo que
  salta de lugar. Si alguna vez pesa, lo que corresponde es ordenar la columna de clientes por baricentro **a partir de
  la base determinística**, no cambiar la regla de orden.
- El tope por nivel y el ancho de la tarjeta son dos límites distintos: el servidor corta en 8 y el navegador puede
  cortar antes si no le entran. Los dos suman al mismo cartel, así que el número siempre dice la verdad de lo que falta.
- El "tablero de staff sobre todas las organizaciones" sigue fuera de alcance, como dice el análisis.

# M15 — Ficha de rubro para el staff (Nucleo/Rubro enriquecida)

Estado: **implementada 2026-09-18, pendiente de QA**. Entrada: pedido de Joaquín (la información de un rubro se veía a
pedazos y **qué organizaciones lo tienen habilitado no se veía en ningún lado**). Repo:
`C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `e248922`. **Sin migración EF. Solo lectura: ni un `<form>` de
escritura ni un endpoint POST nuevo. Ninguna llamada a la API real, sin commits.** `Mcp` y `Cli` sin tocar.

### La decisión de dónde ponerla: se enriquece `Nucleo/Rubro`, no se crea una pantalla nueva

Una pantalla nueva habría repetido nombre, descripción, "incluido en todas las suscripciones", etapas y el desglose de
artefactos — o sea, casi todo lo que `Nucleo/Rubro` ya mostraba. Dos pantallas que dicen lo mismo envejecen distinto y
obligan a elegir cuál mirar. `Nucleo/Rubro` **ya es la ficha del rubro**: le faltaban tres cosas (el desglose por tipo
con publicados/pendientes, quién lo tiene habilitado, y el estado de importación), no una pantalla.

De paso se **eliminó una duplicación que ya existía**: la card suelta "Material de referencia" pasó a ser una fila del
desglose, con su botón "Ver el material" en la fila. Antes había dos lugares donde se contaba el material.

**Rubros como datos, no como ABM.** La pantalla no da de alta ni edita: un rubro sigue siendo un manifiesto del repo que
entra con la consola Admin, versionado por hash, con diff, historial y gate de publicación. Eso quedó escrito en el
resumen XML de `IFichaRubroService` y de `FichaRubroService` para que no se erosione.

### Escaneo de reutilizacion
| Fuente | Qué se tomó | Grado |
|---|---|---|
| `Views/Clientes/Details.cshtml` (vocabulario de licencias) | Las tres palabras Vigente / Vencida / Revocada y el criterio `!Revocada && VigenteHasta > ahora` → `NucleoTextos.EstadoLicencia` | Patrón |
| `Helpers/PruebasTextos.cs` (M8) | Forma del helper de estado: tupla `(Texto, Icono, Clase)`, nunca color solo | Patrón |
| `AgenteOrganizacionService.cs:89` | `IgnoreQueryFilters([AppDbContext.FiltroTenant])` para consultar licencias como staff | Literal |
| `ClientesController.Index` | Exclusión de la organización interna (`!t.EsInterna`, RT-M8-11) | Literal |
| `site.css` → `.ov-detail-grid` | Bloque de pares etiqueta/valor del resumen. **Sin una línea de CSS nueva** | Literal |

No se agregó nada al catálogo de patrones: es una pantalla de detalle de backoffice, sin componente reutilizable nuevo.

### Archivos y capas modificadas
**Application**
- `DTOs/AgentesDtos.cs`: `FichaRubroDto`, `DesgloseArtefactosDto`, `OrganizacionConRubroDto`.
- `Interfaces/INucleoServices.cs`: `IFichaRubroService` (un solo método, `ObtenerAsync(slug)`).

**Infrastructure**
- Nuevo `Services/Nucleo/FichaRubroService.cs`. Cuatro consultas: última versión importada, versiones esperando
  publicación, desglose por tipo y organizaciones habilitadas. Registrado en `DependencyInjection.cs`.

**Web**
- Nuevo `Helpers/NucleoTextos.cs`: nombre de cada tipo de artefacto (singular, plural, una línea de ayuda y clase de
  badge), estado de licencia y fechas en hora argentina. Reemplaza los dos `switch` inline que había en la vista.
- `Controllers/NucleoController.cs`: `Rubro(string id)` inyecta `IFichaRubroService` y pasa la ficha. Nada más.
- `Models/AgentesViewModels.cs`: `NucleoRubroViewModel` suma `Ficha` y `AhoraUtc`.
- `Views/Nucleo/Rubro.cshtml`: resumen, etapas (con estado vacío), "Qué trae este rubro", "Quién lo tiene habilitado" y
  "Detalle de los artefactos".

**Tests**: nuevo `tests/OlvidataAgentes.Tests/FichaRubroTests.cs` (6 tests).

### Decisiones de implementacion
- **DI-M15-1 — "Última versión importada", no "última importación".** No hay registro de importaciones, y un import que
  no cambia ningún hash **no da de alta versiones**. Se informa lo que sí es verificable (el `CreatedAt` de la versión
  más nueva) y el rótulo dice exactamente eso. Prometer "última importación" sería mentir en los casos aburridos.
- **DI-M15-2 — Una fila por organización, con la mejor licencia.** Una organización puede tener varias licencias con el
  mismo rubro. La fila responde "¿lo puede usar hoy?": gana vigente sobre vencida y vencida sobre revocada, y al lado va
  "N licencias incluyen el rubro". El mismo orden ordena la tabla: las vigentes arriba.
- **DI-M15-3 — "Pendientes" del desglose cuenta artefactos, no versiones.** La pregunta del staff es "¿me falta publicar
  algo de este tipo?". El total de versiones esperando el gate va aparte, en el resumen de arriba.
- **DI-M15-4 — `IgnoreQueryFilters([FiltroTenant])` aunque hoy sea redundante.** La sesión de staff ya llega con acceso
  global (`ResolvedorSesion`), así que el filtro no filtra nada. Se ignora igual, por nombre y con comentario: la
  intención queda escrita donde está la consulta y no depende de una decisión que vive en otro archivo. **El filtro de
  borrado lógico sigue puesto.**
- **DI-M15-5 — La consulta va en un service, no en el controller.** `NucleoController` consulta `_db` directo en otras
  acciones, pero la única forma de probar la travesía del filtro de tenant en esta suite (que es de servicios, no de
  controllers) es que la consulta viva en Infrastructure. Además es donde están todos los demás `IgnoreQueryFilters`.
- **DI-M15-6 — `Clientes/Details.cshtml` no se tocó.** Podría usar `NucleoTextos.EstadoLicencia`, pero el helper agrega
  un ícono y eso cambiaría una pantalla que QA ya validó. Queda como mejora menor, anotada abajo.

### Migraciones EF
Ninguna. No se agregó ni cambió una sola columna: todo sale de datos que ya estaban.

### Evidencia de build y tests
- `dotnet build OlvidataAgentes.slnx`: **0 errores, 2 advertencias** — las dos preexistentes (CS0114 en
  `HomeController.StatusCode`, xUnit2013 en `ReglasPropuestasAgentesTests`).
- `dotnet test`: **595 OK / 5 fallidos de 600**. Los 6 tests nuevos pasan.
- **Los 5 fallos son PREVIOS a esta etapa y están en el commit `e248922`.** Verificado guardando los cambios con
  `git stash` y corriendo la suite limpia: **589 OK / 5 fallidos de 594**, los mismos 5 tests. Son los **4 goldens de
  contexto** (`AgentesOrganizacionTests`, `ConfiguradorReglasTests` ×2, `AsistenteDirectorTests`,
  `M14GoldenYPantallasTests`) fallando con hash distinto desde el carácter 0. Nada de M15 toca el render del contexto.
  **Queda como hallazgo para QA: la línea base real del repo no es 594/594.**

### Verificación en el portal (dev, MODELO SIMULADO confirmado en el log de arranque)
- `contable`: 2 organizaciones (Contadores BMA y Estudio Contable Demo), las dos vigentes al 16/09/2027; 10 agentes,
  6 reglas sugeridas y 8 materiales, todos publicados, 0 pendientes.
- `plataforma`: "Ninguna todavía" con la explicación de que es el rubro técnico y no se licencia; 1 versión esperando
  publicación (es PA-13, el configurador v2 en Borrador).
- `inmobiliario`, `estudio-software`: 200. Slug inexistente: 404.
- Un Director de cliente (`socio@contable.test`) sobre `/Nucleo` recibe **403 Acceso denegado**.
- Mobile 390: `scrollWidth == clientWidth` (385/385), **sin scroll horizontal de página**. Tema oscuro verificado.
- **Cero `<form>` dentro de `<main>`** en los 4 rubros: el único formulario de la página es el logout del layout.

### Riesgos y supuestos
- La lista de organizaciones es de **todos los tenants por diseño**. Si alguna vez una policy de cliente llegara a esta
  acción, mostraría datos de otras organizaciones. Hoy lo corta `[Authorize(Policy = "RequireAdministracion")]` a nivel
  de controller (y sigue abierto PA-22: confirmar si el backoffice debería exigir `RequireSuperUsuario`).
- Rendimiento: la consulta trae todas las licencias del rubro y agrupa en memoria. Con miles de licencias habría que
  agrupar en SQL. Hoy son decenas.
- `Nucleo/Index` sigue sin una columna de organizaciones: para saber quién usa un rubro hay que entrar a su ficha.
  Deliberado (era eso o una segunda consulta cross-tenant en el listado); anotado como mejora.
- `Clientes/Details.cshtml` mantiene su propio `if/else` de estado de licencia (DI-M15-6).

### Pruebas minimas para QA
1. Entrar como SuperUsuario a Núcleo IP → Contable y verificar contra la base: organizaciones con el rubro habilitado,
   estado y fecha de vencimiento de cada licencia, y el total del encabezado.
2. Revocar una licencia de una organización que tenga el rubro y recargar: la fila tiene que pasar a **Revocada** y caer
   al final de la tabla.
3. Una organización con dos licencias del mismo rubro (una vencida y una vigente): **una sola fila**, estado Vigente y
   "2 licencias incluyen el rubro".
4. Rubro `plataforma`: lista vacía con la explicación de que no se licencia.
5. Entrar con un usuario de cliente a `/Nucleo/Rubro/contable`: **403**.
6. Mobile 390 y tema oscuro: sin scroll horizontal de página, badges legibles, ningún enum crudo en pantalla.
7. Confirmar que **no hay ninguna acción de escritura**: ni alta, ni edición, ni baja de rubros desde el portal.

### Checklist de salida para merge
- [x] Build 0 errores, advertencias iguales a la línea base.
- [x] Tests nuevos verdes; los fallos restantes probados como preexistentes.
- [x] Sin migración EF.
- [x] Solo lectura verificada en el HTML servido.
- [x] Policy `RequireAdministracion` heredada del controller; 403 probado con usuario de cliente.
- [x] `IgnoreQueryFilters` por nombre y con comentario que dice por qué.
- [x] Mobile 390 y tema oscuro.
- [x] `Mcp` y `Cli` sin tocar. Sin commits.


# D-M14-8 + PA-37 (el configurador propone instructivos) y PA-38 (el visto, por persona)

Estado: **implementado 2026-09-17, pendiente de QA**. Entrada: `metadata.md` (PA-37, PA-38), `6-qa.md` → QA M14
(DEF-M14-5 y DEF-M14-9) y `2-disenador-funcional.md` M14 (D-M14-8). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`,
commit base `78ac1f8`. **Dos migraciones EF: `PropuestaInstructivo` y `VistoPorPersona` (esta última CON DATOS).**
**Ninguna llamada a la API real, sin commits.** `Mcp` y `Cli` sin tocar.

Las dos eran las deudas que M14 dejó anotadas y que Joaquín aprobó cerrar juntas. La primera tenía un orden obligatorio:
**el dispositivo antes que la guarda.** Si se cerraba el alta de reglas de tipo `Procedimiento` antes de darle al
configurador dónde poner los pasos, su propuesta empezaba a fallar **en la cara del Director sin que él hubiera hecho
nada mal**. Así que se hizo en tres pasos, en este orden: (a) la herramienta, (b) el prompt, (c) recién ahí la guarda.

### (a) La herramienta: `proponer_instructivo`

Se **reusa entero el circuito de tarjeta y botón de las propuestas de regla** (`PropuestaRegla` + `IPropuestaReglaService`
+ `_TarjetasPropuesta`), con un tipo nuevo `TipoPropuestaRegla.Instructivo`. No se armó un circuito paralelo: aplicar,
descartar, "Aplicar todas", "ya resuelta", el token de concurrencia y el éxito parcial ya estaban resueltos ahí y
duplicarlos era garantizar que se despeguen.

- **La herramienta valida con los mismos textos del formulario** (`MensajesInstructivos.TituloVacio`, `PasosVacios`,
  `LargoParaQueSirve`…). Están en castellano llano y no nombran ningún código, así que sirven igual para el modelo y para
  "Ver pasos": no hacen falta pares nuevos en `MotivosParaLaPersona` (PA-29).
- **Va siempre a toda la empresa.** El configurador configura la empresa, no las preferencias de nadie (el mismo criterio
  que ya tenía con las reglas, RF-M4b-09). Un instructivo "Solo yo" se carga desde su pantalla.
- **Al aplicarla se crea el instructivo en el MISMO guardado que la propuesta queda Aplicada**
  (`IInstructivoService.CrearAsync(dto, origen)`), con el mismo manejo de "otro Director la resolvió primero" que las
  reglas: `DbUpdateConcurrencyException` sobre `PropuestaRegla` → "ya resuelta" y el instructivo **no** se crea.
- **"Editar y aplicar"** abre el formulario de instructivos precargado (`Instructivos/Crear?propuesta=id`), no el de
  reglas: `DatosParaInstructivoAsync` es un método aparte y el formulario de instructivos **nunca** abre una propuesta de
  regla (404). Cancelar vuelve a la conversación con la propuesta todavía pendiente.

### (b) El prompt (`nucleo/plataforma/agentes/configurador-reglas.md`)

Sección nueva **"Regla o instructivo: la pregunta que desempata"**, con la misma frase que ya usa la pantalla (*¿esto vale
siempre, o solo cuando hago esta tarea?*), y se sacó la línea que mandaba a usar el tipo `procedimiento`. El prompt
**sigue sin publicar** (PA-13): se reimportó y quedó como **versión 2 en Borrador** (`#110`; la `#65` sigue ahí). Nada se
publicó. Los 4 goldens de contexto no se tocan: el test del configurador usa su propio texto de fixture, no este archivo.

### (c) La guarda, recién ahora (PA-37 / DEF-M14-5)

`ReglaService.CrearInternoAsync` rechaza `Tipo == Procedimiento` con `MensajesInstructivos.ProcedimientoNoSeCrea`, que
dice **qué hacer en su lugar** en vez de "valor inválido". Es **solo el alta**: una regla que ya es procedimiento se
sigue editando sin que le cambie el tipo en silencio (DI-M14-6), y las 4 que hay en dev quedan como están.

La guarda equivalente está además **antes**, en las dos herramientas de propuesta: `proponer_regla_nueva` y
`proponer_cambio_regla` ya no ofrecen `procedimiento` en su esquema y, si el modelo lo manda igual, contestan
`MensajesAlModelo.ProcedimientoEsInstructivo` —que nombra `proponer_instructivo` para que se corrija solo— con su par
redactado para la persona. **Esa es la razón del orden**: el Director no llega a ver una propuesta que después iba a
fallar.

### PA-38: el "visto" es de cada persona (DEF-M14-9)

`EjecucionProgramada.VistoAt`/`VistoPorId` se fueron; entra
**`EjecucionProgramadaVista (TenantId, EjecucionProgramadaId, UsuarioId, VistoAt)`** con índice único
`(EjecucionProgramadaId, UsuarioId)` —que es a la vez la garantía contra el doble marcado y el índice por el que entra el
contador— y `(TenantId, UsuarioId)`. La vuelta sigue siendo un registro inmutable: el visto **se le cuelga**, no la
modifica (mismo criterio que `AvisoGasto` con los períodos de M6).

- `MarcarVistoAsync` inserta una fila por persona; marcar dos veces (dos pestañas) **no es un error**: el resultado
  buscado ya está. Solo devuelve "no existe" cuando la vuelta no es visible para quien la pide.
- La bandeja y `ContadorResultadosViewComponent` preguntan por *lo que ESTA persona no vio*.
- El índice viejo `(ProgramacionTareaId, VistoAt)` pasó a `(ProgramacionTareaId, ResueltaAt)`, que es como se ordena la
  bandeja.

**La migración con datos** (`VistoPorPersona`, la primera del módulo) copia las dos columnas a filas **antes** de
borrarlas: crear la tabla → `INSERT … SELECT` → recién ahí `DROP COLUMN`. El `EXISTS` sobre `AspNetUsers` no es adorno:
una marca de un usuario que ya no está no entraría por la FK y haría fallar toda la migración. La vuelta atrás rehace las
columnas y copia **la primera persona que la vio** (el modelo viejo admite una sola).

### Archivo por archivo

**Domain.** `Enums/EnumsReglas.cs`: `TipoPropuestaRegla.Instructivo`. `Entities/PropuestaRegla.cs`: `ParaQueSirve` y
`ResultadoInstructivoId`/`ResultadoInstructivo`. `Entities/Programaciones.cs`: sale el visto de `EjecucionProgramada`,
entra `EjecucionProgramadaVista`.

**Application.** `DTOs/ConfiguradorDtos.cs`: `ParaQueSirve`, `ResultadoInstructivoId`, `EsInstructivo`,
`PuedeEditarYAplicar` con el tipo nuevo y `PropuestaInstructivoFormularioDto`. `DTOs/InstructivosDtos.cs`:
`ProcedimientoNoSeCrea` y `PropuestaRegistrada`. `Motor/MensajesAlModelo.cs`: `ProcedimientoEsInstructivo`.
`Interfaces/IInstructivoService.cs` (sobrecarga con `OrigenAplicacion`), `IPropuestaReglaService.cs`
(`DatosParaInstructivoAsync`), `IProgramaciones.cs` (el visto, por persona).

**Infrastructure.** `Services/Configurador/HerramientasConfigurador.cs`: `HerramientaProponerInstructivo` + las dos
guardas de `procedimiento` + `PideProcedimiento`. `Services/Configurador/PropuestaReglaService.cs`: proyección, aplicar y
`DatosParaInstructivoAsync`. `Services/Configurador/ResumenHerramientasConfigurador.cs` y `Services/Motor/MotivosParaLaPersona.cs`:
el rótulo llano y el par de la herramienta nueva. `Services/Instructivos/InstructivoService.cs`: alta con propuesta.
`Services/Reglas/ReglaService.cs`: la guarda del alta. `Services/Motor/ProveedorModeloSimulado.cs`: la segunda tarjeta
del guion es un instructivo (y **solo si la versión del configurador ofrece la herramienta**: con una vieja el motor la
rechazaría). `Services/Programaciones/ProgramacionTareaService.cs`: el visto por persona. Configuraciones EF y las dos
migraciones.

**Web.** `Controllers/InstructivosController.cs`: `Crear(propuesta)`, POST con `OrigenAplicacion` y vuelta a la
conversación. `Models/InstructivosViewModels.cs` + `Views/Instructivos/Form.cshtml`: los dos hidden, el aviso y Cancelar.
`Helpers/ConfiguradorTextos.cs` + `Views/Tareas/_TarjetasPropuesta.cshtml`: "Nuevo instructivo", *Para qué sirve* en vez
de *Dónde aplica*, "Ver instructivo" y el link de editar. `ViewComponents/ContadorResultadosViewComponent.cs`.

### Decisiones de implementacion

- **DI-P37-1 Se extendió `PropuestaRegla` en vez de crear `PropuestaInstructivo`.** Una tabla nueva obligaba a clonar
  tarjetas, acciones, permisos y concurrencia. Dos columnas nulas que solo usa un tipo son más baratas que dos circuitos
  que se despegan.
- **DI-P37-2 El tipo `procedimiento` se sigue LEYENDO aunque no se ofrezca.** Contestar "valor desconocido" no le diría
  al modelo que existe `proponer_instructivo`. Se lee para poder redirigir.
- **DI-P37-3 El configurador no puede leer los instructivos que ya existen.** No tiene `instructivos_listar` (es de
  tareas de trabajo). Si propone un título repetido, la tarjeta queda **"No se pudo aplicar: Ya hay un instructivo con
  ese título"** y se resuelve con *Editar y aplicar* cambiando el título — camino probado, no callejón. Sumarle la
  lectura es chico y queda **anotado como pendiente**.
- **DI-P38-1 Marcar algo ya visto devuelve éxito, no 404.** Lo que se pedía ya está; el 404 queda para la vuelta que esa
  persona no puede ver.
- **DI-P38-2 El helper de tests crea los procedimientos como dato, no por el servicio.** `EntornoReglas.CrearReglaAsync`
  los crea como regla común y les deja el tipo viejo en la base: es exactamente el dato que dejó el alta de antes de M14,
  que es lo que tienen los goldens y las 4 reglas de dev.

### Evidencia

`dotnet build OlvidataAgentes.slnx --no-incremental` → **0 errores, 2 advertencias** (las preexistentes:
`HomeController.StatusCode` y el `xUnit2013` de M7a). `dotnet test` → **594/594**. Línea base verificada contra el commit
`78ac1f8` en un worktree aparte: **587**; +6 tests nuevos y +1 caso que se suma solo al `[Theory]` del barrido de PA-29
(la herramienta nueva entra en la lista que se recorre). **Los 4 goldens de hash de contexto intactos**: el `git diff` de
`tests/` no toca una sola línea con `HashGolden`.

Migraciones aplicadas a `olvidata_agentes_dev` y **verificadas por SQL, ida y vuelta**: para poder probar la copia de
datos —en dev no había ningún resultado marcado— se simularon por SQL dos vistos (vueltas 8 y 19 de la org 1, marcadas
por `dira@qa.test`), se migró (**2 filas** en `EjecucionesProgramadasVistas` con su tenant, persona y fecha; columnas
viejas e índice borrados), se probó el `Down` (**las dos volvieron a las columnas** y la tabla desapareció) y se volvió a
aplicar. Después se borraron esas dos filas de prueba: **el entorno quedó como estaba** (0 vistos, 11 vueltas, 33
propuestas, 0 instructivos, 4 reglas `Procedimiento`, 154 tareas, 493 eventos). Organizaciones 1, 4, 18, 19 y 20 intactas.

Prompt reimportado: `1 versiones nuevas, 4 sin cambios`; configurador **#110, Numero 2, Borrador**; 51 versiones
publicadas, las mismas de antes. Portal levantado en Development con **MODELO SIMULADO confirmado** en el arranque.

### Pendientes que deja

- **El configurador sigue sin versión publicada (PA-13)**, así que *"Configurar conversando"* no está disponible en el
  portal: **este flujo no se puede recorrer en el navegador** hasta que Joaquín publique el prompt. Lo verificado son los
  tests.
- **`Anthropic:Simulado` no está en `appsettings.Development.json` (dice `false`) ni en los user-secrets**, donde sí está
  la API key real: el portal solo queda en simulado si se arranca con `Anthropic__Simulado=true`. El que estaba corriendo
  al empezar **no lo tenía**. Conviene fijarlo en dev.
- **DI-P37-3**: darle al configurador la lectura de los instructivos que ya existen.

# Correcciones de la QA de M14 (DEF-M14-1, 2, 4, 6, 7 y 12)

Estado: **corregido 2026-09-17**. Entrada: `6-qa.md` sección *QA M14* (commit `8394afa`, línea base 569 tests / 2
advertencias tras los 4 auto-fixes de QA). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.
**Sin migración, sin commits.** `Mcp` y `Cli` sin tocar. Costo cero: modelo simulado, ninguna llamada a la API real.

QA dictaminó que el vocabulario de M14 quedó impecable pero que **los tres dispositivos que actúan en el momento exacto
en que se comete el error de configuración llegaban rotos o a medias**. Eso —y no un defecto más— es lo que se corrigió:
sin esos tres, el criterio rector de Joaquín no se cumple aunque los 12 CA den PASS.

### Los tres major

- **DEF-M14-1 — "Convertirlo en instructivo" daba 404 siempre.** La raíz no era una guarda mal escrita sino **dos
  condiciones distintas para la misma acción**: la vista ofrecía el botón con `Tipo == Regla && ParecePasos(texto)`
  (la detección blanda de D-M14-6) y el servicio solo aceptaba `Tipo == Procedimiento` (la conversión de D-M14-1).
  El arreglo **unifica el criterio en un solo lugar**, `InstructivoService.EsConvertible`: se convierte un
  `Procedimiento` viejo **o** una regla común cuyo texto parece los pasos de una tarea — que es, literalmente, la misma
  condición que hace aparecer el botón. Así no pueden volver a separarse.
  `MensajesInstructivos.ConvertidoDesdeRegla` dejó de decir *"la regla de tipo procedimiento"* (falso en el caso nuevo)
  y ahora dice *"la regla que le dio origen"*, que sirve para los dos.
- **DEF-M14-2 — el aviso "Esto parece una regla" no aparecía al guardar.** Se copió el patrón que el lado de la regla ya
  tenía resuelto en el mismo commit: `InstructivosController.AvisarSiPareceRegla` marca `TempData["AvisoPareceRegla"]`
  en **las dos** salidas exitosas (alta y edición) y el detalle lo muestra con el parcial nuevo
  `Views/Shared/_AvisoPareceRegla.cshtml`, espejo exacto de `_AvisoPareceInstructivo`. Sigue sin bloquear: el
  instructivo ya quedó guardado y *"Dejarlo como instructivo"* es cerrar el aviso.
- **DEF-M14-6 — el informe de automatización podía mezclar organizaciones.** `TenantId` entra **en la clave del
  `GroupBy`**, no solo en la grilla: el informe corre con `IgnoreQueryFilters([FiltroTenant])` y el agente de Olvidata
  se llama igual en todas las organizaciones, así que agrupar por nombre hacía que dos empresas se leyeran como una
  sola gastando el doble. El grupo además **lleva el nombre de la organización** y la grilla tiene su columna, que es
  como se nota. Verificado por test y no por navegador, como pidió QA: reproducirlo a mano exigía crear agentes
  homónimos en organizaciones que hay que dejar intactas.

### Los minor cerrados

- **DEF-M14-4 — "Nueva regla" no pasaba por el desambiguador.** La pregunta de D-M14-5 pasó a
  `Views/Shared/_Desambiguador.cshtml`, **una sola vista para los dos botones** (dos copias se despegan con el tiempo),
  con `DesambiguadorViewModel`: lo único que cambia es cuál tarjeta viene destacada y a dónde va el salteo de un clic.
  `Reglas/Nueva` repite la guarda de permiso del formulario. Los botones contextuales ("Nueva regla para este
  agente / esta área / este cliente") **siguen yendo derecho**: ahí la persona ya eligió qué está configurando.
- **"Cargarlo como regla" mandaba a un formulario vacío.** El botón arrastra título y texto por la URL, y
  `ReglasController.Create` los precarga con tope (150 / 2.000 caracteres: una precarga que viene por la URL no puede
  pasar los topes del formulario). El aviso solo aparece con textos de hasta 200 caracteres, así que la URL nunca crece.
- **DEF-M14-7 — el dashboard abría "por canal" por transporte.** La apertura pasó a ser **para qué** fue la llamada
  (`MensajesUsoOlvidata.CanalFuncional`): Tareas, Configuración, Asistente, Evaluación de prompts, Búsqueda en
  internet, Licencias y Material del rubro. Las categorías son **disjuntas** a propósito, para que la suma de la
  apertura siga siendo exactamente el total de llamadas (verificado en el navegador: 455 = 455). Sigue siendo
  agregación sobre `EventoUso.Accion`, sin registro nuevo. Un solo ajuste en el camino de escritura:
  `ProcesadorTareas` nombra el paso según el tipo de tarea (`paso_configuracion` / `paso_asistente`), porque si no las
  vueltas del configurador y del asistente caían dentro de "Tareas" y el dashboard —que existe para saber en qué se
  gasta— habría atribuido mal la plata. **Las tareas de trabajo siguen siendo `paso_modelo`**, como todo lo ya
  registrado desde M1.
- **DEF-M14-12 — advertencia `CS8619`.** `InstructivosIndexViewModel.Filtros` pasó a `Dictionary<string, string>` con
  `OrdinalIgnoreCase`, que es lo que devuelve `FiltrosSesion.LeerTodos` y lo que usan los otros 8 ViewModels del repo.

### Archivo por archivo

**Application.** `DTOs/InstructivosDtos.cs`: `ConvertidoDesdeRegla` sirve para los dos caminos (+ comentarios de
`ConvertirReglaId` y `ReglaProcedimientoDto`). `DTOs/UsoOlvidataDtos.cs`: `GrupoAutomatizacionDto` suma `TenantId` y
`Organizacion`; `MensajesUsoOlvidata.CanalFuncional(accion, conBusqueda)` nuevo (`Canal(...)` queda, es el transporte).
`Interfaces/IInstructivoService.cs`: contrato de `ReglaParaConvertirAsync` al día.

**Infrastructure.** `Services/Instructivos/InstructivoService.cs`: `EsConvertible` + `ReglaConvertibleAsync`.
`Services/Uso/InformeAutomatizacion.cs`: `TenantId` en el `Select` y en la clave del `GroupBy`, `OrganizacionesAsync`.
`Services/Uso/DashboardUso.cs`: agrupa por `(TenantId, Accion, Busquedas > 0)` y traduce a la etiqueta en memoria.
`Services/Motor/ProcesadorTareas.cs`: `AccionDelPaso(tipo)`.

**Web.** `Controllers/InstructivosController.cs`: `AvisarSiPareceRegla` + `ClaveAvisoPareceRegla`, las dos salidas
exitosas, `Nuevo()` con el parcial compartido. `Controllers/ReglasController.cs`: `Nueva(alcance)` y la precarga
`titulo`/`texto` en `Create`. `Models/InstructivosViewModels.cs`: `DesambiguadorViewModel` y el tipo del diccionario de
filtros. Vistas: `Shared/_AvisoPareceRegla.cshtml` (nueva), `Shared/_Desambiguador.cshtml` (movida desde
`Instructivos/`, ahora con modelo), `Instructivos/Detalle.cshtml` (el aviso), `Instructivos/Form.cshtml` (el botón con
el texto), `Reglas/Index.cshtml` (el botón a `Nueva`), `Uso/Automatizar.cshtml` (columna Organización) y
`Uso/Index.cshtml` (el rótulo "Para qué").

### Lo que NO se tocó, a pedido de Joaquín

- **DEF-M14-5, el POST forzado con `Tipo=Procedimiento`.** El fix choca con el configurador de M4b, que hoy propone
  procedimientos; se resuelve junto con su prompt, que sigue sin publicar (PA-13, D-M14-8).
- **DEF-M14-9, el "visto" por persona.** Es la deuda aceptada en Arquitectura; queda dicho el costo, no implementado.

### Evidencia

`dotnet build OlvidataAgentes.slnx --no-incremental` → **0 errores, 2 advertencias** (las preexistentes:
`HomeController.StatusCode` y el `xUnit2013` de M7a); la `CS8619` de M14 desapareció. `dotnet test` → **587/587**
(569 de línea base + 18 nuevos). **Los 4 goldens de hash de contexto intactos** (las constantes no se tocaron: el
`git diff` de `tests/` no cambia una sola línea con `HashGolden`). Verificación en el navegador con el portal en
Development y **MODELO SIMULADO** confirmado en el arranque, como Director de la org 1 y como SuperUsuario: la regla
común con pasos numerados guardada → aviso → *Convertirlo en instructivo* abre el formulario precargado (200, no 404) →
al guardar queda el instructivo y la regla en **Inactiva** con su evento `Desactivada`; el instructivo de una sola
oración muestra el aviso **en el detalle, al guardar** (en alta y en edición), una sola vez, y su botón abre el
formulario de regla ya escrito; el informe de automatización con la columna **Organización**; el dashboard con la
apertura *Para qué* (Tareas 432 · Asistente 11 · Configuración 10 · Licencias 1 · Material del rubro 1 = **455**, el
total exacto de la organización). **Entorno restaurado y verificado por SQL**: 0 instructivos, 154 tareas, 493 eventos
con `Busquedas = 0` y `CostoUsd = 0`, 4 reglas `Procedimiento`, ninguna regla `FIX-M14` — exactamente como lo dejó QA.

### Pendientes que siguen abiertos

- **DEF-M14-5** y **DEF-M14-9**, arriba, esperando decisión de Joaquín.
- **DEF-M14-3, 8, 10 y 11** ya los cerró QA con auto-fix en el commit `8394afa`.
- La apertura *Para qué* de los eventos **ya registrados** antes de este cambio cuenta los pasos del configurador y del
  asistente dentro de "Tareas": no se reescribe el histórico (los eventos son append-only). Se corrige solo hacia
  adelante, y las conversaciones se siguen viendo por sus eventos de inicio.

# M14 — Instructivos, búsqueda web, espacio del cliente y control de gasto

Estado: **implementado 2026-09-17, QA cerrada; los defectos abiertos de QA se corrigieron en la sección de arriba**. Entrada: `1-analista-funcional.md` M14 (RF-M14-01..33, 12 CA,
R-M14-01..06), `2-disenador-funcional.md` M14 (D-M14-1..8, P-M14-01..10) y `3-arquitecto-mvc.md` M14 (RT-M14-01..06).
Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. **Una migración: `InstructivosM14`.**
**Ninguna llamada a la API real de Anthropic, ninguna salida a internet, sin commits.** `Mcp` y `Cli` sin tocar.

Criterio rector de Joaquín: *"que esto sea totalmente entendible para el usuario, explicando qué es cada cosa para no
cometer errores de configuración"*. Ante dos implementaciones posibles se eligió siempre la que deja más claro **cuándo
se usa cada cosa**.

### Escaneo de reutilizacion

| Fuente | Que se tomo | Grado |
|---|---|---|
| M10 `HerramientasConocimiento` | La forma entera de una familia de herramientas de solo lectura: clase base con las guardas, "no está disponible" como única respuesta para todo lo que no corresponde, aviso fijo en cada resultado y resumidor propio para "Ver pasos". `HerramientasInstructivos` es esa pieza con otra fuente de datos | Literal (patrón) |
| M4 `AgenteOrganizacion` | `VisibilidadAgente` (`SoloYo` / `TodaLaEmpresa`) **se reusa, no se clona**: es la misma decisión de producto y el usuario ya la conoce con esas palabras. También el `VersionToken` como token de concurrencia y el criterio de permisos (cualquiera crea los suyos, el Director los de la empresa) | Literal |
| M3 `Regla` / `ReglaEvento` | El versionado: versión vigente en la entidad + historial inmutable con los campos que cambiaron; activar/desactivar **no** versiona | Literal (patrón) |
| M2/M4/M11 columna generada `*Vigente` | Unicidad entre los vigentes con columna generada STORED + índice único, y la migración escrita a mano porque el proveedor ignora `stored: true` | Literal (cuarta vez) |
| M6 `AvisoGasto` / M12 `EjecucionProgramada` | Cómo se cuelga un dato nuevo de un registro inmutable sin tocar su ciclo de vida (el "visto" de los resultados) | Literal (criterio) |
| M8 gate de corridas reales | **Fail-closed por precio**: sin precio configurado la función no se ofrece. Es el mismo criterio, aplicado a la búsqueda web | Literal (criterio) |
| M7b `ContadorAsignaciones` | El contador del ítem del menú (COUNT indexado por request, sin contador si es 0) | Literal |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún otro proyecto del estudio tiene instructivos, búsqueda web del proveedor ni informe de repetición de pedidos. Lo más cercano son ABMs versionados de textos, que ya están cubiertos por M3/M4 dentro de este mismo repo | Sin match |

### Que se hizo, archivo por archivo

**Domain.** `Entities/Instructivos.cs` (nuevo): `Instructivo` (`SoftDestroyable`, `ITenantOwned`) e `InstructivoVersion`.
`Entities/Tareas.cs`: `TareaAgente.PermiteBusquedaWeb`. `Entities/Programaciones.cs`: `EjecucionProgramada.VistoAt` y
`VistoPorId`. `Entities/Uso.cs`: `EventoUso.Busquedas`.

**Application.** `DTOs/InstructivosDtos.cs` (nuevo) con los DTOs, `MensajesInstructivos`, **`TextosConceptos`** (la tabla
canónica de los cuatro conceptos de D-M14-3, que no se reescribe en ninguna pantalla) y **`DeteccionInstructivo`** (la
detección blanda de D-M14-6, en los dos sentidos). `DTOs/UsoOlvidataDtos.cs` (nuevo): dashboard e informe.
`DTOs/ProgramacionesDtos.cs`: bandeja de resultados. `Interfaces/IInstructivoService.cs` e `Interfaces/IUsoOlvidata.cs`
(nuevos). `Settings/InstructivosOptions.cs` y `Settings/BusquedaWebOptions.cs` (nuevos). `Helpers/HashPedido.cs` (nuevo).
`Motor/NombresHerramientasInstructivos.cs` (nuevo). `Motor/ModeloConversacion.cs`: dos bloques nuevos
(`BloqueBusquedaWeb`, `BloqueResultadoBusquedaWeb` con sus `FuenteWeb`), `SolicitudModelo.BusquedaWeb`,
`RespuestaModelo.Busquedas` y `MotivoFin.PausaTurno`. `Motor/IMotorAgentes.cs`: `PasoVisibleDto.Busquedas`,
`BusquedaWebVistaDto`, la casilla en `CrearTareaDto` y la sobrecarga de `EnviarSeguimientoAsync`.

**Infrastructure.** `Services/Instructivos/InstructivoService.cs` y `Services/Instructivos/HerramientasInstructivos.cs`
(nuevos). `Services/Uso/DashboardUso.cs` e `Services/Uso/InformeAutomatizacion.cs` (nuevos).
`Services/Motor/ProveedorModeloAnthropic.cs`: mapeo de la herramienta del proveedor y de sus bloques, en los dos
sentidos, más el conteo de búsquedas de `usage.server_tool_use`. `Services/Motor/ProcesadorTareas.cs`: oferta de las
herramientas de instructivos, decisión de búsqueda web, costo y `pause_turn`. `Services/Motor/ProveedorModeloSimulado.cs`:
dos guiones nuevos. `Services/Motor/ResumenPasos.cs`: instructivos en la cadena y `Busquedas(...)`.
`Services/Motor/ServicioTareas.cs` y `Services/Motor/PreparadorTareaTrabajo.cs`: la marca de búsqueda.
`Services/Programaciones/ProgramacionTareaService.cs`: bandeja de resultados. `Data/Configurations/InstructivosConfigurations.cs`
(nuevo) y la migración `20260917150924_InstructivosM14`.

**Web.** `Controllers/InstructivosController.cs` + `Views/Instructivos/{Index,Form,Detalle,_Desambiguador}.cshtml`,
`Views/Shared/_ConceptosAyuda.cshtml` y `Views/Shared/_AvisoPareceInstructivo.cshtml` (nuevos).
`CarteraController.Espacio` + `Views/Cartera/Espacio.cshtml`. `ProgramacionesController.Resultados` / `MarcarVisto` +
`Views/Programaciones/Resultados.cshtml` + `ContadorResultadosViewComponent`. `UsoController` (cards + `Automatizar`) +
`Views/Uso/Automatizar.cshtml`. Ajustes: `Reglas/_Form.cshtml` (el combo), `Reglas/Detalle.cshtml` e `Index.cshtml` (los
avisos y la bajada), `ReglasController` (detección blanda al guardar), `Agentes/Ejecutar` y `Tareas/_CuadroSeguimiento`
(la casilla), `Tareas/_PasosTurno.cshtml` (las búsquedas con sus fuentes) y `_Layout.cshtml` (Instructivos y Resultados).

### Decisiones de implementacion (ambiguedades resueltas)

- **DI-M14-1 El contenido de las páginas que vuelven de la búsqueda no se puede mostrar.** Verificado contra el SDK: cada
  fuente trae `title`, `url`, `page_age` y **`encrypted_content`**, que es opaco. Se guarda para poder reenviar el turno y
  nunca se muestra. Consecuencia sobre P-M14-06: *"Ver lo que trajo"* despliega **las fuentes citadas**, no el texto de la
  página. Se mantiene el rótulo *"Información de internet: puede estar equivocada o desactualizada"* y el escapado, porque
  el título y la URL también vienen de internet. `FuenteWeb.Extracto` queda para los proveedores que sí devuelven texto
  (hoy, el modelo simulado de QA).
- **DI-M14-2 El `type` de la herramienta se toma del SDK, no de la configuración.** `BusquedaWeb:TipoHerramienta` solo
  puede pedir una versión **conocida**; un valor desconocido se ignora y se usa la del SDK. Nunca se arma un `type` a
  mano: es exactamente el error que RT-M14-01 manda evitar.
- **DI-M14-3 La búsqueda no lleva una segunda compuerta de gasto.** El motor ya verifica el límite antes de **cada**
  llamada (RF-M6-08): con el límite alcanzado no llama al modelo y por lo tanto no hay búsqueda. Agregar otra compuerta
  sería una segunda verdad sobre lo mismo.
- **DI-M14-4 El costo de la búsqueda se suma al `PasoTarea`, no solo al `EventoUso`.** El control de gasto de M6 suma
  `PasoTarea.CostoUsd`; poner el costo solo en el evento lo habría dejado fuera del límite. Un solo número, en los dos
  lados.
- **DI-M14-5 Solo se cuentan búsquedas si esa llamada las ofrecía.** Si la tarea no tenía la casilla, un proveedor que
  informe búsquedas no puede inventar costo.
- **DI-M14-6 El tipo `Procedimiento` sigue visible en el combo de una regla que ya lo tiene.** Sacarlo del todo le
  cambiaría el tipo en silencio al editarla. En un alta no aparece nunca, y hay test que lo verifica.
- **DI-M14-7 La detección blanda de la regla aparece DESPUÉS de guardar.** La regla queda guardada y el aviso ofrece
  convertirla; *"Dejarlo como regla"* es cerrar el aviso. Así se cumple *"nunca bloquea"* al pie de la letra.
- **DI-M14-8 El espacio del cliente no tiene ni un `<form>`.** Es la forma más barata de garantizar "no se escribe nada
  desde acá", y el test lo verifica sobre la vista.
- **DI-M14-9 `pause_turn` se maneja en el bucle del motor.** Es el único estado nuevo que puede devolver el proveedor
  cuando corre su propia herramienta: se reenvía la conversación y sigue donde quedó, acotado por el máximo de pasos del
  turno como cualquier otra vuelta.

### Evidencia

`dotnet build OlvidataAgentes.slnx` 0 errores / 2 advertencias preexistentes. `dotnet test` **569/569** (509 de línea base
+ 60 nuevos: `InstructivosTests`, `BusquedaWebTests`, `M14GoldenYPantallasTests`). **Los 4 goldens de hash de contexto,
intactos**, con instructivos cargados y con la búsqueda encendida; el test nuevo además compara el prompt de sistema byte
a byte entre la tarea con y sin las herramientas. Migración aplicada a `olvidata_agentes_dev`: `TituloVigente` verificada
como `STORED GENERATED` y el índice único `(TenantId, TituloVigente)` creado. Organizaciones 1, 4, 18, 19 y 20 intactas
(154 tareas con `PermiteBusquedaWeb = 0`, 493 eventos con `Busquedas = 0`). Recorrido en el navegador con el modelo
simulado: instructivos, desambiguador, formulario, resultados, espacio del cliente (org 19), dashboard (493 llamadas,
que es exactamente el conteo de filas de `EventoUso`), informe de automatización y una tarea con búsqueda de punta a
punta — 1 búsqueda, USD 0,01 en el paso y en el evento, fuentes enlazables con `rel="noopener noreferrer nofollow"`.
La tarea de humo se borró para dejar la demo del tenant 19 como estaba.

### Lo que queda pendiente

- **Verificar el precio por búsqueda de Anthropic** antes de facturar. Mientras `BusquedaWeb:PrecioPorBusquedaUsd` sea
  `null`, la función queda apagada en producción (fail-closed). En Development hay un precio de prueba de USD 0,01.
- **El camino del proveedor real nunca se ejecutó** (decisión de costo, PA-18/PA-02): lo verificado es el del modelo
  simulado, que reproduce los mismos bloques.
- **D-M14-8 (el configurador propone instructivos) quedó fuera de esta entrega**: requiere tocar el prompt del
  configurador de M4b, que sigue sin publicar (PA-13), y conviene hacerlo antes de publicarlo, no después.
- **Deuda anotada**: el "visto" de los resultados es del registro y no por persona.

# Cinco pendientes abiertos: PA-35, PA-34, PA-33, PA-29 y el `catch` mudo del importador

Estado: **implementados 2026-09-16, pendientes de QA**. Entrada: `metadata.md` (PA-29/33/34/35), `6-qa.md` → ronda 2
(DEF-R2-1 / OLV-014) y la seccion de abajo del escenario BMA (DEF-BMA-1/2/3). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.
**Sin migracion EF** (el unico tipo nuevo, `TipoDocumento.TablaHtml`, es un valor mas en una columna `int` que ya existe).
**Ninguna llamada a la API real de Anthropic, ninguna salida a internet, sin commits.** `Mcp` y `Cli` sin tocar.

### Escaneo de reutilizacion
| Fuente | Que se tomo | Grado |
|---|---|---|
| Template M5 `ExtractorPlanilla` (.xlsx) | La forma de una tabla leida por partes: una celda por columna separada por tabulador, bloques de `FilasPorParte` filas con el encabezado repetido y el rotulo "…, filas 1–200". `ExtractorHtml` es la misma pieza con otra fuente de datos | Literal (patron) |
| Template M5 `AcumuladorPartes` | El acumulador con tope de caracteres; se le sumo un segundo motivo de "lee solo una parte" sin tocar el existente | Literal |
| Template M5 `ValidadorContenidoArchivo` | La estructura "extension + contenido real": PA-35 agrega una rama, no un camino paralelo | Literal |
| Correcciones ronda 1 `ResumenPasos` (DI-R1-1) | "Nunca llega texto tecnico a la pantalla", y el lugar unico donde se decide. PA-29 aplica exactamente ese criterio a la rama de error | Literal (criterio) |
| PdfPig 0.1.16 (ya instalada) | `Page.GetWords()` con `BoundingBox` y `Letter.StartBaseLine`: **no hizo falta cambiar de biblioteca** para PA-33 | Literal |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningun otro proyecto del estudio lee PDF ni HTML para un modelo. Lo mas cercano son importadores de Excel de CRM, que leen un formato fijo con ClosedXML y no tienen el problema de la estructura | Sin match |
| Escaneo `docs/patrones/catalogo.yml` | PAT-033 (rotulos llanos) ya cubre PA-29 como criterio; esto lo extiende a la rama de error. Nada cubre extraccion de documentos | Sin patron nuevo |

### Que se hizo

1. **PA-35 — los exports de sistemas contables entran (cierra DEF-BMA-1).** Un `.xls` (o `.doc`) ya **no se rechaza por la
   extension**: decide el contenido. Si adentro hay una tabla HTML — lo que exportan SOS Contador y companhia — entra como
   `TipoDocumento.TablaHtml` ("Tabla web") y se lee **como tabla**: `ExtractorHtml` arma una fila por renglon con las celdas
   separadas por tabulador, en bloques de `FilasPorParte` con el encabezado de columnas repetido. El encabezado se detecta
   como la primera de las diez primeras filas que tiene tantas columnas como la mas ancha de ellas, porque en un export
   contable las primeras filas son el titulo y el periodo. Tambien se aceptan `.html` y `.htm`.
   Si el `.xls` **si** es un Excel viejo binario, el mensaje ahora describe el problema:
   *"Este archivo es un Excel viejo (.xls) y no se puede leer. Abrilo con Excel y usa «Guardar como» .xlsx. **Cambiarle el
   nombre al archivo no alcanza: se revisa el contenido.**"*
2. **Nada de HTML activo (la mitad de seguridad de PA-35).** `HtmlDeTablas` es un lector de **solo texto**: descarta
   `script`, `style`, `iframe`, `object`, `embed`, `svg`, `applet`, `noscript`, `template`, `frameset`, `head`, `title`,
   `canvas` y `math` **con su contenido adentro**, no lee **ningun atributo** (asi que un `src`, un `onclick` o una URL no
   tienen por donde llegar), resuelve entidades con `WebUtility.HtmlDecode` y no resuelve nada remoto: es recorrer una
   cadena. Ademas lo guardado **nunca se sirve como HTML**: `TipoContenidoHtml` es `text/plain` y la descarga ya era
   siempre adjunto, con `X-Content-Type-Options: nosniff` global.
3. **PA-33 — el PDF conserva los renglones (cierra DEF-BMA-2).** `TextoPdfPorRenglones` reemplaza a
   `ContentOrderTextExtractor` como primera opcion: agrupa las palabras por **linea de base** (la de su primera letra, no el
   borde inferior de la caja, que baja con las colas) con tolerancia de 0,45 altos de letra, ordena cada renglon de
   izquierda a derecha y marca **salto de columna con un tabulador** cuando el hueco supera 2,5 anchos de caracter del
   renglon. Dos renglones separados por mas de 1,9 altos de letra dejan una linea en blanco. Si esa lectura falla se cae al
   extractor de siempre y, ultimo recurso, al texto crudo: **ninguna pagina se pierde por esto**.
4. **PA-34 — las paginas sin texto se avisan (cierra el hallazgo suelto del escenario BMA).** `ExtractorPdf` junta las
   paginas que no dieron texto y deja el documento en **"El agente lee solo una parte"** con el motivo redactado
   (`MensajesDocumentos.PaginasSinTexto`, acotado a los 300 caracteres de `MotivoNoLegible`). Se ve en los cuatro lugares:
   el mensaje de la subida, el tooltip de la grilla, el cartel del detalle y — lo que faltaba — **el agente**:
   `documentos_listar` dice *"se puede leer solo una parte (la pagina 8 de 12 no tiene texto…)"* en vez del falso "el
   documento es muy largo", y `documento_leer` devuelve `falta_del_documento`. `TextoRecortado` sigue siendo **solo** el
   recorte por largo: son dos motivos distintos y se muestran distinto (o los dos juntos).
5. **PA-29 / OLV-014 — dos textos por error.** `MensajesAlModelo` (Application) junta los mensajes de error que llevan el
   detalle tecnico que el agente necesita para corregirse; `MotivosParaLaPersona` (Infrastructure) tiene, al lado de cada
   uno, **el texto que lee la persona**. `ResumenPasos.Resultado` traduce en la rama de error, en **un solo lugar**, para
   las seis familias a la vez. Ejemplo del disparador de QA: *"…: la propuesta no cambia nada de la regla. Indica el titulo,
   el texto, el modo, el tipo o las etiquetas nuevos"* → **"…: la propuesta no cambiaba nada de la regla"**.
   Hay una **segunda capa mecanica**: si un mensaje sin par redactado nombra una herramienta o un codigo interno
   (lista cerrada armada con los `Nombres*` de todas las familias + los codigos de argumento y de alcance), **no se muestra**
   y sale un generico. Un mensaje que ya esta en castellano llano pasa tal cual, que es el caso de la mayoria.
6. **El `catch` mudo del importador.** `SepararFrontmatter` devuelve ahora `ErrorFrontmatter` y `ImportarAsync` lo suma a
   las advertencias con **el archivo y el motivo**: *"El front matter de 'cont-sueldos.md' no es YAML valido (…): se importo
   el cuerpo, pero 'cont-sueldos' queda sin nombre, sin descripcion y sin herramientas. Revisa las comillas…"*. Ademas la
   metadata a medias se **descarta entera** (`meta.Clear()`) en vez de quedar con lo que YamlDotNet alcanzo a leer.

### Decisiones de implementacion (ambiguedades resueltas)
- **DI-PA35-1 Un `.xls` que es HTML **sin** `<table>` se rechaza igual.** Se exige la tabla para la extension de Office
  viejo, porque "esto en realidad es una pagina web" no es lo que el usuario cree que subio. Para `.html`/`.htm` alcanza con
  que sea HTML: ahi el usuario sabe lo que esta subiendo.
- **DI-PA35-2 `TipoDocumento.TablaHtml` nuevo en vez de reusar `Planilla`.** Reusar `Planilla` habria evitado tocar el enum,
  pero la validacion de `Planilla` exige ZIP y habria que sniffear dos veces; y en pantalla decir "Excel" de algo que no lo
  es es justo el malentendido que origino PA-35. Los filtros de las dos grillas recorren `Enum.GetValues<TipoDocumento>()`,
  asi que la opcion "Tabla web" aparecio sola. **Sin migracion**: la columna ya es `int`.
- **DI-PA33-1 Tabulador para la columna, no relleno con espacios.** La alternativa era emular `pdftotext -layout` y rellenar
  con espacios para conservar la alineacion; asi, **de que columna es un importe** se recuperaria por posicion. Se descarto:
  "se distinguen por cantidad de espacios" es justamente lo que QA marco como material peligroso, y el relleno vuelve a
  depender de contar espacios. **Costo asumido y explicito: con un tabulador, un renglon con la columna DEBITO vacia no
  marca cual de las dos es.** Eso lo resuelve PA-36 (el cruce hecho en codigo), no la extraccion.
- **DI-PA33-2 No se cambio de biblioteca.** PdfPig 0.1.16 ya expone lo necesario. Verificado contra los cinco extractos
  reales: el **multiconjunto de caracteres sin espacios es identico** al del extractor viejo, pagina por pagina — no se
  pierde ni se inventa nada, solo cambia donde se corta.
- **DI-PA33-3 Un documento a dos columnas se leeria entrelazado.** Agrupar por coordenada vertical junta las dos columnas de
  una pagina a dos columnas en un mismo renglon. No se agrego deteccion de columnas (XY-cut) porque agrega mas modos de
  falla que los que resuelve, y los documentos del caso — extractos, mayores, facturas, contratos — son de una sola columna.
  El tabulador deja el corte visible, asi que el caso es recuperable a ojo.
- **DI-PA34-1 "Lee solo una parte" con motivo, en vez de un estado nuevo.** Se evaluo un `LegibleConFaltantes`. Se descarto:
  el estado que ya existe dice exactamente eso y ya tiene sus textos, su icono y su color; lo que faltaba era **el porque**.
- **DI-PA29-1 Se traduce al mostrar, no se guarda una segunda columna.** La alternativa (que `ResultadoHerramienta` llevara
  los dos textos y `EjecucionHerramienta` guardara el de la persona) necesitaba migracion y **solo habria arreglado los pasos
  futuros**. Traducir al mostrar arregla tambien los que ya estan en la base: verificado sobre la conversacion **#187**, la
  que uso QA para reportar el defecto, sin tocar un solo dato.
- **DI-PA29-2 La red de seguridad mira una lista cerrada, no `snake_case` generico.** Un patron generico de guion bajo
  borraria mensajes legitimos (el nombre de un documento o el codigo de una conexion pueden tener guiones bajos). La lista
  cerrada de nombres de herramienta y codigos de argumento no tiene falsos positivos.

### Archivos tocados
| Archivo | Que |
|---|---|
| `src/…Domain/Enums/EnumsDocumentos.cs` | `TipoDocumento.TablaHtml = 7` |
| `src/…Application/Helpers/NombreDocumentoHelper.cs` | `.html`/`.htm` en `Permitidas`, `TipoContenidoHtml`, `FormatosViejos` → **`OfficeViejo`** (ya no es "prohibido" sino "lo decide el contenido"), texto de permitidos y "Tabla web" |
| `src/…Application/DTOs/DocumentosDtos.cs` | `FormatoViejo(extension)` (era constante), `PaginasSinTexto(...)`, `SubidoParcial(partes, recortado, aviso)` |
| `src/…Application/Motor/MensajesAlModelo.cs` | **Nuevo.** Los mensajes de error escritos para el modelo, como constantes |
| `src/…Infrastructure/…/Documentos/Extractores/HtmlDeTablas.cs` | **Nuevo.** Lector de HTML de solo texto (tablas + texto suelto), sin HTML activo |
| `src/…Infrastructure/…/Documentos/Extractores/ExtractorHtml.cs` | **Nuevo.** Partes "Tabla, filas 1–200" con encabezado repetido |
| `src/…Infrastructure/…/Documentos/Extractores/TextoPdfPorRenglones.cs` | **Nuevo.** Renglones por linea de base y columnas por hueco (PA-33) |
| `src/…Infrastructure/…/Documentos/Extractores/ExtractorPdf.cs` | Usa el nuevo lector con respaldo; junta las paginas sin texto y arma el aviso (PA-34) |
| `src/…Infrastructure/…/Documentos/Extractores/ComunesExtraccion.cs` | `AcumuladorPartes.Resultado(motivoSinTexto, avisoFaltante)` |
| `src/…Infrastructure/…/Documentos/ValidadorContenidoArchivo.cs` | `.xls`/`.doc` por contenido; `ValidarHtml` |
| `src/…Infrastructure/…/Documentos/LectorDocumentos.cs` | Despacha `TablaHtml` |
| `src/…Infrastructure/…/Documentos/DocumentoCarteraService.cs` | Mensaje de subida con los dos motivos de "lee solo una parte" |
| `src/…Infrastructure/…/Documentos/HerramientasDocumentos.cs` | `LecturaParaAgente(estado, motivo)` y `falta_del_documento` en `documento_leer` |
| `src/…Infrastructure/Services/Motor/MotivosParaLaPersona.cs` | **Nuevo.** Los pares modelo→persona y la red de seguridad (PA-29) |
| `src/…Infrastructure/Services/Motor/ResumenPasos.cs` | Traduce la rama de error antes de pasarsela a los resumidores |
| `src/…Infrastructure/Services/Motor/ProcesadorTareas.cs` | "La herramienta 'X' no esta disponible" pasa a `MensajesAlModelo` |
| `src/…Infrastructure/Services/Configurador/HerramientasConfigurador.cs` · `Conocimiento/HerramientasConocimiento.cs` · `Conectores/HerramientasConectores.cs` · `Reglas/HerramientaProponerRegla.cs` | Los 14 mensajes pasan a constantes de `MensajesAlModelo` (mismo texto para el modelo) |
| `src/…Infrastructure/Services/Nucleo/ImportadorRubro.cs` | `SepararFrontmatter` devuelve el motivo; el import lo suma a las advertencias |
| `src/…Web/Helpers/DocumentosTextos.cs` | Icono de "Tabla web", `accept` con `.xls`/`.doc`, tooltip con el motivo |
| `src/…Web/Views/Documentos/Ver.cshtml` · `_ZonaSubida.cshtml` | Cartel con los dos motivos; el listado de formatos sale de `TiposArchivoDocumento` |
| `src/…Web/wwwroot/js/documentos.js` | El navegador ya no rechaza `.xls`/`.doc` (no puede mirar el contenido: lo decide el servidor); icono de `TablaHtml` |
| `tests/…/LectorDocumentosTests.cs` | 9 casos nuevos: tabla HTML, `.xls` binario, HTML activo, renglones del PDF, paginas sin texto |
| `tests/…/HerramientasDocumentosTests.cs` | 1 caso: el agente se entera de las paginas sin texto |
| `tests/…/ResumenPasosTests.cs` | 22 casos: los 14 mensajes + la red de seguridad + el texto llano que pasa tal cual |
| `tests/…/NucleoTests.cs` | 1 caso: front matter invalido avisa con archivo y motivo |
| `tests/…/DocumentosTests.cs` | El rechazo de `.doc` ahora usa un binario de Office de verdad |

### Evidencia
- `dotnet build OlvidataAgentes.slnx --no-incremental`: **0 errores, 2 advertencias** — las dos preexistentes de la linea
  base (`HomeController.StatusCode` y el `xUnit2013` de M7a). Las vistas compilan en el build.
- `dotnet test tests/OlvidataAgentes.Tests`: **509/509**. Linea base 478 + **31 nuevos**.
- **Los 4 goldens de hash de contexto intactos**: `HashGoldenCmPanaderia`, `HashGoldenTasadorFerreteria`,
  `HashGoldenFormato2/3` y `HashGoldenFormato4`. Los tres archivos que los contienen **no aparecen en el diff**. Tiene que
  ser asi: nada de esto toca el armado del contexto.
- **Verificacion contra los archivos reales** (no solo fixtures). Los 6 del escenario BMA, por el camino real del portal,
  al cliente 64 de la organizacion 20, con el modelo simulado:
  - **El `.xls` de SOS Contador entra**: "Documento subido. El agente lo puede leer.", tipo **Tabla web**, **93 filas** con
    Cuenta / Fecha / Comprobante / CUIT / Razon Social / Concepto / Debe / Haber / Saldo separadas por tabulador. La primera
    linea trae `Imputaciones Contables - CUIT 30-70823732-5 - <razon social>`: **el dato que el producto nunca habia podido
    leer**.
  - **Los 5 PDF**: primero dieron *"Este archivo ya esta cargado…"* (control de duplicado por hash, correcto). Se les dio de
    baja y se volvieron a subir: los 5 avisan **"Documento subido, pero no entero. La pagina 8 de N no tiene texto…"** con
    su N correcto (8, 10, 8, 12, 8) y quedan en "El agente lee solo una parte".
  - **Renglones**: el resumen de abril paso de **5 saltos de linea para 7.878 caracteres** (pagina 2) a **74 saltos**, con
    cada movimiento en su renglon. Total del archivo: 292 → **678 saltos**. Los otros cuatro, igual (105→473, 230→592,
    103→459, 103→459). **Sin perdida de contenido**: el multiconjunto de caracteres sin espacios es identico pagina por
    pagina en los 12/8/10/8/8 folios.
  - **El CUIT falso (DEF-BMA-3) queda a la vista como lo que es**: el encabezado ahora sale
    `AV 51 1111 CTRO 17` ⇥ `R.N.P.S.P.` ⇥ `CUIT 30-57142135-2`, con el tabulador mostrando que ese CUIT viene de otra
    columna. **No desaparece del renglon del titular**: sigue siendo material que hay que mirar antes de creerle.
- **PA-29 verificado sobre el dato real de QA**: `/Tareas/Detalle/187` — la conversacion con la que QA reporto OLV-014 —
  ahora muestra **"No pudo registrar la propuesta: la propuesta no cambiaba nada de la regla"**, sin tocar la base.
- **Costo cero**: portal con `Anthropic__Simulado=true` (advertencia "MODELO SIMULADO … el costo es cero" en el arranque),
  `anthropic.com` en el log del dia = **0**, y **ningun `EventoUso` nuevo** (el ultimo del tenant 20 es de la sesion
  anterior; todos los tenants siguen en USD 0,000000).
- **Nada del cliente llego al repositorio**: los archivos se copiaron a `.playwright-mcp/` (gitignorado) y se borraron al
  terminar; `git grep` de `credicoop|nefroexcel|70823732|57142135` sobre el repo = **0 archivos**. El fixture del test es
  equivalente pero inventado, y lo dice en su comentario.

### Lo que cambio en la base de desarrollo (para que QA no se sorprenda)
Organizacion **20 (`contadores-bma`), cliente 64**: los 5 documentos originales (ids 63–67) quedaron **dados de baja** y se
volvieron a subir con la extraccion nueva (ids **69–73**), mas el `.xls` (id **68**). Fue la unica forma de volver a subirlos:
el control de duplicado por hash los rechaza mientras el original este vigente. Las tareas #202/#203 **conservan lo que
leyeron** (el propio dialogo de baja lo dice). La organizacion 19 y las demas no se tocaron.

### Pruebas minimas para QA
1. **PA-35, lo central.** Subir un `.xls` que sea una tabla HTML (o el del escenario BMA) → tiene que entrar como
   **"Tabla web"** y en "Lo que el agente puede leer" las columnas tienen que verse separadas, no pegadas. Subir un `.xls`
   binario de verdad (guardado con Excel como "Libro de Excel 97-2003") → rechazo con el mensaje que dice que **renombrarlo
   no alcanza**. Confirmar por SQL que el rechazado **no deja fila** en `DocumentosCartera`.
2. **PA-35, seguridad.** Un `.html` con `<script>alert(1)</script>`, `<style>`, `<iframe src=…>`, `onclick=` y
   `<img src="http://…">` → nada de eso puede aparecer en el texto extraido, **no puede haber ninguna peticion de red** al
   ver el documento (pestania Red del inspector) y la descarga tiene que bajar como archivo, nunca abrirse como pagina.
3. **PA-33.** Un PDF de extracto bancario o de factura con tabla → cada movimiento en **su renglon**. Contar los saltos de
   linea de una parte y compararlos con la cantidad de movimientos de esa pagina. Verificar tambien un PDF **de texto
   corrido** (un contrato) para que no se haya roto lo que ya andaba.
4. **PA-34.** Un PDF con una pagina escaneada en el medio → "El agente lee solo una parte" + el aviso con el numero de
   pagina, en el mensaje de subida, en el tooltip de la grilla y en el detalle. Y **desde el agente**: una tarea con ese
   documento adjunto, "Ver pasos" → la lista tiene que decir el motivo real, no "el documento es muy largo".
5. **PA-29, con el modelo real (es lo unico que lo alcanza).** El disparador esta en `regresiones-manuales.yml` → OLV-014.
   Barrido sobre el texto visible de un paso fallido: **0** apariciones de `equipo_listar`, `estructura_empresa`,
   `clientes_buscar`, `regla_obtener`, `agentes_disponibles`, `cliente_agente`, `mis_preferencias`, `salvo_indicacion`,
   `regla_id`, `sugerencia_id`, `documento_id`, `fragmento_id`. **Y la contracara:** que el modelo siga recibiendo el
   mensaje tecnico — mirar `EjecucionesHerramienta.Resultado` en la base, que **no cambio**.
6. **PA-29, sin modelo real.** `/Tareas/Detalle/187` (organizacion 1) tiene que decir *"…: la propuesta no cambiaba nada de
   la regla"*, sin la instruccion al agente.
7. **El importador.** Poner un `description:` con `:` adentro y sin comillas en un `.md` del nucleo y correr
   `Admin -- importar` → la salida tiene que traer la advertencia con **el archivo y el motivo**, y el artefacto queda sin
   nombre/descripcion/herramientas (que es lo que ya pasaba, pero ahora se ve). Volver a entrecomillar y reimportar: sin
   advertencias y **sin version nueva** (el hash es sobre el cuerpo).
8. **Regresion de M5.** Subir uno de cada formato que ya andaba (.pdf de texto, .docx, .xlsx, .csv, .txt, .png) y verificar
   que el tipo, el estado de lectura y los rotulos de las partes siguen iguales.

### Checklist de merge
- [x] Build 0 errores (2 advertencias preexistentes) · tests **509/509**
- [x] 4 goldens de hash de contexto intactos
- [x] Sin migracion EF (el valor nuevo del enum va en una columna `int` que ya existe)
- [x] Logica en services/extractores/helpers, nunca en controllers
- [x] Multi-tenant sin cambios; ningun `IgnoreQueryFilters()` sin nombre
- [x] `Mcp` y `Cli` sin tocar
- [x] Costo cero: ninguna llamada a la API real, ninguna salida a internet
- [x] Ningun archivo del cliente en el repositorio (verificado con `git grep`)
- [x] Portal levantado al terminar con "MODELO SIMULADO" confirmado · sin commits

# Escenario real `contadores-bma` (datos, no codigo) — prueba del template con archivos de un cliente

Estado: **cargado 2026-09-16**. Pedido de Joaquin: evaluar si el template le sirve a **Contadores BMA** (estudio
contable, cliente de Olvidata, con Discovery propio abierto en `docs/contadores-bma-agentes-ia/`). **Escenario aparte
de `estudio-contable-demo` (tenant 19), que no se toco.** Base: `olvidata_agentes_dev`, tenant **20**.
**Sin cambios de codigo, sin migracion EF, sin commits, costo cero** (portal con `Anthropic__Simulado=true`,
arranque 17:01 con "MODELO SIMULADO"; `grep -c anthropic.com` sobre los logs del dia = 0; `EventoUso` del tenant 20:
12 eventos, USD 0,000000). `git status --porcelain` = 0 al cerrar; `git grep -il "credicoop|nefroexcel|bma.test|70823732"`
sin resultados: **los archivos del cliente viven solo en la base de dev y en `App_Data/documentos/20/64/` (gitignorado)**.

### Que quedo cargado
| Cosa | Detalle |
|---|---|
| Organizacion | Tenant **20** `contadores-bma` "Contadores BMA", licencia **#10** al rubro `contable`, vigente hasta 16/09/2027 (365 dias) |
| Personas | `direccion@bma.test` "Direccion BMA" (Director) y `gaston@bma.test` "Gaston" (Empleado, area Impuestos). Las dos **`Super123!`**, creadas por el camino real (`/Clientes/Details/20` → Nuevo miembro), **sin copiar hashes por SQL** |
| Areas | Impuestos (54), Sueldos (55), Conciliaciones (56) |
| Cartera | **63** SERVICIO TERAPIA RENAL S.A. (sin identificacion: no la sabemos) · **64** "Cliente CUIT 30-70823732-5 (razon social a relevar)". Las notas de los dos separan **lo que sabemos** de **lo que falta relevar** |
| Documentos | **5 de 6**. Los 5 PDF del Credicoop (enero a mayo 2026) al cliente 64, subidos por el camino real, los 5 con `EstadoLectura = 1` y su texto extraido (7 a 11 partes, 45.537 a 60.768 caracteres, ninguno recortado). Hash SHA-256 en disco identico al original. **El `.xls` no entro** |
| Reglas | 4 a nivel empresa: 3 sugerencias del rubro (#100 y #101 en "Siempre", #102 en "Salvo que se indique otra cosa") + **#103 "Los numeros los hace el codigo, no el agente"**, propia de BMA, en **Siempre**. Quedan **3 sugerencias sin activar** |
| Tareas | #202 Registracion (conciliar extracto vs. mayor, 5 PDF adjuntos) · #203 Ingresos Brutos (retenciones y percepciones de ARBA del extracto, 5 PDF) · #204 Comunicacion con el cliente (pedido de lo que falta, 2 turnos). Las 3 a nombre de Gaston, **Completadas, USD 0,00** |
| Programacion | **#16** "Liquidacion de sueldos del mes — SERVICIO TERAPIA RENAL S.A.", agente `cont-sueldos`, cliente 63, mensual dia 5 a las 08:00, responsable Gaston, **sin autonomia** ("Acciones con aprobacion: no se le ofrecen"). **No se disparo** |

### Que paso con los 6 archivos reales (lo que se pidio medir)
- **Los 5 PDF del Credicoop entran y son legibles**: son PDF de texto, no escaneos. Ninguno dio "no legible".
- **El `.xls` se rechaza**, con el mensaje `MensajesDocumentos.FormatoViejo` ("Los formatos .doc y .xls no estan
  permitidos. Guardalo como .docx o .xlsx."). El rechazo esta en los **dos lados**: `wwwroot/js/documentos.js` y
  `ValidadorContenidoArchivo.ValidarExtension`, que llama `DocumentoCarteraService.SubirAsync`. No queda fila en
  `DocumentosCartera`. **Se dejo asi a proposito, sin convertirlo.**
- **DEF-BMA-1 — el `.xls` de SOS Contador no es un Excel: es HTML.** Los primeros bytes son
  `<table><tr><td><b>Imputaciones Contables - CUIT 30-70823732-5 - Nefroexcel SRL</b>`. Son 96 filas con columnas
  Cuenta / Fecha / Comprobante / CUIT / Razon Social / Concepto / Monto Debe / Monto Haber / Saldo: **exactamente el
  dato que la conciliacion necesita**. Consecuencia: el mensaje "Guardalo como .xlsx" describe mal el problema, y
  renombrarlo a `.xlsx` tampoco funcionaria (el validador mira el contenido). El producto no tiene hoy ninguna via
  para ese archivo: HTML no esta entre los formatos permitidos.
- **DEF-BMA-2 — el texto del PDF pierde el renglon.** Las paginas de movimientos salen con **5 a 8 saltos de linea
  para ~8.000 caracteres**: cada movimiento queda pegado al siguiente en una tirada unica, y la separacion entre
  DEBITO, CREDITO y SALDO sobrevive solo como posicion de espacios. El detalle de un movimiento (CUIT y nombre del
  contrasujeto) aparece **antes** de la fecha del movimiento siguiente.
- **DEF-BMA-3 — ese pegoteo ya produjo un dato falso.** En el encabezado, el texto extraido dice
  `NEFROEXCEL SRL ... R.N.P.S.P. CUIT 30-57142135-2`. **Ese CUIT no es del titular**: viene de otra columna del
  encabezado del banco. El CUIT del titular es 30-70823732-5 y en el extracto solo aparece dentro de los debitos de
  AFIP (`AFIP-30708237325`), nunca en el encabezado. El simulador, al citar el documento, mostro el CUIT equivocado en
  pantalla; y la tarea #204 se escribio con esa confusion adentro y **se corrigio con un segundo turno**, que queda en
  la conversacion como demostracion del ciclo.
- **Paginas que se saltean sin avisar**: en el resumen de abril (12 paginas) y en el de febrero (10) falta una parte;
  se nota solo porque los rotulos van "Pagina 7 de 12" → "Pagina 9 de 12". Son paginas sin texto (los anexos de
  comisiones si se extraen). No hay aviso en pantalla.

### Verificado a mano en el portal
- Las dos personas entran de verdad con `Super123!`.
- Aislamiento multi-tenant en **los dos sentidos**: Gaston (org 20) da **404 en 15 URLs** de las organizaciones 1, 4 y
  19 (cartera, tareas, programaciones, reglas, documentos `Ver`/`Descargar`/`Index`) y **200** en las suyas;
  `socio@contable.test` (org 19) da **404 en 12 URLs** de la org 20 y **200** en las 4 suyas.
- Conteos por tenant sin cambios en 1, 4 y 19 (org 19 sigue con 4 personas, 3 areas, 6 clientes, 16 documentos,
  4 reglas, 1 programacion y 4 tareas).
- `/Consumo` muestra 2 personas, 1 area con tareas, 3 agentes y 1 cliente, todo en USD 0,00.
- `dotnet test`: **478/478**, linea base intacta.

### Riesgos y cosas a saber
- La licencia #10 nace con **`Puestos = 1`** (hardcodeado en `Admin licencia-crear`) y la organizacion tiene 2
  miembros. `Puestos` no se valida en ningun lado; queda incoherente a la vista, igual que en la org 19.
- El nombre del cliente 64 **se dejo como "razon social a relevar" a proposito**, aunque ahora sabemos que es
  Nefroexcel SRL: el nombre refleja lo que el producto alcanzo a saber con lo que si pudo cargar. La razon social y
  la advertencia del CUIT estan en las notas del cliente.
- SERVICIO TERAPIA RENAL S.A. **queda sin documentos**: no hay archivos reales suyos en el Discovery. No se invento
  ninguno.
- Los textos que devuelven las tareas salen del **guion del simulador** (lee el primer documento adjunto y lo cita):
  no son una conciliacion de verdad. Lo que si es real es que **leyo los PDF cargados** y los cito por su contenido.
- Los archivos de `docs/contadores-bma-agentes-ia/` son confidenciales de un tercero. Se usaron **solo** para cargar
  la base de desarrollo, por pedido explicito de Joaquin, y **nunca** se copiaron al repositorio ni al nucleo.

# Organizacion de demostracion `estudio-contable-demo` (datos, no codigo)

Estado: **cargada 2026-09-16**. Pedido de Joaquin: modelo de pruebas navegable del producto como estudio contable.
**Sin cambios de codigo, sin migracion EF, sin commits, costo cero** (portal con `Anthropic__Simulado=true`;
`grep -c anthropic.com` sobre el log del arranque = 0). Base: `olvidata_agentes_dev`, tenant **19**.

### Que quedo cargado
| Cosa | Detalle |
|---|---|
| Personas | `socio@contable.test` Marina Sosa (Directora), `impuestos@contable.test` Nicolas Rey (Impuestos), `sueldos@contable.test` Carla Duarte (Sueldos), `junior@contable.test` Tomas Ferro (Registracion). Todas **`Super123!`** |
| Areas | Impuestos (51), Sueldos (52), Registracion (53) |
| Cartera | 57 Bazar del Oeste S.R.L. · 58 Metalurgica Parana S.A. (Convenio Multilateral, 4 jurisdicciones) · 59 Delta Servicios Informaticos S.R.L. (exporta servicios) · 60 Lucia Peralta (monotributista) · 61 Dr. Esteban Quiroga (profesional independiente) · 62 Vivero Las Acacias S.R.L. (**cliente nuevo, 1 solo documento a proposito**) |
| Documentos (M5) | 16, todos por el camino real del portal, **los 16 con `EstadoLectura = 1`** y su texto extraido. 3/4/3/2/3/1 por cliente |
| Reglas | 4 sugerencias del rubro contable activadas a nivel empresa (3 "Siempre", 1 "Salvo que se indique otra cosa"). **2 quedan sin activar**: "Solo lo que resiste una fiscalizacion" y "Al cliente se le habla sin jerga" |
| Programacion (M12) | #15 "Panorama de vencimientos del mes", agente `cont-vencimientos`, mensual dia 5 a las 08:00, responsable Marina, **sin autonomia**. Proxima vuelta 05/10/2026 08:00. **No se disparo** |
| Tareas | #198 Marina · Comunicacion con el cliente · Vivero (Completada) · #199 Carla · Liquidacion de sueldos · Bazar (Completada, 2 turnos con adjunto) · #200 Nicolas · Ingresos Brutos · Metalurgica (Completada, 2 turnos, M10) · #201 Tomas · Registracion · Quiroga (**Espera aprobacion de un Director**) |

### Defecto de contenido corregido en el nucleo (DEF-CONT-1)
5 archivos de `nucleo/rubros/contable/` tenian la `description` del front matter **sin comillas y con `:` adentro**,
que es YAML invalido. `ImportadorRubro.SepararFrontmatter` **traga la excepcion sin emitir advertencia** y descarta
toda la metadata, dejando el cuerpo bien importado. Consecuencia: `cont-balance`, `cont-monotributo` y `cont-sueldos`
tenian el **slug como nombre**, sin descripcion y **con `Herramientas = NULL`** (o sea, sin `fecha_hora_actual` ni las
suyas propias), y `20-sueldos-procedimientos` y `40-calendario-alicuotas-escalas` sin nombre ni descripcion.
Se entrecomillaron las 5 descripciones y se re-importo: **0 artefactos nuevos, 0 versiones nuevas, 22 sin cambios**
(el hash de version es sobre el **cuerpo**, no sobre el front matter), 22/22 publicadas, metadata completa.
**Deuda abierta:** el `catch` mudo de `SepararFrontmatter` deberia sumar una advertencia al resultado del import —
hoy un error de front matter se pierde en silencio y el rubro queda a medias sin que nadie se entere.

### Verificado a mano en el portal
- Las 4 personas entran de verdad con `Super123!` (las cuatro probadas, no deducidas).
- Aislamiento multi-tenant en **los dos sentidos**: Marina da 404 en 4 URLs de las organizaciones 1 y 4;
  `dira@qa.test` (org 1) da **404 en 7 URLs** de la org 19 y su propia cartera sigue devolviendo sus 20 clientes.
- "Ver pasos" de #199 sale entero en palabras, sin JSON ni nombres de herramienta.
- `/Consumo` muestra las 4 personas, 4 areas, 4 agentes y 4 clientes (USD 0,00: modelo simulado).
- `/Aprobaciones` muestra 1 pendiente, "Solo un Director", vence el 19/09.
- `dotnet test`: **478/478**, linea base intacta.

### Riesgos y cosas a saber
- La licencia #9 de la organizacion tiene **`Puestos = 1`** con 4 miembros. `Puestos` **no se valida en ningun lado**
  (solo se muestra en `/Clientes/Details` del backoffice), asi que no rompe nada, pero queda incoherente a la vista.
- Las tarjetas de aprobacion y el contenido que cita el agente salen del **guion del simulador**, no del contenido
  contable: la accion pendiente dice "pago de prueba de $ 15.000 a «Cliente de prueba»". Es esperable con el modelo
  simulado; con el modelo real el texto seria el del caso.
- El guion de conocimiento del simulador **busca la primera palabra de 4+ letras del pedido**, asi que la seccion que
  cita no siempre es la pertinente. Para que la demo se vea coherente, conviene **empezar el pedido con la palabra
  clave** ("Convenio Multilateral, ...").
- Las cuentas `@qa.test` de dev **hoy tienen todas el hash del SuperUsuario**, o sea contrasena `Super123!`, pese a que
  el cierre de la ronda 2 de QA dice que se restauraron los originales. Se verifico sin adivinar (guardando el hash
  antes de tocarlo) y se dejo exactamente como estaba.


# Correcciones de la QA integral ronda 1 (DEF-R1-1 y OBS-R1-1..4)

Estado: **implementadas 2026-09-16, pendientes de la ronda 2 de QA**. Entrada: `6-qa.md` → "QA integral ronda 1
(2026-09-16) — CERRADA", con los pasos de reproducción de cada punto. Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.
**Sin migración EF** (ningún cambio de esquema: lo único nuevo que viaja es un campo de un DTO en memoria).
**Ninguna llamada a la API real de Anthropic, ninguna salida a internet, sin commits.** `Mcp` y `Cli` sin tocar.
Decisión de diseño previa de Joaquín: DEF-R1-1 se unifica en el resumidor que ya tienen M5/M10/M11, sin gate.

### Escaneo de reutilizacion
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M5 `HerramientasDocumentos.Resumir` (D-M5-12) | La forma del resumidor: `ResumenHerramientaDto(Rótulo, ContenidoLegible, EsError)`, con el detalle plegado bajo "Ver lo que leyó" | Literal (patrón) |
| Template M10 `HerramientasConocimiento.Resumir` (D-M10-6) | El manejo del error ("No pudo …: {motivo}" con minúscula inicial) y el recorte del contenido legible | Literal |
| Template M11 `HerramientasConectores.Pedido/Resumir` (D-M11-7) | Que el **pedido** también lleve rótulo, no solo el resultado | Literal |
| Template M7a `ResumenHerramientasPlataforma` | La cadena de `??` entre familias, que ahora vive en un solo lugar | Adaptado |
| Template M11 `GuardiaDestinoHttp.RevisarIp` | La revisión de IP que ya existía; OBS-R1-2 solo la conecta al momento de guardar, resolviendo el nombre | Literal |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún otro proyecto muestra "pasos de un agente" en pantalla: el resumidor es propio de este producto. Lo más cercano (auditorías de CRM) lista acciones de personas, no de un modelo | Sin match |
| Escaneo `docs/patrones/catalogo.yml` | Sin patrón nuevo: PAT-033 (rótulos llanos de herramientas) ya cubre el criterio; esto lo extiende a las familias que faltaban | Sin patrón nuevo |

### Qué se hizo

1. **DEF-R1-1 — un solo resumidor para "Ver pasos" (cierra PA-12 en su parte de "Ver pasos").**
   `Infrastructure/Services/Motor/ResumenPasos.cs` es ahora el **único** lugar que traduce un paso de herramienta a
   palabras. Encadena, en orden, documentos (M5) → conocimiento (M10) → conectores (M11) → plataforma/subagentes (M7a) →
   **configurador (M4b, nuevo)** → **asistente del Director (M7b, nuevo)**, y **nunca devuelve null**: si apareciera una
   herramienta sin rótulo redactado, cae en un texto genérico (`RotulosPasos`, en Application) que **no nombra la función
   ni vuelca lo que devolvió**. `ServicioTareas` pasó de armar la cadena a mano a llamar a `ResumenPasos`.
2. **Rótulos nuevos: las 14 herramientas que faltaban.** `ResumenHerramientasConfigurador` (9: `reglas_listar`,
   `regla_obtener`, `estructura_empresa`, `clientes_buscar`, `sugerencias_listar` y las 4 de propuesta) y
   `ResumenHerramientasAsistente` (5: `equipo_listar`, `agentes_disponibles`, `asignaciones_listar`,
   `proponer_asignacion`, `proponer_tarea_agente`). Ejemplos: `Usa proponer_regla_nueva {"alcance":"empresa",…}` →
   **"Propuso una regla nueva para toda la empresa: «Regla simulada 1-a»"**; `Usa estructura_empresa {}` →
   **"Miró cómo está organizada tu empresa (áreas y agentes)"**. Los códigos internos **no se muestran**: ni el
   `persona_id` (un GUID) ni el código de agente (`b-inmobiliario/inmo-agenda`) ni el alcance en código (`cliente_agente`
   → "para un cliente y un agente"). El resultado de una propuesta no vuelca el texto técnico: manda a la tarjeta.
3. **La vista ya no tiene camino crudo.** `Views/Tareas/_PasosTurno.cshtml` perdió las dos ramas de respaldo que
   imprimían `Usa <code>@herramienta</code> @entrada` y `Resultado de <code>@herramienta</code>` + el contenido sin
   resumir. Todo el texto del modelo y de terceros sigue saliendo por Razor, **escapado**, y lo que viene del modelo se
   limpia de caracteres de control para que no rompa el renglón del rótulo.
4. **OBS-R1-3 — 403 en vez de saneo mudo (CA-M12-12).** `ProgramacionesController.LeerDto` pasaba
   `_permisos.PuedeProgramarParaOtros ? m.ResponsableUsuarioId : yo` y `… && PuedeProgramarParaOtros`: el POST forzado
   se guardaba saneado y el `SinPermiso` del service quedaba inalcanzable. Ahora el formulario se pasa **tal cual** y
   decide el service, que ya devolvía `SinPermiso` → `RespuestasServicio.Error` → **403**. El alta normal de un Empleado
   no cambia: su formulario manda su propio id en un hidden (y si no viajara, se asume él mismo, que es lo único que
   puede). El `&&` del service queda como segunda red, documentado.
5. **OBS-R1-4 — "Probar" dice lo que contestó el externo.** `ResultadoConectorDto` suma `CuerpoExterno` (solo el
   **cuerpo**, nunca encabezados: ahí viajan credenciales) y `MensajesConectores.ResultadoDePrueba` arma
   *"El sistema externo contestó con un error 500. Lo que contestó el sistema externo: «…»"*. Es texto de un tercero:
   `TextoExternoSeguro` lo deja en **una sola línea**, sin caracteres de control, sin ninguno de los caracteres con los
   que se arma marcado (`<`, `>`, `&`, comillas dobles, comillas simples y acento grave: no queda HTML activo posible
   aunque el que lo muestre no escape) y **recortado a 300 caracteres**. El mensaje del historial de
   llamadas no cambió (sigue "HTTP 500"), así que M11 no se movió de lo que QA ya validó.
6. **OBS-R1-2 — el destino se valida al guardar.** `IGuardiaDestinoHttp.RevisarDestinoAlGuardarAsync` = la revisión de
   forma de siempre **más la resolución del nombre**: `https://localhost:8443/` o `intranet.empresa.local` ahora se
   rechazan en el formulario y no quedan guardados como una conexión que nunca va a andar. El mensaje dice qué pasa
   (el motivo del guardia) y qué hacer ("Poné la dirección pública del sistema…"). **Si el DNS no resuelve no se
   bloquea**: un DNS caído no es motivo para no dejar guardar, y la protección real sigue siendo la revisión de IP al
   conectar. Con `Conectores:PermitirDestinosPrivados = true` (tests) el chequeo no estorba: sale antes de pagar el DNS.
7. **OBS-R1-1 — singular y plural.** `/Conocimiento`: "Son 1 documento en total." → **"Hay 1 documento en total."**
   (con 2 o más sigue "Son N documentos en total."). Barrido de los 50 usos de `== 1 ?` en vistas, helpers y JS: el
   único otro caso del mismo patrón era `Nucleo/Rubro.cshtml` ("1 publicados" → "1 publicado y consultable"). El resto
   ya concordaba, o usa "Hay", que sirve para singular y plural.

### Decisiones de implementacion (ambigüedades resueltas)
- **DI-R1-1 El fallback de "Ver pasos" no muestra el contenido, ni siquiera el del error.** Podría haberse mostrado el
  texto devuelto por una herramienta sin rótulo (los mensajes de error del producto son castellano llano). Se descartó:
  no hay forma de garantizar que una herramienta futura devuelva algo legible, y el criterio de la corrección es que
  **nunca** llegue JSON a la pantalla. El costo es diagnóstico: si alguien agrega una herramienta y olvida el rótulo,
  "Ver pasos" dice poco. Lo compensa el test que recorre todas las herramientas registradas y falla si falta un rótulo.
- **DI-R1-2 `CuerpoExterno` como campo del DTO, no re-parsear `ParaElAgente`.** La alternativa era extraer el cuerpo del
  mensaje que va al modelo buscando "Lo que contestó: ". Se descartó por frágil. El campo es opcional y solo lo llena la
  rama de error del sistema externo.
- **DI-R1-3 `TextoExternoSeguro` neutraliza en origen, no confía en el que muestra.** Hoy SweetAlert2 lo pinta con
  `text:` (textContent) y Razor lo escapa en el listado, así que alcanzaría con escapar. Se decidió neutralizar igual en
  el helper: es texto de un tercero y la lista de lugares donde se muestra puede crecer. Cuesta que `<` y `&` se vean
  como espacios en un cuerpo XML o JSON con entidades; se aceptó a cambio de que no haya forma de equivocarse después.
- **DI-R1-4 El chequeo de DNS al guardar no bloquea si no resuelve.** La alternativa (rechazar) haría que un DNS con
  hipo impida guardar una conexión legítima. Contra: un nombre interno que no resuelve desde el servidor igual se
  guarda; se entera al probar, que es exactamente lo que pasaba antes y no es un agujero (el guardia corta al conectar).
- **DI-R1-5 Los rótulos no dicen "herramienta" salvo en el fallback.** "Miró", "Buscó", "Propuso", "Registró": verbos de
  lo que pasó, no de cómo se llama. El genérico sí dice "una herramienta de la plataforma" porque no hay nada más
  honesto que decir sin nombrarla.
- **OBS-R1-3: el criterio NO se cambió.** Se evaluó dejar el saneo y corregir CA-M12-12. Se descartó: sanear en silencio
  le devuelve al usuario un "guardado" que no es el que pidió (la programación quedaba a su nombre y sin autonomía, sin
  un solo aviso), y el criterio escrito es el comportamiento correcto. `1-analista-funcional.md` queda como estaba.

### Archivos tocados
| Archivo | Qué |
|---|---|
| `src/…Application/Motor/IMotorAgentes.cs` | **`RotulosPasos`** (3 constantes del fallback) en Application, para que la vista no dependa de Infrastructure |
| `src/…Infrastructure/Services/Motor/ResumenPasos.cs` | **Nuevo.** Resumidor único; `Pedido`/`Resultado` nunca devuelven null |
| `src/…Infrastructure/Services/Configurador/ResumenHerramientasConfigurador.cs` | **Nuevo.** Las 9 de M4b |
| `src/…Infrastructure/Services/Asistente/ResumenHerramientasAsistente.cs` | **Nuevo.** Las 5 de M7b |
| `src/…Infrastructure/Services/Motor/ServicioTareas.cs` | Llama a `ResumenPasos` en vez de encadenar resumidores a mano |
| `src/…Web/Views/Tareas/_PasosTurno.cshtml` | Se borraron las dos ramas que imprimían nombre de herramienta y JSON |
| `src/…Web/Controllers/ProgramacionesController.cs` | `LeerDto` pasa responsable y autonomía tal cual (OBS-R1-3) |
| `src/…Infrastructure/Services/Programaciones/ProgramacionTareaService.cs` | Solo el comentario del `&&` que queda como segunda red |
| `src/…Application/DTOs/ConectoresDtos.cs` | `CuerpoExterno`, `ResultadoDePrueba`, `TextoExternoSeguro`, `DestinoAlGuardar` |
| `src/…Application/Interfaces/IConectores.cs` | `RevisarDestinoAlGuardarAsync` en el guardia y en `IConectorTipo` (con implementación por defecto) |
| `src/…Infrastructure/Services/Conectores/GuardiaDestinoHttp.cs` | Resolución de nombre al guardar, con espera de 3 s |
| `src/…Infrastructure/Services/Conectores/ConectorHttpGenerico.cs` | Llena `CuerpoExterno` en el 5xx; revisa la base al guardar |
| `src/…Infrastructure/Services/Conectores/ConexionConectorService.cs` | Corta el alta con destino interno; mensaje de prueba con el cuerpo |
| `src/…Web/Views/Conocimiento/Index.cshtml` · `Views/Nucleo/Rubro.cshtml` | Concordancia de número (OBS-R1-1) |
| `tests/…/ResumenPasosTests.cs` | **Nuevo.** 41 casos (incluye los pasos reales de las conversaciones #182 y #173) |
| `tests/…/ConectoresTests.cs` | 6 casos nuevos (OBS-R1-2 y OBS-R1-4) |
| `tests/…/ProgramacionesTests.cs` | 1 caso nuevo + la aserción de `TipoError.SinPermiso` que faltaba (OBS-R1-3) |

### Evidencia
- `dotnet build OlvidataAgentes.slnx`: **0 errores, 2 advertencias** — las dos preexistentes de la línea base
  (`HomeController.StatusCode` oculta el miembro heredado y el `xUnit2013` de M7a). Las vistas compilan en el build
  (verificado a propósito rompiendo una y viendo fallar la compilación), así que `_PasosTurno.cshtml` está cubierto.
- `dotnet test tests/OlvidataAgentes.Tests`: **478/478**. Línea base 430 + 48 nuevos.
- **Los 4 goldens de hash de contexto intactos**: `HashGoldenCmPanaderia`, `HashGoldenTasadorFerreteria`,
  `HashGoldenFormato2/3` y `HashGoldenFormato4` **sin una sola modificación** (los archivos que los contienen no
  aparecen en el diff). Tiene que ser así: nada de esto toca el armado del contexto, solo cómo se muestra después.
- **Verificación contra datos reales** (no solo fixtures sintéticos): se leyeron de `olvidata_agentes_dev` los pasos
  reales que vio QA — `PasosTarea` de la conversación **#182** (configurador) y **#173** (asistente) — y se anclaron
  como test. Ahí apareció lo que un fixture propio no habría reproducido: en `estructura_empresa`, `clientes` es un
  **objeto** y no un arreglo como las demás propiedades. **Solo lecturas: la base no se tocó.**

### Pruebas minimas para QA (ronda 2)
1. **DEF-R1-1, lo central.** Conversación nueva en `/ConfiguracionReglas/Nueva` → "Ver pasos" de la tarea: los tres
   pasos tienen que decir **"Miró cómo está organizada tu empresa (N áreas, M agentes)"**, **"Propuso una regla nueva
   para toda la empresa: «…»"** y **"Propuso un procedimiento nuevo para toda la empresa: «…»"**. Buscar en el HTML
   (Ctrl+U o el inspector): **cero apariciones** de `proponer_regla_nueva`, `estructura_empresa`, `{` y `}`.
2. **El asistente (M7b), que la ronda 1 no recorrió entero.** `/Asistente` → una conversación completa → "Ver pasos":
   "Miró al equipo (N personas)", "Propuso asignarle una tarea a alguien del equipo: «…»". Verificar que **no aparece
   ningún GUID** de persona ni el código `b-inmobiliario/…`.
3. **No romper lo que ya andaba.** Re-verificar "Ver pasos" de M10 (material de Olvidata) y M11 (conector): los rótulos
   y el "Ver lo que leyó" tienen que seguir igual que en la ronda 1.
4. **OBS-R1-3 por el camino del navegador**, que es el único que no se puede cubrir por test (el proyecto de tests no
   referencia Web): como Empleada, forzar el POST de `/Programaciones/Crear` con el `ResponsableUsuarioId` de otra
   persona → **403** (antes: 201 + saneo). Ídem con `PuedeAccionesConAprobacion=true` → **403**. Y verificar que el
   alta normal de la Empleada **sigue funcionando** y que la edición de una propia no se rompe.
5. **OBS-R1-2.** Con el guardia en `false`, cargar una conexión con base `https://localhost:8443/` y la lista de
   dominios vacía → tiene que **no guardarse**, con el mensaje que dice qué pasa y qué hacer. Confirmar por SQL que no
   quedó fila. Y que el camino de M11 con el servidor de prueba local **sigue andando** con la variable en `true`.
6. **OBS-R1-4.** Apuntar una conexión a un endpoint que devuelva 500 con cuerpo → "Probar" tiene que mostrar el cuerpo,
   acotado. Probar también con un cuerpo con HTML (`<script>…`) y verificar que **no se ejecuta nada** y que el texto
   sale neutralizado, tanto en el diálogo como en el "Última prueba" del listado.
7. **OBS-R1-1.** `/Conocimiento` con **un solo** documento: "Hay 1 documento en total.". Con dos o más: "Son N…".

### Checklist de merge
- [x] Build 0 errores (2 advertencias preexistentes) · tests 478/478
- [x] 4 goldens de hash de contexto intactos
- [x] Sin migración EF (ningún cambio de esquema)
- [x] Lógica en services/helpers, nunca en controllers (el controller solo dejó de sanear)
- [x] Multi-tenant sin cambios; ningún `IgnoreQueryFilters()` sin nombre
- [x] `Mcp` y `Cli` sin tocar
- [x] Costo cero: ninguna llamada a la API real, ninguna salida a internet en los tests
- [x] Base de desarrollo solo leída; sin commits

# M12 — Tareas programadas y autonomía gradual por rol

Estado: **implementada 2026-09-16, pendiente de QA (etapa 6)**. **Última etapa del roadmap.** Entrada: `1-analista-funcional.md` M12
(RF-M12-01..17, CA-M12-01..16), `2-disenador-funcional.md` M12 (D-M12-1..12, P-M12-01..03) y `3-arquitecto-mvc.md` M12
(RT-M12-01..11), aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto
personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Una entrega, una migración: `ProgramacionesM12`.
**Ninguna llamada a la API real de Anthropic, ninguna salida a internet, sin commits.** Mcp y Cli sin tocar (solo compilan).

### Escaneo de reutilizacion M12
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M7a `IPreparadorTareaTrabajo` | **La pieza clave.** "Armar una tarea de trabajo sin guardarla", con límite de gasto (M6), suscripción, agente, cliente, adjuntos e instantánea de reglas ya adentro. Una vuelta programada **no duplica ni una línea** de crear una tarea | Literal (reuso de código, no copia) |
| Template M6 `AvisoGasto` (PAT-035) | "Esto se hace una sola vez aunque varios lo intenten": insertar y tratar el `DbUpdateException` (1062) como "otro llegó antes". De ahí sale la reserva de la ocurrencia | Literal (patrón) |
| Template M1 lease del motor | La idea de reservar trabajo con un `UPDATE` condicionado por token de concurrencia. M12 la combina con el índice único porque la reserva y el trabajo van en **guardados distintos** | Adaptado |
| Template M4b `IResolvedorSesion.ResolverUsuarioAsync` | Correr en segundo plano con los permisos de una persona, sin sesión ni caché | Literal |
| Template M6/M7a/M8/M9 barridos de `MotorAgentesWorker` | El quinto barrido con su ritmo y su interruptor; la estructura del `try/catch` que no rompe el ciclo | Literal |
| Template M7b `TareaAsignadaService` + `AsignacionesController` + vistas | La forma completa de un ABM con DataTables server-side, filtros en sesión, búsqueda global sobre las columnas visibles, acciones AJAX con SweetAlert2 y token de concurrencia con mensaje de conflicto | Literal (adaptado) |
| Template M7b `ConversorDia.Dia` | `DateOnly` → columna `date` en MySQL (sin el conversor, proyectar a `DateOnly` revienta con InvalidCastException) | Literal |
| Template M11 DI-M11-6 | "El costo se calcula, nunca se guarda": nada de escribir columnas de otra entidad dentro del commit del motor | Práctica |
| Escaneo `docs/patrones/catalogo.yml` (PAT-001..044) | Ningún patrón cubría "trabajo repetitivo reanudable". Lo más cercano, PAT-034/035, son de aprobación y gasto | Sin match |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún proyecto tiene tareas programadas. Lo más cercano son los vencimientos/recordatorios de CRM, que son **avisos** calculados al mirar la pantalla, no trabajo que corre solo | Práctica, no código |
| PAT-045 | **Creado** en el catálogo | Nuevo |

### Qué se hizo

1. **Programación = receta, no tarea (RF-M12-01/06).** `ProgramacionTarea` (`ITenantOwned` + `SoftDestroyable`) guarda qué se
   pide, a qué agente, cada cuánto y quién responde. `EjecucionProgramada` guarda cada vuelta. La tarea que sale es una
   `TareaAgente` **común y corriente**: mismos pasos, mismo costo, misma conversación de M3b. Por eso los 4 goldens de hash
   quedan intactos: una vuelta usa el mismo `IPreparadorTareaTrabajo` que el botón del portal.
2. **La ocurrencia se reserva antes de trabajar (RT-M12-01, PAT-045).** `ReservarAsync` escribe la vuelta y adelanta
   `ProximaEjecucionAt` **en un guardado**, con índice único `(ProgramacionTareaId, Ocurrencia)` y `VersionToken`. Recién
   después `EjecutarUnaAsync` crea la tarea. Si el proceso muere en el medio, la vuelta queda `Reservada` y el barrido la
   termina sin reservar de nuevo.
3. **Nunca se disparan las vueltas perdidas (RT-M12-02).** La próxima se recalcula **desde ahora**. Un sitio dormido una
   semana crea una tarea al despertar, no siete. Verificado con un test que corre tres barridos seguidos.
4. **Calendario en hora argentina (RT-M12-03).** `CalendarioProgramacion`: diaria, semanal (1 = lunes … 7 = domingo) y
   mensual con **recorte del día 31 al último día del mes**. Siempre estrictamente después del instante que recibe. Helper
   puro: 8 tests lo ejercitan sin base.
5. **Autonomía por rol resuelta en el motor (RT-M12-07).** En `ProcesadorTareas`, una tarea con `ProgramacionTareaId` y
   `AutonomiaConAprobacion = false` **pierde todas las herramientas con `RequiereAprobacion`** antes de armar la solicitud.
   El agente no puede pedir lo que no tiene. Con la autonomía encendida las recibe y el circuito de M6 funciona igual:
   la acción queda esperando y **nunca se aprueba sola**.
6. **La vuelta corre como el responsable (RT-M12-06).** `ResolverUsuarioAsync` puebla tenant y contexto; si dejó la empresa,
   la vuelta queda Bloqueada con "El responsable ya no es un miembro activo de la empresa."
7. **Fallas seguidas con corte y aviso (RF-M12-09).** Una vuelta que no pudo nunca mata la programación: suma una falla y
   recién a las 5 queda Terminada con motivo, y el responsable recibe dos avisos (el de la vuelta y el del corte).
8. **Costo calculado (RT-M12-09).** Del mes y total, sumando `PasosTarea.CostoUsd` de las tareas de esa programación, con el
   período argentino de M6. Aviso una vez por mes cuando **una sola** programación pasa el 50 % del tope de la empresa.
9. **Origen en Tareas (RF-M12-10).** Chip "Programada · «Nombre»" en la grilla, aviso en el detalle, filtro "Origen" y el
   enlace "Ver sus tareas" del detalle que fija la programación.
10. **Pantallas (RF-M12-16) y consola (RF-M12-17).** `Programaciones/{Index, Form, Detalle, _ScriptAcciones}`, ítem en el
    menú de todo miembro, y el verbo `programaciones <tenantSlug>` en Admin.

### Decisiones de implementacion M12 (ambigüedades resueltas)
- **DI-M12-1 Dos fases con estado `Reservada`, no una transacción larga.** La alternativa era abarcar reserva y creación en
  una transacción. Se descartó: con EF InMemory los tests no la tienen, y en MySQL sostenerla mientras se arma el contexto y
  se calcula el hash deja la fila tomada varios segundos. Costo: un estado más y un barrido de recuperación. Hipótesis
  tomada sin gate (autorización 2026-09-14).
- **DI-M12-2 Las vueltas perdidas se pierden.** Al despertar se dispara **solo la última pendiente**, y ni siquiera esa: se
  recalcula desde ahora. Lo pidió el alcance y además es lo correcto —una tarea de IA vieja cuesta plata y casi nunca sirve—.
  Contra: nadie puede "recuperar" el resumen del lunes que no corrió. Queda dicho en el formulario.
- **DI-M12-3 Día 31 en un mes corto → último día del mes.** La otra opción era saltear el mes. Se descartó: "el 31 de cada
  mes" para una persona significa "a fin de mes", y saltear febrero es un silencio que nadie espera.
- **DI-M12-4 La hora se guarda como minutos desde la medianoche argentina (int), no como `TimeOnly`.** Después de que el
  proveedor MySQL obligara a un conversor para `DateOnly` en M7b, un `int` no tiene sorpresas de mapeo, se indexa y se
  compara. El significado está en el nombre de la columna y en su comentario.
- **DI-M12-5 Sin autonomía se QUITA la herramienta, no se auto-aprueba ni se deja pendiente.** Era la decisión central. Se
  descartó auto-aprobar (rompe la promesa de M6) y se descartó dejar el pedido pendiente en silencio (la vuelta queda
  esperando a alguien que no sabe que la esperan, y a la mañana siguiente hay una tarea trabada por cada día). Quitarla es
  fail-closed de verdad: **no hay ninguna rama nueva en el circuito de aprobaciones que pueda tener un agujero**. Efecto
  colateral asumido: sin autonomía, una tarea programada tampoco recibe las herramientas de conectores de M11 (todas tienen
  `RequiereAprobacion = true` por fail-closed) ni las de demostración.
- **DI-M12-6 La autonomía se congela en la tarea (`AutonomiaConAprobacion`).** Si se leyera de la programación al ejecutar,
  editarla a mitad de vuelta cambiaría lo que esa vuelta puede hacer.
- **DI-M12-7 "Ejecutar ahora" solo adelanta la hora; no crea la tarea.** Así el camino de creación es **uno solo** y lo que
  QA prueba a mano es exactamente lo que va a pasar sola de madrugada. Costo: hay que esperar el barrido (hasta un minuto),
  y la confirmación lo dice.
- **DI-M12-8 Sin vista de staff de Olvidata.** M11 sí la tuvo. Acá se dejó afuera para no agrandar la entrega: el verbo de
  consola cubre la necesidad de mirar. **Deuda consciente**, no olvido.
- **DI-M12-9 Una sola pantalla, sin pestañas (D-M12-1).** El Director ve todas con la columna "Responsable" y su filtro; el
  Empleado ve las suyas sin esa columna. Menos superficie que las pestañas de M7b, misma información.
- **DI-M12-10 Sin columnas generadas en la migración.** La unicidad que importa es sobre columnas reales, así que no hizo
  falta el ajuste manual a `STORED` de M2/M4/M11. Es la primera migración del proyecto con un único índice único y sin SQL a
  mano.
- **DI-M12-11 `VersionToken` se incrementa solo en la reserva, nunca al cerrar la vuelta** (RT-M12-11). Si el cierre lo
  tocara, una edición desde la pantalla a mitad de vuelta la haría fallar sin motivo real. El cierre igual va condicionado
  por el token: si alguien editó, la vuelta queda `Reservada` y la retoma el barrido.

### Migraciones EF generadas M12
- `20260916150321_ProgramacionesM12` — `CreateTable ProgramacionesTarea` (`Id int` identity, `TenantId int`,
  `Nombre varchar(150)`, `AgenteArtefactoId int?`, `AgenteOrganizacionId int?`, `ClienteCarteraId int?`, `Pedido text`,
  `Frecuencia/Estado int`, `DiaSemana/DiaMes int?`, `MinutosDelDia int`, `ResponsableUsuarioId varchar(255)`,
  `MotivoFin varchar(500)`, `FinEl date`, `MaxEjecuciones int?`, `EjecucionesHechas/FallasSeguidas int`,
  `PuedeAccionesConAprobacion tinyint(1)`, `ProximaEjecucionAt/UltimaOcurrenciaAt datetime(6)?`,
  `PeriodoAvisoCosto int?`, `VersionToken int` + auditoría y baja lógica) y `CreateTable EjecucionesProgramadas`
  (`Id bigint` identity, `TenantId`, `ProgramacionTareaId`, `Ocurrencia datetime(6)`, `Resultado int`,
  `TareaAgenteId int?`, `Motivo varchar(500)`, `CreadoAt`, `ResueltaAt?`). Más **dos columnas en `TareasAgente`**:
  `ProgramacionTareaId int?` y `AutonomiaConAprobacion tinyint(1) DEFAULT 0`. FK **Restrict** a `Tenants`, `Artefactos`,
  `AgentesOrganizacion`, `ClientesCartera`, `AspNetUsers`, `ProgramacionesTarea` y `TareasAgente`. `Down` = `DropTable` de
  las dos + `DropColumn` de las dos. **Ninguna tabla existente cambia de forma.**
- **Sin ajuste manual a STORED**: no hay columnas generadas (DI-M12-10). Es la diferencia con `OrganizacionM2`,
  `AgentesOrganizacionM4` y `ConectoresM11`.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-16**, con `database update ConectoresM11` (Down OK) y
  `database update` otra vez; `has-pending-model-changes` limpio.
- Verificado por SQL (`scratchpad/verificar-m12*.sql`, transacciones revertidas): tipos y largos exactos;
  **1062 real** al insertar dos veces la misma `(ProgramacionTareaId, Ocurrencia)` — *"Duplicate entry
  '1-2026-09-17 11:00:00.000000'"*; **distinta ocurrencia de la misma programación entra** y **la misma hora en otra
  programación también** (el único es por programación, no global); **1451 real** al borrar una programación con historial y
  **1452** al registrar una vuelta de una programación inexistente; `EXPLAIN` del barrido del worker resuelve por
  `IX_ProgramacionesTarea_Estado_ProximaEjecucionAt` (`range`, `Using index`, nunca `ALL`) y el de las vueltas colgadas por
  `IX_EjecucionesProgramadas_Resultado_CreadoAt` (`range`, `Using index`); collation `utf8mb4_0900_ai_ci` en `Nombre` y
  `Pedido`. **0 restos** tras los ROLLBACK.

### Archivos y capas modificadas M12
**Domain** — Nuevos: `Entities/Programaciones.cs` (`ProgramacionTarea`, `EjecucionProgramada`),
`Enums/EnumsProgramaciones.cs` (`FrecuenciaProgramacion`, `EstadoProgramacion`, `ResultadoEjecucionProgramada`).
Modificado: `Entities/Tareas.cs` (`ProgramacionTareaId`, `AutonomiaConAprobacion`).

**Application** — Nuevos: `Helpers/CalendarioProgramacion.cs`, `Settings/ProgramacionesOptions.cs`,
`DTOs/ProgramacionesDtos.cs` (+ `MensajesProgramaciones`), `Interfaces/IProgramaciones.cs`
(`IProgramacionTareaService`, `IEjecutorProgramaciones`). Modificados: `Interfaces/IPermisosOrganizacion.cs` (2 permisos),
`Motor/IMotorAgentes.cs` (`FiltroTareas.Origen*`, `TareaFiltros.DeProgramacion`/`ProgramacionId`,
`TareaListItemDto.Programacion*`, `TareaDetalleDto.Programacion`).

**Infrastructure** — Nuevos: `Services/Programaciones/EjecutorProgramaciones.cs`, `ProgramacionTareaService.cs`,
`Data/Configurations/ProgramacionesConfigurations.cs`, migración `Data/Migrations/20260916150321_ProgramacionesM12.cs`
(+ Designer y snapshot). Modificados: `Services/Motor/ProcesadorTareas.cs` (quita las herramientas con aprobación en una
tarea programada + aviso de fin en `TrasFinAsync`), `Services/Motor/MotorAgentesWorker.cs` (quinto barrido),
`Services/Motor/ServicioTareas.cs` (filtro de origen, nombre de la programación en la grilla y chip del detalle),
`Services/Organizacion/PermisosOrganizacion.cs`, `Data/AppDbContext.cs` (2 DbSet + exclusión del audit trail),
`Data/Configurations/AgentesConfigurations.cs` (FK e índice de la tarea), `DependencyInjection.cs`.

**Web** — Nuevos: `Controllers/ProgramacionesController.cs`, `Models/ProgramacionesViewModels.cs`, vistas
`Programaciones/{Index, Form, Detalle, _ScriptAcciones}.cshtml`. Modificados: `Controllers/TareasController.cs`
(filtro de origen + `?programacion=`), `Views/Tareas/Index.cshtml` (filtro y chip), `Views/Tareas/_Conversacion.cshtml`
(aviso de origen), `Views/Shared/_Layout.cshtml` (ítem "Programaciones"), `wwwroot/css/site.css` (`.ov-prog-estado`,
`.ov-prog-vuelta`), `appsettings.json` (sección `Programaciones`).

**Admin** — `Program.cs`: verbo `programaciones <tenantSlug>` y ayuda.
**Tests**: nuevo `ProgramacionesTests.cs` (38 con sus casos de Theory).
**Repo**: `docs/diseno-organizacion-roles-reglas.md` (M12 ✅) y `PLAN-IMPLEMENTACION.md`.

### Evidencia de build y tests M12
- `dotnet build OlvidataAgentes.slnx`: **0 errores**. 2 advertencias **preexistentes** que aparecen solo en compilación
  completa y no son de M12 (`xUnit2013` en `ReglasPropuestasAgentesTests` y `CS0114` en `HomeController.StatusCode`).
  Las vistas Razor compilan en el build: `dotnet build` del proyecto Web da 0 advertencias.
- `dotnet test tests/OlvidataAgentes.Tests`: **430 OK / 0 fallidos** (392 previos + 38 nuevos).
- **Inestabilidad preexistente detectada, ajena a M12**: en una de las corridas falló
  `LectorDocumentosTests.Extraccion_que_supera_el_tiempo_queda_como_no_se_pudo_leer`, que mide un tiempo de espera real.
  Vuelto a correr solo y con la suite completa, pasa. Es un test sensible a la carga de la máquina, no una regresión:
  conviene reescribirlo sin depender del reloj cuando se lo toque.
- **Los 4 goldens de hash de contexto intactos**: una tarea programada usa el mismo `IPreparadorTareaTrabajo`, así que el
  prompt de sistema y su hash son los mismos que los de una tarea pedida a mano. Verificado además con un test propio: dos
  vueltas de la misma programación con una regla nueva en el medio dan **hashes distintos** (toma las reglas vigentes).
- **Casos de no duplicación cubiertos** (todos verdes): dos workers globales barriendo a la vez → una sola vuelta y el
  segundo se va con las manos vacías; reinicio entre reservar y crear la tarea → la vuelta queda `Reservada`, la
  programación ya apuntaba al futuro, y el barrido posterior la termina sin duplicar; despertar tras 7 días dormido con
  tres barridos seguidos → **una** tarea y la próxima recalculada dentro de las 24 h.
- **Casos de freno cubiertos**: límite de gasto del mes alcanzado, responsable bloqueado, organización suspendida, 5 fallas
  seguidas → Terminada con motivo y aviso, y tope de ejecuciones → termina sola sin una vuelta de más.
- **Autonomía cubierta**: sin autonomía, `pago_real` y `sin_nivel` **no están** en la lista de herramientas de la solicitud
  al modelo y `nota_libre` sí, y la tarea completa; con autonomía, `pago_real` **sí** se ofrece, queda un `AprobacionAccion`
  Pendiente, la tarea queda `EsperandoAprobacion` y **no hay ninguna `EjecucionHerramienta`** (la acción no se ejecutó).
- **Permisos cubiertos**: un Empleado programa para sí mismo pero no para otro (`SinPermiso`) ni con autonomía; ve solo las
  suyas y una ajena le da `NoEncontrado`; una Directora de otra empresa no ve ni una.
- Lecciones: (1) el orden importa — si la marca de "ya corrí" se escribe **junto** con el trabajo, un corte en el medio
  habilita la doble ejecución; hay que reservar primero y trabajar después; (2) el índice único solo no alcanza si la misma
  instancia reintenta: hace falta el estado intermedio con su barrido de recuperación, o la ocurrencia queda huérfana para
  siempre; (3) una subconsulta con `IgnoreQueryFilters` **dentro de una proyección** no compila (CS9175: un árbol de
  expresión no admite expresiones de colección) — los nombres se resuelven después de la página, como los clientes desde M5;
  (4) la decisión de seguridad más simple fue la mejor: **quitar la herramienta** en vez de agregar una rama al circuito de
  aprobaciones. Menos código nuevo en el camino crítico = menos lugares donde equivocarse.

### Riesgos residuales M12
- **Sin AlwaysRunning (PA-07) las programaciones se atrasan.** SmarterASP duerme el sitio; el worker no corre dormido. Hoy
  solo está el plan B de M9 (ping externo a `/health/vivo`). Una programación de las 08:00 puede correr a las 09:15 si nadie
  entró antes. **Es el riesgo principal de M12 y no lo resuelve el código.** Mitigado a medias: el atraso nunca se convierte
  en avalancha (se dispara una sola vuelta) y el formulario lo dice con esas palabras.
- **Las vueltas perdidas se pierden** (DI-M12-2). Nadie puede recuperar el resumen del lunes que no corrió: hay que usar
  "Ejecutar ahora".
- **La ocurrencia se consume aunque la tarea no se cree.** Evita el bucle infinito de una programación rota, pero significa
  que un problema de un día se lleva la vuelta de ese día.
- **Sin autonomía, una tarea programada tampoco tiene conectores (M11)**, porque todas sus herramientas son fail-closed.
  Es correcto y es lo conservador, pero no es obvio: está dicho en el detalle de la programación.
- **Sin vista de staff** (DI-M12-8) y **sin frecuencias finas** (cada N minutos, días hábiles, "el primer lunes"): deuda
  consciente. Lo primero se cubre con el verbo de consola.
- **El aviso de costo depende de que la empresa tenga tope.** Con `ModoApiKey.PropiaDelCliente` o sin límite no hay contra
  qué comparar y no se avisa; el costo igual se muestra en la pantalla.
- **No se probó con volumen**: el barrido trae hasta 5 vueltas por ciclo y las resuelve en serie dentro del mismo scope. Con
  muchas organizaciones programando a las 08:00 en punto, la cola se va a estirar. Hay que mirarlo cuando haya clientes.
- Verificación visual pendiente (QA): listado, alta con las tres frecuencias, edición, detalle con historial, pausar,
  reanudar, ejecutar ahora, dar de baja, chip y filtro de origen en Tareas, mobile 390 y ambos temas.

### Proximos pasos pendientes M12
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M12).
- **Cerrar PA-07 con soporte de SmarterASP**: es lo que convierte a M12 de "se atrasa" a "corre a la hora".
- Evaluar frecuencias finas y días hábiles si un cliente real las pide (hoy no hay caso).
- Evaluar la vista de staff de programaciones y, con volumen, pasar el barrido a resolver vueltas en paralelo.
- Deuda preexistente vista, fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9.

---

# M11 — Conectores con credenciales por organización

Estado: **implementada 2026-09-16, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M11 (RF-M11-01..17,
CA-M11-01..16), `2-disenador-funcional.md` M11 (D-M11-1..12, P-M11-01..04) y `3-arquitecto-mvc.md` M11 (RT-M11-01..11),
aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal).
Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Una entrega, una migración: `ConectoresM11`. Alcance elegido por
Joaquín: **el mecanismo + un conector HTTP genérico de ejemplo**; los conectores concretos quedan para cuando los
defina. **Ningún sistema externo real configurado, ninguna credencial real usada, ninguna salida a internet, ninguna
llamada a Anthropic, sin commits.** Mcp y Cli sin tocar (solo compilan).

### Escaneo de reutilizacion M11
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1 `Tenant.ApiKeyProtegida` + `ProcesadorTareas.PropositoApiKeyTenant` | Data Protection con propósito propio, descifrado solo al ejecutar y propiedad excluida del audit trail. `PropositoSecretos = "OlvidataAgentes.Conexion.Secretos"` | Literal (mismo mecanismo, otro propósito) |
| Template M6 (PAT-034) `IHerramientaConAprobacion` | Nivel, `DescribirAsync` armada con la entrada, pedido por `tool_use_id`, vencimiento y barrido. **M11 es su primer caso real**: hasta hoy solo lo usaban las acciones de demostración | Literal (extensión: **PAT-044**, la decisión pasa a ser por llamada) |
| Template M5/M6/M10 en `ProcesadorTareas` | "Herramientas en la lista de la solicitud, sin tocar el prompt" + golden de hash | Literal (patrón del repo) |
| Template M2 `AreaConfiguration` / migración `OrganizacionM2` | Unicidad entre vigentes (columna generada + índice único) **y el ajuste manual a STORED** | Literal |
| Template M10 `HerramientasConocimiento.Resumir` / M7a `ResumenHerramientasPlataforma.Pedido` | Rótulos llanos de "Ver pasos", encadenados en `ServicioTareas` | Literal (extensión) |
| Template M4b `HerramientasConfigurador.Texto/Entero` y M5 `HerramientasDocumentos.Json` | **Se llaman, no se copiaron**: mismo assembly y ya probados | Literal (reuso de código) |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún proyecto tiene "conectores con credenciales por organización". Lo más cercano es ARCA/AFIP (instrucción `34`), que es **un** sistema con su protocolo, no un mecanismo genérico: de ahí salieron "credenciales del cliente, nunca del estudio" y "toda llamada externa queda registrada" | Práctica, no código |
| PAT-043 y PAT-044 | **Creados** en el catálogo | Nuevos |

### Qué se hizo

1. **Conector = código, conexión = dato de la organización (RF-M11-01/02, DI-M11-1).** `IConectorTipo` declara código,
   nombre, campos de configuración, validación, herramienta, esquema, "¿es solo lectura?", descripción para la
   aprobación y ejecución. `ConexionConector` (`ITenantOwned` + `SoftDestroyable`) guarda lo que carga el Director.
   Un conector nuevo (Gmail, ARCA) es una implementación más + su registro en DI: no toca el motor, ni las
   aprobaciones, ni las pantallas.
2. **Credenciales cifradas que no vuelven a salir (RF-M11-03).** JSON nombre → valor protegido con Data Protection
   (propósito propio); se guardan además los **nombres** y la fecha. `SecretosProtegidos` está excluida del audit trail
   y no hay ningún camino en el código que devuelva el valor: ni el listado, ni el detalle, ni el backoffice, ni la
   consola. Editar sin escribir nada las conserva; escribir las reemplaza enteras; "borrar" las saca; la baja lógica
   también las borra.
3. **Herramientas (RF-M11-06/07).** `conexiones_listar` (solo lectura, sin aprobación) y una `HerramientaConector` por
   tipo — hoy `http_llamar`. Guardas: solo tareas de trabajo; conexión resuelta por `(tenant de la tarea, código,
   activa, alcance)`; rol del autor re-verificado con `IResolvedorSesion` en cada llamada. "No existe", "está
   inactiva", "es de otra empresa" y "no la podés usar" responden lo mismo.
4. **Aprobación por llamada (RF-M11-09, PAT-044).** `IHerramientaAprobacionPorLlamada` con
   `RequiereAprobacionAsync`; `RequiereAprobacion` sigue en **true** (fail-closed). `ProcesadorTareas` lo resuelve en
   `NecesitaAprobacionAsync`, usado en los **tres** lugares donde antes se leía la propiedad (el recorrido, la rama que
   pide aprobaciones y `SolicitarAprobacionesAsync`). Nivel **Director** siempre.
5. **Conector HTTP genérico (RF-M11-10..14).** Dirección base, métodos habilitados, encabezados fijos, encabezados con
   credenciales, tiempo máximo y KB máximos. El agente manda una **ruta relativa**, nunca una URL libre; el resultado
   se resuelve contra la base y **se valida igual** contra la lista blanca (así `//evil.com/x` no pasa).
6. **Protección contra SSRF (RF-M11-11/12, RT-M11-06).** `GuardiaDestinoHttp`: solo https, sin usuario y contraseña en
   la URL, host en la lista blanca de la conexión (con `*.dominio` y `dominio:puerto`), y ninguna dirección interna.
   La revisión de IP se repite **al conectar**, en el `ConnectCallback` del handler, que después conecta a esas mismas
   direcciones (cierra el DNS rebinding). `AllowAutoRedirect = false` y cada redirección revalidada.
7. **Registro y topes (RF-M11-13/15).** `LlamadaConector` inmutable: quién, cuándo, herramienta, método, **destino sin
   querystring**, resultado, código, ms, bytes y si pasó por aprobación. Tope de llamadas por tarea y por conexión (las
   bloqueadas no cuentan: no llegaron a salir).
8. **"Ver pasos" en palabras (D-M11-7).** `HerramientasConectores.Pedido`/`Resumir`, encadenados en
   `ServicioTareas` después de documentos y conocimiento, y en `ResumenHerramientasPlataforma.Pedido`.
9. **Pantallas (RF-M11-16).** Director: `Conexiones/Index` (tarjetas), `Conexiones/Form` (**dibujado solo a partir de
   los campos del tipo**) y `Conexiones/Uso` (últimas 100 llamadas). Staff: `Clientes/Conexiones` en solo lectura y sin
   secretos, con su botón en la ficha de la organización. Ítem "Conexiones" en el menú del Director.
10. **Simulador y consola (RF-M11-17).** `GuionConectores` (marcador "conexi"/"conector"/"sistema externo" + nombre
    exacto de la herramienta) y el verbo `conexiones <tenantSlug>` en Admin, que nunca muestra una credencial.

### Decisiones de implementacion M11 (ambigüedades resueltas)
- **DI-M11-1 El conector es código, no un dato importable.** La otra opción era declararlo en un manifiesto como los
  rubros. Se descartó: ejecutar una llamada externa es código, y un conector definido en un YAML sería un agujero de
  seguridad editable desde afuera del repositorio. Costo: un conector nuevo pide un deploy. Hipótesis tomada sin gate
  (autorización 2026-09-14).
- **DI-M11-2 Aprobación por llamada, nivel fijo.** Se extendió el motor para que la **necesidad** de aprobación se
  decida por llamada, pero el **nivel** quedó estático en `Director`. Hacerlo variable era otra superficie más en
  `SolicitarAprobacionesAsync` a cambio de poco: lo que el Director necesita —dejar pasar las consultas— ya se resuelve
  por conexión. Hipótesis tomada sin gate.
- **DI-M11-3 `LecturaSinAprobacion = false` por defecto.** Lo más conservador: hasta que el Director lo habilite, toda
  llamada pasa por aprobación. La contra es que una organización que no lo toca va a aprobar mucho; está dicho en la
  pantalla con "(lo recomendado para empezar)".
- **DI-M11-4 Alcance con dos valores, no tres.** `TodaLaOrganizacion` / `SoloDirectores`. Se evaluó agregar "un área"
  (M2 ya tiene áreas) y se dejó afuera: una condición más en la consulta y otra decisión en la pantalla, sin un caso
  que lo pida todavía. Queda como deuda consciente.
- **DI-M11-5 El agente manda una ruta relativa, no una URL.** Dejar que el modelo arme la URL entera hacía que la lista
  blanca fuera la única defensa. Con ruta relativa contra la dirección base de la conexión, más la validación del
  resultado, hacen falta dos fallas para salirse. Verificado con `//evil.com/x` y con una URL absoluta: las dos se frenan.
- **DI-M11-6 El "último uso" se calcula, no se guarda (RT-M11-02).** La primera versión escribía `UltimoUsoAt` en la
  conexión dentro del commit de la tarea. Eso arrastra el `VersionToken` de la conexión al guardado del motor: un
  Director editándola a mitad de una tarea la haría fallar por conflicto de concurrencia sin motivo real (y con EF
  InMemory, un `Attach` parcial habría pisado el resto de la fila). Se quitó la columna; el listado saca el último uso
  y el uso de 30 días con un `GROUP BY` sobre el historial.
- **DI-M11-7 El formulario se dibuja a partir de los campos del tipo.** Un `switch` sobre `TipoCampoConector` en la
  vista, con los valores en `Valores[clave]`. Costo: un poco menos de control fino por campo. Beneficio: el segundo
  conector no pide una vista nueva.
- **DI-M11-8 `PermitirDestinosPrivados` con corte de arranque.** Es la única forma de probar el conector contra un
  servidor local sin salir a internet. Para que no termine encendido en producción, `ValidacionArranque` corta el
  arranque fuera de Development, igual que `Licencias:GenerarClaveSiFalta`, y hay test que lo verifica por el lado del
  guardia (con la opción apagada, ni el servidor local es alcanzable).
- **DI-M11-9 Listado en tarjetas y no en DataTables.** Son pocas conexiones y cada una muestra bastante. Misma
  convención que Reglas y Material de Olvidata. El historial es una tabla plana con las últimas 100, como Consumo.

### Migraciones EF generadas M11
- `20260916141804_ConectoresM11` — `CreateTable ConexionesConector` (`Id int` identity, `TenantId int`,
  `TipoConector varchar(40)`, `Nombre varchar(100)`, `Codigo varchar(40)`, `ParaQueSirve varchar(500)`,
  `Activa/LecturaSinAprobacion tinyint(1)`, `Alcance int`, `ConfiguracionJson text`, `SecretosProtegidos text`,
  `SecretosNombres varchar(500)`, `SecretosActualizadosAt datetime(6)`, `MaxLlamadasPorTarea int`,
  `UltimaPrueba*`, `VersionToken int` + auditoría y baja lógica) y `CreateTable LlamadasConector` (`Id bigint`
  identity, `TenantId`, `ConexionConectorId`, `TareaAgenteId int?`, `UsuarioId varchar(450)`,
  `Herramienta varchar(60)`, `Metodo varchar(10)`, `Destino varchar(500)`, `Resultado int`, `CodigoHttp int?`,
  `Milisegundos`, `BytesRespuesta`, `Mensaje varchar(500)`, `ConAprobacion`, `CreadoAt`). FK **Restrict** a `Tenants`,
  `ConexionesConector` y `TareasAgente`. `Down` = `DropTable` de las dos. **Ninguna tabla existente se modifica.**
- **Ajuste manual (lección de M2/M4, confirmada de nuevo):** el proveedor MySQL **ignora `stored: true`** y creaba
  `CodigoVigente` y `NombreVigente` como **VIRTUAL**. Se sacaron del `CreateTable` y se agregan con
  `migrationBuilder.Sql(... STORED NULL)` antes de sus índices únicos, como en `OrganizacionM2` y `AgentesOrganizacionM4`.
  Verificado en la base: `STORED GENERATED` en las dos.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-16**, con `database update ConocimientoRubroM10` (Down OK,
  las dos tablas desaparecen) y `database update` otra vez; `has-pending-model-changes` limpio.
- Verificado por SQL (`scratchpad/verificar-m11.sql` y `verificar-m11b.sql`, transacción revertida): tipos y largos
  exactos; **1062 real** en `(TenantId, CodigoVigente)` y en `(TenantId, NombreVigente)`; el **mismo código en otra
  organización entra**; con `DeletedAt` puesto las dos columnas generadas pasan a NULL y **el código se puede reusar**;
  **1451 real** al borrar una conexión con historial y **1452** al registrar una llamada de una conexión inexistente;
  `EXPLAIN` del conteo del tope por tarea y de la búsqueda por código resuelven por índice (`ref`, nunca `ALL`);
  collation `utf8mb4_0900_ai_ci` → la unicidad del código es **insensible a mayúsculas y tildes** (`CRM-Prueba` choca
  con `crm-prueba`), que es lo que se busca porque el código se normaliza a minúsculas al guardarlo. **0 restos** tras
  el ROLLBACK.

### Archivos y capas modificadas M11
**Domain** — Nuevos: `Entities/Conectores.cs` (`ConexionConector`, `LlamadaConector`), `Enums/EnumsConectores.cs`
(`AlcanceConexion`, `ResultadoLlamadaConector`).

**Application** — Nuevos: `Settings/ConectoresOptions.cs`, `Motor/NombresHerramientasConectores.cs`,
`DTOs/ConectoresDtos.cs` (+ `MensajesConectores`), `Interfaces/IConectores.cs` (`IConectorTipo`, `IRegistroConectores`,
`IGuardiaDestinoHttp`, `IConexionConectorService`). Modificados: `Motor/IMotorAgentes.cs`
(`IHerramientaAprobacionPorLlamada`), `Interfaces/IPermisosOrganizacion.cs` (2 permisos).

**Infrastructure** — Nuevos: `Services/Conectores/GuardiaDestinoHttp.cs`, `ConectorHttpGenerico.cs`,
`ConexionConectorService.cs`, `HerramientasConectores.cs`, `RegistroConectores.cs`,
`Data/Configurations/ConectoresConfigurations.cs`, migración `Data/Migrations/20260916141804_ConectoresM11.cs`
(+ Designer y snapshot). Modificados: `Services/Motor/ProcesadorTareas.cs` (herramientas por tenant +
`NecesitaAprobacionAsync` en 3 puntos), `Services/Motor/ServicioTareas.cs` (encadenado de `Resumir`),
`Services/Motor/ProveedorModeloSimulado.cs` (`GuionConectores`),
`Services/Subagentes/ResumenHerramientasPlataforma.cs` (rótulo del pedido), `Services/ValidacionArranque.cs`
(corte por `PermitirDestinosPrivados`), `Services/Organizacion/PermisosOrganizacion.cs`, `Data/AppDbContext.cs`
(2 DbSet + exclusiones de audit trail), `DependencyInjection.cs` (registro + cliente HTTP con `ConnectCallback`).

**Web** — Nuevos: `Controllers/ConexionesController.cs`, `Models/ConectoresViewModels.cs`, vistas
`Conexiones/{Index, Form, Uso, _ScriptAcciones}.cshtml` y `Clientes/Conexiones.cshtml`. Modificados:
`Controllers/ClientesController.cs` (1 acción), `Views/Clientes/Details.cshtml` (botón),
`Views/Shared/_Layout.cshtml` (ítem "Conexiones"), `appsettings.json` (sección `Conectores`),
`appsettings.Development.json` y `appsettings.Production.example.json`.

**Admin** — `Program.cs`: verbo `conexiones <tenantSlug>` y ayuda.
**Tests**: nuevo `ConectoresTests.cs` (54 con sus casos de Theory) e `Infra/ServidorLocalDePrueba.cs`.
**Repo**: `docs/diseno-organizacion-roles-reglas.md` (M11 ✅) y `PLAN-IMPLEMENTACION.md`.

### Evidencia de build y tests M11
- `dotnet build OlvidataAgentes.slnx`: **0 errores**. 2 advertencias **preexistentes** que aparecen solo en compilación
  completa y no son de M11 (`xUnit2013` en `ReglasPropuestasAgentesTests` y `CS0114` en `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **392 OK / 0 fallidos** (338 previos + 54 nuevos).
- **Los 4 goldens de hash de contexto intactos**, más el golden nuevo de M11: el hash de una tarea es el mismo con y
  sin conexiones activas, y el prompt de sistema es idéntico.
- **Casos de SSRF cubiertos** (todos verdes): `localhost`/`127.0.0.1`/`127.1.2.3`, `0.0.0.0`, `10.x`, `172.16.x`,
  `192.168.x`, `169.254.169.254` (con mensaje propio de metadata de nube), `169.254.x`, `100.64.x`, multicast, `::1`,
  `fe80::`, `fd00::`, `::ffff:127.0.0.1`; dominio fuera de la lista blanca, subdominio no listado, el apex de un
  comodín, el mismo host en otro puerto, `http` sin TLS, usuario y contraseña en la URL, una IP interna escrita a mano
  aunque esté en la lista blanca, **redirección a un destino no permitido** y una ruta que apunta a otro host.
- **Conector probado contra un servidor local** (`ServidorLocalDePrueba`, 127.0.0.1, puerto que elige el sistema):
  consulta con sus encabezados, error 503 del sistema externo, respuesta más grande que el tope, redirección permitida
  y no permitida, método no habilitado y tiempo de espera agotado. **Cero salidas a internet.**
- Lecciones: (1) escribir una columna de la conexión dentro del commit del motor **acopla su token de concurrencia a la
  tarea** — el "último uso" se calcula del historial; (2) el proveedor MySQL sigue ignorando `stored: true` en
  `CreateTable`, hay que escribir las columnas generadas a mano (tercera vez: M2, M4, M11); (3) para que una decisión de
  seguridad sea confiable tiene que ser **fail-closed en el motor**, no en la herramienta: `RequiereAprobacion` queda en
  true y el motor consulta, así un error nuestro pide aprobación en vez de dejar pasar; (4) validar la IP en el
  `ConnectCallback` **y conectar a esa misma dirección** es lo único que cierra el DNS rebinding — resolver antes y
  conectar por nombre deja una ventana.

### Riesgos residuales M11
- **No hay ningún conector concreto** (a propósito): el HTTP genérico es el ejemplo. Gmail, Drive y ARCA necesitan
  OAuth y refresco de tokens, que M11 **no** resuelve (las credenciales son estáticas, en encabezados).
- **Nunca se llamó a un sistema externo real**: todo se probó contra un servidor local. Lo que falta antes de conectar
  uno de verdad está en "Próximos pasos".
- **La revisión de destinos no cubre un proxy corporativo ni IPv6 detrás de NAT64**: si el hosting mete un proxy, el
  `ConnectCallback` deja de ver la IP real del destino. Hay que verificarlo en SmarterASP antes de habilitar conectores
  en producción.
- **Sin reintentos**: un error del sistema externo vuelve al agente y el agente decide. Puede consumir llamadas del
  tope sin resolver nada.
- **El alcance no llega a nivel de área** (DI-M11-4) y el **nivel de aprobación es siempre Director** (DI-M11-2): las
  dos son deuda consciente, no olvidos.
- **`MaxCaracteresParaElAgente` recorta la respuesta sin paginar**: si un sistema externo devuelve una lista larga, el
  agente ve el principio. No hay "traeme la página siguiente".
- **Data Protection**: si se pierden las claves de `keys/`, las credenciales guardadas quedan ilegibles. El código lo
  detecta y lo deja en el log ("hay que volver a cargarlos"), pero la llamada va a fallar por credenciales.
- Verificación visual pendiente (QA): listado, alta, edición con credenciales ya guardadas, historial, vista de staff,
  "Ver pasos", tarjeta de aprobación, mobile 390 y ambos temas.

### Proximos pasos pendientes M11
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M11).
- **Antes de conectar un sistema real**: (1) confirmar que el hosting no mete un proxy que anule la revisión de IP;
  (2) decidir con Joaquín si un conector concreto necesita OAuth y, si sí, diseñar el refresco de tokens; (3) definir
  qué pasa cuando una credencial vence (hoy la llamada falla y queda en el historial, sin aviso al Director);
  (4) revisar con un caso real si el tope de llamadas por tarea y el de KB alcanzan.
- Evaluar avisos al Director cuando una conexión empieza a fallar seguido.
- Deuda fuera de alcance: alcance por área, reintentos, paginación de respuestas, `dotnet-ef` 10.0.2 más vieja que el
  runtime 10.0.9.

---

# M10 — Base de conocimiento por rubro

Estado: **implementada 2026-09-16, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M10
(RF-M10-01..13, CA-M10-01..12), `2-disenador-funcional.md` M10 (D-M10-1..10, P-M10-01/02) y `3-arquitecto-mvc.md` M10
(RT-M10-01..09), aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto
personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Una entrega, una migración: `ConocimientoRubroM10`.
**Sin contenido real de ningún rubro** (solo un ejemplo de plantilla), **sin una sola llamada a Anthropic**, sin commits.
Mcp y Cli sin tocar (solo compilan).

### Escaneo de reutilizacion M10
| Fuente | Qué se tomó | Grado |
|---|---|---|
| `docs/patrones/catalogo.yml` → **PAT-033** (workspace de documentos por cliente con herramientas de solo lectura) | El patrón entero: clase base con guardas, `PatronLike` con escape "!", recorte en memoria con `IgnoreCase\|IgnoreNonSpace`, serializador JSON escapado, `Resumir` para "Ver pasos", tabla hija sin baja lógica | Literal (mismo patrón, otro eje: rubro en vez de cliente) |
| Template M5 `HerramientasDocumentos.Json` y `PatronLike` | **Se llaman directamente**, no se copiaron: son del mismo assembly y ya están probados | Literal (reuso de código) |
| Template núcleo `ImportadorRubro.ProcesarAsync` | La sección `conocimiento:` es una llamada más al mismo método (mismo hash, mismo "sin cambios no crea versión", mismo Borrador) | Literal (extensión) |
| Template M6 (acciones de demostración) y M5 (documentos) en `ProcesadorTareas` | "Herramientas agregadas a la lista de la solicitud sin tocar el prompt de sistema" | Literal (patrón del repo) |
| Template M1 `PreparadorTareaTrabajo.SuscripcionVigenteAsync` | Criterio de suscripción vigente al rubro, idéntico | Literal |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún otro proyecto tiene "base de conocimiento consultable por un agente". Lo más cercano es la búsqueda por columnas de DataTables, que no aplica | Sin match |
| PAT-042 | **Creado** en el catálogo: "base de conocimiento del proveedor por rubro, consultable por herramientas" | Nuevo |

### Qué se hizo

1. **Un tipo de artefacto más (RF-M10-01, RT-M10-01).** `TipoArtefacto.Conocimiento = 5`. Un documento de conocimiento
   es un `Artefacto` con sus `ArtefactoVersion`: hereda el versionado por hash, el Borrador → Evaluada → Publicada, el
   gate de `IVersionadoService`, la pantalla de la versión y la trazabilidad al archivo de origen. Lo único nuevo es
   `FragmentosConocimiento`.
2. **Troceo determinístico al importar (RF-M10-02, RT-M10-02).** `TroceadorConocimiento.Trocear` (Application, función
   pura): encabezados ATX `#`…`######`, bloques de código ignorados, ruta de encabezados como fuente
   ("Captación › Documentación mínima"), preámbulo en "Introducción", secciones vacías descartadas y secciones largas
   partidas por párrafo en "(parte N de M)" sin cortar palabras.
3. **Manifiesto (RF-M10-01, RT-M10-08).** Sección `conocimiento:` con el mismo `{glob|archivo}` que el resto; rechazada
   con advertencia en el rubro "plataforma". El importador reporta documentos y secciones troceadas.
4. **Tres herramientas de solo lectura (RF-M10-04..08).** `conocimiento_listar`, `conocimiento_buscar` y
   `conocimiento_leer`, con las guardas resueltas contra la base: tarea de trabajo, rubro **de la tarea** (nunca de la
   entrada del modelo), rubro activo y distinto de "plataforma", suscripción vigente y **solo versiones publicadas**.
5. **El contexto no cambia (RF-M10-04, RT-M10-03).** `ProcesadorTareas` las agrega a `permitidas` solo si el rubro tiene
   material publicado. Los 4 formatos y sus hashes quedan intactos (3 goldens previos + un golden nuevo propio).
6. **"Ver pasos" en palabras (RF-M10-09, D-M10-6).** `HerramientasConocimiento.Resumir` se encadena en `ServicioTareas`
   entre el de documentos y el de plataforma; `_PasosTurno.cshtml` oculta los pedidos (se explican en el resultado) y
   usa "Ver lo que leyó" para la lectura.
7. **Pantallas (RF-M10-10/11).** Staff: `Nucleo/Conocimiento/{rubro}` (tarjetas + tabla) y
   `Nucleo/VersionConocimiento/{versionId}` (secciones plegadas), con entradas desde la ficha del rubro y desde la
   versión. Miembro: `Conocimiento/Index` ("Material de Olvidata" en el menú), agrupado por rubro y **sin texto**.
8. **Simulador (RF-M10-12, D-M10-9).** `GuionConocimiento`: listar + buscar → leer → cierra citando documento y sección.
   Se dispara por el pedido ("conocimiento", "guía" o "material") con los nombres **exactos** de las herramientas.
9. **Consola Admin.** `conocimiento <rubro>` y contadores en `importar`.
10. **Ejemplo de plantilla (RF-M10-13).** `nucleo/rubros/_plantilla/conocimiento/00-ejemplo-plantilla.md`, titulado
    "EJEMPLO DE PLANTILLA — no es contenido real", más la sección comentada en `_plantilla/rubro.yml`.

### Decisiones de implementacion M10 (ambigüedades resueltas)
- **DI-M10-1 El conocimiento es un artefacto, no una entidad paralela.** La otra opción era copiar el modelo de M8
  (`ConjuntoCasos` / `VersionConjuntoCasos`), pero los casos **no se publican** y el conocimiento sí: replicar el gate,
  los estados y las pantallas habría sido escribir de nuevo lo que `Artefacto` ya hace. Costo: hay que acordarse de
  excluir el tipo nuevo en los dos caminos que sirven contenido (hecho, y con test).
- **DI-M10-2 El rubro sale de la tarea, no de `ContextoHerramienta`.** No se tocó el record (lo usan todas las
  herramientas del sistema): la clase base consulta `TareaAgente → ArtefactoVersion → Artefacto.RubroId`. Una consulta
  más por llamada a cambio de no tocar una firma compartida ni poder pasarle un rubro equivocado.
- **DI-M10-3 Se habilita por RUBRO, no por licencia (D-M10-5).** Todo el material publicado del rubro está disponible
  para toda organización con suscripción vigente a ese rubro. Cobrarlo aparte sería una condición más en una consulta.
- **DI-M10-4 Bug encontrado contra datos reales: la ruta de encabezados.** La primera versión indexaba la ruta por el
  número de nivel y rellenaba los faltantes con "…". Importando el ejemplo de plantilla real (que arranca en `##`)
  salió `… › Cómo se trocea › Buenas prácticas › Qué NO va acá`, con un hermano convertido en hijo. Se reescribió con
  una **pila que guarda el nivel de cada encabezado** y desapila mientras el tope sea igual o más profundo. Test
  dedicado con el caso real.
- **DI-M10-5 Sin navegación de vuelta en `FragmentoConocimiento`.** `ArtefactoVersion` tiene baja lógica y el fragmento
  no: con navegación, EF levanta la advertencia 10622 ("required end of a relationship with a filtered entity"). Se
  configuró con `HasOne<ArtefactoVersion>().WithMany(v => v.Fragmentos)`, igual que `DocumentoCarteraParte`. Verificado:
  el modelo sigue con las **2 advertencias 10622 preexistentes** (Licencia), ninguna nueva.
- **DI-M10-6 `HerramientasDocumentos.Json` y `PatronLike` se llaman, no se copian.** Son del mismo assembly
  (`Json` es `internal`, `PatronLike` es público) y ya están probados y corregidos por QA de M5. Copiarlos habría
  creado dos verdades para el mismo escape.
- **DI-M10-7 `MaxCaracteresFragmento` solo aplica al importar.** El troceo queda congelado en la versión: bajarlo
  después no reescribe nada, hay que reimportar. Está dicho en `appsettings.json` y en RT-M10-09.
- **DI-M10-8 Listado de staff sin DataTables.** El resto del Núcleo IP (Index, Rubro) usa tablas planas y son listas
  de piezas del núcleo, de decenas de filas. Se siguió la convención local en vez de traer DataTables server-side para
  una tabla que no lo necesita.
- **DI-M10-9 Sin gate de pruebas automáticas (RT-M10-07).** `IGateEvaluacion.ExigePruebas` no se tocó: el conocimiento
  no es un prompt ejecutable. Verificado de punta a punta con la consola (`importar → evaluar --aprobada → publicar`).

### Migraciones EF generadas M10
- `20260916133122_ConocimientoRubroM10` — `CreateTable FragmentosConocimiento` (`Id bigint` identity,
  `ArtefactoVersionId int`, `Numero int`, `Seccion varchar(400)`, `Texto mediumtext`), único
  `(ArtefactoVersionId, Numero)` y FK a `ArtefactoVersiones` **Restrict**. `Down` = `DropTable`. **Ninguna tabla
  existente se modifica**: `TipoArtefacto` se guarda como int y el valor 5 no necesita migración.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-16**, con `database update EvaluacionAutomaticaM8` (Down
  OK, con fragmentos cargados) y `database update` otra vez; `has-pending-model-changes` limpio.
- Verificado por SQL (`scratchpad/verificar-m10.sql` y `verificar-m10b.sql`, transacción revertida): tipos y largos
  exactos; **1062 real** en `(ArtefactoVersionId, Numero)`; **1451 real** al borrar la versión (FK Restrict);
  collation `utf8mb4_0900_ai_ci` → LIKE insensible a mayúsculas **y tildes** (y ñ = n, igual que
  `CompareOptions.IgnoreNonSpace` en memoria, así el pre-filtro nunca descarta de menos); `%` y `_` escapados con `!`
  quedan literales; `EXPLAIN` de la lectura por número usa el índice único (`range`, `Using index condition`) y el join
  de la búsqueda resuelve `v` y `a` por `eq_ref` sobre PRIMARY. **0 restos** tras el ROLLBACK.
- **Importación real verificada** con el ejemplo de plantilla: `importar` → 1 documento, 5 secciones; reimportar sin
  cambios → "1 sin cambios, 0 secciones"; `evaluar --aprobada` → Evaluada; `publicar` → publicada;
  `conocimiento inmobiliario` → "v1 publicada, 5 secciones". **Ninguna llamada a Anthropic.**

### Archivos y capas modificadas M10
**Domain** — Nuevos: `Entities/Conocimiento.cs` (`FragmentoConocimiento`). Modificados: `Enums/EnumsAgentes.cs`
(`TipoArtefacto.Conocimiento = 5`), `Entities/Artefacto.cs` (`ArtefactoVersion.Fragmentos`).

**Application** — Nuevos: `Settings/ConocimientoOptions.cs`, `Motor/NotaConocimiento.cs`
(`NombresHerramientasConocimiento`), `DTOs/ConocimientoDtos.cs` (+ `MensajesConocimiento`),
`Interfaces/IConocimientoNucleo.cs` (`IConocimientoService`), `Helpers/TroceadorConocimiento.cs`. Modificados:
`Interfaces/INucleoServices.cs` (doc de `ListarArtefactosPublicadosAsync`), `DTOs/AgentesDtos.cs` (contadores de
conocimiento en `ImportacionResultadoDto`).

**Infrastructure** — Nuevos: `Services/Conocimiento/HerramientasConocimiento.cs` (3 herramientas + base + `Resumir`),
`Services/Conocimiento/ConocimientoService.cs`, `Data/Configurations/ConocimientoConfigurations.cs`, migración
`Data/Migrations/20260916133122_ConocimientoRubroM10.cs` (+ Designer y snapshot). Modificados:
`Services/Nucleo/ImportadorRubro.cs` (sección `conocimiento:` + troceo), `Services/Nucleo/CatalogoNucleo.cs` (exclusión
en los dos caminos que sirven contenido), `Services/Motor/ProcesadorTareas.cs` (herramientas + `HayConocimientoPublicadoAsync`),
`Services/Motor/ServicioTareas.cs` (encadenado de `Resumir`), `Services/Motor/ProveedorModeloSimulado.cs`
(`GuionConocimiento`), `Data/AppDbContext.cs` (DbSet), `DependencyInjection.cs`.

**Web** — Nuevos: `Controllers/ConocimientoController.cs`, `Models/ConocimientoViewModels.cs`, vistas
`Nucleo/Conocimiento.cshtml`, `Nucleo/VersionConocimiento.cshtml`, `Conocimiento/Index.cshtml`. Modificados:
`Controllers/NucleoController.cs` (2 acciones), `Views/Nucleo/{Rubro, Version}.cshtml`, `Views/Tareas/_PasosTurno.cshtml`,
`Views/Shared/_Layout.cshtml` (ítem "Material de Olvidata"), `appsettings.json` (sección `Conocimiento`).

**Admin** — `Program.cs`: verbo `conocimiento <rubro>`, contadores en `importar` y ayuda.

**Núcleo**: `nucleo/rubros/_plantilla/conocimiento/00-ejemplo-plantilla.md` (**plantilla, sin contenido real**) y la
sección `conocimiento:` comentada en `_plantilla/rubro.yml`.
**Tests**: nuevo `ConocimientoTests.cs` (19). **Repo**: `docs/diseno-organizacion-roles-reglas.md` (M10 ✅) y
`PLAN-IMPLEMENTACION.md`.

### Evidencia de build y tests M10
- `dotnet build OlvidataAgentes.slnx`: **0 errores, 0 advertencias**.
- `dotnet test tests/OlvidataAgentes.Tests`: **338 OK / 0 fallidos** (319 previos + 19 nuevos).
- **Los 4 goldens de hash de contexto (formatos 1, 2, 3 y 4) intactos**, más el golden nuevo de M10: el hash de una
  tarea es el mismo con y sin material publicado en el rubro.
- Lecciones: (1) armar una ruta de encabezados **indexando por el número de nivel** se rompe con documentos que
  arrancan en `##` o que saltean un nivel — va una pila con el nivel de cada encabezado; (2) `utf8mb4_0900_ai_ci`
  ignora tildes **y** trata ñ = n en LIKE, lo mismo que `CompareOptions.IgnoreNonSpace` en .NET: el pre-filtro de la
  base y la verificación en memoria coinciden, que es justo lo que hace falta para que la búsqueda no pierda filas;
  (3) una tabla hija sin baja lógica colgada de un padre que sí la tiene necesita `HasOne<T>()` **sin navegación de
  vuelta**, o EF avisa 10622 en cada arranque.

### Riesgos residuales M10
- **No hay contenido real de ningún rubro** (a propósito): lo único publicado en dev es el ejemplo de plantilla. La
  calidad de las búsquedas con material real está sin medir.
- **Búsqueda por LIKE** (RT-M10-05): escanea los fragmentos publicados del rubro. Con decenas de documentos es
  trivial; con cientos hay que evaluar FULLTEXT. Es deuda consciente, no un olvido.
- **Ningún agente pidió todavía el material con el modelo real**: cuánto tokens agrega una consulta y si el agente la
  usa cuando corresponde son estimaciones hasta la primera corrida real.
- **`MaxCaracteresFragmento` congelado en la versión**: cambiarlo pide reimportar. Está documentado en los dos lados.
- **El ejemplo de plantilla quedó importado y PUBLICADO en `olvidata_agentes_dev`** (rubro inmobiliario) para que QA
  tenga con qué probar. Para sacarlo: borrar de `FragmentosConocimiento`, `EvaluacionesVersion`, `ArtefactoVersiones`
  y `Artefactos` donde `Tipo = 5`. **No está en ninguna base que no sea la local.**
- Verificación visual pendiente (QA): material del rubro, secciones de una versión, pantalla del miembro, "Ver pasos"
  con los tres rótulos, mobile 390 y ambos temas.

### Proximos pasos pendientes M10
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M10).
- Escribir material real del primer rubro en su repo fuente (fuera de este repositorio) e importarlo.
- Evaluar si el conocimiento merece su propio tipo de caso en M8 (hoy no: no es un prompt ejecutable).
- Deuda fuera de alcance: índice FULLTEXT; `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9.

---

# M9 — Preparación de despliegue (local: preparar, no desplegar)

Estado: **implementada 2026-09-16, pendiente de QA**. Entrada: `1-analista-funcional.md` M9 (RF-M9-01..06,
CA-M9-01..06), `2-disenador-funcional.md` M9 (D-M9-1..3) y `3-arquitecto-mvc.md` M9 (RT-M9-01..08), aprobados sin gate
por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal).
Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. **Sin migración EF.** **Nada desplegado, ningún servidor tocado,
ninguna credencial real usada, ninguna llamada a Anthropic, sin commits.** Mcp y Cli sin tocar (solo compilan).

### Escaneo de reutilizacion M9
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template blankproject (este repo) — `DatabaseHealthCheck` / `SmtpHealthCheck` | Los dos chequeos nuevos copian el contrato y el estilo de mensaje | Literal (extensión) |
| Template blankproject — `web.config` ANCM OutOfProcess + redirect HTTPS + compresión y rate limiting ya en `Program.cs` | No hubo que agregar nada de compresión ni de estáticos: ya estaba | Literal |
| Template M1/M8 — lease + `Version` + `Intentos` de `TareaAgente` y `CorridaEvaluacion` | `RecuperadorLeases` usa el mismo token de concurrencia y el mismo `IgnoreQueryFilters([FiltroTenant])` | Literal (patrón del repo) |
| Template M2 — `ResolvedorSesion` + `SesionOrganizacionMiddleware` (fail-closed, caché 60 s) | PA-05 entra por el mismo camino del usuario bloqueado, sin inventar otro | Literal (extensión) |
| Escaneo `docs/*/definiciones/5-implementador.md` del estudio | Ningún otro proyecto tiene "preparación de despliegue" como feature con validación de arranque y health checks propios; los deploys a SmarterASP existen como **práctica** (Web Deploy, skip-rules, subir sin borrar) y de ahí salen §3 y §8 del documento | Práctica, no código |

### Qué se hizo

1. **Publicación (RF-M9-01).** Perfil `Properties/PublishProfiles/SmarterASP.pubxml` (FileSystem → `publish/web`,
   ignorado por git), con `EnvironmentName=Production`, exclusión de `appsettings.Development.json` y skip-rules de
   Web Deploy para `keys`, `App_Data`, `Logs` y `appsettings.Production.json`. Comando único:
   `dotnet publish src/OlvidataAgentes.Web -c Release -p:PublishProfile=SmarterASP`.
   **Verificado sobre el paquete real:** `web.config` con `ASPNETCORE_ENVIRONMENT=Production`, `hostingModel=OutOfProcess`
   y el redirect a HTTPS; `wwwroot` con `.br`/`.gz` precomprimidos; **sin** `appsettings.Development.json`, sin
   `appsettings.Production.example.json`, sin `keys/`, sin `App_Data/`, sin `Logs/`. 138 MB, 70 archivos en la raíz
   (`runtimes/` de todos los SO se lleva 68 MB).
2. **Configuración (RF-M9-02).** `appsettings.Production.example.json` versionado y **excluido del publish**, con todas
   las secciones que el sistema usa hoy y los secretos marcados como variable de entorno.
   `ValidacionArranque` (Infrastructure) revisa configuración y carpetas y, fuera de Development, **corta el arranque**
   con la lista de claves. El bootstrap logger ahora escribe también en `Logs/arranque-*.log` para que el motivo se
   pueda leer por FTP (RT-M9-02).
3. **Carpetas que sobreviven (RF-M9-03).** `keys/`, documentos de clientes y `Logs/` documentadas en
   `docs/deploy-smarterasp.md` §3 con su regla por método de subida; comprobación de escritura al arrancar (las dos
   primeras cortan el arranque, los logs avisan).
4. **Salud (RF-M9-04).** `DocumentosHealthCheck` (sonda de escritura) y `MotorAgentesHealthCheck` (latido del worker,
   registrado solo donde el worker corre). `/health` pasa a JSON por chequeo, **sin excepciones ni stack traces**;
   `/health/vivo` anónimo para el ping externo. Serilog de producción en la plantilla: dos archivos rotativos por día y
   por tamaño (20 MB), operación 14 días y errores 60, `shared: true` por el reciclado solapado de ANCM.
5. **Checklist (RF-M9-05).** `docs/deploy-smarterasp.md`: requisitos, publicar, configurar, carpetas, 11 pasos en orden,
   AlwaysRunning, verificación y humo mínimo, qué no subir, rollback y riesgos del día.
6. **Higiene (RF-M9-06).** El modelo simulado y las herramientas de demostración **ya estaban cubiertos por tests desde
   M3b/M6** (`Development` + `Anthropic:Simulado` explícito; `Production`/`Testing` → 0 registros) — se verificó y no
   hizo falta agregar nada. PA-05 implementado (abajo).

### PA resueltos y abiertos

- **PA-03 (resuelto).** `RecuperadorLeases` + `IProcesosLocales`: al arrancar, el worker vence los leases de procesos
  muertos **de esta misma máquina** y retoma en el primer ciclo (segundos en vez de hasta 5 minutos). No se bajó
  `LeaseSegundos` porque el lease no se renueva durante el turno (RT-M9-05). Fail-closed: "no sé si vive" = no se toca.
- **PA-05 (parcial).** `Tenant.Estado` distinto de Activo corta la sesión (`ResolvedorSesion` → `OrganizacionSuspendida`
  en `IContextoUsuario`) y bloquea el login con un texto con salida. **Abierto**: el staff sigue sin UI para editar
  nombre/email/rol/estado de miembros, las pantallas legadas siguen sin diseño nuevo, y una tarea ya encolada de una
  organización suspendida sigue ejecutándose en el worker.
- **PA-07 (abierto, no depende del código).** Es una respuesta de soporte de SmarterASP. Queda documentado en
  `docs/deploy-smarterasp.md` §5 con el plan B implementado: ping externo a `/health/vivo`.

### Archivos

**Nuevos** — `src/OlvidataAgentes.Application/Motor/LatidoMotor.cs`, `.../Motor/IRecuperadorLeases.cs` (+ `IProcesosLocales`);
`src/OlvidataAgentes.Infrastructure/Services/ValidacionArranque.cs`, `.../Services/DocumentosHealthCheck.cs`,
`.../Services/Motor/MotorAgentesHealthCheck.cs`, `.../Services/Motor/RecuperadorLeases.cs`, `.../Services/Motor/ProcesosLocales.cs`;
`src/OlvidataAgentes.Web/Helpers/SaludJson.cs`, `.../appsettings.Production.example.json`,
`.../Properties/PublishProfiles/SmarterASP.pubxml`; `docs/deploy-smarterasp.md`; `tests/OlvidataAgentes.Tests/DespliegueTests.cs`.

**Modificados** — `Infrastructure/DependencyInjection.cs` (registros y 2 health checks), `Services/Motor/MotorAgentesWorker.cs`
(latido + recuperación al arranque), `Services/Organizacion/ResolvedorSesion.cs` y `ContextoUsuario.cs` +
`Application/Interfaces/IContextoUsuario.cs` (PA-05), `Web/Middleware/SesionOrganizacionMiddleware.cs`,
`Web/Controllers/AccountController.cs`, `Web/Program.cs` (bootstrap logger, revisión de arranque, endpoints de salud),
`Web/OlvidataAgentes.Web.csproj`.

### Evidencia

`dotnet build OlvidataAgentes.slnx` → **0 errores** (2 advertencias preexistentes: `HomeController.StatusCode` y un
`xUnit2013` de M7a). `dotnet test tests/OlvidataAgentes.Tests` → **319/319 OK** (287 previos + 32 nuevos).
`dotnet publish` con el perfil → paquete verificado en `publish/web` (contenido y `web.config` revisados a mano).
**Ningún servidor tocado, ninguna llamada a Anthropic, sin migraciones, sin commits.**

### Pruebas mínimas para QA

1. **Revisión de arranque**: correr el portal con `ASPNETCORE_ENVIRONMENT=Production` y una clave crítica vacía
   (por ejemplo `Anthropic__ApiKey=`): tiene que **no arrancar** y dejar el motivo en `Logs/arranque-*.log`, sin valores.
   Repetir en Development: arranca igual y solo avisa.
2. **`/health`**: entrar como SuperUsuario → JSON con `mysql`, `smtp`, `documentos` y `motor`. Apuntar
   `Documentos:RaizAlmacenamiento` a una carpeta sin permisos y ver `documentos` en `Unhealthy` con texto claro.
   Poner `MotorAgentes:Habilitado=false` → `motor` en `Degraded`. Verificar que no aparezca ningún stack trace.
3. **`/health/vivo`**: sin loguearse, responde `vivo` en texto plano. Como usuario común, `/health` da 403.
4. **PA-03**: con una tarea En curso, matar el proceso del portal y volver a levantarlo. La tarea tiene que retomarse
   en segundos (log "Arranque: N tarea/s… se retoman en este ciclo"), no a los 5 minutos.
5. **PA-05**: con un Director logueado, poner su organización en `Suspendido` por SQL, esperar 60 s (caché) y navegar:
   vuelve al login con el mensaje de empresa suspendida. Intentar entrar de nuevo: mismo mensaje, sin rulo. Un
   SuperUsuario sin organización entra normal. Volver a `Activo` y verificar que entra.
6. **Paquete**: correr el `dotnet publish` del documento y verificar `publish/web/web.config` con
   `ASPNETCORE_ENVIRONMENT=Production` y que no esté `appsettings.Development.json`.
7. **Regresión**: login, portal de cliente y backoffice de M2–M8 sin 5xx (M9 tocó el camino de sesión de todo el portal).

# M8 — Evaluación automática de prompts (núcleo)

Estado: **implementada 2026-09-16, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M8 (RF-M8-01..25,
CA-M8-01..23), `2-disenador-funcional.md` M8 (D-M8-1..26, P-M8-01..08) y `3-arquitecto-mvc.md` M8 (RT-M8-01..13),
aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal).
Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Una entrega, una migración: `EvaluacionAutomaticaM8`.
**Agentes de la organización fuera del alcance (P1).** Sin contenido de rubros, **sin una sola llamada a Anthropic**
(todo con el doble guionado), sin commits.

### Escaneo de reutilizacion M8
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template núcleo (`ImportadorRubro`: hash del cuerpo, `sinCambios`, `FuenteArchivos {Glob, Archivo}`, advertencias) | Sección `evaluaciones:` con el mismo criterio de hash y "sin cambios no crea versión"; los conjuntos son un artefacto **paralelo** (no `TipoArtefacto`) | Literal (extensión) |
| Template M3/M4/M4b/M7b (`ConstructorContexto`: `ArmarAsync`, `ArmarPlataformaAsync`, `CalcularHash`, `Escapar`, 3 bloques con `Cachear`) | **Render extraído a `Renderizar(ContenidoContexto, formato)`**, compartido por los 4 formatos y por `ArmarEvaluacionAsync` | Refactor sin cambio de comportamiento (RT-M8-01) |
| Template núcleo (`IVersionadoService`, `TipoEvaluacion.Automatica` sin llamador) | El ejecutor es el primer llamador de `automatica: true`; el gate de `PublicarAsync` se extiende | Literal (extensión) |
| Template M1 (`IProveedorModelo`, `RespuestaModelo`, `MotivoFin`, bloques de herramienta, `TelemetriaService.CalcularCosto`) | Bucle propio y corto en `EjecutorCorrida` (no se reusa `ProcesadorTareas`: crearía tareas de una organización cliente) | Patrón del mismo repo |
| Template M6 (`PeriodoGasto`, barra de consumo, "cortar antes de cada llamada") | Bolsa mensual propia de Olvidata y barra reusada; **no pasa por `IControlGasto`** | Literal (patrón) |
| Template M7a (`MotorAgentesWorker` con barridos en scopes con `EstablecerAccesoGlobal()`, lease + `Intentos` + `Version`) | Barrido nuevo de corridas, de a una y fuera de `MaxTareasSimultaneas` | Literal (patrón) |
| Template M2/M5 (policies de staff, DataTables + `FiltrosSesion`, SweetAlert2, escape de texto hostil) | Listado de corridas, modales de cancelación y excepción, bloque de texto de prueba | Literal |
| PAT-040 / PAT-041 | **Creados** en el catálogo con rutas reales (`pendiente_verificar: false` en todas las del repo) | Nuevo |

### Archivos y capas modificadas M8
**Domain** — Nuevos: `Enums/EnumsEvaluacion.cs` (7 enums), `Entities/Evaluaciones.cs` (`ConjuntoCasos`,
`VersionConjuntoCasos`, `CasoEvaluacion`, `CorridaEvaluacion`, `ResultadoCaso`). Modificados: `Enums/EnumsAgentes.cs`
(`CanalUso.Evaluacion = 4`), `Entities/Artefacto.cs` (`EvaluacionVersion` + `CorridaEvaluacionId`, `EsExcepcion`,
`RegistradaPorUsuarioId`, `HashCasos`), `Entities/Tenant.cs` (`EsInterna` + `SlugInterno`).

**Application** — Nuevos: `Settings/EvaluacionOptions.cs`, `DTOs/EvaluacionDtos.cs` (+ `MensajesEvaluacion`),
`Interfaces/IEvaluacionAutomatica.cs` (`ICasosEvaluacionService`, `IEstimadorCorrida`, `ICorridaEvaluacionService`,
`IEjecutorCorrida`, `IRevisorAutomatico`, `IGateEvaluacion`), `Helpers/VerificacionesTexto.cs`, `Helpers/HashCasos.cs`.
Modificados: `Motor/IConstructorContexto.cs` (`ArmarEvaluacionAsync` + `SolicitudContextoEvaluacion`),
`Motor/ModeloConversacion.cs` (`SolicitudModelo.EsquemaSalida` y `SolicitudModelo.Guion` + `GuionEvaluacion`),
`Interfaces/INucleoServices.cs` (`RegistrarEvaluacionAsync` con parámetros opcionales y `RegistrarExcepcionAsync`),
`Helpers/ArgentinaTime.cs` (`ToUtc`), `DTOs/AgentesDtos.cs` (contadores de conjuntos en `ImportacionResultadoDto`).

**Infrastructure** — Nuevos: `Services/Evaluacion/{CasosEvaluacionService, EstimadorCorrida, CorridaEvaluacionService,
EjecutorCorrida, RevisorAutomatico}.cs`, `Data/Configurations/EvaluacionConfigurations.cs`, migración
`Data/Migrations/20260916022048_EvaluacionAutomaticaM8.cs` (+ Designer y snapshot). Modificados:
`Services/Motor/ConstructorContexto.cs` (**extracción del render** + `ArmarEvaluacionAsync`),
`Services/Nucleo/ImportadorRubro.cs` (`ImportarCasosAsync` y el modelo YAML de un archivo de casos),
`Services/Nucleo/VersionadoService.cs` (gate, excepción, `MotivoNoPublicableAsync`),
`Services/Motor/ProveedorModeloAnthropic.cs` (`OutputConfig`), `Services/Motor/ProveedorModeloSimulado.cs`
(guion de evaluación y revisor simulado), `Services/Motor/MotorAgentesWorker.cs` (barrido de corridas),
`Services/Organizacion/MiembroService.cs` y `Services/Licencias/LicenciaService.cs` (rechazo de la organización interna),
`Data/AppDbContext.cs` (5 DbSets), `Data/Configurations/AgentesConfigurations.cs` (Tenant y EvaluacionVersion),
`Data/SeedData.cs` (`AsegurarOrganizacionInternaAsync`), `DependencyInjection.cs`.

**Web** — Nuevos: `Models/EvaluacionViewModels.cs`, `Helpers/PruebasTextos.cs`, vistas
`Nucleo/{Casos, CorrerPruebas, Corrida, Pruebas, _ListaCasos, _ResultadosCorrida, _DetalleCaso, _BloqueTextoPrueba,
_ScriptCorrida}`. Modificados: `Controllers/NucleoController.cs` (11 acciones nuevas),
`Controllers/ClientesController.cs` (excluye la organización interna), `Models/AgentesViewModels.cs`
(`NucleoRubroViewModel.Pruebas`), `Views/Nucleo/{Version, Rubro}.cshtml`, `Views/Shared/_Layout.cshtml`
(ítem "Pruebas de prompts"), `wwwroot/css/site.css`, `appsettings.json` (sección `Evaluacion`).

**Admin** — `Program.cs`: 7 verbos `evaluacion-*`, contadores de casos en `importar`, `publicar-rubro` avisa cuántas
excepciones registra; `appsettings.json` con la tabla de precios (los verbos la necesitan para estimar).

**Núcleo**: `nucleo/plataforma/evaluaciones/` (4 archivos, 15 casos, **borrador para revisar**) y sección `evaluaciones:`
en `plataforma.yml`. **Tests**: nuevos `EvaluacionCasosTests.cs`, `EvaluacionCorridaTests.cs`,
`EvaluacionCalificacionTests.cs`, `EvaluacionGateTests.cs` e `Infra/EntornoM8.cs`; ajustados `NucleoTests.cs` y
`ConstructorContextoTests.cs` (el gate nuevo), `Infra/TestServicios.cs` (precio del revisor).
**Repo**: `docs/diseno-organizacion-roles-reglas.md` (M8 ✅) y `PLAN-IMPLEMENTACION.md` (Fase 2).

### Decisiones de implementacion M8 (ambigüedades resueltas)
- **DI-M8-1 El refactor del render salió byte a byte (RT-M8-01, plan B NO usado):** se extrajo
  `ConstructorContexto.Renderizar(ContenidoContexto, formato)` con el mismo código, sin reordenar ni reformatear.
  `ArmarAsync` y `ArmarPlataformaAsync` pasan a leer de la base y llamar al render; los formatos de plataforma (3 y 4)
  llegan con listas vacías de instrucciones y reglas y salen con un solo bloque, igual que antes. **Los 4 goldens
  (formatos 1, 2, 3 y 4) quedaron verdes en la misma corrida**, y el test nuevo "contexto de caso sin reglas = contexto
  de tarea equivalente" cierra la pinza por el otro lado.
- **DI-M8-2 Salidas estructuradas: SÍ existen en el SDK .NET.** Verificado por compilación contra `Anthropic` 12.47.0:
  `MessageCreateParams.OutputConfig` → `OutputConfig.Format` (`JsonOutputFormat`) → `JsonOutputFormat.Schema`
  (`IReadOnlyDictionary<string, JsonElement>`, **required**). Se agregó `SolicitudModelo.EsquemaSalida` (opcional, null
  en todo el resto del motor) y su mapeo en `ProveedorModeloAnthropic`. **Igual se valida el texto con JSON estricto**:
  un proveedor que no lo soporte (el simulado, el guionado) no puede colar un veredicto que no se entiende.
- **DI-M8-3 El simulador reconoce la evaluación por un marcador propio (lección RT-M7-06):** `SolicitudModelo.Guion`
  (`GuionEvaluacion`) lo pone el ejecutor y lleva la clave del caso, su `RespuestaSimulada` y qué herramientas tienen
  resultado fijo. Nunca se adivina por los nombres de las herramientas. El revisor simulado se reconoce por
  `EsquemaSalida`.
- **DI-M8-4 El gate vive en un solo método:** `VersionadoService.MotivoNoPublicableAsync` devuelve el texto exacto del
  botón deshabilitado y **es el mismo que llama `PublicarAsync`**. `IGateEvaluacion` lo expone a la Web y se registra
  como el propio `VersionadoService` (no hay dos implementaciones que se puedan desincronizar).
- **DI-M8-5 `RequireSuperUsuario` ya existía** (RT-M8-13 resuelto sin cambios): estaba en `Program.cs` desde el
  template. No se tocó `RequireAdministracion` ni el acceso de nadie.
- **DI-M8-6 Dos tests viejos se adaptaron a propósito (CA-M8-16):** `NucleoTests.Evaluar_y_publicar...` y
  `ConstructorContextoTests.Reglas_de_plataforma...` publicaban un Agente y una Regla de plataforma con evaluación
  manual. Con el gate eso ya no alcanza: ahora registran la **excepción de SuperUsuario**, que es el camino real
  mientras esos artefactos no tengan casos. No es una regresión: es la conducta nueva.
- **DI-M8-7 El ejecutor nunca resuelve herramientas:** solo `IRegistroHerramientas.Definiciones(nombres)`. El test usa
  `RegistroHerramientasQueFalla`, que lanza si alguien llama `Obtener`. Los nombres salen del contexto del caso o, si no
  los declara, del frontmatter del artefacto.
- **DI-M8-8 Continuar suma al tope, no lo reemplaza:** `TopeUsd = CostoUsd + tope nuevo`, así "seguí hasta USD 5 más"
  significa lo que dice y los casos ya guardados no se vuelven a correr (se cuentan las llamadas del doble en el test).
- **DI-M8-9 La organización interna se siembra por dos caminos:** `InsertData` por SQL en la migración (idempotente,
  con `WHERE NOT EXISTS` para no chocar con el único de `Slug`) y `SeedData.AsegurarOrganizacionInternaAsync` para bases
  creadas con `EnsureCreated`. El `Down` la borra; si ya tiene `EventoUso`, la FK Restrict hace fallar el DELETE **a
  propósito**.
- **DI-M8-10 Un caso a medio correr no cuenta como fallado:** si tiene menos repeticiones que las esperadas y todas
  pasaron, queda **Pendiente** (no "Falló"). Si no, una corrida cortada por tope mostraría fallas que no ocurrieron.
- **DI-M8-11 La consola Admin se identifica como SuperUsuario explícitamente** (`ConsolaComoSuperUsuario`), y solo en
  los verbos que lo necesitan: los servicios re-verifican el rol con `IContextoUsuario` y no confían en el llamador.
- **DI-M8-12 `publicar-rubro --aprobacion-manual` ahora registra excepciones** en los tipos con gate, y avisa cuántas
  antes de hacerlo. Los demás tipos siguen con evaluación manual común.

### Migraciones EF generadas M8
- `20260916022048_EvaluacionAutomaticaM8` — `CreateTable` de `ConjuntosCasos`, `VersionesConjuntoCasos`,
  `CasosEvaluacion`, `CorridasEvaluacion` y `ResultadosCaso` con sus únicos, índices y FKs Restrict; `AddColumn` en
  `EvaluacionesVersion` (`CorridaEvaluacionId`, `EsExcepcion` default 0, `RegistradaPorUsuarioId`, `HashCasos`) e índice
  `(ArtefactoVersionId, EjecutadaAt)`; `AddColumn Tenants.EsInterna` (default 0) e `INSERT` idempotente de la
  organización técnica `olvidata-interno`. `Down` en orden inverso. **Sin cambios en `TareasAgente`, `PasosTarea` ni
  nada del motor de clientes.**
- **Corrección a mano del scaffold:** EF generaba `DropIndex(IX_EvaluacionesVersion_ArtefactoVersionId)` **antes** de
  crear el compuesto y MySQL lo rechaza (*"Cannot drop index: needed in a foreign key constraint"*, 1553). Se invirtió el
  orden: primero se crea `(ArtefactoVersionId, EjecutadaAt)` —que sostiene la FK igual, por ser la primera columna— y
  recién después se borra el simple. En el `Down`, lo mismo al revés.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-16**, luego `database update AsignacionesAsistenteM7b`
  (Down OK, borra la organización interna) y `database update` otra vez (la recrea); `has-pending-model-changes` limpio.
- Verificado por SQL (`scratchpad/verificar-m8.sql` y `verificar-m8b.sql`, transacción revertida): `decimal(18,6)` en los
  3 campos de plata y los 6 decimales se guardan; `longtext` en pedidos, contextos, respuestas y JSON; **1062 real** en
  `(VersionConjuntoCasosId, Clave)` y en `(CorridaEvaluacionId, CasoEvaluacionId, Repeticion)`; los 4 índices de
  `CorridasEvaluacion` y los 2 de `ResultadosCaso` presentes; organización interna única con `EsInterna = 1` y sin
  límite de gasto; `EXPLAIN` del gasto del mes usa `IX_CorridasEvaluacion_Modo_Periodo` (`ref`), el del gate usa
  `IX_EvaluacionesVersion_ArtefactoVersionId_EjecutadaAt` (`Backward index scan; Using index`) y el de los resultados de
  una corrida usa su índice (`ref`); el del reclamo lista `(Estado, LeaseHasta)` en `possible_keys` (con la tabla vacía
  el optimizador prefiere el PK del `ORDER BY`). **0 restos** tras el ROLLBACK.
- **Importación real verificada**: `importar plataforma.yml` creó 4 conjuntos y 15 casos; reimportar sin cambios da
  "4 sin cambios"; `evaluacion-casos 65` lista 8 casos (3 propios + 5 de la suite común) y `evaluacion-estimar 65` da
  USD 0,91 esperado / USD 6,16 peor caso. **Ninguna corrida creada y ningún `EventoUso` de canal 4**: no se llamó a
  Anthropic.

### Evidencia de build y tests M8
- `dotnet build OlvidataAgentes.slnx`: **0 errores, 0 advertencias** (desapareció hasta la CS0114 preexistente de
  `HomeController`, que sigue igual pero ya no se reporta en esta corrida).
- `dotnet test tests/OlvidataAgentes.Tests`: **287 OK / 0 fallidos** (244 previos + 43 nuevos).
- **Los 4 goldens de hash de contexto (formatos 1, 2, 3 y 4) intactos** después del refactor del render.
- Lecciones: (1) MySQL no deja borrar el índice que sostiene una FK: al reemplazar un índice simple por uno compuesto
  con la misma primera columna, **crear el nuevo antes de borrar el viejo**; (2) YAML plano no admite `:` dentro del
  valor (`nombre: Solo propone: ...` revienta): hay que comillarlo, y el importador lo reporta con el nombre del
  archivo; (3) con el entorno de tests en "Testing", todo lo que depende de `IsDevelopment()` queda cortado: el entorno
  de pruebas de M8 registra un `IHostEnvironment` de Development salvo en el test que justamente verifica el corte.

### Riesgos residuales M8
- **Ninguna corrida real se ejecutó todavía** (S-M8-01, PA-01/PA-13/PA-14): la primera con costo la mira Joaquín, con
  tope de USD 1, sobre el configurador (#65) o una regla de plataforma. Hasta entonces la calidad del revisor, el
  costo real y los umbrales son estimaciones.
- Los **casos iniciales son un borrador sin revisar** (PA-17): están en `nucleo/plataforma/evaluaciones/` e importados
  en dev, pero nadie validó todavía si prueban lo correcto ni si los criterios del revisor están bien redactados.
- **La estimación de costo usa 3 caracteres por token**: es una aproximación conservadora, no un cálculo. Lo que
  gobierna de verdad es el tope, que se verifica contra el costo REAL antes de cada llamada.
- **Un corte entre la llamada pagada y su `SaveChanges` pierde el registro de UNA llamada** (RT-M8-06): es el techo del
  error conocido y documentado.
- El *polling* de la corrida es cada 3 s mientras no termina, con corte a los 5 minutos sin avance (R-M8-12).
- `CorrerPruebas` arma la estimación con un contexto de muestra: si el artefacto no tiene casos o falta una versión del
  núcleo, cae a 2000 tokens estimados.
- Verificación visual pendiente (QA): card de pruebas, pantalla de casos, corrida con avance y filtros, detalle de caso,
  bloques de texto hostil, gate y modal de excepción, listado con gasto del mes, mobile 390 y ambos temas.

### Proximos pasos pendientes M8
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M8).
- PA-17: que Joaquín revise los 15 casos iniciales de `nucleo/plataforma/evaluaciones/` antes de la primera corrida real.
- PA-01 / PA-13 / PA-14: correr, aprobar y publicar las 3 reglas de plataforma, el configurador y el asistente.
- M8b (P1): evaluación de agentes de la organización — el objetivo de la corrida quedó desacoplado para que solo haya
  que agregar un origen, sin migrar datos.
- Deuda fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; advertencia CS0114 de `HomeController`.

---

# M7b — Tareas asignadas a personas y asistente del Director que reparte trabajo

Estado: **implementada 2026-09-16, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M7 (RF-M7b-01..17, CA-M7b-01..16),
`2-disenador-funcional.md` M7 parte M7b (D-M7-12..24, P-M7b-01..09) y `3-arquitecto-mvc.md` M7 parte M7b, aprobados sin gate por
autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.
Segunda mitad de M7 (M7a ya estaba implementada, con QA y commit). Sin contenido de rubros, sin llamadas a Anthropic, sin commits.

### Escaneo de reutilizacion M7b
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M4b (`TipoTarea` + `InstantaneaConfiguracion` + render separado, `IniciarConfiguracionAsync`, `ConfiguracionReglasController`, `_TarjetasPropuesta`/`_ScriptPropuestas`, `PropuestaReglaService` con Fallida/Aplicar todas/YaResuelta, PAT-032) | El asistente ES el configurador con otro prompt: se extrajo `IniciarPlataformaAsync` y `ArmarPlataformaAsync` (formato y declaración por parámetro) y se copió el esqueleto de controller, tarjetas y script | Literal (refactor + patrón del mismo repo) |
| Template M4b (`HerramientaClientesBuscar`) | Misma clase, con la guarda ampliada por `TiposPermitidos` (virtual en la base) al asistente | Literal (extensión) |
| Template M7a (`PreparadorTareaTrabajo`, `IHerramientaDelegacion`, `ResumenHerramientasPlataforma`) | Aplicar una propuesta de tarea de agente usa el preparador tal cual (suscripción, cliente, límite M6, instantánea) | Literal |
| Template M6 (`ContadorAprobacionesViewComponent`, bandeja con pestañas y filtros por columna, SweetAlert2 con textarea y contador, `IControlGasto`) | `ContadorAsignacionesViewComponent`, pantalla Asignaciones, confirmaciones de "hecha" y "cancelar", límite al iniciar la conversación y al aplicar | Literal (patrón del mismo repo) |
| Template M2/M5 (`FiltrosSesion`, `DataTableRequestHelper`, `RespuestasServicio`, proyección anónima + nombres en memoria, tokens de color DI-M5-17) | Grilla, filtros por pestaña, respuestas AJAX, colores de estado | Literal |
| century-21 (`docs/century-21/definiciones/3-arquitecto-mvc.md`: "Tomar"/"Reasignar" con RowVersion y mensaje funcional) | Criterio del conflicto: `VersionToken` con `OriginalValue` y "Otra persona cambió esta asignación. Recargá la página." | Patrón (otro dominio) |
| yoga (`docs/yoga/definiciones/2-disenador-funcional.md`: cuota "Vencida" derivada) | "Vencida" calculada con el día argentino, nunca columna | Patrón |
| verif-m7 / verif-m6 (scratchpad) | Verificador EF → MySQL con organización de prueba y limpieza (`scratchpad/verif-m7b`) | Literal (adaptado) |
| PAT-039 / PAT-032 | PAT-039 completado con rutas reales y gotchas confirmados (`pendiente_verificar: false`); PAT-032 aplicado a un segundo tipo de propuesta | Confirmado |

### Archivos y capas modificadas M7b
**Domain** — Nuevos: `Enums/EnumsAsignaciones.cs` (`EstadoTareaAsignada`, `OrigenTareaAsignada`, `TipoPropuestaTrabajo`, `EstadoPropuestaTrabajo`),
`Entities/TareaAsignada.cs` (`TareaAsignada` + `PropuestaTrabajo`). Modificados: `Enums/EnumsAgentes.cs` (`TipoTarea.AsistenteDirector = 3`),
`Entities/Tareas.cs` (`TareaAgente.TareaAsignadaId`).

**Application** — Nuevos: `Settings/AsignacionesOptions.cs`, `DTOs/AsignacionesDtos.cs` (`MensajesAsignaciones`, `MensajesAsistente`,
`AsignacionDto`, `AsignacionListItemDto`, `PestanaAsignaciones`, `AsignacionFiltros`, `AsignacionDetalleDto`, `AsignacionRefDto`,
`PedidoDesdeAsignacionDto`, `PropuestaTrabajoDto`…), `Interfaces/ITareaAsignadaService.cs`, `Interfaces/IPropuestaTrabajoService.cs`
(+ `IAsistenteDirector`). Modificados: `Motor/NotaSubtarea.cs` (`NombresHerramientasAsistente`), `Motor/IMotorAgentes.cs`
(`CrearTareaDto.TareaAsignadaId`, `TareaDetalleDto` + `EsAsistente`/`EsDePlataforma`/`PropuestasTrabajoPorPaso`/`TareaAsignada`,
`IServicioTareas.IniciarAsistenteAsync`, `ListarConfiguracionesAsync`/`OpcionesConfiguracionAsync` con `TipoTarea`),
`Motor/IConstructorContexto.cs` (`FormatoContextoAsistente = 4`, `ArmarAsistenteAsync`), `Interfaces/IPermisosOrganizacion.cs`
(`PuedeAsignarTareas`, `PuedeUsarAsistente`), `DTOs/SubtareasDtos.cs` (QA-M7a-02: `PrefijoResultadoFallida`).

**Infrastructure** — Nuevos: `Services/Asignaciones/TareaAsignadaService.cs`, `Services/Asistente/{AsistenteDirector,
HerramientasAsistente, PropuestaTrabajoService}.cs`, `Data/Configurations/AsignacionesConfigurations.cs` (+ `ConversorDia`), migración
`Data/Migrations/20260916003219_AsignacionesAsistenteM7b.cs` (+ Designer y snapshot). Modificados: `Data/AppDbContext.cs` (DbSets),
`Data/Configurations/AgentesConfigurations.cs` (FK e índice de `TareaAsignadaId`), `Services/Motor/ConstructorContexto.cs`
(`ArmarPlataformaAsync` + `DeclaracionPrecedenciaAsistente`), `Services/Motor/ServicioTareas.cs` (`IniciarPlataformaAsync`,
`IniciarAsistenteAsync`, vínculo con la asignación en `CrearAsync`, detalle con asistente y asignación, listas por tipo),
`Services/Motor/ProcesadorTareas.cs` (guarda de plataforma generalizada, `ReconstruirPlataformaAsync`),
`Services/Motor/ProveedorModeloSimulado.cs` (`GuionAsistente`), `Services/Configurador/HerramientasConfigurador.cs` (`TiposPermitidos`
virtual; `clientes_buscar` habilitada en el asistente), `Services/Subagentes/ResumenHerramientasPlataforma.cs` (QA-M7a-02),
`Services/Organizacion/PermisosOrganizacion.cs`, `DependencyInjection.cs`.

**Web** — Nuevos: `Controllers/{AsignacionesController, AsistenteController}.cs`, `ViewComponents/ContadorAsignacionesViewComponent.cs`,
`Helpers/AsignacionesTextos.cs`, `Models/AsignacionesViewModels.cs`, vistas `Asignaciones/{Index, Form, Detalle, _ScriptAcciones}`,
`Asistente/{Index, Nueva}`, `Tareas/{_TarjetasPropuestaTrabajo, _ScriptPropuestasTrabajo}`, `Shared/Components/ContadorAsignaciones/Default`.
Modificados: `Controllers/{AgentesController (catálogo y Ejecutar con `asignacion`, POST con `TareaAsignadaId`), ConfiguracionReglasController
(tipo explícito)}.cs`, `Models/AgentesViewModels.cs` (`EjecutarAgenteViewModel` + asignación), vistas `Shared/_Layout` (ítem Asignaciones con
contador), `Agentes/{Index, _TarjetaAgente, Ejecutar}`, `Tareas/{Detalle, _Conversacion, Index}`, `wwwroot/css/site.css`,
`appsettings.json` (sección `Asignaciones`).

**Núcleo**: `nucleo/plataforma/agentes/asistente-director.md` (borrador) y entrada en `nucleo/plataforma/plataforma.yml`.
**Tests**: nuevos `AsignacionesTests.cs` (18), `AsistenteDirectorTests.cs` (18) e `Infra/EntornoM7b.cs`; ajustado `SubagentesTests.cs`
(QA-M7a-02). **Repo**: `docs/diseno-organizacion-roles-reglas.md` (M7b ✅).

### Decisiones de implementacion M7b (ambigüedades resueltas)
- **DI-M7b-1 Un solo camino para las conversaciones de plataforma:** en vez de duplicar `IniciarConfiguracionAsync` y
  `ArmarConfiguracionAsync`, se extrajeron `IniciarPlataformaAsync` y `ArmarPlataformaAsync` con el formato, el tipo y la declaración por
  parámetro. El formato 3 queda byte a byte igual (su golden sigue verde) y el 4 tiene el suyo. La guarda del procesador y la reconstrucción
  pasaron de `== ConfiguracionReglas` a `!= Trabajo`: todo tipo nuevo de plataforma hereda el comportamiento.
- **DI-M7b-2 `clientes_buscar` compartida:** `HerramientaConfiguradorBase` expone `TiposPermitidos` virtual (por defecto solo
  configuración) y `HerramientaClientesBuscar` lo amplía al asistente. Una sola clase, una sola lectura acotada, sin copiar código.
- **DI-M7b-3 El vencimiento mínimo se exige SOLO cuando cambia:** si no, una asignación vieja (ya vencida) dejaría de poder editarse para
  cambiarle el título o reasignarla. `ValidarAsync` recibe el vencimiento anterior y compara.
- **DI-M7b-4 "Pedírsela a un agente" pasa por el catálogo:** `Ejecutar` necesita un agente, así que el botón del detalle lleva a
  `Agentes/Index?asignacion=N` (con `ov-alert` "Elegí el agente") y cada "Usar" arrastra la asignación hasta `Agentes/Ejecutar?asignacion=N`.
  Las dos pantallas validan con `DatosParaPedirAAgenteAsync` (403 si no es la persona asignada, 404 si no la ve).
- **DI-M7b-5 El vínculo lo prepara el servicio de asignaciones:** `PrepararVinculoAsync` no guarda: setea `TareaAsignadaId` y pasa la
  asignación a En curso, y `ServicioTareas.CrearAsync` guarda todo junto. Un conflicto de token deja la tarea sin crear (`ChangeTracker.Clear`).
- **DI-M7b-6 La propuesta aplicada se marca en el mismo `SaveChanges` que su resultado:** la asignación por `CrearAsync(dto, propuestaId)` y
  la tarea por la navegación `ResultadoTareaAgente` (EF completa la FK sin un segundo guardado).
- **DI-M7b-7 Permisos, nunca visibilidad (OLV-010):** `VisibleAsync` solo habilita LECTURA; cada acción pasa por `ParaAccionarAsync`
  (asignado o Director, o solo Director en cancelar) y `PropuestaTrabajoService.ParaResolverAsync` (Director activo de esa organización).
  `PuedeAccionar` de las tarjetas es cosmético: el servidor vuelve a decidir.
- **DI-M7b-8 Contador del menú para todo miembro:** el ítem "Asignaciones" está en el bloque `Permisos.EsMiembro` del layout, junto a
  Aprobaciones; "Del equipo" se esconde y, por URL, cae a "Asignadas a mí" (no 403: la pestaña no es un recurso).
- **DI-M7b-9 Filtro Estado múltiple:** la grilla arranca con Pendiente + En curso preseleccionados (D-M7-13) y se persiste como lista
  separada por comas en Session; "Solo vencidas" es una casilla aparte. Sin `data-select2` propio (OLV-007): el `<select multiple>` lo toma
  `ovAplicarSelect2` como todos los demás.
- **DI-M7b-10 El simulador propone a la primera persona del equipo:** el diseño pedía "la primera que no sea el autor", pero el simulador no
  puede saber quién es (el `metadata.user_id` es opaco por el plan §5). Propone a `equipo_listar[0]` (orden alfabético) y a
  `agentes_disponibles[0]`. Para QA es equivalente y no expone identidades.
- **DI-M7b-11 `DateOnly` con conversor (RT-M7-13):** la columna sigue siendo `date`, pero se registró un `ValueConverter<DateOnly, DateTime>`
  porque `MySql.EntityFrameworkCore` devuelve `DateTime` y una proyección anónima a `DateOnly` revienta con `InvalidCastException`. Lo
  encontró el verificador contra MySQL real, no InMemory.
- **DI-M7b-12 QA-M7a-02:** el resultado de una parte fallida ya no dice "subagente" (`MensajesSubtareas.PrefijoResultadoFallida` = "El otro
  agente no pudo terminar: ") y "La subtarea se canceló" pasó a "La parte se canceló". `ResumenHerramientasPlataforma.SinPrefijo` usa la
  constante y el test de `SubagentesTests` afirma además que el texto NO contiene "subagente".

### Migraciones EF generadas M7b
- `20260916003219_AsignacionesAsistenteM7b` — `CreateTable TareasAsignadas` (título 150, descripción 4000, nota y motivo 500, `VenceEl` **date**,
  enums int, `VersionToken` como token, FKs Restrict a Tenant, ClienteCartera y 4 usuarios) y `PropuestasTrabajo` (texto `text`, `VenceEl` date,
  único `(TareaAgenteId, ToolUseId)`, índices `(TareaAgenteId, PasoNumero)` y `(ResultadoTareaAsignadaId)`, token); `AddColumn
  TareasAgente.TareaAsignadaId` + FK Restrict + índice. Índices de negocio: `(TenantId, AsignadaAUsuarioId, Estado)` y `(TenantId, Estado, VenceEl)`.
  Sin transformación de datos (las dos tablas nacen vacías y la columna nueva queda NULL en todas las tareas existentes). `Down` en orden inverso.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-16**, luego `database update SubagentesReglasPropuestasM7a` (Down OK) y
  `database update` otra vez; `has-pending-model-changes` limpio también después de agregar el conversor de `DateOnly`.
- Verificado por SQL (`scratchpad/verificar-m7b.sql`, transacción revertida): `VenceEl` es `date` en las dos tablas y `DATE(VenceEl) = VenceEl`;
  único `(TareaAgenteId, ToolUseId)` con `NON_UNIQUE = 0` y **1062 real** al repetirlo; FK `FK_TareasAgente_TareasAsignadas_TareaAsignadaId`;
  "Vencida" calculada con `CONVERT_TZ(...,'-03:00')`; `EXPLAIN`: el contador usa un índice (`ref`), el listado del equipo usa
  `IX_TareasAsignadas_TenantId_AsignadaAUsuarioId_Estado` (`Using index condition`) y las tareas vinculadas usan
  `IX_TareasAgente_TareaAsignadaId` (`Using index`); 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m7b`, sin Anthropic): **67 pasos OK, 0 fallas, 0 restos**. Alta con cliente y vencimiento,
  vencimiento pasado rechazado, listado del equipo con proyección anónima, 9 filtros, 6 búsquedas globales (texto, persona, cliente, estado en
  palabras, "vencida", fecha) y 4 órdenes; visibilidad, detalle y contador; transiciones y **`DbUpdateConcurrencyException` real**;
  "Pedírsela a un agente" con vínculo y En curso en un guardado, y rechazo a quien no es la persona asignada; conversación del asistente
  (formato 4), las 4 herramientas de lectura y las 2 de propuesta con sus validaciones; aplicar asignación y tarea de agente por los servicios
  reales (origen, autor = Director que aplica), "ya fue resuelta" con token real, Empleado sin tarjetas; lista de conversaciones con
  "con pendientes" y búsqueda por cantidad, y filtro Tipo en Tareas.
- Impacto: 2 tablas nuevas vacías, 1 columna nueva (NULL) con FK e índice en `TareasAgente`.

### Evidencia de build y tests M7b
- `dotnet build OlvidataAgentes.slnx`: **0 errores** (queda la advertencia preexistente CS0114 de `HomeController`).
- `dotnet test tests/OlvidataAgentes.Tests`: **244 OK / 0 fallidos** (208 previos + 36 nuevos: 18 de asignaciones y 18 del asistente);
  golden de hash de los formatos 1, 2 y 3 verdes sin cambios y **golden nuevo del formato 4**
  (`039c7e7b606bde6c09003d40fd9c0e70a06991f1a8395178952a820518bbbbea`).
- Lecciones: (1) **MySQL no materializa `DateOnly` desde una columna `date` en una proyección** — hace falta un `ValueConverter` (InMemory no lo
  detecta, el verificador sí); (2) reusar el mismo scope de servicios entre dos operaciones de un test hace que la entidad quede cacheada:
  una edición que compara contra el valor anterior necesita un scope nuevo (como una request nueva); (3) `IReadOnlySet<T>.Contains` dentro de
  una consulta EF no es el `Contains` de LINQ: hay que materializar a `List<T>` antes.

### Riesgos residuales M7b
- El asistente está **importado en dev como borrador, sin publicar** (PA-14): hasta evaluarlo y publicarlo, "Repartir trabajo conversando"
  aparece deshabilitado. Los pasos para habilitarlo y revertirlo están en la guía de QA de `trazabilidad.md`.
- El prompt es un **borrador sin evaluar**: su calidad (a quién propone, cómo redacta el pedido) todavía no se midió; M8 es el camino previsto.
- El contador del menú hace un `COUNT` por request con menú, como el de M6 (RT-M6-12).
- Una notificación que falla después del commit queda sin reintento (se loguea), igual que en M6 (RT-M6-06).
- "Vencida" depende del reloj del servidor convertido a hora argentina: una asignación que vence hoy pasa a vencida a la medianoche AR.
- El simulador propone a la primera persona del equipo (DI-M7b-10): con un solo miembro, el Director se autoasigna.
- Verificación visual pendiente (QA): pestañas y filtros de Asignaciones, formulario con chips de vencimiento, detalle en dos columnas,
  confirmaciones con textarea, tarjetas del asistente, contador del menú, mobile 390 y ambos temas.

### Proximos pasos pendientes M7b
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M7b).
- PA-14: evaluar y publicar el prompt `asistente-director` (hoy en borrador).
- Deuda fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; advertencia CS0114 de `HomeController` (template).

---

# M7a — Subagentes y reglas propuestas por agentes de trabajo

Estado: **implementada 2026-09-15, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M7 (P1–P26, alcance M7a),
`2-disenador-funcional.md` M7 (D-M7-1..11, D-M7-23/24) y `3-arquitecto-mvc.md` M7 (parte M7a), aprobados sin gate por autorización
de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.
**M7b (asignaciones y asistente del Director) queda para otra corrida.** Sin contenido de rubros, sin llamadas a Anthropic, sin commits.

### Escaneo de reutilizacion M7a
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1 (`TareaPadreId` sin uso, `EjecucionHerramienta` único por `ToolUseId`, `GuardarAsync` con `Version`, `ReclamarSiguienteAsync`) | La parte es una `TareaAgente` hija; su resultado vuelve como ejecución de herramienta; el estado nuevo no se reclama | Literal (extensión) |
| Template núcleo (`Artefacto.ArtefactoPadreId` que completa `ImportadorRubro` desde `coordinador`) | Subagentes = hijos publicados del artefacto base, sin tocar el importador | Literal |
| Template M3/M4 (`ServicioTareas.CrearAsync`, `ValidarAgenteOrganizacionAsync`, instantánea y hash) | Extraídos a `PreparadorTareaTrabajo` sin cambiar comportamiento ni mensajes | Literal (refactor) |
| Template M3b (`ReconstruirConversacion`, `MarcarFinAsync`, `MotivoNoPuedeSeguir`, simulador con guion) | Nota del coordinador en los mensajes, motivos nuevos, guiones nuevos | Literal (extensión) |
| Template M4b (`PropuestaRegla`, `PropuestaReglaService`, `ReglaService(OrigenAplicacion)`, `_TarjetasPropuesta`/`_ScriptPropuestas`, PAT-032) | Reglas propuestas por agentes de trabajo sobre la MISMA entidad, servicio y tarjetas, con permisos por tipo de tarea | Literal (patrón del mismo repo) |
| Template M5 (`NotaAdjuntos`, `ValidarAdjuntosAsync`, `HerramientasDocumentos.Resumir`, JSON con `JavaScriptEncoder`) | Nota de formato fijo, adjuntos de la parte, "Ver pasos" llano, resultado escapado | Literal |
| Template M6 (`IControlGasto`, `AprobacionAccion`, recorrido del paso, barrido del worker, PAT-034/035) | Límite al delegar, aprobaciones que bloquean el recorrido, segundo barrido en el worker | Literal (extensión) |
| verif-m6 (scratchpad) | Verificador EF → MySQL con organización de prueba y limpieza (`scratchpad/verif-m7`) | Literal (adaptado) |
| PAT-038 / PAT-032 | PAT-038 completado con rutas reales y gotchas confirmados; PAT-032 ampliado a agentes de trabajo | Confirmado |

### Archivos y capas modificadas M7a
**Domain** — Modificados: `Enums/EnumsAgentes.cs` (`EstadoTarea.EsperandoSubtareas = 7`), `Entities/Tareas.cs` (`TareaAgente.Profundidad`,
`PasoPadreNumero`, `ToolUseIdPadre`), `Entities/PropuestaRegla.cs` (comentario del uso M7a).

**Application** — Nuevos: `Settings/SubagentesOptions.cs`, `Motor/NotaSubtarea.cs` (+ `NombresHerramientasPlataforma`),
`Motor/IPreparadorTareaTrabajo.cs`, `Interfaces/ISubtareasService.cs` (+ `SubagenteDto`), `DTOs/SubtareasDtos.cs` (`MensajesSubtareas`).
Modificados: `Motor/IMotorAgentes.cs` (`ContextoHerramienta` + profundidad/base/versión, `IHerramientaDelegacion`, `TareaFiltros.IncluirSubtareas`,
`TareaListItemDto` + padre y cantidad, `PasoVisibleDto.PedidosLegibles`, `SubtareaDto`, `TareaRefDto`, `MotivoNoPuedeSeguir` 7 y 8,
`TareaDetalleDto` con partes/principal/costo total/agentes esperados, `FiltroTareas.Ocultar/MostrarPartes`),
`Interfaces/IPropuestaReglaService.cs` (`ListarPendientesParaMiAsync`), `DTOs/ConfiguradorDtos.cs` (`PropuestaReglaDto` + `EsDeTrabajo`,
`AutorNombre`, `AgenteOrigen`, `NoPuedeAccionarTexto`; `PropuestaFormularioDto.AgenteOrigen`), `DTOs/ReglasDtos.cs` (`OrigenAgenteTexto`),
`Helpers/BusquedaHelper.cs` (QA-M6-03: fecha corta "15/09").

**Infrastructure** — Nuevos: `Services/Motor/PreparadorTareaTrabajo.cs`, `Services/Subagentes/{SubtareasService, HerramientasSubagentes,
ResumenHerramientasPlataforma}.cs`, `Services/Reglas/HerramientaProponerRegla.cs`, migración
`Data/Migrations/20260915230800_SubagentesReglasPropuestasM7a.cs` (+ Designer y snapshot). Modificados:
`Services/Motor/ProcesadorTareas.cs` (herramientas de plataforma, nota del coordinador, recorrido del paso con partes, espera +
re-chequeo, `TrasFinAsync`/`GuardarYAvisarAsync`, `ReconstruirConversacion` con nota), `Services/Motor/ServicioTareas.cs` (crear por el
preparador, filtro Partes y chips, búsqueda por estado en palabras, detalle con partes/principal/costo total, ajuste bloqueado,
cancelación en cascada), `Services/Motor/ProveedorModeloSimulado.cs` (nombres exactos + guiones de delegación y de propuesta + parte que
falla), `Services/Motor/MotorAgentesWorker.cs` (barrido de partes), `Services/Configurador/{PropuestaReglaService,
HerramientasConfigurador}.cs` (permisos por tipo, pendientes para mí, `NombresPropuesta`), `Services/Reglas/ReglaService.cs` (aplicar
propuestas de trabajo, origen con nombre del agente), `Data/Configurations/AgentesConfigurations.cs`, `DependencyInjection.cs`.

**Web** — Nuevos: `Controllers/PropuestasReglaController.cs`, `Helpers/SubtareasTextos.cs`, vistas `Tareas/_TarjetaParte.cshtml`,
`Reglas/{_PropuestasAgentes, _PropuestaAgenteFila}.cshtml`. Modificados: `Controllers/{TareasController (filtro Partes, cancelar con
`volver`), ReglasController (card y agente de la propuesta)}.cs`, `Models/{ConfiguradorViewModels (TarjetasParte, PropuestasAgentes),
ReglasViewModels}.cs`, vistas `Tareas/{Detalle, _Conversacion, _CuadroSeguimiento, _EstadoTarea, _PasosTurno, _TarjetasPropuesta,
_ScriptPropuestas, Index}`, `Reglas/{Index, Detalle, _Form}`, `Consumo/_TablasConsumo` (CS8321), `wwwroot/css/site.css`, `appsettings.json`
(sección `Subagentes`).

**Tests**: nuevos `SubagentesTests.cs` (15), `ReglasPropuestasAgentesTests.cs` (6), `BusquedaFechaCortaTests.cs` (2) e `Infra/EntornoM7.cs`;
ajustados `AgentesOrganizacionTests` y `HerramientasDocumentosTests` (listas exactas de herramientas) y `ConfiguradorReglasTests` (nombres
exactos). **Repo**: `docs/diseno-organizacion-roles-reglas.md` (M7a ✅, M7b pendiente).

### Decisiones de implementacion M7a (ambigüedades resueltas)
- **DI-M7a-1 Sin endpoint propio de partes:** como en DI-M6-2, las tarjetas de parte se refrescan con `Tareas/Progreso` (el fragmento de
  la conversación); el procesador avisa por SignalR al padre cuando una parte arranca, espera aprobación o termina, y el respaldo de 10 s
  de la página cubre el resto. No se agregó `Tareas/Partes`.
- **DI-M7a-2 Preparador con las validaciones de agente:** `IPreparadorTareaTrabajo` expone también `ValidarAgenteAsync`,
  `ValidarAgenteOrganizacionAsync` y `SuscripcionVigenteAsync` para que `ServicioTareas` (vista previa, detalle, ajustes) no duplique
  consultas. Direcciones de dependencia: `ServicioTareas` → preparador + partes + propuestas; `SubtareasService` → preparador; ninguno al revés.
- **DI-M7a-3 Aviso al padre sin limpiar el ChangeTracker:** ante `DbUpdateConcurrencyException`, `AvisarFinAsync` desasocia solo la tarea
  principal y la relee (limpiar todo el tracker rompería la unidad de trabajo del procesador que lo llama).
- **DI-M7a-4 Cancelar una parte vuelve a la principal:** `Tareas/Cancelar` acepta `volver` (id de la principal) para el botón de la tarjeta;
  la visibilidad la sigue decidiendo el servicio.
- **DI-M7a-5 Prioridad del simulador:** con `delegar_subagente` ofrecida y "deleg" en el pedido, el guion de delegación gana sobre los de
  documentos y aprobaciones. Así la PARTE (que no delega) dispara esos guiones con el mismo texto y QA puede probar una aprobación o una
  lectura de documentos dentro de una parte. Además, una parte cuyo pedido dice "falle" termina Fallida (QA del resultado de fallo).
- **DI-M7a-6 "Ver pasos" llano centralizado:** `ResumenHerramientasPlataforma` arma los rótulos de delegación, consulta de subagentes,
  propuesta de regla **y de las acciones de demostración de M6** (QA-M6-04); `PasoVisibleDto.PedidosLegibles` los lleva alineados por índice.
- **DI-M7a-7 Orden de validación al aplicar una propuesta:** el mensaje "el configurador no crea preferencias" se responde antes que el
  estado y los permisos (comportamiento de M4b intacto); solo si la propuesta viene de una tarea de trabajo se admite el alcance Usuario.
- **DI-M7a-8 "Aplicar todas" en tareas de trabajo:** un Director que no es el autor aplica en masa solo las reglas de cliente; las
  preferencias ajenas quedan fuera de la selección (sin marcarlas fallidas).
- **DI-M7a-9 Card de propuestas en Reglas:** reusa `_ScriptPropuestas` con un contenedor alternativo (`#propuestasAgentes`); hasta 5
  tarjetas compactas y el resto en "Ver todas (N)".
- **DI-M7a-10 Tests con listas de herramientas:** ofrecer `proponer_regla` en toda tarea de trabajo cambia la lista que ven dos tests de
  M4/M5; se filtran las herramientas de plataforma en esas aserciones (el cambio es esperado, RT-M7-05).

### Migraciones EF generadas M7a
- `20260915230800_SubagentesReglasPropuestasM7a` — `AddColumn TareasAgente.Profundidad` (int, default 0), `PasoPadreNumero` (int null),
  `ToolUseIdPadre` (varchar(100) null) y único `(TareaPadreId, ToolUseIdPadre)`. **Corrección a mano:** MySQL no deja soltar
  `IX_TareasAgente_TareaPadreId` porque lo usa la FK; la migración saca la FK, cambia el índice y la repone (la FK se apoya en el prefijo
  del único). Sin transformación de datos: todas las tareas existentes quedan principales. El índice `(TenantId, Estado)` de
  `PropuestasRegla` ya existía desde M4b.
- **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-15**, luego `database update AprobacionesYGastoM6` (Down OK) y `database update`
  otra vez; `has-pending-model-changes` limpio.
- Verificado EF → MySQL real (`scratchpad/verif-m7`, sin Anthropic): **31 pasos OK, 0 fallas, 0 restos**. Estructura (columnas, único con
  `NON_UNIQUE = 0`, FK repuesta, índice de propuestas); dos principales con `(NULL, NULL)` conviven y **1062 real** al repetir
  `(TareaPadreId, ToolUseIdPadre)`; subagentes permitidos por jerarquía + licencia (y `subagentes_listar`); preparar y guardar una parte con
  autor, cliente, profundidad y hash propios; espera que no despierta con partes sin terminar, aviso que la devuelve con `Intentos = 0` y
  barrido; listado sin/con partes con la subconsulta `CantidadSubtareas`, búsqueda por estado en palabras y por fecha corta (QA-M6-03),
  detalle con tarjetas y costo total y detalle de parte con principal; cancelación en cascada con cierre de turno; propuestas de agente de
  trabajo (tarjetas, card, aplicar como autor, Director sin permiso sobre la preferencia, reglas con `OrigenRegla.PropuestaAgente` y origen
  "Propuesta de «…»"). `EXPLAIN`: el conteo de partes usa el único nuevo (`ref`), el barrido usa `IX_TareasAgente_Estado_LeaseHasta` y la
  card usa `IX_PropuestasRegla_TenantId_Estado`.
- Impacto: 3 columnas nuevas en `TareasAgente` (todas las filas existentes quedan principales), un índice único nuevo y la FK recreada.

### Evidencia de build y tests M7a
- `dotnet build OlvidataAgentes.slnx`: **0 errores** (queda la advertencia preexistente CS0114 de `HomeController`; la CS8321 de
  `_TablasConsumo` que reportó QA quedó resuelta).
- `dotnet test tests/OlvidataAgentes.Tests`: **208 OK / 0 fallidos** (185 previos + 23 nuevos); golden de hash de formatos 1, 2 y 3 verdes
  sin cambios y la instantánea de una parte es idéntica a la de una tarea equivalente sin principal.
- Lecciones: (1) MySQL bloquea el cambio de índice que usa una FK (ver migración); (2) llamar al aviso del padre desde la unidad de trabajo
  del hijo obliga a desasociar en vez de limpiar el tracker; (3) el guion del simulador por prefijo era una bomba de tiempo: los nombres
  exactos tienen test de regresión; (4) el límite de gasto al delegar se prueba mejor contra el servicio (el motor frena antes el turno).
- Observación: `LectorDocumentosTests.Extraccion_que_supera_el_tiempo_queda_como_no_se_pudo_leer` (M5, por tiempos) falló una vez con la
  máquina cargada y pasó al repetirlo; es inestable por diseño, no por M7a.

### Riesgos residuales M7a
- Sin contenido real de coordinadores: en dev el rubro `inmobiliario` ya tiene `inmo-orquestador` publicado con todos sus agentes como
  hijos, que alcanza para QA.
- Con `MaxTareasPorCliente = 1` las partes corren en serie (aceptado, RT-M7-08): una tarea con 5 partes tarda 5 vueltas del worker.
- El re-chequeo inmediato y el barrido cubren la carrera de RT-M7-01; el test cubre el camino del barrido y el del aviso, no una carrera
  real de dos procesos (InMemory).
- `CostoConSubtareasUsd` suma solo un nivel (profundidad 1 hoy); si sube la profundidad hay que sumar recursivamente (la cancelación ya recorre).
- La cancelación en cascada reintenta hasta 3 veces si el worker toca una parte a la vez; con muchas partes en curso podría devolver
  "no se pudo cancelar" y hay que reintentar desde la pantalla.
- Verificación visual pendiente (QA): tarjetas de parte y su refresco en vivo, detalle de parte, filtro Partes y chips, tarjetas de regla
  propuesta y card en Reglas, mobile 390 y ambos temas.

### Proximos pasos pendientes M7a
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M7a).
- M7b (asignaciones a personas y asistente del Director) con la migración `AsignacionesAsistenteM7b`.
- Deuda fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; advertencia CS0114 de `HomeController` (template).

---

# M6 — Aprobaciones de acciones por rol y límites de gasto

Estado: **implementada 2026-09-15, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M6 (P1–P16), `2-disenador-funcional.md` M6 (D-M6-1..16) y `3-arquitecto-mvc.md` M6, aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. **Continuación**: una corrida anterior del implementador se cortó por límite de uso; dejó el backend compilando (Domain, Application, Infrastructure, migración generada sin aplicar, simulador, demostraciones, worker) y faltaban Web, tests, aplicar y verificar la migración y la documentación. Sin llamadas a Anthropic, sin commits.

### Escaneo de reutilizacion M6
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1 (`EsperandoAprobacion`, `RequiereAprobacion`, `EjecucionHerramienta` único por `ToolUseId`, `GuardarAsync` con `Version`) | Espera y resolución sin paso nuevo; idempotencia al reanudar | Literal (extensión) |
| Template M3b/M4b (`MarcarFinAsync` con cierre de turno, `ResolverUsuarioAsync`, `_TarjetasPropuesta`/`_ScriptPropuestas`, simulador con guion) | Turno frenado por límite, autor re-verificado, tarjeta bajo el turno con acciones por delegación, `GuionAprobaciones` | Literal (patrón del mismo repo) |
| Template M2/M5 (`FiltrosSesion`, `DataTableRequestHelper`, `RespuestasServicio`, barra de espacio y tokens de color DI-M5-17, `.ov-enlace-accion`) | Bandeja, columna de Miembros, barras de gasto y estados con contraste | Literal |
| verif-m5 (scratchpad) | Verificador EF → MySQL con organización de prueba y limpieza | Literal (adaptado a M6, `scratchpad/verif-m6`) |
| crm-olvidata (cortes de gasto con motivo) | Criterio de `EvaluarAsync` con motivo antes de cada llamada | Patrón |
| PAT-034 / PAT-035 | Completados con rutas reales de código y lecciones (`pendiente_verificar: false` en las rutas propias) | Confirmado |

### Archivos y capas modificadas M6
**Domain** — Nuevos: `Enums/EnumsAprobacionesGasto.cs` (`NivelAprobacion`, `EstadoAprobacion`, `AmbitoGasto`), `Entities/GastoAprobaciones.cs` (`LimiteGastoMiembro`, `AvisoGasto`, `AprobacionAccion`). Modificado: `Entities/Tenant.cs` (`LimiteMensualUsd`).

**Application** — Nuevos: `Settings/GastoAprobacionesOptions.cs` (`GastoOptions`, `AprobacionesOptions`), `Helpers/PeriodoGasto.cs`, `Helpers/DatosAccionHelper.cs`, `DTOs/GastoDtos.cs` (`EstadoGastoDto`, `BarraGastoDto`, `ConsumoDto`, `MensajesGasto`…), `DTOs/AprobacionesDtos.cs` (`AprobacionDto`, `AprobacionListItemDto`, `AprobacionFiltros`, `MensajesAprobaciones`), `Interfaces/IGastoAprobaciones.cs` (`IControlGasto`, `IConsumoService`, `IAprobacionService`). Modificados: `Motor/IMotorAgentes.cs` (`IHerramientaConAprobacion`, `NombresHerramientasDemostracion`, `MotivoNoPuedeSeguir.EsperandoAprobacion/LimiteGasto`, `TareaDetalleDto.AprobacionesPorPaso/EsperaAprobacionTexto/AvisoGasto/AprobacionesDelTurno`), `Interfaces/IPermisosOrganizacion.cs` (4 permisos), `DTOs/OrganizacionDtos.cs` (filtro y columna de límite en Miembros).

**Infrastructure** — Nuevos: `Services/Gasto/{ControlGasto, ConsumoService}.cs`, `Services/Aprobaciones/AprobacionService.cs`, `Services/Motor/HerramientasDemostracion.cs`, `Data/Configurations/GastoAprobacionesConfigurations.cs`, migración `Data/Migrations/20260915154528_AprobacionesYGastoM6.cs` (+ Designer y snapshot). Modificados: `Data/AppDbContext.cs` (DbSets; avisos y pedidos fuera del audit trail), `Data/Configurations/AgentesConfigurations.cs` (precisión del límite, índice `PasosTarea (TenantId, CreadoAt)`), `Services/Motor/ProcesadorTareas.cs` (gasto antes de cada llamada, avisos tras paso con costo, pedidos + espera en un guardado, ejecución según resolución, unión de demostraciones), `Services/Motor/ServicioTareas.cs` (bloqueo en crear/configurar/ajustar, ajuste bloqueado en espera, cancelar pedidos, detalle con tarjetas, motivo y aviso), `Services/Motor/MotorAgentesWorker.cs` (barrido de vencidos), `Services/Motor/ProveedorModeloSimulado.cs` (`GuionAprobaciones`), `Services/Organizacion/{PermisosOrganizacion, MiembroService}.cs`, `DependencyInjection.cs`.

**Web** — Nuevos: `Controllers/{ConsumoController, AprobacionesController}.cs`, `ViewComponents/ContadorAprobacionesViewComponent.cs`, `Helpers/{GastoTextos, ConsumoTextos}.cs`, `Models/GastoAprobacionesViewModels.cs`, vistas `Consumo/{Index, _BarraGasto, _TablasConsumo, _TablaGrupo, _ModalLimite}`, `Aprobaciones/Index`, `Tareas/{_TarjetasAprobacion, _ScriptAprobaciones}`, `Shared/{_AvisoGasto, Components/ContadorAprobaciones/Default}`. Modificados: `Controllers/{AgentesController, ConfiguracionReglasController, MiembrosController, ClientesController (límite por defecto al crear, card, `CambiarLimiteGasto`, `Consumo`), UsoController}.cs`, `Models/{AgentesViewModels, ConfiguradorViewModels}.cs`, vistas `Shared/_Layout` (menú Aprobaciones con contador y Consumo), `Tareas/{Detalle, _Conversacion, _CuadroSeguimiento, _EstadoTarea, Index}`, `Agentes/Ejecutar`, `ConfiguracionReglas/Nueva`, `Miembros/Index`, `Clientes/Details`, `Uso/Index`, `wwwroot/css/site.css`, `appsettings.json` (secciones `Gasto` y `Aprobaciones`).

**Admin**: `tenant-crear` con el límite por defecto. **Tests**: nuevos `GastoTests.cs` (9), `AprobacionesTests.cs` (17 casos) e `Infra/DoblesM6.cs` (`EntornoM6`, campana de prueba, herramientas de prueba). **Repo**: `docs/diseno-organizacion-roles-reglas.md` (M6 ✅).

### Decisiones de implementacion M6 (ambigüedades resueltas)
- **DI-M6-1 Continuación:** se conservó todo lo del intento anterior (revisado contra la arquitectura y compilando); correcciones: la migración no tenía el `UPDATE Tenants SET LimiteMensualUsd = 100.00` exigido → agregado, `Down` a M5 y `Up` de nuevo en dev; faltaban toda la capa Web, los tests y la documentación.
- **DI-M6-2 Tarjetas sin endpoint propio:** en lugar de `Aprobaciones/Tarjetas` la tarjeta se refresca con `Tareas/Progreso` (el mismo fragmento de la conversación); al aprobar o rechazar se reinicia el seguimiento en vivo (`ovAlResolverAprobacion`) porque la tarea vuelve a la cola.
- **DI-M6-3 Confirmación:** la tarjeta aprueba directo y la bandeja pide SweetAlert2 (`data-confirmar-aprobar`, D-M6-11); rechazar con textarea, contador y validación de 500 caracteres (D-M6-10); resultado "ya resuelto" (`datos.codigo = "YaResuelto"`) refresca.
- **DI-M6-4 Montos:** los límites viajan como texto y se interpretan con `BusquedaHelper.TryParseImporte` (formato argentino "20,50"); mayor a cero, dos decimales, tope y rango los valida el servicio.
- **DI-M6-5 Límite efectivo:** si el límite propio supera al de la empresa, rige el de la empresa como límite del miembro y el bloqueo puede ser "por miembro" aunque la empresa no haya llegado (el mensaje cita el efectivo).
- **DI-M6-6 Cuadro de seguimiento:** "espera aprobación" y "límite de gasto" reemplazan el cuadro con una alerta (mismo patrón que máximo de ajustes y suscripción); el aviso ámbar va dentro del cuadro.
- **DI-M6-7 Estado en palabras:** junto al badge del encabezado de la conversación y en el turno activo con ícono de mano en lugar de spinner.
- **DI-M6-8 Contraste (PA-11):** el badge "Espera aprobación" pasó a `bg-warning text-dark` en `_EstadoTarea` y en la grilla de Tareas (blanco sobre amarillo daba 1,6:1). Barras: verde #15803d / ámbar #b45309 / rojo #b91c1c en claro y #22c55e / #f59e0b / #ef4444 en oscuro; textos de estado con los tokens de DI-M5-17; contador rojo #b91c1c con blanco (6,5:1).
- **DI-M6-9 Bandeja:** un filtro por columna visible por pestaña (Pendientes: Pedido, Tarea, Qué quiere hacer, Pedida por —solo Director—, Cliente, Quién aprueba, Vence; Historial: Pedido, Tarea, Qué quiso hacer, Pedida por, Resultado, Resuelta por, Fecha, Motivo), Session por pestaña; "Vence" muestra relativo + fecha (la búsqueda global encuentra la fecha); columnas secundarias ocultas en mobile.
- **DI-M6-10 Consumo:** cards de agrupaciones con `_TablaGrupo`; buscador del lado del cliente en "Por miembro"; en mobile área y límite bajo el nombre; staff ve la misma vista con breadcrumb y sin "Cambiar límite".
- **DI-M6-11 Miembros:** filtro "Límite del mes" (con límite propio / el de la empresa) además de la columna, con enlace a Consumo; con clave propia "No aplica".
- **DI-M6-12 Mensajes del backoffice:** el aviso de miembros por encima va en `SuccessMessage` (el layout solo muestra Success y Error).
- **DI-M6-13 Uso y consumo:** columnas "Este mes" y "Límite" en las organizaciones del resumen del período (las que tuvieron uso); el nombre lleva al consumo de la organización.
- **DI-M6-14 Alta de organizaciones:** `Clientes/Create` y `tenant-crear` asignan el límite por defecto también con clave propia (no aplica mientras sea propia).
- **DI-M6-15 Tests:** `EntornoM6` sobre `EntornoReglas` con campana de prueba y tres herramientas (`pago_real` con efecto en base y nivel autor, `sin_nivel` sin `IHerramientaConAprobacion`, `nota_libre` sin aprobación); el consumo se siembra en tareas marcadas Completadas para que el worker no las reclame.

### Migraciones EF generadas M6
- `20260915154528_AprobacionesYGastoM6` — generada por la corrida anterior sin aplicar (`migrations list`: Pending; snapshot consistente). **Aplicada en `olvidata_agentes_dev` (MySQL 8.0) el 2026-09-15**, luego `database update WorkspaceClientesM5` (Down OK: tablas, índice y columna fuera) y `database update` otra vez con el `UPDATE` agregado; `has-pending-model-changes` limpio.
- Verificado por SQL (`scratchpad/verificar-m6.sql`, transacción revertida): `decimal(10,2)` en ambos límites (12,345 → 12,35), 2/2 organizaciones con USD 100; índices únicos `(TareaAgenteId, ToolUseId)`, `(TenantId, Periodo, Ambito, UsuarioId, Umbral)` y `(TenantId, UsuarioId)` con **1062 real** (incluido `UsuarioId` vacío); tokens 1 fila / 0 filas; `EXPLAIN` del contador usa `IX_AprobacionesAccion_TenantId_Estado_VenceAt` (index) y el SUM del miembro usa índices (ref); **el SUM de la organización hizo full scan con 139 pasos** (el optimizador descarta el índice con tan pocas filas; revisar con volumen, RT-M6-05); 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m6`, modelo falso, sin Anthropic): **64 pasos OK, 0 fallas, 0 restos**. Evaluar (SUM mensual y join por autor), bloqueo con mensaje, avisos una sola vez y 1062 real; consumo por rol con las 4 agrupaciones, mes anterior, staff (`GroupBy` + `SUM` a diccionario); límites con token, 1062 y **`DbUpdateConcurrencyException` real**; Miembros con filtro, orden y búsqueda por límite; bandeja con 6 órdenes, 7 búsquedas globales (texto, autor con subconsulta, cliente, `#tarea`, fecha, nivel, "sin cliente"), filtros combinados y opciones `Distinct`; aprobar con otro pendiente del paso (`Contains` en MySQL), Empleado sin permiso de nivel Director, rechazar el último → cola con `Intentos = 0`, ya resuelto con nombre, historial con 4 órdenes, búsqueda y filtros; token real y 1062 real en pedidos; barrido de vencidos; cancelar tarea en espera cancela pedidos; **motor real**: pedido + espera en un guardado sin ejecución, aprobar, ejecutar una vez y completar. La primera corrida falló solo en la limpieza (`Notifications` no tiene FK a usuarios); restos borrados por SQL y verificador corregido y corrido de nuevo.
- Impacto: 3 tablas nuevas vacías, columna nueva con USD 100 en las organizaciones existentes, índice nuevo en `PasosTarea`.

### Evidencia de build y tests M6
- `dotnet build OlvidataAgentes.slnx`: 0 errores.
- `dotnet test tests/OlvidataAgentes.Tests`: **185 OK / 0 fallidos** (159 existentes + 26 nuevos); golden de hash de formatos 1, 2 y 3 verdes sin cambios.
- Lecciones: (1) el primer fallo fue un dato del propio test (límite efectivo bloquea por miembro), no del código; (2) InMemory aplica tokens de concurrencia pero no índices únicos: 1062 solo en MySQL; (3) el verificador EF no debe asumir FK en tablas del template (`Notifications.UserId` sin FK).

### Riesgos residuales M6
- RT-M6-05: SUM mensual con full scan a bajo volumen; si crece, acumulado mensual en el mismo commit del paso.
- RT-M6-06: una notificación que falla después del commit queda sin reintento (aviso registrado, logueado).
- RT-M6-07: el vencimiento depende del worker (`MotorAgentes:Habilitado`); resolver un vencido igual lo marca vencido.
- RT-M6-12: el contador hace un `COUNT` en cada request con menú.
- Con el simulador el costo es cero: los avisos del 80 % no se ven sin sembrar costo (guía de QA).
- Todavía no existen herramientas reales con aprobación (solo demostraciones); la descripción y el nivel los define cada herramienta futura.
- Verificación visual pendiente (QA): barras y umbrales, modal de límite, tarjetas, bandeja con contador y filtros, dos aprobadores, mobile 390 y ambos temas.

### Proximos pasos pendientes M6
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M6).
- Deuda fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; referencia de crm-olvidata en PAT-035 sin verificar (antecedente externo).

---

# M5 — Workspace por cliente de cartera

Estado: **implementada 2026-09-15, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M5 (P1–P14), `2-disenador-funcional.md` M5 (D-M5-1..14) y `3-arquitecto-mvc.md` M5, aprobados sin gate por autorización de Joaquín (2026-09-14); `4-presupuestador.md` omitido (proyecto personal). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Sin contenido de rubros, sin llamadas a Anthropic, sin commits (los hace el orquestador tras QA).

### Escaneo de reutilizacion M5
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1/M4b (`IHerramientaAgente`, idempotencia por `ToolUseId`, `ContextoHerramienta` con defaults, lectores de entrada de `HerramientasConfigurador`) | Tres herramientas de solo lectura sin `SaveChanges`; `ContextoHerramienta.ClienteCarteraId` | Literal (extensión) |
| Template M2/M4 (`NombreVigente` STORED por SQL + índice único, `FiltrosSesion`/`DataTableRequestHelper`/`RespuestasServicio`, bajas AJAX PAT-015) | Nombre único con baja lógica, grillas de miembro y de staff, renombrar/baja por AJAX | Literal |
| Template M3/M3b (`ReconstruirConversacion`, `EnviarSeguimientoAsync` con `Version`, `_PasosTurno`, `ProveedorModeloSimulado`) | Nota de adjuntos en los mensajes (sistema y hash intactos), adjuntos en el mismo guardado del ajuste, guion de documentos | Literal (extensión) |
| Template (ClosedXML, QuestPDF) | Lectura de .xlsx; QuestPDF como generador de fixtures en tests | Literal |
| vinosefue PAT-002 | Criterio de validación en servidor (extensiones, tamaño); su almacenamiento público descartado | Patrón |
| ganaderia `Ganaderia.Infrastructure/Services/Ganaderia/LocalComprobanteStorageService.cs` (ruta verificada) | Almacén local fuera de `wwwroot` con endpoint autenticado | Patrón |
| koi PAT-012 | Extractores como clases puras probadas con archivos generados | Patrón |
| PAT-033 | Completado con rutas reales de código y lecciones (`pendiente_verificar: false`, incluida la de ganaderia) | Confirmado |

### Archivos y capas modificadas M5
**Domain**
- Nuevos: `Enums/EnumsDocumentos.cs` (`TipoDocumento`, `EstadoLecturaDocumento`), `Entities/DocumentoCartera.cs` (`DocumentoCartera` + `DocumentoCarteraParte`), `Entities/AdjuntoMensajeTarea.cs`.
- Modificado: `Entities/Uso.cs` (se elimina `DocumentoCliente`, P1).

**Application**
- Nuevos: `Settings/DocumentosOptions.cs`, `Helpers/NombreDocumentoHelper.cs` (+ `TiposArchivoDocumento`), `DTOs/DocumentosDtos.cs` (`MensajesDocumentos` y DTOs), `Interfaces/IDocumentoCarteraService.cs`, `Interfaces/IAlmacenDocumentos.cs` (+ `ILectorDocumentos` y DTOs de lectura), `Motor/NotaAdjuntos.cs` (+ `NombresHerramientasDocumentos`).
- Modificado: `Motor/IMotorAgentes.cs` (`ContextoHerramienta.ClienteCarteraId`, `CrearTareaDto.DocumentoIds`, `PasoVisibleDto.Resumenes` + `ResumenHerramientaDto`, `MensajePersonaDto.Adjuntos` + `AdjuntoMensajeDto`, `TareaDetalleDto.PuedeAdjuntar/MaxAdjuntosPorMensaje`, sobrecarga `IServicioTareas.EnviarSeguimientoAsync(..., documentoIds, ct)`).

**Infrastructure**
- Nuevos: `Services/Documentos/{AlmacenDocumentosDisco, ValidadorContenidoArchivo, LectorDocumentos, DocumentoCarteraService, HerramientasDocumentos}.cs`, `Services/Documentos/Extractores/{ComunesExtraccion, ExtractorPdf, ExtractorWord, ExtractorPlanilla, ExtractorCsv, ExtractorTexto}.cs`, `Data/Configurations/DocumentosConfigurations.cs`, migración `Data/Migrations/20260915135646_WorkspaceClientesM5.cs` (+ Designer y snapshot).
- Modificados: `Data/AppDbContext.cs` (DbSets; partes y adjuntos fuera del audit trail), `Data/Configurations/AgentesConfigurations.cs` (sin `DocumentoClienteConfiguration`), `Services/Motor/ProcesadorTareas.cs` (unión de herramientas de documentos en tareas de trabajo con cliente, contexto con cliente, adjuntos → `ReconstruirConversacion(entrada, pasos, adjuntos)`), `Services/Motor/ServicioTareas.cs` (adjuntos en `CrearAsync` y en el ajuste en el mismo guardado, chips y resúmenes llanos en `ObtenerDetalleAsync`, `PuedeAdjuntar`), `Services/Motor/ProveedorModeloSimulado.cs` (guion de documentos; la nota no cuenta como turno), `DependencyInjection.cs`, `OlvidataAgentes.Infrastructure.csproj` (`PdfPig` 0.1.16, `DocumentFormat.OpenXml` 3.1.1 explícito).

**Web**
- Nuevos: `Controllers/DocumentosController.cs`, `Helpers/DocumentosTextos.cs`, `Models/DocumentosViewModels.cs`, vistas `Documentos/{Index, Ver, _Parte, _ZonaSubida, _VistaPreviaDocumentos, _ScriptAccionesDocumento}`, `Shared/_ModalDocumentos`, `Cartera/_CardDocumentos`, `Clientes/Documentos`, `wwwroot/js/documentos.js` (cola de subida + modal subir/elegir).
- Modificados: `Controllers/{CarteraController (card), AgentesController (documentos, vista previa y adjuntos al crear), TareasController (ajuste con adjuntos), ClientesController (card y grilla de staff)}.cs`, `Models/{AgentesViewModels (EjecutarAgenteViewModel, ClienteDetalleViewModel), TareasViewModels (SeguimientoViewModel)}.cs`, vistas `Cartera/Detalle`, `Agentes/Ejecutar`, `Tareas/{Detalle, _Conversacion, _CuadroSeguimiento, _PasosTurno}`, `Clientes/Details`, `wwwroot/css/site.css`, `appsettings.json` (sección `Documentos`).

**Admin**: comando `documentos-limpiar [--raiz <carpeta>] [--aplicar]`. **Tests**: nuevos `LectorDocumentosTests.cs`, `DocumentosTests.cs` (+ `EntornoDocumentos`), `HerramientasDocumentosTests.cs` (46 casos); ajustados `TenantIsolationTests.cs` y `MotorAgentesTests.cs` (efecto genérico con `ClienteCartera` en lugar de `DocumentoCliente`). **Repo**: `.gitignore` (`**/App_Data/documentos/`, verificado con `git check-ignore`), `PLAN-IMPLEMENTACION.md` (Fase 2: workspace ✅), `docs/diseno-organizacion-roles-reglas.md` (M5 ✅).

### Decisiones de implementacion M5 (ambigüedades resueltas)
- **DI-M5-1 Paquete PdfPig:** el id NuGet oficial es `PdfPig` (mismo proyecto, namespace `UglyToad.PdfPig`, Apache-2.0); `UglyToad.PdfPig` solo conserva un prerelease viejo. `DocumentFormat.OpenXml` 3.1.1 = la que ya resolvía ClosedXML.
- **DI-M5-2 Contratos:** `ILectorDocumentos.Detectar` sincrónico que devuelve tipo + extensión + MIME del servidor; `GuardarTemporalAsync` calcula SHA-256 en streaming y corta al pasar el máximo (el largo del navegador puede mentir); `DarDeBajaAsync(id, version?)`; `EnviarSeguimientoAsync` con adjuntos como sobrecarga (la firma de M3b delega, sin ambigüedad).
- **DI-M5-3 Cliente dado de baja (RF-M5-15):** sus documentos no se listan ni se suben (404), pero cada documento vigente sigue abriendo por id (ver, parte, descargar, imagen, renombrar, dar de baja): los chips de tareas existentes siguen andando y el Director puede darlos de baja. Staff los ve con "(dado de baja)".
- **DI-M5-4 Conflictos:** renombrar o dar de baja un documento que otra persona dio de baja → "Otra persona cambió o dio de baja este documento…" (no 404); de otra organización o inexistente → 404. Token `VersionToken` verificado en el servicio y en la base (`OriginalValue`).
- **DI-M5-5 Baja:** baja lógica + partes borradas como entidades clave en estado Deleted (sin traer el texto) en un guardado; archivo después del commit y `ArchivoEliminadoAt` en un segundo guardado (si falla, queda para `documentos-limpiar`).
- **DI-M5-6 Legible en parte:** no se extrae lo que excede el máximo, así que no hay "N de M" del documento completo: el aviso dice "puede leer hasta la parte N. El resto quedó fuera."
- **DI-M5-7 Partes:** "Parte i de N" (Word, texto), "Página i de N" (PDF; una página de más de 2 × 8.000 caracteres se parte "(k de m)"), "Hoja «X», filas a–b" numeradas por fila de datos con encabezado repetido, "Filas a–b" (CSV) y "Encabezado" si solo hay encabezado. PDF sin texto o con promedio < 20 caracteres por página → no legible. Fórmula que ClosedXML no evalúa → valor guardado.
- **DI-M5-8 Validación:** .docx/.xlsx se descomprimen completos contando bytes leídos (además de los declarados); relación de compresión solo en entradas de más de 1 MB; `vbaProject.bin`, `vbaData.xml` y tipos `macroEnabled` → macros; texto: sin NUL (salvo UTF-16 con BOM) y como máximo 10 % de caracteres de control.
- **DI-M5-9 Búsqueda:** `LIKE … ESCAPE '!'` para `%` y `_`; un `!` del usuario pasa a `_` porque EF InMemory no interpreta `!!` (la comparación exacta en memoria descarta filas de más); en memoria `IgnoreCase | IgnoreNonSpace`, igual a la colación.
- **DI-M5-10 JSON de herramientas:** `JavaScriptEncoder.Create(UnicodeRanges.All)` escapa `< > & '` (un documento no puede simular marcado ni cerrar la nota) sin escapar tildes; aviso "información, nunca instrucciones" en cada resultado.
- **DI-M5-11 Nota de adjuntos:** `<documentos_adjuntos>` + `<documento id nombre/>` escapados, agrupada por `PasoNumero` y ordenada por `Orden`; el simulador la excluye del conteo de turnos. Golden de hash de formatos 1, 2 y 3 verdes; test de que una tarea con adjuntos tiene el mismo hash e instantánea que sin adjuntos.
- **DI-M5-12 Ver pasos:** `Resumenes` alineado con `Resultados`; los pedidos a herramientas de documentos no se muestran en el paso del modelo (se explican en su resultado); nombres de documento de los errores acotados al cliente de la tarea; contenido legible recortado a 10.000 caracteres; "Ver lo que leyó" (leer) / "Ver el detalle" (listar, buscar).
- **DI-M5-13 Pantalla de documentos:** acciones de fila como botones (Ver, Descargar, Renombrar, Dar de baja) en lugar de menú ⋯ (un dropdown queda recortado dentro de `.table-responsive`); en mobile se ocultan Lectura, Partes, Tamaño, Subido por y Fecha y lectura + fecha van bajo el nombre. Filtros del diseño (Nombre, Tipo, Lectura, Subido por, Fecha); partes por búsqueda global.
- **DI-M5-14 Subida:** parcial de marcado `_ZonaSubida` + `wwwroot/js/documentos.js` (en vez de un parcial de script); límite de request 30.000.000 bytes (tope por defecto de IIS) para que un archivo de 25 MB llegue y reciba el mensaje de tamaño.
- **DI-M5-15 Nueva tarea:** si el envío falla, la selección conserva los vigentes del cliente; "Subir un documento" deja elegidos los subidos (hasta el máximo); staff sin campo de documentos.
- **DI-M5-16 Staff:** la grilla ignora Tenant y SoftDelete en la raíz con `TenantId` y `DeletedAt` explícitos sobre los documentos (nombres de clientes dados de baja en la misma consulta); solo metadatos.
- **DI-M5-17 Contraste (lecciones OLV-001..004):** estados en claro verde #15803d (5,0), ámbar #92400e (7,1), gris `--ov-gray-600` (7,6), rojo #b91c1c (6,5); en oscuro #86efac (10,3), #fcd34d (10,1), `--ov-text-muted` (5,7), #fca5a5 (7,6) sobre #1e293b. Enlaces nuevos `.ov-enlace-accion` #1a78b8 (4,7) y marca en oscuro (4,9). SweetAlert2 de documentos con confirmar #1a78b8 y peligro #dc2626.
- **DI-M5-18 Audit trail:** `DocumentoCarteraParte` y `AdjuntoMensajeTarea` fuera (texto confidencial y registro inmutable); `DocumentoCartera` se audita sin contenido.
- **DI-M5-19 `documentos-limpiar`:** ignora todo lo modificado en la última hora (una subida en curso nunca se toca) y cualquier nombre que no sea carpeta entera + GUID; acepta `--raiz` (la raíz relativa del Admin sería su carpeta de binarios).

### Migraciones EF generadas M5
- `20260915135646_WorkspaceClientesM5` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-15** con `dotnet ef database update`; `has-pending-model-changes` limpio. `DocumentosCliente` tenía 0 filas (verificado antes). Ajuste manual: `NombreVigente` quitada del `CreateTable` (el proveedor la creaba VIRTUAL) y agregada con `ALTER TABLE … GENERATED ALWAYS AS (CASE WHEN DeletedAt IS NULL THEN Nombre END) STORED` antes de su índice único. `Down` vuelve a crear `DocumentosCliente` vacía.
- Verificado por SQL (`scratchpad/verif-workspacem5.sql`): `DocumentosCliente` eliminada; `NombreVigente` STORED GENERATED; `HashSha256` char(64), `ArchivoId` char(36), `Texto` mediumtext; 11 índices (únicos `(ClienteCarteraId, NombreVigente)`, `ArchivoId`, `(DocumentoCarteraId, Numero)`, `(TareaAgenteId, PasoNumero, DocumentoCarteraId)`); 5 FK RESTRICT; colación `utf8mb4_0900_ai_ci`.
- Verificado en transacción revertida (`scratchpad/verif-workspacem5-transaccion.sql`, **con `--default-character-set=utf8mb4`**): "CONTRÁTO 2026.PDF" junto a "Contrato 2026.pdf" → 1062; la baja deja `NombreVigente` NULL y libera el nombre; `ArchivoId` repetido → 1062; nombre de 151 → 1406; 5.000.000 de caracteres con tilde (10 MB) en mediumtext OK; parte repetida → 1062; parte o adjunto con padre inexistente → 1452; borrar documento con partes → 1451; `LIKE … ESCAPE '!'` literal 1 / comodín 0 y sin tildes ni mayúsculas 1; token 1 fila / 0 filas; `EXPLAIN` del listado, del espacio y del duplicado usan índices (ref); 0 restos. (Sin ese parámetro el cliente `mysql.exe` manda los literales con tilde en otro charset y las pruebas con tildes dan falsos resultados.)
- Verificado EF → MySQL real (`scratchpad/verif-m5`, modelo sin Anthropic): **47 pasos OK, 0 restos**. Subida legible, sufijos "(2)" y "(3)" con mayúsculas y tildes, duplicado por hash, `NombreVigente` y `CHAR_LENGTH`, 1062 real reconocido por el nombre de la columna, renombrar repetido/OK/versión vieja, **`DbUpdateConcurrencyException` real por `VersionToken`**, listado con filtros, búsqueda por fecha y orden por las 7 columnas, espacio (SUM), vista previa, validar adjuntos (`List<int>.Contains`), staff (resumen, búsqueda por cliente, opciones, cliente dado de baja), herramientas (buscar sin mayúsculas, sin tildes, con `%`/`_` y con `!`; leer; listar), adjuntos (guardado, 1062, 1452, chip vigente y "(dado de baja)"), baja por rol con partes borradas y nombre liberado, sin temporales en disco. **Encontró un bug que InMemory no mostraba** (orden sobre un record construido en la proyección de `ListarAsync`), corregido.
- `documentos-limpiar` probado sobre una carpeta de prueba: informa y con `--aplicar` borra un temporal viejo y un archivo sin documento; no toca un archivo reciente ni un nombre que no es GUID.
- Impacto: 3 tablas nuevas vacías; se elimina `DocumentosCliente` (vacía); sin transformación de datos.

### Evidencia de build y tests M5
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **159 OK / 0 fallidos** (113 existentes + 46 nuevos); golden de hash de formatos 1, 2 y 3 verdes.
- Lecciones: (1) EF InMemory traduce un `OrderBy` sobre la propiedad de un record construido en la proyección y MySQL no: proyectar a tipo anónimo (lo detectó el verificador EF → MySQL); (2) el `catch` de un `FileMode.CreateNew` no debe borrar la ruta si el archivo ya existía (bug real encontrado por el test del almacén); (3) `LIKE … ESCAPE` con el propio carácter de escape duplicado no es portable a InMemory; (4) en tag helpers `model="…"` no se decodifica `&quot;`: armar el modelo en un bloque de código; (5) `mysql.exe` en Windows necesita `--default-character-set=utf8mb4` para probar literales con tilde; (6) el id NuGet de PdfPig es `PdfPig`; (7) en scripts de parche multi-región conviene escribir el script con la herramienta de archivos (un heredoc de bash se rompe con comillas simples de JS).

### Riesgos residuales M5
- RT-M5-02: sin antivirus (aceptado). Un archivo que pasa la validación estructural pero explota un defecto de PdfPig/OpenXml/ClosedXML queda "No se pudo leer" al vencer el tope, pero el hilo de extracción no se puede abortar y sigue consumiendo CPU hasta terminar.
- La relación de compresión > 100 en entradas de más de 1 MB puede rechazar planillas legítimas muy repetitivas ("demasiado grande al abrirlo"); medir con archivos reales y subir el tope si hace falta.
- RT-M5-03 inyección desde documentos: mitigada (solo lectura, cliente de la tarea, JSON escapado con aviso, declaración de contexto) sin validar con el modelo real (PA-02).
- RT-M5-05 despliegue: la carpeta `App_Data/documentos` no debe borrarse al publicar y el pool necesita escritura; preferir ruta absoluta fuera del sitio (checklist M9, `/olvidata-infra`).
- RT-M5-06 rendimiento: ClosedXML carga el .xlsx completo en memoria; `LIKE` sobre mediumtext sin índice (S-M5-04).
- RT-M5-07 cuota: subidas simultáneas pueden excederla en un archivo cada una (aceptado).
- La imagen se muestra con el MIME del servidor y `nosniff` global; no se agregó una CSP propia a esa respuesta.
- Verificación visual pendiente (QA): arrastrar y soltar, cola con progreso, modal subir/elegir, Select2 con plantillas, chips, Ver pasos llano, partes sin recargar, mobile 390 y tema oscuro.

### Proximos pasos pendientes M5
- QA etapa 6 con el modelo simulado (guía en `trazabilidad.md`, entrada del implementador M5).
- M9: ruta absoluta de documentos fuera del sitio publicado, regla para que Web Deploy no la borre y permisos de escritura del pool.
- Corrida real con costo (PA-02): calidad de lectura por partes, uso de las herramientas y costo.
- Deuda preexistente vista, fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; advertencias de filtro global en la relación `Licencia` ↔ `LicenciaRubro`/`TokenEmitido` al arrancar; `Admin licencia-crear` con `slugs.Contains` (MH-001).

---

# M4b — Agente configurador de reglas del Director

Estado: **implementada 2026-09-14, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` M4b (P1–P9), `2-disenador-funcional.md` M4b (D-M4b-1..9) y `3-arquitecto-mvc.md` M4b (gate 1–7) aprobados; `4-presupuestador.md` omitido (gate dispensado). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Prompt del configurador redactado como **borrador** e importado en dev **sin publicar**. Sin contenido de rubros.

### Escaneo de reutilizacion M4b
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1 (`IHerramientaAgente`, `RegistroHerramientas`, ejecución idempotente por `ToolUseId` en un solo commit) | Herramientas del configurador sin `SaveChanges`; la propuesta se guarda con el registro de la ejecución | Literal |
| Template M2 (`ResolvedorSesion`, `ContextoUsuario`, `PermisosOrganizacion`, `FiltrosSesion`/`DataTableRequestHelper`/`RespuestasServicio`, `ovPostAjax`/`ovToast`) | `ResolverUsuarioAsync` para el worker; lista de conversaciones DataTables; acciones AJAX con 403/404 | Literal (extensión) |
| Template M3 (`ReglaService` crear/editar/estado/límites/versiones, `ConstructorContexto`, `Reglas/_Form`, `Detalle`) | Aplicación por el mismo servicio con `OrigenAplicacion`; formato 3; formulario precargado; origen en historial | Literal (extensión) |
| Template M3b (conversación, `EnviarSeguimientoAsync`, `_Conversacion`, refresco en vivo, `ProveedorModeloSimulado`) | Configuración = tarea M3b de tipo propio; tarjetas bajo cada respuesta; simulador con guion de herramientas | Literal (extensión) |
| Template M4 (`ActivarSugerenciaAsync`, importador, `ov-badge-neutro`, golden de hash) | Propuesta "activar sugerencia"; prompt en `nucleo/plataforma`; badges; golden formato 2 capturado antes de tocar el constructor | Literal |
| crm-olvidata | Function calling + ejecución por el servicio de negocio | Patrón |
| PAT-032 (catálogo) | Completado con rutas reales de código, `pendiente_verificar: false` | Confirmado |

### Archivos y capas modificadas M4b
**Domain**
- Nuevo: `Entities/PropuestaRegla.cs`.
- Modificados: `Enums/EnumsAgentes.cs` (`TipoTarea`), `Enums/EnumsReglas.cs` (`OrigenRegla.PropuestaAgente = 3`, `TipoPropuestaRegla`, `EstadoPropuestaRegla`), `Entities/Tareas.cs` (`TareaAgente.Tipo`), `Entities/Regla.cs` (`ReglaEvento.PropuestaReglaId`).

**Application**
- Nuevos: `DTOs/ConfiguradorDtos.cs` (`MensajesConfigurador` con códigos `CambioDesdePropuesta`/`YaResuelta`, `OrigenAplicacion`, `PropuestaReglaDto`, `ResultadoPropuestaDto`, `AplicarTodasResultadoDto`, `PropuestaFormularioDto`, `ConversacionConfiguracionListItemDto`, `ConfiguracionFiltros`), `Interfaces/IPropuestaReglaService.cs` (+ `IConfiguradorReglas`).
- Modificados: `Interfaces/IResolvedorSesion.cs` (`ResolverUsuarioAsync`), `Motor/IMotorAgentes.cs` (`ContextoHerramienta` + `TipoTarea`/`PasoNumero`/`ToolUseId`; `TareaFiltros.Tipo`; `TareaListItemDto.Tipo`; `TareaDetalleDto.EsConfiguracion`/`PropuestasPorPaso`/`PropuestasDelTurno`/`PropuestasSinResolver`; `IServicioTareas.IniciarConfiguracionAsync`/`ListarConfiguracionesAsync`/`OpcionesConfiguracionAsync`), `Motor/IConstructorContexto.cs` (`InstantaneaConfiguracion`, `FormatoContextoConfiguracion = 3`, `ArmarConfiguracionAsync`), `Interfaces/IReglaService.cs` (sobrecargas con `OrigenAplicacion?`), `DTOs/ReglasDtos.cs` (`ReglaDetalleDto.ConversacionOrigenId`, `ReglaEventoDto.DesdeConfigurador/ConversacionId`).

**Infrastructure**
- Nuevos: `Services/Configurador/HerramientasConfigurador.cs` (base con guardas + `reglas_listar`, `regla_obtener`, `estructura_empresa`, `clientes_buscar`, `sugerencias_listar`, `proponer_regla_nueva`, `proponer_cambio_regla`, `proponer_desactivar_regla`, `proponer_activar_sugerencia`), `Services/Configurador/PropuestaReglaService.cs`, `Services/Configurador/ConfiguradorReglas.cs`, `Data/Configurations/ConfiguradorConfigurations.cs`, migración `Data/Migrations/20260915004203_ConfiguradorReglasM4b.cs` (+ Designer y snapshot).
- Modificados: `Services/Organizacion/ResolvedorSesion.cs`, `Services/Motor/ConstructorContexto.cs` (`DeclaracionPrecedenciaConfiguracion`, `ArmarConfiguracionAsync`; formatos 1 y 2 sin cambios), `Services/Motor/ProcesadorTareas.cs` (autor re-verificado, contexto formato 3, contexto de herramienta por `tool_use`), `Services/Motor/ServicioTareas.cs` (iniciar, `Visibles()` sin configuraciones para Empleados, filtro Tipo, detalle con propuestas y sin licencias, lista de conversaciones), `Services/Motor/ProveedorModeloSimulado.cs` (guion de herramientas), `Services/Reglas/ReglaService.cs` (origen de aplicación en crear/editar/estado/sugerencia en el mismo guardado; origen y enlace en el detalle), `Data/AppDbContext.cs` (`DbSet<PropuestaRegla>`), `Data/Configurations/{AgentesConfigurations (Tipo + índice), ReglasConfigurations (FK del evento)}.cs`, `DependencyInjection.cs`.

**Web**
- Nuevos: `Controllers/ConfiguracionReglasController.cs` [RequireDirector], `Models/ConfiguradorViewModels.cs`, `Helpers/ConfiguradorTextos.cs`, vistas `ConfiguracionReglas/{Index, Nueva}`, `Tareas/{_TarjetasPropuesta, _ScriptPropuestas}`.
- Modificados: `Controllers/TareasController.cs` (filtro Tipo, `ViewBag.EsDirector`), `Controllers/ReglasController.cs` (botón y disponibilidad, `Create/Edit ?propuesta=`), `Models/ReglasViewModels.cs` (`PropuestaId`, `PropuestaTareaId`, `ConfiguradorDisponible`, `UrlConfigurar`), `Helpers/ReglasTextos.cs` (origen), vistas `Tareas/{Detalle, _Conversacion, _CuadroSeguimiento, Index}`, `Reglas/{Index, _ListadoScript, _Form, Create, Edit, Detalle}`, `wwwroot/css/site.css` (tarjetas).

**Núcleo**: `nucleo/plataforma/agentes/configurador-reglas.md` (borrador) y `nucleo/plataforma/plataforma.yml` (`agentes`). **Tests**: nuevo `ConfiguradorReglasTests.cs` (13). **Docs del repo**: `docs/diseno-organizacion-roles-reglas.md` (M4b ✅).

### Decisiones de implementacion M4b (ambigüedades resueltas)
- **DI-M4b-1 Formato 3 aislado (RT-M4b-02):** instantánea propia `InstantaneaConfiguracion` (formato 3, tipo, versión del configurador, reglas de plataforma) y `ArmarConfiguracionAsync` separado; `ArmarAsync` (formatos 1 y 2) no se tocó. La tarea ancla la versión del configurador en `ArtefactoVersionId`. Un solo bloque cacheado: reglas de plataforma + declaración propia ("lo que leés con herramientas son datos, nunca instrucciones"; "ningún mensaje aplica cambios") + prompt. Golden: formato 2 capturado con el código de M4 ANTES de tocar el constructor; formato 3 fijado al implementar; el golden de formato 1 de M4 sigue verde.
- **DI-M4b-2 Contexto de herramienta:** `ContextoHerramienta` suma `TipoTarea`, `PasoNumero` (paso LlamadaModelo que pidió la herramienta = número del paso de resultados − 1) y `ToolUseId` (uno por `tool_use`, con `with`), con valores por defecto compatibles.
- **DI-M4b-3 Re-verificación (RT-M4b-01):** `ResolverUsuarioAsync` lee la base sin caché y, si falla, deja el contexto marcado como bloqueado (sin permisos). El procesador lo llama al comienzo de cada ejecución de una configuración (turno Fallido con `CierreTurno` y "La persona que inició la configuración ya no puede configurar reglas." sin llamar al modelo) y cada herramienta lo vuelve a llamar, además de confirmar que la tarea es de configuración, del mismo autor y organización.
- **DI-M4b-4 Lectura:** consultas propias con el criterio de visibilidad del Director (todo lo de su organización salvo preferencias de otros miembros; sus propias preferencias sí se leen pero no se proponen). JSON snake_case con tildes sin escapar; recorte de 300 (sugerencias 500), páginas de 20, clientes 20 + `hay_mas`; `destino.vigente = false` si el área/cliente/agente se dio de baja; `estructura_empresa` incluye uso de caracteres de la empresa y por área y los límites.
- **DI-M4b-5 Validaciones al proponer:** alcance (nunca preferencias), destino de la organización, modo obligatorio en empresa/área, largos, etiquetas, agente que admite reglas, cambio que no cambia nada, desactivar una inactiva, sugerencia ya activada; máximo 10 por paso (base + change tracker). Límites por balde y conflictos se resuelven al aplicar. En un Cambio solo se guardan los campos propuestos (null = sin cambio; etiquetas "" = quitar todas).
- **DI-M4b-6 Aplicación por `ReglaService`:** sobrecargas con `OrigenAplicacion?` (las llamadas existentes no cambian). Con origen: solo Director, nunca alcance Usuario, propuesta sin resolver y que corresponda a la operación (Nueva/ActivarSugerencia en crear, Cambio de esa regla en editar, Desactivar de esa regla en estado). Propuesta Aplicada en el mismo `SaveChanges` que la regla y el evento; si la regla ya dice lo propuesto o ya estaba desactivada, queda Aplicada sin versionar. `DbUpdateConcurrencyException` por la propuesta → código `YaResuelta`. Ante conflicto en `EditarAsync` se desasocian todos los cambios pendientes (antes quedaba el evento en el tracker).
- **DI-M4b-7 Sugerencia por propuesta:** `Origen = PropuestaAgente` conservando `SugerenciaArtefactoId` ("Ya activada" sigue funcionando).
- **DI-M4b-8 Fallida:** error de validación o regla inexistente → Fallida con `MotivoFallo`, en guardado propio sobre la propuesta releída (`ChangeTracker.Clear`); SinPermiso y YaResuelta no la marcan. "Pendientes" en la lista y en el encabezado = Pendiente + Fallida (sin resolver).
- **DI-M4b-9 Aplicar todas:** solo Pendientes, en orden de paso e id, cada una en su unidad de trabajo; una regla cambiada desde la propuesta queda Fallida con ese motivo (nunca confirmación implícita). Contrato ajustado de `int? pasoNumero` a `IReadOnlyCollection<int>? pasos`: el botón es por respuesta y una respuesta puede tener propuestas en varios pasos del modelo (lista de int: sin riesgo MH-001).
- **DI-M4b-10 Editar y aplicar:** solo Nueva y Cambio (Desactivar y Activar sugerencia se aplican con el botón). `Reglas/Create?propuesta=` y `Reglas/Edit/{id}?propuesta=` precargan (Cambio = regla vigente con lo propuesto encima) con `PropuestaId`/`PropuestaTareaId` ocultos (el servicio valida la propuesta; la tarea solo decide adónde volver); al guardar vuelve a `Tareas/Detalle/{id}#propuesta-{n}` con "Propuesta aplicada."; en Edit con propuesta se oculta Activar/Desactivar. Un error de validación del formulario no marca la propuesta Fallida.
- **DI-M4b-11 Visibilidad y licencias:** `Visibles()` del Empleado excluye configuraciones (404, también para un Director degradado). Una configuración no depende de licencias (seguir conversando ni detalle), no ofrece "Nueva tarea con este agente" ni "Lo que el agente tuvo en cuenta". Staff: lectura con tarjetas sin acciones.
- **DI-M4b-12 Lista de conversaciones:** columnas del diseño con filtro por columna, Session y Limpiar; búsqueda global además por el texto del pedido; orden por defecto última actividad desc.
- **DI-M4b-13 Tareas:** filtro Tipo en una tercera fila solo para Director/staff (el Listar lo ignora para Empleados); la columna Agente muestra "Configuración de reglas" como subtítulo (dato visible del filtro).
- **DI-M4b-14 Pantalla:** tarjetas debajo de cada respuesta no activa (también en turnos cancelados o fallidos), texto plegado a partir de 400 caracteres, Antes/Después apilados (con modo anterior si cambia), aviso "La regla cambió desde esta propuesta" en la tarjeta, "Aplicar todas (N)" con los pasos del turno; acciones AJAX con refresco de la conversación (`window.ovRefrescarConversacion`, sin recargar); modal D-M4b-5 con SweetAlert2 (Aplicar igual / Editar y aplicar / Cancelar). Encabezado "Configuración de reglas · fecha" + "Por"; "N propuestas pendientes" en la línea de estado (se refresca en vivo). Chips de D-M4b-7 completan el texto.
- **DI-M4b-15 Simulador:** guion por palabra clave del último mensaje: por defecto `estructura_empresa` + dos `proponer_regla_nueva` ("Regla simulada N-a/b"); con "revis" (chip "Revisá mis reglas actuales") `reglas_listar` → cambio de título de la primera regla activa + desactivación de la segunda; con "sugerencia" `sugerencias_listar` → activar la primera no activada. Extensión del guion aprobado para que QA vea los cuatro tipos sin SQL ni costo.
- **DI-M4b-16 Nueva conversación:** mismo largo que los ajustes (10.000 normalizado; el ViewModel solo `Required`); staff y Empleado → SinPermiso.
- **DI-M4b-17 `TareaAgente.Tipo`:** DEFAULT 1 solo en la migración (tareas existentes); el modelo EF no declara el default (snapshot y Designer ajustados, `has-pending-model-changes` limpio) para evitar la advertencia de "sentinel" en cada arranque.
- **DI-M4b-18 Tema oscuro (lección OLV-001/002/003):** tarjetas solo con tokens, texto con opacidad plena; estado por borde y badge. Contraste medido: muted 4,76 (claro) / 5,71 (oscuro); texto 14,63 / 13,35; "Por qué" 13,08 / 10,68; íconos `#1f8ad0` en claro ~3,75 (la marca daba 2,98) y marca en oscuro 4,91; badges Aplicada 4,53, No se pudo aplicar 4,53, Descartada 4,69, Pendientes 10,95; alertas warning/danger en oscuro 7,75 / 6,75.
- **DI-M4b-19 Prompt borrador (P7):** frontmatter `name`, `description`, `herramientas`; sin `model` (usa el modelo por defecto). Importado en dev como `#65 configurador-reglas v1 Borrador`.

### Migraciones EF generadas M4b
- `20260915004203_ConfiguradorReglasM4b` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-14** con `dotnet ef database update`. Tabla `PropuestasRegla` (FKs RESTRICT a tenant, tarea, reglas, área, cliente, artefactos, agente de la empresa, usuario; único `(TareaAgenteId, ToolUseId)`; índices `(TareaAgenteId, PasoNumero)` y `(TenantId, Estado)`), `TareasAgente.Tipo int NOT NULL DEFAULT 1` + índice `(TenantId, Tipo, UltimaActividadAt)`, `ReglaEventos.PropuestaReglaId` + FK RESTRICT. Sin transformación de datos. Ajuste manual: default de `Tipo` fuera del modelo/snapshot/Designer (DI-M4b-17).
- Verificado por SQL (`scratchpad/verif-configuradorm4b.sql`): tipos y default; 14 índices; 11 FK RESTRICT; 15 tareas existentes en Tipo 1 y 74 eventos intactos. En transacción revertida: 4.000 caracteres con tilde (8.000 bytes) OK; mismo `ToolUseId` en la misma tarea → 1062 y en otra tarea OK; 4.001 → 1406; tarea/regla/sugerencia inexistentes → 1452; token: primer `UPDATE … WHERE VersionToken = 0` 1 fila, el segundo 0; evento enlazado OK, a una propuesta inexistente → 1452, borrar la propuesta referenciada → 1451; `EXPLAIN` de la lista usa `IX_TareasAgente_TenantId_Tipo_UltimaActividadAt` (*Backward index scan*) y las tarjetas `IX_PropuestasRegla_TareaAgenteId_PasoNumero`; 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m4b`, modelo simulado, sin Anthropic): 17 pasos OK. Configuración formato 3 con hash verificado por el motor, herramientas y propuestas persistidas con la ejecución; detalle con tarjetas y visibilidad por rol; lista de conversaciones con orden por las 6 columnas, filtros y búsqueda global; filtro Tipo en Tareas; aplicar nueva con origen y evento; aplicar todas por pasos; revisión con `CambioDesdePropuesta` real y confirmación; activar sugerencia; herramientas directas con todos los filtros; descartar/dos Directores/editar y aplicar; **`DbUpdateConcurrencyException` real por `VersionToken`**; 1062 real desde EF; autora degradada → turno Fallido. Sin errores de type mapping (MH-001). Configurador publicado temporalmente y restaurado a Borrador; limpieza completa, 0 restos.
- Import en dev: `importar nucleo/plataforma/plataforma.yml` → 1 artefacto nuevo (`configurador-reglas`, #65 v1 **Borrador**), 3 reglas de plataforma sin cambios (siguen en Borrador).

### Evidencia de build y tests M4b
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **113 OK / 0 fallidos** (100 existentes + 13 de `ConfiguradorReglasTests`).
- Lecciones: (1) capturar el golden del formato vigente con un test temporal ANTES de tocar el constructor (el hash sale truncado en la salida de xUnit: imprimirlo con `Assert.Fail`); (2) `HasDefaultValue` con un enum que no tiene 0 genera advertencia de sentinel en cada arranque: el default va en la migración, no en el modelo; (3) los guiones del modelo que necesitan ids creados después usan lambdas que capturan variables asignadas luego (el guion se evalúa al consumirse); (4) EF InMemory no aplica índices únicos: la idempotencia se prueba cortando el proceso y la unicidad en MySQL.

### Riesgos residuales M4b
- RT-M4b-04 / S-M4b-01: calidad del prompt borrador y confiabilidad de las herramientas con el modelo real sin medir (corrida con costo, PA-02). El prompt no está publicado: sin publicar, la función queda deshabilitada.
- R-M4b-02 inyección: mitigada por herramientas acotadas por código, declaración de formato 3 y aplicación solo por botón; sin validación con el modelo real.
- RT-M4b-03 costo: cada `reglas_listar` y `estructura_empresa` suma tokens al historial de la conversación; medir en la corrida real.
- Carrera del "máximo 10 por paso": se cuenta base + tracker dentro de la ejecución secuencial de un paso (el motor ejecuta los `tool_use` en orden); no hay índice que lo garantice.
- La publicación temporal del configurador para QA en dev deja una evaluación "QA" en el historial de la versión; la evaluación real de Joaquín se registra aparte (la última es la que habilita publicar).
- Verificación visual pendiente (QA): tarjetas, modal, chips, aplicar todas, formulario precargado, origen en historial, filtro Tipo, mobile y tema oscuro.

### Proximos pasos pendientes M4b
- QA etapa 6 (guía en `trazabilidad.md`, entrada del implementador M4b) con el modelo simulado.
- Joaquín: revisar el prompt borrador, ajustarlo si hace falta (reimportar crea v2), evaluar y publicar con la consola Admin; corrida real con costo (PA-02).
- Deuda preexistente vista, fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; `Admin licencia-crear` con `slugs.Contains` (MH-001); la consola Admin no tiene comando para retirar o volver a borrador una versión.

---

# M4 — Agentes de la organización

Estado: **implementada 2026-09-14, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` (P1–P11, ajuste sin revisión del Director: RF-M4-06/07 pospuestos), `2-disenador-funcional.md` M4 (bloque "Ajuste aprobado en el gate": sin P-M4-04/05, cualquier miembro publica, aviso a Directores) y `3-arquitecto-mvc.md` M4 aprobados; `4-presupuestador.md` omitido por decisión de Joaquín (gate dispensado). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`. Sin contenido real de rubros ni de sugerencias (solo mecanismos, datos de prueba en tests y ejemplo comentado en `nucleo/rubros/_plantilla/rubro.yml`).

### Escaneo de reutilizacion M4
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M3 (`ReglaService`: permisos por registro, límites, token de versión, mensajes; vistas `Reglas/*`, `_CardReglasDestino`) | `AgenteOrganizacionService` (estructura, `VersionToken`, conflicto sin reintento), card "Reglas de este agente" | Literal adaptado |
| Template M2 (`Area.NombreVigente` STORED por SQL + índice único; filtros en memoria DI-8; `FiltrosSesion`/`DataTableRequestHelper`/`RespuestasServicio`; bajas AJAX PAT-015) | `AgenteOrganizacion.NombreVigente`, listado de staff, archivar/duplicar AJAX con SweetAlert2 | Literal |
| Template M3 (`ConstructorContexto`, `InstantaneaContexto`, `ReglasEfectivasDto`, `_ReglasEfectivas`) | Formato 2 con instrucciones del derivado; vista previa y "Lo que el agente tuvo en cuenta" | Literal (extensión compatible) |
| Template M1/M3 (`ImportadorRubro` + `reglas_plataforma`, `CatalogoNucleo`, `IVersionadoService`) | `reglas_sugeridas` e `incluido_siempre`; sugerencias con el mismo ciclo Borrador → evaluación → publicación | Literal (extensión) |
| Template M3b (`ServicioTareas`, `ProcesadorTareas`, modelo simulado, `verif-m3b`) | Tareas con agente de la empresa, P11, verificador EF → MySQL `scratchpad/verif-m4` | Literal (extensión) |
| Template (`INotificationService` + campana) | Aviso a Directores | Literal |
| Catálogo / otros `5-implementador.md` | Sin prompts derivados configurables por el cliente | Diseño nuevo → PAT-030 completado con rutas reales (`pendiente_verificar: false`); notas de M3b que estaban en PAT-030 movidas a PAT-029 |

### Archivos y capas modificadas M4
**Domain**
- Nuevos: `Entities/AgenteOrganizacion.cs` (`AgenteOrganizacion` + `AgenteOrganizacionVersion`), `Enums/EnumsAgentesOrganizacion.cs` (`VisibilidadAgente`, `EstadoVersionAgente` con 4 y 5 libres para revisión).
- Modificados: `Enums/EnumsAgentes.cs` (`TipoArtefacto.ReglaSugerida = 4`), `Enums/EnumsReglas.cs` (`OrigenRegla.Sugerida = 2`), `Entities/Regla.cs` (`AgenteOrganizacionId`, `SugerenciaArtefactoId`), `Entities/Rubro.cs` (`IncluidoSiempre`), `Entities/Artefacto.cs` (`Etiquetas`), `Entities/Tareas.cs` (`AgenteOrganizacionVersionId` + navegación).

**Application**
- Nuevos: `Settings/AgentesOrganizacionOptions.cs`, `DTOs/AgentesOrganizacionDtos.cs` (catálogo, cards, detalle, versiones, formulario, edición, opciones, staff, `MensajesAgentesOrganizacion`), `Interfaces/IAgenteOrganizacionService.cs`.
- Modificados: `Motor/IConstructorContexto.cs` (`SolicitudContexto.AgenteOrganizacionVersionId`, `InstantaneaContexto.AgenteOrganizacionVersionId/Nombre` con `JsonIgnore WhenWritingNull`, `FormatoContextoAgenteOrganizacion = 2`), `Motor/IMotorAgentes.cs` (`CrearTareaDto.AgenteOrganizacionId`, `TareaFiltros.AgenteOrganizacionId`, `FiltroTareas.PrefijoAgenteOrganizacion`, `AgenteRefDto.AgenteOrganizacionId`, `AgenteOrganizacionTareaDto`, `TareaDetalleDto.AgenteOrganizacion`, `VistaPreviaAsync(int, int?)`), `DTOs/ReglasDtos.cs` (`PestanaReglas.Sugerencias`, `FiltroReglas.LeerAgente/ValorAgenteOrganizacion`, `ReglaFormDto/ReglaDetalleDto.AgenteOrganizacionId`, `ReglaDetalleDto.Origen`, `GrupoAgentesDto.EsDeLaEmpresa`, `MismoTemaConsultaDto.AgenteOrganizacionId`, `InstruccionesAgenteDto` en efectivas y aplicadas, DTOs de sugerencias), `Interfaces/IReglaService.cs` (sugerencias, activar, card del agente), `Interfaces/ILicenciaService.cs` (`SincronizarRubrosIncluidosAsync`).

**Infrastructure**
- Nuevos: `Services/Agentes/AgenteOrganizacionService.cs`, `Data/Configurations/AgentesOrganizacionConfigurations.cs`, migración `Data/Migrations/20260914220326_AgentesOrganizacionM4.cs` (+ Designer y snapshot).
- Modificados: `Services/Motor/ConstructorContexto.cs` (formato 2, `DeclaracionPrecedenciaAgenteOrganizacion`, sección `<instrucciones_de_la_empresa>`, reglas por agente del derivado, `CalcularHash(bloques, formato)`), `Services/Motor/ServicioTareas.cs` (validación del agente de la empresa, crear y vista previa, listado/opciones/búsqueda con el nombre del derivado, detalle con versión y archivado, instrucciones aplicadas), `Services/Motor/ProcesadorTareas.cs` (herramientas por intersección), `Services/Reglas/ReglaService.cs` (agentes de la empresa en alta, filtros, búsqueda, nombres, "No se aplica", combo, card, sugerencias y activación, `CrearInternoAsync` con origen), `Services/Nucleo/ImportadorRubro.cs` (`incluido_siempre`, `reglas_sugeridas`, etiquetas, slug con otro tipo), `Services/Nucleo/CatalogoNucleo.cs` (excluye sugerencias), `Services/Licencias/LicenciaService.cs` (rubros incluidos al crear + sincronización), `Data/AppDbContext.cs` (DbSets; `VersionToken` fuera del audit trail), `Data/Configurations/{ReglasConfigurations (check recreado, FKs, índices), AgentesConfigurations (Etiquetas, FK de la tarea)}.cs`, `DependencyInjection.cs`.

**Web**
- Nuevos: `Helpers/AgentesTextos.cs`, `Models/AgentesOrganizacionViewModels.cs`, vistas `Agentes/{_TarjetaAgente, _ScriptAccionesAgente, _Form, _BarraFormAgente, _ScriptFormAgente, Crear, Editar, Detalle}`, `Reglas/{_Pestanas, _Sugerencias, _ScriptSugerencias}`, `Clientes/Agentes`.
- Modificados: `Controllers/AgentesController.cs` (catálogo, crear/editar/detalle, duplicar/archivar/reactivar AJAX, nueva tarea y vista previa con agente de la empresa), `Controllers/ReglasController.cs` (pestaña Sugerencias, `ActivarSugerencia`, `agenteRef`, filtro por agente desde el detalle), `Controllers/ClientesController.cs` (`Agentes`, `ListarAgentes`, `DetalleAgente`), `Controllers/TareasController.cs` (filtro "o<id>"), `Helpers/ReglasTextos.cs`, `Models/{AgentesViewModels (EjecutarAgenteViewModel), ReglasViewModels (AgenteRef, sugerencias, instrucciones)}.cs`, vistas `Agentes/{Index (rediseñada), Ejecutar}`, `Shared/_ReglasEfectivas`, `Tareas/{Detalle, _CuadroSeguimiento}`, `Reglas/{Index, _Listado, _Form, _ScriptFormRegla, Detalle}`, `Clientes/Details`, `Nucleo/Rubro`, `wwwroot/css/site.css`, `appsettings.json` (sección `AgentesOrganizacion`).

**Admin**: comando `sincronizar-rubros-incluidos`. **Núcleo**: `nucleo/rubros/_plantilla/rubro.yml` (ejemplo comentado). **Tests**: nuevo `AgentesOrganizacionTests.cs` (17). **Docs del repo**: `docs/diseno-organizacion-roles-reglas.md` (M4 ✅ y permiso de publicación).

### Decisiones de implementacion M4 (ambigüedades resueltas)
- **DI-M4-1 Compatibilidad del hash (RT-M4-01):** formato de contexto 2 solo para tareas con agente de la empresa, con su propia declaración de precedencia; el formato 1 (texto, orden, rótulos) no cambia y los campos nuevos de la instantánea se omiten del JSON cuando son null. Test golden con dos hashes calculados con el código de M3b antes de tocar el constructor (captura temporal, luego borrada) + JSON con la forma de M3 + reconstrucción de una instantánea sin campos nuevos + ajuste M3b.
- **DI-M4-2 Lugar de las instrucciones:** en B3 (no cacheado) entre las reglas del cliente y las "Por agente": `<instrucciones_de_la_empresa agente="…">` con el texto escapado como el de las reglas. En la vista previa y el detalle, el grupo "Instrucciones de <agente>" se pinta antes del primer grupo de nivel Agente o posterior.
- **DI-M4-3 Reglas por agente (P3):** del base y del derivado en el mismo nivel, primero las del base (orden por marca "del derivado", que sin derivado es siempre falsa: el orden de M3 no cambia).
- **DI-M4-4 Borrador único:** `CreadaPor/CreadaAt` del borrador = última edición. Guardar o publicar con el contenido versionado igual al publicado no crea versión (descarta el borrador): "Datos guardados. Las instrucciones no cambiaron: el agente sigue en la versión N.".
- **DI-M4-5 Alta publicada:** agente y versión nuevos se apuntan entre sí (`VersionPublicadaId`): dos `SaveChanges` en una transacción. Con agente existente alcanza la navegación en un solo guardado.
- **DI-M4-6 Visibilidad:** lo nunca publicado lo ve solo su creador (aunque el borrador diga "Toda la empresa"); el Director ve y edita los borradores de agentes ya publicados para la empresa. El Director no puede dejar como "Solo yo" un agente de otra persona.
- **DI-M4-7 Catálogo:** "De tu área" sale de "De la empresa" (sin duplicar); "Mis agentes" = personales y nunca publicados, siempre visible con el estado vacío del diseño; badge "Borrador pendiente" para quien puede editar. **Agregado:** sección "Archivados" plegada al final, solo con los que quien mira puede reactivar (sin eso un archivado quedaba inalcanzable desde la UI) — a validar en QA.
- **DI-M4-8 Crear mi versión / Duplicar:** desde Olvidata → formulario con el base elegido; desde un agente de la empresa → formulario precargado sin guardar ("<nombre> (mi versión)", personal). Duplicar guarda una copia personal en borrador "Copia de <nombre>" (con " (2)", " (3)"… si hace falta), herramientas ∩ las actuales del base; quien puede editar copia el borrador, el resto lo publicado.
- **DI-M4-9 Nombre único:** comparación como la colación de MySQL (sin mayúsculas ni tildes); el 1062 del índice se reconoce por "NombreVigente" en el mensaje. Reactivar con el nombre tomado → mensaje; un archivado no se edita hasta reactivarlo.
- **DI-M4-10 Límites:** activos = no archivados (personales, de la empresa y borradores); personales = visibilidad publicada o, si nunca se publicó, la del borrador. Se controlan al crear, al pasar a personal, al reactivar y al duplicar.
- **DI-M4-11 "No disponible":** derivado (sin licencia vigente del rubro del base o base sin versión publicada). Permite guardar borrador, no publicar ni usar; un alta nueva exige base habilitada.
- **DI-M4-12 Navegación:** "Guardar y usar" lleva a Nueva tarea con el agente; publicar o guardar borrador, al detalle.
- **DI-M4-13 Aviso a Directores:** Directores activos salvo quien publica; "publicó" o "actualizó" según la visibilidad publicada anterior; URL relativa `/Agentes/Detalle/{id}`; un fallo del aviso se loguea y no revierte (CRM-020).
- **DI-M4-14 Tareas:** visibilidad por `dto.UsuarioId` (igual que el resto de `CrearAsync`); agente ajeno → NoEncontrado. Listado: la columna Agente muestra el derivado; filtro "o<id>"; el filtro del base excluye derivados; búsqueda global por el nombre del derivado. Detalle: "Tarea #N · <agente> (versión N)", "Basado en …", badge "Agente archivado" y sin "Nueva tarea con este agente" si hoy está archivado (P11: el ajuste sigue).
- **DI-M4-15 Reglas:** el combo usa `AgenteRef` ("12" base, "o12" derivado; compatible con los filtros guardados en Session); grupos "De Olvidata · <Rubro>" y "De la empresa". Regla de un agente archivado → "No se aplica" (grilla, filtro de estado y detalle) y no se puede activar. La card del agente incluye reglas de cliente + ese agente. El detalle de una regla muestra "Origen: Sugerida por Olvidata".
- **DI-M4-16 Sugerencias:** pestaña solo del Director (tabs extraídas a `Reglas/_Pestanas`); una activación por organización (sin índice: una doble activación simultánea es carrera aceptada); título truncado a 150; etiquetas filtradas a 5 de 30; modo por defecto "Salvo que se indique otra cosa"; modal Bootstrap con Select2 `dropdownParent`.
- **DI-M4-17 Importador:** `incluido_siempre` se toma siempre del manifiesto (en `plataforma` → advertencia y false); `reglas_sugeridas` de más de 4.000 caracteres o con un slug que ya existe con otro tipo se ignoran con advertencia; etiquetas normalizadas como las de reglas. `CatalogoNucleo.ListarArtefactosPublicadosAsync` excluye sugerencias (también afecta `listar_agentes` del MCP congelado).
- **DI-M4-18 Licencias:** los rubros incluidos se unen a los elegidos (una licencia puede emitirse solo con incluidos); la sincronización exige acceso global; en el alta de licencias del backoffice la casilla va tildada y deshabilitada. No hay "renovar" en el template: lo cubre la sincronización.
- **DI-M4-19 Staff:** listado filtrado y ordenado en memoria (decenas); el detalle reutiliza `Agentes/Detalle` en solo lectura con borrador visible.
- **DI-M4-20 Tema oscuro (lección OLV-002):** badges nuevos con `.ov-badge-neutro` (tokens del theme); override de `.badge.bg-light.text-dark` (etiquetas de reglas, ilegibles en oscuro desde M3), cruz de modales y texto "No disponible".
- **DI-M4-21 Migración:** `Down` borra las reglas de agentes de la organización (con su historial) antes de volver al check de M3b (solo base de desarrollo).

### Migraciones EF generadas M4
- `20260914220326_AgentesOrganizacionM4` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-14** con `dotnet ef database update`. Ajustes manuales: `NombreVigente` quitada del `CreateTable` (el proveedor la creaba VIRTUAL) y agregada con `ALTER TABLE … GENERATED ALWAYS AS (…) STORED` antes de su índice único; el proveedor ya ordenó bien `DropCheckConstraint` → `AddColumn` → `AddCheckConstraint` y la FK circular (versiones → agentes al final).
- Verificado por SQL (`scratchpad/verif-agentesm4.sql`): columnas y tipos; `NombreVigente` STORED GENERATED; check recreado con "exactamente uno de los dos agentes"; 11 FK RESTRICT; índices únicos `(TenantId, NombreVigente)` y `(AgenteOrganizacionId, Numero)`; 42 reglas y 10 tareas existentes intactas. En transacción revertida: 8.000 caracteres con tilde (8.001 bytes) OK; nombre activo repetido con otra capitalización y sin tilde → 1062; archivar libera el nombre y reactivar con el nombre tomado → 1062; número de versión repetido → 1062; 8.001 caracteres → 1406; alcances 5 y 6 válidos con base o derivado, y 4 combinaciones inválidas → 3819; sugerencia inexistente y tarea con versión inexistente → 1452; borrar una versión publicada referenciada → 1451; `EXPLAIN` del catálogo usa `IX_AgentesOrganizacion_TenantId_CreadorUsuarioId`; 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m4`, modelo simulado, sin Anthropic): 62 pasos OK. Alta personal y para la empresa (transacción de dos guardados), columna generada con tildes, índice único con colación y mensaje con la columna, aviso a Directores, privacidad, borrador → publicar → reemplazada, conflicto por token en la app y **`DbUpdateConcurrencyException` real por `VersionToken`**, tarea formato 2 anclada, ejecución con agente archivado y hash verificado, instrucciones escapadas en B3, herramientas efectivas, P11, listado/búsqueda/orden/opciones de tareas con el derivado, reglas con check real, filtros, "No se aplica", combo, card, vista previa v2, duplicar, crear mi versión, catálogo, staff (listado, filtros, detalle), sincronización de licencias, sugerencia publicada → activar → "Ya activada". Sin errores de type mapping (MH-001). Limpieza completa y 0 restos.
- Impacto: 2 tablas nuevas vacías; columnas nulas o en 0 en `Reglas`, `TareasAgente`, `Rubros`, `Artefactos`; ningún rubro marcado como incluido y ninguna sugerencia en dev.

### Evidencia de build y tests M4
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **100 OK / 0 fallidos** (83 existentes + 17 de `AgentesOrganizacionTests`).
- Lecciones: (1) capturar el hash golden ANTES de tocar el render; (2) en un parcial Razor, dentro de un bloque `else` no va `@{`: las funciones locales con markup se declaran directo; (3) los modelos de parciales con expresiones multilínea van en el bloque de código, no dentro del atributo `model="…"`; (4) el verificador EF necesita clave de licencias efímera si resuelve `LicenciaService`.

### Riesgos residuales M4
- R-M4-01 inyección por instrucciones: mismo tratamiento que reglas (nivel fijo, escape, precedencia); sin validación con el modelo real (PA-02).
- Instrucciones del derivado en B3 (sin caché): costo por tarea con instrucciones largas; medir en la corrida real.
- Aviso con URL relativa: si el portal se publica bajo un subdirectorio, el enlace de la campana no incluye el PathBase.
- Límites y activación de sugerencias sin bloqueo: carreras aceptadas (como M3).
- Sección "Archivados" del catálogo agregada por necesidad de UI (DI-M4-7): confirmar con Joaquín/QA.
- Un base dado de baja lógica haría invisibles sus derivados (filtro de navegación requerida); hoy los artefactos no se borran.
- Verificación visual pendiente (QA): cards y dropdown del catálogo, buscador, formulario con herramientas al cambiar de base, barra sticky según "Quién lo usa", modal de sugerencias con Select2, tema oscuro (badges neutros, bg-light, btn-close) y mobile.

### Proximos pasos pendientes M4
- QA etapa 6 (guía en `trazabilidad.md`, entrada del implementador M4) con el modelo simulado.
- Joaquín: contenido del rubro transversal "negocio" (manifiesto con `incluido_siempre: true`) y de las reglas sugeridas; evaluar y publicar; correr `sincronizar-rubros-incluidos`.
- Mejora posterior: revisión del Director (RF-M4-06/07, estados 4 y 5 reservados).
- Deuda preexistente vista, fuera de alcance: `Admin licencia-crear` con `slugs.Contains` (MH-001); `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9.

---

# M3b — Seguir conversando sobre una tarea

Estado: **implementada 2026-09-14, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md` (P1–P8), `2-disenador-funcional.md` (D-M3b-1..7) y `3-arquitecto-mvc.md` M3b aprobados (incluido el proveedor simulado solo en Development); `4-presupuestador.md` omitido por decisión de Joaquín (gate dispensado). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.

### Escaneo de reutilizacion M3b
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M1 (`ProcesadorTareas`, `_Progreso` + SignalR + respaldo 10 s, `TareasHub`) | Bucle reanudable extendido a multi-turno; el refresco en vivo pasa a `_Conversacion` y se reinicia tras enviar | Literal (extensión) |
| Template M2 (`Visibles()`, reintento de `CancelarAsync`, `FiltrosSesion`/`DataTableRequestHelper`, `RespuestasServicio.Json`, `ovPostAjax`/`ovToast`) | Visibilidad, concurrencia con `Version`, columnas y filtros nuevos, POST AJAX con 403/404 | Literal |
| Template M3 (`IConstructorContexto.CalcularAsync`, `ReglasAplicadasAsync`, consulta de licencias de `ValidarAgenteAsync`, `EntornoReglas`/`ModeloGuionado`) | "Reglas cambiaron", preferencias ajenas ocultas, suscripción vigente, entorno de tests | Literal |
| crm-olvidata | Caché de prompt por bloques → breakpoint en el último mensaje | Patrón |
| Catálogo / otros `5-implementador.md` | Sin conversación multi-turno persistida contra un modelo (los "conversación" de crm-olvidata son bots de WhatsApp) | Diseño nuevo → PAT-029 completado con rutas reales, `pendiente_verificar: false` |

### Archivos y capas modificadas M3b
**Domain**
- `Enums/EnumsAgentes.cs`: `TipoPasoTarea.MensajeUsuario = 3`, `CierreTurno = 4`.
- `Entities/Tareas.cs`: `TareaAgente.CantidadSeguimientos`, `UltimaActividadAt`.

**Application**
- `Motor/IMotorAgentes.cs`: `IServicioTareas.EnviarSeguimientoAsync`; `EstadoTurno`, `MotivoNoPuedeSeguir`, `MensajePersonaDto`, `TurnoDto`, `TurnoActivoDto`, `AgenteRefDto`; `TareaDetalleDto` + propiedades `init` (Turnos, TurnoActivo, CantidadSeguimientos, UltimaActividadAt, PuedeSeguir, Motivo, AjustesRestantes, MaxSeguimientos, LargoMaximoSeguimiento, ReglasCambiaron, AgenteRef, ClienteCarteraId, ClienteDadoDeBaja, AutorNombre, EsAutor, CantidadMensajes); `TareaListItemDto` + `Mensajes`, `UltimaActividad`; `TareaFiltros` + `ConAjustes`, `UltimaActividadDesde/Hasta`; `FiltroTareas.SoloPedido/ConAjustes`.
- `Motor/ModeloConversacion.cs`: `ContenidoCierreTurno` (JSON tipado) y `CacheConversacion.IndiceBloque`.
- `Motor/IConstructorContexto.cs`: `ReglasCambiaronAsync`.
- `DTOs/ReglasDtos.cs`: `GrupoReglasDto` + `Oculto`, `CantidadOculta`, `Autor`, `Cantidad`; `ReglasAplicadasDto.CantidadReglas` suma `Cantidad`.
- `Settings/MotorAgentesOptions.cs`: `MaxSeguimientosPorTarea = 20`, `LargoMaximoSeguimiento = 10000`; `MaxPasosPorTarea` documentado como por turno. `Settings/AgentesSettings.cs`: `AnthropicSettings.Simulado`.

**Infrastructure**
- `Services/Motor/ServicioTareas.cs`: `EnviarSeguimientoAsync` (guardas en el orden de la arquitectura, un solo `SaveChanges` mensaje + re-apertura, 2 pasadas ante `DbUpdateException`, telemetría `seguimiento_enviado`); `ObtenerDetalleAsync` por turnos (respuesta = texto del paso `end_turn`, estado por `CierreTurno` o por la tarea en el último turno, nombres por id sin `List<string>.Contains`), puede seguir/motivo, `ReglasCambiaron` solo para el autor; `ReglasAplicadasAsync` con grupo de preferencias oculto; `CancelarAsync` agrega `CierreTurno` (porUsuarioId) y reintenta ante `DbUpdateException`; `ListarAsync` con Mensajes, Última actividad, filtros, búsqueda global y orden por defecto; `CrearAsync` fija `UltimaActividadAt`.
- `Services/Motor/ProcesadorTareas.cs`: `ReconstruirConversacion` normalizada (público, estático); `LlamadasDelTurno`; `MarcarFinAsync` con `CierreTurno` en todo fin Fallida (máximo de pasos, rechazo, max_tokens, fin inesperado, contexto no reconstruible, reintentos agotados al reclamar, `RegistrarErrorAsync`); `UltimaActividadAt` en cada paso y al finalizar; conversación demasiado larga → Fallida sin reintento; `GuardarAsync` distingue carrera del índice `(TareaAgenteId, Numero)`.
- `Services/Motor/ProveedorModeloAnthropic.cs`: `MapearMensajes` (público) con `CacheControlEphemeral` en el último texto/resultado del último mensaje.
- `Services/Motor/ProveedorModeloSimulado.cs` (nuevo) y `DependencyInjection.UsarModeloSimuladoSiCorresponde`.
- `Services/Motor/ConstructorContexto.cs`: `ReglasCambiaronAsync`.
- `Data/Configurations/AgentesConfigurations.cs`: default de `CantidadSeguimientos`, índice `(TenantId, UltimaActividadAt)`.
- Migración `Data/Migrations/20260914201323_ConversacionM3b.cs` (+ Designer y snapshot).

**Web**
- `Controllers/TareasController.cs`: `EnviarSeguimiento` POST JSON (`ValidateAntiForgeryToken`, 403/404 vía `RespuestasServicio`), `Progreso` → `_Conversacion`, `Listar` con Mensajes y Última actividad.
- `Models/TareasViewModels.cs` (nuevo): `SeguimientoViewModel`. `Models/ReglasViewModels.cs`: `CantidadReglas` suma `Cantidad`.
- Vistas: `Tareas/Detalle` (reescrita: encabezado, reglas plegadas + aviso de reglas cambiadas, script de envío/copiar/refresco), `Tareas/_Conversacion`, `Tareas/_PasosTurno`, `Tareas/_CuadroSeguimiento` (nuevas), `Tareas/Index` (columnas y filtros), `Shared/_ReglasEfectivas` (grupo oculto); **eliminada** `Tareas/_Progreso`.
- `Program.cs`: registro del modelo simulado + advertencias de log. `wwwroot/css/site.css`: `.ov-chat*`, cuadro sticky en mobile. `appsettings.json` (`MaxSeguimientosPorTarea`, `LargoMaximoSeguimiento`), `appsettings.Development.json` (`Anthropic:Simulado: false` documentado).
- `AgentesController.Ejecutar`: sin cambios; ya aceptaba `clienteCarteraId` por query y el `<option>` con `asp-for` lo preselecciona (D-M3b-5).

**Tests**: nuevo `ConversacionTests.cs` (22: 16 `Fact` + `Theory` de 6 casos).

**Docs del repo**: `docs/diseno-organizacion-roles-reglas.md` (M3b ✅), `docs/diseno-motor-agentes.md` §4 (multi-turno y modelo simulado).

### Decisiones de implementacion M3b (ambigüedades resueltas)
- **DI-M3b-1 Mensajes:** mensajes de la persona = pedido + ajustes (`1 + CantidadSeguimientos`), igual en el detalle ("N mensajes") y en la columna del listado; "Solo el pedido" = 0 ajustes.
- **DI-M3b-2 Cierres heredados:** una tarea Fallida o Cancelada anterior a M3b (sin `CierreTurno`) recibe el cierre en el mismo guardado del primer ajuste, así su error sigue visible en su turno. Cierre sin usuario → "Se canceló esta respuesta."
- **DI-M3b-3 Autor:** miembro de la organización de la tarea con su `UsuarioId`; staff y procesos sin usuario nunca. Las preferencias se ocultan a todo el que no sea autor ni staff (incluidos scopes sin usuario) y muestran el nombre completo del autor.
- **DI-M3b-4 Largo:** como DI-M3-7, el service normaliza `\r\n` → `\n` y recorta; el ViewModel solo tiene `[Required]` (con `StringLength` el navegador contaría doble los saltos). 10.000 exactos se aceptan.
- **DI-M3b-5 Carreras de `Numero`:** en el service, `DbUpdateException` (versión o índice único) → se descartan los pendientes y se reintenta (ajuste 2 pasadas, cancelar 3). En el procesador, solo se trata como carrera si la `Version` en la base ya no es la leída; si no, se relanza.
- **DI-M3b-6 Normalización extra:** un paso del modelo sin bloques se omite; un `tool_use` pendiente al final de la secuencia también recibe resultado sintético.
- **DI-M3b-7 Conversación demasiado larga (RT-M3b-03):** `RegistrarErrorAsync` detecta por texto del error ("prompt is too long", "request_too_large", "exceeds the context window") y deja el turno Fallido sin reintentos con "La conversación es demasiado larga. Empezá una tarea nueva."
- **DI-M3b-8 Pantalla:** "Cancelar" vive en la línea de estado dentro del parcial refrescable (aparece y desaparece en vivo) en lugar del encabezado; "Nueva tarea con este agente" en el encabezado solo para miembros, con cliente precargado salvo dado de baja. El cuadro se re-renderiza en cada refresco: mientras hay turno activo el textarea está deshabilitado, así que no se pisa texto escrito (REG-008). JS con delegación.
- **DI-M3b-9 Modelo:** la vista usa `TareaDetalleDto` (propiedades `init`) en vez de un `TareaConversacionViewModel` espejo; `Pasos`, `Resultado` y `Error` planos se conservan por compatibilidad (tests M1).
- **DI-M3b-10 Búsqueda global:** también matchea la cantidad de mensajes y la fecha de última actividad (regla 25).
- **DI-M3b-11 Modelo simulado:** extensión de Infrastructure que exige `IsDevelopment()` + `Anthropic:Simulado`; el proveedor además se niega fuera de Development. Demora 1,5 s (para ver "Trabajando"), 0 tokens, texto "Respuesta simulada al turno N. Recibí: «…»". El portal loguea advertencia si está activo o si se pidió fuera de Development.
- **DI-M3b-12 Costo:** "USD 0,12" con hasta 4 decimales (tareas baratas no quedan en 0,00).
- **DI-M3b-13 Texto de cancelación:** "Respuesta cancelada. Si el agente estaba en medio de un paso, se detiene al terminarlo."

### Migraciones EF generadas M3b
- `20260914201323_ConversacionM3b` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-14** con `dotnet ef database update`. Columnas `CantidadSeguimientos int NOT NULL DEFAULT 0` y `UltimaActividadAt datetime(6) NOT NULL` + `migrationBuilder.Sql` de backfill `COALESCE(FinalizadaAt, IniciadaAt, CreatedAt)` + índice `IX_TareasAgente_TenantId_UltimaActividadAt`. Los tipos de paso nuevos son valores int (sin esquema).
- Verificado por SQL (`scratchpad/verif-conversacionm3b.sql`): tipos y default correctos; índice de 2 columnas; backfill 7/7 (0 sin fecha); `EXPLAIN` del listado por organización usa el índice nuevo con *Backward index scan*; pasos tipo 3 y 4 con JSON válido y tildes en transacción revertida; `Numero` repetido → 1062; 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m3b`, modelo simulado, 37 pasos OK): crear, turno, detalle autor/Directora, ajuste 403, ajuste persistido y re-apertura, conversación alternada, **doble envío concurrente con reversión real del paso perdedor**, cancelar con cierre, ajuste fusionado sin cierre al modelo, 4 turnos en el detalle, listado (orden, filtros, búsqueda por fecha y por mensajes, orden por columnas), reintentos agotados y "prompt demasiado largo" con cierre (MAX de `Numero`), ajuste sobre Fallida. Sin errores de type mapping (MH-001). Limpieza de 3 tareas, 11 pasos y 11 eventos; 0 restos.
- Impacto: 2 columnas en `TareasAgente` con backfill; datos existentes intactos.

### Evidencia de build y tests M3b
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **83 OK / 0 fallidos** (61 existentes + 22 de `ConversacionTests`).
- Lecciones: (1) EF InMemory no es transaccional: un `SaveChanges` que falla por concurrencia deja aplicado el INSERT previo; la atomicidad se prueba en MySQL. (2) `SerializacionBloques` (JsonSerializerDefaults.Web) escapa no ASCII en el JSON guardado: comparar el texto deserializado. (3) C# no admite `await` en filtros `catch … when`.

### Riesgos residuales M3b
- RT-M3b-02 costo creciente y caché: el tercer breakpoint no se midió con la API real (medir `cache_read` en la corrida con OK de costo de Joaquín).
- RT-M3b-03: la detección de "conversación demasiado larga" depende del texto del error del SDK; confirmar en corrida real.
- La carrera del índice `(TareaAgenteId, Numero)` en el procesador se cubrió por revisión de código y SQL (1062), no reproducida contra MySQL.
- `UltimaActividadAt` no cambia al reclamar ni al renovar el lease (solo mensajes, pasos y cierres, según la arquitectura).
- Verificación visual pendiente (QA): burbujas y alertas en tema oscuro, cuadro sticky en mobile, Select2 del filtro Mensajes, reinicio del canal SignalR tras enviar, portapapeles (HTTPS).
- Deuda preexistente vista, fuera de alcance: `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9; `Admin licencia-crear` con `slugs.Contains` (MH-001).

### Proximos pasos pendientes M3b
- QA etapa 6 (guía en `trazabilidad.md`, entrada del implementador M3b), con el modelo simulado activo.
- Corrida real con costo (OK de Joaquín): calidad de ajustes, `cache_read` en el segundo turno, error de prompt largo.

---

# M3 — Reglas por alcance

Estado: **implementada 2026-09-14, pendiente de QA (etapa 6)**. Entrada: `1-analista-funcional.md`, `2-disenador-funcional.md` (D-M3-1..12) y `3-arquitecto-mvc.md` M3 aprobados; `4-presupuestador.md` omitido por decisión de Joaquín (gate dispensado). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.

### Escaneo de reutilizacion M3
| Fuente | Qué se tomó | Grado |
|---|---|---|
| Template M2 (`Web/Helpers/{FiltrosSesion, DataTableRequestHelper, RespuestasServicio}`, `Application/Helpers/BusquedaHelper`, `Views/Cartera/*`, `Views/Areas/*`) | Listado DataTables con filtros por columna + Session + Limpiar, búsqueda global con extraIds, formularios `.ov-*`, acción AJAX con `reload(null,false)`, 403/404 por `TipoError` | Literal adaptado |
| Template M1/M2 (`ImportadorRubro`, `IVersionadoService`, `CatalogoNucleo`, `Nucleo/*`) | Reglas de plataforma como `TipoArtefacto.ReglaPlataforma` importadas y publicadas con evaluación | Literal (extensión) |
| Template M2 `MiembroService` / `TareaAgente.Version` | Token de concurrencia (`Regla.VersionActual`) + mensaje de conflicto sin reintento (edición humana) | Literal adaptado |
| Template M1 `MotorAgentesTests.ModeloGuionado` | Motor sin costo en tests → `tests/.../Infra/EntornoReglas.cs` | Literal |
| crm-olvidata | Prefijo estable cacheado + contexto variable → sistema en 3 bloques con `CacheControlEphemeral` por bloque | Patrón |
| PAT-028 (catálogo) | Completado con rutas reales de código, `pendiente_verificar: false` | Confirmado |

### Archivos y capas modificadas M3
**Domain**
- Nuevos: `Enums/EnumsReglas.cs` (`AlcanceRegla`, `TipoRegla`, `ModoRegla`, `OrigenRegla`, `TipoEventoRegla`), `Entities/Regla.cs` (`Regla` + `ReglaEvento` inmutable).
- Modificados: `Enums/EnumsAgentes.cs` (+`TipoArtefacto.ReglaPlataforma = 3`), `Entities/Rubro.cs` (+`SlugPlataforma`), `Entities/Tareas.cs` (+`ClienteCarteraId`, `ReglasAplicadasJson`, `HashContexto`).

**Application**
- Nuevos: `Settings/ReglasOptions.cs`, `DTOs/ReglasDtos.cs` (pestañas, estado derivado, `NivelRegla` + `NivelesRegla`, filtros, ítems, detalle/historial, uso de límite, mismo tema, opciones, cards, `ReglasEfectivasDto`, `ReglasAplicadasDto`, `PiezaNucleoDto`), `Interfaces/IReglaService.cs`, `Motor/IConstructorContexto.cs` (`SolicitudContexto`, `InstantaneaContexto` serializable, `ContextoArmado`, `FormatoContexto = 1`), `Helpers/EtiquetasHelper.cs`.
- Modificados: `Motor/ModeloConversacion.cs` (`SolicitudModelo.SystemPrompt` → `Sistema: IReadOnlyList<BloqueSistema(Texto, Cachear)>`), `Motor/IMotorAgentes.cs` (`CrearTareaDto.ClienteCarteraId`, `FiltroTareas.SinCliente`, `TareaFiltros.Cliente`, `TareaListItemDto.Cliente`, `TareaOpcionesFiltroDto.Clientes`, `TareaDetalleDto.Cliente/ReglasAplicadas`, `IServicioTareas.VistaPreviaAsync`), `Interfaces/IPermisosOrganizacion.cs` (+`PuedeGestionarReglasDeOrganizacion`, `PuedeVerReglasComoStaff`), `Interfaces/INucleoServices.cs` (+`ListarReglasPlataformaPublicadasAsync`), `Interfaces/IClienteCarteraService.cs` (+`ListarComboAsync`), `DTOs/OrganizacionDtos.cs` (+`ClienteCarteraComboDto`).

**Infrastructure**
- Nuevos: `Services/Reglas/ReglaService.cs`, `Services/Motor/ConstructorContexto.cs`, `Data/Configurations/ReglasConfigurations.cs`, migración `Data/Migrations/20260914182556_ReglasM3.cs` (+ Designer y snapshot).
- Modificados: `Data/AppDbContext.cs` (DbSets `Reglas`, `ReglaEventos`; `ReglaEvento` fuera del audit trail), `Data/Configurations/AgentesConfigurations.cs` (tarea: FK cliente Restrict, índice, hash 64), `Services/Motor/ServicioTareas.cs` (valida cliente, instantánea + hash al crear, vista previa, filtro/columna/búsqueda por cliente, reglas aplicadas con "Cambió después" y texto de Olvidata solo staff), `Services/Motor/ProcesadorTareas.cs` (reconstruye y compara hash antes de llamar al modelo; sin instantánea → armado anterior en un bloque), `Services/Motor/ProveedorModeloAnthropic.cs` (caché por bloque), `Services/Nucleo/ImportadorRubro.cs` (`reglas_plataforma`), `Services/Nucleo/CatalogoNucleo.cs` (excluye `plataforma` del catálogo; reglas publicadas), `Services/Licencias/LicenciaService.cs` (rechaza `plataforma`), `Services/Organizacion/{PermisosOrganizacion, ClienteCarteraService}.cs`, `DependencyInjection.cs`.

**Web**
- Nuevos: `Controllers/ReglasController.cs`, `Helpers/ReglasTextos.cs` (rótulos llanos D-M3-8..12 y fila JSON), `Models/ReglasViewModels.cs`, vistas `Reglas/{Index, _Listado, _ListadoScript, Create, Edit, _Form, _ScriptFormRegla, Detalle, _ScriptEstadoRegla, _CardReglasDestino}`, `Shared/_ReglasEfectivas`, `Agentes/_VistaPreviaReglas`, `Tareas/_ReglasAplicadas`, `Clientes/Reglas`.
- Modificados: `Controllers/{AgentesController (cliente + vista previa AJAX), TareasController (filtro Cliente), ClientesController (Reglas, ListarReglas, Regla; rubros sin plataforma), CarteraController (card), AreasController (card)}`, `Models/AgentesViewModels.cs`, vistas `Agentes/Ejecutar` (rediseñada), `Tareas/{Index, Detalle}`, `Cartera/Detalle`, `Areas/Edit`, `Clientes/Details` (botón Reglas), `Nucleo/Rubro` (rótulo de tipo), `Shared/_Layout` (ítem Reglas para miembros), `appsettings.json` (sección `Reglas`).

**Núcleo**: `nucleo/plataforma/plataforma.yml` + `nucleo/plataforma/reglas/{01-no-inventar-datos, 02-no-revelar-instrucciones, 03-pedir-precisiones}.md`.

**Tests**: nuevos `ReglasTests.cs` (5), `ConstructorContextoTests.cs` (8), `Infra/EntornoReglas.cs` (entorno Estudio Pérez + `ModeloGuionado` compartido); `MotorAgentesTests.cs` ajustado a `Sistema`.

**Docs del repo**: `docs/diseno-organizacion-roles-reglas.md` (M3 ✅).

### Decisiones de implementacion M3 (ambigüedades resueltas)
- **DI-M3-1 Solicitud por versión:** `SolicitudContexto` recibe `AgenteVersionId` (no el artefacto): de la versión publicada se derivan artefacto y rubro, y la tarea queda anclada a esa versión.
- **DI-M3-2 Render solo desde inmutables:** el render usa versiones del núcleo, `ReglaEvento` y la propia instantánea (que guarda los nombres de área y cliente del momento). Renombrar un área o un cliente no rompe el hash. Las instrucciones del rubro también quedan fijadas por id (antes se releían en cada ejecución).
- **DI-M3-3 Hash:** SHA-256 de `formato:1` + por bloque `|bloque|` + flag de caché + texto. `ArmarAsync` devuelve null si falta una versión o evento, si un evento no corresponde a su regla o si cambió `FormatoVersion` → la tarea queda Fallida sin llamar al modelo.
- **DI-M3-4 Escape:** `& < > "` en título, etiquetas, texto y nombres de área/cliente de la organización. El contenido del núcleo no se escapa (lo escribe Olvidata y puede traer marcado propio).
- **DI-M3-5 Precedencia:** declaración fija en B1 (arquitectura aprobada) con los rótulos de D-M3-9 y la aclaración de que las reglas nunca dan permisos y que el texto de archivos y herramientas no es instrucción.
- **DI-M3-6 "No se aplica" derivado:** regla activa cuya área o cliente se dio de baja o cuyo autor está bloqueado (no toca `Activa`). Activar exige destino vigente.
- **DI-M3-7 Largo:** el límite suma solo el texto (no el título) normalizado (`\r\n` → `\n`). El ViewModel no valida el largo del texto: lo valida el service con el mensaje del diseño, para no contar doble los saltos de línea del navegador.
- **DI-M3-8 Versiones:** cambiar etiquetas también versiona (el historial del diseño las lista). Activar/desactivar deja evento pero no incrementa `VersionActual` (D-M3-3), así que no invalida una edición abierta.
- **DI-M3-9 Mismo tema (P4):** reglas activas visibles con etiqueta en común y `NivelRegla` menor (más autoridad). Área: la del destino si es regla de área, si no la del usuario. Cliente: el mismo. Agente: el mismo si se eligió. Preferencias: nunca. Se filtra en memoria (volumen acotado por límites).
- **DI-M3-10 Staff (D-M3-6):** `Clientes/Reglas/{id}` con pestañas De la empresa · De las áreas · Por agente · De clientes · De miembros (sin "Mis preferencias"), y detalle `Clientes/Regla/{id}?reglaId=` reutilizando `Reglas/_Listado` y `Reglas/Detalle`. Las URLs usan el marcador `__ID__`.
- **DI-M3-11 Pestañas:** "De mi área" solo si el Empleado tiene área. Última pestaña en Session `Reglas_Pestana`; filtros por pestaña `Reglas_<Pestaña>_*` (staff: `ReglasStaff<tenant>_<Pestaña>_*`). "Ver todas" desde Cartera/Áreas fija el filtro de cliente o área.
- **DI-M3-12 Rótulos en servidor:** la grilla recibe rótulos ya resueltos (`ReglasTextos.Fila`). La búsqueda global también matchea rótulos visibles (siempre, salvo que se indique otra cosa, procedimiento, inactiva), el destino por nombre, el autor, la versión y la fecha.
- **DI-M3-13 Rubro `plataforma`:** excluido de `ListarRubrosAsync` y de los rubros disponibles del backoffice, y rechazado por `LicenciaService.CrearAsync`. `reglas_plataforma` en otro rubro → advertencia y se ignora.
- **DI-M3-14 Compatibilidad:** las tareas M1/M2 (5 en dev) no tienen instantánea: el motor usa el armado anterior en un bloque cacheado y su detalle no muestra reglas. Una instantánea ilegible en el detalle se muestra sin reglas; en el motor, Fallida.
- **DI-M3-15 Edición:** alcance y destinos se toman siempre de la regla guardada, no del formulario (D-M3-1). Crear con un alcance no permitido por URL → 403.
- **DI-M3-16 Filtros de consulta:** `IgnoreQueryFilters([FiltroSoftDelete])` en consultas raíz separadas para nombres de destinos dados de baja (nunca dentro de joins o subconsultas, porque aplica a toda la consulta). `[FiltroTenant]` solo en consultas de staff con `TenantId` explícito.
- **DI-M3-17 Combo de clientes:** `IClienteCarteraService.ListarComboAsync` para la nueva tarea. `AgentesController` sigue con `[Authorize]`: para staff, la vista previa muestra el mensaje del service.

### Migraciones EF generadas M3
- `20260914182556_ReglasM3` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-14** con `dotnet ef database update`. `MySql.EntityFrameworkCore 10.0.9` generó bien el `CHECK` en línea (no hizo falta `migrationBuilder.Sql`, a diferencia de las columnas generadas de M2). Tablas `Reglas` y `ReglaEventos`; columnas `TareasAgente.ClienteCarteraId/ReglasAplicadasJson (longtext)/HashContexto`; FK todas `RESTRICT`; índices por tenant.
- Verificado por SQL en transacción revertida (`scratchpad/verif-reglasm3.sql`): 6 alcances válidos OK; 7 combinaciones inválidas → ERROR 3819 `CK_Reglas_Destino`; `SUM(CHAR_LENGTH)` = 11 caracteres (14 bytes) con tildes; `LIKE '%,tono,%'` no matchea `,tonos,`; evento de regla inexistente → 1452; borrado físico de área con reglas → 1451; 0 restos.
- Verificado EF → MySQL real (`scratchpad/verif-m3`, una transacción revertida): 42 pasos OK. Incluye crear/editar/conflicto/activar, los 13 listados con filtros, estados y búsqueda global, uso de límite, mismo tema, opciones, cards, vista previa, tarea con instantánea y hash, filtro de tareas por cliente, baja de cliente → "No se aplica", vistas de staff y catálogo sin `plataforma`. Sin errores de type mapping (MH-001) y 0 restos.
- Import de plataforma en dev: `importar nucleo/plataforma/plataforma.yml` → 3 artefactos `ReglaPlataforma` v1 en **Borrador** (#56, #57, #58). **No publicados**: publicar requiere `evaluar <id> --aprobada "detalle"` + `publicar <id>`. Hasta entonces ninguna regla de plataforma entra en el contexto.
- Impacto: tablas nuevas vacías y columnas nulas en tareas existentes; sin transformación de datos.

### Evidencia de build y tests M3
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`).
- `dotnet test tests/OlvidataAgentes.Tests`: **61 OK / 0 fallidos** (48 existentes + 13 nuevos).

### Riesgos residuales M3
- RT-M3-01 caché: B2 puede quedar bajo el mínimo cacheable (sin error, sin ahorro). Medir `cache_read` en la primera corrida real.
- RT-M3-02 carrera en límites: aceptada.
- RT-M3-03 inmutabilidad de `ReglaEvento`/`ArtefactoVersion`: la garantiza el código (ningún service los edita), no la base. Una alteración por SQL deja la tarea Fallida (test).
- R-M3-01 inyección: mitigada (escape + plataforma y precedencia en B1 + reglas sin permisos), no garantizada. Prueba real opcional con OK de costo de Joaquín.
- R-M3-04 datos sensibles: aviso en el formulario. El staff lee las reglas (P9): mencionarlo en términos de uso.
- Reglas de plataforma en Borrador en dev: falta la evaluación y publicación de Joaquín.
- Si el cliente elegido no tiene reglas, el prompt no nombra al cliente (el diseño no lo pide); queda como mejora menor.
- Verificación visual pendiente (QA): Select2 con tags, plegables, card de vista previa en mobile, tema oscuro de pestañas y badges.

### Proximos pasos pendientes M3
- QA etapa 6 (guía en `trazabilidad.md`).
- Joaquín: evaluar y publicar las 3 reglas de plataforma.
- Deuda preexistente vista, fuera de alcance: `Admin licencia-crear` usa `slugs.Contains(r.Slug)` sobre `string[]` (patrón MH-001; no se ejercita en tests); herramienta `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9.

---

# M2 — Organización del portal

**M2 — Organización del portal.** Estado: **implementada 2026-09-14, pendiente de QA (etapa 6)**. Entrada: `2-disenador-funcional.md` y `3-arquitecto-mvc.md` aprobados; `4-presupuestador.md` omitido por decisión de Joaquín (gate dispensado). Repo: `C:\Sistemas\Olvidata Agentes Multi-rubro`.

### Escaneo de reutilizacion
| Fuente | Qué se tomó | Grado |
|---|---|---|
| la-platense `FerreteriaLaPlatense.Web/wwwroot/css/site.css` (Sistema de formularios) | `.ov-page-head`, `.ov-form-page`, `.ov-form-actions`, `.ov-required`, `.ov-field-hint`, `.ov-detail-grid` → `OlvidataAgentes.Web/wwwroot/css/site.css` | Literal |
| la-platense `wwwroot/js/site.js` | Auto-init global de Select2 (`ovAplicarSelect2`, excluye `.swal2-select`) + foco en `select2:open` + `window.Filtros` | Literal adaptado |
| la-platense `Helpers/FiltrosSessionHelper.cs`, `Helpers/DataTableRequestHelper.cs`, `ProductosController.Listar/Delete`, `Views/Productos/Index.cshtml` (PAT-015/016) | `Web/Helpers/FiltrosSesion.cs` (+ `Procesar`, `Fijar`), `Web/Helpers/DataTableRequestHelper.cs` (+ rangos), bajas AJAX `{success,message}` con `ajax.reload(null,false)` | Literal adaptado |
| delicias-naturales (`C:\Sistemas\delicias-naturales`, .NET Framework) | Patrón de búsqueda global por fecha/importe con `extraIds` → `Application/Helpers/BusquedaHelper.cs` | Patrón |
| Template propio (M1) | `TareaAgente.Version` + reintento de `ServicioTareas.CancelarAsync` → `Tenant.VersionMiembros` en `MiembroService`; `UsersController` como base de `MiembrosController` | Literal adaptado |
| PAT-027 (catálogo) | Completado con rutas reales de código, `pendiente_verificar: false` | Confirmado |

### Archivos y capas modificadas
**Domain**
- Nuevos: `Enums/EnumsOrganizacion.cs` (`RolOrganizacion`, `TipoIdentificacion`), `Entities/Area.cs`, `Entities/ClienteCartera.cs`.
- Modificados: `Entities/ApplicationUser.cs` (+`RolOrganizacion?`, `AreaId?`, `Area`), `Entities/Tenant.cs` (+`VersionMiembros`).

**Application**
- Nuevos: `Interfaces/IContextoUsuario.cs`, `IResolvedorSesion.cs`, `IPermisosOrganizacion.cs`, `IAreaService.cs`, `IMiembroService.cs`, `IClienteCarteraService.cs`; `DTOs/OrganizacionDtos.cs`; `Helpers/IdentificacionHelper.cs` (CUIT módulo 11, DNI, normalizar, formatear, validar); `Helpers/BusquedaHelper.cs`.
- Modificados: `DTOs/ServiceResult.cs` (+`TipoError` Validacion/NoEncontrado/SinPermiso, `CreateNotFound`/`CreateForbidden`, default compatible); `Motor/IMotorAgentes.cs` (`TareaFiltros`, `TareaListItemDto`, `TareaOpcionesFiltroDto`, `TareaResumenDto.PedidaPor`, `IServicioTareas.ListarAsync(DataTableRequest, TareaFiltros)` + `OpcionesFiltroAsync`).

**Infrastructure**
- Nuevos: `Services/Organizacion/{ContextoUsuario, ResolvedorSesion, PermisosOrganizacion, AreaService, MiembroService, ClienteCarteraService}.cs`; `Data/Configurations/OrganizacionConfigurations.cs`; migración `Data/Migrations/20260914150042_OrganizacionM2.cs` (+ Designer y snapshot).
- Modificados: `Data/AppDbContext.cs` (DbSets `Areas`, `ClientesCartera`; audit trail sin `PasswordHash`/`SecurityStamp`/`ConcurrencyStamp`/`VersionMiembros`); `Data/Configurations/ApplicationUserConfiguration.cs` (rol, FK área SetNull, índice, check constraint); `AgentesConfigurations.cs` (`VersionMiembros` concurrency token); `Services/Motor/ServicioTareas.cs` (consulta base `Visibles()` por rol en listar/detalle/existe/cancelar/opciones, listado paginado con filtros y `PedidaPor`); `DependencyInjection.cs` (`AddMemoryCache`, `AddIdentityCore<ApplicationUser>().AddRoles().AddEntityFrameworkStores`, servicios M2).

**Web**
- Nuevos: `Middleware/SesionOrganizacionMiddleware.cs` (reemplaza `TenantMiddleware`); `Authorization/PermisoOrganizacion.cs` (requirement + handler scoped); `Helpers/{FiltrosSesion, DataTableRequestHelper, RespuestasServicio}.cs`; `Models/OrganizacionViewModels.cs`; `Controllers/{AreasController, MiembrosController, CarteraController}.cs`; vistas `Areas/{Index, Create, Edit, _Form, _ScriptBajaArea}`, `Miembros/{Index, Edit}`, `Cartera/{Index, Create, Edit, Detalle, _Form, _ScriptBajaCliente}`.
- Eliminados: `Middleware/TenantMiddleware.cs`, `Services/TenantClaimsPrincipalFactory.cs`, `Services/TenantDesdeUsuario.cs`.
- Modificados: `Program.cs` (sin claims factory; policies `RequireMiembro`/`RequireDirector`; middleware entre `UseAuthentication` y `UseAuthorization`); `Hubs/TareasHub.cs` (usa `IResolvedorSesion`); `Controllers/ClientesController.cs` (textos D-1, `CrearMiembro` [RequireSuperUsuario], detalle vía services); `UsersController.cs` (solo staff, D-4); `TareasController.cs` (`Index` + `Listar` DataTables, 404 en cancelar ajena); `AccountController.cs` (perfil con organización/rol/área); `Models/AgentesViewModels.cs` (`ClienteDetalleViewModel` con DTOs, se elimina `UsuarioClienteCrearViewModel`); `Models/PerfilViewModels.cs`; vistas `Shared/_Layout` (menú por rol, "Organizaciones y licencias"), `_ViewImports`, `Clientes/{Index, Create, Details}`, `Tareas/Index`, `Account/Perfil`; `wwwroot/css/site.css`, `wwwroot/js/site.js`.

**Tests**
- Nuevo: `tests/OlvidataAgentes.Tests/OrganizacionTests.cs` (13 tests).
- Modificados: `Infra/TestServicios.cs` (`ScopeMiembro`, `ScopeStaff`), `MotorAgentesTests.cs` (2 tests pasan a scope de miembro; firma nueva de `ListarAsync`).

**Docs del repo**: `docs/arquitectura.md` (§2 y §3: middleware y resolvedor), `docs/diseno-organizacion-roles-reglas.md` (rol resuelto por request, M2 ✅).

### Decisiones de implementacion (ambigüedades resueltas)
- **DI-1 SecurityStamp:** se rota solo al **bloquear**. Cambio de rol/área: `Invalidar` + TTL 60 s ya cumplen RF-11 en todas las instancias; rotar el stamp en esos casos obligaría al miembro a volver a loguearse a los 5 min sin motivo.
- **DI-2 Columnas generadas:** `MySql.EntityFrameworkCore 10.0.9` ignora `stored: true` (emite `AS (...) NULL` = VIRTUAL). Se escriben con `migrationBuilder.Sql(... STORED)` (RT-02). El modelo EF las mantiene como `HasComputedColumnSql` (shadow).
- **DI-3 Migración:** `DROP INDEX IX_AspNetUsers_TenantId` movido después de crear el índice compuesto (MySQL 1553 por la FK); `UPDATE ... RolOrganizacion = 1` antes del check (P1). `Down` con orden inverso.
- **DI-4 Identity core en Infrastructure:** `MiembroService` usa `UserManager`; se registra `AddIdentityCore` en `AddInfrastructure` (registros TryAdd; el portal suma `AddIdentity` encima). MCP/Admin compilan y el test MCP real sigue verde.
- **DI-5 Tareas:** DTO de grilla propio (`TareaListItemDto`, fecha ya en hora argentina) y `OpcionesFiltroAsync` para los combos Agente / Pedida por calculados sobre tareas visibles (evita `List<string>.Contains`, MH-001). La columna Tokens se reemplazó por Costo (P-09). Filtro N° = número exacto.
- **DI-6 Staff en Tareas:** `PuedeVerTodasLasTareas` incluye staff, así que el staff también ve la columna "Pedida por".
- **DI-7 Unicidades:** nombre de área comparado sin distinguir mayúsculas (igual que la colación de MySQL); identificación única por (tipo, número), el mismo número con otro tipo se permite (igual que la columna generada).
- **DI-8 Filtrado:** Áreas y Miembros (decenas por organización) filtran en memoria; Cartera y Tareas en SQL con `EF.Functions.Like` + `extraIds` para fecha/identificación/número/importe.
- **DI-9 Contraseña inicial:** se usa la política vigente de Identity (6 caracteres, mayúscula, minúscula, número) con errores traducidos; se eliminó el mínimo de 8 del ViewModel viejo.
- **DI-10 AJAX sin permiso:** si falla una policy (ej. Empleado → `/Areas/DarDeBaja`), la cookie de Identity responde 403 sin cuerpo JSON; el 403 con `{success:false,message}` sale cuando decide el service (Empleado → `/Cartera/DarDeBaja`).
- **DI-11 Usuarios (SuperUsuario):** `CanManageUser` excluye usuarios con organización (Details/Edit/ToggleEstado → 403).

### Migraciones EF generadas
- `20260914150042_OrganizacionM2` — **aplicada en `olvidata_agentes_dev` (MySQL 8.0.29) el 2026-09-14**. Verificado por SQL: `NombreVigente` y `IdentificacionVigente` = `STORED GENERATED`; `CK_AspNetUsers_RolOrganizacion` activo; índices únicos `IX_Areas_TenantId_NombreVigente` e `IX_ClientesCartera_TenantId_IdentificacionVigente`. Prueba en transacción revertida: nombre de área repetido → 1062; tras baja lógica el nombre se libera; identificación repetida → 1062; varias sin identificación OK; tenant sin rol y staff con rol → 3819; miembro válido OK; sin restos.
- Impacto: columnas nuevas nulas en `AspNetUsers`, `Tenants.VersionMiembros` default 0, tablas nuevas; usuarios de organización existentes pasan a Director (solo base de desarrollo).

### Evidencia de build y tests
- `dotnet build OlvidataAgentes.slnx`: 0 errores, 1 advertencia preexistente (CS0114 `HomeController.StatusCode`, no tocado).
- `dotnet test tests/OlvidataAgentes.Tests`: **48 OK / 0 fallidos** (35 existentes + 13 de `OrganizacionTests`).

### Riesgos residuales
- RT-01 caché de sesión por instancia (límite aceptado; con varias instancias el cambio llega al vencer el TTL de 60 s; el bloqueo además por SecurityStamp a los 5 min).
- DI-10: policy fallida en AJAX devuelve 403 sin JSON (el JS muestra el mensaje genérico).
- Alta del primer miembro sin token de concurrencia (solo la hace el SuperUsuario; riesgo bajo).
- Verificación visual pendiente (regla 25): Select2 global con foco, daterangepicker, formularios en escritorio/mobile, tema oscuro de las clases portadas.
- La unicidad y el check solo se prueban en MySQL real (InMemory no los aplica).

### Proximos pasos pendientes
- QA etapa 6 (guía en la salida de esta etapa y en `trazabilidad.md`).
- Deuda fuera de alcance: el staff no tiene UI para cambiar nombre/email/rol/estado de un miembro (P-08 es solo lectura + alta); `Users/*` y `Clientes/Index` del template conservan textos sin tildes y tabla no DataTables; el resolvedor no mira `Tenant.Estado` (organización suspendida); herramienta `dotnet-ef` 10.0.2 más vieja que el runtime 10.0.9.

## Historial de ajustes
- 2026-09-21: **Anatomía de agentes (catálogo + ficha), 4 etapas con commit local cada una.** Diseño `docs/diseno-anatomia-agentes.md` aprobado por Joaquín con D1 (bloque `ficha:`), D2 (contexto real solo SuperUsuario y auditado) y D3 (título + `resumen_publico`).
  - **E1 (16480a3):** `IResolvedorHerramientas` extraído de `ProcesadorTareas` sin cambio de comportamiento (mismo conjunto y orden; `Todas` anota familia, condición y si se ofrece) + `DescripcionesHerramientas` (rótulo y "qué hace" llanos) con test de cobertura sobre el registro.
  - **E2 (6614cc9):** `Agentes/Ficha` y `Agentes/Detalle` en 7 pestañas, `IFichaAgenteService` (DTO del cliente sin campo para texto del núcleo), catálogo con "Ver ficha", etapas, coordinador primero. Herramientas en lenguaje llano también en detalle y formulario. Portal real en tests con `WebApplicationFactory` y centinelas en todas las URLs de cliente (CP-AA-01).
  - **E3 (437133c):** `Nucleo/Agente` y `Nucleo/ContextoArmado` (staff), `IAnatomiaAgenteService` con rol re-verificado adentro; B1 sin organización byte a byte el de una tarea; con organización el mismo hash que una tarea creada ahora, solo SuperUsuario y con fila en `AuditLog`.
  - **E4 (e573151):** importador lee `ficha:`, `resumen_publico` y todas las etapas del manifiesto. **Migración `AnatomiaAgentes`** (`Artefactos.FichaJson` longtext, `Artefactos.ResumenPublico` varchar 500, tabla `ArtefactoEtapas`), aplicada en `olvidata_agentes_dev`; reimportados contable y plataforma contra MySQL dev: **0 versiones nuevas**. Fichas escritas para los 10 agentes de contable y los 2 de plataforma; resumen público para las 3 reglas de plataforma.
  - DI-AA-1: la ficha y el resumen viven en `Artefacto`, fuera del cuerpo versionado: no cambian el hash de versión ni los goldens. DI-AA-2: la colección de tests del portal corre sin paralelo y el csproj de tests excluye los appsettings del portal (su `Production.json` rompía `ServidorLocalDePrueba` con 400 "Invalid Hostname"). DI-AA-3: CSS `ov-capa*` en `site.css` (donde viven las clases de M4), no en `olvidata-theme.css`.
  - Evidencia (sin pipe): línea base 653/654 (el flaky conocido de `LectorDocumentosTests`); E1 659/659, E2 671/671, E3 680/680, **E4 685/685**. Goldens intactos. Sin llamadas a Anthropic, sin deploy.
  - Pendiente: QA funcional y visual (CP-AA-12: 390 px y tema oscuro; el MCP de Playwright no conectó). En producción: aplicar la migración y reimportar contable y plataforma para cargar fichas, resúmenes y etapas.
- 2026-09-21: **PA-05 — backoffice del SuperUsuario.** Editar organización (sin slug), pausar/reactivar/dar de baja con confirmación que cuenta lo afectado, extender licencias, editar miembros (nombre, email, rol, área, bloqueo) y generar contraseña de una sola vez, todo con `RequireSuperUsuario` y verificación en el service. Una organización no activa **frena al motor** en tres puntos (reclamo, bucle antes de cada llamada, reclamo de programaciones) sin cancelar nada. Cambio deliberado en programaciones de empresas suspendidas (DI-PA05-3). Sin migración, 641/641, goldens intactos. Decisiones DI-PA05-1..11.
- 2026-09-19: **Fines de línea fuera del hash del contexto (cierra el hallazgo abierto de la entrada de abajo).** El prompt de sistema salía con los saltos mezclados: las declaraciones `<precedencia>` de `ConstructorContexto.cs` son literales crudos (`"""`) y el compilador de C# conserva el fin de línea **del archivo fuente**, mientras todo el resto del render usa `\n`. Confirmado que era peor de lo anotado: `git ls-files --eol` da `i/lf w/crlf`, o sea que **el índice de git ya guarda LF y el working tree CRLF** — un build desde CI, desde Linux o desde un clon con `core.autocrlf=false` ya producía otro hash que el de esta máquina. Se normalizó ahora, que es el momento barato (nada desplegado; las tareas de dev y demo son descartables).
  - **Dónde se arregló: en `BloqueSistema` (`src/OlvidataAgentes.Application/Motor/ModeloConversacion.cs`), no en los literales.** El record normaliza a LF al construirse (`\r\n` y `\r` sueltos) y expone `Texto` de **solo lectura sobre un campo privado**: no hay setter, no hay `with`, no hay forma de construir un bloque con CRLF. Se eligió el tipo y no cada literal porque el texto del bloque es exactamente lo que entra a `CalcularHash`, y así queda cubierto todo constructor presente y futuro — los 4 formatos, `RevisorAutomatico` (que también arma su prompt con un literal crudo) y `ProcesadorTareas`. **No puede volver a romperse por una herramienta de formateo**: `dotnet format`, "normalizar saltos de línea" del editor o un `core.autocrlf` distinto ya no tienen por dónde llegar al hash, y el arreglo no depende de que nadie se acuerde de nada. Encaja con el patrón que el repo ya usa en las **entradas** (`ReglaService`, `AgenteOrganizacionService`, `ImportadorRubro` ya normalizan al guardar); esto es el último filtro en la **salida**.
  - **DI-CRLF-1:** no se tocó `ConstructorContexto.cs` (queda sin cambios, byte a byte) ni se agregó una regla `eol` al `.gitattributes` para los `.cs`: el arreglo es de código, no de configuración de checkout, así que vale también para quien clone con otra configuración.
  - **Los 5 goldens recalculados, y el diff se lee claro: los `.txt` no cambiaron ni un byte.** Regenerados con `OLVIDATA_GOLDEN_REGENERAR=1`, `git status` de `tests/OlvidataAgentes.Tests/Goldens/` quedó vacío. Los 5 tests fallaron **solo en `VerificarHash`** (nunca en `VerificarTexto`), que es la prueba de que el único cambio son los saltos de línea. Hashes nuevos en `Infra/Golden.cs`: formato-1-cm-panaderia `782c9568…`→`5117f901…`, formato-1-tasador-ferreteria `5553ed2e…`→`37218376…`, formato-2-agente-organizacion `3b2656b6…`→`a4094bf7…`, formato-3-configuracion `dde29dcb…`→`bea8f773…`, formato-4-asistente `10be2a34…`→`039c7e7b…`.
  - **La defensa se reemplazó por una que no tiene número que corregir.** `CasoGolden.VerificarFinDeLinea` contaba CRLF esperados (10/10/10/8/9) y el parámetro `SaltosCrLf` desapareció del record: ahora exige **cero retornos de carro** en el contexto armado y, si falla, dice en castellano que se arregla en `BloqueSistema` y nunca en el assert.
  - **Test permanente nuevo** `ConstructorContextoTests.El_fin_de_linea_del_texto_de_origen_no_entra_al_prompt_de_sistema_ni_al_hash`: mete el CRLF a propósito, así que **no depende de cómo esté guardado el checkout** (la guarda de cero CR sola no alcanzaría en un clon con LF). Comprueba el bloque (`\r\n`, `\r` y `\n` dan el mismo bloque y por lo tanto el mismo hash) y además de punta a punta, guardando el prompt del agente con CRLF en la base y verificando que el contexto armado y el hash no se mueven.
  - **Verificación pedida por Joaquín, hecha a mano sobre el archivo fuente:** `ConstructorContexto.cs` convertido a **LF puro** (`i/lf w/lf`, 0 bytes CR) → 32/32 verde; convertido a **CRLF** (515 CR / 515 LF) → 32/32 verde, con los mismos hashes. El archivo se restauró y `cmp` lo confirma idéntico al original. **El hash no se movió en ninguno de los dos casos.**
  - **Aceptado:** las tareas y conversaciones que ya existen en dev y demo dejan de reconstruir su hash y sus seguimientos fallan sin llamar al modelo. No se migró nada, por decisión.
  - Sin migración EF. Tres archivos tocados (`ModeloConversacion.cs`, `Infra/Golden.cs`, `ConstructorContextoTests.cs`); `Mcp` y `Cli` sin tocar. Sin commits.
  - **Evidencia medida sin pipe** (`dotnet test > archivo 2>&1`, leyendo el resumen impreso): línea base **Con error: 0, Superado: 600, Total: 600**; tras el cambio **Con error: 5** (los 5 goldens, solo por hash) sobre 601; final **Con error: 0, Superado: 601, Omitido: 0, Total: 601**. `dotnet build OlvidataAgentes.slnx`: 0 errores, **0 advertencias**.
- 2026-09-19: **Goldens de contexto: texto versionado + constantes recalculadas.** Diagnóstico confirmado: no había regresión del producto — el render nunca cambió y las 7 constantes `HashGolden*` (5 valores distintos, 2 duplicados literalmente entre `AgentesOrganizacionTests` y `M14GoldenYPantallasTests`) **nacieron mal y nunca coincidieron con ningún estado del repo**. Se verificó primero que el texto actual es *correcto* (orden de las 9 secciones, rótulos coherentes con lo que nombra `<precedencia>`, escapado de `&`/`<`/`>` en reglas e instrucciones de la empresa, y nada que no deba estar: sin instructivos, sin herramientas, sin búsqueda web, sin ids de tenant ni de usuario), y recién después se recalcularon los hashes desde el texto real.
  - **Lo principal: el texto ahora se versiona.** `tests/OlvidataAgentes.Tests/Goldens/*.txt` guarda el contexto renderizado de los 5 casos (formatos 1×2, 2, 3 y 4) con sus bloques y su marca de caché. El test **compara el texto y además el hash**, y **el texto primero**: al fallar deja el contexto nuevo en `<nombre>.actual.txt` y el mensaje trae el `git diff --no-index` listo para pegar. Verificado rompiendo el render a propósito: el diff muestra en castellano el rótulo que cambió, en vez de dos hexadecimales.
  - Todo centralizado en `tests/OlvidataAgentes.Tests/Infra/Golden.cs` (`Goldens` + `CasoGolden`), con el comentario de qué garantiza cada golden y qué hacer si falla. **Se eliminó la duplicación de constantes**, que es cómo `HashGoldenTasadorFerreteria` estuvo mal sin que se notara: el assert anterior fallaba primero y lo tapaba.
  - Regeneración explícita con `OLVIDATA_GOLDEN_REGENERAR=1` (reescribe los `.txt` y deja el hash en un `.hash.tmp`); en ese modo no se verifica nada, así que el verde que cuenta es el de la corrida siguiente sin la variable.
  - **Hallazgo — CERRADO el 2026-09-19** (ver la entrada de arriba: se normalizó en `BloqueSistema` y se recalcularon los 5 hashes). Lo que se había detectado: el hash depende de los **fines de línea de `ConstructorContexto.cs`**. Las declaraciones `<precedencia>` son literales crudos (`"""`) y el compilador de C# conserva el fin de línea del archivo fuente, que está en CRLF; todo el resto del render usa `
`. Un `dotnet format`, un "normalizar saltos" del editor o un clon con otro `core.autocrlf` cambia **los 5 hashes a la vez sin cambiar una letra del texto** — y es la explicación más probable de por qué las constantes nacieron mal. Queda cubierto por `CasoGolden.VerificarFinDeLinea`, que cuenta los CRLF y avisa en castellano. **Normalizar los literales a `
` volvería el hash independiente del checkout, pero cambia los 5 hashes y rompe la reconstrucción de las tareas ya guardadas: se deja a criterio de Joaquín.**
  - Sin migración EF. `Mcp` y `Cli` sin tocar. Sin commits. Los cambios sin commitear de M15 quedaron intactos.
  - **Evidencia medida sin pipe** (`dotnet test > archivo 2>&1` + `$?`): línea base **595 OK / 5 fallidos de 600** (los 5 goldens), resultado final **600/600, `EXITCODE_REAL=0`, 0 `[FAIL]`**.
- 2026-09-18: M15 ficha de rubro para el staff. Se enriqueció `Nucleo/Rubro` en vez de crear una pantalla nueva (evita dos pantallas casi iguales) y se absorbió la card duplicada de material de referencia. Nuevos `IFichaRubroService`/`FichaRubroService` y `NucleoTextos`; la lista de organizaciones cruza el filtro de tenant con `IgnoreQueryFilters([FiltroTenant])` justificado. Sin migración, solo lectura, 6 tests nuevos. Decisiones DI-M15-1..6. **Hallazgo: los 4 goldens de contexto ya fallaban en `e248922` (589/594), no es regresión de esta etapa.**
- 2026-09-14: Implementación de M2 Organización (Domain→Application→Infrastructure→Web), migración `OrganizacionM2` aplicada y verificada en MySQL dev, 13 tests nuevos (48/48 OK). Decisiones DI-1..DI-11. PAT-027 completado en el catálogo.
- 2026-09-14: Implementación de M3 Reglas por alcance: `Regla`/`ReglaEvento`, `ReglaService`, `ConstructorContexto` (3 bloques con caché, instantánea por ids + hash verificado en el motor), vista previa y reglas aplicadas, rubro técnico `plataforma` (3 reglas en Borrador en dev). Migración `ReglasM3` aplicada y verificada con SQL y EF contra MySQL real (transacciones revertidas). 13 tests nuevos (61/61 OK). Decisiones DI-M3-1..17. PAT-028 completado en el catálogo.
- 2026-09-14: Implementación de M3b Seguir conversando: ajustes del autor con re-apertura atómica, normalización de la conversación, pasos por turno, `CierreTurno`, caché en el último mensaje, detalle como conversación, reglas cambiadas, preferencias ajenas ocultas, listado con mensajes y última actividad, modelo simulado solo en Development. Migración `ConversacionM3b` aplicada y verificada con SQL y EF contra MySQL real (37 pasos, 0 restos). 22 tests nuevos (83/83 OK). Decisiones DI-M3b-1..13. PAT-029 completado en el catálogo.
- 2026-09-14: Implementación de M4 Agentes de la organización (sin revisión del Director): `AgenteOrganizacion`/`AgenteOrganizacionVersion`, `AgenteOrganizacionService`, catálogo unificado, formulario, detalle, duplicar/archivar/reactivar, tareas con formato de contexto 2 sin cambiar el hash de las existentes (test golden), herramientas por intersección, reglas por agente de la empresa, sugerencias de Olvidata, `incluido_siempre` + `sincronizar-rubros-incluidos`, vistas de staff. Migración `AgentesOrganizacionM4` aplicada y verificada con SQL y EF contra MySQL real (0 restos). 17 tests nuevos (100/100 OK). Decisiones DI-M4-1..21. PAT-030 completado en el catálogo.
- 2026-09-14: Implementación de M4b Agente configurador de reglas del Director: `TipoTarea.ConfiguracionReglas` con formato de contexto 3 propio (golden de formatos 2 y 3; 1 y 2 intactos), `ResolverUsuarioAsync` y re-verificación del autor, 9 herramientas de lectura/propuesta sin `SaveChanges`, `PropuestaRegla` con token y único por `ToolUseId`, `PropuestaReglaService` y `ReglaService` con origen de aplicación en el mismo guardado, lista de conversaciones, tarjetas con modal de cambio, editar y aplicar, filtro Tipo en Tareas, simulador con guion de herramientas, prompt borrador importado sin publicar (#65). Migración `ConfiguradorReglasM4b` aplicada y verificada con SQL y EF contra MySQL real (17 pasos, 0 restos). 13 tests nuevos (113/113 OK). Decisiones DI-M4b-1..19. PAT-032 completado en el catálogo.
- 2026-09-15: Implementación de M5 Workspace por cliente de cartera: `DocumentoCartera`/`DocumentoCarteraParte`/`AdjuntoMensajeTarea` (reemplazan `DocumentoCliente`), almacén en disco fuera de `wwwroot` con ids y GUID, validación por contenido (ZIP seguro, sin macros), extracción por partes con PdfPig/OpenXml/ClosedXML y topes, servicio con nombre único según la colación y reintento ante 1062, herramientas de solo lectura en tareas de trabajo con cliente, adjuntos en pedido y ajustes con nota en los mensajes (golden 1–3 intactos), chips y Ver pasos llano, pantallas y backoffice solo metadatos, simulador con guion de documentos, `documentos-limpiar`. Migración `WorkspaceClientesM5` aplicada y verificada con SQL (estructura y transacción revertida con utf8mb4) y EF contra MySQL real (47 pasos, 0 restos; detectó un orden no traducible corregido). 46 tests nuevos (159/159 OK). Decisiones DI-M5-1..19. PAT-033 completado con rutas reales y lecciones.
- 2026-09-15: Implementación de M6 Aprobaciones de acciones por rol y límites de gasto (continuación de una corrida cortada por límite de uso: se conservó el backend y se completaron Web, tests, migración y documentación). Límite mensual por organización (USD 100 por defecto) y por miembro con límite efectivo, consumo del mes argentino desde `PasosTarea`, verificación antes de cada llamada y en crear/configurar/ajustar, avisos únicos, pantalla Consumo por rol, columna en Miembros, card/consumo de staff y columnas en Uso; `AprobacionAccion` por `tool_use_id` con pedido + espera en un guardado, tarjeta y bandeja con contador, resolución con tokens y `Intentos = 0`, ejecución única con autor re-verificado, rechazo/vencimiento como error registrado, barrido en el worker, cancelación; demostraciones solo con el simulador en Development. Migración `AprobacionesYGastoM6` (se agregó el `UPDATE` del límite por defecto) aplicada, Down/Up y verificada por SQL y EF contra MySQL real (64 pasos, 0 restos). 26 tests nuevos (185/185 OK), golden 1–3 intactos. Decisiones DI-M6-1..15. PAT-034 y PAT-035 completados con rutas reales y lecciones.
- 2026-09-16: Implementación de M8 Evaluación automática de prompts: **extracción del render de `ConstructorContexto` a una función pura compartida por los 4 formatos y por `ArmarEvaluacionAsync`, byte a byte (4 goldens verdes, plan B no usado)**; casos de prueba como datos del repo (`evaluaciones:` en el manifiesto, `ConjuntoCasos`/`VersionConjuntoCasos`/`CasoEvaluacion` versionados por hash, con dos suites comunes en `plataforma`); `CorridaEvaluacion`/`ResultadoCaso` con único (corrida, caso, repetición), lease, token y barrido propio en `MotorAgentesWorker` (de a una, fuera de `MaxTareasSimultaneas`); ejecutor que **ofrece las herramientas y nunca las resuelve** (doble que lanza en `Obtener`), verifica los dos topes antes de cada llamada y guarda una unidad de trabajo por (caso, repetición); `VerificacionesTexto` puro + `RevisorAutomatico` con salidas estructuradas del SDK (verificadas en Anthropic 12.47.0: `MessageCreateParams.OutputConfig` / `JsonOutputFormat.Schema`) y validación estricta del texto, con control de cordura por corrida; comparación contra la publicada, resultado global, gate de publicación por `HashCasos` con excepción de SuperUsuario auditada, organización interna `olvidata-interno` y `CanalUso.Evaluacion`; 9 vistas y 11 acciones en Núcleo, 7 verbos `evaluacion-*` en Admin. Migración `EvaluacionAutomaticaM8` aplicada y verificada con SQL contra MySQL real (1062 reales en los dos únicos, `decimal(18,6)`, EXPLAIN del gasto del mes y del gate, siembra de la organización interna, Down y Up, 0 restos). 43 tests nuevos (287/287 OK). Decisiones DI-M8-1..12. PAT-040 y PAT-041 creados en el catálogo con rutas reales. Casos iniciales de plataforma importados en dev como **borrador para revisar** (PA-17); **ninguna corrida real ejecutada**.
