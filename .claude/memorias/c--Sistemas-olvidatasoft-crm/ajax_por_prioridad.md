---
name: ajax-por-prioridad
description: "Regla general de UI — usar AJAX y re-renderizar solo la fila/partial afectada, nunca la pantalla completa, siempre que sea viable"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6dad76aa-39ef-4734-885b-25074d2a71fb
  modified: 2026-09-01T23:39:30.514Z
---

Al implementar una acción de UI que modifica un dato puntual dentro de un listado (marcar leído, eliminar, cambiar estado, etc.), usar AJAX por prioridad y re-renderizar **solo la fila o la partial afectada** — nunca recargar la pantalla completa (`RedirectToAction` a un `Index` completo) cuando la acción es puntual.

**Por qué:** pedido explícito del cliente (2026-08-31), tras notar que las acciones de la pantalla de notificaciones (marcar leída, eliminar) recargaban todo el listado para un cambio de una sola fila.

**Cómo aplicar:**
- Patrón ya establecido en el proyecto CRM Olvidata (`ChatsController.MarcarNoLeido`/`MarcarTodosLeidos`, `NotificationsController` desde 2026-08-31): la acción del controller detecta AJAX vía `Request.Headers["X-Requested-With"] == "XMLHttpRequest"` y devuelve `Json(new { ok, mensaje })` en vez de `RedirectToAction`; conserva el redirect como fallback solo si la request NO es AJAX (JS deshabilitado).
- El JS del lado cliente actualiza el DOM de forma quirúrgica: agrega/saca clases, oculta/muestra botones, remueve el elemento de la fila — sin volver a pedir ni redibujar el resto de la pantalla.
- Si la acción afecta a varias filas a la vez (ej. "marcar todas leídas"), el criterio sigue siendo el mismo en espíritu: actualizar solo las filas ya renderizadas en el DOM client-side, no recargar toda la pantalla — no hace falta que el servidor devuelva una partial nueva si el cambio en cada fila es simple (sacar una clase, ocultar un botón).
- Reservar el re-render de una partial completa (`PartialView`) para cuando el HTML de la fila cambia de forma no trivial y no conviene duplicar esa lógica de armado en JS (ver `ChatsController.HiloParcial`/`ListaParcial` para ejemplos de partials ya usadas en el proyecto).
- Esto aplica como criterio de diseño por defecto en cualquier proyecto del estudio, no solo en `crm-olvidata` — evaluar siempre esta opción antes de usar un `<form>` con submit clásico + `RedirectToAction` para una acción de listado.
