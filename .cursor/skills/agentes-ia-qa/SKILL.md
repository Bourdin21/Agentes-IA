---
name: agentes-ia-qa
description: QA funcional del estudio. Usar para pruebas, regresiones cross-proyecto, auto-fix catalogado y reporte de liberación en MVC. Modo Agent.
disable-model-invocation: true
---

# QA MVC

Modo Cursor: **Agent**.

## Arranque

1. Confirmar proyecto y repo del sistema.
2. Leer `C:/Sistemas/Agentes-IA/.github/agents/qa-mvc.agent.md` y adoptar el rol.
3. Leer definiciones 1, 2 y 5 del proyecto y `definiciones/6-qa.md`.
4. Cargar `C:/Sistemas/Agentes-IA/docs/qa/regresiones-manuales.yml` y ejecutar playbook.
5. Cargar instrucciones: `00`, `01`, `23`, `26`, `29`, `30`.

## Cierre

- Actualizar `definiciones/6-qa.md` y `trazabilidad.md`.
- Entregar cobertura por criterio, máquina de estados, catálogo cross-proyecto, defectos y auto-fixes aplicados.
