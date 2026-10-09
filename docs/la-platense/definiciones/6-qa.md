# Memoria - QA

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-10-09 (v27 - **FASE 1 DEL TOKEN CERRADA Y COMMITEADA (`46da1c2`): QA la declara CERRABLE, 7 PASS y 1 parcial.** `LP-125`, `LP-126`, `LP-127` y `LP-128` **CERRADOS**. **El criterio que decidia paso, medido como correspondia:** navegador real, misma sesion, misma URL, los mismos bytes de negocio congelados, cambiando solo el token -- el propio del form **emite**, el **fresco** del form de logout se **rechaza antes de reservar** con cero filas en `SubmitsProcesados`. **No es `M21`: la pantalla no rechaza todo.** **El gate dejo de ser una lista disfrazada y se probo agregandole trabajo nuevo:** QA creo una entidad de dominio con un `decimal` mas un POST que la escribe, **sin declararla en ninguna parte, y el detector la encontro y fallo**; la guarda de derivacion en 0 **aborta con exit 2** ante una mutacion semanticamente nula que compila. **El hallazgo mas caro es de deploy: `LP-133` `major`** -- la huella se calcula de **dos fuentes distintas** (el `action` del form y `Request.Path`), y con `UsePathBase` (la forma de sub-aplicacion de IIS) difieren y **el formulario posteado con SU PROPIO token se rechaza**, silencioso porque falla cerrado, y ni los arneses ni el verificador lo ven porque corren sin PathBase. **Verificado por el orquestador: hoy NO aplica** -- el codigo no usa `UsePathBase` y el sitio va a la raiz de su dominio, no a una carpeta virtual; queda como **condicion de deploy**. **Dos clasificaciones que corrigen un instinto:** `AumentoMasivoPrecios/Aplicar` **es idempotente por construccion** (la huella de los precios de 112.486 productos queda identica, con el control que prueba que la primera corrida si los cambio), y lo que duplica es **la fila de auditoria** (`LP-132`); y en el segundo cierre de caja los perdedores leen un mensaje **en castellano limpio, sin texto crudo de EF**, asi que `LP-116` **no reaparece**. `Presupuestos/ConvertirAVenta`, el de mayor impacto aparente del grupo sin evaluar, **esta protegido** en serie y en paralelo. **Quedan abiertos del gate `LP-129` y `LP-130`** (la clave de escritores sale del **nombre del archivo**, y un POST que escribe desde el Controller nunca entra al perimetro): **ninguno tiene instancia viva, asi que no bloquean el merge -- si bloquean apoyarse en el gate para dar la fase 2 por enumerada**, que es su unico proposito. **El patron entro al catalogo del estudio como `PAT-065`**, recien ahora que hay codigo entregado y medido, con su `cuando_no_usar` y la verificacion de que **el token no es una credencial** (huella fabricada a mano: no compra nada, los topes y los locks siguen corriendo). Catalogo de regresiones: 249 -> **254**. Cola de produccion: **13 pendientes**.)
## Anterior: 2026-10-09 (v26 - **FASE 1 DEL TOKEN DE SUBMIT: el mecanismo FUNCIONA y es mergeable; el GATE DE LA FASE 2 no es confiable.** **El criterio que no se podia falsear PASO:** `ArnesNotaCredito` volvio de 62/1 a **63/0 con `git diff -- tools/ArnesNotaCredito` vacio** -- se puso verde **solo** al retirar la clave natural, y QA lo re-midio en dos pasadas. Ese fixture era el unico testigo honesto: escrito antes del problema, para otra familia, con sus dos tandas en menos de un segundo, y era el caso que **ninguna ventana podia satisfacer**. **El par discriminante que prueba que el problema se resolvio y no se movio: mismos bytes de negocio, solo cambia el token -> EMITEN LOS DOS.** El consumo **es** el `INSERT` sobre la PK del token: atomico, cubre serie y concurrencia **sin ventana de lectura**, que era el agujero estructural de `PAT-059`. **Los locks de `PAT-059` no se tocaron y ahora estan medidos** (el mutante que le saca el lock a `EmitirAsync` tira 3 comprobantes y 3.000 facturado sobre 2.000 vendidas). **El modo de falla que mas preocupaba se midio por NAVEGADOR real** (Chromium, SweetAlert2, doble clic) porque **el filtro falla cerrado** y si el token no llegara la pantalla rechazaria TODA emision -- una caida total, peor que el defecto, y ningun arnes la cubre: **la pantalla NO esta muerta**, delta exactamente 1 con el mismo token, y 2 y 3 al recargar. **Pero los dos `major` que QA encontro son del INSTRUMENTO y bloquean la fase 2:** `LP-127` -- el verificador de perimetro enumera por **lista a mano de 7 entidades y una sola forma**, asi que un `new CierreCajaDiario` y una escritura por **SQL crudo** **no los detecta, exit 0** (es la forma del bloque `MISMA FORMA` aplicada al instrumento que debia protegernos de eso); y `LP-126` -- el chequeo del cableado esta **inerte en un build normal y aun asi imprime que esta bien**, un verde falso en el unico chequeo del modo de falla total. Mas `LP-125` `minor` (un token **fresco** del form de logout posteado a `Emitir` **emite**: `RutaAccion` solo rechaza post-consumo, y el XML-doc afirma lo contrario) y `LP-128` `minor` (de las 15 afirmaciones retiradas, 14 bien y **la vieja 9.10 perdio cobertura**). **El perimetro real son 28 POST que escriben plata, no 23**: faltaban `Caja/CerrarDia` y `Caja/CerrarMes` (no crean `CajaMovimiento`, por eso el detector no los veia), `AumentoMasivoPrecios/Aplicar`, `Presupuestos/ConvertirAVenta` y `Ventas/GuardarBorrador` -- **y 13 sitios siguen declarados SIN EVALUAR**. **Correccion medida al orden de riesgo:** `Ventas/Facturar` es el **menos** urgente, no el mas (deriva sus lineas del pendiente), `Gastos/Anular` esta protegido a proposito y `CCEmpleado/Revertir` tiene una clave natural **buena**. **Dos hallazgos de metodo:** una **renumeracion vuelve inauditable una retirada** (QA tuvo que auditar por texto porque `9.3`-`9.7` y `9.9` existen en las dos versiones con sentidos distintos), y **la trampa del `copy2`** -- restaurar un mutante preservando el mtime deja el mutante vivo en la DLL con el `md5` del fuente en verde, la unica falla que el control recomendado NO atrapa, **ya subida a la instruccion 33 del estudio**. Primera migracion de toda la ronda: la cola de produccion pasa de 12 a **13**. **Y el script de saneamiento NO hace falta**, verificado contra produccion en lectura: prod tiene **0 ventas, 29 tablas y la tabla `ComprobantesAfip` NO EXISTE** -- el riesgo no pudo materializarse; lo que queda es una **condicion de orden de deploy**. Catalogo: 245 -> **249** items.)
## Ultima validacion de reglas cross-proyecto: 2026-10-08

---

# Fase 1 del token de submit — el mecanismo estructural de idempotencia, aplicado a un solo sitio (2026-10-09, rama `entrega-1-migracion`, sin commitear)

## **El mecanismo FUNCIONA y la fase 1 es mergeable. El GATE de la fase 2 no es confiable todavía, y eso es lo que hay que arreglar antes de seguir.** El criterio que no se podía falsear **pasó**: `ArnesNotaCredito` volvió de 62/1 a **63/0 con `git diff -- tools/ArnesNotaCredito` vacío** — se puso verde **solo**, al retirar la clave natural del Service, y QA lo re-midió de forma independiente en dos pasadas. Ese fixture es el único testigo honesto que teníamos: escrito antes del problema, para otra familia, con sus dos tandas legítimas en menos de un segundo, y era el caso que **ninguna ventana podía satisfacer** (§0-quater de la arquitectura). **Que se ponga verde sin tocarlo es la prueba de que el token resuelve el problema en vez de moverlo.** Pero la re-verificación encontró que **el verificador de cobertura —el instrumento que debía impedir que la fase 2 se olvide un sitio— pasa en verde ante dos formas de escritura que el repo ya usa**, y que el **perímetro real son 28 POST, no 23**.

## El mecanismo, y las decisiones que lo hacen distinto de una clave natural

`SubmitsProcesados` con la **PK sobre el token**, así que **el consumo *es* el `INSERT`**: atómico en el motor, cubre serie y concurrencia **sin ventana de lectura** — que era el agujero estructural de `PAT-059`. `INSERT IGNORE` decidido por filas afectadas, en **conexión aparte**, con una razón que vale retener: *"la reserva tiene que ser visible en el acto, y un `SaveChanges` desde el mecanismo de idempotencia arrastraría lo que el Service de negocio tenga trackeado"*. `IRegistroDeSubmit` en Application, filtro y tag helper en Web — **las dos primeras convenciones de ese tipo en el proyecto**, porque no había ninguna.

**Los locks de `PAT-059` no se tocaron, y ahora están medidos**, que es lo que la decisión de arquitectura pedía explícitamente (*"quitar un lock al poner el token sería la peor lectura posible"*): el mutante que le saca el lock a `EmitirAsync` tumba una afirmación con **3 comprobantes y 3.000 facturado sobre 2.000 vendidas**.

## Lo que QA midió, criterio por criterio

| # | Criterio | Veredicto |
|---|---|---|
| 1 | **Facturación parcial por navegador**, el modo de falla total | **PASS** |
| 2 | `ArnesNotaCredito` re-medido por QA | **PASS** (63/0, `git diff` vacío) |
| 3 | Los tres controles con par discriminante | **PASS** |
| 4 | Auditoría de las 15 afirmaciones retiradas | **FAIL en 1 de 15** → `LP-128` |
| 5 | Perímetro real de POST que escriben plata | **FAIL**: son **28**, no 23 |
| 6 | ¿El verificador protege contra el olvido? | **FAIL en lo que importa** → `LP-126`, `LP-127` |
| 7 | Migración aditiva | **PASS** (cola de prod: 12 → **13**) |
| 8 | No-regresión de los 10 cerrados | **PASS**, 6 líneas base verdes |
| 9 | Retención de tokens | **PASS** |

**El criterio 1 era el que más preocupaba y se midió como correspondía: con Chromium real, SweetAlert2 real y doble clic real**, no por HTTP. Importaba porque **el filtro falla cerrado**: si el token no llegara al formulario, la pantalla rechazaría **toda** emisión — una caída total de la función, peor que el defecto original, y **ningún arnés la cubre**. Resultado: 1 de 3 unidades emite correctamente, 2 POST paralelos más 1 en serie con el mismo token dan **delta exactamente 1**, recargar (token nuevo) y emitir da 2 y después 3 hasta igualar lo vendido, y un POST sin token da 0 emisiones con cartel de rechazo. **La pantalla no está muerta.**

**El par discriminante del criterio 3 es el que prueba que el problema se resolvió y no se movió:** mismos bytes de negocio, **sólo cambia el token** → **emiten los dos**. Eso es exactamente lo que ninguna clave derivada del payload podía hacer.

## Los dos `major` son del instrumento, no del sistema — y es la distinción que decide qué sigue

- **`LP-127` `major` — el verificador de perímetro repite el error que esta ronda vino a corregir.** Enumera por **una lista a mano de 7 entidades y una sola forma de escritura**: un `new CierreCajaDiario` (entidad no listada) y una escritura **por SQL crudo** **no los detecta, exit 0**. Es la forma del bloque `MISMA FORMA, SIN TOCAR` —una lista a mano que envejece— aplicada al instrumento que debía protegernos precisamente de eso.
- **`LP-126` `major` — el chequeo del cableado está inerte en un build normal y aun así imprime *"el cableado del helper esta bien"***. Un verde falso en el único chequeo del modo de falla total.
- **`LP-125` `minor` — el token no nace atado a la acción.** Un token **fresco** del `<form>` de logout, posteado a `Emitir`, **emite**: `RutaAccion` sólo rechaza post-consumo. Y el XML-doc afirma lo contrario, que es la familia `LP-044`/`LP-045`/`LP-051` otra vez.
- **`LP-128` `minor`** — de las 15 retiradas, 14 están bien clasificadas y **la vieja `9.10` perdió cobertura**.

**Por qué esta distinción importa:** los dos `major` **no bloquean el merge de la fase 1** —el mecanismo está medido y funciona— **pero bloquean confiar en el verificador como gate de la fase 2**, que es el único trabajo que queda de esta familia. Arreglar el instrumento antes de tocar los 6 sitios restantes no es prolijidad: es la lección de `LP-114`/`LP-117`/`LP-121` aplicada.

## El perímetro: 28, y 13 sitios que nunca se evaluaron

El implementador declaró **23** POST que escriben plata (contra los 13 que la ronda conocía) y **13 de ellos como "SIN EVALUAR"**: sin parte de defecto y sin medición, nunca. QA enumeró de forma independiente y encontró **28**. Los 5 que faltaban: **`Caja/CerrarDia` y `Caja/CerrarMes`** —que crean `CierreCajaDiario`/`Mensual` con `Saldo`/`TotalIngresos`/`TotalEgresos` y **no** crean `CajaMovimiento`, que es exactamente por qué el detector no los veía—, `AumentoMasivoPrecios/Aplicar`, `Presupuestos/ConvertirAVenta` y `Ventas/GuardarBorrador`. **Ni cubiertos ni declarados.**

**Y una corrección al orden de riesgo, medida:** el implementador declaró `Ventas/Facturar` como *"el que más necesita el token"* y es **el menos urgente** de los cuatro de forma peligrosa conocida — deriva sus líneas del pendiente, así que el segundo submit no tiene nada que facturar (1 comprobante en serie y en paralelo). `Gastos/Anular` está protegido **a propósito** (lee `gasto.Anulado` dentro de la transacción, después del lock) y `CCEmpleado/Revertir` tiene una clave natural **buena**, porque usa la identidad del movimiento revertido y no un monto. `OrdenesCompra/RevertirPago` quedó BLOCKED por falta de órdenes en el clon.

## Dos hallazgos de método que valen para todo el estudio

1. **Una renumeración vuelve inauditable una retirada.** QA tuvo que auditar las 15 afirmaciones **por texto y no por id**, porque la renumeración dejó `9.3`–`9.7` y `9.9` existiendo en las dos versiones **con sentidos distintos**. Retirar afirmaciones con una explicación razonable es la forma más limpia de que la cobertura desaparezca sin que nadie lo note, y renumerar al mismo tiempo elimina la única forma barata de controlarlo.
2. **La trampa del `copy2`, que ya subió a la instrucción 33 del estudio.** Restaurar un archivo mutado con una copia que **preserva el mtime** hace que MSBuild no recompile: **el mutante sigue vivo en la DLL y el chequeo de `md5` del fuente pasa en verde**. Es la única falla de la ronda que el control de integridad recomendado **no detecta**, y es peor que las otras porque aparece al limpiar y contamina las mediciones **siguientes**. QA verificó que no afectó ninguna de las suyas, y **por una razón estructural y no por suerte**: su verificación es análisis estático sobre los `.cs`, sin DLL en el circuito. Lo que sí la mordió fue su propia versión: su primer mutante usó una convención de nombres que el verificador no pudo resolver, el POST quedó invisible, y estuvo **a un paso de publicar que el verificador no detecta el olvido ni en el caso fácil**.

