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

### 2026-07-02 - analista-funcional
- Etapa: Analisis — pivot a modelo de negocio SaaS multi-agencia
- Cambio: El sistema se redefine como plataforma multi-tenant revendible a otras inmobiliarias (no solo desarrollo a medida de Century 21 La Plata). Se agrega Modulo 3 (tenancy) y modelo de negocio de reventa.
- Motivo: Pedido explicito del cliente de evaluar reventa del sistema a otras agencias, con estructura multi-agencia y multi-grupo de usuarios por agencia
- Decisiones (confirmadas via preguntas guiadas al cliente):
  - Aislamiento de datos: TenantId compartido (`AgenciaId`) en una sola base MySQL, con Global Query Filter de EF Core — se descarta BD/schema separado por agencia
  - Catalogo propio: pasa de "excluido" a CRUD interno por agencia (necesario para vender a agencias sin sistema propio); Century21 La Plata mantiene ademas su conexion externa de solo lectura
  - Cache de portales externos (ZonaProp/ArgenProp/MercadoLibre): GLOBAL y compartido entre todas las agencias, no se re-scrapea por tenant
  - "Grupos de usuarios": modelados como sucursales/equipos dentro de la agencia; Gerente ve todos los grupos, Asesor ve solo el suyo
  - Pricing: suscripcion fija mensual por plan (Basico/Pro/Enterprise), diferenciados por cantidad de asesores
  - Onboarding de agencias nuevas: manual/asistido por Olvidata (no self-service en esta fase), condicionado por verificacion Meta Business por agencia (1-3 semanas)
  - Se agrega rol `SuperAdmin` con panel propio: alta/baja/suspension de agencias, cambio de plan, metricas globales de consumo
  - Confirmado: Fase 1 no usa IA/LLM (bot de menu estructurado). Se documenta roadmap de IA (bot conversacional, lead scoring, normalizacion de scraping, valuacion asistida, resumenes) como diferencial de venta futuro, fuera de alcance y presupuesto actual
- Impacto en capas: Datos (nuevas entidades Agencia/Grupo/Plan/Suscripcion, AgenciaId en entidades existentes), Negocio (scoping por tenant, limites de plan, panel SuperAdmin), Presentacion (nuevo panel SuperAdmin, CRUD de catalogo propio)
- Riesgos/supuestos: riesgo de fuga de datos entre tenants si falta el filtro por AgenciaId en alguna query (control critico para Arquitectura/QA); ampliacion de alcance respecto al presupuesto no iniciado; nombre de marca "Century 21" en un producto revendible a terceros a resolver antes de comercializar
- Estado: Analisis (etapa 1) actualizado y vigente. Pendiente iniciar Diseno funcional (etapa 2) con estas definiciones como base.

### 2026-07-02 - disenador-funcional
- Etapa: Diseño funcional (etapa 2)
- Cambio: Diseño completo de 14 pantallas en 3 roles (SuperAdmin/Gerente/Asesor), 6 ViewModels, 2 máquinas de estados (Consulta ratificada + Agencia nueva: Activa/Suspendida)
- Motivo: Continuar el flujo tras el pivot SaaS multi-agencia aprobado en Análisis
- Impacto en capas: Presentacion (14 pantallas nuevas, 3 areas de navegacion por rol), Negocio (maquina de estados Agencia, reglas de limite de plan, ruteo de Consulta a Grupo), Datos (entidades funcionales Agencia/Plan/Grupo/PropiedadPropia identificadas, detalle tecnico pendiente de Arquitectura)
- Riesgos/supuestos: asesor mono-grupo asumido (a validar), modo de ruteo automatico vs manual de Consulta a Grupo pendiente de confirmar con cliente, almacenamiento de fotos de catalogo propio condicionado por limitaciones del hosting (a resolver en Arquitectura)
- Estado: Diseño (etapa 2) cerrado y vigente. Pendiente iniciar Arquitectura (etapa 3).

