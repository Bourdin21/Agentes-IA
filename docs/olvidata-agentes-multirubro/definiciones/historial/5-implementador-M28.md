<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/5-implementador.md el 2026-10-03 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - M28 (6 bloques archivados)

- M28 - Ronda de re-verificacion: los tres reparos (OLV-035, OLV-036, OLV-037)
- M28 - Ronda de arreglos de los tres lotes de QA (OLV-030 a OLV-034)
- M28 - Arreglo del lote 1 de QA (OLV-028 y OLV-029)
- M28 — El chat libre (TANDA 2: la pantalla. Última)
- M28 — El chat libre (TANDA 1b: CU-03, A-08 y A-09)
- M28 — El chat libre (TANDA 1: solo el motor)

---

# M28 - Ronda de re-verificacion: los tres reparos (OLV-035, OLV-036, OLV-037)

Estado: **aplicado 2026-10-02 (dos de tres); pendiente de re-verificacion por QA; 1 commit local, sin push y sin
deploy.** Repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `7b508d5`. Entrada: la **ronda de
re-verificacion** de `6-qa.md` (partes OLV-035, OLV-036 y OLV-037) y CA-04.1 / CA-04.2 / RF-08 textuales de
`1-analista-funcional.md`. **Sin migracion EF.** **Lo aplicado queda "aplicado, pendiente de re-verificacion": el
cierre lo declara QA en contexto nuevo.**

### Escaneo de reutilizacion
`docs/patrones/cat_resumen.txt` -> sin match (arreglo de defectos sobre codigo propio). Dentro del repo si, y decidio la
forma de los dos arreglos: (a) `RotulosTipoTarea` -la tabla sin `default` que dejo OLV-029- recibio la leyenda de
origen, en vez de otro ternario en la vista; (b) `IPermisosOrganizacion.VeEnMenuAsync` -la condicion completa que dejo
OLV-028- es la que ahora consulta el camino de arranque, en vez de repetir media condicion.

### OLV-036 (major) - NO APLICADO: el arreglo honesto pide una migracion
**Parado y avisado, como pide la tanda.** El parametro vacio es el sintoma; el fondo es que **un documento de la
organizacion sin cliente no existe en el modelo de datos**:

- `DocumentoCartera.ClienteCarteraId` es `int` **no nulable**, implementa `IClienteOwned` (no `IClienteOwnedOpcional`),
  tiene **FK a `ClientesCartera`** y entra en cuatro indices, uno de ellos el **unico**
  `(ClienteCarteraId, NombreVigente)`.
- Toda la tuberia de subida esta tecleada por cliente: `SubirInternoAsync` arranca con `ClienteVigenteAsync`, el
  duplicado por hash, el tope `MaxPorCliente` y el nombre unico son **del cliente**, y el archivo se guarda en disco
  con `_almacen.GuardarTemporalAsync(tenantId, clienteId, archivoId)` -el **clienteId es parte de la ruta**-.
- `AdjuntoMensajeTarea.DocumentoCarteraId` tambien es FK no nulable: no hay otro lugar donde pueda vivir un adjunto.

Es decir: hacer que "sin cliente" sea **valido de verdad** -y no un mensaje mas claro para un rechazo, ni un
`clienteId = 0` convenido, ni un endpoint paralelo, los tres descartados por la tanda- es volver el cliente
**opcional** en el documento. Eso es **cambio de esquema** (`ALTER` de la columna, bajar y rehacer la FK y los cuatro
indices) **y una decision de producto que nadie tomo todavia**: donde vive un documento de la empresa (la pantalla de
Documentos es por cliente), si dos documentos sin cliente pueden llamarse igual (en MySQL el indice unico deja pasar
varios `NULL`), y contra que cuota cuentan. **El mensaje mentiroso ("Elegi un archivo." con el archivo adentro) sigue
tal cual a proposito:** arreglarlo solo habria dejado un rechazo mas claro -justo lo que la tanda descarta- y habria
dado la falsa senal de que el camino existe. **Decision pendiente de Joaquin.** El reparo que condiciona la liberacion
**sigue abierto**.

### OLV-037 (minor) - la leyenda nombraba al configurador, y el enlace faltaba para el autor
El diagnostico anterior estaba **al reves en una mitad y bien en la otra**, y QA vio una sola porque entro como
Directora:

- **La leyenda estaba mal** (lo que reporto QA). `ReglaService.OrigenAgente` era un `if` de dos ramas -"viene de una
  tarea de trabajo? el nombre del agente; si no, null"- y la vista completaba el `null` con "Propuesta del
  configurador" / "desde el configurador". El `else` se tragaba **las otras tres conversaciones de plataforma**. Ahora
  la frase sale de **`RotulosTipoTarea.OrigenPropuesta`**, la misma tabla sin `default` de OLV-029: "Propuesta del
  configurador", "del asistente", "del analista", "del chat libre", y `Propuesta de <<agente>>` para una tarea de
  trabajo. Un tipo que no propone reglas devuelve `null` y no se le inventa origen.
- **El enlace faltaba, pero solo para el autor que no dirige** (lo declarado). `ReglaService.Conversacion` daba el
  enlace a staff, a un Director **y** al autor **solo si la tarea era `Trabajo`**: por eso QA, como Directora, lo vio
  bien, y el Empleado que propuso la regla en **su** chat libre no llegaba a su propia conversacion -mientras la
  pantalla de propuestas si se la muestra-. Es el molde de OLV-033 otra vez: lista blanca de un valor. Quedo como
  `ClasesDeTarea.ElAutorVeLaConversacion` (`Trabajo`, `Analista`, `ChatLibre`), lista blanca, nunca un `!=`.
- **Los otros dos huecos declarados: el diagnostico era correcto, no hay defecto.** (a) "Propuesta de <<un agente>>" en
  `_PropuestaAgenteFila.cshtml` es **inalcanzable**: la unica fuente de esa tarjeta es `ListarPendientesParaMiAsync`,
  que filtra `Tipo == Trabajo`, asi que `AgenteOrigen` nunca es null ahi. (b) `ListarPendientesParaMiAsync` sigue
  **sin** listar las propuestas del chat libre, igual que no lista las del analista ni las del configurador: cada
  conversacion de plataforma muestra las suyas adentro. Son decisiones, no defectos, y ningun parte las pide.
- **Deuda anotada, no tocada:** la lista `Trabajo | Analista | ChatLibre` esta escrita a mano **cinco veces mas** en
  `PropuestaReglaService` (guardas de permisos). No se unifico -ningun parte lo pide y son guardas de permisos-, pero
  queda dicho en el doc de `ElAutorVeLaConversacion`: son la respuesta a la misma pregunta.

### OLV-035 (trivial) - el arreglo de OLV-028 cerro el menu y no el tablero
`CaminoDeArranqueService` armaba sus pasos con **media condicion**: `EtapasEntrega.Visible(opcion, etapa)`, o sea solo
la etapa. La condicion completa ya existia en `VeEnMenuAsync` (etapa + rol + **version publicada del artefacto**), asi
que el camino **pregunta por la misma funcion que el menu** y no por una regla paralela -que es exactamente lo que
produjo este defecto-. Se cerro tambien la **otra superficie del mismo hueco**: `Views/PrimerosPasos/Index.cshtml`
usaba `VeEnMenu` (sincrona, sin disponibilidad) en los **siete** `@if` de opciones de plataforma (3 de Automatizar, 2
de Configurar, 1 de Repartir, 1 dentro de un `||`); esos pasaron a `await VeEnMenuAsync`. Los otros 15 `@if` siguen con
`VeEnMenu`: no dependen de un agente de plataforma y la version asincrona les daria lo mismo.

**Que quedo distinto en el camino de arranque** (lo unico que cambia, y es el efecto buscado): **sin** version
publicada del analista, el paso 1 ("Conta que venis a resolver" -> `/Analista`) **ya no aparece** y el camino arranca
por "Carga tus clientes". La tarjeta **no desaparece** -los otros cinco pasos siguen- y **publicado el analista el
paso vuelve a su lugar**, que es el control positivo que quedo en un test. **Ningun paso se perdio por el rol**:
ninguna de las tres opciones del camino (`Automatizar`, `Cartera`, `Agentes`) esta en `EtapasEntrega.SoloDirector`, asi
que para un Empleado no cambio nada. **No se rediseno el camino.**

**Efecto lateral en los tests, declarado:** la etapa pasa a leerse de la **sesion** (`_contexto.EtapaEntrega`, de donde
la lee el menu) y no de una consulta propia al tenant. Es lo correcto -el menu y la tarjeta ya no pueden discrepar
durante el TTL de la sesion-, pero los scopes de test no traian etapa (y sin etapa se ve todo, como el staff). Por eso
`ScopeMiembro` y `EntornoReglas.Como` aceptan ahora una `etapa` opcional, y el test de la primera etapa la pasa: sin
eso ese test habria seguido verde sin probar nada.

