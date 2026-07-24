# Olvidata**Soft**

---

**Manual de Usuario — Sistema KOI Dumplings**
**OlvidataSoft · Julio 2026**

## Sobre el sistema

Tu sistema reemplaza los dos Excel que usabas hasta ahora ("Estado de Resultados KOI" y "Reparto de Utilidades Inversores") por una única plataforma web, con un dashboard profesional para vos y para cada uno de tus inversores. En la práctica, así es como lo vas a usar mes a mes:

- Iniciás sesión con tu usuario y contraseña — no hay instalación, funciona desde cualquier navegador.
- Cargás el tipo de cambio del mes (el sistema te sugiere el valor blue del día para que no tengas que buscarlo aparte).
- Cargás las ventas del mes (Salón, Pedidos y Mostrador, separadas en facturadas e informales) y los gastos por rubro — el sistema calcula automáticamente los conceptos que dependen de un porcentaje (regalías, canon, comisiones, impuestos, previsiones).
- Ves el resultado del mes al instante: total de ventas, total de gastos, resultado del ejercicio, rentabilidad y el equivalente en dólares — sin tener que sumar nada a mano.
- Cuando cerrás el período, el sistema calcula automáticamente cuánto le corresponde a cada inversor según sus puntos, descuenta los consumos que hayan tenido en el local, y **le envía un mail a cada inversor activo** con su liquidación personal y el resultado del mes.
- Cada inversor entra con su propio usuario y ve únicamente su inversión: cuánto aportó, cuánto cobró históricamente, qué porcentaje de su capital ya recuperó y su rentabilidad promedio — en pesos y en dólares.
- Vos, como administrador, además tenés a mano el historial completo de reparto de todos los inversores, la vista anual del estado de resultados (igual que la hoja del Excel, pero siempre actualizada), y la gestión de usuarios.
- Todo el sistema tiene tema claro y oscuro, elegís el que prefieras y el sistema lo recuerda la próxima vez que entres.

## Cómo ingresar al sistema

El sistema ya está funcionando con tu información real (se migró el histórico completo desde tus Excel, de noviembre 2024 a mayo 2026 — más detalle en la sección *"De dónde salen los números"* al final de este documento).

Tenés un usuario de prueba ya creado para que empieces a recorrerlo:

| Campo | Valor |
|---|---|
| Usuario | `juani.skari@gmail.com` |
| Contraseña | `Olvidata2026!` |
| Rol | Administrador |

*Por seguridad, te recomendamos cambiar esta contraseña la primera vez que ingreses (Menú de usuario, arriba a la derecha → Cambiar contraseña) y pedirnos que demos de alta con su propio usuario a cada persona que vaya a usar el sistema — Administrador para vos/tu equipo, Inversor para cada uno de tus socios.*

## Rol de usuario

| Rol | Accesos |
|---|---|
| **Administrador** | Dashboard, carga del estado de resultados mensual, vista anual, configuración de rubros/porcentajes/tipo de cambio, puntos de inversión, cierre de período y liquidaciones, reparto general histórico, gestión de usuarios, configuración de notificaciones por mail. |
| **Inversor** | Dashboard, vista anual del estado de resultados (solo lectura), y "Mi inversión" — sus propios datos únicamente. |

*Nota: existe un nivel de acceso adicional de uso interno de Olvidata Soft (soporte técnico y tareas de mantenimiento), que no forma parte de tu operación diaria y no se detalla en este manual.*

## Cómo funciona el Dashboard — paso a paso

El Dashboard es la pantalla principal — la ven tanto vos como cada inversor (cada uno ve los mismos números globales del local; los datos personales de cada inversor están en "Mi inversión", no acá).

**1. Elegí el período.** Arriba a la derecha seleccioná año y mes. Si el mes todavía está abierto (no cerrado), vas a ver un aviso "Abierto — datos parciales": es normal, significa que ese mes se sigue cargando.

**2. Mirá el resumen general.** Las cinco cards de arriba te muestran, para el mes elegido: Ventas Totales, Total Gastos, Resultado, Resultado en dólares (con el tipo de cambio del mes) y Rentabilidad %.