### 2026-07-02 - arquitecto-mvc
- Etapa: Arquitectura (etapa 3)
- Cambio: 5 entidades nuevas (Agencia, Plan, Grupo, PropiedadPropia, PropiedadFoto), 4 enums, query filter global por AgenciaId en AppDbContext via ITenantContext, 4 migraciones EF planificadas, modelo de permisos de 3 roles (SuperAdmin/Gerente/Asesor)
- Motivo: Continuar el flujo tras Diseño funcional aprobado
- Decisiones clave: aislamiento por AgenciaId compartido confirmado tecnicamente viable; almacenamiento de fotos en filesystem local (riesgo de cuota de disco documentado); cifrado de credenciales WhatsApp por agencia con clave en configuracion del servidor
- Impacto en capas: Domain (5 entidades + 4 enums), Application (ITenantContext + interfaces nuevas), Infrastructure (query filter global, seed de roles y planes, servicio de cifrado), Web (3 areas de navegacion por rol, 6 controllers nuevos)
- Riesgos: limite real de conexiones concurrentes MySQL del hosting SmarterASP.NET no confirmado (marketing dice "ilimitado", atipico en hosting compartido) — accion pendiente con soporte del proveedor; limite de 20 BD del plan Premium ratifica el modelo de tenant compartido elegido en Analisis
- Estado: Arquitectura (etapa 3) cerrada y vigente. Gate abierto hacia Presupuesto (etapa 4).

### 2026-07-02 - presupuestador
- Etapa: Presupuesto (etapa 4)
- Cambio: Presupuesto PERT completo con anclaje historico (decorhogar, ShowroomGriffin, Energy Nutrition, labipac). 11 modulos, 64.0h M base, 77.94h con contingencia, $1.076 desarrollo + $100 tokens IA = $1.176 total (Etapa 1 $764 / Etapa 2 $412)
- Motivo: Continuar el flujo tras Arquitectura aprobada; pedido explicito del cliente de tambien armar plan de venta SaaS Basico/Pro/Enterprise
- Decisiones: mantenimiento anual Plan PREMIUM $400/ano (~17 tablas); plan de venta propuesto (Basico USD 49/mes hasta 3 asesores, Pro USD 129/mes hasta 10, Enterprise USD 299/mes + USD 15/asesor extra) marcado como hipotesis comercial sin validacion de mercado; checkpoint tecnico recomendado a los 15-20 agencias pagas para confirmar limite real de conexiones MySQL del hosting antes de escalar el plan Enterprise
- Impacto en capas: sin cambio de capas (documento de negocio), referencia directa a riesgos tecnicos ya documentados en Arquitectura (RP1 limite de conexiones)
- Riesgos: precios de planes sin validacion de mercado externo; M3 (tenancy transversal) sin cierre real de referencia en el estudio, contingencia Alta 25% ya aplicada
- Estado: Presupuesto (etapa 4) cerrado. BORRADOR — pendiente aprobacion del cliente. Gate duro: no iniciar Implementacion (etapa 5) hasta aprobacion explicita del presupuesto por el cliente.

