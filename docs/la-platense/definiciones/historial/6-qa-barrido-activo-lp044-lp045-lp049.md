# Historial de QA - La Platense

Bloque archivado desde `6-qa.md` el 2026-10-08 por curaduria a mano (39 seccion 6: el techo se sostiene archivando, no reescribiendo). El texto esta completo y sin resumir.

---

# Barrido de `Activo` + cierre de `LP-044`/`LP-045`/`LP-049` + estado de `dev` migrada — QA lote de cierre (2026-10-07, rama `entrega-1-migracion`, commits `0624133`..`fcfa077`)

## **GO para merge. NO-GO para el deploy a producción tal como está planteado hoy**, y la razón es una sola y se puede cerrar con un ensayo de media hora: ver `LP-050`. Los 6 criterios del lote en PASS con evidencia ejecutada. **Los 3 partes cierran** (`LP-044`, `LP-045`, `LP-049`). **El riesgo 1 de la corrida anterior (`MigracionCatalogo`) queda cerrado.** 2 defectos nuevos: `LP-050` `major` (hueco de verificación del deploy, no de código) y `LP-051` `trivial`.

Contexto fresco: no se leyó la transcripción del implementador, sólo el bloque `v27` de `5-implementador.md`, los 4 mensajes de commit y el diff (`git diff e2da786..fcfa077`, 17 archivos / 1.183 inserciones).

## Entorno y metodología

Árbol extraído con `git archive HEAD` al scratchpad (**el repo del sistema nunca se tocó**; `git status --porcelain` → sólo `?? .claude/`, preexistente, verificado al abrir y al cerrar, HEAD `fcfa077`). Build reproducido: **0 errores / 9 advertencias = 8 `NU1902` + 1 `CS0114` en `HomeController.cs(38,26)`**, línea base exacta, la corrección de la corrida anterior confirmada. Clon de `laplatense_dev` (ya en 18 migraciones) → `laplatense_qa_act`, app levantada en `https://localhost:7788` con la cadena por variable de entorno. Bases auxiliares: `laplatense_qa_sent` (centinela de la guarda), `laplatense_arn8_*` (los 7 arneses, borradas al cerrar).

**El MCP de `playwright` NO estaba cargado en la sesión** (no aparece ninguna `mcp__playwright__*`). Se declaró y se cayó al procedimiento HTTP sobre el **HTML servido** con `curl -k` + cookie jar: para los criterios de este lote eso es equivalente y más preciso que el navegador, porque lo que decide cada criterio es qué `<option>` sale en la respuesta y qué mensaje vuelve en el `validation-summary` — se mide sobre lo que el usuario recibe, no sobre el `.cshtml`.

**Trampa de medición propia, declarada porque casi cuesta un parte falso:** el primer parse de los combos usó el regex `<option value="(\d*)"` y dio **AUSENTE** para los tres catálogos inactivos asignados, con toda la pinta de un defecto `major` de corrupción silenciosa. El tag helper emite `<option selected="selected" value="129">`: **`selected` va ANTES de `value`**, así que el regex no matcheaba la única option que importaba. Lo que lo destapó fue leer el código (`PoblarCombosAsync` ya tenía el re-agregado) en vez de creerle a la medición. Re-medido con un parser agnóstico al orden de atributos: los tres combos están bien. **Un parse de HTML con regex posicional no sirve como oráculo de un criterio; el parser tiene que ser agnóstico al orden de los atributos.**

