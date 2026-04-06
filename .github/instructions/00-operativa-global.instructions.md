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

# Formato minimo de respuestas tecnicas
1. Alcance funcional resumido.
2. Impacto tecnico por capa.
3. Riesgos y supuestos.
4. Pruebas funcionales minimas requeridas.
5. Checklist de salida para merge.
6. Cierre de calibracion estimado vs real.
