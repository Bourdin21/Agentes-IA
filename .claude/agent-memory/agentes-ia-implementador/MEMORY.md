# Memoria de agentes-ia-implementador

Rol: implementacion .NET (ASP.NET Core MVC + EF Core + MySQL).

Como usar este archivo (limite duro: 200 lineas o 25KB — lo que llegue antes; si se pasa, comprimir):

- Aca van SOLO aprendizajes reutilizables entre corridas: trampas del repo, comandos que funcionan, decisiones que se repiten.
- El estado de cada proyecto NO va aca: vive en `docs/<proyecto>/definiciones/` y `docs/<proyecto>/trazabilidad.md` (fuente de verdad, compartida con los demas agentes).
- Las reglas cross-proyecto tampoco: viven en `.github/instructions/32-estandares-qa-implementador.instructions.md` y `docs/qa/regresiones-manuales.yml`.
- Si un aprendizaje sirve para otros agentes, escribilo en el catalogo cross-proyecto, no solo aca.

## Aprendizajes

- [Verificar una vista Razor sin levantar la app](verificacion-vistas-razor.md) — `node --check` sobre el JS embebido, y el object initializer que no parsea en un atributo de tag helper.
- [Verificar los criterios con numero exacto contra produccion](verificar-criterios-contra-produccion.md) — consulta de solo lectura antes de cerrar la etapa; destapa el agregado mal contado que QA devolveria.
- [Coleccion local de strings hacia SQL = MH-001](coleccion-local-de-strings-hacia-sql.md) — el gatillo no es el refactor: es cualquier `Contains` de strings que se traduzca a SQL, y deja el endpoint en 500.
- [Line endings MIXTOS y el warning CRLF](git-crlf-repos-dotnet.md) - archivo por archivo: un parche por anclas tiene que detectar el EOL, y un script por heredoc no decodea UTF-8.
- [Un arnes que muere en vez de medir](arnes-que-muere-en-vez-de-medir.md) - indexar sin guard hace que el mutante parezca matar 6 cuando mata 18.
- [Reuse total = la estructura, no la aritmetica](reuse-estructura-no-aritmetica.md) — que preguntar campo por campo antes de copiar un modulo de otro proyecto, y cuando el precedente se puede simplificar.
- [La entidad del precedente que ya tengo con otro nombre](entidad-del-precedente-que-ya-tengo.md) — preguntar que ROL cumple alla antes de crearla; si ya esta ocupado, construirla deja dos libros del mismo dinero.
- [Un agregado que tres filas basura pueden secuestrar](agregado-secuestrado-por-outliers.md) — sobre datos migrados, el numero con el que el usuario decide tiene que ser un conteo.
- [Desviarse de un port "literal" que el brief ordena](desvio-de-un-port-literal.md) — medir el radio de impacto primero; el catalogo puede tener el contra-criterio escrito.
- [Sonda EF desechable en el scratchpad](sonda-ef-desechable.md) — ejecutar de verdad una consulta LINQ nueva, medir un backfill y probar CONCURRENCIA (N scopes = N conexiones + barrera) sin levantar la app.
- [Un mutante del importe contra el eco de UI](mutante-del-importe-y-el-eco-de-ui.md) — mide una cascada y deja NO MEDIDA la afirmacion que importa; y como se DISENA el fixture para que el numero correcto y el incorrecto difieran.
- [La forma de baja puede ser INVERSA entre dos familias](forma-de-baja-inversa-entre-familias.md) — "fila vieja vs fila nueva" no predice nada: preguntar que hecho devuelve la CAPACIDAD de repetir la operacion.
- [Un mutante vivo en el binario con el md5 en OK](mutante-vivo-en-el-binario-con-md5-ok.md) — `copy2` preserva el mtime, MSBuild no recompila y el control de integridad recomendado no lo atrapa.
- [Renumerar vuelve inauditable la retirada](renumerar-vuelve-inauditable-la-retirada.md) — los mismos ids en dos versiones con sentidos distintos; y como revisar que una retirada no se lleve otra cobertura.
- [Un verificador de perimetro se calibra con lo que ya sabemos que falta](verificador-de-perimetro-y-su-calibracion.md) — si no ve los sitios que ya tienen parte de defecto, no sirve para los que nadie encontro.
- [El escenario de idempotencia pide MEDIA linea](escenario-de-idempotencia-media-linea.md) — con la linea entera el tope ataja el duplicado y la afirmacion pasa sobre el codigo roto; y la guarda nueva invalida los escenarios que median el tope.
