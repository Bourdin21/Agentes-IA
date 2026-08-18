# Memoria - Arquitecto MVC

## Proyecto: labipac
## Ultima actualizacion: 2026-07-23

## Definiciones vigentes

> Nota: el proyecto fue renombrado de `BlankProject.*` a `LabIPAC.*` entre la arquitectura original (2026-06-13) y la sesion 2 (2026-07-08) — todas las referencias de namespace de esta seccion ya usan `LabIPAC.*`, el nombre vigente.

### Alcance funcional resumido
Sistema de gestion de produccion mensual de laboratorio. Catalogos: Unidades Bioquimicas ("Practicas" en UI), Practicas ("Perfiles" en UI, con composicion M:N informativa), Centros de Salud (Privado/Mutual). Produccion Mensual con snapshot de precio por linea, opcionalmente asociada a un Centro de Salud, con carga individual o masiva. Precio de Perfil derivado de `Unidad × PrecioPorUnidad` (configuracion global unica).

### Domain (`LabIPAC.Domain`)
- `Entities/UnidadBioquimica.cs` — hereda `SoftDestroyable`. `Nombre` (MaxLength 150), `PrecioActual` (decimal 18,2, editable directamente).
- `Entities/Practica.cs` — hereda `SoftDestroyable`. `Nombre` (MaxLength 150), `Unidad` (int, **agregado en sesion 2**), `PrecioActual` (decimal 18,2, **ya no editable por el usuario** — calculado y persistido como `Unidad × PrecioPorUnidad` vigente, se mantiene persistido y no computed-on-read para no romper `AgregarLinea`/`GetPrecioItem`/reportes que lo leen directo).
- `Entities/PracticaDetalle.cs` — hereda `SoftDestroyable`. FK `PracticaId` + FK `UnidadBioquimicaId` (composicion M:N, informativa desde sesion 2 — ya no valida ni determina el precio).
- `Entities/PrecioPorUnidad.cs` — **nuevo en sesion 2**, hereda `SoftDestroyable`. `Valor` (decimal). Patron de fila unica (analogo a la unicidad Mes+Año de `ProduccionMensual`): solo debe existir una fila activa, enforced en Service, no en DB.
- `Entities/ProduccionMensual.cs` — hereda `SoftDestroyable`. `Mes` (int), `Anio` (int), `Notas` (string?, MaxLength 500), `CentroSaludId` (int?, **agregado en sesion 3**) + nav `CentroSalud?`.
- `Entities/ProduccionDetalle.cs` — hereda `SoftDestroyable`. FK `ProduccionMensualId`, `TipoItem` (enum), `PracticaId?`/`UnidadBioquimicaId?` (FKs nullable, exactamente una debe ser non-null), `NombreSnapshot` (MaxLength 200), `PrecioSnapshot` (decimal 18,2), `Cantidad` (int).
- `Entities/CentroSalud.cs` — **nuevo en sesion 3**, hereda `SoftDestroyable`. `Nombre` (string, requerido), `Tipo` (`TipoCentroSalud`), `Activo` (bool, default true) — mismo shape que `UnidadBioquimica.cs` salvo `Tipo`.
- `Enums/TipoItemProduccion.cs` — `Practica = 1`, `UnidadBioquimica = 2`.
- `Enums/TipoCentroSalud.cs` — **nuevo en sesion 3** — `Privado = 1`, `Mutual = 2`.

