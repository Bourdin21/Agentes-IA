# Memoria - Analista funcional

## Proyecto: century-21
## Ultima actualizacion: 2026-07-02

## Definiciones vigentes

### Descripcion del proyecto
Plataforma SaaS multi-agencia inmobiliaria (piloto: Century 21 La Plata, primer cliente y primer tenant) con tres ejes:
1. CRM + Chatbot WhatsApp para filtrado y seguimiento de consultas de clientes
2. Agregador de portales inmobiliarios con cache periodico y busqueda unificada
3. Tenancy multi-agencia: el sistema se disena desde el analisis para ser revendido a otras inmobiliarias como producto, no solo como desarrollo a medida para Century 21 La Plata

**Pivot de modelo de negocio (2026-07-02):** el cliente quiere evaluar revender el sistema a otras agencias inmobiliarias. Esto cambia el analisis de "sistema a medida de un cliente" a "producto SaaS multi-tenant" y agrega una capa de decisiones de negocio y de aislamiento de datos que no formaban parte del alcance original.

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

**Modulo 3 — Plataforma multi-agencia (tenancy)**
- Alta de agencias (tenants) por parte de un rol SuperAdmin a nivel plataforma (no visible para las agencias)
- Cada agencia contrata un plan (Basico / Pro / Enterprise) que limita cantidad de asesores/usuarios habilitados
- Cada agencia puede tener uno o mas grupos internos (modelados como sucursales/equipos), cada grupo con sus propios asesores; el Gerente de la agencia ve todos los grupos, el asesor solo ve su grupo
- Aislamiento de datos por AgenciaId (tenant compartido, no BD separada) — toda entidad de negocio (clientes, consultas, propiedades propias, preferencias) queda scoped a su agencia
- Cache de portales externos (ZonaProp/ArgenProp/MercadoLibre) es GLOBAL, compartido entre todas las agencias — no se re-scrapea por tenant, cada agencia solo filtra sobre el mismo dato de mercado
- Catalogo propio pasa a tener CRUD dentro del sistema (alta/edicion/fotos/baja de propiedades por agencia) — necesario para que agencias sin sistema externo puedan operar; Century 21 La Plata usa ademas su conexion externa de solo lectura como fuente adicional
- Panel SuperAdmin: alta/baja/suspension de agencias, cambio de plan, metricas globales de uso (consultas gestionadas, consumo Apify/WhatsApp por tenant)
- Onboarding de agencia nueva es asistido manualmente por Olvidata (no self-service en esta fase), dado que cada agencia debe verificar su propio numero de WhatsApp Business en Meta Business Manager (proceso de 1-3 semanas)

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
- Catalogo propio: CRUD interno por agencia + opcion de conexion de solo lectura a BD externa (caso Century 21 La Plata, no sincronizacion bidireccional)
- Cache de portales: diario automatico + boton de forzar actualizacion en tiempo real, GLOBAL para toda la plataforma (no por agencia)
- Alertas de fechas clave: WhatsApp automatico (requiere plantillas Meta aprobadas, por agencia)
- Roles: SuperAdmin (plataforma) + Gerente (agencia, todo + asignacion + metricas) + Asesor (su grupo/sus consultas)
- Toda entidad de negocio queda scoped por AgenciaId; ninguna consulta debe cruzar datos entre agencias
- Plan contratado limita cantidad de asesores/usuarios activos por agencia

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

**Multi-agencia:**
- CA-11: Un usuario autenticado en la Agencia A nunca puede ver clientes, consultas o propiedades propias de la Agencia B
- CA-12: El SuperAdmin puede dar de alta una nueva agencia, asignarle un plan y activar su acceso; la agencia nace sin usuarios asesores (los crea luego el Gerente de esa agencia)
- CA-13: Si una agencia alcanza el limite de asesores de su plan, el alta de un nuevo asesor se bloquea con mensaje de upgrade de plan
- CA-14: Un asesor asignado a un grupo (sucursal) solo ve las consultas de su grupo; el Gerente de la agencia ve todos los grupos
- CA-15: El cache de portales externos es identico para todas las agencias en el mismo momento (mismo timestamp de ultima actualizacion global)
- CA-16: Una agencia puede cargar, editar y dar de baja sus propias propiedades desde el CRUD de catalogo propio
- CA-17: El SuperAdmin puede suspender una agencia (por falta de pago); al suspenderla, los usuarios de esa agencia pierden acceso pero los datos se conservan

