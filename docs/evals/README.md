# Evals del harness

Suite que responde una sola pregunta: **cuando cambiamos una instruction, un `.agent.md` o
la carga de arranque de un rol, ¿el agente quedó mejor o peor?**

No evalúa el modelo. Evalúa **nuestra escritura**: si una regla está mal ubicada, mal
redactada o enterrada en un archivo de 67 KB, el eval lo muestra. Un catálogo de 45 reglas
que el agente no aplica es peor que 10 que sí: ocupa contexto y da falsa seguridad.

- **Spec completa:** `.github/instructions/40-evals-del-harness.instructions.md`
- **Casos:** `casos.yml` — 23 activos, todos derivados de fallos reales
- **Runner:** `scripts/evals.py`

## De dónde salen los casos

Ninguno está inventado. Cada caso declara su `fuente`:

| Fuente | Qué pregunta el caso |
|---|---|
| `regresiones-manuales` (`docs/qa/regresiones-manuales.yml`) | con lo que le cargamos hoy, ¿el agente hubiera evitado o detectado este bug que pasó de verdad? |
| `dataset-calibracion` (`docs/calibracion/dataset.yml`) | ¿el presupuestador cae dentro del rango que ya sabemos correcto? |
| `trazas` (`docs/trazas/trazas.tsv`) | una regla que hubo que releer, o un criterio que falló en más de un proyecto |

## Cómo se corre

```bash
python scripts/evals.py validar                            # estructura de casos.yml
python scripts/evals.py listar   --rol implementador-dotnet
python scripts/evals.py costo    --rol implementador-dotnet   # <-- SIEMPRE antes de correr
python scripts/evals.py preparar --rol implementador-dotnet   # escribe los .prompt.txt
#   -> correr cada prompt en un subagente LIMPIO del rol, sin decirle que es un eval,
#      y guardar la respuesta como <id>-<n>.out.txt al lado
python scripts/evals.py gradear  --corrida 2026-09-25-implementador-dotnet
```

**El script no gasta un token por sí solo.** Prepara los prompts y gradea las respuestas;
las corridas las dispara quien orquesta, después de ver el costo. Nunca en cron.

## Cuándo

Obligatorio antes de commitear un cambio a `32`, `27`, `39`, `30`, `33` o a cualquier
`.agent.md` — y solo los casos del rol afectado, no la suite entera.

## Lo que no se saltea

Después de cada corrida se leen los transcripts de **todos los FAIL y 2 PASS al azar**.
Un caso que pasa por el motivo equivocado (el enunciado filtraba la respuesta) contamina
la métrica más que uno que falla. El número final sirve para comparar dos versiones del
harness; para entender algo, hay que leer qué hizo el agente.
