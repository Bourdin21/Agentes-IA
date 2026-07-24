# Memoria - Arquitecto MVC

## Proyecto: labipac
## Ultima actualizacion: 2026-07-23 (sesion 3 — arquitectura de Produccion Mensual por Centro de Salud)

## Sesion 3 (2026-07-23) — Arquitectura: Produccion Mensual por Centro de Salud

Input: `1-analista-funcional.md` sesion 5 y `2-disenador-funcional.md` sesion 3, ambos cerrados.

### 1. Alcance funcional resumido
Ver `2-disenador-funcional.md` sesion 3. Nueva entidad catalogo `CentroSalud` (Privado/Mutual), FK opcional en `ProduccionMensual`, RN-24 (unicidad Mes+Anio+CentroSaludId reemplaza RN-11), columna/filtro en listado, linea condicional en PDF.

### 2. Impacto tecnico por capa

#### Domain (`LabIPAC.Domain`)
- `Entities/CentroSalud.cs` — **nuevo**, hereda `SoftDestroyable`: `Nombre` (string, requerido), `Tipo` (`TipoCentroSalud`), `Activo` (bool, default true). Mismo shape que `UnidadBioquimica.cs` salvo el campo `Tipo`.
- `Enums/TipoCentroSalud.cs` — **nuevo**: `Privado = 1`, `Mutual = 2`.
- `Entities/ProduccionMensual.cs` — **modificado**: agregar `public int? CentroSaludId { get; set; }` + `public CentroSalud? CentroSalud { get; set; }` (nav nullable).

#### Application (`LabIPAC.Application`)
- `Interfaces/ICentroSaludService.cs` — **nuevo**: `GetAllAsync`, `GetActivasAsync`, `GetByIdAsync`, `CreateAsync`, `UpdateAsync`, `DeleteAsync`, `RestoreAsync` — mismo contrato que `IUnidadBioquimicaService`.
- `DTOs/CentroSaludDtos.cs` — **nuevo**: `CentroSaludSummaryDto` (Id, Nombre, Tipo, Activo), `CentroSaludCreateDto`/`UpdateDto` (Nombre, Tipo).
- `Interfaces/IProduccionMensualService.cs` — **modificado**: `CreateAsync` recibe `CentroSaludId` (int?) en su DTO de entrada; la validacion de unicidad interna pasa de "existe Mes+Anio" a "existe Mes+Anio+CentroSaludId" (RN-24).
- `DTOs/ProduccionMensualDtos.cs` — **modificado**: DTO de creacion +`CentroSaludId`; `ProduccionMensualSummaryDto` +`NombreCentroSalud`.

#### Infrastructure (`LabIPAC.Infrastructure`)
- `Services/CentroSaludService.cs` — **nuevo**, implementa `ICentroSaludService`, calco directo de `UnidadBioquimicaService.cs` (mismo patron CRUD + soft delete/restore).
- `Data/AppDbContext.cs` — **modificado**: +`DbSet<CentroSalud> CentrosSalud`, Fluent API (`Nombre` MaxLength 150 requerido; FK `ProduccionMensual.CentroSaludId` -> `CentroSalud`, `OnDelete(DeleteBehavior.Restrict)` para no arrastrar baja fisica sobre historial).
- `Services/ProduccionMensualService.cs` — **modificado**: `CreateAsync` — la consulta de unicidad existente (`Where(p => p.Mes == mes && p.Anio == anio)`) se extiende a `&& p.CentroSaludId == centroSaludId` (comparando explicitamente el caso `centroSaludId == null` con `p.CentroSaludId == null`, ya que EF traduce `==` con nulls correctamente a SQL `IS NULL` — no requiere lógica especial adicional a la ya usada). `GetAllAsync`/`GetByIdAsync` agregan `.Include(p => p.CentroSalud)` para poblar `NombreCentroSalud`.
- `DependencyInjection.cs` — **modificado**: registrar `ICentroSaludService` como Scoped.
- Nueva migracion EF: `AddCentroSaludYProduccionMensualCentroSalud` (detalle en seccion 4).

