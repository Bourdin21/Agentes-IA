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
| subagent `agentes-ia-implementador` | Implementacion (ASP.NET Core MVC) | subagent | Agent |
| subagent `agentes-ia-implementador-astro-front` | Implementacion (sitios institucionales Astro) | subagent | Agent |
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

Sitio institucional estatico (Astro), sin backend de negocio — stack alternativo al MVC:

```
Usa el subagent agentes-ia-implementador-astro-front para construir el sitio institucional de <cliente>, siguiendo el patron de diercas-front.
```

## Agentes de negocio (Olvidata Soft)

Ademas de los agentes del flujo MVC, este repo aloja los agentes de negocio del estudio — no son parte de la secuencia Discovery→Cierre, se invocan sueltos:

| Comando | Rol |
|---|---|
| `/olvidata-ceo` | Estrategia, pricing, producto, pipeline, plan financiero |
| `/olvidata-marketing` | Frameworks de comunicacion, estrategia de canal, angulo editorial |
| `/olvidata-cm` | Community Manager — guiones de Reels, prompts de video IA (higgsfield.ai), carruseles, stories, captions |
| `/olvidata-sales` | Ejecucion de un deal puntual |
| `/olvidata-infra` | Servidores, SSL, dominios, application pools, bases de datos |
| `/olvidata-presupuesto-bot` | Matriz de modulos MVP/FULL del bot/CRM propio |

## Acceso global — junctions de Windows

Los agentes viven **solo aca** (unica copia, versionada en git), pero tienen que estar disponibles desde cualquier carpeta, no solo con el cwd en este repo. Eso se resuelve con dos junctions de Windows que apuntan la carpeta de usuario a este repo:

```
C:\Users\<usuario>\.claude\agents    ==>  C:\Sistemas\Agentes-IA\.claude\agents
C:\Users\<usuario>\.claude\commands  ==>  C:\Sistemas\Agentes-IA\.claude\commands
```

**Los junctions no viajan en git.** En una maquina nueva (o si se recrea el perfil), hay que rehacerlos — con las carpetas destino vacias o inexistentes:

```powershell
Remove-Item "$env:USERPROFILE\.claude\agents" -Force
Remove-Item "$env:USERPROFILE\.claude\commands" -Force
cmd /c mklink /J "$env:USERPROFILE\.claude\agents"   "C:\Sistemas\Agentes-IA\.claude\agents"
cmd /c mklink /J "$env:USERPROFILE\.claude\commands" "C:\Sistemas\Agentes-IA\.claude\commands"
```

`mklink /J` (junction de directorio) no requiere permisos de administrador, a diferencia de los symlinks de archivo.

## Memorias

`.claude/memorias/<proyecto>/` es una **copia versionada** de las memorias que Claude Code guarda en `~/.claude/projects/<proyecto>/memory/`. No es la ruta operativa: el harness lee y escribe siempre en la carpeta de usuario, esta copia existe como respaldo en git. Refrescarla cada tanto:

```bash
find "$USERPROFILE/.claude/projects" -maxdepth 2 -type d -name memory | while read d; do
  proj=$(basename "$(dirname "$d")")
  [ -n "$(ls -A "$d")" ] && mkdir -p ".claude/memorias/$proj" && cp -r "$d/." ".claude/memorias/$proj/"
done
```

**Nunca versionar** `~/.claude/settings.json` sin sanear: guarda reglas de permiso que pueden incluir credenciales de produccion en texto plano. Tampoco `~/.claude/projects/*/*.jsonl` (transcripts de sesion, cientos de MB, los administra la herramienta).

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