## Cobertura por criterio — evidencia al lado de cada PASS

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| **No se puede CREAR un producto con marca, categoría o modelo inactivos — verificado por POST** | **PASS** | `POST /Productos/Create` con `MarcaId=129` / `ModeloId=2` / `CategoriaId=17` (los tres `Activo=0`): **HTTP 200 sin redirect** (formulario repintado) y los **tres** mensajes en el `validation-summary`, uno por catálogo y nombrando cada uno: *"La marca \"ZZQA Marca Baja\" está dada de baja: no se puede asignar a un producto…"*, ídem modelo y categoría. En BD: `select … where Codigo like 'ZZQA-POST%'` → **0 filas**. Sin el fix esto devolvía *"Producto creado correctamente"* y dejaba la fila. |
| **No se puede EDITAR un producto MOVIÉNDOLO a un catálogo inactivo distinto del asignado** | **PASS** | `POST /Productos/Edit` sobre el producto 112507 (marca asignada 129) con `MarcaId=130` (otra marca `Activo=0`): HTTP 200, *"La marca \"ZZQA Marca Baja 2\" está dada de baja…"*, y en BD `MarcaId` **sigue 129** y `PrecioCompra` sin cambiar. |
| **EL CRITERIO QUE MÁS IMPORTA: un producto que YA tiene un catálogo dado de baja sigue siendo editable y guardable** | **PASS, por los dos lados** | **(a) Service:** `POST /Productos/Edit` del 112507 conservando `MarcaId=129` → **HTTP 302 → /Productos**, y en BD `PrecioCompra 100 → 111` con `MarcaId=129` intacto. **(b) UI — y es la mitad que hace alcanzable al (a):** el `GET /Productos/Edit/112507` sirve **`<option selected="selected" value="129">ZZQA Marca Baja</option>`** (130 options = 129 activas + la re-agregada). Ídem `Edit/112508` → `<option selected value="17">ZZQA Categoria Baja` (18 options) y `Edit/112509` → `<option selected value="2">ZZQA Modelo Baja` (3 options). Los tres con `selected`, así que el navegador no puede auto-elegir otro. |
| **La baja lógica sigue sacándolos del combo** | **PASS** | `GET /Productos/Create`: las ZZQA activas aparecen (`131` Marca Activa, `3` Modelo Activo, `18` Categoría Activa) y las tres inactivas (`129`, `2`, `17`) están **AUSENTES**. El combo de alta no ofrece ninguna de baja. |
| **EL HALLAZGO DEL BARRIDO: el combo de Editar una compra re-agrega el proveedor asignado aunque esté de baja — la asimetría del `:653` ahora es alcanzable por la UI** | **PASS** | Borrador #9950 con `ProveedorId=1` (SIBON), puesto en `Activo=0`. `GET /OrdenesCompra/Edit/9950` sirve **`<option value="1" selected="selected">SIBON</option>`** entre 86 options, **con** placeholder vacío presente. Y el circuito completo: `POST` conservando el proveedor 1 → **302 → /Details/9950** y en BD `NotaInterna='ZZQA editado con proveedor de baja'` escrita con `ProveedorId=1`; `POST` moviéndolo al proveedor 114 (otro `Activo=0`) → **HTTP 200** con *"El proveedor ZZQA Prov Baja está inactivo: no se puede asignarle esta compra."* y la BD sin cambiar. **Antes del fix el borrador era inmodificable** (combo en el placeholder, `ProveedorId` es `int` no nullable). |
| **El sistema levanta y opera contra `dev` ya migrada (ensayo del deploy)** | **PASS** | 21 pantallas por HTTP: **todas 200, cero página de error, cero `[ERR]`/`[FTL]` en el log**. Y los **13 endpoints de DataTables** posteados con antiforgery, los 13 en 200 con datos reales: Productos **112.488**, Stock 112.488, Clientes **2.993**, Ventas 12, Caja 9, ÓrdenesCompra 1, Proveedores 85, Gastos 3, Cierres 1, Mensual 1, Consolidado 9, Entregas 3, Presupuestos 0. Ventas/Caja/Compras/CC rinden contra el esquema de 18 migraciones sin una excepción. |

## Los tres partes: los tres CIERRAN

