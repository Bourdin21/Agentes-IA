---
name: metodo-qa-datos-reales
description: El metodo que encuentra los defectos de verdad en este estudio (runner de solo lectura contra produccion + SQL cruzado + medicion de arneses por mutacion + verificacion de backfills de migracion por conteo de filas), las trampas de oraculo que publican partes falsos (regex posicional sobre HTML, criterios escritos como grep literal) y las trampas operativas de levantar la app, clonar el repo y mutar codigo en Windows.
metadata:
  type: project
---

Para validar una pantalla de reporte/metrica, los tres caminos se combinan siempre en este orden, y el segundo es el que encuentra los defectos:

1. **Runner de consola de solo lectura contra la base REAL de produccion.** Un `.csproj` que referencia `<Proyecto>.Infrastructure`, instancia el `AppDbContext` con la connection string de `appsettings.Production.json` y llama al Service directamente. No levanta la app web, asi que **ningun BackgroundService corre** — importante donde los hosted services escriben notificaciones al arrancar. Un `DbCommandInterceptor` de 15 lineas cronometra cada comando y da la evidencia de round-trips.
2. **Recalcular cada numero importante por SQL, por otro camino.** No alcanza con que el service de un numero: hay que llegar al mismo numero con una consulta independiente (y, para busquedas en memoria, con una implementacion distinta — lineal contra binaria). Los defentos de CR-79 y CR-80 aparecieron **todos** en esta comparacion, ninguno en la lectura de codigo.
3. **Pantallas por HTTP con `curl -k` + cookie jar** contra la base de desarrollo, nunca produccion: codigos de respuesta, HTML servido, estados vacios, panel de filtros, sesion y matriz de roles (login real por rol, no lectura del `[Authorize]`).

**Why:** los defectos de una pantalla de reporte no dan error, compilan y cada consulta por separado da bien. Solo se ven cuando el mismo numero se calcula dos veces por caminos distintos, o cuando se lo enfrenta con el numero de al lado. Y necesitan volumen e historia real: con la base de desarrollo no aparecen.

**How to apply:** en cualquier CR de reporte/KPI/dashboard, antes de escribir el informe. Ademas, probar **todas** las ventanas/rangos que ofrece la pantalla, no solo el default: en CR-80 la diferencia era 0 con 60 y 90 dias y aparecia solo con 180.

Trampas operativas (Windows, todos los proyectos del estudio):

- La app corriendo **bloquea** `<Proyecto>.Infrastructure.dll`: un `dotnet build` durante la corrida falla con MSB3027. Bajar el proceso (`Stop-Process -Name "<Proyecto>.Web" -Force`) antes de recompilar, y volver a levantarla si hacen falta mas pruebas HTTP.
- `Invoke-WebRequest` de PowerShell **no conecta a localhost** (proxy del sistema). Usar `curl -k` con `-c/-b` para la cookie de sesion.
- Para el login por `curl` hay que leer el `__RequestVerificationToken` del HTML de `/Account/Login` y postearlo junto a las credenciales.
- Heredoc de bash con contenido largo en castellano se rompe seguido: escribir el bloque con la herramienta Write a un archivo del scratchpad y despues `cat archivo >> destino`.
- Validar el YAML del catalogo con `python -c "import yaml; yaml.safe_load(...)"` despues de agregar items, y contar los ids para confirmar que entraron.

Para **re-verificar una validacion nueva** (un piso, un tope, un "esto no puede pasar"), hay un cuarto paso que el 2026-10-01 (lote D de eleven-la-plata) fue el unico que encontro el defecto:

4. **Contar en produccion cuantas filas reales violan la premisa de la validacion.** No probar solo que la regla rechaza lo que debe rechazar: preguntarle a los datos si lo que la regla declara imposible ya existe y es legitimo. En ELV-004 el fix asumia "ningun valor negativo es valido" y metia `RepuestoMaquina.Durabilidad` (vida util RESTANTE) en el piso en 0; un `select count(*) ... where Durabilidad<0` dio 350 de 1.314 repuestos en 90 maquinas, y el fix bloqueaba todo ajuste negativo en el 46% del parque. Los 11 criterios del brief pasaban; el defecto solo aparecio por ese conteo. La pista mas rapida de que la premisa es falsa suele estar en el propio dominio (ahi, `DurabilidadPorcentaje` ya devolvia 0 explicitamente para `Durabilidad <= 0`).

