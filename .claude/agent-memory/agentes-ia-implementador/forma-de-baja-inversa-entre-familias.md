---
name: forma-de-baja-inversa-entre-familias
description: "Fila vieja vs fila nueva" NO predice si una baja abre una guarda de idempotencia: en dos familias del mismo sistema salio INVERSO. Hay que preguntar que hecho devuelve la CAPACIDAD de repetir la operacion.
metadata:
  type: feedback
---

Antes de escribir una guarda de idempotencia por clave natural hay que preguntar **como se da de baja
esa entidad**. Eso ya lo sabia. **Lo que aprendi el 2026-10-08 es que la respuesta estructural no
alcanza, y me salio al reves en dos sitios consecutivos del mismo sistema.**

**Why:** en `MovimientoCCEmpleado` (`LP-114`) la baja es un **contramovimiento** —fila nueva, la vieja
queda intacta con `EsReversion = false`— asi que la guarda **tenia** que abrirse mirando fuera de la
fila, o registrar → revertir → re-registrar el mismo dia quedaba bloqueado y el empleado no cobraba.
De ahi saque la regla "ojo con la cuarta forma de baja, la que es fila nueva".

En `FacturacionParcialService` (`LP-119`) es **exactamente al reves**:

| Hecho | Estructura | ¿Abre la guarda? |
|---|---|---|
| `DeletedAt` del comprobante | **fila vieja** | **SI** — los lectores del ya-facturado filtran por el, o sea que la baja **devuelve el pendiente** |
| Nota de credito | **fila nueva** (contramovimiento) | **NO** — R18: la NC acredita un documento, no lo deshace; el pendiente **no vuelve** |

O sea: la forma en que la baja se **expresa** (fila vieja / fila nueva) **no predice nada**. Si hubiera
aplicado la regla de `LP-114` por analogia, la NC habria abierto la guarda y el mismo item quedaria
vendido una vez y facturado dos — el defecto que R18 existe para prohibir.

**How to apply:** la pregunta correcta no es *"¿donde se ve la baja?"* sino **"¿que hecho devuelve la
CAPACIDAD de volver a hacer esta operacion?"**, y se contesta por familia, mirando **el criterio que
los lectores del tope/pendiente ya aplican**. Si el pendiente vuelve, la guarda se abre; si no vuelve,
no se abre, por mas contramovimiento que haya. En este caso el discriminador ya estaba escrito y era
literal: los dos filtros que `ObtenerYaFacturadoPorItemAsync` usaba (`DeletedAt == null` y
`ComprobanteAsociadoId == null`) son **exactamente** los que la guarda nueva necesita. Copiarlos de
ahi es lo que evita inventar un segundo criterio para el mismo hecho.

**Y las dos direcciones necesitan su mutante**, porque son dos defectos opuestos: uno que ignore el
soft delete (bloquea una refacturacion legitima) y uno que excluya el contramovimiento (reabre el
pendiente). En la medicion, el primero tumbo 1 afirmacion y el segundo **sobrevivio con cero** — y la
lectura correcta era *"falta el escenario"*: sin el filtro de NC, el aviso le devuelve al operador el
Id de una **nota de credito** presentandolo como la factura. El escenario que lo mata se construye
para que **solo la NC pueda coincidir** (factura por 2, NC por 1, POST de 1).

Ver [[escenario-de-idempotencia-media-linea]].