#### Web (`LabIPAC.Web`)
- `Controllers/CentrosSaludController.cs` — **nuevo**: acciones Index, Create, Edit, Delete, Restore — calco de `UnidadesBioquimicasController.cs`.
- `Controllers/ProduccionMensualController.cs` — **modificado**: `Create` GET pasa `CentrosSaludDisponibles` (SelectList desde `GetActivasAsync`) al ViewModel; `Create` POST pasa `CentroSaludId` al Service; `Index`/`Historial` pasan `NombreCentroSalud` mapeado; `ReportePdf` agrega linea condicional de encabezado si `CentroSaludId != null`.
- `Models/CentroSaludViewModels.cs` — **nuevo**: `CentroSaludCreateViewModel`/`EditViewModel`, `CentroSaludRowViewModel`.
- `Models/ProduccionMensualViewModels.cs` — **modificado**: `ProduccionMensualCreateViewModel` +`CentroSaludId`, +`CentrosSaludDisponibles`; `ProduccionMensualRowViewModel` +`NombreCentroSalud`; `ProduccionMensualDetalleViewModel` +`NombreCentroSalud`.
- Vistas nuevas: `Views/CentrosSalud/Index.cshtml`, `Views/CentrosSalud/Create.cshtml` (compartida con Edit via partial, mismo patron que Unidades Bioquimicas).
- Vistas modificadas: `Views/ProduccionMensual/Crear.cshtml` (selector Centro de Salud), `Views/ProduccionMensual/Index.cshtml` (columna + filtro DataTables), sidebar `_Layout.cshtml` (+1 entrada "Centros de Salud").

### 3. Modelo de permisos
Sin roles/policies nuevos. `CentrosSaludController` usa `[Authorize]` sin politica, igual que `UnidadesBioquimicasController` y `PracticasController`.

### 4. Migraciones EF requeridas
**SI** — 1 migracion: `AddCentroSaludYProduccionMensualCentroSalud`.
```
dotnet ef migrations add AddCentroSaludYProduccionMensualCentroSalud --project LabIPAC.Infrastructure --startup-project LabIPAC.Web
```
Cambios de esquema:
- `CREATE TABLE CentrosSalud` (Id, Nombre nvarchar(150), Tipo int, Activo bit, + columnas estandar `SoftDestroyable`)
- `ALTER TABLE ProduccionMensuales ADD COLUMN CentroSaludId int NULL` + FK a `CentrosSalud` (`ON DELETE RESTRICT`)
- Sin backfill de datos: los periodos existentes quedan con `CentroSaludId = NULL` (comportamiento esperado, confirmado en Analisis P13).

Riesgo de rollback: BAJO (tabla nueva + columna nullable, sin tocar datos existentes).

### 5. Riesgos y supuestos
- **RA-10:** unicidad Mes+Anio+CentroSaludId con NULL como valor propio se enforcea en Service (no en DB, MySQL no soporta unique index parcial de forma nativa sin filtered index) — mismo patron de riesgo ya aceptado para RA-03 original (Mes+Anio), residual MINIMO (monousuario).
- **RA-11:** `DeleteBehavior.Restrict` en la FK `ProduccionMensual.CentroSaludId -> CentroSalud` implica que no se puede eliminar fisicamente un `CentroSalud` referenciado por periodos existentes — coherente con el patron de baja logica (`DeleteAsync` de `CentroSaludService` hace soft-delete, no delete fisico, por lo que este caso no deberia disparar en operacion normal).
- **RA-12:** convivencia sin vinculo entre `CentroSalud` (nuevo) y `Mutual` (FABA existente) — deuda conceptual aceptada explicitamente por el cliente (P12/DD-05), no se corrige en este alcance.
- Sin riesgos nuevos sobre el mecanismo de snapshot de precios ni el calculo de totales del periodo (sin cambios).

### 6. Gate de aprobacion
ARQUITECTURA CERRADA. Sin bloqueos tecnicos. Listo para generar presupuesto.

## Historial de ajustes (agregado 2026-07-23)
- 2026-07-23: Arquitectura de Produccion Mensual por Centro de Salud. 1 entidad nueva (`CentroSalud`), 1 enum nuevo (`TipoCentroSalud`), 1 campo nuevo (`ProduccionMensual.CentroSaludId`, FK nullable). 1 interfaz de servicio nueva (`ICentroSaludService`, calco de `IUnidadBioquimicaService`), `IProduccionMensualService` ajustado (RN-24 reemplaza RN-11). 1 migracion EF sin backfill. Gate de aprobacion: CERRADO, listo para presupuesto.

