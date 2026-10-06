# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

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

## Historial de ajustes de alcance

### Bloques archivados (2026-10-05)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-08** — 17 bloques (2026-08-11 a 2026-08-17) → [`trazabilidad-2026-08-2.md`](historial/trazabilidad-2026-08-2.md)


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

### Traza de corrida -- 2026-10-05 / etapa implementacion
- Reintentos: 2
- Criterios fallados: ninguno
- Reglas releidas: 32#LP-002, 32#MH-001, 32#MH-020, 32#MH-027, 32#MH-033, 32#MH-034, 32#LP-003, 32#MH-021, 32#KOI-001, 32#KOI-B02, 39#3, agents#implementador-dotnet, patrones#PAT-020
- Arranque real: 56 KB (~14k tokens)
- Nota: Fundacion del ledger de caja (las 4 columnas de CajaMovimiento) + anulacion de una venta Confirmada, que NO EXISTIA: EstadoVenta.Anulada estaba en el enum y ningun codigo la disparaba, asi que un error de carga en una venta confirmada era irreparable. Commit local 59dd715, SIN push y SIN deploy por pedido explicito de Joaquin; la migracion se aplico solo a laplatense_dev. PAT-020 encontrado en el PASO 1 del escaneo (cat_resumen.txt), sus dos archivos_referencia confirmados reales, copiado de VentaService.CancelarAsync y EgresoPagoProveedorService.ObtenerNetoPosteadoAsync de marihogar; MH-034 declarado SIN antecedente (verificado en el repo: marihogar tampoco lo resuelve, su medio vive en texto libre) y construido nuevo. LO QUE MAS VALIO, Y ES METODO REPETIBLE: la regla MH-001 pide EJECUTAR y no inspeccionar, asi que se armo una SONDA DESECHABLE EN EL SCRATCHPAD -- proyecto consola fuera del repo que referencia Infrastructure, corrido contra laplatense_dev y borrado despues -- y se ejecutaron de verdad las 7 consultas nuevas, incluido el GroupBy con ENUM NULLABLE EN LA CLAVE del arqueo por medio, que era el shape de mayor riesgo y el que un build limpio no cubre. Las 7 tradujeron. Y el backfill NO se dio por bueno porque el UPDATE no fallo: se MIDIO sobre las 9 filas del ledger -- 2 reversiones marcadas, medio derivado en 8 de 9 (la novena es el ajuste manual, que legitimamente no tiene), las 3 filas de venta con su PagoVentaId exacto apuntando a un pago de la MISMA venta y del MISMO medio, y netos vivos en 0,00 para los dos gastos ya anulados, que es el fix de MH-020 observable con datos. DECISION DE DISEÑO QUE CERRO EL IMPLEMENTADOR Y CONVIENE RETENER: el relevamiento de identificabilidad de los pagos va ANTES de abrir la transaccion, y si UNO falla se bloquea la anulacion COMPLETA -- revertir "los que se pueden" es peor que no anular, porque el stock volvio, el estado cambio y falta plata que nadie va a ir a buscar; y el pago no se infiere por monto, que es exactamente la adivinanza que produjo MH-027 en produccion. Tres divergencias respecto de marihogar, documentadas en el XML-doc: cantidades decimales (su VentaItem es int), reversion de caja POR LINEA DE PAGO y no agregada (unica forma de deshacer exactamente lo posteado y de que el desglose por medio quede coherente: un contramovimiento agregado no tiene medio que declarar), y ausencia del estado "pago no posteado" (acá ese rol lo cumple CuentaCorriente, que se revierte contra el ledger del cliente). El guard de Facturada deja el diseño preparado para la NC de AFIP de la Entrega 5, con el ORDEN documentado: la NC se emite ANTES de revertir, porque si AFIP la rechaza la reversion no se puede aplicar y el orden de ConfirmarYFacturar dejaria la caja revertida con una factura viva. MH-034: el medio es un ATRIBUTO para filtrar y conciliar, NO una caja con saldo propio -- el saldo sigue siendo uno y agrupado, por el corolario que marihogar aprendio con datos. BARRIDO LP-002 de los 4 campos: OrigenTipo (6 lectores, NINGUNO necesito cambio porque la reversion comparte OrigenTipo/OrigenId con el original; los 4 literales pasaron a constantes porque un typo en una punta dejaba el guard de MH-027 sin efecto Y NO FALLABA NADA), EstadoVenta (VERIFICADO y no asumido: Dashboard y ABC filtran por WHITELIST Confirmada||Facturada, asi que Anulada queda afuera sola, y los arqueos no filtran por estado y NO DEBEN porque se calculan sobre el ledger donde el contramovimiento neutraliza), OrigenMovimientoCC (AnulacionVenta=4 al final y numerado, propagado a los DOS lectores de la vista de CC -- combo y mapa de etiquetas, son dos y no uno), MedioPago (combo con opcion "Sin declarar" que necesito parametro booleano propio y no un centinela del enum, porque un option no puede postear null y "" ya significa todos; columna con su caso de ordenamiento MH-015; buscador comparando contra la ETIQUETA VISIBLE y no el nombre del enum). MH-001: el codigo nuevo no introduce ni un caso, y el filtro por medio del buscador usa una consulta por medio con el valor como PARAMETRO ESCALAR, a proposito. Evidencia sin smoke test funcional: build 0 errores (9 advertencias, todas preexistentes) + rebuild forzado --no-incremental del Web para compilar de verdad las 5 vistas Razor + node --check sobre el JS embebido de las 3 vistas con script, que el compilador de Razor no chequea. Migracion aditiva con BACKFILL EN 5 PASOS que no es opcional: sin el, cada fila anterior queda con PagoVentaId NULL y AnularAsync BLOQUEA las ventas ya confirmadas. TRES DECISIONES ABIERTAS PARA JOAQUIN: (1) antes de publicar, verificar CONTRA PRODUCCION que el backfill le resuelve el PagoVentaId a las 3 ventas Confirmada, que es lo que determina si quedan anulables o bloqueadas; (2) la guarda de "periodo de la venta abierto" es MAS ESTRICTA que marihogar y es lo que pedia el criterio 8 -- una venta de un dia ya cerrado no se puede anular y hay que resolverla con ajuste manual; si resulta rigido, esa es la guarda a relajar (la de hoy es tecnica y no se puede sacar); (3) sigue faltando el SALDO INICIAL por medio: este cambio hace conciliable el FLUJO del periodo, pero ningun arreglo del flujo hace que el saldo signifique "la plata que hay" si el punto de partida es un cero inventado. Aparte: con tarjeta de credito el medio NO dice donde quedo la plata (liquida en banco o billetera segun la terminal), conciliar liquidaciones necesitaria una dimension "cuenta" ademas del medio y no entra en esta ronda. Dato raro de dev para QA: las 3 ventas Facturada no tienen pagos cargados. Pendiente de verificacion de QA.


