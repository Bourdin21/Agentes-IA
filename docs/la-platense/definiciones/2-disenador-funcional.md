# Memoria - Disenador funcional

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-10-06 (v7 — Diseno de CR-01 a CR-05: flujos 11 a 15. Venta con/sin factura, facturacion parcial por items con cargo de IVA a la CC del cliente, interes por tarjeta x cuotas con vigencia, plan de echeqs 0/30/60/90/120 sobre el pago programado existente, y transferencia en la venta. LP-014 entra en la misma ronda que CR-01. AnulacionVentaViewModel e IAnulacionVentaService quedan a ajustar: con comprobantes 1:N la NC es por comprobante, no por venta)

## Definiciones vigentes

## Diseño funcional de CR-01 a CR-05 (2026-10-06)

Entrada del Análisis: `1-analista-funcional.md` v6, entradas "Faltantes de alcance relevados el 2026-10-06 — CR-01 a CR-05" y "Decisiones de Joaquín del 2026-10-06 que cierran el Análisis". Reglas R12-R16, criterios PF16-PF20, decisiones D-CR01.1, D-CR01.2, D-CR04.1 y D-CR04.2.

**Escaneo de reutilización (instrucción 39 §3), resultado:** precedente de pantalla verificado archivo por archivo en `C:\Sistemas\marihogar` — `Views/ComprobantesAfip/{Index,Create,Details}.cshtml` para CR-02 (su `Create` **es** la pantalla de "elegir qué ítems facturar"), `Views/Cheques/Index.cshtml` para CR-04, y `ConfiguracionCuotaTarjeta` + su pantalla de Configuración para CR-03. Las pantallas se adaptan al design system Olvidata (instrucción 38), no se copian tal cual: `marihogar` no usa `ov-*`.

### Flujo 11 — Venta con o sin factura (CR-01)

**Dónde vive la decisión:** un control de dos opciones en la cabecera de la venta, junto al cliente — **no** al final, junto a los botones. El vendedor elige antes de cargar ítems porque el IVA cambia el precio que le canta al mostrador, y un control al pie obliga a recalcular toda la pantalla después de que ya dijo un número.

**Comportamiento:**
- Opción **"Con factura"** (default): la venta se comporta exactamente como hoy — IVA por línea, total con IVA.
- Opción **"Sin factura"**: el IVA de todas las líneas pasa a 0 y el total es la suma de los netos. El recalculo es inmediato y visible en la grilla de ítems: la columna IVA muestra una raya apagada (`ov-vacio`) y no un `0,00`, que se lee como "pagó cero de IVA" en vez de "no hay IVA".
- El bloque de totales muestra **siempre** las dos cifras cuando la venta es sin factura: *Neto* y, debajo y tenue (`ov-celda-secundaria`), *"con factura serían $X"*. Es el dato que el vendedor necesita para responder "¿y con factura cuánto sale?" sin cambiar el control de ida y vuelta.
- El recargo por cuotas de tarjeta se calcula **sobre el total resultante** (R12), así que cambiar la marca recalcula también el recargo. Se muestra recalculado antes de confirmar (mismo criterio que PF3).
- **El control se bloquea al confirmar.** Una venta cerrada no cambia de condición: si hace falta, se factura después por el flujo 12.

**Default y permisos (D-CR01.2):** lo elige el vendedor (R12), pero **el precio unitario deja de ser editable para el rol Vendedor**: se recalcula siempre desde el producto. Hoy cualquier usuario con `RequireVentas` puede tipear el precio que quiera (**LP-014**, abierto en producción) y sumarle a eso una palanca que resta el IVA son dos caminos para bajar el precio sin control. El Administrador conserva el precio editable. Es el precedente de `marihogar` (`VentaService.ConfirmarAsync` / `EditarAsync`), se trae completo y **entra en la misma ronda que CR-01, no después**.

**Estado vacío / caso borde:** una venta sin factura de un cliente con CUIT no se bloquea (el negocio decide, no el sistema), pero la cabecera muestra un aviso tenue de una línea: *"este cliente tiene CUIT"*. Avisar sin bloquear es el mismo criterio que R10 usó para el stock sin verificar.

### Flujo 12 — Facturar parte de una venta (CR-02)

**Punto de entrada:** desde el detalle de la venta, acción *"Facturar"*, disponible mientras quede algo sin facturar. En el listado de ventas la columna de estado deja de ser binaria: *Confirmada*, *Facturada en parte*, *Facturada*. El estado habitual va tenue y **solo "Facturada en parte" lleva color** (instrucción 38: lo normal se susurra, lo excepcional se ve) — es el estado sobre el que hay algo pendiente que hacer.

