---
name: presupuesto-parametros
description: Parametros de estimacion y precio del estudio (tasa, factores de Build/Merge, rangos por tipo de modulo, descuentos, planes de mantenimiento, costo interno de IA). Usar al estimar esfuerzo, armar un presupuesto o revisar un precio.
---

# Parametros de presupuesto

Dos archivos, con roles distintos. **Leer el YAML primero** — la prosa solo cuando haga falta el porque.

| Archivo | Que tiene | Cuando leerlo |
|---|---|---|
| `docs/calibracion/dataset.yml` | NUMEROS: tasa, factores, rangos por tipo de modulo, modificacion sobre modulo existente, cierres reales | Siempre, primero |
| `.github/instructions/27-presupuesto-parametros.instructions.md` (~30k tokens) | RAZONES: por que cambio un factor, que causo cada desvio, politicas comerciales | Solo la seccion que necesites |

`27-...` **no entra en una sola lectura**: usar `grep -n "^## "` para ubicar la seccion y leer por rango de lineas.

## Lo que mas se equivoca

- **Factor de Build = 4.0 desde 2026-09-08**: `Costo = M / 4.0 x 1.20 x $35 = M x $10.50`.
- **Merge, modulo nuevo post-entrega y Extras siguen en 2.5** (`M x $16.80`). Fork deliberado: ahi esta el margen. No unificar.
- **Tasa USD 35/h.** USD 30/h es el piso de negociacion, no la tarifa.
- **Tokens IA (25%)** se distribuye dentro del precio de cada modulo (x1.25). NUNCA como linea separada al cliente.
- **Iteracion evolutiva:** si el item reutiliza un patron ya resuelto en el repo, anclar en "modificacion sobre modulo existente", no en rangos de modulo nuevo (sobreestima 5-9x).
- **Segunda o tercera ronda sobre el mismo proyecto:** usar el PISO del rango, no la mediana.
- **Mantenimiento:** el plan sale SOLO de la cantidad de tablas. Los usuarios nunca cambian el precio. Año 1 gratis por defecto en Build de cliente nuevo.

## Obligacion al cerrar

Todo cierre real con horas medidas se carga en `cierres_reales` de `dataset.yml` **antes o al mismo tiempo** que en la prosa. El dataset no puede quedar atras (ya paso: quedo con el factor viejo casi 6 semanas).

## Indice de la fuente

`python scripts/contexto.py indice 27` lista sus secciones con el numero de linea: leer solo la que aplica (`sed -n '<desde>,<hasta>p'`), nunca el archivo completo (`39-presupuesto-contexto.instructions.md`).
