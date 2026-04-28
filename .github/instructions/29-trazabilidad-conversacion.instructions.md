---
description: Trazabilidad documental obligatoria por proyecto en carpeta /docs del repositorio Agentes-IA.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Objetivo
- Mantener memoria acumulativa de trabajo por proyecto y por agente.
- Cada agente tiene un unico archivo por proyecto que se actualiza en cada conversacion.
- Nunca crear un archivo nuevo para el mismo agente y proyecto: siempre editar el existente.

# Contexto de uso
- Este repositorio (Agentes-IA) es compartido por multiples proyectos.
- La memoria de trabajo se guarda aqui, organizada por nombre de proyecto.
- Cada proyecto tiene su propia carpeta bajo /docs con definiciones separadas por agente.

# Estructura obligatoria
- /docs/indice.md
- /docs/<proyecto>/metadata.md
- /docs/<proyecto>/trazabilidad.md
- /docs/<proyecto>/definiciones/1-analista-funcional.md
- /docs/<proyecto>/definiciones/2-disenador-funcional.md
- /docs/<proyecto>/definiciones/3-arquitecto-mvc.md
- /docs/<proyecto>/definiciones/4-presupuestador.md
- /docs/<proyecto>/definiciones/5-implementador.md
- /docs/<proyecto>/definiciones/6-qa.md
- /docs/<proyecto>/definiciones/7-documentador.md

# Regla de memoria acumulativa por agente
- Cada agente edita su archivo existente en /docs/<proyecto>/definiciones/ al trabajar en ese proyecto.
- Si el archivo no existe todavia, crearlo desde la plantilla en /docs/templates/proyecto/definiciones/.
- Si ya existe, editar el mismo archivo agregando o ajustando las definiciones vigentes.
- No crear archivos duplicados para el mismo agente dentro del mismo proyecto.

# Regla de trazabilidad por interaccion
- Cada ajuste relevante debe agregar entrada en /docs/<proyecto>/trazabilidad.md con:
  - fecha y hora
  - agente/etapa
  - resumen del cambio o decision tomada
  - motivo
  - impacto en capas y riesgos/supuestos si aplica

# Regla operativa para el orquestador
1. Al iniciar trabajo sobre un proyecto, verificar si ya existe /docs/<proyecto>/.
2. Si no existe, crear la estructura base desde /docs/templates/proyecto/.
3. Antes de cada etapa, leer la ultima version de definiciones del agente en /docs/<proyecto>/definiciones/.
4. Al cerrar cada etapa, actualizar el archivo del agente y registrar entrada en trazabilidad.md.
5. Mantener /docs/indice.md actualizado con todos los proyectos activos.