## CIERRE DE LA FASE 1 — 2026-10-09, commit `46da1c2`: **QA la declara CERRABLE.** 7 PASS, 1 parcial

El pase que arregló el gate cerró los cuatro defectos que la re-verificación había abierto, y la verificación final midió lo único que nadie había podido medir.

- **`LP-125`, `LP-126`, `LP-127`, `LP-128`: CERRADOS**, cada uno con par discriminante.
- **El criterio que decidía, PASÓ y se midió como correspondía:** navegador real, **misma sesión, misma URL, la misma lista de bytes de negocio congelada**, cambiando sólo el token. Positivo (token propio del form) → emite, con su comprobante en la base. Negativo (token **fresco** del `<form>` de logout) → rechazado **antes de reservar**, con **cero filas** en `SubmitsProcesados`. **No es `M21`: la pantalla no rechaza todo.** El doble clic real por pantalla también entra una sola vez: 3 emisiones = 3 filas de token, y los dos rechazados no dejaron ninguna.
- **El gate dejó de ser una lista disfrazada, y se probó agregándole trabajo nuevo:** QA creó en su copia una entidad de dominio nueva con un `decimal` más un POST que la escribe, **sin declararla en ninguna parte**, y el detector **la encontró y falló**. El perímetro base re-medido de forma independiente coincide: **35 POST, 27 entidades, 1 cubierto + 34 declarados**. La guarda de derivación en 0 probada con una mutación **semánticamente nula** (`decimal` → `Decimal`, que compila): **aborta con exit 2**, no sale 0.
- **Las dos clasificaciones nuevas, verificadas, y las dos corrigen un instinto.** `AumentoMasivoPrecios/Aplicar` **es idempotente por construcción**: la huella de los precios de 112.486 productos es **idéntica** tras la segunda aplicación, con el control que prueba que la primera sí cambió precios (33.451 suben / 22.188 bajan); lo que duplica es **la fila de auditoría** (`LP-132` `minor`: el segundo aviso sale en **verde** diciendo "Se actualizaron 112.071 producto(s)" cuando su propio preview dice `suben=0 bajan=0`). Y en el **segundo cierre de caja**, con 4 sesiones independientes simultáneas, 1 gana y los 3 perdedores leen *"La caja de ese día ya fue cerrada."* — **castellano limpio, cero texto crudo de EF, cero 500: `LP-116` no reaparece**, y el índice nunca contesta porque lo ataja el candado de `LP-037` con relectura.
- **`Presupuestos/ConvertirAVenta`, el de mayor impacto aparente del grupo sin evaluar: está protegido.** En serie, 3 POST → 1 venta y los dos siguientes avisan con el número de la venta ya creada; en paralelo, 4 simultáneos → 1 gana y exactamente 1 venta apunta al presupuesto.

### El hallazgo más caro de la verificación final: `LP-133` `major`, y es de deploy

**La huella del token se calcula de DOS fuentes distintas** —el `action` del form por un lado y `Request.Path` por el otro— **y cualquier cosa que las haga diferir rompe todo en silencio, porque falla cerrado.** Medido: con `app.UsePathBase("/laplatense")`, que es la forma de sub-aplicación de IIS, el `action` lleva el prefijo y `Request.Path` no, y **el formulario posteado con SU PROPIO token se rechaza** (comprobantes 4→4, `SubmitsProcesados` 5→5). **Es `M21` disparado por el deploy**, y ni los arneses ni el verificador lo ven porque corren sin PathBase.

**Verificado por el orquestador contra la configuración real: hoy NO aplica.** El código **no usa `UsePathBase`** (QA lo agregó para provocar el caso) y el deploy apunta a `msdeploySite="olvidatasoft-002-site17"`, un sitio propio con `AllowedHosts` en el dominio raíz — **no una carpeta virtual**. Queda como **condición de deploy**: confirmar que el sitio va a la raíz de su dominio, o derivar las dos huellas de la misma fuente.

### Los dos `major` que quedan abiertos del gate, y por qué no bloquean el merge

- **`LP-129`** — la clave de escritores sale del **nombre del archivo**: dos clases de Service en un mismo archivo dejan el POST **invisible**. Latente hoy (el único caso real no escribe), y se vuelve visible con sólo partir una clase a su propio archivo, **sin tocar código**.
- **`LP-130`** — un POST que escribe la entidad **directo desde el Controller** nunca entra al perímetro, y ese límite **no estaba** en los "límites reales" declarados.
- **`LP-131` `minor`** — el encabezado "CÓMO MIDE" sigue describiendo los dos mecanismos ya retirados (la lista de 5 entidades y el "si existe el Razor generado"). Es la familia `LP-044`/`LP-045`/`LP-051`: un comentario que afirma algo falso sobre su propio archivo.

**Ninguno tiene instancia viva**, así que no bloquean el merge de la fase 1. **Sí bloquean apoyarse en el gate para dar la fase 2 por enumerada**, que es su único propósito.

### Estado final de la fase 1

**Mergeable y commiteada (`46da1c2`).** El patrón entró al catálogo del estudio como **`PAT-065`** —recién ahora, con código entregado, ruta real y medición— con sus seis decisiones, su `cuando_no_usar` (no sirve para un cliente que reenvía sin pedir el formulario, y **no es una credencial**: QA fabricó una huella a mano y verificó que **no compra nada**, porque los topes, el `UsuarioId` y los locks siguen corriendo detrás) y los dos modos de falla total que sólo aparecen midiendo.

**Lo que queda de esta familia:** la **fase 2** —los 6 sitios restantes y el retiro gradual de las claves naturales, cada retiro con su re-verificación— con `LP-129`/`LP-130` arreglados primero, porque son el gate. Más los **12 POST del grupo D que siguen sin evaluar**.

## Riesgos de liberación

1. **El gate de la fase 2 no es confiable** (`LP-126`, `LP-127`). Es lo único que bloquea seguir.
2. **13 sitios sin evaluar nunca**, y 5 recién descubiertos sin declarar — incluidos los dos cierres de caja, que escriben los totales del arqueo.
3. **Primera migración de toda la ronda**: la cola de producción pasa de 12 a **13 pendientes**.
4. **Condición de orden de deploy, verificada contra producción:** prod tiene **0 ventas, 29 tablas y la tabla `ComprobantesAfip` NO EXISTE** (llega con una de las pendientes). Así que el riesgo de la factura duplicada e irrecuperable **no pudo materializarse** y **no hace falta script de saneamiento**. Lo que sí hace falta: **no deployar las migraciones pendientes antes de que el token esté puesto y verificado**, porque traen la tabla y abren la ventana.

## Checklist de salida

- [x] El criterio que no se puede falsear: `ArnesNotaCredito` 63/0 **sin que nadie toque el arnés**, re-medido por QA
- [x] Facturación parcial por navegador real: la pantalla funciona y el filtro falla cerrado sin matarla
- [x] Par discriminante del mecanismo: mismo payload y distinto token **emiten los dos**
- [x] Locks de `PAT-059` intactos y ahora medidos
- [x] Migración aditiva reversible; 6 líneas base verdes con md5 de DLL verificados antes de correr
- [x] La trampa del `copy2` subida a la instrucción 33 del estudio
- [ ] **`LP-126` + `LP-127`: el gate de la fase 2, sin arreglar — bloquea la fase 2, no el merge de la fase 1**
- [ ] `LP-125` (token no atado a la acción en la emisión) y `LP-128` (cobertura perdida), sin arreglar
- [ ] Los 5 sitios nuevos sin declarar y los 13 sin evaluar: alcance a decidir
- [ ] Fase 2: los 6 sitios restantes y el retiro de las claves naturales, **cada retiro con su re-verificación**
- [ ] El patrón al catálogo del estudio, **recién cuando la fase 1 cierre** (no se publica un patrón sin código entregado)
---

# Lote 1 de fixes de la ronda — guardas transaccionales y revocación de acceso — 2 pases de implementación y 2 re-verificaciones independientes (2026-10-08, rama `entrega-1-migracion`, sin commitear)

## **9 defectos CERRADOS con par discriminante. Y la ronda NO se libera, porque hacer la enumeración bien destapó SIETE sitios más de la misma familia, uno `critical` y fiscal.** Los 6 del lote original (`LP-088` `critical`, `LP-106` `high`, `LP-095`, `LP-064`, `LP-082`, `LP-093`) cerraron, más los 3 que la re-verificación del pase 1 abrió (`LP-114`, `LP-115`, `LP-116`). **Pero el saldo de la familia de idempotencia empeoró, no mejoró**: arrancó con 6 sitios conocidos y hoy tiene **7 abiertos** (`LP-112`, `LP-113`, `LP-117`, `LP-118`, `LP-119`, `LP-120`, `LP-121`), y el peor es nuevo: **`LP-119` `critical` — un doble clic en facturación parcial emite DOS comprobantes AFIP, y el remedio (la nota de crédito) también duplica (`LP-120`).** La conclusión operativa de este lote no es "faltan 7 parches": es que **arreglar sitio por sitio ya produjo una regresión y dos huecos en el mecanismo nuevo**, y eso es un dato sobre el método, no sobre el cuidado de quien lo hizo.

## Cómo se corrió

Dos pases de implementación (el primero cortado por un límite de sesión de la API a mitad de escribir su arnés, retomado con su contexto intacto) y **dos re-verificaciones independientes**, en contextos limpios, con el contrato de la 30: el implementador describe, QA mide, **y ningún defecto lo cierra quien lo arregló**. Nada commiteado: los fixes viven en el working tree y las dos re-verificaciones los midieron ahí. **Cero migraciones en los dos pases** — la cola de producción sigue en 12 pendientes.

## Las 6 guardas del pase 1, con su costo declarado y su veredicto

| Defecto | Guarda | Costo declarado | Veredicto |
|---|---|---|---|
| `LP-088` `critical` | lock de `OrdenesCompra` + relectura de estado + **saldos releídos dentro de la transacción** | ninguno: cambió *cuándo* se lee, no qué se decide | **CERRADO** |
| `LP-095` `major` | clave natural **por línea y con multiplicidad** | dos líneas de pago legítimamente iguales **sin nota** colapsan | **CERRADO** |
| `LP-064` `major` | clave de 6 campos, **serializada por el candado del período** (un gasto no tiene dueño que bloquear) | dos fletes de $8.000 el mismo día con igual descripción | **CERRADO** |
| `LP-082` `major` | `BloquearUsuarioAsync` (nuevo, PK string) + clave natural, en los dos caminos | dos movimientos idénticos el mismo día | **CERRADO** |
| `LP-093` `major` | transacción (no tenía) + `BloquearAsync(Proveedores)` + clave natural | dos ajustes idénticos el mismo día | **CERRADO** |
| `LP-106` `high` | **las dos mitades**: rotar el stamp al togglear + chequear `Estado` en `OnValidatePrincipal`, **chaineado y no reemplazado** | una consulta por PK por request | **CERRADO** |

**`LP-106` es el que más importaba y se midió con el rigor que correspondía**, en las dos mitades por separado y aisladas: con el stamp rotado por SQL y `Estado=1`, a t=0 escribe y a t=330s da **302 a Login con 0 filas**; con `Estado=2` por SQL y el stamp intacto, **302 y 0 filas**, y al revertir `Estado=1` con la misma cookie vuelve a escribir — o sea que el rechazo lo causa `Estado` y nada más. El chaineo verificado: el cambio de password sigue rotando el stamp y matando la cookie vieja, así que **el `SecurityStampValidator` sigue vivo**. Y el control positivo: superusuario y víctima activa trabajan normal. **Con esto el sistema puede revocar un acceso, que antes no podía.** (Nota de honestidad del propio QA: su control de "antes escribía" dio 200 por `ModelState` y no probó la escritura en una de las corridas; lo declaró en vez de dejarlo pasar.)

## El escenario de `LP-088` se auto-invalidó, y conviene que quede escrito

Con `LP-095` arreglado, los "3 POST idénticos de $300.000" del parte original **son un doble submit**: la idempotencia los absorbe y los tres contestan éxito. **Medido: la letra del parte da `pagos=1` tanto con el código sano como sobre el mutante roto — no discrimina.** QA diseñó el escenario que sí discrimina (3 POST paralelos con **notas distintas**, 300k cada uno sobre una orden de 400k): entra **1 pago / 1 caja / 1 CC** y dos rechazos nombrando el saldo en castellano, con el control positivo de que 150k+150k **siguen entrando los dos**. Una guarda que rechaza todo también da "0 excesos", así que ese control no es opcional.

**Regla que sale de esto, y es nueva:** cuando se arregla más de un defecto sobre el mismo endpoint, **el criterio de re-verificación del segundo puede quedar invalidado por el fix del primero**. Un parte guarda un escenario, y un escenario envejece. Antes de correr la letra de un criterio viejo hay que preguntarse si todavía discrimina — y la forma de saberlo es correrlo **también sobre el mutante**: si da verde en los dos, no mide nada.

## `LP-114` — la regresión del propio fix, y la forma de baja que faltaba

**El pase 1 bloqueó el pago de un adelanto.** La secuencia **registrar → revertir → re-registrar el mismo día** quedaba rechazada, **con ícono de ÉXITO**, diciendo *"ya estaba registrado… Saldo actual: $ 0,00"*: el adelanto no entraba, **el empleado no cobraba**, y el operador leía verde y se iba.

**La causa es una asimetría de dominio que no se ve leyendo el código de un solo sitio.** En los otros tres la baja vive **en la fila vieja** (`Estado=Revertido` en pago, flag `Anulado` en gasto, soft delete en CC-cliente) y la clave natural sola alcanza. En CC-empleado, `RevertirMovimientoAsync` postea un **contramovimiento** y deja el original intacto con `EsReversion = false`: es **la única familia donde "¿está vivo?" no se responde mirando la fila**. El fix cuenta el candidato sólo si su **neto vivo ≠ 0**, reusando `ObtenerNetoVivoAsync` para no tener un segundo contador del mismo número — y de paso cubre la reversión parcial. Queda declarada en el comentario, que es lo que importa para la próxima.

