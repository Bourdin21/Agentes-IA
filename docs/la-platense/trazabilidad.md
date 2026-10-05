# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-10-05 15:45 - implementador-dotnet (Sprint 0, gate de precio por rol en Ventas)

- Etapa: Implementación. Rama `entrega-1-migracion`, repo `C:\Sistemas\Ferreteria La Platense`.
  **Sin commit** (cambios en el working tree, a la espera de QA). Base de trabajo `laplatense_dev`;
  **producción no se tocó** (ni deploy, ni Web Deploy, ni ninguna operación contra
  `mysql8001.site4now.net`) y el fixture `laplatense_qa_d9` **no se borró ni se modificó**.
- Alcance: **un solo defecto**. Cualquier usuario con la política `RequireVentas` — incluido el rol
  `Vendedor` — podía vender a cualquier precio: `VentasController.GuardarBorrador` tomaba
  `Items[].PrecioUnitario`, `Items[].Descuento` y `Items[].Recargo` del formulario y
  `VentaWorkflowService.GuardarBorradorAsync` los persistía sin control de rol, así que un vendedor
  podía postear `PrecioUnitario = 1`, confirmar, y descontar stock y postear Caja y cuenta corriente
  al precio que eligió. Estaba abierto en producción. **No se amplió a nada más** (hay un plan aparte
  para el resto).
- Reutilización (escaneo de la instrucción 39, sección 3): paso 1 `cat_resumen.txt` **negativo** para
  este caso — lo más cercano, `PAT-021` (modo de precio por ítem) y `PAT-041` (gate de publicación
  por rol), no es el precedente. El precedente lo traía el brief y se usó tal cual: **`marihogar`**
  (`C:/Sistemas/marihogar`, ya en producción), `VentaService.ConfirmarAsync` (~407-465) y
  `EditarAsync` (~738-773), identificado en ese repo como **CR-22**. Se leyó el código real y se
  copió el criterio, no se desarrolló desde cero. **Patrón nuevo agregado al catálogo:
  `PAT-050`** — el criterio ya vive en 2 proyectos y no estaba catalogado.
- Qué se copió: un booleano `esAdministrador` resuelto **exclusivamente** en el Controller con
  `User.IsInRole` sobre el request autenticado y pasado al Service como dato explícito (el Service
  no consulta Identity), que es la **única** puerta que habilita leer del payload los campos de
  precio. Qué **no** se copió, a propósito: la cascada `(1-d/100)*(1+r/100)` de marihogar — acá la
  fórmula comercial es `(1 - d/100 + r/100)` sobre precio de lista, corregida el 2026-09-03 por
  pedido de Joaquín, y se dejó intacta — ni su manejo de subtotal, porque el de La Platense (subtotal
  c/IVA editable que despeja el precio unitario hacia atrás) es mejor y se queda, solo restringido a
  Administrador.
- Adaptación a La Platense: `Administrador` y `SuperUsuario` pueden override de precio, descuento,
  recargo y subtotal, exactamente como hoy; para `Vendedor` y cualquier otro rol/caller el precio lo
  resuelve el servidor y el descuento y el recargo quedan en 0. Lo que venga en el payload para esos
  campos **se descarta en silencio**, no con un error (no es un error del usuario: la UI no se lo
  deja editar). Corolario deliberado: un descuento >100% posteado por un vendedor **no** devuelve el
  mensaje de validación, se ignora; para un administrador sigue rechazando.
- **Qué precio es "el del producto".** `VentaWorkflowService.PrecioDeVentaVigente`: `PrecioOferta` si
  la oferta está vigente hoy (`Producto.EsOfertaVigente(ArgentinaTime.Hoy)`, día de negocio
  argentino) **y** es `> 0`; si no, `PrecioVenta`. No se copió el `PrecioEfectivo` de marihogar, que
  es otro modelo. Es la **misma** resolución que ya hacía la pantalla al agregar un ítem
  (`producto.precioOferta || producto.precioVenta`, sobre el `PrecioOferta` que
  `ProductoService.BuscarParaVentaAsync` y `CodigoBarrasLookupService.BuscarPorCodigoAsync` ya
  filtran por vigencia), para que el vendedor termine con el precio que la UI le mostró. **Los dos
  caminos de la pantalla (buscador Select2 y lector de código de barras) usan la misma resolución y
  coinciden, así que no hubo que elegir ninguno a dedo.** El `> 0` replica el `||` de JavaScript, que
  con una oferta en 0 cae igual a `PrecioVenta`: sin eso el servidor cobraría 0 donde la pantalla
  mostró el precio de lista.
- **Barrido `LP-002` — puntos de entrada del precio.** Cinco pasadas, no solo el grep obvio (la regla
  ya había quedado a medias 3 veces en este proyecto):
  1. `GuardarBorradorAsync` es el **único** punto de entrada del precio: es el único método que
     escribe `ItemVenta`; `ConfirmarAsync`/`FacturarAsync`/`ConfirmarYFacturarAsync` trabajan sobre
     lo persistido y `Details.cshtml` es solo lectura.
  2. **Hallazgo propio:** el input de subtotal c/IVA **no tiene atributo `name`**, así que no se
     postea nunca — la UI lo despeja sobre `PrecioUnitario` client-side, de modo que el gate de
     `PrecioUnitario` lo cubre por elevación y un segundo control habría sido código muerto.
  3. Hermanos semánticos del mismo payload: `Pagos[].PorcentajeRecargoAplicado` ya se resolvía
     server-side (precedente del mismo patrón dentro del mismo método); `Pagos[].Monto` es lo que el
     cliente pagó y no un precio; `ClientesController.RegistrarAjuste` ya era `RequireAdministracion`
     y `RegistrarCobro` queda en `RequireVentas` por decisión previa documentada.
     **`Items[].PorcentajeIVA` sigue llegando del cliente para cualquier rol** → hueco hermano, ver
     abajo.
  4. **Hallazgo propio (patrón de `LP-008`):** `ItemVenta` declaraba la fórmula en **cascada**
     `(1-Descuento/100)*(1+Recargo/100)` en dos lugares (encabezado de clase y doc de `Subtotal`),
     cuando la real desde el 2026-09-03 es `(1 - Descuento/100 + Recargo/100)`. Era una regla de
     negocio **falsa** viviendo en el repo; corregida en la misma pasada.
  5. Mitad simétrica y vistas/JS: ver los dos puntos siguientes.
- **Mitad simétrica (decisión consciente, no omisión).** El otro lado del gate es la reapertura de un
  borrador: si un administrador dejó un override y después un `Vendedor` re-guarda ese mismo
  borrador, el precio vuelve al del producto y el descuento/recargo a 0. Es la consecuencia de copiar
  el criterio de marihogar ("para un no-administrador el precio SIEMPRE se recalcula") y se eligió a
  propósito sobre la alternativa de conservar el valor persistido, que sería un agujero. Verificado
  por ejecución.
- Vistas y JS: precio, descuento, recargo y subtotal en `readonly` para el no-administrador, tanto en
  las filas que renderiza Razor como en las que arma el JS (`agregarFilaItem`), más el texto de ayuda
  reemplazado. Se usó `readonly` y **no** `disabled` a propósito: un input `disabled` no se postea y
  rompe los índices contiguos `0..N-1` que exige el model binder de `List<T>`. La UI es cortesía — el
  control que vale es el del servidor.
- Reglas aplicadas: **`MH-001`** — la única colección local que llega al SQL de este método es
  `productoIds` (`List<int>`), que la regla declara explícitamente segura (el problema es específico
  de colecciones de `string`); no se introdujo ningún `Contains`/`Any` nuevo. **`LP-003`** — no se
  agregó ningún `value` de input nuevo; los existentes ya usaban el helper `num()` con
  `InvariantCulture` y quedaron intactos, y el atributo agregado (`readonly`) no transporta decimales.
- Capas tocadas: Domain (`ItemVenta.cs`, solo documentación), Application (`VentaDtos.cs`,
  `IVentaWorkflowService.cs`), Infrastructure (`VentaWorkflowService.cs` — el gate y el helper
  `PrecioDeVentaVigente`), Web (`VentasController.cs`, `VentaViewModels.cs`, `Views/Ventas/Editar.cshtml`).
- **Migración EF: ninguna.** `dotnet ef migrations has-pending-model-changes` →
  *"No changes have been made to the model since the last migration"*. No recalcula nada histórico.
- **Evidencia ejecutada, sin navegador** (regla del `.agent.md`, que prohíbe al Implementador levantar
  la app o probar por navegador — ver la discrepancia ya registrada en este archivo):
  `dotnet build` de la solución **0 errores**, 9 advertencias todas preexistentes; prueba de que las
  vistas Razor **sí** compilan en el build (símbolo inexistente inyectado en `Editar.cshtml` → `error
  CS0103`, revertido y recompilado limpio); el render del atributo booleano `readonly="@(!esAdministrador)"`
  verificado **ejecutando** las tres llamadas que emite Razor (`BeginWriteAttribute` /
  `WriteAttributeValue` / `EndWriteAttribute`, confirmadas en `Editar_cshtml.g.cs` con
  `EmitCompilerGeneratedFiles`): con `true` emite `readonly="readonly"` y con `false` **omite el
  atributo entero** — importa porque un `readonly=""` sería verdadero en HTML; y el Service
  ejercitado **directamente contra `laplatense_dev`** con los dos roles dentro de una transacción
  revertida al final (**15 checks OK, 0 filas sobrevivientes**, base en su línea base): precio
  manipulado a $1 → se guardó el `PrecioVenta` del producto; descuento 90% y recargo 50% → 0 y 0;
  producto con oferta vigente → cobró `PrecioOferta`; administrador → override respetado con la
  fórmula no-cascada; 10%+10% devuelve el precio original; >100% rechazado para administrador e
  ignorado para vendedor; y la simétrica confirmada.
- **Deuda abierta, decisión de Joaquín (no un olvido):** `Items[].PorcentajeIVA` sigue llegando del
  cliente para cualquier rol. Es el hermano del hueco que se acaba de cerrar y el único que queda: un
  vendedor que lo postea en 0 baja el total de la venta ~21% sin tocar el precio unitario, porque
  `RecalcularTotales` suma `Subtotal * PorcentajeIVA / 100`. Se dejó sin tocar porque el brief de
  esta ronda lo excluyó explícitamente ("el IVA por línea no se toca") y el alcance era un solo
  defecto. Si el IVA por línea es un dato del producto y no una decisión del vendedor, la corrección
  es idéntica a la de esta ronda y son tres líneas; si el vendedor tiene que poder elegir la
  alícuota, hay que decir por qué. Secundario: un `PrecioUnitario` negativo posteado por un
  administrador no se rechaza en el Service (`GuardarBorrador` no chequea `ModelState.IsValid`);
  preexistente, no se tocó, marihogar sí lo valida.
- Reintentos: 3. Dos del arnés y uno de herramienta — `VentaWorkflowService` revienta en el
  constructor con `IOptions<AfipSettings>` en null (`.Value` en el ctor), así que el arnés necesita
  `Options.Create(new AfipSettings())` aunque el camino probado no use AFIP; `RazorPageBase.Output`
  no tiene setter y hay que construir un `ViewContext` completo con su `TextWriter`, más
  `HtmlEncoder.Default`, para ejercitar el render de un atributo; y `dotnet build` con un `/p:` y una
  ruta larga detrás de `-v q` se parsea como un segundo proyecto (`MSB1008`).
- Reglas que hubo que releer: `32-estandares-qa-implementador` secciones `LP-002`, `MH-001` y
  `LP-003`; el `.agent.md` del rol (evidencia de cierre sin smoke por navegador).
- Pendiente: **QA debe re-verificar**. Este agente no cierra el defecto.

### 2026-10-05 14:40 - qa-mvc (QA Sprint 0, RE-VERIFICACION de los 7 defectos — commit `00f7dd4`)
- Etapa: QA (re-verificacion en contexto nuevo, los 7 criterios arrancando en FAIL).
- Resultado: **GO.** Los 7 defectos (`LP-006`..`LP-012`) quedan **CERRADOS** con evidencia observada,
  incluidos los 2 `major` del circuito de dinero que habian dejado el lote 1 en NO-GO. Deja **1
  hallazgo `minor` nuevo (`LP-013`)**, no bloqueante, con una query de pre-deploy como mitigacion.
- Metodologia: build 0 errores (9 advertencias, todas preexistentes) y
  `dotnet ef migrations has-pending-model-changes` -> "No changes have been made to the model" —
  verificado de forma independiente, no tomado del parte. **Esta vez SI hubo navegador real**:
  corrigiendo el error de metodo del lote 1 (que se quedo en HTTP cuando el lote 2 ya habia
  demostrado que se podia), se instalo `playwright-core` en el scratchpad y se condujo el Chromium
  completo de `ms-playwright/chromium-1243/chrome-win64`, con locale es-AR y timezone
  America/Argentina/Buenos_Aires. **Eso es lo unico que permitio cerrar LP-006**, que por HTTP era
  inverificable. El harness HTTP se uso para las guardas de servidor y las 123 llamadas de regresion.
  Fixture `laplatense_qa_d9` reutilizado, con linea base fijada antes de probar; `laplatense_dev` y
  produccion sin tocar.
- LP-009 cerrado en **6/6 vias** (venta confirmada, gasto alta, gasto anulacion, cobro de CC,
  movimiento manual, cierre diario), cada una rechazada con el mensaje del cierre MENSUAL y sin
  persistir nada, mas 3 controles positivos sobre un mes abierto. **La siembra que lo hizo posible**:
  la rama mensual de la guarda es inalcanzable desde la UI para las vias que imputan a "hoy", porque
  `CerrarMesAsync` prohibe cerrar el mes en curso — se sembro un `CierreCajaMensual` de 10/2026 en la
  base, se probo, y se elimino. Sin esa siembra habria quedado un "verificado por lectura" en las 2
  vias mas importantes. `RegistrarAjusteAsync` queda afuera **verificado, no asumido**: el ajuste de
  CC con fecha dentro del mes cerrado se acepta y NO aparece ninguna fila nueva en `CajaMovimientos`.
- LP-010 cerrado: la Venta 8 (`2026-08-25 01:44:10` UTC = 24/08 22:44 ART) aparece en el rango
  24/08..24/08 con `fecha: 2026-08-24T22:44:10`, NO en 25/08..25/08, la encuentra la busqueda
  `24/08/2026` y no `25/08/2026`, el detalle dice "24/08/2026 22:44" y la grilla en el navegador
  dibuja `24/08/2026, 22:44` — el mismo dia que Caja.
- **LO QUE MAS VALIO Y NO ESTABA EN EL PARTE**: buscar el bug que el propio fix podia introducir.
  `MapearDetalle` ahora proyecta `Fecha = ArgentinaTime.From(venta.Fecha)`, y ese DTO alimenta
  `VentaEditableViewModel.Fecha`, que la pantalla de Editar postea de vuelta: si `GuardarBorrador`
  escribiera ese valor, **cada guardado correria la venta 3 horas**. Probado, no deducido: 5 guardados
  consecutivos del borrador 11 dejan `Fecha` intacta en `2026-09-03 16:20:14.338415`. Un fix de
  proyeccion de fechas siempre hay que probarlo en el camino de ESCRITURA, no solo en el de lectura.
- Barrido LP-002 **verificado por mi cuenta y no por la tabla del implementador** (la regla ya habia
  fallado 2 veces en el sprint): `Domain/Entities` tiene **22** propiedades `DateTime`, no 15 — las 15
  de negocio mas las de auditoria. Clasificadas una por una: 8 instantes UTC proyectados (verificados
  en pantalla, incluido el caso nocturno **Entregas/Details/3, `2026-08-25 02:00` UTC -> "ENTREGADA EL
  24/08/2026 23:00"**), 5 dias calendario correctamente NO proyectados, 2 sin exposicion en ninguna
  pantalla (`Gasto.FechaAnulacion`, `PagoVenta.Fecha`), `Notification` por delta y 4 de auditoria sin
  exponer. Los 3 barridos mecanicos limpios: cero `DateTime.Today`/`UtcNow.Date`/`DateTime.Now`/
  `ToLocalTime` en decisiones de dia/mes, cero `toLocale*` de fecha fuera de `window.Fmt`, ninguna
  `ConvertTime*Utc` fuera del helper salvo los 2 call sites fiscales de AFIP. No quedo ninguna
  convencion vieja suelta.
- MH-001 (6ta aparicion potencial) cubierto **por ejecucion**, que es lo que el implementador no hizo
  (verifico solo con `ToQueryString()`): 123 llamadas a los 6 listados server-side x 19 terminos
  (texto del usuario, importes es-AR e invariantes, substrings, 3 formatos de fecha, nombres de mes,
  y `'`, `%`, `_`, `a%b`, `'; DROP TABLE x;--`) + 9 combinaciones de filtros y rangos limite ->
  **0 respuestas no-JSON, 0 HTTP 500**. En este proyecto esa clase de bug aparecio siempre al
  ejecutar y nunca al leer.
- Criterio 2b (ventana 21:00-00:00 ART) **declarado CUBIERTO**, por pedido explicito del coordinador y
  con el razonamiento a la vista: no es un PASS por lectura de codigo, se apoya en 7 superficies con
  instantes nocturnos REALES vistas en pantalla atribuyendo al dia argentino correcto, en que los
  barridos no dejan ninguna otra forma de derivar un dia o un mes en la app, y en que la guarda y la
  imputacion salen de la misma funcion. Lo unico que sigue sin observarse es el reloj de pared; queda
  como **confirmacion post-deploy de 3 minutos, no bloqueante**.
- **LP-013 (`minor`, NUEVO)**: la guarda protege hacia adelante pero **no repara el pasado** y el
  commit no trae migracion de datos, asi que sobre las filas que LP-009 dejo entrar antes del fix
  `/Caja/Mensual?anio=2026&mes=9` sigue mostrando 777,77 de egresos contra 8.555,54 reales, sin
  ningun indicador, y **no existe accion de reabrir, recalcular ni anular un cierre**. No reabre
  LP-009 (su criterio era bloquear escrituras nuevas, y pasa 6/6): es el residuo. Entregable concreto:
  query de deteccion de movimientos posteados despues del cierre de su propio mes
  (`JOIN` por el rango UTC del mes `WHERE m.CreatedAt > cm.FechaCierre`), **para correr sobre
  produccion antes del deploy**; en el fixture devuelve 3 filas. Catalogo 158 -> 159.
- **TRES FALSOS POSITIVOS MIOS que casi reporte como defectos**, y como se descartaron: (1) "la grilla
  de cierres mensuales no trae filas" era mi selector (`#tablaMensuales` en vez de
  `#tablaCierresMensuales`); (2) "el Dashboard viene en blanco" era que la pantalla rotula
  `ESTADO DEL DIA` en mayusculas y mi probe buscaba `Estado del d` — 944 chars y 7 cards, KOI-014 no
  reproduce; (3) "la CC del cliente 2544 muestra 1 de 3 movimientos" era correcto, los otros 2 son
  del cliente 3. Leccion: antes de escribir un parte, confirmar que el sintoma no es del instrumento.
- Regresion: smoke de 24 pantallas en navegador real, 24/24 HTTP 200 con contenido y **cero
  `pageerror`/`console.error`** en todo el recorrido. Los 3 cierres diarios coinciden exacto con el
  recalculo por dia de negocio ART. Maquina de estados del periodo de caja re-recorrida con las
  transiciones nuevas, incluida "dia de un mes cerrado -> Cerrado" (rechazada) y "mes cerrado ->
  movimiento" (rechazada por las 6 vias), que era el FAIL de la corrida anterior.
- Riesgos que siguen abiertos y NO son de este commit: MH-034 (una sola caja para efectivo +
  transferencia + cheque + deposito, no se concilia contra ningun extracto), MH-033 (cuando entren
  Compras, los pagos a proveedores tienen que postear en el ledger) y la semantica de `Venta.Fecha`
  como fecha de creacion del borrador y no de confirmacion — los tres son decision del analista.
- `git status --porcelain` del repo bajo prueba al cerrar: solo `?? .claude/`, que ya estaba al abrir
  la sesion. **No se escribio una sola linea en `C:/Sistemas/Ferreteria La Platense`.**

### 2026-10-05 13:59 - implementador-dotnet (Sprint 0, ronda de fixes de QA: cierre de los 7 defectos abiertos)

- Etapa: Implementación. Rama `entrega-1-migracion`, repo `C:\Sistemas\Ferreteria La Platense`.
  **Un solo commit**: `00f7dd4`. Base de trabajo `laplatense_dev`; **producción no se tocó** (ni
  deploy, ni Web Deploy, ni ninguna operación contra `mysql8001.site4now.net`) y el fixture
  `laplatense_qa_d9` que QA dejó vivo **no se borró ni se modificó**.
- Alcance: los **7** partes de defecto abiertos por los 3 lotes de QA del Sprint 0 (`LP-006` a
  `LP-012` de `docs/qa/regresiones-manuales.yml`), con los 2 `major` del lote 1 (que había dado
  NO-GO) como prioridad. Sin alcance nuevo.
- Reutilización (escaneo paso 1, `cat_resumen.txt`): dos matches directos, los dos aplicados —
  **`PAT-010`** (ArgentinaTime) se **amplía** para `LP-009`/`LP-010`/`LP-011` en vez de construir
  convención nueva, y **`PAT-016`** se porta tal cual desde los 6 listados ya existentes de este
  mismo repo para `LP-012`. No se agregó ningún patrón al catálogo.
- **`LP-009` (major) — guarda de caja cerrada que ignoraba el cierre mensual.** Causa: consultaba
  únicamente `CierresCajaDiarios`; el commit `628cb7a` había puesto la mitad "no se puede cerrar el
  mes en curso ni uno futuro" y había dejado afuera la simétrica "no se puede imputar a un mes ya
  cerrado". Resuelto con una guarda **única y compartida**,
  `ICajaMovimientoService.ValidarPeriodoAbiertoAsync(diaDeNegocio, accion)`, que consulta mes **y**
  día y devuelve el mensaje listo para mostrar (devuelve el mensaje y no un bool justamente para que
  ninguna vía de escritura pueda redactar el suyo y divergir). Aplicada en las **6** vías de
  escritura de caja relevadas por los usos de `EstaCerradoAsync`, no solo en la que reportó QA:
  venta confirmada, gasto (alta y anulación), cobro de cuenta corriente, movimiento manual y cierre
  diario (que tampoco puede abrirse dentro de un mes cerrado). `RegistrarAjusteAsync` queda afuera a
  propósito y documentado: por diseño explícito no toca Caja.
- **`LP-010` (major) — `Venta.Fecha` con la semántica vieja.** Aplicada la decisión ya cerrada por el
  orquestador (mismo criterio que `CajaMovimiento.Fecha`, sin una segunda convención) en sus **4**
  puntos de consumo: filtros `fechaDesde`/`fechaHasta`, proyección del listado (materializar y
  proyectar con `ArgentinaTime.From`, igual que Caja), buscador global por fecha (rango UTC del día
  de negocio en vez de `Year`/`Month`/`Day` de la columna cruda) y detalle. **Sin migración de
  datos**: la columna ya guardaba instantes UTC correctos, el defecto era de consumo. Verificado que
  `Venta.Fecha` no se escribe desde ningún DTO/ViewModel, así que no hay round-trip posible.
- **Barrido `LP-002` completo** (era la segunda vez en el sprint que quedaba a medias): relevadas las
  **15** propiedades `DateTime` de `Domain/Entities` y todos sus sitios de uso, con tabla de cierre en
  `5-implementador.md`. **3 hallazgos propios, corregidos en el mismo commit**: `AjusteStock.Fecha`
  (historial de stock), `Entrega.FechaEntregada` (detalle de entrega) y `ApplicationUser.CreatedAt`
  (listado y detalle de usuarios) se mostraban crudas en UTC.