**Pantalla de emisión (adaptada de `ComprobantesAfip/Create` de marihogar):**
- Grilla de los ítems de la venta con, por fila: producto, cantidad vendida, **cantidad ya facturada**, **cantidad pendiente** y un campo editable *"cantidad a facturar"* precargado con el pendiente.
- Tope duro por fila: no se puede pedir más que el pendiente (R13). La validación vive en el Service, no solo en el input.
- Cabecera del comprobante: tipo (A/B/C, derivado de la condición de IVA del cliente), cliente, y **el total del comprobante calculado en vivo** a medida que se tocan las cantidades.
- **El bloque del IVA es el punto delicado de toda la pantalla.** Si la venta se cobró sin factura (flujo 11), el comprobante lleva IVA que **no se cobró**. La pantalla lo dice en texto, no en un tooltip: *"esta venta se cobró sin IVA. Al facturar estos ítems se genera un cargo de $X en la cuenta corriente del cliente"*, con el importe exacto y antes de emitir. Confirmar emite el comprobante **y** postea ese cargo, en la misma transacción (D-CR01.1).
- Si la venta ya se había cobrado con IVA, ese bloque no aparece: no hay diferencia que cobrar.

**Lo que NO se recalcula nunca:** la venta. Ni su total, ni sus subtotales, ni los pagos ya posteados. El IVA que aparece es un **cargo nuevo en la CC del cliente** con su propio origen en el ledger (`OrigenMovimientoCC` nuevo, propagado a los filtros que listan el ledger — LP-002, mismo camino que `CobroCC`). La venta queda cobrada por un importe y facturada por otro mayor, y **los dos son correctos**.

**Nota de alcance que corrige el diseño anterior:** `AnulacionVentaViewModel` y `IAnulacionVentaService` (definidos para el módulo 16) asumen **un** comprobante por venta. Con comprobantes 1:N, la nota de crédito se emite **contra un comprobante**, no contra la venta. Esas dos definiciones quedan superadas por el flujo 12 y hay que ajustarlas antes de construir el módulo 16 (Entrega 5) — es más barato hacerlo ahora que después de la primera NC real.

### Flujo 13 — Interés de tarjeta por tarjeta y cuotas (CR-03)

**Pantalla de configuración** (Configuración > Intereses de tarjeta), al lado de la que ya existe para recargos por cuotas:
- Grilla de **tarjeta × cuotas** con el % en cada cruce. Filas = tarjetas, columnas = los planes vigentes (1/3/6/9/12/18/24). Es la forma en que el cliente lee el papel que le deja la procesadora, y editar un plan completo de una tarjeta es una fila, no siete pantallas.
- Set de tarjetas **cerrado y configurable por el admin** (alta/baja lógica), no un enum: el negocio agrega una tarjeta cuando cambia de terminal, y eso no puede requerir deploy. Dar de baja una tarjeta no rompe las ventas que la usan (mismo criterio que `RecargoCuota.Activo`).
- **Vigencia por fecha** en cada porcentaje (`VigenteDesde`/`VigenteHasta`, patrón que `OrdenCompra` ya usa para sus impuestos): cambiar el coeficiente no reescribe el pasado y permite cargar el aumento del mes que viene por adelantado.

**En la venta:** al elegir *Crédito en cuotas* aparece el combo de **tarjeta** (hoy no existe) y, con tarjeta + cuotas elegidas, el % se resuelve de la tabla y se muestra el recargo **antes de confirmar** (PF18). El vendedor lo puede ajustar a mano para esa venta, igual que hoy; el valor efectivo se congela en `PagoVenta.PorcentajeRecargoAplicado`, que ya existe y **no se toca** — es lo que garantiza que editar la tabla no cambie ninguna venta posteada (R14).

**Fuera de alcance, confirmado (D-CR04.2):** el costo real de cobranza (lo que la terminal le descuenta al negocio) y la acreditación diferida. La tabla se diseña con lugar para esas alícuotas pero no se construyen ahora.

### Flujo 14 — Plan de echeqs a 0/30/60/90/120 (CR-04)

**Alcance (D-CR04.1):** esto NO es una cartera de cheques. Se construye **sobre el pago programado que ya existe** en `PagoOrdenCompra`.

**Pantalla:** en el formulario de pago a proveedor, al elegir forma de pago *Cheque electrónico (echeq)* se habilita un bloque **"Plan de pago"**:
- Selección múltiple de plazos (0 / 30 / 60 / 90 / 120 días) y, al elegirlos, la pantalla genera **una fila por plazo** con el monto repartido (por defecto en partes iguales, cada monto editable) y el **vencimiento calculado** = fecha del pago + los días del plazo.
- Cada fila pide **número de cheque y banco** (los dos datos que el pedido nombra). El número se valida como obligatorio y único por banco; el banco es texto libre con autocompletado de los ya usados (no hay catálogo de bancos y crear uno para esto es modelar una hipótesis).
- El plazo **0 días** es un echeq al día: entra como una fila más del plan, no por otro camino.
- La suma de las filas tiene que dar el total que se está pagando. Es una validación de Service, con el faltante/sobrante a la vista mientras se tipea.

