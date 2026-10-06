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
- [El warning CRLF de git es normal](git-crlf-repos-dotnet.md) — copia de trabajo en LF + `autocrlf=true`: no indica que se haya reescrito el archivo.
- [Reuse total = la estructura, no la aritmetica](reuse-estructura-no-aritmetica.md) — que preguntar campo por campo antes de copiar un modulo de otro proyecto, y cuando el precedente se puede simplificar.
- [La entidad del precedente que ya tengo con otro nombre](entidad-del-precedente-que-ya-tengo.md) — preguntar que ROL cumple alla antes de crearla; si ya esta ocupado, construirla deja dos libros del mismo dinero.
- [Un agregado que tres filas basura pueden secuestrar](agregado-secuestrado-por-outliers.md) — sobre datos migrados, el numero con el que el usuario decide tiene que ser un conteo.
- [Desviarse de un port "literal" que el brief ordena](desvio-de-un-port-literal.md) — medir el radio de impacto primero; el catalogo puede tener el contra-criterio escrito.
- [Sonda EF desechable en el scratchpad](sonda-ef-desechable.md) — ejecutar de verdad una consulta LINQ nueva, medir un backfill y probar CONCURRENCIA (N scopes = N conexiones + barrera) sin levantar la app.
