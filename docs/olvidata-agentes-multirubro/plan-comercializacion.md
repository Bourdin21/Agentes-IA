# Plan de comercialización y comunicaciones — Olvidata Agentes Multi-rubro

**Fecha:** 2026-09-22 · **Autor:** Joaquín Bourdin · **Horizonte:** 14 días (22/09 → 05/10)
**Objetivo:** una venta real cobrada en los próximos 7 días, con presupuesto ≈ USD 0 en pauta.
**Insumos:** agentes `olvidata-ceo`, `olvidata-marketing`, `olvidata-cm`, `olvidata-sales` (corrida 2026-09-22).

---

## 0. El plan en una página

**Qué se vende, en este orden:** *"sacale una foto y se carga solo"* → *"te digo dónde está la
diferencia"* → el resto de la red de agentes → *"y no te cobro dos veces"*. Los dos primeros cierran
la venta, el tercero justifica el abono mes a mes, el cuarto saca la objeción de precio antes de que
aparezca. Nunca se nombra el portal multi-tenant ni "inteligencia artificial para tu empresa".

**Por qué vale lo que vale:** *el dueño no deja de decidir, decide una vez y a un nivel más alto.* En
vez de resolver lo mismo doscientas veces al año, **define las reglas que lo resuelven** y el sistema
las aplica todos los días. Es su criterio, aplicado sin que él esté. Nunca *"la IA hace tu trabajo"*.

**Precio:** USD 1.300 de setup + USD 90/mes + consumo de IA aparte, con tope. **Reemplaza** el
mantenimiento anual, no se suma.

**Honestidad en el primer contacto:** no hay nada armado todavía para ese cliente. Es un
**ofrecimiento** para mejorar su operatoria diaria, y es **un sistema aparte** del que ya tiene
—aunque se conecte a su base—. Prometer como hecho lo que no está es la forma más rápida de perder a
alguien que ya confía.

**A quién.** Día 1: **Delicias** (conciliación bancaria), **Estancia Santa Rosa** (liquidación del
consignatario por foto), **Eleven** (foto del contador). Día 5: Koi, MariHogar, Vino y Se Fue.
WhatsApp nominal, nunca difusión. Nada de outbound frío: la cartera propia alcanza.

**La demo son 15 minutos y el papel lo pone el cliente**, no Joaquín. Propuesta escrita el mismo día,
vence en 7. Dos seguimientos y se archiva; no hay un tercero.

**Qué se construye primero: la conciliación.** Es de solo lectura, no depende de resolver la
escritura, y el conector MySQL sirve para toda la cartera de una vez.

**Los dos riesgos que hay que mirar antes de ofertar:**
1. A los clientes **SCALE con upsells** el esquema parejo les baja la facturación. Sacarlos de la
   oferta y cotizarlos aparte.
2. Los agentes de foto **escriben, y eso todavía no existe**. Van como borrador que el cliente
   aprueba — que además es el mejor argumento de confianza.

**Dos vías de ciclo largo, en paralelo:** el **gimnasio** (preguntarle cómo programa, la próxima vez
que vayas) y la **Tesorería** (consulta al abogado el día 2: bloquea todo y tarda). En las dos, el
agente **aplica las reglas que define el cliente**; nunca se presenta como que lo reemplaza.

**El único número que cuenta esta semana: un anticipo del 50 % acreditado.**

> Lo que sigue es el detalle: la red de agentes de cada cliente, los mensajes listos para mandar, las
> objeciones y la economía del esquema.

---

## 1. La decisión de fondo

Los cuatro agentes coincidieron en el diagnóstico y divergieron en la vía. La síntesis:

> **En los próximos 7 días se le vende a la cartera propia, uno por uno, por WhatsApp. En las
> próximas 4 semanas el contenido construye demanda. Pauta paga: no todavía.**

**Qué NO se vende:** "el portal multi-tenant de agentes IA", ni "inteligencia artificial para tu
empresa". El motor de atrás no se nombra.

**Qué SÍ se vende, y en este orden:**

1. **"Sacale una foto y se carga solo."** La factura, el remito, el cheque, la liquidación, el
   contador de la máquina. Se termina el tipeo.
2. **"Te digo dónde está la diferencia."** La conciliación contra el banco, contra el proveedor,
   contra el papel. El problema que aparece todos los meses y nadie sabe de dónde sale.
3. **"Y además."** El resto de la red de agentes: el aviso de la mañana, los informes, las consultas
   libres.
4. **"Y no te cobro dos veces."** Todo eso entra dentro del mantenimiento que el cliente ya paga.

Los puntos 1 y 2 son los que cierran la venta. El 3 la justifica mes a mes. El 4 saca la objeción de
precio antes de que aparezca.

### Por qué vale lo que vale — el argumento, para todos los clientes

> **El dueño no deja de decidir: decide una vez y a un nivel más alto.**
> En vez de resolver la misma cosa doscientas veces al año, **define las reglas que la resuelven** y
> el sistema las aplica todos los días.

Es la justificación del precio y sirve para los trece clientes, no solo para el gimnasio:

- El profe no delega la programación: **define su método** y los WODs salen solos.
- El ferretero no revisa producto por producto: **define cuándo reponer** y el sistema le avisa.
- El contador de Delicias no busca la diferencia a mano: **define cómo concilia** y aparece señalada.
- El analista de la Tesorería no escribe cada especificación de cero: **define la plantilla y las
  reglas del área** y arranca con el borrador hecho.

Por eso no es un empleado más barato ni un chatbot: es **su criterio, aplicado sin que él esté**.
Y por eso se paga un abono y no una vez — el criterio se ajusta, y cada ajuste vale para todos los
días siguientes.

**Cómo se dice, y cómo no:** nunca *"la IA hace tu trabajo"*. Siempre *"vos definís cómo se hace, el
sistema lo hace todos los días"*.

---

## 2. Estado técnico real (actualizado 2026-09-22)

| Estado real | Impacto comercial |
|---|---|
| **M9 deploy ejecutado.** Portal en producción: https://agentes.olvidata.com.ar/ (responde 200, `/health/vivo` OK) | **Hay URL pública para mostrar.** La demo es en vivo, no en local |
| **Piloto de Contadores BMA en producción**, en elaboración | Hay un caso real andando: se puede hablar de producto, no de promesa |
| M5 / M10 / M11 / M12: pendientes de QA | Riesgo en la entrega, no en la demo |
| Sin EULA firmado ni registro DNDA | Bloquea el contrato formal, no una orden de trabajo acotada |
| **No existe conector a base de datos.** M11 tiene conector HTTP genérico con lista blanca y protección SSRF, nada más | **Es el trabajo real de esta oferta.** Ver §3.2 |
| Sin conocimiento real cargado por rubro | Cada configuración carga lo del cliente |

**Lo que esto cambia respecto de la versión anterior del plan:** ya no se vende un "piloto fundador"
con cupos. Se vende una **configuración de agentes sobre un producto que está en el aire y con un
cliente andando**. El ángulo de comunicación deja de ser build-in-public y pasa a ser producto.

---

## 3. Vía A — el cierre (días 1 a 7)

### 3.1. La red de agentes de cada cliente

Con **agentes ilimitados**, el modelado deja de ser "un agente que resuelve un dolor" y pasa a ser lo
que dice el objetivo del proyecto: **las etapas operativas del negocio, cada una con su agente,
trabajando coordinadas.** Eso es lo que se muestra en la demo, y es lo que justifica el abono.

**El esqueleto es el mismo para toda la cartera** (por eso escala), y se adapta por rubro:

| Etapa | Agente | Qué hace, en general |
|---|---|---|
| **Entrada de datos** | **Cargá con una foto** | Le sacás una foto a una factura, un remito, un cheque o una planilla y **lo carga al sistema**. No hay que tipear nada |
| **Control** | **Conciliación** | Cruza lo que dice el sistema contra lo que dice el banco, el proveedor o el papel, y **señala dónde está la diferencia** |
| Abastecimiento | **Compras** | Qué pedir, a quién, a qué precio, qué está por vencer |
| Precios | **Precios** | Qué quedó por debajo del costo de reposición |
| Stock | **Stock** | Qué falta, qué sobra, qué no rota |
| Venta | **Ventas** | Qué se vende, qué cayó, qué cliente dejó de comprar |
| Cobranza | **Cobranzas** | Quién debe, hace cuánto, y redacta el reclamo |
| Post-venta | **Entregas / Service** | Qué quedó pendiente y por qué |
| Gestión | **Control de gestión** | Coordina a los demás y arma el informe del período |
| Transversal | **Vigía** | Corre solo cada mañana y avisa sólo si hay algo fuera de lugar |
| Transversal | **Consultas** | "¿Cuánto vendimos de X el mes pasado?" en castellano, sin reportes |

**Los dos primeros son los que venden.** "Sacale una foto y se carga solo" y "encontrá la diferencia
de caja del mes" son problemas que el cliente sufre todos los meses, que entiende en cinco segundos y
que puede ver funcionando en la demo con un papel de su escritorio. Lo demás es la red que los
sostiene.

El **Vigía** es el que justifica el abono mes a mes: trabaja aunque nadie entre al portal.

Abajo, la adaptación por cliente. Relevamiento de repos del 2026-09-22; el orden es por probabilidad
de cierre esta semana.

#### Prioridad 1 — se contactan en los días 1 y 2

**① Koi Dumplings — Portal del Inversor** · gastronomía con inversores · .NET 10 · `db_a7251f_koidump`
Ventas mensuales por canal (salón/pedidos/mostrador), gastos por concepto, liquidaciones y puntos por
inversor, benchmarks de mercado. Integra Ayres POS y el fichador QuickPass.

| Agente | Qué resuelve |
|---|---|
| **Foto → gasto** | Foto de la factura del proveedor gastronómico y queda cargada con su concepto de gasto. Hoy se tipea a mano, factura por factura |
| **Conciliación del POS** | Cruza la venta que informa Ayres contra lo que quedó registrado: dónde falta plata y de qué turno |
| **Cierre del mes** | Arma el estado de resultados y explica los desvíos contra el mes anterior y contra el benchmark. Hoy es manual y llega tarde |
| **Atención al inversor** | Contesta "¿cuánto me tocó y por qué?" con los números de su propia liquidación. Hoy alguien responde de a uno |
| **Costos** | Qué concepto de gasto se disparó y contra qué venta se mide |
| **Personal** | Cruza el fichador con la venta por turno: si está sobredimensionado o falta gente |
| **Vigía** | Avisa si un día de venta se sale del rango esperado |
| **Consultas** | Preguntas libres sobre ventas, gastos y liquidaciones |

**② Vino y Se Fue** · distribuidora de vinos con consignación · .NET 10 · `db_a7251f_vinoyse`
Pedidos, compras, **concesión recibida de proveedores** con sus movimientos, versiones de precio por
producto de proveedor, cuentas corrientes. Ya parsea catálogos PDF/HTML.

| Agente | Qué resuelve |
|---|---|
| **Foto → remito** | Foto del remito del proveedor y el ingreso de mercadería queda cargado, incluida la que entra en consignación |
| **Lista nueva** | Le sacás una foto (o le pasás el PDF) a la lista del proveedor y dice qué cambió, cuánto, y qué precio de venta quedó atrasado. Con inflación, es trabajo semanal y se vende a pérdida sin verlo |
| **Conciliación con proveedor** | Cruza el resumen de cuenta que manda el proveedor contra la cuenta corriente del sistema y marca las diferencias |
| **Consignación** | Qué mercadería en concesión lleva meses sin rotar y hay que devolver. Capital y espacio ajenos que nadie controla |
| **Compras** | Qué reponer según rotación real, y a cuál de los proveedores conviene |
| **Cobranzas** | Cuenta corriente por cliente, con el reclamo redactado |
| **Vigía** | Avisa cuando un producto queda vendiéndose por debajo del costo nuevo |
| **Consultas** | Preguntas libres sobre pedidos, stock y proveedores |

