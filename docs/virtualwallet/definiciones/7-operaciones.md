# 7 - Operaciones (deploy, migraciones, configuracion)

## Entornos

| Entorno | DB | Hosting | Notas |
|---|---|---|---|
| Development | MySQL local (docker o servicio) | `dotnet run` o VS | `appsettings.Development.json`, secretos via User Secrets. |
| Production | MySQL en `olvidatasoft-002` | IIS/Plesk via FTP o Web Deploy | Profiles en `Properties/PublishProfiles/`. |

## Build y test local

```powershell
cd C:\Sistemas\virtualwallet
 dotnet build VirtualWallet.sln -c Debug
```

Build se valida con la herramienta `run_build` del agente. **Antes de finalizar cualquier tarea de codigo, ejecutar build**.

## Migraciones EF Core

Generar nueva migracion (proyecto Infrastructure, startup Web):

```powershell
 dotnet ef migrations add NombreMigracion --project VirtualWallet.Infrastructure --startup-project VirtualWallet.Web --output-dir Data/Migrations
```

Aplicar a DB local:

```powershell
 dotnet ef database update --project VirtualWallet.Infrastructure --startup-project VirtualWallet.Web
```

Generar **script SQL idempotente** para produccion (la app NO aplica migraciones automaticamente en prod):

```powershell
 dotnet ef migrations script <PrevMigracion> <NuevaMigracion> --project VirtualWallet.Infrastructure --startup-project VirtualWallet.Web --idempotent --output VirtualWallet.Infrastructure/Data/Migrations/Scripts/<Nombre>.sql
```

Convenciones:
- Nombrar migraciones en `PascalCase`, descriptivo (verbo + objeto). Ej: `AddEsPagoTarjetaToMovimiento`, `ConstrainDescripcionOriginalLength`.
- Output dir: `Data/Migrations`. La carpeta `Data/Mig/` es un accidente legado; nuevas migraciones van en `Data/Migrations`.
- Cada migracion productiva genera su `*.sql` idempotente versionado en `Data/Migrations/Scripts/`.

## Deploy

Profiles existentes en `VirtualWallet.Web/Properties/PublishProfiles/`:
- `olvidatasoft-002-site7 - FTP.pubxml`
- `olvidatasoft-002-site7 - Web Deploy.pubxml`

Pasos tipicos:
1. `dotnet publish VirtualWallet.Web -c Release`.
2. Aplicar SQL de migracion en MySQL prod (manual, idempotente).
3. Subir artefactos por FTP o Web Deploy.
4. Validar `/health` autenticado y vista principal.

## Configuracion sensible

- Cadenas de conexion, SMTP y claves API se setean via:
  - User Secrets en dev: `dotnet user-secrets set ...` sobre `VirtualWallet.Web`.
  - Variables de entorno en produccion (preferido) o `appsettings.Production.json` no commiteado con valores reales.
- `QuestPDF.Settings.License = LicenseType.Community` se fija en `Program.cs`. **No** commitear claves Pro.

## Logs

- `VirtualWallet.Web/Logs/VirtualWallet-{env}-yyyyMMdd.log`: log general.
- `VirtualWallet.Web/Logs/VirtualWallet-errors-{env}-yyyyMMdd.log`: solo errores.
- Rotacion diaria, retencion configurada en `appsettings.*` -> `Serilog`.

## Health checks

- `/health` -> general (DB + SMTP).
- `/health/ready` -> readiness.
- **Requieren autorizacion**, no son anonimos.

## Backups

(Pendiente formalizar) Recomendado dump diario de MySQL prod + retencion 14 dias. El responsable es el operador del hosting.

## Procedimientos recurrentes

- **Reset password**: admin desde `Users/Edit` o flujo `Account/CambiarPassword` para self-service.
- **Bloquear usuario**: `Users/Edit` -> Estado Bloqueado. La security stamp invalida sesiones activas en <=5 min.
- **Auditar cambios**: `Audit/Index` con filtros por entidad, usuario, accion, rango.
- **Reimportar resumen**: subir PDF nuevamente; el importer detecta cuotas existentes y cuenta `CuotasReutilizadas`.
