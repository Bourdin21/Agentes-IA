# Memoria - Presupuestador

## Proyecto: ganaderia
## Ultima actualizacion: 2026-04-22

## Alcance funcional resumido

Presupuesto funcional para un sistema de gestion ganadera con tres ejes principales: ingresos, egresos y stock, mas transversales de caja, dashboard, catalogos operativos, usuarios y novedades. La estimacion se basa en las definiciones vigentes de analisis funcional v10, diseno funcional v1 y arquitectura tecnica v1.

Resumen economico recomendado:
- Horas base estimadas: 81.5 h
- Horas finales estimadas: 101.0 h
- Tasa aplicada: USD 12 / h
- Total estimado: USD 1,212
- Migraciones EF: si, 2 migraciones previstas (`Ganaderia_Catalogos` y `Ganaderia_Operativa`)

## Impacto tecnico por capa

- Presentacion: 13-14 controllers MVC, aproximadamente 26 vistas, formularios con validaciones, bandeja de novedades, upload de comprobantes y filtros historicos.
- Negocio: servicios para ventas, facturas, cuotas, stock, caja, dashboard, catalogos, usuarios, job diario e idempotencia de acreditaciones.
- Datos: 14 entidades nuevas, tabla tecnica para correlativo, 2 migraciones EF, query filters con lecturas historicas usando `IgnoreQueryFilters()` donde aplique.

## Riesgos y supuestos

- Se asume reutilizacion de componentes ya configurados en la solucion base: `SoftDestroyable`, `ServiceResult`, `IRepository<T>`, `INotificationService`, `AppDbContext`, roles Identity y convenciones MVC.
- No se contempla AFIP, migracion de datos, app mobile, hardware externo ni integraciones fuera de las ya definidas.
- Se asume despliegue single-node para el job diario en v1.
- El correlativo de facturas, la regeneracion de cuotas, el rechazo/regularizacion y las compensaciones de stock concentran el mayor riesgo funcional.
- Los ABM usan contingencia fija del 30% y dentro de esa contingencia quedan absorbidos pruebas, documentacion y riesgo ordinario; no se suman como adicionales.
- Los modulos no ABM usan contingencia variable segun riesgo del item, sin doble contingencia.

## WBS funcional vigente

| Modulo funcional | Tipo | Drivers principales | Requiere migracion EF |
|---|---|---|---|
| Catalogos base ganaderos | ABM intermedio | Grupo con stock minimo y baja logica, Rubro, Proveedor con ambito, Organismo intermediario | Si |
| Usuarios y permisos productor | ABM intermedio | alta/baja/modificacion, reset de password, limite de 5 productores, rol SuperUsuario | Si |
| Stock y movimientos | Workflow con estados | stock inicial unico, ingresos/egresos, compensaciones intra/inter categoria, matriz cerrada, alertas por stock minimo | Si |
| Ingresos: ventas, facturas y cuotas | Modulo financiero o logica sensible | venta multi-linea, factura correlativa, IVA snapshot, generacion y regeneracion de cuotas, bloqueo por estados | Si |
| Rechazos, regularizacion y acreditacion automatica | Workflow con estados | rechazo manual, opcion 3a/3b, job diario idempotente, notificacion in-app | Si |
| Egresos y comprobantes | ABM complejo | gasto, autocomplete de concepto, filtro de proveedor por ambito, comprobante adjunto, impacto en caja | Si |
| Caja y cuenta corriente | Modulo financiero o logica sensible | saldo por movimientos acreditados, filtros por estado/fecha, navegacion al origen | Si |
| Dashboard anual | Reporte o exportacion | mensualizacion por anio, comparativo, filtros por categoria y grupo, soporte historico de grupos inactivos | No adicional |

## Estimaciones PERT por item

Notas de lectura:
- `O`, `M` y `P` estan expresados en horas base por modulo completo.
- `Implementacion`, `Pruebas`, `Documentacion` y `Riesgo` son distribucion interna del esfuerzo final del modulo.
- En ABM con contingencia fija del 30%, pruebas, documentacion y riesgo ordinario ya estan absorbidos dentro de ese 30%.

