---
name: control-positivo-commit-anterior
description: Antes de reportar como regresion una falla de un arnes, reproducirlo sobre el commit ANTERIOR con una base limpia; y nunca dar por cierto el "N OK / 0 FALLADAS" que declara una memoria sin reproducirlo.
metadata:
  type: feedback
---

Cuando un arnes de este proyecto falla en el commit bajo prueba, **correrlo tambien sobre el commit anterior,
con una base desechable propia**, antes de escribir una sola linea de parte. Y si una memoria declara un numero
("`ArnesReconciliacionTx` 153 OK / 0"), ese numero es una hipotesis hasta que se reproduce.

**Why:** el 2026-10-06, re-verificando `LP-040` (commit `c5740c7`), `ArnesReconciliacionTx` dio **142 OK / 10
FALLADAS + crash** contra un "153 OK / 0" que dos memorias daban por cierto. El control en `f05cc92` dio
**147 OK / 6 FALLADAS sin crash**. O sea: **6 de las 10 fallas ya estaban** (grupo 16, *"La fecha del movimiento
no puede ser futura"* — depende del reloj/huso y falla en la ventana nocturna) y el "153/0" **no se reproduce en
ninguno de los dos commits**. Sin el control positivo el parte habria reportado 10 fallas como regresion, o —
peor — habria dado el commit por regresivo en algo que no toco. El delta real eran 4 afirmaciones obsoletas y el
crash, y eso si era del commit.

**How to apply:** ante cualquier FAIL de un arnes en una re-verificacion: (1) base limpia nueva, (2)
`git checkout <commit anterior>`, build, misma corrida, (3) el parte reporta **el delta**, no el total, y nombra
explicitamente las fallas preexistentes y su causa. Si el numero declarado no se reproduce ni antes ni despues,
decirlo: una memoria con un numero falso envenena todas las corridas siguientes. Ver tambien
[[project_falsos_verdes_la_platense]].
