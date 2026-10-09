---
name: feedback-medir-antes-de-heredar
description: Todo numero que venga en un brief o en un reporte anterior se re-mide antes de usarlo como criterio; en La Platense fallo al menos tres veces
metadata:
  type: feedback
---

Ningun numero heredado de un brief, de un parte de QA o de una entrada de documentacion se usa
como criterio sin volver a medirlo con una consulta propia en la corrida actual.

**Why:** en la-platense paso al menos tres veces y cada vez cambiaba el criterio de cierre:
(a) "el repo tiene 19 migraciones" — son 18, el `wc -l` contaba `AppDbContextModelSnapshot.cs`;
(b) "dev tiene 4 filas `ZZ%` de catalogo legado" — eran coincidencias de `%ZZ%` en nombres reales,
cero residuo; (c) 2026-10-07, "produccion tiene 5 ventas y 4 movimientos de caja" — tiene **0
ventas y 1 movimiento**, o sea el riesgo medido era 4x mas chico que el declarado. El caso (c)
venia de un brief del orquestador y el (b) de una traza de QA: **una verificacion independiente
tambien puede propagar un dato mal leido.** El error puede caer en la direccion benigna, pero el
metodo que lo produce es el mismo que produce el que no.

**How to apply:** al abrir cualquier etapa, los numeros del brief son hipotesis, no datos. Medirlos
es la pasada 0 y suele ser la mas rentable. Si una medicion propia contradice al brief, gana la
medicion y se declara explicito que la premisa era falsa — no se arregla en silencio.

Ver tambien [[feedback-conteos-exactos-no-estimados]] y [[feedback-exit-code-de-herramienta]].
