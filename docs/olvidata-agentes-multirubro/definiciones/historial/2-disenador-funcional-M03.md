<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/2-disenador-funcional.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 2-disenador-funcional - M03 (1 bloques archivados)

- M3b — Seguir conversando sobre una tarea

---

# M3b — Seguir conversando sobre una tarea

Estado: **aprobado por Joaquín el 2026-09-14** con D-M3b-1..7. Entrada: `1-analista-funcional.md` M3b aprobado 2026-09-14 (P1–P8 con las hipótesis).

### M3b-0. Escaneo de reutilizacion
| Fuente | Qué hay | Decisión |
|---|---|---|
| Template M1 — `Tareas/Detalle` + `_Progreso` + SignalR con respaldo de 10 s | Progreso en vivo por pasos | **Reutilizar**: el hilo se refresca con el mismo mecanismo (el parcial pasa a renderizar la conversación). |
| Template M3 — `_ReglasAplicadas`, `_VistaPreviaReglas` | Reglas de la tarea | **Reutilizar**, con el ajuste P6 (preferencias ajenas solo como contador). |
| Template M2 — listado de Tareas (filtros por columna, Session) | Grilla | **Reutilizar** sumando columnas. |
| century-21 A-04 (historial de conversación del bot, solo lectura) | Presentación de mensajes | Referencia visual menor. |
| Catálogo y demás proyectos | Sin conversación multi-turno persistida y reanudable contra un modelo | **Diseño nuevo** → PAT-029. |

### M3b-1. Alcance funcional resumido
El detalle de tarea pasa a ser una conversación: el autor envía ajustes sobre una tarea terminada (completada, fallida o cancelada), con el mismo agente, cliente y reglas; respuestas en vivo; costo acumulado; límites; copiar respuesta; listado con última actividad y mensajes; preferencias personales ajenas ocultas al Director.

### Decisiones de diseño M3b a validar en el gate
- **D-M3b-1 Suscripción vencida.** Si la organización ya no tiene licencia vigente para el rubro del agente, no se puede seguir ("Tu organización no tiene la suscripción vigente para este agente."). La conversación se sigue leyendo.
- **D-M3b-2 Cliente dado de baja.** No bloquea el seguimiento (el contexto está congelado); el encabezado muestra "Cliente: Panadería Norte (dado de baja)".
- **D-M3b-3 Qué es "la respuesta".** En cada turno, la burbuja del agente muestra el texto final del turno; los textos intermedios y las herramientas quedan en "Ver pasos".
- **D-M3b-4 Orden del listado.** Por defecto, "Última actividad" descendente.
- **D-M3b-5 Atajo.** Encabezado con "Nueva tarea con este agente" (precarga agente y cliente) y el mismo botón al llegar al límite.
- **D-M3b-6 Envío con teclado.** Ctrl+Enter envía; Enter hace salto de línea.
- **D-M3b-7 Preferencias ajenas (P6).** Para quien no es el autor ni staff, el grupo muestra solo "Preferencias personales de Laura (2 reglas)", sin títulos ni texto.

### Flujos de pantalla acordados M3b

**P-M3b-01 Detalle de tarea — conversación** (reemplaza la estructura Pedido / Resultado / Pasos)
- Encabezado: "Tarea #12 · CM del estudio" · línea: Cliente · creada · última actividad · pedida por (si quien mira no es el autor) · acciones: **Cancelar** (si hay un turno activo, rojo con confirmación) · **Nueva tarea con este agente** (secundario).
- Línea de estado: badge del estado · "5 mensajes" · "12.340 tokens · USD 0,12 en total".
- Card plegada "Lo que el agente tuvo en cuenta (9)" (M3) + si alguna regla cambió desde la creación: `ov-alert info` "Algunas reglas cambiaron desde que empezó esta conversación. Acá se siguen usando las de entonces." con enlace **Empezar una tarea nueva**.
- **Hilo**, en orden:
  - Mensaje de la persona (pedido inicial rotulado "Pedido"; los siguientes, "Ajuste"): inicial del nombre, nombre, fecha y hora, texto con saltos de línea.
  - Respuesta del agente: ícono del agente, nombre, fecha y hora, botón **Copiar**, texto; debajo `<details>` "Ver pasos (3)" con herramientas y resultados (formato actual de pasos).
  - Turno fallido: dentro del turno, `ov-alert danger` con el error ("La respuesta superó el máximo…") + hint "Podés pedirle que siga o reformular el pedido."
  - Turno cancelado: línea gris "Cancelaste esta respuesta." (o "La canceló <nombre>").
  - Turno activo: burbuja del agente con spinner "En cola…" o "Trabajando · paso 2 de hasta 25".
