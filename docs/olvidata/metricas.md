# Métricas reales contra el plan
> **Archivo generado — no editarlo a mano.** Lo regenera `python scripts/olvidata_datos.py metricas` leyendo el CRM productivo.
> Snapshot del 2026-10-15. Lo que el CRM no sabe se edita en `datos-manuales.yml`.

El plan financiero (`olvidata-ceo.md`) fija la decisión de salida del Ministerio en **USD 1.173/mes de recurrente durante 6 meses seguidos**. Esta es la tabla donde ese número se mide en vez de estimarse.

**Cómo leer la serie:** el CRM no fecha las bajas (solo marca `Activo=0`), así que un cliente que se fue sigue contando desde su alta hasta hoy. El último mes de esta tabla queda entonces por encima del total de `clientes.md`, que sí excluye a los inactivos. La diferencia es exactamente el recurrente de las bajas.

| Mes | Clientes activos | Recurrente contratado USD/mes | Cobrable USD/mes | Altas | No recurrente del mes USD | ¿Supera el umbral? |
|---|---:|---:|---:|---:|---:|---|
| 2026-01 | 1 | 21 | 21 | 1 | 525 | no |
| 2026-02 | 2 | 21 | 21 | 1 | 254 | no |
| 2026-03 | 7 | 108 | 108 | 5 | 217 | no |
| 2026-04 | 8 | 132 | 132 | 1 | 1.044 | no |
| 2026-05 | 9 | 158 | 132 | 1 | 585 | no |
| 2026-06 | 13 | 212 | 153 | 4 | 1.120 | no |
| 2026-07 | 15 | 258 | 167 | 2 | 1.432 | no |
| 2026-08 | 17 | 333 | 167 | 2 | 1.621 | no |
| 2026-09 | 17 | 333 | 167 | — | — | no |
| 2026-10 | 17 | 333 | 167 | — | 510 | no |

## Setup + recurrente: las dos mitades del ingreso

El plan tiene que mirar las dos (indicación de Joaquín, 2026-10-16: *"tener en cuenta el precio de setup + recurrente en todo el plan"*). No se suman en una sola línea porque no se comportan igual: el setup entra una vez por cliente y el recurrente vuelve todos los años.

| Concepto | Valor |
|---|---:|
| Ingreso no recurrente acumulado (setup, cuotas de implementación, trabajo adicional) | USD 7.818 |
| Promedio por mes con movimiento (10 meses) | USD 782 |
| Recurrente anual contratado | USD 3.820 |

**Por qué el semáforo de abajo usa solo el recurrente:** la decisión de dejar el Ministerio es sostener un ingreso **sin vender nada nuevo ese mes**. El setup es ingreso real y hoy es la mayor parte de la facturación, pero depende de cerrar un cliente nuevo: si se cuenta en el umbral, el mes que no se cierra nada el sueldo desaparece. Para medir capacidad de pago de un proyecto o la caja del año, sí van los dos.

## Semáforo de la decisión del Ministerio

- Recurrente cobrable hoy: **USD 152/mes**. Umbral: USD 1.173/mes.
- Faltan **USD 1.021/mes** (87% del umbral) para cruzarlo.
- Meses consecutivos por encima del umbral, a hoy: **0** (máximo histórico: 0). El plan pide 6.

## Lo que todavía no se puede medir desde el CRM

- **Tasa demo → cierre:** el CRM registra presupuesto enviado, no la demo. Falta el dato de origen, no el cálculo.
- **Conversión asistida de Instagram:** `CanalOrigen` distingue Instagram orgánico de Ads, pero no hay forma de atribuir un cierre a una publicación.
- **Cierres por frente:** el frente vive hoy en `datos-manuales.yml` para clientes y se infiere del gancho para leads; mientras `Contacto` no tenga `FrenteComercial`, el corte por frente es aproximado.
- **Costos:** se descuentan en `costos.md`, que es a mano. Las cifras de arriba son ingreso recurrente **bruto**, no neto.

3 contacto(s) marcados Cerrado con fecha de completado en el CRM.
