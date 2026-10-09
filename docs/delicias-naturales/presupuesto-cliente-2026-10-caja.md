# Olvidata**Soft**

---

**Diferencia de caja mensual — relevamiento y plan de trabajo — Delicias Naturales**

**OlvidataSoft · Octubre 2026**

---

## Sobre el sistema

Magali viene arrastrando desde hace meses una diferencia entre lo que informa el sistema y lo que muestra el extracto del banco. Tomé el extracto de septiembre y lo crucé contra los pagos del sistema, uno por uno, hasta que los números cerraron al centavo. Esto es lo que encontré y lo que propongo hacer.

- La diferencia que venías arrastrando **es mucho más chica de lo que parecía**, y la mayor parte no era un error del sistema.
- De los 242 movimientos del banco, **221 cruzan bien** contra los pagos cargados: el sistema está registrando bien.
- Los 21 que no cruzan tienen **siete causas concretas**, todas identificadas y con nombre y apellido de venta.
- Y lo más importante: encontré **por qué se repite todos los meses**. No es un error de cálculo, son validaciones que le faltan a la pantalla de cargar pagos.

## Lo primero: la diferencia real no era de 7 millones

El número que estabas comparando contra el sistema **no es la suma de lo que te pagaron los clientes**. El archivo del banco incluye cosas que no son cobranzas:

| Concepto | Importe |
|---|---:|
| Total del archivo del banco | 40.346.813,07 |
| Menos: tus propios depósitos de efectivo al banco (3 el 29/09) | −5.000.000,00 |
| Menos: intereses ganados | −301,83 |
| **Lo que realmente te transfirieron los clientes** | **35.346.511,24** |
| Lo que dice el sistema (pagos por transferencia de septiembre) | 36.019.758,88 |
| **Diferencia real** | **673.247,64** |

Los 5 millones que faltaban eran **tu propia plata**: efectivo que cobraste en el local, que el sistema ya había contado como efectivo, y que el banco vuelve a mostrar como un ingreso cuando lo depositás. Mientras el control sea "total del extracto contra total de transferencias", la caja no puede dar nunca — ni con el sistema perfecto.

*Aparte: el archivo que estás usando lista solamente los ingresos, no los egresos, así que tampoco sirve para controlar el saldo de la cuenta.*

## Las siete causas de los 673.247,64

| Qué pasó | Ejemplo concreto |
|---|---|
| Un cobro por transferencia se cargó como efectivo | $223.669,16 de la venta 9598 |
| Un pago se borró y se volvió a cargar por otro importe | La venta 9324 quedó $28.000 por debajo de lo que entró al banco |
| Se cargó el total de la factura, no lo que el cliente realmente transfirió | 6 ventas, $14.111,93 en total (una con $10.000 de más por un error de tipeo) |
| Cobros del 31/08 que el banco acreditó el 01/09 | $183.149,97 — se compensa contra agosto |
| Movimientos repetidos en el extracto del banco | Dos de $107.350 y dos de $58.222 con un solo pago cada par |
| Pagos marcados como transferencia sin acreditación en el mes | 11 pagos, el mayor de $434.000 (venta 9581) |
| Ingresos del banco sin ningún pago cargado | 15 movimientos, y **7 de ellos son todos del 18/09** |

Te dejo el detalle completo de las 253 líneas en una planilla aparte, para que la recorras con Magali.

## Por qué se repite todos los meses

Miré los 14.131 pagos cargados desde que el sistema está en producción. No hay un error de cálculo: hay validaciones que faltan, y producen el mismo ruido todos los meses.

- **Entre el 9 % y el 20 % de los pagos de cada mes** tienen una fecha distinta al día en que se cargaron. Eso corre cobros de un mes al otro.
- **Entre 82 y 116 pagos por mes se borran**, y entre 37 y 61 de esos se vuelven a cargar con el mismo importe. Cada una de esas correcciones a mano es una oportunidad de dejar el número mal.
- El botón **"Editar pago"** que te entregué en septiembre, hecho justamente para corregir sin borrar, **no se usó ni una vez** en los 840 pagos cargados desde entonces.
- **La fecha del pago no tiene ningún control:** hay 3 pagos cargados con fecha futura, uno de $688.425,33 fechado el 16/10, y dos fechados en diciembre de 2026 que no van a entrar en ningún cierre.
- **El campo del importe viene precargado** con el total que falta de la venta. Para el efectivo está bien. Para una transferencia es justo lo que hace que se cargue el importe de la factura en lugar del que entró al banco.

## Qué propongo hacer — Etapa 1

Esta etapa **no resuelve la diferencia por sí sola**: evita que el dato se siga ensuciando mes a mes. Es la base para que el control después tenga sentido. Prefiero decírtelo así antes de que lo pagues.

**1. Control de la fecha del pago.** El sistema deja de aceptar fechas imposibles: nada más allá de 90 días en el futuro (eso atrapa los errores de año) y nada anterior a la fecha de la venta. Y cuando la fecha se aparta de lo normal —hacia adelante porque es un cheque a depositar, o más de 30 días hacia atrás porque es un cobro atrasado— te pide confirmar antes de guardar, en lugar de aceptarla en silencio.

*Un detalle que salió del relevamiento: los pagos con fecha futura **no son errores**, son los cheques. Hay 242 cargados así, y es como el papá de Magali los viene anotando. Por eso el sistema no los va a rechazar: te va a pedir que confirmes. El día que agreguemos el cheque como medio de pago propio (Etapa 2), ahí sí se puede cerrar del todo.*

