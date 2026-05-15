# Meta Ads — Automatizacion de campanas publicitarias

Proyecto de automatizacion de Meta Ads (Facebook/Instagram) para Olvidata Soft.

## Stack
- **Python 3.12**: scripts de creacion de campanas y discovery de IDs/tokens.
- **.NET 10 (C#)**: cliente `MetaAdsClient` para integracion futura con sistemas MVC.
- **Meta Marketing API v21**.

## Componentes

| Archivo | Descripcion |
|---|---|
| `create_olvidata_campaigns.py` | Script principal. Crea estructura de 3 campanas con dry-run por defecto. |
| `map_posts.py` | Mapea posts de Instagram/Facebook a creatividades. |
| `fetch_ig_posts.py` / `fetch_page_posts.py` | Discovery de posts de la pagina. |
| `discover_ig.py` / `check_ig.py` / `check_token.py` | Herramientas de diagnostico de tokens e IDs. |
| `creative_mapping.json` | Mapa post -> creative para las campanas. |
| `olvidata_ads_ids.json` | IDs reales generados en produccion Meta (campanas, ad sets, ads). |
| `MetaAdsClient.cs` | Cliente .NET para Meta Marketing API con retry handler. |
| `OlvidataCampaignBuilder.cs` | Builder de campanas para uso desde sistemas .NET. |
| `.env` / `.env.template` | Credenciales (no commiteadas). |

## Uso rapido

```bash
# Dry-run (default, no toca la API)
python create_olvidata_campaigns.py

# Buscar IDs de intereses
python create_olvidata_campaigns.py --search "gastronomia"

# Ejecutar real
DRY_RUN=false python create_olvidata_campaigns.py

# Forzar recreacion
python create_olvidata_campaigns.py --force
```

## Estado
- Campanas iniciales creadas en produccion Meta el 2026-05-14.
- IDs persistidos en `olvidata_ads_ids.json`.
