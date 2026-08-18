---
description: Baseline tecnico de BlankProject (.NET 10, EF Core 10, MySQL, Identity, Serilog).
applyTo: "**/*.{cs,csproj,json,cshtml,css,js}"
---

# Informacion general del proyecto
- Framework: .NET 10 (ASP.NET Core MVC)
- C# version: 14.0
- Nullable: enable
- ImplicitUsings: enable
- Base de datos: MySQL (MySql.EntityFrameworkCore)
- ORM: Entity Framework Core 10
- Autenticacion: ASP.NET Core Identity
- Logging: Serilog
- Email: MailKit (SMTP)
- Export Excel: ClosedXML
- Export PDF: QuestPDF (Community License)
- Cultura: es-AR (fija)

# Arquitectura Clean Architecture (4 capas)
- BlankProject.Domain: Entidades, Enums.
- BlankProject.Application: Interfaces, DTOs.
- BlankProject.Infrastructure: EF Core, repositorios, servicios, health checks.
- BlankProject.Web: Controllers, Views, Middleware, ViewModels.

# Reglas de dependencia estrictas
- Domain no depende de otros proyectos (excepto Identity.Stores).
- Application depende solo de Domain.
- Infrastructure depende de Application + Domain.
- Web depende de Domain + Application + Infrastructure.

# Registro de servicios
- Infrastructure expone AddInfrastructure(IConfiguration) en DependencyInjection.cs.
- Web llama builder.Services.AddInfrastructure(builder.Configuration) en Program.cs.
- Default: registro Scoped salvo excepcion justificada.

# Bugs conocidos del template base (aplican a todo proyecto BlankProject)

- **`GlobalExceptionHandler` + `IErrorNotifier` (runtime failure)**: registrar `GlobalExceptionHandler` via `builder.Services.AddExceptionHandler<GlobalExceptionHandler>()` falla en runtime si el handler inyecta `IErrorNotifier` — `AddExceptionHandler<T>()` registra el handler como Singleton, pero `IErrorNotifier` esta registrado como Scoped, y un Singleton no puede depender de un Scoped (falla al resolver el scope). Fix: registrar explicitamente como Scoped en vez de usar el extension method generico:
  ```csharp
  builder.Services.AddScoped<IExceptionHandler, GlobalExceptionHandler>();
  ```
  Detectado originalmente en el proyecto century-21; como es un bug del template base (no del proyecto puntual), aplicar este registro en todo proyecto nuevo desde el arranque (Etapa 0 / bootstrap de la solucion), no solo cuando el error aparezca en runtime.

- **`HttpsPort = 443` hardcodeado rompe el arranque local via `dotnet run`/VS Code (no via IIS Express)**: `Program.cs` configura `builder.Services.AddHttpsRedirection(options => options.HttpsPort = 443)` de forma incondicional (fuera del `if (IsDevelopment())`), pensado para produccion detras de IIS/reverse proxy en el puerto 443 estandar. En local, Kestrel expone HTTPS en el puerto de `launchSettings.json` (tipicamente 7200, no 443) — cualquier request que llegue por HTTP recibe un `307` hacia `https://localhost/...` **sin puerto explicito** (implica 443), y como nada escucha ahi localmente, el navegador falla con "no se puede acceder a este sitio" / puerto no reconocido. Confirmado reproduciendo el request real: `curl http://localhost:5015/...` → `307 Location: https://localhost/...`; `curl https://localhost:7200/...` → `200 OK`. Sintoma tipico reportado por el cliente: "no funciona el proyecto cuando lo levanto, no reconoce el puerto".
  - **Fix para desarrollo local (no tocar el codigo de produccion)**: en `.vscode/launch.json` (o el perfil que se use para correr localmente), bindear Kestrel a ambos puertos (`ASPNETCORE_URLS=https://localhost:<puerto-https-launchSettings>;http://localhost:<puerto-http-launchSettings>`) y forzar que el navegador abra siempre la URL **HTTPS** directamente (`serverReadyAction.pattern` con `https://` explicito, nunca `https?://` ambiguo — Kestrel loguea la linea `https` primero, pero un regex ambiguo puede matchear la de `http` segun el orden real de output). Nunca acceder a la app localmente por el puerto HTTP: cualquier request que llegue por HTTP siempre va a redirigir al 443 inexistente.
  - Aplicar este mismo criterio (bindear ambos puertos + abrir siempre HTTPS) al bootstrap de todo proyecto nuevo que configure `.vscode/launch.json` para debug local, no solo cuando el sintoma aparezca.

- **`DateTime.Now` da la hora del servidor, no la de Argentina — usar siempre `ArgentinaTime.Now`**: en hosting compartido la zona horaria del SO casi nunca es Argentina (confirmado en produccion real: timestamps con offset de zona horaria de EE.UU.), asi que `DateTime.Now`/`.ToLocalTime()` le muestran al cliente una hora incorrecta, con horas de diferencia y hasta dia distinto en horario nocturno. El template ya trae el helper resuelto en `BlankProject.Application/Helpers/ArgentinaTime.cs` (`ArgentinaTime.Now`, `ArgentinaTime.From(utc)`, `ArgentinaTime.HoyRangoUtc()` para queries EF de "hoy calendario"). Usarlo desde el arranque de todo proyecto nuevo para cualquier fecha/hora visible al usuario o usada en logica de negocio sensible a dia calendario (topes diarios, reportes "de hoy") — nunca `DateTime.Now` directo en Web/Infrastructure.
