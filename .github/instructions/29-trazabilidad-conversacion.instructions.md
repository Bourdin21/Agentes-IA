---
description: Trazabilidad documental obligatoria por proyecto en carpeta /docs del repositorio Agentes-IA.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Objetivo
- Mantener memoria acumulativa de trabajo por proyecto y por agente.
- Cada agente tiene un unico archivo por proyecto que se actualiza en cada conversacion.
- Nunca crear un archivo nuevo para el mismo agente y proyecto: siempre editar el existente.

# Contexto de uso
- Este repositorio (Agentes-IA) es compartido por multiples proyectos.
- La memoria de trabajo se guarda aqui, organizada por nombre de proyecto.
- Cada proyecto tiene su propia carpeta bajo /docs con definiciones separadas por agente.

# Estructura obligatoria
- /docs/indice.md
- /docs/<proyecto>/metadata.md
- /docs/<proyecto>/trazabilidad.md
- /docs/<proyecto>/definiciones/1-analista-funcional.md
- /docs/<proyecto>/definiciones/2-disenador-funcional.md
- /docs/<proyecto>/definiciones/3-arquitecto-mvc.md
- /docs/<proyecto>/definiciones/4-presupuestador.md
- /docs/<proyecto>/definiciones/5-implementador.md
- /docs/<proyecto>/definiciones/6-qa.md
- /docs/<proyecto>/definiciones/7-documentador.md

# Regla de memoria acumulativa por agente
- Cada agente edita su archivo existente en /docs/<proyecto>/definiciones/ al trabajar en ese proyecto.
- Si el archivo no existe todavia, crearlo desde la plantilla en /docs/templates/proyecto/definiciones/.
- No crear archivos duplicados para el mismo agente dentro del mismo proyecto.

## Regla de edicion: entradas con id, no reescritura del bloque (actualizada 2026-09-25)

Cada archivo de `definiciones/` tiene exactamente 2 zonas, nunca mas de 2 encabezados de nivel 2 con este rol:

- **`## Definiciones vigentes`** (o el heading equivalente ya presente en el archivo, ej. `## Version actual`): es el estado actual. Es **un conjunto de entradas identificadas**, no un texto continuo que se reescribe entero.
- **`## Historial de ajustes`**: la unica zona que crece por append. Una linea por cambio (fecha + resumen corto + motivo + id afectado), nunca el contenido completo del cambio — el detalle vive arriba y en `trazabilidad.md`.

### Por que cambio (contexto del ajuste)

La version anterior de esta regla decia "editar el bloque vigente in-place, reemplazando el dato viejo por el nuevo". La intencion era buena (evitar dos versiones contradictorias y respetar el techo de 150 KB), pero el efecto medido en sistemas de agentes es el contrario: la **reescritura iterativa erosiona informacion** — cada pasada resume, y cada resumen tira el detalle de dominio que en su momento costo descubrir (el "por que" de una decision, el caso borde que la origino, el numero exacto). El archivo queda mas corto y mas pobre, y nadie se entera de lo que se perdio.

La correccion no es volver a apilar secciones con fecha: es que **la unidad de memoria sea la entrada, no el archivo**.

### Como se escribe una entrada

1. **Todo dato vigente vive en una entrada con id propio.** Se reutiliza el id de dominio que el proyecto ya usa (`CR-80`, `MH-023`, `M19`, `PAT-017`, `REG-004`); si no hay uno, se crea correlativo por rol (`DEF-012`).
2. **Una definicion nueva que reemplaza a otra no pisa su texto:** nace como entrada nueva, con su propio id, y la entrada superada se marca en la misma linea del titulo:
   `### MH-014 — Calculo de caja mensual  ·  superada-por: MH-031`
   La entrada superada **conserva su cuerpo** hasta el archivado; no se vacia ni se resume.
3. **Nunca se edita el cuerpo de una entrada para "corregirla"**, salvo erratas (un typo, una ruta mal escrita). Un cambio de criterio es una entrada nueva.
4. **Cero notas al margen:** prohibido dejar "Correccion 2026-08-14: en realidad es X" pegado al dato viejo. Eso es una entrada nueva que supera a la vieja.
5. **Lectura:** quien lee el archivo consume **solo las entradas sin `superada-por`**. Ese es el estado actual y se puede confiar en el sin reconciliar versiones — que era el objetivo de la regla original, ahora sin costo de informacion.

### La poda es un paso explicito, no un efecto colateral

Las entradas marcadas `superada-por` **no se borran a mano**. Se archivan con `python scripts/archivar_memoria.py <archivo> --aplicar`, que las mueve a `definiciones/historial/` dejando un puntero de una linea. El techo de 150 KB (instruccion `39`, seccion 6) se sostiene **archivando**, no reescribiendo.

Si al archivar quedan dos entradas vigentes que dicen lo mismo con otras palabras, eso es un **dedup** y se resuelve explicitamente: una supera a la otra, con su marca. Nunca fusionando los dos textos en uno nuevo y perdiendo los dos originales.

### Chequeo antes de guardar

- El archivo no quedo con dos encabezados de nivel 2 iguales (ej. dos `## Historial de ajustes`) — es la señal de que se agrego una seccion nueva en vez de una entrada.
- Toda entrada vigente tiene id.
- Ninguna entrada quedo con el cuerpo vaciado o reducido a "ver entrada nueva".

# Regla de trazabilidad por interaccion
- Cada ajuste relevante debe agregar entrada en /docs/<proyecto>/trazabilidad.md con:
  - fecha y hora
  - agente/etapa
  - resumen del cambio o decision tomada
  - motivo
  - id de la entrada de `definiciones/` afectada (y el id que supera, si corresponde)
  - impacto en capas y riesgos/supuestos si aplica

# Traza de corrida (obligatoria al cerrar una etapa, 2026-09-25)

`trazabilidad.md` registra **que se decidio**. La traza de corrida registra **como fue la corrida**: es lo que permite despues mejorar las instrucciones con datos en vez de con intuicion.

Al cerrar su etapa, todo agente agrega un bloque de a lo sumo 5 lineas en `docs/<proyecto>/trazabilidad.md` con:

- **etapa / lote** y fecha.
- **reintentos**: cuantas veces hubo que rehacer algo (build fallido, criterio mal interpretado, fix que no cerro).
- **criterios fallados**: ids de los criterios/items que dieron FAIL, aunque despues se hayan cerrado.
- **reglas releidas**: que instruction o seccion hubo que volver a abrir en el medio del trabajo porque no estaba presente al arrancar. **Este es el dato mas valioso**: una regla que hay que releer siempre es una regla mal ubicada en la carga de arranque.
- **arranque real** en KB/tokens, si se midio.

Se escribe con `python scripts/traza.py registrar` (ver instruccion `39`, seccion 8), que deja el bloque en el formato correcto y acumula el indice consultable en `docs/trazas/`.

# Regla operativa para el orquestador
1. Al iniciar trabajo sobre un proyecto, verificar si ya existe /docs/<proyecto>/.
2. Si no existe, crear la estructura base desde /docs/templates/proyecto/.
3. Antes de cada etapa, leer la ultima version de definiciones del agente en /docs/<proyecto>/definiciones/.
4. Al cerrar cada etapa, actualizar el archivo del agente y registrar entrada en trazabilidad.md.
5. Mantener /docs/indice.md actualizado con todos los proyectos activos.
