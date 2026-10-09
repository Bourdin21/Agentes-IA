# Olvidata**Soft**

---

**La Platense — Lo que se agregó al sistema**

**OlvidataSoft · Octubre 2026**

## Sobre el proyecto

Esta ronda agrega las seis cosas que me pediste después de usar el sistema un tiempo, más el circuito de devoluciones y notas de crédito que quedaba pendiente del alcance original. Todo está construido y probado.

- Ahora podés **vender con factura o sin factura**, y el precio se ajusta solo.
- Podés **facturar solo una parte** de lo que entregaste, y lo demás queda pendiente para facturar después.
- Los **intereses de tarjeta** se configuran por tarjeta y por cantidad de cuotas, y los cambiás vos cuando la procesadora los cambia.
- Podés **pagarle a un proveedor en varios echeqs** a 0, 30, 60, 90 y 120 días, de una sola vez.
- La **transferencia** es un medio de pago propio y ya no se mezcla con el efectivo en el arqueo.
- Podés **registrar una devolución** de mercadería, que vuelve al stock, y emitir la **nota de crédito** cuando lo devuelto estaba facturado.

## Cómo funciona vender con o sin factura — paso a paso

**1. Al abrir la venta elegís la condición.** Arriba, junto al cliente, hay dos opciones: con factura o sin factura. Se elige antes de cargar los productos, porque cambia el precio que le cantás al mostrador.

**2. Sin factura, el precio baja.** El sistema saca el impuesto de cada renglón y el total pasa a ser la suma de los precios netos. Igual te muestra abajo, en chico, cuánto sería **con** factura, así podés contestar "¿y con factura cuánto sale?" sin tocar nada.

**3. Al confirmar, la condición queda fija.** Una venta cerrada no cambia de condición. Si después el cliente pide factura, se factura desde el paso de abajo.

**4. Si después pedís factura de una venta que se cobró sin impuesto**, el sistema te avisa **antes de emitir** cuánto impuesto no estaba cobrado y te muestra el importe exacto. Al confirmar, ese importe queda **como deuda del cliente en su cuenta corriente**, con el número de la factura que la generó. La venta no se toca: queda cobrada por un monto y facturada por otro, y los dos están bien.

**Casos especiales contemplados:**
- Si el cliente tiene CUIT y elegís "sin factura", el sistema te lo avisa pero **no te lo impide** — la decisión es tuya.
- El recargo por cuotas se calcula sobre el total que corresponda a la condición elegida.

## Cómo funciona facturar una parte — paso a paso

**1. La venta confirmada funciona como el remito.** Entregás la mercadería y la venta queda cerrada, con o sin factura.

**2. Cuando hay que facturar, elegís qué renglones y qué cantidad.** La pantalla muestra, por producto, cuánto vendiste, cuánto ya facturaste y cuánto queda. Podés facturar 2 de 5 bultos y dejar el resto.

**3. No se puede facturar más de lo que vendiste.** El sistema lo controla por renglón.

**4. En el listado de ventas ves en qué estado está cada una:** confirmada, facturada en parte, o facturada. Solo "facturada en parte" aparece resaltada, porque es la que tiene algo pendiente que hacer.

## Cómo funciona el plan de echeqs — paso a paso

**1. Al pagarle a un proveedor elegís echeq.** Se abre el plan de pago.

**2. Elegís los plazos.** 0, 30, 60, 90 y 120 días, los que correspondan. El sistema arma un cheque por plazo, reparte el importe en partes iguales y te deja cambiar cada monto a mano.

**3. Cargás número de cheque y banco en cada uno.** El vencimiento se calcula solo, sumando los días a la fecha del pago.

**4. Ningún cheque mueve plata hasta que lo confirmás.** Quedan como compromiso: ni la caja ni la deuda del proveedor se tocan. El día que el banco lo debita, lo confirmás y ahí sale la plata.

**5. La fecha del débito viene propuesta y la podés cambiar.** Viene con el vencimiento del cheque, pero si el banco debitó otro día, lo corregís — y conviene hacerlo, porque es lo que hace que el arqueo coincida con el extracto.

**El sistema te avisa cuando un cheque está por vencer**, la primera vez que alguien entra al sistema ese día.

## Cómo funciona una devolución — paso a paso

**1. Entrás a la venta y elegís qué devolver.** Por renglón, con la cantidad. El motivo es obligatorio.

**2. Antes de confirmar, el sistema te muestra exactamente qué va a pasar:** cuánta mercadería vuelve al stock, cuánta plata se devuelve y de dónde sale.

**3. La plata se devuelve de donde entró.** Si se cobró en efectivo, sale de la caja; si fue fiado, se le descuenta de la cuenta; si fue con tarjeta, se devuelve el importe **sin el recargo de cuotas**, porque ese recargo lo cobró la financiera y no vuelve.

**4. Si lo devuelto estaba facturado, se emite la nota de crédito** contra esa factura. Si no estaba facturado, no se emite ningún comprobante: la devolución queda completa igual.

**5. Si devolvés todo, la venta queda anulada.** Si devolvés una parte, la venta sigue como estaba y la devolución queda registrada en su detalle.

**Casos especiales contemplados:**
- No se puede devolver más de lo que se vendió, ni devolver dos veces lo mismo.
- No hay cambio por otro producto: un cambio se hace como una devolución más una venta nueva.
- Si una nota de crédito corresponde a una factura que te había generado deuda de impuesto, esa deuda **se devuelve también**. No queda nada colgado.

## Lo que además se corrigió

- **El cierre de caja podía firmar un día con el total en cero** si alguien estaba cargando algo en ese momento. El arqueo quedaba firmado con números que cerraban entre sí y eran falsos. Está corregido.
- **Un vendedor podía cambiar el precio de un producto** en la venta. Ahora el precio lo recalcula el sistema y solo el administrador lo puede modificar.
- **Las marcas, categorías, modelos y tarjetas dadas de baja** todavía se podían usar. Ya no, pero lo que se cargó antes con una de ellas sigue funcionando y se puede editar.

## Lo que falta, y de qué depende

1. **Facturación electrónica real.** El circuito está construido y probado completo, pero necesito **el certificado digital y el CUIT** del contribuyente para conectarlo con AFIP. Hasta entonces las facturas y notas de crédito se emiten en el sistema sin número oficial.
2. **Subir todo esto al sistema que usás.** Está listo y ensayado sobre una copia de tus datos reales: las actualizaciones tardan 14 segundos y no se pierde nada. Me falta recuperar una contraseña de acceso al servidor que fue cambiada. **Hasta que suba, nada de esto está disponible en el sistema que usás hoy.**

## Lo que necesito de tu parte

- El **certificado digital** de AFIP y el CUIT del contribuyente, para habilitar la facturación. El trámite lo hacés vos en la página de AFIP y suele tardar unos días.
- Avisarme **un horario conveniente** para subir la actualización: el sistema queda unos minutos sin operar.
- Si tenés **dos o tres listas de precios más** de proveedores distintos, mandámelas. Las necesito para cotizar la importación automática de listas, que todavía no está presupuestada.

---

**Olvidata Soft — bourdinjoaquin@gmail.com**
