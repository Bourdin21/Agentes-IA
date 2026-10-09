---
name: git-crlf-repos-dotnet
description: Los repos .NET del estudio tienen line endings MIXTOS archivo por archivo; el warning CRLF de git es normal, y un parche por anclas de texto tiene que detectar el EOL de cada archivo.
metadata:
  type: project
---

Los repos .NET del estudio tienen `core.autocrlf=true`, asi que `git status`/`git diff` imprimen
`warning: LF will be replaced by CRLF` por **cada** archivo tocado. No significa que la edicion haya
normalizado los saltos de linea ni que el diff vaya a salir entero.

**Pero la copia de trabajo NO es uniformemente LF: es MIXTA, archivo por archivo.** Medido en
la-platense (LP-040): `FerreteriaLaPlatense.Infrastructure/Services/VentaWorkflowService.cs` esta en
**LF** mientras `VentaDtos.cs`, `VentasController.cs`, `Details.cshtml` y los dos archivos de
`Interfaces/` estan en **CRLF**, en el mismo commit y el mismo proyecto.

**Como aplicar:** ignorar el warning. Si hace falta confirmar que un diff es quirurgico y no una
reescritura de line endings, mirar `git diff --stat`.

Y sobre todo: **un parche programatico por anclas de texto multilinea tiene que detectar el EOL del
archivo que abre** (`e = '\r\n' if '\r\n' in s else '\n'`, y reemplazar `\n` por `e` en el ancla y en
el reemplazo antes de buscar). Asumir LF porque el archivo anterior era LF da `substring not found` o
`assert count == 1` fallado, y se parece a un ancla mal copiada cuando es otra cosa. Escribir siempre
con `newline=''` para no introducir CRLF donde el archivo tiene LF.

**Trampa hermana, misma sesion:** un script de Python pasado por **heredoc** a la Bash tool se decodea
con la codificacion del locale, no UTF-8, asi que un ancla que contenga `—`, acentos o comillas
tipograficas **no matchea** el archivo leido como UTF-8 — y el sintoma es, otra vez, un assert de
"ancla 0 veces". La salida: escribir el script a un `.py` con la herramienta Write (que lo deja en
UTF-8, y Python lee los `.py` como UTF-8 por PEP 263) y correrlo con `python archivo.py`, en vez de
`python - <<'PY'`. Ojo tambien con el doble escapado: un `\"` del codigo C# necesita `\\"` en el
literal de Python, y si ese literal se escribe desde OTRO script hacen falta cuatro barras — mas facil
es usar un literal crudo (`r"""..."""`).

Ver tambien [[verificacion-vistas-razor]] y [[arnes-que-muere-en-vez-de-medir]].
