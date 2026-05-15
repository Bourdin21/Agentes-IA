# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes.

## Entradas

### 2026-05-13 - implementador
- Etapa: Implementacion inicial
- Cambio: creacion del proyecto desde cero. Scripts Python para discovery de tokens/IDs de Instagram y Facebook Page. Creacion del script principal `create_olvidata_campaigns.py` con soporte dry-run. Mapeo de posts a creatividades (`map_posts.py`, `creative_mapping.json`). Cliente .NET (`MetaAdsClient.cs`, `MetaAdsModels.cs`, `MetaAdsRetryHandler.cs`, `OlvidataCampaignBuilder.cs`) para integracion futura con sistema MVC.
- Motivo: automatizar la creacion de campanas de Meta Ads para los productos de Olvidata Soft.
- Impacto en capas: N/A (proyecto standalone Python + lib .NET).
- Riesgos/supuestos: credenciales en `.env` (no commiteadas). Dry-run por defecto para evitar cargos accidentales.

### 2026-05-14 - implementador
- Etapa: Ajuste de campanias y generacion de IDs
- Cambio: `create_olvidata_campaigns.py` finalizado con estructura completa de 3 campanas. `olvidata_ads_ids.json` generado con IDs reales de campanas, ad sets y ads creados en produccion Meta. `creative_mapping.json` actualizado con creatives finales.
- Motivo: primer deploy real de campanas en Meta Ads para Olvidata Soft.
- Impacto en capas: N/A.
- Riesgos/supuestos: IDs guardados en `olvidata_ads_ids.json` para reuso/actualizacion sin recrear.
