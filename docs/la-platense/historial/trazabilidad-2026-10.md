<!-- Archivado de docs/la-platense/trazabilidad.md el 2026-10-06 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-10 (19 bloques archivados)

- 2026-10-05 23:30 - implementador-dotnet (Entrega 6: presupuestos en PDF + aumento masivo de precios)
- 2026-10-05 22:55 - implementador-dotnet (Entrega 3, ítem 4c: moneda y cotización + paso 6: pagos programados)
- 2026-10-05 21:50 - implementador-dotnet (Entrega 3, pasos 4 y 5: recepción de mercadería + pagos a proveedores)
- 2026-10-05 20:30 - implementador-dotnet (Entrega 3, pasos 1 a 3: Proveedores + CC de proveedores + Ordenes de compra)
- 2026-10-05 15:45 - implementador-dotnet (Sprint 0, gate de precio por rol en Ventas)
- 2026-10-05 14:40 - qa-mvc (QA Sprint 0, RE-VERIFICACION de los 7 defectos — commit `00f7dd4`)
- 2026-10-05 13:59 - implementador-dotnet (Sprint 0, ronda de fixes de QA: cierre de los 7 defectos abiertos)
- 2026-10-05 12:30 - implementador-dotnet
- 2026-10-05 13:05 - qa-mvc (QA Sprint 0, LOTE 3 — correccion de `UnidadVenta` + Dashboard/ABC con ventas Confirmadas)
- 2026-10-05 13:10 - qa-mvc (QA Sprint 0, LOTE 2 — cobro/ajuste de CC + D8)
- 2026-10-05 12:35 - implementador-dotnet
- 2026-10-05 - orquestador (plan de cierre de alcance: Entregas 3 a 6)
- 2026-10-05 (2) - orquestador / analista-funcional (cierre de los 3 gates del plan + anclaje de reuse en marihogar)
- 2026-10-05 (3) - orquestador (revision del plan contra el codigo real de marihogar)
- 2026-10-05 (4) - orquestador (DEPLOY REAL del Sprint 0 a produccion)
- 2026-10-05 (5) - implementador (fundacion del ledger de caja + anulacion de venta confirmada)
- 2026-10-06 - orquestador (borrado de datos de prueba de produccion + cierre de 2 decisiones)
- 2026-10-06 - implementador (ronda de atomicidad y concurrencia: la familia del LP-018)
- 2026-10-06 (2) - orquestador (HOTFIX de transacciones publicado a produccion)

---

### 2026-10-05 23:30 - implementador-dotnet (Entrega 6: presupuestos en PDF + aumento masivo de precios)

- Etapa: Implementación. Rama `entrega-1-migracion`, repo `C:\Sistemas\Ferreteria La Platense`.
  Base de trabajo `laplatense_dev`. **Producción no se tocó**: ni deploy, ni Web Deploy, ni ninguna
  operación contra `mysql8001.site4now.net`. **Sin push.** El fixture de QA `laplatense_qa_d9` no se
  leyó ni se modificó. Pedido explícito de Joaquín: "no publicar, dejar el desarrollo listo".
  Producción sigue 4 migraciones atrás (5 con esta).
- **El reuse de `marihogar` rindió en la ESTRUCTURA y no en la ARITMÉTICA, y confundir las dos cosas
  era el riesgo real de la ronda.** Se copiaron la máquina de estados, el estado derivado calculado
  al leer y nunca persistido por un job, el `previsualizar → confirmar` y el patrón de PDF con
  QuestPDF (ya en el repo vía `ExportService` — **no se agregó ninguna librería**). Hubo que
  reescribir: cantidad `int` → `decimal(18,3)`, unidad de venta congelada en la línea (`PAT-052`),
  **IVA por línea discriminado por alícuota** (marihogar tiene el 21% hardcodeado en dos precios
  fijos por producto), la fórmula comercial no-cascada en lugar de `base*(1-d)*(1+r)` —que es
  **exactamente el bug corregido acá el 2026-09-03**— y el **gate de precio por rol**
  (`PAT-050`/`LP-014`/`LP-016`), que allá no existe: un presupuesto que aceptara precios del
  navegador reabría por una puerta nueva el agujero cerrado el 2026-10-05.
- **`PAT-004` declarado NO APLICABLE con verificación, no por supuesto:** ninguna entidad de La
  Platense tiene `RowVersion` (se revisó todo `Domain/Entities` y la configuración Fluent). La
  concurrencia optimista se resolvió con `SoftDestroyable.UpdatedAt`, que es el mecanismo que el
  proyecto **ya** usa (`AppDbContext.StampSoftDestroyable` lo escribe en UTC en toda entidad
  modificada), sin inventar un tercer mecanismo. El preview devuelve su instante y el aplicar
  **rechaza fila por fila** toda la que tenga `UpdatedAt` posterior, contándolas aparte en vez de
  abortar: con decenas de miles de productos en juego, tirar todo porque alguien editó uno deja la
  pantalla inusable.
- **Guarda de universo además de la de fila, porque `UpdatedAt` no ve todo.** Las altas, las bajas y
  los productos que cambian de categoría/marca/proveedor **salen o entran** del filtro, no quedan
  "modificados" dentro de él. El aplicar recuenta y rechaza la corrida completa si el total no
  coincide con el que el preview informó (medido: recuento mentido en +7 → rechazo nombrando los dos
  números).
- **`ExecuteUpdateAsync` se descartó a propósito**, aunque es una sola sentencia SQL y mucho más
  rápido: no dispara `SaveChanges`, así que **no estampa `UpdatedAt`** y el próximo aumento masivo se
  quedaría sin la marca que usa para la concurrencia. Se eligió la versión más lenta y consistente:
  lotes de 2.000 entidades trackeadas, un `SaveChanges` por lote y `ChangeTracker.Clear()` entre
  lotes (sin eso `DetectChanges` se vuelve cuadrático sobre 112.485 filas).
- **La conversión presupuesto → venta cambió de lugar respecto del precedente, y es una mejora.** En
  marihogar el botón navega a Ventas con los ítems precargados y la transición a `Convertido` espera
  a que la venta se confirme, porque allá la Venta se crea completa en una transacción y no hay
  estado editable intermedio; el riesgo que evitaba era dejar un presupuesto `Convertido` sin Venta
  detrás. Acá la Venta **nace en `Borrador`**, que es justo el "carrito precargado" que marihogar
  tenía que simular, así que `ConvertirAVentaAsync` crea la venta y marca el presupuesto en la
  **misma transacción** y el riesgo desaparece.
- **El punto de la entrega en el aumento masivo: dos palancas, no una.** Allá el aumento ajusta
  `PrecioEfectivo`, un precio de venta editable a mano. Acá el precio de venta es **derivado**
  (`costo × (1 + rec/100) ÷ (1 + IVA/100)`), así que "aumentar los precios" son dos cosas distintas:
  `RecalcularDesdeCosto` (reaplica el margen que el producto ya tiene; es el modo que **apaga**
  `PrecioVentaDesactualizado` — la mitad que le faltaba a `PAT-054`) y `CambiarRecargo` (escribe una
  política nueva y recalcula en consecuencia). En los dos el precio sale de la misma fórmula, así que
  el catálogo nunca queda con un `PrecioVenta` que no se corresponda con su `PorcentajeRecargo`
  (verificado sobre 2.000 filas: 0 inconsistencias).
- **Dos defectos propios, encontrados EJECUTANDO y no leyendo.** (1) El preview mostraba el precio
  nuevo **sin redondear** (`26254,014876033058` contra el `26254,02` que escribía el aplicar): la
  vista previa prometía un precio distinto del que se persiste, que es precisamente lo que el patrón
  de dos pasos existe para evitar. `Math.Round` con `MidpointRounding` no se traduce a SQL, así que
  se redondea en memoria sobre la página de muestra. (2) La variación porcentual del preview estaba
  **secuestrada por tres filas basura** del catálogo migrado —tres productos con `PrecioCompra` de
  6,3 billones, preexistentes, verificados contra el `mysqldump` de la tabla antes de la primera
  corrida—: aportan el 99,99% de la suma, así que la variación promedio ponderada daba **0,00%
  mientras 112.000 productos cambiaban de precio**. Se reemplazó por contadores **sube / baja /
  igual**, inmunes a outliers.
- **Tercera exclusión, no pedida pero necesaria:** 37 productos con `PrecioCompra` negativo y 1 en
  cero. La fórmula es fiel y por eso los convertía en un **precio de venta negativo** (medido:
  `T78501500`, costo −3,64 y recargo 33% → −4,00). Un precio de venta negativo es peor que un costo
  mal cargado: el costo lo ve solo el administrador, el precio lo ve el mostrador y lo cobra la
  venta. Se excluyen en los dos modos y se informan en el preview, pero **no se corrigen desde acá**:
  arreglar esos 38 es una decisión del cliente sobre su catálogo.
- **Criterio tomado con las ofertas vigentes (el criterio 5 pedía decidirlo): excluirlas por
  defecto**, con contador en el preview, badge por fila y checkbox explícito para incluirlas. El
  motivo no es prudencia genérica: con una oferta vigente lo que se cobra en el mostrador es
  `PrecioOferta`, así que mover el `PrecioVenta` de esos productos **no cambia nada hoy y cambia todo
  el día que la oferta vence** — un aumento que entra en vigencia solo, en una fecha futura, sin que
  nadie lo haya pedido ese día. Si se incluyen, se recalcula el precio de lista y **la oferta no se
  toca**.
