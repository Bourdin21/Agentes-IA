---
name: precondicion-de-un-parche-en-lote
description: Un parche aplicado a N sistemas se verifica en el sistema de referencia y se declara OK en los N; la precondicion que el parche asume hay que LEERLA en cada uno
metadata:
  type: feedback
---

Cuando un mismo parche va a N sistemas, el valor que el parche **asume** (no el que escribe) se lee en cada uno de los N antes de declarar nada. Verificar en el de referencia y escribir "en los 14 queda igual que estaba" es cierto y a la vez inutil: lo que estaba era distinto.

**Why:** 2026-10-15, PAT-070 ("sesion larga solo para la PWA") se aplico a 14 sistemas asumiendo que el `ExpireTimeSpan` del navegador era de 8 h. En 5 era de **90 dias**, asi que el patron quedaba invertido: la app instalada nacia con 30 dias y el navegador tenia 90, o sea la PWA pedia login ANTES que el escritorio. La traza de la corrida anterior decia "navegador 8 h sin cambios" — verdad en 9, falso en 5. Nada en el codigo lo avisa: las dos piezas compilan y funcionan por separado.

**How to apply:** antes de cerrar un cambio en lote, escribir la precondicion como un grep y correrlo sobre los N (`grep -n "ExpireTimeSpan" **/Program.cs` sobre los 14 lleva un minuto y es lo que destapo esto). La frase "queda igual que estaba" en una traza es la senal de alarma: obliga a saber que era, por sistema. Y la precondicion se escribe en la entrada del patron (`docs/patrones/catalogo.yml`), no solo en la trazabilidad del proyecto, porque el que lo reutilice vuelve a caer. Ver [[verificar-criterios-contra-produccion]] y [[reuse-estructura-no-aritmetica]].
