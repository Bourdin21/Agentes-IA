# Historial - Implementador - La Platense

Bloque archivado desde `5-implementador.md` el 2026-10-07 para dejar lugar a la entrada del
lote 2 de la Entrega 5 (devoluciones) sin cruzar el techo de 150 KB
(`39-presupuesto-contexto.instructions.md`). Se lee solo si el trabajo toca el barrido de
`Activo`, la familia LP-047 o la aplicacion de las 4 migraciones pendientes a `laplatense_dev`.

## Barrido de `Activo` (familia LP-047) + migraciones pendientes a `laplatense_dev` (2026-10-07)

Un commit en `entrega-1-migracion` (`fcfa077`), **sin push y sin deploy**, **sin migraciones EF
nuevas**. Mas una operacion sobre `laplatense_dev` que no toca el repo. Produccion NO se toco.

### Lo primero: dos premisas del brief que eran FALSAS

La pasada 0 del barrido (verificar las premisas, no heredarlas) rindio dos, y las dos cambian lo que
hay que verificar al cerrar:

1. **"Hay 19 migraciones en el repo."** Hay **18** (`ls Migrations | grep -v Designer | grep -v
   Snapshot | wc -l` = 18, y la ruta real es `FerreteriaLaPlatense.Infrastructure/Migrations/`). Dev
   estaba en 14, asi que faltaban **4**, no 5. Si el criterio de cierre hubiera sido "19 aplicadas",
   la verificacion habria fallado sobre una migracion exitosa.
2. **"Las 4 filas `ZZ%` de dev son catalogo legado real del 2026-08-21, no las borres."** En
   `laplatense_dev` **no hay ni una fila con prefijo `ZZ`**: cero en Marcas, Modelos, Categorias,
   Proveedores y `Productos.Codigo`. Lo que hay son coincidencias **internas** de `%ZZ%` — 2 codigos
   de producto (`KHPUZZI100`, `WDFWZZ4508A4`), 188 nombres de producto y 20 nombres de cliente,
   todos catalogo real del 2026-08-21. Y cero residuo `ZZTEST`, o sea la limpieza a mano del
   incidente de `ArnesEntrega3Item4c` quedo completa. **El criterio verificable es el de arriba (2 /
   188 / 20 y cero prefijos), no "las 4 filas intactas".**

Ninguna de las dos era inocua: la primera habria hecho reportar una falla inexistente, y la segunda
habria mandado a buscar cuatro filas que no existen (o, peor, a "restaurarlas").

### El defecto: `ProductoService` no miraba `Activo` de ninguno de los tres catalogos

Es `LP-047` otra vez. La baja logica de Marca, Modelo y Categoria vivia **solo en el combo**
(`ListarActivosAsync`). `ValidarAsync` hacia tres `AnyAsync` de EXISTENCIA y nada mas.

**Medido antes de escribir una linea** (el arnes se escribio primero y se corrio contra el codigo sin
tocar): `CrearAsync` con `MarcaId` de una marca `Activo = 0` devuelve **`Success = True`, mensaje
"Producto creado correctamente"**, y la fila queda en la base. Lo mismo con Modelo y Categoria, y lo
mismo editando. **12 de 26 afirmaciones FALLADAS en la linea base.** La premisa del brief sobre el
POST queda confirmada por ejecucion, no por lectura.

**Y por que el arnes mide "el POST" sin levantar la app:** se leyo `ProductosController.Create(POST)`
y `Edit(POST)`. Los dos hacen exactamente tres cosas — `ModelState.IsValid`, `MapearDto(vm)` y
`_service.CrearAsync/EditarAsync`. **Cero validacion propia en el Controller.** O sea el DTO que el
arnes le pasa al Service es, campo por campo, lo que llega por un POST armado a mano, y el Service es
el unico lugar donde se puede parar.

### El fix: una guarda agrupada, con la asimetria de `OrdenCompraService:653`

`ProductoService.ValidarCatalogosActivosAsync(dto, idExcluido)` — forma de
`RecargoCuotasService.ValidarCatalogosActivosAsync` (LP-047): una pasada, una consulta por catalogo,
los errores de los tres **agrupados en la misma respuesta** (si los tres estan de baja, el operador
se entera una vez y no en tres guardados seguidos).