**2. El importe que se carga es el que entró.** Cuando elegís efectivo, el importe sigue viniendo precargado como hasta ahora. Cuando elegís transferencia, débito, crédito o Mercado Pago, el campo arranca **vacío**, con la leyenda "importe acreditado" — porque ese número lo decide el cliente que transfirió, no la factura. Si coinciden, un botón te copia el saldo de la venta en un click. Y mientras tipeás, el sistema te dice en el momento qué consecuencia tiene: cuánto queda por cobrar, o cuánto se cobra de más y dónde queda ese crédito.

**3. Los totales de la pantalla de Pagos dicen contra qué se comparan.** Hoy ves un total por cada medio de pago. Pasás a ver tres números agrupados, cada uno con su aclaración: lo cobrado en efectivo (*no se compara contra el banco*), lo cobrado por transferencia (*comparable con el extracto, descontando tus propios depósitos*), y tarjetas y Mercado Pago (*se liquidan con plazo y retención, no coinciden línea a línea*). Y desaparecen las tarjetas de los medios que no usás, que hoy ocupan lugar en cero.

| Área | USD |
|---|---:|
| Control de la fecha del pago | 42 |
| Registro del importe cobrado | 37 |
| Totales de la pantalla de Pagos | 16 |
| **Subtotal Etapa 1** | **95** |

## Etapa 2 — lo que cierra el problema de fondo

Esto todavía **no es una oferta**: son rangos orientativos. No puedo cerrar el número sin que me contestes las preguntas de más abajo, y no quiero darte una cifra firme sobre algo que todavía no está definido.

| Área | USD (estimado) |
|---|---:|
| Cerrar el camino del borrar-y-recargar un pago | 17 – 25 |
| El cheque como medio de pago propio, con fecha de recepción y fecha de acreditación | 50 – 67 |
| Pantalla de cierre de caja y conciliación del extracto bancario | 168 – 235 |
| **Subtotal Etapa 2 (estimado)** | **235 – 327** |

Sobre la última: el cruce que hice a mano para septiembre **ya lo probé como algoritmo** y resuelve solo el 91 % de los movimientos. Lo que falta es convertirlo en una pantalla donde subís el archivo del banco una vez por mes y el sistema te marca los tres grupos: lo que cruza, lo que falta del lado del sistema y lo que falta del lado del banco. Dos cosas que descubrí haciéndolo y que van adentro: el sistema tiene que **descartar solo** los movimientos que no son cobranzas (tus depósitos, los intereses), y tiene que saber que **una transferencia puede pagar varias ventas** — en septiembre pasó 6 veces.

## Rol de usuario

| Rol | Accesos |
|---|---|
| Administrador | Todo lo de esta propuesta: carga de pagos con las validaciones nuevas, y los totales agrupados de la pantalla de Pagos. |
| Vendedor | Carga de pagos con las validaciones nuevas, desde la pantalla de la venta. No ve la pantalla de Pagos ni sus totales. |

*Las altas de usuarios y la configuración las sigo gestionando yo, como hasta ahora.*

## Qué incluye

- Las tres áreas de la Etapa 1, con sus validaciones funcionando en las tres pantallas donde hoy se carga un pago.
- La planilla con el detalle completo de la conciliación de septiembre, línea por línea.
- Las pruebas sobre las dos pantallas de venta por separado, antes de subirlo.
- El aviso a tu equipo **antes** de subir el cambio, no después. Esto importa: el "Editar pago" de septiembre no se usó nunca, y sospecho que es porque nadie les contó que estaba.
- La corrección sin cargo de cualquier error propio de lo que entrego.

## Qué no está incluido

- La Etapa 2 (es un estimado, no está cotizado en firme).
- La corrección de los datos que ya están mal cargados en el sistema: los 3 pagos con fecha futura y los casos puntuales de septiembre. Son un arreglo a mano sobre la base, lo hago aparte y lo conversamos.
- Averiguar con el banco si los movimientos repetidos del extracto son una doble acreditación real.
- Reemplazar tu planilla de Excel o la carpeta de Drive.
- Capacitación presencial.

## Lo que necesitamos de tu parte

- **Decime dónde se acreditan los cobros con tarjeta y los de Mercado Pago**: en la misma cuenta que las transferencias, o en otra. Son $4.768.320 de septiembre y necesito saberlo antes de armar el tercer total.
- **Preguntale a quien carga los pagos por qué no usa el "Editar pago"**: si no sabía que existía, si le resulta incómodo el motivo obligatorio, o si no lo encuentra. De eso depende cómo encaro la Etapa 2.
- **Revisemos juntos el 18/09**: hay 7 ingresos al banco de ese día sin ningún pago cargado. Es el único día del mes con ese patrón y me cierra que ese día se cargó todo como efectivo.
- Una persona de referencia para probar la carga de pagos cuando esté lista.

## Condiciones comerciales

- **Etapa 1 (USD 95):** 50% para arrancar y 50% contra entrega.
- Precios en dólares.
- La Etapa 2 la cotizo en firme cuando tenga tus respuestas.
- Si el alcance crece sobre lo descripto, lo volvemos a conversar antes de arrancar.

---

**Olvidata Soft — bourdinjoaquin@gmail.com — olvidatasoft.com**
