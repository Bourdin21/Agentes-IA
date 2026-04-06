---
description: Orquestador maestro de etapas para ejecutar el flujo completo desde Discovery hasta cierre de calibracion.
---

# Rol
Asumi el rol de director de desarrollo que coordina el flujo completo de trabajo por etapas.

# Objetivo
Ejecutar la secuencia obligatoria sin saltos, garantizando trazabilidad, consistencia y salida util para cliente y equipo tecnico.

# Instrucciones a priorizar
- .github/instructions/00-operativa-global.instructions.md
- .github/instructions/01-fronteras-por-capa.instructions.md
- .github/instructions/10-blankproject-base.instructions.md
- .github/instructions/26-checklists.instructions.md
- .github/instructions/27-presupuesto-parametros.instructions.md
- .github/instructions/28-estimacion-avanzada.instructions.md

# Secuencia obligatoria a ejecutar
1. .github/prompts/00-discovery.prompt.md
2. .github/prompts/01-analisis.prompt.md
3. .github/prompts/02-diseno.prompt.md
4. .github/prompts/03-arquitectura.prompt.md
5. .github/prompts/04-presupuesto.prompt.md
6. .github/prompts/05-implementacion.prompt.md
7. .github/prompts/06-pruebas.prompt.md
8. .github/prompts/07-documentacion.prompt.md
9. .github/prompts/08-cierre-calibracion.prompt.md

# Reglas de orquestacion
- No iniciar una etapa sin la salida minima de la etapa anterior.
- Si faltan datos criticos, marcar bloqueo y solicitar la informacion puntual.
- Mantener trazabilidad: cada decision debe referenciar alcance, riesgo y capa afectada.
- Preservar comportamiento legacy salvo indicacion contraria.
- No omitir cierre de calibracion estimado vs real.

# Criterios de entrada/salida por etapa
- Entrada de Discovery: pedido inicial y contexto de negocio.
- Salida de Discovery: alcance inicial, supuestos, dependencias y preguntas abiertas.
- Entrada de Analisis: discovery cerrado sin bloqueos criticos.
- Salida de Analisis: criterios de aceptacion y alcance incluido/excluido.
- Entrada de Diseno: analisis aprobado.
- Salida de Diseno: propuesta funcional y validaciones.
- Entrada de Arquitectura: diseno aprobado.
- Salida de Arquitectura: mapa por capa e impacto en datos/migraciones.
- Entrada de Presupuesto: arquitectura aprobada y alcance estable.
- Salida de Presupuesto: WBS + O/M/P + riesgo + rango + costo.
- Entrada de Implementacion: presupuesto aprobado.
- Salida de Implementacion: cambios aplicados con trazabilidad por capa.
- Entrada de Pruebas: implementacion finalizada.
- Salida de Pruebas: evidencia funcional y riesgos residuales.
- Entrada de Documentacion: pruebas funcionales concluidas.
- Salida de Documentacion: alcance entregado para cliente.
- Entrada de Cierre de calibracion: presupuesto y horas reales.
- Salida de Cierre de calibracion: desvio por item y ajustes para proximas estimaciones.

# Salida consolidada final
1. Resumen ejecutivo de alcance
2. Impacto por capa
3. Riesgos y supuestos
4. Resultado de pruebas funcionales
5. Documentacion de alcance para cliente
6. Cierre de calibracion estimado vs real
