---
description: Reglas globales de operacion para todo trabajo tecnico y funcional en BlankProject.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Secuencia operativa obligatoria
Discovery/Relevamiento -> Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas funcionales -> Documentacion de alcance (cliente) -> Cierre de calibracion estimado vs real

# Reglas obligatorias
- No colocar logica de negocio compleja en Controllers.
- Los Controllers solo coordinan request/response y delegan en Services.
- La logica de negocio vive en Services.
- El acceso a datos vive en DbContext, repositorios o infraestructura.
- Toda modificacion debe indicar que capas afecta y por que.
- Si un cambio requiere migracion EF, debe indicarse explicitamente.
- Si un cambio afecta permisos, estados o validaciones, debe listarse.
- No hacer refactors cosmeticos salvo pedido expreso.
- Preservar comportamiento legacy salvo indicacion contraria.
- Las pruebas requeridas son funcionales.
- La documentacion requerida es de alcance para el cliente.
- El cierre de calibracion estimado vs real es obligatorio para mejorar la asertividad del presupuesto.

# Trazabilidad documental obligatoria en /docs
- Este repositorio (Agentes-IA) centraliza la memoria de trabajo de todos los proyectos.
- Cada proyecto tiene su carpeta propia en /docs/<proyecto>/.
- Cada agente tiene un unico archivo de memoria por proyecto en /docs/<proyecto>/definiciones/.
- Al trabajar sobre un proyecto, leer primero la version vigente del agente y luego editar ese mismo archivo.
- No crear archivos nuevos para el mismo agente y proyecto: siempre editar el existente.
- Cada ajuste relevante debe registrarse en /docs/<proyecto>/trazabilidad.md.
- El indice consolidado de proyectos vive en /docs/indice.md.

# Definicion minima por etapa
- Discovery/Relevamiento: alcance inicial, supuestos, exclusiones y dependencias.
- Analisis: problema de negocio, casos de uso y criterios de aceptacion.
- Diseno: propuesta funcional de flujo, datos y validaciones.
- Arquitectura: impacto por capa, riesgos tecnicos y necesidad de migraciones EF.
- Presupuesto: WBS funcional, O/M/P por item, riesgo, contingencia y rango final.
- Implementacion: cambios por capa segun fronteras definidas.
- Pruebas funcionales: validacion de flujos y reglas de negocio con evidencia.
- Documentacion de alcance (cliente): incluido/no incluido, supuestos y condiciones.
- Cierre de calibracion estimado vs real: desvio por item y acciones de recalibracion.

# Modo de trabajo recomendado
- Ask mode: Discovery/Relevamiento, Analisis, Diseno, Arquitectura y Presupuesto.
- Agent mode: Implementacion, pruebas funcionales, correccion de build, documentacion de alcance y cierre de calibracion.

# Gates de aprobacion entre etapas
- Cada etapa debe cerrar su archivo en /docs/<proyecto>/definiciones/ antes de pasar a la siguiente.
- No iniciar Diseno sin Analisis aprobado.
- No iniciar Arquitectura sin Diseno aprobado.
- No iniciar Presupuesto sin Arquitectura aprobada.
- No iniciar Implementacion sin Presupuesto aprobado por el cliente.
- No iniciar Documentacion al cliente sin QA aprobado.
- El Cierre de calibracion lo ejecuta el agente 4 al finalizar el sprint.

# Formato minimo de respuestas tecnicas
Este formato es el contrato de salida del orquestador hacia el cliente. Cada agente entrega su Salida minima propia (definida en su .agent.md), y el orquestador consolida estos puntos:
1. Alcance funcional resumido.
2. Impacto tecnico por capa.
3. Riesgos y supuestos.
4. Pruebas funcionales minimas requeridas.
5. Checklist de salida para merge.
6. Cierre de calibracion estimado vs real.
