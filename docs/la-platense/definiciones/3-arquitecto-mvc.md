# Memoria - Arquitecto MVC

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-10-08 (v15 - **DECISION DE ARQUITECTURA PENDIENTE DE GATE: idempotencia de submit, estructural vs. sitio por sitio.** La ronda de QA del 2026-10-08 midio **13 sitios** de la familia "un POST repetido duplica plata": 6 arreglados sitio por sitio, **7 abiertos**, y en el camino ese metodo produjo **una regresion que bloqueaba el pago de un adelanto** (`LP-114`) y **dos huecos en el mecanismo creado para arreglarla** (`LP-117`, `LP-121`). **Escaneo de reutilizacion: 3 matches, los tres de este mismo proyecto** -- `PAT-059` (el antecedente directo, nacido de 4 defectos que eran el mismo en 4 modulos, con codigo entregado en `BloqueoDeFila.cs`: **reutilizacion literal**), `PAT-061` y `PAT-056`. **La decision del escaneo es que hay DOS invariantes ortogonales y confundirlos es lo que produjo los 13 sitios:** *"la accion sigue siendo valida?"* la resuelve `PAT-059` con lock + relectura y **no se toca**; *"este request ya se proceso?"* **nadie la responde de forma transversal** y es la que falla. **El dato que decide:** la decision 5(a) de `PAT-059` **ya describe exactamente la trampa de `LP-114`**, asi que el patron estaba escrito, era correcto, estaba en el catalogo del estudio y **se volvio a romper igual** -- un patron que exige 13 aplicaciones manuales correctas tiene una tasa de error que no depende de quien lo aplique. **RECOMENDACION: opcion B, token de submit de un solo uso** (tabla `SubmitsProcesados`, consumo por `INSERT` atomico sobre la PK que cubre serie Y concurrencia, `IAsyncActionFilter` que corta el replay antes de llegar al Service, purga oportunista con `PAT-056` sin job). Sus cinco decisiones, cada una atada a un defecto medido: el token identifica al **request** y no al dato, asi que **desaparece el costo de negocio de `LP-064`** (dos fletes de $8.000 el mismo dia entran los dos); el unico va sobre el **token** y no sobre datos de negocio, respetando la decision 1 de `PAT-059`; **no reemplaza al lock, se suma** (quitarlo seria la peor lectura de esta decision); **la forma de baja por familia deja de importar**, asi que la clase de `LP-114` se extingue; y **un solo contrato de resultado**, porque el replay no llega al Service y no hay 8 callers interpretando una bandera. Opcion C (decorador en Application) **rechazada como mecanismo principal**: sin token tiene que derivar la identidad de los argumentos, o sea volver a la clave natural. **Advertencia de terreno verificada: el proyecto no tiene NINGUN filtro propio hoy ni carpeta `TagHelpers`**, asi que el costo incluye establecer la convencion. **Riesgo #1, que repite el error de esta ronda: un filtro opt-in es otra lista mantenida a mano** -- mitigacion obligatoria, o es opt-out o hay una verificacion que enumera los escritores de plata y falla si falta uno. Requiere **1 migracion aditiva**; sin permisos nuevos, con validacion de `UsuarioId` en el consumo para no abrir un IDOR de respuesta. **Los 6 sitios ya cerrados NO se tocan en el mismo cambio.** Gate: decidir si se paga como **garantia** (reemplaza 7 parches ya comprometidos) o como **alcance nuevo**; mi lectura es garantia con subproducto reutilizable. **Nada de esta familia se implementa hasta el gate, salvo `LP-119`** (`critical`, fiscal), con instruccion explicita de no construir abstracciones. Se mantiene v14.)

## Definiciones vigentes

### Idempotencia de submit: estructural vs. sitio por sitio — decisión de arquitectura (2026-10-08)

**Disparador:** la ronda de QA del 2026-10-08 midió 13 sitios de la familia "un POST repetido duplica plata". Se arreglaron 6 sitio por sitio y quedaron **7 abiertos**. En el camino, ese método produjo **una regresión que bloqueaba el pago de un adelanto** (`LP-114`) y **dos huecos en el mecanismo creado para arreglarla** (`LP-117`, `LP-121`). Joaquín frenó los 6 parches no urgentes y pidió evaluar una solución estructural. `LP-119` se arregla igual por ser `critical` y fiscal.

#### 0. Resultado del escaneo de reutilización (instrucción 39 §3)

`docs/patrones/cat_resumen.txt` (64 patrones) → **3 matches, los tres de este mismo proyecto**. Se leyeron **sólo** esas entradas del `catalogo.yml`; ninguna tenía `pendiente_verificar`.

| Patrón | Qué aporta | Grado de reuso |
|---|---|---|
| **`PAT-059`** — *Idempotencia por lectura previa: el patrón que sólo es seguro en secuencia (lock de fila del documento dueño)* | **El antecedente directo.** Nació igual que esto: `LP-018`/`LP-021`/`LP-023`/`LP-024`, *"4 defectos de QA que eran el mismo, encontrados por 3 lotes independientes en 4 módulos distintos"*. Su arreglo —mover la transacción antes de la **lectura** y arrancarla con lock de la fila dueña + **relectura**— está implementado y en producción en este repo | **Reutilización literal**: código ya entregado, `Infrastructure/Data/BloqueoDeFila.cs`, con orden canónico de bloqueo en 4 niveles y el nivel MAESTRO ya extendido en esta ronda con `BloquearUsuarioAsync` |
| `PAT-061` — *Fila centinela de período: serializar la AUSENCIA de una fila* | Serializar "todavía no existe" sin índice único. Aplicable si el registro de submits necesita serializar una ausencia | Patrón de diseño, con código de referencia en el cierre de caja de este repo |
| `PAT-056` — *Chequeo oportunista al primer request del día, en vez de un job programado (idempotencia en la base, no en el scheduler)* | La política de retención del registro de submits **no necesita un job**: se purga oportunistamente | **Reutilización literal**, mismo repo |

**Decisión del escaneo: `PAT-059` se REUTILIZA tal cual para el invariante que resuelve, y para el otro invariante se diseña nuevo — porque `PAT-059` declara explícitamente que no lo cubre.** Son dos preguntas distintas y ortogonales, y confundirlas es lo que produjo los 13 sitios:

- *"¿esta acción sigue siendo válida?"* → la responde `PAT-059` con lock de la fila dueña + relectura. **Está bien resuelta y no se toca.**
- *"¿este request ya se procesó?"* → **nadie la responde de forma transversal.** Hoy se contesta con una clave natural distinta en cada sitio, y es la que falla.

**El dato que decide la discusión, y es la razón por la que esto es un problema de arquitectura y no de cuidado:** la **decisión 5(a) de `PAT-059` ya describe exactamente la trampa de `LP-114`** — *"el campo de estado puede no ser el que discrimina… hay que preguntarse QUÉ COLUMNA cambia de verdad cada competidor"*. El patrón estaba escrito, era correcto, estaba en el catálogo del estudio, y **se volvió a romper igual**, porque hay que re-aplicarlo a mano en cada sitio con una forma de baja distinta por familia. Un patrón que exige 13 aplicaciones manuales correctas tiene una tasa de error que no depende de quién lo aplique.

#### GATE RESUELTO — 2026-10-09: Joaquin aprueba la opcion B (token de submit), **como GARANTIA**

Decision tomada con las cuatro razones medidas y la prueba de imposibilidad de §0-quater en la mano. **Se paga como garantia**, no como alcance nuevo: los 7 defectos abiertos hay que cerrarlos de todos modos y el enfoque A quedo demostrado incapaz de cerrarlos. El mecanismo queda como subproducto reutilizable para el resto del estudio.

**Plan de implementacion acordado, en dos fases y no en una.** Es la leccion de esta misma ronda aplicada a su propio arreglo: hacer 7 sitios de una vez es como se produjeron `LP-114`, `LP-117` y `LP-121`.

- **Fase 1 — el mecanismo mas UN sitio.** Se construye el token y se aplica unicamente a facturacion parcial, que es el sitio con la prueba de imposibilidad y con la linea base roja. **El criterio de aceptacion es el que no se puede falsear: `ArnesNotaCredito` tiene que volver a 63/0 SIN que nadie toque el arnes.** Ese fixture es independiente, fue escrito antes del problema, para otra familia, y es el unico caso que ninguna ventana puede satisfacer — si el token funciona, se pone verde solo. Y el interino de los 10 segundos se retira en el mismo movimiento.
- **Fase 2 — el resto, sobre el mecanismo ya probado:** `LP-118`, `LP-120`, `LP-117`, `LP-121`, `LP-112`, `LP-113`, y el retiro gradual de las claves naturales de los 6 sitios ya cerrados, **cada retiro con su propia re-verificacion**.

**Lo que NO se hace todavia, y es deliberado:** no se agrega el patron a `docs/patrones/catalogo.yml`. El rol del arquitecto pide agregar al catalogo todo componente reutilizable antes de cerrar la etapa, pero **el mecanismo no existe aun**, y publicar un patron como reutilizable antes de que haya codigo entregado es la clase de afirmacion falsa que este proyecto ya pago varias veces (`LP-044`, `LP-045`, `LP-051`, y la afirmacion del commit sobre `LineasEcheq`). **Se agrega cuando QA cierre la fase 1**, con la ruta real del codigo y el grado de reuso medido.

**Riesgo de datos aprobado para resolver en paralelo:** script de saneamiento de comprobantes duplicados, porque ningun endpoint escribe `DeletedAt` sobre `ComprobanteAfip` y una factura duplicada antes del fix solo sale por nota de credito, que duplica. Prod tiene 0 ventas hoy, asi que lo mas probable es que no haya nada que sanear — **y el script es precisamente la verificacion de eso**, no un supuesto.

#### 0-bis. Evidencia que llegó DESPUES de escribir la decisión, y la refuerza (2026-10-08, fix de `LP-119`)

El fix de `LP-119` se hizo con el molde sitio-por-sitio porque es `critical` y fiscal, y **midiendo encontró el piso duro del enfoque de clave natural**. No es una opinión del implementador: salió de ejecutar mutantes.

1. **El costo de la clave natural no se puede bajar agregando campos.** En facturación parcial la clave quedó en `(venta, día de negocio, conjunto EXACTO de líneas ítem→cantidad)` — ya es lo más fina que el dato de negocio permite — y aun así colapsa dos tandas legítimas con los mismos ítems y las mismas cantidades el mismo día. **El motivo es estructural: el doble clic y la segunda tanda legítima son bit a bit el MISMO POST.** Lo único que los distingue es un dato que identifique el **render**, que es precisamente lo que el token de la opción B aporta y lo que ninguna clave derivada del payload puede aportar. La clave natural no es una aproximación barata al token: **tiene un piso que no baja.**
2. **Y hay al menos un sitio donde la clave natural NO ES APLICABLE, ni en principio.** `VentaWorkflowService.FacturarAsync` **nunca** puede tener payloads distinguibles, porque **deriva sus líneas del pendiente** en vez de recibirlas: dos requests legítimos consecutivos producen el mismo conjunto de líneas por construcción. Hoy ese sitio depende **enteramente del lock**. Es decir: la opción A no es "más trabajo manual"; es **incompleta por diseño** para al menos un escritor de plata.
3. **Corolario de medición que vale para la próxima etapa, y que ya pasó dos veces:** poner una guarda de repetición **invalida los escenarios que medían el tope**, porque sus N competidores mandaban payloads idénticos y pasaron a ser un doble submit. Ocurrió con `LP-088` tras el fix de `LP-095`, y volvió a ocurrir con el escenario 4 del arnés de facturación tras el fix de `LP-119`. **Cualquier plan de implementación de la opción B tiene que presupuestar la revisión de los escenarios de tope existentes**, no sólo el mecanismo nuevo.

**Efecto sobre la recomendación: la refuerza y le agrega un argumento que no estaba.** La comparación honesta ya no es "7 parches caros contra 1 mecanismo": es que **el camino de los parches deja un sitio sin cubrir** (`FacturarAsync`) y **paga un costo de negocio que no tiene piso más bajo**. La opción B sigue siendo la recomendada, ahora por tres razones medidas en vez de dos.

#### 0-ter. El experimento controlado que la decisión no esperaba tener (2026-10-08, re-verificación de `LP-119`)

`LP-119` se arregló con el molde sitio-por-sitio **a propósito y con el gate pendiente**, para no bloquear un `critical` fiscal. Sin buscarlo, eso produjo el dato más fuerte de toda la evaluación, porque fue un ensayo real del enfoque A en las mejores condiciones posibles: lo aplicó quien ya lo había aplicado seis veces, con medición por mutación, con tres controles negativos discriminantes y con la trampa de la media línea ya conocida.

**Resultado: el enfoque A, bien aplicado, produjo un defecto `critical` PEOR en términos de negocio que el que arreglaba.**

- `LP-122` `critical`: la clave quedó con ventana de **un día de negocio**, y *"vendí 4, facturo 2 ahora y 2 a la tarde"* es rutina facturando por remito. Medido: facturar el remanente de 2 en un comprobante **colapsa**; partido en 1+1, el segundo colapsa en el primero. **Queda 1 unidad de 4 que no se factura por ningún camino con cantidades enteras**, y la salida que el mensaje prometía no existe en ese caso.
- **Y lo detectó un arnés de OTRA familia**: `ArnesNotaCredito` cayó de 63/0 a 62/1, y su fixture —escrito antes del fix, para otro propósito— era el caso real. Ninguna de las nueve afirmaciones nuevas del propio arnés del fix lo vio. Eso dice algo sobre el enfoque: **el autor de una clave natural no puede enumerar los casos legítimos que colapsa**, porque son casos de negocio y no de código.
- `LP-123` `major`: el contrato `CreateAviso` con `Success=true` rompió el conteo de `ArnesReconciliacionTx` (151/2), **por segunda vez en dos rondas** — la primera fue `16.1`. El mecanismo que se creó para hacer aceptable el costo de la clave natural tiene su propio costo recurrente.
- `LP-124` `minor`: en el atajo `ConfirmarYFacturarAsync`, lo que evita el duplicado **no es la guarda sino un deadlock de MySQL** que mata a los perdedores. La protección de ese camino era accidental, y la afirmación que el código citaba para darla por buena pasa en verde sobre el mutante del lock.

**Lo que esto cambia en la decisión.** La comparación ya no es de costo entre dos caminos razonables. Con cuatro razones medidas:

1. La clave natural **no tiene piso más bajo** (el doble clic y la segunda tanda legítima son bit a bit el mismo POST — §0-bis).
2. Deja **un sitio sin cubrir por diseño** (`FacturarAsync`, que deriva sus líneas del pendiente — §0-bis). *Matizado por la medición: el lock de `EmitirAsync` **sí es portante** y el atajo delega ahí, así que no hay sitio huérfano hoy; pero su protección propia es un deadlock, no una guarda.*
3. **Colapsa operaciones de negocio legítimas que su autor no puede enumerar**, y el síntoma aparece en el arnés de otra familia o en el mostrador.
4. El paliativo que la hace tolerable (`CreateAviso`) **tiene costo recurrente propio** en los instrumentos.

**La prescripción de QA coincide con la opción B y llegó por un camino independiente:** *"la clave necesita un nonce de submit o una ventana de segundos, no el día"*. Un nonce de submit **es** el token de la opción B.

**Interino en curso, declarado como interino:** acotar la ventana de `LP-119` de un día a segundos. Atajan el doble clic y el retry, que es el 100% de los casos reportados, y no colapsan la segunda tanda. **No es la solución**: sigue siendo una clave derivada del payload, con el piso de §0-bis, y hay que poder retirarla cuando el token exista. Por eso el fix lleva instrucción explícita de no construir abstracciones.

**Riesgo de datos que el gate tiene que considerar, porque no es reversible solo:** **ningún endpoint escribe `DeletedAt` sobre `ComprobanteAfip`** (0 escritores, verificado dos veces). Una factura duplicada **antes** del fix sólo sale por nota de crédito, y la nota de crédito duplica (`LP-120`, abierto). **Es irrecuperable sin SQL: hace falta un script de saneamiento antes del deploy**, independientemente de qué opción se elija.

#### 0-quater. La prueba de imposibilidad: los dos criterios son mutuamente excluyentes sin el token (2026-10-08, interino de `LP-122`)

Hasta acá la decisión se apoyaba en costos medidos. **Esto ya no es un argumento de costo: es una demostración de que el enfoque A no puede satisfacer los dos criterios a la vez, con ningún valor de ningún parámetro.**

El interino acotó la ventana de la clave de un día a **10 segundos**, con su piso medido —la emisión tarda **23 ms**, margen de 440x— y eso cerró el caso humano de `LP-122`: la segunda tanda pasada la ventana emite y no queda nada sin facturar. **Pero el fixture de `ArnesNotaCredito` hace sus dos tandas legítimas en menos de un segundo.** Se verificó bajando la ventana a **1 segundo**: sigue colapsando (62/1, los dos comprobantes con el mismo número). No es que 10 s sea generoso — es que ese caso está **tres órdenes de magnitud por debajo de cualquier ventana usable**.

**El enunciado de la imposibilidad, que conviene leer dos veces porque es el centro de la decisión:**

- `LP-119` exige que **N POST idénticos en serie dejen uno solo**.
- `LP-122` exige que **una segunda tanda idéntica, sub-segundo después, emita su comprobante**.
- **Son el mismo evento observable.** Un doble clic y dos tandas legítimas consecutivas producen requests **bit a bit iguales**, en la misma ventana de tiempo, sobre la misma venta, con las mismas líneas y cantidades. **Lo único que los distingue es un dato que identifique el render**, y ese dato no existe en el payload ni puede derivarse de él.

Cualquier clave derivada del payload tiene que elegir cuál de los dos criterios viola. **No hay valor de ventana, ni campo adicional, que los satisfaga a los dos**, porque la diferencia no está en los datos: está en cuántas veces el usuario pidió el formulario.

**El atajo tentador, descartado y documentado para que nadie lo reproponga:** excluir de la clave los comprobantes ya acreditados por una nota de crédito pone `ArnesNotaCredito` en 63/0 —porque *ese* fixture tiene una NC en el medio— y **deja `LP-122` abierto en su forma pura** ("facturo 2 ahora, 2 en seguida", sin NC), además de romper `9.16`. **Cumple la letra del criterio y no el defecto**, que es la forma de falla más cara del proyecto y ya tiene nombre propio en el catálogo.

**Estado que queda en el árbol, declarado y no escondido:** `ArnesNotaCredito` se queda en **62/1** hasta que exista el nonce. Es una línea base roja **conocida y explicada**, no una regresión silenciosa, y es la primera vez en el proyecto que una línea base se deja roja a propósito. Si alguien la "arregla" sin el token, está tomando el atajo del párrafo anterior.

**Efecto sobre el gate: deja de ser una comparación de costos y pasa a ser un sí/no.** Las dos únicas salidas coherentes son:

1. **Construir el token** (opción B) y cerrar `LP-122`, `LP-118`, `LP-120`, `LP-117`, `LP-121`, `LP-112`, `LP-113` sobre un mecanismo que distingue el render.
2. **Aceptar explícitamente** que la facturación parcial no soporta dos tandas idénticas sub-segundo, dejar `LP-122` abierto como riesgo aceptado con `ArnesNotaCredito` en 62/1, y documentarlo para el cliente.

**No hay una tercera que no sea el atajo descartado.** La recomendación sigue siendo la 1, ahora por imposibilidad demostrada y no por balance de costos.

#### 1. Alcance

Un mecanismo transversal que responda **una sola vez** *"¿este request ya se procesó?"*, en reemplazo de las claves naturales por sitio. **No es funcionalidad nueva para el usuario**: es el medio para cerrar 7 defectos abiertos y retirar deuda de los 6 ya cerrados. Magnitud del terreno, medida: **15 archivos de `Infrastructure/Services` escriben `CajaMovimientos`**, ~35 métodos, y **74 vistas** tienen formularios con `asp-action` (no todas escriben plata).

#### 2. Impacto técnico por capa — tres opciones y la recomendada

**Opción A — seguir sitio por sitio (statu quo).** Sin cambios de arquitectura. Costo medido, no estimado: 6 sitios produjeron 1 regresión y 2 huecos, y cada sitio paga **un costo de negocio propio** (la clave natural colapsa operaciones legítimamente idénticas: dos fletes de $8.000 el mismo día, que QA calificó de rutina en una ferretería). Quedan 7 aplicaciones manuales con 7 formas de baja por averiguar. **No recomendada.**

**Opción B — token de submit de un solo uso (RECOMENDADA).**

- **Domain:** nada.
- **Application:** un contrato `IRegistroDeSubmit` con dos operaciones (reservar / consultar), para que la capa Web no dependa de Infrastructure.
- **Infrastructure:** tabla `SubmitsProcesados` — `Token` (PK), `UsuarioId`, `RutaAccion`, `CreadoUtc`, y un resumen del resultado para poder **re-mostrar la respuesta original** en el replay en vez de un error. El consumo es un `INSERT` sobre la PK: **atómico en el motor**, así que cubre serie **y** concurrencia sin ventana. Purga por retención con `PAT-056` (chequeo oportunista al primer request del día), **sin job programado**, porque el hosting es compartido y la base tiene tope de 500 MB.
- **Web:** un `IAsyncActionFilter` que reserva el token antes de ejecutar la acción y corta con el resultado guardado si ya estaba. **Advertencia de terreno, verificada: hoy el proyecto no tiene NINGÚN filtro propio** (`grep` de `IActionFilter`/`ActionFilterAttribute` sobre `Web` da vacío) y **no hay carpeta `TagHelpers`**. Este sería el primero de los dos, así que el costo incluye establecer la convención, no sólo usarla.
- **Permisos:** ninguno nuevo. Pero el consumo **valida `UsuarioId`**: el resultado guardado de un submit no se le puede servir a otro usuario (es un IDOR de respuesta, y la ronda encontró IDOR cerrados en el resto del sistema — acá no hay que abrirlo).

**Las cinco decisiones de diseño que hay que retener, cada una atada a un defecto medido de esta ronda:**

1. **El token identifica al REQUEST, no al dato de negocio.** Por eso **desaparece el costo de negocio** que hizo caro a `LP-064`: dos fletes de $8.000 el mismo día son dos submits distintos y **entran los dos**. La clave natural no puede distinguirlos ni en principio; el token sí, sin preguntarle nada al dominio.
2. **El índice único va sobre el TOKEN, no sobre el dato de negocio**, así que la decisión 1 de `PAT-059` —*"lock de fila, NO índice único"*, porque un único sobre datos de negocio prohíbe reversiones parciales legítimas— **se respeta**: el motor garantiza unicidad de algo que es, por construcción, único.
3. **No reemplaza a `PAT-059`: se suma.** El lock + relectura sigue contestando *"¿la acción es válida?"*. Un token consumido sobre una acción que dejó de ser válida tiene que rechazar igual. **Quitar los locks al poner el token sería la peor lectura posible de esta decisión.**
4. **La forma de baja por familia deja de importar.** `LP-114` existió porque en CC-empleado la baja es un contramovimiento y no un estado en la fila vieja. El token no pregunta si la operación anterior "sigue viva": pregunta si **este** request corrió. Esa clase de defecto se extingue, no se mitiga.
5. **Un solo contrato de resultado, en un solo lugar.** `LP-117` y `LP-121` salieron de que `CreateAviso` deja `Success=true` y cada caller lo interpreta. Con el filtro, el replay **no llega al Service**: la respuesta la arma el filtro, así que no hay 8 callers interpretando una bandera.

**Opción C — decorador de idempotencia en Application sobre los Services que escriben plata.** Más cerca del dominio y no necesita tocar vistas, pero **sigue necesitando una clave**: un decorador que no recibe un token tiene que derivar la identidad del request de los argumentos, o sea volver a la clave natural con su costo de negocio y su pregunta por familia. Resuelve el punto 5 y **no** resuelve los puntos 1 y 4. **Rechazada como mecanismo principal**; sirve como complemento si apareciera un cliente no-navegador.

#### 3. Modelo de permisos

Sin roles ni policies nuevas. Dos requisitos: el consumo del token valida `UsuarioId` (ver arriba), y el filtro **no** puede ser el lugar donde se decide autorización — eso sigue en las policies existentes, que la ronda verificó sanas (206 acciones × 4 identidades, 195/206 redirigen sin cookie, ningún endpoint JSON abierto).

#### 4. Migraciones EF

**Sí, una, aditiva:** creación de `SubmitsProcesados` con su PK y el índice de retención por `CreadoUtc`. Ninguna columna sobre tabla preexistente, ningún backfill, `Down` reversible por `DropTable`. **Se suma a la cola de producción, que hoy tiene 12 pendientes** y que este cambio no altera en nada más.

#### 5. Riesgos y supuestos

1. **El riesgo que repite el error de esta ronda: un filtro opt-in por acción es otra lista mantenida a mano, y las listas a mano envejecen mal.** Es literalmente lo que pasó con el bloque `MISMA FORMA, SIN TOCAR`, que enumeraba 2 sitios de al menos 7. **Mitigación obligatoria, no opcional:** o el filtro es **opt-out** (se aplica por convención a todo POST y se exceptúa explícitamente), o hay una verificación que **enumera** los métodos que escriben plata y falla si alguno no está cubierto. El criterio de enumeración ya existe y QA lo verificó ejecutable en esta ronda.
2. **Un formulario legítimamente enviado dos veces** (dos pestañas) no se bloquea, porque cada GET emite un token nuevo. Es el comportamiento correcto y conviene medirlo explícitamente: es el control negativo del mecanismo.
3. **Botón "atrás" + reenviar** queda bloqueado, que es lo buscado, pero **el mensaje tiene que ser el aviso en `warning`** que ya se construyó en esta ronda, no un error — la lección de `LP-114` fue que un bloqueo con cartel verde es peor que el bug.
4. **Retención y el tope de 500 MB** de la base de producción: sin purga, la tabla crece sin techo. `PAT-056` la resuelve sin job.
5. **No cubre un cliente que reenvía sin pedir el formulario de nuevo** (un script, una integración). **Supuesto verificado hoy:** no existe tal camino — no hay API pública y **nadie llama a `IAfipService`** (los únicos dos lugares que lo nombran son un comentario y un docstring). El día que haya una integración, vuelve la opción C como complemento. **Esto se declara, no se esconde.**
6. **Los 6 sitios ya cerrados NO se tocan en el mismo cambio.** Retirar sus claves naturales mientras el token todavía no está probado es destapar lo que está tapado. Primero el token con red propia, después el retiro, y cada retiro con su re-verificación.
7. **Supuesto de costo:** la comparación honesta es *7 aplicaciones manuales con 7 formas de baja por averiguar* contra *1 mecanismo + convención nueva de filtros + 1 migración + el retiro gradual de 6 claves naturales*. El segundo camino es más caro de arrancar y más barato por sitio, y sobre todo **extingue dos clases de defecto** (`LP-114` y `LP-117`) en vez de mitigarlas.

#### 6. Gate de aprobación para pasar a presupuesto

**Esto no es un fix de defecto: es un mecanismo transversal nuevo, y necesita decisión de Joaquín antes de implementarse.** Lo que hay que decidir no es técnico —la recomendación es la opción B— sino **si se paga como garantía** (reemplaza 7 parches que ya están comprometidos) **o como alcance nuevo** (el mecanismo queda y sirve para todo lo que venga). Mi lectura: es garantía con un subproducto reutilizable, porque los 7 defectos hay que cerrarlos de todos modos y la opción A ya demostró su tasa de error.

**No se implementa nada de esta familia hasta que el gate esté resuelto**, con la única excepción de `LP-119` (`critical`, fiscal), que se arregla con el molde existente y **con la instrucción explícita de no construir abstracciones**, para que pueda ser absorbido o retirado cuando el mecanismo exista.

**Si la opción B se aprueba, antes de cerrar la etapa hay que agregar el patrón al catálogo** (`docs/patrones/catalogo.yml`): no existe hoy, y es exactamente el tipo de pieza que el resto de los proyectos del estudio va a necesitar — `marihogar`, `crm-olvidata` y `delicias-naturales` tienen la misma forma de formularios que escriben plata.

### Arquitectura de CR-01 a CR-05 (2026-10-06)

Entrada: `2-disenador-funcional.md` v7, flujos 11 a 15. Verificado contra el código real del repo (enums, entidades y controladores), no contra la documentación.

#### Impacto por capa

**Datos (el bloque de mayor riesgo — hay 2.990 clientes y ~112.000 productos con actividad real en producción):**

| Cambio | Tipo | Riesgo |
|---|---|---|
| `Venta.Facturar` (bool, default **true**) | columna nueva con default | **Bajo.** El default reproduce el comportamiento actual: toda venta histórica queda "con factura", que es lo que fue |
| `ComprobanteAfip` + `ComprobanteAfipItem` (entidades nuevas, 1:N sobre `Venta`) | tablas nuevas | **Bajo ahora, imposible después.** No hay ninguna factura real emitida (AFIP deshabilitado por falta de certificado), así que `Venta.CAE`/`NumeroComprobante`/`VencimientoCAE` están **todos en null** y no hay backfill que hacer. Después de la primera factura real, esta migración pasa a ser una reconstrucción de datos |
| `Venta.CAE`, `NumeroComprobante`, `VencimientoCAE` | **se dejan en su lugar, sin uso** | Se marcan obsoletos en el XML-doc apuntando a `ComprobanteAfip`. No se borran en la misma migración que crea las tablas nuevas: borrar columnas y crear el reemplazo en un solo paso deja sin camino de vuelta si algo sale mal |
| `Tarjeta` (catálogo con baja lógica) + `InteresTarjetaCuota` (tarjeta, cuotas, %, `VigenteDesde`/`VigenteHasta`) | tablas nuevas | **Bajo.** `RecargoCuota` se **mantiene** como está (no se migra ni se borra): sigue resolviendo el caso sin tarjeta y las ventas viejas siguen leyendo su porcentaje. `IRecargoCuotasService` resuelve primero por tarjeta y cae a `RecargoCuota` cuando no hay tarjeta elegida |
| `PagoVenta.TarjetaId` (nullable) | columna nueva nullable | **Bajo.** Los pagos históricos quedan sin tarjeta, que es la verdad: no se sabe con cuál se cobraron |
| `LineaEcheq` (número, banco, plazo en días, vencimiento) 1:1 con `PagoOrdenCompra` | tabla nueva | **Bajo.** Se cuelga del pago programado que ya existe; ningún pago histórico la necesita |
| `MedioPago.Transferencia = 5` | valor nuevo **al final** | **Bajo si se respeta el orden.** `Confirmada = 4` está al final de `EstadoVenta` a propósito "para no reasignar los enteros ya persistidos": el mismo criterio aplica acá y en los dos enums de abajo |
| `OrigenMovimientoCC.DiferenciaIvaFacturacion = 5` | valor nuevo al final | **Bajo.** Hay que propagarlo a los filtros que listan el ledger — **LP-002**, mismo camino que `CobroCC` ya recorrió |
| `CuotaCheque` con `Dias0 = 0` y `Dias120 = 120` | valores nuevos | El valor numérico **es** la cantidad de días (criterio de `marihogar`), así que 0 y 120 entran sin reordenar nada |

**Una sola migración EF, aditiva, sin un solo `DROP` ni `ALTER` destructivo.** Ninguna columna existente cambia de tipo, de nombre ni de significado. No hay migración de datos: todos los defaults reproducen el comportamiento actual.

**Negocio:**
- `VentaWorkflowService` — el cálculo de IVA pasa a depender de `Venta.Facturar`; el precio unitario se recalcula desde el producto cuando el usuario no es Administrador (**LP-014**). Es el servicio más sensible del sistema: es el que la familia de defectos de atomicidad (LP-018/034/035/036/038) acaba de dejar con relectura real bajo lock, y **el cambio tiene que entrar por dentro de ese patrón, no al lado**.
- `FacturacionParcialService` (nuevo) — emite el comprobante y postea el cargo de IVA en la CC del cliente **en la misma transacción**, con lock de fila y relectura real (`Data/RelecturaBajoLock.cs`, 13 call sites hoy). Facturar dos veces en paralelo la misma venta es exactamente la carrera que el proyecto ya midió en otros cinco lugares.
- `RecargoCuotasService` — firma nueva `(medio, tarjeta, cuotas, fecha)`; el valor efectivo se sigue congelando en `PagoVenta.PorcentajeRecargoAplicado`, que no se toca.
- `PlanEcheqService` (nuevo) — genera las N líneas de pago programado en una transacción. **No mueve caja ni cuenta corriente**: reusa `PagoOrdenCompra` en estado `Pendiente`, que ya está construido y probado (y cuya confirmación es justamente donde se encontró LP-035).
- `AnulacionVentaService` — pasa a operar por comprobante. **Todavía no existe**: se ajusta su contrato ahora para no construirlo dos veces en la Entrega 5.
- Aviso de vencimiento de echeqs — **`PAT-056`** (chequeo oportunista al primer request del día, idempotencia en la base). **No** se agrega el primer `AddHostedService` del repo: en SmarterASP un job con hora fija puede no correr nunca si el pool se recicla por inactividad.

**Presentación:** venta (control de facturación + combo de tarjeta + precio bloqueado por rol), pantalla nueva de facturación parcial, Configuración > Intereses de tarjeta, bloque de plan de echeqs en el pago a proveedor, listado de echeqs pendientes, y la columna de estado de ventas con el valor "Facturada en parte". Todo con el design system (`ov-filtros`, `ov-tabla-datos`, `ov-vacio`, `ov-celda-secundaria`, `ov-estado-tenue` — instrucción 38).

### Arquitectura de la Entrega 5 — Devoluciones y notas de credito (2026-10-07)

Entrada: `2-disenador-funcional.md` v8, flujos 16 a 18. Verificado contra el codigo real, no contra los documentos.

#### Impacto por capa

**Datos — una migracion aditiva, y una advertencia de enum que es la de mayor riesgo del bloque:**

| Cambio | Tipo | Riesgo |
|---|---|---|
| `Devolucion` + `DevolucionItem` (nuevas) | tablas nuevas | **Bajo.** Nada existente las referencia |
| `ComprobanteAfip.ComprobanteAsociadoId` (FK nullable a si misma) + `Motivo` | 2 columnas nullable | **Bajo.** Su XML-doc ya las anticipaba como el alcance de este modulo |
| `TipoComprobanteAfip`: agregar las notas de credito | **valores nuevos de enum** | **El mas delicado del bloque, y por un motivo que no es el habitual** (ver abajo) |
| `OrigenMovimientoCC`: valor nuevo para la devolucion del cargo de IVA | valor nuevo **al final** | **Bajo**, con LP-002: un origen nuevo se propaga a los filtros que leen el ledger, las dos puntas |

**La advertencia del enum, y hay que leerla antes de escribir la migracion:** `TipoComprobanteAfip` **no usa valores correlativos: usa los codigos de comprobante de AFIP** (`FacturaA = 1`, `FacturaB = 6`). O sea que la regla del proyecto de *"todo valor nuevo va al final, numerado explicito"* **aca no aplica igual**: los valores no son arbitrarios, los fija AFIP. Las notas de credito tienen que entrar con **su codigo real de AFIP** (NC A y NC B), no con el siguiente numero libre. Agregar un valor correlativo porque "va al final" produciria un comprobante que el WSFEv1 rechaza, y el error aparece recien cuando llegue el certificado — es decir, lo mas lejos posible de donde se cometio. **Lo mismo vale si el negocio usa comprobantes C.**

**Negocio:**
- `DevolucionService` (nuevo): el unico escritor del circuito. Reingresa stock **por el ledger `MovimientoStock`** (nunca escribiendo `Producto.Stock` directo: el proyecto ya tiene un unico escritor y se respeta), revierte la plata **acotada a lo realmente posteado** (`PAT-020`) y dispara la NC cuando corresponde. Una transaccion, con lock de fila y **relectura real** por `Data/RelecturaBajoLock.cs`.
- `NotaCreditoService` (nuevo): emite la NC contra un comprobante y devuelve la parte proporcional de `DiferenciaIvaCobrada`.
- `VentaWorkflowService` (afectado): `AnularAsync` suma la guarda de "esta venta tiene devoluciones", para que la reversion no sea doble.
- `FacturacionParcialService` (afectado): el pendiente **sigue sin restar notas de credito** (R18); lo que se agrega es que **un item ya devuelto no se puede facturar**.

**Presentacion:** pantalla de devolucion con preview de lo que se revierte, listado de devoluciones, la NC en el detalle del comprobante, y las dos guardas nuevas reflejadas en los botones.

#### El riesgo estructural de este bloque, dicho antes de construirlo

**Los tres defectos `major` de la ronda anterior — `LP-039`, `LP-040` y el hallazgo del combo de Editar — son el mismo error: un criterio que vive en una sola punta, o que pregunta por el estado del padre para inferir la existencia del hijo.** Esta entrega agrega **cuatro** criterios nuevos de esa misma familia:

1. "esta venta tiene devoluciones" → no se puede anular,
2. "este item ya se devolvio" → no se puede facturar,
3. "este comprobante tiene NC" → no se le puede emitir otra NC por lo mismo,
4. "este item ya se facturo" → su devolucion exige NC.

**Los cuatro tienen que estar en el Service y en la UI desde el primer commit**, y el barrido de los lectores/escritores del hecho es **parte del cambio, no una tarea posterior**. Es exactamente la regla que quedo escrita despues de `LP-040`: cuando un modelo pasa de 1:1 a 1:N, todo criterio que preguntaba por el estado del padre queda roto y se barren todos juntos. Aca el modelo pasa de "una venta, un estado" a "una venta con devoluciones parciales y comprobantes parciales", que es el mismo salto.

#### Condicion para habilitar AFIP: el comprobante en `Error` se cuenta de forma asimetrica (2026-10-07)

**Encontrado por el implementador en el lote 2 y hay que resolverlo ANTES de cargar el certificado.** `ObtenerYaFacturadoPorItemAsync` **si** cuenta los comprobantes en `EstadoComprobanteAfip.Error`; el planificador de notas de credito **no**. Las dos lecturas del mismo hecho discrepan.

**Hoy es inalcanzable**: sin certificado, AFIP nunca se llama, asi que **ningun comprobante llega a `Error`** — todos nacen y se quedan en `Pendiente`. **El dia que se cargue el certificado deja de serlo**, y ahi las dos lecturas empiezan a contestar distinto sobre si un item esta facturado.

**Es la misma forma que `LP-039`, `LP-040` y `LP-052`** (un criterio replicado que divergio) y la misma forma que el riesgo que CR-02 cerro a tiempo: **un defecto que hoy no se puede reproducir y que se activa con un evento externo conocido.** Esos son los que conviene cerrar mientras son gratis. Queda como **condicion de entrada del residual del modulo 6**, junto con el certificado: no se habilita AFIP sin unificar esas dos lecturas.

#### El criterio de habilitacion vive en UN lugar y lo consumen las tres puntas (decision del orquestador, 2026-10-07)

**Cuarta aparicion del mismo defecto, y por eso deja de tratarse caso por caso.** `LP-039` (anular con comprobante vivo), `LP-040` (facturar por el camino legado), el combo de Editar de una compra y ahora **`LP-052`** son todos la misma cosa: **un criterio de habilitacion replicado en varios lugares, que divergen.**

`LP-052` tiene el agravante que vuelve inutil la revision por lectura: **el boton de `Details.cshtml:368` guarda TRES condiciones y el GET de `NotasCreditoController:44` guarda UNA.** No es que falte la guarda — **hay guarda, pero no la misma**. Un chequeo de "el GET esta protegido" **da verde**. Medido por QA: `GET /NotasCredito/Emitir/5` sobre una NC devuelve **200** con el formulario, llamando "factura" a una nota de credito; `Emitir/8` sobre un comprobante en `Error` devuelve **200** y la pantalla nunca dice que esta en `Error`. Los `POST` rechazan bien, asi que **no se escribe dato malo**: es una puerta que se abre, no un dato corrupto. Eso lo hace `major` por UX y por confianza, no por integridad.

**Decision: el criterio de habilitacion de una accion se escribe UNA vez, en el dominio o en el Service, y lo consumen las tres puntas** — el `GET` que abre la pantalla, el `POST` que ejecuta, y la vista que decide si muestra el boton. Ninguna de las tres puede tener su propia copia de las condiciones.

Forma concreta: un metodo o propiedad que devuelva **la razon por la que NO se puede** (null = se puede). Asi la vista oculta el boton, el `GET` redirige con ese mensaje y el `POST` rechaza con el mismo texto, **sin repetir una sola condicion**. Es el mismo patron con el que ya se resolvio `puedeAnular` despues de `LP-039`, pero elevado a regla: **lo que alla fue un fix puntual, aca es como se construye.**

**Por que se decide ahora y no despues:** la Entrega 5 agrega **tres criterios mas de esta familia** (venta con devoluciones no se anula; item devuelto no se factura; item facturado exige NC al devolverse). Si nacen con el patron viejo, son tres divergencias futuras — y ya sabemos que la revision por lectura no las encuentra, porque "hay guarda" se ve igual que "hay la guarda correcta". **Los tres criterios nuevos nacen con este mecanismo, y `LP-052` se arregla migrando el de la NC al mismo.**

**Lo que el barrido de QA ya dejo claro sobre contar lectores:** el commit del lote 1 declaraba **tres** lectores del "ya facturado" y son **cuatro** (el cuarto es `ListarComprobantesAsync:422`, el del titulo de la pantalla). Y hay un **quinto consumidor que queda bien por carambola** (`VentaWorkflowService:1054` se alimenta del lector 4: revertir ese filtro hace que el mensaje "ya esta facturada por completo en N comprobante(s)" cuente las notas de credito como facturas, y **ningun arnes lo ve**). **Contar los lectores a ojo no funciona: se enumeran por `grep` sobre todo el arbol, y se declara el numero.**

#### Orden de construccion

1. **`TipoComprobanteAfip` con los codigos reales de AFIP** + `ComprobanteAsociadoId`/`Motivo` + migracion. Solo esquema, no mueve nada.
2. **`NotaCreditoService`** contra un comprobante, con la devolucion del cargo de IVA. Se prueba solo.
3. **`DevolucionService`** (stock + plata), que consume el anterior.
4. **Las cuatro guardas** de la familia de arriba, en las dos puntas.
5. **Residual del modulo 6: AFIP real** — certificado, homologacion y primera NC real. **Unico gate externo del proyecto**, espera al cliente.

#### Mapa de reutilizacion (verificado archivo por archivo, no por memoria)

| Pieza | Origen | Grado |
|---|---|---|
| NC fiscal | `marihogar`: `IComprobanteAfipService.GenerarNotaCreditoAsync` (linea 49) + `ComprobanteAfipService` — ya resuelve "NotaCreditoA/B segun la original" | **Alto** |
| Circuito de mercaderia | `ShowroomGriffin`: `IDevolucionService`, `DevolucionService`, `DevolucionCambio` + `DevolucionCambioDetalle`, `TipoDevolucion` | **Alto, con poda**: contempla cambio/canje y aca **no aplica** (R8, solo devolucion simple) |
| Reversion acotada a lo posteado | `PAT-020` + la anulacion de venta que ya esta en este repo | **Total**, ya construido |
| Devolucion del cargo de IVA | — | **Sin precedente**: `DiferenciaIvaCobrada` es propio de este proyecto |

#### Deploy a produccion POSTERGADO por credencial, y la ventana que caduca (2026-10-07)

**Decision de Joaquin: el deploy queda para despues.** El bloqueante es operativo, no tecnico: la password de FTP/Web Deploy de `credenciales.local.md` **no autentica** (`530`, el usuario existe y esta activo, o sea fue rotada), y Web Deploy usa esa misma credencial. Joaquin eligio **no** rotarla desde el panel: la memoria del estudio la declara **compartida entre sitios**, asi que rotarla romperia el deploy de los otros proyectos hasta actualizar cada uno. Primero hay que recuperarla.

**Estado real de produccion, medido el 2026-10-07 desde el dump (no consultando prod en vivo):** **8 migraciones aplicadas, 10 pendientes.** 112.485 productos, 2.990 clientes, 85 proveedores, **0 ventas y 1 movimiento de caja**. Ese ultimo par corrige el dato que venia en el parte de QA de `LP-050` ("5 ventas y 4 movimientos"), que era falso.

**El ensayo del deploy esta hecho y PASA** (`LP-050`): las 10 migraciones sobre una copia del dump real tardaron **14 segundos**, 28 tablas quedaron con hash y conteo identicos, ninguna fila perdida y ningun valor preexistente cambiado. Snapshot de rollback en `C:/Sistemas/backups/laplatense/laplatense_PROD_2026-10-07_pre-migracion-18.sql`.

**LA CONDICION QUE INVALIDA EL GO — CORREGIDA POR QA EL 2026-10-07, y la version anterior de este parrafo era MIA y estaba MAL.**

Lo que yo habia escrito: *"en cuanto el cliente empiece a vender, el backfill pasa a tener filas reales y hay que re-ensayar"*. **Es falso, y QA lo midio contra el codigo viejo** (`628cb7a`): su enum tope es `CreditoCuotas`, `CuentaCorriente` esta excluida de caja, y el sitio que postea caja por una venta **si** lleva el sufijo que el `CASE` busca (linea 497; el 482 sin sufijo es el movimiento de cuenta corriente, otra cosa). O sea **las 3 ramas del `CASE` cubren todo lo que el codigo viejo puede emitir: una venta hecha ANTES de migrar se backfillearia bien.** El peligro que yo describi no existe.

**El peligro real es la ventana POSTERIOR, y es exactamente el inverso:** una vez migrada la base, si el sitio viejo sigue corriendo, **el modelo EF viejo omite `MedioPago` en el `INSERT`** — el backfill ya corrio y no vuelve a correr — asi que **todo movimiento de caja nuevo queda `NULL` para siempre**. `LP-050` reabierto y, peor, **invisible**: nada falla, solo se ensucia. Lo mismo con `EsReversion = 0` y con `Proveedores.Moneda = 0`, que **no es un valor valido del enum**.

**Por eso la regla no es "deployar pronto" sino "base y sitio en la misma ventana".** Migrar la base y dejar el sitio viejo operando es el escenario que hay que evitar, y produccion **esta activa** (movimiento de ayer). Si hay que elegir, la ferreteria sin operar un rato es mejor que un ledger de caja que se llena de `NULL` sin avisar.

**Lo que QA verifico de la convivencia, para que quede el dato y no la impresion:** de **31 columnas nuevas** sobre tablas preexistentes, **ninguna es `NOT NULL` sin default** (las 5 `NOT NULL` tienen default real en BD, y el `sql_mode` de produccion es `STRICT_TRANS_TABLES`, asi que si faltara uno reventaria en vez de ensuciar). El unico `UNIQUE` nuevo (`IX_Proveedores_CUIT`) **convive con 85 `CUIT` en NULL**, y la unica FK nueva es nullable. **Estructuralmente la base aguanta el codigo viejo; funcionalmente no.**

**Y el snapshot de rollback es restaurable, probado:** QA lo restauro en una base descartable propia en 17 s (8 migraciones, 112.485 productos) y **hasheo las 28 tablas contra ESE restore**, no contra el archivo de evidencia del implementador: 28/28 identicas.

**Dato corregido de paso:** las tablas nuevas son **15, no 6** (el 6 lo repeti yo de un reporte anterior sin contarlas).

**Orden del deploy cuando se desbloquee:** base y sitio **en la misma ventana**. No migrar la base y dejar el sitio viejo corriendo contra el esquema nuevo sin que QA se pronuncie sobre esa convivencia — esta pedido en el lote de QA en curso.

#### Decisiones de Joaquin del 2026-10-06 (cierre de LP-037 y del boton del POS)

**LP-037 — se cierra con FILA CENTINELA por periodo.** Decision de Joaquin. Una tabla con una fila por periodo, bloqueada con `FOR UPDATE` sobre **una fila que existe**: exclusion mutua real, sin ciclo de deadlock. Es el plan B que el propio XML-doc de `BloquearPeriodoCajaAsync` ya nombraba. **Se descarto** la lectura de bloqueo por rango del dia: no necesita migracion, pero convierte el descuadre en un deadlock contra el escritor que ya tiene el gap y obliga a logica de reintento.

Recordatorio de por que la reserva actual no alcanza, porque es el punto que se presta a confusion: **los gap locks de InnoDB conviven entre si** (solo inhiben `INSERT`), asi que el cerrador toma su gap, **lee los totales**, los escritores commitean despues, y el `INSERT` del cierre —que si espera los gaps— graba los totales que ya habia leido. La espera llega tarde: **habia que serializar la LECTURA, no el `INSERT`**. Criterio de cierre: las **2 afirmaciones que hoy fallan a proposito** en `tools/ArnesSeisSitiosRestantes` (su 20 OK / 2 FALLADAS) pasan a OK, y vuelven a fallar si se saca la centinela.

**El boton "Confirmar y facturar" del POS queda OCULTO.** Decision de Joaquin. El mostrador cierra con `Confirmada` y se factura aparte, cuando y si el cliente pide factura — que es lo que el negocio ya hace y lo que CR-01 y CR-02 suponen (la mayoria de las ventas reales nunca llegan a facturarse). **No se habilita ni se retira**: retirarlo era la otra opcion razonable (un camino muerto de facturacion menos, y los caminos muertos de facturacion son de donde salieron LP-039 y LP-040), y se deja la puerta abierta a revisarlo si el negocio cambia de criterio cuando llegue el certificado.

**Proximo lote segun Joaquin: los 3 CR que faltan** (CR-03 interes por tarjeta, CR-04 plan de echeqs, CR-05 transferencia). La Entrega 5 —NC/ND y anulacion por comprobante— queda habilitada pero **no es lo que sigue**.

#### Un solo camino escribe el comprobante — decision del orquestador del 2026-10-06, a raiz de LP-039 y LP-040

**La causa raiz de los dos defectos que QA encontro despues de CR-02 no es una guarda mal escrita: son dos caminos poblando dos modelos distintos para el mismo hecho.**

Los dos partes son el mismo defecto de clase, en dos metodos distintos del mismo servicio: `AnularAsync` (LP-039) y `FacturarAsync` (LP-040) **decidian por `Estado == EstadoVenta.Facturada`**, que era equivalente a "tiene comprobante" **solo mientras hubo un comprobante por venta**. Al introducir los 1:N de CR-02, una venta facturada en parte se queda en `Confirmada` y ninguna de las dos guardas se alcanza. Que aparecieran dos y no una es la seniaL: el criterio viejo estaba replicado en cada camino que lo necesitaba.

**Decision:** `FacturarAsync` deja de ser un camino paralelo de emision y pasa a ser **un atajo del circuito 1:N** ("facturar todo lo pendiente"), delegando en la misma emision que usa `FacturacionParcialService`. Y **deja de escribir `Venta.CAE`, `Venta.NumeroComprobante` y `Venta.VencimientoCAE`**.

**Lo que NO cambia:** esas tres columnas **siguen existiendo**, obsoletas y sin uso, por la decision ya tomada en la tabla de impacto de esta misma seccion (borrarlas en la misma migracion que crea el reemplazo deja sin camino de vuelta). Lo que termina es que alguien las **escriba**. Tener una columna muerta es barato; tener dos escritores del mismo hecho en modelos distintos es lo que produjo LP-039 y LP-040.

**Por que se decide ahora y no en la Entrega 5:** QA lo dejo medido con precision — *el riesgo vence exactamente cuando se enciende lo que el fix anterior desbloqueo*. Hoy lo unico que impide facturar dos veces los mismos items es que **AFIP esta apagado**: el POST al camino legado atraviesa las cuatro guardas de negocio y muere recien en la integracion, por falta de certificado. El dia que se cargue el certificado, ese mismo POST emite un CAE real por el total encima de un comprobante parcial vivo, en columnas que nadie lee y sin fila en `ComprobantesAfip`. **La Entrega 5 no habilita AFIP hasta que esto este cerrado y re-verificado.**

**Regla que queda para el resto del proyecto:** cuando un modelo pasa de 1:1 a 1:N, **todo criterio que preguntaba por el estado del padre para inferir la existencia del hijo queda roto**, y hay que barrerlos todos juntos — no de a uno cuando QA los encuentra. El barrido de los escritores/lectores del hecho es parte del cambio de modelo, no una tarea posterior.

#### Orden de construcción (cada paso compila, deploya y se prueba solo)

1. **LP-014** (precio por rol) — agujero abierto en producción, acoplamiento cero, y precondición de CR-01: sin esto, CR-01 amplifica el defecto.
2. **CR-05** transferencia — un valor de enum y su mapeo. El más chico, y valida el camino de "valor nuevo al final" antes de usarlo tres veces más.
3. **CR-03** interés por tarjeta — tablas nuevas, no toca nada existente. `RecargoCuota` queda intacto.
4. **CR-01** venta sin factura — primer cambio en el motor de precios de la venta.
5. **CR-02** facturación parcial — el más grande, y el que depende de CR-01 (el cargo de IVA solo existe si CR-01 existe). **Antes de habilitar AFIP.**
6. **CR-04** plan de echeqs — independiente de los cinco anteriores; se puede adelantar si conviene.

#### Riesgos técnicos nuevos

- **El orden de CR-02 contra AFIP es la única ventana irreversible del lote.** Mientras no haya un CAE real emitido, la migración a comprobantes 1:N es aditiva y sin backfill. Después de la primera factura, es una reconstrucción de datos sobre documentos fiscales. El certificado del cliente es el único gate de la Entrega 5 y puede llegar en cualquier momento: **CR-02 va antes.**
- **CR-01 toca `VentaWorkflowService.ConfirmarAsync`**, que es el método donde se acaba de medir LP-038 (postear con el grafo de antes del lock). El cambio del cálculo de IVA tiene que quedar **adentro** de la relectura bajo lock, no antes. Un total calculado antes del lock y posteado después es exactamente la forma del defecto que ya se midió.
- **LP-037 sigue abierto y es independiente de este lote**, pero comparte el ledger de caja: el cierre de día puede firmar totales en cero mientras hay escritores concurrentes. Agregar medios de pago (CR-05) y cargos nuevos (CR-02) no lo empeora, pero **tampoco se arregla con esto** — necesita la decisión pendiente (lectura de bloqueo por rango vs. fila centinela).
- **El cargo de IVA en la CC del cliente es un importe que nadie pidió y que aparece en el estado de cuenta.** Si el vendedor no explicó la diferencia, el cliente la ve como un cargo sin motivo. El texto del movimiento tiene que nombrar el comprobante que lo generó, no decir "ajuste".
- **`ComprobanteAfipItem.Cantidad` es `int` en `marihogar` y acá tiene que ser `decimal`** (3 decimales, como `ItemVenta.Cantidad`). Es el error más fácil de cometer al portar: su modelo entero asume cantidades enteras y La Platense vende 2,5 metros.

#### Mapa de reutilización (verificado archivo por archivo, no por memoria)

| Pieza | Origen en `marihogar` | Grado |
|---|---|---|
| CR-02 comprobantes 1:N | `ComprobanteAfip`, `ComprobanteAfipItem`, `EstadoComprobanteAfip`, `IComprobanteAfipService`, `ComprobantesAfipController`, `Views/ComprobantesAfip/{Index,Create,Details}`, migración `20260821143237_AddNotaCreditoAfip` | **Alto** — su `Create` es la pantalla de elegir qué ítems facturar. Adaptar `Cantidad` a decimal |
| CR-03 interés por tarjeta | `ConfiguracionCuotaTarjeta` (eje cuotas) + `TasaCostoCobranza` (clave Procesador/Metodo/Cuotas + vigencia) | **Alto en estructura**, propósito distinto: allá es costo del negocio, acá interés al cliente |
| CR-04 echeqs | `Cheque`, `EstadoCheque`, `CuotaCheque`, `ChequeService` (`AcreditarAsync`, `RevertirEstadoAsync`), `Views/Cheques/Index` | **Medio** — se toma el modelo de datos y la grilla, no la cartera ni el `BackgroundService` |
| CR-01 venta sin IVA | — | **Sin precedente**: el IVA de `marihogar` es 21% hardcodeado en 4 puntos de `VentaService` |
| LP-014 precio por rol | `VentaService.ConfirmarAsync` / `EditarAsync` (`esAdministrador`) | **Alto**, acoplamiento cero |

### Componentes por capa

- **Presentación**: Controllers/Views para Usuarios, Catálogo, Stock, Ventas, Facturación AFIP, Proveedores/Compras, Importación de listas, Caja, Gastos, CtaCteNegocio, CtaCteEmpleado, Presupuestos, Entregas, AumentoMasivo, Dashboard. DataTables para todos los listados; SweetAlert2 para confirmaciones; daterangepicker para filtros de fecha (Caja, Ventas, Compras).
- **Negocio (Services)**: `VentaWorkflowService`, `UnidadMedidaConversionService`, `RecargoCuotasService`, `ListaPreciosProveedorImportService`, `CuentaCorrienteEmpleadoService`, `CajaService` (diaria+mensual), `AfipFacturacionService` (incluye emisión de NC/ND), `AnulacionVentaService`, `DevolucionMercaderiaService`, `EntregaMarkupService`, `AumentoMasivoService`, `DashboardService` (3 niveles: día / salud financiera / tendencias), `AjusteStockService` (corrección manual auditada + venta con stock negativo permitido), `CodigoBarrasLookupService` (resuelve producto por código escaneado en venta). *`EtiquetaService` se retira — la ticketeadora es manual, no hay generación/impresión de etiquetas de por medio. `CatalogoMigracionService` también se retira de este alcance — la migración se pospone, ver `4-presupuestador.md`.*
- **Datos**: `AppDbContext` + repositorios EF Core / MySQL, siguiendo el patrón estándar del blankproject base (10-blankproject-base, soft delete + auditoría en todas las entidades).

### Entidades y configuraciones EF

Entidades nuevas (resumen — el detalle exacto de columnas se cierra en Implementación):

- `Producto` (nombre, codigo, marca, modelo, categoriaId, precioCompra, precioVenta, precioConDescuento, porcentajeIVA, unidadVenta [enum: Unidad/Peso/Metro/Bulto], unidadCompra [enum, nullable], factorConversion [nullable], stock, stockMinimo, clasificacionABC [enum A/B/C, nullable — usado en la puesta a punto de stock inicial], stockVerificado [bool, default false hasta que se cuenta o se ajusta manualmente], codigoBarras [string, único — de fábrica reutilizado o propio asignado por el negocio]).
- `AjusteStock` (productoId, fecha, usuarioId, cantidadAnterior, cantidadNueva, motivo) — reutiliza el patrón de ajuste manual de `ShowroomGriffin` (`StockController`). Marca `Producto.stockVerificado = true` al aplicarse.
- `Marca`, `Modelo`, `Categoria` (catálogo simple, patrón ya resuelto).
- `Cliente` (nombre, CUIT/DNI, condicionIVA, telefono, saldoCuentaCorriente).
- `Venta` (fecha, clienteId [nullable = consumidor final], estado [Borrador/Facturada/Anulada], subtotal, totalIVA, total, tipoComprobanteAfip, cae, numeroComprobante). El repartidor tiene visibilidad total sobre `Entrega` (sin scoping por `repartidorId` — confirmado, ve todas).
- `NotaCreditoDebito` (ventaId, tipoComprobanteAfip [NC/ND], cae, numeroComprobante, motivo, fecha) — vinculada a la `Venta` original, dispara la transición `Facturada`→`Anulada`.
- `DevolucionMercaderia` (ventaId, notaCreditoId, fecha, motivo) con `ItemDevolucion` (productoId, cantidad) — reingresa stock al confirmarse. Sin flujo de "cambio/canje" (confirmado, siempre devolución simple).
- `ItemVenta` (ventaId, productoId, cantidad, unidadVenta, precioUnitario, porcentajeIVA, descuento, recargo, subtotal).
- `PagoVenta` (ventaId, medioPago [Efectivo/Debito/CreditoCuotas/CuentaCorriente], monto, cuotas [nullable], porcentajeRecargoAplicado [nullable]).
- `Proveedor` (nombre, CUIT, tcPropio, porcentajeDescuento, saldoCuentaCorriente).
- `Compra` (fecha, proveedorId, formaPago [Echeck/Transferencia], total).
- `ItemCompra` (compraId, productoId, cantidadUnidadCompra, cantidadUnidadVentaEquivalente, precioUnitario).
- `MovimientoCuentaCorrienteProveedor` (proveedorId, fecha, tipo, monto, saldo) — reutiliza patrón `MovimientoCCProveedor` de `vinosefue`.
- `CajaMovimiento` (fecha, tipo [Ingreso/Egreso], monto, origen, referenciaId).
- `CierreCajaDiario`, `CierreCajaMensual` (fecha/periodo, totalIngresos, totalEgresos, saldo).
- `Gasto` (fecha, concepto, monto, tipoImpacto [CajaChica/CajaMensual]).
- `EmpleadoCuentaCorriente` (usuarioId, fecha, tipo [Sueldo/Retiro/Gasto], monto, saldo) — visibilidad restringida al propio usuario + admin.
- `Presupuesto` (clienteId, fecha, items, total, pdfGenerado).
- `Entrega` (ventaId, tipo [Propia/Tercerizada], costoBase, porcentajeMarkup, costoFinal, estado, repartidorId [nullable]).
- `HistorialPrecio` (productoId, fecha, precioAnterior, precioNuevo, motivo) — soporta Aumento Masivo.

### Migraciones requeridas

- Migración inicial: todas las entidades listadas arriba (incluye `NotaCreditoDebito`, `DevolucionMercaderia`, y los campos nuevos de `Producto` para stock inicial y código de barras).
- **Migración de datos del catálogo existente del cliente — RETOMADA 2026-08-17, ya no pospuesta.** Joaquín consiguió acceso directo al backup real de SQL Server del sistema actual (17,35GB, ~121.691 artículos activos — corrige el volumen estimado de ~17.000). Ver detalle completo de Análisis/Diseño en `1-analista-funcional.md` y `2-disenador-funcional.md` flujo 10. Arquitectura de esta etapa (Etapa 3) en la sección siguiente.

### Etapa 3 — Arquitectura de la migración de catálogo (2026-08-17)

**Entidades nuevas:**
- `CodigoProveedorProducto` (productoId, proveedorId, codigoDelProveedor, activo) — reemplaza la idea original de "un código externo único en `Producto`": un mismo `Producto` puede tener N filas, una por cada proveedor que lo vende con su propio código. Confirmado por los datos reales: dos listas de proveedor de muestra no comparten ningún esquema de código entre sí, y el sistema actual del cliente ya resuelve esto igual (tabla `Codigo` con `ProveedorKey`+`Codigo`). Índice único compuesto `(ProveedorId, CodigoDelProveedor)`.
- Sin entidad nueva para el "reporte de excepciones" de la migración — se modela como una vista/consulta sobre el resultado del proceso de limpieza (paso 1 del flujo 10), no como una tabla persistente del sistema en producción.

**Extensión de entidades ya existentes (Entrega 1/2, no rompe lo ya implementado):**
- `Producto`: agrega `Bonificacion` (string, nullable, ej. `"33+5"` — bonificación compuesta, confirmada como gap real por Joaquín) y `ClasificacionABCSugerida` (enum A/B/C, nullable, calculado — separado de `ClasificacionABC` que ya existe y sigue siendo el campo editable manual de Entrega 1, ver R10 vigente).
- `Cliente`: agrega `Domicilio`, `Localidad`, `Email`, `Notas` (todos string nullable — gaps confirmados en Análisis frente al sistema real).

**Servicios nuevos:**
- ~~`ICatalogoMigracionService`/`CatalogoMigracionService`~~ — **implementado y luego retirado (2026-08-17)**: Joaquín decidió que la carga del catálogo histórico (~121.691 productos) va por **script directo a la base**, no por un Service/Controller de la app con flujo preview→confirmar — al ser una carga de una sola vez, no justifica mantener esa superficie en el sistema. El script reutiliza las entidades (`Producto`/`CodigoProveedorProducto`/`Cliente`/`Proveedor`) y la lógica de deduplicación ya diseñada, pero corre fuera del ciclo de vida de `FerreteriaLaPlatense.Web` — los pasos 1 y 2 del flujo 10 quedan unificados en una sola herramienta batch.
- `IClasificacionAbcAutomaticaService` / `ClasificacionAbcAutomaticaService`: recalcula por lote `Producto.ClasificacionABCSugerida` sobre ventana móvil de `ItemVenta` (12 meses configurable) con corte Pareto 80/95 por cantidad vendida. Se registra Scoped, se invoca desde una acción manual de administración (no job automático en esta etapa — ver riesgo abajo). **Se mantiene** — es funcionalidad permanente del sistema, no exclusiva de la migración.
- **El proceso de limpieza/extracción (paso 1 del flujo 10) NO es un servicio de la aplicación web** — es un proceso batch de una sola corrida (script/herramienta de migración ejecutado por Olvidata contra una copia del backup del cliente), fuera del ciclo de vida normal de `FerreteriaLaPlatense.Web`. No requiere DI ni controller.

**Migración EF de esta etapa:**
- Una migración: `EntregaTres_MigracionCatalogo_CodigoProveedorProducto` (o el nombre que corresponda en Implementación) — agrega `CodigoProveedorProducto`, y las columnas nuevas de `Producto`/`Cliente`. No modifica ninguna migración ya aplicada de Entrega 1/2.
- La carga masiva de datos migrados (~121.691 productos + `CodigoProveedorProducto` + clientes) **no va en la migración EF** — es un seed/import de datos ejecutado una vez, separado del esquema.

### Capacidad de hosting — verificado 2026-08-17 (pregunta de Joaquín: la base de producción tiene un tope de 500MB)

Medición real (no estimada a ojo): se cargó una muestra real de 1.487 productos activos (de la base restaurada) en una tabla MySQL local con el esquema exacto de `Producto`, y se midió el tamaño real vía `information_schema.tables` (InnoDB, datos+índices): **297,8 bytes/fila**. Extrapolado a los 121.691 productos activos reales: **≈ 34,6 MB**. Sumando una estimación de `CodigoProveedorProducto` (asumiendo 0,5-1 código de proveedor por producto en promedio tras la deduplicación, ~180 bytes/fila): **≈ 11-22 MB adicionales**. Total estimado de la migración de catálogo: **≈ 46-67 MB**, contra un tope de **500 MB** — deja **más del 85% de margen libre**, no es un bloqueante para esta etapa.

**Riesgo real distinto, a monitorear (no resuelto por esta medición):** el tope de 500MB es del total de la base, no solo del catálogo — las tablas transaccionales que crecen con el uso diario (`Ventas`/`ItemVenta`/`PagoVenta`/`CajaMovimiento`/`Notifications`, etc., de Entregas 1 y 2) van a acumular filas de forma continua mes a mes, a diferencia de la carga del catálogo que es un evento único. No se midió proyección de crecimiento transaccional en esta ronda — recomendado revisar el uso real de espacio cada pocos meses una vez el sistema esté en producción operativa, no solo antes de la migración de catálogo.

### Riesgos técnicos de Etapa 3 (adicionales a los ya vigentes)

- **Volumen real 7x el estimado original** (121.691 activos vs ~17.000 supuestos): no cambia el diseño (`DataTables` server-side de Entrega 1 ya pagina en servidor, no carga todo en memoria), pero sí el tiempo de import batch inicial y el tamaño del reporte de excepciones — a validar tiempos reales en Implementación con un dataset de este volumen antes de comprometer una ventana de corte a producción.
- **`IClasificacionAbcAutomaticaService` sin trigger automático definido todavía**: el diseño lo deja como acción manual desde administración, no un job programado — si Joaquín pide que se recalcule solo (ej. mensual), es una extensión menor (`CronCreate`/hosted service), no un cambio de arquitectura, pero no está confirmado en esta ronda.
- **Deduplicación de nombre con respaldo `FechaModificacionPrecio`**: decide el 87% de los casos ambiguos (3.544 de 3.612 grupos, ver Análisis) — es una heurística, no una regla infalible; algunos casos van a requerir corrección manual posterior desde el catálogo ya migrado (edición normal de `Producto`, no requiere pantalla especial).
- **Origen de ventas para ABC confirmado como `VentaItem`/`Operacion`, no `tblVentas`/`tblDetalleVentas`** (`tblDetalleVentas.Codigo` no vincula a ningún producto en los datos reales) — si en el futuro el cliente migra su operatoria diaria hacia el otro circuito, `IClasificacionAbcAutomaticaService` deja de tener datos de origen; no aplica mientras el sistema nuevo sea el único en uso post-migración (los `ItemVenta` los genera el sistema nuevo, no dependen de los circuitos legacy una vez migrado).

### Riesgos tecnicos activos

- **Venta con stock negativo permitido**: la validación de stock en `VentaWorkflowService` debe permitir confirmar una venta aunque el producto quede en negativo (solo aviso, no bloqueo) mientras `Producto.stockVerificado = false` — evitar que una regla de "no vender sin stock" (frecuente en ABMs de stock genéricos) bloquee el mostrador durante la transición de datos.
- **Conversión de unidades compra↔venta**: no hay entidad/patrón exacto reutilizable en el historial — es desarrollo nuevo (aislado en `UnidadMedidaConversionService` para minimizar impacto en el resto del sistema).
- **Workflow Venta Borrador→Facturada con edición previa**: mayor superficie de riesgo que el patrón estándar de venta+AFIP ya resuelto (que factura directo, sin estado intermedio editable).
- **Importación de listas de proveedor**: el mapeo de columnas puede no ser 100% genérico entre proveedores — riesgo de tener que ajustar el parser por proveedor real.
- ~~Etiquetado con ticketeadora~~ → **Ya no es un riesgo: la ticketeadora es manual, no se integra con el sistema.**

### Mapa de reutilización cross-proyecto

| Componente / patrón | Proyecto origen | Qué se reutiliza |
|---|---|---|
| Estructura base de Producto/Catálogo/Stock | `marihogar` | Catálogo (M2), Stock (M3) — ABM y alertas de stock mínimo ya resueltos |
| `Producto.unidadMedida` (enum Kg/Unidades/Gramos) | `delicias-naturales` | Base conceptual para `UnidadVenta` — se extiende con `UnidadCompra`+`FactorConversion` (pieza nueva) |
| Ventas + cuenta corriente de clientes (fiado) | `marihogar` | Base de `Venta`/CC cliente — se extiende con workflow Borrador→Facturada (pieza nueva) |
| Facturación AFIP (WSAA/WSFE, .p12) | `marihogar`, `delicias-naturales` | Patrón completo ya resuelto, mismo `AfipFacturacionService` |
| Proveedores + compras + actualización de stock | `marihogar` | Base de `Compra`/`Proveedor` — se extiende con TC propio + % descuento + importación (piezas nuevas) |
| `MovimientoCCProveedor` (ledger) | `vinosefue` | Reutilizado directo para cuenta corriente de proveedores |
| Caja / `CajaService` / `EgresoService` | `ganaderia` | Base de ingresos/egresos — se extiende con cierre diario y mensual como dos niveles separados |
| Gastos varios | `marihogar` | Base directa, se agrega clasificación caja chica/mensual |
| Presupuestos y cotizaciones en PDF | `marihogar` | Reutilizado directo |
| Entregas (seguimiento, estados) | `marihogar` | Base de `Entrega` — se extiende con markup configurable y distinción propia/tercerizada |
| Aumento masivo de precios (categoría/marca) | `marihogar`, `ShowroomGriffin` | Reutilizado directo, se agrega filtro por proveedor |
| Parser de importación Excel propietario | `contadores-bma-conversor` | Referencia para la migración de catálogo cuando se cotice esa fase futura (pospuesta, no forma parte de este alcance) |
| `Marca`/`Modelo` como catálogos separados | `ShowroomGriffin` | Reutilizado directo |
| Devolución de mercadería (stock, motivo, vínculo a venta) | `ShowroomGriffin` | Reutilizado directo — base de `DevolucionMercaderia` |
| Emisión de NC/ND AFIP | `marihogar`/`delicias-naturales` (extensión) | El circuito WSAA/WSFE ya resuelto se extiende para emitir NC vinculada a la factura original — no es una integración nueva desde cero |
| Búsqueda de producto en la pantalla de venta | Módulo Ventas (mismo proyecto) | El escaneo de código de barras extiende el buscador de producto ya existente en el flujo de venta, no crea uno nuevo |
| `CodigoProveedorProducto` (mapeo de código por proveedor) | Sistema actual del cliente (tabla `Codigo`) + patrón de catálogo simple ya usado en Entrega 1 (`ShowroomGriffin`) | No es reuse cross-proyecto en el sentido estricto — es la confirmación de que el propio sistema legacy del cliente ya modela el mismo problema con la misma forma; se reutiliza el patrón EF de catálogo simple ya usado para Marca/Modelo/Categoria |
| Importación de dataset limpio (Etapa 3, paso 2 del flujo 10) | `IListaPreciosProveedorImportService` (mismo proyecto, Entrega 2) | Mismo contrato preview→confirmar, aplicado a Producto/Cliente en vez de precios de proveedor — no es un patrón nuevo |

**Piezas sin precedente exacto (desarrollo nuevo, no reuse):** conversión de unidades compra↔venta con factor configurable, workflow Venta Borrador→Facturada editable, cuenta corriente de empleados con autoservicio (autorización a nivel de registro), cuenta corriente consolidada del negocio, dashboard de 3 niveles ("foto completa del negocio"), la resolución código de barras→producto en venta, **el proceso de limpieza/deduplicación batch de Etapa 3** (reglas de negocio específicas de este dataset, sin precedente en el historial del estudio) y **la clasificación ABC automática por ventas** (`IClasificacionAbcAutomaticaService`, sin precedente exacto — el análisis Pareto sobre `ItemVenta` es una pieza de cálculo nueva).

### Código de barras múltiple por producto (2026-08-21)

- Nueva entidad `CodigoBarrasProducto` (Domain, `SoftDestroyable`): `ProductoId` (FK), `Codigo` (string, único global — no compuesto con `ProductoId`, un código de barras real pertenece a un único producto), `Activo`. Mismo shape que `CodigoProveedorProducto` (patrón ya resuelto en Etapa 3) — reuse directo, no un tipo de entidad nuevo.
- `Producto.CodigoBarras` **no cambia** — sigue siendo el código propio de la impresora interna del cliente, 1 por producto.
- `ICodigoBarrasLookupService.BuscarPorCodigoAsync` se extiende: `WHERE Producto.CodigoBarras = @codigo OR EXISTS (SELECT 1 FROM CodigoBarrasProducto WHERE Codigo = @codigo AND ProductoId = Producto.Id)`.
- Migración EF: tabla nueva, aditiva, sin tocar `Productos`.
- Backfill de datos: extensión del script `tools/MigracionCatalogo/Program.cs` (mismo patrón que el modo `--solo-codigo-barras` ya construido) — para los artículos con más de un código `Tipo='B'`, inserta todos los códigos reales en `CodigoBarrasProducto` en vez de descartarlos como ambiguos.
- Fuera de alcance (declarado, no un gap accidental): ABM en pantalla para agregar/quitar códigos alternos manualmente — igual que `CodigoProveedorProducto`, se carga solo por script/migración por ahora.

## Historial de ajustes
- 2026-08-21: agregada `CodigoBarrasProducto` (1 a N, reuse directo del patrón `CodigoProveedorProducto`) para soportar productos con múltiples códigos de barras reales de fábrica. `Producto.CodigoBarras` sin cambios (sigue siendo el código propio, 1 por producto). Ver `1-analista-funcional.md` §10 y `4-presupuestador.md` para el presupuesto.
- 2026-07-30: Arquitectura v1 — mapa de reutilización cross-proyecto definido (marihogar como base estructural principal; delicias-naturales, vinosefue, ganaderia, ShowroomGriffin y contadores-bma-conversor como donantes puntuales). Identificadas 4 piezas sin precedente exacto que se presupuestan como desarrollo nuevo.
- 2026-07-30 (v2): agregadas entidades `NotaCreditoDebito` y `DevolucionMercaderia` (venta facturada anulable por NC, confirmado por el cliente). Reutilización directa del patrón de devoluciones de `ShowroomGriffin`. Migración de catálogo confirmada en ~17.000 filas — promovida a Etapa 3 independiente, ejecutada por lotes con reporte de errores. Dashboard redefinido como pieza de mayor prioridad de diseño (3 niveles), no un KPI-set genérico.
- 2026-07-30 (v3): agregada entidad `AjusteStock` (reutiliza patrón `StockController` de `ShowroomGriffin`) y campos `Producto.clasificacionABC`/`stockVerificado`, para soportar el plan de puesta a punto de stock inicial (el cliente no tiene stock confiable hoy). Riesgo técnico nuevo declarado: la validación de venta debe permitir stock negativo para productos no verificados, sin bloquear el mostrador.
- 2026-07-30 (v4): dos cambios. (a) Agregado `Producto.codigoBarras` + `EtiquetaService` + `CodigoBarrasLookupService` (código de fábrica o propio, etiquetado con ticketeadora, escaneo en venta) — riesgo declarado: se asume impresora estándar de Windows, a confirmar marca/modelo. (b) **Retirada la migración de catálogo de este alcance** (`CatalogoMigracionService` se saca) — se pospone a una fase posterior, condicionada a si Joaquín consigue acceso directo a la base de datos actual del cliente (segundo relevamiento) en vez de depender de un archivo Excel de formato desconocido.
- 2026-07-30 (v5): Joaquín confirmó que la ticketeadora es manual — no se integra con el sistema. Se retira `EtiquetaService` por completo (no hay generación/impresión de etiquetas). Queda solo `CodigoBarrasLookupService` + el campo `Producto.codigoBarras`. Riesgo de protocolo propietario (ZPL/EPL) ya no aplica.
- 2026-08-17 (v6): **Migración de catálogo retomada** — Joaquín consiguió acceso real al backup de SQL Server del sistema actual (121.691 artículos activos, corrige el volumen estimado de ~17.000). Agregada entidad `CodigoProveedorProducto` (reemplaza la idea de código externo único en `Producto`, confirmado por los datos reales que cada proveedor tiene su propio esquema sin relación entre sí). Extendidos `Producto` (`Bonificacion`, `ClasificacionABCSugerida`) y `Cliente` (`Domicilio`/`Localidad`/`Email`/`Notas`) con gaps confirmados frente al sistema real. Agregados `ICatalogoMigracionService` (import idempotente, mismo contrato que `IListaPreciosProveedorImportService`) y `IClasificacionAbcAutomaticaService` (ABC automática por Pareto sobre `ItemVenta`, ventana de 12 meses, sugerencia editable que nunca pisa el campo manual). El proceso de limpieza/deduplicación (paso 1 del flujo 10) es batch, fuera del ciclo de vida de la app web — no requiere servicio ni controller.
- 2026-08-17 (v7): implementada y QA-pasada la mitad "app" de Etapa 3 (`CodigoProveedorProducto`, `Proveedor` mínimo, extensión de `Producto`/`Cliente`, `ICatalogoMigracionService`, `IClasificacionAbcAutomaticaService` — commit `71daf36` en `migracion-catalogo`). Inmediatamente después, **Joaquín corrigió el enfoque de carga**: la migración del catálogo histórico va por script directo a la base, no por `ICatalogoMigracionService`/`MigracionCatalogoController` (esa carga es de una sola vez, no justifica mantener un flujo web de subida+preview+confirmar). **Se retiró `ICatalogoMigracionService`/`CatalogoMigracionService`/`MigracionCatalogoController` y sus vistas**, ya implementados — build limpio verificado tras la baja. Se conservan `Proveedor`, `CodigoProveedorProducto`, la extensión de `Producto`/`Cliente`, y `IClasificacionAbcAutomaticaService` (funcionalidad permanente, no exclusiva de la migración) — toda esa lógica la va a reutilizar el script de migración real. Aclaración de alcance explícita de Joaquín: esto es distinto de la futura importación de listas de precios de proveedor (flujo 3, recurrente, seguirá siendo por archivo vía pantalla cuando se implemente).