- **Cuadro "Seguir conversando"** (card al pie, sticky en mobile), solo para el autor:
  - Textarea (4 filas, crece hasta 10), placeholder "Pedile un ajuste: más corto, otro tono, agregá…", contador "0 / 10.000".
  - Hint: "Seguís con el mismo agente, cliente y reglas. Quedan 17 ajustes en esta conversación."
  - Botón primario **Enviar** (Ctrl+Enter).
  - Mientras hay un turno activo: textarea y botón deshabilitados, placeholder "Esperá la respuesta para seguir."
  - Límite alcanzado: en lugar del cuadro, `ov-alert warning` "Esta conversación llegó al máximo de 20 ajustes." + **Nueva tarea con este agente**.
  - Suscripción vencida (D-M3b-1): `ov-alert warning` con el mensaje, sin cuadro.
- Quien no es el autor (Director, staff): sin cuadro; nota discreta "Solo quien pidió la tarea puede seguir esta conversación."
- Envío: AJAX; al aceptar, se agrega la burbuja del ajuste y la de "En cola…", se limpia el textarea y se activa el refresco en vivo; al rechazar, toast con el mensaje y el texto queda en el textarea. Al llegar una respuesta nueva, scroll suave al último mensaje.
- Copiar: copia el texto de esa respuesta y muestra toast "Respuesta copiada."

**P-M3b-02 Tareas — listado** (ajuste)
- Columnas nuevas: **Mensajes** (número) y **Última actividad** (fecha y hora). Filtros: Mensajes (Select2: Todas / Solo el pedido / Con ajustes) y Última actividad (daterangepicker). Orden por defecto: última actividad desc (D-M3b-4). "Pedido" sigue mostrando el pedido inicial.

**P-M3b-03 Nueva tarea** (ajuste): acepta agente + cliente precargados desde "Nueva tarea con este agente".

**P-M3b-04 Lo que el agente tuvo en cuenta** (ajuste P6 / D-M3b-7): grupo de preferencias según quién mira (autor y staff: completo; otros: contador).

### ViewModels definidos M3b
| ViewModel | Campos y validaciones |
|---|---|
| `TareaConversacionViewModel` | `Resumen` (id, agente, estado, cliente, clienteDadoDeBaja, creada, ultimaActividad, pedidaPor) · `Mensajes[]` · `TurnoActivo?` (estado, paso, maxPasos) · `TokensTotales` · `CostoTotalUsd` · `PuedeSeguir` · `MotivoNoPuedeSeguir?` (EnCurso / NoEsAutor / Limite / SinSuscripcion) · `AjustesRestantes` · `ReglasCambiaron` · `ReglasAplicadas` · `AgenteRef` + `ClienteCarteraId?` (para el atajo) |
| `MensajeConversacionItem` | `Tipo` (Persona / Agente) · `Rotulo` (Pedido / Ajuste / Respuesta) · `Autor` · `Fecha` · `Texto` · `Pasos[]` (solo agente) · `Error?` · `Cancelado` |
| `SeguimientoViewModel` | `TareaId` · `Texto` [Required "Escribí tu mensaje."] [StringLength 10000 "El mensaje admite hasta 10.000 caracteres."] |
| `TareaListItem` (cambio) | + `mensajes`, `ultimaActividad` |

### Validaciones de UI M3b
| Caso | Mensaje |
|---|---|
| Mensaje vacío | "Escribí tu mensaje." |
| Más de 10.000 caracteres | "El mensaje admite hasta 10.000 caracteres." |
| Turno activo | "La tarea todavía está trabajando. Esperá la respuesta para seguir." |
| No es el autor | "Solo quien pidió la tarea puede seguir esta conversación." (403) |
| Límite | "Esta conversación llegó al máximo de 20 ajustes. Empezá una tarea nueva." |
| Suscripción vencida | "Tu organización no tiene la suscripción vigente para este agente." |
| Tarea inexistente o ajena | 404 |
| Copiar | "Respuesta copiada." |
| Confirmar cancelación de un turno | "¿Cancelar esta respuesta? La conversación anterior se conserva." |

### Maquina de estados M3b
| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Completada / Fallida / Cancelada | Ajuste del autor | Pendiente | autor; < 20 ajustes; texto válido; suscripción vigente; sin turno activo | registra el mensaje; limpia resultado/error del turno; notifica | no autor / límite / en curso / sin suscripción |
| Pendiente | Worker toma | EnCurso | igual que M1 | — | — |
| EnCurso | Fin de turno | Completada / Fallida | pasos del turno ≤ máximo | respuesta del turno | — |
| Pendiente / EnCurso | Cancelar | Cancelada | permiso de cancelar (M2) | conserva conversación | — |

### Permisos por pantalla / accion M3b
| Acción | Autor | Director (tarea ajena) | Empleado (tarea ajena) | Staff |
|---|:---:|:---:|:---:|:---:|
| Ver conversación | ✅ | ✅ | 404 | ✅ |
| Enviar ajuste | ✅ | ❌ 403 | 404 | ❌ |
| Cancelar turno | ✅ | ✅ | 404 | — |
| Copiar | ✅ | ✅ | — | ✅ |
| Texto de preferencias del autor | ✅ | contador | — | ✅ |

