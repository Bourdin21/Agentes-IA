<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/5-implementador.md el 2026-10-09 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - M29 (3 bloques archivados)

- M29 - Ronda de arreglos de QA: el chip del hilo y el mensaje de la subida (OLV-038, OLV-039, OLV-040)
- M29 frente B tanda B2 - El dueno del transitorio, la UI del destino y la purga (CIERRA M29)
- M29 frente B tanda B1 - El documento sin cliente: la migracion y la frontera del portal del cliente

---

# M29 - Ronda de arreglos de QA: el chip del hilo y el mensaje de la subida (OLV-038, OLV-039, OLV-040)

Estado: **implementado 2026-10-02; 1 commit local, sin push y sin deploy. SIN MIGRACION.** Repo
`C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `8fef7ae`. Entrada: los partes de **M29 lote 1 y lote 2** de
`6-qa.md` (OLV-038 major, OLV-039 y OLV-040 minor), D-02/D-03/D-04/RD-02 y «Textos que importan» de «Diseno M29»
(`2-disenador-funcional.md` linea 8), B-03b y B-07 de «Arquitectura M29» (`3-arquitecto-mvc.md` linea 8).
**Los tres defectos quedan "aplicado, pendiente de re-verificacion": el cierre lo declara QA en contexto nuevo.**

## Escaneo de reutilizacion

Los tres defectos son correcciones sobre codigo propio de M29 (commits `37b215b`, `ee7f198`, `8fef7ae`), no
funcionalidad nueva: el escaneo del catalogo no aplica. Lo que si se reuso, y es el punto del arreglo, es el camino de
guardar que **ya existia** para el compositor (`ovGuardarEnCliente` + `_ModalGuardarEnCliente` + `AsignarCliente`), en
vez de abrir un segundo camino para el hilo. Ningun patron nuevo para el catalogo.

## OLV-038 (major) - La accion que cierra el ciclo no existia despues de enviar

**Causa raiz:** el chip del compositor lo arma el JS con lo que devolvio la subida (`SinCliente`, `Version`); el chip del
hilo lo **rehace el servidor** en cada refresco y `AdjuntoMensajeDto` solo traia `(DocumentoId, Nombre, Disponible)`. La
superficie que **relee** el hilo no sabia lo que la que lo **escribe** si sabia — la misma clase de defecto que OLV-030.

**Arreglo, donde vale para las dos superficies:**

1. **El dato, una vez.** `AdjuntoMensajeDto` gana `SinCliente` y `Version`, y un predicado con nombre
   `SePuedeGuardar => SinCliente && Disponible`. `ServicioTareas` los proyecta en la misma consulta que ya traia nombre y
   vigencia (`ClienteCarteraId == null`, `VersionToken`): sin consulta nueva. Un documento que **no se encontro** nunca
   sale como transitorio — si no, el chip ofreceria guardar un archivo que quien mira no puede ver.
2. **La accion, un solo camino.** El chip del hilo (Razor) y el del compositor (JS) **marcan** el boton con
   `data-guardar-adjunto` / `data-adjunto-nombre` / `data-adjunto-version`, y lo atiende **un listener delegado en
   `document`** dentro de `documentos.js`. Delegado y no directo porque `refrescar()` reemplaza `cont.innerHTML` cada 10 s:
   un listener pegado al chip del hilo se perderia en el primer sondeo. Al guardarse, el camino (a) repinta la lista de
   la caja que tenga una propia —el compositor— y (b) emite `ov:adjunto-guardado`; `Detalle.cshtml` lo escucha y llama a
   `refrescar()`, asi que **el hilo lo vuelve a dibujar el servidor** en vez de parchear el DOM a mano.
3. **El boton y la accion, una sola condicion.** `TareaDetalleDto.HayAdjuntosParaGuardar` sale del **mismo**
   `SePuedeGuardar` con el que cada chip decide, y es lo que pone el modal en la pagina. Hizo falta porque
   `PuedeAdjuntar` (`esAutor && ...`) era la unica condicion que incluia el modal: en una conversacion donde no se puede
   adjuntar, el chip habria ofrecido una accion que abria **nada en silencio** — y es justo el hilo al que la purga le va
   a borrar el archivo. Para eso el modal se extrajo de `_ModalDocumentos` a `_ModalGuardarEnCliente` (nunca los dos a la
   vez: son los mismos ids).

**Lo que NO se toco, a proposito:** `Documentos/Ver` sigue sin ofrecer la accion. Lo manda **D-03** —«guardarlo en un
cliente vive en el chip, no en una pantalla aparte»—, asi que la hipotesis de `archivos_fix` de QA en ese punto se
descarto con la definicion, no por omision. Y `OpcionesParaAdjuntarAsync` sigue excluyendo los sin cliente (CA-02.4).

## OLV-039 (minor) - El chip del transitorio en el hilo no decia nada

Mismo dato del punto 1: con `SinCliente` en el DTO, el chip del hilo pasa a usar la **misma** maqueta y las **mismas**
clases que el del compositor (`ov-chip-adjunto--transitorio`, `__cuerpo`, `__destino`) y la **misma** leyenda, *«solo en
esta conversacion»*, sin cuenta regresiva ni fecha (D-04). Cambio de forma: el chip dejo de ser el `<a>` y pasa a ser un
`<span>` con el nombre como enlace adentro (`ov-chip-adjunto__nombre`), porque ahora tiene tres cosas; el hover se
reescribio con dos reglas nuevas y **solo tokens `--ov-*`**.

## OLV-040 (minor) - El mensaje mentiroso por la rama de ModelState

`DocumentosController.Subir` tenia las dos validaciones colapsadas en `if (!ModelState.IsValid || model.Archivo is null)`,
que traducia **todo** ModelState invalido al unico mensaje del ViewModel. Volver el parametro `int?` (B-04) cambio que
entradas rompen el binder, no el colapso. Ahora son dos guardas: sin archivo -> «Elegi un archivo.» (validacion); con
archivo y ModelState invalido -> «El cliente no existe.» con **404**, identico a lo que ya contestaba un `clienteId=0`.
Es correcto porque el ViewModel tiene **un solo campo** (el archivo): con el archivo presente, lo unico que puede romper
el ModelState es el otro parametro.

## Cambios por capa

| Capa | Archivo | Motivo |
|---|---|---|
| Application | `Motor/IMotorAgentes.cs` | `AdjuntoMensajeDto` + `SinCliente`, `Version`, `SePuedeGuardar`; `TareaDetalleDto.HayAdjuntosParaGuardar`. |
| Infrastructure | `Services/Motor/ServicioTareas.cs` | La consulta de documentos del detalle proyecta `ClienteCarteraId` y `VersionToken`. |
| Web (vistas) | `Views/Tareas/_Conversacion.cshtml` | El chip del hilo: clase del transitorio, leyenda y boton marcado. |
| Web (vistas) | `Views/Tareas/Detalle.cshtml` | Inclusion del modal por `HayAdjuntosParaGuardar` + escucha de `ov:adjunto-guardado`. |
| Web (vistas) | `Views/Shared/_ModalGuardarEnCliente.cshtml` (nuevo) y `_ModalDocumentos.cshtml` | El modal, extraido para poder incluirlo solo. |
| Web (front) | `wwwroot/js/documentos.js` | El unico camino de guardar, delegado en `document`. |
| Web (front) | `wwwroot/css/site.css` | `ov-chip-adjunto__nombre` (hover del enlace adentro del chip), solo tokens. |
| Web (controller) | `Controllers/DocumentosController.cs` | Las dos guardas de `Subir` separadas (OLV-040). |
| Tests | `tests/.../ChipDelTransitorioEnElHiloTests.cs` (nuevo) | Un test por defecto, los tres por HTTP sobre la pantalla real. |

**Migraciones EF: ninguna.** Ningun cambio de esquema: `SinCliente` se **deriva** de `ClienteCarteraId` y `Version` ya
existia como `VersionToken`.

## Inventario por lectores (MH-041, la regla nueva de QA)

Se cerro el inventario por la **lista de lectores** de la entidad, no por recorrido de pantallas.

**Chips de adjunto: 5 superficies humanas, 5 consistentes** (una era la rota).

1. `_AdjuntarEnConversacion` -> `#chipsConversacion` (arranque de las cuatro conversaciones de plataforma) - JS compartido.
2. `_CuadroSeguimiento` -> `#chipsSeguimiento` (compositor del ajuste, cableado en `Detalle.cshtml`) - JS compartido.
3. `_Conversacion` (el hilo) - **era la rota**: Razor, el unico renderizador que no pasaba por el JS. Arreglada.
4. `_VistaPreviaDocumentos` («esto es lo que el agente va a tener en cuenta») - no nombra el destino, y **no hace falta**:
   su rama solo corre con `Model.TieneCliente`, asi que nunca lista un transitorio. Consistente por construccion.