- **`LP-007` (minor)**: el `default` del `switch` de `continuar` dejó de significar "guardar y listo"
  — solo la ausencia del campo lo significa, y cualquier valor desconocido falla de forma ruidosa.
  Criterio propio: se redirige con error explícito aclarando que *el borrador se guardó pero la venta
  NO se cerró*, en vez de un `BadRequest` seco que haría pensar que no se guardó nada. Se corrigió
  también el comentario de `Editar.cshtml` que afirmaba el doble envío `"confirmar,confirmar"` que QA
  refutó; la guarda de reentrada se queda, ahora con su motivo real documentado.
- **`LP-008` (minor)**: corregidos los comentarios prescriptivos de `ClasificacionAbcAutomaticaService`
  y `DashboardService` que dejaban en el repo la regla de negocio **falsa** "solo cuentan los ítems
  `Facturada`", conservando la parte válida sobre por qué `Borrador` y `Anulada` quedan afuera. Cerrado
  además el hallazgo que la corrida anterior había dejado "para decidir" (`Confirmada || Facturada`),
  que ya se había resuelto en el commit `7477550`.
- **`LP-006` (minor)**: no era huso sino formato de cliente (`toLocaleString('es-AR')` usa reloj de
  12 h sin meridiano). Helper nuevo `window.Fmt` (`fechaHora` con `hour12: false` y `fecha`) aplicado
  en los **8** renders de fecha de las grillas, para que el formato no vuelva a divergir pantalla por
  pantalla.
- **`LP-011` (minor)**: la validación "Mes o año inválido" era **código muerto para el GET** — un
  `mes=13` reventaba antes, al construir el `DateTime` del rango. El rango válido vive ahora en
  `ArgentinaTime.EsMesDeNegocioValido`, consultado tanto por la pantalla como por `CerrarMesAsync`,
  para que las dos no puedan divergir.
