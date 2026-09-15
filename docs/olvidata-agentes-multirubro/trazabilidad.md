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

### 2026-09-14 - qa
- Etapa: QA (M4 Agentes de la organización, sin revisión del Director)
- Cambio: QA etapa 6 por navegador real (Playwright librería desde Node, MCP `playwright` no disponible en la sesión) con modelo simulado en Development (advertencia confirmada, clave inválida en el proceso, 0 llamadas a Anthropic). 14/14 CA aplicables en PASS (CA-M4-03 pospuesto), 12 HU cumplen, máquina de estados completa, IDOR A↔B sin fugas, regresión del hash de tareas M2/M3b (RT-M4-01) y del portal por rol OK. Datos de núcleo de prueba: rubro `qa-m4` (agente base con herramienta y sugerencias, publicado con aprobación manual "QA M4"), `incluido_siempre` desmarcado al cerrar. Defecto QA-M4-01 (minor): "Archivar" rojo del menú en tema oscuro (3,23) y motivo "No disponible" en claro (2,69) → ítem nuevo OLV-003 en `docs/qa/regresiones-manuales.yml` + auto-fix en `site.css` (7,71 / 6,47). Sección "Archivados" evaluada como clara.
- Motivo: implementación M4 entregada con guía de verificación de 16 pasos.
- Impacto en capas: Web (`wwwroot/css/site.css`, solo CSS). Sin cambios de dominio, servicios ni migraciones; sin tocar Mcp ni Cli; sin commits.
- Evidencia: build 0 errores / 0 advertencias; tests 100/100 antes y después del auto-fix; log del portal sin ERR/FTL; sin tareas Pendiente/EnCurso; portal detenido. Detalle en `6-qa.md` (sección M4).
- Riesgos/supuestos: observaciones OBS-M4-1..7 (Archivados a confirmar con Joaquín, badge de marca 2,98 y text-muted 4,24 del theme, POST sin base sin mensaje, la autora no se entera de ediciones del Director, bases por slug, intersección de herramientas solo por test); inyección por instrucciones y costo del bloque no cacheado sin corrida real; aviso con URL relativa; carreras de límites aceptadas.

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

### 2026-09-14 - analista-funcional
- Etapa: Discovery + Analisis (M4b Agente configurador de reglas del Director)
- Cambio: M4b analizada: conversación de configuración para el Director (reutiliza M3b), agente configurador de Olvidata con herramientas de lectura acotadas a lo que ve el Director y herramientas de propuesta (regla nueva, cambio, desactivación, activar sugerencia) que no aplican nada; tarjetas Aplicar / Editar y aplicar / Descartar / Aplicar todas vía el servicio de reglas; origen "Propuesta del agente" en el historial. 7 CU, 12 RF, 15 CA, 5 riesgos, 9 preguntas. Decisiones chicas de M4 (Archivados, aviso a la autora) y contenido del rubro de negocio registrados como PA-08..PA-10.
- Motivo: pedido N-01 de Joaquín; siguiente etapa del roadmap ("continuar").
- Impacto en capas: Presentación (conversación con tarjetas de propuesta), Negocio (herramientas acotadas por permisos, aplicación vía ReglaService), Datos (propuestas, origen en eventos — migración).
- Riesgos/supuestos: R-M4b-01 propuestas equivocadas, R-M4b-02 inyección/escalamiento (mitigado por herramientas acotadas y aplicación solo por botón). Reutilización: crm-olvidata (function calling + ejecución por servicio de negocio). QA sin costo requiere modelo simulado con herramientas guionadas (P8).

### 2026-09-14 - analista-funcional
- Etapa: Analisis M4b (gate)
- Cambio: Joaquín aprobó con todas las hipótesis P1–P9 ("continuar"): configurador dentro de Reglas, solo Director, propone empresa/áreas/por agente/clientes + cambios/desactivaciones/sugerencias, 10 propuestas por respuesta, sin vencimiento, costo en Tareas, prompt en borrador redactado por Claude y publicado por Joaquín con evaluación, simulador con herramientas guionadas, "Aplicar todas".
- Motivo: cierre del gate Análisis → Diseño de M4b.
- Impacto en capas: —
- Riesgos/supuestos: el prompt del configurador es contenido de plataforma (no de rubro).

