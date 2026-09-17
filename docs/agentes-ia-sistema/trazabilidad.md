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
