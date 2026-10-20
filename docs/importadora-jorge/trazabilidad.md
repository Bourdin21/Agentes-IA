# Trazabilidad — importadora-jorge

## 2026-10-20 — Alta del proyecto y presupuesto preliminar de preventa (PRE-01)

**Origen.** Lead de outbound frio captado por el bot del CRM. Calificado el 2026-10-20, etapa "Derivado
manual". Rubro CRM: comercio o alquiler de maquinaria. Zona: CABA. No existia carpeta en `/docs` ni
antecedente del cliente en el repo.

**Decision de metodo — gate saltado a proposito.** Se cotizo sin definiciones 1, 2 y 3 aprobadas, que es
lo que exige la secuencia obligatoria. Motivo: es preventa, no implementacion. El entregable es un
**presupuesto preliminar con supuestos declarados**, no habilita Implementacion, y si el cliente avanza
corre la secuencia completa antes de tocar codigo. Queda registrado como excepcion consciente, no como
omision.

**Alcance.** Lo pedido por el cliente en la conversacion de calificacion: gestion de importacion + ventas +
stock, en linea, reemplazando un sistema de facturacion que ya pagan. Tambien se menciono un asistente de
WhatsApp.

**Reutilizacion cross-proyecto — verificada en codigo, no declarada.** Siguiendo la regla de 2026-10-06
(no cotizar contra una base de reuso sin confirmar que existe), se corrio `grep` sobre
`C:\Sistemas\Ferreteria La Platense` y `C:\Sistemas\marihogar`. Todo lo citado existe: cuentas corrientes
de clientes y proveedores (PAT-001), ordenes de compra, movimientos y ajuste de stock (PAT-013), ventas con
IVA por linea y multi-medio (PAT-003), notas de credito, ARCA en produccion real (PAT-006) y el patron de
documento que declara moneda y congela cotizacion (PAT-055). **R = 89,2 %.**

`la-platense` queda como proyecto de referencia dominante: a efectos de software es el mismo negocio
(comercio con stock, proveedores en moneda extranjera, cuentas corrientes, ventas con IVA y facturacion).

**Unico item sin base en el estudio:** el prorrateo de costos de importacion (flete, aduana, despachante)
sobre el costo unitario. Se cotizo como item propio con contingencia del 25 %, separado del modulo de
ordenes de compra — exactamente lo que la regla de 2026-10-06 obliga despues del desvio de La Platense
Entrega 3, donde un item sin base quedo escondido dentro del modulo mas grande y lo multiplico x2,4.

**Numeros.** M total 69,5 h en 18 modulos; PERT 73,4 h; techo interno 83,9 h. Sanity check del total:
3,86 h/modulo contra mediana 3,44 de los comparables → ratio 1,12, dentro de rango. Subtotal de lista
USD 729,75; con Tokens IA distribuido, USD 912,19.

**Consulta a `olvidata-ceo` (Paso 0.5, perfil atipico).** Senales de capacidad de pago establecida: ya pagan
software, B2B, importador que opera en USD. Mismo patron que FABINCO. Decision del CEO:

1. Precio de lista, **sin** descuento de expansion (COM-020), aunque R = 89,2 % calificaba para 30 %.
   Dato que respaldo la decision: el descuento solo movia el precio de 912 a 800 (-12 %) porque el piso de
   Build lo comprime — se regalaba el tier casi sin efecto sobre el cierre.
2. **Numero comercial fijado en USD 1.200**, por encima de los USD 912,19 de la formula. Ambos numeros
   quedan documentados (patron habitual: el numero comercial no reemplaza al formal, convive con el).
3. **Excepcion a la regla de ano 1 de mantenimiento gratis**: se cobra desde el ano 1, plan PREMIUM
   USD 600/ano (~26 tablas de negocio).
4. Asistente de WhatsApp en la misma propuesta como setup aparte (USD 700-1.200), **sin recurrente propio**
   (COM-021): al vivir sobre el mismo hosting, su atencion se funde en el plan de mantenimiento.

**Entregables.** `definiciones/4-presupuestador.md` (calculo completo, autocorreccion, costo interno de IA,
riesgos y preguntas abiertas) y `presupuesto-cliente.md` (documento comercial con formato de la instruccion
31). El costo interno de IA (USD 87,40 de costo sombra) no aparece ni se menciona en el documento cliente.

