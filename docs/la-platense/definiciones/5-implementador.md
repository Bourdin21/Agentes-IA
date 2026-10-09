# Memoria - Implementador

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-10-09 (v33 — **TOKEN DE SUBMIT, pase 2: arreglar el GATE de la fase 2.** La re-verificacion de QA tuvo una forma clara: **el mecanismo esta bien y la fase 1 es mergeable; lo que no era confiable era el INSTRUMENTO del que depende la seguridad de la fase 2.** Los cuatro arreglos son del instrumento y de una afirmacion falsa, no del mecanismo. **CERO migraciones nuevas** (la cola de produccion sigue en 13), la fase 2 NO arranco, los 6 sitios con clave natural cerrada sin tocar. **`LP-127`: el detector de escritores de plata era UNA LISTA A MANO DE 7 NOMBRES dentro del programa que existe para que no haya listas a mano** — la forma exacta de `MISMA FORMA, SIN TOCAR`, y la peor version, porque sale en verde. QA lo midio por dos caminos que la lista no podia ver (`new CierreCajaDiario`, entidad no listada; y una escritura por SQL crudo) y el perimetro real eran 28 POST y no 23. **El arreglo no fue agregar las 5 que faltaban: el criterio pasa a ser una PROPIEDAD DEL DATO** — una entidad es de dinero si declara un `decimal`, derivado de `Domain/Entities/*.cs` en cada corrida (**27 entidades, cero nombres a mano**), con TRES formas de escritura (`new`, `.Add/.Update/.Remove` sobre el DbSet del tipo, y **SQL crudo**). **Lo que no se puede clasificar se declara ruidoso y no se ignora:** el SQL crudo entra al perimetro por las dudas y se imprime aparte; hoy ningun Service lo usa, asi que esa rama es TRIPWIRE y no cobertura, y se midio con `M17`. Perimetro final **35 POST**, y si la derivacion da 0 el programa **aborta** (cero entidades con `decimal` es un fallo del verificador, no un dominio sin dinero). Las excepciones pasan a **cinco grupos** porque mezclarlas era parte del problema: A clave cerrada, B defecto abierto, C protegido por otro mecanismo, **D SIN EVALUAR (la cola real: 13 POST)** y E entra por el criterio amplio sin ser un hecho financiero repetible. **DOS CLASIFICACIONES SALIERON DE LEER EL CODIGO Y UNA ME CORRIGIO A MI: `AumentoMasivoPrecios/Aplicar` es IDEMPOTENTE POR CONSTRUCCION** —los dos modos derivan el precio de `PrecioCompra` y nunca del `PrecioVenta` anterior, asi que aplicarlo dos veces da el mismo precio; lo que duplica es la fila de AUDITORIA— y **`Caja/CerrarDia`/`CerrarMes` tienen el duplicado atajado por los indices unicos entre vivos** `UX_CierresCajaDiarios_Fecha_Vivo` / `UX_CierresCajaMensuales_Anio_Mes_Vivo` mas el candado de `LP-037`, **pero lo que NO se midio es QUE SE LE CONTESTA al operador** cuando el segundo choca contra el indice (si sale el mensaje crudo de EF, es `LP-116`). El de mayor impacto aparente del grupo D es **`Presupuestos/ConvertirAVenta`** (un doble submit podria crear dos ventas del mismo presupuesto). **`LP-126`: el chequeo del cableado estaba INERTE en un build normal y aun asi imprimia 'el cableado del helper esta bien'** — un verde falso en el UNICO chequeo del modo de falla TOTAL (si el token no llega, el filtro falla cerrado y la pantalla rechaza TODA emision). Ahora **el verificador se produce su propia evidencia**: lanza el build de Web con `EmitCompilerGeneratedFiles` a un directorio TEMPORAL y lo lee en la misma corrida; si no se puede, **la afirmacion no se imprime** y sale **exit 3**. Medido con `M18`: rompiendo el `@addTagHelper`, dos lineas ROTO y exit 3 sin ningun verde. **`LP-125`: el token no nacia atado a la accion y el XML-doc afirmaba que si** — un token FRESCO del formulario de logout posteado a `Emitir` **emitia**, porque la validacion de accion vivia solo en el CONSUMO y el rechazo llegaba un submit tarde; la afirmacion falsa en la documentacion es la familia `LP-044`/`LP-045`/`LP-051` y es peor que la garantia faltante, porque el que lee deja de buscar. Ahora el token es nonce + huella de la **ruta destino** tomada del `action` YA RESUELTO (de ahi el `Order` alto del helper: no es cosmetico) y el filtro la valida **ANTES de reservar**. **Y se dice lo que NO es, para no repetir `LP-125` en la otra direccion: la huella no esta firmada y no es una credencial** — fabricarla no compra nada, porque un token es una clave de idempotencia y no un permiso, y cualquiera que pueda postear obtiene uno legitimo abriendo el formulario. Detalle de robustez que aparecio arreglandolo: el helper se aplica a TODOS los formularios, asi que su `ViewContext` quedo null-safe **porque una excepcion suya tumbaria la pantalla entera**. **`LP-128`: una de las 15 retiradas habia perdido cobertura** — la vieja `9.10` no media la clave natural sino que dos tandas de cantidades distintas **SUMEN** 2,5 exacto, y mi `9.8` solo mide que las dos ENTREN. Restaurada como **`9.12`, al final de la familia y con numero NUEVO**, porque renumerar otra vez volveria inauditable la propia lista de retiradas. **La leccion de procedimiento la aporto QA y vale para todo el repo: al renumerar, `9.3`-`9.7` y `9.9` quedaron existiendo en las dos versiones CON SENTIDOS DISTINTOS, asi que una auditoria POR ID no podia distinguir retirada de renumerada y hubo que hacerla POR TEXTO — si una familia se reescribe, las afirmaciones nuevas van con numeros nuevos.** **Correccion de QA a mi orden de riesgo, aplicada: `Ventas/Facturar` es el MENOS urgente de los cuatro** (deriva sus lineas del pendiente, asi que el segundo submit no tiene nada que facturar: 1 comprobante en serie y en paralelo) — lo que lo hacia parecer urgente es justamente lo que lo protege; `Gastos/Anular` esta protegido A PROPOSITO (lee `Anulado` dentro de la transaccion despues del lock), `CCEmpleado/Revertir` tiene una clave natural BUENA (identidad del movimiento, no un monto) y `OrdenesCompra/RevertirPago` quedo BLOCKED. **6 mutantes nuevos (`M16`-`M21`) y los cuatro arreglos arrancaron en FAIL. El que mas importa es `M21`** —la huella del filtro no coincide nunca con la del helper—, que es el modo de falla MAS PROBABLE en produccion (cualquier divergencia de normalizacion deja la pantalla muerta) y tumba 18 afirmaciones **incluida `4.6`, mientras `4.5` NO cae**: rechazar todo tambien rechaza el token cruzado, asi que **sin `4.6` se podria afirmar 'la huella funciona' con la pantalla rechazando toda emision**. Evidencia: 5 arneses exit 0 (NC 63/0 con `git diff` vacio, CR-02 **97/0**, token **34/0**, recon 153/0, devoluciones 63/0), verificador exit 0, build no incremental **0 errores / 9 advertencias** con codigos `NU1902` + `CS0114`. `appsettings`/`Seed`/`SeedData` sin tocar. Sin commit. **Ningun defecto marcado como cerrado.**)

## Anterior: 2026-10-09 (v32 — **TOKEN DE SUBMIT, fase 1: el mecanismo transversal mas UN sitio.** Gate aprobado como GARANTIA. **El criterio que no se podia falsear se cumplio: `ArnesNotaCredito` volvio de 62/1 a 63/0, exit 0, con `git diff -- tools/ArnesNotaCredito` VACIO** — la linea base que el pase anterior dejo roja a proposito se puso verde sola al retirar la clave natural del Service, que es la unica forma de verificar que el mecanismo resuelve el problema en vez de esconderlo. **UNA migracion aditiva pura** (`CreateTable` + PK + indice de retencion; `Down` = un `DropTable`): **la cola de produccion pasa de 12 a 13**. Sin commit, sin push, sin deploy, `laplatense_dev` sin tocar. **El mecanismo: `SubmitsProcesados` con LA CLAVE PRIMARIA SOBRE EL TOKEN**, asi que el consumo ES el `INSERT` y es **atomico en el motor** — cubre serie Y concurrencia sin ventana de lectura, o sea sin el antipatron de `PAT-059`. `INSERT IGNORE` decidido por filas afectadas, en **una conexion APARTE** (la reserva tiene que ser visible para los competidores EN EL ACTO, y un `SaveChanges` desde acá arrastraria lo que el Service de negocio tenga trackeado); el caso imposible rompe con excepcion, porque dejar pasar pierde la garantia en silencio y bloquear inventa el rechazo de `LP-114`. **Web estrena sus dos primeras convenciones**: `Filters/` y `TagHelpers/`. **El riesgo #1 se mitigo con la opcion (b), la verificacion ejecutable**, y la mitad opt-out que si se podia poner ya esta: el tag helper apunta a TODO `<form>` que no sea GET —decidido por EXCLUSION, porque `<form asp-action>` sin `method` renderiza POST y exigirlo escrito dejaria afuera la forma mas usada del repo, en silencio— y **48 de 87 vistas lo reciben, medido en el RAZOR COMPILADO** y no por lectura. La enforcement no puede ser opt-out en la fase 1 porque seria encender un rechazo global sobre ~35 metodos y 74 vistas de una vez, que es textualmente como nacieron `LP-114`/`LP-117`/`LP-121`. **`tools/VerificadorCoberturaTokenDeSubmit` enumera por codigo los POST que llegan a un escritor de plata y falla con exit 1 si alguno no esta cubierto ni declarado CON MOTIVO** — la diferencia con el bloque `MISMA FORMA` es que mentir en la lista ahora cuesta un rojo; probado quitando y devolviendo el atributo (exit 1 / exit 0), y tambien denuncia las excepciones MUERTAS. **SU HALLAZGO ES EL MAS IMPORTANTE DE LA RONDA: el perimetro real son 23 POST que escriben plata, no los 13 sitios que QA habia medido** — 1 cubierto, 5 del grupo A (clave natural ya cerrada), 4 del grupo B (defectos abiertos) y **13 del grupo C: sitios que la enumeracion encontro sola, sin parte de defecto ni evaluacion**, declarados como SIN EVALUAR (ni roto ni bien) e incluyendo tres REVERSIONES —la forma 'fila nueva' que `LP-114` ya contesto mal— y `Ventas/Facturar`, el sitio donde la clave natural no es aplicable ni en principio. Y llegar a 23 costo DOS correcciones del propio verificador, las dos por ejecucion: con un nivel de analisis daba 10 y **`Devoluciones/Registrar` no estaba** (el Controller llama a un Service que DELEGA el `new`), y escaneando solo metodos publicos **`NotasCredito/Emitir` tampoco** (el `new ComprobanteAfip` vive en el nucleo PRIVADO de la cascara) — *un verificador que no ve los dos sitios que ya sabemos que faltan no sirve para encontrar los que no sabemos*. **La decision 3 del diseño se respeto y se MIDIO: los locks de `PAT-059` no se tocaron**, y la afirmacion que lo prueba (`9.9`: tres POST en paralelo no facturan mas que lo vendido) **antes estaba TAPADA por la guarda retirada** — con la clave natural los tres salian por idempotencia y el lock no tenia que hacer nada. **El interino se retiro completo** (`VentanaDobleSubmitSegundos` y `CantidadComparable`, que quedo sin usos) y la familia 10 del arnes **se RETIRO en vez de dejarla midiendo una constante borrada**: `10.1`/`10.2` se absorbieron sin la espera real de 12 s (ahora corre en 52 ms, que es el criterio que ninguna ventana usable podia cumplir), `10.3` afirmaba lo CONTRARIO de lo correcto y `10.4` quedo sin objeto. La familia 9 se **reescribio y no se actualizo**, con `9.2` nuevo como **TRIPWIRE** (*el Service YA NO deduplica*): es la red del error mas probable de la fase 2, porque volver a poner una clave natural ahi reabre `LP-122`. El arnes baja de 111 a 96 afirmaciones, 15 retiradas con su motivo una por una y las de valor reconstruidas en el arnes nuevo. **`tools/ArnesTokenDeSubmit` (nuevo, 30/0): referencia Infrastructure Y Web y ejecuta el filtro de verdad** sobre el controller y la base reales, con los tres controles que el gate pidio por nombre — positivo (mismo token: 1 comprobante y LA RESPUESTA ORIGINAL), negativo (tokens distintos, payload identico, sub-segundo: **emiten los dos**) e IDOR (ni otro usuario ni otra accion). **15 mutantes**; cuando cinco marcas `[DISCRIMINA]` quedaron sin mutante que las matara **se escribieron los mutantes que faltaban** (`M11`–`M14`) en vez de bajarles la marca, y `7.3`/`7.4` si bajaron a `[COBERTURA]` con el motivo al lado. Los dos que mas enseñan no son los que mas tumban: **`M2` (leer-y-despues-insertar) tumba SOLO la familia 7** y deja las 6 afirmaciones de la serie en verde sobre codigo con una carrera abierta — la prueba de que concurrencia no es redundante con serie; y **`M4` tumba SOLO `4.4`** (valida usuario y no accion), o sea que sin esa afirmacion el IDOR seria media verdad medida como entera. **DOS TRAMPAS DE MEDICION, las dos invalidaron una corrida entera antes de verse:** (1) al borrar la constante, el arnes de CR-02 dejo de compilar y `--no-build` corrio **el EXE anterior**, dando 111/0 SOBRE EL CODIGO VIEJO — `tools/` no esta en la solucion y hay que mirar el RESULTADO del build, no su tiempo transcurrido; (2) **restaurar el mutante con `shutil.copy2` PRESERVA el mtime**, asi que el fuente restaurado queda mas viejo que la DLL, MSBuild no recompila y **el mutante sigue vivo en el binario mientras el `md5` contra el backup PASA** — es la unica trampa de la ronda que el control de integridad recomendado NO puede atrapar, y se destapo porque el control negativo empezo a fallar en verde-limpio con el mensaje de `M10`, restaurado tres corridas antes. El arnes nuevo arranco en **28/2 por un defecto propio**: leia `ActionExecutingContext.Result`, que esta VACIO cuando el filtro deja correr la accion; arreglarlo agrego `CorrioLaAccion`, que **termino siendo la mitad mas importante de la familia 2** — sin el, un replay que devuelve la respuesta correcta porque la accion volvio a correr pasa todas las afirmaciones habiendo duplicado la plata. Build no incremental **0 errores / 9 advertencias**, codigos `NU1902` + `CS0114`, linea base exacta. `appsettings.json`, `Seed` y `SeedData.cs` sin tocar (`LP-108`). Los 6 sitios con clave natural cerrada, `LP-118`, `LP-120`, `LP-117`, `LP-121`, `LP-112` y `LP-113` **sin tocar**: son fase 2. **Ningun defecto marcado como cerrado — `LP-122` lo cierra QA viendo el arnes en verde.**)
## Anterior 2: 2026-10-08 (v31 — **ronda de QA del 2026-10-08, lote 1 de fixes: guardas transaccionales y revocacion de acceso.** Lote de **GARANTIA** sobre alcance ya entregado y cobrado: **cero alcance nuevo, CERO MIGRACIONES** (la cola de produccion sigue en **12**), sin push y sin deploy. Seis defectos (`LP-088` critical, `LP-106` high, `LP-064` / `LP-082` / `LP-093` / `LP-095` major) **aplicados y PENDIENTES DE RE-VERIFICACION** — el cierre lo declara QA en contexto nuevo. **`LP-088` no era un defecto de comparacion sino de CUANDO se lee**: el tope comparaba contra `SaldoSinComprometer`, una **propiedad calculada del DTO** proyectada antes de abrir la transaccion, asi que el dato vencido viajaba dentro del DTO y la propiedad lo hacia *parecer fresco en el punto de uso*. **El lock no arregla el doble submit y la idempotencia no arregla el paralelo: las dos guardas son necesarias y ninguna sustituye a la otra**, y eso quedo escrito en el call site. Tres sitios se cerraron con el molde de `RegistrarAjusteAsync` (clave natural acotada al dia de negocio) y **cada uno con su costo declarado**; `GastoService` es el unico sin `BloquearAsync` porque **un gasto no tiene dueño** y lo serializa el CANDADO DEL PERIODO que ya estaba puesto. `LP-082` lleva la guarda en **LOS DOS caminos** (adelanto y devengamiento) y no solo en el que el parte nombraba. `LP-106` se arreglo en **las dos mitades** (rotar el stamp al togglear + chequear `Estado` en `OnValidatePrincipal`), y el `OnValidatePrincipal` **se CHAINEA y no se reemplaza** o se pisa la validacion de stamp de Identity — que es el unico mecanismo que hoy revoca al cambiar la password. **TRES DEFECTOS PROPIOS los encontro la MEDICION, no la lectura**: (a) el **ORDEN** de las dos guardas del pago estaba mal — con el tope primero, el doble submit del **saldo completo** (el caso mas frecuente) salia con *"supera el saldo"* en vez de reconocerse como duplicado; salio de un mutante que tumbo una afirmacion `[COBERTURA]`, y la salida facil era bajarle la marca; (b) **el escenario textual de `LP-088` ya no mide `LP-088`** — con `LP-095` arreglado, 3 POST identicos son un doble submit y los tres contestan exito idempotente, asi que QA tiene que mirar LAS FILAS y usar notas distintas para medir el tope; (c) **el lock de `OrdenesCompra` es redundante para un pago inmediato** (el candado del periodo ya serializa) y es el unico serializador para el pago **PROGRAMADO**, que no escribe caja — salio de un mutante que **no mato nada**, y un mutante que no mata nada no prueba que el codigo sobre: prueba que **falta el escenario**. **El bloque `MISMA FORMA` se rehizo por ENUMERACION y no ampliandolo a mano**, con su criterio de regeneracion escrito al lado: nombraba 2 sitios y ninguno de los 4 que QA encontro — se mantenia por memoria del que pasaba, y tres rondas de QA encontraron por separado un sitio que no estaba ahi. El barrido de los 15 escritores del ledger (~35 metodos) dejo **DOS escritores sin guarda que QA no reporto, declarados y NO arreglados** (`CajaMovimientoService.RegistrarMovimientoManualAsync`, gemelo exacto de `GastoService.CrearAsync`; y `ProveedorService.EditarAsync`, sin ningun lock) mas una **categoria nueva, "A con residual"** (tope bien releido bajo lock pero sin idempotencia: un doble submit PARCIAL duplica — `DevolucionService`, `FacturacionParcialService`, `NotaCreditoService`) y **uno que esta bien por accidente** (`ProveedorService.CrearAsync`, que depende de dos indices unicos sin declararlo en el call site). **Arnes nuevo `tools/ArnesLote1Guardas`: 34 OK / 0 FALLADAS**, exit 0, contra un clon desechable; **11 mutantes, union de tumbadas = conjunto `[DISCRIMINA]` = 28, el MISMO conjunto, cero `[COBERTURA]` caida**; **dos marcas mias estaban SUBdeclaradas** y subieron a `[DISCRIMINA]`; integridad de los 4 Services post-mutacion verificada con `md5sum` (los mutantes se revierten **desde el backup, nunca con `git checkout`**). **`LP-106` NO esta medido por el arnes y NO esta en verde: esta SIN MEDIR** — necesita el pipeline de autenticacion y una cookie, y el arnes lo imprime. Build no incremental **0 errores / 9 advertencias**: **lo que se compara son los CODIGOS** (`NU1902` + `CS0114`, los dos preexistentes) **y no el total, porque el total miente** — el incremental da 8 por no recompilar `Web`, y MSBuild tambien deduplica las de paquete entre el nivel `.slnx` y el nivel proyecto. `appsettings.json`, `Seed` y `SeedData.cs` **sin tocar** (`LP-108`, riesgo aceptado por el cliente). **El brief traia las rutas de proyecto equivocadas** (`FerreteriaLaPlatense.Infrastructure`/`.Web`, no `Infrastructure/`/`Web/`) y numeros de linea que no coincidian; el resto de sus datos medidos se verifico y estaba bien)

## Definiciones vigentes


### Certificado AFIP — clave privada generada, CSR pendiente de dos datos (2026-10-07)

**Estado:** la **clave privada ya existe** en `Certificados/privada.key` del repo del sistema (RSA **2048 bits**, verificada con `openssl rsa -check`). **No se vuelve a generar nunca**: el certificado que AFIP emita queda atado a ella, y si se pierde hay que rehacer el tramite completo.

**El CSR NO se genero**, y es a proposito: su subject lleva **la razon social exacta y el CUIT del contribuyente**, y ninguno de los dos existe en el proyecto — `AfipSettings.CUIT` esta vacio y no aparecen en ninguna parte de `/docs`. **Inventarlos produce un certificado que AFIP emite igual y que despues no autoriza nada**, y el error no se ve hasta el primer intento de facturar. La fuente de verdad es **una factura real ya emitida**, que es la misma que hay que pedirle al cliente para los datos impresos (ver el instructivo).

**Como se genera cuando lleguen los datos:** `Certificados/generar-csr.sh "<RAZON SOCIAL>" "<CUIT de 11 digitos>" [alias]`. El script valida el formato del CUIT, exige que la clave privada exista (y se niega a pisarla), arma el subject en el formato de AFIP — `/C=AR/O=<razon>/CN=<alias>/serialNumber=CUIT <cuit>` — e imprime el subject grabado para verificarlo **antes** de mandarlo. Sirve igual para la **renovacion a los dos anios**.

**Higiene aplicada:** el `.gitignore` del repo decia cubrir CSRs en su comentario (`# SSL/TLS material (claves privadas, certificados, CSRs)`) **y no tenia la regla**. Se agregaron `Certificados/` y `*.csr`, y se verifico por `git check-ignore` que la clave privada queda fuera del control de versiones. Mismo layout que `marihogar/Certificados/` (`privada.key`, `pedido.csr`, `certificado.crt`, el `.p12` final).

**Lo que sigue despues del CSR:** el cliente lo sube a AFIP y descarga su `.crt`; con ese `.crt` + `privada.key` se arma el `.p12` que carga el sistema. Y al cargarlo, **empezar directo por `X509KeyStorageFlags.MachineKeySet`**: en SmarterASP el flag por defecto falla con un error enganioso de archivo no encontrado, y `EphemeralKeySet` no funciono en ese hosting (instruccion 34, gotcha que costo 3 iteraciones en produccion).

### Estrategia de ramas Git por entrega (NUEVO, pedido explícito de Joaquín 2026-08-10)

Pedido: desarrollar las 3 entregas en 3 ramas separadas en cascada, con re-entrega y merge hacia adelante cuando una entrega ya delivered recibe mejoras/fixes post-entrega.

**Estructura creada:**
- `master` (rama por defecto del repo local, protegida como "lo ya entregado/production"): en `f5e6af9`, HEAD de Entrega 1.
- `entrega-1` ← creada desde `master` (mismo commit `f5e6af9`). Es donde se aplican las mejoras/fixes que surjan de la prueba del cliente sobre la Entrega 1 ya entregada.
- `entrega-2` ← creada desde `entrega-1`. Es donde se desarrolla la Entrega 2 (Ventas/AFIP/Caja/Entregas/Dashboard Corte 1).
- `entrega-3` ← creada desde `entrega-2`. Es donde se desarrolla la Entrega 3 (Compras/CtaCtes/Presupuestos/Devoluciones/Dashboard Corte final).

Las 3 ramas están pusheadas a `origin` (`git@gitlab.com:olvidata/ferreteria-la-platense.git`), cada una trackeando su par remoto.

**Flujo de trabajo (ciclo que se repite por cada entrega):**
1. Se desarrolla la entrega N en su rama `entrega-N`.
2. Se entrega al cliente para prueba (build + migración aplicada + guía de pasos manuales).
3. El cliente prueba y pide mejoras/fixes → se aplican **en la rama `entrega-N`** (no en una rama nueva).
4. Se re-entrega (vuelta al paso 2 tantas veces como haga falta).
5. Una vez aprobada la entrega N, se **mergea `entrega-N` hacia adelante** en todas las ramas de entregas posteriores todavía no entregadas (ej. al cerrar `entrega-1`: merge `entrega-1` → `entrega-2` y `entrega-1` → `entrega-3`), para que ningún fix se pierda cuando esas entregas posteriores continúen su propio desarrollo. También se mergea `entrega-N` → `master` (production) en este punto.
6. Se repite el ciclo con la entrega siguiente: mientras se desarrolla/prueba `entrega-2`, pueden seguir llegando mejoras sobre `entrega-1` — cada vez que eso pase, re-mergear `entrega-1` → `entrega-2` (y → `entrega-3` si ya existe contenido ahí) antes de la entrega de N+1.

**Regla operativa para el Implementador/QA:** antes de empezar a trabajar en una mejora o fix, confirmar en qué rama corresponde (la entrega ya entregada que la pide, NO necesariamente la rama activa de desarrollo) y hacer `git merge --no-ff entrega-N` hacia las ramas posteriores inmediatamente después de aplicar el fix, para minimizar drift entre ramas. No commitear el mismo fix de forma independiente en más de una rama (siempre merge, nunca reaplicar el cambio a mano en cada rama).

**Riesgo declarado:** el repo remoto ya tenía una rama `main` con un `README.md` inicial (commit `20e7f92`, historia no relacionada a la de `master`) creada por GitLab al momento de crear el proyecto — no se tocó, sigue siendo la rama por defecto en GitLab aunque todo el código real vive en `master`/`entrega-*`. Pendiente: decidir con Joaquín si en algún momento se hace merge/reemplazo de `main` para que coincida con la rama por defecto real del código, o si se cambia la default branch del proyecto en GitLab a `master`.

### Plan de entregas funcionales incrementales (NUEVO, pedido explícito de Joaquín 2026-08-10)

Pedido: dividir la Implementación (101h Etapa 1 + 38h Etapa 2 = 139h totales, ya presupuestadas y aprobadas por el cliente) en **3 entregas funcionales** que el cliente pueda empezar a probar/usar de forma incremental, en vez de esperar al cierre total del proyecto. Motivo declarado: dar dinamismo al proyecto y entregar valor real antes de tiempo.

**Criterio de armado:** cada entrega es un conjunto de módulos con dependencias satisfechas únicamente por entregas anteriores (nunca hacia adelante) — ver mapa de dependencias en `3-arquitecto-mvc.md` — y agrupados temáticamente para que el cliente pueda probar un ciclo de trabajo coherente, no piezas sueltas. El total de horas coincide exacto con el WBS ya aprobado (139h) — **no es una re-estimación**, es una reorganización de secuencia de entrega sobre el mismo alcance y precio ya cerrado con el cliente.

#### Entrega 1 — Fundamentos: Catálogo, Stock y Usuarios (30h)

| Módulo (ref. WBS) | M (h) |
|---|---:|
| 1. Usuarios y roles (admin/vendedor/repartidor) | 5 |
| 2. Catálogo de productos (marca/modelo/categoría/IVA/descuento) | 9 |
| 3. Unidades de medida y conversión compra↔venta | 5 |
| 4. Stock + puesta a punto inicial (ABC, ajuste manual auditado, arranque con negativo permitido) | 8 |
| 11. Código de barras (vinculación al producto) | 3 |
| **Subtotal** | **30** |

**Por qué va primero:** no depende de ningún módulo de Ventas/Compras/Caja — es 100% autocontenida. Ataca directamente el problema real más urgente que el cliente declaró en el relevamiento ("hoy no tenemos stock confiable, se maneja de memoria por la rotación") antes de que el resto del sistema esté terminado. El cliente puede empezar a cargar su catálogo real y clasificar ABC mientras se construyen las entregas 2 y 3.

