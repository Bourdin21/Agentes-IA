# Runbook: Aplicar migraciones EF en PRODUCCION — ShowroomGriffin

> Mergeado a Agentes-IA el 2026-07-23 desde `C:\Sistemas\ShowroomGriffin\docs\runbooks\migraciones-produccion.md` (barrido cross-proyecto de memorias). Contiene datos operativos reales del hosting de produccion, incluida una credencial en texto plano ya presente en el repo del proyecto — considerar rotarla periodicamente, no se redacta aca porque inutilizaria el runbook.

## Contexto
Servidor: `mysql5045.site4now.net`
Base: `db_a7251f_showroo`
Usuario: `a7251f_showroo`

> Las credenciales viven en `ShowroomGriffin.Web\appsettings.Production.json`. **No las pegues en consolas compartidas ni en logs**.

## Pre-requisitos
- Acceso al panel del hosting (site4now) o cliente MySQL local con red abierta al servidor.
- `dotnet-ef` instalado: `dotnet tool install --global dotnet-ef`.
- Build OK en local (`dotnet build`).
- Backup reciente.

## Backup obligatorio
Desde el panel del hosting (recomendado) o por CLI:
```bash
mysqldump -h mysql5045.site4now.net -u a7251f_showroo -p `
  --single-transaction --routines --triggers `
  db_a7251f_showroo > backup_PROD_$(Get-Date -Format yyyyMMdd_HHmm).sql
```

## Verificar estado actual
```sql
SELECT MigrationId FROM `__EFMigrationsHistory` ORDER BY MigrationId DESC LIMIT 10;
```
Debe figurar `20260416154337_M1_AddMaestrosComerciales` como ultima aplicada (o una posterior — ver tabla de migraciones en `metadata.md`).

## Camino A (recomendado): EF Core gestiona todo

Desde la maquina de desarrollo, con conectividad al servidor:

```powershell
cd C:\Sistemas\ShowroomGriffin
dotnet ef database update `
  --project ShowroomGriffin.Infrastructure `
  --startup-project ShowroomGriffin.Web `
  --connection "Server=mysql5045.site4now.net;Database=db_a7251f_showroo;Uid=a7251f_showroo;Pwd=_01vid4t4_"
```

Si la base **ya tiene filas en VariantesProducto** y EF falla con error de NOT NULL al agregar `RowVersion`, usar el Camino B con el SQL ajustado.

## Camino B: SQL manual ajustado

Archivo: `ShowroomGriffin.Web/Migrations-Scripts/PROD_AplicarMigracionesPendientes.sql`

Ejecutar contra la base de produccion con cualquier cliente MySQL (HeidiSQL, MySQL Workbench, phpMyAdmin del hosting, o CLI):

```bash
mysql -h mysql5045.site4now.net -u a7251f_showroo -p db_a7251f_showroo `
  < ShowroomGriffin.Web/Migrations-Scripts/PROD_AplicarMigracionesPendientes.sql
```

El script:
1. Agrega `RowVersion` como NULL.
2. Rellena con UUID en filas existentes.
3. Pasa a NOT NULL.
4. Registra las 3 migraciones en `__EFMigrationsHistory`.
5. Agrega `CantidadCuotas` a `VentasPago`.

Todo dentro de una transaccion.

## Verificacion post-deploy

```sql
SELECT MigrationId FROM `__EFMigrationsHistory` ORDER BY MigrationId DESC LIMIT 5;
-- Debe incluir:
--   20260429155923_AddCantidadCuotasToVentaPago
--   20260429144953_M2_FixRowVersionVariante
--   20260428212244_M2_AddRowVersionToVariante

SHOW COLUMNS FROM `VariantesProducto` LIKE 'RowVersion';
-- Type: longblob, Null: NO

SHOW COLUMNS FROM `VentasPago` LIKE 'CantidadCuotas';
-- Type: int, Null: YES

SELECT COUNT(*) FROM `VariantesProducto` WHERE `RowVersion` IS NULL;
-- 0
```

## Rollback (si algo sale mal)

> No hay Down() automatico para estos cambios; lo mas rapido es restaurar el backup.

Manual:
```sql
ALTER TABLE `VentasPago` DROP COLUMN `CantidadCuotas`;
ALTER TABLE `VariantesProducto` DROP COLUMN `RowVersion`;
DELETE FROM `__EFMigrationsHistory`
WHERE MigrationId IN (
  '20260429155923_AddCantidadCuotasToVentaPago',
  '20260429144953_M2_FixRowVersionVariante',
  '20260428212244_M2_AddRowVersionToVariante'
);
```

## Despues de migrar

1. Hacer **deploy del binario** correspondiente al codigo que usa `RowVersion` y `CantidadCuotas`.
2. Smoke tests:
   - Crear venta con pago Cuotas (cantidad >= 2 + % financ).
   - Crear / editar variante.
   - Ver `Ventas/Detalle` con columna Cuotas.
3. Marcar el deploy en `docs/qa/regresiones-manuales.yml` como verificado en prod (REG-001 y REG-006).

## Riesgos / supuestos
- Supuesto: ya hay datos en `VariantesProducto`. Si la tabla esta vacia, el Camino A o B funcionan igual.
- Riesgo: la cadena de produccion contiene credenciales en texto plano. Considerar rotar el password post-deploy si se compartio en herramientas externas.
- Riesgo: `dotnet ef database update` requiere acceso de red al servidor MySQL (puede haber whitelisting de IP en site4now).

## Script automatizado (recomendado)

`scripts/Apply-ProdMigrations.ps1` (en el repo del proyecto) encadena backup + apply + verify:
- Lee la cadena desde `appsettings.Production.json` (no la imprime).
- Pide confirmacion explicita (`APLICAR`).
- Backup con `mysqldump` (si esta en PATH).
- Aplica via EF (default) o SQL ajustado (`-Modo SQL`).
- Verifica `__EFMigrationsHistory`, `RowVersion` sin nulos y columna `CantidadCuotas`.

```powershell
# Default (EF):
pwsh .\scripts\Apply-ProdMigrations.ps1

# Si EF falla por NOT NULL sobre filas existentes:
pwsh .\scripts\Apply-ProdMigrations.ps1 -Modo SQL
```

## Checklist salida
- [ ] Backup tomado y verificado.
- [ ] Estado previo de `__EFMigrationsHistory` registrado.
- [ ] Migracion aplicada (Camino A o B).
- [ ] Verificaciones post-deploy todas OK.
- [ ] Deploy de binarios.
- [ ] Smoke tests funcionales OK.
- [ ] Credenciales no quedaron en logs/consolas compartidas.