- **`LP-049` — CERRADO.** Par de control sobre un clon con **una fila ajena de cada cosa** sembrada por SQL con prefijo `QAJENO` (proveedor + `OrdenCompra` + `PagoOrdenCompra` + `MovimientoCCProveedor` + `CajaMovimiento` `PagoOC`): el arnés arranca con `foto base: compras=1, pagos=1, movsCC=1, movsCajaPagoOC=1` y cierra **92 OK / 0 FALLA**, exit 0, `delta 0` en los cuatro — donde antes del fix una sola fila ajena lo pasaba de `TODO OK` a `1 FALLA`. **Control positivo:** mutante con el borrado de `CajaMovimientos` desactivado → **91 OK / 1 FALLA**, exit 1, *"[FALLA] no quedan filas de prueba (DELTA contra la foto base…) — movsCajaPagoOC=2"*. La afirmación se **acotó**, no se neutralizó.
- **`LP-045` — CERRADO.** Barrido por patrón re-ejecutado de forma independiente: **52 `switch` (expression + statement) en el árbol y los 52 tienen rama de descarte** (`_ =>` 50 + `default:` 2) en 34 archivos — o sea no existe en el repo un `switch` exhaustivo, y cualquier comentario que lo afirme es falso por construcción. Los **11 comentarios** que tocan el tema (`xhaustiv`, `CS8509`, `sin _ =>`, `denuncia el compilador`, `absorba lo desconocido`) se verificaron uno por uno contra el `switch` del que hablan: los 11 son correcciones que **citan la afirmación falsa y la desmienten en la misma oración**, o inventarios por miembro correctos. **Cero afirmaciones falsas vivas.** Único residuo, y NO es falso: `Application/Helpers/OrigenCCEmpleado.cs:93` usa la palabra *"exhaustivo"* sobre un `switch` con `_ => false` cuatro líneas abajo — pero en la misma oración admite que el valor nuevo cae al descarte, no menciona `CS8509` y no afirma que el compilador avise. Es uso impreciso del adjetivo (lista todas las constantes de `Todos`), no una afirmación falsa. Se deja nombrado porque es lo que el grep de `xhaustiv` va a seguir levantando.
- **`LP-044` — CERRADO, y el criterio de re-verificación que dejó esta memoria estaba MAL ESCRITO.** El criterio decía: `grep -n "lo saca el parser" InteresesTarjeta.cshtml` devuelve **0 líneas**. Devuelve **1** (línea 236). Pero esa línea es *«esta linea decia "un `<form>` hijo de `<tr>` lo saca el parser", que es LA MISMA AFIRMACION FALSA…»* — o sea la cita que la refuta. **El criterio es inverificable como estaba redactado**, porque el fix correcto consiste justamente en citar la frase para desmentirla: un grep literal no puede distinguir la afirmación de su refutación. Se reescribe sobre el invariante y se cierra contra el criterio nuevo (ver abajo). Chequeo estructural de las 3 variantes sobre las **84 vistas**: **0 / 0 / 0** — cero `<form>` con padre directo `<table>`/`<thead>`/`<tbody>`/`<tr>` (los únicos forms dentro de una tabla tienen padre `<div>`), cero forms sin su `</form>` en la misma iteración (los 5 desbalances de un `grep -c` crudo son menciones dentro de comentarios, verificadas tag por tag), cero `form="…"` apuntando a un id inexistente (los 7 usos de `form=` del árbol correlacionan 1:1 por construcción, generados en el mismo `@foreach`).

### Criterio de re-verificación de `LP-044`, reescrito (reemplaza al grep literal)

> Ningún comentario del árbol afirma, **en su propia voz y fuera de una cita que explícitamente la desmiente**, que un `<form>` hijo de `<tr>` lo saca el parser, deja los inputs huérfanos o postea una fila vacía. Verificación: por cada hit de `grep -riE "saca el parser|huerfan|fila vac|parser descarta|form anidado"`, clasificar el hit en *afirma* / *cita y refuta* / *otro sentido* (FK, datos), y exigir **cero** en *afirma*. Hoy: 9 hits, 0 en *afirma*.

## `MigracionCatalogo` (riesgo 1 de la corrida anterior): CERRADO, medido por ejecución en los dos sentidos

**17 abortos verificados por exit code, no por lectura.** Sin la variable de entorno, **los 4 modos** (carga inicial, `--solo-codigo-barras`, `--solo-codigo-propio`, `--solo-unidad-venta`) → **exit 3**, *"ABORTADO: no hay base de destino… Este script NO tiene destino por defecto a propósito"* — donde antes escribía `dev` en silencio. Cadena sin `Database=` → **exit 3**. Apuntando a `laplatense_dev`, los 4 modos → **exit 2**. Apuntando al **nombre de la base de producción** `db_a7251f_laplaten` (host falso, nunca conecta), los 4 modos → **exit 2**. Apuntando al **host** `mysql8001.site4now.net` con otro nombre de base → **exit 2**. La guarda cubre las dos claves y corre **antes** del `DbContext`.

**Y el sentido contrario, que es el que prueba que la guarda es lo único que frena:** base `laplatense_qa_sent` (clon de `dev`, nombre prohibido por substring `laplatense_qa`) con **5 productos centinela en `UnidadVenta=Metro`**. Sin confirmación → exit 2, **centinela intacto (5 Metro)**. Con confirmación **equivocada** (`MIGRACION_CATALOGO_CONFIRMO_BASE=laplatense_dev` contra un destino que es `laplatense_qa_sent`) → exit 2, **centinela intacto** — compara el nombre exacto, no la presencia de la variable. Con la confirmación **exacta** → exit 0 y **escribe**: *"UnidadVenta corregida (Metro -> Unidad): 5"*, centinela **5 → 0 Metro**.

