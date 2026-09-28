---
description: Suite de evals del propio sistema de agentes. Como saber si un cambio en una instruction mejoro o empeoro al agente, con casos sacados de fallos reales.
applyTo: "**"
---

# 40 - Evals del harness (obligatoria antes de tocar una instruction grande)

## Por que existe

Todo este repositorio es el **harness** de los agentes del estudio: las instructions, los `.agent.md`, las skills, los indices planos, los scripts de contexto. Cada vez que se agrega una regla al `32`, se reescribe la carga de arranque de un rol o se cambia el contrato del QA, se esta modificando el comportamiento de un sistema en produccion.

Hasta el 2026-09-25 ese cambio se validaba **por intuicion**: se agregaba la regla, se leia, parecia razonable, se commiteaba. No habia forma de saber si el agente efectivamente la aplicaba, ni si al agregarla se degrado otra cosa. Un catalogo de 45 reglas que el agente no aplica es peor que 10 que si: ocupa contexto y da falsa seguridad.

Un eval no prueba el modelo. Prueba **nuestra escritura**: si una regla esta mal ubicada, mal redactada o enterrada en un archivo de 67 KB, el eval lo muestra.

## Alcance: que se evalua y que no

**Se evalua:** que el agente, cargado como lo cargamos nosotros, detecte/aplique las reglas del estudio sobre un caso concreto.

**No se evalua:** la calidad del modelo, la velocidad, ni el resultado de negocio de un proyecto. Para eso ya estan `docs/calibracion/dataset.yml` (estimado vs. real) y el reporte de QA.

## Los casos salen de fallos reales, nunca inventados

Regla dura. Un caso de eval nace de una de estas tres fuentes, y **declara cual**:

1. **`docs/qa/regresiones-manuales.yml`** — un bug que se reprodujo de verdad en un proyecto. El caso pregunta: "con lo que le cargamos hoy, ¿el agente lo hubiera evitado / detectado?".
2. **`docs/calibracion/dataset.yml`** — una estimacion que se desvio del real. El caso pregunta: "¿el presupuestador cae hoy dentro del rango que sabemos correcto?".
3. **`docs/trazas/trazas.tsv`** (instruccion `39`, seccion 8) — una regla que hubo que releer, o un criterio que fallo en mas de un proyecto.

Arrancar con **20 a 30 casos** alcanza y sobra. No esperar a tener cientos: una suite chica que corre vale infinitamente mas que una grande que nunca se arma.

## Como se escribe un caso

Los casos viven en `docs/evals/casos.yml`. Campos obligatorios: `id`, `rol`, `origen`, `titulo`, `entrada`, `grader`, `metrica`.

Tres reglas de redaccion, todas aprendidas de errores tipicos:

1. **No gradear la secuencia de pasos.** Se grada el **resultado**, no el camino. Exigir que el agente haya hecho A -> B -> C castiga una solucion valida distinta y convierte el eval en una prueba de obediencia. Si el camino importa de verdad, es un criterio de salida del `.agent.md`, no un eval.
2. **La spec del caso tiene que ser inequivoca.** Si dos lectores razonables entienden cosas distintas, el fallo es **de la tarea**, no del agente. Un caso ambiguo se arregla o se borra; nunca se deja "porque a veces pasa".
3. **Entorno limpio entre corridas.** Ningun caso deja estado que el siguiente pueda leer. Si un caso necesita un proyecto levantado, se marca `entorno: proyecto` y corre aparte.

### Tipos de grader

| Tipo | Cuando | Costo |
|---|---|---|
| `codigo` | la respuesta correcta es verificable mecanicamente: cita el id esperado, el numero cae en un rango, el texto contiene/no contiene algo | gratis, deterministico. **Es el default: si un caso se puede gradear por codigo, se gradea por codigo** |
| `modelo` | juicio con rubrica (¿el diagnostico es correcto aunque este dicho con otras palabras?) | cuesta tokens. Se usa solo cuando `codigo` no llega |
| `humano` | criterio comercial o de diseño que solo define Joaquin | se acumulan y se revisan juntos, nunca de a uno |

Se admite **credito parcial**: un caso puede valer 0, 0.5 o 1. Detectar el bug pero errar la capa no es lo mismo que no detectarlo.

### Metricas

- **`pass@k`** (paso al menos 1 de k intentos): para lo exploratorio, donde alcanza con que el agente pueda llegar.
- **`pass^k`** (pasaron **todas** las k corridas): para lo que ve el cliente y para lo que toca plata. Un modulo financiero que anda 2 de 3 veces no anda.

Default: `pass@2`. Los casos de plata (facturacion, pagos, caja, presupuesto) van en `pass^3`.

## Cuando se corre

- **Obligatorio:** antes de commitear un cambio a `32`, `27`, `39`, `30`, `33` o a cualquier `.agent.md`. Se corren **solo los casos del rol afectado**, no la suite entera.
- **Recomendado:** despues de agregar 5 items nuevos al catalogo de regresiones (para confirmar que el agente los aplica y no solo que estan escritos).
- **Nunca en cron.** No hay ninguna razon para quemar tokens en un horario fijo sobre un harness que no cambio.

## Costo (leer antes de correr)

Una corrida **cuesta plata de verdad**: cada caso es una invocacion completa de un agente con su carga de arranque. Antes de ejecutar:

```
python scripts/evals.py costo --rol implementador-dotnet
```

imprime cuantos casos, cuantas corridas y el costo estimado. **`scripts/evals.py` no ejecuta nada sin `--ejecutar`, y con `--ejecutar` imprime el costo y pide confirmacion.** Un eval que se dispara solo es un gasto que nadie autorizo.

## Leer los transcripts (el paso que no se saltea)

El numero final del eval sirve para comparar dos versiones del harness. **No sirve para entender nada.** Lo unico que dice si el grader mide lo que creemos es leer que hizo el agente:

- Un caso que **pasa por el motivo equivocado** (adivino, o el enunciado filtraba la respuesta) es peor que uno que falla: contamina la metrica.
- Un caso que **falla por la spec** y no por el agente hay que arreglarlo o borrarlo.
- Un caso que pasa **siempre**, en todas las versiones, no mide nada: se archiva.

Despues de cada corrida se leen al menos los transcripts de los FAIL y de 2 PASS al azar. Sin eso, la suite es un numero decorativo.

## Mantenimiento

- Un caso que paso 3 corridas seguidas en versiones distintas del harness pasa a `estado: archivado`: ya no discrimina.
- Un bug nuevo del catalogo que se repitio en **dos proyectos distintos** entra como caso nuevo: dejo de ser un accidente.
- La suite no crece sola. Si pasa de ~40 casos activos, se poda por poder de discriminacion, no por antiguedad.