## Sesion 2 (2026-07-08) — Arquitectura de 3 mejoras

Input: `1-analista-funcional.md` sesion 4 y `2-disenador-funcional.md` sesion 2, ambos cerrados.

Verificado contra codigo real (namespaces reales: `LabIPAC.*`, no `BlankProject.*` como en la arquitectura original de 2026-06-13 — el proyecto ya fue renombrado). Entidad `Practica` (Domain) = "Perfil" en UI; `UnidadBioquimica` (Domain) = "Práctica" en UI (swap de nombres ya vigente en produccion).

### 1. Alcance funcional resumido
Ver `2-disenador-funcional.md` sesion 2. Tres items: (A) Unidad + Precio por Unidad reemplazando precio manual y F-001 para Perfiles, (B) pantalla de carga masiva + alta rapida, (C) fix de ancho de columna en PDF.

### 2. Decision arquitectonica clave — simplificacion de RN-02
Se propone relajar RN-02 ("Practica requiere al menos 1 componente") **globalmente**, no solo para el flujo de alta rapida (DD-01 del diseno pedia relajarla "solo para ese flujo"). Motivo: mantener una unica validacion (sin flags condicionales `esAltaRapida`) es mas simple y consistente, y la composicion ya dejo de determinar el precio (RN-20 deroga RN-01) — mantenerla obligatoria solo en el ABM completo y opcional en alta rapida agregaria una rama de validacion sin beneficio real. Impacto: `PracticaCreateViewModel`/`Edit` ya no exigen minimo 1 `UnidadBioquimicaId`. Confirmar con cliente en Presupuesto si esto es aceptable (bajo riesgo, ya que la composicion sigue pudiendose cargar y editar, solo deja de ser obligatoria).

### 3. Impacto tecnico por capa

#### Domain (`LabIPAC.Domain`)
- `Entities/Practica.cs` — **modificado**: agregar `public int Unidad { get; set; }`. Se mantiene `PrecioActual` (ya no editable por el usuario, pasa a ser un campo calculado y persistido — se conserva persistido, no computed-on-read, para no romper `AgregarLinea`/`GetPrecioItem`/reportes que leen `PrecioActual` directamente).
- `Entities/PrecioPorUnidad.cs` — **nuevo**, hereda `SoftDestroyable`: `public decimal Valor { get; set; }`. Patron de fila unica (analogo a `ProduccionMensual` con unicidad Mes+Anio enforced en Service, RA-03 original): solo debe existir una fila activa; se enforce en Service, no en DB.

#### Application (`LabIPAC.Application`)
- `Interfaces/IPracticaService.cs` — **modificado**:
  - `CreateAsync`/`UpdateAsync`: DTO cambia de `PrecioActual` editable a `Unidad` (int). El precio se calcula internamente (`Unidad * PrecioPorUnidad vigente`) antes de persistir.
  - Nuevos metodos: `Task<decimal> ObtenerPrecioPorUnidadVigenteAsync()`, `Task<ServiceResult> ActualizarPrecioPorUnidadAsync(decimal nuevoValor)`, `Task<ServiceResult> AumentarPrecioPorUnidadPorcentajeAsync(decimal porcentaje)`. Ambos metodos de actualizacion persisten el nuevo valor y **recalculan en la misma operacion** el `PrecioActual` de todas las Practicas activas no eliminadas (batch, una sola transaccion/`SaveChangesAsync`).
  - Se elimina la validacion RN-01 (`PrecioActual < SumatoriaComponentes`) del `CreateAsync`/`UpdateAsync`.
  - Se relaja RN-02 (ver seccion 2): `UnidadBioquimicaIds` pasa a ser opcional (0..N).
  - Se decide **no** crear una interfaz `IPrecioPorUnidadService` separada — se mantiene cohesionado dentro de `IPracticaService` porque el valor de PrecioPorUnidad no tiene sentido de negocio fuera del calculo de precio de Practica (evita una dependencia circular entre dos servicios y una interfaz nueva para un unico valor).
