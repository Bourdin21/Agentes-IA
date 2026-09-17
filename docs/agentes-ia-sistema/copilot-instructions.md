# Instrucciones para Copilot — <NombreProyecto> (Olvidata Soft)

> Plantilla base. Al inicializar un proyecto nuevo, copiar este archivo como `.github/copilot-instructions.md` dentro del repositorio del sistema y ajustar los bloques marcados con `<...>` o las secciones marcadas como `[Personalizar]` segun la arquitectura, comandos y design system del proyecto.
>
> Las reglas globales de orquestacion (etapas, agentes, fronteras por capa, presupuesto, QA) viven en el repo `Agentes-IA` (`.github/instructions/*`). Este archivo describe **el stack y convenciones del proyecto puntual** para que el agente IA del repositorio del sistema siga las mismas reglas que las definiciones documentadas en `/docs/<proyecto>/definiciones/`.

Documentacion completa del proyecto: ver [`README.md`](../README.md).

---

## Stack y Arquitectura

[Personalizar segun el proyecto. Baseline BlankProject:]

- **ASP.NET Core MVC** en **.NET 10** (no Razor Pages, no Blazor — usar Controllers + Views `.cshtml`).
- **Entity Framework Core 10** con **MySQL** (`MySql.EntityFrameworkCore`), enfoque **Code First** con Migrations.
- **ASP.NET Core Identity** con cookies para autenticacion.
- **Serilog** para logging estructurado.
- Arquitectura en 4 capas:
  - `<Proyecto>.Domain` — Entidades + Enums (sin dependencias externas salvo Identity).
  - `<Proyecto>.Application` — Interfaces (`IRepository<T>`, `IEmailService`, `INotificationService`, `IExportService`, `IErrorNotifier`) + DTOs (`ServiceResult`, `DataTableRequest/Response`).
  - `<Proyecto>.Infrastructure` — Implementaciones concretas, `AppDbContext`, repositorios, servicios.
  - `<Proyecto>.Web` — Controllers, ViewModels, Views, Middleware.

## Convenciones de Nomenclatura

- **Entidades**: PascalCase (`MiEntidad`).
- **Controllers**: `{Entidad}Controller` en plural ingles (`UsersController`).
- **ViewModels**: `{Entidad}{Accion}ViewModel` (`UserCreateViewModel`, `UserListViewModel`).
- **Interfaces**: prefijo `I` en `Application/Interfaces/`.
- **DTOs**: sufijo `Dto` en `Application/DTOs/`.
- **Enums**: PascalCase en espanol (`EstadoUsuario.Activo`).
- **Vistas**: `Views/{Controller}/{Accion}.cshtml`.
- **CSS del Design System**: prefijo `ov-` (`ov-card`, `btn-ov-primary`).

## Reglas al Crear Entidades

- **Toda entidad de negocio nueva DEBE heredar de `SoftDestroyable`**. Ya incluye:
  - `Id` (`int` autoincremental).
  - Auditoria: `CreatedAt`, `CreatedByUserId`, `UpdatedAt`, `UpdatedByUserId` (se setean automaticamente en `SaveChangesAsync`).
  - Soft delete: `DeletedAt`, `DeletedByUserId`.
- **No filtrar manualmente por `DeletedAt`**: el query filter global en `AppDbContext` ya excluye registros eliminados.
- Registrar el `DbSet<T>` en `AppDbContext` y agregar configuracion Fluent API en `OnModelCreating` si hay restricciones (`HasMaxLength`, `IsRequired`, indices).
- Generar migracion con:
  ```powershell
  dotnet ef migrations add NombreMigracion --project <Proyecto>.Infrastructure --startup-project <Proyecto>.Web
  ```

## Reglas al Crear Controllers

- **Inyeccion de dependencias por constructor.** Inyectar `IRepository<T>` generico para CRUD; usar `AppDbContext` directo solo para queries complejos con joins.
- **Autorizacion por defecto**:
  ```csharp
  [Authorize]                                    // Cualquier usuario autenticado
  [Authorize(Policy = "RequireAdministracion")]  // SuperUsuario o Administrador
  [Authorize(Policy = "RequireSuperUsuario")]    // Solo SuperUsuario
  ```
