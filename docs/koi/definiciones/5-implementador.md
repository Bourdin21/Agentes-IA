# Memoria Implementador — KoiDumplings
# Última actualización: 2026-09-11 (sesión actual — Etapa 28: los cinco cambios del dueño más KOI-B07, el reintento masivo que no reintentaba)

## Módulos implementados

### Etapa 28b — KOI-B07: el reintento masivo no mandaba nada cuando los envíos anteriores fallaron (2026-09-11)
- **Entrada:** hallazgo de QA sobre el propio cambio de KOI-B05 (Etapa 28), ya decidido por el dueño. Trabajo sobre `4dd42a9`. **Sin deploy, sin migración, sin tocar producción.**
- **Síntoma:** con los 3 registros del período en `Fallido` y el SMTP ya funcionando, "Enviar a los 3" contestaba *"El envío de notificaciones fue iniciado"* y **no enviaba ni cambiaba nada**. Única salida: reenviar de a uno.
- **Causa:** `EnviarNotificacionCierreAsync` abría con un guard de deduplicación **por período y todo-o-nada** que contaba CUALQUIER fila, fallida incluida (`PeriodoTieneEnviosAsync` → `AnyAsync(r => r.PeriodoMensualId == id)`). El guard no era nuevo; KOI-B05 lo volvió relevante, porque recién ahora los fallos se ven en el historial y reintentar la tanda pasó a ser la reacción natural del usuario.
- **Criterio nuevo: el guard mira sólo los envíos exitosos, y es POR INVERSOR.** Fuente única: `InversoresYaNotificadosAsync` (ids con fila `Enviado` en el período). Eso resuelve los tres casos de una sola forma, sin ramas especiales: la tanda que falló entera se reintenta completa, la que salió bien no se duplica, y la mezcla reintenta **sólo los que faltaban**. Como el worker drena la cola de a un trabajo por vez, dos clicks seguidos tampoco duplican: el segundo ve los `Enviado` que dejó el primero.
- **El preview aplica el MISMO criterio en el MISMO orden** (el comentario del archivo ya avisaba que los dos lados se tocan juntos o el preview miente): el ya notificado cae en `Omitidos` con motivo "Ya recibió la notificación de este período (envío confirmado)" — no desaparece, que es la diferencia entre "no le llegó" y "nunca se le mandó".
- **`PeriodoTieneEnviosAsync` → `PeriodoTieneEnviosExitososAsync`.** El nombre ambiguo era parte del bug: se renombró para que el criterio esté en el nombre. Un intento fallido no es un envío. También corrige el botón del historial, que decía "Revisar y reenviar" sobre un período donde no había recibido el mail nadie.
- **Mensajes que ya no mienten.** (a) El toast de éxito dice **a cuántos** se le está escribiendo y si es reintento, más cuántos quedan afuera por estar ya notificados; el "fue iniciado" a secas sonaba igual cuando el trabajo no mandaba nada. (b) "No queda nadie porque ya recibieron todos" sale como **éxito, no como error**: pintarlo de rojo hace que el usuario crea que se rompió algo y vuelva a intentar. (c) El motivo contrasta contra los que **podían** recibirlo, no contra el total de liquidaciones — un período de 15 inversores donde sólo 3 tienen usuario con email está completo cuando esos 3 lo recibieron.
- **DTO:** `YaTuvoEnvios` (true con sólo existir una fila) se reemplaza por `YaNotificados` (int) y `EsReintento` (bool). Con eso la pantalla dejó de amenazar con un duplicado que ya no puede pasar: el cartel rojo "van a recibirlo OTRA VEZ" pasa a ser un `alert-info` de cuántos quedan afuera, más un `alert-warning` de reintento cuando de verdad lo es. `EsReintento` mira sólo a los destinatarios PENDIENTES: un fallido de alguien que después recibió el mail ya está resuelto y no cuenta.
- **El pie de la lista de omitidos se volvió condicional:** la lista dejó de ser homogénea (antes todos eran "sin dirección a la cual escribir") y decirle eso a alguien que SÍ tiene dirección sería un dato falso sobre su ficha.
- **El reenvío individual NO pasa por el guard, y es deliberado:** es la acción manual sobre una fila que el usuario eligió a mano, y es el camino que se usa justamente cuando el mail salió pero el inversor no lo tiene (spam, buzón lleno, dirección corregida). El que no puede duplicar es el masivo.

#### Evidencia
- `dotnet build KoiDumplings.slnx -c Release` → **0 errores**.
- Verificado con la app levantada, Chromium real y el catcher SMTP, sobre base local propia (`koidumplings_impl_b07`, borrada al terminar):
  - **(a) tanda que falla entera y se reintenta:** 3 filas `Fallido` sin SMTP → con SMTP sano el preview dice "Reintentar con los 3" y **los 3 mails llegan de verdad** al catcher; 3 filas nuevas `Enviado`.
  - **(b) período ya enviado:** botón deshabilitado ("No hay a quién enviarle"), y **el POST directo también queda cubierto** — se forzó saltando el botón y no salió ni un mail (siguen 3) ni se escribió una fila (siguen 6). Mensaje en verde: "Los 3 inversores que podían recibir el mail ya lo recibieron. Los otros 12 no tienen un usuario con email."
  - **(c) mezcla:** con 2 `Enviado` y 1 pendiente con fallo previo, el preview muestra **Destinatarios (1)**, los 2 notificados en la lista de omitidos con su motivo, botón "Reintentar con 1 inversor", y **sale exactamente 1 mail** (el cuarto del catcher, al que faltaba). Los otros dos no recibieron duplicado.
- Tres defectos propios detectados y corregidos en la misma pasada, gracias a mirar la pantalla y no sólo la base: el motivo elegía la rama equivocada (comparaba contra el total de liquidaciones), el pie de omitidos afirmaba algo falso sobre los ya notificados, y el botón decía "Enviar a los 0".


### Etapa 28 — Las cinco decisiones del dueño sobre los hallazgos de la regresión (2026-09-11)
- **Entrada:** entrada "decisiones del dueño sobre los hallazgos de la regresión" de `trazabilidad.md` y los ítems correspondientes de `6-qa.md`. Trabajo sobre `4d82c86`, árbol limpio. **Sin deploy y sin tocar producción.**
- **Escaneo de reutilización (`catalogo.yml` + `docs/*/definiciones/5-implementador.md`):** sin alta de patrón nuevo. No hay entidad ni flujo nuevo: son un encolado que se saca, un contrato de servicio que deja de tragarse el resultado, dos permisos y un reordenamiento de tarjetas. Sí se **reutilizó de KOI mismo** el mecanismo de feature flag de `IntegracionAyres` para D-C02. Se **corrigió PAT-025**: sus `archivos_referencia` señalaban `EstadoResultadosController.ConfirmarCierre` como uno de los dos usos de la cola, y ese uso dejó de existir con KOI-B06 — ahora apunta a `NotificacionCierreController.EnviarMasivo`.
- **SIN MIGRACIÓN EF.** `RegistroEnvioNotificacion` ya tenía `Estado` (`Enviado`/`Fallido`) y `DetalleError` `varchar(2000)`: KOI-B05 es un cambio de contrato y de flujo, no de esquema. No hay script SQL que entregar.

#### KOI-B06 — cerrar un período NO manda mails
- Se sacó el `_jobs.Encolar("notificacion-cierre", ...)` de `EstadoResultadosController.ConfirmarCierre`. Con él se fueron el campo `_jobs`, el parámetro del constructor y el `using Microsoft.Extensions.DependencyInjection` (ya sin uso en el archivo). El envío queda en **un solo lugar**: `NotificacionCierreController.EnviarMasivo`, que sigue corriendo por la cola (PAT-025) y conserva su previsualización. `EnviarNotificacionCierreAsync` tiene ahora **un único llamador** en todo el repo.
- **Aviso al usuario en DOS momentos, a propósito.** (a) *Antes* de cerrar, en `PreviewCierre.cshtml`, un `alert-info` sobre el botón: cerrar no manda los mails. Va antes porque es ahí donde el usuario se arma la expectativa; decírselo sólo después significa que ya cerró creyendo que salieron. (b) *Después* de cerrar, un banner en `Anual.cshtml` —la pantalla a la que redirige el cierre— con el botón directo a la **previsualización del período recién cerrado**. No se usó el toast del `_Layout` para el link porque usa `text:` de SweetAlert (texto plano, sin HTML) y además se va solo; el toast igual cambió su texto para decir que todavía no se notificó. El banner viaja por `TempData` (como **string**: el TempData por cookie serializa a JSON y un int no vuelve garantizado como int) y por lo tanto es one-shot: no reaparece al recargar el historial.

#### KOI-B05 — "Enviado" sólo cuando el envío confirmó
- **Causa real, más profunda que el orden de dos líneas:** `EmailService.SendEmailAsync` devolvía `Task` y atrapaba **todo** adentro — sin `Smtp:Host`, sin destinatarios válidos o con excepción de MailKit, volvía igual que en un envío exitoso. El `try/catch` que envolvía la llamada en `NotificacionCierreService` **nunca se disparaba**: mover el `registro.Estado = Enviado` una línea más abajo no habría arreglado nada.
- **Fix en el contrato** (`IEmailService` → `Task<EmailSendResult>`, DTO nuevo `KoiDumplings.Application/DTOs/EmailSendResult.cs`): el fallo pasa a ser parte del contrato. Sigue **sin lanzar** a propósito —un mail que no sale no puede invalidar un cierre ya liquidado— pero ya no miente. Las tres salidas de `EmailService` devuelven su motivo.
- **El mismo defecto aparecía en otros tres lugares y se corrigieron los cuatro:** `NotificacionCierreService.EnviarNotificacionCierreAsync` y `.ReenviarAsync` (historial), `NotificacionAdminService.EnviarAsync` (el contador `FallosEmail` sólo se movía por el `catch`, así que informaba "0 fallos" sobre cero mails enviados) y `SystemController.TestEmail` (la pantalla que existe para **diagnosticar** el correo daba verde justo en el caso que tenía que detectar). En `AccountController.ForgotPassword` y `ErrorNotifier` el resultado no puede volver a la pantalla (anti-enumeración el primero, último eslabón el segundo): ahí se loguea como Error, que antes tampoco pasaba.
- `Truncar()` en `NotificacionCierreService` recorta el motivo a los 2000 de la columna y **nunca deja una fila Fallida sin explicación** (motivo vacío → texto genérico): el detalle es lo único que ve el usuario en el historial.

#### D-C01 — Auditoría sólo para el SuperUsuario
- `AuditController` pasa de `RequireAdministracion` a `RequireSuperUsuario`, que es lo que el sidebar ya venía comunicando. La policy va **a nivel de controller**, así que cubre `Index` y `GetData` — el endpoint de datos es el que importa. Barrido: no hay ninguna otra entrada a esa pantalla ni a su endpoint (sólo el link del sidebar, ya restringido a SuperUsuario).
- El filtro `if (!EsSuperUsuario())` de `GetData` **se dejó** aunque ya no se alcance: es la segunda barrera si alguien vuelve a abrir la policy.

#### D-C02 — Cámaras: el flag apaga la pantalla, no sólo el link
- `CamarasController.OnActionExecuting` corta con **404** cuando `Features:ModuloCamaras` está en false. Mecanismo: el mismo de `IntegracionAyres` (leer el flag en el controller y cortar antes de hacer nada), pero en el filtro en vez de repetido acción por acción, porque acá son cinco acciones de HTML y la lista puede crecer — cubre `Ver`, `Index`, `Create`, `Edit`, `Delete` y cualquiera que se agregue. `OnActionExecuting` es de MVC: no se introdujo ninguna abstracción nueva.
- **404 y no 403** porque con el módulo apagado la pantalla no existe para nadie, ni para el Administrador; un "acceso denegado" mandaría a pedir un permiso que no se puede dar. Encender el flag revive links y pantallas sin redeploy, igual que antes. Se actualizaron los comentarios de `FeatureFlags.cs` y `_Layout.cshtml`, que afirmaban que el módulo "sigue accesible por URL".

#### Reordenamiento de las tarjetas de Mi Inversión
- El orden que pidió el dueño para escritorio (Inversor · Div U$D · Rec U$D / Capital · Div ARS · Rec ARS) **no es el mismo** que necesita el celular: puesto tal cual en el HTML, en `col-6` el dólar y el peso del mismo indicador caen en filas distintas con "Capital aportado" en el medio — justo lo que el reordenamiento anterior vino a arreglar y lo que QA validó (ítem f5/g1).
- **Solución:** el HTML conserva el orden bueno para el celular (el que manda sin clases de orden) y el de escritorio se arma con `order-lg-*`, que sólo entra a partir de `lg`. Las seis siguen siendo hermanas de la misma grilla; no se tocaron números, barras de progreso ni `_LeyendaRecupero`.
- **Trampa anotada en la vista:** Bootstrap 5 llega hasta `order-lg-5`; el sexto lugar se pide con `order-lg-last`. Un `order-lg-6` no existe y el navegador lo ignora en silencio — la tarjeta se iría al frente sin que nada avise.

#### Evidencia
- `dotnet build KoiDumplings.slnx -c Release` → **0 errores** (9 warnings preexistentes: 8 NU1902 de MailKit/MimeKit —VUL-001— y CS0114 de `HomeController.StatusCode`).
- **Desvío de rol declarado** (mismo criterio que la Etapa 27): el implementador normalmente no ejecuta smoke test funcional; acá se hizo por pedido explícito del orquestador. App levantada en local contra una base propia (`koidumplings_impl_e28`, copia de dev, creada y borrada en la sesión) y manejada con Chromium real y logins reales de los tres roles. **No se usaron `koidumplings_qa_a/b/c`; de `koidumplings_dev` sólo se leyó (mysqldump).**
- **KOI-B06 probado con la base como testigo:** cerrado Julio 2026 desde la pantalla, el período queda en Cerrado con **15 liquidaciones y `RegistrosEnvioNotificacion` en CERO**, y el log dice "Notificaciones NO enviadas". El aviso previo y el banner posterior aparecen con su texto y el link correcto (`/NotificacionCierre/PreviewEnvio?periodoMensualId=45`); el banner no reaparece al recargar.
- **KOI-B05 probado en los tres caminos, con un servidor SMTP de prueba local:** sin `Smtp:Host` → fila **Fallido** con "El servidor de correo (SMTP) no esta configurado en el sistema" (antes decía Enviado); con SMTP que contesta 250 → los **3 mails llegan de verdad** al servidor y las 3 filas quedan **Enviado**, y el reenvío individual devuelve `success:true` y entrega el cuarto; con el puerto SMTP caído → `success:false` con el error de conexión y fila **Fallido** con ese motivo. El test de email de Herramientas del Sistema, que antes decía "enviado correctamente" sin SMTP, ahora informa Error.
- **D-C01 probado por URL directa:** Administrador e Inversor reciben **302 a AccessDenied** en `/Audit`, `/Audit/Index` y `POST /Audit/GetData`; SuperUsuario sigue recibiendo **200** en la pantalla y en el endpoint de datos.
- **D-C02 probado por URL directa con los tres roles:** `/Camaras`, `/Camaras/Ver`, `/Camaras/Index`, `/Camaras/Create` y `/Camaras/Edit/1` responden **404** para Administrador, Inversor y SuperUsuario con el flag apagado.
- **Tarjetas probadas midiendo la geometría real** (no sólo a ojo): en 1366 px las posiciones dan las dos filas pedidas; en 400 px cada par U$D/ARS queda junto en su fila, sin tarjeta huérfana y **sin scroll horizontal**. Cero errores de consola JS en las pantallas recorridas.


### Etapa 27 — Fix de los cinco defectos de la regresión de QA del 2026-09-11 (2026-09-11)
- **Entrada:** reporte de QA sobre la regresión del 2026-09-11 (DEF-A01 crítico, DEF-A02 y DEF-A03 altos). Trabajo sobre `7cdfe20`, árbol limpio. **Sin deploy y sin tocar producción**: ninguna migración aplicada allá; el script SQL queda para que lo corra el dueño.
- **Escaneo de reutilización (`catalogo.yml` + `docs/*/definiciones/5-implementador.md`):** no corresponde alta de patrón — son tres correcciones sobre código propio de KOI (una longitud de columna, un `catch` que faltaba y una guarda dentro de una migración de datos ya aplicada), no una entidad ni un flujo nuevo. Sí se reutilizó **de KOI mismo**: el patrón de manejo de error de `GuardarConceptoEnPeriodoCerradoAsync` (Etapa 25) para DEF-A02.
- **Una migración EF nueva:** `20260911132810_E24_AuditLogActionLength`. **No aplicada en producción.**

#### DEF-A01 (crítico) — `AuditLogs.Action` no entraba de 21 caracteres
- **Causa:** `AppDbContext` declaraba `Action` con `HasMaxLength(20)`, dimensionado para el audit automático (`Create`/`Update`/`Delete`). La auditoría de NEGOCIO usa nombres descriptivos y dos miden **21**: `"RecalculoPisaManuales"` (`EstadoResultadosService.cs:1013`, commit `f7d8413`) y `"EdicionPeriodoCerrado"` (`:371`, commit `48fc20e`). MySQL estricto responde `Data too long for column 'Action' at row 1`, la transacción hace rollback y **las dos funciones quedan muertas** (fail-safe: no se corrompe nada).
- **Barrido de las demás acciones antes de elegir el ancho:** `Create`/`Update`/`Delete` (6), `Reapertura` (10), `ReasignacionConcepto` (**20 — estaba justo en el límite, sin un carácter de margen**), `EdicionPeriodoCerrado` (21), `RecalculoPisaManuales` (21). 50 deja más del doble de margen sobre la más larga.
- **Datos:** `AppDbContext.cs` → `HasMaxLength(50)` + migración `E24_AuditLogActionLength` (`AlterColumn` a `varchar(50)`). Ampliar un varchar no trunca ni pierde nada; el `Down` sí puede, y está documentado en la migración.
- **Script SQL idempotente para producción** (lo aplica el dueño): ensancha la columna sólo si mide menos de 50 y registra la migración en `__EFMigrationsHistory` sólo si no está. **Ojo: `dotnet ef migrations script --idempotent` NO sirve para MySQL** — emite `IF NOT EXISTS ... BEGIN ... END`, que fuera de un procedimiento es error de sintaxis. El script entregado es el equivalente escrito a mano.

#### DEF-A02 (alta) — `PisarManuales` devolvía 500 con body vacío
- **Causa:** `PisarConceptosManualesAsync` no capturaba el fallo de su `SaveChangesAsync`; la excepción salía por el controller y el front caía en el `.fail()` del AJAX, que sólo sabe decir "Error / No se pudo guardar".
- **Dónde se corrigió:** en el **servicio**, no en el controller — es donde vive el patrón de referencia que pidió QA (`GuardarConceptoEnPeriodoCerradoAsync`) y donde manda la frontera de capas (`00-operativa-global`: los Controllers sólo coordinan). El controller ya traduce `!result.Success` a `Json(new { success = false, message })`, que es exactamente el contrato que consume el `.done()` de `Mensual.cshtml`: **no necesitó cambios**.
- Es un único `SaveChanges`, así que su transacción implícita ya garantiza todo-o-nada (filas pisadas + `AuditLog`): no hace falta transacción explícita como en el método de referencia, que tiene dos.

#### DEF-A03 (alta) — `E20_ConsolidacionCatalogos_A2` movía plata a ciegas fuera de producción
- **Causa:** el mapa viejo→nuevo son pares de **ids literales de producción** (12→39, 13→40, 22→43, 21→42, 28→55, 14→66, 15→80, 30→54, 16→81, 17→84). En cualquier otra base esos ids son otros conceptos y la migración corría igual.
- **Fix:** cada par declara ahora los **nombres esperados** de origen y destino, y **toda** sentencia que usa el mapa (pasos 1 a 4 y las dos del `Down`) valida esos dos nombres contra `Subgrupos` con un JOIN. Un par que no coincide no entra en ningún JOIN y queda intacto — igual que un par bloqueado porque el destino ya tenía importe. Además, un **paso 0** deja una fila en `AuditLogs` (`Action = 'MigracionOmitida'`) explicando cuántos pares se reconocieron, y sólo si además había histórico para mover (en una base recién creada no escribe ruido).
- **Guarda por JOIN y no por subquery, a propósito:** MySQL prohíbe leer en un subquery la misma tabla que el `UPDATE` está modificando, y el paso 4 hace `UPDATE Subgrupos` → `You can't specify target table 's' for update in FROM clause`. También se descartó una variable de sesión: el conector `MySql.Data` interpreta `@var` como parámetro (`Parameter '@e20_pares_ok' must be defined`). Los dos caminos se probaron y fallaron; el JOIN plano no depende de si el optimizador materializa o fusiona la tabla derivada.
- **Comparación de nombres:** ignora los espacios (`REPLACE(TRIM(...), ' ', '')`) porque el mismo concepto viene rotulado `(3 %)` o `(3%)` según el año del catálogo; mayúsculas y tildes las resuelve la collation `_ci` de la columna.
- **Los diez nombres esperados se derivaron del catálogo real** (leído en `koidumplings_dev`, sólo SELECT), no de los comentarios de la migración: los comentarios estaban abreviados (el par 14 decía "Comisiones Tarjetas" cuando el subgrupo se llama "Comisiones Tarjetas (5 %)"). Los ids de prod son los de dev +11 en los dos bloques del catálogo, lo que permitió confirmar los diez pares uno por uno.
- **Producción no cambia:** la migración ya está registrada en `__EFMigrationsHistory` allá, así que editarla no la re-ejecuta; y aun re-ejecutada sobre una base con forma de producción da el mismo resultado (verificado abajo).

#### KOI-B01 (alta) — el tilde "Se muestra" de un benchmark siempre se guardaba apagado
- **Causa:** en `Views/Configuracion/Benchmarks.cshtml` el `<input type="hidden" name="activo" value="false">` estaba escrito **antes** del `<input type="checkbox" name="activo" value="true">`, en las filas existentes (`:90-92`) y en la fila de alta (`:135-136`). Los dos comparten `name`, así que el POST lleva una colección de dos valores y el `SimpleTypeModelBinder` de un `bool` toma el **primero**: siempre `false`. El comentario que estaba arriba del bloque describía el patrón correcto; el código hacía justo lo contrario.
- **Efecto:** guardar el S&P 500 con el tilde puesto lo dejaba `Activo=0` y desaparecía de la comparativa de mercado de los 15 inversores; volver a tildarlo no lo arreglaba y un benchmark nuevo nacía apagado. Ítem h6 del checklist del cliente.
- **Fix:** checkbox primero, hidden después — el orden que genera `asp-for`. Acá no se puede usar `asp-for` porque es edición inline por fila: los `<form>` viven fuera de la tabla (un `<form>` dentro de un `<tr>` es HTML inválido) y los inputs se enganchan con el atributo `form="..."`.
- **Barrido del resto del proyecto:** `grep -B3 'type="checkbox"' Views/**/*.cshtml | grep 'type="hidden"'` sobre todas las vistas → **sólo esos dos lugares**. No hay otro checkbox con hidden companion en KOI.
- **Sin cambios en el controller:** `BenchmarkGuardar(int id, string nombre, decimal porcentajeAnual, int orden, bool activo)` ya estaba bien; el problema era exclusivamente el orden en la vista.

#### KOI-B02 (media) — Dashboard en blanco al cambiar de año
- **Causa:** `cargarHistorico()` (`Views/Dashboard/Index.cshtml:1013-1014`) tocaba `btnHist12`/`btnHist24` sin verificar que existieran, y se autoinvoca al final del `@section Scripts` (`:1093`), **fuera de toda condición Razor**. Los dos botones y el canvas `chartHistorico` viven dentro del `else` de `@if (!d.TieneDatos)`, así que en un período sin ventas no existen: `getElementById` devolvía `null`, el `TypeError` cortaba el bloque `<script>` entero y la pantalla quedaba prácticamente vacía.
- **Fix:** early return si no está el canvas (así ni se dispara el `fetch`, cuyo resultado tampoco tendría dónde ir — el `new Chart(null, ...)` de más abajo tiraba su propio error dentro del `.then`), más null-guard en los dos botones. El `new Chart` ahora reusa la referencia ya resuelta.
- **Barrido del resto de la vista:** los otros ocho `getElementById` del `@section Scripts` ya estaban cubiertos — `chartCanal`/`chartTicket` bajo `d.TieneDatos && v != null && v.VentasTotales > 0` (más estricta que el markup, que sólo pide `d.TieneDatos && v != null`); `chartGastosRubro` bajo `d.TieneDatos && d.Rubros.Any()`, idéntica a `hayGraficoRubros`; `chartVsGastos` bajo `d.TieneDatos && d.VentasTotales > 0`, idéntica a `hayTortaResultado`; `diarioEstado`/`chartDiario` bajo `muestraSerieDiaria`, la misma bandera que su markup. `cargarHistorico` era el único sin ninguna condición.

#### Evidencia de KOI-B01 y KOI-B02 (navegador real + base local)
- App levantada en local contra una base propia (`koidumplings_impl_b`, creada y borrada en la sesión; **no** se usaron `koidumplings_qa_a/b/c` ni `koidumplings_dev`), con Playwright headless y login real.
- **KOI-B01, leído contra la base después de cada guardado:** tilde puesto → el POST viaja `["true","false"]` y `Activo = 1`; tilde sacado → viaja `["false"]` y `Activo = 0`; volver a tildarlo → `Activo = 1` otra vez (el "no se recupera" del reporte queda resuelto); benchmark nuevo con el tilde por defecto → nace con `Activo = 1`.
- **KOI-B02:** `/Dashboard?anio=2024&mes=5` como Inversor → la pantalla renderiza (encabezado, selector de período y el aviso "No hay períodos cargados aún"), `cargarHistorico(24)` invocada a mano no rompe, y **cero errores de consola**. Control con el mes actual (que sí tiene datos): el canvas del histórico se dibuja y `btnHist12` queda activo, sin errores.
- **Contraprueba con las dos vistas revertidas a `7cdfe20`** y la app reconstruida: KOI-B01 postea `["false","true"]` y deja `Activo = 0` pese al tilde; KOI-B02 tira `pageerror: Cannot read properties of null (reading 'classList')`. Los dos defectos se reproducen tal cual los reportó QA, lo que valida que la verificación de arriba mide lo que tiene que medir.
- **Desvío de rol declarado:** el implementador normalmente no ejecuta smoke test funcional (`00-operativa-global`). Acá se hizo por pedido explícito del orquestador ("verificalo de verdad", "verificá con un navegador real"), y se documenta para que no se lea como que la regla cambió.

#### Regla preventiva cross-proyecto
- Se agregaron dos secciones nuevas a `.github/instructions/32-estandares-qa-implementador.instructions.md`: el orden checkbox/hidden para un `bool` (KOI-B01) y "un script que toca elementos condicionales tiene que estar bajo la misma condición que los renderiza" (KOI-B02). Los dos son generalizables a cualquier proyecto del baseline.
- **No se tocó `docs/qa/regresiones-manuales.yml`**: estaba siendo editado por QA en paralelo. Los dos ítems YAML quedan para que los cargue QA.

#### Evidencia de DEF-A01 a DEF-A03
- **Build:** `dotnet build KoiDumplings.slnx -c Release` → **Compilación correcta, 0 errores** (9 warnings preexistentes: NU1902 MailKit/MimeKit y CS0114 `HomeController.StatusCode`; ninguno nuevo).
- **DEF-A01 probado contra bases locales propias** (`koidumplings_impl_pre` / `_post`, creadas para esto; no se tocó `koidumplings_dev` salvo lecturas, ni las `_qa_*`), con un programa mínimo que usa el **`AppDbContext` real**:
  - Con la columna en `varchar(20)`: `EdicionPeriodoCerrado` y `RecalculoPisaManuales` → `Data too long for column 'Action' at row 1`; `ReasignacionConcepto` (20) y `Reapertura` (10) pasan. **Defecto reproducido tal cual lo reportó QA.**
  - Con E24 aplicada: las cuatro guardan y se releen de la base.
  - El **script SQL corrido dos veces seguidas** sobre la base pre-E24: `varchar(20)` → `varchar(50)`, una sola fila en `__EFMigrationsHistory`. Idempotente.
- **DEF-A03 probado con dos bases gemelas** (mismos ids, mismos importes, **sólo cambian los nombres**), migradas hasta E19 y después con E20 aplicada:
  - **Forma de producción:** 10 conceptos trasladados, 10 subgrupos viejos dados de baja, **total del período idéntico** (8.702.000,00), 0 avisos → **mismo resultado que la migración original**.
  - **Forma de desarrollo (ids de dev):** **0 filas tocadas, 0 creadas, 0 dadas de baja**, total idéntico, 1 aviso en `AuditLogs`.
  - **Contraprueba con la migración SIN la guarda** (versión de `7cdfe20`) sobre la misma base de desarrollo: reproduce exactamente lo que vio QA — `Alquiler del local` 4.500.000 aterriza en `Cristalería & Equipamiento`, 20 conceptos tocados, 10 creados, 10 dados de baja.
- **Sin smoke test funcional propio** (no se levantó la app ni se probó por navegador): la verificación es de base de datos y de código. Los pasos de pantalla quedan para QA.

#### Pruebas mínimas para QA
1. **DEF-A01a:** en un mes **cerrado**, corregir el importe de un gasto. Tiene que guardar, informar el impacto en liquidaciones, y en **Auditoría** aparecer una entrada `EdicionPeriodoCerrado`.
2. **DEF-A01b:** en un mes **abierto** con al menos un porcentual escrito a mano que difiera del cálculo, usar **Revisar → tildar → confirmar**. Tiene que pisar y dejar una entrada `RecalculoPisaManuales` en Auditoría.
3. **DEF-A01c:** reasignar el subgrupo de un gasto (`ReasignacionConcepto`, 20 caracteres) — control de que no se rompió lo que ya andaba.
4. **DEF-A02:** con la base caída o el usuario de MySQL sin permiso de escritura, confirmar el pisado: tiene que salir el cartel **"No se reemplazó nada"** con el texto "No se pudo reemplazar los importes escritos a mano. No se modifico nada." y **no** el error genérico.
5. **DEF-A03:** sobre una base nueva que NO sea producción, correr las migraciones de cero y verificar que ningún importe cambió de concepto; si había histórico, que quedó la fila `MigracionOmitida` en `AuditLogs`.
6. **KOI-B01:** en Configuración → Benchmarks, guardar el S&P 500 con el tilde puesto, recargar la pantalla y confirmar que sigue tildado **y** que aparece en la Comparativa de Mercado del reporte de un inversor. Repetir destildándolo (tiene que desaparecer del reporte) y volviendo a tildarlo (tiene que volver). Dar de alta un benchmark nuevo sin tocar el tilde: nace activo.
7. **KOI-B02:** entrar como Inversor a "Rendimiento Histórico" y elegir un año sin datos cargados en el selector. La pantalla tiene que renderizar el encabezado, el selector y el aviso de sin datos, con la consola del navegador **sin errores**. Control: un mes con datos sigue dibujando el gráfico de evolución y el botón "12 meses" queda activo.

#### Riesgos y supuestos
- **El script `E24_action.sql` no está aplicado.** Hasta que se corra en producción, las dos funciones de DEF-A01 siguen muertas allá. El código nuevo **no depende** de que se aplique antes del deploy (nada lee la columna más ancha), pero deployar sin aplicarlo no arregla nada.
- **Orden sugerido:** aplicar el script y después deployar. Si se deploya primero, el `migrate` automático del arranque —si está activo— aplicaría E24 solo; conviene igual correr el script a mano para no depender de eso.
- **DEF-A03 con nombres renombrados:** si el cliente renombra en producción alguno de los diez subgrupos y alguien vuelve a correr E20 sobre una copia, ese par ya no se movería. Es el comportamiento buscado (mejor no mover que mover mal) pero conviene saberlo.
- **La guarda es por par, no todo-o-nada.** Si nueve pares coinciden y uno no, los nueve se mueven y el décimo queda intacto, con aviso en `AuditLogs`. Se eligió así porque el todo-o-nada exigía un subquery agregado que MySQL rechaza en el paso 4.
- **Los 11 subgrupos viejos sin equivalente claro siguen sin decidirse** con el cliente (pendiente que ya venía de la Etapa 22).

#### Checklist de salida para merge
- [x] Build Release 0 errores, sin warnings nuevos.
- [x] Migración nueva creada y **no** aplicada en producción; script SQL idempotente entregado y probado.
- [x] Migraciones ya aplicadas: ninguna modificada en su efecto sobre producción (sólo E20, cuyo resultado en una base con forma de producción es idéntico).
- [x] Sin cambios de permisos, estados ni validaciones de negocio.
- [x] Frontera de capas respetada (el `catch` quedó en el servicio; el controller no cambió).
- [ ] Prueba manual de QA (5 pasos de arriba).
- [ ] Deploy y aplicación del script en producción — **los decide el dueño**.

### Etapa 26 — Política del recálculo de porcentuales + tipo de cambio y fecha de ingreso del inversor (recupero en pesos corregido) (2026-09-10)
- **Decisiones textuales del dueño:** (T1) *"El recálculo automático que pise los valores cargados a mano, avisando previamente que se van a pisar."* (T2) Sí al TC y fecha de ingreso por inversor; el recupero en pesos actual está mal.
- **Gate:** definiciones 2, 3 y 4 aprobadas. **Presupuesto SALTEADO** por decisión del dueño (igual que Etapas 22 a 25). Trabajo sobre `48fc20e` (Etapa 25). **Sin commit ni deploy.** **Cero requests a producción** (ni GET ni POST al portal, ni conexión a `MYSQL5044`, ni `database update` contra prod): todo contra `koidumplings_dev`, con `--connection` explícito y `ASPNETCORE_ENVIRONMENT=Development`.
- **Dos migraciones EF**, aplicadas **sólo en dev**: `20260910162303_E22_PorcentualesManualesHeredados` (sólo datos) y `20260910162500_E23_InversorIngreso` (3 columnas + carga por Id).

**Escaneo de reutilización (`catalogo.yml` + `docs/*/definiciones/5-implementador.md`):** 3 hits, ningún patrón nuevo; **se registró KOI en PAT-021** con la variante nueva.

| Origen | Qué se tomó | Cómo se aplicó |
|---|---|---|
| **PAT-021 — labipac** (valor manual vs. fórmula, excluido del recálculo batch) | Pieza 1: el batch filtra por modo y la fila manual queda fuera a propósito; y la nota (b): el modo manual necesita **visibilidad**, no automatismo. | Es el modelo que KOI ya tenía desde la Etapa 19 (`ImporteEditadoManual`). La variante de esta etapa: la fila manual **se puede** pisar, pero sólo con confirmación explícita; y el aviso del GET es la "visibilidad" que pide la nota (b). Se agregó `koi` a `proyectos_que_lo_usan` con los archivos. |
| **KOI — `AplicarAyres` (Etapa 21)** | Re-consulta y comparación con lo que el usuario vio en el preview antes de escribir. | Mismo principio en `PisarConceptosManualesAsync`: el cliente reenvía los dos importes que VIO y el servidor no pisa una fila que cambió entretanto (chequeo optimista por valor; PAT-004/RowVersion no aplica: la fila no tiene RowVersion y el valor es lo que importa). |
| **KOI — `RevertirConceptoAlPorcentajeAsync` + AuditLog de negocio (Etapas 19 y 25)** | Las escrituras exactas de "volver al %" y el `AuditLog` con snapshot JSON (`SnapshotJsonOptions`). | Pisar = volver al % en lote (mismos tres campos). `AuditLog` `RecalculoPisaManuales` con el valor a mano que se pierde y quién confirmó. |

#### Verificación de las premisas contra el código (y contra dev)
- ✅ **T1:** `Mensual` (GET) llamaba a `RecalcularPorcentualesAsync` en todo período abierto y `RecalcularInternamente` escribía `ImporteCalculado = base × %` en toda fila sin marca. En dev, julio 2026: Regalías y Cánon están **exactamente** en base × % (1.836.807,66 / 1.530.673,05) y el valor original del cliente **sobrevive en `ImporteManual`** (1.379.978,05 / 1.455.673,05) — dato útil para la conciliación pendiente (no verificado en prod: prohibido).
- ✅ **T2:** la fórmula vieja `Σ (neto ÷ (capital × TC_mes))` da **exactamente** el recupero en dólares: en dev, las 15 fichas dan el mismo número al centavo con las dos fórmulas.
- ⚠️ **Hallazgo T1 (corregido):** `RecalcularPorcentualesAsync` **no rechazaba meses cerrados**: un POST directo a `Recalcular` reescribía los porcentuales automáticos de un mes cerrado. Ahora los tres métodos de recálculo rechazan períodos cerrados.
- ⚠️ **Hallazgo T1 (NO corregido, decisión del dueño):** "completar vacíos" incluye **crear la fila** de un porcentual vigente que no está en el mes. En un mes cuyos porcentuales están imputados a subgrupos del **catálogo viejo** (históricos), la fila nueva no es un vacío real: duplica el concepto. Es exactamente lo que pasó en **enero 2026** (4 filas nuevas junto a las viejas). El pedido pide explícitamente completar vacíos "sin fila", así que se respetó; pero **reabrir un mes de 2024/2025 y abrir la pantalla duplicaría Regalías, Cánon y Previsiones**. Ver riesgos.
- ⚠️ **T2 en dev:** los Ids de dev son **26 a 40**, no 1 a 15 (mismo orden, desplazados 25). La migración actualiza **por Id** como se pidió, así que en dev **no tocó ninguna ficha** (las 15 quedaron en NULL). No se cargó nada por nombre.

