## Verificacion por ejecucion de los 6 sitios restantes de la familia de atomicidad (2026-10-06)

Commits locales `58c112b`, `6736b9d` y `bb9e21d` en `entrega-1-migracion`. **Sin push, sin deploy,
sin migracion EF.** Todo queda **aplicado, pendiente de re-verificacion** de QA.

### El punto de partida era falso

El brief pedia cerrar 6 sitios. **Los 6 ya estaban escritos** en `3cf60ab`: el mensaje de ese commit
dice que no se hicieron porque lo redacto el orquestador despues de que los dos agentes murieran por
cuota, sin releer el arbol. Lo que faltaba no era escribirlos sino **ejecutarlos**, y ahi estaba todo
el valor: el arnes de la familia, que `a72e3cd` dejo en **153 OK / 0**, en `HEAD` daba
**139 OK / 14 FALLADAS**. Las 14 eran `ConfirmarPagoProgramadoAsync`. **Un fix sin medir habia
reintroducido el defecto que el fix anterior cerraba.**

Leccion de proceso, no de codigo: *el commit que declara el alcance no es evidencia del alcance.* Que
un sitio este cerrado se releva contra el arbol y contra el arnes.

### `LP-035` - la lectura comun adelantada congela el snapshot (el defecto nuevo del patron)

`3cf60ab` movio `ValidarPeriodoAbiertoAsync` adentro de la transaccion y la puso **antes** de los
locks de fila, razonando que el orden canonico de tablas pone el periodo primero. El razonamiento es
cierto y la conclusion falsa: esa guarda hace **lecturas comunes**, y en REPEATABLE READ **la primera
lectura comun de la transaccion congela el read view**. Desde ahi toda relectura -con el lock tomado
y con `IgnoreQueryFilters`- lee de un snapshot anterior a la espera.

**Es la tercera forma de la misma falla de fondo: la relectura parece hecha y no relee.** Las otras
dos ya estaban catalogadas (el `ReloadAsync` que el query filter vacia, y el `Estado` que no
discrimina). Esta la esconde el motor.

| | sin fix (= `3cf60ab`) | con fix |
|---|---|---|
| N=3 | **3** confirmaciones de 3, **$ 2.331** de caja y 3 Pagos de deuda | 1 de 3, $ 777 |
| N=8 | **8** confirmaciones de 8, **$ 6.216** de caja | 1 de 8, $ 777 |
| invariante | un pago **BORRADO** con caja=4 ($ 3.108) y cc=4 ya posteados | un solo ganador |

**La regla, verificada con dos sesiones MySQL y escrita en el XML-doc de `BloqueoDeFila`:** dentro de
la transaccion, **todos los locks primero (en orden canonico) y todas las lecturas comunes despues**.
Un `FOR UPDATE` es una lectura **actual** y **no** crea el read view -ni sobre otra tabla, ni cuando
no matchea ninguna fila-, asi que reservar el periodo antes de los locks de fila es gratis. Por eso la
**RESERVA** del periodo (`BloquearPeriodoCajaAsync`) se separo de su **VALIDACION**
(`ValidarPeriodoAbiertoAsync`): la reserva es un lock y va con los locks, la validacion lee y va con
las lecturas.

Barrido de la ventana `BeginTransaction` -> primer lock en los 26 caminos escritores: **dos** la
violaban (`ConfirmarPagoProgramadoAsync`, medido; y `GuardarBorradorAsync`, encontrado por el barrido
y no por una falla - su `Include` corria antes del lock). Los otros 24 toman el lock como primera
sentencia. Las lecturas **anteriores** a `BeginTransaction` no molestan.

### Orden de locks invertido en 6 sitios, con un deadlock reproducido

`ValidarPeriodoAbiertoAsync` toma el gap lock del periodo, y seis escritores la llamaban **despues**
de su lock de fila: `RevertirPagoAsync`, `GastoService.AnularAsync`, `RegistrarCobroAsync`,
`ConfirmarAsync` y `AnularAsync` de ventas, y `CCEmpleadoService.RevertirMovimientoAsync`.

**Deadlock reproducido** con dos sesiones sobre el grafo de locks real:
`ERROR 1213 (40001): Deadlock found when trying to get lock`. `RevertirPagoAsync` tiene la linea de
pago y espera el periodo; `ConfirmarPagoProgramadoAsync` tiene el periodo y espera la linea. Son dos
botones de la misma pantalla sobre la misma linea.

**La precondicion acota el defecto, y hay que decirla:** el ciclo necesita que la fila del cierre del
dia **ya exista**. Con el periodo abierto la reserva es un **gap lock** sobre una fila que no existe,
y **los gap locks de InnoDB conviven entre si** (solo inhiben `INSERT`), asi que dos escritores nunca
se esperan ahi. Verificado en las dos condiciones. O sea: el usuario que iba a recibir *"la caja de
ese dia ya fue cerrada"* recibia a veces un deadlock crudo.

