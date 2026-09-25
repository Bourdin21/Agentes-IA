<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/1-analista-funcional.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 1-analista-funcional - M07 (2 bloques archivados)

- Preguntas abiertas M7 (hipótesis tomadas sin gate, autorización 2026-09-14)
- Clasificacion de perfil de cliente M7

---

### Preguntas abiertas M7 (hipótesis tomadas sin gate, autorización 2026-09-14)
- **P1 — ¿Una etapa o dos?** *A:* M7a (subagentes + reglas propuestas) y M7b (asignaciones + asistente). *B:* una sola etapa. *Tomada: A* (dos mecanismos independientes; M7b usa lo de M7a solo al proponer tareas a coordinadores).
- **P2 — ¿A quién puede delegar un agente?** *Ejemplo:* el "Orquestador inmobiliario" delega "armá la ficha" en el "Tasador" de su rubro; o un "CM del estudio" le pide algo al "Asistente contable". *A:* jerarquía del núcleo (hijos del base, más derivados de la empresa de esos hijos que el autor puede usar). *B:* a cualquier agente que el autor pueda usar. *Tomada: A* (el núcleo define qué equipos tienen sentido y está evaluado).
- **P3 — Profundidad.** *A:* un nivel (el subagente no delega). *B:* hasta dos niveles. *Tomada: A* (la jerarquía del núcleo hoy es de un nivel; configurable a futuro).
- **P4 — Cantidad.** *A:* 5 por respuesta y 10 por turno. *B:* sin tope (solo el límite de gasto). *Tomada: A*.
- **P5 — ¿Cómo espera la principal?** *A:* estado nuevo "Esperando a otros agentes" que suelta el motor. *B:* el worker queda esperando dentro de la tarea. *C:* la principal sigue en la cola y se salta hasta que terminen. *Tomada: A* (B bloquea el único hilo del cliente; C consume reclamos e intentos).
- **P6 — ¿Se puede conversar con una subtarea?** *A:* no; se sigue en la principal. *B:* sí, con ajustes propios. *Tomada: A* (evita resultados que el coordinador nunca ve).
- **P7 — Costo.** *A:* cada subtarea con su costo y la principal muestra el total con subtareas. *B:* sumar el costo al de la principal. *Tomada: A* (evita contar dos veces en M6).
- **P8 — Subtareas en Tareas.** *A:* ocultas por defecto, con filtro y contador en la principal. *B:* listadas como cualquier tarea. *Tomada: A*.
- **P9 — Qué recibe el coordinador.** *A:* la respuesta final recortada a 20.000 caracteres o el motivo del fallo. *B:* toda la conversación de la subtarea. *Tomada: A*.
- **P10 — Cancelación.** *A:* cascada al cancelar la principal; una subtarea se puede cancelar sola. *B:* solo cascada. *Tomada: A*.
- **P11 — ¿Qué reglas propone un agente de trabajo?** *Ejemplo:* "de ahora en más, en viñetas" (preferencia de Laura) o "a Panadería Norte nunca le mencionamos precios" (regla del cliente). *A:* preferencias del autor y reglas del cliente de la tarea, solo nuevas. *B:* también de empresa y área. *Tomada: A* (B es del configurador del Director, M4b).
- **P12 — ¿Quién confirma?** *A:* preferencia solo el autor; regla del cliente el autor o un Director. *B:* siempre un Director. *Tomada: A* (coincide con quién puede crear cada regla en M3).
- **P13 — ¿Dónde se ven las propuestas?** *A:* tarjeta en la conversación + card en Reglas. *B:* solo la tarjeta. *Tomada: A* (el Director puede no abrir la tarea del Empleado).
- **P14 — Máximo de propuestas por respuesta.** *A:* 3. *B:* 10 como el configurador. *Tomada: A* (un agente de trabajo no es un configurador).
- **P15 — ¿Quién asigna tareas a personas?** *Ejemplo:* el Director asigna "Llamar a Panadería Norte por el balance" a Laura; o Laura se la pasa a Martín. *A:* solo el Director (a mano o con el asistente). *B:* cualquier miembro a cualquiera. *Tomada: A*.
- **P16 — Estados de la asignación.** *A:* Pendiente, En curso, Hecha, Cancelada, con Reabrir y "Vencida" calculada. *B:* solo Pendiente / Hecha. *Tomada: A*.
- **P17 — ¿La tarea de agente cierra la asignación?** *A:* no, la persona la marca como hecha. *B:* se cierra al completarse la tarea. *Tomada: A* (la persona responde por el resultado).
- **P18 — Recordatorios de vencimiento.** *A:* no; "Vencida" visible y contador. *B:* notificación el día anterior. *Tomada: A* (recordatorios → M12).
- **P19 — Contexto del asistente.** *A:* propio, sin reglas de la empresa como instrucciones (como M4b). *B:* con las reglas de la empresa. *Tomada: A*.
- **P20 — ¿A nombre de quién queda la tarea de agente que propone el asistente?** *A:* del Director que aplica (su límite y su visibilidad). *B:* de un Empleado elegido. *Tomada: A* (para que la haga un Empleado, se le asigna y él se la pide a un agente).
- **P21 — ¿El asistente delega en subagentes?** *A:* propone tareas a cualquier agente disponible, incluidos coordinadores que después delegan. *B:* crea subtareas directamente. *Tomada: A*.
- **P22 — ¿El staff ve asignaciones?** *A:* no en M7b; ve (lectura) las conversaciones del asistente como las de configuración. *B:* sí, en el backoffice. *Tomada: A*.
- **P23 — Prompt del asistente.** *A:* primera versión redactada como borrador, importada sin publicar, Joaquín la revisa y publica. *B:* la escribe Joaquín. *Tomada: A* (es de plataforma, como el configurador).
- **P24 — QA sin costo.** *A:* guiones del simulador para delegación ("deleg"), propuesta de regla ("de ahora en más" / "prefer") y asistente ("repart"). *B:* solo tests. *Tomada: A*.
- **P25 — ¿Un Empleado ve asignaciones de otros?** *Tomada: no* (404; decisión 4 de organización aplica a clientes, no a trabajo asignado).
- **P26 — ¿Con qué coordinador se prueba?** *A:* rubro ficticio en tests y, en el navegador, el rubro ya importado en dev que declara coordinador, publicado solo en dev. *B:* crear un rubro de demostración en `nucleo/`. *Tomada: A* (no se crea contenido de rubros).
### Clasificacion de perfil de cliente M7
Producto propio (proyecto personal): presupuesto omitido.