**La asimetria es la mitad que importa y se copio del `:653`:** el catalogo de baja se rechaza **solo
si es NUEVO para ese producto**; el que el producto ya tenia asignado pasa igual. Sin eso, dar de baja
una marca convertiria en **ineditable** a todo producto que la use hasta que alguien la reactive — y
esa regresion es **peor que el defecto**, porque el defecto necesita un POST a mano y la regresion
rompe el camino normal del operador. Es la misma decision que `OrdenCompraService` tomo para el
proveedor de un borrador: *lo que se impide es MOVER, no tener*.

**Las dos causas siguen con mensajes distintos a proposito.** "No existe" es un dato invalido; "esta
dada de baja" es un dato valido que ya no se ofrece, y lo segundo le dice al operador que puede
reactivarlo y donde. Confundirlas en un mensaje unico lo manda a buscar un error de carga que no
existe. El mensaje **nombra** el catalogo (`La marca "X" esta dada de baja...`) y aclara que *los
productos que ya la tenian asignada se siguen editando con normalidad*.

### El barrido fue POR PATRON, no leyendo (quinta vez que uno por instancia deja vivas otras)

Grep reproducible, y queda escrito: `grep -rn "bool Activo" --include=*.cs` sobre los cuatro
proyectos (excluyendo `obj/`, `bin/` y `Migrations/`) da **9 declaraciones** — 8 entidades mas la
interfaz `ICatalogoSimpleEntity`. Para cada una, la pregunta es la misma: *hay algun Service que
valide el estado al ESCRIBIR?*

| Entidad con `Activo` | El combo filtra | El Service valida al escribir | Veredicto |
|---|---|---|---|
| `Marca` | si (`ProductosController:321`) | **NO** | **defecto, arreglado en esta ronda** |
| `Modelo` | si (`:322`) | **NO** | **defecto, arreglado** |
| `Categoria` | si (`:323`) | **NO** | **defecto, arreglado** |
| `Tarjeta` | si | si (`ValidarCatalogosActivosAsync`, LP-047) | cubierta |
| `RecargoCuota` | si | si (idem) | cubierta |
| `Proveedor` | si | si (`OrdenCompraService:596` y `:653`) | cubierta en el Service — **pero la UI lo derrotaba, ver abajo** |
| `CodigoBarrasProducto` | n/a | n/a | **fuera de la forma**: sin escritor de UI. Solo lo carga la migracion y se lee ya filtrado por `Activo` (5 call sites). No hay camino por el que un operador le asigne uno de baja. |
| `CodigoProveedorProducto` | n/a | n/a | **fuera de la forma**: idem. |
| `ICatalogoSimpleEntity` | — | — | es el contrato, no una tabla. |

**Tres casos que se revisaron y se decidio NO tocar, declarado y no omitido:**

- **`CCProveedorService.RegistrarAjusteAsync` y los pagos a proveedor** leen el proveedor y **no**
  validan `Activo`. Es **correcto y es intencional**: el XML-doc de `Proveedor.Activo` lo dice
  textual — *"un proveedor inactivo NO se ofrece para cargar una compra nueva, pero sigue visible en
  el listado, en su cuenta corriente y en las compras historicas"*. Dar de baja un proveedor
  significa "no le compro mas", no "le congelo la cuenta": hay que poder seguir pagandole lo que se
  le debe. Y esas pantallas **no** usan el combo filtrado, asi que tampoco hay una restriccion de mas
  por el otro lado. Agregar la guarda ahi seria el error de M2 en produccion.
- **`CCEmpleadoService`** usa `EstadoUsuario` (enum de estado de cuenta, no bandera de catalogo) y su
  listado ofrece el filtro por estado **incluyendo los inactivos**, a proposito: la cuenta de un ex
  empleado tiene que poder liquidarse. Fuera de la forma.
- Los combos de **filtro** de listados (`ProductosController:53-55`, `StockController:38`,
  `AumentoMasivoPreciosController:140-142`) traen solo activos. Es de solo lectura y no corrompe
  nada, pero significa que un listado no se puede filtrar por una marca jubilada. **Queda anotado, no
  arreglado** — no es de esta familia, y una afirmacion cierta no es una autorizacion para ampliar
  alcance.

