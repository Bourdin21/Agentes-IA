# Memoria - Documentador

## Proyecto: La Platense
## Ultima actualizacion: 2026-09-03

## Definiciones vigentes

### Entregable vigente
`docs/la-platense/manual-usuario.md` — **Manual de uso para el personal de la ferreteria** (no un resumen de sprint). Pedido explicito de Joaquin el 2026-09-03: un documento para entregarle al usuario final con las funcionalidades completas de todo lo entregado hasta la fecha.

Se aparta del formato estandar de la etapa 7 (`07-documentacion.prompt.md` produce un resumen de sprint de media pagina). Se conservo el envoltorio de `31-formato-documento-cliente` (encabezado de marca, voseo, primera persona singular, pie de firma, cero tecnicismos) pero la estructura es de manual: una seccion por flujo, con pasos numerados y tablas de variantes.

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