**Cerrado con par discriminante en las dos direcciones:** re-registrar deja Id nuevo, `EsAviso=False`, **2 movimientos de alta / 2 egresos / 1 ingreso de reversión**; y el control positivo que impide el fix fácil — 3 POST del movimiento **vivo** siguen dejando 1 fila, con el 2.º y 3.º devolviendo el Id del 1.º. Los dos mutantes (`M12`, que vuelve al bug, y `M13`, que abre la guarda del todo y reabre `LP-082`) **tumban los dos la misma afirmación**, que es la que exige que el doble submit del movimiento vivo siga colapsando.

## `LP-115` — el arnés tenía razón, y no tocarlo fue la decisión difícil

El fix del pase 1 hizo caer `ArnesReconciliacionTx` de 153/153 a **152/153**. La salida cómoda era actualizar la afirmación "con justificación escrita". **No se hizo, y fue correcto:** el escenario 16 corre `foreach (n in {3,8})` y siembra las dos veces con la **misma clave natural** (el `Motivo` es una constante, sin `n` adentro), así que la siembra de `N=8` colapsaba contra el movimiento de `N=3` ya revertido y las 8 reversiones fallaban. **`LP-114` y `LP-115` eran el mismo defecto por dos lados**, y actualizar la afirmación habría tapado justo lo que bloqueaba el merge. Con el fix vuelve a **153/153 y exit 0 sin un solo cambio en el instrumento** — verificado por QA con `git diff -- tools/` vacío y con un mutante propio que tumba **exactamente** `16.1/N=8`. La tesis quedó **medida, no declarada**.

**Regla:** cuando un fix hace caer un arnés, las dos lecturas posibles no valen lo mismo. "La afirmación quedó vieja" es la cómoda y "el arnés detectó algo" es la que hay que descartar primero, porque el costo de equivocarse es tapar el defecto con el instrumento que lo encontró.

## El mecanismo nuevo de aviso, y los dos huecos que abrió

El costo de `LP-064` y `LP-095` lo midió QA y su juicio de negocio fue que **el de `LP-064` es alto**: dos fletes de $8.000 el mismo día con igual descripción es rutina en una ferretería (dos viajes del mismo flete, mismo precio, descripción "flete"), y **el problema real no es el bloqueo sino el ícono de éxito** — la operación no entra y nadie se entera. La salida elegida no fue sacar la guarda: se agregó un tercer resultado, `ServiceResult.CreateAviso` + bandera `EsAviso`, con `TempData["WarningMessage"]`, `icon: 'warning'` y título *"No se registró de nuevo"*. **Verificado por navegador**: diálogo visible, `.swal2-icon.swal2-warning`, cero `icon:'success'`, y el par discriminante de que con descripción nueva vuelve a `swal2-success`.

**Pero `CreateAviso` deja `Success` en `true` a propósito** ("la operación no falló, y los callers que sólo miran `Success` siguen igual"). Eso es defendible y **crea un lector nuevo del contrato**, que es exactamente la forma de `LP-076` aplicada a un resultado en vez de a una regla. La enumeración de callers —hecha por **injection sites de las 4 interfaces, no por nombre de método**— encontró **2 huecos sobre 8 callers**:

| Caller | Qué hace con el resultado | Veredicto |
|---|---|---|
| `CCEmpleadoController`, `GastosController`, `ProveedoresController` | sólo muestran, mapean `EsAviso` | seguros |
| `OrdenesCompraController:390` | redirige por `vm.OrdenCompraId`, no por el Id del resultado | seguro |
| **`PlanEcheqService:199`** | lee sólo `!Success`, **descarta `EsAviso`**, encadena `ObtenerSaldosAsync` y arma su propio `CreateSuccess` con `EcheqsGenerados = input.Lineas.Count` | **`LP-117` `major`** |
| **`ClientesController:264`** | el service **ni emite** el aviso: colapsa con `CreateSuccess` | **`LP-121` `minor`** |

`LP-117` medido: con un plan de 3 echeqs ya cargado, recargarlo con **números nuevos** deja **0 filas nuevas** y la pantalla dice, en verde, *"Plan de 3 echeq(s) generado por $ 300.000,00"*. Y lo que **no** rompió, también medido: cero `switch` exhaustivo sobre `ServiceResult` en el repo, el JS consumidor lee sólo `.success`/`.message` (así que `esAviso` es aditivo), y ningún endpoint `Json(result)` está en un camino que pueda devolver el aviso.

## `LP-116` — cerrado, y la guarda no quedó demasiado ancha

Mensaje de negocio en castellano que **nombra el CUIT**, matcheando **por nombre de índice y no por el error 1062** (el número dice que hay duplicado pero no de qué, y los dos índices necesitan mensajes distintos). Par discriminante del `when(...)`: un `CHECK` inyectado produce una `DbUpdateException` de otra naturaleza y **sigue al catch genérico sin afirmar una causa falsa**. Nombre y CUIT dan mensajes **distintos**. Hallazgo de método del propio QA: **el catch sólo se alcanza por la carrera** —en serie frena la pre-validación con el mensaje viejo—, y eso le había dado un falso verde en su primera corrida.

## El trío que estuvo BLOCKED dos veces: los tres duplican

Era la categoría "A con residual" que el implementador declaró y que dos corridas dejaron sin medir por falta de fixture. **Armado el fixture (borrador → pago exacto → confirmar), los 2 POST idénticos PARCIALES en serie duplican en los tres, reproducido en dos corridas:**

- **`LP-119` `critical`** — facturación parcial: **2 comprobantes AFIP**. Camino fiscal: un doble clic emite dos facturas, y la única salida es una nota de crédito que **también duplica**.
- **`LP-120` `major`** — nota de crédito: 2 notas, **$1.210 por un pedido de $605**.
- **`LP-118` `major`** — devolución: 2 devoluciones, 2 unidades de stock, **$2.000 de caja por 1 unidad**.

Los seis resultados vuelven `Success=True, EsAviso=False`. La guarda de residual **acota el daño al remanente pero no impide el duplicado**. Y el dato que explica por qué nadie lo veía: **los arneses de esos tres sitios están verdes y no cubren el submit parcial.**

## Estado de la familia de idempotencia, que es el entregable de este lote

**Arreglados y cerrados (6):** alta de gasto, adelanto de CC empleado (los dos caminos), ajuste de CC proveedor, alta de pago a proveedor, el tope de pago sin lock, y la revocación de acceso.

**Abiertos (7):** `LP-112` ajuste manual de caja · `LP-113` divergencia campo/ledger en `ProveedorService.EditarAsync` (QA corrigió el diagnóstico del implementador: la causa es `cambioElSaldoInicial` leído **antes** de la transacción, no el neto vivo) · `LP-117` el hueco del aviso en el plan de echeqs · `LP-118` devolución · **`LP-119` facturación parcial, `critical` y fiscal** · `LP-120` nota de crédito · `LP-121` CC cliente colapsa sin avisar.

**Y un sitio que está bien por accidente:** `ProveedorService.CrearAsync` depende de 2 índices únicos sin declararlo — con índice deja 1 fila, sin índice deja 3 en paralelo. La dependencia quedó declarada en el call site; no se le agregó lock porque el dueño del nombre y del CUIT es la tabla entera, así que **la solución correcta es el índice**.

**El bloque `MISMA FORMA, SIN TOCAR` se rehízo por enumeración** (15 archivos, ~35 métodos) con el criterio de regeneración escrito al lado, y **QA verificó que el criterio es ejecutable**: lo volvió a correr y el grep devuelve exactamente los 15 archivos que declara. Eso es lo que impide que la lista vuelva a envejecer.

## Lo que este lote dice sobre el método, y la recomendación

Nueve defectos cerrados con evidencia es un buen resultado. Pero en el camino, **arreglar sitio por sitio produjo una regresión que bloqueaba el pago de un sueldo (`LP-114`) y dos huecos en el mecanismo que se creó para arreglarlo (`LP-117`, `LP-121`)**, y la enumeración honesta descubrió que la familia era el doble de grande de lo que parecía, con un `critical` fiscal adentro. Eso no es falta de cuidado: es lo que pasa cuando **la misma invariante se re-implementa una vez por sitio**, con una forma de baja distinta en cada familia y un contrato de resultado que cada caller interpreta a su manera.

**Recomendación, que es una decisión de arquitectura y no de implementación:** antes de escribir siete parches más, evaluar una solución **estructural** para "este POST ya se procesó" —un token de submit por formulario, o un decorador de idempotencia sobre los Services que escriben plata— contra el costo de seguir sitio por sitio. Los siete abiertos son la oportunidad de decidirlo con datos en la mano. **Queda para el arquitecto (etapa 3); no se implementa nada más de esta familia hasta que esa decisión esté tomada.** `LP-119` es la excepción: es `critical`, es fiscal, y no espera.

## Riesgos de liberación

1. **`LP-119` `critical`.** Un doble clic emite dos comprobantes AFIP con CAE y el remedio duplica. **No se libera el lote sin los tres del trío.**
2. **Los 7 abiertos de la familia** siguen duplicando plata en producción el día que esos módulos se usen.
3. **`LP-108` sigue como riesgo aceptado por decisión del cliente** (ver la sección de esa decisión). `LP-106` cerrado **baja** ese riesgo de *no revocable* a *revocable con intervención*, que era el objetivo de incluirlo.
4. **Nada está commiteado.** Los fixes viven en el working tree; si alguien hace `git checkout` se pierden los dos pases.
5. Cero migraciones en los dos pases, confirmado dos veces: **la cola de producción sigue en 12 pendientes** y este lote no la mueve.

## Trampas de medición declaradas en estos dos pases

Las de QA, que son las que casi produjeron veredictos falsos: contar `CajaMovimientos` sin mirar la dirección (la reversión escribe su ingreso con el `OrigenId` del original, así que daba 3 donde esperaba 2); el signo del neto de un Adelanto es negativo y el contramovimiento sembrado iba con el `Tipo` equivocado; `offsetParent` es `null` en un `position: fixed`, lo que da "diálogo invisible" sobre un diálogo visible; una assertion que buscaba una subcadena **compartida por el mensaje viejo y el nuevo**, que dio falso verde hasta forzar la carrera; `last_insert_id()` no sirve para sembrar porque cada `mysql -e` es una conexión nueva; un mutante por árbol, porque el proceso vivo bloquea el DLL; y un `nohup` huérfano que cambió la password de la víctima antes del test de chaineo e hizo parecer defecto del sistema lo que era basura propia. Del lado del implementador: el primer mutante del lock de `OrdenesCompra` **no mató nada**, y recién un mutante dirigido al pago **programado** demostró que el lock es portante ahí.

## Checklist de salida

- [x] Los 6 defectos del lote original cerrados con par discriminante y control positivo
- [x] `LP-114` (regresión propia), `LP-115` (el arnés tenía razón) y `LP-116` cerrados
- [x] `LP-106`: el sistema puede revocar un acceso, medido en las dos mitades por separado
- [x] El bloque `MISMA FORMA` regenerado por enumeración, con criterio ejecutable verificado
- [x] Cero migraciones; líneas base de los arneses re-medidas hoy, ninguna citada de corridas anteriores
- [x] Repo sin un solo archivo tocado por QA en ninguna de las dos re-verificaciones
- [ ] **`LP-119` `critical` (fiscal): sin arreglar, y no espera la decisión de arquitectura**
- [ ] **`LP-118`, `LP-120`: el resto del trío, sin arreglar**
- [ ] **`LP-117`, `LP-121`: los dos huecos del mecanismo de aviso, sin arreglar**
- [ ] `LP-112`, `LP-113`: alcance aparte, sin arreglar
- [ ] **Decisión de arquitectura sobre idempotencia estructural vs. sitio por sitio, antes de escribir más parches**
- [ ] Commit de los dos pases (hoy sin commitear, a la espera de la decisión de Joaquín)
---

# Ronda de QA completa del sistema — 9 lotes en paralelo, barrido de los 26 controllers (2026-10-08, rama `entrega-1-migracion`, HEAD `05d44f2`)

## **NO-GO para producción. 34 defectos nuevos: 2 `critical`, 2 `high`, 11 `major`.** No es una corrida de un alcance entregado: es un barrido del sistema entero pedido por Joaquín, con 9 lotes de contexto limpio sobre los 26 controllers. **Lo que la ronda encontró no son 34 bugs sueltos: son tres familias y un agujero de seguridad.** La familia de **idempotencia** (un POST repetido duplica plata) aparece en **6 escritores distintos** y tiene en el código una lista de pendientes que nombra 2 de ellos. La familia de **lectores de una regla** (`LP-039`/`LP-040`/`LP-052`) suma **tres puntas nuevas** que los barridos anteriores no alcanzaban: el ViewModel de la Web, el endpoint AJAX de preview, y el precargado de un campo editable. La familia de **tope leído fuera de la transacción** produce el peor defecto de la ronda. Y aparte de las tres: **el sistema no puede revocar un acceso y su cuenta más privilegiada tiene una password fijada en un archivo versionado que es la que corre en producción.** Lo único que se verificó sano de punta a punta es el hotfix `LP-057` del 2026-10-07, que **nunca había pasado por QA**: 8 de 8 criterios PASS, incluida la réplica del backup de producción con diff vacío.

## Por qué esta corrida existió y cómo se armó

`6-qa.md` v23 cerraba en el commit `3758423`. Los dos commits siguientes de código (`1c472fa`, `42c4667`) **no tenían corrida de QA** y eran el hotfix de los 16 índices únicos, con el SQL de 14 de ellos corrido **a mano contra producción**. Eso definió el lote 1. El resto de la ronda es el barrido que el proyecto nunca había tenido: los módulos se habían probado de a uno, en el sprint que los construyó, y nunca todos juntos ni contra el catálogo cross-proyecto completo.

**Reparto en 9 lotes** (instrucción 39 §5, lotes de a lo sumo 3 módulos y 1 si es financiero o de integración), en 3 oleadas de 3 para no pasar de 6 simultáneos:

| Lote | Alcance | Veredicto | Defectos |
|---|---|---|---|
| 1 | Hotfix `LP-057` (16 índices entre vivos) + migraciones y deploy (`LP-050`) | **8/8 PASS** | `LP-058`, `LP-059` |
| 2 | Ledger de caja + gastos | 8 PASS, 1 FAIL, 1 BLOCKED | `LP-064` |
| 3 | Ventas / POS + medios de pago (CR-01, CR-03, CR-05) | 6 PASS, 4 FAIL | `LP-070`, `LP-071`, `LP-072` |
| 4 | Facturación parcial + NC + devoluciones (re-verificación dirigida) | 3 PASS, 4 FAIL, 1 BLOCKED | `LP-076`..`LP-080` |
| 5 | Clientes + CC clientes + CC empleados + entregas | 7 PASS, 1 FAIL | `LP-082`..`LP-086` |
| 6 | Proveedores + CC + pagos + plan de echeqs | 6 PASS, 3 FAIL | `LP-088`..`LP-093` |
| 7 | Compras: órdenes, recepción, moneda | 7 PASS, 2 BLOCKED | `LP-094`, `LP-095` |
| 8 | Catálogo + stock + presupuestos + aumento masivo | 5 PASS, 4 FAIL, 1 BLOCKED | `LP-100`..`LP-103` |
| 9 | Transversal: autorización, usuarios, config, notificaciones, dashboard, higiene | 6 PASS, 3 FAIL | `LP-106`..`LP-111` |

