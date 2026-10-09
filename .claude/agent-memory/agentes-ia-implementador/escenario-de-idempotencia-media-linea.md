---
name: escenario-de-idempotencia-media-linea
description: El escenario de un doble submit tiene que pedir MEDIA linea, porque con la linea entera el tope ataja el duplicado y la afirmacion pasa sobre el codigo roto; y poner la guarda de repeticion INVALIDA los escenarios que median el tope
metadata:
  type: feedback
---

**Dos mitades de la misma trampa, las dos medidas el 2026-10-08 en La Platense (`LP-119`).**

## 1. El escenario pide MEDIA linea, no la linea entera

Escribi la familia del doble submit parcial pidiendo las **dos primeras lineas completas** y la corri
contra el codigo sin arreglar: **pasaba**. No porque el codigo estuviera bien — porque el **tope** por
item atajaba el duplicado: facturar 2 de 2 dos veces deja el pendiente en 0 y el segundo POST sale con
*"quedan 0 por facturar"*.

El duplicado **solo entra cuando cada cantidad pedida es <= la MITAD del pendiente**: 1 de 2 deja
pendiente 1, y el segundo POST de 1 pasa el tope legitimamente. Con media linea aparecieron las 10
fallas.

**Why:** el tope y la idempotencia contestan **preguntas distintas** —*"¿esta cantidad cabe?"* vs.
*"¿este submit ya entro?"*— y **coinciden** cuando el submit es completo. Es la forma 1 del falso
verde (una afirmacion que pasa con y sin el fix) con una cara nueva: no coinciden los **numeros** por
casualidad, coincide el **veredicto** porque otra guarda hace el trabajo.

**How to apply:** en toda familia que tenga un **limite** (tope, cupo, saldo, stock) y se le agregue
una guarda de **repeticion**, el escenario del duplicado tiene que ejercitar un submit que el limite
**deje pasar dos veces**. Y la unica forma de saberlo es **correr la familia nueva contra el codigo sin
el fix antes de tocar una linea del Service**.

## 2. La guarda de repeticion INVALIDA los escenarios que median el tope

El escenario de concurrencia que ya existia largaba N competidores pidiendo **la cantidad completa**,
o sea **payloads identicos**. Con la guarda puesta, N payloads identicos son un **doble submit**: la
idempotencia los colapsa antes de que el tope los vea, los N contestan exito idempotente y el
escenario **deja de medir el tope** — con las afirmaciones de datos (un comprobante, nada facturado
de mas) **igualmente en verde**, que es lo peligroso.

Ya me habia pasado con el escenario de `LP-088` tras el fix de `LP-095`. **Es la segunda vez, asi que
es una regla y no una anecdota.**

**El arreglo no es relajar la afirmacion: es hacer los competidores DISTINGUIBLES** (cada uno pide una
milesima menos: 2 / 1,999 / 1,998...). Cada cantidad cabe sola, la suma no, y ninguna es la repeticion
de otra. **Y se deja una afirmacion-canario** que falla si alguna vez un competidor sale por
idempotencia, porque si no el escenario vuelve a perder su sentido en silencio.

**Cuando los payloads NO se pueden distinguir, decirlo y cambiar el contrato, no el veredicto.** El
atajo `FacturarAsync` **deriva** sus lineas del pendiente, asi que tres POST simultaneos piden lo mismo
por construccion. Ahi el invariante de datos sigue midiendo el lock (sin el, los tres leen la tabla de
comprobantes vacia y los tres emiten) y lo que cambia es **la respuesta**: "ganador" se redefine como
**emitio de verdad** (`Success && !EsAviso`).

## Y el corolario que ya tenia, confirmado otra vez

Contar filas **no** distingue "salio por idempotencia" de "salio por el tope": las dos dejan una sola
fila. Lo que distingue es **que se le contesta al operador**, asi que el orden entre las dos guardas
necesita su propia afirmacion sobre el **mensaje**. La guarda de repeticion va **antes** de la de
limite.

Ver [[forma-de-baja-inversa-entre-familias]] y [[mutante-del-importe-y-el-eco-de-ui]].
