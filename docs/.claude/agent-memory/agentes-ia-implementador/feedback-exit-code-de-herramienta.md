---
name: feedback-exit-code-de-herramienta
description: Un backup o dump con exit distinto de 0 no se usa aunque el tamano parezca razonable; se mira el exit y el footer, no el peso del archivo
metadata:
  type: feedback
---

El resultado de una herramienta externa se juzga por su **exit code** y por su marca de cierre, no
por si el archivo "parece" bien.

**Why:** 2026-10-07, haciendo el snapshot de produccion de la-platense: `mysqldump` con `--events`
salio con **exit 2** porque el usuario de la base no tiene ese privilegio
(`Access denied ... (1044)` sobre `show events`). El archivo quedo **truncado** en la seccion de
events, **sin el footer `-- Dump completed`**, pero con **33.718.329 bytes** — un tamano
perfectamente creible. Usarlo como plan de rollback habria sido confiar en un backup incompleto.
Repetido sin `--events`, exit 0 y footer presente. Es la misma familia que el
`dotnet build --no-build` que corre el binario viejo sin avisar.

**How to apply:** despues de todo dump/build/script externo, capturar `$?` y afirmarlo. Para un
`mysqldump`, los tres controles son: **exit 0**, el `-- Dump completed on ...` al final, y el
conteo de `CREATE TABLE` contra las tablas que la base dice tener. El tamano del archivo no es
ninguno de los tres. Y un dump que no pasa los tres **no se usa**, se regenera.

Ver tambien [[feedback-conteos-exactos-no-estimados]].