**Qué mueve plata y cuándo:** ninguna fila mueve caja ni cuenta corriente al crearse — nacen como pago programado `Pendiente`, que es el comportamiento que ya está construido y probado. **La plata sale al confirmar cada fila**, manualmente, por el camino que ya existe (`ConfirmarPagoProgramadoAsync`). El aviso de vencimiento usa el patrón propio **`PAT-056`** (chequeo oportunista al primer request del día, idempotencia en la base), **no** el `BackgroundService` de `marihogar`: La Platense no tiene ni un `AddHostedService` y en SmarterASP un job con hora fija puede no correr nunca.

**La fecha de confirmación — decisión de diseño sobre un dato medido en contra:** la decisión pide la acreditación *"calculada con los x cantidad de días"*. En `marihogar` se midió qué fecha acierta contra el extracto bancario: **el vencimiento del cheque acertó 1 de 13; la fecha que el usuario leyó del extracto, 8 de 13.** Resolución: el vencimiento **se calcula** (es lo pedido) y es el que ordena la grilla y dispara el aviso; al confirmar, la fecha viene **propuesta con ese vencimiento y queda editable**. El camino normal es un click sin tipear nada, y el 61% de los casos en que el banco debitó otro día sigue teniendo arreglo. **Nada se acredita solo.**

**Listado:** los echeqs pendientes se ven en el detalle de la compra y en un listado propio filtrable por proveedor, estado y rango de vencimiento (`ov-filtros` plegado por defecto, contador de filtros puestos — instrucción 38). La fila cuyo vencimiento cae dentro de 7 días se resalta; el resto va tenue.

### Flujo 15 — Transferencia en la venta (CR-05)

Valor nuevo en el combo de medios de pago de la venta, **al final del enum** (los enteros ya están persistidos en producción: ningún valor se intercala ni se reordena). Campo de nota opcional para el número de operación, que ya existe en `PagoVenta.Nota`. En el cierre diario aparece como línea propia, separada del efectivo (PF20) — hoy se carga como Efectivo y el arqueo cuenta como plata en el cajón algo que está en el banco.

### ViewModels nuevos y extendidos

- `VentaEditableViewModel` (extendido): agrega `Facturar` (bool, default true), `TotalConFactura` y `TotalSinFactura` (los dos calculados, para el bloque de totales), `TarjetaId` y la lista de tarjetas en cada `PagoViewModel`. `PrecioUnitario` pasa a ser **solo lectura para el rol Vendedor**.
- `FacturacionParcialViewModel` (nuevo): venta, tipo de comprobante, datos del cliente, grilla de `ItemFacturableViewModel` (ítem, cantidad vendida, ya facturada, pendiente, a facturar), total del comprobante, y **`DiferenciaIvaACobrar`** con el texto del aviso cuando la venta se cobró sin IVA.
- `TarjetaInteresViewModel` (nuevo): grilla tarjeta × cuotas con el % en cada cruce y la vigencia de cada valor.
- `PlanEcheqViewModel` (nuevo): total a cubrir, plazos elegidos, grilla de `LineaEcheqViewModel` (plazo en días, monto, vencimiento calculado, número de cheque, banco), y el faltante/sobrante contra el total.
- `AnulacionVentaViewModel` — **a ajustar**: pasa a operar sobre un comprobante, no sobre la venta (ver flujo 12).

### Validaciones de UI acordadas (se suman a las vigentes)

- No permitir cambiar la marca "con factura / sin factura" de una venta ya confirmada.
- No permitir facturar más cantidad que la pendiente de cada ítem — validado en el Service, no solo en el input.
- No permitir emitir un comprobante parcial sin que el usuario haya visto el importe del cargo de IVA que se va a postear en la CC del cliente (cuando corresponde): el importe está en pantalla, no detrás de un tooltip.
- No permitir confirmar un plan de echeqs cuya suma no dé el total del pago, ni con una fila sin número de cheque o sin banco.
- No permitir dos cheques con el mismo número en el mismo banco.
- El precio unitario de la venta no es editable para el rol Vendedor (bloqueado a nivel de autorización, no solo de UI — mismo criterio que la CC de empleados).

### Contratos funcionales para Services (nuevos y afectados)

