<!-- Archivado de docs/olvidata-agentes-multirubro/trazabilidad.md el 2026-10-05 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-09 (15 bloques archivados)

- 2026-09-14 - arquitecto-mvc
- 2026-09-14 - implementador
- 2026-09-14 - qa
- 2026-09-14 - documentador
- 2026-09-14 - presupuestador
- 2026-09-14 - analista-funcional
- 2026-09-14 - analista-funcional
- 2026-09-14 - disenador-funcional
- 2026-09-14 - arquitecto-mvc
- 2026-09-14 - orquestador
- 2026-09-14 - implementador
- 2026-09-14 - documentador
- 2026-09-14 - presupuestador
- 2026-09-14 - orquestador
- 2026-09-14 - presupuestador

---

### 2026-09-14 - arquitecto-mvc
- Etapa: Arquitectura (M3 Reglas)
- Cambio: entidades `Regla` (token `VersionActual`) y `ReglaEvento` (historial inmutable), `TipoArtefacto.ReglaPlataforma` con rubro técnico `plataforma` en el núcleo (3 reglas iniciales en borrador), `IReglaService` (permisos por alcance, límites por balde, versiones, mismo tema, etiquetas, vista staff), `IConstructorContexto` único para vista previa, instantánea y motor (instantánea por ids + hash, reconstrucción verificada al ejecutar), `SolicitudModelo.Sistema` en 3 bloques con caché, tarea con cliente de cartera, `ReglasController` y ajustes en Agentes/Tareas/Cartera/Áreas/backoffice; migración `ReglasM3`.
- Motivo: diseño M3 aprobado con simplificación de UI.
- Impacto en capas: Domain (2 entidades, 5 enums, tarea), Application (servicio de reglas, constructor, DTOs, opciones, permisos), Infrastructure (servicios, constructor, proveedor de modelo, importador, configs), Web (1 controller nuevo, 5 modificados, vistas).
- Riesgos/supuestos: RT-M3-01 caché de bloques chicos, RT-M3-02 carrera de límites aceptada, RT-M3-03 inmutabilidad de eventos/versiones, R-M3-01 inyección (mitigada, no garantizada; prueba real opcional con OK de costo). Reuso literal: pantallas/helpers M2, importador y versionado del núcleo, concurrencia M2, ModeloGuionado; patrón crm-olvidata. PAT-028 ampliado.
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
### 2026-09-14 - presupuestador
- Etapa: Arquitectura M4b (gate) + Presupuesto (omitido)
- Cambio: Joaquín aprobó la arquitectura de M4b ("si", puntos 1–7). Presupuesto omitido. Se lanza Implementación.
- Motivo: gate Arquitectura → Implementación de M4b.
- Impacto en capas: —
- Riesgos/supuestos: —