- **Auditoría: entidad propia, no `AuditLog`.** Esa tabla no existe en este proyecto (se eliminó por
  pedido explícito del cliente el 2026-07-28), así que se siguió el precedente real de La Platense
  para "cambio masivo auditado", que es `AjusteStock`: columnas tipadas y no JSON. **Una fila por
  corrida**, con la consecuencia declarada: no alcanza para deshacer producto por producto, y
  deshacer no está en el alcance.
- **Separación `Observaciones` / `NotaInterna` en el presupuesto, dos campos y no uno a propósito:**
  el PDF imprime solo el primero. Con un único campo libre, cualquier anotación de margen o de costo
  termina impresa en la cotización que se le manda al cliente (criterio 7).
- **El barrido `LP-002` rindió 7 hallazgos** (radio: todo lector/escritor de `PrecioVenta`,
  `PorcentajeRecargo`, `PrecioOferta`, `PrecioVentaDesactualizado` y `FechaUltimoCostoCompra`). El
  `LP-008` es el **cuarto del proyecto**: el XML-doc de clase de `VentaWorkflowService` seguía
  declarando como asunción vigente que descuento y recargo eran **importes monetarios** —falso desde
  el 2026-08-21— con la fórmula correcta tres líneas más abajo en la misma clase. También:
  `ProductoService.UpdateAsync` era el **único** que apagaba `PrecioVentaDesactualizado` (sin
  apagador por lote el cliente tenía que abrir 112.485 fichas de a una); `PorcentajeRecargo` tiene
  **un solo lector funcional** en toda la app, que es la razón de que `CambiarRecargo` recalcule el
  precio **siempre** y no opcionalmente; la regla de la oferta vigente está escrita en **cuatro**
  lugares (ahora seis) y queda declarada como pendiente de unificación porque extraerla toca Ventas,
  que está en producción; y la columna "Venta" del listado nuevo era `orderable` **sin rama de
  ordenamiento** en el Service, o sea un click que no hacía nada y sin forma de que el usuario lo
  supiera.
- **`MH-001` cubierto por EJECUCIÓN**, con dos sondas EF desechables en el scratchpad contra
  `laplatense_dev`: las 6 combinaciones de filtro del aumento masivo **incluidas las que devuelven 0
  filas** (que es donde la regla revienta) y las 10 ramas del buscador global. Cero colecciones
  locales de `string` en el código nuevo: los filtros de catálogo son comparaciones por Id
  **escalar** a propósito —la pantalla elige *una* categoría y no una lista, precisamente porque un
  `IN` sobre colección local era el candidato obvio a la séptima aparición— y los dos `IN` que hay
  son de `int`. El filtro por proveedor es un `EXISTS` correlacionado sobre
  `CodigoProveedorProducto`, no un `IN`.
- **Hallazgo técnico que conviene retener:** la regla de la oferta vigente tuvo que escribirse como
  `Expression<Func<Producto,bool>>` y **no** como método `static bool`, porque un método compila
  igual y **revienta en runtime** contra MySQL — la misma razón por la que `Producto.EsOfertaVigente`
  ya estaba escrita inline en `ProductoService`.
- **Tiempos medidos sobre el catálogo real (112.485 productos), que es el criterio 7:** preview con
  filtro vacío **464 ms** en caliente (1,0–2,2 s en frío) sobre 112.022 productos; por categoría
  527 ms–1,1 s; por proveedor (`EXISTS` sobre 110.683 mapeos) 465 ms–2,5 s; **aplicar** por categoría
  **10,4 s** sobre 62.657; **aplicar todo el catálogo 7,6–8,0 s** sobre 112.054; PDF 585 ms. El
  preview está muy por debajo de lo que necesita una pantalla interactiva, y el aplicar es un batch
  aceptable que la pantalla **informa** (el mensaje de éxito trae la duración medida server-side). No
  hizo falta background ni paginar el aplicar más allá de los lotes.
- **Evidencia sin smoke test funcional:** build de la solución **0 errores** (4 advertencias
  `NU1902` preexistentes); `node --check` sobre el JS embebido de las 4 vistas nuevas **más
  `Ventas/Editar.cshtml` como control** —vista preexistente en producción, usada para validar el
  extractor: las dos primeras corridas dieron FALLA en las dos, y eso probó que el defecto estaba en
  el script y no en las vistas—, 5/5 OK; y las dos sondas con la tabla `Productos` respaldada por
  `mysqldump` antes y restaurada después, dejando la base en su línea base exacta (112.485 productos,
  0 presupuestos, 0 corridas de aumento).
- **Contexto que QA necesita:** `laplatense_dev` tiene **0 productos** con
  `PrecioVentaDesactualizado`, porque ninguna recepción corrió ahí. El filtro "solo desactualizados"
  **no tiene ni un dato real que lo ejercite** — se midió sembrando 100 banderas a mano, y para
  probarlo de punta a punta hay que recibir una compra primero.
- **Aviso para el cliente antes del primer uso:** su primera corrida de "recalcular desde el costo"
  sobre todo el catálogo va a reportar **~29.600 cambios**, porque ese número de productos migrados
  tiene hoy un `PrecioVenta` que no coincide con su propia fórmula por centavos. Es inocuo en
  importe, pero mejor que no lo sorprenda.
- **Cinco decisiones para Joaquín, ninguna bloquea el desarrollo.** (1) La más importante: si un
  Vendedor re-guarda el borrador de una venta convertida, el gate de precio le recalcula los precios
  desde el producto y **los cotizados se pierden**. No se debilitó el gate: se agregó
  `Venta.PresupuestoOrigenId` y un aviso en pantalla que lo dice con esas palabras, pero resolverlo
  de verdad necesita una excepción al gate y eso es decisión suya. (2) Qué se hace con los 38
  productos de costo cero/negativo y los 3 de costo 6,3 billones. (3) Si el preview tiene que
  exportarse a Excel antes de aplicar (con 112.000 productos, revisar 25 por página es revisar poco;
  no estaba pedido). (4) Si hace falta deshacer una corrida, que requiere tabla de detalle y es otra
  ronda. (5) Si se unifica la regla de la oferta vigente, que toca Ventas en producción.
- Detalle completo (archivos por capa, migración, criterios verificados con números, guía de
  verificación manual, riesgos y checklist de merge) en
  `definiciones/5-implementador.md`, sección "Entrega 6".
### 2026-10-05 22:55 - implementador-dotnet (Entrega 3, ítem 4c: moneda y cotización + paso 6: pagos programados)

- Etapa: Implementación. Rama `entrega-1-migracion`, repo `C:\Sistemas\Ferreteria La Platense`.
  Base de trabajo `laplatense_dev`. **Producción no se tocó**: ni deploy, ni Web Deploy, ni ninguna
  operación contra `mysql8001.site4now.net`. **Sin push.** El fixture de QA `laplatense_qa_d9` no se
  leyó ni se modificó. Pedido explícito de Joaquín: "no publicar, dejar el desarrollo listo".
- **El ítem 4c no era una feature pendiente: era un bug activo, y el brief tenía razón.** La ola 2
  agregó `Proveedor.Moneda` y `Proveedor.TipoCambio` y **ninguno de los dos se aplicaba en ningún
  cálculo** — verificado por grep: el 100% de los hits era persistencia, proyección o pantalla, cero
  aritmética. Desde que la ola 3 hizo que `RecibirAsync` escriba `Producto.PrecioCompra`, una compra
  en dólares persistía el costo **en dólares dentro de un campo que todo el sistema lee como pesos**,
  y aguas abajo cuelgan `PorcentajeRecargo` → `PrecioVenta` → `PrecioOferta`. **Medido en el arnés:
  donde correspondía `$ 12.658,28` quedaba `8,55`.**
- **Pasada 0 de `LP-002` (verificar las premisas del brief): las cuatro se confirmaron.** Es la
  primera ronda en que la pasada 0 no encuentra nada falso — `TipoCambio`/`Moneda` sin un solo uso
  aritmético, **0 hits de `AddHostedService`**, `INotificationService.CreateAsync` con firma
  idéntica a la del precedente, y los tres campos del paso 6 ya declarados sin escritor. Que esta
  vez no rindiera no la invalida: costó tres greps y es lo que habilitó confiar en el resto del
  brief.
- **La decisión de diseño de la ronda: `TotalEnPesos` se PERSISTE.** Dos razones, las dos medidas y
  ninguna estética: (a) el `Cargo` de la cuenta corriente y el tope de pago tienen que ser **el
  mismo número al centavo**, o pagar el total no deja el saldo del proveedor en cero (CA 2), y
  recalcular pone una multiplicación y un redondeo en cada consumidor; (b) **el listado ordena por
  el total del lado del servidor**, y una propiedad calculada en C# no traduce a SQL — ordenar por
  `Total` mezclando monedas pone una compra de USD 1.000 arriba de una de $ 1.500.000.
- **El punto único: `ConversionMoneda`** (`Application/Helpers/`, estático, sin dependencias, mismo
  rol que `ArgentinaTime`). Una sola fórmula de conversión con un solo redondeo, la única definición
  de "cuándo hace falta cotización" (consumida por las **cuatro** mitades de la guarda: alta,
  edición, confirmación y recepción) y un solo diccionario de etiquetas y símbolos. **LANZA** si
  falta la cotización en moneda extranjera: devolver el importe sin convertir "por las dudas" es
  exactamente el bug que la ronda cierra.
- **La moneda y la cotización se CONGELAN en el documento**, con el mismo criterio que `PAT-052`
  aplica al factor de conversión: se precargan de la ficha del proveedor, son editables, y cambiar
  la ficha después no altera ninguna compra ya cargada (CA 4, medido). `Proveedor.TipoCambio` dejó
  de ser pendiente declarado y pasó a ser lo que siempre debió: **el default, nunca la fuente de
  verdad de una compra ya cargada.**
