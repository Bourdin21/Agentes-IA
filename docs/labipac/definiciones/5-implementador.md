# Memoria - Implementador

## Proyecto: labipac
## Ultima actualizacion: 2026-06-14 (sesion 1 — implementacion completa Etapa 1)

## Definiciones vigentes

### Cambios implementados
- M4 Infra transversal: RestoreAsync en IRepository + Repository implementado.
- M1 Unidades Bioquimicas: entidad, servicio, controller, 3 vistas (Index/Create/Edit), sidebar.
- M2 Practicas: entidad + PracticaDetalle, IPracticaService + PracticaService (IgnoreQueryFilters RN-01), controller, 4 vistas (Index/Create/Edit/Details), sidebar.
- M3 Produccion Mensual: entidad + ProduccionDetalle + TipoItemProduccion, IProduccionMensualService + ProduccionMensualService, controller con AJAX endpoint GetPrecioItem, 3 vistas (Index/Create/Detalle con 2 modales Bootstrap), sidebar.
- Migracion EF: AddLabipacEntities aplicada a DB (5 tablas nuevas).
- Build: OK sin errores.

### Archivos tocados
**Domain (nuevos):**
- Entities/UnidadBioquimica.cs
- Entities/Practica.cs
- Entities/PracticaDetalle.cs
- Entities/ProduccionMensual.cs
- Entities/ProduccionDetalle.cs
- Enums/TipoItemProduccion.cs

**Application (nuevos):**
- Interfaces/IUnidadBioquimicaService.cs
- Interfaces/IPracticaService.cs
- Interfaces/IProduccionMensualService.cs
- DTOs/UnidadBioquimicaDtos.cs
- DTOs/PracticaDtos.cs
- DTOs/ProduccionMensualDtos.cs

**Application (modificados):**
- Interfaces/IRepository.cs — RestoreAsync agregado

**Infrastructure (nuevos):**
- Services/UnidadBioquimicaService.cs
- Services/PracticaService.cs
- Services/ProduccionMensualService.cs
- Data/Migrations/[timestamp]_AddLabipacEntities.cs (generado)

**Infrastructure (modificados):**
- Repositories/Repository.cs — RestoreAsync implementado
- Data/AppDbContext.cs — 5 DbSets + Fluent API config
- DependencyInjection.cs — 3 servicios registrados como Scoped

**Web (nuevos):**
- Models/UnidadBioquimicaViewModels.cs (VM-01, VM-02)
- Models/PracticaViewModels.cs (VM-03 a VM-05)
- Models/ProduccionMensualViewModels.cs (VM-06 a VM-11 + SelectItemSimple)
- Controllers/UnidadesBioquimicasController.cs
- Controllers/PracticasController.cs
- Controllers/ProduccionMensualController.cs
- Views/UnidadesBioquimicas/Index.cshtml
- Views/UnidadesBioquimicas/Create.cshtml
- Views/UnidadesBioquimicas/Edit.cshtml
- Views/Practicas/Index.cshtml
- Views/Practicas/Create.cshtml
- Views/Practicas/Edit.cshtml
- Views/Practicas/Details.cshtml
- Views/ProduccionMensual/Index.cshtml
- Views/ProduccionMensual/Create.cshtml
- Views/ProduccionMensual/Detalle.cshtml

**Web (modificados):**
- Views/Shared/_Layout.cshtml — 2 secciones sidebar (Configuracion + Produccion) con 3 links

### Riesgos y dependencias
- RA-01 RESIDUAL: PracticaService.CalcularSumatoriaAsync usa IgnoreQueryFilters — ok, encapsulado.
- RA-03 RESIDUAL: Unicidad Mes+Anio enforced en Service (no DB index). OK para monousuario.
- Warnings NU1902 MailKit/MimeKit — vulnerabilidades conocidas, pendiente de parche por separado (no bloquean funcionalidad).
- SA-01/SA-02/SA-03/SA-05 confirmados OK en build.

## Historial de ajustes
- 2026-06-14: Implementacion completa Etapa 1 (todo el alcance). 6 entidades + enum, 9 interfaces/servicios, 3 controllers, 10 vistas, 1 migracion EF. Build OK. DB actualizada.
