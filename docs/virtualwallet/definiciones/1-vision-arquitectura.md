# 1 - Vision y arquitectura

## Producto

**VirtualWallet** es una aplicacion web de finanzas personales multiusuario que permite:

- Registrar **movimientos** (ingresos y egresos) clasificados por **categoria** y **subcategoria**, asociados a una **cuenta** (efectivo, banco, tarjeta) y opcionalmente a una **cuota** (financiacion).
- Importar resumenes de **tarjetas Visa y Mastercard del Banco Provincia** (PDF) generando movimientos y cuotas automaticamente con categorizacion sugerida.
- Visualizar un **dashboard financiero** con KPIs, comparativas, tendencias, deuda de tarjeta, cuotas activas, top de gastos y alertas.
- Dolarizar montos al cambio del dia (`CotizacionService`).
- Administrar usuarios, roles, auditoria y notificaciones internas.

## Stack

- **.NET 10** (todas las capas).
- **ASP.NET Core MVC** (controllers + Razor Views; **NO** Razor Pages a pesar del hint del IDE).
- **EF Core 10** + **Pomelo MySQL**.
- **ASP.NET Core Identity** con lockout, security stamp y cookies.
- **Serilog** con sinks a consola y archivo (`Logs/VirtualWallet-*.log`).
- **QuestPDF 2025.x** (Community license) para exportar PDF.
- **HealthChecks** para DB y SMTP.
- **Bootstrap 5**, **jQuery**, **DataTables**, **Select2**, **SweetAlert2**, **Chart.js** en el front.
- **CSRF** via antiforgery en todos los POST/AJAX.

## Arquitectura por capas

```
+----------------------+        +----------------------+
|   VirtualWallet.Web  | -----> | VirtualWallet.       |
|   (MVC, Views, JS)   |        |   Application        |
+----------------------+        +----------------------+
		|                                  |
		v                                  v
+----------------------+        +----------------------+
| VirtualWallet.       | -----> | VirtualWallet.Domain |
|   Infrastructure     |        | (entidades, enums)   |
| (EF Core, services)  |        +----------------------+
+----------------------+
```

### Reglas de dependencia

- `Domain` no referencia a nadie.
- `Application` referencia solo a `Domain` (interfaces y DTOs).
- `Infrastructure` referencia a `Application` y `Domain` (implementa interfaces, EF Core, servicios externos).
- `Web` referencia a `Application`, `Infrastructure` y `Domain` (composicion + DI).
- **Prohibido**: que `Application` o `Domain` referencien a EF Core, ASP.NET o tipos de Web.

### Composition root

`VirtualWallet.Web/Program.cs` es el unico composition root. `VirtualWallet.Infrastructure/DependencyInjection.cs` expone `AddInfrastructure(IConfiguration)` que registra DbContext, repositorios genericos, servicios de cotizacion, importacion, email, parsers, health checks, etc.

## Patrones transversales

- **Soft delete**: entidades heredan de `SoftDestroyable` (`IsDeleted`, `DeletedAt`, `DeletedBy`). Un global query filter las oculta. El override de `SaveChanges` registra auditoria como `Delete` (no como `Update`).
- **Auditoria**: cada cambio en entidades trackeadas genera un `AuditLog` (entity, action, user, before/after JSON).
- **Multi-tenant por usuario**: practicamente toda query filtra por `UsuarioId == User.GetUserId()` (excepto roles administrativos).
- **AntiForgery**: token global publicado en `_Layout.cshtml` y consumido por `site.js` en cada `$.ajax` (header `RequestVerificationToken`).
- **Session**: `AddSession` se usa para persistir filtros del dashboard entre navegaciones.
- **Notifications**: `INotificationService` crea avisos in-app que el header consume via polling (`notifications.js`).
- **Email + ErrorNotifier**: errores no controlados disparan email al admin via `ErrorEmailNotifierMiddleware` + `IErrorNotifier`.

## Modulos funcionales

| Modulo | Controller | Vistas |
|---|---|---|
| Cuentas | `CuentasController` | `Views/Cuentas/*` |
| Categorias / Subcategorias | `CategoriasController`, `SubCategoriasController` | `Views/Categorias/*`, `Views/SubCategorias/*` |
| Movimientos | `MovimientosController` | `Views/Movimientos/*` |
| Cuotas | `CuotasController` | `Views/Cuotas/*` |
| Importacion resumenes | `ImportacionController` | `Views/Importacion/*` |
| Dashboard | `DashboardController` | `Views/Dashboard/*` |
| Usuarios y roles | `UsersController`, `AdminController` | `Views/Users/*`, `Views/Admin/*` |
| Auditoria | `AuditController` | `Views/Audit/*` |
| Sistema y health | `SystemController` | `Views/System/*` |
| Cuenta personal | `AccountController` | `Views/Account/*` |
| Notificaciones | `NotificationsController` | `Views/Notifications/*` |

## Convencion de roles

- `SuperUsuario`: acceso total (admin, usuarios, sistema, auditoria).
- `Usuario`: acceso a sus propios datos financieros y dashboard.
- Policies declaradas en `Program.cs`: `RequireSuperUsuario` y `RequireAdministracion`.
