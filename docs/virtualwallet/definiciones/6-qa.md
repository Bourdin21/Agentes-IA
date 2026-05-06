# 6 - QA (memoria acumulativa)

## Etapa actual: revision de reportes y KPIs del dashboard

### Alcance funcional validado
- `Dashboard/ResumenGeneral`: KPIs (ingresos, egresos, balance, tasa de ahorro), donut, barras por cuenta, pies por categoria, detalle por cuenta, cuotas activas, recurrentes, deuda de tarjeta, top 10 gastos, alertas.
- `Dashboard/EvolucionTendencias`: linea de tiempo anual, historico anual, proyeccion con inflacion 5%/mes, egresos por subcategoria, tablas mensual y por anio.

### Defectos detectados (severidad)
- B-01 (medio) - Sobreconsumo: comparaba contra un periodo anterior medido en dias (`fechaHasta - fechaDesde`), generando ventanas de longitud distinta cuando el rango cruza meses con 28/30/31 dias. Ahora se usa cantidad de meses calendario equivalentes.
- B-02 (bajo) - Top 10 gastos: orden no determinista para empates de monto. Se agrega desempate estable por fecha desc + id desc.
- B-03 (alto) - Movimientos recurrentes: el agrupador incluia ingresos, pagos a tarjeta y movimientos pendientes, mezclando signos y arrastrando categorias del flujo de tarjeta. Ahora restringido a egresos efectivos no pago-tarjeta y estado realizado.
- B-04 (info) - Proyeccion en USD: cuando `usd=true` y los movimientos historicos no tienen `MontoUsd`, la proyeccion se calcula con valor 0 y "desaparece". Documentado como sugerencia de mejora (no es bug funcional, es contrato del dato).
- B-05 (medio) - Egresos por subcategoria: no excluia `EsPagoTarjeta`, por lo que los pagos a tarjeta clasificados con subcategoria distorsionaban el grafico mensual. Ahora alineado con el resto del dashboard (`!EsPagoTarjeta`).
- B-06 (medio) - `EvolucionTendencias`: el toggle USD/ARS no se persistia entre vistas; al volver del Resumen General se reseteaba. Ahora ambas vistas comparten la clave `Dashboard_Usd` en Session, con `Request.Query.ContainsKey("usd")` para distinguir default de seleccion explicita.
- B-07 (alto) - Cuotas activas: el filtro `fechaFin < fechaHasta.AddMonths(-1)` consideraba activa una cuota incluso cuando ya habia vencido en el periodo elegido (porque `fechaFin` se computaba como mes de inicio + n-1 meses, sin avanzar al fin del mes calendario). Ahora `fechaFin` es el ultimo dia del mes de la ultima cuota y se descarta solo cuando ya paso respecto al fin del periodo.
- B-08 (info) - Recurrentes: se calculan sobre los movimientos del periodo unicamente. Si el periodo es < 3 meses, casi nunca habra coincidencias (umbral >= 3 apariciones). Sugerencia: hacer el umbral configurable o explicar el criterio en la UI.

### Auto-fixes aplicados
| id | archivos tocados | resultado |
|----|------------------|-----------|
| B-01 | `VirtualWallet.Web/Controllers/DashboardController.cs` | OK, build verde |
| B-02 | `VirtualWallet.Web/Controllers/DashboardController.cs` | OK |
| B-03 | `VirtualWallet.Web/Controllers/DashboardController.cs` | OK |
| B-05 | `VirtualWallet.Web/Controllers/DashboardController.cs` | OK |
| B-06 | `VirtualWallet.Web/Controllers/DashboardController.cs` | OK |
| B-07 | `VirtualWallet.Web/Controllers/DashboardController.cs` | OK |