### Permisos y roles
- Rol `SuperAdmin`: nivel plataforma, alta/baja/suspension de agencias, gestion de planes, metricas globales — no pertenece a ninguna agencia
- Rol `Gerente`: nivel agencia, acceso a todos los grupos de su agencia, asignacion de consultas, metricas de su agencia, alta de asesores dentro del limite del plan
- Rol `Asesor`: nivel grupo, acceso a sus propias consultas asignadas dentro de su grupo y al agregador de su agencia
- Politicas: `RequireSuperAdmin` (SuperAdmin), `RequireGerencia` (Gerente de su agencia), cualquier autenticado de la agencia para funciones de asesor
- Todo dato de negocio filtrado por `AgenciaId` a nivel de query (global query filter EF Core) — **hipotesis a validar en Arquitectura**

### Supuestos y dependencias
- Century 21 La Plata tiene una BD existente de propiedades (motor a confirmar en Arquitectura) — se conecta como fuente adicional de solo lectura, no reemplaza el CRUD propio
- Cada agencia nueva gestiona su propia cuenta Meta Business y aprobacion de plantillas (prerequisito para alertas de esa agencia); Olvidata asiste el proceso pero no lo reemplaza
- El hosting del sistema soporta Playwright/Chromium si aplica (VPS o contenedor — NO hosting compartido)
- Los portales scrapeados mantienen estructura HTML estable (frágil por naturaleza)
- El cliente acepta y firma que asume responsabilidad legal del scraping a portales de competidores
- El onboarding de agencias nuevas es manual/asistido en esta fase (no hay self-service ni cobro automatico todavia) — **hipotesis a validar**: el flujo de alta exacto (quien completa el formulario, quien paga, quien verifica Meta) queda pendiente de definir en Diseno
- Los planes (Basico/Pro/Enterprise) limitan por cantidad de asesores; los valores concretos de cada tier (ej. Basico=3, Pro=10, Enterprise=ilimitado) quedan pendientes de confirmar con el cliente antes de Presupuesto

### Exclusiones confirmadas
- Bot conversacional con IA/LLM (Fase 2 futura — ver seccion "Uso de IA")
- Publicacion automatica de propiedades en portales
- App movil
- Integracion con sistemas contables o firma digital
- Sincronizacion bidireccional con BD externa de Century 21 (la conexion externa sigue siendo de solo lectura)
- Self-service de alta de agencia y cobro automatico (queda para una fase posterior; Fase 1 es onboarding manual)
- Base de datos separada o schema separado por agencia (se descarta explicitamente a favor de TenantId compartido)

### Catalogo de propiedades
El sistema SI tiene catalogo propio (CRUD por agencia: alta, edicion, fotos, baja). Cada agencia gestiona sus propiedades dentro del sistema. Century 21 La Plata, ademas del CRUD propio, mantiene su conexion externa de solo lectura a su BD existente como fuente adicional. El resto de la informacion de propiedades (mercado externo) proviene del scraping global de portales.

### Stack tecnologico definido
- ASP.NET Core MVC .NET 10 (coherente con stack Olvidata) — el pivot a multi-agencia NO requiere cambiar de framework
- EF Core 10 + MySQL para la BD del sistema, con Global Query Filter por `AgenciaId` en todas las entidades scoped a tenant
- ASP.NET Core Identity extendido con `AgenciaId` (nullable solo para SuperAdmin) y `GrupoId` para resolver el tenant/grupo del usuario autenticado en cada request
- Meta WhatsApp Cloud API (oficial) para bot y alertas — credenciales/numero configurados por agencia (tabla de configuracion por tenant, no appsettings global)
- MercadoLibre REST API oficial (publica, sin autenticacion para busquedas) — endpoint confirmado: `GET https://api.mercadolibre.com/sites/MLA/search?category=MLA1459&...`
- Apify REST API para ZonaProp y ArgenProp (maneja Cloudflare internamente) — actores ya existentes, ejecucion GLOBAL (una sola vez para toda la plataforma)
- Hangfire para jobs programados (ScrapingDiarioJob global a las 3am, AlertasFechasJob a las 9am iterando todas las agencias activas)
- Paquetes nuevos vs baseline: Hangfire.AspNetCore, Hangfire.MySql