**③ Eleven La Plata** · alquiler y service de fotocopiadoras · .NET 10 · `db_a7251f_eleven2`
Máquinas, contratos, **historia de contadores**, incidencias, repuestos, pedidos a técnico y a
proveedor, cuentas corrientes.

| Agente | Qué resuelve |
|---|---|
| **Foto → contador** | El técnico le saca una foto al display de la máquina y **la lectura queda cargada** en la historia de contadores, sin planilla ni cargado posterior. *Es el que más ahorra: hoy cada lectura se anota a mano y se tipea después* |
| **Excedentes** | Cruza contadores contra el tope de cada contrato: qué cliente se pasó de copias y hay que facturar. Hoy se factura tarde o no se factura |
| **Foto → remito de repuestos** | Foto del remito del proveedor y el ingreso de repuestos queda cargado |
| **Service predictivo** | Qué máquina viene con historial de incidencias y conviene visitar antes de que pare |
| **Repuestos** | Qué repuesto se va a necesitar según las máquinas instaladas y su consumo |
| **Cobranzas** | Quién debe, hace cuánto, con el recordatorio escrito |
| **Renovaciones** | Qué contrato vence y cuál conviene renegociar según su consumo real |
| **Vigía** | Avisa del contador que se disparó y del contrato por vencer |
| **Consultas** | Preguntas libres sobre máquinas, contratos y clientes |

**④ MariHogar** · casa de decoración y hogar · .NET 10 · `db_a7251f_marihog` · **AFIP en producción real**
El de datos financieros más ricos de la cartera: ventas con pagos en cuotas de tarjeta, **cheques con
acreditación automática**, gastos recurrentes, cuenta corriente de proveedores y local, órdenes de
compra, entregas con reintentos, presupuestos, y ya tiene un módulo de proyección financiera.

| Agente | Qué resuelve |
|---|---|
| **Foto → cheque** | Foto del cheque y queda cargado con banco, importe y fecha de acreditación. Hoy se copia a mano, número por número |
| **Foto → factura de proveedor** | Foto de la factura y queda la orden de compra con su movimiento de cuenta corriente |
| **¿Llego a fin de mes?** | Proyecta la caja cruzando cheques por acreditar, cuotas de tarjeta por cobrar, gastos recurrentes y vencimientos de órdenes de compra. Vender en cuotas y pagar al contado rompe la caja, y hoy se ve cuando ya pasó |
| **Conciliación bancaria** | Cruza el extracto del banco contra los cheques y pagos del sistema, y marca qué no coincide |
| **Entregas** | Qué venta quedó sin entregar y por qué, con los intentos fallidos. Hoy el cliente reclama antes de que nadie se entere |
| **Presupuestos** | Cuál no se convirtió en venta y hace cuánto: el seguimiento que nadie hace |
| **Compras** | Qué reponer, de qué proveedor, y cómo queda la cuenta corriente con él |
| **Precios** | Qué producto quedó por debajo del costo de reposición tras el último aumento |
| **Vigía** | Cheque por vencer, entrega trabada, gasto recurrente que se disparó |
| **Consultas** | Preguntas libres sobre ventas, caja y proveedores |

#### Prioridad 2 — días 3 a 5

**⑤ Showroom Griffin** · indumentaria y calzado · .NET 10 · `db_a7251f_showroo`
Stock por variante (talle/color) con movimientos y ajustes, ventas con múltiples pagos y cuotas,
devoluciones y cambios, remitos.

| Agente | Qué resuelve |
|---|---|
| **Foto → ingreso de mercadería** | Foto del remito del proveedor y carga el ingreso **abierto por talle y color**. Es la carga más tediosa del rubro: una caja son decenas de variantes |
| **Conciliación de recuento** | Le pasás el conteo físico y te marca dónde no coincide con el sistema, variante por variante |
| **Curva de talles** | Qué talle/color se agotó de lo que más sale y hay que reponer ya. Se pierde venta con la curva rota y no se ve hasta el recuento |
| **Temporada** | Qué quedó sin vender y conviene liquidar antes de que valga menos |
| **Precios** | Qué quedó por debajo del costo de reposición |
| **Devoluciones** | Qué producto vuelve más de lo normal — problema de calidad o de talle mal cargado |
| **Vigía** | Quiebre de stock en los productos que más rotan |
| **Consultas** | Preguntas libres sobre ventas por variante y stock |

**⑥ LabIPAC** · laboratorio bioquímico · .NET 10 · `db_a7251f_labipac` · integra FABA
Producción mensual facturable por centro de salud, valorizada por unidad bioquímica, con precios
automáticos y manuales.

| Agente | Qué resuelve |
|---|---|
| **Foto → planilla del centro** | Foto de la planilla de prácticas que manda el centro de salud y queda cargada la producción, sin tipear |
| **Producción facturable** | Conciliación: diferencias entre lo que llegó de FABA y lo cargado. Cada práctica sin conciliar es facturación perdida, todos los meses |
| **Precios por centro** | Qué centro quedó con precios viejos frente al nomenclador |
| **Cierre mensual** | Arma la producción del mes por centro y explica las variaciones |
| **Vigía** | Avisa si la producción de un centro cae fuera de su rango habitual |
| **Consultas** | Preguntas libres sobre producción, prácticas y centros |

**⑦ Delicias Naturales** · dietética y elaboración · MVC5/EF6 · `db_a7251f_delicia` · **AFIP real**
Recetas, movimientos de stock, solicitudes de ingreso, caja, ventas y facturación electrónica.

| Agente | Qué resuelve |
|---|---|
| **Foto → remito** | Foto del remito y te dice qué dice, si coincide con lo que se pidió y lo deja cargado. Consultar un remito deja de ser buscar el papel |
| **Balance de caja del mes** | Arma el balance mensual solo. *Hoy les cuesta sacar balances y es trabajo de varios días* |
| **Conciliación bancaria** | **Todos los meses hay diferencia con la cuenta del banco.** Este agente cruza el extracto contra la caja y los pagos del sistema y **dice exactamente dónde está la diferencia**: qué movimiento falta, cuál está duplicado, cuál tiene otro importe. *Es el agente que justifica la venta por sí solo* |
| **Producción** | Qué insumo va a faltar para producir lo que se está vendiendo, según las recetas |
| **Control fiscal** | Comprobantes pendientes y la **RG 5616/2024** — condición de IVA del receptor, obligatoria desde el **01/12/2026**, hoy en `false` en su configuración. *Urgencia real y con fecha* |
| **Costos de receta** | Cuánto cuesta hoy producir cada cosa, con los precios de compra actuales |
| **Vigía** | Insumo por quebrar, comprobante rechazado, diferencia de caja del día |
| **Consultas** | Preguntas libres sobre ventas, stock y producción |

**⑧ Ferretería La Platense** · ferretería · .NET 10 · `db_a7251f_laplaten`
Miles de SKU con código de barras, **clasificación ABC automática**, venta por unidad de medida
(metro, kilo), cierres de caja diarios y mensuales.

| Agente | Qué resuelve |
|---|---|
| **Foto → factura de proveedor** | Foto de la factura y actualiza costos y stock. En ferretería son remitos largos, de decenas de renglones |
| **Arqueo** | Conciliación del cierre de caja: de dónde sale exactamente la diferencia del día |
| **Reposición ABC** | Qué productos clase A están por quebrar y qué clase C tiene capital dormido. Con esa cantidad de artículos, nadie mira el ABC a mano |
| **Precios** | Qué quedó desactualizado contra el último costo de proveedor |
| **Cuenta corriente** | Qué cliente de cuenta se atrasó |
| **Vigía** | Quiebre de clase A y diferencias de caja |
| **Consultas** | Preguntas libres sobre stock, ventas y clientes |

*Gancho extra:* tiene el código de AFIP ya portado, esperando el certificado. Se puede ofrecer activar
la facturación electrónica en la misma visita.

**⑨ Estancia Santa Rosa** · ganadería · .NET 10 · `db_a7251f_ganader`
Movimientos de hacienda por categoría con matriz de transiciones, ventas con deducciones de
consignatario, egresos con pagos y caja.

| Agente | Qué resuelve |
|---|---|
| **Foto → comprobante de venta** | Foto de la liquidación del consignatario y **queda cargada la factura de venta con todas sus deducciones**, renglón por renglón. Hoy es cargado manual de un papel largo y lleno de conceptos |
| **Foto → comprobante de compra** | Foto de la factura del proveedor y queda el egreso cargado con su rubro |
| **Neto de venta** | Qué quedó realmente después de las deducciones. El precio de remate no es lo que entra |
| **Hacienda** | Stock de cabezas por categoría y qué animales corresponde recategorizar |
| **Conciliación de caja** | Cruza los movimientos de caja contra los comprobantes y marca lo que no cierra |
| **Egresos** | Qué gasto por rubro se disparó contra la campaña anterior |
| **Vigía** | Pagos por vencer y movimientos de stock fuera de lo esperado |
| **Consultas** | Preguntas libres sobre hacienda, ventas y gastos |

**⑩ RecoTrack** · logística de recolección · .NET 10 · `db_a7251f_recotra`

| Agente | Qué resuelve |
|---|---|
| **Foto → parte del chofer** | Foto del parte o del remito de descarga y queda cargado el trabajo del día, sin que alguien lo pase a mano en la oficina |
| **Foto → multa** | Foto de la boleta de infracción y queda asociada al chofer y al camión |
| **Parte diario** | Resumen del día y desvíos: horas extra, multas y accidentes por chofer |
| **Flota** | Qué camión acumula incidencias y conviene revisar |
| **Personal** | Horas extra por empleado contra lo presupuestado |
| **Vigía** | Trabajo sin cerrar, chofer con multas repetidas |
| **Consultas** | Preguntas libres sobre trabajos, camiones y empleados |

#### Prioridad 3 — ciclo más largo, no para esta semana

**⑪ LumiTrack** (alumbrado público municipal — despacho y priorización de reclamos por zona, control
de cuadrillas y consumo de materiales; cliente público, compra lenta) · **⑫ PI Apartments / Roaming** y
**⑬ Las Latas** (alquileres — ocupación, cobranza y gastos por unidad; legacy MVC5) ·
**⑭ Saldo Claro** (billetera personal, ticket chico).

*Inactivos, no se contactan:* CellPic (2022), Alquileres (2023), Dunas Village (2024).
*Sitios WordPress sin sistema propio* (Escaba, Bel Clau, el institucional de BMA): no aplican.

#### Fuera de cartera — el gimnasio, y por qué importa más que un cliente

**El gimnasio de Joaquín** · plataforma **Crossfy** (`app.crossfyapp.com`) · cliente nuevo, no paga
mantenimiento. Se le vende al profesor y dueño.

La oferta: **el agente aplica las reglas de programación que definen los administradores del
gimnasio**, arma los WODs siguiendo ese método, el profesor los ajusta si quiere, y se publican solos
en Crossfy por API. Sin foto y sin cargado manual.

> **Cómo se posiciona, y no es un detalle:** el profesor **no delega el criterio, lo automatiza.**
> El agente no inventa entrenamientos: **ejecuta el método que él definió**, con sus reglas, su
> progresión y sus escalados. Lo que se le saca de encima es el trabajo mecánico de escribir y cargar
> todos los días, no la decisión. Jamás presentarlo como "la IA te programa las clases": eso suena a
> reemplazo y se cierra la puerta sola. **Se presenta como "tu método, aplicado solo, todos los
> días".**

