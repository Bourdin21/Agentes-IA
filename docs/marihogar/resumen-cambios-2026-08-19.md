# Olvidata**Soft**
---

**marihogar — Mejoras del 19 de agosto**
**OlvidataSoft · Agosto 2026**

## Sobre el día

Hoy trabajamos sobre varios pedidos puntuales que nos hiciste, todos ya probados y funcionando en el sistema real (no en modo de pruebas). Te dejamos el detalle de cada cambio.

## Cambios entregados

- **Listado de ventas:** ahora se ve y se puede ordenar por número de venta, el buscador del listado ya funciona correctamente, y las ventas sin cliente cargado muestran "Consumidor Final" en vez de quedar vacías.
- **Ventas con descuento del 100%:** ya se pueden cargar y confirmar ventas con ítems bonificados al 100% (antes el sistema lo bloqueaba con un error de precio inválido).
- **Fecha de la venta editable:** como Administrador podés elegir la fecha real de una venta, por ejemplo para cargar ventas de días anteriores sin que queden con la fecha de hoy.
- **Facturas reales cargadas:** registramos en el sistema las 6 facturas de AFIP/ARCA que ya habías emitido la semana pasada por fuera del sistema, cada una con los productos que efectivamente vendiste, para que tu historial quede completo.
- **Diseño de la factura AFIP:** rediseñamos el PDF de la factura para que se vea igual al formato oficial de AFIP/ARCA, con los datos reales de tu empresa (razón social, domicilio, condición frente al IVA, etc.). También corregimos un error de configuración en el Punto de Venta que, de no detectarse, hubiera hecho que el sistema numerara mal las próximas facturas reales.
- **Fecha de compra y de recepción de mercadería editables:** ahora podés elegir la fecha real en que se hizo una compra y la fecha real en que recibiste la mercadería, en vez de que el sistema use siempre la fecha de hoy — útil para cargar compras de días anteriores.
- **Pagos de compra programados:** un pago de una orden de compra ahora puede tener una fecha tentativa a futuro. Cuando llega esa fecha, el sistema te avisa con una notificación que tenés un pago por confirmar — y ese pago no se descuenta de la deuda con el proveedor hasta que vos lo confirmés de verdad.
- **Cheques entregados a proveedores:** corregimos que un cheque contara como pagado apenas se entregaba. Ahora recién cuenta como pagado cuando lo marcás **Acreditado** (cuando el banco lo cobra) — así el saldo pendiente de la compra refleja la realidad y no baja a $0 antes de tiempo. También corregimos los cheques que ya tenías cargados con este problema, para que tu Cuenta Corriente de proveedores quede al día.
- **Proyección financiera:** ahora también contempla los pagos de compra que ya programaste con fecha futura, para una proyección más precisa de tu caja.
- **Carga de productos:** los campos de % de descuento y % de recargo ahora son opcionales — no hace falta completarlos si no aplican.
- **Etiquetas de precio en ventas y productos:** los dos precios del producto ahora se llaman **"Precio efectivo" / "Precio transferencia"** en todas las pantallas (antes "Negro"/"Con IVA", después "Precio de lista").
- **Precio transferencia editable a mano:** en la ficha del producto, dejó de ser un valor fijo calculado (+21% del efectivo) — lo escribís vos mismo, sin ninguna sugerencia automática.

## Qué gana tu negocio con esto

- El saldo que le debés a cada proveedor (y el de tu caja proyectada) ahora refleja la plata real que salió, no la que "prometiste" con un cheque todavía sin cobrar.
- Podés cargar ventas y compras de días anteriores sin que se mezclen con las del día en que las cargás — útil para poner al día operaciones atrasadas.
- Tus facturas AFIP van a salir numeradas y con el formato correcto desde la primera vez que factures de verdad.

## Próximo paso sugerido

Te pedimos que pruebes vos: cargar un pago de compra con cheque y confirmar que el saldo pendiente se ve correcto hasta que lo acredités, y cargar una compra o venta con fecha pasada para chequear que se ve como esperás. Cualquier cosa que no se sienta bien, avisanos.

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