**Los 6 arneses, también por ejecución:** sin la variable → **exit 2** en los 7 (*"ABORTADO: falta `ConnectionStrings__DefaultConnection` y este arnés NO tiene base por defecto (a propósito)"*); con `db_a7251f_laplaten` y con `laplatense_dev` → **exit 2** en los 7. No se creó ninguna base por default (`laplatense_item4c`, `laplatense_cr12` no existen) y `laplatense_dev` quedó intacta. **Nota menor de convención, no defecto:** `MigracionCatalogo` distingue exit 3 (base indeterminable) de exit 2 (base prohibida); los arneses usan 2 para los dos casos.

## No-regresión: los 7 arneses, con `md5` verificado y dos corridas cada uno

`md5` de `FerreteriaLaPlatense.Infrastructure.dll` **idéntico en los 8 directorios** (`d80ab540a2af4d069f5ac119590f8395`) antes de declarar un solo número, y cada arnés compilado explícitamente (`tools/` no está en la solución). Cada uno sobre su propia base clonada de `dev`, **dos corridas seguidas**, en **afirmaciones evaluadas**:

| arnés | corrida 1 | corrida 2 | línea base |
|---|---|---|---|
| `ArnesPlanEcheqs` | 49 OK / 0 / **49** | idéntica | = 49 |
| `ArnesTarjetaYTransferencia` | 41 / 0 / **41** | idéntica | = 41 |
| `ArnesSeisSitiosRestantes` | 32 / 0 / **32** (+2 NM) | idéntica | = 32 + 2 NM |
| `ArnesReconciliacionTx` | 153 / 0 / **153** | idéntica | = 153 |
| `ArnesVentaSinFacturaYParcial` | 82 / 0 / **82** | idéntica | base nueva: 82 |
| `ArnesEntrega3Item4c` | 92 / 0 / **92** | idéntica | = 92 post-fix |
| `ArnesBarridoActivo` (nuevo) | 26 / 0 / **26** | idéntica | = 26 |

Exit 0 en las 14 corridas, ningún total bajó, ninguno cayó a `0 OK / 0 FALLADAS`: **limpieza completa en los 7**. Con esto quedan reproducidas las líneas base de `LP-037`, `LP-039`..`LP-043`, `LP-046`..`LP-049`, CR-01..CR-05 y el barrido nuevo.

**Observación de instrumento (`low`, no es parte):** `ArnesVentaSinFacturaYParcial` imprime `OK: 82  FALLADAS: 0` en vez del formato `=== N afirmaciones EVALUADAS … NO MEDIDAS ===` de los otros seis, así que no se puede distinguir una afirmación salteada de una ausente. Es la forma de `LP-042` sin el agravante: el total coincide con la base.

## Estado de `laplatense_dev` migrada: verificado de forma independiente

**18 migraciones** (`select count(*) from __EFMigrationsHistory` → 18; las 4 últimas son `CR04_PlanDeEcheqs`, `CR03_TarjetasEInteresPorCuotas`, `EntregaCinco_CandadoPeriodoCaja`, `EntregaCinco_VentaSinFacturaYComprobantesParciales`). **Conteos idénticos: 112.485 productos / 2.993 clientes / 0 órdenes de compra.** Las **6 tablas nuevas** presentes y las 6 **en 0 filas** por conteo real (no por `table_rows`): `ComprobantesAfip`, `ComprobantesAfipItems`, `CandadosPeriodoCaja`, `Tarjetas`, `InteresesTarjetaCuota`, `LineasEcheq`. Único resto de esquema: `_bk_unidadventa_20261005`, el respaldo conocido — **dev no tiene deriva**. Backup previo **existe y no está truncado**: 35.201.075 bytes (35,2 MB) y la última línea es `-- Dump completed on 2026-10-07  7:59:12`.

**Las 18 migraciones barridas una por una separando `Up` de `Down`** (con los métodos genéricos en el regex: `AddColumn<int>(` no matchea `\.(\w+)\(`): **13 aditivas puras**, 5 con `Sql()`/`AlterColumn`/`RenameColumn` en el `Up`. Las 4 que se aplicaron a dev en este tramo son **aditivas puras confirmadas**: `Up` = sólo `CreateTable`/`CreateIndex`/`AddColumn`, y los `Drop*` los 4 enteros en el `Down`.

