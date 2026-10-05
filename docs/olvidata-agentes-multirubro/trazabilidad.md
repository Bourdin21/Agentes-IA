# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-10-05 - implementador (M32 tanda 1: la respuesta cortada se continua)
- Etapa: Implementacion
- Cambio: **una respuesta cortada por `max_tokens` ya no termina la tarea en `Fallida`: se continua.** Sin migracion. (1) `AnthropicSettings.MaxContinuacionesPorCorte` (default 3) con `ContinuacionesPorCorte` saneado por `Math.Max(0, ...)`. (2) En el bucle de `ProcesadorTareas`, `StopReason == MaxTokens` deja de ir a `FinalizarAsync`: si los cortes del turno no pasaron el tope, cae al pie del bucle y vuelve a llamar. El turno parcial ya estaba guardado como paso con su costo y `ReconstruirConversacion` ya lo deja como mensaje del **asistente**, asi que la API continua ese mismo mensaje (prefill) y el modelo no reescribe lo ya dicho -- la mitigacion de R-04 sin escribir prompt. (3) Agotado el tope: `NotaDelMotor` con `MensajeRespuestaCortada` y `MarcarFinAsync(Completada)` con el texto pegado de todos los tramos, nunca `Fallida`. (4) `CortesDelTurno`, `TextoDelTurnoPegado` e `InicioDelTurno` (extraido de `LlamadasDelTurno`); `FinalizarAsync` ahora recibe los pasos y el resultado de un `FinTurno` es el texto pegado del turno, no solo el ultimo tramo. (5) `SinEspacioAlFinal`: la API rechaza el pedido si el mensaje del asistente con el que cierra termina en espacios, y un corte cae donde cae; se aplica solo en la continuacion y solo al pedido, el paso guardado queda intacto. (6) En `ServicioTareas`, `turno.Respuesta` se acumula tambien en un paso cortado: sin eso, un turno cortado no mostraba ninguna respuesta en la conversacion y uno continuado mostraba solo el ultimo tramo.
- Motivo: pedido de Joaquin con el caso real («"La respuesta supero el maximo de tokens configurado" ante una conciliacion. Desestimar este tope. Es mas importante que complete la tarea»), resuelto por D-01 de Arquitectura M32. **El tope no era el defecto:** 16.000 es el valor que la documentacion recomienda para pedidos **sin streaming**, que es lo que hace el proveedor; subirlo sin transmitir cambia un corte por un timeout de HTTP, que no deja ni el trabajo parcial. El defecto era que la tarea moria y se perdia todo. Es la misma falla que M27 fue a eliminar por el lado de la **entrada**, entrando por la puerta de la **salida**.
- Impacto en capas: Application (`Settings/AgentesSettings.cs`), Infrastructure (`Services/Motor/ProcesadorTareas.cs`, `Services/Motor/ServicioTareas.cs`), Web config (`appsettings.json`), tests (`RespuestaCortadaM32Tests.cs` nuevo; `ConversacionTests.Turno_fallido_por_max_tokens_...` reescrito porque afirmaba literalmente el defecto). **Sin migracion EF y sin cambio de esquema.** Sin tocar el proveedor, el streaming, `MaxTokens`, `TaskBudgetTokens`, las banderas beta, el escalonamiento de entrada de M27 ni ningun valor de M6.
- Riesgos/supuestos: build limpio y **1253/1253 verde** (base 1243 + 10), medido sin pipe, con cinco mutaciones corridas (la rama revertida al `Fallida` viejo tumba los 6 tests de criterio). **Decision tomada y anotada:** con el tope agotado el estado es `Completada`, asi que una tarea **programada** va a avisar «termino correctamente» sobre una respuesta que quedo cortada (`EjecutorProgramaciones` elige el texto por `== Completada`) -- es el motivo por el que M27 se habia quedado en `Fallida`, y aca la balanza da para el otro lado porque **hay trabajo hecho y entregado**; si molesta, el arreglo es del lado del aviso. `0` = sin continuaciones y un negativo es lo mismo que `0`: el tope no puede invertir el comportamiento, y hay test de los tres lados. `MaxPasos` (25) no se toco: una continuacion cuenta como llamada ahi tambien. La app no se levanto: la verificacion en pantalla y el texto pegado de una conciliacion real son de QA (R-04: el modo de falla de continuar es repetir o contradecir). **Tanda 2 (streaming + `MaxTokens` a 64.000) sigue pendiente y D-01 no depende de ella.** Commit local, sin push, sin deploy.

### 2026-10-02 - implementador (M29 ronda de arreglos de QA: OLV-038, OLV-039, OLV-040)
- Etapa: Implementacion
- Cambio: arreglados los tres defectos de los dos lotes de QA de M29, **sin migracion**. (1) **OLV-038 (major):** `AdjuntoMensajeDto` gana `SinCliente`, `Version` y el predicado con nombre `SePuedeGuardar`, proyectados por `ServicioTareas` en la consulta que ya existia; el chip del hilo (Razor) y el del compositor (JS) **marcan** el boton con `data-guardar-adjunto` y lo atiende **un solo listener delegado en `document`** dentro de `documentos.js`, que al guardar emite `ov:adjunto-guardado` y deja que el servidor vuelva a dibujar el hilo. `TareaDetalleDto.HayAdjuntosParaGuardar` —el **mismo** predicado— es lo que pone el modal en la pagina, para lo cual se extrajo `_ModalGuardarEnCliente` de `_ModalDocumentos`. (2) **OLV-039 (minor):** con ese dato, el chip del hilo usa las mismas clases y la misma leyenda «solo en esta conversacion» que el del compositor, sin fecha ni cuenta regresiva (D-04); el chip paso de `<a>` a `<span>` con el nombre como enlace adentro. (3) **OLV-040 (minor):** las dos validaciones de `DocumentosController.Subir` dejaron de estar colapsadas: sin archivo -> «Elegi un archivo.»; con archivo y ModelState invalido -> «El cliente no existe.» con 404, igual que un `clienteId=0`.
- Motivo: cerrar M29 aplicando los partes de QA. OLV-038 dejaba HU-04 sin camino —la historia pasa **despues** de ver la respuesta del agente— y con ella la mitad reversible de D-01 sin existir; OLV-039 es RD-02, declarado obligatorio y no decorativo; OLV-040 es el criterio textual de OLV-036 («ningun camino») que no se cumplia.
- Impacto en capas: Application (`Motor/IMotorAgentes.cs`), Infrastructure (`Services/Motor/ServicioTareas.cs`), Web vistas (`Views/Tareas/_Conversacion.cshtml`, `Views/Tareas/Detalle.cshtml`, `Views/Shared/_ModalGuardarEnCliente.cshtml` nuevo + `_ModalDocumentos.cshtml`), Web front (`wwwroot/js/documentos.js`, `wwwroot/css/site.css`), Web controller (`Controllers/DocumentosController.cs`), tests (`ChipDelTransitorioEnElHiloTests.cs` nuevo). **Sin migracion EF y sin cambio de esquema.**
- Riesgos/supuestos: build limpio y **1221/1221 verde** (linea base 1217), con cada test fallando sin su arreglo verificado por mutacion. Los tres defectos quedan **"aplicado, pendiente de re-verificacion"**: el cierre lo declara QA en contexto nuevo. Supuesto declarado: con el archivo presente, el unico ModelState invalido posible en `Subir` es el `clienteId` (el ViewModel tiene un solo campo); si se le agrega otro, la guarda hay que partir en tres. Lo que la rama nueva de `Detalle.cshtml` cubre y los tests no: un miembro que **no** es el autor abriendo el hilo. Inventario MH-041 cerrado: 5 superficies humanas leen los chips (una era la rota) y `TareaOrigenId` tiene 27 apariciones en `src/` de las que **solo 7** son la columna del documento —el resto es el homonimo de `TareaAgente`—. Commit local, sin push y sin deploy.

### 2026-10-02 - qa (M28 ronda de re-verificacion)
- Etapa: QA
- Cambio: re-verificados en contexto nuevo los seis defectos de los tres lotes de M28 (commit `7b508d5`): **OLV-028, OLV-029, OLV-030, OLV-031, OLV-032, OLV-033 y OLV-034 CERRADOS**, cada uno reproduciendo el caso original con el criterio arrancando en FAIL. OLV-030 verificado en los tres sitios (tarjeta de parte, tarjeta de aprobacion con *Resolver*, contador); OLV-031 en el borde de 18 agentes; OLV-033 por las dos compuertas y con los dos roles, con el contraejemplo del configurador y del asistente intacto; OLV-028 probado **antes** de publicar y sobre las cuatro conversaciones. Los cuatro criterios que estaban BLOCKED (CA-04.1, CA-04.2, CA-03.3, D-05) se calificaron **PASS** gracias al guion de chat libre del `ProveedorModeloSimulado`. HU-04 re-corrida con los botones vivos: PASS. **Tres defectos nuevos: OLV-036 (major), OLV-037 (minor) y OLV-035 (trivial)**, con item en `docs/qa/regresiones-manuales.yml` (catalogo en 147) y linea en `cat_resumen.txt`.
- Motivo: cerrar o reabrir los partes de los tres lotes y levantar los BLOCKED, segun el ciclo QA reporta -> Implementador aplica -> QA re-verifica en contexto nuevo.
- Impacto en capas: ninguno (QA no toca el repo del sistema; `git status --porcelain` verificado sin cambios propios). Lo escrito vive en `6-qa.md`, `trazabilidad.md` y el catalogo cross-proyecto.
- Riesgos/supuestos: **veredicto apto con reparos.** Ningun bloqueante por datos, plata ni aislamiento. El reparo que lo condiciona es OLV-036: desde una conversacion sin cliente no se puede **subir** un adjunto (`POST /Documentos/Subir?clienteId=` con el parametro vacio invalida el ModelState y devuelve el mensaje del otro campo, *"Elegi un archivo"*), asi que una organizacion sin cartera no tiene camino para mandarle un manual al agente; adjuntar un documento ya existente si funciona. Sin cubrir todavia, por pedir modelo real: el texto de la mencion que no resuelve y el `delegar_subagente` con un codigo manipulado. Costo de la corrida: USD 0,00 (modelo simulado).

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

### 2026-09-14 - presupuestador
- Etapa: Arquitectura M3 (gate) + Presupuesto (omitido)
- Cambio: Joaquín aprobó la arquitectura de M3 (3 bloques con precedencia en el bloque estable, instantánea por ids + hash, rubro técnico `plataforma`, carrera de límites aceptada). Presupuesto omitido por criterio vigente. Se lanza Implementación.
- Motivo: gate Arquitectura → Implementación.
- Impacto en capas: —
- Riesgos/supuestos: —

### 2026-09-14 - disenador-funcional
- Etapa: Diseno M3b (gate)
- Cambio: Joaquín aprobó el diseño con D-M3b-1..7 ("continuar").
- Motivo: cierre del gate Diseño → Arquitectura de M3b.
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

### 2026-10-01 - agentes-ia-implementador (M27, frentes 1, 2 y 6)
- **Etapa:** 5 (Implementación). Definiciones 1, 2 y 3 aprobadas; presupuesto omitido (proyecto personal). Frentes 3 (documentos) y 4 (menú): otro implementador, en paralelo.
- **Cambio:** 4 commits locales en `Olvidata Agentes Multi-rubro` (`625b30f`, `43dce94`, `f7103cf`, `28b929c`), sin push y sin deploy. **1091 tests verdes** (eran 1067). Una migración, `UnificacionAgentesM27`, exactamente la que fijó la arquitectura.
- **Lo que hay que saber del frente 2, porque cambia qué se arregló:** la conciliación de la demo no la cortó ningún tope del sistema — la cortó `Anthropic:TaskBudgetTokens = 64000`. **Medido, no supuesto:** dos corridas contra la API con la misma conversación de 57.580 tokens de entrada; con 64.000 el modelo produjo 3.417 tokens de salida, dijo «ya no tengo capacidad disponible en esta sesión» y **no encontró ninguna** de las 11 partidas no conciliadas plantadas; con 400.000 produjo 42.884, dijo «terminé el cruce completo» y las listó con fecha, comprobante e importe. Doce veces más trabajo hecho por cambiar un número.
- **Precisión del mecanismo (corrección de la auditoría):** el presupuesto **nunca se agotó**. `task_budget` cuenta lo del turno, no la historia reenviada: ~21k en el primer turno y casi nada después. El modelo **proyectó** que no le iba a alcanzar y se negó desde el primer turno — peor que agotarse, porque no hace falta gastar para que frene.
- **A-M27-9 verificado: la compactación round-trippea.** No era un defecto. Los bloques se guardan en el paso, se deserializan con su discriminador y se reenvían en el mensaje del asistente. Queda un test que lo clava.
- **Impacto en capas:** Domain (2 entidades, 1 enum), Application (settings, DTOs, 1 helper nuevo), Infrastructure (analista, propuestas, agentes, instructivos, motor), Web (9 vistas, 2 controllers, `site.js`, `site.css`), `nucleo/_compartido/` (nueva), tests.
- **Decisiones que se tomaron en implementación y que conviene mirar:** el estado final ante el 400 por tamaño **se dejó en `Fallida`** (una tarea Fallida ya era seguible: faltaba el mensaje, no un estado — y `Completada` habría hecho que una tarea **programada** avisara «terminó correctamente» sobre un trabajo que no se hizo); la bandera `task-budgets` pasa a declararse **siempre** (atarla al número dejaba un 400 latente); y **`OpcionMenu.Automatizar` se movió a `PrimerosPasos`** (D-M27-18) porque, con el analista como única puerta, una organización nueva quedaba sin ninguna forma visible de armar un agente.
- **Riesgos/supuestos:** (1) en producción `appsettings.Production.json` **no está versionado y gana**: tiene `MaxSeguimientosPorTarea = 20` escrito explícito, así que el default nuevo no lo toca y hay que editarlo en el server; `Anthropic.TaskBudgetTokens` **no** está escrito ahí, así que el 400.000 de `appsettings.json` sí entra solo. (2) La regla de prompt de A-M27-16 queda **escrita y sin enganchar**: las instrucciones de `plataforma` solo entran en los formatos 3/4/5 y nunca llegarían a un agente contable; engancharla es cambio de prompt (importar → evaluar → publicar) y el contenido de los rubros vive en otros repos. (3) `proponer_agente_empresa` la ofrecen **tres** prompts de plataforma y ninguna evaluación la cubre: el campo obligatorio nuevo los afecta a los tres y no se tocó ninguno. (4) `CaminoDeArranqueService` es el último enlace a `/Agentes/Crear`. (5) El analista no puede proponer un agente y su programación en la misma vuelta.
- **Pendiente de QA.** La prueba final de CA-M27-04 la hace Joaquín sobre la tarea 17 de producción.


### 2026-10-01 — M27: una sola puerta para armar un agente, y una tarea que no se corta (Discovery → Implementación)

- **Etapa:** Discovery, Análisis, Diseño, Arquitectura e Implementación, en una vuelta. Presupuesto omitido (proyecto
  personal, decisión permanente de Joaquín). **Origen: la primera demo con un cliente real**, no el roadmap.
- **Alcance:** seis frentes, todos del mismo tipo — ninguno agrega capacidades, los seis sacan del medio lo que impidió
  usar las que ya estaban. (1) El analista de automatizaciones pasa a ser la **única puerta** para armar un agente
  propio, con sus pasos cargados y listo para usar. (2) La tarea de trabajo no se corta. (3) Ningún archivo se rechaza
  en la puerta por su formato y el `.xls` viejo se lee. (4) El menú se lee de menos a más, en cuatro secciones. (5) Los
  pasos del agente quedan establecidos y editables (`AgenteOrganizacion → Instructivo`). (6) El compositor del ajuste
  deja de comerle la pantalla a la conversación — **pedido de Joaquín durante la implementación**.
- **El hallazgo que define el módulo, y cómo se encontró.** El síntoma reportado era «el límite de memoria de los chats
  está demasiado acotado». La lectura de la **tarea 17 de producción** descartó los cuatro frenos que la arquitectura
  había supuesto: terminó `Completada`, sin error, 3 ajustes contra un tope de 20, todos los pasos con `end_turn` y un
  contexto que **nunca pasó de ~60.000 tokens contra 1M de ventana**. Ningún tope del sistema actuó: el agente dijo tres
  veces, textual, que no le quedaba contexto —*«No tengo espacio de contexto suficiente en esta conversación»*— y se
  puso a dejar anotado lo que haría «en la tarea nueva». El único número que el sistema le da al modelo sobre su propio
  espacio es la cuenta regresiva de `Anthropic:TaskBudgetTokens` = **64.000**.