### Sugerencias y mejoras (no aplicadas)
- M-01: agregar a Resumen General un KPI "Gastos no recurrentes vs recurrentes" para visualizar el peso del consumo discrecional.
- M-02: incluir mediana de egresos mensuales en `Proyeccion`, no solo promedio (los outliers distorsionan la estimacion).
- M-03: en `Proyeccion`, hacer la inflacion mensual configurable (hoy es 5% hardcoded). Idealmente leer de la cotizacion historica/IPC.
- M-04: excluir movimientos `Pendiente` de `Top 10 gastos` o marcarlos visualmente con badge "Pendiente" en la tabla.
- M-05: en `Cuotas Activas`, mostrar tambien la cantidad de cuotas restantes y el monto pendiente de pago (cuotas - pagadas) * monto cuota.
- M-06: en `Deuda Tarjeta`, agregar columna "Saldo arrastrado" (deuda anterior - pagos del periodo) y separar gastos del periodo del saldo abierto.
- M-07: alerta "Categoria que crecio X%" comparando totales por categoria contra el periodo anterior equivalente.
- M-08: cachear los KPIs por (usuario, periodo, moneda) durante N minutos via `IMemoryCache` o cache distribuido para alivianar la carga del controller (hoy levanta todos los movimientos del periodo + extras a memoria).
- M-09: en USD, cuando un movimiento no tiene `MontoUsd`, ponerlo en una cubeta "Sin cotizacion" en lugar de sumarlo como 0; reportar la cantidad como aviso.
- M-10: en `EgresosSubcategoriaAnual`, agregar un boton "Mostrar todas" / "Ocultar todas" para alternar visibilidad de las series del line chart (hoy hay que clickear cada leyenda).
- M-11: exportacion (CSV/Excel) de las tablas del dashboard (Top 10, recurrentes, deuda tarjeta).

### Pruebas minimas ejecutadas
- Build de la solucion despues de los fixes: PASS.
- Revision estatica de los controladores y vistas: PASS.
- Pruebas funcionales sobre datos reales: pendiente (no hay corrida de la app en este ciclo).

### Pruebas funcionales sugeridas para QA manual
1. Login y abrir Resumen General sin filtros -> verifica que toma el ultimo rango en sesion (D-10).
2. Cambiar periodo a un mes con cantidad de dias atipica (ej. febrero) -> alerta "Sobreconsumo" debe comparar contra enero, no contra "ultimos 28 dias" (B-01).
3. Cargar pagos a tarjeta dentro del periodo -> no aparecen en "Movimientos recurrentes" ni en "Egresos por subcategoria" del anual (B-03/B-05).
4. Ir a `EvolucionTendencias?usd=true` y volver a Resumen General sin parametros -> el toggle sigue en USD (B-06).
5. Crear una cuota de 6 meses iniciada hace 3 meses, filtrar dashboard al mes actual -> debe seguir siendo "Activa" (B-07). Si se elige un periodo posterior al ultimo mes de la cuota, ya no debe aparecer.
6. Top 10 gastos: con varios gastos del mismo monto, el orden debe ser estable entre recargas (B-02).

### Cobertura de criterios de aceptacion
| criterio | resultado |
|----------|-----------|
| Filtros del dashboard se mantienen | PASS (D-10 aplicado en sesion previa) |
| KPIs respetan flag `EsPagoTarjeta` | PASS (revisado en todas las series) |
| Cuotas finalizadas no aparecen en activas | PASS (B-07 corregido) |
| Recurrentes solo egresos | PASS (B-03 corregido) |
| Sobreconsumo usa ventana comparable | PASS (B-01 corregido) |
| Toggle USD persistente entre vistas | PASS (B-06 corregido) |

### Riesgos de liberacion
- R-01: el cambio en `ObtenerCuotasActivas` puede ocultar cuotas que antes aparecian si el usuario consultaba periodos en el futuro lejano. Mitigacion: revisar dashboard tras el deploy con un usuario con cuotas en distintos estados.
- R-02: el desempate del top 10 ahora incluye `Id`, lo que cambia el orden visible aunque sea trivial. Mitigacion: comunicar en release notes que el orden es estable.
- R-03: la persistencia de `usd` puede confundir a usuarios que esperaban que el toggle siempre arrancara en ARS. Mitigacion: documentar y mostrar visualmente el modo activo (ya hay badge ARS/USD).

### Checklist de salida para merge
- [x] Build OK.
- [x] Capas respetadas (calculos en controller; UI inalterada en estructura).
- [x] No hay migraciones EF nuevas.
- [x] Memoria QA actualizada.
- [ ] QA manual segun escenarios listados.
- [ ] Despliegue de migracion `ConstrainDescripcionOriginalLength` en produccion (operativo).