**De los 6, solo ese uno tenia contraparte.** Los otros 5 son **correccion del invariante sin falla
medida** y se tocaron igual, para que el proximo par no lo fabrique en silencio. `AnularAsync` reserva
**dos** dias (el de la venta y hoy) ordenados por fecha ascendente, porque dos anulaciones de ventas
de dias distintos tomarian los mismos dos periodos.

### `LP-036` - el soft delete generico pisaba toda la fila

`Repository<T>.DeleteAsync` hacia `_dbSet.Update(entity)`, que marca **todas** las propiedades como
modificadas: el `UPDATE` del soft delete reescribia **cada columna** con los valores del snapshot que
leyo el que borra, y toda escritura ajena commiteada en el medio se perdia en silencio. Es el escritor
**generico** de `DeletedAt`, asi que aplicaba a **toda** entidad del dominio.

Medido, determinista: con el stock ya descontado a 98 por una venta, un `EliminarAsync` que habia
leido el producto antes lo devolvia a **100** - venta Confirmada, caja posteada, **stock intacto**.
Con fix: 98. Explica la falla **intermitente** del escenario 10b del arnes de la familia (1 de 9
corridas antes de reproducirla a mano).

**No se arregla con un lock, y no corresponde:** el que borra no decide nada sobre una lectura previa.
Es una escritura de mas, y el arreglo es **no escribirla** (se marca solo `DeletedAt` como modificado).

### `LP-038` - `ConfirmarAsync` posteaba con el grafo de antes del lock

El lock y la relectura del `Estado` no alcanzaban: `venta.Items`, `venta.Pagos` y `venta.Total` son la
foto de **antes** de esperar el lock, y la relectura solo traia `Estado` y el `Stock` de los productos.

Medido (escenario 2 del arnes nuevo, N=3 y N=8), con un `GuardarBorradorAsync` que agrega una linea:

| | sin fix | con fix |
|---|---|---|
| estado | **Confirmada** | Borrador |
| items / total de la venta | 7 unidades / **$ 8.470** | 7 unidades / $ 8.470 |
| stock descontado | **2** unidades | 0 |
| ingreso de caja | **$ 2.420** | $ 0 |

**5 unidades salen sin registrar su salida y $ 6.050 no estan en ningun ledger**, y los importes
cierran entre si, que es lo que lo hace invisible.

Se cierra con una **guarda optimista** (comparar total, cantidad de lineas, suma de unidades y suma de
pagos contra la base bajo lock) y **no** recargando el grafo: recargarlo bien exige reordenar el
metodo -el lock de `Productos` necesita los ids de los items, y leer los items antes de ese lock
congela el read view (`LP-035`)- y eso es un rediseno, no un arreglo. Queda **declarado en el codigo**
lo que la guarda no cubre: una edicion que deje los cuatro numeros iguales (cambiar un producto por
otro de igual precio y cantidad) pasa.

**Detalle de orden que costo una regresion:** la guarda tiene que ir **despues** de la de `LP-034`.
Cuando un producto esta dado de baja, el `Include(i => i.Producto)` es un INNER JOIN que pasa por el
query filter y **descarta tambien la fila del `ItemVenta`**, asi que `venta.Items` viene vacia; la
comparacion lee los items ignorando el filtro, las dos fotos dejan de ser comparables, y la guarda
saltaba antes tapando el mensaje de `LP-034`. Lo detecto el escenario 10.5 del arnes de la familia.

### `LP-037` - COMO SE ENCONTRO Y SE MIDIO (registro historico; **CERRADO el 2026-10-07**)

> **Estado: CERRADO.** Se eligio la salida **(b)**, fila centinela por periodo. El arreglo, la
> medicion y la contraprueba estan en la entrada `LP-037` de **Definiciones vigentes**. Lo de abajo
> queda tal como se escribio el 2026-10-06 porque es como se encontro el defecto, **no** como esta
> hoy: el texto que dice "necesita decision" y "queda fallando a proposito" ya no describe el repo.

La reserva del periodo de caja cierra **una** de las dos mitades del descuadre silencioso, y el
XML-doc de `BloquearPeriodoCajaAsync` **afirmaba que cerraba las dos**. Medido con conexiones
separadas y barrera: `CerrarDiaAsync` contra 2 y contra 7 escritores concurrentes deja el dia
**CERRADO con `TotalIngresos = 0`** mientras la suma de los movimientos vivos de ese mismo dia es
**$ 201** y **$ 721**. El arqueo firmado miente y sus numeros son internamente coherentes.