### Cambios por capa
- **Application**: `RotulosTipoTarea.OrigenPropuesta` (+ tabla `OrigenDePlataforma`);
  `ClasesDeTarea.ElAutorVeLaConversacion`.
- **Infrastructure**: `ReglaService` (`OrigenAgente` por la tabla, `Conversacion` por la lista blanca nombrada);
  `CaminoDeArranqueService` (`VeEnMenuAsync` en vez de `EtapasEntrega.Visible`).
- **Web**: `ReglasTextos.Origen` (el respaldo de `PropuestaAgente` ya no nombra al configurador);
  `Views/Reglas/Detalle.cshtml` (respaldo del historial); `Views/PrimerosPasos/Index.cshtml` (7 `@if` asincronos).
- **Tests**: `TestServicios.ScopeMiembro` y `EntornoReglas.Como` (+`etapa` opcional); `CaminoDeArranqueTests` (publica
  el analista donde espera el paso 1, y pasa la etapa donde la prueba); `M28ArreglosQaTests` (+4 tests).
- **Sin migracion EF, sin tocar ningun valor de M6, sin publicar nada** (artefacto 121 / version 147 intactos).

### Evidencia
- `dotnet build OlvidataAgentes.slnx` -> **Compilacion correcta**, 0 errores, **0 advertencias CS nuevas** (quedan las
  preexistentes de NuGet y xUnit).
- `dotnet test tests/OlvidataAgentes.Tests` -> **1164/1164** (se partia de 1160; +4 tests). Medido **sin pipe**, con el
  resumen completo a archivo.
- **Verificado por el camino inverso.** Revirtiendo solo los arreglos de `ReglaService` y `CaminoDeArranqueService`:
  `Una_regla_nacida_en_un_chat_libre_dice_que_vino_del_chat_libre` falla con `Expected: "Propuesta del chat libre" /
  Actual: null`, y `El_camino_no_ofrece_contar_sin_una_version_publicada_del_analista` falla con "El camino sigue
  pidiendo el paso de contar." El control positivo (`Publicado_el_analista...`) pasa en las dos corridas.

### Pruebas minimas para QA
1. **OLV-037, la leyenda.** Chat libre de un **Empleado** con una propuesta de regla aplicada -> `/Reglas/Detalle/<id>`
   dice **"Propuesta del chat libre"** en Origen y en el historial, no "del configurador". Repetir desde el
   **configurador**: ahi tiene que seguir diciendo "Propuesta del configurador".
2. **OLV-037, el enlace.** El mismo detalle, como el **Empleado autor** (no Director): el enlace *Ver conversacion*
   **esta** y llega a su chat libre. Un Empleado que **no** es el autor sigue sin ver la regla personal ajena.
3. **OLV-035.** Con las cuatro versiones de plataforma en **Borrador**: ningun `a[href]` del **tablero** ni de
   **Primeros pasos** apunta a `/Analista`, `/ConfiguracionReglas/Nueva` ni `/Asistente/Nueva`, y la tarjeta del camino
   **sigue apareciendo**, con el paso que sigue arrancando en "Carga tus clientes". Publicadas las cuatro: el paso 1
   vuelve a ser "Conta que venis a resolver".
4. **OLV-036: sin cambios, no re-verificar.** Se reproduce igual (mismo mensaje mentiroso incluido). Espera decision de
   producto sobre el documento de la empresa sin cliente.

### Checklist de merge
- [x] Build 0 errores - tests 1164/1164 (de 1160)
- [x] Goldens de hash de contexto intactos (no se toco ningun prompt ni formato)
- [x] Sin migracion EF (ningun cambio de esquema)
- [x] Logica en services/helpers, nunca en controllers
- [x] Multi-tenant sin cambios; ningun `IgnoreQueryFilters()` sin nombre nuevo
- [x] `Mcp` y `Cli` sin tocar
- [x] Costo cero: ninguna llamada a la API real ni salida a internet; no se levanto la app
- [x] Nada publicado; ningun valor de M6 tocado; commit local, sin push
- [ ] **OLV-036 sin arreglar: requiere migracion EF y una decision de producto. Avisado, no implementado.**
# M28 - Ronda de arreglos de los tres lotes de QA (OLV-030 a OLV-034)