### Traza de corrida -- 2026-10-05 / etapa implementacion
- Reintentos: 4
- Criterios fallados: CRM-019, LP-002, MH-001
- Reglas releidas: 32#MH-001, 32#CRM-019, 32#LP-003, 25#formularios, 26#entidades, 26#workflow, 26#modificacion, 39#3
- Nota: Entrega 3 pasos 1-3 (Proveedores + CC proveedores + Ordenes de compra). 4 reintentos de build/diseno: (1) nombre de variable duplicado en OrdenCompraService; (2) RZ1031 por autofocus condicional en un tag helper de una vista parcial -- confirma que las vistas Razor SI entran en el build; (3) el arnes de verificacion reprodujo CRM-019 en vivo con StartsWith sobre constante (fix: EF.Functions.Like); (4) ObtenerNetoVivoAsync filtraba por tipo y devolvia la suma en vez del neto vigente -- se rediseno el contrato a neto CON SIGNO. LP-002 citado porque el barrido rindio 5 hallazgos propios, incluido que la premisa del brief sobre los consumidores de Proveedor era falsa y que la migracion dejaba los 85 proveedores existentes con un valor de enum invalido. MH-001 citado como regla aplicada preventivamente y verificada ejecutando (cero colecciones locales de string). Evidencia: build limpio, grafo de DI validado, 161/161 checks de Services contra laplatense_dev con la base devuelta a su linea base. Sin push y sin deploy por pedido explicito de Joaquin.


