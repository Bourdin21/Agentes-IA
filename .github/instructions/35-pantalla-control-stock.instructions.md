---
description: Patron de referencia para pantallas de control de stock (listado editable inline vs. formulario de ajuste, ledger inmutable, semantica reemplaza-vs-delta). Fuente real: marihogar (.NET 10, produccion), CR-61, 31/08/2026.
applyTo: "**/*.{cs,cshtml,md,instructions.md}"
---

# 35 - Pantalla de control de stock (listado editable inline)

Memoria tecnica reutilizable para cualquier proyecto nuevo que necesite una pantalla de gestion de stock/inventario. Antes de disenar una desde cero, leer esto — ya se resolvieron en produccion las decisiones de arquitectura y UX mas comunes (semantica de edicion, guardado, motivo, identificacion univoca de fila).

## Modelo de datos: columna desnormalizada + ledger inmutable, no calculo on-the-fly

Patron estable, ya usado en varios proyectos del estudio (marihogar `Producto.StockActual`/`MovimientoStock`, mismo concepto en otros): el stock actual de un producto es una **columna real** en la tabla del producto, escrita por un unico servicio de dominio (`IStockService` o equivalente) — nunca se recalcula sumando el historial de movimientos en cada lectura. El historial de movimientos (`MovimientoStock` o equivalente) es un **ledger inmutable**: nunca se edita ni se soft-deletea una fila ya escrita, solo se revierte con un contramovimiento si hiciera falta.

**Por que**: la columna desnormalizada permite que cualquier query del sistema (alertas de stock bajo minimo, validaciones de venta, listados con filtro/orden por stock) siga siendo una comparacion SQL directa (`WHERE StockActual < StockMinimo`), sin tener que traducir una agregacion sobre el ledger completo cada vez que se lee. El costo es la disciplina de que **un unico servicio** escriba esa columna, siempre en la misma transaccion que el movimiento que la justifica — nunca un `UPDATE` directo desde otro lugar del codigo.

## Ajuste manual vs. listado editable inline — cuando usar cada uno

Un formulario dedicado de "Ajuste manual" (elegir producto, cargar un delta +/-, motivo obligatorio) es el patron por defecto para una correccion puntual y ocasional. Pero si el caso de uso real del cliente es **carga masiva** (conteo fisico periodico, actualizacion de muchos productos de una sola sentada), un formulario por producto es lento — el patron correcto es un **listado con la columna de stock editable inline**, reemplazando (no complementando) al formulario:

- **Semantica: reemplaza, no delta.** El usuario escribe el stock real (el resultado de contar), no una cuenta de cuanto sumar/restar — el sistema calcula la diferencia internamente y la postea al ledger. Evita que el usuario tenga que hacer aritmetica mental fila por fila, que es exactamente el cuello de botella de una carga masiva.
- **`min="0"` en el input elimina la necesidad de "confirmar negativo".** Un formulario de delta (+/-) puede producir un resultado negativo si el usuario se equivoca, y necesita una confirmacion extra (SweetAlert2 "esto va a dejar el stock en -N, ¿confirmar?"). Al reemplazar en vez de sumar/restar, un valor negativo es simplemente invalido (el campo no lo permite escribir) — no hay decision de negocio que confirmar, es una simplificacion real del flujo viejo, no solo un recorte de alcance.
- **Guardado: por fila al instante (AJAX on blur/Enter) vs. en lote (un formulario con multiples filas y un solo submit)** — ambos son patrones validos, la eleccion depende de lo que pida el cliente, no asumir uno por defecto. Guardado por fila al instante da sensacion de "planilla en vivo" (mas rapido para tipear muchas filas seguidas); guardado en lote permite revisar todo antes de confirmar (mas seguro si el ledger es dificil de revertir). El precedente de ShowroomGriffin (`Stock/MatrizEditar.cshtml`) usa guardado en lote con un unico `<form>` — no asumir que ese mecanismo de transporte aplica si el cliente pide "al instante"; son disenos de UI distintos aunque compartan la semantica "reemplaza, no delta".
- **Motivo: opcional en la version inline, con generacion automatica en el ledger.** Pedirle al usuario un motivo por cada fila editada mata la velocidad de una carga masiva. Si el cliente confirma explicitamente que no quiere que se lo pidan, la version inline no muestra el campo — pero el `MovimientoStock`/ledger sigue recibiendo un `Motivo` no vacio generado por el sistema (ej. `"Ajuste desde listado de Stock"`), para no romper la invariante de que un movimiento tipo Ajuste siempre tiene contexto textual, y para no dejar el ledger con un campo NULL que otro reporte pueda no esperar. **Esto es un trade-off que debe confirmar el cliente explicitamente** (perder trazabilidad del "por que" en texto libre a cambio de velocidad) — no asumirlo por default, preguntarlo.
- **No escribir un movimiento de cantidad 0.** Si el usuario edita una celda pero el valor final coincide con el que ya tenia (toco el campo sin cambiarlo, o escribio y borro), no postear nada al ledger — evita ruido de auditoria sin informacion real.

