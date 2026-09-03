# Olvidata**Soft**

---

**Manual de uso — Entrega 2: el ciclo diario de venta**
**OlvidataSoft · Septiembre 2026**

---

## Sobre esta entrega

Esta es la parte del sistema que usás todos los días: vender, cobrar, fiar, cerrar la caja, cargar los gastos y seguir las entregas.

La Entrega 2 cubre seis módulos:

- **Ventas y cuenta corriente de clientes** — el carrito editable, el pago mixto y el fiado.
- **Facturación AFIP** — la emisión del comprobante, como paso opcional de la venta.
- **Caja** — el movimiento del día y los cierres diario y mensual.
- **Gastos** — lo que sale del negocio, con su impacto en la caja.
- **Entregas a domicilio** — reparto propio o tercerizado, con seguimiento de estado.
- **Pantalla de inicio** — la foto del día y las tendencias del mes.

*El catálogo de productos, el stock, las marcas, los modelos, las categorías y el alta de usuarios son de la Entrega 1 y no se explican acá — ya los venías usando.*

Todo entra por el menú de la izquierda. Cada persona entra con su propio usuario y contraseña.

---

## Cómo hacer una venta — paso a paso

Es el flujo que más vas a usar. Entrás por **Ventas → Nueva venta**.

**1. Elegí el cliente (o dejalo vacío).** Si dejás el campo vacío, la venta queda como **Consumidor Final**, que es lo normal para el mostrador. Elegís un cliente cuando querés que quede registrada a su nombre, o cuando le vas a fiar. El buscador arranca mostrándote los primeros clientes; si escribís, filtra por nombre o por CUIT/DNI. Si el cliente es nuevo, el botón **Nuevo cliente** lo abre en otra pestaña sin perder la venta que estás armando.

**2. Cargá los productos.** Tenés dos formas y podés mezclarlas:

| Forma | Cuándo conviene |
|---|---|
| **Buscar producto** | Cuando lo buscás por nombre o por código. Escribís y elegís de la lista. |
| **Escanear código de barras** | Con el lector. Pasás el producto y se agrega solo. También sirve tipeando el código y apretando Enter. |

Cada producto que agregás se suma como una fila con su precio y su IVA ya cargados. Si el producto tiene una oferta vigente, entra con el precio de oferta.

**3. Ajustá la fila si hace falta.** En cada renglón podés cambiar:

- **Cantidad.** Los productos que se venden por unidad suben de a 1. Los que se venden por peso o por metro admiten decimales (por ejemplo, 2,5 metros).
- **Precio unitario**, si en ese caso puntual cobrás distinto.
- **Descuento %** y **Recargo %**. Los dos se calculan sobre el precio de lista, así que si ponés 10% de descuento y 10% de recargo, el precio queda igual que al principio.
- **Subtotal c/IVA.** Es el total del renglón ya con IVA. *Este campo se puede escribir directamente*: si el cliente te dice "dejámelo en $10.000", lo escribís ahí y el sistema recalcula solo el precio unitario para que cierre en ese número.

**4. Cargá los pagos.** Con **Agregar pago** sumás un medio de pago. El primero nace con el total de la venta, así que si te pagan todo junto con un solo medio, ya está.

Si el cliente paga con dos medios (por ejemplo, una parte en efectivo y el resto con tarjeta), agregás una segunda fila: escribís cuánto va en la primera y **la última fila se ajusta sola** para completar el total. Si preferís escribir los dos montos a mano, también podés — abajo te va a quedar indicado el **saldo pendiente**.

| Medio de pago | Qué tiene en cuenta |
|---|---|
| **Efectivo** | Entra directo a la caja del día. |
| **Tarjeta de débito** | Entra a la caja del día. |
| **Tarjeta de crédito (cuotas)** | Te habilita elegir en cuántas cuotas. Según el plan, suma el recargo al total de la venta. |
| **Cuenta corriente (fiado)** | No entra a la caja: queda como deuda del cliente en su cuenta corriente. Necesita sí o sí un cliente elegido en el paso 1. |

En cada pago podés dejar una **nota** opcional: los últimos dígitos de la tarjeta, el número de operación, o lo que te sirva para identificarlo después.

**5. Cerrá la venta.** Tenés dos botones:

- **Guardar borrador** deja la venta a medio armar para seguirla después. Mientras está en borrador no descuenta stock ni toca la caja.
- **Confirmar venta** cierra la venta: descuenta el stock, registra el ingreso en la caja y, si hubo fiado, carga la deuda en la cuenta corriente del cliente. Desde ese momento la venta ya no se edita.

*La factura es un paso aparte y opcional.* Confirmar es lo que hace que la venta exista para el sistema.

**Estados por los que pasa una venta:**

