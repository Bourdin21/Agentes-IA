# Memoria - Documentador

## Proyecto: La Platense
## Ultima actualizacion: 2026-10-07 (resumen de sprint de los 5 CR + Entrega 5, e instructivo del certificado AFIP)

## Definiciones vigentes

### Entregables vigentes
1. `docs/la-platense/manual-usuario.md` — manual completo del sistema (Entrega 1 + Etapa 3 + Entrega 2).
2. `docs/la-platense/manual-usuario-entrega-2.md` — **manual acotado a la Entrega 2**, para la aceptacion de esa entrega puntual. Cubre los 6 modulos del alcance real de Entrega 2 segun `5-implementador.md` (M5 Ventas+CC clientes, M6 AFIP, M8 Caja, M9 Gastos, M15 Entregas, M10 Dashboard corte 1) y deja explicitamente afuera Catalogo/Stock/Usuarios, que son Entrega 1.

Ojo con el naming: la **Etapa 2 del presupuesto** (CC del negocio, CC de empleados, presupuestos PDF, aumento masivo, devoluciones) NO es lo mismo que la **Entrega 2 de implementacion**. El manual sigue el alcance de implementacion, que es lo que el cliente esta usando.

Los dos son **manuales de uso para el personal de la ferreteria**, no resumenes de sprint. Se apartan del formato estandar de la etapa 7 (`07-documentacion.prompt.md` produce un resumen de media pagina): se conservo el envoltorio de `31-formato-documento-cliente` (encabezado de marca, voseo, primera persona singular, pie de firma, cero tecnicismos) pero la estructura es de manual — una seccion por flujo, con pasos numerados y tablas de variantes.

Cada uno tiene ademas una version navegable publicada como pagina para compartir con el personal (el `.md` es la fuente; la pagina es la copia de lectura).

### Instructivo del certificado AFIP (2026-10-07)

Entregables: **`docs/la-platense/manual-certificado-afip.md`** (fuente) + doc navegable para compartir con el cliente — `https://claude.ai/code/artifact/ac2481cc-a127-43dc-b4b0-d6924af4be99`. Mismo criterio que los dos manuales anteriores: el `.md` es la fuente, la pagina es la copia de lectura.

**Por que existe:** AFIP es el unico gate externo que queda en el proyecto, y el tramite **solo lo puede hacer el cliente** (requiere su Clave Fiscal). El instructivo convierte ese bloqueo en una lista de cinco pasos con tres cosas a devolver.

**Lo que lo hace util y no generico: sale de la instruccion 34, que tiene el circuito depurado contra AFIP produccion real.** Dos cosas concretas que un manual escrito de memoria no tendria:
1. **La trampa del paso 5, que es la que cuesta dias.** AFIP distingue el punto de venta del portal manual del habilitado para un sistema externo, **son objetos distintos aunque el numero se vea igual en la factura impresa**, y la opcion correcta es **"RECE para aplicativo y web services"** y no "Factura en Linea — Responsable Inscripto", que es la visualmente mas parecida. Es confusion documentada **ocurrida en vivo**, no hipotetica.
2. **El paso 4 (autorizar el certificado a usar el servicio) declarado como "el que mas se saltea"**, porque sin el el certificado existe y no sirve.

**Decision de redaccion:** se nombran **literalmente** las opciones del portal ("Administracion de Certificados Digitales", "Administrador de Relaciones de Clave Fiscal", "ABM de Puntos de Venta"), que es la unica excepcion a la regla de cero tecnicismos — el cliente tiene que **encontrarlas en pantalla**. Y donde no hay certeza del nombre exacto (ARCA renombro servicios), se le pide una captura en vez de afirmar: es mas honesto y mas rapido que mandarlo a adivinar.

**Lo que se le explica y normalmente no se le dice al cliente:** que **una factura con numero oficial no se puede borrar** — por eso la primera se emite juntos, sobre una venta real y chica. Y **por que** se le pide una factura real suya: los datos del emisor que van impresos se copian de un comprobante real en vez de adivinarlos, porque si alguno no coincide con lo que AFIP tiene registrado, la factura sale mal.

**Pedidos concretos de vuelta:** el `.crt`, el numero de punto de venta y el alias, y una factura real. Sin esas tres cosas el certificado no se puede cargar.

### Resumen de sprint 2026-10 — los 5 CR + devoluciones y notas de credito (2026-10-07)