**Chequeo de reglas cross-proyecto nuevas (33): hecho UNA vez, por el orquestador, y pasado como dato a los 9.** Última validación declarada 2026-10-07; `regresiones-manuales.yml` sin ítems posteriores; en la 32 las dos entradas de 2026-10-07 son `LP-004` (crm-olvidata, plantillas de WhatsApp, N/A) y `LP-057` (de este proyecto, objeto del lote 1). **Resultado: ninguna regla nueva pendiente.** Nueve lotes repitiendo ese chequeo habría sido el gasto más caro y más inútil de la ronda.

**Lo que NO hicieron los lotes, y por qué.** Joaquín pidió auto-fix de lo trivial. No se aplicó: la instrucción 33 y el contrato de evaluación independiente de la 30 prohíben que el evaluador sea el que arregla, porque un generador que se autocalifica aprueba su propio trabajo. Los 9 lotes reportaron; los fixes los decide Joaquín. Tampoco escribieron en `6-qa.md` ni en `trazabilidad.md`: ese archivo era el quinto recurso que los lotes paralelos se pisaban, y lo consolidó el orquestador. **Verificado al cierre: `git status --porcelain` del repo del sistema no tiene un solo archivo de código, vista, migración o configuración tocado por ningún lote.**

## Los tres hallazgos sistémicos

### 1. Idempotencia: un POST repetido duplica plata, en 6 escritores, y la lista de pendientes del código nombra 2

Cuatro lotes independientes encontraron la misma forma, **y todos la reprodujeron EN SERIE** — no hace falta concurrencia, alcanza un doble clic, un F5 o un retry de red:

- **`LP-064` `major`** — alta de gasto: 2 POST idénticos → 2 `Gastos` y 2 `CajaMovimientos`, los dos con mensaje de éxito.
- **`LP-082` `major`** — adelanto de CC empleado: 3 POST → 3 movimientos y 3 egresos de caja.
- **`LP-093` `major`** — ajuste de CC proveedor (2 en serie → 2 filas) y alta de pago.
- **`LP-095` `major`** — pago de orden de compra: 3 POST → 3 pagos, 3 egresos y 3 movimientos de CC.

**El dato que convierte esto en un hallazgo de proceso y no en cuatro bugs:** el bloque de comentario `MISMA FORMA, SIN TOCAR` de `CuentaCorrienteClienteService.cs:364` enumera **sólo dos** sitios pendientes (`CCProveedorService.RegistrarAjusteAsync` y el devengamiento de `CCEmpleadoService`) y **no nombra ninguno de los cuatro que fallaron**. Alguien relevó la familia, escribió la lista a mano, y la lista envejeció mal. **Tres lotes encontraron por separado un sitio que no estaba en ella.**

Y el agravante que invalida el fix barato: **el token antiforgery de ASP.NET no es de un solo uso.** El lote 6 reenvió el mismo payload con el mismo token tres veces y duplicó igual. Un `disabled` en el botón no cubre el F5 ni el retry de red. **El único sitio de la familia que resiste el triple submit es `CuentaCorrienteClienteService.RegistrarAjusteAsync`, que tiene idempotencia por clave natural: ése es el molde del fix.**

**Lo que pasó bien, y conviene no perderlo:** el aumento masivo de precios **no** reincide — su guarda `UpdatedAt > PreviewGeneradoEn` funciona, y el 2.º y 3.er envío aplican 0 productos. Y el ajuste de stock tampoco, porque lo frena su chequeo de `StockEsperado`. Dos formas distintas de resolverlo que ya existen en el sistema.

### 2. Lectores de una regla de negocio: tres puntas nuevas que los barridos anteriores no podían ver

La familia `LP-039`/`LP-040`/`LP-052` llevaba tres recurrencias. Esta ronda le suma **tres superficies estructuralmente invisibles** para la forma en que se venían barriendo (grep sobre Services y DTOs):

- **`LP-076` `major` — el ViewModel de la Web.** `Web/Models/FacturacionParcialViewModels.cs` recalcula el pendiente a facturar (`Cantidad - YaFacturada`) sin restar lo devuelto, y el mapeo nunca copia el campo bueno del DTO. **La pantalla muestra 7, el server acepta 6, y el botón "Todo" precarga el 7 que rebota** — con el `Subtotal` de la misma fila calculado sobre 6. Es el **séptimo** lector de una regla cuyos seis anteriores estaban todos correctos y contados.
- **`LP-078` `low` — el endpoint AJAX de preview.** `POST /Devoluciones/Preview` no evalúa la habilitación ni acota la cantidad: informa importes sobre una venta que el botón, el GET y el POST rechazan, y con cantidad 999999 devuelve nueve cifras. Cuarta punta de `LP-052`; no aparece en un barrido por "dónde hay un botón o un form".
- **`LP-077` `low` / `LP-055`** — el **valor precargado** de un campo editable. Los arneses afirman sobre lo que el POST acepta, no sobre lo que el GET precarga, así que los mutantes de esas ramas sobreviven con el arnés entero en verde. Los tres precargados del alcance (`ACobrar`, `AAcreditar`, `ADevolver`) están sin red; los tres hidden de confirmación sí la tienen.

**Dos lotes buscaron la forma `LP-076` en su propio módulo y volvieron limpios, por medición y no por suposición:** en ventas no hay ninguna propiedad calculada en `Web/Models` (el mapeo copia los nueve números del DTO), y en compras las cuatro calculadas delegan en `SaldosCompraDto`. En clientes hay una (`DevolucionViewModels.cs:89`) que duplica literalmente la fórmula del DTO y hoy **coincide**: riesgo de divergencia futura, no defecto.

### 3. Topes leídos fuera de la transacción

- **`LP-088` `critical`** — el tope de "saldo sin comprometer" de una compra se lee **fuera de la transacción y sin lock**: **3 POST paralelos de $300.000 entran los tres contra una compra de $400.000**. Medido en 5 tandas, con un exceso acumulado de **$2.500.000 sobre cinco compras de $400.000**, 9 egresos de caja y el saldo de CC del proveedor en **−$2.228.131**. Confirmado de forma independiente por el lote 7 desde el lado compras. Re-confirmado por el lote 6 con la cadena de conexión fiel al repo, después de detectar que su propio parámetro `UseAffectedRows=False` podía estar fabricando un síntoma distinto.
- **El contraste que prueba que es resoluble:** la **recepción** de mercadería **sí** tiene el lock, y el lote 7 lo midió como portante — con la fila tomada por fuera (`FOR UPDATE` + `DO SLEEP(20)`) la recepción **esperó 18.018 ms** antes de completar. El mismo módulo tiene el mecanismo bien en una punta y ausente en la otra.

## El agujero de seguridad, que es independiente de las tres familias

- **`LP-108` `high` — la password del SuperUsuario de producción está en un archivo versionado y es la que corre.** `appsettings.json` (trackeado por git) fija `Seed:SuperUser:Password`; `appsettings.Production.json` no tiene la clave; y el app pool del sitio de producción **no define** `Seed__SuperUser__Password`. **Verificado de forma independiente por el orquestador contra el hosting real**, no sólo por el lote. Agravante: la misma credencial está escrita en texto en un archivo de memoria de agente versionado dentro del repo del cliente (`LP-111`), así que también está en el historial de git. **Rotarla no alcanza: hay que sacarla del archivo y del historial, y definirla como secreto del app pool.**
- **`LP-106` `high` — el sistema no puede revocar un acceso.** Bloquear a un usuario (`POST /Users/ToggleEstado`) **no rota su `SecurityStamp`** y `OnValidatePrincipal` no chequea `Estado`: la cookie ya emitida sigue sirviendo hasta 8 horas. El lote bloqueó un Vendedor, esperó 7m36s (más que el `ValidationInterval` de 5 min) y con la cookie vieja **escribió**: `POST /Clientes/Create` → 302 y fila `clientes.Id=2994` con el `CreatedByUserId` del usuario bloqueado. Asimetría probada en el mismo controller: `Users/Edit` con `NewPassword` **sí** rota el stamp.
- **Combinados son peores que por separado:** la cuenta más privilegiada tiene una password pública y, si se la usa, no se puede cortar la sesión en caliente.
- **`LP-110` `minor`** — el app pool de La Platense tiene definido un `ConnectionStrings__RecoTrackMySql`, de otro cliente del estudio. Nadie lo lee, pero es una credencial ajena dentro de este proceso. Hallazgo del orquestador al verificar `LP-108`.

**Lo que la revisión de autorización encontró sano, y vale como línea base:** 206 acciones × 4 identidades = 824 requests. Sin cookie, 195 de 206 redirigen a login; las 11 alcanzables sin autenticar son exactamente las que deben serlo, y las 13 alcanzables por cualquier autenticado son todas de autoservicio. Ningún endpoint JSON/AJAX quedó abierto. Un Administrador no alcanza ninguna de las 10 acciones de SuperUsuario. El IDOR de `MiCuenta` y el de notificaciones están cerrados, con oráculo no vacuo. Y el filtro por tarjeta del Dashboard —lo único que tapa la fuga de la política `ConsultaDashboard`, deliberadamente floja— **funciona**: con sondas sembradas, el Vendedor ve 1 de 5 tarjetas y el Repartidor ninguna.

## Decision del cliente sobre `LP-108` (2026-10-08)

**Joaquin decidio dejar la password del superadmin como esta.** Se le reporto el hallazgo con la cadena de precedencia verificada de punta a punta contra el hosting real -- `appsettings.json` versionado la fija, `appsettings.Production.json` no la sobrescribe, el app pool del sitio de produccion no define `Seed__SuperUser__Password` -- y pidio no tocarla. **Queda como riesgo aceptado, no como defecto abierto**, anotado asi en el `fix_aplicado` del item del catalogo, que **no se cierra**: el fix y las pruebas minimas siguen escritas por si el criterio cambia.

La consecuencia, en una linea y sin volver sobre ella: **cualquiera con acceso al repositorio, a su historial de git o al artefacto de deploy tiene la cuenta de maximo privilegio de produccion, y mientras `LP-106` siga abierto esa sesion no se puede cortar hasta que expire.** Por eso `LP-106` **si** entra al primer lote de fixes: arreglarlo no elimina este riesgo, pero lo baja de *no revocable* a *revocable con intervencion*, que es la diferencia entre un incidente y un problema.

`LP-111` (la memoria de agente versionada en el repo del cliente, que es uno de los lugares donde la credencial quedo escrita) **conserva su valor igual**: la parte de "rotar porque esta en el historial" queda fuera por esta decision, pero sacar el directorio del repo del cliente sigue correspondiendo por las otras dos razones -- es metodologia del estudio, no entregable, y muta durante las corridas ensuciando el arbol de todos los lotes.

## Defectos nuevos: 34

| Severidad | Ids |
|---|---|
| `critical` | `LP-088` (tope de pago sin lock), `LP-100` (código de barras en dos productos vivos) |
| `high` | `LP-106` (no se puede revocar acceso), `LP-108` (credencial de producción versionada) |
| `major` | `LP-064`, `LP-070`, `LP-076`, `LP-082`, `LP-089`, `LP-090`, `LP-093`, `LP-094`, `LP-095`, `LP-101`, `LP-103` |
| `minor` | `LP-058`, `LP-071`, `LP-072`, `LP-083`, `LP-084`, `LP-085`, `LP-086`, `LP-091`, `LP-092`, `LP-102`, `LP-109`, `LP-110` |
| `low` | `LP-059`, `LP-077`, `LP-078`, `LP-079`, `LP-080`, `LP-107` |
| `trivial` | `LP-111` |

Los 34 están en `docs/qa/regresiones-manuales.yml` (198 → **232** ítems, sin duplicados, YAML válido, índice `cat_resumen.txt` regenerado). **13 de ellos los publicó el orquestador al consolidar**, porque los lotes 4, 7 y 9 reportaron sus partes y no los escribieron al catálogo: el 4 no lo intentó, y el 7 y el 9 se abstuvieron a propósito al ver que el archivo se movía bajo sus pies con 9 lotes en paralelo. **La aritmética cierra exacta (198 + 2 + 1 + 3 + 5 + 6 = 215 antes de la consolidación), así que ninguna escritura concurrente se perdió** — se verificó, porque una escritura perdida en un catálogo compartido no avisa.

Sigue abierto de antes: **`LP-051` `trivial`**, confirmado hoy en el árbol en `Views/Configuracion/InteresesTarjeta.cshtml:243`, con el mecanismo reproducido en las líneas 238-242, inmediatamente arriba del comentario que promete no reproducirlo.

## Los dos `critical`, con su evidencia

- **`LP-088`** — ver arriba. $2.500.000 de exceso en 5 tandas.
- **`LP-100`** — `POST /Productos/Create` con un EAN que ya es **código de barras alterno activo de un producto vivo** devuelve **200 sin un solo mensaje** y crea el producto. El código queda en **dos productos vivos a la vez** y, peor, **las dos pantallas resuelven a productos distintos**: `/Productos/BuscarPorCodigoBarras` devuelve el nuevo y `/Presupuestos/BuscarProductos` el original — **dos precios para el mismo código escaneado** ($11,04 contra $150,00). El caso de `LP-057` (código tomado por un producto borrado) **sí** pasa; lo que falta es la validación contra los alternos vivos. Con 8.276 códigos alternos en producción sobre 3.865 productos, la superficie es real.

## Lo que se cerró o se acotó de la corrida anterior

