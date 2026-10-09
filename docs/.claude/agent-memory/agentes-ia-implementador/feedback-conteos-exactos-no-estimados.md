---
name: feedback-conteos-exactos-no-estimados
description: TABLE_ROWS de information_schema es estimado en InnoDB y ya mintio midiendo produccion; todo conteo va con COUNT(*)
metadata:
  type: feedback
---

Todo conteo de filas que sirva de evidencia va con `COUNT(*)`. Nunca con
`information_schema.TABLES.TABLE_ROWS`.

**Why:** en InnoDB `TABLE_ROWS` es una **estimacion del optimizador**, no un conteo. Midiendo
produccion de la-platense el 2026-10-07 dio **6** para `__efmigrationshistory`, que tiene **8**
filas, y **0** para `cajamovimientos`, que tiene **1**. Si el estado de produccion se hubiera
reportado con esa consulta, el conteo de migraciones aplicadas habria salido mal — y ese numero era
justo el dato que la etapa venia a confirmar. Es barato de evitar y caro de descubrir despues.

**How to apply:** `TABLE_ROWS` sirve solo para una ojeada de orden de magnitud, y si se usa hay que
decir que es estimado. Para cualquier conteo que entre en un veredicto, en una comparacion antes/
despues o en una verificacion de "no se perdio ninguna fila", va `COUNT(*)` por tabla.

Para probar que **ningun valor preexistente cambio** cuando una migracion agrega columnas,
`CHECKSUM TABLE` tampoco sirve: las columnas nuevas le cambian el valor aunque nada viejo se haya
movido. Lo que funciona es hashear **solo las columnas que existian antes** (pedirle la lista a la
base sin migrar) con la misma query en las dos bases, y diffear las salidas.

Ver tambien [[feedback-medir-antes-de-heredar]].
