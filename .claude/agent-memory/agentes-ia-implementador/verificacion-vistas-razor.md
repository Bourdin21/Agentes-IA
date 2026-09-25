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

Ver tambien [[git-crlf-repos-dotnet]].