**Why:** una validacion se prueba facil contra los casos que el implementador imagino y es casi imposible de refutar leyendo el codigo; lo que la refuta es el parque de datos que ya existe.

**How to apply:** ante cualquier CA del tipo "X no puede ser negativo/mayor/menor", antes de dar PASS: identificar los campos que entran al calculo y contar en produccion las filas que ya estan del lado prohibido. Si hay alguna, el criterio esta mal especificado y vuelve al analista (BLOCKED), no solo el codigo.

Dos trampas operativas nuevas de la misma corrida:

- **El TempData viaja por cookie.** Para leer el mensaje "en pantalla" despues de un POST con `curl` hay que abrir el cookie jar con `-b` **y** `-c` en el POST y en el GET del redirect; con solo `-b` el `Set-Cookie` del `CookieTempDataProvider` se pierde y la pagina llega sin alerta. Se ve como "no hay mensaje" y parece un FAIL de CA.
- **La connection string se sobreescribe sin tocar el repo** con la variable de entorno `ConnectionStrings__DefaultConnection` al lanzar `dotnet bin/Debug/net10.0/<Proyecto>.Web.dll`. Es la forma de apuntar la app al clon respetando el read-only del repo del sistema.

**El MCP de Playwright puede no estar disponible en la sesion** (verificarlo buscando herramientas `mcp__playwright__*`). Cuando no esta: declararlo explicitamente en el informe, cubrir por HTTP todo lo que se pueda (status, HTML servido, roles, estados vacios) y dejar como procedimiento manual solo lo que exige un navegador de verdad — consola de JS limpia, breakpoints de ancho, interaccion de graficos, simular la caida de un endpoint. Nunca dar una verificacion por hecha sin decir por que camino se cubrio.

Para **re-verificar un fix** (no un feature nuevo), tres cosas que se aprendieron el 2026-10-01 (lote C de eleven-la-plata):

- **Leer el mensaje "en pantalla" despues de un 302 no se hace con `curl -L`:** al seguir el redirect vuelve a postear y da 405. Hay que hacer el POST con `-w "%{http_code} %{redirect_url}"` y despues un GET aparte a esa URL con la misma cookie jar. El TempData sobrevive un solo GET, asi que no se puede pedir la pagina dos veces.
- **El render JS se extrae del HTML servido, no del `.cshtml`.** Es la unica forma de probar un render de DataTables sin navegador y poder afirmar que lo que se probo es lo que el usuario recibe: regex sobre la respuesta HTTP para sacar el cuerpo del `render: function (data) {...}`, volcarlo a un `.js` y correrlo con `node` con los valores de borde (`null`, `0`, `''`, un valor real). Lo mismo sirve para verificar que `orderable: false` **se sirve**.
- **El criterio de re-verificacion que dejo la corrida anterior puede estar mal redactado, y hay que corregirlo en vez de marcar FAIL.** En ELV-005 el criterio pedia que `data[0].saldoAcumulado` igualara el saldo del encabezado; con el fix aplicado la primera fila anulada devuelve `null` a proposito, asi que el criterio era inverificable. La redaccion correcta nombra la fila **no anulada**. Al cerrar, reescribir el criterio en `6-qa.md` y decirlo en la traza.
- **Un fix de una instancia no cierra la clase.** ELV-006 se arreglo poniendo `orderable: false` en una columna, pero las otras cuatro de la misma grilla siguen clickeables sin ordenar. Al re-verificar, probar siempre **las columnas/casos hermanos** que el fix no toco y reportar el resto como item abierto.

Para **re-verificar el fix de un piso/tope** (lote E de eleven-la-plata, 2026-10-01), dos pasos que convierten un "anda" en un PASS defendible:

5. **Un fixture por campo del piso, elegido por SQL para que ese campo sea el minimo.** No alcanza con probar que el piso rechaza: hay que probar, campo por campo, **quien define el minimo**, porque el mensaje solo delata un numero. La query que los encuentra compara los `min()` de cada campo por maquina y filtra por el que queda mas abajo. Despues, en cada fixture: `-min-1` rechaza entero (snapshot identico) y `-min` se aplica dejando ese campo exactamente en 0. Asi se prueba la cobertura del piso, no su existencia.
6. **El conteo de produccion se repite en la direccion contraria.** En el lote D el conteo refuto la premisa; en el E confirma la del criterio nuevo: 0 filas negativas en los tres campos que quedaron en el piso. Y conviene medir **el alcance del fix**, no solo su correccion: de las 90 maquinas bloqueadas, 68 se destrabaron y 22 siguen en piso 0 por una causa distinta y legitima (un contador exactamente en 0). Ese numero es lo que separa "el fix esta bien" de "el fix resuelve el problema".

Dos cosas operativas mas de esa corrida:

- **Para loguearse en el clon sin conocer ninguna password:** generar un hash Identity v3 en Python (`pbkdf2_hmac('sha512', pwd, salt16, 100000, 32)`, prefijo `\x01` + `>I`:prf=2 + `>I`:iter + `>I`:saltlen + salt + subkey, en base64) y hacer un `update AspNetUsers set PasswordHash=... where UserName=...` **solo en el clon**. Elegir un usuario Administrador/SuperUsuario, no el Tecnico.
- **Un campo que se acumula por diferencias (`x += ultimo - anterior`) casi nunca tiene piso en 0.** Es la pista de codigo mas barata para decidir si un campo pertenece al piso; en eleven-la-plata `CambiarRepuesto` hacia exactamente eso con `Durabilidad`, y confirmaba que no era una lectura absoluta.

Para **medir un arnes por mutacion** (lo que separa "el arnes afirma" de "el arnes cubre"), tres cosas aprendidas el 2026-10-06 cerrando LP-039 en la-platense:

7. **Verificar que la mutacion se aplico, antes de concluir que sobrevivio.** Un mutante que nunca entro se lee EXACTAMENTE igual que un mutante que pasa: el arnes da verde en los dos casos. En esa corrida un `perl -0pi -e` multilinea no matcheo contra CRLF, M3 dio 59/0 y por un rato parecio un hueco real del arnes. El chequeo es una linea: `git diff --stat` (o `--stat` del mutante) despues de cada sed/perl, antes de compilar. En Windows, preferir `sed` sobre una sola linea a un regex multilinea.

8. **Mutar TODAS las afirmaciones nuevas, no solo las que mutó el implementador, y aceptar que algunas sean defensa en profundidad.** Una afirmacion que no muere con ningun mutante de la guarda nueva no es necesariamente vacia: puede estar cubriendo un invariante que tiene DOS guardas encima (en LP-039, "una venta totalmente facturada no se anula" solo murio cuando se saco la guarda nueva **y** el catch-all de estado). La conclusion que hay que escribir no es "vacia" ni "OK" sino **que mide**: esa afirmacion no mide el fix, mide el invariante.

9. **Lo que el arnes no siembra, no cubre — y las ramas de un mensaje cuentan.** El arnes de LP-039 solo ejercitaba la forma "interno #N" del mensaje porque con AFIP apagado ningun comprobante tiene numero: la rama con numero fiscal nunca corrio. Se cubrio seteando el campo por SQL en el fixture y re-posteando. Antes de dar PASS a un criterio de "el mensaje dice X", contar las ramas del `string.Join`/ternario en el codigo y verificar que haya una siembra por rama.

Trampa operativa (Windows): **`git clone` del repo falla con "Filename too long"** si el destino es el scratchpad (ruta profunda). Clonar a una ruta corta (`C:/qa039`) y con `-c core.longpaths=true`. Al cerrar, el `Remove-Item -Recurse` puede dejar un directorio colgado: el que lo tiene es un `dotnet` huerfano (build server) — `dotnet build-server shutdown` y, si no alcanza, `Stop-Process` del pid que `Get-Process dotnet` muestra.

Dos cosas mas, aprendidas el 2026-10-06 cerrando LP-040 en la-platense, que son las que encontraron el defecto de esa corrida:

