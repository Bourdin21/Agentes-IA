---
applyTo: "**"
---

# 30 - QA: catalogo de regresiones manuales

## Fuente unica
- Archivo de datos: `docs/qa/regresiones-manuales.yml`
- README humano: `docs/qa/README.md`

Este catalogo es **autoritario** para regresiones funcionales reproducidas manualmente. Cualquier bug funcional corregido debe quedar registrado alli antes del merge.

**Alcance (2026-08-20):** esta obligacion no depende del modo de trabajo. Aplica igual si el fix salio del flujo formal de subagentes (orquestador -> implementador -> QA) o de una sesion de chat directa sobre un proyecto ya en produccion (ej. Claude Code respondiendo pedidos del cliente sobre un repo existente, sin pasar por `agentes-ia-implementador`/`agentes-ia-qa`). El criterio es el bug y su generalizacion, no quien lo corrigio.

## Obligaciones del agente Implementador

Cuando arregles un bug funcional reproducido manualmente:

1. Agregar o actualizar un item en `docs/qa/regresiones-manuales.yml` con todos los campos requeridos:
   - `id`, `modulo`, `titulo`, `severidad`, `pasos`, `sintoma`, `expectativa`, `causa_raiz`, `capa`, `archivos_fix`, `migracion_ef`, `deteccion_qa`, `criterio_aceptacion`, `pruebas_minimas`.
2. Si el fix involucra migracion EF, completar `migracion_ef` con el nombre exacto.
3. No borrar ids existentes; en caso de invalidar, marcar `severidad: deprecated`.
4. Mantener el archivo en YAML 1.2, sin tabs, claves en ASCII puro.

## Obligaciones del agente QA

Antes de aprobar un build:

1. Cargar `docs/qa/regresiones-manuales.yml`.
2. Para cada item con `severidad != deprecated`:
   - Ejecutar `deteccion_qa` segun su `tipo` (api | data | static) de forma automatica.
   - Para items con `tipo: ui` **(actualizado 2026-08-14): automatizar por navegador** siguiendo `33-verificacion-automatizada-qa.instructions.md` — reproducir los `pasos` del item con la herramienta de automatizacion disponible y evaluar `condicion_falla` sobre el resultado real. Solo si el caso queda fuera del alcance automatizable (ver esa instruccion para los criterios de exclusion), describir el procedimiento de prueba manual paso a paso para que el usuario lo ejecute a mano y reporte PASS/FAIL.
   - Si se cumple `condicion_falla` (confirmado por automatizacion o por el reporte manual del usuario), reportar regresion citando el `id`.
   - Validar `criterio_aceptacion` y correr `pruebas_minimas`.
3. Reportar resultado consolidado por `id`.
4. **Parte de defecto obligatorio (reemplaza al auto-fix, 2026-09-25)**:
   - Cuando se reproduce una regresion, el agente QA **no aplica el parche**. Emite un parte de defecto con: `id` del catalogo, severidad, pasos de reproduccion, **evidencia observada**, `archivos_fix` + `migracion_ef` sugeridos (como hipotesis) y el **criterio de re-verificacion** que va a decidir el PASS.
   - Si el item no esta catalogado todavia, crearlo en `docs/qa/regresiones-manuales.yml` antes de emitir el parte. Escribir el catalogo si es tarea de QA: es memoria del estudio, no el sistema del cliente.
   - Registrar el parte en `/docs/<proyecto>/definiciones/6-qa.md` (memoria del agente QA).
   - Si la causa raiz es ambigua, declararlo y escalar con la evidencia, en lugar de adivinar el parche.
   - **Ciclo de cierre:** QA reporta -> Implementador aplica -> QA re-verifica en una corrida posterior, con contexto nuevo y el criterio de vuelta en FAIL. Un defecto no se cierra en la misma corrida que lo encontro, ni lo cierra quien lo arreglo.

## Contrato de evaluacion independiente (2026-09-25)

Motivo del cambio: hasta esta fecha el mismo agente que arreglaba el bug era el que despues lo calificaba (auto-fix + reporte PASS). Es el problema que Anthropic documento construyendo aplicaciones largas — el generador elogia su propio trabajo — y lo teniamos por diseño.

