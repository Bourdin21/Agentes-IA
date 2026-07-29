# Olvidata**Soft**

---

**Propuesta de desarrollo — Sistema de gestión integral para La Platense**
**OlvidataSoft · Julio 2026**

---

## Sobre el sistema

Un sistema pensado para que dejes de manejar el día a día de la ferretería a mano — desde el mostrador hasta la caja de fin de mes.

- Cargás tu catálogo con precio de compra, precio de venta, IVA por producto y las unidades reales con las que trabajás (unidad, peso, metro o bulto) — el sistema controla el stock en la unidad correcta aunque compres por bulto y vendas por unidad.
- Vendés rápido, con cualquier medio de pago — efectivo, tarjeta en 3 o 6 cuotas con el recargo que vos definas, o fiado con seguimiento por cliente. Podés revisar y corregir una venta antes de facturarla, y si hace falta anular una venta ya facturada, el sistema emite la nota de crédito correspondiente y reingresa la mercadería devuelta al stock.
- Emitís el comprobante fiscal (AFIP) de cada venta, a un cliente cargado o a consumidor final.
- Tus compras a proveedores actualizan el stock solo, y cada proveedor tiene su propio dólar y su propio descuento configurado — podés importar su lista de precios en vez de cargarla a mano.
- Al cierre del día y del mes tenés la caja controlada, con una cuenta corriente única del negocio donde ves todo: ingresos, egresos y cierres.
- Tus empleados tienen su propio usuario y pueden ver su propia cuenta corriente (sueldo, retiros) sin acceso a la información de sus compañeros. Tu repartidor ve el listado completo de entregas.
- Armás presupuestos en PDF para tus clientes y hacés seguimiento de las entregas a domicilio, con el margen de envío que vos definas.
- Un panel te muestra la foto completa del negocio de un vistazo — es la pantalla en la que más vamos a invertir en diseño, porque es la que vas a mirar todos los días.
- Migramos tu catálogo actual (~17.000 productos) al sistema nuevo, y te ayudamos a poner en orden el stock inicial sin frenar la operación (ver más abajo).

---

## Cómo funciona la venta — paso a paso

**1. Cargás la venta.** Elegís los productos, cantidades, precio y % de IVA — todo editable antes de cerrar.
**2. Cobrás.** Un pago o varios: efectivo, tarjeta (3 o 6 cuotas, con recargo visible antes de confirmar) o cuenta corriente (fiado).
**3. Revisás.** Mientras no facturaste, podés corregir cualquier producto, precio o cantidad — sin tener que anular nada.
**4. Facturás.** Elegís el cliente (o "Consumidor final") y emitís el comprobante AFIP.
**5. Si hace falta anular.** Aunque la venta ya esté facturada, se puede anular: el sistema emite la nota de crédito y, si hay mercadería que vuelve, la reingresa al stock automáticamente.

**Casos especiales contemplados:**
- Pago combinado (parte efectivo, parte tarjeta, parte cuenta corriente).
- Devolución parcial (algunos productos de la venta, no todos).
- Devoluciones sí — cambios por otro producto, no (se resuelve como una devolución más una venta nueva).

---

## Cómo funciona la compra por bulto y venta por unidad

**1. Configurás el producto una vez.** Definís que se compra por bulto (ej. una caja de 100 tornillos) y se vende por unidad.
**2. Comprás en la unidad del proveedor.** Cargás la compra en bultos; el sistema calcula automáticamente cuántas unidades de venta entran al stock.
**3. Vendés en la unidad real.** El mostrador vende por unidad, sin que el vendedor tenga que hacer la cuenta a mano.

*Este es el desarrollo más a medida de todo el proyecto — no es una funcionalidad de catálogo estándar, es lógica pensada específicamente para cómo trabaja tu ferretería.*

---

## Cómo ponemos en orden el stock inicial, sin frenar el mostrador

Hoy el stock se maneja de memoria, y son ~17.000 productos — ni arrancar de cero ni contar todo antes de empezar son opciones realistas. Por eso proponemos un camino intermedio:

**1. Vos clasificás qué productos son los que más rotan o más valen.** El sistema te da la posibilidad de marcar esa clasificación en el catálogo (producto por producto o por categoría) — sos vos quien mejor conoce tu negocio, así que esta decisión la tomás vos, no nosotros. No hace falta revisar los 17.000 productos uno por uno: alcanza con identificar el 15-20% que concentra la mayor parte de tus ventas.
**2. Contás físicamente solo esos productos.** Es un trabajo acotado, factible en pocos días con tu equipo actual.
**3. El resto arranca sin stock verificado, pero se puede vender igual.** El sistema no bloquea una venta por esto — solo te avisa que ese producto todavía no tiene un conteo confirmado.
**4. Vas corrigiendo sobre la marcha.** Cualquier empleado autorizado puede ajustar el stock de un producto en el momento, con el motivo, y queda todo registrado.

*Recomendamos además revisar una categoría de productos por semana durante los primeros 2-3 meses, hasta que todo el catálogo quede con stock confiable — es un hábito operativo simple, no algo que tengas que construir aparte.*

---

## Rol de usuario

| Rol | Accesos |
|---|---|
| Dueño / Administrador | Acceso completo: ventas, catálogo, stock, compras, caja, cuentas corrientes, empleados, reportes |
| Vendedor | Ventas, catálogo (consulta), stock (consulta), su propia cuenta corriente como empleado |
| Repartidor | Listado completo de entregas, su propia cuenta corriente como empleado |

*El alta de usuarios y la configuración inicial las gestionamos nosotros como parte del servicio — no necesitás administrar nada técnico.*

---

## Etapa 1 (MVP — lo mínimo para operar el día a día)

| Área funcional | Incluye |
|---|---|
| Usuarios y roles | Alta de administrador, vendedores y repartidor con permisos propios |
| Catálogo de productos | Precio de compra/venta, IVA por producto, marca, modelo, categorías |
| Unidades de medida | Venta por unidad, peso, metro o bulto, con conversión automática compra↔venta |
| Stock | Control de inventario + alertas de stock mínimo + ajuste manual y puesta a punto del stock inicial (ver sección dedicada más arriba) |
| Ventas + cuenta corriente de clientes | Venta editable antes de facturar, pagos combinados, tarjeta en cuotas con recargo configurable, fiado con seguimiento |
| Facturación electrónica (AFIP) | Comprobante a cliente cargado o consumidor final |
| Proveedores + compras | Lista de precios propia por proveedor (dólar + descuento configurables), importación de listas, pago con echeck/transferencia |
| Caja | Ingresos, egresos, cierre diario y cierre mensual (punto de venta único) |
| Gastos varios | Gastos operativos, diferenciados entre caja chica y caja mensual |
| Dashboard | Panel con la foto completa del negocio — pantalla de mayor inversión de diseño del proyecto |

**Etapa 1: USD 1.329**

## Etapa 2 (funcionalidades adicionales)

| Área funcional | Incluye |
|---|---|
| Cuenta corriente propia del negocio | Vista consolidada de cierres de caja, ingresos y egresos |
| Cuenta corriente de empleados | Cada empleado ve su propio sueldo y retiros, sin acceso a los de sus compañeros |
| Presupuestos y cotizaciones en PDF | Cotizar y enviar presupuestos a clientes |
| Entregas a domicilio | Seguimiento de entregas, con margen de envío configurable y distinción entre reparto propio y tercerizado |
| Aumento masivo de precios | Actualizar precios por categoría, proveedor o marca en un paso |
| Devoluciones de mercadería + notas de crédito | Anulación de ventas facturadas con nota de crédito y reingreso automático de stock |

**Etapa 2: USD 516**

## Etapa 3 (migración del catálogo actual + puesta a punto de stock inicial)

| Área funcional | Incluye |
|---|---|
| Migración de catálogo | Carga de tu catálogo actual (~17.000 productos) al sistema nuevo, con validación de datos y reporte de lo que se migró sin inconvenientes |
| Puesta a punto de stock inicial | Incorporación del conteo real de los productos de mayor rotación/valor al importador de catálogo |