- **Me aparté del precedente en dos lugares, a propósito, y los dos quedan declarados.**
  (1) **No se portó su `BackgroundService` a hora fija (03:10 ART).** Este proyecto no tiene ni un
  hosted service y corre en SmarterASP, donde el pool se recicla por inactividad: un job de la
  madrugada en un sistema que se usa de 8 a 20 **puede no correr nunca y nadie se enteraría** —
  no hay ningún error que lo delate. Un scheduler que no se puede garantizar es **peor** que no
  tenerlo, porque se confía en él. En su lugar, chequeo oportunista al primer request autenticado
  del día, con tres guardas y **la idempotencia donde el precedente ya la tenía y no depende del
  scheduler**: filtrar `Estado == Pendiente && !Notificado` y marcar en la misma llamada. El orden
  importa — si la garantía viviera en el flag en memoria, cada reciclado de pool mandaría los avisos
  de nuevo.
  (2) **La confirmación de un pago programado NO pisa `FechaPagoTentativa`.** Allá sí, y deja
  `PagoOrdenCompra.Fecha` en el instante del registro: el documento y sus asientos quedan con fechas
  distintas y **se pierde el plazo que se había pactado**. Acá se reescribe `Fecha` (que está
  documentada como "el instante en que la plata salió") y la tentativa queda intacta como registro.
  Lo que SÍ se copió tal cual es su CR-63: **los asientos van con la fecha de HOY**, no con la
  prevista.
- **La mitad simétrica de `LP-009` en el paso 6:** el alta de un pago **enteramente programado** NO
  corre `ValidarPeriodoAbiertoAsync`, porque no mueve un peso — exigirle un período abierto sería
  impedir agendar un pago futuro porque el mes pasado ya se cerró. El criterio es el que ya decidía
  que el ajuste manual de CC la saltee: **lo que la hace necesaria es que el movimiento escriba
  CAJA**, no que la operación se llame "pago". La confirmación sí la corre (CA 5).
- **Tres números de saldo, distintos y no intercambiables**, cada uno con su método: lo **pagado**
  (solo `Pagado`, lo que salió de verdad), lo **comprometido** (`Pagado` + `Pendiente`, que **es el
  tope** — con el primero como tope se podría agendar el total completo tres veces) y
  `ObtenerSaldosAsync`, que los devuelve juntos en una consulta agrupada.
- **El barrido `LP-002` rindió 7 hallazgos propios.** El más grande: **la resta "total − pagado"
  estaba escrita a mano en CUATRO lugares** (el Service, el ViewModel del detalle y dos métodos del
  controller) y los cuatro usaban `Total` — con la moneda en el documento, los cuatro pasaron a
  restar **dólares menos pesos**. Se cerró con `ObtenerSaldosAsync` y ahora no la repite ninguno.
  Los otros: el listado ordenando por `Total` y mezclando monedas; `Details.cshtml` mostrando la
  cotización de **hoy** de la ficha en una compra vieja (un número que esa compra nunca usó); el
  total de las compras en la CC del proveedor en moneda del documento al lado de movimientos en
  pesos; el XML-doc de `OrdenCompraItem.PrecioCompra` que decía "en pesos" (`LP-008`); el texto de
  `CuentaCorriente.cshtml` que decía que la recepción "es la próxima etapa del módulo", falso desde
  el paso 4 y que la ola 3 no barrió; y **la tercera copia del mapa de monedas** —
  `BusquedaHelper.EnumsQueCoinciden` compara contra el nombre del enum (`Dolar`) y no contra la
  etiqueta visible (`Dólares`), así que `ProveedorService` tenía las dos etiquetas escritas a mano
  al lado de la llamada. **Ese último lo encontró el arnés, no la lectura: la consulta ejecutaba y
  devolvía 0 filas.**
- **Pasada 3 (promesas vencidas): 9 correcciones.** Los 5 lugares de `PagoOrdenCompra` que decían
  "DECLARADO, NUNCA ESCRITO (paso 6)", los 2 de `EstadoPagoProveedor`, el de `IPagoProveedorService`
  y el de `DependencyInjection` ("para que los pasos 6 y 7 no vuelvan a armar el egreso inline"),
  que ahora dice que **el paso 6 ya lo consumió y entró sin tocar una línea del punto único, que es
  exactamente para lo que se había creado**. Es la cuarta ronda consecutiva en que esta pasada
  rinde.
- **Pasada 6 (la migración sobre las filas que YA estaban): el hallazgo más caro, y es la segunda
  vez que la misma enfermedad aparece con otra cara.** EF agrega las dos columnas NOT NULL con
  `defaultValue: 0`: `Moneda = 0` es el **mismo defecto** que la migración de la ola 2 tuvo que
  repararle a 85 proveedores, pero **`TotalEnPesos = 0` es peor, porque es un importe que miente** —
  toda compra ya cargada pasaría a tener saldo pendiente 0, se mostraría como **totalmente pagada**,
  el tope de pago sería 0 así que no se le podría imputar un peso, y recibirla postearía un `Cargo`
  de **$ 0,00** en la cuenta corriente, en silencio. Dos `UPDATE` con `WHERE` acotado, el índice
  creado **después** del backfill, y el backfill **verificado ejecutándolo** sobre filas fabricadas
  en ese estado exacto (`laplatense_dev` tiene 0 compras, así que no tocó ni una fila real) con
  `GROUP BY` de control, segunda corrida para probar que es inocuo, y `ROLLBACK`.
- **Evidencia, toda ejecutada y sin navegador** (la discrepancia de abajo sigue vigente): build de
  la solución limpio; **las vistas Razor SÍ compilan en el build**, probado metiendo un símbolo
  inexistente en la vista nueva y viendo el `CS0103` con número de línea; grafo de DI con
  `ValidateOnBuild + ValidateScopes` — y esta vez el arnés necesitó **registrar Identity de verdad**
  (`AddIdentityCore` + `AddRoles` + `AddEntityFrameworkStores`) en vez de stubear, porque
  `IAvisoPagosProgramadosService` depende de `UserManager<ApplicationUser>` y sin eso **el grafo
  falla por el arnés y esa falla tapa las del código**; Services ejercitados contra
  `laplatense_dev`, idempotentes, corridos 3 veces, cerrando en **0 filas de prueba y 112.485
  productos**.
- **`MH-001`: las 7 consultas nuevas o modificadas se EJECUTARON, no se leyeron**, incluidas las dos
  que filtran por colección (`monedas.Contains(...)` en los dos listados) y el caso borde de la
  regla — la búsqueda global con **todas** las colecciones de enum **vacías**. Ejecutar fue lo que
  encontró el séptimo hallazgo del barrido.
- **Los 10 criterios de aceptación de las dos partes dieron OK, con números medidos.** Compra de
  US$ 1.034,55 a cotización congelada $ 1.480,50 → `Cargo` en la CC **$ 1.531.651,28**, `Egreso` en
  caja **$ 1.531.651,28**, saldo del proveedor al pagar el total **$ 0,00**, `PrecioCompra`
  resultante **$ 12.658,28** (base neta sin IVA, convertida, por unidad de venta).
- **Lo que NO se probó y queda para QA**: `INotificationService.CreateAsync` dentro del flujo del
  aviso y el middleware en el pipeline real. Los dos necesitan usuarios con rol y un request HTTP
  — o sea navegador. Son los pasos 13 a 17 de la guía de pruebas manuales.
- **Discrepancia de método, cuarta vez que se declara:** los briefs de este proyecto piden verificar
  por navegador y el `.agent.md` del Implementador lo **prohíbe explícitamente**. Gana el rol
  (el prompt lo designa fuente de verdad) y se compensa con evidencia ejecutada que no es navegador.
  QA dio GO a las tres rondas anteriores con esta misma forma de evidencia. **Si se quiere el smoke
  por navegador, hay que cambiar la regla en el `.agent.md`, no pedirlo por brief**, porque si no se
  repite cada corrida.
- **Catálogo de patrones: dos entradas nuevas.** `PAT-055` (documento que congela su moneda y su
  cotización) y `PAT-056` (chequeo oportunista al primer request del día en vez de hosted service,
  con la idempotencia en la base y no en el scheduler).
- **Decisiones que necesita Joaquín** (ninguna bloquea el desarrollo, las tres bloquean el deploy):
  (1) el **aviso de impacto de los egresos automáticos** en el arqueo sigue sin darse y ahora hay un
  segundo camino que los genera (la confirmación de un pago programado); (2) **la fórmula fiscal de
  la compra** sigue sin confirmarse contra una factura real suya, y el `ratioDescuento` determina el
  costo que se persiste en el catálogo; (3) **si la ferretería paga con cheque propio diferido**, que
  decide si el paso 7 (cartera) entra. Y una nueva: **si en el futuro hacen falta jobs a hora fija,
  la decisión es de hosting (pool `AlwaysRunning`, Idle Time-out 0) y corresponde consultarla con
  `olvidata-infra`** — no se resuelve escribiendo un hosted service que el entorno no puede
  sostener.
- Artefactos: `docs/la-platense/definiciones/5-implementador.md` (v13), `docs/patrones/catalogo.yml`
  (`PAT-055`, `PAT-056`).
### 2026-10-05 21:50 - implementador-dotnet (Entrega 3, pasos 4 y 5: recepción de mercadería + pagos a proveedores)

