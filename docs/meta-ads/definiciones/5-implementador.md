# Memoria - Implementador

## Proyecto: meta-ads
## Ultima actualizacion: 2026-05-14

## Features completadas

### 2026-05-13 — Proyecto inicial: discovery y estructura base
- **Scripts de diagnostico**: `check_token.py`, `check_ig.py`, `discover_ig.py` para validar tokens de acceso, descubrir cuentas de Instagram vinculadas y verificar permisos de la API.
- **Fetch de posts**: `fetch_ig_posts.py` (posts de Instagram) y `fetch_page_posts.py` (posts de Facebook Page) para obtener los IDs de contenido organico a usar como creatividades.
- **Mapeo de creatividades**: `map_posts.py` genera `creative_mapping.json` asociando cada post a su campana/ad set objetivo.
- **Cliente .NET**: `MetaAdsClient.cs` (HttpClient con `MetaAdsRetryHandler`), `MetaAdsModels.cs` (DTOs), `OlvidataCampaignBuilder.cs` (builder pattern para campanas). Proyecto `Olvidata.MetaAds.csproj` apuntado a .NET 10.
- **Script principal dry-run**: `create_olvidata_campaigns.py` con soporte `DRY_RUN=true` por defecto, `--search` para discovery de intereses, `--force` para recreacion. Estructura de 3 campanas con targeting por intereses gastronomia/tecnologia/startups (pendiente ajuste final).

### 2026-05-14 — Campanas creadas en produccion Meta
- `create_olvidata_campaigns.py` finalizado con estructura de campanas aprobada.
- Ejecutado en modo real (`DRY_RUN=false`): campanas, ad sets y ads creados en la cuenta de Meta Ads de Olvidata Soft.
- `olvidata_ads_ids.json` generado con todos los IDs reales para reuso y actualizaciones futuras.
- `creative_mapping.json` actualizado con los creative IDs finales.

## Configuracion requerida
- Archivo `.env` (basado en `.env.template`) con:
  - `ACCESS_TOKEN`: token de usuario de larga duracion con permisos `ads_management`, `ads_read`, `pages_read_engagement`.
  - `AD_ACCOUNT_ID`: ID de la cuenta publicitaria (`act_XXXXXXXXXX`).
  - `PAGE_ID`: ID de la pagina de Facebook.
  - `INSTAGRAM_ACTOR_ID`: ID de la cuenta de Instagram Business.
  - `DRY_RUN`: `true` por defecto, `false` para ejecucion real.

## Riesgos residuales
- Tokens de Meta expiran; renovar via `check_token.py` antes de cada corrida productiva.
- Los IDs en `olvidata_ads_ids.json` son de produccion real: usar `--force` solo con intencion de reemplazar campanas existentes.
- El cliente .NET (`MetaAdsClient`) no tiene tests automatizados; usar solo como referencia para integraciones futuras con sistemas MVC.

## Proximos pasos
- Monitorear metricas de las campanas creadas via Meta Ads Manager.
- Evaluar integracion del cliente .NET con un sistema MVC existente (ej. dashboard de campanas en vinosefue o ShowroomGriffin).
- Renovar token de acceso cuando expire (tipicamente 60 dias para tokens de larga duracion).
