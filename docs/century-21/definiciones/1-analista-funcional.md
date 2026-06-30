# Memoria - Analista funcional

## Proyecto: century-21
## Ultima actualizacion: 2026-06-25

## Definiciones vigentes

### Descripcion del proyecto
Sistema web para inmobiliaria Century 21 La Plata con dos ejes principales:
1. CRM + Chatbot WhatsApp para filtrado y seguimiento de consultas de clientes
2. Agregador de portales inmobiliarios con cache periodico y busqueda unificada

### Modulos definidos

**Modulo 1 — CRM + Chatbot WhatsApp**
- Recepcion de consultas entrantes y respuesta automatica con flujo de menu estructurado (sin IA en Fase 1)
- Categorizacion de consulta: comprador / alquiler / vendedor / valuacion
- Captura y persistencia de preferencias del cliente por numero de telefono (zona, tipo, precio, ambientes)
- Perfil de cliente en el sistema web con historial de conversacion y estado de consulta
- Registro de fechas clave: cumpleanos, aniversario de compra de propiedad
- Envio automatico de mensaje WhatsApp en fechas clave (plantillas Meta aprobadas)
- Panel asesor: mis consultas, estado, perfil de cliente
- Panel gerente: todas las consultas, asignacion a asesor, metricas basicas
- Maquina de estados: Nueva → Categorizada → Asignada → En gestion → Cerrada

**Modulo 2 — Agregador de portales**
- Conexion de solo lectura al catalogo propio de Century 21 La Plata (BD existente)
- Cache diario automatico de portales externos (job 1x/dia a las 3am)
- Boton de actualizacion en tiempo real (forzar scraping on-demand)
- Busqueda unificada con filtros: tipo, zona, precio, ambientes, origen
- Resultados etiquetados por fuente: Propio / ZonaProp / ArgenProp / MercadoLibre / etc.
- Soporte de valuacion: buscar comparables por zona y caracteristicas
- Aplicar preferencias guardadas de un cliente como filtros de busqueda

### Portales incluidos
| Portal | Estrategia | Estado legal |
|---|---|---|
| Catalogo propio | Conexion BD solo lectura | Sin riesgo |
| MercadoLibre | API oficial (OAuth2) | Sin riesgo |
| ZonaProp | Playwright for .NET (scraping) | Verificar ToS |
| ArgenProp | Playwright for .NET (scraping) | Verificar ToS |
| Century21.com.ar | A evaluar — cliente asume riesgo contractual | Riesgo alto |
| Remax.com.ar | Playwright for .NET (scraping) | Riesgo — cliente asume responsabilidad |

### Reglas funcionales acordadas
- Bot Fase 1: flujo/menu estructurado, sin LLM/IA conversacional
- Catalogo propio: conexion de solo lectura a su BD existente (no sincronizacion bidireccional)
- Cache de portales: diario automatico + boton de forzar actualizacion en tiempo real
- Alertas de fechas clave: WhatsApp automatico (requiere plantillas Meta aprobadas)
- Roles: Asesor (sus consultas) + Gerente (todo + asignacion + metricas)

### Criterios de aceptacion verificables

**CRM/Bot:**
- CA-01: Un mensaje entrante de WhatsApp de numero desconocido activa el flujo de menu y crea un registro de cliente
- CA-02: Al completar el flujo, las preferencias quedan guardadas en el perfil del cliente asociado al numero de telefono
- CA-03: Un asesor puede ver en su panel todas las consultas asignadas con estado actualizado
- CA-04: El gerente puede ver todas las consultas y reasignarlas entre asesores
- CA-05: En la fecha de cumpleanos del cliente el sistema envia automaticamente un mensaje WhatsApp usando plantilla aprobada
- CA-06: La maquina de estados impide pasar a "En gestion" sin pasar por "Categorizada"

**Agregador:**
- CA-07: El job diario actualiza el cache y registra timestamp de ultima actualizacion
- CA-08: El boton "Actualizar ahora" dispara el scraping en tiempo real y muestra progreso
- CA-09: La busqueda devuelve resultados de todas las fuentes activas con el origen etiquetado
- CA-10: Desde el perfil de un cliente se puede lanzar una busqueda con sus preferencias precargadas como filtros

### Permisos y roles
- Rol `Asesor`: acceso a sus propias consultas asignadas y al agregador
- Rol `Gerente`: acceso total, asignacion de consultas, metricas
- Politicas: `RequireGerencia` (Gerente), cualquier autenticado para funciones de asesor

