---
name: verificar-vistas-razor
description: Cómo verificar errores de Razor en las vistas .cshtml de delicias-naturales (no se compilan en el build normal)
metadata: 
  node_type: memory
  type: reference
  originSessionId: be0c6204-2b83-412a-abdc-5cf1f307358b
  modified: 2026-08-01T02:16:28.008Z
---

En el proyecto `delicias-naturales` (ASP.NET MVC5 / .NET Framework), `MvcBuildViews` está en `false` (ver DeliciasNaturales.csproj), así que el build normal **no** detecta errores de Razor en `.cshtml` — fallan recién en runtime.

Para validar las vistas en tiempo de build:
```
msbuild DeliciasNaturales.csproj /t:Build /p:Configuration=Debug /p:MvcBuildViews=true
```
MSBuild path típico: `C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe`

**Gotcha:** si falla con `error ASPCONFIG: ... allowDefinition='MachineToApplication' beyond application level` apuntando a `obj\...\AspnetCompileMerge\source\web.config`, es un falso positivo por una carpeta obsoleta de un publish previo. Borrar `obj\*\AspnetCompileMerge` y reintentar. Tras limpiarla, la precompilación da EXITCODE 0.

**Gotcha (Git Bash):** `/t:Build /p:X=Y` se corrompe por la conversión de rutas de MSYS. Prefijar el comando con `MSYS2_ARG_CONV_EXCL="*"`.

**Gotcha (sintaxis Razor, dos bugs reales encontrados en Pedidos/Details.cshtml):**
1. El compilador de vistas (CodeDom, no Roslyn) **no soporta `?.`** (null-conditional operator, C#6+) en un .cshtml — ni dentro de bloques `@{ }` ni dentro de expresiones explícitas `@(...)` embebidas en un atributo HTML (p.ej. `data-x="@((Model.Cliente?.Saldo ?? 0).ToString(...))"`), aunque el mismo operador sí compila sin problema en archivos .cs del proyecto. Da `error CS1525: Invalid expression term '.'`. Hay que precomputar el valor en una variable dentro de un bloque `@{ }` usando `Model.X != null ? Model.X.Y : default` (ternario, sin `?.`/`??`), y después referenciar esa variable simple en el atributo.
2. Un `if` anidado **dentro de un bloque de código ya abierto** (p.ej. dentro del `{ }` de un `@if` exterior, después de markup HTML) **no lleva `@`** — ya estás en contexto de código. Escribir `@if` ahí da `error ASPPARSE: Unexpected "if" keyword after "@" character`. Patrón correcto confirmado en `Views/Productos/Index.cshtml:224-226` (`@if (...) { if (...) { ... } }`). El `@` solo se necesita para la PRIMERA transición markup→código, no para ifs subsiguientes ya dentro del mismo bloque.

**Gotcha grave (runtime, no se detecta en build ni con MvcBuildViews): múltiples `.Include()` de colecciones en una sola query EF6 + MySql.Data.EntityFramework rompen la materialización.**
Si una query de EF hace `.Include()` de 2+ colecciones distintas (p.ej. `Venta.ProductosVenta` + `Venta.Facturas` + `Pedido.Detalles` todas en la misma query), MySQL genera un join cartesiano y el conector (`MySql.Data.EntityFramework`) desalinea columnas al materializar, tirando `System.FormatException: String was not recognized as a valid Boolean` (stack trace pasa por `MySql.Data.EntityFramework.EFMySqlDataReader.GetValue` / `Convert.ChangeType`). El error NO aparece en compilación, solo en runtime al ejecutar esa query puntual — hay que probar la pantalla en el navegador o revisar el mail de error (`SiEnviarMailErrores=true` en producción, manda a `olvidatasoft@gmail.com` via `NotificacionesHelper.EnviarCorreoError`, buscar en Gmail `subject:ERROR` + nombre del controller/parse).
**Fix:** no agregar una tercera colección Include al mismo query. Cargar esa colección aparte con una query simple después (`db.Facturas.Where(f => f.VentaId == x).ToList()`), no vía `.Include()` anidado.
**Caso real:** `PedidosController.Details` — agregar `.Include(x => x.Venta.Facturas)` junto a los Includes ya existentes de `Venta.ProductosVenta` y `Detalles` rompió `/Pedidos/Details/{id}` en producción (2026-07-22). Se resolvió sacando el Include y cargando `pedido.Venta.Facturas` con una query separada.

**Gotcha (autorización): `[Authorize]` de clase + `[Authorize]` de acción con roles distintos se combinan con AND, no se amplían.** En ASP.NET MVC5 clásico (no Core), si un controller tiene `[Authorize(Roles="Administrador,Vendedor")]` a nivel de clase y una acción puntual tiene `[Authorize(Roles="Administrador,Vendedor,Cliente")]`, un usuario Cliente sigue sin poder entrar: ambos filtros se evalúan y TIENEN que pasar los dos (no es una unión de roles). El rol agregado a nivel de acción es ilusorio si la clase no lo tiene. **Fix:** sacar el `[Authorize]` de la clase y ponerlo explícito en cada acción individualmente. Ya pasó dos veces en este proyecto: `FacturasController` (para permitir a Cliente `Descargar`) y `VentasController` (para permitir a Cliente `DescargarComprobante`, usado desde los botones de Pedidos/Details y `_VentaCompletaPartial`). Antes de asumir que "ya tiene `[Authorize(Roles=...,Cliente)]` en la acción, debería andar", verificar si el controller tiene un `[Authorize]` de clase más restrictivo por encima.
