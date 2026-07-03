# Memoria - Documentador

## Proyecto: ganaderia
## Ultima actualizacion: 2026-07-02

## Definiciones vigentes

### Alcance entregado al cliente

**Iteracion v11 — Pagos de compras con cheques diferidos (sistema `ganaderia - emo`)**

Resumen del sprint: hasta ahora, cada compra a un proveedor (Egreso) se registraba con una unica forma de pago que se daba por pagada al instante. En la práctica, muchas compras se pagan combinando uno o varios cheques diferidos — que no siempre cubren el total — mas un pago adicional en efectivo o transferencia por la diferencia. El sistema ahora soporta esa forma real de pagar.

Cambios entregados:
- Al cargar una compra (Egreso), ahora se puede agregar mas de un pago: efectivo, transferencia o cheque diferido, cada uno con su propio importe y fecha.
- Los cheques diferidos piden ademas la fecha de vencimiento (cuando se hacen efectivos). El sistema exige que la suma de todos los pagos coincida exactamente con el total de la compra.
- Los pagos en efectivo o transferencia impactan la caja al instante, igual que antes. Los cheques diferidos impactan la caja recien en su fecha de vencimiento, de forma automatica (mismo mecanismo diario que ya usa el sistema para acreditar los cobros a clientes).
- Si un cheque entregado a un proveedor rebota, se puede marcarlo como rechazado y despues regularizarlo: corregirlo si fue un error de carga, o registrar que se termino pagando de otra forma.
- Se preservo el historial de todas las compras ya cargadas: no se perdio ningun dato existente al aplicar el cambio.

### Pendientes o fuera de alcance

- Este cambio es exclusivo del sistema de este cliente (`ganaderia - emo`); no aplica al otro sistema similar de otro cliente (`ganaderia - fausto`).
- No se agrego edicion de una compra ya cargada (se mantiene: cargar y anular, igual que antes).
- La aplicacion de este cambio en el servidor de produccion real (con los datos reales del cliente) queda pendiente del proceso de despliegue, con resguardo previo de la informacion.

### Beneficios comunicados

- El sistema ahora refleja como se paga realmente: varios cheques con distintas fechas mas un pago de ajuste, en vez de forzar una sola forma de pago por compra.
- La caja/cuenta corriente queda mas precisa: un cheque diferido ya no aparece pagado antes de tiempo, sino recien cuando efectivamente se hace efectivo.
- Se gana trazabilidad ante un cheque rebotado: queda registrado el rechazo y como se resolvio despues, sin perder el historial.

### Proximo paso sugerido

Validar el cambio en un ambiente de prueba con datos reales (o una copia resguardada de los datos de produccion) antes de aplicarlo al sistema en vivo, y coordinar una ventana breve para el despliegue con resguardo previo de la informacion existente.

## Historial de ajustes

- 2026-07-02: primera entrega de este documento. Iteracion v11 — pagos multiples de Egreso (cheques diferidos + pago compensatorio) implementada y probada. QA con veredicto "apto para release con deuda tecnica documentada" (validacion de la migracion contra una copia real de produccion queda pendiente del despliegue).
