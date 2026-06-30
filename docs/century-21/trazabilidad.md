# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-06-25 - bootstrap
- Etapa: Discovery
- Cambio: Inicialización del proyecto en el sistema de agentes
- Motivo: Nuevo proyecto Century 21 incorporado al flujo Agentes-IA
- Impacto en capas: —
- Riesgos/supuestos: Stack pendiente de definir en fase de análisis

### 2026-06-25 - analista-funcional
- Etapa: Discovery + Análisis
- Cambio: Alcance funcional cerrado. Dos ejes: CRM+Chatbot WhatsApp y Agregador de portales.
- Motivo: Relevamiento completo con cliente — 5 decisiones de diseño confirmadas
- Impacto en capas: Presentación (CRM web, búsqueda unificada), Negocio (máquina de estados consulta, jobs de alertas y scraping), Datos (cache portales en MySQL)
- Riesgos/supuestos: Meta Business verification pendiente, hosting debe soportar jobs Hangfire

### 2026-06-26 - analista-funcional
- Etapa: Análisis — investigación técnica de scraping
- Cambio: Estrategia de scraping definida y confirmada factible. Sin catálogo propio — todo desde portales.
- Motivo: Investigación exhaustiva de APIs y protecciones de cada portal
- Decisiones:
  - MercadoLibre: API oficial pública confirmada (GET /sites/MLA/search?category=MLA1459) — HttpClient directo, gratis
  - ZonaProp y ArgenProp: Cloudflare bloquea HttpClient directo desde servidor. Solución: Apify REST API con actores específicos ya existentes. Costo ~$10-15/mes.
  - Playwright (opción C) descartado definitivamente
  - Remax y Century21.com.ar: técnicamente viables vía Apify, pendiente confirmación legal del cliente
- Impacto en capas: Infraestructura (3 adapters HttpClient), Datos (tabla PropiedadesCache)
- Riesgos: Costo operativo Apify, cambios de Cloudflare absorbidos por Apify
