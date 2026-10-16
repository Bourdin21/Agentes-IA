<!-- Archivado de docs/crm-olvidata/trazabilidad.md el 2026-10-15 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-09 (1 bloques archivados)

- 2026-09-14 (9) — arquitecto-mvc: Arquitectura de "4 frentes — combo con gancho" (pendiente de aprobacion)

---

## 2026-09-14 (9) — arquitecto-mvc: Arquitectura de "4 frentes — combo con gancho" (pendiente de aprobacion)

- **Agente/etapa:** `arquitecto-mvc`, modo Ask (sin codigo). Entrada: analisis (6) y diseño (8) aprobados. Detalle en `definiciones/3-arquitecto-mvc.md` §7.2.
- **Reutilizacion:** PAT-031 es patron sin codigo portable (nacido en este diseño); ningun proyecto del historial resuelve algo equivalente. Todo lo demas es reutilizacion literal intra-repo → para el presupuestador es iteracion evolutiva sobre modulos existentes, no modulo nuevo.
- **Modelo:** enums `GanchoContacto` y `FrenteComercial`; `Contacto` + `Gancho`/`MotivoGancho`/`FechaGancho`/`GanchoAMano`/`PlantillaPrimerContacto` + metodo `AsignarGancho` (CRM-001); `ModuloCatalogo.Frente` (default Build); 4 plantillas por gancho en `ConfiguracionOutbound`. **1 migracion aditiva `AddGanchoYFrenteComercial`**, sin SQL de datos (la carga inicial usa las reglas en C#).
- **Piezas nuevas:** `CategoriaHelpers` (fuente unica del vocabulario de categorias, hoy escrito en 3 lugares), `GanchoHelpers` (grupos, dominios en memoria, tabla de decision), `PlantillasCombo` (nombres fijos: los botones QUICK_REPLY no los soporta la rama generica G1), `ModuloCatalogoQueries` (la consulta de modulos estaba duplicada en `BotFlowService` y `ConversacionIaService`).
- **Hallazgos tecnicos nuevos:** (1) el lote corta con `.Take(cupo)` antes de enviar — el filtro de "sin plantilla" tiene que ir antes o un salteado ocupa cupo; (2) la guarda de rename/delete de plantillas (B5) y `TemplatesSinCampana` de `/Bot/Salud` solo miran campañas — hay que sumar la configuracion (LP-002); (3) `ProcessFollowUpsAsync` manda `olv_nurturing_v2` (texto de gestion) a todo `MensajeEnviado` y `MarkColdAsync` solo enfria desde `FollowUpEnviado` → decision A1.
- **Cache del prompt:** todo lo nuevo que es igual para todos va al bloque estable; gancho/oferta/modulos al bloque del contacto. Reescritura de cache una sola vez al desplegar.
- **Riesgos:** T1-T12 (MH-001/CRM-019, CRM-001, CRM-007/016, CRM-020, CRM-022, LP-002 cubiertos explicitamente). Permisos sin cambios. Maquina de estados sin valores nuevos.
- **Gate:** Presupuesto bloqueado hasta aprobar la arquitectura y decidir A1 (follow-up de los ganchos combo; recomendada A1-a: sin `nurturing_v2`, frio directo a los 7 dias) y A2 (nombres de plantilla combo en codigo).
- **ARQUITECTURA APROBADA (mismo dia):** Joaquin avanzo con las opciones recomendadas — A1-a (sin follow-up de gestion para PresenciaWeb/Administracion/Consultas, frio directo a los 7 dias) y A2 (nombres de plantilla combo en codigo). Presupuesto habilitado.
