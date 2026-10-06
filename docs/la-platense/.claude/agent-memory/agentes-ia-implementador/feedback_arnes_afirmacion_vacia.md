---
name: arnes-afirmacion-vacia
description: Toda afirmacion de concurrencia con forma "si paso X entonces Y" pasa gratis cuando X no pasa nunca — hay que forzar X o afirmar que ocurrio
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