**Pendiente.** Nueve preguntas de relevamiento abiertas, todas gatillo de reestimacion — entre ellas cuantos
depositos, si facturan electronicamente hoy, como reparten los costos de importacion y el volumen esperado de
WhatsApp (define si el setup del asistente es 700 o 1.200). El numero no esta comunicado al cliente todavia.

## 2026-10-20 (bis) — El rubro del CRM estaba mal: revision PRE-02

**Disparador.** Research del sitio del cliente antes de mandar la propuesta, a pedido de Joaquin.

**Hallazgo.** Importadora Jorge **no vende maquinaria**. Es una **importadora mayorista poli-rubro** con mas
de 70 anos (bazar, jugueteria, libreria, cosmetica, electronica, fitness, kiosco), que vende a comercios y
revendedores desde Sarmiento 2444, Once. El rubro del CRM — "Comercio o alquiler de maquinaria" — es
incorrecto, y con el se armo el gancho del outbound y todo el alcance de PRE-01.

**Lo que el research agrega y el CRM no sabia:** catalogo de **1.604 SKUs** en 11 rubros, venta por **bulto y
por unidad**, minimos de compra ($200.000 envio / $50.000 pedido), pagos solo por transferencia y efectivo
(sin tarjetas), envios al interior por transporte, y sobre todo un **e-commerce a medida ya en produccion**
(desarrollado por `kirke.ws`) **que no publica stock**.

**Consecuencia de alcance.** Aparecen tres cosas que PRE-01 no tenia: sincronizacion de stock y precios con
la tienda existente, doble lista mayorista/minorista, y expedicion de envios al interior. Y la migracion del
catalogo deja de ser una exclusion comoda: nadie carga 1.604 SKUs a mano.

**Chequeo de reuso que evito un error de cotizacion.** El item mas valioso — sincronizar stock con la tienda —
matchea con **PAT-036**, pero el patron esta **disenado, no construido** (`libreria-horizonte`). Por la regla
de 2026-10-06 **no se cotiza como reuso**: va como item sin base, contingencia 25 %, con la dependencia de un
tercero (acceso a la base o API del sitio de Kirke) declarada como riesgo propio. Es exactamente el error que
costo x2,4 en La Platense Entrega 3, detectado esta vez antes de poner el numero.

**Impacto estimado (grueso, no cotizacion).** M de 69,5 a ~93,8 h; la zona comercial razonable pasa de
USD 1.200 a **USD 1.800-2.200**. El numero formal queda pendiente de responder las 9 preguntas nuevas de
relevamiento, que reemplazan a las de PRE-01.

**Estado.** `presupuesto-cliente.md` **quedo desactualizado a proposito** — describe un sistema para una
importadora de maquinaria. No enviar hasta rehacerlo. El mensaje de WhatsApp preparado por `olvidata-sales`
tampoco sirve: su gancho es el prorrateo de costos de importacion de maquinaria.

**Pendiente de decision de Joaquin.** (a) Corregir el rubro del contacto en el CRM productivo — no se toco
desde esta sesion. (b) Rehacer el presupuesto con el alcance real. (c) Rehacer el mensaje de contacto.

## 2026-10-20 (ter) — Correccion del rubro en el CRM productivo

Autorizada explicitamente por Joaquin. Contacto **Id 5247** (`contactos`), CRM productivo:

| Campo | Antes | Ahora |
|---|---|---|
| `Rubro` | `Comercio o alquiler de maquinaria` | `Comercios de venta por peso o unidad` (Id 18 del catalogo) |
| `Categoria` | `rent` | `NULL` |

Revertir, si hiciera falta:
`UPDATE contactos SET Rubro='Comercio o alquiler de maquinaria', Categoria='rent' WHERE Id=5247;`

**Hallazgo que corrige una hipotesis propia.** Al principio se supuso que `Categoria='rent'` explicaba la mala
clasificacion del rubro. **No la explica:** 376 contactos tienen ese valor y abarcan Salud, Dieteticas,
Inmuebles e Indumentaria — es una etiqueta de campana vieja, no una categoria de negocio. Se vacio igual
por autorizacion explicita, no porque fuera la causa. El error de rubro viene de la clasificacion del bot,
que queda sin causa identificada.