- **El hotfix `LP-057`: verificado de punta a punta, 8/8 PASS.** 16 índices `UX_*_Vivo` enumerados uno por uno sobre 14 tablas; los 16 `IX_` originales en `NON_UNIQUE=1` como el commit declara; la barrida de reuso anda **16/16** y el control positivo sobre la base con el `Down` aplicado da **0/16**, cada caso con su `1062`. End-to-end por HTTP: el `POST /Productos/Edit` con el código del producto dado de baja el 2026-10-07 devuelve 302 sin pantalla de error, y el mismo POST contra el fixture pre-hotfix devuelve 500 con `Duplicate entry`.
- **La pregunta que el estado de producción no podía responder leyendo el repo, respondida:** réplica del backup de prod + el SQL **del archivo de hoy** + la fila en `__EFMigrationsHistory` → snapshot **idéntico a producción real, diff vacío sobre 67 hechos**. O sea: lo que se corrió a mano coincide con lo que quedó en el repo después de que `42c4667` le sacara 51 líneas, y **nada quedó sin aplicar**. Después, `ef database update` sobre esa réplica aplica las 12 pendientes, **saltea** `203515`, aplica `232224` y termina en 119 hechos idénticos a una base desde cero. Las dos asimetrías también cerradas: de las 12 pendientes, **ninguna toca una columna base** de las 14 generadas que prod ya tiene.
- **`LP-050` `major`: ACOTADO, no cerrado.** 3 de las 4 migraciones con backfill **sí** autorrevierten, porque su `Down` dropea las columnas que el `UPDATE` escribió. La única con `UPDATE` sobre datos que se quedan es `D9`, y eso se convirtió en `LP-058`. El ensayo sobre la réplica con datos reales dio `MedioPago` NO NULL y conteos idénticos antes/después (112.485 / 2.990 / 85 / 128 / 8.276 / 110.683).
- **`LP-020` y `LP-013`** siguen abiertos por decisión de negocio declarada, no por defecto. El criterio "las reversiones restan del total de ingresos" quedó **BLOCKED** y vuelve al analista: netearlo descuadraría cierres ya firmados.
- **`LP-023`** (reclamo concurrente de pagos programados) **realmente cerrado**: 4 tandas × 8 llamadas concurrentes con `Barrier`, siempre una sola reclama y las otras siete devuelven 0.
- **`LP-014`, `LP-031`, `LP-037`, `LP-039`, `LP-040`, `LP-047`, `MH-001`** y una veintena más del catálogo: re-medidos PASS por los lotes que los tocaban.

## Correcciones a afirmaciones de corridas anteriores y de los propios commits

Esto es lo que más conviene leer de todo el bloque, porque son cosas que el proyecto creía ciertas:

1. **El PASS de v23 sobre el gate de AFIP se apoyaba en evidencia que no cubría lo que afirmaba.** v23 dice que "Confirmar y facturar" está gateado por `afipConfigurado`, *"que es el mismo guard server-side"*, y lo midió por la **ausencia del botón en el DOM**. El lote 3 posteó `continuar=facturar` directo con AFIP apagado y dejó una venta en `Facturada` con un `ComprobanteAfip` creado. **Pero el lote reconcilió la contradicción y la resolvió en contra de su propio hallazgo:** el estado final del bypass es **idéntico** al que produce un botón que la UI **sí ofrece** (`POST /Ventas/Facturar` desde Details, visible con AFIP apagado), porque desde `LP-040` eso es el comportamiento buscado. Así que no hay bypass funcional: hay una **inferencia no cubierta por la evidencia** (forma `LP-052`) y un comentario que afirma un guard inexistente → **`LP-072` `minor`**, y nada más. El `continuar=facturar` tiene **un solo emisor** en toda la solución y el input lo crea el JS en el click: hace falta armar el POST a mano.
2. **La afirmación del commit `1c472fa` sobre `LineasEcheq` es falsa.** El commit dice que el hotfix *"habilita el único de `LineasEcheq (Banco, Numero)` que la Entrega 3 había dejado sin poner por este mismo hueco"*. El lote 6 midió que **la baja del plan le escribe `DeletedAt` al pago, no a la línea**, así que una columna `NumeroVivo` no liberaría nada. Y el índice **sigue sin estar**: en serie la validación del Service rechaza bien, pero **en paralelo entran dos líneas vivas con el mismo banco y número** → **`LP-092`**.
3. **El dato de producción que `6-qa.md` declara está desactualizado.** El documento dice "5 ventas (3 `Confirmada`) y 4 movimientos de caja". Medido hoy contra prod: **0 `Ventas` y 1 `CajaMovimiento`**. No usarlo como oráculo.
4. **`2-disenador-funcional.md`, flujo 16 punto 1, está equivocado y el código tiene razón.** Afirma el principio de escritor único de `Producto.Stock`; el único escritor que el proyecto defiende es el de la **tabla** del ledger, y `IMovimientoStockService` declara explícito que **no** toca la columna, que tiene 5 escritores, todos callers. Ya hizo que un brief mandara al implementador por el camino equivocado. **Pendiente de corregir en el documento de diseño.**
5. **`LP-056` necesita refinarse: su regla no es ejecutable como está escrita.** Dice "los arneses que la afirman, enumerados por `grep`". El lote 4 midió que grepear el nombre de la función mudada da **0 arneses**, y que el ancla que sí funciona es la propiedad del DTO que los arneses leen. El criterio tiene que nombrar el ancla.
6. **El conteo de advertencias del build tiene una trampa:** si el proyecto Web no recompila, el `CS0114` no reaparece y el build da **8** en vez de 9. Tres lotes lo pisaron. La línea base real es **0 errores / 9 advertencias**, confirmada con recompilación forzada.

## Gaps de alcance: cosas que no existen, no defectos

- **La importación de listas de precios de proveedor no está construida** (`IListaPreciosProveedorImportService`: 0 hits). Declarada como pendiente en diseño y arquitectura, pero el `metadata.md` del proyecto la lista **dentro** del alcance ("compras con listas de precios de proveedor"). **Decisión de alcance para Joaquín.**
- **La recepción parcial de mercadería no existe**, y la frase no aparece en **ninguna** definición: era un criterio del brief sin requisito detrás. Vuelve al analista.
- **`CodigosProveedorProducto` no tiene camino de escritura en la aplicación**: lo escribe únicamente `tools/MigracionCatalogo`. No hay pantalla que probar.
- **No existe baja de usuario**, sólo bloqueo — y el bloqueo es `LP-106`.
- **No existe edición de gasto** (`IGastoService` = Listar/Crear/Anular).
- **No hay endpoint para dar de baja un comprobante**, así que una venta en `Facturada` **no tiene salida**: la única puerta que el catch-all de `MotivoParaNoAnularVenta` deja abierta ("llega acá sólo si TODOS sus comprobantes fueron dados de baja") no tiene implementación. Preexistente, idéntico por el camino normal, y es condición de entrada para habilitar AFIP real.
- **`Home/Index` autenticado redirige a `/Notifications`** con un TODO *"redirigir al Dashboard cuando se defina"* — y el Dashboard existe y es, según el análisis, la pantalla de mayor prioridad del cliente. Pantalla de arranque equivocada.
- La cartera de cheques y los impuestos por cheque/plataforma/gasto son **exclusión confirmada**, no gap.

## Mejoras priorizadas

1. **`NU1902`, primero porque son CVE con dependencia:** MailKit 4.14.1 → **4.16.0** y MimeKit 4.14.0 → **4.15.1**. Un solo bump de MailKit arrastra MimeKit y **no es breaking** para `EmailService` (misma línea 4.x). Riesgo real **menor** al que sugiere la advertencia: el camino STARTTLS no se ejecuta porque producción usa `SslOnConnect` en el puerto 465; el de MimeKit sí es alcanzable, porque las direcciones vienen de `user.Email`.
2. **Los listados de 112k filas leen de 337.480 a 642.084 filas por página de 25** (≈3–6 barridos completos: dos `CountAsync` más un `ORDER BY` sobre columna sin índice), medido con `Innodb_rows_read` y con el ruido de fondo verificado en 0. Contra el MySQL compartido de SmarterASP con tope de 500 MB, es riesgo de liberación.
3. **`CS0114` en `HomeController.cs:38`**: es **intencional pero mal declarado** — `StatusCode(int)` es la acción de `UseStatusCodePagesWithReExecute` y funciona (404/403/500 verificados). Falta `new`. No es bug hoy, pero la próxima línea que llame a `StatusCode(...)` dentro de ese controller va a devolver una vista 200 en silencio.
4. **Mensajes de EF Core en inglés llegando al usuario** en dos superficies distintas (alta de proveedor concurrente y aumento masivo fallido): *"Could not save changes. Please configure your entity type accordingly."*
5. **`.ov-monto`**: la usan 5 vistas y **26 de las 31** con importes no. Lo nuevo es que la inconsistencia está **dentro de un mismo sprint**: `Devoluciones/Registrar` la usa y `FacturacionParcial/Emitir` y `NotasCredito/Emitir` no.
6. **`AutoValidateAntiforgeryToken` global** en vez del atributo por acción (ver `LP-107`): la protección aplicada acción por acción se degrada sola.
7. **`ICCProveedorService.ObtenerSaldoTotalAsync` no tiene ningún lector** y, si se cableara a un dashboard, sumaría saldos de todos los proveedores **mezclando monedas**. Conviene borrarlo o acotarlo antes de que alguien lo use.
8. **El `id` de compra en `Confirmar/CancelarPagoProgramado` es cosmético**: acepta un par (compra, pago) inconsistente y actúa igual. Sin frontera de rol cruzada, pero la URL miente.
9. **Declarar en el código las ramas dominadas** (`D3`, `H6`), que el cierre anterior ya había recomendado y sigue sin hacerse: `grep "defensa en profundidad\|dominad"` da **1 hit en todo el código**, sin relación.

## Riesgos de liberación, ordenados

1. **`LP-108` + `LP-106`** — bloqueantes absolutos de producción: password pública en la cuenta más privilegiada, y sin capacidad de revocar la sesión.
2. **`LP-088` + `LP-095`** — plata duplicada y topes vulnerados en el pago a proveedor. Producción tiene **0 órdenes de compra**: el primer día de uso real los encuentra el cliente.
3. **`LP-064` + `LP-082` + `LP-093`** — plata duplicada en caja, CC empleado y CC proveedor, **y entra al cierre firmado, que después no se puede corregir** (`LP-013`). Mitigación inmediata mientras se implementa la idempotencia: guarda de submit en las vistas, sabiendo que **no cubre el F5 ni el retry**.
4. **`LP-100`** — un código de barras en dos productos vivos con dos precios según la pantalla. Es catálogo, el corazón del sistema para este cliente.
5. **`LP-070`** — sobrepago: una venta de $121 con pagos de $50 + $1.000 se confirma y postea $1.050 en caja; por cuenta corriente, $5.000 de débito sobre $242 de mercadería. **Se alcanza con un cero de más al tipear**, sin POST armado, y los importes cierran entre sí, así que el descuadre no se ve hasta el arqueo.
6. **`LP-076`** — no escribe dato malo, pero muestra un número equivocado en una pantalla fiscal y lleva al usuario a una operación que rebota.
7. **`LP-101`** — `Producto.Stock` y la suma del ledger difieren en una milésima por redondeo, y **el ledger está partido en dos tablas** (`AjustesStock` no escribe `MovimientosStock`), así que la reconciliación completa cierra en esa misma diferencia.
8. **Los 12 pendientes de producción siguen pendientes.** Todo lo verificado en el lote 1 es del **deploy futuro**, no del estado actual. `ef database update` contra prod sigue aplicando las 12 de una, que es el deploy entero de las Entregas 3 a 6.

## Defectos de la propia red de medición

Que la ronda haya encontrado estos es parte del resultado: son la razón por la que los verdes anteriores no eran tan verdes.

- **`LP-091` `minor`** — la guarda de nombre de base de **los nueve arneses** corta por substring contra `laplatense_qa` (`MigracionCatalogo/Program.cs:165`), que es exactamente el prefijo que la convención de aislamiento por lote manda usar. **Ningún arnés del repo corre contra un clon llamado `laplatense_qa_lN`**: cuatro lotes lo pisaron y tuvieron que renombrar su base o escribir un runner propio. Es un defecto del harness causado por el choque de dos convenciones del propio estudio.
- **`LP-077`, `LP-055`** — los precargados sin red (ver familia 2).
- **`LP-056`** — el set de regresión armado por archivos editados en vez de por la condición medida, más el agravante del DLL equivocado: `HabilitacionDeAccion` vive en `Domain`, así que un chequeo de "el mutante entró al binario" escrito contra `Infrastructure.dll` **descarta los mutantes en silencio**. El lote 4 lo reprodujo exacto: mutar la clase deja `Infrastructure.dll` byte-idéntico.
- **`LP-080`** — un camino de cálculo sin consumidor: puede divergir para siempre sin que ninguna pantalla lo delate.
- **`LP-111`** — la memoria de los agentes versionada en el repo del cliente, que además mutaba durante las corridas y ensuciaba el `git status` de todos los lotes.

## Trampas de medición que los lotes declararon

Las anoto porque varias casi produjeron defectos falsos, y las mismas van a reaparecer en la próxima corrida:

- **Aislamiento entre lotes paralelos.** Dos lotes encontraron su **puerto asignado ya tomado** por otro proceso; uno de ellos murió al bindear con un `AddressInUseException` visible sólo en el log y **escribió 6 POST en la base de otro lote** antes de darse cuenta. Los revirtió y lo declaró; **el lote dueño de esa base lo verificó de primera mano y lo descartó con evidencia** (el hueco de `AUTO_INCREMENT` 67-72 sin fila viva, y su primera fila en la 73). La regla que sale: **no derivar el puerto del número de lote; elegirlo verificando que esté libre y confirmar que el PID que escucha es propio antes de la primera medición** — y confirmar la identidad por una fila que sólo exista en la base propia, no por el log, que a dos lotes les mostró el arranque de **otra** aplicación.
- **Leer HTML como texto plano miente en las dos direcciones.** Los banners `d-none` aparecen como si estuvieran en pantalla (un lote casi reportó tres contradicciones falsas); y quitarle los `<script>` **borra los mensajes de rechazo**, que en este proyecto viven dentro del `Swal.fire`. Un lote concluyó dos veces "el POST volvió sin explicar nada" cuando el mensaje era bueno, y después rehizo la medición con un oráculo que ve los scripts, con control positivo que pasa, y **su hallazgo se sostuvo**.
- **Cuatro tablas en juego para el cierre de caja, no dos.** `EstaCerradoAsync` lee `CierresCajaDiarios`, `EstaMesCerradoAsync` lee `CierresCajaMensuales`, y **`CandadosPeriodoCaja` es sólo el `FOR UPDATE` del lock: nadie la lee como dato.** Un lote estuvo a un paso de publicar un blocker inexistente por encontrar `CierresCajaDiarios` vacía cuando el cierre mensual vivía en otra tabla.
- **El propio instrumento midiendo de más.** El conteo ingenuo de migraciones da 23 y son 22 (`AppDbContextModelSnapshot.cs` no es una migración). Un lote usó `UseAffectedRows=False` en su cadena de conexión, que es justo el parámetro que produce el mensaje de EF que estaba reportando, y relanzó con la cadena fiel para confirmar que el defecto era real. Otro midió `Innodb_rows_read`, que es un contador **global** del server compartido, y verificó 0 de ruido en tres ventanas antes de creerle. Y un `grep` de un nombre de acción matcheó el `Url.Action` del JS y dio un falso positivo: el oráculo correcto es el `id` del elemento.
- **Oráculos con cero en los dos lados no prueban nada.** Un IDOR que devuelve `recordsTotal=0` para víctima y atacante no está cerrado: hay que sembrar la fila de la víctima primero.
- **Rate limiting leído como autorización.** Un barrido de 206 acciones no entra en la ventana de 300 req/min: sin pausas aparecen 429 que se leen como denegaciones.
- **El `Set-Cookie` de `TempData` de un POST cuyo redirect no se siguió** se lo come el **siguiente** GET: a un lote el Details de una venta le sirvió el mensaje de otra. Se resolvió leyendo el estado por SQL y no por la alerta.
- **Compilar en paralelo no se puede:** varios lotes se encontraron `bin/Debug` tomado por otro (`MSB3027`), y redirigir `obj` compartido falla con `CS0579`. La salida es copiar el source a un árbol propio (`git archive HEAD`).

