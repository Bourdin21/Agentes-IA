# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes.

## Entradas

### 2026-07-01 — analista-funcional
- Etapa: Discovery + Análisis funcional (borrador)
- Cambio: Nueva extensión del proyecto — "Bot de respuesta automática WhatsApp". Relevado el código actual de `BotPublicitario`: outbound (Canal B) completo; inbound solo loguea mensajes, sin respuesta automática ni parseo de `referral`. Definidos 7 módulos nuevos (N1-N7): parser de referral, máquina de estados por contacto, motor de calificación por rubro, calculador de presupuesto, envío, persistencia unificada y notificación a Joaquín. Mismo patrón conceptual que M8 de decorhogar, aplicado a los 8 sistemas propios de OlvidataSoft (HEAVEN/SIGMA/OLVIDATES/FORGE/CREW/FLOW/BUILD/LANDING).
- Motivo: cliente quiere automatizar el tramo entre "el prospecto responde" y "se le envía un presupuesto", hoy 100% manual, en los dos canales de captación (ads pagos y outbound frío).
- Impacto en capas: N/A (proyecto standalone .NET Console + Webhook, sin capas MVC).
- Riesgos/supuestos: reutiliza infraestructura de mensajería existente sin reescritura. Quedan 3 abiertos que bloquean el pase a Diseño: (1) variable de ajuste de precio por cada uno de los 8 sistemas, (2) mecánica de la pregunta de calificación (botones interactivos vs texto libre), (3) si se unifica la persistencia de leads de ambos canales o quedan separados.

### 2026-07-01 — analista-funcional (cierre de análisis)
- Etapa: Análisis funcional — cierre
- Cambio: Resueltos los 3 abiertos. Ajuste de precio = usuarios extra (USD 100/año c/u sobre incluidos por plan). Calificación por texto libre. Persistencia unificada por número de teléfono. Se detectó y resolvió una contradicción entre `plan_contacto_whatsapp.md` (precio fijo por sistema vertical) y la página pública `precios.astro` (4 planes por cantidad de tablas) — se adopta esta última como fuente de verdad, con mapeo HEAVEN/SIGMA→PREMIUM ($400), OLVIDATES/FORGE/CREW/FLOW→PRO ($300). BUILD y LANDING quedan fuera de cotización automática por no tener cantidad de tablas fija.
- Motivo: cliente confirmó explícitamente que los sistemas verticales son productos ya desarrollados con cantidad de tablas fija, que determina el plan público.
- Impacto en capas: N/A. Cierra el análisis funcional — habilita el pase a Diseño.
- Riesgos/supuestos: `plan_contacto_whatsapp.md` queda desactualizado respecto al mapeo real de precios; no se actualiza en este proyecto (doc de proceso comercial, fuera de alcance técnico).

### 2026-07-01 — analista-funcional (reemplazo de verticales ficticios por industrias reales)
- Etapa: Análisis funcional — ajuste post-cierre
- Cambio: Reemplazados los nombres de marca ficticios (HEAVEN/SIGMA/OLVIDATES/FORGE/CREW/FLOW/BUILD/LANDING) por 13 industrias reales, relevadas con un agente de exploración que contó tablas reales (DbContext/migraciones EF) de los sistemas ya construidos en `C:\Sistemas\`: Delicias Naturales, KOI Dumplings, Vino y Se Fue (gastronomía, PREMIUM), ShowroomGriffin (retail, PREMIUM), TicketMarket (eventos, PREMIUM), Eleven/Eleven La Plata (alquiler de maquinaria, PREMIUM), Ganadería (PRO), CellPic (e-commerce, PRO), LumiTrack (utilities, PRO), Alquileres/Roaming/Las Latas (inmuebles, PRO), RecoTrack (residuos, PRO), VirtualWallet (finanzas, PRO), SaldoClaro (finanzas simples, STARTER). Se corrigieron varios errores de clasificación de plan que cometió el agente (aplicó mal los rangos de tablas en TicketMarket, Vino y Se Fue, Eleven, Alquileres, Las Latas, RecoTrack, VirtualWallet). Dos excepciones de negocio confirmadas por el cliente: Laboratorios/consultorios médicos cotiza en SCALE (no en PRO que le tocaría por las tablas actuales de LabIPAC, porque ese build está incompleto y la oferta completa apunta a un sistema mayor); Landing page/sitio sin gestión de datos cotiza en STARTER. Inmobiliarias (venta/corretaje, Century 21) queda sin sistema de referencia real — se trata como "a medida".
- Motivo: cliente pidió reemplazar los nombres de marca inventados por las industrias reales de los sistemas ya resueltos en el repositorio, para que el bot cotice sobre precedente real en vez de sobre un catálogo ficticio.
- Impacto en capas: N/A. Actualiza la tabla de segmentación del módulo N4 (calculador de presupuesto) y N3 (motor de calificación).
- Riesgos/supuestos: LabIPAC (11 tablas reales) y RecoTrack (8 tablas reales, no 15 como decía la documentación previa del proyecto) muestran discrepancias entre lo documentado en `docs/<proyecto>/` y el código real — se priorizó el conteo real del código. "Eleven" confirmado por el cliente como alquiler de maquinaria (no reservas deportivas, que era la hipótesis inicial sin confirmar).

### 2026-05-28 - implementador
- Etapa: Modulo WhatsApp Bot outbound
- Cambio: nuevo proyecto `Olvidata.WhatsApp` (.NET) con bot de contacto directo. Servicios: `WhatsAppClient`, `MessagingService`, `OutboundCampaignService`, `TemplateCreationService`, `CatalogService`, `ExcelTrackerService`, `GoogleMapsService`. CLI con comandos: setup-profile, setup-templates, setup-catalog, check-templates, search-maps, test-send, run, stats, load-prospects, mark. Estado de campana persistido en `outbound_state.json`. Prospectos desde `contactos.xlsx`. Playbook de contacto directo documentado en `playbook_contacto_directo.md`.
- Motivo: automatizar campana outbound de WhatsApp para captura de PYMEs (La Plata → AMBA). Complementa campanas Meta Ads activas en Instagram.
- Impacto en capas: N/A (proyecto standalone .NET Console).
- Riesgos/supuestos: credenciales en variables de entorno (`META_ACCESS_TOKEN`, `META_WHATSAPP_NUMBER_ID`, `META_WHATSAPP_ACCOUNT_ID`, `META_BUSINESS_ID`). Aprobacion de templates en Meta requerida antes de ejecutar campana real.

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