**Nota de zona horaria (relevante para cualquier escritura futura a mano sobre el CRM).** La aplicacion
guarda `UpdatedAt` en **UTC**, el servidor MySQL responde `NOW()` en otra zona, y la maquina local corre en
hora argentina. La primera escritura dejo el timestamp 3 h atrasado respecto de la convencion de la app y
hubo que corregirlo con `datetime.utcnow()`. Los tres relojes son distintos: no asumir ninguno.

El snapshot `docs/olvidata/pipeline.md` se regenero y ya muestra el rubro corregido.

## 2026-10-20 (quater) — PRE-03: presupuesto rehecho sobre el alcance real

Recotizacion completa con el negocio verdadero (mayorista poli-rubro, 1.604 SKU, e-commerce propio).
Participaron los tres criterios que pidio Joaquin: presupuestador (WBS y PERT), `olvidata-ceo` (numero
comercial y particion) y `olvidata-presupuesto-bot` (asistente de WhatsApp, cotizado aparte).

**Alcance:** 19 modulos, M 81,5 h, PERT 86,2 h, techo interno 101,0 h. Subtotal de lista USD 855,75.
**R cayo de 89,2 % a 66,9 %** (tier 2) porque los 5 items sin base construida suman 27 h.

**Numero: USD 1.900** (o **USD 1.690** sin la sincronizacion con la tienda). Sin descuento, 50/50 por etapa,
mantenimiento PREMIUM USD 600/ano desde el ano 1.

