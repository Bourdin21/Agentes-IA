---
name: falsos-verdes-la-platense
description: Las cuatro formas en que los arneses de La Platense dan verde sin cubrir, con el barrido concreto que detecta cada una. Se recorre antes de aceptar cualquier "N OK / 0 FALLADAS".
metadata:
  type: project
---

Las cuatro formas catalogadas hasta el 2026-10-06, en orden de aparicion:

1. **La afirmacion que pasa en los dos mundos.** Con AFIP apagado, "el atajo es rechazado" pasa con el defecto
   puesto (el error es de la integracion) y sin el. La afirmacion tiene que medir que el codigo **haga lo
   correcto**, no que falle. Se detecta por mutacion, nunca leyendo.
2. **El arnes no siembra la rama.** `LP-039`: el mensaje tenia dos ramas (numero fiscal / id interno) y el arnes
   solo ejercitaba una, porque con AFIP apagado ningun comprobante tiene numero. Antes de dar PASS a "el mensaje
   dice X", contar las ramas del ternario/`string.Join` y verificar una siembra por rama.
3. **La afirmacion que ningun mutante mata.** Puede ser defensa en profundidad (un invariante con dos guardas
   encima) y no necesariamente vacia. Lo que hay que escribir no es "vacia" ni "OK" sino **que mide**. Y hay que
   mutar **todas** las afirmaciones nuevas, no solo las que muto el implementador.
4. **El arnes muere, o no mide, en vez de fallar** — la peor, porque la salida de un arnes que no corrio es
   indistinguible de "no hay nada que reportar". Dos casos medidos:
   - `ArnesVentaSinFacturaYParcial` 8.9 indexaba `comprobantes[1]` sin verificar el `Count`: bajo mutacion moria
     por indice fuera de rango y dejaba 14 afirmaciones sin ejecutar (el implementador lo encontro y corrigio).
   - `ArnesReconciliacionTx` (`LP-041`, 2026-10-06): su `LimpiarAsync` borra `ItemsVenta` sin borrar antes
     `ComprobantesAfipItems`. En cuanto `LP-040` hizo que el atajo **si** cree comprobantes con AFIP apagado, la
     FK `RESTRICT` lo mata. **La segunda corrida sobre la misma base termina en 0 OK / 0 FALLADAS con exit 127.**

**Why:** en este proyecto los arneses son la unica medicion de concurrencia y atomicidad que existe, y un arnes
verde (o mudo) cierra defectos que siguen vivos. Las cuatro formas aparecieron todas en corridas reales, ninguna
leyendo codigo.

**How to apply:** antes de aceptar un "N OK / 0 FALLADAS", en este orden:
- Contar las afirmaciones **evaluadas** (`grep -c '^  OK '` + `grep -c '^  FALLA '`) en **cada** corrida de cada
  mutante, y exigir que el total sea el mismo en todas. Si baja, el arnes murio o salteo.
- Correr el arnes **dos veces seguidas sobre la misma base**: una limpieza incompleta se manifiesta recien en la
  segunda.
- Barrer el indexado: todo `[0]`/`[1]` tiene que estar cortocircuitado (`Count == N && ...`) o dentro de un `if`
  que tenga su propia afirmacion ruidosa al lado.
- Barrer la limpieza de **todos** los arneses del repo contra las FK `RESTRICT` nuevas, no solo el del sprint.
  El 2026-10-06 el implementador arreglo su propio arnes y dejo los dos hermanos con el mismo patron
  (`ArnesSeisSitiosRestantes` no rompio solo porque no llama a `FacturarAsync`).

Ver tambien [[feedback_control_positivo_commit_anterior]].
