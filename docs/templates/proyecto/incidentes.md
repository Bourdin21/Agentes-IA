# Incidentes de produccion

Registro de la via rapida (`42-incidente-produccion.instructions.md` / `/agentes-ia-emergencia`).
Solo P1 (caida o corrupcion en curso) y P2 (operacion diaria bloqueada sin workaround). Un pedido urgente **sin**
caida es P3 y no se anota aca: va por el flujo normal.

Reglas de este archivo: **entradas con id** (`29-trazabilidad-conversacion`) — una definicion nueva no pisa el texto
viejo; techo de 150 KB, archivado con `python scripts/archivar_memoria.py incidentes.md --aplicar`.

El `INC` se **abre en el paso 0 del triage**, con los cinco campos de arranque, y se completa mientras avanza. El
informe que se deja para el final no se escribe nunca.

Estados, en orden y sin saltos: **`abierto`** (en curso) -> **`restablecido`** (el cliente trabaja, smoke propio) ->
**`cerrado`** (paso la corrida de QA independiente). `doctor.py` avisa a los 7 dias sin cerrar y marca error a los 30.

## Incidentes

### INC-001 — <titulo del sintoma, como lo ve el usuario>  ·  estado: <abierto|restablecido|cerrado>
- **nivel:** <P1|P2>
- **abierto:** <YYYY-MM-DD HH:mm>
- **sintoma observado:** <lo que se ve, no la hipotesis>
- **alcance:** <quienes y que modulo>
- **cobertura:** <mantenimiento vigente (plan) | fuera de plan — declarado, no discutido ahora>
- **contencion:** <que se hizo (revert / modulo bajado / job apagado) y a que hora; o "no se contuvo" + motivo>
- **plan de vuelta atras:** <una linea: como se deshace lo que se va a hacer>
- **backup:** <id o nombre del backup de BD, y a que hora>
- **filas medidas:** <conteo antes / conteo despues, con el WHERE usado — solo si el fix toco datos>
- **causa raiz:** <observada: evidencia citada (log, fila, request) | PALIATIVO: + id del CR de causa raiz>
- **archivos del fix:** <ruta por capa>
- **migracion EF:** <nombre exacto | no>
- **aviso enviado:** <a quien, cuando, por que canal | no hacia falta + motivo>
- **restablecido:** <YYYY-MM-DD HH:mm + evidencia del smoke>
- **cerrado:** <YYYY-MM-DD + corrida de QA que lo cerro>
- **horas reales:** <h de incidente, al dataset de calibracion>
- **regresion catalogada:** <id en docs/qa/regresiones-manuales.yml | N/A + motivo>

## Historial de ajustes
- <YYYY-MM-DD>: <resumen del ajuste y motivo>