- `Interfaces/IProduccionMensualService.cs` — **modificado**: nuevo metodo `Task<ServiceResult> AgregarLineasAsync(int produccionMensualId, IEnumerable<ProduccionDetalleLineaDto> lineas)` para el guardado atomico de la carga masiva (RN-12).
- `DTOs/PracticaDtos.cs` — **modificado**: `PracticaSummaryDto` +campo `Unidad`. Nuevos DTOs: `PracticaCreateDto`/`PracticaUpdateDto` (si no existen ya como tales, verificar en Infrastructure — hoy el mapeo se hace directo desde ViewModel a entidad segun `PracticaService` real) — ajustar quitando `PrecioActual` de entrada y agregando `Unidad`.
- `DTOs/ProduccionMensualDtos.cs` — **nuevo**: `ProduccionDetalleLineaDto` (TipoItem, ItemId, Cantidad, PrecioSnapshot) para `AgregarLineasAsync`.

#### Infrastructure (`LabIPAC.Infrastructure`)
- `Data/AppDbContext.cs` — **modificado**: +`DbSet<PrecioPorUnidad> PreciosPorUnidad`, Fluent API config (`Valor` decimal(18,2)).
- `Services/PracticaService.cs` — **modificado**:
  - `CreateAsync`/`UpdateAsync`: leer el `PrecioPorUnidad` vigente (`.Where(x => x.DeletedAt == null).First()`), calcular `PrecioActual = Unidad * valorVigente.Valor` antes de guardar.
  - Nuevo: `ActualizarPrecioPorUnidadAsync` — actualiza `Valor` de la fila vigente y recorre `Practicas.Where(p => p.Activo && DeletedAt == null)` recalculando `PrecioActual = p.Unidad * nuevoValor`, `SaveChangesAsync` unico (atomico por diseno de EF).
  - Nuevo: `AumentarPrecioPorUnidadPorcentajeAsync` — `nuevoValor = Math.Round(valorActual * (1 + pct/100m), 2, MidpointRounding.AwayFromZero)` (mismo criterio de redondeo que F-001, AC-01.5), luego reusa `ActualizarPrecioPorUnidadAsync`.
  - Se quita el chequeo `PrecioActual < SumatoriaComponentes` del flujo de guardado.
- `Services/ProduccionMensualService.cs` — **modificado**: nuevo `AgregarLineasAsync` — valida cada linea (item activo y existente, cantidad >=1, sin duplicados TipoItem+ItemId dentro del batch — RN-13), mapea a `ProduccionDetalle`, `AddRange` + `SaveChangesAsync` unico (atomicidad natural de EF: si falla una insercion, no se persiste ninguna).
- Nueva migracion EF: `AddPracticaUnidadYPrecioPorUnidad` (detalle en seccion 4).

#### Web (`LabIPAC.Web`)
- `Controllers/ProduccionMensualController.cs` — **modificado**:
  - Nuevas acciones: `CargaMasiva(int id)` [GET], `CargaMasiva(ProduccionCargaMasivaViewModel model)` [POST] — `[Authorize]` sin politica (igual que `AgregarLinea` hoy).
  - `CrearPerfilRapido(PerfilAltaRapidaViewModel)` [POST, AJAX, retorna JSON `{success, id, nombre, precio}`] — reusa `IPracticaService.CreateAsync`.
  - `CrearPracticaRapido(PracticaAltaRapidaViewModel)` [POST, AJAX] — reusa `IUnidadBioquimicaService.CreateAsync`, sin cambios de contrato.
  - `ReportePdf`: cambio de una linea — `c.ConstantColumn(55)` → `c.ConstantColumn(75)` para "Precio unit."; ajustar `c.ConstantColumn(65)` → `c.ConstantColumn(60)` para "Tipo" (compensa el ancho total en A4 portrait, la columna "Ítem" es `RelativeColumn` y absorbe el resto).
