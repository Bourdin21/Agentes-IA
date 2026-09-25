<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/5-implementador.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - M14 (2 bloques archivados)

- D-M14-8 + PA-37 (el configurador propone instructivos) y PA-38 (el visto, por persona)
- Correcciones de la QA de M14 (DEF-M14-1, 2, 4, 6, 7 y 12)

---

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
