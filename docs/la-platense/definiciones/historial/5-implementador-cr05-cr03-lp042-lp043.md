## CR-05 + CR-03 + LP-042 + LP-043 — transferencia, interes por tarjeta, y el instrumento (2026-10-07)

**Cuatro commits locales en `entrega-1-migracion`, sin push y sin deploy:** `e356522` (CR-05),
`7c49732` (CR-03), `7820277` (LP-042 + LP-043). Build **0 errores / 9 advertencias**, la linea base
exacta; ninguna advertencia sale de codigo nuevo (8 NU1902 de MailKit/MimeKit + 1 CS0114 de
`HomeController`, todas preexistentes).

### Lo primero: la linea base se REPRODUJO antes de tocar una linea

`ArnesReconciliacionTx` **153/153/0** y `ArnesSeisSitiosRestantes` **32/32/0**, igual que lo
declarado. **Pero la primera corrida murio** con una excepcion de MySQL: la base
`laplatense_recon_tx` tenia el esquema de una ronda anterior. Recreada y migrada de cero, dio los
153. **La leccion operativa: estas bases no son re-usables entre rondas si hubo migraciones nuevas
en el medio** — se recrean siempre, y el arnes no tiene por que sobrevivir a un esquema viejo.

Y el `| tail -30` con el que se la corrio **se comio el mensaje de error y devolvio exit 0**: en un
pipe, `$?` es el del ultimo comando. Correr un arnes a traves de un pipe destruye su exit code, que
es justamente lo que `LP-041` construyo. **Se redirige a archivo y se filtra el archivo.**

### CR-05 — transferencia (`e356522`)

`MedioPago.Transferencia = 5`, al final y numerado (produccion tiene actividad real). Mapeado en
`MedioPagoCajaMapper.DesdeMedioPagoVenta` a `MedioPagoCaja.Transferencia`, que ya existia. **Sin
migracion EF**: la columna ya es `int`. El numero de operacion va en `PagoVenta.Nota`, que ya
existe. El desglose por medio del cierre (`_ArqueoPorMedio.cshtml`) es data-driven desde el ledger,
asi que la fila separada aparece sola.

**DOS HALLAZGOS DEL BARRIDO LP-002 QUE EL COMPILADOR NO DA:**

1. `MedioPagoCajaMapper` afirmaba que sus switch eran exhaustivos *"sin `_ =>` que absorba lo
   desconocido"* y que por eso *"el compilador avisa con CS8509 — es el barrido LP-002 hecho por el
   compilador"*. **Es FALSO:** los tres switch SI tienen `_ =>`, asi que con un valor nuevo el
   compilador no emite nada. **Verificado por ejecucion:** el build con `Transferencia = 5` y sin la
   rama de traduccion compilo en 0 errores / 9 advertencias, las mismas 9 de la linea base. Sin el
   barrido a mano, la primera venta por transferencia habria tirado `ArgumentOutOfRangeException` al
   postear en caja. **Se corrigio el comentario y NO el codigo** (la rama que lanza es la que se
   quiere: falla cerrado en el unico punto de traduccion). Lo que no se puede es creerle al
   comentario y saltear el barrido.
2. El XML-doc de `MedioPagoCaja` declaraba como regla de negocio que *"MedioPago no tiene
   Transferencia (una venta no se cobra asi en esta ferreteria)"*. CR-05 la dejo falsa. **Es la
   forma exacta de `LP-008`:** una regla de negocio que el repo afirma y el negocio ya no cumple.

**LA LISTA DE MEDIOS ESTABA COPIADA EN CUATRO LUGARES.** Las cuatro se generan ahora desde
`MedioPagoCajaMapper.EtiquetaMedioVenta` / `MediosVenta`:

- `Ventas/Details.cshtml`: era un `Dictionary<MedioPago,string>` **indexado por clave**. Un medio
  nuevo no mostraba una etiqueta fea: tiraba `KeyNotFoundException` y **rompia la ficha de la venta**.
- `Ventas/Editar.cshtml`, combo de Razor (filas ya guardadas).
- `Ventas/Editar.cshtml`, **plantilla JS de "Agregar pago"**. La copia que mas facil se queda vieja:
  el mismo medio aparecia o no **segun como naciera la fila**.
- `Clientes/RegistrarCobro.cshtml`, ahora desde `MediosCobroCuentaCorriente`.

**Transferencia entro tambien en el cobro de cuenta corriente, y no por completitud:** `MedioPago`
es el MISMO enum que el de la venta, asi que un cobro por transferencia tenia el defecto identico
(se cargaba como Efectivo y el arqueo lo contaba en el cajon). Arreglar la venta y dejar ese combo
con tres opciones habria sido *"unificar una semantica en un lugar y desunificarla de todos los que
no se tocaron"*, que es textualmente como QA resumio `LP-010`.