### Supuestos y dependencias
- Century 21 La Plata tiene una BD existente de propiedades (motor a confirmar en Arquitectura)
- El cliente gestiona la cuenta Meta Business y aprobacion de plantillas (prerequisito para alertas)
- El hosting del sistema soporta Playwright/Chromium (VPS o contenedor — NO hosting compartido)
- Los portales scrapeados mantienen estructura HTML estable (frágil por naturaleza)
- El cliente acepta y firma que asume responsabilidad legal del scraping a portales de competidores

### Exclusiones confirmadas
- Bot conversacional con IA/LLM (Fase 2 futura)
- Publicacion automatica de propiedades en portales
- App movil
- Integracion con sistemas contables o firma digital
- Sincronizacion bidireccional con BD existente de Century 21

### Catalogo de propiedades
El sistema NO tiene catalogo propio. Toda la informacion de propiedades proviene exclusivamente del scraping de portales externos.

### Stack tecnologico definido
- ASP.NET Core MVC .NET 10 (coherente con stack Olvidata)
- EF Core 10 + MySQL para la BD del sistema
- Meta WhatsApp Cloud API (oficial) para bot y alertas
- MercadoLibre REST API oficial (publica, sin autenticacion para busquedas) — endpoint confirmado: `GET https://api.mercadolibre.com/sites/MLA/search?category=MLA1459&...`
- Apify REST API para ZonaProp y ArgenProp (maneja Cloudflare internamente) — actores ya existentes
- Hangfire para jobs programados (ScrapingDiarioJob a las 3am, AlertasFechasJob a las 9am)
- Paquetes nuevos vs baseline: Hangfire.AspNetCore, Hangfire.MySql

### Arquitectura de scraping — investigacion confirmada (2026-06-25)

#### MercadoLibre — API oficial
- Endpoint publico: `GET https://api.mercadolibre.com/sites/MLA/search?category=MLA1459`
- No requiere autenticacion para busquedas de lectura
- Registro gratuito en developers.mercadolibre.com.ar (10 min)
- Parametros: zona (lat/lon), precio, tipo, ambientes, operacion (venta/alquiler), limit/offset
- Devuelve JSON estructurado: titulo, precio, moneda, superficie, ambientes, zona, coordenadas, fotos, URL
- Paginacion offset-based, 48 resultados por pagina
- Implementacion: HttpClient directo en .NET — sin servicios intermedios

#### ZonaProp y ArgenProp — via Apify (servicio de scraping)
- Ambos portales tienen proteccion Cloudflare que bloquea IPs de datacenter
- HttpClient directo desde servidor devuelve 403 — NO FUNCIONA en produccion
- Solucion: Apify (apify.com) tiene actores especificos ya construidos y mantenidos para ambos portales
  - ZonaProp actor: `majere11/zonaprop-scraper`
  - ArgenProp actor: `ecomscrape/argenprop-property-search-scraper`
- El codigo .NET llama a la REST API de Apify con HttpClient — igual de simple que MercadoLibre
- Apify maneja proxies residenciales, Cloudflare bypass y cambios de estructura internamente
- Costo estimado: plan gratuito ($5 credito/mes incluido) puede alcanzar para bajo volumen; plan basico ~$10-15/mes
- Alternativa: Piloterr (piloterr.com) tiene endpoint especifico para ZonaProp con free trial

#### Remax.com.ar y Century21.com.ar
- Tecnicamente scrapeables via Apify (actores genericos)
- Bloqueante: riesgo legal, no tecnico — cliente debe asumir responsabilidad antes de incluirlos

#### Patron de implementacion (todos los portales)
```
IPortalAdapter
├── MercadoLibreAdapter   → HttpClient → api.mercadolibre.com (directo)
├── ZonaPropAdapter       → HttpClient → api.apify.com (servicio externo)
└── ArgenPropAdapter      → HttpClient → api.apify.com (servicio externo)

ScrapingOrchestratorService
├── Task.WhenAll(adapters) — llamadas en paralelo
├── Normaliza a PropiedadCacheDto unificado
└── Persiste en tabla PropiedadesCache (MySQL)
```

### Riesgos identificados
1. Verificacion Meta Business puede tomar 1-3 semanas — iniciar antes del desarrollo
2. Portales pueden cambiar estructura interna — mitigado porque Apify absorbe ese mantenimiento
3. Costo mensual de Apify (~$10-15/mes) — asumir como costo operativo del sistema
4. Cloudflare puede escalar su proteccion — si Apify falla, alternativa es Piloterr o Bright Data
5. Costo por conversacion iniciada por empresa en WhatsApp — revisar pricing Meta
6. Century21.com.ar: riesgo contractual con la franquicia — cliente debe confirmar

## Historial de ajustes
- 2026-06-25: Discovery completado. Alcance funcional cerrado. Pendiente fase de Diseno.