Entregable: **`docs/la-platense/resumen-sprint-2026-10.md`**. Sigue el formato de resumen de sprint de la instruccion 31 (encabezado de marca, voseo, primera persona singular, cero tecnicismos, pie de firma) **con secciones "paso a paso"**, que el formato reserva para flujos no triviales: esta ronda introdujo **cuatro** que lo ameritan (vender con o sin factura, facturar una parte, el plan de echeqs, y la devolucion).

**Lo comunicado, en lenguaje de negocio:** vender con o sin factura con el precio ajustandose solo; facturar una parte de lo entregado; intereses de tarjeta configurables por tarjeta y por plan; pagar a un proveedor en varios echeqs a 0/30/60/90/120 con numero y banco; transferencia como medio propio separado del efectivo en el arqueo; devolucion de mercaderia con reingreso de stock y nota de credito cuando lo devuelto estaba facturado.

**Las tres decisiones que habia que explicar sin tecnicismos, y como se explicaron:**
1. **Que una venta quede cobrada por un monto y facturada por otro mayor** — se explico como lo que es desde el mostrador: si se cobro sin impuesto y despues se pide factura, **ese impuesto queda como deuda del cliente**, con el numero de factura que la genero, y la venta no se toca. Se dice que **los dos numeros estan bien**, porque es la pregunta que el cliente va a hacer.
2. **Que la devolucion de una venta con tarjeta no devuelve el recargo de cuotas** — con el motivo, que es comercial y no tecnico: ese recargo lo cobro la financiera y no vuelve.
3. **Que la fecha de debito de un cheque viene propuesta pero conviene corregirla** — sin explicar la medicion que lo respalda, pero diciendo para que sirve: que el arqueo coincida con el extracto.

**Los dos pendientes se comunicaron con su dependencia y con la consecuencia, no como "en proceso":** la facturacion electronica necesita **el certificado y el CUIT**, que el cliente tramita; y la actualizacion **todavia no esta subida**, con la frase explicita de que **nada de esto esta disponible en el sistema que usa hoy**. Decirlo asi evita el malentendido mas probable de esta entrega.

**Lo que NO se menciono, a proposito:** nombres de clases, servicios o tablas; los identificadores de defecto; que varias de las correcciones salieron de defectos propios encontrados en esta misma ronda. Las tres correcciones si se comunicaron **por su efecto en el negocio** (el arqueo que podia firmarse en cero, el precio editable por un vendedor, los catalogos dados de baja que seguian usandose), porque son cosas que el cliente puede haber visto o puede preguntar.

**Pedidos concretos al cliente:** el certificado de AFIP, un horario para subir la actualizacion, y **dos o tres listas de precios mas de proveedores distintos** — este ultimo es prerequisito para cotizar la importacion automatica, que sigue sin presupuestar.

### Alcance entregado al cliente (cubierto por el manual)
- **Ventas**: borrador editable, buscador de producto por nombre/codigo/codigo de barras + lector, descuento y recargo por linea (formula comercial), subtotal con IVA editable, pago mixto con auto-balanceo, nota por pago, cuotas con recargo configurable.
- **Cierre de venta en dos pasos**: Confirmar (descuenta stock, Caja y Cuenta Corriente) y Facturar (AFIP, opcional y posterior).
- **Clientes**: alta/edicion y consulta de cuenta corriente (saldo calculado en vivo).
- **Catalogo**: productos con esquema de precios completo, unidades de medida con conversion, codigos de barras alternos; marcas, modelos y categorias.
- **Stock**: alerta de minimos, ajuste manual auditado, historial, marca de verificado, clasificacion ABC.
- **Caja**: movimientos automaticos por venta y gasto, movimiento manual, cierre diario y mensual.
- **Gastos**: alta con categoria/forma de pago/impacto en caja, anulacion (sin edicion).
- **Entregas**: programacion desde la venta, propia o tercerizada, maquina de estados con reagendado.
- **Dashboard**: ventas del dia, caja del dia, entregas pendientes, stock critico, gastos del mes por categoria, top de productos.
- **Configuracion**: recargos por cuotas editables por el usuario (1/3/6/9/12/18/24).
- Transversal: filtros por columna persistidos en sesion, busqueda global que matchea importes y fechas, bajas logicas fuera de los listados, modo oscuro, gestion de la propia contraseña.