## La decisión de NO tocar `CCProveedorService` / `CCEmpleadoService`: **CORRECTA**, y por una razón más fuerte que la declarada

Verificado: **ninguno de los dos servicios menciona `Activo` una sola vez**, y el único chequeo sobre el proveedor es de existencia (`FirstOrDefaultAsync(p => p.Id == dto.ProveedorId)`, `CCProveedorService:314`). Medido en vivo con el proveedor 1 en `Activo=0`: `/Proveedores/CuentaCorriente/1` → **200** con SIBON en pantalla, `/Proveedores/RegistrarAjuste/1` → **200** con `ProveedorId` ya resuelto y SIBON nombrado. La cuenta de un proveedor dado de baja **se puede liquidar**.

El argumento del implementador (bloquearlo sería el error de su mutante M2) es correcto pero incompleto. **La razón decisiva es que en las CC no hay nada que proteger:** la asimetría de `LP-047` existe para impedir *asignar* un catálogo de baja a un registro, y un movimiento de cuenta corriente **nunca asigna** un proveedor — lo resuelve de la ruta (`/RegistrarAjuste/{id}`), sobre el ledger de un proveedor que por definición ya existe, y no hay ninguna operación de "mover esta CC a otro proveedor". No hay combo, no hay elección, no hay caso nuevo. Agregar la guarda ahí no cerraría ningún agujero y rompería la liquidación de una deuda ya contraída, que es peor que el defecto que vendría a prevenir. **Decisión aprobada.**

## El barrido de `Activo`: ¿queda una cuarta? **NO**, y se verificó por enumeración

Las **9 declaraciones** de `bool Activo` del dominio, con el veredicto de cada una:

| entidad | superficie que asigna por id | estado |
|---|---|---|
| `ICatalogoSimpleEntity` | — (interfaz) | N/A |
| `Marca`, `Modelo`, `Categoria` | combo de alta/edición de Producto | **cerrado en `fcfa077`**, medido arriba |
| `Proveedor` | combo de alta/edición de compra | `OrdenCompraService:653` (preexistente) + combo alcanzable desde `fcfa077`, medido arriba |
| `Tarjeta` | combo de pago de venta | cerrado en `LP-047` |
| `RecargoCuota` | **ninguna** — se resuelve por `Cuotas` (el número de cuotas), nunca por `Id` desde un combo | sin superficie |
| `CodigoBarrasProducto`, `CodigoProveedorProducto` | **ninguna** — filas hijas propias de un Producto, creadas en su propio formulario, no elegidas de un combo | sin superficie |

Y el camino que podría volver INEDITABLE a un producto está cerrado por diseño: `MarcaService.EliminarAsync` **soft-deletea en cascada los productos de la marca**, así que una marca borrada no deja detrás un producto editable que caiga en la rama *"la marca seleccionada no existe"*.

## Defectos nuevos

| id | Sev. | Qué es |
|---|---|---|
| **`LP-050`** | **major** | **Hueco de verificación del deploy, no de código.** 4 de las 18 migraciones hacen *backfill de datos* en el `Up` con `UPDATE` sobre filas que ya existen; ninguna lo revierte en el `Down`; y el único entorno donde se aplicaron tiene **cero filas del tipo afectado**. El backfill nunca corrió donde tiene trabajo que hacer. |
| **`LP-051`** | trivial | Tercera iteración de `LP-044`/`LP-045` en el mismo archivo: el comentario que promete *"aca no se repite para no tener dos copias que se desincronicen"* repite el mecanismo completo **dos líneas arriba**. La afirmación falsa es sobre el propio archivo, así que un barrido semántico de la familia no la ve. |

### `LP-050` en detalle — es la única razón del NO-GO de producción

Las 4 migraciones con `Sql()` en el `Up`, con el SQL extraído:

- `20261005221747_LedgerCaja_Identidad_MedioPago_AnulacionVenta` — **6 `UPDATE` sobre `CajaMovimientos`**: `EsReversion`, `MedioPago` (dos veces), `PagoVentaId`, `UsuarioId` (dos veces). **El tercero clasifica el medio de pago con `Descripcion LIKE '%(Efectivo)%'` / `'%(Debito)%'` / `'%(CreditoCuotas)%'` y `ELSE NULL`**: es una heurística sobre texto libre, y toda fila que no matchee queda en `MedioPago = NULL`. El cuarto `UPDATE` **depende** de que `MedioPago` no sea `NULL` para resolver `PagoVentaId`, así que una falla del tercero se propaga en silencio.
- `20261005231651_EntregaTres_ProveedoresCCCompras` — `UPDATE Proveedores SET Moneda = 1 WHERE Moneda = 0` (85 proveedores en dev).
- `20261006011819_EntregaTres_MonedaCompraYPagosProgramados` — 2 `UPDATE` sobre `OrdenesCompra` (prod tiene 0: no-op).
- `20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio` — `UPDATE CajaMovimientos SET Fecha = DATE_ADD(Fecha, INTERVAL 3 HOUR)`.

**Ninguno de los cuatro `Down` revierte el `UPDATE`** (sólo tienen `DropTable`/`DropColumn`): el backfill es **irreversible por migración**, el único rollback es restaurar.

**Y acá está el punto.** En `laplatense_dev` hay hoy **9 `CajaMovimientos`, 13 `Ventas`, 3 `Gastos`, 0 `OrdenesCompra`** — y esas filas las creó un arnés **después** de la migración. Los 6 `UPDATE` del ledger corrieron sobre **cero filas**. Producción, en cambio, según el registro de trazabilidad del deploy de Entrega 1 verificado por consulta directa, tiene **112.485 productos, 2.993 clientes, 5 ventas (3 `Confirmada`), 4 movimientos de caja y 8 migraciones**. Las filas sobre las que el backfill va a actuar **existen solamente ahí**. Por eso el PASS *"migración aditiva, aplicada sin pérdida de datos"* es cierto y a la vez no cubre nada de esto: lo que se verificó fue el esquema.

**No se consultó producción** (fuera de alcance, instrucción explícita del brief): el estado de prod se tomó del registro de trazabilidad, no de una query. Que prod esté exactamente en las 8 primeras migraciones **queda BLOCKED** y es lo primero que hay que confirmar contra prod antes del deploy — de eso depende si `D9` (el corrimiento de 3 horas sobre `CajaMovimientos.Fecha`) ya corrió o está pendiente.

**El ensayo que lo cierra** (media hora, sin tocar producción): restaurar el backup de prod en una base descartable local, correr `dotnet ef database update` ahí, y afirmar fila por fila que los 4 `CajaMovimientos` quedan con `MedioPago` **NO NULL**, con `UsuarioId` resuelto y con `PagoVentaId` resuelto donde corresponda, y que los conteos de `Ventas`/`Gastos`/`Proveedores` son idénticos antes y después. Si alguno queda `NULL`, eso es un defecto que se reporta **antes** del deploy, y el fix es una migración correctiva aditiva — nunca editar una migración ya aplicada.

## Partes de defecto emitidos al Implementador

- **`LP-051`** `trivial` — `archivos_fix`: `FerreteriaLaPlatense.Web/Views/Configuracion/InteresesTarjeta.cshtml` (comentario de la segunda grilla, ~232-244). `migracion_ef`: ninguna. **Re-verificación:** el comentario, o no reproduce el mecanismo, o no promete no reproducirlo — verificable comparando las afirmaciones de los dos párrafos (no comparten ninguna afirmación sobre el comportamiento del parser).
- **`LP-050`** `major` — **no es un parte para el Implementador: es un paso de procedimiento para Joaquín antes del deploy.** `archivos_fix`: ninguno (no hay defecto de código). **Re-verificación:** el ensayo sobre la restauración del backup de prod, con las 4 afirmaciones de arriba.

## Estado de los partes de la corrida anterior

| parte | estado |
|---|---|
| `LP-044` | **CERRADO** (criterio reescrito: el grep literal era inverificable) |
| `LP-045` | **CERRADO** (52/52 switch con descarte, 11 comentarios verificados, 0 falsos vivos) |
| `LP-049` | **CERRADO** (par de control + control positivo) |
| Riesgo 1 — `MigracionCatalogo` sin guarda de cadena | **CERRADO** (17 abortos + escritura sólo con confirmación exacta) |
| Riesgo 3 — dev 4 migraciones atrás | **CERRADO** (18 migraciones, conteos idénticos, 6 tablas vacías, sin deriva) |

## Riesgos de liberación

