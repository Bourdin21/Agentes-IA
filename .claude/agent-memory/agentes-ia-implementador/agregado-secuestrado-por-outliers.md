---
name: agregado-secuestrado-por-outliers
description: Sobre datos migrados, un agregado ponderado (suma, promedio, variacion %) lo pueden secuestrar tres filas basura; el numero con el que el usuario decide tiene que ser un CONTEO.
metadata:
  type: feedback
---

Cuando una pantalla muestra **un numero con el que el usuario decide** (cuanto aumentan los
precios, cuanto cambia el total) sobre un catalogo **migrado de un sistema legacy**, ese numero no
puede ser un agregado ponderado. Tiene que ser un **conteo**: cuantas filas suben, cuantas bajan,
cuantas quedan igual. Los agregados ponderados quedan igual, pero etiquetados como lo que son: un
total de control.

**Why:** en la-platense, el preview del aumento masivo mostraba la variacion porcentual promedio
ponderada del catalogo. **Tres productos con un `PrecioCompra` de 6,3 billones** —datos sucios de
la migracion, preexistentes— aportaban el 99,99% de la suma, asi que el preview informaba **0,00%
de variacion mientras 112.000 productos cambiaban de precio**. El numero no estaba mal calculado:
estaba mal elegido. Y no se ve leyendo el codigo ni con un build limpio; aparecio al ejecutar la
consulta contra los 112.485 productos reales y desconfiar de un 0,00% que no cerraba con el resto.

**How to apply:** antes de poner un agregado en una pantalla sobre datos migrados, correr
`SELECT COUNT(*), MIN(col), MAX(col), AVG(col)` sobre la columna. Si el MAX esta varios ordenes de
magnitud sobre el AVG, o si hay negativos, el agregado es inservible como señal y hay que
reemplazarlo por conteos. **Verificar siempre contra el backup de la tabla si el outlier ya estaba
antes** de darlo por dato basura: si lo introdujo tu propio cambio, el hallazgo es otro.

**Lo que suele venir pegado:** esa misma consulta destapa filas que la formula convierte en algo
inadmisible. Aca habia 37 productos con costo negativo y 1 en cero, y reaplicarles el margen les
escribia un **precio de venta negativo** (el costo lo ve solo el administrador; el precio lo ve el
mostrador y lo cobra la venta). Se excluyen del lote y se informan en el preview, pero **no se
corrigen desde el modulo**: limpiar el catalogo es una decision del cliente, y arreglarlo de prepo
esconde el problema.

Relacionado: [[verificar-criterios-contra-produccion]], [[sonda-ef-desechable]].