5. `Documentos/Ver` (ficha) - dice «Sin cliente (solo de esta conversacion)» por `MensajesDocumentos.SinClienteAsignado`,
   y por D-03 **no** ofrece la accion.

Y tres lectores que lo excluyen a proposito, verificados por QA: `OpcionesParaAdjuntarAsync` (modal elegir, CA-02.4),
`Documentos/Index`+`Listar` (grilla por cliente) y `PortalDocumentos` (siete caminos del portal del cliente).

**`TareaOrigenId`: 27 apariciones en `src/`, y solo 7 son del transitorio.** El hallazgo es que el nombre esta en **dos
entidades distintas** con dos significados: `DocumentoCartera.TareaOrigenId` (M29: de que conversacion es este archivo
transitorio; 7 lineas, todas en `DocumentoCarteraService` - la purga, la guarda B-07 y la adopcion del huerfano) y
`TareaAgente.TareaOrigenId` (M28: desde que tarea de trabajo se abrio esta configuracion; 19 lineas en 9 archivos -
`HerramientaTareaOrigenLeer`, tres controllers, tres ViewModels, tres vistas). Un grep crudo del nombre devuelve 27 hits
de los que **20 son historia ajena**: quien toque la columna del documento tiene que filtrar por entidad primero. Es la
misma forma del hallazgo de M28 (84 comparaciones donde se buscaban 7).

## Evidencia

- `dotnet build OlvidataAgentes.slnx` -> **Compilacion correcta, 0 errores** (15 advertencias, todas preexistentes:
  NU1902 de ImageSharp, NU1510 y tres de analizadores xUnit en tests viejos).
- `dotnet test tests/OlvidataAgentes.Tests` (sin pipe, leyendo el resumen completo) -> **Con error: 0, Superado: 1221,
  Omitido: 0, Total: 1221**. Linea base de la corrida: 1217. Los 4 nuevos son el test por defecto (OLV-040 es un
  `[Theory]` con los dos valores de la reproduccion de QA).
- **Cada test falla sin su arreglo, verificado por mutacion y revertido:** con `SinCliente: false` en `ServicioTareas`
  caen los dos del chip y **no** el de la subida; volviendo a colapsar la guarda de `Subir` caen los dos casos de la
  subida y **no** los del chip.
- Sin smoke test propio (regla del rol): la app no se levanto.

## Pruebas minimas para QA (re-verificacion)

1. **CA-03.1 / HU-04:** subir un archivo con el destino reversible en `/ChatLibre`, **enviar**, dejar que el agente lo
   lea, **reabrir** el hilo y guardar el transitorio desde el chip. Esperado: `.ov-chip-adjunto__accion` >= 1,
   `ClienteCarteraId` en base **sin volver a subir**, el blob movido de `_organizacion/` a la carpeta del cliente
   (B-03b) y el chip repintado con el nombre del cliente **sin recargar la pagina**.
2. **Duplicado y cuota contra ESE cliente** al guardar desde el hilo (RD-04: el archivo queda transitorio si falla).
3. **El negativo:** un adjunto que ya tiene cliente **no** ofrece la accion, en el mismo hilo.
4. **RD-02 / D-04 en el hilo:** `getComputedStyle` del chip del transitorio distinto del chip con cliente, en claro y en
   oscuro, con la leyenda «solo en esta conversacion» y **sin** fecha ni cuenta regresiva.
5. **El modal, donde no se puede adjuntar:** un miembro que **no** es el autor abriendo el hilo — el chip ofrece y el
   modal esta (es la rama nueva de `Detalle.cshtml`, la que los tests no cubren).
6. **CA-02.1:** `POST /Documentos/Subir` con archivo y `clienteId` = `abc`, `../../otro`, vacio y uno valido.
7. **CA-02.4 y B-07 sin romper:** el transitorio sigue sin aparecer en ningun listado, y un id de otra conversacion
   sigue sin adjuntarse.
8. **Regresion del sondeo:** con el hilo refrescandose (10 s), tocar la accion una sola vez abre el modal **una** vez.

## Riesgos y supuestos

- **Bajo - el refresco y el modal.** `ov:adjunto-guardado` dispara `refrescar()`, que reemplaza el hilo entero. Si el
  modal quedara abierto al momento del refresco no se rompe (vive fuera de `#conversacion`), pero es lo que mas vale
  mirar a mano.
- **Bajo - el chip dejo de ser un `<a>`.** El enlace al documento ahora es el nombre; el resto del chip no es clickeable.
  Es lo que pide D-03 (la accion vive en el chip) y lo que ya hacia el compositor.
- **Supuesto declarado:** con el archivo presente, el unico ModelState invalido posible en `Subir` es el `clienteId`.
  Vale porque `SubirDocumentoViewModel` tiene un solo campo; si manana se le agrega otro, la guarda hay que partir en tres.

## Checklist de salida para merge