| Agente | Qué resuelve |
|---|---|
| **Programador según tus reglas** | Aplica el reglamento de programación cargado por los administradores —progresión semanal, qué no se mezcla nunca, material y espacio disponibles, niveles y escalados— y deja los WODs armados. El profe abre, mira y ajusta lo que quiera |
| **Publicador** | Los publica en Crossfy por API, todos los días, a horario. Tarea programada de M12: nadie tiene que acordarse de nada |
| **Ciclos** | Cuida que la semana tenga sentido dentro del mes, según el ciclo que definió el gimnasio |
| **Control de reglas** | Revisa lo publicado contra el reglamento propio y avisa si algo se desvió. *El agente auditándose contra las reglas del profe: refuerza que el método manda* |
| **Ocupación** | Qué horarios se llenan y cuáles quedan vacíos, para mover la grilla con datos y no por intuición |
| **Vigía** | Avisa si un día no se publicó o si una clase quedó sin cupo |

**La escalera de autonomía** — es cómo se vende y cómo se entrega, en ese orden:

| Etapa | Qué hace el agente | Qué hace el profe |
|---|---|---|
| 1 | Aplica las reglas y propone la semana | Revisa y aprueba cada día. **Nada se publica sin su visto bueno** |
| 2 | Publica lo que ya está aprobado | Aprueba la semana de una vez, los lunes |
| 3 | Aplica y publica siguiendo el reglamento | Ajusta **las reglas**, no los WODs uno por uno |

La etapa 3 es la que hay que saber vender: el profe no deja de decidir, **decide una vez y a un nivel
más alto**. En vez de escribir doscientos entrenamientos al año, define el método que los genera.

M12 ya implementa exactamente esto: por defecto una tarea programada **no recibe** las herramientas
que piden aprobación, y el Director las habilita cuando decide. Nunca se auto-aprueba. La escalera no
hay que construirla, hay que configurarla.

> **Acá el gate de evaluación de prompts no es burocracia: es seguridad física.** Un WOD mal
> programado —volumen de más, dos días seguidos del mismo patrón, una progresión mal escalada— puede
> lesionar a alguien. Por eso se arranca en la etapa 1 y **el profesor es siempre el responsable de
> lo que se publica**, lo cual además hay que decirlo explícitamente en el acuerdo. Nunca se ofrece
> la etapa 3 en la venta inicial: se ofrece como algo que él va a poder habilitar cuando confíe.

**El activo que queda del otro lado:** el motor de reglas de programación cargado como conocimiento
de rubro (M10), versionado y evaluado, que **nunca se distribuye**. Ojo con la distinción, porque
es la que hace escalable el negocio: **las reglas de cada gimnasio son suyas** —eso se le dice y se
le cumple—, pero **la estructura para expresarlas y ejecutarlas es de Olvidata**, y es lo que se
reutiliza en el gimnasio siguiente sin volver a construir nada. Es exactamente el caso de uso para el
que se diseñó el núcleo.

**Por qué es estratégicamente el más interesante de todo el plan:** no es un cliente, es **un rubro
nuevo entero**. Crossfy la usan muchos gimnasios; si esto funciona en uno, el manifiesto de rubro
`gimnasio` más el conector de Crossfy se replican a todos los demás **sin desarrollo nuevo**. Es el
primer caso donde el producto multi-rubro hace lo que dice el título del proyecto.

**El camino técnico está resuelto.** Crossfy tiene **API para dueños de gimnasio**, y Joaquín ya la
usa desde servidor en `C:\Sistemas\Crossfy Bot\webapp`: REST sobre `https://www.crossfyapp.com/api/`,
autenticada por token (`GET token/`), llamada por cURL desde PHP, con su propia webapp de
planificación semanal y cron (`api/plan.php`, `weekly.php`, `schedules.php`, `cron/scheduler.php`).
**No hay que descubrir cómo hablar con la plataforma: ya se habla.**

*(La extensión de Chrome del repo —la de auto-reserva— es otra cosa y no interviene acá.)*

**Lo único a confirmar, y es chico:** lo que la webapp ejercita hoy son endpoints de **lectura**
(`GET clases`, `GET detalleTurnos`). Falta probar el de **alta/publicación de clases con credenciales
de administrador** — el token que se usa hoy es de socio, no de dueño. Es una prueba de un rato con
el acceso del gimnasio, no un desarrollo.

**Encaja con lo que la plataforma ya tiene, sin construir nada nuevo:** M11 da credenciales cifradas
por organización, lista blanca de dominios y aprobación humana antes de que algo salga hacia afuera;
M12 da la tarea programada diaria y la autonomía gradual; M10 da el conocimiento de rubro versionado.
**Es el único caso de toda la propuesta que no necesita ni el conector a base de datos ni la vía de
escritura de §3.2.3.** Si Crossfy tiene API, este puede ser el primer cliente entregado de punta a
punta.

**Dónde está el trabajo, entonces:** no en el código, en el **relevamiento de la metodología**. Hay
que sentarse con el profesor y extraer cómo programa: qué estructura tiene su semana, qué no mezcla
nunca, cómo escala por nivel, qué material tiene. Eso se carga como conocimiento de rubro y es lo que
separa un agente que propone WODs genéricos —que el profe descarta en diez segundos— de uno que
propone los que él hubiera escrito. **Es el mismo trabajo que después se reutiliza en cada gimnasio
nuevo.**

> **Cuidado con PA-07 (AlwaysRunning).** Sigue abierto: sin él el sitio se duerme y las tareas
> programadas se atrasan. Un gimnasio que publica las clases a horario lo nota el primer día.
> Acá deja de ser una precondición técnica y pasa a ser parte del producto.

> **Precio:** no aplica el esquema de "no te cobro dos veces" — no paga mantenimiento. Decisión
> pendiente (§9): lo natural es tratarlo como **cliente cero del rubro**, con precio de referencia a
> cambio de poder usarlo como caso documentado. Lo que se compra acá no es el margen de un gimnasio:
> es abrir el rubro.

#### Fuera de cartera — Tesorería General de la Provincia, área de Análisis Funcional

**Quién compra:** la jefatura de Análisis Funcional de la Dirección de Sistemas, donde trabaja
Joaquín. **Qué se le vende:** que el área tenga **el contexto de todos sus sistemas cargado y
consultable**, y que **la especificación funcional salga en borrador**, conectado a **Jira y
Confluence**, que son las herramientas que el área usa todos los días.

**El dolor, dicho como dato:** el conocimiento de los sistemas está repartido entre páginas de
Confluence, tickets viejos de Jira y la cabeza de los analistas con más antigüedad. Cada
requerimiento nuevo arranca por reconstruir ese contexto a mano, y la especificación se escribe desde
cero con la plantilla del área. El analista nuevo tarda meses en saber qué toca qué.

| Agente | Qué resuelve |
|---|---|
| **Consultas sobre los sistemas** | "¿Qué valida el alta de una orden de pago?", "¿qué sistemas usan este circuito?". Contesta con la documentación del área **citando la página de Confluence o el ticket de Jira** de donde lo sacó |
| **Especificación funcional** | Toma un ticket de Jira con el requerimiento y arma el **borrador de la especificación con la plantilla del área**: alcance, actores, flujos, reglas de negocio, criterios de aceptación e impacto. Lo deja en Confluence como borrador, pendiente de revisión |
| **Relevamiento** | Antes de la reunión con el usuario, prepara las preguntas a partir del ticket y de lo que ya está documentado. Se llega a la reunión sabiendo qué falta, no a preguntar lo que ya estaba escrito |
| **Impacto** | Ante un cambio, qué otros sistemas, circuitos o especificaciones anteriores se ven afectados |
| **Consistencia** | Revisa que la especificación nueva no contradiga reglas ya documentadas en otra |
| **Casos de prueba** | De la especificación aprobada deriva los casos de prueba para QA |
| **Onboarding** | Le explica un sistema desde cero al analista nuevo, con la documentación del área |
| **Vigía** | Tickets "en análisis" sin especificación hace más de N días, y páginas de Confluence que quedaron viejas frente a cambios recientes |

> **Cómo se posiciona — misma regla que el gimnasio:** el analista **no delega el criterio**. El
> agente le saca de encima el borrador y la búsqueda de contexto; **la especificación la firma el
> analista**. Nunca presentarlo como "la IA hace el análisis funcional": en un área de sistemas del
> Estado eso cierra la puerta sola. Se presenta como *"arrancás cada requerimiento con el contexto ya
> juntado y el borrador ya escrito"*.

**Encaje técnico — casi todo existe:**

- **Jira y Confluence tienen API REST.** El conector HTTP de M11 (lista blanca de dominios,
  credenciales cifradas por organización, protección SSRF) alcanza para leer los dos. **No necesita
  el conector MySQL de §3.2.3.**
- **La escritura va con aprobación humana** (M6): crear la página borrador en Confluence o comentar el
  ticket en Jira es una llamada que el analista aprueba. Nada se publica solo.
- **La plantilla de especificación y las convenciones del área** se cargan como conocimiento (M10).
- **Es el mismo método que ya usa el estudio**: el flujo analista funcional → diseñador → arquitecto
  de Agentes-IA, aplicado a los sistemas de otro. Es además la mejor demo: se muestra funcionando sobre
  un proyecto propio, sin tocar un dato de la Tesorería.

**Lo que define la arquitectura, y hay que confirmar primero:** ¿Jira y Confluence son **Cloud** o
**Data Center** instalado en la red interna? Si son internos, el portal en SmarterASP no llega a
ellos, y la plataforma tendría que desplegarse **dentro de la infraestructura de la Tesorería**. Eso
cambia el producto de "abono sobre nuestra plataforma" a "instalación en el organismo", con otro
precio y otro soporte.

**Riesgos que frenan la venta hasta resolverlos:**

1. **Conflicto de intereses.** Joaquín es empleado del organismo al que le vendería. Hay que
   **consultar con un abogado** el régimen de incompatibilidades del empleo público provincial y de
   ética pública **antes de hacer cualquier oferta**. De eso depende la vía: venta como proveedor a
   través de Olvidata, o propuesta como proyecto interno del área. Y en cualquier caso, dejar
   documentado que **la plataforma es previa y propia de Olvidata**, desarrollada fuera del horario y
   de los recursos del organismo.
2. **Datos del Estado y modelo externo.** La documentación de los sistemas de Tesorería es
   información sensible. Mandarla a la API de un modelo de IA externo necesita **autorización de
   Seguridad Informática** del organismo y verificar si hay normativa provincial sobre el uso de IA.
   Hasta tenerla, **no se carga ni un documento real de la Tesorería** en el portal.
3. **Compra pública.** No hay seña del 50 %: se compra por procedimiento de contratación (directa por
   monto o licitación), con un ciclo de meses. **No entra en la semana de cierre**: es ciclo largo,
   como LumiTrack.

**Por qué igual vale la pena:** como el gimnasio con Crossfy, **no es un cliente, es un rubro**. Jira
y Confluence son estándar en áreas de sistemas de organismos públicos, bancos y empresas medianas.
Una plantilla de rubro `analisis-funcional` más el conector de Atlassian se replica sin desarrollo
nuevo. Y el comprador es alguien que entiende el producto a la primera: otro analista.

**Próximo paso, en este orden:** consulta legal → preguntar Cloud o Data Center → charla informal con
la jefatura para medir interés, con la demo sobre un proyecto propio → recién ahí, propuesta.