### El hallazgo del barrido: el combo de Editar de una compra perdia el proveedor asignado

Es el mismo defecto **por el otro lado**, y es el que mas valor dio.

`OrdenCompraService:653` tiene la asimetria correcta desde la Entrega 3. Pero
`OrdenesCompraController` armaba el combo —en el GET de `Edit` (linea 210) y en
`RecargarFormularioAsync` (675)— con `ListarActivosParaComboAsync()` **sin re-agregar el proveedor
asignado**. Resultado: **la asimetria del Service era INALCANZABLE por la UI.** El `<select>` tiene un
placeholder `value=""` primero, asi que caia ahi; `ProveedorId` es `int` no nullable; el POST rebotaba
por `ModelState` y el borrador quedaba **inmodificable** con el mensaje *"el campo Proveedor es
obligatorio"*, que no tiene nada que ver con la causa. Exactamente lo que el comentario del `:653`
dice que no tiene que pasar.

**Una guarda correcta en el Service, derrotada por la vista.** Y el contraste esta en el mismo repo:
`ProductosController.PoblarCombosAsync` (lineas 326-341) **si** re-agrega la marca/modelo/categoria
asignada, con la regla de `32-estandares-qa-implementador` citada al lado.

El arreglo va en **un solo lugar invocable** —una sobrecarga
`IProveedorService.ListarActivosParaComboAsync(int? proveedorIdAsignado)`— y no copiado en cada
Controller, que es como nacen estas reincidencias. Detalles que importan: la condicion es `is not > 0`
y no `HasValue`, porque el ViewModel del alta trae `ProveedorId = 0` (es `int` no nullable) y tratar
solo el `null` dejaba la mitad del caso sin cubrir; el asignado **no se duplica** si ya venia activo;
y el combo se reordena por nombre para que el agregado no quede al final.

**Y la pasada 3 (comentarios) rindio aca:** `Views/OrdenesCompra/Create.cshtml` afirmaba *"Checklist
10b: en Editar el combo llega CON el proveedor ya seleccionado, nunca vacio"*. **Era FALSO** para el
proveedor dado de baja — una regla de negocio mentirosa viviendo en el repo, que es `LP-008`. No se
borro: se reescribio **con la medicion** (dice que era falsa, que se midio, y que lo que la hace
verdadera ahora es el Controller + el Service, no la vista). Y el hint visible decia *"Solo aparecen
los proveedores activos"*, que ahora seria impreciso: tambien se corrigio.

### Evidencia

**Build: 0 errores / 9 advertencias** (`dotnet build --no-incremental`: 8 `NU1902` de MailKit/MimeKit
+ 1 `CS0114` de `HomeController.StatusCode`, de codigo y preexistente de Entrega 1). Identico a la
linea base. *Nota operativa: el build incremental reporta 8 porque no recompila `Web`; para confirmar
la linea base hace falta `--no-incremental`.*

**`tools/ArnesBarridoActivo`** — nuevo, 26 afirmaciones, base desechable `laplatense_barrido_activo`
(DROP + CREATE + `dotnet ef database update`, porque **los fixtures no se reutilizan entre rondas**).
Guarda de identidad sin default y medida en las dos direcciones: contra `laplatense_dev` aborta con
**exit 2**, sin la variable aborta con **exit 2**, contra la base desechable imprime *"Base de destino
verificada"* y corre.

| Corrida | Resultado |
|---|---|
| Codigo **sin** el fix (linea base) | 13 OK / **12 FALLADAS** / 1 NO MEDIDA, exit 1 |
| Codigo **con** el fix | **26 OK / 0 / 0**, exit 0 |

**Seis mutantes, y el reparto por marca lo IMPRIME el arnes (no un comentario):**

