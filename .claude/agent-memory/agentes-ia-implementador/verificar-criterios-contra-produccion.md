---
name: verificar-criterios-contra-produccion
description: Los criterios de aceptacion que traen un numero exacto se pueden verificar durante la implementacion con el cliente mysql de Windows contra la base del proyecto, antes de entregar a QA.
metadata:
  type: feedback
---

Cuando un criterio de aceptacion trae un **numero exacto** (un total, una cantidad de filas, un
importe), reproducirlo con una consulta de **solo lectura** contra la base del proyecto *antes*
de dar la etapa por cerrada, y escribir en el reporte cuales dieron exacto y cuales no.

**Why:** el build limpio no dice nada sobre si el agregado que escribiste da el numero que el
analisis midio. En CR-86 de marihogar, verificar en el momento destapo que el backfill contado
de la forma obvia ("movimientos no-reversion con fecha distinta") daba 32 de dia / 8 de mes en
vez de los 27 / 3 del analisis, porque 5 cheques tenian un par Pago+Cargo ya reversado que habia
que valuar en 0. Era un defecto que QA habria devuelto, y se corrigio antes de entregarlo.

**How to apply:** el cliente esta en
`C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe`; la cadena de conexion de cada proyecto
vive en `<repo>/<Proyecto>.Web/appsettings.Production.json` (no copiarla al chat ni a un archivo).
Solo `SELECT` — nunca escribir en produccion. Las credenciales quedan en el archivo del repo, no
en esta memoria.

Relacionado: [[verificacion-vistas-razor]].