Estado: **aplicado 2026-10-02; pendiente de re-verificacion por QA; 1 commit local, sin push y sin deploy.** Repo
`C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `6d679d8`. Entrada: los partes de los **tres lotes de M28**
(`6-qa.md`), **A-10** de `3-arquitecto-mvc.md` (decision ya tomada) y **D-05 / D-07** de `2-disenador-funcional.md`.
**Sin migracion EF** (ningun cambio de esquema). **Los cinco defectos quedan "aplicado, pendiente de
re-verificacion": el cierre lo declara QA en contexto nuevo.**

### Escaneo de reutilizacion
`docs/patrones/cat_resumen.txt` -> sin match (arreglo de defectos sobre codigo propio). Dentro del repo si se reutilizo,
y decidio la forma de dos arreglos: (a) la tabla de `ClasesDeTarea`, que ya era el lugar donde vive "que clase de tarea
es cada tipo", recibio las dos preguntas nuevas en vez de dejarlas sueltas en la vista y en el service; (b) el test de
contrato sobre un `.js` del repo (`TableroTests.El_dibujo_toma_el_orden_del_servidor...`) es el molde del test del
recorte por grupo, porque el proyecto de tests no corre JavaScript.

### Los cinco defectos

- **OLV-030 (major) - la tarjeta de parte no se dibujaba nunca en un chat libre.** No era un switch de enum: era un
  **booleano viejo con dos significados** (`EsDePlataforma` = "no es un pedido de trabajo a un agente" **y** "no tiene
  partes"), y el chat libre es lo primero sin ser lo segundo, porque es la unica conversacion de plataforma que delega.
  Los dos significados quedaron con **un nombre propio cada uno**: `EsDePlataforma` (la palanca de A-01, sin tocar) y
  `ClasesDeTarea.MuestraPartesYAprobaciones` / `TareaDetalleDto.MuestraPartesYAprobaciones`, lista blanca por inclusion
  (`Trabajo`, `ConsultaCliente`, `ChatLibre`). **No se pego un `|| EsChatLibre` a ningun condicional.** Grepear el
  booleano entero destapo un **tercer** lugar que QA no habia visto: `Detalle.cshtml` cargaba `_ScriptAprobaciones` con
  `!esDePlataforma`, asi que un chat libre podia **mostrar** la tarjeta de aprobacion y no tener con que **resolverla**
  (el boton sin la accion). Las tres decisiones usan ahora la misma propiedad. La pastilla "Sin propuestas pendientes"
  paso a `TieneTarjetasDeTrabajo`: habla de propuestas, no de partes (mismo conjunto hoy, nombre correcto).
- **OLV-031 (major) - el grupo "Configurar" desaparecia con 16 agentes o mas.** El tope del autocomplete es ahora
  **por grupo** (`recortarPorGrupo` en `site.js`) y no un `.slice(0, TOPE)` sobre la lista plana. Un grupo fijo y corto
  -"Configurar" son cuatro items- nunca llega al tope, asi que no hay lista larga que lo pueda empujar afuera. El tope
  sigue existiendo para que una organizacion con cien agentes no abra un menu de cien.
- **OLV-033 (major, bloqueante) - una preferencia personal del chat libre no se podia aplicar nunca.** A-10 al pie:
  el chat libre **se agrega a la lista blanca** y sigue siendo lista blanca (`Trabajo` o `ChatLibre`,
  `ClasesDeTarea.OrigenDePreferenciaPersonal`), nunca un `!=` negado. **Eran dos compuertas, no una:** la que QA
  diagnostico (`ReglaService.EsPropuestaDeTrabajoAsync`, renombrada a `NaceDondePuedeNacerUnaPreferenciaAsync`) y,
  detras, la de permisos de `PropuestaParaAplicarAsync`, que mandaba a un Empleado al "solo el Director". Con una sola
  arreglada el defecto seguia vivo para el Empleado. El configurador, el asistente y el analista siguen afuera.
- **OLV-034 (minor)** - `ConfiguradorTextos.DondeAplica` no tenia rama para `AlcanceRegla.Usuario` y la tarjeta decia
  "Donde aplica: -". Ahora estan los **seis** alcances escritos: el descarte deja de tragarse un valor del enum.
- **OLV-032 (trivial)** - `data-menciones` se emitia siempre, vacio. Se cierra de los dos lados: el atributo se arma
  completo o no existe (`HtmlString`), y en `site.js` un atributo sin URL ya no dispara pedido.

### El pendiente: tres criterios que iban a seguir BLOCKED
`ProveedorModeloSimulado` tiene **guion propio de chat libre** (solo Development, `Anthropic:Simulado`, costo cero), con
marcadores explicitos del pedido y nunca adivinando (leccion RT-M7-06). Cubre **CA-04.1 / CA-04.2** (llama a
`adjunto_leer` con un id de la nota de adjuntos de esa tarea), **CA-03.3** (propone **once** de un saque, para ver el
tope de 10 cortando la numero once) y **D-05** (dos menciones de agente no delegan: preguntan a cual, con las dos a la
vista; las menciones de configuracion pueden ser varias y no disparan la pregunta). El guion **agrega** caminos: sin
ninguno de sus marcadores el chat libre sigue contestando lo que contestaba, y eso esta afirmado como regresion.

### El grep de las dos formas (la leccion de A-10)
OLV-033 es el **molde inverso de R-A1**: no un `default` que traga el tipo nuevo, sino una **lista blanca de un valor**
que lo rechaza en silencio. Se grepearon las dos formas sobre `TipoTarea` y sobre los booleanos de familia:

- **Clase A (`default` / `_ =>` que lo tragan): 7 sitios de switch sobre `TipoTarea`, los 7 con rama explicita de
  `ChatLibre` - 0 pendientes.** (`PoliticaProponerRegla.Para`, `PropuestaReglaService.PuedeResolver`,
  `ProcesadorTareas` x3, `ServicioTareas.Armar...`, `SubtareasService.SubagentesPermitidos`.) Mas `RotulosTipoTarea`,
  que ya es una tabla sin `default` por OLV-029.
- **Clase B (igualdad / listas blancas de un valor que lo excluyen): 84 comparaciones por `TipoTarea`, 23 ya lo
  incluian y 61 lo excluian.** De esas 61, **5 eran del molde del defecto y se arreglaron** (2 de OLV-033 en
  `ReglaService`, 3 de OLV-030 en las vistas, estas ultimas por el booleano de familia y no por el enum). Las otras 56
  excluyen el chat libre **con razon** y se revisaron una por una: conectores, entregables, documentos de un cliente,
  conocimiento, destilado de memoria, tablero, informes, portal del cliente y las aprobaciones de nivel autor (las de
  una parte viven en la parte, que es `Trabajo`).
- **Declarado y no tocado** (son decisiones, no defectos, y ningun parte las pide): `ReglaService.Conversacion` y
  `OrigenAgente` no le dan al autor el enlace "ver la conversacion que la propuso" ni la leyenda "Propuesta de X"
  cuando el origen es un chat libre; `PropuestaReglaService.ListarPendientesParaMiAsync` no lista las propuestas del
  chat libre, igual que no lista las del analista ni las del configurador (cada una vive en su conversacion).

### Cambios por capa
- **Application**: `ClasesDeTarea` +2 funciones (`MuestraPartesYAprobaciones`, `OrigenDePreferenciaPersonal`);
  `TareaDetalleDto.MuestraPartesYAprobaciones` (derivada de `Tipo`, que ya venia poblado desde OLV-029).
- **Infrastructure**: `ReglaService` (las dos compuertas de OLV-033); `ProveedorModeloSimulado` (guion de chat libre).
- **Web**: `_Conversacion.cshtml` (partes y aprobaciones del turno, y la pastilla de propuestas), `Detalle.cshtml`
  (`_ScriptAprobaciones`), `_CuadroSeguimiento.cshtml` (atributo de menciones), `ConfiguradorTextos.DondeAplica`,
  `wwwroot/js/site.js` (tope por grupo + guarda de URL vacia).
- **Sin migracion EF, sin tocar ningun valor de M6, sin publicar nada** (artefacto 121 / version 147 intactos).

### Evidencia
- `dotnet build OlvidataAgentes.slnx` -> **Compilacion correcta**, 0 errores (advertencias preexistentes de NuGet y xUnit).
- `dotnet test tests/OlvidataAgentes.Tests` -> **1160/1160** (se partia de 1151; +9 tests nuevos en
  `M28ArreglosQaTests.cs`). Medido sin pipe, con el resumen completo a archivo.
- **OLV-033 verificado por el camino inverso:** revirtiendo solo el arreglo de `ReglaService`, el test nuevo falla con el
  **mensaje exacto** que reporto QA ("El configurador no crea ni cambia preferencias personales...").

### Pruebas minimas para QA
1. **OLV-030.** Chat libre con una mencion que deje el hilo en `EsperandoSubtareas`:
   `document.querySelectorAll('.ov-parte').length >= 1`, y la tarjeta tiene el enlace *Resolver* cuando la parte espera
   aprobacion. Las otras tres conversaciones de plataforma **siguen sin** tarjeta de parte.
2. **OLV-031.** Organizacion con **18** agentes usables: con la arroba sola, el menu dibuja **los dos** encabezados de
   grupo y las cuatro opciones de "Configurar" estan en el DOM y se alcanzan con las flechas.
3. **OLV-033.** Como **Empleado**, propuesta de alcance personal en su chat libre -> *Aplicar* funciona, la regla nace
   con alcance personal y la propuesta queda **Aplicada**. Repetir como Director sobre la suya. Y confirmar que en el
   **configurador** una preferencia personal sigue rechazada con el mismo mensaje.
4. **OLV-034.** La tarjeta de alcance personal dice una frase en *Donde aplica*, no una raya.
5. **OLV-032.** En la conversacion del analista, `document.querySelector('textarea').hasAttribute('data-menciones')`
   es **false** y la pestana de red no muestra ningun pedido a la pagina actual al tipear.
6. **Los tres criterios desbloqueados** (con `Anthropic__Simulado=true`): "Lee el archivo que te adjunte" con un adjunto
   -> paso con `adjunto_leer`; "dejame **once** propuestas de un saque" -> **10** tarjetas y el mensaje del tope en los
   pasos; "@agenteA @agenteB ..." -> **ninguna** tarea nueva y una respuesta que pide elegir, con los dos a la vista.

### Checklist de merge
- [x] Build 0 errores - tests 1160/1160 (de 1151)
- [x] Goldens de hash de contexto intactos (no se toco ningun prompt ni formato)
- [x] Sin migracion EF (ningun cambio de esquema)
- [x] Logica en services/helpers, nunca en controllers
- [x] Multi-tenant sin cambios; ningun `IgnoreQueryFilters()` sin nombre nuevo
- [x] `Mcp` y `Cli` sin tocar
- [x] Costo cero: ninguna llamada a la API real ni salida a internet; no se levanto la app
- [x] Nada publicado; ningun valor de M6 tocado; commit local, sin push
# M28 - Arreglo del lote 1 de QA (OLV-028 y OLV-029)

Estado: **aplicado 2026-10-02; pendiente de re-verificacion por QA; 1 commit local, sin push y sin deploy.** Repo
`C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `87530b2`. Entrada: partes de defecto del **lote 1 de M28**
(`6-qa.md`), CA-01.2 textual de `1-analista-funcional.md` y **R-A1** de `3-arquitecto-mvc.md`. **Sin migracion EF.**
**Los dos defectos quedan "aplicado, pendiente de re-verificacion": el cierre lo declara QA.**

### Escaneo de reutilizacion
`docs/patrones/cat_resumen.txt` -> sin match (es un arreglo de dos defectos sobre codigo propio, no un patron nuevo).
Dentro del repo **si** se reutilizo, y es lo que decidio la forma del arreglo: la condicion del menu de M27
(`VeEnMenu` = etapa + rol, una tabla por opcion) y la consulta de publicados del catalogo de Agentes
(`AgentesPlataforma.CardsAsync`), que ya tenia escrita la condicion de "publicado" correcta.

### OLV-028 - era de las cuatro conversaciones, no del chat libre
`VeEnMenu` era **etapa y rol**, y la disponibilidad del artefacto la chequeaban la pantalla de cada conversacion
-que contesta "Todavia no esta disponible."- y el catalogo de Agentes, **nunca el menu**. Eso vale igual para
*Automatizar lo que repetis*, *Configurar conversando* y *Repartir trabajo conversando*: el chat libre no estreno el
agujero, lo hizo visible. **Un solo arreglo para las cuatro.**

La tercera dimension entra **con la misma forma** que el rol en M27 -una tabla por opcion, consultada en los permisos-
y no como un `if` en el layout:

| Capa | Que se hizo |
|---|---|
| **Application** | `IDisponibilidadPlataforma` + la tabla `AgentePorOpcion` (`OpcionMenu` -> slug del agente de plataforma), al lado de `EtapasEntrega.SoloDirector` y por el mismo motivo. `IPermisosOrganizacion.VeEnMenuAsync(opcion, ct)`: la condicion completa, que es `VeEnMenu` **mas** la disponibilidad. `VeEnMenu` queda intacta como la parte pura (etapa + rol), que es el contrato que ya afirman los tests de etapas. |
| **Infrastructure** | `DisponibilidadPlataforma` (Services/Nucleo): **una consulta por request**, por los cuatro slugs, memorizada en el alcance de la request. No se usan los cuatro `DisponibleAsync` de los services porque serian cuatro consultas, una por opcion. `PermisosOrganizacion.VeEnMenuAsync` corta antes de tocar la base para el staff y para lo que la etapa ya oculta. |
| **Web** | `MenuOrganizacion.Secciones` -> `SeccionesAsync` (la visibilidad de la seccion se sigue calculando una vez, de sus items). `_Layout.cshtml`: `await MenuOrganizacion.SeccionesAsync(Permisos)`. Una condicion por item, en un solo lugar. |
| **Tests** | `MenuLateralTests` +1 (`Sin_version_publicada_el_menu_no_ofrece_ninguna_de_las_cuatro_conversaciones`): sin publicar no esta ninguna de las cuatro, publicadas aparecen, y el filtro por rol sigue mandando. Helper `PublicarConversacionesAsync()`, que necesitan los tres tests que esperan el menu completo: **el escenario base no publica ninguno de los cuatro, que es el estado de hoy del repo.** |

