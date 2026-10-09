# Memoria - Presupuestador

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-10-07 (v12 — cierre de calibracion PARCIAL de los 5 CR: falta el dato de horas reales, que solo aporta Joaquin. Hallazgo principal: el item "QA + fixes 2h" esta groseramente subestimado para un cambio de CARDINALIDAD (1:1 -> 1:N), que reabre criterios en todo el sistema; regla nueva de estimacion propuesta. Y el riesgo se declaro medio cuando correspondia alto)

## Definiciones vigentes

### Cierre de calibracion de los 5 CR + Entrega 5 (2026-10-07) — PARCIAL: falta el dato de horas reales

**Lo que falta y solo lo puede aportar Joaquin:** las **horas reales** de la ronda. El estudio no registra tiempo de reloj y ningun agente puede inferirlo — inventar un numero aca contaminaria el dataset que despues se usa para cotizar, que es exactamente el error que la instruccion 28 busca evitar. **Sin ese dato el cierre queda abierto**, y lo que sigue es lo que si se midio.

**Estimado:** 18,68 h PERT / **USD 392** para los 5 CR (fork de post-entrega, factor 2.5, sin descuento). La Entrega 5 no entra en esta cuenta: es el modulo 16 del WBS de Etapa 2 (9 h) + ~3 h residuales del modulo 6, ya cobradas desde el 2026-07-30.

#### El hallazgo de calibracion, y es el mas util de todo el cierre

**El item "ronda de QA + fixes: M = 2,0 h" esta groseramente subestimado para un cambio que altera la cardinalidad de un modelo**, y la autocorreccion lo **bajo** (de 2,5 a 2,0) anclandolo en el historico del proyecto. Eso fue un error de anclaje: los historicos de 2 h eran rondas sobre modulos **aditivos**, no sobre un cambio de 1:1 a 1:N.

**Lo que paso de verdad:** CR-01 y CR-02 cambiaron "una venta, un comprobante" por "una venta, N comprobantes", y eso **reabrio criterios en todo el sistema**. Se necesitaron **7 lotes de implementacion y 7 pasadas de QA**, y aparecieron **20 defectos** (`LP-037` a `LP-056`), de los cuales **cuatro fueron `major` y los cuatro eran el MISMO defecto**: un criterio de habilitacion replicado que divergio (anular, facturar por el camino legado, el combo de Editar, y el GET de la nota de credito). El contador de "lectores del dato" subio **tres veces** durante la ronda: 3 → 4 → 6.

**Regla de estimacion que sale de esto, para el proximo presupuesto:** cuando un item **cambia la cardinalidad de una relacion existente** (1:1 → 1:N, o un estado unico → varios), el costo no esta en construir la entidad nueva: esta en **barrer todos los lectores del criterio viejo**, y ese barrido **no se puede enumerar al cotizar** porque los lectores aparecen a medida que se tocan. Dos formas de cotizarlo, las dos honestas: (a) un item propio de "barrido de criterios" dimensionado por la **cantidad de lectores contados con un grep ANTES de cotizar** (el grep cuesta minutos y es el unico numero duro disponible), o (b) declarar el item como **rango abierto** con un gatillo de reestimacion explicito. Lo que no sirve es meterlo dentro de "QA + fixes" con el M de una ronda normal.

**Dato comparable para el dataset:** el presupuesto de la Entrega 3 ya habia sufrido una version de esto (18 h → 32,5 h, absorbidas por Joaquin), y la causa raiz que se registro entonces fue *"verificar que la base de reutilizacion EXISTE antes de cotizarla"*. **Esta ronda agrega la segunda causa raiz de desvio del proyecto, distinta de la primera:** no es que falte la base de reuse, es que **el alcance real de un cambio de cardinalidad es mas grande que la pieza que se nombra en el WBS**.

#### Lo que la ronda confirmo del metodo de cotizacion

- **El fork de post-entrega fue la clasificacion correcta** (factor 2.5, sin descuento de expansion): la instruccion 27 lo excluye explicitamente para sistema propio ya entregado, y cotizarlo como Build habria dado ~37% menos por un trabajo que resulto mas caro, no mas barato.
- **La regla anti-doble contingencia se aplico bien:** el 1.20 vive dentro de la formula y no se sumo el +15% de riesgo medio aparte.
- **La regla nueva de verificar que la base de reuse existe funciono en modo preventivo por primera vez:** las 10 piezas citadas de `marihogar` se confirmaron por `find`/`grep` antes de cotizar, y las 10 existian. Esa parte de la estimacion no desvio.
- **El riesgo se declaro "medio" y deberia haber sido "alto".** El criterio de la instruccion 28 para alto incluye "estados criticos": una venta que pasa a tener N comprobantes fiscales **es** eso. Con riesgo alto la contingencia habria sido +25% en vez de +15%.

#### Metricas de proceso de la ronda (insumo para las trazas, no para el precio)

| Dato | Valor |
|---|---:|
| Lotes de implementacion | 7 |
| Pasadas de QA | 7 (una se cayo por un stall y se reanudo) |
| Defectos encontrados | 20 (`LP-037` a `LP-056`) |
| De ellos, `major` | 4 — **los cuatro, el mismo patron** |
| De ellos, del instrumento de medicion y no del producto | 9 |
| Formas distintas de "falso verde" catalogadas en la ronda | 6 |
| Premisas falsas en briefs del orquestador | 6, que produjeron 3 reglas nuevas en la instruccion 39 |

**Lo que estas metricas dicen y conviene no perder:** **9 de los 20 defectos fueron del arnes de medicion, no del sistema.** Eso no es ruido: es el costo de construir el instrumento, y es trabajo real que ningun item del WBS contempla. Si la proxima ronda se cotiza igual, ese costo vuelve a caer fuera del presupuesto.

### Presupuesto de CR-01 a CR-05 (2026-10-06) — alcance NUEVO, fuera del WBS ya cobrado

**Lo primero, porque cambia cómo se lee todo lo demás:** estos 5 CR **no salen del WBS de Etapa 1 + Etapa 2**. Todo el plan de cierre de alcance (Entregas 3 a 6) declara "USD 0 de precio nuevo" porque cada módulo ya estaba aprobado y cobrado dentro de los USD 1.500. **Estos cinco no estaban.** Son capacidades que el cliente pidió el 2026-10-06, y dos de ellas **revierten exclusiones confirmadas por escrito** (cheques diferidos; y el alcance reducido del módulo 13). Son el gatillo de reestimación textual de la instrucción 28: *"cambio de alcance funcional"* y *"cambio de reglas de negocio"*.

#### Clasificación de la fórmula — fork de post-entrega, no Build

Se cotiza con **factor 2.5 / M × $16.80**, no con el factor 4.0 de Build, y **sin descuento de expansión agresiva ni de volumen**. No es una elección: la instrucción 27 lo dice en dos lugares distintos. *"Merge, 'modulo nuevo' post-entrega y el resto de Extras opcionales NO usan esta tabla ni el factor 4.0"*, y el descuento *"NO aplica a Mantenimiento anual, Extras opcionales (...módulo nuevo post-entrega...) ni a Merge sobre sistema propio ya entregado — esos se cotizan siempre a precio de lista, sin descuento: ahí está el margen real del negocio"*. La Platense es un sistema propio ya entregado y en producción desde 2026-08-24.

**Reglas de granularidad aplicadas (las dos, a la baja):**
- **Regla de granularidad (2026-07-03):** antes de anclar un ítem en los rangos de "módulo nuevo", verificar si es iteración evolutiva que reutiliza un patrón ya resuelto. Aplica a CR-02 (padre/hijos con pantalla de selección — el patrón de `OrdenCompra` + items ya está en el repo), CR-03 y CR-04. **No** se usó "ABM complejo 7,7-11,5h" para CR-02 por esto mismo.
- **Regla de segunda/tercera ronda (2026-07-08, labipac):** este proyecto ya tuvo varias rondas sobre el mismo sistema y reutiliza su propio AJAX, sus servicios y sus patrones visuales. Se usa el **piso** de la banda, no la mediana. Es lo que bajó CR-01 y CR-03 en la autocorrección de abajo.
- **Regla nueva del 2026-10-06 (que salió de este mismo proyecto):** verificar que la base de reutilización **existe** antes de cotizarla. Hecho por `find`/`grep` sobre `C:\Sistemas\marihogar`, archivo por archivo: `ComprobanteAfip`, `ComprobanteAfipItem`, `IComprobanteAfipService`, `Views/ComprobantesAfip/{Index,Create,Details}`, `Cheque`, `EstadoCheque`, `CuotaCheque`, `ChequeService`, `ConfiguracionCuotaTarjeta`, `TasaCostoCobranza`. **Todos confirmados.** Es el detonante de la regla (`ICatalogoMigracionService`, cotizado como 3h de reuse sin existir) aplicado por primera vez de forma preventiva.

#### Estimación PERT por ítem

