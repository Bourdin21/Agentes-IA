---
description: Checklists para nuevas entidades y nuevos servicios en la arquitectura BlankProject.
applyTo: "**/*.{cs,csproj,cshtml}"
---

# Checklist nuevas entidades
1. Crear entidad en Domain/Entities heredando SoftDestroyable.
2. Agregar DbSet<T> en AppDbContext.
3. Configurar Fluent API (lengths, indexes, relations).
4. Crear interfaz Application si requiere servicio dedicado.
5. Crear DTOs Application si requiere proyecciones.
6. Implementar servicio en Infrastructure/Services.
7. Registrar servicio en DependencyInjection.cs (Scoped).
8. Crear ViewModels en Web/Models con DataAnnotations en espanol.
9. Crear Controller en Web/Controllers.
10. Crear Views segun design system.
11. Agregar link en sidebar de Shared/_Layout.cshtml.
12. Generar migracion EF.

# Checklist nuevos servicios
1. Definir interfaz en Application/Interfaces.
2. Implementar en Infrastructure/Services.
3. Registrar como Scoped en DependencyInjection.cs.
4. Inyectar por constructor donde corresponda.

# Checklist modulo con workflow / maquina de estados
1. Definir enum de estados en Domain/Enums.
2. Mapear transiciones validas en el Service (no en Controller).
3. Validar guardas y permisos por transicion antes de persistir.
4. Registrar evento/auditoria del cambio de estado.
5. Cubrir transiciones invalidas con error funcional explicito.
6. ViewModel con estado actual + acciones disponibles segun rol.
7. QA debe recorrer todas las transiciones validas e invalidas.

# Checklist reporte o exportacion
1. DTO/proyeccion en Application sin exponer entidades.
2. Service en Infrastructure con consulta optimizada (no N+1).
3. Filtros y paginacion en ViewModel.
4. Export Excel via ClosedXML o PDF via QuestPDF segun corresponda.
5. Permiso explicito para acceder al reporte.
6. Pruebas funcionales con datos representativos.

# Checklist integracion externa
1. Interfaz en Application con contrato del proveedor.
2. Implementacion en Infrastructure con HttpClient tipado o SDK.
3. Configuracion en appsettings con seccion dedicada.
4. Manejo de timeouts, reintentos y errores controlados.
5. Logging estructurado con Serilog (sin secretos).
6. Pruebas funcionales con caso ok, caso error y caso timeout.

# Checklist modificacion sobre modulo existente
1. Identificar modulo y archivo(s) a tocar antes de codificar.
2. Confirmar que la regla nueva no contradice la maquina de estados vigente.
3. Mantener compatibilidad con datos existentes (migracion EF si aplica).
4. Actualizar ViewModel y validaciones de la pantalla afectada.
5. Probar regresion del flujo previo ademas del cambio nuevo.
