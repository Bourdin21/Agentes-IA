# Claude Code — Agentes-IA

Punto de entrada para usar los agentes del estudio desde **Claude Code** (terminal / VSCode).
Fuente de verdad de cada rol: `.github/agents/*.agent.md` (no se duplica logica aca).

## Como se activa cada agente

| Comando / accion | Rol | Mecanismo | Modo |
|---|---|---|---|
| `/agentes-ia-orquestador` | Flujo completo E2E | slash command | Ask + Agent |
| `/agentes-ia-analista-funcional` | Discovery + analisis | slash command | Ask |
| `/agentes-ia-disenador-funcional` | Diseño funcional | slash command | Ask |
| `/agentes-ia-arquitecto-mvc` | Arquitectura tecnica | slash command | Ask |
| `/agentes-ia-presupuestador` | Presupuesto PERT | slash command | Ask |
| `/agentes-ia-documentador` | Resumen para cliente | slash command | Ask |
| subagent `agentes-ia-implementador` | Implementacion | subagent | Agent |
| subagent `agentes-ia-qa` | Pruebas funcionales | subagent | Agent |

- **Slash commands** (`.claude/commands/`): corren en la conversacion actual. Los invocas con `/` + tus indicaciones, igual que `@rol` en Copilot. Mantienen el ida y vuelta interactivo.
- **Subagents** (`.claude/agents/`): contexto aislado, trabajan solos y devuelven un resumen. Los invoca el orquestador, o los pedis explicitamente: "usa el subagent agentes-ia-implementador para ...".

## Ejemplos

```
/agentes-ia-analista-funcional Proyecto: ShowroomGriffin — el cliente quiere reservar prendas del showroom por 48hs
```

```
/agentes-ia-orquestador Proyecto: vinosefue — nueva feature: alta de promociones por rango de fechas
```

Implementacion (subagent, tras aprobar presupuesto):

```
Usa el subagent agentes-ia-implementador para implementar la feature aprobada en ShowroomGriffin.
```

## Reglas siempre activas

`CLAUDE.md` (raiz del repo) se carga en cada sesion — cumple el rol de la operativa global.
Cada agente ademas lee al activarse las instrucciones modulares que le corresponden de `.github/instructions/` (Claude Code no tiene auto-inject por glob como los `.mdc` de Cursor; el scoping por capa lo hace cada agente al leer su instruccion).

## Workspace

Abrir Claude Code apuntado a `C:/Sistemas/` (o abrir el repo del sistema con `C:/Sistemas/Agentes-IA` como carpeta adicional) para que los agentes lean definiciones aca y editen codigo en el repo del sistema.

## Proyecto nuevo

1. Copiar `docs/templates/proyecto/` → `docs/<proyecto>/`.
2. Iniciar con `/agentes-ia-orquestador Proyecto: <nombre> — <feature>`.

## Equivalencia Copilot → Cursor → Claude Code

| Copilot | Cursor | Claude Code |
|---|---|---|
| `@analista-funcional` | `/agentes-ia-analista-funcional` | `/agentes-ia-analista-funcional` |
| `@implementador` (Agent) | `/agentes-ia-implementador` | subagent `agentes-ia-implementador` |
| `copilot-instructions.md` + rules | `.cursor/rules/*.mdc` | `CLAUDE.md` + lectura de `.github/instructions/` por agente |
| `.github/agents/*.agent.md` | Skills que leen el `.agent.md` | Commands/subagents que leen el `.agent.md` |
