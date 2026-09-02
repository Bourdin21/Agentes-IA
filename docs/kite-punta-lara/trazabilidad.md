# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-09-01 - analista-funcional
- Etapa: Discovery
- Cambio: Alta de proyecto nuevo (kite-punta-lara). Investigación de dominio completada sobre 7 temas (CARP, SHN, SMN, Windguru, birazón, sudestada, spot Punta Lara/Club Universitario) y borrador de alcance funcional entregado al cliente (Joaquín) con 9 preguntas abiertas marcadas como hipótesis a validar.
- Motivo: pedido inicial del cliente — pronóstico de viento/kite para Punta Lara, sin definiciones previas.
- Impacto en capas: N/A (etapa de discovery, sin diseño técnico todavía).
- Riesgos/supuestos: Windguru no tiene API pública de pronóstico (solo Upload API de estaciones propias) — el "promedio de modelos" que hace el cliente manualmente requiere una fuente de datos alternativa (Open-Meteo, scraping, o servicio pago) a definir. Stack PHP/DonWeb no tiene precedente en el catálogo del estudio.

### 2026-09-01 - analista-funcional
- Etapa: Análisis
- Cambio: Cierre de Análisis en la misma sesión, 3 rondas de preguntas resueltas por el cliente. Decisiones clave: multiusuario con registro abierto, dashboard público sin login (cuenta solo para equipo/bitácora), Open-Meteo como fuente de pronóstico del MVP (Windy API y scraping Windguru documentados como fallback futuro), recomendación de equipo (tabla nudos→kite) en vez de sí/no simple, birazón modelada como 2 señales independientes (brisa de calma + bajante), sudestada como oportunidad condicional, bitácora de sesiones con fin de calibración + uso social, notificación proactiva por email, horizonte de pronóstico hoy+3 días, subdominio nuevo dedicado en DonWeb. 6 casos de uso con criterios de aceptación definidos.
- Motivo: cerrar el gate de Análisis antes de habilitar Diseño funcional, según secuencia obligatoria del estudio.
- Impacto en capas: Presentación (dashboard público + área logueada), Negocio (modelo de cálculo/scoring, reglas de birazón/sudestada, notificación), Datos (usuarios, tabla de equipo, bitácora de sesiones — requiere esquema de BD nuevo).
- Riesgos/supuestos: CARP/SHN/SMN sin API oficial estable (cada fuente debe fallar aislada); Open-Meteo puede tener menor resolución cerca de la costa que el promedio manual de Windguru — recomendable validación empírica corta antes de Implementación; umbrales de birazón/sudestada son aproximación bibliográfica a calibrar con la bitácora real; registro abierto sin moderación (riesgo bajo, grupo chico); no hay agente implementador PHP en el catálogo del estudio, a resolver en Arquitectura/Presupuesto.

### 2026-09-01 - disenador-funcional
- Etapa: Diseno
- Cambio: Diseño funcional cerrado sobre el Análisis del mismo día. 7 pantallas (Home público, Login, Registro, Dashboard logueado, Mi equipo, Cargar sesión, Bitácora social) con wireframe textual, 5 ViewModels (PronosticoDia, EstacionEnVivo, EquipoQuiverItem, PerfilUsuario, SesionBitacora) con validaciones funcionales, motor de cálculo con reglas explícitas (birazón = 2 señales independientes con umbrales configurables; sudestada ConTemporal fuerza "No recomendable" con prioridad sobre la recomendación de equipo), permisos por pantalla, y plan funcional en 3 etapas (núcleo de cálculo sin cuentas → cuentas → bitácora/notificaciones) para que Arquitectura pueda secuenciar el trabajo.
- Motivo: cerrar el gate de Diseño antes de habilitar Arquitectura, según secuencia obligatoria del estudio.
- Impacto en capas: Presentación (7 pantallas + 2 plantillas de email), Negocio (5 servicios: ConsolidadorEstaciones, Pronostico, MotorDeCalculo, Notificaciones, Bitacora — umbrales configurables, no hardcodeados), Datos (Usuario, EquipoQuiverItem, SesionBitacora + recomendación de caché de corta duración 15-30min sobre las APIs externas).
- Riesgos/supuestos: se agrega un supuesto nuevo no confirmado — registro sin verificación de email (alta directa), a confirmar con el cliente antes de Arquitectura. Se reutiliza PAT-007 (SmtpMailer.php) para el envío de avisos y el criterio PAT-008 (filtro por columna visible) para la bitácora social; no se agrega patrón nuevo al catálogo (motor de scoring específico del dominio, sin indicio de reutilización en otros proyectos del estudio).