10. **Contar las afirmaciones EVALUADAS en cada corrida de cada mutante, no solo las falladas.** Un mutante que mata 6 y un mutante que mata 18 pero deja 12 sin ejecutar se leen casi igual si solo se mira la lista de fallas. La verificacion es una suma: `OK + FALLADAS` tiene que dar el mismo total en la corrida limpia y en los N mutantes (en LP-040: 82 en las cinco). Si baja, el arnes murio o salteo, y lo que no se ejecuto no se midio. Corolario: **correr cada arnes DOS VECES SEGUIDAS sobre la misma base** — una limpieza incompleta se manifiesta recien en la segunda, y ahi el arnes puede terminar en 0 OK / 0 FALLADAS, que es indistinguible de "todo bien" para quien lee rapido.

11. **Un fix que cambia QUE FILAS escribe el sistema rompe los arneses de alrededor, y los arneses no estan en los `archivos_fix` de nadie.** En LP-040 el cambio fue "el camino legado ahora SI crea un `ComprobanteAfip` con la integracion apagada", y eso rompio dos cosas en un arnes hermano que el fix no toco: una limpieza que borraba la tabla padre asumiendo que la FK `RESTRICT` nunca se poblaba, y cuatro afirmaciones que median el contrato retirado. El implementador habia arreglado exactamente este patron en SU arnes y no lo barrio en los otros dos. **Al re-verificar: correr TODOS los arneses que toquen la entidad afectada, con control positivo en el commit anterior** (ver el aprendizaje de control positivo en la memoria del proyecto), y chequear si el defecto del instrumento tiene gemelo en produccion antes de ponerle severidad — aca `grep` de borrados fisicos en `Application`+`Infrastructure`+`Web` dio cero, el sistema usa soft delete, y el defecto quedo `minor` en vez de `major`.

Cuatro cosas mas, del 2026-10-06 cerrando LP-041 y LP-037 en la-platense. La primera casi hizo publicar un blocker inexistente:

12. **Cada arnes tiene su PROPIA copia de `<Proyecto>.Infrastructure.dll` en su `bin/`, y restaurar el fuente del mutante no la actualiza.** Despues de medir por mutacion, `git checkout` del fuente + `git status` limpio **no** garantizan que el arnes corra el codigo limpio: si se recompilo otro arnes y no ese, su `bin/` sigue con el DLL mutado. En esa corrida 10 corridas seguidas dieron la **firma exacta del defecto blocker** (`cierre=0,00` contra plata viva) sobre codigo que el `git status` reportaba limpio, y el instinto fue "el fix no cierra". La verificacion que lo atrapa es una linea: `md5sum <Proyecto>.Infrastructure/bin/Debug/net10.0/*.dll tools/*/bin/Debug/net10.0/<Proyecto>.Infrastructure.dll` — **los tres hashes tienen que ser identicos antes de declarar cualquier numero**. El tamaño del archivo NO sirve (los DLL mutados pesaban igual). Y recompilar explicitamente **cada** arnes que se va a correr, no solo el ultimo que se toco.

    Corolario: `dotnet build <solucion>.slnx` **no compila `tools/`** (los arneses no estan en la solucion). Hay que hacer `dotnet build tools/<Arnes>` uno por uno, y si no, `dotnet run --no-build` falla con "no se puede encontrar el archivo especificado" en vez de con algo que se entienda.

13. **Un mutante que mata MAS afirmaciones de las esperadas no es un hallazgo hasta que un segundo mutante, mas quirurgico, separa la medicion del efecto colateral.** Quitarle el ` FOR UPDATE` a un lock deja la sentencia como **lectura comun**, y en REPEATABLE READ la primera lectura comun de la transaccion **congela el read view**: el mutante rompe cosas que el lock no protegia. Ahi aparecieron 2 fallas extra con pinta de defecto nuevo (una venta `Confirmada` con 7 unidades y stock descontado 2). El mutante correcto es **no ejecutar la sentencia** (`return Task.CompletedTask`), que quita el lock sin tocar el snapshot: ahi fallan exactamente las 4 esperadas. Regla: para medir si un lock es load-bearing, el mutante es *saltear la sentencia*, no *debilitarla*.

