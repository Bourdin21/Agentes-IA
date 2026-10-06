---
name: build-razor-incremental
description: En La Platense, "0 errores" de un build incremental NO acredita que las vistas Razor compilen — hay que forzar --no-incremental
metadata:
  type: feedback
---

Un `dotnet build` incremental puede devolver **0 errores sin haber recompilado las vistas `.cshtml`**.
La evidencia de cierre "build limpio" queda falsa justo para la capa que más se acaba de tocar.

**Why:** medido el 2026-10-06 en la corrida de CR-01/CR-02. Tras escribir una vista nueva y editar
tres, el build daba 0 errores; el volcado de archivos generados del source generator de Razor
(`obj/Debug/net10.0/generated/.../Views/`) tenía fecha del **5-Oct** y no incluía la carpeta de la
vista nueva. El proyecto **no** usa `AddRazorRuntimeCompilation`, así que un error de Razor es un
error de build: el riesgo de dar por bueno un build que no las miró es real, no teórico.

**How to apply:** al cerrar una etapa que tocó vistas, correr
`dotnet build FerreteriaLaPlatense.Web --no-incremental`. Y si hace falta acreditarlo de verdad,
**comprobar que el mecanismo funciona**: agregar una línea deliberadamente inválida a la vista nueva
(`@Model.PropiedadQueNoExiste`), confirmar que el build falla señalando ese archivo y esa línea, y
restaurar. Es la única forma de distinguir "las vistas compilan" de "las vistas no se compilaron".

Ese directorio `generated/` es un volcado que no se refresca solo: **no sirve como evidencia de
nada**, ni de que algo se compiló ni de que no.
