# Decisiones abiertas

Preguntas que esperan una definición de Joaquín. Estaban dispersas como notas al pie dentro del
archivo de cada agente, donde nadie las vuelve a leer: una frase "sin validar" en el CM, un "falta
confirmar" en el CEO, un reparo sobre un caso en BotPublicitario. Juntas se pueden despachar de una
sentada.

**Cómo se usa:** cada decisión tiene un ID estable (`DEC-NNN`). Cuando se resuelve, se mueve a
"Resueltas" con la fecha y la decisión textual, y el archivo que la citaba se actualiza. No se borra:
el historial de por qué algo se decidió así vale tanto como la decisión.

## Abiertas

### DEC-001 · La frase de oferta del Chatbot no está validada
- **Qué:** `"Te contesta a las 3 de la mañana y a la mañana ves quién quiere comprar."` figura como
  mensaje del frente Chatbots con la marca *(sin validar por Joaquín)*.
- **Dónde:** `.claude/agents/olvidata-cm.md`, tabla de mensajes por frente.
- **Por qué importa:** es el único mensaje del frente y ya está en la tabla que el CM usa para
  producir piezas. O se aprueba, o se reemplaza: hoy cualquiera la usa sin saber que no pasó
  revisión.
- **Lo que ya está acotado:** no se puede decir que resuelve sin humano (es *contesta y deriva*), ni
  usar ninguna tasa de conversión del bot propio, que no está medida.

### DEC-002 · El caso del frente Landing tiene el formulario roto
- **Qué:** el formulario del único caso de webs dio **error 500** en producción después de la
  migración de dominio, y el frente quedó con "reparos sin resolver".
- **Dónde:** `BotPublicitario/CAMPANAS-POR-FRENTE.md` y `plan_contenido_instagram_oct-dic2026.md`.
- **Por qué importa:** Landing se vende con ese caso. Mientras el formulario falle, mostrarlo es
  exponer un sistema roto; y es el único cliente real del frente (Diercas, ver `casos.md`).
- **Lo que hace falta:** confirmar si el 500 sigue, arreglarlo, y recién entonces habilitar el caso.

### DEC-003 · La lista post-promo 2027 está "confirmada" en un agente y "sin confirmar" en otro
- **Qué:** `olvidata-ceo.md` dice que la lista 2027 es **promo × 1,20, confirmada por Joaquín el
  2026-09-19**. `olvidata-marketing.md` dice que desde 2027-01-01 rige "una lista post-promo todavía
  sin confirmar, no cotizar esa lista de memoria".
- **Por qué importa:** los dos agentes cotizan. Si un lead pregunta hoy qué pasa en enero, la
  respuesta depende de a quién se le preguntó.
- **Para resolver:** si está confirmada, corregir marketing; si no, corregir el CEO. Es una línea en
  cada uno, pero hay que decidir cuál es la verdad.

### DEC-004 · El ticket de planificación (USD 426) está 31% arriba del real
- **Qué:** el plan financiero proyecta con USD 426/año por cliente. El real de los clientes que pagan
  recurrente, medido en el CRM, es **USD 294/año** (ver `clientes.md`).
- **Por qué importa:** el breakeven del Ministerio se calcula con ese número. Con 426, 35 clientes
  alcanzan; con 294 harían falta ~48 para el mismo recurrente. No es un detalle de planilla: cambia
  cuántos clientes hay que cerrar antes de poder dejar el empleo.
- **Para resolver:** recalibrar el plan con el ticket real, o explicar por qué el real es más bajo
  (año 1 gratis vigente en 4 clientes, 2 clientes con recurrente en 0 — ver DEC-005) y proyectar el
  ticket que va a quedar cuando esos se normalicen.

### DEC-005 · Dos clientes activos tienen recurrente en 0
- **Qué:** Contadores BMA (ambos sistemas) y LABIPAC figuran activos con `TicketAnualUsd = 0`.
- **Por qué importa:** o no tienen plan de mantenimiento (y entonces el conteo de "clientes activos"
  mezcla dos cosas distintas), o lo tienen y está sin cargar en el CRM (y entonces el recurrente real
  es más alto que el medido).
- **Para resolver:** una línea por cliente. Es el dato que más mueve la aguja de DEC-004.

### DEC-006 · La renovación de ESCABA venció y el cliente sigue activo
- **Qué:** `FechaProximaRenovacion` = 2026-10-02, hace 13 días, y el cliente está activo con USD
  160/año.
- **Por qué importa:** o se renovó y nadie lo registró (el CRM queda mintiendo), o hay plata sin
  cobrar.
- **Dónde:** `clientes.md`, sección Renovaciones.

### DEC-007 · Dos de los cuatro frentes no tienen ningún caso propio
- **Qué:** **AI Agents** y **Chatbots** se venden sin un caso de cliente verificable. El único
  "caso" de Chatbots es el bot del CRM propio de Olvidata, que es herramienta interna, no un cliente.
- **Por qué importa:** la regla de oro del contenido exige respaldo documental para todo claim. Esos
  dos frentes solo pueden comunicar promesa, y la regla vigente dice que el producto se muestra
  terminado operando.
- **Para resolver:** decidir si el bot propio se puede mostrar como caso (es real y está en vivo), o
  si el frente espera al primer cliente.

### DEC-008 · El frente de dos clientes está inferido, no confirmado
- **Qué:** ESCABA y PiApartments tienen frente **Build** asignado por inferencia del tipo de sistema.
- **Dónde:** `datos-manuales.yml`, marcados con un comentario.
- **Por qué importa:** poco, hoy. Importará cuando se mida "cierres por frente" (ver `metricas.md`).

### DEC-009 · El plan atribuye USD 1.243/mes a 43 clientes, y matemáticamente son 35
- **Qué:** la sección "La matemática del hito 2028" dice "43 clientes → recurrente USD 1.243/mes",
  pero 1.243 sale de 35 × 426 / 12. Con 43 el recurrente sería ≈USD 1.526/mes.
- **Por qué importa:** la conclusión ("cubre el Ministerio") se sostiene igual y de hecho con más
  margen, así que no urge. Pero el texto queda contradiciendo su propia aritmética, y ya está
  marcado como hallazgo sin corregir dentro del propio `olvidata-ceo.md`.
- **Para resolver:** decidir si 35 es el breakeven y 43 el objetivo con colchón (lo más probable) y
  redactarlo así, o corregir el número.

## Resueltas

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
