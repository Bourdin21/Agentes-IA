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

# Matematica de porcentajes (aplicar/revertir recargo o descuento)
- Nunca revertir un recargo o descuento restando el mismo %. `valorConRecargo * (1 - pct/100)`
  NO es la inversa de `valorBase * (1 + pct/100)` y da un numero distinto al original (ej.
  100 con 21% de recargo da 121; "restarle 21%" a 121 da 95,59, no 100).
- La inversa correcta es dividir: si `conRecargo = base * (1 + pct/100)`, entonces
  `base = conRecargo / (1 + pct/100)`. Mismo criterio para descuento (dividir por
  `1 - pct/100` para revertir).
- Cualquier proyecto que necesite sumar/revertir un % de precio implementa un helper
  invertible (`AplicarRecargo`/`QuitarRecargo`/`AplicarDescuento`/`QuitarDescuento`) en vez
  de la cuenta a mano en cada lugar que la usa — ver `MariHogar.Domain.Helpers.PorcentajeHelper`
  (docs/marihogar/definiciones/1-analista-funcional.md, CR-40) como referencia de
  implementacion.