### OLV-029 - el `default` de la vista (R-A1, variante de vista)
Los dos mapeos que nombro QA eran cadenas ternarias con `else` final de default, y habia **dos mas de la misma
familia** que el grep encontro. Los cuatro se arreglaron contra **una sola tabla**:

1. `Views/Tareas/Detalle.cshtml:15` - el chat libre se titulaba "Configuracion de reglas".
2. `Views/Tareas/Index.cshtml:219` (JS) - el chat libre **y el analista** caian al rubro tecnico "plataforma".
3. `TareaDetalleDto.TieneTarjetasDeTrabajo` - lista por inclusion sin el chat libre: `ServicioTareas` ya le cargaba
   `PropuestasTrabajoPorPaso` desde la tanda 1b, pero la vista no cargaba `_ScriptPropuestasTrabajo`, asi que
   **no se podia aplicar ninguna tarjeta de trabajo de un chat libre**. Es el mismo final que el defecto 1 de la
   tanda 1b: la tarjeta se guardaba bien y no servia de nada.
4. `Views/Tareas/_Conversacion.cshtml:17` - el contador "sin resolver" sumaba una sola familia segun el tipo; al chat
   libre no le contaba las de trabajo. Se elimino la ternaria: las dos cuentas siempre (en una tarea de trabajo el
   termino de trabajo es 0).

| Capa | Que se hizo |
|---|---|
| **Application** | `RotulosTipoTarea` (Helpers): la tabla de los cuatro tipos de plataforma, **sin `default`** -un tipo que no es de plataforma devuelve `null` y la vista muestra el rubro del agente- y la misma tabla con el nombre del enum como clave para el listado en JavaScript. `TareaDetalleDto.Tipo` (el tipo tal cual, para que el rotulo no se deduzca de los booleanos). `TieneTarjetasDeTrabajo` suma `EsChatLibre`. |
| **Infrastructure** | `ServicioTareas`: `Tipo = tarea.Tipo` en el detalle. |
| **Web** | `Detalle.cshtml` y `_Conversacion.cshtml` sin ternarias; `Index.cshtml` sirve la tabla al script (`rotulosPlataforma`) y el render hace `rotulosPlataforma[row.tipo] || row.rubroSlug`. |
| **Tests** | `RotuloConversacionesTests` (nuevo, +2): uno exige **rotulo para todo tipo que `ClasesDeTarea.EsDePlataforma` considere de plataforma** -la quinta conversacion sin su rotulo rompe un test- y el otro **renderiza** `/Tareas/Detalle` de un chat libre real y afirma que dice "Chat libre" y **no** "Configuracion de reglas". Verificado rojo sin el arreglo. |

### Evidencia
- `dotnet build OlvidataAgentes.slnx` -> **0 errores**, 0 advertencias de compilador (solo las NU1510/NU1902 preexistentes).
- `dotnet test tests/OlvidataAgentes.Tests` -> **1151/1151 verdes** (1148 + 3 nuevos), sin pipe (memoria "Medir sin pipe").
- Los dos tests nuevos se verificaron **en rojo** revirtiendo el arreglo correspondiente.

### Pruebas minimas para QA
1. **OLV-028, re-verificacion.** Con el chat libre en Borrador (estado de hoy): el menu **no** ofrece "Chat libre", y
   `/ChatLibre` por URL sigue contestando "Todavia no esta disponible." con el cuadro deshabilitado. Mismo chequeo con
   las otras tres: **ninguna de las cuatro** se ofrece si su agente no tiene version publicada.
2. Publicar el chat libre y confirmar que la opcion **aparece**, que al Empleado le aparece (es de cualquier miembro) y
   que *Configurar* / *Repartir* **no**.
3. **OLV-029, re-verificacion.** Detalle de un chat libre: el titulo y el encabezado dicen "Chat libre". En `/Tareas`,
   la fila de un chat libre dice "Chat libre" y la de un analista, "Automatizacion" (antes: "plataforma").
4. **Lo que el arreglo 3 destapa:** en un chat libre con tarjetas, los botones de las tarjetas de **trabajo**
   (programacion, agente propio, tarea, asignacion) ahora **existen y aplican**. Antes la tarjeta se veia y el boton no
   hacia nada porque el script no se cargaba. Vale re-correr HU-04 mirando los botones.
5. **Regresion del menu:** con todo publicado, el menu tiene las 26 opciones de siempre y ninguna seccion queda con el
   encabezado solo, en las tres etapas y con los dos roles.

### Checklist de merge
- [x] Build 0 errores, tests 1151/1151
- [x] Sin migracion EF (ninguna entidad ni propiedad persistida nueva; `TareaDetalleDto.Tipo` es un DTO)
- [x] Logica en Application/Infrastructure; el layout no decide permisos
- [x] Una consulta por request para la disponibilidad, no una por opcion ni por item del menu
- [x] M6 (tope de gasto) sin tocar; nada publicado (el agente sigue en Borrador, artefacto 121 version 147)
- [x] Multi-tenant sin cambios; ningun `IgnoreQueryFilters()` sin nombre
- [x] `Mcp` y `Cli` sin tocar; costo cero (ninguna llamada a la API real)

### Donde el brief no alcanzo (declarado, no inventado)
- **La tercera superficie sigue con el hueco.** `Views/PrimerosPasos/Index.cshtml` usa `VeEnMenu` (~25 veces) y por lo
  tanto puede ofrecer un acceso a una conversacion sin publicar. CA-01.2 nombra el menu y el catalogo, asi que no se
  toco: cambiarlo mueve los pasos del camino de arranque de M26 y eso es una decision funcional, no un arreglo.
- **El chat libre no esta en el catalogo de Agentes.** `AgentesPlataforma.Presentaciones` tiene tres entradas, no
  cuatro: el criterio se cumple de forma trivial (no se ofrece), pero *ofrecerlo publicado* es alcance que nadie pidio.
# M28 — El chat libre (TANDA 2: la pantalla. Última)