| Estado | Qué significa |
|---|---|
| **Borrador** | Se está armando. Se puede editar. No descuenta stock ni toca la caja. |
| **Confirmada** | La venta ocurrió: descontó stock, entró a la caja y cargó el fiado si lo hubo. Ya no se edita. |
| **Facturada** | Además tiene el comprobante AFIP emitido, con su CAE y su número. |

**Casos especiales contemplados:**

- **Vender sin stock.** Si un producto queda en negativo, el sistema te avisa pero no te frena. La venta real manda.
- **Caja cerrada.** Si ya cerraste la caja del día, no vas a poder confirmar una venta nueva hasta que un administrador la reabra. Es a propósito, para que no entren movimientos a un día ya cerrado.
- **Venta que no se completa.** Un borrador que no vas a usar se descarta con **Cancelar borrador** y deja de aparecer en el listado.
- **Ventas anuladas.** No se muestran en el listado para no confundir, pero no se borran: las ves eligiendo "Anulada" en el filtro de estado.

---

## Facturación AFIP

La factura es un paso **posterior y opcional** a confirmar la venta. Desde el detalle de una venta confirmada, el botón **Emitir factura AFIP** genera el comprobante y guarda su número y su CAE. No vuelve a tocar stock ni caja: eso ya pasó al confirmar.

El tipo de comprobante lo decide el sistema según la condición de IVA que tenga cargada el cliente:

| Condición de IVA del cliente | Comprobante |
|---|---|
| Responsable Inscripto | **Factura A** |
| Monotributo, Exento, Consumidor Final o sin cliente | **Factura B** |

*La facturación electrónica todavía no está activa: falta cargar el certificado y el CUIT del contribuyente. Hasta que se configure, el botón no aparece y las ventas se cierran con **Confirmar venta**, funcionando con normalidad.*

---

## Clientes y cuenta corriente

Desde **Clientes** das de alta y editás a quienes te compran. Los datos que más pesan son el **nombre** y la **condición de IVA** (define el tipo de factura); el resto — CUIT/DNI, teléfono, domicilio, localidad, email y notas — es opcional y se puede completar después.

Cuando le fiás a un cliente, el sistema le lleva la cuenta solo:

**1. La deuda se genera sola.** Al confirmar una venta con un pago en **Cuenta corriente**, esa deuda queda cargada a nombre del cliente. No hay que anotarla aparte.

**2. Consultás el estado cuando querés.** Entrás a la cuenta corriente del cliente y ves el saldo actual y todos los movimientos, con filtros por fecha y por tipo. El saldo se calcula en el momento, sumando lo que debe y restando lo que pagó.

Los movimientos se identifican por su origen: **venta a cuenta corriente** (la deuda que generó una venta), **pago** (lo que el cliente entregó) y **ajuste** (una corrección manual).

*Importante: por ahora esta pantalla es solo de consulta.* La deuda se carga sola cuando fiás en una venta, pero **todavía no hay una pantalla para registrar el pago del cliente ni para hacer un ajuste** — está previsto en el diseño pero no entregado. Hasta que se agregue, el cobro del fiado se sigue llevando por fuera del sistema.

---

## Caja

**1. Durante el día se llena sola.** Cada venta confirmada que se cobra en efectivo, débito o tarjeta genera un ingreso automático. Los gastos que cargás generan el egreso.

**2. Cargás a mano lo que no vino de una venta.** Con **Movimiento manual** registrás un ingreso o un egreso suelto — por ejemplo, plata que ponés para cambio, o un retiro. Siempre pide un motivo.

**3. Cerrás el día.** Al final de la jornada, **Cerrar día** deja la caja del día cuadrada y bloqueada. Después de cerrarla no se pueden confirmar ventas nuevas con esa fecha.

**4. Cerrás el mes.** La pantalla **Cierre de caja mensual** acumula los cierres diarios del mes y te deja hacer el cierre mensual.

En **Caja** ves los movimientos del día con sus totales de ingresos y egresos, y en **Cierres de caja diarios** el historial de los días ya cerrados, con quién los cerró y cuándo.

*El fiado no entra a la caja:* es una deuda diferida que queda en la cuenta corriente del cliente, no plata que entró ese día.

---

## Gastos

En **Gastos** registrás lo que sale del negocio. Cada gasto lleva fecha, categoría, monto, forma de pago y una descripción.

| Dato | Opciones |
|---|---|
| **Categoría** | Alquiler · Servicios · Sueldos · Impuestos · Flete · Otro |
| **Forma de pago** | Efectivo · Transferencia · Cheque · Depósito |
| **Impacto en caja** | Caja chica (sale de la caja del día) · Caja mensual |

Un gasto **no se edita**: si te equivocaste, se **anula** y se carga de nuevo. Los gastos anulados dejan de aparecer en el listado para no confundir, pero no se borran — los seguís viendo eligiendo "Solo anulados" en el filtro de estado.

