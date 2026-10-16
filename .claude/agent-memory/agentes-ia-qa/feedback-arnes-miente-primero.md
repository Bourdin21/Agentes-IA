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

Relacionado: [[entorno-sin-navegador]], [[crm-028-estado]]