**Por que no la cierra:** mientras el cierre no existe, lo que se toma es un **gap lock**, y los gap
locks **conviven**. El cerrador toma su gap, **lee los totales**, los escritores commitean despues, y
el `INSERT` del cierre -que si espera los gaps- graba los totales que ya habia leido. **La espera
llega tarde: habia que serializar la LECTURA, no el `INSERT`.**

Lo que si queda cubierto: la mitad 1 (un escritor no queda dentro de un dia que se cierra despues) y
el cierre duplicado con su mensaje de negocio.

**Las dos salidas, y no se improviso ninguna:**

- **(a) Lectura de bloqueo** sobre el rango del dia en `CajaMovimientos` al leer los totales. Existe
  `IX_CajaMovimientos_Fecha`, asi que el rango no escala a la tabla. **Sin migracion**, pero convierte
  el descuadre en un **deadlock** contra el escritor que ya tiene el gap del cierre, asi que necesita
  reintento.
- **(b) Fila centinela por periodo** que las dos mitades bloqueen con `FOR UPDATE` sobre una fila
  **que existe**: exclusion mutua real, sin ciclo. Es el plan B que ese mismo XML-doc ya nombraba.
  **Cuesta una tabla y su migracion.**

Hasta que se decida, el invariante queda **medido y FALLANDO** en el arnes, a proposito.

### El sitio donde el mecanismo correcto NO es un lock

`RegistrarAjusteAsync` de la CC de clientes se cierra con **idempotencia por clave natural**
(cliente, dia, tipo, importe, motivo) y **no** con un lock, porque su exposicion real es el **doble
submit** y no dos usuarios: un ajuste no decide nada sobre una lectura previa, y dos ajustes iguales
intencionales son un concepto legitimo del negocio - un lock los serializaria y los dejaria entrar a
los dos. **Por eso la prueba es la del doble submit:** N llamadas del **mismo acto**, misma clave.
Medido: **1 solo movimiento** y las N llamadas devuelven **exito** con el mismo Id, 3 de 3 y 8 de 8.
El lock del cliente esta, pero como **serializador** de la verificacion de duplicado, no como arreglo.

### `ClasificacionAbcAutomaticaService.RecalcularAsync`

**Revisado, no ejercitado por concurrencia**, y se declara asi. `3cf60ab` decidio **no** envolverlo en
una transaccion y la fundamentacion es correcta: la operacion es idempotente (la sugerencia es funcion
pura de las ventas de la ventana), no hay plata ni stock, y una sola transaccion sobre ~112.000
productos mantendria lock de escritura sobre el catalogo entero mientras `ConfirmarAsync` bloquea
`Productos` - cambiaria un contador que miente por una caja frenada. El defecto real era el contador,
y ahora cuenta lo que el motor confirmo.

### Evidencia

- **Build: 0 errores y 9 advertencias**, la linea base exacta (8 x `NU1902` de MailKit/MimeKit +
  `CS0114` de `HomeController.StatusCode`).
- `tools/ArnesReconciliacionTx` (base `laplatense_recon_tx`): **153 OK / 0 FALLADAS**, 8 corridas
  seguidas. Contra el codigo roto: **139 OK / 14 FALLADAS**.
- `tools/ArnesSeisSitiosRestantes` (base `laplatense_seis`, 14 migraciones): **20 OK / 2 FALLADAS**,
  y las 2 son `LP-037`. N=3 y N=8, conexiones separadas y barrera.
- Semantica de snapshot y de gap locks verificada con **dos sesiones MySQL** sobre el motor real, no
  razonada.

**Dos trampas del propio arnes, que valen mas que varios de sus asserts:**

1. **Falso verde por DI.** Sin un doble de `IWebHostEnvironment`, DI no puede construir `AfipService`
   y las 8 llamadas mueren con *"Unable to resolve service"*. Los invariantes pasaban **vacios**:
   nadie confirmaba, nadie guardaba, y *"si quedo Confirmada, lo posteado coincide"* se cumplia de
   taquito. Queda una afirmacion dedicada a que **ningun rechazo sea una excepcion cruda**.
2. **El invariante mal escrito.** La primera version afirmaba *"si quedo Confirmada, nadie le guardo
   items encima"*, y eso es falso como invariante: que un guardado commitee **antes** de la
   confirmacion es correcto. Lo que no puede pasar es que **lo posteado** no coincida con los items de
   la venta confirmada. Con el invariante mal escrito, `LP-038` se veia como una falla del arnes.

### Fixtures que quedan vivos

`laplatense_recon_tx` y el nuevo `laplatense_seis`. No se toco ninguno de los que hay que preservar
(`laplatense_qa_l1`..`l6`, `laplatense_qa_d9`, `laplatense_gate_fix`).
