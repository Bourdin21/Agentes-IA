<!-- Archivado de docs/olvidata-agentes-multirubro/trazabilidad.md el 2026-10-03 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-09 (11 bloques archivados)

- 2026-09-14 - qa
- 2026-09-14 - analista-funcional
- 2026-09-14 - analista-funcional
- 2026-09-14 - disenador-funcional
- 2026-09-14 - disenador-funcional
- 2026-09-14 - arquitecto-mvc
- 2026-09-14 - presupuestador
- 2026-09-14 - documentador
- 2026-09-14 - presupuestador
- 2026-09-25 — olvidata-ceo (diferenciales comerciales del frente AI Agents)
- 2026-09-28 - olvidata-ceo

---

### 2026-09-14 - qa
- Etapa: QA (M3b Seguir conversando sobre una tarea)
- Cambio: verificación por navegador real (Playwright librería desde Node; MCP `playwright` no disponible en la sesión) con el modelo simulado en Development (costo cero; advertencia confirmada en cada arranque y clave de API inválida en el proceso como resguardo). 14/14 CA-M3b y 10 HU en PASS, más D-M3b-1/2 y la máquina de estados (Completada/Fallida/Cancelada → Pendiente, fallo por máximo de pasos, cancelación por autora y por Directora, reinicio del portal a mitad de turno con reanudación al vencer el lease sin duplicar el ajuste). IDOR: 20 combinaciones → 404. Listado con Mensajes y Última actividad (filtros, orden por defecto, Session, Limpiar, búsqueda), mobile con cuadro sticky, regresión M3/M2 y portal por rol sin fallas. Defecto QA-M3b-01 (minor): alertas `.ov-alert` y badge "Ajuste" ilegibles en tema oscuro → ítem nuevo OLV-002 en `docs/qa/regresiones-manuales.yml` y auto-fix en `src/OlvidataAgentes.Web/wwwroot/css/site.css` (contraste 1,5–2,6 → ≥ 6,7; tema claro sin cambios; cierra OBS-4 de M2).
- Motivo: etapa 6 del flujo sobre la implementación M3b.
- Impacto en capas: Web (CSS de tema oscuro). Sin cambios de lógica, datos ni migraciones.
- Evidencia: build 0 errores / 0 advertencias; tests 83/83 antes y después del auto-fix; scripts y capturas `m3b-*` en el scratchpad de la sesión; portal detenido; ninguna tarea Pendiente/EnCurso; licencia, reglas 16/21, `MaxPasos` y costo de #14 restaurados.
- Riesgos/supuestos: OBS-M3b-1 reanudación tras reinicio espera el lease (hasta 5 min, heredado de M1); OBS-M3b-3 `ReglasCambiaronAsync` sin protección en el detalle (CRM-020); calidad real del ajuste, caché del historial y error de conversación demasiado larga pendientes de la corrida paga. Veredicto: apto con observaciones. Detalle en `definiciones/6-qa.md` (M3b).
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
### 2026-09-25 — olvidata-ceo (diferenciales comerciales del frente AI Agents)