### Application (`LabIPAC.Application`)
- `Interfaces/IUnidadBioquimicaService.cs` — `GetAllAsync`, `GetActivasAsync`, `GetByIdAsync`, `CreateAsync`, `UpdateAsync`, `DeleteAsync`, `RestoreAsync`.
- `Interfaces/IPracticaService.cs` — mismo shape base + (sesion 2) `CreateAsync`/`UpdateAsync` reciben `Unidad` (no `PrecioActual`, calculado internamente); `Task<decimal> ObtenerPrecioPorUnidadVigenteAsync()`, `Task<ServiceResult> ActualizarPrecioPorUnidadAsync(decimal nuevoValor)`, `Task<ServiceResult> AumentarPrecioPorUnidadPorcentajeAsync(decimal porcentaje)` (ambos recalculan en batch el `PrecioActual` de todas las Practicas activas en la misma operacion). **Sin validacion RN-01** (`PrecioActual < SumatoriaComponentes`, derogada). **Decision arquitectonica:** no se creo una interfaz `IPrecioPorUnidadService` separada — el valor no tiene sentido de negocio fuera del calculo de precio de Practica (evita dependencia circular y una interfaz nueva para un unico valor).
- `Interfaces/IProduccionMensualService.cs` — `GetAllAsync`, `GetByIdAsync`, `CreateAsync` (unicidad Mes+Año+CentroSaludId desde sesion 3, RN-24), `DeleteAsync`, `GetPrecioVigente`, `AgregarLineaAsync`, `EditarLineaAsync`, `EliminarLineaAsync`, + (sesion 2) `AgregarLineasAsync(int produccionMensualId, IEnumerable<ProduccionDetalleLineaDto> lineas)` (guardado atomico de carga masiva).
- `Interfaces/ICentroSaludService.cs` — **nuevo en sesion 3**, mismo contrato que `IUnidadBioquimicaService`.
- `Interfaces/IRepository.cs` — `Task RestoreAsync(T entity)` (reactivar soft-deleted).
- DTOs: `UnidadBioquimicaDtos.cs`; `PracticaDtos.cs` (`PracticaSummaryDto` +`Unidad`, sin `PrecioActual` de entrada); `ProduccionMensualDtos.cs` (+`CentroSaludId`, +`NombreCentroSalud`, + `ProduccionDetalleLineaDto` para carga masiva); `CentroSaludDtos.cs` (`CentroSaludSummaryDto`, `CentroSaludCreateDto`/`UpdateDto`).

### Infrastructure (`LabIPAC.Infrastructure`)
- `Data/AppDbContext.cs` — `DbSet<UnidadBioquimica>`, `DbSet<Practica>`, `DbSet<PracticaDetalle>`, `DbSet<ProduccionMensual>`, `DbSet<ProduccionDetalle>`, `DbSet<PrecioPorUnidad>` (sesion 2), `DbSet<CentroSalud>` (sesion 3, Fluent API: `Nombre` MaxLength 150 requerido; FK `ProduccionMensual.CentroSaludId → CentroSalud` con `OnDelete(DeleteBehavior.Restrict)` para no arrastrar baja fisica sobre historial).
- `Repositories/Repository.cs` — `RestoreAsync` (`entity.DeletedAt = null`, `entity.DeletedByUserId = null`).
- `Services/UnidadBioquimicaService.cs` — implementa `IUnidadBioquimicaService`.
- `Services/PracticaService.cs` — implementa `IPracticaService`; usa `IgnoreQueryFilters()` para sumatoria de componentes (informativa); `CreateAsync`/`UpdateAsync` leen el `PrecioPorUnidad` vigente y calculan `PrecioActual = Unidad × valorVigente.Valor` antes de guardar; `ActualizarPrecioPorUnidadAsync` actualiza `Valor` y recorre `Practicas.Where(Activo && DeletedAt == null)` recalculando `PrecioActual`, `SaveChangesAsync` unico (atomico); `AumentarPrecioPorUnidadPorcentajeAsync` calcula `nuevoValor = Math.Round(valorActual × (1 + pct/100m), 2, MidpointRounding.AwayFromZero)` y reusa `ActualizarPrecioPorUnidadAsync`. Sin el chequeo `PrecioActual < SumatoriaComponentes`.
- `Services/ProduccionMensualService.cs` — implementa `IProduccionMensualService`; `CreateAsync` valida unicidad `Mes+Año+CentroSaludId` (comparacion explicita del caso `centroSaludId == null`, EF traduce `==` con nulls a SQL `IS NULL` sin logica especial adicional); `GetAllAsync`/`GetByIdAsync` con `.Include(p => p.CentroSalud)`; `AgregarLineasAsync` valida cada linea (item activo/existente, cantidad >=1, sin duplicados TipoItem+ItemId en el batch — RN-13), `AddRange` + `SaveChangesAsync` unico (atomicidad natural de EF).
- `Services/CentroSaludService.cs` — **nuevo en sesion 3**, implementa `ICentroSaludService`, calco de `UnidadBioquimicaService.cs`.
- `DependencyInjection.cs` — registra `IUnidadBioquimicaService`, `IPracticaService`, `IProduccionMensualService`, `ICentroSaludService` como Scoped.

