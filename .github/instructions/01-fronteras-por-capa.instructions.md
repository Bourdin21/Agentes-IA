---
description: Fronteras arquitectonicas por capa para cambios ASP.NET Core MVC + EF Core.
applyTo: "**/*.{cs,cshtml,json}"
---

# Fronteras por capa
- Presentacion: Controllers, Views, ViewModels, validaciones de pantalla.
- Negocio: Services, reglas de negocio, estados, permisos, procesos.
- Datos: DbContext, entidades, configuraciones EF, migraciones, acceso MySQL.

# Regla de ubicacion de logica
- Logica UI y coordinacion en Presentacion.
- Logica de negocio en Negocio.
- Persistencia y acceso a datos en Datos.
- No mezclar responsabilidades entre capas.