- [x] Build limpio y 1221/1221 verde, leido del resumen completo (sin pipe).
- [x] Un test por defecto, los tres **fallando sin su arreglo** (mutacion verificada y revertida).
- [x] Sin migracion EF y sin cambio de esquema.
- [x] Solo tokens `--ov-*` en el CSS nuevo.
- [x] Ningun valor de M6 tocado; `adjunto_leer` sin cambios de universo; B-07 y CA-02.4 intactos.
- [x] Inventario por lectores (MH-041) cerrado y escrito.
- [ ] **OLV-038, OLV-039 y OLV-040: aplicados, pendientes de re-verificacion.** No los cierra el Implementador.
- [ ] Sin push y sin deploy (decision del brief).
# M29 frente B tanda B2 - El dueno del transitorio, la UI del destino y la purga (CIERRA M29)

Estado: **implementado 2026-10-02; 1 commit local, sin push y sin deploy. CON MIGRACION chica (una columna, ningun
indice).** Repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `ee7f198`. Entrada: B-05 y **B-07** de
«Arquitectura M29» (`3-arquitecto-mvc.md`), D-01..D-07 y RD-02/RD-04 de «Diseno M29» (`2-disenador-funcional.md`),
CA-02.1/02.2, CA-03.1..CA-03.6. **Con esto M29 queda cerrado.**

### Escaneo de reutilizacion

`docs/patrones/cat_resumen.txt` -> **sin match**, y era lo esperado: B-05 ya venia declarado como el unico punto «sin
antecedente» de M29. Lo que el escaneo del propio repo si decidio son las tres formas que mas importan:
(a) **descartar es `DarDeBajaAsync`**, partida en un `BajaAsync` privado sin una sola decision de permiso, asi que la
purga hereda el borrado fisico, el borrado de las partes, `ArchivoEliminadoAt` y la liberacion de cuota y **no hay una
sola linea de logica de borrado nueva**; (b) el worker copia el molde de `MotorAgentesWorker` (scope propio por pasada +
`EstablecerAccesoGlobal`, una pasada que falla no tira abajo el worker); (c) el **buscador de clientes** y el dibujo del
**chip** se escribieron una vez en `documentos.js` y los usan las cinco pantallas, en vez de las dos copias que habia.

### B-07 - Que se eligio para el dueno del transitorio, y por que NO fue `GeneradoEnTareaId`

El brief dejaba elegir entre reusar `GeneradoEnTareaId` o una hermana con nombre propio. **Se eligio una columna nueva,
`DocumentoCartera.TareaOrigenId` (`int?`, sin FK ni navegacion), y la razon no es estetica: reusarla rompia dos cosas
visibles.** `GeneradoEnTareaId` tiene **dos lectores**: `ServicioTareas` lo usa para la seccion «lo que armo el agente en
esta tarea» del detalle, y `HerramientasEntregables` para el tope `MaxPorTarea` de la impresora. Con el transitorio
guardado ahi, **un archivo que subio una persona habria aparecido como entregable del agente y le habria comido el tope
de entregables de la conversacion**. Dos significados con dos lectores distintos son dos columnas.

**Migracion: si, una y chica.** `20261002214130_DuenoDelTransitorioM29`: **un solo `AddColumn`**, ningun indice y ninguna
FK tocada. El riesgo R-A2 de B1 (una columna de cinco indices) aca no existe. Aplicada contra `olvidata_agentes_dev` y
verificada con `SHOW COLUMNS` + `SHOW INDEX`: la columna quedo `int NULL` y **los cinco indices de la tabla intactos**.
Sin indice propio a proposito: la purga arranca por `ClienteCarteraId IS NULL`, que es un corte chico, y un indice que
empieza por una columna casi siempre nula no paga.

**La regla, nombrando el caso** (`ValidarAdjuntosAsync`, el unico camino por el que un adjunto llega a un mensaje):

- documento **con** cliente -> `continue`: el universo de la cartera **no cambio**;
- transitorio **con** dueno -> solo esa conversacion (`duenio != tareaId` -> rechazo), y eso vale tambien en una pantalla
  de arranque, donde `tareaId` es null y por lo tanto no puede ser el dueno de nada;
- transitorio **sin** dueno -> solo **quien lo subio**, y al mandar el mensaje queda ligado.

**El hueco que el brief no nombraba y hubo que resolver: en una pantalla de arranque la conversacion todavia no existe**,
asi que el transitorio no puede nacer con dueno. De ahi el estado «huerfano» y `AdoptarTransitoriosAsync`, que lo liga
cuando el id de la tarea ya existe: en el ajuste **antes** del guardado del mensaje (misma transaccion), y en los dos
arranques (plataforma y tarea de trabajo) justo despues. Es idempotente y un transitorio **no cambia de conversacion
nunca**.

### La purga (B-05) y la decision que fue mas alla de la letra del brief

Un `BackgroundService` nuevo, `PurgaDocumentosSinClienteWorker`, **al lado de `MotorAgentesWorker` y separado de el**
(`AddPurgaDocumentosSinCliente()` en `Program.cs`). No decide nada: le pide al servicio que descarte, y toda la decision
vive en `ListarSinClienteVencidosAsync`, que es lo que `documentos-limpiar` imprime **sin `--aplicar`**.

Qué alcanza, en este orden:

1. **`ClienteCarteraId == null` es la PRIMERA clausula de la consulta**, no un `if` adentro del bucle (CA-03.6).
2. vigente (el filtro de baja logica **no** se ignora: lo que se descarta es lo vigente);
3. **con conversacion**: esa conversacion terminada (`Completada`/`Fallida`/`Cancelada`) y `FinalizadaAt` **mas viejo**
   que la ventana;
4. **sin conversacion**: `CreatedAt` mas viejo que la ventana **y sin ninguna fila en `AdjuntosMensajeTarea`**.

**El punto 4 va mas alla de la letra de B-05 («cuya tarea de origen esta terminada») y se declara como decision, no como
arreglo silencioso.** Sin el, el archivo que alguien sube en una pantalla de arranque y nunca manda **no se borra nunca**,
y ese es justo el camino mas comun de la feature: HU-05 dice «lo que se subio y no se guardo no me come la cuota para
siempre». La condicion de los adjuntos es su red de seguridad: «nunca llego a una conversacion» tiene que ser **verdad**,
y la dice la misma tabla por la que `adjunto_leer` resuelve su universo. **Un archivo que se esta usando no se borra por
su fecha de subida**, pase lo que pase con la columna del dueno.

**`DiasGraciaAdjuntoSinCliente` = 7, y `<= 0` APAGA la purga** (`PurgaAdjuntosSinClienteHabilitada`), con el test que lo
afirma en los dos sentidos: con 0 y con -1 no descarta nada, y el **mismo** escenario con 7 si descarta —lo que apaga es
el cero, no el escenario—. El worker, con la purga apagada, loguea el motivo y se va. Suman
`HorasEntrePurgasAdjuntosSinCliente` (6) y `MaxPorPasadaPurgaAdjuntosSinCliente` (200): lo que sobra queda para la
proxima vuelta, porque cada baja borra un archivo del disco.

