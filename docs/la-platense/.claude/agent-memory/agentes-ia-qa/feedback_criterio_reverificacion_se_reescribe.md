---
name: criterio-reverificacion-se-reescribe
description: Si el fix resolvio el defecto cambiando el diseno en vez de poner la guarda que el parte pedia, el criterio de re-verificacion queda inverificable: se reescribe sobre el invariante y se declara, no se marca FAIL.
metadata:
  type: feedback
---

Un criterio de re-verificacion describe **una** forma de cerrar el defecto, no el defecto. Si el implementador
eligio otra forma (legitima), el criterio literal puede volverse imposible de cumplir sin que el defecto siga
vivo. En ese caso: **reescribir el criterio sobre el invariante, declarar el cambio en `6-qa.md` y en la traza,
y calificar contra el invariante.** Nunca marcar FAIL por la letra, y nunca aprobar por interpretacion tampoco:
el invariante tiene que seguir siendo una assertion observable.

**Why:** 2026-10-06, `LP-040`. El parte pedia *"el POST se rechaza con un mensaje de negocio que nombra el
comprobante y la venta sigue en `Confirmada`"*. El fix no puso la guarda: **retiro el camino** —`FacturarAsync`
paso a delegar en `FacturacionParcialService.EmitirAsync`—, que era la alternativa que el propio parte declaraba
*"valida y probablemente mejor, decision del analista"*. Con ese diseno lo correcto es **emitir por el pendiente**,
asi que "rechazar" habria sido un FAIL de un sistema correcto. El invariante que no cambio: *los mismos items no
pueden quedar facturados por dos documentos*, mas la `condicion_falla` del catalogo (query de deteccion) en
**0 filas**. (Antes habia pasado lo mismo en eleven-la-plata con `ELV-005`.)

**How to apply:** al abrir una re-verificacion, leer el diff **antes** de fijar los criterios. Si el fix cambio el
contrato, buscar el invariante en el `causa_raiz` / `condicion_falla` del item del catalogo (que sobreviven al
cambio de diseno) en vez de en el `criterio_aceptacion` (que no). Escribir el criterio nuevo en el
`fix_aplicado` del catalogo para que la proxima corrida lo herede ya corregido. Y verificar como criterio propio
lo que el cambio de diseno **retiro**: si el fix saco guardas y las delego, hay que medir que el delegado las
aplique — en `LP-040` eso significo probar las 4 transiciones invalidas (`Borrador`, `Anulada`, `Facturada`,
inexistente) que el metodo habia dejado de guardar.