## Checklist de salida

- [x] Hotfix `LP-057`: 8/8 criterios PASS, verificado contra réplica de producción con diff vacío
- [x] Chequeo de reglas cross-proyecto nuevas: hecho una vez, ninguna pendiente
- [x] Los 26 controllers barridos; 206 acciones × 4 identidades en la superficie de autorización
- [x] 34 defectos publicados en `regresiones-manuales.yml` (198 → 232), sin duplicados, YAML válido, índice regenerado
- [x] Ninguna escritura concurrente perdida (aritmética verificada)
- [x] Repo del sistema sin un solo archivo de código tocado por ningún lote
- [ ] **`LP-108` + `LP-106`: bloqueantes de producción, sin arreglar**
- [ ] **`LP-088` + `LP-095` + `LP-064` + `LP-082` + `LP-093`: la familia de idempotencia y topes, sin arreglar**
- [ ] **`LP-100`, `LP-070`, `LP-076`, `LP-101`, `LP-103`, `LP-089`, `LP-090`, `LP-094`: `major`/`critical` restantes, sin arreglar**
- [ ] El bloque `MISMA FORMA, SIN TOCAR` rehecho **por enumeración** de escritores, no ampliado a mano
- [ ] `2-disenador-funcional.md` flujo 16 punto 1 corregido (afirma lo contrario del código)
- [ ] `LP-056` refinado para que su criterio nombre el ancla greppeable
- [ ] Decisión de alcance sobre la importación de listas de precios de proveedor
- [ ] `LP-020` y el criterio de reversiones en el total de ingresos: vuelven al analista
- [ ] Quién puede emitir una nota de crédito y quién puede devolver: el diseño no lo dice, hoy es `RequireVentas` (incluye Vendedor). Vuelve al analista
---

# Entrega 5 lote 2 — devoluciones + mecanismo único de habilitación + cierre de `LP-052` y `LP-053` — QA lote único financiero (2026-10-07, rama `entrega-1-migracion`, commits `001d983`..`3758423` sobre `1116cdf`)

## **GO para merge. `LP-052` CERRADO y `LP-053` CERRADO.** Los 13 criterios del lote en PASS con evidencia ejecutada; 2 BLOCKED por inalcanzables (AFIP). **Los dos defectos propios que el implementador encontró antes de medir están los dos verificados en la BD**, y son los de mayor impacto. **La premisa de mi brief anterior era falsa y el implementador tenía razón en la dirección**: el único escritor que el proyecto defiende es el de la TABLA del ledger, no el de la columna. **Mi conteo independiente de lectores del "ya facturado" da exactamente 6**, el número declarado. **Los 24 mutantes no se pueden auditar de a uno (no están enumerados): se sustituyeron por 21 mutantes propios derivados del diff**, con 15 muertos, 4 sobrevivientes explicados y 2 controles negativos en cero. 2 defectos nuevos, los dos `low` y los dos de red de medición: `LP-055` y `LP-056`.

## Cómo se corrió (y la caída declarada)

**Playwright MCP NO está disponible en la sesión**: `ToolSearch` no devuelve ninguna herramienta `mcp__playwright__*`. Caída declarada al procedimiento por HTTP de `33-verificacion-automatizada-qa`: app levantada sobre un **segundo clon** (`C:/qaE5w`) y la base desechable `lp_e5http`, login real por POST a `/Account/Login` con antiforgery, asserts sobre el HTML servido y sobre la BD. El segundo clon existe para que los rebuilds del driver de mutación (sobre `C:/qaE5`) no choquen con el DLL que la app tiene tomado.

**Bases desechables**, las 7, armadas **siempre con `dotnet ef database update`** y nunca con `mysqldump --no-data` (regla de `LP-054`, adoptada): `lp_e5devol`, `lp_e5nc`, `lp_e5recon`, `lp_e5seis`, `lp_e5http`, `lp_e5vsf`, las 6 verificadas en **20 migraciones**. **Producción y `laplatense_dev` no se tocaron.** El repo del sistema es read-only: la mutación salió por `git archive HEAD` a `C:/qaE5`, con fidelidad probada por `diff` módulo CR (el archive queda en CRLF y el árbol de trabajo en LF; el contenido es idéntico).

## Cobertura por criterio de aceptación

| # | Criterio | Resultado | Evidencia observada |
|---|---|---|---|
| 1 | Devolución parcial de ítems facturados: reingresa stock, revierte la plata acotada a lo posteado, emite la NC | **PASS** | V1 (5 vendidas, 3 facturadas, 1 acreditada), `POST /Devoluciones/Registrar` de 2 → 302. BD: NC nueva `tipo3 Pendiente asoc=1 total=2420,00`; stock 1006→1008; mensaje *"Devolución #3 registrada. Se reingresó el stock de 1 ítem(s), se devolvieron $ 2.420,00 por caja, se emitieron 1 nota(s) de crédito."* |
| 2 | …y deja el **pendiente de facturar y el badge IDÉNTICOS** (R18/R19) | **PASS** | Antes: badge `('Confirmada', True)`, `Items[0].ACobrar = 2.000`. Después: badge `('Confirmada', True)`, `ACobrar = 2.000`. **Idénticos**, comparados por igualdad y no a ojo. |
| 3 | Devolución de ítems NO facturados: **no emite ningún comprobante** y queda completa | **PASS** | V6 (sin factura, efectivo): 302, `select count(*) from ComprobantesAfip where VentaId=6` → **0**. Mensaje sin mención de NC. |
| 4 | Devolución total → la venta pasa a `Anulada` | **PASS** | V6 → `Estado=3`; V7 → `Estado=3`; V10 tras devolución total → `Estado=3`. Neto vivo de caja de V6 = **0,00** exacto. |
| 5 | Devolución **parcial** → la venta **NO** cambia de estado (no hay flag "con devoluciones") | **PASS** | V1 tras devolver 2 de 5 → `Estado=4` (Confirmada). V8 tras devolver 2 de 4 → `Estado=4`. V10 tras devolver 1 de 3 → `Estado=4`. Y la migración **no agrega ninguna columna a `Ventas`** (verificado operación por operación). |
| 6 | No se puede devolver más que lo vendido menos lo ya devuelto, **por ítem**, validado en el Service | **PASS** | `POST` con 99 sobre 5 vendidas / 2 ya devueltas → 200, nada escrito (`count(Devoluciones)` igual antes y después), mensaje *"…vendieron 5 y quedan 3 por devolver; se pidieron 99. Ya hay 2 devueltas en devoluciones anteriores de esta venta."* Y un ítem de **otra** venta → *"uno de los ítems a devolver ya no pertenece a esta venta."* |
| 7 | `LP-052`: el GET sobre una NC **ya no devuelve 200 con formulario** | **PASS** | `GET /NotasCredito/Emitir/2` (es una NC) → **302** a `/Ventas/Details/1`, `form=0 boton=0 camposItems=0`. |
| 8 | `LP-052`: el GET sobre un comprobante en `Error` tampoco | **PASS** | `GET /NotasCredito/Emitir/3` (`Estado=Error`, pendiente 2) → **302**, `form=0`. |
| 9 | `LP-052`: el mensaje es **el mismo** en la vista, el GET y el POST | **PASS** | Comparación literal: el texto del GET para `Error` y para `ya acreditado` es **carácter por carácter idéntico** al `title` de la leyenda de `Ventas/Details`. Para "ya es una NC" la vista no muestra leyenda **a propósito** (`else if (!esNota)`), y es correcto: en una fila que ya es NC la acción no se ofrece. En devoluciones, el POST rechaza con *"La venta #6 está anulada: ya se le devolvió el stock y se le revirtió la plata entera, así que no hay nada que devolver."*, **idéntico** al que el GET deja en pantalla para V5. |
| 10 | `LP-052`: **no quedó una cuarta punta** con su propia copia de las condiciones | **PASS** | Grep de las 4 condiciones sobre todo el árbol: `EstadoComprobanteAfip.Error` aparece en 1 solo sitio de decisión (`HabilitacionDeAccion:105`); los 4 hits restantes son **display** (`"Sin emitir"`/`"Acreditado"`). `TodoAcreditado` sobrevive solo en 4 comentarios. Los 4 call-sites de `MotivoParaNoEmitirNotaCredito` son los 3 puntas + el planificador de NC, y **ninguno repite una condición**. Ver el residuo declarado más abajo. |
| 11 | Los tres criterios nuevos, **en el Service y en la UI** | **PASS** | (a) venta con devoluciones no se anula: POST rechaza con el texto exacto y `Estado` queda en 4; la vista **no renderiza** `<button id="btnAnular">` (preguntado por el TAG, no por el string). (b) ítem devuelto no se factura: `ACobrar` precargado = 2 sobre V8 (4 vendidas, 0 facturadas, 2 devueltas) — sin la resta daría 4. (c) comprobante con NC no recibe otra por lo mismo: `GET /NotasCredito/Emitir/4` → 302 *"ya está acreditado por completo"*. |
| 12 | Devolución imputada a un período de caja cerrado: rechazada (`LP-037`) | **PASS** | Con una fila en **`CierresCajaDiarios`** para hoy: 200, **0** devoluciones, **0** egresos de caja, **0** movimientos de stock, mensaje *"La caja del día 07/10/2026 ya está cerrada: no se puede registrar una devolución de la venta #10, que es de ese período."* **Control positivo**: se borra el cierre y la MISMA devolución entra (302, 1 devolución, stock +1). |
| 13 | El preview de lo que se va a revertir se muestra antes de confirmar, con los importes exactos y calculado por el **Service** | **PASS** | `POST /Devoluciones/Preview` devuelve el JSON del Service (`plata`, `totalDevuelto`, `recargoCuotasQueNoVuelve`, `notasDeCredito`). Y el eco es real: mi primer POST con `TotalARevertirConfirmado` vacío **fue rechazado** por la comparación. |
| B1 | Transición `Emitido → NC` | **BLOCKED — inalcanzable** | Sin certificado todos los comprobantes nacen en `Pendiente`. Sin cambio respecto del lote 1. |
| B2 | `CbtesAsoc` en el request de AFIP | **BLOCKED — inalcanzable** | `AfipComprobanteRequestDto` no lo tiene y nadie llama a `IAfipService`. Riesgo de liberación 1. |

## Los dos defectos propios del implementador: los dos verificados en la BD

**(a) El mismo producto en dos líneas de la misma venta.** Es el peor tipo de defecto de este proyecto y está cerrado. V6 con el producto 1 en **dos líneas** (1 y 3 unidades), devolución de las dos:

- `Producto.Stock` **1000,000 → 1004,000** (exactamente 1+3, no 3);
- el **ledger** suma `4,000` en **dos filas** (`Tipo=5/1,000/Devolucion/1` y `Tipo=5/3,000/Devolucion/1`) → **la columna y el ledger coinciden**;
- mutante propio: escribir el reingreso **por ítem** en vez de acumularlo por producto → **MUERTO**, tumba `3B.2`. Y el control negativo sobre la misma línea (`+ reingreso * 0m + reingreso`, que es un no-op) → **0 tumbadas**, así que el driver no está roto.

**(b) El recargo de cuotas en la devolución total.** V7, tarjeta en 6 cuotas al 10%: base 2000, recargo 200, la caja había posteado **2200**.

- egreso de caja de la devolución total = **2000,00** (la base), neto vivo = **200,00** = exactamente el recargo que la financiera ya cobró;
- el **preview lo avisa antes de confirmar**: `recargoCuotasQueNoVuelve: 200.00`;
- mutante propio: acotar la devolución total al **neto vivo** en vez de al remanente de la base → **MUERTO**, tumba `5.2` y `5.3`.

## La premisa de mi brief que era falsa: el implementador tenía razón

Mi brief anterior decía *"nunca escribas `Producto.Stock` directo: el proyecto tiene un único escritor y se respeta"*. **Es falso, y la dirección importa.** Verificado:

- `IMovimientoStockService.RegistrarMovimientoAsync` declara **explícitamente** que *"NO toca `Producto.Stock` y es a propósito: el stock del producto lo mueve el caller sobre la entidad que ya tiene cargada y trackeada"*;
- el proyecto tiene **5 escritores** de la columna, todos callers: `AjusteStockService:190`, `OrdenCompraService:925`/`945`, `VentaWorkflowService:843`/`966`/`1373`/`1487`. `DevolucionService:492` sigue la misma convención.
- **Obedecer el brief al pie de la letra dejaba el stock sin mover**, y está medido por la contraria: el stock se movió (1000→1004) y el ledger quedó consistente.

**Acción para el Diseñador funcional, no para el Implementador:** `2-disenador-funcional.md`, flujo 16, punto 1, dice *"por el ledger de stock (`MovimientoStock`), **nunca escribiendo `Producto.Stock` directo**"*. Esa frase es **falsa sobre este código** y es la que originó el desvío. Hay que reescribirla sobre el invariante real: *"el stock se mueve escribiendo la columna sobre la entidad trackeada **y** registrando la fila del ledger — las dos cosas, nunca una sola"*. Si no se corrige, el próximo que lea el diseño vuelve a tomar el camino equivocado.

## `LP-052` — CERRADO

Cerrado por las tres puntas y con la cuarta auditada. Lo que lo hace valioso no es que las tres rechacen, es que **rechazan con el mismo texto porque leen la misma función**:

| Condición | Mutante sobre `HabilitacionDeAccion` | Resultado |
|---|---|---|
| 1 — es una NC | `if (false && esNotaCredito)` | **MUERTO**, tumba `5.4` |
| 2 — está en `Error` (R17) | `if (false && estado == …Error)` | **MUERTO**, tumba `11.2`, `11.3`, `11.4`, `11.5` |
| 3 — ya acreditado por completo | `if (false && pendienteDeAcreditar <= 0)` | **MUERTO**, tumba `13.3` y `13.4` |
| control negativo | `if (esNotaCredito == true)` (no-op) | **0 tumbadas**, como corresponde |

