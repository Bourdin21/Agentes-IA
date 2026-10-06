---
name: desvio-de-un-port-literal
description: Cuando el brief ordena portar un mecanismo de otro proyecto "literal", medir el radio de impacto en ESTE proyecto antes de obedecer; el propio catalogo puede tener escrito el contra-criterio.
metadata:
  type: feedback
---

Un brief que dice "esto lo resuelve <otro proyecto>, portalo, acá es literal" **no exime de medir el
radio de impacto en este proyecto**. Antes de portar: buscar **todos** los escritores de la entidad o
del mecanismo que se va a tocar, y si el port cambia el comportamiento de un modulo que QA ya paso,
eso es parte del costo y hay que declararlo.

**Why:** en la-platense (familia LP-018, 2026-10-06) el brief pedia portar `Producto.RowVersion` de
marihogar textualmente. Un token de concurrencia es **global al modelo**, y `Producto` tenia dos
escritores masivos que guardan entidades trackeadas por lotes sobre 112.485 filas
(`AumentoMasivoPrecioService`, `ClasificacionAbcAutomaticaService`): con el token, **una sola** edicion
concurrente aborta el `SaveChanges` del lote completo, cuando hoy rechaza fila por fila y sigue.
Ademas el `RowVersion` comparaba la cosa equivocada para el caso (cambia con cualquier columna, asi que
una edicion de precio ajena rechazaria un conteo fisico correcto). Y lo mas util: **`docs/patrones/
catalogo.yml` ya tenia escrito el contra-criterio para ESTE proyecto**, en la nota de `PAT-004` del dia
anterior — *"la salida no es agregar RowVersion a una entidad de 112.485 filas en el medio de otra
entrega"*. El brief lo venia de un agente, no de Joaquin; la preferencia de Joaquin ("copiar de
marihogar lo mas posible") es general, no una instruccion sobre ese mecanismo.

**How to apply:** portar el **criterio** (que garantia se quiere y donde vive: la base, no la memoria) y
elegir la implementacion que lo cumple con el menor radio. Escribir el desvio **fuerte y en tres
lugares**: el comentario del codigo, la memoria del proyecto y el reporte, con las razones en orden de
peso y una linea explicita de "queda para que Joaquin lo confirme o lo revierta". Nunca desviarse en
silencio, y nunca obedecer en silencio tampoco: si el port rompe otro modulo, decirlo antes de hacerlo.

Corolario de busqueda: antes de declarar que un patron "no existe en este proyecto", leer la nota de la
entrada del catalogo completa — las variantes por proyecto viven ahi y suelen estar escritas por mi
mismo en una ronda anterior. Ver [[reuse-estructura-no-aritmetica]] y
[[entidad-del-precedente-que-ya-tengo]], que son la misma familia de error en el otro sentido.
