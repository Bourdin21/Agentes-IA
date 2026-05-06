# 4 - Web (UI MVC)

Proyecto: `VirtualWallet.Web`. ASP.NET Core MVC clasico (controllers + views Razor). **No** Razor Pages.

## Pipeline (`Program.cs`)

Resumen del pipeline (orden):

1. Serilog (bootstrap + `UseSerilog` con configuracion).
2. `AddInfrastructure(Configuration)`.
3. Identity con lockout (5 intentos / 15 min) y password policy.
4. `SecurityStampValidatorOptions` (revalidacion cada 5 min) - corta sesiones de bloqueados.
5. Cookie hardening (`HttpOnly`, `SecurePolicy.Always`, `SameSite.Lax`, `ExpireTimeSpan = 8h`, sliding).
6. Authorization policies (`RequireSuperUsuario`, `RequireAdministracion`).
7. `AddControllersWithViews()`.
8. `AddSession` (memory cache distribuido) para filtros del dashboard.
9. `AddAntiforgery`, `AddHealthChecks`.
10. Middleware: `UseSerilogRequestLogging`, `UseHttpsRedirection`, `UseStaticFiles`, `UseRouting`, `UseAuthentication`, `UseAuthorization`, `UseSession`, `ErrorEmailNotifierMiddleware`, `MapControllerRoute`, `MapHealthChecks`.

## Controllers

Cada uno protegido por `[Authorize]` salvo `AccountController`. Convenciones:

- Filtran siempre por `User.GetUserId()`.
- Para listados: server-side DataTables via endpoint `*Datatable` que devuelve `DataTablesResponse<TVm>`.
- Para mutaciones AJAX: `[ValidateAntiForgeryToken]` y devuelven JSON.
- POST tradicionales (sin AJAX) tambien `[ValidateAntiForgeryToken]`.

### `DashboardController` (criterio especial)

Persiste filtros (`periodo`, `moneda`, `cuentaId`) en `Session` para que la moneda elegida sobreviva navegaciones (ResumenGeneral <-> EvolucionTendencias).

- `ResumenGeneral`: KPIs del periodo, top 10 gastos, deuda de tarjeta, cuotas activas, alertas.
- `EvolucionTendencias`: serie anual, comparacion historica, proyeccion, gastos por subcategoria.

Reglas clave (ya implementadas):
- Excluye `EsPagoTarjeta` de aggregations de gasto y de subcategoria.
- Compara periodos por **mes calendario** (no por cantidad de dias).
- Top 10 ordenado de forma estable (monto desc + Id desc).
- Alerta de crecimiento por categoria si crecio >=30% vs periodo equivalente anterior y supera monto minimo.
- Cuotas activas considera reales pendientes y muestra `CuotasRestantes`/`MontoPendiente`.
- Deuda de tarjeta calcula `SaldoArrastrado` del ciclo previo.

### `MovimientosController`

- `Create`/`Edit` bindean `EsPagoTarjeta`; lo fuerzan a `false` si `Tipo == Ingreso`.
- Cuentas inactivas siguen visibles en `Edit` (no se filtran del select).
- Movimientos con `CuotaId != null` no permiten edit/delete individual (los gestiona la cuota).
- Endpoints AJAX: `Autocomplete` (descripciones recientes), `GetSubCategorias`, `CambiarEstado`.

### `ImportacionController`

- `Preview(IFormFile pdf, string banco, string marca)`: invoca importer en modo preview.
- `Confirmar(...)`: persiste y muestra `Resultado.cshtml` con contadores (incluye `CuotasReutilizadas`).

### `UsersController` y `AdminController`

- Paginacion EF-based (no carga full table).
- Bloquear usuario invalida security stamp (cierra sesiones activas).
- Borrado de usuario revisa dependencias antes.

## Views (Razor)

Layout: `Views/Shared/_Layout.cshtml`. Incluye:

- Navbar con notificaciones (consume `notifications.js`).
- Toaster de SweetAlert.
- Antiforgery token global publicado para que `site.js` lo lea y lo inyecte como header en cada `$.ajax`.
- Bootstrap 5, jQuery, DataTables, Select2, Chart.js (cargados desde `wwwroot/lib`).

Convenciones de vistas:

- Formularios usan `asp-for`, `asp-validation-for`, y la validacion unobtrusive (`_ValidationScriptsPartial`).
- Listados con DataTables server-side.
- Botones de accion peligrosa abren modal SweetAlert antes de POST.
- Iconos: Bootstrap Icons (`<i class="bi bi-...">`).
- CSS de marca: `wwwroot/css/olvidata-theme.css` define paleta y tipografia. `site.css` extiende.

## ViewModels (`Models/*`)

| ViewModel | Vistas que lo consumen |
|---|---|
| `LoginViewModel` | `Account/Login` |
| `PerfilViewModels` | `Account/Perfil`, `Account/CambiarPassword` |
| `AbmViewModels` (Cuenta, Categoria, SubCategoria, Cuota, Movimiento) | ABMs respectivos. `MovimientoFormViewModel` incluye `EsPagoTarjeta`. |
| `DataTableModels` | DataTables wrappers. |
| `ResumenGeneralViewModel` | `Dashboard/ResumenGeneral` |
| `EvolucionTendenciasViewModel` | `Dashboard/EvolucionTendencias` |
| `DashboardViewModel` | (legacy / shared bits) |
| `ImportarResumenViewModel` | `Importacion/Preview`, `Importacion/Resultado`, `Importacion/Resumen` |
| `UserViewModels` | `Users/*`, `Admin/Index` |
| `ErrorViewModel` | `Shared/Error` |

## JavaScript (`wwwroot/js`)

- `site.js`: inicializa DataTables defaults, registra antiforgery header, helpers (formato moneda, confirmaciones SweetAlert), select2 defaults.
- `notifications.js`: poll a `/Notifications/Count` y `/Notifications/Recent`.

## PWA

`wwwroot/manifest.webmanifest` + `wwwroot/sw.js` declaran PWA basica. Iconos en `wwwroot/icons/`.

## Helpers

- `Helpers/FormatoMoneda.cs`: `FormatoMoneda.Formatear(decimal, string moneda)` con cultura `es-AR`.