| # | Ítem | O | M | P | PERT | Base de anclaje |
|---|---|---:|---:|---:|---:|---|
| 1 | **CR-05** Transferencia como medio de pago de venta | 0,3 | 0,5 | 1,0 | **0,55** | "Agregar campo simple / regla de negocio", piso. Valor de enum + mapeo a caja, sin migración |
| 2 | **CR-03** Interés por tarjeta × cuotas (catálogo de tarjetas, tabla con vigencia, pantalla de configuración, combo en la venta) | 1,8 | 2,5 | 4,0 | **2,63** | "ABM reutilizando servicios ya existentes" + la pantalla de Configuración ya existe. `RecargoCuota` queda intacto |
| 3 | **CR-01** Venta sin factura cobrada sin IVA (flag, motor de IVA, totales duales, bloqueo al confirmar) | 2,0 | 2,5 | 4,5 | **2,75** | "Agregar regla de negocio" + campo + migración. P alto a propósito: toca `VentaWorkflowService.ConfirmarAsync`, el método donde se midió LP-038 |
| 4 | **CR-02** Facturación parcial por ítems (comprobantes 1:N, pantalla de emisión, cargo de IVA en la CC del cliente) | 4,5 | 6,0 | 9,5 | **6,33** | Anclado en el paso 3 de la Entrega 3 (`OrdenCompra` + items + estados + Create/Details, 6,5h, "reuse alto, volumen real"): es el mismo patrón padre/hijos con pantalla de selección |
| 5 | **CR-04** Plan de echeqs 0/30/60/90/120 (líneas con número y banco, vencimiento calculado, listado, aviso por `PAT-056`) | 3,0 | 4,0 | 6,5 | **4,25** | El paso 7 de la Entrega 3 estimaba la cartera completa en 4,0h. Acá el alcance es **menor** (sin rechazo ni conciliación) y el agregado es el generador de plan |
| 6 | Ronda de QA + fixes | 1,5 | 2,0 | 3,5 | **2,17** | Histórico del proyecto (2,0h por ronda) |
| | **Total PERT** | | | | **18,68** | |

**Riesgo: medio (+15%), no alto.** Hay estados críticos y datos reales en producción, que empujarían a alto, pero los tres mitigantes son concretos y verificados: la migración es **aditiva sin un solo `DROP`**, el reuse está confirmado archivo por archivo, y no hay integración externa nueva (AFIP ya está codificado). **La contingencia se aplica UNA sola vez**, dentro de la fórmula `M × $16.80` (= M/2.5 × 1.20 × $35, donde el 1.20 **es** la contingencia): no se suma un 15% aparte. Regla anti-doble contingencia de la instrucción 28.

#### Autocorrección contra históricos (obligatoria, instrucción 28 §6)

Los comparables son del **mismo repo y el mismo proyecto**, que es el anclaje más fuerte posible — mejor que cualquier referencia cross-proyecto.

| Ítem | Referencia | Ratio | Ajuste aplicado |
|---|---|---:|---|
| CR-02 | Entrega 3 paso 3 (OC + items + estados + vistas): 6,5h | 0,97 | Ninguno (dentro de 0,85-1,15) |
| CR-04 | Entrega 3 paso 7 (cartera de cheques): 4,0h | 1,06 | Ninguno |
| CR-03 | Primera estimación 3,17h | 1,20 | **Bajado de M=3,0 a M=2,5** por la regla de segunda ronda (piso de la banda): la pantalla de Configuración y su patrón de grilla editable ya existen |
| CR-01 | Primera estimación 3,25h | 1,18 | **Bajado de M=3,0 a M=2,5**, mismo motivo. Se conservó el P alto (4,5) en vez de bajarlo: el riesgo real está en el método, no en el volumen |
| QA | Histórico 2,0h | 1,29 | **Bajado de M=2,5 a M=2,0** al histórico real del proyecto |

Las tres correcciones fueron **a la baja**, sumando −1,45h de PERT. Es coherente con la alerta de sobreestimación sistemática del dataset y con que las cuatro bases de reuse se verificaron antes de cotizar en vez de después.

#### Precio

| Concepto | Cálculo | USD |
|---|---|---:|
| Subtotal de lista | 18,68 h × $16,80 | **314** |
| Tokens IA (25% del subtotal de lista) | 314 × 0,25 | **78** |
| Descuento de expansión / volumen | no aplica a post-entrega sobre sistema propio | 0 |
| **Precio final** | | **USD 392** |

**Desglose a exponer al cliente** (Tokens IA ya distribuido dentro de cada línea, × 1,25 — nunca como línea aparte):

| Área funcional | USD |
|---|---:|
| Facturación parcial: elegir qué ítems de una venta se facturan | 133 |
| Pago a proveedores con echeq a 0/30/60/90/120 días | 89 |
| Venta con o sin factura (precio sin impuestos cuando no se factura) | 58 |
| Intereses de tarjeta de crédito configurables por tarjeta y cuotas | 55 |
| Pruebas funcionales y ronda de ajustes | 46 |
| Transferencia como medio de pago | 12 |
| **Total** | **393** |

(La diferencia de USD 1 con el precio final es redondeo por línea; se cobra **USD 392**.)

#### Lo que NO se cobra, y por qué se dice

- **LP-014** — **sin cargo, y ademas sin trabajo: verificado el 2026-10-06 que ya estaba cerrado desde el 2026-10-05 con PASS de QA** (ver `1-analista-funcional.md`, D-CR01.3). No afecta el precio (entraba en cero) pero si el calendario: el lote arranco con un item menos. Lo que sigue es el razonamiento original, que se mantiene porque la exigencia era correcta:
- ~~**LP-014** (cualquier usuario con `RequireVentas` puede vender a cualquier precio) — **sin cargo, es garantía.** Es un defecto propio abierto en producción, mismo criterio con el que el Sprint 0 absorbió D8 y D9. Entra **dentro** de esta ronda y no después: CR-01 le da al vendedor una palanca que baja el precio legítimamente, y sumarla sobre un agujero de precio sin control es amplificar un defecto en vez de agregar una capacidad.
- **Impuesto al cheque, impuesto por plataforma e impuesto por gasto** — v2, fuera de este presupuesto (D-CR04.2). Las entidades que se crean ahora se diseñan con lugar para esas alícuotas, así que agregarlas después es aditivo. Ese diseño preventivo ya está dentro de las horas de CR-03 y CR-04.
- **Costo real de cobranza y acreditación diferida de tarjeta** — declarados fuera del plan el 2026-10-06, con el efecto aceptado por escrito (la caja cuenta como ingreso del día plata de tarjeta que se acredita a 30 días).

#### Tier y perfil de cliente — por qué no se consultó a `olvidata-ceo`

El perfil es el del cliente chico/mediano típico del estudio (ferretería de barrio, proyecto cerrado en USD 1.500 en 3 pagos, PREMIUM año 1 gratis), así que **no se aparta** del caso para el que el criterio por defecto está calibrado y no se activa la regla de consulta por precio atípico. Lo que sí es atípico es otra cosa, y conviene decirlo: el 2026-10-06 Joaquín **absorbió** un desvío de 14,5h en la Entrega 3 (18h → 32,5h), con la instrucción de *"tener en cuenta estos casos de reestructuración a la hora de armar presupuestos"*. Este presupuesto es la primera aplicación de esa instrucción: **estos 5 CR no se absorben, se cotizan**, porque son alcance nuevo y no una reestimación de algo ya vendido.

#### Supuestos, exclusiones y dependencias

**Supuestos:**
- Las 4 decisiones del 2026-10-06 (D-CR01.1, D-CR01.2, D-CR04.1, D-CR04.2) se mantienen. Un cambio en D-CR01.1 (quién paga el IVA de una factura posterior) **reestima CR-01 y CR-02 juntos**: es lo que define si el total de una venta cerrada puede cambiar.
- La migración queda aditiva. Si apareciera una columna a reescribir, se reestima.

**Exclusiones:**
- Cartera de cheques (rechazo, reemplazo, conciliación de extracto).
- Los tres impuestos de v2.
- Cheques recibidos de clientes.
- Costo de cobranza y acreditación diferida de tarjeta.

**Dependencia dura, y es de calendario, no de plata:** **CR-02 tiene que construirse antes de habilitar AFIP.** Mientras no haya un CAE real emitido, pasar a comprobantes 1:N es aditivo y sin backfill; después de la primera factura real es una reconstrucción de datos sobre documentos fiscales. El certificado del cliente es el único gate pendiente de la Entrega 5 y puede llegar en cualquier momento. **Si el certificado llega antes de que CR-02 esté construido, hay que decidir cuál va primero** — y la respuesta barata es CR-02.

#### Gate

**Presupuesto EMITIDO, pendiente de aprobación.** No se inicia Implementación hasta que el cliente apruebe (gate duro de la instrucción 00). LP-014 es la única pieza que puede arrancar sin esa aprobación: es garantía, no alcance nuevo.

### Revision del plan contra el codigo real de `marihogar` (2026-10-05, v10)

**Origen:** instruccion de Joaquin — *"quiero que la logica de venta y pagos este hecha como esta en marihogar. tambien los proveedores y compras. marihogar es un proyecto que ya esta en produccion. copiar lo mas que se pueda de ahi."* Antes de implementar se leyo el codigo real de los dos proyectos, por entidad, servicio y vista. Lo que sigue **reemplaza la estimacion de la Entrega 3** y agrega una entrega nueva de Ventas/Pagos.

#### Hallazgo central: "copiar lo mas que se pueda" tomado literal seria destructivo

