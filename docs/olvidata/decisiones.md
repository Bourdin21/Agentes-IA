# Decisiones abiertas

Preguntas que esperan una definición de Joaquín. Estaban dispersas como notas al pie dentro del
archivo de cada agente, donde nadie las vuelve a leer: una frase "sin validar" en el CM, un "falta
confirmar" en el CEO, un reparo sobre un caso en BotPublicitario. Juntas se pueden despachar de una
sentada.

**Cómo se usa:** cada decisión tiene un ID estable (`DEC-NNN`). Cuando se resuelve, se mueve a
"Resueltas" con la fecha y la decisión textual, y el archivo que la citaba se actualiza. No se borra:
el historial de por qué algo se decidió así vale tanto como la decisión.

## Abiertas


### DEC-002 · El caso del frente Landing tiene el formulario roto
- **Qué:** el formulario del único caso de webs dio **error 500** en producción después de la
  migración de dominio, y el frente quedó con "reparos sin resolver".
- **Dónde:** `BotPublicitario/CAMPANAS-POR-FRENTE.md` y `plan_contenido_instagram_oct-dic2026.md`.
- **Por qué importa:** Landing se vende con ese caso. Mientras el formulario falle, mostrarlo es
  exponer un sistema roto; y es el único cliente real del frente (Diercas, ver `casos.md`).
- **Lo que hace falta:** confirmar si el 500 sigue, arreglarlo, y recién entonces habilitar el caso.






### DEC-008 · El frente de dos clientes está inferido, no confirmado
- **Qué:** ESCABA y PiApartments tienen frente **Build** asignado por inferencia del tipo de sistema.
- **Dónde:** `datos-manuales.yml`, marcados con un comentario.
- **Por qué importa:** poco, hoy. Importará cuando se mida "cierres por frente" (ver `metricas.md`).


## Resueltas

### DEC-004 · El ticket real es USD 294 y no 426 — **resuelto 2026-10-16**
- **Decisión de Joaquín:** *"el real es más bajo porque son clientes antiguos que quedaron con precio
  viejo"*.
- **Qué significa:** no es un error de carga ni una pérdida — es la política de no aplicar las subas
  retroactivamente a clientes ya firmados (precedente 2026-07-24, mismo criterio que el
  grandfathering de COM-016). El promedio de la base mezcla precios de tres rondas distintas.
- **Qué se cambió:** `clientes.md` ahora calcula también **el mismo parque a lista vigente**: USD
  6.480/año, ticket **USD 498** — es decir, por encima de los 426 de planificación, no por debajo. La
  diferencia de USD 2.660/año contra lo contratado es lo que se decidió no cobrarle a la base.
- **Regla que queda:** para proyectar clientes **nuevos** se usa la lista vigente (498); el promedio
  de la base (294) sirve para medir la cartera actual, no para planificar. Mezclarlos era lo que hacía
  parecer descalibrado al plan. El breakeven quedó recalculado en `olvidata-ceo.md`: **29 clientes** a
  lista vigente, contra los 48 que harían falta si el ticket real fuera el de la base.

### DEC-005 · Dos clientes activos con recurrente en 0 — **resuelto 2026-10-16**
- **Decisión de Joaquín:** *"Contadores BMA y LABIPAC están en 0 porque son sistemas regalados"*.
- **Qué se cambió:** los tres sistemas (BMA Front web, BMA Conversor, LABIPAC) están marcados como
  `regalados` en `datos-manuales.yml`. `clientes.md` los cuenta aparte — "16 activos (13 con plan pago
  + 3 regalados)" — y ya no los mete en el ticket promedio ni los reporta como dato faltante.
- **Lo que sigue vivo:** si mañana aparece otro cliente en 0 sin estar marcado, el archivo lo señala
  como "falta cargar el plan o falta marcarlo". El control queda, el falso positivo no.

### DEC-006 · La renovación de ESCABA figuraba vencida — **resuelto 2026-10-16**
- **Decisión de Joaquín:** *"ya se cobró, y el plan anual es de USD 240 en 4 pagos trimestrales"*.
- **Hallazgo que destapó:** **el CRM no modela periodicidad de pago.** Tiene `TicketAnualUsd` y una
  sola `FechaProximaRenovacion`, así que un plan trimestral se va a ver como una renovación anual
  vencida cada tres meses — y el aviso de renovación va a saltar cuatro veces por año sin motivo.
- **Qué se cambió:** el dato quedó en `datos-manuales.yml` como corrección pendiente, y `clientes.md`
  lo imprime como aviso para que no se pierda mientras el CRM no se actualice.
- **Pendiente operativo (no es una decisión, es una carga):** poner 240 como anual y mover la fecha a
  2027-01-02 en el CRM. Y decidir, cuando haya tiempo, si el CRM necesita un campo de periodicidad —
  con un solo cliente trimestral, el workaround alcanza.