> **Contadores BMA** ya es el piloto en producción: no se le vende esta oferta, se lo usa como
> **caso de referencia** ("esto ya está andando en un estudio contable"). Sus agentes propios siguen
> la misma línea:
>
> | Agente | Qué resuelve |
> |---|---|
> | **Foto → control contra Bejerman** | Foto de una factura o de un extracto y **la compara contra lo que figura en Bejerman**: qué no está cargado, qué tiene otro importe, qué está duplicado |
> | **Conversor** | Lo que ya hace el conversor de liquidaciones, pero dentro del portal |
> | **Consultas** | Preguntas sobre procedimientos del estudio |
>
> Es, además, la mejor demo para los demás clientes: el mismo agente que mira un papel y lo cruza
> contra el sistema, cambiando de rubro.

> **Nada de prospección fría** (§8.3). Ni los ~94 escritos en mayo–julio con el pitch de
> HEAVEN/SIGMA/FORGE —productos dados de baja— ni los ~13 nunca contactados. La regla del estudio no
> la habilita para este producto hasta que esté definido su ICP, y con la cartera propia alcanza.

### 3.2. La oferta — "Agentes sobre tu sistema"

**No es un producto que se suma al mantenimiento: es el que lo reemplaza.** El cliente deja de pagar
el mantenimiento anual de su sistema y pasa a un único abono que cubre las dos cosas. *No se le cobra
dos veces al año.*

| Concepto | Precio |
|---|---|
| **Setup** — acceso a la plataforma completa, **agentes ilimitados** | **USD 1.300** (50/50) |
| **Abono mensual** — incluye el mantenimiento del sistema que ya tienen | **USD 90/mes** |
| **Consumo de IA** | **aparte, según uso real** |

Precio del token verificado contra la página oficial el **2026-09-22**: Sonnet 5 en USD 2/10 por
millón, sin cambios.

**Qué cambia respecto de lo que paga hoy:** hoy paga una vez al año el mantenimiento de su web.
A partir de ahora paga USD 90 por mes y eso **incluye ese mismo mantenimiento** más la plataforma de
agentes entera. Un solo abono, un solo vencimiento.

**Incluye:** el mantenimiento del sistema actual, igual que hasta hoy · acceso a la plataforma con
**agentes ilimitados, configurados por ellos** · el conector de solo lectura a su propia base ·
**la capacitación para que sepan usarlo** · acompañamiento durante el arranque · monitoreo y tope de
gasto.

> ### Lo que Joaquín hace, y lo que no
>
> **El relevamiento lo hace un agente, no Joaquín.** El configurador conversacional ya existe (M4b,
> *"Configurar reglas conversando"*): el Director le cuenta al agente cómo trabaja la empresa, el
> agente lee las reglas actuales y propone las nuevas, y cada propuesta se aplica, se corrige o se
> descarta con un botón. Nada se aplica sin confirmación.
>
> **Entonces el trabajo de Joaquín es explicar el sistema, no configurarlo.** Eso cambia tres cosas
> de golpe:
>
> 1. **"Ilimitado" deja de ser un riesgo** y pasa a ser literal. Los agentes los arma el cliente; no
>    hay horas de Joaquín detrás de cada uno.
> 2. **El costo marginal por cliente se desploma**, y con él buena parte del problema de precio de
>    §8.4. Lo que se entrega es acceso más capacitación, no trabajo a medida.
> 3. **El cuello deja de ser el tiempo de Joaquín.** El techo ya no son diecinueve clientes: es
>    cuántos puede capacitar y acompañar, que es otro número y mucho más alto.
>
> **Y cambia qué es el producto.** No se vende "te configuro agentes": se vende **una plataforma
> donde el cliente configura sus propias reglas, conversando**, más alguien que le enseña a usarla.
> El concepto de la campaña —*vos definís las reglas*— deja de ser una metáfora de venta y pasa a ser
> la descripción literal del producto.

**Queda afuera, y se dice:** el consumo de IA (va aparte, medido) · integraciones con terceros
(bancos, Mercado Pago, ARCA) · desarrollo nuevo sobre el sistema web, que sigue cotizándose como
siempre.

**Cómo se explica lo que el agente puede tocar** — es la pregunta que va a hacer todo cliente:
*"Consulta y concilia solo. Cuando carga algo —una factura, un remito, un cheque— te lo deja
preparado y vos le das aceptar. Nunca modifica nada por su cuenta."*

**El argumento, en una línea:** *"En vez de cobrarte el mantenimiento una vez al año, te cobro un
abono mensual que incluye el mantenimiento igual que hasta ahora, y encima te da la plataforma de
agentes completa sobre tu propio sistema."*

### 3.2.1. La economía del esquema

USD 90/mes = **USD 1.080/año**. Contra lo que cada cliente paga hoy de mantenimiento:

| Plan de mantenimiento hoy | Delta anual |
|---|---|
| STARTER (USD 360) | **+720** |
| PRO (USD 480) | **+600** |
| PREMIUM (USD 600) | **+480** |
| SCALE (USD 1.000) | **+80** |
| **SCALE con upsells activos (~1.390)** | **−310 — se pierde plata** |

> **Antes de anunciar el esquema parejo hay que sacar de la lista a los SCALE con upsells.** A esos
> se les cotiza aparte, con precio pactado. El resto de la cartera da fuertemente positivo.
> *Falta el mapeo cliente → plan: el CEO no lo tiene y no lo inventó.*

Sobre ~19 clientes activos, si migra toda la cartera: **+USD 24.700 de setup por única vez** y el
recurrente pasa de ~USD 9.000 a ~USD 20.500 al año, es decir **+USD 11.500/año que se sostienen**.
El recurrente promedio por cliente sube de ~450 a 1.080.

**Cómo y cuándo se cobra cada cosa** (decisión 2026-09-23):

| | Cuándo se cobra | Qué es |
|---|---|---|
| **Abono del plan** | **Adelantado**, a principio de mes | Ingreso fijo y predecible |
| **Consumo de IA** | **Vencido**, al cierre, por lo realmente usado | Sólo se puede saber al final |

**Los dos topes, que son distintos y hacen cosas distintas:**

1. **Tope del plan (comercial).** Es el crédito de IA incluido en el abono. **Al superarlo no se corta
   nada:** a partir de ahí se factura **excedente a costo real × 3**, vencido y junto con el abono del
   mes siguiente. Una sola factura, nunca una nota aparte.
2. **Tope real (duro), configurable por organización.** Es el que **corta cualquier uso de IA**. Existe
   para que un mes raro no termine en una factura impagable ni en un consumo sin control. Lo define
   Olvidata por cliente.

**Aviso automático al 80 %** del tope del plan, y de nuevo al acercarse al tope real.

> **Cuidado con cómo se dice.** El excedente **no es recuperar un costo: es el componente de mayor
> margen** (por cada dólar de tokens se facturan tres). Eso está bien como negocio, pero hay que
> tenerlo presente: **cuanto más consume el cliente, más se gana**, y el que controla cuántos tokens
> se queman es Olvidata, que escribe los prompts. El día que se optimice el caché y baje el consumo,
> baja también la facturación. Conviene saberlo de antemano y no descubrirlo cuando pase.
>
> El tope real, además, **no es una cortesía al cliente: es protección propia.** El consumo se cobra
> vencido, así que los tokens ya se gastaron cuando llega la factura. Sin tope duro, un cliente que no
> paga se lleva puesto un consumo que Olvidata ya desembolsó.

**Falta implementarlo.** Hoy existe un solo tope (`Tenant.LimiteMensualUsd`) y **corta**: funciona
como tope real, pero no hay tope del plan separado. Hace falta un segundo valor por organización —el
crédito incluido— que dispare el aviso y la facturación del excedente sin bloquear. Es un campo nuevo
en `Tenant`, su migración, el cálculo en `ControlGasto` y el comando del Admin. Acotado, pero toca
el esquema con un cliente en producción.

### 3.2.2. Qué significa "ilimitado" (y dónde está el límite)

Si cada agente lo modela Joaquín a mano, ilimitado es pérdida garantizada. La distinción, que se dice
desde el primer día y no cuando el cliente pida el agente número doce:

| | Quién lo hace | Costo |
|---|---|---|
| **La red inicial de §3.1** | Olvidata, desde las plantillas del rubro en el núcleo | Incluida en el setup |
| **Agentes que el cliente arma solo** | El cliente, con el configurador del portal | **Ilimitados, sin cargo** |
| **Un agente a medida** (reglas propias, conectores nuevos, subagentes) | Olvidata | Se cotiza aparte: +500 / +1.000 / +2.000 según tier |

Lo ilimitado es **la plataforma**, no las horas de Joaquín. Eso es verdad y se puede decir sin mentir.

> **Decisión pendiente:** el CEO propone incluir en el setup **un** agente configurado por Olvidata.
> El modelado de §3.1 propone la **red inicial completa**, que es viable sólo si sale de plantillas
> de rubro reutilizables y no de trabajo a medida por cliente. La red completa es mucho mejor
> argumento de venta y mejor demo; el riesgo es el tiempo de configuración del primer cliente de cada
> rubro. **Se resuelve armando la plantilla una vez por rubro**, no por cliente.

### 3.2.3. El conector a la base de datos — lo que hay que construir

**No existe todavía.** M11 sólo tiene conector HTTP genérico con lista blanca y protección SSRF.
Hace falta un `IConectorTipo` nuevo. Reglas con las que se acota, y que además son argumento de
venta:

- **Solo lectura, siempre.** El agente nunca escribe sobre la base de producción del cliente.
- **Vistas SQL dedicadas**, nunca tablas crudas: se define explícitamente qué ve el agente, sin PII
  de más. Esto también achica el relevamiento.
- Usuario de base de solo lectura sobre esas vistas, credenciales cifradas con el mismo patrón por
  organización que ya usa M11.
- Conexión directa a la base de producción (el mismo MySQL que ya administra Joaquín). Réplica o
  snapshot recién cuando el volumen lo justifique.
- **Plazo real: 3–4 semanas** para construirlo y probarlo. Por eso: **el primer cliente que cierra
  es el piloto del conector**, no se le promete en firme a dos organizaciones en paralelo.

> Consecuencia comercial: **la venta se cierra esta semana, la entrega completa cae en un mes.**
> El plazo que se comunica al cliente contempla eso desde el primer mensaje.

#### Los agentes de foto necesitan escribir — y eso todavía no existe

Los agentes "Cargá con una foto" de §3.1 son los que más venden, y **rompen la regla de solo
lectura**: cargar un comprobante es escribir en el sistema del cliente. Hay que resolverlo antes de
prometerlo, y la forma de resolverlo es también el argumento de confianza:

- **El agente nunca escribe en la base.** Lee la foto, extrae los datos y **deja un borrador
  pendiente de confirmación**. Una persona lo aprueba desde el portal y recién ahí se registra.
  M6 ya tiene el mecanismo de aprobación humana por llamada.
- **La escritura va por la aplicación, no por SQL**: un endpoint del propio sistema que valida como
  si lo hubiera cargado un usuario. Nada de `INSERT` directo contra tablas de producción.
- Esto suma trabajo sobre cada sistema del cliente (un endpoint de alta por tipo de comprobante).
  **Es el punto a dimensionar antes de comprometer plazo**, más que el conector de lectura.
- **Se vende como garantía, no como limitación:** *"el agente no toca nada solo; te deja el
  comprobante cargado y vos le das aceptar"*. Para quien desconfía de la IA, eso es exactamente lo
  que necesita escuchar.

**La conciliación, en cambio, es de solo lectura**: cruza el extracto o el papel contra lo que ya
está y señala la diferencia. No escribe nada. Es el agente de mayor valor y menor riesgo técnico de
toda la propuesta — **conviene que sea el primero que se construye y el primero que se muestra**.

#### El hallazgo que cambia la economía

