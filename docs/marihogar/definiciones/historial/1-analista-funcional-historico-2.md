<!-- Archivado de docs/marihogar/definiciones/1-analista-funcional.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 1-analista-funcional - historico (3 bloques archivados)

- CR-77 — Nota de Crédito: elegir si se corrige la factura o se anula la venta
- CR-53 — Fecha de pago con Transferencia editable
- CR-54 — Registrar pago con Transferencia: admite fecha pasada (backdatear) al cargar

---

## CR-77 — Nota de Crédito: elegir si se corrige la factura o se anula la venta

Caso real de producción (23/09/2026, Venta #724): el usuario generó una Nota de Crédito para **anular la venta de verdad** (motivo "cambio por otro colchón"), pero la NC de CR-55 solo anula el comprobante ante AFIP y nunca toca `Venta.Estado` — la venta siguió viva y pagada. Para "deshacerla" el usuario borró el pago a mano, y `EliminarPagoAsync` recalculó el estado dejando la venta en **Pendiente**, con el stock descontado y sin pago. Venta inconsistente.

**Diagnóstico**: no es un bug de CR-55 sino un alcance incompleto. CR-55 se diseñó para un único escenario ("me equivoqué al facturar, quiero volver a facturar la misma venta"), pero en la operación la NC se usa también para el escenario opuesto ("esta venta no va más"). Los dos son legítimos y solo el usuario sabe cuál está haciendo.

**Alcance confirmado con el cliente**: al generar la Nota de Crédito el usuario elige explícitamente qué está haciendo, con **"Corregir la factura" como opción por defecto** (no cambia nada para quien ya venía usando la pantalla):
- **Corregir la factura** (default, comportamiento histórico de CR-55): se anula la factura ante AFIP y la venta queda disponible para volver a facturarse. La venta **no** cambia de estado. Caso típico: CUIT mal cargado, cliente equivocado.
- **Anular la venta**: además de la NC, la venta se **cancela** con todo el circuito que ya existe (`VentaService.CancelarAsync`): revierte el stock, da de baja los pagos que quedaron en acreditación Pendiente, reversa en Cuenta Corriente del local **solo lo efectivamente acreditado** (CR-64/CR-65) y deja el `MotivoCancelacion` con la referencia a la NC.

**Arquitectura**: la orquestación vive en `ComprobantesAfipController.GenerarNotaCredito`, **no** en `ComprobanteAfipService`. Motivo: `VentaService` ya inyecta `IComprobanteAfipService`, así que la dependencia inversa cerraría un ciclo de DI que revienta en runtime; el controller puede inyectar los dos sin problema. El flag viaja del form al controller y no entra al `GenerarNotaCreditoInput` (el service no lo usa: sería un campo muerto). El `VentaId` a cancelar se lee del comprobante server-side, nunca del form (sería manipulable).

**Dos transacciones separadas, deliberadamente**: la NC ya emitida en AFIP es irreversible, así que un fallo al cancelar la venta **nunca** hace rollback de la NC. En ese caso el mensaje al usuario dice explícitamente que la NC sí se emitió y que la venta hay que cancelarla a mano — para que no crea que tiene que volver a generar la NC (lo que además está bloqueado por la regla de a lo sumo 1 NC por factura).

**Guards de `CancelarAsync` sin cambios**: el de Entrega asociada se mantiene tal cual (una venta con entrega sigue sin poder cancelarse, y si falla se muestra el mensaje del `ServiceResult`). El de `TieneComprobanteAsociadoAsync` ya excluye desde CR-55/MH-013 las facturas anuladas por una NC Emitida, así que la venta cuya factura se acaba de anular pasa el guard sin tocarlo. Caso residual conocido: una venta facturada en **varias** facturas y anulada solo en una sigue bloqueada por la(s) otra(s) vigente(s) — es el comportamiento correcto y el mensaje del guard lo explica.

**Impacto en capas**: Web únicamente (`ComprobantesAfipController.cs`, `ComprobantesAfip/Details.cshtml`). Sin cambios en Application/Infrastructure/Domain. Sin migración EF.
## CR-53 — Fecha de pago con Transferencia editable

Pedido explícito del cliente (21/08/2026), en la misma entrega que el cierre de CR-52: "hacer que se pueda modificar la fecha de pago con transferencia de las compras".

`PagoOrdenCompra.Fecha` se fijaba una única vez, a `DateTime.UtcNow`, al registrar el pago — sin forma de corregirla después (ej. el pago se carga hoy pero la transferencia real se hizo días antes). Nuevo método `IPagoOrdenCompraService.ActualizarFechaPagoTransferenciaAsync(pagoOrdenCompraId, nuevaFecha)`, acotado a `Metodo=Transferencia` (pedido explícito — los demás métodos ya tienen su propio mecanismo: Cheque vía acreditación desde CR-46, el resto no fue pedido), nunca futura. Si el pago ya está `Pagado` (con su `MovimientoCCProveedor.Pago` ya posteado), la corrección se cascadea a ese movimiento para que el ledger de Cuenta Corriente no quede con una fecha distinta a la del pago que lo originó — mismo criterio de consistencia ya aplicado en CR-42/44/45/46. Disponible en cualquier estado de la OC (mismo criterio que la nota interna de CR-50), acción propia en `OrdenesCompra/Details.cshtml`: un ícono de lápiz junto a la fecha de cada pago con Transferencia abre un selector de fecha (SweetAlert2, mismo patrón visual que "Marcar recibida").

**Impacto en capas**: Application (`IPagoOrdenCompraService`), Infrastructure (`PagoOrdenCompraService.cs`), Web (`OrdenesCompraController.cs`, `OrdenesCompra/Details.cshtml`). Sin migración EF.
## CR-54 — Registrar pago con Transferencia: admite fecha pasada (backdatear) al cargar

Pedido explícito del cliente (21/08/2026): "registrar pago de las compras con transferencia el usuario quiere poder seleccionar fechas pasadas para cargar transferencias realizadas". Complementa CR-53 (que permite corregir la fecha después de registrado) con la posibilidad de cargarla bien desde el principio.

El campo "fecha tentativa de pago" (CR-44) ya existía en la pantalla de Registrar pago, pero tenía `min=hoy` — solo servía para programar un pago a futuro, cualquier fecha pasada quedaba descartada (el pago se registraba con `Fecha=ahora`, sin importar qué se hubiera tipeado). Para Transferencia específicamente (pedido explícito, mismo alcance que CR-53), ahora una fecha pasada en ese mismo campo **backdatea** el pago: queda `Estado=Pagado` de inmediato (no programado) pero con `Fecha` = la fecha real elegida, cascadeada también al `MovimientoCCProveedor.Pago` que se postea en el momento — mismo criterio de consistencia que el resto de los "fecha real" de esta sesión (CR-42/44/45/46/53). Una fecha futura sigue programando el pago exactamente como antes (CR-44 intacto); vacío sigue pagando "ahora". El `min=hoy` del datepicker se saca únicamente para Transferencia — el resto de los métodos (Efectivo/MercadoPago/Depósito) no fue pedido, mantienen el comportamiento anterior.

**Impacto en capas**: Infrastructure (`PagoOrdenCompraService.RegistrarPagoAsync`), Web (`OrdenesCompra/Details.cshtml`). Sin migración EF.