`marihogar` **no tiene** cuenta corriente de clientes (ni entidad `Cliente`: `Venta.ClienteNombre` es texto libre), **no tiene** IVA por linea (dos precios fijos por producto con el 21% incluido, hardcodeado en 4 puntos de `VentaService`), **no tiene** cantidades decimales (`VentaItem.Cantidad`, `OrdenCompraItem.Cantidad` y `Producto.StockActual` son `int`), **no tiene** unidades de medida ni conversion (0 hits de `UnidadMedida`/`FactorConversion`/`Bulto` en todo el repo) y **no tiene** cierre de caja (su `CajaService` es solo una agregacion del ledger).

La Platense es **mejor** en los cinco puntos y los cinco son requisitos reales de este cliente. Lo que `marihogar` si tiene y aca falta es **el ciclo de cobranza posterior al cierre de la venta** y **todo el modulo de compras**. Ese es el pedido real.

**Confirmacion que despeja la duda principal:** el estado `Confirmada` **no entra en conflicto con marihogar** — alla tampoco se exige factura para cerrar una venta. Su `EstadoVenta` (Pendiente/PagadaParcial/Pagada/Cancelada) no tiene ningun estado "Facturada"; el comprobante fiscal es una entidad aparte (`ComprobanteAfip`) que se emite despues y puede no existir nunca. El criterio del 2026-09-03 queda confirmado, no revisado.

#### Dos defectos de produccion encontrados en el analisis (verificados en el codigo, no reportados por QA)

| # | Defecto | Gravedad |
|---|---|---|
| **LP-014** | **Cualquier usuario con la politica `RequireVentas` puede vender a cualquier precio.** `VentasController.GuardarBorrador` (~147-156) pasa `PrecioUnitario` del payload del navegador al DTO y `VentaWorkflowService.GuardarBorradorAsync` lo persiste sin control de rol. `marihogar` tiene exactamente esa puerta (`esAdministrador` en `VentaService.ConfirmarAsync` 407-465 y `EditarAsync` 738-773: un Vendedor **siempre** recalcula desde el producto). Acoplamiento cero: se trae solo. **Abierto en produccion.** |
| **LP-015** | **Una venta con una linea de cuenta corriente de $1 se confirma y el remanente desaparece.** `VentaWorkflowService.ConfirmarAsync:486`: con cualquier pago de CC presente la verificacion de cobertura se desactiva entera (`pagosCC.Count == 0 && sumaPagos < venta.Total`), y el debito en CC es `pago.Monto` (linea 512), **no el remanente no cubierto**. Sale el stock, la plata no queda ni en caja ni en la deuda del cliente. Esta documentado como intencional, pero lo intencional era permitir fiado, no perder el remanente. **Abierto en produccion.** |

#### Entrega 3 — Proveedores y Compras: el presupuesto de 18h no es realista

Estimacion propia tras leer el codigo real: **42,5h M**, rango 38-46. Es **2,4x** el presupuesto vigente. Las tres razones, en orden de peso:

1. **El item 3.3 (importacion de listas de precios) esta estimado contra una base de reuse que no existe.** El WBS dice que reusa *"el contrato preview→confirmar de `ICatalogoMigracionService`"*. **Verificado: ese tipo no existe en ninguno de los dos repos** — nunca se construyo, pese a figurar como 3h de reuse en el WBS de Etapa 3. Y `marihogar` tampoco tiene importacion de listas: su `tools\ImportarHistorico` se declara en su propia primera linea como *"script de migracion de datos de UNA SOLA VEZ"*, y `AumentoMasivoPrecioService` es aumento por porcentaje a mano, no por archivo. Reuse real: **cero**. Sumado a que las dos listas de muestra reales de `Migracion/` **no comparten ninguna columna de codigo entre si** y una esta en `.XLS` antiguo que ClosedXML no lee, son ~10h por si solas: mas de la mitad del presupuesto completo del modulo.
2. **El anclaje "marihogar M12+M13" cubre menos de lo que el item 3.2 promete.** Lo que `marihogar` aporta de verdad —y ahi el reuse es genuinamente alto— es proveedores, OC con estados, CC de proveedores, pagos y cheques. Lo que **no** aporta, y el item 3.2 pide explicitamente: unidades de medida con conversion, impacto en el costo del producto (`RecibirAsync` **no toca** `Producto.PrecioCompra`), tipo de cambio propio, % de descuento por proveedor y codigo de proveedor por producto. Son cinco conceptos, ~7h, todos nuevos. Verificado por grep: `CodigoProveedor`, `TipoCambio`, `Moneda` y `Descuento` en `Proveedor` dan **0 hits** en `marihogar`.
3. **Dos deudas de infraestructura que el modulo activa y no estan presupuestadas.** (a) El ledger de caja de La Platense no tiene `EsReversion`, y los pagos a proveedores tienen varios caminos de reversion que lo necesitan — hoy `GastoService.AnularAsync` simula la reversion con un `Ingreso` sobre el mismo `OrigenId`, con lo cual **un gasto anulado es indistinguible de un ingreso real**. (b) No existe ledger de stock ni metodo delta: los unicos escritores de `Producto.Stock` son `VentaWorkflowService` (resta directa) y `AjusteStockService` (**SET absoluto**, que ademas fuerza `StockVerificado = true`), asi que un ingreso por compra no tiene donde dejar rastro. `marihogar` si tiene `MovimientoStock` + `IStockService` como unico escritor.

**Nota de reuse que aparece recien ahora:** `UnidadMedidaConversionService.ConvertirCompraAVenta` esta escrito, registrado en DI y **nunca llamado desde ningun lado** — su unico call site es `EsFactorConversionValido` en `ProductoService:444`. Compras es el consumidor que ese servicio estaba esperando desde que se construyo.

| # | Pieza | M (h) | Base |
|---|---|---:|---|
| 0 | Decision MH-034 + `EsReversion` en `CajaMovimiento` + discriminador de cuenta/medio + backfill + filtro en la grilla | 2,5 | Nuevo, acotado |
| 1 | `Proveedor` ampliado (CUIT, condicion IVA, contacto, domicilio fiscal, TC propio, % descuento, forma de pago) + romper `CatalogoSimpleServiceBase` + ABM + sidebar | 3,0 | Reuse alto |
| 2 | CC de proveedores (ledger + saldo acumulado por fila + pantalla) | 2,0 | Patron `MovimientoCCCliente`, ya en el repo |
| 3 | `OrdenCompra` + items + estados + Create/Details (1.170 lineas de vista, 460 de JS en marihogar) | 6,5 | Reuse alto, volumen real |
| 4a | Entrada de stock con conversion de unidad | 2,0 | **Sin precedente**: marihogar es `int` y tiene ledger; LP no tiene ninguno de los dos |
| 4b | Impacto en el costo del producto | 2,5 | **Sin precedente en marihogar** + decision de negocio |
| 4c | TC propio por proveedor + % descuento + moneda en la compra | 2,5 | **Sin precedente en marihogar** |
| 5 | Pagos de OC + egreso en caja + `ValidarPeriodoAbiertoAsync` + LP-002 | 3,5 | Reuse alto |
| 6 | Pagos programados + primer hosted service del repo | 2,0 | Ver riesgo de hosting abajo |
| 7 | Cheques (entidad, estados, acreditacion con fecha de extracto, cartera, job) | 4,0 | Reuse alto, volumen grande |
| 8 | **Importacion recurrente de listas de precios** | 10,0 | **Reuse cero** |
| 9 | Ronda de QA + fixes | 2,0 | Historico del proyecto |
| | **Total** | **42,5** | |
| | *Sin el item 8* | *32,5* | |

**Decision de alcance propuesta:** sacar el item 8 de la Entrega 3 y dejarlo como entrega propia con su propio relevamiento, empezando por pedirle al cliente dos o tres listas mas de proveedores reales para ver cuantos esquemas distintos hay. Con eso la Entrega 3 queda en 32,5h M — sigue siendo casi el doble de 18, pero es un bloque coherente, y el item mas riesgoso del plan deja de estar escondido dentro del modulo mas grande.

**Orden de port (cada paso compila, deploya y se prueba solo; nada toca lo que esta en produccion hasta el paso 5):** 0 discriminador de caja → 1 Proveedor + ABM → 2 CC de proveedores → 3 OC sin impacto (el paso mas grande y el mas seguro) → 4 `RecibirAsync` con conversion (primer paso que mueve datos reales) → 5 pagos + egreso en caja (**aca ya impacta el arqueo del cliente: avisarle antes**) → 6 pagos programados → 7 cheques → 8 importacion (aparte) → 9 QA.

#### MH-034: `marihogar` no lo resuelve — tiene el mismo problema

Hay que decirlo antes de cualquier decision de port. `MovimientoCCLocal` de `marihogar` **no tiene `MetodoPago` ni id de cuenta**, y no existe entidad `CuentaBancaria`, `Banco` ni `Conciliacion` en todo el repo. El medio de pago vive **solo en el texto libre de `Descripcion`** (`"Pago de orden de compra #44 (Transferencia)"`). Efectivo, transferencia, Mercado Pago, cheque y deposito caen todos en el mismo pozo. **Su modelo no es portable como solucion porque no hay solucion que portar.**

