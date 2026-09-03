# Memoria - Documentador

## Proyecto: La Platense
## Ultima actualizacion: 2026-09-03

## Definiciones vigentes

### Entregables vigentes
1. `docs/la-platense/manual-usuario.md` — manual completo del sistema (Entrega 1 + Etapa 3 + Entrega 2).
2. `docs/la-platense/manual-usuario-entrega-2.md` — **manual acotado a la Entrega 2**, para la aceptacion de esa entrega puntual. Cubre los 6 modulos del alcance real de Entrega 2 segun `5-implementador.md` (M5 Ventas+CC clientes, M6 AFIP, M8 Caja, M9 Gastos, M15 Entregas, M10 Dashboard corte 1) y deja explicitamente afuera Catalogo/Stock/Usuarios, que son Entrega 1.

Ojo con el naming: la **Etapa 2 del presupuesto** (CC del negocio, CC de empleados, presupuestos PDF, aumento masivo, devoluciones) NO es lo mismo que la **Entrega 2 de implementacion**. El manual sigue el alcance de implementacion, que es lo que el cliente esta usando.

Los dos son **manuales de uso para el personal de la ferreteria**, no resumenes de sprint. Se apartan del formato estandar de la etapa 7 (`07-documentacion.prompt.md` produce un resumen de media pagina): se conservo el envoltorio de `31-formato-documento-cliente` (encabezado de marca, voseo, primera persona singular, pie de firma, cero tecnicismos) pero la estructura es de manual — una seccion por flujo, con pasos numerados y tablas de variantes.

Cada uno tiene ademas una version navegable publicada como pagina para compartir con el personal (el `.md` es la fuente; la pagina es la copia de lectura).

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
- 2026-09-03: primera version real del archivo (estaba en blanco desde el template). Se escribio `manual-usuario.md` completo a pedido de Joaquin, cubriendo Entrega 1 + Etapa 3 (migracion) + Entrega 2 + los cambios del 2026-09-03. Al verificar cada afirmacion contra el codigo aparecieron dos correcciones antes de entregar: la cuenta corriente es solo de consulta (no hay alta de pagos) y la marca de "verificado" del stock se pone sola al ajustar, no es un check manual. Ambas quedaron reflejadas en el manual.
- 2026-09-03 (2): se agrego `manual-usuario-entrega-2.md`, acotado a la Entrega 2. Al delimitar el alcance aparecio una ambiguedad de naming que conviene no volver a pisar: la **Etapa 2 del presupuesto** (CC del negocio, CC de empleados, presupuestos PDF, aumento masivo de precios, devoluciones/NC) es un conjunto DISTINTO de la **Entrega 2 de implementacion** (M5 Ventas+CC clientes, M6 AFIP, M8 Caja, M9 Gastos, M15 Entregas, M10 Dashboard corte 1, 61h). El manual sigue el alcance de implementacion — que es lo que el cliente tiene funcionando. Se verifico ademas contra la vista real que el nivel "Salud financiera" del dashboard es una tarjeta con candado que anuncia la proxima entrega, y quedo documentado como tal en vez de omitirlo.