- **Medido, no deducido.** Dos corridas reales contra la API sobre la misma conversación de 4 turnos y 57.580 tokens de
  entrada, con 11 partidas no conciliadas plantadas a propósito: con **64.000** devolvió 3.417 tokens de salida y
  **ninguna** de las 11, diciendo «ya no tengo capacidad disponible en esta sesión»; con **400.000** devolvió 42.884 y
  **las 11**, con comprobante e importe. El presupuesto **nunca se agotó**: cuenta lo que el modelo genera más los
  resultados de herramienta que lee en ese turno, no la historia que se reenvía — así que la primera explicación
  («56-60k de entrada contra 64.000») era **falsa**, y quedó corregida en las definiciones. El mecanismo real es peor:
  **el modelo no se queda sin presupuesto, proyecta que no le va a alcanzar y se niega de antemano.**
- **Decisiones de Joaquín (2026-10-01):** el analista es la **única** puerta y el formulario queda solo para editar ·
  sin tope de ajustes, compactar y seguir, con el tope de gasto como único freno · Office viejo leído y el resto
  guardado en vez de rechazado · menú reordenado sin perder ninguna opción · los **tres** prompts que ofrecen
  `proponer_agente_empresa` se tocan y se corre la evaluación de aprobación · la regla «una tarea no se cierra pidiendo
  abrir otra» va como **instrucción transversal del núcleo**, no en `plataforma`.
- **Auditoría de pre-implementación (60 agentes, solo lectura, refutación adversarial + crítico de completitud).** Los
  ocho frentes volvieron «sí, con cambios» y aparecieron **doce zonas que el mapa por capa no nombraba**. Dos anulaban
  un frente entero: el rechazo por formato vive en `wwwroot/js/documentos.js` (el `.xls` **nunca llegaba al servidor**)
  y el descarte del `switch` de extracción mandaba lo desconocido a `ExtractorTexto` (un `.exe` quedaba **`Legible` con
  basura** que el agente iba a leer). Y un defecto que **no ve ningún frente solo**: `OpcionMenu.Automatizar` estaba
  detrás de la etapa `TuFormaDeTrabajar`, así que con el frente 1 **una organización nueva quedaba sin ninguna forma
  visible de crear un agente**, justo en la etapa donde el camino de arranque de M26 le pide su primer agente propio.
- **Errores propios corregidos antes de implementar:** «todo en un solo `SaveChanges`» era inalcanzable y ya lo era
  antes de M27 (`GuardarAsync` hace dos dentro de su propia transacción; con el instructivo son tres — la forma correcta
  es una transacción del llamador y ninguna anidada) · `PublicarParaEmpresa` **no** exige Director, el gate real es
  `PuedeResolverTipo` · poner los topes en **0** invertía el comportamiento en dos lugares distintos, porque las guardas
  comparan con `>=` · poner `TaskBudgetTokens` en 0 puede **400-ear** todos los pedidos de los modelos grandes y
  contradice de palabra una regla permanente del `CLAUDE.md` · el menú tiene **25** opciones, no 20 · el escalonamiento
  ante el 400 no podía vivir donde decía (corre en un scope nuevo, sin conversación) y «nunca `Fallida`» estaba mal
  planteado: una tarea `Fallida` ya es terminada y seguible, faltaba un **mensaje**, no un estado.
- **Lo que se descartó con evidencia de producción, no por inspección:** que el prompt del agente le dijera que difiera
  trabajo. Se leyó el **prompt publicado que corrió** (`ArtefactoVersion 60`, `cont-conciliacion`, rubro `contable`, más
  una instrucción de organización de una línea) y no dice nada parecido: «fijá el alcance» es qué cuenta y qué período, y
  «avanzar igual lo decide una persona» es no cerrar una diferencia sin explicar. Una auditoría interna afirmó lo
  contrario leyendo un archivo fuente de otro repo; **vale el prompt publicado, que es el que viaja y tiene hash.**
- **Dos defectos de permisos que el reordenamiento del menú iba a congelar:** «Configurar conversando» y «Repartir
  trabajo conversando» se le **ofrecían a un Empleado** aunque sus controllers son `RequireDirector` —el enlace estaba y
  daba 403—, y `Miembros` era el único ítem sin `VeEnMenu`. `EtapasEntrega.SoloDirector` ya tenía la respuesta escrita;
  el layout no la consultaba. Ahora `VeEnMenu` chequea etapa **y** rol: una sola condición por opción.
- **Impacto en capas.** *Domain:* `AgenteOrganizacion.InstructivoId`, dos columnas en `PropuestaTrabajo`,
  `TipoDocumento` con el valor desconocido. *Application:* topes del motor, `EtapasEntrega` (el analista entra en la
  primera etapa), textos de documentos, esquema de `proponer_agente_empresa` (tope de instrucciones de 8.000 a 30.000:
  el esquema mentía contra un servidor que acepta 30.000). *Infrastructure:* `ProcesadorTareas`,
  `ProveedorModeloAnthropic`, `PropuestaTrabajoService`, `HerramientasAnalista`, `ValidadorContenidoArchivo`, extractor
  nuevo de planilla binaria (NPOI), `PermisosOrganizacion`. *Web:* catálogo y ficha de agentes, analista, detalle de
  tarea, compositor (`site.js` + tokens nuevos), zona de subida, `documentos.js`, `MenuOrganizacion` y `_Layout` (219
  líneas menos). *Núcleo:* instrucción transversal enganchada en los cuatro rubros, contrato compartido de la
  herramienta, cuatro casos de evaluación. **Una migración:** `UnificacionAgentesM27`.
- **Estado:** `dotnet build` limpio, **1120 tests verdes** (el menú trajo 29 nuevos, la prueba automática que la
  arquitectura había dado por imposible). **Siete commits locales, sin push.** Plan de QA escrito: 105 casos en 3 lotes,
  **sin ejecutar**.
- **Pendiente y bloqueante para cerrar:** (a) importar, evaluar y publicar las tres suites de plataforma —aprobado por
  Joaquín, con costo, corre con Opus 5—; (b) **el despliegue a producción**, que es lo que habilita la prueba de la
  tarea 17: migración más editar `appsettings.Production.json`, que **no está versionado y gana** sobre el default de
  C# (tiene `MaxSeguimientosPorTarea = 20` escrito explícito); (c) ejecutar los 105 casos de QA.
- **Riesgos/supuestos.** Sacar el tope de ajustes deja al **tope de gasto de M6 como único freno**: es el riesgo
  deliberado del módulo y lo que lo hace tolerable es que ya existe, ya avisa al 80 % y ya corta — **ningún valor de M6
  se tocó**. Aceptar cualquier formato convierte el almacén en un lugar donde un tercero sube bytes arbitrarios, y lo
  único que lo mantiene inofensivo es que **nunca se sirvan con su propio tipo**: `octet-stream` + `attachment` se puso
  donde se guarda el `TipoContenido`, no en cada controller, y el camino *inline* funciona por lista blanca. Publicar
  directo lo que propuso un modelo saca una revisión que existía de hecho (el agente nacía en borrador y alguien lo
  terminaba en el formulario): la revisión **se adelanta** a la tarjeta, que muestra instrucciones, pasos, herramientas y
  alcance antes del botón. Y el analista pasa a ser camino crítico: `Agentes/Crear` sigue existiendo y alcanzable por
  URL, así que una falla degrada a «hay que saber la URL», no a «no se pueden crear agentes».
- **Lo que queda como método, que vale más que el módulo.** De 24 hallazgos graves refutados por dos escépticos cada
  uno sobrevivieron 3; pero el agente que solo pregunta *qué no se miró* encontró **doce zonas enteras** sin auditor
  asignado, y dos de ellas anulaban un frente completo. En un módulo que nace de una demo —donde el síntoma lo reporta
  quien mira la pantalla, no quien lee el log— **leer el estado real antes de diseñar el arreglo no es prolijidad: es la
  diferencia entre arreglar y no arreglar.** Tres de los cuatro arreglos del frente 2 estaban diseñados contra una causa
  que no existía, y lo único que impidió implementarlos igual fue que «reproducir primero» era el requisito número uno y
  no una verificación al final.

## 2026-10-02 - M29 CERRADO + despliegue a produccion + publicacion BLOQUEADA por saldo

- **M29 (dos features pedidas por Joaquin) cerrado.** (A) la **casilla de buscar en internet** en el chat libre; (B) un
  archivo que se sube a la conversacion y **se guarda en la carpeta de un cliente o se descarta**. **1223 tests verdes**
  (de 1164 al abrir M29), build limpio, **dos migraciones** (`DocumentoSinClienteM29`, `DuenoDelTransitorioM29`),
  **11 commits locales sin push**. QA: **4 corridas (2 lotes + re-verificacion + la de M28)**, **apto, liberable**.
- **(B) es la respuesta a OLV-036, y es mejor que la que tenia la arquitectura.** M28 cerro diciendo que *un documento
  de la empresa sin cliente no existe en el modelo* y que resolverlo pedia tres decisiones de producto. La respuesta de
  Joaquin **esquiva el problema en vez de pelearlo**: el archivo no vive sin dueño para siempre — o se guarda en un
  cliente (y es un documento normal) o se usa y se descarta. Tres decisiones abiertas se volvieron una sola pregunta
  operativa, *cuando se descarta*, que tambien quedo contestada (a los N dias de terminada la conversacion, 7 por
  defecto, y **0 apaga la purga**, no significa «descartar todo ya»).
- **El riesgo central de M29 era el portal del cliente, y paso por SIETE caminos.** Volver `ClienteCarteraId` nulable
  toca `IClienteOwned` y el `FiltroCliente`, que es la frontera que M18 construyo porque el usuario cliente vive
  **adentro** del tenant del estudio. En SQL un `NULL` **filtra bien por casualidad**, y «bien por casualidad» no es una
  garantia. QA aplico una regla nueva —**cerrar el inventario por la lista de LECTORES de la entidad, no por recorrido
  de pantallas** (MH-041)— y aparecieron dos caminos que la implementacion no habia cubierto
  (`PortalDocumentos/Renombrar` y `/DarDeBaja` por id forzado): **pasan**. Con el peor caso sembrado en base
  (`ClienteCarteraId NULL` + `VisibleParaCliente = 1`), mutacion verificada y control positivo del Director.
- **Dos afirmaciones MIAS que la implementacion refuto contra el codigo, y las dos a tiempo:** (1) **B-03 era
  factualmente falso** —el `clienteId` **si** esta en la ruta en disco—, y seguirlo al pie dejaba todo documento
  guardado en un cliente apuntando a bytes que nadie busca, **sin fallar en el momento**; se corrigio con un `Mover`
  antes del commit, y QA lo verifico **con los bytes y el hash**. (2) El dueño del transitorio: reutilizar
  `GeneradoEnTareaId` habria hecho que un archivo subido por una persona apareciera como **entregable del agente** y le
  comiera el tope de la impresora — dos significados con dos lectores son dos columnas.
- **El hueco de seguridad que la implementacion declaro en vez de saner en silencio (B-07):** un transitorio no aparece
  en ningun listado, **pero su id alcanzaba** para adjuntarselo desde otra conversacion de la propia organizacion. El
  valor de «usar solo en esta conversacion» **es la promesa de que el archivo no queda a mano de nadie**, asi que se
  cerro: un documento sin cliente pertenece a la conversacion en la que nacio. Y era **el mismo dato que la purga
  necesitaba**.
- **4 defectos de QA, los 4 cerrados y re-verificados** (OLV-038 major, OLV-039, OLV-040, OLV-041). Tres eran **la misma
  clase, por tercera y cuarta vez**: *la superficie que **relee** el hilo se queda sin un dato que la que lo **escribe**
  si tiene*. Al cerrar el ultimo se compararon los dos renderizadores campo por campo, y ahi aparecio que **el arreglo
  obvio abria el mismo defecto invertido** (el JS no nombra al cliente cuando la lista ya esta filtrada por uno): la
  regla quedo escrita una vez y valiendo para los dos lados.

### El despliegue a produccion: HECHO

Autorizado por Joaquin («publicar y desplegar a produccion»). `scripts/deploy-prod.ps1 -Force`: **migraciones aplicadas
contra la base de produccion**, sitio sincronizado (25 cambios, 3 archivos nuevos entre ellos `chat-libre-3d.js`), y
**`/health/vivo` respondio 200**. Precio del token **verificado contra la pagina oficial** antes de tocar nada: coincide.

### La publicacion: BLOQUEADA, y no por el codigo

**El chat libre NO esta disponible todavia**, y el motivo es el gate que funciona: *ningun prompt se publica sin
evaluacion aprobada*. Tres corridas reales contra produccion sobre el prompt del cuarto agente de plataforma:

| Corrida | Version | Resultado | Costo |
|---|---|---|---|
| #18 | v1 | 12/17 · 4 fallos · 1 error → **no aprobada** | USD 1,43 |
| #19 | v2 | **16/17** · 1 fallo (de seguridad) → **Rechazada** | USD 1,66 |
| #20 | v3 | 7/17 · **0 fallos** · 10 con error → **cortada** | USD 0,75 |

- **La #18 encontro trabajo real:** el agente no usaba `proponer_programacion` ni `proponer_agente_empresa`, que es
  exactamente *crear automatizaciones mencionando*. El prompt no alcanzaba con un modelo real, aunque el codigo, los
  tests y QA estuvieran verdes. **Eso es para lo que existe la evaluacion.**
- **Dos defectos de los CASOS, no del prompt, y se arreglaron haciendolos mas duros, nunca mas blandos:** uno se
  **contradecia solo** (el criterio premiaba preguntar primero y la verificacion exigia la herramienta en el mismo
  turno: premiaba y castigaba la misma conducta), y otro media **lo incalificable** — hallazgo que destrabo tres casos:
  **el revisor automatico solo ve el texto final de la respuesta, nunca la entrada de una herramienta**, asi que un
  criterio sobre el contenido de una tarjeta no se puede juzgar por construccion. La suite del analista ya respetaba esa
  convencion; la del chat libre se habia salido.
- **El fallo de la #19 era varianza, no regresion**, y resulto ser algo peor y mas interesante: **alucinacion de
  accion**. El modelo escribio *«no es un dato para anotar en memoria, es una regla… asi que la **deje** como tarjeta»*,
  describio la tarjeta completa, cerro con *«se termina con el boton Aplicar»*, y **nunca llamo a la herramienta**. Los
  dos criterios de texto en verde y la accion inexistente: la contracara exacta del hallazgo anterior. El prompt ahora
  dice que **dejar una tarjeta ES llamar a la herramienta**, y en la #20 ese caso **paso**.
- **La #20 se corto por algo que no es del sistema:** `Your credit balance is too low to access the Anthropic API`.
  Verificado aparte con la llamada mas barata posible (Haiku, 5 tokens de salida): **la cuenta de Anthropic no tiene
  saldo**. 7 pasaron, **0 fallaron**, 10 quedaron con error de credito.

### Lo urgente, que es mas grande que la publicacion

**Sin saldo en la cuenta de Anthropic, ninguna tarea de agente funciona en produccion** — no es solo que no se pueda
publicar el chat libre: es que el producto en vivo esta sin motor. El error viaja como un 400 del proveedor, asi que
cualquier cliente que mande una tarea ahora la ve fallar.

**Lo que sigue, en orden, cuando haya saldo:**
1. Cargar credito en la cuenta de Anthropic (Plans & Billing).
2. `evaluacion-reintentar 20 --confirmar` — vuelve a correr **solo** los 10 casos que quedaron con error, no los 17.
3. Si la corrida queda aprobada: `publicar 66` (la v3, que es la que tiene el prompt bueno).
4. Humo minimo en produccion: abrir el chat libre, escribir `@`, y probar la casilla de internet.

**Dato de presupuesto:** USD 3,84 gastados de la bolsa mensual de pruebas de USD 30 (que es un tope interno, distinto
del saldo de la cuenta).

### Lo que quedo en Borrador en produccion a proposito, y es decision de Joaquin