Lo que si vale traer, y es la parte barata:
1. **`EsReversion` en el ledger** + el calculo `ObtenerNetoPosteadoAsync` = `Egresos no-reversion − Ingresos reversion`, que es lo que impide reversar dos veces el mismo importe. Se vuelve obligatorio en cuanto entren pagos a proveedores.
2. **El choke point unico**: `EgresoPagoProveedorService` es el unico lugar que postea y revierte el egreso de un pago a proveedor, y usa **el mismo `OrigenTipo` y el mismo `OrigenId`** en los dos ledgers, asi que un pago se rastrea de uno al otro sin traduccion. Son ~80 lineas de runtime (las otras ~460 del archivo son backfill one-shot de marihogar, no se portan).
3. **La unica conciliacion que marihogar tiene**, que es manual y por documento: al acreditar un cheque se le **pide al usuario la fecha en que el banco debito**, leida del extracto. La medicion de su CR-86 es elocuente: usar la fecha del click acertaba 8 de 13 contra el extracto real; usar el vencimiento del cheque, 1 de 13.

**El costo es asimetrico y por eso conviene decidirlo ahora:** como paso 0 son ~2,5h M (una columna discriminadora + backfill por `OrigenTipo`/`Descripcion` + filtro en la grilla + partir el arqueo). Despues de que entren miles de pagos a proveedores, es un job de reconstruccion de datos sobre texto libre, con el arqueo del cliente sin conciliar en el medio.

#### Entrega nueva — Ventas y Pagos: traer el ciclo de cobranza de `marihogar`

No estaba en el WBS: el modulo 5 ("Ventas + CC clientes", 23h) se dio por cerrado y esta en produccion. Esto es alineacion de un modulo ya entregado, pedida explicitamente.

**Traer, en este orden (cada paso habilita al siguiente):**

| # | Pieza | Por que en este orden |
|---|---|---|
| 1 | **LP-014** gate de precio por rol | Agujero de seguridad abierto hoy. Acoplamiento cero |
| 2 | **`CancelarAsync`**: reversion de una venta ya cerrada (motivo, contramovimiento de stock, contramovimiento de caja **acotado a lo realmente posteado**, soft-delete de pagos pendientes, guard por Entrega/Comprobante) | Hoy **no existe ninguna anulacion**: `EstadoVenta.Anulada` esta en el enum pero ningun codigo la dispara. Un error de carga en una venta Confirmada en produccion es **irreparable**. Es el gap mas urgente despues del anterior |
| 3 | `PagoVentaId` + `EsReversion` + `UsuarioId` en `CajaMovimiento` | Precondicion de todo lo demas. Sin `PagoVentaId` no hay forma de revertir una linea de pago puntual: en una venta con dos pagos del mismo monto se revierte el equivocado — **es literalmente el defecto MH-027 que marihogar ya sufrio en produccion** |
| 4 | Saldo pendiente + sub-estado de cobranza derivado de Σpagos | Hoy no existe el concepto de "cuanto falta cobrar de esta venta" |
| 5 | `RegistrarPagoAsync` sobre una venta ya cerrada + `EliminarPagoAsync` con guard | Cerrada la venta no hay forma de cobrar el resto |
| 6 | **Entrega aparte, con presupuesto propio:** acreditacion diferida de tarjeta (+ job + notificacion) y costo real de cobranza con tasas vigentes | Es lo que mas plata mide y lo que mas tablas arrastra. Hoy la caja del dia cuenta como ingreso plata de tarjeta que entra a 30 dias |

**Como se compone con lo que ya hay, sin romperlo:** el estado de La Platense es la **etapa documental** (Borrador/Confirmada/Facturada/Anulada) y el de marihogar es el **grado de cobranza** (Pendiente/PagadaParcial/Pagada). No son excluyentes y **no se reemplaza un enum por el otro**: se conservan las 4 etapas y se agrega un sub-estado de cobranza derivado de Σpagos.

**Dejar como esta, sin tocar:** estado `Confirmada` (marihogar confirma el criterio), cantidad decimal + `UnidadVenta` por linea + conversion, IVA por linea con subtotal c/IVA editable que despeja el precio hacia atras (estrictamente mejor que el de marihogar, que deja el `PrecioUnitario` desactualizado), formula `(1-d+r)`, recargo de cuotas resuelto server-side que suma al total, cierre de caja diario/mensual, y toda la CC de clientes.

**Traer el criterio y no el codigo:** el flag `subtotalManual` de marihogar (que ningun recalculo pise un subtotal tipeado a mano) y su modelo *"`Subtotal` es la fuente de verdad, los `%` son traza"*.

#### Riesgo de regresion sobre datos reales — lo que NO se puede hacer

Produccion tiene la Entrega 2 completa desde 2026-08-24 con actividad real, 2.990 clientes y ~112.000 productos. **AFIP esta deshabilitado, asi que no hay ninguna venta `Facturada`: todo lo cerrado esta en `Confirmada`.**

- **`Ventas.Estado`** — `Confirmada=4` esta al final del enum **a proposito** ("para no reasignar los enteros ya persistidos en produccion", comentario literal en `EstadoVenta.cs`). Si se adoptara el enum de marihogar (`Pendiente=1/PagadaParcial=2/Pagada=3/Cancelada=4`), **cada venta Confirmada se leeria como Cancelada y cada Borrador como Pendiente**. Es el riesgo mas grave y el mas facil de cometer. Todo estado nuevo va al final, numerado explicito.
- **`ItemVenta.Descuento`/`Recargo`/`Subtotal`** — hay lineas persistidas con `(1-d+r)`. Si se pasara a cascada y algo recalculara subtotales, **el total de esas ventas cambiaria contra la caja y la CC ya posteadas**. Regla: en una venta cerrada, `Subtotal` es dato historico y no se recalcula nunca.
- **`ItemVenta.Cantidad`** (decimal 3 decimales), **`ItemVenta.UnidadVenta`**, **`Productos.Stock`** (decimal) — pasarlos a `int` trunca cantidades ya vendidas y descuadra el stock. Migracion destructiva, sin vuelta atras.
- **`PagosVenta.Monto`** — hoy `Monto` es la base y el recargo de cuotas se suma aparte al total y al ingreso de caja. Si se adoptara la convencion de marihogar (recargo embebido en el precio del item), cualquier conciliacion que sume `PagosVenta.Monto` **daria de menos exactamente el recargo**.
- **`MovimientosCCCliente`** — si se cambia el criterio de cuanto se debita (LP-015), los movimientos viejos quedan con una regla y los nuevos con otra. Lo correcto es exigir cobertura **de ahora en adelante** y **no** recalcular lo pasado.
- **`Ventas.CAE`** — pasar al modelo `ComprobanteAfip` 1:N (facturacion parcial + NC) es una migracion con backfill. Hoy es **barata** porque no hay ninguna factura real emitida; deja de serlo para siempre en cuanto se emita la primera.

#### Riesgo de hosting (pasos 6 y 7 de la Entrega 3)

La Platense **no tiene ni un hosted service** (verificado: 0 hits de `AddHostedService`) y corre en SmarterASP. `marihogar` usa `BackgroundService` + `PeriodicTimer` con hora fija (03:00/03:10 ART), que depende de que el application pool este vivo a esa hora. Con reciclado por inactividad, el job puede no correr nunca. Antes de portarlo: o se configura el pool como always-running, o se cambia el disparador por un chequeo oportunista al primer request del dia. **No es codigo, es una decision de hosting** — corresponde consultarlo con `olvidata-infra`.

#### Decisiones que requieren a Joaquin

1. **MH-034 / discriminador de caja**: decidirlo como paso 0 (~2,5h) o convivir con una caja sin conciliar. El costo es asimetrico.
2. **El remanente de una venta fiada (LP-015)**: debitar el remanente completo a la cuenta del cliente, exigir cobertura total, o dejarlo como hoy. *Recomendacion: debitar el remanente — es lo que el cliente realmente debe.*
3. **El CAE**: quedarse con 1 factura por venta, o pasar a `ComprobanteAfip` 1:N con facturacion parcial y notas de credito. **Barato ahora, caro para siempre despues de la primera factura real.**
4. **El recargo de cuotas**: *recomendacion: no tocar.* El modelo de La Platense es mejor y cambiar la convencion obliga a elegir entre migrar pagos ya posteados o convivir con dos lecturas.
5. **El costo del producto en la compra (item 4b)**: si una compra pisa `Producto.PrecioCompra`, y que pasa con el precio de venta cuando lo pisa. En La Platense esta minado: `PrecioCompra` es un campo manual **ya neto de bonificacion**, `Bonificacion` es **texto libre informativo** (`"33+5"`) que no participa de ningun calculo, y aguas abajo cuelgan `PorcentajeRecargo` → `PrecioVenta` → `PrecioOferta`.
6. **El factor de conversion por producto**: el XML-doc de `UnidadMedidaConversionService` marca como "a validar con el cliente" que el factor sea **fijo por producto**. Si el mismo producto llega en bultos de distinto tamaño segun el proveedor, el factor tiene que moverse a `CodigoProveedorProducto`. **Preguntarlo antes de escribir la migracion del paso 4, no despues.**
7. **Cheques (paso 7)**: confirmar si la ferreteria paga con cheque propio diferido. El presupuesto pide "echeck/transferencia", que no es necesariamente la cartera de cheques de marihogar (4h).
8. **El desvio de 18h a 32,5h (o 42,5h con importacion)**: el precio ya esta cobrado dentro de Etapa 1 y el plan declara USD 0 nuevo, asi que **no es un problema de precio sino de margen y de calendario**. Hay que decidir si se absorbe, si se renegocia el item 3.3, o si se recorta alcance (los candidatos naturales son cheques y pagos programados).


