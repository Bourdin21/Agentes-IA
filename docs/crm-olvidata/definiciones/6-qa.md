# Memoria - QA

## Proyecto: crm-olvidata — migración de BotPublicitario
## Ultima actualizacion: 2026-10-16

## Definiciones vigentes

### Reglas cross-proyecto validadas

**Última validación de reglas cross-proyecto: 2026-10-16**

- Primera corrida con este campo (antes no existía): se tomó como referencia la última QA de este proyecto (2026-08-28) y se validó contra el sistema todo lo agregado o modificado desde entonces en `32-estandares-qa-implementador.instructions.md` y `docs/qa/regresiones-manuales.yml`. Detalle en la sección "QA — feature 4 frentes — combo con gancho (2026-09-14)", punto F5.
- Reglas agregadas por esta corrida: **CRM-023** (yml) y "Arrays por AJAX GET con jQuery: `traditional: true`" (32). La próxima corrida diferencia desde 2026-09-14.
- 2026-10-15 (corrida CRM-028): diferencia tomada desde 2026-09-14 con `git log --since` sobre `32-estandares-qa-implementador.instructions.md` y `docs/qa/regresiones-manuales.yml`. Reglas nuevas en el período: **CRM-026** (defaultValue de enum en columna nueva), **CRM-027** (`Results.Forbid()` en endpoint anónimo), **LP-057** (único sobre entidad con baja lógica), **LP-004**, **MH-060/061**, **KOI-015/016/017**, **OLV-ALUC-01**, **OLV-EVAL-01** y el bloque LP-037→LP-111 de La Platense. Aplicables a este sistema y ejecutadas retroactivamente: **LP-057 PASS** (probada a nivel SQL contra `UX_PushSubscriptions_EndpointHash_Vivo`), **CRM-027 N/A verificado** (CRM-028 no agrega ningún endpoint anónimo: los 4 nuevos responden 302 al login sin sesión), **CRM-026 N/A** (la migración no agrega columnas de enum), **CRM-025 PASS** (el único admite varios dispositivos por usuario: 5 filas vivas del mismo `UserId`). El resto son reglas de dominio de otros proyectos (cobranzas, ledger, impositivo) sin superficie equivalente acá.
- **PAT-069** (Web Push servidor → navegador sin el sitio abierto) validado como patrón nuevo: las 3 piezas que declara (service worker vivo, claves VAPID, suscripción por dispositivo en BD) existen y el sobre real sale bien formado (`vapid t=<jwt>, k=<clave pública>`, `Content-Encoding: aes128gcm`, TTL 1800, `Urgency: high`). Lo único de PAT-069 que **no** se pudo validar es la última milla (el navegador recibiendo el globo), por aislamiento de red del entorno — ver la sección de la corrida.
- Reglas agregadas por esta corrida: **CRM-029** (yml) — un polling de background que estampa "leído" re-arma un guard anti-ruido en cada mensaje.
- 2026-10-16 (re-verificación de CRM-029): sin reglas nuevas en el catálogo entre el 2026-10-15 y hoy más allá de las propias de esta corrida. Regla agregada: **CRM-030** (yml) — al angostar un guard de un campo compartido a uno propio se pierden los re-armados legítimos de ese campo. La próxima corrida diferencia desde **2026-10-16**.
- 2026-10-16 (corrida de la cola de seguimiento, segundo lote del día): `git log --since=2026-10-16` sobre `32-estandares-qa-implementador.instructions.md` y `docs/qa/regresiones-manuales.yml` → **sin commits**: ninguna regla nueva ni modificada desde la corrida anterior de hoy, más allá de las dos que agrega esta. Reglas agregadas: **CRM-031** (major) y **CRM-032** (minor). La próxima corrida diferencia desde **2026-10-16**.

### 0. Alcance funcional validado

QA sobre la implementación completa de la migración de BotPublicitario a `OlvidataCRM` (`C:\Sistemas\olvidatasoft-crm`): CU-01 a CU-06 y CU-10 a CU-12 del Análisis, 11 historias de usuario (HU-01 a HU-11) del Diseño, 5 pantallas (`Contactos` Index/Details/Create/Edit, `Industrias` CRUD, `Bot/Outbound`), 2 máquinas de estados (`FaseConversacion`, `EstadoEmbudo`) y permisos por rol.

