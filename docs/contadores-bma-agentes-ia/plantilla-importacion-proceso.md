# Plantilla de importación de proceso — desde el Proyecto de Claude de Gastón

Objetivo: convertir lo que salga de la charla de Gastón en su Proyecto de Claude.ai en algo directamente importable a `docs/contadores-bma-agentes-ia/` — sin perder los pasos ni las reglas de conversión en una narrativa suelta. Completar **una copia de esta plantilla por cada proceso** que Gastón describa (conciliación bancaria, traslado Bejerman→SOS, liquidación de un impuesto puntual, etc.) — no un documento único mezclando todo.

Mapea directo a la arquitectura en capas ya definida en `definiciones/1-analista-funcional.md`: la sección 3 de acá abajo es la capa de **adaptador** (reglas de conversión, mecánico), la sección 4 es la capa de **reglas de negocio/agente** (juicio, excepciones).

---

## 1. Identificación del proceso

- Nombre del proceso:
- Herramienta(s) involucradas: Bejerman Web / SOS Contador / ambas / banco u otro externo
- Frecuencia y tiempo aprox. que le insume a Gastón hoy:
- ¿Es igual para todos los clientes, o varía? (si varía, aclarar qué varía)

## 2. Pasos del proceso (tal como lo hace Gastón hoy)

Numerados, en el orden real. Ejemplo de nivel de detalle esperado:

> 1. Entro a Bejerman Web y exporto el movimiento de cuenta del mes (menú X > opción Y).
> 2. Descargo el resumen del banco desde el home banking.
> 3. Comparo movimiento por movimiento...

## 3. Datos de entrada y reglas de conversión (capa de adaptador — script determinístico)

Esta es la parte más valiosa para sistematizar — equivalente a lo que ya existe en `mapeo-archivos.md` del conversor:

| Campo/dato de origen | Sistema/archivo de origen | Campo/dato de destino | Sistema/archivo de destino | Transformación o regla |
|---|---|---|---|---|
| | | | | |

- Formato del archivo de entrada (Excel/CSV/XML, columnas, filas de encabezado):
- Formato de salida esperado:
- Casos donde el dato de origen puede faltar o venir distinto (ver también sección 5):

## 4. Reglas de negocio y juicio (capa de agente)

- ¿Qué decisiones no son 100% mecánicas — requieren criterio de Gastón? (ej. "si la diferencia es menor a $X, la doy por conciliada igual", "si el concepto no está en la lista, lo clasifico según...")
- ¿Qué cálculos numéricos/impositivos están involucrados? (recordar: estos van siempre en código determinístico, nunca "calculados" por el agente — solo hace falta identificarlos acá)

## 5. Casos borde y excepciones

- ¿Qué pasa cuando algo no calza/no matchea automáticamente? ¿Cómo lo resuelve Gastón hoy?
- ¿Hay clientes o situaciones particulares que rompen el proceso estándar descrito arriba?

## 6. Ejemplo real (anonimizado si hace falta por confidencialidad del cliente)

Un caso concreto de principio a fin, con datos de muestra — igual que se usó `Docs/Grilla Informe de Liquidación.xlsx` como referencia real en el conversor.

---

## Nota para quien hace la importación a este proyecto

Al volcar esto a `docs/contadores-bma-agentes-ia/`, un proceso completado con esta plantilla va a:
- `definiciones/1-analista-funcional.md` si es un proceso nuevo del catálogo (sección "Catálogo real de tareas")
- Un archivo de mapeo dedicado (tipo `mapeo-<proceso>.md`) si la sección 3 (reglas de conversión) es extensa — mismo patrón que `contadores-bma-conversor/mapeo-archivos.md`
- Registrar siempre la entrada correspondiente en `trazabilidad.md`