- **Anti-forgery obligatorio** en todo POST: `[ValidateAntiForgeryToken]`.
- **CRUD estandar**: `Index`, `Details`, `Create` (GET/POST), `Edit` (GET/POST), `Delete` (POST).
- **Patron POST tipico**:
  ```csharp
  if (!ModelState.IsValid) return View(model);
  // ... logica ...
  TempData["SuccessMessage"] = "Registro creado correctamente.";
  return RedirectToAction(nameof(Index));
  ```
- **Soft delete**: usar `_repo.DeleteAsync(entity)` — nunca `_dbSet.Remove()` ni borrado fisico.
- **Logging con structured logging** (placeholders, no interpolacion):
  ```csharp
  _logger.LogInformation("Usuario creado: {Email} por {Admin}", email, User.Identity?.Name);
  ```
- **Respuestas JSON para AJAX**:
  ```csharp
  return Json(new { success = true, message = "OK", data = resultado });
  ```
- **DataTables server-side**: parsear `Request.Form` a `DataTableRequest` y devolver `DataTableResponse<T>`.

## Reglas al Crear ViewModels

- En `<Proyecto>.Web/Models/`.
- **Data Annotations en espanol** con `[Display(Name="...")]`:
  ```csharp
  [Required(ErrorMessage = "El nombre es obligatorio.")]
  [StringLength(200, ErrorMessage = "Maximo 200 caracteres.")]
  [Display(Name = "Nombre completo")]
  public string FullName { get; set; } = string.Empty;
  ```
- Propiedades string no nullables: inicializar con `= string.Empty;`.
- Para listados con filtros, incluir: `SearchTerm`, filtros, `Page`, `PageSize`, `TotalCount`, `TotalPages`.

## Reglas al Crear Vistas

- **Encabezado**: `@{ ViewData["Title"] = "..."; }` siempre.
- **Cabecera con boton "Nuevo"** en `Index`:
  ```html
  <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">Titulo</h3>
      <a asp-action="Create" class="btn btn-primary">
          <i class="fas fa-plus me-1"></i> Nuevo registro
      </a>
  </div>
  ```
- **Formularios**: dentro de `<div class="card"><div class="card-body">`, columna `col-md-6`.
- **Tag Helpers** ASP.NET Core (`asp-for`, `asp-action`, `asp-validation-for`, `asp-route-id`).
- **Estructura de campo**:
  ```html
  <div class="mb-3">
      <label asp-for="Campo" class="form-label"></label>
      <input asp-for="Campo" class="form-control" />
      <span asp-validation-for="Campo" class="text-danger"></span>
  </div>
  ```
- **Botones del formulario** — siempre Guardar (primary) + Cancelar (outline-secondary):
  ```html
  <div class="d-flex gap-2">
      <button type="submit" class="btn btn-primary">
          <i class="fas fa-save me-1"></i> Guardar
      </button>
      <a asp-action="Index" class="btn btn-outline-secondary">Cancelar</a>
  </div>
  ```
- **Validacion client-side**: incluir al final
  ```html
  @section Scripts {
      <partial name="_ValidationScriptsPartial" />
  }
  ```
- **Tablas**: `class="table table-hover mb-0"` dentro de `<div class="card"><div class="table-responsive">`. Header con `class="table-light"`. Columna de acciones con `btn-group btn-group-sm`.
- **Botones de accion en tabla**: `btn-outline-info` (ver), `btn-outline-primary` (editar), `btn-outline-danger` (eliminar).
- **Confirmacion de acciones destructivas**: clase `btn-swal-confirm` + `data-message="..."` (el handler global ya esta en `site.js`).
- **Iconos**: Font Awesome 6 (`fas fa-*`, `fab fa-*`), siempre con `me-1` antes del texto.
- **Badges de estado**: `bg-success` (Activo), `bg-secondary` (Neutral), `bg-warning` (Pendiente), `bg-danger` (Error/Bloqueado), `bg-primary` (Info principal).

## Mensajes al Usuario

- **Exito tras redirect**: `TempData["SuccessMessage"] = "..."` -> SweetAlert2 verde automatico.
- **Error tras redirect**: `TempData["ErrorMessage"] = "..."` -> SweetAlert2 rojo automatico.
- **Errores de validacion**: `ModelState.AddModelError("Campo", "Mensaje");` -> se muestran junto al campo.
- **No usar `alert()` de JavaScript** — siempre SweetAlert2.