- `IVentaWorkflowService` (afectado): el cálculo de IVA pasa a depender de la marca de facturación de la venta; el precio unitario se recalcula desde el producto cuando el usuario no es Administrador.
- `IFacturacionParcialService` (nuevo): dada una venta y las cantidades elegidas, valida los pendientes, emite el comprobante, y postea el cargo de IVA en la CC del cliente **en la misma transacción**. Devuelve el pendiente actualizado por ítem.
- `IRecargoCuotasService` (afectado): la firma pasa de `(medio, cuotas)` a `(medio, tarjeta, cuotas, fecha)` — la fecha porque el porcentaje tiene vigencia.
- `IPlanEcheqService` (nuevo): dado un total, los plazos y la fecha de pago, genera las N líneas de pago programado con sus vencimientos, números y bancos, en una transacción. No mueve caja ni cuenta corriente.
- `IAnulacionVentaService` (afectado): pasa a operar por comprobante.

### Lo que este diseño deja afuera, explícito

- Cartera de cheques como módulo (rechazo, reemplazo, conciliación de extracto) — D-CR04.1.
- Impuesto al cheque, impuesto por plataforma e impuesto por gasto — **v2**, con el precedente ya identificado (D-CR04.2). Las entidades nuevas se diseñan con lugar para esas alícuotas.
- Costo real de cobranza y acreditación diferida de tarjeta — fuera del plan desde el 2026-10-06.
- Cheques recibidos de clientes — no aplica.

### Historias de usuario

Ver `1-analista-funcional.md` §"Criterios de aceptacion vigentes" (PF1-PF8). Se agregan acá los flujos de pantalla que las soportan.

### Flujos de pantalla acordados

**1. Unidades de medida y conversión compra↔venta**
- Alta/edición de producto: campo `UnidadVenta` (Unidad / Peso(Kg) / Metro / Bulto). Si el producto se compra en una unidad distinta a la que se vende, se activa `UnidadCompra` + `FactorConversion` (ej. `UnidadCompra=Bulto`, `FactorConversion=100` → 1 bulto = 100 unidades de venta).
- Pantalla de Compra: el usuario carga cantidad en `UnidadCompra`; el sistema muestra en tiempo real el equivalente en `UnidadVenta` que impactará en stock, antes de confirmar.
- Pantalla de Venta: el ítem se carga siempre en `UnidadVenta` (stock se mantiene en la unidad más granular).
- *Hipótesis a validar con el cliente: el factor de conversión es fijo por producto (no varía de una compra a otra). Si un mismo producto viene en bultos de distinto tamaño según el proveedor, el modelo necesita revisarse antes de implementar.*

**2. Venta editable — workflow Borrador → Facturada**
- **1. Iniciar venta.** El vendedor abre "Venta rápida", agrega productos (unidad, cantidad, precio unitario editable, % IVA editable, descuento/recargo por ítem). La venta queda en estado `Borrador`.
- **2. Cargar pago(s).** Se pueden cargar uno o varios pagos (efectivo, tarjeta débito, tarjeta crédito 3/6 cuotas con recargo, cuenta corriente/fiado). El sistema calcula el recargo de cuotas según la configuración vigente y lo suma al total antes de confirmar.
- **3. Revisar antes de facturar.** Mientras la venta está en `Borrador`, el vendedor puede volver a editar cualquier ítem, cantidad, precio o IVA.
- **4. Emitir comprobante AFIP.** El vendedor elige cliente cargado o "Consumidor final" y emite. La venta pasa a `Facturada` y deja de ser editable.

| Estado | Editable | Acción disponible |
|---|---|---|
| Borrador | Sí (ítems, precios, IVA, pagos) | Editar, cancelar, emitir comprobante |
| Facturada | No | Consultar, anular/NC (si el cliente confirma que aplica — ver pregunta abierta en Analisis) |

*Hipótesis a validar: si una venta en Borrador ya tiene pagos cargados y se edita el total, el saldo pendiente se recalcula automáticamente — a confirmar con el cliente antes de implementar la regla de recálculo.*

**Casos especiales contemplados:**
- Venta con pago mixto (parte efectivo + parte tarjeta + parte cuenta corriente).
- Venta a "Consumidor final" sin cliente cargado (no genera movimiento de cuenta corriente).
- Venta con ítems de distintas unidades de medida en el mismo comprobante.

**3. Importación de lista de precios de proveedor**
- **1. Configurar proveedor.** El admin carga el TC propio del proveedor y su % de descuento particular, una sola vez (editable cuando cambien).
- **2. Subir archivo.** El admin sube el Excel de lista de precios del proveedor.
- **3. Previsualizar.** El sistema muestra una grilla de preview con el precio recalculado (`precio_lista_USD × TC_propio × (1 − %descuento)`) antes de aplicar nada.
- **4. Confirmar.** Al confirmar, se actualizan los precios de compra de los productos vinculados a ese proveedor.

*Hipótesis a validar: el formato de Excel de cada proveedor no es estándar — el mapeo de columnas puede necesitar configuración por proveedor. Se define con el archivo real en mano, no antes.*