#### T1 · Política del recálculo — "nunca en silencio"
- **`RecalcularInternamente(..., soloCompletarVacios)`** — un solo lugar decide:
  - **Fila automática** (`ImporteEditadoManual = false`): se recalcula siempre (POST), sin preguntar.
  - **Fila escrita a mano:** acá **nunca** se pisa. Si difiere del cálculo (> medio centavo) va a `PendientesDeConfirmar` (concepto, rubro, %, actual → recalculado). En un POST se sigue refrescando `PorcentajeAplicado` (la referencia visible, Etapa 19), no el importe.
  - **GET (`soloCompletarVacios = true`):** no se escribe **nada** de una fila con valor. Sólo se completan los vacíos: sin fila, o en 0 y no manuales. Se informan las manuales que difieren y se cuentan las automáticas desactualizadas.
- **`CompletarPorcentualesVaciosAsync`** (GET) y **`RecalcularPorcentualesAsync`** (botón) delegan en `RecalcularPeriodoAsync`, que rechaza meses cerrados. `GuardarVentasAsync` pasa a devolver `ServiceResult<RecalculoPorcentualesDto>`: **las ventas se guardan igual** y sólo el pisado queda sujeto a confirmación.
- **`PisarConceptosManualesAsync`** — pisa **sólo lo confirmado** y sólo si el importe actual y el recalculado siguen siendo los que el usuario vio (tolerancia medio centavo); si no, omite la fila y lo dice. Mismas escrituras que "volver al %": `ImporteCalculado = base × %`, `PorcentajeAplicado`, **`ImporteEditadoManual = false`**. `AuditLog` `RecalculoPisaManuales` con valor anterior y nuevo por concepto y **el usuario que confirmó** (el automático del `DbContext` suma el detalle por columna). Rechaza meses cerrados.
- **Los tres caminos que recalculan** (`Recalcular`, `GuardarVentas`, `AplicarAyres`) devuelven `pendientesPisado`. **`AgregarConceptoAlMes`** también recalcula (modo POST): las manuales no se tocan y ahí no se pregunta (no cambió la base).
- **Acción nueva `PisarManuales`** — `[Authorize(Policy = "GestionOperativa")]` + `[HttpPost, ValidateAntiForgeryToken]`, JSON en el body (`[FromBody] PisarManualesRequest`): los importes viajan invariantes; el binder de formularios usa es-AR. **Placa de atributos verificada acción por acción** después de insertar (ninguna acción sin su bloque).
- **Vista `Mensual`:** `confirmarPisadoManuales(pendientes, luego)` — SweetAlert2 con la lista (concepto, rubro · %, "Hoy (a mano)" → "Con el %"), **un tilde por fila** (todos tildados; destildar = conservar), "Reemplazar los tildados" / "Dejarlos como están". Cancelar no manda nada. Enganchado a Guardar ventas, Recalcular % y Traer de Ayres, siempre **después** de que las ventas ya se guardaron. **Aviso discreto** arriba de la grilla (`alert-light`) en el GET: "N conceptos porcentuales escritos a mano no coinciden…" + botón **Revisar** (abre el mismo diálogo) y, si hay, "N automáticos desactualizados: se actualizan con Recalcular %".
- **Migración E22 (sólo datos):** marca `ImporteEditadoManual = 1` en toda fila porcentual viva (tipo del **subgrupo** ≠ Manual) cuyo `ImporteCalculado` no coincide con `ROUND(base × PorcentajeAplicado / 100, 2)` de su período (base = Ventas A si tipo 2, Ventas Totales si tipo 3). Detalles: **tolerancia 1 centavo** (el sistema redondea con `Math.Round` al par; MySQL `ROUND` lejos del cero: en un punto medio exacto difieren 0,01 y esa fila es del sistema); sin `PorcentajeAplicado` se marca si tiene importe (el sistema siempre escribe el %); lápidas fuera. **No cambia ningún importe.** Antes de marcar deja un `AuditLog` **`MarcaManualHeredada` por fila** (importe y lo que daba el %); el **Down** desmarca exactamente esas filas y borra las marcas.
  - **Resultado en dev:** 145 filas marcadas, **todas de meses cerrados** y todas sin `%` (importadas del Excel); 145 `AuditLog`; las 20 porcentuales de meses abiertos **quedaron automáticas** porque coinciden con base × % (fueron pisadas por la 19b). Esperable en prod lo mismo: los porcentuales pisados de 2026-01/07/08 quedan automáticos (el dueño pidió no restaurarlos todavía).

#### T2 · Tipo de cambio y fecha de ingreso; recupero en pesos
- **`Inversor`:** `TipoCambioIngreso` (`decimal(18,4)`, igual que los otros TC), `AnioIngreso`, `MesIngreso` (int, criterio año/mes de `AsignacionPuntos` y `PeriodoMensual`). **Nullables** en base (fichas sin el dato → el recupero en pesos sale "—", nunca se inventa); **obligatorios** en el formulario.
- **Migración E23:** agrega las 3 columnas y carga **por Id** (Ids de prod): 1–11 → 980 / 2024-11; 12 → 1200 / 2024-11; 13–14 → 1000 / 2024-11; 15 → 1180 / 2025-04. En dev no actualizó nada (Ids 26–40).
- **ABM Inversores:** partial `_CamposIngreso` compartido por Alta y Edición (TC en `$`, combo de mes inicializado con el valor cargado — estándar QA de combos en Editar —, año). Listado: columna **Ingreso** ("Noviembre 2024 · U$D a $ 980") o badge **"Falta cargar"**.
- **Recupero ARS** = `Σ Neto de las Pagada ÷ (capital U$D × TC de ingreso) × 100` (fórmula del Excel, `M3 = L3*980`, `M5 = M4/M3`). **Criterio de cobradas: Pagada**, el de siempre. Aplicado en **todos** los lugares: KPI de Mi Inversión, **fila por fila** del historial (`RentaMensualPesos` = neto del mes ÷ capital en pesos; `RecuperoAcumuladoPesosPorc` = Σ pesos cobrados hasta ese mes ÷ capital en pesos, running total del mismo recorrido → la última fila coincide con el KPI), la serie en pesos del **gráfico** (sale de esas filas) y el **Reporte** (toma todo de `ObtenerMiInversionAsync`, no recalcula). **El recupero en dólares no cambió.**
- **Rentabilidad mensual promedio** = recupero ÷ **meses desde el ingreso**, en U$D y en $, calculada en `ObtenerMiInversionAsync` (una sola fuente) sobre el cociente sin redondear. **Decisión de implementación:** meses = desde el mes de ingreso **hasta el último mes cobrado (Pagada), inclusive** — el mismo corte que el numerador. Un mes sin liquidación en el medio cuenta. No se copió ninguna fórmula del Excel (14, 9, corte en diciembre). El "En N meses" del Reporte pasa a ser ese mismo N. Sin fecha de ingreso → "—".
- **Leyenda reescrita** (partial `_LeyendaRecupero`, compartido por Mi Inversión y Reporte): con los números del propio inversor — "Cuando pusiste tu capital en noviembre de 2024, el dólar estaba a $ 980: tus U$D 21.000 equivalían a $ 20.580.000. Ese es el valor en pesos de tu inversión, y queda fijo. Los dividendos, en cambio, los cobrás en pesos…". Si en pesos da más alto dice que el dólar subió; si no, un texto neutro (no afirma algo falso).

**Números en dev con la fórmula nueva** (TC por nombre sólo para este cálculo de control; en la base no se cargó nada):

| Inversor | U$D (Pagada) | $ (Pagada) | U$D (todas) | $ (todas) | $ fórmula vieja |
|---|---|---|---|---|---|
| Minjo Wang | 44,25 % | **57,21 %** | 48,12 % | 62,74 % | 44,25 % |
| Marcelo Irigo | 41,20 % | **53,22 %** | 44,59 % | 58,05 % | 41,20 % |
| Martin Salas | 42,04 % | **53,17 %** | 45,53 % | 58,05 % | 42,04 % |
| Juan M. Lanzillota | 35,05 % | **36,92 %** | 37,95 % | 40,31 % | 35,05 % |
| Andrés Caicedo | 15,67 % | **17,30 %** | 17,93 % | 19,98 % | 15,67 % |

- **En pesos da mayor que en dólares en los 15** (dev). La columna "fórmula vieja" confirma el diagnóstico: coincidía con la de dólares.
- **La referencia del encargo (Wang 60,9 / 46,6, etc.) no se puede reproducir en dev:** dev tiene liquidaciones hasta 2026-04 con importes que no son los de prod (Wang U$D "todas" = 48,12 % en dev vs 46,6 % en prod), así que no es una copia de prod. La referencia además suma **todas** las liquidaciones; el sistema cuenta **sólo las Pagada** (criterio vigente): en prod la diferencia son las liquidaciones pendientes (agosto 2026 y lo que siga sin pagar). Con "todas", dev da el orden de magnitud esperado (Wang 62,7 % / 48,1 %).

#### Cambios por capa
| Capa | Archivo | Cambio |
|---|---|---|
| Domain | `Entities/Inversor.cs` | `TipoCambioIngreso`, `AnioIngreso`, `MesIngreso` (nullables, documentados). |
| Application | `Interfaces/IEstadoResultadosService.cs` | `GuardarVentasAsync` y `RecalcularPorcentualesAsync` devuelven `RecalculoPorcentualesDto`; nuevos `CompletarPorcentualesVaciosAsync` y `PisarConceptosManualesAsync`; DTOs `RecalculoPorcentualesDto`, `PisadoPendienteDto`, `ConfirmacionPisadoDto`, `ResultadoPisadoDto`. |
| Application | `DTOs/InversionesDtos.cs` | `MiInversionDto`: TC/mes/año de ingreso, `CapitalAportadoPesos`, `MesesDesdeIngreso`, rentabilidades U$D y $. `ReporteRendimientoDto`: datos de ingreso. Comentarios de fórmula corregidos. |
| Infrastructure | `Services/EstadoResultadosService.cs` | `RecalcularInternamente` con la política nueva; `RecalcularPeriodoAsync` (rechaza cerrados); `PisarConceptosManualesAsync`. Nombre de rubro por diccionario con `IgnoreQueryFilters`, **no con `Include`** (navegación requerida con query filter → INNER JOIN que sacaría del recálculo los subgrupos de un rubro dado de baja). |
| Infrastructure | `Services/InversionesService.cs` | Recupero en pesos con TC de ingreso (KPI + historial), meses desde el ingreso y rentabilidad promedio; el Reporte las toma de `MiInversion`. |
| Infrastructure | `Data/AppDbContext.cs` + 2 migraciones + snapshot | Precisión `(18,4)` del TC de ingreso. E22 (datos) y E23 (esquema + datos). |
| Web | `Controllers/EstadoResultadosController.cs` | `Mensual` usa `CompletarPorcentualesVaciosAsync` y llena el aviso; `pendientesPisado` en `GuardarVentas`, `AplicarAyres` y `Recalcular`; acción nueva `PisarManuales`. |
| Web | `Controllers/InversoresController.cs`, `Models/ConfiguracionViewModels.cs` | Campos nuevos en alta, edición y listado; validación obligatoria. |
| Web | `Models/EstadoResultadosViewModels.cs`, `Models/LeyendaRecuperoViewModel.cs` (nuevo) | Datos del aviso, `PisarManualesRequest`, modelo de la leyenda. |
| Web | `Views/EstadoResultados/Mensual.cshtml` | Aviso + botón Revisar, `confirmarPisadoManuales`, enganches en los 3 caminos, tooltip del botón Recalcular. |
| Web | `Views/Inversores/*` (+ `_CamposIngreso.cshtml` nuevo) | Campos de ingreso y columna Ingreso. |
| Web | `Views/MiInversion/Index.cshtml`, `Reporte.cshtml` (+ `_LeyendaRecupero.cshtml` nuevo) | Leyenda nueva compartida; títulos de columnas y comentarios corregidos. |

#### Evidencia de build y de base
- `dotnet build KoiDumplings.slnx -c Debug` → **Compilación correcta, 0 errores**; advertencias **todas preexistentes** (NU1902 MailKit/MimeKit — VUL-001; CS0114 `HomeController.StatusCode`). Ninguna nueva.
- `dotnet ef database update --connection "…koidumplings_dev…"` → aplicadas E22 y E23 **en dev**. Historial: `E23_InversorIngreso`, `E22_PorcentualesManualesHeredados`, `E21_…`. Verificado por SQL: 145 marcadas / 145 `AuditLog` / 20 abiertas intactas / 15 fichas en NULL (Ids 26–40).
- **Sin smoke test funcional** (regla del rol). Guía manual abajo.

#### Barrido legal (ítem 23) — revalidado
- Las únicas líneas agregadas con `VentasA`/`VentasTotales` son **internas del servicio** (la base del %). Superficie nueva: `PisarManuales` y el aviso (`GestionOperativa`; el Inversor no entra) y la leyenda del inversor, que habla sólo de capital, tipo de cambio y dividendos. **Ningún dato facturado/informal nuevo para el rol Inversor.** El diálogo de pisado dice "% de las ventas", sin A/B.

#### Riesgos y supuestos
- **Duplicación al completar vacíos en meses del catálogo viejo** (ver hallazgo): reabrir un mes de 2024/2025 y abrir la pantalla crea los porcentuales nuevos al lado de los históricos. Preexistente desde la 19b y fuera del pedido; **decisión del dueño**: o no completar filas nuevas en meses con porcentuales históricos, o conciliar el catálogo de esos meses antes de reabrir.
- **En prod, los porcentuales pisados por la 19b quedan automáticos** (coinciden con base × %): el próximo cambio de ventas en julio/agosto los recalcula sin preguntar. Es lo pedido (no restaurar sin aprobación); si el cliente escribe su valor, queda protegido.
- **Falsos "manuales" posibles:** una fila que generó el sistema y quedó vieja porque las ventas cambiaron por otra vía sin recalcular (importación) queda marcada como manual. Es el error seguro: pide confirmación en vez de pisar.
- **Down de E22:** desmarca las 145 filas registradas; si alguna se editó a mano después, también la desmarca.
- **Rentabilidad promedio:** el corte "hasta el último mes cobrado" es decisión de implementación; si el dueño prefiere "hasta el último mes cerrado" (incluye meses pendientes de pago), es cambiar una línea.
- **Dev sin TC de ingreso:** Mi Inversión y el Reporte en dev muestran el recupero en pesos "—" hasta cargar las fichas a mano (paso 11 de la guía).
- **La auditoría del GET:** completar un vacío sigue quedando a nombre de quien abrió la página, pero ahora sólo pasa con filas sin valor.

#### Guía de prueba manual (dev — NUNCA contra producción)
1. **GET no pisa:** como Administrador, abrir **julio 2026**. Anotar Regalías. Recargar dos veces: el valor no cambia y no aparece nada nuevo en Auditoría para esas filas.
2. **Manual protegido + aviso:** escribir en Regalías `1379978,05` (borde naranja). Recargar: aparece el aviso gris "1 concepto porcentual escrito a mano no coincide…" con **Revisar**, y Regalías sigue en 1.379.978.
3. **Revisar → cancelar:** el diálogo muestra Regalías `1.379.978 → 1.836.808`. "Dejarlos como están": nada cambia (recargar).
4. **Recalcular %:** los automáticos se recalculan; aparece el mismo diálogo para Regalías. Destildar todo y confirmar → pide "Tildá al menos uno". Cancelar → Regalías intacta.
5. **Guardar ventas:** cambiar una venta y guardar. Aparece el diálogo (no el toast). Cancelar: al recargar **las ventas nuevas están guardadas**, los automáticos recalculados y Regalías intacta.
6. **Confirmar:** repetir y confirmar. Regalías queda en base × %, borde punteado (automático). En **Auditoría** hay una fila `RecalculoPisaManuales` con el 1.379.978,05 anterior y **el usuario que confirmó**.
7. **Concurrencia:** dejar el diálogo abierto en una pestaña, cambiar Regalías a mano en otra y confirmar en la primera → "el importe cambió desde que se mostró el aviso; no se tocó".
8. **Traer de Ayres** (si está configurado en dev): mismo comportamiento que el paso 5 después del diálogo "Ventas aplicadas".
9. **Mes cerrado:** forzar `POST /EstadoResultados/Recalcular` sobre un mes cerrado → `success:false`, "El periodo esta cerrado…".
10. **Migración:** en Auditoría, acción `MarcaManualHeredada` → 145 filas (dev), todas de meses cerrados.
11. **Inversores:** el listado muestra "Falta cargar" en las 15 fichas (dev). Editar **Minjo Wang**: sin TC/mes/año no deja guardar. Cargar `980` / Noviembre / 2024 → el listado muestra "Noviembre 2024 · U$D a $ 980". Alta de un inversor nuevo sin esos datos → no deja guardar.
12. **Mi Inversión (Wang):** Recupero U$D **44,25 %**, $ **57,21 %**; leyenda con "$ 980" y "$ 20.580.000"; la última fila del historial, columna Recupero acum. abajo, **= 57,21 %**; en el gráfico la línea en pesos va por encima de la de dólares.
13. **Reporte (Wang):** "En 18 meses"; rentabilidad mensual **2,46 %** y **3,18 % en pesos**; misma leyenda.
14. **Ficha sin TC** (cualquier otra): recupero $ "—", sin leyenda, sin línea en pesos, rentabilidad "—".
15. **Barrido legal:** con un Inversor recorrer Dashboard, Mes Actual, Mi Inversión, Reporte e Historial: ningún dato facturado/informal (A/B).

#### Checklist de salida para merge
- [x] Build 0 errores, 0 advertencias nuevas
- [x] T1: ningún camino pisa una fila manual sin confirmación; el GET no escribe nada con valor; cerrados rechazados
- [x] T1: pisado con chequeo de lo que el usuario vio + AuditLog con quién confirmó
- [x] T1: migración de datos que sólo marca, con AuditLog por fila y Down exacto
- [x] T2: campos en entidad, migración por Id, alta/edición obligatorios, listado
- [x] T2: recupero $ con TC de ingreso en KPI, historial, gráfico y Reporte; U$D sin cambios
- [x] T2: rentabilidad promedio por meses desde el ingreso (U$D y $); leyenda reescrita
- [x] Placa de atributos del controller verificada; barrido legal revalidado
- [x] Migraciones aplicadas y verificadas **sólo en dev**
- [ ] **Commit, deploy y `database update` en prod: deliberadamente SIN hacer** (a cargo del dueño)
- [ ] Prueba manual de los 15 pasos
- [ ] Decidir: duplicación al completar vacíos en meses del catálogo viejo; corte de la rentabilidad promedio
- [ ] Conciliación de los porcentuales pisados por la 19b (pendiente de aprobación del dueño)

### Etapa 25 — Estado de Resultados: editar gastos históricos, corregir meses cerrados y reasignar el subgrupo (2026-09-10)
- **Pedido del dueño del estudio:** *"estado de resultados con gastos históricos cargados, se deben poder editar de igual manera el importe y los subgrupos."*
- **Gate:** definiciones 2, 3 y 4 aprobadas. **Presupuesto SALTEADO** por decisión explícita del dueño, igual que en las Etapas 22 a 24. **Sin commit ni deploy** por instrucción.
- **Sin migraciones EF** (ni de esquema ni de datos). Todo se apoya en columnas que ya existían: `ConceptoGasto.DeletedAt` (lápida de C3), `ImporteEditadoManual` (E19) y `AuditLogs`.
- **El diseño del punto 2 NO se inventó en esta etapa:** es el criterio de aceptación **3** de `1-analista-funcional.md` §14.2, aprobado en agosto y nunca implementado. Se implementó textual.

**Escaneo de reutilización (`catalogo.yml` + `docs/*/definiciones/5-implementador.md`):** 4 hits, ningún patrón nuevo al catálogo.

| Origen | Qué se tomó | Cómo se aplicó |
|---|---|---|
| **PAT-020 — marihogar** (cancelación con pagos: reversión acotada a lo posteado) | El principio: lo ya posteado no se edita; la corrección se acota a lo que todavía no se ejecutó. | Es exactamente la regla del criterio 3: liquidaciones **Pendientes** se recalculan, **Pagadas** no se tocan. No se copió código: el dominio es otro (no hay ledger ni contramovimiento). |
| **KOI — `ReabrirPeriodoAsync` (Etapa 17)** | Transacción + `AuditLog` de negocio con snapshot JSON (`SnapshotJsonOptions`) + resumen de liquidaciones con nombres (`IgnoreQueryFilters` sobre `Inversores`). | Mismo esqueleto en la corrección de mes cerrado y en la reasignación. **El aviso previo reutiliza `ResumenReapertura`**, que el controller ya cargaba para los meses cerrados: los números del diálogo son los mismos que los de la reapertura, sin endpoint nuevo. |
| **KOI — `ImportacionExcelKoiService.EscribirConceptosAsync`** | El criterio de escritura por tipo de subgrupo (Manual → `ImporteCalculado = null`; porcentual → `ImporteCalculado` + `ImporteEditadoManual = true`). | Copiado a `EscribirImporteEnConcepto`, que usa la reasignación. Los dos caminos de escritura dejan la fila en el mismo estado. |
| **crm-olvidata — `IndustriasController.ImpactoDelete`** + **la-platense Etapa 3, riesgo 8** | Modal que muestra el impacto real antes de reasignar; y la trampa del índice único que incluye filas soft-deleted. | La reasignación muestra el impacto (suma/fila nueva/porcentual) antes de confirmar. La trampa del índice se resolvió reviviendo la lápida en vez de insertar. |

#### Verificación de las premisas del encargo contra el código
- ✅ **Bloqueo A** (`!concepto.EsInactivo` en `Mensual.cshtml`) y **bloqueo B** (`GuardarConceptoGastoAsync` rechaza `Cerrado`): confirmados tal cual.
- ✅ Índice único `(PeriodoMensualId, SubgrupoId)` **sin filtro** en `AppDbContext`: las lápidas lo ocupan. Confirmado.
- ✅ El E.R. lee `ImporteManual`/`ImporteCalculado` según el tipo del **subgrupo**. Confirmado.
- ⚠️ **El bloqueo A tenía una segunda mitad que el diagnóstico no nombraba, en el servidor:** `GuardarConceptoGastoAsync` buscaba el subgrupo con `_db.Subgrupos.FindAsync(...)`, y **`FindAsync` aplica el query filter global**. Sacar sólo la condición de la vista habría habilitado el campo y el guardado habría fallado con *"Subgrupo no encontrado"*. Corregido con `IgnoreQueryFilters()`. Mismo defecto en `RevertirConceptoAlPorcentajeAsync`, corregido igual.
- ⚠️ **Hay dos reglas de lectura del importe conviviendo en el sistema, no una:** el E.R. mensual mira el tipo del subgrupo, pero `ObtenerResumenAnualAsync`, `DashboardService` e `InversionesService` suman `ImporteCalculado ?? ImporteManual` **sin mirar el tipo**. Coinciden sólo mientras una fila Manual tenga `ImporteCalculado = null`. No se cambió ningún lector (no era alcance), pero **toda escritura nueva de esta etapa deja la fila de forma que las dos reglas den lo mismo**: en la reasignación el origen queda con `ImporteManual = 0` e `ImporteCalculado = null`, y un destino Manual con `ImporteCalculado = null`.

#### 1 · Editar el importe de un concepto histórico (bloqueo A)
- `Mensual.cshtml`: `puedeEditarConcepto` deja de exigir `!concepto.EsInactivo`. El badge **"Histórico"** se conserva.
- `GuardarConceptoGastoAsync`: `IgnoreQueryFilters()` al buscar el subgrupo (ver arriba). Guarda nueva: a un subgrupo dado de baja **sólo se le edita la fila que ya tiene**; nunca se le da de alta un concepto nuevo.
- En la fila de un histórico **no se ofrece "dar de baja del catálogo"** (ya está dado de baja; el servicio lo rechazaría). "Sacar del mes" sí, en meses abiertos y con importe 0, como cualquier otro.
- Un histórico porcentual **no entra al recálculo automático**: `RecalcularInternamente` lista los subgrupos con el query filter, así que los dados de baja nunca se recalculan.

#### 2 · Corregir un gasto de un mes CERRADO (bloqueo B) — criterio 3 de §14.2
- **Sólo Administrador/SuperUsuario.** Doble barrera: la vista sólo habilita el campo con `esAdmin && EsCerrado`, y el servicio revalida el rol contra la base (`EsAdministradorAsync`, que es la misma consulta que ya protegía el cierre, extraída a un helper). La acción `GuardarConcepto` sigue en `GestionOperativa` porque el Encargado la usa en meses abiertos; **la barrera del mes cerrado está en el servicio**.
- **Confirmación previa** (SweetAlert2) en cada guardado: muestra el importe viejo → nuevo del concepto, **qué liquidaciones pendientes se van a recalcular (con nombre)** y **qué liquidaciones pagadas NO se tocan (con neto y fecha de pago)**. Cancelar restaura el campo y no manda nada.
- **`GuardarConceptoEnPeriodoCerradoAsync`**, en una sola transacción:
  1. Foto del resultado **antes** de escribir.
  2. Escribe el importe con el mismo criterio que el mes abierto (Manual → `ImporteManual`; porcentual → `ImporteCalculado` + `ImporteEditadoManual = true`) y hace un primer `SaveChanges` dentro de la transacción, para que el recálculo lea el importe nuevo.
  3. **`RecalcularLiquidacionesPendientesAsync`**: misma fórmula que `CerrarPeriodoAsync` (monto a repartir / 100 × puntos − consumos), pero **sobre los datos congelados de cada liquidación** (sus puntos, sus consumos, su TC). No re-deriva los puntos de las asignaciones vigentes: esto corrige un gasto, no vuelve a cerrar el mes, y re-derivar podría sumar o sacar inversores. **Si el cierre fijó un `MontoAjuste`, manda el ajuste**, igual que en el cierre: el resultado cambia pero lo que se reparte no.
  4. **Las Pagadas se saltean** y se listan como intactas.
  5. `AuditLog` de negocio (`Action = "EdicionPeriodoCerrado"`) con importe/resultado/utilidad por punto antes y después, la lista de recalculadas con neto anterior y nuevo, y la lista de pagadas no tocadas. La auditoría automática del `DbContext` suma además el detalle columna por columna del concepto y de cada liquidación.
- **Después de guardar**, un diálogo (no un toast que se va solo) informa: resultado anterior → nuevo, tabla de recalculadas antes/ahora, **bloque de pagadas no tocadas**, aviso si mandaba el ajuste manual y alertas de neto negativo.
- **Neto negativo** (consumos > bruto recalculado): el cierre lo bloquea, acá **no se bloquea** —impediría corregir un gasto mal cargado— pero se informa por inversor.
- **Qué NO se habilita en un mes cerrado, a propósito:** agregar/sacar filas del mes, dar de baja del catálogo y **volver al %** (recalcularía un importe histórico con el % vigente). El botón de volver al % se oculta en Razor **y** en `marcarOverride()`, que si no lo volvía a mostrar después de cada guardado.
- **Editar directo ≠ reabrir, y conviven.** Reabrir descarta todas las liquidaciones (pagadas incluidas) y deja el mes abierto; esto deja el mes cerrado y respeta las pagadas. El banner del mes cerrado explica la diferencia.
- **Fuera de alcance:** editar las **ventas** de un mes cerrado. §14.1 ítem 3 las nombraba, pero el pedido y el criterio 3 hablan de gastos, y cambiar ventas mueve además todos los porcentuales del mes. `GuardarVentasAsync` sigue rechazando meses cerrados.

#### 3 · Reasignar el subgrupo de un concepto
- Botón por fila (ícono ⇄), **sólo Administrador**, en meses abiertos **y** cerrados, visible sólo cuando la fila tiene importe (y en vivo: `actualizarAccionesConcepto()` lo muestra/oculta y le actualiza el importe tras una edición inline). Abre un diálogo con un selector de destino agrupado por rubro con **todo el catálogo vigente** (`EstadoResultadosDto.SubgruposDestino`, nuevo, armado en el mismo recorrido que la grilla). Al elegir destino muestra el impacto antes de confirmar.
- **`ReasignarSubgrupoConceptoAsync`**, en una sola transacción:
  - Origen: puede estar dado de baja (es el caso de uso). Destino: **tiene que estar vigente**, y su rubro también.
  - **Foto del total de gastos DENTRO de la transacción**, antes de tocar nada.
  - Busca el destino con `IgnoreQueryFilters()` y **nunca inserta a ciegas**: sin fila → la crea; **lápida → la revive** (su importe cuenta como 0 y el viejo no se restaura, igual que `AgregarConceptoAlPeriodoAsync`); viva → **fusión**.
  - Escribe `previo + movido` en el campo **del tipo del destino** (`EscribirImporteEnConcepto`); el origen queda en 0 en los dos campos y como lápida, **en el mismo `SaveChanges`**. No existe estado intermedio con el importe en los dos renglones ni en ninguno.
  - **Verificación, no confianza:** relee el total desde la base dentro de la misma transacción y, si difiere en un centavo, **revierte todo** y lo informa. Es la garantía de que una reasignación nunca crea ni destruye plata.
  - Como el total no cambia, el resultado tampoco, y **las liquidaciones no se tocan** (se informa en el diálogo si el mes está cerrado).
  - `AuditLog` de negocio (`Action = "ReasignacionConcepto"`) con origen, destino, los dos importes previos, el final, si hubo fusión o lápida revivida, y total antes/después. Con eso se deshace a mano reasignando de vuelta.
- **DECISIÓN ante un destino ocupado: SE SUMAN. No se reemplaza ni se rechaza.**
  - **Reemplazar**, descartado: destruye el importe del destino y **el total del mes baja** exactamente en ese monto. Es el modo de falla que todo este sprint viene evitando.
  - **Rechazar**, descartado: deja al cliente sin salida. Si "Otros gastos" ($212 M) tiene que ir a un renglón que ya tiene importe, lo único que le quedaría es poner el destino en 0, mover y volver a cargar a mano: tres pasos propensos a error, y el importe original del destino desaparece del rastro.
  - **Sumar** es la operación semánticamente correcta: dos renglones del catálogo viejo que mapean al mismo renglón nuevo **son el mismo gasto partido en dos**, y consolidarlos es sumarlos. Es además la única de las tres que **conserva el total por construcción**.
  - **Nunca es silenciosa:** el diálogo dice *"Se suman"* y muestra `previo + movido = final` antes de confirmar; el mensaje de éxito lo repite; y la auditoría guarda los dos importes por separado.
- **Un destino porcentual queda con `ImporteEditadoManual = true`** (deja de seguir su % en ese mes). Sin la marca, el próximo "Recalcular %" o la próxima apertura del mes reemplazaría el importe movido por ventas × %. El diálogo lo avisa.

#### Punto del orquestador — recálculo automático al abrir la pantalla (Etapa 19b)
- **Punto 1 (toda edición de un porcentual deja `ImporteEditadoManual = true`) — CUBIERTO en los tres caminos:** mes abierto (`GuardarConceptoGastoAsync`, rama porcentual, ya lo hacía), mes cerrado (`GuardarConceptoEnPeriodoCerradoAsync`) y destino de una reasignación (`EscribirImporteEnConcepto`). El origen de una reasignación queda como lápida en 0, y `RecalcularInternamente` ya hace `continue` sobre lápidas. Los históricos sobre subgrupos dados de baja ni siquiera entran al recálculo.
- **Punto 2 (reabrir un mes para editar) — APLICA, y es un riesgo del camino de REABRIR, no de esta etapa.** Lo editado por los caminos de esta etapa sobrevive a una reapertura (tiene la marca: el recálculo sólo refresca `PorcentajeAplicado`). Pero **reabrir un mes expone al recálculo del GET todas sus filas porcentuales SIN la marca**, que se reescribirían con ventas × % la primera vez que alguien abra la pantalla. **Editar directo en el mes cerrado es el camino seguro**: `Mensual` sólo recalcula meses abiertos y ninguno de los dos caminos nuevos llama a `RecalcularInternamente`.
- **Punto 3 — la política del recálculo NO se tocó.** El diseño no la necesita cambiada.
- **Efecto útil para el hallazgo:** con esto el cliente puede **corregir a mano** las filas ya pisadas en los meses abiertos escribiendo el valor de su Excel; quedan marcadas y dejan de revertirse solas.

#### Cambios por capa
| Capa | Archivo | Cambio |
|---|---|---|
| Application | `Interfaces/IEstadoResultadosService.cs` | `GuardarConceptoGastoAsync` devuelve `ServiceResult<ImpactoLiquidacionesDto?>` (null en mes abierto). Método nuevo `ReasignarSubgrupoConceptoAsync`. DTOs nuevos: `ImpactoLiquidacionesDto`, `LiquidacionImpactadaDto`, `ReasignacionSubgrupoDto`, `SubgrupoDestinoDto`; `EstadoResultadosDto.SubgruposDestino`. |
| Infrastructure | `Services/EstadoResultadosService.cs` | Helpers `ImporteAplicadoDe` / `EscribirImporteEnConcepto` / `NombreUsuarioAsync` / `EsAdministradorAsync` (la consulta de rol del cierre, extraída; `PuedeCerrarPeriodoAsync` delega en él). `ObtenerAsync` arma `SubgruposDestino`. `GuardarConceptoGastoAsync` (bloqueo A en servidor + bifurcación a mes cerrado). Nuevos `GuardarConceptoEnPeriodoCerradoAsync`, `RecalcularLiquidacionesPendientesAsync`, `ReasignarSubgrupoConceptoAsync`. `RevertirConceptoAlPorcentajeAsync`: `IgnoreQueryFilters()` al buscar el subgrupo. |
| Web | `Controllers/EstadoResultadosController.cs` | `GuardarConcepto` devuelve el bloque `impacto`. Acción nueva `ReasignarConcepto` con `[Authorize(Policy = "SoloAdministrador")]` **a nivel acción**. `MapearAViewModel` mapea `SubgruposDestino`. **Mapa atributo→método re-verificado completo después de insertar**: las 17 acciones conservan su bloque. |
| Web | `Models/EstadoResultadosViewModels.cs` | `ErMensualViewModel.SubgruposDestino`. |
| Web | `Views/EstadoResultados/Mensual.cshtml` | Banderas nuevas `puedeEditarCerrado`, `puedeCargarImportes`, `puedeReasignar` (se respetan `esAdmin` y `puedeGestionar`, no se unificaron). Banner de mes cerrado; bloque oculto del aviso previo; botón ⇄ por fila; columna de acciones más ancha; JS: `confirmarEdicionCerrada`, `mostrarImpactoLiquidaciones`, `enviarConcepto` (el POST de la edición inline, extraído sin cambios para poder anteponerle la confirmación), diálogo de reasignación, `escHtml`. Los destinos viajan con `JsonSerializer` (invariante; lección de la Etapa 24, punto 2.3). |

#### Evidencia de build
- `dotnet build KoiDumplings.slnx -c Debug` → **Compilación correcta, 0 errores**, 9 advertencias, **todas preexistentes** (8× NU1902 MailKit/MimeKit — VUL-001; 1× CS0114 `HomeController.StatusCode`). Ninguna nueva. No había ninguna instancia de la app corriendo que bloqueara los `.dll`.
- El primer build dio 4 errores en `Mensual.cshtml` (tipo `LiquidacionDescartadaDto` sin `using` en la vista); corregido con el nombre calificado y re-compilado.
- **Sin smoke test funcional** (regla del rol). No hay proyecto de tests. Guía manual abajo.

#### Barrido legal (ítem 23) — revalidado
- `git diff` sobre las líneas agregadas: **cero** menciones a `VentasA`, `VentasB`, `Informal`, `Facturado`, `NoFacturado`, `s/impuesto`, `c/impuesto`, `PctVentasA`, `TicketPromedioA/B`.
- Superficie nueva: `Mensual` (`GestionOperativa`), `GuardarConcepto` (`GestionOperativa`) y `ReasignarConcepto` (`SoloAdministrador`). **El rol Inversor no entra a ninguna.** Los nombres y netos de inversores que ahora viajan en la respuesta de `GuardarConcepto` **sólo se generan en meses cerrados, que el servicio sólo le permite al Administrador**: el Encargado tampoco ve la parte de inversores.

#### Riesgos y supuestos
- **Las liquidaciones pagadas quedan desfasadas del resultado después de una corrección, por diseño.** Es lo que pide el criterio 3 (esa plata ya se transfirió). La pantalla lo dice; compensar la diferencia con esos inversores es una decisión operativa aparte y el sistema no la toma solo.
- **Una fusión hereda el importe que el destino tenía en pantalla.** Si ese importe es uno de los porcentuales pisados por el recálculo automático (hallazgo del orquestador), la fusión lo congela sumado. El diálogo muestra el valor previo antes de confirmar; conviene corregir el destino **antes** de fusionar.
- **No se re-midió producción.** Las cifras del encargo (104 conceptos en cerrados por $687.845.959, 29 en abiertos por $97.281.568, 6 subgrupos viejos con importe sin equivalente) son del diagnóstico del orquestador. La Etapa 22 contaba 11 subgrupos viejos sin migrar; no se contradicen (no todos tienen importe).
- **Reabrir un mes lo expone al recálculo automático** para las filas porcentuales sin marca (ver punto 2 del orquestador). No es de esta etapa pero pesa sobre la decisión de "reabrir vs editar directo".
- **Concurrencia:** dos administradores reasignando el mismo renglón a la vez. La verificación de total dentro de la transacción protege el invariante financiero; el peor caso es un error claro para el segundo. Aceptado para un sistema de un local.
- El aviso previo de un mes cerrado lista pendientes y pagadas; si el cierre tuvo `MontoAjuste`, el aviso lo menciona en general y el diálogo posterior lo informa con el monto.

