# Olvidata**Soft**
---

**marihogar — Etapa 1 completada: el negocio operando en el sistema**
**OlvidataSoft · Julio 2026**

## Sobre el proyecto

Terminamos la Etapa 1 completa del sistema de gestión comercial: todo lo necesario para reemplazar Contagram y operar tu negocio de decoración y hogar de punta a punta ya está implementado — catálogo, stock, presupuestos, ventas, entregas, compras a proveedores, cheques, caja, gastos, proyección financiera y facturación electrónica. Los 16 módulos de la Etapa 1 están construidos, revisados y aprobados internamente. Antes de que lo uses en producción, falta que lo pruebes vos siguiendo las guías que dejamos y que nos confirmes un par de cosas pendientes de tu lado (ver abajo).

## Cambios entregados

- **Catálogo de productos y stock:** cargá tus productos con precio de compra/venta, marca, modelo, categoría y hasta 5 fotos. El stock se descuenta y se incrementa solo con cada venta o compra, y te avisa cuando un producto está por debajo del mínimo.
- **Presupuestos y ventas:** armá un presupuesto en segundos, generá el PDF y convertilo en venta con un clic. La pantalla de ventas la trabajamos especialmente para que sea rápida en el mostrador: buscás el producto, se arma el carrito, cobrás con uno o varios medios de pago combinados, y listo — pensada para que una venta completa te lleve menos de un minuto.
- **Entregas a domicilio:** programá la entrega, y desde el celular en la casa del cliente registrás el cobro (si quedaba pendiente) y marcás la entrega como completada.
- **Compras a proveedores y cheques:** armá órdenes de compra, marcalas como recibidas para que el stock suba solo, y pagá con efectivo, transferencia, cheque o depósito. Los cheques a 30/60/90 días se acreditan solos cuando vencen, y si un banco te rechaza uno, lo marcás vos y el sistema reabre la deuda automáticamente.
- **Cuenta corriente y caja:** siempre sabés cuánto tenés en el local y cuánto le debés a cada proveedor, con el historial completo de movimientos. La caja mensual te muestra el resumen del mes con comparativo contra el mes anterior.
- **Gastos y proyección financiera:** cargá tus gastos operativos (alquiler, sueldos, servicios) y mirá una proyección de cómo viene tu caja para el próximo período, combinando tu historial con los compromisos que ya sabés que vienen (cheques por vencer, pagos pendientes a proveedores).
- **Aumento masivo de precios:** actualizá precios por marca, categoría o modelo en un solo paso, con una vista previa de los precios nuevos antes de confirmar — nunca se aplica nada sin que lo confirmes.
- **Panel de inicio (dashboard):** al entrar al sistema ves de un vistazo las ventas del período, el stock crítico, los cheques por vencer y los productos que más se venden.
- **Facturación electrónica AFIP/ARCA:** desde cada venta elegís qué ítems facturar (todo, una parte, o un solo producto) y el sistema emite la Factura A o B directamente contra AFIP.
- **Usuarios y roles:** vos (Administrador) tenés acceso a todo; tu equipo de venta (Vendedor) accede a contactos, presupuestos, ventas, entregas y facturación, sin ver precios de costo ni información financiera del negocio.

## Qué gana tu negocio con esto

- Dejás de llevar el control en Contagram y planillas sueltas: todo el ciclo (venta, stock, compras, caja) queda en un solo sistema, con trazabilidad completa de cada movimiento.
- Menos carga manual: el stock, la cuenta corriente y la caja se actualizan solos con cada operación, en vez de que alguien tenga que ir anotando todo aparte.
- Anticipás la caja del próximo mes en vez de enterarte sobre la marcha, gracias a la proyección financiera.
- Tu equipo de venta tiene una pantalla de ventas pensada para ser rápida en el mostrador, no un formulario largo de carga.

## Pendientes de tu parte

- **Certificado digital de AFIP/ARCA (.p12):** el módulo de facturación ya está terminado y probado a nivel de código, pero para emitir facturas reales necesitamos el certificado de tu CUIT. Mientras tanto, el sistema queda configurado en modo de pruebas de AFIP (no factura de verdad hasta que lo cambiemos a modo producción con tu certificado). Te vamos a pedir ayuda para tramitarlo.
- **Probar el sistema en tu navegador:** el equipo revisó todo el código línea por línea y hay evidencia técnica de que la lógica funciona (incluyendo pruebas reales contra la base de datos), pero **todavía nadie lo probó haciendo clic en las pantallas como lo vas a usar vos**. Te dejamos, para cada tramo entregado, una guía de pasos concretos para que lo recorras — es importante que la hagas antes de dar la Etapa 1 por definitivamente cerrada. Podemos coordinar una sesión juntos si preferís hacerlo acompañado.
- **Etapa 2 (captación automática por WhatsApp y CRM de contactos)** queda en pausa, tal como nos pediste — no la vamos a tocar hasta que nos digas que arranquemos. Cuando quieras retomarla, vamos a necesitar de tu lado un número de WhatsApp dedicado para el bot y el listado de tu catálogo para configurar las preguntas automáticas por categoría de producto.

## Consideraciones

- Durante el desarrollo hubo un incidente interno de proceso (dos procesos nuestros trabajando en paralelo sobre el mismo módulo por error nuestro, no un problema de tu sistema) que generó una alerta de seguridad. La investigamos a fondo, confirmamos que no hubo ningún riesgo real ni código malicioso, y quedó todo documentado. Te lo contamos por transparencia, aunque no requiere ninguna acción de tu parte.
- La facturación AFIP, al no tener todavía el certificado real, no pudo probarse contra AFIP de verdad — solo por revisión de código. Es el único módulo de la Etapa 1 con esa salvedad.

## Próximo paso sugerido

Te pedimos que recorras las guías de prueba que dejamos módulo por módulo (podemos coordinar una videollamada para hacerlo juntos si preferís), nos confirmes que todo se ve y funciona como esperás, y nos acerques el certificado de AFIP cuando lo tengas para pasar la facturación a modo producción. En paralelo, avisanos cuándo querés que arranquemos la Etapa 2.

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
