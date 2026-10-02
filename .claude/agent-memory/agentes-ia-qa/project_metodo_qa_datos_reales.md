---
name: metodo-qa-datos-reales
description: El metodo que encuentra los defectos de verdad en las pantallas de reporte de este estudio (runner de consola de solo lectura contra produccion + SQL cruzado), y las trampas operativas de levantar la app en Windows.
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
