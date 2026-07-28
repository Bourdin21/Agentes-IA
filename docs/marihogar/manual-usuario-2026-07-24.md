# Olvidata**Soft**
---

**marihogar — Manual de uso del sistema**
**OlvidataSoft · Julio 2026**

## Sobre este manual

Esta guía te muestra cómo usar cada pantalla del sistema, paso a paso, en el orden en que normalmente las vas a usar en el día a día del local. No hace falta leerla de punta a punta: podés ir directo a la sección del módulo que necesitás. El sistema ya está funcionando en `http://olvidatasoft-002-site16.jtempurl.com/` — entrás con el usuario y contraseña que te dimos.

## Índice

1. [Antes de empezar: roles y acceso](#1-antes-de-empezar-roles-y-acceso)
2. [Dashboard (pantalla de inicio)](#2-dashboard-pantalla-de-inicio)
3. [Catálogo de productos y stock](#3-catálogo-de-productos-y-stock)
4. [Presupuestos](#4-presupuestos)
5. [Ventas](#5-ventas)
6. [Entregas a domicilio](#6-entregas-a-domicilio)
7. [Facturación electrónica (AFIP/ARCA)](#7-facturación-electrónica-afipARCA)
8. [Compras a proveedores](#8-compras-a-proveedores)
9. [Cheques](#9-cheques)
10. [Cuenta corriente del local](#10-cuenta-corriente-del-local)
11. [Caja mensual](#11-caja-mensual)
12. [Gastos del negocio](#12-gastos-del-negocio)
13. [Proyección financiera](#13-proyección-financiera)
14. [Aumento masivo de precios](#14-aumento-masivo-de-precios)
15. [Qué falta para estar 100% operativo](#15-qué-falta-para-estar-100-operativo)

---

## 1. Antes de empezar: roles y acceso

El sistema tiene dos tipos de usuario:

| Accede a | Administrador | Vendedor |
|---|---|---|
| Dashboard, notificaciones | Ver todo | Ver versión simplificada (sin datos financieros) |
| Presupuestos, Ventas, Entregas, Facturación | ✓ | ✓ |
| Catálogo, stock, precios de costo | ✓ | ✗ (no ve precio de compra en ningún lado) |
| Compras a proveedores, cheques | ✓ | ✗ |
| Cuenta corriente, caja, gastos, proyección | ✓ | ✗ |
| Aumento masivo de precios | ✓ | ✗ |

*El vendedor puede vender, presupuestar, entregar y facturar sin ver información financiera del negocio ni el costo de los productos. Vos, como Administrador, ves y gestionás todo.*

Cada pantalla del sistema tiene el mismo formato: un botón para crear algo nuevo arriba a la derecha, filtros para buscar en el listado, y una tabla con lo ya cargado. **Los filtros que usás en un listado se guardan solos**: si salís de la pantalla y volvés, los seguís viendo aplicados (hay un botón "Limpiar filtros" si querés sacarlos).

---

## 2. Dashboard (pantalla de inicio)

Es lo primero que ves al entrar al sistema.

- **Si sos Administrador**, ves: ventas del período (con selector de fechas), stock por debajo del mínimo, cheques por vencer, balance de caja actual y los productos más vendidos. Cada dato se carga por separado, así que si uno tarda un poco no te frena el resto de la pantalla.
- **Si sos Vendedor**, ves una versión simple: tus ventas del día y accesos directos para "Nueva venta" y "Nuevo presupuesto".

---

## 3. Catálogo de productos y stock

**Menú: Catálogo → Productos / Categorías / Marcas / Stock**

### Cargar un producto nuevo
1. `Catálogo → Productos → Nuevo`.
2. Completá nombre, descripción, precio de compra, precio de venta, marca, modelo, categoría y stock mínimo.
3. Subí hasta 5 fotos — la primera que subís queda como portada, pero podés cambiarla después con el botón "Hacer portada".
4. Guardar.

*Si el precio de venta queda por debajo del precio de compra, el sistema te avisa (no te lo bloquea, por si es una promoción a propósito).*

### Buscar y filtrar productos
El listado de Productos tiene un filtro por cada columna que ves (nombre, marca, modelo, categoría, stock, precio de venta). Como Vendedor, no vas a ver la columna de precio de compra en ningún lado de esta pantalla.

### Stock
- El stock se descuenta y se incrementa **solo**, con cada venta y cada compra recibida — no tenés que tocar nada manualmente en el uso normal.
- Si necesitás corregir el stock a mano (por un conteo físico, una rotura, etc.), andá a `Catálogo → Stock → Ajustar` (solo Administrador), elegí el producto, indicá la cantidad y el motivo. El sistema no te deja dejar el stock en negativo sin que lo confirmes explícitamente.
- Cuando un producto está por debajo del stock mínimo que configuraste, aparece marcado en rojo en el listado y se cuenta en el Dashboard.

---

## 4. Presupuestos

**Menú: Ventas → Presupuestos**

1. `Presupuestos → Nuevo`.
2. Buscá los productos (con foto, precio y stock disponible a la vista) y armá la lista de ítems — el total se calcula solo a medida que agregás.
3. Guardá como Borrador o mandalo directo a Enviado.
4. Descargá el PDF para mandárselo al cliente por WhatsApp o email.
5. Cuando el cliente lo aprueba, marcá el presupuesto como **Aprobado**.
6. Con un clic en **"Convertir a venta"**, se abre la pantalla de Ventas con todos los productos y cantidades ya cargados — no tenés que volver a tipear nada.

Si pasa mucho tiempo sin que el cliente responda, el presupuesto pasa solo a **Expirado**. También podés marcarlo como **Rechazado** si el cliente dice que no.

---

## 5. Ventas

**Menú: Ventas → Ventas** — la pantalla de mayor uso diario del sistema, pensada para ser rápida en el mostrador.

### Cargar una venta
1. `Ventas → Nueva venta`.
2. **Buscador de productos** arriba: escribís el nombre y aparecen resultados con foto, precio y stock disponible. Apretás Enter (o hacés clic) y el producto se agrega a la lista — el cursor vuelve solo al buscador para que sigas cargando sin usar el mouse.
3. A la derecha tenés siempre visible el **resumen de la venta**: cantidad de productos, el total en letra grande, y la sección de pago.
4. **Formas de pago**: hay botones rápidos como "Todo efectivo" o "Todo transferencia" que completan el monto solos, o podés combinar varios medios de pago (por ejemplo, una parte en efectivo y otra en transferencia). El sistema te muestra en vivo cuánto falta cobrar o cuánto hay que dar de vuelto.
5. El botón **"Confirmar venta"** se habilita recién cuando el pago cierra con el total.
6. Al confirmar, en un solo paso: se descuenta el stock, se registra el pago y se genera el movimiento en la cuenta corriente del local. Después te aparece una pantalla de éxito con accesos directos para "Nueva venta", "Ver venta", "Programar entrega" o "Facturar".

*Si intentás vender más cantidad de la que hay en stock, el sistema te avisa con una marca amarilla en esa línea, pero **no te bloquea** la venta (por si es una venta que se cubre con una compra próxima).*

### Cancelar una venta
Solo se puede cancelar si todavía no tiene una entrega programada ni un comprobante de AFIP emitido. Al cancelar, se revierte automáticamente el stock y el movimiento de caja — nunca se borra el historial, queda registrado que se anuló.

---

## 6. Entregas a domicilio

**Menú: Ventas → Entregas**

1. Desde una venta ya confirmada, apretás **"Programar entrega"** (aparece en la pantalla de éxito de la venta o en su detalle).
2. Completás dirección, fecha y qué vendedor la reparte.
3. El día de la entrega, abrís la pantalla desde el **celular** — está pensada para usarse en la casa del cliente, con botones grandes y poco scroll: registrás el cobro si quedaba pendiente, y marcás **"Entregada"**.
4. Si el cliente no estaba, marcás **"No entregada"** (con motivo) y podés reagendar para otra fecha — el sistema guarda el historial de todos los intentos, no lo pisa.

*Una venta con entrega ya programada no se puede cancelar.*

---

## 7. Facturación electrónica (AFIP/ARCA)

**Menú: Ventas → Comprobantes AFIP**

1. Desde el detalle de una venta, apretás **"Facturar"**.
2. Elegís qué productos y qué cantidades facturar — podés facturar **todo, una parte, o un solo producto** de la venta (y facturar el resto después, en otro comprobante).
3. Elegís tipo de comprobante (Factura A o B) y completás los datos fiscales del cliente (CUIT o DNI según corresponda).
4. Al emitir, el sistema pide el CAE a AFIP y te genera el PDF del comprobante.
5. Si AFIP rechaza o no responde, el comprobante queda marcado en **Error** con el motivo a la vista, y podés reintentarlo desde la misma pantalla sin tener que volver a elegir los productos.

*⚠️ Importante: mientras no tengamos tu certificado digital de AFIP, el sistema está en modo de pruebas (homologación) y no emite facturas reales. Ver sección 15.*

---

## 8. Compras a proveedores

**Menú: Compras → Proveedores / Órdenes de compra**

### Proveedores
`Compras → Proveedores → Nuevo`: cargás razón social, CUIT, teléfono, email y dirección.

### Órdenes de compra
1. `Compras → Órdenes de compra → Nueva`, elegís el proveedor y armás la lista de productos con cantidad y precio de compra (mismo buscador que en Ventas/Presupuestos).
2. La confirmás — a partir de ahí ya no se pueden editar los ítems, solo cancelarla.
3. Cuando llega la mercadería, la marcás como **"Recibida"** — el stock de cada producto sube solo.
4. Registrás el pago: efectivo, transferencia, cheque o depósito. Si es cheque, completás número, banco, fecha de vencimiento y la cuota (30/60/90 días) en el mismo formulario, sin salir de la pantalla.

*Una orden de compra ya Recibida no se puede cancelar (ya impactó el stock) — solo se puede cancelar mientras está en Borrador o Confirmada.*

---

## 9. Cheques

**Menú: Financiero → Cheques**

- Cada cheque que entregás como pago a un proveedor queda visible acá con su fecha de vencimiento, color según estado (amarillo = pendiente, verde = acreditado, rojo = rechazado) y resaltado si vence en los próximos 7 días.
- **No tenés que hacer nada para acreditarlos**: el sistema los pasa solo a "Acreditado" el día que vencen, y te llega una notificación in-app avisándote.
- Si el banco te rechaza un cheque, entrás y lo marcás manualmente como **"Rechazado"** — el sistema reabre automáticamente la deuda con ese proveedor.

---

## 10. Cuenta corriente del local

**Menú: Financiero → Cuenta corriente**

Acá ves el saldo actual del local (lo que entró por ventas menos lo que salió por pagos a proveedores y gastos) con el detalle completo de cada movimiento, filtrable por fecha. Es de solo lectura: los movimientos se generan solos desde Ventas, Compras y Gastos.

---

## 11. Caja mensual

**Menú: Financiero → Caja mensual**

Resumen de ingresos y egresos del mes (o del rango de fechas que elijas), con un comparativo automático contra el período anterior para que veas si mejoraste o empeoraste respecto al mes pasado.

---

## 12. Gastos del negocio

**Menú: Financiero → Gastos**

1. `Gastos → Nuevo gasto`, elegís categoría (Alquiler, Servicios, Sueldos, Flete u Otro), monto, forma de pago, fecha y una descripción.
2. Al guardarlo, se genera automáticamente el movimiento correspondiente en la cuenta corriente del local y en la caja del período — no hay que cargarlo dos veces.
3. Un gasto no se edita: si te equivocaste, lo **anulás** (queda visible en el listado con la marca "Anulado", no desaparece) y cargás uno nuevo correcto.

---

## 13. Proyección financiera

**Menú: Financiero → Proyección financiera**

Te muestra una estimación de cómo viene tu caja para el próximo período, combinando:
- El promedio de tus ingresos y gastos de los últimos meses (elegís ver 1, 3 o 6 meses de historial).
- Los compromisos que ya sabés que vienen: cheques por vencer y pagos pendientes a proveedores.

Si los compromisos que ya tenés superan lo que proyectás que vas a ingresar, aparece una alerta en rojo. *Es una estimación para ayudarte a anticipar, no un número exacto garantizado — siempre lo vas a ver aclarado en la misma pantalla.*

---

## 14. Aumento masivo de precios

**Menú: Catálogo → Aumento masivo**

1. Elegís el criterio: por marca, por categoría o por modelo.
2. Elegís si el aumento va sobre el precio de compra, el de venta, o ambos, y el porcentaje.
3. Apretás **"Previsualizar"**: te muestra una tabla con el precio actual y el precio nuevo de cada producto afectado — **todavía no se aplicó nada**.
4. Recién cuando apretás **"Confirmar aumento"** se actualizan los precios de verdad.

Esto queda registrado en la auditoría del sistema (quién lo hizo, cuándo, a cuántos productos y con qué porcentaje).

---

## 15. Qué falta para estar 100% operativo

El sistema ya está desplegado y funcionando en producción con la Etapa 1 completa. Quedan dos cosas pendientes, ambas de tu lado:

1. **Certificado digital de AFIP/ARCA (.p12) de tu CUIT**: sin él, el módulo de Facturación queda en modo de pruebas (homologación) — no emite comprobantes fiscales reales todavía. En cuanto nos lo acerques, lo activamos en modo producción (es solo un cambio de configuración, no hay que tocar nada más).
2. **Recorrer el sistema vos mismo**: te dejamos guías de verificación paso a paso para cada módulo — te pedimos que las recorras (podemos hacerlo juntos en una videollamada si preferís) antes de dar todo por definitivamente probado en el uso real del día a día.

Ante cualquier duda usando el sistema, escribinos.

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
