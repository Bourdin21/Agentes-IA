# Memoria - Documentador

## Proyecto: ganaderia
## Ultima actualizacion: 2026-09-07

## Definiciones vigentes

### Alcance entregado al cliente

**Iteracion v17 — Descuento comercial antes del IVA + posicion de IVA en el Tablero Anual (2026-09-07)**

Resumen del sprint: el cliente pidio dos cosas concretas despues de usar el sistema en produccion. Primero, poder aplicar un **descuento sobre el total antes de calcular el IVA**, tanto en las ventas como en las compras, cargable en porcentaje o en importe. Segundo, ver en el tablero economico **cuanto IVA generan las ventas y cuanto las compras**, para anticipar su posicion antes de que se la informe el contador.

Cambios entregados:
- **Descuento opcional** en facturas de venta y en egresos, cargable indistintamente en **porcentaje o en importe** (los dos campos se completan solos; el ultimo tocado manda). Se resta del Subtotal para dar el **Neto gravado**, y ese neto es la base de **todos** los impuestos: IVA, Ingresos Brutos y Otras percepciones en ventas; IVA en compras. El sistema no permite un descuento que deje el total en cero o en negativo.
- **Reajuste de cuotas al editar una factura**: si el total cambia, el sistema avisa antes de guardar (total anterior, nuevo y diferencia) y ofrece redistribuir la diferencia entre las cuotas **respetando la proporcion cargada** y sin mover las fechas de vencimiento. Nunca reajusta por su cuenta.
- **Grafico de IVA de compras y ventas** en el Tablero Anual, con linea de saldo y KPI del periodo. Va por **fecha del comprobante** (devengado), no por fecha de cobro o pago — a diferencia del grafico de flujo de caja que ya existia. Los comprobantes anulados no computan. Rotulado en la propia pantalla como informativo y **no un Libro IVA**.
- **Tres correcciones**, dos de ellas serias y preexistentes: las cuotas generadas con "Generar sugerido" no se podian guardar (el sistema rechazaba el guardado con un mensaje que parecia un error de cuentas, cuando en realidad era un problema interno de interpretacion de decimales); "Guardar cambios" al editar una factura no hacia absolutamente nada; y el total del egreso quedaba en cero en pantalla mientras se completaba el formulario.
- Las facturas y egresos **ya cargados no se tocaron**: quedan sin descuento y con exactamente los mismos totales de siempre.

### Pendientes o fuera de alcance

- Un unico descuento **global por comprobante**; no hay descuento por item ni acumulacion de descuentos, y no se registra un motivo de descuento.
- El grafico de IVA **no reemplaza un Libro IVA**: no contempla notas de credito ni percepciones. Esta explicitado en la pantalla.
- Queda abierto un detalle menor (BUG-G-011): el validador en vivo del descuento no marca un porcentaje negativo, aunque el servidor siempre lo rechaza — no hay riesgo de dato incorrecto guardado.
- El otro sistema similar (`ganaderia - fausto`) no recibe estos cambios.

### Beneficios comunicados

- La factura refleja lo que realmente se va a cobrar: el descuento entra en la base imponible, no despues, que es como se factura de verdad.
- Editar una factura deja de ser una tarea de recalculo manual: el sistema muestra el desvio y ofrece corregirlo respetando el reparto que armo el usuario.
- El cliente puede anticipar su posicion de IVA mes a mes sin esperar al contador, con la salvedad contable escrita en la propia pantalla para que no se use como lo que no es.
- Se recupero un flujo que estaba roto en produccion: la edicion de facturas y el boton "Generar sugerido" no funcionaban, y nadie lo habia reportado.

### Proximo paso sugerido

Desplegar la version junto con la migracion de base (agrega dos columnas por comprobante con valor cero, sin modificar ningun dato existente). Las dos correcciones criticas de la edicion de facturas deben viajar en el **mismo** despliegue. Despues del despliegue, conviene avisarle al cliente que revise una factura existente y confirme que sus totales quedaron intactos.

## Historial de ajustes

- 2026-07-02: primera entrega de este documento. Iteracion v11 — pagos multiples de Egreso (cheques diferidos + pago compensatorio) implementada y probada. QA con veredicto "apto para release con deuda tecnica documentada" (validacion de la migracion contra una copia real de produccion queda pendiente del despliegue).
- 2026-09-07: iteracion v17 — descuento comercial pre-IVA (ventas y compras), reajuste de cuotas al editar, y grafico de IVA compras/ventas en el Tablero Anual. Documento de novedades para el cliente en `docs/ganaderia/novedades-entrega-2026-09-07.md` (repo) y manual de usuario actualizado a v1.1: se reescribio la seccion 2 (seguia describiendo el panel unico previo a la separacion Dashboard/Tablero Anual), se documento el descuento y el reajuste en la seccion 5, y se corrigio la seccion 8 (Egresos), que todavia describia un importe unico sin IVA y sin pagos multiples. QA con veredicto **apto para deploy condicionado** a que las dos correcciones criticas viajen en el mismo despliegue. Etapa de presupuesto salteada por decision explicita del usuario.
