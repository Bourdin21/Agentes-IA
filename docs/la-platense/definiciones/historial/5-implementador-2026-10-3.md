<!-- Archivado de docs/la-platense/definiciones/5-implementador.md el 2026-10-08 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - 2026-10 (2 bloques archivados)

- Entrega 5 lote 2 — `DevolucionService`, el mecanismo unico de habilitacion, `LP-052` y `LP-053` (2026-10-07)
- Modulo 16 / Entrega 5 lote 1 — esquema de notas de credito + `NotaCreditoService` (2026-10-07)

---

## Entrega 5 lote 2 — `DevolucionService`, el mecanismo unico de habilitacion, `LP-052` y `LP-053` (2026-10-07)

Ultimo lote de construccion del alcance comprometido. Despues de esto solo queda AFIP real, que
espera el certificado del cliente.

**Siete commits locales en `entrega-1-migracion`, SIN push y SIN deploy:**

| Commit | Que cierra |
|---|---|
| `001d983` | `LP-052` — el criterio de habilitacion en UN lugar, leido por las tres puntas |
| `c739896` | Esquema: `Devolucion` + `DevolucionItem` + `ComprobantesAfip.DevolucionId` + migracion |
| `6c1038b` | `DevolucionService` y los tres criterios nuevos |
| `05618b5` | Las tres pantallas y la entrada de menu |
| `5382fb6` | `LP-053` — las tres afirmaciones que faltaban y una cuarta |
| `7f75919` | `tools/ArnesDevoluciones` y los dos huecos que la mutacion encontro en el propio arnes |
| `3758423` | Dos campos muertos del DTO de devolucion, con el comentario de por que no estan |

### Reutilizacion (escaneo de la instruccion 39, seccion 3)

| Paso | Resultado |
|---|---|
| 1. `docs/patrones/cat_resumen.txt` | `PAT-020` (reversion acotada a lo posteado) y `PAT-059` (leer-decidir-escribir bajo lock) ya estaban en el catalogo y se aplicaron |
| 2. Codigo real del origen | `VentaWorkflowService.AnularAsync` de ESTE repo es el precedente directo del circuito de reversion: se copio el criterio (reversion por LINEA de pago contra su neto vivo, contramovimiento fechado HOY, guarda de periodo por los DOS dias) |
| 3. `grep` dirigido | `ShowroomGriffin` para el circuito de mercaderia, **con poda**: su `DevolucionCambio`/`TipoDevolucion` contemplan canje y acá **no aplica** (R8). Sus cantidades son **enteras** y acá tienen que ser `decimal(18,3)` |
| Patron nuevo | **No se agrego ninguno**: `PAT-020` y `PAT-059` ya cubren el criterio, y el mecanismo de habilitacion unico quedo como **seccion de `3-arquitecto-mvc.md` v13**, que es donde el arquitecto lo elevo a regla |

### El mecanismo unico de habilitacion — `LP-052` deja de ser un fix puntual

`FerreteriaLaPlatense.Domain/Reglas/HabilitacionDeAccion.cs` (nuevo). Cada metodo devuelve **la razon
por la que NO se puede**, y `null` cuando se puede. Lo consumen **las tres puntas**: la vista (oculta
el boton y muestra la razon como leyenda), el `GET` (redirige con ese mismo texto) y el `POST` (rechaza
con ese mismo texto). Ninguna tiene su propia copia de las condiciones.

**El defecto medido que lo justifica:** el boton de `Ventas/Details.cshtml` guardaba **TRES**
condiciones y el `GET` de `NotasCreditoController` guardaba **UNA** (`TodoAcreditado`). No faltaba la
guarda — **habia guarda y no era la misma** — asi que un chequeo de *"el GET esta protegido"* daba
**verde** mientras `GET /NotasCredito/Emitir/5` sobre una nota de credito devolvia **200** con el
formulario armado, rotulando la NC como "factura".

**Lo que NO entro al mecanismo, declarado para que no se lea como omision:**

- **Las guardas de concurrencia.** *"¿la fila se dio de baja mientras preparabamos la pantalla?"* no es
  un criterio de habilitacion: es la segunda mitad de la relectura bajo lock, solo existe dentro de una
  transaccion y la vista no puede evaluarla. Vive en el Service, al lado de su lock.
- **Los topes por item.** El criterio contesta *"¿se puede entrar a esta pantalla?"*; el tope contesta
  *"¿esta cantidad es valida?"*. El segundo necesita el dato releido bajo lock y no tiene sentido en un
  boton.

Los **tres criterios nuevos del lote nacieron con el mecanismo**, que es la condicion que puso la
decision de arquitectura: venta con devoluciones no se anula, item devuelto no se factura, y el de la
nota de credito (que entro con `LP-052`).

### `DevolucionService` — las cuatro cosas que tiene que hacer bien

1. **El tope por item es lo vendido menos lo ya devuelto**, releido con el lock tomado (`PAT-059`).
2. **La plata se revierte acotada a lo realmente posteado** (`PAT-020`), linea de pago por linea,
   contra su propio neto vivo, y con el **MISMO `PagoVentaId` y `EsReversion = true`** que usa la
   anulacion. Eso ultimo no es una etiqueta: es lo que hace que
   `ObtenerNetoPosteadoPorPagoVentaAsync` descuente estas reversiones, asi que varias devoluciones
   parciales de la misma venta **no pueden sumar mas de lo que entro**.
3. **La tarjeta en cuotas se revierte SIN el recargo** (ver el defecto propio (b) de abajo).
4. **El reingreso de stock escribe LAS DOS COSAS**: `Producto.Stock` sobre la entidad trackeada **y**
   la fila del ledger `MovimientoStock`.

**Correccion a una premisa del brief, y la direccion importa:** el brief decia *"nunca escribas
`Producto.Stock` directo: el proyecto tiene un unico escritor y se respeta"*. El unico escritor que el
proyecto defiende es el de **la TABLA del ledger**, no el de la columna `Stock` —
`IMovimientoStockService.RegistrarMovimientoAsync` declara **explicito** que NO toca el stock del
producto, porque lo mueve el caller sobre la instancia que ya tiene cargada (asi lo hace
`OrdenCompraService.RecibirAsync`). Obedecer el brief literalmente habria dejado el stock **sin mover**
y la devolucion habria reingresado mercaderia que no vuelve a `Producto.Stock`: el ledger diria que
entro y el catalogo no. `Σ MovimientoStock.Cantidad` sigue **sin** reconstruir `Producto.Stock`, que
tiene tres escritores.