| Modulo funcional | Tipo | Referencia historica usada | O | M | P | Horas PERT base | Implementacion | Pruebas | Documentacion | Riesgo | Contingencia | Horas finales | USD |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| Catalogos base ganaderos | ABM intermedio | Recotrack/Lumitrack/Piapartments ABM intermedio + Delicias ABM Categorias/Proveedores | 13.0 | 15.0 | 18.0 | 15.2 | 14.0 | 2.7 | 0.8 | 2.2 | Fija 30% | 19.7 | 236.4 |
| Usuarios y permisos productor | ABM intermedio | Recotrack ABM Usuarios + Lumitrack ABM Usuarios | 4.5 | 5.5 | 7.0 | 5.6 | 5.2 | 1.0 | 0.3 | 0.8 | Fija 30% | 7.3 | 87.6 |
| Stock y movimientos | Workflow con estados | Lumitrack ABM Relevamientos + ABM intermedio historico + Delicias ABM Pedidos | 12.0 | 14.0 | 17.0 | 14.2 | 13.2 | 2.3 | 0.7 | 1.5 | Variable 25% | 17.7 | 212.4 |
| Ingresos: ventas, facturas y cuotas | Modulo financiero o logica sensible | Delicias ABM Ventas + Gestion de pedidos + ABM Pagos | 15.0 | 18.0 | 22.0 | 18.2 | 16.9 | 3.0 | 0.8 | 2.0 | Variable 25% | 22.7 | 272.4 |
| Rechazos, regularizacion y acreditacion automatica | Workflow con estados | Delicias Notificaciones SignalR + workflow de pedidos como comparable de estados | 8.0 | 10.0 | 13.0 | 10.2 | 8.8 | 1.9 | 0.5 | 1.5 | Variable 25% | 12.7 | 152.4 |
| Egresos y comprobantes | ABM complejo | Delicias ABM Pagos + ABM Proveedores + ajuste por upload/autocomplete | 6.5 | 8.0 | 10.0 | 8.1 | 6.7 | 1.4 | 0.4 | 0.8 | Variable 15% | 9.3 | 111.6 |
| Caja y cuenta corriente | Modulo financiero o logica sensible | Delicias ABM Pagos + consulta operativa comparable | 4.0 | 5.0 | 6.5 | 5.1 | 4.2 | 0.9 | 0.2 | 0.5 | Variable 15% | 5.8 | 69.6 |
| Dashboard anual | Reporte o exportacion | mezcla de consulta historica comparable + filtro anual/mensual | 4.0 | 5.0 | 6.0 | 5.0 | 4.1 | 0.9 | 0.3 | 0.5 | Variable 15% | 5.8 | 69.6 |
| **Total** |  |  | **67.0** | **80.5** | **99.5** | **81.5** | **73.1** | **14.1** | **4.0** | **9.8** |  | **101.0** | **1,212.0** |

## Tasa vigente y contingencia aplicada

- Tasa aplicada: USD 12 / hora.
- Contingencia fija 30%: `Catalogos base ganaderos`, `Usuarios y permisos productor`.
- Contingencia variable 25%: `Stock y movimientos`, `Ingresos: ventas, facturas y cuotas`, `Rechazos, regularizacion y acreditacion automatica`.
- Contingencia variable 15%: `Egresos y comprobantes`, `Caja y cuenta corriente`, `Dashboard anual`.
- No se aplico doble contingencia sobre referencias historicas que ya venian con 30% incluido: primero se normalizaron a horas base.

## Calibraciones historicas usadas

- `/docs/recotrack/definiciones/4-presupuestador.md`: ABM simple e intermedio con 30% incluido.
- `/docs/lumitrack/definiciones/4-presupuestador.md`: ABM intermedio y ABM complejo con 30% incluido.
- `/docs/piapartments/definiciones/4-presupuestador.md`: ABM intermedio con 30% incluido.
- `/docs/delicias-naturales/definiciones/4-presupuestador.md`: workflows, ventas, pagos, compras, proveedores, notificaciones.
- `/docs/vinosefue/definiciones/4-presupuestador.md`: referencia global de proyecto con workflows y alta complejidad por modulo.
- `/docs/eleven-la-plata/definiciones/4-presupuestador.md`: referencia global de proyecto de complejidad media.

## Autocorreccion pre-cierre

