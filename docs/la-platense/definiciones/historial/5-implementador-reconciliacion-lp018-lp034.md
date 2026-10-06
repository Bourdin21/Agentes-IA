# Historial — Reconciliacion de la familia LP-018 / LP-034 en `entrega-1-migracion`

Archivado de `5-implementador.md` el 2026-10-06 (eran 12 KB) para sostener el techo de 150 KB de la
instruccion 39, al cerrar CR-01/CR-02. **Ronda CERRADA y medida:** `LP-034` cerrado, los once sitios
de la familia reconciliados, y `tools/ArnesReconciliacionTx` en 153 afirmaciones OK / 0 falladas
(verificado otra vez el 2026-10-06, sin regresion).

**Se lee solo si hace falta el detalle de esa reconciliacion.** Lo que hay que saber sin abrirlo ya
vive en tres lugares que son la fuente de verdad y no se archivan:

- El XML-doc de `Data/BloqueoDeFila.cs` y `Data/RelecturaBajoLock.cs` en el repo del sistema: el
  patron completo (orden canonico de locks, por que no `ReloadAsync`, la regla `LP-035`).
- `PAT-059` en `docs/patrones/catalogo.yml`: el antipatron y sus cinco decisiones.
- El bloque `## Verificacion por ejecucion de los 6 sitios restantes` de `5-implementador.md`, que
  **no** se archivo porque contiene `LP-037` **abierto y medido a proposito**.

---

## Reconciliacion de la familia LP-018 / LP-034 en `entrega-1-migracion` (2026-10-06)

Commit local **`a72e3cd`** sobre `entrega-1-migracion`. **Sin push, sin deploy, sin migracion EF.**
La rama `hotfix-transacciones-ventas` **no se toco**: sigue reflejando exactamente lo publicado.

### Por que NO se mergeo, y es la decision de fondo

El merge base es `2580f7c` y un `git merge` habria chocado en 3 archivos. Se descarto por una
razon que no es de comodidad:

- **Ninguna rama es superconjunto de la otra.** Desarrollo cubre mas superficie (7 constantes de
  tabla contra 4, mas los ledgers de proveedores y empleados, la recepcion, la conversion de
  presupuesto), pero **le faltaban por completo dos de los cinco sitios del hotfix**:
  `VentaWorkflowService.CancelarBorradorAsync` y `CuentaCorrienteClienteService.RegistrarCobroAsync`
  **no tenian ni lock ni transaccion**. La premisa del brief ("la cobertura amplia de desarrollo
  mas el helper del hotfix") era **falsa en esa mitad**: no alcanzaba con agregar el helper, habia
  que traer dos sitios enteros.
- **La unidad de reconciliacion es la decision POR ENTIDAD, no el archivo.** Un merge resuelve
  hunks y declara exito; no puede decidir que `PagoOrdenCompra` necesita el helper, porque
  **ninguna de las dos ramas lo habia aplicado ahi**. Los 4 servicios que el hotfix nunca toco
  (`PagoProveedorService`, `PresupuestoService`, `OrdenCompraService`, `AjusteStockService`) son
  justamente los que tenian la relectura decorativa, y un merge los habria dejado intactos con el
  arbol limpio.
- El arnes del hotfix esta escrito contra el esquema de produccion (8 migraciones) y 5 metodos;
  arrastrarlo al merge habria dado un arnes que no aplica. Se escribio su sucesor.

### RELEVAMIENTO ENTIDAD POR ENTIDAD — el criterio y su resultado

**El criterio:** `ReloadAsync` solo vale si se verifico que **nadie escribe el `DeletedAt` de esa
entidad**. Si hereda `SoftDestroyable` y alguien lo escribe, el query filter global esconde la fila,
EF detacha la entidad y los valores quedan en los de **antes** del lock: la relectura parece hecha
y no relee.

**El grep reproducible** (es el que da el numero, no la lectura):
`grep -rn "DeletedAt\s*=" --include=*.cs ... | grep -v "== null" | grep -v "!= null"`.
Escritores reales hoy: `Repository.DeleteAsync` (generico, linea 50) y 6 escrituras directas.

| # | Sitio | Fila(s) bloqueada(s) | Hereda `SoftDestroyable` | ¿Alguien escribe su `DeletedAt`? | Veredicto |
|---|-------|----------------------|--------------------------|----------------------------------|-----------|
| 1 | `VentaWorkflowService.ConfirmarAsync` | `Ventas` + `Productos` | si / si | **si** / **si** (`VentaWorkflow:501` · `ProductoService:394` + `:573`) | helper en **las dos** (`Producto` = LP-034) |
| 2 | `VentaWorkflowService.FacturarAsync` | `Ventas` | si | **si** | helper |
| 3 | `VentaWorkflowService.AnularAsync` | `Ventas` + `Productos` | si / si | **si** / **si** | helper en las dos |
| 4 | `VentaWorkflowService.CancelarBorradorAsync` | **ninguna** (no tenia lock) | si | **si** (el mismo metodo) | lock + helper + guarda de "ya cancelada" |
| 5 | `CuentaCorrienteClienteService.RegistrarCobroAsync` | **ninguna** (no tenia lock) | `Cliente`: si | **si** (`ClienteService:231`) | lock de `Clientes` + re-correr el AGREGADO |
| 6 | `GastoService.AnularAsync` | `Gastos` | si (por convencion) | **NO** | **`ReloadAsync` se queda**, declarado |
| 7 | `OrdenCompraService.RecibirAsync` | `OrdenesCompra` + `Productos` | si / si | OC: **NO** · `Producto`: **si** | OC con `ReloadAsync`; productos con helper |
| 8 | `PagoProveedorService.RevertirPagoAsync` | `PagosOrdenCompra` | si | **si** (`:613`) | helper + guarda |
| 9 | `PagoProveedorService.ConfirmarPagoProgramadoAsync` | `PagosOrdenCompra` | si | **si** (`:613`) | helper + guarda — **el mas caro** |
| 10 | `PagoProveedorService.CancelarPagoProgramadoAsync` | **ninguna** (no tenia lock) | si | **si** (el mismo metodo) | lock + helper + guarda |
| 11 | `PresupuestoService.ConvertirAVentaAsync` | `Presupuestos` | si | **si** (`:496`) | helper |
| 12 | `PresupuestoService.CancelarBorradorAsync` | **ninguna** (no tenia lock) | si | **si** (el mismo metodo) | lock + helper + guarda |
| 13 | `CCEmpleadoService.RevertirMovimientoAsync` | `MovimientosCCEmpleado` | **NO hereda** | n/a (sin query filter) | **ya era relectura real**, declarado |
| 14 | `AjusteStockService.AplicarAjusteAsync` | `Productos` | si | si | **consulta FILTRADA a proposito**: da `null` y falla cerrado |

**El brief hablaba de "7 sitios": son las 7 constantes de tabla, no los metodos.** Los metodos de
la familia son **14**, y **13** usan el helper o una relectura real declarada.

### Las tres asimetrias deliberadas (defendidas por escrito en su call site)

Estan escritas donde viven porque, si no, el proximo barrido las "arregla" por prolijidad:

1. **`Gasto`** — la baja es el flag `Anulado`, una columna normal que la recarga SI ve. Nadie
   escribe `Gasto.DeletedAt` (verificado con el grep, no supuesto). El comentario dice **que hacer
   el dia que se agregue una baja de gastos**.
2. **La fila de la compra en `RecibirAsync`** — la baja de una compra es `Estado = Cancelada`
   (`CancelarAsync`), nadie escribe `OrdenCompra.DeletedAt`. **Los productos de esa misma recepcion
   si van por el helper**: la asimetria esta DENTRO de un metodo.
3. **`AjusteStockService`** — es el unico sitio donde el query filter juega a favor: la consulta
   fresca y FILTRADA devuelve `null` si el producto se borro, y el metodo falla cerrado. El helper
   existe para distinguir "borrada" de "no existe"; este sitio los trata igual.

### Hallazgos propios de esta ronda

**`PagoOrdenCompra` tenia la misma forma que `Venta`, y era peor.**
`CancelarPagoProgramadoAsync` da de baja una programacion escribiendo `DeletedAt` **y dejando
`Estado = Pendiente`** — que es **exactamente** el estado que `ConfirmarPagoProgramadoAsync` exige
para pagar. Los dos caminos **se pisan en el mismo estado** y son dos botones de la misma pantalla,
asi que la carrera no es teorica. Medido con N=8: **5 exitos** y un pago **BORRADO** con el egreso
de caja y el `Pago` de deuda ya posteados. La fila sale del saldo comprometido de la compra, asi
que **la compra se muestra impaga y la plata salio igual**. Y `CancelarPagoProgramadoAsync` no
tenia ni lock ni transaccion: es la mitad simetrica, y se cerro junto.

**Misma forma en `PresupuestoService.CancelarBorradorAsync`** (mitad simetrica de
`ConvertirAVentaAsync`): sin lock, y la guarda de "ya dado de baja" no se puede escribir mirando
`Estado`, que queda en `Borrador`.

**Un bug de relectura incompleta que no es de concurrencia:** `ConvertirAVentaAsync` informa en su
mensaje de rechazo el numero de la venta que si se creo, y lo leia de **la copia anterior al lock**
(= `null`). El mensaje salia como *"ya se convirtio en la venta #"*, sin numero. **La relectura
tiene que traer todo lo que se LEE despues de ella, no solo lo que DECIDE.**

### LP-034 cerrado, y su premisa corregida

`Producto` admite baja y `ProductoService.EliminarAsync` / `EliminarLoteAsync` escriben `DeletedAt`
**sin guarda de uso**. Se cierra **fallando CERRADO** en los tres escritores de stock
(`ConfirmarAsync`, `AnularAsync`, `RecibirAsync`): la operacion se rechaza **nombrando el
producto**, en vez de seguir sin poder escribir el stock. Es un criterio distinto del aviso de
`UnidadVenta` cambiada (que no bloquea) y la diferencia es deliberada: un cambio de unidad hace que
el numero sea discutible, un producto borrado hace que **la escritura no ocurra**.

**LO QUE EL ARNES MIDIO NO ES LO QUE EL PARTE DESCRIBIA.** El parte decia *"el descuento de stock
se pierde en silencio: venta confirmada, plata correcta, stock intacto"*. Con la ventana forzada
(escenario 10c) y antes del fix, lo que pasa es: la venta se confirma *"correctamente"*, se postean
los $1.420 de caja y el debito de CC, **y el descuento SI se persiste** (100 -> 98) sobre una fila
que ninguna consulta ve. **No es que el stock se pierda: es una venta cerrada contra un producto
que ya no esta en el catalogo**, con su stock movido donde nadie puede verlo ni corregirlo. El
invariante roto es otro y el fix es el mismo, pero la descripcion habia que corregirla.

**Y un detalle de EF que explica por que el guard de LP-034 solo se alcanza en carrera:**
`ItemVenta.Producto` es una navegacion **requerida**, asi que si el producto ya estaba borrado al
cargar la venta, EF descarta **tambien la fila del item** (inner join) y `venta.Items` vuelve
**vacia** — salta la guarda de "al menos un item" y no la de LP-034. Falla cerrado igual, pero por
otra puerta. Por eso el escenario secuencial **no alcanza** y hubo que forzar la ventana.

### Evidencia ejecutada — `tools/ArnesReconciliacionTx`

Sucesor de `tools/ArnesHotfixTransacciones` (que vive en la rama publicada y mide 5 metodos sobre
el esquema de produccion). Base **`laplatense_recon_tx`** — nombre elegido para no disparar la
guarda del arnes, que **aborta** si la cadena menciona `laplatense_dev`, `laplatense_qa*` o
`site4now`; levantada con `dotnet ef database update` y **las 14 migraciones de desarrollo**.
Un scope de DI por competidor (= un `AppDbContext` = una conexion MySQL), **conexion abierta ANTES
de la barrera**, `Barrier.SignalAndWait()`, **N=3 y N=8** en cada sitio.

| | Afirmaciones OK | FALLADAS |
|---|---|---|
| **Con el fix** | **153** | **0** |
| **Sin el fix** (services revertidos a `bdfd99b`, arnes IDENTICO) | 123 | **30** |

Las 30 que discriminan, con sus numeros:

- **Cobro de cuenta corriente (14 afirmaciones):** con N=8, **8 de 8 exitos** sobre una deuda de
  $1.000 → **saldo −$7.000** y **$8.000 de ingreso de caja** donde correspondia $1.000.
- **Venta BORRADA con plata movida (4):** `borrada=True, caja=1, cc=1, stock=98` — el invariante
  del criterio 8, violado.
- **Pago programado BORRADO con la plata ya salida (8):** `borrado=True, caja=1 ($777), cc=1`.
- **LP-034 (4):** confirmacion exitosa contra un producto borrado, con $1.420 posteados.

**ADVERTENCIA METODOLOGICA, declarada y no omitida:** los sitios **11 (recepcion), 12 (confirmar
pago), 14 (revertir pago), 15 (convertir presupuesto) y 16 (CC empleado)** pasan **tambien sin el
fix** en la prueba de N-way simple — porque ahi el `ReloadAsync` alcanza cuando no hay una baja
logica compitiendo. **En esos cinco el cambio es correctitud del mecanismo, no un bug con falla
medida.** Lo que falla sin el fix son los entrelazados que involucran una baja logica. Decirlo al
reves seria reportar como logro algo que ya funcionaba (la leccion de la pasada 0).

**Afirmacion que NO discrimina y quedo marcada como tal en el codigo:** el escenario 10b (N-way de
confirmar contra borrar el producto) pasa con fix y sin fix, porque el borrado **gana siempre la
barrera** (no toma ningun lock) y la implicacion *"si confirmo, el stock se desconto"* se cumple de
taquito con `confirmo=False`. Lo que mide LP-034 de verdad es **10c**, con la ventana forzada a
mano: el arnes toma el lock de la venta, larga la confirmacion, la deja clavada esperando, borra el
producto y recien entonces suelta el lock.

**Fallas del arnes por si mismo en esta ronda (5, todas del arnes y no del codigo):**
`LeerEstadoAsync` leia el producto por la consulta filtrada y reventaba con *"Sequence contains no
elements"* justo en el escenario que borra el producto; el `OrigenTipo` real de los asientos de un
pago a proveedor es **`PagoOC`** y no `"PagoProveedor"`; el ledger de empleados exige una fila
**real** en `AspNetUsers` (y `CreatedAt` es NOT NULL sin default); el concepto `Adelanto` mueve caja
y **exige `MedioPago`**; y la limpieza final chocaba con la FK `RESTRICT` de
`MovimientosCCProveedor` porque borraba por los dos origenes conocidos y quedaba el saldo inicial.

### Build y estado

`dotnet build` de la solucion: **0 errores**, 9 advertencias **todas preexistentes** (`NU1902` de
MailKit/MimeKit y el `CS0114` de `HomeController.StatusCode`). Sin migracion EF: **no hay columnas
nuevas**. Limpieza final del arnes verificada: 0 filas de prueba restantes.

### Pendiente de re-verificacion de QA

- **`LP-034`**: **aplicado, pendiente de re-verificacion**. El cierre lo declara QA.
- Los sitios 4, 5, 10 y 12 de la tabla (los que no tenian lock) y los 9 que cambiaron de mecanismo
  de relectura: **aplicados, pendientes de re-verificacion**.