Estado: **tanda 2 implementada 2026-10-02; pendiente de QA; 1 commit local, sin push y sin deploy.** Repo
`C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `0c16930`. Entrada: pasos **7 y 8** del orden de
implementación de `3-arquitecto-mvc.md` (A-05, A-05b, A-08) + «Diseño M28» de `2-disenador-funcional.md`
(D-01, D-03, D-06, D-08, P1) + instrucción `38` completa. **Sin migración EF** (tercera vez: no se agregó ninguna
entidad ni ninguna propiedad persistida).

### Escaneo de reutilización
`docs/patrones/cat_resumen.txt` → **PAT-029** otra vez, y por D-02 se reutilizó entera: enviado el primer mensaje se va
a `Tareas/Detalle`, la conversación compartida, sin copiar un renglón de `_Conversacion` ni de los scripts de `Detalle`.
Dentro del repo se copió el molde de `data-autosize` para el autocomplete (mismo patrón: comportamiento una vez en
`site.js`, un atributo por vista) y la lista blanca del CSP para el CDN, que el tablero de M16 ya había dejado resuelta
(`cdn.jsdelivr.net` ya estaba, así que la pieza 3D **no tocó el CSP**). **Sin antecedente** en ningún proyecto para:
autocomplete de menciones y carga diferida de una librería 3D — son lo único construido desde cero.

### Cambios por capa

| Capa | Qué se hizo |
|---|---|
| **Application** | `MencionDto(Mencion, Nombre, Detalle, Grupo)` y `PastillaMencionDto` (las cuatro pastillas, con lo que escribe cada una) · `MensajesChatLibre` suma los dos rótulos de grupo (`Agentes` / `Configurar`) y las cuatro menciones de configuración como constantes · `IChatLibre.MencionablesAsync()`. |
| **Infrastructure** | `ChatLibre` deja de ser una clase de un método: implementa `MencionablesAsync` **pidiéndole la lista al modo abierto de `SubagentesPermitidosAsync`** con un `ContextoHerramienta` de chat libre. No hay consulta propia (A-08). Agrega el grupo fijo de configurar y pasa de código a texto (`ComoMencion`). |
| **Web** | `ChatLibreController.Mencionables` (GET, JSON, **sin un solo parámetro**) · `Views/ChatLibre/Index.cshtml` reescrita (P1) · `Views/Tareas/_CuadroSeguimiento.cshtml`: `data-menciones` **solo si `EsChatLibre`**, más su placeholder y su ayuda · `wwwroot/js/site.js` +212 líneas: el autocomplete compartido · `wwwroot/js/chat-libre-3d.js` (nuevo) · `wwwroot/css/site.css` +~170 líneas: arranque, pieza plana, pastillas y menú de menciones, **solo tokens `--ov-*`**. |
| **Núcleo** | `chat-libre.md`: `mis_automatizaciones` en el frontmatter y la regla de mirarla antes de proponer una programación o un agente propio (era el pendiente 2 de la tanda 1b) · `13-chat-libre.yml`: los dos casos de programación y de agente propio ahora la ofrecen y verifican que la use. **Nada publicado: el agente sigue en Borrador.** |
| **Tests** | `ChatLibreTests` +2: el autocomplete ofrece **exactamente** los agentes que la herramienta autoriza (comparación agente por agente, y ninguna mención es un código interno), y el grupo *Configurar* está **aunque no haya ningún agente**. El test de las cuatro herramientas afirma además `mis_automatizaciones`. `EntornoM28.HerramientasChatLibre` refleja el frontmatter nuevo. |

### A-08: una sola lista, y la forma más fuerte de garantizarlo
No se escribió una consulta para la pantalla ni se llamó a `IAgentesDisponiblesQuery` desde el controller. El
autocomplete le pide la lista **a la misma operación que autoriza** (`SubagentesPermitidosAsync`, modo abierto), con un
`ContextoHerramienta` de `TipoTarea.ChatLibre`. Así no hay dos consultas que puedan divergir: hay **una**, y el test las
compara por los dos caminos. `TareaId: 0` porque todavía no hay tarea, y está comentado para que, si algún día el modo
abierto usa la tarea, este método tenga que cambiar en vez de seguir funcionando de casualidad.

### D-04: la mención es texto, y se verifica que lo sea
Lo que se inserta es `@slug` en plano. Los códigos internos (`b-<rubro>/<slug>` para los de Olvidata, `o-<id>` para los
de la empresa) **viajan al cliente nunca**: un agente de la empresa no tiene slug propio, así que su mención se arma de
su **nombre** (sin acentos, en minúsculas, con guiones) y jamás de su id. Hay un assert que afirma las dos cosas: que
toda mención matchea `^[a-z0-9][a-z0-9/-]*$` y que ninguna coincide con un código de la herramienta. Cuando dos rubros
repiten un slug, la mención lleva el rubro adelante (`rubro/slug`) para que una sola palabra no señale a dos agentes.

### D-01 / RD-02: la pieza se desmonta, y el desmontaje es lo primero que se escribió
Tres compuertas antes de pedir el script, en el orden de A-05: `prefers-reduced-motion`, contexto WebGL (preguntado con
un canvas descartable, no por user agent) y la pantalla montada. Si alguna falla, **la librería no se descarga**. El
`import()` está en `try/catch` y su fallo es silencioso. Al enviar el primer mensaje: `cancelAnimationFrame`,
`dispose()` de las dos geometrías y los dos materiales, `renderer.dispose()`, y el canvas **fuera del DOM** junto con su
contenedor. **Nunca `display:none`.** De paso, el bucle también se corta con la pestaña en segundo plano. La pieza es un
icosaedro en alambre que **no recibe ni muestra ningún dato**: no hay vía por la que un dato de la organización llegue
al script del CDN.

### D-08 / RD-01: las pastillas escriben menciones
Las cuatro pastillas (`PastillaMencionDto.Todas`) no llevan texto de pedido: dejan `@`, `@regla `,
`@tarea-programada ` o `@instructivo ` y el cursor al final, y disparan un evento `input` para que el autocomplete se
abra. La que enseña el mecanismo entero es la primera, que deja la arroba sola y abre el menú con los dos grupos.

### RD-04: el menú se abre hacia arriba cuando no hay lugar
Anclado al **cuadro de escribir** y no al caret, a propósito: un menú pegado al caret de un `textarea` se calcula con un
clon invisible y se corre con cada reflow. Se mide `window.innerHeight - caja.bottom` contra `caja.top` y, si abajo no
entra y arriba sí, se abre hacia arriba con `data-lado="arriba"`. Se reposiciona en `resize` y en `scroll`.

### Evidencia
- `dotnet build OlvidataAgentes.slnx` → **0 errores** (15 advertencias, todas preexistentes). Las vistas compilan en el
  build, así que el build limpio también valida los dos `.cshtml`.
- `dotnet test tests/OlvidataAgentes.Tests` → **1148 de 1148, 0 con error, exit 0** (eran 1146; +2).
- Los goldens de contexto **no se tocaron**: el formato 6 no cambió y sumar una herramienta al frontmatter no entra en
  el hash del contexto.
- No se levantó la app ni se probó por navegador: la verificación a 1440 y 390, en claro y oscuro, es de QA.

### Pruebas mínimas para QA (se suman a las 19 de las tandas 1 y 1b)
20. **CA-02.1** En el arranque, escribir `@`: aparece el menú con **dos grupos**. Flechas para navegar, `Enter` y `Tab`
    para elegir, `Escape` para cerrar. `Ctrl+Enter` tiene que **enviar** aunque el menú esté abierto.
21. **CA-02.2 / A-08** Comparar lo que ofrece el menú con lo que lista `/Agentes` para esa persona: ni uno más. Un
    agente personal de otra persona y un agente sin versión publicada **no** aparecen. Elegir uno, enviar, y confirmar
    que la herramienta **no lo rechaza** (si lo rechaza, divergieron las listas: es R-A2).
22. **HU-03** Con la licencia del rubro revocada, escribir `@`: el grupo **Configurar** sigue estando con sus cuatro
    opciones. Es el caso que prueba que el grupo que enseña no depende de ninguna licencia.
23. **D-08 / RD-01** Tocar cada pastilla: tiene que **escribir una mención** y dejar el cursor listo. Ninguna puede
    mandar una pregunta armada ni enviar el formulario.
24. **RD-04** A **390 px**, con el teclado del teléfono abierto, escribir `@`: el menú se abre **hacia arriba** y no
    queda tapado. Verificar en navegador real, con scroll de verdad (no con captura de página completa).
25. **CA-07.2 / RD-02** Con el monitor de rendimiento: abrir el arranque, ver que `three.module.js` se pide **después**
    del primer render. Enviar el primer mensaje y confirmar que en `Tareas/Detalle` **no queda ningún canvas**, que no
    hay frames de WebGL y que la memoria del contexto se liberó. Mirar la pantalla no alcanza.
26. **CA-07.3 / HU-08** Con `prefers-reduced-motion: reduce`: `three.module.js` **no se pide** (ni un byte), no hay
    movimiento, y la pantalla está completa y usable.
27. **CA-07.5** Bloquear `cdn.jsdelivr.net` en el navegador: la pantalla queda con el anillo plano, **sin hueco y sin
    un solo cartel de error**. Lo mismo con WebGL deshabilitado.
28. **CA-07.4** A 1440 y 390, en tema claro y oscuro: el menú de menciones, las pastillas y la pieza. Buscar cualquier
    color que no se invierta con el tema (sería un literal que se escapó).
29. **D-03** En un chat libre ya abierto, en `Tareas/Detalle`, escribir `@` en *Seguir conversando*: el autocomplete
    tiene que funcionar igual. Y en una conversación del **configurador**, del **asistente** o del **analista**: ahí
    `@` **no** abre nada (el atributo está solo en el chat libre).
30. **D-02** Confirmar que el primer mensaje lleva a `Tareas/Detalle` y que el hilo es el compartido, con su barra de
    contexto, su costo y su pastilla de *Ver pasos*.
31. **(f)** Pedir una tarea programada que ya exista: el agente tiene que **mirar `mis_automatizaciones`** (se ve en
    *Ver pasos*) y decir que ya la tiene, en vez de proponerla de nuevo.

### Checklist de merge
- [x] Build limpio y suite verde (1148).
- [x] Sin migración EF.
- [x] A-08 con un test que compara las dos listas agente por agente.
- [x] D-04 con un test que afirma que ninguna mención es un código ni un id.
- [x] D-06 con un test que afirma el grupo *Configurar* sin ningún agente disponible.
- [x] Solo tokens `--ov-*` en el CSS nuevo (revisado a mano, sin un literal).
- [x] El autocomplete vive **una vez** en `site.js` y se enciende con un atributo.
- [x] El CSP no se tocó: `cdn.jsdelivr.net` ya estaba en la lista blanca.
- [x] La versión del 3D va **fija** en la URL, no `latest`.
- [x] Nada publicado en el núcleo (el agente sigue en Borrador).
- [x] Commit local, sin push.
- [ ] QA de las tandas 1, 1b y 2 (las 31 pruebas), **en navegador real**.
- [ ] Publicación del agente del núcleo: `importar` → `evaluar --aprobada` → `publicar` (lo decide Joaquín).

### Donde el brief no alcanzó (declarado, no inventado)
1. **La «casilla de internet» del compositor no se implementó.** El diseño la pide en P1, pero el motor no tiene por
   dónde: `ResolvedorHerramientas` calcula `busquedaOfrecida = trabajo && …`, así que **ninguna** conversación de
   plataforma la ofrece hoy (ni el configurador, ni el asistente, ni el analista), e `IniciarChatLibreAsync` /
   `IniciarPlataformaAsync` no tienen el parámetro. Ponerla son cuatro switches del motor más un flag que se persiste, y
   además es una decisión de costo (USD 10 cada 1.000 búsquedas) sobre una conversación que usa **cualquier miembro**.
   La tanda 2 era la pantalla y el motor estaba cerrado y verde: **no se tocó**. Si se la quiere, es una tanda chica de
   motor con su propio test por switch, no un renglón de la vista.
2. **La versión de `three` está fija en `0.160.0` y no se verificó contra el CDN** (no se salió a la red en esta
   corrida). Es un número elegido por ser una versión estable conocida con `build/three.module.js`. **Antes del primer
   despliegue hay que abrir la URL una vez**: si no existe, el `catch` silencioso hace que la pieza no aparezca nunca y
   nadie se va a enterar, que es exactamente el riesgo de un fallo silencioso bien hecho.
3. **Las pastillas no tenían texto en «Textos que importan».** El diseño fija el encabezado, la bajada, el rótulo del
   compositor y los dos mensajes de mención, pero no las pastillas. Se escribieron cuatro respetando D-08 (ninguna es
   una pregunta): *Pedirle un trabajo a un agente*, *Dejar armada una regla*, *Automatizar algo que repito* y *Escribir
   los pasos de una tarea*. Son invento del implementador: si no gustan, cambian en un solo lugar
   (`PastillaMencionDto.Todas`).
4. **«Mención que no resolvió» y «dos menciones» son estados del agente, no de la pantalla.** Los dos están en el prompt
   del núcleo desde la tanda 1 y la pantalla no los dibuja: salen como texto del agente en el hilo compartido. Si se los
   quiere como una pieza de maqueta propia, hace falta que el motor marque el turno, y eso no estaba pedido.
5. **La pieza 3D no se vio nunca andando.** No se levantó la app (por consigna). Lo que está verificado es el código:
   las tres compuertas en orden, el `try/catch`, el desmontaje completo y que el CSP ya permite el CDN. **Que se vea
   linda es de QA**, y es lo único de M28 que se puede sacar sin que el módulo deje de funcionar.
# M28 — El chat libre (TANDA 1b: CU-03, A-08 y A-09)

Estado: **tanda 1b implementada 2026-10-02; pendiente de QA; 1 commit local, sin push y sin deploy.** Repo
`C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `d7ee4c8`. Entrada: **A-07, A-08 y A-09** de
`3-arquitecto-mvc.md` (agregadas después de la tanda 1 para cerrar el hueco que la tanda 1 declaró) + CU-03 / RF-05 /
CA-03.x del análisis. **Sigue siendo solo motor: ni una vista, ni CSS, ni 3D.**

