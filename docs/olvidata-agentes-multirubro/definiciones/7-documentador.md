# Memoria - Documentador

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-09-14

## Definiciones vigentes

### M4b Configurador de reglas (2026-09-14)
Documento entregado: `docs/olvidata-agentes-multirubro/resumen-sprint-m4b-configurador.md` (formato 31, lector Joaquín).
- **Alcance entregado:** configurar conversando (chips, tarjetas de propuesta Aplicar / Editar y aplicar / Descartar / Aplicar todas / Reintentar, aviso de regla cambiada), confirmación solo por botón, lista compartida entre Directores, origen en historial, costo en Tareas, lectura acotada. QA: apto con observaciones, 15/15 CA, sin defectos funcionales; OLV-004 de contraste global reportado sin fix.
- **Pendientes:** prompt del configurador en borrador (evaluar y publicar), corrida real con costo, configurador para Empleados, contraste global de botones (PA-11), "Ver pasos" técnico (PA-12).
- **Próximo paso:** publicar prompt + corrida real antes de M5.

### M4 Agentes de la organización (2026-09-14)
Documento entregado: `docs/olvidata-agentes-multirubro/resumen-sprint-m4-agentes.md` (formato 31, lector Joaquín).
- **Alcance entregado:** catálogo por secciones, crear/editar/duplicar agentes derivados, versiones, publicar para la empresa sin revisión con aviso a Directores, archivar/reactivar (con sección Archivados), reglas para agentes de la empresa, sugerencias activables, rubro incluido siempre + sincronización, vista de staff. QA: apto con observaciones, 14/14 CA aplicables (CA-M4-03 pospuesto), 1 defecto menor de contraste corregido.
- **Pendientes:** revisión del Director (pospuesta), contenido de rubro "negocio" y sugerencias reales, confirmar sección "Archivados", aviso a la autora cuando el Director edita su agente, contrastes heredados del theme, pendientes abiertos PA-01..07.
- **Próximo paso:** M4b Agente configurador de reglas del Director.

### M3b Seguir conversando (2026-09-14)
Documento entregado: `docs/olvidata-agentes-multirubro/resumen-sprint-m3b-conversacion.md` (formato 31, lector Joaquín).
- **Alcance entregado:** ajustes sobre tareas terminadas (incluidas fallidas y canceladas) con el mismo agente/cliente/reglas, conversación en orden con pasos plegados, respuesta en vivo, copiar, aviso de reglas cambiadas con atajo a tarea nueva, preferencias ajenas ocultas al Director, listado con mensajes y última actividad, límites. QA: apto con observaciones, 14/14 CA, 1 defecto menor corregido (tema oscuro).
- **Pendientes:** corrida real con costo (calidad, caché, error de conversación larga); recuperación tras reinicio hasta 5 min (lease del motor M1); adjuntos (M5); publicar reglas de plataforma (pendiente de M3).
- **Beneficios comunicados:** iterar como en Claude web con contexto de la empresa y registro; costo claro por autor.
- **Próximo paso:** M4 Agentes de la organización + reglas sugeridas por rubro.

### M3 Reglas (2026-09-14)
Documento entregado: `docs/olvidata-agentes-multirubro/resumen-sprint-m3-reglas.md` (formato 31, lector Joaquín).
- **Alcance entregado:** reglas en lenguaje llano por empresa, área, agente, cliente y preferencias; "Siempre / Salvo que se indique otra cosa"; procedimientos; historial y desactivación; nuevo pedido con cliente y vista previa; registro de reglas usadas por tarea con aviso de cambios; límites; vista de staff; reglas de Olvidata con evaluación; accesos desde cliente y área; filtro por cliente en tareas. QA: apto con observaciones, 15/15 CA, sin defectos.
- **Pendientes:** publicar las 3 reglas de plataforma (en borrador); corrida real con costo para validar obediencia/inyección/caché; seguir conversando (M3b); OBS-M3-1 (Director ve preferencias de quien pidió la tarea en el detalle) a decidir.
- **Beneficios comunicados:** sin repetir contexto, lo obligatorio lo decide el Director, auditoría de instrucciones por tarea.
- **Próximo paso:** M3b Seguir conversando sobre una tarea.

### M2 Organización (2026-09-14)
Documento entregado: `docs/olvidata-agentes-multirubro/resumen-sprint-m2-organizacion.md` (formato 31). Lector: Joaquín (dueño del producto; proyecto personal).

### Alcance entregado al cliente
M2 Organización del portal, validado por QA (apto con observaciones, todos los CA OK): roles Director/Empleado con refresco inmediato de permisos; ABM de Áreas; gestión de miembros (rol, área, bloqueo) con organización siempre con un Director activo; cartera de clientes con CUIT/DNI validado, búsqueda y filtros persistentes, baja solo Director; tareas visibles según rol; backoffice "Organizaciones y licencias" con alta de miembros; formularios unificados, Select2 y tema oscuro corregido.

### Pendientes o fuera de alcance
- Sin UI de staff para editar nombre/email/rol/estado de un miembro existente.
- `Tenant.Estado` no se evalúa en la sesión (organización suspendida sigue entrando).
- Pantallas legadas (Usuarios, listado y alta de organizaciones, Perfil) sin el sistema de formularios nuevo.
- Observaciones QA menores: filtros de texto solo con `keyup` (pegar con mouse no refresca), bajo contraste de `ov-alert info` en tema oscuro, URLs absolutas en layout.

### Beneficios comunicados
Autonomía de cada organización, aislamiento verificado entre organizaciones, base para reglas por nivel (M3) y agentes propios (M4).

### Proximo paso sugerido
M3 Reglas.

## Historial de ajustes
- 2026-09-14: Resumen de entrega de M2 Organización redactado en formato 31, en primera persona, sin tecnicismos, con pendientes declarados por implementador y QA.
- 2026-09-14: Resumen de entrega de M3 Reglas (formato 31, lenguaje llano alineado a D-M3-8..12), con pendientes de publicación de reglas de plataforma, corrida real y M3b.
- 2026-09-14: Resumen de entrega de M3b Seguir conversando (formato 31), próximo paso M4.
- 2026-09-14: Resumen de entrega de M4 Agentes de la organización (formato 31), próximo paso M4b.
- 2026-09-14: Resumen de entrega de M4b Configurador de reglas (formato 31), próximo paso: publicar prompt y corrida real antes de M5.
