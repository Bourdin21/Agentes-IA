# Memoria - Implementador

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-09-25 (M21 ojos, segunda mitad: PDF escaneado)

## Definiciones vigentes

# M21 — Ojos, segunda mitad: el agente mira un PDF escaneado

Estado: **implementado 2026-09-25; pendiente de QA; 1 commit local `2acfa4f`, sin push y sin deploy (los hace el
orquestador)**. Repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `b551010` (M20). Entrada: análisis M21
(RF-M21-01..07, D-M21-a..d, CA-M21-01..05, R-M21-01/02, S-M21-01), el bloque M21 de `2-disenador-funcional.md` (la tabla
de «dónde se ve», D-M21-e y los cuatro riesgos de implementación) y el de `3-arquitecto-mvc.md` (mapa de componentes,
flujo punta a punta, R-T-04..06). Gate: definiciones 2 y 3 cerradas; presupuesto omitido (proyecto personal).

### Escaneo de reutilización
- **Otros proyectos: nada para traer.** Se confirmó lo del diseñador: `luciano-inmobiliaria/1-analista-funcional.md`
  §viabilidad documentó **esta misma vía técnica** (PDF nativo a Claude, sin pipeline de OCR) como respuesta a un cliente,
  pero nunca se implementó. Ningún otro proyecto del historial tiene visión sobre documentos.
- **Del propio repo, y es casi todo: M16 (ojos).** El camino entero ya estaba armado —`EstadoLecturaDocumento.SeMira`, la
  referencia en la base (nunca los bytes), la lectura del disco al armar la llamada, el tope por conversación y la guarda
  de cliente/tenant—, así que **lo único nuevo es que el archivo puede ser un PDF y que sale como bloque de documento**.
  No se duplicó una sola guarda: `ImagenesParaModelo` atiende los dos tipos con las mismas líneas.

### Qué se construyó
- **Application:** `Settings/DocumentosOptions.cs` (`MaxPaginasPdfParaMirar` 20, `MaxMbPdfParaMirar` 10,
  `MaxPdfsEnConversacion` 2, con el porqué verificado contra la doc de la API), `DTOs/DocumentosDtos.cs`
  (`SubidoSeMiraEscaneado`, `SubidoNoLegibleEscaneado`, `MotivoSeMiraEscaneado`, `MotivoEscaneadoLargo`,
  `MotivoEscaneadoPesado`, `PaginasDelEscaneado`, `Paginas`), `Motor/MensajesOjos.cs` (rótulo con páginas y las variantes
  de archivo), `Motor/IMotorAgentes.cs` (`ImagenParaMirar.EsPdf`), `Motor/ModeloConversacion.cs`
  (`BloqueImagenDocumento.EsPdf`, `BloqueImagenDatos.Paginas`), `Interfaces/IAlmacenDocumentos.cs`
  (`ResultadoLecturaDto.PaginasEscaneadas`), `Helpers/NombreDocumentoHelper.cs` (`TextoLectura` con tipo),
  `Helpers/MensajesPortalCliente.cs` (una palabra).
- **Infrastructure:** `Extractores/ExtractorPdf.cs` (la decisión de escaneado), `Documentos/ImagenesParaModelo.cs`
  (acepta PDF con su tope), `Motor/ProveedorModeloAnthropic.cs` (`MapearArchivoParaMirar` + `EsPdf`),
  `Motor/ProcesadorTareas.cs` (rehidratado con tope **por tipo**), `Documentos/HerramientasDocumentos.cs`
  (`documento_leer` sobre un escaneado, `LecturaParaAgente`, el paso «Miró …»), `Documentos/DocumentoCarteraService.cs`
  (mensaje de subida y el tipo en los DTO).
- **Web:** `Helpers/DocumentosTextos.cs` (tooltip), `Views/Documentos/Ver.cshtml` (el aviso del PDF escaneado, sin vista
  previa embebida) y tres claves en `appsettings.json`.
- **Tests:** `tests/OlvidataAgentes.Tests/OjosPdfTests.cs` (nuevo, 7 casos), 2 casos nuevos y 1 actualizado en
  `LectorDocumentosTests.cs`, 1 aserción de texto en `DocumentosTests.cs`.
- **Documentación del repo:** `docs/el-sistema-como-computadora.md` (la fila de Ojos, «Qué falta» y el bloque de M21) y
  `docs/manual-de-uso.md` (los estados al subir, el aviso de costo, el párrafo del escaneado y el «Qué no hace»).
- **Datos: ninguno. Sin entidades y sin migración.** `Mcp`, `Cli` y `distribuible/` sin tocar.

