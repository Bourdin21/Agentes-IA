# Memoria - QA

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-09-14

## Definiciones vigentes

# M4b — Agente configurador de reglas del Director

QA etapa 6 ejecutada el 2026-09-14 sobre `C:\Sistemas\Olvidata Agentes Multi-rubro`, portal local `https://localhost:7200` en Development con **modelo simulado** en 4 arranques (advertencia "Motor de agentes con MODELO SIMULADO … el costo es cero" confirmada en cada uno; `Anthropic__ApiKey` inválida en el proceso; user-secrets sin tocar). Arranques: (1) normal; (2) `MotorAgentes__Habilitado=false` + `Reglas__MaxOrganizacion=100`; (3) `Reglas__MaxOrganizacion=621`; (4) normal. **Costo cero:** 0 menciones a anthropic.com y 0 ERR/FTL en 2.890 líneas de log. Configurador #65 publicado **solo en `olvidata_agentes_dev`** con `evaluar 65 --aprobada "QA M4b: solo desarrollo"` + `publicar 65` después de verificar CA-M4b-11, y **revertido a Borrador** con el UPDATE del implementador (verificado por SQL: `Estado=1`, `PublicadaAt` y `PublicadaPorUserId` NULL). Texto del prompt sin tocar. Estado: **apto con observaciones** (0 defectos funcionales; 1 defecto minor de contraste en tokens del portal reportado como OLV-004, sin auto-fix por ser del design system).

Camino de verificación: servidor MCP `playwright` **no cargado en la sesión** (ToolSearch sin `mcp__playwright__*`); librería Playwright 1.63 desde Node con Chromium headless (navegador real), scripts `m4b-*.js` en el scratchpad (`pw/`), integridad con `mysqlsh`, consola Admin real. Falsos negativos del propio script diagnosticados y descartados: form POST no-AJAX de la Empleada que redirige a AccessDenied (status 0 por `redirect: manual`, igual que CA-M3-02; el POST AJAX sí da 403), rótulos Antes/Después en mayúscula por CSS, columna `ContenidoJson` (no `Contenido`) en dos consultas (re-verificadas por SQL), "Contale" (voseo correcto) y "Fallida" (rótulo visible de estado desde M1) en el barrido de ortografía y rótulos. Ningún PASS sin ejecución.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-09-14
- Sin reglas nuevas desde la corrida M4 del mismo día: `32-estandares-qa-implementador` solo difiere de git en CRM-017..CRM-022 (validados en M4 y re-aplicados abajo); `regresiones-manuales.yml` en OLV-001..003 (validados) y **OLV-004, creado por esta corrida**. PAT-032 no es ítem del yml. Stack 34/35: no aplican.

### Cobertura de criterios de aceptación M4b
| CA | Resultado | Evidencia |
|---|---|---|
| CA-M4b-01 | PASS | Directora A → Configurar conversando → "Somos un estudio contable; nunca prometemos plazos ante ARCA y hablamos formal" con Ctrl+Enter → Tareas/Detalle/29 (Tipo 2). Sin recargar (0 navegaciones): "Te dejé propuestas simuladas.", "Aplicar todas (2)" y 2 tarjetas "Nueva regla" · "Dónde aplica: En toda la empresa" · "Salvo que se indique otra cosa" · título/texto · etiqueta `simulada` / badge "Procedimiento" · "Por qué: …" · Aplicar / Editar y aplicar / Descartar. Encabezado "Configuración de reglas · 14/09/2026 · Por Directora A"; línea "… USD 0,00 en total · 2 propuestas pendientes"; sin "Lo que el agente tuvo en cuenta" ni "Nueva tarea con este agente". Reglas de la org sin cambios (40 → 40); 2 propuestas Pendiente. |
| CA-M4b-02 | PASS | Aplicar → toast "Propuesta aplicada.", badge verde "Aplicada" + "Ver regla" sin recargar; regla 74 `Origen=3` de empresa, 1 evento con `PropuestaReglaId`. Aparece en la grilla de Reglas y en la vista previa de Nueva tarea (inmo-cm) en "De la empresa". |
| CA-M4b-03 | PASS | Editar y aplicar (Nueva, propuesta 22) → `Reglas/Create?propuesta=22` con "Estás aplicando una propuesta del configurador. Revisala, ajustá lo que haga falta y guardá para aplicarla.", título/texto/modo/alcance precargados; Volver y Cancelar → `Tareas/Detalle/29#propuesta-22`. Título vacío → "Ingresá un título." y la propuesta sigue Pendiente (DI-M4b-10). Guardado con "Regla simulada 3-a editada por QA" → vuelve a `#propuesta-22` con "Propuesta aplicada."; regla 77 con el título editado, origen 3 y evento. Cambio (propuesta 28, Director A Dos): `Reglas/Edit/16?propuesta=28` precargado con lo propuesto → "QA M4b cambio editado" v4 → v5, Aplicada. |
| CA-M4b-04 | PASS | Descartar → "Propuesta descartada.", badge gris "Descartada", sin acciones, clase `--descartada`, sin regla creada; encabezado pasa a "0 propuestas pendientes". |
| CA-M4b-05 | PASS | Con `MaxOrganizacion=100`: Aplicar la propuesta 25 → toast y alerta danger "Con esta regla se superan los 100 caracteres de reglas activas de la empresa (quedan 0). Acortala o desactivá otra.", badge rojo "No se pudo aplicar", Reintentar / Editar y aplicar / Descartar, `MotivoFallo` = mensaje, sigue contando como pendiente. Con límite 621: la propuesta 32 falla por límite; tras desactivar la regla 16 (desde otra propuesta), **Reintentar** → "Propuesta aplicada.", badge Aplicada. |
| CA-M4b-06 | PASS | "Revisá mis reglas actuales…" → "Cambio en «QA Tono formal»" (Antes/Después, "(ajustada)") + "Desactivar «Regla simulada 1-a»" (sin Editar y aplicar). Director A Dos edita la regla 16 (v2→v3) → tarjeta con "La regla cambió desde esta propuesta. Al aplicarla vas a poder revisar la versión actual." → Aplicar → modal SweetAlert2 "La regla cambió" · "Esta regla cambió desde la propuesta. Revisá la versión actual antes de aplicar." · Versión actual (con el texto editado) · Propuesta · botones **Aplicar igual / Editar y aplicar / Cancelar**. Cancelar: sin cambios (v3, Pendiente). Editar y aplicar: `Reglas/Edit/16?propuesta=26` con lo propuesto sobre la versión actual, aviso y sin Activar/Desactivar. Aplicar igual: v4 "(ajustada)", Aplicada, evento enlazado. Reintentar de un cambio fallido también abre el modal y "Aplicar igual" lo aplica. |
| CA-M4b-07 | PASS | En "Seguir conversando" (placeholder "Pedile otra regla o que ajuste una propuesta…") "Aplicalo, dale." → nueva respuesta con 2-a/2-b Pendientes; cantidad de reglas y de propuestas Aplicadas sin cambio. |
| CA-M4b-08 | PASS (test + UI) | Tests `ConfiguradorReglasTests` (113/113). En UI: `estructura_empresa` devolvió solo áreas de la org 1; los guiones `reglas_listar` propusieron solo reglas de empresa de la org 1; ninguna propuesta sobre preferencias. |
| CA-M4b-09 | PASS | Empleada: sin botón en Reglas; GET `/ConfiguracionReglas/Nueva` y POST Iniciar de formulario → AccessDenied; POST AJAX AplicarPropuesta / DescartarPropuesta / AplicarTodas → 403; `Reglas/Create?propuesta=` → AccessDenied; conversación y Progreso → 404; propuesta sin cambios. |
| CA-M4b-10 | PASS | Todas válidas: SweetAlert2 "Se van a aplicar 2 propuestas. Las que no se puedan aplicar quedan marcadas con el motivo." → "2 aplicadas.". Parcial por límite (621): "1 aplicada, 1 no se pudo aplicar." (toast warning), la segunda con motivo y Reintentar. Parcial por regla cambiada: el cambio queda "No se pudo aplicar" con "Esta regla cambió desde la propuesta…" y la desactivación se aplica (sin confirmación implícita, DI-M4b-9). |
| CA-M4b-11 | PASS | Con #65 en Borrador: "Configurar conversando" antes de "Nueva regla", deshabilitado con `title="Todavía no está disponible."`; lista con "Nueva conversación" deshabilitado y alerta; Nueva con chips, textarea y "Empezar" deshabilitados y "Todavía no está disponible."; POST Iniciar → mismo mensaje en el resumen, 0 tareas creadas. |
| CA-M4b-12 | PASS | Conversación 29 retomada 3 veces con ajustes; la propuesta 25 de un turno anterior siguió accionable (Director A Dos la ve con Aplicar) y luego falló/quedó reintentable. |
| CA-M4b-13 | PASS | Directora: detalle de regla con "Origen · Propuesta del configurador" + "Ver conversación" e historial "Alta desde el configurador · Ver conversación" (2 enlaces a la tarea 29). Empleada: badge y "desde el configurador" sin ningún enlace. Staff (`Clientes/Regla/1?reglaId=74`): origen con enlace. |
| CA-M4b-14 | PASS | Tareas (Directora y SuperUsuario): filtro "Tipo" Todos · Tareas · Configuración de reglas; con Configuración, 4 filas "Configurador de reglas / Configuración de reglas" con "U$D 0,00"; con Tareas, ninguna; Session repone el filtro. Empleada: sin filtro Tipo y `Listar` con `tipo=ConfiguracionReglas` no devuelve configuraciones. |
| CA-M4b-15 | PASS | Director de la org 4 contra la conversación 29 y la propuesta 25: Detalle, Progreso, `Reglas/Create?propuesta=`, `Reglas/Edit/16?propuesta=26` → 404; AplicarPropuesta ("La propuesta no existe."), DescartarPropuesta, AplicarTodas, EnviarSeguimiento → 404; POST Create con `PropuestaId` ajeno → 404 sin regla; su lista de conversaciones vacía; propuesta intacta. |

### Historias de usuario M4b
| HU | Resultado |
|---|---|
| HU-M4b-01 | cumple (CA-01; chips D-M4b-7: "Cómo hablamos con los clientes" / "Cosas que nunca hacemos" / "Revisá mis reglas actuales" / "Reglas para un área" completan el texto, el segundo se agrega en línea nueva y "Revisá…" reemplaza si está vacío; contador "0 / 10.000", 6 filas, placeholder y hint del diseño; vacío → toast "Contame qué querés configurar."; 10.001 → contador rojo "10.001 / 10.000" y toast "El mensaje admite hasta 10.000 caracteres." (UI y POST); Ctrl+Enter empieza) |
| HU-M4b-02 | cumple (CA-02) |
| HU-M4b-03 | cumple (CA-03, Nueva y Cambio) |
| HU-M4b-04 | cumple (CA-04, sin confirmación) |
| HU-M4b-05 | cumple (CA-10) |
| HU-M4b-06 | cumple (CA-06) |
| HU-M4b-07 | cumple (CA-07) |
| HU-M4b-08 | cumple: lista compartida (Directora A y Director A Dos), otro Director lee, aplica (`ResueltaPorUsuarioId` = dira2) y descarta, sin cuadro ("Solo quien pidió la tarea puede seguir esta conversación.", POST → 403) |
| HU-M4b-09 | cumple (CA-13) |
| HU-M4b-10 | cumple (CA-14) |
| Activar sugerencia | cumple: "¿Hay alguna sugerencia de Olvidata para nosotros?" → "Activar sugerencia «QA M4 Sugerencia tono cordial»", En toda la empresa, Aplicar/Descartar → regla 79 `Origen=3`, `SugerenciaArtefactoId=63`; pestaña Sugerencias "Ya activada" + "Ver la regla" |
| Dos Directores | cumple: A descarta; A Dos sin refrescar aplica → toast "Esta propuesta ya fue resuelta." y la tarjeta pasa a Descartada |
| Autor degradado (RT-M4b-01) | cumple: turno de Director A Dos encolado con el motor apagado, degradada a Empleado por SQL, motor encendido → tarea 31 Fallida con `CierreTurno` "La persona que inició la configuración ya no puede configurar reglas." inmediatamente después del mensaje (sin `LlamadaModelo`), 0 propuestas nuevas; mensaje visible para la Directora. Rol restaurado a Director (verificado). |

### Máquina de estados M4b (propuesta)
| Transición | Resultado |
|---|---|
| — → Pendiente (herramienta del guion; ≤ 10 por paso) | PASS (2 por respuesta, 1 en sugerencia) |
| Pendiente → Aplicada (Aplicar, Editar y aplicar, Aplicar todas; Director autor u otro Director) | PASS |
| Pendiente → Descartada | PASS |
| Pendiente → Fallida (límite; regla cambiada dentro de Aplicar todas) | PASS |
| Fallida → Aplicada (Reintentar tras liberar lugar; Reintentar de cambio con modal + Aplicar igual) | PASS |
| Pendiente + regla cambiada → Aplicar | Modal; Cancelar mantiene Pendiente (PASS) |
| Editar y aplicar con error de formulario | Sigue Pendiente (PASS) |
| Aplicada/Descartada → cualquier acción | "Esta propuesta ya fue resuelta." (PASS) |
| Empleado / staff | 403 (PASS) · otra organización → 404 (PASS) |
| Conversación: autor degradado entre turnos | Turno Fallido sin modelo (PASS) |