### Pendientes o fuera de alcance (declarados explicitamente en el manual)
1. **Cobro de cuenta corriente — gap funcional real, detectado al escribir el manual.** Se puede fiar y consultar el saldo, pero **no existe pantalla para registrar el pago del cliente ni un ajuste manual**. `ICuentaCorrienteClienteService.RegistrarMovimientoAsync` lo llama unicamente `VentaWorkflowService` al confirmar una venta fiada; los origenes `Pago` y `Ajuste` del enum no tienen ningun camino desde la UI. Es lo mas urgente de la lista para el dia a dia: hoy el cobro del fiado se lleva por fuera del sistema.
2. **Facturacion electronica AFIP**: circuito construido, falta certificado y CUIT del contribuyente.
3. **Anulacion de una venta ya confirmada**: un borrador se cancela, una venta confirmada todavia no se revierte.
4. **Compras a proveedores, cuenta corriente de proveedores y notas de credito**: fuera de lo entregado.

### Beneficios comunicados
- Poder cerrar una venta sin depender de AFIP (antes el modulo era inusable sin certificado).
- Un solo lugar para saber cuanto entro, cuanto salio y quien debe.
- Inventario que se puede ordenar de a poco (marca de verificado) sin frenar el mostrador.
- Parametros de negocio (recargos por cuotas) editables por el propio usuario, sin pedir un cambio de sistema.

### Proximo paso sugerido
Construir la pantalla de **cobro/ajuste de cuenta corriente de clientes** — cierra el unico circuito que hoy queda a medias dentro de lo ya entregado.

## Historial de ajustes
- 2026-10-07 (2): instructivo del certificado AFIP, pedido por Joaquin. Se escribio sobre la instruccion 34 (circuito depurado contra AFIP produccion real) y no de memoria: de ahi salen la trampa del punto de venta tipo "RECE para aplicativo y web services" — confusion ocurrida en vivo — y el paso de autorizar el certificado al servicio, que sin el deja el certificado inutil. Unica excepcion aceptada a la regla de cero tecnicismos: los nombres de las opciones del portal van literales, porque el cliente tiene que encontrarlas en pantalla.
- 2026-10-07: resumen de sprint de los 5 CR (venta sin factura, facturacion parcial, interes por tarjeta, plan de echeqs, transferencia) + la Entrega 5 (devoluciones y notas de credito). Se aparto del resumen de media pagina del formato estandar porque la ronda introdujo cuatro flujos nuevos no triviales, y la instruccion 31 habilita las secciones "paso a paso" justamente para eso. **Al redactarlo aparecio una verificacion que conviene dejar anotada:** el pendiente 1 del bloque anterior ("cobro de cuenta corriente, gap funcional real") **ya esta resuelto** desde el Sprint 0 del 2026-10-05, y el pendiente 3 ("anulacion de una venta ya confirmada") tambien — los dos seguian listados como pendientes en este archivo. Quedan vigentes solo AFIP (pendiente 2) y lo de compras/proveedores (pendiente 4), este ultimo ya construido pero sin deployar.
- 2026-09-03: primera version real del archivo (estaba en blanco desde el template). Se escribio `manual-usuario.md` completo a pedido de Joaquin, cubriendo Entrega 1 + Etapa 3 (migracion) + Entrega 2 + los cambios del 2026-09-03. Al verificar cada afirmacion contra el codigo aparecieron dos correcciones antes de entregar: la cuenta corriente es solo de consulta (no hay alta de pagos) y la marca de "verificado" del stock se pone sola al ajustar, no es un check manual. Ambas quedaron reflejadas en el manual.
- 2026-09-03 (2): se agrego `manual-usuario-entrega-2.md`, acotado a la Entrega 2. Al delimitar el alcance aparecio una ambiguedad de naming que conviene no volver a pisar: la **Etapa 2 del presupuesto** (CC del negocio, CC de empleados, presupuestos PDF, aumento masivo de precios, devoluciones/NC) es un conjunto DISTINTO de la **Entrega 2 de implementacion** (M5 Ventas+CC clientes, M6 AFIP, M8 Caja, M9 Gastos, M15 Entregas, M10 Dashboard corte 1, 61h). El manual sigue el alcance de implementacion — que es lo que el cliente tiene funcionando. Se verifico ademas contra la vista real que el nivel "Salud financiera" del dashboard es una tarjeta con candado que anuncia la proxima entrega, y quedo documentado como tal en vez de omitirlo.
