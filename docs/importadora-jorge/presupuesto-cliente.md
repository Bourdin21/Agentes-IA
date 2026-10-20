# Olvidata**Soft**

---

**Sistema de gestión mayorista — Importadora Jorge**

**OlvidataSoft · Octubre 2026**

## Sobre el sistema

Un sistema online que une lo que hoy está repartido entre el sistema de facturación y lo que se resuelve
a mano: la importación, el stock, la venta mayorista y la facturación. El objetivo es que el stock, el costo y la
deuda de cada cliente sean un dato confiable en un solo lugar, y no el resultado de juntar planillas.

- Cargás una **orden de compra al exterior** con su moneda y su cotización, y el sistema la congela: un
  embarque de hace seis meses sigue valiendo lo que valió, aunque el dólar se haya movido.
- Sumás los **costos de la importación** —flete, aduana, despachante, seguro— y el sistema los reparte sobre
  cada producto del embarque, así sabés el costo real puesto en depósito de cada artículo.
- El catálogo entiende que **comprás por bulto y vendés por bulto o por unidad**, sin que nadie tenga que
  hacer la cuenta a mano cada vez.
- Manejás **precio mayorista y precio minorista** sobre el mismo producto, y actualizás listas enteras de una
  pasada en vez de artículo por artículo.
- Cada **venta descuenta stock** y actualiza la cuenta corriente del comercio que te compra. Los mínimos de
  compra quedan controlados por el sistema, no por la memoria de quien atiende.
- Los **envíos al interior** quedan registrados: a qué transporte se despachó, qué pedido y en qué fecha.
- Un **tablero** muestra cómo viene el mes, qué rota y qué quedó inmovilizado.

## Cómo funciona una importación — paso a paso

**1. Cargás la orden de compra.** Elegís el proveedor del exterior, la moneda y la cotización de ese día. El
sistema la congela dentro del documento: no la toma de la ficha del proveedor, así un embarque de hace seis
meses sigue mostrando el número con el que realmente lo compraste.

**2. Sumás los costos de la importación.** A medida que aparecen —flete, derechos, despachante, seguro— los
cargás contra ese embarque.

**3. El sistema prorratea.** Reparte esos costos sobre los productos del embarque y te deja el **costo real
por artículo puesto en depósito**, que es el número con el que después definís el precio de venta.

*Esta es la parte que quiero relevar con vos antes de arrancar: cómo repartís hoy esos costos —por valor, por
peso o por unidad— porque de eso depende cómo lo configuro.*

**4. Recibís la mercadería.** Contra la orden, marcando qué llegó y qué quedó pendiente. Lo recibido entra al
stock automáticamente, con su costo ya calculado.

**5. Vendés.** El stock baja solo, la cuenta corriente del comercio que te compra se actualiza y el
comprobante sale del mismo lugar.

## Rol de usuario

| Rol | Accesos |
|---|---|
| Administrador | Todo el sistema: importaciones, costos, precios, ventas, stock, cuentas corrientes y tablero |
| Ventas | Clientes, pedidos, ventas, facturación, cuentas corrientes y consulta de stock |
| Depósito | Stock, recepción de mercadería, ajustes de existencias y expedición de envíos |
| Consulta | Solo lectura de tablero y reportes |

*Los roles se configuran de tu lado: vos decidís quién entra a qué. El alta inicial la dejo hecha en la
puesta en marcha.*

## Inversión

### Etapa 1 — El sistema operativo

| Área | USD |
|---|---:|
| Puesta en marcha, usuarios y publicación | 128 |
| Catálogo poli-rubro, con bulto y unidad | 117 |
| Listas de precio mayorista y minorista | 93 |
| Clientes y cuentas corrientes | 93 |
| Proveedores del exterior y cuentas en dólares | 82 |
| Importaciones: órdenes, costos y recepción | 303 |
| Stock y control de existencias | 105 |
| Ventas mayoristas y facturación | 210 |
| Expedición y envíos al interior | 82 |
| Tablero y reportes de gestión | 81 |
| Carga inicial de los 1.604 productos | 163 |
| **Subtotal Etapa 1** | **1.457** |

### Etapa 2 — Comprobantes fiscales

| Área | USD |
|---|---:|
| Facturación electrónica ARCA | 117 |
| Notas de crédito y débito | 70 |
| Búsqueda global y filtros guardados | 46 |
| **Subtotal Etapa 2** | **233** |

### Total del proyecto

| Concepto | USD |
|---|---:|
| Etapa 1 | 1.457 |
| Etapa 2 | 233 |
| **Total de desarrollo** | **1.690** |

### Mantenimiento anual

| Concepto | USD/año |
|---|---:|
| Plan Premium — servidor, seguridad, respaldos y soporte prioritario | 600 |

*Incluye hosting, actualizaciones de seguridad, respaldos y dos rondas de ajuste por año. No cubre
funcionalidades nuevas, que se cotizan aparte. Si en algún momento superan los diez usuarios, lo conversamos.
Los valores son sin IVA.*

## Qué incluye el proyecto

- Sistema web, accesible desde cualquier navegador, sin instalar nada.
- Las áreas funcionales detalladas en las tablas de Etapa 1 y Etapa 2.
- La carga inicial de los 1.604 productos del catálogo actual.
- Puesta en producción y configuración inicial.
- Capacitación del equipo para operarlo.
- Ajustes y correcciones durante el desarrollo, hasta la entrega de cada etapa.

## Qué no está incluido

- **Tienda online o catálogo público en internet.** Este sistema es de uso interno. Si más adelante quieren
  volver a vender online, se puede hacer y se cotiza aparte.
- Costo del servidor y del hosting durante el desarrollo.
- Aplicación móvil para iOS o Android.
- Conexión con lectoras de código de barras, balanzas o impresoras fiscales.
- Conexión directa con el despachante de aduana o con sistemas aduaneros.
- Seguimiento del envío dentro de la web del transporte.
- Cambios de alcance posteriores al inicio, que se presupuestan aparte.

## Lo que necesito de tu parte

- Una charla de una hora para cerrar detalles: cuántas personas van a usar el sistema, cómo reparten hoy los
  costos de importación y si el precio mayorista sale de una lista propia o de un descuento sobre el público.
- **Una exportación del catálogo actual** —del sistema de facturación o del sitio, antes de darlo de baja—
  para la carga inicial de los 1.604 productos. Conviene sacarla cuanto antes, mientras el sitio siga activo.
- Los datos fiscales de la empresa y, para la Etapa 2, el certificado de ARCA y el punto de venta habilitado
  *(ese trámite puede tardar unos días, conviene arrancarlo temprano)*.
- Alguien del equipo que conozca la operación diaria, para validar las pantallas antes de cerrarlas.

## Condiciones comerciales

- 50% al inicio de cada etapa y 50% contra la entrega de esa etapa.
- Valores en dólares, sin IVA.
- La Etapa 2 se puede arrancar junto con la Etapa 1 o dejarla para después: no cambia el precio.
- El mantenimiento anual se factura por adelantado, a partir de la puesta en producción.
- Si durante el desarrollo aparece algo que no está en este alcance, te paso el detalle y el valor antes de
  hacerlo — nunca aparece como sorpresa en la factura.

---

**Olvidata Soft — bourdinjoaquin@gmail.com — olvidatasoft.com**