14. **Para re-verificar un fix de reloj/huso, correr dentro de la ventana que rompia Y correr el arnes VIEJO ahi mismo.** Si el fix es "`UtcNow` -> dia de negocio", la ventana es 21:00-24:00 ART (`UtcNow.Date` ya es el dia siguiente). Que el arnes nuevo pase no prueba nada por si solo: puede ser que la ventana no estuviera activa. El control positivo es `git checkout <commit-anterior> -- tools/<Arnes>/Program.cs`, compilar y correr **en la misma hora**: tiene que reproducir el mensaje exacto del guard (`La fecha del movimiento no puede ser futura.`). Ojo al cerrar: `git checkout <commit> -- <archivo>` **deja el archivo en el INDEX**, asi que `git checkout -- <archivo>` lo "restaura" a la version vieja; hay que hacer `git reset HEAD -- <archivo>` y despues `git checkout HEAD -- <archivo>`.

15. **Archivar un `6-qa.md`/`trazabilidad.md` ANTES de escribir, con el techo bajado a mano:** `python scripts/archivar_memoria.py docs/<proyecto>/definiciones/6-qa.md --techo 120 --aplicar`. El script por defecto solo toca lo que ya paso 150 KB, asi que un archivo en 144 KB no entra y la entrada nueva lo revienta. El `--techo` va DESPUES de la ruta y el script igual imprime "120 NO EXISTE" al final (lo parsea tambien como ruta): es ruido, no un error.

Tres cosas mas, del 2026-10-07 cerrando el barrido de `Activo` en la-platense. La primera casi publico un parte `major` inexistente:

16. **Un parse de HTML con regex posicional no sirve como oraculo de un criterio.** El tag helper de ASP.NET emite `<option selected="selected" value="129">`: **`selected` va ANTES de `value`**. Un regex `<option value="(\d*)"([^>]*)>` no matchea esa option, asi que devuelve "AUSENTE" justo para la unica que importa — la del catalogo inactivo re-agregado. La firma del falso defecto es perfecta y asustadora ("el combo no trae el asignado, el navegador auto-selecciona la primera option y al guardar pisa la marca en silencio"). Lo que lo destapo fue **leer el codigo del Controller** y encontrar el re-agregado ya escrito, en vez de creerle a la medicion. El parser correcto saca los atributos primero y pregunta despues: `for om in re.finditer(r'<option\b([^>]*)>([^<]*)', sel)` y despues `re.search(r'value="([^"]*)"', at)` + `"selected" in at.lower()`.

    **Why:** una medicion negativa sobre HTML servido se siente como evidencia dura ("esta o no esta en la respuesta") y por eso no se la vuelve a cuestionar. Pero el oraculo no es el HTML, es el regex, y un regex que fija el orden de los atributos esta midiendo una convencion de serializacion y no el comportamiento.

    **How to apply:** antes de emitir un parte por algo que **falta** en una respuesta HTTP, confirmarlo por un segundo camino: grep del texto visible (`grep -c "ZZQA Marca Baja"`), conteo de options, y una lectura del codigo que lo produce. Si el codigo dice que deberia estar, el sospechoso es la medicion.

17. **Un `Sql()` en el `Up` de una migracion no se verifica leyendolo ni aplicandolo en desarrollo: se verifica contando, en el entorno donde se aplico, cuantas filas del tipo afectado habia.** Si el conteo es cero, el backfill **nunca corrio** y el PASS de esa migracion es estructuralmente imposible de obtener ahi (BLOCKED, no PASS). En la-platense las 4 migraciones con backfill corrieron contra `laplatense_dev`, que tiene 9 `CajaMovimientos` creados por un arnes **despues** de la migracion: los 6 `UPDATE` del ledger actuaron sobre 0 filas, mientras produccion tiene 5 ventas y 4 movimientos de caja reales. Dos agravantes que hay que buscar siempre: que el backfill **clasifique por `LIKE` sobre texto libre** con `ELSE NULL` (heuristica), y que una sentencia **dependa** del resultado de la anterior (si la primera deja NULL, la segunda no hace nada en silencio). Y revisar si el `Down` revierte el `UPDATE`: casi nunca lo hace, asi que el backup previo deja de ser precaucion y pasa a ser el unico rollback.

    Mecanica: separar `Up` de `Down` por archivo y contar operaciones **incluyendo los metodos genericos** — `migrationBuilder.AddColumn<int>(` **no** matchea `\.(\w+)\(`, hay que usar `\.(\w+)(?:<[^>]*>)?\(`. Sin eso una migracion con `AddColumn`/`Sql` se lee como "aditiva pura" y el informe anterior queda mal.