#### Guía de prueba manual (para el dueño del estudio / QA)
**Preparación:** anotar antes, para un mes cerrado con liquidaciones pagadas y pendientes, el Total de Gastos, el Resultado y el neto de cada liquidación (pantalla Liquidaciones).
1. **A — histórico en mes abierto:** como Administrador, abrir un mes abierto con un concepto de badge "Histórico". El importe tiene que ser un campo editable. Cambiarlo y salir: tilde verde, y el Total de Gastos y el Resultado se actualizan sin recargar. Recargar: el valor sigue.
2. **A — sin baja del catálogo:** en esa misma fila, con importe 0, tiene que aparecer "sacar del mes" (ojo tachado) y **no** el tacho de "dar de baja".
3. **B — Encargado:** con un Encargado, abrir un mes cerrado: los importes son texto, no campos, y no hay banner ni botón ⇄. Forzar `POST /EstadoResultados/GuardarConcepto` sobre un mes cerrado → `{ success:false, "solo un Administrador..." }`.
4. **B — banner:** como Administrador en un mes cerrado: aparece el banner amarillo con la cantidad de pendientes y pagadas, y la diferencia con "Reabrir período".
5. **B — confirmación previa:** cambiar un importe y salir del campo. Tiene que aparecer el diálogo con viejo → nuevo, los nombres de las pendientes y las pagadas con neto y fecha. **Cancelar:** el campo vuelve al valor anterior y **en la base no cambió nada** (recargar).
6. **B — guardar:** repetir y confirmar. Aparece "Corrección guardada" con resultado anterior → nuevo, tabla de recalculadas y bloque de **pagadas no tocadas**.
7. **B — verificación (lo importante):** en *Liquidaciones*, las **pendientes** del mes cambiaron a `puntos × (resultado nuevo / 100) − consumos`, y las **pagadas tienen exactamente el mismo neto que antes**, al peso. El período sigue **Cerrado**.
8. **B — auditoría:** en *Auditoría* hay una fila `EdicionPeriodoCerrado` con el importe viejo y nuevo y las dos listas.
9. **B — ajuste manual:** en un mes cerrado con ajuste manual en el cierre, corregir un gasto: el diálogo tiene que decir que el monto a repartir estaba fijado y las pendientes **no** cambian.
10. **B — sin "volver al %":** en un mes cerrado, editar un porcentual (Regalías, por ejemplo). Después de guardar, **no** tiene que aparecer el botón ↺ de volver al %.
11. **C — reasignar a un renglón vacío:** en un mes con "Otros gastos" (histórico), tocar ⇄, elegir un destino que **no** tenga importe en el mes. El diálogo dice "queda en $X". Confirmar: el origen desaparece de la grilla, el destino tiene $X y **el Total de Gastos es idéntico al de antes**.
12. **C — fusión:** reasignar a un destino que **ya tiene** importe. El diálogo tiene que decir **"Se suman"** con `previo + movido = final`. Confirmar: el destino queda en la suma y el **Total de Gastos no cambia**.
13. **C — manual → porcentual (la trampa E20):** reasignar un gasto de un subgrupo Manual a uno porcentual. El destino queda con el importe (no en 0) y marcado como escrito a mano (borde naranja); **el total no cambia**. Recargar la página (dispara el recálculo automático en un mes abierto): **el importe sigue igual**.
14. **C — lápida:** en un mes abierto, sacar del mes un concepto vigente con importe 0 (ojo tachado). Después reasignar otro concepto **a ese mismo destino**: tiene que funcionar, sin error de base de datos, y el destino vuelve a la grilla con el importe movido.
15. **C — mes cerrado:** reasignar en un mes cerrado. El mensaje final dice que las liquidaciones no se tocaron; verificarlo en *Liquidaciones* (ningún neto cambió).
16. **C — vista anual y Dashboard:** después de 11 a 15, el Total de Gastos de esos meses en *Historial de Resultados* y en el *Dashboard* es **el mismo que en el E.R. mensual**.
17. **C — permisos:** con un Encargado no aparece el botón ⇄; forzar `POST /EstadoResultados/ReasignarConcepto` → **403**.
18. **Barrido legal:** con un Inversor, recorrer Dashboard, Mes Actual, Mi Inversión, Reporte e Historial: **ningún** dato facturado/informal (A/B).

#### Checklist de salida para merge
- [x] Build 0 errores, 0 advertencias nuevas
- [x] Criterio 3 de §14.2 implementado textual: guarda, recalcula pendientes, pagadas intactas e informadas, auditoría
- [x] Barrera de mes cerrado y de reasignación en el **servicio**, no sólo en la vista
- [x] Confirmación previa con números reales antes de corregir un mes cerrado
- [x] Reasignación: índice único resuelto (lápida revivida), campo del tipo del destino, total verificado dentro de la transacción con reversión
- [x] Toda escritura sobre un porcentual deja `ImporteEditadoManual = true` (punto 1 del orquestador)
- [x] Política del recálculo automático **sin tocar**
- [x] Bloques de atributos del controller verificados acción por acción tras insertar
- [x] Barrido legal revalidado
- [x] Sin migraciones
- [ ] **Commit y deploy: deliberadamente SIN hacer**
- [ ] Prueba manual de los 18 pasos
- [ ] Decidir con el dueño la política del recálculo automático (hallazgo del orquestador): pesa sobre "reabrir vs editar directo"


### Etapa 24 — Ajustes de la prueba manual de la Entrega 1 (2026-09-10)
- Entrada: lote de ajustes del **dueño del estudio probando a mano la Entrega 1**, sobre las Olas 1 y 2 ya implementadas (Etapas 22 y 23) y deployadas. Alcance base en `1-analista-funcional.md` §16, `2-disenador-funcional.md` §15 y `3-arquitecto-mvc.md` §13. **Gate de presupuesto SALTEADO por decisión explícita del dueño**, igual que en las dos olas anteriores — registrado, no omitido.
- **Sin migraciones EF**: ni de esquema ni de datos. Los campos nuevos de esta etapa son propiedades de DTO calculadas en memoria, no columnas.
- **Los meses históricos no se tocan.** Ningún cálculo financiero se modificó: los dos indicadores nuevos en pesos (2.6) se **agregan** con la fórmula que ya usaba el KPI acumulado, y el cálculo en dólares queda intacto (P-B05).
- **El barrido legal de la Ola 2 (E1, ítem 23) se revalidó** después de tocar el Dashboard. Ver el detalle en 3.1: la etapa **reduce** la superficie A/B del rol Inversor, no la amplía.

**Escaneo de reutilización (`catalogo.yml` + `docs/*/definiciones/5-implementador.md` de todos los proyectos):** 3 hits reutilizados y **1 patrón nuevo agregado al catálogo**.

| Origen | Qué se tomó | Cómo se aplicó |
|---|---|---|
| **KOI — `.btn-revertir-concepto` (Etapa 18)** | Botón que ya se renderizaba siempre y se mostraba/ocultaba con `d-none` desde el mismo AJAX de edición inline. | Es exactamente el mecanismo de **2.2**. No se inventó nada: los botones de "sacar del mes" y "dar de baja" pasan a comportarse como el de reversión al %, que vive en la celda de al lado. |
| **KOI — `AyresTokenCache` / PAT-024 (Etapa 21)** | La lección de ciclos de vida: cache Singleton + servicio Scoped, con el error clásico documentado. | Es el mismo razonamiento de **2.1**: la cola es Singleton porque tiene que sobrevivir al request; el worker crea el scope. Se escribió el registro con el mismo comentario de "ORDEN DE VIDA CRÍTICO". |
| **KOI — `MesActual/Index` (chart de canales)** | `ToString(CultureInfo.InvariantCulture)` al interpolar números en JS. | Es la corrección de **2.3**: la misma vista lo hacía bien y el Dashboard lo hacía mal. Se copió el criterio a los 4 gráficos del Dashboard. |
| **NUEVO — PAT-025** | — | Se agregó al catálogo la **cola de trabajo en segundo plano con scope propio** (ver 2.1): es genuinamente portable a cualquier proyecto del estudio con Identity + envío de mails, y el bug que corrige es del baseline, no de KOI. |

---

#### 1.1 · Falta el rol Encargado al crear usuarios (BLOQUEANTE)
- `UsersController.GetAssignableRoles()`: SuperUsuario pasa a `[Administrador, Encargado, Inversor]`; el resto (Administrador), a `[Encargado, Inversor]`.
- **El criterio de escalada del método se respetó y se documentó**: la lista quedó alineada con `CanManageUser()`, que es quien decide a quién se puede **editar**. Ese método ya dejaba a un Administrador gestionar Encargados pero no SuperUsuarios ni otros Administradores; ahora la lista de "qué puedo crear" dice lo mismo que la de "a quién puedo tocar". Un Administrador sigue sin poder crear un SuperUsuario ni otro Administrador.
- **Defecto silencioso corregido de paso, y es el más grave de este punto.** `GetAssignableRoles()` también alimenta el combo de **Editar**. Como `Encargado` no estaba en la lista, editar un usuario Encargado (por ejemplo para cambiarle el mail) renderizaba un `<select>` sin su valor actual: el navegador seleccionaba la primera opción (`Inversor`) y **guardar lo degradaba de rol sin avisar**. Es exactamente el estándar de QA de `32-estandares-qa-implementador` ("todo combo de una vista de Editar se inicializa con el valor ya asignado"). Con el rol en la lista, el tag helper `asp-for="Rol"` lo selecciona solo.

#### 1.2 · `/System` vuelve al menú del Administrador (BLOQUEANTE)
- `SystemController`: `RequireSuperUsuario` → **`RequireAdministracion`**. Revierte el ítem 3 de la Ola 1 (Etapa 22, A4) por pedido explícito posterior. Queda escrito en el XML doc de la clase que es una reversión y por qué la pantalla es segura para el Administrador (remitente de mail, health checks y BaseUrl de Ayres; las credenciales sólo viven en `appsettings.Production.json`).
- **El link aparece UNA sola vez para cada rol, y esa era la trampa.** El bloque "Sistema" del sidebar lo ven Administrador **y** SuperUsuario; el bloque "Super Usuario" tenía además su propio link al mismo destino. Agregarlo arriba sin tocar abajo le habría dejado dos "Sistema" al SuperUsuario. **Se movió**, no se duplicó: ahora vive sólo en la sección "Sistema" y el bloque "Super Usuario" conserva únicamente "Auditoría". Queda un comentario en el layout advirtiéndolo para la próxima pasada.
- El pie de la card de health checks sigue diciendo que el endpoint `/health` requiere SuperUsuario, **y sigue siendo cierto**: esa ruta tiene su propio `.RequireAuthorization("RequireSuperUsuario")` en `Program.cs` y no se tocó. El Administrador usa el botón "Verificar ahora", que va por la acción del controller.

#### 2.1 · Mail de recuperación de contraseña asincrónico — y el mismo defecto en otros dos lugares
- **Componente nuevo y reutilizable: `IBackgroundJobQueue` + `BackgroundJobWorker`** (PAT-025). Cola en memoria (`Channel` acotado a 200, `DropWrite`), Singleton; el worker es un `BackgroundService` que drena de a un trabajo por vez y **crea un scope de DI propio para cada uno**.
- **Por qué no alcanzaba con `Task.Run`, que es lo que el proyecto venía haciendo:** `_ = Task.Run(() => _servicioScoped.HacerAlgoAsync())` captura en la clausura un servicio **scoped** del request. Al terminar el request, ASP.NET dispone el scope y con él el `DbContext`; la tarea sigue corriendo contra objetos dispuestos. No falla siempre: **falla cuando pierde la carrera**, que es la peor forma de fallar. Y sin `catch`, no deja rastro.
- **`AccountController.ForgotPassword`**: el token y el link se siguen armando **dentro del request** (dependen de `UserManager` y de `Url.Action`, que necesita host y `PathBase` — el sitio corre bajo `/koi`). Al trabajo encolado viajan sólo strings: destinatario, asunto y HTML ya renderizado. Se sacó `IEmailService` del controller: ya no se usa desde el request.
- **La anti-enumeración quedó MÁS fuerte, no igual.** Antes la respuesta era idéntica en texto pero no en tiempo: la rama "email existente" esperaba al SMTP (segundos) y la inexistente contestaba al instante. Eso delata la cuenta igual. Ahora las dos ramas hacen exactamente el mismo trabajo medible —una consulta por email, común a las dos— y el único paso lento salió del request. Lo que queda de diferencia es `GeneratePasswordResetTokenAsync`, que es criptografía en memoria sobre el usuario **ya cargado** (no vuelve a la base): microsegundos, por debajo del ruido de red.
- **Los fallos ahora se ven.** El worker loguea cada trabajo completado con su duración y cada excepción como `Error` con el nombre del trabajo. Encolar sobre una cola llena también se loguea como `Error` en vez de descartarse en silencio.

#### 2.1b · El fire-and-forget del cierre SÍ estaba roto (defecto preexistente en producción)
- **Confirmado.** `EstadoResultadosController.ConfirmarCierre` hacía `_ = Task.Run(() => _notificaciones.EnviarNotificacionCierreAsync(id))`. `INotificacionCierreService` está registrado **`AddScoped`** y su constructor toma `AppDbContext` (scoped) y `UserManager` (scoped). La clausura capturaba la instancia del request. Al devolver el redirect, el scope se dispone y el envío sigue corriendo contra un `DbContext` dispuesto → `ObjectDisposedException` **silenciosa**: el período queda cerrado, las liquidaciones generadas y **los inversores sin mail**, sin una sola línea en el log. Es más grave que el ítem encargado, porque es el aviso de pago a 15 inversores.
- **Y no era uno solo: eran dos.** El barrido de `Task.Run(` sobre todo el repo encontró el mismo patrón en **`NotificacionCierreController.EnviarMasivo`** — el botón "Enviar a los N" que se agregó en la Ola 2 (C4), sobre el mismo servicio scoped. Corregido igual.
- Los dos pasan por la cola nueva: resuelven `INotificacionCierreService` del `IServiceProvider` del scope propio y sólo capturan el `periodoMensualId`. `_notificaciones` se conserva en `NotificacionCierreController` porque ahí sí se usa dentro del request (la revalidación del preview antes de encolar); se **quitó** de `EstadoResultadosController`, donde el fire-and-forget era su único uso.
- **`ErrorNotifier.NotifyError` se evaluó y NO se tocó, a propósito.** También usa `Task.Run`, pero lo que captura es `IEmailService`, que es sin estado (`IOptions<SmtpSettings>` + logger, no toca el `DbContext` y no es `IDisposable`): disponer el scope no lo rompe. Además ya tiene su propio `try/catch` con logging. Cambiarlo sería refactor cosmético sobre el manejador global de excepciones, que es el peor lugar para tocar sin motivo.

#### 2.2 · Los botones de un concepto aparecen solos al poner el importe en 0 (pedido 11)
- `Views/EstadoResultados/Mensual.cshtml`: los botones "sacar del mes" y "dar de baja del catálogo", más el candado, se **renderizan siempre** para un concepto editable y lo que cambia es la clase `d-none`. Es el mismo mecanismo que ya usaba `.btn-revertir-concepto` en la celda del % de la misma fila.
- Helper nuevo `actualizarAccionesConcepto(row, importe)`, llamado desde los **tres** puntos donde el importe aplicado puede cambiar sin recarga: el `done` de la edición inline (que es donde el usuario escribe el 0), el de "volver al % de referencia", y dentro de `pintarImporteConcepto()` — que cubre de una vez "guardar ventas" y "recalcular %".
- **La llamada va ANTES de los early-returns de `pintarImporteConcepto`**: ese helper no repinta un input con foco o con guardado en curso, pero el importe aplicado en el servidor ya cambió y los botones tienen que reflejarlo igual.
- **Funciona en los dos sentidos**, como pedía el encargo: si el concepto vuelve a tener importe, los botones se ocultan y reaparece el candado.
- **Esto NO es la guarda y el código lo dice con todas las letras.** El servicio sigue revalidando importe 0 en `QuitarConceptoDelMes` y `DarDeBajaSubgrupo`. Que ahora los botones existan ocultos en el DOM no cambia nada del lado del servidor: forzar el POST sigue devolviendo error explícito.
- Se usa un margen de medio centavo (`< 0.005`) y no `== 0`: un residuo de un concepto porcentual dejaría la fila mostrando "$ 0" con el botón escondido.

#### 2.3 · La torta "Resultado vs Gastos" — la causa real no era el color
- **La premisa del encargo era un síntoma, no la causa.** Los colores ya eran distintos en el código (`['#22c55e', '#ef4444']`, verde y rojo). El bug estaba en los **datos**.
- **Causa raíz:** los gráficos del Dashboard interpolaban números crudos dentro de un array literal de JS — `data: [@(ventasTot - gastosTot), @gastosTot]`. La app corre con cultura fija **es-AR** (`Program.cs`, `UseRequestLocalization`), así que Razor rinde los decimales **con coma**. Un `decimal` de EF conserva escala 2, así que **siempre** sale con coma: `data: [-1383000,50, 63131109,00]` no son 2 números, son **4 elementos**. Chart.js recicla el array de colores por índice (`i % length`), así que la porción grande de "Gastos" (índice 2) volvía a caer en el verde del índice 0: **las dos porciones visibles del mismo color**. Exactamente lo reportado.
- **El mismo bug estaba en los otros dos gráficos de la vista**, sin haber sido reportado: `chartCanal` (torta de canales) recibía 6 valores con 3 colores y `chartTicket` (barras de ticket por canal) lo mismo — las porciones se pintaban corridas respecto de las badges de la leyenda de abajo. Corregidos los tres. `chartGastosRubro` ya estaba bien (usaba `JsonSerializer`), y `MesActual/Index` también (`ToString(InvariantCulture)`): el criterio existía en el proyecto, sólo no se había aplicado acá.
- **Corrección de fondo:** todo número que va a un gráfico se serializa invariante. Queda un comentario en la vista con la regla, porque es el tipo de bug que vuelve.
- **Además, la torta estaba conceptualmente rota con resultado negativo**, que es justo el caso del cliente (rentabilidad −2,2 %). Chart.js dibuja el valor negativo como un arco positivo, así que una **pérdida** se veía pintada de verde y rotulada "Resultado". Ahora: con resultado negativo la porción es **ámbar** (`#f59e0b`, el mismo "atención" del resto de la app) y se rotula **"Pérdida"**; con resultado positivo sigue verde. Verde/ámbar contra rojo, los tres de la paleta del sistema y con contraste suficiente en tema claro y oscuro; el borde toma el fondo de la card según el tema, igual que la torta de canales.
- El tooltip pasa a calcular el % **sobre las ventas del mes**, que es el todo real que la torta reparte. Sobre la suma de las porciones daba un número sin sentido apenas el resultado era negativo.

#### 2.4 · "Evolución diaria": las dos series en un solo gráfico, con doble eje
- Se eliminó el selector `$ Plata / Cubiertos` de la Ola 2. Las dos series se dibujan juntas: **barras** para la plata contra el eje izquierdo, **línea** para los cubiertos contra el eje derecho.
- **El doble eje Y no es decoración.** Las escalas son de órdenes de magnitud distintos (millones de pesos contra decenas de cubiertos): sobre un eje único la línea de cubiertos queda pegada al cero y no se lee. Cada eje va rotulado y **pintado del color de su serie**, así que no hay que adivinar cuál es cuál; la leyenda de Chart.js queda visible (antes estaba en `display:false`, porque con una sola serie sobraba).
- `grid.drawOnChartArea: false` en el eje derecho: sin eso se superponen dos rejillas sobre el mismo dibujo y el fondo queda rayado. `order` invertido para que la línea se dibuje por encima de las barras.
- Los dos colores (`#2b9de4` azul, `#f59e0b` ámbar) son los que ya usan las tarjetas de ventas y de cubiertos de más arriba en la misma pantalla, y los dos tienen contraste suficiente en tema claro y oscuro.
- **La caché de 5 minutos se conservó sin tocar**: el cambio es todo del lado del dibujo, el endpoint `SerieDiaria` no se modificó. Su policy `GestionOperativa` tampoco (E1).

#### 2.5 · La rentabilidad en pesos y en dólares — LA PREMISA NO SE SOSTIENE
- **No se implementó como venía pedido, y hay que decírselo al dueño.** El KPI "Rentabilidad" del Dashboard es `Resultado / Ventas Totales × 100` **del mismo mes** (`DashboardService`, línea 69). Numerador y denominador son pesos del mismo período: dividir los dos por el mismo tipo de cambio da **exactamente el mismo número**. Mostrar "Rentabilidad U$D" al lado sería el mismo −2,2 % repetido.
- La decisión de P-B05 (`1-analista-funcional.md` §16.8) es real pero aplica a **otra cosa**: al recupero/rentabilidad **del inversor**, que acumula muchos meses convertidos cada uno al TC de su propio mes. Ahí sí las dos monedas divergen — y ahí sí se muestran las dos (ver 2.6).
- **Lo que sí faltaba era decir qué mide ese KPI**, que es de donde salió la confusión: un inversor entrando a "Rendimiento Histórico" lee "Rentabilidad" y asume que es la suya. Se agregó el subtítulo "del total vendido" y un `title` que aclara que es el margen del local sobre las ventas del mes, no el rendimiento de su inversión.
- **Contrapropuesta concreta para el dueño:** si lo que quiere es ver su rendimiento en las dos monedas al entrar como inversor, eso ya existe y está a un click — *Mi Inversión* y *Reporte de rendimiento*, los dos con ambas monedas y la leyenda que explica la brecha. Si quiere además un acceso desde el Dashboard, es un ítem nuevo (una tarjeta con el recupero propio en la pantalla del inversor) y se estima aparte.

#### 2.6 · Recupero en pesos y en dólares en todos los lugares donde el inversor cobra
- **Regla del dueño aplicada como barrido, no como parche puntual.** Lugares evaluados y qué se hizo en cada uno:

| Superficie | Rol que la ve | Decisión |
|---|---|---|
| **`MiInversion/Index` — tarjetas** | Inversor / Admin | Ya tenía las dos monedas. **Rediseñada** la grilla (ver 3.3) para que cada par U$D/$ quede junto. |
| **`MiInversion/Index` — gráfico "Evolución del recupero"** | Inversor / Admin | **TOCADO.** Serie nueva de recupero acumulado **en pesos**, punteada y ámbar, sobre el mismo eje (las dos son % del mismo capital): la brecha se ve abrirse mes a mes, que es justo lo que el ítem 25 quería comunicar. |
| **`MiInversion/Index` — tabla de liquidaciones** | Inversor / Admin | **TOCADO.** Las columnas "Renta" y "Recupero acum." muestran las dos monedas (U$D arriba, $ abajo). Las columnas "Neto $" y "Neto U$D" ya estaban. |
| **`MiInversion/Reporte`** | Inversor / Admin | **TOCADO.** Segunda línea en pesos en "Utilidad acumulada", "% Recupero" y "Rentabilidad mensual", más la misma leyenda que Mi Inversión. El **dólar sigue siendo la unidad del reporte** (número grande, eje del gráfico, comparativa de mercado): es la fidelidad al PDF aprobado, y el pedido era agregar la lectura en pesos, no cambiar la unidad. En el gráfico de pagos los pesos van en el **tooltip**, no como serie: dos escalas distintas en un gráfico de barras no se leen. |
| **`Liquidaciones/Index`** | **Admin únicamente** (`RequireAdministracion`) | **DESCARTADO — ya cumple.** Muestra Neto en $ y en U$D. El inversor no entra acá. |
| **Email de notificación de cierre** | Inversor | **DESCARTADO — ya cumple.** Muestra "Neto a cobrar" en $ y "Neto USD" con el TC del mes. |
| **`Dashboard/Index` ("Rendimiento Histórico")** | Inversor / Admin | **DESCARTADO — no informa plata cobrada por el inversor.** Son ventas, gastos y resultado del **local**. Ver 2.5. |
| **`MesActual/Index`** | Inversor | **DESCARTADO — mismo motivo.** Ventas del local del mes en curso. |
| **`EstadoResultados/Anual` ("Historial de Resultados")** | Inversor / Admin | **DESCARTADO — mismo motivo.** Resultado del local por mes, no reparto. |
| **`RepartoGeneral/Index`** | **Admin únicamente** | **DESCARTADO** — el inversor no entra, y es utilidad por punto del local, no lo cobrado por una persona. |

- **El cálculo en dólares NO se tocó** (P-B05). Los indicadores en pesos se calculan con **exactamente la misma fórmula** que ya usaba el KPI acumulado `RecuperoPesosPorc`: cada liquidación sobre el capital convertido al TC de **su propio mes**. Escrito de otra forma, la última fila del historial no coincidiría con el KPI del encabezado y el inversor vería dos números distintos para lo mismo — que es justo la inconsistencia que el ítem 25 vino a cerrar.
- El acumulado en pesos se lleva como *running total* dentro del **mismo recorrido** que ya llevaba el de dólares, sin una segunda pasada, y se redondea recién al armar la fila (no se suman porcentajes ya redondeados).
- **Null y no 0 cuando falta el tipo de cambio.** Un "0,00 %" en las primeras filas se leería como "no cobré nada", cuando lo que pasa es que falta el TC de ese mes. Y si **ningún** mes tiene TC, la serie del gráfico no se dibuja: una línea plana en cero mentiría. Nunca se convierte al dólar de hoy — es literalmente lo que §16.8 dice que no hay que hacer.
- Sin migración: son propiedades de DTO calculadas en memoria a partir de datos que ya estaban.

#### 3.1 · Dashboard — distribución de tarjetas (rol de diseño UX/UI)
- **Fila hero: de 5 tarjetas a 4.** Tenía `col-6 col-md-4 col-xl` con 5 ítems: 2+2+**1** en mobile, 3+**2** en md. Siempre quedaba una tarjeta suelta con el hueco al lado. La quinta ("Resultado USD") **no se eliminó**: se unificó con la tarjeta "Resultado del mes" de la fila de ventas, que ya mostraba $ y U$D juntos y ahora se lleva también el tipo de cambio y el link a cargarlo. Quedan `col-6 col-lg-3`: 2×2 en mobile, 1×4 en desktop.
- **Fila de KPIs de venta: 7/6 → 6 para los dos roles.** Era el peor caso de la pantalla: **7 tarjetas para el Administrador y 6 para el Inversor**. 7 no tiene ningún divisor ≥ 2, así que **ninguna** grilla de 2, 3 o 6 columnas lo puede llenar — y con dos conteos distintos por rol, cualquier grilla que arreglara uno rompía el otro. Se sacó la tarjeta "Ventas s/impuesto", que era **la única condicionada por rol** y por lo tanto la causa de la disparidad.
  - **No se pierde el dato:** `VentasSinImpuestos` es literalmente `VentasA`, y ese número ya está —con su desglose por canal y su total— en la tabla "Ventas por canal" de abajo, columna "S/impto. (A)", que el Administrador ve entera. El "% del total" que mostraba la tarjeta se movió al pie de esa columna, así que tampoco se pierde.
  - Las 6 restantes pasan de `col-6 col-sm-4 col-xl-2` a **`col-6 col-md-4 col-xl-2`**: 2, 3 y 6 columnas, los tres divisores exactos de 6. El salto de `sm` a `md` es deliberado: con `sm-4` entraban 3 tarjetas desde 576 px y los importes de 8 cifras se partían.
- **Sección Gastos: anchos calculados en vez de fijos.** Las cards del gráfico de rubros y de la torta son **condicionales**; con `4/5/3` fijos, un mes sin gastos cargados dejaba `4 + 3` (5 columnas de aire) y un mes sin ventas dejaba `4 + 5`. Ahora los tres casos posibles suman 12 exacto.
- La torta "Resultado vs Gastos" sube de 220 px a 320 px: iba al lado de un gráfico de 420 px y, con `h-100`, la card se estiraba con el dibujo chiquito flotando en el medio. Ahora comparten línea de base.
- **Revalidación del barrido legal (E1, ítem 23) tras tocar el Dashboard.** Todas las superficies A/B siguen dentro de `@if (!esInversor)`: la columna "S/impto. (A)" en sus 4 filas, el nuevo % del pie, y la etiqueta "Ventas c/impuesto" vs "Ventas del mes". El gráfico de evolución diaria (que rotula "Facturado") sigue detrás de `muestraSerieDiaria`, que incluye `!esInversor`, **y** su endpoint conserva la policy `GestionOperativa`. **La etapa reduce la superficie A/B del Inversor en vez de ampliarla**: la tarjeta que se sacó era admin-only, y ninguna etiqueta nueva menciona el corte.
- No se inventó lenguaje visual: todo son clases de grilla de Bootstrap y las `card`/`ov-*` que la pantalla ya usaba.

#### 3.2 · Mes Actual — distribución de tarjetas
- Las 4 tarjetas pasan de `col-6 col-md-3` a **`col-6 col-lg-3`**. El conteo ya era par (2×2 en mobile, 1×4 en desktop) desde la Ola 2 y eso no cambia; **lo que se corrige es el tramo `md`** (768–991 px, tablet vertical), donde entraban 4 tarjetas de ~190 px y los importes de 8 cifras se partían en dos renglones. La grilla se mantiene 2×2 hasta los 992 px.
- Es el único cambio de la pantalla: el resto ya cumplía los criterios.

#### 3.3 · Mi Inversión — distribución de tarjetas
- **Se eliminó el `offset-md-6`, que era media fila de espacio muerto.** Antes eran dos filas: una de 4 tarjetas y otra de 2 empujadas a la derecha con un offset. En desktop quedaba medio ancho vacío; en mobile el bloque se partía y las dos monedas del mismo indicador quedaban lejos una de la otra.
- **Ahora es UNA grilla de 6 tarjetas hermanas con `col-6 col-lg-4`.** 6 es divisible por 2 y por 3, así que la fila se llena exacta en los dos casos: 3 filas de 2 en mobile, 2 filas de 3 en desktop. Ninguna tarjeta sola, ningún hueco, ningún offset.
- **El orden se eligió para el ancho más chico**, que es donde el dueño lo viene pidiendo: en mobile cada par cae junto — Dividendos U$D al lado de Dividendos $, Recupero U$D al lado de Recupero $.
- **Las dos tarjetas de recupero tienen ahora la misma estructura interna** (valor, barra de progreso, escala 0–100 % y el aviso de capital recuperado). Antes sólo la de dólares tenía barra, así que era el doble de alta que su hermana y con `h-100` la otra quedaba con un agujero abajo.
- Las tarjetas de dividendos ganan una línea de contexto ("cada pago al dólar de su mes" / "lo que te depositaron") que además empareja la línea de base.

---

#### Evidencia de build
- `dotnet build` desde la raíz → **Compilación correcta, 0 errores**, 9 advertencias, **todas preexistentes** y ninguna introducida por esta etapa: 8× NU1902 (MailKit 4.14.1 / MimeKit 4.14.0 — VUL-001, pendiente) y 1× CS0114 (`HomeController.StatusCode`).
- Las vistas Razor se compilan en build (no hay `RuntimeCompilation` en el `.csproj`), así que los 0 errores cubren los `.cshtml`. Se aprovechó: un `@{` mal anidado dentro del bloque `else` de `Dashboard/Index.cshtml` lo cazó el compilador (RZ1010), no el navegador.
- **Sin migraciones**: no se corrió `dotnet ef`. Esta etapa no agrega ni cambia ninguna columna.
- **Sin smoke test funcional** (regla del rol). No hay proyecto de tests en el repo. La guía de prueba manual va abajo.

#### Riesgos y supuestos
- **2.5 no se implementó como venía pedido.** La premisa no se sostiene contra el código: el KPI de rentabilidad del Dashboard es un cociente del mismo mes y no cambia de valor entre monedas. Requiere confirmación del dueño (ver la contrapropuesta en 2.5). **Es el ítem del lote que puede volver.**
- **La cola de trabajos es en memoria.** Si el sitio se recicla (IIS) con trabajos pendientes, esos mails se pierden. Es aceptable para lo que se encola hoy —avisos reintentables a mano desde "Hist. notif. cierre"— pero **nada que deba sobrevivir a un reinicio puede ir por acá**. Está documentado en el propio archivo.
- **El fix de 2.1b cambia el comportamiento observable del cierre bajo carga**: mails que antes desaparecían en silencio ahora se envían de verdad. Si algún período viejo se cerró sin que salieran los mails, el guard de deduplicación de `EnviarNotificacionCierreAsync` sigue vigente y no los va a mandar solo — hay que reenviarlos a mano desde el historial.
- **La corrección de 2.3 cambia lo que se ve en los tres gráficos del Dashboard**, no sólo el color: los valores estaban mal repartidos desde antes. Los números de las tarjetas y las tablas **siempre estuvieron bien** (usan `FormatoMoneda`, no interpolación en JS); lo que estaba mal era el dibujo.
- **Caso degenerado del hero:** si `Datos.Ventas` llegara en `null` con `TieneDatos == true`, la fila de ventas no se renderiza y el resultado en dólares no se muestra en ningún lado (antes vivía en el hero). Es prácticamente inalcanzable —`TieneDatos` sale de que existan `VentasMensuales` del período, que es exactamente lo que hace no-nulo a `Ventas`— y la vista ya muestra un alerta explícito en ese caso. Queda anotado por si alguna vez aparece.
- **La tarjeta "Ventas s/impuesto" del Dashboard se sacó por diseño de grilla, no por E1.** Si el dueño la extraña, el dato está en la tabla de abajo; volver a ponerla obliga a rediseñar la fila entera (vuelve a 7 y 6).
- **P-B06 sigue abierta** (alcance del Dashboard para el Gerente), heredada de las Olas 1 y 2.
- Los archivos tocados quedaron con fin de línea LF en el working tree (el repo usa CRLF con `autocrlf`). Git normaliza al hacer `git add`; sin impacto funcional.

#### Guía de prueba manual (para el dueño del estudio / QA)
**No hay migración que aplicar. Se prueba directo sobre el deploy.**

**1.1 y 1.2 — lo que bloqueaba**
1. Como **SuperUsuario**, *Usuarios → Nuevo*: el combo Rol tiene que ofrecer **Administrador, Encargado e Inversor**. Crear el usuario Gerente con rol **Encargado** y confirmar que entra y ve KOI + Gestión (Dashboard, Notificaciones, Estado de Resultados, Historial, Fichador) y **no** ve Inversiones ni Sistema.
2. Como **Administrador** (no SuperUsuario), *Usuarios → Nuevo*: el combo tiene que ofrecer **Encargado e Inversor**, y **no** Administrador ni SuperUsuario.
3. **Regresión del combo de Editar (era un defecto silencioso):** editar el usuario Encargado recién creado, cambiarle sólo el nombre y guardar. Volver a abrirlo: **tiene que seguir siendo Encargado**. Antes de este cambio se guardaba como Inversor sin avisar.
4. Como **Administrador**: en el sidebar, sección Sistema, tiene que estar **"Sistema"**, y al entrar tiene que abrir la pantalla (no 403). Verificar que aparece **una sola vez**.
5. Como **SuperUsuario**: "Sistema" tiene que seguir apareciendo **una sola vez** (ahora en la sección "Sistema", no en "Super Usuario"), y "Auditoría" tiene que seguir estando.
6. Como **Encargado** e **Inversor**: "Sistema" **no** tiene que aparecer, y forzar la URL `/System` tiene que dar **403**.

**2.1 y 2.1b — mails en segundo plano**
7. *Login → ¿Olvidaste tu contraseña?* con un email **existente**: la pantalla de confirmación tiene que aparecer **al instante** (antes esperaba al servidor de correo). El mail llega unos segundos después. Seguir el link y cambiar la contraseña.
8. **Anti-enumeración:** repetir con un email **inexistente**. La pantalla tiene que ser **exactamente la misma** y tardar **lo mismo**. Si una de las dos tarda notoriamente más que la otra, avisar: es un defecto de seguridad.
9. **Cierre de período (el defecto real):** cerrar un período de prueba. Verificar en *Hist. notif. cierre* que **los mails salieron de verdad** y que los inversores los recibieron. Antes esto podía no pasar en silencio.
10. **"Enviar a los N":** desde *Hist. notif. cierre* → "Revisar y enviar" → confirmar. Mismo criterio: los mails tienen que llegar.
11. **Que los fallos se vean:** pedir un reset de contraseña con el SMTP mal configurado a propósito (o el servidor caído). La pantalla tiene que responder igual de rápido, y en el log del sitio tiene que quedar una línea de **Error** que diga `FALLO el trabajo en segundo plano reset-password`. Antes no quedaba nada.

**2.2 — los botones del concepto**
12. Como Administrador, en un mes **abierto**: buscar un concepto **con importe**. Tiene que verse el candado y **ningún** botón.
13. Poner ese importe en **0** y salir del campo (Tab o click afuera). **Sin recargar**, tienen que aparecer los dos botones (ojo tachado y tacho) y desaparecer el candado.
14. **El sentido inverso:** volver a cargarle un importe y salir del campo. Los botones tienen que **desaparecer** solos y volver el candado.
15. Repetir 13 y 14 con un concepto **porcentual** (badge azul). Mismo comportamiento.
16. **Que la guarda siga estando:** con un concepto **con importe**, forzar el POST a `/EstadoResultados/QuitarConceptoDelMes`. Tiene que devolver un error explícito y **no** sacar la fila.
17. Como **Encargado**: el botón de sacar del mes tiene que aparecer y desaparecer igual; el de dar de baja del catálogo **no tiene que existir** en ningún estado.

