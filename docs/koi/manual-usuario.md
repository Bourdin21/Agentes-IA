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

  **Ahora podés traerlas directo de Ayres.** El botón **"Traer de Ayres"** consulta tu sistema de ventas y te muestra, antes de tocar nada, una comparación entre lo que hay cargado y lo que informa Ayres. Recién si le das "Aplicar" se guardan los valores. Si cancelás, no se modifica nada. Ver la sección *"Traer las ventas desde Ayres"* más abajo.

**4. Cargá los gastos por rubro.** Los conceptos que se calculan solos por porcentaje (regalías, canon, comisiones de tarjeta, impuestos, previsiones) **ya aparecen calculados** apenas cargaste las ventas — no hace falta tocarlos.

  Los conceptos manuales (costo de mercadería, sueldos, alquiler, servicios) **los escribís directamente en la grilla**: hacés clic en el importe, escribís y al salir del campo se guarda solo. Un tilde verde te confirma cada guardado. Ya no hay que abrir ninguna ventana ni recargar la página entre gasto y gasto.

  *Los campos que se calculan por porcentaje se distinguen con un borde punteado.* Si alguna vez necesitás poner un importe distinto del que da el porcentaje (por ejemplo, el impuesto real que te liquidaron), **podés escribirlo igual**: esa línea queda marcada en naranja y deja de seguir el porcentaje, hasta que uses el botón ↺ de la columna "%" para volver al cálculo automático.

**5. Revisá los totales.** Al pie de la pantalla ves, actualizados en tiempo real, el Total de Gastos, el Resultado del Ejercicio y su equivalente en dólares.

**6. Cerrá el período cuando esté todo cargado.** El botón "Cerrar período" te lleva a una pantalla de previsualización (ver siguiente sección) antes de confirmar — el cierre es la acción que dispara el reparto a los inversores y el envío de los mails, así que solo lo hacés cuando ya cargaste todo el mes.

*Aclaración: una vez que un período está cerrado, sus valores quedan fijos — si necesitás corregir algo después de cerrado, contactanos a nosotros o a tu super-administrador interno.*

**Casos especiales contemplados:**
- Si intentás cerrar un mes sin tipo de cambio cargado o sin ventas cargadas, el sistema te avisa qué falta antes de dejarte continuar.
- Los porcentajes de cada concepto calculado (regalías 3%, canon 2,5%, comisiones de tarjeta 5%, etc.) se configuran una sola vez en "Configuración" y de ahí en adelante se aplican solos cada mes — si en algún momento cambia un porcentaje, se lo actualizamos nosotros y rige desde el mes que corresponda, sin alterar los meses ya cerrados.

## Traer las ventas desde Ayres — paso a paso

Hasta ahora las ventas del mes se cargaban a mano, mirando los reportes de Ayres. Ahora el sistema las trae solo.

**1. Entrá al Estado de Resultados del mes** que querés cargar. El botón **"Traer de Ayres"** aparece al lado de las ventas, siempre que el período esté **abierto**. En un mes ya cerrado no aparece: los meses cerrados no se tocan.

**2. Hacé clic.** El sistema consulta Ayres y arma el total del mes. Puede tardar unos segundos: Ayres solo permite pedir de a 10 días, así que por detrás se hacen tres o cuatro consultas y se suman. Eso es cosa del sistema, vos no tenés que hacer nada.

**3. Mirá la comparación.** Se abre una ventana con dos columnas: lo que hay cargado hoy y lo que informa Ayres. Las líneas que cambian aparecen resaltadas; las que quedan igual, en gris. Abajo te dice cuántas ventas leyó y de qué fechas.

  **Hasta acá el sistema no modificó nada.** Solo leyó.

**4. Decidí.** *"Aplicar"* guarda los valores; *"Cancelar"* cierra la ventana y todo queda como estaba.

**5. Listo.** Al aplicar, las ventas quedan cargadas y **los conceptos que se calculan por porcentaje se actualizan solos** (regalías, canon, previsiones), igual que si las hubieras escrito a mano. El resultado del ejercicio se recalcula al instante.

### Cosas que conviene saber

**Las ventas anuladas no se cuentan.** Ayres marca las ventas anuladas por separado. El sistema las excluye del total y te avisa cuántas encontró. Esto importa para la cantidad de comensales y el ticket promedio: si se contaran, los números saldrían distorsionados.

**Los canales se separan solos.** Ayres identifica cada venta como Salón, Pedidos o Mostrador, y el sistema las imputa a la columna que corresponde. Es una de las cosas que la carga manual venía teniendo difícil de sostener.

**El mes en curso se puede consultar.** Si traés un mes que todavía no terminó, el sistema te avisa que el total es parcial. Sirve para ir mirando cómo viene el mes.