**El residuo que queda, declarado y no bloqueante:** la *condición* se escribe una vez, pero su *entrada* `pendienteDeAcreditar` se calcula por **cuatro caminos independientes** — `FacturacionParcialService:520` y `VentaWorkflowService:1713` (subconsulta en la base, texto idéntico), `NotaCreditoDto.PendienteDeAcreditar` (`Items.Sum`) y el planificador de `DevolucionService:1121-1164`. El XML-doc de la clase lo declara fuera de alcance a propósito (*"la aritmética: estos métodos no calculan pendientes ni saldos, los reciben"*) y verifiqué que los cuatro coinciden en los casos probados (el GET abre con pendiente 2 y la vista ofrece el botón sobre el mismo comprobante). **Es la mitad del problema que el mecanismo no resuelve, y es correcto que no lo resuelva acá — pero el día que un lector se desincronice, las tres puntas van a seguir "leyendo la misma función" y decidiendo distinto.** Es el barrido de lectores, no este mecanismo.

**Y una afirmación del propio XML-doc que no se cumple en dos de sus tres consumidores** (`trivial`, anotado y sin parte): la clase dice que *"la **vista** oculta el botón cuando hay razón, **y la muestra como leyenda**"*. Para `MotivoParaNoEmitirNotaCredito` se cumple; para `MotivoParaNoRegistrarDevolucion` y `MotivoParaNoAnularVenta` la vista hace `@if (motivo == null) { botón }` **sin `else`**, así que el usuario ve desaparecer la acción sin saber por qué. No es un defecto de datos ni de seguridad: es la mitad que el propio comentario promete y que evita el ticket de soporte.

## `LP-053` — CERRADO, y la distinción "se mide por la razón, no por el dato" está bien hecha

Los tres criterios de re-verificación, arrancando en FAIL:

| Criterio de `LP-053` | Mutante | Resultado |
|---|---|---|
| (a) el filtro de `ListarComprobantesAsync` tiene que hacer fallar algo | `.Where(c => c.VentaId == ventaId)` | **MUERTO**, tumba `10.2` y `10.3` |
| (b) la guarda del comprobante en `Error` | `if (false && estado == …Error)` | **MUERTO**, tumba 4 afirmaciones de la familia 11 |
| (c) la cota `Math.Min(proporcional, remanente)` | `return proporcional;` | **MUERTO**, tumba `12.4` |

**Los tres criterios: MUERTOS los tres**, sobre línea base verificada en 63/63 antes de medir. Y la cota exigió buscarla: **ya no está en `NotaCreditoService`** — la fórmula se movió a `Domain/Reglas/CargoDeIvaDiferido.cs:92` porque desde este lote tiene dos consumidores. El ancla del criterio viejo da **0 hits**, y el driver se negó a medir en vez de inventar un resultado. Es el mismo agravante de `LP-056`: la cota ahora vive en `Domain`, así que el chequeo de "el mutante entró al binario" hay que hacerlo contra `Domain.dll`.

**La cuarta afirmación, la que no venía en el parte: la distinción es legítima y no es una excusa.** El mutante de `pendienteDeAcreditar <= 0` sobrevivía con 59/59 y el implementador declara que no era una afirmación vacía sino un **segundo mecanismo** (el tope por ítem frena igual, con otro mensaje). **Lo verifiqué por los dos lados, que es lo que separa una distinción de una coartada:**

- contra `ArnesNotaCredito`, el mutante **MUERE** y tumba `13.3` y `13.4` — la familia 13 es la que mide **la razón**;
- contra `ArnesDevoluciones`, el **mismo** mutante **SOBREVIVE** con 63/63 — que es exactamente lo que la declaración predice: ahí la condición la consume el planificador de NC, y el tope por ítem la domina.

Las dos mediciones juntas son la prueba. Si la afirmación nueva fuera débil, el mutante habría sobrevivido en los dos. **La distinción "se mide por la razón y no por el dato" está bien hecha**, y el agregado es una red real, no un relleno.

## Los 24 mutantes: no se pueden auditar de a uno, así que se sustituyeron

**El brief pide verificar que los 24 mutantes sean válidos. No es posible: `5-implementador.md` no los enumera** — declara el total (18 + 6), los tres sobrevivientes de la primera corrida y el inválido, pero no la lista. **Verificar la validez de un conjunto que no está escrito es inverificable, así que ese pedido queda BLOCKED.** Lo que sí hice, y es más fuerte: **21 mutantes propios derivados del DIFF**, con el conjunto construido sin mirar las afirmaciones de los arneses.

**Resultado: 15 muertos, 4 sobrevivientes y 2 controles negativos en cero tumbadas.** Los cuatro sobrevivientes tienen **tres causas distintas**, y separarlas es el trabajo:

| Mutante | Qué apaga | Veredicto |
|---|---|---|
| `D3` | la cota interna de la devolución **parcial** (`baseRemanente` → `neto`) | **RAMA DOMINADA, no es hueco.** `proporcional = Monto·(dev/total)` y `baseRemanente = Monto·(1 − devAnterior/total)`: con el mismo denominador, `proporcional ≤ baseRemanente` **por construcción**, así que el `Min` interno solo puede morder por redondeo de centavos, y el `Math.Min(pedido, neto)` final ya acota. Hice la aritmética de tres escenarios de dos parciales sucesivas sobre tarjeta con recargo y en los tres el mutante da **el mismo número**. **No publico parte: no es un defecto de plata.** Corresponde declararlo en el código como defensa en profundidad. |
| `H5` | `if (comprobantesVivos > 0)` de anular (la condición de `LP-039`) | **CUBIERTO EN OTRO ARNÉS.** Ver `LP-056`. |
| `H6` | `if (cantidadDevolvible <= 0)` | **RAMA DOMINADA.** Una venta devuelta por completo **siempre** queda `Anulada` (lo hace `RegistrarAsync`), así que la rama `Anulada` se evalúa primero y esta no es alcanzable por los servicios reales. Defensa en profundidad. |
| `F1` | la resta de lo devuelto en el **precargado** de `ACobrar` | **HUECO REAL → `LP-055`.** |

**Y una trampa de medición propia que vale escribir, porque casi me costó el informe:** mis nueve mutantes de `HabilitacionDeAccion` se declararon los nueve *"el DLL no cambió, la mutación no entró al binario"* y no se midieron. La causa: **`HabilitacionDeAccion` vive en `Domain`, no en `Infrastructure`**, y mi chequeo vigilaba `FerreteriaLaPlatense.Infrastructure.dll`. El chequeo falla-cerrado funcionó — se negó a medir en vez de reportar nueve falsos "sobrevive" — pero si lo hubiera escrito como un `warning` en vez de como un abort, el informe habría dicho que **ninguna** de las cuatro condiciones de `LP-052` tiene red. Está en `LP-056`.

**Segunda trampa propia, y es la de la memoria 12 otra vez:** al re-correr la serie con el chequeo arreglado, la **línea base dio 61/63** con el fuente limpio y `git status` limpio — porque restaurar el fuente **no actualiza el binario** y los arneses seguían corriendo el DLL del mutante anterior. El driver ahora **reconstruye al restaurar y exige que el md5 del DLL vuelva al valor limpio**, y aborta si la base no arranca en 0 falladas. Con eso la línea base volvió a 63/63 y toda la tabla de arriba se re-midió.

## Mi conteo de lectores del "ya facturado": **6**, el número declarado

Contado por mi cuenta, con un parser que **clasifica** en vez de contar hits sueltos (comentarios y copias a DTO aparte):

- **6 lectores del "ya facturado"** (`ComprobanteAsociadoId == null` como filtro de una suma): `DevolucionService:882` y `:1164`, `FacturacionParcialService:429` y `:495`, `VentaWorkflowService:172` y `:1732`. **Coincide con lo declarado.** (El commit cita `:806` y `:1061` para `DevolucionService`: son las líneas del XML-doc del método, no del filtro — mismo par de métodos.)
- **6 lectores del contrario** ("lo acreditado", `!= null`): `DevolucionService:901`, `:1139`, `:1156`, `FacturacionParcialService:475`, `VentaWorkflowService:184`, `:1751`.
- 1 uso de `!EsNotaCredito` en la vista, que es **agrupación para display** y no una suma (`Details.cshtml:297`), + 8 usos derivados y 18 copias a DTO / config de EF.

El contador subió 3 → 4 → 6 en tres rondas. **Los 3 que forman el pendiente se barrieron juntos en el mismo commit** y los tres están medidos por mutación (`F2` tumba `3.7` y `8.6`; `V1` tumba `8.12`; `V2` tumba `8.6` y `8.12`).

## Medición: los arneses

| Arnés | Declarado | Medido por QA | Veredicto |
|---|---|---|---|
| `ArnesDevoluciones` (nuevo) | 63/0 | **63 evaluadas, 63 OK, 0 FALLADAS, 0 NO MEDIDAS**, dos rondas seguidas sobre la misma base | **coincide, idempotente** |
| `ArnesNotaCredito` (45→63) | 63/0 | **63/63/0/0**, dos rondas | **coincide, idempotente** |
| `ArnesReconciliacionTx` | 153/0 | **153/153/0**, dos rondas | **sin regresión por el refactor de `AnularAsync`** |
| `ArnesSeisSitiosRestantes` | 32/0 | **32/32/0 + 2 NO MEDIDAS**, dos rondas | **coincide.** Las 2 NM son la precondición de concurrencia (`estado=Borrador`: la guarda optimista ganó), igual que en la corrida anterior. |
| `ArnesVentaSinFacturaYParcial` | **no declarado — no se corrió** | **82/82/0**, dos rondas | **verde, pero es el dueño de la condición que el lote movió** → `LP-056` |

Los 5 compilados **explícitamente** (`tools/` no está en la solución) y con los **md5 de `FerreteriaLaPlatense.Infrastructure.dll` idénticos** entre el proyecto y los 5 `bin/` antes de declarar cualquier número (trampa de `LP-041`).

## Migración

**Aditiva pura, confirmado operación por operación** con el patrón que incluye los métodos genéricos (`\.(\w+)(?:<[^>]*>)?\(`, sin el cual un `AddColumn<int>(` no matchea y la migración se lee mal):

- **`Up`: 9 operaciones** — 2 `CreateTable` (`Devoluciones`, `DevolucionItems`), 1 `AddColumn` (`ComprobantesAfip.DevolucionId`, **nullable, sin default**), 5 `CreateIndex`, 1 `AddForeignKey`. **Cero `Sql()`, cero `InsertData`, cero `UpdateData`, cero `AlterColumn`, cero `DropColumn`.**
- **`Down`: 5 operaciones**, simétrico.
- **4 FK nuevas**: `Devoluciones→Ventas` Restrict, `DevolucionItems→Devoluciones` Cascade, `DevolucionItems→ItemsVenta` Restrict, `ComprobantesAfip→Devoluciones` Restrict. La única sobre tabla preexistente es **nullable**, así que el código viejo inserta NULL y pasa.
- **`LP-050` N/A por AUSENCIA de backfill** (0 `Sql()` contados), no por razonamiento. **No está aplicada a `laplatense_dev` y es correcto**: es parte del deploy.
- **Ninguna columna nueva en `Ventas`**, consistente con la decisión de no tener flag "con devoluciones".

## Cobertura del catálogo cross-proyecto

| Ítem | Aplica | Resultado | Nota |
|---|---|---|---|
| `LP-052` (el botón guarda N condiciones y el GET guarda M) | sí | **PASS → CERRADO** | Las 3 condiciones en una función, 4 call-sites, mensaje idéntico verificado carácter por carácter, par discriminante con control positivo en 200 |
| `LP-053` (la matriz de mutación del autor hereda su punto ciego) | sí | **PASS → CERRADO** | 3 criterios + la cuarta afirmación verificada por los dos lados (muere en un arnés, sobrevive en el otro) |
| `LP-054` (base desechable por `mysqldump --no-data`) | sí | **PASS** | Las 7 bases por `dotnet ef database update`, 20 migraciones verificadas en cada una |
| `LP-039` (anular mira el estado y no los comprobantes) | sí | **PASS** | `POST /Ventas/Anular` sobre V1 (2 comprobantes vivos) rechaza nombrándolos; `ArnesVentaSinFacturaYParcial` 7.2 verde, y con el mutante reporta textualmente *"SE ANULÓ una venta con un comprobante fiscal vivo (es el defecto LP-039)"* |
| `LP-040` (el fix no barre el sitio hermano) | sí | **PASS** | Los 3 lectores del pendiente barridos juntos y los 3 medidos por mutación |
| `LP-037` (período de caja cerrado) | sí | **PASS** | Rechazo con 0 filas escritas + control positivo. **Ojo: el guard lee `CierresCajaDiarios`, no `CandadosPeriodoCaja`** — ver la trampa de medición abajo |
| `LP-041` (cada arnés tiene su propia copia del DLL) | sí | **PASS** | 5 md5 idénticos verificados antes de declarar números |
| `LP-002` (valor de enum nuevo sin propagar a sus lectores) | sí | **PASS** | `TipoMovimientoStock.Devolucion=5` leído en la BD (`Tipo=5`); `OrigenMovimientoCC` con los dos lectores de `CuentaCorriente.cshtml` propagados |
| `PAT-020` / `MH-027` (reversión acotada a lo posteado) | sí | **PASS** | Egreso 2000 sobre 2200 posteado. Y la guarda de MH-027 **se disparó de verdad** cuando mi fixture no tenía movimiento de caja identificable: *"1 pago(s) … no tienen un movimiento de caja identificable de forma exacta … Revertirlos a ciegas descuadraría la caja"* — falla cerrado, correcto |
| `PAT-059` (tope bajo concurrencia) | sí | **PASS** | Familia 11 del arnés: 4 devoluciones simultáneas de 2 unidades devuelven 2, no 8; stock +2; neto vivo 0 |
| `LP-034` (relectura decorativa si el producto se borra) | sí | **PASS** | Guarda presente en `DevolucionService:344`, falla cerrado |
| `LP-018` / `LP-035` (lock y orden canónico) | sí | **PASS** | `ArnesReconciliacionTx` 153/0 |
| `KOI-001` (botón fuera del form con SweetAlert) | sí | **PASS** | `btnAnular` vive fuera de todo `<form>` y arma el POST por JS |
| `LP-050` (backfill probado contra base con 0 filas) | **N/A** | — | Por ausencia de backfill, contada |
| `LP-046`/`LP-047`/`LP-048`/`LP-049` | no | — | Otros módulos |

## Validación de reglas cross-proyecto

`6-qa.md` declaraba **"Ultima validacion de reglas cross-proyecto: 2026-10-07"** (hoy). Verificado:
`git log --since=2026-10-07 -- .github/instructions/32-estandares-qa-implementador.instructions.md docs/qa/regresiones-manuales.yml` → **sin commits**. El índice de `32` y `cat_resumen.txt` coinciden con lo validado. **Ninguna regla nueva ni modificada desde la última validación.** Esta corrida agrega `LP-055` y `LP-056`: el catálogo pasa de 195 a **197 ítems**, sin duplicados (validado con `yaml.safe_load` + `Counter`), índice regenerado con `scripts/contexto.py resumenes`.