**2.3 y 2.4 — los gráficos del Dashboard**
18. *Dashboard*, sección Gastos: la torta **"Resultado vs Gastos"** tiene que tener **dos porciones de colores claramente distintos**. En un mes con resultado **negativo**, la porción tiene que decir **"Pérdida"** y ser **ámbar** (no verde). Pasar el mouse: el tooltip muestra el importe y el % **sobre las ventas del mes**.
19. **Regresión de los otros dos gráficos** (estaban rotos y no se había reportado): en "Distribución por canal", los colores de las porciones tienen que coincidir con las badges de abajo — Salón **azul**, Pedidos **naranja**, Mostrador **verde**. Y "Ticket promedio por canal" tiene que tener **3 barras**, no 6.
20. **Comprobación numérica:** los porcentajes del tooltip de la torta de canales tienen que sumar 100 % y coincidir con las badges.
21. *Dashboard* con Ayres encendido, **"Evolución diaria"**: tiene que haber **un solo gráfico con las dos series a la vez** — barras azules de facturado y línea ámbar de cubiertos — **sin botones de selector**. Eje izquierdo en pesos (azul), eje derecho en cubiertos (ámbar), leyenda arriba.
22. **Que la línea se lea:** la línea de cubiertos **no** tiene que estar pegada al cero. Si lo está, el doble eje no se aplicó.
23. **Caché:** recargar el Dashboard dentro de los 5 minutos. El gráfico tiene que aparecer **al instante**.
24. **Los dos temas:** repetir 18, 21 y 22 en **tema claro y en tema oscuro**. Todo tiene que leerse en los dos.

**2.5 — la rentabilidad (LEER ANTES DE PROBAR)**
25. *Dashboard*: la tarjeta **"Rentabilidad"** sigue mostrando **un solo porcentaje**, ahora con el subtítulo "del total vendido". **Es a propósito** — ver el punto 2.5 de esta entrada: ese número es el margen del local sobre las ventas del mes y vale lo mismo en pesos que en dólares. La rentabilidad que sí cambia según la moneda es la de la inversión, y está en los pasos 26 a 29. **Si igual querés una tarjeta de rendimiento propio en el Dashboard del inversor, decilo: es un ítem nuevo.**

**2.6 y 3.3 — Mi Inversión y el Reporte**
26. Entrar como **Inversor**. *Mi Inversión*: tienen que verse **6 tarjetas parejas**, sin ningún hueco ni tarjeta corrida a la derecha. **En el celular**, 3 filas de 2, con Dividendos U$D y Dividendos $ una al lado de la otra, y lo mismo con los dos Recupero.
27. Las **dos** tarjetas de Recupero tienen que tener barra de progreso y escala, y la misma altura.
28. El gráfico **"Evolución del recupero"** tiene que tener **dos líneas**: la azul llena (dólares) y la ámbar punteada (pesos), más la línea verde de la meta. Las dos tienen que **separarse** con el tiempo — esa es la brecha que la leyenda explica.
29. La tabla de liquidaciones: las columnas **"Renta"** y **"Recupero acum."** muestran **dos números** cada una, U$D arriba y $ abajo.
30. **Consistencia (importante):** el número de arriba de la **última fila** de "Recupero acum." tiene que coincidir **al decimal** con la tarjeta "Recupero U$D", y el de abajo con la tarjeta "Recupero $". Si no coinciden, avisar.
31. *Reporte de rendimiento*: los KPIs "Utilidad acumulada", "% Recupero" y "Rentabilidad mensual" tienen que mostrar **el número en dólares grande y el de pesos abajo en chico**, y debajo de los KPIs tiene que aparecer la **misma leyenda** que Mi Inversión.
32. El "% Recupero" en dólares del Reporte tiene que coincidir **al decimal** con el de Mi Inversión, y el de pesos también.
33. El gráfico de pagos del Reporte sigue **en dólares** (eje y rótulos). Pasar el mouse sobre una barra: el tooltip tiene que mostrar **las dos monedas**.
34. **Un mes sin tipo de cambio cargado:** en la tabla y en el gráfico, el valor en pesos de ese mes tiene que aparecer como **"—"** y no como 0. Nunca se convierte al dólar de hoy.

**3.1 y 3.2 — distribución (mirar, no calcular)**
35. *Dashboard* como **Administrador**, en **desktop**: la fila de arriba tiene **4 tarjetas** que llenan el ancho. La fila de ventas tiene **6**. Ninguna tarjeta sola con un hueco al lado.
36. Lo mismo en **celular**: 2×2 arriba, 3 filas de 2 en la fila de ventas.
37. Lo mismo entrando como **Inversor**: la fila de ventas también tiene **6** tarjetas y queda pareja.
38. *Dashboard*, sección Gastos: las tres cards llenan la fila. Probar también un mes **sin gastos cargados**: lo que quede tiene que llenar el ancho igual.
39. *Mes actual* en **tablet vertical** (o achicando la ventana a ~800 px): las 4 tarjetas tienen que verse **2×2**, con los importes **en un solo renglón**.

**Barrido legal (E1) — revalidación obligatoria**
40. Entrar con un usuario **INVERSOR real**. En *Rendimiento Histórico*: **no** tiene que aparecer "informal", "facturado", "A / B", "s/impuesto" ni "c/impuesto" en ningún lado, ni ninguna columna que separe la venta en dos. La tabla "Ventas por canal" tiene que tener **3 columnas**.
41. **No** tiene que existir la card "Evolución diaria". Forzar `GET /Dashboard/SerieDiaria?anio=2026&mes=8` con ese usuario tiene que dar **403**.
42. Con el **Administrador**, verificar que **sí** sigue viendo la columna "S/impto. (A)" en la tabla "Ventas por canal", ahora **con el % del total al pie**.

#### Checklist de salida para merge
- [x] Build 0 errores; 0 advertencias nuevas (las 9 son preexistentes)
- [x] Sin migraciones EF: ningún cambio de esquema ni de datos
- [x] Meses históricos intactos; ningún cálculo financiero modificado (P-B05 respetada)
- [x] Barrido legal E1 revalidado tras tocar el Dashboard — la etapa **reduce** la superficie A/B del Inversor
- [x] Bloques de atributos verificados método por método en `UsersController`, `SystemController`, `AccountController`, `EstadoResultadosController` y `NotificacionCierreController` tras insertar
- [x] Escalada de roles de `GetAssignableRoles()` alineada con `CanManageUser()`
- [x] "Sistema" en el sidebar exactamente una vez por rol (se movió, no se duplicó)
- [x] `Task.Run` sobre servicios scoped barrido en todo el repo: 2 corregidos, 1 evaluado y descartado con motivo
- [x] Las guardas de servidor de C2/C3 intactas: 2.2 sólo cambia visibilidad de botones
- [x] Números que van a gráficos serializados **invariantes** en las 4 series del Dashboard
- [x] Caché de 5 minutos de la serie diaria conservada; `SerieDiaria` y su policy sin tocar
- [x] Patrón nuevo agregado a `docs/patrones/catalogo.yml` (**PAT-025**)
- [ ] **Commit y deploy: deliberadamente SIN hacer** — los revisa y ejecuta el dueño del estudio
- [ ] Prueba manual de los 42 pasos de arriba — **los pasos 40 a 42 (E1, legal) no son opcionales**
- [ ] **Decidir 2.5**: la premisa no se sostiene. Confirmar el criterio o pedir el ítem nuevo
- [ ] Responder P-B06 (alcance del Dashboard para el Gerente)
- [ ] Pendientes heredados de las Etapas 22 y 23 que siguen abiertos (migraciones E20/E21 en producción, los 6 subgrupos sin equivalente)

---

### Etapa 23 — Sprint "Entrega 1: fixes y mejoras" — OLA 2 (lotes C, D, E y F) (2026-09-10)
- Alcance aprobado en `1-analista-funcional.md` §16, `2-disenador-funcional.md` §15 (15.3 a 15.6) y `3-arquitecto-mvc.md` §13 (13.6 a 13.10). **Gate de presupuesto SALTEADO por decisión explícita del dueño**, igual que en la Ola 1 — registrado, no omitido.
- **Ola 2 de 2, ejecutada DESPUÉS de la Ola 1 y no en paralelo** (§13.1). Vuelve sobre tres archivos de la ola anterior: `EstadoResultadosController`, `Views/EstadoResultados/Mensual.cshtml` y `Views/ImportacionInicial/Index.cshtml`.
- **1 migración EF de ESQUEMA** (`E21_BenchmarkMercado_E4`), la única del sprint, con carga inicial de datos incluida.
- **Las DOS banderas de `Mensual.cshtml` se respetaron**: `esAdmin` (cierre/reapertura) y `puedeGestionar` (carga). No se unificaron. El botón nuevo de C2 usa `esAdmin`; el de C3, `puedeGestionar`.

**Escaneo de reutilización (`catalogo.yml` + `docs/*/definiciones/5-implementador.md` de todos los proyectos):** 4 hits, los 4 reutilizados. **Ninguno de otro proyecto: los cuatro son de KOI mismo**, lo cual es esperado — esta ola es UI sobre pantallas que ya existen, no componentes nuevos.

| Origen | Qué se tomó | Cómo se aplicó |
|---|---|---|
| **KOI — PAT-012 / `ImportacionInicial`** | Flujo analizar → preview → confirmar, con la escritura detrás de una confirmación explícita. | Es el patrón de **C4**: `PreviewEnvio` (GET, sólo lectura) → `EnviarMasivo` (POST). Se copió también la parte que suele olvidarse: el POST **revalida** en el servidor que haya destinatarios, porque una pantalla de confirmación no es control de acceso — se puede postear directo. |
| **KOI — `EstadoResultados/Mensual` (Etapa 18)** | Edición inline por AJAX con `pintarImporteConcepto` y el indicador de estado por fila. | **C3** reusa el mismo `$('#tbodyGastos').on('click', ...)` delegado y el mismo formato de respuesta JSON `{success, message}`. |
| **KOI — `MiInversion` (gráfico de recupero)** | Chart.js con el patrón de tema claro/oscuro (`data-theme` → `textColor`/`gridColor`). | Copiado tal cual a los dos gráficos nuevos: evolución diaria (D) y pagos mensuales USD (E4). |
| **KOI — `AyresService` (Etapa 21)** | El agregador que acumula y descarta el detalle. | **D**: se le agregó el acumulado por día **dentro del mismo recorrido**, sin tocar la política de descarte. |

**No se agregó ningún patrón nuevo al catálogo.** El único candidato era el reporte de rendimiento, pero está atado al modelo de puntos/liquidaciones de KOI y no es portable tal cual.

---

#### C1 · Importes sin decimales y sin flechitas (ítems 5 y 6)
- **`Helpers/FormatoMoneda.cs` es el único punto de cambio del redondeo**: `FormatMonto` pasa de `N2` a `N0`. La base y todos los cálculos **conservan los centavos** (P-B03): es presentación y nada más, así que la conciliación al centavo contra el Excel del cliente sigue dando exacta.
- **Las tres excepciones de §13.6 se implementaron como métodos propios y se verificaron una por una:**
  - `FormatTipoCambio` (`N2`) — **el TC no es un importe**: es el divisor de todo lo que se muestra en dólares. Redondearlo movía los USD de toda la pantalla. Aplicado en los **6 lugares** donde se renderiza un TC: `Dashboard/Index`, `EstadoResultados/Anual`, `EstadoResultados/Mensual` (badge), `EstadoResultados/PreviewCierre`, `ImportacionInicial/Index` y `TipoCambio/Index` (compra, venta, promedio y promedio blue). En `TipoCambio/Index` el `formatNum()` de JS **se dejó en 2 decimales a propósito**: sólo formatea cotizaciones.
  - `FormatPorcentaje` (`N1`) / `FormatPorcentaje2` (`N2`) — porcentajes.
  - `FormatPuntos` (`N2`) — los puntos de inversión admiten fracciones. Aplicado en `Puntos/Index` (4 usos), `Liquidaciones/Index` y `PreviewCierre`.
- **Los `ToString("N2")` sueltos de las vistas se pasaron al helper**, que era el punto del ítem: si no, "centralizar" habría dejado 30 lugares formateando por su cuenta. Tocadas: `Anual` (8), `Mensual` (17), `PreviewCierre` (8), `Inversores/Index`, `Liquidaciones/Index`, `Puntos/Index`, `TipoCambio/Index`.
- **Del lado JS hubo que partir el formateador, no sólo bajarle los decimales.** `Mensual.cshtml` tenía un único `fmt()` que se usaba para importes **y para el % de referencia de cada concepto**. Bajarlo a 0 decimales habría repintado "3,00 %" como "3 %" en cuanto se recalculara. Ahora hay `fmt` (importes, 0 dec.), `fmtPct` (porcentajes, 2 dec.) y `fmtDec` (ítems por venta, que es una cantidad con fracción). Mismo criterio en `PreviewCierre.cshtml`.
- **Los inputs de importe muestran el valor sin `,00` cuando el número guardado no tiene centavos, y CON centavos cuando sí los tiene.** Lo que viaja al servidor no cambió: `data-valor-anterior` sigue en `F2` invariante. **La asimetría es deliberada**: si el valor mostrado y el de referencia fueran iguales, cada blur sin edición dispararía un guardado inútil — y peor, un guardado que redondearía el importe en la base, que es exactamente lo que P-B03 prohíbe.
- **Flechitas: una regla CSS global en `olvidata-theme.css`**, no 17 vistas. `::-webkit-*-spin-button { appearance:none }` + `-moz-appearance:textfield` sobre `input[type="number"]`. Se dejó una clase de escape `.ov-spinner` por si algún contador chico las quiere de vuelta. El `inputmode="decimal"` se aplica desde **un script en `_Layout`** a todos los `input[type=number]` sin `inputmode` propio — mismo criterio: un lugar, no diecisiete. Es `decimal` y no `numeric` porque los importes **se guardan** con centavos y el teclado del celular tiene que tener el separador.

#### C2 · Dar de baja subgrupos desde el EDR (ítem 7)
- Botón de tacho por fila, **sólo Administrador** (`esAdmin`, no `puedeGestionar`: el Encargado carga, no administra el catálogo) y **sólo con importe 0 en el período**.
- Acción `EstadoResultadosController.DarDeBajaSubgrupo` con `[Authorize(Policy = "SoloAdministrador")]` **a nivel acción** — el controller es `[Authorize]` simple, igual que resolvió la Ola 1.
- `EstadoResultadosService.DarDeBajaSubgrupoAsync` **revalida el importe en el servidor**: ocultar el botón no es la guarda. Es baja lógica (`DeletedAt` en el `Subgrupo`), el mismo mecanismo que `ConfiguracionController.SubgrupoDelete`.
- **La historia no se toca y se sigue viendo:** `ObtenerAsync` ya listaba los subgrupos inactivos en los períodos donde tienen importe cargado. La confirmación se lo dice al usuario con esas palabras: afecta a los meses siguientes, no a los anteriores.

#### C3 · Conceptos por mes — el gasto extraordinario (ítem 11)
- **Es el ítem con más diseño del lote y el único que necesitó una decisión de modelo.**
- **Sin columna nueva ni migración:** "sacado de este mes" se representa con `DeletedAt` en el propio `ConceptoGasto` (una *lápida*). Funciona porque el par `(PeriodoMensualId, SubgrupoId)` ya tiene índice único —la lápida **es** la fila, no puede haber dos— y porque **todos** los que suman totales ya filtraban `DeletedAt == null`: `EstadoResultadosService.ObtenerAsync`, `ObtenerResumenAnualAsync`, `DashboardService` (×2) e `InversionesService`. Una fila sacada no suma en ningún lado, sin tocar ninguno de esos cinco lugares.
- **La contracara del truco: el query filter global esconde las lápidas, y eso rompe todo lo que hace "buscá y si no está, insertá".** Se corrigieron **cuatro** puntos, que sin esto tiraban una violación de índice único en la cara del usuario:
  - `GuardarConceptoGastoAsync` → `IgnoreQueryFilters()` + rechaza guardar sobre un concepto que no está en el mes.
  - `RevertirConceptoAlPorcentajeAsync` → ídem.
  - `RecalcularInternamente` → `IgnoreQueryFilters()` y **`continue` si es lápida**: el recálculo de porcentuales **no resucita** un concepto que alguien sacó a propósito.
  - `ImportacionInicialService` (importador de plantilla, 6 hojas) → **este no estaba en el alcance del ítem y era un crash real**: chequeaba `AnyAsync(...)` sin `IgnoreQueryFilters`, así que una lápida le daba `false` y el `INSERT` reventaba contra el índice único. Ahora la ve y la reporta como "ya existe — omitido".
- **Agregar:** selector "Agregar concepto a este mes" en el header de la card de Gastos, que lista los subgrupos **vigentes** del catálogo que hoy no están en el período (`EstadoResultadosDto.SubgruposDisponibles`, armado en el mismo recorrido que ya arma la grilla). Crea la fila en 0. Si el subgrupo es porcentual, dispara el recálculo para que le quede el % vigente. **El importe viejo NO se restaura**: si volvió a la grilla es porque este mes hay que cargarlo de nuevo.
- **Quitar:** sólo con importe 0. Con importe, el botón no se renderiza (aparece un candado con la explicación) **y además el servicio lo rechaza**. Así nunca se borra plata por accidente.
- **La guarda mira el MISMO campo que lee el EDR** para ese subgrupo (`ImporteManual` si es Manual, `ImporteCalculado` si es porcentual). Mirar el otro habría dejado pasar una fila con importe visible en pantalla — es el mismo modo de falla que apareció en la migración A2 de la Ola 1.
- **Interacción con el importador del Excel del cliente, documentada a propósito:** `ImportacionExcelKoiService.EscribirConceptosAsync` **revive** la lápida (`DeletedAt = null`) si el Excel trae ese concepto para ese mes. Es correcto —el Excel es la fuente de verdad— pero hay que saberlo: reimportar puede devolver a la grilla un concepto que se había sacado. Si el Excel no lo trae, no lo toca y sigue afuera.
- **C2 y C3 son cosas distintas y la UI lo dice con todas las letras.** Ícono de ojo tachado = sacar del **mes**; ícono de tacho = baja del **catálogo**. Cada confirmación explica el alcance.

#### C4 · Previsualizar la notificación de cierre (ítem 14)
- `INotificacionCierreService.GenerarPreviewEnvioAsync` — **sólo lectura**: abrir la pantalla no manda ni registra nada.
- **Recorre exactamente el mismo criterio de exclusión que `EnviarNotificacionCierreAsync`** (usuario con rol Inversor vinculado a la ficha + email no vacío). Está escrito igual en los dos lados y **hay que tocarlos juntos**: si divergen, el preview miente, que es lo único que puede invalidar este ítem.
- La vista muestra **el mail real**, armado con `BuildEmailHtml` y la liquidación real del primer destinatario, dentro de un `<iframe srcdoc sandbox>`. El iframe no es decorativo: el HTML del mail trae sus propios estilos inline y, metido directo en la página, se pisa con el tema de la app y se ve **distinto** de lo que llega al inversor — justo lo que el ítem quiere evitar. `sandbox` sin permisos lo deja inerte.
- Lista de destinatarios **con su dirección** y neto, más un bloque aparte de **omitidos con el motivo** (tienen liquidación pero no hay a dónde escribirles). Botones "Enviar a los N" / "Cancelar".
- **`EnviarMasivo` revalida en el servidor** que haya destinatarios. Que el botón esté en una pantalla de confirmación no impide postear directo.
- **Bug preexistente corregido de paso:** `Views/NotificacionCierre/Index.cshtml` estaba guardado en **Windows-1252** y Razor lee UTF-8, así que en producción se veía "Per?odo", "Env?o", "Notificaci?n". Reencodeado a UTF-8 con BOM, como el resto de las vistas.
- **También de paso:** el asunto del mail se armaba con `GetMonthName()` crudo en dos lugares (minúscula: "agosto 2026") mientras el historial usaba el helper `NombreMes` (capitalizado). Los tres usan ahora el mismo helper. **Sin esto el preview habría mostrado un asunto distinto del que sale**, y un preview que no dice literalmente lo que se manda no sirve para lo que se lo agregó.

#### D · Dashboard, Mes actual y mobile (ítems 15 a 22, 29)
- **Serie diaria de Ayres (§13.7) — la política de descarte NO se tocó.** El `HashSet<DateOnly>` que sólo contaba días pasó a ser un `Dictionary<DateOnly, AcumuladoDia>` que suma importe, cubiertos y tickets **en el mismo `foreach`**. Son ≤31 entradas; las ~1.000 ventas del mes se siguen tirando tramo a tramo (R-A03). Sólo entran las ventas **cerradas**, igual que el resto del agregado: si entraran las anuladas, el gráfico diario no cerraría contra el total del mes.
- **Ítem 15** — el KPI "Ticket promedio" del Dashboard mensual pasa a ser **"Cubiertos / día"** (`IndicadoresDto.PromedioCubiertosPorDia`, mismo denominador que `PromedioVentasPorDia` para que las dos se lean juntas). El ticket promedio no se perdió: sigue en el preview de Ayres del EDR. Se agregó además una tarjeta **"Resultado del mes"** con el valor en **$ y en U$D** al lado de los KPIs de venta — ya estaba en el hero de arriba, pero el cliente lo busca junto a las ventas.
- **Ítem 16** — eliminados el gráfico **y** la tabla "Facturado vs informal (A/B)". Se fue con ellos el pie de "Ticket A / comensal" y "Ticket B / comensal", que vivía dentro de esa card y era otra exposición del mismo corte.
- **Ítem 17** — eliminado el gráfico "Ventas por canal — desglose A y B", con sus 6 variables Razor.
- **Ítems 18 y 24 (E2)** — el desglose por rubro pasa de `col-md-3` a `col-lg-5` y de 240 px a **420 px** de alto; la tabla de rubros baja a `col-lg-4` y la torta a `col-lg-3`. Era el gráfico más apretado de la pantalla. **Sirve a los dos ítems de una vez** porque `Dashboard/Index` es la misma vista para el Administrador y para el Inversor.
- **Ítems 20 y 22 — UN SOLO gráfico** de evolución diaria con selector **$ Plata / Cubiertos**, no dos. Son la misma serie sobre el mismo eje: dos gráficos apilados obligaban a comparar de memoria. Ocupa el ancho que liberó el ítem 16.
- **El gráfico diario se carga por AJAX y no bloquea el render**, y **está cacheado 5 minutos en memoria**. Sin la caché, **cada** carga del Dashboard de un Administrador disparaba **4 consultas HTTP a Ayres** (el mes se trae en tramos de ≤10 días) sólo para dibujar un gráfico. Se cachea únicamente el éxito: un error de red transitorio no deja la card rota cinco minutos. Requirió `AddMemoryCache()` en `Program.cs`.
- **Ítems 19, 21 y 29 (Mes actual)** — se agregó la tarjeta **Cubiertos** (cantidad + $ por cubierto). Las tarjetas pasan de 3 a 4 y de `col-md-4` a `col-md-3`: **en mobile la grilla queda 2×2 simétrica**, que era el ítem 21/29 — con tres, la última quedaba sola ocupando media pantalla.

#### E1 · Barrido legal — ítem 23 (lo más sensible del sprint)
- **Se barrió por DATO y no por nombre de pantalla** (§13.9). `grep` sobre `VentasA`, `VentasB`, `VentasASalon/BSalon/APedidos/BPedidos/AMostrador/BMostrador`, `VentasSinImpuestos`, `PctVentasA`, `TicketPromedioA/B`, `Informal`, `Facturado`, `NoFacturado`, `s/impuesto`, `c/impuesto`.
- **Resultado del barrido — TODO lo accesible al rol Inversor:**

| Superficie | Rol Inversor | Veredicto |
|---|---|---|
| `Dashboard/Index` ("Rendimiento Histórico") | **sí entra** | **Único lugar con exposición. Corregido.** |
| `Dashboard/Historico` (JSON) | sí | Sólo `VentasTotales`/`TotalGastos`/`Resultado`. Limpio. |
| `Dashboard/SerieDiaria` (JSON) | **no** — policy `GestionOperativa` | Devuelve venta facturada por día: barrera en el **endpoint**, no sólo en el `@if` de la vista. |
| `MesActual/Index` | sí | Sólo totales y % por canal. Limpio. |
| `MiInversion/Index` y `/Reporte` | sí | Liquidaciones y dólares. Sin A/B. |
| `EstadoResultados/Anual` ("Historial de Resultados") | sí | Ventas totales, gastos, resultado, TC. Limpio. |
| `EstadoResultados/Mensual` | **no** — `GestionOperativa` | El Administrador **conserva** el desglose completo: es donde lo carga. |
| `ImportacionInicial/Index` | **no** — `SoloAdministrador` | Muestra A/B del Excel. Fuera de alcance. |
| **Exportables** (`ExportarAnualExcel`, `DescargarPlantilla`) | **no** — `GestionOperativa` / `SoloAdministrador` | **Son los dos únicos exportables del sistema.** Ninguno llega al Inversor. |

- **Lo corregido en `Dashboard/Index`** (bandera `esInversor`): fuera la tarjeta "Ventas s/impuesto" (con su `PctVentasA`); fuera la columna "S/impto. (A)" de la tabla "Ventas por canal", en las 4 filas; y la etiqueta de la tarjeta de totales pasa de **"Ventas c/impuesto" + "Total A + B"** a **"Ventas del mes"**. Ese último es sutil y por eso se hizo: el número es el mismo para los dos roles, pero decir "c/impuesto" y "A + B" **reintroduce el desglose por la puerta de atrás** aunque no se muestre ninguna cifra.
- Los ítems 16 y 17 ya habían sacado los dos gráficos y la tabla A/B **para todos los roles**, así que ahí no hizo falta bandera.

#### E3 · La brecha del recupero (ítem 25)
- **El cálculo NO se tocó**, como manda P-B05. Se agregó en `MiInversion/Index`, entre los dos porcentajes y el gráfico, una leyenda sin tecnicismos: el capital está en dólares, los dividendos se cobran en pesos, y cada pago se convierte al dólar **del mes en que se cobró**, no al de hoy. Los dos porcentajes son correctos y distintos. Sólo aparece cuando existen los dos.

#### E4 · Reporte de rendimiento (ítems 26, 27 y 28)
- **`MiInversion/Reporte`** replica el PDF aprobado: encabezado con marca + nombre + período cubierto, **4 KPIs** (Capital Aportado · Utilidad Acumulada en verde · % Recupero con "En N meses" · Rentabilidad Mensual promedio), **gráfico de barras** de pagos mensuales en USD **con el valor rotulado sobre cada barra**, **comparativa de mercado** en barras horizontales, y párrafo de análisis al pie. **Todo en dólares.**
- **`ObtenerReporteRendimientoAsync` NO recalcula nada**: parte de `ObtenerMiInversionAsync`, que ya resuelve dividendos y recupero con el criterio acordado. Recalcular por separado habría permitido que el reporte y Mi Inversión mostraran dos números distintos para lo mismo — justo la inconsistencia que el ítem 25 vino a cerrar.
- **"En N meses" cuenta los meses del RANGO, no las liquidaciones.** Un mes sin liquidación igual pasó y tiene que bajar el promedio mensual. Con liquidaciones consecutivas da lo mismo; sin ellas, contar filas inflaría la rentabilidad.
- **Los rótulos sobre las barras se hacen con un plugin inline de Chart.js**, no con `chartjs-plugin-datalabels`: no vale sumar una dependencia de CDN para dibujar 14 números.
- **Las barras de la comparativa se escalan sobre el máximo, no sobre 100 %** — como el PDF. Con escala fija, un recupero del 37 % dejaría las cuatro barras en un cuarto del panel y la comparación no se leería.
- **El párrafo de análisis se redacta según el propio número**, no es un texto fijo. Un párrafo que dice "excelente tracción" abajo de un recupero del 3 % le hace perder credibilidad a todo el reporte.
- **Liquidaciones pendientes:** se dibujan con la barra clara y el tooltip lo aclara. No suman a la Utilidad Acumulada, que sigue contando sólo las **pagadas** — el mismo criterio que Mi Inversión.
- **Benchmarks — tabla nueva `BenchmarkMercado`** (`Nombre`, `PorcentajeAnual`, `Orden`, `Activo`), única migración de esquema del sprint. **No se reutilizó `ParametroPorcentaje`** (la otra opción que §13.8 dejaba abierta): cuelga de un Subgrupo de gastos y tiene vigencia por período, así que habría exigido un subgrupo fantasma dentro del catálogo de gastos del EDR.
- `Activo` **no lleva `HasDefaultValue(true)`**: el sentinel de un `bool` en EF es `false`, así que un benchmark apagado a propósito se habría guardado como "no seteado" y la base le habría vuelto a poner `true`.
- **Carga inicial en la migración** (S&P 500 12 %, Bonos Corporativos 8 %, Propiedades Inmobiliarias 5 %) con `INSERT ... SELECT ... WHERE NOT EXISTS`: si alguien ya los cargó a mano, no se duplican.
- ABM en **Configuración → Comparativa de mercado**, con edición inline. **Los `<form>` van FUERA de la tabla** y los inputs se enganchan con el atributo `form="..."`: un `<form>` dentro de un `<tr>` es HTML inválido y el navegador lo saca de la tabla al parsear, dejando los campos huérfanos.
- Accesos nuevos en el sidebar: **Inversor** → "Reporte de rendimiento" en Mi Cuenta; **Administrador** → el mismo reporte con selector de inversor (sección Inversiones) y "Comparativa de mercado" (bajo Configuración). Más un botón desde Mi Inversión.

#### F · Texto del importador (ítem 30)
- **La funcionalidad NO se sacó.** Se agregó arriba de todo un bloque **"¿Cuándo se usa esta pantalla?"** en dos columnas: *sí, usala para* (cargar historial de varios meses, corregir varios meses juntos, dar de alta rubros/subgrupos del Excel) / *no, para esto no* (el mes en curso va en Estado de Resultados; un solo importe se edita en la grilla; los meses cerrados que no querés tocar). Cierra con que nunca escribe sin mostrar antes qué va a hacer.
- **Corrección de la frase señalada — y acá el enunciado del sprint y el código no coincidían.** "Los registros que ya existen se omiten con advertencia" **no está en el importador principal**: está en el bloque de la **plantilla del sistema** (las 6 hojas, `ImportacionInicialService`), donde **sigue siendo cierta** — ese importador da de alta y omite lo existente, y la Ola 1 no lo tocó. Lo que cambió en la Ola 1 es el **importador del Excel del cliente** (`ImportacionExcelKoiService`, `ActualizarExistentes = true` por defecto). Se corrigieron **las dos cosas por separado**, que es lo único honesto:
  - **Importador del Excel del cliente:** el texto de la opción ahora dice que **viene activado**, que un período ya cargado **se actualiza** y que reimportar deja el sistema igual al Excel sin duplicar; y qué pasa si se destilda.
  - **Plantilla del sistema:** se explicita que **es otra cosa** y para qué sirve (puesta en marcha: inversores, puntos y liquidaciones), y la frase pasa a **"Acá los registros que ya existen se omiten... Esta ruta es de alta, no de corrección"**. Mismo criterio en el diálogo de confirmación.

---

#### Evidencia de build
- `dotnet build` desde la raíz → **Compilación correcta, 0 errores**, 9 advertencias, **todas preexistentes** y ninguna introducida por esta ola: 8× NU1902 (MailKit 4.14.1 / MimeKit 4.14.0 — VUL-001, pendiente) y 1× CS0114 (`HomeController.StatusCode`).
- Las vistas Razor **se compilan en build** (no hay `RuntimeCompilation` en el `.csproj`), así que los 0 errores cubren los `.cshtml`. Se aprovechó: un `@{` mal anidado en `Reporte.cshtml` lo cazó el compilador, no el navegador.
- `dotnet ef migrations script E20 → E21` render OK: `CREATE TABLE` + el `INSERT` de carga inicial, envueltos en `START TRANSACTION; ... COMMIT;`.
- **Sin smoke test funcional** (regla del rol). No hay proyecto de tests en el repo. La guía de prueba manual va abajo.

#### Riesgos y supuestos
- **C3 usa `DeletedAt` de `ConceptoGasto` con una semántica nueva** ("sacado de este mes"). Se auditaron los **10** consumidores de `ConceptosGasto` del repo: 5 ya filtraban bien, 4 se corrigieron, 1 (`SeedData`) no aplica. **Cualquier código nuevo que busque un `ConceptoGasto` para insertarlo si no existe tiene que usar `IgnoreQueryFilters()`** o va a chocar contra el índice único.
- **El importador del Excel del cliente revive los conceptos sacados del mes** si el archivo los trae. Es correcto, pero hay que decírselo al cliente.
- **La serie diaria depende de Ayres.** Con el flag apagado o la integración caída, la card avisa y el resto del Dashboard sigue funcionando. **La caché de 5 minutos implica que el mes en curso puede mostrarse desactualizado hasta 5 minutos** — deliberado.
- **E1 se verificó por dato sobre el código, no en navegador.** La tabla de arriba es el resultado del barrido; **QA tiene que confirmarlo con un usuario Inversor real**, porque es el ítem legal del sprint.
- **E4 muestra `NetoUsd ?? 0`** para un mes sin TC cargado. **No se inventa una conversión al dólar de hoy**, que es exactamente lo que el ítem 25 dice que no hay que hacer: la barra queda en el piso, igual que el "Oct 25" del PDF.
- **Los archivos tocados quedaron con fin de línea LF** en el working tree (el repo usa CRLF con `autocrlf`). Git normaliza al hacer `git add`; no hay impacto funcional.
- **P-B06 sigue abierta** (alcance del Dashboard para el Gerente), heredada de la Ola 1.
- **Los 6 subgrupos del catálogo viejo sin consolidar** (CMV, Otros gastos, Honorarios, Publicidad, Previsión I y II) siguen sin equivalente y **es lo esperado**: requieren definición del cliente. Esta ola no los tocó.

#### Guía de prueba manual (para el dueño del estudio / QA)
**Antes de nada: aplicar `E21_BenchmarkMercado_E4` (`dotnet ef database update`). Es sólo creación de tabla + 3 filas, no toca datos existentes.**

**C1 — decimales y flechitas**
1. Recorrer *Dashboard*, *Estado de Resultados* (mensual y anual), *Liquidaciones*, *Reparto General*, *Mi Inversión*: **ningún importe con centavos**.
2. **Tipo de Cambio**: en *Tipo de Cambio*, en el badge "TC:" del EDR mensual, en la vista anual, en el preview de cierre y en el Dashboard, el TC **tiene que seguir con 2 decimales**. Si perdió los decimales, todos los valores en USD de la pantalla están mal.
3. **Puntos**: en *Puntos* y en *Liquidaciones*, los puntos siguen con 2 decimales (ej. "0,75").
4. **Porcentajes**: en el EDR, la columna "% aplicado" sigue con 2 decimales. Tocar "Recalcular %" y verificar que **después del recálculo siga mostrando "3,00 %" y no "3 %"**.
5. **Flechitas**: en cualquier `<input type=number>` (ventas, importes, comensales) **no** tienen que aparecer las flechitas al pasar el mouse. Desde el celular, el teclado tiene que abrir en numérico.
6. **Que la base conserve los centavos**: cargar un importe con centavos (ej. `1234,56`), guardar, recargar. El input tiene que volver a mostrar **1234.56** (con centavos) aunque el total de la fila se vea redondeado. Después entrar y salir del campo **sin tocarlo**: no tiene que dispararse ningún guardado.

**C2 y C3 — conceptos**
7. Como **Administrador**, en un mes **abierto**: buscar un concepto con importe **0**. Tiene que tener dos botones. Con importe distinto de 0, un candado.
8. **Sacar del mes** (ojo tachado) → confirmar. La fila desaparece y **el Total de Gastos del mes no cambia** (era 0). El concepto tiene que aparecer en el selector "Agregar concepto a este mes".
9. **Volver a agregarlo** desde el selector → aparece con importe 0. Cargarle un importe y verificar que suma al total.
10. **Que el recálculo no lo resucite**: sacar del mes un concepto **porcentual** con importe 0, tocar "Recalcular %" y verificar que **sigue afuera**.
11. **Que no se borre plata**: cargarle importe a un concepto e intentar sacarlo. El botón no tiene que estar. Forzando el POST a `/EstadoResultados/QuitarConceptoDelMes` tiene que devolver un error explícito, **no** sacar la fila.
12. **Dar de baja del catálogo** (tacho) sobre un concepto en 0 → confirmar. Verificar en **el mes siguiente** que ya no aparece, y en **un mes histórico donde tenía importe** que **sigue apareciendo con su importe y el badge "Histórico"**.
13. Como **Encargado**: el botón de sacar del mes tiene que estar; el de dar de baja del catálogo **no**. Forzando `POST /EstadoResultados/DarDeBajaSubgrupo` tiene que dar **403**.
14. **Regresión del importador de plantilla:** después de sacar un concepto de un mes, ir a *Importación desde Excel* → bloque "plantilla del sistema" e importar una plantilla que incluya un gasto de ese mes/subgrupo. Tiene que decir **"ya existe — omitido"**, no reventar con un error de base.

