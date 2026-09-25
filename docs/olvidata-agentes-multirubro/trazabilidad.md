# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-09-14 - orquestador
- Etapa: Setup
- Cambio: Proyecto incorporado al flujo formal del estudio a pedido de Joaquín ("todo lo que sea portal desarrollarlo bajo las reglas de /agentes-ia-orquestador"). Carpeta creada desde la plantilla, metadata y fila en `docs/indice.md`.
- Motivo: el template (motor M1) se construyó fuera del flujo; a partir de M2 el desarrollo del portal sigue las 9 etapas con gates.
- Impacto en capas: —
- Riesgos/supuestos: producto propio de Olvidata; el aprobador de gates, incluido el de presupuesto, es Joaquín. Documentos de producto de referencia en el repo: `docs/diseno-organizacion-roles-reglas.md`, `docs/diseno-motor-agentes.md`, `PLAN-IMPLEMENTACION.md`.

### 2026-09-14 - analista-funcional
- Etapa: Discovery + Analisis
- Cambio: M2 Organización analizada: rol de organización Director/Empleado en sesión, ABM de Áreas, gestión de miembros, cartera de clientes de la organización (todos ven todos, baja solo Director), servicio de permisos por rol, visibilidad de tareas por rol y rol en el alta de usuarios del backoffice. 6 casos de uso, 12 reglas funcionales, 17 criterios de aceptación.
- Motivo: base de reglas por nivel (M3) y agentes de la organización (M4) del diseño aprobado el 2026-09-14.
- Impacto en capas: Presentación (pantallas Miembros, Áreas, Clientes, menú por rol), Negocio (permisos por rol, regla del último Director, unicidades), Datos (rol y área del usuario, áreas, clientes de cartera — migración EF).
- Riesgos/supuestos: R-01 fuga entre organizaciones en gestión de miembros (usuario sin filtro automático por tenant); R-02 sesión desactualizada tras cambio de rol; R-03 organización sin Director. Reutilización relevada: century-21 (filtro de tenant resuelto desde el usuario + validación de pertenencia en escrituras contra IDOR); su modelo de roles plano no aplica. 5 preguntas abiertas con hipótesis (P1–P5).

### 2026-09-14 - analista-funcional
- Etapa: Analisis (gate)
- Cambio: Joaquín aprobó el análisis y respondió P1–P5: sin migración de datos (no hay clientes), cliente de cartera con todos los datos, alta de miembros solo por el SuperUsuario, clientes solo con baja lógica, área opcional para el Director.
- Motivo: cierre del gate Análisis → Diseño.
- Impacto en capas: Presentación (sin alta de miembros para el Director), Negocio (RF-06 alta por SuperUsuario), Datos (sin estado Activo/Inactivo en cartera).
- Riesgos/supuestos: R-04 descartado.

### 2026-09-14 - disenador-funcional
- Etapa: Diseno
- Cambio: 10 pantallas (Áreas, Miembros, Cartera, detalle de organización en backoffice, Tareas por rol, perfil), 10 ViewModels, mensajes de validación, permisos por pantalla, contratos funcionales de Permisos/Áreas/Miembros/Cartera/Tareas y 16 historias de usuario.
- Motivo: diseño implementable de M2 sobre el análisis aprobado.
- Impacto en capas: Presentación (menú por rol, sistema de formularios portado de la-platense, Tareas a DataTables), Negocio (invariante del último Director, CUIT/DNI), Datos (rol/área del miembro, Área, Cliente de cartera).
- Riesgos/supuestos: decisiones a validar D-1 renombre "Organizaciones y licencias", D-2 staff en solo lectura sobre áreas/cartera (ajusta la matriz del análisis), D-3 Tareas a DataTables, D-4 Usuarios solo staff, D-5 portar sistema de formularios. Reutilización: century-21, PAT-017, la-platense (PAT-015, formularios), Users del template. Nuevo patrón PAT-027.

### 2026-09-14 - disenador-funcional
- Etapa: Diseno (gate)
- Cambio: Joaquín aprobó el diseño con D-1..D-5 sin cambios.
- Motivo: cierre del gate Diseño → Arquitectura.
- Impacto en capas: —
- Riesgos/supuestos: —

### 2026-09-14 - arquitecto-mvc
- Etapa: Arquitectura
- Cambio: componentes por capa de M2: entidades `Area` y `ClienteCartera` (ITenantOwned), `RolOrganizacion`/`AreaId` en usuario, `Tenant.VersionMiembros`; `IContextoUsuario` + `IResolvedorSesion` (reemplaza claim tenant_id y `TenantDesdeUsuario`), `IPermisosOrganizacion`, servicios de Áreas/Miembros/Cartera, visibilidad de tareas por rol en `ServicioTareas`; policies `RequireMiembro`/`RequireDirector`; migración `OrganizacionM2`.
- Motivo: resolver RF-11 (refresco inmediato), RF-05 bajo concurrencia y R-01 (IDOR en usuarios) sobre el diseño aprobado.
- Impacto en capas: Domain (2 entidades, 2 enums, campos en usuario/tenant), Application (5 interfaces, DTOs, `ServiceResult.TipoError`, helper CUIT/DNI), Infrastructure (6 servicios, configs, audit trail sin PasswordHash/SecurityStamp), Web (middleware antes de UseAuthorization, 3 controllers nuevos, 5 modificados, vistas, CSS/JS portados).
- Riesgos/supuestos: RT-01 cache por instancia (límite aceptado en pool único), RT-02 columnas generadas/check en MySql.EntityFrameworkCore, RT-03 cambio de orden del pipeline, RT-04 extensión de `ServiceResult`. Reuso literal: template (filtro tenant, concurrencia M1, Users), la-platense (formularios, PAT-015, Select2); patrones: century-21, PAT-008/016/017. PAT-017 verificado sin código; PAT-027 ampliado con notas de arquitectura.

### 2026-09-14 - presupuestador
- Etapa: Presupuesto (omitida)
- Cambio: Joaquín pidió saltear el presupuesto por ser un proyecto personal. Arquitectura aprobada. Se habilita Implementación sin cotización.
- Motivo: producto propio sin cliente externo.
- Impacto en capas: —
- Riesgos/supuestos: la etapa 8 (cierre de calibración) solo registra esfuerzo real, sin estimado para comparar.

### 2026-09-14 - implementador
- Etapa: Implementacion
- Cambio: M2 Organización implementada. Domain: `Area`, `ClienteCartera`, `RolOrganizacion`/`AreaId` en usuario, `Tenant.VersionMiembros`. Application: `IContextoUsuario`, `IResolvedorSesion`, `IPermisosOrganizacion`, servicios de Áreas/Miembros/Cartera, `ServiceResult.TipoError`, helpers CUIT/DNI y búsqueda. Infrastructure: resolvedor con caché 60 s invalidable, `MiembroService` con invariante del último Director por token de versión y reintento, `ServicioTareas` con visibilidad por rol. Web: `SesionOrganizacionMiddleware` antes de `UseAuthorization` (se eliminan claim `tenant_id`, `TenantMiddleware`, `TenantClaimsPrincipalFactory`, `TenantDesdeUsuario`), policies `RequireMiembro`/`RequireDirector`, pantallas Áreas, Miembros, Cartera, backoffice "Organizaciones y licencias" con alta de miembros (SuperUsuario), Tareas en DataTables, perfil, menú por rol, sistema de formularios y Select2 global portados de la-platense. Migración `OrganizacionM2` aplicada en `olvidata_agentes_dev`. Build OK; tests 48/48 (13 nuevos).
- Motivo: arquitectura M2 aprobada; presupuesto dispensado por Joaquín.
- Impacto en capas: Datos (migración: 2 tablas, 3 columnas, check constraint, columnas generadas STORED con índice único), Negocio (permisos por rol, RF-05, RF-11, RF-12), Presentación (3 controllers nuevos, 5 modificados, 14 vistas nuevas).
- Riesgos/supuestos: RT-01 caché por instancia; `MySql.EntityFrameworkCore` ignora `stored: true` (columnas generadas escritas con SQL); SecurityStamp se rota solo al bloquear (DI-1); policy fallida en AJAX devuelve 403 sin JSON (DI-10). Pendiente explícito (LP-002): el staff no tiene UI para editar rol/estado/nombre/email de miembros; `Users/*` y `Clientes/Index` legacy sin revisar ortografía/DataTables; `Tenant.Estado` no se evalúa en la sesión. PAT-027 del catálogo completado con rutas reales.