**Método:** revisión de código completa por capa (Domain/Application/Infrastructure/Web) contra los 4 documentos de definición (1-analista, 2-diseñador, 3-arquitecto, 5-implementador) + recompilación de la solución + verificación de migraciones aplicadas contra `olvidatacrm_dev` + ejecución del playbook cross-proyecto (`docs/qa/regresiones-manuales.yml`). **No se ejecutaron pruebas contra la app corriendo** (sin credenciales reales de Meta WhatsApp/Google Maps configuradas — `Olvidata_WhatsApp`/`Olvidata_GoogleMaps`/`Olvidata_Bot:VerifyToken` vacíos en `appsettings.json`, confirmado; riesgo #3 ya señalado por el implementador). Todo lo relacionado a envío/recepción real de WhatsApp o búsqueda real en Google Maps queda **BLOCKED**, no FAIL. Los casos de UI puramente de CRUD (Contactos/Industrias/Bot sin depender de las APIs externas) se describen como procedimiento manual para que Joaquín los ejecute a mano y reporte PASS/FAIL, dado que este agente no automatiza navegador.

**Build:** `dotnet build OlvidataCRM.slnx` → **Compilación correcta, 0 errores**, 8 warnings preexistentes (`NU1902` MailKit/MimeKit, ajenos a este alcance). Confirmado por este QA, no solo por el implementador.

**Migraciones:** `dotnet ef migrations list` confirma `20260715005143_InitialCreate` y `20260717141923_AddContactosYCatalogoIndustrias` aplicadas sin `(Pending)`.

### 1. Cobertura por historia de usuario (HU-01 a HU-11)

| HU | Criterio | Resultado | Nota |
|---|---|---|---|
| HU-01 (alta manual, CU-01) | CA1: teléfono único rechazado con mensaje claro y link al existente | **PARCIAL** | `ContactosController.Create` rechaza duplicado y arma el mensaje con `#{Id}` y nombre, pero es texto plano dentro de `asp-validation-for` (no hay `<a href>` real) — el mensaje es "claro" pero no hay "link" clickeable como pide la CA literalmente. Defecto menor, no bloqueante. |
| HU-01 | CA2: al guardar, Estado=Pendiente, Canal=Manual | **PASS** | `Create` fija `CanalOrigen.Manual`, `EstadoEmbudo.Pendiente`, `FaseConversacion.Nuevo` — verificado en código. |
| HU-02 (listado/filtros, CU-02) | CA1: cada columna visible tiene su filtro | **PASS** | Rubro/Canal/Estado (select), Última actividad (daterangepicker), buscador libre — todos presentes y conectados a `GetData`. |
| HU-02 | CA2: buscador encuentra por teléfono o nombre | **PASS** | `SearchValue` filtra `Telefono`/`NombreContacto`/`NombreNegocio`. |
| HU-02 (extra, no HU pero regla 25) | Ordenar por columna (click en encabezado) | **FAIL** | Ver defecto **CRM-003**: `GetData` ignora `order[0][column]`/`order[0][dir]`, siempre devuelve el mismo orden fijo pese a que la UI permite click-to-sort. |
| HU-03 (bot 1er mensaje) | CA1/CA2: salta menú si outbound conocido / pregunta categoría si espontáneo | **PASS (código)** / **BLOCKED (E2E)** | Lógica de `OnNewAsync` correcta contra el Diseño §3. E2E real bloqueado por falta de `Olvidata_WhatsApp`/`Olvidata_Bot:VerifyToken`. |
| HU-04 (presupuesto automático, CU-04) | CA1: precio base + upsell por usuario excedente | **PASS (código)** / **BLOCKED (E2E)** | `CompleteAsync`/`ResolveIndustriaCatalogoAsync`/`UsuariosIncluidosPorPlan` verificados línea a línea contra el seed de 13 industrias — mapeo de nombres correcto, cálculo de excedente correcto. Es la pieza de mayor riesgo señalada por el implementador (código nuevo, sin precedente en BotPublicitario); no se detectó bug en la lógica en sí. |
| HU-04 | CA2: rubro sin cotización automática → sin número, solo aviso | **PASS (código)** | Confirmado: "Farmacia" y "Contabilidad/Estudios contables" (vía outbound) y "Otro rubro" (vía inbound) mapean a `null` en `IndustryToCatalogoNombre` → `EstadoEmbudo.DerivadoManual`, sin excepción ni bloqueo. Comportamiento esperado, no error — riesgo #2 del implementador validado como correcto. |
| HU-05 (notificación a Joaquín, CU-05) | CA1: notificación in-app (campanita) | **FAIL** | Ver defecto **CRM-006** (severidad major): `INotificationService` nunca se inyecta ni se llama desde `BotFlowService`. Solo se implementó el canal WhatsApp. No depende de credenciales — 100% verificable y reproducible por código. |
| HU-05 | CA2: mismo resumen por WhatsApp a admin | **PASS (código)** / **BLOCKED (E2E real)** | `SendBriefToAdminAsync` arma y envía el brief correctamente; envío real bloqueado por falta de credenciales. |
| HU-06 (derivación manual, CU-06) | CA1/CA2: aviso al lead + notificación a Joaquín | **PASS parcial (código)** | Mensaje al lead (`MsgClosing`) correcto. Notificación a Joaquín solo por WhatsApp (mismo gap que HU-05/CRM-006 — el brief se manda igual en la rama `DerivadoManual`). |
| HU-07 (outbound diario, CU-10) | CA1/CA2/CA3: cronograma por rubro, límite diario, follow-up 7d, frío 4d | **PASS (código)** | `OutboundCampaignService`/`OutboundSchedulerService` replican el cronograma, límites y ventanas de tiempo tal cual el legacy. Arranca en `Standby=true` (esperado). No ejecutable en vivo sin credenciales de WhatsApp — se puede invocar manualmente `IOutboundCampaignService` para validar la mecánica sin enviar mensajes reales una vez haya credenciales. |
| HU-08 (Google Maps, CU-11) | CA1: resultados cargan como Contacto (Canal=OutboundFrío) | **PASS (código)** / **BLOCKED (E2E, sin ApiKey)** | `BotController.BuscarProspectos` arma el `Contacto` con el canal correcto. |
| HU-08 | CA2: no duplica por teléfono | **FAIL condicional** | Ver defecto **CRM-004** (severidad major): el chequeo de duplicado solo mira la DB, no los duplicados dentro del mismo batch en memoria; un `SaveChangesAsync()` único al final puede tirar `DbUpdateException` sin manejar y perder todo el lote si dos resultados del mismo rubro comparten teléfono (escenario plausible en Google Places). `OutboundSchedulerService` sí maneja este caso correctamente (guarda incremental + catch) — inconsistencia entre las dos implementaciones del mismo patrón. |
| HU-09 (catálogo industrias, CU-12) | CA1: cambio de precio se refleja sin redeploy | **PASS (código)** | `ResolveIndustriaCatalogoAsync` consulta la tabla en cada cálculo, sin caché. |
| HU-09 | CA2: no permite `CotizaAutomatico=true` sin precio | **PASS** | `ValidatePrecioSiCotizaAutomatico` en `IndustriasController` (Create y Edit) — validación server-side presente además de `[Range]` en el ViewModel. |
| HU-10 (panel scheduler, CU-Bot) | CA1: panel muestra enviados/pendientes/estado igual que `/outbound/status` | **PASS (código)** | `GetStatsAsync` calcula por `COUNT` sobre `Contacto`, consistente con el reemplazo de `CampaignState` descrito en Análisis §3. |
| HU-10 | CA2: pausar/reanudar con confirmación + queda en auditoría | **FAIL** | Confirmación SweetAlert2 sí está. Pero ver defecto **CRM-001** (severidad major): `TogglePausa` no persiste ningún registro en `AuditLog` — el toggle es un flag estático en memoria, nunca pasa por `AppDbContext.SaveChanges` (único disparador del audit trail automático). Coincide con la prueba mínima #7 que el propio implementador dejó pendiente de verificar. |
| HU-11 (cambio de estado manual, CU-Contacto) | CA1: selector solo ofrece estados posteriores a Respondido, no permite volver a Pendiente | **PASS** | `EstadosManualesPermitidos` = exactamente `[DemoSolicitada, DemoRealizada, PropuestaEnviada, Cerrado, Descartado]`, coincide con Diseño §3. Controller valida ambos lados (whitelist + policy `RequireAdministracion`). |
| HU-11 | CA2: `Descartado` pide confirmación explícita | **PASS** | `Details.cshtml` diferencia el texto/color del SweetAlert2 cuando `nuevoEstado === 'Descartado'`. |
| HU-11 (implícito, Diseño §4) | Vendedor no debe ver la opción de cambiar estado | **FAIL** | Ver defecto **CRM-002** (severidad minor): el control se renderiza sin gate de rol en la vista, pese a que el controller sí bloquea la acción (`RequireAdministracion`). Defensa en profundidad rota solo del lado de la vista — no es un agujero de seguridad (el servidor igual rechaza), pero expone al Vendedor un control que va a fallarle. |

### 2. Cobertura de máquina de estados — `FaseConversacion`

Todas las transiciones de la tabla del Diseño §3 recorridas por revisión de código:

| Origen → Evento → Destino | Resultado |
|---|---|
| (sin conv.) + outbound conocido → `AskingQuestions` | PASS |
| (sin conv.) + sin outbound → `AwaitingCategory` | PASS |
| `AwaitingCategory` + "1" → `AwaitingIndustry` | PASS |
| `AwaitingCategory` + "2"/"3" → `AskingQuestions` | PASS |
| `AwaitingCategory` + texto libre no reconocido → `Completed` (Categoria=other) | PASS |
| `AwaitingIndustry` + rubro reconocido (1-8) → `AskingQuestions` | PASS |
| `AwaitingIndustry` + texto libre no reconocido → `AskingQuestions` (Categoria=rent_other esperado) | **FAIL** — ver **CRM-005** (minor): solo asigna `rent_other` si el texto es exactamente "Otro rubro"; cualquier otro texto libre no listado cae a `rent` en vez de `rent_other` como especifica la tabla de Diseño. |
| `AskingQuestions` + responde, quedan preguntas → `AskingQuestions` | PASS |
| `AskingQuestions` + última pregunta → `Completed` | PASS |
| `Completed` + <24h → `Completed` (sin cambio, reenvía extra a admin) | PASS |
| `Completed` + ≥24h → `Nuevo` → reinicia | PASS (conserva historial de `ContactoRespuesta` previo, como pide el Diseño) |

**Cobertura: 10/11 transiciones PASS, 1/11 FAIL (defecto menor, cosmético en el guion de preguntas, no rompe el flujo).**

### 3. Cobertura de máquina de estados — `EstadoEmbudo`

| Origen → Evento → Destino | Resultado |
|---|---|
| `Pendiente` + scheduler corre en día del rubro + cupo disponible → `MensajeEnviado` | PASS (código) / BLOCKED (E2E) |
| `Pendiente` + error API Meta → queda `Pendiente` | PASS (try/catch en `SendDailyBatchAsync`, no cambia estado en la rama de error) |
| `MensajeEnviado` + ≥7 días sin respuesta + día programado → `FollowUpEnviado` | PASS |
| `FollowUpEnviado` + ≥4 días sin respuesta → `Frio` | PASS |
| `MensajeEnviado`/`FollowUpEnviado`/`Pendiente` + responde → `Respondido` | PASS |
| `Respondido` + Completed con industria que cotiza → `PresupuestoEnviado` | PASS |
| `Respondido` + Completed sin cotización → `DerivadoManual` | PASS |
| Manual (Administrador) → `DemoSolicitada`/`DemoRealizada`/`PropuestaEnviada`/`Cerrado`/`Descartado` | PASS (lógica) / **FAIL parcial de UI** (ver CRM-002, visible también para Vendedor) |
| Manual → intento de volver a `Pendiente` (transición inválida) | PASS — `EstadosManualesPermitidos` no incluye `Pendiente`, rechazado con mensaje claro |
| Manual → intento de estado no permitido (ej. `MensajeEnviado` inyectado por POST directo) | PASS — whitelist rechaza cualquier valor fuera de la lista, incluso valores de enum no definidos |

**Cobertura: 10/10 transiciones núcleo PASS a nivel de lógica de negocio. El único FAIL de esta máquina es de superficie (UI), no de la máquina de estados en sí.**

### 4. Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica (si/no/N/A) | resultado | acción |
|---|---|---|---|
| REG-001 (RowVersion MySQL) | N/A | — | `SoftDestroyable` no define ningún token de concurrencia (`RowVersion`); ninguna entidad de este proyecto lo usa. No aplicable al stack actual. |
| REG-002 (stock inicial variantes) | N/A | — | Sin módulo de Variantes/Stock en este alcance. |
| REG-003 (autocomplete Compras) | N/A | — | Sin módulo de Compras. El único combo remoto-simil (`Rubro` en Contactos) es un Select2 con lista estática en página + `tags:true`, no AJAX. |
| REG-004 (máquina de estados Compra desalineada con UI) | Sí (patrón) | FAIL (equivalente encontrado) | Mapeado a la UI de `EstadoEmbudo`/`Contactos/Details` → ver **CRM-002**. |
| REG-005 (autocomplete Ventas) | N/A | — | Sin módulo de Ventas. |
| REG-006 (medio de pago Cuotas) | N/A | — | Sin módulo de pagos/cuotas. |
| REG-007 (autocomplete Devoluciones) | N/A | — | Sin módulo de Devoluciones. |
| REG-008 (input pierde foco en re-render de grilla) | N/A | — | Ninguna vista de este alcance re-renderiza una grilla de inputs dinámica en cada keystroke. |
| REG-009 (cascada de combos rota) | N/A | — | No hay combos en cascada (Categoría→Subgrupo o equivalente) en este alcance. |
| REG-010 (link de menú visible para rol sin permiso) | Sí | PASS | Sidebar (`_Layout.cshtml`) gatea correctamente Contactos (Vendedor+), Industrias/Bot (Administrador+), Auditoría (SuperUsuario) — revisado línea a línea, sin regresión. |
| KOI-001 (botón SweetAlert2 fuera del form, `closest('form')` falla) | Sí | PASS | `Contactos/Details` (Cambiar estado), `Bot/Index` (TogglePausa) usan botón `type="button"` **dentro** del `<form>` correspondiente + `trigger('submit')`. `Industrias/Index` (Delete) arma un `<form>` dinámico vía JS con el token antiforgery. Los 3 patrones funcionan correctamente, sin el bug de KOI-001. |
| KOI-002 (export Excel faltante) | N/A | — | Sin requerimiento de exportación en este alcance. |
| KOI-003 (rol sin acceso a una vista que debería ver) | Sí (patrón inverso) | FAIL (equivalente encontrado) | Encontrado el caso inverso: un rol ve un control que NO debería (Vendedor ve "Cambiar estado") → ver **CRM-002**. |
| KOI-004 (validación de negocio ausente, permite estado inválido) | N/A | — | Sin flujo de consumos/liquidación en este alcance. |
| KOI-005 (link de sidebar sin controller → 404) | Sí | PASS | Verificado que `ContactosController`, `IndustriasController`, `BotController` existen y responden a las rutas que referencia `_Layout.cshtml`. Sin 404 potencial detectado. |
| KOI-006 (mismo patrón, otro controller) | Sí | PASS | Cubierto por la misma verificación que KOI-005. |
| DN-001 / DN-002 (crash de provider EF6-MySQL legacy con Include+OrderBy dinámico+Skip/Take) | N/A | — | El proyecto usa el provider EF Core moderno (`MySql.EntityFrameworkCore`, ver migración), no `MySql.Data.EntityFramework` (discontinuado). Causa raíz no aplica a este stack. `ContactosController.GetData` ni siquiera implementa OrderBy dinámico (ver CRM-003, problema opuesto: falta de sort dinámico, no crash por combinarlo). |
| GAN-001 (guard "al menos un pago" no se dispara) | N/A | — | Sin grilla de pagos múltiples en este alcance. |
| GAN-002 (backfill sin FechaVencimiento en dato histórico) | N/A | — | Sin entidad Egreso/backfill de datos históricos en este alcance. |
| GAN-003 (`<script type="text/x-template">` con `<partial>` adentro, Razor no lo procesa) | Sí (patrón revisado) | PASS | Ninguna vista de este alcance usa grillas dinámicas de filas con plantillas embebidas en `<script>`; no hay patrón para reproducir el bug. |
| GAN-004 (quirk de `<datalist>` nativo) | N/A | — | Ninguna vista usa `<datalist>`; los combos de este alcance son `<select>`/Select2. |
| VSF-001 (FK a estado terminal bloquea operación) | N/A | — | `Rubro` en `Contacto` es texto libre, no FK a `IndustriaCatalogo` (decisión explícita de Diseño §4) — no puede replicarse el patrón de bloqueo por FK a un estado terminal. |
| VSF-002 (transición faltante en diccionario de máquina de estados) | Sí (patrón revisado) | PASS | `EstadosManualesPermitidos` fue comparado campo a campo contra la tabla de Diseño §3 — no falta ninguna transición manual documentada. |
| **CRM-001** (nuevo) | Sí | **FAIL** | TogglePausa no genera `AuditLog`. Ver defecto abajo. |
| **CRM-002** (nuevo) | Sí | **FAIL** | Selector "Cambiar estado" visible para Vendedor. Ver defecto abajo. |
| **CRM-003** (nuevo) | Sí | **FAIL** | Ordenamiento de columna ignorado en `GetData` de Contactos/Industrias. Ver defecto abajo. |
| **CRM-004** (nuevo) | Sí | **FAIL** | `BuscarProspectos` sin manejo de duplicado dentro del mismo batch. Ver defecto abajo (BLOCKED para prueba E2E real, PASS/FAIL de código ya confirmado FAIL). |
| **CRM-005** (nuevo) | Sí | **FAIL** | `AwaitingIndustry` con texto libre no asigna `rent_other`. Ver defecto abajo. |
| **CRM-006** (nuevo) | Sí | **FAIL** | Notificación in-app nunca se crea. Ver defecto abajo. |

### 5. Defectos detectados (severidad y pasos)

Los 6 defectos nuevos quedaron catalogados en `docs/qa/regresiones-manuales.yml` (ids `CRM-001` a `CRM-006`) siguiendo el formato obligatorio (pasos, síntoma, expectativa, causa raíz, archivos de fix sugeridos, criterio de aceptación, pruebas mínimas). Resumen:

| id | Severidad | Módulo | Resumen | Bloqueado por credenciales |
|---|---|---|---|---|
| CRM-001 | major | Bot/Outbound (`TogglePausa`) | Pausar/reanudar no genera `AuditLog` (HU-10 CA2 incumplida) | No — reproducible sin credenciales |
| CRM-002 | minor | Contactos/Details | Selector "Cambiar estado" visible para Vendedor (servidor sí lo bloquea; solo falta el gate en la vista) | No |
| CRM-003 | minor | Contactos/Index, Industrias/Index | Click en encabezado de columna no reordena (falta soporte de `order[0][column]` en `GetData`) | No |
| CRM-004 | major | Bot/Index (`BuscarProspectos`, CU-11/HU-08) | Sin manejo de `DbUpdateException` por duplicado dentro del mismo batch de Google Maps (a diferencia de `OutboundSchedulerService`, que sí lo maneja) | Sí para prueba E2E real (falta `Olvidata_GoogleMaps:ApiKey`); el hallazgo en sí es de código, no bloqueado |
| CRM-005 | minor | Bot — `BotFlowService.OnIndustryInputAsync` | Rubro no reconocido no asigna `Categoria=rent_other` como pide la tabla de Diseño | Sí para prueba E2E real; hallazgo de código no bloqueado |
| CRM-006 | major | Bot — `BotFlowService.SendBriefToAdminAsync` | Notificación in-app (campanita) nunca se crea — solo se implementó el canal WhatsApp (HU-05 CA1 incumplida) | No — es un INSERT en BD, no depende de WhatsApp/Google Maps |

**Ningún defecto fue auto-corregido en esta pasada.** Ninguno de los 6 estaba catalogado antes de esta sesión y, por instrucción explícita del orquestador para esta tarea ("si no está catalogado o la causa raíz es ambigua, no adivinés — documentalo como defecto para que el Implementador lo resuelva en otra pasada"), se optó por documentar + catalogar en vez de aplicar parches sin una pasada de Implementador dedicada, aun cuando la causa raíz de cada uno es clara y no ambigua. Los 6 quedan con `archivos_fix` sugeridos (marcados "PENDIENTE DE AUTORIZACIÓN") para que el Implementador los aplique en la próxima pasada.

### 6. Validación de los 3 riesgos señalados por el implementador

1. **Cálculo automático de presupuesto (CU-04), código nuevo sin precedente:** revisado línea a línea (`BotFlowService.CompleteAsync`/`ResolveIndustriaCatalogoAsync`/`UsuariosIncluidosPorPlan`) contra las 13 industrias sembradas — el mapeo de nombres y el cálculo de excedente por usuario son correctos. **No se encontró bug en la lógica de cálculo en sí.** Riesgo mitigado a nivel de código; queda pendiente la prueba E2E real (BLOCKED por credenciales).
2. **"Farmacia" y "Contabilidad/Estudios contables" sin cotización automática:** confirmado que es una decisión intencional y correctamente implementada (`IndustryToCatalogoNombre` devuelve `null` para ambas → `EstadoEmbudo.DerivadoManual`, sin excepción). El comportamiento es "derivación manual, no error", como se esperaba. **PASS.**
3. **Credenciales reales de WhatsApp/Google Maps ausentes:** confirmado en `appsettings.json` (`Olvidata_WhatsApp:AccessToken`, `Olvidata_GoogleMaps:ApiKey`, `Olvidata_Bot:VerifyToken` todos vacíos). Todos los casos E2E reales del bot/outbound/Google Maps quedan **BLOCKED**, marcados así explícitamente (no como FAIL) en toda esta memoria.

### 7. Procedimiento de prueba manual (para Joaquín — casos UI no bloqueados por credenciales)

Los siguientes casos **no** dependen de WhatsApp/Google Maps y se pueden ejecutar hoy mismo contra `olvidatacrm_dev`. Reportar PASS/FAIL por caso.

**A. HU-01/CU-01 — Alta manual de contacto**
1. Login con el SuperUsuario (`no-reply@olvidata.com.ar` / `Super123!` salvo que se haya cambiado en `appsettings`).
2. Ir a Contactos → "Nuevo contacto". Completar Teléfono `5492211234567`, Nombre "Prueba QA", Negocio "Test SRL", Rubro (elegir de la lista o escribir uno libre), Guardar.
3. **Esperado:** redirige a Contactos/Index, aparece la fila nueva con Estado "Pendiente" y Canal "Manual".
4. Repetir el alta con el **mismo** teléfono `5492211234567`.
5. **Esperado:** el formulario NO guarda, muestra un mensaje de error mencionando que ya existe un contacto con ese teléfono y su Id/nombre (verificar si aparece como texto o como link — ver CRM-002/defecto de HU-01 CA1 arriba, se espera que hoy sea solo texto, no un link clickeable).

**B. HU-02/CU-02 — Filtros del listado**
1. En Contactos/Index, probar cada filtro por separado: Rubro, Canal, Estado, rango de fecha (Última actividad), buscador de texto libre (teléfono y nombre).
2. **Esperado:** cada filtro acota los resultados correctamente.
3. Click en el encabezado de la columna "Nombre" (o cualquier otra columna con flechas de orden).
4. **Esperado esta prueba (para confirmar CRM-003):** la flecha visual cambia pero el orden de las filas **no** cambia — confirmar que este es el comportamiento actual (reproduce el defecto).

**C. HU-09/CU-12 — Catálogo de industrias**
1. Login Administrador o SuperUsuario. Ir a Industrias → "Nueva industria".
2. Activar el switch "¿Cotiza automático?" sin cargar precio base y Guardar.
3. **Esperado:** error de validación bloqueante, no guarda.
4. Cargar un precio y guardar. Editar esa industria y bajar el precio. Guardar.
5. **Esperado:** el cambio se refleja de inmediato sin redeploy (verificable comparando el valor mostrado en el listado antes/después).
6. Eliminar una industria de prueba (no una de las 13 sembradas) y confirmar el SweetAlert2.
7. **Esperado:** desaparece del listado (soft-delete), sin errores.

**D. HU-10 — Panel del scheduler + defecto CRM-001**
1. Login Administrador. Ir a Bot / Outbound.
2. Click en "Pausar outbound" (o "Reanudar"), confirmar el SweetAlert2.
3. **Esperado:** el badge de estado cambia (Activo ↔ En pausa).
4. Login SuperUsuario, ir a Auditoría, buscar un registro reciente relacionado con el toggle.
5. **Esperado esta prueba (para confirmar CRM-001):** NO aparece ningún registro nuevo en Auditoría para esa acción — confirma el defecto.

**E. HU-11/CU-Contacto — Cambio de estado manual + defecto CRM-002**
1. Login Vendedor (no Administrador/SuperUsuario). Ir a Contactos → Details de cualquier contacto.
2. **Esperado esta prueba (para confirmar CRM-002):** el selector "Cambiar estado (manual)" es visible pese a que el Vendedor no debería poder usarlo (confirma el defecto — el intento real de guardar debe fallar/redirigir, aunque el control se vea).
3. Login Administrador, repetir en el mismo contacto: elegir un estado (ej. "DemoSolicitada"), confirmar.
4. **Esperado:** el estado cambia, aparece el mensaje de éxito, y el badge de Estado en Details se actualiza.
5. Elegir "Descartado" y confirmar.
6. **Esperado:** el SweetAlert2 muestra el texto de advertencia específico de descarte antes de confirmar.

**F. Permisos — Empleado y Vendedor**
1. Si existe un usuario con rol Empleado, login y verificar que no aparece ningún link de "Contactos"/"Industrias"/"Bot / Outbound" en el sidebar, y que navegar directo a `/Contactos`, `/Industrias`, `/Bot` devuelve error de acceso.
2. Login Vendedor: confirmar que ve "Contactos" en el sidebar pero NO ve "Industrias" ni "Bot / Outbound".

### 8. Riesgos de liberación y mitigaciones

- **HU-05 (notificación in-app) no implementada (CRM-006, major):** si se libera así, Joaquín depende 100% de que el mensaje de WhatsApp llegue — sin campanita de respaldo dentro del CRM. Mitigación: no requiere nueva lógica de negocio, solo inyectar el servicio ya existente; recomendado resolver antes de activar el scheduler en producción (`Standby=false`).
- **HU-10 sin registro de auditoría del toggle (CRM-001, major):** en un sistema de un solo operador (Joaquín) el impacto de negocio es bajo hoy, pero rompe la trazabilidad si en el futuro hay más de un Administrador operando el bot. Mitigación: fix acotado y de bajo riesgo (insert manual en `AuditLog`, patrón ya usado en el resto de la base).
- **CRM-004 (duplicado en batch de Google Maps sin manejar):** riesgo de negocio real una vez se cargue la ApiKey — puede perder un batch completo de prospección por un solo duplicado. Mitigación: mismo patrón ya resuelto en `OutboundSchedulerService`, portarlo también a `BotController.BuscarProspectos` antes de la primera corrida real con datos.
- **Corte de producción de BotPublicitario:** no se tocó en esta sesión (confirmado fuera de alcance, según runbook de Arquitectura §5). BotPublicitario sigue operando sin cambios — sin riesgo de este ciclo de QA.
- **Bloqueo de pruebas E2E reales:** persiste hasta que Joaquín cargue `Olvidata_WhatsApp`/`Olvidata_GoogleMaps`/`Olvidata_Bot:VerifyToken`. Recomendado no activar `Standby=false` en producción hasta cerrar CRM-001, CRM-004 y CRM-006 (los 3 `major`).

### 9. Pruebas mínimas ejecutadas por este QA

- Recompilación completa de la solución (`dotnet build OlvidataCRM.slnx`) — 0 errores confirmado independientemente del reporte del implementador.
- Verificación de migraciones aplicadas (`dotnet ef migrations list`) contra `olvidatacrm_dev`.
- Revisión de código línea a línea de: `BotFlowService.cs`, `OutboundCampaignService.cs`, `OutboundSchedulerService.cs`, `GoogleMapsService.cs`, `ContactosController.cs`, `IndustriasController.cs`, `BotController.cs`, `AppDbContext.cs`, `SeedData.cs`, `Program.cs` (webhook + policies), todos los ViewModels y Views de Contactos/Industrias/Bot, `_Layout.cshtml`, migración EF generada.
- Recorrido completo de las 11 transiciones de `FaseConversacion` y las 10 transiciones núcleo de `EstadoEmbudo` contra las tablas de Diseño §3.
- Ejecución del playbook cross-proyecto completo (24 items preexistentes + 6 nuevos) con mapeo de aplicabilidad módulo por módulo.
- Validación puntual de los 3 riesgos señalados por el implementador.

**No ejecutado (fuera del alcance de este agente o bloqueado):** pruebas automatizadas de navegador (regla del estudio: QA nunca automatiza UI), pruebas E2E reales contra Meta WhatsApp Graph API / Google Maps Places API (sin credenciales), corrida real del scheduler outbound en horario de producción.

### 10. Estado go/no-go

**NO-GO para producción con `Standby=false` / uso comercial real hasta resolver los 3 defectos `major` (CRM-001, CRM-004, CRM-006).**

**GO condicional para continuar usando el CRM en modo interno/QA manual** (Contactos/Industrias CRUD, sin bot/outbound activos) — esos flujos no dependen de los defectos encontrados y están operativos.

Condiciones para pasar a GO completo:
1. Implementador aplica fix de CRM-001 (audit log del toggle), CRM-004 (manejo de duplicado en batch de Maps) y CRM-006 (notificación in-app) — los 3 `major`.
2. Joaquín carga credenciales reales de `Olvidata_WhatsApp`/`Olvidata_GoogleMaps`/`Olvidata_Bot:VerifyToken`.
3. Nueva pasada de QA ejecuta las pruebas E2E hoy BLOCKED (HU-03 a HU-08) contra credenciales reales, en la ventana de desarrollo aparte (sin tráfico de producción), antes del runbook de corte de BotPublicitario.
4. CRM-002, CRM-003, CRM-005 (los 3 `minor`) pueden resolverse en la misma pasada o en un ciclo posterior sin bloquear el go-live — no afectan la operación comercial del bot, solo UX/consistencia.

## Re-verificación post-corrección — CRM-007 / CRM-010 / CRM-012 (2026-08-27, misma fecha)

Pasada **acotada** sobre la corrección del Implementador (`5-implementador.md` §9). No se re-ejecutaron los 17 items del sprint: solo los 2 hallazgos bloqueantes, el riesgo que el Implementador declaró y un smoke de regresión. **CRM-008 queda descartado por el cliente** (la migración `AddMensajeProgramado` sí está aplicada en producción; la pasada anterior probó contra `olvidatacrm_dev` y confundió las bases) — no se re-verificó.

**Método:** `dotnet build -c Release --no-incremental` propio → **0 errores, 13 advertencias** (idénticas a las preexistentes). App levantada contra `olvidatacrm_dev` (`https://localhost:5443`, `ASPNETCORE_ENVIRONMENT=Development`), autenticada como SuperUsuario, ejercitada por HTTP real. Cada número que devuelve un endpoint fue contrastado contra una **consulta SQL independiente** escrita por este QA — no contra lo que el propio endpoint informa. MCP `playwright` **no disponible** en esta sesión (declarado según `33-verificacion-automatizada-qa.instructions.md`); sustituido por HTTP + assertions sobre la BD. Estado de dev **restaurado y verificado** al terminar (436 contactos, 14 industrias, 54 industrias de campaña). **Ningún archivo de código modificado por QA** (`git status` = 36, idéntico al inicio).

### R1. CRM-007 — conteo y reasignación por `ClaveRubro` → **PASS**

`ImpactoDelete` contrastado contra ground truth SQL propio para **las 14 industrias del catálogo, no solo las 7 con datos**. Coincidencia exacta en las 14, incluida la lista de `claves`:

| Industria | endpoint | ground truth SQL | |
|---|---|---|---|
| #2 Retail / comercio minorista | 155 | 155 | ✔ |
| #5 Laboratorios / consultorios | 104 | 104 | ✔ |
| #9 Alquiler de inmuebles | 58 | 58 | ✔ |
| #8 Utilities | 38 | 38 | ✔ |
| #6 Ganadería | 35 | 35 | ✔ |
| #16 Estudios contables | 28 | 28 | ✔ |
| #15 Farmacias | 1 | 1 | ✔ |
| #4, #7, #10, #11, #12, #13, #14 | 0 | 0 | ✔ (7 industrias sin `ClaveRubro` asociada — el 0 es la respuesta correcta) |

Los 54 `CampanaOutboundIndustria` de dev tienen `IndustriaCatalogoId` poblado, así que **el camino de respaldo por mapeo clave→industria→catálogo no se ejercitó** — sigue sin cobertura empírica, tal como el Implementador declaró.

**Reasignación real, probada end-to-end sobre la industria #15 (Farmacias, 1 contacto):**
- Destinos ofrecidos = **ClaveRubro de campañas activas**, no nombres de catálogo. Para #9: 23 opciones = 26 claves activas − 3 propias que este borrado deja huérfanas. Aritmética verificada contra SQL.
- **Rama negativa:** `POST /Industrias/Delete/15` con `reasignarA=E-commerce / tiendas online` (un `Nombre` de catálogo) → **rechazado**, mensaje *"no pertenece a ninguna campaña activa. No se eliminó nada."* renderizado en `/Industrias`; en BD el contacto **y la industria quedan intactos** (la guarda aborta antes del soft-delete).
- **Rama positiva:** mismo POST con `reasignarA=estudio-palermo` → contacto #158 pasó de `farmacia` a **`estudio-palermo`**, con `UpdatedAt` y `UpdatedByUserId = 6cdb16cd-7a0c-4879-a4a2-0a8051d63706` (GUID real del SuperUsuario — el stamping manual de `ExecuteUpdateAsync` sigue correcto, patrón G6), e industria #15 soft-deleteada.
- **Cierre del círculo (lo que M-B nunca lograba antes):** el contacto reasignado quedó cubierto por la campaña **activa #35 "Estudio Palermo"** — verificado con un JOIN directo. Ya no queda huérfano. Datos restaurados.

### R2. CRM-010 — el selector guarda la clave real → **PASS**

`Contactos/Create` renderiza el `<select name="Rubro">` en 2 `optgroup` ("Con campaña activa…" / "Sin campaña activa…") con `value` = **ClaveRubro** (`estudio-palermo`, `agro-nortebsas`, `comercio-microcentro`…), no nombres de catálogo.

Alta real con canal **Referido**: contacto #442 creado con `Rubro=estudio-palermo`, `CanalOrigen=3`, `EstadoEmbudo=Pendiente`. Assertion decisiva en BD: ese contacto **satisface el filtro completo de `SendDailyBatchAsync`** (`EstadoEmbudo=Pendiente` + `CanalOrigen IN (OutboundFrio, Referido)` + `Rubro` ∈ claves de campaña activa) y matchea la campaña activa #35. B7 ahora sí entra al circuito.

`Edit` verificado en 3 contactos: conserva el rubro actual como opción seleccionada incluso cuando ninguna campaña lo alcanza (#236 `Inmuebles / Real estate`, #128 `restaurant`), y **editar otro campo no pisa el rubro** (POST sobre #442 cambiando `NombreNegocio` → `Rubro` intacto). Contacto de prueba eliminado.

### R3. CRM-012 — `Alineadas` es una alerta real → **PASS**

`Alineadas` dejó de ser un campo con setter: es propiedad calculada sobre `PorPantalla`, sin forma de fijarla a mano. Los 3 valores que compara son los reales de cada pantalla, **verificados uno por uno contra SQL independiente**: Bot/Outbound 0/19, Contactos/Pipeline 0/19, Campañas/Dashboard 0/18 — las 4 cifras coinciden con mis queries.

Aunque no era exigido, **se forzó una divergencia real** para probar que la alerta dispara: se cargó `PresupuestoCotizadoUsd` en el único contacto que está en el universo de Bot/Pipeline pero no en el de Dashboard (#194) → las tasas pasaron a **5,3% / 5,3% / 0,0%**, el badge cambió a **`bg-danger` "Divergen"** y se renderizó el `alert alert-danger`. Restaurado; badge de vuelta en "Alineadas".

**Observación (menor, no bloqueante):** `Alineadas` compara únicamente la **tasa**, no los denominadores. Hoy las 3 pantallas informan 0,0% con denominadores 19/19/**18**, así que el badge dice "Alineadas" pese a que el universo de Campañas/Dashboard sigue siendo más angosto (la divergencia de B6). Es defendible —la tasa es el número que el usuario ve— y la diferencia queda visible en la columna de denominador de la tabla nueva, que es justo lo que la pasada anterior pedía. No es regresión.

### R4. Riesgo declarado por el Implementador (contactos con Rubro reescrito por el bot) → **CONFIRMADO, con una salvedad**

**Confirmado para el caso descrito.** Los 2 contactos de dev cuyo `Rubro` fue reescrito por `BotFlowService` al nombre de industria del diálogo — #236 (`Inmuebles / Real estate`) y #194 (`Otro rubro`), ambos `FaseConversacion=Completed` con 3 respuestas cada uno — **no son contados ni alcanzados por la reasignación**: `ImpactoDelete/9` devuelve 58 (las claves `inmobiliaria*`) y no 59. El `Delete` sólo hace `UPDATE … WHERE Rubro = <clave>` por cada `ClaveRubro`, y ningún nombre de industria del diálogo es una `ClaveRubro`, así que esos contactos son inalcanzables por construcción. Reasignarlos habría roto su conversación; no ocurre.

**Salvedad que hay que dejar dicha: la protección es incidental, no una guarda explícita.** Depende de que el bot haya reescrito el rubro. Los contactos que conversaron pero conservan su `ClaveRubro` **sí quedan dentro del conteo y de la reasignación**. Medido en dev: de los 419 contactos contados por `ImpactoDelete`, **401 están en `Nuevo`** (nunca hablaron, correcto), pero **18 tienen conversación**:

| Fase | n | estado | industrias afectadas |
|---|---|---|---|
| `AwaitingCategory` (2) | 17 | `Respondido`, los 17 con envío y con respuesta — **conversación en curso** | Retail 9, Utilities 4, Ganadería 3, Estudios 2 |
| `Completed` (5) | 1 | contacto #7 (`estudio`), conversación cerrada el 2026-07-16 | Estudios contables |

Si el SuperUsuario borrara Retail / Utilities / Ganadería / Estudios con reasignación, esos 18 cambiarían de rubro; los 17 en `AwaitingCategory` están esperando respuesta y pasarían a resolver otra industria al contestar. **No es un defecto introducido por esta corrección** (antes del fix el conteo daba 0 para todo, así que tampoco había protección — sólo que no reasignaba a nadie) y la acción es deliberada, detrás de un modal de confirmación. Pero el comentario del código afirma sin matices *"NO se cuentan los contactos que ya conversaron con el bot"*, y eso **no es exacto**: no se cuentan los que además tuvieron el rubro reescrito. Queda como **CRM-014 (minor)**.

Detectada además una colisión latente de vocabulario, sin impacto hoy: la clave `farmacia` y el nombre de industria del diálogo `"Farmacia"` difieren sólo en mayúscula, y tanto la comparación en memoria (`OrdinalIgnoreCase`) como el `UPDATE` en MySQL (collation case-insensitive) las tratan como iguales. Es el **único** par de los 17 mapeos donde eso puede pasar (el resto son frases multi-palabra). Hoy hay 0 contactos con `Rubro='Farmacia'`, así que no afecta a nadie. Anotado dentro de CRM-014.

### R5. Regresión / smoke → **PASS**

18 pantallas cargadas autenticado, **todas 200** (`/` 302 al dashboard, normal): `/Industrias`, `/Industrias/Create`, `/Contactos`, `/Contactos/Create`, `/Contactos/Edit/158`, `/Contactos/Details/158`, `/Contactos/Pipeline`, `/Bot`, `/Bot/Salud`, `/Campanas`, `/Campanas/Dashboard`, `/Chats`, `/Chats/Detail/7`, `/Templates`, `/Clientes`, `/Negocio/Dashboard`, `/Notifications`. Las 2 vistas tocadas renderizan bien: el modal de `Industrias/Index` arma el `<option>` con `value=a.valor` (la clave) y muestra `a.etiqueta`, coherente con lo que valida el `Delete`. **0 errores en el log de Serilog durante la sesión** (la única entrada del día es un `HostAbortedException` de las 00:35, de tooling EF, previo a esta pasada). **0 migraciones EF** en la corrección; `dotnet ef migrations list` sin pendientes.

Nota de entorno: cargar `/Chats/Detail/7` en el smoke estampó `UpdatedAt`/`UpdatedByUserId` en el contacto #7 — es el marcado de lectura documentado (G5/G6), no un efecto de estos cambios. Ningún `Rubro` fue alterado.

### R6. Defectos

| id | severidad | estado |
|---|---|---|
| CRM-007 | major (era bloqueante) | **CERRADO** — verificado en las 14 industrias + reasignación real en ambas ramas |
| CRM-010 | medium | **CERRADO** — verificado con alta real de Referido que entra al lote |
| CRM-012 | minor | **CERRADO** — alerta real, probada disparando una divergencia forzada |
| CRM-008 | — | **descartado por el cliente** (falsa alarma: la migración sí está en producción) |
| CRM-009, CRM-011, CRM-013 | medium/minor | **abiertos**, fuera de esta corrida por decisión explícita |
| **CRM-014** (nuevo) | **minor** | La exclusión de contactos en conversación es incidental (depende de que el bot haya reescrito el rubro), no una guarda explícita: 18 contactos con conversación siguen dentro del conteo/reasignación. Incluye la colisión `farmacia`/`"Farmacia"` por case. Documentación del código imprecisa. No bloquea. |

### R7. Estado go/no-go

**GO para deploy de producción.** Los 2 bloqueantes del NO-GO anterior están cerrados y verificados contra datos reales, no contra la palabra del endpoint: CRM-007 con coincidencia exacta en las 14 industrias y la reasignación cerrando el círculo hasta una campaña activa, CRM-010 con un Referido que efectivamente entra al lote. CRM-008 era falsa alarma de la pasada anterior. Build en Release 0 errores, 0 migraciones nuevas, 18 pantallas sin 500, sin errores en log.

Condiciones de liberación (ninguna bloqueante):
1. El selector de Rubro cambia visiblemente para el SuperUsuario (claves con sufijo de región en vez de 16 nombres de catálogo) — **avisarle antes del deploy**, no es un bug.
2. `Alineadas` puede dar **false** en producción por la divergencia de universo de Campañas/Dashboard: es la alerta funcionando, no una regresión.
3. CRM-014 y los 3 defectos abiertos (CRM-009/011/013) para un ciclo posterior.
4. El camino de respaldo por mapeo (campañas sin `IndustriaCatalogoId`) sigue sin cobertura empírica: si producción tiene filas con esa FK en null, conviene mirar el primer `ImpactoDelete` post-deploy antes de confirmar un borrado.

## QA — feature "4 frentes — combo con gancho" E1-E7 (2026-09-14)

### F0. Alcance, método y seguridad

- **Alcance:** CU-30 a CU-35 (`1-analista-funcional.md`), diseño §8, arquitectura §7.2 (pruebas 7.2.10), los 14 puntos de §8 y los 11 desvíos de `5-implementador.md`. Código sin commitear, migración `AddGanchoYFrenteComercial` solo en `olvidatacrm_dev`.
- **Seguridad:** dev tiene credenciales **reales** de Meta y Places en user-secrets, y el outbound estaba despausado (26 campañas activas, 234 Pendiente copiados de producción). Durante la corrida: `OutboundPausado=1`/`BusquedaMapsPausada=1`; app levantada con `Olvidata_WhatsApp__AccessToken`, `PhoneNumberId`, `Olvidata_GoogleMaps__ApiKey` y `AdminNotifyPhone` inválidos por variable de entorno; lote, follow-up, frío, webhook e IA ejecutados con un **harness de consola** (DI real de `AddInfrastructure` + `IWhatsAppClient` falso que registra lo que se habría mandado + cada escenario en transacción con **rollback**). Resultado: **0 mensajes de WhatsApp, 0 llamadas a Places, IA real 7 mensajes / 14 requests / USD 0,149.**
- **Automatización:** Playwright MCP **no disponible** (el navegador del MCP no alcanza el host: `ERR_CONNECTION_REFUSED` en localhost y 127.0.0.1, `host.docker.internal` no resuelve). Se cubrió con HTTP autenticado (cookies + antiforgery) contra la app local, assertions SQL y el harness. Comparaciones "idéntico a antes" contra un **baseline HEAD (2ad3830)** en worktree temporal corriendo sobre la misma base.
- **Build propio:** `dotnet build -c Release --no-incremental` → 0 errores (antes y después del auto-fix).

### F1. Puntos obligatorios del Implementador

| # | Caso | Resultado | Evidencia |
|---|---|---|---|
| 1 | Cupo con salteados | **OK** | Cupo 2, 3 contactos sin plantilla adelante (2 Presencia web, 1 Consultas): salieron los 2 elegibles siguientes (Gestión auto y a mano); el sin-gancho quedó afuera por cupo. Salteados en `Pendiente`, sin `PlantillaPrimerContacto`, log "no se enviaron", `GanchosSinEnvio` y card de /Bot con "Esperando". |
| 2 | Regresión Gestión sin combo / sin gancho / Referido | **OK** | `olv_frio_v13` y `olv_frio_v12` por A/B (variantes A y B registradas), mismos parámetros que hoy; Referido primero con `olv_referido_v2`. Con combos configuradas: web/consultas/gestión salen con su combo sin A/B, admin no aprobada no sale. |
| 3 | Botón "Sí, contame más" + IA | **OK** | Presencia web → `landing` + "Partís de cero…"; Administración → `ai_agents`; Consultas → `chatbot`; Gestión → `rent` + matriz Build. **Sin gancho: texto idéntico byte a byte al baseline HEAD** (3 rubros). "No me interesa" → Descartado. Módulo genérico de Chatbots → pregunta 1 con módulos. IA: los 4 mensajes de CU-30 CA2 cambiaron a `chatbot`/`ai_agents`/`landing`/`rent`; pregunta de precio → sin precio + escalada; cliente actual pidiendo mejora → `escalar_a_humano` en el mismo mensaje; prospecto frío con sistema viejo → sin ofrecer Merge. Venta cruzada mencionada una sola vez (e2). |
| 4 | Fallbacks | **OK** | IA deshabilitada con `ai_agents`/`chatbot` en `ConversandoConIa` → sigue con la pregunta 2, sin re-presentarse. Categoría sin cuestionario → `DerivadoManual`, bot pausado, **1 sola notificación** tras 2 mensajes, nada al prospecto, sin excepción. `merge` histórico sigue su cuestionario. |
| 5 | Filtros Gancho / Interés | **OK** | Contactos `GetData`: cada valor coincide con SQL (sin 204, PW 235, rent+rent_other 2, other 2, sin clasificar 438); valores inválidos ignorados; **combinaciones sin coincidencias → 200 con 0 filas** (MH-001); orden por las 2 columnas; Session repuesta en Index y vaciada por "Limpiar"; columnas visibles = filtros. Chats: filtro + Session + `limpiar=1` + chip "Administración" en la fila. Base totalmente vacía no probada (no se borra dev); el camino MH-001 se cubre con resultados vacíos y no hay `Contains`/`StartsWith` en SQL (grep). |
| 6 | Plantillas | **OK** | Guardar válido persiste; 4 POST manipulados (combo de otro gancho, no aprobada, `olv_frio_v3` en Gestión, combo inexistente) → "No se guardó ninguna plantilla", config intacta; sin antiforgery 400. Templates: renombrar combo configurada → bloqueado con mensaje; editar texto sin renombrar → permitido; borrar → bloqueado; columna "Gancho Presencia web" en el listado; Salud no la lista como "sin campaña". |
| 7 | A1-a | **OK** | Presencia web 4d y Administración 6d → sin follow-up; Consultas 8d y Presencia web 7d+1h → `Frio`; Gestión 4d, sin gancho 4d y Gestión 8d → `olv_nurturing_v2`. `MarkColdAsync` global dentro de la transacción no tocó ningún contacto real. |
| 8 | Armar presupuesto solo Build | **OK tras auto-fix** | Checklist de 3 rubros (Retail, Estudios, Landing page): mismos módulos, flags, rangos y orden que HEAD (única diferencia: atributo `data-frentes="1"`). `Calcular` y `GenerarMensaje` **byte a byte iguales** a HEAD; CRM-015 sin regresión. **`frentes[]` NO bindeaba en el GET del checklist → defecto CRM-023**, corregido. En POST sí bindea (Calcular con `frentes[]=2` e ids de Build → 0 módulos). |
| + | Tabla `GanchoHelpers` | **OK** | 26 casos: vacía/null → Presencia web "Sin web"; `instagram.com/x`, `www.instagram.com/…`, `x.mitiendanube.com`, `sites.google.com/view/x`, `wixsite`, `maps.app.goo.gl`, `linktr.ee`, `mercadolibre` → Presencia web con el dominio; `modalu.com.ar` + estudio → Administración; + `consultorio-palermo` → Consultas; + comercio → Gestión; `netflix.com` (no confunde con `x.com`) → Gestión; "no tengo" / "localhost" → Presencia web "dirección no válida"; Ads/Manual/Referido → sin gancho. |
| + | Carga inicial "Asignar ganchos" | **OK** | 234 asignados, segunda corrida 0, sin antiforgery 400. |
| + | Contactos Create/Edit/Details | **OK** | Alta con cada rama de la tabla; gancho a mano con canal Manual → error; web inválida → error; gancho inválido → error. Edit: combo pre-poblado (a mano) o "Automático"; Automático recalcula al cambiar la web; guardar otro campo no mueve `FechaGancho`; aviso "Ya se le escribió…" en GET y mensaje "Ojo…" al guardar; histórico ya enviado sin gancho no recibe uno automático (desvío 3). Card Oferta en Details y Chats/Detail con textos correctos. |
| + | Módulos | **OK** | 84 módulos en Build tras migrar; filtro Frente (y valores inválidos ignorados) + Session + limpiar; Create default Build; Edit pre-seleccionado. |
| + | Ortografía / tildes de UI nueva | **OK** | Revisados los textos agregados en vistas, ViewModels, helpers y enums: sin faltas. Nombres de frente en inglés (Build, Landing, AI Agents, Chatbots) por diseño. |
| + | Consola del navegador limpia | **NO PROBADO** | Sin navegador disponible. Barrido estático KOI-B02: los ids que tocan los scripts nuevos no están bajo `@if`. Queda manual. |

### F2. Cobertura por criterio de aceptación

| CU | CA | Resultado | Nota |
|---|---|---|---|
| CU-30 | CA1 `ai_agents`/`chatbot` sí, `merge` no | PASS | `ClavesVigentes` y `CategoriasValidas` de la IA sin `merge` (verificado por reflexión); la tool usa ese enum. |
| CU-30 | CA2 los 4 mensajes | PASS | IA real, 4/4. |
| CU-30 | CA3 sin precios ni plazos | PASS | e5. |
| CU-30 | CA4 sin mejoras a frío / cliente actual escala | PASS | e6 y e7. |
| CU-31 | CA1-CA4 (reemplazados por la tabla de gancho del diseño 8.3/8.4) | PASS | Visible antes del envío (Contactos, Chats, /Bot), determinístico y puro. |
| CU-32 | CA1-CA4 | PASS | Combo por gancho, v13 intacta, no cae a otra plantilla, mismos payloads, cupo y presupuesto. |
| CU-33 | CA1, CA2, CA4, CA5 | PASS | Botón por gancho, cambio de categoría, fallback, módulos del frente. |
| CU-33 | CA3 guardas vigentes | PASS parcial | Baja y escalada por precio verificadas; detección de no-humano y las 7 guardas no se re-ejecutaron contra la IA (fuera del cambio, cuidando el tope de costo). |
| CU-34 | CA1, CA2 | PASS | Etiquetas legibles, filtros = columnas. |
| CU-35 | CA1 | PASS | Ninguna vía nueva asigna `merge`. |
| CU-35 | CA2 | PASS (sin datos) | Etiqueta "Mejoras en sistema Olvidata (discontinuado)" en helper y filtro; dev no tiene contactos con `merge`. |

### F3. Máquina de estados

- `FaseConversacion`: `ConfirmandoContinuar` + `seguir` → `AskingQuestions` con la categoría del gancho (4 ganchos + sin gancho) — PASS. `ConfirmandoContinuar` + `no_interesa` → `Descartado` — PASS. `ConversandoConIa` con IA caída → `AskingQuestions` si la categoría tiene cuestionario — PASS. `AskingQuestions` con categoría sin cuestionario → `DerivadoManual` + bot pausado (sin cambio de fase) — PASS. Texto libre con IA disponible → `ConversandoConIa` o `AskingQuestions`+`DerivadoManual` al escalar — PASS.
- `EstadoEmbudo`: `Pendiente` → `MensajeEnviado` con combo — PASS; `Pendiente` se mantiene para ganchos sin plantilla — PASS; `MensajeEnviado` → `Frio` a los 7 días para los 3 ganchos combo y nunca `FollowUpEnviado` — PASS; `MensajeEnviado` → `FollowUpEnviado` para Gestión/sin gancho — PASS. Transición inválida probada: combo con 3-6 días no recibe follow-up ni pasa a frío — PASS.

### F4. Cobertura del catálogo cross-proyecto (items relevantes a esta superficie; el resto sigue como en las corridas anteriores)

| id | aplica | resultado | acción |
|---|---|---|---|
| MH-001 (Contains de lista / StartsWith / EndsWith en SQL) | sí | PASS | grep de las líneas agregadas: todo en memoria; filtros por igualdad; endpoints con 0 resultados → 200. |
| CRM-001 (campo nuevo con varios puntos de alta) | sí | PASS | `AsignarGancho` en Maps (2), Create/Edit, carga inicial y red de seguridad. |
| CRM-007 / CRM-016 (vocabulario en 2 lugares) | sí | PASS | `CategoriaHelpers` fuente única; comercio → matriz de Retail en el botón. |
| CRM-015 (siglas en el mensaje) | sí | PASS | Utilities idéntico a HEAD, "ABM Cuadrilla". |
| LP-002 (capacidad nueva propagada a todos los usos) | sí | PASS | rename/delete/Salud contemplan la configuración por gancho. |
| REG-010 / KOI-005 (sidebar vs. autorización) | no | N/A | Sin links nuevos. |
| KOI-001 (SweetAlert fuera del form) | sí | PASS | "Asignar ganchos" arma el POST con token del form de la card. |
| KOI-009 (URLs AJAX absolutas) | sí | PASS | Endpoints nuevos con `Url.Action`. |
| KOI-011 (largo de Action de auditoría) | no | N/A | El proyecto no tiene tabla de auditoría. |
| KOI-012 (migración con ids hardcodeados) | sí | PASS | Migración sin SQL de datos. |
| KOI-013 / KOI-014 (checkbox+hidden / script condicional) | sí | PASS (estático) | Sin checkboxes nuevos a mano; ids de scripts nuevos incondicionales. Consola: manual. |
| OLV-001/002/003/004 (tema oscuro: Select2, alertas, outline) | sí | NO PROBADO | Sin navegador. Los badges nuevos `violet`/`slate` tienen variante oscura; los Select2 nuevos usan el mismo theme que los existentes (sin override propio en `site.css`). Manual. |
| GAN-005/006, DN-003/004, MH-016..021, KOI-010 | no | N/A | Sin grillas decimales, pagos, cajas ni stock en este alcance. |
| **CRM-023** (nuevo) | sí | FAIL → **corregido** | Ver F6. |

### F5. Reglas nuevas o modificadas desde la última corrida (2026-08-28)

| Regla | Origen | Resultado | Acción |
|---|---|---|---|
| Tope de gasto en todos los caminos (CRM-017) | 32 | PASS | El combo sale solo por `SendDailyBatchAsync` (mismo cupo y presupuesto); los 3 ganchos combo no abren camino de follow-up. |
| Flag operativo persistido (CRM-018) | 32 | PASS | Plantillas por gancho en `ConfiguracionesOutbound`. |
| StartsWith/EndsWith en SQL (MH-001 variante) | 32 | PASS | Solo en memoria (`GanchoHelpers`). |
| Feature opcional no rompe el host (CRM-020) | 32 | PASS | `ModuloCatalogoQueries`, escalada y red de seguridad envueltas; probado S4. |
| Navegación vs FK en flujo con padre nuevo (CRM-021) | 32 | PASS | El código nuevo del webhook corre sobre contactos existentes y registra por la colección de navegación. |
| Modo sombra sin efectos (CRM-022) | 32 | PASS (código) | Sin escrituras nuevas desde la IA. |
| Lote con cupo: filtro antes del `Take` | 32 | PASS | Punto 1. |
| Checkbox + hidden (KOI-B01) y script condicional (KOI-B02) | 32 / yml KOI-013, KOI-014 | PASS (estático) | Consola y estado vacío con navegador: manual. |
| KOI-009..012, GAN-005/006, DN-003/004, MH-016..021, OLV-001..004, CRM-015/016 | yml | Ver F4 | — |

### F6. Defectos

| id | Severidad | Resumen | Estado |
|---|---|---|---|
| **CRM-023** | major | El selector múltiple "Frentes" de `/Modulos/Presupuesto` y del modal de `Chats/Detail` nunca llegaba al servidor: `$.get` con array manda `frentes[]=2`, que ASP.NET Core no bindea desde el query string, y `NormalizarFrentes` caía a Build **en silencio** (probado: `?frentes%5B%5D=2` → `data-frentes="1"`; `?frentes=1&frentes=2` → `"1,2"`). Hoy latente porque no hay módulos de otros frentes cargados, pero invalida E6 apenas se carguen. | **Auto-fix aplicado**: `$.ajax({ url, data, traditional: true })` en `Views/Modulos/Presupuesto.cshtml` y `Views/Chats/Detail.cshtml`. Rebuild Release 0 errores; re-verificado que las 2 vistas sirven el JS nuevo y que el formato tradicional bindea. Catalogado en yml + regla en 32. |

Observaciones no bloqueantes:
- **O1 — R3 medido en dev:** los 234 contactos Pendiente reciben gancho **Presencia web / "Sin web"** (ninguno tiene `PaginaWeb`). Con la combo web sin aprobar, el outbound manda 0 primeros contactos.
- **O2:** clave de rubro no mapeada con guión (`rubro-raro`) deja motivo "Rubro de gestión: rubro" (usa la base antes del guión). Cosmético.
- **O3 (preexistente):** /Bot/Salud "Templates activos sin campaña" dice "Están aprobados y activos" pero filtra solo `Activo` (listó una plantilla en `PendienteRevision`).
- **O4:** EF advierte que `ModuloCatalogo.Frente` tiene default de base sin sentinel; inocuo (0 no es un frente válido y el formulario lo exige).
- **O5 (operativo, preexistente):** dev combina credenciales reales de Meta/Places con outbound despausado y 26 campañas activas: levantar la app local sin pausar puede mandar mensajes reales.

### F7. Pruebas mínimas ejecutadas por este QA

Harness (rollback): S1 tabla de gancho (26), S2A lote sin combos con A/B, S2B lote con combos, S6 A1-a (7 contactos), S4 fallbacks (4), S3 botones (10 + baseline HEAD), S5 IA real (7). HTTP: Contactos Create (9), Details (4), Edit (6), GetData (27), Chats (10), Bot plantillas (7), Templates rename/edit/delete (3), Salud, AsignarGanchos (3), Modulos GetData/Create/Edit/Session, Checklist/Calcular/GenerarMensaje en las 2 versiones (16), re-verificación CRM-023.

### F8. Riesgos de liberación y mitigaciones

- Outbound en 0 hasta tener la combo web aprobada y asignada (O1) → no reactivar outbound esperando volumen; aprobar primero `olv_frio_combo_web_v1` (con la concordancia de género corregida).
- Migración `AddGanchoYFrenteComercial` pendiente en producción → aplicarla antes del deploy; después, "Asignar ganchos pendientes" desde /Bot.
- Consola, tema oscuro y XHR real de "Frentes" sin verificar en navegador → procedimiento manual abajo.
- Primer mensaje de IA después del deploy reescribe la cache del prompt (~USD 0,03, esperado).
- O5: en dev, pausar outbound antes de levantar la app local.

**Procedimiento manual pendiente (Joaquín, 10 minutos):**
1. Con la consola del navegador abierta (F12), recorrer en tema claro y oscuro: Contactos (filtrar por Gancho e Interés, Limpiar), Contactos/Nuevo y Editar (combo "Gancho del mensaje"), Chats (filtro Gancho), Bot (card "Plantillas de primer contacto"), Bot/Salud, Módulos, Módulos/Armar presupuesto. Esperado: 0 errores en consola, combos Select2 legibles en oscuro.
2. En Módulos/Armar presupuesto, pestaña Red: elegir un rubro, dejar solo "Landing" en Frentes. Esperado: la request a `/Modulos/Checklist` lleva `frentes=2` (no `frentes%5B%5D`) y aparece "Todavía no hay módulos cargados … en los frentes elegidos".
3. En un chat, "Armar propuesta": el modal arranca con Landing + AI Agents + Chatbots y cambiar los frentes recarga el checklist.

### F9. Checklist de salida para merge

- [x] Build Release 0 errores (QA, antes y después del auto-fix).
- [x] 8 puntos obligatorios + extras verificados (F1).
- [x] CRM-023 corregido y re-verificado.
- [x] Dev restaurado: contactos, ganchos y `UpdatedAt` idénticos al backup; configuración y flags como estaban; plantillas y contactos de prueba borrados.
- [ ] Procedimiento manual F8 (consola / tema oscuro / XHR real).
- [ ] Textos combo por `olvidata-marketing` (género) + aprobación de Meta.
- [ ] Migración en producción + deploy + "Asignar ganchos".
- [ ] Commit (no realizado por instrucción).

### F10. Estado go/no-go

**GO condicional** para merge y deploy de E1-E7 con el outbound pausado, sujeto al procedimiento manual F8. **NO GO para reactivar el envío de combos** hasta tener las plantillas corregidas y aprobadas en Meta.

## QA — canal nuevo de DM de Instagram (2026-10-15)

**Alcance probado: la mitad de INGRESO, sin Meta y sin deployar.** Migraciones aplicadas a `olvidatacrm_dev`, app en local y 19 chequeos contra el webhook con firma HMAC real. **19/19 PASS.** El lado de ENVÍO queda abierto: necesita credenciales y un IGSID real.

### Resultados

| Chequeo | Resultado |
|---|---|
| GET de verificación con token correcto | 200 + el challenge |
| GET con token incorrecto | 403 |
| POST con firma `X-Hub-Signature-256` inválida | 403, ningún contacto creado |
| DM de texto con firma válida | 200 inmediato (ACK); contacto con `CanalMensajeria=2`, `CanalOrigen=5`, `Telefono=NULL`, `IgScopedId`, `EstadoEmbudo=Respondido` |
| El mensaje queda en el hilo aunque el envío falle | sí (ver CRM-020 abajo) |
| Mismo `mid` dos veces | el segundo se descarta |
| `is_echo: true` | no crea contacto ni dispara al bot |
| `sender.id` = la propia cuenta | descartado |
| Reacción (corazón) | no llega al LLM ni crea contacto |
| Mensaje sin texto ni adjunto | descartado |

Esquema verificado contra la base de dev y después contra producción: `Telefono` nullable, `IgScopedIdVivo` VIRTUAL GENERATED con su único, `ArchivoAdjunto` longblob, y **los 10.235 contactos de producción en `CanalMensajeria = 1`**. La base de dev se devolvió a su estado previo (flags restaurados, contactos de prueba borrados).

### Defectos encontrados por esta prueba

**CRM-020 (reincidencia) — un fallo de envío perdía el mensaje entrante completo.** `major`.
Los envíos del árbol (`OnNewAsync`, `SendCurrentQuestionAsync`) no están envueltos uno por uno, así que una excepción subía hasta el handler del webhook y el `SaveChanges` final nunca corría: el contacto no se creaba y el mensaje del prospecto desaparecía **sin ningún rastro**. No era nuevo —le pasaba igual a WhatsApp— pero en Instagram pasaba de raro a probable: al vencer el token a los 60 días, **cada DM nuevo se perdía**, no solo quedaba sin respuesta. Fix: `ProcessAsync` envuelto, la entrega es best-effort y el registro está garantizado, con nota en el hilo y notificación in-app al admin. Verificado en la prueba (el contacto se creó con el envío fallando por falta de token).

**CRM-027 (nuevo) — `Results.Forbid()` en un endpoint anónimo devuelve 200, no 403.** `minor`, pero con consecuencia operativa real.
El GET de verificación con token incorrecto devolvía 200: `Forbid()` invoca el esquema de cookies y responde un 302 a `/Account/AccessDenied`, que con `UseStatusCodePagesWithReExecute` termina en una página HTML. No filtraba el challenge, pero no era un 403 y era inconsistente con el POST del mismo endpoint. Fix: `Results.StatusCode(403)`. **El GET de `/webhook/whatsapp` tiene el mismo detalle y se dejó como está**: funciona en producción y no se toca por cosmética. Cargado al catálogo 32 y a `regresiones-manuales.yml`.

### Defecto encontrado en revisión, antes de aplicar (no por prueba)

**CRM-026 — el `defaultValue` que genera EF para una columna nueva ignora el default de la entidad.** `blocker` si se aplicaba.
Detalle y reincidencia en el catálogo 32. Lo relevante para QA: el caso 2 del smoke-check de "modificación sobre módulo existente" (los datos PREVIOS a la migración, no solo los nuevos) es el que lo detecta — `SELECT Campo, COUNT(*) FROM Tabla GROUP BY Campo` después de migrar.

### Incidente durante la prueba

Al levantar la app en local, el `AvisosRenovacionSchedulerService` **mandó un template real de WhatsApp**: el `user-secrets` de desarrollo tiene las credenciales de Meta de producción. Fue a un número de datos sembrados (`5490000770005`), nadie lo recibió, pero Meta aceptó la llamada. La prueba se repitió apagando los switches del propio sistema en la base de dev y restaurándolos después, sin tocar `user-secrets`.
**Regla operativa para el próximo QA de este proyecto: verificar el `user-secrets` antes de levantar la app en local.** El recordatorio de renovación de ese mismo cliente vence el 18/10 y volvería a salir en cada corrida local mientras `AvisoRenovacionHabilitado = 1`.

### Pendiente — fase 6 con credenciales

1. **Envío**: texto, quick replies (incluido el menú de rubros degradado a quick replies y a texto numerado si pasan de 13), perfil (`GetPerfilAsync` sobre un IGSID real) y descarga de adjuntos entrantes antes de que venza la URL.
2. **Ventana**: 24hs, el cartel de cerrada, el botón "Reactivar" oculto y "Seguir por WhatsApp" cuando hay número.
3. **`is_echo` con un mensaje real** mandado desde la app de Instagram del celular — el fallo más probable de toda la integración.
4. **Regresión completa de WhatsApp** sobre la base ya migrada (outbound, follow-ups, avisos de renovación), no solo registros nuevos.
5. **LP-002**: la búsqueda global de `/Chats`, `/Contactos`, `/Clientes` y `/Clientes/Nuevo` con un `@usuario` que solo existe en un contacto de Instagram.
6. **Editar un contacto de Instagram sin teléfono y guardar** (el teléfono es opcional en Edición y obligatorio en Alta: son reglas distintas a propósito).
7. **Captura de teléfono por DM**: que tome `2216085665` → `5492216085665` y que **no** tome un CUIT de 11 dígitos.

## QA — Web Push de chats derivados a mano (CRM-028, 2026-10-15)

Lote de 1 ítem (integración: webhook de Meta + Web Push + service worker). Repo del sistema en
**read-only**: `git status --porcelain` idéntico al del arranque (19 entradas, las del Implementador),
verificado al cerrar. Todo criterio arrancó en FAIL. Build propio `dotnet build` **0 errores**
(21 advertencias, todas preexistentes).

### Método y límite del entorno

App levantada contra `olvidatacrm_dev` en `https://localhost:7201`, con el access token real de
WhatsApp de dev **neutralizado por variable de entorno** (`Olvidata_WhatsApp__AccessToken` inválido,
confirmado por el `Invalid OAuth access token` del scheduler de templates) — 0 mensajes reales
enviados. Outbound en standby. Evidencia por: HTTP autenticado, SQL contra la base, log de la app, y
un **push service falso** propio (HTTP en `:8099`) que recibe el sobre real que emite
`PushNotificationService` y devuelve el status que la prueba necesita (201 / 404 / 410 / 500 /
conexión rechazada).

**Lo que este entorno NO permitió verificar — declarado, no aprobado:** el MCP `playwright` y
cualquier Chrome lanzado desde las herramientas no alcanzan al puerto de la app
(`ERR_CONNECTION_REFUSED` contra `localhost`, `127.0.0.1` y la IP de LAN, con el listener confirmado
por `netstat` y accesible por `curl`; probado también con `--disable-features=NetworkServiceSandbox`
y `--no-sandbox`). Sin navegador quedan **sin verificar**: R1 (que `push-sw.js` sobreviva a las
recargas con el `unregister` selectivo), la entrega del globo al navegador, los 4 estados del botón,
iOS (R3) y Firefox/Safari.

### Cobertura por criterio

| Criterio | Veredicto | Evidencia observada |
|---|---|---|
| Multimedia de un `DerivadoManual` (rama `loAtiendeUnaPersona`) | **PASS** | Audio de un contacto en `DerivadoManual`: webhook 200, mensaje guardado (`ContactoRespuesta` "[Audio / nota de voz]"), campanita "Te escribió QA Push A" / "Te mandó un audio." → `/Chats/Detail/525`, sobre push de 230 B entregado, `FechaUltimoEnvioOk` sellado |
| Texto con el bot pausado | **PASS** | Campanita + push con el texto del mensaje, `FechaUltimoAvisoDerivado` sellado, mensaje guardado como "(bot pausado, lo atiende un asesor)" |
| Texto con la pausa de 48 hs vencida (flujo normal) | **PASS** | Contacto con `FechaBotPausado` a −72 hs: aviso emitido igual, 3er sobre al push service |
| **No** avisa cuando es ese mensaje el que recién deriva | **PASS** | Contacto `Respondido` con categoría sin cuestionario: queda `DerivadoManual`, recibe **su** aviso de derivación (`/Contactos/Details/528`) y **ningún** aviso de CRM-028 — `FechaUltimoAvisoDerivado` quedó en `NULL` y no hubo 4º sobre |
| Anti-ruido: varios mensajes → 1 aviso | **PASS** (con reserva, ver CRM-029) | 4 mensajes seguidos (2 texto + 2 audio) → **1** campanita, **1** push, marca sin cambiar |
| Vuelve a avisar recién tras una lectura real | **PASS** | `GET /Chats/Detail/{id}` (uno de los 6 puntos) estampa `FechaUltimaLecturaAgente`; el mensaje siguiente genera aviso nuevo. Probado con la acción real del controller, no con SQL |
| `MarcadoNoLeidoManual` sin tocar | **PASS** | `POST /Chats/MarcarNoLeido` cambia **solo** el flag (lectura sigue `NULL`, aviso sin cambiar) y el mensaje siguiente **no** avisa de nuevo. El guard no mira ese flag |
| Best-effort del webhook (CRM-020) | **PASS** | 5 modos de falla forzados — 410, 404, 500, conexión rechazada y **clave privada VAPID basura** (`VAPID private key should be 32 bytes long`): en los 5 el mensaje del contacto quedó guardado, la campanita se creó y el webhook respondió 200 |
| `404`/`410` dan de baja la suscripción sola | **PASS** | 410 → `DeletedAt` sellado + log "dada de baja sola (410)"; 404 → ídem. 500 y conexión rechazada → `FallosConsecutivos=1` y la fila **viva** |
| Alta / baja / re-alta del dispositivo | **PASS** | `POST Suscribir` 200; `Desuscribir` idempotente (200 dos veces); endpoint vacío → 400 con motivo; endpoint > 500 chars → 400; sin antiforgery → 400; los 4 endpoints sin sesión → 302 al login |
| **Único sobre `EndpointHashVivo`** (LP-057) | **PASS** | SQL directo: fila soft-deleted + fila viva con el **mismo** hash conviven; una 2ª fila viva con ese hash → `ERROR 1062 ... UX_PushSubscriptions_EndpointHash_Vivo`. Columna `VIRTUAL GENERATED` confirmada en `information_schema` |
| Rama de **revivir** la fila (la que el Implementador declaró sin probar) | **PASS** | Con la fila dada de baja por el 410, re-suscribir el **mismo** endpoint la revive en su lugar: `DeletedAt=NULL`, `FallosConsecutivos` a 0 y el total de filas sin cambiar (4 → 4). La rama `IgnoreQueryFilters` queda ejercitada |
| Privada de VAPID fuera del repo | **PASS** | `grep -rn PrivateKey` sobre `*.json/cs/js/cshtml/config/xml`: solo código y comentarios, ningún valor. `appsettings.Secrets.json` no está trackeado y no contiene `Push`. La privada vive en `user-secrets` (`aspnet-OlvidataCRM-4f6a9b2e…`) |
| Canal sin configurar | **PASS** | Con la privada vacía: `configurado:false` en los 2 GET, **0** envíos intentados, mensaje y campanita igual |
| Recorte del cuerpo a ~120 chars | **PASS** | Texto de 200 caracteres → cuerpo de exactamente 120 con elipsis |
| Regresión campanita in-app | **PASS** | `GetRecent` 200 (`unreadCount` + 8 items), `MarkAsRead` 200, `/Notifications` 200 con el botón nuevo presente |
| Regresión `/Chats` | **PASS** | `/Chats` 200, `Detail` 200 (2 contactos), `ListaParcial` 200, `HiloParcial` 200 |
| Regresión flujo normal del bot | **PASS** | Contacto nuevo por webhook: creado (`Respondido` / `AwaitingCategory`), sin aviso de CRM-028 |
| **R1 — `push-sw.js` sobrevive a las recargas** | **NO VERIFICADO** | Requiere navegador. Lo que sí se verificó: `sw.js` ya no existe en `wwwroot` (el único SW que la app puede registrar es `push-sw.js`), `GET /push-sw.js` 200 y el archivo no tiene handler de `fetch` ni uso de `caches` |
| Entrega del globo a un navegador real | **NO VERIFICADO** | Lo reportado por el Implementador no se pudo reproducir por el aislamiento de red. Sí está probado todo lo anterior a la última milla: sobre cifrado `aes128gcm`, VAPID `vapid t=<jwt>, k=<pública>`, TTL 1800, `Urgency: high` |
| iOS (R3) / Firefox / Safari | **NO VERIFICADO** | Fuera del alcance del entorno (iPhone real con el CRM en pantalla de inicio; solo había Chromium) |

### Máquina de estados del anti-ruido

`FechaUltimoAvisoDerivado = NULL` → (mensaje de `DerivadoManual`) → **avisado** → (n mensajes más)
→ **avisado**, sin aviso nuevo → (`FechaUltimaLecturaAgente > FechaUltimoAvisoDerivado`) →
**re-armado** → (mensaje) → **avisado**. Los 4 saltos reproducidos. El flag `MarcadoNoLeidoManual`
**no** es una transición de esta máquina: verificado que no re-arma.

### Defectos

**CRM-029 — minor — parte de defecto emitido.** El anti-ruido no se sostiene cuando la pestaña del
chat queda abierta: `Chats/HiloParcial` estampa `FechaUltimaLecturaAgente` cuando trae mensajes
nuevos, y eso re-arma el guard justo antes del mensaje siguiente. Reproducido 3/3 — aviso 23:49:23 →
lectura 23:49:27 → aviso 23:49:27 → lectura 23:49:31 → aviso 23:49:31: **3 mensajes, 3 avisos**, en
el escenario más común (el asesor deja el chat abierto toda la jornada) y el peor (suena mientras
está mirando ese mismo chat). Catalogado en `docs/qa/regresiones-manuales.yml`. **No se aplicó
ningún fix.** Criterio de re-verificación: con la pantalla de detalle abierta en background, 3
mensajes seguidos del contacto producen **1** aviso, y después de abrir o responder deliberadamente
el siguiente mensaje **sí** vuelve a avisar.

Defectos de la corrida anterior (2026-09-14): **CRM-023 cerrado** — no se re-abrió nada en esta
corrida.

### Observaciones no bloqueantes

1. El envío de push corre **dentro** del procesamiento del webhook: con 3 dispositivos y uno
   inalcanzable tardó ~8 s. Meta ya tiene su ACK (el procesamiento es en background), pero demora la
   respuesta del bot al contacto. Candidato a cola si alguna vez hay muchos dispositivos.
2. `push.js` usa `navigator.serviceWorker.getRegistration('/push-sw.js')`, que toma una URL de
   **cliente** y no de script: hoy funciona porque el scope es la raíz, pero devolvería igual
   cualquier otro SW registrado en `/`. Cosmético.
3. El comentario del `_Layout` dice que "dos SW pueden compartir scope"; en realidad un scope tiene
   una sola registración. La condición por `scriptURL` es correcta igual.
4. Incidental, fuera de CRM-028: con el token de WhatsApp inválido aparecieron una notificación
   apuntando a `/Contactos/Details/0` y la pérdida del `ContactoRespuesta` cuando `OnNewAsync` falla
   al enviar (la excepción sube hasta el `catch` del webhook y se pierde el `SaveChanges`). Es
   preexistente y solo se manifiesta con credenciales rotas; no lo introduce este CR.

### Riesgos de liberación

- **R2 sigue abierto y es el riesgo dominante:** sin HTTPS válido no hay push. El certificado de
  `portal.olvidata.com.ar` vence **2026-10-19**. Deployar CRM-028 antes de resolver el certificado
  es publicar una funcionalidad que se apaga en 4 días.
- La privada de VAPID **todavía no está cargada en producción**: hay que ponerla en
  `appsettings.Secrets.json` del sitio o en `Push__PrivateKey` **antes** del deploy; si no, el canal
  queda inerte (degrada bien, pero no avisa nada).
- R1 y la entrega real al navegador no están verificados por QA. Es un chequeo manual de 5 minutos
  en el navegador de Joaquín: activar los avisos, recargar 3 veces, confirmar que el botón sigue en
  "activados" y que llega un globo con el CRM cerrado.
- La migración es aditiva y ya está aplicada en dev; producción sin tocar.

### Checklist de merge

- [x] Build en limpio, 0 errores
- [x] Migración aditiva, reversible (`DropTable` se lleva la columna generada y su único)
- [x] Ningún secreto en el repo
- [x] Los 4 endpoints nuevos exigen sesión y antiforgery
- [x] Best-effort del webhook probado con 5 modos de falla
- [x] Sin regresión en campanita, `/Chats` ni flujo normal del bot
- [ ] R1 + entrega real al navegador (manual, pendiente)
- [ ] Certificado de producción resuelto (R2)
- [ ] `Push:PrivateKey` cargada en producción
- [ ] CRM-029 resuelto o aceptado explícitamente como conocido

### Estado go/no-go

**NO-GO para deploy a producción hoy**, por dos condiciones de entorno que no dependen del código:
el certificado que vence el 2026-10-19 (sin HTTPS válido el push no existe) y la privada de VAPID
sin cargar en el sitio. El código, en lo que este QA pudo observar, está sano: 19 criterios PASS,
1 defecto minor, 0 major, 0 blocker, y la rama que el Implementador había dejado sin probar quedó
cubierta y pasa. **GO condicionado** a: (1) certificado resuelto, (2) privada cargada, (3) el
chequeo manual de 5 minutos de R1 + globo real en un navegador, y (4) decisión sobre CRM-029 —
arreglarlo o aceptarlo por escrito.

## QA — re-verificacion de CRM-029 (2026-10-16)

Contexto nuevo, criterio de vuelta en **FAIL**. Alcance acotado a lo que toco el fix (`fb45699`
sobre `1005cd2`): **no** se repitieron los 19 criterios de CRM-028 que ya habian pasado. Repo del
sistema en read-only: `git status --porcelain` **vacio** al abrir y al cerrar (el Implementador
commiteo todo). Build propio `dotnet build` **0 errores**, 21 advertencias preexistentes.
Dev restaurado al cerrar: 444 contactos, 0 suscripciones, notificaciones 18-27, siembra intacta.

### CRM-029: CERRADO

El criterio que escribi, medido contra el fix:

| Mitad del criterio | Veredicto | Evidencia observada |
|---|---|---|
| Pestania de detalle abierta en background, 3 mensajes seguidos → **1** aviso | **PASS** | La lectura comun se mueve en cada tick (00:14:25 → 00:14:29 → 00:14:33) y el aviso **no** se mueve: queda en 00:14:21. `FechaUltimaLecturaDeliberadaAgente` sigue en `NULL`. **1 aviso para 3 mensajes** (antes del fix: 3) |
| Tras abrir o responder deliberadamente, el siguiente **si** avisa | **PASS** | `GET /Chats/Detail/{id}` estampa las 2 fechas (DELIB=00:14:34) y el mensaje siguiente genera aviso nuevo (00:14:34), 1 sobre al push service |

### Los 3 puntos pedidos

**1. El "no leido" de `/Chats` — PASS.** Los 6 pasos, con el filtro real `Interaccion=noLeidos`:
recien abierto el detalle → leido; mensaje entrante nuevo → **no leido**; reabrir → leido;
`MarcarNoLeido` → **no leido** (y el flag queda en 1); `MarcarTodosLeidos` (camino bulk) → leido;
otro mensaje entrante → **no leido**. La semantica historica de `ChatsController.cs:351` intacta: el
tick de `HiloParcial` sigue estampando la lectura comun y sigue siendo lo que sostiene el "no leido".
(Dos lecturas intermedias dieron falso negativo por **mi** propio flood — 12 mensajes al mismo
contacto en 2 minutos dispararon el corte anti-loop y el `MarcarTodosLeidos` masivo toco un contacto
de otra prueba. Re-medido limpio sobre 2 contactos nuevos: PASS.)

**2. El `UPDATE` de siembra — PASS.** En dev: 20 contactos tenian lectura comun, los 20 quedaron con
la lectura deliberada sembrada, **0 sin sembrar** → ningun contacto preexistente arranca en "nadie
leyo nunca". Idempotencia probada en el caso que importa: a un contacto con lectura deliberada
**vieja** (2026-10-01) y lectura comun **mas nueva** (2026-10-14, el patron que deja el polling) se
le volvio a correr el `UPDATE` y **no se piso** la deliberada — la clausula `WHERE ... IS NULL` lo
protege. Y la siembra no tiene efecto observable sobre el guard en el deploy: los 444 contactos
tienen `FechaUltimoAvisoDerivado` en `NULL`, asi que gana la primera condicion del guard y el primer
mensaje de cada chat derivado avisa igual.

**3. Los 5 puntos deliberados — 2 ejecutados (PASS), 3 verificados solo estructuralmente.**
- `GET /Chats/Detail` → **PASS ejecutado** (estampa las 2 fechas y re-arma).
- `MarcarTodosLeidos`, el camino bulk por `ExecuteUpdateAsync` → **PASS ejecutado**: estampa las 2
  por `.SetProperty` (lectura=DELIB=00:15:56), el mensaje previo sin leer **no** habia avisado de
  nuevo (0 avisos) y el posterior al bulk **si** aviso (1). El `.SetProperty` replicado no se olvido
  de la columna nueva.
- Los **3 envios** (`EnviarMensaje`, `EnviarPresupuestoPdf`, `EnviarImagen`) → **NO EJECUTADOS**: los
  3 estampan recien **despues** de un envio exitoso a Meta, y la URL de la Graph API esta hardcodeada
  en `WhatsAppClient` (`https://graph.facebook.com/{ApiVersion}/`), asi que no se puede sustituir por
  un doble local ni hay destinatario seguro para un envio real. Lo que **si** esta medido
  mecanicamente es el invariante que importa: en `ChatsController` queda **una sola** escritura de
  `FechaUltimaLecturaAgente` —la linea 381, el tick de `HiloParcial`— y las otras 4 pasan por
  `Contacto.RegistrarLecturaDeliberada` (lineas 249, 551, 650, 760), con la unica escritura directa
  de la columna nueva en el `.SetProperty` del bulk (linea 499). El metodo ya quedo probado de punta
  a punta por el camino de `Detail`. Riesgo residual: bajo, pero no es un PASS observado.

### Defecto nuevo: CRM-030 (minor) — parte emitido, sin fix

**El argumento del Implementador sobre los 3 estampados de `Descartado` es correcto en la direccion
que se temia, y falla en la vuelta.** Medido:

- `ContactosController.CambiarEstado → Descartado` estampa la lectura **comun** y deja
  `FechaUltimaLecturaDeliberadaAgente` en `NULL` → **ninguno de los 3 puede re-armar el guard de
  mentira.** La preocupacion planteada ("el guard arranca re-armado sin que nadie haya leido nada")
  es estructuralmente imposible: esos 3 no escriben el campo del que ahora cuelga el guard.
- Pero la entidad **si** puede volver a `DerivadoManual`: `EstadosManualesPermitidos` es
  `Enum.GetValues<EstadoEmbudo>()`, o sea **todos** los estados son asignables a mano. Secuencia
  medida limpia: avisado (aviso 00:17:48) → `CambiarEstado` a `Descartado` (estampa la lectura comun
  00:17:54, DELIB sigue `NULL`) → `CambiarEstado` de vuelta a `DerivadoManual` → el contacto escribe
  → **0 avisos**. Antes del fix ese mismo estampado re-armaba el guard y el aviso salia: el fix
  cierra un re-armado espurio y, de paso, uno legitimo.
- **No se pierde informacion**: el chat sigue visible en la bandeja de no leidos (verificado). Lo que
  queda muerto es el canal push para ese chat hasta que alguien lo abra desde `/Chats`.
- Alcance real acotado: si el pase de estado se hace **desde** `/Chats/Detail` el hueco no existe
  (abrir el detalle ya estampo la deliberada). Solo se da haciendolo desde `/Contactos` sin abrir el
  chat.

Fix sugerido como hipotesis, no como instruccion: limpiar `FechaUltimoAvisoDerivado` cuando el
contacto **sale** de `DerivadoManual`. Es mas barato que migrar escritores y cubre cualquier camino
futuro. Criterio de re-verificacion: avisado → sacado del estado → devuelto al estado → el mensaje
siguiente **si** avisa, sin reintroducir CRM-029 (3 mensajes seguidos con la pestania abierta siguen
dando 1 aviso).

### Cosmeticos del fix

`push.js` ahora busca su registracion recorriendo `getRegistrations()` y matcheando por `scriptURL`,
y el comentario del `_Layout` quedo corregido. Revisados por lectura: el `for` toma
`active || waiting || installing`, que es el mismo criterio del barrido del layout, y no cambia el
`register()`. **Que el SW siga sobreviviendo a las recargas sigue NO VERIFICADO**: el entorno sigue
sin permitir que ningun navegador alcance el puerto de la app, y por indicacion del coordinador no se
gasto otra vuelta en pelearlo. Es el mismo chequeo manual de 5 minutos que ya estaba pendiente, y
ahora cubre tambien esta linea nueva.

### Estado go/no-go

**GO para subir, en lo que depende del codigo.** CRM-029 cerrado con evidencia en las 2 mitades del
criterio, el "no leido" de `/Chats` sin regresion, la siembra correcta e idempotente, y los 2 puntos
deliberados ejecutables pasando. Queda **CRM-030 (minor)** como conocido: no bloquea, degrada un
corner case a "sin push, pero visible en la bandeja". Lo que sigue fuera de mi alcance y ya es
decision tomada del owner: el certificado del 19/10 (sin HTTPS valido el push no existe) y la
privada VAPID, que carga el coordinador en el deploy. Lo unico que pido que no se saltee es el
chequeo manual de 5 minutos del service worker en un navegador real.

## QA — cola de seguimiento (2026-10-16)

**Alcance:** pantalla `/Seguimiento` (cola + modal del toque + endpoints `Index`/`GetData`/`OpcionesToque`/`Toque`). 1 lote (módulo de integración + gasto real). Repo del CRM en read-only: `git status --porcelain` al cerrar = los 9 ítems del implementador y +6/+5 líneas en los 2 archivos tocados, **nada de QA**.

**Método.** Build propio (0 errores, 16 advertencias todas preexistentes). App levantada en `Development` sobre **un clon local de producción** (`olvidatacrm_qacola`, 33 tablas / 25.518 filas, copiado con `SELECT` + `SHOW CREATE TABLE` y `rollback()` del lado de prod — cero escrituras en producción, verificado al cerrar: `ContactoRespuestas` 9075 antes y después, 0 filas del arnés, 0 usuarios del arnés, `ConfiguracionesOutbound` intacta). **Nunca contra producción.** Neutralización del envío antes de levantar: `Olvidata_WhatsApp__AccessToken` pisado por variable de entorno con un token inválido, y en el clon `OutboundPausado=1`, `AvisoRenovacionHabilitado=0`, `BusquedaMapsPausada=1`, `ConversacionIaPausada=1` — los 7 hosted services quedaron inertes. **Cero mensajes enviados**, verificado por conteo de `ContactoRespuestas` antes y después de cada POST.

*Hallazgo de entorno a tener presente:* el `user-secrets` del proyecto Web tiene el **AccessToken real de WhatsApp**, y `dotnet run` en Development lo carga. Levantar la app sobre datos de producción sin pisar ese token por variable de entorno habilita a 3 schedulers a mandar mensajes reales. No es un defecto del sistema; es un paso obligatorio del procedimiento de QA de este proyecto.

**Navegador: no disponible.** Un (1) intento de `browser_navigate` contra el puerto de la app → `ERR_CONNECTION_REFUSED`, con el listener confirmado por `netstat` y alcanzable por `curl`/`requests` desde el mismo contexto. Es el aislamiento de red del entorno ya medido el 2026-10-15, no el MCP. Sin reintentos. Camino usado: **HTTP autenticado (`requests` + cookie de sesión) + SQL directo contra el clon + un oráculo SQL independiente del LINQ**.

**Oráculo independiente.** Se reescribió el criterio de la cola en SQL plano desde el enunciado del plan (no desde el LINQ) para que el número de la pantalla tuviera contra qué contrastarse: universo 320, con toque posterior 50, cola 270, ventana abierta 0, Instagram en la cola 0, WhatsApp con `Telefono` nulo en la cola 0. Los 6 coinciden con lo que muestra la pantalla.

### Cobertura por criterio

| # | Criterio | Resultado | Evidencia observada |
|---|---|---|---|
| 1 | Cola 270 / 50 excluidos / 320 con el filtro; universo 320, 180 con matriz, 0 en ventana | **PASS** | Encabezado servido: "270 en la cola · 180 con matriz MVP/FULL · 0 con ventana abierta (gratis) · 270 necesitan plantilla paga · 50 excluidos porque ya les escribimos (320 cumplen el criterio de 48 hs)". `GetData` sin filtros → 270; con `incluirToque=1` → 320. Oráculo SQL: 320/50/270/0. Ninguna fila del default trae `toquePosteriorUtc` (0 de 270): la exclusión vive en un solo lugar |
| 2 | Combo con exactamente 2 plantillas, `olv_retomar_conversacion_v1` sugerida; la guarda del servidor rechaza cualquier otra | **PASS** | `OpcionesToque` → 2 plantillas, `sugerida=true` en retomar. POST `/Seguimiento/Toque` rechazó **11/11**: `olv_frio_v13`, `olv_renovacion_recordatorio_v1`, `olv_notif_respuesta`, `olv_nurturing_v2`, `olv_referido_v2`, `olv_frio_combo_admin_v2`, `olv_renovacion_notificacion_v3`, `olv_laboratorio_v1`, una inexistente, la sugerida en mayúsculas y la sugerida con un espacio al final. Las 11 con `ok=false` y `ContactoRespuestas` sin cambios: cortó antes de la red. Antiforgery: POST sin token → 400 |
| 3 | Contacto traído con el filtro sigue elegible; aviso rojo con la fecha, antes del de matriz | **PASS (datos) / verificado en el fuente (orden del aviso)** | #9954 Farina Balbi: ausente del default, presente con el filtro, `toquePosteriorUtc=2026-10-08T12:32:14`, y `OpcionesToque` le devuelve las 2 plantillas sin bloqueo — sigue elegible. El orden del aviso está en el fuente (`Index.cshtml` 423 y 458: `avisoYaContactado(op) + avisoMatriz(op)`, en los 2 modales) pero **no renderizado**: sin navegador no se observa el pixel |
| 4 | Cada filtro por separado, uno que vacíe la grilla, el rango de fechas, "Primeros 30" = 30 | **PASS** | 46 combinaciones por `GetData`, **ningún 500**. Valores tomados del HTML servido, no inventados. Casos que vacían: buscador sin match → 0, `ventana=abierta` → 0, `canal=AdsPagos/Referido/Manual/InstagramOrganico` → 0, `categoria=build` → 0, fechas invertidas → 0. Rango de fechas: `01/09/2026-10/09/2026` → 44, idem en ISO → 44, basura → 270 (ignora, no revienta): el bug del `Kind` está corregido. Tope: 10→10, 50→50, `abc`/`-5`/`0`→270 (sin tope). **CRM-024**: matriz+ventana+estado+tope 30 → **30**; Retail+matriz+ventana+tope 30 → **30** |
| 5 | Columnas visibles = filtros disponibles; nunca un combo vacío en silencio | **PASS** | 10 columnas (Negocio, Contacto, Rubro, Zona, Interés, Origen, Días, Matriz, Ventana, Posterior) y 11 controles de filtro, todos con columna que los respalda (Estado se dibuja dentro de la celda de identidad, `labelByEstado`). `ordering: false` global: la UI no promete un orden que el servidor ignore (no repite **CRM-003**). Combo vacío provocado desactivando las 2 plantillas en el clon → mensaje explícito con los 2 nombres y link a `/Templates`, y el POST igual rechazado por el catálogo; restaurado, vuelve a 2 |

**Extras cubiertos.** Orden por valor: 180 con matriz primero, corte exacto en el índice 180, días monótonos no decrecientes en cada grupo (primera fila #7293 Ferretería Mil Cosas, 36 días, 14 módulos; última #194 FM reparaciones, 91 días). Persistencia de filtros en Session, ida y vuelta de los 11, con las cards del encabezado siguiendo siendo los totales. Rama de **ventana abierta**, que con los datos de hoy no tiene ninguna fila: se abrió la ventana de #7293 con un entrante sintético en el clon y el servidor pasó a texto libre (0 plantillas, costo 0, sugerido pre-cargado, cards a 1 abierta / 269 pagas, filtro `ventana=abierta` → 1), y rechazó tanto el texto vacío como un POST con plantilla —no paga por algo que es gratis—; revertido. Performance: Index 58 ms, GetData 69 ms, OpcionesToque 157 ms.

### Catálogo cross-proyecto y reglas nuevas

| id | aplica | resultado | evidencia |
|---|---|---|---|
| MH-001 | sí | **PASS** | 46 filtros, incluidos 6 que devuelven 0 filas, sin un solo 500 |
| CRM-019 | sí | **PASS** | las 2 subconsultas correlacionadas con `Like "[%"` tradujeron y devolvieron las 320 filas |
| CRM-024 | sí | **PASS** | tope 30 después de 4 filtros → 30 |
| CRM-017 | sí | **PASS** | con `PresupuestoMensualArs=0.01` en el clon, el modal bloquea y el POST **con la plantilla sugerida** devuelve "El tope de gasto de mensajería del mes ya está consumido", sin tocar la red; restaurado, vuelve a habilitar. Es el único camino de envío de plantillas |
| CRM-007 (histórico de este proyecto, ya archivado del catálogo) | sí | **PASS** | la opción Retail agrupa 3 vocabularios de `Rubro`: 'indumentaria' (2), 'Indumentaria o calzado' (25), 'indumentaria-laplata' (1) |
| CRM-023 | sí | **PASS** | el único GET con parámetro manda un escalar |
| LP-002 | sí | **PASS** | `identidadVisible` poblado en las 270 filas; 0 filas de WhatsApp con `Telefono` nulo en la cola |
| REG-010 | sí | **PASS** | usuario Vendedor creado en el clon: el sidebar **no** muestra el ítem y los 4 endpoints responden 302 a `AccessDenied` |
| CRM-003 | sí | **PASS (no repetido)** | `ordering: false`: ninguna columna es clickeable |
| CRM-026 / CRM-027 | no | **N/A verificado** | 0 migraciones EF; 0 endpoints anónimos nuevos (los 4 responden 302 al login sin sesión) |
| reglas nuevas desde la corrida anterior | — | **ninguna** | `git log --since=2026-10-16` sobre `32` y el yml: sin commits |

### Defectos y partes emitidos

- **CRM-031 (major) — parte emitido, es de `/Chats` y preexistente.** El defecto señalado queda **CONFIRMADO, no refutado**: `GET /Chats/Detail/7293` sirve un combo de reactivación con 5 plantillas y 3 son las del texto centinela (`olv_notif_respuesta`, `olv_nurturing_v2`, `olv_referido_v2`). Causa raíz verificada: `!t.Texto.Contains('{')` sobre la copia local, con las 22 plantillas en `Activo=1 / Aprobado`. Que `olv_nurturing_v2` lleva parámetros en Meta lo prueba el propio sistema: el pipeline la manda con `BuildFollowUpComponents` (`OutboundCampaignService` 716-717), mientras `ReactivarConversacionAsync` manda `components = null`. **Lo que no se pudo observar es el rechazo de Meta** (exigiría un envío real): queda declarado, no afirmado. La pantalla nueva **no** las ofrece. Re-verificación: la intersección entre lo que ofrece el combo de `/Chats` y las plantillas con texto centinela tiene que ser vacía.
- **CRM-032 (minor) — parte emitido, propio de esta pantalla.** El botón del toque se deshabilita para traer las opciones y se re-habilita en el `always()` del `getJSON`, **antes** del POST de envío; la marca de salida de la cola se escribe después del envío. Durante el vuelo del POST pagado la fila vuelve a aceptar un toque y los dos pasarían todos los guards. **No reproducido end-to-end**: reproducirlo exige autorizar un envío pago real. Re-verificación: dos POST concurrentes con el mismo id → uno `ok=true` y el otro rechazado explícitamente.
- Observación cosmética (no defecto, sin parte): con el filtro de ya contactados tildado, `recordsTotal` sigue siendo 270 y `recordsFiltered` 320, así que el pie dice "1 a 25 de 320 (de 270 en la cola)". Es literal pero se lee raro.

### Riesgos de liberación

1. **El envío no tiene una sola evidencia de ejecución** — R1 del implementador, confirmado. Los dos caminos (plantilla paga y texto libre) se ejercitaron hasta el borde: validación de catálogo, guarda de lista blanca, tope de gasto, elección de rama y mensajes de rechazo, todo con `ok=false`. **Ningún envío exitoso fue observado.** Lo que no está probado: que `SendTemplateAsync` con `components=null` y una plantilla de reenganche salga bien, que la fila facturable quede bien etiquetada en el hilo, y que `FechaFollowUp` saque de la cola al contacto después de un envío real.
2. **CRM-032** convierte una impaciencia en un cobro doble, y el lote de prueba son 30 clicks seguidos: es exactamente el escenario donde pasa.
3. **CRM-031** no afecta a esta pantalla, pero sí a `/Chats`, que es la pantalla desde la que se va a mirar el resultado del lote.

### Estado go/no-go

**La pantalla: GO.** 5 criterios PASS con evidencia observada, 9 reglas del catálogo PASS, 2 N/A verificados, 0 defectos propios de la cola, 0 regresiones (`/Chats`, `/Contactos`, `/Bot`, `/Templates`, `/Clientes`, `/Negocio/Dashboard`, `/Seguimiento` → 200).

**El envío del lote de 30: NO-GO todavía**, y no por un defecto de la cola. Falta (a) el fix de **CRM-032** o la decisión explícita de convivir con él, y (b) una prueba de envío de **1 contacto** autorizada por Joaquín antes de los 30 — el camino de envío no tiene ninguna evidencia de ejecución y el primer lote sería la primera vez que corre de verdad.

### Checklist de merge

- [x] Build verde propio, 0 errores, sin advertencias nuevas
- [x] 46 combinaciones de filtro sin un 500
- [x] Números de la cola contrastados contra un oráculo SQL independiente
- [x] Guarda de la lista blanca verificada con 11 nombres rechazados, 0 envíos
- [x] Tope de gasto verificado por comportamiento, no por lectura de código
- [x] Autorización por rol verificada con un usuario no SuperUsuario
- [x] 0 migraciones EF; 0 escrituras en producción; `git status` del CRM limpio de QA
- [x] **CRM-032** aplicado y **cerrado por QA el 2026-10-16** (ver bloque de re-verificación)
- [ ] Prueba de envío de 1 contacto autorizada y observada
- [ ] **CRM-031** (de `/Chats`, no bloquea este merge)

## QA — re-verificación de CRM-032 (2026-10-16)

**CRM-032: CERRADO.** Criterio de vuelta en FAIL al arrancar; pasó con evidencia observada. Mismo arnés que la corrida de la cola (clon de producción `olvidatacrm_qacola`, `Development`, token de WhatsApp pisado por variable de entorno, schedulers pausados en el clon). **Cero mensajes enviados:** `ContactoRespuestas` en 9075 al abrir y al cerrar, medido entre cada POST. Universo de la cola en 320 al cerrar, igual que al abrir: el arnés no sacó a nadie.

**Cómo se ejercitó el camino pagado sin pagar:** con `PresupuestoMensualArs=0.01` en el clon, `ReactivarConversacionAsync` corta por tope **después** de la reserva y **antes** de la red. Eso permite recorrer reserva → envío fallido → liberación completo, con el mensaje del tope como marcador inequívoco de "esta request llegó al envío".

| # | Criterio | Resultado | Evidencia |
|---|---|---|---|
| 13 | N concurrentes sobre la misma fila: 1 envío | **PASS** | 4 corridas × **10 POST concurrentes** (10 sesiones HTTP = 10 conexiones y 10 scopes de DI, barrera por corrida). Las 4: **llegaron al envío = 1**, reserva perdida 7-9, pre-chequeo 0-2. El trabajo lo hace el `UPDATE` atómico, no el pre-chequeo: en 2 de las 4 corridas el pre-chequeo no filtró a nadie y los 9 perdedores los rechazó la reserva |
| 14 | POST repetido con el mismo `contactoId` | **PASS** | Con la marca escrita como la deja un envío exitoso (`FechaFollowUp = utc_timestamp(6)`), los 2 POST siguientes se rechazan y el contacto **sale de la cola**. Nota: con el envío en `!Ok` el reintento secuencial **sí** vuelve a ganar la reserva, y eso es correcto — la liberación lo devolvió a la cola. La prueba 14 tal como está escrita en §12 supone un envío exitoso, así que su mitad de carrera real queda cubierta por la 13 |
| 15/16 | Botón deshabilitado del click al fin del POST | **verificado en el fuente, NO en navegador** | El `always()` del `getJSON` que rehabilitaba ya no existe. `liberarBoton` se llama en 6 sitios y sólo en ésos: bloqueo del servidor (395), falla de opciones (402), cancelar texto libre (448), sin plantillas (458), cancelar plantilla (486) y el `always()` de `enviar()` (518). `$btn` viaja como parámetro a los 2 modales y a `enviar()`. **Sin navegador alcanzable no se observa el estado del botón** — y deja de ser carga estructural: el servidor rechaza igual un POST a mano |

**Las 3 consecuencias que pedía el coordinador, las 3 PASS:**

1. **La liberación restaura el valor anterior EXACTO, no null.** #1012 BAHIAPROP tenía `FechaFollowUp = 2026-08-05 12:38:00.713174` (follow-up frío anterior a su respuesta, uno de los 28). Después del envío en `!Ok` volvió a **ese mismo valor al microsegundo**, y el contacto sigue en la cola. Idem #2123 y #1379 en las corridas concurrentes. La columna es `datetime(6)`, así que el `WHERE FechaFollowUp = @ahora` de la liberación no pierde precisión — era el riesgo real de este diseño y no se materializó.
2. **Se libera con el envío en `!Ok`.** Tope consumido → `ok=false`, `enviadoSinMarcar=false`, `FechaFollowUp` restaurada y **el contacto vuelve a la cola** (verificado por `GetData`, no por la base solamente). No sale en silencio sin que nadie lo haya contactado.
3. **La lista blanca corre antes de reservar.** POST con `olv_frio_v13` → rechazado y `FechaFollowUp` **idéntica** antes y después: no dejó reserva. Idem con `plantilla` vacía. Extra propio: un contacto en estado Descartado se rechaza por estado y tampoco deja reserva.

**Lo que no se pudo observar y queda declarado, no afirmado:** la rama residual `enviadoSinMarcar` (ahora "marcado y no enviado", con el `Swal` "Revisá esto a mano" en la línea 500) exige que falle la base **en el medio** del envío; no se simuló. Y la carrera con un envío **exitoso** de verdad sigue sin ejercitarse, porque exige autorizar un envío pago — pero es el caso benigno: ahí la reserva ya quedó escrita y nadie la libera.

**Nota de arnés (mío, no del sistema).** La primera pasada marcó FAIL en concurrencia: mi grader contaba como "ganó la reserva" a todo lo que no dijera "toque en curso", y 6 de 8 habían sido cortados antes por el **pre-chequeo** de `FechaFollowUp`. El sistema había hecho lo correcto (1 solo envío) desde el principio. Hay que clasificar por **dónde** cortó cada request —mensaje del tope / "toque en curso" / "ya recibió su toque"— y no por `ok`. Tercera vez que el arnés miente antes que el sistema en este proyecto.

**Veredicto sobre el lote de 30: mejora, y el bloqueante que quedaba era éste.** Con CRM-032 cerrado, de mi lado no queda nada abierto: la prueba de 1 envío real a un número propio ya está decidida y pendiente de autorización, así que no la cuento como bloqueante mía. **CRM-031** sigue abierto, es de `/Chats`, preexistente, y no bloquea este lote. Mi recomendación pasa a **GO para el lote de 30 una vez observada la prueba de 1 envío**, que es lo único que le falta al camino de envío para tener evidencia de ejecución.

## Historial de ajustes

### Bloques archivados (2026-10-16)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-08** — 1 bloques (2026-08-27 a 2026-08-27) → [`6-qa-2026-08-3.md`](historial/6-qa-2026-08-3.md)


### Bloques archivados (2026-10-16)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-08** — 1 bloques (2026-08-28 a 2026-08-28) → [`6-qa-2026-08-2.md`](historial/6-qa-2026-08-2.md)


### Bloques archivados (2026-10-15)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-08** — 1 bloques (2026-08-28 a 2026-08-28) → [`6-qa-2026-08.md`](historial/6-qa-2026-08.md)


### Bloques archivados (2026-09-25)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-07** — 2 bloques (2026-07-21 a 2026-07-25) → [`6-qa-2026-07.md`](historial/6-qa-2026-07.md)

- 2026-10-16 (re-verificacion de CRM-029, fix `fb45699`): contexto nuevo, criterio de vuelta en FAIL, alcance acotado al fix. **CRM-029 CERRADO** con las 2 mitades medidas: pestania abierta en background + 3 mensajes → **1** aviso (la lectura comun se mueve en cada tick, el aviso no), y tras `GET /Chats/Detail` el siguiente **si** avisa. El "no leido" de `/Chats` sin regresion en los 6 pasos con el filtro real (`Interaccion=noLeidos`), incluidos `MarcarNoLeido` y el bulk. Siembra de la columna nueva correcta (20/20, 0 sin sembrar) e **idempotente en el caso que importa**: no pisa una deliberada vieja con una lectura comun mas nueva. De los 5 puntos deliberados, 2 ejecutados (Detail y el bulk por `.SetProperty`) y los 3 envios **no ejecutados** —estampan despues de un envio exitoso y la URL de la Graph API esta hardcodeada—, cubiertos solo por el invariante mecanico de que en `ChatsController` queda una sola escritura directa de `FechaUltimaLecturaAgente` (el tick) y las otras 4 pasan por `RegistrarLecturaDeliberada`. **1 defecto minor nuevo: CRM-030** — el argumento del Implementador sobre los 3 estampados de `Descartado` es correcto en la direccion que se temia (no pueden re-armar el guard de mentira, no escriben el campo nuevo) pero falla en la vuelta: `EstadosManualesPermitidos` admite **todos** los estados, y Descartado → DerivadoManual a mano deja el guard con el aviso viejo puesto y 0 avisos para el mensaje siguiente; el chat sigue visible en la bandeja de no leidos, asi que degrada sin perder nada. Parte emitido, sin fix. El service worker sobreviviendo a las recargas sigue **NO VERIFICADO** (mismo aislamiento de red; por indicacion del coordinador no se gasto otra vuelta). **GO para subir en lo que depende del codigo**; certificado y privada VAPID son decision del owner.
- 2026-10-15 (CRM-028, Web Push de chats derivados a mano): lote de 1 ítem, repo del sistema read-only y `git status` idéntico al cierre. Navegador **no disponible** (ni el MCP `playwright` ni un Chrome propio alcanzan el puerto de la app: `ERR_CONNECTION_REFUSED` con el listener confirmado por `netstat` y accesible por `curl`) → método HTTP autenticado + SQL + log + **push service falso propio** que recibe el sobre real y devuelve 201/404/410/500/conexión rechazada. WhatsApp de dev neutralizado por variable de entorno, 0 mensajes reales. **19 criterios PASS, 3 NO VERIFICADOS** (R1 del `unregister` selectivo, el globo llegando a un navegador real, iOS/Firefox/Safari). Los 3 caminos de entrada PASS y el negativo PASS (el mensaje que recién deriva **no** duplica el aviso). LP-057 probado a nivel SQL contra el único de la columna generada; **la rama de revivir la fila soft-deleted, que el Implementador declaró sin probar, quedó cubierta y pasa**. Best-effort CRM-020 probado con 5 modos de falla incluida la clave VAPID basura. Privada de VAPID fuera del repo, confirmada en `user-secrets`. **1 defecto minor nuevo: CRM-029** — el anti-ruido se cae a un aviso por mensaje cuando la pestaña del chat queda abierta, porque `HiloParcial` estampa la lectura en cada tick con mensajes nuevos (3/3 reproducido); parte de defecto emitido, **sin fix aplicado**. **NO-GO hoy**: el certificado de producción vence el 2026-10-19 y sin HTTPS válido no hay push, y la privada no está cargada en el sitio. GO condicionado a esas 2 cosas + el chequeo manual de R1/globo real + decisión sobre CRM-029.
- 2026-09-14 (feature "4 frentes — combo con gancho", E1-E7): QA con la app ejecutada contra `olvidatacrm_dev`, sin navegador (Playwright MCP aislado del host) → HTTP autenticado + SQL + **harness de consola con WhatsApp falso y rollback** (dev tenía credenciales reales de Meta/Places y outbound despausado: se pausó y se usaron credenciales inválidas; 0 mensajes, 0 Places). Baseline HEAD en worktree para "idéntico a antes". IA real 7 mensajes, USD 0,149. **8/8 puntos obligatorios OK**; CU-30 a CU-35 PASS (CU-33 CA3 parcial, CU-35 CA2 sin datos). **1 defecto major, CRM-023** (selector "Frentes" nunca bindeaba en el GET del checklist → Build en silencio), auto-fix `traditional: true` en 2 vistas, re-verificado, catalogado en yml y en 32. R3 medido: 234/234 Pendiente → Presencia web. Primera corrida con el campo "Última validación de reglas cross-proyecto" (2026-09-14). **GO condicional**; manual pendiente: consola, tema oscuro y XHR real.
- 2026-08-28 (expansión nacional de outbound): QA de un **cambio de datos** en producción — 176 campañas + 176 industrias + 528 queries insertadas por 2 agentes en paralelo sobre 22 ciudades nuevas. Sólo lectura contra la base real, 0 escrituras. **GO, 7/7 PASS, 0 defectos.** Conteos exactos y rangos de `Id` perfectamente contiguos (142-317 / 142-317 / 881-1408), `ClaveRubro` única en 304/304 filas incluyendo las soft-deleteadas, `IndustriaCatalogoId` verificado en **las 22 ciudades** con firma idéntica y coincidente con el mapeo de las 108 preexistentes, las 6 campañas protegidas intactas (`UpdatedAt` ≤ 08-26; las únicas escrituras de hoy sobre filas viejas son del scheduler de 03:02-03:09), integridad referencial sin un solo huérfano, y las **528** queries con anclaje geográfico correcto (510 con la ciudad en el texto, 18 con localidad vecina + provincia), 0 duplicados y 0 colisiones con `GoogleMapsQueryUsadas`. Cupo real **465-469 msj/día** (49,4-49,9% de `CupoDiario`=940, lejos del techo y con tope global duro que lo hace inviolable). El incidente de MySqlConnector de la tanda A no dejó rastro — probado por contigüidad de `AUTO_INCREMENT`. **3 observaciones no bloqueantes**: el próximo barrido nocturno pasa de 91 a ~255 queries de Google Maps (el restock global recorre todas las campañas activas todos los días, sin filtrar por `Dias`) → salto de coste de API a vigilar; la demanda diaria quedó ~17% arriba de `MetaDiaria`=400 (preexistente, palanca `RebalancearMatrizAsync`); slug vs. `Nombre` cosmético. **Efecto colateral positivo no reportado por las tandas**: 266 contactos huérfanos adoptados (127 `Pendiente`), huérfanos totales de 460 a 333. Hallazgo preexistente cuantificado: **140 de 721 queries viejas** sin anclaje geográfico a su `Region`, con ~20 genuinamente ambiguas — no se tocó, queda como deuda.
- 2026-08-28: QA de la feature **matriz de módulos valorizados + borrador de propuesta MVP/FULL**, previa al primer deploy (código sin commitear, migración sólo en dev). Método: build propio en Release **2 veces** (0 errores / 13 advertencias preexistentes, antes y después del auto-fix), app levantada contra `olvidatacrm_dev`, **26 pantallas, 8 endpoints POST/AJAX y 29 generaciones de mensaje** por HTTP autenticado, con assertions SQL independientes. MCP `playwright` no disponible (declarado; residuo manual acotado al texto real de la pregunta 1 por WhatsApp). **Los 11 escenarios del Implementador: 11 PASS** (el #4 con 1 defecto, auto-fixeado). Seed verificado contra la base —**84/88/9/62** y los 9 rangos por rubro coincidiendo uno por uno—; la lectura inicial de 89/10 resultó ser 2 filas soft-deleteadas de datos de prueba, eliminadas al cerrar. Los 5 rubros sin matriz (incluido **Alquiler de inmuebles**, el hallazgo del Implementador) muestran el aviso, no un checklist vacío. Las **9 reglas de redacción**: PASS, con el truncado a 4 ítems verificado en el caso pedido (**Ganadería con 7 imprescindibles → "y 3 más"**) y **el bug del doble "y" confirmado como corregido leyendo la salida, no el código**. Wiring de "Sugerir" probado con **12 contactos reales** cubriendo los 3 vocabularios de `Contacto.Rubro`: 7 con matriz (incluido `estudio`, o sea el fix del mapeo funcionando, y `indumentaria-once` con sufijo de región), 5 con el comportamiento viejo intacto. Cuestionario del bot: `Questions["build"]` en **2 preguntas** con la numeración de emoji correcta, `Contacto.CantidadUsuarios` **sin un solo escritor ni lector** (por grep), y la tabla de decisión computada contra la base da **7 rubros al mecanismo nuevo + "Vinos y bebidas" al menú fijo**; los 2 hallazgos del Implementador (`MecanismoPregunta1Async` como fuente única en los 2 call sites, `ArmarPitchPostDolorAsync` reconociendo las 2 fuentes) verificados, con la prueba social real confirmada para los rubros nuevos. **El fix Farmacia/Contabilidad no reintroduce cotización automática**: rastreados todos los consumidores hasta el último (`industria?.Plan` sólo dentro de `if (PresupuestoCotizadoUsd.HasValue)`, campo que el bot ya nunca setea; `CotizaAutomatico` sigue en `false`). `.gitignore` efectivo y **ningún archivo de clave commiteado nunca** (`git log --all` sin resultados) — cierra la duda que el Implementador dejó abierta. Regresión del sprint ya deployado: 24 rutas sin 500, 0 `[ERR]`/`[FTL]`. **1 defecto: CRM-015 (major) — auto-fixeado.** Los módulos cuyo nombre empieza con sigla salían deformados en el texto que se copia al WhatsApp del cliente (`ABM Cuadrilla` → `aBM Cuadrilla`, `SEO básico y deploy` → `sEO…`, `CRM de WhatsApp` → `cRM…`): 9 de 84 módulos, los 9 imprescindibles, en 4 de los 9 rubros. Catalogado en `docs/qa/regresiones-manuales.yml` **antes** del fix, corregido con un guard de sigla inicial en `PropuestaMvpFullService.Minuscula()` (sin lógica de negocio nueva: restaura la intención ya declarada en el comentario del propio método), y re-verificado sobre **18 mensajes con 0 fallas** y sin regresión en los nombres que sí deben bajar la inicial. 4 observaciones no bloqueantes (interpretación de la regla 5, "y" duplicada que viene del nombre del módulo, inconsistencia matriz-con-0-MVP entre los 2 consumidores, comentario desactualizado en `RubroHelpers`). Estado dev restaurado (84/88/9/62). Estado: **GO para deploy de producción** (deploy no ejecutado, queda para el cliente; pendiente commitear y aplicar la migración en producción).
- 2026-08-27 (re-verificación acotada post-corrección): re-test de **CRM-007 / CRM-010 / CRM-012** tras la corrección del Implementador (§9), con app corriendo contra `olvidatacrm_dev` y assertions SQL independientes. **CRM-007 cerrado**: `ImpactoDelete` contrastado contra ground truth propio en **las 14 industrias** (no solo las 7 con datos) con coincidencia exacta —Retail 155, Laboratorios 104, Inmuebles 58, Utilities 38, Ganadería 35, Estudios 28, Farmacias 1, y 0 legítimo en las otras 7—, más reasignación real probada en ambas ramas (destino inválido → rechazado sin borrar nada; destino válido → contacto #158 `farmacia`→`estudio-palermo`, con auditoría estampada, quedando cubierto por la campaña activa #35, que es el círculo que M-B nunca cerraba). **CRM-010 cerrado**: el selector guarda `ClaveRubro`; alta real de un Referido (#442) que satisface el filtro completo de `SendDailyBatchAsync`; `Edit` conserva el rubro heredado y no lo pisa al editar otro campo. **CRM-012 cerrado**: `Alineadas` es propiedad calculada, sus 3 entradas coinciden con SQL independiente (0/19, 0/19, 0/18), y se forzó una divergencia real para ver la alerta disparar (5,3%/5,3%/0,0% → badge "Divergen"). **CRM-008 descartado por el cliente** (falsa alarma de la pasada anterior: se probó contra dev y se confundió con producción). Riesgo declarado por el Implementador (`BotFlowService` sin tocar) **confirmado**: los contactos con rubro reescrito por el bot (#194, #236) no son contados ni reasignados —son inalcanzables por construcción—, pero se detectó que la protección es **incidental y no una guarda explícita**: 18 contactos con conversación (17 en `AwaitingCategory` esperando respuesta + 1 `Completed`) conservan su `ClaveRubro` y sí quedan dentro del conteo/reasignación, contra lo que afirma el comentario del código → nuevo **CRM-014 (minor)**, que incluye además la colisión por mayúsculas entre la clave `farmacia` y el nombre de diálogo `"Farmacia"` (sin impacto hoy: 0 contactos). Build propio en Release **0 errores / 13 advertencias preexistentes**, 0 migraciones nuevas, 18 pantallas autenticadas todas 200, 0 errores en Serilog, dev restaurado y verificado. Ningún archivo de código modificado por QA. Estado: **GO para deploy de producción** (deploy no ejecutado, queda para el cliente).
- 2026-08-27: QA del sprint "corrección de bugs/gaps de auditoría completa + 3 mejoras" (17 items: B1-B7, G1-G7, M-A/M-B/M-C). **Primera pasada de QA de este proyecto con la aplicación efectivamente ejecutada** — build propio en Release (0 errores), app levantada contra `olvidatacrm_dev`, 12 pantallas y 6 endpoints POST/AJAX ejercitados por HTTP autenticado, con verificación del efecto real en base de datos antes/después de cada acción y restauración del estado de dev al terminar. MCP `playwright` no disponible en la sesión (declarado); sustituido por verificación HTTP + assertions sobre la BD. Resultado: **10 PASS, 4 PARCIAL, 2 FAIL, 1 PASS-con-observación**. Los 4 puntos que el Implementador marcó como delicados quedaron los 4 confirmados (B3 manda `ultimoIdVisto` en cada tick; G6 estampa `UpdatedAt`/`UpdatedByUserId` con el claim correcto en los 2 call sites, verificado en BD; G5 negocia bien los 2 invocadores; `EtiquetaErrorEnvio` quedó como evento). 7 defectos nuevos: **CRM-007** (major, bloqueante — `Industrias/ImpactoDelete`/`Delete` cuentan y reasignan por `IndustriaCatalogo.Nombre` cuando el vocabulario real de `Contacto.Rubro` es `CampanaOutboundIndustria.ClaveRubro`: devuelve `contactos: 0` para las 14 industrias mientras `/Bot/Salud` del mismo sprint reporta 425 huérfanos, dejando a G7 y M-B sin cumplir e informando algo falso), **CRM-008** (major, bloqueante — la migración `AddMensajeProgramado` no estaba aplicada; se aplicó en dev, falta en producción, sin ella `Chats/Detail` queda caído), **CRM-009** (B3: pestaña en background marca leído un entrante nuevo, contradiciendo la HU), **CRM-010** (B7: el Referido manual no entra al pipeline, misma causa raíz que CRM-007), **CRM-011** (G1: tope de reintentos cuenta fallos históricos, no consecutivos, sin reset), **CRM-012** (M-C: `Alineadas=true` hardcodeado), **CRM-013** (citas cruzadas incorrectas al catálogo). **Sin auto-fix**: la causa raíz de los bloqueantes es una decisión de diseño no tomada (vocabulario canónico de `Contacto.Rubro`), así que se escala al Implementador por regla del rol. Ningún archivo de código modificado por QA. B2 verificado con el escenario exacto de su HU (campaña Lunes+Miércoles: 400 msj/día en ambos, contra los 800 que daba el agrupamiento viejo) y G3 verificado end-to-end incluida la exclusión del ARR. Estado: **NO-GO para producción** por los 2 bloqueantes; **GO parcial** para los otros 15 items una vez aplicada la migración y revertido/degradado el modal de Industrias.
- 2026-07-25: QA del ajuste de UI en `Notifications/Index.cshtml` (ícono `fas fa-xmark` + modal SweetAlert2 reemplazando `confirm()` nativo). Método: revisión de código + diff contra HEAD para aislar el alcance de esta tarea de la feature previa de borrado (2026-07-24) + rebuild completo independiente (`dotnet build --no-incremental` → 0 errores, 9 warnings preexistentes idénticos a lo ya documentado). Confirmado: 2 íconos `fa-xmark` (0 `fa-trash` residual), 0 `confirm()`/`onsubmit` residual, patrón `Swal.fire` consistente con `Campanas/Index.cshtml`, `NotificationsController`/`NotificationService`/`INotificationService` sin ningún cambio atribuible a esta tarea (solo contienen lo ya documentado de "eliminar notificaciones"). Catálogo cross-proyecto reevaluado para items relevantes (KOI-001 PASS, resto N/A sin cambios). **Cero defectos.** Estado: **GO** para prueba manual del cliente.
- 2026-07-17: Primera pasada de QA funcional sobre la migración de BotPublicitario (HU-01 a HU-11, CU-01 a CU-06 y CU-10 a CU-12). Método: revisión de código completa por capa + recompilación + verificación de migraciones + playbook cross-proyecto (24 items preexistentes evaluados + 6 items nuevos catalogados: CRM-001 a CRM-006). Validados los 3 riesgos que señaló el implementador (CU-04 sin bug de lógica, Farmacia/Contabilidad comportamiento esperado, credenciales ausentes confirmado como bloqueo). Detectados 6 defectos nuevos no catalogados previamente (3 major: CRM-001 sin auditoría del toggle outbound, CRM-004 sin manejo de duplicado en batch de Google Maps, CRM-006 notificación in-app nunca implementada; 3 minor: CRM-002 UI de cambio de estado visible para Vendedor, CRM-003 ordenamiento de columna ignorado, CRM-005 categoría de fallback incorrecta en máquina de estados del bot). Por instrucción explícita del orquestador para esta tarea, ningún defecto nuevo (no catalogado previamente) fue auto-corregido en esta pasada — los 6 quedan documentados en `docs/qa/regresiones-manuales.yml` con `archivos_fix` sugeridos, pendientes de una pasada del Implementador. Recomendación: NO-GO para producción/uso comercial real hasta resolver los 3 defectos major; GO condicional para uso interno de Contactos/Industrias sin bot activo.
- 2026-07-21: QA de "campañas de contacto frío configurables" (CU-13/14/15, HU-12 a HU-16). Método: revisión de código completa contra Análisis/Diseño/Arquitectura + recompilación independiente + verificación de migración aplicada + corrida real de 20s confirmando seed (13 campañas) sin excepciones. Cobertura del catálogo cross-proyecto reevaluada para los items relevantes a la superficie nueva (KOI-001 PASS, 32-estándares N/A justificado — la pantalla no usa combo multi-select tradicional, GAN-003 PASS, resto sin cambios respecto a la pasada anterior). **Cero defectos funcionales detectados** — solo 2 observaciones de UX no bloqueantes (inconsistencia reload vs. DOM-update entre AgregarIndustria y el resto de las acciones AJAX; comparación de `ClaveRubro` no fuerza case-insensitive a nivel SQL, sin impacto real porque todas las claves ya se generan en minúsculas). Estado: **GO** para uso interno; pipeline outbound real queda sujeto al mismo criterio ya vigente (no activar `Standby=false` sin verificación manual + credenciales confirmadas).
- 2026-08-28: QA de un cambio de **datos** en producción (no de código): expansión de 93 queries de Google Maps sobre 33 `CampanaOutboundIndustria` + reset de racha/`Completa`, hecha por script descartable ya borrado. Método nuevo para el rol: sin build/deploy/navegador — consultas de sólo lectura contra la base real + lectura de `GoogleMapsService` para entender el consumo de los campos tocados. **Aprendizaje reutilizable**: cuando el cambio se aplica por SQL crudo, `UpdatedAt` NO se setea (lo setea EF, no la base), así que no sirve para identificar filas tocadas ni para detectar daño colateral — hay que identificar el universo por `CreatedAt` de las filas insertadas y validar el resto por **reconciliación de estado** (acá: las campañas `Completa=1` pasaron de 50 a 17 y los 17 reconcilian exacto contra 10 Ski + 5 Mercado Municipal + 2 descartadas por cobertura). Ayuda mucho que el scheduler nocturno corra a otra hora (03:02-03:09) que el script (03:49-03:50): permite separar escrituras por timestamp. Resultado: **GO**, 5/5 criterios PASS, 0 duplicados, 0 daño colateral, `ClaveRubro` intacto (verificado indirectamente vía historial de `GoogleMapsQueryUsadas`). 6 observaciones LOW de calidad geográfica (deriva Palermo→Belgrano en 4 campañas, Gran Mendoza etiquetado como Mendoza Capital, etc.), todas cosméticas porque se verificó en código que `CampanaQuery.Zona` nunca llega a la API de Google y `Contacto.Zona` no filtra ni rutea nada. 1 hallazgo preexistente ajeno al cambio: `Dieteticas Montevideo` (57) con `SinResultadosNuevos=1` pero `Completa=0` — única fila así en la base, la campaña no busca nunca y no aparece como agotada en la UI.