| Mutante | Que rompe | Tumba |
|---|---|---|
| M1 | saca la guarda entera (reproduce LP-047 en producto) | 12: `1.1`, `1.3`-`1.6`, `2.1`-`2.4`, `3.4`, `3.5`, `4.2` |
| M2 | guarda **demasiado amplia**: sin la asimetria | `3.2`, `3.3` |
| M3 | solo Marca, se olvida Modelo y Categoria (barrido por instancia) | `1.4`-`1.6`, `2.3`, `2.4` |
| M4 | el combo vuelve a perder el proveedor asignado | `5.2` |
| M5 | combo **demasiado amplio**: todos los inactivos | `5.3`, `5.5` |
| M6 | rechaza con mensaje **generico**, sin nombrar el catalogo | `1.2` |

**La verificacion del relabel, comparando salidas y no intenciones: la union de las tumbadas por
M1..M6 es de 18 afirmaciones y el conjunto `[DISCRIMINA]` es de 18 — son el MISMO conjunto. Y en los
seis mutantes cayeron CERO `[COBERTURA]` y CERO `[CONTEXTO]`.**

**M2 es el mutante que mas valor dio, y es el de la direccion OPUESTA al defecto.** Es el unico que
mide la familia 3 (el caso que no se puede romper): en la linea base `3.2` y `3.3` pasaban —
obviamente, sin guarda el producto viejo se guarda igual— asi que su `[DISCRIMINA]` **no** sale de la
linea base, sale de M2. Si un fix tiene un "caso que hay que seguir permitiendo", ese caso necesita un
mutante que lo rompa.

**Tres correcciones del instrumento, y dos salieron de los mutantes:**

1. **M1 moria con una `DbUpdateException` de FK en la familia 4 y se llevaba puesta la familia 5
   entera** (exit 3, "corrida sin resultado"). Sin validacion de existencia, EF manda el INSERT y
   `FK_Productos_Marcas_MarcaId` lo rechaza en la base. Es la **segunda forma de falso verde** del
   proyecto (morir y dejar de medir lo que venia despues). Al taparlo con un `try` aparecio la
   informacion que faltaba: *"se rechaza"* y *"se rechaza BIEN"* son dos afirmaciones distintas — un
   rechazo por excepcion de FK le llega al operador como un error 500, no como un mensaje. Ahora
   `4.1` solo exige que no se guarde (la cumplen las dos formas) y `4.2` exige que el rechazo venga
   **por validacion**: esa discrimina, y M1 la tumba.
2. **M5 tumbo `5.5`, que estaba marcada `[COBERTURA]`** entonces subio a `[DISCRIMINA]`. Subdeclarar
   cobertura va para el lado seguro, pero el arnes dice que prueba menos de lo que prueba y el
   proximo que lo lea no sabe cuales afirmaciones defender.
3. **`1.2` quedo `[DISCRIMINA]` sin que ningun mutante la matara.** Bajo M1 el alta no se rechaza,
   asi que `1.2` (condicional) queda **NO MEDIDA** y desde ahi no se puede matar. Se agrego **M6** en
   vez de bajarle la etiqueta: **faltaba el mutante, no sobraba la marca.** Bajarla habria cumplido
   la letra y dejado el invariante sin probar una sola vez.

**El cuarto accidente operativo se evito a proposito:** `tools/` no esta en
`FerreteriaLaPlatense.slnx` (`grep -c tools` da 0), asi que `dotnet build` de la raiz **no** compila
los arneses y `--no-build` levanta el binario de la ronda anterior sin avisar. Las 8 corridas de esta
ronda (linea base + limpia + 6 mutantes) llevaron `dotnet build
tools/ArnesBarridoActivo/ArnesBarridoActivo.csproj` **explicito** antes de cada una.

**Y los mutantes se aplicaron y revirtieron por BACKUP de archivo, no con `git checkout`:** el fix no
estaba commiteado todavia, asi que un `checkout` lo habria borrado. Al final, `md5sum` de los dos
archivos contra el backup para probar que el codigo quedo exactamente como antes de mutar.

### Migraciones pendientes aplicadas a `laplatense_dev` — y SOLO a dev

Produccion **no se toco** (ni la base ni el sitio): el deploy lo autoriza Joaquin aparte. Lo unico que
corrio contra dev fue `dotnet ef database update`; **ningun arnes y ningun `MigracionCatalogo`**.

