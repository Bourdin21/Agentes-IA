# AGENTS.md

Contexto de proyecto para cualquier agente de codigo que trabaje sobre este repositorio
(Claude Code, Codex, Copilot, Cursor u otro). Es el punto de entrada portable: la fuente
de verdad de cada regla vive en los archivos que este documento apunta, no aca.

- Entrada especifica de Claude Code: `CLAUDE.md` y `.claude/README.md`
- Entrada especifica de Copilot: `.github/copilot-instructions.md`
- Entrada especifica de Cursor: `.cursor/README.md`

## Que es este repositorio

**No es una aplicacion.** Es el *harness* de los agentes del estudio Olvidata Soft: la
memoria de trabajo, las instrucciones y las definiciones de rol con las que se construyen
y mantienen los sistemas de los clientes. Los sistemas reales viven en otros repositorios
(la ruta de cada uno esta en `docs/<proyecto>/metadata.md`, campo `ruta_repositorio`).

Consecuencia practica: **cambiar un archivo de `.github/instructions/` cambia el
comportamiento de un sistema en produccion.** Se trata con el mismo cuidado que el codigo.

## Como se trabaja

Secuencia obligatoria por feature:

```
Discovery -> Analisis -> Diseño -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas -> Documentacion -> Cierre de calibracion
```

Reglas de etapa:

1. Cada etapa cierra su archivo en `docs/<proyecto>/definiciones/` **antes** de pasar a la siguiente.
2. Ninguna etapa arranca sin la anterior aprobada.
3. **La etapa siguiente arranca en un contexto nuevo**, cargado desde ese archivo y desde
   un brief comprimido — no se continua en el contexto de la anterior, y no se compacta el
   historial para seguir (`.github/instructions/39-presupuesto-contexto.instructions.md`, seccion 4b).

Los roles estan definidos en `.github/agents/*.agent.md` (fuente de verdad) y expuestos
como subagentes/slash commands en `.claude/agents/` y `.claude/skills/`.

## Reglas que aplican a todo cambio de codigo

De `.github/instructions/00-operativa-global` y `01-fronteras-por-capa`:

- Logica de negocio en **Services**, nunca en Controllers.
- Controllers: solo coordinan request/response.
- Acceso a datos en DbContext, repositorios o infraestructura.
- Toda modificacion declara las capas afectadas y el motivo.
- Migraciones EF: explicitarlas siempre, con el nombre exacto.
- Cambios en permisos, estados o validaciones: listarlos.
- Nada de refactors cosmeticos salvo pedido expreso; se preserva el comportamiento legacy.

Stack por defecto: ASP.NET Core MVC + EF Core + MySQL (.NET 10, Clean Architecture).
UI: SweetAlert2 para alertas, DataTables para listados, daterangepicker para rangos,
maskMoney para importes.

## Antes de construir algo nuevo: buscar el antecedente

Obligatorio en Diseño, Arquitectura e Implementacion, y **barato** si se hace en este orden:

1. `docs/patrones/cat_resumen.txt` — una linea por patron. Primer lookup, siempre.
2. Si hay match: leer **solo** esa entrada de `docs/patrones/catalogo.yml`, y despues el
   codigo real en el repo de origen.
3. Si no hay match: `grep -ril "<entidad o flujo>" docs/*/definiciones/` y leer **solo** la
   seccion que matchea.
4. Recien ahi: declarar "sin antecedente" y construir nuevo — agregando el patron al
   catalogo antes de cerrar la etapa.

Nunca leer las definiciones del historial por cuerpo completo: son 7,5 MB.

## Presupuesto de contexto (no es opcional)

Un agente que arranca con media ventana gastada en historia ajena a la tarea razona peor.
Medicion del 2026-09-25: el QA sobre un proyecto maduro cargaba **2,05 MB (~510k tokens)**
antes de abrir el sistema.

- Techo de arranque: 40k tokens (analista, diseñador, documentador), 50k (arquitecto),
  60k (presupuestador, implementadores, QA). Se mide con `python scripts/contexto.py presupuesto <proyecto>`.
- Los archivos grandes se leen **por indice**, nunca enteros: `python scripts/contexto.py indice <alias>`.
- Ningun archivo de memoria pasa de **150 KB**; lo cerrado se archiva con `scripts/archivar_memoria.py`.

Detalle completo: `.github/instructions/39-presupuesto-contexto.instructions.md`.

## Separacion de roles: quien construye no califica

- El **Implementador** escribe codigo. No ejecuta la aplicacion ni se autocalifica.
- El **QA** prueba y califica. **El repo del sistema bajo prueba es read-only para el:**
  no aplica fixes, emite *partes de defecto*. Todo criterio arranca en **FAIL** y solo pasa
  con evidencia observada.
- Un defecto no se cierra en la misma corrida que lo encontro, ni lo cierra quien lo arreglo.

Contrato completo: `.github/instructions/30-qa-regresiones.instructions.md`.

## Memoria: entradas con id, no reescritura

Cada dato vigente vive en una **entrada con id propio** (`CR-80`, `MH-023`, `PAT-017`).
Una definicion que reemplaza a otra **no pisa su texto**: nace con id nuevo y la vieja se
marca `superada-por: <id>`. La poda es un paso explicito (`scripts/archivar_memoria.py`),
nunca el efecto colateral de reescribir — reescribir erosiona el detalle de dominio.

Detalle: `.github/instructions/29-trazabilidad-conversacion.instructions.md`.

## Scripts

| Comando | Para que |
|---|---|
| `python scripts/doctor.py [--fast]` | consistencia de la memoria: precios contradictorios, ids duplicados, archivos sobre el techo, indices desactualizados. **Correr antes de cerrar cualquier etapa** |
| `python scripts/contexto.py presupuesto \| indice \| resumenes` | arranque por agente vs. su techo, indices de archivos grandes, regeneracion de los `cat_resumen.txt` |
| `python scripts/archivar_memoria.py <archivo> [--aplicar]` | mueve sprints/CR cerrados a `historial/` para sostener el techo de 150 KB |
| `python scripts/traza.py registrar \| resumen` | traza de corrida al cerrar una etapa: reintentos, criterios fallados, reglas releidas |
| `python scripts/evals.py validar \| costo \| preparar \| gradear` | suite de evals del harness. **`costo` antes de correr: gasta tokens de verdad** |

## Convenciones de escritura

- Castellano rioplatense, de vos, en interfaz, logs, documentacion y commits.
- Los archivos de `.github/instructions/` y `docs/` estan en ASCII sin acentos por
  compatibilidad historica de herramientas; los documentos al cliente, no.
- Commits: que hizo y por que, citando el id del CR/patron/regresion cuando aplique.

## Que NO hacer

- No crear un archivo nuevo de memoria para un agente que ya tiene el suyo en
  `docs/<proyecto>/definiciones/`. Siempre se edita el existente.
- No duplicar el estado de los proyectos: la fuente unica es `docs/indice.md`.
- No `cat` de `docs/qa/regresiones-manuales.yml` (424 KB) ni de `docs/patrones/catalogo.yml`
  (184 KB): se entra por sus `cat_resumen.txt`.
- No correr evals sin mirar antes `python scripts/evals.py costo`.
- No ejecutar ninguna accion con costo real (tokens, campañas, servicios pagos) sin mostrar
  el costo y esperar confirmacion explicita.