### Web (`LabIPAC.Web`)
- `Controllers/UnidadesBioquimicasController.cs` — Index, Create, Edit, Delete, Restore.
- `Controllers/PracticasController.cs` — Index, Details, Create, Edit, Delete, Restore; (sesion 2) `Index` pasa `PrecioPorUnidadVigente`; `Create`/`Edit` GET pasan `PrecioPorUnidadVigente` (calculo en vivo por JS), POST reciben `Unidad` en vez de `PrecioActual`; acciones AJAX nuevas `ActualizarPrecioPorUnidad`/`AumentarPrecioPorUnidadPorcentaje` (`RequireAdministracion`).
- `Controllers/ProduccionMensualController.cs` — Index, Create, Detalle, Delete, AgregarLinea, EditarLinea, EliminarLinea, GetPrecioItem (AJAX); (sesion 2) `CargaMasiva` GET/POST (`[Authorize]` sin politica), `CrearPerfilRapido`/`CrearPracticaRapido` (POST AJAX, JSON `{success, id, nombre, precio}`), `ReportePdf` con columna "Precio unit." de 75pt (antes 55) y "Tipo" de 60pt (antes 65); (sesion 3) `Create` pasa `CentrosSaludDisponibles`, `Index`/`Historial` pasan `NombreCentroSalud`, `ReportePdf` agrega linea condicional de Centro de Salud en el encabezado.
- `Controllers/PreciosController.cs` — **simplificado en sesion 2**: se elimino toda la logica de cascade UB→Perfil y seleccion de Perfiles en `AumentoMasivo`/`Previsualizar`/`AplicarAumento` — opera solo sobre `UnidadBioquimica` (~40% menos codigo: se fueron `cascadeDict`, `perfilesDeltaAcum`, los `Include(u => u.PracticaDetalles)`). Deuda tecnica preexistente sin corregir en ese alcance: accede a `AppDbContext` directo en vez de via Service (viola `01-fronteras-por-capa`), se preservo el patron para minimizar riesgo.
- `Controllers/CentrosSaludController.cs` — **nuevo en sesion 3**, calco de `UnidadesBioquimicasController.cs` (Index, Create, Edit, Delete, Restore).
- ViewModels: `UnidadBioquimicaViewModels.cs`; `PracticaViewModels.cs` (`Create`/`EditViewModel` sin `PrecioActual`, con `Unidad` `[Range(1, int.MaxValue)]` y `PrecioPorUnidadVigente` solo lectura; `RowViewModel` +`Unidad`; nuevo `PrecioPorUnidadViewModel`); `ProduccionMensualViewModels.cs` (+`CentroSaludId`/`CentrosSaludDisponibles`/`NombreCentroSalud`; nuevos `ProduccionCargaMasivaViewModel`, `ProduccionCargaMasivaFilaViewModel`, `PerfilAltaRapidaViewModel`, `PracticaAltaRapidaViewModel`); `PreciosViewModels.cs` (`AumentoMasivoViewModel` sin `PerfilesSeleccionados`); `CentroSaludViewModels.cs` (nuevo).
- Vistas: 10 vistas base (Unidades Bioquimicas, Practicas, Produccion Mensual) + `ProduccionMensual/CargaMasiva.cshtml` + 2 partials de modal (`_ModalAltaRapidaPerfil`, `_ModalAltaRapidaPractica`) + `Practicas/Index/Create/Edit` ajustadas + `Precios/AumentoMasivo` (sin tab Perfiles) + `CentrosSalud/Index.cshtml`/`Create.cshtml` (compartida con Edit via partial).
- `Views/Shared/_Layout.cshtml` — sidebar: Unidades Bioquimicas, Practicas, Produccion Mensual, Centros de Salud.