**Qué puede probar el cliente al cierre de esta entrega:** alta/edición de usuarios por rol; alta de marcas/modelos/categorías; alta de productos con conversión de unidad de compra↔venta; clasificación ABC de productos; ajuste manual de stock con motivo auditado; vinculación de código de barras a un producto.

#### Entrega 2 — Motor de ventas: Ventas, Facturación AFIP, Caja y Entregas (61h)

| Módulo (ref. WBS) | M (h) |
|---|---:|
| 5. Ventas + CC clientes (workflow Borrador→Facturada, recargo cuotas) | 23 |
| 6. Facturación AFIP (Factura) | 7 |
| 8. Caja (cierre diario + mensual) | 7 |
| 9. Gastos varios | 4 |
| 15. Entregas a domicilio (markup, propia/tercerizada) | 8 |
| 10. Dashboard — **Corte 1**: nivel 1 "estado del día" + nivel 3 "tendencias" | 12 |
| **Subtotal** | **61** |

**Por qué va segunda:** depende de Producto (Entrega 1). Es el ciclo diario de venta — la operación central del negocio — y concentra el mayor riesgo técnico del proyecto (workflow editable + integración AFIP), por lo que queda aislada en su propia entrega para poder dedicarle foco de prueba sin bloquear el resto. Se adelanta "Entregas a domicilio" desde la Etapa 2 original porque el nivel 1 del Dashboard necesita datos de entregas pendientes del día — sin este adelanto, el primer corte del dashboard quedaría incompleto.

**Dashboard en 2 cortes (no es una re-estimación, es fasear el mismo módulo de 12h ya presupuestado):** el diseño ya define el dashboard en 3 niveles jerárquicos (día / salud financiera / tendencias — ver `2-disenador-funcional.md` flujo 6). Nivel 1 (ventas de hoy, caja del día, entregas pendientes) y nivel 3 (gastos del mes, top productos, stock crítico) solo necesitan datos que ya existen al cierre de esta entrega. Nivel 2 (cobros/pagos pendientes, saldo de caja consolidado) necesita CC proveedores y el consolidado del negocio — ver Entrega 3.

**Qué puede probar el cliente al cierre de esta entrega:** venta rápida con carrito editable (cantidad/precio/IVA/descuento por ítem) en estado Borrador; pago mixto (efectivo + tarjeta + fiado) con recargo de cuotas calculado; emisión de comprobante AFIP real; fiado con seguimiento de saldo por cliente; cierre de caja diario y mensual; registro de gastos; seguimiento de entregas a domicilio; primer corte del dashboard con datos reales de venta/caja/stock.

#### Entrega 3 — Ciclo completo: Compras, Cuentas corrientes y Cierre de negocio (48h)

| Módulo (ref. WBS) | M (h) |
|---|---:|
| 7. Proveedores + compras (TC propio, % descuento, importación de listas) | 18 |
| 12. Cuenta corriente de empleados (autoservicio) | 4 |
| 13. Cuenta corriente propia del negocio (consolidado) | 5 |
| 14. Presupuestos y cotizaciones en PDF | 8 |
| 16. Aumento masivo de precios (categoría/proveedor/marca) | 4 |
| 17. Devoluciones de mercadería + Notas de crédito/débito AFIP | 9 |
| 10. Dashboard — **Corte final**: nivel 2 "salud financiera" | (incluido en los 12h de Entrega 2) |
| **Subtotal** | **48** |

**Por qué va tercera:** Devoluciones/NC depende de Venta Facturada + AFIP (Entrega 2). Aumento masivo por proveedor depende de Proveedor (mismo módulo, esta entrega). CtaCte consolidada del negocio depende de Caja+Gastos (Entrega 2) y de Compras (esta entrega). Ninguno de estos módulos es prerequisito de las entregas anteriores — cierran el ciclo completo del negocio (compras, cuentas corrientes, devoluciones) sin bloquear valor entregado antes.

*Nota: "Cuenta corriente de empleados" (módulo 12) solo depende de Usuarios (Entrega 1) — no tiene bloqueo técnico para adelantarse a la Entrega 2 si el cliente prioriza verlo antes. Se mantiene en Entrega 3 por afinidad temática (cuentas corrientes) salvo pedido explícito de reordenar.*

**Qué puede probar el cliente al cierre de esta entrega (= cierre del proyecto):** registro de compras con actualización de stock; importación de lista de precios de proveedor con TC propio + % descuento; cuenta corriente de proveedores; cuenta corriente de empleados (autoservicio); cuenta corriente consolidada del negocio; presupuestos/cotizaciones en PDF; aumento masivo de precios; devolución de mercadería con nota de crédito AFIP y anulación de venta; dashboard completo (3 niveles).

#### Verificación de consistencia con el presupuesto aprobado

- Suma de las 3 entregas: 30h + 61h + 48h = **139h = Etapa 1 (101h) + Etapa 2 (38h) del WBS aprobado.** Ningún módulo se agregó ni se quitó — solo se reordenó la secuencia de entrega.
- El precio ya cerrado con el cliente (USD 1.500/3 pagos o USD 1.800/12 pagos) **no cambia** — esto es una decisión de secuenciación de Implementación, no una re-cotización. Ver `4-presupuestador.md`.
- Encaje comercial natural (a proponer, no impuesto): las 3 entregas funcionales quedan alineadas 1 a 1 con la modalidad de pago en 3 cuotas si el cliente la elige — cada entrega cerrada puede disparar el cobro de la cuota correspondiente. Si el cliente eligió la modalidad de 12 pagos, las entregas funcionan igual como hitos de prueba, sin atarse a cuotas individuales.

### Archivos y capas modificadas

**Cierre de Entrega 1 (2026-08-10) — Catálogo, Stock y Usuarios.** Repo: `C:\Sistemas\Ferreteria La Platense`, solución `FerreteriaLaPlatense.slnx`.

Reutilización aplicada (ver escaneo debajo): patrón de `Marca`/`Modelo`/`Categoria` de `ShowroomGriffin`, patrón de `AjusteStock`/`StockController` de `ShowroomGriffin`, helper `DataTableRequestHelper` de `marihogar`.

- **Domain** (`FerreteriaLaPlatense.Domain`):
  - `Enums/UnidadMedida.cs` (Unidad/Peso/Metro/Bulto), `Enums/ClasificacionABC.cs` (A/B/C) — nuevos.
  - `Entities/ICatalogoSimpleEntity.cs` — contrato común (Nombre/Activo) para no triplicar el CRUD de los 3 catálogos simples.
  - `Entities/Marca.cs`, `Entities/Modelo.cs`, `Entities/Categoria.cs` — nuevas, heredan `SoftDestroyable` + `ICatalogoSimpleEntity` (Nombre, Activo).
  - `Entities/Producto.cs` — nueva, núcleo de la entrega (todas las columnas de `3-arquitecto-mvc.md`: precios, IVA, unidades de compra/venta + `FactorConversion`, `Stock`, `StockMinimo`, `ClasificacionABC`, `StockVerificado`, `CodigoBarras`).
  - `Entities/AjusteStock.cs` — nueva (ProductoId, Fecha, UsuarioId, CantidadAnterior, CantidadNueva, Motivo).
- **Application** (`FerreteriaLaPlatense.Application`):
  - `DTOs/CatalogoItemDto.cs`, `DTOs/ProductoDtos.cs` (ProductoListItemDto/ProductoDto/ProductoLookupDto), `DTOs/StockDtos.cs` (StockListItemDto con `Alerta` calculada, AjusteStockDto, AjusteStockHistorialItemDto) — nuevos.
  - `Interfaces/ICatalogoSimpleService.cs` (+ marcadoras `IMarcaService`/`IModeloService`/`ICategoriaService`), `Interfaces/IProductoService.cs`, `Interfaces/IUnidadMedidaConversionService.cs`, `Interfaces/IAjusteStockService.cs`, `Interfaces/ICodigoBarrasLookupService.cs` — nuevos, todos los contratos funcionales pedidos por `2-disenador-funcional.md`.
- **Infrastructure** (`FerreteriaLaPlatense.Infrastructure`):
  - `Data/AppDbContext.cs` — agregados `DbSet<Marca/Modelo/Categoria/Producto/AjusteStock>` + Fluent API (índices únicos en `Nombre`/`Codigo`/`CodigoBarras`, precisión decimal, `OnDelete(Restrict)` en las FK a los catálogos).
  - `Data/SeedData.cs` — agregados roles `Vendedor` y `Repartidor` al array de seed (antes solo `SuperUsuario`).
  - `Services/CatalogoSimpleServiceBase.cs` — clase base genérica (CRUD + listado DataTable + validación de unicidad + bloqueo de baja si el catálogo está en uso por un Producto) reutilizada por `MarcaService`, `ModeloService`, `CategoriaService`.
  - `Services/ProductoService.cs` — CRUD + `ListarAsync` (DataTable con filtros) + validación de negocio en el Service (R4: `FactorConversion` obligatorio y > 0 si `UnidadCompra != UnidadVenta`; unicidad de `Codigo`/`CodigoBarras`; IVA en {10,5; 21}).
  - `Services/UnidadMedidaConversionService.cs` — cálculo simple (multiplicación por `FactorConversion`), sin precedente exacto en el historial, tal como anticipó `3-arquitecto-mvc.md`.
  - `Services/AjusteStockService.cs` — listado de Stock con `Alerta` (stock negativo o bajo el mínimo), `AplicarAjusteAsync` (registra auditoría + pisa `Producto.Stock` + `StockVerificado = true`), `HistorialAsync`.
  - `Services/CodigoBarrasLookupService.cs` — resuelve producto por `CodigoBarras` o `Codigo`.
  - `DependencyInjection.cs` — registrados como Scoped: `IMarcaService`, `IModeloService`, `ICategoriaService`, `IProductoService`, `IUnidadMedidaConversionService`, `IAjusteStockService`, `ICodigoBarrasLookupService`.
- **Web** (`FerreteriaLaPlatense.Web`):
  - `Helpers/DataTableRequestHelper.cs` — parseo estándar de `Request.Form` a `DataTableRequest` (adaptado de `marihogar`), reutilizado por todos los controllers nuevos.
  - `Models/CatalogoSimpleFormViewModel.cs`, `Models/ProductoFormViewModel.cs` (con combos `SelectListItem` para Marca/Modelo/Categoria), `Models/AjusteStockViewModel.cs` — nuevos.
  - `Controllers/MarcasController.cs`, `Controllers/ModelosController.cs`, `Controllers/CategoriasController.cs` — CRUD + `Listar` (DataTable server-side) + `ListarActivas` (combo). Policy `RequireCatalogoConsulta` a nivel de clase (lectura), `RequireSuperUsuario` en Create/Edit/Delete.
  - `Controllers/ProductosController.cs` — CRUD + `Listar` (DataTable con filtros: texto libre, Marca, Modelo, Categoria, rango de Precio, rango de Stock) + `BuscarPorCodigoBarras` (endpoint de prueba de `ICodigoBarrasLookupService`, reutilizable por Ventas en la Entrega 2). Combos en Editar se inicializan con la Marca/Modelo/Categoria ya asignada aunque esté inactiva (regla `32-estandares-qa-implementador.instructions.md`).
  - `Controllers/StockController.cs` — `Listar` (DataTable con alerta), `Ajuste` (GET/POST, solo Admin), `Historial`/`HistorialListar`.
  - `Controllers/UsersController.cs` — `GetAssignableRoles()` extendido a `[SuperUsuario, Vendedor, Repartidor]` (antes solo `SuperUsuario`); no se reescribió el resto del controller ni las Views de Usuarios (ya soportaban una lista dinámica de roles).
  - `Program.cs` — nueva policy `RequireCatalogoConsulta` (`SuperUsuario` + `Vendedor`).
  - `Views/Marcas/*`, `Views/Modelos/*`, `Views/Categorias/*` (Index con DataTable server-side + filtros Nombre/Estado, Create, Edit), `Views/Productos/*` (Index con DataTable + filtros por cada columna visible + buscador de código de barras, Create, Edit con card de Stock de solo lectura), `Views/Stock/*` (Index con alerta visual, Ajuste, Historial) — nuevas, con SweetAlert2 para confirmaciones destructivas y DataTables server-side en todos los listados.
  - `Views/Shared/_Layout.cshtml` — nueva sección de sidebar "Catálogo" (Productos/Stock/Marcas/Modelos/Categorías), visible a `SuperUsuario` y `Vendedor`, respaldada por `[Authorize(Policy=...)]` en cada controller (defensa en profundidad).

**Escaneo de reutilización realizado antes de codificar:** se revisó `docs/ShowroomGriffin/definiciones/5-implementador.md` (no existe un `5-implementador.md` de reutilización directa en ese proyecto, pero sí código de referencia real en `C:\Sistemas\ShowroomGriffin` — `Marca`/`MarcaConfiguration`/`MarcasController`/`MarcaService` y `AjusteStock`/`AjusteStockConfiguration`/`StockController`) y `marihogar` (`CategoriaService`, `DataTableRequestHelper`). Decisión: reutilizar el patrón (estructura de entidad, Fluent API, forma del Controller/Service) adaptándolo a las diferencias reales de este proyecto — acá el repositorio usa `IRepository<T>` genérico para las mutaciones (en vez de `AppDbContext` directo como en ShowroomGriffin) y el stock vive directamente en `Producto` (no hay `Stock`/`VarianteProducto` separados, porque este catálogo no tiene variantes).

### Migraciones EF generadas
- `EntregaUno_CatalogoStockUsuarios` (20260810165155) — **primera migración real del proyecto** (no había ninguna previa). Incluye: todo el esquema base de Identity (`AspNetUsers`, `AspNetRoles`, etc., `Notifications`, `PreferenciasUsuario` — ya existían en código pero nunca se habían migrado) + las tablas nuevas de esta entrega: `Marcas`, `Modelos`, `Categorias` (Nombre único, Activo), `Productos` (FK Restrict a Marca/Modelo/Categoria, índices únicos en `Codigo` y `CodigoBarras`, decimales con precisión `18,2`/`5,2`/`18,3` según el campo), `AjustesStock` (FK Restrict a Producto).
- Generada con `dotnet ef migrations add EntregaUno_CatalogoStockUsuarios --project FerreteriaLaPlatense.Infrastructure --startup-project FerreteriaLaPlatense.Web`. **No se aplicó contra ninguna base de datos** (el Implementador no ejecuta `dotnet ef database update` ni levanta la app — ver guía de verificación manual en la sección de pruebas). El `HostAbortedException` que aparece en la consola al generarla es el comportamiter normal de la tooling de EF Core (aborta el host de diseño a propósito), no un error.
- Impacto: sobre una base nueva, `database update` crea todo el esquema. Sobre una base ya con datos reales del cliente (no es el caso hoy — el proyecto no tiene datos de producción todavía), habría que revisar si `AspNetUsers`/`Notifications`/`PreferenciasUsuario` ya existen antes de aplicarla.

### Riesgos residuales
- Pregunta abierta sin cerrar con el cliente (no bloquea Entrega 1, sí bloquea el módulo de anulación en Entrega 3): quién puede anular una venta facturada (¿solo admin o también vendedor?) y si hay límite de tiempo — ver `1-analista-funcional.md` §9.
- Riesgos técnicos ya declarados en `3-arquitecto-mvc.md` (venta con stock negativo permitido, conversión de unidades sin precedente, workflow Venta editable, importación de listas por proveedor no 100% genérica) se mantienen vigentes, sin cambios por esta reorganización.
- **Nuevo (Entrega 1):** `Producto.CodigoBarras` es único a nivel de base (MySQL permite múltiples `NULL`, así que productos sin código de barras coexisten sin problema) — si el cliente en algún momento pide códigos de barras "sugeridos" no únicos (ej. balanza con código variable por peso) el modelo actual no lo soporta y habría que revisar el índice único.
- **Nuevo (Entrega 1):** la hipótesis de `2-disenador-funcional.md` ("el factor de conversión es fijo por producto") queda **codificada tal cual** en `UnidadMedidaConversionService` — si el cliente confirma que un mismo producto llega en bultos de distinto tamaño según el proveedor, este servicio y el modelo de `Producto` necesitan revisión antes de la Entrega 2 (Compras).
- **Nuevo (Entrega 1):** al ajustar manualmente el stock (`AjusteStockService.AplicarAjusteAsync`), la cantidad nueva **pisa** el stock actual (no lo suma/resta) — es el comportamiento pedido ("cantidad nueva", no "cantidad a sumar"); confirmar con el cliente que esto matchea su expectativa operativa antes de que lo use el personal de mostrador.
- **Nuevo (Entrega 1):** `Marca`/`Modelo`/`Categoria` bloquean la baja física (soft delete) si hay algún `Producto` activo que los referencia (mensaje explícito, sugiere desactivar en su lugar) — esto es una regla de integridad agregada por el Implementador (no estaba explícita en `3-arquitecto-mvc.md`), coherente con el patrón ya usado en `marihogar`.
- **Nuevo (Entrega 1):** no se generó ninguna migración de datos/seed para Marca/Modelo/Categoria — el catálogo arranca vacío, el cliente carga sus propias marcas/modelos/categorías antes de poder cargar productos.

### Ajuste puntual (2026-08-10, post-QA/GO) — rol Administrador + redirect post-login a Stock

Modificacion sobre modulo existente (Entrega 1 ya en GO), no una entrega nueva. Pedido explicito de Joaquin (ver `trazabilidad.md` 2026-08-10 17:00 y 17:30): agregar un rol **Administrador** con acceso a todo el sistema salvo las herramientas tecnicas de `SystemController` (exclusivas de `SuperUsuario`, acceso tecnico de Olvidata Soft), y redirigir a `Stock/Index` despues del login en vez de `Home/Index`.

- **Infrastructure** (`FerreteriaLaPlatense.Infrastructure`):
  - `Data/SeedData.cs` — agregado `public const string RolAdministrador = "Administrador"` y sumado al array `roles` de `InitializeAsync` (se crea automaticamente en el seed).
- **Web** (`FerreteriaLaPlatense.Web`):
  - `Program.cs` — nueva policy `RequireAdministracion` (`SuperUsuario` + `Administrador`); `RequireCatalogoConsulta` extendida para incluir `Administrador`. `RequireSuperUsuario` sin cambios (sigue exclusiva de `SystemController` y `/health`).
  - `Controllers/MarcasController.cs`, `Controllers/ModelosController.cs`, `Controllers/CategoriasController.cs`, `Controllers/ProductosController.cs`, `Controllers/StockController.cs` — todas las acciones de escritura (`Create`/`Edit`/`Delete`/`Ajuste`) cambiaron de `[Authorize(Policy = "RequireSuperUsuario")]` a `[Authorize(Policy = "RequireAdministracion")]`.
  - `Controllers/UsersController.cs` — atributo de clase cambiado a `RequireAdministracion`; `GetAssignableRoles()` extendido a `[SuperUsuario, Administrador, Vendedor, Repartidor]`. Administrador gestiona usuarios igual que SuperUsuario, incluida la asignacion del rol `SuperUsuario` a otro usuario desde esta pantalla — decision de negocio confirmada explicitamente por Joaquin, no limitada por criterio propio.
  - `Controllers/SystemController.cs` — **no tocado**, sigue exclusivo de `RequireSuperUsuario` (unica excepcion explicita del pedido).
  - `Controllers/AccountController.cs` — `Login` GET (shortcut si ya autenticado) y `Login` POST (exito) redirigen por defecto a `Stock/Index` en vez de `Home/Index`; se preserva `returnUrl` si el usuario venia de un deep-link. `Logout` y `AccessDenied` sin cambios.
  - `Views/Home/Index.cshtml`, `Views/Stock/Index.cshtml`, `Views/Marcas/Index.cshtml`, `Views/Modelos/Index.cshtml`, `Views/Categorias/Index.cshtml`, `Views/Productos/Index.cshtml` — `User.IsInRole("SuperUsuario")` cambiado a `(User.IsInRole("SuperUsuario") || User.IsInRole("Administrador"))` en los botones de alta/edicion/baja y en la card de "Administrar Usuarios" de Home.
  - `Views/Shared/_Layout.cshtml` — sidebar "Catalogo" (Productos/Stock/Marcas/Modelos/Categorias) extendido a `SuperUsuario || Administrador || Vendedor`. Sidebar "Sistema" reestructurado: el link "Sistema / Email" (`SystemController`) quedo aislado en un `if` propio exclusivo de `SuperUsuario`; "Usuarios" y "Notificaciones" ahora se muestran tambien a `Administrador` (el `if` contenedor paso a `SuperUsuario || Administrador`).
- **Migraciones EF**: ninguna — los roles de Identity (`AspNetRoles`) no requieren cambio de esquema, se crean via seed en `InitializeAsync`.
- **Build**: `dotnet build FerreteriaLaPlatense.slnx` → 0 errores, mismas advertencias preexistentes (NU1902 MailKit/MimeKit, CS0114 en `HomeController`).
- **No se ejecuto smoke test funcional** (regla del rol Implementador) — ver guia de pruebas manuales mas abajo.

**Correccion inmediata (2026-08-10, minutos despues del cierre anterior):** Joaquin corrigio el alcance — gestion de Usuarios y Herramientas del Sistema quedan **exclusivas de `SuperUsuario`**, Administrador es "todo lo demas" (Catalogo/Stock, que si quedan en `RequireAdministracion`). Revertido:
- `Controllers/UsersController.cs` — atributo de clase vuelto a `[Authorize(Policy = "RequireSuperUsuario")]` (estaba en `RequireAdministracion`). `GetAssignableRoles()` sin cambios (Administrador sigue siendo un rol asignable desde esta pantalla, solo que ahora unicamente SuperUsuario puede entrar a asignarlo).
- `Views/Shared/_Layout.cshtml` — separado el bloque: "Usuarios" y "Sistema / Email" quedan bajo `@if (User.IsInRole("SuperUsuario"))` exclusivamente; "Notificaciones" se sacó de ese `if` (no tiene restriccion de rol en `NotificationsController`, es personal de cualquier usuario autenticado) para que Administrador (y en rigor cualquier rol) la siga viendo.
- Build no pudo confirmar el paso final de copia (`MSB3027`, archivo `.dll` en uso por un proceso `dotnet FerreteriaLaPlatense.Web.dll` corriendo en paralelo, PID 22748) — 0 errores de compilacion de codigo, solo fallo el copy-to-output por lock de archivo. Cambios de bajo riesgo (revertir un valor de atributo + condicionales Razor con sintaxis ya probada en otras vistas del mismo archivo).

### Riesgos residuales y asunciones (Entrega 2, ola 1)

1. **AFIP sin datos reales (bloqueante solo para probar, no para el código):** no hay CUIT ni certificado `.p12` de La Platense todavía. `AfipService.EmitirAsync` devuelve `Exito=false` con `DetalleError` explícito mientras `Afip:CertificadoPath`/`Afip:CUIT` estén vacíos en `appsettings` — comportamiento igual al ya validado en marihogar, no bloquea el resto del sistema. No hay nada para probar de punta a punta contra AFIP real hasta que el cliente traiga esos datos.
2. **Asunción sobre Descuento/Recargo de `ItemVenta`:** se modelaron como importes monetarios de la línea, no porcentajes — `3-arquitecto-mvc.md` no precisa la unidad. A confirmar con el cliente en la prueba de esta entrega.
3. **Asunción sobre el recargo de cuotas:** a diferencia de marihogar (donde el interés es solo informativo), aquí el recargo de `CreditoCuotas` se suma efectivamente al `Venta.Total` (tal como pide `2-disenador-funcional.md`: "el sistema calcula el recargo... y lo suma al total antes de confirmar"). El `PagoVenta.Monto` es el importe **base** financiado; el recargo se calcula aparte (`Monto * %/100`) y se agrega al total — no hay un campo adicional en el modelo para el "monto con recargo", se reconstruye en tiempo de cálculo.
4. **Asunción sobre cobertura de pagos:** se exige que la suma de pagos (+ recargo de cuotas) cubra el `Total` de la venta, **salvo** que exista alguna línea de pago `CuentaCorriente` (en cuyo caso no se exige cobertura completa — el saldo pendiente ahí es intencional, tal como pide el diseño). No hay una regla de "monto exacto restante" automático: el vendedor decide cuánto carga a la cuenta corriente escribiendo el monto de esa línea.
5. **% de recargo por cuotas sin pantalla propia de configuración:** se resolvió con una sección de `appsettings.json` (`RecargoCuotas`) en vez de una pantalla de administración — `2-disenador-funcional.md` no define una pantalla específica para esto. Si el cliente pide poder cambiarlo sin depender de un despliegue/reinicio, hay que migrar `RecargoCuotasSettings` a una entidad con su propio CRUD (el contrato `IRecargoCuotasService` no cambiaría).
6. **Filtro de "Comprobante" no implementado en el listado de Ventas:** la columna "Comprobante" (número/CAE) se muestra en la grilla pero no tiene un filtro de columna dedicado (a diferencia del resto de columnas, que sí cumplen la regla de `25-frontend-design-system.instructions.md`) — desvío menor, documentado para no perderlo de vista en QA.
7. **`Marca`/`Modelo`/`Categoria` y `Producto` no se tocaron** salvo la extensión mínima de `IProductoService`/`ProductoService` (nuevo método `BuscarParaVentaAsync`, aditivo, sin cambiar comportamiento existente).
8. El descuento de stock al facturar permite negativo sin bloquear (R10/PF13, ya resuelto en Entrega 1) — no se agregó ninguna validación nueva de stock en `VentaWorkflowService`.
9. `IUnidadMedidaConversionService` (Entrega 1) **no tiene un call-site real en Venta**: el ítem siempre se carga en `UnidadVenta` (no hay conversión compra→venta en el flujo de venta, eso es exclusivo de Compras). Se documenta en vez de forzar un uso artificial del servicio solo para cumplir la letra del pedido — el servicio queda disponible sin cambios para cuando se implemente Compras.

### Riesgos residuales y asunciones (Entrega 2, ola 2)

1. **Interpretación del markup de Entrega (R2):** se asumió `CostoFinal = CostoBase * (1 + PorcentajeMarkup/100)` (markup sobre el costo de envío, no sobre el valor del producto/venta) — `3-arquitecto-mvc.md` no distingue explícitamente entre ambas lecturas. A confirmar con el cliente.
2. **CajaMovimiento por PagoVenta, no por Venta:** se generó un `CajaMovimiento` por cada línea de `PagoVenta` (excepto CuentaCorriente), no uno consolidado por Venta — permite ver en Caja el desglose por medio de pago, pero implica varias filas de Caja para una sola venta con pago mixto. Documentado como decisión de diseño, no contradice `3-arquitecto-mvc.md` (que no precisa el nivel de agregación).
3. **Cierre mensual independiente del diario:** `CerrarMesAsync` no exige que los días del mes ya estén cerrados individualmente — agrega `CajaMovimiento` directo por rango de fecha. Si el cliente espera que el cierre mensual dependa de los cierres diarios (ej. bloquear el cierre de mes si falta cerrar algún día), hay que agregar esa validación.
4. **Entregas sin cobro en destino ni intentos históricos:** a diferencia de marihogar, no se implementó `EntregaIntento` (historial de intentos fallidos) ni el cobro en destino vía `PagoVenta` — no hay pedido funcional explícito de esto en `1-analista-funcional.md`/`2-disenador-funcional.md` para La Platense. Si el cliente lo pide, es una extensión aditiva sobre `IEntregaService` sin romper lo ya construido.
5. **Acceso a Caja/Gastos exclusivo de Administrador:** interpretado de la tabla de permisos del analista ("Vendedor: ventas, catálogo consulta, stock consulta, su propia CC" — no menciona Caja/Gastos). Si el cliente espera que el Vendedor consulte (no necesariamente escriba) Caja/Gastos, es un cambio de policy de una línea.
6. **Dashboard sin reducción de contenido por rol:** a diferencia de marihogar (que reduce el dashboard de Vendedor), en este corte cualquier usuario autenticado ve el mismo contenido — nivel 1/3 no expone datos que la tabla de permisos restrinja explícitamente. A revisar si el cliente considera que Caja/Gastos del día son datos sensibles que el Vendedor no debería ver ni en el Dashboard.
7. **Top productos y gastos del mes acotados al mes calendario actual** — asunción documentada, sin precedente explícito en `2-disenador-funcional.md`.
8. **Guarda de "día cerrado" aplicada de forma amplia:** tanto el alta de Gasto como la confirmación de Venta (para la fecha de hoy) y la anulación de Gasto (fecha de hoy) quedan bloqueadas si esa fecha ya tiene `CierreCajaDiario`. Esto significa que, una vez cerrada la caja de hoy, **no se puede seguir vendiendo ni registrando gastos hasta el otro día** — comportamiento coherente con un cierre de caja físico real, pero a confirmar explícitamente con el cliente antes de que el personal de mostrador lo experimente en producción.
9. **`Marca`/`Modelo`/`Categoria`/`Producto`/`Cliente`/`Venta` no se tocaron** salvo la extensión aditiva de `IProductoService`/`ProductoService` (`ContarStockCriticoAsync`) y la modificación de `VentaWorkflowService` (integración con Caja, ya declarada arriba).