### 2026-09-14 - disenador-funcional
- Etapa: Diseno (M4b)
- Cambio: botón "Configurar conversando" en Reglas, lista de conversaciones de configuración compartida entre Directores, nueva conversación con chips, conversación M3b con tarjetas de propuesta (Nueva / Cambio con Antes-Después / Desactivar / Activar sugerencia; Aplicar, Editar y aplicar, Descartar, Aplicar todas, Reintentar), modal de "la regla cambió desde la propuesta", formulario de regla precargado, origen en historial, filtro de tipo en Tareas, configurador en Núcleo. 5 ViewModels, mensajes, máquina de estados de propuesta, permisos, contratos y 10 historias.
- Motivo: diseño implementable de M4b sobre el análisis aprobado.
- Impacto en capas: Presentación (tarjetas, lista, entrada), Negocio (herramientas acotadas, aplicación por reglas), Datos (propuestas, origen, tipo de tarea).
- Riesgos/supuestos: decisiones a validar D-M4b-1..9 (entrada en Reglas, lista compartida y cualquier Director aplica, configurador sin reglas de la empresa como instrucciones, tarjeta con Por qué y Antes/Después, modal de cambio, editar y aplicar, chips, filtro en Tareas, origen con enlace). Nuevo PAT-032 (PAT-031 ya estaba tomado por crm-olvidata).

### 2026-09-14 - arquitecto-mvc
- Etapa: Diseno M4b (gate) + Arquitectura (M4b)
- Cambio: Joaquín aprobó el diseño con D-M4b-1..9 ("continuar"). Arquitectura: `TipoTarea.ConfiguracionReglas` con contexto formato 3 (plataforma + configurador, sin reglas de la empresa), `IResolvedorSesion.ResolverUsuarioAsync` para el worker, herramientas `reglas_listar`/`regla_obtener`/`estructura_empresa`/`clientes_buscar`/`sugerencias_listar` y `proponer_*` acotadas y re-verificadas, entidad `PropuestaRegla` (estados, token, único por `ToolUseId`), `IPropuestaReglaService` (aplicar con verificación de cambio, aplicar todas parcial, descartar, precarga), `ReglaService` con origen de aplicación en el mismo guardado, `ConfiguracionReglasController`, tarjetas en el detalle de tarea, prompt del configurador en borrador en `nucleo/plataforma`, simulador con guion de herramientas; migración `ConfiguradorReglasM4b`.
- Motivo: diseño M4b aprobado.
- Impacto en capas: Domain (entidad, 3 enums, campos en tarea y evento), Application (servicios, resolvedor, constructor formato 3, DTOs), Infrastructure (herramientas, servicios, procesador, simulador, núcleo, migración), Web (controller nuevo, detalle de tarea, reglas, tareas).
- Riesgos/supuestos: RT-M4b-01 permisos en segundo plano, RT-M4b-02 compatibilidad de hash (golden formatos 1 y 2), RT-M4b-04 prompt borrador sin publicar hasta evaluación de Joaquín. PAT-032 ampliado.

### 2026-09-14 - presupuestador
- Etapa: Arquitectura M4b (gate) + Presupuesto (omitido)
- Cambio: Joaquín aprobó la arquitectura de M4b ("si", puntos 1–7). Presupuesto omitido. Se lanza Implementación.
- Motivo: gate Arquitectura → Implementación de M4b.
- Impacto en capas: —
- Riesgos/supuestos: —