### Traza de corrida -- 2026-10-05 / etapa implementacion
- Reintentos: 2
- Criterios fallados: ninguno
- Reglas releidas: 32#LP-002, 32#MH-001, 32#MH-020, 32#MH-027, 32#LP-003, 32#LP-009, 32#CRM-019, 39#3, agents#implementador-dotnet, patrones#PAT-052, patrones#PAT-020, patrones#PAT-019
- Arranque real: 58 KB (~14k tokens)
- Nota: Entrega 3 pasos 4 y 5: recepcion de mercaderia y pagos a proveedores. Commit local, SIN push y SIN deploy por pedido explicito de Joaquin; la migracion se aplico solo a laplatense_dev. LO QUE MAS VALIO Y NO ESTABA EN EL BRIEF: la PASADA 0 del barrido LP-002 (verificar las premisas en vez de heredarlas) encontro que el brief pedia DOS COSAS INCOMPATIBLES -- usar IUnidadMedidaConversionService.ConvertirCompraAVenta Y el factor congelado de la linea (PAT-052). Ese metodo lee producto.FactorConversion, o sea el factor de HOY, asi que usarlo habria roto exactamente el congelamiento que OrdenCompraItem existe para garantizar, en silencio y solo cuando alguien editara la ficha entre la carga y la recepcion. La salida facil (que la recepcion se arme la multiplicacion aparte) parte la regla en dos lugares, que es como nacen las reincidencias de LP-002: se agrego al contrato ConvertirConFactor(unidadCompra, unidadVenta, factorCongelado, cantidad) y ConvertirCompraAVenta quedo como envoltorio -- una sola formula, dos entradas. Y el brief tambien afirmaba que el unico call site era EsFactorConversionValido en ProductoService:444; el real es :554 y ADEMAS OrdenCompraService:707 (el paso 3 ya lo habia cableado). Lo que si era cierto es que ConvertirCompraAVenta tenia CERO consumidores. GUARD PREVIO Y NO TRY/CATCH, decidido por una razon medible: con 80 renglones, descubrir el factor invalido en el renglon 40 deja 39 productos ya modificados en el change tracker -- funciona por el rollback, pero 'no deja nada a medio aplicar' pasa a ser propiedad de la base y no del codigo. ValidarConversion devuelve el mensaje en vez de tirar, se recorren TODAS las lineas y se juntan TODOS los problemas. Medido corrompiendo el dato a mano (FactorConversionAplicado=0 directo en la base, el unico camino por el que puede quedar invalido porque la carga lo valida): rechazo nombrando el producto, y stock 15->15 y 7->7, movsCC 1->1, ledger 2->2, estado Confirmada -- la linea que SI se podia convertir no se movio. LEDGER DE STOCK CONSTRUIDO DE CERO porque AjusteStock no servia por dos motivos independientes: no tiene OrigenTipo/OrigenId (el movimiento no se ata al documento) y su semantica es 'alguien conto y corrigio', que es otra cosa -- por eso RecibirAsync NO toca StockVerificado, marcarlo seria afirmar algo que no paso. ALCANCE DECLARADO que hay que tener a la vista: Sigma MovimientoStock NO reconstruye Producto.Stock (Ventas y el ajuste siguen escribiendo sin rastro y lo historico no se migro), asi que la recepcion escribe LAS DOS COSAS y no deriva una de la otra. COSTO: la base no es el total de la factura sino Subtotal menos descuentos prorrateado, SIN IVA ni percepciones -- sumarselo inflaria el catalogo entero un 21% y, por la formula derivada, despues el precio de venta. Es un numero DISTINTO del Cargo de deuda (que si lleva impuestos) y conviene dejarlo escrito antes de que alguien lo 'arregle'. Dos detalles no cosmeticos: se acumula POR PRODUCTO (una compra con el mismo producto en dos renglones queda con el promedio ponderado real, no con el ultimo cargado) y un costo calculado en 0 NO se escribe (remito sin precios o descuento del 100% pisarian el catalogo con 0, destructivo y silencioso). PAT-054 nuevo (primera implementacion del estudio): bandera 'costo actualizado, precio sin recalcular' + fecha, expuesta en el listado como columna, FILTRO tri-estado, orden y busqueda global por etiqueta -- sobre 112.485 filas una alerta que no se puede aislar es inservible. HALLAZGO DE LA MITAD SIMETRICA: nada la APAGABA, y una alerta que no se apaga deja de significar algo; se apaga en ProductoService.EditarAsync solo si cambio PrecioVenta o PorcentajeRecargo, y se MANTIENE si el usuario guardo la ficha sin tocarlos (guardar no es decidir el precio). PAT-053 nuevo: punto unico de egreso de caja de un pago, portado de marihogar CR-84 y SIMPLIFICADO -- de sus 579 lineas solo ~80 son runtime, el resto es backfill one-shot suyo y no se porto. El punto unico se crea AHORA con 2 escritores y no con 5, porque crearlo despues obligo alla a un backfill que fue 500 de esas 579 lineas. Se copio el detalle valioso: mismo OrigenTipo y mismo OrigenId (el id de la LINEA de pago, no del documento -- MH-027) en los dos ledgers. CIERRE DE LP-002 QUE CORTA LA RECURRENCIA: el relevamiento encontro el ledger de caja YA DESINCRONIZADO antes de agregarle nada -- tres constantes en CajaMovimientoService mas un cuarto literal suelto en CuentaCorrienteClienteService (no habia un lugar con los cuatro), y el combo de filtro de Views/Caja/Index.cshtml con etiquetas legibles mientras la columna 'Origen' de la MISMA grilla mostraba el valor crudo: el filtro decia 'Cobro de cuenta corriente' y la fila 'CobroCC'. Se creo OrigenCajaMovimiento con los 5 origenes y sus etiquetas, las constantes viejas quedaron como alias, y agregar un origen ya NO requiere tocar la vista. Mismo criterio de entrada para el ledger nuevo (OrigenMovimientoStock nace como helper). PASADA 3 rindio 20 correcciones de XML-doc: siete lugares declaraban como 'no implementado todavia' lo que esta ronda implemento, o sea reglas de negocio FALSAS viviendo en el repo. Y un hallazgo que no es un comentario viejo sino una PROMESA VENCIDA: Proveedor.TipoCambio decia que convertir la moneda era 'alcance del paso 4' y NO LO FUE -- se reescribio como pendiente declarado, porque una promesa vencida en un comentario hace creer que el caso esta cubierto, y ahora pesa mas que antes porque ese costo se persiste en la ficha del producto. PASADA 2: el grep de DateTime en Domain/Entities da 34 (eran 29), las 5 nuevas clasificadas. PASADA 6 verificada y no supuesta: la leccion de los 85 proveedores con Moneda=0 NO aplica (bool con false legitimo, datetime nullable, y el unico enum no nullable esta en tabla NUEVA), confirmado con GROUP BY sobre la base -- una sola fila, 0 con 112.485. CONTEXTO QUE QA NECESITA: laplatense_dev tiene 0 productos con UnidadCompra distinta de UnidadVenta sobre 112.485 (el item 0.4 paso los 87.542 Metro a Unidad en bloque), asi que el camino principal del paso 4 NO tiene ni un dato real que lo ejercite -- se midio con productos sembrados y limpiados, y para probarlo a mano hay que crear uno. EVIDENCIA EJECUTADA SIN NAVEGADOR: build 0 errores (9 advertencias preexistentes); prueba de que las vistas Razor SI compilan (simbolo inexistente -> CS0103 en RegistrarPago.cshtml:293, revertido); grafo de DI con BuildServiceProvider(ValidateOnBuild+ValidateScopes), cuyas 3 fallas iniciales eran DEL ARNES (IConfiguration e IWebHostEnvironment los aporta el host) y se stubearon porque si no tapan las del grafo; y 51/51 checks de los Services DIRECTO contra laplatense_dev con la base devuelta a su linea base (0 filas de prueba, 112.485 productos). MH-001 cubierto POR EJECUCION en las 10 consultas nuevas INCLUIDO EL RESULTADO VACIO, que es donde la regla revienta. CRM-019 reaparecio en el arnes (StartsWith sobre constante): el bug esta vivo, el codigo de produccion no lo tiene. TRES PENDIENTES PARA JOAQUIN: (1) TipoCambio no se aplica y ahora el costo en dolares se persiste MAL en la ficha del producto; (2) el aviso de impacto -- este es el primer egreso automatico del arqueo y en marihogar los egresos del periodo 'subieron mucho' de golpe el dia del deploy, hay que avisarle ANTES de que lo vea; (3) la formula fiscal sigue sin confirmarse contra una factura real suya, y ahora su ratio de descuento determina el costo que queda en el catalogo. REINTENTOS: 2 (una tupla con nombres de campo que el compilador no infirio en el acumulador de costos; y dos heredocs de bash que rompieron por las comillas -- los scripts de parcheo van por Write, ya es la quinta vez en el proyecto). Produccion y laplatense_qa_d9 sin tocar. Pendiente de verificacion de QA.