### Escaneo de reutilización
`docs/patrones/cat_resumen.txt` → sigue siendo **PAT-029**; ningún patrón nuevo y nada traído de otro repo. Se reusó el
molde completo del analista de M15: sus `TiposPermitidos`, su `PoliticaProponerRegla`, y —lo que más importó— la regla de
permisos que ya tenía escrita (*el autor resuelve lo suyo, quien dirige lo que alcanza a la empresa*). El chat libre no
estrenó ninguna regla de permisos: entró en la que ya existía.

### Sin migración EF
**Confirmado otra vez, no hay migración.** No se agregó ninguna entidad ni ninguna propiedad persistida: todo lo que se
tocó son listas blancas de `TipoTarea`, una política y un campo `init` de un record en memoria (`SolicitudModelo`).

### Cambios por capa

| Capa | Qué se hizo |
|---|---|
| **Application** | `PoliticaProponerRegla.Para(ChatLibre)` **deja de ser `null`**: alcances `{Usuario, Organizacion}`, `ClienteYAgenteDelContexto: false`, `EmpresaYAreaSoloDirector: **false**`, `MaxPorPaso: 10` · `Descripcion()` arma los alcances **desde el conjunto** en vez de una frase fija (`AlcancesEnPalabras()`) · `SolicitudModelo.EsChatLibre` (marca explícita, solo para el proveedor simulado). |
| **Infrastructure** | `HerramientaProponerRegla.TiposPermitidos` += `ChatLibre` · `HerramientaProponerInstructivo.TiposPermitidos` += `ChatLibre` · `HerramientaConfiguradorBase.TienePermiso` suma `ChatLibre` a la rama de «miembro activo» · `HerramientaAnalistaBase.EjecutarAsync` suma `ChatLibre` a la lista blanca y a la consulta de «la conversación es suya» (abre `proponer_programacion` y `proponer_agente_empresa`) · **`PropuestaReglaService`**: `ChatLibre` en las 8 compuertas de visibilidad y de permiso, con la misma regla del analista · **`PropuestaTrabajoService`**: ídem en las 6 suyas, y la bandera `esAnalista` pasó a llamarse `resuelveElAutor`, que es lo que de verdad significa · `ServicioTareas`: el detalle del chat libre ahora carga `PropuestasTrabajoPorPaso` · `ProcesadorTareas`: pasa `EsChatLibre` en la solicitud · `ProveedorModeloSimulado`: un chat libre no entra más al guion de configuración. |
| **Web** | `TareasController.MostrarTipo` pasa de `EsDirector \|\| EsStaff` a **`EsMiembro \|\| EsStaff`** (A-09). Es el único cambio de Web, y no toca ninguna vista. |
| **Núcleo** | `chat-libre.md`: frontmatter con `herramientas: [proponer_regla, proponer_instructivo, proponer_programacion, proponer_agente_empresa]` (antes no tenía la clave) y **sección 3 reescrita**: la tabla de las cuatro cosas, el alcance más chico, los pasos que no son una regla, el tope de 10 y qué no puede elegir · `13-chat-libre.yml`: de 6 a **12 casos** (el de «una orden no es un recuerdo» se invirtió: ahora tiene que dejar la tarjeta y **no** usar `recordar`; 6 nuevos para las cuatro cosas, el alcance mínimo, «nada cambió hasta el botón» y «no inventa un área ni un cliente»). **Nada publicado: el agente sigue en Borrador.** |
| **Tests** | `ChatLibreTests`: se **invirtió** el test del hueco (`Todavia_no_se_proponen_reglas...` → `La_politica_del_chat_libre_propone_lo_personal_y_la_empresa_tambien`) y se sumaron 5: las cuatro herramientas ofrecidas y las de repartir trabajo no; el turno con las cuatro tarjetas y **cero filas nuevas**; el Empleado que propone para la empresa, la ve y recibe `SinPermiso` al aplicar; la propuesta de un chat ajeno; y el filtro por tipo del Empleado. `EntornoM28.HerramientasChatLibre` refleja el frontmatter nuevo. |

### A-07: qué se abrió y qué no, con el motivo
- **Dos alcances, no seis.** `{Usuario, Organizacion}`. Área, agente y cliente piden un id que sale de
  `estructura_empresa` o de `clientes_buscar`, y el chat libre **no recibe ninguna de las dos**: ofrecerlos sería
  invitar al modelo a inventar un id, que es la misma clase de error que un esquema que miente sobre lo que acepta
  (commit `5c3bd9d`). La preferencia personal es **el default**; para configurar con ese detalle, el configurador.
- **`EmpresaYAreaSoloDirector: false`, a propósito.** La política decide **qué** se propone y nunca **quién** aplica. Una
  propuesta de alcance de empresa se registra la haga quien la haga, y el Director obligatorio lo pone
  `PropuestaReglaService` al aplicar. No se duplica el permiso en dos lugares.
- **`proponer_asignacion` y `proponer_prueba` NO se sumaron.** Repartir trabajo es el asistente (M7/M15) y está fuera
  del alcance declarado de M28.
- **`proponer_instructivo` y `proponer_agente_empresa` siguen rechazando «empresa» a quien no dirige ya al proponer.** Es
  la conducta de M15, compartida y sin tocar: no es una decisión nueva del chat libre. CA-03.2 se verifica por
  `proponer_regla`, que es donde A-07 pidió explícitamente que la propuesta se registre igual y el rol se chequee al
  aplicar.

### Dos defectos que A-07 destapó (y que un `default` habría dejado pasar en silencio — R-A1)
1. **Las tarjetas del chat libre eran invisibles.** El `switch` de visibilidad de `PropuestaReglaService.ListarPorTareaAsync`
   tiene `_ => false`: una propuesta de un chat libre se guardaba perfecto y **no la veía nadie, ni su autor**. Lo mismo
   en `PropuestaTrabajoService`, que filtra por tipo en la consulta. Es el peor final posible para una propuesta, y no
   daba ningún error.
