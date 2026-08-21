# Olvidata**Soft**
---

**marihogar — Nota de Crédito para anular facturas AFIP**
**OlvidataSoft · Agosto 2026**

## Sobre el pedido

Cuando se carga mal una factura ya emitida (CUIT equivocado, monto mal, cliente incorrecto), AFIP no permite borrarla ni corregirla — exige un documento fiscal separado, la Nota de Crédito, que la anule formalmente. Sin esto, una factura mal hecha quedaba sin forma de corregirse dentro del sistema.

## Cambio entregado

- Nuevo botón **"Generar Nota de Crédito"** en cualquier factura ya emitida (con CAE real). Pide un motivo y la emite contra AFIP de verdad, vinculada a la factura original.
- Si AFIP la aprueba, la factura original queda marcada **"Anulada"** y la venta vuelve a estar disponible para facturarse de nuevo — ya con los datos correctos.
- Si AFIP la rechaza, queda en estado reintentable (mismo comportamiento ya conocido de "Facturar"), sin tocar la factura original ni la venta.
- El PDF de la Nota de Crédito respeta el mismo formato oficial que ya usa la factura.

## Beneficio

Ya no hace falta contactar a un contador ni salir del sistema para corregir una factura mal cargada — todo el circuito (anular + volver a facturar bien) queda resuelto dentro de marihogar.

## Cómo se construyó (transparencia de proceso)

Este cambio pasó por el proceso completo: análisis, diseño, arquitectura, presupuesto (aprobado en USD 67), implementación y una revisión de calidad independiente antes de subirlo a producción — la revisión encontró un detalle real (un camino que, en teoría, permitía crear un comprobante mal formado si alguien manipulaba la carga) y se corrigió antes del deploy.

## Recomendación antes de usarlo con una corrección real

Probalo primero con una factura de monto bajo, para confirmar que AFIP la acepta de punta a punta antes de usarlo para corregir una factura real importante.

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