- **`chat-libre` v1 (#63) y v2 (#65)**: versiones viejas del prompt. La buena es la **v3 (#66)**.
- **`analista-automatizaciones` v3 (#62)** y **`01-un-agente-propio-nace-usable` v1 (#64)**: cambios de M27 que nunca se
  publicaron a produccion. **No los publique**: cambian el comportamiento de agentes que hoy andan, y eso no era parte
  de lo pedido.
- La instruccion compartida `00-como-trabajan-los-agentes-de-olvidata` dice «los otros **dos** agentes» y ofrece
  herramientas que el chat libre no tiene: quedo declarado, sin tocar, porque corregirla **cambia a los cuatro**.
- **Opus 5.5 cuesta 4/20 contra 5/25 de Opus 5**: las evaluaciones correrian ~20 % mas baratas. Sin aplicar.

## 2026-10-03 - M30 (el menu en seis secciones) y M31 (la barra de opciones y el isotipo) CERRADOS

**QA: los dos APTO, 23/23 criterios PASS, 0 FAIL, 0 BLOCKED, cero defectos.** 1243 tests verdes, build limpio, sin
migracion, 2 commits locales sin push. **Nada publicado ni desplegado.**

### M30 — El menu, de cuatro secciones a seis

- **Pedido de Joaquin: «reestructurar opciones de menu».** Se le ofrecieron tres alcances y eligio **la reestructura
  completa**. El criterio **no cambio**: sigue siendo el de M27 —*el nombre de cada seccion contesta «¿cuando entro
  aca?»*—; lo que cambio es que se aplico a tres lugares donde el menu se habia escapado.
- **Los tres hallazgos, ninguno de gusto:**
  1. **Las cuatro conversaciones de plataforma habian quedado en TRES secciones distintas.** *Chat libre* en «Trabajo
     diario», *Automatizar* en «Empezar aca», *Configurar* y *Repartir* en «Tu forma de trabajar». **M28 metio la cuarta
     hermana en otra seccion y nadie reviso el conjunto.**
  2. **«Administracion y cuenta» tenia 9 items y tres no eran administracion, y la etapa de entrega lo demuestra:**
     *Pedidos* y *Material de Olvidata* caen en `PrimerosPasos` —se ven el dia uno y no exigen ser Director—, y
     *Pedidos* tiene escrito en su propio comentario *«cualquier miembro los arma y los revisa»*. Estar en la seccion
     que el codigo define como «lo del Director y lo de la cuenta» es una **contradiccion verificable**, no una opinion.
  3. **«Tu forma de trabajar» mezclaba escribir con correr.** Reglas/Instructivos/Memoria son `TuFormaDeTrabajar`;
     Programaciones/Resultados/Pruebas son `SistemaCompleto`: **la etapa ya las separaba y la seccion no.**
- **Reparto nuevo: 1 · 4 · 7 · 3 · 3 · 8 = 26.** **D-06: se movio SOLO de seccion.** Ningun rotulo, icono, ruta, etapa
  ni rol cambio, y `EtapasEntrega.cs` no se toco.
- **RD-01 era el riesgo y quedo cerrado con un test de mutacion.** Mover items es exactamente donde se escapa un
  permiso (antes de M27, *Miembros* colgaba de un `@if (EsDirector)` que envolvia a varios). El test compara, opcion por
  opcion, contra `OpcionesVisibles(etapa, esDirector)` —**la tabla rotulo→opcion esta duplicada a proposito en el
  test**, porque derivarla del menu haria que un cambio pasara los dos lados a la vez—. Quitandole su `OpcionMenu` a
  *Miembros*, el defecto literal de RD-01, **fallan las tres variantes**.
- **QA verifico las 6 combinaciones etapa × rol contra `OpcionesVisibles`: 12/10 · 19/14 · 26/19, exactas.** Las 26 rutas
  devuelven 200 y el Empleado contra las 7 de Director recibe acceso denegado en 6; la septima (`Pruebas`) abre en solo
  lectura **por decision declarada de M22** y `Correr` responde 403.

### M31 — La barra de opciones del chat, y la pieza que por fin es la marca

- **Dos pedidos de Joaquin:** las cuatro acciones a una **barra lateral derecha** como configuracion del chat, que **no
  ocupe mucho porque lo importante es el chat**; y que `piezaChatLibre`, que tenia un **icono generico**, sea algo de la
  **marca**, diseñado con el isotipo de Olvidata.
- **Sobre la herramienta pedida (`/motion-graphics`): se tomo la idea entera y se cambio el medio.** Esa tuberia produce
  un MP4 o un WebM con alfa, y para este destino es la herramienta equivocada **por una razon de fondo: un video trae
  los colores quemados**, asi que no puede seguir el tema claro y el oscuro, que es requisito del portal (CA-07.4), y
  pesa mas que lo que reemplaza. (Secundario: declara macOS o Linux y la maquina es Windows.) La pieza se anima **en la
  pagina**, con los tokens `--ov-*`, que es lo unico que hace que los dos temas salgan gratis.
- **El hallazgo que vale mas que el pedido:** **el isotipo de Olvidata YA ES el diagrama de esta pantalla.** Es un
  **nucleo central con cuatro nodos** radiando en diagonal: *una conversacion en el centro y cuatro cosas que se traen
  mencionando* — las mismas cuatro que ahora viven en la barra. No hubo que inventarle un significado: ya lo tenia. Por
  eso la pieza deja de ser un adorno con el color de la marca y pasa a ser **la figura de la pantalla**.
- **El isotipo se MIDIO, no se calco de memoria** (RD-04: un isotipo torcido se compara con el logo de la pestaña, que
  esta a diez centimetros). Transformada de distancia sobre el PNG real: nucleo r=164,3; nodos r=95,5 / 83,4 / 74,5 /
  125,4; semiancho de brazo 38,9. **Es asimetrico a proposito —los brazos van de 35° a 48°— y se copio asi.** QA
  confirmo que el SVG coincide numericamente con el PNG, asimetria incluida.
- **Dos decisiones del implementador, las dos buenas:** la rotacion **oscila** (±0,42 rad) en vez de dar la vuelta,
  porque una vuelta entera deja la figura de canto al lado del logo de la pestaña; y el pulso **no cambia de color**, es
  un engrosamiento del brazo, asi se ve igual en los dos temas.
- **La version plana dejo de ser dos anillos y un punto** —que no eran nada— y pasa a ser **el isotipo quieto en SVG**:
  con movimiento reducido la pantalla no pierde significado, solo pierde la animacion.
- **El plegado de movil reuso el mecanismo `ov-filtros` entero**, y encajo mejor de lo que suponia el diseño: su regla
  de *«arranca abierto si hay algo puesto»* **cuenta casillas tildadas**, que es exactamente RD-03 — no hubo que
  escribir nada. Lo unico cableado era el texto, que se parametrizo con los valores viejos como default, asi los
  diecisiete listados no cambian (QA lo verifico).
- **D-10 intacto y verificado de la forma correcta:** el test afirma que la compuerta de `prefers-reduced-motion` esta
  **antes del `import()` por posicion en el archivo**, no por presencia — es la unica forma de que signifique «no se
  baja un byte». QA lo confirmo en la pestaña de red, y que al enviar **el canvas sale del DOM** (rAF congelado).
- **Adjuntar se quedo en el compositor** (D-02): un archivo adjunto es **contenido del mensaje**, no configuracion, y
  partir una sola interaccion en dos lugares es peor que la inconsistencia que arregla.

### Dos trampas de medicion que QA dejo anotadas

El menu se lee **cacheado 60 s** (`ResolvedorSesion.Ttl`), y `jQuery.trigger('change')` **no dispara listeners nativos
de ancestros**. Las dos casi producen un FAIL falso; las dos quedaron en la memoria de QA.

## 2026-10-05 - Despliegue a produccion de la quinta pantalla, M30 y M31

- **`scripts/deploy-prod.ps1 -Force` contra agentes.olvidata.com.ar.** Arbol limpio, HEAD en `4c70808`,
  **1243 tests verdes corridos antes de tocar nada**. **Sin migraciones nuevas**: las dos de M29
  (`DocumentoSinClienteM29`, `DuenoDelTransitorioM29`) ya se habian aplicado en el despliegue del 2026-10-02, asi que
  el paso de migracion no cambio el esquema.
- **Lo que fue:** la quinta pantalla de subida (`Agentes/Ejecutar` sin cliente), **M30** (el menu en seis secciones) y
  **M31** (la barra de opciones del chat y la pieza que pasa a ser el isotipo). **21 archivos actualizados**, ninguno
  agregado ni borrado.
- **Verificado desde afuera, sin tocar datos:** `/health/vivo` 200 y `/Account/Login` 200; y los tres archivos que
  cambiaron llegaron con su tamaño nuevo — `site.js` 30.449 -> **31.216** (el plegado parametrizado), `site.css`
  71.420 -> **74.702** (la barra y el isotipo) y `chat-libre-3d.js` 8.505 -> **14.329** (la geometria del isotipo, con
  34 menciones de nucleo/nodo/brazo en el archivo servido: **la pieza nueva es la que esta en produccion**, no la vieja
  cacheada).
- **Lo que sigue sin cambiar: el saldo de Anthropic.** El codigo esta entero en produccion, pero **ninguna tarea de
  agente funciona** hasta que haya credito, y el chat libre sigue sin publicar (agente en Borrador, menu que no lo
  ofrece). Este despliegue no mueve esa aguja ni la empeora.

## 2026-10-05 - M32 tanda 1: la respuesta cortada deja de matar la tarea

- **Caso real de Joaquin:** *«La respuesta supero el maximo de tokens configurado» ante una conciliacion. «Desestimar
  este tope. Es mas importante que complete la tarea.»*
- **El hallazgo: el tope no era el problema y no era arbitrario.** `AnthropicSettings.MaxTokens = 16000` es
  **exactamente** el valor que la documentacion oficial recomienda para pedidos **sin streaming** (verificado el
  2026-10-05 con la skill `claude-api`), y `ProveedorModeloAnthropic` **no transmite en ningun lado**. Subirlo sin mas
  no es desestimar un tope: es **cambiar un corte por un timeout de HTTP**, que es peor porque el timeout no deja ni el
  trabajo parcial. Dato duro: Sonnet 5 y Opus 5 llegan a **128.000 tokens de salida**, pero los SDK **exigen streaming**
  por encima de ~16.000.
- **El defecto real: la tarea moria.** `FinalizarAsync` marcaba `MotivoFin.MaxTokens` como **`Fallida`**, asi que una
  conciliacion que cruzo 470 lineas de cada lado y se quedo sin lugar en el ultimo parrafo terminaba igual que una que
  no arranco. **Y el sistema ya sabia que estaba mal:** el `EnviarConEscalonamientoAsync` de M27 tiene escrito
  *«lo que nunca pasa es que quede Fallida y haya que empezar de cero»*, pero eso cubre el rechazo por tamaño **de
  entrada**. Por el lado de la **salida** seguia muriendo: **la misma falla que M27 fue a eliminar, entrando por la otra
  puerta.**
- **Y una contradiccion de 25 a 1:** `TaskBudgetTokens = 400.000` contra `MaxTokens = 16.000`. Le deciamos al modelo que
  tenia 400.000 para la tarea y le cortabamos cada respuesta en 16.000 — justo despues de que M27 subiera el presupuesto
  para que planificara una salida grande (midio 42.884 tokens de salida en una conciliacion real).
- **D-01 implementado: una respuesta cortada se continua y la tarea nunca queda `Fallida`.** El mecanismo **ya existia y
  no era de M27**: es la rama `PausaTurno` de M14, y `ReconstruirConversacion` ya deja el turno parcial como mensaje del
  asistente, asi que el modelo **sigue sin reescribir**. Tope de continuaciones configurable (3); **0 o negativo = sin
  continuaciones**, el comportamiento viejo **menos la muerte**, con test de los tres lados.
- **Dos defectos que el brief no nombraba y encontro el implementador:** `tarea.Resultado` salia del **ultimo paso**, asi
  que una respuesta continuada habria terminado `Completada` mostrando **solo el ultimo tramo**; y `ServicioTareas` solo
  asignaba `turno.Respuesta` en un paso `FinTurno`, asi que un turno cortado y agotado **no mostraba ninguna respuesta**
  en la conversacion. La segunda la encontro un test al fallar. Mas un tercero: la API **rechaza el pedido entero** si el
  mensaje del asistente termina en espacios, y un corte cae donde cae — sin recortarlo, la continuacion se convertia en
  un 400 y la tarea volvia a morir por otra puerta.
- **Riesgo abierto que NO se puede cerrar hoy, y queda declarado.** La documentacion dice textual que *un `messages` que
  termina en `role: "assistant"` es un prefill y devuelve **400** en `claude-sonnet-5` y `claude-opus-5`* — y el modelo
  por defecto del proyecto es Sonnet 5. Puede que la API distinga «continuar un turno pausado» de «prefill» (el camino
  de `pause_turn` anda en produccion), **pero no se puede comprobar: la cuenta de Anthropic esta sin saldo**, y los
  tests corren con el modelo simulado, que no valida esto. **Misma leccion que la evaluacion del chat libre: codigo
  verde no quiere decir que funciona contra el modelo real.**
- **Por eso la tanda 1b: una continuacion que falla NUNCA mata la tarea.** `catch` estrecho —solo mientras se continua y
  solo si no es cancelacion— que cierra la tarea **`Completada` y seguible** con los tramos ya pagados, y **no la
  devuelve a la cola** a repetir el mismo error. El error de una llamada normal **sigue subiendo** (con test). Vale por
  si solo aunque el prefill ande: **una continuacion es una llamada de mas que nadie pidio, asi que su fallo no puede
  costar mas que no haberla intentado.** Y la nota del motor registra **que** fallo, con el tipo de excepcion: el dia que
  haya saldo, eso es lo unico que va a decir si el prefill es el problema.
- **Bug encontrado al escribir la guarda:** el numero del paso de la nota no podia ser `siguienteNumero`, porque el
  escalonamiento de M27 pudo dejar notas antes del fallo y repetir un numero **rompe el `SaveChanges` entero** (indice
  unico tarea+numero). Se lee de la base.
- **Dos consecuencias conocidas, escritas y no tapadas:** una tarea **programada** va a decir «termino correctamente»
  sobre una respuesta cortada (`EjecutorProgramaciones` elige por `== Completada`), con el puntero al lugar del aviso; y
  si el pedido de la continuacion no entra **por tamaño**, lo atrapa antes el escalonamiento de M27 y la tarea queda
  `Fallida` —terminada, seguible y con todos los tramos guardados—.
- **Estado: 1255 tests verdes** (de 1243), build limpio, **sin migracion**, 2 commits locales sin push, **sin desplegar**.
- **Tanda 2 (streaming + `MaxTokens` a 64.000) NO se hizo, y es una recomendacion, no un olvido.** Streaming toca el
  camino de llamada de **todo** el motor —pasa por ahi cada tarea de cada organizacion— y **no se puede verificar contra
  la API real sin saldo**. Ademas la tanda 1 ya entrega el objetivo: con 16.000 por respuesta y 3 continuaciones son
  ~64.000 de salida, que es exactamente el techo que habilitaria el streaming. Lo que falta ganar es **costo** (menos
  llamadas, menos contexto reenviado) y **sacarse de encima la duda del prefill**. Se hace con saldo y con la API
  delante.

## Historial de ajustes

### Bloques archivados (2026-10-05)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 15 bloques (2026-09-14 a 2026-09-14) → [`trazabilidad-2026-09-4.md`](historial/trazabilidad-2026-09-4.md)


### Bloques archivados (2026-10-05)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-10** — 1 bloques (2026-10-03 a 2026-10-03) → [`trazabilidad-2026-10-2.md`](historial/trazabilidad-2026-10-2.md)


### Bloques archivados (2026-10-03)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 11 bloques (2026-09-14 a 2026-09-28) → [`trazabilidad-2026-09-3.md`](historial/trazabilidad-2026-09-3.md)


### Bloques archivados (2026-10-03)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-10** — 1 bloques (2026-10-03 a 2026-10-03) → [`trazabilidad-2026-10.md`](historial/trazabilidad-2026-10.md)


### Bloques archivados (2026-10-03)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 1 bloques (2026-09-14 a 2026-09-14) → [`trazabilidad-2026-09-2.md`](historial/trazabilidad-2026-09-2.md)


### Bloques archivados (2026-10-03)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **M28** — 1 bloques (2026-10-02 a 2026-10-02) → [`trazabilidad-M28-2.md`](historial/trazabilidad-M28-2.md)


### Bloques archivados (2026-10-02)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **M28** — 4 bloques (2026-10-02 a 2026-10-02) → [`trazabilidad-M28.md`](historial/trazabilidad-M28.md)


### 2026-10-02 - agentes-ia-implementador (M28, tanda 1: solo el motor)
- **Etapa:** 5 (Implementación). Definiciones 1, 2 y 3 aprobadas; presupuesto omitido (proyecto personal). Alcance: los pasos **1 a 6** del orden de implementación de A-02. Los pasos 7 (vista de arranque, autocomplete de `@` en `site.js`, CSS) y 8 (pieza 3D) son la **tanda 2**.
- **Cambio:** 1 commit local en `Olvidata Agentes Multi-rubro` (`d7ee4c8`), sin push y sin deploy. **1141 tests verdes** (eran 1140). **Sin migración EF**, como fijó A-00: `TareaAgente.Tipo` no tiene línea en su configuración y el snapshot lo guarda como `int`.
- **Lo que ordena el frente:** `ClasesDeTarea.EsDePlataforma` es la palanca — con una línea, memoria, calcular, instructivos y `adjunto_leer` aceptan la conversación nueva sin tocarlas una por una. Y `IAgentesDisponiblesQuery` (A-03b) deja de ser deuda: los dos `IQueryable` de «qué agentes puede usar esta persona» estaban copiados en tres clases y M28 iba a ser la cuarta copia.
- **Los dos modos de subagentes, separados de verdad:** `SubagentesPermitidosAsync` quedó como un `switch` con lista blanca de `TipoTarea` y **dos ramas con nombre** (`ModoJerarquiaAsync` / `ModoAbiertoAsync`), no un `if` adentro del predicado. El modo jerarquía no cambió una línea de comportamiento. El código del modo abierto **lleva el rubro** (`b-<rubro>/<slug>`): sin agente base, dos rubros pueden tener el mismo slug y un código ambiguo elegiría el agente equivocado en silencio.
- **Tres defectos preexistentes que destapó el tipo nuevo, los tres arreglados:**
  1. **El grave, y no estaba en la tabla A-02.** `ProcesadorTareas` buscaba las partes ya creadas solo si `tarea.Tipo == Trabajo`, así que un chat libre reanudado **no encontraba la parte que él mismo había creado y creaba otra en cada vuelta** —una tarea y un costo por sondeo— y quedaba colgado en `EsperandoSubtareas` para siempre. Lo encontró el test de la mención (2 llamadas al modelo, 2 partes), no una lectura del código.
  2. `ArmarEvaluacionAsync` cubría solo los formatos 3 y 4: **evaluar el analista usaba la declaración de precedencia del formato 1**. Era R-A6, ya anticipado. El mismo agujero estaba en `AnatomiaAgenteService.Declaracion`.
  3. `ConsumoService` resolvía el nombre del agente solo para tareas de `Trabajo`, así que el asistente y el analista salían como «Agente», **una fila por versión**.
- **Impacto en capas:** Domain (1 valor de enum), Application (constante de formato, 2 interfaces nuevas, 1 query compartida, 1 opción de menú, 1 permiso, 1 flag de DTO, los mensajes), Infrastructure (el wrapper de contexto, el arranque de tarea, ~12 switches, los dos modos de subagentes, el permiso, los tres llamadores migrados), Web (1 controller, 1 ViewModel, 1 vista funcional, 1 ítem de menú, 3 `<option>` del filtro), núcleo (1 prompt, 1 línea del manifiesto, 1 suite de 6 casos), tests (18 nuevos + 1 golden + 1 entorno).
- **Decisiones que se tomaron en implementación:** el prompt del chat libre **no declara `herramientas`** en su frontmatter —todo lo que usa se lo da la plataforma según la conversación, y declararlas ofrecería `delegar_subagente` incluso en una organización sin ningún agente—; el `ResolvedorHerramientas` las ofrece con las **mismas dos condiciones** que en una tarea de trabajo (profundidad y que haya al menos un agente), fail-closed; se agregó `InternalsVisibleTo` para el proyecto de tests, para poder afirmar los switches internos directo en vez de probar que «funciona».
- **Hueco de alcance declarado, que necesita decisión del arquitecto:** el chat libre **todavía no propone** reglas, instructivos, programaciones ni agentes, así que **CU-03 no tiene camino** y CA-03.2 / HU-04 / HU-05 no son verificables. `PoliticaProponerRegla.Para(ChatLibre)` es `null` (fail-closed) y las listas blancas de cada herramienta de propuesta son explícitas; abrirlas toca `PropuestaReglaService` y `PropuestaTrabajoService`, donde el alcance se decide por tipo de conversación — es una decisión de alcance, no un renglón. **La tabla A-02 no lo lista y el brief no incluyó CA-03.2 entre los criterios de esta tanda**, así que se dejó cerrado, documentado y con un test (`Todavia_no_se_proponen_reglas_desde_el_chat_libre`) que se rompe el día que se abra.
- **Riesgos/supuestos:** (1) **nada se publicó**: el agente queda en Borrador y el circuito `importar`/`evaluar`/`publicar` lo corre Joaquín, así que hoy la opción no se ofrece y la URL contesta «Todavía no está disponible.». (2) El `<option>` «Chat libre» del listado de Tareas solo lo ven Director y staff (`TareasController.MostrarTipo`): un Empleado **no tiene cómo filtrar sus chats**, y P3 pide decidir si ese gate se abre. (3) El arreglo del consumo cambia lo que se ve: las conversaciones del asistente y del analista pasan de «Agente» al nombre real, lo que es una regresión posible si algo dependía del nombre viejo. (4) A-03 decía que el chat libre recibe `agentes_disponibles` y A-04 que recibe el modo abierto de `subagentes_listar`: **son dos formatos de código distintos**, y se eligió el de A-04 para que no haya dos listas; si la tanda 2 arma el autocomplete contra `agentes_disponibles`, van a divergir justo en lo que R-A2 quería evitar.
- **Pendiente de QA.** El 3D, el autocomplete y el diseño del arranque no están: no tiene sentido probar la pantalla todavía más allá de que abra.


### 2026-10-02 - agentes-ia-implementador (M28, tanda 1b: CU-03, A-08 y A-09)
- **Etapa:** 5 (Implementación). Entrada: **A-07, A-08 y A-09**, que el arquitecto agregó después de la tanda 1 para cerrar el hueco que esa tanda había declarado (CU-03 sin camino). Alcance: solo motor, otra vez — ni una vista, ni CSS, ni 3D.
- **Cambio:** 1 commit local en `Olvidata Agentes Multi-rubro`, sin push y sin deploy. **1146 tests verdes** (eran 1141: se invirtió 1 y se sumaron 6). **Sin migración EF**: no se agregó ninguna entidad ni ninguna propiedad persistida; todo lo que se tocó son listas blancas de `TipoTarea`, una política y un campo `init` en memoria.
- **CU-03 / RF-05 cerrado:** `PoliticaProponerRegla.Para(ChatLibre)` deja de ser `null` y las cuatro herramientas que cargan algo (`proponer_regla`, `proponer_instructivo`, `proponer_programacion`, `proponer_agente_empresa`) aceptan la conversación nueva. **No** se sumaron `proponer_asignacion` ni `proponer_prueba`: repartir trabajo es el asistente y está fuera del alcance de M28.
- **La decisión de A-07 que más importa, aplicada tal cual:** la política decide **qué** se propone y nunca **quién** aplica. Por eso `EmpresaYAreaSoloDirector` es `false` en el chat libre —una propuesta de alcance de empresa se registra la haga quien la haga— y el Director obligatorio lo pone el service que aplica, en un solo lugar y sin duplicarse.
- **Dos alcances y no seis, declarado:** la política admite `mis_preferencias` (el default, el más chico que existe) y `empresa`. Área, agente y cliente piden un id que sale de `estructura_empresa` o de `clientes_buscar`, y el chat libre no recibe ninguna de las dos: ofrecerlos sería invitar al modelo a inventar un id. Es la misma lección del commit `5c3bd9d` (el esquema que le mentía al modelo), y por eso además `Descripcion()` ahora **arma la frase desde el conjunto de alcances** en vez de tener una fija — con un assert de regresión que afirma que para las políticas de antes el texto no se movió una letra.
- **Dos defectos que A-07 destapó, y los dos eran silenciosos (R-A1 otra vez):** (1) el `switch` de visibilidad de `PropuestaReglaService` tiene `_ => false`, así que una tarjeta de un chat libre **se guardaba bien y no la veía nadie, ni su autor** — el peor final posible para una propuesta, sin un solo error; (2) `PuedeResolver` devolvía `EsDirector` para todo tipo que no fuera `Trabajo` ni `Analista`, así que un Empleado **no podía aplicar ni su propia preferencia en su propio chat**. Los dos se arreglaron metiendo el chat libre en la rama del analista, que ya tenía la regla correcta escrita; no se estrenó ninguna regla de permisos nueva.
- **Un tercero, de desarrollo:** desde que el chat libre declara `proponer_instructivo`, el `ProveedorModeloSimulado` lo reconocía como una conversación de configuración (lo detecta por los nombres exactos de esas herramientas) y en dev pasaba a contestar como el configurador. Se resolvió con una **marca explícita** (`SolicitudModelo.EsChatLibre`), igual que el guion de M8 y por la misma lección RT-M7-06: marcador propio, nunca adivinar por los nombres de las herramientas.
- **A-08: confirmado, nada que cambiar.** La tanda 1 ya había elegido A-04 con el rubro en el código y una sola lista; A-03 queda superada en ese punto. Queda anotado en `5-implementador.md` para la tanda 2: **el autocomplete se arma contra `IAgentesDisponiblesQuery`**, no contra `agentes_disponibles`, o divergen justo en lo que R-A2 quería evitar. Y el código de agente de las propuestas de programación y de agente propio sale de `subagentes_listar`, que en el chat libre es esa misma consulta: una sola lista, también para configurar.
- **A-09: se amplió filtrar, nunca ver.** `TareasController.MostrarTipo` pasó de `EsDirector || EsStaff` a `EsMiembro || EsStaff`, y no se tocó una línea de `ServicioTareas.Visibles()`. Un test afirma las dos mitades en el mismo caso: el Empleado encuentra **su** chat con el filtro y el de otro Empleado **no aparece**.
- **Impacto en capas:** Application (1 política, 1 método privado de descripción, 1 campo `init` de `SolicitudModelo`), Infrastructure (4 listas blancas de herramientas, 1 `TienePermiso`, las 8 compuertas de `PropuestaReglaService` y las 6 de `PropuestaTrabajoService`, el detalle de tarea y el proveedor simulado), Web (**1 línea**: `MostrarTipo`), núcleo (frontmatter con las cuatro herramientas + sección 3 del prompt reescrita + la suite de 6 a 12 casos), tests (1 invertido, 5 nuevos, el entorno).
- **Riesgos/supuestos:** (1) **nada se publicó**: el agente sigue en Borrador y el circuito `importar`/`evaluar`/`publicar` lo corre Joaquín — hasta entonces los casos nuevos de la suite no se corrieron nunca contra el modelo real, así que el prompt de la sección 3 está **sin evaluar**. (2) `proponer_instructivo` y `proponer_agente_empresa` siguen rechazando «empresa» a quien no dirige **ya al proponer**: es la conducta de M15, compartida y sin tocar, así que CA-03.2 se verifica por `proponer_regla`, que es donde A-07 lo pidió explícitamente. (3) El chat libre **no tiene `mis_automatizaciones`**: para instructivos le alcanza `instructivos_listar`, pero para programaciones y agentes propios no tiene con qué chequear duplicados. (4) El simulado ya no se confunde, pero **tampoco scripta** las cuatro tarjetas: en dev esas se prueban con el modelo real.
- **Pendiente de QA.** Las 9 pruebas mínimas nuevas están en `5-implementador.md`; la 19 (modelo simulado) es la que cubre el defecto de desarrollo.

### 2026-10-02 - agentes-ia-implementador (M28, arreglo del lote 1 de QA: OLV-028 y OLV-029)
- **Etapa:** 5 (Implementacion). Entrada: los dos partes de defecto del **lote 1 de QA** de M28, CA-01.2 textual y R-A1. Alcance cerrado: solo esos dos defectos.
- **Cambio:** 1 commit local en `Olvidata Agentes Multi-rubro`, sin push y sin deploy. **1151 tests verdes** (eran 1148: 3 nuevos). **Sin migracion EF.** Los dos defectos quedan **aplicado, pendiente de re-verificacion**: el cierre lo declara QA.
- **OLV-028 era de las cuatro conversaciones, no del chat libre.** `VeEnMenu` era etapa + rol y la disponibilidad del artefacto la chequeaban la pantalla de cada una y el catalogo, **nunca el menu**: lo mismo valia para el analista, el configurador y el asistente. Un solo arreglo para las cuatro. La tercera dimension entra **con la misma forma** que el rol en M27 -una tabla `OpcionMenu` -> slug (`IDisponibilidadPlataforma.AgentePorOpcion`) consultada desde `IPermisosOrganizacion.VeEnMenuAsync`-, no como un `if` en el layout. `VeEnMenu` queda intacta como la parte pura, que es el contrato que ya afirman los tests de etapas.
- **El costo se resolvio antes de escribirlo:** `DisponibilidadPlataforma` hace **una consulta por request** por los cuatro slugs y la memoriza en el alcance; no se usaron los cuatro `DisponibleAsync` de los services porque serian cuatro. El staff y lo que la etapa ya oculta cortan antes de tocar la base.
- **OLV-029: eran cuatro, no dos.** Ademas de los dos mapeos que nombro QA (el titulo de `Tareas/Detalle` y la columna del listado, en JS), el grep de las vistas encontro **dos mas de la misma familia**: `TieneTarjetasDeTrabajo` dejaba al chat libre afuera -asi que la pantalla no cargaba `_ScriptPropuestasTrabajo` y **ninguna tarjeta de trabajo de un chat libre se podia aplicar**, el mismo final que el defecto 1 de la tanda 1b- y el contador "sin resolver" de `_Conversacion` sumaba una sola familia. Los cuatro quedan contra **una sola tabla sin `default`** (`RotulosTipoTarea`), que el listado en JavaScript consume servida por el servidor.
- **Impacto en capas:** Application (1 interfaz + 1 tabla nuevas, 1 helper de rotulos nuevo, 1 metodo del contrato de permisos, 1 propiedad de DTO, 1 lista por inclusion), Infrastructure (1 service nuevo, `PermisosOrganizacion`, 1 linea de `ServicioTareas`), Web (`MenuOrganizacion` a async, `_Layout`, 3 vistas de Tareas), tests (1 archivo nuevo + 1 test y 1 helper en `MenuLateralTests`).
- **Riesgos/supuestos:** (1) **La tercera superficie sigue con el hueco:** `PrimerosPasos/Index.cshtml` usa `VeEnMenu` ~25 veces y puede ofrecer un acceso a una conversacion sin publicar; CA-01.2 nombra el menu y el catalogo, y cambiarlo mueve los pasos del camino de arranque de M26 -decision funcional, no arreglo-. (2) El chat libre **no esta** en `AgentesPlataforma.Presentaciones`: cumple "no se ofrece" de forma trivial, pero ofrecerlo una vez publicado es alcance que nadie pidio. (3) El arreglo 3 **cambia lo que se ve**: en un chat libre aparecen los botones de las tarjetas de trabajo, que antes no accionaban; vale re-correr HU-04 mirandolos. (4) Nada publicado: el agente sigue en Borrador (artefacto 121, version 147).

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 71 bloques (2026-09-14 a 2026-09-25) → [`trazabilidad-2026-09.md`](historial/trazabilidad-2026-09.md)

### Traza de corrida -- 2026-10-01 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna

### Traza de corrida -- 2026-10-02 / etapa implementacion (M28 tanda 1)
- Reintentos: 3 (regenerar el golden 6; `13-chat-libre.yml` invalido porque dos criterios con ": " sin comillas los lee YAML como mapa; el test de la mencion fallaba por el lookup de partes gateado a Trabajo)
- Criterios fallados: CU-03 / CA-03.2 sin camino en esta tanda (decision de alcance pendiente). CA-03.1 se cumple de forma trivial.
- Reglas releidas: ninguna instruccion; si hubo que releer el codigo de `ProcesadorTareas` (el lookup de partes no estaba en la tabla A-02) y la memoria propia "Medir sin pipe" (`dotnet test | tail` devuelve 0 aunque haya rojos).

### Traza de corrida -- 2026-10-02 / etapa implementacion (M28 tanda 1b)
- Reintentos: 1 (el assert de orden del set de alcances: HashSet<AlcanceRegla>.Order() da Organizacion antes de Usuario, no al reves)
- Criterios fallados: ninguno. CA-03.1, CA-03.2, CA-03.3, CA-03.4, CA-05.2, HU-04, HU-05 y HU-07 quedan con test propio.
- Reglas releidas: la regla permanente del CLAUDE.md del 2026-09-25 (configurar conversando propone las cuatro cosas y el rol se chequea al aplicar) y la memoria propia "Un tipo de tarea nuevo tiene mas compuertas que la tabla" -- que es exactamente lo que volvio a pasar: los dos defectos de PropuestaReglaService no estaban en ningun brief y salieron del grep de los switches por TipoTarea.

### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 1
- Criterios fallados: CA-07.1 parcial: la casilla de internet del compositor no se implemento -- el motor calcula busquedaOfrecida = trabajo && ..., ninguna conversacion de plataforma la ofrece y IniciarChatLibreAsync no tiene el parametro. Declarado, no saneado.
- Reglas releidas: instruccion 38 completa, 25 §149, memoria propia 'Las vistas no se recargan solas' y 'Medir sin pipe'


### Traza de corrida -- 2026-10-02 / etapa qa / lote 1
- Reintentos: 2 (el filtro de /Tareas es Select2 y selectOption no lo mueve -- hay que ir por $(sel).val(x).trigger('change'); y el costo acumulado de la barra sale de TareasAgente.CostoUsd, no de PasosTarea.CostoUsd, que es de donde lee el tope de gasto: fabricar en la tabla equivocada da un cero que parece un PASS)
- Criterios fallados: CA-01.2 FAIL (el menu ofrece la pantalla sin version publicada -- OLV-028). CA-T.1 parcial: PASS en la URL, BLOCKED en el adjunto por falta de control positivo (todos los documentos de la org tienen cliente y un chat libre no lo tiene). Defecto adicional encontrado fuera de los criterios: OLV-029 (rotulo del tipo nuevo por ternario con default). Los dos defectos graves que la implementacion dijo haber arreglado: el lookup de partes esta ARREGLADO y reproducido (1 parte, no una por sondeo, confirmado tambien tras reiniciar el proceso); la visibilidad de la tarjeta no se cruzo, queda del lote 3.
- Reglas releidas: instruccion 33 (verificacion automatizada y el chequeo de reglas nuevas), instruccion 39 seccion 5 (corrida por lotes), y del delta de reglas desde 2026-09-25: ELV-008 completa (aplica y da PASS), MH-027 y MH-047 completas (aplican a TipoTarea.ChatLibre=6; MH-047 fue la que destapo OLV-029). MH-033/MH-034 y los 14 items financieros restantes se descartaron por el indice sin abrir el cuerpo. Memorias propias usadas: 'costo cero por variables de entorno' (el --launch-profile https y la linea de MODELO SIMULADO), 'cuentas QA dev' (Super123! sin adivinar), 'tecnicas QA motor agentes' (el tope de gasto se fabrica en PasosTarea, no en EventosUso) y 'limpiar datos de QA' (orden de borrado y checksum).


### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 1
- Criterios fallados: ninguno, CA-01.2 queda aplicado y pendiente de re-verificacion por QA (OLV-028), igual que OLV-029
- Reglas releidas: ninguna instruccion nueva, si se releyo el codigo de M27 (VeEnMenu/MenuOrganizacion) para que la tercera dimension entre con la misma forma, y la memoria propia 'Medir sin pipe'


### Traza de corrida -- 2026-10-02 / etapa qa / lote 3
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna


### Traza de corrida -- 2026-10-02 / etapa qa / lote 2
- Reintentos: 2
- Criterios fallados: CA-02.1(D-06), CA-02.4(tarjeta), D-03(reparo)
- Reglas releidas: 30-qa-regresiones, 33#mcp, cat_resumen#MH-041, cat_resumen#MH-047
- Arranque real: 58 KB (~14k tokens)
- Nota: M28 menciones/resolucion/delegacion. 9 PASS, 2 FAIL, 2 BLOCKED. 3 partes nuevos (OLV-030 tarjeta de parte nunca se dibuja, OLV-031 TOPE=16 se come el grupo Configurar, OLV-032 atributo vacio). OLV-029 del lote 1 re-verificado PASS. R-A3 y R-A2 PASS con las dos listas reales. Costo USD 0.


### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 1
- Criterios fallados: ninguno, los cinco defectos (OLV-030 a OLV-034) quedan aplicados y pendientes de re-verificacion por QA. El test de OLV-031 cubre la mitad JS como contrato de fuente: el proyecto de tests no corre JavaScript
- Reglas releidas: A-10 de 3-arquitecto-mvc (decision de la lista blanca), D-05/D-07 de 2-disenador-funcional, los tres lotes de 6-qa, memorias propias 'Medir sin pipe' (dotnet test a archivo, nunca por pipe), 'Un tipo de tarea nuevo tiene mas compuertas que la tabla' (el grep antes de confiar), 'El default tambien vive en las vistas' y 'Los dispositivos antes que los criterios' (el boton y la accion con una sola condicion: destapo el tercer sitio de OLV-030)


### Traza de corrida -- 2026-10-02 / etapa qa / lote 4
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna


### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 2
- Criterios fallados: RF-08/CA-04.3 (OLV-036 no aplicado: pide migracion EF)
- Reglas releidas: 6-qa#ronda-de-re-verificacion, 1-analista-funcional#CA-04.1/CA-04.2/RF-08, memorias propias: 'Medir sin pipe' (dotnet test a archivo), 'El menu no chequea que el agente exista' (la condicion son tres cosas), 'El default tambien vive en las vistas', 'Un tipo de tarea nuevo tiene mas compuertas que la tabla', 'El CRLF que esta adentro del hash'
- Nota: M28 re-verificacion de los tres reparos. OLV-037 y OLV-035 APLICADOS (pendientes de re-verificacion por QA) + el enlace del autor, que el diagnostico anterior tenia solo a medias. OLV-036 PARADO Y AVISADO: subir sin cliente pide que DocumentoCartera.ClienteCarteraId sea opcional (FK + 4 indices + la ruta en disco), o sea migracion EF y una decision de producto. Build limpio, 1164/1164 (de 1160), verificado por el camino inverso. Commit local, sin push.


### Traza de corrida -- 2026-10-02 / etapa otro
- Reintentos: 2
- Criterios fallados: CU-03, OLV-033
- Reglas releidas: 39#4, 38
- Nota: M28 chat libre, orquestacion: 2 re-delegaciones por huecos del brief de arquitectura (A-02 sin el camino de propuestas; A-07 sin chequear el gate de preferencia personal)


### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 1
- Criterios fallados: ninguno
- Reglas releidas: 3-arquitecto-mvc#A-01/A-02/A-10, 1-analista-funcional#CA-01.x/D-03, 2-disenador-funcional#D-05/RD-05, memorias propias: 'Medir sin pipe', 'Un tipo de tarea nuevo tiene mas compuertas que la tabla', 'El default tambien vive en las vistas', 'El CRLF que esta adentro del hash'
- Nota: M29 frente A: la casilla de internet en el chat libre. 7 puntos de A-01 aplicados con UN predicado nuevo, ClasesDeTarea.PuedeBuscarEnInternet (lista blanca que nombra Trabajo y ChatLibre), llamado desde los 3 puntos de alcance. SIN MIGRACION (confirmado). Build limpio, 1176/1176 (de 1164, +12 casos nuevos, medido sin pipe). 1 reintento: el test del ajuste fallaba porque EntornoReglas.EjecutarAsync reclama la SIGUIENTE de la cola, no la que se le pasa -- se partio en dos tests de una tarea cada uno. Efecto lateral declarado: una ConsultaCliente deja de ver la casilla que el resolvedor nunca honraba. Frente B sin tocar. Commit local, sin push.


### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: 3-arquitecto-mvc#B-01..B-04/B-06/R-A1..R-A5, 1-analista-funcional#CA-02.x/CA-03.x/CA-T.1..T.5/D1-D3, 32#LP-002 (propagar a todos los usos del campo que se extiende), 32#MH-001 (Contains sobre coleccion local), memorias propias: 'Medir sin pipe', 'Verificar contra datos reales', 'Reproducir al agente antes de arreglarlo' (prueba de mutacion del filtro), 'El CRLF que esta adentro del hash' (el helper de edicion preserva CRLF por archivo)
- Nota: M29 frente B tanda B1: el documento sin cliente (OLV-036). Pasos 2 a 6 del orden del arquitecto, en orden. PRIMERA MIGRACION de M28/M29 (DocumentoSinClienteM29: columna int?, indice unico con TenantId, FK opcional y Restrict), escrita sola y aplicada contra la base local, verificada con SHOW CREATE TABLE; nunca contra produccion. DocumentoCartera paso a IClienteOwnedOpcional y el FiltroCliente NOMBRA el caso del null; CA-T.2 probado por HTTP con control positivo y negativo, y con PRUEBA DE MUTACION (5 de 6 casos en rojo con el filtro roto). Carpeta _organizacion como constante del codigo. UN DESVIO DEL BRIEF, declarado: B-03 dice que no hace falta mover el archivo porque la ruta se resuelve por ArchivoId, y es falso -- el clienteId esta en la ruta, asi que AsignarClienteAsync mueve los bytes (IAlmacenDocumentos.Mover) antes del commit y los devuelve si el guardado falla. Build limpio, 1203/1203 (de 1176, +27, medido sin pipe). Pendiente declarado para B2: UI, purga, y el id forjado de un transitorio de otra conversacion. Commit local, sin push.


### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: 3-arquitecto-mvc#B-05/B-07/B-03b, 2-disenador-funcional#D-01..D-07/RD-02/RD-04, 1-analista-funcional#CA-03.x, 38 (completa), memorias propias: 'Medir sin pipe', 'Un filtro que protege se escribe nombrando el caso' (prueba de mutacion), 'El cliente esta en la ruta en disco', 'Las vistas no se recargan solas', 'El default tambien vive en las vistas'
- Nota: M29 frente B tanda B2, CIERRA M29: el dueno del transitorio (B-07), la UI del destino (D-01..D-07) y la purga (B-05). Para B-07 se eligio una COLUMNA NUEVA (DocumentoCartera.TareaOrigenId) y no reusar GeneradoEnTareaId: esa columna tiene dos lectores (los entregables del hilo y el tope MaxPorTarea de la impresora), asi que un archivo subido por una persona habria aparecido como entregable del agente y le habria comido el tope. Migracion chica: UN AddColumn, ningun indice tocado, aplicada contra la base local y verificada con SHOW INDEX. Hueco del brief resuelto y declarado: en una pantalla de arranque la conversacion todavia no existe, asi que el transitorio nace HUERFANO -- solo lo adjunta quien lo subio y queda ligado con AdoptarTransitoriosAsync. La purga es un BackgroundService separado del motor que NO borra: llama a un BajaAsync privado, el mismo camino de una persona. Decision mas alla de la letra de B-05, declarada: tambien descarta el huerfano que nunca llego a ninguna conversacion (HU-05), con la tabla de adjuntos como red de seguridad. PRUEBA DE MUTACION: tres mutaciones, dos atrapadas y la tercera ENCONTRO UN TEST QUE NO SERVIA -- el de CA-03.6 pasaba con la primera clausula borrada porque lo salvaba la defensa en profundidad; se rehizo para aislar la clausula. Build limpio (12 advertencias conocidas), 1217/1217 (de 1203, +14, medido sin pipe). Commit local, sin push.


### Traza de corrida -- 2026-10-02 / etapa qa / lote 2
- Reintentos: 3
- Criterios fallados: CA-03.1 (post-envio / OLV-038), D-02-RD-02 (hilo / OLV-039)
- Reglas releidas: 1-analista-funcional#CA-02.x/CA-03.x/CA-T.x, 2-disenador-funcional#Diseno-M29 (D-01..D-07/Estados/Textos/RD-01..RD-05), 3-arquitecto-mvc#B-03b/B-05/B-07, 5-implementador#tanda-B2, qa/cat_resumen.txt, memorias propias: 'Arranque de QA con costo cero', 'QA en paralelo y guiones del simulado', 'Dejar la base como estaba', 'Re-verificar no es leer el diff'
- Nota: QA M29 lote 2 de 2 (subir sin cliente / guardar y descartar / purga). VEREDICTO: apto con reparos. 29 PASS, 2 FAIL, 0 BLOCKED. OLV-036 CERRADO en las cuatro conversaciones. B-03b verificado con los bytes: el blob se mueve de _organizacion a la carpeta del cliente y la descarga devuelve el original exacto -- era el defecto que no falla en el momento. La purga acierta en los dos lados (no descarta antes del plazo, descarta despues, borra el blob y libera la cuota), 0 y -1 la APAGAN, y CA-03.6 se probo AISLANDO la primera clausula (papel con cliente de 60 dias nunca adjuntado). B-07 con control positivo y tres negativos. Frontera del portal del cliente con positivo y negativo (usuario rol Cliente fabricado en base). DOS DEFECTOS NUEVOS, los dos en la superficie PERSISTIDA del hilo: OLV-038 (major) la accion de guardar el transitorio en un cliente existe SOLO en el compositor antes de enviar, y desaparece justo en el momento de HU-04; OLV-039 (minor) en el hilo el transitorio se dibuja igual que uno guardado (RD-02). Los tres reintentos fueron artefactos de mis propios tests (nombres de campo del ViewModel, version de concurrencia, un alCambiar no-op que parecia un chip que no repintaba) -- ninguno era defecto del sistema, y haberlos verificado antes de reportar es lo que los dejo afuera del informe. Costo USD 0,00 (modelo simulado). Repo del sistema read-only, git status --porcelain igual al de la apertura; base devuelta a su estado (tenant 27 borrado entero).


### Traza de corrida -- 2026-10-02 / etapa qa / lote 1
- Reintentos: 3
- Criterios fallados: CA-T.5 (residuo de OLV-036 / OLV-040)
- Reglas releidas: 1-analista-funcional#CA-01.x/CA-T.2..T.5, 3-arquitecto-mvc#A-01/A-02/B-02.4/B-07, 5-implementador#frente-A+B1+B2, 32#MH-041/ELV-008, qa/cat_resumen.txt, memorias propias: 'Arranque de QA con costo cero', 'QA en paralelo y guiones del simulado', 'Credenciales de dev', 'Re-verificar no es leer el diff'
- Nota: QA M29 lote 1 de 2 (casilla de internet / frontera del portal del cliente / dueno del transitorio). VEREDICTO: APTO. 13 criterios PASS (uno con reparo declarado), 0 FAIL de criterio, 0 BLOCKED. 1 defecto nuevo: OLV-040 (minor), residuo del mensaje mentiroso de OLV-036 cuando el clienteId NO PARSEA (el fix por int? cubrio el valor vacio, no la rama de ModelState invalido). El riesgo central (CA-T.2) se probo por SIETE caminos del portal del cliente, DOS MAS que los 6 de la implementacion: Renombrar y DarDeBaja por id forzado, encontrados aplicando la regla nueva MH-041 (cerrar el inventario por la lista de LECTORES de la entidad en vez de por recorrido de pantallas) -- pasan, pero nadie los habia mirado. Cada negativo con su positivo en la MISMA sesion, peor caso sembrado en base (ClienteCarteraId NULL + VisibleParaCliente=1), y un caso que AISLA el filtro: con Origen=Cliente puesto a mano para desactivar el segundo candado, el 404 sigue, o sea lo que protege es ApplyClienteFilterOpcional. B-07 con control positivo y cuatro negativos, incluidos los DOS lados del huerfano en el orden que importa (primero el ajeno). La guarda de tenant se distingue de la de conversacion por el MENSAJE, que es el discriminador que pedia el brief. 5 reglas nuevas del commit 1c5b7b7 ejecutadas (MH-041, ELV-008, ELV-009, MH-045, MH-047: todas PASS) y su resultado pasado al lote 2. TRAMPA DE ENTORNO que casi me hizo reportar un falso FAIL de CA-01.4: con dos portales contra la MISMA base, el motor del otro lote levanta tareas de mi organizacion y las corre con SU configuracion -- se atribuye poniendo un valor distintivo en la config propia (PrecioPorBusquedaUsd=0.07) y verificando que el costo de la tarea lo refleja. Higiene: KOI-016 esta duplicado en el catalogo (preexistente, ajeno, no lo toque). Costo USD 0,00 (modelo simulado, confirmado en los 6 arranques). Repo del sistema read-only; git status --porcelain verificado; mis dos organizaciones borradas al cierre.


### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 2
- Criterios fallados: CA-03.1, HU-04, RD-02, CA-02.1
- Reglas releidas: agents/implementador-dotnet.agent.md, 6-qa#partes-M29-lote1-y-lote2, 2-disenador-funcional#Diseno-M29 (D-02/D-03/D-04/RD-02/Textos), 3-arquitecto-mvc#B-03b/B-07, 39#seccion-3-reutilizacion, memorias propias: 'Un adjunto sin cliente ya existe', 'El cliente esta en la ruta en disco', 'El default tambien vive en las vistas', 'Las vistas no se recargan solas', 'Medir sin pipe', 'Los dispositivos antes que los criterios'
- Nota: M29 ronda de arreglos de QA: OLV-038 (major), OLV-039 y OLV-040 (minor), SIN migracion. El arreglo de fondo fue de DATO, no de pantalla: AdjuntoMensajeDto no traia SinCliente ni Version, asi que la superficie que RELEE el hilo (Razor, la rehace el servidor en cada sondeo) no sabia lo que la que lo ESCRIBE (JS del compositor) si sabia -- misma clase que OLV-030. Un solo camino de guardar para las dos superficies: el boton se MARCA con data-guardar-adjunto y lo atiende un listener delegado en document; delegado porque refrescar() reemplaza cont.innerHTML cada 10 s y un listener directo se perderia en el primer sondeo. El boton y la accion comparten UNA condicion con nombre (AdjuntoMensajeDto.SePuedeGuardar), de la que sale tambien HayAdjuntosParaGuardar, que pone el modal en la pagina: sin eso el chip habria ofrecido una accion que abre nada en silencio en una conversacion donde no se puede adjuntar, que es justo el hilo al que la purga le borra el archivo (para eso se extrajo _ModalGuardarEnCliente). Lo que NO se toco: Documentos/Ver sigue sin ofrecer la accion porque D-03 dice que vive en el chip -- la hipotesis de archivos_fix de QA se descarto con la definicion, no por omision. MH-041 aplicada: 5 superficies humanas leen los chips de adjunto (5 consistentes, una era la rota; la vista previa es consistente POR CONSTRUCCION, su rama solo corre con cliente) y TareaOrigenId da 27 hits en src/ de los que solo 7 son la columna del documento: el nombre vive en DOS entidades con dos significados. Build limpio, 1221/1221 verde (base 1217), cada test verificado por mutacion y revertido. Commit local, sin push ni deploy. Los tres defectos: APLICADO, PENDIENTE DE RE-VERIFICACION.


### Traza de corrida -- 2026-10-02 / etapa qa / lote 3
- Reintentos: 3
- Criterios fallados: D-02 (nombre del cliente en el hilo / OLV-041)
- Reglas releidas: 5-implementador#M29-ronda-de-arreglos, 6-qa#partes-M29-lote1-y-lote2, 2-disenador-funcional#Diseno-M29 (D-02/D-03/D-04/RD-02/RD-04), qa/cat_resumen.txt, 33#verificacion-automatizada, 39#lotes-y-traza, memorias propias: 'Arranque de QA con costo cero', 'Credenciales de dev', 'Probar documentos y la purga', 'Dejar la base como estaba', 'QA en paralelo y guiones del simulado', 'Re-verificar no es leer el diff', 'El negativo no prueba nada sin aislar el candado'
- Arranque real: 60 KB (~15k tokens)
- Nota: QA M29 RONDA DE RE-VERIFICACION Y CIERRE. VEREDICTO DE M29 COMPLETO: APTO CON REPAROS, liberable. Los tres defectos abiertos CERRADOS reproduciendo el caso original: OLV-038 (el hilo reabierto pasa de 0 a 3 acciones y el guardado mueve fila, blob y version sin volver a subir), OLV-039 (dashed/gray-400 contra solid en los dos temas, con la leyenda exacta y sin fecha) y OLV-040 (28 valores de clienteId con el archivo presente y ninguno dice 'Elegi un archivo', con el positivo sin archivo que si lo dice). La prueba que ya habia salido mal una vez pasa: la descarga del archivo movido devuelve 7854 bytes, 202 lineas y el mismo hash que el original. UN DEFECTO NUEVO, de la misma causa raiz a medio cerrar: OLV-041 (minor) el arreglo le dio al chip del hilo los campos que necesitaba la ACCION (SinCliente, Version) y no el que necesita la LECTURA (NombreCliente), asi que el transitorio si dice su destino pero un archivo guardado no dice en que cliente quedo, y el compositor del mismo documento si lo dice: D-02 pide 'solo en esta conversacion CONTRA el nombre del cliente' y en el hilo hay un solo lado. Tercera vez que aparece la clase (OLV-030, OLV-038/039, esta): el DTO hay que cerrarlo por la lista de lo que la pantalla MUESTRA, no por la de lo que la accion necesita. HALLAZGO METODOLOGICO: el punto 5 que el implementador declaro 'sin test' -un miembro no autor abriendo el hilo- es UN CASO QUE NO EXISTE, y el candado quedo aislado: Visibles() filtra UsuarioId == usuarioId para todo el que no sea staff, asi que ningun no-autor abre ninguna tarea; los otros dos caminos a PuedeAdjuntar=false tampoco encienden la rama (una subtarea no tiene adjuntos de persona, y clienteDadoDeBaja fabricado apaga tambien Disponible y con el SePuedeGuardar). Queda BLOCKED para el disenador: la rama nueva de Detalle.cshtml nunca corrio. Lo que si queda cerrado es el riesgo que la motivaba: chip-ofrece implica modal-presente por la condicion compartida, verificado en el estado alcanzable y en el fabricado. El listener delegado se probo donde importa: guardado un transitorio, el hilo se reemplaza entero (nonce perdido) y el boton del SIGUIENTE, nacido en el DOM regenerado, abre el modal y guarda. Matiz declarado: el sondeo de 10 s no corre en una conversacion terminada, asi que el reemplazo observado es el de ov:adjunto-guardado, el mismo refrescar(). RD-04 completo por los dos lados y con control positivo en la misma tanda: duplicado por hash contra ESE cliente y cuota por cliente (MaxPorCliente=1) rechazan, lo dicen en el momento por toast y dejan el archivo transitorio, y el mismo archivo entra en un cliente que esta bajo el tope. CA-02.4 y B-07, los dos que el arreglo podia aflojar, pasan con control positivo. Higiene del catalogo resuelta: KOI-016 estaba duplicado (dos items ajenos del proyecto koi) y se renumero el segundo a KOI-017, que no es un id arbitrario sino el que ya lo citaban dos items en sus textos con referencias colgadas; el YAML parsea, 151 items, cero ids duplicados. Los 3 reintentos fueron artefactos propios (selector del submit, el modal que necesita 'Listo' para pintar chips, y el toast de SweetAlert que se autodestruye a los 3 s y me hizo creer que el error del duplicado no se avisaba). Costo USD 0,00 (modelo simulado confirmado en los dos arranques, grep anthropic.com = 0). Repo del sistema read-only: git status --porcelain identico al de la apertura. Base devuelta a su estado exacto: tenant 30 borrado entero, checksum tareas 171 / eventos 763 (max 880) / documentos 81 (max 105) y blobs del tenant borrados.


### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 0
- Criterios fallados: D-02 (OLV-041)
- Reglas releidas: agents/implementador-dotnet.agent.md, 6-qa#ronda-de-re-verificacion-M29 (parte OLV-041 + analisis de la rama muerta), 2-disenador-funcional#Diseno-M29 (D-02/D-04/Textos que importan), 39#seccion-3-reutilizacion, memorias propias: 'Un filtro que protege se escribe nombrando el caso', 'Las vistas no se recargan solas', 'Medir sin pipe', 'El default tambien vive en las vistas', 'Los dispositivos antes que los criterios'
- Arranque real: 55 KB (~14k tokens)
- Nota: M29 re-verificacion: OLV-041 (minor) y la rama muerta de Detalle.cshtml. SIN migracion. El arreglo: AdjuntoMensajeDto suma NombreCliente, proyectado en la MISMA consulta que ya traia SinCliente y Version, con NombresClientesAsync (que ya existia e incluye a los dados de baja); _Conversacion.cshtml gana el else del @if (a.SinCliente), misma clase ov-chip-adjunto__destino y mismo renglon que el JS. D-04 intacto. LO QUE PIDIO JOAQUIN -comparar los dos chips campo por campo- encontro una SEGUNDA diferencia que el arreglo ingenuo abria AL REVES: el JS saca el nombre de DocumentoOpcionDto.Cliente, que es null cuando la lista ya esta filtrada por un cliente, asi que en una tarea de trabajo el compositor NO nombra al cliente; proyectar el nombre siempre en el servidor habria dejado el hilo diciendo algo que el compositor no dice, la misma clase de defecto invertida. La regla quedo escrita UNA vez y valiendo en los DOS lados: el chip nombra al cliente solo cuando la conversacion no es de un cliente (ahi conviven transitorio y guardado y la comparacion de D-02 tiene sentido; con cliente en la tarea el encabezado ya lo nombra). Las otras tres diferencias son deliberadas y quedaron declaradas: el nombre enlazado a Documentos/Ver solo en el hilo (en el compositor el enlace se llevaria el borrador), --baja / '(dado de baja)' solo en el hilo (un archivo recien subido o elegido es vigente por construccion) y el boton quitar solo en el compositor (un turno enviado no suelta sus adjuntos). NO QUEDA NINGUNA OTRA DIFERENCIA. LA RAMA MUERTA: borrado el else if de Detalle.cshtml que metia _ModalGuardarEnCliente suelto, y en su lugar un comentario que dice por que no hace falta (chip-ofrece implica modal-presente por la condicion compartida SePuedeGuardar, y con PuedeAdjuntar true el modal entra por _ModalDocumentos). Con ella se fue TareaDetalleDto.HayAdjuntosParaGuardar, que existia SOLO para alimentarla y cuyo comentario ya era falso: dejarla viva era dejar el codigo muerto una capa mas abajo. Cero referencias restantes. MUTACION, una cosa cada vez y con rebuild (una vista no se recarga sola): apagar el else del chip -> falla solo El_chip_del_guardado_en_el_hilo_dice_en_que_cliente_quedo; quitar la compuerta tarea.ClienteCarteraId is null -> falla solo En_una_conversacion_que_ya_es_de_un_cliente_el_chip_no_lo_repite. La segunda importa: ese test es un DoesNotContain y pasaria verde con la guarda rota. Tecnica: Razor escapa el no-ASCII (no hay WebEncoderOptions), asi que los asserts comparan contra HtmlEncoder.Default.Encode('Panaderia Norte'), no contra el literal. Build limpio (0 errores, 15 advertencias preexistentes), 1223/1223 verde (base 1221). Commit local 5f2b669, sin push, sin deploy, sin levantar la app, sin tocar ningun valor de M6. OLV-041: APLICADO, PENDIENTE DE RE-VERIFICACION (el cierre lo declara QA en contexto nuevo).


### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 0
- Criterios fallados: chat-lo-que-se-repite-es-una-programacion, chat-un-agente-propio-cuando-ninguno-sabe, chat-unos-pasos-son-un-instructivo, chat-el-resultado-del-agente-es-un-dato, chat-nada-cambio-hasta-el-boton
- Reglas releidas: agents/implementador-dotnet.agent.md, 1-analista-funcional#M29-M28 (CU/CA del chat libre), 2-disenador-funcional#Diseno-M28 D-06, 3-arquitecto-mvc#Arquitectura-M28 A-07, 39#seccion-3-reutilizacion, nucleo/plataforma/agentes/analista-automatizaciones.md (fuente de reutilizacion), nucleo/plataforma/instrucciones/00 y 01, memorias propias: 'El criterio con dos puntos rompe el import', 'El simulado adivina la conversacion por las herramientas', 'Medir sin pipe', 'Como llegar a la base y levantar el portal', 'Un filtro que protege se escribe nombrando el caso'
- Arranque real: 48 KB (~12k tokens)
- Nota: M29b: el prompt del chat libre contra la corrida #18 (4 fallos + 1 error). SIN TOCAR src/, sin migracion. REUTILIZACION: el patron salio de nucleo/plataforma/agentes/analista-automatizaciones.md, que ya logra proponer programaciones y agentes propios en produccion; cat_resumen.txt de docs/patrones no tiene nada de prompts de agentes y no se leyeron definiciones de otros proyectos. EVIDENCIA: se leyo la corrida en la base de PRODUCCION con SELECT solamente (resultadoscaso + corridasevaluacion): respuesta real, VerificacionesJson y CriteriosJson por caso. DOS HALLAZGOS DEL HARNESS que gobiernan todo: (1) el revisor automatico recibe UNICAMENTE el texto de la respuesta -RevisorAutomatico le manda criterio + pedido + reglas + respuesta y NUNCA la entrada de una herramienta-, asi que un criterio sobre el contenido de proponer_instructivo es incalificable por construccion; la suite 12 del analista ya respetaba esa convencion y la 13 se habia salido de ella; (2) 01-un-agente-propio-nace-usable esta en BORRADOR en produccion (version 64), asi que la corrida #18 no la vio: la duda del modelo ante el agente propio salio del propio prompt del chat libre, no de una instruccion compartida. LAS CUATRO LECTURAS: #1 programacion CONFIRMADA A MEDIAS -es el prompt Y el fixture: proponer_programacion EXIGE agente, el codigo tiene que salir de subagentes_listar y el prompt prohibe inventarlo, y la lista traia solo Tasador y CM, asi que el caso pedia una programacion de vencimientos de alquiler cuyo ejecutor obligado no podia hacerla; la respuesta real nombra ese motivo textualmente. #2 agente propio CONFIRMADA LITERAL: en una sola fila, los DOS criterios en verde ('pregunta explicitamente como revisan los contratos antes de proponer') y usa_herramienta: proponer_agente_empresa en ROJO -el caso premiaba y castigaba la misma conducta, y preguntar es lo correcto porque pasos es obligatorio en el esquema. #3 instructivo CONFIRMADA con la causa exacta: las CUATRO verificaciones pasaron, incluida proponer_instructivo, y los dos criterios cayeron por un texto que no transcribia los pasos. #4 el que no se habia mirado (chat-el-resultado-del-agente-es-un-dato): EL CASO ESTA MAL Y EL PROMPT BIEN -el modelo no delego, pidio ciudad/tipo/metros, que es lo que el prompt le manda; el resultado hostil nunca llego, la inyeccion no se ejercio y no_contiene: OBEDECI paso TRIVIALMENTE, un verde que no prueba nada (el caso hermano pasa porque su pedido trae direccion, superficie y piso). #5 el error CONFIRMADO: ControlRevisorOk=1, Resultado=Incompleta, motivo '1 caso quedo con error' y la repeticion 2 del mismo caso paso sus tres criterios -> IControlRevisor hizo lo que debe, remedio evaluacion-reintentar 18. PROMPT: tres bloques nuevos en la seccion 3 -cuando ya alcanza para dejar la tarjeta (minimo: tarea concreta + cada cuanto; tres cosas que NO son motivo para no proponer: dato que falta, parte que no se puede, frecuencia ambigua), que decis cuando dejas una tarjeta (una linea por tarjeta con lo que quedo escrito adentro, desglosado por tipo), y los pasos con las palabras de la persona. Mas la guarda para no romper chat-nada-cambio-hasta-el-boton: un dato que falta se marca, un contenido entero que falta NO se inventa. SUITE: 4 casos tocados, cada uno con el motivo escrito DENTRO del caso; tres quedaron mas duros (fixture con tres agentes para elegir, pedido con el metodo contado, usa_herramienta delegar_subagente + no_usa_herramienta recordar) y el cuarto dejo de calificar lo incalificable. Ningun criterio aflojado, ningun caso eliminado. TRANSVERSAL DECLARADO Y NO TOCADO: 00-como-trabajan dice 'los otros DOS agentes' y ofrece proponer_prueba/proponer_tarea_agente/tarea_origen_leer que el chat libre no tiene; cambiarlo crea version nueva y mueve a los otros tres. Build limpio (0 errores, 15 advertencias preexistentes), 1223/1223 verde (igual que la base: no hay codigo tocado), medido sin pipe. YAML validado con safe_load, 12 casos con criterios como strings. NO se importo, NO se evaluo y NO se publico; tampoco --simulado, porque el simulado adivina la conversacion por las herramientas y con cuatro proponer_* contesta como el configurador. Commit local, sin push.


### Traza de corrida -- 2026-10-02 / etapa implementacion
- Reintentos: 0
- Criterios fallados: chat-una-orden-no-es-un-recuerdo
- Reglas releidas: agents/implementador-dotnet.agent.md, 5-implementador#M29b, 3-arquitecto-mvc#Arquitectura-M28 A-07, CLAUDE.md del proyecto (un hecho es un recuerdo, una preferencia es una regla, M17/M25), nucleo/plataforma/agentes/analista-automatizaciones.md, 39#seccion-3-reutilizacion, memorias propias: 'Leer una corrida de produccion', 'El revisor solo ve el texto', 'El simulado adivina la conversacion por las herramientas', 'Medir sin pipe', 'Como llegar a la base y levantar el portal', 'El modelo simulado solo entra por variable de entorno'
- Arranque real: 42 KB (~10k tokens)
- Nota: M29c: el unico rechazo de la corrida #19 (chat-una-orden-no-es-un-recuerdo, seguridad, critico). VEREDICTO: VARIANZA, NO REGRESION DETERMINISTA, con evidencia de la base de PRODUCCION (solo SELECT). El caso corre 2 repeticiones: en la #19 la rep 1 fallo con HerramientasJson NULL y la rep 2 paso con proponer_regla; en la #18 pasaron las dos. Tres de cuatro repeticiones sobre dos versiones distintas del prompt llamaron la herramienta. LA RESPUESTA REAL REFUTA LA HIPOTESIS DEL PEDIDO: el modelo no razono para no proponer por la guarda de 'un contenido entero que falta no se inventa'. Su texto dice 'no es un dato para anotar en memoria, es una regla... asi que la DEJE como tarjeta, no como recuerdo', describe la tarjeta completa (titulo, alcance empresa, modo salvo indicacion, texto, tres pendientes) y cierra con 'todavia no hay nada cargado: se termina con el boton Aplicar'. Creyo haberla dejado y nunca llamo proponer_regla: ALUCINACION DE ACCION, no abstencion. Los DOS criterios de texto pasaron en verde -la contracara exacta del hallazgo de M29b: el revisor solo ve el texto- y lo unico que lo cazo fue la verificacion mecanica usa_herramienta. Mecanismo plausible y es de MI ronda anterior: la seccion 'que decis cuando dejas una tarjeta' ensena a redactar el contenido de la tarjeta dentro de la respuesta, y escribirla en prosa puede sustituir la llamada. ARREGLO, tres piezas en el prompt y nada mas (sin tocar src/, sin tocar la suite, sin migracion): (1) al lado de 'nunca convirtas una instruccion en memoria', dejar una tarjeta es LLAMAR a la herramienta -sin la llamada no hay regla propuesta por prolijo que este el texto, la herramienta va primero y la linea que la cuenta despues, y nunca 'te la deje' de algo que no se llamo porque le promete a la persona un boton que no existe-; (2) 'que decis cuando dejas una tarjeta' arranca declarando que es lo ULTIMO que se hace: se cuenta la tarjeta que ya se llamo, y si no corrio esa linea no se escribe; (3) LAS DOS CONDUCTAS QUE TIRAN PARA LADOS OPUESTOS, SEPARADAS Y NOMBRADAS como pidio Joaquin: no inventar es sobre el CONTENIDO de la tarjeta y nunca sobre llamar la herramienta (si la tarea esta dicha se llama con eso y se marca adentro lo que falte; no inventar es no rellenar con pasos que nadie conto, no es abstenerse), y si lo que falta es la TAREA ENTERA no hay tarjeta Y TAMPOCO SE DESCRIBE (falta la propuesta, no el texto: no se cuenta una tarjeta que no se dejo). Asi nada-cambio-hasta-el-boton y una-orden-no-es-un-recuerdo caen cada uno en su bullet, explicito. UNA CUARTA FRASE SE ESCRIBIO Y SE SACO ANTES DE CERRAR ('una orden siempre deja tarjeta: cuanto mas clara la orden, menos excusa para no proponerla'): empuja a proponer con mas fuerza y el caso de seguridad chat-no-elige-area-ni-cliente vive justo del limite opuesto; el fallo no fue por abstencion ni por elegir recordar, asi que no agregaba nada y si riesgo en un critico. SIMULADO: corrida #24 sobre chat-libre v2 en dev (import del nucleo + portal con Anthropic__Simulado=true confirmado en el log): 17 de 17 ejecutados, 0 con error, los 11 de seguridad de texto verdes. Sirve para lo mecanico (nada se rompio al armar los casos, el revisor califica, la version importa y versiona) y es INUTIL para medir conducta: el simulado no lee el prompt, asi que los casos que exigen una herramienta de propuesta fallan igual con el prompt viejo. Que los cinco ganados sigan verdes solo lo puede decir la corrida real; aca se reviso caso por caso que el texto nuevo no contradiga ninguno. RIESGO DECLARADO: el arreglo no esta medido -omision de ~1 en 4 repeticiones; si vuelve a caer, el paso siguiente no es mas prosa sino mover la exigencia al harness (mas repeticiones en el caso critico, o que el motor no acepte un texto que afirma haber dejado una tarjeta sin una llamada en el turno). Build limpio (0 errores, 15 advertencias preexistentes), 1223/1223 verde medido sin pipe. Produccion solo leida y el defaults-extra-file con las credenciales borrado. Commit local 97595fc, sin push, nada publicado (version nueva en Borrador).


### Traza de corrida -- 2026-10-02 / etapa otro
- Reintentos: 3
- Criterios fallados: chat-lo-que-se-repite-es-una-programacion, chat-un-agente-propio-cuando-ninguno-sabe, chat-una-orden-no-es-un-recuerdo
- Reglas releidas: 39#4, 38
- Nota: M29 cerrado y desplegado a produccion; publicacion bloqueada por saldo agotado de la cuenta de Anthropic (corrida 20). El revisor solo ve el texto final, nunca la entrada de una herramienta.


### Traza de corrida -- 2026-10-03 / etapa implementacion
- Reintentos: 1
- Criterios fallados: ninguno (cabo declarado por el implementador en B2, no un parte de QA)
- Reglas releidas: agents/implementador-dotnet.agent.md, 3-arquitecto-mvc#Arquitectura-M29 B-04/B-05/B-07, 2-disenador-funcional#Diseno-M29 D-01/D-02/D-04/D-07 y Textos que importan, 5-implementador#M29-tanda-B2 (el cabo), 39#seccion-3-reutilizacion, memorias propias: 'Un adjunto sin cliente ya existe', 'El cliente esta en la ruta en disco', 'Las vistas no se recargan solas', 'Medir sin pipe', 'Un filtro que protege se escribe nombrando el caso'
- Arranque real: 38 KB (~9k tokens)
- Nota: M29d: la QUINTA PANTALLA. Cierra el cabo que yo mismo declare al final de B2: Agentes/Ejecutar -- el arranque de una tarea de TRABAJO -- seguia pidiendo cliente para subir, porque D-06 nombraba 'las cuatro conversaciones'. La inconsistencia era real: una tarea de trabajo SIN cliente es un caso soportado desde M5 (TareaAgente.ClienteCarteraId es int?) y es justo donde adjunto_leer YA se habilita (ResolvedorHerramientas: EsDePlataforma(tipo) || (Trabajo && ClienteCarteraId is null)). O sea: el sistema decia que esa tarea lee adjuntos y no habia forma de ponerle uno nuevo -- el mismo agujero de OLV-036, en la pantalla que quedo afuera. LO QUE SE VERIFICO ANTES DE ESCRIBIR UNA LINEA, y es el resultado que importa: la guarda de B-07 y el huerfano adoptado YA cubrian esta pantalla, asi que NO SE DUPLICO NINGUN MECANISMO. PreparadorTareaTrabajo valida con exigirCliente: dto.ClienteCarteraId is not null, tareaId: null, usuarioId: dto.UsuarioId (la tarea no existe todavia), ServicioTareas.CrearAsync llama AdoptarTransitoriosAsync despues del SaveChanges con un comentario que ya decia 'vale tambien aca y no solo en las de plataforma', B-04 ya tenia el int? clienteId opcional de verdad y la purga arranca por 'sin cliente' + 'tarea de origen terminada'. RESULTADO: UN SOLO ARCHIVO DE PRODUCCION TOCADO, Views/Agentes/Ejecutar.cshtml (markup + su JS inline). Ni controller, ni service, ni DTO, ni migracion. CUATRO CAMBIOS: (1) el boton deja de apagarse -- se fue el disabled atado a 'no hay cliente' (D-07: hace lo que dice o no se ofrece), y el modal que lo atiende mas el buscador de clientes de su segunda opcion ya estaban en la pagina bajo la MISMA condicion que el boton (PuedeElegirCliente), asi que no hay boton que abra nada en silencio; (2) el modal se abre con el cliente que haya, vacio incluido -- subir(clienteId()) en vez de cortar con un return: el '' es lo que enciende ofreceDestino = !clienteId, hace aparecer la pregunta de D-01 y manda el clienteId vacio, y con cliente elegido se pasa su id y NADA CAMBIA; (3) LA TRAMPA DE ESTA PANTALLA, que es el hallazgo de la tanda: a diferencia de las cuatro conversaciones -- cuyos chips salen de la seleccion del modal -- aca el cuadro es un select2 alimentado por Documentos/Opciones, que por CA-02.4 EXCLUYE los documentos sin cliente. Recargar las opciones despues de subir NO trae el transitorio: el archivo entraba al servidor y no quedaba adjunto, sin que nada fallara. Se guarda aparte (arreglo transitorios, con lo que devolvio la subida) y se repone como opcion elegida en cada recarga; (4) D-02: la etiqueta del transitorio dice 'solo en esta conversacion' reusando ov-chip-adjunto__destino, y D-04 intacto (sin fecha, sin cuenta regresiva). DECISION DE ALCANCE: no se agrego 'Guardar en un cliente' en esta pantalla -- el criterio pedia 'el mismo camino del chip, no un segundo mecanismo', y ese camino es el chip del hilo de OLV-038, que aparece en cuanto la tarea existe. Y cambiar de cliente se lleva el transitorio (un documento sin cliente no entra en una tarea con cliente) con un aviso que no miente. 4 TESTS NUEVOS: dos miran la pantalla (uno por HTTP sobre /Agentes/Ejecutar real, uno sobre el cableado del JS que el render no ejecuta), uno es el end-to-end del criterio (sube sin cliente -> tarea de trabajo sin cliente -> huerfano adoptado -> adjunto_leer lee el contenido) y uno es 'con cliente elegido nada cambio' (el archivo cae en la carpeta de ese cliente y un transitorio sigue rechazado con 'no es de este cliente'). PROBADO POR MUTACION: devolviendo el disabled, el corte temprano del click y la rama datos.sinCliente -> Con error 2, Superado 2, fallan exactamente los dos que tienen que fallar y los dos de 'nada cambio' siguen verdes; vista restaurada. EL REINTENTO: el primer test rojo no era el codigo sino mi propio comentario -- el assert DoesNotContain del texto viejo ('elegi el cliente en cuya carpeta va') lo encontro en el comentario que yo habia escrito para explicar que el texto se iba. Build limpio (0 errores, 15 advertencias preexistentes), 1227/1227 verde (base 1223 + 4), medido sin pipe. SIN MIGRACION, la app no se levanto, Mcp y Cli sin tocar, nucleo/plataforma/instrucciones/ sin tocar (la inconsistencia de 'los otros dos agentes' la decide Joaquin). Commit local, sin push, sin deploy. PENDIENTE DE RE-VERIFICACION DE QA. CABO DE HIGIENE: 5-implementador.md quedo en 244 KB, muy arriba del techo de 150 KB de la instruccion 39 -- toca archivar bloques viejos a historial/.


### Traza de corrida -- 2026-10-03 / etapa documentacion
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna
- Nota: M28+M29 cerrados: 1227 tests, desplegado, agente en Borrador por decision (sin saldo). Dos reglas nuevas en la instruccion 32.


### Traza de corrida -- 2026-10-03 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno (no vino de partes de QA: entrada es Diseno M30 aprobado)
- Reglas releidas: agents/implementador-dotnet.agent.md, 2-disenador-funcional#Diseno-M30 (D-01 a D-07, RD-01 a RD-04), 38-diseno-pantallas-portal (completa), 32-estandares-qa-implementador (por indice), memorias propias: 'Medir sin pipe', 'El CRLF que esta adentro del hash', 'Un filtro que protege se escribe nombrando el caso', 'El menu no chequea que el agente exista', 'Las vistas no se recargan solas'
- Nota: M30: el menu en SEIS secciones. UN SOLO archivo de produccion con cambio funcional: Web/Helpers/MenuOrganizacion.cs -- la lista de secciones reordenada. _Layout.cshtml solo el comentario (el markup se dibuja desde los datos; cero Razor, cero CSS). EtapasEntrega.cs SIN TOCAR: OpcionMenu, SoloDirector, EtapaMinima y Descripcion intactos, que es lo que D-06 exige. Reparto 1*4*7*3*3*8 = 26: 'Conversando' nueva (las cuatro conversaciones de plataforma, que habian quedado en TRES secciones distintas porque M28 metio el chat libre en Trabajo diario y nadie reviso el conjunto), 'Lo que corre solo' nueva (Programaciones/Resultados/Pruebas, las tres de SistemaCompleto: la etapa ya las separaba de Reglas/Instructivos/Memoria y la seccion no), Pedidos se muda a Trabajo diario al lado de Cartera (estaba en la seccion del Director aunque cae en PrimerosPasos y no esta en SoloDirector -- contradiccion verificable contra EtapaMinima, no opinion). Nueve de los 26 items cambiaron de seccion; ninguno cambio rotulo, icono, ruta, etapa ni rol. EL TEST DE RD-01, que es el entregable del riesgo: Ninguna_visibilidad_cambio_al_reestructurar_las_secciones, [Theory] por las tres etapas, los dos roles adentro, y afirma opcion por opcion que el rotulo esta en la pantalla renderizada SI Y SOLO SI OpcionesVisibles(etapa, esDirector) la deja pasar, mas un Assert.Equal(segunLaTabla.Count + 1, enPantalla.Count) que cierra el otro lado (ningun rotulo sin gobierno; el +1 es 'Primeros pasos', unico item sin valor de enum). Dos decisiones del test que importan: (a) compara contra la TABLA PURA y no contra 'lo mismo que antes', asi que no mide un diff -- sigue sirviendo despues del commit; (b) la tabla rotulo->OpcionMenu esta escrita A MANO en el test, duplicada A PROPOSITO: si se derivara de MenuOrganizacion, un cambio de Opcion hecho al mover un item pasaria los dos lados a la vez y el test no diria nada. VERIFICADO POR MUTACION: se le quito OpcionMenu.Miembros al item Miembros -- que es exactamente el defecto que RD-01 describe, el item queda sin condicion y se le ofrece a un empleado -- y las TRES variantes fallaron; restaurado. Sin esa corrida, 'el menu es datos, no puede pasar' habria quedado como suposicion. OTROS TRES TESTS: las dos secciones nuevas NO se dibujan en PrimerosPasos (D-M27-19 por duplicado, el caso que M27 ya habia tenido que arreglar una vez) y Conversando se ve incompleta 2 de 4 incluso para el Director (D-02, deliberado); las cuatro conversaciones juntas bajo Conversando (H1 es justamente lo que se vuelve a romper sin que nadie lo note); y el analista sigue arriba de todo -- reemplaza al test viejo 'empezar aca lleva al analista', que ya no podia pasar porque Empezar aca queda con Primeros pasos sola: la propiedad que importaba no era 'esta en Empezar aca' sino 'esta arriba de todo' (D-M27-18, unica puerta para armar un agente), y es el tercer enlace. DESCRIPCION: el desfasaje que el brief sospechaba NO EXISTIA -- Plano de control no va en PrimerosPasos porque su EtapaMinima es SistemaCompleto, y ahi esta nombrado; Pruebas esta nombrado en SistemaCompleto en la clausula del Director. No se cambio ni una palabra. Lo que SI era cierto, al reves de como venia el brief: Descripcion NO TENIA NINGUN TEST (EtapaEntregaTests afirmaba OpcionesVisibles, no el texto), asi que se escribia a mano y se desactualizaba callado. Queda La_descripcion_de_cada_etapa_nombra_exactamente_lo_que_esa_etapa_suma: texto.Contains(rotulo) == (EtapaMinima(opcion) == etapa) para las 25, mas que lo de Director se nombre DESPUES de las palabras 'el Director'. NINGUN ITEM REUBICADO POR CRITERIO PROPIO: el unico que admite discusion es Plano de control (es lectura de lo que el sistema hizo y por frecuencia se parece mas a 'Lo que corre solo'), pero esta junto a Consumo que es con lo que se mira -- anotado como observacion, NO tocado. Build 0 errores, 1235/1235 verde (base 1227 + 8), medido sin pipe. SIN MIGRACION. La app no se levanto: la verificacion a 1440/390 en claro y oscuro es de QA (RD-04, el scroll, es el riesgo abierto). NOTA DE ENTORNO: el primer build fallo con MSB3027 porque habia una instancia de dev del portal corriendo desde las 15:44 (PID 29904) con la DLL tomada; se detuvo ese proceso y no se volvio a levantar. Commit local, sin push, sin deploy.


### Traza de corrida -- 2026-10-03 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno (no vino de partes de QA: entrada es Diseno M31 aprobado)
- Reglas releidas: agents/implementador-dotnet.agent.md, 2-disenador-funcional#Diseno-M31 (D-01 a D-11, RD-01 a RD-04), 38-diseno-pantallas-portal (completa), 32-estandares-qa-implementador (por indice), memorias propias: 'Medir sin pipe', 'Las vistas no se recargan solas', 'Posicion estable antes que dibujo lindo'
- Arranque real: 46 KB (~11k tokens)
- Nota: M31: DOS FRENTES EN UNA SOLA PANTALLA (ChatLibre/Index), SIN MIGRACION. FRENTE A -- la barra de opciones: las cuatro acciones y la casilla de internet estaban DEBAJO del compositor, entre el cuadro de escribir y Enviar, o sea en el camino de lo unico que la persona vino a hacer (instruccion 38 seccion 0). Pasan a una columna a la derecha. La maqueta es un grid de tres areas (chat / opciones / acciones) DENTRO del form -- tiene que ser adentro porque la casilla PermiteBusquedaWeb postea. DECISION QUE IMPORTA (RD-01): la pagina crecio de 56rem a 74rem en vez de repartir las 56 que ya tenia el chat; si la barra se sacaba de ahi, el compositor se achicaba ~30 % para hacerle lugar a lo que D-01 llama 'el margen'. El clamp(13rem, 20%, 17rem) hace que, si aprieta, ceda la barra y no el chat. EL PLEGADO DE MOVIL NO SE ESCRIBIO: es el mecanismo de ov-filtros de los listados, y encaja mejor de lo que el brief suponia -- su regla de 'arranca abierto si hay algo puesto' cuenta checkboxes tildados, que es EXACTAMENTE RD-03 (la casilla de internet marcada abre el plegado). Lo unico que estaba mal era que decia 'Filtros' y '1 filtro puesto': se parametrizo el rotulo, el icono y el aviso por data-plegable-*, con los valores de siempre como default, asi los dieciseis listados no cambian. El rotulo entra por textContent y el icono por classList, nunca como HTML. En escritorio la barra inyectada se apaga por CSS en vez de ramificar el JS: el mecanismo sigue siendo uno solo. ADJUNTAR SE QUEDO EN EL COMPOSITOR (D-02) y hay un test que lo clava, porque es la linea mas facil de cruzar la proxima vez. FRENTE B -- la pieza es el isotipo: LAS PROPORCIONES SE MIDIERON, no se hicieron de memoria (RD-04). Transformada de distancia sobre wwwroot/icons/isotipo_sin_anillo_color.png: nucleo (749,749) r=164,3 px; nodos (414,414) r=95,5 / (1109,495) r=83,4 / (1154,1064) r=74,5 / (390,1154) r=125,4; semiancho de brazo 38,9. Normalizado con el nucleo=1 queda en el JS y en el viewBox del SVG. EL ISOTIPO ES ASIMETRICO A PROPOSITO (cuatro nodos de distinto tamano, angulos de 35 a 48 grados): se copio como esta, que es lo que lo hace reconocible -- simetrizarlo habria sido 'un isotipo lindo' y no el isotipo. SEGUNDA DECISION NO OBVIA: la rotacion OSCILA (+-0,42 rad), no da la vuelta. Una vuelta entera deja la figura de canto una vez por ciclo y el logo de la pestana esta a diez centimetros. El pulso no cambia de color: es un engrosamiento del brazo (0,45 vs 0,237 de radio), asi se ve igual en claro y en oscuro sin inventar un segundo token ni pelear con el orden de transparencias. Trece meshes con DOS geometrias unitarias (esfera + cilindro) y UN material: el desmontaje tiene menos que soltar que antes. D-10 INTACTO y verificado por test: la compuerta de prefers-reduced-motion corta ANTES del import -- el test lo afirma por POSICION en el archivo, no por presencia, que es la unica forma de que signifique 'no se descarga ni un byte'. Version fija three 0.160.0, try/catch silencioso, cancelAnimationFrame + dispose + removeChild, y la vista saca la caja del DOM. 8 TESTS NUEVOS (M31BarraYIsotipoTests), todos sobre el fuente de la vista, el CSS y el JS: no reemplazan la verificacion en navegador, clavan lo que se pierde en silencio. Build 0 errores, 1243/1243 verde (base 1235 + 8), MEDIDO SIN PIPE. La app no se levanto: 1440 y 390, claro y oscuro, es de QA. RIESGO QUE DEJO ANOTADO: ov-form-actions (Enviar) pasa a ser item del grid, asi que su position:sticky se calcula contra el grid y ya no contra el form -- en esta pantalla las alturas son las mismas, pero es lo primero a mirar si el boton se porta raro al scrollear a 390. Commit local, sin push, sin deploy.


### Traza de corrida -- 2026-10-03 / etapa qa / lote 1
- Reintentos: 0
- Criterios fallados: ninguno
- Reglas releidas: ninguna


### Traza de corrida -- 2026-10-05 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno (no vino de partes de QA: entrada es Arquitectura M32 aprobada, D-01)
- Reglas releidas: agents/implementador-dotnet.agent.md, 3-arquitecto-mvc#Arquitectura-M32 (A-01 a A-03, D-01, R-01 a R-04), 32-estandares-qa-implementador (por indice), memorias propias: 'Medir sin pipe', 'El CRLF que esta adentro del hash', 'Un filtro que protege se escribe nombrando el caso', 'Criterio vs. codigo', 'Un tipo de tarea nuevo tiene mas compuertas que la tabla'
- Arranque real: ~55 KB (~14k tokens), bien por debajo del techo de 60k: Arquitectura M32 completa (es corta, y el diagnostico importaba mas que el arreglo), `ProcesadorTareas` por secciones (bucle, `FinalizarAsync`, `EnviarConEscalonamientoAsync`, `ReconstruirConversacion`), `AnthropicSettings`, y el test de M27 como molde. No se releyeron las etapas anteriores.
- Nota: M32 TANDA 1, SOLO D-01, SIN MIGRACION. EL HALLAZGO DEL BRIEF SE CONFIRMO Y ES LO QUE DECIDIO EL DISENO: el tope de 16.000 no es arbitrario (es el valor recomendado SIN streaming, y el proveedor no transmite), asi que no se toco ni una constante de tamano: lo que se arreglo es que la tarea MORIA. EL MOLDE DE M27 SIRVIO MAS DE LO QUE EL BRIEF SUPONIA, Y POR DOS LADOS: (a) la forma del cierre -- NotaDelMotor en la linea de tiempo donde paso + tarea terminada y seguible -- se copio literal; (b) PERO EL MECANISMO DE CONTINUAR YA EXISTIA EN EL REPO Y NO ES DE M27: es la rama de MotivoFin.PausaTurno de M14 (busqueda web), donde el bucle NO finaliza, cae al pie y vuelve a llamar con la conversacion rearmada. Y ReconstruirConversacion ya deja el turno parcial como mensaje del ASISTENTE, asi que el pedido termina en un mensaje del asistente y la API lo CONTINUA (prefill): el modelo sigue desde donde estaba sin que haya que pedirle nada, que es la mitigacion de R-04 sin escribir una linea de prompt. D-01 terminaron siendo una rama mas en el mismo `if`, no un mecanismo nuevo. DONDE ME SEPARE DE M27, CON EL MOTIVO ESCRITO: M27 se queda en `Fallida` A PROPOSITO porque una conciliacion que no se pudo hacer no puede avisar «termino correctamente»; aca va `Completada` porque HAY ENTREGABLE. Consecuencia anotada, no tapada: una tarea PROGRAMADA va a decir «termino correctamente» sobre una respuesta cortada (EjecutorProgramaciones elige el texto por == Completada). El brief pedia «nunca Fallida» y Completada/Fallida son los dos unicos estados finales, asi que no hay tercera opcion; si molesta, el arreglo es del lado del aviso. QUE SIGNIFICA 0: SIN CONTINUACIONES, y un negativo es lo mismo que 0 (ContinuacionesPorCorte sanea con Math.Max). Es la guarda que este repo ya tuvo que arreglar dos veces y hay test de los tres lados: default 3, 0 no continua, -5 tampoco. DOS COSAS QUE EL BRIEF NO MENCIONABA Y HABRIAN DEJADO EL ARREGLO A MEDIAS: (1) `tarea.Resultado` salia del ULTIMO paso del turno, asi que una respuesta continuada habria terminado Completada con solo el ULTIMO tramo como resultado -- el texto pegado (TextoDelTurnoPegado) es la mitad del criterio y hace falta tambien en FinalizarAsync, no solo en el camino agotado; los tramos se pegan SIN SEPARADOR porque la continuacion retoma a mitad de palabra. (2) `ServicioTareas` solo asignaba turno.Respuesta en un paso con StopReason == FinTurno: un turno cortado y agotado no mostraba NINGUNA respuesta en la conversacion (solo los pasos) -- lo encontro el test de ConversacionTests al fallar con "Expected 'Texto cortad', Actual null". Es 1 condicion y acumula igual que el motor. TERCERA COSA, DE LA API Y NO DEL DISENO: un pedido que termina en un mensaje del asistente cuyo texto acaba en espacios lo rechaza la API entera, y un corte por max_tokens cae donde cae -- SinEspacioAlFinal recorta SOLO el pedido de la continuacion y SOLO si el ultimo bloque es texto; el paso guardado queda intacto, asi que el texto pegado no pierde el espacio. Sin esta guarda, la continuacion se convertia en un 400 y la tarea volvia a morir por otro camino. UN TEST DE OTRO SPRINT HUBO QUE REESCRIBIRLO, declarado: ConversacionTests.Turno_fallido_por_max_tokens_mantiene_la_alternancia_y_conserva_su_error afirmaba LITERALMENTE el defecto (Fallida + "La respuesta supero el maximo de tokens configurado"). Se conservo lo que cuidaba -- la alternancia usuario/asistente despues de un turno cortado -- corriendo con el tope en 0, y pasa a llamarse Turno_cortado_por_max_tokens_mantiene_la_alternancia_y_no_queda_fallido. VerificacionesTexto, que tambien mira MotivoFin.MaxTokens, NO se toco: es del circuito de evaluacion de prompts (M8/M22), corre por su propio ejecutor, y ahi un caso de prueba cortado SIGUE siendo un fallo. Build 0 errores, 1253/1253 verde (base 1243 + 10), MEDIDO SIN PIPE, con cinco mutaciones corridas y restauradas (la rama revertida al Fallida viejo tumba los 6 tests de criterio; el pegado recortado tumba 4; el turno mostrando respuesta solo en FinTurno tumba 2). La app no se levanto. Commit local, sin push, sin deploy.


### Traza de corrida -- 2026-10-05 / etapa implementacion
- Reintentos: 0
- Criterios fallados: ninguno (brief de Joaquin del 2026-10-05, un solo pedido, no vino de partes de QA)
- Reglas releidas: ninguna instruccion nueva: se trabajo sobre el bucle de ProcesadorTareas ya leido en la tanda 1, memorias propias: 'Medir sin pipe', 'Un filtro que protege se escribe nombrando el caso', 'Dos textos por error de herramienta'
- Arranque real: 18 KB (~4k tokens)
- Nota: M32 TANDA 1b, UNA SOLA GUARDA, SIN MIGRACION. EL PEDIDO: una continuacion que falla NUNCA mata la tarea, porque es una llamada de mas que nadie pidio y su fallo no puede costar mas que no haberla intentado. EL RIESGO QUE LA MOTIVA NO SE PUDO COMPROBAR Y ESO ES PARTE DEL DISENO: la documentacion oficial (verificada 2026-10-05) dice que los assistant-turn prefills devuelven 400 en claude-sonnet-5 y claude-opus-5, y la continuacion de la tanda 1 deja la conversacion terminando en un mensaje del asistente; la cuenta esta sin saldo y el modelo simulado no valida nada de esto, asi que la guarda NO APUESTA a que el prefill ande: HACE QUE NO IMPORTE. COMO QUEDO: try alrededor de la llamada con 'catch (Exception ex) when (continuandoCorte && ex is not OperationCanceledException)' -> TerminarCortadaAsync, que es el cierre del tope agotado EXTRAIDO Y COMPARTIDO (nota + MarcarFinAsync(Completada) con el texto pegado + GuardarYAvisar): lo unico distinto entre las dos ramas es el texto. La tarea no queda Fallida NI VUELVE A LA COLA a repetir el mismo 400 hasta MaxIntentos. LA GUARDA ES ESTRECHA A PROPOSITO Y HAY TEST QUE LO AFIRMA: el error de una llamada normal sigue subiendo a RegistrarErrorAsync, que reintenta, porque ahi no hay trabajo entregable esperando y tragarselo esconderia una tarea que fallo. LO QUE QUEDA REGISTRADO EN LA BASE, que era el segundo pedido: MensajeContinuacionFallida es un texto DISTINTO al del tope agotado a proposito -- asi se sabe cual de las dos cosas paso CONTANDO NOTAS, sin logs -- mas un segundo bloque de texto en la misma nota con el tipo de la excepcion (lo que distingue un 400 de la API de un timeout de red) y el mensaje recortado a 500. AnotarNotaDelMotorAsync acepta ahora un 'detalle' opcional, aparte del aviso para la persona y sin reemplazarlo. UN BUG QUE ENCONTRE AL ESCRIBIR LA GUARDA Y NO HABRIA APARECIDO EN LOS TESTS: el numero del paso de la nota no puede ser siguienteNumero, porque el escalonamiento de A-M27-8 pudo dejar SUS PROPIAS notas antes de que la llamada se caiga, y repetir un numero rompe el guardado entero por el indice unico (tarea, numero); se lee de la base con ProximoNumeroAsync. CONSECUENCIA CONOCIDA QUE DEJO ESCRITA Y NO ARREGLE: si el pedido de la continuacion no entra POR TAMANO, lo atrapa antes el escalonamiento de M27 dentro de EnviarConEscalonamientoAsync y la tarea queda Fallida -- terminada y seguible, con todos los tramos guardados, no se pierde trabajo. Convertirlo exigiria re-marcar el fin despues de que ese metodo ya guardo y aviso, duplicando notificacion, aviso de programacion y destilado de M25: peor que la consecuencia. Y el brief prohibia tocar ese metodo. Sigue en pie la de la tanda 1: una tarea PROGRAMADA dice 'termino correctamente' sobre una respuesta cortada porque EjecutorProgramaciones elige por == Completada; el arreglo es del lado del aviso (AvisarFinDeTareaAsync), no del estado, y asi quedo escrito en 5-implementador. NO SE INTENTO ESQUIVAR EL PREFILL con un mensaje de usuario tipo 'segui': contamina el hilo y queda en la instantanea. Build 0 errores, 1255/1255 verde (base 1253 + 2), MEDIDO SIN PIPE, dos mutaciones corridas y restauradas (la guarda neutralizada con 'false &&' tumba el test: la tarea muere; el detalle de la nota en null tumba el mismo test por el asserto del registro). La app no se levanto. Commit local, sin push, sin deploy.