---

## Entregas a domicilio

**1. Se programa desde la venta.** En el detalle de una venta confirmada, **Programar entrega** abre la entrega con los datos del cliente y el total ya cargados. Cada venta puede tener una sola entrega.

**2. Elegís el tipo y cargás el costo.**

- **Propia**: la hace el negocio, con un repartidor asignado.
- **Tercerizada**: la hace un tercero.

Cargás el **costo base** (lo que te sale a vos), y el sistema le aplica el **porcentaje de markup** configurado para calcular el costo final que se le cobra al cliente. Ese porcentaje queda guardado en la entrega, así que si más adelante se cambia, las entregas viejas mantienen el que tenían.

También cargás la fecha programada y la dirección.

**3. El repartidor la va actualizando.** La entrega pasa por estos estados:

| Estado | Qué significa |
|---|---|
| **Pendiente** | Programada, todavía no salió. |
| **En camino** | El repartidor arrancó el recorrido. |
| **Entregada** | Se entregó. |
| **No entregada** | No se pudo entregar. Queda registrado el motivo y se puede reagendar. |

---

## Recargos por cuotas

En **Configuración → Recargos por cuotas** definís cuánto interés se le suma a una venta según en cuántas cuotas paga el cliente con tarjeta de crédito.

Están los planes de **1, 3, 6, 9, 12, 18 y 24 cuotas** y vos cargás el porcentaje de cada uno. Mientras lo editás, la pantalla te muestra un ejemplo en vivo sobre $100.000 para que veas cuánto termina pagando el cliente y de cuánto le queda cada cuota.

Si hay un plan que no querés ofrecer, lo desactivás con el interruptor: deja de aparecer al cargar un pago, y las ventas viejas que ya lo usaban siguen funcionando igual.

*Los cambios acá impactan en la próxima venta que cargues, sin necesidad de reiniciar nada.*

---

## Pantalla de inicio

Es lo primero que ves al entrar. Está organizada en tres niveles.

**Estado del día** — la foto de hoy:

- **Ventas de hoy**: cuántas hiciste y por cuánto.
- **Caja de hoy**: ingresos, egresos y si está abierta o cerrada.
- **Entregas pendientes**: las que están pendientes o en camino.

**Salud financiera** — aparece con un candado. Son los cobros pendientes de clientes, los pagos pendientes a proveedores y el saldo de caja consolidado. *Llega en la próxima entrega: depende de Compras y de la cuenta corriente de proveedores.*

**Tendencias del mes**:

- **Gastos del mes por categoría**, para ver en qué se va la plata.
- **Productos más vendidos**.
- **Stock crítico**: los que están en negativo o por debajo del mínimo.

---

## Roles de usuario

| Rol | Qué puede hacer en esta entrega |
|---|---|
| **Administrador** | Todo: ventas, clientes y cuentas corrientes, caja, gastos, entregas y la configuración de recargos por cuotas. |
| **Vendedor** | Ventas completas (alta, edición y cierre), clientes y cuentas corrientes, y programar entregas. No accede a caja, gastos ni configuración. |
| **Repartidor** | El listado de entregas, para ir actualizando el estado de sus recorridos. |

*Las altas de usuarios y la asignación de roles las hace un Administrador. Un usuario que deja de trabajar en el negocio se bloquea en vez de borrarse, así queda el historial de lo que hizo.*

---

## Cosas que conviene saber

- **Los listados se filtran por cualquier columna que veas.** Además, el buscador general encuentra también por importe y por fecha: si escribís `1500` te trae las filas de $1.500,00, y si escribís `15/03/2026` te trae las de ese día.
- **Los filtros se recuerdan.** Si filtrás un listado, te vas a otra pantalla y volvés, los filtros siguen puestos. El botón **Limpiar filtros** los borra.
- **Nada se borra del todo.** Lo que se cancela o se anula deja de mostrarse en los listados, pero queda guardado y se puede consultar con los filtros.
- **Todo queda registrado.** Cada movimiento guarda quién lo hizo y cuándo.

---

## Qué queda pendiente de esta entrega

- **Cobro de la cuenta corriente.** Se puede fiar y consultar el saldo, pero falta la pantalla para registrar el pago del cliente y para hacer ajustes manuales. Es lo más importante de esta lista para el día a día.
- **Facturación electrónica AFIP.** El circuito está construido y probado, pero falta el certificado y el CUIT del contribuyente para emitir comprobantes reales.
- **Anulación de una venta ya confirmada.** Un borrador se cancela sin problema, pero una venta confirmada todavía no se puede revertir desde el sistema. Llega junto con las notas de crédito, en la próxima entrega.
- **Nivel "Salud financiera" del inicio.** Depende de Compras y de la cuenta corriente de proveedores, ambos de la próxima entrega.

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