### CR-03 — interes por tarjeta x cuotas x fecha (`7c49732`)

- **`Tarjeta`** (catalogo en tabla, **no enum**): el negocio agrega una tarjeta cuando cambia de
  terminal y eso no puede requerir deploy. La baja es `Activo`, no delete (criterio de
  `RecargoCuota.Activo`); la pantalla no expone borrar. **Sin seed**: que tarjetas acepta la terminal
  es dato del negocio, y sembrar "Visa/Mastercard/Naranja" seria adivinar la procesadora.
- **`InteresTarjetaCuota`** — `(TarjetaId, Cuotas, Porcentaje, VigenteDesde, VigenteHasta)`, con la
  forma de `TasaCostoCobranza` de **marihogar**. **NO hereda `SoftDestroyable` a proposito**: es
  configuracion con vigencia, no un documento; se cierra con `VigenteHasta` y nunca se borra (una
  fila borrada dejaria sin explicacion el recargo ya cobrado). Al no heredar, **tampoco la alcanza el
  query filter global** y no hace falta `IgnoreQueryFilters`. `decimal(7,4)` y no `(5,2)`: en
  marihogar se midio que truncar a dos decimales desviaba ~$29 sobre $670.600.
- **La firma paso de `(medio, cuotas)` a `(medio, tarjeta, cuotas, FECHA)`.** La fecha hace falta
  porque el porcentaje tiene vigencia: sin ella, *"el porcentaje de Visa a 6 cuotas"* no es una
  pregunta con una sola respuesta. Se pasa **explicita** (no `UtcNow` adentro) para que el arnes
  pueda medir una vigencia futura sin tocar el reloj.
- **`RecargoCuota` NO se migra ni se borra:** sigue siendo el porcentaje general, el fallback de todo
  pago sin tarjeta, y **la tabla que define QUE PLANES existen** (da las columnas de la grilla
  nueva). **`PagoVenta.PorcentajeRecargoAplicado` NO se toca** (R14).
- **Migracion aditiva, verificada operacion por operacion:** el `Up` tiene 1 `AddColumn`
  (`TarjetaId` nullable) + 2 `CreateTable` + 3 `CreateIndex` + 1 `AddForeignKey`. **Ningun `DROP` ni
  `ALTER` destructivo** — los `DropTable`/`DropColumn` del archivo estan todos en el `Down`.
- **`PagoVenta.TarjetaId` nullable y sin default:** los pagos historicos quedan sin tarjeta porque
  eso ES la verdad, y una inventada se leeria despues como un hecho.
- **Lugar reservado para v2 (`D-CR04.2`):** las 4 alicuotas del costo real de cobranza (comision, IVA
  de la comision, IIBB, Ley 25413) se crean en 0 y **sin lectores**. Agregarlas despues NO seria
  aditivo: habria que inventar su valor para cada vigencia ya cerrada, o sea un **backfill sobre
  datos que nadie puede reconstruir**.

**LA FECHA ES EL DIA DE NEGOCIO ARGENTINO** (`ArgentinaTime.DiaDeNegocio`), no `UtcNow.Date`, **en
los tres lugares que la usan**: el workflow al guardar, la vista de la venta al previsualizar y la
grilla de configuracion. Una venta de las 22:00 del 14 en Argentina es el 15 a la 01:00 UTC: por UTC
se le aplicaria una tasa que todavia no rige, y si los tres lugares no usan la misma fecha **la
pantalla muestra un numero y la venta guarda otro**. Es la leccion de `D9`/`LP-010` aplicada antes
de que duela.

**DOS COSAS QUE SE ARREGLARON POR LECTURA, NO POR EJECUCION** (el rol no corre navegador):

1. Las dos grillas de la pantalla nueva tenian **`<form>` como hijo directo de `<tr>`**. El unico
   contenido valido de un `<tr>` son `<td>`/`<th>`, asi que **el parser SACA el form de la tabla**:
   los inputs quedan huerfanos y el submit postea **una fila vacia**. Una pantalla que parece andar y
   guarda nada, que **ni el compilador ni el build de Razor ven**. Resuelto con el atributo `form=`
   de HTML5. **Es el tipo de defecto que solo lo atrapa leer el HTML generado o un smoke real** —
   anotarlo porque va a volver a aparecer en la proxima grilla editable.
2. El porcentaje se resolvia **dos veces** en el JS de la venta (el cartel de la fila y el recalculo
   de totales), cada una por su lado: la fila podia decir "+20%" y el total sumar otra cosa. Ahora las
   dos pasan por `porcentajeDeFila()`, **con el mismo orden de resolucion que el servidor**. Y el
   chequeo es contra `undefined`, **no un truthy**: un interes de 0% es un valor CARGADO y 0 es falsy
   en JS, asi que un `if (pct)` lo perderia y la tarjeta cobraria el general cuando se configuro que
   no cobre nada.

