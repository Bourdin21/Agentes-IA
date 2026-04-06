---
description: Reglas de Infrastructure (AppDbContext, repositorio, servicios, health checks y seed).
applyTo: "**/Infrastructure/**/*.cs"
---

# AppDbContext
- Hereda de IdentityDbContext<ApplicationUser>.
- Aplica query filter global para SoftDestroyable.
- En SaveChangesAsync: auditoria automatica de campos y creacion de AuditLog.
- Usa IHttpContextAccessor para usuario actual e IP.

# Repository<T>
- DeleteAsync hace soft delete (set DeletedAt), nunca Remove fisico.
- AddAsync y UpdateAsync no invocan SaveChangesAsync.
- Queries complejas: usar AppDbContext directo en servicios.

# Servicios
- EmailService (MailKit SMTP: 465 SslOnConnect, 587 StartTls).
- ErrorNotifier (fire-and-forget, destino en Olvidata_ErrorEmail:Destinatarios).
- NotificationService (CRUD directo en Notifications).
- ExportService (ClosedXML + QuestPDF; headers por Display).

# Health checks y seed
- /health con DatabaseHealthCheck y SmtpHealthCheck.
- SeedData crea roles SuperUsuario/Administrador y superusuario inicial.