### Decision arquitectonica — relajacion global de RN-02
El Diseño (DD-01) pedia relajar RN-02 ("Practica requiere al menos 1 componente") solo para el flujo de alta rapida. Arquitectura propuso y el cliente confirmo relajarla **globalmente**: mantener una unica validacion (sin flags condicionales `esAltaRapida`) es mas simple, y la composicion ya dejo de determinar el precio (RN-01 derogada) — `PracticaCreateViewModel`/`Edit` ya no exigen minimo 1 `UnidadBioquimicaId` en ningun flujo.

### Modelo de permisos
Sin roles ni policies nuevos. `[Authorize]` sin politica especifica: todos los ABM (Unidades Bioquimicas, Practicas, Centros de Salud), `CargaMasiva`, `CrearPerfilRapido`, `CrearPracticaRapido`, `AgregarLinea`. `[Authorize(Policy = "RequireAdministracion")]`: `ActualizarPrecioPorUnidad`, `AumentarPrecioPorUnidadPorcentaje` (mismo criterio que `PreciosController`/guardado de IVA).

### Migraciones EF (historico acumulado, todas aplicadas)
1. **`AddLabipacEntities`** (2026-06-13): crea `UnidadesBioquimicas`, `Practicas`, `PracticaDetalles`, `ProduccionMensuales`, `ProduccionDetalles`. Sin tablas modificadas. Riesgo de rollback: nulo.
2. **`AddPracticaUnidadYPrecioPorUnidad`** (2026-07-08): `ALTER TABLE Practicas ADD COLUMN Unidad int NOT NULL DEFAULT 0`; `CREATE TABLE PreciosPorUnidad` (+seed `Valor=892.03`). **Backfill obligatorio** (riesgo critico RA-06, ver Riesgos): `UPDATE Practicas SET Unidad = GREATEST(1, ROUND(PrecioActual / 892.03)) WHERE DeletedAt IS NULL` — sin este backfill, los Perfiles existentes quedarian con precio calculado $0. Confirmado con el cliente que la aproximacion automatica es aceptable. Riesgo de rollback: bajo.
3. **`AddCentroSaludYProduccionMensualCentroSalud`** (2026-07-23): `CREATE TABLE CentrosSalud`; `ALTER TABLE ProduccionMensuales ADD COLUMN CentroSaludId int NULL` + FK `ON DELETE RESTRICT`. Sin backfill — periodos existentes quedan con `CentroSaludId = NULL` (comportamiento esperado, P13). Riesgo de rollback: bajo.