## Servicios Disponibles (inyectar por interfaz)

| Interfaz | Uso |
|----------|-----|
| `IRepository<T>` | CRUD generico con soft delete |
| `IEmailService` | `SendEmailAsync(to, subject, htmlBody)` — via MailKit/SMTP |
| `INotificationService` | Notificaciones in-app (`CreateAsync`, `GetRecentAsync`, `MarkAsReadAsync`) |
| `IExportService` | `ExportToExcel<T>()` (ClosedXML), `ExportToPdf<T>()` (QuestPDF) |
| `IErrorNotifier` | `NotifyError(ex, usuario, request)` — fire-and-forget para errores |
| `UserManager<ApplicationUser>` | Gestion de usuarios Identity |
| `SignInManager<ApplicationUser>` | Login/logout |

## Roles y Politicas

- Roles: `SeedData.RolSuperUsuario` (`"SuperUsuario"`), `SeedData.RolAdministrador` (`"Administrador"`).
- Policies: `"RequireSuperUsuario"`, `"RequireAdministracion"`.
- En vistas: `@if (User.IsInRole("SuperUsuario")) { ... }`.
- Para agregar entrada al sidebar, editar `Views/Shared/_Layout.cshtml` siguiendo el patron existente con `ov-sidebar-link` y la condicion `active`.

## Paleta de Colores

[Personalizar por proyecto si el design system difiere del baseline Olvidata.]

- Primario: `#2b9de4` (variable CSS `--ov-primary`). Usar `btn-primary` o `btn-ov-primary`.
- Exito: `#22c55e` | Warning: `#f59e0b` | Danger: `#ef4444` | Info: `#06b6d4`.
- Tipografia: **Inter** (Google Fonts), ya cargada en `_Layout.cshtml`.

## Cultura

- App configurada en `es-AR`. Fechas: `dd/MM/yyyy`, decimal `,`, miles `.`.
- Para formato de moneda usar `<Proyecto>.Web.Helpers.FormatoMoneda`:
  - `FormatoMoneda.FormatMonto(valor)` -> `"1.234.567,89"`
  - `FormatoMoneda.FormatMoneda(valor, "$")` -> `"$ 1.234.567,89"`

## Manejo de Errores

- No envolver controladores enteros en try/catch — el `GlobalExceptionHandler` ya maneja excepciones no controladas (log + email en produccion + JSON/redirect segun tipo de request).
- Usar try/catch solo cuando hay una **accion de recuperacion especifica** (ej: enviar email, exportar archivo) y loguear con `_logger.LogError(ex, "...")`.

## Comandos de desarrollo

[Personalizar segun el proyecto. Baseline BlankProject:]

```powershell
# Restaurar y compilar
dotnet restore
dotnet build

# Ejecutar
dotnet run --project <Proyecto>.Web

# Migraciones EF Core
dotnet ef migrations add NombreMigracion --project <Proyecto>.Infrastructure --startup-project <Proyecto>.Web
dotnet ef database update --project <Proyecto>.Infrastructure --startup-project <Proyecto>.Web

# Pruebas (si aplica)
dotnet test
```

## NO Hacer

- No usar Razor Pages (el contexto del workspace lo sugiere, pero este proyecto es MVC clasico).
- No usar Blazor.
- No borrar entidades fisicamente (`_dbSet.Remove`) — siempre soft delete via `IRepository<T>.DeleteAsync()`.
- No filtrar manualmente `Where(e => e.DeletedAt == null)` — el query filter global ya lo aplica.
- No setear manualmente `CreatedAt`/`UpdatedAt`/`CreatedByUserId` — el `AppDbContext` lo hace automaticamente.
- No usar `Console.WriteLine` — usar `ILogger<T>` con Serilog.
- No interpolar strings en logs — usar placeholders estructurados.
- No instanciar `HttpClient` ad-hoc — usar `IHttpClientFactory` si se necesita.
- No agregar paquetes NuGet sin justificacion — preferir lo ya disponible (MailKit, ClosedXML, QuestPDF, Serilog).
- No commitear secretos (passwords SMTP, connection strings de produccion) — usar User Secrets o variables de entorno.
