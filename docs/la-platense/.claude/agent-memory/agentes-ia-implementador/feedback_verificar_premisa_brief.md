---
name: verificar-premisa-brief
description: En La Platense, verificar contra el codigo real toda premisa "esto esta abierto/falta hacerlo" que traiga un brief del orquestador (ya paso 3 veces), antes de escribir una linea
metadata:
  type: feedback
---

Antes de implementar un item que el brief declara "abierto en produccion" o "falta construir",
**leer el codigo real del metodo citado**. Tres veces seguidas el punto de partida del brief fue falso.

**Why:** el orquestador redacta los briefs a ciegas, sin leer el repo. Tres casos medidos:
(a) ronda del 2026-10-06 de la familia de atomicidad — el mensaje de `3cf60ab` daba por cerrados
6 sitios "sin medir" y en realidad **ya estaban escritos**; (b) lote CR-01/CR-02 del 2026-10-06 —
el brief declaraba `LP-014` (gate de precio por rol) "abierto en produccion" con numeros de linea
exactos, y estaba **completo desde el 2026-10-05** y ya verificado PASS por QA. Implementarlo de
nuevo habria sido trabajo duplicado sobre el servicio mas sensible del sistema.

El agravante: el brief trae numeros de linea ("~147-156"), que dan una sensacion de verificado
que no tienen. Los numeros salen del documento de diseño, no del archivo.

(c) **Lote `LP-041`/`LP-037` del 2026-10-07** — el brief pedia corregir el XML-doc de
`BloquearPeriodoCajaAsync` "que afirmaba cerrar las dos mitades del descuadre y no es cierto". **Ya
estaba corregido**: el propio XML-doc decia "este XML-doc afirmaba que cubria las dos hasta
2026-10-06, y era falso". El brief describia el estado ANTERIOR al commit que encontro el defecto. Lo
que si habia que hacer era reescribirlo con el mecanismo nuevo — distinto trabajo, misma linea del
brief. Costo de no verificar: habria "arreglado" algo correcto, o peor, habria dudado del diagnostico.

(d) **Lote 2 de la Entrega 5 del 2026-10-07, y es la variante que mas cuesta ver: la premisa era
PARCIALMENTE cierta, y obedecerla al pie de la letra rompia el codigo.** El brief decia *"nunca
escribas `Producto.Stock` directo: el proyecto tiene un unico escritor y se respeta"*. El unico
escritor que el proyecto defiende es el de **la TABLA del ledger `MovimientoStock`**, NO el de la
columna `Stock` — y el XML-doc de `IMovimientoStockService.RegistrarMovimientoAsync` lo declara
explicito: *ese metodo NO toca `Producto.Stock`, lo mueve el caller sobre la instancia que ya tiene
cargada*. `OrdenCompraService.RecibirAsync`, el unico escritor real del ledger, escribe **las dos
cosas**. Obedecer el brief literalmente habria dejado el stock **sin mover**: el ledger diria que
entro mercaderia y el catalogo no, y nada habria fallado.

**La forma general:** un brief puede citar una regla REAL del proyecto y **errarle al sujeto**. La
regla existia, el nombre era casi el mismo, y la diferencia (la tabla vs. la columna) es justo la que
decide que codigo escribir. **Se detecta leyendo el XML-doc del contrato que la regla nombra**, no el
brief ni el nombre del servicio.

**How to apply:** por cada item del brief, un `grep` del simbolo o del guard que supuestamente
falta antes de planificar. Y si el brief invoca una regla del proyecto ("hay un unico escritor", "ya
existe la guarda"), **abrir el contrato que la declara y leer de QUE es la regla**: el sujeto de una
regla transversal es lo primero que un brief redactado de memoria confunde. Si ya esta, decirlo en la salida como hallazgo (no como item hecho) y
no tocarlo. Ojo tambien al reciproco: el **comentario** del codigo puede estar vencido aunque el
codigo este bien (ver [[comentarios-vencidos-lp008]]) — la fuente de verdad es la sentencia que
ejecuta, no su XML-doc ni su bloque de seguridad.
