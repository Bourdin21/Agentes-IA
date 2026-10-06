---
name: sonda-ef-desechable
description: Como ejecutar de verdad una consulta LINQ nueva (lo que MH-001 exige) sin levantar la app ni violar la prohibicion de smoke test funcional - proyecto consola en el scratchpad
metadata:
  type: feedback
---

Para probar una consulta LINQ nueva, armar un **proyecto consola desechable en el scratchpad** (nunca en el repo) que referencie el `.csproj` de Infrastructure, correrlo contra la base de **dev**, y borrarlo al terminar.

**Why:** `MH-001` pide explicitamente *"si una consulta filtra por coleccion, probala ejecutandola"*, y la regla aclara que el bug "compila, pasa code review y falla SOLO en runtime contra MySQL". Pero el rol del implementador prohibe levantar la app y probar flujos por navegador o HTTP. La sonda resuelve las dos cosas: ejecuta SQL real contra EF (que es la evidencia tecnica que la regla pide) sin ser una prueba funcional de la aplicacion. Un build limpio **no** cubre este riesgo, que es justamente por lo que MH-001 es el patron mas reincidente del catalogo.

**How to apply:** cuando una corrida agrega consultas con shapes que el compilador no valida — `GroupBy` con clave anonima o con enum **nullable**, `Contains`/`Any` sobre coleccion local, `StartsWith`/`EndsWith` (ver [[coleccion-local-de-strings-hacia-sql]]), o cualquier proyeccion nueva sobre columnas recien agregadas. Tambien sirve para **medir un backfill** en vez de darlo por bueno porque el `UPDATE` no tiro error: imprimir las filas afectadas y los netos resultantes destapa un backfill que corrio pero dejo el dato mal.

Gotchas que costaron tiempo:

- **El provider importa y no se adivina:** mirar la llamada real en `Infrastructure/DependencyInjection.cs` antes de escribir el `DbContextOptionsBuilder`. La Platense usa `MySql.EntityFrameworkCore` → `.UseMySQL(cs)` (S mayuscula, sin `ServerVersion`). Pomelo seria `.UseMySql(cs, ServerVersion.AutoDetect(cs))`. Escribir la de Pomelo por reflejo da `CS0103: ServerVersion no existe` + `CS1061: no contiene UseMySql`.
- El `.csproj` de la sonda referencia Infrastructure por **ruta absoluta**; no hace falta tocar la solucion ni el `.slnx`.
- Hardcodear la cadena de conexion de **dev** en el `Program.cs` de la sonda, nunca leer `appsettings` ni aceptar un parametro: una sonda que puede apuntar a produccion por descuido no vale el riesgo (ver [[verificar-criterios-contra-produccion]], que es la contraparte de solo-lectura cuando hay que mirar produccion a proposito).
- **Predicado reutilizable para un `Where` traducido: `Expression<Func<T,bool>>`, NUNCA un metodo
  `static bool`.** El metodo compila igual y revienta en RUNTIME contra MySQL ("could not be
  translated"), exactamente como un metodo de instancia de la entidad — que es la razon por la que
  esas reglas suelen estar escritas inline y duplicadas en el repo. Con una Expression se escribe
  una vez y se puede negar con `Expression.Not(e.Body)` sin duplicar la condicion. Dos shapes mas
  que EF no garantiza traducir y que conviene no escribir de entrada: proyectar a `ValueTuple` y
  agregar con `GroupBy(_ => 1)` (dos `SumAsync` sobre la misma query filtrada son mas baratos que
  el reintento).
- **Si la sonda ESCRIBE sobre una tabla grande, respaldarla con `mysqldump` ANTES y restaurarla
  despues**, y dejar en el reporte que la base quedo en su linea base exacta (contar filas al
  final). Una corrida de aumento masivo sobre 112.485 productos deja dev irreconocible para la
  proxima sonda y para QA; el dump de la tabla tarda segundos y vale el paso.
- **Si hace falta ejercitar un CONTROLLER y no solo un Service, el `.csproj` de la sonda va con
  `Sdk="Microsoft.NET.Sdk.Web"`** (mas `<OutputType>Exe</OutputType>`) y referencia el proyecto Web.
  Con `Microsoft.NET.Sdk` no estan los tipos de ASP.NET Core y no compila. Se instancia el controller
  a mano con un `DefaultHttpContext`, un `ClaimsPrincipal` armado con los claims que importan, y una
  **`ISession` falsa en memoria** (10 lineas) si el controller usa `FiltrosSessionHelper`. Es la
  UNICA forma de probar de verdad un control de **scoping por identidad** (PAT-017 / IDOR): el
  Service recibe un id, asi que lo que hay que verificar es que el controller nunca le pase el de la
  request. Probar el Service solo no prueba nada. La prueba que vale: claim de un usuario + id de
  OTRO inyectado en el form por varias vias a la vez, y afirmar que las filas devueltas son las del
  claim — con dos cuentas de saldos distinguibles, para que no sea vacia.
- **La linea base se calcula con SQL crudo, no con el codigo bajo prueba.** Si el "saldo esperado"
  sale del mismo LINQ que se esta probando, la sonda compara el codigo consigo mismo y pasa siempre.
  Abrir la conexion del `DbContext` y correr un `SELECT SUM(...)` a mano al principio.
- **Cuando la sonda audita datos EXISTENTES, esperar que falle por datos y no por codigo.** Una
  pantalla nueva que contrasta totales congelados contra un recalculo va a destapar inconsistencias
  historicas de antes del fix que las cerro. Antes de reportarlas como defecto propio: verificar la
  causa por SQL (comparar `CreatedAt` de la fila contra la fecha de la firma del cierre, por
  ejemplo) y decidir si es residuo o bug. En la-platense Entrega 4, 2 de ~45 verificaciones fallaron
  y las dos eran la misma fila cargada cuatro dias despues de que el mes estuviera cerrado — residuo
  del defecto que LP-009 ya habia cerrado. Que la sonda lo encuentre es la feature, no el problema;
  lo que hay que escribir en el reporte es el corolario accionable: **produccion corrio el mismo
  codigo viejo, asi que puede tener el mismo residuo**.
- **Para probar CONCURRENCIA, la sonda sirve y es la unica forma que tengo** (el rol me prohibe HTTP, y
  una prueba secuencial da **falso verde**: con un cliente compartido las sentencias se serializan
  solas). Receta: `services.AddInfrastructure(config)` + **N scopes de DI independientes** (cada scope
  = su propio `AppDbContext` = su propia conexion a MySQL, que es el equivalente de los "sockets
  separados"), **abrir las N conexiones ANTES de la barrera** (si no, se mide el costo de conectarse y
  no la carrera), soltarlas juntas con un `TaskCompletionSource`, y **contar FILAS en la base**, no
  respuestas. Probar con N=3 y N=8. Dos dependencias que `AddInfrastructure` no trae y hacen fallar la
  resolucion: `IWebHostEnvironment` (lo pide `AfipService`; stub de 10 lineas con `NullFileProvider`) y
  `UserManager<ApplicationUser>` (lo pide el servicio de avisos; `AddIdentityCore<ApplicationUser>()
  .AddRoles<IdentityRole>().AddEntityFrameworkStores<AppDbContext>()`).
- **Si la sonda ESCRIBE mucho, no respaldar dev: clonarla.** `mysqldump` de dev a una base nueva
  (`laplatense_probe_*`), apuntar la sonda ahi y dropearla al final. Mas barato y mas seguro que
  dump+restore de dev, y deja dev verificablemente intacto (contar filas al cerrar). **Ojo con los
  clones que dejo QA** (`laplatense_qa_*`): son fixtures de re-verificacion, no se borran.
- **Los fixtures que la sonda crea tienen que pasar por las reglas de negocio del propio servicio.** Un
  pago de $2.500 sobre una compra de $4.000 que ya tenia $4.000 programados se rechaza por saldo
  comprometido: el fixture se arma llamando a los servicios reales (asi los dos ledgers nacen como en
  produccion) y hay que dimensionar los montos para que las guardas lo dejen pasar.
- Borrar la carpeta despues. Si queda, el proximo `dotnet build` de la solucion no la toma (esta afuera), pero ensucia el scratchpad y puede confundirse con codigo del proyecto.