---

**M6 — Aprobaciones de acciones por rol y límites de gasto por organización y miembro** (Discovery + Análisis, 2026-09-15). Estado: **aprobado sin gate por autorización de Joaquín 2026-09-14** (programa "plan completo local": se toma la opción recomendada en cada pregunta y queda como hipótesis). Pendientes PA-01..13 siguen abiertos (ver `metadata.md`). Presupuesto omitido (proyecto personal).

Contexto: el motor (M1) ya tiene el estado `EsperandoAprobacion` (enum, badge "Espera aprobación", Cancelar lo acepta) y la marca `IHerramientaAgente.RequiereAprobacion`, pero **el procesador ignora la marca** y todas las herramientas actuales la tienen en `false` (fecha, configurador M4b, documentos M5). El costo de cada llamada al modelo ya se calcula y se guarda por paso (`PasoTarea.CostoUsd`, valor del momento), por tarea y en `EventoUso`; con API key propia del cliente se guarda 0. **No existe ningún tope**: `docs/diseno-motor-agentes.md` §8 prevé `Tenant.LimiteMensualUsd` y §6 el flujo de aprobación; `docs/diseno-organizacion-roles-reglas.md` §2 fija "Consumo y límites de gasto por miembro: Director ✅ / Empleado 👁 su propio consumo" y "Aprobar acciones de agentes: Director cualquiera; Empleado las de sus tareas salvo las marcadas 'requiere Director'", y §6 la entidad `LimiteGastoMiembro`. La pantalla "Uso y consumo" es solo del staff, por rango de fechas y por organización. PLAN §5: Olvidata paga los tokens, así que hace falta medición real y protección del margen. M11 (conectores) traerá las primeras herramientas con efectos fuera del sistema y M12 (programadas) ejecutará tareas sin nadie mirando: ambas dependen de esta etapa.

Objetivo de negocio: (1) que ninguna organización ni miembro gaste en un mes más de lo acordado, con avisos antes de llegar, para proteger el margen de Olvidata y evitarle sorpresas al Director; (2) que cada organización vea en palabras cuánto gasta y en qué; (3) que **ninguna acción de un agente marcada como sensible se ejecute sin que una persona con permiso la apruebe**, con el mecanismo listo y probado antes de que existan herramientas reales.

