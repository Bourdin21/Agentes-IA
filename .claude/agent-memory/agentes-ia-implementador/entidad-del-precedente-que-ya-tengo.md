---
name: entidad-del-precedente-que-ya-tengo
description: Antes de crear la entidad que un precedente tiene con ese nombre, averiguar que ROL cumple alla: puede ser algo que el destino ya tiene con otro nombre, y construirla seria duplicar el mismo libro.
metadata:
  type: feedback
---

Cuando un modulo nuevo se ancla en un precedente que tiene una entidad con ese nombre, la pregunta
no es "¿como copio `MovimientoCCLocal`?" sino **"¿que ES `MovimientoCCLocal` en ese proyecto?"**.
Buscar su rol en el mapa de dependencias del origen, no su nombre. Si el rol que cumple alla ya lo
cumple otra entidad en el destino, **no se crea nada**: se construye la vista o el servicio que
faltaba sobre lo que ya hay.

**Why:** en la-platense Entrega 4, el modulo 13 del WBS se llama "cuenta corriente propia del
negocio" y marihogar tiene `MovimientoCCLocal` + `CCLocalService` + `CCLocalController`. El camino
natural —crear `MovimientoCCLocal` en el destino— habria sido un desastre silencioso: en marihogar
esa entidad **ES la caja**, su unico ledger de dinero (su `CajaService` no tiene entidad propia, es
pura agregacion sobre ese ledger). En la-platense ese ledger ya existia y se llama `CajaMovimiento`,
y encima con cierres diarios y mensuales que el origen no tiene. Crear el segundo habria dejado
**dos libros del mismo dinero**, que es como se descubre meses despues que ninguno de los dos
cuadra — y el defecto no aparece en ningun build ni en ningun test, aparece cuando el cliente
compara dos pantallas. Lo que el presupuesto pedia, leido literal, era "vista consolidada": una
pantalla de lectura, no una tabla.

**How to apply:** ante un modulo anclado en una entidad de otro proyecto, antes de escribir el
`Domain/Entities/*.cs`:

1. Leer el mapa de dependencias / `3-arquitecto-mvc.md` del ORIGEN y responder **quien escribe esa
   tabla y quien la lee**. Eso define su rol mejor que su nombre.
2. Preguntarse si ese rol ya esta ocupado en el destino. Los nombres divergen por historia: el mismo
   concepto puede ser `MovimientoCCLocal` en un proyecto y `CajaMovimiento` en otro.
3. Releer la frase EXACTA del presupuesto. "Vista consolidada de X" es una pantalla; "registrar X"
   es una tabla. La diferencia estaba escrita y es facil pasarla de largo cuando el precedente
   ofrece una entidad lista para copiar.
4. Si el rol esta ocupado: el entregable es la pantalla/servicio que falta **mas** lo que le daba
   sentido y no estaba (en este caso, el saldo inicial declarado y el contraste de los cierres). Se
   escribe en el reporte como decision, con el precedente citado — "no construi la entidad porque
   alla ES la caja" es defendible; "no la construi" solo, no.

**Senal de alarma concreta:** si para justificar la entidad nueva hay que explicar como se van a
mantener sincronizadas las dos tablas, la entidad no va. La sincronizacion es el sintoma de la
duplicacion.

Relacionado: [[reuse-estructura-no-aritmetica]] (el eje complementario: una vez decidido QUE se
copia, la aritmetica igual hay que relevarla campo por campo).