18. **Un criterio de re-verificacion escrito como grep de una frase literal se vuelve inverificable en cuanto el fix correcto consiste en CITAR esa frase para refutarla.** Paso con `LP-044`: el criterio pedia `grep "lo saca el parser"` = 0 lineas, y el fix correcto escribio *«esta linea decia "...lo saca el parser", que es LA MISMA AFIRMACION FALSA...»*. El grep da 1 y el fix esta bien. No es FAIL: es un criterio mal redactado, y se reescribe sobre el invariante — "cero hits que **afirmen**, en su propia voz y fuera de una cita que desmiente" — clasificando cada hit en *afirma* / *cita y refuta* / *otro sentido*. Corolario para el barrido de comentarios falsos: incluir las afirmaciones que el comentario hace **sobre si mismo o sobre el archivo** (`"aca no se repite"`, `"la unica fuente es X"`), porque son las que ningun chequeo mecanico levanta — no hay codigo al lado con el que confrontarlas — y son faciles de escribir con conviccion justo cuando se esta corrigiendo una afirmacion falsa anterior. En esa corrida `LP-051` era exactamente eso: el parrafo promete no repetir el mecanismo y lo repite dos lineas arriba.

Cuatro cosas mas, del 2026-10-07 cerrando la Entrega 5 lote 2 de la-platense (devoluciones). La primera y la segunda son del INSTRUMENTO, y la segunda casi dejo el informe sin su unica medicion:

19. **El chequeo de "el mutante entro al binario" tiene que seguir al PROYECTO del archivo mutado, no a un DLL fijo.** Una regla de dominio (`HabilitacionDeAccion`) compila en `<Proyecto>.Domain.dll`, no en `Infrastructure.dll`. Con el chequeo apuntado a Infrastructure, **los nueve mutantes de la regla se declararon "no entraron al binario" y no se midieron**. Falla-cerrado salvo el informe (se nego a medir en vez de reportar nueve falsos "sobrevive"), pero escrito como `warning` el informe habria dicho que ninguna condicion del defecto que se venia a cerrar tiene red. Y pasa igual cuando el codigo se MUEVE entre proyectos a mitad de un lote: la cota de IVA de `LP-053` se fue de `Infrastructure/Services/NotaCreditoService.cs` a `Domain/Reglas/CargoDeIvaDiferido.cs`, y el ancla del criterio de re-verificacion viejo dio **0 hits**.

    **How to apply:** mapear archivo -> assembly en el driver (`startswith("<Proyecto>.Domain")` -> `Domain.dll`) y listar los md5 de **los dos** DLL en la referencia limpia. Si un criterio de re-verificacion da 0 hits de su ancla, no es que el fix falte: buscar donde se mudo el codigo antes de concluir nada.

20. **Restaurar el fuente NO restaura el binario, y la LINEA BASE del driver siguiente lo paga.** Despues de una tanda de mutantes, un segundo driver midio su corrida limpia en **61/63** con el fuente en el md5 limpio y `git status` limpio — porque los `bin/` de los arneses seguian con el DLL del ultimo mutante. Es la memoria 12 un paso mas adelante: alla el problema era *entre* arneses, aca es *entre corridas del driver*.

    **How to apply:** el driver **reconstruye al restaurar** y hace `assert` de que el md5 del DLL volvio al valor limpio; y **aborta si su corrida limpia no da 0 falladas** antes de medir el primer mutante. Las dos cosas son una linea cada una y son lo unico que separa una tabla de mutacion publicable de una inventada.

