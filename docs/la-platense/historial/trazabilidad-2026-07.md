<!-- Archivado de docs/la-platense/trazabilidad.md el 2026-10-05 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-07 (1 bloques archivados)

- 2026-07-30 19:00 - implementador (arranque de infraestructura)

---

### 2026-07-30 19:00 - implementador (arranque de infraestructura)
- Etapa: Implementación (arranque)
- Cambio: creado el repositorio real del proyecto en `C:\Sistemas\Ferreteria La Platense`, a partir de una copia saneada de `olvidatasoft-crm` (base .NET 10/Identity/EF Core/MySQL del estudio, mismo patrón usado para crear el propio CRM desde KoiDumplings). Se eliminó toda la lógica de negocio específica del CRM (entidades Contacto/CampanaOutbound/IndustriaCatalogo, servicios de bot/WhatsApp/Google Maps, controllers y vistas de Contactos/Chats/Campañas/Industrias/Bot, todas las migraciones EF existentes) y se conservó la infraestructura base reutilizable (Identity, notificaciones in-app, email, exportación, health checks, middleware de errores, layout). Proyecto renombrado de `OlvidataCRM` a `FerreteriaLaPlatense` en carpetas, `.slnx`, `.csproj` y namespaces. Se creó el workspace `C:\Sistemas\Ferreteria La Platense.code-workspace` (folders: proyecto + Agentes-IA).
- Motivo: pedido explícito de Joaquín — arrancar el desarrollo de La Platense sobre una base técnica actualizada en vez de crear un proyecto desde cero, reutilizando el mismo patrón de "copiar y sanear" ya usado antes en el estudio.
- Impacto en capas: las 4 capas del proyecto (Domain/Application/Infrastructure/Web) — ver detalle completo en el mensaje de confirmación de borrado (no repetido acá por extensión).
- Riesgos/supuestos: **se encontraron y corrigieron 3 hallazgos de seguridad reales al hacer la copia**, no relacionados con la limpieza de lógica de negocio en sí: (1) `appsettings.Production.json` tenía credenciales reales del CRM en texto plano (MySQL, SMTP, WhatsApp, Google Maps) — reemplazado por template vacío; (2) `ssl/` tenía la clave privada real del certificado de `portal.olvidata.com.ar` — eliminada; (3) los publish profiles (`Properties/PublishProfiles/*.pubxml`) apuntaban al sitio real del CRM en producción (`olvidatasoft-002-site12`) — eliminados por completo, para que un `dotnet publish` accidental no pise el CRM real. El `.git` original (con remote al repo real del CRM) se reinició limpio, a pedido explícito de Joaquín. Build verificado (`dotnet build`, 0 errores) tras la limpieza y el renombrado. Todavía no hay ninguna entidad ni migración EF de la ferretería — el `AppDbContext` quedó con un comentario placeholder apuntando a `3-arquitecto-mvc.md` para cuando arranque la implementación real de los módulos.