**C4 — preview de la notificación**
15. *Hist. notif. cierre* → elegir un período → **"Revisar y enviar"**. **Verificar que no salió ningún mail todavía** (el historial no suma filas).
16. En la pantalla: el mail se ve **con el diseño real** (encabezado celeste, tabla de importes), con el nombre e importes de un inversor real, y el **asunto capitalizado** ("Liquidación Agosto 2026").
17. La lista de destinatarios muestra **la dirección** de cada uno. Los inversores sin usuario/email aparecen en el bloque amarillo con el motivo.
18. **"Cancelar"** vuelve al historial **sin enviar nada**. Recién "Enviar a los N" → confirmar dispara el envío.
19. **Acentos**: en *Hist. notif. cierre* ya no tiene que verse "Per?odo" ni "Notificaci?n".

**D — Dashboard y Mes actual**
20. *Dashboard*: la tarjeta de ticket promedio ahora dice **"Cubiertos / día"**. Hay una tarjeta **"Resultado del mes"** con $ y U$D.
21. **No** tiene que haber ningún gráfico ni tabla de "Facturado vs informal", ni el gráfico "Ventas por canal — desglose A y B".
22. El gráfico **"Desglose por Rubro"** se ve claramente más grande que antes.
23. Con Ayres encendido: aparece **"Evolución diaria"** con los botones **$ Plata / Cubiertos**. Alternar cambia la serie **sin recargar**. Recargar el Dashboard dentro de los 5 minutos: el gráfico tiene que aparecer **al instante** (caché).
24. *Mes actual*: **4 tarjetas** — Ventas Totales, Ticket Promedio, Cant. de Tickets y **Cubiertos**. En el **celular**, la grilla tiene que quedar **2×2 pareja**, sin una tarjeta suelta abajo.

**E1 — legal (el más importante de esta ola)**
25. **Entrar con un usuario INVERSOR real** (no el Administrador). En *Rendimiento Histórico*: **no** tiene que aparecer en ningún lado la palabra "informal", ni "facturado", ni "A / B", ni "s/impuesto", ni "c/impuesto", ni ninguna columna que separe la venta en dos.
26. La tarjeta de ventas tiene que decir **"Ventas del mes"** (no "Ventas c/impuesto") y **no** tiene que estar el subtítulo "Total A + B".
27. La tabla "Ventas por canal" tiene que tener **3 columnas** (Canal, Importe, %), no 4.
28. **No** tiene que existir la card "Evolución diaria". Forzando `GET /Dashboard/SerieDiaria?anio=2026&mes=8` con ese usuario tiene que dar **403**.
29. Recorrer *Mes actual*, *Mi Inversión*, *Reporte de rendimiento* e *Historial de Resultados* con el mismo criterio.
30. Con el **Administrador**, verificar que **sí** sigue viendo el desglose donde lo necesita: el EDR mensual con Ventas A y B por canal, y la tabla del Dashboard con la columna "S/impto. (A)".

**E3 y E4 — inversor**
31. *Mi Inversión*: debajo de los dos recuperos aparece la leyenda que explica por qué difieren. Leerla como si fueras el inversor: no puede tener una sola palabra técnica.
32. *Reporte de rendimiento*: los 4 KPIs contra el PDF. El "% Recupero" tiene que coincidir con el de *Mi Inversión* (el de dólares) **al decimal**, y "Rentabilidad mensual" tiene que ser ese número dividido los meses del rango.
33. El gráfico de barras tiene el **valor rotulado arriba de cada barra** y el eje en u$s. Las barras claras (si las hay) son liquidaciones pendientes.
34. **Comparativa de mercado**: la barra de KOI en rojo y arriba; abajo S&P 500 12 %, Bonos Corporativos 8 %, Propiedades Inmobiliarias 5 %.
35. Como Administrador, ir a *Configuración → Comparativa de mercado*, cambiar el S&P 500 a **15 %**, guardar, y verificar que el reporte del inversor lo refleja. Destildar "Se muestra" en uno y verificar que **desaparece del reporte** pero **sigue en la lista de Configuración** con su valor.
36. **Prueba de aislamiento (identidad):** con un inversor, forzar `GET /MiInversion/Reporte?inversorId=<otro>` → tiene que dar **403**.

**F — importador**
37. *Importación desde Excel*: arriba aparece el bloque "¿Cuándo se usa esta pantalla?" con las dos columnas.
38. La opción "Actualizar los períodos que ya existan" viene **tildada** y el texto dice que los períodos existentes **se actualizan**.
39. En el bloque de la plantilla, la frase dice **"Acá los registros que ya existen se omiten"** con la aclaración de que es de alta, no de corrección.

#### Checklist de salida para merge
- [x] Build 0 errores; 0 advertencias nuevas (las 9 son preexistentes)
- [x] Migración de esquema única, con carga inicial idempotente y `Down()` generado
- [x] Decimales centralizados en `FormatoMoneda`, con las **tres excepciones verificadas una por una** (TC, porcentajes, puntos)
- [x] Spinners resueltos con **una** regla CSS y **un** script de `inputmode`, no vista por vista
- [x] Las **dos banderas** de `Mensual.cshtml` (`esAdmin` / `puedeGestionar`) respetadas, no unificadas
- [x] C2 y C3 con la guarda de importe 0 **en el servicio**, no sólo en el botón
- [x] Los 10 consumidores de `ConceptosGasto` auditados contra la lápida de C3 (4 corregidos, 1 era un crash real fuera de alcance)
- [x] C4 no envía nada hasta confirmar, y `EnviarMasivo` **revalida en el servidor**
- [x] Serie diaria sin romper la política de descarte de detalle (R-A03), sólo ventas cerradas
- [x] **Barrido legal por dato**, con la tabla de superficies documentada; exportables verificados (son 2 y ninguno llega al Inversor)
- [x] Cálculo del recupero **NO tocado** (P-B05); el ítem 25 se resolvió como comunicación
- [x] Bloques de atributos verificados método por método tras insertar en `EstadoResultadosController`, `NotificacionCierreController`, `ConfiguracionController`, `DashboardController` y `MiInversionController`
- [x] Meses históricos intactos
- [ ] **Commit y deploy: deliberadamente SIN hacer** — los revisa y ejecuta el dueño del estudio
- [ ] Aplicar `E21_BenchmarkMercado_E4` en producción
- [ ] Prueba manual de los 39 pasos de arriba — **el paso 25 al 30 (E1, legal) no es opcional**
- [ ] Responder P-B06 (alcance del Dashboard para el Gerente)
- [ ] Decidir con el cliente los 6 subgrupos viejos sin equivalente
- [ ] Avisar al cliente que reimportar el Excel puede devolver a la grilla un concepto que sacó del mes


### Etapa 22 — Sprint "Entrega 1: fixes y mejoras" — OLA 1 (lotes A y B) (2026-09-09)
- Alcance aprobado en `1-analista-funcional.md` §16, `2-disenador-funcional.md` §15 (15.1 y 15.2) y `3-arquitecto-mvc.md` §13 (13.2 a 13.5 y 13.10). **Gate de presupuesto SALTEADO por decisión explícita del dueño del estudio**, registrado en `trazabilidad.md` — no es un descuido del flujo.
- **Ola 1 de 2.** Los lotes C, D, E y F quedan para la Ola 2, que se ejecuta en secuencia y no en paralelo: ambas olas tocan `EstadoResultadosController` y se pisarían (§13.1).
- **1 migración EF de DATOS** (`E20_ConsolidacionCatalogos_A2`), sin cambios de esquema y sin cambios en Domain.

**Escaneo de reutilización (catalogo.yml + docs/\*/definiciones):** 2 hits, los 2 reutilizados.

| Origen | Qué se tomó | Cómo se aplicó |
|---|---|---|
| **PAT-014** — `C:\Sistemas\BlankProject` (baseline) | Flujo completo "olvidé mi contraseña": acciones `ForgotPassword`/`ResetPassword`, `PasswordResetViewModels.cs`, 3 vistas `ov-login-card` y la policy de rate limiting `"password-reset"`. | Portado tal cual. KOI no lo tenía porque se clonó **antes** de que el patrón se portara al baseline. Se conservaron las dos decisiones de seguridad del patrón (respuesta idéntica exista o no el email, y rate limiting propio) y se renombró la marca del email a "KOI Dumplings". Entrada del catálogo ya estaba con `pendiente_verificar: false` y las 3 rutas se confirmaron correctas — sin cambios al catálogo. |
| **KOI mismo** — fix `data-order` de la columna Período (Reparto General) | `data-order` numérico en la celda + `columnDefs type:'num'`. | Copiado a las 4 columnas de importe de la misma vista. Es el mismo bug en otra columna. |

**No se agregó ningún patrón nuevo al catálogo:** nada de esta ola es un componente reutilizable nuevo — son fixes de defectos y ajustes de permisos específicos de KOI.

#### A1 · Repositorio genérico que no persistía (defecto crítico, í12)
- `KoiDumplings.Infrastructure/Repositories/Repository.cs`: `AddAsync`, `UpdateAsync` y `DeleteAsync` hacían `_dbSet.X(entity); await Task.CompletedTask;` — marcaban la entidad y **nunca guardaban**. Ahora los tres llaman `await _context.SaveChangesAsync()`.
- `SaveChangesAsync()` público **se conserva** (documentado en el propio archivo): llamarlo después es inocuo porque no encuentra cambios pendientes, así que ningún consumidor que lo invoque explícito se rompe.
- **Verificación de consumidores, antes y después (`grep "IRepository<"`):** hay **dos**, no uno. `InversoresController` (único que escribe: `AddAsync`/`UpdateAsync`/`DeleteAsync`) y `UsersController`, que inyecta `IRepository<Inversor>` pero **sólo lee** (`GetByIdAsync` ×2, `GetAllAsync`). Ningún consumidor dependía de que no guardara — el cambio no tiene efecto lateral. `InversoresController` no requirió cambios.

#### A2 · Consolidación de los dos catálogos (lo más riesgoso del sprint, í8)
- Migración **de datos**: `KoiDumplings.Infrastructure/Data/Migrations/20260910014549_E20_ConsolidacionCatalogos_A2.cs`. **Ni una sentencia DDL a propósito**: en MySQL el DDL hace commit implícito y cortaría la transacción con la que EF envuelve la migración. Verificado con `dotnet ef migrations script`: el SQL sale envuelto en `START TRANSACTION; ... COMMIT;`.
- **Mapeo explícito escrito en la migración** (const `Mapeo`, derived table `UNION ALL`), nunca inferido en runtime: `12→39` Regalías, `13→40` Cánon, `22→43` Cargas Sociales. Inferir por nombre es justamente lo que no se puede hacer acá: los nombres colisionan entre los pares que hay que unir ("Regalías (3 %)" vs "Regalías (3%)").
- **Los otros 11 subgrupos viejos (14,15,16,17,18,19,20,21,28,29,30) NO SE MIGRAN** — sin equivalente claro. Quedan intactos y se reportan (paso 3.d del pre-vuelo, paso 3 del post-vuelo).
- **El total por período no se puede mover, por construcción y no por verificación posterior:** el traslado es UNA sola sentencia (`UPDATE` multi-tabla) que escribe el importe en el subgrupo destino y da de baja el concepto origen **en el mismo statement**. No existe estado intermedio con el importe en los dos lados (sumaría doble) ni en ninguno (restaría). Un par que no se puede mover no se toca y el total tampoco cambia.
- **Se respeta qué campo lee el EDR**, que depende del `TipoConcepto` del **subgrupo** y no del concepto (`EstadoResultadosService.ObtenerAsync`): Manual→`ImporteManual`, porcentual→`ImporteCalculado`. El importe se lee del campo del subgrupo ORIGEN y se escribe en el del DESTINO. Sin esto, mover un concepto entre un subgrupo manual y uno porcentual haría que el EDR leyera un campo vacío y el total se desplomara. **Este era el modo de falla real y no estaba contemplado en el diseño.**
- **Guarda de destino ocupado:** el `WHERE` sólo deja pasar destinos con importe aplicado 0. Si el destino ya tiene importe, ese par no se mueve nunca.
- **Aserción de aborto:** si después del traslado quedó vivo algún concepto de un subgrupo del mapa, la migración **falla y revierte todo**. MySQL no permite `SIGNAL` fuera de un procedimiento y crear uno sería DDL (commit implícito), así que se fuerza con un `INSERT` que sólo se ejecuta en el caso malo y está construido para fallar siempre: el mensaje va en una columna `DECIMAL` (Error 1366 con el texto visible, bajo `sql_mode` estricto) y, si el modo no fuera estricto, `PeriodoMensualId = 0` viola la FK (Error 1452). Por cualquiera de los dos caminos: excepción, rollback, base intacta.
- **Baja de los viejos recién al final** (paso 4), sólo los del mapa y sólo si ya no les quedó ningún concepto vivo.
- **`Down()`** revierte de forma simétrica y atómica, pero sólo es fiel si nadie editó importes después. El rollback autoritativo es la tabla de backup.
- **Dos scripts nuevos en `scripts/`, que son parte obligatoria del procedimiento:**
  - `A2_consolidacion_catalogos_PREVUELO.sql` — backup de `ConceptosGasto` y `Subgrupos` a tablas `_BackupA2` + foto previa del total por período (a guardar en archivo) + listado de los 14 subgrupos viejos con importe + catálogo nuevo para revisar el mapeo + **semáforo** que avisa qué par bloquea ANTES de aplicar.
  - `A2_consolidacion_catalogos_POSTVUELO.sql` — verificación **al centavo** de total por período antes vs. después (comparando contra las tablas de backup, no contra una salida copiada a mano), veredicto de una línea, listado de lo movido, listado de lo que quedó sin consolidar y bloque de reversión comentado.
  - La reversión **no** vacía `Subgrupos`: le apuntan `ParametrosPorcentaje` y `ConceptosGasto` con FK. Repone sólo las columnas de baja lógica y auditoría con un `UPDATE JOIN`.

#### A2b · Importador idempotente (í8, parte 2)
- **Hallazgo: la premisa del diseño no se sostenía contra el código.** El diseño (§15.1 A2.2) decía que al reimportar "se crea un concepto paralelo". No es así: `EscribirConceptosAsync` ya hacía upsert con clave `(período, subgrupo)` — un subgrupo que ya tenía concepto se actualiza, nunca se agrega una fila paralela. La duplicación real venía del **catálogo duplicado** (viejo 12 vs nuevo 39), que la resuelve A2.
- **La omisión real estaba a nivel PERÍODO, no concepto:** con `ActualizarExistentes = false` (el default histórico), un período ya cargado se omitía entero y reimportar no refrescaba nada.
- **Fix:** `ActualizarExistentes` pasa a `true` por defecto en `ImportacionExcelOpcionesDto` y en `ImportacionInicialViewModel` (checkbox pre-tildado). Reimportar deja la base igual al Excel. Omitir sigue siendo posible, pero ahora es una decisión explícita del operador y no el default silencioso; el motivo de omisión se reformuló para decir eso.
- **Reporte por fila nuevo/actualizado/omitido:** `PeriodoImportacionDto` suma `ConceptosNuevos` y `ConceptosActualizados`, que `EscribirConceptosAsync` incrementa, y la vista los muestra como badges en la celda de conceptos (sólo tras confirmar — en el preview todavía no se escribió nada).

#### A3 · Orden de "Util/Punto" en Reparto General (í13)
- `Views/RepartoGeneral/Index.cshtml`: `data-order` numérico en las **4** columnas de importe (Ventas, Resultado, Util/Punto, Util/Punto USD) y `columnDefs: [{ type:'num', targets:[0,1,2,3,4] }]`. El análisis nombraba sólo Util/Punto y Util/Punto USD, pero Ventas y Resultado tenían exactamente el mismo bug — el diseño dice "las celdas de importe", en plural.
- **`CultureInfo.InvariantCulture` a propósito** en el `data-order`: la app corre en es-AR y sin esto el atributo sale con coma decimal, que `parseFloat` trunca. Era el detalle que podía dejar el fix a medias.

#### A4 · `/System` fuera del menú del Administrador (í3)
- `Views/Shared/_Layout.cshtml`: eliminado el link "Sistema / Email" del bloque `Administrador || SuperUsuario`. **No hizo falta moverlo**: el bloque `SuperUsuario` ya tenía su propio link "Sistema" al mismo destino, así que mover el otro habría dejado dos links duplicados. Sin cambios de permisos: `SystemController` ya exigía `RequireSuperUsuario`.

#### B1 · Recuperar contraseña (PAT-014, í1)
- **Nuevos:** `Models/PasswordResetViewModels.cs`, `Views/Account/ForgotPassword.cshtml`, `ForgotPasswordConfirmacion.cshtml`, `ResetPassword.cshtml`.
- **`Controllers/AccountController.cs`:** 5 acciones nuevas. Se inyectaron `IEmailService` e `ILogger<AccountController>` (no estaban). Marca del email renombrada a "KOI Dumplings".
- **`Program.cs`:** policy de rate limiting `"password-reset"` (10/min por IP, igual que login).
- **`Views/Account/Login.cshtml`:** link "¿Olvidaste tu contraseña?" debajo del botón Ingresar.
- **Las dos decisiones de seguridad del patrón se conservaron intactas:** respuesta idéntica exista o no el email (anti-enumeración) y rate limiting propio. La vista de confirmación lleva un comentario explícito de que el texto está en condicional a propósito y no hay que "mejorarlo" a un mensaje afirmativo.
- **"Recuperar nombre de usuario":** en KOI el usuario **es** el email, así que no se construyó nada — se aclara en pantalla y en el email.
- **Verificado que no se cortó ningún bloque de atributos** al insertar (la trampa que ya dejó `TestEmail` sin antiforgery el 2026-09-08): las acciones se anclaron contra el bloque completo `[Authorize]/[HttpGet]/public ... Perfil()`, no contra offsets de línea, y se re-verificó el mapa atributo→método de todo el archivo después de escribir.

#### B2 · Ocultar Cámaras (í2)
- `FeatureFlags.ModuloCamaras` (mismo mecanismo que estrenó `IntegracionAyres`), en `false` en `appsettings.json` y en `appsettings.Production.json`. **El default en código también es `false`**, así que aunque no se suba el `appsettings.Production.json` (gitignoreado) las cámaras quedan ocultas igual.
- `_Layout.cshtml` inyecta `IOptions<FeatureFlags>` y esconde "Cámaras" y "Config. cámaras". La sección **"Local" entera** queda detrás del flag: es su único link, y ocultar sólo el link dejaba un header de sección vacío.
- **El módulo no se borró y sus permisos no se tocaron:** `CamarasController` sigue accesible por URL. Se reactiva poniendo el flag en `true`, sin redeploy.

#### B3 · Rol "Gerente" (í9)
- Policy nueva `GestionOperativa` = SuperUsuario + Administrador + Encargado en `Program.cs`. Se **reutiliza el rol `Encargado`** existente ampliándolo, sin crear un cuarto rol.
- **`EstadoResultadosController`: la policy se aplicó POR ACCIÓN, no al controller.** El diseño decía "controller → `GestionOperativa`", pero el controller es `[Authorize]` simple y el rol **Inversor** entra a `Anual` desde su propio sidebar ("Historial de Resultados"). Poner la policy a nivel clase le habría cortado el acceso al inversor. Resultado:
  - **8 acciones de carga/consulta** pasaron a `GestionOperativa`: `Mensual`, `GuardarVentas`, `PreviewAyres`, `AplicarAyres`, `GuardarConcepto`, `RevertirConcepto`, `Recalcular`, `ExportarAnualExcel`.
  - **3 acciones de cierre conservan `SoloAdministrador`**: `ReabrirPeriodo`, `PreviewCierre` (es el "Cerrar período" del menú; no existe una acción llamada `CerrarPeriodo`) y `ConfirmarCierre`.
  - `Anual` sigue `[Authorize]` simple, sin cambios.
- **Doble barrera de cierre, como pide §13.5:** además de la policy en la acción, `EstadoResultadosService.CerrarPeriodoAsync` y `ReabrirPeriodoAsync` arrancan con `PuedeCerrarPeriodoAsync(userId)`, un helper nuevo que consulta `_db.UserRoles`/`_db.Roles` y sólo deja pasar Administrador y SuperUsuario. Ocultar el botón no es control de acceso cuando lo que se dispara son pagos.
- **`Views/EstadoResultados/Mensual.cshtml`:** la vista usaba una sola bandera `esAdmin` para todo. Se partió en dos: `esAdmin` sigue gobernando los botones de **cierre/reapertura** (3 usos) y `puedeGestionar` (= esAdmin + Encargado) gobierna la **carga** (8 usos). Sin este split el Encargado veía el EDR en sólo lectura y no podía cargar nada, que es justo lo que el rol tiene que poder hacer.
- **`NotificationsController`: NO requirió cambios — la premisa del análisis no se sostenía.** §16.6 y §13.5 dan por hecho que es `SoloAdministrador` y que la campanita le daría 403 al Encargado en toda pantalla. En el código real la clase es `[Authorize]` simple y sólo `Crear`/`UsuariosPorRol`/`Enviar` son `SoloAdministrador`. La campanita (`Index`, `GetRecent`, `MarkAsRead`, `MarkAllAsRead`) ya funcionaba para el Encargado. **No se amplió nada**: hacerlo le habría abierto el compositor de notificaciones a inversores, que no es suyo.
- **Sidebar del Encargado** (bloque excluyente, ya existía): pasa de ver sólo Fichador a ver KOI (Dashboard, Notificaciones) + Gestión (Estado de Resultados, Historial de Resultados, Fichador). **No** ve Inversores, Puntos, Liquidaciones, Reparto General, Configuración, Usuarios ni System — esos controllers siguen en `SoloAdministrador`/`RequireAdministracion` y le darían 403.

#### Evidencia de build
- `dotnet build` desde la raíz → **Compilación correcta, 0 errores**, 9 advertencias, **todas preexistentes** y ninguna introducida por esta ola: 8× NU1902 (MailKit 4.14.1 / MimeKit 4.14.0 — VUL-001, pendiente) y 1× CS0114 (`HomeController.StatusCode`).
- `dotnet ef migrations script E19 → E20` render OK: SQL válido y envuelto en `START TRANSACTION; ... COMMIT;`.
- **Sin smoke test funcional** (regla del rol). No hay proyecto de tests en el repo. La guía de prueba manual va abajo.

#### Riesgos y supuestos
- **R-B01 (alto) — A2 sobre plata ya liquidada.** Mitigado por construcción (traslado atómico) + guarda de destino + aserción de aborto + pre/post-vuelo. **La migración no se aplica sin correr el pre-vuelo primero.**
- **Los ids del mapeo (12,13,22 → 39,40,43) son los verificados en producción en agosto 2026.** Si los ids de la base donde se aplique no coinciden, el paso 3.c del pre-vuelo lo muestra antes de tocar nada.
- **Quedan 11 subgrupos viejos sin consolidar.** La duplicación visual del EDR histórico persiste para ellos hasta que el cliente decida su equivalencia. **Requiere conversación con el cliente.**
- **P-B06 sigue abierta** ("¿el Gerente debe ver el Dashboard completo, con importes de resultado?"). Se le dio acceso al Dashboard porque el diseño dice "ve KOI + Gestión" y `DashboardController` ya era `[Authorize]` simple (o sea, el Encargado ya entraba por URL antes de este sprint — lo único nuevo es el link). Si la respuesta del cliente es "no", el cambio es sacar el link y poner `GestionOperativa`/`ConsultaDashboard` en el controller.
- `appsettings.Production.json` está gitignoreado: el bloque `Features` con `ModuloCamaras` hay que subirlo a mano. Sin él igual queda oculto (default `false` en código).
- **La Ola 2 vuelve sobre archivos de esta ola**: `EstadoResultadosController`, `Views/EstadoResultados/Mensual.cshtml` y `Views/ImportacionInicial/Index.cshtml`. Se ejecuta **después**, nunca en paralelo.

#### Guía de prueba manual (para el dueño del estudio / QA)
**Antes de nada: A2 no se aplica sin backup.**
1. **A1 —** Entrar como Administrador a *Inversores*. Editar el nombre de un inversor y guardar. **Recargar la pantalla y releer el registro** (no confiar en el cartel de éxito, que es lo que enmascaraba el bug). El nombre tiene que haber cambiado. Repetir con alta y con baja.
2. **A3 —** *Reparto General*: ordenar por "Util/Punto" y por "Util/Punto USD", ascendente y descendente. Los importes tienen que ordenar como números (no "1.000" antes que "9"). Probar también Ventas y Resultado.
3. **A4 —** Entrar como **Administrador** (no SuperUsuario): en el sidebar, sección Sistema, **no** tiene que estar "Sistema / Email". Entrar como SuperUsuario: "Sistema" sigue estando, una sola vez.
4. **B2 —** Con cualquier rol: no tiene que aparecer la sección "Local" ni "Config. cámaras". Poner `Features:ModuloCamaras = true` en `appsettings.Production.json`, reiniciar el sitio y verificar que vuelven a aparecer.
5. **B1 —** En *Login*, "¿Olvidaste tu contraseña?" → cargar un email **existente** → llega el mail con marca "KOI Dumplings" → seguir el link → poner contraseña nueva → iniciar sesión con ella.
6. **B1 anti-enumeración —** Repetir con un email **inexistente**: la pantalla de confirmación tiene que ser **exactamente la misma**. Si difiere en algo, es un defecto de seguridad.
7. **B1 token de un solo uso —** Volver a abrir el link ya usado: tiene que rechazarlo con "el link no es válido o venció".
8. **B3 carga —** Con un usuario **Encargado**: entrar a *Estado de Resultados*, cargar ventas y editar un importe de gasto. Tiene que poder.
9. **B3 barrera de cierre (lo importante) —** Con el mismo Encargado: el botón "Cerrar período" **no** tiene que aparecer. Y forzando la URL `POST /EstadoResultados/ConfirmarCierre` y `POST /EstadoResultados/ReabrirPeriodo` tiene que dar **403**. Es control de acceso, no UI.
10. **B3 sidebar —** Con el Encargado: **no** tienen que verse Inversores, Puntos, Liquidaciones, Reparto General, Configuración, Usuarios ni System. La **campanita** de notificaciones tiene que funcionar en toda pantalla (no 403).
11. **A2 —** Correr `scripts/A2_consolidacion_catalogos_PREVUELO.sql`. Verificar el backup, **guardar la foto previa a archivo** y mirar el semáforo (3.c). Si alguna fila dice "BLOQUEA", **frenar** y avisar.
12. **A2 —** Aplicar `dotnet ef database update`. Después correr `A2_consolidacion_catalogos_POSTVUELO.sql`: el paso 1.b tiene que decir **0 períodos con diferencia**. Si dice otra cosa, revertir con el paso 4 y avisar.
13. **A2 —** En el EDR de un mes histórico (ej. agosto 2026), verificar que "Regalías", "Cánon" y "Cargas Sociales" aparecen **una sola vez** y con el importe histórico, y que el **Total de Gastos del mes es idéntico** al de antes.
14. **A2b —** Reimportar el mismo Excel dos veces seguidas. La segunda no tiene que cambiar ningún total, y el reporte por fila tiene que mostrar los conceptos como **actualizados** (no nuevos).

#### Checklist de salida para merge
- [x] Build 0 errores; 0 advertencias nuevas
- [x] `SaveChangesAsync()` público conservado y consumidores del repositorio verificados antes y después
- [x] Migración de datos sin DDL, transaccional, con mapeo explícito, guarda de destino, aserción de aborto y `Down()`
- [x] Scripts de pre-vuelo (backup + foto previa + semáforo) y post-vuelo (verificación al centavo + reversión)
- [x] Barrera de cierre en **acción y en servicio**, no sólo en la vista
- [x] Bloques de atributos verificados método por método tras insertar en `AccountController`
- [x] Credenciales sólo en `appsettings.Production.json` (gitignoreado); no se agregó ninguna al repo
- [x] Meses históricos intactos salvo A2, que va con verificación al centavo
- [ ] **Commit y deploy: deliberadamente SIN hacer** — los revisa y ejecuta el dueño del estudio
- [ ] Prueba manual de los 14 pasos de arriba
- [ ] **Aplicar E20 en producción con backup previo y verificación post** (paso 11-13)
- [ ] Decidir con el cliente los 11 subgrupos viejos sin equivalente
- [ ] Responder P-B06 (alcance del Dashboard para el Gerente)
- [ ] Ola 2 (lotes C, D, E, F) — en secuencia, nunca en paralelo con esta


### Etapa 21 — Integración Ayres POS (E2-01, Fase 6) (2026-09-08)
- Alcance aprobado en `1-analista-funcional.md` §15 (Discovery + Análisis, R-A01 cerrado en §15.10), `2-disenador-funcional.md` §14 (8 historias HU-A01..HU-A08) y `3-arquitecto-mvc.md` §12. **Gate de presupuesto SALTEADO por decisión explícita del dueño del estudio** ("implementar, saltear presupuesto"), registrado en `trazabilidad.md` — no es un descuido del flujo.
- **Sin cambios en Domain. Sin migración EF.** Las ventas se escriben en `VentasMensuales`, que ya existía.

**Escaneo de reutilización (catálogo + docs/\*/definiciones):** 3 hits, los 3 reutilizados.

| Origen | Qué se tomó | Cómo se aplicó |
|---|---|---|
| **marihogar** — `MariHogar.Infrastructure/Services/AfipTokenCache.cs` (PAT-006) | Cache de token con vigencia informada por el servidor | **Portado y adaptado** a `AyresTokenCache`: de la tupla `(Token, Sign)` de WSAA a un único JWT, y de `expirationTime` (DateTime) a `aliveTime` (segundos). Se conservaron las 4 decisiones del patrón: vigencia del servidor, margen de seguridad (60 s acá, 10 min en AFIP), `SemaphoreSlim` + doble chequeo dentro del lock, e `Invalidar()` con **un solo** reintento. **Se extrajo como patrón propio `PAT-024`** en `docs/patrones/catalogo.yml`: ya tiene 2 implementaciones en dominios que no comparten nada (AFIP y un POS gastronómico), así que dejarlo enterrado dentro de PAT-006 (facturación electrónica) lo hacía invisible para el próximo que lo necesite. |
| **KOI mismo** — `QuickPassService` / `QuickPassSettings` / `QuickPassIndisponibleException` (Etapa 12) | Convenciones internas de integración con API externa | **Estructura copiada tal cual, renombrada**: cliente nombrado por `IHttpClientFactory`, POCO de settings estilo `SmtpSettings`, excepción de dominio propia, DTOs crudos privados anidados en el servicio, datos en vivo sin persistencia local. Evita que el proyecto tenga dos estilos distintos de integración. |
| **PAT-012** — Importación con preview → confirmar | Separar *analizar* de *persistir*, no pisar lo que el usuario administra a mano | **Flujo de dos pasos reutilizado, sin el staging**: acá la fuente es una API, no un archivo, así que al confirmar se **re-consulta**. Se agregó esta variante como `archivo_referencia` de PAT-012 en el catálogo. |
| **No reutilizado:** el chunking de QuickPass | — | Aquel parte por 31 días sobre otro endpoint; acá el límite es 10 días y la agregación es propia. Escrito nuevo, mismo estilo. |

**Application**
- `DTOs/AyresDtos.cs` (nuevo): `CanalesAyres` (constantes Salon/Pedidos/Mostrador/Otros), `VentasPeriodoAyresDto` (agregado del mes + KPIs como propiedades calculadas), `VentasCargadasDto` (lo que hay en el sistema, **solo lado A**) y `PreviewVentasAyresDto` (comparativo, con `HayDiferencias`).
- `Interfaces/IAyresService.cs` (nuevo): `ObtenerVentasPeriodoAsync(anio, mes, ct)`, `ProbarConexionAsync(ct)` y `EstaConfigurado`. **`EstaConfigurado` es un agregado deliberado al contrato de §14.3**: sin él, la capa Web tendría que inyectar `AyresSettings` (Infrastructure) solo para decidir si renderiza un botón.
- `Exceptions/AyresIndisponibleException.cs` (nuevo): mismo criterio que `QuickPassIndisponibleException` **más un flag `EsCredenciales`**, que separa "no llegué a Ayres" (red/puerto/DNS — el síntoma de D-A01) de "Ayres me atendió y rechazó el usuario". Son dos problemas con dos responsables distintos y el mensaje al usuario tiene que distinguirlos.
- `Settings/FeatureFlags.cs`: `IntegracionAyres` (default `false`). **Primer flag real del scaffold**, que hasta hoy estaba vacío.

**Infrastructure**
- `Services/AyresSettings.cs` (nuevo): `BaseUrl` (con el puerto adentro — el 8520 es config, no código), `Email`, `Pass`, `IdSucursal`, `TimeoutSeconds` (60), `DiasPorConsulta` (10) y `MapeoCanales` (diccionario `OrdinalIgnoreCase` con ME/PE/MO por defecto). `EstaConfigurado` chequea BaseUrl + credenciales.
- `Services/AyresTokenCache.cs` (nuevo, **Singleton**): ver PAT-024. `ObtenerAsync(loginFactory, ct)` recibe el login como delegate, así el cache no sabe nada del protocolo de Ayres. Si `aliveTime <= 0` el token queda vencido de entrada (degrada a un login por llamada, que es lento pero correcto) en vez de inventarle una duración.
- `Services/AyresService.cs` (nuevo, **Scoped**): login, chunking secuencial, agregación y mapeo de canales.
- `DependencyInjection.cs`: `Configure<AyresSettings>`, cliente nombrado `"Ayres"` (BaseAddress normalizada con `TrimEnd('/') + "/"`, Accept JSON, timeout de config), `AddSingleton<AyresTokenCache>()` y `AddScoped<IAyresService, AyresService>()`, con el comentario del error de ciclo de vida al lado del registro.

**Web**
- `Controllers/EstadoResultadosController.cs`: se inyectan `IAyresService` e `IOptions<FeatureFlags>`. `Mensual` setea `vm.AyresHabilitado = flag && configurado && !cerrado`. Dos acciones nuevas, ambas `[Authorize(Policy = "SoloAdministrador")]` + `[HttpPost, ValidateAntiForgeryToken]`:
  - `PreviewAyres(anio, mes)` → consulta Ayres y devuelve el comparativo. **No escribe.**
  - `AplicarAyres(anio, mes, totalPreview, cantidadPreview, forzar)` → re-consulta, y si difiere de lo previsualizado devuelve `requiereConfirmacion` con los números nuevos en vez de escribir. Si coincide (o `forzar`), llama a `GuardarVentasAsync` y devuelve **la misma forma JSON que `GuardarVentas`**, para reusar el repintado que ya existía en el cliente.
  - Helpers privados: `ValidarAyresDisponibleAsync` (flag + configurado + mes válido + período abierto), `MapearVentasCargadas`, `SerializarVentasAyres`, `ArmarAdvertenciasAyres`, `EsMesEnCurso` (huso AR, no el del hosting).
- `Controllers/SystemController.cs`: **eliminado `DiagnosticoAyres`** con sus ramas `?ping=` y `?puertos=` (era temporal, existía solo para responder R-A01), junto con `IHttpClientFactory` e `IConfiguration`, que se habían inyectado únicamente para él. En su lugar, `ProbarAyres` (`[HttpPost]` + `[ValidateAntiForgeryToken]`) sobre `IAyresService.ProbarConexionAsync` (HU-A08). **Se verificó que el bloque de atributos de `TestEmail` quedó pegado a `TestEmail`** — es el incidente de esta misma mañana, cuando un método insertado en este controller partió ese bloque y dejó `TestEmail` sin antiforgery. Chequeo de cierre: `HttpPost`/`ValidateAntiForgeryToken` en líneas 95-96 → `TestEmail` en 97; 176-177 → `ProbarAyres` en 178.
- `Models/EstadoResultadosViewModels.cs`: `ErMensualViewModel.AyresHabilitado`.
- `Models/SystemIndexViewModel.cs`: `AyresConfigurado` + `AyresBaseUrl` (sin credenciales, solo para mostrar contra qué se prueba).
- `Views/EstadoResultados/Mensual.cshtml`: botón **"Traer de Ayres"** (`btn-outline-primary`, `fa-cloud-arrow-down`) como acción **secundaria** debajo de "Guardar ventas", que sigue siendo la primaria. Modal de preview con SweetAlert2 —misma convención que el diálogo de reapertura de la Etapa 17, en este mismo archivo—: tabla comparativa con las filas que cambian resaltadas y las iguales en gris, KPIs (ticket promedio, venta por cubierto, ítems por venta), pie "se leyeron N ventas entre X e Y en Z consultas" y bloque de advertencias.
- `Views/System/Index.cshtml`: tarjeta "Conexión con Ayres POS" con tres desenlaces visualmente distintos (verde = conecta, amarillo = credenciales, rojo = inalcanzable).

**Config**
- `appsettings.json` (versionado): sección `Ayres` **con credenciales vacías** + `MapeoCanales` + `Features.IntegracionAyres: false`. Mismo criterio que QuickPass.
- `appsettings.Production.json` (**gitignoreado, no se commitea**): ya tenía las credenciales; se le agregaron `TimeoutSeconds`, `DiasPorConsulta`, `MapeoCanales` y `Features.IntegracionAyres: true`. **Ese archivo se sube a mano al hosting: si el que está en el servidor no recibe el bloque `Features`, el flag queda en `false` y el botón no aparece aunque el deploy esté bien.**