**4. Cuenta corriente de empleados (autoservicio)**
- El admin carga pagos de sueldo y retiros/gastos del empleado desde su panel de administración.
- El empleado, al ingresar con su usuario, ve únicamente su propia cuenta corriente (sueldo pagado, retiros) — no ve la de otros empleados, ni accede a reportes generales de caja/negocio.

**5. Anulación de venta facturada + devolución de mercadería (NUEVO — confirmado por el cliente 2026-07-30)**
- **1. Iniciar anulación.** Desde una venta en estado `Facturada`, el admin (a confirmar si también el vendedor, ver pregunta abierta en Analisis) inicia la anulación.
- **2. Registrar devolución (si aplica).** Si hay mercadería física que vuelve, se carga la devolución: producto, cantidad, motivo. El stock se reingresa automáticamente.
- **3. Emitir nota de crédito AFIP.** El sistema emite la NC vinculada al comprobante original (mismo circuito WSAA/WSFE ya resuelto para facturas).
- **4. Cerrar el ciclo.** La venta pasa a estado `Anulada`; si había saldo en cuenta corriente del cliente, se ajusta.

*Hipótesis a validar con el cliente (pregunta abierta): si la anulación la puede iniciar cualquier vendedor o solo el admin, y si existe un límite de tiempo (ej. solo el mismo día de la venta).*

**Casos especiales contemplados:**
- Devolución parcial (algunos ítems de la venta, no todos).
- Venta con pago ya cobrado: la NC ajusta el saldo, no genera un reintegro de efectivo automático (eso se resuelve operativamente, fuera del sistema).
- No existe flujo de "cambio" (canje por otro producto) — confirmado, siempre es devolución simple.

**6. Dashboard — "foto completa del negocio" (pantalla de mayor prioridad de diseño)**

El cliente confirmó que esta es la pantalla más importante del sistema y pidió priorizar diseño y estructura por sobre el resto. Enfoque propuesto:
- **Jerarquía en 3 niveles**, no una grilla plana de tarjetas sueltas: (1) estado del día (ventas de hoy, caja del día, entregas pendientes), (2) salud financiera (cobros pendientes de clientes, pagos pendientes a proveedores, saldo de caja consolidado), (3) tendencias (gastos del mes por categoría, top productos, stock crítico).
- Cada bloque debe poder navegarse hacia el detalle correspondiente (ej. click en "cobros pendientes" lleva al listado de clientes con saldo).
- *Antes de construir el detalle final, se recomienda una sesión de diseño dedicada con el cliente para priorizar qué KPIs van en el "primer vistazo" (nivel 1) — evitar construir un dashboard con demasiada información sin jerarquía clara, que es el riesgo típico de un pedido de "foto completa".*

**7. Migración de catálogo — POSPUESTA, fuera de este alcance**

Se retira este flujo del diseño actual. Se cotiza y diseña en una fase posterior, cuando se confirme si hay acceso directo a la base de datos del sistema actual (segundo relevamiento) o si sigue siendo por archivo Excel — el diseño del importador (mapeo configurable, preview, carga por lotes) queda como referencia para esa fase futura, no se construye ahora.

**8. Puesta a punto de stock inicial (plan ABC + arranque suave) — vigente, independiente de la migración**
- **1. Clasificar (fuera del sistema, lo hace el cliente).** El cliente marca en el catálogo qué productos son "A" (mayor rotación/valor) usando el campo de clasificación ABC — no requiere sesión con Olvidata, es una decisión de negocio propia.
- **2. Contar los "A" y cargarlos con stock real.** Vía alta o edición manual de stock (ya no depende de un importador de migración, dado que esa etapa se pospuso).
- **3. El resto arranca en 0/sin verificar.** El sistema permite vender con stock negativo para estos productos (aviso visual, no bloqueo).
- **4. Ajustar sobre la marcha.** Pantalla de "ajuste de stock" (producto, cantidad, motivo) disponible para el rol autorizado — reutiliza patrón de `ShowroomGriffin`.

*Casos especiales contemplados:*
- Producto con stock negativo: la venta se permite pero queda marcado visualmente en el listado de stock hasta que se ajuste.
- El "conteo cíclico" (revisar una categoría por semana) es un hábito operativo del cliente, no una pantalla nueva — se apoya en el mismo "ajuste de stock" del punto 4.

**9. Código de barras — vinculación al producto + lectura en venta (SIMPLIFICADO — la ticketeadora es manual, no se integra)**
- **1. Vincular código.** Al cargar/editar un producto, se ingresa su código de barras (de fábrica, si lo tiene, o el que el cliente le asignó con su ticketeadora manual) — campo único en el catálogo. El sistema no genera ni imprime nada; el etiquetado físico lo sigue haciendo el cliente por su cuenta.
- **2. Escanear en la venta.** En la pantalla de venta, un campo con foco detecta el código escaneado (el lector USB actúa como teclado) y agrega el producto automáticamente al carrito, sin necesidad de buscarlo.

