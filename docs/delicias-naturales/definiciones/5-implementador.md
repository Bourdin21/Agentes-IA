# Memoria - Implementador

## Proyecto: delicias-naturales
## Ultima actualizacion: 2026-07-01

## Definiciones vigentes

### Archivos y capas modificadas
- `Controllers/VentasController.cs` (Web/Presentacion — coordinacion HTTP, sin logica de negocio nueva): metodo `ListarVentas`, bloque de paginacion (antes lineas ~157-164).

### Migraciones EF generadas
- Ninguna. Fix es puramente de forma de consulta LINQ, no toca el modelo ni el esquema.

### Riesgos residuales
- `PagosController.ListarPagos` (linea ~168) tiene el mismo patron de riesgo: Include de coleccion (`Venta.Facturas`) + WHERE complejo + OrderBy dinamico + Skip/Take en la misma query. Riesgo menor que el de Ventas (un solo Include de coleccion vs. tres), pero la causa raiz (provider EF6-MySQL discontinuado no soporta bien esa combinacion) es la misma. No se toco: fuera de alcance de este hotfix. Recomendado evaluar aplicar el mismo patron (separar IDs de pagina de entidades con Include) si aparecen sintomas similares (500 intermitente al filtrar).
- El provider `MySql.Data.EntityFramework` sigue discontinuado/sin mantenimiento activo; este tipo de bug puede reaparecer en otros listados con Include de colecciones + Skip/Take + OrderBy dinamico combinados. Vale la pena, a futuro (no en este hotfix), auditar todos los `ListarX` con DataTable del proyecto buscando el mismo patron.

### Proximos pasos pendientes
- QA funcional del fix en `/Ventas/ListarVentas` (ver pruebas minimas en trazabilidad.md / reporte de esta tarea).
- Evaluar si se quiere aplicar preventivamente el mismo patron en `PagosController.ListarPagos` (requiere decision de negocio, no autorizado en este hotfix).

## Historial de ajustes
- 2026-07-01: HOTFIX de produccion (excepcion de proceso, sin discovery/diseno/arquitectura/presupuesto previos — decision explicita del cliente para este caso puntual). Bug: 500 intermitente (`NullReferenceException` en `MySql.Data.EntityFramework.SelectStatement.AddColumn`) al filtrar `/Ventas/ListarVentas` por numero de venta. Causa raiz: 3 Include de coleccion (`Facturas`, `Pagos`, `ProductosVenta`) + WHERE complejo + OrderBy dinamico + Skip/Take en la misma IQueryable, combinacion no soportada por el provider EF6-MySQL. Fix aplicado: separar la query en dos pasos — (1) `query.Select(v => v.Id).Skip(start).Take(length)` para obtener los Ids de la pagina sin Includes de coleccion, (2) segunda query con todos los Include necesarios, filtrando por `pageIds.Contains(v.Id)`, sin Skip/Take/OrderBy dinamico, reordenada en memoria con `pageIds.IndexOf` para preservar el orden ya calculado. Build verificado con MSBuild (`DeliciasNaturales.sln`, Configuration=Debug) — exit code 0, sin errores nuevos (solo warnings preexistentes de binding redirects y TypeScript tools version). Se detecto patron identico de riesgo en `PagosController.ListarPagos` (linea ~168) — no tocado, reportado como riesgo residual.
