<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/1-analista-funcional.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 1-analista-funcional - M06 (4 bloques archivados)

- Casos de uso M6
- Permisos M6
- Supuestos M6
- Banderas tempranas M6

---

### Casos de uso M6
| CU | Actor | Descripción |
|---|---|---|
| CU-M6-01 | Staff Olvidata | Fija o cambia el límite mensual de una organización |
| CU-M6-02 | Director | Fija, cambia o quita el límite mensual de un miembro |
| CU-M6-03 | Director | Ve el consumo del mes de la organización por miembro, área, agente y cliente |
| CU-M6-04 | Empleado | Ve su propio consumo y su límite |
| CU-M6-05 | Staff Olvidata | Ve consumo y límites de cualquier organización |
| CU-M6-06 | Sistema | Avisa al llegar al 80 % y al 100 % de un límite |
| CU-M6-07 | Sistema | Bloquea tareas, configuraciones y ajustes nuevos y frena turnos en curso al llegar al límite |
| CU-M6-08 | Agente (motor) | Pide una acción que requiere aprobación: la tarea queda esperando |
| CU-M6-09 | Autor de la tarea / Director | Aprueba una acción desde la tarea o la bandeja |
| CU-M6-10 | Autor de la tarea / Director | Rechaza una acción con motivo opcional |
| CU-M6-11 | Director | Aprueba o rechaza una acción de nivel "solo un Director" |
| CU-M6-12 | Sistema | Vence los pedidos sin respuesta |
| CU-M6-13 | Miembro | Consulta la bandeja de aprobaciones y su historial |
| CU-M6-14 | Autor / Director | Cancela una tarea que espera aprobación |
### Permisos M6
| Acción | Director | Empleado | Staff |
|---|:---:|:---:|:---:|
| Ver consumo de la organización (por miembro, área, agente, cliente) | ✅ | ❌ | ✅ (backoffice) |
| Ver su propio consumo y límite | ✅ | ✅ | — |
| Cambiar el límite de un miembro | ✅ | ❌ | ❌ |
| Cambiar el límite de la organización | ❌ | ❌ | ✅ (sin límite: solo SuperUsuario) |
| Ver pedidos de aprobación de una tarea | según visibilidad M2 | sus tareas | ✅ lectura |
| Aprobar / rechazar "quien pidió la tarea" | ✅ cualquiera | ✅ sus tareas | ❌ |
| Aprobar / rechazar "solo un Director" | ✅ | ❌ (ve que espera a un Director) | ❌ |
| Bandeja de aprobaciones | ✅ organización | ✅ sus tareas | ❌ |
| Cancelar una tarea en espera | ✅ (como M2) | ✅ sus tareas | ❌ |
### Supuestos M6
- S-M6-01 El costo guardado por paso es suficientemente fiel para limitar (tabla de precios verificada; calidad real del conteo de caché en PA-02).
- S-M6-02 Una sola llamada al modelo no excede el límite en una magnitud relevante (con `MaxTokens` 16.000 de salida en Opus 5, del orden de USD 0,50) y `MaxTareasPorCliente = 1` acota el exceso concurrente.
- S-M6-03 El volumen inicial permite calcular el consumo del mes sumando pasos en cada verificación (sin tabla acumulada).
- S-M6-04 La notificación del portal alcanza como canal de avisos y pedidos en esta etapa.
- S-M6-05 El worker corre de forma continua para vencer pedidos (AlwaysRunning, PA-07); si se duerme, los vencidos se procesan al despertar y aprobar un vencido igual se impide.
- S-M6-06 Las herramientas reales de M11 van a poder describir en palabras la acción a partir de sus datos.
### Banderas tempranas M6
- Migración EF: **sí** (límite en la organización, límites por miembro, pedidos de aprobación, avisos enviados, índice de consumo).
- Integración externa: **no** (sin llamadas nuevas; notificaciones del portal existentes).
- Máquina de estados: **sí** (pedido de aprobación; la tarea empieza a usar `EsperandoAprobacion` y el corte por límite).