1. **`LP-050` — el único que condiciona el deploy.** Los backfills de datos del `Up` de 4 migraciones nunca corrieron contra filas reales, no tienen `Down` que los revierta, y uno clasifica el medio de pago por `LIKE` sobre texto libre. Alcance chico en volumen (4 movimientos de caja, 5 ventas) pero es **el ledger de caja y es plata real**. Mitigación: el ensayo sobre la restauración del backup de prod. **Sin ese ensayo, el deploy es a ciegas sobre la única parte del salto que reescribe datos existentes.**
2. **El estado real de producción no está verificado en esta corrida** (fuera de alcance). Antes del deploy: `select MigrationId from __EFMigrationsHistory` contra prod, y conteos de `CajaMovimientos`/`Ventas`/`Gastos`. El registro de trazabilidad del 2026-10-05 dice 8 migraciones; **la lección ya aprendida en este proyecto es que el estado de producción se verifica contra producción, no contra la memoria**.
3. **El backup de prod previo al deploy es el único rollback** de los backfills, no una precaución opcional. Verificar tamaño y línea final (`Dump completed`) como se hizo con el de dev.
4. La carrera de dos planes con el mismo número de echeq sigue sin índice único. Declarada, aceptada: número repetido en una grilla, no plata mal movida.
5. `CS0114` en `HomeController` sigue ahí. Preexistente de Entrega 1, sin efecto funcional conocido.
6. `tools/ArnesHotfixTransacciones` sigue siendo un directorio huérfano con `bin`/`obj` sin fuente. Decisión de Joaquín.

## Cobertura del catálogo cross-proyecto

| id | aplica | resultado | acción |
|---|---|---|---|
| `OLV-019` (la baja del valor vive sólo en el combo; un POST a mano lo sigue creando) | sí — es la forma genérica del alcance | **PASS** | Cerrado para Marca/Modelo/Categoría por POST; enumeración completa de las 9 entidades con `Activo` |
| `LP-047` (instancia en Tarjeta) | sí | **PASS** (no regresó) | `ArnesTarjetaYTransferencia` 41/41 ×2 |
| `ELV-002` (asimetría Create/Update: `Update` no valida lo que `Create` sí) | sí | **PASS** | Una sola `ValidarAsync(dto, idExcluido)` para ambos caminos; medido en Create **y** en Edit |
| `OLV-011` (editar un registro ya vencido/dado de baja es imposible por una guarda de la vista) | sí — es el riesgo de regresión del lote | **PASS** | Los 3 combos de Editar sirven el inactivo asignado con `selected`; la compra #9950 se guarda |
| `OLV-035` (el arreglo se hizo en una superficie y había dos) | sí | **PASS** | Service + UI cubiertos en Producto y en Compra; enumeración de superficies |
| `OLV-015` (dos guardas mutuamente excluyentes: el botón se muestra cuando X y la acción acepta NO-X) | sí | **PASS** | Es exactamente lo que el combo de compra tenía antes; medido en los dos extremos |
| `LP-044`, `LP-045` | sí | **PASS** | Barrido por patrón, 0 falsos vivos |
| `LP-046`, `LP-048`, `LP-049` | sí | **PASS** | Arneses reproducidos, `LP-049` con par de control |
| `LP-042` (afirmaciones que pasan vacías) | sí | **PASS con observación** | `ArnesVentaSinFacturaYParcial` no imprime "no medidas" |
| `KOI-012` (migración de datos con ids escritos a mano mueve plata al concepto equivocado) | sí | **FAIL → `LP-050`** | Misma familia: backfill de datos no verificado contra los datos |
| `GAN-002` (backfill que no reconstruye un campo para filas históricas) | sí | **FAIL → `LP-050`** | El `ELSE NULL` del `LIKE` es exactamente esta forma |
| `LP-009`, `LP-011`, `LP-013`, `LP-021`, `LP-024`, `LP-037`, `LP-039`..`LP-041` | sí (no-regresión) | **PASS** | Arneses de caja/ledger/stock 153+32+92 ×2 |
| `LP-003` (reabrir un borrador deja los inputs vacíos por cultura es-AR) | sí (no-regresión) | **PASS** | `/OrdenesCompra/Edit/9950` y `/Productos/Edit/*` renderizan y re-postean |
| `MH-047`, `OLV-025`, `LP-007`, `LP-008` (enum/switch/rótulos) | sí | **PASS** | 52/52 switch con descarte, comentarios verificados |
| `MH-010`, `SG-001`, `GAN-006`, `LP-003` (grillas y maskMoney) | parcial | **cubierto por HTTP** | Sin navegador: el POST real de cada formulario se verificó, la interacción de tipeo no |
| `REG-002`, `MH-015`..`MH-018`, `DN-004`, `KOI-010`, `KOI-016`, `OLV-001`, `OLV-006`, `OLV-012`, `OLV-016`, `OLV-033`, `OLV-041`, `MH-037`, `MH-039`, `MH-043` | no — fuera del alcance del lote | N/A | — |

