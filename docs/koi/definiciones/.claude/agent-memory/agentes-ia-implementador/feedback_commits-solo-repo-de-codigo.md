---
name: implementador-solo-commitea-repo-de-codigo
description: Al cerrar una etapa, commitear sólo el repo del sistema (ej. KoiDumplings); nunca el repo Agentes-IA, aunque se hayan actualizado sus documentos
metadata:
  type: feedback
---

Cuando el pedido dice "commit con el formato del proyecto", eso es **el repo del sistema** (`C:/Sistemas/KoiDumplings`, ShowroomGriffin, etc.). Los cambios en `C:/Sistemas/Agentes-IA` —`5-implementador.md`, `trazabilidad.md`— se dejan en el working tree, sin commitear.

**Why:** `Agentes-IA` es un repo compartido por todos los proyectos del estudio y casi siempre tiene cambios pendientes de varios a la vez (contadores-bma, delicias-naturales, marihogar, koi…). Un commit desde una etapa arrastraría trabajo de otros proyectos que no se revisó. El dueño los consolida él, en commits propios que suele llamar "memorias".

**How to apply:** `git add` acotado a los directorios del repo de código, y decir en el cierre que los documentos quedaron sin commitear a propósito. Si el pedido menciona explícitamente commitear la documentación, preguntar antes de arrastrar los cambios de los otros proyectos.

Ver también [[koi-e25-pendiente]].
