---
name: roles-activos
description: "Qué roles de Identity están realmente en uso hoy en OlvidataCRM, vs. los que existen en código pero no se usan aún"
metadata: 
  node_type: memory
  type: project
  originSessionId: 6dad76aa-39ef-4734-885b-25074d2a71fb
  modified: 2026-07-21T13:47:47.789Z
---

Por el momento el único rol activo/en uso en la aplicación es **SuperUsuario**. Aunque `Program.cs` define policies para `Administrador`, `Vendedor` y `Empleado` (`RequireAdministracion`, `RequireVendedor`, `RequireEmpleado`, `SoloAdministrador`) y varios controllers ya están decorados con `[Authorize(Policy = "RequireAdministracion")]` (ej. `BotController`), en la práctica no hay usuarios con esos otros roles todavía — todo lo opera Joaquín como SuperUsuario.

**Why:** el usuario lo aclaró explícitamente (2026-07-21) al pedir trabajar en nuevas funcionalidades, para que no se asuma que hay un equipo multi-rol usando el sistema activamente.

**How to apply:** al diseñar nuevas pantallas o features, no es necesario construir UI condicional por rol distinto de SuperUsuario todavía (ej. ocultar/mostrar según Vendedor/Empleado) salvo que el usuario lo pida explícitamente. Las policies ya definidas en código pueden reusarse tal cual para no romper el patrón, pero no hay urgencia en diferenciar permisos finos entre roles no-SuperUsuario porque no hay usuarios reales en esos roles todavía.