**Decisiones de implementación que conviene no reabrir**
- **La escritura no duplica nada.** `AplicarAyres` llama a `GuardarVentasAsync`, el mismo método del guardado manual. De ahí salen gratis el recálculo de porcentuales, la validación de período cerrado y el respeto de los overrides manuales de la Etapa 19. Cero lógica financiera nueva.
- **El lado B (informal) no se toca.** Ayres no lo informa. `AplicarAyres` lee el período y **re-envía los valores B que ya estaban** en el mismo DTO, porque `GuardarVentasAsync` escribe las 8 columnas: pasar 0 los habría borrado en silencio.
- **Al confirmar se re-consulta la API**, no se guarda el preview en sesión. Y si la reconsulta difiere, se pregunta de nuevo con los números nuevos. La comparación usa **tolerancia de $0,01**: el cliente manda el total con `toFixed(2)` y una diferencia de redondeo no es "los números cambiaron" — sin la tolerancia, ese caso dejaría al usuario sin poder aplicar nunca.
- **Chunking secuencial con descarte de detalle.** Un `AgregadorVentas` privado acumula por tramo y el detalle del tramo (ventas con sus `items[]`) queda sin referencias al terminar cada vuelta. Agosto 2026 = 4 tramos (1-10, 11-20, 21-30, 31).
- **Fechas asimétricas.** Se envían `yyyy-MM-dd` y vuelven `dd/MM/yyyy`: dos constantes distintas y `DateOnly.TryParseExact` con `InvariantCulture`. Nunca `DateTime.Parse` por cultura del servidor.
- **El sobre viene anidado** (`content.ventas[i].venta.*`). Todos los DTOs crudos llevan `[JsonPropertyName]` explícito, y hay un guard extra: si un tramo trae elementos pero **ninguno** con nodo `venta` adentro, se lanza excepción en vez de devolver 0 ventas en silencio. Un campo mal mapeado da 0 sin error, que es exactamente el modo de falla peligroso acá.
- **Deserialización tolerante a números como string** (`JsonNumberHandling.AllowReadingFromString`): si Ayres empieza a mandar `"63131109.00"`, el agregado sigue funcionando en vez de romper a mitad de una importación.
- **Canal desconocido → "Otros" + advertencia** (HU-A07), nunca descarte silencioso ni excepción. La advertencia dice explícitamente que ese importe **no se aplica a ninguna columna** y que hay que agregar el mapeo en configuración.
- **`estado` (R-A04): se cuenta, no se filtra.** El agregado lleva `VentasPorEstado` y el preview advierte si aparece algo distinto de `'C'`. En agosto el total cerró al centavo, así que aparentemente no hay anuladas — pero eso no está probado, y filtrar por una regla no validada era peor que informarla.
- **Reintento único ante token rechazado.** Se detecta por HTTP 401/403 **o** por `resultCode = UNAUTHORIZED_ACCESS` leído del sobre parseado (no por buscar el texto suelto en el cuerpo, que daría falso positivo si el string apareciera en un dato).
- **El token nunca se loguea ni se devuelve.** Ante un JSON ilegible se loguea el tamaño del cuerpo, no el cuerpo: en `/login` ahí adentro viene el token.

**Build:** `dotnet build` desde la raíz → **Compilación correcta, 0 errores**. 9 advertencias, todas preexistentes (NU1902 MailKit/MimeKit — VUL-001 — y CS0114 `HomeController.StatusCode`). Ninguna introducida por esta etapa. Rebuild completo del proyecto Web para forzar la compilación de las vistas Razor: 0 errores.

**Guía de prueba manual (la ejecuta el dueño del estudio)**

> Requiere el `appsettings.Production.json` con el bloque `Features.IntegracionAyres: true` subido al hosting. Para probar en local hace falta cargar la sección `Ayres` por *user secrets* (`dotnet user-secrets set "Ayres:BaseUrl" ...`), **nunca** en `appsettings.Development.json`, que está versionado.

1. **Conexión (HU-A08).** Herramientas del Sistema (SuperUsuario) → tarjeta "Conexión con Ayres POS" → "Probar conexión". Esperado: alerta **verde** con el tiempo de respuesta. Verificar de paso que la tarjeta de email sigue enviando (confirma que no se rompió el antiforgery de `TestEmail`).
2. **El diagnóstico viejo ya no existe.** Navegar a `/System/DiagnosticoAyres`, `/System/DiagnosticoAyres?ping=1` y `?puertos=1`. Esperado: **404** en los tres.
3. **Preview sin escribir (HU-A01/A02) — el caso de aceptación duro.** Estado de Resultados → un período **abierto** → "Traer de Ayres". Sobre **agosto 2026**, el preview tiene que dar **1.062 ventas**, total **63.131.109,00**, `ME`/Salón **52.404.760,00**, `PE`/Pedidos **8.293.849,00**, `MO`/Mostrador **2.432.500,00** y **1.735** comensales. Pie: "4 consulta(s) a Ayres". **Cancelar** y verificar que la pantalla quedó **exactamente** igual (recargar y comprobar que los importes no cambiaron).
4. **Aplicar (HU-A03/A04).** Repetir y esta vez **Aplicar**. Esperado: mensaje de éxito, la página se recarga, las ventas quedan con esos valores y los conceptos porcentuales se recalcularon solos. Anotar el Resultado del Ejercicio antes y después.
5. **El lado B no se pisa.** Antes de aplicar, cargar a mano un valor en "Ventas B Salón" (ej. 1.000) y guardar. Aplicar Ayres. Esperado: **el valor B sigue ahí**.
6. **Período cerrado (HU-A06).** Ir a un mes cerrado: el botón **no aparece**. Con las herramientas del navegador, forzar un POST a `/EstadoResultados/AplicarAyres` con ese anio/mes: tiene que responder "El período está cerrado." y no escribir.
7. **Mes en curso.** Traer el mes actual: el preview tiene que mostrar el aviso azul "El mes todavía no terminó: el total es parcial."
8. **Mes sin ventas.** Traer un mes futuro o muy viejo sin datos: diálogo informativo "Ayres no devolvió ventas para este período." **sin** botón Aplicar.
9. **Caída de la API (HU-A05).** Apagar la regla de puerto saliente en el panel del hosting (o cambiar `Ayres:BaseUrl` a un puerto muerto) y pulsar "Traer de Ayres". Esperado: "No se pudo conectar con Ayres. El período quedó sin cambios.", el período intacto, y en el log de errores el detalle técnico con la mención a D-A01. **Restaurar la regla al terminar.**
10. **Credenciales (mensaje distinto).** Cambiar `Ayres:Pass` por algo inválido y probar la conexión desde Herramientas del Sistema. Esperado: alerta **amarilla** "Ayres rechazó las credenciales. Revisá la configuración." — distinta de la de red. **Restaurar la clave.**
11. **Feature flag.** Poner `Features.IntegracionAyres: false` y recargar el Estado de Resultados: el botón **desaparece** sin redeploy. Volver a `true`.
12. **Un solo login por importación.** Con el log en `Information`, mirar `Logs/`: una importación de un mes tiene que dejar **un** "login OK" y **un** "período ... resuelto en 4 tramos". Si aparecen 4 logins, los ciclos de vida de DI quedaron invertidos.

**Pendientes de esta etapa**
- Prueba manual (guía de arriba) — **no se ejecutó smoke test propio**, por regla del rol.
- **Commit y deploy**: deliberadamente sin hacer, los ejecuta el dueño del estudio después de revisar.
- Recordar subir el `appsettings.Production.json` actualizado (bloque `Features`) — es gitignoreado, no viaja con el commit.
- P-A09 (¿se corrigen el desglose por canal y la cantidad de ventas de los períodos históricos mal cargados?) sigue **abierta con el cliente**. Este módulo no toca meses cerrados.
- R-A02 sigue abierto: la API va por HTTP plano y la credencial viaja en el body. No se resuelve desde este código; es tema para el cliente / MaxiSistemas.
- D-A01: la regla de salida del hosting apunta a la IP fija `190.245.226.181`. Si Ayres migra de servidor, la integración se corta y el síntoma es un `SocketException`/WSAEACCES. Está documentado en el XML-doc de `AyresSettings` y en el log del error de red.

### Etapa 18 — Estado de Resultados mensual: edición inline de gastos por AJAX (2026-09-08)
- Pedido textual del dueño del estudio: *"el importe de los gastos se debe poder modificar on demand via ajax en vez de post"*. Refactor de UI acotado sobre una pantalla ya aprobada (P-03), autorizado directamente: sin entidades nuevas, sin migración EF, sin endpoint nuevo. Reemplaza el flujo botón-lápiz → modal SweetAlert2 → `$.post` → `window.location.reload()` por un `<input type="number">` inline que guarda solo al salir del campo.
- **Escaneo de reutilización:** `docs/patrones/catalogo.yml` no tiene una entrada de "edición inline por celda con auto-save" (la entrada existente cubre *acciones* de listado DataTables por AJAX, no edición de campos). Escaneo de `docs/*/definiciones/5-implementador.md` → 2 hits reales: (a) **marihogar CR-61** (`MariHogar.Web/Views/Stock/Index.cshtml`, `StockController.ActualizarStock`) — inline `<input type="number">` + `$.post` con `RequestVerificationToken`, `data-valor-anterior` para no guardar sin cambios, revert al valor previo ante error, y flash de borde verde/rojo (`destello`) en vez de toast por guardado OK; (b) **vinosefue** (ítems de compra editables inline con auto-save), mismo patrón, menos documentado. **Decisión: reutilizar el patrón de marihogar adaptándolo**, no copiar el archivo (marihogar renderiza las filas desde DataTables server-side y KOI las renderiza en Razor, y el endpoint de KOI ya existía). Se adaptaron: comparación contra `data-valor-anterior`, revert + foco en error, flash de borde y guardado por fila. **Divergencia deliberada:** marihogar bloquea el input con `disabled` durante el guardado; acá se usa `readonly`, porque `disabled` roba el foco y rompe el recorrido con Tab en el caso de uso real (cargar ~40 gastos seguidos). No se agregó una entrada nueva al catálogo: el patrón todavía no es un componente reutilizable (es JS por pantalla), pero ya tiene 3 implementaciones y es candidato a catalogar si aparece una cuarta.
- **Web — `Controllers/EstadoResultadosController.cs`:**
  - `GuardarConcepto` suma los parámetros `anio` y `mes` (mismo criterio que `Recalcular`, que ya los recibe) y devuelve los totales recalculados vía `ObtenerAsync(anio, mes)`: `importeAplicado` (del concepto guardado), `totalGastos`, `resultado`, `resultadoUsd` y `rubros[] { rubroId, totalRubro }`. Se respetó **exactamente** la convención de nombres de `GuardarVentas`/`Recalcular`; `rubros[]` es el único agregado, porque el subtotal por rubro no estaba expuesto por ningún endpoint. **No se agregó `rentabilidad`**: no existe en `EstadoResultadosDto`, no la devuelve ningún otro endpoint AJAX de esta vista y la pantalla Mensual no la muestra (sí la muestra el Dashboard, con su propio DTO) — habría sido un campo JSON sin consumidor.
  - La escritura sigue validándose **contra `periodoId`** dentro de `GuardarConceptoGastoAsync` (período existe / no cerrado / subgrupo manual). `anio`/`mes` solo alimentan la relectura de totales, así que un desfasaje entre ambos afectaría lo que se muestra, nunca lo que se guarda. Queda comentado en el código.
  - **Eliminada la línea muerta** `var periodo = await _erService.RecalcularPorcentualesAsync(0, 0); // no-op` — se llamaba con `anio=0, mes=0` (siempre "Periodo no encontrado") y su resultado se descartaba. Confirmado leyendo `EstadoResultadosService.GuardarConceptoGastoAsync`: **no recalcula los porcentuales**, y no hace falta que lo haga — los conceptos calculados dependen de `VentasA`/`VentasTotales`, no de los gastos manuales. Por eso el endpoint no necesita devolver el array `conceptos` completo.
- **Web — `Views/EstadoResultados/Mensual.cshtml`:**
  - Variable `puedeEditarConcepto` (`esAdmin && !EsCerrado && !EsCalculado && !EsInactivo`) calculada una vez por fila y usada en las dos celdas. Si es editable, la celda de importe rinde el `<input type="number" step="0.01" min="0">` con `value` y `data-valor-anterior` en `F2`/`InvariantCulture`; si no, el importe sigue siendo texto dentro de un `<span class="ov-monto">` (período cerrado, concepto calculado, concepto histórico, o inversor).
  - La 5ª columna deja de ser la del lápiz y pasa a ser el indicador de guardado por fila (`<span class="estado-concepto" aria-live="polite">`, ancho fijo `2.25rem`, `<th>` con `visually-hidden`). Feedback discreto: spinner mientras guarda → check verde + borde verde que se desvanece a 1,8 s. **SweetAlert2 queda solo para errores**, como pide el pedido: un toast de éxito por gasto sería invasivo cargando 40 filas.
  - Botón `.btn-editar-concepto` y su handler/modal eliminados por completo. Nota en el card header ("Los importes se guardan solos al salir del campo") porque al desaparecer el botón de guardar el usuario necesita saber cuándo se persiste.
  - **Formato numérico:** el input manda punto decimal y el server corre en `es-AR`, pero eso ya está resuelto globalmente por `KoiDumplings.Web/ModelBinders/InvariantDecimalModelBinder.cs` (registrado en `Program.cs` con `ModelBinderProviders.Insert(0, ...)`, aplica a `decimal`/`decimal?` incluidos los parámetros sueltos de acción). Mismo camino que ya usan los inputs de ventas de esta pantalla. **No hizo falta tocar nada.**
  - **Bug latente corregido de paso:** los handlers de `GuardarVentas` y `Recalcular` hacían `row.find('.importe-cell').text(...)`, que ahora **borraría el `<input>`** de los conceptos manuales. Se extrajo el helper `pintarImporteConcepto(row, valor)`, que escribe en el input o en el `<span class="ov-monto">` según corresponda, y **nunca pisa un campo con foco o con un guardado en curso** (evita que una respuesta lenta borre lo que el usuario está tipeando en otra fila). Los tres handlers lo usan.
- **Manejo de errores (todos revierten el input al último valor guardado y devuelven el foco al campo al cerrar el diálogo):** importe no numérico o negativo (validación local, sin request); `success: false` del servicio (período cerrado, subgrupo calculado, subgrupo inexistente) con el mensaje real; **sesión perdida** — con `LoginPath = "/Account/Login"` el pipeline responde 302 y el XHR lo sigue, así que llega HTML y no JSON: se detecta con `typeof res !== 'object'` y se avisa "Sesión expirada… el importe no se guardó"; 401/403 y fallo de red en el `.fail`. Sin `location.reload()` en ningún camino.
- **Sin migración EF** — confirmado: `git status` muestra únicamente `Controllers/EstadoResultadosController.cs` y `Views/EstadoResultados/Mensual.cshtml`. Ni Domain, ni `KoiDumplingsDbContext`, ni `Infrastructure/Data/Migrations/`.
- **Build:** `dotnet build` desde la raíz → Compilación correcta, **0 errores**, 9 warnings **todos preexistentes** (`CS0114 HomeController.StatusCode` + 8 `NU1902` de MailKit/MimeKit, ver VUL-001). El proyecto no tiene `AddRazorRuntimeCompilation`, así que las vistas Razor se compilan en el build: el build limpio también es evidencia de que la sintaxis de la vista es válida. Sigue sin haber proyecto de tests en el repo.
- **Sin smoke test funcional** (regla del estudio). Guía de prueba manual, sobre un período **abierto** y con usuario Administrador:
  1. Abrir Estado de Resultados de un mes abierto. Verificar que los conceptos **manuales** muestran un campo editable y que los **calculados por %**, los marcados como **Histórico** y todo el resto siguen siendo texto.
  2. Cambiar un importe manual y salir del campo con Tab. Esperado: spinner → check verde y borde verde que se desvanece, **sin diálogo de éxito y sin que la página recargue**. El subtotal del rubro, "Total Gastos" y "Resultado Ejercicio" (con su color y el valor en USD) se actualizan solos.
  3. Volver a entrar al mismo campo y salir **sin cambiar nada**. Esperado: no pasa nada — sin spinner, sin request (verificable en la pestaña Red del navegador).
  4. Cargar 5 o 6 gastos seguidos moviéndose solo con Tab. Esperado: el foco nunca se pierde ni salta, y cada fila confirma por separado.
  5. Recargar la página (F5) y confirmar que todos los importes cargados quedaron persistidos.
  6. Escribir un negativo (`-100`) y salir del campo. Esperado: error de SweetAlert2, el importe vuelve al valor anterior y el foco vuelve al campo con el texto seleccionado.
  7. **Caso de error / sesión perdida:** con la pantalla abierta, cerrar sesión desde **otra pestaña** del mismo navegador; volver a la pantalla del ER y modificar un importe. Esperado: **"Sesión expirada — Se cerró la sesión, el importe no se guardó"**, el campo vuelve al valor anterior y ningún total se mueve. Al iniciar sesión de nuevo y recargar, ese importe debe seguir con el valor **viejo** (nada quedó a medias).
  8. Abrir un período **cerrado**: los importes tienen que verse como texto, sin campos editables ni columna de estado.
  9. Con un usuario **Inversor**, abrir la pantalla: sin campos editables.
  10. Regresión de lo que convive en la misma pantalla: "Guardar ventas" y "Recalcular %" siguen funcionando y **no dejan celdas de gasto en blanco** al refrescar la tabla.
- **Riesgos y supuestos:** (a) **sin commit ni deploy** (pedido explícito); (b) la validación es por revisión de código y build, no contra una base ni un navegador; (c) el guardado es por fila y sin transacción entre filas — es lo pedido y lo correcto acá, pero implica que una carga masiva interrumpida a la mitad deja las filas anteriores ya guardadas (mitigado: cada fila confirma visualmente); (d) `anio`/`mes` viajan desde el cliente solo para releer totales, nunca para decidir dónde escribir; (e) al no haber ya un botón "Guardar" en gastos, un usuario que cierre la pestaña **con el foco todavía dentro del campo** y sin salir de él pierde ese último importe — el navegador no dispara `change`; se mitigó con la leyenda del header y no se agregó un `beforeunload` para no molestar en el uso normal.
- **Checklist de merge:** [x] build 0 errores · [x] sin warnings nuevos · [x] sin migración EF · [x] antiforgery en el POST (header + campo, y `[ValidateAntiForgeryToken]` intacto) · [x] policy `SoloAdministrador` intacta en el endpoint · [x] sin `Console.WriteLine` · [x] Serilog con placeholders (el `LogInformation` del servicio no se tocó) · [x] SweetAlert2 solo para errores · [x] texto visible con tildes y ortografía revisada · [x] `.ov-monto` conservado en los importes que siguen siendo texto · [ ] prueba manual del dueño del estudio · [ ] commit y deploy (deliberadamente pendientes).

### Etapa 17 — Reapertura de períodos cerrados (reemplaza el enfoque de la Fase 4) (2026-09-07)

**Alcance.** Reapertura de un período cerrado por el Administrador: `Cerrado → Abierto`, descartando las liquidaciones generadas en el cierre. **Reemplaza el enfoque de la Fase 4 del `plan-implementacion.md`** ("editar el mes cerrado en el lugar recalculando las liquidaciones pendientes"): con la reapertura ya no hace falta, el flujo pasa a ser **reabrir → editar con las pantallas normales → volver a cerrar**. Los guards de período cerrado de `GuardarVentas` y `GuardarConceptoGastoAsync` **quedan intactos** (no se editan meses cerrados; se reabren).

**Revierte D-04.** La decisión D-04 de junio ("el período no puede reabrirse una vez cerrado") queda revertida por pedido explícito posterior del cliente — el camino ya estaba anticipado en Análisis §14.1 ítem 3 y en `4-presupuestador.md` §383. Detalle en `trazabilidad.md` (entrada 2026-09-07, Etapa 17). El enum `EstadoPeriodo` **no cambia**: sigue con `Abierto`/`Cerrado`, la reapertura es una transición, no un estado nuevo. D-30 (reabrir una liquidación individual) sigue vigente sin cambios.

**Decisión del cliente (tomada antes de implementar): "reabrir y regenerar todo".** Se descartan TODAS las liquidaciones del período, incluidas las pagadas, y al volver a cerrar se generan de cero. El cliente aceptó la contrapartida de volver a marcar los pagos. Mitigaciones aplicadas: baja lógica (recuperable) + snapshot completo en auditoría.

**Escaneo de reutilización.** `docs/patrones/catalogo.yml` → **PAT-005** ("Máquina de estados") aplica como método (transición validada en el Service, nunca en el Controller; auditoría por cambio de estado; acciones del ViewModel según estado y rol) y ya lista a KOI en `proyectos_que_lo_usan`; no aporta código copiable para este caso. Escaneo de `docs/*/definiciones/5-implementador.md`: los hits de "reabrir" en **ganaderia**, **marihogar** y **virtualwallet** son de otro tema (reabrir un formulario en Editar, y el contramovimiento que reabre una deuda al rechazar un cheque) — **ninguno es una reapertura de período contable con descarte de liquidaciones**. El precedente real es **del propio proyecto**: `InversionesService.ReabrirAsync` (D-30, reabrir una liquidación individual `Pagada → Pendiente` con motivo obligatorio), del que se copió el estilo: validar el motivo primero, guard de estado explícito, `LogWarning` con el motivo. **No se agregó un patrón nuevo al catálogo**: la operación es específica del modelo de período/liquidación de KOI.

**Hallazgo bloqueante: hacía falta una migración EF (el pedido pedía evitarla si se podía).** El pedido asumía que bastaba con la baja lógica. No alcanzaba: `Liquidaciones` tenía un índice **UNIQUE real en la base** sobre `(PeriodoMensualId, InversorId)` (`IX_Liquidaciones_PeriodoMensualId_InversorId`, creado en `E3_EstadoResultados`, confirmado en el `.cs` de la migración y en el `ModelSnapshot`) que **no contempla `DeletedAt`**. Las filas dadas de baja siguen ocupando la clave en MySQL, así que el nuevo cierre habría fallado con *duplicate key* al insertar la liquidación del mismo inversor. MySQL no soporta índices filtrados, y sumar `DeletedAt` a la clave no sirve (NULL cuenta como distinto y habilitaría duplicados **activos**). El índice pasa a **no único** y la unicidad de liquidaciones activas se sostiene en los servicios.

**Verificación obligatoria del pedido — no se duplican liquidaciones al volver a cerrar.** Verificado por lectura del código, no por ejecución:
- `CerrarPeriodoAsync` **no consulta liquidaciones existentes en ningún punto** (antes de este cambio): solo hace `_db.Liquidaciones.Add(...)` por inversor. No había ningún `IgnoreQueryFilters()` que revisar ahí.
- `grep -rn "IgnoreQueryFilters"` en todo el repo → **10 hits, ninguno sobre `Liquidaciones`** (son `Rubros`, `Subgrupos`, `ConceptosGasto`, `VentasMensuales`, `PeriodosMensuales`). O sea: **todo consumidor de liquidaciones pasa por el query filter global** (`DeletedAt == null`) y las descartadas quedan fuera de dividendos cobrados, recupero y reparto general — `InversionesService` (listado, marcar pagada, reparto general, mi inversión), `NotificacionCierreService` e `ImportacionInicialService`.
- El único `IgnoreQueryFilters()` nuevo que agrega esta etapa es sobre `Inversores` (para poder nombrar en la advertencia y en el snapshot a un inversor dado de baja después del cierre) — no sobre `Liquidaciones`.
- Se agregó igual un **guard explícito** en `CerrarPeriodoAsync`: si el período ya tiene liquidaciones **activas**, se rechaza el cierre. Reemplaza la garantía que daba el índice único y hace imposible el doble juego aunque alguien llame al servicio fuera del flujo de pantalla.

**Cambios por capa.**
- **Application** — `KoiDumplings.Application/Interfaces/IEstadoResultadosService.cs`: dos métodos nuevos (`ObtenerResumenReaperturaAsync`, `ReabrirPeriodoAsync`) y dos DTOs nuevos (`ResumenReaperturaDto`, `LiquidacionDescartadaDto`).
- **Infrastructure** — `Services/EstadoResultadosService.cs`: `ReabrirPeriodoAsync` (validaciones → snapshot → baja lógica → `Estado = Abierto` → `AuditLog` → commit, todo en una transacción con rollback y `LogError` si falla, y `LogWarning` estructurado al terminar), `ObtenerResumenReaperturaAsync` (solo lectura), el helper `ConstruirResumenReaperturaAsync` y el guard nuevo en `CerrarPeriodoAsync`. `Data/AppDbContext.cs`: el índice de `Liquidacion` pasa de `.IsUnique()` a no único, con el comentario explicando por qué y quién sostiene la regla ahora.
- **Web** — `Controllers/EstadoResultadosController.cs`: `Mensual` completa `vm.ResumenReapertura` cuando el período está cerrado; acción `ReabrirPeriodo` (POST, `[ValidateAntiForgeryToken]`, policy `SoloAdministrador`) que arma el `TempData["SuccessMessage"]` con el detalle de lo descartado. `Models/EstadoResultadosViewModels.cs`: `ErMensualViewModel.ResumenReapertura`. `Views/EstadoResultados/Mensual.cshtml`: botón "Reabrir período" (`btn-outline-warning`, ícono `fa-lock-open`, junto al badge de estado, solo Admin y solo si está cerrado), formulario oculto con antiforgery, bloque de aviso renderizado server-side y confirmación SweetAlert2.

**Detalles de implementación que no estaban en el pedido y conviene saber.**
1. **`FechaCierre`, `MontoAjuste` y `MotivoAjuste` se limpian al reabrir** (sus valores previos quedan en el snapshot). `FechaCierre` porque la propia entidad documenta "null mientras esté Abierto"; el ajuste manual porque formaba parte del cierre que se deshace — si quedara, el período mostraría un ajuste que ya no respalda ninguna liquidación (`CerrarPeriodoAsync` solo pisa `MontoAjuste` cuando el nuevo cierre trae uno, así que el valor viejo habría sobrevivido a un cierre sin ajuste).
2. **El aviso de SweetAlert2 se arma en Razor, no en JavaScript**: se renderiza un `<div id="avisoReapertura" class="d-none">` con el HTML ya formateado (números, nombres, importes con `.ov-monto`, tildes) y el diálogo lo levanta con `html: $('#avisoReapertura').html()`. Evita todo escapado de comillas/tildes en el string de JS. El `input: 'textarea'` de SweetAlert2 convive con `html:` sin problema (el textarea se renderiza debajo).
3. **El mensaje de `TempData["SuccessMessage"]` va en una sola línea, sin saltos.** `_Layout.cshtml` lo inyecta dentro de un string JS de comillas simples escapando solo `'` — un salto de línea rompería el script.
4. **`AuditLog.UserName` se resuelve desde `_db.Users`** por `userId`, para que la fila de Auditoría no aparezca como "Sistema" en una operación sensible (el servicio no tiene `IHttpContextAccessor`).
5. **El snapshot se serializa con `JavaScriptEncoder.UnsafeRelaxedJsonEscaping`** para que los nombres con tildes/ñ se lean tal cual en el modal de detalle de Auditoría.
6. **La pantalla de Auditoría ya soporta la acción nueva sin tocarla**: el `render` de la columna Acción cae en `bg-secondary` y muestra la etiqueta cruda "Reapertura" para acciones no mapeadas, y `OldValues`/`NewValues` ya se muestran como JSON formateado en el modal. `Action` tiene `HasMaxLength(20)` y "Reapertura" son 10 caracteres.
7. **Auditoría doble, a propósito:** además del `AuditLog` explícito con `Action = "Reapertura"` y el snapshot, el interceptor de `AppDbContext.SaveChangesAsync` genera sus propias filas `Update` por cada liquidación dada de baja y por el período. No hay recursión: el interceptor ignora las entidades `AuditLog`.

**Migración EF: una, generada y NO aplicada a ninguna base.**
- `KoiDumplings.Infrastructure/Data/Migrations/20260907203443_E17_LiquidacionesIndiceNoUnico_Reapertura.cs` — `DropIndex` + `CreateIndex` sin `unique` sobre `Liquidaciones (PeriodoMensualId, InversorId)`. El `Down` restaura el único.
- **Impacto:** la base deja de impedir dos liquidaciones activas para el mismo par período/inversor. La regla queda del lado de los servicios (`CerrarPeriodoAsync` con el guard nuevo, `ImportacionInicialService` con su `AnyAsync` previo, ya existente).
- **Es requisito para usar la funcionalidad:** sin aplicarla, reabrir funciona pero **volver a cerrar rompe con duplicate key**. No se ejecutó `dotnet ef database update` ni en local ni en producción.

**Build.** `dotnet build` desde la raíz del repo → **Compilación correcta, 0 errores.** 9 warnings, todos preexistentes y ya documentados en etapas anteriores (`CS0114 HomeController.StatusCode` + `NU1902` de MailKit/MimeKit, ver VUL-001) — ninguno introducido por esta etapa. El proyecto Web no usa `AddRazorRuntimeCompilation`, así que las vistas Razor se compilan en el build: el `Mensual.cshtml` modificado está cubierto por esta evidencia.

**Sin smoke test funcional** (regla del estudio). Evidencia de cierre: build limpio + la revisión de código propia documentada arriba (en particular la verificación de no-duplicación).

**Guía de prueba manual (para el dueño del estudio).**
1. **Aplicar primero la migración** `E17_LiquidacionesIndiceNoUnico_Reapertura` en la base contra la que se pruebe (`dotnet ef database update`). Sin esto el paso 6 falla con duplicate key.
2. Login como Administrador → Estado de Resultados → navegar a un período **cerrado** con liquidaciones (ideal: uno con al menos una **pagada**). Debe aparecer el botón "Reabrir período" al lado del badge "Cerrado". En un período **abierto** el botón no tiene que estar.
3. Click en "Reabrir período": el diálogo debe mostrar la cantidad real de liquidaciones a descartar, el bloque rojo con las pagadas (nombre, importe y fecha de pago) y el aviso de que el período deja de verse en "Rendimiento Histórico". Confirmar con el motivo vacío → debe rechazar con "El motivo es obligatorio." Cancelar → no debe pasar nada.
4. Reabrir con un motivo real → el mensaje de éxito debe nombrar cuántas liquidaciones se descartaron y cuáles estaban pagadas con su fecha; el badge debe pasar a "Abierto" y los formularios de ventas/gastos volver a ser editables.
5. Verificar el efecto de la baja lógica: **Liquidaciones** y **Reparto General** ya no muestran nada de ese período; **Mi Inversión** de un inversor de ese período muestra su dividendo cobrado y su recupero **sin** el mes reabierto; el mes desaparece de "Rendimiento Histórico" del Dashboard. En la base, `SELECT COUNT(*) FROM Liquidaciones WHERE PeriodoMensualId = X AND DeletedAt IS NOT NULL` debe dar el total descartado (las filas siguen ahí).
6. **La verificación central:** editar algo del período (ej. un gasto manual), cerrarlo de nuevo desde "Cerrar período" → tiene que generar **exactamente una** liquidación por inversor. Confirmar con `SELECT COUNT(*) FROM Liquidaciones WHERE PeriodoMensualId = X AND DeletedAt IS NULL` (debe dar la cantidad de inversores, no el doble) y revisar que Reparto General y Mi Inversión no muestren importes inflados.
7. Marcar de nuevo como pagadas las liquidaciones que lo estaban, usando el detalle del mensaje de éxito o el registro de Auditoría.
8. **Auditoría** (Sistema → Auditoría): debe haber una fila con acción "Reapertura" sobre `PeriodoMensual`, con el usuario correcto; el detalle (ojo) tiene que mostrar en "Valores anteriores" el JSON con cada inversor, sus puntos, bruto, consumos, neto, netoUsd, estado y fecha de pago, y en "Valores nuevos" el motivo escrito.
9. Verificar que un usuario **Inversor** no ve el botón y que un POST directo a `/EstadoResultados/ReabrirPeriodo` con ese rol es rechazado.
10. Ortografía y tildes de todo el texto visible nuevo, en tema claro y en tema oscuro.

**Riesgos y supuestos abiertos.**
- **La migración no está aplicada** y es requisito funcional. Es una operación de índice sobre una tabla chica (265 liquidaciones en producción), pero conviene backup previo igual.
- **La base ya no impide el duplicado**; lo impide el código. Si en el futuro se agrega otro camino de inserción de liquidaciones, tiene que repetir el guard.
- **Volver a cerrar dispara otra vez el email de notificación de cierre** (`NotificacionCierreService`, fire-and-forget desde `ConfirmarCierre`). Es lo esperado —los inversores tienen que ver los números corregidos— pero el cliente debe saber que recibirán un segundo aviso del mismo mes.
- **Los pagos se pierden como estado.** El detalle exacto (inversor, importe, fecha) queda en el snapshot de Auditoría y las filas son recuperables por baja lógica, pero re-marcarlos es trabajo manual, tal como el cliente aceptó.
- **Los `RegistrosEnvioNotificacion` del cierre anterior no se tocan**: quedan como historia de que ese aviso se mandó.
- Sin commit ni deploy (pedido explícito).

### Etapa 16 — Fases 3 y 5 fusionadas: catálogo real desde el Excel + importador nativo (2026-09-07)

**Alcance:** ítems 4 y 5 del Análisis §14 / Diseño §13.3 y §13.4 / Arquitectura §11.5 y §11.6, o sea Fases 3 y 5 del `plan-implementacion.md`, ejecutadas **fusionadas y con un enfoque distinto al documentado**. Fases 4 (editar meses cerrados) y 6 (API de Ayres) siguen fuera de alcance.

**El plan de remapeo de §11.5 quedó SUPERADO y no se ejecutó.** El mapeo "373 conceptos históricos → catálogo nuevo" asumía que el detalle real estaba en la base y solo había que reetiquetarlo. No es así: el catálogo cargado hoy es el genérico del seed inicial (21 subgrupos tipo "CMV", "Otros gastos") y en la migración de julio el detalle del Excel se aplastó contra él — hay 18-20 gastos por período en la base contra ~46 por mes en el Excel. Remapear habría conservado el aplastamiento. La decisión del dueño del estudio fue **reimportar el detalle real desde el Excel del cliente** y construir el catálogo como **unión de todas las variantes históricas** (no normalización): el catálogo del cliente cambió con los años y la historia tiene que quedar como él la registró.

**Escaneo de reutilización.** `docs/patrones/catalogo.yml` → match directo en **PAT-012** ("Importación de archivo con preview → confirmar (staging + reporte de excepciones)"), cuya propia nota dice que sigue vigente para todo import **recurrente** por archivo. Sus tres archivos de referencia de la-platense estaban marcados `pendiente_verificar: true`; **verificado en esta pasada**: efectivamente ya no existen en el working tree de `C:\Sistemas\Ferreteria La Platense` (borrados en los commits 71daf36 y 42cae2a, solo viven en el historial de git). Se actualizó el catálogo: flags bajados a `false` con la aclaración, KOI agregado a `proyectos_que_lo_usan` y los archivos de KOI sumados como **referencia viva** del patrón (era el único caso reutilizable que no tenía implementación consultable). Se copiaron del patrón las cinco decisiones: una sola función de proceso con flag `persistir`, staging con token validado como Guid, `IgnoreQueryFilters()` en todo matcheo, no pisar lo que el usuario administra a mano, y límite de request elevado. No se agregó un patrón nuevo: el parser del Excel es específico del formato de este cliente.

**1. Catálogo real derivado del Excel (Fase 3, ítem 4).** El catálogo **no se hardcodeó**: se deriva leyendo las tres hojas del archivo, así queda reproducible y sin errores de tipeo.
- Estructura reconocida (verificada contra el archivo real): hoja por año; fila 1 con el año en A y los meses en B..N cerrando en "TOTAL"; filas 2/3/4 = VENTAS, Ventas "A", Ventas "B"; después bloques de rubro donde **la negrita de la columna A distingue rubro de subgrupo**; cierre con "Total Gastos", "Resultado Ejercicio", "Rentabilidad" y un bloque "USD {año}" con la fila "Tipo de cambio" en las mismas columnas de mes.
- **Rubro sin subgrupos** (caso "Alquiler", y "Gastos Extras" en 2026): se sintetiza un subgrupo homónimo dentro del rubro, tal como decidió el Diseño §13.3 — el modelo exige que todo importe cuelgue de un subgrupo. Se aplica de forma uniforme, no como caso especial de "Alquiler".
- **Resultado derivado (validado contra el archivo real): 10 rubros y 79 subgrupos, 81 etiquetas distintas** — coincide exactamente con el conteo independiente del dueño del estudio. 47 subgrupos quedan vigentes (los del año 2026) y **32 quedan cargados pero de baja lógica** (variantes 2024/2025: "Jornales diarios", "Tubos de Co2 / Nitrógeno", "Comisiones Mercadopago", "Terminales de Pagos", "Cánon de publidad (2,5%)" con el typo del original, el rubro completo "Prov. imputables a gastos" renombrado a "Gastos Varios" en 2026, etc.).
- **Orden de presentación:** lo manda el año más reciente del archivo (es el que se usa para cargar el mes en curso); las variantes que solo existieron antes se agregan al final de su rubro.
- **TipoConcepto:** regla derivada, no lista fija — **un subgrupo es calculado si y solo si el propio Excel rotula un porcentaje en su etiqueta** (regex de `(N%)`). Da exactamente 5: Regalías (3%), Cánon de publicidad (2,5%), la variante con typo Cánon de publidad (2,5%), Fondo de juicios laborales (1%) y Reposición maquinaria (1%) — todos `PorcentajeVentasTotales`, confirmado contra las fórmulas del archivo (`=B2*0.03` sobre la fila VENTAS). Se les crea el `ParametroPorcentaje` con vigencia desde el año más antiguo del archivo. **Todo lo demás queda Manual, incluidos IIBB, comisiones de tarjeta, débitos/créditos y tasa municipal**, que en el catálogo genérico estaban como calculados pero en el Excel son importes cargados a mano.