### LP-014 / LP-016 — Gate de precio y de alicuota por rol: CERRADO, verificado contra el codigo

**Estado: cerrado desde el 2026-10-05, confirmado por lectura el 2026-10-06.** Esta entrada existe porque el brief de la ronda de CR-01/CR-02 lo declaraba **abierto en produccion**, con numeros de linea, y lo puso como primer item del lote. Era falso en ese HEAD, y QA ya lo habia dado PASS (`6-qa.md`, criterio 4).

Lo que esta efectivamente construido, verificado archivo por archivo:

- `VentasController.GuardarBorrador` resuelve `EsAdministrador` con `User.IsInRole` sobre el `ClaimsPrincipal` del request; **nunca** viaja en el formulario. `GuardarVentaBorradorDto.EsAdministrador` es `init`.
- `GuardarBorradorAsync` solo lee `PrecioUnitario`/`Descuento`/`Recargo` del payload cuando ese flag es `true`. Para cualquier otro rol (o caller) el precio se recalcula desde el `Producto` y descuento y recargo quedan en 0, **descartando el payload en silencio y sin excepcion** — no es un error del usuario, la UI simplemente no le deja editar esos campos.
- **LP-016:** el `% de IVA` no se lee del payload para **ningun** rol, administrador incluido: `porcentajeIva = producto.PorcentajeIVA`. La alicuota es un atributo fiscal del producto, no una palanca comercial.
- La UI acompaña sin ser la garantia: los inputs van `readonly` (no `disabled`, que no se postearia) y el input de IVA **no tiene `name`**, asi que no viaja.

**Lo unico que quedaba era un comentario vencido, y es un `LP-008` de manual:** el bloque de seguridad de `GuardarBorradorAsync` seguia declarando que "el % de IVA de la linea sigue llegando del payload para los dos roles" y lo dejaba como deuda abierta. `LP-016` lo habia cerrado en la misma ronda, unas lineas mas abajo, y nadie actualizo el comentario — una regla de negocio **falsa** viviendo justo en el bloque que alguien va a leer para saber si el agujero esta cerrado. Corregido.

**Por que importa para CR-01:** LP-014 era precondicion real, no ceremonia. Con el gate cerrado, "sin factura" pasa a ser la **unica** forma que tiene un Vendedor de bajar el total — y es una decision comercial explicita, registrada en la venta y visible en el listado, no un numero tipeado que no deja rastro.

### CR-01 — Venta sin factura: `Venta.Facturar` y el IVA por condicion