### Checklists UI (25/26/32)
- Lista (P-M4b-02): breadcrumb, encabezado y vacío del diseño; columnas Iniciada · Por · Última actividad · Pendientes (badge ámbar) · Aplicadas · Estado · Abrir; orden inicial `[[2,"desc"]]`; filtros Pendientes con/sin, Por, Estado con resultados correctos; Session repone Por + Estado; "Limpiar filtros" no reaparece; búsqueda global por texto del pedido; orden por 5 columnas sin error.
- Tarjetas: 4 tipos con íconos y rótulos llanos, borde/badge por estado, "Aplicar todas (N)" solo con ≥ 2 pendientes, acciones = transiciones válidas (Aplicada: solo "Ver regla"; Descartada: sin acciones; Fallida: Reintentar/Editar y aplicar/Descartar; Desactivar y Activar sugerencia sin Editar y aplicar; staff: solo "Ver regla").
- Formulario de regla con propuesta: aviso info, `PropuestaId`/`PropuestaTareaId`, vuelta a la tarjeta.
- Modal D-M4b-5: textos y 3 botones del diseño.
- Mobile 390px: sin scroll horizontal en Reglas, lista, Nueva, 2 conversaciones, detalle de regla, Tareas y formulario con propuesta; tarjetas dentro del ancho (374 px); cuadro de seguimiento `sticky`. Capturas `m4b-mobile-*`.
- **Contraste** (esperando el fundido, opacidad heredada): todo lo nuevo de M4b cumple en ambos temas — tipo 13,35, "Por qué" 10,63 (oscuro) / 13,08 (claro), alerta de fallo 6,74, aviso de cambio 6,84 / 7,78, badges Aplicada/No se pudo aplicar 4,53, Descartada/modo 4,69. **Bajo 4,5 solo tokens de botones/enlaces del portal → OLV-004 (reportado, sin auto-fix):** `btn-outline-secondary` en oscuro 3,12 (chips, Descartar, Ver regla; 58 usos en el portal), `btn-outline-info` en claro 1,96 ("Abrir"; 10 vistas), `btn-outline-primary`/enlaces de marca en claro 2,70–2,98 ("Configurar conversando", "Editar y aplicar", "Ver conversación"), `btn-primary` 2,98 (OBS-M4-2) y `text-muted` 4,24–4,31 (OBS-M4-3). Capturas `m4b-dark-*`/`m4b-light-*`, medición en `m4b-f5-contraste.json`.
- Ortografía: sin palabras de riesgo sin tilde en 8 pantallas M4b (el barrido marcó "Contale", voseo correcto). Rótulos llanos: sin enums ni códigos (el barrido marcó "Fallida", rótulo visible de estado).
- Consola: sin errores JS ni 5xx en todas las fases (solo 403/404 provocados).

### Regresión
- **Hash (RT-M4b-02):** ajustes sobre #13 (M3b, formato 1), #18 (M4 agente personal, formato 2) y #22 (M4, inmo-cm) → Completada, hash de 64 conservado, `CantidadSeguimientos` +1, último paso `LlamadaModelo`, 0 cierres por contexto alterado. Tarea de trabajo nueva #36 → Tipo 1, hash 64, Completada.
- M4/M3/M3b: vista previa con reglas del configurador en su nivel; reglas por pestaña; conversación M3b con ajustes; sugerencias "Ya activada".
- M2 y portal por rol: todos los links del menú de Laura, Directora A, Empleada, Director B, SuperUsuario y Administrador → 200 + las 5 pestañas de Reglas y Agentes (staff en Reglas → AccessDenied, esperado).
- Build 0 errores / 0 advertencias; tests 113/113 (sin cambios de código en esta corrida).

### Cobertura del catálogo cross-proyecto (M4b)
| id | aplica | resultado | acción |
|---|---|---|---|
| OLV-004 (nuevo) | sí (botones outline y enlaces de marca en pantallas M4b) | FAIL (tokens del portal, previos a M4b) | ítem creado; fix propuesto al implementador/diseño, sin auto-fix |
| OLV-001 | sí (filtros de la lista y Tipo en oscuro) | PASS | — |
| OLV-002 | sí (alertas de tarjeta en oscuro) | PASS (6,74 / 7,78) | — |
| OLV-003 | sí (motivo de falla rojo) | PASS (6,74) | — |
| CRM-002 | sí (acciones por estado y rol, 403/404) | PASS | — |
| CRM-017 | sí (límites de reglas por propuesta) | PASS: aplicar, Aplicar todas, Reintentar y Editar y aplicar pasan por `ReglaService` con el balde | — |
| CRM-020 | sí (feature opcional en Reglas y Tareas) | PASS por lectura y ejecución: Reglas funciona con el configurador sin publicar | — |
| CRM-021 | sí (regla nueva + propuesta + evento en un guardado) | PASS: sin FK en 0, evento enlazado | — |
| CRM-022 | no (sin modo sombra; el simulado solo existe en Development) | N/A | — |
| LIP-001 | sí | PASS (errores del servicio en el resumen de Nueva) | — |
| LP-004 | sí (Session de la lista y de Tipo) | PASS | — |
| CRM-003, MH-015, MH-018 | sí (orden de la lista) | PASS | — |
| DN-001, DN-002, MH-001 | sí (filtros, búsqueda y `pasos` en MySQL) | PASS (sin errores de traducción) | — |
| MH-009, MH-014 | sí (fechas) | PASS (hora argentina) | — |
| KOI-001 | sí (Aplicar todas y modal con SweetAlert2) | PASS | — |
| KOI-009 | parcial | PASS (`Url.Action` en tarjetas y data-urls) | — |
| KOI-011, KOI-014, REG-010, KOI-003/005/006, ELV-001 | sí | PASS (sin links nuevos en el menú; policy RequireDirector) | — |
| Resto del catálogo | no | N/A | Igual que M2..M4. |

### Cobertura de reglas nuevas/modificadas desde la última corrida
Ninguna nueva desde 2026-09-14 (corrida M4). OLV-004 se creó en esta corrida.

### Defectos M4b
- **QA-M4b-01 (minor, OLV-004 nuevo) — reportado, sin auto-fix.** Botones y enlaces con color de Bootstrap/marca sin variante por tema: `btn-outline-secondary` #6c757d sobre #1e293b = 3,12 (oscuro), `btn-outline-info` #0dcaf0 sobre blanco = 1,96 (claro, "Abrir" de la lista), `btn-outline-primary` y enlaces #2b9de4 = 2,70–2,98 (claro). Pasos: tema oscuro → Configurar conversando → Nueva (chips) o conversación (Descartar / Ver regla); tema claro → lista (Abrir) y detalle de regla (Ver conversación). No lo introduce M4b (58/10/18 usos en todo el portal): es decisión del design system; se reporta para corregir en `site.css` con variantes por tema (mismo patrón de OLV-002/003) y, para `btn-primary`/marca, con decisión de Joaquín (OBS-M4-2).

Observaciones (no bloquean):
- OBS-M4b-1 "Ver pasos" (formato M1, `_PasosTurno`) muestra al Director y al staff nombres de herramientas (`estructura_empresa`, `proponer_regla_nueva`) y el JSON de entrada y de resultado. En M4b es más visible porque cada respuesta usa 3–5 herramientas con JSON largo; contradice el criterio de esconder complejidad (D-M3-8..12). Sugerencia al diseñador: rótulos llanos por herramienta o plegar el JSON.
- OBS-M4b-2 En un turno fallido por autor degradado se muestra también "Podés pedirle que siga o reformular el pedido." (texto genérico de M3b): quien lo lee (otro Director) no puede seguir la conversación.
- OBS-M4b-3 El título de una tarjeta de Cambio usa el título vigente de la regla ("Cambio en «QA M4b cambio editado»") mientras "Antes" muestra el título que vio el agente. Correcto como dato; puede confundir en propuestas viejas.
- OBS-M4b-4 El simulador acumula "(ajustada)" si se revisa una regla ya ajustada ("QA Tono formal (ajustada) (ajustada)"): solo guion de desarrollo.
- OBS-M4-2 / OBS-M4-3 siguen (marca 2,98; muted 4,24–4,31).

### Riesgos de liberación M4b
- RT-M4b-04 / S-M4b-01 calidad del prompt y de las herramientas con el modelo real: sin medir (corrida paga PA-02); el configurador queda en Borrador y la función deshabilitada hasta la evaluación de Joaquín.
- R-M4b-02 inyección: mitigada por código (aplicación solo por botón verificada, CA-07); sin prueba con modelo real.
- RT-M4b-03 costo de lectura: los resultados de `estructura_empresa` y `reglas_listar` quedan en el historial (visibles en Ver pasos); medir en la corrida real.
- Carrera real de dos Directores en paralelo: verificada secuencial en UI; concurrencia real cubierta por el implementador con `VersionToken` en MySQL.
- OLV-004: botones poco legibles en ambos temas en todo el portal.

### Estado go/no-go M4b
**Apto con observaciones.** 15/15 CA en PASS (CA-M4b-08 con apoyo de tests), 10 HU + sugerencia, dos Directores y autor degradado cumplen, máquina de estados completa, IDOR sin fugas, regresión de hash OK, 0 defectos funcionales, 1 minor de contraste en tokens del portal (OLV-004, reportado), build 0/0 y tests 113/113, costo cero.

