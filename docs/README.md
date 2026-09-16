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
    trazabilidad-historico-hasta-<YYYY-MM-DD>.md  <- solo si el log se partio por tamaño (archivo cerrado)
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

## Formato del log de trazabilidad
- Formato canonico: el de `/docs/templates/proyecto/trazabilidad.md` — una entrada por decision, encabezado
  `### <YYYY-MM-DD [HH:mm]> - <agente>` y vinetas `Etapa / Cambio / Motivo / Impacto en capas / Riesgos-supuestos`
  (se omite la vineta que no aplica, no se inventa el dato).
- `trazabilidad.md` es un log (que se decidio y por que). El estado vigente del proyecto (fecha de inicio, estado,
  URLs de produccion, estado del ciclo por agente) va en `metadata.md`, no en el log.
- Cuando el log se vuelve muy grande, se parte: las entradas viejas pasan a
  `trazabilidad-historico-hasta-<fecha>.md` (archivo cerrado, no se le agregan entradas nuevas) y `trazabilidad.md`
  queda con las recientes y un puntero al historico arriba de `## Entradas`.

## Mantenimiento

### 2026-09-15 - limpieza y normalizacion de /docs
- Borrados por huerfanos (0 referencias): `templates/conversacion/` (plantilla deprecada, reemplazada por
  `templates/proyecto/`), `conversaciones/` (indice marcado DEPRECATED), `ShowroomGriffin/definiciones/1-analista-funcional.bak.md`,
  `plan-generate-comprehensive-readme.md-for-blankproject.md`, `plan-guardar-respuestas-de-agentes-ia-en-docs.md`,
  `plan-rediseo-catlogo-mvil-ptimo.md` y la carpeta vacia `estudios-medicos/`.
- Movido: `borrador-ferreteria-2026-07-25.md` -> `la-platense/` (es el borrador previo de la propuesta de
  La Platense, citado en `27-presupuesto-parametros.instructions.md`).
- Normalizados al formato canonico: `contadores-bma-conversor/trazabilidad.md`, `contadores-bma-agentes-ia/trazabilidad.md`
  (venian en formato tabla) y `ShowroomGriffin/trazabilidad.md` (venia con emojis + tabla de estado). El estado vigente
  de ambos proyectos se movio a su `metadata.md`.
- Partidos por tamaño: `crm-olvidata`, `marihogar` y `koi` — entradas anteriores al 2026-07-15 en
  `trazabilidad-historico-hasta-<fecha>.md`.
- Quitado el BOM UTF-8 de `koi/trazabilidad.md`, `labipac/trazabilidad.md` y `.github/agents/implementador-dotnet.agent.md`.
