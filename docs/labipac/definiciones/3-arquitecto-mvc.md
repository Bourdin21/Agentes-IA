# Memoria - Arquitecto MVC

## Proyecto: labipac
## Ultima actualizacion: 2026-06-13 — ARQUITECTURA COMPLETA Y CERRADA

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