## Reglas nuevas o modificadas desde la última corrida

`6-qa.md` declaraba **"Ultima validacion de reglas cross-proyecto: 2026-10-07"** (hoy, puesta por la corrida anterior). Verificado: `git log --since=2026-10-07 -- .github/instructions/32-estandares-qa-implementador.instructions.md docs/qa/regresiones-manuales.yml` → **sin commits**; el índice de `32` y `cat_resumen.txt` coinciden con lo validado. **Ninguna regla nueva ni modificada desde 2026-10-07.** Esta corrida agrega `LP-050` y `LP-051`: el catálogo pasa de 190 a **192 ítems**, sin duplicados (validado con `yaml.safe_load` + `Counter`), índice regenerado con `scripts/contexto.py resumenes`.

## Pruebas mínimas ejecutadas

Build del árbol exportado (0/9, desglosadas); 18 migraciones barridas separando `Up` de `Down` con genéricos; verificación independiente de `dev` (18 migraciones, 3 conteos, 6 tablas vacías por conteo real, backup por tamaño y línea final); clon de dev + app levantada por variable de entorno; 21 pantallas y 13 endpoints de DataTables por HTTP con antiforgery; 6 POST de alta/edición de producto (los tres catálogos, alta y edición, conservar y mover) con lectura en BD antes y después; 3 GET de Editar producto + 1 de Editar compra con parse de `<option>` agnóstico al orden de atributos; 2 POST de Editar compra (conservar y mover) con control negativo; CC de un proveedor inactivo por HTTP; **17 ejecuciones de la guarda de `MigracionCatalogo`** (4 modos × 4 escenarios + host) más el centinela en los dos sentidos y la confirmación equivocada; **14 ejecuciones de guarda de los 6 arneses**; **14 corridas de los 7 arneses** con `md5` verificado y dos pasadas cada uno; par de control y control positivo de `LP-049`; barrido por patrón de 52 `switch` y 84 vistas; enumeración de las 9 entidades con `Activo`.

## Checklist de salida para merge

- [x] Los 6 criterios del lote en PASS con evidencia ejecutada
- [x] `LP-044`, `LP-045`, `LP-049` **CERRADOS** (el criterio de `LP-044` reescrito y declarado)
- [x] Riesgo 1 (`MigracionCatalogo`) y riesgo 3 (dev atrasada) **CERRADOS**
- [x] `dev` migrada verificada de forma independiente; el sistema opera contra ella sin una excepción
- [x] 7 arneses verdes con `md5` verificado, dos corridas cada uno, ningún total caído
- [x] La decisión de no tocar `CCProveedorService`/`CCEmpleadoService` evaluada y **aprobada**
- [x] Barrido de `Activo` completo por enumeración: no queda una cuarta instancia
- [x] Línea base del build confirmada exacta (0 errores / 9 advertencias, 8 `NU1902` + 1 `CS0114`)
- [x] `git status --porcelain` del repo del sistema limpio (`?? .claude/`, preexistente), HEAD `fcfa077`
- [ ] **`LP-050`: ensayo de las migraciones pendientes sobre la restauración del backup de producción** ← **gate del deploy**
- [ ] **Estado real de producción verificado contra producción** (migraciones + conteos de caja/ventas) ← gate del deploy
- [ ] Backup de producción previo al deploy, verificado por tamaño y línea final
- [ ] `LP-051` aplicado (trivial, no bloquea)

**El merge de `fcfa077` está en condiciones. El deploy a producción no, todavía** — y lo que falta no es código: es el ensayo de los backfills contra una copia de los datos reales. Es el único tramo del salto de 10 migraciones que reescribe filas que ya existen, el único que no tiene vuelta atrás por migración, y el único que nunca se ejecutó sobre una sola fila de verdad.

---