- `Controllers/PracticasController.cs` — **modificado**: `Index` pasa `PrecioPorUnidadVigente` al ViewModel (para la card nueva); `Create`/`Edit` GET pasan `PrecioPorUnidadVigente` (para el calculo en vivo por JS), POST ya no reciben `PrecioActual` sino `Unidad`. Nuevas acciones AJAX `ActualizarPrecioPorUnidad(decimal nuevoValor)` y `AumentarPrecioPorUnidadPorcentaje(decimal porcentaje)`, ambas `[Authorize(Policy = "RequireAdministracion")]` (mismo criterio que F-001/guardado de IVA).
- `Controllers/PreciosController.cs` — **modificado y simplificado**: se elimina toda la logica de cascade UB→Perfil y de Perfiles seleccionados directamente en `AumentoMasivo` (GET), `Previsualizar` (POST) y `AplicarAumento` (POST) — quedan operando **solo** sobre `UnidadBioquimica`. Esto reduce la complejidad del controller (se elimina ~40% del codigo actual: `cascadeDict`, `perfilesDeltaAcum`, los `Include(u => u.PracticaDetalles)`, etc.). Nota de deuda tecnica preexistente: este controller accede a `AppDbContext` directamente en vez de a traves de un Service (viola 01-fronteras-por-capa) — se preserva el patron existente para minimizar riesgo, no se corrige en este alcance (no fue pedido).
- `Models/PracticaViewModels.cs` — **modificado**: `PracticaCreateViewModel`/`EditViewModel` quitan `PrecioActual` (input), agregan `Unidad` (int, `[Range(1, int.MaxValue)]`) y `PrecioPorUnidadVigente` (decimal, solo lectura para JS). `PracticaRowViewModel` +`Unidad`. Nuevo `PrecioPorUnidadViewModel` (ValorActual, NuevoValor, PorcentajeAumento).
- `Models/ProduccionMensualViewModels.cs` — **modificado**: nuevos `ProduccionCargaMasivaViewModel`, `ProduccionCargaMasivaFilaViewModel`, `PerfilAltaRapidaViewModel`, `PracticaAltaRapidaViewModel`.
- `Models/PreciosViewModels.cs` — **modificado**: `AumentoMasivoViewModel` quita `PerfilesSeleccionados`.
- Vistas nuevas: `Views/ProduccionMensual/CargaMasiva.cshtml` (+ 2 partials de modal: `_ModalAltaRapidaPerfil.cshtml`, `_ModalAltaRapidaPractica.cshtml`).
- Vistas modificadas: `Views/ProduccionMensual/Detalle.cshtml` (boton "Carga masiva"), `Views/Practicas/Index.cshtml` (card Precio por Unidad + columna Unidad), `Views/Practicas/Create.cshtml`/`Edit.cshtml` (quitar precio editable, agregar Unidad + calculo en vivo), `Views/Precios/AumentoMasivo.cshtml` (quitar tab Perfiles).

### 4. Modelo de permisos
Sin roles/policies nuevos. Se reutilizan:
- `[Authorize]` sin politica: `CargaMasiva`, `CrearPerfilRapido`, `CrearPracticaRapido` (igual que ABM y `AgregarLinea` existentes).
- `[Authorize(Policy = "RequireAdministracion")]`: `ActualizarPrecioPorUnidad`, `AumentarPrecioPorUnidadPorcentaje` (igual criterio que F-001 y `ActualizarIva`).
- `PreciosController` mantiene su `[Authorize(Policy = "RequireAdministracion")]` a nivel de clase, sin cambios.

### 5. Migraciones EF requeridas
**SI** — 1 migracion: `AddPracticaUnidadYPrecioPorUnidad`.
```
dotnet ef migrations add AddPracticaUnidadYPrecioPorUnidad --project LabIPAC.Infrastructure --startup-project LabIPAC.Web
```
Cambios de esquema:
- `ALTER TABLE Practicas ADD COLUMN Unidad int NOT NULL DEFAULT 0`
- `CREATE TABLE PreciosPorUnidad` (Id, Valor decimal(18,2), + columnas estandar de `SoftDestroyable`: CreatedAt, UpdatedAt, DeletedAt, CreatedByUserId, DeletedByUserId)
- Seed: `InsertData` de la fila inicial `Valor = 892.03`
- **Data migration obligatoria (riesgo RA-06, ver abajo):** backfill de `Unidad` para Practicas existentes via `migrationBuilder.Sql(...)`: `UPDATE Practicas SET Unidad = GREATEST(1, ROUND(PrecioActual / 892.03)) WHERE DeletedAt IS NULL` — evita que los Perfiles existentes queden con precio $0 apenas se despliegue el cambio (sin este backfill, `Unidad` NOT NULL DEFAULT 0 dejaria el precio calculado en $0 para todo perfil preexistente hasta que el usuario lo edite a mano).
Riesgo de rollback: BAJO (columna nueva + tabla nueva, sin tocar datos existentes salvo el backfill explicito y reversible).

