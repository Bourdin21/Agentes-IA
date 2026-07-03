# Olvidata**Soft**

---

**Compras al proveedor: armado manual y cuenta corriente**
**OlvidataSoft · Julio 2026**

---

## Sobre el proyecto

Este sprint cambia cómo tu equipo compra mercadería al proveedor y cómo se lleva su cuenta dentro del sistema. Antes, cada vez que se confirmaba un pedido de un cliente, el sistema armaba una compra automáticamente — y ahí se mezclaba, sin querer, el stock propio (que ya está pagado) con lo que realmente había que pedirle al proveedor. A partir de ahora, tu equipo arma cada compra a mano, eligiendo justo lo que corresponde, y la cuenta corriente del proveedor dentro del sistema quedó igual al extracto real que él les manda.

---

## Cómo funciona: armar una compra al proveedor — paso a paso

**1. Elegís qué comprar.** Desde los pedidos ya confirmados de tus clientes, seleccionás los artículos puntuales que querés comprarle al proveedor en ese momento — no hace falta tomar el pedido completo, ni esperar a nada automático.

**2. Armás la compra.** El sistema junta esos artículos en una orden de compra nueva y calcula el total a pagar.

**3. La confirmás.** Al confirmar la compra, se genera la deuda correspondiente en la cuenta corriente del proveedor — como una factura recibida.

**4. Marcás la recepción.** Cuando la mercadería llega, marcás la compra como recibida.

**5. Registrás el pago cuando corresponda.** Cargás el pago (efectivo o transferencia) o una nota de crédito directamente contra el saldo general del proveedor, sin tener que indicar a qué compra puntual corresponde — igual que en la vida real, donde un pago puede cubrir varias facturas juntas.

*Esta función está disponible para el rol de Administración de tu equipo.*

**Casos especiales contemplados:**
- Si cancelás el pedido de un cliente y alguno de sus artículos ya estaba incluido en una compra recién armada (todavía no confirmada), el sistema lo saca solo de esa compra.
- Si la compra ya fue confirmada, el sistema no te deja cancelar ese pedido sin antes sacar el artículo de la compra — para que no se pierda de vista una compra ya en marcha.

---

## Cambios entregados

- El stock propio ya no aparece en el detalle de una compra al proveedor — ya está pagado, no correspondía mostrarlo ahí.
- El listado de compras muestra primero la fecha, ordenado de la más reciente a la más antigua.
- Nueva pantalla para armar una compra a mano, eligiendo los artículos puntuales de los pedidos confirmados.
- El estado de una compra y el estado del pedido de un cliente dejan de estar atados entre sí — cada uno se gestiona por separado.
- Nueva cuenta corriente del proveedor dentro del sistema, con el mismo formato que su extracto real: fecha, hora, detalle, debe, haber y saldo.
- Se puede cargar un pago o una nota de crédito del proveedor sin tener que asociarlo a una compra puntual.

## Beneficio para tu equipo

Ganás control sobre cuándo y qué comprarle al proveedor, en vez de que el sistema lo decida solo. Y ganás precisión para conciliar cuentas: la cuenta corriente del sistema ahora se puede comparar línea por línea contra el extracto real del proveedor, sin traducir formatos ni adivinar a qué corresponde cada pago.

## Pendientes

- Aplicar estos cambios en el sistema de producción — necesita tu aprobación y un respaldo previo de la base de datos, por tratarse de datos de plata.
- Hacer, en conjunto, una prueba a mano en el navegador del circuito completo: armar una compra y cargar un pago o nota de crédito.
- Dos migraciones de sprints anteriores (reversión de pedidos, stock propio) siguen pendientes de producción — no las generó este sprint, ya estaban así.

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
