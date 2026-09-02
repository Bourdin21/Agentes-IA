---
name: feedback-costo-ia-interno-presupuesto
description: Metodologia interna (solo estudio) para estimar el costo sombra de consumo de IA por modulo, distinta del cargo "Tokens IA 25%" visible al cliente. Vigente desde 2026-08-15.
metadata:
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-08-15T17:00:29.780Z
---

Se agrego una seccion nueva "Costo interno de IA por consumo de motores de pensamiento" en `27-presupuesto-parametros.instructions.md` (y PASO 10 en `presupuesto-mvc.agent.md`), distinta del cargo "Tokens IA = 25% del subtotal" que ya existia (ver [[feedback-tokens-ia-10-porciento]] — ese es un mecanismo de pricing/margen visible al cliente; esto es un costo REAL proyectado, invisible al cliente).

**Dato clave verificado en la cuenta:** el estudio paga Claude via suscripcion Stripe (`billingType: stripe_subscription`, confirmado en `~/.claude.json`), no por token via API. Por eso el calculo es un "costo sombra" a precio de lista de la API (Opus 5: $5/$25 por MTok; Sonnet 5: $3/$15, intro $2/$10 hasta 2026-08-31) — sirve para trazabilidad de margen interno, no es un gasto variable real mes a mes.

**Formula:** Costo_IA_modulo = Horas_facturables_modulo (M/2.5x1.20, la misma que ya se usa para precio) x tarifa_Opus_USD_hora, porque Implementador+QA (ambos en Opus desde 2026-08-14) concentran casi todo el esfuerzo asistido por IA a nivel modulo. Overhead fijo de 4h a tarifa Sonnet cubre las etapas Ask-mode (Discovery/Analisis/Diseño/Arquitectura/Presupuesto/Documentacion), una sola vez por proyecto.

**Tarifas placeholder (sin calibrar todavia):** Opus USD 4/h (rango 3-10), Sonnet USD 1/h (rango 0.5-1.5) — estimadas desde precio de lista + supuesto de throughput tipico, NO medidas. Plan de calibracion: capturar el costo real via `/cost` de Claude Code al cierre de cada sprint con Implementador/QA, reemplazar el placeholder tras 3+ cierres con dato real (mismo metodo que la calibracion del factor de eficiencia 2.5 de horas).

**Como se aplica:** si Costo_IA_modulo supera 15% del precio de lista del modulo, la diferencia se suma AL NUMERO FINAL de ese modulo (ya calculado, sin linea nueva, sin desglose visible). Si esta por debajo del umbral, el 25% de Tokens IA ya lo cubre y no se ajusta nada. El calculo completo vive solo en `4-presupuestador.md`; `presupuesto-cliente.md` nunca lo menciona.

**Por que:** el usuario pidio explicitamente (2026-08-15) tener en cuenta, solo para el estudio, el costo real proyectado de IA en base al modelo/configuracion usado (dado el cambio reciente de Implementador+QA a Opus), y que ese dato se sume al precio final del cliente ya calculado (folded in), no como linea aparte.

**Como aplicar:** cuando el presupuestador cierre un proyecto nuevo, seguir el PASO 10 de `presupuesto-mvc.agent.md`. Al cierre real de los primeros 3 proyectos bajo esta regla, recalibrar las tarifas placeholder con datos medidos de `/cost`. Relacionado: [[project-agentes-ia]], [[feedback-tokens-ia-10-porciento]].
