---
description: Reglas de Domain (entidades, enums, soft delete, auditoria y convenciones).
applyTo: "**/Domain/**/*.cs"
---

# Domain
- Entidades de negocio heredan de SoftDestroyable.
- Soft delete por DeletedAt != null.
- Nunca hard delete para entidades SoftDestroyable.

# Entidades especiales
- ApplicationUser hereda de IdentityUser y no de SoftDestroyable.
- AuditLog es entidad independiente y se genera automaticamente en SaveChangesAsync.
- Notification es entidad independiente para notificaciones in-app.

# Enums
- EstadoUsuario: Activo = 1, Bloqueado = 2.
- Persistencia de enums en int via HasConversion<int>().

# Convenciones C#
- Nullable habilitado.
- File-scoped namespace.
- Codigo en ingles, UI y mensajes en espanol argentino.
