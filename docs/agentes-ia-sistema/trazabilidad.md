# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### <YYYY-MM-DD HH:mm> - <agente>
- Etapa: <Discovery|Analisis|Diseno|Arquitectura|Presupuesto|Implementacion|Pruebas|Documentacion|Cierre>
- Cambio: <resumen de la decision o ajuste>
- Motivo: <por que se tomo esta decision>
- Impacto en capas: <Presentacion|Negocio|Datos>
- Riesgos/supuestos: <resumen si aplica>

## 2026-09-17 - Discovery abierto (etapa 0)

- Proyecto creado desde `docs/templates/proyecto/`. Pedido: 6 criterios de uso de agentes LLM en el estudio.
- **Relevamiento del estado real** (no supuesto): C2 ya existe (5 skills en `.claude/skills/`); C1 existe parcialmente como convencion documental + memoria por repo/subagente; C3, C5 y C6 no existen; C4 existe como herramienta del harness pero sin criterio ni persistencia.
- **Hallazgo 1 (condiciona C5)**: el estudio paga Claude Code por **suscripcion Stripe, no por token**. No hay facturacion por llamada/token que se pueda desglosar por cliente. El tablero pedido cambia de naturaleza: costo sombra estimado y/o consumo real solo donde hay API propia (multirubro M6, CRM `contactomensajesia`).
- **Hallazgo 2 (regla de reutilizacion)**: `olvidata-agentes-multirubro` ya implemento **5 de los 6 criterios** (M5 workspace por cliente, M6 limites y consumo, M10 base de conocimiento, M11 conectores, M12 tareas programadas), roadmap completo y QA cerrado el 2026-09-16. C6 es el unico criterio sin precedente en todo el historial.
- **Gate**: Discovery NO cerrado. 3 preguntas bloqueantes abiertas (P1/P2/P3). No se inicia Analisis.

## 2026-09-25 - Harness: gaps del research de ingenieria de agentes (secciones 3 y 4)

- **Origen**: research de novedades de ingenieria de agentes en big tech (OpenAI harness engineering, Anthropic harness design / effective harnesses / evals / managed agents, Microsoft Build ACS+ASSERT, AWS AgentCore, A2A, papers AHE / Self-Harness / ACE / progressive disclosure). Contraste contra lo que el repo ya tenia: la mayoria de los conceptos publicados **ya estaban implementados** con otro nombre (instructions = harness, skills + cat_resumen = progressive disclosure, instruccion 39 = context budget, scripts/*.py = code execution). Se implementaron los 6 gaps reales.
- **Gap 1 - Evaluador independiente (impacto alto, costo cero)**: el QA hacia auto-fix y despues se calificaba a si mismo. Ahora el repo del sistema bajo prueba es **read-only** para QA, todo criterio arranca en **Default-FAIL** y solo pasa con evidencia observada, los fixes salen como **parte de defecto** al Implementador, y el cierre de un defecto lo declara QA en una corrida posterior con contexto nuevo. Toca `qa-mvc.agent.md`, `agentes-ia-qa.md`, `30-qa-regresiones`, `33-verificacion-automatizada-qa`, `implementador-dotnet.agent.md`, `agentes-ia-implementador.md`.
- **Gap 2 - Evals del harness**: instruction `40-evals-del-harness` + `docs/evals/casos.yml` (23 casos activos, todos derivados de fallos reales del catalogo de regresiones y del dataset de calibracion) + `scripts/evals.py` (validar/listar/costo/preparar/gradear). **No ejecuta nada por si solo**: prepara prompts y gradea respuestas; `costo` imprime el gasto antes de correr (USD ~14 en Opus para la suite completa, a precio de lista).
- **Gap 3 - Observabilidad del durante**: `scripts/traza.py` registra al cerrar cada etapa los reintentos, criterios fallados y **reglas que hubo que releer** (senal de regla mal ubicada en el arranque del rol), en `trazabilidad.md` + indice plano `docs/trazas/trazas.tsv`. `resumen` agrega y marca que corregir.
- **Gap 4 - Memoria incremental con id**: `29-trazabilidad-conversacion` deja de exigir "editar el bloque vigente in-place" (reescritura iterativa = erosion del detalle de dominio) y pasa a **entradas con id propio** marcadas `superada-por: <id>`. El techo de 150 KB se sostiene archivando, no reescribiendo.
- **Gap 5 - Reset de contexto como regla dura**: `39` seccion 4b. Compactar el historial no evita que el modelo cierre el trabajo antes de tiempo con la ventana llena. Toda etapa cierra su artefacto y la siguiente arranca en contexto nuevo; prohibido compactar para seguir.
- **Gap 6 - `AGENTS.md`** en la raiz: entrada portable cross-herramienta (Codex/Cursor/Copilot), apuntando a las instructions sin duplicarlas.
- **Seccion 4 del research (comercializacion)**: delegada a `olvidata-ceo`, quedo en `docs/olvidata-agentes-multirubro/` (plan-comercializacion §2.1, PA-42/43/44).
- **Motivo**: el repo es el harness de todos los sistemas del estudio; tocarlo cambia el comportamiento de produccion. Faltaban las tres piezas que permiten mejorarlo con datos en vez de intuicion: un evaluador que no sea el generador, trazas de lo que pasa durante la corrida, y evals que digan si un cambio a una instruction mejoro o empeoro al agente.
- **Impacto en capas**: N/A (harness documental + scripts). `doctor.py` sin errores.
- **Riesgos/supuestos**: la suite de evals todavia **no se corrio** (gasta tokens, requiere confirmacion explicita). El ciclo de defecto ahora necesita dos corridas de QA en vez de una: es mas lento a proposito.

### Traza de corrida -- 2026-09-25 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: 29, 30, 33, 39
- Nota: gaps 1-6 del research de ingenieria de agentes; doctor.py sin errores