## Identificacion univoca de fila — critica cuando el guardado es sin confirmacion

Si el guardado es al instante y sin dialogo de confirmacion (patron de arriba), el listado **debe garantizar que el usuario identifica sin ambiguedad la fila que esta editando** antes de escribir un ledger irreversible:

- Toda columna ofrecida como filtro debe tener su dato visible como columna en la tabla — un filtro sobre un campo invisible (ej. filtrar por "Modelo" pero no mostrar la columna Modelo) deja al usuario sin forma de confirmar que agarro la fila correcta cuando hay productos con el mismo nombre pero distinto modelo/variante.
- Si una pantalla externa linkea al listado con un filtro pre-cargado (ej. un boton "Ajustar stock" desde el listado de Productos que navega a `Stock/Index?nombre=X`), verificar si ese filtro usa **igualdad exacta o coincidencia parcial** (`Contains`) — un filtro parcial puede traer mas de una fila cuando el diseno asumia que iba a quedar una sola. Si el campo usado para filtrar (ej. `Nombre`) no tiene restriccion de unicidad en la base, dos productos homonimos son un escenario real, no un caso de borde a ignorar.

## Cuidado con `RowVersion`/concurrencia optimista generica y procesos batch en paralelo

Si el proyecto usa un manejador generico de concurrencia optimista (ej. un hook en `DbContext.SaveChanges` que renueva `RowVersion` ante **cualquier** propiedad modificada de una entidad, sin discriminar cual), una pantalla de edicion rapida por celda (como el listado de stock de arriba) puede colisionar con un proceso batch que ya tiene una previsualizacion/lote abierto sobre la MISMA entidad (ej. un "Aumento masivo de precios" con preview ya calculado, esperando confirmacion del usuario) — el batch se aborta con un mismatch de concurrencia si alguien edita el stock de un producto que ya esta en ese lote, aunque los dos cambios sean sobre columnas distintas y no exista conflicto real de datos.

**Esto no es un problema exclusivo de esta pantalla** — es un riesgo latente en cualquier combinacion de "edicion rapida fila por fila" + "proceso batch con confirmacion diferida" sobre la misma entidad, bajo un `RowVersion` que no distingue que campo cambio. Si aparece en un proyecto nuevo:
- Documentarlo como limitacion conocida en vez de forzar un fix apurado — tocar el manejador generico de concurrencia es transversal a todo el proyecto (afecta cualquier entidad con `RowVersion`), no un cambio acotado a la pantalla de stock.
- Recomendacion operativa minima mientras no se resuelva: avisar al cliente que evite correr el proceso batch en paralelo con una sesion de carga masiva sobre la misma entidad.
- Si se decide resolverlo de raiz, evaluarlo como un item propio de Arquitectura (no como parte del CR de la pantalla de stock) — puede requerir que `RowVersion` se scoped por grupo de columnas, o que el proceso batch relea el estado justo antes de confirmar en vez de confiar en un `RowVersion` capturado en el momento de la previsualizacion.

## Que NO tocar al construir esta pantalla

- El metodo que descuenta/repone stock desde Ventas/Compras (tipicamente `RegistrarMovimientoAsync` o equivalente) **nunca bloquea por stock negativo** — es una regla de negocio deliberada y distinta de la de "Ajuste manual"/listado inline (que si valida `>= 0`). No unificar ambas validaciones: una venta se puede confirmar aunque supere el stock disponible (advertencia no bloqueante en la UI), un ajuste manual/inline no.
- Las alertas de "stock bajo minimo" (dashboard, badges de listados) siguen leyendo la columna desnormalizada directo — no requieren ningun cambio al construir el listado editable, siempre que la columna se siga escribiendo en la misma transaccion que el movimiento.