**El reparto de la plata, dicho con precision:**

```
proporcion = totalDevuelto / (Venta.Subtotal + Venta.TotalIVA)
importe de cada linea = min( round(pago.Monto * proporcion, 2) , remanente de la base , neto vivo )
```

El denominador es el total **sin** el recargo de cuotas, que es exactamente la suma de los `Monto` de
los pagos cuando la venta esta cubierta — asi que una devolucion total da proporcion 1 y revierte el
`Monto` completo de cada linea, **ni un peso de recargo**.

### Los dos defectos propios, encontrados ANTES de medir

**(a) El stock de un producto repetido en dos lineas.** El reingreso se escribia dentro del bucle por
item (`Stock = fresco + cantidad`), y un producto que aparece en **DOS lineas de la misma venta** —
caso real: dos tramos del mismo caño con descuentos distintos, y `GuardarBorradorAsync` no lo impide —
quedaba con la segunda linea **pisando a la primera sobre la MISMA base releida**. Volvia **menos**
mercaderia de la que el cliente trajo, con los importes cerrando y sin que nada avisara. Es la misma
familia del read-modify-write que el lock existe para cerrar, solo que los dos competidores son dos
iteraciones del propio bucle. Se acumula por producto antes de escribir.

**(b) El recargo de cuotas volvia en la devolucion total.** La caja postea `Monto + recargo` al
confirmar, asi que el **neto vivo de la linea INCLUYE el recargo**. Acotar contra el neto vivo a secas
dejaba pasar el recargo entero: plata que la ferreteria pone de su bolsillo porque la financiera ya la
cobro. La cota correcta es el **remanente de la BASE**, derivado del propio neto vivo
(`Monto + recargo − neto`) en vez de contarse aparte, para no tener un segundo contador del mismo
numero. Se encontro **calculando el fixture del arnes**, antes de correrlo.

### El criterio "lo devuelto no se factura" — por que es una resta de dos terminos

`pendiente = cantidad − yaFacturada − max(0, devuelta − acreditada)`.

Restar la devolucion **completa** es la forma obvia y esta **mal**: una devolucion de items facturados
emite una NC, y esa NC **no reabre el pendiente** (R18). Si se restara entera, la parte ya acreditada se
restaria **dos veces** —una por la factura que la cubre y otra por la devolucion— y el pendiente se iria
a **negativo** en toda venta facturada y devuelta. Los dos casos:

| Caso | Acreditado | No facturable | Pendiente |
|---|---|---|---|
| Venta 5, facturada 3, devuelve 2 **sin factura** | 0 | 2 | 5 − 3 − 2 = **0** (lo que quedaba por facturar volvio) |
| Venta 5, facturada 3, devuelve 2 **de lo facturado** | 2 | 0 | 5 − 3 − 0 = **2** (R18: la NC no reabre nada) |

### El barrido, por `grep` y con el numero declarado

Los lectores del "ya facturado" (filtro `ComprobanteAsociadoId == null`) pasaron de **CUATRO a SEIS**
con este lote:

| # | Sitio | Que decide |
|---|---|---|
| 1 | `FacturacionParcialService:429` | el tope de la emision |
| 2 | `FacturacionParcialService:495` | el titulo "Ya facturado de esta venta" |
| 3 | `VentaWorkflowService:172` | el badge "Facturada en parte" del listado |
| 4 | `VentaWorkflowService:1732` | el pendiente del detalle |
| 5 | `DevolucionService:806` | la columna "Facturado" de la grilla de devolucion |
| 6 | `DevolucionService:1061` | el planificador de notas de credito |