**2. Baja lógica sin perder la historia — cambio de fondo en el E.R.** El query filter global (`DeletedAt == null`) hacía que dar de baja un subgrupo **borrara visualmente** el gasto histórico de los períodos que lo usaban: `EstadoResultadosService.ObtenerAsync` itera rubros→subgrupos, así que un subgrupo filtrado no renderiza su concepto aunque la fila siga en la base. Sin esto, dar de baja el catálogo genérico habría vaciado la pantalla de 2026-01..05 y de toda la historia migrada.
- `ObtenerAsync` pasa a leer rubros y subgrupos con `IgnoreQueryFilters()` y **muestra un subgrupo inactivo solo en los períodos donde efectivamente tiene un `ConceptoGasto` cargado**. `RubroErDto`/`ConceptoErDto` suman `EsInactivo`.
- `Views/EstadoResultados/Mensual.cshtml`: el concepto inactivo se muestra con badge "Histórico" (con `title` explicativo) y **sin botón de editar**.
- **Efecto colateral bueno:** antes, los conceptos de un subgrupo dado de baja quedaban fuera del `TotalGastos` de la pantalla Mensual pero seguían sumando en `ObtenerResumenAnualAsync` y en `DashboardService` (que suman conceptos sin pasar por el catálogo). Ahora las tres vistas coinciden.
- `DashboardService.ObtenerAsync`: `.IgnoreQueryFilters()` + `c.DeletedAt == null` explícito en la query de conceptos. Sin esto, `c.Subgrupo` venía **null** para los conceptos de un subgrupo dado de baja y el `GroupBy(c => c.Subgrupo.RubroId)` reventaba con NRE apenas se diera de baja el primer subgrupo con historia.
- `ConfiguracionController.Parametros`: el `Include(p => p.Subgrupo).ThenInclude(s => s.Rubro)` + proyección tenía el mismo problema (los 8 subgrupos calculados del seed genérico tienen `ParametroPorcentaje` y todos pasan a inactivos). Reescrito como **join explícito** contra `_db.Subgrupos`/`_db.Rubros`, que aplican su propio filtro y dejan el JOIN en INNER: los parámetros de un concepto discontinuado simplemente no se listan. `Subgrupos()` y `GetSubgruposCalculadosSelectList()` **no** necesitaron cambio: la sincronización garantiza que un rubro nunca queda inactivo con subgrupos activos (un subgrupo vigente implica su rubro vigente, verificado).

**3. Importador del Excel nativo (Fase 5, ítem 5 — opción B del plan).**
- **Application:** `DTOs/ImportacionExcelKoiDtos.cs` (`ImportacionExcelOpcionesDto`, `ImportacionExcelResultadoDto`, `PeriodoImportacionDto`, `CatalogoImportacionDto`, `EtiquetaSinMapeoDto`, enum `AccionPeriodo`) e `Interfaces/IImportacionExcelKoiService.cs` (`AnalizarAsync` / `ConfirmarAsync`).
- **Infrastructure:** carpeta nueva `Services/Importacion/` con dos piezas separadas a propósito:
  - `EstadoResultadosExcelParser.cs` — **puro, sin base de datos**: lee el libro con ClosedXML y deriva el catálogo (`ConstruirCatalogo`). Al no depender de EF se pudo validar de forma aislada contra los archivos reales.
  - `ImportacionExcelKoiService.cs` — sincronización de catálogo + import, todo dentro de una transacción.
- **Una sola función de proceso** (`ProcesarAsync(stream, opciones, persistir, userId)`): el preview y la confirmación recorren el mismo archivo con el mismo código, cambiando solo el flag. El preview no puede desalinearse de lo que pasa al confirmar.
- **Staging:** el archivo subido queda en `%TEMP%/koi-importacion-excel/{guid}.xlsx`; el token **se valida como Guid antes de construir la ruta** (path traversal) y el archivo se borra al confirmar OK; limpieza de los vencidos (más de 24 h) en cada análisis. Confirmar dos veces el mismo token no repite la carga: el archivo ya no está.
- **Modo actualizar** (`ActualizarExistentes`, apagado por defecto): apagado mantiene el comportamiento histórico (omitir); prendido actualiza. **Nunca toca el estado del período, la fecha de cierre ni el ajuste manual** — eso lo administra el cierre, no una importación.
- **Baja de conceptos en desuso** (`DarDeBajaEnDesuso`, prendido por defecto): controla **solo la baja lógica**. El alta de rubros/subgrupos faltantes se hace siempre, porque sin ellos no habría dónde imputar los importes. El label de la pantalla dice exactamente eso, para no prometer más de lo que hace.
- **Ventas:** el Excel solo distingue facturado (A) e informal (B), sin canal. Se imputa a Salón. **`CantidadComensales` y `CantidadVentas` nunca se pisan** (no vienen en el archivo), y si un período existente ya tiene desglose por canal (Pedidos/Mostrador) **las ventas no se actualizan** y se avisa en el preview — pisarlas perdería ese detalle. Los gastos de ese período sí se actualizan.
- **`ImporteCalculado` se corrige:** el importador viejo lo seteaba siempre igual a `ImporteManual`, incluso en subgrupos manuales. Como el Dashboard lee `ImporteCalculado ?? ImporteManual`, editar después el importe a mano dejaba al Dashboard mostrando el valor viejo. Ahora: subgrupo manual → `ImporteCalculado` y `PorcentajeAplicado` en null; subgrupo porcentual → ambos cargados.

**4. Preview obligatorio con las diferencias a la vista (nada silencioso).** El análisis no escribe nada y reporta, período por período: acción prevista (crear / actualizar / omitir), estado actual, ventas A/B, total de gastos, cantidad de conceptos (contra la que hay hoy) y tipo de cambio. Más cinco familias de **diferencias**, todas derivadas de chequeos genéricos, no de casos especiales:
- **Excel contra sí mismo — VENTAS distinto de A + B.** Aparece en **2026-07**: la fila VENTAS dice 58.226.922 pero A + B suma 61.226.922 (3.000.000 de diferencia; en 2024/2025 la fila A es `=VENTAS-B` y siempre cierra, en 2026 está hardcodeada). Se importa A + B y se avisa.
- **Suma de conceptos distinta de la fila "Total Gastos" del Excel.** Cae acá todo lo que la propia fórmula del cliente deja afuera de su total: 2024-12 (2.142.600 — el `=SUM(C40:C56)` de "Servicios" no alcanza la fila 57 "Comisiones PedidosYa"), 2025-02/04/10 (el rubro "Gastos Extras" está excluido del Total Gastos en varias columnas) y 2025-05 (1.335.352 — el importe de "Almacén" está escrito como **texto** `$1.335.352` y el `SUM` de Excel lo ignora; el parser sí lo lee).
- **Encabezado de rubro distinto de la suma de sus subgrupos** (plata no itemizada, no se importa porque no hay a qué subgrupo imputarla): 2025-02 "Gastos Extras" declara 2.581.000 con solo 1.500.000 abierto.
- **Concepto porcentual cuyo importe no coincide con el %.** Avisa que un "Recalcular porcentuales" posterior cambiaría el valor. Caso real: 2026-07 Regalías usa `=(VENTAS*0,79)*0,03` en vez de `=VENTAS*0,03`.
- **Excel contra la base:** ventas totales, total de gastos y cantidad de conceptos actuales vs. los que traería el archivo; aviso propio si el período está **cerrado** (al actualizarlo cambia el Resultado del Ejercicio ya usado para liquidar, y **las liquidaciones no se recalculan solas** — eso es Fase 4, no implementada).
- **Etiquetas sin mapear** en su propia tabla: si una fila no matchea contra el catálogo se reporta y **no se inventa el subgrupo**. Contra el archivo real la lista sale vacía.
- **Valores no numéricos**: "no da a pagar" en IVA (2024-11, 2025-10, 2025-11) se reporta y no se importa para ese mes. El guion y `#DIV/0!` se tratan como "sin movimiento", no como error.

**5. Web.** `Views/ImportacionInicial/Index.cshtml` reescrita: la pantalla pasa a llamarse **"Importación desde Excel"** (sidebar incluido). Card primaria = Excel del cliente (archivo + las dos opciones agrupadas en un panel "Opciones" + botón "Analizar archivo"); panel de preview con KPIs, cambios de catálogo agrupados por tipo, etiquetas sin mapear, tabla de detalle por período con las diferencias en una fila secundaria bajo cada período, y el botón "Confirmar importación" con confirmación SweetAlert2 que **nombra cuántos períodos se pisan**. El importador de plantilla del sistema sigue disponible, degradado a card colapsable secundaria (es el único camino para inversores, puntos y liquidaciones). Importes con `.ov-monto`. `ImportacionInicialController` suma `Analizar` / `ImportarKoi` y `[RequestSizeLimit]`/`[RequestFormLimits]` de 50 MB (el default de Kestrel de 30 MB es riesgoso para un libro con formato). Sigue todo bajo `RequireSuperUsuario`.

**Sin migración EF.** `Rubro`, `Subgrupo`, `ConceptoGasto`, `VentaMensual` y `PeriodoMensual` no se tocaron: los cambios son de DTOs, servicios, controllers y vistas. Verificado: `git status` no muestra ningún archivo bajo `KoiDumplings.Domain/` ni `Infrastructure/Data/Migrations/`.

**Validación ejecutada.** `dotnet build` → **Compilación correcta, 0 errores**; 1 warning de compilador (`CS0114 HomeController.StatusCode`) + 7 `NU1902` de MailKit/MimeKit, todos preexistentes — ninguno introducido. Además, como el parser es procesamiento de archivos y no la app, **se corrió contra los archivos reales** con un harness aislado que linkea `EstadoResultadosExcelParser.cs` y solo referencia ClosedXML: 0 errores de lectura, **16 períodos** detectados (2024-11/12, 2025-01..12, 2026-07/08 — exactamente los meses con datos reales), **81 etiquetas distintas**, 0 subgrupos duplicados dentro de un rubro, 0 rubros duplicados y 0 inconsistencias rubro-inactivo-con-subgrupo-activo. Se verificó que los meses futuros de 2026 (09..12), que traen fórmulas dando 0, **no** se detecten como períodos a importar — 2026-09 está abierto en la base y no se toca. **No se corrió smoke test de la aplicación** ni se ejecutó nada contra producción: el camino de escritura EF queda validado solo por revisión de código.

**Lo que este cambio NO hace (para que no se asuma).**
- No ejecuta la migración: eso lo corre el dueño del estudio, con backup previo y verificación de totales.
- No recalcula liquidaciones al actualizar un período cerrado (Fase 4).
- No importa 2026-01..05: el Excel arranca en julio 2026, esos períodos quedan intactos con el catálogo viejo (y ahora se siguen viendo, gracias al punto 2).
- No importa el "Reparto de Utilidades Inversores.xlsx" — sigue siendo la plantilla del sistema.

**Riesgos y supuestos abiertos.**
- **La detección rubro/subgrupo depende de la negrita de la columna A.** Es la única marca que el archivo tiene. Si el cliente pega valores sin formato en una versión futura, el parser corta con un error explícito ("no se reconoció ningún rubro") en vez de importar mal.
- **La unión genera subgrupos con el mismo nombre en rubros distintos** (Almacén, Aceite, Fletes… existen bajo "Gastos Varios" y bajo "Prov. imputables a gastos"). Es la consecuencia buscada de "unión, no normalización": la historia 2024/2025 queda bajo el rubro con el que se registró.
- **El "Gastos Extras" 2025 se importa aunque el Excel lo excluya de su Total Gastos** (unos 9.635.000 en el año). Es un gasto real del local; la decisión de importarlo o no queda del lado del usuario, con la diferencia exacta a la vista en el preview de cada período.
- **Los 4 conceptos porcentuales vigentes quedan como calculados** (decisión del dueño del estudio). Un "Recalcular porcentuales" sobre un período importado los pisaría con el porcentaje sobre ventas totales; el preview avisa dónde eso cambiaría el valor.
- El matcheo normaliza mayúsculas, espacios **y tildes**. Dos etiquetas que solo difieran en acentuación se fusionarían — no ocurre en el archivo actual, y reduce el riesgo de duplicados por drift de encoding contra MySQL.

**Pruebas mínimas para QA.**
1. Importación desde Excel → subir `Estado de Resultados KOI (Inversores).xlsx` con las dos opciones por defecto → "Analizar": deben salir 2026-07 a crear, el resto omitidos, 0 etiquetas sin mapear y el detalle de catálogo con 10 rubros / 79 subgrupos.
2. Confirmar y verificar en Configuración → Subgrupos que quedan 47 activos, y que Rubros ya no lista "Prov. imputables a gastos".
3. Estado de Resultados de 2026-07 → cada concepto del Excel aparece como línea propia (46), no 18-20.
4. Estado de Resultados de **2026-03** (período viejo, catálogo genérico) → los conceptos siguen visibles con badge "Histórico" y **sin** botón de editar; el Total Gastos no cambió respecto de antes de la importación.
5. Dashboard de un período histórico → carga sin error y el gráfico "Gastos por rubro" muestra los rubros viejos.
6. Configuración → Parámetros → la pantalla carga (no debe romper con los parámetros de los subgrupos dados de baja).
7. Repetir el análisis con "Actualizar los períodos que ya existan" prendido → 2026-08 debe aparecer como "Se actualiza" con la diferencia de ventas de $100 visible, y con el aviso de período cerrado.
8. Confirmar dos veces seguidas el mismo token → la segunda debe responder que el archivo ya no está disponible, sin duplicar nada.
9. Ortografía y tildes en toda la pantalla nueva.

**Checklist de salida para merge.**
- [x] Build 0 errores, sin warnings nuevos.
- [x] Sin migración EF (verificado por `git status`).
- [x] Parser validado contra los archivos reales del cliente.
- [x] Lógica de negocio en Services, no en el Controller.
- [x] Serilog con placeholders, sin `Console.WriteLine`.
- [x] SweetAlert2 en la acción destructiva, `.ov-monto` en importes, ortografía y tildes revisadas.
- [x] `PAT-012` verificado y actualizado en `docs/patrones/catalogo.yml`.
- [ ] **Prueba manual del dueño del estudio contra la base local** (guía arriba) — pendiente.
- [ ] **Commit y deploy** — deliberadamente sin hacer (hay trabajo en paralelo sobre el mismo repo).
- [ ] **Migración de los datos reales en producción** — la ejecuta el dueño del estudio, con backup previo y verificación de totales.

### Etapa 15 — Fases 1 y 2 del plan de implementación (2026-09-07)

**Alcance:** ítems 1, 2 y 6 del Análisis §14 / Diseño §13.1 y §13.5 / Arquitectura §11.2, §11.3 y §11.7 — o sea Fase 1 (correcciones rápidas) y Fase 2 (Mi Inversión: recupero acumulado + gráfico) del `plan-implementacion.md`. **Fases 3, 4, 5 y 6 explícitamente fuera de alcance** (catálogo de rubros, edición de meses cerrados, importación de Excel, API de Ayres) — se trabajan aparte, en paralelo, sobre el mismo repo.

**Escaneo de reutilización:** sin match cross-proyecto y sin necesidad de buscarlo — no hay entidad ni flujo nuevo. Los tres ítems son modificaciones puntuales sobre código propio de KOI ya existente. Sí hubo **reutilización interna**: el fix de orden del ítem 6 es copia literal del patrón ya aplicado en `Views/EstadoResultados/Anual.cshtml` (Etapa 14, fix 2), y el gráfico del ítem 2 sigue el patrón de Chart.js + manejo de tema (`isDark`/`textColor`/`gridColor`) ya establecido en `Views/Dashboard/Index.cshtml`. No se agregó ningún patrón nuevo a `docs/patrones/catalogo.yml` — nada de esto es un componente genérico reutilizable fuera de KOI.

**1. Remitente de correos (Fase 1.1, ítem 1 — sin código).** `KoiDumplings.Web/appsettings.Production.json` → `Olvidata_Email.Smtp.FromName`: `"Koi Dumplings - Olvidata"` → `"KOI Dumplings"`. El archivo está en `.gitignore` (tiene credenciales SMTP reales) → **no se commitea**, viaja con el deploy. `appsettings.json` (base, `"Olvidata Soft"`) no se tocó: es el default del blankproject y en producción lo pisa el de Production.

**2. Reparto General — orden por año y mes (Fase 1.2, ítem 6).** `KoiDumplings.Web/Views/RepartoGeneral/Index.cshtml`, tabla `#tablaReparto`: la columna Período ordenaba por el texto ("Agosto 2026") → alfabético por nombre de mes. Se agregó `data-order="@($"{f.Anio}{f.Mes:D2}")"` al `<td>` del período (`RepartoFilaDto` ya exponía `Anio` y `Mes`, sin cambios en Application) y `columnDefs: [{ type: 'num', targets: 0 }]` al init de DataTables. El `order: [[0, 'desc']]` ya estaba correcto — se verificó, no se tocó. El texto visible del período no cambia. Idéntico al fix de Etapa 14 sobre `EstadoResultados/Anual.cshtml`.

**3. Mi Inversión — recupero acumulado + gráfico de evolución (Fase 2, ítem 2).**
- **Application** — `KoiDumplings.Application/DTOs/InversionesDtos.cs`: `MiInversionFilaDto` suma `public decimal? RecuperoAcumuladoPorc { get; set; }`. `RentaMensual` no cambia (sigue siendo el recupero *del mes*).
- **Infrastructure** — `KoiDumplings.Infrastructure/Services/InversionesService.cs`, `ObtenerMiInversionAsync`: el historial dejó de armarse con un `Select` sobre la lista descendente y pasó a un `foreach` sobre la misma lista **ordenada ascendente** (`OrderBy(Anio).ThenBy(Mes)`) llevando un running total, con un `filas.Reverse()` final para devolver el orden descendente de siempre (la vista renderiza tal cual, la tabla tiene `ordering: false`). La query a la base no cambió.
  - **Criterio de acumulación elegido** (decisión de negocio del Análisis §14.1): solo suman las liquidaciones con `Estado == Pagada` **y** `NetoUsd` con valor. Una liquidación **Pendiente se muestra en la tabla arrastrando el acumulado vigente hasta ese momento**, no en blanco ni con "—". Razón: en una serie que solo puede crecer, un hueco en el medio se lee como error de dato; arrastrar el valor comunica correctamente "este mes no movió la aguja" y además deja la línea del gráfico continua. Queda como supuesto a validar con el cliente (hoy es indistinto en la práctica: 264 de 265 liquidaciones están Pagada).
  - **Se acumula el `NetoUsd` crudo y se redondea recién al calcular el porcentaje** (`Math.Round(acumuladoNetoUsd / capital * 100, 2)`), no se suman porcentajes ya redondeados. Es lo que garantiza que el acumulado de la fila más reciente coincida **exactamente** con el KPI `RecuperoPorc` de las cards de arriba, que usa el mismo numerador (`dividendosUsd` = suma de `NetoUsd` de las pagadas) y el mismo redondeo final. Sumar los `RentaMensual` ya redondeados habría arrastrado hasta ~2 centésimas de error contra el KPI.
- **Web** — `KoiDumplings.Web/Views/MiInversion/Index.cshtml`:
  - Columna nueva **"Recupero acum."** en `#tablaHistorial`, inmediatamente después de "Renta", con `FormatoMoneda.FormatPorcentaje` y clase `.ov-monto` (consistente con la columna Renta, que ya la usaba).
  - **No se agregó una columna "Recupero del mes"**: "Renta" ya ES ese número. Para que la relación quede explícita sin duplicar el dato, el `<th>` de Renta lleva ahora `title="Recupero del mes: neto en dólares de esta liquidación sobre el capital aportado"` (tooltip nativo — el proyecto no inicializa tooltips de Bootstrap en ninguna vista, se usa `title` como en el resto del sistema). El `<th>` de la columna nueva lleva su propio `title` equivalente.
  - **Gráfico de evolución** (`<canvas id="chartRecupero">`) en una card propia **entre las cards de KPI y la tabla de historial**: línea del recupero acumulado (azul `#2b9de4`, con `fill` suave) + línea punteada de meta al 100 % (verde `#22c55e`, `pointRadius: 0`), eje X en orden **cronológico ascendente** (al revés que la tabla), `beginAtZero` + `suggestedMax: 100` para que la meta siempre entre en cuadro, tooltips y ticks formateados en es-AR con 1 decimal y " %".
  - **Chart.js no se agregó**: ya viene global del `_Layout.cshtml` (v4.4.0, en el `<head>`). El Dashboard además carga la 4.4.3 en su propia sección de scripts — no se tocó, pero conviene saber que hay dos versiones cargadas en esa pantalla.
  - Colores según tema con el mismo patrón que Dashboard (`document.documentElement.getAttribute('data-theme') === 'dark'` → `textColor`/`gridColor`). Recordar que desde la Etapa 9 el toggle de tema hace `location.reload()`, así que el canvas siempre se crea con los colores correctos.
  - **Sin endpoint AJAX nuevo**: labels y datos salen del mismo `Model` que ya viajaba a la vista, serializados con `System.Text.Json.JsonSerializer` + `@Html.Raw` dentro de `@section Scripts`.
  - **Estado vacío**: tanto el `<canvas>` como el bloque de script están envueltos en un guard de historial no vacío (`d.Historial.Any()` / `Model.Datos != null && Model.Datos.Historial.Any()`) — sin historial no se renderiza ningún gráfico y queda el alert "Aún no hay liquidaciones generadas" de siempre.

**Archivos modificados:**
- `KoiDumplings.Web/appsettings.Production.json` (`FromName`) — **gitignored, no se commitea, se publica con el deploy.**
- `KoiDumplings.Web/Views/RepartoGeneral/Index.cshtml` (`data-order` + `columnDefs` numérico).
- `KoiDumplings.Application/DTOs/InversionesDtos.cs` (`MiInversionFilaDto.RecuperoAcumuladoPorc`).
- `KoiDumplings.Infrastructure/Services/InversionesService.cs` (`ObtenerMiInversionAsync`: running total ascendente).
- `KoiDumplings.Web/Views/MiInversion/Index.cshtml` (columna nueva + tooltips de encabezado + card del gráfico + script de Chart.js).

**Migración EF:** ninguna, confirmado. Ningún ítem agrega ni modifica entidades ni columnas — `RecuperoAcumuladoPorc` es un campo **calculado en memoria** dentro de un DTO de Application, no una propiedad de dominio persistida. Coincide con lo declarado en Arquitectura §11.1.

**Build:** `dotnet build KoiDumplings.slnx` (ojo: el repo usa `.slnx`, no `.sln`) → **Compilación correcta, 0 errores.** 9 warnings preexistentes sin cambios (NU1902 MailKit/MimeKit — VUL-001 pendiente — y CS0114 `HomeController.StatusCode`), ninguno introducido por esta etapa. El proyecto Web no usa Razor Runtime Compilation, así que las vistas `.cshtml` se compilan en el build: el build limpio también valida la sintaxis Razor de las dos vistas tocadas.

**Sin smoke test funcional** (regla del estudio) — evidencia de cierre: build limpio + revisión de código propia.

**Guía de pasos para prueba manual del dueño del estudio:**
1. **Remitente**: después del deploy (con el `appsettings.Production.json` actualizado subido), disparar cualquier mail del sistema (ej. una notificación de cierre) → el remitente debe llegar como "KOI Dumplings", sin "- Olvidata".
2. **Reparto General**: entrar a `/RepartoGeneral` con períodos de más de un año → agosto 2026 arriba de julio 2026, y todo 2026 arriba de todo 2025. Hacer click en el encabezado "Período" para invertir el orden → debe pasar a ascendente cronológico (enero antes que febrero), nunca alfabético (abril antes que agosto).
3. **Mi Inversión — acumulado**: entrar como Inversor (o como Admin eligiendo un inversor en el combo) → la columna "Recupero acum." debe crecer monótonamente de abajo hacia arriba (la tabla va del mes más nuevo al más viejo), y el valor de la **primera fila** debe ser idéntico al KPI "Recupero" de la card de arriba.
4. **Mi Inversión — gráfico**: entre las cards y la tabla debe aparecer "Evolución del recupero" con una línea que sube de izquierda a derecha (mes más viejo a la izquierda) y una línea verde punteada horizontal en 100 %. Pasar el mouse por un punto → tooltip con el período y el porcentaje. Verificar en **tema claro y oscuro** (recargando después del toggle) que los ejes y la leyenda se lean bien.
5. **Mi Inversión — inversor sin liquidaciones**: elegir (como Admin) un inversor sin historial → no debe aparecer la card del gráfico, solo el alert "Aún no hay liquidaciones generadas".
6. **Fila Pendiente**: si hay alguna liquidación en estado Pendiente, verificar que su fila muestre el mismo acumulado que la fila inmediatamente anterior (más vieja) — no suma hasta que se marque Pagada. Confirmar que ese criterio es el que quiere el cliente.

**Pruebas mínimas requeridas para QA:** los 6 pasos de arriba, más regresión del listado de Reparto General (paginación y buscador siguen funcionando después del `columnDefs`) y de la tabla de Mi Inversión con un inversor de muchos períodos (la columna nueva no debe romper el `responsive` de DataTables).

### Etapa 14 — Fixes post-QA (4 ítems, sesión actual, 2026-08-13)

**Contexto:** 4 bugs puntuales detectados en QA manual del dueño del estudio sobre lo construido en Etapa 13. No pasaron por Análisis/Diseño/Arquitectura/Presupuesto — bugs ya relevados, causa raíz identificada de antemano por el pedido. Sin migración EF en ninguno. Sin escaneo de reutilización cross-proyecto (no son entidad/flujo nuevo, son correcciones puntuales sobre código propio ya existente).

1. **Dashboard Histórico no debía permitir ver meses abiertos ni futuros** — `DashboardService.ObtenerPeriodosAsync()` (`KoiDumplings.Infrastructure/Services/DashboardService.cs`) ahora filtra `.Where(p => p.Estado == EstadoPeriodo.Cerrado)` antes de materializar la query (confirmado por grep: único caller es `DashboardController.Index`, sin riesgo de romper otra pantalla). `DashboardController.Index` (`KoiDumplings.Web/Controllers/DashboardController.cs`) ajustó el fallback de período por defecto: con la lista ya filtrada a solo cerrados, toma `periodos.FirstOrDefault()` (el cierre más reciente, la lista ya viene ordenada desc) en vez de comparar contra `DateTime.Today`; `hoy.Year`/`hoy.Month` quedó solo como último fallback si no hay ningún período cerrado (ambiente vacío).
2. **EstadoResultados/Anual ordenaba alfabéticamente en vez de cronológicamente** — `Views/EstadoResultados/Anual.cshtml`: se agregó `data-order="@($"{m.Anio}{m.Mes:D2}")"` al `<td>` de la columna Período (ej. "202608" para agosto 2026), y se cambió `order: [[0, 'asc']]` a `order: [[0, 'desc']]` (más reciente primero, pedido explícito) más `columnDefs: [{ type: 'num', targets: 0 }]` explícito para que DataTables trate la columna como numérica (verificado con prueba aislada en Node que confirma que, al tener todos los valores el mismo largo fijo de 6 dígitos, la comparación como string ya coincidía con la numérica — se dejó `type: 'num'` de todas formas para no depender de esa coincidencia).
3. **Rename "Dashboard Histórico" → "Rendimiento Histórico"** — `Views/Shared/_Layout.cshtml` (única ocurrencia del texto, confirmado por grep, sección "Mi Cuenta" del bloque Inversor). `Views/Dashboard/Index.cshtml`: `ViewData["Title"]` pasó de fijo `"Dashboard"` a condicional `User.IsInRole("Inversor") ? "Rendimiento Histórico" : "Dashboard"` — Admin/SuperUsuario sin cambios. El `<h3>` visible de la página (línea ~14, texto "Dashboard" fijo) no se tocó — el pedido fue específico al título (afecta el `<title>` del navegador vía `_Layout.cshtml` línea 7), no un refactor cosmético del encabezado visible.
4. **Notificaciones — texto invisible en `<option>` de `#selectRol`** — causa raíz: `[data-theme="dark"] .form-select { color: var(--ov-text) }` (casi blanco) se hereda en el popup nativo de `<option>` que el navegador renderiza casi siempre con fondo claro real, sin heredar `background-color` del `<select>` de forma confiable. Fix en `KoiDumplings.Web/wwwroot/css/olvidata-theme.css`, sección "Form controls" (fuera de cualquier bloque `[data-theme]`, para que aplique siempre): regla nueva `.form-select option { color: var(--ov-gray-800); background-color: #ffffff; }`. Es global a todos los `<select class="form-select">` del sistema — cubre `Notifications/Crear.cshtml` y cualquier otro select existente o futuro con el mismo riesgo, sin trabajo adicional.

**Archivos modificados:**
- `KoiDumplings.Infrastructure/Services/DashboardService.cs` (filtro `EstadoPeriodo.Cerrado`).
- `KoiDumplings.Web/Controllers/DashboardController.cs` (fallback de período por defecto).
- `KoiDumplings.Web/Views/EstadoResultados/Anual.cshtml` (`data-order` + `order desc` + `columnDefs` numérico).
- `KoiDumplings.Web/Views/Shared/_Layout.cshtml` (rename link sidebar).
- `KoiDumplings.Web/Views/Dashboard/Index.cshtml` (`ViewData["Title"]` condicional por rol).
- `KoiDumplings.Web/wwwroot/css/olvidata-theme.css` (`.form-select option` color/background explícitos).

**Migración EF:** ninguna.

**Build:** `dotnet build` desde la raíz del repo → **Compilación correcta, 0 errores.** 9 warnings preexistentes sin cambios (NU1902 MailKit/MimeKit — VUL-001 pendiente — y CS0114 HomeController.StatusCode), ninguno introducido por esta etapa.

**Sin smoke test funcional** (regla del estudio) — evidencia de cierre: build limpio + revisión de código propia. Excepción puntual: fix 2 se verificó de forma aislada (fuera de la app) con un script Node que compara el orden de los valores `data-order` como string vs. como número sobre datos sintéticos con el mismo formato ("202601".."202608") — confirma que el orden coincide en ambos casos, dado el largo fijo de 6 dígitos; no reemplaza la prueba manual en la app real.

**Guía de pasos para prueba manual del dueño del estudio:**
1. **Dashboard Histórico**: como Inversor o Admin, entrar a "Rendimiento Histórico"/"Dashboard" → el combo de año/mes debe listar únicamente meses ya cerrados (no debe aparecer el mes en curso si todavía está abierto) → por defecto debe abrir en el cierre más reciente, no en el mes calendario actual.
2. **Historial de Resultados (Anual)**: entrar a `/EstadoResultados/Anual` de un año con varios meses cargados → la tabla debe mostrar los meses en orden cronológico descendente (ej. Agosto, Julio, Junio... no Abril, Agosto, Diciembre alfabético).
3. **Rename**: como Inversor, el link del sidebar en "Mi Cuenta" debe decir "Rendimiento Histórico" (no "Dashboard Histórico") y el título de la pestaña del navegador debe decir lo mismo. Como Admin, debe seguir diciendo "Dashboard" en sidebar y pestaña.
4. **Notificaciones**: como Admin, ir a "Nueva Notificación" → hacer click en el combo de Rol para abrir el popup nativo de opciones → el texto de cada opción debe verse en negro/oscuro y legible, tanto en tema claro como en tema oscuro.

### Etapa 13 — Sprint UX/UI Inversor + fixes (2026-08-12)

**Escaneo de reutilización (obligatorio antes de implementar):** re-confirmado el escaneo ya hecho en Diseño §11.0 — sin match cross-proyecto. Los 9 ítems son 100% reutilización de servicios/entidades propios de KOI (Dashboard, `IIndicadoresService`, `InversionesService`, sistema de notificaciones in-app ya existente). No se copió código de ningún otro proyecto del estudio.

**Alcance implementado (9 ítems, ver `1-analista-funcional.md` §12 para criterios de aceptación completos):**

1. **"Mes actual" (nueva, solo Inversor)** — `MesActualController` (`[Authorize]` simple) + `Views/MesActual/Index.cshtml`. Sin selector de período: siempre mes/año actual calculado en huso horario Argentina (`TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, "America/Buenos_Aires")`, mismo patrón que `CotizacionService.HoyArgentina()`/`FichadorController`, para no depender del huso del hosting site4now.net EE.UU.). Título dinámico "Rendimiento {Mes} {Año}". KPIs: Ventas Totales, Ticket Promedio, Cant. de Tickets, torta % por canal (Salón/Pedidos/Mostrador — se mantuvo el término "Pedidos" porque es el nombre real del campo en `IndicadoresDto`/`VentaMensual` y el que ya usa el Dashboard actual). Reutiliza `IIndicadoresService.ObtenerAsync(anio, mes)` tal cual — cero lógica de cálculo duplicada.
2. **"Dashboard Histórico" (relabel, solo Inversor)** — mismo `DashboardController`/`Views/Dashboard/Index.cshtml`/URL de siempre, sin tocar contenido. Solo el sidebar cambia el texto del link para Inversor.
3. **Rol "Encargado"** — `SeedData.RolEncargado` sembrado. Ve únicamente "Fichador" en el sidebar (bloque excluyente, no evalúa el resto de secciones). `FichadorController` usa una policy nueva `SoloAdministracionOFichador` (no se tocó `SoloAdministrador`, usada por otros 6 controllers).
4. **Fix del bug de puntos ("Wang")** — `InversionesService.AsignacionesVigentesQuery` → `AsignacionesVigentesAsync`, dedupe por inversor igual que `EstadoResultadosService`. Sin migración, sin tocar datos de producción. Verificación aislada de la lógica (detalle abajo): 95/15 tras el fix vs 102/16 antes.
5. **Reparto General simplificado** — tabla sin columna por inversor; `RepartoGeneralViewModel.NombresInversores` eliminado (sin uso). Desglose individual intacto en `RepartoFilaDto.Inversores` (Application), solo se dejó de renderizar en esta vista.
6. **Rename "Vista Anual ER" → "Historial de Resultados"** — título de página + `<h3>` en `Anual.cshtml`, y el link del sidebar en sus 2 apariciones (Admin/SuperUsuario e Inversor). Aplica a todos los roles, no solo Inversor.
7. **Notificaciones — composición nueva** — `INotificacionAdminService`/`NotificacionAdminService` nuevo (orquesta `INotificationService`+`IEmailService`, ninguno de los dos se modificó). `NotificationsController` extendido con `Crear`/`UsuariosPorRol`/`Enviar` (`SoloAdministrador`). Vista `Crear.cshtml`: combo de rol → AJAX → chips removibles → 2 checkboxes (correo/in-app, ≥1 obligatorio) → confirmación SweetAlert2 → resumen post-envío con detalle de fallos de email (no aborta el resto, mismo criterio que `NotificacionCierreService`). Link "Notificaciones" persistente para todos los roles autenticados (bandeja personal) + "Nueva Notificación" solo Admin/SuperUsuario.
8/9. **Mi Inversión — tabla de historial** — sin columnas Puntos/TC; Período dividido en Año/Mes (usa `MiInversionFilaDto.Anio`/`.Mes` ya existentes). Mes en palabras capitalizado vía helper nuevo `FormatoFecha.NombreMes(int)`. `ordering: false` en el DataTable (se saca el click-to-sort completo); el orden Año desc/Mes desc ya lo entregaba el servicio sin cambios.
10. **Fix global `.ov-monto`** — clase `white-space: nowrap` en `olvidata-theme.css`, aplicada en Dashboard/Liquidaciones/RepartoGeneral/MiInversión/MesActual/EstadoResultados (Mensual+Anual+PreviewCierre, solo celdas con patrón símbolo+espacio+número). Puntos/Index.cshtml revisada y descartada (no tiene celdas de importe monetario).

**Archivos nuevos:**
- `KoiDumplings.Web/Controllers/MesActualController.cs`, `KoiDumplings.Web/Models/MesActualViewModels.cs`, `KoiDumplings.Web/Views/MesActual/Index.cshtml`.
- `KoiDumplings.Web/Helpers/FormatoFecha.cs` (nombre de mes capitalizado, reutilizado por `MesActualController` y `MiInversion/Index.cshtml`).
- `KoiDumplings.Application/Interfaces/INotificacionAdminService.cs`, `KoiDumplings.Infrastructure/Services/NotificacionAdminService.cs`, `KoiDumplings.Web/Models/NotificationsViewModels.cs`, `KoiDumplings.Web/Views/Notifications/Crear.cshtml`.

