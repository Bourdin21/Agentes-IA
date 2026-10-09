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

## El primo del mismo problema: `StartsWith` revienta por COLLATE, no por la coleccion

`EF.Functions.Like(col, prefijo + "%")` y no `col.StartsWith(prefijo)`. El provider
`MySql.EntityFrameworkCore` traduce `StartsWith` a una expresion con `COLLATE utf8mb4_bin` a la que
**no le asigna type mapping**, y la consulta revienta en RUNTIME con *"Expression ... COLLATE
utf8mb4_bin in the SQL tree does not have a type mapping assigned"*. Compila, pasa code review y solo
falla contra MySQL: es MH-001 con otra cara y por eso vive aca.

**Why:** medido en la-platense el 2026-10-07, y lo peor fue **donde** paso: en la LIMPIEZA del arnes.
La corrida habia medido 40 afirmaciones en verde y murio con exit 3 al contar las filas propias para
afirmar que no quedaba ninguna. Si la limpieza hubiera estado **fuera** del `try`, el proceso habria
terminado con un codigo que parecia limpio.

**How to apply:** `grep -rn "\.StartsWith(\|\.EndsWith("` sobre lo que viaja a SQL. `Contains` sobre
una **columna** si traduce (va a `LIKE '%x%'`); los otros dos, no. Y la conclusion general:
**la limpieza de un arnes corre DENTRO del try y se AFIRMA**, no al final y a la buena de Dios.