2. **Nadie podía aplicar nada.** `PuedeResolver` devolvía `EsDirector` para todo tipo que no fuera `Trabajo` ni
   `Analista`, así que un Empleado no podía aplicar ni **su propia** preferencia en su propio chat.
   Los dos se arreglaron metiendo el chat libre en la rama del analista, que ya tenía la regla correcta escrita.

### Un tercero, de desarrollo: el simulado confundía el chat libre con el configurador
Desde que el chat libre declara `proponer_instructivo`, el `ProveedorModeloSimulado` lo reconocía como una conversación
de configuración (lo detecta por los nombres **exactos** de esas herramientas) y un chat libre en dev pasaba a contestar
como el configurador, perdiendo su propio guion. Se resolvió con una **marca explícita** en la solicitud
(`SolicitudModelo.EsChatLibre`), igual que el guion de M8 y por la misma lección (RT-M7-06: marcador propio, nunca
adivinar por los nombres de las herramientas). El proveedor real la ignora.

### A-08: confirmado, no hubo nada que cambiar
La tanda 1 ya había elegido **A-04 con el rubro en el código** (`b-<rubro>/<slug>`), una sola lista, y
**A-03 queda superada en ese punto**. Queda anotado para la tanda 2, que es donde importa:

> **El autocomplete de menciones de la pantalla se arma contra `IAgentesDisponiblesQuery`**, nunca contra
> `agentes_disponibles`. Misma fuente y mismos códigos que la herramienta que autoriza. Si divergieran, el síntoma sería
> el peor posible: la pantalla ofrece un agente que la herramienta después rechaza (R-A2). El test
> `La_pantalla_y_la_herramienta_resuelven_los_agentes_con_la_misma_consulta` ya corre la misma query por los dos caminos.

Y para las propuestas: el código de agente de `proponer_programacion` y de `proponer_agente_empresa` sale de
`subagentes_listar`, que en el chat libre es **esa misma** consulta. Una sola lista, también para configurar.

### A-09: se amplió filtrar, nunca ver
`TareasController.MostrarTipo` ahora incluye a todo miembro. Lo que **no** cambió es una línea de
`ServicioTareas.Visibles()`: un Empleado sigue viendo solo sus tareas. El test
`El_empleado_filtra_por_tipo_y_sigue_viendo_solo_sus_tareas` afirma las dos mitades en el mismo caso: encuentra el chat
**suyo** y **no** aparece el de Martín, con el filtro ya disponible.

### Evidencia
- `dotnet build OlvidataAgentes.slnx` → **0 errores** (15 advertencias, todas preexistentes).
- `dotnet test tests/OlvidataAgentes.Tests` → **1146 de 1146, 0 con error, exit 0** (eran 1141; −1 invertido, +6 nuevos).
- Los 6 goldens **no se tocaron** (`Descripcion()` da el mismo texto, letra por letra, para las políticas de antes: hay
  un assert de regresión que lo afirma).
- No se levantó la app ni se probó por navegador: eso es de QA.

### Pruebas mínimas para QA (se suman a las 10 de la tanda 1)
11. Como **Director**, en un chat libre: contar cómo se trabaja, cómo se hace una tarea paso por paso, qué se repite
    todos los meses y que ningún agente conoce el método. Tienen que aparecer las **cuatro tarjetas**. Antes de tocar
    ningún botón, mirar `/Reglas`, `/Instructivos`, `/Programaciones` y `/Agentes`: **no tiene que haber nada nuevo**.
12. Aplicar **una sola** tarjeta y volver a mirar: solo esa existe; las otras tres siguen pendientes.
13. Como **Empleado**, pedir algo «para toda la empresa». La tarjeta tiene que **aparecer** y **sin botón**; forzando el
    POST de aplicar, 403 y nada guardado. Después, el Director de esa organización la aplica y recién ahí nace.
14. Como **Empleado**, pedir una preferencia propia («a mí dame siempre viñetas»): esa sí la puede aplicar él.
15. Pedirle una regla «para el área de Impuestos» o «para Panadería Norte»: tiene que decir que no puede elegir un área
    ni un cliente y mandar a *Configurar conversando*. **No** tiene que inventar un id.
16. Decirle «de ahora en más hacelo así»: tiene que dejar una **regla propuesta** y **no** anotarlo en memoria.
17. Como **Empleado**, en `/Tareas`: el filtro **Tipo** ahora se ve. Filtrar por «Chat libre» y encontrar los suyos.
    Después, entrar por URL al chat de otro Empleado: **404** (el filtro no amplió lo que ve).
18. `Aplicar todas` en un chat libre de un Empleado con tarjetas mezcladas (una personal y una de empresa): tiene que
    aplicar **solo la personal** y dejar la de empresa para quien dirige.
19. Con el **modelo simulado** (`Anthropic__Simulado=true`), abrir un chat libre y comprobar que **no** contesta como el
    configurador (es el defecto de desarrollo que se arregló con `EsChatLibre`).

### Checklist de merge
- [x] Build limpio y suite verde (1146).
- [x] Sin migración EF.
- [x] CA-03.1 con un test que cuenta filas en las **cuatro** tablas.
- [x] CA-03.2 con un test que afirma que la tarjeta **se ve** y que aplicar da `SinPermiso` sin guardar nada.
- [x] CA-03.3 (`TopePropuestas` = 10) afirmado contra la política, no solo contra la constante.
- [x] CA-03.4: las cuatro cosas, una de cada familia, en un solo turno.
- [x] A-09 con un test que afirma las dos mitades (filtra más, ve lo mismo).
- [x] Ningún valor de M6 tocado.
- [x] Nada publicado en el núcleo.
- [x] Commit local, sin push.
- [ ] QA de la tanda 1 y de la 1b.
- [ ] Tanda 2 (pasos 7 y 8), con A-08 como regla de arranque del autocomplete.

### Donde el brief no alcanzó (declarado, no inventado)
1. **A-07 nombra la política pero no enumera los alcances.** Dice «alcance personal por defecto» y «empresa se puede
   proponer igual», y no menciona área, agente ni cliente. Se resolvió por el camino conservador —solo esos dos— porque
   el chat libre no tiene con qué obtener un `area_id` ni un `cliente_id`. **Si se quisieran los seis alcances, hay que
   sumarle `clientes_buscar` y `estructura_empresa` al chat libre**, y eso es una decisión de alcance, no un renglón.
2. **`mis_automatizaciones` quedó afuera.** El analista la usa *siempre antes de proponer*, para no proponer de nuevo
   algo que ya existe. Para instructivos el chat libre tiene `instructivos_listar` y alcanza, pero **para programaciones
   y agentes propios no tiene con qué chequear duplicados**. El brief nombró cuatro herramientas y se respetaron las
   cuatro; sumarla es una línea en el frontmatter el día que se decida.
3. **El simulado no tiene guion propio de las propuestas del chat libre.** Con `EsChatLibre` ya no se confunde con el
   configurador, pero tampoco scripta las cuatro tarjetas: en dev esas se prueban con el modelo real o con los tests
   guionados. No se inventó un guion nuevo por estar fuera del alcance.
# M28 — El chat libre (TANDA 1: solo el motor)

Estado: **tanda 1 implementada 2026-10-02; pendiente de QA; 1 commit local (`d7ee4c8`), sin push y sin deploy.** Repo
`C:\Sistemas\Olvidata Agentes Multi-rubro`, commit base `5c3bd9d`. Entrada: análisis M28 (6 CU, 30 CA), diseño
(D-01..D-09, P1..P4) y arquitectura (A-00..A-06, R-A1..R-A6, orden de implementación pasos 1 a 8). Gate: definiciones 1,
2 y 3 aprobadas; presupuesto omitido (proyecto personal). **Alcance de esta tanda: pasos 1 a 6.** Los pasos 7 (vista de
arranque, CSS, autocomplete en `site.js`) y 8 (pieza 3D) son la tanda 2.

### Escaneo de reutilización
`docs/patrones/cat_resumen.txt` → **PAT-029** (conversación multi-turno reanudable con contexto congelado), de este mismo
proyecto, como anticiparon el diseñador y el arquitecto. **Ningún patrón nuevo y nada traído de otro repo:** ningún otro
proyecto del estudio tiene conversación con un modelo. Del propio repo se reusó el molde entero del analista de M15
(`AnalistaAutomatizaciones`, `AnalistaController`, `AnalistaAutomatizacionesTests`), el render genérico de contexto de
plataforma (`ArmarPlataformaAsync`, que **no se tocó**) y todo el camino de delegación de M7a.

### Sin migración EF
**Confirmado, no hay migración.** `TareaAgente.Tipo` no tiene línea en `TareaAgenteConfiguration`, cae en la convención
de EF para enums y el snapshot lo guarda como `int`. `dotnet ef migrations add` no se corrió y no hace falta.

