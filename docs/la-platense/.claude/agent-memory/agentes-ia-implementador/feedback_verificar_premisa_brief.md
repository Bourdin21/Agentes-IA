---
name: verificar-premisa-brief
description: En La Platense, verificar contra el codigo real toda premisa "esto esta abierto/falta hacerlo" que traiga un brief del orquestador, antes de escribir una linea
metadata:
  type: feedback
---

Antes de implementar un item que el brief declara "abierto en produccion" o "falta construir",
**leer el codigo real del metodo citado**. Dos veces seguidas el punto de partida del brief fue falso.

**Why:** el orquestador redacta los briefs a ciegas, sin leer el repo. Dos casos medidos:
(a) ronda del 2026-10-06 de la familia de atomicidad — el mensaje de `3cf60ab` daba por cerrados
6 sitios "sin medir" y en realidad **ya estaban escritos**; (b) lote CR-01/CR-02 del 2026-10-06 —
el brief declaraba `LP-014` (gate de precio por rol) "abierto en produccion" con numeros de linea
exactos, y estaba **completo desde el 2026-10-05** y ya verificado PASS por QA. Implementarlo de
nuevo habria sido trabajo duplicado sobre el servicio mas sensible del sistema.

El agravante: el brief trae numeros de linea ("~147-156"), que dan una sensacion de verificado
que no tienen. Los numeros salen del documento de diseño, no del archivo.

**How to apply:** por cada item del brief, un `grep` del simbolo o del guard que supuestamente
falta antes de planificar. Si ya esta, decirlo en la salida como hallazgo (no como item hecho) y
no tocarlo. Ojo tambien al reciproco: el **comentario** del codigo puede estar vencido aunque el
codigo este bien (ver [[comentarios-vencidos-lp008]]) — la fuente de verdad es la sentencia que
ejecuta, no su XML-doc ni su bloque de seguridad.
