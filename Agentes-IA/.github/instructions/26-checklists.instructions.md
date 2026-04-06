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