- **Etapa:** fuera del flujo Discovery→Cierre. Revisión comercial a pedido de Joaquín, a partir del research de ingeniería de agentes 2026 (Microsoft Build, Anthropic Engineering, AWS AgentCore, Google A2A).
- **Cambio:** nueva sección **§2.1 de `plan-comercializacion.md`** — seis diferenciales escritos como argumento de venta (frase literal al cliente, objeción que desactiva, módulo/plan al que engancha, y si es «ya lo tenemos y falta nombrarlo» o «hay que construirlo»). Se ubicó después del estado técnico real (§2) porque es su lectura comercial: qué de lo construido es vendible. Tres pendientes nuevos en `metadata.md`: **PA-42** (plano de control auditable por organización), **PA-43** (telemetría de horas ahorradas sobre `EventoUso`), **PA-44** (memoria de largo plazo aislada por tenant).
- **Motivo:** la objeción que frena el setup de lista es *«¿por qué te pago a vos si un freelance me lo arma por USD 500?»*, y no se contesta con horas ni con funcionalidades. Se contesta con controles — que en su mayoría **ya están construidos y no se nombran en ninguna propuesta**. El trabajo faltante es mayormente de redacción, no de desarrollo.
- **Lo accionable hoy, sin tocar código:** (1) *«las credenciales nunca entran al entorno donde corre el agente»* es verdad por M11 y por el modelo Tech Provider de Chatbots — entra tal cual en la próxima propuesta, costo cero; (2) los controles de M6/M11/M12 se enumeran módulo por módulo, **sin prometer «auditable»** hasta tener PA-42.
- **Dos reordenamientos de prioridad que salen de acá:** **PA-36** (herramienta de cálculo determinístico) deja de ser mejora técnica y pasa a ser **bloqueante comercial**: mientras «el agente no hace la aritmética» sea una instrucción de prompt y no código, el argumento de controles tiene un agujero justo en conciliación, IVA y balances, que es donde el cliente lo va a auditar. Y **PA-17 + PA-18** (aprobar los casos de M8 y correr la primera evaluación real con tope USD 1) dejan de ser deuda operativa: desbloquean el diferencial más difícil de copiar —los evals como entregable— y le dan contenido demostrable a la línea más floja del abono, la «1 ronda de ajuste de prompt por mes».
- **Respuesta comercial a una decisión que estaba abierta:** **PA-21** — si los evals son parte del abono, los agentes de la organización **sí** se evalúan antes de publicarse y lo paga el abono.
- **Impacto en capas:** ninguno. Documentación comercial y pendientes de producto. **No se tocó ningún precio vigente** (§3.2 para la cartera propia; rubro estándar y tiers Básico/Intermedio/Avanzado para organizaciones nuevas): cambia qué se dice para sostenerlos, no cuánto se cobra.
- **Riesgos/supuestos:** A2A (§2.1-F) es **solo posicionamiento a 2027** — no hay una línea de código ni está en el roadmap, y no se vende interoperabilidad. Se ata a PA-41 (canal internacional). El estado de M8 se tomó de `metadata.md` (PA-17..PA-22) y de las definiciones: **construido pero sin una sola corrida real contra la API**, así que el argumento B no se puede afirmar como probado hasta PA-18.
### 2026-09-28 - olvidata-ceo
- Etapa: Estrategia comercial (seguimiento de PA-41 / entrada 2026-09-25)
- Cambio: Agustín Hollger (lead-gen internacional) respondió a las 3 preguntas de calibración sin contestar ninguna en concreto: ICP genérico ("todo lo que sea tech b2b lo trabajamos"), prueba social sin un solo caso nombrado ("+50 empresas tech"), ningún mercado mencionado, y el único dato sustantivo fue "hay que invertir" — o sea retainer con plata adelantada, sin mención de success fee. Cierra con "llegado el momento coordinamos", dejando la pelota de nuestro lado sin aportar nada verificable.
- Decisión: se archiva el contacto sin pedir una segunda vuelta de datos (2 nombres + rango de fee) — ya tuvo la oportunidad de responder algo concreto y no la usó; insistir de nuevo es tiempo regalado, no filtro. El hilo ya tenía cierre natural (Joaquín le había dicho "te escribo yo cuando esté listo" el 2026-09-25); se responde un cierre corto para no dejarlo flotando ni reabrir con más preguntas que ya demostró esquivar.
- Motivo: coherente con PA-41 — el hito para sentarse con un canal externo (EULA en inglés + cobro internacional + caso real facturando) sigue sin cumplirse, así que no había nada que activar hoy aunque el contacto hubiera calificado.
- Aprendizaje agregado a PA-41 en `metadata.md`: cuando el canal internacional esté habilitado, preferir **partner por comisión/referido** sobre agencia de prospección fría a retainer — el retainer cobra por volumen de contacto y no por resultado, y no exige probar encaje de ICP antes de cobrar; un esquema por comisión alinea el incentivo del canal con el cierre real.
- Impacto en capas: — (decisión de negocio, sin cambios de código)
- Riesgos/supuestos: ninguno nuevo. No se tocó código ni ningún proyecto fuera de `docs/olvidata-agentes-multirubro/`.