Reglas duras:

1. **QA no escribe en el repo del sistema bajo prueba.** Lo lee, lo compila, lo levanta y lo navega; no lo edita. Su unica escritura es sobre `Agentes-IA/docs/` (memoria del rol, `trazabilidad.md`, catalogo de regresiones).
2. **Default-FAIL:** todo criterio de aceptacion, item del catalogo y regla cross-proyecto **arranca en FAIL**. Solo pasa a PASS con evidencia observada (respuesta HTTP, texto en pantalla, fila en la BD, snapshot). Inferencia desde el codigo, palabra del implementador o ausencia de sintomas **no** son evidencia.
3. **Criterio no testeable = BLOCKED**, no PASS: vuelve al analista para que lo reescriba como assertion observable.
4. **Contexto fresco:** QA no arranca con la transcripcion de la construccion. Se entera de lo que se hizo por los artefactos (`5-implementador.md` del sprint, diff), no por el razonamiento del que lo hizo.
5. **Verificacion mecanica:** al cerrar, QA corre `git status --porcelain` en el repo del sistema y declara en su salida que no dejo cambios propios.

## Obligaciones del agente Implementador frente a un parte de defecto

1. Aplicar el fix del parte respetando las fronteras por capa, sin re-litigar el diagnostico salvo que tenga evidencia de que el parte esta mal.
2. Dejar el `id` del catalogo en el mensaje de commit y en su bloque de `5-implementador.md`.
3. **No marcar el defecto como cerrado.** El cierre lo declara QA en la corrida siguiente. El Implementador declara "aplicado, pendiente de re-verificacion".

## Reutilizacion cross-proyecto del catalogo

El catalogo es **transversal**: aunque cada item se reprodujo en un proyecto puntual, sus pasos describen patrones funcionales que se repiten en cualquier sistema MVC + EF Core + MySQL del baseline BlankProject (variantes/stock, compras, ventas, devoluciones, aumento masivo, sidebar/permisos, etc.).

Cuando el agente QA valida un **sistema nuevo** (primera entrada del proyecto a la etapa de QA):

1. Cargar `docs/qa/regresiones-manuales.yml` como **playbook funcional minimo** ademas de los criterios del analista funcional propios del proyecto.
2. Para cada `id` con `severidad != deprecated`:
   - Mapear el `modulo` del catalogo al modulo equivalente del sistema bajo prueba (ej. "Variantes/Stock" -> modulo de stock del nuevo proyecto). Si no hay equivalente, marcar el item como `N/A para este proyecto` con justificacion en el reporte.
   - Replicar los `pasos` manuales en la UI/API del sistema nuevo.
   - Aplicar `deteccion_qa.condicion_falla` adaptando el `selector_o_endpoint` al nuevo proyecto.
   - Si reproduce el bug, activar el flujo de **auto-fix obligatorio** descripto arriba, citando el `id` original como antecedente.
3. El reporte QA del sistema nuevo debe incluir una seccion **"Cobertura del catalogo cross-proyecto"** con una tabla `id | aplica (si/no/N/A) | resultado | accion`.
4. Cualquier bug nuevo detectado en la prueba manual del sistema nuevo que no este en el catalogo debe registrarse alli (con un `id` nuevo) antes del cierre del gate QA, para que quede disponible al siguiente proyecto.

## Reglas de borde

- Solo se registran bugs **funcionales** reproducidos. No usar este catalogo para tareas, mejoras o refactors.
- Cada item debe ser ejecutable de forma independiente (sin orden implicito).
- Los `selector_o_endpoint` deben ser estables; si cambian, actualizar el item en el mismo PR.
- El parte de defecto de QA **no exime** al Implementador de su obligacion de catalogar bugs corregidos en su propio flujo: ambos agentes mantienen el catalogo.
- Un `id` reportado en FAIL dos corridas seguidas escala: deja de ser un bug de implementacion y pasa a revisarse como problema de diseño o de criterio.
- Si el sistema bajo prueba no usa MySQL/EF Core, marcar como `N/A` los items cuya `causa_raiz` dependa exclusivamente de ese stack (ej. RowVersion MySQL).