| Modulo funcional | Mediana historica base comparable | Base preliminar | Ratio preliminar | Ajuste aplicado | Base final | Ratio final | Motivo del ajuste |
|---|---:|---:|---:|---|---:|---:|---|
| Catalogos base ganaderos | 16.9 | 16.0 | 0.95 | -0.8 h | 15.2 | 0.90 | se desconto sinergia por reutilizacion del mismo patron ABM y componentes compartidos |
| Usuarios y permisos productor | 5.0 | 5.5 | 1.10 | +0.1 h | 5.6 | 1.12 | se mantuvo cercano a la mediana por limite de 5 usuarios y reset de password |
| Stock y movimientos | 12.7 | 15.0 | 1.18 | -0.8 h | 14.2 | 1.12 | se bajo para no salir de banda, manteniendo sobrecosto solo por matriz y compensaciones |
| Ingresos: ventas, facturas y cuotas | 19.2 | 19.0 | 0.99 | -0.8 h | 18.2 | 0.95 | se reconoce reutilizacion de patrones MVC/EF pero se conserva complejidad financiera central |
| Rechazos, regularizacion y acreditacion automatica | 11.2 | 10.5 | 0.94 | -0.3 h | 10.2 | 0.91 | se corrigio a la baja por reaprovechar notificaciones y servicio existente de jobs |
| Egresos y comprobantes | 9.2 | 8.5 | 0.92 | -0.4 h | 8.1 | 0.88 | se mantuvo por debajo de la mediana al no incluir AFIP ni integraciones externas |
| Caja y cuenta corriente | 5.3 | 5.0 | 0.94 | +0.1 h | 5.1 | 0.96 | se ajusto por necesidad de navegacion al origen y saldo por estado acreditado |
| Dashboard anual | 5.0 | 4.8 | 0.96 | +0.2 h | 5.0 | 1.00 | se sumo esfuerzo por filtros historicos y grupos inactivos en periodos previos |

Resumen de autocorreccion:
- Total preliminar base: 84.3 h
- Total final base ajustado: 81.5 h
- Total final con contingencia: 101.0 h
- Total final USD: 1,212.0

## Pruebas funcionales minimas requeridas

- Alta/edicion/anulacion de ventas sin factura y bloqueo con factura emitida.
- Emision de factura con correlativo unico, IVA snapshot y cuotas 30/60/90 con redondeo correcto.
- Rechazo de cuota desde `Pendiente` y `Acreditada`, con mutacion correcta del movimiento de caja.
- Regularizacion opcion 3a y 3b sin duplicar saldo ni romper auditoria.
- Job diario idempotente: acredita una sola vez y genera novedades del dia.
- Alta de gasto con proveedor filtrado por ambito, autocomplete de concepto y comprobante valido/invalido.
- Carga de stock inicial unica por grupo, compensaciones intra/inter categoria y bloqueo fuera de matriz.
- Baja logica de grupo solo con stock cero y presencia historica de grupos inactivos en consultas previas.
- Caja con saldo calculado solo por movimientos acreditados.
- Dashboard anual con filtros por categoria y grupo, incluyendo historia de grupos inactivos.

## Checklist de salida para merge

- [ ] 2 migraciones EF creadas y validadas (`Ganaderia_Catalogos`, `Ganaderia_Operativa`).
- [ ] Roles `Productor` y `SuperUsuario` sembrados correctamente.
- [ ] Tabla contador para factura inicializada y protegida contra concurrencia.
- [ ] Controllers sin logica de negocio compleja.
- [ ] Services con `ServiceResult`/`ServiceResult<T>` y operaciones transaccionales en flujos criticos.
- [ ] Validaciones de stock, matriz de transiciones, cuotas y comprobantes cubiertas funcionalmente.
- [ ] `NotificationService` o equivalente reutilizado para novedades in-app.
- [ ] Query historicas con `IgnoreQueryFilters()` donde se necesite ver grupos inactivos.
- [ ] Endpoint autenticado para descarga de comprobantes fuera de `wwwroot`.
- [ ] Pruebas funcionales minimas ejecutadas sobre ventas, facturas, cuotas, stock, gastos, caja y dashboard.

## Cierre de calibracion estimado vs real esperado

- Items a medir luego de implementar: horas reales por `Stock y movimientos`, `Ingresos: ventas, facturas y cuotas` y `Rechazos, regularizacion y acreditacion automatica`, porque concentran la mayor incertidumbre funcional.
- Indicadores de calibracion a registrar: horas estimadas base por modulo, horas reales base, desvio porcentual, ratio de calibracion usado al presupuestar y si la reutilizacion de componentes efectivamente redujo esfuerzo.
- Umbral de reestimacion recomendado: si al cerrar los dos primeros modulos el desvio absoluto promedio supera 20%, recalibrar los modulos restantes antes de continuar.

## Historial de ajustes

- 2026-04-22: presupuesto inicial ejecutado sobre analisis funcional v10, diseno funcional v1 y arquitectura tecnica v1, con calibracion contra datasets Abril 2026 y estructura de trazabilidad creada para el proyecto.