- Etapa: Implementación. Rama `entrega-1-migracion`, repo `C:\Sistemas\Ferreteria La Platense`.
  Base de trabajo `laplatense_dev`. **Producción no se tocó**: ni deploy, ni Web Deploy, ni ninguna
  operación contra `mysql8001.site4now.net`. **Sin push.** El fixture de QA `laplatense_qa_d9` no se
  leyó ni se modificó. Pedido explícito de Joaquín: "no publicar, dejar el desarrollo listo".
- **Cierra el impacto real del módulo de Compras.** Hasta el paso 3 nada de Compras movía un peso ni
  una unidad: `RecibirAsync` (`Confirmada → Recibida`) incrementa stock, escribe un ledger de stock
  nuevo y postea el `Cargo` de deuda en una transacción — **y no toca la caja**; `PagoProveedorService`
  es el **primer punto del módulo por donde sale plata**, con un `Pago` en la cuenta corriente y un
  `Egreso` en la caja por línea, mismo monto, misma fecha y mismo `OrigenId`.
- **El hallazgo que cambió el diseño, y vino de verificar la premisa del brief en vez de heredarla
  (pasada 0 de `LP-002`):** el brief pedía usar `IUnidadMedidaConversionService.ConvertirCompraAVenta`
  **y** el factor congelado de la línea (`PAT-052`) — **las dos cosas son incompatibles**, porque ese
  método lee `producto.FactorConversion`, o sea el factor de **hoy**. Usarlo habría roto exactamente
  el congelamiento que `OrdenCompraItem` existe para garantizar, en silencio, y solo cuando alguien
  editara la ficha entre la carga y la recepción. La salida fácil (que la recepción se arme la
  multiplicación aparte) parte la regla en dos lugares, que es cómo nacen las reincidencias de
  `LP-002`: se agregó al contrato `ConvertirConFactor(unidadCompra, unidadVenta, factorCongelado,
  cantidad)` y `ConvertirCompraAVenta` quedó como envoltorio. **Una sola fórmula, dos entradas.**
  El brief también afirmaba que el único call site era `EsFactorConversionValido` en
  `ProductoService:444`; el real es `:554` **y además** `OrdenCompraService:707`. Lo que sí era
  cierto es que `ConvertirCompraAVenta` tenía **cero** consumidores.
- **Guard previo y no try/catch, por una razón medible:** con 80 renglones, descubrir el factor
  inválido en el renglón 40 deja 39 productos ya modificados en el change tracker — funcionaría por
  el rollback, pero "no deja nada a medio aplicar" pasaría a ser propiedad de la base y no del
  código. `ValidarConversion` devuelve el mensaje en vez de tirar, se recorren **todas** las líneas y
  se juntan **todos** los problemas. Medido corrompiendo el dato a mano
  (`FactorConversionAplicado = 0` directo en la base, el único camino por el que puede quedar
  inválido porque la carga lo valida): rechazo nombrando el producto, y stock `15→15` y `7→7`,
  movimientos de CC `1→1`, ledger `2→2`, estado `Confirmada`. **La línea que sí se podía convertir no
  se movió.**
- **Ledger de stock construido de cero.** `AjusteStock` no servía por dos motivos independientes: no
  tiene `OrigenTipo`/`OrigenId` (el movimiento no se ata al documento) y su semántica es "alguien
  contó y corrigió", que es otra cosa — por eso `RecibirAsync` **no toca `StockVerificado`**, marcarlo
  sería afirmar algo que no pasó. **Alcance declarado:** `Σ MovimientoStock` **no** reconstruye
  `Producto.Stock` (Ventas y el ajuste siguen escribiendo sin rastro, y lo histórico no se migró),
  así que la recepción escribe **las dos cosas** y no deriva una de la otra.
- **El costo del producto: la base no es el total de la factura.** Es `Subtotal − descuentos`
  prorrateado por línea, **sin IVA ni percepciones** — sumárselo inflaría el catálogo entero un 21%
  y, por la fórmula derivada, después el precio de venta. Es un número **distinto** del `Cargo` de
  deuda (que sí lleva impuestos): los dos son correctos y conviene dejarlo escrito antes de que
  alguien lo "arregle". Dos detalles no cosméticos: se acumula **por producto** (una compra con el
  mismo producto en dos renglones queda con el promedio ponderado real, no con el último cargado) y un
  costo calculado en **0 no se escribe** (un remito sin precios o un descuento del 100% pisarían el
  catálogo con 0, destructivo y silencioso).
- **`PAT-054` nuevo, primera implementación del estudio:** bandera "costo actualizado, precio sin
  recalcular" + fecha, expuesta en el listado del catálogo como columna, **filtro tri-estado**, orden
  y búsqueda global por su etiqueta — sobre 112.485 filas una alerta que no se puede aislar es
  inservible. **Hallazgo de la mitad simétrica: nada la apagaba**, y una alerta que no se apaga deja
  de significar algo. Se apaga en `ProductoService.EditarAsync` solo si cambió `PrecioVenta` o
  `PorcentajeRecargo`, y se **mantiene** si el usuario guardó la ficha sin tocarlos — guardar no es
  decidir el precio.
- **`PAT-053` nuevo:** punto único de egreso de caja de un pago, portado de marihogar CR-84 y
  **simplificado** (de sus 579 líneas solo ~80 son runtime; el resto es backfill one-shot suyo y no
  se portó). El punto único se crea **ahora con 2 escritores y no con 5**, porque crearlo después
  obligó allá a un backfill que fue 500 de esas 579 líneas. Se copió el detalle valioso: mismo
  `OrigenTipo` y mismo `OrigenId` (**el id de la línea de pago, no del documento** — `MH-027`) en los
  dos ledgers, así que un pago se rastrea de uno al otro sin traducción.
- **Cierre de `LP-002` que corta la recurrencia.** El relevamiento encontró el ledger de caja **ya
  desincronizado antes de agregarle nada**: tres constantes en `CajaMovimientoService` más un cuarto
  literal suelto en `CuentaCorrienteClienteService` (no había un lugar con los cuatro), y el combo de
  filtro de `Views/Caja/Index.cshtml` con etiquetas legibles mientras la columna "Origen" de la
  **misma grilla** mostraba el valor crudo — el filtro decía "Cobro de cuenta corriente" y la fila
  "CobroCC". Se creó `OrigenCajaMovimiento` con los 5 orígenes y sus etiquetas, las constantes viejas
  quedaron como **alias**, y **agregar un origen ya no requiere tocar la vista**. Mismo criterio de
  entrada para el ledger nuevo (`OrigenMovimientoStock` nace como helper, no como constantes del
  Service).
- **Pasada 3 del barrido: 20 correcciones de XML-doc.** Siete lugares declaraban como "no
  implementado todavía" lo que esta ronda implementó, o sea **reglas de negocio falsas viviendo en el
  repo**. Y un hallazgo que no es un comentario viejo sino una **promesa vencida**:
  `Proveedor.TipoCambio` decía que convertir la moneda era "alcance del paso 4" y **no lo fue** — se
  reescribió como pendiente declarado, porque una promesa vencida hace creer que el caso está
  cubierto, y ahora pesa más que antes porque ese costo **se persiste en la ficha del producto**.
- **Pasada 2:** el grep de `DateTime` en `Domain/Entities` da **34** (eran 29), las 5 nuevas
  clasificadas. **Pasada 6 verificada y no supuesta:** la lección de los 85 proveedores con
  `Moneda = 0` **no aplica** (bool con `false` legítimo, datetime nullable, y el único enum no
  nullable está en tabla **nueva**), confirmado con `GROUP BY` sobre la base — una sola fila, `0` con
  112.485.
- **Contexto que QA necesita:** `laplatense_dev` tiene **0 productos** con `UnidadCompra` distinta de
  `UnidadVenta` sobre 112.485 (el ítem 0.4 pasó los 87.542 `Metro` a `Unidad` en bloque), así que el
  camino principal del paso 4 **no tiene ni un dato real que lo ejercite**: se midió con productos
  sembrados y limpiados, y para probarlo a mano **hay que crear uno**.
- **Evidencia ejecutada, sin navegador** (lo prohíbe el rol): build **0 errores** (9 advertencias
  preexistentes); prueba de que las vistas Razor **sí** compilan en el build (símbolo inexistente →
  `CS0103` en `RegistrarPago.cshtml:293`, revertido); grafo de DI con
  `BuildServiceProvider(ValidateOnBuild + ValidateScopes)` —  sus 3 fallas iniciales eran **del
  arnés** (`IConfiguration` e `IWebHostEnvironment` los aporta el host) y se stubearon, porque si no
  tapan las del grafo; y **51/51 checks** de los Services **directo** contra `laplatense_dev`, con la
  base devuelta a su línea base (0 filas de prueba, 112.485 productos). `MH-001` cubierto **por
  ejecución** en las 10 consultas nuevas, **incluido el resultado vacío**, que es donde la regla
  revienta. `CRM-019` reapareció en el arnés (`StartsWith` sobre constante): el bug está vivo; el
  código de producción no lo tiene.
- **Migración** `20261006002448_EntregaTres_RecepcionMercaderiaYPagosProveedor`, **estrictamente
  aditiva** (2 columnas en `Productos` + 2 tablas nuevas), aplicada **solo a `laplatense_dev`**.
  Producción queda **4 migraciones atrás**.
