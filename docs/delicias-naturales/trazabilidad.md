# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-06-28 - presupuestador
- Etapa: Presupuesto
- Cambio: Batch de 4 mejoras evolutivas presupuestado (F1 badge stock + SweetAlert, F2 Vendedor Pedidos, F3 Totalizador Pagos, F4 Layout Resumen). M total 8 h. USD 135. Etapa 1: USD 51 / Etapa 2: USD 84.
- Motivo: Solicitud directa del cliente sin etapas previas formales (analista/disenador/arquitecto). Features bien delimitadas; presupuesto producido desde descripcion funcional + exploracion de codigo.
- Impacto en capas: Presentacion (Views, CSS, JS) y Negocio (permisos, validacion stock). Sin cambios en Datos (no hay migraciones EF).
- Riesgos/supuestos: F4 riesgo medio por CSS 1122 lineas con breakpoints; cargo IA tokens no aplica (facturables 3.84 h < 4 h umbral). Sin documentos upstream aprobados — advertencia registrada.

### 2026-07-01 - implementador-dotnet
- Etapa: Implementacion
- Cambio: HOTFIX de produccion en `Controllers/VentasController.cs` (`ListarVentas`). Se separo la query de paginacion en dos pasos: (1) obtener `pageIds` (Skip/Take sobre `Select(v => v.Id)`, sin Includes de coleccion), (2) segunda query con los Include necesarios (`Cliente`, `Usuario`, `Facturas`, `Pagos`, `ProductosVenta`) filtrando por `pageIds.Contains(v.Id)`, sin Skip/Take ni OrderBy dinamico, reordenada en memoria con `pageIds.IndexOf` para preservar el orden. Resto del metodo (busqueda, filtros, proyeccion final) sin cambios.
- Motivo: HOTFIX de bug de produccion — excepcion de proceso explicita del cliente, se salteo discovery/analisis/diseno/arquitectura/presupuesto para este caso puntual. Bug: 500 intermitente (`NullReferenceException` en `MySql.Data.EntityFramework.SelectStatement.AddColumn`) al filtrar el listado de Ventas por numero, causado por el provider EF6-MySQL (discontinuado) al no soportar 3 Include de coleccion + WHERE complejo + OrderBy dinamico + Skip/Take combinados en la misma IQueryable.
- Impacto en capas: Web (Controllers) unicamente. Sin cambios en Domain/Application/Infrastructure. Sin migraciones EF.
- Riesgos/supuestos: Build verificado con MSBuild, exit code 0 (sin errores nuevos). Se detecto el mismo patron de riesgo en `PagosController.ListarPagos` (linea ~168) — no tocado, fuera de alcance de este hotfix, reportado para evaluacion futura. Pruebas minimas de QA requeridas: filtrar Ventas por numero exacto (caso que rompia), por texto de cliente, por importe, por fecha, por estado, combinando con paginacion (pagina 2+), ordenamiento por columna (incluida columna Cliente) y con filtro `pendientePago`, verificando que el orden y el conteo (`recordsTotal`) se mantengan identicos al comportamiento previo al fix (sin el bug).

### 2026-07-01 - qa-mvc
- Etapa: Pruebas funcionales (QA de hotfix, sin discovery/diseno/arquitectura/presupuesto previos -- excepcion de proceso autorizada por el cliente para este caso puntual)
- Cambio: Validacion del hotfix en `Controllers/VentasController.cs::ListarVentas`. Se releyo el metodo completo (838 lineas), se re-ejecuto Rebuild con MSBuild 2022 sobre `DeliciasNaturales.sln` (exit limpio, mismos warnings preexistentes que reporto el implementador) y se trazaron por codigo los 7 escenarios minimos dejados por el implementador: filtro por numero exacto, filtro por texto/importe/fecha/estado, combinacion filtro+paginacion pagina 2+ (preserva orden via `pageIds.IndexOf`), ordenamiento por cada columna incluida Cliente, `pendientePago` combinado con busqueda por numero, estabilidad de `recordsTotal`/`recordsFiltered`, y alimentacion correcta de columnas calculadas (`GetTotalEfectivo`/`GetTotalBanco`/`GetMontoRestante`/`GetPorcentajePagado`) sobre `ventasDB` materializado con los 5 Include. Resultado: 7/7 PASS por revision estatica rigurosa (no se ejecuto e2e real via navegador -- se confirmo MySQL en localhost:3306 e IIS Express disponibles, pero no se armo harness de autenticacion por cookie no solicitado). Se creo el item DN-001 (blocker) en `C:/Sistemas/Agentes-IA/docs/qa/regresiones-manuales.yml` porque el bug no estaba catalogado previamente. Se confirmo por lectura de codigo el riesgo identico en `PagosController.ListarPagos` (linea ~168: `Include(p => p.Venta.Facturas)` + WHERE/OrderBy dinamico + Skip/Take en la misma IQueryable) y se catalogo como DN-002 (major, NO corregido, requiere autorizacion explicita antes de tocarlo).
- Motivo: Cierre del gate QA del hotfix de produccion antes de autorizar merge. Cumplimiento de la obligacion del catalogo cross-proyecto (`30-qa-regresiones`): todo bug funcional corregido debe quedar registrado en `regresiones-manuales.yml` antes del merge.
- Impacto en capas: Ninguno adicional (QA no modifico codigo de produccion; el fix ya estaba aplicado por el implementador). Se agregaron 2 items al catalogo de QA compartido (`docs/qa/regresiones-manuales.yml`).
- Riesgos/supuestos: GO para merge del hotfix de Ventas. Riesgo residual MEDIO abierto en Pagos (DN-002) documentado y NO corregido por decision explicita de alcance (el orquestador/cliente debe autorizar ese fix por separado). Riesgo BAJO general: provider EF6-MySQL discontinuado, recomendable auditar otros `ListarX` con DataTable del sistema a futuro.

### 2026-07-01 - documentador
- Etapa: Documentacion
- Cambio: Reporte de negocio para el CEO explicando que mide cada indicador de los 6 modulos del dashboard (Ventas, Productos, Rentabilidad, Pedidos, Clientes) y como impacta en decisiones comerciales, mas un analisis comparativo real de enero a junio 2026. Entregable: `docs/delicias-naturales/reporte-dashboards-ceo-2026-07.md`.
- Motivo: Pedido directo del cliente ("ultima modificacion en los dashboards" + necesidad de explicar utilidad de negocio y mandar comparativo al CEO). No es una feature de codigo, por lo que se salteo discovery/analisis/diseno/arquitectura/presupuesto (excepcion de proceso, sin objecion del cliente). Se autorizo explicitamente una conexion de solo lectura a la base de produccion (host mysql5049.site4now.net) para sacar numeros reales en vez de placeholders.
- Impacto en capas: Ninguno en codigo. Solo consulta de lectura (SELECT agregados) contra produccion, conexion unica y corta, sin escritura.
- Riesgos/supuestos: Se detecto y reporto una anomalia de datos (pago con fecha fuera de rango, "2026-12", ~$163.781) excluida del analisis; pendiente que el cliente la corrija. Julio 2026 excluido del comparativo por ser mes en curso.
