---
applyTo: "**"
---

# 30 - QA: catalogo de regresiones manuales

## Fuente unica
- Archivo de datos: `docs/qa/regresiones-manuales.yml`
- README humano: `docs/qa/README.md`

Este catalogo es **autoritario** para regresiones funcionales reproducidas manualmente. Cualquier bug funcional corregido debe quedar registrado alli antes del merge.

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
   - Ejecutar `deteccion_qa` segun su `tipo` (ui | api | data | static).
   - Si se cumple `condicion_falla`, reportar regresion citando el `id`.
   - Validar `criterio_aceptacion` y correr `pruebas_minimas`.
3. Reportar resultado consolidado por `id`.
4. **Auto-fix obligatorio cuando se reproduce un bug detectado en prueba manual**:
   - Si la regresion fue confirmada manualmente (humano reporto el sintoma o `deteccion_qa` la confirmo), el agente QA debe:
     1. Aplicar el parche derivado de `archivos_fix` y `migracion_ef`, respetando las fronteras por capa.
     2. Si el item no esta catalogado todavia, crearlo en `docs/qa/regresiones-manuales.yml` antes de proponer el fix.
     3. Re-ejecutar `deteccion_qa` y `pruebas_minimas` post-parche para confirmar cierre.
     4. Registrar el resultado en `/docs/<proyecto>/definiciones/6-qa.md` (memoria del agente QA).
   - El auto-fix no debe re-implementar logica de negocio nueva: se limita a replicar la solucion ya validada en el catalogo.
   - Si la causa raiz es ambigua o no hay item catalogado, escalar al agente Implementador con la evidencia, en lugar de adivinar el parche.

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
- El auto-fix de QA **no exime** al Implementador de su obligacion de catalogar bugs corregidos en su propio flujo: ambos agentes mantienen el catalogo.
- Si el sistema bajo prueba no usa MySQL/EF Core, marcar como `N/A` los items cuya `causa_raiz` dependa exclusivamente de ese stack (ej. RowVersion MySQL).