- **Tres pendientes para Joaquín:** (1) `Proveedor.TipoCambio` **no se aplica** y ahora el costo de
  una compra en dólares se persiste **mal** en la ficha del producto; (2) **aviso de impacto** — este
  es el primer egreso automático del arqueo del cliente, y en marihogar los egresos del período
  "subieron mucho" de golpe el día del deploy: no es un bug, es plata que siempre salió, pero hay que
  avisarle **antes** de que lo vea; (3) la fórmula fiscal de la compra sigue sin confirmarse contra
  una factura real suya, y ahora su ratio de descuento **determina el costo que queda en el catálogo**.
- Pendiente de verificación de QA.
### 2026-10-05 20:30 - implementador-dotnet (Entrega 3, pasos 1 a 3: Proveedores + CC de proveedores + Ordenes de compra)

- Etapa: Implementación. Rama `entrega-1-migracion`, repo `C:\Sistemas\Ferreteria La Platense`.
  Base de trabajo `laplatense_dev`. **Producción no se tocó**: ni deploy, ni Web Deploy, ni ninguna
  operación contra `mysql8001.site4now.net`. **Sin push.** El fixture de QA `laplatense_qa_d9` no se
  leyó ni se modificó. Pedido explícito de Joaquín: "no publicar, dejar el desarrollo listo".
- Gate verificado antes de empezar: definiciones 2, 3 y 4 aprobadas. El plan de cierre de alcance de
  `4-presupuestador.md` declara para la Entrega 3 **"Gates abiertos: ninguno"** y "arranca sin
  esperar nada del cliente".
- Alcance: los **pasos 1, 2 y 3 de 9** del módulo de Compras. Al cerrar, el **alta y la edición de
  compras están completas y no tocan stock, ni caja, ni cuenta corriente**. La recepción (paso 4,
  que mueve stock y genera deuda) y los pagos (paso 5) **no entran**, y es una frontera construida,
  no una omisión: `IOrdenCompraService` no expone `RecibirAsync` y `OrdenCompraService` no inyecta
  `IStockService`/`ICajaMovimientoService`/`ICCProveedorService`, así que no se puede llamar por
  accidente lo que no está inyectado. Los mensajes de la UI lo dicen explícitamente para que el
  perímetro no se lea como un bug durante la prueba.
- Reutilización (escaneo de la instrucción 39, sección 3): encontrado en el **paso 1**
  (`cat_resumen.txt`), sin necesidad de grep dirigido. `PAT-001` (ledger de cuenta corriente —
  port de `marihogar/CCProveedorService.cs`, con el camino de vuelta ya recorrido en casa:
  `MovimientoCCCliente` de este proyecto es un port del `MovimientoCCProveedor` de vinosefue, así
  que el patrón volvió a Proveedor), `PAT-005` (máquina de estados), `PAT-008`/`PAT-016`
  (DataTables + búsqueda global + filtros en Session). `PAT-020`/`PAT-051` leídos y declarados como
  el camino de los pasos 4 y 5, no aplicados todavía. `PAT-050` revisado y descartado (todo el
  módulo es Administrador exclusivo). **Tres piezas sin antecedente, declaradas**: el modelo de
  unidad de la línea de compra, el buscador por código de proveedor, y los campos
  `TipoCambio`/`Moneda`/`PorcentajeDescuentoHabitual`/`FormaPagoHabitual` (los tres verificados con
  0 hits en marihogar).
- **Catálogo de patrones**: agregado **`PAT-052`** ("Línea de documento que declara su unidad y
  CONGELA el factor de conversión") y actualizado **`PAT-001`** con tres `archivos_referencia`
  nuevos de la-platense (`CCProveedorService`, `OrigenCCProveedor`, y el contrato corregido de
  `ObtenerNetoVivoAsync`) más la aplicación en `proyectos_que_lo_usan`. `cat_resumen.txt`
  regenerado (50 patrones).
- **Barrido LP-002 (las 4 pasadas + 2 extras) — 5 hallazgos propios:**
  1. **La premisa del brief era falsa.** Decía que `Proveedor` "se consume como catálogo simple en
     los combos del catálogo de productos". El relevamiento dio **CERO consumidores en `Web/`**: el
     único escritor real era `tools/MigracionCatalogo` (inicializador de objeto con `Nombre` +
     `Activo`) y el único lector, el `CatalogoSimpleServiceBase` que se reemplazó. Eso permitió una
     migración **estrictamente aditiva** y **mantener `Nombre` como nombre de columna** (marihogar
     lo llama `RazonSocial`): renombrarlo era destructivo sobre 85 razones sociales reales y rompía
     el contrato de la herramienta de migración, a cambio de nada funcional.
  2. **La migración dejaba los 85 proveedores existentes con `Moneda = 0`**, un valor que no
     existe en el enum (`Peso = 1`). El listado habría mostrado "0" crudo y el filtro "Pesos" no
     los habría encontrado: la columna funciona perfecto para las filas nuevas y está mal en las
     que ya estaban, en silencio. Se agregó a mano la corrección de datos a la migración generada.
  3. **`AppDbContext.cs`** seguía diciendo que "el módulo de Compras la amplía más adelante".
     Corregido (pasada de comentarios prescriptivos).
  4. **`Views/Dashboard/Index.cshtml`** decía que el nivel 2 "depende de Compras y Cuenta Corriente
     de proveedores". Las dos piezas ya existen; lo que falta es la CC propia del negocio (Entrega
     4). Corregido el texto, no el panel.
  5. **La mitad simétrica**: las líneas de la compra viajan en inputs `hidden` que arma el JS, y
     `EditarAsync` reemplaza el set completo — un post con cero líneas habría **vaciado la compra
     en silencio**. Se agregó la guarda.
- **2 bugs propios encontrados EJECUTANDO**, los dos invisibles en revisión de código:
  (a) `ObtenerNetoVivoAsync` devolvía 160.000 en vez de 60.000 porque filtraba por tipo, y en un
  ledger de deuda la reversión de un `Cargo` se postea como un `Pago`. Corregido a neto **con
  signo** sobre los dos tipos; efecto colateral deseado: `EsReversion` queda informativo y no
  participa de la aritmética. (b) el neto vivo no estaba acotado por proveedor, y como los orígenes
  manuales usan `OrigenId = 0`, habría mezclado el saldo inicial de **todos** los proveedores.
  Y un tercero **en el arnés de verificación**: `p.Nombre.StartsWith("ZZVERIF-E3")` reventó con
  `COLLATE utf8mb4_bin ... does not have a type mapping assigned`, que es **`CRM-019`** reproducido
  en vivo. El código de producción de esta ronda no tiene ni un `StartsWith`/`EndsWith`.
- Migración EF: **`20261005231651_EntregaTres_ProveedoresCCCompras`**, 100% aditiva (18 `AddColumn`,
  3 `CreateTable`, 9 `CreateIndex`, cero `DropColumn`/`AlterColumn`), **aplicada solo a
  `laplatense_dev`**, sin drift de modelo. **Producción queda ahora TRES migraciones atrás.**
- Evidencia ejecutada (sin navegador, según el rol): build limpio de la solución con las vistas
  Razor dentro del build (confirmado: un `RZ1031` en una vista rompió el build y hubo que
  corregirlo); grafo de DI validado con `ValidateOnBuild` + `ValidateScopes`; y los Services
  ejercitados **directamente contra `laplatense_dev`** — **161 checks, 161 OK**, con limpieza final
  que dejó la base en su línea base exacta (85 proveedores, 0 compras, 0 movimientos de CC, 0
  residuo de prueba).
- **Discrepancia de rol, ya registrada el 2026-10-05 y que se repite**: el brief pide verificación
  en navegador real y el `.agent.md` del Implementador se lo prohíbe explícitamente. Se siguió el
  rol (que el prompt designa como fuente de verdad) y se compensó con evidencia ejecutada que no es
  navegador. **Si se quiere el smoke por navegador del Implementador, hay que cambiar la regla en
  el `.agent.md`, no pedirlo por brief** — si no, se vuelve a discutir en cada corrida.
- **Decisiones que necesita Joaquín** (ninguna bloquea los pasos 4 y 5, pero las dos primeras
  conviene cerrarlas antes):
  1. **La fórmula fiscal de la compra.** La *estructura* de dos descuentos en cascada está
     respaldada por dato propio (`Producto.Bonificacion` guarda `"33+5"`, que es 36,35% efectivo y
     no 38%). La *fórmula exacta* — en particular que las percepciones de IIBB y Otros se liquiden
     sobre la base pelada y no sobre base + IVA — viene de una factura real de un proveedor de
     **marihogar**, no de uno de La Platense. **Confirmar contra una factura real suya.**
  2. **El factor de conversión es fijo por producto** (pregunta abierta 6 de `4-presupuestador.md`,
     sigue sin resolver). Si el mismo producto llega en bultos de distinto tamaño según el
     proveedor, tendría que vivir en `CodigoProveedorProducto`. El snapshot congelado en la línea
     **absorbe** ese caso sin cambio de esquema (el operador corrige el factor a mano), pero no lo
     resuelve de raíz. **Preguntárselo antes de escribir la migración del paso 4.**
  3. **Cheques**: `FormaPagoProveedor` declara `Cheque` y `ChequeElectronico` porque el presupuesto
     menciona "echeck/transferencia", pero **no existe cartera de cheques en el sistema**.
     Confirmar si la ferretería paga con cheque propio diferido antes del paso 7 (4h).
  4. **El listado de proveedores no puede ordenar ni filtrar por saldo del lado del servidor**
     porque el saldo no es una columna (vive en el ledger). Hoy el filtro de rango aplica sobre la
     página visible y está declarado en la pantalla; la columna no es ordenable. Con 85 proveedores
     alcanza — si el padrón creciera a miles habría que materializar el saldo.
