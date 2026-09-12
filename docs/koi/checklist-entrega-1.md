# Olvidata**Soft**

---

**Checklist — Entrega 1 · Sistema KOI Dumplings**
**OlvidataSoft · Septiembre 2026**

Resumen de los arreglos y cambios de la Entrega 1, agrupados por pantalla. Las referencias *Pedido N* corresponden a la numeración de la lista de pedidos de la entrega.

## Ingreso y usuarios

- [ ] **1. Recuperar contraseña** · *Pedido 1* — Link visible en la pantalla de ingreso. El mail llega en segundos, la respuesta es la misma exista o no la cuenta, y el link sirve una sola vez.
- [ ] **2. Rol Encargado** — Disponible al crear usuarios. Editar un Encargado ya no lo cambia a Inversor al guardar.
- [ ] **3. Permisos del Encargado** · *Pedido 9* — Carga ventas y gastos, pero no puede cerrar el mes, ni corregir meses cerrados, ni ver la parte de inversores. El bloqueo está del lado del servidor, no sólo en la pantalla.
- [ ] **4. Menú** · *Pedido 2* — «Sistema» vuelve a estar disponible para el Administrador. Cámaras se quitó del menú y su pantalla quedó bloqueada. Auditoría queda reservada a soporte técnico.

## Inversores

- [ ] **5. Editar un inversor guarda** · *Pedido 12* — El alta, la edición y la baja no se guardaban, aunque mostraban el cartel de éxito.
- [ ] **6. Tipo de cambio y fecha de ingreso** — Dos datos nuevos en la ficha de cada inversor, ya cargados para los 15 con los valores del Excel.

## Estado de Resultados

- [ ] **7. Importes sin centavos** · *Pedido 5* — Se muestran redondeados pero se guardan con centavos. El tipo de cambio, los porcentajes y los puntos conservan sus decimales.
- [ ] **8. Campos numéricos sin flechitas** · *Pedido 6* — En el celular se abre el teclado numérico.
- [ ] **9. Sacar un gasto de un mes puntual** · *Pedido 11* — Se puede sacar un concepto de un mes y volver a agregarlo (el caso de la fumigación). Sólo con el importe en 0, para que nunca desaparezca un gasto con plata adentro.
- [ ] **10. Dar de baja un concepto del catálogo** · *Pedido 7* — Deja de aparecer en los meses siguientes y se conserva, con su importe, en los meses anteriores.
- [ ] **11. Meses históricos sin conceptos duplicados** · *Pedido 8* — Se ordenaron los conceptos de los 18 meses cerrados, con los totales idénticos al centavo.
- [ ] **12. Ventas desde Ayres** — Las ventas del mes se traen del sistema de caja, excluyendo las anuladas.
- [ ] **13. Editar gastos históricos** — Los conceptos con la etiqueta «Histórico» se editan como cualquier otro.
- [ ] **14. Corregir un mes cerrado sin reabrirlo** — Se puede cambiar un gasto de un mes cerrado: recalcula las liquidaciones pendientes y no toca las ya pagadas, con un aviso previo que detalla ambas.
- [ ] **15. Mover un gasto a otro concepto** — Botón ⇄ para reasignar un gasto. Si el concepto de destino ya tiene importe, se suman; el total del mes no cambia.
- [ ] **16. Conceptos por porcentaje** — Regalías, Cánon y Previsiones ya no se recalculan solos al abrir un mes. Reemplazar un valor cargado a mano pide confirmación, también al guardar las ventas.
- [ ] **17. Julio, agosto y enero 2026 conciliados** — Los tres meses coinciden al centavo con el Excel. Gastos: julio $ 57.287.371,34, agosto $ 58.034.260,47 y enero $ 55.112.086,89.

## Reparto General

- [ ] **18. Orden de las columnas de importe** · *Pedido 13* — Ordenan por valor y no como texto.

## Dashboard y Mes actual

- [ ] **19. Cubiertos por día** · *Pedido 15* — Reemplaza al ticket promedio. El resultado del mes se muestra en pesos y en dólares.
- [ ] **20. Gráficos quitados** · *Pedidos 16, 17 y 18* — Se sacaron «facturado vs informal» y las ventas por canal con IVA. El desglose por rubro ocupa ese espacio.
- [ ] **21. Tortas y barras con los valores correctos** — Los números llegaban mal a tres gráficos. Un mes con pérdida ahora se ve como pérdida.
- [ ] **22. Evolución diaria** · *Pedidos 20 y 22* — Plata y cubiertos en un mismo gráfico, cada uno con su escala.
- [ ] **23. Tarjetas parejas** · *Pedidos 19, 21 y 29* — En computadora y en celular, para todos los usuarios. Mes actual suma la tarjeta de Cubiertos.
- [ ] **24. Rentabilidad del mes** — Aclarada como «del total vendido». Se muestra una sola vez porque en pesos y en dólares da el mismo valor.
- [ ] **25. Períodos sin datos** — Elegir un mes sin ventas cargadas ya no deja la pantalla en blanco.

## Vista del inversor

- [ ] **26. Sin desglose facturado / informal** · *Pedido 23* — Ninguna pantalla del inversor muestra ventas A y B ni etiquetas que lo sugieran. El Administrador sigue viendo el desglose.
- [ ] **27. Recupero en pesos corregido** · *Pedido 25* — Se calcula con el tipo de cambio de ingreso de cada inversor, como en el Excel. Antes daba igual que en dólares.
- [ ] **28. Rentabilidad mensual promedio** — Se divide por los meses desde el ingreso de cada inversor hasta el último mes cerrado.
- [ ] **29. Mi Inversión** — Dólares y pesos en tarjetas, gráfico y tabla. Tarjetas reordenadas: dólares arriba, pesos abajo.
- [ ] **30. Reporte de rendimiento** · *Pedidos 26, 27 y 28* — Suma las cifras en pesos y la comparativa contra el mercado, con valores configurables. El tilde «Se muestra» de cada índice ahora se guarda.
- [ ] **31. Privacidad entre inversores** — Un inversor no puede ver el reporte de otro.

## Notificaciones de cierre

- [ ] **32. Vista previa del mail** · *Pedido 14* — Se ve el mail tal como le llega a cada inversor antes de enviarlo. Cancelar no envía nada.
- [ ] **33. Envío sólo desde Notificaciones de cierre** — Cerrar el mes ya no manda los mails: se envían desde esta pantalla, ubicada en el menú arriba de «Nueva Notificación».
- [ ] **34. Estado real de cada envío** — El historial marca «Enviado» sólo si el mail salió; si falla, queda «Fallido» con el motivo. Una tanda fallida se puede reenviar sin duplicarle el mail a nadie.
- [ ] **35. Acentos** — Corregidos en los títulos del historial.

## Importación desde Excel

- [ ] **36. Pantalla explicada** · *Pedido 30* — Indica cuándo usarla y cuándo no.
- [ ] **37. Reimportar no duplica** · *Pedido 8* — Volver a importar el mismo Excel actualiza los importes en lugar de sumarlos.