**Toda la cartera es MySQL, en la misma cuenta de SmarterASP (`olvidatasoft-002`).** Los seis
sistemas en .NET 10 (Koi, Griffin, LabIPAC, RecoTrack, Eleven, Vino y Se Fue) comparten el *mismo
template*: 4 capas, EF Core 10, `MySql.EntityFrameworkCore`, Identity, Serilog, `AuditLog`. Los
legacy en MVC5 (Delicias, LumiTrack, Roaming, Las Latas, Saldo Claro) también son MySQL, y hasta los
WordPress lo son.

Es decir: **un único `IConectorTipo` de MySQL de solo lectura cubre la cartera entera.** Las 3–4
semanas no son costo del primer cliente: son inversión de plataforma que se amortiza en diez o más.
A partir del segundo cliente, el setup es definir vistas y configurar — horas, no semanas.

Esto habilita una decisión: **cerrar dos o tres clientes de prioridad 1 en simultáneo**, entregando
en orden, en vez de uno solo. El cuello no es el conector, es el tiempo de relevamiento por cliente.

#### Riesgo que hay que resolver antes de conectar nada

El relevamiento encontró **credenciales en claro versionadas en git** en varios repos:
connection strings y contraseñas SMTP en `appsettings.Production.json` (Koi, Griffin, LabIPAC,
RecoTrack, Eleven, Vino y Se Fue), API keys de terceros (QuickPass, Ayres), password del certificado
AFIP y `machineKey` en los `Web.config` de Delicias, credenciales de FTP/WebDeploy en archivos
`.pubxml.user`, y las claves de base en los `wp-config.php`.

No es parte de la oferta, pero **se toca el mismo material**: hay que rotar y migrar a secretos antes
de sumarle un usuario de solo lectura por cliente. Conviene hacerlo en la misma pasada.

### 3.3. Secuencia de 7 días

| Momento | Acción |
|---|---|
| Día 1 | Mensaje 1 (abajo). 4–5 contactos por día, personalizados. |
| Día 2 | Si no respondió: **no insistir**. |
| Día 3 | Si respondió sin fecha: "cuando tengas 15 minutos te lo muestro andando". |
| Demo | Mismo día: propuesta por escrito, vence en 7 días. |
| +3 días | Seguimiento 1: "¿pudiste verla? ¿alguna duda?" |
| +6 días | Seguimiento 2: "vence mañana, si querés arrancamos esta semana". |
| +7 días | Archivar. **No hay tercer mensaje.** |

### 3.4. Demo de 15 minutos

1. **(1 min)** Nombrar el dolor como dato, no como pregunta.
2. **(6 min) La foto.** *"Agarrá una factura de las que tenés ahí y sacale una foto."* Se carga en
   vivo, con el papel de él, delante de él. **Es toda la demo**: no hay argumento que gane contra
   verlo pasar. Y ahí mismo se muestra que queda *pendiente de que él lo apruebe* — el agente no
   toca nada solo.
3. **(4 min) La conciliación.** Sobre sus datos: acá está la diferencia del mes y de dónde sale.
4. **(4 min) Que configure una regla él, hablando.** Se abre *"Configurar reglas conversando"* y
   **se le pide que le cuente al agente cómo trabajan**, con sus palabras. El agente propone la
   regla, y él la aplica con un botón. *"Así vas a armar todos los que necesites, sin llamarme."*
5. **(1 min)** Precio, una sola vez: *"esto va adentro del mantenimiento que ya pagás"*.
6. **(1 min)** Cierre pasivo: *"¿Te sirve? Si querés arrancamos: la seña es el 50 % y me pongo a
   trabajar."* Y esperás.

> **Las dos reglas de la demo.**
> **El papel lo pone el cliente**, no vos: una factura preparada por Joaquín no prueba nada; la que
> él tiene arrugada sobre el escritorio, sí.
> **Y el que escribe la regla es él, no vos.** Si en la demo configurás vos, le estás mostrando un
> producto que no es el que va a comprar — y encima le enseñás a depender de vos. Que lo haga él,
> aunque salga torcido y haya que corregirlo ahí mismo: eso **es** la demo.

### 3.5. El cierre

- El sí se pide **una vez**, directo: *"¿Arrancamos?"*
- Anticipo 50 %, no negociable: *"Así arranca todo proyecto acá."*
- *"Lo pienso"* → *"¿Qué información te falta para decidir?"*
- *"Mandame el presupuesto"* (antes de la demo) → *"Prefiero mostrártelo funcionando primero, porque
  el precio depende de la complejidad real de tu caso."*

---

## 4. Copy listo para usar

**Propuesta de valor (1 línea):**
> Un equipo de agentes de IA que conoce tu rubro y se organiza como tu negocio — no un chatbot genérico.

**Hooks:**
1. "¿Cuántas consultas se te pierden por no llegar a contestar a tiempo?"
2. "Mientras vos atendés, el agente ya separó al que quiere comprar del que solo pregunta precio."
3. "Armé esto para mi propio estudio. ¿Te muestro en 15 minutos cómo quedaría en el tuyo?"

**Tres reglas de honestidad, porque de esto depende que la relación siga:**

1. **Todavía no hay nada armado para ese cliente.** No se dice "le sumé agentes a tu sistema" ni
   "armé un agente que hace X". Es un **ofrecimiento**: hay una plataforma andando y se propone
   aplicarla a su operación. Prometer como hecho lo que no está es la forma más rápida de perder un
   cliente que ya confía.
2. **Es un sistema aparte, no un módulo nuevo del que ya tienen.** Se conecta a su base de datos y
   trabaja con sus datos, pero es otra cosa, con su propio acceso. Decirlo desde el principio evita
   la confusión cuando vean una pantalla que no es la suya.
3. **Lo que se ofrece es mejorar la operatoria diaria**, no "inteligencia artificial". El cliente
   compra que su gente deje de hacer una tarea todos los días.

**Estructura del mensaje** (WhatsApp, nominal, nunca difusión): una o dos tareas diarias que le
sacarías de encima → *"es un sistema aparte que se conecta con el tuyo"* → *"vos definís cómo se
hace"* → pedido de 15 minutos para mostrarlo. **El precio no va en el primer mensaje**; el *"no vas a
pagar dos veces"* recién cuando pregunte, o en la demo.

> Cada mensaje lleva **el criterio de §8.2 adentro**: el gancho propio de ese cliente, la frase que
> evita lo que puede matar la venta, y la fecha del cliente —no una inventada por nosotros—.

**① Koi Dumplings** · *cierra contra el próximo cierre de mes · nada de inversores todavía*
> Hola [Nombre], soy Joaquín. Estuve armando un sistema nuevo —va aparte del Portal del Inversor,
> conectado a los mismos datos— para sacar trabajo manual del día a día. Para Koi lo veo en dos
> cosas: que a las facturas de proveedor les saquen una foto y queden cargadas con su concepto de
> gasto en vez de tipearlas una por una, y que cruce lo que informa el POS contra lo que quedó
> registrado, para decirte si falta plata y de qué turno. Las reglas las definís vos una vez y
> después corre solo. ¿Lo vemos 15 minutos antes del cierre de este mes?

*No mencionar el agente que le contesta a los inversores. Eso se muestra recién cuando esté probado
puertas adentro: un número mal contestado a alguien que puso plata no se arregla con una disculpa.*

**② Vino y Se Fue** · *cierra contra la próxima lista de proveedor · adelantarse al "eso ya lo tengo"*
> Hola [Nombre], soy Joaquín. Estoy poniendo en marcha un sistema nuevo —aparte del que usás, pero
> conectado a tu base— para sacarle horas a la operación diaria. Lo pensé para vos por lo de las
> listas: no hablo de leer el PDF del proveedor, eso ya lo hacés. Hablo de que te diga **qué precios
> de venta te quedaron por debajo del costo nuevo** apenas entra la lista, con el criterio que vos
> le marques una vez. Y de paso, que el remito se cargue con una foto, también el de consignación.
> ¿Te lo muestro 15 minutos cuando te llegue la próxima lista, con tu catálogo real?

**③ Eleven La Plata** · *cierra contra la facturación de excedentes · el técnico tiene que estar*
> Hola [Nombre], soy Joaquín. Armé un sistema nuevo —va aparte del de Eleven, conectado a sus datos—
> para sacar trabajo manual del día a día. Lo primero que pensé para ustedes: que el técnico le saque
> una foto al contador de la máquina y la lectura quede cargada sola, sin planilla ni tipeo después.
> Con eso mismo te avisa quién se pasó del tope de copias **antes** de que lo factures tarde. Vos
> definís las reglas una vez y después corre solo. ¿Tenés 15 minutos esta semana? Si podés, que esté
> [el técnico]: es el que lo va a usar todos los días y quiero que lo vea él.

**④ MariHogar** · *cierra contra un vencimiento de cheques · no toca la facturación*
> Hola [Nombre], soy Joaquín. Estoy armando un sistema nuevo, separado del tuyo pero conectado a tu
> base —**la facturación no se toca**, eso queda exactamente como está—. Para MariHogar lo veo en dos
> cosas: que a los cheques y a las facturas de proveedor les saquen una foto y queden cargados, y que
> cruce el extracto del banco contra los cheques y pagos del sistema para marcarte qué no coincide.
> Con eso mismo se arma la proyección de caja, que hoy la ves cuando ya pasó. ¿Te lo muestro 15
> minutos antes del próximo vencimiento?

**⑤ Showroom Griffin** · *cierra ANTES del ingreso de temporada*
> Hola [Nombre], soy Joaquín. Estoy poniendo en marcha un sistema nuevo —aparte del que usás,
> conectado a tu base— y te escribo ahora por el tema de la temporada. Lo veo para dos cosas: que el
> remito del proveedor se cargue con una foto, abierto por talle y color, en vez de a mano; y que te
> avise qué talle se está agotando de lo que más sale, para que no se te rompa la curva. Vos definís
> una vez cuándo querés que salte el aviso. ¿Lo vemos 15 minutos antes de que entre la temporada?

**⑥ LabIPAC** · *cierra contra el cierre mensual · decir "solo lectura" sin que lo pregunte*
> Hola [Nombre], soy Joaquín. Estoy armando un sistema nuevo —va aparte del portal, conectado a la
> misma base y **con acceso de solo lectura**, no modifica nada—. Lo pensé para lo que más plata les
> cuesta: las diferencias entre lo que llega de FABA y lo que quedó cargado, que cada mes es
> producción que no se factura. El sistema las cruza y te las señala. ¿Lo vemos 15 minutos antes del
> cierre del mes?

**⑦ Delicias Naturales** · *cierra con la RG 5616 del 01/12 · sin prometer fecha de entrega*
> Hola [Nombre], soy Joaquín. Me quedé pensando en algo que me comentaste: que todos los meses les da
> diferencia con la cuenta del banco y que sacar los balances les lleva un montón. Estoy poniendo en
> marcha un sistema nuevo —aparte del que usan, conectado a sus datos— y ese es justo el caso donde
> más sirve: definís una vez cómo concilian, y después cruza el extracto contra la caja y los pagos y
> te señala dónde está la diferencia. ¿Lo vemos 15 minutos esta semana?
>
> *(Segundo tema para la misma visita: el 01/12 arranca la obligación de informar la condición de IVA
> del receptor, RG 5616, y hay que activarla en su facturación.)*

*No comprometer fecha de entrega hasta resolver el tope de conexiones de su base (§8.2): un agente
conectándose puede agotarlas y voltearle el sistema que ya usa.*