### Decisiones de implementación
- **DI-M21-A — El umbral es «cero caracteres», no el promedio.** El extractor ya tenía «menos de 20 caracteres por
  página → escaneado»; para **mirar** se exige que no se haya extraído **ni una letra** (RF-M21-01, D-M21-a). Un PDF con
  poco texto sigue por el camino barato, que cuesta como diez veces menos, y el sello OCR con dos palabras queda fuera de
  alcance a propósito (R-M21-02).
- **DI-M21-B — La cantidad de páginas viaja en `MotivoNoLegible`, la columna que ya existía.** Sin migración no hay dónde
  guardar un número, y las alternativas eran peores: `CantidadPartes` significa «partes de texto legible» (la ficha
  mostraría «12 partes» de un documento sin una sola letra) y volver a abrir el PDF para contar páginas es I/O en cada
  listado. `MensajesDocumentos.MotivoSeMiraEscaneado` es el único que escribe ese texto y `PaginasDelEscaneado` el único
  que lo lee, con un test de ida y vuelta.
- **DI-M21-C — El peso se decide al subir, además del guardarraíl del motor.** El tope de bytes del motor sigue
  existiendo, pero avisar recién en la tarea sería prometer algo que no se puede cumplir (D-M21-b). El extractor mira el
  largo del stream cuando se puede buscar y, si pasa, deja `NoLegible` con el motivo del peso.
- **DI-M21-D — `EsPdf` se agregó al final y con valor por defecto, y no se renombró nada.** `BloqueImagenDocumento`
  conserva su discriminador `imagen_documento` y `ImagenParaMirar` su nombre: hay filas en producción desde M16 cuyo JSON
  no tiene el campo y toma el default. Un test deserializa un JSON viejo de las dos formas (`ContenidoJson` e
  `ImagenesJson`) y verifica que sigue siendo una imagen.
- **DI-M21-E — El mapeo al SDK se extrajo a un método público (`MapearArchivoParaMirar`).** `MapearBloque` es privado y
  el proyecto de tests no ve los internos, así que R-T-05 («el tipo del SDK no está verificado») se cubre con un test que
  comprueba que un `application/pdf` sale como `BetaRequestDocumentBlock` y **no** como imagen. Es el mismo precedente que
  M16 usó con `MapearTipoImagen`. El tipo lo confirmó el compilador en el primer intento:
  `new BetaRequestDocumentBlock(new BetaRequestDocumentBlockSource(new BetaBase64PdfSource { Data = base64 }))`, sin
  `MediaType` (el del SDK ya es el del PDF).
- **DI-M21-F — Un arreglo chico fuera del alcance, a propósito.** `MensajesPortalCliente.LaMiraElAgente` decía «Tu estudio
  **la** puede ver», escrito cuando solo una imagen se miraba: con un PDF el portal del cliente se contradecía. Quedó
  neutro («lo puede ver»); el nombre del const se dejó como está para no tocar M18.

### Lo que el criterio decía distinto (resuelto a la vista, no en silencio)
- **RF-M21-06 y la tabla del diseñador no dicen lo mismo.** El requisito pide que el estado se lea «El agente lo mira
  (escaneado, N páginas)»; la tabla de diseño pide «El agente lo mira» + **tooltip** que nombre el escaneado. Se
  implementó el rótulo **«El agente lo mira (escaneado)»** y las páginas en el tooltip y en la ficha del documento: meter
  el número en el rótulo de la grilla pedía persistirlo como número, y eso pedía migración.
- **El «antes» del paso no era el que dice el diseño.** La tabla dice que el paso pasaba de «Miró «Frente.png»» a «Miró
  «Extracto marzo.pdf» (4 páginas)», pero M16 nunca escribió «Miró»: una imagen caía en el brazo de lectura del resumidor
  y el paso decía **«Leyó «Frente.png», parte 1»**. El brazo de «lo miró» se escribió acá y vale para los dos tipos de
  archivo (una imagen ahora también dice «Miró «Frente.png»»).
- **El tope de imágenes por conversación estaba mal documentado.** `docs/el-sistema-como-computadora.md` hablaba de
  `Memoria:MaxImagenesEnConversacion`; la clave vive en la sección `Documentos`. Quedó corregido de paso.
- **`MaxMbPdfParaMirar` = 10 MB puede quedar corto para un escaneado real, y eso lo dijo un archivo real, no una
  suposición.** Un PDF **solo de imágenes de 10 páginas** de un cliente mide **11,76 MB**: con el tope de RF-M21-01 queda
  «no puede leerlo» por peso, aunque **entra holgado en el tope de la API (32 MB)** y en el de páginas (10 ≤ 20). Se
  implementó el 10 que pide el criterio y **no se cambió por cuenta propia**, pero conviene decidirlo: subirlo a 20 MB es
  **una clave de `appsettings.json`**, sin código ni tests, y el costo lo sigue acotando el tope de páginas (lo que se paga
  son las páginas, no los megabytes). Queda para el gate de QA / Joaquín.