`Venta.Facturar` (bool, **default `true` en la BASE**, no solo como inicializador de la propiedad: el default de C# no alcanza a las filas que ya existen, y es lo que hace la migracion aditiva y sin backfill — toda venta historica queda "con factura", que es lo que fue). Con `false`, el IVA de **todas** las lineas es 0 y el total es la suma de los netos (R12).

**La regla vive en un solo lugar:** `VentaWorkflowService.CalcularIva(item, facturar)`, invocado desde `RecalcularTotales`. El proyecto ya midio lo que cuesta la alternativa: el barrido `LP-002` del 2026-10-05 encontro la regla de la oferta vigente escrita en **4 lugares**.

**Lo que NO se hace, y es la decision de fondo: no se pisa `ItemVenta.PorcentajeIVA` con 0.** Esa alicuota es el atributo fiscal del producto (`LP-016`) y es exactamente el dato que la facturacion parcial necesita despues para calcular el IVA a cobrarle al cliente. Si se la pisara al vender, el comprobante posterior no tendria de donde sacarla y habria que ir a buscarla al producto, que a esa altura pudo cambiar. **La condicion de la venta decide si el IVA se COBRA; el porcentaje de la linea sigue diciendo cuanto le corresponde a ese producto.** Verificado ejecutando (afirmacion 1.7 del arnes): tras confirmar una venta sin factura, las alicuotas persistidas siguen siendo `[21, 10,50, 21, 10,50, 21]`.

**Se congela al confirmar por construccion, no por un `if`:** `GuardarBorradorAsync` es el unico metodo que la escribe, y sus dos ramas ya garantizan `Estado == Borrador` (el alta la crea asi; la edicion lo exige con la relectura bajo lock). Confirmar/Facturar/Anular no la tocan.

**`Facturar` entra en la guarda optimista de `LP-038` de `ConfirmarAsync`, y esto es lo que mas vale de la entrada.** Es un dato nuevo que **decide** el total que se postea, y `RecalcularTotales` lo lee del grafo cargado **antes** del lock: la forma exacta de `LP-038`. El `Total` solo no alcanza, y se midio: con todas las lineas al 0% de IVA, girar la palanca deja los cinco numeros que la guarda ya comparaba **identicos** (total, cantidad de lineas, suma de unidades, suma de pagos) y la unica diferencia observable es el flag. **Contraprueba ejecutada** (sacar ese campo de la guarda y volver a correr): la venta queda **Confirmada con la condicion girada, $ 2.000 de caja posteados y 2 unidades descontadas de stock**. El daño no es en plata —los importes cuadran— es que la venta queda **mintiendo sobre como se cobro**, y la mentira aparece semanas despues en el estado de cuenta de un cliente, porque es esa condicion la que decide si facturarla le genera un cargo de IVA.

**UI (flujo 11):** control de dos opciones en la **cabecera** junto al cliente, no al pie con los botones — el IVA cambia el precio que el vendedor canta al mostrador, y un control al pie lo obliga a recalcular toda la pantalla despues de haber dicho un numero en voz alta. Dos radios y no un checkbox: "no facturar" obliga a leer una negacion para entender el caso normal. La columna IVA muestra una **raya apagada** (`ov-vacio`, clase nueva en el tema) y no un `0,00`: un cero se lee como "pago cero de IVA" cuando lo que pasa es que **no hay IVA**, y en un comprobante fiscal la diferencia importa. El bloque de totales muestra la segunda cifra ("con factura seria $X", `ov-celda-secundaria`), que es la respuesta a la pregunta del mostrador sin girar el control de ida y vuelta. Aviso tenue de "este cliente tiene CUIT" al vender sin factura: **avisa sin bloquear**, mismo criterio que R10 para el stock sin verificar.

**Detalle que se cerro y es facil de omitir:** el override del "Subtotal c/IVA" del administrador despeja el precio hacia atras dividiendo por `(1 + IVA/100)`. Con la venta sin factura hay que despejar con el **IVA efectivo** (0), o tipear un subtotal le bajaria el precio un 21% sin que haya pedido nada.

### CR-02 — Facturacion parcial: comprobantes 1:N y el IVA que no se cobro

`ComprobanteAfip` + `ComprobanteAfipItem` 1:N sobre `Venta`, portados de `marihogar` (en produccion con CAE real), mas `EstadoComprobanteAfip` y `IFacturacionParcialService`/`FacturacionParcialService`.

**Por que fue ahora y no en la Entrega 5:** AFIP esta codificado pero deshabilitado (falta el certificado del cliente), asi que `Venta.CAE`/`NumeroComprobante`/`VencimientoCAE` estan **todos en null** y la migracion es aditiva y sin backfill. Despues del primer CAE real seria una reconstruccion de datos sobre documentos fiscales. Era la unica ventana irreversible del lote.

**Las tres adaptaciones de `marihogar` que no se pueden omitir:**

1. **`ComprobanteAfipItem.Cantidad` es `decimal(18,3)` y NO `int`.** Su modelo asume cantidades enteras; aca se venden 2,5 metros de cable. Con `int`, facturar 2,5 de 2,5 dejaria **0,5 pendiente para siempre** y el tope del pendiente nunca cerraria. Verificado ejecutando (2.10): 2,5 facturados como 2,500.
2. **`PrecioUnitario` es el precio EFECTIVO (`ItemVenta.Subtotal / Cantidad`), no el de lista** — y este es el error mas facil de cometer, porque el campo se llama igual en los dos lados. En este proyecto descuento y recargo son **porcentajes que NO estan aplicados en `PrecioUnitario`** sino en `Subtotal` (formula `Cantidad x PrecioUnitario x (1 - d/100 + r/100)`). Copiar el de lista emitiria un comprobante **fiscal** por mas plata de la que se vendio en toda linea con descuento, y por menos en toda linea con recargo. En `marihogar` el error no existe porque alla la cascada va sobre el precio.
3. **Se agrega `PorcentajeIVA` a la linea del comprobante.** `marihogar` tiene el 21% hardcodeado; este catalogo tiene productos al 21 y al 10,5, y la alicuota con la que se calculo el cargo al cliente tiene que quedar congelada con el documento.

**`ItemVenta.CantidadFacturada` NO se agrega**, aunque `marihogar` la reservo desde su Sprint 2. Un contador denormalizado hay que mantenerlo sincronizado en cada emision y en cada baja de comprobante, y si se desincroniza el tope "no facturar mas que el pendiente" **deja de valer sin que nada falle**. El pendiente se calcula sumando las lineas vivas; una venta tiene pocos comprobantes y pocos items.

**Los dos filtros de soft delete del calculo del pendiente no son redundantes:** el query filter global esconde el `ComprobanteAfipItem` borrado, pero **no** esconde los items de un `ComprobanteAfip` dado de baja entero (la baja del padre no toca las filas hijas). Sin el filtro sobre el padre, dar de baja un comprobante dejaria su cantidad contada como facturada para siempre y el tope bloquearia una refacturacion legitima sin que nada explique por que.

**`Venta.CAE`/`NumeroComprobante`/`VencimientoCAE` se quedan**, marcadas obsoletas en su XML-doc apuntando a `ComprobanteAfip`. Borrar columnas y crear el reemplazo en un solo paso deja sin camino de vuelta. Nadie debe escribirlas.

**"Facturada en parte" es un estado DERIVADO**, no un valor nuevo de `EstadoVenta`: se calcula de los comprobantes vivos y sus cantidades. Asi no hay que renumerar enteros ya persistidos ni mantener un estado sincronizado con las cantidades en cada emision — y es el tercer uso del estado derivado en el proyecto (Presupuesto, y la "factura anulada" de `marihogar` que se infiere de la nota de credito). En el listado se calcula **en la misma consulta que la pagina** (DataTables server-side), no con un N+1. En la grilla solo ese valor lleva color: Confirmada y Facturada son finales, "Facturada en parte" es la que tiene algo pendiente que hacer (instruccion 38).

**El cargo de IVA (D-CR01.1), que es la pieza que no se podia omitir.** `OrigenMovimientoCC.DiferenciaIvaFacturacion = 5`, al final del enum, **propagado a los dos lados del ledger (`LP-002`)**: el combo de origen y el mapa `etiquetasOrigen` de `Views/Clientes/CuentaCorriente.cshtml` — son dos lugares, no uno. Al facturar una venta cobrada sin IVA se postea **un** Debito en la CC del cliente por el IVA **exacto** de los items facturados, **en la misma transaccion** que el comprobante (si fueran dos, un fallo en el medio deja un comprobante fiscal con IVA que nadie cobro, o un cargo sin comprobante que lo explique). **La venta no se recalcula nunca**: ni su total, ni sus subtotales, ni los pagos ya posteados. Queda cobrada por un importe y facturada por otro mayor, **y los dos son correctos**. La `Referencia` **nombra el comprobante** (`"IVA de la factura #3 sobre la venta #2 (cobrada sin IVA)"`) y no dice "ajuste": es plata que el cliente no pidio y que va a ver en su estado de cuenta, asi que si no puede rastrearla hasta la factura que la genero, la lee como un cargo sin motivo.

`ComprobanteAfip.DiferenciaIvaCobrada` **no es redundante con `Iva`** aunque hoy coincidan cuando se postea: `Iva` es un dato fiscal del comprobante, el otro es el registro de que **se genero un cargo al cliente**. Son dos hechos distintos y hay que poder contestar "¿este comprobante le genero deuda?" sin cruzar la condicion de la venta, que vive en otra tabla.

**La validacion de UI "no se puede emitir sin haber visto el importe del cargo" se cierra server-side**, porque desde la vista no se puede garantizar: el importe que el usuario confirmo viaja en el POST, el Service lo recalcula y **rechaza** si no coincide. El JS usa el mismo redondeo comercial por linea que el Service, para que un centavo de diferencia no produzca un rechazo incomprensible.

**Concurrencia (`PAT-059`):** `FacturacionParcialService.EmitirAsync` abre la transaccion **antes de leer**, toma el lock de la fila de la venta como **primera sentencia**, y recien despues lee el ya-facturado (`LP-035`: una lectura comun adelantada congela el read view de REPEATABLE READ y toda relectura posterior lee el pasado). Relectura **real** por `RelecturaBajoLock`, no `ReloadAsync` (`ComprobanteAfip` y `Venta` heredan `SoftDestroyable`). No se bloquean productos (no se lee ni escribe stock) ni `Clientes` (no se decide sobre el saldo: se le suma un Debito, que es escritura ciega sobre un ledger aditivo). Medido: N=3 y N=8 emisiones simultaneas de la misma venta dan **1 ganador, 1 comprobante, y nunca mas cantidad que la vendida**.

**Queda declarado por escrito por que las cantidades vendidas SI se pueden tomar del grafo pre-lock aca** y en `ConfirmarAsync` no: la diferencia es la inmutabilidad. `GuardarBorradorAsync` es el unico que escribe `ItemVenta` y exige `Borrador`; las guardas ya rechazaron Borrador, asi que los items no pueden cambiar. Lo que **si** cambia en la ventana es el ya-facturado, y eso se relee bajo lock.

**Nota de alcance heredada y todavia abierta:** `AnulacionVentaViewModel` e `IAnulacionVentaService` (modulo 16, Entrega 5) asumen **un** comprobante por venta. Con comprobantes 1:N la nota de credito se emite **contra un comprobante**, no contra la venta. Esas dos definiciones quedan superadas y hay que ajustarlas **antes** de construir el modulo 16. `ComprobanteAsociadoId`/`Motivo` de `marihogar` (su CR-55) quedaron deliberadamente fuera de este alcance.

**Lo que NO hace y nadie debe buscar:** no toca stock, no toca caja, no recalcula la venta y **no llama a AFIP**. El comprobante nace y queda en `EstadoComprobanteAfip.Pendiente`, que es el estado **normal** mientras falte el certificado, no una anomalia. Pedir el CAE es el paso que queda para la Entrega 5.

### LP-039 — Anular una venta con comprobantes vivos: la guarda pasa a decidir por el documento, no por el estado

**Aplicado, pendiente de re-verificacion por QA.** Parte `LP-039` (`major`, bloqueante) de la ronda del 2026-10-06, sobre el HEAD que acababa de introducir CR-02. Un commit, sin migracion EF, sin push y sin deploy.

**El defecto es una consecuencia directa de CR-02 y no se ve leyendo `AnularAsync` sola.** La guarda decidia con `fresca.Estado == EstadoVenta.Facturada`, que era equivalente a "esta venta tiene comprobante" mientras hubo **un** comprobante por venta. Con 1:N dejo de serlo: una venta facturada **en parte** sigue en `Confirmada` — lo afirma el propio arnes de CR-02 ("2.3 la venta NO pasa a Facturada") — asi que en el caso parcial la guarda **no se alcanzaba nunca**. QA lo midio: la venta #9029, con su comprobante #2 **vivo** por $ 2.904 (IVA $ 504), paso a `Anulada`, la caja posteo la reversion de $ 9.455 **completa** y el comprobante quedo con `DeletedAt IS NULL` y sin nota de credito. Y se llegaba **con un click**, porque `puedeAnular` en la vista tampoco miraba comprobantes y la pantalla ofrecia el boton.

**El criterio correcto es "¿hay algun comprobante VIVO?", y el cambio de criterio es el fix entero.** Lo que impide revertir no es el estado de la venta sino la existencia del documento fiscal: es al documento al que hay que darle de baja con una nota de credito. El estado de la venta es un derivado de eso, y los derivados se desincronizan.

**Por eso la guarda tampoco mira `EstadoComprobanteAfip`,** y es la decision que mas facil seria revertir por error: un comprobante en `Pendiente` o en `Error` **tambien** bloquea. Hoy, con AFIP deshabilitado, **todos** estan en `Pendiente` y sin numero — exigir `Emitido` haria que la guarda volviera a no alcanzarse nunca, que es el mismo defecto con otra cara. El camino para desbloquear es dar de baja el comprobante, no anular la venta por encima suyo.

**Las dos puntas, nunca una sola.** `puedeAnular` en `Views/Ventas/Details.cshtml` usa `Model.Comprobantes.Count == 0`, que es exactamente lo que evalua el Service: ese `List` lo llena el detalle con una consulta directa sobre `ComprobantesAfip`, asi que el query filter global de soft delete ya lo restringio a los vivos. Sigue sin ser la autorizacion (la que vale es la del Service, con el flag de rol del Controller), pero una UI que ofrece un boton que el servidor rechaza es la mitad de un defecto.

**El mensaje de rechazo lee el numero del COMPROBANTE.** El viejo lo leia de `Venta.NumeroComprobante`, que CR-02 dejo obsoleta y esta siempre en null: imprimia `"(número )"` vacio — es el control positivo de QA, que "funcionaba" con un mensaje roto. Y como AFIP esta deshabilitado el numero **puede no existir**, asi que hay dos formas: `0001-00000005 por $ X` cuando hay numero, e `interno #6 (sin número de AFIP asignado, Pendiente) por $ X` cuando no. Nunca un parentesis vacio. El id interno es lo que el usuario necesita para encontrar el comprobante en la grilla de la venta.

**Orden de locks (familia LP-035):** la consulta de comprobantes es una **lectura comun** y esta despues de **todos** los locks (periodo, venta, productos). No necesita ser de bloqueo: `FacturacionParcialService.EmitirAsync` bloquea la **misma** fila de venta antes de insertar su comprobante, asi que una emision concurrente o ya commiteo antes de que tomaramos el lock —y entonces la vemos, porque el read view se abre con la primera lectura comun, que es posterior al lock— o esta esperando nuestro commit. La consulta va **directa** sobre `ComprobantesAfip` y sin `Include(c => c.Venta)`: ese `Include` haria un INNER JOIN contra el query filter de `Venta` y descartaria filas (el detalle de EF de `LP-034`).

**Lo que quedo como catch-all:** `fresca.Estado != EstadoVenta.Confirmada`. Una venta `Facturada` llega ahi solo si **todos** sus comprobantes fueron dados de baja, y se la sigue rechazando — fallar cerrado es lo correcto mientras la nota de credito no exista.

**Alcance: esto solo CIERRA LA PUERTA.** El camino para anular una venta facturada es la nota de credito, que es el **modulo 16 (Entrega 5)**. No se construyo circuito de NC, ni pantalla de baja de comprobante, ni se emite nada. La nota de alcance de CR-02 sigue vigente y se repitio en el codigo: `AnulacionVentaViewModel` e `IAnulacionVentaService` quedaron superados por 1:N y hay que rediseñarlos **antes** del modulo 16.

**Evidencia, y lo que la hace valer: la verificacion por mutacion.**

- Build: `dotnet build --no-incremental` → **0 errores, 9 advertencias** (la linea base; las 9 son preexistentes: 8 NU1902 de MailKit/MimeKit y el CS0114 de `HomeController`). El arnes compila con 0 errores y **ninguna** advertencia `CS` propia.
- `tools/ArnesVentaSinFacturaYParcial` extendido con el **escenario 7** (9 afirmaciones nuevas): **59 OK / 0 FALLADAS**. El caso sembrado es el que **discrimina** — venta facturada **en parte**, con su precondicion afirmada explicitamente (7.1: `Estado == Confirmada`), porque un escenario sembrado sobre una venta `Facturada` pasaria igual con el defecto puesto.
- **Mutacion 1** — devolverle a la guarda el criterio por estado (`comprobantesVivos.Count > 0 && fresca.Estado == Facturada`): **7.2/7.3/7.4/7.5 FALLAN** y reproducen el parte de QA textualmente (`Estado=Anulada`, stock devuelto, caja con la reversion posteada, `reversiones=1`, y el comprobante `DeletedAt=NULL` colgado de una venta `Anulada`). Las de la venta totalmente facturada (7.6/7.7) y las de la venta limpia (7.8/7.9) siguen OK: la mutacion toca solo lo que tiene que tocar.
- **Mutacion 2** — que el mensaje vuelva a leer `Venta.NumeroComprobante`: **7.5 y 7.7 FALLAN**, con el `"(número )"` vacio impreso en la evidencia.
- **Una afirmacion vacia encontrada y corregida en el camino, que es la leccion de la ronda anterior repitiendose.** La 7.4 decia "el comprobante sigue vivo" y **pasaba en los dos mundos**: con el defecto puesto el comprobante tambien queda vivo — eso es justamente lo malo. No medía nada. El invariante que QA midio roto es el **par**, asi que la afirmacion es ahora la conjuncion: comprobante vivo **y** venta que no esta `Anulada`. Recien con eso falla bajo mutacion.
- **No-regresion de la familia de atomicidad:** `tools/ArnesReconciliacionTx`, que es el que ejercita `AnularAsync` concurrente (`LP-018`), da **153 OK / 0 FALLADAS**.
- Bases desechables (`laplatense_lp039`, `laplatense_lp039b`), **nunca** `laplatense_dev` ni los fixtures de QA ni produccion. Borradas al terminar.

**Pruebas minimas para QA (navegador, que este rol no ejecuta):** (1) venta confirmada, facturarle **un** item, volver al detalle → el boton "Anular venta" **no** tiene que aparecer, y la venta sigue mostrandose `Confirmada`; (2) postear el `POST Ventas/Anular` a mano sobre esa misma venta → rechazo, con el mensaje nombrando el comprobante y **sin** parentesis vacio; (3) misma cosa sobre una venta totalmente `Facturada`; (4) venta confirmada **sin** comprobantes → se anula, con stock devuelto y reversion en caja, igual que antes.

**`LP-037` sigue ABIERTO y MEDIDO a proposito** (el cierre de caja puede firmar totales en cero con escritores concurrentes). `tools/ArnesSeisSitiosRestantes` sigue dando **20 OK / 2 FALLADAS** y esas 2 son LP-037. No se toco, no se silencio, y **no** es una regresion de esta ronda: espera decision. *(Cierto cuando se escribio esto. **`LP-037` se cerro el 2026-10-07** con fila centinela por periodo: ver su entrada en Definiciones vigentes. El arnes pasa a 32 OK / 0.)*

### LP-040 — El camino legado de facturacion deja de ser un camino: `FacturarAsync` pasa a ser un atajo del circuito 1:N

**Aplicado, pendiente de re-verificacion por QA.** Parte `LP-040` (`major`) de la ronda del 2026-10-06, sobre el commit `f05cc92` (el cierre de `LP-039`). Un commit, **sin migracion EF**, sin push y sin deploy.

**Es el mismo defecto de clase que `LP-039`, en el otro extremo del circuito.** `FacturarAsync` decidia con `fresca.Estado == EstadoVenta.Facturada`, y una venta facturada **en parte** sigue en `Confirmada`: la guarda no se alcanzaba nunca. QA lo midio textualmente: `POST /Ventas/Facturar/97` sobre la venta facturada en parte **atraviesa las cuatro guardas de negocio** y muere recien en la integracion — "AFIP no esta configurado: falta el certificado (.p12)". El gate del boton tampoco miraba comprobantes. **Lo unico que impedia facturar dos veces los mismos items era que AFIP estaba apagado**, asi que el riesgo vencia exactamente cuando se enciende lo que el fix anterior desbloquea: un CAE por el total encima de un comprobante parcial vivo de esos mismos items, escrito en las columnas obsoletas y sin fila en `ComprobantesAfip`.

**Por eso el fix NO es poner la guarda de `LP-039` acá.** Eso tapaba el caso y dejaba la causa viva: dos caminos poblando **dos modelos distintos del mismo hecho** (`ComprobanteAfip` por un lado, `Venta.CAE`/`NumeroComprobante`/`VencimientoCAE` por el otro). De ahi salieron `LP-039` y `LP-040` seguidos, y un parche de guarda garantizaba un tercero. `FacturarAsync` pasa a ser lo que la pantalla ya ofrecia como caso habitual — **"facturar todo lo pendiente"** — expresado sobre el unico modelo que existe: resuelve el pendiente por item con `ObtenerFacturableAsync` y delega en `FacturacionParcialService.EmitirAsync`, que emite **un** `ComprobanteAfip` con sus items.

**Lo que el metodo deja de hacer, y cada cosa es deliberada:**

- **No escribe las tres columnas obsoletas** (ni `Venta.TipoComprobanteAfip`: el tipo es del comprobante). Siguen existiendo sin uso — borrarlas en la misma migracion que creo el reemplazo dejaba sin camino de vuelta. Lo que termina acá es que alguien las **escriba**.
- **No llama a AFIP**, y por lo tanto **no sostiene un lock de fila durante el round-trip del webservice** (el costo que el comentario de `LP-018` asumia explicitamente en este metodo). El comprobante nace en `Pendiente`, igual que por el camino parcial. Cuando el certificado llegue, la llamada a AFIP se escribe **una** vez sobre `ComprobanteAfip` y los dos caminos la heredan: eso es lo que este cambio compra. La resolucion de `DocTipo`/`DocNro` del receptor que vivia acá queda en git (`f05cc92`) para ese momento.
- **No decide por estado.** El tope por item y las guardas de estado las aplica `EmitirAsync` **bajo lock** de la fila de venta. La concurrencia no se cerro con una guarda nueva: se cerro **delegando en el unico lugar que la tiene medida**. Dos POST simultaneos leen el mismo pendiente afuera de la transaccion, pero el segundo espera el lock y al entrar relee el ya-facturado y lo rechaza.
- **Se fue la dependencia de AFIP del Service** (`IAfipService` + `AfipSettings`) y los dos helpers que solo usaba este camino. No es limpieza cosmetica: dejarla inyectada diria que este servicio emite comprobantes, y la confusion entre "quien factura" y "quien mueve stock y caja" es de donde salio esta familia.

**El caso que el brief no cubria y hubo que decidir: el cargo de IVA.** Si la venta se cobro **sin factura**, el comprobante lleva un IVA que el cliente no pago y ese importe se le carga en su cuenta corriente, y `D-CR01.1` exige que el usuario **vea el importe antes de confirmar**. El atajo es **un click**: no tiene pantalla donde mostrarlo. Entonces **no emite** — rechaza con un mensaje que manda a "Facturar ítems", que es la pantalla que lo muestra y lo hace confirmar. La condicion es **cualitativa** ("¿corresponde un cargo?": `!VentaFacturada && alguna linea con alicuota > 0`), nunca un importe: duplicar la aritmetica del IVA acá seria inventar un segundo criterio para el mismo numero. Por eso se delega con `DiferenciaIvaConfirmada = 0` — si pese a esa guarda el Service calculara un cargo, la emision **se rechaza sola**. Defensa en profundidad, y esta medida (mutante M5).

**Las dos puntas, nunca una sola.** `VentaDetalleDto` expone `PendienteDeFacturar` (derivado: lo vendido menos lo que cubren los comprobantes vivos, calculado una vez en el mapper) y la vista decide con **ese** numero, no con el estado. El gate viejo (`Estado == Confirmada || FacturadaEnParte`) es equivalente **hoy** solo porque la emision pone `Facturada` cuando el pendiente llega a cero: un gate que depende de una condicion que vive en otro metodo es la forma exacta de esta familia. El boton legado, ademas: se renombro a **"Facturar todo lo pendiente"** (decia "Emitir factura AFIP por el total", que ya no es lo que hace), **dejo de depender de `afipConfigurado`** —no llama a AFIP, y pedirlo seria esconder una accion que el servidor acepta, el espejo del defecto— y no se ofrece sobre una venta cobrada sin factura.

**Un defecto de pantalla que aparecio al abrirlo y se cerro en la misma pasada:** la tarjeta "Comprobante AFIP" del detalle se dibujaba con `Estado == Facturada` y leia las columnas obsoletas. Toda venta facturada por el circuito de CR-02 ya la mostraba con los **cuatro campos vacios** — el mismo `"(número )"` que QA levanto como control positivo en `LP-039`, una pantalla mas abajo. Ahora se condiciona a que **haya dato** (`CAE` o numero), asi una venta historica lo sigue mostrando y las nuevas no dibujan una tarjeta vacia.

**`Confirmar y facturar` del POS (`Editar.cshtml`) NO se toco, y es una decision.** Ese boton sigue gateado por `afipConfigurado`, asi que hoy no se muestra. Un borrador no tiene comprobantes: no puede duplicar nada, y el gate es **mas estricto** que el Service, que es seguro. Habilitarlo haria que **cada venta del POS emitiera un comprobante automaticamente**, que es una decision de producto y no un fix de defecto. Queda para que Joaquin lo confirme. El camino en si quedo cubierto por el arnes (8.22/8.23).

**Evidencia, y lo que la hace valer: la verificacion por mutacion.**

- Build: `dotnet build FerreteriaLaPlatense.slnx` → **0 errores, 9 advertencias**, la linea base exacta (8 NU1902 de MailKit/MimeKit + el CS0114 de `HomeController`). El arnes compila sin **ninguna** advertencia `CS` propia.
- `tools/ArnesVentaSinFacturaYParcial` extendido con el **escenario 8** (23 afirmaciones nuevas): **82 OK / 0 FALLADAS** (59 previas + 23).
- **La trampa de este escenario, y por que las afirmaciones estan escritas al revés:** con AFIP apagado, el codigo **con** el defecto tambien devuelve un error (el de la integracion), asi que una afirmacion "el atajo es rechazado sobre una venta facturada en parte" **pasa en los dos mundos** — la misma forma de falso verde que la 7.4 de la ronda anterior. Lo que discrimina es que en el mundo arreglado el atajo **hace lo correcto**: emite por el **pendiente** (no por el total), completa la venta y no escribe las columnas obsoletas.
- **Mapa de mutacion (5 mutantes corridos, cada uno con su build y su corrida):**
  - **M1** — el metodo viejo entero (criterio por estado + emision contra AFIP): **mata 18 de las 23**.
  - **M2** — la delegacion pide `i.Cantidad` en vez de `i.ACobrar`, o sea facturar el **total** encima del comprobante parcial (el defecto con AFIP encendido): **mata 8** (8.2, 8.4, 8.5, 8.6, 8.7, 8.9, 8.10, 8.11).
  - **M3** — el atajo vuelve a escribir las columnas obsoletas: **mata 3** (8.8, 8.15, 8.23).
  - **M4** — sin la guarda de "no queda nada pendiente": **mata 1** (8.10), con el mensaje degradado a "hay que indicar al menos un ítem".
  - **M5** — el atajo postea el cargo de IVA **sin que nadie lo haya visto** (saca la guarda de `D-CR01.1` y confirma el importe que el mismo calcula): **mata 8.17 y 8.18**.
- **Las que sobreviven a los cinco, declaradas en vez de contadas como cobertura:** 8.1 es la **precondicion** (afirma que la venta sembrada esta en `Confirmada` con pendiente; si fallara, el escenario no mediria el caso que importa), y 8.16 / 8.18 / 8.21 son controles de **daño colateral** (que una venta cobrada con IVA no genere cargo, que un rechazo no deje nada posteado, que ningun rechazo sea una excepcion cruda). Son defensa en profundidad, no miden la guarda nueva — es lo mismo que QA reporto de la 7.6 y conviene no confiar en ellas.
- **Una falla propia del arnes, encontrada corriendo los mutantes:** la afirmacion 8.9 indexaba `comprobantes[1]` sin verificar el `Count`, asi que un mutante que no emitia nada hacia **morir el arnes por indice fuera de rango** en lugar de reportar la afirmacion como FALLADA — y las 14 afirmaciones de mas abajo quedaban **sin medir** (M1 "mataba" 6 y el resto no se ejecutaba). Corregido: con el guard, M1 mata 18. Un arnes que se cae deja de ser una medicion.
- **No-regresion:** las 59 afirmaciones previas (CR-01, CR-02, el cargo de IVA, la concurrencia del tope con N=3 y N=8, `LP-038`, y el escenario 7 de `LP-039` completo) siguen **todas** en OK.
- Base desechable `laplatense_lp040`, **nunca** `laplatense_dev`, ni los fixtures `laplatense_qa_*`, ni produccion. Borrada al terminar (verificado con `SHOW DATABASES`).

**Pruebas minimas para QA (navegador, que este rol no ejecuta):** (1) venta confirmada, facturarle **un** item por "Facturar ítems", volver al detalle → tiene que aparecer "Facturar todo lo pendiente" (**aunque AFIP siga apagado**) y la tarjeta "Comprobante AFIP" **no** tiene que dibujarse vacia; (2) tocarlo → emite **un** comprobante nuevo por el resto, la venta pasa a `Facturada`, y en la base `Venta.CAE`/`NumeroComprobante`/`VencimientoCAE` siguen en `NULL`; (3) volver a postear `POST /Ventas/Facturar/<id>` a mano sobre esa venta → rechazo con "ya está facturada por completo", **nunca** un error de AFIP; (4) sobre una venta cobrada **sin factura** → el boton no aparece, y el POST a mano rechaza mandando a "Facturar ítems", sin postear cargo de IVA; (5) venta confirmada sin comprobantes → el atajo la factura entera y el comprobante vale lo mismo que la venta; (6) no-regresion de `LP-039`: la anulacion sigue rechazada sobre cualquier venta con comprobante vivo.

**`LP-037` sigue ABIERTO y MEDIDO a proposito.** No se toco, no se silencio, y no es una regresion de esta ronda. *(Cierto cuando se escribio esto. **`LP-037` se cerro el 2026-10-07** con fila centinela por periodo: ver su entrada en Definiciones vigentes. El arnes pasa a 32 OK / 0.)*

**Alcance que sigue abierto, repetido porque se cruza con esto:** no se construyo nota de credito ni baja de comprobante (modulo 16, Entrega 5), y `AnulacionVentaViewModel` / `IAnulacionVentaService` siguen superados por el modelo 1:N — hay que rediseñarlos **antes** del modulo 16.

### `LP-041` — El arnes que mentia: un aborto que parecia una corrida limpia, y una linea base que no se reproducia

**Va primero a proposito.** Es la herramienta con la que se mide `LP-037`: arreglar el metro antes de
medir con el.

**Lo que estaba roto, y son cuatro cosas distintas:**

1. **La limpieza mataba al arnes.** `ComprobanteAfipItem.ItemVentaId` -> `ItemsVenta` es `RESTRICT` a
   proposito, y `LimpiarAsync` borraba `ItemsVenta` sin borrar antes los comprobantes. Hasta `LP-040`
   no se notaba porque el atajo de facturacion escribia las columnas obsoletas de `Venta` y **no
   creaba filas** en `ComprobantesAfip`; desde `LP-040` si las crea. **Medido: la segunda corrida
   sobre la misma base daba 0 OK / 0 FALLADAS y exit 127.** Orden nuevo: items del comprobante ->
   comprobante -> items de la venta. Mismo arreglo, preventivo, en `ArnesSeisSitiosRestantes`, que
   tenia el mismo patron y hoy no rompe **por casualidad** (ninguno de sus escenarios factura).
2. **Un aborto se podia leer como exito.** Sin resumen, sin mensaje y con un exit code que nadie
   mira. El cuerpo de los dos arneses va dentro de un `try` (**sin reindentar**, para que el diff
   siguiera siendo legible), el resumen imprime primero **cuantas afirmaciones se EVALUARON**, y los
   exit codes se separan: `0` midio y todo OK, `1` midio con fallas, `2` guarda de cadena de
   conexion, `3` abortado por excepcion, `4` termino sin evaluar nada. Verificado contra una base sin
   migraciones: exit **3** con "EL ARNES NO SE MIDIO".
3. **Dos afirmaciones median un comportamiento retirado a proposito.** `5.2` ("AFIP invocado una
   vez") y `5.4` ("un CAE persistido") median el camino legado que `LP-040` saco del medio: el atajo
   delega y no escribe el CAE. Reescritas a la version vigente (**cero** invocaciones a AFIP; **un**
   comprobante 1:N **y** las columnas obsoletas de `Venta` vacias), con lo que median y por que
   dejaron de aplicar escrito al lado. `5.4` **discrimina** (contraprueba: con la escritura legada del
   CAE reinsertada falla en los dos N). `5.2` queda declarada **tripwire de regresion y no
   evidencia**: `IAfipService` ya no esta inyectado en el camino, asi que no puede fallar hoy — y una
   afirmacion que no puede fallar no prueba nada.
4. **Las 6 fallas del grupo 16 eran del RELOJ, no del codigo.** La siembra pasaba
   `Fecha = DateTime.UtcNow` y `RegistrarMovimientoAsync` rechaza fecha futura contra
   `ArgentinaTime.Hoy` (LP-009: el huso del hosting no es el del negocio): **entre las 21:00 y la
   medianoche ART, `UtcNow.Date` ya es el dia siguiente**. `16.0` fallaba, `movId` quedaba en 0,
   `16.1` y `16.2` fallaban en cascada y **`16.3` PASABA VACIA** (el neto vivo de un id inexistente es
   0, que es justo lo que esperaba). Tres por N, dos N = las seis. Reproducido a las **22:28 ART del
   2026-10-06**; a las 10:00 no aparecen. Va `ArgentinaTime.Hoy`, y si la siembra no entra el
   escenario se declara **SIN MEDIR** en vez de dejar correr afirmaciones sobre un id que no existe.

**LINEA BASE REAL DE LOS DOS ARNESES — este numero reemplaza al "153 OK / 0" que se venia citando.**
Medida el **2026-10-07** (madrugada ART) contra clones desechables `laplatense_lp041` y
`laplatense_lp037`:

| Arnes | Resultado | Exit | Idempotente |
|---|---|---|---|
| `tools/ArnesReconciliacionTx` | **153 afirmaciones EVALUADAS: 153 OK, 0 FALLADAS** | 0 | si (1a y 2a corrida identicas) |
| `tools/ArnesSeisSitiosRestantes` | **32 afirmaciones EVALUADAS: 32 OK, 0 FALLADAS** (post-`LP-037`) | 0 | si |

El "153 OK / 0" que se citaba como no-regresion **era el numero correcto pero no se reproducia en
ningun commit**: hacia falta que el reloj acompañara y que la limpieza no muriera. Un numero que
depende de la hora a la que se corre no es una linea base. El `20 OK / 2 FALLADAS` del segundo arnes
si se reproducia, y se verifico antes de tocar nada (control positivo propio).

**Archivos:** `tools/ArnesReconciliacionTx/Program.cs`, `tools/ArnesSeisSitiosRestantes/Program.cs`.
Sin migracion EF, sin cambios en el sistema. Commit local `41ec1b2`, **sin push y sin deploy**.

### `LP-037` — CERRADO: fila centinela por periodo de caja (los gap locks conviven, la espera llegaba tarde)

**El defecto:** `CerrarDiaAsync` contra 2 y contra 7 escritores concurrentes dejaba el dia **cerrado
con `TotalIngresos = 0`** mientras la suma de los movimientos vivos de ese mismo dia era **$ 201** y
**$ 721**. El arqueo firmado miente y sus numeros son internamente coherentes. `CerrarMesAsync` tenia
el mismo agujero por la misma razon y **no estaba medido**.

**Por que la reserva anterior no alcanzaba:** era un `SELECT ... FOR UPDATE` sobre la clave del
cierre, que **no existe** todavia -> **gap lock**, y los gap locks **conviven entre si** (solo
inhiben `INSERT`). El cerrador tomaba su gap, **leia los totales**, los escritores commiteaban
despues, y el `INSERT` del cierre —que si espera los gaps— grababa los totales que ya habia leido.
**Habia que serializar la LECTURA, no el `INSERT`.**

**La solucion (decision de Joaquin, 2026-10-06):** entidad nueva `CandadoPeriodoCaja` / tabla
`CandadosPeriodoCaja`, **una fila por periodo**, indice unico `(Anio, Mes, Dia)`, bloqueada con
`FOR UPDATE` sobre una fila **que existe** -> record lock, exclusion mutua real, **sin ciclo y sin
logica de reintento**. `Dia = 0` es el candado del **mes** (0 y no `NULL`: un indice unico de MySQL
**no deduplica los NULL**, y con `NULL` dos cerradores mensuales podrian crear dos filas del mismo
mes). Se descarto la lectura de bloqueo por rango sobre `CajaMovimientos`: no costaba migracion pero
convertia el descuadre en un **deadlock** contra el escritor que ya tenia el gap.

**Orden canonico (escrito en el XML-doc de `BloqueoDeFila`):** el candado es el **paso 0**, antes de
todos los locks de fila, y va **mes y despues dia** en los dos lados de la carrera. Un cierre mensual
toma solo el del mes; un escritor o un cierre diario toman el del mes y despues el del dia — un
**prefijo del mismo orden** nunca cierra un ciclo. Los gap locks de las dos tablas de cierre **se
quedan**: hacen que el cierre duplicado siga cayendo como mensaje de negocio en vez de
`DbUpdateException` cruda.

**Como se crea la fila, que es la parte delicada:** `INSERT IGNORE` en una **conexion aparte**,
**fuera** de la transaccion, y **antes** de tomar ningun lock sobre esa tabla. Hacerlo adentro
**fabrica el deadlock que la centinela existe para evitar** (dos gaps que conviven + dos
insert-intention, o dos `S` que escalan a `X`). Y **antes del `INSERT` va una lectura comun**: un
`INSERT IGNORE` contra una fila existente que otro tiene tomada con `FOR UPDATE` pide un **lock
compartido y se queda esperando**. **Eso aparecio por accidente en la contraprueba** —con los
`FOR UPDATE` del candado sacados, el escenario mensual **seguia pasando** porque el que serializaba
era el `INSERT IGNORE`— y era un riesgo real: la guarda de periodo se llama **despues** de los locks
de documento, asi que esa espera podia ocurrir con locks en la mano, entre dos conexiones del mismo
request, que InnoDB **no detecta** como deadlock.

**El XML-doc que mentia:** `BloquearPeriodoCajaAsync` afirmaba que la reserva cerraba las **dos**
mitades del descuadre (categoria `LP-008`). Ya se habia corregido en la ronda que encontro el
defecto; ahora se reescribio entero con el mecanismo nuevo, y declara que la garantia **ya no depende
del isolation level** (el record lock sigue siendo exclusivo en READ COMMITTED; lo unico que se
perderia ahi es el mensaje lindo del cierre duplicado).

**Migracion EF:** **una**, `20261007014129_EntregaCinco_CandadoPeriodoCaja`, **aditiva pura** (tabla
nueva + indice unico). **Ninguna columna existente cambia. SIN backfill y no hace falta:** la fila
aparece la primera vez que alguien toca el periodo, y un periodo ya cerrado no recibe escrituras
nuevas. El primer cierre de un periodo no puede fallar por falta de fila porque se crea en la misma
llamada, antes del lock. Verificado: tras dos corridas del arnes la tabla tiene **exactamente 4
filas** (mes y dia de los dos periodos tocados), sin duplicados.

**Medicion — `tools/ArnesSeisSitiosRestantes` pasa de `20 OK / 2 FALLADAS` a `32 OK / 0 FALLADAS`:**

- `3.2/N=3` y `3.2/N=8`, las dos que estaban abiertas, **pasan a OK**. Es el criterio de cierre del
  brief.
- **Escenario `3c` NUEVO, determinista, y existe porque el viejo no alcanzaba.** El escenario 3 usa
  una barrera y **con el fix gana el CERRADOR las dos veces**: los escritores salen rechazados y el
  invariante queda en `0 == 0` — correcto, pero **cumplido vacio** (misma familia que la 7.4 de
  `LP-039`). El `3c` fabrica la ventana a mano: una conexion aparte toma el candado, inserta un
  movimiento del dia y **no commitea**; recien ahi se larga el cierre. Ahi el escritor **gana
  siempre**: cierre = **$ 500** = suma viva. Con **dos precondiciones afirmadas explicitamente** (el
  movimiento quedo vivo; el dia quedo cerrado), porque sin ellas volveria a poder pasar vacio.
- **Escenario `3d` NUEVO:** lo mismo para el **cierre mensual**, que comparte el mecanismo y no
  estaba medido (cierre = **$ 333** = suma viva del mes), mas la **no-regresion de sus guardas de
  rango** (el mes en curso y un mes futuro siguen rechazados con mensaje de negocio).
- **Contraprueba (mutacion):** con los tres `FOR UPDATE` del candado comentados **fallan las cuatro**
  (`3.2/N=3`, `3.2/N=8`, `3c.3`, `3d.3`) con cierre `$ 0` contra `$ 201`, `$ 721`, `$ 500` y `$ 333`
  vivos. Las precondiciones de `3c` y `3d` **siguen en OK**, asi que la falla es medicion y no efecto
  colateral.
- **Sin deadlocks:** el escenario 5 (orden de locks con el dia **cerrado**, donde el periodo pasa a
  ser lock exclusivo) sigue en OK y ninguna corrida reporto "Deadlock found".
- **No-regresion:** `tools/ArnesReconciliacionTx` sigue en **153 OK / 0 FALLADAS** con la centinela
  puesta — son 11 sitios que reservan el periodo en cada escritura.

**Archivos:** `FerreteriaLaPlatense.Domain/Entities/CandadoPeriodoCaja.cs` (nuevo),
`FerreteriaLaPlatense.Infrastructure/Data/BloqueoDeFila.cs`,
`FerreteriaLaPlatense.Infrastructure/Data/AppDbContext.cs`, la migracion, y
`tools/ArnesSeisSitiosRestantes/Program.cs` (escenarios `3c` y `3d`). **`CajaMovimientoService` no se
toco:** el fix entero vive en el helper de bloqueo, que es el unico lugar invocable — once copias de
una garantia son once oportunidades de que una se olvide. Commit local `408b814`, **sin push y sin
deploy**.

**Pruebas minimas para QA (navegador, que este rol no ejecuta):** (1) cerrar la caja de un dia sin
nadie mas usando el sistema -> cierra igual que antes, con los mismos totales que muestra el resumen;
(2) volver a cerrar el mismo dia -> rechazo con **mensaje de negocio** ("ya fue cerrada"), nunca un
error crudo de base; (3) con el dia cerrado, intentar una venta / un gasto / un cobro de CC con esa
fecha -> sigue rechazado con el mensaje de LP-009; (4) cerrar el **mes anterior** -> permitido; el
mes **en curso** y un mes **futuro** -> rechazados con su mensaje; (5) despues de cerrar un dia,
`SELECT * FROM CandadosPeriodoCaja` tiene que tener **una** fila del mes (`Dia = 0`) y **una** del dia
— nunca dos del mismo periodo; (6) el descuadre en si no se prueba a mano: necesita concurrencia real
y vive en el arnes.

**Bases desechables:** `laplatense_lp037` y `laplatense_lp041`. **Nunca** `laplatense_dev`, ni los
fixtures `laplatense_qa*`, ni produccion.

### Proximos pasos pendientes

> **AL 2026-10-07, LO QUE DE VERDAD QUEDA ABIERTO (lo de abajo es historico de la Entrega 2 y en
> buena parte esta superado).**
>
> 1. **`laplatense_dev` esta CUATRO MIGRACIONES ATRASADA** respecto de `entrega-1-migracion` (tiene
>    14, la rama tiene 18) y por lo tanto **no tiene `CandadosPeriodoCaja`**. Cualquier prueba contra
>    dev de algo que escriba caja va a fallar por esquema, no por codigo. Decision de Joaquin:
>    aplicarle las migraciones o dejarla declaradamente atrasada.
> 2. **`Marca.Activo`, `Categoria.Activo` y `Modelo.Activo` siguen con la forma de `LP-047`**:
>    `ProductoService` no las valida y viajan por POST hacia `Producto`. **Es una pregunta de
>    negocio, no una omision tecnica:** si un producto nuevo puede nacer con una marca dada de baja.
>    Efecto economico nulo (una marca no entra en ningun calculo), a diferencia de la tarjeta.
> 3. **La desviacion del flujo 14** (el plan de echeqs quedo en pantalla propia y no como bloque
>    dentro del formulario de pago) **queda para que el Disenador la acepte o la rechace.**
> 4. **Los seis commits de `CR-04` + `LP-044`..`LP-048` estan "aplicados, pendientes de
>    re-verificacion" de QA.** Sin push y sin deploy.
> 5. La **Entrega 5** (AFIP real, NC/ND, anulacion por comprobante) y el rediseno de
>    `AnulacionVentaViewModel` / `IAnulacionVentaService` siguen superados con la nota puesta.

**Historico de la Entrega 2 (en gran parte superado):**
1. QA funcional (`agentes-ia-qa`) sobre la Entrega 2 completa (ola 1 + ola 2).
2. Aplicar ambas migraciones (`EntregaDos_VentasCCClientesAfip`, `EntregaDos_CajaGastosEntregasDashboard`) contra la base de desarrollo.
3. Conseguir del cliente el CUIT real + certificado `.p12` de La Platense para poder probar AFIP de punta a punta (homologación primero) — sigue bloqueando la prueba end-to-end de Caja (el ingreso automático depende de una venta facturada con éxito).
4. Confirmar con el cliente las asunciones documentadas en ambas olas (Descuento/Recargo como monto, mecánica de recargo de cuotas, cobertura de pagos, markup de Entrega sobre costo base, alcance de "caja cerrada" bloqueando ventas/gastos, acceso de Vendedor a Caja/Gastos, reducción de contenido del Dashboard por rol).
5. Arrancar la Entrega 3 (Compras/Proveedores, CtaCte empleados, CtaCte consolidada del negocio, Presupuestos, Aumento masivo, Devoluciones+NC/ND AFIP, Dashboard Corte final) sobre la rama `entrega-3` — depende de que Entrega 2 esté aprobada por el cliente.
6. Sigue sin confirmar (heredado de Entrega 1): hipótesis de factor de conversión fijo por producto en `UnidadMedidaConversionService` — relevante para Compras (Entrega 3).

## TOKEN DE SUBMIT — pase 2: arreglar el GATE de la fase 2 (2026-10-09)

**Alcance: los 4 defectos de la re-verificacion de QA y nada mas.** La fase 2 NO arranco: los 6
sitios con clave natural cerrada siguen sin tocarse. **Cero migraciones nuevas** (la cola de
produccion sigue en 13). `appsettings.json`, `Seed` y `SeedData.cs` sin tocar. Sin commit. Ningun
defecto marcado como cerrado.

**La forma del resultado de QA, que es la que ordena este pase:** el mecanismo esta bien y la fase 1
es mergeable; **lo que no era confiable era el instrumento del que depende la seguridad de la fase 2.**
Los cuatro arreglos son del instrumento y de una afirmacion falsa, no del mecanismo.

### `LP-127` `major` — el verificador repetia el error que esta ronda vino a corregir

**El defecto, dicho sin suavizarlo: el detector de escritores de plata era una lista a mano de 7
nombres de entidad, dentro del programa que existe para que no haya listas a mano.** Es la forma
exacta del bloque `MISMA FORMA, SIN TOCAR` —que enumeraba 2 sitios de al menos 7 y es la causa raiz de
toda esta ronda— aplicada al instrumento. Y es la peor version del problema, porque **sale en verde**.

QA lo midio por dos caminos que la lista no podia ver: un `new CierreCajaDiario` (entidad **no
listada**) y una escritura **por SQL crudo**. **El perimetro real eran 28 POST y no 23.**

**El arreglo no fue agregar las 5 que faltaban: el criterio pasa a ser una propiedad DEL DATO.** Una
entidad es "de dinero" si **declara una propiedad `decimal`**, y eso se lee de
`Domain/Entities/*.cs` en cada corrida: **27 entidades derivadas, cero nombres escritos a mano**. Una
entidad nueva con un importe entra al perimetro **el dia que se escribe**. Y tres formas de escritura
en vez de una: `new Entidad`, `.Add/.AddRange/.Update/.Remove` sobre el `DbSet` del tipo, y **SQL
crudo**.

**Lo que no se puede clasificar se declara ruidoso, no se ignora:** el verificador **no puede** saber
a que tabla escribe un `ExecuteSqlRaw` sin interpretar el SQL, asi que esos metodos **entran al
perimetro por las dudas** y se imprimen en una lista aparte para que alguien los mire. Hoy **ningun
Service usa SQL crudo**, asi que esa rama es un **tripwire y no cobertura** — y por eso se midio con
un mutante (`M17`) que agrega una escritura por SQL crudo y verifica que el detector la liste.

**El perimetro quedo en 35 POST** (QA habia medido 28 con su propio criterio; el de acá es mas amplio
a proposito). Si el conteo de entidades derivadas da 0, **el programa aborta**: "cero entidades con
`decimal`" es un fallo del verificador, no un dominio sin dinero.

**Los 12 que no estaban cubiertos ni declarados se clasificaron uno por uno**, y la clasificacion
ahora tiene **cinco grupos** en vez de tres, porque mezclarlos era parte del problema: **A** clave
natural cerrada, **B** defecto abierto, **C** protegido hoy por otro mecanismo (leido o medido), **D**
**SIN EVALUAR** (la cola real de la fase 2), **E** entra por el criterio amplio y no es un hecho
financiero repetible.

**Dos clasificaciones salieron de leer el codigo y no de suponer, y una me corrigio a mi:**

- **`AumentoMasivoPrecios/Aplicar` es IDEMPOTENTE POR CONSTRUCCION.** Mi instinto decia "un doble
  submit aplicaria el aumento dos veces" y **estaba mal**: los dos modos derivan el precio de
  `PrecioCompra` (`PrecioCompra * (1 + recargo/100) / (1 + IVA/100)`), **nunca del `PrecioVenta`
  anterior**, asi que aplicarlo dos veces da el mismo precio. Lo que si duplica es la fila de
  **auditoria**: el riesgo es de auditoria, no de plata.
- **`Caja/CerrarDia` y `Caja/CerrarMes` tienen el duplicado atajado** por los indices unicos entre
  vivos `UX_CierresCajaDiarios_Fecha_Vivo` y `UX_CierresCajaMensuales_Anio_Mes_Vivo` (migracion
  `Hotfix_UnicidadEntreVivos`) mas el candado del periodo de `LP-037`. **Lo que NO se midio es QUE SE
  LE CONTESTA al operador** cuando el segundo cierre choca contra el indice: si sale el mensaje crudo
  de EF, es `LP-116`. Eso queda escrito como el pendiente concreto de fase 2.

**Y el que mas impacto aparente tiene del grupo D es `Presupuestos/ConvertirAVenta`**: convierte un
presupuesto en una VENTA, asi que un doble submit podria crear dos ventas del mismo presupuesto.
Prioridad alta para la evaluacion de fase 2.

### `LP-126` `major` — un verde falso en el unico chequeo del modo de falla total

**El chequeo del cableado buscaba el Razor generado en `obj/generado`, que solo existe si alguien hizo
antes un build especial. En un build normal quedaba inerte — y el programa igual imprimia "el cableado
del helper esta bien".** Es el peor lugar del sistema para un verde que no midio nada: si el token no
llega al formulario, el filtro **falla cerrado** y la pantalla **rechaza toda emision**.

**Arreglo: el verificador se produce su propia evidencia.** Lanza el build de Web con
`EmitCompilerGeneratedFiles` a un **directorio temporal** (no ensucia el repo) y lo lee en la misma
corrida. Si el build no se puede hacer, **la afirmacion no se imprime** y la corrida sale con **exit
3** diciendo por que. Tambien sale exit 3 si el build anda pero no deja ningun Razor generado (un
cambio de nombre de propiedad del SDK no puede convertirse en un verde).

Medido con `M18`: rompiendo el `@addTagHelper` de `_ViewImports.cshtml`, el verificador imprime las
**dos** lineas `ROTO` y sale con **exit 3**, sin ninguna afirmacion en verde.

### `LP-125` `minor` — el token no nacia atado a la accion, y el XML-doc afirmaba que si

**El defecto tenia dos mitades y la segunda es la grave.** Un token **fresco** tomado del `<form>` de
logout y posteado a `Emitir` **emitia**: la validacion de accion vivia solo en el **consumo**
(`RutaAccion` se compara al encontrar el token ya usado), asi que el primer uso cruzado reservaba con
la accion del request que lo gastaba y el rechazo llegaba **un submit tarde**. Y el XML-doc decia lo
contrario — **eso es la familia `LP-044`/`LP-045`/`LP-051`: una afirmacion falsa en la documentacion,
que es peor que la garantia faltante, porque el que lee deja de buscar.**

**Arreglo: el token nace atado.** Pasa a ser `{nonce}.{huella}`, donde la huella son 8 hex del
SHA-256 de la **ruta destino normalizada**, que el tag helper toma del `action` **ya resuelto** por el
`FormTagHelper` (de ahi que este helper corra con `Order` alto — no es cosmetico). El filtro recalcula
la huella sobre `Request.Path` y **rechaza ANTES de reservar**, asi que el rechazo es pre-consumo. Un
token sin huella —la forma que emitia la version anterior— tampoco pasa.

**Y se dice lo que esto NO es, para no repetir `LP-125` en la otra direccion: la huella no esta
firmada y no es una credencial.** Cualquiera puede fabricar un token con la huella que quiera, y **no
compra nada**: un token es una clave de idempotencia, no un permiso, y cualquiera que pueda postear
obtiene uno legitimo abriendo el formulario. Lo que la huella evita es el uso **cruzado**. La
confidencialidad del resultado guardado es otra cosa y la cubre `UsuarioId` en el consumo. El XML-doc
ahora separa los dos momentos de validacion y dice que protege cada uno.

**Un detalle de robustez que aparecio arreglando esto:** el helper se aplica a **todos** los
formularios del sistema, asi que una excepcion suya tumbaria la pantalla entera. El acceso a
`ViewContext` quedo null-safe **por eso** y no por prolijidad — lo descubri porque el arnes lo
instanciaba sin `ViewContext` y el helper reventaba.

### `LP-128` `minor` — una de las 15 retiradas habia perdido cobertura

La vieja **`9.10`** afirmaba que el item fraccionario queda facturado por **2,5 EXACTO (1,5 + 1,0)**.
No medía la clave natural: medía que dos tandas de cantidades distintas **SUMEN** exacto. Mi nueva
`9.8` mide que las dos **entren**, que no es lo mismo — un bug que acepte las dos y sume mal, redondee
al entero o pise una con la otra pasa `9.8` en verde y deja la venta facturada por una cantidad que no
se vendio.

**Restaurada como `9.12`, al final de la familia y con numero NUEVO.** Va al final a proposito:
renumerar otra vez volveria inauditable esta misma lista de retiradas.

**La leccion de procedimiento, que es el dato mas util de este defecto y lo aporto QA:** al renumerar
la familia, `9.3`–`9.7` y `9.9` quedaron existiendo en las dos versiones **con sentidos distintos**,
asi que una auditoria **por id** no podia distinguir "retirada" de "renumerada" y QA tuvo que hacerla
**por texto**. **Si una familia se reescribe, las afirmaciones nuevas van con numeros nuevos.** Quedo
escrito en el encabezado de la familia 9.

### La correccion de QA a mi orden de riesgo, aplicada

Habia declarado `Ventas/Facturar` como *"el que mas necesita el token"*. **Es el menos urgente de los
cuatro**, medido: deriva sus lineas del pendiente, asi que el segundo submit **no tiene nada que
facturar** (1 comprobante en serie y en paralelo). Lo que lo hacia parecer urgente —que nunca puede
tener payloads distinguibles— es justamente lo que lo protege. Los otros tres tambien se movieron:
`Gastos/Anular` esta protegido **a proposito** (lee `gasto.Anulado` dentro de la transaccion, despues
del lock: `PAT-059` bien aplicado), `CCEmpleado/Revertir` tiene una clave natural **buena** (usa la
identidad del movimiento revertido y no un monto, asi que no paga el costo de negocio de las otras) y
`OrdenesCompra/RevertirPago` quedo **BLOCKED** (0 ordenes en el clon) y sigue sin evaluar.

Los cuatro pasaron del grupo "sin evaluar" al grupo C (protegido por otro mecanismo) salvo
`RevertirPago`, que se queda en D con el motivo del BLOCKED escrito.

### Cambios por capa

- **Web** — `TagHelpers/TokenDeSubmitTagHelper.cs` (el token nace atado: `Emitir`, `Huella`,
  `HuellaDe`; `[ViewContext]` null-safe), `Filters/TokenDeSubmitAttribute.cs` (valida la huella
  **antes de reservar**; XML-doc reescrito con los dos momentos de validacion y con lo que la huella
  **no** es).
- **tools/VerificadorCoberturaTokenDeSubmit** — entidades de dinero **derivadas de Domain**, tres
  formas de escritura, SQL crudo declarado aparte, chequeo de cableado que **corre de verdad** o no
  imprime, y las excepciones reclasificadas en cinco grupos.
- **tools/ArnesVentaSinFacturaYParcial** — `9.12` restaurada (vieja `9.10`) y la lista de retiradas
  del encabezado corregida: esa retirada **estaba mal** y lo dice.
- **tools/ArnesTokenDeSubmit** — `1.5`/`1.6` (la huella distingue rutas y normaliza), `4.5` (token
  fresco de otra pantalla **no** emite) y `4.6` (el control **anti-fail-closed**: un token de ESTA
  ruta si emite). Los tokens del arnes se emiten con **la funcion de produccion** y el fixture setea
  `Request.Path`.
- **Cero cambios en Domain, Application, Infrastructure/Services (salvo el mutante, revertido) y cero
  migraciones.**

### Evidencia

| Arnes | Antes del pase | Despues |
|---|---|---|
| `ArnesNotaCredito` | 63 OK / 0 | **63 OK / 0**, exit 0, `git diff` **vacio** |
| `ArnesVentaSinFacturaYParcial` | 96 OK / 0 | **97 OK / 0**, exit 0 (+`9.12` restaurada) |
| `ArnesTokenDeSubmit` | 30 OK / 0 | **34 OK / 0**, exit 0 (+`1.5`, `1.6`, `4.5`, `4.6`) |
| `ArnesReconciliacionTx` | 153 OK / 0 | **153 OK / 0**, exit 0 |
| `ArnesDevoluciones` | 63 OK / 0 | **63 OK / 0**, exit 0 |
| `VerificadorCoberturaTokenDeSubmit` | exit 0 con **23** y el cableado **inerte** | **exit 0**, perimetro **35**, cubiertos 1, declarados 34, sin cubrir 0, cableado **medido en la corrida** |

**Corrida mutante del pase (6 mutantes nuevos, `M16`–`M21`), y los cuatro arreglos arrancaron en FAIL:**

| Mutante | Que revierte | Tumbadas |
|---|---|---|
| `M16` | se saca la validacion de la huella | `4.5`, `4.6` (en cascada) |
| `M17` | una escritura de plata por **SQL crudo** | el verificador la lista como `[SQL CRUDO]` y la declara en el AVISO |
| `M18` | se rompe el `@addTagHelper` | el verificador imprime **dos** `ROTO` y sale **exit 3**, sin ningun verde |
| `M19` | la cantidad se trunca al entero al escribir la linea | **`9.12`**, `2.10` |
| `M20` | `Huella` devuelve una constante | `1.5`, `4.5`, `4.6` |
| `M21` | **la huella del filtro no coincide nunca con la del helper** | **18**, incluida `4.6`; **`4.5` NO cae** |

**`M21` es el que mas importa de los seis y conviene leer por que:** es el modo de falla **mas
probable** de esta pieza en produccion — cualquier divergencia de normalizacion entre la emision y la
validacion deja la pantalla **muerta**, porque el filtro falla cerrado. Y la asimetria entre `4.5` y
`4.6` es la que fija las dos direcciones: `4.5` **pasa en verde** bajo `M21`, porque rechazar todo
tambien rechaza el token cruzado. **Sin `4.6`, "la huella funciona" se podria afirmar con la pantalla
rechazando toda emision.**

**Build de la solucion `--no-incremental`: 0 errores / 9 advertencias**, codigos **`NU1902` +
`CS0114`** — la linea base exacta. Los `md5` de los 5 archivos mutados, identicos al pre-mutacion, y
la restauracion con `os.utime` (la trampa del `copy2` de la ronda anterior).

### Riesgos

1. **El perimetro de 35 incluye 2 entradas del grupo E** (catalogo y parametros) que entran por el
   criterio amplio. El criterio es deliberadamente amplio: sobre-reportar obliga a declarar de mas,
   sub-reportar deja plata duplicandose en silencio. **Si el grupo E crece, hay que revisar el
   criterio — no vaciarlo con excepciones.**
2. **El grupo D son 13 POST sin evaluar y es deuda, no cobertura.** El verde del verificador significa
   "nadie quedo sin mirar", no "la idempotencia esta resuelta"; el programa lo imprime en su ultima
   linea.
3. **La rama de SQL crudo es un tripwire sin uso en produccion** (cero Services la usan hoy). Esta
   medida por `M17`, no por un camino real.
4. **La huella agrega un modo de falla nuevo y es el que hay que mirar en el deploy:** si la
   normalizacion del helper y la del filtro divergen, la pantalla cubierta rechaza todo. Lo cubre
   `4.6` y lo mide `M21`, pero **en un request HTTP real sigue sin medirse**: es el punto #1 de la
   prueba manual, otra vez.
5. **El chequeo de cableado ahora corre un build dentro del verificador**, asi que la corrida tarda
   bastante mas. Es el precio de no imprimir un verde sin medir.

### Pruebas minimas para QA (pase 2)

1. **`dotnet run --project tools/VerificadorCoberturaTokenDeSubmit`** → exit 0, perimetro 35, sin
   cubrir 0, y la linea del cableado tiene que decir **"medido en ESTA corrida"**.
2. **Repetir los dos contraejemplos de `LP-127`**: una entidad nueva con un `decimal` y una escritura
   por SQL crudo. Las dos tienen que aparecer (la segunda, en el AVISO).
3. **`LP-126`**: romper el `@addTagHelper` de `_ViewImports.cshtml` → exit 3 y **ninguna** afirmacion
   en verde sobre el cableado.
4. **`LP-125` por navegador**: tomar el token del `<form>` de logout (o de cualquier otra pantalla) y
   postearlo a `FacturacionParcial/Emitir` → **0 emisiones** y cartel de rechazo. Y el control
   negativo en la misma sesion: el formulario propio **tiene que emitir** (si rechaza los dos, es
   `M21` en produccion).
5. **`LP-128`**: facturar 1,5 y despues 1,0 del item fraccionario → el item queda en **2,5 exacto**.
6. **Las 6 lineas base verdes** con los md5 de los DLL verificados antes de correr, como en el pase
   anterior.

## TOKEN DE SUBMIT — fase 1: el mecanismo + UN sitio (2026-10-09)

**Alcance: el mecanismo transversal y su aplicacion a UN solo POST (facturacion parcial), con el
interino de los 10 segundos retirado en el mismo movimiento.** Los 6 sitios con clave natural ya
cerrada no se tocaron. `LP-118`, `LP-120`, `LP-117`, `LP-121`, `LP-112`, `LP-113` tampoco. **Una
migracion aditiva. Sin commit. Ningun defecto marcado como cerrado.**

### El criterio que no se podia falsear, y como quedo

`ArnesNotaCredito` **volvio de 62/1 a 63/0, exit 0, sin que nadie toque el arnes**:
`git diff -- tools/ArnesNotaCredito` **vacio**. Es la linea base que el pase anterior dejo roja a
proposito, y es el unico caso que ninguna ventana podia satisfacer (su fixture hace dos tandas
legitimas identicas en milisegundos). Se puso verde solo al retirar la clave natural del Service.

### El mecanismo, por capa

- **Domain** — `SubmitProcesado`. **La clave primaria ES el token**, no un `Id` autoincremental: el
  consumo del token es literalmente el `INSERT`, asi que es **atomico en el motor** y cubre la
  repeticion EN SERIE y la CONCURRENCIA con el mismo mecanismo, sin ventana de lectura (no hay
  "consultar y despues insertar", que es el antipatron que `PAT-059` documenta). No hereda
  `SoftDestroyable`, mismo criterio que `CandadoPeriodoCaja`: una fila "borrada" contra la que el
  `INSERT` igual choca y que las consultas no ven seria un token quemado e invisible.
- **Application** — `IRegistroDeSubmit` (reservar / guardar resultado / purgar) y
  `ResultadoDeSubmit` + `ReservaDeSubmit`. El contrato vive en Application porque lo consume **Web**,
  que no depende de Infrastructure.
- **Infrastructure** — `RegistroDeSubmitService`. Dos decisiones que no son de estilo: (a) **todo va
  por SQL crudo en una conexion APARTE**, reusando el helper de `BloqueoDeFila.AsegurarCandadoPeriodoAsync`
  — porque la reserva tiene que ser visible para los competidores EN EL ACTO (dentro de la
  transaccion de la accion no lo seria hasta el commit y los dos ejecutarian) y porque un
  `SaveChanges` desde el mecanismo de idempotencia arrastraria al flush lo que el Service de negocio
  tenga trackeado; (b) la reserva es `INSERT IGNORE` y **se decide por las filas afectadas**, 1 = gane
  / 0 = ya estaba. El caso imposible (0 filas y la fila no existe) **rompe fuerte** con excepcion:
  las dos salidas silenciosas son peores — dejar pasar pierde la garantia sin que nadie se entere, y
  bloquear inventa un rechazo sobre una operacion legitima, que es la direccion de `LP-114`.
- **Web** — `TokenDeSubmitAttribute` (`IAsyncActionFilter`) + `TokenDeSubmitTagHelper` + 
  `PurgaSubmitsProcesadosMiddleware`. **Son el primer filtro y el primer tag helper propios del
  proyecto**, asi que establecen la convencion: carpetas `Filters/` y `TagHelpers/`, el helper
  registrado por assembly en `Views/_ViewImports.cshtml`.
- **Infrastructure/Migrations** — `20261009045813_TokenDeSubmit_SubmitsProcesados`. **Aditiva pura:**
  un `CreateTable` con su PK y el indice de retencion por `CreadoUtc`; cero columnas sobre tabla
  preexistente, cero backfill, `Down` = un solo `DropTable`. **Se suma a la cola de produccion, que
  pasa de 12 a 13 pendientes**, y no altera nada mas de esa cola.

### Las cinco decisiones del diseño, y como quedaron verificadas

1. **El token identifica al REQUEST, no al dato de negocio** → desaparece el costo de negocio. Medido
   en `ArnesTokenDeSubmit` 3.1/3.2/3.3: dos tandas identicas con **tokens distintos**, sub-segundo
   (81 ms), **emiten las dos** y no queda nada sin facturar. Es lo que ninguna clave derivada del
   payload podia hacer con ningun valor de ningun parametro.
2. **El unico va sobre el TOKEN y no sobre datos de negocio** → la decision 1 de `PAT-059` ("lock de
   fila, NO indice unico") se respeta: el unico es sobre algo que es unico por construccion.
3. **No reemplaza a `PAT-059`: se suma.** Los locks + relectura siguen puestos y se midieron DESPUES
   de retirar la guarda: `ArnesVentaSinFacturaYParcial` 9.9 ejecuta tres POST identicos en paralelo y
   afirma el invariante de la base (facturado <= vendido). **Esa afirmacion antes estaba tapada por la
   guarda retirada**: con la clave natural, los tres salian por idempotencia y el lock no tenia que
   hacer nada. Ahora el lock es lo unico que impide facturar mas que lo vendido. **Y se midio con su
   propio mutante (`M15`): quitando el lock, `9.9` cae con 3 comprobantes y 3.000 facturado sobre
   2.000 vendidas** — el numero exacto del defecto original de la familia `LP-018`.
4. **La forma de baja por familia deja de importar** (la clase de `LP-114` se extingue): el token no
   pregunta si la operacion anterior sigue viva, pregunta si **este** request corrio. Se retiraron las
   dos ramas que contestaban eso (`DeletedAt` y la nota de credito) porque quedaron sin objeto.
5. **Un solo contrato de resultado**: el replay **no llega al Service**. Medido por `2.4`, que exige
   las dos mitades: que el replay devuelva el mismo destino **y que la accion NO haya corrido**. Un
   replay que diera la respuesta correcta porque el Service volvio a emitir cumpliria todo lo demas y
   habria duplicado la plata.

### El contrato de resultado del replay

Se guarda, sobre la misma fila del token: la **clase** (redirect a accion / redirect a URL / no
replicable), el **tipo de aviso** (exito / advertencia / error, que es lo que decide el ICONO —
leccion de `LP-114`: un bloqueo con cartel verde es peor que el bug), el **mensaje** que el operador
vio, y el **destino** como **valores de ruta y no como URL ya armada**, para que la URL la genere MVC
al ejecutar el redirect del replay y un cambio de rutas no deje tokens apuntando a direcciones
muertas. El mensaje se toma de `TempData` con **`Peek` y no con el indexador**: leerlo de verdad lo
marcaria como consumido y el operador se quedaria sin el cartel de su propio submit, el que si entro.

**Tres decisiones del filtro que conviene leer antes de tocarlo:**

- **FALLA CERRADO.** Un POST sin token se rechaza, no se ejecuta sin proteccion. Fallar abierto
  convertiria cualquier formulario escrito a mano en un hueco silencioso, y esta ronda entera nacio de
  huecos silenciosos. El costo es que el mecanismo depende del tag helper global, y **eso se verifico
  en el RAZOR COMPILADO** (ver mas abajo), no por lectura.
- **NO hace falta "liberar" la reserva cuando la accion falla**, y es la pregunta que se contesto
  antes de escribir el codigo: el camino de error devuelve la VISTA, o sea **re-renderiza el
  formulario**, y el tag helper emite un token NUEVO en ese render. El reintento del operador nunca
  pasa por el replay. Liberar seria peor: habria que decidir "¿esto escribio algo?" desde afuera del
  Service, que es exactamente la pregunta que este mecanismo existe para no tener que hacer.
- **El residual, declarado:** un duplicado que llega mientras el ganador todavia corre no puede
  re-mostrar nada y recibe un aviso de *"se esta procesando"*. Pasa solo en concurrencia real, no en
  la repeticion en serie, y lo importante es que **NO EJECUTA** (medido en 7.1/7.2).

### El riesgo #1: se eligio la mitigacion (b), la verificacion ejecutable — y por que

El gate daba dos salidas: **(a)** filtro opt-out, **(b)** una verificacion ejecutable que enumere los
escritores de plata y falle si alguno no esta cubierto. **Se eligio (b), y la mitad opt-out que SI se
podia poner ya esta puesta.**

- **La mitad opt-out, gratis:** `TokenDeSubmitTagHelper` apunta a **todo `<form>` que no sea GET**, asi
  que del lado del render **no hay ninguna lista**: un formulario recibe su token por existir. Se
  decide por EXCLUSION (`method="get"`) y no por inclusion, porque `<form asp-action="X">` **sin
  atributo `method` renderiza un POST** y exigir `method="post"` escrito dejaria afuera la forma mas
  usada del repo — y afuera en silencio (lo mide 1.2).
- **Por que la ENFORCEMENT no puede ser opt-out en la fase 1:** aplicar el filtro globalmente a todo
  POST significa volver idempotentes ~35 metodos y 74 vistas **de una vez**, con un filtro que falla
  cerrado. Hacer siete sitios de una vez es textualmente como nacieron `LP-114`, `LP-117` y `LP-121`;
  el motivo de partir esto en dos fases es esa misma leccion aplicada a su propio arreglo. Encender un
  rechazo global en un solo movimiento es el cambio mas riesgoso disponible.
- **La mitigacion:** `tools/VerificadorCoberturaTokenDeSubmit`. Enumera por codigo los POST que llegan
  a un escritor de plata y **falla con exit 1** si alguno no esta ni cubierto ni declarado como
  excepcion **con su motivo**. La diferencia con el bloque `MISMA FORMA, SIN TOCAR` es exacta: ahi la
  lista era un comentario que nadie ejecutaba; acá un sitio nuevo que nadie anoto pone la corrida en
  rojo. **La lista sigue existiendo; lo que cambia es que mentir en ella cuesta un rojo.** Tambien
  denuncia las excepciones MUERTAS (las que ya no corresponden a ningun POST), porque una lista de
  permitidos que acumula entradas viejas vuelve a ser un comentario.
- **Probado por ejecucion, no por lectura:** quitandole `[TokenDeSubmit]` al unico POST cubierto, el
  verificador da **exit 1** y lo nombra; devolviendolo, **exit 0**.
- **Se puede borrar cuando la fase 2 termine** y el filtro pase a ser opt-out de verdad.

### EL HALLAZGO DEL VERIFICADOR, que no estaba en ningun parte de defecto

**El perimetro real son 23 POST que escriben plata, no los 13 sitios que la ronda de QA habia
medido.** Y llegar a ese numero costo dos correcciones del propio verificador, las dos encontradas
corriendolo y no leyendolo:

1. **Con un solo nivel de analisis el perimetro daba 10 POST y `Devoluciones/Registrar` NO estaba**,
   aunque es uno de los defectos abiertos de la familia: su Controller llama a `DevolucionService`,
   que no instancia la entidad de dinero — la instancia el Service de cuenta corriente en el que
   delega. Se agrego **cierre transitivo** sobre el grafo de llamadas entre Services. *Un verificador
   que no ve los dos sitios que ya sabemos que faltan no sirve para encontrar los que no sabemos.*
2. **Escaneando solo metodos publicos, `NotasCredito/Emitir` tampoco aparecia:** `NotaCreditoService`
   se partio en cascara y nucleo, y el `new ComprobanteAfip` vive en el **nucleo privado**. Se
   escanean todos los metodos y se agregaron las aristas intra-clase.

De los 23: **1 cubierto con token**, **5 del grupo A** (clave natural ya cerrada y medida, su retiro
es fase 2), **4 del grupo B** (defectos abiertos con parte de QA) y **13 del grupo C: sitios que esta
enumeracion encontro sola y que no tienen parte de defecto ni evaluacion.** El grupo C se declaro uno
por uno con lo unico que se puede sostener hoy — **"SIN EVALUAR"**, ni roto ni bien — e incluye tres
REVERSIONES (`CCEmpleado/Revertir`, `Gastos/Anular`, `OrdenesCompra/RevertirPago`), que son la forma
"fila nueva" que `LP-114` ya contesto mal, y `Ventas/Facturar`, que es **el sitio donde la clave
natural no es aplicable ni en principio** porque deriva sus lineas del pendiente.

### El cableado del tag helper, verificado en el Razor COMPILADO

Importa porque el filtro falla cerrado: si el token no llegara, la pantalla rechazaria **todo**. No se
dio por bueno por lectura:

```
dotnet build FerreteriaLaPlatense.Web -p:EmitCompilerGeneratedFiles=true \
  -p:CompilerGeneratedFilesOutputPath=obj/generado --no-incremental
```

El Razor generado de `Views/FacturacionParcial/Emitir.cshtml` **aplica `TokenDeSubmitTagHelper`** (3
referencias), y **48 de 87 vistas** lo reciben (las que tienen formularios no-GET). El verificador
rehace este chequeo; si el Razor generado no esta en disco, **lo declara NO MEDIDO con el comando
exacto** en vez de darlo por bueno.

### Que se hizo con la familia 10 del interino (y con la mitad de la familia 9)

**La familia 10 completa se RETIRO**, y la familia 9 de `ArnesVentaSinFacturaYParcial` se **reescribio,
no se "actualizo"**: lo que medía dejo de existir. El detalle, retiro por retiro, esta en el
encabezado de la familia 9 del arnes. Lo esencial:

- `10.1`/`10.2` (la misma tanda pasada la ventana emite) **se absorbieron en `9.6`/`9.7` SIN la espera
  real de 12 segundos**: ahora no hay nada que esperar y el escenario corre en 52 ms, que es
  justamente el criterio que ninguna ventana usable podia cumplir.
- `10.3` ("dentro de la ventana el doble clic colapsa") **afirmaba lo contrario de lo que hoy es
  correcto**: retirada. `10.4` (el margen de la ventana) quedo sin objeto: la ventana no existe.
  Dejarla midiendo una constante borrada era la unica salida deshonesta disponible.
- De la familia 9 se retiraron las que medían la clave natural (`9.4` del aviso, `9.11` del orden
  guarda-vs-tope, `9.12`/`9.13` del cargo de IVA, `9.14` del soft delete, `9.16` y `9.20` de la
  milesima) **y las dos que importan se reconstruyeron donde ahora vive la guarda**: el cargo de IVA
  que no se duplica es `ArnesTokenDeSubmit` 6.1/6.2 (postea dos veces con el MISMO token y verifica un
  solo cargo y un solo IVA de saldo).
- **Y se agrego `9.2` como TRIPWIRE:** *"el Service YA NO deduplica: dos POST identicos dejan DOS
  comprobantes"*. Es la red del error mas probable de la fase 2 — si alguien vuelve a poner una clave
  natural ahi, reabre `LP-122`, y esta afirmacion se enciende primero y con el motivo escrito. El
  mutante `M10` la mata junto con 9.3, 9.4, 9.6 y 9.7.

El arnes baja de **111 a 96 afirmaciones**: 15 retiradas por quedar sin objeto, con su motivo escrito
una por una, y las de valor reconstruidas en el arnes del token.

### Instrumento nuevo: `tools/ArnesTokenDeSubmit` (30 OK / 0 FALLADAS, exit 0)

Referencia **Infrastructure Y Web** (es la razon de que sea un arnes nuevo y no una familia mas: el
mecanismo vive en Web y los otros arneses no pueden ni instanciar el filtro) y **ejecuta el filtro de
verdad** sobre el controller de verdad sobre la base de verdad: se construye un `ActionExecutingContext`
a mano y el `next` del filtro invoca `FacturacionParcialController.Emitir(vm)`. Familias: 1 tag helper,
2 control **positivo**, 3 control **negativo**, 4 **IDOR**, 5 **falla cerrado**, 6 la plata, 7
concurrencia (un scope de DI por competidor + barrera), 8 la purga.

**Lo que NO puede medir, declarado y es el punto #1 para QA:** el pipeline HTTP real (antiforgery,
cookies) y el cableado del tag helper en la vista — eso lo cubre el verificador sobre el Razor
compilado. `TempData` usa el `TempDataDictionary` **real** de ASP.NET con un **proveedor** doblado en
memoria, asi que la semantica de `Peek` que el filtro usa es la de produccion.

### Corrida mutante: 15 mutantes

La union de tumbadas es **exactamente** el conjunto `[DISCRIMINA]` menos `7.3` y `7.4`, **que por eso
bajaron a `[COBERTURA]` con el motivo escrito al lado** en vez de quedar infladas. Cuando cinco marcas
`[DISCRIMINA]` quedaron sin mutante que las matara (`1.1`, `1.2`, `1.3`, `8.1`, `8.3`), **se escribieron
los mutantes que faltaban** (`M11`–`M14`) en vez de bajarles la marca. La tabla completa esta en el
encabezado del arnes. Los dos que mas enseñan **no son los que mas tumban**:

- **`M2` tumba SOLO la familia 7.** Cambia el `INSERT IGNORE` por "consultar si existe y despues
  insertar" —el antipatron de `PAT-059`— y **la repeticion en serie sigue toda en verde**: las 6
  afirmaciones de la familia 2 pasan sobre codigo con una ventana de carrera abierta. Es la prueba de
  que la familia de concurrencia **no es redundante** con la de serie, y de que *"el `INSERT` sobre la
  PK cubre las dos sin ventana de lectura"* se gano midiendo.
- **`M4` tumba SOLO `4.4`.** Valida el usuario y **no** la accion, o sea el IDOR a medias: `4.2` (otro
  usuario) pasa en verde. Sin `4.4`, *"el consumo valida usuario Y accion"* seria media verdad medida
  como entera.

- **`M15` es el mutante de la DECISION 3**, y hacia falta correrlo porque es la decision que mas
  facil se toma por cierta sin medirla. Quita el lock de fila de la venta en `EmitirAsync` y tumba
  `9.9` **con el numero exacto del defecto original: 3 comprobantes y 3.000 facturado sobre 2.000
  vendidas** (tambien `4.1`–`4.3` en dos escenarios y `8.21`). Sobre el arnes del token **no tumba
  nada**, y eso tambien es parte del resultado: el token corta el duplicado antes del Service. Las dos
  mitades juntas SON la decision 3 medida — ninguno de los dos mecanismos tapa al otro.

**Correccion de marca que salio de la corrida:** `4.3` ("el usuario ajeno tampoco EJECUTA") **no la
tumba `M3`**: sin la validacion, el ajeno recibe el REPLAY, asi que sigue sin ejecutar. Es
`[COBERTURA]` del invariante, no `[DISCRIMINA]` de la validacion — la que discrimina es `4.2`.

**Y una leccion de procedimiento del mismo M15, porque se llevo una corrida:** la primera vez `M15`
**no mato nada** y eso parecia decir que `9.9` era una afirmacion vacia. No lo era: el script lo habia
corrido contra **el arnes equivocado** (el del token, donde el mutante del lock efectivamente no
cambia nada), porque un `&&` corto-circuitado dejo sin aplicar el parche que agregaba la rama. *Un
mutante que no mata nada hay que creerle solo despues de verificar que corrio contra el instrumento
que mide esa afirmacion.*

### DOS TRAMPAS DE MEDICION, y las dos invalidaron una corrida entera antes de verse

1. **El arnes que corre el binario viejo.** Al borrar `VentanaDobleSubmitSegundos`,
   `ArnesVentaSinFacturaYParcial` dejo de compilar (referenciaba la constante). El build fallo, pero
   `dotnet run --no-build` corrio **el EXE anterior** y la corrida salio **111/0 midiendo el codigo
   viejo** — con los mensajes de la guarda que ya no existe en el log, que fue la unica pista.
   `tools/` no esta en la solucion, asi que `dotnet build` de la solucion no lo compila: **hay que
   mirar el resultado del build, no su tiempo transcurrido.** La corrida final ahora cuenta los
   errores de cada build y se niega a correr si hay alguno.
2. **La restauracion del mutante que no se recompila, Y EL `md5` NO LA DETECTA.** Restaurar el fuente
   desde el backup con `shutil.copy2` **preserva el mtime**, asi que el archivo restaurado queda **mas
   viejo que la DLL compilada con el mutante**: MSBuild lo ve "al dia", no recompila, y **el mutante
   sigue vivo en el binario mientras el fuente esta provablemente limpio**. El control de integridad
   por `md5` contra el backup **PASA**, porque el md5 es correcto — es la unica trampa de esta ronda
   que la verificacion de integridad recomendada no puede atrapar. Se descubrio porque el control
   negativo (familia 3) empezo a fallar en verde-limpio con el mensaje *"MUTANTE: clave natural de
   vuelta"* de `M10`, que ya estaba restaurado tres corridas antes. Y contamino la primera corrida
   entera en las dos direcciones: Web se "limpiaba" sola cuando el mutante siguiente tocaba
   Infrastructure (porque Web referencia Infrastructure y eso forza su recompilacion), pero no al
   reves. **Arreglo: `os.utime` al restaurar y todos los builds de la corrida con `--no-incremental`.**

### Cambios por capa

- **Domain** — `Entities/SubmitProcesado.cs` (nuevo).
- **Application** — `DTOs/ResultadoDeSubmit.cs` (nuevo: `ClaseDeResultadoDeSubmit`,
  `TipoDeAvisoDeSubmit`, `ResultadoDeSubmit`, `ReservaDeSubmit`), `Interfaces/IRegistroDeSubmit.cs`
  (nuevo).
- **Infrastructure** — `Services/RegistroDeSubmitService.cs` (nuevo); `Data/AppDbContext.cs` (DbSet +
  configuracion: PK sobre el token, indice de retencion); `DependencyInjection.cs` (registro scoped);
  `Services/FacturacionParcialService.cs` (**se retiro** la guarda de clave natural, la constante
  `VentanaDobleSubmitSegundos` y `CantidadComparable`, que quedo sin usos; el bloque de comentarios que
  queda cuenta que habia, por que se fue y **por que no tiene que volver**; se reescribio el punto 3
  del XML-doc de la clase, con la consecuencia para el que llame al Service: **dos llamadas identicas
  emiten dos comprobantes y eso es correcto**).
- **Web** — `Filters/TokenDeSubmitAttribute.cs` (nuevo), `TagHelpers/TokenDeSubmitTagHelper.cs`
  (nuevo), `Middleware/PurgaSubmitsProcesadosMiddleware.cs` (nuevo), `Views/_ViewImports.cshtml`
  (`@addTagHelper *, FerreteriaLaPlatense.Web`), `Program.cs` (`UsePurgaSubmitsProcesados()`, al lado y
  por la misma razon que `UseAvisoPagosProgramados()`), `Controllers/FacturacionParcialController.cs`
  (`[TokenDeSubmit]` sobre el POST + el comentario del aviso corregido: `EmitirAsync` ya no devuelve
  aviso por repeticion, la rama queda sin camino que la alcance y esta declarado).
- **Migraciones** — `20261009045813_TokenDeSubmit_SubmitsProcesados` (aditiva pura).
- **tools/** — `ArnesTokenDeSubmit` (nuevo), `VerificadorCoberturaTokenDeSubmit` (nuevo),
  `ArnesVentaSinFacturaYParcial` (familia 9 reescrita, familia 10 retirada).
- **`tools/ArnesNotaCredito` SIN TOCAR**, a proposito: es el criterio de aceptacion.
- **`appsettings.json`, `Seed` y `SeedData.cs` sin tocar** (`LP-108`, riesgo aceptado por el cliente).

### Evidencia

| Arnes | Antes | Despues |
|---|---|---|
| **`ArnesNotaCredito`** | **62 OK / 1 FALLADA** | **63 OK / 0**, exit 0, **`git diff` vacio** |
| `ArnesVentaSinFacturaYParcial` | 111 OK / 0 | **96 OK / 0**, exit 0 (15 retiradas con motivo) |
| **`ArnesTokenDeSubmit`** (nuevo) | — | **30 OK / 0**, exit 0 |
| `ArnesReconciliacionTx` | 153 OK / 0 | **153 OK / 0**, exit 0 |
| `ArnesDevoluciones` | 63 OK / 0 | **63 OK / 0**, exit 0 |
| `VerificadorCoberturaTokenDeSubmit` (nuevo) | — | **exit 0** — perimetro 23, cubiertos 1, declarados 22, sin cubrir 0 |

**Se midio arrancando en FAIL, dos veces y las dos veces de verdad:** la linea base de partida era
`ArnesNotaCredito` en 62/1 (el criterio de aceptacion, rojo a proposito antes de tocar nada), y el
arnes nuevo arranco en **28/2** por un defecto del instrumento — leia el resultado de
`ActionExecutingContext.Result`, que **esta vacio cuando el filtro deja correr la accion** (el
resultado vive en el `ActionExecutedContext` que devuelve el `next`), asi que el destino del submit
ganador salia en blanco. Arreglarlo agrego el campo `CorrioLaAccion`, que **termino siendo la mitad
mas importante de la familia 2**: sin el, un replay que devolviera la respuesta correcta porque la
accion volvio a correr pasaria todas las afirmaciones habiendo duplicado la plata.

**Build de la solucion `--no-incremental`: 0 errores / 9 advertencias**, codigos **`NU1902` +
`CS0114`**, los dos preexistentes — **la linea base exacta**. Lo que se compara son los codigos y no
el total, porque el total miente (el incremental da 8 por no recompilar `Web`).

**Migraciones:** 1 aditiva. **La cola de produccion pasa de 12 a 13 pendientes.**
`laplatense_dev` **no se toco**. Todo se midio contra clones desechables (`laplatense_token`,
`laplatense_nc16`, `laplatense_cr12`, `laplatense_recon_tx`, `laplatense_lote2`).

### Riesgos

1. **El cableado del tag helper es la pieza de la que depende el fail-closed**, y esta verificado en
   el Razor compilado pero **no en un request HTTP real**. Es el punto #1 de la prueba manual.
2. **`Views/_ViewImports.cshtml` es el unico del proyecto** (no hay `Areas`), asi que cubre todas las
   vistas. El dia que se agregue un `_ViewImports` de area, hay que repetir el `@addTagHelper` ahi o
   los formularios de esa area salen sin token **y el filtro los rechaza**.
3. **El token no cubre un cliente que reenvia sin pedir el formulario** (un script, una integracion).
   Supuesto verificado y sin cambios: no hay API publica y nadie llama a `IAfipService`. El filtro
   acepta tambien un encabezado `X-Token-De-Submit` para ese dia; hoy **ningun** POST lo usa.
4. **El residual de concurrencia**: el perdedor recibe *"se esta procesando"* en vez del resultado,
   porque el ganador todavia no lo guardo. No duplica plata (medido) pero el operador tiene que
   refrescar.
5. **Retencion de 7 dias** sobre una base con tope de 500 MB. Una fila son ~250 bytes; sin purga crece
   sin techo. La purga es oportunista (`PAT-056`): si el pool se recicla, el flag en memoria se pierde
   y vuelve a correr sin duplicar nada.
6. **El grupo C del verificador (13 POST sin evaluar) es deuda con nombre, no cobertura.** El verde del
   verificador significa "nadie quedo sin mirar", **no** "la idempotencia esta resuelta"; el programa
   lo imprime en su ultima linea para que no se lea mal.

### Pruebas minimas para QA

1. **`ArnesNotaCredito` tiene que dar 63/0 con `git diff -- tools/ArnesNotaCredito` vacio.** Es el
   criterio de aceptacion y no se puede falsear tocando el arnes.
2. **EL PUNTO #1, Y NINGUN ARNES LO CUBRE: facturacion parcial desde el NAVEGADOR, con el pipeline
   HTTP real.** El filtro falla cerrado, asi que si el token no llegara, la pantalla rechazaria toda
   emision con *"el formulario venía sin su identificador de envío"*. Hay que (a) abrir
   `FacturacionParcial/Emitir/{id}`, (b) **ver en el HTML el `<input type="hidden"
   name="__TokenDeSubmit">`** dentro del form, (c) emitir y que emita.
3. **Doble clic real** sobre "Confirmar": un solo comprobante y **el segundo submit tiene que mostrar
   el cartel de EXITO original**, no un error. (El arnes lo mide, pero no con SweetAlert ni con la
   cookie de TempData de verdad.)
4. **Dos tandas legitimas seguidas**: facturar 1 de 2, volver al detalle, "Facturar ítems" otra vez,
   facturar el 1 restante. **Tienen que entrar las dos** y la venta quedar facturada por completo —
   sin esperar ningun segundo. Es `LP-122`.
5. **Botón atrás + reenviar** el formulario viejo: tiene que re-mostrar la respuesta original (o el
   aviso de que ya se procesó), nunca emitir de nuevo ni mostrar un error crudo.
6. **Camino de error y reintento:** forzar un rechazo (pedir más que el pendiente), corregir sobre la
   pantalla que vuelve y confirmar. **Tiene que entrar** — es el escenario que prueba que el
   re-render emite un token nuevo, y es el que convertiria el fail-closed en un bloqueo si estuviera
   mal.
7. **`dotnet run --project tools/VerificadorCoberturaTokenDeSubmit`** tiene que dar exit 0, y vale
   leerle el grupo C: son 13 POST que escriben plata y nadie evaluó.
8. **Las dos pantallas que comparten el circuito**: anular una venta con comprobantes y emitir una
   nota de credito **siguen sin token** (fase 2) y no tienen que haber cambiado de comportamiento.

### Checklist de merge

- [x] Build de la solucion `--no-incremental`: 0 errores, 9 advertencias, codigos `NU1902` + `CS0114`
      (linea base exacta).
- [x] Cinco arneses en verde con exit 0, incluido el criterio de aceptacion sin tocar el arnes.
- [x] 15 mutantes; union de tumbadas = `[DISCRIMINA]`; **tres** marcas bajadas con motivo; cuatro
      mutantes escritos para cerrar las marcas que ningun mutante mataba; y `M15` corrido a proposito
      sobre la decision 3 (el lock sigue siendo portante: su mutante deja 3.000 facturado sobre 2.000).
- [x] `md5` de los cuatro archivos mutados identico al pre-mutacion, **y** verificado que la
      restauracion recompila (la trampa del mtime).
- [x] Migracion aditiva pura, `Down` por `DropTable`, revisada a mano.
- [x] `appsettings.json`, `Seed`, `SeedData.cs` sin tocar.
- [x] Verificador de cobertura en exit 0, con autotest (falla al quitar el atributo).
- [ ] **Sin commit y sin push** (pedido explicito).
- [ ] **Ningun defecto cerrado:** `LP-122` lo cierra QA viendo el arnes en verde, no esta nota.
- [ ] `laplatense_dev` sigue sin la migracion nueva: decision de Joaquin.

## `LP-122` / `LP-123` — la ventana de la guarda y el contrato del aviso (2026-10-08)

Segundo pase sobre `LP-119`, pedido por la re-verificacion de QA. **`LP-123` queda cerrado y
`LP-122` NO: el interino no alcanza, y abajo esta la medicion que lo prueba.**

### `LP-123` — `Success` solo no alcanza, y es el precio del diseño de `CreateAviso`

`ArnesReconciliacionTx` cayo de 153/0 a **151/2** (`5.1/N=3` y `5.1/N=8`). El dato estaba intacto
(`5.4` confirmaba un solo comprobante): el instrumento medía mal. `CreateAviso` deja `Success = true`
a proposito, asi que contar "exitos" por `Success` convierte **1 emision + (n-1) avisos** en "n de n"
y la afirmacion falla **sobre codigo correcto**.

**Arreglado y anotado en el lambda**, con la regla escrita para todo arnés del repo: si la operacion
medida puede devolver aviso, "exito" significa **`Success && !EsAviso`** (aplicó de verdad) y los
avisos se cuentan aparte. **`ArnesReconciliacionTx` vuelve a 153/153, exit 0.**

**El barrido completo de los 6 metodos que pueden devolver aviso** (`CCEmpleadoService.
RegistrarMovimientoAsync`, `CCProveedorService.RegistrarAjusteAsync`, `GastoService.CrearAsync`,
`PagoProveedorService.RegistrarPagoAsync`, `VentaWorkflowService.FacturarAsync` y
`FacturacionParcialService.EmitirAsync`) contra todos los `tools/`:

| Arnés | Estado | Por qué |
|---|---|---|
| `ArnesReconciliacionTx` `5.1` | **corregido** | el unico conteo por `Success` sobre un metodo con aviso |
| `ArnesLote1Guardas` `1.1`/`1c.2`/`1d.2` | sin cambios | ya resuelto por el otro camino: competidores **distinguibles** (una nota por competidor) |
| `ArnesSeisSitiosRestantes` `4.x` | sin cambios | afirma `exitos == n` **a proposito** ("idempotencia devuelve exito, no error") y tiene el invariante de filas aparte |
| `ArnesReconciliacionTx` `16.1` | sin cambios | `RevertirMovimientoAsync` no devuelve aviso (el aviso esta en `RegistrarMovimientoAsync`) |
| `ArnesDevoluciones` | **verificado por ejecucion**, 63/63 | llama a `EmitirAsync` tres veces, con payloads distintos |

### `LP-122` — la ventana: NO SE CIERRA CON EL INTERINO, y la medicion lo prueba

**Lo que SI se arreglo.** La ventana paso del **dia de negocio** a **10 segundos**
(`FacturacionParcialService.VentanaDobleSubmitSegundos`, publica y con el razonamiento completo en su
XML-doc, no enterrada en la consulta). Con eso:

- **La familia 10 del arnés, nueva, mide los dos lados:** `10.1`/`10.2` (control negativo) la misma
  tanda el mismo dia pasada la ventana **emite** y **no queda nada sin facturar**; `10.3` (control
  positivo) dentro de la ventana el doble clic sigue colapsando.
- **El piso de la ventana esta MEDIDO y no estimado** (`10.4`): una emision tarda **23 ms**, asi que
  10 s son **428x de margen**. La afirmacion exige >= 10x y se enciende si algun dia la emision se
  acerca a la ventana.
- El mensaje ahora ofrece una salida **que existe**: *"esperá 10 segundos y volvé a confirmar"*. El
  anterior prometia "repartilo en cantidades distintas", que en el caso de QA era imposible.
- `ArnesVentaSinFacturaYParcial`: **107 -> 111 OK / 0 FALLADAS**, exit 0.

**Lo que NO se arregla, y por que ningun valor de ventana puede:** el fixture de `ArnesNotaCredito`
hace sus dos tandas con **menos de un segundo** de diferencia. Medido: con la ventana en **1 segundo**
el fixture **sigue colapsando** (`62/1`, `facturas #61 y #61`). No es que 10 s sea mucho — es que el
fixture emite las dos tandas en milisegundos, tres ordenes de magnitud por debajo de cualquier ventana
usable.

**La razon de fondo, y es la misma que la nota al arquitecto:** un doble clic y una segunda tanda
legitima son **bit a bit el MISMO POST**. Lo unico que los separa es que el segundo se compuso sobre
una pantalla renderizada **despues** de que el primero commiteara, y eso **no viaja en el payload**.
Entonces los dos criterios de aceptacion son **mutuamente excluyentes**:

- `LP-119` exige que **N POST identicos EN SERIE** dejen uno.
- `LP-122` exige que una **segunda tanda identica, sub-segundo despues**, emita.

Son el mismo evento observable. **Ninguna condicion de tiempo puede satisfacer los dos.**

**El atajo que NO hay que tomar, escrito para que no lo tome el proximo:** excluir de la clave los
comprobantes **ya acreditados por una NC** pondria `ArnesNotaCredito` en 63/0 — porque en **ese**
fixture hay una NC en el medio. Y dejaria `LP-122` **abierto** en su forma pura ("facturo 2 ahora y 2
en seguida", sin NC de por medio), ademas de romper `9.16`. Cumple la letra del criterio y no el
defecto: es un parche al fixture, no un fix.

**Lo que cierra las dos:** el **nonce que identifica el render**, que es lo que la decision de
arquitectura recomienda y esta pendiente del gate de Joaquin. La ventana de 10 s esta escrita para que
el nonce **reemplace una sola condicion** y no haya nada mas que desarmar.

### Tres correcciones de QA a afirmaciones mias, aplicadas

1. **`8.19` no sostenia lo que el comentario decia.** Pasa en verde sobre el mutante del lock, 6 de 6:
   lo que evita el duplicado en el atajo **no es la guarda, es un `MySqlException: Deadlock found`**
   que mata a los perdedores (el atajo hace `UPDATE Venta.Estado` y el camino parcial no toca esa
   fila). Solo `8.21` lo delata. **Queda como `LP-124` `minor`, sin arreglar y declarado** en el
   arnés y en `VentaWorkflowService`. El lock de `EmitirAsync` **si** es portante para el camino
   parcial (su mutante deja 3 comprobantes y 3,000 facturado sobre 2,000 vendidas): la conclusion era
   correcta, la evidencia citada no.
2. **`9.16` no sostiene la direccion de la nota de credito** (sobrevive a los dos mutantes de filtro).
   La que la lleva es **`9.22`**. Se renombro para que diga lo que mide; **la marca sigue siendo
   `[DISCRIMINA]` y no bajo a `[COBERTURA]`**, porque la tumban `M1`, `M4`, `M6` y `M7` — discrimina
   la guarda, no el filtro.
3. **La rama del soft delete es INALCANZABLE en produccion:** **cero** escritores de
   `ComprobanteAfip.DeletedAt` (contado por QA, re-contado acá). `9.14` pasa a
   `[DISCRIMINA/DEFENSA-EN-PROFUNDIDAD]` y queda declarada como tripwire para cuando exista la baja
   de un comprobante, no como cobertura de un camino real.

### Cambios por capa

- **FacturacionParcialService.cs** — `VentanaDobleSubmitSegundos` (publica, documentada, con los dos
  limites y el residual); la condicion de tiempo pasa a `Fecha >= UtcNow - ventana`, calculada **en
  C#** y no dentro del `Where` (adentro EF usaria el reloj del motor y la ventana mediria tambien la
  deriva entre relojes); mensaje nuevo; anotaciones de las dos formas de baja.
- **VentaWorkflowService.cs** — la declaracion de `LP-124`.
- **tools/ArnesVentaSinFacturaYParcial** — familia 10 (4 afirmaciones) y las tres correcciones.
- **tools/ArnesReconciliacionTx** — `LP-123`.
- **CERO migraciones.** `appsettings.json`, `Seed` y `SeedData.cs` sin tocar. Sin commit.

### Corrida mutante (11 mutantes; los dos nuevos son de la ventana)

| Mutante | Tumbadas |
|---|---|
| `M1` la guarda no corre | 15 (las 14 de antes + `10.3`) |
| `M2` clave gruesa (sin mirar las lineas) | 20, incluidas 2.6, 2.9–2.12, 4.6 y 8.4–8.11 |
| `M3` ignora el soft delete | `9.14` |
| `M4` la guarda corre DESPUES del tope | `9.11`, `9.16` |
| `M5` no excluye las notas de credito | `9.22` |
| `M6` el colapso sale como exito liso | `8.19`, `9.4`, `9.5`, `9.11`, `9.16`, `9.17`, `9.20`, `10.3` |
| `M7` el aviso no devuelve el Id | `9.3`, `9.5`, `9.11`, `9.16`, `9.20`, `10.3` |
| `M8` no redondea al ancho de la columna | `9.20` |
| `M9` el atajo convierte el aviso en exito | `8.19` |
| **`M10` la ventana no tiene limite de tiempo** | **`10.1`, `10.2`** |
| **`M11b` la ventana vuelve a ser de UN DIA** (el valor del defecto) | **`10.1`, `10.2`** |

Las tres `[DISCRIMINA]` de la familia 10 (`10.1`, `10.2`, `10.3`) son **exactamente** las tumbadas de
esa familia; `10.4` `[COBERTURA]` no cayo con ningun mutante. `md5` del Service identico al
pre-mutacion.

**Un mutante invalido por construccion, y la leccion queda escrita en el arnés:** la primera version
de `M11` cambiaba **la constante** `VentanaDobleSubmitSegundos` a 86400. La familia 10 **deriva su
espera de esa constante**, asi que el arnés se quedo esperando **la ventana que el mutante acababa de
ensanchar** — la corrida quedo colgada y el log se leia como si el escenario no hubiera llegado (y
dejo el Service mutado, restaurado despues desde el backup, con `md5` de control). El mutante correcto
muta **la expresion de la consulta** y deja la constante quieta. Es la misma familia que "un mutante
puede volver excepcional un camino que en el codigo sano es un `return`": **el mutante puede romper al
instrumento, no solo al codigo.**

### Evidencia de la corrida final

| Arnés | Antes | Despues |
|---|---|---|
| `ArnesVentaSinFacturaYParcial` | 107 OK / 0 | **111 OK / 0**, exit 0 |
| `ArnesReconciliacionTx` | 151 OK / **2** | **153 OK / 0**, exit 0 |
| `ArnesDevoluciones` | 63 OK / 0 | **63 OK / 0**, exit 0 |
| `ArnesNotaCredito` | 62 OK / **1** | **62 OK / 1** — `LP-122` NO cerrado |

Build de la solucion `--no-incremental`: **0 errores / 9 advertencias**, codigos **8 `NU1902` + 1
`CS0114`** (la linea base).

**`LP-123` aplicado, pendiente de re-verificacion. `LP-122` NO CERRADO** — necesita la decision del
gate. Ningun defecto marcado como cerrado.

## `LP-119` — el doble submit PARCIAL de la facturacion parcial (2026-10-08)

**Alcance: UN defecto.** Los otros 6 de la familia de idempotencia quedan congelados esperando la
decision de arquitectura (token de submit vs. sitio por sitio). Nada de lo que entro acá anticipa esa
decision: es el molde que ya existe, sin abstraccion nueva, y se puede retirar borrando un bloque.

### El defecto, y por que el tope no lo cubria

`FacturacionParcialService.EmitirAsync` tenia el tope por item (R13) bajo lock y relectura, y por eso
se leia como cubierto. **Son dos preguntas distintas:** el tope pregunta *"¿esta cantidad cabe en el
pendiente?"* y la idempotencia *"¿este submit ya entro?"*. Con el submit **parcial** las respuestas
difieren: facturar 1 de 2 dos veces deja el acumulado en 2, que no supera lo vendido, asi que **el
tope deja pasar las dos emisiones**. Con el submit **completo** el tope si lo ataja — que es
exactamente por que nadie lo veia y por que el escenario del arnes tiene que pedir **media linea**.
Medido: con la linea entera, la familia nueva pasaba sobre el codigo roto (falso verde forma 1).

### La guarda

Clave natural **(venta, dia de negocio argentino, conjunto EXACTO de lineas `item -> cantidad`)**,
sobre **facturas vivas** de esa venta (`DeletedAt == null` por el query filter global +
`ComprobanteAsociadoId == null`), **bajo el mismo lock de la fila de venta, dentro de la misma
transaccion**, y **ANTES del tope**. Devuelve el Id del primer comprobante con
`ServiceResult.CreateAviso` / `EsAviso`.

- **Las lineas entran en la clave** porque facturar en dos tandas es el caso de uso del modulo: una
  clave por `(venta, dia)` a secas cierra el defecto y rompe la funcion principal. Medido con `M2`.
- **El orden (repeticion antes que limite)** es la regla que quedo escrita al cerrar `LP-095`: sin
  ella, el duplicado del ultimo tramo contesta *"quedan 0 por facturar"*, un error sobre algo que ya
  habia entrado bien. Se fija con la afirmacion 9.11, que compara **la respuesta** y no la cantidad
  de filas.
- **La comparacion se redondea al ancho de la columna** (`CantidadComparable`, `decimal(18,3)`): la
  cantidad viaja sin redondear y MySQL redondea al guardar, asi que comparar el payload crudo contra
  el valor guardado dejaba pasar el duplicado **por una milesima, en silencio**, justo en un catalogo
  que vende metros y kilos. Medido con `M8` / afirmacion 9.20.

### El costo, declarado

Dos tandas legitimas con **exactamente los mismos items y exactamente las mismas cantidades el mismo
dia** se colapsan — facturar 1 y 1 de un item de 2 en dos comprobantes separados. Implausible (la
pantalla propone por defecto el pendiente completo) y con salida en el mensaje: facturar el remanente
en un solo comprobante, o repartirlo en cantidades distintas. Preferible a dos comprobantes fiscales
por el mismo acto, que **el operador no tiene forma de deshacer**: no hay endpoint para dar de baja un
comprobante y la nota de credito no devuelve el item al pendiente (R18).

### Las dos formas de baja de un comprobante (la pregunta que `LP-114` contesto mal)

| Forma | Como se expresa | ¿Abre la guarda? |
|---|---|---|
| `DeletedAt` (soft delete) | **fila vieja** | **SI** — los lectores del ya-facturado filtran por el, o sea que la baja devuelve el pendiente. Sin endpoint hoy, latente. Afirmacion 9.14, mutante `M3`. |
| Nota de credito | **fila nueva** (contramovimiento) | **NO** — R18: la NC acredita un documento, no lo deshace. Es la **asimetria con CC-empleado** y lo que NO hay que copiar de ahi. Afirmaciones 9.16 y 9.22, mutante `M5`. |

### Cambios por capa

- **Infrastructure/Services/FacturacionParcialService.cs** — la guarda + `CantidadComparable`;
  XML-doc de clase de "LAS DOS COSAS" a "LAS TRES COSAS".
- **Application/Interfaces/IFacturacionParcialService.cs** — el contrato declara el tercer resultado
  y que todo caller tiene que mirar `EsAviso`.
- **Infrastructure/Services/VentaWorkflowService.cs** — `FacturarAsync` (el atajo legado) **propaga**
  el aviso en vez de convertirlo en exito, y se corrigio el comentario que decia *"el segundo ... lo
  rechaza"*, hoy falso para el caso que este atajo produce siempre (deriva las lineas del pendiente,
  asi que dos POST simultaneos mandan payloads identicos).
- **Application/Interfaces/IVentaWorkflowService.cs** — el contrato de `FacturarAsync` declara el
  aviso.
- **Web/Controllers/FacturacionParcialController.cs** y **VentasController.cs** (`Facturar` y
  `ConfirmarYFacturar`) — `TempData[EsAviso ? "WarningMessage" : "SuccessMessage"]`.
- **CERO migraciones.** La cola de produccion sigue en 12 pendientes.

### Instrumento: `tools/ArnesVentaSinFacturaYParcial`

**82 OK / 0 FALLADAS antes -> 107 OK / 0 FALLADAS despues**, exit 0. Linea base con el defecto vivo:
**10 FALLADAS** (9.2, 9.3, 9.4, 9.5, 9.6, 9.8, 9.11, 9.12, 9.13, 9.16).

Tres correcciones del propio instrumento, las tres encontradas **ejecutando**:

1. **El escenario 4 dejo de medir el tope.** Sus N competidores pedian la cantidad completa, o sea
   payloads **identicos**: con la guarda puesta son un doble submit y la idempotencia los colapsa
   antes del tope, con 4.2/4.3 igualmente en verde. Es lo mismo que le paso al escenario de `LP-088`
   al cerrar `LP-095`. Ahora cada competidor pide una milesima menos (2 / 1,999 / 1,998...): cabe
   solo, la suma no, y ninguno es la repeticion de otro. **4.6 es el canario que lo fija.**
2. **La limpieza final moria con exit 127.** `ComprobantesAfip` tiene una FK **a si misma**
   (`ComprobanteAsociadoId`), asi que el `DELETE` unico revienta en cuanto un escenario emite una NC
   — **despues** de imprimir todas las afirmaciones y **antes** del `=== RESULTADO ===`: la corrida
   se lee completa. Se borran las NC primero y **la limpieza ahora se afirma** (`0.1`).
3. **`8.19` cambio de contrato, no de veredicto.** El atajo deriva sus lineas del pendiente, asi que
   tres atajos simultaneos piden lo mismo **por construccion** y no se pueden distinguir. El
   invariante sigue midiendo el lock (sin el, los tres leen la tabla vacia y los tres emiten); lo que
   cambia es la respuesta, asi que "ganador" se redefinio como **emitio de verdad**
   (`Success && !EsAviso`).

### Corrida mutante (9 mutantes)

| Mutante | Tumbadas |
|---|---|
| `M1` la guarda no corre (el defecto) | 14 |
| `M2` guarda DEMASIADO ANCHA (por venta+dia) | 19, incluidas 2.6, 2.9–2.12, 4.6 y 8.4–8.11 |
| `M3` ignora el soft delete | 9.14 |
| `M4` la guarda corre DESPUES del tope | 9.11, 9.16 |
| `M5` no excluye las notas de credito | 9.22 |
| `M6` el colapso sale como exito liso | 8.19, 9.4, 9.5, 9.11, 9.16, 9.17, 9.20 |
| `M7` el aviso no devuelve el Id | 9.3, 9.5, 9.11, 9.16, 9.20 |
| `M8` no redondea al ancho de la columna | 9.20 |
| `M9` el atajo convierte el aviso en exito | 8.19 |

**Reparto:** las 18 afirmaciones `[DISCRIMINA]`/`[DISCRIMINA/NEGATIVO]` de la familia 9 son
**exactamente** las tumbadas de la familia 9, salvo `9.21` `[CONTEXTO]`, que cae solo bajo `M2`
porque ese mutante le rompe la **precondicion** (es el canario funcionando, no una marca mal puesta).
`9.1` y `9.7` `[COBERTURA]` no cayeron con ningun mutante. `md5` de los dos Services identico al
pre-mutacion.

**`M5` sobrevivio en la primera vuelta con cero tumbadas**, y la lectura correcta no era "sobra el
filtro" sino **"falta el escenario"**: sin `ComprobanteAsociadoId == null`, las lineas de una NC son
candidatas a *"el comprobante que ya emitiste"* y el aviso devolveria el Id de una **nota de credito**
presentandolo como la factura. Se construyo 9.22 para que **solo la NC pueda coincidir** (factura por
2, NC por 1, POST de 1) y `M5` murio.

### Lo que NO entro

`LP-120` (la nota de credito duplica igual, $1.210 por un pedido de $605) **queda abierto y es el
camino de remedio de este defecto**: una factura que ya se duplico sigue sin salida limpia. Los otros
5 de la familia, congelados. Ninguna migracion. Ningun commit.

**`LP-119` queda APLICADO, PENDIENTE DE RE-VERIFICACION.** El cierre lo declara QA en contexto nuevo.

### Nota para el arquitecto

Trabajando esto quedo claro **cual es el limite de este molde, y es medible, no una opinion**: ningun
dato del payload distingue *"doble clic de 1 de 2"* de *"segunda tanda legitima de 1 de 2"*. Son
**bit a bit el mismo POST**; lo unico que los separa es que el segundo se compuso sobre una pantalla
**renderizada despues** de que el primero commiteara. O sea: **el costo declarado de esta guarda no
se puede bajar agregando campos a la clave natural — solo con un dato que identifique el RENDER**
(token de submit por formulario, o el ya-facturado al momento de abrir la pantalla, que es el mismo
mecanismo con otra cara). Esto vale para **toda** la familia; en facturacion parcial se ve mas porque
emitir dos veces lo mismo es un caso de uso y no un error.

Dos datos mas para la evaluacion:

- El atajo `VentaWorkflowService.FacturarAsync` **no puede** tener payloads distinguibles: deriva las
  lineas del pendiente. Un token de submit es la **unica** forma de darle idempotencia de acto, y hoy
  depende enteramente del lock.
- `CantidadComparable` existe porque la clave natural compara un payload `decimal` contra un valor
  **ya redondeado por la base**. Un token no tiene ese problema: toda clave natural sobre importes o
  cantidades lo tiene, y es un error que no se ve.

## Ronda de QA 2026-10-08 / lote 1, PASE 2 — la regresion propia y los tres puntos de la re-verificacion (2026-10-08)

QA re-verifico el lote de forma independiente: **5 de las 6 guardas cerradas con par discriminante**
(incluida `LP-106`, medida en las dos mitades y confirmando que el `SecurityStampValidator` **no**
quedo reemplazado), y **las tres afirmaciones propias del pase 1 probadas las tres**. La del lock de
`OrdenesCompra` quedo probada del lado que mi primer mutante no habia logrado: quitandolo, el pago
**enteramente programado** mete 2 y 3 pagos, asi que **el lock es portante ahi**.

Este pase corrige **una regresion propia que bloqueaba el merge** y tres puntos mas.

### 1. `LP-114` `major` — regresion propia en `CCEmpleadoService`: LA BAJA QUE SE EXPRESA COMO FILA NUEVA

**Lo que rompia:** la secuencia **registrar -> revertir -> re-registrar el mismo dia** quedaba
bloqueada. **El empleado no cobraba.** Y el agravante es el aviso: salia con **icono de EXITO**
diciendo *"ya estaba registrado... Saldo actual: $ 0,00"*, asi que el operador leia verde y se iba.
Un bloqueo que se presenta como exito es peor que un error.

**La forma que me faltaba en el barrido, y es la que va a reaparecer.** En los otros tres sitios la
baja **se expresa como ESTADO EN LA FILA VIEJA**, y por eso la clave natural sola alcanza: en el pago
es `Estado = Revertido`, en el gasto el flag `Anulado`, en la CC de clientes el soft delete que el
query filter ya saca. Las tres se ven mirando la fila que la consulta trae. **Acá la baja se expresa
como una FILA NUEVA**: `RevertirMovimientoAsync` postea un **contramovimiento** con
`MovimientoRevertidoId` apuntando al original y **no toca el original** — queda con
`EsReversion = false`, el mismo importe y el mismo motivo. Mi filtro `!EsReversion` lo seguia
encontrando. Es la unica de las cuatro familias donde la pregunta *"¿esta vivo?"* **no se puede
responder mirando la fila**.

**El fix:** el candidato cuenta como duplicado **solo si su NETO VIVO es distinto de cero**, y se
consulta con `ObtenerNetoVivoAsync` en vez de escribir un segundo calculo — en este ledger
*"¿esta vivo?"* ya tiene **una** definicion (`signo(X) + Σ signo(contramovimientos de X)`), y tener
dos contadores del mismo numero es como se descubre un saldo que no cuadra. Sirve ademas para la
reversion **parcial**, donde un flag booleano no alcanzaria.

**La guarda se abre SOLO para la fila revertida, no para todo:** abrirla del todo cerraria `LP-114` y
**reabriria `LP-082`**. Esta medido en las dos direcciones (ver mas abajo, `M13`).

**Verificado que ARRANCA EN FAIL:** sobre el codigo del pase 1, el escenario `4b` del arnes daba **3
FALLADAS** — el re-registro devolvia el Id del original (`Id 3` cuando el original era `3`) y dejaba
**1 egreso de caja en vez de 2**. Con el fix, 38 OK / 0 FALLADAS.

### 2. El ICONO — el costo real de dos claves naturales no era el bloqueo, era el aviso

QA midio los dos costos que declare en el pase 1 y los **confirmo**; su juicio de negocio sobre
`LP-064` es que el costo es **alto**: *"dos fletes de $8.000 el mismo dia con igual descripcion es
rutina en una ferreteria"* (dos viajes del mismo flete, mismo precio, descripcion "flete"). **Y que
el problema no esta en la guarda sino en que el aviso venia con icono de exito**: el operador lee
verde, se va, y el segundo flete nunca se pago.

**No se saco ninguna guarda.** Se agrego el tercer resultado que faltaba:
`ServiceResult<T>.CreateAviso` + la bandera `EsAviso`, con `Success` **en `true` a proposito** — la
operacion no fallo, no hay nada que reintentar ni `ModelState` que repintar, y los callers que solo
miran `Success` siguen redirigiendo igual. **Lo unico que cambia es el icono y el titulo.** El
`_Layout` tiene una rama nueva `TempData["WarningMessage"]` con `icon: 'warning'` y titulo *"No se
registró de nuevo"*, y los cuatro controllers mapean
`TempData[result.EsAviso ? "WarningMessage" : "SuccessMessage"]`.

Aplicado a los cuatro avisos de colapso: `GastoService`, `CCEmpleadoService`, `CCProveedorService` y
`PagoProveedorService`. `LP-095` sin nota sigue siendo un costo aceptado (hay numero de transferencia
a mano y el mensaje ensena la salida), **pero el icono corresponde igual**.

### 3. `LP-116` `major` — el mensaje crudo de EF al usuario

`/Proveedores/Create` concurrente mostraba `"Error al crear el proveedor: Could not save changes.
Please configure your entity type accordingly."` — texto de EF Core, en ingles, y el operador no
puede hacer nada con eso. Ahora hay un `catch (DbUpdateException ex) when
(EsDuplicadoDeProveedor(ex, out var porCuit))` que contesta un mensaje de negocio **nombrando el dato
que colisiono** (el CUIT o la razon social) y diciendo que lo busque en el listado.

**Se matchea por el NOMBRE DEL INDICE y no por el numero de error 1062**, a proposito: el numero dice
*"hay un duplicado"* pero no **de que**, y este metodo tiene dos indices que producen el mismo numero
y necesitan mensajes distintos. **Si no reconoce el indice devuelve `false` y la excepcion sigue al
catch generico**: tragarse una `DbUpdateException` cualquiera y contestar "ya existe un proveedor"
seria mentirle al usuario sobre un fallo que puede ser otra cosa (una columna corta, una FK, un
timeout). Falla cerrado hacia el mensaje generico, que al menos no afirma una causa falsa.

**Y se declaro la dependencia accidental**, que es lo que mas vale del punto: las dos validaciones de
`CrearAsync` son `AnyAsync` **fuera de la transaccion**, asi que no dan exclusion. Lo que hoy evita el
duplicado son los indices unicos `UX_Proveedores_Nombre_Vivo` y `UX_Proveedores_CUIT_Vivo` — QA lo
midio: **con indice deja 1 fila, sin indice deja 3 en paralelo**. El metodo esta bien **por
accidente**, y si alguien relaja uno de esos indices pasa a duplicar sin que su codigo haya cambiado.
Ahora esta escrito en el call site. **No se le agrego lock**: el dueno del nombre/CUIT es la tabla
entera y no una fila bloqueable, asi que la solucion correcta **es** el indice unico — cerrar esa
carrera de otro modo es alcance aparte.

### 4. `LP-115` `low` — DECISION: el arnes estaba detectando algo REAL, no quedo desactualizado

`ArnesReconciliacionTx` habia bajado de **153/153 a 152/153**, fallando `16.1/N=8` (*"0 de 8"*).

**Decision: NO se toco una sola linea del arnes, porque la afirmacion tenia razon.** El escenario 16
corre `foreach (var n in new[] { 3, 8 })` y siembra las dos veces con **la misma clave natural** —
mismo empleado, concepto, tipo, importe, dia **y el mismo `Motivo`**, que es una constante sin `n`
adentro. Con la guarda del pase 1, la siembra de `N=8` **colapsaba contra el movimiento de `N=3`, que
ya estaba revertido**, y devolvia su Id; las 8 reversiones concurrentes fallaban entonces con *"Ese
movimiento ya fue revertido"* y `exitos` daba **0**.

O sea: **`LP-115` y `LP-114` son el mismo defecto visto desde dos lados.** El arnes estaba midiendo
la regresion por un camino que ninguna otra medicion toco — y si hubiera "actualizado la afirmacion
con una justificacion", habria tapado el defecto que bloqueaba el merge. **Con el fix de `LP-114`,
`ArnesReconciliacionTx` vuelve a 153/153 y exit 0 sin ningun cambio en el instrumento**, que es la
prueba de que la decision era esa y no la otra.

Es el caso inverso al de la memoria del rol (*"si el parte deja elegir entre arreglarla para que mida
y declararla como tripwire, elegir medir"*): acá la eleccion era entre **ajustar el instrumento** y
**creerle al instrumento**, y la regla que queda es — **un arnes que cae junto con un fix se
investiga antes de actualizarse; el orden "entender despues de editar" es el que pierde el defecto.**

### Evidencia del pase 2

- **Build de la solucion no incremental: 0 errores / 9 advertencias**, mismos **codigos** que la linea
  base (`NU1902` + `CS0114`, los dos preexistentes). Cero advertencias nuevas.
- **`tools/ArnesLote1Guardas`: 38 OK / 0 FALLADAS**, exit 0 (eran 34; el escenario `4b` de `LP-114`
  suma 4 afirmaciones).
- **`LP-114` arranca en FAIL y pasa despues**, con control positivo: dos mutantes nuevos, los dos
  discriminan y **cero `[COBERTURA]` caida**.
  - `M12` — vuelve al bug (toma el primer candidato sin mirar si sigue vivo): tumba `4b.1 4b.2 4b.4`.
  - `M13` — **direccion opuesta**, abre la guarda del todo (cierra `LP-114` y reabre `LP-082`):
    tumba `4.1 4.2 4b.4`. **`4b.4` es el control positivo** y lo tumban los dos, que es exactamente
    lo que tiene que pasar: no alcanza con abrir la guarda, hay que abrirla **solo** para la fila
    revertida.
- `md5sum` de `CCEmpleadoService.cs` post-mutacion **identico** al pre-mutacion.
- **Las dos lineas base de arneses, intactas y sin tocarlas**: `ArnesReconciliacionTx` **153 OK / 0
  FALLADAS** (vuelve de 152) y `ArnesSeisSitiosRestantes` **32 OK / 0 FALLADAS / 2 NO MEDIDAS** (las
  2 NO MEDIDAS son las preexistentes declaradas, no nuevas).
- **Cero migraciones** en este pase tambien. La cola de produccion sigue en **12**.
- `appsettings.json`, bloque `Seed` y `SeedData.cs` **sin tocar**.

**`LP-112` y `LP-113` no se tocaron**: son partes aparte. Dato para cuando toquen — **QA corrigio mi
diagnostico de `LP-113`**: la causa es `cambioElSaldoInicial` leido **antes** de la transaccion, no el
neto vivo que yo habia declarado en el bloque `MISMA FORMA`. Conviene corregir esa linea del bloque
cuando se encare, para no mandar al siguiente por el camino errado.

**Ningun defecto se marca como cerrado:** el veredicto es de QA. Los cuatro puntos de este pase
quedan **aplicados, pendientes de re-verificacion**.

## Ronda de QA 2026-10-08 / lote 1 de fixes — guardas transaccionales y revocacion de acceso (2026-10-08)

Lote de **garantia** sobre alcance ya entregado y cobrado: cero alcance nuevo, cero migraciones.
Seis defectos de QA, **todos aplicados y PENDIENTES DE RE-VERIFICACION** — el cierre lo declara QA
en una corrida independiente, con cada criterio arrancando en FAIL.

**El brief traia dos datos de ruta equivocados y conviene dejarlos corregidos**: los proyectos son
`FerreteriaLaPlatense.Infrastructure` / `.Web`, no `Infrastructure/` / `Web/`, y los numeros de
linea citados no coincidian. El resto de los datos medidos del brief (22 migraciones, build 0/9, los
15 escritores del ledger) se verificaron de primera mano y estaban bien.

### Las seis guardas, con su costo declarado

| Defecto | Sitio | Guarda puesta | Por que esa y no otra | Costo declarado (caso legitimo que se colapsa) |
|---|---|---|---|---|
| `LP-088` critical | `PagoProveedorService.RegistrarPagoAsync` | lock de `OrdenesCompra` + relectura de estado + **`ObtenerSaldosAsync` releido adentro de la transaccion** | el tope comparaba contra `SaldoSinComprometer`, una **propiedad calculada del DTO** proyectada antes de abrir la transaccion: el dato vencido viajaba dentro del DTO y la propiedad lo hacia **parecer fresco en el punto de uso**. Mover la lectura ES el fix; el lock es lo que la hace valer | ninguno: la comparacion y los mensajes no cambiaron, solo **cuando** se lee |
| `LP-095` major | idem | idempotencia por clave natural **por linea y con multiplicidad** (compra, dia, metodo, importe, nota, estado, fecha tentativa) | el lock NO arregla el doble submit: 3 POST identicos pasan el tope **de a uno** y en serie, asi que son individualmente validos. Y la idempotencia sin lock no frena el paralelo. **Las dos son necesarias y ninguna sustituye a la otra** | dos pagos realmente distintos, identicos en los seis campos, el mismo dia. Es el mas plausible de la familia porque **la nota es opcional y dos lineas sin nota son identicas**. Se acepta: el mensaje dice que poner el numero de transferencia en la nota lo habilita, y eso es justo para lo que ese campo existe |
| `LP-064` major | `GastoService.CrearAsync` | clave natural de 6 campos (dia, categoria, importe, forma de pago, tipo de impacto, descripcion), **serializada por el candado del periodo** | un gasto **no tiene dueño**: no hay cliente, proveedor ni documento padre que bloquear. Lo que si hay es la fila centinela del dia (`CandadosPeriodoCaja`), que `ValidarPeriodoAbiertoAsync` ya toma y es un record lock sobre una fila que **existe**. El dia es exactamente el alcance que la clave necesita; un lock mas serializaria dias distintos sin comprar nada | dos gastos distintos identicos en los seis campos el mismo dia (dos fletes de $8.000). **Mas plausible que en los otros sitios**, porque la descripcion de un gasto se repite mas que un motivo de ajuste. Mensaje: diferenciar la descripcion |
| `LP-082` major | `CCEmpleadoService.RegistrarMovimientoAsync` | `BloquearUsuarioAsync` (nuevo) + clave natural (empleado, dia, concepto, tipo, importe, motivo) | el saldo del empleado es un agregado sin fila propia: se serializa por su dueño, la fila de `AspNetUsers`. Necesita un **lock por PK string** (450 chars), que `BloquearAsync` no soporta. La guarda va en **LOS DOS caminos** (el que mueve caja y el devengamiento), no solo en el que QA reporto — ponerla dentro del `if (mueveCaja)` habria cerrado el parte y dejado el defecto vivo en el camino de al lado | dos movimientos identicos intencionales el mismo dia para el mismo empleado. El medio de pago queda **afuera** de la clave a proposito: si el operador lo cambia no esta cargando otro adelanto sino corrigiendo el mismo |
| `LP-093` major | `CCProveedorService.RegistrarAjusteAsync` | transaccion (no tenia ninguna) + `BloquearAsync(Proveedores)` (nuevo) + clave natural | clon del molde con el proveedor en lugar del cliente. **No** valida ni bloquea periodo de caja: un ajuste de CC no escribe caja, asi que toma un solo lock, el de nivel 4 | un ajuste identico intencional el mismo dia (dos bonificaciones de $1.000 con el mismo texto de motivo) |
| `LP-106` high | `UsersController.ToggleEstado` **y** `Program.cs` `OnValidatePrincipal` | (a) `UpdateSecurityStampAsync` al togglear; (b) chequeo de `Estado` en cada request autenticado | **las dos mitades, y por razones distintas.** (a) es lo que revoca de verdad: el `ValidationInterval` dice **cada cuanto** se pregunta, no **que** se pregunta — si el stamp no cambia, la comparacion da igual y la sesion se renueva hasta el `ExpireTimeSpan` de 8 h. (b) existe para que el bloqueo valga **aunque mañana aparezca otro camino que escriba `Estado` sin rotar el stamp**, que es exactamente como nacio el defecto. Una guarda que depende de que todos los escritores futuros se acuerden de algo no es una guarda | una consulta por PK por request autenticado. La revocacion pasa de "hasta 5 minutos" a **inmediata**. Si alguna vez molesta, lo que hay que cachear es el resultado, no sacar la guarda |

**`OnValidatePrincipal` se CHAINEA, no se reemplaza**, y es lo que no hay que romper: `AddIdentity`
instala `SecurityStampValidator.ValidatePrincipalAsync` en ese mismo evento y
`ConfigureApplicationCookie` corre **despues**, asi que asignarlo sin llamarla pisa la validacion de
stamp entera — y con ella el unico mecanismo que hoy revoca al cambiar la password. La llamada
explicita es la que mantiene vivo el criterio *"el cambio de password sigue rotando el stamp"*.

**Un comentario falso corregido**: `Program.cs` decia que el `ValidationInterval` *"revoca sesiones
de usuarios bloqueados/modificados"*. Era falso, y es la misma categoria de defecto que `LP-008`:
una regla de negocio mentirosa viviendo en el repo.

### Tres defectos PROPIOS que encontro la medicion, no la lectura

1. **El ORDEN de las dos guardas de `RegistrarPagoAsync` estaba mal.** El tope corria **antes** de la
   idempotencia, asi que un submit repetido se medía contra el saldo como si fuera un compromiso
   nuevo: el operador paga **el saldo completo** y hace doble click, el 1.er submit deja el saldo
   libre en $ 0, y el 2.º salia con *"supera el saldo pendiente"* — un error sobre su propio
   duplicado en vez del reconocimiento de que su pago ya entro. No corrompe datos, pero rompe el
   contrato de idempotencia **en el caso mas frecuente**: pagar todo lo que falta es lo normal, no el
   borde. Reordenado a lock -> idempotencia -> estado -> tope, con la afirmacion `2c.2` que fija ese
   orden. **No estaba en ningun parte de QA.**
2. **El escenario textual de `LP-088` ya no mide `LP-088`.** El parte usa 3 POST **identicos**, y con
   `LP-095` arreglado tres payloads identicos son un **doble submit**: la idempotencia los colapsa
   antes de que el tope los vea. El dato de plata queda bien (un pago, $ 300.000) pero los tres
   contestan **exito idempotente** en vez de "supera el saldo". **Para QA**: si se corre el criterio
   textual tal cual y se ven tres mensajes de exito, la lectura natural es "`LP-088` sigue abierto" y
   **no lo esta** — hay que mirar **las filas**. Para medir el tope hacen falta tres pagos paralelos
   y **distinguibles** (nota distinta). Las dos variantes quedaron medidas por separado (escenarios 1
   y 1c).
3. **El lock de `OrdenesCompra` es redundante para un pago inmediato del mismo dia**, porque el
   candado del periodo ya los serializa. Donde **si** es el unico serializador es en el pago
   enteramente **programado**, que no escribe caja y por lo tanto no toma el candado: sin el, tres
   POST paralelos programan $ 900.000 sobre una compra de $ 400.000 — el *"se podria agendar el
   total completo tres veces"* que el comentario del tope dice que previene y que en concurrencia
   **no prevenia**. Salio de un mutante que no mato nada: **un mutante que no mata nada no prueba que
   el codigo sobre, prueba que falta el escenario** (de ahi el escenario 1d).

### El bloque `MISMA FORMA` rehecho por ENUMERACION

El bloque vive en `CuentaCorrienteClienteService.cs` y nombraba **2** sitios pendientes, ninguno de
los 4 que QA encontro fallando. **Tres rondas de QA encontraron por separado un sitio que no estaba
ahi.** El problema no era que la lista estuviera corta: se mantenia **por memoria del que pasaba**,
asi que lo que no se le ocurria a nadie no entraba nunca. Se rehizo barriendo los 15 archivos y
quedo con el **criterio de regeneracion escrito al lado**, para que la proxima vez se rehaga
corriendolo en vez de confiar en que alguien lo actualizo.

Resultado del barrido (~35 metodos clasificados): **A** = tiene guarda, **B** = abierto, **C** = no
aplica (escritor de bajo nivel sin `SaveChanges` propio — contrato del caller —, o reversion con
lock propio sobre una fila existente).

**DOS ESCRITORES SIN GUARDA QUE QA NO REPORTO. No se arreglaron en este lote** (eran alcance nuevo
sobre un lote de garantia) y quedan declarados en el bloque:

1. `CajaMovimientoService.RegistrarMovimientoManualAsync` — **gemelo exacto de
   `GastoService.CrearAsync`**: toma el candado del periodo (exclusion real) y despues **no decide
   nada bajo ese lock**. Un doble submit mete dos ajustes de caja del mismo importe, motivo y dia. El
   serializador ya esta puesto; falta la consulta. Clave natural: (dia, tipo, monto, medio de pago,
   motivo).
2. `ProveedorService.EditarAsync` — abre transaccion y **no toma ningun lock**.
   `saldoInicialAnterior` sale de una lectura previa al `BeginTransactionAsync` y
   `RevertirAperturaAsync` decide sobre `ObtenerNetoVivoAsync` sin exclusion: dos ediciones
   concurrentes postean las dos contramovimiento + apertura nueva y el saldo del proveedor queda
   corrido. Es `LP-018` en su forma original (*"el neto vivo protege la repeticion SECUENCIAL, no la
   CONCURRENTE"*) trasladado a la CC de proveedores. `BloqueoDeFila.Proveedores` ya existe desde
   `LP-093`.

**Categoria nueva, "A con residual"**: el tope esta bien releido bajo lock pero **no hay
idempotencia**, asi que un doble submit **parcial** queda por debajo del tope las dos veces y
duplica. Son `DevolucionService.RegistrarAsync`, `FacturacionParcialService.EmitirAsync` y
`NotaCreditoService.EmitirAsync`. Merece categoria propia porque el tope **da la impresion** de
cubrirlo, y por eso es el residual que mas facil se pasa por alto.

**Y uno que esta bien por accidente**: `ProveedorService.CrearAsync` no duplica porque los indices
unicos `UX_Proveedores_Nombre_Vivo` / `_CUIT_Vivo` rechazan el segundo INSERT. Funciona, pero **la
dependencia no esta declarada en el call site**: si alguien relaja uno de esos indices, el sitio pasa
a duplicar sin que su codigo haya cambiado.

**Sin tocar, resuelven bien con otros mecanismos** (QA los midio PASS): aumento masivo de precios
(`UpdatedAt > PreviewGeneradoEn`) y ajuste de stock (`StockEsperado`). No hay un unico mecanismo
correcto para la familia: hay tres, y lo que importa es que cada sitio tenga uno.

### Evidencia

**Migraciones: NINGUNA.** Los seis fixes son de codigo. No hace falta indice unico: las claves
naturales incluyen texto libre y se evaluan bajo lock, asi que el indice no aportaria exclusion que
el lock no de ya — y uno sobre `Descripcion` seria un cambio de esquema sobre tablas de ledger con
produccion 12 migraciones atras. **La cola de pendientes de produccion sigue en 12.**

**Build de la solucion, no incremental: 0 errores / 9 advertencias**, linea base exacta. **Y el
numero por si solo no alcanza**: lo que se compara son **los codigos** — los unicos presentes son
`NU1902` (MailKit/MimeKit) y `CS0114` (`HomeController.cs:38`), los dos preexistentes. Un build
incremental da **8** porque el proyecto `Web` no se recompila y su `CS0114` no se vuelve a emitir; y
el total tambien puede dar 8 por como MSBuild deduplica las advertencias de paquete entre el nivel
`.slnx` y el nivel proyecto. **El total miente, los codigos no.**

**Arnes nuevo `tools/ArnesLote1Guardas`: 34 OK / 0 FALLADAS**, exit 0, contra un clon desechable
`laplatense_lote1` (22 migraciones, 46 tablas, armado con `dotnet ef database update`, **nunca con
`mysqldump --no-data`**, que es `LP-054`). Falla cerrado: sin `ConnectionStrings__DefaultConnection`
aborta con exit 2, y aborta igual si la cadena menciona dev/qa/produccion. El nombre de la base
evita a proposito el prefijo `laplatense_qa`, que dispara la guarda por substring (`LP-091`).

**11 mutantes, los 11 compilaron y corrieron. Union de tumbadas = 28 afirmaciones; conjunto
`[DISCRIMINA]` = 28; EL MISMO CONJUNTO, con CERO `[COBERTURA]` caida.** Seis de los once son de la
**direccion opuesta** (clave demasiado amplia, tope demasiado estricto, lock de menos): los que
prueban que el fix no rompio el pasado, y los que dieron dos de los tres hallazgos propios.

**Dos marcas mias estaban mal, en la direccion de SUBdeclarar**: `1c.2` y `2c.3` estaban
`[COBERTURA]` y los mutantes las tumbaron, asi que subieron a `[DISCRIMINA]`. Subdeclarar va para el
lado seguro, pero deja al proximo lector sin saber cual afirmacion defender.

**Integridad del codigo despues de mutar: verificada con `md5sum`** contra un backup previo — los 4
Services quedaron identicos al pre-mutacion. Los mutantes se revierten **desde el backup, nunca con
`git checkout`**, que volveria a HEAD y borraria el fix de la ronda.

**`LP-106` NO ESTA MEDIDO por el arnes, y no esta en verde: esta SIN MEDIR.** Necesita el pipeline de
autenticacion, una cookie emitida y dos requests separadas por mas que el `ValidationInterval` —
nada de eso existe en un host de consola, y un arnes que lo "simulara" llamando al Service estaria
midiendo otra cosa. El arnes lo imprime explicitamente al final, porque un lote de 6 defectos con un
arnes de 5 invita a leer el verde como si cubriera los 6.

### Pruebas minimas para QA

1. **`LP-088`** — 3 POST paralelos de $300.000 con **nota distinta** sobre una compra de $400.000: 1
   aceptado, 2 rechazados nombrando el saldo. Con nota **igual** el resultado correcto es 1 pago y
   **3 exitos** (ver el hallazgo 2). Negativo: dos pagos que juntos no exceden siguen entrando.
2. **`LP-095`** — 3 POST identicos: 1 pago / 1 egreso / 1 mov de CC, los tres con exito y el 2.º y
   3.º diciendo *"ya estaba registrado"*. Negativo: nota cambiada crea el segundo.
3. **`LP-095` extra (no estaba en el parte)** — doble submit del **saldo completo**: el 2.º tiene
   que salir por idempotencia, **no** por el tope.
4. **`LP-064`** — 2 POST identicos: 1 `Gasto` + 1 `CajaMovimiento`, el 2.º devuelve el Id del 1.º.
   Negativo: descripcion distinta entra.
5. **`LP-082`** — 2 POST identicos del adelanto: 1 mov + 1 egreso, el 2.º devuelve el Id del 1.º.
   Negativo: motivo cambiado entra. **Probar tambien el devengamiento** (no mueve caja), que no
   estaba en el parte y tambien lleva la guarda.
6. **`LP-093`** — 2 en serie **y** 3 en paralelo: 1 fila en los dos casos. Negativo: motivo cambiado.
7. **`LP-106`** — bloquear al usuario, esperar mas que el `ValidationInterval`, `POST
   /Clientes/Create` con la cookie vieja: 302 a Login y **ninguna fila**. Un usuario no bloqueado
   sigue trabajando. **El cambio de password sigue rotando el stamp** (es lo que el chaineo podria
   romper). Y probar que **borrar** un usuario tambien revoca.
8. **Regresion de los dos que no se tocaron**: aumento masivo (2.º y 3.er envio aplican 0 productos)
   y ajuste de stock (`StockEsperado`).

### Checklist de merge

- [x] Build de la solucion no incremental: 0 errores, 9 advertencias, **mismos codigos** que la linea base
- [x] Arnes del lote: 34 OK / 0 FALLADAS, exit 0
- [x] Corrida mutante: union de tumbadas == conjunto `[DISCRIMINA]`, cero `[COBERTURA]` caida
- [x] `md5sum` de los 4 Services == pre-mutacion
- [x] Cero migraciones nuevas (cola de produccion sigue en 12)
- [x] `appsettings.json`, bloque `Seed` y `SeedData.cs` **sin tocar** (`LP-108`, riesgo aceptado)
- [x] Bloque `MISMA FORMA` regenerado **con su criterio de regeneracion**
- [ ] **Re-verificacion de QA en contexto nuevo** — los 6 defectos quedan *aplicados, pendientes de re-verificacion*
- [ ] Sin push ni deploy (produccion no se toco)

## Barrido de `Activo` (familia LP-047) + migraciones pendientes a `laplatense_dev` (2026-10-07)

Archivado el 2026-10-07 en
[`historial/5-implementador-barrido-activo.md`](historial/5-implementador-barrido-activo.md).
Se movio para dejar lugar a la entrada del lote 2 de la Entrega 5 (devoluciones) sin cruzar el
techo de 150 KB. Ronda cerrada: la guarda de catalogo dado de baja en Marca/Modelo/Categoria, la
asimetria de `OrdenCompraService:653` y su combo de Editar, y las 4 migraciones aplicadas a
`laplatense_dev`. **La pasada 7 del barrido LP-002 (¿la guarda del Service es ALCANZABLE por la
UI?) nacio ahi** y se lee solo si el trabajo toca alguna de esas cosas.


## Bloques archivados (2026-10-07)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB
(`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **Lote de cierre: guarda de `MigracionCatalogo` + `LP-044`/`LP-045` reabiertos + `LP-049`** (2026-10-07)
  -> [`5-implementador-lote-cierre-lp049.md`](historial/5-implementador-lote-cierre-lp049.md)


## Historial archivado (2026-08)

El cierre de la Entrega 2, los items de app de la Etapa 3 (migracion de catalogo) y el armado
de la rama de produccion `entrega-1-migracion` se movieron a
`historial/5-implementador-2026-08-etapa3-y-entrega2.md` el 2026-10-06 (techo de 150 KB).
Son sprints cerrados y deployados: leerlos solo si hace falta el detalle de esa etapa.

## Hotfix de transacciones de ventas - rama `hotfix-transacciones-ventas` (2026-10-06)

Movido a [`historial/5-implementador-hotfix-transacciones.md`](historial/5-implementador-hotfix-transacciones.md) el 2026-10-06 (eran 26 KB) para mantener este
archivo bajo el techo de 150 KB. **Se lee solo si el trabajo toca la rama publicada o un deploy a
produccion.** Lo que hay que saber sin abrirlo:

- La rama existe, tiene **dos commits locales** (`c5b27a4` y `7ca5ce3`), **nunca se pusheo ni se
  deployo**, y refleja el estado exacto de produccion mas `PAT-059` en **cinco** metodos.
- **`entrega-1-migracion` ya la reconcilio** (commit `a72e3cd`): la version de desarrollo es la que
  manda y es un superconjunto. La rama publicada **no se toco** desde entonces.
- Nada de lo que se arreglo despues de `a72e3cd` -incluidos `LP-035`, `LP-036`, `LP-037` y
  `LP-038`- esta en esa rama. **Si alguna vez se deploya el hotfix solo, se deploya con esos
  cuatro defectos adentro.**

## Reconciliacion de la familia LP-018 / LP-034 en `entrega-1-migracion` (2026-10-06)

Movido a [`historial/5-implementador-reconciliacion-lp018-lp034.md`](historial/5-implementador-reconciliacion-lp018-lp034.md) el 2026-10-06 (eran 12 KB) para mantener
este archivo bajo el techo de 150 KB. **Ronda cerrada:** `LP-034` cerrado, los once sitios de la
familia reconciliados, `ArnesReconciliacionTx` en **153 OK / 0** (reverificado el 2026-10-06 al
cerrar CR-01/CR-02, sin regresion). **Se lee solo si hace falta el detalle de esa reconciliacion** —
el patron en si vive en el XML-doc de `BloqueoDeFila`/`RelecturaBajoLock` y en `PAT-059`, que son la
fuente de verdad.

## Verificacion por ejecucion de los 6 sitios restantes de la familia de atomicidad (2026-10-06)

Archivado el 2026-10-07 en
[`historial/5-implementador-verificacion-6-sitios.md`](historial/5-implementador-verificacion-6-sitios.md)
(12 KB). Se movio para dejar lugar a la entrada del barrido de `Activo` sin cruzar el techo de
150 KB: el archivo estaba en 146 KB. Se lee solo si el trabajo toca la familia de atomicidad.

## Historial de ajustes

### Bloques archivados (2026-10-08)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-10** — 2 bloques (2026-10-07 a 2026-10-07) → [`5-implementador-2026-10-3.md`](historial/5-implementador-2026-10-3.md)


### Bloques archivados (2026-10-08)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-10** — 2 bloques (2026-10-07 a 2026-10-07) → [`5-implementador-2026-10-2.md`](historial/5-implementador-2026-10-2.md)


Archivado el 2026-10-07 en
[`historial/5-implementador-historial-de-ajustes.md`](historial/5-implementador-historial-de-ajustes.md)
(52 KB). Se movio para dejar lugar a la entrada de CR-05/CR-03 sin cruzar el techo de 150 KB:
el archivo estaba en 142 KB. Se lee solo si el trabajo toca alguno de esos ajustes.

## LP-050 — ensayo del deploy sobre una COPIA de produccion (2026-10-07)

**No es una implementacion: es un ensayo de migracion. Cero lineas de codigo de negocio, cero
commits, cero migraciones nuevas. PRODUCCION NO SE TOCO** — verificado al final por consulta:
sigue en **8 migraciones**, ultima `20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`,
29 tablas, y **0 de las 4 columnas nuevas de `CajaMovimientos`** (`MedioPago`, `EsReversion`,
`PagoVentaId`, `UsuarioId`). `laplatense_dev` tampoco se toco (sigue en 18 migraciones, 9
`CajaMovimientos`), asi que el control se preserva.

### Estado real de produccion — el dato que QA habia dejado BLOCKED

Medido por `SELECT` directo contra `db_a7251f_laplaten` (host `mysql8001.site4now.net`,
MySQL **8.0.39**) y re-confirmado contra la copia:

| | |
|---|---|
| Migraciones aplicadas | **8** (exactamente las 8 primeras del repo, en orden) |
| Migraciones pendientes | **10** (de `LedgerCaja_Identidad_MedioPago_AnulacionVenta` a `CR04_PlanDeEcheqs`) |
| Tablas | 29 |

Conteos **exactos** (`COUNT(*)`, no `TABLE_ROWS`): Productos **112.485**, Clientes **2.990**,
CodigosProveedorProducto **110.683**, CodigosBarrasProducto **8.276**, Proveedores **85**, Marcas
**128**, Categorias **16**, RecargosCuota **7**, AspNetUsers **3**, Modelos **1**,
**CajaMovimientos 1**, **Gastos 1**, y **0** en Ventas, ItemsVenta, PagosVenta,
MovimientosCCCliente, Entregas, AjustesStock, CierresCajaDiarios y CierresCajaMensuales.

**La suposicion "las 8 primeras" era correcta y ahora esta medida.** Pero:

> **UNA PREMISA DEL BRIEF ERA FALSA Y CAMBIA EL TAMANO DEL RIESGO.** El brief afirmaba que
> produccion tiene **"5 ventas y 4 movimientos de caja reales"**. Produccion tiene **0 ventas y 1
> movimiento de caja**. Es otra vez un numero heredado de un reporte anterior citado como hecho sin
> medirlo. Aca el error era en la direccion benigna (el riesgo era 4x mas chico de lo declarado),
> pero el metodo que lo produjo es el mismo que en v27 produjo "19 migraciones" y "4 filas ZZ%".

**Trampa de medicion que hay que retener:** `information_schema.TABLES.TABLE_ROWS` es un **estimado**
en InnoDB y aca mintio de forma verificable — dio **6** para `__efmigrationshistory`, que tiene **8**
filas, y **0** para `cajamovimientos`, que tiene **1**. Si el estado de produccion se hubiera
reportado con esa consulta, el conteo de migraciones habria salido mal. Todo conteo va con `COUNT(*)`.

### Desvio de procedimiento: el backup del panel no se pudo bajar, y se hizo algo mejor

El paso 1 del brief (bajar `/db/db_a7251f_laplaten.sql` por FTP) **no se pudo ejecutar: el FTP
rechaza la credencial** (`530 User cannot log in.` para `olvidatasoft-002`, probado con y sin TLS
explicito). El usuario root del plan existe y esta `Active` (`ftp_list_users`), asi que lo que falla
es la password de `credenciales.local.md` — **probablemente rotada**. Queda como pendiente operativo.

En vez de parar, se tomo el camino **estrictamente de lectura y mas verificable**: `mysqldump`
directo contra produccion. Es mejor evidencia que el backup del panel por tres razones: el archivo
se genera y se verifica en el mismo acto, se sabe con que flags salio, y el `-- Dump completed`
prueba que no quedo truncado (el del panel habria que auditarlo a ciegas).

- Dump: **33,7 MB**, **29 `CREATE TABLE`**, cierra con `-- Dump completed on 2026-10-07 9:40:01`.
- Flags: `--single-transaction --set-gtid-purged=OFF --no-tablespaces --column-statistics=0
  --routines --triggers --default-character-set=utf8mb4`.
- **Dato operativo:** el primer intento llevaba `--events` y **salio con exit 2** —
  `Access denied ... to database (1044)` sobre `show events`: el usuario de produccion no tiene ese
  privilegio. El archivo quedo **truncado en la seccion de events** (33.718.329 bytes, sin footer).
  Se repitio sin `--events` -> exit 0. **Un dump con exit distinto de 0 no se usa**, aunque el
  tamano parezca razonable: es exactamente la forma de un backup que parece completo y no lo esta.

### La copia: `laplatense_ensayo_prod`

Restaurada en el MySQL local (**8.0.29**, root), exit 0 sin una sola advertencia. Nombre elegido
para que **ninguna guarda la confunda con produccion ni con dev**. Fidelidad probada antes de tocarla:
**8 migraciones y los 16 conteos identicos a produccion**, uno por uno.

**Toda medicion de esta ronda declara contra que base se hizo**, porque el riesgo propio del ensayo
era medir la copia creyendo medir produccion. Antes de aplicar nada se corrio
`dotnet ef dbcontext info`, que imprimio `Database name: laplatense_ensayo_prod` / `Data source:
127.0.0.1` y `10 (Pending)` — o sea el destino se **leyo de EF**, no se asumio del entorno.

### Veredicto sobre LP-050: el backfill deja TODAS las filas bien clasificadas

**`SELECT COUNT(*), SUM(MedioPago IS NULL) FROM CajaMovimientos` sobre la copia migrada: 1 fila,
`MedioPago IS NULL` = 0.** El criterio de cierre de QA se cumple.

**Pero el motivo por el que se cumple es lo que importa, y no es el que el parte suponia.** El
`UPDATE` riesgoso —el que clasifica por `Descripcion LIKE '%(Efectivo)%'` con `ELSE NULL`— tiene
`WHERE OrigenTipo IN ('Venta','CobroCC')`, y produccion **no tiene ni una fila de esos dos tipos**.
**El backfill por parseo de texto toca CERO filas en produccion.** La unica fila que existe es de
`OrigenTipo = 'Gasto'` y la resuelve el paso 2, que **no lee texto**: deriva de `Gasto.FormaPago`,
un entero cargado por el usuario.

Traza de la unica fila, paso por paso (foto antes y despues en `backups/laplatense/`):

- Antes: `Id=1, Tipo=2 (Egreso), OrigenTipo='Gasto', OrigenId=1, Monto=1200000.00,
  Descripcion='Servicios - pago a sumar'`. `Gasto 1`: `FormaPago=2 (Transferencia)`, `Anulado=0`.
- Paso 1 (`EsReversion=1 WHERE OrigenTipo='Gasto' AND Tipo=1`): **no la toca**, y corresponde —
  `Tipo=2` es el egreso del alta del gasto, no la reversion de su anulacion. Quedo `EsReversion=0`.
- Paso 2 (`JOIN Gastos`, `CASE FormaPago WHEN 2 THEN 4`): **`MedioPago = 4` (Transferencia)**. Correcto.
- Paso 3 (el del `LIKE`): 0 filas en alcance.
- Paso 4 (`PagoVentaId` por `JOIN PagosVenta ... n = 1`): 0 filas (`OrigenTipo='Venta'` no existe).
  Quedo `PagoVentaId=NULL`, que es lo correcto: la fila no viene de una venta.
- Pasos 5 y 6 (`UsuarioId` desde `Ventas.VendedorId` / `MovimientosCCCliente.UsuarioId`): 0 filas.
  Quedo `UsuarioId=NULL` — el dato honesto que el XML-doc de la migracion ya declaraba para gastos.

**El segundo `UPDATE` que depende del primero** (paso 4, que exige `MedioPago IS NOT NULL`) hizo lo
que corresponde: no tenia filas en alcance, y no las tenia por ausencia de ventas, no por un
`MedioPago` que el paso 3 hubiera dejado en `NULL`. **Esa era la cadena que el parte marcaba como
riesgo y en produccion no tiene superficie.**

### Los otros backfills de la ronda

- `UPDATE Proveedores SET Moneda = 1 WHERE Moneda = 0`: **85 filas**, y despues
  `GROUP BY Moneda` da **una sola fila: `1` con 85**. Sin esto los 85 proveedores quedaban en `0`,
  que no es ningun valor del enum (`MonedaProveedor.Peso = 1`).
- Los dos `UPDATE OrdenesCompra` (`Moneda`, `TotalEnPesos`): **0 filas, la tabla esta vacia**. No-op.
- La verificacion que el comentario de `RecepcionMercaderiaYPagosProveedor` pedia correr en vez de
  confiar en el razonamiento: `SELECT PrecioVentaDesactualizado, COUNT(*) FROM Productos GROUP BY 1`
  devuelve **UNA fila: `0` con 112.485**. Como el comentario predecia.

### Ninguna fila preexistente cambio de valor — probado, no razonado

`CHECKSUM TABLE` **no sirve** para esto: las columnas nuevas le cambian el valor aunque ningun dato
viejo se haya movido. Lo que se hizo: pedirle a **produccion** su lista de columnas (que es el estado
pre-migracion), generar con ella **una sola query identica** —`MD5` de los `MD5(CONCAT_WS(...))` de
**solo esas columnas**, mas `COUNT(*)`, por tabla— y correrla en las dos bases.

**`diff` de las dos salidas: vacio. Las 28 tablas con el mismo hash y el mismo conteo.** Es a la vez
la prueba de que no se perdio ninguna fila y de que ningun valor preexistente se toco. (El hash de
`proveedores` coincide justamente porque `Moneda` es columna **nueva** y no entra: el backfill la
poblo sin tocar nada de lo que ya estaba.)

### Tiempo sobre volumen real: NO hace falta ventana de servicio

`dotnet ef database update` sobre la copia con los **112.485 productos** y **110.683** codigos de
proveedor: **14 segundos end-to-end** (09:41:48 -> 09:42:02), exit 0, `Done.`, 8 -> **18**
migraciones. De esos 14 s una parte es el bootstrap del host de EF (el `HostAbortedException` del
log es el comportamiento normal de design-time, no un error).

**Caveat honesto, declarado y no omitido:** son 14 s en un MySQL **local**. El MySQL de produccion es
compartido y esta del otro lado de la red. Lo que sostiene la conclusion no es el numero sino la
**forma** de las operaciones: las migraciones son aditivas (`AddColumn` / `CreateTable` /
`CreateIndex`), que en MySQL 8 son `INSTANT`/`INPLACE`, y los `UPDATE` de backfill tocan **85 filas
en total** (los 85 proveedores) **mas 1** (el movimiento de caja) — el volumen de 112.485 productos
**no entra en ningun `UPDATE`**. Margen de sobra incluso con un factor 10x.

### Medicion extra: el `LIKE` del paso 3 SI matchea el formato que el Service escribe

Es la pregunta que el ensayo sobre produccion **no puede** contestar (0 filas en alcance), asi que se
midio por lectura en `laplatense_dev` (solo `SELECT`, no se escribio nada). Los movimientos de venta
que `VentaWorkflowService.ConfirmarAsync` genero tienen `Descripcion` = `Venta #12 (Efectivo)`,
`Venta #12 (CreditoCuotas)`, `Venta #13 (Efectivo)` — **los tres matchean** su patron y derivarian
`1`, `3` y `1`. El sufijo lo pone el `ToString()` del enum, como el XML-doc afirmaba. **El
mecanismo del backfill es sano; lo que no se probo en produccion es porque alli no hay sustrato.**

Lo que ese mismo barrido mostro de paso: `OrigenTipo = 'Ajuste'` **no esta en el `WHERE` de ningun
paso** del backfill y en dev tiene `MedioPago NULL`. **No es un defecto del backfill**: esa fila la
creo el codigo actual *despues* de migrar y tambien la dejo en `NULL`, o sea el ajuste manual sin
medio de pago es una decision del dominio, no una fila que el backfill se perdio. En produccion no
hay ajustes, asi que no tiene efecto en este deploy. Queda anotado.

### Que queda para decidir el deploy

- **No hace falta ningun `UPDATE` correctivo ni migracion extra.** Era el entregable condicional del
  brief y **no se activa**: no quedo una sola fila en `NULL`.
- **El riesgo de `LP-050` en el deploy de hoy es nulo por ausencia de datos**, no por un backfill
  verificado sobre los datos que lo ejercitan. La diferencia es operativa: **si se deploya ahora, el
  parseo de texto nunca corre**. Si produccion empezara a operar ventas **antes** del deploy, el
  paso 3 pasaria a tener superficie real y este ensayo habria que repetirlo sobre la copia nueva.
  **Ese es el argumento para deployar pronto**, y es el unico que este ensayo habilita.
- El `Down` sigue sin revertir ningun backfill (lo que `LP-050` senalaba). **No cambia el veredicto
  porque el `Down` no es el plan de rollback**: el plan es restaurar
  `laplatense_PROD_2026-10-07_pre-migracion-18.sql`, que es lo que de verdad vuelve atras.
- **Pendiente operativo nuevo:** la password de FTP/Web Deploy de `credenciales.local.md` no
  autentica. **Hay que resolverlo ANTES del deploy del sitio** — Web Deploy usa esa misma credencial.

### Donde quedo todo

- Snapshot de produccion (pre-migracion-18):
  `C:/Sistemas/backups/laplatense/laplatense_PROD_2026-10-07_pre-migracion-18.sql` (33,7 MB).
  **Es el plan de rollback del deploy.**
- Evidencia: `C:/Sistemas/backups/laplatense/ensayo-lp050_*` — fotos antes/despues de
  `CajaMovimientos`, `Gastos`, los dos checksums comparados y el log de `ef database update`.
- Copia viva: base local **`laplatense_ensayo_prod`**, ya en 18 migraciones. Descartable: se puede
  borrar con `DROP DATABASE`, el snapshot la reconstruye.

### Lo que NO entro

Deploy a produccion (lo autoriza Joaquin aparte), cualquier escritura sobre produccion o sobre
`laplatense_dev`, `tools/MigracionCatalogo` y los arneses contra la copia, codigo de negocio,
`LP-051` (trivial, el comentario redundante) y Entrega 5.

**`LP-050` queda APLICADO, PENDIENTE DE RE-VERIFICACION.** El cierre lo declara QA en contexto nuevo.