**⑧ Ferretería La Platense** · *cierra junto con AFIP · sin fecha para AFIP*
> Hola [Nombre], soy Joaquín. Estoy armando un sistema nuevo —aparte del que usás, conectado a tu
> base— para sacar trabajo del día a día. Para la ferretería lo veo en dos cosas: que la factura del
> proveedor se cargue con una foto y actualice costos, en vez de pasar renglón por renglón; y que te
> avise qué productos de los que más salen están por quebrar stock, con el corte que vos definas.
> Aprovecho: si conseguís el certificado y el CUIT, dejamos andando la facturación electrónica en la
> misma pasada. ¿Tenés 15 minutos esta semana?

**El gimnasio** (cara a cara, no por WhatsApp — lo ves todas las semanas):
> Che [Nombre], te quiero mostrar algo que armé. Cargamos **tus reglas de programación** —cómo
> armás la semana, qué no mezclás nunca, cómo escalás por nivel, qué material tenés— y el sistema
> arma los WODs siguiendo **tu método** y los publica solo en Crossfy todos los días. Vos entrás, le
> das una mirada y cambiás lo que quieras. Y no publica nada sin tu aprobación hasta que vos decidas
> lo contrario. ¿Te muestro una semana armada con tu criterio?

**El gancho, decilo exactamente así:** *"no te programa las clases: aplica tu método todos los días
sin que te tengas que sentar a escribirlo."* Él sigue siendo el que sabe; el sistema es el que
ejecuta.

*Antes de esa charla:* **pedirle que te cuente cómo programa él.** Es lo único que falta —la API ya
está resuelta— y además es el mejor arranque posible de la conversación: a alguien que se toma en
serio su método, preguntarle por su método lo predispone. Sin sus reglas cargadas, el agente propone
entrenamientos genéricos y el primer WOD que le muestres lo descarta en diez segundos.

**⑨ Estancia Santa Rosa** · *cierra antes del próximo movimiento de hacienda*
> Hola [Nombre], soy Joaquín. Armé un sistema nuevo —va aparte del que usan, conectado a sus datos—
> para sacar trabajo manual del día a día. Para ustedes lo veo claro en una cosa: que le saquen una
> foto a la liquidación del consignatario y quede cargada la venta con todas las deducciones, renglón
> por renglón, en vez de pasar ese papel a mano. Y que después te diga qué quedó neto de verdad, que
> no es el precio de remate. ¿Lo vemos 15 minutos antes del próximo movimiento?

**~~DM frío~~ — descartado (§8.3).** La regla del estudio no habilita prospección fría para este
producto hasta que esté definido su ICP (`36:36`), y el diagnóstico vigente dice que el cuello es la
tasa de cierre, no el volumen. Con la cartera propia alcanza y sobra.

**Email (5 líneas):**
> Hola [Nombre],
> Te escribo porque en [negocio] seguro se pierde alguna consulta por no llegar a contestar a tiempo.
> Armé un agente de IA que se ocupa de eso, armado para tu rubro, no genérico.
> Te mando un video de un minuto mostrándolo en acción.
> Cualquier cosa me contestás directo por acá. Joaquín.

**Objeciones:**

| Dice | Respondés |
|---|---|
| **"¿Y si lee mal la factura?"** *(la que más va a aparecer)* | "Por eso no carga nada solo: te lo deja preparado y vos le das aceptar. Revisás en cinco segundos en vez de tipear cinco minutos." |
| "Es caro" | "Es el mismo mantenimiento que ya pagás, ahora mensual y con todo esto adentro. Lo único que se suma es el consumo, y tiene tope para que nunca te sorprenda." |
| "Ya uso ChatGPT" | "ChatGPT no está adentro de tu sistema. Este ve tus datos, te carga el comprobante y te dice dónde está la diferencia de tu caja." |
| "No confío en que se filtre mi data" | "Cada cliente tiene su espacio separado, las credenciales son tuyas y cifradas, y nada sale a un sistema externo sin que lo autorices." |
| "No tengo tiempo" | "Son 15 minutos y lo único que tenés que hacer es agarrar una factura tuya y sacarle una foto." |
| "Ahora no, más adelante" | "Dale. Igual te dejo andando la conciliación del mes que viene, así lo ves con tus números y después decidís." |

---

## 5. Vía B — contenido orgánico (días 1 a 14)

**El contenido no es el canal de venta de esta semana: es el respaldo.** Cuando un cliente de la
cartera recibe el WhatsApp del día 1 y entra a mirar el Instagram, tiene que encontrar un producto
andando, no un perfil muerto. Esa es toda la función del calendario.

**Ángulo: producto en producción**, ya no build-in-public. Hay URL pública y un caso real corriendo
en un estudio contable. Se muestra el sistema funcionando y se habla de resultados concretos.

**Regla de confidencialidad, sin excepción:** no se nombra a ningún cliente ni se muestra un solo dato
suyo. Se dice *"un estudio contable"*, *"una distribuidora"*. Toda captura o video sale de una
organización de prueba vacía.

**CTA:** *"Escribime"* / DM. El precio nunca va en el post: se da en la conversación.

### 5.1. El concepto de la campaña

> **Vos no le pedís cosas. Vos le enseñás cómo se hacen.**

Todo el contenido sale de la misma idea: **decidís una vez y a un nivel más alto**. En vez de
resolver lo mismo doscientas veces al año, definís las reglas que lo resuelven. El profe define su
método y salen los entrenamientos; el ferretero define cuándo reponer y salen los avisos; el de la
dietética define cómo concilia y aparece la diferencia señalada.

**Nunca se dice "la IA hace tu trabajo".** Se dice *"vos definís cómo se hace, el sistema lo hace
todos los días"*. Es la diferencia entre sonar a reemplazo —que cierra la puerta sola— y sonar a que
su criterio, que es lo que más valoran, por fin rinde más.

### 5.2. El eje educativo — chat suelto contra sistema

Es el contenido que más convierte, porque casi todos los clientes ya probaron ChatGPT y se quedaron
con la sensación de que "sirve para algunas cosas". Cuatro temas, uno por pieza:

1. **Qué es un prompt, y por qué una instrucción suelta no es una regla.** En un chat le explicás
   todo de cero cada vez. Una regla se escribe una vez, queda guardada y se aplica siempre, a todos,
   todos los días.
2. **Qué pasa cuando se usa sin contexto ni estructura.** No conoce tu negocio ni tus
   procedimientos, así que contesta genérico o inventa; cada empleado lo usa distinto y obtiene otra
   cosa; y no queda registro de nada: no sabés qué le preguntaron ni qué contestó.
3. **Cómo una instrucción se vuelve regla.** Se escribe, se guarda, se versiona, **se prueba antes de
   publicarse** y recién ahí entra en producción. Igual que un procedimiento de la empresa, no como
   un mensaje de WhatsApp.
4. **Dónde viven los datos — el más importante.** *La base de datos tiene que estar en un sistema, no
   puede vivir en el chat.* Pegar planillas en un chat es perder el control: el dato no se actualiza,
   no es confidencial, no es auditable, y mañana no está más. El sistema **se conecta** a la base que
   ya tenés y la lee donde vive, con permiso de solo lectura.

**Por qué conviene este eje:** posiciona a Joaquín como el que entiende el tema, le da al cliente un
motivo concreto por el que lo que ya probó no le funcionó, y deja el precio justificado antes de
hablar de precio.

### 5.3. La serie — «Se decide una vez» (`#SeDecideUnaVez`)

> **Documento propio de la campaña, con los guiones completos, las stories y el checklist de
> producción: [campania-se-decide-una-vez.md](campania-se-decide-una-vez.md).** Lo de acá abajo es el
> resumen para no tener que abrirlo.

**Hilo visual que la vuelve reconocible:** un gesto de sello —un check, un enter, una firma— que
dispara un timelapse de calendario donde los días se tildan solos. Va siempre en el mismo lugar:
apenas termina el gancho. Es el bumper de marca, se arma una vez y se reusa en todas las piezas.

| # | Formato | Tema | Gancho (0-2s) | Cámara |
|---|---|---|---|---|
| 1 | Reel | **El profe no deja de decidir** — abre la serie | *"¿Pensás que usar IA significa dejar de decidir vos? Es al revés."* | Sí |
| 2 | Carrusel | **Un prompt no es una regla** | *"Escribirle algo a ChatGPT no es lo mismo que tener una regla en tu negocio."* | No |
| 3 | Reel | **Las desventajas de usarlo suelto** | *"Si usás ChatGPT así nomás, tenés un empleado brillante con amnesia."* | Sí |
| 4 | Carrusel | **De instrucción a regla** — se escribe, se prueba, se aprueba, se aplica | *"¿Cómo pasa una idea tuya a ser algo que el sistema hace solo?"* | No |
| 5 | Reel | **Dónde viven tus datos** | *"Si pegás tu planilla en un chat, perdiste el control de ese dato."* | Sí |
| 6 | Reel | **Cierre: ya está andando** (sin nombrar al cliente) | *"Esto no es una idea. Ya lo usa un estudio contable, todos los días."* | Sí |

**Stories de acompañamiento:** encuesta *"¿le explicás tu negocio a ChatGPT cada vez que lo abrís?"* ·
objeción *"¿esto reemplaza a mi empleado?"* → *"No. Lo que no sigue es tener que explicarle el
procedimiento cada vez"* · objeción *"yo ya uso ChatGPT y me arreglo"* → *"Lo usás como un cuaderno
que se borra cada noche: te arreglás hoy, mañana escribís lo mismo"* · detrás de escena del portal ·
teaser de la pieza siguiente.

**Las analogías, que son lo que hace que cada pieza se explique sola:**

| Concepto | Cómo se dice |
|---|---|
| Prompt suelto vs. regla guardada | Explicarle a un empleado nuevo cada mañana **vs.** el manual de procedimientos colgado en la pared |
| Usar IA sin sistema | Un empleado brillante con amnesia: no importa cuánto sepa, mañana no se acuerda |
| Regla sin versionar ni probar | Alguien que decide sobre la marcha, sin que nadie revise antes de que impacte |
| Dato pegado en un chat | Queda fuera de tu control: no se actualiza, nadie audita quién lo usó, y mañana no está |
| El sistema conectado a la base | Va a leer donde el dato **ya vive**; no le pide que se mude a un chat |

**CTA de toda la serie: "Seguinos".** Sin venta directa y sin precio: el contenido construye demanda
para las semanas siguientes, la venta de esta semana sale por WhatsApp (§3).

**Producción:** las piezas 2 y 4, el bumper y todas las capturas salen **sin cámara** (screen
recording de una organización de prueba vacía). Las piezas 1, 3, 5 y 6 necesitan a Joaquín: sostienen
un argumento, y el texto solo no lo sostiene.

> **Ajuste antes de grabar la pieza 5:** la versión original de la analogía era "sacar la plata de la
> caja fuerte y dejarla en la vereda". Suena bien pero **exagera** —un dato pegado en un chat no queda
> expuesto a cualquiera—, y alguien con conocimiento técnico puede discutirlo y hacer perder
> credibilidad a toda la serie. El argumento honesto, que además es el verdadero, es el otro: el dato
> queda **desactualizado, sin control y sin rastro**. Con eso alcanza.

**Checklist antes de grabar:** organización de prueba vacía · ningún nombre, logo ni dato de cliente
real (tampoco en la pieza 6) · cada afirmación funcional verificada contra el repo, no inventada ·
nada presentado como "la IA hace tu trabajo" · handle en todas las piezas.

**Hashtags base:** `#pymeargentina #gestioncomercial #inteligenciaartificial #agentesdeia
#emprendedoresargentina #softwareparapymes #buildinpublic #olvidatasoft`

---

## 6. Pauta paga: todavía no

Con ciclo de venta de 7–10 días y una lista chica, el 1 a 1 rinde más que aprender a optimizar una
campaña en dos semanas. **Recién el día 14**, si el orgánico se saturó y hay caja: Meta Ads,
USD 3–5/día, objetivo "mensajes", audiencia local de 5–10 km por rubro, 5–7 días de prueba antes de
escalar nada.