### Plan de cierre de alcance — Entregas 3 a 6 (2026-10-05)

**Que es:** la secuenciacion de lo que falta construir para cerrar el alcance completo del sistema. **No es un presupuesto nuevo.** Todos los modulos de abajo salen del WBS de Etapa 1 + Etapa 2 ya aprobado por el cliente el 2026-07-30 y **ya cobrado** dentro de los USD 1.500 (3 pagos) / USD 1.800 (12 pagos). Las horas son las M del WBS vigente, sin recotizar.

**Estado de partida (verificado contra el repo el 2026-10-05, rama `entrega-1-migracion`):** 17 controladores, 24 entidades. Construido y en produccion: catalogo, unidades/conversion, stock + ABC + ajustes, codigos de barras multiples, usuarios/roles, ventas Borrador→Confirmada→Facturada, CC de clientes **solo de consulta**, caja diaria/mensual, gastos, entregas, dashboard, configuracion de recargos, migracion de catalogo (112.485 productos + 2.990 clientes). `AfipService` esta codificado pero deshabilitado a proposito (sin certificado del cliente). `Proveedor` existe solo como catalogo simple minimo creado en Etapa 3 — sin ABM, sin sidebar, sin CC, sin compras. `EstadoVenta.Anulada` existe en el enum pero **ningun codigo la dispara**: no hay anulacion de ningun tipo.

#### Sprint 0 — Deuda abierta (prerequisito de todo lo demas, ~8h, SIN CARGO)

| # | Item | M (h) | Por que no se factura |
|---|---|---:|---|
| 0.1 | Deploy pendiente del commit `a6a78f0` + migracion EF `EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago` (tabla `RecargosCuota` + `PagosVenta.Nota`) | 0,5 | Entrega ya cerrada, nunca subida |
| 0.2 | **D8** — "Confirmar y facturar" no persiste el borrador antes de facturar | 1 | Defecto (garantia). **Bloqueante antes de cargar el certificado AFIP** |
| 0.3 | **D9** — `CajaMovimiento.Fecha`/`GastoService` mezclan `DateTime.Today` y `DateTime.UtcNow`: la venta de las 22:44 se lista como del dia siguiente | 1,5 | Defecto (garantia). **Definicion cerrada 2026-10-05**: dia de negocio = dia calendario en hora Argentina, mes de negocio = mes calendario cerrado el dia 1. Incluye verificar que el cierre mensual admita cerrar un mes anterior al actual |
| 0.4 | Correccion de datos: 87.542 de 112.485 productos (78%) migrados con `UnidadVenta = Metro` — modo correctivo del script, mismo patron que `--solo-codigo-propio` del 2026-09-02. **Regla cerrada 2026-10-05**: pasan en bloque a `Unidad` (el `METRO` del legado es su default basura — 2.898 de ellos se llaman a si mismos "Unidad de…" o "C/U…") + lista de 2.635 candidatos a corte por metro para marcar a mano | 2 | Consecuencia de Etapa 3 ya cobrada |
| 0.5 | **Cobro de CC de clientes** — pantalla de registro de pago + ajuste manual, con impacto en Caja. Hoy `RegistrarMovimientoAsync` lo llama solo `VentaWorkflowService`: los origenes `Pago`/`Ajuste` del enum no tienen camino desde la UI y el cobro del fiado se lleva por fuera del sistema | 3 | Gap de alcance ya entregado y cobrado (modulo 5 del WBS, "Ventas + CC clientes"). Una CC que no admite cobros esta incompleta, no es un modulo nuevo |
| | **Subtotal** | **8** | |

#### Entrega 3 — Proveedores + Compras (cierra Etapa 1 del presupuesto)

| # | Item | Base de reutilizacion |
|---|---|---|
| 3.1 | Ampliar `Proveedor` (CUIT, condicion IVA, TC propio, % de descuento, contacto, forma de pago habitual) + migracion EF **aditiva** + ABM propio con entrada de sidebar | La entidad ya existe como catalogo simple: se amplia, no se reemplaza (ver el XML doc de `Proveedor.cs`) |
| 3.2 | Compra con items, TC propio del proveedor, bonificacion, impacto en stock y en el costo del producto | `marihogar` M12+M13 |
| 3.3 | Importacion de listas de precios de proveedor (recurrente, distinta de la migracion de una sola corrida de Etapa 3) | Reusa `CodigoProveedorProducto` + el contrato preview→confirmar de `ICatalogoMigracionService` |
| 3.4 | CC de proveedores + pago con echeck/transferencia | Patron ledger de `MovimientoCCCliente`, ya construido |

**Total: 18h** (modulo 7 del WBS Etapa 1 — 13h reuse + 5h nuevo).

Gates abiertos: **ninguno**. Es el bloque mas grande que falta y el unico pendiente de Etapa 1 — arranca sin esperar nada del cliente.

#### Entrega 4 — Cuentas corrientes y consolidado

| # | Item | M (h) | Base de reutilizacion |
|---|---|---:|---|
| 4.1 | CC de empleados (autoservicio: cada empleado ve su sueldo y retiros, nunca los de un companero) | 4 | Patron ledger conocido (1h) + 3h nuevo |
| 4.2 | CC propia del negocio (consolidado de cierres de caja, ingresos y egresos) | 5 | `ganaderia` CajaService (2h) + 3h nuevo |
| | **Total (modulos 12 y 13 del WBS Etapa 2)** | **9** | |

Depende de la Entrega 3: la CC de proveedores entra al consolidado del negocio.

#### Entrega 5 — AFIP real + devoluciones/NC-ND + anulacion

| # | Item | Observacion |
|---|---|---|
| 5.1 | Habilitar facturacion electronica: certificado real del cliente, homologacion, primera factura real, verificacion del circuito posterior (descuento de stock, CC, caja) que nunca se probo en la practica | Residual del modulo 6 (~3h de las 7h), ya codificado y hardeado contra los 2 bugs reales de `marihogar`. **D8 tiene que estar corregido antes** |
| 5.2 | Devoluciones de mercaderia con reingreso de stock + NC/ND AFIP vinculada al comprobante original | `ShowroomGriffin` devoluciones |
| 5.3 | **Anulacion de venta — cambio de alcance real respecto de `1-analista-funcional.md` §6.5** | Ver nota de abajo |

**Total: 12h** (modulo 17 del WBS = 9h + ~3h residuales del modulo 6).

**Nota de alcance (la unica pieza del plan que se aparta del diseno aprobado):** §6.5 definia la anulacion como "transicion `Facturada`→`Anulada` disparada por la emision de una NC, sin anulacion silenciosa sin comprobante fiscal". Ese diseno es de antes del 2026-09-03, cuando `Confirmada` paso a ser la forma normal de cerrar una venta sin factura. Hoy la mayoria de las ventas reales nunca llegan a `Facturada`, asi que hacen falta **dos caminos**: anular una `Confirmada` (reversa de stock, caja y CC, **sin** comprobante fiscal — caso que el diseno original no preveia) y anular una `Facturada` (por NC AFIP, como estaba definido). No agrega horas al modulo 17; cambia su diseno.

Gates abiertos: **solo el certificado AFIP del cliente** (sin el, 5.1 y 5.2 no se pueden cerrar). La pregunta abierta 7 quedo cerrada el 2026-10-05: **anula el Administrador o el usuario que creo la venta** (un vendedor solo sus propias ventas, validando `UsuarioId`; el repartidor no anula), **sin limite de tiempo propio del sistema** — el unico tope real es el que imponga AFIP para la NC de una venta ya facturada.

#### Entrega 6 — Herramientas comerciales

| # | Item | M (h) | Base de reutilizacion |
|---|---|---:|---|
| 6.1 | Presupuestos y cotizaciones en PDF | 8 | `marihogar` M4, reuse total |
| 6.2 | Aumento masivo de precios por categoria / proveedor / marca | 4 | `marihogar` / `ShowroomGriffin`, reuse total |
| | **Total (modulos 14 y 16 del WBS Etapa 2)** | **12** | |

Sin dependencias de ninguna otra entrega ni del cliente. Es la valvula de escape del plan: si el certificado AFIP se demora, esta entrega se adelanta sin romper nada.

#### Resumen y orden recomendado

| Bloque | M (h) | Gate | Precio |
|---|---:|---|---|
| Sprint 0 — deuda abierta | 8 | **ninguno** (las 2 definiciones se cerraron el 2026-10-05) | sin cargo |
| Entrega 3 — Proveedores + Compras | 18 | ninguno | ya cobrado (Etapa 1) |
| Entrega 4 — CC empleados + CC negocio | 9 | Entrega 3 | ya cobrado (Etapa 2) |
| Entrega 6 — Presupuestos PDF + aumento masivo | 12 | ninguno | ya cobrado (Etapa 2) |
| Entrega 5 — AFIP + devoluciones + anulacion | 12 | **solo el certificado AFIP** (la pregunta abierta 7 se cerro el 2026-10-05) | ya cobrado (Etapas 1 y 2) |
| **Total restante** | **59** | | **USD 0 de precio nuevo** |