### 2026-09-14 - qa
- Etapa: Pruebas funcionales (QA M2)
- Cambio: verificación en navegador real (Playwright librería 1.63 + Chromium; el MCP `playwright` no estaba cargado en la sesión) con portal local y motor apagado. CA-01.1..CA-06.3, CA-T.1 (ids de otra organización en URL y POST de Áreas, Miembros incl. AreaId, Cartera y Tareas) y R-03 (carrera de degradaciones) en PASS. Checklists de listados, Select2, daterangepicker, formularios, mobile, tema oscuro y ortografía; regresión de login, Usuarios, backoffice, Núcleo, Uso, Agentes, Tareas con progreso y Perfil. Auto-fix REG-010: `Views/Shared/_Layout.cshtml` (link de Auditoría solo staff + tilde). Auto-fix OLV-001 (ítem nuevo en `docs/qa/regresiones-manuales.yml`): `wwwroot/css/site.css` con tema oscuro para Select2 y daterangepicker. Build 0 errores, tests 48/48. Veredicto: apto con observaciones.
- Motivo: gate de QA de M2 antes de Documentación.
- Impacto en capas: Presentación (layout y CSS; sin cambios de negocio ni datos).
- Riesgos/supuestos: observaciones sin cambio de comportamiento (filtros de texto solo por `keyup`, pantallas legadas sin sistema de formularios, contraste de `ov-alert info` en oscuro, URLs absolutas del layout si se hostea en subdirectorio). Datos de prueba en `olvidata_agentes_dev`: org "QA Org B" (id 4), usuarios `dira@`, `dira2@`, `empa@`, `dirb@`, `adminqa@qa.test`, 16+2 áreas, 19+1 clientes de cartera, 4 tareas QA terminadas (ninguna pendiente). Primera validación completa del catálogo cross-proyecto registrada en `6-qa.md`.

### 2026-09-14 - documentador
- Etapa: Documentacion
- Cambio: resumen de entrega `resumen-sprint-m2-organizacion.md` (formato 31, primera persona, sin tecnicismos) con lo validado por QA, beneficios, pendientes (UI staff para editar miembros, organización suspendida sigue entrando, pantallas legadas) y próximo paso M3 Reglas.
- Motivo: cierre de comunicación de M2.
- Impacto en capas: —
- Riesgos/supuestos: lector Joaquín (proyecto personal).

### 2026-09-14 - presupuestador
- Etapa: Cierre calibracion
- Cambio: registrado esfuerzo real de M2 sin estimado (implementador ~43 min de agente, QA ~32 min); lecciones para M3–M12: margen fijo en migraciones con MySql.EntityFrameworkCore (columnas generadas STORED, orden de índices con FK), cambios transversales de sesión como ítem propio, verificar tema oscuro de componentes portados, registrar horas humanas de revisión desde M3.
- Motivo: cierre del flujo de 9 etapas de M2.
- Impacto en capas: —
- Riesgos/supuestos: sin desvío calculable por presupuesto omitido. M2 cerrada.

### 2026-09-14 - analista-funcional
- Etapa: Discovery + Analisis (M3 Reglas)
- Cambio: M3 analizada: reglas por alcance (organización, área, usuario, cliente de cartera, cliente + agente base, agente base), modo obligatoria/por defecto, tipo regla/procedimiento, reglas de plataforma, constructor de contexto con precedencia de 9 niveles, cliente de cartera opcional en la nueva tarea, vista previa de reglas efectivas, instantánea auditable en la tarea, versiones, límites de tamaño. 10 casos de uso, 12 reglas, 15 criterios de aceptación, 5 riesgos, 9 preguntas con hipótesis.
- Motivo: siguiente etapa del diseño aprobado (`docs/diseno-organizacion-roles-reglas.md`), pedido de Joaquín ("continuar").
- Impacto en capas: Presentación (pantallas de reglas, nueva tarea con cliente y vista previa, detalle de tarea), Negocio (constructor de contexto, permisos por alcance, límites, versiones), Datos (reglas, versiones, reglas de plataforma, instantánea y cliente en la tarea — migración EF).
- Riesgos/supuestos: R-M3-01 inyección de instrucciones en reglas; R-M3-02 costo; R-M3-03 deriva vista previa/instantánea/motor. Reutilización: crm-olvidata (prompt en prefijo cacheado + contexto variable), versionado del núcleo. Nivel 6 (agentes de la organización) reservado para M4.

### 2026-09-14 - analista-funcional
- Etapa: Analisis M3 (gate, parcial)
- Cambio: respuestas de Joaquín: P1 solo Director; P2 cualquier miembro; P3 instantánea al crear; P4 etiquetas en M3; P6 procedimientos en M3; P7 límites confirmados; P8 Empleado ve reglas por defecto; P9 staff ve el texto de las reglas de las organizaciones (control de prompts). P5 (reglas de plataforma) queda abierta: se re-explica. Pedidos nuevos: N-01 agente configurador de reglas del Director; N-02 agente asistente que crea tareas a empleados/subagentes — ubicación propuesta fuera de M3, a confirmar.
- Motivo: gate Análisis → Diseño de M3.
- Impacto en capas: Presentación (vista de reglas en backoffice para staff), Negocio (permisos de staff sobre reglas).
- Riesgos/supuestos: N-01/N-02 amplían el roadmap (agentes con herramientas que escriben reglas y tareas asignadas a personas).

### 2026-09-14 - analista-funcional
- Etapa: Analisis M3 (gate)
- Cambio: P5 respondida: reglas de plataforma como archivo del núcleo importado y publicado con evaluación obligatoria. N-01 y N-02 ubicados después de M4 (N-01 = etapa M4b; N-02 dentro de M7). Análisis de M3 aprobado. Roadmap actualizado en `docs/diseno-organizacion-roles-reglas.md` del repo.
- Motivo: cierre del gate Análisis → Diseño de M3.
- Impacto en capas: Datos/Negocio (reglas de plataforma vía núcleo versionado, sin ABM).
- Riesgos/supuestos: —

### 2026-09-14 - disenador-funcional
- Etapa: Diseno (M3 Reglas)
- Cambio: 9 pantallas/ajustes (Reglas con pestañas por alcance, alta/edición con aviso de reglas del mismo tema y uso del límite, detalle con historial, Nueva tarea con cliente y vista previa, reglas aplicadas en el detalle de tarea, cliente en listado de tareas, cards de reglas en Cartera y Áreas, vista de staff en backoffice, reglas de plataforma en Núcleo), 7 ViewModels, mensajes, máquina de estados Activa/Inactiva/No se aplica, contratos de Reglas/Permisos/Constructor de contexto/Tareas/Núcleo y 15 historias.
- Motivo: diseño implementable de M3 sobre el análisis aprobado.
- Impacto en capas: Presentación (pantallas nuevas y Nueva tarea rediseñada), Negocio (constructor de contexto único para vista previa, instantánea y motor), Datos (reglas, versiones, etiquetas, instantánea y cliente en tarea).
- Riesgos/supuestos: decisiones a validar D-M3-1 alcance fijo al editar, D-M3-2 límites de alcances por agente, D-M3-3 versiones solo con cambios, D-M3-4 cliente en Tareas, D-M3-5 accesos desde Cartera/Áreas, D-M3-6 staff solo lectura con reglas de miembros, D-M3-7 etiquetas sugeridas. Reutilización: pantallas M2, versionado del núcleo, crm-olvidata. Nuevo patrón PAT-028.

### 2026-09-14 - disenador-funcional
- Etapa: Diseno M3 (gate)
- Cambio: Joaquín aprobó el diseño con D-M3-1..D-M3-7 y los ajustes de simplificación D-M3-8..D-M3-12 (nombres llanos, "Siempre / Salvo que se indique otra cosa", opciones avanzadas plegadas, vista previa como centro). Roadmap: nueva etapa M3b "Seguir conversando sobre una tarea" y reglas sugeridas por rubro junto con M4.
- Motivo: consulta de Joaquín sobre reemplazar el uso de Claude web por algo más organizado y simple; se detectó que sin iteración sobre el resultado los usuarios volverían a Claude web.
- Impacto en capas: Presentación (rótulos y plegables); sin cambio de arquitectura.
- Riesgos/supuestos: la complejidad interna de precedencia no se expone al usuario.

### 2026-09-14 - arquitecto-mvc
- Etapa: Arquitectura (M3 Reglas)
- Cambio: entidades `Regla` (token `VersionActual`) y `ReglaEvento` (historial inmutable), `TipoArtefacto.ReglaPlataforma` con rubro técnico `plataforma` en el núcleo (3 reglas iniciales en borrador), `IReglaService` (permisos por alcance, límites por balde, versiones, mismo tema, etiquetas, vista staff), `IConstructorContexto` único para vista previa, instantánea y motor (instantánea por ids + hash, reconstrucción verificada al ejecutar), `SolicitudModelo.Sistema` en 3 bloques con caché, tarea con cliente de cartera, `ReglasController` y ajustes en Agentes/Tareas/Cartera/Áreas/backoffice; migración `ReglasM3`.
- Motivo: diseño M3 aprobado con simplificación de UI.
- Impacto en capas: Domain (2 entidades, 5 enums, tarea), Application (servicio de reglas, constructor, DTOs, opciones, permisos), Infrastructure (servicios, constructor, proveedor de modelo, importador, configs), Web (1 controller nuevo, 5 modificados, vistas).
- Riesgos/supuestos: RT-M3-01 caché de bloques chicos, RT-M3-02 carrera de límites aceptada, RT-M3-03 inmutabilidad de eventos/versiones, R-M3-01 inyección (mitigada, no garantizada; prueba real opcional con OK de costo). Reuso literal: pantallas/helpers M2, importador y versionado del núcleo, concurrencia M2, ModeloGuionado; patrón crm-olvidata. PAT-028 ampliado.

### 2026-09-14 - presupuestador
- Etapa: Arquitectura M3 (gate) + Presupuesto (omitido)
- Cambio: Joaquín aprobó la arquitectura de M3 (3 bloques con precedencia en el bloque estable, instantánea por ids + hash, rubro técnico `plataforma`, carrera de límites aceptada). Presupuesto omitido por criterio vigente. Se lanza Implementación.
- Motivo: gate Arquitectura → Implementación.
- Impacto en capas: —
- Riesgos/supuestos: —