- **`LP-012` (minor)**: **sí correspondía `PAT-016`**, así que se aplicó a los 2 listados de cierres
  (búsqueda global contra importes, las dos fechas con su semántica propia, nombre del mes y "Cerrado
  por", más filtros persistidos en Session y limpieza real de punta a punta) en vez de sacar el
  buscador. Cerrado de paso un gap de diseño: `MensualListar` leía un filtro `anio` que la vista
  **nunca mandaba** — se agregó el control al listado, por la regla de poder filtrar por lo que se ve
  en la grilla.
- **`MH-001` evitado justo donde era el riesgo real de `LP-012`**: la única columna de texto de las
  dos grillas es el nombre del usuario que cerró, que vive en `AspNetUsers` **sin navegación** desde
  las entidades de cierre, y el camino intuitivo (resolver ids y filtrar con
  `CerradoPorUsuarioId IN (...)`) es exactamente el `IN` sobre colección local de string que revienta
  en este provider incluso vacío. Resuelto con **sub-consulta correlacionada** (`Users.Any(...)`), y
  **traducción a SQL verificada con `ToQueryString()`** —sin levantar la app ni conectar a ninguna
  base— confirmando que baja a `EXISTS (SELECT 1 FROM AspNetUsers ...)`. En el listado mensual, el
  match por nombre de mes también se armó sin `Contains` sobre la lista local de ≤12 ints: la forma
  prohibida no se usa ni donde sería inocua.
- Evidencia: `dotnet build FerreteriaLaPlatense.slnx` → **0 errores**, 9 advertencias **todas
  preexistentes** (8 × `NU1902` de MailKit/MimeKit + `CS0114` de `HomeController.StatusCode`), corrido
  3 veces. **Sin migración EF**: `dotnet ef migrations has-pending-model-changes` → *"No changes have
  been made to the model since the last migration"*. Traducción a SQL verificada para las 5 formas de
  consulta nuevas o modificadas que podían no traducir. **Sin smoke test funcional** (regla del rol):
  la verificación por navegador la ejecuta QA, con la guía de 12 pruebas mínimas dejada en
  `5-implementador.md`.
- Estado de los defectos: los 7 quedan **"aplicado, pendiente de re-verificación"**. El cierre lo
  declara QA en contexto nuevo (`30-qa-regresiones.instructions.md`) — el Implementador no cierra
  ningún defecto.
- Pendiente de decisión de Joaquín (no son bugs de esta ronda, quedan anotados): (1) `Venta.Fecha` es
  el momento en que nació el **borrador**, no el de la confirmación, así que una venta empezada el día
  N y confirmada el N+1 figura en el día N en Ventas y en el N+1 en Caja — comportamiento preexistente
  y ajeno a `LP-010`; (2) avisar en la pantalla de Caja que un mes está cerrado **antes** de que el
  usuario intente imputar ahí (hoy el rechazo llega al guardar, que es lo que pedía el criterio de
  aceptación) — es mejora de UX y no se hizo para no ampliar alcance; (3) el **deploy a producción**
  sigue bloqueado hasta el GO de QA.

### 2026-10-05 13:25 - qa-mvc (QA Sprint 0, LOTE 1 — dia y mes de negocio / D9)
- Etapa: QA (gate del commit `628cb7a`, item 0.3 / D9, + migracion de datos
  `20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`). Lote **financiero**, 1 modulo
  (Caja / Gastos / cierres) por instruccion 39 seccion 5, con la superficie LP-002 (Ventas,
  Entregas, Dashboard, Productos, AFIP) cubierta como regresion.
- Resultado: **D9 CERRADO** — los 5 criterios de aceptacion PASS con evidencia observada, mas el
  criterio de arranque de la app (R1). **NO-GO para cerrar el Sprint 0 completo**: el lote deja 2
  defectos `major` nuevos, los dos en el circuito de dinero y los dos derivados del propio cambio.
- Metodologia: el servidor MCP `playwright` **no estaba disponible en la sesion** y tampoco hay
  `playwright-core`; se declaro y se cayo al procedimiento alternativo de la instruccion 33 —
  **automatizacion por HTTP real** (harness Node con cookies de Identity + antiforgery) contra la
  app levantada, mas assertions SQL directas. Para aislar la corrida de **otro lote de QA que
  estaba escribiendo `laplatense_dev` en paralelo** (fila `CobroCC` y usuario `admin.qa` creados
  durante la corrida), se clono la base a **`laplatense_qa_d9`** y la app se levanto contra la
  copia en `https://localhost:7202`. Unico cambio sobre `laplatense_dev`: reescritura del
  `PasswordHash` de `qa.super@test.local` y `vendedor.qa@test.local` (credencial `QaD9#2026x`);
  no se toco `no-reply@olvidata.com.ar`.
- Evidencia de los criterios: un `CajaMovimiento` con instante `2026-10-01 01:44 UTC` (= 30/09
  22:44 ART) se lista y se filtra como **30/09** y entra en el cierre de ese dia
  (`TotalIngresos=1234.56`); un gasto cargado con fecha 30/09 persiste su movimiento en
  `2026-09-30 03:00 UTC` (00:00 ART) y cae en el **mismo** cierre (`TotalEgresos=777.77`);
  cerrada la caja de hoy, `POST /Ventas/Confirmar` responde "La caja de hoy ya esta cerrada…" y la
  venta queda en Borrador (con control positivo antes del cierre); `CerrarMes` del mes anterior
  acepta (09/2026: 96.898,36 / 777,77, e **incluye** la venta de las 22:44 del 30/09), el mes en
  curso y los futuros rechazan con mensajes distintos. Migracion de datos integra: 0 filas sin
  normalizar y todos los cierres guardados coinciden con el recalculo por dia/mes de negocio ART.
- Defectos emitidos (partes al Implementador, 4 items **nuevos** en `docs/qa/regresiones-manuales.yml`,
  catalogo 154 -> 158, `cat_resumen.txt` regenerado):
  **D17 / LP-009 (`major`)** cerrado el mes, el sistema sigue aceptando movimientos dentro de ese mes
  — la guarda de periodo cerrado solo consulta `CierresCajaDiarios` y nunca `CierresCajaMensuales`;
  reproducido: 09/2026 cerrado y aun asi se aceptaron un ajuste de 3.333,33 y un gasto de 4.444,44
  fechados 15/09, con la pantalla mostrando todavia 777,77 de egresos contra 8.555,54 reales.
  **D18 / LP-010 (`major`)** la unificacion cambio `CajaMovimiento.Fecha` pero dejo `Venta.Fecha`
  con la semantica vieja: la Venta 8 (24/08 22:44 ART) se lista y se busca como **25/08** en Ventas
  y como **24/08** en Caja — barrido LP-002 incompleto, y se ve en el Dashboard ("Ventas de hoy 0 /
  $ 0,00" junto a "Caja de hoy $ 2.845,67"). **D19 / LP-011 (`minor`)** `GET
  /Caja/Mensual?anio=2026&mes=13` y `?anio=0&mes=0` dan HTTP 500 en `ArgentinaTime.RangoMesUtc`, y
  el redirect de `CerrarMes` pasa por ahi, asi que el mensaje "Mes o año invalido." agregado en este
  commit es codigo muerto. **D20 / LP-012 (`minor`)** los dos listados de cierres dibujan el
  buscador de DataTables pero el server ignora `search[value]`.
- Catalogo cross-proyecto: MH-009, MH-014 (con reserva de huso del navegador), MH-001 (ejecutado:
  24/24 HTTP 200 sobre busqueda global y filtros, incluidos los dos `List<string>.Contains` de
  `CajaMovimientoService`), CRM-019, LP-003, MH-020, MH-021, KOI-014, KOI-015 → **PASS**.
  LP-002, MH-035, CRM-017, KOI-017 → **FAIL** (son D17 y D18). MH-034 → **riesgo confirmado** (un
  gasto por transferencia cae en el mismo ledger que el efectivo); MH-033 → **N/A hoy**, riesgo para
  cuando entren Compras/CC de proveedores. Ambos escalados al analista, no son defectos de D9.
- Reglas nuevas desde la ultima corrida (2026-08-24): **24 reglas** agregadas a
  `32-estandares-qa-implementador`; se ejecutaron las 10 que este lote puede disparar (ver la tabla
  en `6-qa.md`). Campo "Ultima validacion de reglas cross-proyecto" ya en 2026-10-05.
- Riesgos/supuestos: **la ventana 21:00-00:00 ART del criterio 2 quedo BLOCKED** — a las 12:51 ART de
  la corrida `DateTime.Today`, `DateTime.UtcNow.Date` y `ArgentinaTime.Hoy` valen lo mismo, y las tres
  formas de forzar la divergencia se descartaron a proposito (reloj del sistema: hay agentes
  commiteando en paralelo; `tzutil` a Pacifico: no produce divergencia de fecha a esa hora; contenedor
  Linux: no hay Docker). Cobertura alternativa ejecutada: barrido mecanico que confirma **cero**
  `DateTime.Today` / `UtcNow.Date` / `DateTime.Now` / `ToLocalTime` en una decision de dia/mes en toda
  la app, y ninguna `ConvertTime*Utc` fuera del helper salvo los 2 call sites fiscales de AFIP. Queda
  una prueba manual de 3 minutos descripta en `6-qa.md` para cerrarlo. Para la proxima corrida por
  lotes: **un clon de base por lote**, no compartir `laplatense_dev`.
- `git status --porcelain` del repo bajo prueba al cerrar: solo `?? .claude/`, que ya estaba al abrir
  la sesion. **No se escribio una sola linea en `C:/Sistemas/Ferreteria La Platense`.**

### 2026-10-05 12:30 - implementador-dotnet
- Etapa: Implementacion (Sprint 0 — deuda abierta, prerequisito de la Entrega 3)
- Cambio: cerrados los 4 items del Sprint 0 sobre `entrega-1-migracion`, un commit por item.
  **0.2 (D8)**: ya estaba corregido en `a6a78f0` (construido el 2026-09-03, nunca deployado) —
  `guardarYContinuar` postea el formulario entero a `GuardarBorrador` y solo sigue a
  Confirmar/Facturar si el guardado fue exitoso, en los dos botones. Se verifico el diff y se
  agrego la **guarda de doble envio** que faltaba (dos hidden `continuar` hacian que el `switch`
  cayera en el default: el borrador se guardaba y la venta **no se cerraba, en silencio**).
  **0.3 (D9)**: unificada la semantica de `CajaMovimiento.Fecha` a instante UTC y centralizada
  toda frontera de dia/mes en `ArgentinaTime` (PAT-010 ampliado con `Hoy`, `MesActual`,
  `DiaDeNegocio`, `InicioDiaUtc`, `RangoDiaUtc/DiasUtc/MesUtc`); barrido LP-002 por Caja, Gastos,
  Ventas, CC, Dashboard, Entregas, Productos y vistas; migracion **solo de datos**
  `D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`. **0.4**: modo `--solo-unidad-venta` (solo
  MySQL) corrido contra `laplatense_dev`: 87.542 `Metro` a **0**, `Unidad` 24.929 a **112.471**,
  `Peso` 14 sin cambios, **2.635 candidatos** a corte por metro listados a CSV sin modificarlos.
  **0.5**: cobro de cuenta corriente (Credito en CC + Ingreso en Caja en una transaccion) y ajuste
  manual (solo CC, con motivo obligatorio) sobre la pantalla existente, con origen nuevo
  `"CobroCC"` del ledger de caja propagado al filtro de Caja.
- Motivo: cerrar la deuda abierta antes de arrancar la Entrega 3, segun el bloque "Sprint 0" del
  plan de cierre de alcance aprobado el 2026-10-05. Decisiones de negocio ya cerradas con el
  cliente, no re-litigadas.
- Impacto en capas: **Application** (`ArgentinaTime`, 2 interfaces, 2 DTOs nuevos, defaults),
  **Infrastructure** (8 Services + 1 migracion de datos), **Web** (2 controllers, 1 ViewModel
  nuevo, 2 vistas nuevas, 5 vistas modificadas), **tools** (modo correctivo nuevo).
- Reutilizacion: escaneo paso 1 (`cat_resumen.txt`) con 3 matches — **PAT-010** (ampliado, no
  reconstruido), **PAT-001** (base del ledger; su `pendiente_verificar: true` **resuelto** en esta
  pasada contra `C:/Sistemas/vino-y-se-fue`) y **PAT-019** (importe prellenado con el saldo).
  No hizo falta el grep dirigido de definiciones ajenas.
- Riesgos/supuestos: la migracion D9 discrimina las filas viejas por medianoche exacta
  (`00:00:00.000000`) + `OrigenTipo IN ('Gasto','Ajuste')` — conviene contar esas filas en
  produccion antes de aplicar. `Gasto.Fecha` y `CierreCajaDiario.Fecha` siguen siendo fechas
  calendario a proposito. El ajuste de CC no impacta Caja por diseno. El cobro no registra la
  cuenta real donde entro la plata (MH-034 sigue abierto, consistente con Ventas).
  **Sin deploy**: produccion esta dos migraciones atras (esta + `EntregaTres_...` del item 0.1).

### 2026-10-05 13:05 - qa-mvc (QA Sprint 0, LOTE 3 — correccion de `UnidadVenta` + Dashboard/ABC con ventas Confirmadas)

- Etapa: QA (gate de los commits `3efbe82` y `7477550`, rama `entrega-1-migracion`). Corrida por
  lotes, instruccion 39 seccion 5: 2 modulos, contexto propio.
- Resultado: **GO**. Los **11 criterios de aceptacion en PASS con evidencia observada** contra el
  sistema corriendo (`https://localhost:7200`) y contra `laplatense_dev`. **1 defecto nuevo**,
  `minor`, catalogado como `LP-008`.
- Parte A (`UnidadVenta`): `Metro` **0**, `Unidad` **112.471**, `Peso` **14**, total **112.485** sin
  cambios — coincide exacto con lo reportado. CSV con **2.635 registros unicos** (2.637 lineas
  fisicas: el producto 66109 tiene un salto de linea embebido dentro del campo `Nombre`
  entrecomillado, o sea un registro RFC4180 valido partido en dos); los **2.635 ids verificados uno
  por uno en la base, los 2.635 en `Unidad`** — listados y no modificados. `step="1"` observado en
  pantalla sobre dos productos **que estan en el CSV** (venian de `Metro`) y `step="0.001"` + acepta
  `2.5` sobre un producto en `Peso`.
- **No requiere SQL Server: probado con una cadena de conexion deliberadamente inalcanzable**, no por
  ausencia del servicio (MSSQLSERVER y SQLEXPRESS estan corriendo en la maquina, asi que la ausencia
  no habria probado nada). Idempotente: segunda corrida es no-op, exit 0, sin CSV nuevo.
- **El fix de `MH-001` (quinta aparicion, variante `Any()` + `EF.Functions.Like` sobre `string[]`
  local) se verifico por EJECUCION, no por lectura:** la segunda corrida corta antes del query de
  patrones, asi que se **sembraron 2 filas en `Metro`** (una que matchea "CABLE" y una que no matchea
  ningun patron) y se volvio a correr — los 6 grupos / 8 patrones `LIKE` corrieron sin excepcion y el
  listado salio correcto. Estado restaurado al snapshot exacto.
- Parte B (Dashboard / ABC): Dashboard muestra **"Ventas de hoy: 4 · $ 2.611,11"**, exacto contra el
  oraculo. Top del mes muestra el producto de la venta `Confirmada` con **8** unidades. Recalculo ABC
  disparado desde la UI reporta **"5 productos con ventas en el periodo"** (con el criterio viejo
  habrian sido 4) y el **producto 67 — que aparece UNICAMENTE en ventas `Confirmada` — quedo en
  clase `B`**: ese es el discriminador decisivo. `Borrador` y `Anulada` excluidas de los tres
  calculos, probado con discriminadores de **9.999 y 5.555 unidades** que habrian dominado el Pareto.
  Dia de negocio ART verificado con el par de borde 02:00 UTC de hoy (= ayer 23:00 ART, excluida) vs.
  02:00 UTC de manana (= hoy 23:00 ART, incluida) — **`D7`/`MH-009` sigue cerrado**.
- Defecto nuevo **`LP-008`** (`minor`, no corregido, parte de defecto emitido): el XML-doc y el
  comentario de bloque que **justifican** el filtro siguen diciendo *"Solo cuentan los items de
  Ventas en estado `Facturada`"* y *"El filtro por `Estado == Facturada` es imprescindible"*, mientras
  el codigo filtra por `(Confirmada || Facturada)`. Son comentarios **prescriptivos**, no
  descriptivos: persiste una regla de negocio falsa en el repo, y es lo que el proximo lector va a
  tomar como autoridad. Archivos sugeridos: `ClasificacionAbcAutomaticaService.cs` (XML-doc de la
  clase y comentario previo al `Where`) y `DashboardService.cs` (XML-doc de
  `ObtenerTopProductosMesAsync`). **No borrar el comentario, corregirlo** — la parte que explica por
  que `Borrador` y `Anulada` quedan afuera es correcta y es lo valioso (`LP-001`).
- Memoria del estudio actualizada: **`LP-008` creado** en `docs/qa/regresiones-manuales.yml` +
  `cat_resumen.txt`, y **`nota_qa_laplatense_sprint0` agregada a `MH-001`** en el YAML con la variante
  `Any()` y el barrido ampliado (en `32-estandares` ya estaba documentada; en el YAML, que es la via de
  entrada de QA, faltaba).
- Hallazgo de metodo a tener en cuenta en corridas paralelas: **otro proceso estaba escribiendo
  `laplatense_dev` al mismo tiempo** (la Venta #7 paso de `Borrador`/cantidad 1 a `Confirmada`/cantidad
  50 entre dos consultas mias). Los oraculos numericos de la ABC se recalcularon inmediatamente antes
  de cada medicion en vez de reusar el valor anterior.
- Riesgos de liberacion: el modo correctivo todavia **no se corrio contra produccion** (lo corre
  Joaquin; el CSV de produccion va a tener otros ids, los de dev no sirven para marcar a mano); los
  2.635 candidatos y los 14 de `Peso` quedan a marcar por el cliente; `MH-023` latente en el
  denominador del Pareto (hoy 0 productos soft-deleted); `KOI-017` observacion: "Ventas de hoy" y
  "Caja de hoy" usan la misma ventana pero son magnitudes distintas y la pantalla no lo aclara.
- Deuda declarada: la validacion de reglas cross-proyecto de este lote es **parcial** — solo el
  subconjunto que toca sus 2 modulos. `KOI-015`, `KOI-016`, `CRM-017` a `CRM-024`, `MH-020`, `MH-021`,
  `MH-034`, `ELV-008` y las `OLV-*` quedan asignadas a los lotes de Ventas/Caja/CC/Entregas. `MH-022`
  hay que correrla cuando se construya el nivel 2 del Dashboard ("salud financiera", hoy inexistente).
- El servidor MCP `playwright` **no estaba conectado en esta sesion** (declarado): se automatizo
  conduciendo un Chrome real via `playwright-core` desde Node.
- **Repo del sistema bajo prueba: no se escribio ninguna linea.** `git status --porcelain` limpio (solo
  el `?? .claude/` preexistente al arranque de la sesion). Base de desarrollo restaurada y verificada:
  7 Ventas + 4 `ItemsVenta` de prueba borradas, columna `ClasificacionABCSugerida` restaurada desde
  backup con **0 diferencias**, tabla de backup y CSV de prueba borrados.
- Archivos: `docs/la-platense/definiciones/6-qa.md` (bloque "Sprint 0 — LOTE 3 de QA"),
  `docs/qa/regresiones-manuales.yml`, `docs/qa/cat_resumen.txt`, este registro.

### 2026-10-05 13:10 - qa-mvc (QA Sprint 0, LOTE 2 — cobro/ajuste de CC + D8)
- Etapa: QA (evaluacion independiente, contexto fresco). Lote **financiero**, 1 modulo.
- Alcance: commits `3b4d9fa` (item 0.5, cobro y ajuste manual de cuenta corriente de clientes) y
  `800db75` (item 0.2, guarda de doble envio en Confirmar / Confirmar y facturar), rama
  `entrega-1-migracion`.
- Resultado: **GO**. Los **7 criterios de la parte A** y los **4 de la parte B** en PASS con
  evidencia observada (navegador real + lectura directa de `laplatense_dev`). **1 BLOCKED por
  entorno** y **2 defectos nuevos `minor`**.
- Evidencia que vale la pena retener:
  (1) **Atomicidad del cobro demostrada, no inferida**: se inyecto el fallo con un trigger MySQL
  `BEFORE INSERT ON CajaMovimientos` que hace `SIGNAL` sobre `OrigenTipo='CobroCC'`. El cobro
  fallo, **no quedo ni el credito de CC ni el ingreso de caja**, y el salto del `AUTO_INCREMENT`
  (de 5 a 7) prueba que el insert de CC se hizo y se revirtio. Al cerrar los 2 cobros reales de la
  corrida: `SUM(Importe) Origen=Pago` = `SUM(Monto) OrigenTipo='CobroCC'` = 3095.37, **1:1 sin
  huerfanos**. Trigger eliminado.
  (2) **Permisos verificados tambien por POST directo**, no solo por visibilidad del boton: el
  Vendedor no ve "Ajuste manual", el `GET` le da `AccessDenied`, y un `POST` a `RegistrarAjuste`
  con un token antiforgery valido suyo no persiste nada.
  (3) **`LP-003`/`D5` (cultura) PASS en el lugar donde era inmediato y no latente**: el importe
  arranca prellenado y el HTML real trae `value="12345.67"` invariante, con el input poblado en el
  navegador.
  (4) **D8 CERRADO en su camino `confirmar`**: reproduccion exacta del caso original (venta 7,
  cantidad 1 -> 50, pantalla "$ 76,84") -> se confirma con `Total = 76.84`, no con el $ 1,54 viejo.
  Triple disparo del handler con `jQuery.trigger('click')` (que ignora `disabled`, asi que ejercita
  la guarda de reentrada y no solo el bloqueo del boton) -> **un unico POST** en la red, una sola
  confirmacion, stock/Caja/CC una sola vez.
- **Hallazgo de proceso**: la premisa del commit `800db75` **no se reproduce**. El commit justifica
  la guarda en que un segundo click posteaba `continuar=confirmar&continuar=confirmar` y el `switch`
  caia en el default dejando el borrador guardado sin cerrar la venta; posteado a mano ese POST
  duplicado sobre un borrador confirmable, la venta **queda Confirmada** (el `SimpleTypeModelBinder`
  de ASP.NET Core toma el primer valor, no la concatenacion). La guarda de reentrada es correcta y
  se queda, pero el agujero de esa clase que **sigue abierto** es otro: un valor **desconocido** de
  `continuar` guarda el borrador y no cierra la venta en silencio (`LP-007`).
- Defectos catalogados (partes de defecto emitidos al Implementador, con criterio de
  re-verificacion que arranca en FAIL):
  - **`LP-006`** (`minor`) — la hora de los ledgers se renderiza en reloj de 12 horas **sin AM/PM**:
    un cobro de las 13:04 ART se muestra `01:04:22` y un movimiento de las 00:00 se muestra
    `12:00:00`. El servidor esta bien (el wire entrega `2026-10-05T13:04:22`, ya en ART y sin `Z`:
    **no** hay doble conversion, no es `MH-014`); el defecto es solo de formato en
    `new Date(v).toLocaleString('es-AR')`. Confirmado identico en `chrome-headless-shell` y en
    Chromium completo, asi que **no es artefacto del entorno de prueba**. Afecta
    `Clientes/CuentaCorriente.cshtml` y `Caja/Index.cshtml` (en Caja es preexistente).
  - **`LP-007`** (`minor`) — el `switch` de `continuar` en `GuardarBorrador` cae en el caso por
    defecto para cualquier valor no reconocido: HTTP 200, borrador guardado, venta sin cerrar, **sin
    ningun mensaje**. Residual server-side de la clase de D8; la guarda de `800db75` es solo de
    cliente.
- BLOCKED: **la rama `facturar` de `guardarYContinuar` no es ejercitable** — sin certificado AFIP el
  boton no se renderiza, asi que no hay camino de usuario para disparar `continuar=facturar`. Es
  BLOCKED **por entorno**, no por criterio mal escrito, y es la verificacion que de verdad cierra el
  riesgo fiscal original de D8: **re-verificarla como condicion de habilitar AFIP**, no despues.
- Informativos anotados sin catalogar (D17 el mensaje crudo de EF que se filtra a pantalla en el
  rollback; D18 el ajuste de Credito sin tope, que es coherente con el diseno; D19 `ConfirmarAsync`
  saltea la verificacion de cobertura de pagos en los dos sentidos cuando hay un pago en CC —
  preexistente de Ventas, para el lote de Ventas).
- Nota de herramientas: **el servidor MCP `playwright` no estaba disponible en la sesion**. Se
  declaro y se cubrio con verificacion automatizada equivalente (Playwright instalado en el
  scratchpad de QA, reusando los binarios de Chromium ya presentes en `ms-playwright`), no con
  procedimiento manual ni con revision de codigo.
- Memoria: `6-qa.md` v5 con el bloque del lote y el campo **"Ultima validacion de reglas
  cross-proyecto" inicializado en 2026-10-05** (no existia: la memoria v4 es previa a la regla).
  Catalogo cross-proyecto con los 2 items nuevos y el indice regenerado.
- Estado de `laplatense_dev`: **restaurada a su linea base y verificada** (CC 0 filas, Caja 9 filas,
  ventas 7/9/10/11 de vuelta en Borrador con sus totales originales — recalculados con la logica del
  propio sistema, no por SQL —, stock y pagos restaurados, usuario de prueba eliminado, trigger
  eliminado).
- **El repo del sistema bajo prueba no se modifico**: `git status --porcelain` devuelve solo
  `?? .claude/`, que ya estaba al arrancar la corrida.
- Pendiente para la corrida siguiente: re-verificar `LP-006` y `LP-007` en contexto nuevo con los
  criterios de vuelta en FAIL; **recibir del lote 1 el barrido completo de reglas cross-proyecto**,
  que esta corrida no tuvo y por eso declaro el hueco en vez de darlo por hecho.

### 2026-10-05 12:35 - implementador-dotnet
- Etapa: Implementacion (hallazgos de proceso del Sprint 0)
- Cambio: tres aportes a la memoria del estudio, mas dos cosas que **requieren decision de
  Joaquin**.
  (1) **MH-001 por quinta vez en el proyecto, en variante nueva**: `patrones.Any(pat =>
  EF.Functions.Like(...))` sobre un `string[]` local revienta igual que el `IN`, pero con otro
  mensaje (`UnreachableException: A RelationalTypeMapping collection type mapping could not be
  found`) y **sin ningun `.Contains(` en el codigo**, asi que el grep canonico de la regla no lo
  encuentra. Documentada la variante en `32-estandares-qa-implementador.instructions.md` con el
  barrido ampliado a `grep -rnE "\.(Contains|Any)\("`. La encontro la **ejecucion real** contra
  `laplatense_dev`, no la revision de codigo.
  (2) **PAT-010 ampliado** en `docs/patrones/catalogo.yml` con la API de dia/mes de negocio y con
  la zona resuelta por cadena de fallback (IANA, id de Windows, UTC-3 custom): el helper de
  la-platense queda como candidato a portar al template base, reemplazando el de blankproject.
  (3) **PAT-001 confirmado**: `pendiente_verificar` pasado a `false` con las rutas reales, y
  agregada la-platense como segunda referencia por los dos caminos de alta manual (cobro con
  impacto en caja vs. ajuste sin impacto) que la version original no tenia.
- Motivo: obligaciones del rol — resolver los `pendiente_verificar` que se cruzan en la pasada y
  catalogar lo genuinamente reutilizable antes de cerrar la etapa.
- Impacto en capas: ninguno (memoria documental del estudio).
- Riesgos/supuestos: **dos puntos abiertos para Joaquin.**
  (a) **Hallazgo fuera de alcance, NO corregido**: `DashboardService` cuenta las ventas del dia y
  del mes filtrando solo `Estado == EstadoVenta.Facturada`. Desde el 2026-09-03 `Confirmada` es la
  forma normal de cerrar una venta y, con AFIP deshabilitado, casi ninguna llega a `Facturada`: el
  Dashboard va a mostrar **cerca de cero** en cuanto se deploye. No es ninguno de los 4 items del
  Sprint 0, asi que se dejo intacto en vez de ampliar el alcance por cuenta propia. Lo mas probable
  es que el criterio correcto sea `Confirmada || Facturada`.
  (b) **Discrepancia de proceso entre el brief y el rol, resuelta a favor del rol**: el brief de
  esta corrida pedia "verificar en navegador real contra `laplatense_dev` antes de declarar nada
  hecho", mientras `implementador-dotnet.agent.md` prohibe explicitamente al Implementador
  ejecutar smoke tests funcionales (no levantar la app, no probar flujos por navegador) y define
  el build limpio + la guia de pasos manuales como la evidencia de cierre. Se siguio el **rol**,
  que el prompt del agente designa como fuente de verdad. Para no entregar solo "verificado por
  lectura de codigo" — que es justamente lo que el brief rechaza — se produjo evidencia
  **ejecutada** sin navegador: build limpio (con la comprobacion de que las vistas Razor si
  compilan en el build), grafo de DI validado con `ValidateOnBuild`/`ValidateScopes`, **8/8**
  verificaciones de frontera de dia/mes y **24/24** del cobro/ajuste corridas a nivel Service
  contra `laplatense_dev` (incluidos los criterios de aceptacion de D9), mas la corrida real del
  item 0.4. La verificacion por navegador queda en la guia de 9 pasos de `5-implementador.md`.
  **Si Joaquin quiere que el Implementador haga el smoke test por navegador, hay que cambiar la
  regla en el `.agent.md`, no pedirlo por brief** — si no, la contradiccion se repite en cada
  corrida.


### 2026-08-10 09:00 - orquestador / implementador (arranque de Implementación)
- Etapa: Implementacion (planificacion de secuencia de entrega)
- Cambio: Joaquín pidió dividir la Implementación (139h ya aprobadas) en **3 entregas funcionales incrementales** para que el cliente pueda probar/usar partes del sistema mientras el resto sigue en desarrollo. Plan armado y registrado en `5-implementador.md`: **Entrega 1 — Fundamentos** (Usuarios/roles, Catálogo, Unidades de medida/conversión, Stock+puesta a punto, Código de barras — 30h); **Entrega 2 — Motor de ventas** (Ventas+CC clientes, AFIP, Caja, Gastos, Entregas a domicilio adelantado desde Etapa 2 original, Dashboard Corte 1 nivel día+tendencias — 61h); **Entrega 3 — Ciclo completo** (Proveedores+Compras, CtaCte empleados, CtaCte consolidado del negocio, Presupuestos, Aumento masivo, Devoluciones+NC/ND AFIP, Dashboard Corte final nivel salud financiera — 48h).
- Motivo: pedido explícito de Joaquín de dar dinamismo al proyecto y entregar valor real al cliente antes del cierre total, en vez de esperar a las 139h completas para la primera entrega utilizable.
- Impacto en capas: ninguno técnico todavía — es una reorganización de secuencia de entrega sobre el WBS ya aprobado, no una re-estimación ni un cambio de alcance/precio. El Dashboard (12h, un solo módulo en el WBS) se fasea en 2 cortes sin sumar horas.
- Riesgos/supuestos: la suma de las 3 entregas (30+61+48=139h) coincide exacta con el WBS aprobado (Etapa 1 101h + Etapa 2 38h) — verificado explícitamente para no reabrir el gate de Presupuesto. El precio ya cerrado (USD 1.500/3 pagos o USD 1.800/12 pagos) no cambia. Encaje comercial propuesto (no impuesto): si el cliente eligió la modalidad de 3 pagos, cada entrega cerrada puede alinearse con el cobro de una cuota. Pregunta abierta de `1-analista-funcional.md` §9 (quién anula una venta facturada) sigue pendiente y bloquea específicamente el módulo de anulación en Entrega 3, no el arranque de Entrega 1.

### 2026-08-10 09:30 - orquestador (regla nueva de estudio, no especifica de este proyecto)
- Etapa: Implementacion (regla transversal agregada durante Entrega 1)
- Cambio: Joaquin pidio que no haya errores de ortografia ni acentuacion faltante en ningun texto de UI (vistas, ViewModels, mensajes SweetAlert2/TempData/JS), y que quede plasmado como regla del estudio para todo desarrollo futuro, no solo para La Platense. Agregada la seccion "Ortografia y acentuacion en texto de UI" en `C:/Sistemas/Agentes-IA/.github/instructions/25-frontend-design-system.instructions.md`, referenciada desde `23-web.instructions.md` (ViewModels/DataAnnotations) y agregada como paso 13 del checklist de nueva entidad en `26-checklists.instructions.md`.
- Motivo: pedido explicito de calidad de texto visible al cliente final — no es un bug funcional puntual de este proyecto, es un estandar transversal (por eso se documenta en las instructions globales de Agentes-IA, no en las definiciones propias de La Platense).
- Impacto en capas: Presentacion (Views, ViewModels, JS de UI) en todos los proyectos futuros del estudio. Sin impacto en Datos/Negocio.
- Riesgos/supuestos: la regla explicita que NO aplica a la documentacion tecnica interna de Agentes-IA (`.github/**`, `docs/**`), que mantiene su convencion historica sin tildes por temas de encoding del propio tooling — solo aplica a texto que efectivamente ve un usuario/cliente final. Se notifico al agente implementador que esta corriendo la Entrega 1 de este proyecto para que aplique la regla antes de cerrar su tarea.

### 2026-08-10 15:00 - implementador (cierre de Entrega 1)
- Etapa: Implementacion (cierre de Entrega 1 — Catalogo, Stock y Usuarios)
- Cambio: implementados los 5 modulos de la Entrega 1 sobre `C:\Sistemas\Ferreteria La Platense`: (1) catalogos simples Marca/Modelo/Categoria (CRUD + DataTables server-side); (2) Producto (nucleo de la entrega, con conversion de unidad compra/venta via `IUnidadMedidaConversionService`, validacion de la regla R4 en el Service); (3) Stock — listado con alerta visual (negativo o bajo el minimo) + `AjusteStock` auditado (reutiliza patron `StockController` de ShowroomGriffin) que marca `StockVerificado=true`; (4) Codigo de barras — `Producto.CodigoBarras` unico + `ICodigoBarrasLookupService` + endpoint de prueba AJAX desde el Catalogo (listo para que Ventas lo reutilice en la Entrega 2); (5) Usuarios y roles — agregados `Vendedor` y `Repartidor` al seed, extendido `GetAssignableRoles()`, nueva policy `RequireCatalogoConsulta`. Generada la primera migracion EF real del proyecto (`EntregaUno_CatalogoStockUsuarios`). Build limpio (0 errores). Aplicada tambien la regla nueva de ortografia/acentuacion de UI (entrada anterior, 09:30) sobre todo el texto escrito en esta entrega.
- Motivo: ejecutar el alcance aprobado de la Entrega 1 del plan de 3 entregas (ver entrada 2026-08-10 09:00) para que el cliente pueda empezar a probar catalogo/stock mientras se construyen las Entregas 2 y 3.
- Impacto en capas: Domain (5 entidades + 2 enums nuevos), Application (7 interfaces + DTOs nuevos), Infrastructure (7 Services nuevos, AppDbContext con 5 DbSet + Fluent API, SeedData con 2 roles nuevos, DependencyInjection), Web (5 Controllers nuevos + 1 modificado, 14 Views nuevas, sidebar extendido, nueva policy de autorizacion). Detalle completo archivo por archivo en `5-implementador.md` ("Archivos y capas modificadas").
- Riesgos/supuestos: migracion generada pero **no aplicada** a ninguna base de datos (responsabilidad del cliente/Joaquin en dev-staging). Hipotesis de factor de conversion fijo por producto queda codificada tal cual en `UnidadMedidaConversionService` — pendiente de confirmar con el cliente antes de Compras (Entrega 2). `Marca`/`Modelo`/`Categoria` bloquean la baja si estan en uso por un Producto activo (regla agregada por el Implementador, no explicita en `3-arquitecto-mvc.md`, pero coherente con el patron de `marihogar`). Ver el resto de riesgos nuevos en `5-implementador.md`.

### 2026-08-10 16:00 - qa-mvc (QA funcional de Entrega 1)
- Etapa: Pruebas funcionales (primera entrada del proyecto a QA)
- Cambio: validada por revisión de código completa (Domain/Application/Infrastructure/Web, sin ejecución en caliente — no hay base con la migración aplicada) la Entrega 1 (Catálogo, Stock, Usuarios/roles, Código de barras) sobre `C:\Sistemas\Ferreteria La Platense`. `dotnet build FerreteriaLaPlatense.slnx` → 0 errores. Cargado y ejecutado el playbook cross-proyecto completo `docs/qa/regresiones-manuales.yml` (30 ids: ShowroomGriffin/KOI/delicias-naturales/ganaderia/vinosefue/crm-olvidata) mapeado a Catálogo/Stock/Usuarios — **0 regresiones reproducidas** (12 ids aplicaron con PASS, 18 N/A justificados por módulo inexistente en esta entrega). Criterios de aceptación PF13/PF14 y reglas R4/R10/R11 verificados PASS por código. Permisos por rol (Admin/Vendedor/Repartidor) verificados: policy de controller/action coincide con gate de sidebar en las 8 pantallas de esta entrega.
- Motivo: gate obligatorio de QA antes de que el cliente pruebe una entrega funcional (`00-operativa-global.instructions.md`: "No iniciar Documentación al cliente sin QA aprobado").
- Impacto en capas: Web únicamente — auto-fix aplicado sobre 2 defectos de ortografía/acentuación (regla nueva del estudio, entrada 2026-08-10 09:30): `'Si, eliminar'` → `'Sí, eliminar'` en `Views/Productos/Index.cshtml`, `Views/Marcas/Index.cshtml`, `Views/Modelos/Index.cshtml`, `Views/Categorias/Index.cshtml`; `'Exito'` → `'Éxito'` en `Views/Shared/_Layout.cshtml` (toast global de éxito, máxima visibilidad). Ambos son fixes de contenido de string puro, sin lógica nueva; no requieren alta en `regresiones-manuales.yml` (no son regresiones funcionales). Re-build post-parche: 0 errores, mismas advertencias preexistentes.
- Riesgos/supuestos: documentado un defecto fuera de alcance (D3, `UserViewModels.cs`, mensaje de validación de email sin tilde en "válido" — archivo preexistente no tocado por Entrega 1, se deja para el próximo touch del Implementador) y una mejora de UX no bloqueante (D4, link de Notificaciones ausente del sidebar para Vendedor/Repartidor pese a que el controller ya lo permite por ser bandeja propia — sin riesgo de seguridad). **Recomendación: GO condicionado** — antes de que Joaquín o el cliente prueben esta entrega, se debe aplicar `dotnet ef database update` con la migración `EntregaUno_CatalogoStockUsuarios` (generada por el Implementador pero nunca aplicada a ninguna base). Riesgos de negocio ya declarados por el Implementador (factor de conversión fijo por producto; ajuste de stock "pisa" en vez de sumar/restar) siguen vigentes sin cerrar, no bloquean Entrega 1. Detalle completo en `definiciones/6-qa.md`.

### 2026-08-10 16:32 - orquestador (cierre de la condición del GO de QA)
- Etapa: Implementacion (Entrega 1 — post-QA)
- Cambio: aplicada la migración `EntregaUno_CatalogoStockUsuarios` contra la base local de desarrollo (`laplatense_dev`, MySQL 8.0 local) mediante `dotnet ef database update`. Verificado por conexión directa a MySQL que las tablas se crearon correctamente: Identity (`AspNetUsers`, `AspNetRoles`, etc.), `Notifications`, `PreferenciasUsuario`, y las nuevas de Entrega 1 (`Marcas`, `Modelos`, `Categorias`, `Productos`, `AjustesStock`), más `__EFMigrationsHistory` con el registro de la migración aplicada.
- Motivo: era el único prerequisito bloqueante que dejó el QA para pasar de "GO condicionado" a GO real — sin esto no había ninguna tabla creada para que Joaquín/el cliente prueben.
- Impacto en capas: Datos (base local `laplatense_dev` ahora con el esquema real de Entrega 1). Sin cambios de código.
- Riesgos/supuestos: la ejecución de `dotnet ef` imprime un `HostAbortedException`/log Fatal de Serilog en consola durante la resolución del DbContext de diseño — es un comportamiento esperado del tooling de EF (aborta el host antes de `app.Run()`), no una falla real; se confirmó éxito por inspección directa de las tablas en MySQL, no por el texto de consola. Queda como nota para no interpretar ese log como error en corridas futuras de migraciones en este proyecto.

### 2026-08-10 17:00 - orquestador (config de producción + ajuste de roles, dentro de Entrega 1)
- Etapa: Implementacion (Entrega 1 — post-QA, ajustes previos a deploy)
- Cambio: (a) Joaquín confirmó el SMTP real de producción para notificaciones/errores (`vps-5574162-x.dattaweb.com`, cuenta `no-reply@olvidata.com.ar`, destinatario de errores `olvidatasoft@gmail.com`) y la URL real ya configurada (`https://ferreterialaplatense.com.ar/`) — aplicado directamente en `FerreteriaLaPlatense.Web/appsettings.Production.json` (`AllowedHosts` + `Olvidata_Email:Smtp`), archivo gitignorado, nunca se commitea. (b) Pedido de agregar el rol **Administrador** (acceso total al sistema excepto las herramientas de `SystemController`, que quedan exclusivas de `SuperUsuario`) y (c) redirigir a la pantalla de Stock luego de iniciar sesión (en vez de Home).
- Motivo: preparar el sistema para el primer deploy real a producción y cerrar la brecha de roles — hasta ahora solo existía `SuperUsuario` con permisos de escritura total; el negocio necesita un rol de administrador operativo distinto del acceso técnico de Olvidata.
- Impacto en capas: Datos/Identity (nuevo rol), Negocio (nueva policy `RequireAdministracion`), Presentación (controllers Marcas/Modelos/Categorias/Productos/Stock/Users cambian de `RequireSuperUsuario` a `RequireAdministracion` en las acciones de escritura; vistas con `User.IsInRole("SuperUsuario")` ganan el OR con `Administrador`; `AccountController.Login` cambia el redirect por defecto a Stock).
- Riesgos/supuestos: el `FromName` que pasó Joaquín para el SMTP decía "Koi Dumplings - Olvidata" (de otro proyecto del estudio) — se mantuvo el valor ya cargado "La Platense" en vez de sobreescribir con el nombre equivocado, señalado explícitamente al usuario para confirmar. Falta todavía la connection string de MySQL de producción (placeholder sin completar) antes de poder desplegar. Se interpretó "todo el sistema menos superusuario" como incluyendo gestión de Usuarios (el "Admin" de `1-analista-funcional.md` es "todo") — a confirmar si Administrador no debería poder gestionar otros usuarios.

### 2026-08-10 17:30 - implementador (ajuste puntual: rol Administrador + redirect post-login a Stock)
- Etapa: Implementacion (modificacion sobre modulo existente — Entrega 1 ya en GO, no es una entrega nueva)
- Cambio: agregado el rol `Administrador` (const `SeedData.RolAdministrador`, seed en el array de roles) y la policy nueva `RequireAdministracion` (`SuperUsuario` + `Administrador`) en `Program.cs`. `RequireCatalogoConsulta` extendida para incluir tambien `Administrador`. Las acciones de escritura (Create/Edit/Delete/Ajuste) de `MarcasController`, `ModelosController`, `CategoriasController`, `ProductosController` y `StockController` pasaron de `RequireSuperUsuario` a `RequireAdministracion`. `UsersController` (atributo de clase) pasa a `RequireAdministracion` — Administrador gestiona usuarios igual que SuperUsuario, incluida la asignacion del rol `SuperUsuario` a otro usuario desde esa pantalla (decision de negocio ya tomada: "Admin = todo el sistema"). `GetAssignableRoles()` incluye `Administrador`. En vistas, todo `User.IsInRole("SuperUsuario")` relevante (Home, Stock, Marcas, Modelos, Categorias, Productos, sidebar en `_Layout.cshtml`) ganó el OR con `Administrador`; en el sidebar, el link "Sistema / Email" (`SystemController`) se aislo dentro de un `if` propio que sigue exclusivo de `SuperUsuario` mientras "Usuarios" y "Notificaciones" ahora se muestran tambien a `Administrador`. `SystemController.cs` y el endpoint `/health` **no se tocaron** — quedan exclusivos de `RequireSuperUsuario` por ser la excepcion explicita del pedido (acceso tecnico de Olvidata Soft). `AccountController.Login` (GET shortcut y POST de exito) redirige por defecto a `Stock/Index` en vez de `Home/Index`; se preservo el `returnUrl` para deep-links y no se tocaron los redirects de `Logout`/`AccessDenied`.
- Motivo: pedido explicito de Joaquin (ver entrada 2026-08-10 17:00) — el negocio necesita un rol operativo de administrador distinto del acceso tecnico de SuperUsuario, y que el login lleve directo a Stock (pantalla de uso diario) en vez de Home.
- Impacto en capas: Infrastructure (`SeedData.cs` — const + seed de rol), Web (`Program.cs` — 2 policies; 6 Controllers — atributo de autorizacion en acciones de escritura; `AccountController.cs` — 2 redirects; 7 Views — condicion de rol en botones/sidebar). Sin migracion EF (los roles de Identity no requieren cambio de esquema, `AspNetRoles` ya existe).
- Riesgos/supuestos: se interpreto "Admin = todo el sistema menos SuperUsuario tecnico" de forma literal, incluyendo que Administrador puede asignar el rol `SuperUsuario` a otro usuario desde `UsersController` — Joaquin confirmo explicitamente dejarlo asi (no limitarlo por criterio propio del Implementador). Build limpio (`dotnet build FerreteriaLaPlatense.slnx`, 0 errores, mismas advertencias preexistentes de MailKit/MimeKit/CS0114). No se ejecuto smoke test funcional (regla del rol Implementador) — pendiente prueba manual de Joaquin/QA: crear un usuario con rol Administrador y verificar que puede operar Catalogo/Stock/Usuarios pero NO ve ni accede a `/System` (debe dar 403/AccessDenied), y que el login lo lleva a `/Stock`.

### 2026-08-10 17:45 - orquestador (corrección de alcance de permisos de Administrador)
- Etapa: Implementacion (Entrega 1 — corrección puntual sobre el ajuste anterior)
- Cambio: Joaquín corrigió el alcance del rol `Administrador` agregado minutos antes: gestión de Usuarios y Herramientas del Sistema quedan **exclusivas de `SuperUsuario`**, no de Administrador. Revertido `UsersController` a `[Authorize(Policy = "RequireSuperUsuario")]` (estaba en `RequireAdministracion`). En `Views/Shared/_Layout.cshtml` se separó el bloque del sidebar: "Usuarios" y "Sistema / Email" quedan bajo `@if (User.IsInRole("SuperUsuario"))` exclusivamente; "Notificaciones" se sacó de ese bloque (no tiene restricción de rol en `NotificationsController`, es personal de cualquier usuario autenticado) para que Administrador (y en rigor cualquier rol) la siga viendo.
- Motivo: corrección explícita del cliente sobre el alcance recién implementado — Administrador es "todo lo demás" (Catálogo/Stock, que sí quedan en `RequireAdministracion`), no gestión de usuarios ni herramientas técnicas.
- Impacto en capas: Presentación (`UsersController`, `_Layout.cshtml`). Sin cambio en Datos/Negocio — la policy `RequireAdministracion` sigue existiendo y sigue aplicando a Marcas/Modelos/Categorias/Productos/Stock.
- Riesgos/supuestos: build de verificación no pudo completar el paso de copia final porque hay un proceso `dotnet FerreteriaLaPlatense.Web.dll` corriendo (PID 22748) que bloquea el `.dll` de salida — no es un error de compilación (0 errores de código, solo falla el `MSB3027` de copia por archivo en uso). Los cambios son de bajo riesgo (revertir un valor de atributo + condicionales Razor ya usados en otras vistas) — no se forzó el cierre del proceso por si el usuario lo tiene abierto probando manualmente.

### 2026-08-10 18:00 - orquestador (commit + push de Entrega 1)
- Etapa: Implementacion (Entrega 1 — cierre y publicación)
- Cambio: Joaquín confirmó pruebas manuales OK y pidió commitear y pushear. Primer commit del repo (`f5e6af9`, root-commit, 192 archivos) con todo el código de Entrega 1 (Catálogo, Stock, roles Administrador/Vendedor/Repartidor, redirect a Stock, renombrado completo de OlvidataCRM, config de producción). Agregado remoto `origin` → `git@gitlab.com:olvidata/ferreteria-la-platense.git` y pusheada la rama `master`.
- Motivo: cierre formal de la Entrega 1 con el código versionado y publicado en el remoto del estudio, tras confirmación de prueba manual del cliente/Joaquín.
- Impacto en capas: ninguno técnico — solo control de versiones.
- Riesgos/supuestos: excluidos del commit por contener credenciales reales: `site17.PublishSettings` (passwords de FTP/MSDeploy en texto plano — se agregó `*.PublishSettings` a `.gitignore`) y `appsettings.Production.json` (ya estaba ignorado). Verificado explícitamente con `git check-ignore` antes de commitear que ninguno de los dos quedó incluido.

### 2026-08-10 18:15 - orquestador (estrategia de ramas por entrega)
- Etapa: Implementacion (infraestructura de branching, aplica a las 3 entregas)
- Cambio: Joaquín pidió desarrollar las 3 entregas en ramas separadas con re-entrega y merge hacia adelante en cascada. Creadas `entrega-1` (desde `master`, = Entrega 1 ya entregada), `entrega-2` (desde `entrega-1`) y `entrega-3` (desde `entrega-2`), las 3 pusheadas a `origin`. Detalle completo del flujo de trabajo (ciclo desarrollo→entrega→mejoras→re-entrega→merge hacia adelante) documentado en `5-implementador.md`. Checkout activo movido a `entrega-2` para arrancar el desarrollo de esa entrega.
- Motivo: dar continuidad ordenada al plan de 3 entregas funcionales (ver entrada 2026-08-10 09:00) a nivel de control de versiones — permite seguir mejorando una entrega ya entregada sin bloquear el desarrollo de las siguientes, y sin perder esos fixes cuando las siguientes entregas se completen.
- Impacto en capas: ninguno técnico — solo control de versiones/proceso.
- Riesgos/supuestos: detectado que el repo remoto ya tenía una rama `main` con un README inicial autogenerado por GitLab (historia no relacionada), que sigue siendo la default branch de GitLab aunque el código real vive en `master`/`entrega-*` — no se tocó, queda pendiente de decisión con Joaquín (cambiar default branch en GitLab, o mergear `main`).

### 2026-08-10 18:30 - orquestador (arranque Entrega 2, ola 1)
- Etapa: Implementacion (Entrega 2, rama `entrega-2`)
- Cambio: arrancada la Entrega 2 en la rama `entrega-2`. Antes de delegar, el orquestador escaneó código real (no solo docs) de `marihogar` y `vino-y-se-fue` para el mapa de reutilización de Ventas/AFIP/CC clientes. Hallazgo relevante: `3-arquitecto-mvc.md` afirma que "Ventas + CC clientes" reusa `marihogar`, pero la `Venta` de marihogar no tiene entidad `Cliente` ni ledger de cuenta corriente (cliente es texto libre) — la reutilización real de forma es solo `Venta`/`ItemVenta`/`PagoVenta`/`VentaService`/`VentasController`; el ledger de CC cliente se adapta en cambio del patrón `MovimientoCCProveedor` de `vino-y-se-fue` (con `ClienteId` en vez de `ProveedorId`, sin persistir saldo — se calcula on-the-fly, igual que en `vino-y-se-fue`). Delegada a `agentes-ia-implementador` la primera mitad de la Entrega 2 (Cliente + CC cliente + Venta/ItemVenta/PagoVenta + workflow Borrador→Facturada + AFIP), con las rutas exactas de los archivos de referencia ya identificadas para minimizar exploración redundante.
- Motivo: arrancar el módulo de mayor riesgo de todo el proyecto (venta editable + AFIP) primero y aislado, antes de Caja/Gastos/Entregas/Dashboard (segunda mitad de la Entrega 2, dependen de que Venta ya exista).
- Impacto en capas: Datos (Cliente, MovimientoCCCliente, Venta, ItemVenta, PagoVenta — nueva migración), Negocio (VentaWorkflowService, RecargoCuotasService, AfipService/IAfipService), Presentación (ClientesController, VentasController).
- Riesgos/supuestos: AFIP requiere CUIT real + certificado .p12 de La Platense (no disponibles todavía) — el servicio se construye con el mismo patrón de fallo controlado que `AfipService.cs` de marihogar (falla explícita y clara si no está configurado, no bloquea el resto del sistema). Corrección documental pendiente: `3-arquitecto-mvc.md` debería reflejar que el campo `Cliente.saldoCuentaCorriente` no se persiste (se calcula), y que el reuse de CC clientes es de `vino-y-se-fue`, no de `marihogar` — pendiente de ajustar esa memoria cuando se re-visite Arquitectura.

### 2026-08-11 13:20 - implementador (cierre de Entrega 2, ola 1 — Ventas/CC Clientes/AFIP)
- Etapa: Implementacion (Entrega 2, rama `entrega-2`)
- Cambio: implementada la primera mitad de la Entrega 2 sobre `C:\Sistemas\Ferreteria La Platense` (rama `entrega-2`, sin cambiar de rama). Domain: `Cliente` (sin columna de saldo), `MovimientoCCCliente`, `Venta`/`ItemVenta`/`PagoVenta` + 6 enums nuevos (`EstadoVenta` propio, distinto del de marihogar; `MedioPago`; `CondicionIVA`; `TipoMovimientoCC`; `OrigenMovimientoCC`; `TipoComprobanteAfip`). Application: DTOs + `IClienteService`/`ICuentaCorrienteClienteService`/`IRecargoCuotasService`/`IVentaWorkflowService`/`IAfipService` + extendido `IProductoService` con `BuscarParaVentaAsync`. Infrastructure: `ClienteService`, `CuentaCorrienteClienteService`, `RecargoCuotasService`, `VentaWorkflowService` (workflow completo Borrador→Facturada con validaciones de guardas, AFIP-primero-luego-persistir), `AfipService`/`AfipTokenCache` portados tal cual de marihogar. Web: `ClientesController`/`VentasController` + Views (pantalla de venta rápida con carrito editable, buscador Select2 + escaneo de código de barras reutilizando `ICodigoBarrasLookupService` de Entrega 1), nueva policy `RequireVentas`, sidebar extendido. Migración `EntregaDos_VentasCCClientesAfip` generada (Clientes/Ventas/ItemsVenta/MovimientosCCCliente/PagosVenta), no aplicada a ninguna base. Build limpio (0 errores, mismas advertencias preexistentes).
- Motivo: ejecutar la primera mitad del alcance de Entrega 2 (ver arranque en la entrada 2026-08-10 18:30) — el módulo de mayor riesgo técnico del proyecto (venta editable + integración AFIP), aislado antes de Caja/Gastos/Entregas/Dashboard.
- Impacto en capas: Domain (5 entidades + 6 enums), Application (5 interfaces + DTOs + 2 Settings + extensión de `IProductoService`), Infrastructure (6 Services nuevos + `AppDbContext`/`DependencyInjection` extendidos + extensión de `ProductoService`), Web (2 Controllers nuevos + `Program.cs`/`appsettings.json`/`_Layout.cshtml` extendidos + 9 Views nuevas). Detalle completo por archivo en `5-implementador.md`, sección "Cierre de Entrega 2 — ola 1".
- Riesgos/supuestos: AFIP sigue sin poder probarse de punta a punta (falta CUIT real + certificado `.p12` de La Platense) — comportamiento de fallo controlado ya verificado, no bloquea el resto del sistema. Documentadas 3 asunciones de negocio sin precedente exacto en `2-disenador-funcional.md` (Descuento/Recargo de ítem como monto no porcentaje; el recargo de cuotas SÍ se suma al total, a diferencia del criterio informativo de marihogar; cobertura de pagos exigida salvo que haya línea de cuenta corriente) — a confirmar con el cliente en la prueba de esta ola. Desvío menor: la columna "Comprobante" del listado de Ventas no tiene filtro de columna dedicado (resto de columnas sí cumplen la regla de `25-frontend-design-system.instructions.md`). Pendiente heredado de Entrega 1 sin resolver: hipótesis de factor de conversión fijo por producto (no bloquea Ventas, sí a Compras en Entrega 3).

### 2026-08-11 13:30 - orquestador (Entrega 2, ola 2)
- Etapa: Implementacion (Entrega 2, rama `entrega-2`)
- Cambio: cerrada la ola 1 (Cliente/CC cliente/Venta/AFIP) con build limpio verificado por el orquestador. Delegada la ola 2 (Caja, Gastos, Entregas a domicilio, Dashboard Corte 1) a `agentes-ia-implementador`, con el mapa de reutilización ya resuelto: `CajaMovimiento` adapta `MovimientoCCLocal` de `marihogar` (mismo shape Tipo/Monto/OrigenTipo+OrigenId); Gastos y Entregas reusan directo de `marihogar` (`Gasto`/`Entrega`/`EntregaIntento`); Dashboard Corte 1 reusa forma de `DashboardController`/`DashboardService` de `marihogar` (`DashboardVendedorDto.VentasHoyCantidad/Total`, `ProductoMasVendidoDto` como referencia de shape), explícitamente sin nivel 2 (salud financiera, Entrega 3).
- Motivo: cerrar el alcance completo de la Entrega 2 (61h) una vez que Venta/PagoVenta/Cliente ya existen (dependencia de esta ola).
- Impacto en capas: Datos (`CajaMovimiento`, `CierreCajaDiario`, `CierreCajaMensual`, `Gasto`, `Entrega`, `EntregaIntento`), Negocio (`CajaService`, `GastoService`, `EntregaService`, `DashboardService`; integración con `VentaWorkflowService` de la ola 1 para generar `CajaMovimiento` por cada pago confirmado), Presentación (Controllers/Views nuevos + Dashboard rediseñado en 3 niveles, mostrando solo 1 y 3 por ahora).
- Riesgos/supuestos: el concepto de "cierre" (bloqueo de un período de caja) no tiene precedente exacto en el historial — desarrollo nuevo, ya declarado en `3-arquitecto-mvc.md`. R9 (repartidor ve todas las entregas sin scoping) es una regla de negocio explícita a no romper por conveniencia de implementación.

### 2026-08-11 13:47 - implementador (cierre de Entrega 2, ola 2 — Caja/Gastos/Entregas/Dashboard Corte 1)
- Etapa: Implementacion (Entrega 2, rama `entrega-2`) — **cierra el alcance funcional completo de la Entrega 2 (61h)**.
- Cambio: implementada la segunda mitad de la Entrega 2 sobre `C:\Sistemas\Ferreteria La Platense` (rama `entrega-2`, sin cambiar de rama). Domain: `CajaMovimiento`/`CierreCajaDiario`/`CierreCajaMensual`/`Gasto`/`Entrega` + 6 enums nuevos. Application: `ICajaMovimientoService`/`IGastoService`/`IEntregaService`/`IDashboardService` + DTOs + `EntregaMarkupSettings`; extendido `IProductoService` con `ContarStockCriticoAsync`. Infrastructure: `CajaMovimientoService` (ledger + cierre diario/mensual con guarda de "no movimiento retroactivo a un dia cerrado" — pieza sin precedente exacto en el historial, confirmada por escaneo de `marihogar`/`ganaderia`), `GastoService` (transaccion explicita, contramovimiento de reversion fechado al momento de la anulacion), `EntregaService` (R9: listado completo sin scoping por repartidor), `DashboardService` (nivel 1 "estado del dia" + nivel 3 "tendencias", nivel 2 "salud financiera" explicitamente diferido a Entrega 3). Modificado `VentaWorkflowService` (ola 1): guarda de caja cerrada antes de llamar a AFIP + generacion de `CajaMovimiento` de Ingreso por cada `PagoVenta` confirmado (excepto CuentaCorriente). Web: `CajaController`/`GastosController`/`EntregasController`/`DashboardController` nuevos + boton "Programar entrega" en `Ventas/Details`, nueva policy `RequireEntregas`, sidebar extendido (Dashboard como primer link, secciones Caja/Entregas). Migracion `EntregaDos_CajaGastosEntregasDashboard` generada (`CajaMovimientos`/`CierresCajaDiarios`/`CierresCajaMensuales`/`Entregas`/`Gastos`), no aplicada a ninguna base. Build limpio (0 errores, verificado 2 veces — la segunda tras reforzar `GastoService` con transaccion explicita `BeginTransactionAsync` para evitar una ventana de inconsistencia entre el alta/anulacion del Gasto y su movimiento de Caja).
- Motivo: ejecutar la segunda mitad del alcance de Entrega 2 (ver arranque en la entrada 2026-08-11 13:30) una vez que `Venta`/`ItemVenta`/`PagoVenta`/`IVentaWorkflowService` de la ola 1 ya existian — cierra el alcance funcional completo de la Entrega 2 del plan de 3 entregas.
- Impacto en capas: Domain (5 entidades + 6 enums), Application (4 interfaces + DTOs + 1 Settings + extension de `IProductoService`), Infrastructure (4 Services nuevos + modificacion de `VentaWorkflowService`/`ProductoService` + `AppDbContext`/`DependencyInjection` extendidos), Web (4 Controllers nuevos + `Program.cs`/`appsettings.json`/`_Layout.cshtml`/`Views/Ventas/Details.cshtml` extendidos + 11 Views nuevas). Detalle completo por archivo en `5-implementador.md`, seccion "Cierre de Entrega 2 — ola 2".
- Riesgos/supuestos: interpretacion del markup de Entrega sobre `CostoBase` (no sobre el valor del producto/venta) a confirmar con el cliente; `CajaMovimiento` se genera por cada `PagoVenta` (no consolidado por Venta); cierre mensual independiente de los cierres diarios individuales; Caja/Gastos exclusivos de Administrador (Vendedor no figura en la tabla de permisos del analista para estos modulos); Dashboard sin reduccion de contenido por rol en este corte; la guarda de "dia cerrado" bloquea tanto ventas como gastos nuevos con fecha de hoy una vez cerrada la caja — comportamiento coherente con un cierre fisico real, a confirmar explicitamente con el cliente. Ninguna pregunta abierta de negocio nueva se cerro en esta ola. Pendiente: aplicar ambas migraciones de Entrega 2 a la base de desarrollo, QA funcional completo, y conseguir CUIT real + certificado `.p12` para probar AFIP (y por extension el ingreso automatico en Caja) de punta a punta. Guia de pruebas manuales completa de toda la Entrega 2 (ola 1 + ola 2) documentada en `5-implementador.md`.

### 2026-08-11 14:00 - orquestador (primer deploy real a producción — Entrega 1)
- Etapa: Implementacion (cierre real de Entrega 1)
- Cambio: primer deploy real de La Platense a producción. Joaquín confirmó desplegar **solo Entrega 1** (Entrega 2 todavía sin QA ni prueba manual — queda en su rama, sin tocar producción). Pasos ejecutados: (1) checkout de la rama `entrega-1`, build Release limpio; (2) `dotnet ef database update` con `ASPNETCORE_ENVIRONMENT=Production` contra la base real `db_a7251f_laplaten` en `mysql8001.site4now.net` (SmarterASP/site4now) — verificado por conexión directa que se crearon las tablas de Entrega 1 (Identity + Productos/Marcas/Modelos/Categorias/AjustesStock); (3) `dotnet publish` Release + deploy real vía Web Deploy (`msdeploy.exe`, perfil `olvidatasoft-002-site17` de `site17.PublishSettings`) — Joaquín pasó la contraseña de deploy puntualmente en el chat (no se guardó en ningún archivo del repo ni en memoria); 345 cambios sincronizados (343 archivos agregados, 123MB). Verificado `https://ferreterialaplatense.com.ar/` respondiendo 200 con la app real (no placeholder).
- Motivo: dar valor real al cliente con la Entrega 1 ya operable, siguiendo el plan de entregas incrementales — Entrega 2 sigue su propio ciclo de QA/mejora sin bloquear esto.
- Impacto en capas: ninguno de código — despliegue de infraestructura/operaciones sobre lo ya aprobado.
- Riesgos/supuestos: `msdeploy.exe` (Web Deploy V3) tuvo problemas de parseo de argumentos al invocarse desde PowerShell/bash directo con paths con espacios — se resolvió armando un `.bat` temporal (borrado inmediatamente después junto con el log de la migración, ambos con la contraseña real) e invocándolo vía `cmd /c`. Queda pendiente: (a) seed de `SuperUsuario` corre en el primer arranque de la app (`SeedData.InitializeAsync`) — a confirmar con Joaquín que el primer login funciona con las credenciales de `Seed:SuperUser` configuradas; (b) SMTP/email de producción configurado pero no probado end-to-end todavía; (c) sigue pendiente decidir la rama `main` vs `master`/`entrega-*` como default branch de GitLab (riesgo declarado desde el 2026-08-10).

### 2026-08-17 12:30 - orquestador / analista-funcional (arranque Análisis Etapa 3 — Migración de catálogo)
- Etapa: Analisis (Etapa 3, previamente pospuesta)
- Cambio: Joaquín trajo el segundo relevamiento prometido (backup real de SQL Server del sistema actual, 17,35GB, + 2 listas de proveedor de muestra). Se restauró el backup completo (no una muestra) en una instancia local de SQL Server 2022 Developer recién instalada (las instancias Express ya presentes tienen tope de 10GB/base, insuficiente) y se analizó el esquema y los datos reales. Hallazgos volcados en `1-analista-funcional.md` sección "Etapa 3 — Migración de catálogo": (a) el catálogo real es de 121.691 artículos activos (142.227 totales) — 7x el supuesto de "~17.000" usado hasta ahora; (b) confirmado que cada proveedor tiene su propio esquema de código sin relación entre sí — valida el diseño de `CodigoProveedorProducto`, que además el sistema actual ya implementa como tabla `Codigo`; (c) la tabla de importes histórica de proveedor (`articuloProveedor`, 58,8M filas) tiene 49% de filas sin conciliar contra un artículo real — el "barrido" que pidió Joaquín es un problema medido, no preventivo, con regla de deduplicación propuesta (última importación procesada+matcheada por proveedor+código); (d) detectados 8 gaps funcionales reales del sistema actual no cubiertos por el diseño/implementación de Entregas 1-2 (multi-moneda, oferta con vigencia, bonificación compuesta, listas de precio por forma de pago/tarjeta con nombre propio, límite de crédito en CC, campos de Cliente faltantes, categoría jerárquica con reglas de precio, doble circuito Cliente/Venta en paralelo) — pendientes de decisión con Joaquín antes de Diseño.
- Motivo: cumplir la secuencia obligatoria Discovery→Análisis antes de Diseño para esta pieza específica (Etapa 3), sin reabrir lo ya aprobado de Entregas 1/2.
- Impacto en capas: ninguno técnico todavía (etapa de Análisis, modo Ask). Impacto económico futuro: el precio provisional histórico de la migración (USD 315-394, basado en ~17.000 productos) queda obsoleto, a recalcular en `4-presupuestador.md` una vez cerrado Diseño/Arquitectura de esta etapa.
- Riesgos/supuestos: la base restaurada (`LaPlatense_MigracionAnalisis`) es solo para análisis, vive en `C:\SQLRestore\` (~17GB) en la instancia local `.\MSSQLSERVER01` (SQL Server Developer, recién instalada en esta sesión) — no es la base de producción del cliente ni se sincroniza con ella. Queda pendiente decidir si "tblVentas"/"tblClientes" (paralelos a "Operacion"/"Cliente", ambos con datos hasta la fecha actual) son dos circuitos vivos distintos o uno de los dos es descartable — no asumido, es pregunta abierta.

### 2026-08-17 12:45 - orquestador / analista-funcional (cierre de Análisis Etapa 3)
- Etapa: Analisis (Etapa 3 — cierre)
- Cambio: Joaquín resolvió los gaps planteados: (1) el recargo por forma de pago se modela como planes con nombre por programa (Ahora 12/3/6, Naranja) en vez del simple "cuotas→%" de Entrega 2 — ampliación sobre `RecargoCuotasService` ya entregado; (2) entran a Etapa 3: bonificación compuesta y campos de Cliente faltantes; (3) precio de oferta con vigencia queda documentado para el futuro, explícitamente fuera de Etapa 3; (4) multi-moneda y límite de crédito en CC quedan sin decisión (ni dentro ni fuera, a repreguntar); (5) confirmado que el circuito activo de ventas/clientes hoy es `tblClientes`/`tblVentas`/`tblDetalleVentas`, no `Cliente`/`Operacion` — cambia la fuente de verdad de la migración.
- Motivo: cerrar el Análisis de Etapa 3 antes de pasar a Diseño, según la secuencia obligatoria.
- Impacto en capas: ninguno técnico todavía. Define alcance para el Diseño/Arquitectura/Presupuesto de Etapa 3 que siguen.
- Riesgos/supuestos: queda una inconsistencia de volumen sin resolver (`OperacionVenta` 74.317 filas 2002-2026 vs `tblVentas` 4.279 filas 2022-2026 pese a que Joaquín confirmó que `tblVentas` es el circuito activo) — hipótesis de trabajo: `Operacion`/`OperacionVenta` puede registrar otros tipos de movimiento ademas de venta (hay tablas satélite `OperacionCambio`/`OperacionCaja`/`OperacionNota`/`OperacionFinanciacion` del mismo modelo). No se resolvió en esta ronda, a confirmar antes de diseñar el importador de historial de ventas/CC.

### 2026-08-17 13:00 - orquestador / analista-funcional (cierre final de gaps — Análisis Etapa 3 100% cerrado)
- Etapa: Analisis (Etapa 3 — cierre final)
- Cambio: Joaquín confirmó que multi-moneda por producto y límite de crédito en cuenta corriente **no** entran al alcance de Etapa 3 — ambos quedan documentados para una fase futura, mismo criterio que el precio de oferta con vigencia. Con esto, los 5 gaps quedan resueltos: entran (bonificación compuesta, campos de Cliente), no entran/documentados a futuro (oferta con vigencia, multi-moneda, límite de crédito).
- Motivo: cerrar completamente el Análisis de Etapa 3 antes del gate hacia Diseño.
- Impacto en capas: ninguno técnico todavía.
- Riesgos/supuestos: ninguno nuevo — ver entrada anterior (12:45) para los riesgos vigentes de esta etapa.

### 2026-08-17 13:30 - orquestador / analista-funcional (barrido de duplicados + ABC automática — Análisis Etapa 3)
- Etapa: Analisis (Etapa 3 — profundización pedida por Joaquín)
- Cambio: análisis cuantitativo real sobre los 121.691 artículos activos para el "barrido" pedido: 5.794 grupos de nombre duplicado (13.353 filas excedentes), de los cuales solo 2.181 grupos son auto-resolubles (todo inactivo o un solo activo) y **3.612 grupos (62%) tienen más de un activo con el mismo nombre — requieren revisión manual**, no es automatizable con nombre solo. 3.204 artículos con nombre vacío (3.203 de ellos marcados Activo=1, no los filtra el flag). 16.258 códigos de barra compartidos por más de un artículo. Confirmado empíricamente que el stock actual no es confiable (121.690 de 121.691 activos en 0 o negativo) — valida el plan ya diseñado en Entrega 1, no es solo una afirmación anecdótica del cliente. Para la clasificación ABC automática por ventas: hallazgo crítico de que `tblDetalleVentas.Codigo` (el circuito que Joaquín confirmó como el activo) está vacío en el 100% de sus filas — no vincula a ningún artículo; la única fuente usable es `VentaItem` (FK real a Articulo), que sigue activo hasta la misma fecha que `tblVentas`. Simulación Pareto real con `VentaItem`: histórico completo 675 "A"/3.206 "B"/11.198 "C" (solo ~12% del catálogo activo con alguna venta); últimos 12 meses solo 1.536 artículos con venta. Propuesta: ABC automática sobre ventana móvil de 12 meses, como sugerencia editable (no reemplaza la decisión previa de que el cliente clasifica por su cuenta), usado como clasificación inicial de arranque en la migración.
- Motivo: profundizar el Análisis de Etapa 3 con los dos pedidos explícitos de Joaquín (barrido de duplicados/inútiles, ABC automática por ventas) antes de pasar a Diseño.
- Impacto en capas: ninguno técnico todavía (Análisis). Anticipa impacto futuro en Negocio (`AjusteStockService`/nuevo servicio de clasificación ABC automática) y en el diseño del importador de Etapa 3 (reglas de deduplicación).
- Riesgos/supuestos: la brecha entre `tblDetalleVentas` (circuito confirmado como activo por Joaquín, pero sin vínculo a producto en los datos) y `VentaItem` (vínculo confiable, pero de un circuito que Joaquín no mencionó como el principal) sigue sin resolverse — se usó `VentaItem` por ser la única fuente técnicamente viable, no porque se haya confirmado que es "el" circuito correcto: a validar con Joaquín/personal de La Platense. Los 3.612 grupos de nombre duplicado con múltiples activos quedan como bloque de trabajo manual/semiautomático a diseñar en la etapa de Diseño (posible pantalla de revisión de duplicados durante el import), no resuelto en este análisis.

### 2026-08-17 13:45 - orquestador / analista-funcional (cierre de decisiones — barrido y circuito de ventas)
- Etapa: Analisis (Etapa 3 — cierre de esta ronda)
- Cambio: Joaquín cerró dos decisiones: (1) para los 3.612 grupos de duplicados ambiguos, regla automática sin pantalla de revisión — conservar el de venta más reciente en `VentaItem`; (2) corrigió su respuesta anterior sobre el circuito de ventas — **`VentaItem`/`Operacion` es el circuito correcto**, no `tblVentas`/`tblDetalleVentas` (coherente con el hallazgo técnico de que `tblDetalleVentas.Codigo` no vincula a ningún producto). Verificación posterior de la regla de duplicados: de los 3.612 grupos, solo 486 (13%) tienen alguna venta registrada — en el 87% restante (3.544 grupos) la regla principal no alcanza y decide el criterio de respaldo (`FechaModificacionPrecio` más reciente, propuesto, a confirmar en Diseño).
- Motivo: cerrar las últimas dos preguntas abiertas de esta ronda de Análisis antes de pasar a Diseño de Etapa 3.
- Impacto en capas: ninguno técnico todavía.
- Riesgos/supuestos: el criterio de respaldo (`FechaModificacionPrecio`) es una propuesta del analista, no una decisión explícita de Joaquín todavía — sí se le comunicó el peso real que tiene (decide el 87% de los casos, no un caso de borde) para que pueda objetarlo con esa información antes de Diseño.

### 2026-08-17 14:00 - disenador-funcional (Diseño de Etapa 3 — migración de catálogo)
- Etapa: Diseno (Etapa 3)
- Cambio: cerrado el Análisis de Etapa 3 (ver entradas anteriores del mismo día) y diseñado el flujo 10 en `2-disenador-funcional.md`: (1) extracción/limpieza batch sin UI aplicando todas las reglas de barrido ya cerradas (excluir inactivos/sin nombre/precio cero, dedup de nombre por venta más reciente→fecha de modificación, dedup de `articuloProveedor` por última importación procesada+matcheada, ABC inicial por Pareto 12 meses sobre `VentaItem`), y (2) importación con UI reutilizando el patrón preview→confirmar ya usado para listas de proveedor de Entrega 2. Diseñado también el mecanismo de clasificación ABC automática por lote (`IClasificacionAbcAutomaticaService`) como sugerencia editable que nunca sobrescribe el campo manual sin acción explícita del usuario.
- Motivo: continuar la secuencia obligatoria Análisis→Diseño para Etapa 3 antes de Arquitectura/Presupuesto.
- Impacto en capas: Presentación (ViewModels nuevos/extendidos: `ImportacionCatalogoMigracionViewModel`, `ReporteExcepcionesMigracionViewModel`, extensión de `ProductoFormViewModel`/`ClienteFormViewModel`), Negocio (`ICatalogoMigracionService`, `IClasificacionAbcAutomaticaService` nuevos).
- Riesgos/supuestos: el proceso de limpieza del paso 1 corre una sola vez sobre una copia del backup del cliente (no en vivo contra su sistema actual) — a coordinar con Joaquín el momento exacto de la extracción final (cuanto más cerca del corte a producción, menos desactualizado queda el dataset limpio). Pendiente: Arquitectura (mapeo detallado a capas/entidades EF) y Presupuesto (recalcular sobre 121.691 productos reales, no 17.000).

### 2026-08-17 14:15 - arquitecto-mvc / presupuesto-mvc (Arquitectura + Presupuesto real de Etapa 3)
- Etapa: Arquitectura → Presupuesto (Etapa 3)
- Cambio: Arquitectura de Etapa 3 cerrada en `3-arquitecto-mvc.md` (entidad `CodigoProveedorProducto`, extensión de `Producto`/`Cliente`, servicios `ICatalogoMigracionService`/`IClasificacionAbcAutomaticaService`, proceso de limpieza batch fuera del ciclo de vida de la app). Presupuesto real calculado en `4-presupuestador.md`: WBS de 7 ítems, 27h, R=18,5% → Tier 3 (0% descuento, coherente con ser ampliación sobre sistema ya entregado) → **precio final ≈ USD 567**, reemplaza la referencia provisional histórica (USD 315-394, nunca cotizada en firme).
- Motivo: continuar la secuencia obligatoria Diseño→Arquitectura→Presupuesto para Etapa 3 antes del gate de aprobación del cliente.
- Impacto en capas: Datos (`CodigoProveedorProducto`, columnas nuevas en `Producto`/`Cliente`, 1 migración EF), Negocio (2 servicios nuevos), Presentación (ViewModels y pantallas ya diseñados en Diseño).
- Riesgos/supuestos: el número sube frente a la referencia histórica pese a resolverse el riesgo de formato desconocido, por volumen real 7x mayor y alcance funcional ampliado — documentado explícitamente para que no se lea como cambio de criterio de precio. **Pendiente el gate de aprobación de Joaquín antes de iniciar Implementación de Etapa 3** (misma regla que Entregas 1/2).

### 2026-08-17 14:20 - orquestador (aprobación de Etapa 3 + housekeeping de ramas + arranque Implementación)
- Etapa: Implementacion (Etapa 3 — arranque)
- Cambio: Joaquín aprobó el presupuesto de Etapa 3 (USD 567) y pidió arrancar la implementación. Housekeeping de ramas antes de arrancar: detectado que el fix de Joaquín en `entrega-1` (commit `557f820`, `Home/Index.cshtml`) nunca se había mergeado hacia adelante — corregido (`entrega-1`→`entrega-2`→`entrega-3`, sin conflictos). Creada rama nueva `migracion-catalogo` (desde `entrega-2`, no desde `entrega-3` porque esta última está reservada para el alcance funcional "Ciclo completo: Compras/CtaCtes" y la migración es una pieza distinta que solo depende de `Producto`+`Cliente`, ya disponibles en `entrega-2`). Agregada `Migracion/` (carpeta con el backup real de 17GB + listas de proveedor) a `.gitignore` en las 5 ramas — nunca se commitea. Delegada a `agentes-ia-implementador` la implementación de los ítems 2-6 del WBS (15h) sobre `migracion-catalogo`; los ítems 1 y 7 (script de extracción contra el backup real + carga a producción) quedan como paso separado posterior.
- Motivo: cerrar el gate de aprobación del cliente y arrancar Implementación siguiendo la secuencia obligatoria del estudio.
- Impacto en capas: ninguno todavía (delegado, en curso). Housekeeping de ramas sin impacto de código (merges sin conflicto).
- Riesgos/supuestos: se le pidió al implementador crear una versión mínima de `Proveedor` (solo Nombre) como prerequisito real de `CodigoProveedorProducto` que no estaba contemplado explícitamente en la Arquitectura de esta etapa — la versión completa (CUIT, TC propio, etc.) se termina cuando se implemente el módulo de Compras funcional (alcance de la rama `entrega-3`). El formato del archivo de intercambio entre el script de extracción (paso 1, fuera de esta tarea) y el importador de la app (paso 2) lo define el implementador en su cierre — a revisar antes de escribir el script de extracción real contra el backup del cliente.

### 2026-08-17 16:45 - implementador-dotnet (cierre de los ítems de app de Etapa 3)
- Etapa: Implementacion (Etapa 3 — ítems 2 a 6 del WBS, 15h de 27h)
- Cambio: Implementados sobre `migracion-catalogo`: entidad `CodigoProveedorProducto` (índice único compuesto `(ProveedorId, CodigoDelProveedor)`), entidad `Proveedor` en **versión mínima** (prerequisito, ver riesgos), extensión de `Producto` (`Bonificacion`, `ClasificacionABCSugerida`) y de `Cliente` (`Domicilio`, `Localidad`, `Email`, `Notas`); `ICatalogoMigracionService`/`CatalogoMigracionService` (import de un `.xlsx` de 3 hojas con patrón previsualizar→confirmar, idempotente por `Codigo`/`CUIT`/`(proveedor,código)`, reporte de excepciones paginado y exportable a Excel); `IClasificacionAbcAutomaticaService`/`ClasificacionAbcAutomaticaService` (Pareto 80/95 sobre `ItemVenta` en ventana móvil configurable, escribe solo `ClasificacionABCSugerida`); `MigracionCatalogoController` + 4 vistas nuevas; botón "Recalcular clasificación ABC" en `Stock`; bloque de sugerencia + "Aceptar sugerencia" en `Productos/Edit`; los 4 campos nuevos en las vistas de `Clientes`. Migración `EntregaTres_MigracionCatalogo` generada (aditiva pura: 2 tablas + 6 columnas nullable) y **no aplicada a ninguna base**. Build limpio (`dotnet build FerreteriaLaPlatense.slnx`, 0 errores). **Formato del archivo de intercambio definido y documentado** en `5-implementador.md` — es la especificación que debe cumplir la herramienta del paso 1 (ítem 1 del WBS, todavía sin construir).
- Motivo: ejecutar el alcance aprobado de los ítems de app de Etapa 3, dejando el contrato de archivo cerrado para poder escribir después la herramienta de extracción.
- Impacto en capas: Datos (2 entidades nuevas + 6 columnas + migración EF), Negocio (3 Services nuevos; `ProductoService`/`ClienteService` extendidos para mapear los campos nuevos), Presentación (1 controller + 4 vistas nuevas; `StockController`/`ProductosController`/`ClientesController` y sus vistas extendidos; sidebar; `appsettings.json`; `site.css`). Permisos: todo lo nuevo contra `RequireAdministracion`, sin policy nueva.
- Riesgos/supuestos: (a) **`IListaPreciosProveedorImportService`, que el alcance daba por implementado en Entrega 2, no existe en el repo** — pertenece al módulo de Compras, no implementado; el contrato de `ICatalogoMigracionService` se diseñó desde cero y queda como referencia para cuando se construya aquel. (b) `Proveedor` mínimo creado como prerequisito real de `CodigoProveedorProducto` — se amplía de forma aditiva cuando se implemente Compras. (c) Tiempo de proceso con los 121.691 productos reales **sin medir**: el import corre síncrono en el request (límite de subida elevado a 200 MB, lotes de 500); mitigación operativa recomendada, aprovechando la idempotencia, partir el archivo en tandas. (d) Decisiones tomadas por el implementador a confirmar con Joaquín: productos sin venta en la ventana quedan en `C` (no null), unidades del legacy no modeladas (Litros/Pares/Escalones) caen en `Unidad` con excepción registrada, y los movimientos de cuenta corriente de clientes no se migran (arrancan en saldo 0). (e) El archivo subido queda en staging en el temp del servidor: hay que borrarlo a mano tras la migración real (contiene datos del cliente).

### 2026-08-17 17:00 - orquestador (verificación de capacidad de hosting — 500MB)
- Etapa: Implementacion (Etapa 3 — verificación previa a correr nada en producción)
- Cambio: Joaquín preguntó si ya se corrió la migración (no, ni el esquema ni los datos — el schema migration está generado sin aplicar, y el script de extracción de datos reales ni se construyó) y advirtió que la base de producción tiene tope de 500MB. Se verificó el uso actual real (0,39MB, prácticamente vacía) y se midió empíricamente (no estimado) el tamaño real de una muestra de 1.487 productos activos cargados en una tabla MySQL local con el esquema exacto de `Producto` — 297,8 bytes/fila reales, extrapolado a los 121.691 productos activos ≈ 34,6MB, más ≈11-22MB estimados de `CodigoProveedorProducto` → total migración de catálogo ≈46-67MB contra el tope de 500MB (>85% de margen libre).
- Motivo: responder con un dato medido, no una suposición, antes de decidir si hace falta upgradear el plan de hosting para poder migrar el catálogo.
- Impacto en capas: ninguno de código — verificación de infraestructura.
- Riesgos/supuestos: la migración de catálogo en sí no es un problema de capacidad. El riesgo real y distinto es el crecimiento continuo de las tablas transaccionales (Ventas/Caja/Notificaciones) con el uso diario una vez en producción — no medido en esta ronda, recomendado monitorear cada pocos meses de uso real, no es un bloqueante inmediato para Etapa 3.

### 2026-08-17 18:30 - qa-mvc (QA de Etapa 3 — migración de catálogo, rama `migracion-catalogo`)
- Etapa: QA (Etapa 3, revisión pre-merge de los ítems de app; Entregas 1/2 solo como regresión puntual)
- Cambio: ejecutado el ciclo de QA sobre los cambios sin commitear de `migracion-catalogo` — cobertura de los criterios de aceptación de Etapa 3, matriz de casos, y el catálogo cross-proyecto completo (`docs/qa/regresiones-manuales.yml`, 43 ids). Sin ejecución en caliente: la migración `EntregaTres_MigracionCatalogo` **no está aplicada a ninguna base**, así que la evidencia es lectura completa de código por capa + `dotnet build` (0 errores, 3 corridas). **Confirmados por código los 4 puntos que el alcance pidió verificar explícitamente**: (a) idempotencia sólida (claves de identidad `Codigo`/`CuitDni`/`(proveedor,código)`, `IgnoreQueryFilters()` para revivir soft-deleted, y `Stock`/`StockVerificado`/`ClasificacionABC` efectivamente nunca pisados en el upsert); (b) el matching de cliente sin CUIT matchea solo contra clientes que tampoco tengan CUIT, así que no le borra el CUIT a un homónimo; (c) la ventana ABC se calcula en UTC contra `Venta.Fecha` (que se persiste en UTC) y solo se convierte a hora Argentina para mostrar — el bug de huso que el Implementador declaró haber corregido **está realmente corregido en el código final**; (d) `ClasificacionABCSugerida` nunca pisa `ClasificacionABC` (verificado en el recálculo por lote, en el ABM de `ProductoService` y en el único camino explícito `AceptarSugerenciaAsync`). Permisos verificados controller por controller (no por el reporte del Implementador): `RequireAdministracion` a nivel de clase en `MigracionCatalogoController` y a nivel de acción en `RecalcularClasificacionAbc`/`AceptarClasificacionAbcSugerida`, cuyas clases son `RequireCatalogoConsulta` (incluye Vendedor) — el atributo por acción es imprescindible y está. Migración EF revisada línea por línea: **aditiva pura** (6 columnas nullable + 2 tablas + 3 índices, sin un solo `AlterColumn`/`DropColumn` sobre lo existente). **2 defectos corregidos con auto-fix**: D2 (`blocker`) y D1 (`major`), ver abajo.
- Motivo: gate de QA de la etapa antes de commitear/mergear, con foco explícito en idempotencia del import, cálculo ABC y permisos.
- Impacto en capas: Infrastructure (2 archivos parchados por QA). Sin cambios de esquema, sin migración EF nueva, sin lógica de negocio nueva.
- Defectos y auto-fixes: **D2 `blocker` — `CatalogoMigracionService` tenía dos `Where(coleccionLocalDeString.Contains(...))`** (`codigos.Contains(p.Codigo)` y `codigos.Contains(c.CodigoDelProveedor)`), que es exactamente el patrón catalogado en **MH-001** como no soportado por `MySql.EntityFrameworkCore` en EF Core 10 — y este proyecto usa ese provider en la versión 10.0.1, la misma donde MH-001 se reprodujo empíricamente. Lo grave es que **ambos están solo en el camino de persistir**: el preview retorna antes, así que el operador habría visto un preview impecable y el `Confirmar la importación` habría fallado con 500 (`does not have a type mapping assigned`) — el paso más caro y menos reversible, y justamente el que el Implementador marcó como la prueba más importante de la etapa. Corregido convirtiendo el `IN` de string en un `IN` de `Id` (colección de `int`, segura según la propia nota del catálogo) aprovechando los mapas `codigo→Id`/`clave→Id` que ambos métodos **ya tenían en memoria**: cero consultas extra y semántica idéntica. Se descartó a propósito el `archivos_fix` canónico de MH-001 ("traer la tabla a memoria"), inaceptable con 121.691 productos en lotes de 500. **D1 `major` — el recálculo ABC agregaba `ItemVenta` sin filtrar `Venta.Estado`**, así que las ventas en `Borrador` (carritos editables, que en este proyecto ya tienen ítems persistidos) contaban como cantidad vendida e inflaban la clase ABC sugerida; con la anulación por NC de Entrega 3, las `Anulada` contarían igual. Se detectó por incoherencia interna: `DashboardService.ObtenerProductosMasVendidos` hace la misma agregación y sí filtra `== EstadoVenta.Facturada`. Corregido con el filtro contra el conjunto explícito de estados consumados. **Catalogado el ítem nuevo `LP-001`** + sección de patrón generalizable ("Agregaciones sobre filas hijas de un documento con máquina de estados") en `32-estandares-qa-implementador.instructions.md`, y **registrada la reaparición de MH-001** en otro proyecto con la lección de que su fix canónico no escala a tablas de volumen.
- Riesgos/supuestos: **GO CONDICIONADO** al merge; **NO-GO para carga a producción**. Condiciones bloqueantes: (1) aplicar `EntregaTres_MigracionCatalogo` a la base de desarrollo — sigue sin aplicar; (2) ejecutar las pruebas manuales 1-5 de `6-qa.md`, en particular la verificación en caliente de los dos auto-fixes (confirmar el import, y recalcular ABC con una venta en Borrador). Riesgo principal: **nada de esta etapa se ejecutó nunca** — los dos defectos, uno `blocker`, salieron de revisión de código. Además: (a) los criterios de aceptación centrales de la etapa (dedup de nombre y de `articuloProveedor`) **no son validables** con lo implementado, porque dependen de la herramienta batch del ítem 1 del WBS, todavía sin construir — conviene no comunicar la Etapa 3 como "migración terminada": está el importador, no la extracción; (b) tiempo de proceso con el volumen real sigue sin medir; (c) **Entrega 2 nunca pasó por el gate de QA** y esta etapa se apoya en `Venta`/`ItemVenta`/`Cliente`; (d) observación colateral fuera de alcance: `DashboardService` usa `DateTime.Today` contra `Venta.Fecha` en UTC, la misma clase de bug de huso que el ABC sí evita — revisar en el QA pendiente de Entrega 2; (e) D3 `minor` aceptado sin corregir: un reimport sobreescribe la sugerencia ABC recién recalculada (el campo manual nunca se toca, se resuelve recalculando).

### 2026-08-17 17:30 - orquestador (corrección de enfoque — migración por script, no por app)
- Etapa: Implementacion (Etapa 3 — corrección post-QA GO)
- Cambio: Joaquín aclaró que la migración del catálogo histórico (una sola vez) la va a hacer por **script directo a la base**, no por la pantalla web de import que se acababa de implementar y pasar QA — y que esto es distinto de la futura importación de listas de precios de proveedor (recurrente, seguirá siendo por archivo vía pantalla). Se retiraron `ICatalogoMigracionService`/`CatalogoMigracionService`/`MigracionCatalogoController` y sus vistas (commiteado y QA-pasado minutos antes) — se rescataron a archivos propios los 2 tipos que `IClasificacionAbcAutomaticaService` seguía necesitando. Se conservan `Proveedor`, `CodigoProveedorProducto`, extensión de `Producto`/`Cliente`, e `IClasificacionAbcAutomaticaService` completo.
- Motivo: evitar mantener una superficie de código (Controller + Views + Service con flujo preview→confirmar) que no se va a usar nunca en producción — no tiene sentido para una carga de una sola vez.
- Impacto en capas: Presentación (baja de 1 Controller + 4 Views + 1 ViewModel + sidebar), Negocio (baja de 1 Service + su interfaz + DTOs, con 2 tipos rescatados a archivos propios). Sin impacto en Datos — la migración EF no se tocó, las entidades/columnas siguen siendo necesarias para el script real.
- Riesgos/supuestos: build limpio verificado tras la baja. El script de migración real (próximo paso) todavía no existe — es la pieza que efectivamente va a cargar los ~121.691 productos, reutilizando las entidades y reglas de deduplicación ya diseñadas pero sin pasar por la app web.

### 2026-08-17 17:10 - orquestador (script real de migración construido y corrido en dev)
- Etapa: Implementacion (Etapa 3 — migración real ejecutada por primera vez)
- Cambio: construida `tools/MigracionCatalogo` (consola de una sola corrida) y ejecutada de punta a punta contra `laplatense_dev` con los datos reales del backup. Resultado: 112.485 Productos, 128 Categorías, 85 Proveedores, 110.683 `CodigoProveedorProducto`, 2.990 Clientes, 270 excepciones documentadas. Encontrados y corregidos 3 bugs reales durante la corrida (destracking de entidades compartidas al limpiar el ChangeTracker por lotes, comparación case-sensitive de códigos donde el índice de MySQL es case-insensitive, y falta de deduplicación de `Proveedor.Nombre`/`Cliente.CuitDni` legacy) — ninguno se había detectado en el análisis/diseño previo, salieron de ejecutar contra el volumen real.
- Motivo: pedido explícito de Joaquín de armar el script y correrlo en dev, siguiendo la decisión previa de migrar por script directo en vez de por la pantalla web retirada.
- Impacto en capas: Datos (112.485 filas reales cargadas en `laplatense_dev`, base de desarrollo, no producción). Sin impacto en código de la app (el script vive fuera de `FerreteriaLaPlatense.Web`).
- Riesgos/supuestos: corrida contra dev únicamente — no se tocó producción. El backup usado es del 2026-08-14; si el corte real a producción es varios días/semanas después, conviene re-exportar un backup más nuevo y volver a correr el script antes de esa fecha (los datos de venta para la ABC inicial y el catálogo mismo pueden haber cambiado). Quedan 270 excepciones para revisión humana opcional (no bloquean, ya están resueltas con una regla automática, pero un vistazo rápido de Joaquín podría detectar algo que la regla no previó).

### 2026-08-17 20:00 - orquestador (corrección Rubro→Marca/Categoría tras revisión de Joaquín)
- Etapa: Implementacion (Etapa 3 — corrección tras primera revisión de datos migrados)
- Cambio: Joaquín, revisando el resultado en dev, detectó que "Categoria" en el sistema nuevo mostraba nombres de marca (SIBON, VIOLINI, etc.), y que la pantalla de Stock no tiene categoría asignada/visible. Investigado y confirmado: el `Rubro` legacy es jerárquico y mezcla categoría real (nivel raíz: ferretería/electricidad/sanitarios/pinturas) con marca/proveedor (nivel específico, el que realmente usa `Articulo.RubroKey`). Corregido el script de migración para separar ambos correctamente, y agregada la columna/filtro de Categoría a la pantalla de Stock (gap de Entrega 1). Re-corrida completa en dev con el resultado correcto.
- Motivo: corrección de datos + UI antes de considerar la migración lista para producción.
- Impacto en capas: Datos (script de migración, re-corrido en dev), Presentación (Stock: columna+filtro de Categoría), Negocio (`IAjusteStockService.ListarStockAsync` extendido con filtro por categoría).
- Riesgos/supuestos: quedan algunas categorías raíz residuales que también parecen brand-like (WADFOW, ITURRIA, GAMMA 2024) — limitación real de cómo el cliente organizó su propio Rubro, no resoluble por código sin que el cliente reclasifique esos casos puntuales manualmente después de la migración (el sistema nuevo permite reasignar categoría/marca por producto sin problema).

### 2026-08-17 20:45 - implementador-dotnet (rama de producción `entrega-1-migracion` — Etapa 1 + migración, aisladas de Entrega 2)
- Etapa: Implementacion (preparación del deploy a producción de Etapa 1 + Etapa 3)
- Cambio: el cliente aprobó llevar a producción **Etapa 1 + la migración de catálogo (Etapa 3)**, pero **NO la Entrega 2** (Ventas/CC clientes/AFIP/Caja/Gastos/Entregas/Dashboard), que pasó QA de código pero nunca se probó manualmente en caliente. La rama `migracion-catalogo` no servía para deployar porque se creó desde `entrega-2` (la migración necesitaba la entidad `Cliente`, nacida en Entrega 2) y arrastra toda esa entrega como ancestro. Se creó **`entrega-1-migracion` desde `entrega-1`** (commit `bdf3796`) con 2 commits encima: `b06f895` (código de app) y `8e6de67` (migración EF). Contiene `Proveedor`, `CodigoProveedorProducto`, la extensión de `Producto` (`Bonificacion`/`ClasificacionABCSugerida`), `Cliente` mínimo + `CondicionIVA`, `ProveedorService`, la parte de `ClasificacionAbcAutomaticaService` que no depende de Ventas, el fix de columna/filtro de Categoría en la pantalla de Stock (parte de `138d8a4`, gap puro de Entrega 1) y `tools/MigracionCatalogo` completo en su estado final (`229c6c1`). No contiene ningún controller, vista, servicio, entidad ni migración EF de Entrega 2 — verificado contra el `AppDbContextModelSnapshot` y el sidebar.
- Motivo: separar lo aprobado de lo no aprobado para el primer deploy a producción del catálogo migrado, sin exponer al cliente un módulo de ventas/facturación que todavía no se probó en caliente.
- Impacto en capas: Domain (3 entidades + 1 enum), Application (2 interfaces + 3 DTOs extendidos), Infrastructure (2 servicios nuevos, `AppDbContext`, `DependencyInjection`, migración EF nueva `20260817233056_EtapaTres_MigracionCatalogo` — aditiva pura: 3 tablas nuevas vacías + 2 columnas nullable en `Productos`, sin drops ni modificaciones de datos existentes), Presentación (ficha de Producto: Bonificación + bloque de sugerencia ABC; Stock: columna y filtro de Categoría). Build de la solución y del script de migración: **0 errores**.
- Riesgos/supuestos: **(1)** No se pudo hacer por `cherry-pick` — `71daf36` mezcla la extensión de `Cliente`/`ClienteService` (Entrega 2) con `Proveedor`/`CodigoProveedorProducto` (Etapa 3) en un mismo diff; se portó archivo por archivo con `git show`, aplicando el delta de Etapa 3 sobre la versión de `entrega-1` en los 8 archivos que Entrega 2 había tocado. **(2) Decisión a validar con el cliente**: `Cliente` queda como tabla y entidad, **sin ABM, sin servicio, sin pantalla y sin entrada de sidebar** — existe solo para recibir las ~3.000 fichas migradas; el script escribe directo por `DbContext`, nunca necesitó `ClienteService`. La gestión de clientes se habilita con Entrega 2. **(3) Decisión a validar**: el recálculo POR LOTE de la clasificación ABC sugerida (`RecalcularAsync` + botón "Recalcular clasificación ABC" en Stock) se retiró porque agrega `ItemVenta` sobre ventas facturadas — imposible sin el módulo de Ventas. Sin impacto en el arranque: la ABC inicial la escribe la carga de catálogo con el mismo Pareto 80/95 sobre las ventas del legacy, y sigue siendo editable a mano; se conservó "Aceptar sugerencia". Al habilitar Entrega 2 hay que restituir ese flujo desde `migracion-catalogo` y **saltear/marcar como aplicada** la creación de la tabla `Clientes` en la migración de Entrega 2 (esta rama ya la crea con su forma final). **(4)** La rama **no se mergeó a `master` ni se pusheó** — queda local para revisión y deploy del orquestador.

### 2026-08-17 21:55 - orquestador (deploy real a producción de Etapa 1 + migración)
- Etapa: Implementacion (cierre del deploy)
- Cambio: ejecutado el deploy a producción aprobado por Joaquín sobre la rama `entrega-1-migracion`. Pasos: (1) backup de seguridad de `db_a7251f_laplaten` vía `mysqldump`; (2) detectado y borrado (confirmado con Joaquín) 1 producto de smoke-test que ya existía en producción desde el 2026-08-15, más 3 filas huérfanas de catálogo (Marca/Categoría/Modelo) que le pertenecían y quedaron sin uso tras el borrado; (3) migración EF `EtapaTres_MigracionCatalogo` aplicada contra la base real y verificada por `DESCRIBE`/`SHOW TABLES`; (4) código publicado a `olvidatasoft-002-site17` vía Web Deploy (`msdeploy.exe`, reglas `AppOffline` + `DoNotDeleteRule`), sitio verificado arriba (`HTTP 200`); (5) `tools/MigracionCatalogo` corrido contra producción real (origen: backup del cliente restaurado en SQL Server local). Resultado verificado por consulta directa a la base: 112.485 Productos, 128 Marcas, 16 Categorías, 85 Proveedores, 110.683 `CodigoProveedorProducto`, 2.990 Clientes — coincide con la corrida de dev.
- Motivo: pedido explícito de Joaquín ("deployar y correr script en producción") tras aceptar las 2 decisiones de diseño de `entrega-1-migracion` (Cliente mínimo sin ABM, recálculo por lote de ABC retirado por depender de Ventas).
- Riesgos/pendientes: quedan en una carpeta temporal local (no en el repo) el backup pre-migración y el CSV de 270 excepciones de la corrida real — contienen datos del cliente, pendiente de borrarlos cuando Joaquín confirme que ya no los necesita. La password de Web Deploy de la cuenta `olvidatasoft-002` (compartida por todos los sitios de SmarterASP) quedó guardada en `docs/credenciales.local.md` (gitignored) para reutilizar en futuros deploys sin volver a pedirla.

### 2026-09-02 - orquestador (Codigo propio de Producto: placeholder vs codigo real del negocio)
- Etapa: Investigación real + Implementación directa (hallazgo del cliente sobre datos ya migrados)
- Cambio: Joaquín reportó un caso puntual (producto 148320 "SOLDADORA INVERTER DUAL", migrado con `Codigo="148320"` en vez de `"SML120-8D"`, el código real que tiene la caja de la máquina). Investigado contra el backup real: `Producto.Codigo` viene de `Articulo.Codigo` (campo aparte de la tabla `Codigo` con el discriminador Tipo P/B/I) — y ese campo está vacío/es un placeholder (igual al `ArticuloKey`) en **115.779 de 116.028 artículos activos válidos (99.8%)**. El negocio casi nunca lo completaba en el sistema legacy.
- De esos, 106.800 tienen al menos un código de proveedor (`Codigo.Tipo='P'`) real; 106.433 tienen exactamente uno (sin ambigüedad). Pero muchos de esos códigos únicos son en realidad genéricos/compartidos entre decenas de artículos distintos (ej. "ZB" en 100 artículos, "ZA" en 40) — no son identificadores reales. Filtrando a códigos de largo ≥7 caracteres y verificando unicidad real (sin colisión entre candidatos ni contra un código ya existente), el grupo seguro quedó en **46.760 productos** (sobre los ganadores finales de la migración).
- Implementado como nuevo modo correctivo `--solo-codigo-propio` en `tools/MigracionCatalogo/Program.cs` (mismo patrón que `--solo-codigo-barras`: UPDATE dirigido contra un catálogo ya migrado, sin tocar nada más). Validado en `laplatense_dev` primero (46.760 corregidos, 0 duplicados, conteo de filas intacto, ejemplo puntual confirmado exacto) y luego en producción real (mismos números, backup fresco previo de 33 MB, ejemplo puntual verificado — producto Id=90004 en prod).
- Motivo: hallazgo directo de Joaquín revisando el catálogo migrado, con pedido explícito de "evaluar hacer una migración completa de estos códigos".
- Riesgos/pendientes: quedan **75.937 productos** con código todavía puramente numérico (mezcla de códigos de proveedor cortos/ambiguos y algunos que genuinamente ya eran códigos numéricos reales) — Fase 2, decisión de negocio aparte (cómo resolver los casos ambiguos: manual, o un criterio de "proveedor principal", a definir), no incluida en esta corrección. Backup pre-fix queda en carpeta temporal local, pendiente de borrar cuando Joaquín confirme que no lo necesita.

### 2026-09-03 - orquestador (auditoría de buscadores de artículos tras el fix de código propio)
- Etapa: Auditoría (regla LP-002: cambio data-model-adjacent exige revisar todos los call-sites) + Implementación directa del hallazgo
- Cambio: pedido explícito de Joaquín tras el fix de `Producto.Codigo` del 2026-09-02 ("en los buscadores de artículos siempre se debe buscar también por el código este nuevo migrado, y también por el código de barras"). Auditados todos los métodos de búsqueda de producto del código base: `ProductoService.ListarAsync`, `AplicarBusquedaGlobalAsync` (PAT-016, ambas ramas con/sin extraIds) y `BuscarParaVentaAsync` ya cubrían `Nombre` + `Codigo` + `CodigoBarras` + `CodigosBarrasAlternos`. Único gap real encontrado: `AjusteStockService.ListarStockAsync` (buscador de la pantalla de Stock) solo filtraba por `Nombre`/`Codigo`, sin `CodigoBarras` ni alternos. Corregido con el mismo patrón ya usado en `ProductoService`.
- Motivo: pedido directo de Joaquín, consecuencia natural de que el código propio recién migrado (SML120-8D, etc.) sea buscable donde antes solo servía el código de barras.
- **Deploy real ejecutado** (sin migración EF): build 0 errores, publicado vía Web Deploy (310 archivos — build limpio completo, no incremental sobre el deploy anterior), sitio verificado `HTTP 200`.
- Riesgos/pendientes: ninguno.

### 2026-09-03 (2) - orquestador (Ventas: confirmar sin factura + 10 fixes + rediseño de formularios)
- Etapa: Implementación directa (lista de pedidos de Joaquín usando Ventas en producción) + regla nueva de Agentes-IA
- **Cambio estructural — la factura deja de ser la forma de cerrar una venta.** Nuevo estado `Confirmada` (Borrador → Confirmada → *opcional* Facturada). Confirmar es lo que hace que la venta ocurra: descuenta stock, registra Caja y Cuenta Corriente. Facturar solo agrega CAE/comprobante y no vuelve a mover nada. Esto desbloquea el módulo: con AFIP sin configurar, el botón "Confirmar y facturar" estaba deshabilitado y **no había forma de cerrar una venta**. Entregas también se ajustó (antes exigía `Facturada`, ahora acepta `Confirmada`).
- **Fórmula comercial de descuento/recargo** (bug real reportado): se aplicaban en cascada `(1-d)*(1+r)`, así que 10% de descuento + 10% de recargo daba 0,99 del precio original. Ahora los dos porcentajes se aplican sobre el precio de lista `(1-d+r)` y se cancelan exactamente. Corregido en el service y en el JS de la pantalla.
- Otros fixes de la pantalla de Venta: `step` de cantidad = 1 en unidades enteras y 0,001 solo en fraccionables (Peso/Metro); subtotal del ítem ahora es **con IVA y editable** (al editarlo se despeja el precio unitario hacia atrás — decisión de Joaquín entre las dos opciones planteadas); auto-balanceo de pagos (la última fila absorbe el resto hasta cubrir el 100%, salvo que se la edite a mano) + botón "Completar saldo"; nota libre opcional por pago (`PagoVenta.Nota`); combo de cliente centrado, con búsqueda y cargando los primeros 20 sin tipear nada.
- **Bug del "combo suelto" en el toast de guardado — causa raíz encontrada**: el auto-init global de Select2 del 2026-08-31 estaba tomando el `<select class="swal2-select">` interno de SweetAlert2 y construyéndole al lado un `.select2-container` visible que SweetAlert no sabe ocultar. Excluido en `site.js`. Segundo caso del mismo patrón: ocultar el combo de Cuotas con `$select.hide()` ya no funciona con Select2 (lo visible es el container hermano) — ahora se oculta un wrapper. Ambos quedaron documentados como comentario en `site.js`.
- **Recargos por cuotas configurables desde el menú**: nueva entidad `RecargoCuota` + pantalla Configuración → Recargos por cuotas con los planes 1/3/6/9/12/18/24 y su porcentaje editable a mano (con ejemplo en vivo sobre $100.000). Reemplaza la sección `RecargoCuotas` de `appsettings.json`, que exigía tocar un archivo y reiniciar el sitio. `IRecargoCuotasService` pasó a async; el contrato con los consumidores no cambió — exactamente la salida que ya dejaba anticipada el comentario de `RecargoCuotasSettings`.
- **Bajas lógicas fuera de los listados**: ventas anuladas y gastos anulados dejan de listarse por defecto (siguen accesibles eligiéndolos en el filtro de estado, no se borran). El soft delete por `DeletedAt` ya estaba resuelto con query filter global — el gap era el de los *estados* anulados.
- **Rediseño de formularios (21 pantallas)**: sistema de clases `.ov-form-page` / `.ov-page-head` / `.ov-form-actions` / `.ov-required` / `.ov-field-hint` / `.ov-detail-grid` en `site.css`, aplicado a todas las pantallas de alta, edición y detalle. Encabezado con título + descripción + Volver, ancho de lectura acotado, campos obligatorios marcados, textos de ayuda, botonera sticky y grillas de detalle uniformes.
- **Regla nueva documentada en Agentes-IA**: `25-frontend-design-system.instructions.md`, sección "Formularios de alta / edicion / detalle: diseño grafico obligatorio" — checklist de 10 puntos, pedido explícito de Joaquín.
- Verificado en navegador real (Chromium/playwright contra `laplatense_dev`, login real): fórmula que se cancela (1210 = 1210), subtotal editado a $500 que recalcula el precio unitario a $413,2231, auto-balanceo (200 → la otra fila pasa a 300, saldo $0), combo de cliente con 20 resultados sin tipear y foco en el buscador, **cero combos sueltos**, y el circuito completo Borrador → Confirmada verificado en la base: `Estado=4`, `CAE` NULL, subtotal 413,22 + IVA 86,78 = 500,00 exacto, 2 movimientos de Caja, nota del pago persistida y stock descontado. Las 17 pantallas de formulario responden 200 sin errores de JS ni scroll horizontal (también en 390px).
- Motivo: lista de pedidos de Joaquín tras usar el módulo de Ventas en producción, con instrucción explícita de registrar la parte de diseño como regla nueva del estudio.
- Riesgos/pendientes: **sin deployar todavía** (requiere migración EF `EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago`: tabla `RecargosCuota` + `PagosVenta.Nota`). **Hallazgo aparte para decidir con Joaquín: 87.542 de 112.485 productos (78%) quedaron migrados con `UnidadVenta = Metro`** — el mapeo del script es correcto (mapea por nombre de la unidad legacy), así que el dato viene así del sistema viejo. Es la causa real de que el input de cantidad muestre decimales en casi todo el catálogo, y probablemente amerite una corrección de datos como la de `Codigo` del 2026-09-02.

### 2026-09-03 (3) - documentador (manual de usuario final)
- Etapa: 7 - Documentación
- Entregable: `docs/la-platense/manual-usuario.md` — manual de uso para el personal de la ferretería, cubriendo TODO lo entregado hasta la fecha (Entrega 1 + Etapa 3 migración + Entrega 2 + los cambios del 2026-09-03). Pedido explícito de Joaquín.
- Se apartó del formato estándar de la etapa 7 (que produce un resumen de sprint de media página, no un manual): se conservó el envoltorio de `31-formato-documento-cliente` (encabezado de marca, voseo, primera persona singular, pie de firma, cero tecnicismos) pero la estructura es de manual — una sección por flujo, con pasos numerados y tablas de variantes. Cubre venta paso a paso, cuenta corriente, caja, entregas, catálogo y stock, gastos, configuración de recargos, dashboard, roles y una sección de "todavía no está activo".
- **Hallazgo real al verificar el manual contra el código (gap funcional, no un error de documentación): la cuenta corriente de clientes es solo de consulta.** La deuda se genera sola al confirmar una venta fiada, pero **no existe ninguna pantalla para registrar el pago del cliente ni un ajuste manual** — `RegistrarMovimientoAsync` lo llama únicamente `VentaWorkflowService`, y los orígenes `Pago`/`Ajuste` del enum no tienen camino desde la UI. Hoy el cobro del fiado se lleva por fuera del sistema. Queda declarado en el manual y es el próximo paso sugerido del documentador.
- Segunda corrección del mismo chequeo: la marca "verificado" del stock se pone sola al hacer un ajuste, no es un check que el usuario tilda — el manual decía lo contrario en el borrador.
- Motivo: pedido de Joaquín ("manual de usuario con las funcionalidades completas de la etapa entregada, para darle al usuario").
- Riesgos/pendientes: el manual declara 4 pendientes (cobro de CC, facturación AFIP sin certificado, anulación de venta confirmada, compras/proveedores/notas de crédito). El manual documenta el sistema **tal como está en la rama, no como está en producción**: los cambios del 2026-09-03 todavía no fueron deployados.

### 2026-10-05 - orquestador (plan de cierre de alcance: Entregas 3 a 6)
- Etapa: 4 - Presupuesto (secuenciacion, sin precio nuevo). Las etapas 0-3 de este alcance ya estaban cerradas desde el 2026-07-30: todos los modulos salen del WBS de Etapa 1 + Etapa 2 aprobado por el cliente.
- Entregable: `4-presupuestador.md` v8, seccion "Plan de cierre de alcance - Entregas 3 a 6". **59h M restantes, USD 0 de precio nuevo** (Etapa 1 y Etapa 2 ya cobradas dentro de los USD 1.500/1.800).
- **Estado de partida verificado contra el repo, no contra la memoria** (rama `entrega-1-migracion`, 17 controladores, 24 entidades): `Proveedor` existe solo como catalogo simple minimo de Etapa 3 (sin ABM, sin sidebar, sin CC, sin compras); `AfipService` codificado pero deshabilitado; `EstadoVenta.Anulada` existe en el enum pero **ningun codigo la dispara** (solo se usa como filtro en `VentaWorkflowService:75` y como badge en `Views/Ventas/Details.cshtml:11`) - no hay anulacion de ningun tipo. Las ramas `entrega-2`, `entrega-3` y `migracion-catalogo` no tienen ningun controlador que no este ya en `entrega-1-migracion`.
- Secuencia: **Sprint 0** (deuda abierta, 8h sin cargo: deploy pendiente de `a6a78f0`, D8, D9, correccion de `UnidadVenta`, cobro de CC de clientes) -> **E3** Proveedores + Compras (18h, cierra Etapa 1, sin gates) -> **E4** CC empleados + CC negocio (9h) -> **E6** Presupuestos PDF + aumento masivo (12h, sin dependencias, valvula de escape) -> **E5** AFIP + devoluciones/NC-ND + anulacion (12h), que se inserta en cuanto llegue el certificado del cliente en vez de bloquear la secuencia.
- **Cambio de alcance real detectado (unica pieza que se aparta del diseno aprobado):** `1-analista-funcional.md` §6.5 definia la anulacion como `Facturada`->`Anulada` disparada por una NC AFIP, "sin anulacion silenciosa sin comprobante fiscal". Ese diseno es anterior al 2026-09-03, cuando `Confirmada` paso a ser la forma normal de cerrar una venta sin factura. Hoy la mayoria de las ventas reales nunca llegan a `Facturada`, asi que el modulo 17 necesita **dos caminos** (anular `Confirmada` revirtiendo stock/caja/CC sin comprobante fiscal, y anular `Facturada` por NC). No agrega horas; cambia el diseno.
- **Criterio economico declarado:** Sprint 0 va sin cargo. D8/D9 son defectos (garantia); el cobro de CC de clientes es un gap del modulo 5 ya entregado y cobrado (una CC que no admite cobros esta incompleta, no es un modulo nuevo, no se factura como upsell); la correccion de `UnidadVenta` es consecuencia de Etapa 3 ya cobrada.
- Motivo: pedido de Joaquin ("armar un plan de desarrollo para terminar el desarrollo completo del sistema").
- Riesgos/pendientes: **3 decisiones bloqueantes antes de arrancar Sprint 0** - (1) dia de negocio de la caja para cerrar D9, (2) pregunta abierta 7 de `1-analista-funcional.md` §9 (quien anula y con que limite de tiempo), (3) regla de mapeo de `UnidadVenta` para los 87.542 productos migrados como Metro. Ninguna de las tres bloquea E3, que es el bloque mas grande: se puede arrancar en paralelo a la respuesta del cliente. Contexto de los agentes chequeado con `scripts/contexto.py presupuesto la-platense`: los 8 agentes bajo su techo, sin archivado pendiente.

### 2026-10-05 (2) - orquestador / analista-funcional (cierre de los 3 gates del plan + anclaje de reuse en marihogar)
- Etapa: 1 - Analisis (cierre de decisiones) sobre el plan de `4-presupuestador.md`. Deja el plan **sin ningun gate abierto salvo el certificado AFIP**.
- **Decision 1 — dia y mes de negocio de la caja (cierra D9).** Respuesta del cliente: la caja chica se cierra todos los dias y la caja grande el dia 1 de cada mes sobre el mes anterior. Lectura funcional: **dia de negocio = dia calendario en hora Argentina** (no hay corte nocturno: la venta de las 22:44 del 24 pertenece al 24) y **mes de negocio = mes calendario**. El fix mantiene UTC en la base pero proyecta a hora Argentina toda frontera de dia/mes. **Derivado a verificar durante el fix, no asumido:** que la guarda del cierre mensual admita cerrar un mes **anterior** al actual — si solo deja cerrar el mes en curso, el flujo real del cliente no entra.
- **Decision 2 — quien anula una venta (cierra la pregunta abierta 7, abierta desde el 2026-07-30).** La anula el **Administrador o el usuario que la creo**: un vendedor solo sus propias ventas (validando `UsuarioId`), el repartidor no anula. **Supuesto declarado:** sin limite de tiempo propio del sistema — el unico tope real es el de AFIP para la NC de una venta facturada. El cliente no definio el limite; si quiere un tope es una linea de validacion, no un cambio de diseno.
- **Decision 3 — `UnidadVenta`: el cliente respondio "no se", asi que se resolvio midiendo la base en vez de volver a preguntar.** Medido sobre `laplatense_dev` (catalogo real migrado): 87.542 `Metro` / 24.929 `Unidad` / 14 `Peso`. **La prueba de que el `METRO` del legado es su valor por defecto y no un dato real: 2.898 de los productos marcados `Metro` se llaman a si mismos "Unidad de…", "C/U…" o "x unidad"**, y la muestra aleatoria del grupo devuelve martillos demoledores, puertas plasticas, pinzas y brocas. El script de migracion no tiene ningun error — `MapearUnidad` (`tools/MigracionCatalogo/Program.cs:149`) mapea fielmente lo que el dato dice; el problema es el origen. **Regla acordada:** los 87.542 pasan en bloque a `Unidad` (default seguro, devuelve el `step` a 1 y elimina los decimales de casi todo el catalogo, que es el sintoma que origino esto) + lista de los **2.635 candidatos reales a corte por metro** (cable 804, manguera 535, cadena 534, alambre 283, soga/piola/cuerda 271, tanza 221) para que el cliente marque a mano los que corta al mostrador. Se excluyen a proposito los 4.077 de cano/tubo (se venden por barra entera) y **no se infiere la unidad por palabra clave del nombre** ("cable x 100 mt" es un rollo que se vende por unidad: adivinar meteria un error nuevo donde hoy hay uno conocido). Los 14 `Peso` tambien son sospechosos (en una ferreteria se espera granel por kilo) y se resuelven por el mismo camino, no por inferencia.
- **Anclaje de reuse confirmado por instruccion explicita de Joaquin: AFIP, NC, circuito de ventas, presupuestos, aumento masivo, proveedores, compras y pagos de compras se toman de `marihogar`** (`C:\Sistemas\marihogar`). Verificado archivo por archivo, no asumido: `ComprobanteAfipService` (incluye NC, migracion `AddNotaCreditoAfip`), `VentaService`, `PagoVentaService`, `ProveedorService`, `OrdenCompraService`, `PagoOrdenCompraService`, `EgresoPagoProveedorService`, `CCProveedorService`, `ChequeService` (echeck/diferidos), `PresupuestoService`, `AumentoMasivoPrecioService` y `CCLocalService` + `CCLocalController`. Tabla completa pieza->origen en `4-presupuestador.md` v9.
- **Hallazgo del anclaje:** la CC propia del negocio (item 4.2 del plan, Entrega 4) tiene **precedente directo** en `CCLocalService`/`CCLocalController` de `marihogar`, mejor que el `CajaService` de `ganaderia` que asumia el WBS (que la estimaba como 2h reuse + 3h nuevo). No se recotiza — las M del WBS ya estaban ancladas en `marihogar`, asi que la confirmacion valida la estimacion en vez de reducirla; el desvio se refleja en el cierre de calibracion.
- Entregables: `1-analista-funcional.md` v4 (seccion nueva "Decisiones del cliente del 2026-10-05" + pregunta abierta 7 cerrada) y `4-presupuestador.md` v9 (gates cerrados en Sprint 0 y Entrega 5 + seccion "Anclaje de reutilizacion").
- Motivo: respuestas de Joaquin a las 3 decisiones bloqueantes planteadas al presentar el plan, mas su instruccion de anclar todo el reuse en `marihogar`.
- Riesgos/pendientes: **unico gate que queda abierto en todo el plan: el certificado AFIP del cliente** (bloquea E5, no el resto). El supuesto de "sin limite de tiempo para anular" esta declarado y hay que confirmarselo al implementar 5.3. La base legada (`LaPlatense_MigracionAnalisis`, SQL Server local) **ya no existe en la maquina** — se verifico: solo quedan `ConversionDataNetABejerman` y su copia. Si la correccion de `UnidadVenta` necesitara volver al origen, hay que restaurar el `.bak` de `Migracion/` otra vez; la regla acordada no lo necesita porque opera sobre el catalogo ya migrado.

### 2026-10-05 (3) - orquestador (revision del plan contra el codigo real de marihogar)
- Etapa: 1 - Analisis / 4 - Presupuesto (reestimacion). Entregable: `4-presupuestador.md` v10.
- Origen: instruccion de Joaquin — *"quiero que la logica de venta y pagos este hecha como esta en marihogar. tambien los proveedores y compras. copiar lo mas que se pueda de ahi."* **Se leyo el codigo real de los dos proyectos antes de implementar**, entidad por entidad.
- **Hallazgo central: tomado literal, "copiar lo mas que se pueda" seria destructivo.** `marihogar` no tiene CC de clientes (ni entidad `Cliente`), no tiene IVA por linea, no tiene cantidades decimales (`VentaItem.Cantidad`, `OrdenCompraItem.Cantidad` y `Producto.StockActual` son `int`), no tiene unidades de medida ni conversion (0 hits de `UnidadMedida`/`FactorConversion`/`Bulto`) y no tiene cierre de caja. La Platense es mejor en los cinco y los cinco son requisitos reales del cliente. Lo que si aporta `marihogar` es el **ciclo de cobranza posterior al cierre de la venta** y **todo el modulo de compras**.
- **Despeja la duda principal del pedido:** el estado `Confirmada` **no choca con marihogar** — alla tampoco se exige factura para cerrar una venta (su `EstadoVenta` no tiene ningun estado "Facturada"; el comprobante es una entidad aparte que puede no existir nunca). El criterio del 2026-09-03 queda **confirmado**, no revisado.
- **2 defectos de produccion encontrados en el analisis, no por QA, verificados en el codigo por el orquestador:** **`LP-014`** cualquier usuario con `RequireVentas` puede vender a cualquier precio (`VentasController.GuardarBorrador` pasa `PrecioUnitario` del payload sin control de rol; `marihogar` tiene la puerta `esAdministrador` y aca no existe) — ya delegado a implementacion. **`LP-015`** con cualquier pago de CC presente, `ConfirmarAsync:486` desactiva la verificacion de cobertura **entera** y debita `pago.Monto` en vez del remanente: una venta de $100.000 con una linea de CC de $1 se confirma, sale el stock y $99.999 no quedan ni en caja ni en la deuda del cliente.
- **Entrega 3 reestimada: 18h -> 42,5h M (2,4x), rango 38-46.** Tres causas: (1) **el item 3.3 esta estimado contra una base de reuse que no existe** — `ICatalogoMigracionService`, declarado en el WBS como "3h reuse", **da 0 hits en los dos repos**, nunca se construyo; y `marihogar` tampoco tiene importacion de listas (su `tools\ImportarHistorico` se declara "de UNA SOLA VEZ"), asi que son ~10h con reuse cero. (2) El anclaje "marihogar M12+M13" no cubre 5 conceptos que el item 3.2 pide: conversion de unidades, impacto en el costo del producto (`RecibirAsync` **no toca** `PrecioCompra`), TC propio, % de descuento por proveedor y codigo de proveedor por producto — `CodigoProveedor`, `TipoCambio` y `Moneda` dan **0 hits** en `marihogar`. (3) Dos deudas de infra no presupuestadas: el ledger de caja no tiene `EsReversion` (hoy un gasto anulado es **indistinguible de un ingreso real**) y no existe ledger de stock ni metodo delta (`AjusteStockService` hace **SET absoluto** y fuerza `StockVerificado`).
- **Propuesta de alcance:** sacar la importacion de listas de la Entrega 3 y dejarla como entrega propia con relevamiento previo (pedir al cliente 2-3 listas mas de proveedores reales). Entrega 3 queda en 32,5h M, con un orden de port de 9 pasos donde nada toca produccion hasta el paso 5.
- **`MH-034`: `marihogar` NO lo resuelve, tiene el mismo problema.** Su `MovimientoCCLocal` no tiene `MetodoPago` ni id de cuenta, y no existe `CuentaBancaria`/`Banco`/`Conciliacion` en todo el repo: el medio de pago vive solo en el texto libre de `Descripcion`. Su modelo no es portable porque no hay solucion que portar. Si vale traer: `EsReversion` + `ObtenerNetoPosteadoAsync`, el choke point unico `EgresoPagoProveedorService` (~80 lineas de runtime; las otras ~460 son backfill one-shot), y su unica conciliacion real, que es manual y por documento (al acreditar un cheque se le pide al usuario **la fecha en que el banco debito, leida del extracto** — su medicion: la fecha del click acertaba 8 de 13, el vencimiento del cheque 1 de 13). Costo asimetrico: ~2,5h como paso 0, o un job de reconstruccion sobre texto libre despues de miles de pagos.
- **Entrega nueva de Ventas/Pagos** (no estaba en el WBS; el modulo 5 se dio por cerrado y esta en produccion): gate de precio por rol -> **`CancelarAsync`** (hoy **no existe ninguna anulacion**: `EstadoVenta.Anulada` esta en el enum pero ningun codigo la dispara, asi que un error de carga en una venta Confirmada en produccion es **irreparable**) -> `PagoVentaId`+`EsReversion`+`UsuarioId` en `CajaMovimiento` (sin `PagoVentaId` se revierte el pago equivocado cuando hay dos del mismo monto: **es el defecto MH-027 que marihogar ya sufrio en produccion**) -> saldo pendiente -> `RegistrarPagoAsync`/`EliminarPagoAsync`. Aparte, con presupuesto propio: acreditacion diferida de tarjeta y costo de cobranza.
- **Como se compone sin romper nada:** el estado de La Platense es la etapa documental y el de marihogar el grado de cobranza. **No se reemplaza un enum por el otro**: se conservan las 4 etapas y se agrega un sub-estado de cobranza derivado de Σpagos.
- **Riesgo de regresion declarado tabla por tabla.** El mas grave: `Confirmada=4` esta al final del enum **a proposito** para no reasignar enteros ya persistidos; adoptar el enum de marihogar haria que **cada venta Confirmada se lea como Cancelada**. Tambien: las lineas con `(1-d+r)` persistido, `Cantidad`/`Stock` decimales que un `int` truncaria, y `PagosVenta.Monto` (hoy base, con el recargo sumado aparte: la convencion de marihogar haria que toda conciliacion de nueva data de menos exactamente el recargo).
- Riesgo de hosting: La Platense **no tiene ni un hosted service** (0 hits de `AddHostedService`) y corre en SmarterASP; el patron de `marihogar` (hora fija 03:00 ART) depende de que el pool este vivo. Consultar con `olvidata-infra` antes de los pasos 6 y 7.
- Nota de reuse: `UnidadMedidaConversionService.ConvertirCompraAVenta` esta escrito, en DI y **nunca llamado** — Compras es el consumidor que esperaba desde que se construyo.
- Riesgos/pendientes: **8 decisiones abiertas con Joaquin**, listadas en `4-presupuestador.md` v10 (MH-034, remanente de venta fiada, modelo del CAE —barato ahora, caro para siempre tras la primera factura real—, recargo de cuotas, costo del producto en la compra, factor de conversion fijo por producto vs. por proveedor, cheques propios, y el desvio de 18h a 32,5h que es problema de margen y calendario, no de precio). Sigue pendiente el OK del deploy del Sprint 0.

### 2026-10-05 (4) - orquestador (DEPLOY REAL del Sprint 0 a produccion)
- Etapa: liberacion. **Ejecutado con autorizacion explicita de Joaquin** ("entregar Sprint 0, commit push deploy con migraciones").
- Pusheado `a6a78f0..2580f7c` (7 commits) a `origin/entrega-1-migracion` en GitLab.
- **Correccion del registro: `a6a78f0` YA ESTABA DEPLOYADO.** La memoria y la trazabilidad del 2026-09-03 decian "sin deployar todavia" y ese supuesto se arrastro hasta el plan (item 0.1 del Sprint 0). Verificado contra produccion: la migracion `EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago` ya estaba en `__EFMigrationsHistory`, `RecargosCuota` tiene sus 7 filas y hay **3 ventas en estado `Confirmada`** — un estado que no existe en el codigo viejo, asi que el codigo tambien estaba publicado y el cliente lo venia usando. **Leccion de proceso: el estado de produccion se verifica contra produccion, no contra la memoria del proyecto.**
- Secuencia ejecutada: (1) **backup** de `db_a7251f_laplaten` via `mysqldump --single-transaction` (33 MB, fuera del repo); (2) **migracion** `20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio` aplicada y confirmada en el historial — **no-op real en produccion**: se conto antes de aplicarla y las filas que matchean su predicado (hora 00:00:00.000000 exacta + `OrigenTipo IN ('Gasto','Ajuste')`) eran **0**, porque los unicos 4 movimientos de caja de produccion son de Venta; (3) **build Release** + publicacion via Web Deploy (`msdeploy -verb:sync`, `AppOffline` + `DoNotDeleteRule`, `-allowUntrusted`) — **310 archivos actualizados, exit 0**; (4) sitio verificado `HTTP 200` en `/` y en `/Account/Login`; (5) **modo correctivo `--solo-unidad-venta` corrido contra produccion real**.
- **Resultado del modo correctivo en produccion, identico a dev**: `Metro` **87.542 -> 0**, `Unidad` 24.929 -> **112.471**, `Peso` **14 sin tocar**, total **112.485 sin cambios** (nada borrado ni duplicado). CSV de **2.635 candidatos a corte por metro** generado contra los Ids **de produccion** (cable 804, manguera 535, cadena 534, alambre 276, soga/piola/cuerda 271, tanza 215) y copiado al escritorio de Joaquin para revision manual. Los Ids de dev no servian: son otros.
- **Nota sobre el CSV, para cuando se revise**: tiene ruido de las dos clases, que es exactamente por lo que la regla fue "listar y que lo marque una persona" y no inferir por palabra clave. Falsos positivos de producto que no se corta (`ABRAZADERA DE ALAMBRE 32-50 MM`) y, mas interesante, filas que no son `Metro` sino **`Peso`** (`ALAMBRE 0,9 X 5 KG (PRECIO X KILO)`). Esto refuerza la sospecha ya declarada de que los 14 productos en `Peso` son muy pocos para una ferreteria: conviene aprovechar la misma revision manual para marcar los de granel por kilo.
- Detalle de nota: el script temporal `.cmd` con la password de Web Deploy se borro inmediatamente despues del deploy, segun la regla de `docs/credenciales.local.md`. El publish se copio a una ruta sin espacios porque `msdeploy` no parsea `-source:contentPath` con espacios ni desde bash ni desde PowerShell.
- Estado de produccion post-deploy, verificado por consulta directa: 112.485 productos, 5 ventas (3 `Confirmada`, 0 `Facturada`), 4 movimientos de caja, 8 migraciones aplicadas.
- Riesgos/pendientes: **el commit `2580f7c` (LP-014 gate de precio + LP-016 IVA) se deployo sin la re-verificacion de QA** — esta "aplicado, pendiente de re-verificacion", y se subio porque son dos agujeros de seguridad abiertos en produccion y dejarlos un dia mas era peor que el riesgo del fix. **Mandarlo a QA igual, ahora contra produccion.** Queda tambien la confirmacion manual de 3 minutos de la ventana 21:00-00:00 ART (criterio 2b del lote 1), que QA no pudo cubrir por la hora real de la corrida. AFIP sigue deshabilitado a proposito.

## Historial de ajustes de alcance

### Bloques archivados (2026-10-05)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-08** — 20 bloques (2026-08-18 a 2026-08-31) → [`trazabilidad-2026-08.md`](historial/trazabilidad-2026-08.md)
- **2026-07** — 7 bloques (2026-07-30 a 2026-07-30) → [`trazabilidad-2026-07-3.md`](historial/trazabilidad-2026-07-3.md)


### Bloques archivados (2026-10-05)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-07** — 3 bloques (2026-07-30 a 2026-07-30) → [`trazabilidad-2026-07-2.md`](historial/trazabilidad-2026-07-2.md)


### Bloques archivados (2026-10-05)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-07** — 1 bloques (2026-07-30 a 2026-07-30) → [`trazabilidad-2026-07.md`](historial/trazabilidad-2026-07.md)

- 2026-07-30: se descarta el módulo "Cheques 30/60/90 días" como módulo aparte (el cliente no opera con pagos diferidos propios) — se absorbe como campo de forma de pago en Proveedores + Compras.
- 2026-07-30: mantenimiento acordado previo a este relevamiento (año 1 con Etapa 1 = PRO sin costo; desde Etapa 2 = PREMIUM USD 500/año) se mantiene sin cambios para este proyecto.
- 2026-07-30: agregado módulo "Devoluciones + Notas de crédito/débito AFIP" (Etapa 2, confirmado por el cliente: aplican devoluciones, no cambios). Migración de catálogo promovida de ítem dentro de Etapa 2 a **Etapa 3 independiente** (~17.000 productos, formato aún no recibido, precio provisional USD 315). Dashboard ampliado de 8h a 12h por pedido explícito del cliente de priorizar diseño y estructura de esa pantalla.
- 2026-07-30: agregado plan de puesta a punto de stock inicial (clasificación ABC + conteo focalizado + arranque suave + ajuste manual auditado + conteo cíclico). Stock (Etapa 1) 6h→8h. Etapa 3 12h→15h base, precio provisional USD 315→USD 394.
- 2026-07-30: agregado módulo "Código de barras — etiquetado con ticketeadora + lectura en venta" (Etapa 1, 7h). **Retirada la migración de catálogo como etapa del presupuesto** (se cotiza aparte más adelante, tras un segundo relevamiento con posible acceso a la base de datos real). Efecto combinado: el proyecto pasa de Tier 1 a Tier 2 (R bajó de 70,6% a 68,5%). Total: Etapa 1 USD 1.649 / Etapa 2 USD 597 / Total USD 2.246.
- 2026-07-30: ticketeadora confirmada como manual — módulo de código de barras simplificado a 3h (solo vinculación, sin etiquetado). Joaquín fijó el precio final de cierre en **USD 1.800** (Etapa 1 USD 1.308 / Etapa 2 USD 492), por debajo de los ≈USD 2.183 de la fórmula/política estándar, respaldado por su propio chequeo de margen (30h reales + USD 200 tokens IA → tasa efectiva ≈USD 53,3/h).
- 2026-07-30: precio final reestructurado como dos modalidades de pago del total del proyecto: **USD 1.500 en hasta 3 pagos** o **USD 1.800 en hasta 12 pagos**. Mantenimiento simplificado a un único plan PREMIUM (año 1 gratis, USD 500/año desde el año 2), reemplaza la transición PRO→PREMIUM anterior.


### Traza de corrida -- 2026-10-05 / etapa implementacion
- Reintentos: 2
- Criterios fallados: D8 (ya venia corregido en a6a78f0: verificado, no reimplementado) D9 0.4 0.5 -- los 4 aplicados, pendientes de re-verificacion de QA
- Reglas releidas: agents/implementador-dotnet.agent.md (completo) 32-estandares-qa-implementador por indice: LP-002 LP-003 MH-001 MH-020 MH-021 MH-033 MH-034 KOI-001 KOI-B01 ELV-008, 4-presupuestador#Plan-de-cierre-Sprint-0, patrones: cat_resumen + PAT-010 PAT-001 PAT-019 PAT-020
- Arranque real: 55 KB (~14k tokens)
- Nota: SPRINT 0, 4 ITEMS, UN COMMIT POR ITEM, SIN DEPLOY. LO PRIMERO QUE CAMBIO EL PLAN: el item 0.2 (D8) YA ESTABA CORREGIDO en a6a78f0, construido el 2026-09-03 y nunca deployado -- el brief describia el codigo viejo. No se reimplemento: se verifico el diff (guardarYContinuar postea el form entero a GuardarBorrador y solo sigue si result.Success, en los DOS botones) y se endurecio con la guarda de doble envio que faltaba, que era un defecto real no reportado: los dos hidden comparten name=continuar, un segundo click posteaba 'confirmar,confirmar', el switch caia en el default y el borrador se guardaba SIN cerrar la venta, en silencio -- el mismo sintoma de clase que D8. LA CAUSA RAIZ DE D9 NO ERA DateTime.Today: era que CajaMovimiento.Fecha tenia DOS SEMANTICAS EN LA MISMA COLUMNA (VentaWorkflowService y GastoService.AnularAsync escribian instante UTC; GastoService.CrearAsync y RegistrarMovimientoManualAsync escribian fecha calendario a medianoche). Sin unificar la columna primero, ser consistente era imposible. Se unifico a instante UTC siempre y el dia de negocio se DERIVA proyectando a ART; toda la conversion quedo en ArgentinaTime (PAT-010 ampliado), cero DateTime.Today/UtcNow.Date en decisiones de dia/mes y cero ConvertTimeToUtc fuera del helper (verificado por grep). Migracion SOLO DE DATOS para las filas viejas de medianoche (+3h, discriminador 00:00:00.000000 + OrigenTipo IN Gasto/Ajuste), porque leidas como UTC caian a las 21:00 del dia ANTERIOR y descuadraban dos dias. DOS HALLAZGOS QUE EL PARTE NO MENCIONABA: (1) el cierre mensual NO TENIA NINGUNA GUARDA DE PERIODO -- dejaba cerrar el mes en curso y meses futuros, no solo 'faltaba permitir el anterior' como suponia el brief; ahora anterior si, en curso no, futuro no, y CerrarDiaAsync rechaza dia futuro. (2) ArgentinaTime.Zone resolvia la zona con el id de WINDOWS unicamente: al volverse la fuente unica de TODAS las fechas, un TimeZoneNotFoundException ahi dejaba de romper una pantalla y pasaba a romper el ARRANQUE de la app (inicializador estatico); se le porto la cadena de fallback que AfipService ya tenia y AfipService ahora reusa el helper. ITEM 0.4 CORRIDO CONTRA laplatense_dev: 87.542 Metro -> 0, Unidad 24.929 -> 112.471, Peso 14 sin tocar, 2.635 candidatos a corte por metro listados a CSV sin modificarlos (coincide EXACTO con el total previsto; los per-grupo del brief sumaban 2.648 porque estaban pre-dedup). El CSV confirma por que la regla de no inferir estaba bien: entre los 'alambre' hay ABRAZADERA DE ALAMBRE y ALAMBRE 0,9 X 5 KG (PRECIO X KILO). MH-001 POR QUINTA VEZ EN EL PROYECTO Y EN VARIANTE NUEVA: Any() + EF.Functions.Like sobre string[] local revienta igual que el IN pero con OTRO mensaje (UnreachableException: A RelationalTypeMapping collection type mapping could not be found) y SIN NINGUN .Contains( en el codigo, asi que el grep canonico de la regla no lo encuentra. La encontro la EJECUCION REAL, no la revision -- documentada en 32-estandares con el barrido ampliado a (Contains|Any). ITEM 0.5: cobro (Credito en CC + Ingreso en Caja en UNA transaccion, MH-033) y ajuste (solo CC, SIN tocar caja a proposito -- un ajuste corrige la deuda, no es plata que se movio; meterlo en caja inflaria el arqueo). Origen nuevo CobroCC del ledger propagado al filtro de Caja por LP-002. Permisos POR PRECEDENTE, sin inventar: cobrar = Vendedor (es lo que ya hace al confirmar una venta, que tambien postea a Caja); ajustar = Administrador (equivale al movimiento manual de caja, que es admin-only). LP-003 no era latente aca sino inmediato: el importe arranca PRELLENADO con la deuda, asi que asp-for en es-AR habria dejado el input vacio sin mensaje. EVIDENCIA EJECUTADA, SIN NAVEGADOR: build 0 errores + comprobado que las vistas Razor SI compilan en el build (metiendo un simbolo inexistente a proposito y revirtiendo), grafo de DI validado con ValidateOnBuild+ValidateScopes, 8/8 fronteras de dia/mes (incluido el criterio de aceptacion: UTC 2026-09-25 01:44 -> dia 24; el arqueo del 24 la incluye y el del 25 no) y 24/24 del cobro/ajuste a nivel Service contra laplatense_dev, con las filas de prueba borradas al final. DISCREPANCIA DE PROCESO QUE DEJO PLANTEADA: el brief pedia verificar en NAVEGADOR real, el .agent.md se lo prohibe explicitamente al Implementador y designa el build limpio + la guia manual como evidencia de cierre. Segui el rol (el prompt lo designa fuente de verdad) y compense con evidencia ejecutada no-navegador para no entregar 'verificado por lectura de codigo', que es lo que el brief rechaza. Si se quiere el smoke por navegador, hay que cambiar la REGLA, no pedirlo por brief: si no, la contradiccion se repite cada corrida. HALLAZGO FUERA DE ALCANCE QUE NO TOQUE: DashboardService cuenta ventas solo con Estado == Facturada, y desde que Confirmada es el cierre normal (y con AFIP apagado) el Dashboard va a mostrar CERCA DE CERO en cuanto se deploye. No es ninguno de los 4 items, asi que lo deje intacto y lo escale en vez de ampliar alcance solo. REINTENTOS: 2 (el modo 0.4 reventó por MH-001 y hubo que reescribir el listado query-por-patron; un comentario inline que me quedo partiendo una expresion y rompio el build de CodigoBarrasLookupService). PAT-001 tenia pendiente_verificar: true y lo RESOLVI en la misma pasada contra C:/Sistemas/vino-y-se-fue, como pide el rol.


### Traza de corrida -- 2026-10-05 / etapa qa / lote 2
- Reintentos: 3
- Criterios fallados: LP-006, LP-007, B4b-BLOCKED
- Reglas releidas: qa-mvc.agent.md (completo), cat_resumen+LP-002/LP-003/MH-001/MH-014/MH-027/MH-033/MH-037/REG-010, 6-qa.md#D8-D9-D11
- Arranque real: 58 KB (~14k tokens)
- Nota: LOTE 2 FINANCIERO, 2 COMMITS (3b4d9fa cobro/ajuste de CC + 800db75 guarda de doble envio). GO: 7/7 criterios de la parte A y 4/4 de la parte B en PASS con evidencia observada, 1 BLOCKED por entorno, 2 defectos nuevos minor. EL SERVIDOR MCP PLAYWRIGHT NO ESTABA DISPONIBLE: se declaro y se compenso instalando Playwright en el scratchpad de QA y reusando los binarios de Chromium ya presentes en ms-playwright -- toda la evidencia es de navegador real + lectura directa de MySQL, cero 'verificado por lectura de codigo'. LO MAS CARO Y LO QUE MAS VALIO: la atomicidad del cobro no se verifica leyendo el BeginTransaction, se verifica ROMPIENDOLA -- trigger MySQL BEFORE INSERT ON CajaMovimientos con SIGNAL sobre OrigenTipo=CobroCC, el cobro fallo, no quedo ni el credito de CC ni el ingreso de caja, y el salto del AUTO_INCREMENT (5 -> 7) probo que el insert de CC se hizo y se revirtio. Trigger eliminado al cerrar. Cierre contable: SUM(Importe) Origen=Pago = SUM(Monto) OrigenTipo=CobroCC = 3095.37, 1:1 sin huerfanos. HALLAZGO DE PROCESO QUE HAY QUE RETENER: LA PREMISA DEL COMMIT 800db75 NO SE REPRODUCE. El commit dice que un segundo click posteaba continuar=confirmar,confirmar, el switch caia en el default y el borrador se guardaba sin cerrar la venta. Posteado a mano ese POST duplicado sobre un borrador confirmable, la venta QUEDA CONFIRMADA: el SimpleTypeModelBinder de ASP.NET Core toma el PRIMER valor, no la concatenacion. La guarda de reentrada es correcta y se queda (verificada en B2: 3 invocaciones con jQuery.trigger('click'), que ignora disabled, -> UN unico POST y UNA sola confirmacion), pero el defecto que decia cerrar era otro. Moraleja: un parte de defecto que describe una causa raiz hay que ejecutarlo, no aceptarlo -- vale para los del Implementador igual que para los mios. EL AGUJERO REAL DE ESA CLASE SIGUE ABIERTO -> LP-007: cualquier valor desconocido de continuar da HTTP 200, guarda el borrador y NO cierra la venta, sin ningun mensaje; la guarda que se agrego es SOLO DE CLIENTE. LP-006 (nuevo): la hora de los ledgers de CC y Caja sale en reloj de 12 HORAS SIN AM/PM -- un cobro de las 13:04 ART se muestra 01:04:22 y un movimiento de las 00:00 se muestra 12:00:00. CASI LO DESCARTE COMO ARTEFACTO DEL HEADLESS: lo verifique en chrome-headless-shell Y en el Chromium completo y da identico, asi que es real. NO es MH-014: el wire entrega 2026-10-05T13:04:22 ya en ART y SIN sufijo Z, o sea el servidor esta bien y no hay doble conversion -- es solo el formato de toLocaleString('es-AR'). Preexistente tambien en Caja. D8 CERRADO en su camino confirmar (venta 7, cantidad 1->50, pantalla 76,84 -> Total persistido 76.84, no el 1,54 viejo), pero la rama FACTURAR quedo BLOCKED POR ENTORNO: sin certificado AFIP el boton no se renderiza y no hay camino de usuario para disparar continuar=facturar. Esa es la verificacion que de verdad cierra el riesgo fiscal original, asi que hay que RE-VERIFICARLA COMO CONDICION DE HABILITAR AFIP, no despues. 6-qa.md NO TENIA el campo 'Ultima validacion de reglas cross-proyecto' (memoria v4, previa a la regla), asi que por contrato todo el catalogo contaba como a validar por primera vez -- ese barrido es del lote 1 y ESTA CORRIDA NO RECIBIO SU RESULTADO; lo declare como hueco en vez de darlo por hecho y ejecute el subconjunto que toca la superficie del lote. Campo inicializado en 2026-10-05. laplatense_dev restaurada a su linea base y verificada, con el detalle fino de que los encabezados de las ventas se recalcularon ABRIENDO EL BORRADOR Y GUARDANDOLO (logica del propio sistema), no por UPDATE a mano, porque reconstruir Subtotal/TotalIVA por SQL habria dejado totales que el sistema no genera. Repo del sistema intacto: git status --porcelain devuelve solo ?? .claude/, que ya estaba al arrancar. REINTENTOS: 3 (el MCP de playwright ausente y el fallback del executablePath de Chromium, que apunta a chrome-win64 y no a chrome-win; un selector button[type=submit] ambiguo que resolvia a un dropdown-item invisible del layout; y el hash del usuario Vendedor de prueba, que me quedo mal clonado y me hizo leer un 'AccessDenied' que en realidad era un login fallido mio -- NO un defecto de permisos del sistema, casi lo reporte como tal).


### Traza de corrida -- 2026-10-05 / etapa qa / lote 3
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna


### Traza de corrida -- 2026-10-05 / etapa qa / lote 1
- Reintentos: 3
- Criterios fallados: C2b-BLOCKED, LP-009, LP-010, LP-011, LP-012
- Reglas releidas: 32#LP-002, 32#MH-033, 32#MH-034, 32#KOI-015, 32#KOI-017, 30, 33, 39#5
- Arranque real: 52 KB (~13k tokens)
- Nota: LOTE 1 FINANCIERO, 1 COMMIT (628cb7a item 0.3 / D9 + migracion de datos). D9 CERRADO: los 5 criterios del parte original en PASS con evidencia observada, mas el criterio de arranque de la app. PERO NO-GO para cerrar el Sprint 0: el lote deja 2 defectos major nuevos, los dos en el circuito de dinero y los dos derivados del propio cambio. EL MCP DE PLAYWRIGHT NO ESTABA DISPONIBLE (ToolSearch sobre mcp__playwright__* no devuelve nada, y tampoco hay playwright-core); se declaro y se compenso con un harness HTTP en Node (cookies de Identity + antiforgery) mas assertions SQL directas -- cero 'verificado por lectura de codigo'. ERROR DE METODO QUE HAY QUE RETENER: el lote 2 de esta misma corrida SI consiguio navegador real instalando Playwright en su scratchpad y reusando los binarios de ms-playwright; yo no lo intente y me quede en HTTP. Para un lote cuyo sintoma es 'lo que ve el operador' (D18), el navegador habria sido mejor evidencia. LO QUE MAS VALIO: no probar el huso leyendo el codigo sino FORZANDO EL BORDE CON DATOS -- sembrar un CajaMovimiento en 2026-10-01 01:44 UTC (= 30/09 22:44 ART) hace observable el dia de negocio sin tocar el reloj: se lista y se filtra como 30/09, entra en el cierre de ese dia (1234.56) y entra en el mes de septiembre, y el 01/10 devuelve 0. Mismo truco para el gasto de esa noche (persiste en 2026-09-30 03:00 UTC = 00:00 ART) y los dos caen en el MISMO cierre. CONTROL DE INTEGRIDAD QUE ENCONTRO UN BUG SOLO: query que compara cada cierre guardado contra el recalculo por rango UTC del dia/mes de negocio. 4 de 5 coinciden exacto; el que no (agosto, 2500.75 de diferencia) destapo LP-009. Esa query vale como smoke permanente de cualquier modulo de caja. LP-009 (major, NUEVO): cerrado el mes, el sistema SIGUE ACEPTANDO movimientos dentro de ese mes -- la guarda de periodo cerrado es EstaCerradoAsync(dia) y solo consulta CierresCajaDiarios, nunca CierresCajaMensuales. Con 09/2026 cerrado se aceptaron un ajuste de 3333.33 y un gasto de 4444.44 fechados 15/09 y la pantalla sigue mostrando 777.77 de egresos contra 8555.54 reales. El commit agrego la mitad 'no cerrar el mes en curso' y dejo afuera la simetrica. Familia MH-035/MH-038/DN-004, y forma genericade CRM-017. LP-010 (major, NUEVO): UNIFICAR UNA SEMANTICA EN UN LUGAR LA DESUNIFICA DE TODOS LOS QUE NO SE TOCARON. CajaMovimiento.Fecha paso a dia de negocio ART y Venta.Fecha quedo cruda, asi que la Venta 8 (24/08 22:44 ART) se lista y se busca como 25/08 en Ventas y como 24/08 en Caja; el Dashboard lo muestra junto: 'Ventas de hoy 0 / 0,00' al lado de 'Caja de hoy 2.845,67'. El codigo de Ventas NO cambio: la incoherencia es nueva igual. Y su XML-doc DECLARA el criterio viejo como intencional, que es LP-008 otra vez. LP-011 (minor): GET /Caja/Mensual?anio=2026&mes=13 y ?anio=0&mes=0 dan 500 en ArgentinaTime.RangoMesUtc, y CerrarMes redirige ahi, asi que el mensaje 'Mes o anio invalido' que el commit agrego es CODIGO MUERTO -- una guarda del servicio no sirve si el controller redirige despues con los mismos valores invalidos. LP-012 (minor): los 2 listados de cierres dibujan el buscador de DataTables y el server ignora search[value] (familia MH-015/MH-018/ELV-006). LO QUE NO SE PUDO OBSERVAR Y SE DECLARO: la ventana 21:00-00:00 ART del criterio 2. A las 12:51 ART de la corrida DateTime.Today, UtcNow.Date y ArgentinaTime.Hoy valen lo mismo, asi que el entorno NO PUEDE distinguirlos. Las 3 formas de forzarlo se descartaron a proposito: reloj del sistema (hay agentes commiteando en paralelo, un reloj corrido les corrompe los timestamps), tzutil a Pacifico (no produce divergencia de FECHA a esa hora: PST y ART caen el mismo dia) y contenedor Linux con TZ (no hay Docker). Cobertura alternativa: barrido mecanico con CERO DateTime.Today / UtcNow.Date / DateTime.Now / ToLocalTime en una decision de dia/mes en toda la app web, y ninguna ConvertTime*Utc fuera del helper salvo los 2 call sites fiscales de AFIP. Queda prueba manual de 3 minutos escrita en 6-qa.md. MIGRACION DE DATOS INTEGRA: las 4 filas viejas a medianoche quedaron en 03:00 UTC (= 00:00 ART del mismo dia) y 0 filas sin normalizar. AISLAMIENTO: al abrir laplatense_dev aparecio una fila CobroCC creada a las 15:56 UTC DURANTE la corrida y un usuario admin.qa de las 15:52 -- OTRO LOTE DE QA ESCRIBIENDO LA MISMA BASE EN PARALELO. Se clono a laplatense_qa_d9 y se probo contra la copia; laplatense_dev no se uso para probar. PARA LA PROXIMA CORRIDA POR LOTES: UN CLON DE BASE POR LOTE, no compartir laplatense_dev. MH-034 confirmado como riesgo de diseno (un gasto por transferencia cae en el MISMO ledger que el efectivo) y MH-033 como riesgo futuro (cuando entren Compras, los pagos a proveedores tienen que postear en caja); los dos escalados al analista, no son defectos de D9. REINTENTOS: 3 (el 307 de HttpsRedirection con la app bindeada solo a http, que obligo a rebindear con ASPNETCORE_HTTPS_PORT; dos heredocs de bash que se comieron los backslashes de los regex y hubo que pasar los scripts por Write; y la contaminacion de la base, que invalido la primera tanda de totales y obligo a clonar y rehacerla).


### Traza de corrida -- 2026-10-05 / etapa implementacion
- Reintentos: 1
- Criterios fallados: LP-006, LP-007, LP-008, LP-009, LP-010, LP-011, LP-012
- Reglas releidas: 39#3, PAT-016, MH-001
- Nota: Ronda de fixes de QA del Sprint 0: 7 defectos aplicados en 1 commit (00f7dd4), sin migracion EF. Reintento 1: el script de reemplazo masivo en vistas agrego BOM a 5 .cshtml que no lo tenian, hubo que normalizar y rebuildear. Barrido LP-002 sobre las 15 propiedades DateTime de Domain: 3 hallazgos propios ademas de Venta.Fecha (AjusteStock.Fecha, Entrega.FechaEntregada, ApplicationUser.CreatedAt). MH-001 era el riesgo real de LP-012 (columna de texto en AspNetUsers sin navegacion): resuelto con subconsulta correlacionada y traduccion a SQL verificada con ToQueryString, sin levantar la app.


### Traza de corrida -- 2026-10-05 / etapa qa
- Reintentos: 2
- Criterios fallados: LP-013
- Reglas releidas: 32#LP-002, 32#MH-001, 30, 33
- Arranque real: 34 KB (~8k tokens)
- Nota: RE-VERIFICACION del commit 00f7dd4 (ronda de fixes de los 7 defectos del Sprint 0). GO: los 7 (LP-006..LP-012) CERRADOS con evidencia observada, incluidos los 2 major del circuito de dinero que habian dejado el lote 1 en NO-GO. 1 hallazgo minor nuevo: LP-013. Build 0 errores y 'has-pending-model-changes' -> sin cambios de modelo, verificado por mi y no tomado del parte. ESTA VEZ SI HUBO NAVEGADOR REAL, corrigiendo el error de metodo del lote 1: me quede en HTTP cuando el lote 2 de la misma corrida ya habia demostrado que se podia instalar playwright-core en el scratchpad y reusar el Chromium de ms-playwright. Lo hice (chromium-1243/chrome-win64, locale es-AR, timezone America/Argentina/Buenos_Aires) y ES LO UNICO QUE PERMITIO CERRAR LP-006: el reloj de 12 horas sin AM/PM es inverificable por HTTP, hay que ver el render. window.Fmt probado en el navegador: 00:00:00 -> '05/10/2026, 00:00' (antes 12:00:00), 13:04:22 -> '13:04' (antes 01:04:22), null/''/'no-es-fecha' -> string vacio y nunca 'Invalid Date'. LP-009 cerrado en 6/6 VIAS, no solo la que yo habia reportado, cada una rechazada con el mensaje del cierre MENSUAL y sin persistir nada, mas 3 controles positivos. LA SIEMBRA QUE LO HIZO POSIBLE: la rama mensual de la guarda es INALCANZABLE desde la UI para las vias que imputan a 'hoy', porque CerrarMesAsync prohibe cerrar el mes en curso -- sembre un CierreCajaMensual de 10/2026 en la base, probe venta-confirmada y gasto-anulacion, y lo borre. Sin esa siembra las 2 vias mas importantes quedaban en 'verificado por lectura'. RegistrarAjusteAsync queda afuera VERIFICADO Y NO ASUMIDO: el ajuste de CC con fecha dentro del mes cerrado se acepta y NO aparece ninguna fila nueva en CajaMovimientos. LO QUE MAS VALIO Y NO ESTABA EN EL PARTE: buscar el bug que el PROPIO FIX podia introducir. MapearDetalle ahora proyecta Fecha = ArgentinaTime.From(venta.Fecha), ese DTO alimenta VentaEditableViewModel.Fecha y la pantalla de Editar lo postea de vuelta: si GuardarBorrador escribiera ese valor, CADA GUARDADO CORRERIA LA VENTA 3 HORAS. Probado y no deducido: 5 guardados consecutivos dejan Fecha intacta. Un fix de proyeccion de fechas hay que probarlo en el camino de ESCRITURA, no solo en el de lectura. BARRIDO LP-002 VERIFICADO POR MI CUENTA y no por la tabla del implementador (la regla ya habia fallado 2 veces en el sprint): Domain/Entities tiene 22 propiedades DateTime, no 15; clasificadas una por una, con el caso nocturno real Entregas/Details/3 (2026-08-25 02:00 UTC -> 'ENTREGADA EL 24/08/2026 23:00') visto en pantalla. 3 barridos mecanicos limpios. MH-001 (6ta aparicion potencial) cubierto POR EJECUCION, que es justo lo que el implementador no hizo (verifico solo con ToQueryString(), sin levantar la app): 123 llamadas a los 6 listados x 19 terminos, incluidos ', %, _, a%b y '; DROP TABLE x;-- -> 0 no-JSON, 0 HTTP 500. CRITERIO 2b (ventana 21:00-00:00) DECLARADO CUBIERTO con el razonamiento a la vista: no es PASS por lectura de codigo, son 7 superficies con instantes nocturnos REALES vistas en pantalla atribuyendo al dia argentino correcto + los barridos que no dejan otra forma de derivar un dia + guarda e imputacion desde la misma funcion. Queda confirmacion post-deploy de 3 minutos, no bloqueante. LP-013 (minor, nuevo): la guarda protege hacia adelante pero NO REPARA EL PASADO y no hay migracion de datos, asi que los cierres mensuales que ya quedaron desfasados siguen mostrando el total viejo sin ningun aviso y no existe accion de reabrir/recalcular/anular. Entregable: query de deteccion (JOIN por rango UTC del mes WHERE m.CreatedAt > cm.FechaCierre) PARA CORRER SOBRE PRODUCCION ANTES DEL DEPLOY; en el fixture da 3 filas. TRES FALSOS POSITIVOS MIOS QUE CASI REPORTE: la grilla de cierres mensuales 'sin filas' era mi selector (#tablaMensuales vs #tablaCierresMensuales), el Dashboard 'en blanco' era que rotula ESTADO DEL DIA en mayusculas y mi probe buscaba 'Estado del d', y la CC del cliente 2544 con 1 de 3 movimientos era correcta (los otros 2 son del cliente 3). Antes de escribir un parte, confirmar que el sintoma no es del instrumento. Smoke de 24 pantallas en navegador: 24/24 HTTP 200 y CERO pageerror/console.error. REINTENTOS: 2 (otra vez los heredocs de bash comiendose los backslashes de las rutas de Windows y de los regex -- ya van 4 en la corrida, los scripts van por Write y listo; y el Stock/Historial que parecia vacio hasta que note que la accion exige ?productoId=).


### Traza de corrida -- 2026-10-05 / etapa implementacion
- Reintentos: 3
- Criterios fallados: ninguno
- Reglas releidas: 32#LP-002, 32#MH-001, 32#LP-003, agents#implementador-dotnet
- Nota: Gate de precio por rol en Ventas (un solo defecto): cualquier usuario con RequireVentas podia vender a cualquier precio porque GuardarBorrador tomaba PrecioUnitario/Descuento/Recargo del formulario y el Service los persistia sin control de rol. Copiado el criterio de marihogar CR-22 (VentaService.ConfirmarAsync/EditarAsync, ya en produccion): esAdministrador resuelto SOLO en el Controller con User.IsInRole y pasado al Service como dato explicito del DTO (init, no bindeable), unica puerta que habilita leer esos campos del payload. Para Vendedor y cualquier otro rol/caller el precio sale de PrecioDeVentaVigente (PrecioOferta si EsOfertaVigente(ArgentinaTime.Hoy) y > 0, si no PrecioVenta) y descuento/recargo quedan en 0, descartados EN SILENCIO y no con error. Esa resolucion es la MISMA que ya hacia la pantalla (producto.precioOferta || producto.precioVenta) y los dos caminos de la UI -- buscador Select2 y lector de codigo de barras -- coinciden, asi que no hubo que elegir ninguno a dedo; el > 0 replica el || de JS, sin el el servidor cobraria 0 donde la pantalla mostro el precio de lista. NO se trajo de marihogar la cascada (1-d)*(1+r) (el bug corregido el 2026-09-03) ni su manejo de subtotal. BARRIDO LP-002 en 5 pasadas con 2 HALLAZGOS PROPIOS: (1) el input de subtotal c/IVA no tiene atributo name, no se postea nunca y la UI lo despeja sobre PrecioUnitario client-side, asi que el gate del precio lo cubre por elevacion y un segundo control habria sido codigo muerto; (2) patron de LP-008 otra vez -- ItemVenta declaraba la formula en CASCADA en dos lugares (encabezado de clase y doc de Subtotal) cuando la real desde el 2026-09-03 es (1 - d/100 + r/100): una regla de negocio FALSA viviendo en el repo, corregida en la misma pasada. Mitad simetrica decidida a conciencia y verificada: un Vendedor que re-guarda un borrador pisa el override del administrador (falla segura; conservar el valor persistido seria un agujero). Vistas: readonly y NO disabled por rol en Razor y en el JS, porque un input disabled no se postea y rompe los indices contiguos que exige el model binder de List<T>. MH-001 sin riesgo nuevo (la unica coleccion local es productoIds, List<int>, que la regla declara segura). Sin migracion EF. EVIDENCIA EJECUTADA SIN NAVEGADOR: build 0 errores (9 advertencias preexistentes); prueba de que las vistas Razor SI compilan (simbolo inexistente -> CS0103, revertido); render del atributo booleano readonly verificado EJECUTANDO las tres llamadas que emite Razor (confirmadas en Editar_cshtml.g.cs con EmitCompilerGeneratedFiles) -- true emite readonly=readonly y false OMITE el atributo, que importa porque readonly= vacio seria verdadero en HTML; y el Service ejercitado DIRECTO contra laplatense_dev con los dos roles en una transaccion revertida, 15 checks OK y 0 filas sobrevivientes. DEUDA ABIERTA explicita para Joaquin: Items[].PorcentajeIVA sigue llegando del cliente para cualquier rol (postearlo en 0 baja el total ~21%), excluido a proposito por el brief. Patron nuevo PAT-050 agregado al catalogo (el criterio ya vive en 2 proyectos y no estaba). Produccion y laplatense_qa_d9 sin tocar. Pendiente de re-verificacion de QA.