### DEC-003 · La lista post-promo 2027 — **resuelto 2026-10-16**
- **Decisión de Joaquín:** *"la del CEO está confirmada"* — la lista 2027 es **promo × 1,20**,
  confirmada el 2026-09-19.
- **Qué se cambió:** `olvidata-marketing.md` era el desactualizado y se corrigió; `precios.md` dejó de
  decir "no aplicar hasta que Joaquín la confirme" y ahora dice que está confirmada, con la aclaración
  de que aplica a clientes nuevos (el que cerró con la promo mantiene su precio, COM-016).

### DEC-007 · Los frentes AI Agents y Chatbots sí tienen caso — **resuelto 2026-10-16**
- **Decisión de Joaquín:** *"sí tienen: Contadores BMA y CRM Olvidata"*.
- **Qué se cambió:** `casos.md` suma las dos fichas. **Contadores BMA** es el caso de AI Agents (con
  la salvedad de que sus dos sistemas son regalados, así que no sirve para hablar de recurrente) y **el
  CRM de Olvidata** es el de Chatbots: el bot de ventas está en vivo desde 2026-09-14, contesta en
  WhatsApp y categoriza, con más de 10.000 contactos reales detrás. Se presenta como producto propio
  funcionando —"el que lo vende lo usa"—, nunca como un cliente.
- **Lo que no cambia:** sigue prohibido afirmar tasas de conversión del bot, que no están medidas, y
  decir que resuelve sin humano (contesta y deriva).
- **Queda un solo frente sin ficha:** Landing, cuyo cliente real es Diercas y arrastra DEC-002.

### DEC-001 · La frase del Chatbot — **resuelto 2026-10-16**
- **Decisión de Joaquín:** confirmarla, y mejorarla si se podía.
- **Vigente:** **"Contesta a las 3 de la madrugada. A las 8 sabés quién quiere comprar."**
- **Qué se mejoró:** la original —"Te contesta a las 3 de la mañana y a la mañana ves quién quiere
  comprar"— usaba *mañana* con dos sentidos distintos en la misma frase (la madrugada y el comienzo del
  día), que es justo donde un hook pierde el golpe. La versión nueva fija dos horas concretas, y la
  decisión sigue siendo del dueño ("sabés quién quiere comprar"), no del bot.
- **Lo que se mantiene prohibido:** "IA conversacional", que resuelva sin humano, y cualquier tasa de
  conversión del bot propio.

### DEC-009 · Setup + recurrente en todo el plan — **resuelto 2026-10-16**
- **Decisión de Joaquín:** *"tener en cuenta el precio de setup + recurrente en todo el plan de
  Olvidata"*.
- **Qué se cambió:** `metricas.md` tiene una sección propia con las dos mitades (no recurrente
  acumulado USD 7.818 contra recurrente contratado USD 3.820/año — hoy el setup es la mayor parte de
  lo que entra), y la columna mensual pasó a llamarse "no recurrente del mes". `olvidata-ceo.md`
  arranca la matemática del hito declarando que el plan se piensa con las dos.
- **La distinción que queda escrita:** el **umbral del Ministerio se mide solo con el recurrente**,
  porque la decisión es sostener el ingreso sin vender nada nuevo ese mes. Si el setup cuenta para el
  umbral, el mes que no se cierra un cliente el sueldo desaparece. Para capacidad de pago de un
  proyecto o caja del año, van los dos.
- **De paso, la aritmética que molestaba:** 35 era el breakeven y 43 el objetivo con colchón; el texto
  no lo decía y parecía un error. Ahora la tabla muestra el breakeven con los tres tickets posibles.


### DEC-000 · MARCA.md § 0c prohibía una frase que el CEO tenía habilitada — **resuelto 2026-10-15**
- **Era:** § 0c prohibía toda la familia de "la IA hace tu trabajo", y con eso vetaba la promesa que
  `olvidata-ceo.md` tiene vigente desde el 2026-10-11 ("que trabajen más las máquinas, entendiendo la
  lógica del usuario" / "jubilar a la gente de su trabajo cotidiano").
- **Decisión de Joaquín:** prevalece el CEO. Se prohíbe la frase que suena a reemplazo de la persona;
  se habilita la que dice que el trabajo cotidiano se jubila. § 0c reescrito con la distinción
  explícita y la nota de cambio.
- **Por qué vivió semanas sin detectarse:** los dos archivos estaban en repos distintos y ningún
  chequeo podía verlos juntos. Por eso el mismo día se movió `MARCA.md` a
  `docs/olvidata/marca/MARCA.md` y se dejó un puntero en BotPublicitario.