### 6. Riesgos y supuestos
- **RA-06 (critico, nuevo):** sin el backfill de `Unidad` en la migracion, todos los Perfiles existentes mostrarian precio $0 hasta ser editados manualmente — mitigado con `UPDATE` en la propia migracion (ver seccion 5). El valor de Unidad resultante es una aproximacion; el usuario debera revisar y ajustar los Perfiles existentes despues del deploy.
- **RA-07:** al remover el cascade de F-001, cualquier Perfil cuyo precio dependia historicamente de aumentos previos via cascade queda "congelado" en su ultimo valor hasta que se ejecute el primer recalculo (creacion/edicion del Perfil o cambio de PrecioPorUnidad). Es el comportamiento esperado segun P10, se documenta para que no se interprete como bug.
- **RA-08:** el recalculo batch de `PrecioActual` para todas las Practicas activas al cambiar `PrecioPorUnidad` es una operacion O(n) sobre la tabla `Practicas` — a volumen esperado (bajo, mono-laboratorio) sin impacto de performance; no requiere batching adicional.
- **RA-09:** `PreciosController` sigue con `AppDbContext` inyectado directamente (deuda tecnica preexistente, no introducida por este cambio) — se simplifica pero no se refactoriza a Service en este alcance.
- Riesgos heredados de la arquitectura original (RA-01 a RA-05, sesion 2026-06-13) — RA-01 (baja logica UB con composicion activa) deja de tener impacto en precio pero se mantiene el badge informativo si aplica.

### 7. Gate de aprobacion
ARQUITECTURA CERRADA. Confirmado por el cliente: (a) RN-02 se relaja globalmente (sin distincion alta rapida vs ABM completo) y (b) el backfill de `Unidad` en la migracion usa aproximacion automatica (`Unidad = ROUND(PrecioActual / 892.03)`, minimo 1) para todos los Perfiles existentes. Sin bloqueos. Listo para presupuesto.

## Historial de ajustes
- 2026-06-13: Arquitectura completa producida. 6 entidades nuevas, 3 interfaces de servicio nuevas, 6 archivos de DTOs nuevos, 16 archivos Web nuevos, 4 archivos existentes modificados, 1 migracion EF. Gate de aprobacion para presupuesto: ABIERTO.
- 2026-07-08: Arquitectura de 3 mejoras (Unidad/PrecioPorUnidad reemplazando precio manual y simplificando F-001, pantalla de carga masiva + alta rapida atomica, fix de ancho de columna PDF). 1 entidad nueva (`PrecioPorUnidad`), 1 entidad modificada (`Practica` +Unidad), `IPracticaService` extendido sin nueva interfaz (evita dependencia circular), `IProduccionMensualService` +`AgregarLineasAsync` atomico, `PreciosController` simplificado (se elimina cascade UB→Perfil). 1 migracion EF con backfill de datos (RA-06, riesgo critico identificado y mitigado). Gate de aprobacion: ABIERTO, pendiente confirmar RN-02 global y criterio de backfill en Presupuesto.

## Definiciones vigentes

### Impacto por capa

#### Domain (BlankProject.Domain)
Archivos nuevos (6):
- Entities/UnidadBioquimica.cs — hereda SoftDestroyable, Nombre MaxLength 150, PrecioActual decimal 18,2
- Entities/Practica.cs — hereda SoftDestroyable, Nombre MaxLength 150, PrecioActual decimal 18,2
- Entities/PracticaDetalle.cs — hereda SoftDestroyable, FK PracticaId + FK UnidadBioquimicaId
- Entities/ProduccionMensual.cs — hereda SoftDestroyable, Mes int, Anio int, Notas string? MaxLength 500
- Entities/ProduccionDetalle.cs — hereda SoftDestroyable, FK ProduccionMensualId, TipoItem enum, PracticaId? nullable FK, UnidadBioquimicaId? nullable FK, NombreSnapshot MaxLength 200, PrecioSnapshot decimal 18,2, Cantidad int
- Enums/TipoItemProduccion.cs — Practica = 1, UnidadBioquimica = 2
Archivos modificados: Ninguno.