### Traza de corrida -- 2026-10-05 / etapa implementacion
- Reintentos: 4
- Criterios fallados: LP-002, MH-001, LP-008, LP-009
- Reglas releidas: 32#LP-002 32#MH-001 32#LP-003 32#LP-008 32#LP-009 32#MH-027 39#3 agents#implementador-dotnet patrones#PAT-052 patrones#PAT-053 patrones#PAT-054 patrones#PAT-055 patrones#PAT-056
- Arranque real: 62 KB (~15k tokens)
- Nota: Entrega 3 item 4c (moneda y cotizacion) + paso 6 (pagos programados). Commit local, SIN push y SIN deploy por pedido explicito de Joaquin; la migracion se aplico solo a laplatense_dev. EL ITEM 4c NO ERA UNA FEATURE PENDIENTE SINO UN BUG ACTIVO, y el brief tenia razon: Proveedor.Moneda y Proveedor.TipoCambio existian desde la ola 2 y NO SE APLICABAN EN NINGUN CALCULO (verificado por grep: el 100% de los hits era persistencia, proyeccion o pantalla, cero aritmetica), asi que desde que la ola 3 hizo que RecibirAsync escriba Producto.PrecioCompra una compra en dolares persistia el costo EN DOLARES dentro de un campo que todo el sistema lee como pesos, y aguas abajo cuelgan PorcentajeRecargo -> PrecioVenta -> PrecioOferta. Medido en el arnes: donde correspondia $ 12.658,28 quedaba 8,55. PASADA 0 DEL BARRIDO: las cuatro premisas del brief se CONFIRMARON -- es la primera ronda en que la pasada 0 no encuentra nada falso (TipoCambio/Moneda sin un solo uso aritmetico, 0 hits de AddHostedService, INotificationService.CreateAsync con firma identica a la del precedente, y los tres campos del paso 6 ya declarados sin escritor). Que no rindiera no la invalida: costo tres greps y es lo que habilito confiar en el resto del brief. LA DECISION DE DISEÑO DE LA RONDA, y es la que conviene retener: TotalEnPesos SE PERSISTE, por dos razones duras y ninguna estetica. (1) El Cargo del ledger de proveedores y el tope de pago tienen que ser EL MISMO NUMERO AL CENTAVO o pagar el total no deja el saldo en cero, y recalcular pone una multiplicacion y un redondeo en cada consumidor, que es como dos de ellos terminan difiriendo en un centavo. (2) El listado ORDENA POR EL TOTAL DEL LADO DEL SERVIDOR y una propiedad calculada en C# no traduce a SQL: ordenar por el total del documento mezclando monedas pone una compra de USD 1.000 arriba de una de $ 1.500.000, o sea que la grilla miente por yuxtaposicion. PUNTO UNICO NUEVO, ConversionMoneda (Application/Helpers, estatico y sin dependencias, mismo rol que ArgentinaTime): una sola formula con un solo redondeo, la unica definicion de "cuando hace falta cotizacion" consumida por las CUATRO mitades de la guarda (alta, edicion, confirmacion y recepcion -- exigirla solo al guardar no cubre un documento cargado antes de que la columna existiera ni un UPDATE directo, y sin las guardas de aguas abajo TotalEnPesos=0 postea una deuda de cero EN SILENCIO), y un solo diccionario de etiquetas y simbolos. LANZA si falta la cotizacion en moneda extranjera: devolver el importe sin convertir "por las dudas" ES el bug que la ronda cierra. Valida ademas que el enum no sea 0, el valor que un POST armado a mano manda. La moneda y la cotizacion se CONGELAN en el documento con el mismo criterio que PAT-052 aplica al factor de conversion: se precargan de la ficha, son editables, y cambiar la ficha despues no altera ninguna compra ya cargada (medido). Proveedor.TipoCambio dejo de ser pendiente declarado y paso a ser lo que siempre debio ser: el DEFAULT, nunca la fuente de verdad de una compra ya cargada. DOS DIVERGENCIAS DELIBERADAS DEL PRECEDENTE, las dos declaradas en el codigo. (1) NO SE PORTO SU BackgroundService A HORA FIJA (03:10 ART): este proyecto no tiene ni un hosted service y corre en SmarterASP, donde el pool se recicla por inactividad, asi que un job de la madrugada en un sistema que se usa de 8 a 20 PUEDE NO CORRER NUNCA y nadie se enteraria -- no hay ningun error que lo delate, y un scheduler que no se puede garantizar es PEOR que no tenerlo porque se confia en el. En su lugar, middleware con chequeo oportunista al primer request autenticado del dia, tres guardas (solo autenticados -> flag estatico con el ultimo dia, que es una comparacion de DateTime y deja el costo real en UNA consulta por dia y por proceso -> la idempotencia real) y LA IDEMPOTENCIA EN LA BASE Y NO EN EL FLAG: filtrar Pendiente && !Notificado y marcar en la MISMA llamada con su SaveChanges. El orden importa y es lo central -- si la garantia viviera en el flag en memoria, CADA RECICLADO DE POOL MANDARIA LOS AVISOS DE NUEVO. Con su mitad simetrica: reprogramar pone Notificado=false, porque la fecha nueva es un vencimiento nuevo (sin eso, reprogramar lo deja marcado como avisado para siempre). El middleware VA DESPUES de UseAuthentication o context.User no esta poblado y no dispararia nunca, y se awaitea en vez de fire-and-forget porque un Task suelto se queda sin scope y sin DbContext justo cuando el request termina. (2) LA CONFIRMACION NO PISA FechaPagoTentativa: alla si, y deja PagoOrdenCompra.Fecha en el instante del registro, asi que el documento y sus asientos quedan con fechas distintas y se pierde el plazo pactado. Aca se reescribe Fecha (documentada como "el instante en que la plata salio") y la tentativa queda intacta como registro. Lo que SI se copio tal cual es su CR-63: los asientos van con la fecha de HOY, no con la prevista. MITAD SIMETRICA DE LP-009 EN EL PASO 6: el alta de un pago ENTERAMENTE programado NO corre ValidarPeriodoAbiertoAsync porque no mueve un peso -- exigirle periodo abierto seria impedir agendar un pago futuro porque el mes pasado ya se cerro. El criterio es el que ya decidia que el ajuste manual de CC la saltee: lo que la hace necesaria es que el movimiento ESCRIBA CAJA, no que la operacion se llame "pago". La confirmacion si la corre. TRES NUMEROS DE SALDO DISTINTOS Y NO INTERCAMBIABLES, cada uno con su metodo: lo pagado (solo Pagado, lo que salio de verdad y lo que la CC refleja), lo comprometido (Pagado+Pendiente, que ES EL TOPE -- con el primero como tope se podria agendar el total completo tres veces) y ObtenerSaldosAsync, que los devuelve juntos en una consulta agrupada por estado (dos llamadas separadas podrian leer estados distintos si alguien confirma un pago en el medio). BARRIDO LP-002: 7 HALLAZGOS PROPIOS. El mas grande: la resta "total - pagado" estaba escrita A MANO EN CUATRO LUGARES (el Service, el ViewModel del detalle y dos metodos del controller) y los cuatro usaban Total, asi que con la moneda en el documento los cuatro pasaron a restar DOLARES MENOS PESOS -- se cerro con ObtenerSaldosAsync y ahora no la repite ninguno. Los otros seis: el listado ordenando por Total y mezclando monedas; Details.cshtml mostrando ProveedorTipoCambio, o sea la cotizacion de HOY de la ficha, en una compra vieja (un numero que esa compra nunca uso); el total de las compras en la CC del proveedor en moneda del documento al lado de movimientos de ledger que estan todos en pesos; el XML-doc de OrdenCompraItem.PrecioCompra que decia "en pesos" (LP-008, regla falsa viviendo en el repo); el texto de Proveedores/CuentaCorriente.cshtml que decia que la recepcion "es la proxima etapa del modulo", falso desde el paso 4 y que la ola 3 no barrio; y LA TERCERA COPIA DEL MAPA DE MONEDAS -- BusquedaHelper.EnumsQueCoinciden compara contra el nombre del enum (Dolar) y no contra la etiqueta visible (Dolares), asi que ProveedorService tenia las dos etiquetas ESCRITAS A MANO al lado de la llamada; con el combo del filtro y el renderer de la grilla eran tres copias, y se cerro con ConversionMoneda.QueCoincidenConElTexto. ESE ULTIMO LO ENCONTRO EL ARNES Y NO LA LECTURA: la consulta EJECUTABA y devolvia 0 filas, o sea que el build limpio y la revision de codigo la habrian dejado pasar. PASADA 3 (promesas vencidas): 9 correcciones -- los 5 lugares de PagoOrdenCompra que decian "DECLARADO, NUNCA ESCRITO (paso 6)", los 2 de EstadoPagoProveedor, el de IPagoProveedorService y el de DependencyInjection ("para que los pasos 6 y 7 no vuelvan a armar el egreso inline"), que ahora dice que el paso 6 YA LO CONSUMIO y entro sin tocar una linea del punto unico, que es exactamente para lo que se habia creado. Cuarta ronda consecutiva en que esta pasada rinde. PASADA 2: el grep de DateTime en entidades sigue dando 34 -- esta ronda no agrego ninguna columna de fecha, pero cambio la SEMANTICA de dos que ya existian y las dos quedaron declaradas: PagoOrdenCompra.Fecha ahora se REESCRIBE al confirmar, y FechaPagoTentativa es un DIA CALENDARIO SIN HORA y no un instante UTC, por eso ListarPorOrdenCompraAsync NO la proyecta con ArgentinaTime.From (le restaria tres horas y la correria al dia anterior); verificado por grep que ningun call site la proyecta. PASADA 6 (la migracion sobre las filas que YA estaban): EL HALLAZGO MAS CARO, y es la segunda vez que la misma enfermedad aparece con otra cara. EF agrega las dos columnas NOT NULL con defaultValue 0: Moneda=0 es el MISMO defecto que la migracion de la ola 2 tuvo que repararle a 85 proveedores, pero TotalEnPesos=0 ES PEOR PORQUE ES UN IMPORTE QUE MIENTE -- toda compra ya cargada pasaria a tener saldo pendiente 0, se mostraria como TOTALMENTE PAGADA, su tope de pago seria 0 asi que no se le podria imputar un peso, y recibirla postearia un Cargo de $ 0,00 en la cuenta corriente, en silencio. Dos UPDATE con WHERE acotado, indice creado DESPUES del backfill, y el backfill VERIFICADO EJECUTANDOLO y no suponiendolo: laplatense_dev tiene 0 compras, asi que no toco ni una fila real -- se fabricaron dos filas en el estado exacto post-defaultValue (una con total y una con total 0), se corrieron los dos UPDATE literales de la migracion, GROUP BY de control, SEGUNDA corrida para probar que son inocuos, y ROLLBACK. EVIDENCIA EJECUTADA SIN NAVEGADOR: build 0 errores; prueba de que las vistas Razor SI compilan (simbolo inexistente en PagosProgramados.cshtml -> CS0103 con numero de linea 6,20, revertido); grafo de DI con BuildServiceProvider(ValidateOnBuild+ValidateScopes), y ESTA VEZ EL ARNES NECESITO REGISTRAR IDENTITY DE VERDAD (AddIdentityCore + AddRoles + AddEntityFrameworkStores) en vez de stubear, porque IAvisoPagosProgramadosService depende de UserManager<ApplicationUser> y sin eso el grafo falla POR EL ARNES y esa falla tapa las del codigo; Services ejercitados directo contra laplatense_dev, idempotentes con prefijo ZZTEST y LimpiarAsync al principio y al final, corridos 3 VECES, cerrando en 0 filas de prueba y 112.485 productos. MH-001: las 7 consultas nuevas o modificadas SE EJECUTARON, incluidas las dos que filtran por coleccion (monedas.Contains en los dos listados) y el caso borde de la regla -- la busqueda global con TODAS las colecciones de enum VACIAS, que es donde revienta. LOS 10 CRITERIOS DE ACEPTACION DIERON OK CON NUMEROS MEDIDOS: compra de US$ 1.034,55 (10 bultos a US$ 100, 10%+5% en cascada = base US$ 855, IVA 21%) a cotizacion congelada $ 1.480,50 -> Cargo en la CC $ 1.531.651,28, Egreso en caja $ 1.531.651,28, saldo del proveedor al pagar el total $ 0,00, stock 100 unidades y PrecioCompra resultante $ 12.658,28 (base neta sin IVA, convertida, por unidad de venta). LO QUE NO SE PROBO Y QUEDA PARA QA: INotificationService.CreateAsync dentro del flujo del aviso y el middleware en el pipeline real -- los dos necesitan usuarios con rol y un request HTTP, o sea navegador (pasos 13 a 17 de la guia). DISCREPANCIA DE METODO, CUARTA VEZ QUE SE DECLARA: los briefs de este proyecto piden verificar por navegador y el .agent.md del Implementador lo PROHIBE explicitamente; gana el rol y se compensa con evidencia ejecutada que no es navegador, con la que QA dio GO a las tres rondas anteriores. Si se quiere el smoke por navegador hay que cambiar la regla en el .agent.md, no pedirlo por brief. HALLAZGO LATERAL EN EL TOOLING DEL ESTUDIO: el generador de cat_resumen.txt (scripts/contexto.py resumenes, regex de _items_yml) DESCARTA EN SILENCIO cualquier valor que contenga comillas dobles escapadas, asi que el patron queda en el indice CON EL NOMBRE VACIO -- o sea invisible en el PRIMER LOOKUP del escaneo de reutilizacion, que es justo el que existe para no reconstruir desde cero. Le pasaba a PAT-054 (se renombro para destrabarlo) y le sigue pasando a 4 regresiones del catalogo de QA (GAN-003, LP-003, OLV-008, KOI-016), dos de ellas perdiendo tambien el modulo -- y LP-003 es una de las reglas que los briefs de este proyecto citan. No se toco regresiones-manuales.yml porque es de QA. DOS PATRONES NUEVOS: PAT-055 (documento que declara su moneda y congela la cotizacion, con el total convertido persistido) y PAT-056 (chequeo oportunista al primer request del dia en vez de job programado, con la idempotencia en la base y no en el scheduler, y con la alternativa de hosting documentada en el codigo para que nadie "complete" el patron escribiendo el hosted service que se evito a proposito). DECISIONES QUE NECESITA JOAQUIN, ninguna bloquea el desarrollo y las tres bloquean el deploy: (1) el aviso de impacto de los egresos automaticos en el arqueo sigue sin darse y ahora hay un SEGUNDO camino que los genera (la confirmacion de un pago programado); (2) la formula fiscal de la compra sigue sin confirmarse contra una factura real suya y el ratioDescuento determina el costo que se persiste en el catalogo; (3) si la ferreteria paga con cheque propio diferido, que decide si el paso 7 (cartera) entra. Y UNA NUEVA: si en el futuro hacen falta jobs a hora fija, la decision es DE HOSTING (pool AlwaysRunning, Idle Time-out 0) y corresponde consultarla con olvidata-infra, no resolverla escribiendo un hosted service que el entorno no puede sostener. REINTENTOS: 4 -- (1) un heredoc de bash volvio a romper por las comillas, sexta vez en el proyecto, todo script de parcheo va por Write; (2) Producto no tiene propiedad Activo y las FK MarcaId/CategoriaId/ModeloId son obligatorias, el arnes fallo dos veces hasta leer la entidad y la base; (3) ValidateOnBuild fallo por UserManager faltante en el arnes; (4) el primer test del buscador de proveedores paso el termino por el parametro texto (filtro de columna) en vez de por SearchValue (buscador global), asi que el FALLA era del test y no del codigo -- se corrigio el test. Produccion y laplatense_qa_d9 sin tocar. Pendiente de verificacion de QA.