**Orden:** Sprint 0 → E3 → E4 → E6, con E5 insertandose en cuanto llegue el certificado del cliente (no bloquear la secuencia esperandolo). Las 51h del WBS mas las 8h de Sprint 0 cierran el 100% del alcance comprometido: al terminar E5 no queda ningun modulo del presupuesto sin construir.

**Lo que este plan deja deliberadamente afuera** (no esta comprometido ni cotizado): cambios/canjes de mercaderia, integracion con balanzas o ticketeadora de etiquetas, las 217 fichas de clientes reales distintos bajo un mismo CUIT descartadas por el dedupe (decision de Joaquin del 2026-09-28: se cargan a mano cuando aparezcan), y ABM de pantalla para codigos alternos / codigos de proveedor (hoy solo lectura, por decision de alcance).

**Decisiones bloqueantes: las 3 quedaron cerradas el 2026-10-05.** Detalle y evidencia en `1-analista-funcional.md`, seccion "Decisiones del cliente del 2026-10-05". Resumen: (1) dia de negocio = dia calendario en hora Argentina, mes = mes calendario cerrado el dia 1 sobre el mes anterior; (2) anula el Administrador o el usuario que creo la venta, sin limite de tiempo propio del sistema; (3) `UnidadVenta`: el cliente respondio "no se", se resolvio midiendo la base — los 87.542 `Metro` pasan a `Unidad` en bloque y se marcan a mano los 2.635 candidatos reales a corte. **El plan no tiene mas gates que el certificado AFIP de la Entrega 5.**

#### Anclaje de reutilizacion — instruccion de Joaquin del 2026-10-05

Todo lo que falta **se toma de `marihogar`** (`C:\Sistemas\marihogar`), no se disena de cero: AFIP, notas de credito, circuito de ventas, presupuestos, aumento masivo, proveedores, compras y pagos de compras. Verificado que el precedente existe archivo por archivo:

| Pieza del plan | Origen en `marihogar` |
|---|---|
| E5 — AFIP + NC/ND | `ComprobanteAfipService.cs`, `AfipService.cs`, `TipoComprobanteAfip.cs`, migracion `20260821143237_AddNotaCreditoAfip`, `ComprobantesAfipController.cs` |
| E5 — circuito de ventas / anulacion | `VentaService.cs`, `PagoVentaService.cs`, `VentasController.cs` |
| E3 — Proveedores | `ProveedorService.cs`, `ProveedoresController.cs` |
| E3 — Compras | `OrdenCompraService.cs`, `OrdenesCompraController.cs` |
| E3 — Pagos de compras | `PagoOrdenCompraService.cs`, `EgresoPagoProveedorService.cs`, `PagoOrdenCompraVencimientoHostedService.cs`, `ChequeService.cs` (echeck/diferidos) |
| E3 — CC de proveedores | `CCProveedorService.cs` |
| E4 — CC propia del negocio | `CCLocalService.cs` + `CCLocalController.cs` (**precedente directo, mejor que el `CajaService` de `ganaderia` que asumia el WBS**) |
| E6 — Presupuestos PDF | `PresupuestoService.cs`, `PresupuestosController.cs` |
| E6 — Aumento masivo | `AumentoMasivoPrecioService.cs`, `AumentoMasivoPreciosController.cs` |

Efecto sobre las horas: **ninguno a la baja todavia**. Las M del WBS ya estaban ancladas en `marihogar` (modulo 7 = `marihogar` M12+M13, modulo 14 = M4, modulo 16 = reuse total), asi que esta confirmacion valida la estimacion en vez de reducirla. La unica mejora real es la CC del negocio (item 4.2), que pasa de "3h nuevas sobre `ganaderia`" a tener precedente directo — se refleja en el cierre de calibracion, no en una recotizacion.


### Etapa 3 — Presupuesto real (2026-08-17), reemplaza la referencia provisional

**Contexto:** la referencia histórica (v2/v3 de este documento, ver Historial) era una hipótesis de trabajo: ~17.000 filas migradas desde un archivo Excel de formato desconocido, con 25% de riesgo declarado por esa incertidumbre — nunca se cotizó en firme. Con el backup real de SQL Server analizado (`1-analista-funcional.md`, `2-disenador-funcional.md` flujo 10, `3-arquitecto-mvc.md`), el volumen real es **121.691 artículos activos (7x el supuesto)** pero el riesgo de "formato desconocido" queda resuelto — el esquema, las reglas de deduplicación y el origen de ventas para ABC ya están definidos con datos reales, no quedan por descubrir. El alcance también creció respecto de la hipótesis original: ya no es "solo migrar filas", incluye clasificación ABC automática por ventas y extensión de `Producto`/`Cliente` con los gaps confirmados.

**WBS (Working Breakdown Structure) por ítem:**

| # | Ítem | M (h) | Base de reutilización |
|---|---|---:|---|
| 1 | Extracción/limpieza batch (dedup nombre 2 niveles, dedup `articuloProveedor` por última importación conciliada, exclusiones, ABC inicial por Pareto) | 8 | Sin precedente exacto — reglas de negocio específicas de este dataset, 100% desarrollo nuevo |
| 2 | `CodigoProveedorProducto` (entidad + config EF) | 2 | Patrón de catálogo simple ya resuelto en Entrega 1 (Marca/Modelo/Categoria) — 2h reuse |
| 3 | `ICatalogoMigracionService` (import preview→confirmar, idempotente) | 3 | Mismo contrato que `IListaPreciosProveedorImportService` de Entrega 2 — 3h reuse |
| 4 | `IClasificacionAbcAutomaticaService` (cálculo Pareto sobre `ItemVenta` + UI de sugerencia) | 5 | Sin precedente exacto — desarrollo nuevo |
| 5 | Extensión `Producto`/`Cliente` (6 campos: Bonificacion, ClasificacionABCSugerida, Domicilio, Localidad, Email, Notas) + migración EF | 3 | Modificación sobre módulo existente — desarrollo nuevo pero de bajo riesgo (campos simples) |
| 6 | Reporte de excepciones (pantalla informativa, sin persistencia propia) | 2 | Sin precedente exacto — desarrollo nuevo |
| 7 | Carga real de datos a producción (ejecución del batch, validación contra el reporte de excepciones, iteración con Joaquín) | 4 | Sin precedente exacto — operación puntual de este proyecto |
| | **Subtotal** | **27** | |

**Cálculo de reutilización (R):** horas ancladas en reuse directo = ítems 2+3 = 5h. Horas de desarrollo nuevo = 22h. **R = 5/27 = 18,5% → Tier 3 (R < 40%): 0% de descuento** — coherente con que esta es una ampliación sobre un sistema ya entregado (`27-presupuesto-parametros.instructions.md`: "Merge sobre sistema propio ya entregado... se cotiza siempre a precio de lista, sin descuento"), no un Build inicial de cliente nuevo.

**Riesgo declarado (cualitativo, no aplicado como % ciego sobre la fórmula):** clasificado como riesgo **Alto** por tratarse de migración de datos legado con inconsistencias reales medidas (ver Análisis: 49% del historial de importaciones de proveedor sin conciliar, 3.612 grupos de duplicados que requieren regla heurística). El riesgo ya está incorporado en el M de cada ítem (especialmente el ítem 1, estimado en el techo realista de su banda) en vez de aplicarse como un multiplicador adicional sobre el total — evita doble contingencia.

**Cálculo económico (fórmula vigente, `27-presupuesto-parametros.instructions.md`):**

| Concepto | USD |
|---|---:|
| Subtotal (lista, 27h × $16,80) | 453,60 |
| Tokens IA (25% del subtotal de lista) | 113,40 |
| Descuento Tier 3 (0%) | 0,00 |
| **Precio final Etapa 3** | **≈ 567,00** |

**Comparación con la referencia histórica (v2/v3, nunca cotizada en firme):** el número sube frente al rango provisional anterior (USD 315-394) pese a que se resolvió el riesgo de formato desconocido, porque (a) el volumen real es 7x el supuesto original y (b) el alcance funcional creció (ABC automática + extensión de Producto/Cliente + reporte de excepciones no estaban en la hipótesis original de "solo migrar filas"). No es una subida de criterio de precio, es un presupuesto real sobre un alcance mejor definido y más amplio que la hipótesis de trabajo anterior.

**Este número queda pendiente de aprobación de Joaquín antes de pasar a Implementación de Etapa 3** — mismo gate que Entregas 1 y 2 ("No iniciar Implementación sin Presupuesto aprobado por el cliente", `00-operativa-global.instructions.md`).

### Código de barras múltiple por producto — Presupuesto (2026-08-21)

**Contexto:** hallazgo real post-migración (ver `1-analista-funcional.md` §10) — 4.371 de 23.197 artículos con código de barras tienen más de uno real (variantes de fábrica agrupadas bajo un mismo producto interno), y el modelo actual los descarta a todos por "ambiguos". Es una **corrección/ampliación puntual sobre un módulo ya entregado** (Código de barras, Etapa 1 módulo 11) — mismo criterio de clasificación que el resto del trabajo de esta sesión sobre Producto (recargo/oferta, baja en lote, restablecer contraseña): "Merge sobre sistema propio ya entregado", sin descuento de expansión aplicable (`27-presupuesto-parametros.instructions.md`).