### Uso de IA — definicion
- **Fase 1 (alcance actual): NO usa IA/LLM.** El bot es de flujo/menu estructurado y el matching de propiedades es por filtros exactos, no por lenguaje natural.
- Puntos donde IA es tecnicamente viable como evolucion futura (Fase 2+, fuera de alcance de esta etapa, solo para dimensionar el producto de cara a la reventa):
  1. Bot conversacional con LLM en reemplazo del menu fijo (mejor experiencia de cliente, mayor costo por conversacion)
  2. Lead scoring: priorizacion automatica de consultas segun probabilidad de cierre
  3. Normalizacion de publicaciones scrapeadas (titulos/descripciones ambiguos) para mejorar el matching de busqueda
  4. Valuacion asistida: sugerencia de precio segun comparables de portales + ajuste por caracteristicas
  5. Resumen automatico del historial de conversacion de un cliente para el asesor
- Estas opciones no estan presupuestadas ni diseñadas; se documentan para que el modelo de negocio pueda venderse como "roadmap con IA" sin comprometer alcance ni costo de Fase 1.

### Modelo de negocio — reventa SaaS (decisiones 2026-07-02)
- **Pricing:** suscripcion fija mensual por plan (no pass-through de costos variables, no pay-as-you-go)
- **Diferenciacion de planes:** por cantidad de asesores/usuarios activos (Basico / Pro / Enterprise) — valores concretos de cada tier pendientes de definir con el cliente
- **Onboarding:** asistido manualmente por Olvidata; no hay autoregistro ni cobro automatico en esta fase
- **Panel SuperAdmin:** si, incluido en el alcance — alta/baja/suspension de agencias, cambio de plan, metricas globales de uso y consumo (Apify/WhatsApp) por tenant
- **Costo operativo compartido:** el cache de portales es global, por lo que el costo de Apify NO escala linealmente con la cantidad de agencias (mejora el margen del modelo de reventa)
- **Costo operativo por agencia:** cada agencia asume su propio costo de conversaciones WhatsApp ante Meta (facturado aparte o incluido en el plan — a definir en Presupuesto)

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
7. Cada agencia nueva depende de su propia verificacion Meta Business (1-3 semanas) — puede frenar el onboarding comercial de nuevos clientes SaaS
8. Global query filter por AgenciaId es un control critico de seguridad: un olvido en una sola query puede filtrar datos entre agencias — requiere checklist especifico en Arquitectura y QA
9. Ampliar el alcance a CRUD de catalogo propio (antes excluido) suma modulo nuevo no contemplado en la primera estimacion — impacta Presupuesto
10. Nombre de marca "Century 21" en un producto revendible a otras agencias (posiblemente competidoras) puede requerir independizar el naming del producto SaaS del nombre del cliente piloto — a resolver antes de comercializar

## Historial de ajustes
- 2026-06-25: Discovery completado. Alcance funcional cerrado. Pendiente fase de Diseno.
- 2026-07-02: Pivot a modelo SaaS multi-agencia. Decisiones confirmadas con el cliente: aislamiento por AgenciaId compartido (no BD/schema separado), catalogo propio pasa a tener CRUD interno, cache de portales global compartido entre agencias, grupos = sucursales/equipos, pricing por suscripcion fija diferenciada por cantidad de asesores, onboarding manual asistido, panel SuperAdmin incluido. Confirmado que Fase 1 no usa IA/LLM; se documenta roadmap de IA como diferencial de venta futuro. Pendiente: iniciar Diseno funcional (etapa 2) con estas definiciones como base.