### Riesgos y supuestos vigentes
- **RA-01:** baja logica de UnidadBioquimica con composicion activa en Practica — ya no impacta el precio (derivado de `Unidad × PrecioPorUnidad`, no de la composicion), se mantiene badge informativo si un componente esta inactivo. Residual: bajo.
- **RA-02:** `ProduccionDetalle` con 2 FK nullable — Service valida exactamente una non-null. Residual: muy bajo.
- **RA-03 / RA-10:** sin unique DB index para Mes+Año(+CentroSaludId desde sesion 3) en `ProduccionMensual` (MySQL no soporta partial index nativo) — unicidad enforced en Service. Residual: minimo (monousuario).
- **RA-04:** AJAX `GetPrecioItem` con item inactivo/inexistente — Service retorna `decimal?` null, Controller `{ success: false }`, JS bloquea el modal. Residual: bajo.
- **RA-05:** decimal binding en es-AR — cubierto por `InvariantDecimalModelBinder` ya existente.
- **RA-06 (critico, sesion 2):** mitigado por el backfill de la migracion 2 (ver arriba) — el valor de `Unidad` resultante es una aproximacion, el usuario debe revisar/ajustar Perfiles existentes despues del deploy.
- **RA-07:** al remover el cascade de F-001, un Perfil cuyo precio dependia de aumentos previos via cascade queda "congelado" hasta el primer recalculo (creacion/edicion o cambio de `PrecioPorUnidad`) — comportamiento esperado segun P10, no es un bug.
- **RA-08:** recalculo batch de `PrecioActual` en todas las Practicas activas al cambiar `PrecioPorUnidad` es O(n) — sin impacto de performance al volumen esperado (mono-laboratorio).
- **RA-09:** `PreciosController` sigue con `AppDbContext` inyectado directo (deuda tecnica preexistente, no introducida por este cambio) — simplificado pero no refactorizado a Service.
- **RA-11:** `DeleteBehavior.Restrict` en `ProduccionMensual.CentroSaludId → CentroSalud` impide eliminar fisicamente un `CentroSalud` referenciado — coherente con baja logica (`DeleteAsync` de `CentroSaludService` hace soft-delete, no deberia disparar en operacion normal).
- **RA-12:** convivencia sin vinculo entre `CentroSalud` (nuevo) y `Mutual` (FABA existente) — deuda conceptual aceptada explicitamente por el cliente (P12/DD-05), no se corrige en este alcance.
- **SA-01 a SA-05 (supuestos originales, vigentes):** cultura es-AR + `InvariantDecimalModelBinder` ya configurados; global query filter `SoftDestroyable` automatico en entidades nuevas; `AuditLog` automatico en `SaveChangesAsync` sin config adicional; DataTables client-side suficiente al volumen esperado; sin paquetes NuGet nuevos requeridos en ningun ciclo.

### Gate de aprobacion
ARQUITECTURA CERRADA (los 3 ciclos). Sin bloqueos tecnicos pendientes. Confirmado con el cliente: relajacion global de RN-02, criterio de backfill de `Unidad`. Lista para presupuesto/implementacion.

## Historial de ajustes
- 2026-06-13: Arquitectura completa producida (base). 6 entidades nuevas, 3 interfaces de servicio, 6 archivos de DTOs, 16 archivos Web, 4 archivos existentes modificados, 1 migracion EF (`AddLabipacEntities`). En ese momento bajo namespace `BlankProject.*` (renombrado a `LabIPAC.*` antes de la sesion 2).
- 2026-07-08 (sesion 2): Arquitectura de 3 mejoras — `Unidad`/`PrecioPorUnidad` reemplazando el precio manual y simplificando F-001 (elimina cascade UB→Perfil de `PreciosController`), pantalla de carga masiva + alta rapida atomica (`AgregarLineasAsync`), fix de ancho de columna del PDF. Decision arquitectonica de relajar RN-02 globalmente (no solo en alta rapida), confirmada por el cliente. 1 entidad nueva (`PrecioPorUnidad`), 1 migracion EF con backfill critico (RA-06, mitigado).
- 2026-07-23 (sesion 3): Arquitectura de Produccion Mensual por Centro de Salud. 1 entidad nueva (`CentroSalud`), 1 enum nuevo (`TipoCentroSalud`), 1 campo nuevo (`ProduccionMensual.CentroSaludId`), 1 interfaz de servicio nueva (`ICentroSaludService`), RN-24 reemplaza RN-11. 1 migracion EF sin backfill.
- 2026-08-16: Reestructuración documental — este archivo tenia 3 secciones de nivel 2 apiladas por sesion (Sesion 3, Sesion 2, y la arquitectura base sin encabezado de sesion) con **3 encabezados `## Historial de ajustes` duplicados** intercalados entre ellas, y la arquitectura base seguia referenciando el namespace `BlankProject.*` ya renombrado. Consolidado en una unica `## Definiciones vigentes` (namespaces corregidos a `LabIPAC.*`, estado final de Domain/Application/Infrastructure/Web/permisos/migraciones/riesgos) + este historial cronologico unico. Ningun dato funcional se perdio.