21. **Un mutante que sobrevive puede ser una RAMA DOMINADA por aritmetica, y eso se decide con la cuenta, no con un fixture mas.** Dos sobrevivientes de esta corrida parecian huecos: la cota interna `Math.Min(proporcional, baseRemanente)` de un reparto, y una guarda `cantidadDevolvible <= 0`. Haciendo el algebra: `proporcional = Monto·(dev/total)` y `baseRemanente = Monto·(1 − devAnterior/total)`, y como `dev + devAnterior <= total`, **`proporcional <= baseRemanente` por construccion** — el `Min` interno solo puede morder por redondeo de centavos, y el `Min` final ya acota. La guarda, idem: el servicio deja la venta en `Anulada` siempre que se devuelve todo, asi que la rama `Anulada` se evalua antes y la otra es inalcanzable.

    **Why:** la tentacion es sembrar escenarios hasta que el mutante muera, y se pueden gastar tres fixtures en una rama que ninguna entrada puede alcanzar. El algebra lo decide en dos minutos y el veredicto es distinto: **no es "falta una afirmacion", es "falta declararlo en el codigo"**, y el parte no se emite.

    **How to apply:** ante un sobreviviente de una cota o de una guarda, escribir las dos expresiones que compara y preguntarse si una domina a la otra con las precondiciones del dominio. Si domina: declararlo, no medirlo. El tercer tipo de causa (ademas de "hueco real" y "rama dominada") es **"cubierto en otro arnes"**, y se distingue corriendo el MISMO mutante contra los demas arneses: un `SOBREVIVE` sin decir contra que arnes no alcanza para llamarlo hueco.

22. **Para probar que una afirmacion nueva mide LA RAZON y no el dato, hay que medirla por los DOS lados.** Un implementador puede declarar que un mutante sobrevive "por un segundo mecanismo" y no por una afirmacion vacia — y la declaracion es facil de escribir y dificil de refutar. La prueba es correr el mismo mutante contra los dos arneses: si **muere** en el que agrego la afirmacion de la razon y **sobrevive** en el que la condicion esta dominada por otra guarda, la distincion es legitima. **Si sobrevive en los dos, la afirmacion es relleno.** Las dos mediciones juntas son la evidencia; ninguna de las dos sola lo es.

Tres cosas del 2026-10-08, lote 1 de la-platense (datos/migraciones), verificando un hotfix que se habia corrido A MANO contra produccion:

23. **Para verificar una migracion aplicada a mano en produccion, se REPLICA el camino de produccion, no se lee el diff.** El ensayo que lo cierra: restaurar el backup pre-hotfix en una base descartable, correr el SQL extraido del ARCHIVO ACTUAL de la migracion, insertar su fila en `__EFMigrationsHistory` (igual que se hizo en prod), y despues `dotnet ef database update`. Despues, dos diffs: (a) el snapshot de indices+columnas generadas de la replica recien aplicada contra el de **produccion real** —si es identico, el archivo de hoy es lo que corrio alla, y nada se perdio cuando el commit siguiente le saco lineas—; y (b) el snapshot despues del deploy completo contra una base creada **desde cero**. En esa corrida los dos dieron identicos (67 y 119 hechos). Ninguna lectura del diff da esa conclusion: el archivo cambio DESPUES de que su fila entrara al historial, asi que el unico oraculo es el estado de la base.

24. **Una migracion ya marcada como aplicada invierte el ORDEN en que corre respecto de las pendientes, y eso es una asimetria que hay que chequear explicitamente.** En una base nueva el hotfix corre DESPUES de las 12 pendientes; en produccion ya corrio ANTES. Entonces hay dos preguntas distintas y las dos son mecanicas: (1) *que indice unico crea una pendiente que el hotfix ya no va a poder acotar* —se saca con un parser del `Up` de cada pendiente filtrando `unique: true`, y el que aparece tiene que estar cubierto por la segunda mitad del hotfix o ser una exclusion declarada; (2) *que pendiente toca una columna BASE de una columna generada que en produccion ya existe* —un `AlterColumn`/`DropColumn`/`RenameColumn` ahi hace fallar el deploy solo en produccion, nunca en una base nueva. Las dos se responden con un script de 20 lineas sobre los archivos de migracion y valen mas que cualquier lectura.

25. **El control positivo de un fix de esquema es el `Down`.** Para afirmar que una barrida de N casos mide algo, correrla sobre la base con el `Down` aplicado: en esa corrida dio **0/16 con la firma exacta del defecto** (`Duplicate entry ... for key 'productos.IX_Productos_CodigoBarras'` en el insert de reuso) contra 16/16 con el fix. Y el `Down` es gratis de obtener: `dotnet ef database update <la migracion anterior>`. Sirve igual a nivel app — con el `Down` el mismo POST da **500 con `DbUpdateException`** y con el fix da **302**; ese par es lo que convierte un "reproducido y resuelto" en evidencia. Ojo que el `Down` puede fallar si durante la corrida ya se reuso un valor (el `ADD UNIQUE INDEX` global choca): para el control positivo a nivel app conviene un fixture aparte donde se revierte **un solo** indice a mano.