### Contratos funcionales para Services M3b
| Contrato | Operaciones | Reglas |
|---|---|---|
| Tareas | enviar ajuste (tarea, texto) · obtener conversación (mensajes por turno, turno activo, totales, puede seguir y motivo, ajustes restantes, reglas cambiaron) · listar con mensajes y última actividad · precargar nueva tarea desde otra | RF-M3b-01..10; D-M3b-1..7 |
| Motor | reconstruir conversación con mensajes de ajuste · contar pasos por turno · reanudar sin duplicar el ajuste | RF-M3b-04, 05; CA-M3b-13 |
| Constructor de contexto | ¿cambiaron las reglas de la instantánea? (versión posterior, desactivada o nueva regla aplicable) · visibilidad de preferencias por observador | P2, P6 |

Eventos: ajuste enviado; turno iniciado/terminado con tokens y costo (telemetría por turno).

### M3b-6. Impacto funcional por capa
- **Presentación:** detalle de tarea como conversación con cuadro de ajuste, listado con mensajes y última actividad, atajo a nueva tarea, preferencias ajenas ocultas.
- **Negocio:** re-apertura con guardas, pasos por turno, límites, reglas cambiadas, suscripción vigente.
- **Datos:** mensaje de ajuste como parte de la conversación persistida; contador de ajustes y última actividad en la tarea.

### M3b-7. Riesgos y supuestos
- R-M3b-01..04 heredados (costo creciente, reanudación, thinking, confusión con reglas congeladas).
- R-M3b-05 (bajo, nuevo) "Copiar" usa la API del portapapeles del navegador (requiere HTTPS; el portal ya lo usa).
- R-M3b-06 (bajo, nuevo) conversaciones de 21 turnos con pasos: el hilo puede ser largo; pasos plegados mitigan.
- S-M3b-01, S-M3b-02 heredados. D-M3b-1..7 pendientes de validar.

### M3b-8. Plan funcional por etapas (para el arquitecto)
1. Datos y motor: mensaje de ajuste en la conversación, re-apertura con guardas, pasos por turno, reanudación.
2. Detalle como conversación + cuadro de ajuste + refresco en vivo + copiar.
3. Reglas cambiadas, preferencias ajenas ocultas, suscripción vigente.
4. Listado (mensajes, última actividad) + atajo a nueva tarea.

### Historias de usuario M3b
- **HU-M3b-01** Como autor de una tarea, quiero pedirle un ajuste al agente sobre su respuesta, para no empezar de cero ni volver a Claude web. *CA:* CA-M3b-01, CA-M3b-02; Ctrl+Enter envía.
- **HU-M3b-02** Como autor, quiero que el ajuste use el mismo agente, cliente y reglas, para no volver a explicar el contexto. *CA:* CA-M3b-03; aviso de reglas cambiadas con acceso a tarea nueva.
- **HU-M3b-03** Como autor, quiero ver la respuesta del ajuste en vivo. *CA:* CA-M3b-01; burbuja "En cola…" / "Trabajando · paso N".
- **HU-M3b-04** Como autor, quiero que no se pueda mandar otro ajuste mientras el agente trabaja. *CA:* CA-M3b-04.
- **HU-M3b-05** Como autor, quiero saber cuánto lleva gastado la conversación y cuántos ajustes me quedan. *CA:* CA-M3b-06, CA-M3b-07.
- **HU-M3b-06** Como autor, quiero retomar una tarea fallida o cancelada. *CA:* CA-M3b-08; también desde Cancelada (P3).
- **HU-M3b-07** Como autor, quiero copiar una respuesta. *CA:* CA-M3b-10.
- **HU-M3b-08** Como Director, quiero leer la conversación completa de una tarea de mi equipo sin poder intervenir ni ver sus preferencias personales. *CA:* CA-M3b-05; D-M3b-7.
- **HU-M3b-09** Como miembro, quiero ubicar en el listado las tareas con actividad reciente y las que tuvieron ajustes. *CA:* CA-M3b-11; D-M3b-4.
- **HU-M3b-10** Como autor, quiero empezar una tarea nueva con el mismo agente y cliente cuando la conversación llegó al límite o las reglas cambiaron. *CA:* D-M3b-5.
- **Transversal** CA-M3b-12 (tareas viejas), CA-M3b-13 (reinicio a mitad de turno) y CA-M3b-14 (404 entre organizaciones) aplican a HU-M3b-01..06.

---

## Historial de ajustes

### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-09** — 4 bloques (2026-09-14 a 2026-09-14) → [`2-disenador-funcional-2026-09.md`](historial/2-disenador-funcional-2026-09.md)
- **historico** — 3 bloques → [`2-disenador-funcional-historico.md`](historial/2-disenador-funcional-historico.md)
