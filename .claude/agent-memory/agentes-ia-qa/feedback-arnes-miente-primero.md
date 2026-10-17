---
name: feedback-arnes-miente-primero
description: Ante un resultado inesperado en una prueba, sospechar del arnés antes que del sistema — y usar un contacto nuevo por escenario, sin acciones masivas en el medio
metadata:
  type: feedback
---

Ante un resultado inesperado, chequear **primero el arnés contra la base**, no reportar el defecto.
Dos falsos negativos en la re-verificación de CRM-029 (2026-10-16) salieron del arnés, no del CRM:

1. Un helper usaba un parámetro de filtro inventado (`soloNoLeidos`) y el endpoint devolvía *todo*,
   así que el chequeo daba "no leído = True" siempre. El filtro real estaba en el ViewModel
   (`Interaccion=noLeidos`).
2. Contaminación cruzada: reciclé el mismo contacto entre escenarios y corrí un `MarcarTodosLeidos`
   **masivo** en el medio, que pisó el estado de un contacto de otra prueba. Además, 12 mensajes al
   mismo contacto en 2 minutos dispararon el corte anti-loop del bot y se comieron un mensaje.

**Why:** los dos resultados parecían defectos reales y dignos de un parte. Reportarlos habría
mandado al implementador a buscar un bug que no existe, y habría costado la credibilidad del reporte
de verdad que sí había (CRM-030).

**How to apply:** un **contacto/entidad nueva por escenario**, nunca reciclar; ninguna acción masiva
entre dos mediciones de escenarios distintos; espaciar los eventos si el sistema tiene cortes
anti-flood. Y antes de escribir un parte de defecto, verificar la aserción contra la base por una
vía independiente de la que la midió. Si un parámetro de filtro o de query lo inventé yo, leer el
ViewModel o el controller y confirmar el nombre real.

**Tercera y cuarta vez, 2026-10-16 (cola de seguimiento del CRM).** Dos falsos FAIL mas, los dos del
grader y no del sistema:

- **Clasificar por el booleano de resultado en vez de por DONDE corto.** Midiendo la reserva atomica
  de CRM-032 conte como "gano la reserva" a todo POST que no dijera "toque en curso", pero 6 de 8 los
  habia cortado antes el pre-chequeo: el sistema habia hecho lo correcto (1 solo envio) desde el
  principio. En un camino con varios guards en cadena el oraculo es **cual de los guards contesto**,
  con un marcador inequivoco por guard. Un `ok=false` no distingue nada.
- **Mirar el HTML cuando el estado lo pone el JS.** Los filtros persistidos en Session no aparecian
  como seleccionados en el markup porque la vista los restaura por script con `.val(...)`. Antes de
  declarar que un valor no viaja, buscar quien lo escribe del lado del cliente.

**How to apply (agregado):** cuando un resultado contradice lo que el implementador midio con un
arnes propio, sospechar del grader antes que del sistema — sobre todo si el implementador avisó de la
trampa (avisó que una prueba secuencial da falso verde) y el resultado raro cae justo ahi.

Relacionado: [[entorno-sin-navegador]], [[crm-028-estado]]