**Si Ayres no responde, no pasa nada.** El sistema te avisa que no pudo conectarse y **el período queda exactamente como estaba**. Nunca queda un mes cargado a medias: o entra todo, o no entra nada.

**Podés probar la conexión sin tocar ningún mes.** En "Sistema" hay una prueba de conexión con Ayres que te dice si está todo bien, sin modificar ningún dato.

### Si alguna vez deja de funcionar

La conexión con Ayres depende de la dirección del servidor donde corre tu sistema de ventas. **Si en algún momento cambian ese servidor, la conexión se corta** y el sistema va a avisarte que no puede conectarse. No es una falla del sistema ni se pierde ningún dato: hay que reconfigurar la dirección nueva. Avisanos y lo resolvemos.

Mientras tanto, la carga manual de ventas **sigue estando disponible siempre**: la conexión con Ayres es una comodidad, no un requisito.

## Cómo funciona el cierre de período y el reparto a inversores — paso a paso

Esta es la operación más importante del sistema: **es la que reparte plata**. Por eso tiene una previsualización antes de confirmar y varias trabas para que nada se dispare por accidente.

### Qué pasa exactamente cuando cerrás un mes

**1. Vista previa antes de cerrar.** Al hacer clic en "Cerrar período" desde el Estado de Resultados, el sistema te muestra una previsualización: el resultado del mes, la utilidad que le corresponde a cada punto de inversión, y el detalle de lo que cobraría cada inversor según sus puntos vigentes. **Todavía no pasó nada** — es sólo una cuenta en pantalla.

**2. Cargá los consumos del mes, si los hay.** Si algún inversor consumió en el local durante el mes, cargás ese monto en su fila y el sistema lo descuenta de lo que le corresponde cobrar. Nunca te va a dejar cargar un consumo mayor a lo que ese inversor cobraría ese mes.

**3. Confirmá el cierre.** Recién acá el sistema hace tres cosas, en este orden:

  - **Cierra el período.** Los números del mes quedan fijos y la pantalla de carga pasa a sólo lectura.
  - **Genera una liquidación por inversor**, en estado *Pendiente*, con el detalle de cómo se llegó a ese monto.
  - **Manda un mail a cada inversor activo** con el resumen del mes y su liquidación personal.

*El envío de los mails corre por detrás, después de cerrar. Si falla el mail de alguien, el cierre **no se cancela** ni se deshace: el período queda cerrado, las liquidaciones generadas, y el mail fallido queda registrado para reenviarlo.*

### Cómo se calcula lo que cobra cada inversor

El reparto sale del **Resultado del Ejercicio** del mes — ventas menos gastos — dividido por los **100 puntos** de inversión. Eso da la utilidad por punto. A cada inversor le corresponde esa utilidad multiplicada por **los puntos que tenía vigentes ese mes**, menos sus consumos.

Dos aclaraciones que suelen generar preguntas:

- **Los puntos son por mes.** Si un inversor cambió su cantidad de puntos, el sistema usa los que estaban vigentes en el mes que se está cerrando, no los de hoy.
- **Puede haber puntos sin dueño.** Si en un mes no están asignados los 100 puntos, la parte no asignada simplemente no se reparte.

### Los estados de una liquidación

En **Liquidaciones** seguís el recorrido de cada pago:

| Estado | Qué significa |
|---|---|
| **Pendiente** | Se generó al cerrar el mes. El inversor todavía no cobró. |
| **Pagada** | Vos la marcaste como pagada, con su fecha. Es el registro de que la transferencia se hizo. |

Marcás como pagadas de a una o varias juntas, indicando la fecha del pago. Si te equivocaste, un Administrador puede **reabrir una liquidación ya pagada** dejando el motivo, y vuelve a *Pendiente*.

### Volver a abrir un mes cerrado

Si necesitás corregir números de un mes ya cerrado, un Administrador puede reabrirlo desde el Estado de Resultados. **Pedís el motivo obligatoriamente**, y antes de confirmar el sistema te dice **cuántas liquidaciones se van a descartar y cuántas de ellas ya estaban pagadas**.

Eso último es lo importante y conviene leerlo con atención: **reabrir un mes descarta las liquidaciones de ese mes, incluidas las que ya marcaste como pagadas**. El dinero que efectivamente transferiste no se deshace —eso pasó en el banco, no en el sistema— pero sí desaparece el registro de esa liquidación. Al volver a cerrar el mes se generan liquidaciones nuevas con los números corregidos, y hay que volver a marcarlas como pagadas.

