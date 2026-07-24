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
