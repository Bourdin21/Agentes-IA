# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-08-20 - orquestador (Discovery + Analisis + Diseno + Arquitectura + Presupuesto — pasada consolidada)
- Etapa: Discovery, Analisis, Diseno, Arquitectura, Presupuesto (corridas en una sola pasada por velocidad comercial, mismo criterio que audifonos-bariloche 2026-08-19).
- Cambio: creado el proyecto `estudio-contable-maribel-garcia` a partir de la conversacion de calificacion outbound (3 respuestas via WhatsApp, 20/08, recibidas fuera de orden respecto de las preguntas — reconstruidas por contenido en 1-analista-funcional.md). Escaneado `docs/patrones/catalogo.yml` y `docs/*/definiciones/` para reutilizacion cross-proyecto: sin match de dominio (conciliacion bancaria es dominio nuevo en el estudio), reuso limitado al enfoque tecnico de parser de archivos (contadores-bma-conversor). Armado WBS de 8 items (7 en Etapa 1 deterministica, 1 en Etapa 2 — asistencia por IA). PERT por item, sin comparable historico exacto (se documento la ausencia en vez de forzar comparacion invalida). Ratio de reutilizacion R=0% (Tier 3) y volumen Subtotal_lista=USD 462 (Tier V0) — ambos ejes dan 0% de descuento por calculo objetivo, sin override pedido esta vez. Costo final: Etapa 1 USD 395 + Etapa 2 USD 67 + Tokens IA USD 116 = **USD 578 total desarrollo**. Mantenimiento: PRO USD 400/año (hasta 2 usuarios, cubre el caso "1 o 2 personas" mas barato que STARTER+usuario adicional). Documento `presupuesto-cliente.md` armado con precios (a diferencia de otros leads sin discovery) porque el lead pidio costos explicitamente durante la calificacion.
- Motivo: pedido explicito del cliente ("quiero enviar una estimacion funcional o presupuesto al lead").
- Impacto en capas: ninguno de codigo — solo documentacion de propuesta. Sin repo creado todavia.
- Riesgos/supuestos: **discovery minimo y desordenado** — 3 respuestas de un cuestionario automatico de calificacion, sin llamada/reunion de relevamiento, con las respuestas fuera de orden respecto de las preguntas (reconstruidas por contenido, no por posicion). Supuestos explicitos declarados en `1-analista-funcional.md`: formato exacto de los extractos (banco especialmente, riesgo de que solo entreguen PDF no tabular), cantidad exacta de usuarios (1 vs 2). **Primera integracion de una API de IA en tiempo de ejecucion de un producto entregado por el estudio** (item 8) — sin precedente, con nota explicita de costo operativo continuo en produccion (distinto del costo de desarrollo), declarado como pregunta abierta en la propuesta, no asumido en silencio. **Gate cliente pendiente**: propuesta lista para revision de Joaquin antes de enviarse al lead real.

### 2026-08-20 - orquestador (dos opciones de stack ofrecidas al lead — PHP liviano vs .NET profesional)
- Etapa: Presupuesto/Documentacion comercial (ajuste sobre el alcance, previo a numeros — sin cambio de PERT ni precio, esos siguen calculados solo para la Opcion B en `4-presupuestador.md`).
- Cambio: Joaquin pidio evaluar PHP (como contadores-bma-conversor) vs .NET/BlankProject para este proyecto. Se recomendo .NET (reuso del ecosistema del estudio: Identity, AdjuntoService, calibracion PERT, QA automatizado, etc. — todo asume BlankProject; PHP forfeitea esa base). Joaquin pidio en cambio ofrecer AMBAS opciones al lead para que elija: creado `especificacion-funcional-opciones.md` — Opcion A (conversor liviano, sin login/historial/IA/crecimiento, estilo contadores-bma-conversor) vs Opcion B (sistema profesional con usuarios, historial, auditoria, asistencia IA y espacio para crecer, ya especificado en 2-disenador-funcional.md/3-arquitecto-mvc.md). Documento sin precios (mismo criterio que `propuesta-funcional-cliente.md`).
- Motivo: pedido explicito del cliente ("ofrecer opcion php como conversor liviano o .NET como sistema de gestion profesional... Haceme un documento con especificacion funcional").
- Impacto en capas: ninguno de codigo — documento de propuesta. Si el lead elige Opcion A, el presupuesto de `4-presupuestador.md` (calculado para Opcion B) no aplica — requeriria una reestimacion nueva sobre alcance PHP sin reuso del ecosistema .NET.
- Riesgos/supuestos: la Opcion A esta descripta funcionalmente pero NO tiene WBS/PERT propio todavia — si el lead la elige, hace falta una pasada de presupuesto separada antes de cotizarla.

### 2026-08-20 - presupuestador (Opcion A calculada + documento combinado especificacion+presupuesto)
- Etapa: Presupuesto (cierre de la comparacion — ambas opciones ya tienen numero propio).
- Cambio: calculado WBS/PERT/costo de Opcion A (PHP conversor liviano) en `4-presupuestador.md`, anclado directamente contra contadores-bma-conversor (mismo stack, mismo perfil sin estado) en vez de reusar los numeros de Opcion B. Total Opcion A: USD 325 desarrollo (subtotal USD 260 + Tokens IA USD 65) + STARTER USD 300/año. `presupuesto-cliente.md` reescrito como documento combinado: especificacion funcional de ambas opciones (heredada de `especificacion-funcional-opciones.md`) + tabla de precios de cada una + tabla de diferencias clave con los totales lado a lado.
- Motivo: pedido explicito del cliente ("hacer un documento para el cliente con especificacion funcional y presupuesto").
- Impacto en capas: ninguno de codigo — documento de propuesta.
- Riesgos/supuestos: mismos supuestos que las entradas anteriores (formato real de extractos, 1 vs 2 usuarios). Ninguna opcion tiene descuento de expansion agresiva aplicado (ambas caen en Tier 3 reutilizacion / Tier V0 volumen por calculo objetivo, sin override pedido).

### 2026-08-20 - presupuestador (Tokens IA distribuido dentro de cada modulo — regla invertida)
- Etapa: Presupuesto (cambio de exposicion, sin cambio de total).
- Cambio: a pedido explicito de Joaquin, se invirtio la regla vigente desde 2026-07-03 de mostrar "Tokens IA" como linea separada — ahora se distribuye dentro del precio de cada modulo (factor constante x1.25 sobre el precio de lista, ya que Tokens IA es siempre 25% del subtotal). Actualizado `27-presupuesto-parametros.instructions.md` y `presupuesto-mvc.agent.md` (regla de estudio, aplica a todo proyecto futuro, no solo este). En este proyecto: `4-presupuestador.md` ahora tiene tabla "Precios distribuidos al cliente" en ambas opciones, y `presupuesto-cliente.md` ya no menciona "Tokens IA" en ningun lado — los totales (USD 325 Opcion A, USD 578 Opcion B) no cambiaron, solo el desglose visible.
- Motivo: pedido explicito del cliente ("distribuir el valor USD de tokens IA dentro de toda la funcionalidad... tiene que estar impuesta ya en el precio del modulo").
- Impacto en capas: ninguno de codigo — documento de propuesta + regla de instrucciones del estudio.
- Riesgos/supuestos: el descuento de expansion agresiva (si aplicara) sigue mostrandose como linea propia, no se distribuye — solo Tokens IA cambio de exposicion. En este proyecto no aplica ningun descuento (Tier 3/V0 ambas opciones), asi que no hay caso de prueba de la interaccion entre ambas reglas todavia.

## Historial de ajustes
- 2026-08-20: primera version.
