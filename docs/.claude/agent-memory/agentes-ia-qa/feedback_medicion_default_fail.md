---
name: feedback-medicion-default-fail
description: En La Platense, todo numero citado como "verificado" se vuelve a medir; un diff vacio y un total de information_schema no son evidencia
metadata:
  type: feedback
---

Al evaluar en **la-platense**, ningun numero se hereda: ni del brief, ni del implementador, ni de un parte
mio anterior. Se vuelve a medir contra la fuente antes de usarlo como premisa.

**Why:** pasó tres corridas seguidas y en las tres el dato venia citado como *"verificado por consulta
directa"*. 2026-10-07: mi propio parte `LP-050` afirmaba que produccion tenia "5 ventas y 4 movimientos de
caja" — tiene **0 y 1**. El brief de la misma corrida hablaba de "6 tablas nuevas" — son **15**. Antes, un
`wc -l` hizo afirmar "19 migraciones" cuando son 18 (contaba el `ModelSnapshot`), y "4 filas `ZZ%`" que eran
coincidencias internas de `%ZZ%` en catalogo real. El error suele ir para el lado benigno, pero el **metodo**
que lo produce es el mismo y la proxima vez puede no ir para ese lado.

**How to apply:** dos oraculos concretos que ya dieron falso PASS y no se usan solos:

- **Un `diff` vacio entre dos salidas no prueba igualdad** si no se verifico que los dos lados produjeron
  algo. Me dio "sin diferencias" porque **ambos lados habian fallado identico** con `ERROR 1064` de sintaxis
  SQL: el `diff` comparo dos mensajes de error iguales. Siempre imprimir una muestra de la salida.
- **`information_schema.TABLES.TABLE_ROWS` es un ESTIMADO en InnoDB** y miente de forma comprobable (dio
  `gastos=0` y `productos=111.453` contra `1` y `112.485` reales). Todo conteo va con `COUNT(*)`.

Y cuando hay varias bases en juego, cada medicion declara contra cual se hizo — confundirlas es el error mas
facil y el mas caro. Ver [[project-la-platense-deploy-entrega-1]].
