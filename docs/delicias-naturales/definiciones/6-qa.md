# Memoria - QA

## Proyecto: DeliciasNaturales
## Ultima actualizacion: 2026-07-01

## Estado go/no-go
GO -- Hotfix de Ventas validado por revision estatica rigurosa + build real (MSBuild) ejecutado por QA. 7/7 escenarios PASS por trazado de codigo. 0 defectos nuevos en el alcance del hotfix. 1 riesgo residual documentado y catalogado (DN-002, PagosController), fuera de alcance, no autorizado a corregir.

## Defectos resueltos (historico)
- DEF-001 CRITICO: Vendedor creaba en VerificadoDeposito -- fixed controller+vista
- DEF-002 MAYOR: Default modal Sumar -- fixed a Pisar
- DEF-003 MAYOR: Falta banner rol en Create -- fixed
- DEF-004 MENOR: Falta badge Actualizado -- fixed

## Defectos catalogados en esta etapa
- DN-001 BLOCKER (catalogo cross-proyecto `regresiones-manuales.yml`): NullReferenceException en `MySql.Data.EntityFramework.SelectStatement.AddColumn` al filtrar `/Ventas/ListarVentas` por numero, con 3 Include de coleccion + WHERE/OrderBy dinamico + Skip/Take combinados. FIXED por el implementador en `Controllers/VentasController.cs` (separacion pageIds / ventasDB). Validado por QA (build real + trazado de los 7 escenarios). Item creado en el catalogo porque no existia previamente.
- DN-002 MAJOR (catalogo cross-proyecto, NO corregido): mismo patron de riesgo confirmado por lectura de codigo en `Controllers/PagosController.cs::ListarPagos` (linea ~168): `Include(p => p.Venta.Facturas)` (coleccion) + WHERE dinamico + OrderBy dinamico (incluye rama especial para columna "Cliente") + `Skip/Take` en la misma `IQueryable`, antes de materializar. No hay reporte de sintoma real en produccion todavia (a diferencia de DN-001). NO corregido: fuera de alcance de este hotfix, requiere autorizacion explicita antes de tocarlo.

## Riesgos de liberacion
- BAJO (historico): Migracion EF aplicada por SQL directo. Regenerar con Add-Migration en dev si se necesita snapshot limpio.
- MEDIO: `PagosController.ListarPagos` tiene el mismo patron de riesgo que causo DN-001 (ver DN-002). Puede manifestarse como 500 intermitente en produccion ante ciertas combinaciones de filtro+orden+paginacion. Mitigacion: aplicar el mismo patron de fix (separar IDs de pagina de entidades con Include) cuando el cliente autorice, o preventivamente si reaparecen sintomas de 500 en Pagos.
- BAJO: El provider `MySql.Data.EntityFramework` sigue discontinuado. Recomendado (fuera de este hotfix) auditar el resto de los `ListarX` con DataTable del sistema buscando el mismo patron (Include de coleccion + Skip/Take + OrderBy dinamico combinados en una sola query) antes de que se conviertan en blockers de produccion.
- Limitacion de entorno: no se ejecuto una prueba end-to-end real via navegador/HTTP contra el sitio levantado (requeriria resolver login por cookie del pipeline de Identity y datos representativos en la base `delicias`). Se confirmo MySQL escuchando en localhost:3306 e IIS Express disponible, pero se opto por no armar un harness de autenticacion no solicitado. La validacion funcional se hizo por revision estatica rigurosa (trazado linea por linea de cada escenario) + build real (MSBuild Rebuild, exit limpio, mismos warnings preexistentes que reporto el implementador).

## Historial de ajustes
- 2026-05-27: QA inicial ciclo mejoras stock. 4 defectos detectados y auto-fixed. Build OK.
- 2026-07-01: QA de HOTFIX de produccion (sin discovery/diseno/arquitectura/presupuesto previos, excepcion de proceso autorizada por el cliente para este caso puntual). Alcance: `Controllers/VentasController.cs::ListarVentas`. Se releyo el metodo completo, se re-corrio Rebuild con MSBuild 2022 (exit limpio, mismos warnings preexistentes) y se trazaron los 7 escenarios minimos dejados por el implementador -- los 7 PASS por revision estatica. Se catalogo el bug como DN-001 en `regresiones-manuales.yml` (no existia previamente) y se confirmo por lectura de codigo el riesgo residual en `PagosController.ListarPagos` (linea ~168), catalogado como DN-002 (major, NO corregido, requiere autorizacion). No se detectaron defectos nuevos dentro del alcance de Ventas. GO para merge del hotfix de Ventas.