**El permiso es el acceso global**, exigido explicitamente (`if (!_tenant.EsAccesoGlobal) return []`): un pedido del
portal no puede descartar archivos de todas las organizaciones. Hay test.

### Prueba de mutacion (hecha, no supuesta)

Tres mutaciones, una por guarda, y lo que ensenaron:

| Mutacion | Resultado |
|---|---|
| La guarda de B-07 no rechaza nada (`if (true) continue;`) | **3 casos en rojo** (2 nuevos + el de `AdjuntosEnConfiguracionTests`) |
| `diasGracia <= 0` pasa a `< 0` (el 0 deja de apagar) | **1 caso en rojo** (CA-03.4) |
| Se borra la primera clausula `ClienteCarteraId == null` | **verde** -> el test no servia |

La tercera es la que vale la pena contar. **El test de CA-03.6 pasaba con la clausula borrada**, porque lo salvaban las
otras dos guardas: la condicion de los adjuntos y la relectura antes de la baja, que vuelve a exigir «sin cliente». El
escenario se cambio por el que **aisla** la clausula —un papel viejo de la carpeta de un cliente que **nunca se adjunto a
ninguna conversacion**— y se asserta sobre el **listado**, que es el unico lugar donde vive. Ahi la mutacion se pone roja.
La leccion: *una defensa en profundidad hace que un test de la capa de arriba pase aunque la de abajo este roto*, y eso
es exactamente lo que la prueba de mutacion encuentra y la lectura del diff no.

### La UI (D-01..D-07)

- **D-01** El destino se pregunta **una vez, al subir**, y solo cuando el modal no viene con un cliente dado (desde la
  carpeta de un cliente no hay nada que preguntar). El reversible —*«Usar solo en esta conversacion»*— viene marcado, con
  su linea de ayuda textual del diseno. Si se elige guardar en un cliente y no se dijo cual, **el archivo no sale de la
  maquina**: lo corta el gancho `bloqueado` de la cola de subida, antes de empujar 20 MB.
- **D-02 / RD-02** El chip dice en una linea qué va a pasar: *«solo en esta conversacion»* contra el nombre del cliente,
  y el transitorio se distingue con borde punteado (sin color de alarma: no es un error, es su estado). `SinCliente` y
  `Version` viajan en la respuesta de la subida: **lo que paso con el archivo lo dice el servidor, no lo deduce la
  pantalla**.
- **D-03** *«Guardar en un cliente»* vive **en el chip** y abre el buscador de clientes (`#modalGuardarEnCliente`,
  busqueda + lista, el mismo widget que el bloque de destino). El listado de clientes se pide **cuando hace falta**
  (`GET /Documentos/ClientesParaGuardar`), no al cargar cada pantalla que incluye el modal.
- **D-04** Sin cuenta regresiva y sin fecha. **D-05/A** sin cambios (frente A).
- **D-06** Un solo renderer de chips en `documentos.js` para las **cinco** pantallas (las cuatro conversaciones y el
  cuadro de ajuste), en vez de las dos copias del mismo dibujo que habia: la leyenda se agrego una vez.
- **D-07** El boton *«Subir un documento»* **ya no miente**: despues de B1 funciona siempre que se ofrece, asi que no hay
  nada que esconder. Se arreglo tambien el estado vacio de la lista, que decia en prosa la misma mentira («se suben desde
  la carpeta de un cliente»).

### Donde el brief no alcanzo (declarado, no inventado)

1. **El transitorio del arranque no puede nacer con dueno.** Ver B-07 arriba: de ahi el estado huerfano, la regla «solo
   quien lo subio» y `AdoptarTransitoriosAsync`. Es el unico agregado conceptual de la tanda.
2. **El huerfano que nunca se manda**, punto 4 de la purga. Declarado como decision.
3. **`GeneradoEnTareaId` no se podia reusar** por sus dos lectores. El brief lo dejaba abierto; esta es la respuesta con
   el motivo medido.
4. **`AsignarClienteAsync` no limpia `TareaOrigenId`**, a proposito: desde que hay cliente nada la mira (las dos guardas
   arrancan por «sin cliente») y queda como historia util. Esta escrito en la entidad.
5. **Fuera de alcance, y sigue afuera:** `Agentes/Ejecutar` (el arranque de una tarea de **trabajo**) sigue pidiendo
   cliente para subir un archivo nuevo, con su texto propio. D-06 nombra «las cuatro conversaciones» y esa es la quinta
   pantalla: **no se toco**. La guarda de B-07 si la cubre (un transitorio ajeno no se adjunta ahi tampoco).
6. **El chip de un documento elegido de una lista filtrada por cliente no repite el nombre del cliente**, porque la
   conversacion entera ya es de ese cliente. La distincion que D-02 pide —transitorio contra guardado— se ve igual.

### Cambios por capa

| Capa | Archivo | Que |
|---|---|---|
| Domain | `Entities/DocumentoCartera.cs` | **nueva** `TareaOrigenId` (`int?`), con el por que de no reusar `GeneradoEnTareaId` |
| Application | `Settings/DocumentosOptions.cs` | `DiasGraciaAdjuntoSinCliente` (7, `<= 0` apaga), `HorasEntrePurgas...` (6), `MaxPorPasada...` (200), `PurgaAdjuntosSinClienteHabilitada` |
| Application | `DTOs/DocumentosDtos.cs` | `AdjuntoDeOtraConversacion`; `SubidaDocumentoResultadoDto.SinCliente`/`Version`; **nuevo** `TransitorioVencidoDto` |
| Application | `Interfaces/IDocumentoCarteraService.cs` | `ValidarAdjuntosAsync(..., tareaId, usuarioId)`; **nuevos** `AdoptarTransitoriosAsync`, `ListarSinClienteVencidosAsync`, `DescartarSinClienteVencidosAsync` |
| Infrastructure | `Data/Migrations/20261002214130_DuenoDelTransitorioM29` | **nueva**: un `AddColumn` y nada mas |
| Infrastructure | `Services/Documentos/DocumentoCarteraService.cs` | la guarda de B-07 nombrando los tres casos; `AdoptarTransitoriosAsync`; `DarDeBajaAsync` partido en un `BajaAsync` privado; las dos de la purga; `+ITenantContext` |
| Infrastructure | `Services/Documentos/PurgaDocumentosSinClienteWorker.cs` | **nuevo** `BackgroundService`, separado del motor |
| Infrastructure | `Services/Motor/ServicioTareas.cs` | arranque de plataforma y ajuste: pasan tarea y usuario, y adoptan |
| Infrastructure | `Services/Motor/PreparadorTareaTrabajo.cs` | idem para la tarea de trabajo (la adopcion va en `CrearAsync`, donde existe el id) |
| Infrastructure | `DependencyInjection.cs` | `AddPurgaDocumentosSinCliente()` |
| Web | `Program.cs` | registra la purga al lado del motor |
| Web | `Controllers/DocumentosController.cs` | **nueva** `ClientesParaGuardar` |
| Web | `Views/Shared/_ModalDocumentos.cshtml` | bloque de destino (D-01) + modal del buscador de clientes (D-03) |
| Web | `Views/Shared/_ScriptAdjuntarEnConversacion.cshtml`, `Views/Tareas/Detalle.cshtml` | usan el renderer compartido (dos copias del dibujo -> una) |
| Web | `wwwroot/js/documentos.js` | gancho `bloqueado`; `selectorClientes`; `ovGuardarEnCliente`; `ovChipsAdjuntos`; destino del modal; el estado vacio que mentia |
| Web | `wwwroot/css/site.css` | chip con leyenda y accion, transitorio punteado, lista de clientes. **Solo tokens `--ov-*`** |
| Web | `appsettings.json` | la seccion `Documentos` suma las tres claves, con el aviso del 0 escrito al lado |
| Admin | `Program.cs` | `documentos-limpiar` imprime los transitorios vencidos con **el motivo en palabras** y los descarta con `--aplicar` |
| Tests | `TransitorioDeLaConversacionTests.cs` (**nuevo**, 14 casos) | B-07 (5) y la purga (9), con las mutaciones verificadas |
| Tests | `AdjuntosEnConfiguracionTests.cs` | el transitorio huerfano necesita `SubidoPorUsuarioId`, y **+1 assert**: su id no sirve en otra conversacion de plataforma |