**Razor SE COMPILA en el build** — verificado positivamente metiendo un error a proposito en la vista
nueva (dio 2 errores) **antes** de confiar en el verde. El build limpio valida el C# de las vistas;
**no valida su estructura HTML**, que es por donde entro el defecto del `<form>`.

### El arnes nuevo y la mutacion

`tools/ArnesTarjetaYTransferencia` (base **`laplatense_tarjetas`**, idempotente, aborta si se lo
apunta a dev/qa/produccion): **41 afirmaciones, 41 OK, 0 FALLADAS, 0 NO MEDIDAS, exit 0**.

**Matriz de mutacion:** `M1` = `Transferencia -> MedioPagoCaja.Efectivo` (el bug de CR-05);
`M2` = se arranca el bloque `if (tarjetaId.HasValue)` entero (el comportamiento pre-CR-03). Con
`M1+M2`: **27 OK, 14 FALLADAS, y las 14 son TODAS las marcadas `[DISCRIMINA]`** — PF20 (1.2, 1.3,
1.4) y PF18 (2.2, 2.3, 2.6, 3.1-3.4, 4.2, 4.5, 5.3, 6.5). **Ninguna FALLADA sin esa marca.**

**LA MUTACION ENCONTRO UN FALSO VERDE ADENTRO DEL ARNES ESCRITO PARA EVITARLOS.** La afirmacion
`2.6` ("un 0% cargado le gana al general") estaba escrita sobre **9 cuotas, cuyo recargo general
sembrado tambien es 0%**: pasaba con y sin el fix, y fue la **unica `[DISCRIMINA]` que quedo verde**
con el eje tarjeta arrancado. Movida a 3 cuotas (general 10%), ahora falla. **La marca
`[DISCRIMINA]` no se declara, se MIDE.**

Las tres marcas significan cosas distintas y **no son intercambiables**: `[DISCRIMINA]` (fallo contra
el codigo mutado — 14), `[COBERTURA]` (mide un mecanismo real pero **ninguna mutacion de esta ronda
la tumbo**, asi que no esta probado que pueda fallar — 17, relabeladas despues de ver la corrida
mutante) y `[CONTEXTO]` (pasa con y sin el fix; sirve para ubicar un fallo y **no cuenta como
cobertura**).

### LP-042 — dos de las 32 afirmaciones "OK" no median nada (`7820277`)

`2.2/N=3` y `2.2/N=8` tenian la forma `venta.Estado != Confirmada || invariante`. Cuando la venta no
queda Confirmada **el primer termino basta y el invariante no se evalua**, pero la afirmacion imprime
OK. En **46 de 46 corridas** la confirmacion perdio la carrera: el invariante nunca se evaluo y las
dos sumaron a la cobertura 46 veces cada una. **Una afirmacion vacia es PEOR que una que falta: la
que falta se ve en el conteo, la vacia se disfraza de cobertura.**

El arnes pasa a tener **tres resultados**. `AfirmarCondicional` toma la precondicion explicita y, si
no se cumple, el resultado es **NO MEDIDA — nunca OK**. Se listan con nombre **incluso en una corrida
verde**, y si una familia condicional no se evaluo ni una vez el arnes sale con **exit 6** (separado
del 0 a proposito: si los dos devolvieran 0, el agujero se leeria como exito, que es exactamente como
esto se escondio 46 corridas).

**VERIFICADO POR EJECUCION, Y EL NUMERO DECLARADO ESTABA MAL:** con el mecanismo puesto y sin otro
cambio, el arnes paso de **"32 OK"** a **"30 OK, 0 FALLADAS, 2 NO MEDIDAS" con exit 6**. **La linea
base nunca fue 32: era 30 medidas + 2 fantasma.**

**Y el invariante AHORA SE MIDE, no se declaro como tripwire y listo.** Declararlo habria cumplido la
letra del parte dejando el invariante sin evaluar una sola vez, y habria dejado este arnes **saliendo
con exit 6 en todas las corridas futuras** — un numero que a las tres semanas nadie mira. La carrera
deja la venta en Borrador con los items **ya editados por el guardado ganador**, que es justamente el
estado peligroso: **`2.4/N=n` la confirma DESPUES, en secuencia**, y evalua el mismo invariante.
Mide de verdad: stock descontado = 7 unidades, caja = $8.470, total = $8.470, los tres coincidiendo.
`2.2` **no se elimina**: mide el caso en que la confirmacion GANA (el que `LP-018` ataca) y sigue
siendo condicional porque depende de quien gane.

