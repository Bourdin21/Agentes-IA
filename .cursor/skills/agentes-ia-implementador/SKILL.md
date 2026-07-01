---
name: agentes-ia-implementador
description: Implementador .NET del estudio. Usar para codificar cambios aprobados en ASP.NET Core MVC, EF Core y MySQL con trazabilidad y reutilización cross-proyecto. Modo Agent.
disable-model-invocation: true
---

# Implementador .NET

Modo Cursor: **Agent**.

## Arranque

1. Confirmar proyecto y repo del sistema (ruta en `docs/<proyecto>/metadata.md` o `copilot-instructions.md`).
2. Leer `C:/Sistemas/Agentes-IA/.github/agents/implementador-dotnet.agent.md` y adoptar el rol.
3. Escanear `docs/*/definiciones/5-implementador.md` para reutilización antes de implementar desde cero.
4. Verificar definiciones 2, 3 y 4 aprobadas.
5. Leer `definiciones/5-implementador.md`.
6. Cargar instrucciones: `00`, `01`, `20`–`26`, `29`.

## Cierre

- Build y pruebas mínimas con evidencia.
- Actualizar `definiciones/5-implementador.md` y `trazabilidad.md`.
- Entregar plan por etapas, cambios por capa, migraciones EF y checklist de merge.