### Evidencia

- `dotnet build OlvidataAgentes.slnx` -> **Compilacion correcta**, 0 errores, **12 advertencias, todas las de siempre**
  (`NU1902` de ImageSharp y `NU1510`): ninguna nueva.
- `dotnet run --project src/OlvidataAgentes.Admin -- migrar` -> «Migraciones aplicadas» contra `olvidata_agentes_dev`
  (local). **Nunca contra produccion.** `SHOW COLUMNS` -> `TareaOrigenId int YES NULL`; `SHOW INDEX` -> los cinco
  indices de la tabla **intactos**.
- `dotnet test tests/OlvidataAgentes.Tests` -> **1217 verdes, 0 con error, 0 omitidos** (34 s). Partia de 1203: +14.
  Medido **sin pipe**, salida a archivo y codigo de salida en 0.
- `documentos-limpiar` sin `--aplicar` contra la base local -> «Archivos sin cliente vencidos: 0 (plazo de 7 dia/s)».
- **Prueba de mutacion**: tres mutaciones, dos atrapadas de entrada y la tercera **encontro un test que no servia** (ver
  arriba). Ninguna quedo en el codigo.
- Sin smoke test funcional: no se levanto la app. La verificacion en navegador real a 1440 y 390, en claro y oscuro, es
  de QA.

### Pruebas minimas para QA

1. **CA-02.2 (el corazon de la tanda)** En cada una de las **cuatro** conversaciones (chat libre, configurar, repartir,
   automatizar): *Adjuntar documentos* -> *Subir un documento*. Aparece **«¿Donde va este archivo?»** con *«Usar solo en
   esta conversacion»* **ya marcada**. Subir asi: el chip dice **«solo en esta conversacion»** y ofrece *«Guardar en un
   cliente»*.
2. **CA-02.2 bis** Repetir eligiendo *«Guardar en la carpeta de un cliente»*: (a) sin elegir cliente, intentar subir ->
   avisa y **el archivo no se sube**; (b) eligiendo cliente -> el chip muestra **el nombre del cliente** y el archivo
   aparece en la carpeta de ese cliente.
3. **CA-03.1 / D-03 / RD-04** Desde el chip, *«Guardar en un cliente»*: queda guardado y el chip cambia de estado **sin
   volver a subir el archivo**. Repetirlo contra (a) un cliente que ya tiene ese archivo, (b) un cliente con el tope
   lleno: se avisa **en el momento** y **el chip sigue diciendo «solo en esta conversacion»** —no queda a medio camino—.
4. **CA-03.1 bis** Despues de guardarlo, **descargarlo**: si diera 404, el movimiento de los bytes fallo.
5. **B-07 (el que importa)** Subir un transitorio en la conversacion A y mandar el mensaje. Despues, en la conversacion B
   de **la misma organizacion**, forzar ese id en el POST (DevTools: agregar un `<input name="DocumentoIds">` con ese id):
   contesta **«Uno de los documentos ya no esta disponible en esta conversacion. Volve a subirlo.»** y no se adjunta.
   Probarlo tambien con **otro usuario** de la organizacion y con una tarea de trabajo.
6. **B-07 control positivo** En la **propia** conversacion, mandar otro ajuste adjuntando el **mismo** transitorio: entra.
   Si este diera rojo, el punto 5 no estaria probando nada.
7. **CA-03.3** Con `DiasGraciaAdjuntoSinCliente` en 1: subir un transitorio, terminar la conversacion, y con un
   `UPDATE TareasAgente SET FinalizadaAt = DATE_SUB(UTC_TIMESTAMP(), INTERVAL 3 DAY)` esperar una pasada (o correr
   `documentos-limpiar --aplicar`): el archivo **desaparece**, el binario no queda en `{raiz}/{tenant}/_organizacion/` y
   el espacio usado de la organizacion baja. **Antes de mover la fecha, NO desaparece.**
8. **CA-03.4** Poner la clave en **0** y reiniciar: el log de arranque dice **«Purga de archivos sin cliente apagada»** y
   `documentos-limpiar` imprime «la purga esta APAGADA». Con un transitorio de una conversacion terminada hace meses,
   **nada se borra**.
9. **CA-03.6** Un documento **con** cliente de una conversacion terminada hace meses: `documentos-limpiar` **no lo
   lista** ni con `--aplicar`.