### Cambios por capa

| Capa | Qué se hizo |
|---|---|
| **Domain** | `TipoTarea.ChatLibre = 6`, con el comentario de por qué no lleva migración y de que el riesgo son los switches con `default`. |
| **Application** | `ClasesDeTarea.EsDePlataforma` suma el chat libre (**la palanca de A-01**) · `IConstructorContexto.FormatoContextoChatLibre = 6` + `ArmarChatLibreAsync` · `IChatLibre` (`SlugChatLibre = "chat-libre"`, `DisponibleAsync`) · **`IAgentesDisponiblesQuery` nueva** (A-03b) · `MensajesChatLibre` · `OpcionMenu.ChatLibre` (etapa `PrimerosPasos`, **fuera** de `SoloDirector`) · `IPermisosOrganizacion.PuedeUsarChatLibre` · `TareaDetalleDto.EsChatLibre` · `IServicioTareas.IniciarChatLibreAsync`. |
| **Infrastructure** | `ConstructorContexto`: `DeclaracionPrecedenciaChatLibre` + wrapper (`ArmarPlataformaAsync` intacta) · `ServicioTareas`: `IniciarChatLibreAsync` y los 4 switches (visibilidad, permiso, constructor, flags) · `ProcesadorTareas`: permiso del autor, mensaje, evento `paso_chat_libre`, constructor al retomar y **el lookup de partes** · `AnatomiaAgenteService` (3 switches) · `EstimadorCorrida.FormatoDe` · `ConsumoService` · `PermisosOrganizacion.PuedeUsarChatLibre => EsMiembro && !EsStaff` · `ChatLibre : IChatLibre` + `AgentesDisponiblesQuery` + DI · `SubtareasService`: **dos modos** (`ModoJerarquiaAsync` / `ModoAbiertoAsync`), `PrepararAsync` y `PorTareaAsync` con lista blanca · `HerramientasSubagentes` ídem · `ResolvedorHerramientas`: bloque propio del chat libre para `subagentes_listar`/`delegar_subagente`, fail-closed. |
| **Web** | `ChatLibreController` (`RequireMiembro`, molde del analista) · `IniciarChatLibreViewModel` · `Views/ChatLibre/Index.cshtml` (**funcional, sin diseño ni 3D**: eso es la tanda 2) · ítem «Chat libre» en el menú · `<option>` del filtro de Tareas (y de paso los dos que faltaban desde M15 y M18). |
| **Núcleo** | `nucleo/plataforma/agentes/chat-libre.md` (**sin clave `herramientas`** a propósito: todo lo que usa se lo da la plataforma según la conversación) · línea en `plataforma.yml` · `nucleo/plataforma/evaluaciones/13-chat-libre.yml` (6 casos, 4 de seguridad). **Nada publicado.** |
| **Tests** | `ChatLibreTests.cs` (18 tests) · `Infra/EntornoM28.cs` · golden `formato-6-chat-libre` · un test HTTP de la pantalla en `MenuLateralTests` · ajustes de `EtapaEntregaTests`, `MenuLateralTests` (25 → 26 opciones) y `FichaImportadaTests` (17 → 18 agentes). `InternalsVisibleTo` para el proyecto de tests, para afirmar los switches internos directo. |

### Los dos modos de subagentes (A-04)
`SubagentesPermitidosAsync` es ahora un `switch` con **lista blanca** de tipo y dos ramas separadas:
**modo jerarquía** (`Trabajo` + `ArtefactoBaseId`, los hijos publicados del base — sin un solo cambio de comportamiento)
y **modo abierto** (`ChatLibre`, exactamente lo que devuelve `IAgentesDisponiblesQuery`). Lo que no cambió: filtro de
licencia del rubro, visibilidad y creador, `ProfundidadMaxima`, topes por paso y por turno, largo del pedido.
**El código del modo abierto lleva el rubro** (`b-<rubro>/<slug>`, el mismo que arma `agentes_disponibles`): sin agente
base los slugs de dos rubros pueden repetirse y un código ambiguo elegiría el agente equivocado en silencio.

### Defectos preexistentes encontrados y arreglados
1. **`ProcesadorTareas`, el lookup de partes (el grave).** Buscaba las partes ya creadas solo si `tarea.Tipo == Trabajo`.
   Un chat libre reanudado **no encontraba la parte que él mismo había creado y creaba otra en cada vuelta** —una tarea y
   un costo por sondeo— y quedaba colgado en `EsperandoSubtareas` para siempre. **No estaba en la tabla A-02**; lo
   encontró el test de la mención (2 llamadas al modelo, 2 partes). Arreglado con lista blanca.
2. **`ConstructorContexto.ArmarEvaluacionAsync`** (R-A6, ya anticipado): su switch de declaración de precedencia cubría
   solo los formatos 3 y 4, así que **evaluar el analista usaba la declaración del formato 1**. Se agregaron el 5 y el 6.
   El mismo agujero estaba en `AnatomiaAgenteService.Declaracion`.
3. **`ConsumoService.AgruparPorAgenteAsync`** resolvía el nombre del agente solo para tareas de `Trabajo`, así que el
   asistente y el analista aparecían como «Agente», **una fila por versión**. Ahora resuelven su nombre real.

### Qué quedó afuera de esta tanda, y por qué
- **Pasos 7 y 8** (vista de arranque con el 3D, autocomplete de `@` en `site.js`, CSS): tanda 2, por el brief.
- **CU-03, las menciones de configuración** y **P3, el filtro del Empleado**: quedaron declarados como huecos de esta
  tanda y **los cerró la tanda 1b** (ver más arriba), con A-07, A-08 y A-09 ya escritas por el arquitecto. El test
  `Todavia_no_se_proponen_reglas_desde_el_chat_libre` se invirtió ahí, como estaba previsto.
- **CA-05.2, la mitad de «el Director lee pero no envía»:** verificado que `EsAutor` es false para el Director; que el
  POST de ajuste lo rechace lo cubre el camino de M3b, que no se tocó.
- **CA-T.4** (guardia de destinos de M11): no se tocó nada de conectores y el chat libre no los recibe.

### Evidencia
- `dotnet build OlvidataAgentes.slnx` → **0 errores** (15 advertencias, todas preexistentes: NU1902/NU1510 y 3 de xUnit).
- `dotnet test tests/OlvidataAgentes.Tests` → **1141 de 1141, 0 con error, exit 0** (eran 1140 antes del frente).
- Golden nuevo `formato-6-chat-libre` regenerado con `OLVIDATA_GOLDEN_REGENERAR=1` y verificado en una corrida limpia
  después; el golden del formato 5 y los otros cuatro **no se tocaron** (CA-T.3).
- No se levantó la app ni se probó por navegador: eso es de QA.

### Pruebas mínimas para QA
1. Entrar a `/ChatLibre` sin publicar el agente: tiene que decir «Todavía no está disponible.» y el menú no ofrecerlo.
2. Correr `importar` + `evaluar --aprobada` + `publicar` del rubro `plataforma` y repetir: ahora sí abre.
3. Abrir un chat como Empleado, preguntar algo suelto y ver que responde sin elegir agente ni cliente.
4. Pedirle trabajo a un agente mencionándolo: el hilo tiene que pasar a «esperando», mostrar la tarjeta de parte y
   **despertarse solo** al terminar. **Revisar que quede UNA sola parte**, no una por sondeo (es el defecto 1).
5. Hacer fallar la parte (cancelarla) y ver que el hilo se despierta igual y lo informa.
6. Mencionar un slug inventado: no tiene que abrir nada ni decir si existe.
7. Adjuntar un archivo sin cliente y pedirle que lo lea.
8. Con el tope de gasto alcanzado: no arranca y dice por qué.
9. Entrar al chat de otra persona por URL (otro Empleado, otra organización): 404.
10. Mirar Consumo: las conversaciones del analista y del asistente ahora tienen que salir **con el nombre del agente**,
    no como «Agente» (es el defecto 3, y es una regresión posible si algo dependía del nombre viejo).

### Checklist de merge
- [x] Build limpio y suite verde.
- [x] Sin migración EF (verificado contra la configuración y el snapshot).
- [x] Un test por switch de mapeo de `TipoTarea` (R-A1).
- [x] Un test que corre la misma `IAgentesDisponiblesQuery` por los dos caminos (R-A2).
- [x] Un test que afirma que una tarea de trabajo sigue viendo solo los hijos de su base (R-A3).
- [x] Goldens 1 a 5 intactos; golden 6 nuevo y verificado.
- [x] Nada publicado en el núcleo (el agente queda en Borrador).
- [x] Commit local, sin push.
- [ ] QA de la tanda 1.
- [x] Decisión del arquitecto sobre CU-03: llegó como A-07/A-08/A-09 y la implementó la **tanda 1b**.
- [ ] Tanda 2 (pasos 7 y 8).