### Casos de prueba acordados M4b (datos que quedaron en dev)
- Configurador **#65 en Borrador** (verificado); en su historial queda la evaluación "QA M4b: solo desarrollo".
- Conversaciones de configuración (todas Completadas salvo #31 Fallida; ninguna Pendiente/EnCurso): #29 (Directora A, 4 turnos), #30 y #34/#35 ("Revisá…", Directora A), #31 (Director A Dos, turno fallido por degradación), #32 (sugerencia), #33 (dos nuevas). Propuestas: 19 en total (ids 18–36): 13 Aplicadas, 3 Descartadas, 2 Pendientes (cambio y desactivación de #35) y 1 Fallida por límite (propuesta 25).
- Reglas de la org 1 creadas o cambiadas por el configurador: 74 (inactiva), 75–78, 80, 81 "Regla simulada …", 79 "QA M4 Sugerencia tono cordial (ajustada)" (sugerencia activada por el configurador, v3). **Regla 16 "QA Tono formal" (dato M3) quedó como "QA M4b cambio editado" v5 inactiva**; **regla 64 (sugerida en Marketing, dato M4) dada de baja lógica** para liberar la sugerencia (79 la reemplaza como "Ya activada"). Reglas 13 y 65 de la org 4: baja temporal y restauradas (verificado).
- Roles restaurados: Director A Dos = Director (verificado). Tarea de trabajo #36 (Directora, inmo-cm) y ajustes de regresión en #13, #18, #22.
- Scripts: `m4b-f1.js` (CA-11, Empleada), `m4b-f2.js` (flujo del Director, otro Director, carrera), `m4b-f3.js` (cambio/modal, sugerencia, lista, Tipo, permisos, IDOR, staff, invitación), `m4b-f4a.js` (preparación), `m4b-f4b.js` (sin motor, límite 100), `m4b-f4c.js` (autor degradado, aplicar todas parcial, Reintentar), `m4b-f5.js` (mobile, contraste, ortografía), `m4b-f6.js` (hash y menú); `m4b-ids.json`; logs `portal-m4b*.log`.

---

# M4 — Agentes de la organización

QA etapa 6 ejecutada el 2026-09-14 sobre `C:\Sistemas\Olvidata Agentes Multi-rubro`, portal local `https://localhost:7200` en Development con **modelo simulado** (`Anthropic__Simulado=true`; advertencia "Motor de agentes con MODELO SIMULADO … no se llama a Anthropic y el costo es cero" confirmada al arrancar; `Anthropic__ApiKey` con clave inválida en el proceso como resguardo, sin tocar user-secrets), base `olvidata_agentes_dev`. **Costo cero:** 0 llamadas a anthropic.com en 3.857 líneas de log, 0 ERR/FTL. Alcance: M4 **sin revisión del Director** (ajuste del gate: RF-M4-06/07, CA-M4-03, HU-M4-03/04, P-M4-04/05 pospuestos). Estado: **apto con observaciones** (1 defecto minor corregido por auto-fix).

Camino de verificación: servidor MCP `playwright` **no cargado en la sesión** (ToolSearch sin `mcp__playwright__*`); librería Playwright 1.63 desde Node con Chromium headless (navegador real), scripts `m4-*.js` en el scratchpad (`pw/`), integridad con `mysqlsh`, consola Admin real para importar/publicar/sincronizar. Cada FAIL de script se diagnosticó antes de reportar: 16 falsos negativos del propio script (etiquetas en mayúscula por CSS, `<details>` cerrados, Directora "Usuario Demo" también destinataria, `CambiarEstado` con `activar` y no `activa`, selector de casilla que tomaba "Puestos", SweetAlert pendiente de TempData tapando el formulario, colación de MySQL sin mayúsculas en `Nombre='cm del estudio'`, fundido `fadeIn` 250 ms que daba contraste 1) re-verificados con scripts `m4-f2b`, `m4-f3b`, `m4-f3c`, `m4-f4b` o diagnósticos `m4-diag1..3`; 1 defecto real (contraste, OLV-003). Ningún PASS sin ejecución.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-09-14
- Sin reglas nuevas desde la corrida M3b del mismo día: `32-estandares-qa-implementador` sin cambios desde 2026-09-13 (validado en M2); `regresiones-manuales.yml` solo difiere en OLV-001/OLV-002 (validados) y **OLV-003, creado por esta corrida**. Stack 34/35: no aplican.

### Datos de prueba de núcleo creados (identificados "QA")
- Rubro **`qa-m4` "QA M4 Rubro de prueba"** importado desde `scratchpad/qa-m4-rubro/rubro.yml` (raíz en el scratchpad, sin contenido real): agente base `qa-m4-redactor` (herramienta `fecha_hora_actual`) **publicado**, sugerencia `qa-m4-sug-tono` "QA M4 Sugerencia tono cordial" **publicada** y `qa-m4-sug-borrador` en **Borrador**; publicación con `publicar-rubro qa-m4 --aprobacion-manual "QA M4: datos de prueba, sin contenido real"`. `incluido_siempre` quedó en **0** al cerrar (se usó en 1 para CA-M4-12). No se publicaron reglas de plataforma ni contenido de rubros reales.

### Cobertura de criterios de aceptación M4
| CA | Resultado | Evidencia |
|---|---|---|
| CA-M4-01 | PASS | Laura: ⋮ "Crear mi versión" de inmo-cm → formulario con base precargada, "0 / 8.000", "Guardar y usar" → "Agente listo para usar." y Nueva tarea "Mis mails formales · basado en inmo-cm". Vista previa con cliente: … "De Panadería Norte" → **"Instrucciones de Mis mails formales"** → "De la empresa para este agente" → "De tu área «Marketing»". Tarea #18: "Tarea #18 · Mis mails formales (versión 1)", "Basado en inmo-cm", instrucciones v1 en "Lo que el agente tuvo en cuenta", `AgenteOrganizacionVersionId=11`, hash 64; ajuste M3b completado. Martín, la Directora y Director B: sin card y 11 accesos (Detalle, Ejecutar, Editar, Crear?desde, VistaPrevia, Archivar, Reactivar, Duplicar, POST Editar, POST tarea) → 404. |
| CA-M4-02 | PASS | Laura publica "CM del estudio" (Toda la empresa, Marketing) → "Agente publicado para toda la empresa."; aviso "Laura Marketing publicó «CM del estudio» para toda la empresa." con `/Agentes/Detalle/13` a los 3 Directores activos de la org 1 (Directora A, Director A Dos, Usuario Demo), no a la autora ni a la org B; Laura lo ve en "De tu área «Marketing»" con badge de área, Martín y la Directora en "De la empresa". |
| CA-M4-03 | Pospuesto | Ajuste del gate (sin propuestas ni revisión). Verificado lo que lo reemplaza: cualquier miembro publica y se avisa a Directores; el formulario no muestra "lo revisa el Director". |
| CA-M4-04 | PASS | POST con `Herramientas=fecha_hora_actual` sobre inmo-cm (alta) y `borrar_todo` (edición) → "Esa herramienta no está disponible en el agente de Olvidata elegido.", 0 filas / versiones sin cambio. Con el base QA la casilla "Fecha hora actual" se guarda y se muestra. |
| CA-M4-05 | PASS | Borrador → card "Borrador (versión 2)" para autora y Directora, no para Martín; badge "Borrador pendiente" solo a quien edita; vista previa sigue en v1; publicar → historial v2 Publicada / v1 Reemplazada y aviso "actualizó"; tarea #19 sigue "(versión 1)" con texto v1, #20 "(versión 2)"; la Directora publica v3 (autor "Directora A"). Publicar sin cambios → "Datos guardados. Las instrucciones no cambiaron: el agente sigue en la versión 2.". Dos pestañas → "Otra persona modificó este agente mientras lo editabas. Revisá la versión actual y volvé a guardar.", borrador de la pestaña 1 intacto y texto de la 2 conservado. |
| CA-M4-06 | PASS | Un fragmento del contenido publicado de inmo-cm no aparece en Detalle, Ejecutar, Editar, Crear, detalle de tarea ni VistaPrevia (HTML completo). |
| CA-M4-07 | PASS | Regla "QA M4 regla solo CM del estudio" creada desde la card del detalle (`agenteRef=o13` precargado): pestaña "Por agente" con el nombre, card "Reglas de este agente"; en la vista previa de CM del estudio aparece después de "QA CM hashtags" (regla del base, P3) y no aparece en inmo-cm ni en "Mis mails formales" (que sí reciben la del base). POST de regla para el agente personal → "Ese agente no admite reglas…". Combo: "De Olvidata · Inmobiliario" y "De la empresa: CM del estudio" (sin personales). |
| CA-M4-08 | PASS | La Directora archiva desde el detalle con "¿Archivar «CM del estudio»? Deja de aparecer para pedir tareas nuevas; las tareas y conversaciones existentes siguen disponibles." → "Agente archivado."; fuera de "De la empresa"; sección **"Archivados (N)"** plegada con nota y Reactivar para autora y Directora; Martín solo ve sus archivados. GET Ejecutar → detalle con "Este agente está archivado. Reactivalo para pedirle tareas nuevas."; POST sin tarea; Editar → "Reactivalo para editarlo". Tarea #21: "Agente archivado", sin "Nueva tarea con este agente", ajuste completado (P11). Reactivar desde Archivados con confirmación → "Agente reactivado." con su v3. Nombre liberado al archivar; reactivar con el nombre tomado → "Ya hay un agente activo con ese nombre en tu empresa. Cambiale el nombre…". |
| CA-M4-09 | PASS | Sin licencia de Inmobiliario (SQL temporal, restaurada): card atenuada con "Este agente no está disponible: la suscripción a Inmobiliario no está vigente.", sin Usar ni Duplicar; "De Olvidata · Inmobiliario" desaparece; Ejecutar → detalle con el motivo, POST sin tarea; detalle con badge "No disponible"; Editar con aviso "…Podés guardar un borrador; para publicar tiene que estar disponible.", borrador OK y publicar rechazado; ajuste de #21 → "Tu organización no tiene la suscripción vigente para este agente." (POST y alerta). |
| CA-M4-10 | PASS | Nombre repetido ("cm del estudio", "CM DEL ESTUDIO", "CM del estúdio", con espacios) → "Ya hay un agente activo con ese nombre en tu empresa.". 8.001 caracteres → contador "8.001 / 8.000" en rojo y "Las instrucciones admiten hasta 8.000 caracteres." (UI y POST); 8.000 con CRLF normalizado se guarda. 10 personales: alta por formulario, duplicar, reactivar y pasar un agente de la empresa a personal → "Llegaste al máximo de 10 agentes personales. Archivá alguno para crear otro.". 50 activos: alta y duplicar → "Tu empresa llegó al máximo de 50 agentes activos. Archivá alguno para crear otro."; la org B sigue creando. (Reactivar con 50 activos no se re-ejecutó por un error del script; mismo camino de código que el caso de personales, que sí se verificó.) 44 agentes "QA M4 Lim…" archivados al terminar. |
| CA-M4-11 | PASS | ⋮ Duplicar → "¿Crear una copia personal de «CM del estudio»? …" → "Copia creada como borrador." → Editar de "Copia de CM del estudio" (personal, Borrador, sin publicar, mismas instrucciones); segunda copia "Copia de CM del estudio (2)". "Crear mi versión" de Martín → formulario "CM del estudio (mi versión)" sin guardar. Si Olvidata quita la herramienta del base, la copia no la conserva. |
| CA-M4-12 | PASS | Núcleo IP → "QA M4 Rubro de prueba" con badge "Incluido en todas las suscripciones" (inmobiliario sin badge). Alta de licencia (org B): casilla tildada y deshabilitada "Se incluye en todas las suscripciones.", plataforma no figura; enviada solo Inmobiliario → licencia 4 con `inmobiliario,qa-m4`. `sincronizar-rubros-incluidos`: "Se agregaron 1 rubros incluidos a 1 licencias vigentes." (licencia 1: 1 → 1,6); segunda corrida 0; con plataforma marcada a mano, 0 y revertido. |
| CA-M4-13 | PASS | Sin licencia del rubro: "Todavía no hay sugerencias de Olvidata para tus rubros.". Con licencia: grupo "QA M4 Rubro de prueba", card con etiquetas `tono`, `qa` y acciones; la de borrador no se ve y su POST → 404. Modal "Activar en un área": "Elegí el área." sin área, "Salvo que se indique otra cosa" por defecto, Select2 dentro del modal con foco en el buscador → regla 64 del área Marketing, modo PorDefecto, origen Sugerida, texto y etiquetas copiados; "Ya activada" + "Ver la regla"; detalle "Origen: Sugerida por Olvidata"; entra en la vista previa de Laura; segunda activación → "Esa sugerencia ya está activada en tu empresa.". Org B: "Activar en la empresa" con "Siempre" → "Regla activada." (regla 65). Empleada: sin pestaña, POST → 403. |
| CA-M4-14 | PASS | SuperUsuario y Administrador: botón "Agentes" en la organización, grilla "Solo lectura… Incluye los personales de cada miembro." con 8 de 8; filtros por las 5 columnas (Select2), búsqueda global por rótulos ("Toda la empresa", "Borrador"), orden asc/desc de 5 columnas, Session repone el filtro y "Limpiar filtros" no reaparece; detalle con instrucciones y borrador, solo "Volver". Director → AccessDenied / POST 403; staff en /Agentes con aviso, sin crear (AccessDenied) ni archivar (403). |
| CA-M4-15 | PASS | A→B y B→A (Directora, Laura, Director B contra CM del estudio y "QA M4 agente org B"): 10 accesos GET/POST cada uno → 404, sin catálogo ni vista previa; regla por agente con `o<id>` ajeno → rechazada; regla por agente, regla sugerida y tarea de la org A → 404 para B; filtro de Tareas de B sin agentes de A; staff con organización equivocada → 404; activar sugerencia con un área de la org A → "El área elegida no existe."; 0 reglas/tareas/agentes basura. |

### Historias de usuario M4
| HU | Resultado |
|---|---|
| HU-M4-01 | cumple (CA-M4-01/04/06) |
| HU-M4-02 | cumple (CA-M4-02; aviso a Directores por el ajuste del gate) |
| HU-M4-03 / HU-M4-04 | pospuestas (ajuste del gate) |
| HU-M4-05 | cumple (CA-M4-05; la edición de la empresa por creador y Director publica directo) |
| HU-M4-06 | cumple (secciones De tu área · De la empresa · Mis agentes · De Olvidata por rubro · Archivados; buscador por nombre/descripción sin tildes ni mayúsculas con "No hay agentes que coincidan con la búsqueda."; estado vacío de "Mis agentes") |
| HU-M4-07 | cumple (grupo "Instrucciones de…" en vista previa y detalle de tarea) |
| HU-M4-08 | cumple (CA-M4-07) |
| HU-M4-09 | cumple (CA-M4-08; cada miembro archiva/reactiva los suyos; otro Empleado → 403) |
| HU-M4-10 | cumple (CA-M4-11) |
| HU-M4-11 | cumple (CA-M4-09) |
| HU-M4-12 | cumple (CA-M4-13) |
| HU-M4-13 | cumple (CA-M4-12) |
| HU-M4-14 | cumple (CA-M4-14) |

### Máquina de estados M4 (versión y agente)
| Transición | Resultado |
|---|---|
| — → Borrador (Guardar borrador) | PASS ("Agente guardado como borrador."; lo nunca publicado solo lo ve su creador) |
| — / Borrador → Publicada personal (Guardar y usar) | PASS (lleva a Nueva tarea) |
| — / Borrador → Publicada empresa (Publicar para la empresa, Empleado o Director) | PASS (aviso a Directores "publicó"/"actualizó") |
| Publicada → Borrador N+1 (editar) → Publicada N+1, anterior Reemplazada | PASS |
| Guardar/publicar igual a lo publicado | Sin versión nueva y borrador descartado (PASS) |
| Botón que no corresponde a "Quién lo usa" | Rechazado "El botón elegido no corresponde a «Quién lo usa»…" (PASS) |
| Director deja "Solo yo" un agente ajeno | Rechazado "Solo quien creó el agente puede dejarlo para uso personal." (PASS) |
| Edición simultánea | Conflicto sin pisar (PASS) |
| Activo → Archivado (Director cualquiera de la empresa; creador los suyos) | PASS; otro Empleado → 403 |
| Archivado → Activo | PASS; con nombre tomado o en límite → rechazado con mensaje |
| Archivado + editar / tarea nueva | Rechazado (PASS); ajuste de tarea existente permitido (P11, PASS) |
| Activo → "No disponible" derivado (sin licencia del rubro) | PASS: borrador sí, publicar/usar/ajustar no |
| Regla por agente de un archivado | "No se aplica" (derivado); desactivar OK; activar → "No se puede activar: el agente de la empresa fue archivado." (PASS) |
| Cualquier acción sobre agente ajeno (personal de otro, otra organización) | 404 (PASS) |

### Checklists UI (25/26/32)
- Catálogo: cards `col-md-6 col-xl-4`, badges llanos (De Olvidata / De la empresa / Personal / área / "Basado en …" / Borrador / Archivado / "Borrador pendiente"), menú ⋮ con acciones = permisos reales (Martín: Crear mi versión · Ver · Usar; autora y Directora: Ver · Editar · Duplicar · Archivar; Directora además Crear mi versión); "Seguir editando" en borradores.
- Formulario: cards en el orden de D-M4-1, Select2 en base y área, casillas de herramientas rearmadas al cambiar de base, contador con separador de miles y rojo al superar, barra sticky con "Guardar y usar"/"Publicar para la empresa" según "Quién lo usa" + "Guardar borrador" + Cancelar; en edición "Publicar crea la versión N. Las tareas anteriores no cambian." y Archivar; aviso de borrador y de no disponible; resumen de validación con los mensajes del service (LIP-001). Rótulos de P-M4-02 presentes y sin "lo revisa el Director".
- Detalle: `ov-detail-grid` con vacíos explícitos ("Sin área destacada", "Sin herramientas", "Sin publicar"), card de borrador, historial con "Ver instrucciones", card "Reglas de este agente".
- Grilla de staff: DataTables server-side sin 500, filtro por cada columna con Select2, búsqueda global por rótulos, Session, "Limpiar filtros", orden de las 5 columnas.
- Modal de sugerencias: Select2 con `dropdownParent` y foco en el buscador, cruz visible en oscuro (`invert`), modo por defecto; "Elegí el área." sin área.
- Mobile 390px: sin scroll horizontal en 10 pantallas (catálogo, crear, editar, detalle, nueva tarea, detalle de tarea, sugerencias, reglas por agente, staff y detalle de staff); barra de Editar sticky al pie (bottom 844 = viewport); menú ⋮ dentro del viewport (198–358 px); buscador OK. Capturas `m4-mobile-*`.
- **Contraste** (61 elementos por tema, esperando el fin del `fadeIn`): tema oscuro OK en textos de cards, badges neutros (13,35), etiquetas `bg-light` (13,35), Select2 del modal (13,35), alertas (9,65), hints (5,71). **Defecto QA-M4-01 (OLV-003) corregido:** "Archivar" rojo del menú en oscuro 3,23 → 7,71; motivo "No disponible" en claro 2,69 → 6,47 (en oscuro 4,70 → 7,71). Quedan bajo 4,5 solo tokens previos del theme (ver observaciones). Capturas `m4-dark-*`/`m4-light-*`.
- Ortografía: sin palabras de riesgo sin tilde en 16 pantallas M4 (miembros, Directora, staff; excluido el contenido de artefactos del núcleo). Rótulos llanos: sin enums, tokens ni nombres de acciones visibles.
- Consola: sin errores JS ni 5xx en todas las fases (solo 403/404 provocados); log sin ERR/FTL.

### Regresión
- **RT-M4-01 (hash):** ajustes sobre #13 y #15 (M3b con instantánea formato 1) y #3 (M2 sin instantánea) → Completada con el mismo `HashContexto`, sin error, contador +1; tarea nueva #22 con inmo-cm → formato 1 (sin agente de la empresa), hash 64, completada. Tests 100/100 incluyen el golden.
- M3b: conversación de #14 visible (8 respuestas) para Directora y Laura; ajustes con agente de la empresa, personal y archivado; D-M3b-1 con agente de la empresa.
- M3: vista previa por niveles con el grupo nuevo en su lugar; reglas por agente del base aplican a derivados; "No se aplica" por archivado; sugerida en el contexto del área.
- M2 y portal por rol: todos los links del menú de Directora A, Laura, SuperUsuario, Administrador y Director B → 200 (Inicio, Agentes, Tareas, Cartera, Reglas, Miembros, Áreas, Notificaciones, Clientes, Núcleo, Uso, Auditoría, Usuarios, LoginAudit, Sistema) + pantallas puntuales (Reglas por pestaña y alta, Áreas/Create, Clientes/Details y Reglas de la org 1); Laura sigue con AccessDenied en Áreas y Miembros.
- Build 0 errores / 0 advertencias; tests 100/100 antes y después del auto-fix.

### Cobertura del catálogo cross-proyecto (M4)
| id | aplica | resultado | acción |
|---|---|---|---|
| OLV-003 (nuevo) | sí (menú ⋮ en oscuro y motivo de card atenuada) | FAIL → PASS post-fix | ítem creado + auto-fix `site.css` |
| OLV-002 | sí (alertas de edición, detalle y tarea en oscuro) | PASS (9,65) | — |
| OLV-001 | sí (Select2 del formulario, filtros de staff y modal en oscuro) | PASS (13,35) | — |
| CRM-002 | sí (acciones ocultas sin permiso + 403/404) | PASS | — |
| CRM-017 | sí (topes 10/50 en todos los caminos) | PASS: alta, duplicar, reactivar y pasar a personal controlan el tope | — |
| CRM-020 | sí (aviso a Directores) | PASS por lectura: `AvisarDirectoresAsync` envuelto; publicación no se revierte (no reproducible sin forzar fallo) | — |
| CRM-021 | sí (agente y versión nuevos) | PASS: alta publicada con transacción de dos guardados, sin FK en 0 | — |
| LIP-001 | sí | PASS (errores del service en el resumen) | — |
| LP-002 | sí (agente derivado en tareas) | PASS (columna, filtro `o<id>`, búsqueda global, detalle, reglas) | — |
| LP-004 | sí (Session de la grilla de staff) | PASS | — |
| REG-010, KOI-003, KOI-005, KOI-006, ELV-001 | sí (policies de Agentes, Clientes/Agentes) | PASS (sin links nuevos; staff y miembros con la autorización correcta) | — |
| CRM-003, MH-015, MH-018 | sí (orden de la grilla de staff) | PASS | — |
| DN-001, DN-002, MH-001 | sí (catálogo, staff, filtros de tareas/reglas) | PASS (sin 500 ni errores de traducción) | — |
| MH-009, MH-014 | sí (fechas de versiones, creado, archivado) | PASS (hora argentina) | — |
| KOI-001 | sí (archivar/duplicar/reactivar con SweetAlert) | PASS | — |
| KOI-009 | parcial | PASS en URLs nuevas (`Url.Action`); el aviso guarda `/Agentes/Detalle/{id}` relativo (DI-M4-13) | observación si se hostea en subdirectorio |
| KOI-011, KOI-014 | sí (escrituras con auditoría; estados vacíos) | PASS | — |
| KOI-013 | no (casillas de herramientas sin hidden) | N/A | — |
| CRM-018, CRM-022 | no | N/A | — |
| Resto del catálogo | no | N/A | Igual que M2/M3/M3b. |

### Cobertura de reglas nuevas/modificadas desde la última corrida
Ninguna nueva desde 2026-09-14 (corrida M3b). OLV-003 se creó en esta corrida y quedó validado.

### Defectos M4
- **QA-M4-01 (minor, OLV-003 nuevo) — corregido.** (a) Tema oscuro: "Archivar" del menú ⋮ (y "Cerrar sesión" del topbar) `text-danger` #dc3545 sobre #1e293b = 3,23. (b) Tema claro: el motivo "Este agente no está disponible: la suscripción a … no está vigente." en #ef4444 con la opacity .72 heredada de `.ov-card-atenuada` = 2,69 (lo que explica por qué no se puede usar era lo menos legible). Pasos: tema oscuro → Agentes → ⋮ de un agente propio; tema claro → quitar la licencia del rubro → Agentes. Fix en `src/OlvidataAgentes.Web/wwwroot/css/site.css`: la opacity pasa a nombre, badges y descripción de la card; motivo en #b91c1c (claro) / #fca5a5 (oscuro) con opacidad plena; `[data-theme="dark"] .dropdown-item.text-danger { color: #fca5a5 !important; }`. Post-fix: 7,71 / 6,47 / 7,71; card sigue atenuada; build 0/0 y tests 100/100.

Observaciones (no bloquean):
- OBS-M4-1 **Sección "Archivados" (DI-M4-7): clara.** Plegada al final con contador, nota "No aparecen para pedir tareas nuevas. Sus tareas y conversaciones siguen disponibles.", badge "Archivado" y "Reactivar"; solo la ve quien puede reactivar. Sin ella un archivado no tendría camino de vuelta. Sugerencia menor: el menú ⋮ de una card archivada ofrece "Duplicar" (permitido por DI-M4-8, no listado en el diseño). Recomiendo confirmarla con Joaquín como parte del diseño.
- OBS-M4-2 Badge de marca `bg-primary` (blanco sobre #2b9de4) = 2,98 en ambos temas ("De la empresa", "Incluido en todas las suscripciones") y opción seleccionada de Select2 en oscuro (estilo de OLV-001) = 2,98. Token del design system usado en todo el portal; decisión de marca, no de M4.
- OBS-M4-3 Tema claro: `text-muted` sobre el fondo de página = 4,24 (subtítulo de rubro, nota de Archivados, "· basado en …", descripción de sugerencias) y `.ov-detail-item__value--empty` = 2,56 (M2). Tokens previos del theme (misma familia que OBS-M3b-2).
- OBS-M4-4 POST de Editar sin `BaseArtefactoId` (campo oculto requerido) vuelve al formulario sin ningún mensaje. Solo con request manipulado; la UI siempre lo envía.
- OBS-M4-5 Cuando la Directora edita un agente de la empresa creado por un Empleado, el aviso va a los otros Directores pero la autora no se entera (el diseño solo pide avisar a Directores).
- OBS-M4-6 Los agentes base siguen mostrándose por slug ("Basado en inmo-cm", "qa-m4-redactor"): OBS-M3-2 (dato del núcleo).
- OBS-M4-7 La intersección de herramientas al ejecutar (RF-M4-02) no es observable con el modelo simulado; cubierta por test y por la copia sin la herramienta quitada.

### Riesgos de liberación M4
- R-M4-01 inyección por instrucciones del cliente: escape y nivel verificados en UI; obediencia real del modelo sin corrida paga (PA-02).
- RT-M4-03 publicación sin revisión: mitigada con aviso a Directores y archivo; la autora no se entera de cambios del Director (OBS-M4-5).
- Instrucciones del derivado fuera del bloque cacheado: costo por tarea sin medir (corrida real pendiente).
- Aviso con URL relativa (KOI-009) si el portal se publica bajo subdirectorio.
- Carreras aceptadas en límites y activación de sugerencias (no probadas en paralelo).

### Estado go/no-go M4
**Apto con observaciones.** 14/14 CA aplicables en PASS (CA-M4-03 pospuesto por el gate), 12 HU cumplen (HU-M4-03/04 pospuestas), máquina de estados completa, IDOR sin fugas, regresión del hash OK, 1 defecto minor corregido por auto-fix (OLV-003), build 0/0 y tests 100/100.

### Casos de prueba acordados M4 (datos que quedaron en dev)
- Org 1: "Mis mails formales" (12, personal de Laura, v1) · "CM del estudio" (13, empresa, Marketing, v3 publicada por la Directora) · "QA M4 8000 exactos" (14, borrador) · "cm del estudio" (15, borrador de Martín, archivado) · "Copia de CM del estudio" (16) y "(2)" (17, Martín) en borrador · "QA M4 con herramienta" (18, base qa-m4-redactor) y su copia (19) · 45 "QA M4 Lim…" archivados (incluido 1 de la org B). Org 4: "QA M4 agente org B" (20, empresa).
- Tareas #18 (Mis mails formales, 1 ajuste), #19/#20 (Martín, CM v1/v2), #21 (Laura, CM v3, 1 ajuste con el agente archivado), #22 (Directora, inmo-cm); ajustes de regresión en #3, #13, #15. Ninguna Pendiente/EnCurso (verificado por SQL).
- Reglas: 63 "QA M4 regla solo CM del estudio" (activa), 64 sugerida en Marketing (org 1), 65 sugerida en la empresa (org 4). 8 avisos "Agente para toda la empresa".
- Licencias: 1 "Suscripcion piloto" con inmobiliario + qa-m4 (por la sincronización); 4 "QA M4 licencia org B" con inmobiliario + qa-m4 (emitida por backoffice). Rubro `qa-m4` con `IncluidoSiempre=0`.
- Scripts: `m4lib.js`, `m4-f1.js` (catálogo, personal, privacidad, publicar, validaciones), `m4-f2.js` + `m4-f2b.js` (versiones, conflicto, permisos, reglas, archivar, P11, duplicar, filtro de tareas), `m4-f3.js` (sugerencias, rubro incluido, herramientas, suscripción vencida), `m4-f3b.js` (licencia org B, IDOR, staff, hash), `m4-f3c.js` (límites), `m4-f4.js` + `m4-f4b.js` (mobile, ortografía, rótulos, regresión, contraste), `m4-diag1..3.js`; manifiesto `scratchpad/qa-m4-rubro/`.

---

# M3b — Seguir conversando sobre una tarea

QA etapa 6 ejecutada el 2026-09-14 sobre `C:\Sistemas\Olvidata Agentes Multi-rubro`, portal local `https://localhost:7200` en Development con **modelo simulado** (`Anthropic__Simulado=true`, advertencia "Motor de agentes con MODELO SIMULADO" confirmada en cada arranque; además `Anthropic__ApiKey` apuntada a una clave inválida en el proceso como resguardo, sin tocar user-secrets), base `olvidata_agentes_dev`. **Costo cero, sin llamadas a Anthropic.** Estado: **apto con observaciones** (1 defecto minor corregido por auto-fix).

Camino de verificación: servidor MCP `playwright` **no cargado en la sesión** (ToolSearch sin `mcp__playwright__*`); librería Playwright 1.63 desde Node con Chromium headless (navegador real), scripts `m3b-*.js` en el scratchpad de la sesión (`pw/`), integridad con `mysqlsh`. Cada FAIL de script se diagnosticó: 6 falsos negativos del propio script (acentos escapados en JSON, `\r\n` del portapapeles de Windows, encabezados en mayúscula por CSS, `aoColumns.mData`, valores de opción `pedido`/`ajustes`, texto de ajuste repetido en dos cortes) re-verificados con evidencia o re-ejecutados (`m3b-f3b-listado.js`); 1 defecto real (tema oscuro). Ningún PASS sin ejecución.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-09-14
- Sin reglas nuevas desde la corrida M3 del mismo día: `32-estandares-qa-implementador` sin cambios desde 2026-09-13 (ya validado en M2/M3); `regresiones-manuales.yml` solo suma OLV-002, creado por esta corrida. Stack 34/35: no aplican.

### Cobertura de criterios de aceptación M3b
| CA | Resultado | Evidencia |
|---|---|---|
| CA-M3b-01 | PASS | Tarea #14 (Laura, CM, Panadería Norte): "Trabajando · paso 1 de hasta 25" → "Respuesta simulada al turno 1." sin recargar; cuadro "Seguir conversando", placeholder del diseño, "0 / 10.000", "Quedan 20 ajustes…". Ctrl+Enter: burbuja "Ajuste" + "En cola…", textarea limpio y deshabilitado, 0 navegaciones; respuesta del turno 2 en 2,5 s por SignalR (websocket al hub) con scroll al último mensaje. |
| CA-M3b-02 | PASS (UI + test) | La respuesta simulada del turno 2 cita el ajuste con su salto de línea y numera el turno por la cantidad de mensajes de la persona que recibió el modelo (pedido + ajuste). Contenido completo de la conversación: `ConversacionTests`. |
| CA-M3b-03 | PASS | Directora desactiva la regla 16 (en la instantánea): Laura ve el aviso; el ajuste siguiente se completa con `HashContexto` idéntico (instantánea intacta). Directora no ve el aviso (solo el autor). |
| CA-M3b-04 | PASS | Con turno activo: textarea y botón deshabilitados, placeholder "Esperá la respuesta para seguir."; POST forzado → `{"success":false,"message":"La tarea todavía está trabajando. Esperá la respuesta para seguir."}` sin crear ajuste (1 en base). |
| CA-M3b-05 | PASS | Directora A en #14: conversación completa, "Pedida por Laura Marketing", sin cuadro, nota "Solo quien pidió la tarea puede seguir esta conversación."; POST → 403 con ese mensaje; Progreso 200 sin cuadro. |
| CA-M3b-06 | PASS | Vacío y solo espacios → toast "Escribí tu mensaje." (UI y POST). 10.001 caracteres → contador "10.001 / 10.000" en rojo, toast "El mensaje admite hasta 10.000 caracteres.", texto conservado; POST con 10.001 y con `\r\n` normalizado rechazados. 19 ajustes → "Queda 1 ajuste en esta conversación."; 20 → `ov-alert warning` "Esta conversación llegó al máximo de 20 ajustes." + "Nueva tarea con este agente" (precarga inmo-cm + cliente 41), sin cuadro; POST → "…Empezá una tarea nueva."; contador sin cambios. |
| CA-M3b-07 | PASS (con datos sembrados) | El modelo simulado informa 0 tokens: se sembró 1.000/234 tokens y USD 0,1234 en #14, se envió un ajuste y el detalle siguió en "1.234 tokens · USD 0,1234 en total" y el listado en "U$D 0,1234" (acumula, no reinicia). Suma con tokens reales: tests + corrida paga pendiente. Valores restaurados a 0. |
| CA-M3b-08 | PASS | `MaxPasos=0` en #14 → turno Fallida con `ov-alert danger` "Se alcanzó el máximo de 0 pasos sin terminar la respuesta." + "Podés pedirle que siga o reformular el pedido." dentro de su turno; turnos previos visibles; cuadro disponible; `CierreTurno` registrado. Con `MaxPasos=25` un nuevo ajuste se completa y el error queda en su turno. |
| CA-M3b-09 | PASS | "Ver pasos (1)" como `<details>` cerrado dentro de cada respuesta. |
| CA-M3b-10 | PASS | "Copiar" → toast "Respuesta copiada."; el portapapeles contiene el texto de la respuesta (idéntico salvo `\r\n` de Windows). |
| CA-M3b-11 | PASS | Columnas "Última actividad" y "Mensajes"; orden inicial `[[7,"desc"]]` = Última actividad desc (D-M3b-4); filtro Mensajes Select2 con foco en el buscador: Con ajustes 5 (todas >1), Solo el pedido 4 (todas =1); daterangepicker (hoy 8, 01–13/09 1); Session repone "Con ajustes" y "Limpiar filtros" no reaparece; búsqueda global por "11" (mensajes) y por fecha; orden asc/desc por Mensajes y Última actividad; "11 mensajes" del detalle = columna. Empleada: solo sus 4 tareas sin "Pedida por"; staff: las 10. |
| CA-M3b-12 | PASS | #3 (Empleado A, M2, sin instantánea, sin pasos) admite ajuste y responde. #4 (Directora, Cancelada vieja): el ajuste agrega 1 `CierreTurno`, turno 1 muestra "Se canceló esta respuesta." y responde. |
| CA-M3b-13 | PASS | #15: ajuste enviado y portal matado a los 2 s con la tarea **EnCurso** (lease hasta 20:51:11 UTC, último paso = MensajeUsuario 6, sin respuesta). Al relevantar, el worker la retomó al vencer el lease (20:51:14, `Intentos=2`): una sola respuesta (paso 7), 0 ajustes nuevos, `CantidadSeguimientos` sin incremento, una sola burbuja del ajuste de ese turno, log sin ERR/FTL. (Un primer intento cortó con el turno ya terminado: sin duplicados.) |
| CA-M3b-14 | PASS | Martín y Empleado A (ajenos), Director org B contra #14; Laura contra #2 (Empleado A) y #5 (org B): Detalle, Progreso, EnviarSeguimiento y Cancelar → 404 en los 20 casos; base sin cambios. |

### Historias de usuario M3b
| HU | Resultado |
|---|---|
| HU-M3b-01 | cumple (Ctrl+Enter envía, Enter hace salto de línea: valor "Ajuste línea uno\nlínea dos" sin envío) |
| HU-M3b-02 | cumple (aviso info "Algunas reglas cambiaron desde que empezó esta conversación. Acá se siguen usando las de entonces." + "Empezar una tarea nueva" con agente y cliente) |
| HU-M3b-03 | cumple ("En cola…" / "Trabajando · paso 1 de hasta 25"; respaldo de 10 s con SignalR bloqueado: respuesta en 10,1–10,2 s sin recargar) |
| HU-M3b-04 | cumple (CA-M3b-04) |
| HU-M3b-05 | cumple ("N mensajes · tokens · USD … en total", "Quedan N ajustes", singular con 1) |
| HU-M3b-06 | cumple (cancelar un ajuste con confirmación "¿Cancelar esta respuesta? La conversación anterior se conserva." → "Cancelaste esta respuesta."; seguir desde Cancelada y desde Fallida) |
| HU-M3b-07 | cumple (CA-M3b-10) |
| HU-M3b-08 | cumple (Director lee; preferencias de Laura como "Preferencias personales de Laura Marketing (1 regla)" sin título ni texto; staff adminqa y SuperUsuario ven "QA Laura neutro") |
| HU-M3b-09 | cumple (CA-M3b-11) |
| HU-M3b-10 | cumple ("Nueva tarea con este agente" en encabezado para miembros y en la alerta de límite; precarga agente y cliente; sin cliente cuando está dado de baja; no se muestra al staff) |
| D-M3b-1 | cumple (licencia 1 revocada por SQL: `ov-alert warning` "Tu organización no tiene la suscripción vigente para este agente.", sin cuadro, conversación legible; POST rechazado; licencia restaurada `Revocada=0`) |
| D-M3b-2 | cumple (cliente "QA M3b Cliente baja" (43) dado de baja por la Directora: "Cliente: QA M3b Cliente baja (dado de baja)", cuadro presente, ajuste completado, atajo sin `clienteCarteraId`) |

### Máquina de estados M3b
| Transición | Resultado |
|---|---|
| Completada → Pendiente (ajuste del autor) | PASS |
| Fallida → Pendiente (ajuste) | PASS |
| Cancelada → Pendiente (ajuste; cancelada M3b y cancelada vieja sin cierre) | PASS |
| Pendiente → EnCurso → Completada (worker, pasos por turno: con `MaxPasos=2` y 5 llamadas previas se completa) | PASS |
| EnCurso → Fallida (máximo de pasos del turno) | PASS |
| Pendiente/EnCurso → Cancelada (autor) | PASS |
| Pendiente/EnCurso → Cancelada (Director sobre turno de la empleada: "La canceló Directora A." para la autora, "Cancelaste esta respuesta." para la Directora) | PASS |
| EnCurso interrumpido por reinicio → EnCurso retomado al vencer el lease → Completada | PASS (CA-M3b-13) |
| Pendiente/EnCurso + ajuste | Rechazado (PASS) |
| Ajuste de no autor (Director, staff) | 403 (PASS) |
| Ajuste con límite / sin suscripción / vacío / largo | Rechazado con mensaje (PASS) |
| Cualquier acción sobre tarea ajena (Empleado) u otra organización | 404 (PASS) |
| EsperandoAprobacion | N/A: el modelo simulado no pide herramientas con aprobación |

### Checklists UI (25/26/32)
- Grilla de Tareas server-side sin 500: columnas y filtros nuevos, Select2 (foco en buscador), daterangepicker, Session, "Limpiar filtros", búsqueda global por rótulo/fecha/número, orden de columnas nuevas (ver CA-M3b-11).
- Cuadro de ajuste: contador en vivo con separador de miles, rojo al superar, hint con ajustes restantes, botón con `title="Ctrl+Enter"`, estado deshabilitado coherente con el turno activo; acciones visibles = transiciones válidas (Cancelar solo con turno activo; cuadro solo para el autor; alerta en límite/suscripción).
- Mobile 390px: sin scroll horizontal en detalle #14/#15, Tareas y Nueva tarea; cuadro `position: sticky` al pie (bottom 844 = alto del viewport con hilo de 4.280 px); burbujas dentro del ancho. Capturas `m3b-mobile-*`.
- Tema oscuro: burbujas (contraste 13–15), cabecera del cuadro (12,2), notas/hint/pasos (5,7–7,0), Select2 del listado oscuro. **Alertas `.ov-alert` y badge "Ajuste" ilegibles → QA-M3b-01, corregido** (danger 1,54→6,74; warning 1,96→9,65; info 2,61→9,63; badge 1,79→9,12). Tema claro sin cambios. Capturas `m3b-dark-*`/`m3b-light-*`.
- Rótulos del diseño presentes ("Seguir conversando", "Pedile un ajuste: más corto, otro tono, agregá…", "Seguís con el mismo agente, cliente y reglas.", "Nueva tarea con este agente", "Última actividad", "Mensajes", "Solo el pedido", "Con ajustes", "Ver pasos", "Copiar", "Pedido", "Ajuste", nota de no autor, "Podés pedirle que siga…", "Se canceló esta respuesta."; el aviso de reglas cambiadas y la confirmación de cancelar verificados en su estado). Sin términos internos (MensajeUsuario, CierreTurno, EnCurso, Turno) para miembros. Ortografía: sin palabras de riesgo sin tilde en 8 pantallas (los "Cuando"/"Pendiente" detectados son texto del método del núcleo que ve el staff, correctos).
- Consola: sin errores JS ni 5xx en ninguna fase (solo 403/404 provocados).

### Regresión
- M3: vista previa en Nueva tarea con 8 grupos en el orden de niveles ("De la empresa — siempre" …); "Lo que el agente tuvo en cuenta (8)" para autora con su preferencia y para la Directora con el contador; Reglas por pestaña (5) → 200; reglas 16 y 21 vueltas a Activa.
- M2 y portal por rol: Directora (Inicio, Áreas, alta/edición, Miembros, Cartera, alta/edición/detalle, Tareas, Agentes, Perfil, Reglas y alta), Empleada (Inicio, Cartera, Tareas, Agentes, Perfil, Reglas; Áreas/Miembros → AccessDenied), staff (todos los links del menú, detalles de organizaciones 1 y 4, reglas de la org 1, núcleo, detalle de tarea de org B) → 200.
- Build 0 errores / 0 advertencias; tests 83/83 antes y después del auto-fix.

### Cobertura del catálogo cross-proyecto (M3b)
| id | aplica | resultado | acción |
|---|---|---|---|
| OLV-002 (nuevo) | sí (alertas y badge del detalle en tema oscuro) | FAIL → PASS post-fix | ítem creado + auto-fix `site.css` |
| OLV-001 | sí (Select2/daterangepicker del listado en oscuro) | PASS | — |
| CRM-002 | sí (cuadro oculto a no autores + 403/404) | PASS | — |
| CRM-017 | sí (tope de 20 ajustes y largo) | PASS: único camino que crea `MensajeUsuario` e incrementa el contador es `EnviarSeguimientoAsync`, que valida el tope; POST directo también rechazado | — |
| CRM-020 | parcial (`ReglasCambiaronAsync` dentro del detalle) | Observación: no está envuelto; si falla, cae el detalle del autor (no reproducido) | OBS-M3b-3 al implementador |
| REG-008 | sí (re-render del cuadro en cada refresco) | PASS: el textarea está deshabilitado mientras hay refrescos y el canal se detiene al estado final | — |
| KOI-001 | sí (Cancelar con `btn-swal-confirm`) | PASS (dentro del form, confirmación y POST) | — |
| LP-004 | sí | PASS | — |
| CRM-003, MH-015, MH-018 | sí (orden de columnas nuevas) | PASS | — |
| DN-001, DN-002, MH-001 | sí (filtros/búsqueda nuevos en MySQL) | PASS (sin errores de traducción ni 500) | — |
| MH-009, MH-014 | sí (fechas) | PASS (Última actividad 17:36 ART = 20:36 UTC en base) | — |
| KOI-009 | parcial | PASS en URLs nuevas (`Url.Action`); el hub sigue en `/hubs/tareas` absoluto (heredado M1) | observación si se hostea en subdirectorio |
| KOI-011, KOI-014 | sí | PASS (rango sin resultados sin errores) | — |
| REG-010, KOI-003/005/006, ELV-001 | sí (menú sin cambios) | PASS | — |
| LIP-001, KOI-013, CRM-018, CRM-021, CRM-022 | no | N/A | Sin formularios con ModelOnly, checkbox+hidden, flags de negocio, padre nuevo ni modo sombra (el modelo simulado solo existe en Development). |
| Resto del catálogo | no | N/A | Igual que M2/M3. |

### Cobertura de reglas nuevas/modificadas desde la última corrida
Ninguna nueva desde 2026-09-14 (corrida M3). OLV-002 se creó en esta corrida y quedó validado.

### Casos de prueba acordados M3b
- Tareas creadas en QA M3b (ninguna Pendiente/EnCurso al cerrar, verificado por SQL): **#13** Completada (Laura, 1 ajuste); **#14** Cancelada (Laura, CM, Panadería Norte, 10 ajustes; turnos completados, cancelados por autora y por Directora, fallido por máximo de pasos; el último turno lo canceló la Directora; costo/tokens restaurados a 0); **#15** Completada (Laura, cliente "QA M3b Cliente baja" (43) dado de baja, 3 ajustes, incluido el del reinicio).
- Tareas viejas con ajuste: #3 (Empleado A, 1 ajuste) y #4 (Directora, cancelada vieja con cierre + 1 ajuste).
- Datos restaurados: licencia 1 `Revocada=0`; reglas 16 y 21 activas (nuevos eventos de activar/desactivar en su historial); `MaxPasos=25` en todas.
- Scripts: `m3b-f1.js` (autor), `m3b-f2.js` (permisos, límites, reglas, baja, pasos, costo, viejas), `m3b-f3.js` + `m3b-f3b-listado.js` (listado, mobile, oscuro, textos, regresión), `m3b-diag-dark.js` (contraste efectivo), `m3b-f4-reinicio.js` (cortar/verificar).

### Defectos M3b
- **QA-M3b-01 (minor, OLV-002 nuevo) — corregido.** En tema oscuro el texto de `.ov-alert` (danger/warning/info/success) quedaba oscuro sobre fondo oscuro y el badge "Ajuste" (`bg-info text-dark`) blanco sobre celeste: el error de un turno fallido, la alerta de límite y la de suscripción no se leían. Pasos: cookie `crm-tema=dark` → detalle de una tarea con turno fallido / con 20 ajustes / Reglas como Empleada. Causa: el theme oscurece `--ov-*-subtle` (rgba .15) sin variante de color de texto y fuerza `.text-dark` con `!important`. Fix: bloque `[data-theme="dark"]` en `src/OlvidataAgentes.Web/wwwroot/css/site.css` (tonos claros por variante, enlaces heredan color, `.badge.bg-info/bg-warning.text-dark` oscuro). Verificado post-fix con contraste WCAG efectivo (≥ 6,7) y tema claro sin cambios. Cierra también OBS-4 de M2.

Observaciones (no bloquean):
- OBS-M3b-1 Tras un reinicio con un turno EnCurso, la tarea se retoma recién al vencer el lease (`LeaseSegundos` 300): hasta 5 minutos mostrando "Trabajando · paso 1 de hasta 25" sin avance (Cancelar disponible). Comportamiento heredado del motor M1; sugerencia al implementador: liberar al arrancar los leases del propio host o acortar el lease.
- OBS-M3b-2 En tema claro la nota gris del turno cancelado (`.ov-chat-nota`, token muted) mide 4,31 de contraste (bajo 4,5 AA para texto chico). Cosmético, token del theme.
- OBS-M3b-3 (CRM-020) `ReglasCambiaronAsync` corre sin protección dentro de `ObtenerDetalleAsync`: un fallo del recálculo de reglas tiraría el detalle del autor en vez de omitir el aviso.
- OBS-M3b-4 Reactivar la regla desactivada hace desaparecer el aviso de reglas cambiadas (el conjunto vigente vuelve a coincidir con la instantánea). Coherente con el diseño; informativo.
- OBS-M3-2 sigue: el agente se muestra por slug ("inmo-cm") en encabezado, burbujas y listado.

### Riesgos de liberación M3b
- R-M3b-01/RT-M3b-02 costo creciente y caché del historial: sin medir con la API real (corrida paga pendiente del OK de Joaquín).
- RT-M3b-03 detección de "conversación demasiado larga" depende del texto del error del SDK: no verificable sin costo.
- CA-M3b-02 calidad real del ajuste: solo verificable con el modelo real.
- OBS-M3b-1: reanudación hasta 5 minutos después de un reinicio (en SmarterASP los reciclajes del pool lo harían visible).
- RT-M3-02/RF-M3b-08 carrera de doble envío: cubierta por test y SQL del implementador; en navegador solo se probó el rechazo secuencial.

### Estado go/no-go M3b
**Apto con observaciones.** 14/14 CA en PASS (CA-M3b-02 y CA-M3b-07 con apoyo de tests por el modelo simulado), 10 HU + D-M3b-1/2 cumplen, IDOR sin fugas, 1 defecto minor corregido por auto-fix (OLV-002), build 0/0 y tests 83/83.

---

# M3 — Reglas por alcance

QA etapa 6 ejecutada el 2026-09-14 sobre `C:\Sistemas\Olvidata Agentes Multi-rubro`, portal local `https://localhost:7200` con `MotorAgentes__Habilitado=false` (sin llamadas a Anthropic), base `olvidata_agentes_dev`. Estado: **apto con observaciones** (0 defectos; sin cambios de código).

Camino de verificación: servidor MCP `playwright` **no cargado en la sesión** (ToolSearch sin `mcp__playwright__*`); se usó la librería Playwright 1.63 desde Node con Chromium headless (navegador real), scripts `m3-*.js` en el scratchpad de la sesión, consultas de integridad con `mysqlsh` (el cliente `mysql.exe` 8 no carga `caching_sha2_password`). Cada FAIL de script se reprodujo o descartó con diagnóstico propio (`m3-f3b-diag.js`, `m3-f3c.js`, `m3-f3d.js`, `m3-f4b-grilla.js`); ningún PASS sin ejecución.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-09-14
- Sin reglas nuevas desde la corrida M2 del mismo día: `regresiones-manuales.yml` solo difiere de git en OLV-001 (agregado por QA M2); `32-estandares-qa-implementador` modificado 2026-09-13. Stack 34/35: no aplican.

### Cobertura de criterios de aceptación M3
| CA | Resultado | Evidencia |
|---|---|---|
| CA-M3-01 | PASS | Vista previa de Laura (CM + Panadería Norte): "De la empresa — siempre" primero y "De la empresa" (salvo…) después; Directora sin área: mismo orden. |
| CA-M3-02 | PASS | Empleada: pestañas De la empresa · De mi área · Por agente · De clientes · Mis preferencias; sin "Nueva regla" ni acciones, aviso "Estas reglas las define el Director…"; GET Create/Edit → AccessDenied; POST Create/Edit → redirect a AccessDenied; POST CambiarEstado → 403 JSON; 0 filas creadas, R1 intacta. Empleado sin área no ve "De mi área". |
| CA-M3-03 | PASS | Regla de Marketing aplica a Laura y no a Martín (Contable); Laura pasada a Contable → la siguiente vista previa muestra la de Contable y no la de Marketing (revertido). |
| CA-M3-04 | PASS | Martín con Panadería ve "QA Panadería horario"; sin cliente o con Ferretería no. |
| CA-M3-05 | PASS | Cliente + agente CM aparece en "De Panadería Norte para este agente" antes de "De Panadería Norte"; con Tasador no aplica. Orden completo de 9 niveles verificado. |
| CA-M3-06 | PASS | "Mis preferencias" solo del autor en listado, búsqueda global de las 5 pestañas, vista previa; Detalle/Edit ajeno → 404, POST estado → 404. |
| CA-M3-07 | PASS | Editar → "Regla actualizada: versión 2."; guardar sin cambios → "No hubo cambios; la regla sigue en la versión 2."; historial con autor, fecha, campo "Texto" y texto de cada versión. |
| CA-M3-08 | PASS | Desactivar desde grilla con confirmación del diseño, toast, estado Inactiva y fuera de la vista previa; tarea previa conserva la regla con v1 y badge "Cambió después". |
| CA-M3-09 | PASS | Área dada de baja: regla fuera de la vista previa, "No se aplica" con tooltip "El área fue dada de baja.", filtro de Estado OK, `Activa=1` sin borrar; activar → "No se puede activar: el área fue dada de baja.". Cliente dado de baja: "No se aplica · El cliente fue dado de baja.", fuera del combo, vista previa por GET → "El cliente elegido no existe.", POST de tarea forzado rechazado sin crear tarea. |
| CA-M3-10 | PASS | 4.001 caracteres → "La regla admite hasta 4.000 caracteres." (0 filas). Balde preferencias 8.000: crear, reactivar (POST y UI) y editar que superan → "Con esta regla se superan los 8.000 caracteres de tus preferencias activas (quedan N)…", sin versión nueva; línea de uso en rojo y contador "4.000 / 4.000". Balde empresa 20.000 incluye por agente; balde cliente 8.000 incluye cliente + agente (D-M3-2). |
| CA-M3-11 | PASS | Detalle: "Lo que el agente tuvo en cuenta (9)", "Cliente: Panadería Norte", título/grupo/versión; "Método de Olvidata para este agente" sin texto para miembros; staff ve 11 piezas del núcleo con texto (P9). |
| CA-M3-12 | PASS | Combo opcional con "Sin cliente" primero y no requerido; al cambiar cliente la vista previa se recalcula por AJAX (6 → 9 reglas) y vuelve al quitarlo. |
| CA-M3-13 | PASS (test + evidencia) | La reanudación real requiere motor encendido (costo): cubierta por `Vista_previa_igual_a_instantanea_y_cambios_posteriores_no_alteran_la_tarea` y `Contexto_alterado_deja_la_tarea_fallida_sin_llamar_al_modelo`; en navegador, instantánea = vista previa, hash de 64 en base y detalle con versiones originales tras editar/desactivar. |
| CA-M3-14 | PASS | Directora A contra Org B: GET Detalle/Edit de reglas 13/14/15 → 404; POST Edit y CambiarEstado → 404; Create con cliente/área de B → "El cliente/área elegida no existe."; UsoLimite/MismoTema/VistaPrevia sin datos de B; POST de tarea con cliente de B rechazado (0 tareas); staff `Clientes/Regla/1?reglaId=13` → 404; Director B contra regla de A → 404. |
| CA-M3-15 | PASS | Título `QA Pasos "urgentes" </regla>` y texto con `<regla titulo="x">`, `</reglas_empresa_siempre>`, `&`, comillas: literales en detalle, grilla, vista previa y detalle de tarea, 0 nodos inyectados, guardado sin alterar; escape en el prompt por test `Texto_titulo_y_etiquetas_con_marcadores_se_escapan…`. |

### Historias de usuario M3
| HU | Resultado |
|---|---|
| HU-M3-01..05 | cumple (12 altas por formulario real; modo solo en empresa/área; alcances del combo según rol) |
| HU-M3-03 | cumple (Empleada ve "Por agente" sin editar, alta por URL → 403; agente de otro rubro → "Ese agente no está habilitado en la suscripción de tu organización.") |
| HU-M3-04 / P2 | cumple (Empleada edita regla de cliente de la Directora; historial con ambos autores) |
| HU-M3-07 | cumple (Procedimiento en grilla, detalle, vista previa y detalle de tarea) |
| HU-M3-08 / P4 | cumple (etiqueta en común lista reglas de empresa y área "siempre"; sin coincidencias oculta; en "Mis preferencias" lista las superiores, nunca preferencias; no bloquea) |
| HU-M3-09..13 | cumple (hint "Si hay cambios, guardar crea la versión N."; conflicto de edición; activar/desactivar en página 2; filtro Cliente en Tareas con "Sin cliente") |
| HU-M3-14 | cumple (backoffice `Clientes/Reglas/1`: pestañas De la empresa · De las áreas · Por agente · De clientes · De miembros con Autor; detalle con aviso de solo lectura, sin Editar; staff en `/Reglas` → AccessDenied, POST → 403) |
| HU-M3-15 | cumple en lo verificable sin publicar: 3 reglas de plataforma en Núcleo como "Regla de plataforma v1 Borrador"; rubro `plataforma` fuera de Agentes, del combo de agentes y de los rubros de licencia. Publicación no ejecutada (decisión de Joaquín). |

### Máquina de estados (regla)
| Transición | Resultado |
|---|---|
| Activa → Inactiva (con permiso) | PASS, confirmación + evento en historial |
| Inactiva → Activa (destino vigente, con lugar) | PASS |
| Inactiva → Activa superando el balde | Rechazada con mensaje (PASS) |
| Inactiva → Activa con área dada de baja | Rechazada "No se puede activar: el área fue dada de baja." (PASS) |
| Activa → Activa vN+1 (editar con cambios) / sin cambios | PASS / sin versión (PASS) |
| Editar con versión vieja (edición simultánea) | "Otra persona modificó esta regla mientras la editabas…" sin pisar (PASS) |
| Activa → "No se aplica" derivado (baja de área, baja de cliente, autor bloqueado) | PASS (sin tocar `Activa`) |
| Cualquier transición sin permiso / de otra organización | 403 / 404 (PASS) |

### Checklists UI (25/26/32)
- Grilla de reglas server-side: filtro por cada columna (Título, Cliente, Agente con "Sin agente", Tipo, Versión, Etiqueta, Cuándo se aplica, Estado, Modificada con daterangepicker), Session repone filtros, "Limpiar filtros" no reaparecen, búsqueda global por rótulo visible ("siempre") y fecha, orden asc/desc de todas las columnas ordenables en las 5 pestañas (200), desactivar en página 2 se queda en página 2. Línea de uso del balde en pestañas.
- Select2 en todos los combos (filtros y formulario) con foco en el buscador; etiquetas con tags: minúscula, máximo 5 ("Hasta 5 etiquetas."), sugiere las usadas. "Opciones avanzadas" plegado por defecto y se despliega. Formulario `.ov-*`, barra sticky (igual que Cartera en mobile), contador de caracteres.
- Mobile 390px: sin scroll horizontal en 8 pantallas; vista previa debajo del pedido, colapsada con contador "N reglas" y se abre.
- Tema oscuro: Reglas, formulario, detalle, Nueva tarea, detalle de tarea y ficha de cliente legibles (capturas `m3-dark-*`); badges "Cambió después"/"Procedimiento" legibles.
- Rótulos D-M3-8..12 presentes y sin términos internos para miembros ("Obligatoria", "Por defecto", "Organización", "Alcance"). Ortografía: sin palabras de riesgo sin tilde en 18 pantallas M3.
- Consola: sin errores JS ni 5xx en todas las fases; log del portal sin ERR/FTL.

### Regresión
M2 y portal por rol: Directora (Inicio, Áreas, alta/edición de área con card de reglas, Miembros y edición, Cartera, alta/edición, Tareas, Agentes, Perfil), Empleada (Inicio, Cartera, Tareas, Agentes, Perfil; Áreas/Miembros → AccessDenied), staff (todos los links del menú: Agentes, Tareas, Organizaciones, Núcleo, Uso, Notificaciones, Auditoría, Usuarios, Conexiones, Sistema; detalles de organizaciones 1 y 4) → 200. Visibilidad de tareas: Directora 6, Empleada solo la suya, staff todas. Menú "Reglas" solo miembros. Bloqueo/desbloqueo de miembro OK. Build 0 errores / 0 advertencias; tests 61/61.

### Cobertura del catálogo cross-proyecto (M3)
| id | aplica | resultado | acción |
|---|---|---|---|
| REG-010, KOI-003, KOI-005, KOI-006, ELV-001 | sí (link Reglas y policies) | PASS | — |
| CRM-002 | sí (acciones sin permiso) | PASS | — |
| LIP-001 | sí (errores del service en `alert-danger`) | PASS | — |
| LP-004 | sí (Session por pestaña) | PASS | — |
| CRM-003, MH-015, MH-018 | sí (orden de columnas) | PASS | — |
| DN-001, DN-002, MH-001 | sí (listados y filtros por etiqueta/ids) | PASS (sin errores de traducción en MySQL real) | — |
| MH-009, MH-014 | sí (fechas) | PASS (Modificada y historial en hora argentina) | — |
| KOI-009 | sí | PASS (`Url.Action`) | — |
| KOI-011 | sí | PASS | — |
| KOI-014 | sí (estados vacíos) | PASS | — |
| OLV-001 | sí (tema oscuro Select2/daterangepicker) | PASS | — |
| KOI-001, KOI-013 | no | N/A | — |
| Resto del catálogo | no | N/A | Igual que M2: módulos de ventas, stock, pagos, AFIP, bot, decimales. |

### Cobertura de reglas nuevas/modificadas desde la última corrida
Ninguna nueva desde 2026-09-14 (corrida M2).

### Casos de prueba acordados M3
- Org 1: áreas Marketing (41) y Contable (42); clientes Panadería Norte (41) y Ferretería Sur (42, dado de baja en QA); Laura Marketing `laura@qa.test` (Empleada, Marketing) y Martín Contable `martin@qa.test` (Empleado, Contable); áreas "QA Temporal M3" y "QA Temporal M3 b" dadas de baja.
- Reglas "QA …" (39 en org 1, 29 activas): 12 de la matriz (R1..R11 + "Marketing por defecto"), 16 "QA Pag NN" sobre "QA Cartera 01", reglas de límites desactivadas, preferencias de Laura/Martín. Org 4: 3 reglas (empresa, cliente, preferencia) para IDOR.
- Tareas #7 (Laura, CM, Panadería) y #8 (Martín, sin cliente) con instantánea: **canceladas**. Reglas de plataforma #56–#58 en Borrador.
- Scripts: `m3lib.js`, `m3-f1-setup.js`, `m3-f2-ca.js`, `m3-f3-ca.js`, `m3-f3b-diag.js`, `m3-f3c.js`, `m3-f3d.js`, `m3-f4-ui.js`, `m3-f4b-grilla.js`.

### Defectos activos M3
Ninguno. Sin auto-fixes.

Observaciones (no bloquean, sin cambio de comportamiento):
- OBS-M3-1 El Director ve el texto de las preferencias personales del autor en el detalle de una tarea visible ("Preferencias de quien la pidió"). Coincide con P-M3-05 y la matriz (reglas aplicadas en tareas visibles), pero tensiona CA-M3-06 ("no las ve en ningún listado"): confirmar con el analista.
- OBS-M3-2 El agente se muestra por slug ("para inmo-cm") en destino, cards y combos porque el nombre del artefacto importado es el slug (dato del núcleo, no de M3).
- OBS-M3-3 `UsoLimite` con cliente de otra organización responde "Elegí el cliente." en vez de "El cliente elegido no existe." (sin fuga).
- OBS-M3-4 La línea de uso dice "(con esta regla)" aunque el texto esté vacío (cosmético).
- OBS-M3-5 Filtros de texto con `keyup` (OBS-1 de M2) también en Reglas.

### Riesgos de liberación M3
- R-M3-01 inyección: mitigada y verificada en UI/escape; la obediencia real del modelo requiere corrida paga (pendiente OK de costo).
- Reglas de plataforma sin publicar: hasta la evaluación de Joaquín no entran en ningún contexto.
- CA-M3-13 y caché de bloques (RT-M3-01) sin corrida real.
- RT-M3-02 carrera de límites aceptada (no probada en paralelo).

### Estado go/no-go M3
**Apto con observaciones.** 15/15 CA y 15 HU en PASS (CA-M3-13 por test + evidencia de instantánea), IDOR sin fugas, 0 defectos, build y tests 61/61.

---

# M2 — Organización del portal

**M2 — Organización del portal.** QA etapa 6 ejecutada el 2026-09-14 sobre el repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, portal local `https://localhost:7200` con `MotorAgentes__Habilitado=false` (sin llamadas a Anthropic), base `olvidata_agentes_dev`. Estado: **apto con observaciones**.

Camino de verificación: el servidor MCP `playwright` **no estaba cargado en la sesión** (ToolSearch sin herramientas `mcp__playwright__*`); se usó la librería Playwright 1.63 desde Node con Chromium local (navegador real, headless), scripts en el scratchpad de la sesión. Consultas de integridad directas a MySQL. Nada se dio por PASS sin ejecución.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-09-14
- Primera corrida de QA del proyecto: se validó por primera vez el catálogo vigente completo (`regresiones-manuales.yml`, 72 ítems incluido el nuevo OLV-001) y `32-estandares-qa-implementador.instructions.md` a esa fecha. Instructions de stack 34 (AFIP) y 35 (stock): no aplican.

### Cobertura de criterios de aceptación
| CA | Resultado | Evidencia |
|---|---|---|
| CA-01.1 | PASS | Director: Cartera + Mi organización (Miembros, Áreas). Empleado: Cartera sin Mi organización. |
| CA-01.2 | PASS | Empleado en `/Areas`, `/Areas/Create`, `/Areas/Edit/1`, `/Miembros`, `/Miembros/Edit/{id}` → pantalla "403 Acceso denegado"; POST AJAX `/Areas/DarDeBaja` y `/Miembros/CambiarEstado` → 403. |
| CA-02.1 | PASS | "Área creada."; "ventas" repetida → "Ya existe un área con ese nombre en tu organización." (1 sola vigente en base); vacío y >100 caracteres bloqueados (cliente y servidor); Org B crea "Ventas". |
| CA-02.2 | PASS | "Área actualizada.", descripción releída; renombrar a "VENTAS" → mensaje de duplicado. |
| CA-02.3 | PASS | Confirmación "¿Dar de baja el área «Ventas»? Su único miembro va a quedar sin área."; toast "Área dada de baja. 1 miembro quedó sin área."; miembro "Sin área" en grilla y `AreaId` NULL en base. |
| CA-02.4 | PASS | Ventas → 1 miembro; el número enlaza a Miembros con filtro de área aplicado. |
| CA-03.1 | PASS | Solo los 4 miembros de la org A; sin acción de alta; fila propia con "Vos" y sin bloqueo. |
| CA-03.2 | PASS | Empleado→Director: en la siguiente request (sin re-login) ve Mi organización y `/Areas` 200; vuelta a Empleado → AccessDenied en la siguiente request. |
| CA-03.3 | PASS | Degradar a la última Directora (UI con confirmación) y al único Director de Org B (POST) → "La organización tiene que tener al menos un Director activo…"; rol intacto en base. |
| CA-03.4 | PASS | Bloqueo por AJAX sin recargar; sesión abierta del bloqueado: AJAX → 401 "Tu sesión terminó. Volvé a iniciar sesión."; segunda ventana → Login; login posterior → "Su cuenta se encuentra bloqueada."; al desbloquear vuelve a entrar. |
| CA-03.5 | PASS | POST de Editar miembro con `AreaId` de la org B → "El área elegida no existe."; `AreaId` sin cambio en base. |
| CA-04.1 | PASS | Empleado carga y edita con todos los datos (CUIT normalizado a dígitos, email en minúsculas); vacío bloqueado; ficha con "Cargado por". |
| CA-04.2 | PASS | CUIT repetido (pegado con puntos) → "Ya hay un cliente con esa identificación en la cartera."; mismo CUIT en Org B se guarda. CUIT con DV inválido, DNI de 3 dígitos, tipo sin número y número sin tipo → mensajes del diseño; 0 filas basura. |
| CA-04.3 | PASS | Empleado sin botón de baja (listado, detalle, edición); POST forzado → 403 `{"success":false,"message":"Solo un Director puede dar de baja clientes."}`; cliente vigente. |
| CA-04.4 | PASS | Server-side; filtro por cada columna (Nombre, Identificación, Email, Teléfono, Alta con daterangepicker); búsqueda global por CUIT con y sin guiones y por fecha dd/MM/yyyy; filtros y buscador repuestos desde Session; "Limpiar filtros" no reaparecen; baja AJAX en página 2 se queda en página 2. |
| CA-05.1 | PASS | Director ve 4 tareas de la org con "Pedida por"; staff ve las 5 de todas las orgs. |
| CA-05.2 | PASS | Empleado: "Mis tareas", sin columna/filtro "Pedida por", solo 2 propias; detalle, progreso y cancelar de tarea ajena → 404. |
| CA-06.1 | PASS | SuperUsuario da de alta Director/Empleado con rol y área; los 4 miembros inician sesión. Email repetido y contraseña floja con mensajes en castellano. |
| CA-06.2 | PASS | Org sin miembros: combo solo "Director" + hint; POST manipulado con Empleado → "El primer miembro de una organización tiene que ser Director." |
| CA-06.3 | PASS | Administrador sin card "Nuevo miembro"; POST `CrearMiembro` → redirect AccessDenied, 0 usuarios creados; ve Miembros y Estructura en solo lectura. |
| CA-T.1 | PASS | Director B contra ids de A: GET Áreas/Edit, InfoBaja, Miembros/Edit, Cartera/Detalle y Edit, Tareas/Detalle y Progreso → 404; POST Áreas/Edit y DarDeBaja, Miembros/Edit y CambiarEstado (incl. AreaId), Cartera/Edit y DarDeBaja, Tareas/Cancelar → 404; datos de A intactos en base; `TenantId=1` agregado al POST de alta de área → se crea en Org B; listados de B sin datos de A. |
| R-03 (riesgo) | PASS | Carrera: dos Directoras se degradan mutuamente en paralelo (única otra Directora bloqueada) → una se guarda, la otra recibe el mensaje; queda 1 Directora activa. |

### Máquina de estados (miembro)
| Transición | Resultado |
|---|---|
| Activo → Bloqueado (otro Director activo) | PASS "Miembro bloqueado.", sesión invalidada |
| Bloqueado → Activo | PASS "Miembro desbloqueado." |
| Empleado → Director | PASS, impacta en la siguiente request |
| Director → Empleado (queda otro) | PASS; uno mismo: confirmación, redirect a Inicio, "Dejaste de ser Director." |
| Director → Empleado (último) | Rechazada con mensaje (PASS) |
| Bloquear la propia cuenta | Rechazada "No podés bloquear tu propia cuenta." (PASS) |
| Cualquier transición sobre miembro de otra org | 404, sin cambios (PASS) |

### Cobertura de historias de usuario
| HU | Resultado |
|---|---|
| HU-01..HU-16 | cumple (HU-01 perfil con organización/rol/área; HU-05/06 filtros por columna; HU-07 confirmación al quitarse el rol; HU-09 errores de alta; HU-16 renombre D-1 y lectura del Administrador) |

### Checklists UI (regla 25/26/32)
- DataTables server-side en Áreas, Miembros, Cartera y Tareas, sin 500; filtro por cada columna visible; ordenamiento de todas las columnas ordenables contemplado en los services (costo por valor numérico); búsqueda global por texto, fecha, identificación e importe ("1,25", "0.5").
- Persistencia en Session y "Limpiar filtros" (Cartera verificado de punta a punta; mismo helper en las 4 grillas). Bajas AJAX con `ajax.reload(null,false)` verificadas en página 2 (Cartera y Áreas) y bloqueo de miembros sin recarga.
- Select2 en todo `<select>` de las pantallas M2 (salvo el "Mostrar N registros" de DataTables) y foco en el buscador al abrir. daterangepicker en Último acceso, Alta y Creada.
- Formularios: `ov-page-head` con descripción, `ov-form-page` (1080px), cards con encabezado, `ov-required`, hints, barra `ov-form-actions` sticky (visible al pie del viewport en mobile), resumen de validación `alert-danger` (oculto sin errores), autofocus en altas, `ov-detail-grid` con vacíos explícitos. Combos de Editar prepoblados (Rol, Área, Tipo de identificación) y todos los campos de negocio en alta y edición.
- Mobile 390px: sin scroll horizontal de página en 7 pantallas; sidebar abre. Tema oscuro: correcto tras auto-fix OLV-001.
- Ortografía: sin palabras de riesgo sin tilde en el texto visible de las pantallas M2 ni en backoffice; se corrigió "Auditoria" del sidebar.
- Consola: sin errores JS ni 5xx (solo los 403/404 provocados a propósito).

### Regresión
Login; Usuarios solo staff (listado solo `adminqa`, Details/Edit de un miembro → AccessDenied); Organizaciones y licencias (listado, alta, detalle con miembros, estructura y "Clientes en cartera: 19"); Núcleo, Uso, Agentes (staff y miembro), Tareas y detalle de tarea con progreso, Perfil (staff y Empleado), Sistema, Conexiones, Notificaciones, Auditoría (SuperUsuario) → 200. Build 0 errores; tests 48/48 después de los auto-fixes.

### Cobertura del catálogo cross-proyecto
| id | aplica | resultado | acción |
|---|---|---|---|
| REG-010 | sí (link "Auditoria de Cambios" para miembros) | FAIL → PASS post-fix | auto-fix `_Layout.cshtml` |
| KOI-003, KOI-005, KOI-006 | sí (links de sidebar vs policy/controller) | PASS | — |
| ELV-001 | sí (autorización de controllers M2) | PASS | — |
| CRM-002 | sí (acción visible sin permiso) | PASS (baja de cartera oculta al Empleado + 403) | — |
| LIP-001 | sí (errores `ModelOnly` del service) | PASS (se muestran en `alert-danger`) | — |
| LP-004 | sí (Session de filtros) | PASS | — |
| CRM-003, MH-015, MH-018 | sí (orden de columnas) | PASS (switch de SortColumn completo) | — |
| DN-001, DN-002 | sí (listados server-side) | PASS (sin Include de colecciones) | — |
| MH-001 (incl. variante StartsWith) | sí | PASS (sin `Contains/StartsWith/EndsWith` traducidos; `extraIds` es `List<int>`) | — |
| MH-009, MH-014 | sí (fechas en grillas) | PASS (Alta y Último acceso en hora argentina) | — |
| KOI-001 | sí (btn-swal-confirm) | PASS (el único uso, revocar licencia, está dentro del form) | — |
| KOI-009 | parcial (URLs AJAX absolutas) | PASS en M2 (`Url.Action`); el layout legado usa `/Account/ToggleTema` y `/sw.js` absolutos | observación si se hostea en subdirectorio |
| KOI-011 | sí (auditoría en escrituras) | PASS (todas las escrituras M2 persistieron con auditoría activa) | — |
| KOI-013 | no (M2 sin checkbox + hidden) | N/A | — |
| KOI-014 | sí (estados vacíos) | PASS (Org B vacía, filtros sin resultados: consola limpia) | — |
| OLV-001 (nuevo) | sí | FAIL → PASS post-fix | ítem creado + auto-fix `site.css` |
| REG-001..009, KOI-002, KOI-004, KOI-010, KOI-012, GAN-001..006, VSF-001..002, CRM-001, CRM-004..006, CRM-015..016, MH-002..008, MH-010..013, MH-016..021, SG-001, LP-001, LP-003, LP-005, ELV-002, DN-003..004 | no | N/A | Ventas, compras, stock, pagos, AFIP, bot, migraciones de catálogos o decimales en inputs: M2 no tiene esos módulos ni inputs decimales renderizados por Razor. |

### Cobertura de reglas nuevas/modificadas desde la última corrida
Primera corrida (sin fecha previa): todo el catálogo se validó por primera vez; ver tabla anterior. Reglas recientes de la instrucción 32 evaluadas explícitamente: KOI-B01 checkbox+hidden (N/A), KOI-B02 script bajo la misma condición (PASS, consola limpia en estados vacíos y por rol), MH-001 variante StartsWith (PASS), CRM-017 tope en todos los caminos y CRM-018 flag persistido (N/A para M2; el motor quedó apagado), CRM-020..022 (N/A), LP-002 propagación de campo nuevo (PASS: rol/área en sesión, perfil, backoffice y Tareas).

### Casos de prueba acordados
- Usuarios: Director A (`dira@qa.test`), Director A Dos (`dira2@qa.test`), Empleado A (`empa@qa.test`) y Usuario Demo en "Inmobiliaria Demo" (id 1); Director B (`dirb@qa.test`) en "QA Org B" (id 4, slug `qa-org-b`); Administrador `adminqa@qa.test`. Contraseña de prueba común de QA (solo base de desarrollo).
- Volumen: 18 clientes "QA Cartera NN" y 16 áreas "QA Área NN" en org 1 para paginación; 4 tareas terminadas (Completada/Cancelada) insertadas por SQL para visibilidad por rol.
- Scripts reutilizables (fases 1–4) en el scratchpad de la sesión: alta por backoffice, matriz de CA, IDOR, sesión/rol/bloqueo, regresión, formularios, mobile, tema oscuro y ortografía.

### Defectos activos
Ninguno bloqueante ni mayor. Corregidos en esta corrida:
- **QA-M2-01 (minor, REG-010)** — "Auditoria de Cambios" visible para Director/Empleado en la sección Administración, `/Audit` exige `RequireAdministracion` (AccessDenied) y sin tilde. Fix: `Views/Shared/_Layout.cshtml` muestra el link solo a SuperUsuario/Administrador y corrige "Auditoría". Verificado: Empleado/Director sin link; SuperUsuario con link y `/Audit` 200.
- **QA-M2-02 (minor, OLV-001 nuevo)** — combos Select2 y calendario daterangepicker blancos en tema oscuro. Fix: `wwwroot/css/site.css` con overrides `[data-theme="dark"]` sobre los tokens `--ov-*`. Verificado: fondo oscuro/texto claro en combo, desplegable, buscador y calendario; tema claro sin cambios.

Observaciones (no bloquean, sin cambio de comportamiento):
- OBS-1 Los filtros de texto disparan con `keyup`: pegar con el mouse no refresca la grilla hasta la próxima tecla (sugerencia: escuchar `input`).
- OBS-2 `/Miembros?areaId=` con un área de otra organización queda guardado en Session aunque el combo lo ignora; no muestra datos ajenos.
- OBS-3 Pantallas legadas (`Users/*`, `Clientes/Index`, `Clientes/Create`, `Account/Perfil`) conservan `<h3>` suelto y tablas no DataTables (deuda declarada por el implementador); "Crear Usuario"/`<h3>` sin sistema de formularios.
- OBS-4 `ov-alert info` con bajo contraste en tema oscuro (estilo legado).
- OBS-5 Acceso denegado de pantalla es redirect a `/Account/AccessDenied` (200 con "403 Acceso denegado"); policy fallida en AJAX → 403 sin JSON (DI-10). Coincide con el diseño.

### Riesgos de liberación
- RT-01 caché de sesión por instancia (límite aceptado; con un solo proceso en SmarterASP RF-11 se cumple en la siguiente request, verificado).
- Staff sin UI para editar/bloquear miembros (P-08 solo lectura + alta): el SuperUsuario depende del Director o de la base.
- El resolvedor no evalúa `Tenant.Estado` (organización suspendida sigue entrando).
- Scripts de QA dependen de CDN (DataTables/Select2/daterangepicker/SweetAlert2), igual que el resto del template.

### Estado go/no-go
**Apto con observaciones.** Todos los CA y CA-T.1 en PASS; dos defectos menores corregidos por auto-fix y re-verificados; build 0 errores y tests 48/48.

## Historial de ajustes
- 2026-09-14: QA M4 Agentes de la organización (sin revisión del Director): 14 CA aplicables y 12 HU en PASS por navegador real (Playwright librería, MCP no disponible) con modelo simulado (costo cero); CA-M4-03 y HU-M4-03/04 pospuestos por el gate; IDOR A↔B → 404; regresión del hash M2/M3b OK; rubro de prueba `qa-m4` (agente base + sugerencias, `incluido_siempre` desmarcado al cerrar); defecto QA-M4-01 contraste del menú rojo en oscuro y del motivo "No disponible" en claro → ítem OLV-003 + auto-fix `site.css`; 7 observaciones (Archivados clara, badge de marca 2,98, text-muted 4,24, POST sin base sin mensaje, autora sin aviso de ediciones del Director, bases por slug, intersección de herramientas solo por test); build 0/0 y tests 100/100; veredicto apto con observaciones.
- 2026-09-14: QA M3b Seguir conversando: 14 CA y 10 HU en PASS por navegador real (Playwright librería, MCP no disponible) con modelo simulado en Development (costo cero); reinicio a mitad de turno sin duplicar; IDOR 20 casos → 404; defecto QA-M3b-01 tema oscuro de `.ov-alert` y badge → ítem OLV-002 + auto-fix `site.css`; 4 observaciones (reanudación tras reinicio espera el lease, nota gris 4,31 en claro, `ReglasCambiaronAsync` sin protección, aviso que desaparece al reactivar); build 0/0 y tests 83/83; veredicto apto con observaciones.
- 2026-09-14: QA M3 Reglas por alcance: 15 CA y 15 HU en PASS por navegador real (Playwright librería, MCP no disponible; motor apagado, sin costo); IDOR contra Org B sin fugas; 0 defectos y sin cambios de código; 5 observaciones (preferencias visibles al Director en detalle de tarea, agente por slug, mensaje de UsoLimite, "(con esta regla)" vacío, filtros keyup); tareas de QA canceladas; reglas de plataforma sin publicar; veredicto apto con observaciones.
- 2026-09-14: QA M2 Organización (primera corrida del proyecto): 21 CA + R-03 en PASS por navegador real (Playwright librería, MCP no disponible); auto-fix REG-010 (`_Layout.cshtml`) y OLV-001 nuevo (`site.css`, tema oscuro de Select2/daterangepicker); catálogo completo validado por primera vez; veredicto apto con observaciones.
