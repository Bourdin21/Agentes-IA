---
name: feedback-no-commit-no-deploy
description: El implementador deja los cambios en el working tree sin commitear ni deployar; el commit, la migración en producción y el deploy los autoriza Joaquín explícitamente
metadata:
  type: feedback
---

Al terminar una implementación: dejar los cambios **sin commitear** y **sin deployar**, y la migración
EF aplicada **solo en dev**. El commit, la migración en producción y el deploy esperan una
autorización explícita de Joaquín, pedido por pedido.

**Why:** separación de roles del estudio — quien construye no califica ni libera. El QA prueba después
con el repo en read-only, y un defecto encontrado post-commit es más caro de revertir que uno en el
working tree. Joaquín lo pidió literalmente en el pedido de CRM-028 ("No commitees y no deployes:
queda pendiente de mi autorización. Tampoco toques producción").

**How to apply:** al cerrar la etapa, correr el build, aplicar la migración en dev, actualizar
`5-implementador.md` + `trazabilidad.md`, y reportar el estado del working tree — nada más. Si el
pedido no dice nada sobre deploy, asumir que **no** va: preguntar antes, no después. Lo mismo para
rotar un secreto en el hosting: se reporta el valor para que lo cargue él, no se carga por cuenta
propia.