Por eso la reapertura pide motivo y muestra el conteo antes: **no es una acción para deshacer un tipeo**. Para corregir el importe de un gasto existe la corrección directa, que se explica a continuación y no descarta ninguna liquidación. La reapertura queda para cuando hay que cambiar las ventas del mes, o agregar y sacar conceptos.

### Corregir un gasto de un mes cerrado, sin reabrirlo

A veces un mes ya cerrado tiene un gasto mal cargado. En vez de reabrirlo —que descarta todas sus liquidaciones—, un Administrador puede corregir el importe directamente, desde el mismo Estado de Resultados.

Antes de confirmar, el sistema te muestra qué va a pasar con las liquidaciones de ese mes:

- Las **pendientes** se recalculan con el resultado corregido, respetando los puntos, los consumos y el tipo de cambio que cada inversor tenía al cierre.
- Las **pagadas no se tocan**: esa plata ya se transfirió. El sistema te dice cuáles son, con su importe y su fecha de pago, para que decidas vos si hace falta compensar a alguien.

Cada corrección queda registrada. **Sólo el Administrador puede hacerla**; el Encargado no.

En un mes cerrado se corrigen importes de gastos. Para agregar o sacar conceptos, o para cambiar las ventas, hay que reabrir el mes.

### Mover un gasto a otro concepto

Si un gasto quedó cargado en un concepto equivocado —o en uno del catálogo anterior, como "Otros gastos"—, un Administrador puede moverlo a otro concepto con el botón ⇄ de su fila. Funciona en meses abiertos y cerrados.

Si el concepto de destino ya tiene un importe en ese mes, los dos se suman. Antes de confirmar ves la cuenta completa: lo que había, lo que se mueve y cómo queda. **El total de gastos del mes nunca cambia al mover**: el gasto sólo cambia de renglón.

Es la herramienta para ordenar los meses históricos que todavía muestran conceptos del catálogo anterior. Esos conceptos aparecen con la etiqueta "Histórico" y su importe se puede editar como el de cualquier otro.

### Los mails a los inversores

Hay dos caminos por los que sale un mail de cierre:

**Automático, al cerrar el mes.** Es el de siempre: cerrás y salen los mails. No tenés que hacer nada.

**Manual, desde "Hist. notif. cierre".** Sirve para reenviar. Podés reenviarle a un inversor puntual —por ejemplo si su mail rebotó— o volver a mandar a todos los del período.

Cuando elegís reenviar a todos, **el sistema te muestra primero una previsualización**: el mail tal como lo va a recibir el inversor, con datos reales, y la lista completa de destinatarios con su dirección. Los inversores que no pueden recibirlo —porque no tienen usuario o no tienen mail cargado— aparecen aparte, con el motivo.

Recién cuando confirmás salen los mails. **Si cancelás, no se envía nada.**

En esa misma pantalla queda el historial de todo lo enviado: a quién, cuándo, y si salió bien o falló.

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

Las tres funcionalidades que habían quedado fuera de la primera entrega —cámaras, registro de asistencia por huella y conexión con Ayres— **ya están entregadas**. Lo que sigue afuera por ahora:

- **Sincronización automática de ventas.** Traer las ventas de Ayres es una acción que disparás vos, con confirmación previa. El sistema **no** se conecta solo ni actualiza nada por su cuenta: es a propósito, para que nadie modifique un mes sin querer.
- **Traer de Ayres otra cosa que no sean ventas** (compras, stock, caja). La conexión existe y podría ampliarse, pero hoy solo se usa para ventas.

## De dónde salen los números (para tu tranquilidad)

Todo el histórico que ves desde noviembre 2024 hasta mayo 2026 fue migrado directamente desde tus dos Excel, mes por mes — no se volvió a calcular ni a estimar nada, se llevaron los mismos valores. El total de gastos de cada uno de esos meses fue verificado uno por uno contra el total que el propio Excel calculaba, y el capital total de los inversores migrado (**USD 287.500**) coincide exactamente con el que manejabas.

Dos aclaraciones sobre el histórico, para que no te llame la atención si las ves:
- Tu Excel no separaba las ventas entre Salón, Pedidos y Mostrador en los meses históricos (solo llevabas el total facturado/no facturado) — por eso, en los meses migrados, vas a ver el 100% cargado como "Salón". A partir del primer mes que cargues vos directamente en el sistema, vas a ver el desglose real por canal.
- Tampoco se llevaba la cantidad de comensales ni la cantidad de tickets por mes en el Excel — esos campos aparecen vacíos ("—") en los meses históricos, y se van a completar a partir del primer mes que cargues en el sistema.

---

**Olvidata Soft — olvidatasoft@gmail.com — olvidatasoft-002-site15.jtempurl.com**
