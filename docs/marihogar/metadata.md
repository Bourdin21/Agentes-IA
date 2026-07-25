# Metadata del proyecto

- nombre: marihogar *(confirmado)*
- fecha_inicio: 2026-06-29
- estado: activo
- owner: Joaquín Bourdin
- descripcion: Sistema de gestión comercial completo para casa de decoración y hogar (reemplazo de Contagram) — catálogo, stock, presupuestos, ventas, entregas, facturación AFIP/ARCA, compras a proveedores, cheques, financiero (CC local/proveedores, caja, proyección), y en Etapa 2 (en espera) captación de leads vía Meta Ads + WhatsApp con CRM.
- ruta_definiciones: /docs/marihogar/definiciones
- ruta_repositorio: C:\Sistemas\marihogar
- repositorio_git: git@gitlab.com:olvidata/mari-hogar.git (remote `origin` configurado 2026-07-24)

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
- analista-funcional: /docs/marihogar/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/marihogar/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/marihogar/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/marihogar/definiciones/4-presupuestador.md
- implementador: /docs/marihogar/definiciones/5-implementador.md
- qa: /docs/marihogar/definiciones/6-qa.md
- documentador: /docs/marihogar/definiciones/7-documentador.md
