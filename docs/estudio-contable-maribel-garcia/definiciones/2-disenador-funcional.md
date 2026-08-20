# Memoria - Disenador funcional

## Proyecto: estudio-contable-maribel-garcia
## Ultima actualizacion: 2026-08-20

## Definiciones vigentes

### Historias de usuario

**HU-01 — Importar extracto bancario**
Como contador, quiero subir el archivo de extracto bancario (CSV/Excel) para cargar los movimientos del banco al sistema.
- Criterio: valida columnas minimas (fecha, monto, concepto); rechaza con mensaje claro si el archivo no tiene el formato esperado.

**HU-02 — Importar extracto de Mercado Pago**
Como contador, quiero subir el archivo de actividad/reporte de Mercado Pago para cargar esos movimientos al sistema.
- Criterio: mismo tipo de validacion que HU-01, adaptada a las columnas del export de MP.

**HU-03 — Conciliacion automatica**
Como contador, quiero que el sistema empareje automaticamente los movimientos que coinciden en monto y fecha (dentro de una tolerancia) para no revisar a mano lo que es obvio.
- Criterio: un movimiento bancario y uno de MP con mismo monto exacto y fecha dentro de la tolerancia configurada quedan marcados "Conciliado" sin intervencion manual. Un movimiento no se concilia dos veces (1 a 1).

**HU-04 — Revision de sugerencias**
Como contador, quiero ver los movimientos que no calzaron exacto pero tienen candidatos razonables, para confirmar o rechazar cada sugerencia.
- Criterio: cada sugerencia muestra el/los candidato(s) posibles con su diferencia de monto/fecha. Confirmar mueve a "Conciliado"; rechazar lo deja en "Sin conciliar".

**HU-05 — Movimientos sin conciliar**
Como contador, quiero ver los movimientos que no encontraron ningun candidato, para investigarlos manualmente.
- Criterio: lista separada, filtrable por origen (Banco / Mercado Pago), fecha y monto.

**HU-06 — Exportar reporte de conciliacion**
Como contador, quiero exportar el resultado de la conciliacion (conciliados, sugeridos confirmados, sin conciliar) para el cierre contable.
- Criterio: exporta a Excel con las 3 categorias claramente separadas, totales por categoria.

**HU-07 — Acceso de usuarios**
Como estudio, quiero que cada persona del equipo (1-2) tenga su propio login para saber quien hizo cada confirmacion/rechazo.
- Criterio: login basico, sin roles diferenciados (equipo chico, mismo nivel de acceso para todos).

*(Etapa 2)* **HU-08 — Asistencia por IA en casos ambiguos**
Como contador, quiero que el sistema use IA para sugerir el candidato mas probable cuando el emparejamiento automatico por monto/fecha no alcanza (conceptos parecidos pero no identicos, montos con pequenas diferencias, mas de un candidato posible) para reducir el tiempo de revision manual en los casos dificiles.
*Hipotesis a validar con el cliente: esto complementa el motor deterministico de HU-03, no lo reemplaza — la mayoria del volumen se resuelve por monto+fecha exacto sin necesidad de IA (ver justificacion tecnica en 3-arquitecto-mvc.md). Requiere definir si el costo operativo de las consultas a la IA en produccion lo cubre el estudio (via mantenimiento) o el cliente (con su propia cuenta) — pregunta activa en la propuesta.*

### Flujos de pantalla acordados
1. Login → Panel de conciliacion (resumen: X conciliados, Y sugeridos pendientes, Z sin conciliar).
2. Panel → Importar extracto (Banco o Mercado Pago) → subir archivo → confirmacion de carga.
3. Panel → Ver sugerencias pendientes → por cada una, confirmar o rechazar.
4. Panel → Ver sin conciliar (Banco / Mercado Pago, filtrable).
5. Panel → Exportar reporte (rango de fechas) → descarga Excel.

### ViewModels definidos
- `MovimientoBancarioViewModel` (Fecha, Monto, Concepto, Estado).
- `MovimientoMercadoPagoViewModel` (Fecha, Monto, Concepto, Estado).
- `SugerenciaConciliacionViewModel` (MovimientoBancario, Candidatos MercadoPago[], DiferenciaMonto, DiferenciaDias).
- `ReporteConciliacionViewModel` (RangoFechas, TotalConciliado, TotalSugeridoConfirmado, TotalSinConciliar, Detalle[]).

### Validaciones de UI acordadas
- No permitir importar un archivo sin las columnas minimas requeridas — mensaje especifico de que columna falta.
- Confirmar/rechazar una sugerencia requiere seleccion explicita (no defaults automaticos en casos ambiguos).
- Exportar reporte requiere rango de fechas valido (fecha desde <= fecha hasta).

### Logica de distribucion de elementos en pantalla
- priorizar simplicidad visual y comprension inmediata del flujo
- ubicar primero informacion y acciones criticas (pendientes de revision) antes que lo ya resuelto
- mantener jerarquia consistente (titulo, contexto, formulario, acciones)
- reducir ruido visual: evitar bloques redundantes y opciones duplicadas
- reutilizar este criterio de distribucion en todas las pantallas del sistema

### Contratos funcionales para Services
- `IConciliacionService.ConciliarAutomatico(extractoBancoId, extractoMpId, toleranciaDias) : ResultadoConciliacion` — matching deterministico por monto exacto + fecha dentro de tolerancia.
- `IConciliacionService.ObtenerSugerencias(...)` — candidatos para los no conciliados automaticamente (por proximidad de monto/fecha).
- `IImportadorExtractoService` — parseo de archivo a movimientos, con validacion de columnas (candidato de reutilizacion parcial del patron de parser Excel propietario ya construido en `contadores-bma-conversor`, adaptado a un formato tabular simple en vez de jerarquico).

## Historial de ajustes
- 2026-08-20: primera version.