**Archivos modificados:**
- `KoiDumplings.Infrastructure/Services/InversionesService.cs` (fix Wang — `AsignacionesVigentesAsync` + caller).
- `KoiDumplings.Infrastructure/Data/SeedData.cs` (`RolEncargado`).
- `KoiDumplings.Web/Program.cs` (policy `SoloAdministracionOFichador`).
- `KoiDumplings.Web/Controllers/FichadorController.cs` (nueva policy).
- `KoiDumplings.Web/Controllers/RepartoGeneralController.cs`, `KoiDumplings.Web/Models/InversionesViewModels.cs` (sin `NombresInversores`).
- `KoiDumplings.Web/Views/RepartoGeneral/Index.cshtml`, `KoiDumplings.Web/Views/EstadoResultados/Anual.cshtml`, `KoiDumplings.Web/Views/MiInversion/Index.cshtml`, `KoiDumplings.Web/Views/Shared/_Layout.cshtml` (sidebar reestructurado: bloque Encargado excluyente, Dashboard/Mes actual condicional, Notificaciones persistente, rename Historial de Resultados x2).
- `KoiDumplings.Web/Controllers/NotificationsController.cs` (3 acciones nuevas), `KoiDumplings.Web/Views/Notifications/Index.cshtml` (botón "Nueva notificación" para Admin/SuperUsuario).
- `KoiDumplings.Infrastructure/DependencyInjection.cs` (registro `INotificacionAdminService`).
- `KoiDumplings.Application/DTOs/NotificationDtos.cs` (`UsuarioRolDto`/`EnviarNotificacionDto`/`ResultadoEnvioNotificacionDto`).
- `KoiDumplings.Web/wwwroot/css/olvidata-theme.css` (`.ov-monto`).
- `KoiDumplings.Web/Views/Dashboard/Index.cshtml`, `Views/Liquidaciones/Index.cshtml`, `Views/EstadoResultados/Mensual.cshtml`, `Views/EstadoResultados/Anual.cshtml` (celda adicional), `Views/EstadoResultados/PreviewCierre.cshtml` — clase `.ov-monto` aplicada a celdas de importe.

**Verificación del fix de puntos (Wang) — evidencia sin smoke test de la app:** se armó un proyecto console aislado (fuera del repo, en el scratchpad de la sesión) que reproduce EXACTAMENTE la misma lógica LINQ del fix (`GroupBy(InversorId)` + `OrderByDescending(VigenteDesdeAnio).ThenByDescending(VigenteDesdesMes).First()`) contra datos sintéticos calcados del escenario real documentado en `trazabilidad.md` (14 inversores de una sola vigencia + Wang con 2 vigencias: 7 pts desde 2024-01, 8 pts desde 2025-04). Resultado ejecutado:
```
=== ANTES del fix (bug) ===
Filas devueltas: 16
TotalAsignado: 102
Apariciones de 'Wang': 2

=== DESPUÉS del fix ===
Inversores devueltos: 15
TotalAsignado: 95
Wang aparece 1 sola vez, con 8 puntos vigentes (vigencia 2025/4)

RESULTADO: OK
```
Coincide exactamente con lo validado manualmente contra producción por el orquestador antes de presupuestar (`trazabilidad.md`, entrada 2026-08-12 orquestador). **No se tocó ninguna fila de `asignacionpuntos` en producción** — es un fix de query, no de datos.

**Migración EF:** ninguna — confirmado en las 9 ítems, coincide con Arquitectura §9.1.

**Build:** `dotnet build` desde la raíz del repo → **Compilación correcta, 0 errores.** 9 warnings preexistentes sin cambios (NU1902 MailKit/MimeKit — VUL-001 pendiente — y CS0114 HomeController.StatusCode), ninguno introducido por esta etapa.

**Sin smoke test funcional** (regla del estudio) — evidencia de cierre: build limpio + revisión de código propia + verificación aislada de la lógica del fix Wang (detallada arriba, no es una prueba contra la app real ni contra producción).

**Decisiones técnicas tomadas en implementación (no explícitas en las 4 definiciones):**
1. Policy `SoloAdministracionOFichador` nueva para `FichadorController` en vez de agregar `Encargado` directo a `SoloAdministrador` (que la arquitectura citaba como opción) — se verificó por grep que otros 6 controllers (`Camaras`, `Inversores`, `EstadoResultados`, `Users`, `TipoCambio`, `Configuracion`) usan `SoloAdministrador`; modificarla habría abierto esas pantallas al rol nuevo, violando el criterio de aceptación del ítem 3.
2. Link "Notificaciones" (bandeja) visible a TODOS los roles autenticados (no solo Admin) — el diseño dejaba la decisión abierta ("decidí vos"); se optó por visibilidad universal porque la funcionalidad de bandeja personal ya existía y estaba abierta a cualquier autenticado (`NotificationsController` con `[Authorize]` simple desde antes de este sprint), solo faltaba el link. El Encargado no lo ve por el bloque excluyente del ítem 3.
3. Sidebar: el link "Dashboard"/"Mes actual" en la sección superior ("KOI") ahora tiene 3 ramas (Admin/SuperUsuario → Dashboard, Inversor → Mes actual, cualquier otro rol autenticado → Dashboard sin cambios) para no dejar sin link a Vendedor/Empleado, roles sembrados pero sin pantallas asignadas hoy — decisión conservadora, sin regresión, fuera del alcance explícito del sprint.
4. Helper `FormatoFecha.NombreMes(int)` nuevo en vez de reutilizar el `NombreMes(anio, mes)` privado de `InversionesService`/`DashboardService` — porque esos devuelven "Mes Año" (para el nombre del período) y la vista necesitaba solo la palabra del mes, sin año; se creó un helper de capa Web en `Helpers/` (mismo patrón que `FormatoMoneda`) en vez de exponer un método nuevo en Infrastructure, ya que es puramente de presentación.
5. Item 10: se aplicó `.ov-monto` con criterio — únicamente en celdas con el patrón literal del bug (símbolo `$`/`U$D`/prefijo "USD "/"TC:" + espacio + número). Las celdas de `EstadoResultados` que muestran solo un número `N2` sin símbolo (mayoría de `Mensual.cshtml`) se dejaron sin tocar por no reproducir el bug reportado (el diseño explícitamente no obligaba a tocar TODAS las celdas, solo las de importe con signo). `Puntos/Index.cshtml` no tiene celdas de importe monetario — se descartó tras revisión, no se tocó.

**Guía de pasos para prueba manual del dueño del estudio** (uno por ítem, calcado de los criterios de aceptación de `1-analista-funcional.md` §12.3):
1. **Mes actual**: login como Inversor → el sidebar debe decir "Mes actual" (no "Dashboard") → la pantalla debe mostrar "Rendimiento {mes actual} {año actual}" sin ningún selector, con Ventas Totales/Ticket Promedio/Cant. de Tickets y la torta Salón/Pedidos/Mostrador. Login como Administrador → debe seguir viendo "Dashboard" sin ningún cambio.
2. **Dashboard Histórico**: como Inversor, entrar a "Dashboard Histórico" (sección "Mi Cuenta") → debe verse exactamente igual al Dashboard actual, con su selector de mes/año y sus 3 secciones. Como Admin, el link debe seguir diciendo "Dashboard".
3. **Rol Encargado**: crear un usuario con rol único "Encargado" (vía `/Users` o directamente en Identity) → loguearlo → el sidebar debe mostrar ÚNICAMENTE "Fichador" → entrar a `/Fichador` debe funcionar → probar navegar manualmente a `/Dashboard`, `/MiInversion`, `/Inversores`, etc. → todas deben denegar el acceso (redirect a Access Denied, no contenido).
4. **Fix de puntos**: entrar a `/Puntos` con el período actual (o cualquiera desde abril 2025) → el total debe decir **95** (no 102) y Wang debe aparecer una sola vez con **8 puntos**. Revisar un período anterior a abril 2025 (ej. 2024) → sus valores no deben haber cambiado.
5. **Reparto General**: entrar a `/RepartoGeneral` → la tabla no debe tener ninguna columna con nombre de inversor, solo Período/Ventas/Resultado/Util. Punto/Util. Punto USD/Estado.
6. **Historial de Resultados**: el texto "Vista Anual ER" no debe aparecer en ningún lado del sidebar (ni para Admin ni para Inversor) → debe decir "Historial de Resultados" en ambos → el título de la página debe decir "Historial de Resultados {año}".
7. **Notificaciones**: como Admin, click en "Nueva Notificación" (sidebar o botón en "Notificaciones") → elegir un rol → debe cargar automáticamente los usuarios de ese rol como chips → sacar algún chip puntual con "×" → completar Asunto/Mensaje → tildar "correo", "in-app", o ambos → confirmar con el diálogo de SweetAlert2 → debe llegar la notificación in-app (campanita) y/o el email a los usuarios que quedaron en la lista, no a los que se sacaron. Probar enviar sin tildar ningún canal → debe bloquear con mensaje claro.
8/9. **Mi Inversión**: entrar como Inversor → la tabla de historial no debe reaccionar al click en los encabezados de columna (sin flechitas de orden, sin reordenar) → debe mostrar Año y Mes como columnas separadas al principio (mes en palabras, ej. "Agosto") → no debe tener columnas "Puntos" ni "TC" → el orden visual debe ser año más reciente primero, y dentro del año, mes más reciente primero.
10. **Importes sin salto de línea**: angostar la ventana del navegador (o usar el modo responsive de las devtools) en Dashboard, Mi Inversión, Reparto General, Estado de Resultados (mensual y anual), Liquidaciones — ningún importe con signo "$"/"U$D"/"USD" debe cortarse en dos líneas.

### Etapa 12 — Fichador de empleados (QuickPass) — E2-02

**Escaneo de reutilización (obligatorio antes de implementar):** se re-confirmó el escaneo ya hecho en Diseño/Arquitectura (`docs/*/definiciones/{2-disenador-funcional,3-arquitecto-mvc,5-implementador}.md` de todos los proyectos del estudio) — sin match. Ningún proyecto tenía todavía un `HttpClient` tipado contra un SaaS externo de solo lectura con headers de auth estáticos. Se implementó desde cero. Este módulo queda como el primer patrón de "integración REST de solo lectura con ApiKey/IdEmpresa estáticos + dos APIs con base URL distinta" del estudio — candidato a reutilizar si aparece un caso similar (ver también nota de E2-01 Ayres en `1-analista-funcional.md` §10.1, que sigue pendiente de decisión API vs MySQL directo).

**Alcance implementado:** pantalla P-15 "Fichador" (solo Administrador/SuperUsuario) con 3 tabs — Hoy (fichadas del día), Rango de fechas (resumen de horas con `daterangepicker`), Empleados (listado QuickPass). Datos en vivo, sin persistencia local (confirmado sin migración EF).

**Archivos nuevos:**
- `KoiDumplings.Application/DTOs/QuickPassDtos.cs` — `HoraTrabajadaDiaDto`, `ResumenHorasUsuarioDto`, `EmpleadoQuickPassDto`.
- `KoiDumplings.Application/Interfaces/IQuickPassService.cs`.
- `KoiDumplings.Application/Exceptions/QuickPassIndisponibleException.cs` — carpeta `Exceptions/` nueva en Application (primera excepción de dominio propia del proyecto).
- `KoiDumplings.Infrastructure/Services/QuickPassSettings.cs` — POCO de configuración (mismo patrón que `SmtpSettings.cs`).
- `KoiDumplings.Infrastructure/Services/QuickPassService.cs` — implementación completa.
- `KoiDumplings.Web/Models/FichadorViewModels.cs` — `FichadorIndexViewModel` + 3 sub-ViewModels de ítem.
- `KoiDumplings.Web/Controllers/FichadorController.cs` — `Index`/`Rango`/`Empleados`, todas renderizan `Views/Fichador/Index.cshtml`.
- `KoiDumplings.Web/Views/Fichador/Index.cshtml` — 3 tabs Bootstrap, `daterangepicker`, 3 DataTables client-side, SweetAlert2 para errores de conexión.

**Archivos modificados:**
- `KoiDumplings.Infrastructure/DependencyInjection.cs` — `Configure<QuickPassSettings>`, dos `AddHttpClient` nombrados (`QuickPassEntidades`/`QuickPassReporting`) resolviendo headers desde `IOptions<QuickPassSettings>`, `AddScoped<IQuickPassService, QuickPassService>`.
- `KoiDumplings.Web/appsettings.json` — sección `QuickPass` nueva con las credenciales reales del cliente (`ApiKey`, `IdEmpresa=4364`, `BaseUrlEntidades`, `BaseUrlReporting`, `TimeoutSeconds=10`).
- `KoiDumplings.Web/Views/Shared/_Layout.cshtml` — link "Fichador" en sidebar, sección "Gestión", después de "Tipo de Cambio", visible solo para Administrador/SuperUsuario.

**Schema real descubierto por inspección directa (no publicado en el instructivo — hecho con `curl`/credenciales reales del cliente, autorizado explícitamente por el pedido; los archivos temporales con PII de empleados se borraron apenas terminó la inspección):**

- `GET /Usuarios?excluirFotos=true` (API Entidades) → array plano. Campos usados: `id, nombre, apellido, legajo, email, habilitado, fechaIngreso` (string `"yyyyMMdd"`), `sector.{id, nombre}`. 13 empleados activos en el ambiente real del cliente al momento de la prueba (todos `habilitado:true`).
- `GET /HorasTrabajadas` (API Reporting) → array de objetos usuario×día, ~70 campos por registro (`ParteParaReporteDTO` interno de QuickPass). Campos usados: `idUsuario, nombreUsuario, legajo, nombreSector, fecha` (ISO), `tieneMarcaciones, impar, ausente, tarde, esSectorBajas, horasNetas, movimientosList` (array de strings `"HH:mm"`), `idsMovimientos` (array de ids). **Hallazgo clave:** el campo `impar` (booleano) es exactamente el flag de "turno abierto/incompleto" que el diseño pedía calcular — cantidad impar de marcaciones en el día (ej. una sola fichada = entrada sin salida). Se verificó en vivo un caso real: empleado con `movimientosList: ["09:35"]`, `impar: true`. Mapeo usado: `HoraEntrada = movimientosList[0]`; `HoraSalida = movimientosList[^1]` solo si `!impar && Count >= 2`. `esSectorBajas: true` marca empleados dados de baja (aparecen en el reporte histórico aunque ya no estén activos) — se filtran del tab "Hoy" para respetar el criterio de HU-1 ("empleados activos"); verificado que los 13 registros con `esSectorBajas:false` de "hoy" coinciden 1 a 1 con los 13 usuarios de `/Usuarios`.
- `GET /HorasTrabajadas/ResumenPorUsuario` (API Reporting) → un objeto por usuario. Campos usados: `idUsuario, nombreUsuario, legajo, horasTrabajadasNetasDecimal, horasTrabajadasNetas` (string `"H:MM"` ya formateado por QuickPass), `cantidadDiasTrabajados, cantidadDiasAusente, cantidadDiasTarde`. **No trae** conteo de "turnos incompletos" ni "cantidad de fichadas" — el diseño (`FichadorRangoVM`) pedía esos dos campos pero no existen en este endpoint. Decisión de implementación (no estaba en ninguna de las 4 definiciones previas): `ObtenerResumenPorRangoAsync` hace una segunda llamada en paralelo a `/HorasTrabajadas` para el mismo rango y **agrega** (`Count`/`Sum`, no recalcula horas) el campo `impar` y el largo de `idsMovimientos` por usuario para completar `TurnosIncompletos`/`CantidadFichadas`. Es una agregación de valores ya calculados por la API, consistente con la simplificación de arquitectura §8.2/§8.8 ("el sistema no recalcula, solo proyecta").

**Decisiones técnicas tomadas en implementación (no explícitas en las 4 definiciones):**
1. "Hoy" se calcula en huso horario Argentina explícito (`TimeZoneInfo.FindSystemTimeZoneById("America/Buenos_Aires")`, igual patrón que `CotizacionService.HoyArgentina()`) — evita que "hoy" quede mal calculado si el hosting corre en otro huso (KOI corre en site4now.net, EE.UU.).
2. Se usó la policy `[Authorize(Policy = "SoloAdministrador")]`, no `"RequireAdministracion"` como decía literalmente el texto de arquitectura — porque `InversoresController`/`ConfiguracionController` (citados como precedente explícito en la arquitectura) usan `SoloAdministrador` en el código real. Ambas policies son funcionalmente idénticas en `Program.cs` (`RequireRole(SuperUsuario, Administrador)`) — no es un desvío de permisos, solo de nombre de policy.
3. Las 3 acciones del controller (`Index`/`Rango`/`Empleados`) renderizan la misma vista y cargan Hoy+Empleados siempre (eager) más Rango si hay fechas — se evitó AJAX/partials por simplicidad y porque el volumen es bajo. Cada sección tiene su propio try/catch contra `QuickPassIndisponibleException`: si una falla, las otras dos igual muestran datos (nunca pantalla en blanco completa, criterio de HU-4).
4. Validación de rango máximo 31 días duplicada: en el Controller (antes de llamar al service, con mensaje amigable para SweetAlert2) y en `QuickPassService` (`ArgumentException` como red de seguridad) — mismo criterio que `32-estandares-qa-implementador.instructions.md` para validaciones numéricas de negocio.

**Migración EF:** ninguna (confirmado por las 4 definiciones — sin entidades nuevas, QuickPass es la fuente de verdad).

**Build:** `dotnet build` desde la raíz del repo → **Compilación correcta, 0 errores.** 9 warnings preexistentes sin cambios (NU1902 MailKit/MimeKit — ver VUL-001 pendiente — y CS0114 HomeController.StatusCode), ninguno introducido por esta etapa.

**Sin smoke test funcional** (regla del estudio — el Implementador nunca levanta la app ni prueba flujos por navegador/curl contra el sistema propio). La inspección de la API externa de QuickPass con `curl` fue una excepción explícitamente autorizada por el pedido para descubrir el schema de deserialización antes de codear los DTOs — no es un smoke test del sistema KOI, es descubrimiento de contrato de un tercero. Evidencia de cierre: build limpio + esta revisión de código propia documentada acá.

**Guía de pasos para prueba manual del dueño del estudio:**
1. Login como Administrador (o SuperUsuario) → debe aparecer el link "Fichador" en el sidebar, sección "Gestión".
2. Tab "Hoy": debe listar los empleados activos con su fichada del día — entrada/salida si fichó completo, badge "Turno abierto" si fichó solo entrada, badge "Sin fichada hoy" si no fichó. Ninguna fila debe faltar ni quedar vacía sin explicación.
3. Tab "Rango de fechas": elegir un rango real (ej. últimos 7 días) con el `daterangepicker` → botón "Consultar" → debe mostrar horas trabajadas, cantidad de fichadas, turnos incompletos y días ausente por empleado. Probar un rango de más de 31 días → debe mostrar el mensaje de error de rango máximo sin romper la pantalla.
4. Tab "Empleados": debe listar todos los empleados de QuickPass con su estado Activo/Inactivo, igual a lo que se ve en el panel de QuickPass.
5. Caso de error: cambiar transitoriamente el valor de `QuickPass:ApiKey` en `appsettings.json` a un valor inválido y reiniciar → visitar `/Fichador` → debe aparecer un SweetAlert2 con el mensaje "No se pudo conectar con el sistema de fichadas..." en vez de una excepción visible o pantalla en blanco. Restaurar la ApiKey real después de la prueba.
6. Verificar que un usuario con rol Inversor no puede acceder a `/Fichador` (debe redirigir/denegar, no mostrar contenido).

### Etapa 11 — Migraciones aplicadas en PRODUCCIÓN (sesión actual)
- Ver detalle completo en `trazabilidad.md` (entrada 2026-07-13, "migraciones aplicadas en PRODUCCIÓN"). Resumen: `dotnet ef database update` creó las 22 tablas en `db_a7251f_koidump` (site4now.net, estaba vacía — primer aprovisionamiento). Seed básico (roles/catálogo/SuperUsuario) y la migración histórica completa (misma plantilla validada en local) quedaron aplicados: 19 períodos, 373 gastos, 15 inversores, 16 asignaciones, 265 liquidaciones, capital USD 287.500 — idéntico a lo validado en local.
- **Nota operativa importante:** el hosting MySQL remoto cortó la conexión dos veces durante operaciones con muchas escrituras secuenciales chicas (el seed de catálogo, con un `SaveChangesAsync` por Rubro sin transacción envolvente, y el primer intento de import vía navegador). Si se vuelve a tocar esta base desde una herramienta con timeout corto, preferir sondeo directo a la base en vez de esperar la respuesta HTTP/navegación.
- SuperUsuario de producción quedó con las credenciales por defecto del código (decisión explícita del cliente) — pendiente cambiarlas antes de exponer el sitio públicamente.
- Sin cambios de código — solo despliegue de esquema (EF) y datos (mecanismo de importación ya existente).

### Etapa 10 — Migración histórica ejecutada en local
- Ver detalle completo en `trazabilidad.md` (entrada 2026-07-13, "migración histórica ejecutada"). Resumen: ambos Excel fuente transformados a la plantilla de `ImportacionInicialService` y cargados vía el endpoint real `/ImportacionInicial` (SuperUsuario), tras vaciar los datos de demo en la DB local. 19 períodos, 373 gastos, 15 inversores, 16 asignaciones, 265 liquidaciones — 0 advertencias. Total Gastos reconcilia al centavo contra el Excel en los 19 períodos; capital migrado = USD 287.500 (coincide con el análisis funcional).
- Sin cambios de código — solo datos, vía el mecanismo de importación ya existente.
- Ejecutado y validado en el **entorno local** únicamente (pendiente replicar en el entorno del cliente cuando corresponda).

### Etapa 9 — Fix sistémico tema oscuro
- Pedido del cliente: alinear el tema oscuro en la totalidad del sistema (no pantalla por pantalla) porque había elementos ilegibles.
- **Diagnóstico (Playwright headless contra la app corriendo local, login real + cookie `koi-tema=dark` para simular SSR fresco):**
  - **Causa raíz:** el proyecto usa Bootstrap **5.1.0** (no 5.3+), cuya `.table` fija `color: #212529` como literal — no vía variable CSS. El override existente `[data-theme="dark"] .table { --bs-table-color: ... }` seteaba una variable que Bootstrap 5.1 nunca lee, dejando el texto de **todas** las tablas/listados (DataTables incluidos) ilegible en oscuro en todo el sistema.
  - `.card-header`/`.card-footer` (y sus variantes `.ov-card-*`) usaban el token fijo `--ov-gray-50` (nunca redefinido en `[data-theme="dark"]`) → cabeceras de card blancas sobre fondo oscuro en toda la app.
  - Paginación de DataTables (`.page-link`, vía `dataTables.bootstrap5`) sin override de tema → botones "Anterior/Siguiente" blancos.
  - `#themeToggle` (botón, no link) sin `background:none` explícito → heredaba el fondo blanco por defecto del user-agent para `<button>`, visible como caja blanca en el topbar oscuro (bug independiente del tema, agravado en oscuro).
  - Alerts nativas de Bootstrap (`.alert-info/success/warning/danger`, usadas directo en varias vistas) sin override de tema.
  - Chart.js en sí NO tenía bug de renderizado (los `isDark` checks de cada vista funcionan bien en carga fresca), pero el toggle de tema es 100% client-side (solo cambia el atributo `data-theme`, sin reload) — los canvases ya creados quedan con los colores calculados en el load anterior hasta que el usuario navega a otra pantalla. Confirmado visualmente comparando toggle-en-vivo vs carga fresca con cookie ya seteada.
- **Fix aplicado (single-file, sin tocar vistas individuales):**
  - `KoiDumplings.Web/wwwroot/css/olvidata-theme.css`: dentro de `[data-theme="dark"]` se agregó `color: var(--ov-text)` directo en `.table`/`.table-light` (más `--bs-table-striped-color/--active-color/--hover-color`), override de `.card-header`/`.card-footer`/`.ov-card-header`/`.ov-card-footer` (fondo `rgba(255,255,255,.03)`), override de `.page-link`/`.page-item.active/.disabled` (paginación DataTables), y override de `.alert-info/success/warning/danger` + `.alert-link`. Fuera del bloque dark: `.ov-topbar-icon-btn` ahora fija `background:none; border:none` (fix general, no solo oscuro).
  - `Views/Shared/_Layout.cshtml`: el click de `#themeToggle` ya no togglea el atributo `data-theme` en vivo — espera la respuesta de `POST /Account/ToggleTema` (que ya persistía la cookie server-side) y hace `location.reload()`. Esto elimina de raíz toda la clase de bugs "toggle sin reload" (Chart.js con colores viejos, y cualquier futuro widget JS que lea el tema solo al cargar) sin necesitar un sistema de re-theming en vivo.
- **Validación:** recompilado (`dotnet build` OK) y verificado visualmente con Playwright headless (login real, click real en el botón de tema, screenshots antes/después) en Dashboard, Estado de Resultados Mensual, Vista Anual ER, Tipo de Cambio, Configuración/Rubros, Inversores — 0 errores de consola, todas las tablas/cards/paginación/alerts legibles en oscuro tanto en carga fresca como en toggle en vivo.
- **Sin migración EF** — cambio 100% de presentación (CSS + un handler JS).
- **Impacto cross-proyecto:** `olvidata-theme.css` es el design system compartido por todos los proyectos del estudio sobre el mismo blankproject base — si otro proyecto activo (ShowroomGriffin, vinosefue, virtualwallet, etc.) usa Bootstrap 5.1 con el mismo archivo de tema, probablemente tenga el mismo bug de tablas/card-headers en oscuro y valga la pena portar el mismo fix.

### Etapa 8 — Refactor UI/UX: fusión Dashboard + Indicadores
- Autorizado directamente por el cliente/dueño del estudio como refactor puntual de UI sobre dos pantallas ya aprobadas (sin ciclo completo Análisis→Diseño→Arquitectura→Presupuesto): sin entidades nuevas, sin migración EF, mismos DTOs/servicios reutilizados.
- **Escaneo de reutilización:** no aplica búsqueda cross-proyecto (no es una entidad/flujo nuevo) — el propio proyecto KOI ya tenía ambas piezas (`IIndicadoresService`/`IndicadoresService`/`IndicadoresDto` como fuente de verdad de KPIs de venta) y se reutilizaron tal cual desde `DashboardService`.
- **Cambio funcional:** pantallas `Dashboard` e `Indicadores` (KPIs de venta) se fusionan en una sola pantalla `Dashboard` con 3 secciones diferenciadas (Ventas / Gastos / Evolución Histórica) + hero de KPIs de resultado global (Ventas Totales, Total Gastos, Resultado, Resultado USD, Rentabilidad %). Todo el contenido —incluido el desglose Facturado(A)/Informal(B) antes solo-Admin— queda visible para todos los roles autenticados (Admin, SuperUsuario, Inversor) bajo `[Authorize]` simple.
- **Domain/Application:** `DashboardDto` (KoiDumplings.Application/DTOs/DashboardDtos.cs) se simplifica — se quitan los campos duplicados que ya calculaba `IndicadoresDto` (VentasA, VentasSalon, VentasPedidos, VentasMostrador, CantidadComensales, CantidadVentas, TicketPromedioA, TicketPromedio, CubiertoProm) y se agrega `public IndicadoresDto? Ventas { get; set; }` como fuente única para la sección "Ventas". Se mantienen los campos propios del hero (VentasTotales, TotalGastos, ResultadoEjercicio, Rentabilidad, TipoCambio, ResultadoUsd, TieneTipoCambio).
- **Infrastructure:** `DashboardService` (KoiDumplings.Infrastructure/Services/DashboardService.cs) inyecta `IIndicadoresService` y delega en él el cálculo de todos los KPIs de venta (`ObtenerAsync(anio, mes)` reutilizado tal cual); ya no recalcula manualmente ticket promedio, cubierto promedio, ventas por canal, etc. Solo conserva lógica propia: existencia de ventas del período (`AnyAsync`, no recalcula KPIs — solo determina `TieneDatos`), gastos por rubro, total de gastos, resultado del ejercicio, rentabilidad %, TC y resultado en USD. `DependencyInjection.cs` no requirió cambios (`IIndicadoresService` ya estaba registrado como Scoped).
- **Web:**
  - `Views/Dashboard/Index.cshtml` reescrita completa: header + selector (sin cambios), hero de 5 KPIs con el estilo de card de Indicadores (icon badge circular, `border-0 shadow-sm`), sección "Ventas" (todo el contenido de la ex-pantalla Indicadores: KPIs, torta canal + barras ticket, tabla desglose por canal, tabla A/B + torta + barras apiladas), sección "Gastos" (tabla Gastos por Rubro existente + nuevo gráfico de barras horizontales por rubro + torta Resultado-vs-Gastos reubicada desde el Dashboard viejo), sección "Evolución Histórica" (gráfico de líneas sin cambios funcionales, reubicado al cierre). Cada sección tiene encabezado diferenciado (icon badge + accent de color: azul=Ventas, rojo=Gastos, verde=Histórico).
  - `IndicadoresController.cs`, `Views/Indicadores/Index.cshtml` e `IndicadoresIndexViewModel` (en `IndicadoresViewModels.cs`) eliminados — sin otras referencias en el repo (verificado por grep antes de borrar).
  - `Views/Shared/_Layout.cshtml`: eliminado el link "Indicadores de Venta" del sidebar (sección "Gestión"). El link "Dashboard" ya era visible para todos los roles, sin cambios.
- **Permisos:** `DashboardController` sigue `[Authorize]` simple (Admin/SuperUsuario/Inversor), sin cambios. El contenido antes restringido a `RequireAdministracion` (Facturado vs Informal) ahora es visible para todos los roles autenticados dentro del Dashboard fusionado — cambio de negocio explícito del cliente, no un descuido de permisos. La policy `RequireAdministracion` sigue vigente y en uso en otros controllers (NotificacionCierre, RepartoGeneral, Liquidaciones, Puntos, Audit) — no se tocó.
- **Sin migración EF** — no se tocaron entidades de dominio ni `VentasMensuales`/`ConceptosGasto`.
- **Build:** `dotnet build` desde la raíz del repo → Compilación correcta, 0 errores (9 warnings preexistentes: NU1902 MailKit/MimeKit — ver VUL-001 pendiente — y CS0114 HomeController.StatusCode, ninguno introducido por este cambio).
- **No hay proyecto de tests automatizados en el repo** (`**/*Tests*.csproj` → sin resultados); validación queda a cargo de QA manual.

### Etapa 7 — ABM Inversores
- InversoresController.cs creado en KoiDumplings.Web/Controllers
- Acciones: Index, Create (GET/POST), Edit (GET/POST), Delete (POST, soft-delete vía IRepository<Inversor>)
- Guard en Delete: bloquea si el inversor tiene usuario vinculado (ApplicationUser.InversorId)
- ViewModels: InversorListViewModel, InversorListItemViewModel, InversorFormViewModel (en ConfiguracionViewModels.cs)
- Vistas: Views/Inversores/Index.cshtml, Create.cshtml, Edit.cshtml
- Sidebar: link 'Inversores' agregado en sección 'Inversiones' (antes de Puntos)
- Sin migración EF (entidad Inversor ya existía)
- Build: PASS

### Bugs resueltos en sesión anterior
- KOI-002: Export Excel ER Anual
- KOI-005: CamarasController
- KOI-006: Link Notificaciones → System

## Pendientes
- Etapa 24 (ajustes de la prueba manual de la Entrega 1): sin pendientes técnicos de código y **sin migraciones**. Falta (a) la prueba manual de los 42 pasos de la entrada de la Etapa 24 —los pasos 40 a 42 son el barrido legal E1 y no son opcionales—, (b) el **commit y deploy**, deliberadamente sin hacer, y (c) **la decisión del dueño sobre el ítem 2.5**: la premisa no se sostiene contra el código (la rentabilidad del Dashboard es Resultado/Ventas del mismo mes y vale igual en las dos monedas), así que se implementó como aclaración de qué mide el KPI, no como duplicación. Si lo que quiere es ver su rendimiento propio al entrar como inversor, eso ya está en Mi Inversión y en el Reporte, y una tarjeta nueva en el Dashboard del inversor es un ítem aparte.
- **Advertencia para cualquier pasada futura sobre envío de mails en KOI:** no volver a escribir `_ = Task.Run(() => _servicioScoped.X())`. Ese patrón rompía en silencio el aviso de cierre a los inversores (Etapa 24, punto 2.1b). El proyecto tiene ahora `IBackgroundJobQueue` (PAT-025): encolar y resolver los servicios del `IServiceProvider` que recibe el trabajo, capturando sólo datos.
- **Advertencia para cualquier pasada futura sobre gráficos:** la app corre con cultura fija es-AR, así que interpolar un `decimal`/`double` crudo dentro de un array de JS lo rinde **con coma** y parte el número en dos elementos. Rompía tres gráficos del Dashboard sin dar error (Etapa 24, punto 2.3). Serializar siempre con `JsonSerializer` o `ToString(CultureInfo.InvariantCulture)`.
- Etapa 22 (Sprint "Entrega 1", Ola 1): sin pendientes técnicos de código. Falta (a) la prueba manual de los 14 pasos de la entrada de la Etapa 22, (b) el **commit y deploy**, deliberadamente sin hacer, (c) **aplicar la migración `E20_ConsolidacionCatalogos_A2` en producción** corriendo antes el pre-vuelo y después el post-vuelo — no se aplica sin backup verificado, (d) subir a mano el bloque `Features:ModuloCamaras` al `appsettings.Production.json` (gitignoreado; sin él el default en código ya lo deja oculto), (e) **decidir con el cliente los 11 subgrupos viejos sin equivalente claro** que la migración no toca, y (f) responder P-B06 (alcance del Dashboard para el Gerente).
- **Ola 2 del Sprint "Entrega 1" (lotes C, D, E y F): pendiente.** Se ejecuta en secuencia, NUNCA en paralelo con la Ola 1 — vuelve sobre `EstadoResultadosController`, `Views/EstadoResultados/Mensual.cshtml` y `Views/ImportacionInicial/Index.cshtml`, que esta ola ya tocó. Notas para esa pasada: (1) `Mensual.cshtml` ahora tiene DOS banderas, `esAdmin` (cierre/reapertura) y `puedeGestionar` (carga) — no volver a unificarlas; (2) el lote F tiene que actualizar el texto del importador, que después de A2b ya no omite por defecto los períodos existentes: los actualiza.
- Etapa 18: sin pendientes técnicos. Falta (a) la prueba manual del dueño del estudio (guía de 10 pasos en la entrada de la Etapa 18, incluido el caso de sesión perdida) y (b) el **commit y deploy**, deliberadamente sin hacer. Nota para futuras pasadas sobre `Views/EstadoResultados/Mensual.cshtml`: la celda de importe de gastos ya no es texto plano — para repintarla hay que usar el helper `pintarImporteConcepto(row, valor)`, nunca `.find('.importe-cell').text(...)`, que borraría el input de los conceptos manuales.
- Nota para futuras pasadas sobre `Controllers/SystemController.cs`: al insertar un método nuevo, verificar que el bloque `[HttpPost]`/`[ValidateAntiForgeryToken]` quede pegado al método que corresponde. Ya pasó una vez (2026-09-08): un método insertado en el medio partió el bloque de `TestEmail` y lo dejó sin antiforgery.
- KOI-007: Users/Index DataTables
- KOI-008: TipoCambio/Index DataTable init
- VUL-001: MailKit/MimeKit → 4.17.0
- Etapa 15: sin pendientes técnicos. Falta (a) la prueba manual del dueño del estudio (guía en la entrada de la Etapa 15), (b) el **commit y deploy**, que quedaron deliberadamente sin hacer porque hay trabajo en paralelo sobre el mismo repo, y (c) validar con el cliente el criterio de que las liquidaciones Pendientes no suman al recupero acumulado.
- Fases 3 y 5 del `plan-implementacion.md`: **implementadas en la Etapa 16**, fusionadas y con enfoque nuevo (el remapeo de 373 gastos de Arquitectura §11.5 quedó superado — ver la entrada de la Etapa 16). Falta (a) la prueba manual del dueño del estudio contra la base local, (b) el **commit y deploy**, y (c) la **migración de los datos reales en producción**, que la ejecuta él con backup previo y verificación de totales.
- Fase 4 del `plan-implementacion.md` (editar meses cerrados): **resuelta con otro enfoque en la Etapa 17** — reabrir el período en vez de editarlo cerrado. El recálculo de liquidaciones que planteaba la Fase 4 ya no hace falta: al volver a cerrar se generan de cero. Queda pendiente (a) **aplicar la migración `E17_LiquidacionesIndiceNoUnico_Reapertura`**, que es requisito funcional, (b) la prueba manual del dueño del estudio (guía en la Etapa 17) y (c) el commit y deploy. Nota que sigue vigente desde la Etapa 16: actualizar un período cerrado **desde la importación** tampoco recalcula liquidaciones — el camino correcto ahora es reabrir el período antes de importar sobre él.
- Fase 6 del `plan-implementacion.md` (API de Ayres): **implementada en la Etapa 21** (módulo E2-01). Quedan (a) la prueba manual del dueño del estudio (guía de 12 pasos en la entrada de la Etapa 21, con el criterio de aceptación duro de agosto 2026: 1.062 ventas / 63.131.109,00), (b) el **commit y deploy**, deliberadamente sin hacer, y (c) **subir a mano el `appsettings.Production.json` con el bloque `Features`**, que es gitignoreado y no viaja con el commit — sin él el flag queda en false y el botón no aparece. Sin sincronización automática ni endpoints de Compras/Caja/Stock/Datos Maestros: quedaron fuera de alcance a propósito.
- Etapa 13: sin pendientes técnicos nuevos — falta únicamente la prueba manual del dueño del estudio (guía completa en la entrada de la Etapa 13, arriba).