### 2026-09-14 - implementador
- Etapa: Implementación (M3 Reglas por alcance)
- Cambio: entidades `Regla` (token `VersionActual`, check `CK_Reglas_Destino`) y `ReglaEvento` inmutable; `IReglaService` (permisos por alcance P1/P2, preferencias solo del autor, límites por balde con `SUM(CHAR_LENGTH)`, versiones con campos cambiados, conflicto de versión, estado derivado "No se aplica", mismo tema por etiquetas, cards de Cartera/Áreas, vista de staff solo lectura); `IConstructorContexto` único (calcular → instantánea por ids → armar en 3 bloques: B1 plataforma + precedencia + agente + instrucciones y B2 empresa + área con caché, B3 cliente/agente/usuario sin caché; escape XML; hash SHA-256); `SolicitudModelo.Sistema` en bloques con `CacheControlEphemeral` por bloque; tarea con cliente de cartera, instantánea y hash verificado antes de llamar al modelo (distinto → Fallida; sin instantánea → armado anterior); pantallas Reglas (pestañas con rótulos llanos D-M3-8..12, formulario con opciones avanzadas plegadas, uso del límite y mismo tema, detalle con historial), Nueva tarea con cliente y "Esto es lo que el agente va a tener en cuenta", "Lo que el agente tuvo en cuenta" en el detalle, columna/filtro Cliente en Tareas, backoffice `Clientes/Reglas`; `nucleo/plataforma/plataforma.yml` + 3 reglas; importador `reglas_plataforma`; `plataforma` fuera del catálogo y no licenciable. Migración `ReglasM3` aplicada en dev.
- Motivo: arquitectura M3 aprobada (presupuesto omitido por decisión de Joaquín).
- Impacto en capas: Domain (2 entidades, 5 enums, tarea), Application (servicio de reglas, constructor, DTOs, opciones, permisos, bloques de sistema), Infrastructure (servicios, constructor, motor, proveedor, importador, catálogo, licencias, configs, migración), Web (1 controller nuevo, 5 modificados, 14 vistas nuevas, 7 modificadas, menú).
- Evidencia: build 0 errores (1 advertencia preexistente); tests 61/61 (13 nuevos, incluido el ejemplo Laura/Martín/Panadería Norte); SQL real en transacción revertida (check 3819 en 7 casos inválidos, CHAR_LENGTH con tildes, LIKE de etiqueta exacta, FK 1452/1451, 0 restos); EF → MySQL real en transacción revertida: 42 pasos OK sin errores de type mapping (MH-001), 0 restos. Import de plataforma: 3 versiones en Borrador (#56–#58), sin publicar.
- Riesgos/supuestos: caché de B2 a medir en la primera corrida real; carrera de límites aceptada; inmutabilidad de eventos garantizada por código; inyección mitigada, no garantizada (prueba real opcional con OK de costo); reglas de plataforma sin publicar hasta la evaluación de Joaquín; verificación visual pendiente de QA. Deuda preexistente anotada: `Admin licencia-crear` con `string[].Contains` (MH-001).
- Guía QA (sin costo, motor apagado con `MotorAgentes:Habilitado=false` o sin API key): organización con Directora, Empleada en Marketing y Empleado en Contable, áreas Marketing y Contable, clientes Panadería Norte y Ferretería Sur, licencia al rubro con al menos 2 agentes publicados; recorrer CA-M3-01..15 y HU-M3-01..15 según la salida del implementador (vista previa al cambiar el cliente, detalle de tarea con "Cambió después", 403/404 manipulando ids, staff en solo lectura, límites con textos largos, rótulos llanos, Select2 con tags, mobile y tema oscuro).

### 2026-09-14 - qa
- Etapa: QA (M3 Reglas por alcance)
- Cambio: verificación funcional en navegador real (Playwright librería + Chromium; MCP no disponible) con motor apagado: CA-M3-01..15 y HU-M3-01..15 en PASS (CA-M3-13 por test + evidencia de instantánea), máquina de estados de la regla, permisos por alcance (Directora, Empleadas de Marketing/Contable, autor, staff solo lectura), orden de 9 niveles y recálculo al cambiar cliente, instantánea y "Cambió después", bajas de área/cliente y autor bloqueado → "No se aplica", límites por regla y por balde (empresa incluye por agente, cliente incluye cliente + agente), conflicto de edición simultánea, mismo tema por etiquetas, cards en Cartera/Áreas, filtro Cliente en Tareas, núcleo con reglas de plataforma en Borrador y rubro `plataforma` excluido, IDOR contra Org B (404 / "no existe", sin fugas), escape de `</regla>`/comillas. Checklists 25/26/32, mobile 390px, tema oscuro, ortografía y rótulos D-M3-8..12. Regresión M2 y portal por rol. Tareas de QA #7/#8 canceladas; reglas de plataforma sin publicar. `6-qa.md` con sección M3.
- Motivo: etapa 6 de M3 tras la implementación.
- Impacto en capas: ninguno (sin cambios de código; sin auto-fixes).
- Evidencia: scripts `m3-*.js` y capturas `m3-mobile-*`/`m3-dark-*` en el scratchpad de la sesión; consola sin errores JS ni 5xx y log del portal sin ERR; build 0 errores / 0 advertencias; tests 61/61.
- Riesgos/supuestos: 0 defectos. Observaciones: el Director ve el texto de preferencias del autor en el detalle de tarea (coincide con P-M3-05, tensiona CA-M3-06: confirmar con el analista); agente mostrado por slug (dato del núcleo); mensaje de `UsoLimite` con cliente ajeno; "(con esta regla)" con texto vacío; filtros por `keyup`. Pendientes con costo: obediencia real de reglas/inyección, reanudación real (CA-M3-13) y caché de bloques. Veredicto: apto con observaciones.

### 2026-09-14 - documentador
- Etapa: Documentacion (M3)
- Cambio: resumen de entrega `resumen-sprint-m3-reglas.md` (formato 31, rótulos llanos) con pendientes: publicar reglas de plataforma, corrida real con costo, M3b.
- Motivo: cierre de comunicación de M3.
- Impacto en capas: —
- Riesgos/supuestos: OBS-M3-1 queda a decisión de Joaquín.

### 2026-09-14 - presupuestador
- Etapa: Cierre calibracion (M3)
- Cambio: esfuerzo real sin estimado (implementador ~52 min, QA ~28 min); lecciones: cambios de contrato del motor como ítem propio, check constraint del proveedor MySQL como verificación, "validación con modelo real" como ítem explícito en features con prompts.
- Motivo: cierre del flujo de 9 etapas de M3.
- Impacto en capas: —
- Riesgos/supuestos: M3 cerrada.

### 2026-09-14 - analista-funcional
- Etapa: Discovery + Analisis (M3b Seguir conversando sobre una tarea)
- Cambio: M3b analizada: seguimientos del autor sobre tareas terminadas con el mismo agente/cliente/instantánea, vista de conversación, progreso en vivo, costo acumulado, límites (10.000 caracteres, 20 seguimientos), copiar respuesta, última actividad en el listado, compatibilidad con tareas sin instantánea. 5 CU, 10 RF, 14 CA, 4 riesgos, 8 preguntas (incluye OBS-M3-1 como P6).
- Motivo: pedido de Joaquín ("continuar") tras cerrar M3; roadmap M3b.
- Impacto en capas: Presentación (detalle de tarea como conversación, listado), Negocio (re-apertura de tareas, pasos por turno, límites), Datos (tipo de paso de mensaje, última actividad y contador — migración leve).
- Riesgos/supuestos: R-M3b-01 costo creciente por reenvío de conversación; R-M3b-02 reanudación sin duplicar mensajes. Decisiones pendientes de M3 fuera de este análisis: publicar reglas de plataforma y corrida real con costo (requieren OK de Joaquín).

### 2026-09-14 - analista-funcional
- Etapa: Analisis M3b (gate)
- Cambio: Joaquín aprobó con todas las hipótesis: solo el autor sigue la conversación; reglas congeladas con aviso; seguimiento sobre Completada, Fallida y Cancelada; 10.000 caracteres y 20 seguimientos; pasos por turno; ocultar texto de preferencias ajenas al Director (OBS-M3-1); sin compactación; rótulo "Seguir conversando".
- Motivo: cierre del gate Análisis → Diseño de M3b.
- Impacto en capas: Presentación (detalle de tarea), Negocio (permisos de seguimiento, visibilidad de preferencias).
- Riesgos/supuestos: —

### 2026-09-14 - disenador-funcional
- Etapa: Diseno (M3b)
- Cambio: detalle de tarea rediseñado como conversación (hilo de pedido/ajustes/respuestas con pasos plegados, turno activo en vivo, cuadro "Seguir conversando" solo para el autor con contador y ajustes restantes, copiar, aviso de reglas cambiadas, costo acumulado), listado con Mensajes y Última actividad, atajo "Nueva tarea con este agente", preferencias ajenas como contador. 4 ViewModels, mensajes, máquina de estados, permisos, contratos y 10 historias.
- Motivo: diseño implementable de M3b sobre el análisis aprobado.
- Impacto en capas: Presentación (detalle y listado de tareas), Negocio (re-apertura con guardas, reglas cambiadas, suscripción vigente), Datos (mensaje de ajuste, contador y última actividad).
- Riesgos/supuestos: decisiones a validar D-M3b-1 suscripción vencida bloquea, D-M3b-2 cliente dado de baja no bloquea, D-M3b-3 respuesta = texto final del turno, D-M3b-4 orden por última actividad, D-M3b-5 atajo a nueva tarea, D-M3b-6 Ctrl+Enter, D-M3b-7 preferencias ajenas como contador. Nuevo PAT-029.

### 2026-09-14 - disenador-funcional
- Etapa: Diseno M3b (gate)
- Cambio: Joaquín aprobó el diseño con D-M3b-1..7 ("continuar").
- Motivo: cierre del gate Diseño → Arquitectura de M3b.
- Impacto en capas: —
- Riesgos/supuestos: —

### 2026-09-14 - arquitecto-mvc
- Etapa: Arquitectura (M3b)
- Cambio: tipos de paso `MensajeUsuario` y `CierreTurno`; `TareaAgente.CantidadSeguimientos` y `UltimaActividadAt`; `IServicioTareas.EnviarSeguimientoAsync` con re-apertura atómica (token `Version`); normalización de la conversación para la API (resultados sintéticos y fusión de mensajes de usuario); máximo de pasos por turno; caché en el último mensaje; detalle como turnos con `ReglasCambiaronAsync` y preferencias ajenas ocultas; listado con mensajes/última actividad; atajo de nueva tarea con cliente; migración `ConversacionM3b`.
- Motivo: diseño M3b aprobado.
- Impacto en capas: Domain (2 valores de enum, 2 campos), Application (servicio de tareas, DTOs de turnos, opciones, constructor), Infrastructure (servicio, procesador, proveedor, constructor, migración), Web (controller, detalle/conversación, listado, JS).
- Riesgos/supuestos: RT-M3b-01 reglas de alternancia de la API (alto, cubierto por normalización y tests), RT-M3b-02 costo creciente, RT-M3b-03 ventana de contexto sin compactación, RT-M3b-06 QA sin costo no ve respuestas → propuesta de proveedor simulado solo en Development (requiere aprobación). PAT-029 ampliado.

### 2026-09-14 - orquestador
- Etapa: Arquitectura M3b (gate) + definición de producto
- Cambio: Joaquín aprobó la arquitectura de M3b (CierreTurno, normalización de conversación, caché en el último mensaje, pasos por turno, proveedor simulado solo en Development). Presupuesto omitido. Se lanza Implementación. Además definió dos formas de uso: tareas individuales y tareas repetitivas programadas; se mantiene M12 al final del roadmap (camino A) con reglas vigentes por ejecución y dependencias M5/M6/M10/M11, documentado en `docs/diseno-organizacion-roles-reglas.md`.
- Motivo: gate Arquitectura → Implementación de M3b; consulta de Joaquín sobre automatización periódica.
- Impacto en capas: —
- Riesgos/supuestos: la elección del camino A se tomó del "ok" de Joaquín a la propuesta recomendada; revertible si pide el camino B.

### 2026-09-14 - implementador
- Etapa: Implementacion (M3b Seguir conversando sobre una tarea)
- Cambio: pasos `MensajeUsuario`/`CierreTurno`; `TareaAgente.CantidadSeguimientos`/`UltimaActividadAt`; `EnviarSeguimientoAsync` con re-apertura en un solo guardado (token `Version`); normalización de la conversación (resultados sintéticos, fusión de mensajes, cierres fuera del modelo, thinking intacto); pasos por turno; cierre de turno en todo fin Fallida y al cancelar; caché en el último mensaje; detalle como conversación con cuadro "Seguir conversando", copiar y refresco en vivo reiniciable; aviso de reglas cambiadas; preferencias ajenas ocultas; listado con Mensajes y Última actividad; modelo simulado solo en Development. Migración `ConversacionM3b` aplicada en dev. PAT-029 completado con rutas reales.
- Motivo: arquitectura M3b aprobada (presupuesto omitido).
- Impacto en capas: Domain (2 valores de enum, 2 campos), Application (contrato de tareas, DTOs de turnos, opciones, constructor), Infrastructure (servicio, procesador, proveedores, constructor, migración), Web (controller, 4 vistas de tareas, reglas, CSS, config).
- Evidencia: build 0 errores (1 advertencia preexistente); tests 83/83 (61 + 22 nuevos); SQL real (columnas, índice usado por el listado, backfill 7/7, 1062 por `Numero` repetido, 0 restos); EF → MySQL 37 pasos OK con el modelo simulado, incluida la reversión real del doble envío; 0 restos.
- Riesgos/supuestos: caché y detección de prompt largo sin validar con la API real; `Cancelar` en la línea de estado del hilo (se actualiza en vivo) en vez del encabezado; InMemory no transaccional (la atomicidad se validó en MySQL). Decisiones DI-M3b-1..13 en `5-implementador.md`.
- Guía de verificación manual para QA (sin costo):
  0. Activar el modelo simulado: `$env:Anthropic__Simulado = "true"; dotnet run --project src/OlvidataAgentes.Web --launch-profile https` (el perfil ya usa `ASPNETCORE_ENVIRONMENT=Development`), o `dotnet user-secrets set "Anthropic:Simulado" "true" --project src/OlvidataAgentes.Web`. En la consola debe aparecer la advertencia "Motor de agentes con MODELO SIMULADO". Desactivar: quitar la variable o `dotnet user-secrets remove "Anthropic:Simulado"`. Con cualquier otro entorno la opción se ignora (advertencia en el log).
  1. Laura (Empleada) crea una tarea con el CM: el detalle muestra "En cola…" / "Trabajando · paso 1 de hasta 25" y luego "Respuesta simulada al turno 1."; debajo, el cuadro "Seguir conversando" con placeholder "Pedile un ajuste: más corto, otro tono, agregá…", contador "0 / 10.000" y "Quedan 20 ajustes en esta conversación."
  2. Escribir un ajuste con saltos de línea (Enter no envía) y enviar con Ctrl+Enter: aparecen la burbuja "Ajuste" y "En cola…" sin recargar, el textarea queda deshabilitado con "Esperá la respuesta para seguir.", llega "Respuesta simulada al turno 2." con scroll al último mensaje, línea "2 mensajes · … tokens · USD 0 en total", "Quedan 19 ajustes".
  3. Validaciones: enviar vacío → toast "Escribí tu mensaje."; pegar más de 10.000 caracteres → contador en rojo y toast "El mensaje admite hasta 10.000 caracteres."
  4. "Copiar" en una respuesta → toast "Respuesta copiada." y pegar en otro lado.
  5. Enviar un ajuste y cancelarlo mientras está en cola (confirmación "¿Cancelar esta respuesta? La conversación anterior se conserva.") → nota "Cancelaste esta respuesta."; volver a enviar un ajuste desde la tarea Cancelada.
  6. Paula (Directora) abre la tarea de Laura: sin cuadro, nota "Solo quien pidió la tarea puede seguir esta conversación.", "Pedida por Laura…", y en "Lo que el agente tuvo en cuenta" las preferencias de Laura solo como "Preferencias personales de … (N reglas)". POST forzado a `/Tareas/EnviarSeguimiento` (tareaId, texto, token) → 403 con el mensaje. Martín (Empleado ajeno) y la Directora de otra organización → 404 en detalle y POST.
  7. Límite: `UPDATE TareasAgente SET CantidadSeguimientos = 20 WHERE Id = <id>;` → alerta "Esta conversación llegó al máximo de 20 ajustes." con "Nueva tarea con este agente" (abre Nueva tarea con agente y cliente precargados).
  8. Suscripción vencida: revocar la licencia de la organización → alerta "Tu organización no tiene la suscripción vigente para este agente." sin cuadro; la conversación se sigue leyendo. Restaurar.
  9. Reglas cambiaron: el Director edita o desactiva una regla aplicada → Laura ve el aviso info con "Empezar una tarea nueva"; el siguiente ajuste sigue usando las reglas de la instantánea.
  10. Listado de Tareas: columnas Mensajes y Última actividad, orden inicial por última actividad desc, filtro Mensajes (Todas / Solo el pedido / Con ajustes) y rango de Última actividad, búsqueda global por fecha y por número de mensajes, persistencia al volver y "Limpiar filtros".
  11. Tareas viejas de dev (#1–#7, sin instantánea o canceladas antes de M3b): admiten ajuste; la cancelada muestra "Se canceló esta respuesta." en su turno.
  12. Reinicio: enviar un ajuste, detener el portal mientras está "En cola…" y volver a levantarlo → el turno se responde una sola vez, sin duplicar el ajuste.
  13. Mobile (cuadro fijo al pie) y tema oscuro (burbujas, alertas, badges).

### 2026-09-14 - qa
- Etapa: QA (M3b Seguir conversando sobre una tarea)
- Cambio: verificación por navegador real (Playwright librería desde Node; MCP `playwright` no disponible en la sesión) con el modelo simulado en Development (costo cero; advertencia confirmada en cada arranque y clave de API inválida en el proceso como resguardo). 14/14 CA-M3b y 10 HU en PASS, más D-M3b-1/2 y la máquina de estados (Completada/Fallida/Cancelada → Pendiente, fallo por máximo de pasos, cancelación por autora y por Directora, reinicio del portal a mitad de turno con reanudación al vencer el lease sin duplicar el ajuste). IDOR: 20 combinaciones → 404. Listado con Mensajes y Última actividad (filtros, orden por defecto, Session, Limpiar, búsqueda), mobile con cuadro sticky, regresión M3/M2 y portal por rol sin fallas. Defecto QA-M3b-01 (minor): alertas `.ov-alert` y badge "Ajuste" ilegibles en tema oscuro → ítem nuevo OLV-002 en `docs/qa/regresiones-manuales.yml` y auto-fix en `src/OlvidataAgentes.Web/wwwroot/css/site.css` (contraste 1,5–2,6 → ≥ 6,7; tema claro sin cambios; cierra OBS-4 de M2).
- Motivo: etapa 6 del flujo sobre la implementación M3b.
- Impacto en capas: Web (CSS de tema oscuro). Sin cambios de lógica, datos ni migraciones.
- Evidencia: build 0 errores / 0 advertencias; tests 83/83 antes y después del auto-fix; scripts y capturas `m3b-*` en el scratchpad de la sesión; portal detenido; ninguna tarea Pendiente/EnCurso; licencia, reglas 16/21, `MaxPasos` y costo de #14 restaurados.
- Riesgos/supuestos: OBS-M3b-1 reanudación tras reinicio espera el lease (hasta 5 min, heredado de M1); OBS-M3b-3 `ReglasCambiaronAsync` sin protección en el detalle (CRM-020); calidad real del ajuste, caché del historial y error de conversación demasiado larga pendientes de la corrida paga. Veredicto: apto con observaciones. Detalle en `definiciones/6-qa.md` (M3b).

### 2026-09-14 - documentador
- Etapa: Documentacion (M3b)
- Cambio: resumen de entrega `resumen-sprint-m3b-conversacion.md` (formato 31) con pendientes: corrida real con costo, recuperación tras reinicio hasta 5 min, adjuntos en M5; próximo paso M4.
- Motivo: cierre de comunicación de M3b.
- Impacto en capas: —
- Riesgos/supuestos: —

### 2026-09-14 - presupuestador
- Etapa: Cierre calibracion (M3b)
- Cambio: esfuerzo real sin estimado (implementador ~37 min, QA ~32 min); lecciones: proveedor simulado desde el inicio en features del motor, normalización con tests antes de UI, contraste en tema oscuro al checklist del implementador, atomicidad probada contra MySQL (InMemory no transaccional).
- Motivo: cierre del flujo de 9 etapas de M3b.
- Impacto en capas: —
- Riesgos/supuestos: M3b cerrada.

### 2026-09-14 - orquestador
- Etapa: Pendientes abiertos
- Cambio: por decisión de Joaquín los pendientes quedan abiertos y se continúa con la siguiente etapa; registrados como PA-01..PA-07 en `metadata.md` (reglas de plataforma sin publicar, corrida real con costo, reanudación tras reinicio, protección de `ReglasCambiaronAsync`, deuda de M2, mejoras menores, AlwaysRunning).
- Motivo: "dejar pendientes en estado abierto y continuar con la siguiente etapa de implementación".
- Impacto en capas: —
- Riesgos/supuestos: PA-02 y PA-03 conviene cerrarlos antes de producción.

### 2026-09-14 - analista-funcional
- Etapa: Discovery + Analisis (M4 Agentes de la organización)
- Cambio: M4 analizada: agentes creados desde un agente base (instrucciones, herramientas acotadas, visibilidad personal/organización, área destino), versiones propias, propuestas del Empleado con aprobación del Director, catálogo unificado, nivel 6 del contexto y reglas por agente de la organización, archivar/reactivar, duplicar, mecanismo de rubro incluido siempre y de reglas sugeridas por rubro (sin contenido), lectura de staff. 11 CU, 15 RF, 15 CA, 4 riesgos, 11 preguntas.
- Motivo: siguiente etapa del roadmap tras M3b.
- Impacto en capas: Presentación (catálogo, alta/edición de agentes, propuestas, sugerencias), Negocio (versiones y aprobación, contexto nivel 6, licencias con rubro incluido), Datos (agentes, versiones, referencias en tareas y reglas, sugerencias — migración).
- Riesgos/supuestos: R-M4-01 inyección vía instrucciones; R-M4-02 cambios del agente base impactan derivados; relevado que no existe rubro "negocio" ni inclusión automática en licencias; contenido de rubro fuera de alcance (regla template antes que rubros).

### 2026-09-14 - analista-funcional
- Etapa: Analisis M4 (gate)
- Cambio: Joaquín aprobó con todas las hipótesis P1–P11 (última versión publicada del base; personales privados; reglas del base aplican a derivados; límites 8.000/50/10; edición de Empleado vuelve a revisión; rubro "negocio" y sugerencias solo como mecanismos; casillas de herramientas; modelo heredado; duplicar; ajustes permitidos con agente archivado).
- Motivo: cierre del gate Análisis → Diseño de M4.
- Impacto en capas: —
- Riesgos/supuestos: —

### 2026-09-14 - disenador-funcional
- Etapa: Diseno (M4)
- Cambio: catálogo por secciones (De tu área, De la empresa, Mis agentes, De Olvidata), formulario único de agente con cards, detalle con historial y reglas del agente, bandeja de propuestas y revisión lado a lado con motivo de rechazo, notificaciones, pestaña "Sugerencias de Olvidata" para el Director, ajustes en nueva tarea/reglas/detalle de tarea, vistas de staff, rubro incluido en núcleo y licencias. 8 ViewModels, mensajes, máquina de estados de versión, permisos, contratos y 14 historias.
- Motivo: diseño implementable de M4 sobre el análisis aprobado.
- Impacto en capas: Presentación (catálogo, agentes, propuestas, sugerencias), Negocio (versiones con aprobación, nivel 6, sugerencias, rubro incluido), Datos (agentes, versiones, sugerencias, referencias).
- Riesgos/supuestos: decisiones a validar D-M4-1..10 (formulario único, estados en palabras, botones por caso, bandeja de propuestas, revisión lado a lado, catálogo por secciones, notificaciones, reglas solo para agentes de la empresa, sugerencias como pestaña, rubro incluido desde manifiesto). Reutilización: pantallas de M3, vista previa, versiones del núcleo, notificaciones. Nuevo PAT-030.

### 2026-09-14 - disenador-funcional
- Etapa: Diseno M4 (gate)
- Cambio: Joaquín aprobó D-M4-1..3 y D-M4-6..10 y pidió saltear "En revisión del Director" por ahora; eligió que el Empleado publique directo para toda la empresa. Se quitan propuestas y revisión (P-M4-04/05, D-M4-4/5), la versión queda Borrador → Publicada → Reemplazada, edición de agentes de la empresa por creador y Director, y notificación a Directores cuando se publica o actualiza un agente de la empresa.
- Motivo: cierre del gate Diseño → Arquitectura de M4.
- Impacto en capas: Presentación (sin bandeja ni revisión), Negocio (sin estados de aprobación; permisos de edición/archivo), Datos (versión sin estados de revisión).
- Riesgos/supuestos: menos control sobre lo que se comparte; mitigado con aviso a Directores y archivo. La revisión del Director queda como mejora posterior.

### 2026-09-14 - arquitecto-mvc
- Etapa: Arquitectura (M4)
- Cambio: `AgenteOrganizacion` (nombre/descripción no versionados, proyección de lo publicado, `VersionToken`, `NombreVigente` STORED) y `AgenteOrganizacionVersion` (borrador único → publicada → reemplazada); `IAgenteOrganizacionService` (catálogo, guardar con acción, duplicar, crear desde, archivar/reactivar, staff); tareas con agente de la empresa (base última publicada, herramientas por intersección, instantánea extendida compatible); instrucciones del derivado antes de reglas "Por agente" y reglas por agente de la empresa (`Regla.AgenteOrganizacionId`, check recreado); sugerencias `TipoArtefacto.ReglaSugerida` + activación; `Rubro.IncluidoSiempre` al crear licencias + comando `sincronizar-rubros-incluidos`; notificación a Directores; migración `AgentesOrganizacionM4`.
- Motivo: diseño M4 aprobado sin revisión del Director.
- Impacto en capas: Domain (2 entidades, 2 enums, campos en regla/tarea/rubro/artefacto), Application (servicio, opciones, DTOs, constructor, licencias, reglas), Infrastructure (servicios, constructor, procesador, importador, licencias, configs, migración), Web (Agentes rediseñado, Reglas/Sugerencias, staff, núcleo, licencias).
- Riesgos/supuestos: RT-M4-01 compatibilidad del hash de tareas existentes (alto, test golden), RT-M4-02 recrear check constraint en MySQL, RT-M4-03 publicación sin revisión. Reuso literal: ReglaService/vistas M3, columnas generadas M2, constructor M3, importador, notificaciones, tareas M3b. PAT-030 actualizado.

### 2026-09-14 - presupuestador
- Etapa: Arquitectura M4 (gate) + Presupuesto (omitido)
- Cambio: Joaquín aprobó la arquitectura de M4 ("continuar"): nombre/descripción no versionados, borrador único, instantánea extendida compatible, instrucciones antes de reglas por agente, sugerencias como artefactos del núcleo, rubro incluido al crear licencias + sincronización. Presupuesto omitido. Se lanza Implementación.
- Motivo: gate Arquitectura → Implementación de M4.
- Impacto en capas: —
- Riesgos/supuestos: —

### 2026-09-14 - implementador
- Etapa: Implementacion (M4 Agentes de la organización, sin revisión del Director)
- Cambio: entidades `AgenteOrganizacion` (proyección de lo publicado, `VersionToken`, `NombreVigente` STORED) y `AgenteOrganizacionVersion` (borrador único → publicada → reemplazada); `AgenteOrganizacionService` (catálogo por secciones, permisos creador/Director, límites 8.000/50/10, nombre único, publicar con aviso a Directores, duplicar, crear mi versión, archivar/reactivar, staff); tareas con agente de la empresa (base = última publicada, formato de contexto 2 con `<instrucciones_de_la_empresa>` entre reglas del cliente y "Por agente", herramientas por intersección, P11); reglas por agente de la empresa (check recreado) y "No se aplica" con agente archivado; sugerencias de Olvidata (`TipoArtefacto.ReglaSugerida`, pestaña del Director, activar con origen Sugerida); `incluido_siempre` en manifiestos, rubros incluidos al emitir licencias y comando `sincronizar-rubros-incluidos`; vistas de agentes, sugerencias, staff, núcleo y licencias. Migración `AgentesOrganizacionM4` aplicada en dev. PAT-030 completado con rutas reales (notas de M3b movidas a PAT-029). Sin contenido real de rubros ni sugerencias.
- Motivo: arquitectura M4 aprobada (presupuesto omitido).
- Impacto en capas: Domain (2 entidades, 2 enums, campos en regla/tarea/rubro/artefacto), Application (servicio, DTOs, opciones, constructor, tareas, reglas, licencias), Infrastructure (servicio nuevo, constructor, tareas, procesador, reglas, importador, catálogo, licencias, configuraciones, migración), Web (Agentes rediseñado, Reglas/Sugerencias, Tareas, Clientes/Agentes, Núcleo, licencias, CSS), Admin (comando).
- Evidencia: build 0 errores (1 advertencia preexistente); tests 100/100 (83 + 17 nuevos, incluido el golden de hash de tareas existentes calculado con el código previo); SQL real en transacción revertida (STORED, check, FKs, 1062/1406/3819/1452/1451 esperados, datos existentes intactos, 0 restos); EF → MySQL 62 pasos OK con el modelo simulado, incluida la `DbUpdateConcurrencyException` real por `VersionToken`, sin errores MH-001 y 0 restos.
- Riesgos/supuestos: inyección por instrucciones sin validación con el modelo real (PA-02); instrucciones del derivado en el bloque no cacheado; URL relativa en el aviso; sección "Archivados" del catálogo agregada (DI-M4-7, a validar); carreras aceptadas en límites y activación de sugerencias. Decisiones DI-M4-1..21 en `5-implementador.md`.
- Guía de verificación manual para QA (sin costo):
  0. Modelo simulado: `$env:Anthropic__Simulado = "true"; dotnet run --project src/OlvidataAgentes.Web --launch-profile https` (advertencia "MODELO SIMULADO" en consola). Datos de prueba: publicar al menos un agente de Olvidata con licencia vigente para la organización (ya existe `inmobiliario/inmo-cm` en dev) y tener Laura (Empleada, Marketing), Martín (Empleado, otra área) y la Directora.
  1. Laura → Agentes: encabezado "Agentes", buscador, secciones "Mis agentes" (vacía: "Todavía no creaste agentes…") y "De Olvidata · <rubro>". En una card de Olvidata → menú ⋮ → "Crear mi versión": formulario con el agente base elegido, su descripción y sus herramientas; contador "0 / 8.000"; "Solo yo" → botón "Guardar y usar".
  2. Crear "Mis mails formales" (Solo yo) → "Agente listo para usar." y lleva a Nueva tarea con "· basado en …"; en "Esto es lo que el agente va a tener en cuenta" aparece "Instrucciones de Mis mails formales" (antes de las reglas "Por agente"). Enviar la tarea y abrir el detalle: "Tarea #N · Mis mails formales (versión 1)", "Basado en …", y en "Lo que el agente tuvo en cuenta" las instrucciones v1. Seguir conversando funciona.
  3. Martín y la Directora: el agente no aparece en su catálogo; `/Agentes/Detalle/<id>` y `/Agentes/Ejecutar?agenteOrganizacionId=<id>` → 404.
  4. Laura crea "CM del estudio" con "Toda la empresa" y área destacada Marketing → botón "Publicar para la empresa" → "Agente publicado para toda la empresa."; la Directora recibe en la campana "Laura … publicó «CM del estudio» para toda la empresa." con enlace al detalle; Laura lo ve en "De tu área «Marketing»", Martín en "De la empresa" con "Usar" y "Crear mi versión" (sin Editar/Archivar).
  5. Validaciones: nombre repetido (también con otras mayúsculas/tildes) → "Ya hay un agente activo con ese nombre en tu empresa."; instrucciones de más de 8.000 → "Las instrucciones admiten hasta 8.000 caracteres."; POST manipulado con una herramienta que el base no tiene → "Esa herramienta no está disponible en el agente de Olvidata elegido."; 11.º personal → "Llegaste al máximo de 10 agentes personales…".
  6. Versiones: Laura edita "CM del estudio", cambia instrucciones y "Guardar borrador" → detalle con card "Borrador (versión 2)" (Martín no la ve) y badge "Borrador pendiente" en el catálogo; publicar → historial v1 Reemplazada / v2 Publicada; la tarea previa sigue mostrando versión 1. Abrir Editar en dos pestañas y guardar en ambas → "Otra persona modificó este agente mientras lo editabas…". Publicar sin cambios → "Datos guardados. Las instrucciones no cambiaron…".
  7. Permisos: la Directora edita y archiva "CM del estudio" (confirmación "¿Archivar «CM del estudio»? Deja de aparecer…"); Martín → POST a `/Agentes/Archivar` → 403. Archivado: fuera de "De la empresa", visible en "Archivados" (plegado) para Laura y la Directora con "Reactivar"; la tarea existente admite ajustes y muestra "Agente archivado" sin "Nueva tarea con este agente". Reactivar lo devuelve.
  8. Duplicar (menú ⋮ o detalle) → "Copia creada como borrador." y abre Editar de "Copia de …" (personal, mismas instrucciones y herramientas).
  9. Reglas: la Directora → Reglas → Nueva regla "Por agente": el combo tiene "De Olvidata · <rubro>" y "De la empresa"; crear una para "CM del estudio" → aparece en la pestaña "Por agente" con el nombre, filtrable, y en la card "Reglas de este agente" del detalle ("Nueva regla para este agente" y "Ver todas"). Archivar el agente → la regla queda "No se aplica" (motivo "El agente de la empresa fue archivado.").
  10. Sugerencias (datos de prueba): importar un rubro de ejemplo con `reglas_sugeridas` (ver `_plantilla/rubro.yml`), evaluar y publicar la sugerencia, licenciar el rubro. Directora → Reglas → pestaña "Sugerencias de Olvidata": card con etiquetas; "Activar en un área" → modal con Área* y "Salvo que se indique otra cosa" tildado → "Regla activada." → badge "Ya activada" con "Ver la regla" (detalle con "Origen: Sugerida por Olvidata"). Empleado: la pestaña no aparece; POST forzado a `/Reglas/ActivarSugerencia` → 403. Una sugerencia en borrador no se ve.
  11. Rubro incluido (datos de prueba): manifiesto con `incluido_siempre: true` → importar → Núcleo IP → rubro con badge "Incluido en todas las suscripciones"; Organizaciones → detalle → "Nueva licencia": la casilla del rubro tildada y deshabilitada con "Se incluye en todas las suscripciones."; la licencia emitida lo trae. `dotnet run --project src/OlvidataAgentes.Admin -- sincronizar-rubros-incluidos` lo agrega a las vigentes (segunda corrida: 0). Deshacer los datos de prueba al terminar.
  12. Suscripción vencida: revocar la licencia → card atenuada con "Este agente no está disponible: la suscripción a <rubro> no está vigente.", sin "Usar"; Editar permite "Guardar borrador" pero no publicar; ajuste de una tarea → "Tu organización no tiene la suscripción vigente para este agente.". Restaurar.
  13. Staff (SuperUsuario) → Organizaciones → detalle → "Agentes": grilla con filtros por Agente, Basado en, Quién lo usa, Estado y Creado por, búsqueda global, Session y "Limpiar filtros"; detalle en solo lectura con instrucciones y borrador.
  14. Listado de Tareas: filtro Agente con el agente de la empresa; la columna muestra su nombre; el filtro del agente de Olvidata no incluye las tareas de sus derivados.
  15. Mobile y tema oscuro: cards, dropdown ⋮, badges neutros y etiquetas (bg-light), barra sticky del formulario, modal de sugerencias (cruz visible, Select2 dentro del modal) y texto "No disponible".

### 2026-09-14 - documentador
- Etapa: Documentacion (M4)
- Cambio: resumen de entrega `resumen-sprint-m4-agentes.md` (formato 31) con pendientes: revisión del Director pospuesta, contenido del rubro de negocio y sugerencias reales, pendientes abiertos PA-01..07; próximo paso M4b.
- Motivo: cierre de comunicación de M4.
- Impacto en capas: —
- Riesgos/supuestos: sección "Archivados" y aviso a la autora ante ediciones del Director quedan a decisión de Joaquín.

### 2026-09-14 - presupuestador
- Etapa: Cierre calibracion (M4)
- Cambio: esfuerzo real sin estimado (implementador ~70 min / 300 acciones, QA ~39 min); lecciones: features que integran entidad nueva + versiones + constructor/tareas/reglas/núcleo/licencias equivalen a varias features; test golden de hash obligatorio en cambios del constructor; verificación de contraste en tema oscuro al checklist del implementador (tercera ocurrencia).
- Motivo: cierre del flujo de 9 etapas de M4.
- Impacto en capas: —
- Riesgos/supuestos: M4 cerrada.

### 2026-09-14 - presupuestador
- Etapa: Arquitectura M4b (gate) + Presupuesto (omitido)
- Cambio: Joaquín aprobó la arquitectura de M4b ("si", puntos 1–7). Presupuesto omitido. Se lanza Implementación.
- Motivo: gate Arquitectura → Implementación de M4b.
- Impacto en capas: —
- Riesgos/supuestos: —

### 2026-09-24 — implementador-dotnet (ajustes post-QA de M18)

- Etapa: Implementación (M18, dos ajustes decididos por Joaquín sobre lo que QA dejó abierto). Base: los 4 fixes de QA (`974edb5`, `aacfe0a`, `6df04a9`, `1915a54`).
- **Ajuste 1 (`3bb0596`) — la consulta del cliente no ve la cocina del estudio.** QA verificó con datos reales que **una regla interna sobre honorarios quedó delante del agente al que le pregunta el propio cliente**. En una `ConsultaCliente` el contexto se arma ahora solo con las reglas de alcance **Cliente** de ese cliente; quedan afuera las de la empresa, del área, del usuario y del agente.
- **Hallazgo propio, la misma fuga un renglón más abajo:** la **nota de memoria** viaja en los mensajes con el título y el «cuándo sirve» de cada recuerdo, así que un hecho de la empresa («se cobra el 3 % del facturado») llegaba igual a la consulta. Se cerró con la misma condición; RF-M18-27 ya decía «recuerdos suyos».
- **Ajuste 2 (`170a016`) — el agente lee exactamente lo que el cliente ve.** Las herramientas de documentos de una `ConsultaCliente` devuelven el mismo conjunto que «Mis documentos»: lo del cliente (siempre) más lo marcado con «Lo ve el cliente». **Esto cambia lo que decía el §3.3 del diseño** («la carpeta del cliente» entera), a sabiendas: se eligió coherencia total y cero sorpresas a costa de respuestas peores cuando el estudio se olvide de marcar un documento.
- **Documentación alineada con el código, con fecha y motivo:** `docs/diseno-portal-cliente.md` §3.3 (tabla de tres filas: reglas, recuerdos, documentos) y RF-M18-27 de `1-analista-funcional.md`.
- **Evidencia:** build `0 Errores`; `dotnet test` medido sin pipe de **891/891** a **`Con error: 0, Superado: 896, Omitido: 0, Total: 896`**. Los 5 goldens de hash, **sin un cambio**: la condición nueva solo se activa con `TipoTarea.ConsultaCliente`. Los 5 tests nuevos se verificaron **en rojo** neutralizando los arreglos antes de darlos por buenos.
- **Choque de trabajo concurrente, sin resolver a propósito:** un `git add` de otro proceso levantó los **7 archivos de código del Ajuste 1** dentro del commit `437c41f` («Lo que encontró la evaluación real de los tres agentes»), que por su mensaje solo debería traer los 5 de `nucleo/`. No se reescribió ese commit porque no es del implementador; el detalle de qué archivos sacar está en el mensaje de `3bb0596`. Decisión de Joaquín si lo divide.
- **Nada de lo de QA se pisó:** los 4 fixes siguen en pie. El Ajuste 2 se apoya en `6df04a9` (sin él el bloque de consultas era inerte) y lo acota, sin tocar la guarda de aislamiento que QA escribió.
- Sin push y sin deploy: los hace Joaquín.

### 2026-09-24 — cierre de calibracion (M18)

- Etapa: Cierre. **Sin presupuesto previo** (proyecto personal): no hay ratio PERT/real posible. Se registra en `docs/calibracion/dataset.yml` → `cierres_agentic` como dato duro.
- Medido: **288,2 minutos de agente** (implementación E1–E5 78,9 · QA 57,4 · ajustes post-QA 151,9), ~1,2 h de orquestación humana no cronometrada, **1.834.465 tokens de subagente**, tests **747 → 896 (+149)**, 11 commits locales.
- Segunda fila con dato duro de la familia «entrega 100 % agéntica»: con la de crm-olvidata son 2, falta 1 para el umbral de 3 que dejó pedido marihogar antes de usarla para calibrar.
- **Aprendizaje (a):** la corrida de ajustes post-QA **costó más que implementar el módulo entero** (151,9 min contra 78,9). Las dos decisiones que la motivaron eran de contexto del modelo —qué reglas y qué documentos ve el agente del cliente— y una de ellas ya estaba escrita en el análisis. Para el próximo: esas preguntas se cierran **antes** de implementar, no después de QA.
- **Aprendizaje (b):** QA encontró 4 defectos que 891 tests verdes no veían, tres solo visibles en el navegador con una sesión real, incluido uno crítico (el agente del cliente no podía leer un solo documento y lo disimulaba en castellano). En un módulo de frontera, el QA con navegador no es opcional.
- Estado final: **aprobado con reparos**, los reparos arreglados. 896/896, build limpio, los 5 goldens sin un byte de cambio. **Sin push y sin deploy.**
- Pendiente de decisión de Joaquín: el commit `437c41f` («Lo que encontró la evaluación real de los tres agentes») se llevó 7 archivos de código de M18 que otra sesión barrió con un `git add`; el mensaje solo describe los 5 de `nucleo/`. No se reescribió porque el commit es de otra sesión. Es higiene de historial local, no correctitud.

### 2026-09-24 — despliegue a produccion (M18)

- Autorizado por Joaquín. `git push origin main`: **17 commits** a GitLab (`44053ff..170a016`) — los 11 de M18 más los de la sesión paralela sobre `nucleo/plataforma`.
- `./scripts/deploy-prod.ps1 -Force`: migraciones aplicadas contra la base de producción (incluye `PortalCliente`), publicación Release, 10 archivos sincronizados por Web Deploy (12,1 MB), **`/health/vivo` 200**.
- Verificación posterior en producción: `/Account/Login` 200 · **`/acceso` 404** — el portal de clientes arranca **apagado en todas las organizaciones**, que es exactamente RF-M18-06: hasta que un Director lo prenda, estas pantallas no existen para nadie.
- **No se reimportó `nucleo/plataforma`**: los cambios de la sesión paralela sobre los prompts de los tres agentes de configuración viajaron en el push pero **no están publicados** en producción (requieren `publicar-rubro` con evaluación aprobada, `IVersionadoService`). Es trabajo de esa sesión, no de M18.
- Pendiente de decisión: el commit `437c41f` mezcla 5 archivos de `nucleo/` con 7 de código de M18 que otra sesión barrió con un `git add`. Ya está pusheado; reescribirlo ahora sería reescribir historia publicada. **Se deja como está.**

### 2026-09-25 — implementador (M20)

- Etapa: Implementación. Commit local único `b551010` sobre `5e69afe`. **Sin push y sin deploy**: los hace el orquestador
  después de QA.
- Cambio: **el agente hace la cuenta en vez de escribir el número.** Herramienta `calcular` con lista de cuentas, nombre
  opcional y encadenado por nombre dentro de la misma llamada; evaluador propio por descenso recursivo en `decimal`
  (`+ - * / ( )`, unario, `%` sufijo, `SUMA PROMEDIO MIN MAX CONTAR ABS REDONDEAR`, `;` entre argumentos); el paso en
  palabras «Calculó: neto = 1.234,50 · iva = 259,25 · total = 1.493,75» con la cuenta entera en el detalle plegado; se
  ofrece en toda tarea de trabajo, con cliente o sin él, y no pide aprobación. La heurística de «número escrito por una
  persona» de M19 se mudó a `Application/Helpers/NumeroEscrito.cs` y quedó **compartida**.
- Motivo: el modelo no calcula, predice. Es el agujero más caro del producto en un rubro contable, porque un número mal
  no se ve mal (análisis M20, D-M20-a..e).
- Impacto en capas: Application (evaluador, helper compartido, opciones, mensajes, nombres y rótulo llano),
  Infrastructure (herramienta, resumidor de pasos, resolvedor, DI, el generador de M19 que ahora llama al helper), Web
  (un texto de condición en la ficha del agente y la sección `Calculo` de `appsettings.json`). **Datos: sin entidades y
  sin migración.**
- Riesgos/supuestos: **los 5 goldens de contexto quedaron sin un byte de cambio** (R-T-06: las herramientas viajan en la
  lista de la solicitud, no en el prompt de sistema) y **los tests de M19 quedaron verdes sin tocarlos** (R-T-03). Cada
  test nuevo se verificó **en rojo** con tres tandas de mutaciones antes de darlo por bueno. Evidencia medida sin pipe:
  **907 → 985 tests**, build `0 Errores`.
- **Tres cosas que el criterio decía mal, corregidas en la documentación y no en silencio:** (1) CA-M20-01 afirma que en
  `double` esa cuenta daría 259,24499999999997 — da 259,2450000000000045 y redondea igual; el caso que sí rompe es
  acumular (diez veces 0,10 da 0,9999999999999999) y ése quedó en el test; (2) el tope de 1.000 números por función de
  RF-M20-07 es inalcanzable con 500 caracteres por expresión; (3) compartir la heurística de M19 (RF-M20-03) implica que
  un número con exactamente tres cifras detrás de la coma se lee como **miles** (`1234,567` no es 1234 con tres
  decimales), lo que quedó documentado en la descripción que lee el modelo y fijado en la tabla de casos.
- **Defecto viejo arreglado de paso (DI-M20-G):** la ficha del agente mostraba «en tareas principales» para la condición
  `TodaTareaDeTrabajo`, que venía sin brazo en `AgentesTextos.Condicion` desde M17 (memoria). Queda igual
  `PortalDeClientesEncendido` (M18), que cae al mismo texto por defecto: anotado para quien tome ese módulo.

### 2026-09-25 — implementador (M21)

- Etapa: Implementación. Commit local único `2acfa4f` sobre `b551010`. **Sin push y sin deploy**: los hace el orquestador
  después de QA.
- Cambio: **el agente mira un PDF escaneado.** Un PDF del que no se extrajo ni una letra queda
  `EstadoLecturaDocumento.SeMira` si entra en los topes (20 páginas, 10 MB) y sale hacia la API como **bloque de
  documento** (`BetaRequestDocumentBlock` + `BetaBase64PdfSource`) en vez de bloque de imagen; si no entra, sigue
  `NoLegible` pero **con el motivo exacto** («es un escaneado de 60 páginas y el máximo para mirar es 20»). El tope por
  conversación pasó a contarse **por tipo** (8 imágenes y 2 escaneados, en dos cuentas separadas). Los cinco textos que
  decían «imagen» hablan del archivo, y el paso se lee «Miró «Extracto marzo.pdf» (4 páginas)».
- Motivo: era el formato más común de lo que manda un cliente —el extracto, la factura fotocopiada— y hasta acá no
  existía para la tarea (análisis M21, D-M21-a..d; diseño D-M21-e).
- Impacto en capas: Application (topes en `DocumentosOptions`, mensajes de subida y de motivo, `MensajesOjos` con
  variante de archivo, `EsPdf` en `ImagenParaMirar` y `BloqueImagenDocumento`, `Paginas` en `BloqueImagenDatos`,
  `TextoLectura`), Infrastructure (`ExtractorPdf`, `ImagenesParaModelo`, `ProveedorModeloAnthropic`,
  `ProcesadorTareas.RehidratarImagenesAsync`, `HerramientasDocumentos`, `DocumentoCarteraService`), Web (tooltip y la
  pantalla del documento, tres claves en `appsettings.json`). **Datos: sin entidades y sin migración.**
- Riesgos/supuestos: **los 5 goldens quedaron sin un byte de cambio** y **los tests de M16 quedaron verdes sin tocarlos**
  (R-T-06, R-T-05 resuelto por el compilador y no adivinando el tipo del SDK). El tope por tipo (R-T-04) tiene test
  dedicado con escaneados y fotos mezclados. Evidencia medida sin pipe: **985 → 994 tests**, build `0 Errores`. Cada
  test nuevo verificado **en rojo** (apagar la rama del extractor deja 7 rojos; contar el tope junto y mandar el PDF como
  imagen, 2).
- **Dos cosas que el criterio decía distinto, resueltas a la vista:** (1) RF-M21-06 pide que el estado se lea «El agente
  lo mira (escaneado, N páginas)», pero la tabla del diseñador pide «El agente lo mira» + tooltip que nombre el
  escaneado: se implementó **«El agente lo mira (escaneado)»** en el rótulo y **las páginas en el tooltip y en la
  ficha**, porque el número no se puede persistir como número sin migración; (2) el diseñador dice que el paso «antes»
  decía «Miró «Frente.png»» y en realidad M16 nunca lo dijo —una imagen caía en el brazo de lectura y salía «Leyó
  «Frente.png», parte 1»—, así que el paso «Miró …» se escribió en M21 para los dos tipos de archivo.
- **Verificado contra PDF reales** (18 archivos de clientes que ya estaban en la máquina, leídos en el lugar y sin copiar
  ninguno al repo): los extractos reales del Credicoop **siguen `LegibleEnParte`** (el camino barato no se movió), un PDF
  real de una página sin texto **pasó a `SeMira`**, y **un PDF real solo de imágenes de 10 páginas mide 11,76 MB**, o sea
  que el tope de 10 MB de RF-M21-01 lo rechaza aunque entre holgado en el de la API (32 MB). Se implementó el 10 que pide
  el criterio; **subirlo a 20 MB es una clave de `appsettings.json`, sin código ni tests**, y queda para decidir en el gate.

### 2026-09-24/25 — orquestador (M19, M20 y M21, ciclo completo hasta produccion)

- **M19 (la impresora) se hizo fuera del flujo formal**, en el hilo y a pedido directo de Joaquín, antes de invocar al orquestador: `planilla_armar` e `informe_armar` dejan el trabajo como documento del cliente por el camino de subida de M5 (commits `61bc996` y `5e69afe`, diseño en el repo: `docs/diseno-entregables.md`). Queda anotado acá porque es el precedente del que sale M20: la fila de totales como `=SUM(...)` fue la primera cuenta confiable del sistema.
- **M20 y M21 sí pasaron por el flujo**, con las 9 etapas menos la 4: Discovery + Análisis, Diseño y Arquitectura en el hilo (secciones nuevas en `1-analista-funcional.md`, `2-disenador-funcional.md` y `3-arquitecto-mvc.md`), **presupuesto omitido** (proyecto personal) e implementación y QA delegadas a los subagents. Sin frenar en cada gate, por decisión de Joaquín al arranque.
- **Escaneo de reutilización (etapas 2 y 3):** ningún proyecto del historial tiene evaluador de expresiones ni visión sobre documentos; los cuatro hits del grep eran falsos positivos. El precedente conceptual de M21 es `luciano-inmobiliaria/1-analista-funcional.md` §viabilidad —misma vía técnica, PDF nativo a Claude sin pipeline de OCR—, sin código. **La reutilización real fue interna:** M16 (ojos) aportó el camino completo de M21 y M19 la heurística de número de M20, que se mudó a `Application/Helpers/NumeroEscrito.cs` y quedó **compartida**, no duplicada.
- **Decisión del orquestador sobre lo que el implementador dejó abierto (`0335340`):** el tope de peso para mirar un escaneado sube de 10 a **20 MB**, el mismo máximo con que se sube un archivo. Motivo: el implementador midió 18 PDF reales de clientes y encontró un escaneado de 10 páginas de 11,76 MB; que el portal acepte subir 20 MB y después diga «no se puede leer» por peso es una contradicción que la persona no puede resolver. Lo que acota el costo es el tope de **páginas** (20), que no se tocó.
- **QA: aprobado con reparos**, los tres reparos arreglados por QA con test verificado en rojo (`84b54fd`, `019b850`, `4f9809f`). Lo caro pasó sin corrección: aislamiento del PDF entre clientes y organizaciones, tope por conversación medido sobre el pedido real al modelo, y cero base64 en la base.
- **Documentación (etapa 7):** `resumen-sprint-m19-m21-archivos-cuentas-escaneados.md` — media página en lenguaje de negocio para el equipo del cliente, con lo que cambia en el día, lo que cuesta más (mirar un escaneado), los cuatro límites que conviene conocer y lo que todavía no está.
- **Cierre (etapa 8):** `docs/calibracion/dataset.yml` → `cierres_agentic`, tercera fila con dato duro de la familia agéntica — **con esta se alcanza el umbral de 3** que había pedido marihogar para usar la familia en calibración. 135,4 minutos de agente, 1.102.205 tokens de subagente, tests **896 → 996**, 9 commits.
- **El aprendizaje de M18 se aplicó y se puede medir:** allá los ajustes post-QA costaron 151,9 minutos porque dos decisiones de producto se cerraron después de QA; acá las 9 decisiones (D-M20-a..e, D-M21-a..e) se cerraron en Discovery y los ajustes post-QA fueron **cero**.
- **En producción el 2026-09-25**, autorizado por Joaquín: `git push origin main` (`170a016..35057f3`, 9 commits) y `./scripts/deploy-prod.ps1 -Force` — migraciones aplicadas contra la base de producción (incluida **`Entregables`, de M19, que nunca se había desplegado** y que QA encontró faltante en dev), 11 archivos sincronizados (12,4 MB), y `/health/vivo`, `/Account/Login` y `/` en **200**.
- **Pendientes que quedan abiertos, ninguno bloqueante:** (1) guion del modelo simulado para M19/M20, para poder mostrar la calculadora en el navegador sin gastar tokens (QA tuvo que fabricar el paso en la base); (2) desborde horizontal de 3 px a 390 px en tema oscuro por `.ov-topbar-user`, **preexistente y de todo el portal**, no de estos módulos; (3) que la búsqueda de la grilla de documentos encuentre «escaneado» (decisión de producto, no defecto).

## Historial de ajustes

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 71 bloques (2026-09-14 a 2026-09-25) → [`trazabilidad-2026-09.md`](historial/trazabilidad-2026-09.md)