Resultado: **32 OK, 0 FALLADAS, 2 NO MEDIDAS, exit 0, sin agujero de cobertura** — 32 afirmaciones
**reales** (las 2 fantasma reemplazadas por 2 que evaluan) mas 2 declaradas a la vista.

### LP-043 — un arnes que se cuelga ahora muere diciendolo (`7820277`)

Tope de tiempo en **los tres** arneses, **exit code 5** propio (una excepcion tiene stack trace y un
cuelgue tiene locks: son dos cosas distintas de mirar). Default 600 s en los dos grandes y 300 s en
el nuevo; configurable con `ARNES_TIMEOUT_SEG` y **no desactivable**.

**Es un `Timer` y no un `CancellationToken`**, y el motivo es el caso real: un `INSERT IGNORE` contra
una fila tomada con `FOR UPDATE` **se colgo 400 s** e InnoDB **no lo detecta como deadlock**, asi que
nadie lo corta. Ese hilo esta en una **espera nativa de MySQL y no mira ningun token** — no hay a
quien pedirle que corte. El timer corre en el threadpool, es independiente de lo que este bloqueado,
informa y mata el proceso. El mensaje dice que mirar:
`SELECT * FROM performance_schema.data_locks`.

**VERIFICADO POR EJECUCION EN LOS TRES**, no declarado: con `ARNES_TIMEOUT_SEG` en 2-3 s los tres
mueren con **exit 5** y el cartel *"ES UNA CORRIDA SIN RESULTADO"*. **Un tripwire sin probar no es un
tripwire.**

### Estado de los tres arneses al cierre (todos idempotentes y re-corribles por QA)

| Arnes | Base | Resultado | Exit |
|---|---|---|---|
| `ArnesReconciliacionTx` | `laplatense_recon_tx` | 153 OK / 0 FALLADAS | 0 |
| `ArnesSeisSitiosRestantes` | `laplatense_seis` | 32 OK / 0 FALLADAS / 2 NO MEDIDAS | 0 |
| `ArnesTarjetaYTransferencia` | `laplatense_tarjetas` | 41 OK / 0 FALLADAS / 0 NO MEDIDAS | 0 |

**Las tres bases quedan vivas para QA, las tres con la migracion `CR03_TarjetasEInteresPorCuotas`
aplicada.** La base scratch `laplatense_cr03` (solo para generar la migracion) se borro.

### Pruebas minimas para QA (el rol no corre navegador; esto es para la corrida de QA)

1. **PF20:** venta cobrada por **Transferencia** -> el cierre diario la lista como **fila propia** y
   el efectivo del dia **no la incluye**.
2. **PF18:** cargar dos tarjetas con % distinto para **6 cuotas**; la misma venta con una y con otra
   tiene que mostrar **dos recargos distintos ANTES de confirmar**.
3. **R14:** confirmar una venta con tarjeta, **despues editar la grilla**, y verificar que el total y
   el recargo de esa venta **no cambiaron**.
4. **La grilla de configuracion GUARDA DE VERDAD** (fue el defecto del `<form>` en `<tr>`): editar una
   fila, guardar, recargar y confirmar que el valor quedo. **Probar las dos tablas** de la pantalla
   (intereses y catalogo de tarjetas).
5. **Celda vacia != 0:** dejar una celda **en blanco** y verificar que esa tarjeta usa el **recargo
   general**; cargar **0** y verificar que **no cobra nada**.
6. **Vigencia futura:** cargar un % con `Vigente desde` **el mes que viene** y verificar que **hoy no
   se aplica**.
7. **Baja de tarjeta:** desactivarla -> **no aparece** en el combo de una venta nueva, pero la ficha
   de una venta vieja **sigue mostrando su nombre** y su recargo.
8. **Pago historico:** una venta anterior a CR-03 muestra **"Sin especificar"** en Tarjeta, no un
   nombre inventado ni un error.
9. **Combo de tarjeta con catalogo VACIO:** la venta tiene que poder cobrarse igual (cae al recargo
   general) y la fila **dice "Sin tarjetas cargadas"** con un link a configurar.
10. **La fila que agrega "Agregar pago"** tiene que traer **las mismas opciones** de medio y de
    tarjeta que las filas ya guardadas (fue la copia de la lista que se quedaba vieja).

### Lo que NO se toco (decisiones cerradas respetadas)

"Confirmar y facturar" sigue **oculto**. `Venta.CAE` / `NumeroComprobante` / `VencimientoCAE` /
el tipo siguen **obsoletas y sin escritores** — no se borraron y no se volvieron a escribir.
`FacturarAsync` sigue siendo el **unico** camino que escribe comprobante. **`CR-04` (plan de echeqs)
no se empezo**, ni la Entrega 5.