**Casos especiales contemplados:**
- Producto sin código de fábrica: el cliente le asigna uno propio con su ticketeadora manual, y lo carga en el sistema — sin distinción funcional para el resto del sistema (venta, stock, etc.) respecto de un código de fábrica.

**10. Migración de catálogo (Etapa 3) — retomada 2026-08-17 con acceso real a la base del sistema actual**

Base: `1-analista-funcional.md` sección "Etapa 3 — Migración de catálogo" (análisis completo con datos reales: 121.691 artículos activos, reglas de barrido/deduplicación, fuente de ventas confirmada `VentaItem`/`Operacion`).

- **1. Extracción y limpieza (batch, sin UI — corre una vez, antes del import a producción).** Sobre una copia del backup del cliente (no se conecta en vivo a su sistema):
  1. Excluir `Articulo` con `Activo=0`, `Nombre` vacío, o `PrecioVenta=0`.
  2. Resolver duplicados de nombre (grupos con >1 activo): conservar el de venta más reciente en `VentaItem`/`Operacion`; si ninguno vendió, el de `FechaModificacionPrecio` más reciente (ver regla final en `1-analista-funcional.md`).
  3. Resolver `articuloProveedor` (58,8M filas históricas): tomar por `(ProveedorKey, CodigoProv)` solo la fila del `IngresoKey` más reciente con `Procesado=1` y `ArticuloKey IS NOT NULL` → construye `CodigoProveedorProducto` limpio.
  4. Resolver código de barras (`Codigo`) compartido por más de un artículo: preferir el vínculo hacia el artículo que sobrevivió la deduplicación del punto 2; si dos artículos "ganadores" comparten el mismo código de barras, es inconsistencia real de datos → generar en un reporte de excepciones, no bloquea el resto del import.
  5. Calcular clasificación ABC inicial por artículo: Pareto 80/95 sobre cantidad vendida en `VentaItem` de los últimos 12 meses (relativo a la fecha del backup) — el resto (sin venta en la ventana) arranca en "C" sin verificar, mismo criterio que la puesta a punto de stock de Entrega 1.
  6. Generar un **reporte de excepciones** (no un bloqueo): artículos sin `Rubro` válido (asignados a categoría "Sin categoría" por defecto), códigos de barra en conflicto sin resolver, grupos de duplicados sin ningún ganador claro.
  - Resultado de este paso: un dataset limpio listo para cargar Producto/CodigoProveedorProducto/Cliente en el sistema nuevo.
- **2. Carga al sistema nuevo — CORREGIDO 2026-08-17: por script directo, no por pantalla web.** Joaquín decidió que, al ser una carga de una sola vez, no tiene sentido pasar por un flujo de subida de archivo + preview + confirmar en la app — se hace con un script que escribe directo en la base (reutilizando las entidades `Producto`/`CodigoProveedorProducto`/`Cliente`/`Proveedor` ya definidas). **Se retira `ICatalogoMigracionService`/`MigracionCatalogoController` y las vistas asociadas, ya implementadas — no se usan.** Esto es exclusivo de la migración histórica: la futura importación de listas de precios de proveedor (flujo 3, recurrente, la sigue operando el personal de La Platense) sigue siendo por archivo vía pantalla, son necesidades distintas — no se confunde una con la otra.
- **3. Clasificación ABC automática — ida y vuelta con el criterio manual ya existente (Entrega 1).** El campo `Producto.ClasificacionABC` (ya editable a mano desde Entrega 1) pasa a tener además un cálculo automático sugerido:
  - Job/acción manual "Recalcular clasificación ABC" (no en tiempo real por venta — se recalcula por lote, ej. mensual o a demanda desde una pantalla de administración) que recorre `ItemVenta` de los últimos 12 meses (ventana móvil, no todo el histórico) y aplica el mismo criterio Pareto 80/95 documentado en el análisis.
  - El resultado se guarda como **sugerencia** — el campo sigue siendo editable a mano por el cliente en cualquier momento (no contradice R10/analisis v1: "la clasificación la hace el cliente por su cuenta"). La pantalla de Producto/Catálogo muestra el valor sugerido junto al valor vigente si son distintos, con un botón para aceptar la sugerencia.

**Casos especiales contemplados:**
- Producto nuevo (sin historial de venta, dado de alta después de la migración): sin sugerencia ABC hasta que acumule ventas — el campo queda en blanco/"C" por defecto, editable a mano igual que hoy.
- Reimportación / segunda corrida del paso 1 (ej. el cliente pide corregir algo después de la primera migración): el proceso debe ser idempotente sobre `CodigoProveedorProducto` (actualizar, no duplicar, si el `Producto` ya fue migrado antes).

### ViewModels definidos