El **quinto consumidor por carambola** sigue siendo `VentaWorkflowService:1082` (el mensaje *"ya esta
facturada por completo en N comprobante(s)"*), que se alimenta del lector 2. **Y los TRES que forman el
pendiente (1, 3 y 4) se barrieron juntos y en el mismo commit**, que es la regla que quedo escrita
despues de LP-040.

### `NotaCreditoService` partido en cascara y nucleo

`EmitirEnTransaccionAsync` corre dentro de la transaccion del caller con el lock **ya tomado**, porque
la mercaderia, la plata y el documento fiscal son el **mismo hecho**: emitir la NC en una transaccion
aparte dejaria, ante un fallo en el medio, mercaderia devuelta y plata revertida sin el documento que lo
acredita. Mismo criterio que `ICajaMovimientoService` y `ICuentaCorrienteClienteService`, que tampoco
controlan la transaccion.

**Al partirlo quedaron DOS comentarios falsos y se corrigieron en el mismo commit** (pasada 3 del
barrido LP-002): *"lecturas comunes FUERA de la transaccion"* (ahora van **despues del lock**, que es el
orden canonico de LP-035) y la pre-evaluacion del criterio de habilitacion, que paso a leer **las mismas
filas** que la relectura — se **elimino** en vez de dejarla como dos evaluaciones indistinguibles.

**Y la formula del cargo de IVA se movio al dominio** (`CargoDeIvaDiferido.Devolucion`) porque desde
este lote tiene **DOS consumidores**: la emision y el preview de la devolucion. Dos copias harian que el
preview mostrara un importe y la escritura posteara otro — justo lo que la comparacion *"lo que el
usuario confirmo == lo que el Service calculo"* existe para impedir.

### El debito vivo de cuenta corriente, en UN solo lugar

`ObtenerDebitoVivoVentaAsync` es ahora `Σ(Debito, VentaFiado) − Σ(Credito, AnulacionVenta) −
Σ(Credito, DevolucionVenta)`. Hasta este lote el unico reversor era la anulacion y el calculo vivia
dentro suyo; con **un segundo reversor**, dos copias de esa resta serian dos criterios para el mismo
numero. **El modo de falla concreto, medido por mutacion:** si la devolucion no restara los creditos de
devoluciones anteriores, cada devolucion parcial leeria el **mismo** vivo y la suma superaria el debito,
dejando saldo a favor por plata que nunca se debio.

### Pantallas

| Pantalla | Nota |
|---|---|
| `Devoluciones/Registrar` | **El preview lo calcula el SERVICE**, por AJAX a `Devoluciones/Preview`, no el JS. Si la pantalla hiciera su aritmetica, la comparacion contra `TotalARevertirConfirmado` seria entre dos criterios distintos y no garantizaria nada. Muestra stock, plata por medio de pago con su destino, el credito de IVA, los comprobantes que se acreditan, **el recargo que NO vuelve** y el aviso de que una devolucion total deja la venta `Anulada` |
| `Devoluciones/Index` | DataTables server-side, daterangepicker + Select2 de cliente, filtros persistidos en `Session` con "Limpiar filtros", y busqueda global que matchea **importes y fechas** (no solo texto) |
| `Ventas/Details` | Boton de devolucion y tarjeta de devoluciones. La tarjeta existe porque una devolucion **PARCIAL no cambia `Venta.Estado`**: sin ella, una venta devuelta en parte se veria **identica** a una intacta |

**Hallazgo del design system:** el proyecto **no tenia** la clase con `white-space: nowrap` para
importes que el estandar pide **desde agosto de 2026** como parte del tema base — las vistas vienen
concatenando `$ @valor` sin nada que impida que el navegador corte entre el signo y el numero, el mismo
bug que se midio en KOI. Se agrego `.ov-monto` al tema y la usan las pantallas de este lote. **Las
anteriores NO se retocaron** (decenas de celdas, pantallas ya verificadas por QA, y seria un refactor
cosmetico): queda declarado como **deuda del design system**, no como resuelto.

### Migracion EF

`20261007162451_Entrega5_Devoluciones` — **aditiva pura, sin backfill**: 2 tablas nuevas
(`Devoluciones`, `DevolucionItems`) y **1 columna nullable** sobre una tabla preexistente
(`ComprobantesAfip.DevolucionId`, FK Restrict). Ni una columna `NOT NULL` sin default sobre una tabla con
filas, ningun `UNIQUE` nuevo, la unica FK nueva es nullable, y **cero filas que reconstruir** — toda
devolucion es un hecho futuro y las anteriores al modulo no se pueden inventar.

**NO se agrego ninguna columna a `Ventas`, y es deliberado: no hay flag "con devoluciones".** Un
derivado persistido habria que mantenerlo sincronizado con las cantidades en cada devolucion y en cada
baja, que es exactamente la clase de dato que produjo LP-039 y LP-040.

Valores nuevos de enum **al final y explicitos**: `TipoMovimientoStock.Devolucion = 5` y
`OrigenMovimientoCC.DevolucionVenta = 7`, este ultimo con sus **DOS lectores** de
`CuentaCorriente.cshtml` propagados en el mismo commit (LP-002).

### `LP-053` — las tres afirmaciones que faltaban, y una cuarta

El arnes del modulo 16 pasa de **45 a 63** afirmaciones (63 OK / 0 FALLADAS, exit 0, idempotente).

| Familia | Que cubre | Como se mide |
|---|---|---|
| 10 | el filtro de `ListarComprobantesAsync` (el 4to lector) | por **delta** y por la propiedad que lo explica (`EsNotaCredito`); se cubre tambien el 5to consumidor por carambola. El escenario factura en **dos tandas**: con 1 contra 1 el conteo no distingue "cuento facturas" de "cuento documentos" |
| 11 | la guarda del comprobante en `Error` (R17) | `grep EstadoComprobanteAfip.Error` daba **cero hits**. El estado se **siembra con UPDATE** porque ningun servicio lo produce hoy, y queda declarado; con **control positivo** (devuelto a `Pendiente`, la misma emision funciona) |
| 12 | la **proporcion** y la **cota `Math.Min`** | sembrando `DiferenciaIvaCobrada` **por debajo** de `Iva`. El importe esperado va **HARDCODEADO**: si saliera de `CargoDeIvaDiferido`, una mutacion cambiaria los dos lados a la vez |
| 13 | las tres puntas dan la **misma razon** | el `GET` contesta un motivo y el `POST` rechaza con **el mismo texto** |

**Mi limitacion declarada acotaba de MENOS**, y es el hallazgo del parte: decia que la rama proporcional
no era discriminable (cierto, porque hoy `DiferenciaIvaCobrada == Iva` siempre) y **se olvidaba de que la
cota tampoco lo era, por el mismo motivo**. Las dos quedaban sin medir y **solo una estaba declarada**.

**La cuarta no venia en el parte y la encontro la mutacion:** el mutante que apaga la tercera condicion
del criterio (`pendienteDeAcreditar <= 0`) **sobrevivia** con 59/59 en verde. **No era una afirmacion
vacia: era un SEGUNDO MECANISMO no declarado** — el tope por item frena la emision igual, con otro
mensaje. El dato **no** se corrompe (por eso ninguna afirmacion de integridad lo notaba) pero **la puerta
se abre**, que es textualmente LP-052. La familia 13 lo mide **por la RAZON y no por el dato**.

**Defecto propio del instrumento**, encontrado en la primera corrida: la familia 10 llamaba a
`FacturarTodoAsync` dos veces sobre la misma venta y la segunda no tenia nada que facturar — el arnes
murio con **exit 3 despues de medir 46 afirmaciones en verde**. Se agrego `FacturarParcialAsync`.

### `tools/ArnesDevoluciones` — 63 OK / 0 FALLADAS, y los tres sobrevivientes

Los **dos casos que el brief pidio sembrar**, medidos:

- una devolucion **PARCIAL de items FACTURADOS** reingresa stock, revierte la plata, emite la NC y deja
  el pendiente de facturar y el badge **IDENTICOS** (R18/R19) — medido por **los TRES lectores** del
  pendiente, no por uno;
- una devolucion de items **NO facturados** no emite **ningun** comprobante, y lo devuelto **sale** del
  pendiente.

**Corrida mutante: 18 mutantes derivados del DIFF, 17 muertos y 1 declarado.** Los tres que
sobrevivieron a la primera corrida son el valor de medir asi, y **las tres causas son distintas**:

| Mutante | Por que sobrevivia | Que se hizo |
|---|---|---|
| badge del listado | **AFIRMACION VACIA mia**: la unica que miraba el badge lo hacia sobre una venta que la devolucion total habia dejado `Anulada`, y `ListarAsync` **no la devuelve** — la fila venia `null` y el badge salia `false` **por omision**, con y sin el fix | se midio sobre una venta **VIVA** (4 vendidos, 2 facturados, 2 devueltos sin NC: pendiente 0 y badge apagado; sin la resta serian 2 y quedaria prendido) |
| stock sin acumular | **HUECO DEL FIXTURE**: ningun escenario sembraba el **mismo producto en dos lineas** de la misma venta | familia 3B, con cantidades **DISTINTAS** (1 y 3) para que el delta correcto (4) no coincida con ninguno de los parciales |
| rollback de la NC | **SEGUNDO MECANISMO**: la unica forma que el arnes tiene de hacer fallar la emision es un trigger, que la hace fallar **por excepcion**, y entonces el `catch` hace el trabajo | **declarado y no medido**: alcanzar la rama exigiria un `ServiceResult` fallado **sin** excepcion, hoy inalcanzable porque el planificador y la emision leen el comprobante bajo el **mismo** lock y en la **misma** transaccion |

**Y el primer mutante que escribi para el hueco del stock era INVALIDO:** `.Take(1)` sobre un
diccionario **ya indexado por producto** es un no-op, porque las dos lineas del mismo producto son UNA
entrada. **Un mutante que sobrevive por estar mal escrito no es un agujero de cobertura**, y confundir
las dos cosas manda a reescribir una afirmacion que estaba bien. El mutante correcto escribe el
reingreso **por item** y la familia 3B lo mata.

### Evidencia de cierre

| Que | Resultado |
|---|---|
| Build de la solucion, `--no-incremental` | **0 errores / 9 advertencias** (8 `NU1902` + 1 `CS0114` preexistente): linea base exacta |
| Control positivo de Razor | Se inyecto `@Model.PropiedadQueNoExiste` en `Devoluciones/Registrar.cshtml` y el build **fallo senialando ese archivo y esa linea** (CS1061, linea 14); restaurado, vuelve a 0 errores. **Las vistas nuevas se compilan de verdad** |
| Evidencia organica del mismo mecanismo | el primer `--no-incremental` fallo con **dos CS1503** en `Details.cshtml` (`Model.Id` es `int?`) — un incremental habria dado 0 errores sin mirarlas |
| `tools/ArnesNotaCredito` | **63 OK / 0 FALLADAS / 0 NO MEDIDAS**, exit 0, idempotente |
| `tools/ArnesDevoluciones` | **63 OK / 0 FALLADAS / 0 NO MEDIDAS**, exit 0, idempotente en dos corridas seguidas |
| `tools/ArnesReconciliacionTx` | **153 OK / 0 FALLADAS** — sin regresion por el refactor de `AnularAsync` |
| `tools/ArnesSeisSitiosRestantes` | **32 OK / 0 FALLADAS** |
| Base de prueba | `laplatense_lote2`, **20 migraciones**, armada con `dotnet ef database update`. **`laplatense_dev` NO se toco** (sigue en 18) ni produccion (sigue en 8) |

**Dato operativo:** la guarda de identidad de los arneses es por **substring**, asi que una base
llamada `laplatense_dev16` **aborta con exit 2** (contiene `laplatense_dev`). Es la guarda funcionando,
no un bug — pero conviene saberlo antes de perder una corrida: el nombre de la base desechable no puede
empezar con el de una base prohibida.

### Riesgos y supuestos

- **AFIP sigue deshabilitado** y es el unico gate de la Entrega 5. Las notas de credito nacen en
  `Pendiente` sin CAE y eso es el estado **normal**.
- **El planificador de notas de credito saltea los comprobantes en `Error`**, usando el mismo criterio
  de habilitacion. Hoy esa rama es **inalcanzable** por los servicios reales (sin certificado todos los
  comprobantes estan en `Pendiente`); **el dia del certificado deja de serlo**, y entonces una devolucion
  de items facturados en un comprobante fallido **no emitira NC por esa parte**. Esta declarado en el
  XML-doc del planificador.
- **`ObtenerYaFacturadoPorItemAsync` SI cuenta los comprobantes en `Error`** y el planificador **no**.
  Es una asimetria **preexistente** (el filtro de ese lector es solo de soft delete) que este lote no
  cambia: con un comprobante en `Error`, un item apareceria como "facturado" en el pendiente y no
  generaria NC al devolverse. **Hoy inalcanzable**, igual que el punto anterior, y fuera del alcance de
  este lote — pero hay que resolverlo **antes** de habilitar AFIP.
- **El preview acota al neto vivo de AHORA**, no al releido bajo lock. Si cambia en la ventana, el POST
  lo rechaza con el mensaje de "el importe cambio mientras confirmabas", que es el comportamiento
  correcto.

### Pruebas minimas para QA

1. **Devolucion parcial de una venta sin factura cobrada en efectivo.** Verificar: stock del producto
   sube exactamente lo devuelto, hay un movimiento en el ledger de stock con origen "Devolución de
   mercadería", hay un egreso de caja por el importe del **precio efectivo** (no el de lista), **no se
   emitio ningun comprobante**, y la venta **sigue Confirmada**.
2. **Devolucion parcial de items FACTURADOS.** Verificar: se emitio la nota de credito, el cliente
   recibio el credito de IVA en su cuenta corriente, y **el pendiente de facturar y el badge "Facturada
   en parte" quedaron IGUALES** que antes de la devolucion.
3. **Devolucion de una venta cobrada con tarjeta en cuotas.** Verificar que el egreso de caja es el
   **monto base** y **no** incluye el recargo, y que el preview lo avisa antes de confirmar.
4. **Devolucion total.** Verificar que la venta pasa a `Anulada` y que el movimiento de caja queda
   neteado en cero.
5. **Los dos criterios nuevos por la URL, no por el boton.** Entrar a mano a
   `/Ventas/Details/{id}` de una venta con devoluciones e intentar anularla (el POST tiene que rechazar
   con el texto de la leyenda), y entrar a `/Devoluciones/Registrar?ventaId={id}` de una venta ya
   devuelta por completo (tiene que redirigir con el motivo).
6. **El listado de devoluciones:** filtrar por rango de fechas y por cliente, buscar **por importe**
   escribiendo solo el numero, buscar por fecha en `dd/MM/yyyy`, y comprobar que "Limpiar filtros" los
   borra **tambien al volver a entrar** a la pantalla.
7. **Lo devuelto no se factura:** devolver items sin facturar y verificar que la pantalla de facturacion
   ya no los ofrece, y que forzar el POST con esa cantidad **rechaza nombrando la devolucion**.

### Checklist de salida para merge

- [x] Build de la solucion `--no-incremental`: 0 errores, 9 advertencias (linea base exacta)
- [x] Control positivo de compilacion de Razor sobre una vista nueva
- [x] Migracion EF aditiva pura, sin backfill, verificada columna por columna
- [x] Los cuatro arneses en verde, dos de ellos nuevos o ampliados, todos idempotentes
- [x] Corrida mutante derivada del **diff**: 24 mutantes en total, 23 muertos y 1 declarado
- [x] Barrido de lectores por `grep` con el numero declarado (4 -> 6)
- [x] Valores nuevos de enum al final, explicitos, con sus lectores propagados (LP-002)
- [x] Produccion y `laplatense_dev` **no se tocaron**
- [ ] **Push y deploy: NO.** Siete commits locales en `entrega-1-migracion`
- [ ] **Re-verificacion de QA de `LP-052` y `LP-053`**: aplicados, **pendientes de re-verificacion**

### Partes de defecto aplicados en esta corrida

| Id | Archivos | Estado |
|---|---|---|
| `LP-052` | `Domain/Reglas/HabilitacionDeAccion.cs` (nuevo), `Application/DTOs/ComprobanteAfipDtos.cs`, `Application/DTOs/NotaCreditoDtos.cs`, `Infrastructure/Services/NotaCreditoService.cs`, `Web/Controllers/NotasCreditoController.cs`, `Web/Views/Ventas/Details.cshtml` | **aplicado, pendiente de re-verificacion** |
| `LP-053` | `tools/ArnesNotaCredito/Program.cs` (familias 10, 11, 12 y 13) | **aplicado, pendiente de re-verificacion** |
| `LP-054` | Ninguno de codigo: es una falla de metodo de QA. Se **adopto** su regla — la base de prueba se armo con `dotnet ef database update` y queda escrito en el encabezado de los dos arneses | **adoptado** |

El cierre de un defecto lo declara QA en su corrida siguiente, nunca el implementador.
## Modulo 16 / Entrega 5 lote 1 — esquema de notas de credito + `NotaCreditoService` (2026-10-07)

**Dos commits locales en `entrega-1-migracion`** (`c5538d3` esquema, `a3f8d6d` servicio + pantalla),
**SIN push y SIN deploy**, **una** migracion EF aditiva, **produccion no se toco** (sigue en 8
migraciones; el deploy esta postergado por la credencial rotada). Base de prueba: clon desechable
`laplatense_nc16`, creado y dropeado por el arnes — **no se toco `laplatense_dev`, ni produccion, ni
los fixtures de QA** (`laplatense_gate_cr04`, `laplatense_ensayo_prod` quedaron intactos; hay una
guarda en el arnes que aborta con exit 2 si la cadena los menciona).

### Escaneo de reutilizacion (instruccion 39 §3)

Paso 1 (`cat_resumen.txt`) dio **tres** matches y los tres se usaron: **PAT-060** (comprobante fiscal
parcial 1:N con la diferencia de impuesto cargada al ledger — es nuestro propio CR-02 y define el
terreno), **PAT-020** (reversion acotada a lo posteado) y **PAT-006** (circuito WSFEv1). Paso 2: el
precedente fiscal de `marihogar` (`IComprobanteAfipService.GenerarNotaCreditoAsync` linea 49 +
`ComprobanteAfipService`) se reuso en la **forma** — NC como fila de la misma tabla con auto-FK, tipo
derivado del original — y **no en la aritmetica**: alla el 21% esta hardcodeado, las cantidades son
`int` y el descuento va en cascada sobre el precio. **Sin precedente:** la devolucion del cargo de
IVA, que es propia de este proyecto. **Patron nuevo agregado al catalogo: `PAT-064`.**

### Verificacion de las premisas del brief (pasada 0 del barrido LP-002)

Las ocho premisas verificadas contra el arbol. **Siete ciertas** (`ComprobanteAfip` sin
`ComprobanteAsociadoId` ni `Motivo`; `DiferenciaIvaCobrada` presente; `TipoComprobanteAfip` con solo
1 y 6; `EstadoComprobanteAfip` con tres valores; `OrigenMovimientoCC` hasta 5; no existe
`AnulacionVentaService` ni `DevolucionService`; linea base de build 0/9 con el `CS0114` preexistente).
**Dos correcciones:**

1. **`VentaWorkflowService:1484` no es la anulacion, es una linea de adentro.** `AnularAsync` se
   declara en **1165**. La premisa de fondo (la anulacion sin comprobante ya existe y funciona) es
   cierta y no se toco.
2. **"`FacturacionParcialService` no cambia en este lote" es FALSA, y la direccion importa.** El
   brief lo decia para fijar R18 (el pendiente no resta las NC), y ese criterio se respeto — pero
   **dejar el codigo sin tocar NO lo respeta: lo rompe**. Ver abajo.

### El cambio que el brief no preveia, y es el de mayor radio

Una NC es una fila mas de `ComprobantesAfip` **sobre la misma venta**, con sus propios
`ComprobanteAfipItem` de cantidad **POSITIVA** (esta tabla no es un ledger de signos). Los tres
lectores del "ya facturado" sumaban *todo comprobante vivo de la venta*, asi que sin tocarlos:
acreditar 2 de las 5 unidades que un comprobante facturo dejaba el facturado en **7 sobre una venta
de 5** → pendiente **negativo**, badge "Facturada en parte" **apagado** sobre una venta con items sin
facturar, y el tope duro de R13 **rechazando refacturaciones legitimas de otros items** sin que nada
explique por que.

Los tres llevan ahora `c.ComprobanteAsociadoId == null`, barridos **juntos y en el mismo commit**:
`FacturacionParcialService.ObtenerYaFacturadoPorItemAsync`, el listado paginado de
`VentaWorkflowService` y `ObtenerDetalleAsync`. **El filtro MANTIENE el criterio de R18, no lo
cambia**, y restarlas seria peor (devolveria los items al pendiente: el mismo item vendido una vez y
facturado dos). `TieneComprobantes` **no** lleva el filtro, a proposito: una NC tambien es un
documento fiscal vivo, y es el mismo criterio con el que la guarda de `AnularAsync` cuenta
comprobantes.

### Esquema (commit `c5538d3`)

- **`TipoComprobanteAfip`: `NotaCreditoA = 3` y `NotaCreditoB = 8`, los codigos de AFIP.** El XML-doc
  del enum quedo escrito para que el proximo no repita el error: estos valores **no son nuestros**,
  los fija AFIP y el WSFEv1 los valida en `CbteTipo`, asi que la regla del proyecto de "todo valor
  nuevo al final" **no aplica**. Con la tabla de codigos completa (1/2/3/6/7/8/11/13).
- **Los comprobantes C no entran, y es una decision verificada, no una omision.** Un C lo emite un
  Monotributista, y este sistema **deriva** el tipo de la condicion de IVA del **RECEPTOR** (A al
  Responsable Inscripto, B al resto) — derivacion que solo tiene sentido si el emisor es Responsable
  Inscripto. Ni el Analisis ni `AfipSettings` tienen nada de la condicion fiscal del emisor, y **no
  hay camino de codigo que pudiera producir un C**. Un valor de enum que nada puede emitir es una rama
  muerta en todos los `switch` que lo lean.
- **`ComprobanteAfip.ComprobanteAsociadoId`** (auto-FK nullable, `Restrict`) + **`Motivo`** (500).
  **No hay flag "es nota de credito"**: se infiere de la FK, igual que en `marihogar`. `Motivo` es
  trazabilidad interna y **nunca** viaja a AFIP (el WSFEv1 no tiene campo).
- **`OrigenMovimientoCC.DevolucionDiferenciaIva = 6`** (aca si al final: el enum es nuestro y sus
  enteros estan persistidos), propagado a los **dos** lectores del ledger en el mismo commit
  (LP-002): el combo "Origen" y el mapa `etiquetasOrigen` de `Views/Clientes/CuentaCorriente.cshtml`.
- **Migracion `20261007132638_Modulo16_NotasDeCredito_ComprobanteAsociadoYMotivo`: aditiva pura**, y
  es verificable operacion por operacion — 2 `AddColumn` nullable, 1 `CreateIndex`, 1 `AddForeignKey`.
  Cero `AlterColumn`, cero `DropColumn`, cero `Sql()` de backfill. Ninguna fila existente necesita un
  valor: un comprobante con `ComprobanteAsociadoId` en null **es** una factura, que es lo que son
  todas las filas de hoy. `Down` simetrico. Dev pasa de 18 a 19 migraciones **cuando se aplique**;
  este lote la aplico **solo** al clon desechable.
- **Barrido del enum (pasada 3):** al pasar de 2 valores a 4, `Views/Ventas/Details.cshtml` rotulaba
  con `== FacturaA ? "Factura A" : "Factura B"` — una **NC B** habria salido como **"Factura B"** en la
  pantalla que mas se consulta. El tipo se muestra ahora por `ComprobanteAfipListItemDto.TipoLegible`,
  unico traductor del enum y con rama por defecto. `FacturacionParcial/Emitir.cshtml` ya tenia su
  `_ =>` y no necesito cambio (verificado, no supuesto).

### `NotaCreditoService` (commit `a3f8d6d`)

Emite contra **un comprobante**, puede ser parcial, y reemplaza a `IAnulacionVentaService` /
`AnulacionVentaViewModel`, que nunca se construyeron y partian de "un comprobante por venta".

**La devolucion del cargo de IVA, que es la razon de construir esto primero.** Si el comprobante
tiene `DiferenciaIvaCobrada > 0`, la NC postea un **Credito** en la CC del cliente con el origen
nuevo, **en la misma transaccion**. Sin eso el cliente queda debiendo el IVA de una factura que
fiscalmente ya no existe.

**La regla del remanente, que es la parte que no se ve hasta medirla.** El importe se reparte en
proporcion al IVA acreditado, pero **cuando la NC cierra el comprobante se devuelve el REMANENTE
EXACTO** y no la proporcion redondeada. Tres NC parciales redondeando cada una por su cuenta pueden
dejar al cliente con **$ 0,01 de deuda eterna** por el IVA de una factura acreditada por completo —
un saldo que ninguna pantalla deja cerrar. El fixture del arnes esta **disenado para medir ese
centavo** (ver abajo).

**El "ya devuelto" sale de `ComprobantesAfip`, no del ledger**, y eso ahorra una columna: en una
factura `DiferenciaIvaCobrada` significa "cuanto le cargue al cliente" y en una NC "cuanto le
devolvi", con la direccion dada por el tipo de fila. Del ledger es **imposible** leerlo:
`MovimientoCCCliente` guarda `VentaId` y no el comprobante, asi que no se puede saber cual de los N
comprobantes de una venta genero cada movimiento. Y leerlo de ahi tiene la ventaja de que **lo
serializa el mismo lock** que serializa el tope de cantidades.

**Precio efectivo congelado, copiado del comprobante** — no el de lista ni un recalculo desde la
venta. Es la leccion que CR-02 ya pago: descuento y recargo viven en el `Subtotal`. El IVA se
redondea **por linea** y despues se suma, mismo orden que la emision, para que una NC total de
exactamente el importe de su factura.

**Concurrencia.** Transaccion **antes** de leer, lock de la fila de la **VENTA** como primera
sentencia, relectura **REAL** por `RelerBajoLockAsync` (nunca `ReloadAsync`: `ComprobanteAfip` hereda
`SoftDestroyable`). El lock es el de la venta y no el del comprobante porque **con una sola fila
serializa las dos carreras**: dos NC simultaneas sobre el mismo comprobante y una NC contra una
emision de factura (que bloquea esa misma fila). Un lock propio sobre `ComprobantesAfip` no agregaria
exclusion y si agregaria una tabla al orden canonico, que es como se fabrica un deadlock
intermitente. No se bloquea `Clientes`: el Credito es una escritura ciega sobre un ledger aditivo y
el importe **no sale del saldo**, sale de `ComprobantesAfip`.

**LP-034.** NO se usa `Include(c => c.Venta)` ni `ThenInclude(ci => ci.ItemVenta)`: las dos
navegaciones son requeridas y las tres entidades son `SoftDestroyable`, asi que el INNER JOIN contra
el query filter global haria **desaparecer el comprobante entero** (o perder una de sus lineas, y con
ella su cantidad del tope) si la venta, el item o el producto estuvieran de baja. Los datos de rotulo
se traen aparte con `IgnoreQueryFilters`: **un producto dado de baja del catalogo no puede borrar una
linea de un documento fiscal**.

**Guardas, y las tres son alcanzables.** Se rechaza acreditar un comprobante que **ya es una NC**
(eso seria una nota de debito, fuera de alcance) y uno en **`Error`** (nunca se emitio: el camino es
darlo de baja, R17). **No se exige `Emitido`**: hoy, con AFIP apagado, todos estan en `Pendiente`, asi
que esa guarda no se alcanzaria nunca y cambiaria de comportamiento el dia del certificado sin que
nadie lo note — es el razonamiento que ya dejo escrito la guarda de `AnularAsync`.

**`Venta.Estado` no se toca y no es un olvido:** R19 (el estado solo avanza) y R18 (el pendiente no se
reabre). Despues de una NC el pendiente de facturar de la venta es **exactamente el mismo**, y eso es
una afirmacion del arnes, no una declaracion.

### El criterio de la familia LP-039/LP-040, en las dos puntas desde el primer commit

El tercero de los cuatro criterios que esta entrega agrega — *"este comprobante ya tiene una NC por
estos items"* — vive en el Service (tope por item releido bajo lock) **y** en la UI
(`ComprobanteAfipListItemDto.PendienteDeAcreditar`, calculado en la base en la misma consulta que ya
trae el comprobante, mas el redirect del Controller para el link pegado). **Es el MISMO numero**: el
arnes lo afirma (5.3). Un gate que preguntara por el **estado** del comprobante, o por *"¿tiene alguna
NC?"*, seria exactamente la forma de LP-039 — **una NC PARCIAL deja el comprobante con NC y con
pendiente al mismo tiempo**, y el boton tiene que seguir estando.

### Hallazgo propio del barrido (pasada 3: buscar el TEXTO de la regla)

**`FacturacionParcial/Emitir.cshtml` lista los comprobantes de la venta bajo el titulo "Ya facturado
de esta venta", y con las NC adentro ese titulo pasa a ser falso.** Peor: sugiere que esa NC explica
un pendiente que **no** explica (R18). Antes del modulo 16 la lista no podia contener otra cosa que
facturas, asi que el titulo era cierto; agregar las NC a la misma tabla lo volvio falso **sin tocar
una linea de esa pantalla**. `ListarComprobantesAsync` filtra ahora `ComprobanteAsociadoId == null` y
el XML-doc del DTO dice por que la exclusion **es** el titulo. Las NC se ven en el detalle de la
venta, indentadas bajo la factura que acreditan y con el signo de la columna de IVA invertido (en una
factura es un cargo, en una NC una devolucion: el mismo campo con la direccion dada por el tipo de
fila, asi que el signo se dibuja o la columna miente).

### Pasada 3, segunda cosecha: el comentario que mi propio commit volvio falso

`AfipService.MapearCondicionIvaReceptor` decia que su `is 1 or 3` era **preventivo** porque
*"TipoComprobanteAfip solo tiene FacturaA=1/FacturaB=6, asi que no hay forma de llegar a el todavia"*.
El commit del esquema lo volvio falso. **Se corrige el comentario, no el codigo**: la rama ya estaba
bien escrita dos entregas antes y por eso hoy no hay nada que arreglar ahi — lo que no puede pasar es
que el repo prometa una limitacion que ya no tiene.

### Evidencia

**Build no incremental: 0 errores / 9 advertencias**, linea base exacta (8 `NU1902` + el `CS0114` de
`HomeController.cs(38,26)`, preexistente de Entrega 1). El build INCREMENTAL daba **8** y esconde una:
el numero se toma siempre de `--no-incremental`.

**La vista nueva SI se compila, medido y no supuesto:** mutada a proposito con un simbolo inexistente
→ `CS1061` en `Emitir.cshtml(26,24)`; restaurada **desde un backup** (nunca `git checkout`, que
volveria a HEAD) y `md5sum` identico. Su JS embebido pasa `node --check`.

**`tools/ArnesNotaCredito` (nuevo): 45 afirmaciones EVALUADAS / 45 OK / 0 FALLADAS / 0 NO MEDIDAS**,
idempotente, 7 s. Reparto contado por el arnes (no declarado en un comentario).

**El fixture esta disenado para que las afirmaciones DISCRIMINEN, y es la parte mas facil de errarle:**
lineas con **descuento Y recargo** (producto A: lista 1000, efectivo 900 — que es justo lo que el
arnes de CR-03 no hacia) y un producto a **100,01 facturado por 3**, que fabrica la deriva de redondeo
de **un centavo** con la que se mide la regla del remanente: el IVA del comprobante es
`round(300,03 × 21%) = 63,01`, pero partido en 1 + 2 da `21,00 + 42,00 = 63,00`. La ultima NC devuelve
**1.302,01** y no 1.302,00, y el saldo de la CC del cliente vuelve a **0,00 exacto**.

**Medido por mutacion: 21 mutantes, CERO sobrevivientes**, union de tumbadas = el conjunto
`[DISCRIMINA]` completo (32), con **cero** `[COBERTURA]`/`[CONTEXTO]` caida. Y la atomicidad se midio
**inyectando una falla** (trigger que aborta el INSERT del movimiento de CC) con las dos direcciones:
con el trigger no queda ni la NC ni el movimiento, y sacado el trigger la MISMA emision pasa.

### Lo que la medicion encontro MAL en mis propias etiquetas y afirmaciones

Esto es el valor de la pasada, no el ruido:

1. **`2.4` estaba `[DISCRIMINA]` y no discriminaba.** Miraba la linea del producto **C**, que no tiene
   descuento ni recargo: ahi lista y efectivo son los dos 100,01, asi que el mutante que congela el
   precio de **lista** la deja en verde. Es la primera forma de falso verde — el valor esperado y el
   del mundo sin fix coinciden **por casualidad**. Bajo a `[COBERTURA]` y se agrego **`2.6`** sobre la
   linea del producto **A** (900 vs 1000), que si discrimina y que M3 tumba.
2. **`4.4` estaba `[DISCRIMINA]` y el mutante M5 SOBREVIVIO con los 44 en verde.** El fixture
   facturaba la venta **completa** y despues acreditaba: con el pendiente en 0, sumar las NC lo manda a
   −2 y `PendienteDeFacturar > 0` sigue siendo false — **el badge queda apagado en los dos mundos**. El
   fixture paso a ser una facturacion **PARCIAL** (5 vendidas, 3 facturadas, 2 acreditadas): el
   pendiente correcto es 2, el badge esta **encendido**, y M5 lo apaga. Se agrego `4.6` para la otra
   mitad de R19 (la venta `Facturada` acreditada por completo).
3. **`5.7` pasaba POR EL MOTIVO EQUIVOCADO.** Forzaba un importe malo sobre un comprobante que a esa
   altura ya estaba acreditado **por completo**: el rechazo que llegaba era el del **tope de cantidad**,
   no el del eco. La afirmacion decia OK y el mensaje probaba otra cosa; un mutante que borrara el eco
   la habria dejado en verde (cuarta forma de falso verde). Se reescribio con un comprobante propio con
   pendiente **y** cargo vivo, y ahora afirma **que el rechazo hable de la devolucion**. Se ve solo
   leyendo el texto del rechazo que el arnes imprime — razon suficiente para imprimirlo siempre.
4. **`1.3` estaba subestimada:** `[CONTEXTO]` y M3 la tumba. Subio a `[DISCRIMINA]`.
5. **`5.9` estaba inflada:** es el **control positivo** de 5.7 y por construccion no la puede matar
   ningun mutante de defecto. Bajo a `[COBERTURA]`. (`8.2` es el mismo tipo de control pero **si** la
   tumban M2 y M12, asi que se queda en `[DISCRIMINA]`.)
6. **`2.2`, `2.5`, `3.2`, `3.4`, `4.5`, `5.5` y `6.4` sobrevivieron a las primeras rondas, y en 6 de
   los 7 casos faltaba el mutante, no sobraba la marca.** Se agregaron M15 a M21. Solo `2.2` se bajo a
   `[COBERTURA]` (lo que afirma lo miden de verdad 5.1, 5.2 y 5.5 por el lado del tope).

### Lo que NO se puede discriminar, declarado en vez de disfrazado

**La rama PROPORCIONAL de `CalcularDevolucionDeIva` no se puede distinguir de "devolver el IVA de la
NC tal cual" con un fixture construido por los servicios reales**, porque hoy
`FacturacionParcialService` postea el IVA **exacto** del comprobante y entonces
`DiferenciaIvaCobrada == Iva` **siempre**: con cargo igual al IVA, la proporcion se simplifica al IVA
de la NC. La proporcion existe para que la formula siga siendo correcta si alguna vez se posteara un
cargo parcial, y eso **no es alcanzable hoy**. Lo que si se mide, y es la mitad que importa, son la
**cota** (nunca devolver mas que el remanente, M15) y el **remanente** de la ultima NC (M1, M14).
Esto esta escrito en el encabezado del arnes, no solo aca.

### Dos defectos del INSTRUMENTO que la medicion destapo (y que valen para el proximo arnes)

1. **Un `First`/indexacion sin guard mata al arnes en los casos de rechazo DELIBERADO.** El arnes pide
   a proposito acreditar un item que ese comprobante no facturo (5.5), y con `First` moria con
   *"Sequence contains no matching element"* **antes** de que el Service pudiera rechazarlo: se llevo
   puestas todas las afirmaciones de abajo. Toda cuenta previa del arnes tiene que sobrevivir a los
   datos que el arnes manda **justamente para que el codigo los rechace**.
2. **Un mutante puede volver EXCEPCIONAL un camino que en el codigo sano es un `return` limpio.**
   Medido con M8 y con M12. El `try/catch` alrededor de la llamada al Service no es prolijidad: es lo
   que separa *"esta afirmacion fallo"* de *"el arnes dejo de medir"*.

Y dos mas del mismo tipo, operativos:

3. **La limpieza murio por traduccion de `StartsWith`** (el provider MySQL lo manda a un
   `COLLATE utf8mb4_bin` sin type mapping y revienta en runtime: MH-001 con otra cara). Paso **en la
   limpieza**, que es el peor lugar: la corrida habia medido 40 afirmaciones en verde y salio con exit
   3. Si la limpieza hubiera estado **fuera** del `try`, habria terminado con un codigo que parecia
   limpio. Se cambio por `EF.Functions.Like`.
4. **Un mutante del IMPORTE tiene que apagar tambien el ECO, o apunta al lugar equivocado.** El arnes
   replica la formula de la devolucion para poder mostrar el numero antes de confirmar (igual que la
   pantalla); con el eco activo, un mutante del importe hace que el Service **rechace todas las
   emisiones** y lo que se mide es una **cascada** (M2 tumbaba 21 afirmaciones, casi ninguna por la
   propiedad que rompe) **y** deja `3.6` **NO MEDIDA** — una afirmacion condicional no se puede matar
   con un mutante que rompe su precondicion.

Y uno del driver de mutacion, que es el mas vergonzoso y el mas facil de repetir: **parchee la lista
de mutantes con `str.replace` SIN assert y el ancla no matcheo**, asi que M2 y M14 corrieron **sin** el
"sin eco" que yo creia haberles puesto. El driver tiene un assert por ancla precisamente para esto y
lo salte al editar el driver. Y la segunda version del parche uso `re.sub`, que **interpreta las
secuencias de escape del reemplazo**: convirtio los `\n` de los anclas en saltos de linea reales y
dejo el driver sin compilar. **Un archivo de mutantes se escribe entero, no se parchea.**

### Riesgos y supuestos

- **AFIP no se llamo y no se puede llamar:** la NC nace en `Pendiente` y sin CAE, igual que las
  facturas hoy. El circuito esta completo y probado; falta **solo** la comunicacion, que es el residual
  del modulo 6 y espera el certificado del cliente. El `is 1 or 3` de
  `MapearCondicionIvaReceptor` ya cubre la NC A (RG 5616/2024).
- **La migracion no se aplico a `laplatense_dev`.** Dev sigue en 18. Aplicarla es un paso de deploy y
  el deploy esta postergado por la credencial; cuando se desbloquee, **base y sitio en la misma
  ventana** (la condicion de v26/v28 sigue vigente y esta migracion no la cambia: es aditiva, nullable
  y sin backfill, asi que el codigo viejo la aguanta estructuralmente).
- **Lo que queda fuera de este lote, declarado para que nadie lo busque:** `DevolucionService` y el
  reingreso de stock (lote 2), las otras **tres** guardas de la familia, y AFIP real.
- **`EsNotaCredito` es azucar de lectura y esta `Ignore()` explicito en el modelo.** Si alguna vez le
  crece un `private set`, la convencion de EF la mapearia y apareceria una columna que nadie pidio.
