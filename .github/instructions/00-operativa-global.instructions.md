---
description: Reglas globales de operacion para todo trabajo tecnico y funcional en BlankProject.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Secuencia operativa obligatoria
Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas -> Documentacion

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
- Siempre proponer pruebas minimas.

# Modo de trabajo recomendado
- Ask mode: Analisis, Diseno, Arquitectura, Presupuesto.
- Agent mode: Implementacion, pruebas tecnicas, correccion de build, generacion de tests, documentacion tecnica derivada de codigo.

# Formato minimo de respuestas tecnicas
1. Alcance funcional resumido.
2. Impacto tecnico por capa.
3. Riesgos y supuestos.
4. Pruebas minimas requeridas.
5. Checklist de salida para merge.
