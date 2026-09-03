# Olvidata**Soft**

---

**Manual de uso — Sistema de gestión La Platense**
**OlvidataSoft · Septiembre 2026**

---

## Sobre el sistema

Este es el manual del sistema que hoy usás en la ferretería. Está escrito para el mostrador: qué hace cada pantalla, en qué orden se usan y qué tener en cuenta en cada paso.

En la práctica, con el sistema podés:

- Buscar un producto por nombre, por código o pasando el lector de código de barras.
- Armar una venta con varios productos, aplicar descuentos o recargos, y cobrarla con uno o varios medios de pago.
- Cerrar la venta con o sin factura — la factura es un paso aparte y opcional.
- Fiar a un cliente y llevarle la cuenta corriente, con lo que debe y lo que va pagando.
- Ver la caja del día en vivo, cargar movimientos a mano y cerrarla al final de la jornada.
- Registrar los gastos del negocio y ver en qué se va la plata cada mes.
- Programar entregas a domicilio y seguir en qué estado está cada una.
- Tener el stock al día, con avisos de lo que se está por acabar.

Todo entra por el menú de la izquierda. El sistema se abre en `https://ferreterialaplatense.com.ar` y cada persona entra con su propio usuario y contraseña.

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

Los medios disponibles son:

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

*La factura es un paso aparte y opcional.* Confirmar es lo que hace que la venta exista para el sistema. Si más adelante necesitás el comprobante fiscal de esa venta, se emite desde el detalle de la venta con el botón **Emitir factura AFIP** — sin volver a tocar stock ni caja.

**Casos especiales contemplados:**

- **Vender sin stock.** Si un producto queda en negativo, el sistema te avisa pero no te frena. La venta real manda.
- **Caja cerrada.** Si ya cerraste la caja del día, no vas a poder confirmar una venta nueva hasta que un administrador la reabra. Es a propósito, para que no entren movimientos a un día ya cerrado.
- **Venta que no se completa.** Un borrador que no vas a usar se descarta con **Cancelar borrador** y deja de aparecer en el listado.
- **Facturación electrónica.** *Todavía no está activa: falta el certificado y el CUIT del contribuyente.* Hasta que se configure, las ventas se cierran con **Confirmar venta** y funcionan con normalidad.

---

## Cómo funciona la cuenta corriente de un cliente

Cuando le fiás a un cliente, el sistema le lleva la cuenta solo.

**1. La deuda se genera sola.** Al confirmar una venta con un pago en **Cuenta corriente**, esa deuda queda cargada a nombre del cliente. No hay que anotarla aparte.

**2. Consultás el estado cuando querés.** Desde **Clientes**, entrás a la cuenta corriente del cliente y ves el saldo actual y todos los movimientos, con filtros por fecha y por tipo. El saldo se calcula en el momento, sumando todo lo que debe y restando lo que pagó.

Los movimientos se identifican por su origen: **venta a cuenta corriente** (la deuda que generó una venta), **pago** (lo que el cliente entregó) y **ajuste** (una corrección manual).

*Importante: por ahora esta pantalla es solo de consulta.* La deuda se carga sola cuando fiás en una venta, pero **todavía no hay una pantalla para registrar el pago del cliente ni para hacer un ajuste** — está previsto en el diseño pero no entregado. Hasta que se agregue, el cobro del fiado se sigue llevando por fuera del sistema.

---

## Cómo funciona la caja

**1. Durante el día se llena sola.** Cada venta confirmada que se cobra en efectivo, débito o tarjeta genera un ingreso automático. Los gastos que cargás generan el egreso.

**2. Cargás a mano lo que no vino de una venta.** Con **Movimiento manual** registrás un ingreso o un egreso suelto — por ejemplo, plata que ponés para cambio, o un retiro. Siempre pide un motivo.

**3. Cerrás el día.** Al final de la jornada, **Cerrar día** deja la caja del día cuadrada y bloqueada. Después de cerrarla no se pueden confirmar ventas nuevas con esa fecha.

**4. Cerrás el mes.** La pantalla mensual acumula los cierres diarios del mes y te deja hacer el cierre mensual.

En **Caja** ves los movimientos del día con sus totales de ingresos y egresos, y en **Cierres** el historial de los días ya cerrados, con quién los cerró.

---

## Cómo funcionan las entregas

Para las ventas que se llevan a domicilio.

**1. Se programa desde la venta.** En el detalle de una venta confirmada, **Programar entrega** abre la entrega con los datos del cliente y el total ya cargados.

**2. Elegís el tipo.** **Propia** (la hace el negocio, con un repartidor asignado) o **Tercerizada** (la hace un tercero). Cargás el costo, la fecha programada y la dirección.

**3. El repartidor la va actualizando.** La entrega pasa por estos estados:

| Estado | Qué significa |
|---|---|
| **Pendiente** | Programada, todavía no salió. |
| **En camino** | El repartidor arrancó el recorrido. |
| **Entregada** | Se entregó. |
| **No entregada** | No se pudo entregar. Queda registrado el motivo y se puede reagendar. |

---

## Catálogo y stock

**Productos.** Es el corazón del sistema. Cada producto tiene su código, nombre, marca, modelo y categoría, y todo el esquema de precios: precio de compra, porcentaje de recargo, IVA, precio de venta, bonificación y precio de oferta con fecha de vigencia. También podés cargarle el código de barras y códigos de barras alternos (los de fábrica, cuando el mismo producto viene con más de uno).

Los productos se pueden buscar por nombre, por código, por código de barras y por los códigos alternos — el buscador del listado los cubre a todos.

