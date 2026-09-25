---
name: git-crlf-repos-dotnet
description: El warning "LF will be replaced by CRLF" de git en los repos .NET del estudio es normal y no indica que se haya reescrito el archivo.
metadata:
  type: project
---

Los repos .NET del estudio tienen la copia de trabajo en **LF** y `core.autocrlf=true`, asi que
`git status`/`git diff` imprimen `warning: LF will be replaced by CRLF` por **cada** archivo tocado.
No significa que la edicion haya normalizado los saltos de linea ni que el diff vaya a salir entero.

**Como aplicar:** ignorar el warning. Si hace falta confirmar que un diff es quirurgico y no una
reescritura de line endings, mirar `git diff --stat` (la cantidad de lineas cambiadas tiene que
parecerse a lo que se edito) en vez de asumir por el warning. Al escribir un archivo con un script
de Python, usar `newline=''` para no introducir CRLF donde el resto del repo tiene LF.

Ver tambien [[verificacion-vistas-razor]].