| # | Ítem | M (h) | Base de reutilización |
|---|---|---:|---|
| 1 | Entidad `CodigoBarrasProducto` (Domain + EF config) | 1 | Patrón idéntico a `CodigoProveedorProducto` (Etapa 3) — reuse directo |
| 2 | Migración EF (tabla nueva, aditiva) | 0,5 | — |
| 3 | Extensión `ICodigoBarrasLookupService` (buscar en `Producto.CodigoBarras` OR `CodigoBarrasProducto`) | 1 | Servicio ya existente, solo amplía la condición del `WHERE` |
| 4 | Extensión del script `tools/MigracionCatalogo` (backfill de los códigos alternos perdidos para los 4.371 artículos) | 1,5 | Reutiliza la lógica de resolución de ganador y lectura `Tipo='B'` ya construida — solo cambia el destino de escritura |
| 5 | Ficha de Producto: sección de solo lectura "Otros códigos de barras válidos" | 0,5 | — |
| | **Subtotal** | **4,5** | |

**Cálculo económico:**

| Concepto | USD |
|---|---:|
| Subtotal (lista, 4,5h × $16,80) | 75,60 |
| Tokens IA | 0,00 (no aplica — 2,16h facturables, bajo el umbral de 4h de `27-presupuesto-parametros.instructions.md`) |
| Descuento por Tier | 0,00 (no aplica — merge sobre sistema ya entregado) |
| **Precio de lista** | **≈ 76** |

**Nota de criterio (para que Joaquín decida, no una recomendación cerrada):** este hallazgo salió de la misma investigación que ya se venía haciendo por el reclamo original del cliente sobre el código de barras mal migrado (mismo módulo, mismo día) — es defendible tratarlo como continuación de esa corrección ya en curso (sin cargo adicional), en vez de un ítem nuevo a cobrar. Ambos caminos son razonables; queda a criterio comercial de Joaquín, no es una decisión técnica.

### WBS funcional vigente

**Etapa 1 (MVP operable — lo mínimo para reemplazar el manejo manual del día a día)**

| # | Módulo | M (h) | Base de reutilización |
|---|---|---:|---|
| 1 | Usuarios y roles (admin/vendedor/repartidor, repartidor ve todas las entregas) | 5 | `marihogar` M10 (4h) + 1h nuevo |
| 2 | Catálogo de productos (desc./IVA config./marca/modelo) | 9 | `marihogar` M2 (8h) + `ShowroomGriffin` (Marca/Modelo) + 1h nuevo |
| 3 | Unidades de medida y conversión compra↔venta | 5 | Sin precedente exacto — 100% desarrollo nuevo |
| 4 | Stock + alertas + puesta a punto de stock inicial (ajuste manual, flag negativo, ABC) | 8 | `marihogar` M3 (6h) + `ShowroomGriffin` ajuste manual (1h) + 1h nuevo |
| 5 | Ventas + CC clientes (recargo cuotas + workflow Borrador→Facturada) | 23 | `marihogar` M5+M11 (17h) + 6h nuevo |
| 6 | Facturación AFIP (Factura) | 7 | `marihogar`/`delicias-naturales`, reuse total |
| 7 | Proveedores + compras (TC propio + % desc. + importación de listas) | 18 | `marihogar` M12+M13 (13h) + 5h nuevo |
| 8 | Caja (cierre diario + mensual, punto de venta único) | 7 | `marihogar` M15 (4h) + 3h nuevo |
| 9 | Gastos varios (caja chica/mensual) | 4 | `marihogar` M18 (3h) + 1h nuevo |
| 10 | Dashboard — "foto completa del negocio" (3 niveles, prioridad de diseño confirmada) | 12 | `marihogar` M9 (6h) + 6h nuevo |
| 11 | **Código de barras — vinculación al producto + lectura en venta (SIMPLIFICADO — la ticketeadora es manual, no se integra)** | 3 | Buscador de venta (1h, mismo proyecto) = 1h reuse + 2h nuevo (campo único + lookup por código) |
| | **Subtotal Etapa 1** | **101** | |

**Etapa 2 (alcance complementario)**

| # | Módulo | M (h) | Base de reutilización |
|---|---|---:|---|
| 12 | Cuenta corriente de empleados (autoservicio) | 4 | Patrón ledger conocido (1h) + 3h nuevo |
| 13 | Cuenta corriente propia del negocio (consolidado) | 5 | `ganaderia` CajaService (2h) + 3h nuevo |
| 14 | Presupuestos y cotizaciones en PDF | 8 | `marihogar` M4, reuse total |
| 15 | Entregas a domicilio (markup + propia/tercerizada) | 8 | `marihogar` M6 (6h) + 2h nuevo |
| 16 | Aumento masivo de precios (cat./proveedor/marca) | 4 | `marihogar`/`ShowroomGriffin`, reuse total |
| 17 | Devoluciones de mercadería + Notas de crédito/débito AFIP | 9 | `ShowroomGriffin` devoluciones (3h) + extensión AFIP (1h) + workflow anulación (1h) = 5h reuse + 4h nuevo |
| | **Subtotal Etapa 2** | **38** | |

*Nota: "Cheques (30/60/90 días)" sigue sin presupuestarse como módulo aparte — se absorbe como campo de forma de pago dentro del módulo 7.*

### Migración de catálogo — RETIRADA de este presupuesto (2026-07-30)

Se saca como etapa del presupuesto actual, a pedido explícito de Joaquín. Motivos:
1. El problema real que la motivaba —el cliente no tiene stock confiable hoy— ya queda resuelto por el módulo 4 (puesta a punto de stock inicial), que es **independiente** de si el catálogo se migra por archivo o por acceso a base de datos.
2. Joaquín va a hacer un **segundo relevamiento tras la aprobación de este presupuesto**, para evaluar acceso directo a la base de datos del sistema actual del cliente — de lograrlo, el costo real de importación bajaría al mínimo comparado con mapear un archivo Excel de formato desconocido (que era la hipótesis de trabajo de la versión anterior de este documento, ~15h / USD 394 provisional).
3. Se cotiza en una fase posterior, separada de este presupuesto, con datos reales (acceso a BD o archivo confirmado) en mano — no tiene sentido fijar un precio ahora sobre una incertidumbre que está a punto de resolverse con información mejor.

*Referencia histórica (v2/v3 de este documento): la estimación anterior era 12h de migración base + 3h de extensión para conteo real = 15h, Tier 3 (0% descuento) + 25% de riesgo declarado = USD 394 provisional. Queda como ancla de referencia si la fase futura termina dependiendo igual de un archivo Excel; si hay acceso a base de datos, se espera un costo bastante menor.*

### Estimaciones PERT por item

M anclado en calibración histórica de `marihogar` (rubro más cercano). El módulo de código de barras quedó reducido a lo mínimo tras confirmarse que la ticketeadora es manual: solo vincular el código al producto y resolverlo en la búsqueda de venta — sin generación/impresión de etiquetas.

### Tasa vigente y contingencia aplicada

- Tasa vigente: USD 35/h. Fórmula de lista: `Costo módulo = M × $16.80`.

### Cálculo de reutilización (R) y Tier aplicable — Etapa 1 + Etapa 2

| | Horas |
|---|---:|
| Total M (Etapa 1 + Etapa 2) | 139h |
| Horas ancladas en reuse directo | 97h |
| Horas de desarrollo genuinamente nuevo | 42h |

**R = 97 / 139 = 69,8%** → **Tier 2 (40% ≤ R < 70%): 15% de descuento**, por 0,2 puntos porcentuales.

**Nota de transparencia (caso límite):** al simplificar el módulo de código de barras (7h→3h), el ratio combinado subió de 68,5% a 69,8% — a un pelo del umbral de Tier 1 (70%). Es, literalmente, un caso al límite: la clasificación reuse/nuevo de una sola hora en cualquier módulo podría inclinarlo a un lado u otro. Se aplica Tier 2 por el criterio estricto (R < 70%), pero se deja constancia de que es una zona gris, no un resultado robusto.

Gatillo económico: tablero de ciclos económicos en verde/consolidación a la fecha (2026-07-30) → Tier 2 habilitado sin restricción.

### Resumen economico (con Tokens IA como item individual) — precio según fórmula/política vigente

| Concepto | USD |
|---|---:|
| Subtotal Etapa 1 (lista, 101h × $16.80) | 1.696,80 |
| Subtotal Etapa 2 (lista, 38h × $16.80) | 638,40 |
| **Subtotal desarrollo (sin Tokens IA, sin descuento)** | **2.335,20** |
| Tokens IA (25% del subtotal de lista) | 583,80 |
| Descuento Tier 2 (15% del subtotal de lista) | −350,28 |
| **Precio real Etapa 1 + Etapa 2 (antes de referido)** | **≈ 2.568,72** |
| Descuento por referido (15%) | −385,31 |
| **Precio según fórmula/política vigente** | **≈ 2.183** |

### Precio final a cobrar — estructura de dos modalidades de pago (override comercial de Joaquín, 2026-07-30)

Joaquín definió el precio final del proyecto como **dos modalidades de pago**, ambas por debajo de los ≈USD 2.183 que da la fórmula/política estándar — no es un ajuste de la política de Tier ni del referido, es un precio de cierre puntual para este cliente, con un incentivo por pago más concentrado:

| Modalidad | Total USD | Cuotas |
|---|---:|---|
| Pago en hasta 3 pagos | **1.500** | ej. 3 × USD 500 |
| Pago en hasta 12 pagos | **1.800** | ej. 12 × USD 150 |

La diferencia entre ambas (USD 300, ≈16,7%) es el incentivo por elegir la modalidad de pago más corta — más cobro concentrado y menos riesgo de cobranza a lo largo de 12 cuotas.

Split por etapa (misma proporción de horas, 101h:38h ≈ 72,7%:27,3%) — referencia interna, no se expone al cliente con este detalle dado que ahora se cotiza como total del proyecto con modalidad de pago, no por etapa:

| Etapa | USD (si 1.500) | USD (si 1.800) |
|---|---:|---:|
| Etapa 1 | 1.090 | 1.308 |
| Etapa 2 | 410 | 492 |

### Chequeo de margen real con los números propios de Joaquín (ambas modalidades)

Joaquín estima el proyecto en **30 horas reloj reales + USD 200 de tokens IA** → piso de referencia a tasa objetivo (USD 35/h): 30×35 + 200 = **USD 1.250**.

| Concepto | Modalidad 3 pagos (1.500) | Modalidad 12 pagos (1.800) |
|---|---:|---:|
| Precio a cobrar | 1.500 | 1.800 |
| Margen sobre el piso de referencia (1.250) | 250 (≈20%) | 550 (≈30,6%) |
| Tasa efectiva realizada: (precio − 200) / 30h | **≈ USD 43,3/h** | **≈ USD 53,3/h** |

**Conclusión:** ambas modalidades quedan por encima del objetivo de USD 35/h — incluso la opción de 3 pagos (la más barata) deja margen saludable según la propia estimación de esfuerzo real de Joaquín. El incentivo por pago corto no compromete la rentabilidad del proyecto en ninguno de los dos casos.

### Total del proyecto (Etapa 1 + Etapa 2 — la migración queda fuera, se cotiza aparte más adelante)

| Modalidad | Total USD |
|---|---:|
| Hasta 3 pagos | 1.500 |
| Hasta 12 pagos | 1.800 |

*Nota histórica: la versión anterior de este documento (con ticketeadora integrada, 7h) daba Total ≈ USD 2.246 según fórmula. Con el módulo simplificado (3h) la fórmula bajaba a ≈USD 2.183; Joaquín estructuró el precio final como dos modalidades de pago (USD 1.500 / USD 1.800) en vez de un único número, con el respaldo del chequeo de margen de arriba.*

### Costo real de producción vs. precio cobrado (actualizado)

USD 200 de tokens IA reales quedan cubiertos en ambas modalidades — el chequeo relevante es el de arriba (30h reales + USD 200 tokens vs. USD 1.500 o USD 1.800 cobrados), que confirma tasas efectivas de USD 43,3/h y USD 53,3/h respectivamente, ambas saludables sobre el objetivo de USD 35/h.

### Mantenimiento anual — actualizado (2026-07-30)

Se simplifica a un único plan: **PREMIUM** desde el arranque (coherente con que el sistema completo, Etapa 1+2, supera ampliamente las 15 tablas del rango PRO). Año 1 sin costo, año 2 en adelante a precio de lista.

| Momento | Plan | USD/año |
|---|---|---:|
| Año 1 | PREMIUM | Sin costo |
| Desde año 2 | PREMIUM | 500 |

*Reemplaza la estructura anterior (PRO gratis año 1 → PREMIUM USD 500 desde Etapa 2) — ya no hay transición de plan, es PREMIUM desde el día uno, con el año 1 regalado como parte del cierre comercial.*

### Calibraciones historicas usadas

- `marihogar/definiciones/4-presupuestador.md`: fuente principal de M-hour por módulo.
- `delicias-naturales`: referencia conceptual para `UnidadMedida`.
- `ganaderia`: referencia de `CajaService`/`EgresoService`.
- `vinosefue`: referencia de `MovimientoCCProveedor`.
- `ShowroomGriffin`: referencia de `Marca`/`Modelo`, aumento masivo de precios, devoluciones de mercadería, y ajuste manual de stock.
- `contadores-bma-conversor`: referencia para cuando se cotice la migración de catálogo en su fase futura (retirada de este presupuesto).

### Cierre estimado vs real (si disponible)
Pendiente — proyecto en etapa de presupuesto, aún no iniciado.

## Historial de ajustes
- 2026-08-21: agregado presupuesto de "Código de barras múltiple por producto" — hallazgo real (4.371 artículos con más de un código de barras real, descartados hoy como ambiguos). WBS de 5 ítems, 4,5h, sin Tokens IA (bajo umbral de 4h facturables) ni descuento de Tier (merge sobre sistema ya entregado). Precio de lista ≈ **USD 76**. Pendiente de aprobación de Joaquín antes de Implementación.
- 2026-08-17 (v7): Presupuesto real de Etapa 3 (migración de catálogo) — reemplaza la referencia provisional de v2/v3 (USD 315-394, nunca cotizada en firme). WBS de 7 ítems, 27h, R=18,5% → Tier 3 (0% descuento) — coherente con ser una ampliación sobre sistema ya entregado, no un Build inicial. Precio final ≈ **USD 567** (453,60 lista + 113,40 Tokens IA). Sube frente a la referencia anterior pese a resolverse el riesgo de formato desconocido, porque el volumen real (121.691 activos) es 7x el supuesto y el alcance creció (ABC automática + extensión Producto/Cliente + reporte de excepciones). Pendiente de aprobación de Joaquín antes de Implementación — mismo gate que Entregas 1/2.
- 2026-07-30: Presupuesto interno v1 — WBS de 16 módulos (126h totales), R=73% → Tier 1, precio real de desarrollo ≈ USD 2.011.
- 2026-07-30: Aplicado 15% de descuento por referido sobre el costo real → USD 1.709.
- 2026-07-30: Analizado el consumo estimado de USD 200 en tokens IA contra el precio final — cubierto con margen por la línea de Tokens IA existente.
- 2026-07-30 (v2 — respuestas del cliente): confirmada anulación de venta facturada por NC + devoluciones sin cambios (nuevo módulo, Etapa 2); migración confirmada en ~17.000 productos, formato aún no recibido, promovida a Etapa 3 independiente (USD 315 provisional); dashboard ampliado (prioridad de diseño); confirmado punto de venta único y repartidor con visibilidad total. R de Etapa 1+2 bajó de 73% a 70,9% (Tier 1, más ajustado). Total con las 3 etapas ≈ USD 2.133.
- 2026-07-30 (v3 — plan de stock inicial): Stock ampliado (6h→8h) con ajuste manual/ABC/flag negativo, reutilizando patrón `ShowroomGriffin`; Etapa 3 sumó extensión del importador para conteo real (12h→15h). R de Etapa 1+2 bajó a 70,6% (sigue Tier 1, colchón mínimo). Total con las 3 etapas ≈ USD 2.239.
- 2026-07-30 (v4 — código de barras + retiro de la migración como etapa): (a) agregado el módulo "Código de barras — etiquetado con ticketeadora + lectura en venta" (7h, Etapa 1) — el cliente tiene ticketeadora física y códigos propios/de fábrica; (b) **retirada la migración de catálogo de este presupuesto** — el problema de stock que la motivaba ya está resuelto por el módulo de stock ampliado, y Joaquín va a evaluar acceso a la base de datos real en un segundo relevamiento antes de cotizar esa fase por separado. **Efecto combinado: R de Etapa 1+2 bajó de 70,6% a 68,5% — el proyecto pasa de Tier 1 (30%) a Tier 2 (15%)**, tal como se había advertido. Precio final actualizado: Etapa 1 ≈ USD 1.649, Etapa 2 ≈ USD 597 — **Total ≈ USD 2.246** (la migración se cotiza aparte, en una fase posterior).
- 2026-07-30 (v5 — ticketeadora manual + override de precio a USD 1.800): Joaquín aclaró que la ticketeadora es manual (no se integra) — el módulo de código de barras baja de 7h a 3h (solo vinculación + lookup en venta, sin etiquetado). Esto sube el R de Etapa 1+2 a 69,8% (caso límite, a 0,2 puntos de Tier 1, se mantiene Tier 2 por criterio estricto). El precio según fórmula/política queda en ≈USD 2.183. **Joaquín fijó el precio final a cobrar en USD 1.800** (override comercial directo, ≈17,5% por debajo de la fórmula) — Etapa 1 ≈ USD 1.308, Etapa 2 ≈ USD 492. Chequeo de margen con sus propios números (30h reales + USD 200 tokens IA): tasa efectiva realizada ≈USD 53,3/h, por encima del objetivo de USD 35/h — el override no compromete la rentabilidad esperada.
- 2026-07-30 (v6 — estructura final de pago + mantenimiento): Joaquín reestructuró el precio final como dos modalidades de pago del total del proyecto (ya no por etapa): **USD 1.500 en hasta 3 pagos**, o **USD 1.800 en hasta 12 pagos**. Chequeo de margen con sus propios números confirma que ambas modalidades quedan por encima del objetivo de USD 35/h (≈USD 43,3/h y ≈USD 53,3/h respectivamente). Mantenimiento simplificado a un único plan **PREMIUM** desde el arranque (año 1 gratis, USD 500/año desde el año 2) — reemplaza la transición PRO→PREMIUM de versiones anteriores.