**Backup, antes de tocar nada:**
`C:\Sistemas\backups\laplatense\laplatense_dev_2026-10-07_pre-migracion-18.sql`
(`mysqldump --single-transaction --routines --triggers --events`, **35,2 MB**, 53 `INSERT`, cierra con
`-- Dump completed`, o sea no quedo truncado).

**Verificacion de que las 4 pendientes son aditivas, hecha ANTES de aplicarlas** (operacion por
operacion sobre el `Up()` de cada una, hasta el `Down()`): solo `AddColumn` (2), `CreateTable` (6),
`CreateIndex` (11) y `AddForeignKey` (1). **Cero**
`DropColumn`/`DropTable`/`DropForeignKey`/`DropIndex`/`DeleteData`/`AlterColumn`/`RenameColumn`/`TRUNCATE`.
Coincide con lo declarado.

**Pasada 6 (la columna nueva sobre las filas que YA estaban), columna por columna:**

- `Ventas.Facturar` — `bool NOT NULL defaultValue: true`. Para las 13 ventas que ya existian, `true`
  **es** el valor verdadero: la opcion "confirmar sin facturar" la trae **esta misma migracion**, asi
  que ninguna fila previa pudo haber sido "no facturar". **Sin backfill, y verificado despues:
  `Facturar = 1` en las 13.**
- `PagosVenta.TarjetaId` — `int` **nullable**. `NULL` = "no declara tarjeta", legitimo para los 10
  pagos previos (las tarjetas llegan con CR-03). **Sin backfill, y verificado: `NULL` en los 10.**

| | antes | despues |
|---|---|---|
| Productos | 112.485 | **112.485** |
| Clientes | 2.993 | **2.993** |
| OrdenesCompra | 0 | **0** |
| Marcas / Modelos / Categorias / Proveedores | 128 / 1 / 16 / 85 | **128 / 1 / 16 / 85** |
| Ventas / PagosVenta | 13 / 10 | **13 / 10** |
| Migraciones aplicadas | 14 | **18** |
| Tablas | 39 | **45** |
| `%ZZ%` reales (cod. producto / nombre producto / nombre cliente) | 2 / 188 / 20 | **2 / 188 / 20** |
| filas con prefijo `ZZ%` | 0 | **0** |

Las 4 migraciones nuevas en `__EFMigrationsHistory`:
`EntregaCinco_VentaSinFacturaYComprobantesParciales`, `EntregaCinco_CandadoPeriodoCaja`,
`CR03_TarjetasEInteresPorCuotas`, `CR04_PlanDeEcheqs`. Las 6 tablas nuevas presentes y en 0 filas:
`CandadosPeriodoCaja`, `ComprobantesAfip`, `ComprobantesAfipItems`, `Tarjetas`,
`InteresesTarjetaCuota`, `LineasEcheq`.

**Un control que conviene retener: el esquema de dev se diffeo contra una base recien creada con las
18 migraciones.** La unica diferencia es **una** tabla, `_bk_unidadventa_20261005` (112.485 filas de
`Id` + `UnidadVenta`), que es el respaldo conocido de la correccion del 2026-10-05 y ya estaba
anotado. Eso explica exacto el 45 contra 44 y es la evidencia de que **dev no tiene deriva de
esquema**: aparte de ese respaldo, es igual a una base limpia al dia.

No hizo falta restaurar el backup. **Queda guardado igual** — es la base con el catalogo real del
cliente y reconstruirla cuesta una corrida de migracion de 112.485 productos.

### Fixtures y como re-crear el arnes

Queda vivo `laplatense_barrido_activo` (18 migraciones, **sin residuo**: el arnes limpia al principio
y al final, y lo afirma). No se toco ninguno de los que hay que preservar (`laplatense_qa_l1`..`l6`,
`laplatense_qa_d9`, `laplatense_gate_fix`, `laplatense_gate_cr04`, `laplatense_gate_4c`,
`laplatense_cr04`). Para re-correrlo desde cero:

```
DROP DATABASE IF EXISTS laplatense_barrido_activo; CREATE DATABASE laplatense_barrido_activo CHARACTER SET utf8mb4;
set ConnectionStrings__DefaultConnection=Server=127.0.0.1;Port=3306;Database=laplatense_barrido_activo;Uid=root;Pwd=root;CharSet=utf8mb4
dotnet ef database update --project FerreteriaLaPlatense.Infrastructure --startup-project FerreteriaLaPlatense.Web
dotnet build tools/ArnesBarridoActivo/ArnesBarridoActivo.csproj
dotnet run --project tools/ArnesBarridoActivo --no-build
```

### Pruebas minimas para QA (no se ejecuto smoke por navegador: lo prohibe el rol)

1. **Catalogo > Marcas**: dar de baja una marca que tenga productos. En **Productos > Nuevo** la marca
   no tiene que aparecer en el combo. Postear igual el alta con esa marca (DevTools, cambiar el
   `value` del `option`, o `curl` con el antiforgery) tiene que rechazar **nombrando la marca** y
   **no** crear el producto. Repetir con Modelo y con Categoria.
2. **El caso que no se puede romper:** abrir un producto que YA tenia esa marca jubilada, editarle el
   nombre y **guardar**. Tiene que guardar sin un solo error, y el combo tiene que llegar con la marca
   de baja seleccionada.
3. **La precision de la excepcion:** en ese mismo producto, intentar cambiarlo a **otra** marca de
   baja. Tiene que rechazar.
4. **Los tres a la vez:** postear un alta con marca, modelo y categoria de baja, tienen que salir
   **tres** errores en la misma respuesta, no uno.
5. **Compras:** dejar una orden en Borrador, dar de baja su proveedor, y entrar a **Editar** esa
   orden. El combo tiene que llegar **con ese proveedor seleccionado** (antes caia en vacio y el
   borrador quedaba inmodificable), el guardado tiene que funcionar, y **otro** proveedor inactivo
   **no** tiene que aparecer en el combo.
6. **No-regresion:** alta y edicion normales de producto con los tres catalogos activos; alta normal
   de una compra con un proveedor activo.

### Riesgos y lo que NO entro

- **Riesgo 1 — la guarda es nueva en un camino caliente.** `ValidarAsync` corre en cada alta y cada
  edicion de producto. Pasa de 3 consultas `AnyAsync` a 3 proyecciones `Select` mas 1 lectura del
  producto solo en edicion: **una consulta mas en el peor caso**, todas por PK y `AsNoTracking`. No
  toca el listado de 112.485 productos.
- **Riesgo 2 — el mensaje nombra el catalogo**, o sea expone el nombre de una marca de baja a quien
  postee. Es informacion que ya esta en el ABM de catalogos y el alta de producto pide
  `RequireAdministracion`: aceptado.
- **No entro:** deploy a produccion (base y sitio), Entrega 5 (AFIP real, NC/ND, anulacion por
  comprobante), `tools/ArnesHotfixTransacciones` (el directorio huerfano con `bin`/`obj` sin fuente
  queda como esta, lo decide Joaquin), el `CS0114` de `HomeController`, y los combos de **filtro** de
  listados que solo ofrecen activos (anotado arriba).

### Checklist de salida para merge

- [x] Build 0 errores / 9 advertencias (linea base exacta, con `--no-incremental`).
- [x] Logica de negocio en el Service, no en el Controller. El Controller solo elige **que** combo
      pedir.
- [x] Sin migraciones EF nuevas. La unica operacion de datos fue aplicar las 4 pendientes a dev, con
      backup previo y conteos verificados.
- [x] Barrido por patron con el grep escrito y la tabla de las 9 declaraciones de `Activo`.
- [x] Afirmacion verificable medida y no declarada: el comentario falso de la vista se reescribio con
      la medicion.
- [x] Arnes con guarda de identidad sin default, medida en las dos direcciones, y limpieza afirmada
      por delta.
- [x] Relabel verificado contra las corridas mutantes, en las dos direcciones.
- [ ] **Pendiente de re-verificacion por QA.** `LP-047` ya estaba cerrado por QA para Tarjeta; esta es
      la misma familia en tres catalogos mas y en el combo de compras, y el cierre lo declara QA en
      contexto nuevo.