Cinco cosas del 2026-10-09, re-verificando la fase 1 del token de submit en la-platense. La primera
convierte "el MCP de Playwright no esta" en una prueba de navegador de verdad:

26. **Sin el MCP de Playwright, `playwright` de Python + el Chromium ya bajado alcanzan para cubrir
    un criterio que EXIGE navegador.** Verificar con `python -c "import playwright"` y
    `ls ~/AppData/Local/ms-playwright`. Con eso se prueba el SweetAlert2 real, el doble clic real y
    la consola de JS. Declarar que el MCP no estaba y por que camino se cubrio, pero **no bajar el
    criterio a "manual" sin mirar si el paquete esta instalado**.

27. **Un `fetch` con `redirect:'follow'` CONSUME el TempData, asi que el cartel llega vacio y se lee
    como "la pantalla no dice nada".** Me costo tres intentos. Dos reglas: (a) el POST que tiene que
    dejar un cartel se hace por NAVEGACION REAL —armar un `<form>` en el DOM con los pares del
    `FormData` original y `submit()`, dentro de `expect_navigation`—; (b) el oraculo del mensaje no
    es el toast renderizado (depende del timing) sino el bloque `Swal.fire({icon:'...',text:'...'})`
    que el `_Layout` emite desde TempData, leido del **HTML servido** con un regex que corta en
    `confirmButtonColor`. Ahi se lee tambien el ICONO, que es lo que distingue un replay de exito de
    un rechazo.

    Corolario del par discriminante: para probar "con el mismo token no emite y con otro si", los
    dos POST tienen que llevar **los mismos bytes de negocio**. Tomar el `FormData` del form dos
    veces NO los da iguales: entre los dos renders cambia `YaFacturada` (y el antiforgery). Hay que
    guardar UNA lista de pares y reemplazar **solo** el token.

28. **El perimetro de "POST que escriben plata" se enumera por TIPOS DECLARADOS, no por nombres.**
    Mi primera pasada resolvia `_foo.Bar()` emparejando prefijos de `_foo` con `IFooService` y dio
    **11 sitios, sin incluir el unico que estaba cubierto**. Leyendo las declaraciones
    (`private readonly IFooService _foo;`) y mapeando `IFoo`->`Foo` dio **28**. Es el mismo error que
    le costo dos correcciones al verificador del implementador (10 y despues 23). Y la deteccion de
    escritura tiene que cubrir `new <Entidad>`, `.Add/.AddRange`, SQL crudo **y** la mutacion de una
    propiedad monetaria sobre una variable de tipo entidad: con solo `new X` se pierden los cierres
    de caja, que es exactamente el agujero que encontre (`LP-127`).

29. **Un verificador de analisis ESTATICO es inmune a la trampa del `copy2`/mtime, porque no hay DLL
    en el circuito.** Pero tiene su propia trampa: **el mutante tiene que respetar la convencion de
    nombres del repo**. Mi primer mutante inyectaba `IQaMutante` con clase `QaMutanteService`, el
    verificador no pudo resolver `IQaMutante`->`QaMutante` y el POST nuevo quedo invisible: estuve a
    un paso de publicar que el verificador no detecta el olvido ni en el caso facil. Con el nombre
    corregido lo detecta y sale 1. Antes de acusar al instrumento, chequear si el mutante entra por
    la puerta que el instrumento mira — y despues medir si ALGUN caso real rompe esa convencion
    (ahi dio 0, asi que no era un hueco).

30. **Copiar el arbol con `tar` deja 13 GB por `Migracion/`, y casi nunca hace falta el arbol.**
    Un verificador que busca la raiz subiendo hasta el `.slnx` se conforma con una copia de
    **3,5 MB**: el `.slnx`, `Web/Controllers`, `Infrastructure/Services`, `Views/_ViewImports.cshtml`,
    el Razor generado y el `bin/` del propio verificador (hay que copiarlo, si no sube hasta la raiz
    REAL y mide el repo del cliente en vez de la copia). Ojo que `Remove-Item` de PowerShell se niega
    a borrar rutas tipo `C:\qatok` ("protected from removal"): el que funciona es
    `cmd //c "rmdir /s /q C:\ruta"` desde bash.