## Mis propias trampas de medición, declaradas

1. **`CandadosPeriodoCaja` no es la tabla del guard.** Sembré un candado ahí, el POST entró, y la firma era un **blocker**: *"una devolución se registró con la caja cerrada"*, con `LP-037` de fondo. El guard lee **`CierresCajaDiarios`**. Lo destapó leer cómo siembra el cierre la familia 9 del arnés, en vez de creerle a mi medición. **Un oráculo construido sobre la tabla equivocada produce un defecto perfecto y falso.**
2. **`"btnAnular" in html` no es oráculo.** Dio `True` sobre una venta con devoluciones y parecía que la vista seguía ofreciendo anular. El string vive también en el `<script>` que engancha el SweetAlert. El parser correcto saca los `<script>`, busca el **TAG** y pregunta por el `id` **sin fijar el orden de los atributos**; ahí da `False` en los 3 casos bloqueados y `True` en el control positivo (una venta limpia). Es la memoria 16 otra vez, en forma nueva.
3. **Dos premisas del propio brief refutadas al medir** (además de la del stock): los 24 mutantes no están enumerados, así que auditarlos de a uno es inverificable; y `D3`, que el brief sugiere como el riesgo del recargo, es una rama **dominada** y no un defecto de plata.

## Defectos

**De la corrida anterior:**

- **`LP-052` `major` → CERRADO.** Criterio de re-verificación cumplido arrancando en FAIL, por las tres puntas, con mensaje idéntico y par discriminante.
- **`LP-053` `low` → CERRADO.** Los tres criterios + la cuarta afirmación verificada por los dos lados.
- **`LP-054` `low` → CERRADO.** Adoptado como regla de método; las 7 bases de esta corrida se armaron así.
- **`LP-051` `trivial`** — fuera del alcance de este lote, sigue **ABIERTO**.

**Emitidos en esta corrida: 2, los dos `low` y los dos de red de medición. Ninguno de producto.**

### Parte de defecto `LP-055` `low` — el precargado de `ACobrar` no tiene red

- **Pasos:** línea base `ArnesDevoluciones` 63/63 → en `FacturacionParcialService.ObtenerFacturableAsync` cambiar `ACobrar = Math.Max(0m, item.Cantidad - facturada - devueltoSinNc)` por `ACobrar = Math.Max(0m, item.Cantidad - facturada)` → verificar que el md5 del `Infrastructure.dll` **del bin del arnés** cambió → correr.
- **Evidencia observada:** **63 evaluadas, 63 OK, 0 FALLADAS. El mutante sobrevive.** Que la rama es alcanzable y el mutante semánticamente real: `GET /FacturacionParcial/Emitir/8` (4 vendidas, 0 facturadas, 2 devueltas, 0 acreditadas) sirve `name="Items[0].ACobrar" value="2.000"` con el código sano; con el mutante serviría **4.000**, ofreciendo facturar mercadería que el cliente ya trajo de vuelta. Los otros dos lectores de la misma regla **sí** están medidos (`V1` tumba `8.12`; `V2` tumba `8.6` y `8.12`).
- **`archivos_fix` sugeridos** (hipótesis, no instrucción): `tools/ArnesDevoluciones/Program.cs` — una afirmación sobre el valor **precargado**, con un fixture donde `vendidas−facturadas` y `vendidas−facturadas−devueltas` sean números distintos.
- **`migracion_ef`:** ninguna.
- **Criterio de re-verificación:** neutralizar la resta de lo devuelto en el precargado de `ACobrar` hace **FALLAR** al menos una afirmación de `ArnesDevoluciones`. Hoy deja 63 OK / 0 FALLADAS.

### Parte de defecto `LP-056` `low` — el arnés dueño de la condición movida no está en el set de regresión

- **Pasos:** `grep -rn "Afirmar(" tools/*/Program.cs | grep -i anul` → aparece `tools/ArnesVentaSinFacturaYParcial` con `7.2`, `7.4` y `7.8`, que son la red de `LP-039`. No figura en la evidencia del lote, que declara `ArnesReconciliacionTx` y `ArnesSeisSitiosRestantes`.
- **Evidencia observada:** corrido, **82/82/0**, idempotente — **no hay regresión, el refactor está bien.** Que **es** la red: con `if (comprobantesVivos > 0)` neutralizado pasa a **77 OK / 5 FALLADAS** y `7.2` reporta *"SE ANULÓ una venta con un comprobante fiscal vivo (es el defecto LP-039)"*. El **mismo** mutante contra los dos arneses del lote **sobrevive con 63/63 en los dos**.
- **Agravante de medición, parte del mismo parte:** `HabilitacionDeAccion` se mudó a `Domain`, así que un chequeo de "la mutación entró al binario" escrito contra `Infrastructure.dll` descarta **los nueve** mutantes de la regla en silencio.
- **`archivos_fix` sugeridos** (hipótesis): `docs/la-platense/definiciones/5-implementador.md` — armar el set de regresión por `grep` sobre la condición movida, no por los archivos editados.
- **`migracion_ef`:** ninguna.
- **Criterio de re-verificación:** por cada condición que un diff **mueva** de un archivo a otro, el set de regresión declarado incluye todos los arneses que la afirman, enumerados por `grep`; y el chequeo de "el mutante entró al binario" usa el DLL del **proyecto del archivo mutado**.

## Lo que el lote declara como no limpio: mi juicio

- **`trazas.tsv`: estructuralmente SANO.** Medido sobre los bytes: 101 `CRLF` + 3 `LF` sueltos, que son las 3 filas que `traza.py` agregó en esta tanda (el script escribe `\n` y el archivo histórico es `\r\n`; `git` lo normaliza y avisa). **Cada fila tiene exactamente 9 campos**, incluida la degenerada. La fila vacía (`2026-10-07 la-platense implementacion - 0 - - - -`) **está y es válida estructuralmente**, solo vacía de contenido. **El implementador hizo bien en dejarla**: `traza.py` no tiene modo reemplazar y arreglarla a mano es lo que me costó una corrida. *(Mi primer conteo dio "una fila con 25 campos" — artefacto de partir solo por `CRLF` cuando hay `LF` sueltos. No era el archivo, era mi parser.)*
- **`.ov-monto`: queda ANOTADO como deuda, sin parte.** La clase está definida (`olvidata-theme.css:1352`) y la usan **5 vistas**: las 2 nuevas de devoluciones, `Ventas/Details` y 2 de órdenes de compra. Hay ~23 vistas con columnas de importe que no la usan. **No emito parte**: la clase es aditiva y no rompe nada, el lote **no creó** la deuda (cerró parte de ella), y mandar a retocar 23 vistas no relacionadas en el lote de cierre de un alcance financiero tiene más riesgo de regresión que beneficio cosmético. Va al backlog del design system.

## Riesgos de liberación

1. **AFIP real (el único gate que queda).** La NC nace en `Pendiente` sin CAE, y `AfipComprobanteRequestDto` **no tiene `CbtesAsoc`**, que la instruction 34 exige para emitir una NC. Hoy inalcanzable porque nadie llama a `IAfipService`. **Mitigación:** es el residual del módulo 6 y está declarado en `3-arquitecto-mvc.md` v14.
2. **La asimetría del comprobante en `Error`, ya registrada y no re-reportada.** `ObtenerYaFacturadoPorItemAsync` **sí** cuenta los comprobantes en `Error` y el planificador de NC **no**: el día del certificado, un ítem facturado en un comprobante fallido aparecería como facturado en el pendiente y no generaría NC al devolverse. Hoy inalcanzable. **Es condición de entrada del residual del módulo 6.**
3. **La ventana código-viejo / esquema-nuevo del deploy.** Esta migración es más benigna que la tanda anterior (la única columna sobre tabla preexistente es nullable y su FK también), pero la condición del GO del deploy anterior sigue valiendo: base y sitio en la misma ventana.
4. **El `pendienteDeAcreditar` se calcula por 4 caminos** (ver el residuo de `LP-052`). No es un defecto hoy; es el próximo lugar donde esta familia puede reaparecer.
5. **Dos ramas de defensa en profundidad sin red, por dominación** (`D3`, `H6`). No son defectos: conviene **declararlas en el código** para que la próxima corrida mutante no las vuelva a investigar desde cero.

## ¿Queda algo que no deba liberarse al usuario?

**No. Nada de este lote queda fuera del alcance del usuario.** Las devoluciones (listado, registrar, preview), la emisión de notas de crédito y los tres criterios de habilitación están completos, probados por pantalla y por BD, y se pueden liberar. Los dos defectos que emito son de **red de medición** (arneses y proceso), no de producto: no cambian lo que el usuario puede hacer ni lo que el sistema escribe. **"Confirmar y facturar" del POS sigue OCULTO** y verificado así por HTTP sobre un borrador real (ausente del DOM, con "Confirmar venta" presente) — está gateado por `afipConfigurado`, que es el mismo guard server-side.

**Con esto el alcance comprometido de la Entrega 5 queda completo salvo AFIP real**, que espera el certificado del cliente y es un gate externo, no una deuda del código.

## Checklist de salida para merge

- [x] `LP-052` CERRADO con evidencia ejecutada por las tres puntas, arrancando en FAIL
- [x] `LP-053` CERRADO, con la cuarta afirmación verificada por los dos lados
- [x] `LP-054` adoptado: las 7 bases por `dotnet ef database update`, 20 migraciones cada una
- [x] Los 13 criterios del lote en PASS con evidencia observada; 2 BLOCKED por inalcanzables (AFIP)
- [x] Los 2 defectos propios del implementador verificados en la BD (stock 1000→1004 en dos filas del ledger; egreso 2000 sobre 2200 posteado)
- [x] Build `--no-incremental` de la solución: **0 errores / 9 advertencias**, línea base exacta
- [x] 5 arneses verdes e idempotentes (63 + 63 + 153 + 32 + 82 = **393 afirmaciones**, 0 falladas), los 5 compilados explícitamente y con los md5 del DLL verificados
- [x] 21 mutantes propios derivados del diff: 15 muertos, 4 sobrevivientes explicados, 2 controles negativos en 0
- [x] Migración aditiva pura verificada operación por operación (`Up`: 9 ops, cero `Sql`/`AlterColumn`/`DropColumn`)
- [x] Conteo independiente de lectores del "ya facturado": **6**, coincide con lo declarado
- [x] `trazas.tsv` estructuralmente sano (9 campos por fila)
- [x] `git status --porcelain` limpio en el repo del sistema
- [x] Producción (8 migraciones) y `laplatense_dev` (18) **no se tocaron**
- [ ] **Corregir `2-disenador-funcional.md` flujo 16 punto 1**: *"nunca escribiendo `Producto.Stock` directo"* es falso sobre este código y originó el desvío ← Diseñador funcional
- [ ] `LP-055` y `LP-056` — red de medición, no bloqueantes del merge ← Implementador
- [ ] `LP-051` `trivial` — pendiente de otro lote
- [ ] **AFIP real + `CbtesAsoc`** ← gate externo, espera el certificado

**Veredicto del lote: GO PARA MERGE.** El mecanismo de `HabilitacionDeAccion` es la decisión correcta y está medido: es la primera vez en este proyecto que la familia `LP-039`/`LP-040`/`LP-052` se cierra con **una** definición en vez de con un parche más, y el mensaje idéntico en las tres puntas lo prueba por ejecución y no por lectura. Los dos defectos que emito son de la red que mide, no del sistema que se libera.

---



---

---


## Historial de ajustes

**Archivado el 2026-10-08 por curaduria a mano** (los headings de nivel 1 de este archivo no los reconoce `archivar_memoria.py`, asi que la decision de que ya es historia la tomo el orquestador). Los tres bloques estan completos en `historial/`, sin resumir:
- **2026-10-07** — Modulo 16 - notas de credito por comprobante (2026-10-07, GO para merge con `LP-052` abierto en su momento) → [`6-qa-modulo-16-notas-credito.md`](historial/6-qa-modulo-16-notas-credito.md)
- **2026-10-07** — Barrido de `Activo` + cierre de `LP-044`/`LP-045`/`LP-049` + estado de `dev` migrada (2026-10-07) → [`6-qa-barrido-activo-lp044-lp045-lp049.md`](historial/6-qa-barrido-activo-lp044-lp045-lp049.md)
- **2026-10-07** — Cierre de `LP-050` - ensayo del backfill contra los datos reales de produccion (2026-10-07) → [`6-qa-cierre-lp050-backfill-produccion.md`](historial/6-qa-cierre-lp050-backfill-produccion.md)

### Bloques archivados (2026-10-07, tercera tanda)

- **`CR-04` plan de echeqs + cierre de `LP-044`..`LP-048`** y **`CR-05` + `CR-03` + cierre de `LP-042` y
  `LP-043`** -> [`6-qa-2026-10-07-cr04-cr05-cr03.md`](historial/6-qa-2026-10-07-cr04-cr05-cr03.md). Movidos a
  mano al cerrar la Entrega 5 lote 2 (el archivo habia llegado a 158 KB y `archivar_memoria.py` no reconoce
  los headings de este archivo). Las dos corridas estan CERRADAS; sus defectos siguen en el catalogo.


### Bloques archivados (2026-10-07, segunda tanda)

- **`LP-039` - re-verificacion de cierre (2026-10-06, commit `f05cc92`)** y **Entrega 5 - venta sin factura (CR-01) + facturacion parcial (CR-02) - QA lote unico (2026-10-06)** -> `historial/6-qa-2026-10-06-lp039-y-entrega5.md`. Movidos a mano al cerrar la corrida del barrido de `Activo` (`archivar_memoria.py` no reconoce los headings de este archivo). Las dos corridas estan CERRADAS; `LP-039` y `LP-040` siguen en el catalogo cross-proyecto.

### Bloques archivados (2026-10-07)

- **HOTFIX de transacciones de ventas - gate de publicacion (2026-10-06, rama `hotfix-transacciones-ventas`, GO)** y
  **Entrega 6 LOTE 5 - presupuestos en PDF y aumento masivo de precios (2026-10-06, NO-GO)** ->
  `historial/6-qa-2026-10-06-hotfix-y-entrega6-lote5.md`. Se movieron al cerrar la corrida de `CR-03`/`CR-05`,
  cuando el archivo llego a 152 KB. Las dos corridas estan CERRADAS; sus defectos (`LP-029`, `LP-030`, `LP-031`,
  `LP-032`, `LP-033`, `LP-034`) siguen en el catalogo cross-proyecto.

### Bloques archivados (2026-10-06)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-10** — 1 bloques (2026-10-06 a 2026-10-06) → [`6-qa-2026-10-4.md`](historial/6-qa-2026-10-4.md)
