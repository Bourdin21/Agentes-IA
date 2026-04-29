# Copilot Instructions - BlankProject (Orquestador)

Este archivo define el marco general. El detalle operativo y técnico se encuentra modularizado en instrucciones por etapa y por capa dentro de .github/instructions.

## Secuencia operativa obligatoria
Discovery/Relevamiento -> Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas funcionales -> Documentacion de alcance (cliente) -> Cierre de calibracion estimado vs real

## Objetivo de la reestructuracion
- Separar reglas globales de reglas por capa.
- Facilitar reutilizacion por agentes especializados.
- Reducir ambigüedad al implementar cambios en MVC + EF Core + MySQL.

## Mapa de instrucciones modulares
- .github/instructions/00-operativa-global.instructions.md
- .github/instructions/01-fronteras-por-capa.instructions.md
- .github/instructions/10-blankproject-base.instructions.md
- .github/instructions/20-domain.instructions.md
- .github/instructions/21-application.instructions.md
- .github/instructions/22-infrastructure.instructions.md
- .github/instructions/23-web.instructions.md
- .github/instructions/24-config-paquetes.instructions.md
- .github/instructions/25-frontend-design-system.instructions.md
- .github/instructions/26-checklists.instructions.md
- .github/instructions/27-presupuesto-parametros.instructions.md
- .github/instructions/28-estimacion-avanzada.instructions.md
- .github/instructions/29-trazabilidad-conversacion.instructions.md
- .github/instructions/30-qa-regresiones.instructions.md

## Reglas base que siempre aplican
- No colocar lógica de negocio compleja en Controllers.
- Los Controllers coordinan request/response y delegan en Services.
- La lógica de negocio vive en Services.
- El acceso a datos vive en DbContext, repositorios o infraestructura.
- Toda modificación debe indicar capas afectadas y motivo.
- Si hay migración EF, debe explicitarse.
- Si hay impacto en permisos, estados o validaciones, debe listarse.
- Preservar comportamiento legacy salvo indicación contraria.
- Las pruebas requeridas son funcionales.
- La documentacion requerida es de alcance para el cliente.
- El cierre de calibracion estimado vs real es obligatorio.
- La trazabilidad de la conversacion debe persistirse en /docs/conversaciones con definiciones por agente en archivos .md individuales.

## Formato mínimo de respuestas técnicas
1. Alcance funcional resumido.
2. Impacto técnico por capa.
3. Riesgos y supuestos.
4. Pruebas funcionales mínimas requeridas.
5. Checklist de salida para merge.
6. Cierre de calibracion estimado vs real.

## Presupuesto
- Los parámetros están en .github/instructions/27-presupuesto-parametros.instructions.md.
- El metodo avanzado de estimacion esta en .github/instructions/28-estimacion-avanzada.instructions.md.