**Lo que define esta cotizacion:** el item mas caro (#16, publicar stock en la tienda, M=9) es a la vez el
mas riesgoso y el argumento de venta, y **depende de que `kirke.ws` de acceso**. Se resolvio con una clausula
de **alcance** —10 dias para confirmar, y si no hay acceso el total baja a 1.690— en vez de una de cobro. Se
descarto cobrar 70 % por adelantado de esa pieza: cobrar por algo que todavia no se sabe si se puede construir
crea un problema peor que el que evita. El numero comercial quedo deliberadamente por debajo del techo del
rango de mercado por la misma razon.

**Sanity check fuera de rango, aceptado:** 4,29 h/modulo contra mediana 3,44 → ratio 1,25. No se recalibro:
los items sin base (migracion de 1.604 SKU, sincronizacion con un sitio de terceros) son estructuralmente mas
pesados que el modulo promedio del historial, que casi siempre tiene patron disponible. Forzar el ratio a 1,20
habria recortado justo donde esta el riesgo.

`presupuesto-cliente.md` reescrito entero y listo para entregar.

## 2026-10-20 (quinquies) — El asistente de WhatsApp sale de la propuesta

Decision de Joaquin: la propuesta lleva **solo el sistema de gestion**. El asistente no aparece en
`presupuesto-cliente.md` ni como opcional. La cotizacion que habia preparado `olvidata-presupuesto-bot`
(MVP USD 700-900 ofrecible ya, FULL USD 900-1.200 + conector, sin abono propio) queda archivada en
`definiciones/4-presupuestador.md` por si el cliente lo pide mas adelante, junto con la advertencia de que
el tier FULL no tiene precedente construido en el estudio.

El mensaje de contacto preparado por `olvidata-sales` tampoco lo menciona: quedo centrado en el stock
publicado en la tienda.

## 2026-10-20 (sexies) — PRE-04: baja de Kirke, sistema interno solamente

El cliente informo que **dan de baja el sitio de Kirke**. Joaquin definio el alcance: **solo sistema interno,
sin web publica**. Sale el modulo de sincronizacion de stock con la tienda (M=9).

**USD 1.900 → USD 1.690.** No es decision nueva: es el numero que `olvidata-ceo` ya habia fijado para el
escenario sin esa pieza. Desaparece la clausula de alcance a 10 dias y la dependencia de un tercero; el
precio queda cerrado y unico.

**Dos indicadores mejoraron al sacar ese item:** R subio de 66,9 % a 75,2 % (vuelve al tier 1) y el sanity
check del total entro en rango (ratio 1,17 contra 1,25). Era el item sin base mas grande del WBS.

**Se verifico antes de cotizar** que el estudio **no tiene antecedente de catalogo publico ni e-commerce**:
los carritos del historial son de punto de venta interno. Si mas adelante piden canal online, es desarrollo
sin base y se cotiza aparte.

**Dos cosas quedaron explicitas en la propuesta:** que al apagar el sitio se quedan sin canal de venta online
y que este sistema no lo reemplaza (en "Que no esta incluido", sin dramatizarlo), y el pedido de **exportar
el catalogo antes de dar de baja el sitio** — si lo apagan sin bajar los 1.604 productos, la carga inicial
se complica.

`presupuesto-cliente.md` actualizado: sin tienda, sin alcance A/B, total USD 1.690.

## 2026-10-20 (septies) — ALERTA: el producto que ibamos a vender no es el que necesitan

**Aparecio una segunda conversacion del mismo cliente, por otro canal.** Contacto **Esteban**
(tel 5491176530700, canal **Ads pagos**, no outbound), que abre con *"Hablamos recien desde Importadora
Jorge"*. Es el mismo negocio con otro interlocutor.

**Lo que dijo Esteban, textual:**
- *"Vendemos bazar, libreria, jugueteria, art de kiosco y pesca"* (confirma poli-rubro; agrega **pesca**)
- *"Son mas de 1800 items"* (el sitio publica 1.604; el catalogo real es mayor)
- **"hacemos todo de un mismo sistema"**
- **"control de stock bien, procesar importaciones que lo hago por fuera (excel + claude)"**

**Consecuencia: el alcance de PRE-01 a PRE-04 apunta al lugar equivocado.** Ya tienen un sistema que les
resuelve el stock. Venderles un sistema de gestion completo de USD 1.690 es proponerles reemplazar algo que
no esta roto: de los 18 modulos cotizados, la enorme mayoria resuelve problemas que ellos ya tienen
resueltos. **El dolor real es un proceso puntual** — normalizar las planillas de importacion y dejarlas
listas para cargar en el sistema que ya usan, trabajo que hoy hacen a mano con Excel y Claude.

El bot ya le ofreció exactamente eso (*"un agente que te toma las planillas de importacion, las normaliza y
te deja todo listo para cargar al sistema"*) y Esteban respondio **"que tienen ustedes que me puedan
ofrecer?"**: esta esperando una propuesta concreta de ESO, no de un ERP.

**Contradiccion entre los dos interlocutores, sin resolver:** "Equipo" dijo *"estoy averiguando para cambiar
a un sistema online"*; Esteban dice que el sistema actual les va bien salvo importaciones. Puede ser que no
opinen lo mismo, o que decida uno solo. **Hay que identificar quien decide antes de cotizar.**

**Estado:** `presupuesto-cliente.md` (USD 1.690) **NO SE ENVIA.** El mensaje de WhatsApp con el numero
tampoco. Encuadre y precio del producto correcto elevados a `olvidata-ceo`, junto con que hacer con las dos
conversaciones abiertas y si el sistema de gestion queda como etapa posterior o sale de la conversacion.

**Dato comercial:** el contacto de Esteban entro por **Ads pagos** — es un lead ya pagado, no outbound frio.

## 2026-10-20 (octies) — PRE-05: decision de reencuadre

`olvidata-ceo` confirmo el freno. **El Build sale de la conversacion** (no queda como etapa 2: ofrecer
reemplazo de algo que no esta roto viola COM-002). El producto pasa a ser un **agente de importaciones
bespoke standalone** del frente AI Agents — no licencia de rubro, porque no hay nucleo de "importadora
mayorista" y no se vende una licencia por un solo agente de un solo cliente.

**Tier Basico: setup USD 1.500-2.500 (promo hasta 31/12) + USD 2.400/ano.** Sin integracion directa al
sistema del cliente: entrega listo para carga manual. Si piden integracion, sube de tier con la regla vigente.

**Se sigue con Esteban** (Ads pagos, lead ya pagado, pidio propuesta). El hilo de "Equipo" se archiva.

**Advertencia de metodo anotada:** no cotizar un agente standalone con la tasa de modulos de Build
(M x USD 10,50) — subestima un producto que vive solo. El numero sale del catalogo de AI Agents.

**Para cerrar el numero hace falta ver una planilla de importacion real:** el formato manda sobre el esfuerzo
del parser. Es el primer pedido al cliente.
