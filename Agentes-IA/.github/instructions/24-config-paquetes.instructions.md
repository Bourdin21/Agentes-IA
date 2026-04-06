---
description: Configuracion de appsettings, SMTP, Serilog y paquetes NuGet por proyecto.
applyTo: "**/*.{csproj,json}"
---

# Claves de configuracion esperadas
- ConnectionStrings:DefaultConnection
- Olvidata_Email:Smtp
- Olvidata_ErrorEmail:Destinatarios
- Seed:SuperUser
- Serilog

# SMTP esperado
- Host: vps-5574162-x.dattaweb.com
- User/FromAddress: no-reply@olvidata.com.ar
- SSL: true, Port: 465

# Serilog por ambiente
- Development: Console + File errors, min Information.
- Production: File errors, min Warning.

# Paquetes NuGet por proyecto
- Domain: Microsoft.Extensions.Identity.Stores 10.0.2
- Infrastructure: EF Core 10.0.2, Identity EF 10.0.2, MySql.EntityFrameworkCore 10.0.1, MailKit 4.14.1, ClosedXML 0.105.0, QuestPDF 2025.12.4
- Web: Identity EF 10.0.2, EF.Design 10.0.2, Serilog.AspNetCore 9.0.0
