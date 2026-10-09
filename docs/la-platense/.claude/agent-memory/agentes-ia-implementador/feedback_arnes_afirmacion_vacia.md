---
name: arnes-afirmacion-vacia
description: Afirmaciones que pasan sin medir nada — la condicional que se cumple vacia, y la que es verdadera tambien en el mundo con el defecto; la mutacion es lo unico que las distingue
metadata:
  type: feedback
---

En un arnés de concurrencia, una afirmación escrita como **"si el documento quedó Confirmado,
entonces su total es coherente"** pasa en verde cuando la confirmación **nunca gana la carrera**.
El invariante se cumple vacío y el arnés reporta OK sin haber probado nada.

**Why:** medido en la corrida de CR-01/CR-02 (2026-10-06). El escenario de `LP-038` usaba una
barrera con dos competidores; `GuardarBorradorAsync` ganó el lock **3 de 3** y la confirmación salió
rechazada antes de postear. El arnés mostró **47 OK / 0 FALLADAS** y el invariante que justificaba
todo el escenario no se había evaluado ni una vez. Es la misma familia del falso verde que
`ArnesSeisSitiosRestantes` ya se había comido (las llamadas morían por un servicio de DI sin
registrar y las afirmaciones pasaban vacías), y se colό igual.

**How to apply:** cuando el escenario necesita que un competidor concreto llegue primero, **no usar
una barrera: fabricar la ventana a mano.** Una conexión aparte toma el lock con
`SELECT ... FOR UPDATE` y lo retiene; se larga la operación que debe quedar con el grafo vencido (se
clava esperando el lock); recién entonces se hace el cambio y se commitea, liberando el lock. Es
determinista y es exactamente la forma del defecto.

Y en toda afirmación condicional: o se afirma además que la precondición ocurrió, o se imprime en
qué rama cayó. Dos corridas con la misma cuenta de OK pueden haber probado cosas distintas.

Complemento obligatorio: **la contraprueba.** Sacar el guard recién escrito, volver a correr, y
verificar que el arnés falla. Sin eso no hay evidencia de que el código nuevo haga algo — en esta
corrida la contraprueba mostró la venta Confirmada con la condición girada, $2.000 de caja posteados
y 2 unidades descontadas. Ver también [[arnes-falla-del-instrumento]].

**Segunda forma, encontrada en LP-039 (2026-10-06) y la más silenciosa de las tres: la afirmación
que es verdadera TAMBIÉN en el mundo con el defecto.** La 7.4 afirmaba *"el comprobante sigue
vivo"* — y con el defecto puesto el comprobante también queda vivo: eso es justamente lo malo
(queda colgado de una venta anulada). Pasaba bajo mutación, así que no medía nada, aunque no tenía
forma condicional ni dependía de ninguna carrera. **La prueba de que una afirmación mide algo es que
falle bajo mutación, no que su enunciado suene a invariante.** El arreglo casi siempre es la
**conjunción**: el invariante real era el par (comprobante vivo **y** venta no `Anulada`).

**Tercera forma, de QA en la ronda anterior: la mutación que pasa 50/50 porque la siembra no
discrimina** (`PrecioEfectivo` devolviendo el precio de lista pasaba porque el arnés sembraba sin
descuento ni recargo). Por eso **sembrar el caso que discrimina y afirmar su precondición explícita**
— en LP-039, que la venta parcialmente facturada esté en `Confirmada`, porque sembrada sobre una
`Facturada` el escenario entero pasa con el defecto puesto.

**Regla operativa que cubre las tres:** correr el arnés **con la mutación puesta** y mirar *cuáles*
afirmaciones fallan, no solo que el total baje. Una afirmación del escenario nuevo que siga en OK
bajo la mutación que reproduce el defecto es una afirmación vacía, y hay que reescribirla antes de
cerrar.

**Cuarta forma, de `LP-037` (2026-10-07) y la que más sorprende: la afirmación que medía el defecto
y pasa a cumplirse VACÍA justo cuando el fix entra.** El escenario usaba una barrera y el invariante
era *"si el día quedó CERRADO, su arqueo firmado cuadra"*. Con el defecto puesto fallaba (cierre $ 0
contra $ 201 vivos). Con el fix, **gana el cerrador las dos veces**, los escritores salen rechazados,
no queda ningún movimiento, y el invariante queda en `0 == 0`. Es el comportamiento correcto y es un
OK que no distingue los dos mundos: si mañana alguien rompe el fix de otra forma, puede seguir
pasando.

**La forma de arreglarlo es la misma de siempre, fabricar la ventana a mano, y acá tiene una receta
concreta:** una conexión aparte abre transacción, toma el mismo lock que tomaría el escritor real,
escribe su fila y **no commitea**; recién entonces se larga el competidor que debe esperar; se espera,
se commitea y se mira el resultado. Así el escritor gana **siempre**. Y el escenario afirma sus
**precondiciones por separado** ("el movimiento quedó vivo", "el período quedó cerrado"), porque son
ellas las que impiden que vuelva a pasar vacío sin que se note.

**Quinta forma, del lote 2 de la Entrega 5 (2026-10-07): la afirmación que lee un campo de una fila
que la consulta NO DEVUELVE, y el valor por defecto coincide con el esperado.**

La única afirmación que medía el badge *"Facturada en parte"* lo hacía sobre una venta que la
devolución total había dejado `Anulada` — y `ListarAsync` **no devuelve las anuladas**. La fila venía
`null`, el helper hacía `fila?.FacturadaEnParte ?? false`, y el badge salía **`false` por omisión**,
con y sin el fix. El mutante que saca la resta de devoluciones del badge **sobrevivió con 58/58**.

**Why:** es la forma más silenciosa de todas, porque la afirmación **dice la verdad** (*"el badge está
apagado"*) y el escenario **parece el correcto** (*"devolví todo, el badge tiene que apagarse"*). Lo
que falla es que el sujeto desapareció de la consulta y el `?? false` lo tapó.

**How to apply:** cuando una afirmación mira un campo de **una fila que vino de una consulta
filtrada**, afirmar primero que **la fila existe** — y, si el fixture puede sacarla del filtro (un
estado terminal, una baja lógica), medir sobre un sujeto que **siga entrando**. En este caso: una venta
VIVA con 4 vendidos, 2 facturados y 2 devueltos sin nota de crédito (pendiente 0 y badge apagado; sin
la resta serían 2 y quedaría prendido). Y nunca escribir `?? valorEsperado` en una afirmación: el
default tiene que ser un valor que **falle**, o la ausencia de la fila tiene que ser su propia
afirmación.

**Corolario que vale para el día que un fix hace pasar un escenario:** mirar *por qué* pasó, no que
pasó. Si pasó porque la rama difícil no se ejecutó, el escenario sigue sin medir el fix — y la cuenta
de OK sube igual.