### Pruebas
- **`OjosPdfTests.cs` (7):** el camino entero (sube → «lo puede mirar (escaneado, 4 páginas)» → el agente lo pide → llega
  el archivo en base64 con `application/pdf`, el rótulo con las páginas, el bloque de documento del SDK, y en la base solo
  la referencia con `EsPdf`, sin el base64, más el paso «Miró «Extracto marzo.pdf» (4 páginas)»); el escaneado por encima
  del tope (mensaje de subida con el motivo exacto, `documento_leer` que falla diciéndolo, `ImagenesParaModelo` que
  devuelve null y la tarea **Completada**); el de otro cliente y el de otra organización; el **tope por tipo** con
  escaneados y fotos mezclados (R-T-04); el JSON viejo de M16 sin `esPdf`; el archivo que ya no está en disco contado en
  palabras con la tarea terminando bien; y los textos del portal y del modelo comparados entre sí.
- **`LectorDocumentosTests.cs`:** el PDF con texto sigue `Legible` con una parte por página (el camino barato intacto), el
  escaneado de 1 y de 4 páginas queda `SeMira` con el motivo en palabras, el que pasa el tope de páginas y el que pasa el
  de peso quedan `NoLegible` con su motivo, y el ida y vuelta de `PaginasDelEscaneado`.
- **Cada test nuevo verificado en rojo** antes de darlo por bueno: apagar la rama del extractor → **7 rojos**; contar el
  tope de la conversación junto (sin separar tipos) y mandar el PDF como bloque de imagen → **2 rojos**. Código
  restaurado antes de seguir.

### Evidencia
- `dotnet build OlvidataAgentes.slnx`: **0 Errores**, 2 advertencias (las dos preexistentes de xUnit en tests de M18).
- `dotnet test tests/OlvidataAgentes.Tests` **medido sin pipe** (`> archivo 2>&1` y el código de salida): línea base
  **985**; final **Con error: 0, Superado: 994, Omitido: 0, Total: 994** (+9), exit 0.
- **Los 5 goldens de contexto, sin un byte de cambio:** `git status` de `tests/OlvidataAgentes.Tests/Goldens/` vacío. Era
  lo esperado (R-T-06): M21 no toca el prompt de sistema.
- **Los tests de M16 (`OjosTests.cs`) quedaron verdes sin tocarlos:** no figuran en el commit. Ningún texto de imagen
  cambió una letra; las firmas de `MensajesOjos` crecieron con parámetros opcionales justamente para eso.
- **Dos tests ajenos sí cambiaron, con motivo:** `LectorDocumentosTests` afirmaba que un escaneado de una página es
  `NoLegible` (justo el comportamiento que M21 cambia) y `DocumentosTests` afirmaba el texto «El agente la mira» (que la
  tabla del diseñador manda cambiar por «lo mira»). Son las dos aserciones que el módulo viene a cambiar.
- **Verificado contra PDF REALES, no solo sintéticos** (18 archivos de clientes que ya están en esta máquina, leídos en
  el lugar y **sin copiar ninguno al repo**): los 5 extractos del Credicoop de `contadores-bma` y un extracto real de otro
  cliente **siguen `LegibleEnParte`** con su página 8 sin texto, o sea que **el camino barato no se movió en datos reales**;
  un PDF real de una página sin texto que estaba guardado como documento de la demo **pasó a `SeMira`** (antes no existía
  para la tarea); trece PDF con texto quedaron `Legible`, incluido un brochure de 9 páginas con apenas 1.943 caracteres,
  que es exactamente el borde de D-M21-a (tiene algo de texto → camino barato). El hallazgo está abajo.

### Lo que quedó afuera
- **El PDF mixto** (algunas páginas con texto y otras escaneadas) sigue `LegibleEnParte` y sus páginas sin texto no se
  miran: D-M21-a lo deja fuera y duplicaría los caminos.
- **Sin vista previa embebida del PDF** en la pantalla del documento (D-M21-e): pediría una acción nueva que sirva el
  binario `inline` y el navegador ya abre el PDF descargado. El botón Descargar alcanza.
- **`MaxImagenesPorLectura` sigue siendo de las imágenes:** una llamada a `documento_leer` trae un archivo, igual que en
  M16, así que no hizo falta un tope propio por lectura para los PDF.
- Sin push y sin deploy: los hace el orquestador después de QA.

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

## Historial de ajustes

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **M14** — 2 bloques (2026-09-17 a 2026-09-17) → [`5-implementador-M14.md`](historial/5-implementador-M14.md)
- **M07** — 2 bloques (2026-09-15 a 2026-09-16) → [`5-implementador-M07.md`](historial/5-implementador-M07.md)
- **M04** — 1 bloques (2026-09-14 a 2026-09-14) → [`5-implementador-M04.md`](historial/5-implementador-M04.md)