- `ProductoFormViewModel`: incluye `UnidadVenta`, `UnidadCompra` (nullable), `FactorConversion` (nullable), `PrecioCompra`, `PrecioVenta`, `PrecioConDescuento`, `PorcentajeIVA`, `MarcaId`, `ModeloId`, `CategoriaId`.
- `VentaEditableViewModel`: lista de `ItemVentaViewModel` (producto, cantidad en `UnidadVenta`, precio unitario editable, %IVA editable, subtotal calculado), lista de `PagoViewModel` (medio de pago, monto, cuotas si aplica, % recargo aplicado), estado (`Borrador`/`Facturada`), cliente (cargado o consumidor final).
- `ImportacionListaProveedorViewModel`: proveedor, archivo, `TCPropio`, `PorcentajeDescuento`, grilla de preview (producto detectado, precio original, precio recalculado, acción: crear/actualizar/omitir).
- `CuentaCorrienteEmpleadoViewModel`: solo lectura para el empleado — movimientos (fecha, tipo: sueldo/retiro/gasto, monto, saldo).
- `AnulacionVentaViewModel`: venta original, ítems a devolver (parcial o total), motivo, preview de la NC antes de emitir.  ·  **a ajustar por CR-02** (con comprobantes 1:N la NC es por comprobante, no por venta — ver flujo 12)
- `DashboardViewModel`: 3 niveles (estado del día, salud financiera, tendencias) — ver flujo 6.
- `AjusteStockViewModel`: producto, cantidad actual, cantidad nueva, motivo — genera registro auditado.
- `VentaEditableViewModel` (extendido): campo de escaneo de código de barras que agrega un `ItemVentaViewModel` automáticamente al detectar un código válido.
- ~~`ImportacionCatalogoMigracionViewModel`~~ / ~~`ReporteExcepcionesMigracionViewModel`~~ — **retirados 2026-08-17** junto con `ICatalogoMigracionService` (ver arriba).
- `RecalculoClasificacionAbcViewModel` (Etapa 3): parámetro de ventana en meses (default 12) para la acción manual "Recalcular clasificación ABC".
- `ProductoFormViewModel` (extendido, Etapa 3): agrega `Bonificacion` (texto libre tipo `"33+5"`, ver gap confirmado en Análisis) y `ClasificacionABCSugerida` (solo lectura, junto al `ClasificacionABC` editable ya existente).
- `ClienteFormViewModel` (extendido, Etapa 3): agrega `Domicilio`, `Localidad`, `Email`, `Notas` (campos confirmados como gap en Análisis).

### Validaciones de UI acordadas

- No permitir emitir comprobante AFIP si la venta no tiene al menos un ítem y el total de pagos no cubre el total (salvo venta a cuenta corriente/fiado, donde el saldo pendiente es intencional).
- No permitir guardar un producto con `UnidadCompra != UnidadVenta` sin `FactorConversion` > 0.
- No permitir confirmar importación de lista de proveedor sin revisar el preview.
- Bloquear a nivel de autorización (no solo de UI) el acceso de un empleado a la cuenta corriente de otro.
- No permitir confirmar la importación de migración de catálogo (Etapa 3) sin haber revisado el conteo del reporte de excepciones (no bloquea el import, pero exige que el usuario haya abierto/visto el reporte antes de confirmar).
- El botón "Aceptar sugerencia" de clasificación ABC automática nunca sobrescribe el valor manual sin una acción explícita del usuario — el cálculo por lote solo actualiza el campo `ClasificacionABCSugerida`, nunca `ClasificacionABC` directamente.

### Logica de distribucion de elementos en pantalla
- priorizar simplicidad visual y comprension inmediata del flujo
- ubicar primero informacion y acciones criticas; dejar secundario en segundo plano
- mantener jerarquia consistente (titulo, contexto, formulario, acciones)
- reducir ruido visual: evitar bloques redundantes y opciones duplicadas
- reutilizar este criterio de distribucion en todas las pantallas del sistema
- Listados (Catálogo, Ventas, Compras, Cuentas corrientes) con DataTable — columnas visibles = filtros disponibles (criterio estándar del estudio).

### Contratos funcionales para Services