**3. Revisá el detalle de Ventas.** Más abajo vas a encontrar: ventas con y sin impuesto, cantidad de ventas, ticket promedio, ventas por día y cubierto promedio; un gráfico de torta con la distribución por canal (Salón / Pedidos / Mostrador); una tabla con el desglose de facturado (A) vs informal (B); y las mismas ventas por canal desagregadas en A y B.

**4. Revisá el detalle de Gastos.** La tabla de "Gastos por Rubro" te muestra cuánto se gastó en cada categoría (Costo de Mercadería, Personal, Servicios, Alquileres, Impuestos y Cargas, Gastos Generales) y qué porcentaje representa cada una sobre el total.

**5. Mirá la evolución histórica.** Al final de la pantalla hay un gráfico de líneas con Ventas, Gastos y Resultado de los últimos 12 o 24 meses (podés alternar entre ambas vistas con los botones de arriba del gráfico) — te sirve para ver la tendencia del negocio de un vistazo.

**Casos especiales contemplados:**
- Si un mes no tiene ventas cargadas todavía, el Dashboard lo indica claramente en vez de mostrar un error o un cero engañoso.
- Si falta cargar el tipo de cambio del mes, el valor en dólares queda marcado como "pendiente" hasta que se cargue.

## Cómo funciona la carga del Estado de Resultados — paso a paso

Esta es la pantalla que usás vos (o quien vos designes) para cargar la información del mes — reemplaza la carga manual que hacías en el Excel.

**1. Elegí el mes.** Se navega con las flechas de mes anterior/siguiente, o desde el menú.

**2. Cargá el tipo de cambio.** Hacé clic en "Tipo de Cambio" en el menú: vas a ver una tabla con las cotizaciones del día (oficial, blue, MEP, cripto, tarjeta, etc.). El sistema te sugiere el valor blue promedio; podés usarlo tal cual con el botón "Usar" de la fila que prefieras, o escribir el valor manualmente. Guardás y ese es el tipo de cambio de ese mes.

**3. Cargá las ventas del mes.** En "Estado de Resultados", completás las ventas de Salón, Pedidos y Mostrador, cada una separada en facturada (A) y no facturada (B), más la cantidad de comensales y la cantidad de ventas (tickets) del mes. El sistema calcula automáticamente los totales (Ventas A, Ventas Totales) a medida que cargás.

**4. Cargá los gastos por rubro.** Los conceptos que se calculan solos por porcentaje (regalías, canon, comisiones de tarjeta, impuestos, previsiones) **ya aparecen calculados** apenas cargaste las ventas — no hace falta tocarlos. Los conceptos manuales (costo de mercadería, sueldos, alquiler, servicios, etc.) los cargás vos con el botón de edición (lápiz) de cada línea.

**5. Revisá los totales.** Al pie de la pantalla ves, actualizados en tiempo real, el Total de Gastos, el Resultado del Ejercicio y su equivalente en dólares.

**6. Cerrá el período cuando esté todo cargado.** El botón "Cerrar período" te lleva a una pantalla de previsualización (ver siguiente sección) antes de confirmar — el cierre es la acción que dispara el reparto a los inversores y el envío de los mails, así que solo lo hacés cuando ya cargaste todo el mes.

*Aclaración: una vez que un período está cerrado, sus valores quedan fijos — si necesitás corregir algo después de cerrado, contactanos a nosotros o a tu super-administrador interno.*

**Casos especiales contemplados:**
- Si intentás cerrar un mes sin tipo de cambio cargado o sin ventas cargadas, el sistema te avisa qué falta antes de dejarte continuar.
- Los porcentajes de cada concepto calculado (regalías 3%, canon 2,5%, comisiones de tarjeta 5%, etc.) se configuran una sola vez en "Configuración" y de ahí en adelante se aplican solos cada mes — si en algún momento cambia un porcentaje, se lo actualizamos nosotros y rige desde el mes que corresponda, sin alterar los meses ya cerrados.

## Cómo funciona el cierre de período y el reparto a inversores — paso a paso

**1. Vista previa antes de cerrar.** Al hacer clic en "Cerrar período" desde el Estado de Resultados, el sistema te muestra una previsualización: el resultado del mes, la utilidad que le corresponde a cada punto de inversión, y el detalle de lo que cobraría cada inversor según sus puntos vigentes.