### 2026-07-02 - arquitecto-mvc + presupuestador
- Etapa: Ajuste sobre Arquitectura (etapa 3) y Presupuesto (etapa 4) ya cerradas
- Cambio: El cliente confirmo el limite real de conexiones del hosting SmarterASP.NET: 10 conexiones simultaneas por usuario MySQL, con disponibilidad de crear hasta 5 usuarios MySQL (techo teorico 50 conexiones en pools separados). Reemplaza el riesgo RP1 "no confirmado" por una decision de arquitectura concreta: pool Web dedicado (usuario #1, 8 conexiones), pool Hangfire separado (usuario #2), Staging (usuario #3), 2 usuarios de reserva
- Motivo: Dato tecnico real aportado por el cliente, resuelve un riesgo abierto documentado en Arquitectura y Presupuesto
- Tambien se agrego ejemplo de rentabilidad para 3 agencias en Plan Basico en el presupuesto (seccion 17): ganancia recurrente ~USD 126.55/mes (~86% margen) desde el mes 2, bajo el supuesto de que Olvidata opera la infraestructura SaaS de forma propia (no Century21 La Plata) — supuesto pendiente de confirmar explicitamente con el cliente antes de comercializar
- Impacto en capas: Infrastructure (connection strings segregadas por usuario MySQL), sin impacto en Domain/Application/Web
- Confirmado por el usuario (2026-07-02): Olvidata Soft es duena y operadora de la infraestructura SaaS (no Century21 La Plata). Habilita vender a agencias competidoras sin conflicto de titularidad. Documento de presupuesto actualizado para reflejar esto como decision confirmada, no como supuesto pendiente.
- Estado: Arquitectura y Presupuesto actualizados y vigentes con esta informacion. No cambia el gate: Presupuesto sigue en BORRADOR pendiente de aprobacion del cliente.

### 2026-07-02 - presupuestador (politica de cobro)
- Etapa: Ajuste sobre Presupuesto (etapa 4) ya cerrado
- Cambio: Se agrega politica de cobro con prepago anual (10 meses = 12, "2 meses gratis") como mecanismo para que los primeros clientes SaaS cubran el costo de desarrollo (USD 1.176) de entrada, en vez de diluirlo en la facturacion mensual. Facturacion mensual sigue disponible sin el descuento.
- Motivo: Pedido explicito del cliente ("quiero que entre las tres agencias me cubran el costo de desarrollo de entrada")
- Numeros: 3 agencias Basico en prepago anual + setup = USD 1.920 cobrados al firmar, cubre el costo de desarrollo (USD 1.176) con USD 744 de excedente. Con solo 2 agencias en prepago anual (sin contar setup) ya casi se cubre el costo.
- Impacto en capas: ninguno (decision comercial, no tecnica)
- Estado: Presupuesto (etapa 4) actualizado. Sigue en BORRADOR pendiente de aprobacion del cliente.

### 2026-07-02 - presupuestador (investigacion de mercado)
- Etapa: Ajuste sobre Presupuesto (etapa 4) — research de competencia regional
- Cambio: Research de CRMs inmobiliarios SaaS en Argentina/LatAm (KiteProp, 2clicsApp, Tokko Broker, Wasi, Xintel, ALTOR, Bitrix24, Follow Up Boss como referencia EEUU). Precios de century-21 (USD 49/129/299) confirmados en banda media-alta pero dentro de rango de mercado (rango verificado: USD 10-190/mes segun cantidad de usuarios)
- Motivo: Pedido explicito del cliente de comparar precios/funcionalidades contra el mercado regional para un sistema competitivo y escalable
- Hallazgo clave: ningun competidor verificado combina multi-agencia jerarquica real + agregador de portales + bot WhatsApp automatizado con alertas de fechas clave en un solo producto. KiteProp es el mas cercano (30+ portales, multisucursal, WhatsApp "nativo" sin confirmar si es bot automatizado). El argumento de venta de century-21 es "todo incluido", no "mas barato"
- Advertencias de calidad de dato: Wasi, Xintel y Tokko Broker Argentina no publican precio en planes grandes (piden demo/cotizacion). Conversion ARS-USD con dolar blue $1.505 (01/07/2026) — variaria con otra cotizacion. Plan Enterprise de century-21 sin comparable de mercado verificado
- Impacto en capas: ninguno (decision comercial)
- Estado: Presupuesto (etapa 4) actualizado con seccion "Investigacion de mercado" en el plan de venta SaaS. Precios de lista sin cambios (USD 49/129/299) — quedan pendientes de validar el diferencial de bot automatizado y el precio de Enterprise directamente con agencias grandes.

### 2026-07-02 - presupuestador (segunda pasada de research, cross-check)
- Etapa: Ajuste sobre Presupuesto (etapa 4) — segunda corrida de investigacion de mercado, independiente de la primera
- Cambio: Confirma conclusion general (century-21 en banda media-alta, no outlier) pero corrige dos puntos: (1) Xintel SI tiene automatizacion real de WhatsApp ("Chat Multiagente" con derivacion automatica) — la primera pasada lo marco como no confirmado; (2) las afirmaciones de KiteProp sobre si mismo (multisucursal, WhatsApp nativo, 30+ portales) vienen mayormente de contenido autopromocional propio (se autoevalua 9.4/10), recomendado verificar independientemente antes de asumirlo como el rival mas fuerte
- Motivo: Notificacion de tarea en background que corrio investigacion adicional sobre el mismo tema
- Nuevo dato: competidor adicional detectado, Solution Malls (+20 anios, +80 clientes LatAm), orientado a holdings/ERP grandes, precio no publico. Ambas pasadas coinciden en que Tokko Broker Argentina bloquea precios publicos (HTTP 403) y que Wasi/Xintel esconden precio en planes grandes
- Impacto en capas: ninguno (decision comercial)
- Estado: Presupuesto (etapa 4) actualizado con cross-check de la segunda pasada. Sin cambio de precios de lista.

### 2026-07-02 - presupuestador (documento cliente)
- Etapa: Entrega — documento de presupuesto para Century 21 La Plata
- Cambio: Se crea `docs/century-21/presupuesto-cliente.md`, version comercial sin jerga tecnica, siguiendo el formato de `decorhogar/presupuesto-cliente.md`
- Decision de precio: por pedido del cliente de no mencionar el esquema multiusuario/multi-agencia, se excluyo del presupuesto facturado a Century21 el modulo "Plataforma SuperAdmin (Agencias, Planes, metricas)" (USD 109 del presupuesto interno) porque no tiene valor funcional para Century21 — lo absorbe Olvidata como inversion propia en el producto revendible. Se mantuvo el modulo de tenancy transversal (USD 76) pero relabeled como "Seguridad y control de accesos", porque SI entrega valor real a Century21 (permisos por rol, trazabilidad) independientemente del motivo multi-tenant de fondo
- Total facturado a Century21: USD 1.067 (vs. USD 1.176 del presupuesto interno completo) — diferencia de USD 109 (mas los USD 100 tokens IA que se mantienen). Esta es una decision de precio tomada con criterio propio, senializada explicitamente al usuario para su confirmacion/ajuste
- Se agrego nota de "Qué no está incluido" para la conexion de solo lectura a la BD externa de propiedades de Century21 (no tenia item de presupuesto propio en el WBS interno) y para el costo operativo de Apify (~USD 10-15/mes), ambos a coordinar aparte
- Estado: documento cliente listo para enviar. Presupuesto interno (`4-presupuestador.md`) permanece como memoria completa, no se comparte con el cliente.

### 2026-07-02 - disenador-funcional + arquitecto-mvc (cambio de modelo de roles)
- Etapa: Ajuste sobre Diseño (etapa 2) y Arquitectura (etapa 3) ya cerradas — gatillo de reestimacion (cambio de reglas de negocio y permisos)
- Cambio: Se elimina el rol Gerente. El sistema pasa a 2 roles: SuperAdmin (gestion de usuarios/grupos/agencias/planes, uso interno Olvidata) y Asesor (unico rol de negocio, operacion peer-to-peer dentro de su grupo, sin jerarquia intermedia)
- Motivo: Pedido explicito del cliente — "el rol de Gerente sera reemplazado por un estado grupal de los asesores". Confirmado via preguntas guiadas: (1) el plan se contrata por Grupo, no por Agencia — cada grupo tiene su propio plan y cupo; (2) gestion de usuarios (alta/baja de asesores y grupos) la hace SuperAdmin, los asesores solo editan su propio perfil y se reasignan consultas entre si; (3) consultas nuevas van a una bandeja compartida del grupo con self-assign, no asignacion manual
- Decisiones de arquitectura derivadas: PlanId y configuracion de WhatsApp se mueven de Agencia a Grupo; filtro de tenant principal (Global Query Filter EF Core) pasa de AgenciaId a GrupoId; se agrega RowVersion a Consulta para concurrencia optimista (evitar doble self-assign simultaneo); webhook de WhatsApp resuelve GrupoId directamente por numero de destino (1 numero = 1 grupo, ya no ambiguo); Agencia pasa a ser contenedor liviano sin plan ni estado propio
- Nuevas pantallas: A-01 Mi perfil (stats personales) y A-02 Perfil de grupo (stats grupales), explicitamente pedidas por el cliente
- Impacto en capas: Domain (Grupo ampliado con PlanId/Estado/WhatsApp, Consulta con RowVersion, Agencia simplificada), Application (ITenantContext ahora resuelve GrupoId no AgenciaId), Infrastructure (query filter global movido a GrupoId, manejo de DbUpdateConcurrencyException en self-assign), Web (2 areas de navegacion en vez de 3, se elimina toda autorizacion condicionada a Gerente)
- Riesgos nuevos: sin control jerarquico intermedio (decision de negocio confirmada, no defecto); gestion compartida de catalogo/clientes sin dueño unico marcada como hipotesis a validar antes de Implementacion; riesgo de consulta "flotando" sin tomar en la bandeja, sin alerta automatica (fuera de alcance actual)
- Estado: Diseño y Arquitectura actualizados y cerrados nuevamente con el modelo de 2 roles. Presupuesto (etapa 4) requiere reestimacion de los modulos afectados (M1 SuperAdmin, M2 Grupos/Asesores, M5 Consultas) antes de poder reconfirmarse con el cliente.

### 2026-07-02 - presupuestador (reestimacion por cambio de roles)
- Etapa: Presupuesto (etapa 4) — reestimacion completa por gatillo de cambio de reglas de negocio y permisos
- Cambio: 13 modulos (se quita M8 standalone Config. WhatsApp, absorbido en M2; se agregan M12 Mi perfil y M13 Perfil de grupo, pantallas nuevas pedidas por el cliente). Total interno 69.0h M / USD 1.259 (incluye Tokens IA). Total facturado a Century21: USD 1.041 (excluye M1 Plataforma SuperAdmin + M2 Gestion de Grupos/Asesores, USD 218 combinados, que ahora son 100% gestion de Olvidata sin pantalla visible para el cliente)
- Motivo: Cascada del cambio de modelo de roles (ver entrada anterior de disenador-funcional + arquitecto-mvc)
- Detalle de ajustes por modulo: M2 crece (6.5h, absorbe config. WhatsApp), M3 crece (+1h por concurrencia RowVersion), M5 crece (+0.5h por patron de bandeja compartida), M6 baja (-0.5h, resolucion de grupo mas simple que la ambiguedad agencia-grupo anterior). Sanity check contra decorhogar/ShowroomGriffin/EN sigue en rango sin ajuste adicional
- Se actualiza plan de venta SaaS (seccion 17): unidad de contratacion pasa de Agencia a Grupo — una franquicia multi-sucursal ahora genera un plan pago por sucursal, mejora la economia de reventa sin cambiar precios de lista
- Se actualiza `presupuesto-cliente.md` en paralelo: se quita la fila "Usuarios, equipos y accesos" (ya no facturable, es gestion interna de Olvidata), se agregan "Mi perfil" y "Perfil de equipo", rol Gerente eliminado de la tabla de roles, nuevo total USD 1.041 (antes USD 1.067)
- Estado: Presupuesto (etapa 4) reestimado y cerrado. Sigue en BORRADOR pendiente de aprobacion del cliente.

### 2026-07-02 - presupuestador (ajustes comerciales finales)
- Etapa: Ajuste sobre Presupuesto (etapa 4) ya cerrado
- Cambios pedidos por el cliente:
  1. La cobertura "de entrada" del costo de desarrollo se reconfirma con **3 grupos** (no agencias, terminologia actualizada) en Plan Basico con prepago anual. Recalculado contra el nuevo costo de desarrollo interno (USD 1.259, post-reestimacion de roles): 3 grupos x ($490 prepago anual + $150 setup) = USD 1.920 cobrados al firmar, cubre el costo con USD 661 de excedente (antes $744 contra el target anterior de $1.176)
  2. Confirmado sin cambios: costo de mantenimiento anual USD 400/año (Plan PREMIUM)
  3. Se eliminan las "2 rondas de ajuste al año" del alcance del plan de mantenimiento — motivo explicito del cliente: la gestion del sistema es pura y exclusivamente de Olvidata (no hay autoadministracion del cliente que requiera "ajustes"). El precio del plan se mantiene en USD 400/año sin cambios pese a la reduccion de alcance del beneficio
- Impacto en capas: ninguno (decisiones comerciales)
- Estado: Presupuesto (etapa 4) y `presupuesto-cliente.md` actualizados con estos tres ajustes. Sigue en BORRADOR pendiente de aprobacion final del cliente.

### 2026-07-02 - presupuestador (presupuesto de grupo SaaS para Century21)
- Etapa: Entrega — presupuesto de suscripcion SaaS para el grupo de 2 asesores de Century21 La Plata
- Cambio: Se crea `docs/century-21/presupuesto-grupo-2-asesores.md` — Plan Basico, USD 150 setup + USD 490/año, total primer año USD 640, renovacion USD 490/año
- Motivo: Pedido explicito del cliente de presupuestar el grupo de 2 asesores de Century21 bajo el modelo de suscripcion SaaS (no como desarrollo a medida), recordando que la estrategia es fondear el costo de desarrollo (USD 1.259) con 2 o 3 grupos de este tipo
- Tension identificada y senializada al usuario (no resuelta unilateralmente): este presupuesto de grupo SaaS (USD 640 primer año, USD 490/año en adelante) es un modelo comercial distinto y con montos muy diferentes al de `presupuesto-cliente.md` (desarrollo a medida, USD 1.041 unico pago). Ambos documentos conviven en el proyecto pero representan dos estrategias comerciales distintas para el mismo cliente piloto — pendiente que el usuario confirme cual es el modelo definitivo
- Calculo de cobertura: 2 grupos cubren el costo de desarrollo con apenas USD 21 de excedente (margen muy ajustado, no recomendado); 3 grupos cubren con USD 661 de excedente (recomendado)
- Estado: documento listo. Pendiente definicion del usuario sobre como conviven ambos esquemas de facturacion para Century21.

### 2026-07-02 - presupuestador (unificacion del modelo de facturacion)
- Etapa: Resolucion de la tension identificada en la entrada anterior
- Cambio: El usuario define que `presupuesto-cliente.md` ES el presupuesto final para cualquier grupo de asesores que contrate la suscripcion (Basico/Pro/Enterprise), incluido el propio grupo de Century21. Se elimina `presupuesto-grupo-2-asesores.md` (redundante). Se reescribe `presupuesto-cliente.md` de un formato de proyecto BUILD por etapas (USD 1.041, WBS con modulos) a una hoja de precios de suscripcion SaaS: tabla de 3 planes (Basico/Pro/Enterprise) con configuracion inicial + plan anual, feature set unico (todos los planes tienen las mismas funciones, la diferencia es el limite de asesores)
- Motivo: Pedido explicito del cliente — presupuesto-cliente.md pasa a ser el documento unico de venta de suscripcion
- Impacto en documentos: se actualiza `4-presupuestador.md` secciones 9 y 14 para reflejar que ya no se factura por proyecto/etapas — el costo interno de USD 1.259 (construir la plataforma una vez) se recupera con las suscripciones de los grupos, no con una factura de desarrollo a Century21. Condiciones comerciales del documento cliente cambian de "50/50 por etapa" a "100% al confirmar el alta (setup + primer año)"
- Se elimina la seccion "Mantenimiento anual USD 400/año Plan PREMIUM" del documento cliente porque ya no aplica como linea separada — el soporte/mantenimiento queda incluido dentro del precio del plan anual de suscripcion
- Estado: `presupuesto-cliente.md` es ahora el unico documento de venta vigente para grupos de asesores. `4-presupuestador.md` mantiene el detalle interno de costos (WBS, PERT) y el plan de venta SaaS (seccion 17) como fuente de la logica de precios.

### 2026-07-02 - disenador-funcional (detalle del flujo del bot)
- Etapa: Ajuste sobre Diseño (etapa 2) — profundizacion de un apartado a pedido del cliente
- Cambio: Se detalla el flujo conversacional del bot de WhatsApp (2-disenador-funcional.md, nueva subseccion 2.1): menu de bienvenida de 4 opciones, preguntas de calificacion especificas por categoria (Comprador/Alquiler/Vendedor/Valuacion), manejo de cliente conocido vs desconocido, manejo de respuesta fuera de menu. Se replica version en lenguaje de cliente en `presupuesto-cliente.md`
- Motivo: Pedido explicito de profundizar el apartado del chatbot en el presupuesto cliente
- Hipotesis marcadas explicitamente (no relevadas en Analisis original): preguntas exactas por categoria son propuesta del equipo de diseño basada en flujo estandar de calificacion de leads inmobiliarios; posibles campos nuevos si el cliente confirma (DocumentacionEnRegla para Vendedor, Superficie para Valuacion)
- Impacto en capas: Presentacion/Negocio (logica de flujo del bot mas detallada, sin cambio de arquitectura), posible impacto menor en Datos si se confirman campos nuevos (no dispara reestimacion salvo logica condicional compleja)
- Estado: Diseño actualizado con el detalle. Pendiente confirmacion del cliente sobre las preguntas exactas antes de Implementacion.

### 2026-07-02 - presupuestador (profundizacion buscador + comparacion Tokko + curva de precio por asesor)
- Etapa: Ajuste sobre `presupuesto-cliente.md` y `4-presupuestador.md` seccion 17
- Cambios:
  1. Se profundizo el apartado del buscador unificado en `presupuesto-cliente.md`: tabla de fuentes (catalogo propio, MercadoLibre directo, ZonaProp/ArgenProp via servicio externo anti-bots), aclaracion honesta de que la busqueda es instantanea sobre un cache actualizado diario + boton manual (no scraping en vivo por busqueda), filtros disponibles, caso de uso tipico
  2. Se obtuvo precio real de Tokko Broker via fuente de terceros (comparasoftware.com.ar, el sitio oficial sigue bloqueando con HTTP 403): Plan Duo USD 69/mes (~2 usuarios), Plan Empresa USD 110/mes, Plan Empresa superior USD 147/mes. Reemplaza el proxy de precios de Mexico usado hasta ahora
  3. Se rediseño la curva de precio por asesor a pedido del cliente ("el crecimiento del precio por usuario deberia ser mayor"): se detecto que el diseño anterior tenia el defecto de que Pro constaba MENOS por asesor que Basico (12.90 vs 16.33 USD/asesor) — un descuento por volumen no intencional. Nuevos precios: Basico sin cambios (USD 49/mes, ≤3), Pro sube de USD 129 a **USD 199/mes** (≤10), Enterprise cambia de "base fija $299 + $15/asesor extra" a **USD 30/asesor/mes plano, sin tope**. Curva resultante: USD 16.33 → 19.90 → 30.00 por asesor, ascendente
- Motivo: Pedidos explicitos del cliente (profundizar 2 apartados + comparar contra Tokko + corregir la curva de precio)
- Impacto: Pro ahora queda POR ENCIMA del techo de Tokko (USD 199 vs USD 147) — se documenta como decision consciente/apuesta comercial, ya no hay "estamos mas barato que todos" como red de seguridad en ese escalon. Basico se mantiene mas barato que la entrada de Tokko (USD 49 vs USD 69 por 2 usuarios)
- Recomendacion registrada: validar el precio de Pro con 1-2 conversaciones de venta reales antes de publicarlo como definitivo, dado el mayor riesgo comercial de la nueva estrategia
- Estado: Documentos actualizados. Presupuesto (etapa 4) sigue en BORRADOR pendiente de aprobacion final del cliente sobre esta nueva curva de precios.

### 2026-07-02 - presupuestador (correccion de rumbo — v3, volumen = mas barato)
- Etapa: Ajuste sobre `presupuesto-cliente.md` y `4-presupuestador.md` seccion 17 — corrige la v2 del turno anterior
- Cambio: El cliente aclaro que la intencion real era la opuesta a la v2 (curva ascendente por asesor): el servicio es el mismo en todos los planes y a mayor cantidad de usuarios el precio por usuario debe bajar (descuento por volumen estandar). Nueva base explicita del cliente: Basico = USD 60/mes para 3 asesores (subio de USD 49)
- Nuevos precios v3: Basico USD 60/mes (≤3, USD 20.00/asesor), Pro USD 150/mes (≤10, USD 15.00/asesor), Enterprise USD 150/mes + USD 10/mes por asesor extra sobre 10 (USD 14.55/asesor en 11, bajando asintoticamente). Metodo: precio base + costo marginal decreciente por asesor adicional (evita el salto/cliff entre planes que tendria una tarifa plana por asesor)
- Motivo: Pedido explicito del cliente, corrigiendo la interpretacion anterior
- Recalculos: cobertura de desarrollo con 3 grupos Basico ahora es USD 2.250 cobrados de entrada vs USD 1.259 de costo (excedente USD 991, mucho mas holgado que antes); con 2 grupos el excedente es USD 241 (antes casi sin margen). Ejemplo de rentabilidad de 3 grupos Basico: ganancia recurrente USD 159.55/mes (~89% margen), USD 2.365 en el año 1
- Comparacion Tokko actualizada: Basico sigue mas barato que Tokko Duo (USD 60 vs USD 69 por 2 usuarios); Pro queda practicamente empatado con el techo de Tokko (USD 150 vs USD 147) pero cubriendo mas asesores — a diferencia de la v2, ya no hay ningun escalon por encima del techo de mercado conocido
- Estado: v3 marcada como version vigente recomendada para publicar. `presupuesto-cliente.md` y `4-presupuestador.md` actualizados. Presupuesto (etapa 4) sigue en BORRADOR pendiente de aprobacion final del cliente.

### 2026-07-02 - presupuestador (precio oficial real de Tokko Broker, aportado por el cliente)
- Etapa: Ajuste sobre `4-presupuestador.md` seccion 17 — reemplaza los dos datos anteriores de Tokko (proxy Mexico y comparasoftware.com.ar), ambos muy por debajo del precio real
- Cambio: El cliente aporto los precios oficiales de tokkobroker.com/es-ar/planes (accedidos con sesion real de navegador, el bloqueo HTTP 403 de WebFetch es solo para trafico automatizado): Inicial 2 usuarios $136.956 ARS/mes ($90.40 USD con dolar blue 1515), plan intermedio 4 usuarios $237.835 ARS/mes ($156.99 USD), Profesional 10 usuarios $378.201 ARS/mes ($249.64 USD), Corporativo 15 usuarios $656.678 ARS/mes ($433.45 USD). Tambien se registraron los precios "sin impuestos nacionales" de cada plan
- Motivo: Dato real aportado directamente por el cliente, mas confiable que las dos fuentes usadas anteriormente
- Hallazgo: la brecha de precio es mucho mayor de lo que mostraba la fuente de terceros. century-21 v3 queda 33-54% mas barato que Tokko en los tres tramos comparables (2-3, 10 y 15 usuarios) — hay espacio real para subir precios y seguir siendo claramente mas barato que el jugador mas establecido del mercado
- Accion tomada: NINGUN cambio de precio aplicado todavia — se dejo registrado el hallazgo y el espacio de negociacion disponible (ej. duplicar Pro a ~$300/mes seguiria 20% por debajo de Tokko Profesional), pendiente de que el cliente decida si quiere capturar ese margen
- Estado: Investigacion de mercado actualizada con el dato mas confiable disponible hasta ahora. Precios v3 sin cambios, a la espera de decision del cliente.

### 2026-07-02 - presupuestador (rearmado de planes — v4, captura de margen)
- Etapa: Ajuste sobre `presupuesto-cliente.md` y `4-presupuestador.md` seccion 17 — v4, reemplaza v3
- Cambio: A pedido del cliente ("rearmar Planes disponibles para ofrecer"), tras confirmar el precio oficial real de Tokko, se recalibran Pro y Enterprise para capturar parte del margen documentado (33-54% mas barato en v3) sin perder la ventaja de precio. Basico se mantiene sin cambios (USD 60/mes, gancho de entrada agresivo)
- Nuevos precios v4: Pro USD 185/mes (antes $150, +23%), Enterprise USD 185/mes + USD 25/mes por asesor extra sobre 10 (antes $150+$10, marginal +150%). Metodo: costo marginal decreciente ($20/asesor en Basico, $18/asesor incremental en Pro, $25/asesor incremental en Enterprise)
- Resultado vs Tokko real: Basico 33.6% mas barato (Inicial), Pro 25.9% mas barato (Profesional), Enterprise 28.5% mas barato a 15 usuarios (Corporativo) — posicionamiento consistente ~25-30% por debajo del lider de mercado en Pro/Enterprise, decision de posicionamiento (no techo tecnico, hay mas margen documentado si se quiere subir mas)
- La cobertura del costo de desarrollo con 2-3 grupos no cambia (sigue basada en Basico, sin modificar)
- Estado: v4 es la version vigente recomendada para ofrecer. `presupuesto-cliente.md` actualizado con la tabla final. Presupuesto (etapa 4) sigue en BORRADOR pendiente de aprobacion final del cliente.

### 2026-07-02 - presupuestador (eliminacion del pago inicial de configuracion)
- Etapa: Ajuste sobre `presupuesto-cliente.md` y `4-presupuestador.md` seccion 17
- Cambio: Se elimina el fee de setup/configuracion inicial (USD 150/200/300 segun plan) de los tres planes. Los planes pasan a cobrarse solo como plan anual o mensual, sin cargo de alta separado. Se quita tambien el texto explicativo sobre el descuento anual y el pago unico de configuracion, simplificando la tabla de planes
- Motivo: Pedido explicito del cliente
- Recalculos: cobertura del costo de desarrollo con 3 grupos Basico ahora es USD 1.800 (antes 2.250 con setup) vs costo de USD 1.259 → excedente USD 541 (antes 991). **Cambio relevante:** con 2 grupos ya NO alcanza a cubrir el costo (2×$600=$1.200 < $1.259, faltan $59) — antes con setup, 2 grupos si cubrian. La meta de "2 o 3 grupos" pasa a depender de tener 3 como minimo. Ejemplo de rentabilidad recalculado sin ingreso de setup: ganancia $159.55/mes (~89% margen) desde el primer mes, $1.915/año todos los años (ya no hay diferencia entre año 1 y año 2+)
- Estado: `presupuesto-cliente.md` y `4-presupuestador.md` actualizados sin fee de configuracion inicial. Presupuesto (etapa 4) sigue en BORRADOR pendiente de aprobacion final del cliente.

### 2026-07-02 - presupuestador (correccion de calculo USD/asesor + facturacion anual exclusiva)
- Etapa: Ajuste sobre `presupuesto-cliente.md` y `4-presupuestador.md` seccion 17 — corrige un error de calculo senializado por el cliente
- Cambio 1 (error corregido): el marginal de Enterprise estaba en USD 25/mes por asesor extra sobre 10, MAYOR al promedio de Pro (USD 18,50/asesor) — eso hacia que el USD/asesor de Enterprise subiera en vez de bajar con mas asesores, rompiendo la promesa central de "a mayor volumen, mas barato por asesor". Se corrige el marginal a USD 15/mes por asesor extra (menor al promedio de Pro), restaurando una curva estrictamente decreciente: USD 20,00 (Basico) → USD 18,50 (Pro) → USD 18,18 en 11 asesores → bajando progresivamente
- Cambio 2: se elimina la facturacion mensual como opcion — factura exclusivamente anual. Se quita la oracion "Tambien esta disponible facturacion mensual..." del documento cliente y del interno. La columna "precio mensual" que queda en el documento interno es solo referencia de calculo, no una opcion real de cobro
- Recalculo Enterprise: formula nueva USD 1.850/año + USD 150/año por asesor extra sobre 10 (antes USD 250/año). A 15 asesores: USD 2.600/año (antes USD 3.100/año) = USD 260/mes lista vs Tokko Corporativo USD 433,45/mes → 40.0% mas barato (antes 28.5%, calculado mal)
- Motivo: Cliente detecto el error de calculo directamente
- Estado: `presupuesto-cliente.md` y `4-presupuestador.md` actualizados con la curva corregida y facturacion anual exclusiva. Presupuesto (etapa 4) sigue en BORRADOR pendiente de aprobacion final del cliente.