#### Alcance incluido (M6)
1. **Límite mensual de la organización** en USD, cargado por el staff en el backoffice; valor por defecto configurable para organizaciones nuevas y existentes; "sin límite" solo SuperUsuario (P2).
2. **Límite mensual por miembro**, opcional, cargado por el Director, nunca mayor que el de la organización (P3).
3. **Período = mes calendario argentino**; consumo = suma del costo guardado de las llamadas al modelo del mes (P1).
4. **Avisos** al 80 % y al 100 % del límite de la organización (a los Directores) y del límite de un miembro (al miembro; al 100 % también a los Directores), una vez por mes y umbral, como notificación del portal (P7).
5. **Bloqueo**: con el límite alcanzado no se crean tareas, conversaciones de configuración ni ajustes; una tarea en curso termina la llamada que está haciendo y su turno queda "Fallida" con un mensaje llano; se retoma con un ajuste cuando haya margen (P5).
6. **Pantalla Consumo**: el Director ve la organización (gastado / límite / %) y el detalle por miembro (con su límite y "Cambiar límite"), por área, por agente y por cliente de cartera, eligiendo el mes; el Empleado ve su consumo, su límite y su detalle por agente y por cliente; el staff ve lo mismo por organización (backoffice) y el mes en curso con el límite en "Uso y consumo".
7. **Organizaciones con API key propia**: sin límites, avisos ni bloqueos; el consumo se muestra en tokens con un aviso (P4).
8. **Aprobación de acciones**: si el agente pide una herramienta marcada, la tarea pasa a "Espera aprobación" **sin ejecutarla**; la conversación muestra una tarjeta con lo que quiere hacer en palabras y los datos; **Aprobar** la ejecuta y el agente sigue; **Rechazar** (motivo opcional) le devuelve el rechazo al agente, que sigue sin hacerla.
9. **Quién aprueba** según el nivel que define la herramienta: "Quien pidió la tarea" (el autor o cualquier Director) o "Solo un Director" (P8, P16). El staff solo ve.
10. **Bandeja "Aprobaciones"** con los pedidos pendientes que la persona puede resolver, historial y contador en el menú (P15).
11. **Vencimiento** a las 72 h: el pedido queda "Venció sin respuesta" y el agente sigue sabiendo que no se hizo (P10).
12. **Notificaciones** del portal al pedir aprobación, cuando la resuelve otra persona y cuando vence.
13. **Cancelar** una tarea en espera cancela sus pedidos pendientes.
14. **Reanudación segura**: el pedido queda guardado antes de soltar la tarea y una acción aprobada se ejecuta una sola vez aunque el proceso se corte (idempotencia M1).
15. **Herramientas de demostración** (solo Development con modelo simulado): una de nivel "quien pidió la tarea" y una de "solo un Director", sin efectos fuera del sistema, con guion en el simulador para QA sin costo (P14).

#### Alcance no incluido
- **Facturación y cobro al cliente** (precio por uso, margen, comprobantes): depende de la unidad de cobro, **decisión pendiente de Joaquín (PLAN §8.1)**. El consumo de M6 es costo en USD a precio de lista, no un monto a facturar.
- Planes comerciales como entidad (el staff carga el número a mano).
- Presupuesto **por tarea** (sigue el máximo de pasos por turno), límites por área o por agente (solo se muestran), límites diarios.
- Herramientas reales con efectos (mails, WhatsApp, pagos, sistemas del cliente) → **M11**; escritura de documentos por el agente → posterior (M5 P11).
- Que el Director configure qué herramientas requieren aprobación o suba una a "solo un Director" (lo define la herramienta en código, P8).
- Aprobación automática, "no volver a preguntar", aprobar en lote, delegar aprobaciones y autonomía por rol → **M12**.
- Avisos por email o WhatsApp (solo notificación del portal, P7); proyección de gasto a fin de mes y gráficos históricos.
- Editar los datos de la acción antes de aprobar (P13).
- Valorizar en USD el consumo con API key propia.

#### Dependencias
- M1 (bucle reanudable, idempotencia por `tool_use_id`, `EsperandoAprobacion`, Cancelar), M2 (roles, áreas, visibilidad de tareas, backoffice de organización), M3b (turnos, cierre de turno, ajustes, modelo simulado), M4 (agentes de la organización para agrupar consumo), M4b (herramientas con contexto, guion de herramientas en el simulador, tarjetas confirmables PAT-032), M5 (clientes de cartera en tareas); notificaciones del portal y SignalR del template.
- Previsto para **M11**: los conectores declaran sus herramientas con aprobación y nivel. Para **M12**: una programación consume el límite de su responsable y sus pedidos de aprobación vencen igual.
