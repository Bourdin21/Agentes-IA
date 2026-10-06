---
name: arnes-falla-del-instrumento
description: Antes de perseguir una FALLA del arnes como defecto del sistema, descartar que sea una afirmacion mal escrita contra estado que los escenarios previos ya consumieron
metadata:
  type: feedback
---

Cuando una afirmación del arnés falla, **primero descartar que la falla sea del instrumento.** El
caso típico: una afirmación compara contra un valor prístino (`stock == 1000`) que los escenarios
anteriores del **mismo** arnés ya consumieron.

**Why:** pasó en la corrida de CR-01/CR-02 (2026-10-06). La afirmación "no se descuenta stock"
comparaba contra 1000 y la base decía 992, porque los escenarios 1 a 4 ya habían vendido 8 unidades
del mismo producto sembrado. Leído rápido parece un descuento de stock indebido en el camino que se
estaba probando — justo el tipo de defecto que se estaba buscando — y hace perder tiempo
persiguiendo algo que no existe.

**How to apply:** una afirmación de "esto no cambió" captura el valor **inmediatamente antes** del
escenario y compara contra ese, nunca contra la constante de siembra. Si varios escenarios comparten
el mismo fixture, o cada uno siembra lo suyo, o cada uno mide su propio delta.

El reverso también vale y es peor: un arnés que **pasa** puede estar roto (ver
[[arnes-afirmacion-vacia]]). La cuenta de OK no es evidencia por sí sola; el detalle impreso de cada
afirmación sí, y por eso cada una imprime el número medido y el esperado.
