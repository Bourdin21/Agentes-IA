# CLAUDE.md — Agentes-IA

Este repositorio centraliza la memoria de trabajo, instrucciones y agentes para todos los proyectos activos del estudio.

## Marco operativo

Ver `.github/copilot-instructions.md` para el inventario de proyectos, patrones cross-proyecto y calibración histórica del presupuestador.

### Secuencia obligatoria por feature

Discovery → Análisis → Diseño → Arquitectura → Presupuesto → Implementación → Pruebas → Documentación (cliente) → Cierre de calibración

- Cada etapa cierra su archivo en `C:/Sistemas/Agentes-IA/docs/<proyecto>/definiciones/` antes de pasar a la siguiente.
- No iniciar Diseño sin Análisis aprobado. No iniciar Arquitectura sin Diseño aprobado. No iniciar Presupuesto sin Arquitectura aprobada. No iniciar Implementación sin Presupuesto aprobado por el cliente.

## Agentes disponibles

| # | Rol | Archivo | Modo |
|---|---|---|---|
| 1 | analista-funcional | `.github/agents/analista-funcional.agent.md` | Ask |
| 2 | disenador-funcional | `.github/agents/disenador-funcional.agent.md` | Ask |
| 3 | arquitecto-mvc | `.github/agents/arquitecto-mvc.agent.md` | Ask |
| 4 | presupuesto-mvc | `.github/agents/presupuesto-mvc.agent.md` | Ask |
| 5 | implementador-dotnet | `.github/agents/implementador-dotnet.agent.md` | Agent |
| 6 | qa-mvc | `.github/agents/qa-mvc.agent.md` | Agent |
| 7 | documentador | `.github/agents/documentador.agent.md` | Ask |

**Regla de oro:** no iniciar etapa hasta que la anterior haya cerrado su archivo de definición.

## Cursor

Ver `.cursor/README.md` para workspaces, skills (`/agentes-ia-*`) y rules.

Abrir siempre un `.code-workspace` en `C:/Sistemas/` que incluya este repo + el sistema bajo trabajo.

## Claude Code

Ver `.claude/README.md`. Entrada por rol:

- Slash commands (modo Ask, conversación actual): `/agentes-ia-orquestador`, `/agentes-ia-analista-funcional`, `/agentes-ia-disenador-funcional`, `/agentes-ia-arquitecto-mvc`, `/agentes-ia-presupuestador`, `/agentes-ia-documentador`.
- Subagents (modo Agent, contexto aislado): `agentes-ia-implementador` y `agentes-ia-qa` — los invoca el orquestador o se piden explícitamente.

Cada comando/subagent lee su `.github/agents/*.agent.md` (fuente de verdad) y carga sus instrucciones modulares al activarse. Equivalen a `@rol` de Copilot / `/agentes-ia-*` de Cursor.

## Cómo activar un agente en esta terminal

Para adoptar el rol de un agente específico, indicar explícitamente al inicio del pedido:
- `@analista-funcional` — discovery + análisis funcional
- `@disenador-funcional` — propuesta funcional de flujo y datos
- `@arquitecto-mvc` — diseño técnico por componentes y capas
- `@presupuesto-mvc` — estimación PERT, calibración y precio al cliente
- `@implementador-dotnet` — implementación segura en Agent mode
- `@qa-mvc` — pruebas funcionales en Agent mode
- `@documentador` — resumen de sprint para el cliente

Al activar un agente, leer primero su archivo `.github/agents/<nombre>.agent.md` para asumir el rol completo, incluyendo reglas, input esperado y salida mínima.

## Instrucciones modulares activas

Leer según el agente activo:

- `00-operativa-global` — reglas base para todo trabajo (siempre)
- `01-fronteras-por-capa` — separación Presentación / Negocio / Datos
- `10-blankproject-base` — stack .NET 10, Clean Architecture, MySQL
- `20-domain` — entidades, enums, soft delete, auditoría
- `21-application` — interfaces, DTOs, contratos
- `22-infrastructure` — EF Core, repositorios, servicios, health checks
- `23-web` — Controllers, Views, Middleware, ViewModels
- `24-config-paquetes` — configuración de paquetes NuGet
- `25-frontend-design-system` — SweetAlert2, DataTables, daterangepicker
- `26-checklists` — checklists por tipo de módulo
- `27-presupuesto-parametros` — rangos y parámetros de estimación
- `28-estimacion-avanzada` — método PERT y contingencia variable
- `29-trazabilidad-conversacion` — persistencia de memoria por agente
- `30-qa-regresiones` — regresiones y pruebas funcionales
- `31-formato-documento-cliente` — formato y estilo obligatorio de todo documento entregado al cliente (presupuesto, resumen de sprint)

## Trazabilidad documental

- Toda referencia a `/docs` apunta a `C:/Sistemas/Agentes-IA/docs/`
- Cada proyecto tiene carpeta propia en `docs/<proyecto>/definiciones/`
- Cada agente tiene un único archivo de memoria por proyecto — siempre editar el existente, nunca crear uno nuevo
- Registrar ajustes relevantes en `docs/<proyecto>/trazabilidad.md`
- Índice consolidado: `docs/indice.md`

## Reglas base (siempre aplican)

- Lógica de negocio: en Services, nunca en Controllers
- Controllers: solo coordinan request/response
- Acceso a datos: en DbContext, repositorios o infraestructura
- Toda modificación indica capas afectadas y motivo
- Si hay migración EF: explicitarla
- Si afecta permisos, estados o validaciones: listarlos
- No refactors cosméticos salvo pedido expreso
- Preservar comportamiento legacy salvo indicación contraria
- UI: SweetAlert2 para alertas, DataTables para listados, daterangepicker para rangos de fecha

## Proyectos activos

| Proyecto | Estado | Repo local |
|---|---|---|
| ShowroomGriffin | activo | `C:\Sistemas\ShowroomGriffin` |
| vinosefue | activo | `C:\Sistemas\vino-y-se-fue` |
| virtualwallet | abierto | `C:\Sistemas\virtualwallet` |
| ganaderia | QA pendiente | `C:\Sistemas\ganaderia` |
| contadores-bma-conversor | activo | `C:\Sistemas\Contadores BMA - Conversor` |
| century-21 | activo | `C:\Sistemas\Century 21` |

Ver `.github/copilot-instructions.md` para el detalle completo de items pendientes por proyecto.