### 2026-09-01 - arquitecto-mvc (adaptado a PHP)
- Etapa: Arquitectura
- Cambio: Arquitectura técnica cerrada sobre el Diseño del mismo día. Sin agente arquitecto PHP en el catálogo del estudio, se tradujo el rol .NET (Domain/Application/Infrastructure/Web) al stack real: front controller sin framework + `src/Services` (negocio) + `src/Repositories` con PDO (datos), sesión nativa de PHP sin roles (solo autenticado/anónimo), 3 tablas nuevas (`usuarios`, `equipo_quiver_items`, `sesiones_bitacora`) y cron standalone para el aviso diario. Reutilización literal confirmada de PAT-007 (`SmtpMailer.php`, ya en producción en labipac-front/diercas-front). Cliente confirmó SSH/Composer y cron disponibles en DonWeb, y durante esta misma etapa envió credenciales reales de FTP (`club@olvidata.com.ar` / `ftp://olvidata.com.ar`) y de la base de datos MySQL ya creada (`olvidata_club`) — guardadas únicamente en `docs/credenciales.local.md` (gitignored, nunca en un archivo tracked).
- Motivo: cerrar el gate de Arquitectura antes de habilitar Presupuesto, según secuencia obligatoria del estudio.
- Impacto en capas: Presentación (front controller + 4 controllers + plantillas PHP planas con `htmlspecialchars` consistente), Negocio (7 Services, umbrales del motor de cálculo como configuración editable, no hardcodeados), Datos (3 tablas nuevas vía migraciones SQL numeradas, sobre la base `olvidata_club` ya provista).
- Riesgos/supuestos: sin framework, la seguridad (CSRF/XSS/sesión) depende de un helper centralizado usado con disciplina en las 4 pantallas con formulario — a reforzar explícitamente en el checklist de QA de este proyecto. Cron en hosting compartido puede fallar silenciosamente — mitigado con logging propio, pero sin alerta automática. Versión exacta de PHP del plan DonWeb aún no confirmada. Host de conexión MySQL (típicamente `localhost`) a confirmar al empezar Implementación.

### 2026-09-01 - arquitecto-mvc (adaptado a PHP)
- Etapa: Arquitectura
- Cambio: Confirmado el subdominio definitivo — `club.olvidata.com.ar`. No es un dominio propio nuevo: se aloja bajo el dominio `olvidata.com.ar` en DonWeb, mismo esquema que otros bots/subdominios de Olvidata Soft (coincide con el usuario FTP `club@olvidata.com.ar` ya recibido).
- Motivo: precisión pedida por el cliente sobre la decisión de hosting ya cerrada en Arquitectura (antes documentada como "subdominio nuevo dedicado" sin nombre confirmado).
- Impacto en capas: Presentación/infraestructura de deploy — sin cambio en el código de la app. DNS y certificado SSL del subdominio quedan bajo la infraestructura ya existente de Olvidata Soft, no como alta de dominio nueva.
- Riesgos/supuestos: si al momento de deploy el subdominio no resuelve o falta el SSL, es un tema de configuración DNS/panel DonWeb a resolver con la cuenta de Olvidata, no un problema de arquitectura de la aplicación.

### 2026-09-01 - arquitecto-mvc (adaptado a PHP)
- Etapa: Arquitectura
- Cambio: Confirmada la versión de PHP del hosting — 8.4 (lsphp, LiteSpeed). Cierra el último riesgo abierto de la etapa. Se agrega nota de gotcha típico de hosting LiteSpeed: el PHP que ejecuta el cron/CLI puede no coincidir con el `lsphp` que sirve la web — verificar con `php -v` dentro de la tarea programada en Implementación, no asumirlo.
- Motivo: dato de panel de hosting compartido por el cliente, necesario para cerrar el riesgo de versión que había quedado pendiente en el cierre de Arquitectura.
- Impacto en capas: Infraestructura/despliegue — sin cambio de diseño, habilita usar sintaxis PHP 8.x moderna sin restricción.
- Riesgos/supuestos: ninguno nuevo más allá del gotcha de CLI vs. web ya anotado.

### 2026-09-01 - presupuestador
- Etapa: Presupuesto
- Cambio: Etapa saltada por pedido explícito del cliente ("saltear presupuesto"). Mismo precedente que vinosefue (presupuesto saltado 2026-08-31). Gate de "Presupuesto aprobado por el cliente" se da por satisfecho porque el cliente es el propio Joaquín.
- Motivo: proyecto personal sin cliente externo — el presupuesto hubiese sido solo informativo, no una propuesta comercial a enviar.
- Impacto en capas: N/A.
- Riesgos/supuestos: sin estimación de horas/esfuerzo registrada — no hay cierre de calibración posible para este proyecto (no se puede comparar estimado vs. real).