**Unidades de medida.** Cada producto se vende por **Unidad**, **Peso (Kg)**, **Metro** o **Bulto**. Si lo comprás en una unidad y lo vendés en otra, se carga el factor de conversión.

**Stock.** La pantalla de Stock te muestra qué tenés y te marca en rojo lo que está por debajo del mínimo. Desde ahí:

- **Ajustar** corrige la cantidad real de un producto. Siempre pide un motivo y queda registrado quién lo hizo y cuándo.
- **Historial** te muestra todos los ajustes hechos.
- **Verificado** es una marca que el producto recibe solo, en cuanto le hacés un ajuste. Sirve para ir ordenando el inventario de a poco: filtrás por "no verificados" y sabés qué te falta contar, sin frenar el negocio mientras tanto.

**Clasificación ABC.** El sistema clasifica los productos según cuánto se venden: **A** son los que más rotan, **B** los intermedios y **C** los de poca salida. Sirve para saber a qué prestarle atención cuando reponés.

**Marcas, Modelos y Categorías** son listas simples que se usan para clasificar los productos. Se pueden desactivar sin borrarlas: dejan de ofrecerse al cargar un producto nuevo, pero los productos que ya las tienen siguen igual.

---

## Gastos

En **Gastos** registrás lo que sale del negocio. Cada gasto lleva fecha, categoría (**Alquiler**, **Servicios**, **Sueldos**, **Impuestos**, **Flete** u **Otro**), monto, forma de pago (efectivo, transferencia, cheque o depósito) y una descripción.

También elegís el **impacto en caja**: si el gasto sale de la **caja chica** del día o si va a la **caja mensual**.

Un gasto no se edita: si te equivocaste, se **anula** y se carga de nuevo. Los gastos anulados dejan de aparecer en el listado para no confundir, pero no se borran — los seguís viendo eligiendo "Solo anulados" en el filtro de estado.

---

## Configuración: recargos por cuotas

En **Configuración → Recargos por cuotas** definís cuánto interés se le suma a una venta según en cuántas cuotas paga el cliente con tarjeta de crédito.

Están los planes de **1, 3, 6, 9, 12, 18 y 24 cuotas** y vos cargás el porcentaje de cada uno. Mientras lo editás, la pantalla te muestra un ejemplo en vivo sobre $100.000 para que veas cuánto termina pagando el cliente y de cuánto le queda cada cuota.

Si hay un plan que no querés ofrecer, lo desactivás con el interruptor: deja de aparecer al cargar un pago, y las ventas viejas que ya lo usaban siguen funcionando igual.

*Los cambios acá impactan en la próxima venta que cargues, sin necesidad de reiniciar nada.*

---

## Dashboard

La pantalla de inicio te da la foto del día y del mes: cuántas ventas hiciste hoy y por cuánto, los ingresos y egresos de la caja del día, si la caja está abierta o cerrada, cuántas entregas tenés pendientes, cuántos productos están en stock crítico, los gastos del mes por categoría y los productos más vendidos.

---

## Roles de usuario

Cada persona entra con su usuario y ve solo lo que le corresponde.

| Rol | Accesos |
|---|---|
| **Administrador** | Todo el sistema: ventas, clientes y cuentas corrientes, catálogo y stock con edición, caja, gastos, entregas, configuración de recargos y alta de usuarios. |
| **Vendedor** | Ventas completas (alta, edición y cierre), clientes y cuentas corrientes, y consulta de catálogo y stock. Puede programar entregas. No accede a caja, gastos ni configuración. |
| **Repartidor** | El listado de entregas, para ir actualizando el estado de sus recorridos. |

*Las altas de usuarios y la asignación de roles las hace un Administrador desde la pantalla de Usuarios. Un usuario que deja de trabajar en el negocio se bloquea en vez de borrarse, así queda el historial de lo que hizo.*

---

## Cosas que conviene saber

- **Los listados se filtran por cualquier columna que veas.** Además, el buscador general encuentra también por importe y por fecha: si escribís `1500` te trae las filas de $1.500,00, y si escribís `15/03/2026` te trae las de ese día.
- **Los filtros se recuerdan.** Si filtrás un listado, te vas a otra pantalla y volvés, los filtros siguen puestos. El botón **Limpiar filtros** los borra.
- **Nada se borra del todo.** Lo que se cancela o se anula deja de mostrarse en los listados para no confundir, pero queda guardado y se puede consultar con los filtros.
- **Todo queda registrado.** Cada movimiento guarda quién lo hizo y cuándo.
- **Modo oscuro.** El botón de la luna arriba a la derecha cambia el tema y se acuerda de tu preferencia.
- **Contraseñas.** Cada uno cambia la suya desde **Mi perfil → Cambiar contraseña**. Si alguien se la olvida, desde la pantalla de ingreso puede pedir el reinicio por correo.

---

## Todavía no está activo

- **Cobro de la cuenta corriente.** Hoy se puede fiar y consultar el saldo, pero falta la pantalla para **registrar el pago del cliente** y para hacer ajustes manuales. Es lo más importante de esta lista para el día a día.
- **Facturación electrónica AFIP.** El circuito está construido, pero falta cargar el certificado y el CUIT del contribuyente para poder emitir comprobantes reales. Mientras tanto, las ventas se cierran con **Confirmar venta** y el negocio funciona con normalidad.
- **Anulación de una venta ya confirmada.** Un borrador se cancela sin problema, pero una venta confirmada todavía no se puede revertir desde el sistema.
- **Compras a proveedores, cuenta corriente de proveedores y notas de crédito** quedaron fuera de lo entregado hasta acá.

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
