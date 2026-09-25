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

### Stacks alternativos al MVC

El rol #5 (implementador) tiene una variante por stack — la secuencia 1-4 y 7 (análisis/diseño/arquitectura/presupuesto/documentación) es genérica y sirve igual; lo que cambia es quién codifica:

| Stack | Reemplaza a | Archivo |
|---|---|---|
| ASP.NET Core MVC + EF Core + MySQL (default) | — | `.github/agents/implementador-dotnet.agent.md` |
| Sitio institucional estático (Astro + Tailwind, sin backend de negocio) | implementador-dotnet | `.github/agents/implementador-astro-front.agent.md` |

Precedente: `diercas-front` (ver `docs/diercas/`), primer proyecto del estudio en este stack alternativo.

## Cursor

Ver `.cursor/README.md` para workspaces, skills (`/agentes-ia-*`) y rules.

Abrir siempre un `.code-workspace` en `C:/Sistemas/` que incluya este repo + el sistema bajo trabajo.

## Claude Code

Ver `.claude/README.md`. Entrada por rol:

- Slash commands (modo Ask, conversación actual): `/agentes-ia-orquestador`, `/agentes-ia-analista-funcional`, `/agentes-ia-disenador-funcional`, `/agentes-ia-arquitecto-mvc`, `/agentes-ia-presupuestador`, `/agentes-ia-documentador`.
- Subagents (modo Agent, contexto aislado): `agentes-ia-implementador` (MVC), `agentes-ia-implementador-astro-front` (sitios estáticos Astro) y `agentes-ia-qa` — los invoca el orquestador o se piden explícitamente.

Cada comando/subagent lee su `.github/agents/*.agent.md` (fuente de verdad) y carga sus instrucciones modulares al activarse. Equivalen a `@rol` de Copilot / `/agentes-ia-*` de Cursor.

Este repo aloja ademas los **agentes de negocio de Olvidata Soft** (`/olvidata-ceo`, `/olvidata-marketing`, `/olvidata-cm`, `/olvidata-sales`, `/olvidata-infra`, `/olvidata-presupuesto-bot`) — fuera de la secuencia Discovery→Cierre, se invocan sueltos. Detalle y setup de acceso global en `.claude/README.md`.

## Cómo activar un agente en esta terminal

Para adoptar el rol de un agente específico, indicar explícitamente al inicio del pedido:
- `@analista-funcional` — discovery + análisis funcional
- `@disenador-funcional` — propuesta funcional de flujo y datos
- `@arquitecto-mvc` — diseño técnico por componentes y capas
- `@presupuesto-mvc` — estimación PERT, calibración y precio al cliente
- `@implementador-dotnet` — implementación segura en Agent mode (ASP.NET Core MVC)
- `@implementador-astro-front` — implementación de sitios institucionales estáticos en Agent mode (Astro, sin backend de negocio)
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
- `25-frontend-design-system` — SweetAlert2, DataTables, daterangepicker, maskMoney (importes)
- `26-checklists` — checklists por tipo de módulo
- `27-presupuesto-parametros` — rangos y parámetros de estimación
- `28-estimacion-avanzada` — método PERT y contingencia variable
- `29-trazabilidad-conversacion` — persistencia de memoria por agente
- `30-qa-regresiones` — regresiones y pruebas funcionales
- `31-formato-documento-cliente` — formato y estilo obligatorio de todo documento entregado al cliente (presupuesto, resumen de sprint)
- `32-estandares-qa-implementador` — estandares de implementacion derivados del barrido de errores QA cross-proyecto
- `34-integracion-afip-arca` — circuito completo de facturacion electronica AFIP/ARCA (WSAA, certificado, WSFEv1, Notas de Credito), depurado contra produccion real
- `35-pantalla-control-stock` — patron de pantalla de control de stock/inventario (listado editable inline vs. formulario de ajuste)
- `36-metodologia-pacs` — growth B2B para agentes comerciales de Olvidata (nicho → autoridad → mensaje conversacional → sistematizacion); objetivo: reuniones agendadas
- `33-verificacion-automatizada-qa` — QA ejecuta verificacion automatizada por navegador para casos objetivamente chequeables (catalogo de regresiones + estandares 32 + criterios de aceptacion criticos); el resto sigue siendo manual
- `37-servicios-externos-fiscales` — consumo de servicios fiscales externos (padrones, constancias, validaciones)
- `38-diseno-pantallas-portal` — decisiones de diseño de las pantallas del portal del usuario final
- `39-presupuesto-contexto` — **techo de contexto por agente, carga por indice, techo de 150 KB por archivo de memoria, hand-off comprimido y QA por lotes (siempre)**

## Presupuesto de contexto (obligatorio, `39-presupuesto-contexto`)

Un agente que arranca con media ventana de contexto gastada en historia ajena a la tarea razona peor. Medicion del 2026-09-25: el QA sobre marihogar cargaba **2,05 MB (~510k tokens)** antes de abrir el sistema, y el implementador 621 KB. Reglas vigentes desde entonces:

- **Techo de arranque** (sale de cuantos documentos de etapa previa necesita cada rol, no de una fraccion de la ventana): 40k tokens (analista, diseñador, documentador), 50k (arquitecto), 60k (presupuestador, implementadores y QA). Medirlo con `python scripts/contexto.py presupuesto <proyecto>`.
- **Carga por indice, no por cuerpo:** las instructions grandes (`27`, `32`, `25`, `34`, `35`, `37`) se leen por seccion — `python scripts/contexto.py indice <alias>`. El catalogo de regresiones entra por `docs/qa/cat_resumen.txt` (24 KB) y el de patrones por `docs/patrones/cat_resumen.txt`, no por los YAML de 424 y 184 KB (`python scripts/contexto.py resumenes` los regenera).
- **El escaneo de reutilizacion cross-proyecto sigue siendo obligatorio, pero barato:** `cat_resumen.txt` → entrada del catalogo si hay match → `grep -ril` dirigido sobre `docs/*/definiciones/` → recien entonces "sin antecedente". Nunca leer las definiciones del historial por cuerpo completo (son 7,5 MB).
- **Techo de 150 KB por archivo de memoria** (`definiciones/*.md` y `trazabilidad.md`): al cerrar una etapa, los sprints/CR/modulos cerrados se archivan con `python scripts/archivar_memoria.py <archivo> --aplicar`, que los mueve agrupados a `historial/` y deja un puntero de una linea por grupo. `doctor.py` lo vigila.
- **Hand-off comprimido:** el orquestador delega con un brief de <= 2 paginas (alcance, criterios, decisiones cerradas, punteros con numero de linea), no con "lee las definiciones".
- **QA por lotes:** a lo sumo 3 modulos por corrida (1 si es financiero o integracion), un subagente por lote, reporte de <= 40 lineas, y el orquestador consolida.

## Skills (carga bajo demanda)

Las instrucciones modulares de arriba son la **fuente completa**; las skills de `.claude/skills/` son el indice fino que se carga solo cuando hace falta (al inicio solo entra su descripcion, el cuerpo recien al invocarse). No duplican contenido: apuntan al archivo de instrucciones y dicen que seccion leer.

| Skill | Cubre | Se activa con |
|---|---|---|
| `estandares-qa` | catalogo de bugs recurrentes (32 + regresiones) | archivos `.cs` / `.cshtml` |
| `presupuesto-parametros` | tasa, factores, rangos, descuentos (27 + dataset) | invocacion explicita |
| `design-system` | vistas MVC, DataTables, Select2, importes (25) | vistas, css, js |
| `checklists-modulo` | checklists de salida por tipo de trabajo (26) | archivos `.cs` / `.cshtml` |
| `memoria-documental` | donde va cada dato, regla vigente vs. historial (29) | archivos de `docs/` |

## Chequeo de consistencia (`scripts/doctor.py`)

`python scripts/doctor.py` verifica en segundos que la memoria no se haya desincronizado: numeros de precio contradictorios entre archivos, estado de proyecto declarado fuera de `docs/indice.md`, IDs de regla duplicados, cierres reales que quedaron sin cargar en `docs/calibracion/dataset.yml`, **archivos de memoria sobre el techo de 150 KB**, **indices planos (`cat_resumen.txt`) desactualizados respecto de su catalogo**, archivos de mas de 300 KB y huerfanos. `--fast` corre solo los chequeos baratos (incluye el techo de memoria).

Los otros dos scripts: `python scripts/contexto.py` (presupuesto de arranque por agente, indices de los archivos grandes, regeneracion de los `cat_resumen.txt`) y `python scripts/archivar_memoria.py` (mueve los sprints/CR/modulos cerrados a `historial/` para mantener el techo; dry-run por defecto, `--aplicar` para hacerlo).

Esta enganchado a 3 hooks (`.claude/settings.json` -> `.claude/hooks/hook_doctor.py`): avisa al editar `docs/` o `.github/`, al abrir sesion y al terminar si quedaron muchos cambios sin commitear. **Errores** (rojo) son contradicciones que hay que arreglar; **avisos** son deuda documental. Corre tambien antes de dar por cerrada cualquier etapa.

## Trazabilidad documental

- Toda referencia a `/docs` apunta a `C:/Sistemas/Agentes-IA/docs/`
- Cada proyecto tiene carpeta propia en `docs/<proyecto>/definiciones/`
- Cada agente tiene un único archivo de memoria por proyecto — siempre editar el existente, nunca crear uno nuevo
- Ese archivo no pasa de **150 KB**: los sprints/CR/módulos cerrados se archivan en `docs/<proyecto>/definiciones/historial/` (y `docs/<proyecto>/historial/` para trazabilidad) con `scripts/archivar_memoria.py`, dejando un puntero de una línea por grupo. El archivo vigente es el estado actual, no el diario completo
- Registrar ajustes relevantes en `docs/<proyecto>/trazabilidad.md`
- Índice consolidado: `docs/indice.md`

## Reglas base (siempre aplican)

- Reutilización cross-proyecto: en Diseño, Arquitectura e Implementación, consultar primero `docs/patrones/cat_resumen.txt` (índice plano, una línea por patrón) y leer del `catalogo.yml` solo la entrada que matchea; si no hay match, `grep -ril "<entidad o flujo>" docs/*/definiciones/` y leer solo la sección que matchea, antes de proponer algo nuevo — si la funcionalidad ya fue diseñada/implementada en otro proyecto, reutilizar y adaptar ese diseño/código (ver `ruta_repositorio` en el `metadata.md` de origen, o completar la ruta en `catalogo.yml` si estaba pendiente) en vez de construir desde cero. Nunca leer las definiciones del historial por cuerpo completo (ver `39-presupuesto-contexto`). Todo patrón reutilizable nuevo se agrega al catálogo antes de cerrar la etapa.
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

**Fuente unica de estado de proyectos: `docs/indice.md`.** Ahi vive, por proyecto, el estado real (activo / cerrado / en produccion), la URL productiva, el repo local y el ultimo hito. No duplicar esa tabla aca ni en `.github/copilot-instructions.md`: cada copia se desincronizo (auditoria 2026-09-15 — ganaderia figuraba a la vez como "QA pendiente" y "en produccion").

- Estado y repo de cada proyecto: `docs/indice.md`
- Metadata propia de cada uno (owner, hosting, `ruta_repositorio`): `docs/<proyecto>/metadata.md`
- Historial de decisiones: `docs/<proyecto>/trazabilidad.md`