---

## 7. Precondiciones antes de mandar el primer mensaje

- [x] ~~Ejecutar el deploy a SmarterASP~~ — **hecho**: https://agentes.olvidata.com.ar/ en producción.
- [x] ~~Confirmar el número de WhatsApp~~ — Joaquín tiene el WhatsApp de todos sus clientes.
      El contacto es **directo y nominal**, no un CTA de DM masivo.
- [ ] Confirmar **AlwaysRunning (PA-07)**: sin él el sitio se duerme y las tareas programadas se
      atrasan. Es lo primero que se nota en un cliente pagando.
- [ ] Grabar el screen recording del portal **en producción** (login → organización → menú por
      etapas → chat del agente). Único activo de comunicación imprescindible.
- [ ] Correr una ronda de QA acotada al flujo que se va a mostrar, no al sistema entero.
- [ ] Definir el alcance técnico del conector a base de datos (§3.2) antes de prometer plazo.

---

## 8. Lo que no se hace

- **No** grabar ni publicar nada que muestre el backoffice con datos de un cliente real. Para todo
  video o captura se usa una organización de prueba vacía.
- **No** vender el portal multi-tenant como producto terminado.
- **No** prometer integraciones automáticas: no hay conectores concretos.
- **No** mandar precio sin demo, salvo pedido explícito.
- **No** fabricar escasez inventada. La única urgencia real es el vencimiento de la propuesta.
- **No** hacer un tercer follow-up. Eso es presión, no venta.
- **No** recontactar la lista vieja con el pitch de productos dados de baja.
- **No** cargar documentación real de la Tesorería en el portal, ni ofrecerle nada, antes de la
  consulta legal y de la autorización de Seguridad Informática.

---

## 8.1. Criterios de decisión

Las reglas para resolver en el momento lo que vaya apareciendo, sin volver a pensarlo cada vez. Es lo
mismo que se le vende al cliente: **se decide una vez, a un nivel más alto.**

**A quién le hablo primero.** Gana el que tenga un dolor que se explique en una frase y se demuestre
en dos minutos con un papel suyo. Ese es el orden, no el tamaño del cliente ni lo que factura.

**Cuánto insisto.** Mensaje, y si no contesta en 48 h no se reenvía nada. Después de la propuesta:
dos seguimientos y se archiva. **Nunca un tercero.** Un cliente de cartera que no contesta no es un
lead perdido: es alguien ocupado al que se le vuelve a escribir dentro de dos meses, no en tres días.

**Cuándo bajo el precio.** Nunca por pedido. El setup ya viene con descuento por ser cliente activo,
y el abono cubre el mantenimiento que ya paga. Si el precio frena la venta, se achica el alcance
—menos agentes configurados, sin conector— pero **no se toca el número**. Bajarlo con uno obliga a
bajarlo con todos, y son diecinueve.

**El anticipo del 50 % no se negocia.** Sin anticipo no se empieza. La única excepción es que el
cliente tenga una fecha de renovación cercana y prefiera cobrarlo todo junto ahí, que es a favor
nuestro.

**Cuándo digo que no.** Si el cliente quiere que el agente **escriba solo** en su base sin
aprobación, la respuesta es no, aunque pague. Si quiere integraciones con terceros (bancos, Mercado
Pago, ARCA), no entra en este precio y se cotiza aparte. Si pide algo que no existe, se dice que no
existe y cuándo podría existir: nunca "sí, lo tiene".

**Qué prometo de plazo.** Dos semanas para lo que ya funciona; un mes cuando hay conector de por
medio. Ante la duda, el plazo largo: un cliente de cartera perdona un mes, no perdona un incumplido.

**Si entran tres «sí» la misma semana.** Se aceptan los tres y se entregan en orden, avisándolo desde
el principio. El conector y la conciliación se construyen una sola vez para toda la cartera, así que
el cuello es el relevamiento, no la plataforma. Lo que no se hace es frenar a dos para no demorar a
uno.

**Qué construyo primero, siempre.** Lo que sea de solo lectura antes que lo que escriba. Da el mayor
valor con el menor riesgo, y no depende de resolver la vía de escritura.

**Cuándo freno una venta por razones técnicas.** Si el cliente es SCALE con upsells —el abono le
bajaría la facturación—, no se le ofrece el esquema parejo hasta cotizarlo aparte. Si el agente
tuviera que tocar datos que no podemos leer con permiso de solo lectura, tampoco.

**Qué muestro en público.** Ningún dato ni nombre de un cliente real, sin excepción, ni siquiera con
su permiso verbal. Toda captura sale de una organización de prueba vacía. Un cliente que se entera
por Instagram de que sus datos aparecieron en un video es un cliente perdido y un problema legal.

**Cómo hablo del producto.** Se ofrece mejorar la operatoria diaria, es un sistema aparte conectado a
su base, y **vos definís las reglas**. Nunca "la IA hace tu trabajo", nunca "ya te lo armé" si no
está armado.

**Qué mido.** Un anticipo acreditado. No mensajes enviados, no reuniones, no seguidores. Si al día 7
no hay ninguno, el problema está en la oferta o en a quién se la estoy ofreciendo — no en el volumen
de mensajes, y mandar más no lo arregla.

## 8.2. El criterio de cada cliente

Para cada uno: **con qué se abre**, **qué puede matar la venta** y **contra qué fecha se cierra**.
Cerrar contra una fecha propia del cliente vale más que cualquier vencimiento que inventemos: no hay
que fabricar urgencia donde el calendario ya la pone.

**① Koi Dumplings** — *Abre:* el cierre de mes y las preguntas de los inversores.
*Cuidado:* hay inversores mirando. **No exponer el agente a los inversores hasta que esté probado
puertas adentro**: un número mal contestado a alguien que puso plata no se arregla con una
disculpa. Se arranca por uso interno. *Cierra:* contra el próximo cierre mensual.

**② Vino y Se Fue** — *Abre:* la lista nueva del proveedor y los precios que quedaron atrasados.
*Cuidado:* **ya parsea catálogos**, así que puede contestar "eso ya lo tengo". La diferencia no es
leer el PDF: es decirte qué precio de venta quedó por debajo del costo nuevo. Hay que decirlo así
desde el primer mensaje. *Cierra:* contra la próxima lista que le mande un proveedor.

**③ Eleven La Plata** — *Abre:* la foto del contador.
*Cuidado:* **el que saca la foto es el técnico, no el dueño.** Si el técnico no lo adopta, el agente
no se usa y la renovación se cae al año. Que el técnico esté en la demo, o al menos que el dueño lo
consulte antes de firmar. *Cierra:* contra el próximo ciclo de facturación de excedentes.

**④ MariHogar** — *Abre:* "¿llego a fin de mes?" con cheques y cuotas.
*Cuidado:* tiene **AFIP emitiendo de verdad**. Dejar clarísimo que el sistema nuevo **no toca la
facturación**; si lo asocia con riesgo fiscal, se cierra la puerta y con razón. *Cierra:* contra un
vencimiento de cheques que ya tenga en agenda.

**⑤ Showroom Griffin** — *Abre:* la curva de talles rota.
*Cuidado:* es estacional. Ofrecerlo con la temporada ya cargada llega tarde y el valor se ve recién
el año que viene. *Cierra:* **antes del ingreso de temporada**, no después.

**⑥ LabIPAC** — *Abre:* las prácticas que no concilian contra FABA, que es facturación perdida todos
los meses. *Cuidado:* son **datos de salud**. Decir sin que lo pregunte que el acceso es de solo
lectura y que nada sale del sistema sin autorización. *Cierra:* contra el cierre mensual de
producción.

**⑦ Delicias Naturales** — *Abre:* la diferencia con el banco, que lo dijo él mismo.
*Cuidado técnico serio:* su base tiene **tope de conexiones del hosting** (por eso hay dos usuarios
con round-robin). Un agente conectándose puede agotarlas y **voltearle el sistema que ya usa**. Hay
que resolver la conexión antes de prometer fecha. *Cierra:* la RG 5616 del 01/12 ya pone la fecha.

**⑧ Ferretería La Platense** — *Abre:* la reposición de los productos clase A.
*Cuidado:* el código de AFIP está portado pero **sin certificado**. Se puede ofrecer activarlo, pero
depende de que el cliente consiga el `.p12` y el CUIT: **no prometer facturación con fecha**.
*Cierra:* junto con la activación de AFIP, que es lo que más quiere.

**⑨ Estancia Santa Rosa** — *Abre:* la liquidación del consignatario cargada por foto.
*Cuidado:* es estacional y depende de los remates. Fuera de temporada el dolor no se siente.
*Cierra:* antes del próximo movimiento de hacienda.

**⑩ RecoTrack** — *Abre:* el parte diario y los desvíos por chofer.
*Cuidado:* ya tiene envíos automáticos por cron, así que **va a notar enseguida si algo se atrasa**.
No ofrecerlo hasta tener PA-07 (AlwaysRunning) confirmado. *Cierra:* sin fecha natural; queda para
después de los primeros tres.

**⑪-⑭ LumiTrack, PI Apartments, Las Latas, Saldo Claro** — no esta semana. LumiTrack es compra
pública; los de alquileres son legacy con ticket chico; Saldo Claro es personal y no aplica. Se los
contacta cuando los primeros estén entregados y haya caso propio para mostrar.

**El gimnasio** — *Abre:* preguntarle cómo programa él. *Cuidado:* no paga mantenimiento, así que el
esquema de la cartera no aplica y el precio está sin definir. *Cierra:* recién cuando su método esté
relevado; antes no hay nada que mostrar que no sea genérico.

**La Tesorería** — *Abre:* nada, todavía. *Cuidado:* la consulta legal va **antes** de cualquier
insinuación de oferta. *Cierra:* por procedimiento de compra pública, en meses.

**Contadores BMA** — no se le vende esta oferta: **es el caso de referencia**. Su criterio es otro —
que lo que está andando siga andando, porque es lo que se muestra en todas las demás demos.

---

## 8.3. Lo que choca con las reglas escritas del estudio

Revisión del 2026-09-22 contra `.github/instructions/`, los agentes del estudio y `PLAN-IMPLEMENTACION.md`.
**Esto no son opiniones: son reglas ya escritas que este plan estaba contradiciendo.**

| Choque | Regla | Qué hay que hacer |
|---|---|---|
| **El precio no dice "+ IVA"** | Todos los precios del catálogo son + IVA (`27:142`) | USD 1.300 + IVA y USD 90/mes + IVA. Decirlo en la propuesta, no en la demo |
| **Prospección fría a los 13 negocios** | No hay prospección fría habilitada para AI Agents hasta que se defina el ICP de ese segmento (`36:36`) | **Se saca del plan.** La cartera propia alcanza y sobra |
| **La campaña habla de tecnología** | "No publicar sobre tecnología: publicar sobre la vida del dueño sin el problema; pain-first en la primera línea" (`cm:75-76`) | Ver la corrección en el doc de campaña: el eje educativo se mantiene, pero **cada pieza abre por el dolor del dueño**, no por el concepto técnico |
| **Reveals del backoffice** | El backoffice de Olvidata, `docs/calibracion/` y los parámetros de estimación **nunca se muestran** (`PLAN-IMPLEMENTACION.md:186-196`) | Los reveals son solo de la pantalla del cliente. Nada del lado Olvidata |
| **Ofrecerle AFIP a La Platense en pantalla** | En contenido no se muestra su facturación/AFIP, que está bloqueada (`cm:50`) | El ofrecimiento 1 a 1 sigue; **en redes no aparece** |
| **"El agente hace X"** en rubros regulados | Las salidas son asistencia y no reemplazan el juicio profesional; en rubros regulados todo documento es **borrador para el matriculado** (`legal/BORRADOR:57-59`) | Vale para LabIPAC, Delicias y BMA: se dice "borrador", nunca "resuelto" |