- Documentos actualizados: `5-implementador.md` (v11, sección "Entrega 3 — pasos 1 a 3" + entrada
  de historial), `docs/patrones/catalogo.yml` (`PAT-052` nuevo, `PAT-001` actualizado),
  `docs/patrones/cat_resumen.txt` (regenerado) y esta entrada.
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
### 2026-10-05 (5) - implementador (fundacion del ledger de caja + anulacion de venta confirmada)
- Etapa: implementacion. Repo del sistema, rama `entrega-1-migracion`, commit local **`59dd715`**.
- **NO pusheado y NO deployado**, por pedido explicito de Joaquin ("no publicar, dejar el desarrollo listo"). La migracion se aplico **solo a `laplatense_dev`**; nada corrio contra produccion.
- **Parte 1 — `CajaMovimiento` gana las 4 columnas que le faltaban**: `EsReversion` (MH-020), `PagoVentaId` (MH-027), `UsuarioId` y `MedioPago` (MH-034, enum nuevo `MedioPagoCaja` = union de `MedioPago` y `FormaPagoGasto`, con mapper unico de `switch` exhaustivos). `GastoService.AnularAsync` migrado al mecanismo del **neto vivo** (`Sigma originales no-reversion - Sigma reversiones`): revertir dos veces pasa a ser imposible **por construccion** y no por un flag que haya que acordarse de chequear en cada via nueva, que es como nacio MH-020 en marihogar.
- **Decision de diseño declarada sobre MH-034**: el medio es un **atributo para filtrar y conciliar, no una caja con saldo propio**. El saldo sigue siendo uno y agrupado y el arqueo por medio es un desglose del mismo total — es el corolario que marihogar aprendio con datos (partirlo obliga a cargar cada traspaso entre cuentas propias, que este negocio no carga, y cada traspaso no cargado descuadra dos cajas en vez de ninguna). El rotulo de la pantalla lo dice y la fila de Total repite el saldo agrupado.
- **Parte 2 — anulacion de una venta `Confirmada`, que no existia**: `EstadoVenta.Anulada` estaba en el enum y ningun codigo la disparaba, asi que un error de carga en una venta confirmada era **irreparable**. `AnularAsync` devuelve el stock en la unidad de la linea (decimal, no `int` como marihogar), revierte la caja **pago por pago** por el neto posteado y revierte el **debito vivo** de cuenta corriente, todo en una transaccion. Guardas: motivo obligatorio, Administrador **o** el vendedor que la creo, sin Entrega asociada, periodo de la venta **y** de hoy abiertos (LP-009), y bloqueo completo si algun pago no es identificable (MH-027). Una venta `Facturada` se rechaza con mensaje: necesita NC de AFIP (Entrega 5), y el guard es el punto exacto donde se enchufa — documentado, incluido **por que la NC tiene que emitirse antes** de revertir (si AFIP la rechaza, la reversion no se puede aplicar; el orden de `ConfirmarYFacturar` dejaria la caja revertida con una factura viva).
- Reutilizacion: `PAT-020` encontrado en el **paso 1** del escaneo (`cat_resumen.txt`), sus dos `archivos_referencia` confirmados reales. Copiado de `VentaService.CancelarAsync` y `EgresoPagoProveedorService.ObtenerNetoPosteadoAsync` de marihogar. **MH-034 se declaro sin antecedente** (verificado en el repo: marihogar tampoco lo resuelve) y se construyo nuevo.
- **Decision que cerro el implementador y conviene retener**: el relevamiento de identificabilidad de los pagos va **antes** de abrir la transaccion, y si **uno** falla se bloquea la anulacion **completa**. Revertir "los que se pueden" es peor que no anular: el stock volvio, el estado cambio, y falta plata que nadie va a ir a buscar. Y no se infiere el pago por monto — esa es exactamente la adivinanza que produjo MH-027 en produccion.
- **Barrido LP-002, los 4 campos**: `OrigenTipo` (6 lectores relevados, **ninguno necesito cambio** porque la reversion comparte `OrigenTipo`/`OrigenId` con el original y no se agrego ningun origen nuevo; los 4 literales pasaron a constantes porque un typo en una punta dejaba el guard de MH-027 sin efecto **y no fallaba nada**); `EstadoVenta` (**verificado, no asumido**: Dashboard y ABC filtran por **whitelist** `Confirmada || Facturada`, asi que `Anulada` queda afuera sola — los arqueos no filtran por estado y **no deben**, se calculan sobre el ledger donde el contramovimiento neutraliza); `OrigenMovimientoCC` (origen nuevo `AnulacionVenta = 4` al final y numerado, propagado a los **dos** lectores de la vista de CC: el combo y el mapa de etiquetas — son dos y no uno); `MedioPago` (combo con opcion "Sin declarar", columna en la grilla con su caso de ordenamiento MH-015, buscador global comparando contra la **etiqueta visible** y no el nombre del enum, campo opcional en el alta manual, y desglose en los arqueos diario y mensual).
- **Evidencia, sin smoke test funcional**: build limpio (9 advertencias, **todas preexistentes**) + rebuild forzado `--no-incremental` del Web para compilar de verdad las 5 vistas Razor + `node --check` sobre el JS embebido de las 3 vistas con script (el compilador de Razor no lo chequea). **MH-001**: barrido ampliado a `\.(Contains|Any)\(` — el codigo nuevo **no introduce ni un caso**, y el filtro por medio del buscador se resuelve con una consulta por medio y el valor como **parametro escalar**, a proposito.
- **Lo que mas valio, y es metodo repetible**: la regla MH-001 pide **ejecutar**, no inspeccionar, asi que se armo una **sonda desechable en el scratchpad** (proyecto consola fuera del repo, que referencia `Infrastructure` y se borro despues) y se corrieron **de verdad** las 7 consultas nuevas contra `laplatense_dev`, incluido el `GroupBy` con **enum nullable en la clave** del arqueo por medio, que era el shape de mayor riesgo. Las 7 tradujeron. Y el backfill no se dio por bueno porque el `UPDATE` no fallo: se **midio** sobre las 9 filas del ledger — 2 reversiones marcadas ($91.500,50), medio derivado en 8 de 9 (la novena es el ajuste manual, que legitimamente no tiene), **las 3 filas de venta con su `PagoVentaId` exacto apuntando a un pago de la misma venta y del mismo medio**, y netos vivos en **0,00** para los dos gastos ya anulados, que es el fix de MH-020 observable con datos y no por lectura.
- Migracion `20261005221747_LedgerCaja_Identidad_MedioPago_AnulacionVenta`: **aditiva** (7 columnas nullable/con default + 2 indices, ninguna columna existente cambia de tipo ni de nullabilidad) y con **backfill en 5 pasos**. El backfill **no es opcional**: sin el, cada fila anterior queda con `PagoVentaId NULL`, que es lo que hace que `AnularAsync` **bloquee las ventas ya confirmadas**. El paso 3 (medio de ventas y cobros) lee el sufijo de la `Descripcion`, que es el unico lugar donde el dato quedo — y que haya que leer texto para recuperarlo es, literalmente, la razon por la que la columna tiene que existir.
- **Riesgos/pendientes, 3 decisiones para Joaquin**: (1) **antes de publicar**, verificar contra produccion que el backfill le resuelve el `PagoVentaId` a las 3 ventas `Confirmada` — es lo que determina si quedan anulables o bloqueadas (query de control en `5-implementador.md`); (2) la guarda de "periodo de la venta abierto" es **mas estricta que marihogar** y es lo que pedia el criterio 8: una venta de un dia ya cerrado **no se puede anular** y hay que resolverla con ajuste manual — si resulta demasiado rigido, esa es la guarda a relajar (la de hoy es tecnica y no se puede sacar); (3) sigue faltando el **saldo inicial por medio**: este cambio hace conciliable el **flujo** del periodo, que es lo que se puede conciliar con saldo agrupado, pero ningun arreglo del flujo hace que el saldo signifique "la plata que hay" si el punto de partida es un cero inventado (MH-034). Aparte: con tarjeta de credito el medio **no** dice donde quedo la plata (liquida en banco o billetera segun la terminal); conciliar liquidaciones de tarjeta necesitaria una dimension "cuenta" ademas del medio, y no entra en esta ronda. Dato raro de dev para QA: las 3 ventas `Facturada` no tienen pagos cargados.
### 2026-10-06 - orquestador (borrado de datos de prueba de produccion + cierre de 2 decisiones)
- **Autorizado explicitamente por Joaquin**: *"Esa venta fue de prueba. Borrar datos de prueba"*. Backup previo de 33 MB (`backup-prod-ANTES-DE-BORRAR-PRUEBAS-20261006-031533.sql`, fuera del repo).
- **Esto cierra el hallazgo del cierre de caja firmado en $0,00.** El 2026-10-06 se detecto que el cierre diario del 03/09 estaba firmado en $0,00 mientras el dia tenia $286.449,57 en tres ventas (defecto D9: el cierre consultaba el dia equivocado). Resulta que **las tres ventas eran de prueba**, asi que no habia un documento contable real mal emitido: habia datos de prueba. El hallazgo igual sirvio — es lo que destapo que produccion nunca habia tenido actividad real.
- **Correccion de un supuesto que venia desde el 2026-09-28:** la memoria del proyecto afirmaba *"Prod ya tiene actividad real encima (Venta 1 con ClienteId=1248), asi que una recarga total de Clientes no es opcion sin preservar Ids"*. **Era falso: esa venta tambien era de prueba.** Produccion no tenia ni una sola transaccion real. Si en el futuro hace falta recargar Clientes, esa restriccion ya no aplica — pero verificar de nuevo antes de asumirlo, que es justamente el error que se corrige acá.
- Borrado (orden seguro de FK, en una transaccion): 5 Ventas, 5 ItemsVenta, 6 PagosVenta, 4 CajaMovimientos, 1 CierreCajaDiario, 1 Entrega, 1 AjusteStock (con `Motivo = 'prueba'` literal). `Gastos`, `MovimientosCCCliente` y `CierresCajaMensuales` ya estaban vacios.
- **El paso que un `DELETE` pelado se habria olvidado: restituir el stock.** Las 3 ventas `Confirmada` habian dejado **5 productos en −1,000**. Se devolvio sumando la cantidad vendida (no un `SET 0` a ciegas, que habria perdido el valor real si no hubiera sido 0 antes), y el ajuste de prueba se revirtio a su `CantidadAnterior` con `StockVerificado = 0`. Verificado: **0 productos con stock distinto de 0, 0 negativos**.
- Contadores `AUTO_INCREMENT` reiniciados en las 10 tablas vaciadas, para que la primera venta real del cliente sea la #1 y no la #6.
- Verificado post-borrado: catalogo intacto (112.485 productos), 2.990 clientes, 85 proveedores, 7 recargos de cuota. **Produccion queda en cero transaccional, lista para el arranque real.**
- **Decision cerrada — formula fiscal de la compra:** Joaquin respondio *"Imitar las facturas de compra de marihogar"*. Es lo que ya esta construido (dos descuentos en cascada + percepciones sobre la base pelada, portado de `OrdenCompra` de marihogar), asi que **no hay cambio de codigo**: la duda declarada desde la ola 2 queda resuelta confirmando lo implementado.
- **Decision cerrada — aviso de impacto de los egresos:** Joaquin respondio "Ok". El cliente va a ser avisado de que el arqueo va a mostrar egresos automaticos por dos caminos nuevos (pago a proveedor y confirmacion de pago programado) antes de publicar.
- Riesgos/pendientes: **sigue abierta la decision de los cheques** (si la ferreteria paga con cheque propio diferido), que define si se construye el paso 7 de la Entrega 3 — lo unico que queda sin construir de ese modulo. Y los 6 lotes de QA de las olas 1 a 6 estaban corriendo al momento de esta limpieza, **contra copias propias de `laplatense_dev`**, asi que no se vieron afectados.
### 2026-10-06 - implementador (ronda de atomicidad y concurrencia: la familia del LP-018)

