---
name: coleccion-local-de-strings-hacia-sql
description: Cualquier coleccion local de strings que entre a un Where traducido a SQL dispara MH-001 y deja el endpoint en 500 — sea parametro, variable local o static readonly.
metadata:
  type: feedback
---

El gatillo de MH-001 es **cualquier coleccion local de `string` que entre a un `Where` que se
traduce a SQL**: parametro, variable local, `static readonly`, campo — a EF le da igual. Revisarlo
cada vez que se escribe un `Contains` sobre una coleccion en memoria, no solo al refactorizar.

**Why:** en CR-86 de marihogar escribi la version original con un `static readonly string[]` en el
`Where` y crei que era seguro; despues, al extraer el metodo compartido, el array paso a parametro
y asumi que el refactor habia *introducido* el defecto. Las dos cosas eran falsas: el defecto
estuvo desde el primer commit, y QA lo califico sin que nadie lo viera porque el codigo compila y
parece correcto. Si la lección hubiera quedado como "cuidado con los refactors", la proxima vez
habria mirado el lugar equivocado. MH-001 se dispara **tambien con la coleccion vacia**, asi que no
es un listado parcial: es 500 en todo el endpoint desde el dia 1.

**How to apply:** `grep -n "\.Contains("` sobre los archivos del alcance y quedarse con los casos
cuya coleccion local sea de `string` **y** viaje a SQL. Las colecciones de `int` o de enum son
seguras; `columna.Contains(texto)` es otra cosa (LIKE) y tambien. El arreglo es materializar y
filtrar en proceso contra un `HashSet`, **sin** un `if (count == 0) return` delante, que enmascara
el bug hasta el primer dato. Si la tabla se midio con la collation case-insensitive de MySQL, usar
`StringComparer.OrdinalIgnoreCase` — y entonces el `GroupBy` y el `OrderBy` de la misma consulta
tambien, o los tres criterios dejan de hablar del mismo universo.

Relacionado: [[verificar-criterios-contra-produccion]].
