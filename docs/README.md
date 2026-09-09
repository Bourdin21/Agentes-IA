# Memoria de trabajo por proyecto

Este directorio centraliza la memoria acumulativa de trabajo de todos los proyectos
gestionados desde este repositorio de agentes.

## Objetivo
- Un folder por proyecto que persiste la memoria de cada agente.
- Cada agente tiene un unico archivo por proyecto que se actualiza en cada conversacion.
- Nunca crear un archivo nuevo para el mismo agente y proyecto: siempre editar el existente.

## Estructura

/docs/
  indice.md
  <proyecto>/
    metadata.md
    trazabilidad.md
    definiciones/
      1-analista-funcional.md
      2-disenador-funcional.md
      3-arquitecto-mvc.md
      4-presupuestador.md
      5-implementador.md
      6-qa.md
      7-documentador.md
  templates/
    proyecto/  <- plantillas base para inicializar un proyecto nuevo
  referencia/  <- estudios tecnicos de sitios/sistemas ajenos que originan reglas de un rol
                  (no son proyectos: no van en indice.md; se enlazan desde el .agent.md que los usa)

## Reglas de uso
1. Al iniciar trabajo en un proyecto nuevo, copiar /docs/templates/proyecto/ como /docs/<nombre-proyecto>/.
2. Registrar el proyecto en /docs/indice.md.
3. Cada agente lee y actualiza su archivo en definiciones/ al inicio y cierre de cada etapa.
4. Si una definicion cambia, editar el mismo archivo existente (no crear uno nuevo).
5. Cada ajuste relevante se registra en trazabilidad.md del proyecto.