**Reglas que el plan ya venía cumpliendo, y conviene no perder:** anticipo del 50 % innegociable ·
cierre pasivo, sin pedir fecha ni fabricar urgencia · dos seguimientos y se archiva · propuesta con
vencimiento a 7 días · la promo se menciona **una sola vez** · Instagram como canal de demanda con
CTA "Seguinos", nunca venta directa · primera persona singular siempre, nunca "nosotros" · ninguna
pantalla inventada.

> **El diagnóstico vigente del estudio dice que el cuello de botella es la tasa de cierre, no el
> volumen: nunca más de 8–10 contactos nuevos por semana** (`olvidata-ceo.md:181-182`). Este plan
> contacta tres el día 1 y tres el día 5. Está en regla, y conviene que siga así aunque tiente
> escribirle a los diecinueve el mismo día.

## 8.4. Criterios que faltaban

**Precio y contrato**

- **Todo va + IVA.** USD 1.300 de setup y USD 90/mes, más IVA.
- **Grandfathering, y por escrito.** El que cierra ahora mantiene los USD 90/mes mientras siga
  activo. Es la regla que ya rige para AI Agents y hay que aplicarla acá: sin ella, en un año hay que
  subirle el precio a la misma cartera a la que hoy se le dijo "no te cobro dos veces".
- **Si pide comprar el código:** existe y tiene precio — USD 6.000 por rubro, con contrato de
  licencia sin reventa. Es decisión comercial por cliente, nunca se ofrece primero.
- **Si se atrasa un mes:** aviso, y a los 30 días se cortan los agentes. **El sistema base que ya
  tenía no se toca nunca**: una cosa es suspender el servicio nuevo y otra dejarlo sin trabajar.
- **Si se da de baja:** vuelve a su plan de mantenimiento anual anterior, al precio de lista vigente.
  Hay que decírselo antes de que lo pregunte; es la primera cuenta que va a hacer.
- **Sin permanencia.** Coherente con el resto del catálogo. Lo que se lleva si se va: su sistema
  intacto y sus datos; lo que pierde es el acceso a los agentes.

**El riesgo de precio, que es el más grande**

> **Atenuado por la decisión del 2026-09-23** (el cliente configura solo, ver §3.2). El riesgo era
> que USD 90/mes planos cubrieran seis a nueve agentes **a medida**, que según la tabla de tiers del
> 21/09 valen entre USD 1.000 y 9.000 de setup y entre 40 y 150 por mes cada uno. **Si los configura
> el cliente, eso ya no es trabajo de Joaquín y el abono deja de ser un regalo**: pasa a ser el
> precio del acceso, la conexión a la base y el acompañamiento, que es otra cosa.
>
> **Lo que queda vivo del riesgo, y hay que resolver igual:**
>
> - **El agente a medida sigue existiendo.** Cuando un cliente pida uno que el configurador no pueda
>   armar solo —reglas propias, un conector nuevo, subagentes—, **eso se cotiza aparte** con los
>   tiers ya definidos. El abono cubre lo que el cliente puede hacer por su cuenta; lo que requiera
>   horas de Joaquín, no.
> - **El grandfathering se limita a 24 meses**, no "de por vida". Con el producto recién entrando al
>   mercado, atarse para siempre a un precio de lanzamiento es apostar a que nada cambie en cinco
>   años.
> - **El consumo de IA sube**, porque configurar conversando también gasta tokens. El crédito de USD
>   9/mes se calculó para uso, no para uso más configuración. Hay que mirarlo en el primer cliente.

**Venta**

- **Pedir un referido siempre**, en el cierre y también cuando dicen que no. Es el canal más barato y
  el plan no lo tenía. Una sola frase: *"¿conocés a alguien a quien le sirva esto?"*.
- **A los seis meses, el agente a medida.** La cartera migrada queda con abono plano y sin motivo
  para crecer. La expansión vive ahí, y hay que agendarla desde el día que se firma.

**El configurador pasa a ser el producto — y hoy le falta una pieza**

Si el cliente configura solo, **la calidad del agente configurador es el negocio**. No es una función
más: es de lo que depende que el abono se sostenga.

**Lo que ya hace** (verificado en `HerramientasConfigurador.cs`): lee la estructura de la empresa, las
reglas vigentes y las sugerencias; propone **reglas** (nueva, cambio, desactivar, activar) y
**instructivos**; y deja cada propuesta como tarjeta para aplicar, editar o descartar.

> **Lo que no hace: crear agentes.** El configurador propone reglas e instructivos. "Agente" aparece
> únicamente como *alcance* de una regla —una regla que se aplica a tal agente—, nunca como algo que
> el cliente pueda crear conversando. **Si el modelo es que el cliente arma sus propios agentes, esa
> pieza falta y hoy vuelve a caer en Joaquín.** Es la precondición más importante del plan: sin
> ella, "agentes ilimitados configurados por el cliente" no es cierto todavía.

**Qué necesita el configurador para sostener el modelo:**

1. **Proponer agentes**, no solo reglas: que el cliente pueda decir *"necesito algo que revise los
   remitos"* y salga un agente configurado, con sus herramientas y su alcance.
2. **Arrancar con ejemplos del rubro.** Frente a una pantalla en blanco, un dueño de pyme no sabe qué
   pedir. Tiene que ofrecer *"esto es lo que suelen necesitar los negocios como el tuyo"* y que él
   elija y corrija, en vez de inventar desde cero.
3. **Repreguntar cuando falta información**, en vez de proponer una regla genérica con lo poco que
   le dijeron. Una regla floja aplicada es peor que ninguna: el agente responde mal y la culpa se la
   lleva el producto.
4. **Explicar el efecto antes de aplicar**: *"si aplicás esto, el agente va a hacer tal cosa en tal
   caso"*. Sin eso, el cliente aprueba tarjetas sin entender qué cambió.
5. **Revisar lo que ya está configurado** y avisar cuando dos reglas se contradicen.

> Mejorar el configurador **pasa por el evaluador** (`IVersionadoService`): ningún prompt se publica
> sin evaluación aprobada. Es lento a propósito, y conviene empezar antes de que haya diecinueve
> clientes dependiendo de él.

**El riesgo nuevo que abre el autoservicio: la adopción**

Si el cliente configura solo, **puede configurar mal** — y cuando el agente responda mal, la culpa se
la va a llevar el producto, no la regla que él escribió. Con autoservicio, la capacitación deja de
ser un extra de la entrega y **pasa a ser el producto**. Tres criterios que salen de ahí:

- **No se entrega un acceso y chau.** Se entrega una sesión donde el cliente configura **su primera
  regla real, delante de Joaquín**, sobre un caso suyo. Si no sale de esa sesión con algo andando,
  no se va a usar nunca.
- **Quién es el Director importa.** El configurador es rol de Director, así que hay que identificar
  en cada cliente a **la persona concreta** que va a definir las reglas — y que tenga tiempo y ganas.
  Si es alguien que no entra nunca al sistema, la venta se cae a los dos meses aunque esté paga.
- **Se mide la adopción, no la facturación** (§8.5): cuántas reglas creó el cliente por su cuenta el
  primer mes. Cero reglas nuevas es la señal temprana de que se va a dar de baja.

**Lo que no existe escrito y hay que definir antes de prometerlo**

1. **Garantía post-entrega**: no hay plazo de corrección sin cargo, ni tiempo de respuesta por plan.
   Si un cliente pregunta "¿y si falla?", hoy no hay respuesta escrita.
2. **Política de mora** para clientes de catálogo.
3. **Autorización de imagen y logo**: no existe modelo escrito ni registro de quién autorizó.
4. **Qué del portal se puede mostrar en público**: existe la regla §9 como principio, pero nadie la
   bajó nunca a contenido audiovisual. Hay que hacerlo antes de grabar.
5. **Contrato de servicios** para clientes de catálogo: el único documento legal es el borrador de
   licencia del producto, y dice "requiere abogado".

## 8.5. Qué se mide mes a mes

Más allá del anticipo de la primera semana:

- **MRR del esquema nuevo contra lo que reemplazó.** ¿Los +USD 11.500/año se sostienen o se caen por
  bajas y downgrades?
- **Consumo real de IA contra el crédito de USD 9.** Valida si el tope alcanza o si el excedente se
  come el margen.
- **Adopción real:** cuántos borradores de "foto → carga" se aprueban contra cuántos el cliente
  ignora mientras sigue tipeando a mano. Mide si el producto **se usa**, no si se factura.
- **Horas de relevamiento por cliente nuevo.** Valida la promesa de "horas, no semanas" del segundo
  cliente en adelante.
- **Referidos generados** en esta ronda.

---

## 9. Decisiones abiertas para Joaquín

1. **Los tres del día 1.** Recomendación: **Delicias Naturales** (la conciliación bancaria es el
   dolor más nítido y declarado de la cartera), **Estancia Santa Rosa** (la liquidación del
   consignatario cargada por foto) y **Eleven** (la foto del contador). Los tres tienen un agente que
   se explica en una frase y se demuestra en dos minutos.
   **Y el gimnasio, que no cuesta nada preguntar**: lo ves esta semana igual.
2. **¿Qué se construye primero?** Recomendación: **la conciliación**, que es de solo lectura y no
   depende de resolver la escritura (§3.2.3). Da el mayor valor con el menor riesgo técnico.
3. **Cuáles de la cartera son SCALE con upsells** — a esos el esquema parejo les baja la facturación
   (−310/año) y hay que cotizarlos aparte. *Falta el mapeo cliente → plan.*
4. **El alcance de "ilimitado"**: ¿el setup incluye la red inicial completa (§3.1) o un solo agente?
   Depende de armar las plantillas por rubro una vez, no por cliente.
5. **La vía de escritura** para los agentes de foto: hay que dimensionar el endpoint de alta por tipo
   de comprobante en cada sistema. Es lo que define el plazo real.
6. **Rotación de credenciales** (§3.2.3): ¿entra en esta pasada o va aparte?
7. **El gimnasio:** ¿qué precio? No paga mantenimiento, así que el esquema de la cartera no aplica.
   *(La API ya está confirmada y en uso; sólo falta probar el alta de clases con token de dueño.)*
8. **¿Se abre el rubro `gimnasio` como producto replicable?** Es la decisión de más alcance de
   todo el plan: deja de ser un cliente y pasa a ser un mercado.
9. **La Tesorería:** ¿se puede vender siendo empleado? (consulta legal). ¿Jira y Confluence son Cloud
   o Data Center? Y según eso, ¿venta como proveedor o propuesta como proyecto interno?

---

## 10. Los próximos siete días

| Día | Qué pasa |
|---|---|
| 1 | Grabar el video de la foto cargándose. WhatsApp nominal a los tres del día 1. **En el gimnasio: preguntarle cómo programa él.** |
| 2 | Confirmar AlwaysRunning. Responder y agendar las demos. **Pedir la consulta al abogado por las incompatibilidades** (Tesorería): la venta es de ciclo largo, pero esto bloquea toda la vía, no depende de nadie más y tarda. Arranca ahora aunque se cierre en meses. |
| 3–4 | Demos de 15 minutos, **con un papel del cliente**. Propuesta el mismo día, vence en 7. |
| 5 | Contactar al segundo grupo: Koi, MariHogar, Vino y Se Fue. |
| 6–7 | Seguimiento 1. Arrancar la conciliación con el primero que señó. |

**El indicador de la semana no son los mensajes enviados ni las publicaciones: es un anticipo del
50 % acreditado.**
