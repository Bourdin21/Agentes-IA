# Metadata del proyecto

- nombre: decorhogar *(provisional — confirmar con cliente)*
- fecha_inicio: 2026-06-29
- estado: activo
- owner: Joaquín Bourdin
- descripcion: Sistema de gestión y automatización de ventas para casa de decoración y hogar. Captación de leads via Meta Ads + WhatsApp, seguimiento CRM, catálogo de productos, presupuestador y registro de ventas.
- ruta_definiciones: /docs/decorhogar/definiciones
- ruta_repositorio: C:\Sistemas\decorhogar *(a confirmar)*

## Stack confirmado
- .NET 10 / EF Core 10 / ASP.NET Core Identity / MySql.EntityFrameworkCore v10.0.1 (Oracle)
- QuestPDF (presupuestos + facturas PDF), Serilog, MailKit
- WhatsApp Business Cloud API (Meta) — reutilizar WhatsAppClient.cs de BotPublicitario
- AFIP WSAA + WSFE (.NET 10 SOAP client, patrón delicias-naturales)
- Hosting: SMARTEASP olvidatasoft (confirmado compatible con webhook Meta y AFIP)

## Reutilización de componentes existentes
- `WhatsAppClient.cs`, `MessagingService.cs` de `C:\Sistemas\BotPublicitario\WhatsApp\`
- Patrón AFIP (.p12, WSAA token 24h, FECAESolicitar) de `C:\Sistemas\delicias-naturales\`

## Archivos de memoria por agente
- analista-funcional: /docs/decorhogar/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/decorhogar/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/decorhogar/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/decorhogar/definiciones/4-presupuestador.md
- implementador: /docs/decorhogar/definiciones/5-implementador.md
- qa: /docs/decorhogar/definiciones/6-qa.md
- documentador: /docs/decorhogar/definiciones/7-documentador.md