### 2026-09-14 - implementador
- Etapa: Implementacion (M4b Agente configurador de reglas del Director)
- Cambio: `TipoTarea.ConfiguracionReglas` con instantánea y render propios (formato 3: reglas de plataforma + declaración + prompt, sin reglas de la empresa; formatos 1 y 2 intactos con golden); `ResolverUsuarioAsync` y re-verificación del autor en el worker y en cada herramienta; 9 herramientas (`reglas_listar`, `regla_obtener`, `estructura_empresa`, `clientes_buscar`, `sugerencias_listar`, `proponer_regla_nueva`, `proponer_cambio_regla`, `proponer_desactivar_regla`, `proponer_activar_sugerencia`) sin `SaveChanges`; entidad `PropuestaRegla` (estados, token, único por `ToolUseId`); `PropuestaReglaService` (tarjetas, aplicar con verificación de cambio, Fallida con motivo, aplicar todas parcial, descartar, precarga); `ReglaService` con `OrigenAplicacion` en el mismo guardado; `ConfiguracionReglasController` (lista, nueva con chips, acciones AJAX); tarjetas en la conversación con modal de cambio; formulario de regla precargado; origen "Propuesta del configurador" con enlace; filtro Tipo en Tareas; simulador con guion de herramientas (nuevas / revisión / sugerencia). Migración `ConfiguradorReglasM4b` aplicada en dev. Prompt borrador `nucleo/plataforma/agentes/configurador-reglas.md` importado (#65 v1 Borrador, sin publicar). PAT-032 completado con rutas reales.
- Motivo: arquitectura M4b aprobada (presupuesto omitido).
- Impacto en capas: Domain (entidad, 3 enums, campos en tarea y evento), Application (DTOs, 2 interfaces nuevas, resolvedor, motor, constructor, reglas), Infrastructure (herramientas, 2 servicios nuevos, constructor, procesador, tareas, simulador, reglas, resolvedor, configuraciones, migración), Web (controller nuevo, 2 vistas + 2 parciales, Tareas y Reglas ajustados, CSS), Núcleo (prompt borrador + manifiesto).
- Evidencia: build 0 errores (1 advertencia preexistente); tests 113/113 (100 + 13 nuevos, con golden de formatos 2 y 3); SQL real en transacción revertida (1062 por `ToolUseId`, token 1/0 filas, 1406/1452/1451 esperados, índices usados, datos existentes intactos, 0 restos); EF → MySQL 17 pasos OK con modelo simulado, incluida la `DbUpdateConcurrencyException` real por `VersionToken`, sin errores MH-001 y 0 restos (configurador restaurado a Borrador).
- Riesgos/supuestos: calidad del prompt y de las herramientas con el modelo real sin medir (PA-02); inyección mitigada por código sin validación real; costo de lectura por conversación; máximo de 10 por paso sin índice. Decisiones DI-M4b-1..19 en `5-implementador.md` (incluye el ajuste de `AplicarTodas` a una lista de pasos y el guion del simulador por palabra clave).
- Guía de verificación manual para QA (sin costo, solo en desarrollo):
  0. **Preparación.** Modelo simulado: `$env:Anthropic__Simulado = "true"; dotnet run --project src/OlvidataAgentes.Web --launch-profile https` (advertencia "MODELO SIMULADO" en consola). **Habilitar el configurador solo en `olvidata_agentes_dev`** (publica la versión importada; nunca contra producción):
     `dotnet run --project src/OlvidataAgentes.Admin -- versiones plataforma` (debe listar `#65 Agente configurador-reglas v1 Borrador`) →
     `dotnet run --project src/OlvidataAgentes.Admin -- evaluar 65 --aprobada "QA M4b: publicación solo en desarrollo para probar la UI; no evalúa el contenido"` →
     `dotnet run --project src/OlvidataAgentes.Admin -- publicar 65`.
     **Revertir al terminar** (vuelve a Borrador; las conversaciones creadas siguen reconstruyéndose porque se anclan por id): `UPDATE olvidata_agentes_dev.ArtefactoVersiones SET Estado = 1, PublicadaAt = NULL, PublicadaPorUserId = NULL WHERE Id = 65 AND Estado = 3;` (la evaluación "QA M4b" queda en el historial; la evaluación real de Joaquín se registra después y es la que habilita publicar). Datos: "Inmobiliaria Demo" (3 Directores, 3 Empleados, rubros `inmobiliario` y `qa-m4` con la sugerencia publicada `qa-m4-sug-tono`) y "QA Org B" para pruebas entre organizaciones.
  1. **Reglas (Director), antes de publicar:** botón secundario "Configurar conversando" antes de "Nueva regla", deshabilitado con tooltip "Todavía no está disponible."; `/ConfiguracionReglas/Nueva` muestra "Todavía no está disponible." y el formulario deshabilitado. Después de publicar: botón activo. Empleado: no ve el botón; `/ConfiguracionReglas` → 403. Pestaña "De la empresa" sin reglas (por ejemplo en QA Org B): "Todavía no hay reglas de la empresa. ¿Preferís contarlo con tus palabras? Configurá conversando." con enlace.
  2. **Lista (P-M4b-02):** breadcrumb Reglas › Configurar conversando; vacía: "Todavía no hay conversaciones. Empezá una y contale cómo trabajan."; con datos: Iniciada · Por · Última actividad · Pendientes (badge ámbar si > 0) · Aplicadas · Estado · Abrir; filtros por columna (Iniciada y Última actividad con rango, Por, Pendientes con/sin, Estado), búsqueda global (nombre, fecha, número, estado, texto del pedido), persistencia en Session y "Limpiar filtros".
  3. **Nueva conversación (P-M4b-03):** los chips completan el texto ("Revisá mis reglas actuales" lo reemplaza si está vacío); contador "0 / 10.000"; enviar vacío → "Contame qué querés configurar."; más de 10.000 → "El mensaje admite hasta 10.000 caracteres."; Ctrl+Enter envía; "Empezar" lleva a la conversación.
  4. **Conversación con propuestas nuevas (pedido cualquiera, p. ej. "Somos un estudio contable"):** encabezado "Configuración de reglas · dd/MM/yyyy" · Por · Iniciada · Última actividad; línea de estado "… · USD 0,00 en total · 2 propuestas pendientes"; respuesta "Te dejé propuestas simuladas…"; debajo, "Aplicar todas (2)" y dos tarjetas "Nueva regla": "Regla simulada 1-a" (etiqueta "simulada") y "Regla simulada 1-b" (badge "Procedimiento"), "Dónde aplica: En toda la empresa", badge "Salvo que se indique otra cosa", "Por qué: …", botones Aplicar / Editar y aplicar / Descartar. "Ver pasos" muestra `estructura_empresa` y `proponer_regla_nueva`. Sin "Lo que el agente tuvo en cuenta" ni "Nueva tarea con este agente".
  5. **Aplicar:** toast "Propuesta aplicada."; la tarjeta pasa a badge verde "Aplicada" con "Ver regla" sin recargar. La regla: detalle con Origen badge "Propuesta del configurador" + "Ver conversación"; historial con "desde el configurador" + "Ver conversación". Un Empleado ve el badge y "desde el configurador" sin enlaces.
  6. **Descartar:** toast "Propuesta descartada."; badge gris "Descartada", sin acciones; ninguna regla nueva.
  7. **Editar y aplicar (nueva):** formulario "Nueva regla" precargado con el aviso "Estás aplicando una propuesta del configurador…"; cambiar el título y Guardar → vuelve a la conversación, a la tarjeta, con "Propuesta aplicada."; la regla guardada tiene el título editado. Volver/Cancelar también regresan a la tarjeta.
  8. **Aplicar todas:** SweetAlert2 "Se van a aplicar N propuestas. Las que no se puedan aplicar quedan marcadas con el motivo." → toast "2 aplicadas." (o "1 aplicada, 1 no se pudo aplicar.").
  9. **CA-M4b-07:** en "Seguir conversando" (placeholder "Pedile otra regla o que ajuste una propuesta…") escribir "Aplicalo, dale." → nueva respuesta con dos propuestas "Regla simulada 2-a/2-b" pendientes; ninguna regla se aplicó. Otro Director abre la conversación: ve tarjetas y acciones, sin cuadro ("Solo quien pidió la tarea puede seguir esta conversación.").
  10. **Cambio y desactivación:** con al menos 2 reglas de la empresa activas, nueva conversación con el chip "Revisá mis reglas actuales" → tarjetas "Cambio en «…»" con Antes / Después (título "(ajustada)") y "Desactivar «…»" (sin "Editar y aplicar"). Aplicar la desactivación → la regla queda Inactiva con evento "desde el configurador". Para el modal D-M4b-5: antes de aplicar el cambio, editar esa regla desde Reglas (otro Director u otra pestaña) → refrescar la conversación: aviso "La regla cambió desde esta propuesta…" en la tarjeta → Aplicar → modal "La regla cambió" con "Versión actual" y "Propuesta": Cancelar (no cambia nada), "Editar y aplicar" (formulario de edición precargado con lo propuesto sobre la versión actual y el aviso) o "Aplicar igual" (versión N+1).
  11. **Activar sugerencia:** conversación con la palabra "sugerencia" (p. ej. "¿Hay alguna sugerencia de Olvidata para nosotros?") → tarjeta "Activar sugerencia «…»" en la empresa. Aplicar → pestaña "Sugerencias de Olvidata" con "Ya activada" y el detalle con origen del configurador. Si la sugerencia ya estaba activada por QA M4, la respuesta dice "No hay sugerencias de Olvidata disponibles para activar." (desactivar la regla no la libera: hay que borrar esa regla de prueba en dev).
  12. **No se pudo aplicar y Reintentar:** arrancar el portal además con `$env:Reglas__MaxOrganizacion = "100"` → aplicar una propuesta nueva de la empresa cuando ya hay reglas activas → badge rojo "No se pudo aplicar" con "Con esta regla se superan los 100 caracteres…"; botón "Reintentar" y "Editar y aplicar". Desactivar otra regla y Reintentar → "Aplicada". Quitar la variable al terminar.
  13. **Dos Directores:** dos navegadores con Directores de la misma organización sobre la misma tarjeta pendiente: uno descarta; el otro, sin refrescar, aplica → toast "Esta propuesta ya fue resuelta." y la tarjeta se actualiza.
  14. **Permisos e IDOR:** Empleado → `/Tareas/Detalle/<id conversación>` 404 y `POST /ConfiguracionReglas/AplicarPropuesta` 403; Director de QA Org B → detalle 404 y POST a una propuesta ajena → 404 JSON. Staff (SuperUsuario) → Tareas con filtro Tipo y detalle en solo lectura (tarjetas sin botones, breadcrumb Tareas).
  15. **Tareas (D-M4b-8):** Director/staff ven el filtro "Tipo" (Tareas / Configuración de reglas); la columna Agente muestra "Configurador de reglas" con "Configuración de reglas" debajo; costo U$D 0,00 con el simulado; Session y Limpiar. Empleado: sin filtro Tipo y sin configuraciones en su listado.
  16. **Mobile y tema oscuro:** tarjetas (borde por estado, "Dónde aplica", "Por qué" sobre fondo azul suave, Antes/Después, badges Aplicada / Descartada / No se pudo aplicar / modo / Procedimiento / etiquetas), íconos del tipo, aviso de cambio y motivo de falla, modal SweetAlert2, chips, badge ámbar de Pendientes, botones del encabezado de Reglas y cuadro sticky en mobile. Contrastes medidos en código (DI-M4b-18); confirmar visualmente.
  17. **Al terminar:** revertir la publicación del configurador (paso 0), quitar `Reglas__MaxOrganizacion` y, si hace falta, borrar las reglas de prueba.

### 2026-09-14 - qa
- Etapa: QA (M4b Agente configurador de reglas del Director)
- Cambio: verificación en navegador real (Playwright 1.63 desde Node; el MCP `playwright` no estaba cargado) con modelo simulado en 4 arranques (normal; motor apagado + `Reglas:MaxOrganizacion=100`; límite 621; normal), costo cero (0 llamadas a Anthropic, 0 ERR/FTL). CA-M4b-11 verificado con #65 en Borrador; después publicado solo en dev (`evaluar 65 --aprobada "QA M4b: solo desarrollo"` + `publicar 65`) y revertido a Borrador con el UPDATE del implementador (verificado por SQL). 15/15 CA en PASS: tarjetas de los 4 tipos, Aplicar, Editar y aplicar (Nueva y Cambio), Descartar, Aplicar todas (total y parcial por límite y por regla cambiada), Reintentar, modal D-M4b-5 con sus 3 salidas, "aplicalo" no aplica, dos Directores ("Esta propuesta ya fue resuelta."), otro Director aplica sin cuadro, Empleada 403/404, org B 404, staff lectura, origen con/sin enlace, filtro Tipo, lista compartida con filtros/Session, invitación en "De la empresa" vacía, autor degradado → turno Fallido sin llamar al modelo. Regresión de hash (formatos 1 y 2) y menú por rol OK. Checklists: mobile 390 OK, ortografía y rótulos OK, contraste de lo nuevo OK.
- Motivo: etapa 6 del flujo para M4b.
- Impacto en capas: sin cambios de código (build 0/0, tests 113/113). Catálogo: OLV-004 creado (botones/enlaces con color sin variante por tema). Memoria QA actualizada (`6-qa.md`, sección M4b; última validación de reglas 2026-09-14).
- Riesgos/supuestos: **apto con observaciones**. QA-M4b-01 minor (OLV-004, tokens del portal previos a M4b, reportado sin auto-fix: decisión de design system). Observaciones: "Ver pasos" muestra herramientas y JSON al Director (formato M1), texto genérico "Podés pedirle que siga…" en el turno fallido por degradación, título de la tarjeta de Cambio con el título vigente. Pendiente: evaluación y publicación real del prompt por Joaquín y corrida paga (PA-02). Datos de dev modificados: regla 16 (M3) renombrada e inactiva, regla 64 (M4) con baja lógica, reglas "Regla simulada …" y conversaciones #29–#35 de QA.

### 2026-09-14 - documentador
- Etapa: Documentacion (M4b)
- Cambio: resumen de entrega `resumen-sprint-m4b-configurador.md` (formato 31); pendientes registrados en `metadata.md` como PA-11 (contraste global OLV-004), PA-12 ("Ver pasos" técnico y textos menores) y PA-13 (evaluar y publicar el prompt del configurador).
- Motivo: cierre de comunicación de M4b.
- Impacto en capas: —
- Riesgos/supuestos: la función queda deshabilitada hasta publicar el prompt.

### 2026-09-14 - presupuestador
- Etapa: Cierre calibracion (M4b)
- Cambio: esfuerzo real sin estimado (implementador ~72 min / 257 acciones, QA ~29 min); lecciones: guiones de herramientas en el simulador desde el diseño, contraste verificado en implementación con deuda global aparte, features con tool use + permisos en segundo plano = complejidad alta.
- Motivo: cierre del flujo de 9 etapas de M4b.
- Impacto en capas: —
- Riesgos/supuestos: M4b cerrada.

### 2026-09-14 - orquestador
- Etapa: Programa "plan completo local"
- Cambio: Joaquín pidió implementar todo el plan en local, ejecutar 2 iteraciones de QA y probarlo él al final. Decisiones: M5→M12 **sin frenar en gates** (se toman las propuestas recomendadas y se documentan); M11 = mecanismo de conectores + conector HTTP de ejemplo; QA en navegador por etapa + 2 rondas de QA integral finales; git local con commit por etapa cerrada (sin remoto); M9 en versión local (paquete, configuración y guía de deploy, sin publicar). Sin corridas pagas ni publicación de prompts reales. Fase 0 (legal/comercial) y decisiones §8.1/§8.3 del plan quedan fuera por no ser implementables.
- Motivo: pedido explícito de Joaquín.
- Impacto en capas: todas, por etapa.
- Riesgos/supuestos: sin gates, las hipótesis quedan registradas para revisión posterior; facturación depende de la unidad de cobro (decisión §8.1 pendiente).

### 2026-09-15 - analista-funcional
- Etapa: Discovery + Analisis (M5 Workspace por cliente de cartera) — aprobado sin gate por autorización de Joaquín 2026-09-14
- Cambio: sección M5 en `1-analista-funcional.md`: 11 CU, 18 RF, 19 CA, 7 riesgos, 4 supuestos y 14 preguntas con la opción recomendada tomada como hipótesis (P1 reemplazar `DocumentoCliente`; P2 texto extraído por código, imágenes y escaneados no legibles; P3 20 MB por archivo, 1 GB por organización, 200 por cliente, 1.000.000 de caracteres legibles, 10 adjuntos por mensaje; P4 baja por Director o por quien lo subió; P5 herramientas automáticas en tareas de trabajo con cliente; P6 adjuntar = referencia + lectura con herramientas; P7 staff solo metadatos; P8 baja con borrado físico, sin papelera; P9 duplicados por contenido rechazados y nombre con sufijo; P10 extracción al subir; P11 sin escritura del agente; P12 sin documentos de empresa; P13 simulador con guion; P14 sin versiones).
- Motivo: programa "plan completo local" (M5→M12 sin gates); PLAN Fase 2 "workspace por cliente en servidor propio"; M3b dejó adjuntos para M5.
- Impacto en capas: Presentación (ficha, documentos, adjuntos, vista previa), Negocio (validación, límites, permisos, herramientas acotadas), Datos (documentos, texto por partes, adjuntos; baja de `DocumentosCliente`).
- Riesgos/supuestos: R-M5-01 inyección desde documentos y R-M5-02 archivos maliciosos/confidencialidad (altos); S-M5-01 carpeta fuera de `wwwroot` escribible en SmarterASP a confirmar en M9; calidad real de lectura por partes pendiente de corrida con costo (PA-02).

### 2026-09-15 - disenador-funcional
- Etapa: Diseno (M5) — aprobado sin gate por autorización de Joaquín 2026-09-14
- Cambio: sección M5 en `2-disenador-funcional.md`: D-M5-1..14 (card en la ficha del cliente, pantalla de documentos con subida en cola de a un archivo, estado de lectura con ícono y texto, ver por partes, renombrar y baja con SweetAlert2, espacio solo para el Director, adjuntar en Ejecutar y en ajustes con modal compartido, chips en la conversación, vista previa de documentos, Ver pasos llano para herramientas de documentos, staff solo metadatos); 8 pantallas/ajustes, 12 ViewModels, tabla de mensajes, máquina de estados del documento, permisos por pantalla, contratos y 10 historias. Nuevo PAT-033; PAT-002 verificado en `C:\Sistemas\vino-y-se-fue` y corregido (guarda en `wwwroot`, no apto para documentos confidenciales).
- Motivo: diseño implementable de M5 sobre el análisis.
- Impacto en capas: Presentación (Cartera/Detalle, Documentos/*, modal, Agentes/Ejecutar, Tareas/_Conversacion, _CuadroSeguimiento, _PasosTurno, backoffice), Negocio (contratos de documentos, lectura, almacén, herramientas, tareas), Datos (documento, partes, adjuntos).
- Riesgos/supuestos: R-M5-08 cola de subida interrumpida, R-M5-09 nombre del chip vs. nombre actual; hipótesis P2–P12 re-expuestas.

### 2026-09-15 - arquitecto-mvc
- Etapa: Arquitectura (M5) — aprobada sin gate por autorización de Joaquín 2026-09-14
- Cambio: sección M5 en `3-arquitecto-mvc.md`: `DocumentoCartera` (reemplaza `DocumentoCliente`; `NombreVigente` STORED único por cliente; `VersionToken`), `DocumentoCarteraParte` (mediumtext) y `AdjuntoMensajeTarea` (PasoNumero 0 = pedido); `IAlmacenDocumentos` en disco fuera de `wwwroot` (ruta con enteros y GUID, temporal + confirmación post-commit); `ValidadorContenidoArchivo` y extractores puros (UglyToad.PdfPig, DocumentFormat.OpenXml, ClosedXML, CSV/texto) con topes de tiempo, páginas, caracteres y descompresión; `DocumentoCarteraService`; `HerramientasDocumentos` (`documentos_listar`, `documento_leer`, `documentos_buscar`) de solo lectura unidas a las del agente en tareas de trabajo con cliente; `ContextoHerramienta` + `ClienteCarteraId`; adjuntos en el mismo guardado de la tarea o del ajuste y nota fija en `ReconstruirConversacion` (prompt de sistema y hash intactos); rótulos llanos en Ver pasos; `DocumentosController`; backoffice solo metadatos; simulador con guion de documentos; comando Admin `documentos-limpiar`; `.gitignore` + `App_Data/documentos/`; migración `WorkspaceClientesM5` (drop `DocumentosCliente` + 3 tablas).
- Motivo: diseño M5 tomado sin gate.
- Impacto en capas: Domain (3 entidades, 2 enums, baja de `DocumentoCliente`), Application (options, helper de nombres, DTOs, 3 interfaces, extensiones del motor, nota de adjuntos), Infrastructure (almacén, validador, extractores, servicio, herramientas, procesador, servicio de tareas, simulador, configuraciones, DI, 2 paquetes, comando Admin, ajuste de 2 tests), Web (controller nuevo, Cartera, Agentes, Tareas, Clientes, vistas y scripts).
- Riesgos/supuestos: RT-M5-01 path traversal/exposición, RT-M5-02 archivos maliciosos y bombas de compresión, RT-M5-03 inyección (altos); RT-M5-04 disco ↔ base, RT-M5-05 despliegue que borre `App_Data/documentos` y permisos de escritura del pool (checklist M9, `/olvidata-infra`), RT-M5-06 rendimiento en pool compartido, RT-M5-07 cuota excedida por concurrencia (aceptado), RT-M5-08 hash (golden 1–3). PAT-033 agregado al catálogo.