**Etapa 3: USD 394** *(estimación provisional — el valor final se confirma cuando nos compartas el archivo real de tu catálogo, ya que todavía no conocemos el formato exacto)*

## Total del proyecto

| Concepto | USD |
|---|---:|
| Etapa 1 | 1.329 |
| Etapa 2 | 516 |
| Etapa 3 (migración + stock inicial, provisional) | 394 |
| **Total proyecto** | **2.239** |

*Tokens IA, eficiencia de desarrollo y el descuento por referido ya están contemplados dentro de los valores de Etapa 1 y Etapa 2 — no hay costos ocultos ni adicionales por fuera de esta tabla. La Etapa 3 se confirma en un valor final una vez recibido el archivo de catálogo.*

---

## Mantenimiento anual

| Momento | Plan | USD/año |
|---|---|---:|
| Con Etapa 1 (año 1) | PRO | **Sin costo** |
| Desde Etapa 2 en adelante | PREMIUM | 500 |

*Tu primer año de mantenimiento (Plan PRO) no tiene costo — arrancás a operar el sistema sin ese gasto adicional. Al sumar la Etapa 2, el plan pasa a PREMIUM (más capacidad, más rondas de ajuste incluidas) a USD 500/año, sin permanencia. Incluye hosting, SSL, dominio, actualizaciones de seguridad y soporte.*

---

## Qué incluye el proyecto

- Desarrollo funcional completo del alcance de Etapa 1, Etapa 2 y Etapa 3.
- Migración del catálogo de productos actual (~17.000 productos) al sistema nuevo.
- Aplicación web accesible desde cualquier navegador, instalable como app en el celular (sin tienda de aplicaciones).
- Hosting, certificado de seguridad (SSL) y dominio incluidos en el mantenimiento anual.
- Pruebas funcionales internas y entrega operativa.
- Ajustes menores de puesta en marcha dentro del alcance acordado.
- Soporte directo con quien desarrolla el sistema — sin intermediarios.

## Qué no está incluido

- Cambios/canjes de mercadería por otro producto — el sistema contempla devoluciones, no canjes.
- Reservas de stock/apartados de mercadería.
- Múltiples puntos de venta/cajas físicas (el proyecto contempla un único punto de venta).
- Integración con hardware externo (lectoras de código de barras, balanzas, etc.).
- Aplicación móvil nativa (Android/iOS con tienda de aplicaciones).
- Cambios de alcance posteriores al inicio — se presupuestan por separado.

---

## Lo que necesitamos de tu parte

- El archivo real del catálogo de productos (~17.000 productos) apenas lo tengas disponible, para confirmar el valor final de la Etapa 3.
- Confirmar si la anulación de una venta facturada la puede iniciar cualquier vendedor o solo vos como administrador, y si querés poner un límite de tiempo para hacerlo.
- Clasificar por tu cuenta los productos de mayor rotación/valor de tu catálogo (el sistema te da la herramienta para marcarlo), antes de arrancar la Etapa 3 (ver "Cómo ponemos en orden el stock inicial").
- Una sesión corta para definir juntos qué información va primero en el panel principal (dashboard) — dado que es la pantalla más importante, preferimos priorizarla con vos antes de construirla.
- CUIT y certificado digital ARCA para la facturación electrónica (el trámite se puede iniciar en paralelo mientras armamos el sistema).

---

## Condiciones comerciales

- Forma de pago: 50% al inicio y 50% a la entrega de cada etapa.
- Moneda: USD, pagadero en pesos al tipo de cambio del día.
- Incluye descuento por referido aplicado sobre el valor de desarrollo de Etapa 1 y Etapa 2.
- El valor de Etapa 3 es provisional y se confirma al recibir el archivo real del catálogo.
- Sin contrato de permanencia en el mantenimiento anual.
- Cambio de alcance disponible en cualquier momento si el negocio crece — se cotiza aparte.

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
