# Cursor — Agentes-IA

Configuración para usar los 7 agentes del estudio desde Cursor.

## Abrir workspace (obligatorio)

Usá un archivo `.code-workspace` en `C:/Sistemas/` que incluya **el repo del sistema + Agentes-IA**:

| Proyecto | Workspace |
|---|---|
| ShowroomGriffin | `C:/Sistemas/ShowroomGriffin.code-workspace` |
| vinosefue | `C:/Sistemas/vinosefue.code-workspace` |
| virtualwallet | `C:/Sistemas/virtualwallet.code-workspace` |
| ganaderia | `C:/Sistemas/ganaderia.code-workspace` |
| Century 21 | `C:/Sistemas/Century21.code-workspace` |
| contadores-bma-conversor | `C:/Sistemas/contadores-bma-conversor.code-workspace` |
| labipac | `C:/Sistemas/labipac.code-workspace` |
| decorhogar | `C:/Sistemas/decorhogar.code-workspace` |

En Cursor: **File → Open Workspace from File…**

## Skills (comandos `/`)

| Comando | Rol | Modo |
|---|---|---|
| `/agentes-ia-analista-funcional` | Discovery + análisis | Ask |
| `/agentes-ia-disenador-funcional` | Diseño funcional | Ask |
| `/agentes-ia-arquitecto-mvc` | Arquitectura técnica | Ask |
| `/agentes-ia-presupuestador` | Presupuesto PERT | Ask |
| `/agentes-ia-implementador` | Implementación | **Agent** |
| `/agentes-ia-qa` | Pruebas funcionales | **Agent** |
| `/agentes-ia-documentador` | Resumen para cliente | Ask |
| `/agentes-ia-orquestador` | Flujo completo E2E | Ask + Agent |

Ejemplo:

```
/agentes-ia-implementador
Proyecto: ShowroomGriffin
Implementá [feature] según definiciones aprobadas.
```

## Rules (automáticas)

| Archivo | Cuándo aplica |
|---|---|
| `operativa-global.mdc` | Siempre |
| `capa-web.mdc` | Archivos Web/Controllers/Views |
| `capa-domain-app-infra.mdc` | Domain/Application/Infrastructure |
| `presupuesto.mdc` | Manual / etapa presupuesto |
| `qa-regresiones.mdc` | Al editar `6-qa.md` |

## Proyecto nuevo

1. Copiar `docs/templates/proyecto/` → `docs/<proyecto>/`
2. Copiar `docs/templates/proyecto/.cursor/` → repo del sistema
3. Crear `C:/Sistemas/<proyecto>.code-workspace` con dos carpetas
4. Iniciar con `/agentes-ia-orquestador`

## Equivalencia Copilot → Cursor

| Copilot | Cursor |
|---|---|
| `@analista-funcional` | `/agentes-ia-analista-funcional` |
| `chat.instructionsFilesLocations` | `.cursor/rules/*.mdc` |
| `.github/agents/*.agent.md` | Skills + lectura del `.agent.md` |

Definiciones canónicas de agentes: `.github/agents/*.agent.md` (sin duplicar lógica en skills).
