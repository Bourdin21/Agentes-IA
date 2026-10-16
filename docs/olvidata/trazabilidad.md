# Trazabilidad de la memoria de negocio

Log de cambios de **precios** y **reglas comerciales**. No es estado: el estado vigente vive en
`precios.md` y `reglas-comerciales.md`. Acá queda el rastro de qué cambió, cuándo y por decisión de
quién.

**Obligatorio:** todo cambio a `precios.md` deja una línea acá. `scripts/doctor.py` lo verifica y
avisa si un commit toca los precios sin registrarlo. Un precio que cambia sin rastro es un precio
que nadie puede defender frente a un cliente que pregunta por qué le cotizaron distinto el mes
pasado.

Formato: `### <fecha> — <qué cambió>` y, abajo, de dónde a dónde y quién lo decidió.

## Entradas

### 2026-10-15 — nace esta carpeta: la memoria de negocio deja de ser solo reglas y supuestos
- **Cambio:** se crean `clientes.md`, `pipeline.md`, `metricas.md` (generados del CRM),
  `costos.md`, `casos.md`, `precios.md`, `reglas-comerciales.md`, `decisiones.md` y
  `datos-manuales.yml`; se mueven `MARCA.md`, el plan de comercialización del Second Brain y la línea
  editorial desde `BotPublicitario` a `marca/`.
- **Motivo:** la memoria guardaba reglas y supuestos pero no lo que pasa de verdad con clientes y
  ventas. El plan proyectaba con un ticket de USD 426 sin medir el real, y el umbral que gobierna la
  salida del Ministerio (USD 1.173/mes) no se registraba en ningún lado.
- **Precios:** `precios.md` sale de `olvidata-ceo.md` **sin cambiar un solo número** — es un
  movimiento de archivo, no una revisión de lista. El agente quedó con un puntero.
- **Reglas:** `reglas-comerciales.md` es índice, no cuerpo: cada regla sigue viviendo con su contexto
  en el archivo que la decidió, y acá tiene ID citable (`COM-NNN`) más puntero.
- **Hallazgos que el dato real dejó a la vista** (anotados en `decisiones.md`): el ticket real es USD
  294 contra los 426 del plan (DEC-004); dos clientes activos tienen recurrente en 0 (DEC-005); la
  renovación de ESCABA venció hace 13 días (DEC-006); el recurrente cobrable hoy es USD 152/mes, el
  13% del umbral del Ministerio; y la lista post-promo 2027 figura confirmada en un agente y sin
  confirmar en otro (DEC-003).
- **Impacto:** `olvidata-ceo.md` 66 → 39 KB y `olvidata-cm.md` 75 → 69 KB, por extracción de los
  precios y del inventario de casos. Menos contexto gastado al arrancar, y los datos quedan donde los
  pueden leer los cuatro agentes en vez de uno.

### 2026-10-15 — MARCA.md § 0c reescrito: prevalece la promesa del CEO
- **Cambio:** § 0c pasaba de prohibir toda la familia de "la IA hace tu trabajo" a distinguir el
  **reemplazo de la persona** (prohibido) del **alivio del trabajo cotidiano** (habilitado, COM-005).
- **Decisión:** Joaquín, 2026-10-15, consultado explícitamente.
- **Motivo:** la redacción anterior vetaba la promesa vigente del CEO desde el 2026-10-11. La
  contradicción vivió semanas sin detectarse porque los archivos estaban en repos distintos; por eso
  el mismo día MARCA.md se movió acá.
- **Registrado como:** `decisiones.md` DEC-000 (resuelta).

### 2026-10-16 — siete decisiones resueltas por Joaquín, y lo que cambió con cada una
- **DEC-004 (ticket real):** el promedio de la base es más bajo por el precio viejo de los clientes
  antiguos, no por error de carga. Se agregó el cálculo **a lista vigente**: ticket USD 498, por
  encima de los 426 de planificación. El breakeven del Ministerio bajó de "48 clientes si el ticket
  real fuera 294" a **29 a lista vigente**.
- **DEC-005 (recurrente en 0):** BMA (x2) y LABIPAC son **sistemas regalados**; marcados como tal, se
  cuentan aparte y ya no bajan el ticket promedio.
- **DEC-006 (ESCABA):** la renovación ya se cobró; el plan es de USD 240 anuales en 4 cuotas
  trimestrales. **Destapó que el CRM no modela periodicidad de pago** — un plan trimestral se ve como
  una renovación anual vencida cada 3 meses. Queda como corrección pendiente de cargar.
- **DEC-003 (lista 2027):** está confirmada (promo × 1,20). El desactualizado era
  `olvidata-marketing.md`; corregido ahí y en `precios.md`.
- **DEC-007 (casos por frente):** AI Agents tiene **Contadores BMA** y Chatbots **el CRM propio**
  (en vivo desde 2026-09-14). Dos fichas nuevas en `casos.md`. Landing queda como único frente sin
  ficha.
- **DEC-001 (frase del Chatbot):** confirmada y mejorada — *"Contesta a las 3 de la madrugada. A las 8
  sabés quién quiere comprar."* La original usaba "mañana" con dos sentidos en la misma frase.
- **DEC-009 (setup + recurrente):** el plan se piensa con las dos mitades. `metricas.md` las muestra
  separadas (no recurrente acumulado USD 7.818 contra recurrente contratado USD 3.820/año) y queda
  escrito por qué el umbral del Ministerio se mide **solo** con el recurrente.
- **Precios:** `precios.md` cambió solo la nota de la lista 2027 (de "sin confirmar" a confirmada).
  Ningún número de la tabla se tocó.
- **Quedan abiertas:** DEC-002 (formulario del caso de Landing con error 500) y DEC-008 (el frente de
  ESCABA y PiApartments sigue inferido).

### 2026-10-16 — primera corrida de evals de los agentes de negocio
- **Qué:** 5 casos, 10 corridas, en subagentes limpios de `olvidata-cm`, `olvidata-ceo` y
  `olvidata-sales`, para verificar que mover los precios y el inventario de casos fuera de los
  `.agent.md` no dejara a los agentes inventando el dato.
- **Resultado: 5 de 5 en sustancia, 3 de 5 mecánico.** Ninguno citó de memoria: los cinco fueron a
  buscar el archivo. Los dos FAIL eran de los graders.
- **Lo que se arregló:** `EV-NEG-001` castigaba la palabra "prohibid", que aparece justo cuando el
  agente acierta; `EV-NEG-003` y `EV-NEG-004` pasaron a grader de modelo (distinguir "lo afirmó" de
  "lo nombró para negarlo", y reconocer una regla dicha con las palabras del cliente, es juicio);
  `EV-NEG-005` se reescribió porque medía el mundo anterior a DEC-007.
- **Hallazgo que justificó la corrida sola:** la ficha de **Contadores BMA** en `casos.md` decía "en
  Discovery/Diseño" y era falso — está **en producción desde el 2026-10-07 con tres agentes**
  (conciliación bancaria, sueldos, impuestos). El agente de ventas lo citó mejor que la ficha porque
  fue a leer `docs/contadores-bma-agentes-ia/`. Ficha corregida.
- **Detalle de la corrida:** `docs/evals/corridas/negocio-2026-10-16/RESULTADO.md`.
