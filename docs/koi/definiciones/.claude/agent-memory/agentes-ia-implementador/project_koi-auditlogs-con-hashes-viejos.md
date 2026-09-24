---
name: koi-auditlogs-con-hashes-viejos
description: KOI — las filas viejas de AuditLogs en producción tienen hashes de contraseña escritos en el JSON; el código ya no los escribe, pero limpiar el historial quedó como decisión pendiente del dueño
metadata:
  type: project
---

En KOI, hasta el commit `ef47250` (2026-09-23) la auditoría automática de `AppDbContext` escribía el **`PasswordHash` viejo y el nuevo** en el JSON de `AuditLogs` en cada cambio de contraseña. Esa tabla se lee desde la pantalla de Auditoría. Desde ese commit, `PropiedadesNoAuditables` excluye `PasswordHash`, `SecurityStamp` y `ConcurrencyStamp`, así que **no se escriben más** — pero **las filas ya existentes en producción los siguen teniendo**.

**Why:** el ítem 1 del sprint "Fixes y mejoras" pedía que toda acción de contraseña quedara auditada *sin guardar la contraseña*; al implementarlo apareció que el rastro automático ya venía guardando el hash desde antes, por un camino que nadie había mirado (`Edit` de usuarios llamaba a `ResetPasswordAsync` y EF auditaba la columna como cualquier otra). Limpiar el historial es un `UPDATE` sobre datos de producción, así que **no se hizo**: es decisión del dueño.

**How to apply:** si alguien pide tocar `AuditLogs`, exportarla, o abrir la pantalla de Auditoría a un rol nuevo, **avisar primero de esto** — las filas viejas siguen teniendo material sensible. Si el dueño decide limpiarlas, va con backup previo y como trabajo aparte, no colgado de otra tanda. Y si se agrega una entidad con un campo secreto (token, API key), sumar su nombre a `PropiedadesNoAuditables` en `AppDbContext`: el rastro automático audita **todas** las columnas de **toda** entidad trackeada.

Ver también [[koi-e25-pendiente]].