#### Application (BlankProject.Application)
Archivos nuevos (6):
- Interfaces/IUnidadBioquimicaService.cs
- Interfaces/IPracticaService.cs
- Interfaces/IProduccionMensualService.cs
- DTOs/UnidadBioquimicaDtos.cs
- DTOs/PracticaDtos.cs
- DTOs/ProduccionMensualDtos.cs
Archivos modificados (1):
- Interfaces/IRepository.cs — agregar Task RestoreAsync(T entity) para reactivar soft-deleted

#### Infrastructure (BlankProject.Infrastructure)
Archivos nuevos (3):
- Services/UnidadBioquimicaService.cs — implementa IUnidadBioquimicaService
- Services/PracticaService.cs — implementa IPracticaService, usa IgnoreQueryFilters() para sumatoria de componentes (RA-01)
- Services/ProduccionMensualService.cs — implementa IProduccionMensualService
Archivos modificados (3):
- Data/AppDbContext.cs — agregar 5 DbSets + Fluent API config (sin tocar configuraciones existentes)
- Repositories/Repository.cs — implementar RestoreAsync (entity.DeletedAt = null, entity.DeletedByUserId = null)
- DependencyInjection.cs — registrar 3 nuevos servicios como Scoped
Nueva migracion: AddLabipacEntities

#### Web (BlankProject.Web)
Archivos nuevos (16):
- Controllers/UnidadesBioquimicasController.cs — acciones: Index, Create, Edit, Delete, Restore
- Controllers/PracticasController.cs — acciones: Index, Details, Create, Edit, Delete, Restore
- Controllers/ProduccionMensualController.cs — acciones: Index, Create, Detalle, Delete, AgregarLinea, EditarLinea, EliminarLinea, GetPrecioItem (AJAX)
- Models/UnidadBioquimicaViewModels.cs — VM-01, VM-02
- Models/PracticaViewModels.cs — VM-03, VM-04, VM-05
- Models/ProduccionMensualViewModels.cs — VM-06 a VM-11
- 10 Views (.cshtml)
Archivos modificados (1):
- Views/Shared/_Layout.cshtml — 3 entradas sidebar: Unidades Bioquimicas, Practicas, Produccion Mensual

### Riesgos arquitectonicos
- RA-01: Baja logica UnidadBioquimica con composicion activa — resuelto: PracticaService usa IgnoreQueryFilters para sumatoria + badge de aviso en Edit si componente inactivo. Residual: BAJO.
- RA-02: ProduccionDetalle con 2 FK nullable — resuelto: Service valida exactamente uno non-null. Residual: MUY BAJO.
- RA-03: Sin unique DB index para Mes+Anio en ProduccionMensual (MySQL no soporta partial index) — resuelto: unicidad enforced en Service. Residual: MINIMO (monousuario).
- RA-04: AJAX GetPrecioItem con item inactivo o inexistente — resuelto: Service retorna decimal? null, Controller retorna { success: false }, JS bloquea modal. Residual: BAJO.
- RA-05: Decimal binding precio en es-AR — NULO: InvariantDecimalModelBinder existente cubre.

### Necesidad de migracion EF
SI — 1 migracion: AddLabipacEntities.
Tablas creadas: UnidadesBioquimicas, Practicas, PracticaDetalles, ProduccionMensuales, ProduccionDetalles.
Tablas modificadas: Ninguna.
Riesgo rollback: NULO.
Comando: dotnet ef migrations add AddLabipacEntities --project BlankProject.Infrastructure --startup-project BlankProject.Web

### Permisos
Sin nuevos roles ni policies. Todos los controllers nuevos usan [Authorize] sin politica.
Roles existentes (SuperUsuario, Administrador) no impactados.

### Supuestos y dependencias
- SA-01: Cultura es-AR ya configurada, InvariantDecimalModelBinder ya registrado.
- SA-02: Global query filter SoftDestroyable se aplica automaticamente a todas las nuevas entidades.
- SA-03: AuditLog automatico en SaveChangesAsync cubre todas las operaciones nuevas sin configuracion adicional.
- SA-04: DataTables client-side suficiente para volumenes esperados.
- SA-05: Sin paquetes NuGet nuevos requeridos.

## Historial de ajustes
- 2026-06-13: Arquitectura completa producida. 6 entidades nuevas, 3 interfaces de servicio nuevas, 6 archivos de DTOs nuevos, 16 archivos Web nuevos, 4 archivos existentes modificados, 1 migracion EF. Gate de aprobacion para presupuesto: ABIERTO.
