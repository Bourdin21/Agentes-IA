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