10. **Mirar antes de aplicar** `documentos-limpiar` sin `--aplicar` dice, por archivo, **por que** entro («la conversacion
    #12 termino el ...» o «nunca llego a una conversacion»). Confirmar que **mirar no borra**.
11. **Pantalla (38)** A **1440 y 390**, en **claro y oscuro**: el bloque de destino y el buscador de clientes dentro del
    modal; el chip con dos renglones no desborda ni empuja el compositor; el borde punteado del transitorio se distingue
    en los dos temas.
12. **Regresion de M5** Subir, renombrar, dar de baja y adjuntar documentos **con** cliente, desde la carpeta de un
    cliente y desde una tarea de trabajo: el camino viejo entero, incluidos los chips del ajuste.
13. **Regresion de M19** Una conversacion donde el agente arma un entregable (`planilla_armar`): el archivo sigue
    apareciendo en «Lo que armo» y el tope por tarea sigue contando **solo** los suyos (es lo que se habria roto reusando
    `GeneradoEnTareaId`).

### Checklist de merge

- [x] Build limpio (0 errores, 12 advertencias conocidas) y **1217 tests verdes**, medidos sin pipe.
- [x] Migracion chica (un `AddColumn`), aplicada contra la base local y verificada: **ningun indice tocado**.
- [x] La guarda de B-07 **nombra los tres casos** y esta probada por mutacion, desde dos puntos de entrada.
- [x] La purga **no borra**: llama a `BajaAsync`, el mismo camino de una persona. Cero logica de borrado nueva.
- [x] `ClienteCarteraId == null` es la **primera clausula** de la consulta de la purga, y el test que lo afirma **aisla**
      esa clausula (la version anterior del test pasaba con la clausula borrada).
- [x] `<= 0` **apaga** la purga, con test en los dos sentidos.
- [x] `IgnoreQueryFilters([FiltroTenant])` justificado y nombrado; el filtro de baja logica **no** se ignora.
- [x] Solo tokens `--ov-*` en el CSS; textos exactos del diseno.
- [x] Ningun valor de M6 ni de M14 tocado; `adjunto_leer` sin cambios.
- [x] Logica en services; los controllers solo bindean y devuelven.
- [x] Commit local, sin push y sin deploy.
- [ ] **OLV-036 y M29 completo: aplicado, pendiente de re-verificacion.** El cierre lo declara QA en contexto nuevo.
# M29 frente B tanda B1 - El documento sin cliente: la migracion y la frontera del portal del cliente

Estado: **implementado 2026-10-02; 1 commit local, sin push y sin deploy. CON MIGRACION (la primera de M28/M29),
aplicada contra la base local, nunca contra produccion.** Repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base
`37b215b`. Entrada: B-01..B-04 y B-06 de «Arquitectura M29» (`3-arquitecto-mvc.md`), CA-02.1/02.3/02.4,
CA-03.1/03.2/03.5 y CA-T.1..T.5 (`1-analista-funcional.md`). **Es la respuesta a OLV-036.** La UI (modal, chips,
`documentos.js`) y la purga (`BackgroundService`) son la tanda B2 y **no se tocaron**.

### Escaneo de reutilizacion

`docs/patrones/cat_resumen.txt` -> sin match, y es lo esperable: no se construyo nada nuevo. Toda la tanda es el
pipeline de M5 con **un parametro opcional** (`SubirInternoAsync`), mas un alta que reusa sus mismas validaciones
(`AsignarClienteAsync`). Lo que el escaneo si decidio es la **forma** de dos cosas: (a) el universo «sin cliente» se
escribio como un hermano de `DelCliente` (`DelAlcance`), no como un `if` repartido por el archivo; (b) la frontera se
probo con el molde de `PortalClienteFronteraHttpTests` de M18, que ya tenia el portal real levantado y el escenario de
dos clientes sembrado.

### El riesgo central: como quedo el `FiltroCliente` y como se probo (R-01, CA-T.2)

`DocumentoCartera` paso de `IClienteOwned` a **`IClienteOwnedOpcional`** (es lo que exige una columna `int?`), asi que
el filtro que lo cubre es `AppDbContext.ApplyClienteFilterOpcional`, el mismo que ya usaba `TareaAgente`. **Nombra el
caso:**

```
e => ClienteCarteraIdActual == null || (e.ClienteCarteraId != null && e.ClienteCarteraId == ClienteCarteraIdActual)
```

La condicion `!= null` es **redundante en SQL** —`NULL == @cliente` da *unknown* y la fila ya quedaba afuera— y esta
escrita igual porque «queda afuera por el unknown de SQL» no es una garantia que se pueda leer: un `OR`, un `?? 0` o un
cambio de proveedor la invierten sin que falle nada. Para `TareaAgente` **no cambia una sola fila**: es la misma
semantica, dicha en voz alta.

**Como se probo, con control positivo y negativo y por HTTP** (`DocumentoSinClienteFronteraHttpTests`, 6 casos): el
portal real levantado con su propia carpeta de documentos en disco, y un documento sin cliente sembrado **en el peor
caso posible** (`VisibleParaCliente = true`, que es justamente lo que el servicio ahora impide y la base no). Cada
asercion «no lo ve» viaja al lado de un «esto si lo ve» en la **misma respuesta**: la pantalla de *Mis documentos*, la
portada del cliente, la descarga por id a mano, el vecino (Ferreteria), y un caso que afirma que el **Director si
descarga** ese mismo archivo —si ese se pusiera rojo, los otros dejarian de probar algo—.

**Prueba de mutacion hecha, no supuesta:** con el filtro cambiado a `|| e.ClienteCarteraId == null`, **5 de los 6 casos
se ponen rojos** y el sexto (el control del Director) sigue verde. Es la unica forma de saber que el test no pasa por
casualidad; es la leccion de M18, donde cuatro auto-fixes fueron invisibles para 891 tests verdes.

**Segundo candado, defensa en profundidad:** `CambiarVisibilidadParaClienteAsync` **rechaza** un documento sin cliente.
Sin eso, encender «Lo ve el cliente» dejaria una fila visible-para-el-cliente sin cliente, y lo unico que la mantendria
afuera del portal seria el filtro. Son dos candados, no uno.

### La migracion (B-02, R-A2)

`20261002211208_DocumentoSinClienteM29`. Escrita y revisada sola, y corrida contra la base local
(`olvidata_agentes_dev`) **antes** de seguir. Tres operaciones y nada mas:

1. `DropIndex IX_DocumentosCartera_ClienteCarteraId_NombreVigente`.
2. `AlterColumn ClienteCarteraId` -> `int NULL`.
3. `CreateIndex IX_DocumentosCartera_TenantId_ClienteCarteraId_NombreVigente` **unico**.

Verificado con `SHOW CREATE TABLE`: la columna quedo `int DEFAULT NULL`, el unico nuevo lleva `TenantId`, los otros
tres indices (`ArchivoId` unico, `(TenantId, ClienteCarteraId, DeletedAt)`, `(ClienteCarteraId, HashSha256)`) quedaron
**intactos** y la FK sigue siendo `ON DELETE RESTRICT`, ahora opcional (`IsRequired(false)`). EF no toco la FK ni los
otros indices: MySQL admite el `MODIFY COLUMN` con todo en su lugar.

### Donde el brief NO alcanzo (lo unico que hay que decidir)

**B-03 dice «no mueve el archivo de carpeta: la ruta se resuelve por `ArchivoId`». Eso es factualmente falso en este
repo** y es el unico punto donde me aparte del brief. `AlmacenDocumentosDisco.Ruta` es
`{raiz}/{tenant}/{cliente}/{archivoId}`: **el cliente esta en la ruta**, y todo lector la arma con
`documento.ClienteCarteraId` (`Abrir`, `Eliminar`, `Confirmar`). Asignar la columna sin mover los bytes dejaria el
archivo en `_organizacion/` y a todos los lectores buscandolo en `{cliente}/`: el documento quedaria **imposible de
abrir y de borrar**, y `documentos-limpiar` lo veria como huerfano.

Habia dos salidas: (a) mover los bytes; (b) persistir una columna nueva que diga «este archivo vive en la carpeta de la
organizacion» y pasarla a las seis llamadas del almacen. **Se eligio (a)**, porque es menos codigo, no agrega una
segunda fuente de verdad y mantiene el invariante «carpeta = cliente» del que vive el pareo disco<->base. Se agrego
`IAlmacenDocumentos.Mover(tenant, origen, destino, archivoId)` (un `File.Move` sin sobrescribir, dentro del mismo
tenant) y el Move va **antes** del commit: si el guardado falla, los bytes vuelven y el documento sigue siendo
transitorio, que es el estado del que se partio. **Lo que si quedo escrito en el codigo, porque sigue siendo verdad:**
la carpeta en disco **no** es la fuente de verdad de a quien pertenece un documento —eso lo dice la columna—; la carpeta
es solo donde estan los bytes, y por eso hay que mantenerla de acuerdo.

### Decisiones que el brief dejaba abiertas y se cerraron

- **Duplicado por hash y tope por cliente en una subida SIN cliente: no corren.** Son validaciones *por cliente* y sin
  cliente no hay contra que compararlas —dos conversaciones distintas pueden adjuntar el mismo papel y las dos lo
  necesitan—. Se revalidan las dos, contra ESE cliente, en `AsignarClienteAsync` (CA-03.1, que es exactamente lo que
  pide). **La cuota de la organizacion vale siempre** y no hubo que tocarla: la suma ya era por `TenantId` (verificado
  con test). Consecuencia que conviene saber: la cantidad de transitorios de una organizacion la limita **solo** el
  tope de 1 GB hasta que exista la purga de B2.
- **CA-02.4, «ni en el de la organizacion»:** `OpcionesParaAdjuntarAsync(null)` —el listado de toda la organizacion que
  usan las conversaciones de plataforma— **excluye** los documentos sin cliente, nombrando el caso en vez de dejarlo al
  `join`. Un transitorio es de la conversacion donde se subio: ofrecerlo en otra seria compartirlo, que esta fuera de
  alcance. En el backoffice de Olvidata se partio la consulta base: el **listado** (grilla, totales y opciones de
  filtro) los excluye, porque es un listado por cliente; el **medidor de espacio** los sigue contando, porque ocupan
  disco real y cuentan contra la cuota, y un medidor que no los mire miente.
- **`ValidarAdjuntosAsync` no cambio y es deliberado:** un transitorio se adjunta en una conversacion sin cliente
  (asi es como llega a `adjunto_leer`), y en una tarea CON cliente queda afuera solo, porque su `ClienteCarteraId`
  (null) no es ese cliente. Lo que **no** quedo cerrado es que alguien forje el id de un transitorio de otra
  conversacion de su propia organizacion al mandar el mensaje: no esta en ningun listado, pero el id alcanza. No hay CA
  que lo pida (el alcance no incluido dice «compartir entre conversaciones» como no-feature, no como prohibicion) y
  cerrarlo pide saber de que conversacion nacio el archivo —dato que la purga de B2 va a necesitar igual—. **Queda
  declarado para B2, no resuelto en silencio.**
- **El camino de arranque (LP-002):** `hayDocumentos` pedia «existe un documento» y un transitorio lo habria tildado.
  El paso dice «subi los papeles DEL CLIENTE», y la regla del `CLAUDE.md` es que se tilda porque lo que pedia existe de
  verdad —borrar los clientes lo destilda—. Ahora exige `ClienteCarteraId != null`, con test de control positivo y
  negativo.
- **`AsignarClienteAsync` no reasigna:** un documento que ya tiene cliente se rechaza. Mudar un papel de un cliente a
  otro es otra cosa y nadie la pidio.
- **La ficha del documento (`Views/Documentos/Ver.cshtml`)**, que no es de B2: un archivo sin cliente muestra el rotulo
  «Sin cliente (solo de esta conversacion)» **sin enlace** (no hay ficha de cliente a la que ir) y, al darlo de baja,
  vuelve a Cartera en vez de a `/Documentos` sin `clienteId`, que no es una pantalla.

### Cambios por capa

| Capa | Archivo | Que |
|---|---|---|
| Domain | `Entities/DocumentoCartera.cs` | `ClienteCarteraId` -> `int?`; pasa de `IClienteOwned` a **`IClienteOwnedOpcional`**, con el por que escrito |
| Domain | `Entities/IClienteOwned.cs` | el doc de `IClienteOwnedOpcional` nombra a `DocumentoCartera` y al caso del null |
| Application | `DTOs/DocumentosDtos.cs` | `SinClienteAsignado`, `VisibilidadSinCliente`, `YaTieneCliente`, `GuardadoEnCliente(cliente)`; `DocumentoDetalleDto.ClienteCarteraId` -> `int?` |
| Application | `Interfaces/IAlmacenDocumentos.cs` | `clienteId` -> `int?` en las 6 operaciones; **nuevo** `Mover`; `ArchivoAlmacenadoDto.ClienteCarteraId` -> `int?` |
| Application | `Interfaces/IDocumentoCarteraService.cs` | `SubirAsync(int? clienteId, ...)`; **nuevo** `AsignarClienteAsync(id, clienteCarteraId, version)` |
| Infrastructure | `Data/AppDbContext.cs` | `ApplyClienteFilterOpcional` **nombra el caso del null** (el riesgo central) |
| Infrastructure | `Data/Configurations/DocumentosConfigurations.cs` | unico -> `(TenantId, ClienteCarteraId, NombreVigente)`; FK `IsRequired(false)`, sigue Restrict |
| Infrastructure | `Data/Migrations/20261002211208_DocumentoSinClienteM29` | **nueva** (3 operaciones) |
| Infrastructure | `Services/Documentos/AlmacenDocumentosDisco.cs` | `CarpetaOrganizacion = "_organizacion"` (constante del codigo); `Ruta` toma `int?` y resuelve adentro, con la guarda `> 0` intacta; `Mover`; `Enumerar` recorre la carpeta nueva con el cliente en null |
| Infrastructure | `Services/Documentos/DocumentoCarteraService.cs` | `DelAlcance` (universo con o sin cliente); `SubirInternoAsync` con cliente opcional; `GuardarConNombreUnicoAsync` por alcance (CA-T.4); **nuevo** `AsignarClienteAsync`; guarda en `CambiarVisibilidadParaClienteAsync`; `ObtenerAsync` sin cliente; `OpcionesParaAdjuntarAsync` y el listado de staff excluyen los transitorios |
| Infrastructure | `Services/Organizacion/CaminoDeArranqueService.cs` | el paso «papeles» exige cliente |
| Web | `Controllers/DocumentosController.cs` | `Subir(int? clienteId, ...)` (**el mensaje mentiroso de OLV-036 se va con el binding**); **nueva** accion `AsignarCliente` |
| Web | `Views/Documentos/Ver.cshtml` | la ficha de un archivo sin cliente no ofrece enlaces que no existen |
| Admin | `Program.cs` | `documentos-limpiar` imprime `_organizacion` cuando no hay cliente |
| Admin | `Demo.cs` | los ejemplos son siempre de un cliente (el `Contains` sobre `int?`) |
| Tests | `DocumentoSinClienteTests.cs` (**nuevo**, 19 casos) | subir sin cliente, corte por bytes, cuota, nombre unico por organizacion, listados, asignar cliente con sus 4 rechazos, multi-tenant, `Ruta`, `Enumerar`, y el tipo del parametro de `Subir` (OLV-036) |
| Tests | `DocumentoSinClienteFronteraHttpTests.cs` (**nuevo**, 6 casos) | CA-T.2 por HTTP con control positivo y negativo + mutacion verificada |
| Tests | `AdjuntosEnConfiguracionTests.cs` | **+1**: un transitorio entra por `adjunto_leer` sin ninguna rama nueva (B-06, CA-T.1) |
| Tests | `CaminoDeArranqueTests.cs` | **+1**: un transitorio no tilda el paso de los papeles |
| Tests | `DocumentosTests.cs` | el helper de subida toma `int?` |

### Evidencia

- `dotnet build OlvidataAgentes.slnx` -> **Compilacion correcta**, 0 errores. 12 advertencias, todas las de siempre
  (`NU1902` de ImageSharp y `NU1510`): **ninguna nueva**.
- `dotnet run --project src/OlvidataAgentes.Admin -- migrar` -> «Migraciones aplicadas» contra
  `olvidata_agentes_dev` (local). **Nunca contra produccion.** Esquema verificado con `SHOW CREATE TABLE`.
- `dotnet test tests/OlvidataAgentes.Tests` -> **1203 verdes, 0 con error, 0 omitidos** (32 s). Partia de 1176: +27
  (19 + 6 + 1 + 1). Medido **sin pipe**: salida a archivo y `grep` despues, con el codigo de salida en 0.
- **Prueba de mutacion del filtro**: 5 de 6 casos de la frontera en rojo con el filtro roto. Dejada documentada, no
  dejada en el codigo.

### Pruebas minimas para QA

1. **CA-02.1 / OLV-036** `POST /Documentos/Subir` con un archivo y **sin** `clienteId` (DevTools o curl): la respuesta
   ya **no** es «Elegi un archivo» —el archivo entra y queda sin cliente—. Repetirlo con `clienteId` vacio (`""`), que
   es lo que manda un form sin cliente: mismo resultado.
2. **CA-02.3** Subir sin cliente un archivo de mas de 20 MB (corte por bytes), un .docm (macros) y un PDF escaneado:
   los tres contestan **lo mismo** que contestarian con cliente, y nada queda guardado cuando se rechaza.
3. **CA-02.4** Subir sin cliente y despues: (a) abrir Documentos de cualquier cliente -> no esta; (b) en una
   conversacion de plataforma, abrir el selector de documentos de la organizacion -> no esta; (c) en el backoffice de
   Olvidata, el listado de esa organizacion -> no esta, pero el **espacio usado** si lo cuenta.
4. **CA-T.2 (el que importa)** Con un archivo sin cliente cargado, entrar al portal como **usuario cliente**: no esta
   en *Mis documentos* ni en la portada, y `/PortalDocumentos/Descargar?id=<ese id>` da **404**. Control positivo en la
   misma sesion: un documento del estudio con «Lo ve el cliente» encendido **si** se lista y **si** se descarga.
5. **CA-T.2 bis** Intentar encender «Lo ve el cliente» sobre el archivo sin cliente (desde la grilla o forzando el
   POST): se rechaza con «todavia no es de ningun cliente».
6. **CA-03.1** `POST /Documentos/AsignarCliente` con `id`, `clienteId` y `version`: queda como documento normal de ese
   cliente y aparece en su listado. Repetir con (a) un archivo cuyo contenido ya esta en ese cliente -> «ya esta
   cargado como...»; (b) un cliente con el tope lleno -> «ya tiene N documentos»; (c) un nombre que ya existe ahi -> se
   guarda con «(2)»; (d) una `version` vieja -> «Otra persona cambio...»; (e) un documento que **ya** tiene cliente ->
   «ya esta guardado en la carpeta de un cliente».
7. **El archivo se abre despues de guardarlo** (es lo que prueba que los bytes se movieron): asignar cliente y despues
   **descargar** el documento. Si diera 404, el Move fallo.
8. **CA-03.2 / CA-03.5** Dar de baja un archivo sin cliente: desaparece, el binario **no** queda en
   `{raiz}/{tenant}/_organizacion/` y el espacio usado de la organizacion baja.
9. **CA-T.3** Con la sesion de otra organizacion, forzar el id de un archivo sin cliente ajeno en ver, descargar,
   asignar cliente y dar de baja: los cuatro contestan «no existe» y el documento queda intacto.
10. **CA-T.4** Subir `balance.txt` sin cliente en dos organizaciones distintas: las dos lo guardan como `balance.txt`,
    sin sufijo. En la misma organizacion, el segundo se guarda como `balance (2).txt`.
11. **CA-T.5** Mirar la carpeta del almacen: el archivo sin cliente esta en `{raiz}/{tenant}/_organizacion/{guid}`.
    Mandar `clienteId=0` en el POST de subida: **no** cae ahi (es un cliente que no existe -> 404).
12. **Regresion de M18** Repetir el recorrido del portal del cliente completo (sus documentos, su portada, sus pedidos)
    con los dos usuarios cliente del escenario: nada cambio para ellos.
13. **Regresion de M5** Subir, renombrar, dar de baja y adjuntar documentos **con** cliente: el camino viejo entero.

### Checklist de merge

- [x] Build limpio (0 errores, 12 advertencias conocidas) y **1203 tests verdes**.
- [x] Migracion escrita y revisada sola, en su propio paso, y **aplicada contra la base local** (nunca produccion).
- [x] El `FiltroCliente` **nombra** el caso del null, y la frontera esta probada por HTTP con control positivo y
      negativo **y con prueba de mutacion**.
- [x] La carpeta del archivo sin cliente es una **constante del codigo**; la guarda `clienteId > 0` sigue entera.
- [x] El nombre unico sin cliente lo garantiza `GuardarConNombreUnicoAsync` filtrando por `TenantId` (CA-T.4).
- [x] `adjunto_leer` **sin cambios**, con un test que lo afirma (B-06).
- [x] Ningun valor de M6 ni de M14 tocado.
- [x] Logica en services; los controllers solo bindean y devuelven.
- [x] Castellano rioplatense en mensajes y comentarios.
- [x] Commit local, sin push y sin deploy.
- [ ] **Tanda B2 (pendiente):** UI (modal, chips de destino, `documentos.js`), la purga (`BackgroundService` +
      `DiasGraciaAdjuntoSinCliente` + `documentos-limpiar`), y **cerrar el id forjado de un transitorio de otra
      conversacion** (declarado arriba).
- [ ] **OLV-036: aplicado, pendiente de re-verificacion.** El cierre lo declara QA en contexto nuevo.
