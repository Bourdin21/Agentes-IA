---
name: verificacion-vistas-razor
description: Como verificar una vista Razor sin levantar la app (node --check sobre el JS embebido) y la trampa del object initializer en atributos de tag helper.
metadata:
  type: project
---

En proyectos donde no se hace smoke test propio (marihogar y cualquier otro con esa regla), el build
es el unico gate automatizado — y **el compilador de Razor no valida el JavaScript embebido**. Una
vista puede compilar con 0 errores y estar rota en pantalla.

**Como aplicar:** al cerrar una vista con JS no trivial (graficos, fetch por card, DataTables),
extraer los bloques `<script>` a un archivo temporal, neutralizar las expresiones Razor
(`@Url.Action(...)` y `@Model.X` a un literal) y correr `node --check archivo.js`. Node esta
disponible en la maquina. Contar llaves/parentesis a mano no sirve: los comentarios en castellano
con "(s)" y los apostrofes desbalancean cualquier heuristica.

**Trampa de Razor, cuesta un ciclo de build entero:** un object initializer dentro de un atributo de
tag helper **no parsea** — `<partial name="_X" model="new MiVm { A = 1 }" />` tira una cascada de
CS1525/CS1003 en el `.g.cs` generado, con el error apuntando a la linea del `<partial>`. Se arma la
instancia en el bloque `@{ }` de arriba y el atributo recibe solo la variable.

**Por que:** las dos cosas se descubren recien al compilar o al abrir el navegador, y la segunda deja
20 errores ilegibles que parecen un problema del ViewModel y no de la sintaxis del atributo.

**El extractor se valida con un GRUPO DE CONTROL, no con buena fe.** Incluir en la corrida una
vista PREEXISTENTE y en produccion junto a las nuevas. Si el script marca FALLA en esa, el defecto
es del script. Paso tal cual en la-platense Entrega 6: dos vistas dieron FALLA y la pista fue que
una era `Ventas/Editar.cshtml`, que corre en produccion desde agosto — el regex que borraba
`@if (...) {` dejaba la llave de cierre huerfana. Sin el control, el camino natural era "arreglar"
una vista que estaba bien. El fix es sustituir el `@if` por `if (true) {` en vez de borrarlo, para
que las llaves queden balanceadas.

**Otra trampa de Razor de la misma familia que la del object initializer:** texto plano suelto
despues de un `<br />` dentro de un bloque `@if { }` hace que Razor cambie a modo codigo y tire
~30 errores CS sobre palabras en castellano ("el nombre del tipo 'si' no se encontro"). El
contenido va envuelto en un tag (`<div>`), nunca suelto.

**Un partial de Razor NO puede definir `@section Scripts`.** El bloque simplemente **no se
renderiza**: compila sin error, la pagina carga, y el JS nunca se ejecuta — el peor modo de falla
posible, porque no hay nada que mirar. Si dos vistas tienen que compartir una grilla con su JS (el
caso tipico: la misma pantalla con permisos distintos), el reparto es **markup en el partial y JS en
un `.js` de `wwwroot`**, parametrizado por un objeto de config que cada vista define en su propio
`@section Scripts` antes de incluirlo:

```
window.MiGridConfig = { urlListar: '@Url.Action(...)', usuarioId: null, esAdmin: false };
<script src="~/js/mi-grid.js" asp-append-version="true"></script>
```

Beneficio colateral que vale por si solo: el `.js` externo pasa `node --check` de verdad, sin
extractor ni neutralizacion de expresiones Razor.

**Y la razon para compartirlo, no solo la mecanica:** cuando dos pantallas se diferencian por
SEGURIDAD y no por presentacion, dos copias del markup son dos oportunidades de que eso deje de ser
cierto — en seis meses una muestra el importe con dos decimales y la otra con cero, o una filtra por
una columna y la otra no. Es LP-002 aplicado al front.

Ver tambien [[git-crlf-repos-dotnet]].