**2. Cargá los consumos del mes, si los hay.** Si algún inversor consumió en el local durante el mes, cargás ese monto en su fila — el sistema lo descuenta automáticamente de lo que le corresponde cobrar (nunca te va a dejar cargar un consumo mayor a lo que ese inversor cobraría ese mes).

**3. Confirmá el cierre.** Al confirmar, el sistema: cierra el período (ya no se puede editar), genera la liquidación de cada inversor con estado "Pendiente", y **envía automáticamente un mail a cada inversor activo** con el resumen del mes y su liquidación personal.

**4. Gestioná los pagos.** Una vez cerrado el mes, entrás a "Liquidaciones" para marcar como "Pagada" la liquidación de cada inversor a medida que efectivamente les transferís el dinero (con la fecha de pago). Si te equivocaste, un Administrador puede reabrir una liquidación ya pagada, indicando el motivo.

**Casos especiales contemplados:**
- Si el envío de un mail falla (por ejemplo, un problema de conexión puntual), el cierre del período **no se cancela** — el mail fallido queda registrado y lo podés reenviar manualmente desde "Hist. notif. cierre".
- Los consumos de un inversor nunca pueden superar el monto que cobraría ese mes — el sistema te avisa si lo intentás.

## Cómo funciona "Reparto General" — para vos como administrador

Es la vista histórica completa de todos los repartos mensuales: por cada período ves el tipo de cambio usado, la utilidad por punto, el total repartido y cuánto cobró cada inversor — todo en una sola tabla, con buscador y filtros, para que no tengas que ir mes por mes.

## Cómo funciona "Mi inversión" — para cada inversor

Cada inversor, al ingresar con su propio usuario, ve únicamente sus datos:

- Capital que aportó, dividendos cobrados (acumulados y del mes), porcentaje de su capital ya recuperado, y su rentabilidad mensual promedio — en pesos y en dólares.
- Un historial completo mes a mes de lo que cobró, con la fecha de pago de cada liquidación.

*Un inversor nunca puede ver los datos de otro inversor — cada uno ve exclusivamente lo propio.*

## Cómo funciona la configuración del sistema — para vos como administrador

En "Configuración" administrás el catálogo de rubros y subrubros de gasto (por ejemplo, agregar un nuevo subrubro dentro de "Gastos Generales" si aparece un tipo de gasto nuevo) y los porcentajes de los conceptos que se calculan solos. En "Usuarios" das de alta, editás o desactivás los usuarios que acceden al sistema, y podés blanquear la contraseña de cualquiera si la olvida. En "Inversores" y "Puntos" gestionás la ficha de cada inversor y sus puntos de inversión asignados (los puntos de un inversor pueden cambiar de un mes a otro, y el sistema lleva el historial de esos cambios).

## Qué no incluye esta versión

Estas tres funcionalidades quedaron fuera de esta entrega — son candidatas a una próxima etapa, una vez que definamos el alcance y el costo con vos:

- Visualización de las cámaras IP del local dentro del sistema.
- Registro de asistencia del personal por huella digital.
- Conexión automática con la base de datos de tu sistema de ventas (Ayres) — hoy la carga de ventas se hace de forma manual, tal como se acordó en el alcance de esta etapa.

## De dónde salen los números (para tu tranquilidad)

Todo el histórico que ves desde noviembre 2024 hasta mayo 2026 fue migrado directamente desde tus dos Excel, mes por mes — no se volvió a calcular ni a estimar nada, se llevaron los mismos valores. El total de gastos de cada uno de esos meses fue verificado uno por uno contra el total que el propio Excel calculaba, y el capital total de los inversores migrado (**USD 287.500**) coincide exactamente con el que manejabas.

Dos aclaraciones sobre el histórico, para que no te llame la atención si las ves:
- Tu Excel no separaba las ventas entre Salón, Pedidos y Mostrador en los meses históricos (solo llevabas el total facturado/no facturado) — por eso, en los meses migrados, vas a ver el 100% cargado como "Salón". A partir del primer mes que cargues vos directamente en el sistema, vas a ver el desglose real por canal.
- Tampoco se llevaba la cantidad de comensales ni la cantidad de tickets por mes en el Excel — esos campos aparecen vacíos ("—") en los meses históricos, y se van a completar a partir del primer mes que cargues en el sistema.

---

**Olvidata Soft — olvidatasoft@gmail.com — olvidatasoft-002-site15.jtempurl.com**