- Etapa: implementacion. Repo del sistema `C:\Sistemas\Ferreteria La Platense`, rama `entrega-1-migracion`, commit local **`bdfd99b`**.
- **NO pusheado y NO deployado**, por pedido explicito de Joaquin (*"no publicar, dejar el desarrollo listo"*). **Ninguna migracion EF** (esta ronda no agrega ni una columna), asi que no corrio nada contra ninguna base mas que un clon desechable. `laplatense_dev` quedo en su linea base exacta, verificada por conteo. Los 7 clones de QA (`laplatense_qa_l1..l6`, `laplatense_qa_d9`) no se tocaron. **Produccion intacta.**
- **El hallazgo que ordena todo**: los 4 partes de defecto que dejaron 6 lotes de QA — `LP-018` (critical), `LP-023` y `LP-024` (major), `LP-021` (minor latente) — **eran una sola cosa**, encontrada por 3 lotes independientes en 4 modulos distintos: *leer, decidir y despues escribir, sin nada que lo haga atomico*. Se cerro como familia, con **un** mecanismo aplicado en 9 sitios, y no como 4 arreglos.
- **Mecanismo elegido y su fundamento**: `BloqueoDeFila` (`SELECT ... FOR UPDATE` sobre la fila del documento dueño) + **relectura bajo lock**, con la transaccion movida de *"antes de escribir"* a **"antes de LEER"**. Se descarto la otra opcion razonable, el **indice unico**, por una razon de negocio y no de gusto: el neto vivo EXISTE para permitir reversiones **parciales**, asi que dos filas de reversion sobre el mismo origen son legitimas y un unique las prohibiria — habria roto el criterio 4 del propio parte, que QA ya habia verificado ($600 sobre una reversion parcial de $400). Se descarto el flag en memoria por `PAT-056`: en SmarterASP lo normal es mas de un worker y el pool recicla, asi que un `static` no es una garantia.
- **Desvio declarado del brief, para que Joaquin lo confirme o lo revierta**: el brief pedia portar `Producto.RowVersion` de marihogar *"literal"*. Se porto el **criterio** (la garantia vive en la base, verificada al guardar) y no la implementacion. Tres razones: (1) un token de concurrencia es **global al modelo** y `Producto` tiene dos escritores **masivos** que guardan entidades trackeadas por lotes sobre 112.485 filas (`AumentoMasivoPrecioService`, `ClasificacionAbcAutomaticaService`) — una sola edicion concurrente abortaria el `SaveChanges` del lote **completo**, cuando hoy rechaza fila por fila y sigue; (2) el `RowVersion` compara la cosa equivocada para este caso, porque cambia con **cualquier** columna y una edicion de precio ajena rechazaria un conteo fisico correcto; (3) **el propio catalogo ya habia escrito este criterio para este proyecto** el 2026-10-05, en la nota de `PAT-004`: *"la salida no es agregar RowVersion a una entidad de 112.485 filas en el medio de otra entrega"*. En su lugar, el ajuste compara el `StockEsperado` que la pantalla **mostro** (campo oculto, nunca releido en el POST).
- **Barrido `LP-002`: 5 hallazgos propios, y varios PEORES que el que reporto QA.** La leccion de busqueda vale mas que los arreglos: no se arregla el sitio reportado, se busca la **forma** — `grep` de los metodos de transicion (`Anular|Cancelar|Confirmar|Cerrar|Convertir|Revertir|Marcar`) y, en cada uno, si la lectura que decide esta antes o despues del `BeginTransaction`. Encontrados y arreglados: la **confirmacion** de una venta (doble ingreso de caja + doble debito de CC + doble descuento de stock; la transaccion **no existia**, el metodo era atomico por accidente), la **facturacion** (**dos CAE de AFIP** para una venta: dos comprobantes fiscales de un solo hecho no se arreglan con una reversion interna, se arreglan con una NC ante AFIP), la **recepcion** de una compra (doble stock + doble deuda), la **confirmacion** de un pago programado (doble egreso) y la **conversion** de un presupuesto (dos ventas de la misma cotizacion). En tres de esos cinco, **el mensaje de la guarda ya describia con precision lo que el codigo no impedia** (*"recibirla otra vez duplicaria las dos cosas"*).
- **Lo que NO hubo que tocar, y verificarlo ahorro trabajo**: `CerrarDiaAsync`/`CerrarMesAsync` tienen la misma forma pero ya estan protegidos por el motor — `CierreCajaDiario` tiene indice **unico** en `Fecha` y `CierreCajaMensual` en `(Anio, Mes)`. Donde hay un unique que sirve, no hace falta lock. Otros 7 sitios con la forma pero **sin plata ni stock** (entregas, cancelaciones de borrador, aprobacion de presupuesto) quedaron relevados y declarados sin arreglar: el peor caso es una transicion escrita dos veces con el mismo resultado.
- **`LP-008`, 6 XML-doc y 2 comentarios corregidos, y cuatro eran promesas vencidas que escribi yo.** El defecto se encontro **en parte leyendo comentarios que afirmaban lo contrario de lo que el codigo hacia**: *"idempotente por construccion"*, *"imposible por construccion"*, *"correrlo dos veces en paralelo no duplica nada"* — todo cierto **en serie** y falso en paralelo, sin que ninguno lo calificara. En la ronda del 2026-10-05 se le presento a Joaquin el neto vivo como garantia por construccion contra la doble reversion; era falso para el caso concurrente y el comentario se replico en cinco archivos. Las correcciones ahora separan las dos cosas: el neto vivo garantiza **el importe** (y habilita las parciales), el lock garantiza **la exclusion mutua**.
- **Evidencia, y el dato de metodo que explica por que nadie lo vio antes.** Build limpio (0 errores, 9 advertencias **todas preexistentes**). Sin smoke test funcional. En su lugar, **sonda desechable** (consola en el scratchpad, borrada al terminar) contra un **clon aislado** (`mysqldump` de dev → base nueva, dropeada despues). La concurrencia se ejercito **de verdad, con conexiones separadas y barrera de sincronizacion**: con un cliente compartido las sentencias **se serializan solas y el test da FALSO VERDE** — exactamente lo que QA tuvo que forzar por HTTP. Equivalente en capa de datos: N scopes de DI independientes (N `DbContext`, N conexiones), las N conexiones abiertas **antes** de la barrera, soltadas juntas con un `TaskCompletionSource`, y se cuentan **filas**, no respuestas. Las lineas base, con **SQL crudo**, nunca con el codigo bajo prueba. **35 afirmaciones, 35 OK.**
- **Numeros medidos**: anulacion de la misma venta con **N=3** y con **N=8** → **1** exito y N−1 rechazos explicitos, **1** fila de reversion, neto vivo **0,00**, stock devuelto **una** vez. Reversion de un pago a proveedor, N=8 → 1 exito, **1** fila de reversion **en cada** ledger (caja y CC de proveedor), los dos netos en **0,00**. Reversion de un movimiento de CC de empleado, N=8 → 1 exito, **1** contramovimiento, los dos netos en **0,00**. Anulacion de gasto, N=8 → 1 exito, **1** reversion. `LP-023` con N=8 → devoluciones `[0,0,0,0,0,0,0,8]`, o sea **7 de 8 devuelven 0**, los 4 pagos marcados **una** vez y **8** notificaciones (4 pagos × 2 destinatarios, que es el numero correcto del diseño "una por pago y por usuario" — el criterio pedia 4 porque asumia 1 destinatario) y **no 32**. `LP-024` → con el stock cambiado de 30 a 35 entre el GET y el POST, el conteo de 29 se **rechaza**, el stock **sigue en 35**, `StockVerificado` **sigue en false** y **no** se escribe auditoria; sin carrera el ajuste entra igual (no regresion); con 8 ajustes simultaneos, **1** entra. Criterio 4 medido aparte: con una reversion parcial previa de $1.000 ya posteada, la anulacion revirtio **$4.163,80** (el neto) y no $5.163,80 (el nominal).
- **Aporte cross-proyecto**: `PAT-059` agregado a `docs/patrones/catalogo.yml` (*"Idempotencia por lectura previa: el patron que solo es seguro en secuencia"*), con las cuatro decisiones de diseño (lock y no unique; el dueño del lock es la fila mas fina; orden de bloqueo encapsulado; un lock fuera de transaccion es una garantia fantasma), la distincion entre la carrera de milisegundos y la de tiempo humano, y **el criterio de verificacion con conexiones separadas** — que es lo que separo el falso verde del defecto real. `cat_resumen.txt` regenerado (57 patrones).
- **Riesgos/pendientes — 4 decisiones para Joaquin**: (1) **el desvio de `RowVersion`**, a confirmar o revertir; (2) **`LP-024` criterio 2 no se puede cumplir en esta ronda y no es un defecto de este cambio**: el ledger de stock tiene **un solo escritor** (la recepcion), los otros tres valores del enum estan declarados *"sin escritor"* y los movimientos historicos **nunca se migraron** — el lost update si quedo cerrado, pero la suma historica no cuadra hasta que se decida si los tres escritores postean al ledger + backfill, o si se declara que el ledger es *rastro* y no *libro mayor*; (3) **comprobante AFIP huerfano**: ya no se pueden emitir dos CAE, pero si el proceso muere **entre** la respuesta de AFIP y el commit el comprobante existe alla y no aca — pide un estado intermedio *"facturacion en curso"* persistido antes de llamar (columna + enum nuevos), y no se improviso en una ronda de concurrencia; (4) si se cierran por consistencia los 7 sitios que tienen la forma pero no mueven plata. Aparte, **costo asumido y declarado en `FacturarAsync`**: el lock **se sostiene** mientras AFIP responde (soltarlo antes deja la ventana abierta justo donde dura mas); se bloquea **una** fila, pero si AFIP tarda mas que `innodb_lock_wait_timeout` (50 s) un segundo request sobre esa misma venta falla con un error de base y no con un mensaje lindo. Y `OrdenCompraService` (recepcion) y `PresupuestoService.ConvertirAVentaAsync` estan arreglados y compilados pero **no** ejercitados por la sonda (sin fixtures en el clon): **van en la lista de QA**.
- Los 4 partes quedan **"aplicado, pendiente de re-verificacion"**. El cierre lo declara QA en contexto nuevo, y el test tiene que ser **por sockets separados** por HTTP: la verificacion secuencial daria verde sobre el codigo viejo.
### 2026-10-06 (2) - orquestador (HOTFIX de transacciones publicado a produccion)
- Etapa: liberacion de hotfix. Rama **`hotfix-transacciones-ventas`** creada desde `2580f7c` (el commit publicado), **no** desde `entrega-1-migracion`, que tiene 7 commits de desarrollo con 3 lotes de QA en NO-GO. Commits `c5b27a4` + `7ca5ce3`, pusheados a GitLab.
- **Origen del hotfix:** la ronda de atomicidad sobre la rama de desarrollo destapo que **el codigo publicado tenia CERO `BeginTransaction` en `VentaWorkflowService`** (verificado: `git show 2580f7c:...VentaWorkflowService.cs | grep -c BeginTransaction` -> 0). Cinco sitios leian, decidian y escribian sin atomicidad, todos moviendo plata, todos alcanzables en produccion.
- **Lo que el arnes midio contra el codigo roto** (los services revertidos a `2580f7c`, 40 fallas reproducibles, confirmadas despues por QA de forma independiente con su propio fixture): `RegistrarCobroAsync` era el peor — con N=8, **una deuda de $1.000 se cobro 8 veces**: saldo de CC **−$7.000**, 8 creditos y **$8.000** de ingresos de caja. `GastoService.AnularAsync`: N=8 -> 9 movimientos, neto **+$3.500** de plata que nunca entro. `ConfirmarAsync`: N=8 -> 2 exitos, $2.840 de caja donde iban $1.420. `FacturarAsync`: **8 comprobantes AFIP por una sola venta**. `CancelarBorradorAsync`: 5-6 exitos de 8, con estado prohibido persistido.
- **Mecanismo:** `BloqueoDeFila.cs` — `SELECT ... FOR UPDATE` sobre la fila dueña, relectura bajo lock, y la transaccion abierta **antes de LEER**, no antes de escribir. El helper tira si se lo llama fuera de transaccion (ahi el lock se libera solo y la garantia seria fantasma). **Se descarto el indice unico**: el neto vivo existe para permitir reversiones parciales, asi que dos filas de reversion sobre el mismo origen son legitimas. Sin migracion EF y sin columnas nuevas.
- **El hallazgo que justifico la pasada, y que aplica a todo el estudio:** aplicar el patron mecanicamente a `CancelarBorradorAsync` **fallo**, por dos razones invisibles leyendo el codigo. (1) Cancelar pone `DeletedAt` y **no toca `Estado`**, asi que el estado no discriminaba. (2) **`ReloadAsync` no ve las filas que el filtro global de soft delete esconde**: EF deja la entidad detached y los valores quedan en los de antes del lock — **la relectura parece hecha y no relee**. Como TODAS las entidades de estos proyectos heredan soft delete, el fix habria sido una ilusion. Cerrado con un helper unico (`IgnoreQueryFilters` + proyeccion de `Estado` y `DeletedAt`). Catalogado en `PAT-059`.
- **QA: GO.** 6/6 criterios, y verifico por **mutacion** en vez de por lectura: rompio el arbol arreglado de dos formas (relectura decorativa -> 24 fallas, rompe los tres metodos; sin `IgnoreQueryFilters` -> 4 fallas, justo el invariante de cancelar-vs-confirmar) y confirmo que el arnes detecta cada rotura. Midio el lock del cliente con dos sesiones MySQL reales: bloquea al mismo cliente (3.271 ms) y **no** a clientes distintos (234 ms).
- **QA corrigio un error del brief que habria invalidado la verificacion:** le pedi clonar `laplatense_dev`, que tiene **14 migraciones** contra las **8** de la rama publicada. Habria probado contra un esquema que produccion no tiene. Armo la base desde las 8 migraciones de la rama. **Leccion: el fixture de un hotfix se construye desde la rama publicada, nunca desde dev.**
- **Tres premisas de los briefs del orquestador salieron falsas al ejecutarlas** (van 3 rondas con lo mismo): la falla parcial ya estaba cubierta por el `SaveChanges` unico + transaccion implicita de EF (el criterio pasa con y sin el fix); el stock **no se duplicaba, se perdia** (los dos leen 100, los dos escriben 98, daba el numero correcto por casualidad); y el `RowVersion` de marihogar no correspondia (es global al modelo, habria hecho abortar los procesos masivos sobre 112.485 productos, y compara la cosa equivocada: una edicion de precio ajena rechazaria un conteo fisico correcto — `PAT-004` ya tenia el criterio escrito).
- Deploy ejecutado: backup previo de 33 MB, build Release, Web Deploy (`msdeploy -verb:sync`, `AppOffline` + `DoNotDeleteRule`), **310 archivos, exit 0 en el segundo intento** — el primero murio con `ERROR_DESTINATION_NOT_REACHABLE` por una caida transitoria del servicio de administracion de SmarterASP en el puerto 8172, el mismo sintoma del 2026-08-18. El sitio respondio `HTTP 200` todo el tiempo. Script `.cmd` con la credencial borrado inmediatamente despues.
- Verificado post-deploy: `/` y `/Account/Login` en `HTTP 200`, 8 migraciones sin cambios, 112.485 productos, 0 ventas, 0 movimientos de caja. **Produccion queda en cero transaccional y sin los 5 defectos: el cliente puede empezar a operar.**
- Riesgos/pendientes: **`LP-034`** (`minor`, abierto, no bloqueaba el deploy) — el unico camino decorativo que quedo no esta en el estado de la venta sino en el **stock**: el `ReloadAsync` sobre `Producto`, y `Producto` **si** admite baja logica (`EliminarAsync`/`EliminarLoteAsync` escriben `DeletedAt` sin guarda de uso). Si un producto se borra en la ventana, el descuento de stock se pierde en silencio: venta confirmada, plata correcta, stock intacto. La asimetria se razono para `Venta` y `Gasto` y no para la unica de las tres con baja expuesta. **`RegistrarAjusteAsync` de CC tambien mueve plata del ledger**, pero su exposicion es doble submit y su arreglo es idempotencia, no lock. Quedan 4 sitios mas del barrido sin tocar. **Y falta reconciliar `hotfix-transacciones-ventas` con `entrega-1-migracion`**, donde los mismos 5 metodos ya tenian su version del fix: no mergear a ciegas.

## Historial de ajustes de alcance
