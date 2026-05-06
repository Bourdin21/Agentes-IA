# 8 - Convenciones (reglas para agentes IA)

Reglas obligatorias al editar este codebase. Si una regla entra en conflicto con un cambio, **detener y consultar** antes de codificar.

## Idioma

- Identificadores de dominio en **espaniol sin tildes** (`Movimiento`, `Categoria`, `EsPagoTarjeta`, `CuotasReutilizadas`).
- Comentarios y mensajes de UI en **espaniol** (con o sin tildes segun archivo, mantener consistencia local).
- Documentacion en `docs/` en espaniol sin tildes para evitar problemas de encoding entre editores.
- Mensajes de commit en espaniol o ingles, breve y descriptivo.

## Estilo C#

- C# moderno (`net10.0`): file-scoped namespaces, `var` cuando el tipo es obvio, `nullable enable` activo.
- DI por constructor; **no** Service Locator.
- Async todo el camino IO (`async/await`, `CancellationToken` cuando ya este en la firma upstream; no agregar tokens de forma masiva sin necesidad).
- Acceso a `DbContext` directamente desde el controller esta aceptado (no introducir nuevo Repository por estetica).
- LINQ legible: separar `.Where().Select()` en lineas si es complejo.
- Logging con Serilog (`ILogger<T>`), no `Console.WriteLine`.

## Capas

- **Prohibido**: agregar referencias EF Core o ASP.NET en `Domain` o `Application`.
- Nuevos servicios externos -> interfaz en `Application/Interfaces`, implementacion en `Infrastructure/Services`, registro en `Infrastructure/DependencyInjection.cs`.
- Nuevos endpoints -> controller en `Web/Controllers`, vista en `Web/Views/<Controller>/`, viewmodel en `Web/Models`.

## Persistencia y datos

- **Soft delete obligatorio** para entidades de negocio. Nunca borrar fisicamente sin pedido explicito.
- **Multi-tenant**: toda query nueva DEBE filtrar `UsuarioId == User.GetUserId()` salvo endpoints administrativos explicitos.
- Cualquier cambio de schema requiere migracion EF + script SQL idempotente.
- Excluir `EsPagoTarjeta` de KPIs de gasto y de subcategoria; incluirlo solo en deuda de tarjeta.
- Comparaciones de periodo en dashboard: por **mes calendario**, no por dias.

## UI / Web

- Todo POST -> `[ValidateAntiForgeryToken]`.
- AJAX -> incluir el header `RequestVerificationToken` (ya gestionado por `site.js`).
- Datalists grandes -> DataTables server-side.
- Confirmaciones destructivas -> SweetAlert (no `confirm()` nativo).
- Iconos -> Bootstrap Icons.
- Formato de monedas -> `Helpers.FormatoMoneda.Formatear`.

## Identity y seguridad

- Nuevas politicas -> agregar a `Program.cs` + `[Authorize(Policy = ...)]`.
- Bloquear usuario debe invalidar la security stamp.
- Lockout (5 intentos / 15 min) ya configurado, no cambiar sin acuerdo.
- Cookies: `HttpOnly`, `SecurePolicy.Always`, `SameSite.Lax`, `ExpireTimeSpan = 8h`. No bajar.
- Health checks no son anonimos.

## Testing manual

- No hay proyecto de tests automatizados aun. Cada cambio entrega **escenarios de prueba manual** documentados en `5-implementador.md` y `6-qa.md`.
- Antes de cerrar tarea: `run_build` exitoso, escenarios manuales listados, riesgos en doc del implementador.

## Documentacion

- Cada etapa nueva agrega seccion en `5-implementador.md` (no reemplaza historia).
- Defectos descubiertos van a `6-qa.md` con codigo (D-XX o B-XX), severidad, fix y estado.
- Cambios estructurales (capas, dominio, deploy) actualizan los docs `1-`, `2-`, `3-`, `4-` o `7-`.
- No duplicar contenido entre docs; preferir referenciar.

## Lo que NO hay que hacer

- No introducir Razor Pages (la app es MVC).
- No bypassear el filtro de soft delete (`IgnoreQueryFilters` solo justificado en admin/audit).
- No agregar dependencias NuGet sin necesidad. Si se agrega, motivar en `5-implementador.md`.
- No commitear secretos, claves SMTP, conexiones reales, ni archivos de log.
- No correr `database update` directo en produccion: siempre script SQL idempotente revisado.
- No editar archivos en `wwwroot/lib/` (libs vendoreadas); upgradear con la cadena oficial (LibMan / npm) si fuese necesario.