- `IUnidadMedidaConversionService`: calcula equivalencia compra↔venta dado un producto y una cantidad en unidad de compra.
- `IVentaWorkflowService`: gestiona transición Borrador→Facturada, valida reglas de edición según estado.
- `IRecargoCuotasService`: calcula el recargo aplicable según medio de pago y cantidad de cuotas configurada.
- `IListaPreciosProveedorImportService`: parsea el archivo del proveedor, aplica TC propio + % descuento, devuelve preview antes de persistir.
- `ICuentaCorrienteEmpleadoService`: expone movimientos de UN empleado, validando que el usuario autenticado sea el dueño de la cuenta o el admin.
- `IAnulacionVentaService`: valida que la venta esté en estado `Facturada`, coordina devolución de stock + emisión de NC + transición a `Anulada`.  ·  **a ajustar por CR-02** (pasa a operar por comprobante — ver flujo 12)
- `IAjusteStockService`: aplica una corrección manual de stock con motivo, genera auditoría (usuario, fecha, valor anterior/nuevo).
- `ICodigoBarrasLookupService`: resuelve un producto a partir de un código escaneado (propio o de fábrica) para el flujo de venta.
- ~~`ICatalogoMigracionService`~~ — **retirado 2026-08-17**: la carga del catálogo histórico va por script directo a la base, no por un Service de la app (ver flujo 10, paso 2, corrección de Joaquín).
- `IClasificacionAbcAutomaticaService` (Etapa 3): recalcula por lote la clasificación ABC sugerida de todos los productos sobre una ventana móvil de ventas (12 meses configurable), usando Pareto 80/95 por cantidad vendida en `ItemVenta` — nunca escribe el campo manual `ClasificacionABC` directo, solo `ClasificacionABCSugerida`. Se mantiene — es una funcionalidad permanente del sistema (recalculable en cualquier momento), no exclusiva de la migración.

### Código de barras múltiple por producto (2026-08-21, ver `1-analista-funcional.md` §10)

- El buscador de código de barras (Catálogo hoy, Venta en el futuro) tiene que resolver un producto escaneando **cualquiera** de sus códigos válidos: el propio (impresora interna del cliente, siempre 1) o cualquiera de sus códigos de fábrica alternos (0 a N, uno por variante real).
- La ficha de Producto muestra, además del campo actual "Código de barras" (sin cambios), una sección de solo lectura "Otros códigos de barras válidos" cuando el producto tiene alguno — lista simple, sin ABM en esta ronda (igual criterio que `CodigoProveedorProducto`, cargado hoy solo por script/migración, sin pantalla de gestión propia).
- Regla de validación: un código de barras (propio o alterno) no puede repetirse en dos productos distintos — mismo criterio de unicidad que ya aplica hoy.

## Historial de ajustes
- 2026-08-21: agregado el flujo de código de barras múltiple — buscador debe resolver por cualquier código válido (propio o alterno de variante), ficha de producto muestra los alternos en solo lectura. Ver `1-analista-funcional.md` §10 para el hallazgo real que lo origina.
- 2026-07-30: Diseño v1 — flujos de venta editable, conversión de unidades, importación de listas de proveedor y cuenta corriente de empleados definidos como los cuatro flujos no triviales del sistema.
- 2026-07-30 (v2): agregados 2 flujos nuevos tras respuestas del cliente — anulación de venta facturada + devolución de mercadería (con NC AFIP), y migración de catálogo (Etapa 3, 17.000 productos, mapeo configurable por lote). Dashboard rediseñado como pantalla de 3 niveles jerárquicos (día / salud financiera / tendencias), marcado como prioridad de diseño explícita del cliente — se recomienda sesión de diseño dedicada antes de cerrar el detalle final.
- 2026-07-30 (v3): agregado el flujo de puesta a punto de stock inicial (clasificación ABC + conteo focalizado + arranque suave con stock negativo permitido + ajuste manual auditado) — responde al problema real del cliente de no tener stock confiable hoy por la rotación de artículos.
- 2026-07-30 (v4): agregado el flujo de código de barras (etiquetado con ticketeadora + escaneo en venta). Retirado el flujo de migración de catálogo (pospuesto, se cotiza en una fase posterior) — el flujo de puesta a punto de stock inicial queda independiente de la migración.
- 2026-07-30 (v5): simplificado el flujo de código de barras — la ticketeadora es manual (no se integra con el sistema); se retira la generación/impresión de etiquetas, queda solo la vinculación del código al producto y la lectura en venta.
- 2026-08-17 (v6): retomado el flujo de migración de catálogo (Etapa 3, flujo 10) con datos reales del sistema actual (ver `1-analista-funcional.md`). Diseñado en 2 pasos: (1) extracción/limpieza batch sin UI (excluye inactivos/sin nombre/precio cero, dedup por venta más reciente o fecha de modificación, dedup de `articuloProveedor` por última importación procesada+matcheada, ABC inicial por Pareto 12 meses) y (2) importación con UI reutilizando el patrón preview→confirmar ya usado para listas de proveedor. Agregado el mecanismo de clasificación ABC automática por lote como sugerencia editable, sin reemplazar el campo manual ya existente de Entrega 1 (no contradice R10). Agregados los ViewModels `ImportacionCatalogoMigracionViewModel`, `ReporteExcepcionesMigracionViewModel`, y extendidos `ProductoFormViewModel`/`ClienteFormViewModel` con los gaps confirmados (bonificación compuesta, campos de Cliente, ABC sugerida).
