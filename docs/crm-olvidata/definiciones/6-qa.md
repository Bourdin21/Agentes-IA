# Memoria - QA

## Proyecto: crm-olvidata — migración de BotPublicitario
## Ultima actualizacion: 2026-07-17

## Definiciones vigentes

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

## QA — campañas de contacto frío configurables (2026-07-21)

### 0. Alcance funcional validado

CU-13 (crear campaña), CU-14 (editar/pausar/reanudar), CU-15 (gestionar queries por industria), HU-12 a HU-16, sobre la implementación documentada en `5-implementador.md` (sección "Implementación de campañas de contacto frío configurables"). Sin máquina de estados que recorrer (confirmado en Análisis y Diseño: `Activa` es un flag simple).

**Método:** revisión de código completa por capa contra los 3 documentos de definición (1-analista, 2-diseñador, 3-arquitecto) + recompilación independiente de la solución + verificación de la migración aplicada + corrida real de la app (20 seg) para confirmar seed y arranque sin excepciones. **No se ejecutaron pruebas contra la app corriendo con navegador** (regla del estudio: QA no automatiza UI) ni contra WhatsApp/Google Maps reales (scheduler en `Standby=true`, no se activó a propósito para no arriesgar envíos). Los casos de UI se describen como procedimiento manual para que Joaquín los ejecute a mano.

**Build:** `dotnet build OlvidataCRM.slnx` → **Compilación correcta, 0 errores**, 4 warnings preexistentes (`NU1902` MailKit/MimeKit). Confirmado por este QA en corrida independiente, no solo por el reporte del implementador.

**Migración:** `dotnet ef migrations list` confirma `20260721155711_AddCampanasOutbound` aplicada, sin `(Pending)`.

**Seed:** corrida real de 20 segundos (`dotnet run --no-build`) — log confirma `"Campañas de contacto frío sembradas: 13"` sin excepciones en la primera corrida tras la migración; scheduler arrancó en `Standby=True` (default legacy preservado); no hubo errores de resolución de dependencias (confirma que `CampanasController`, `GoogleMapsService`, `OutboundCampaignService` con sus nuevas firmas resuelven correctamente en el contenedor DI).

### 1. Cobertura por caso de uso / historia

| # | Criterio | Resultado | Nota |
|---|---|---|---|
| CU-13 (crear) | No permite guardar sin al menos un día de envío | **PASS (código)** | `CampanasController.Create` valida `ArmarDias(model) == 0` antes de `ModelState.IsValid`. |
| CU-13 (crear) | `Activa` forzada a `false` al crear | **PASS** | Coherente con la guarda "no se puede activar sin industrias/queries" — evita el estado inconsistente de una campaña "activa" vacía incluso por un instante. |
| CU-13 (industrias) | Rechaza `ClaveRubro` ya asignada a otra campaña **activa** | **PASS (código)** | `AgregarIndustria` y `ValidarPuedeActivarAsync` comparan contra `CampanaOutbound.Activa` de otras campañas, no contra todas — coincide con la resolución de Arquitectura §1.a (el conflicto es solo entre campañas activas). |
| CU-13 (activar) | No permite `Activa=true` sin industrias, o con alguna industria sin queries | **PASS (código)** | `ValidarPuedeActivarAsync`, invocado desde `Edit` (POST) y `TogglePausa`. Mensaje señala explícitamente qué falta. |
| CU-14 (pausar/reanudar) | Pausar no afecta industrias/queries ni contactos en curso | **PASS (código)** | `TogglePausa` solo togglea `Activa`; no toca `Contacto` ni las relaciones. |
| CU-14 (eliminar) | Soft-delete en cascada (campaña + industrias + queries) | **PASS (código)** | `Delete` setea `DeletedAt` explícitamente en las 3 entidades relacionadas — necesario porque el query filter global de EF no cascadea entre entidades `SoftDestroyable` independientes (a diferencia de un `OnDelete(Cascade)` de FK real, que solo aplica a hard-delete). |
| CU-15 (agregar query) | Alta inline sin perder el resto del formulario | **PASS (código)** | `AgregarQuery` es un endpoint AJAX independiente del POST principal de `Edit`; la vista actualiza el DOM sin recargar. |
| CU-15 (eliminar última query) | Avisa si la industria queda sin poder buscar prospectos | **PASS (código)** | `EliminarQuery` calcula `esLaUltima` antes de borrar y devuelve `advertencia` solo si la campaña está activa — coherente con Diseño §1 Pantalla 8 ("no bloqueante, es una campaña ya creada"). |
| HU-12 | `Bot/Index` muestra resumen de campañas (activas/pausadas + nombres) con link a `Campanas/Index` | **PASS (código)** | `BotController.Index` arma `CampanasActivas`/`CampanasPausadas`/`CampanasResumen`; la vista los renderiza. |
| HU-13 (regresión) | `OutboundSchedulerService`/`OutboundCampaignService`/`GoogleMapsService` operan contra campañas, no diccionarios fijos | **PASS (código)** | Verificado que `RunDayByType`/`RubrosByDay`/`QueriesByRubro`/`RubrosRetirados`/`BotSettings.DailyLimit` (como límite único) ya no existen en el código — `grep` confirma cero referencias residuales. |
| HU-14/CU-13 | Crear campaña con industrias — flujo completo | **BLOCKED (E2E navegador)** | Lógica revisada por código; el flujo visual (Create → redirect a Edit → agregar industria por AJAX) no se probó en navegador real (regla del estudio). Ver procedimiento manual §7. |
| HU-15/CU-15 | Gestión de queries — flujo completo | **BLOCKED (E2E navegador)** | Idem — lógica revisada, no probado en navegador. |
| HU-16 | Pausar/reanudar puntual sin afectar standby global | **PASS (código)** | `TogglePausa` de `CampanasController` es independiente del `TogglePausa` de `BotController` (standby global) — no comparten estado ni lógica. |

### 2. Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Se reevaluaron solo los items potencialmente relevantes a la superficie nueva (el resto ya fue evaluado N/A para este proyecto en la pasada de QA de 2026-07-17 y no cambia con esta feature):

| id | aplica | resultado | acción |
|---|---|---|---|
| KOI-001 (SweetAlert2 fuera del `<form>`) | Sí | **PASS** | `Campanas/Index.cshtml` arma un `<form>` dinámico vía JS con el token antiforgery para pausar/eliminar (mismo patrón ya validado en `Industrias/Index.cshtml`). Los botones de industria/query dentro de `Edit.cshtml` no usan `.btn-swal-confirm` (usan `$.post` directo + SweetAlert2 manual para confirmaciones destructivas) — revisado, sin el bug de KOI-001 porque no dependen de `closest('form')`. |
| REG-010 / KOI-003/005/006 (link de sidebar sin controller, o rol sin acceso) | Parcial | **N/A** | `Campanas` no tiene entrada de sidebar propia (por diseño, se accede desde `Bot/Index`) — no aplica el patrón de "link roto". Policy `RequireSuperUsuario` verificada en el controller, coherente con el resto del sistema post-ajuste de roles del 2026-07-21. |
| 32-estándares (combo de Editar debe pre-cargarse con valores ya asignados) | Parcial | **N/A justificado** | `Campanas/Edit` no usa un combo multi-select tradicional para industrias (a diferencia de, por ejemplo, un Select2 multi de tags) — usa gestión por filas AJAX (acordeón), donde cada industria ya asignada se renderiza server-side directamente en el `@foreach` inicial (equivalente funcional a "pre-cargado", no hay combo que arranque vacío pese a tener datos). El único `<select>` de la pantalla (`#nuevaIndustriaCatalogoId`) es exclusivamente para **agregar** una industria nueva, nunca representa una selección ya existente que deba precargarse. |
| GAN-003 (`<script type="text/x-template">` con Tag Helpers adentro) | Sí (patrón revisado) | **PASS** | El JS de `Edit.cshtml` arma los nodos nuevos con jQuery (`$('<li>...</li>')`), no usa `<script type="text/x-template">` — no aplica el bug. |
| REG-001 (RowVersion MySQL) | No | **N/A** | Ninguna entidad nueva usa control de concurrencia optimista. |
| Resto del catálogo (REG-002/003/005/006/007/008/009, DN-001/002, GAN-001/002/004, VSF-001/002, CRM-001 a 006) | No | **N/A** | Sin cambios en las superficies que esos items cubren (Compras/Ventas/Devoluciones, pagos en cuotas, backfills, `<datalist>`, FK a estado terminal, y los 6 defectos ya resueltos de la migración de BotPublicitario) — se mantiene la evaluación de la pasada anterior. |

### 3. Observaciones (no bloqueantes, calidad de UX)

- **`AgregarIndustria` recarga la página completa** (`location.reload()`) tras agregar una industria, mientras que `EliminarIndustria`/`AgregarQuery`/`EliminarQuery` actualizan el DOM sin recargar. Inconsistencia menor de UX (no de funcionalidad): si el usuario tenía cambios sin guardar en la card "Datos de la campaña" al agregar una industria, esos cambios se pierden con el reload. No es un defecto funcional de CU-13/14/15 (ninguna historia de usuario pide "no perder cambios no guardados al agregar industria"), pero vale la pena unificar el patrón en una pasada de pulido si el cliente lo nota.
- **`ClaveRubro` se normaliza a minúsculas** (`ToLowerInvariant`) en `AgregarIndustria`, consistente con cómo se seedearon los 13 rubros y con `Contacto.Rubro` — pero la comparación `HashSet<string>.Contains`/`List<string>.Contains` usada en `OutboundCampaignService`/`ValidarPuedeActivarAsync` se traduce a SQL como comparación literal (la collation de MySQL, no `OrdinalIgnoreCase` de C#, decide sensibilidad a mayúsculas). No es un defecto observado — todas las claves ya se generan en minúsculas de forma consistente — pero es un punto a tener en cuenta si en el futuro se permite cargar `ClaveRubro` con mayúsculas desde algún otro punto de entrada.

### 4. Defectos detectados

**Ninguno.** No se encontraron defectos funcionales nuevos en esta pasada — las 2 observaciones de la sección anterior son de UX/robustez, no incumplimientos de un criterio de aceptación aprobado.

### 5. Riesgos de liberación y mitigaciones

- **Sin prueba E2E real de envío/búsqueda:** el pipeline outbound completo (campañas → `SendDailyBatchAsync`/`SearchDailyAsync` reales) no se ejecutó contra WhatsApp/Google Maps reales. Mitigación: el scheduler sigue en `Standby=true` (no cambia nada en producción hasta que Joaquín lo active manualmente); la lógica de selección de candidatos por campaña fue revisada línea a línea contra el comportamiento anterior.
- **Sin tope global de límite diario** (decisión explícita del cliente, heredada de Análisis/Arquitectura) — riesgo de negocio, no de código: si se activan muchas campañas con límites altos el mismo día, no hay freno automático.
- **Recomendación antes de activar `Standby=false` por primera vez con este cambio:** verificar en `Campanas/Index` que las 13 campañas migradas automáticamente tienen el día/límite/template esperado, y hacer una corrida manual de `IOutboundCampaignService`/`IGoogleMapsService` fuera de horario (mismo procedimiento que ya usaba el estudio en el ciclo de QA anterior) antes de la primera corrida real con esta nueva fuente de datos.

### 6. Procedimiento de prueba manual (para Joaquín)

**A. CU-13 — Crear campaña y agregar industria**
1. Login SuperUsuario. Ir a Bot / Outbound → "Ver campañas".
2. "Nueva campaña": nombre "Prueba QA", sin marcar ningún día, Guardar. **Esperado:** rechaza con mensaje "Elegí al menos un día".
3. Marcar "Martes", límite 10, template el único disponible, Guardar. **Esperado:** redirige a Edit de la campaña recién creada.
4. En "Industrias y queries de búsqueda", clave de rubro "pruebaqa", sin industria de catálogo, click "+". **Esperado:** aparece un panel de acordeón nuevo, expandido, con aviso "sin queries".
5. Intentar activar el switch "Activa" y Guardar. **Esperado:** rechaza, mensaje señala que la industria "pruebaqa" no tiene queries.
6. Agregar una query ("test La Plata" / "La Plata") dentro del panel. **Esperado:** aparece en la lista sin recargar la página, el contador de queries del acordeón se actualiza.
7. Activar el switch y Guardar. **Esperado:** ahora sí permite activar.
8. Eliminar la campaña de prueba desde `Campanas/Index` (confirmación SweetAlert2). **Esperado:** desaparece del listado.

**B. CU-13 — Conflicto de rubro entre campañas activas**
1. En una campaña activa existente (una de las 13 migradas, ej. "Comercio"), anotar una de sus claves de rubro (ej. "comercio").
2. Crear una campaña nueva y en Edit intentar agregar la industria con clave "comercio". **Esperado:** rechaza, mensaje indica que ya está en la campaña "Comercio".

**C. HU-12 — Resumen en Bot/Index**
1. Ir a Bot / Outbound. **Esperado:** la card "Campañas de contacto frío" muestra el conteo de activas/pausadas y los nombres con su día corto (ej. "Comercio (Mar)").

### Estado go/no-go

**GO** para uso interno (gestión de campañas/industrias/queries vía UI) — no depende de credenciales externas ni de defectos pendientes. El pipeline outbound real con estas campañas sigue sujeto al mismo criterio ya vigente en el proyecto: no activar `Standby=false` sin que Joaquín haya verificado manualmente el cronograma migrado y confirmado las credenciales de Meta/Google Maps.

## Historial de ajustes
- 2026-07-17: Primera pasada de QA funcional sobre la migración de BotPublicitario (HU-01 a HU-11, CU-01 a CU-06 y CU-10 a CU-12). Método: revisión de código completa por capa + recompilación + verificación de migraciones + playbook cross-proyecto (24 items preexistentes evaluados + 6 items nuevos catalogados: CRM-001 a CRM-006). Validados los 3 riesgos que señaló el implementador (CU-04 sin bug de lógica, Farmacia/Contabilidad comportamiento esperado, credenciales ausentes confirmado como bloqueo). Detectados 6 defectos nuevos no catalogados previamente (3 major: CRM-001 sin auditoría del toggle outbound, CRM-004 sin manejo de duplicado en batch de Google Maps, CRM-006 notificación in-app nunca implementada; 3 minor: CRM-002 UI de cambio de estado visible para Vendedor, CRM-003 ordenamiento de columna ignorado, CRM-005 categoría de fallback incorrecta en máquina de estados del bot). Por instrucción explícita del orquestador para esta tarea, ningún defecto nuevo (no catalogado previamente) fue auto-corregido en esta pasada — los 6 quedan documentados en `docs/qa/regresiones-manuales.yml` con `archivos_fix` sugeridos, pendientes de una pasada del Implementador. Recomendación: NO-GO para producción/uso comercial real hasta resolver los 3 defectos major; GO condicional para uso interno de Contactos/Industrias sin bot activo.
- 2026-07-21: QA de "campañas de contacto frío configurables" (CU-13/14/15, HU-12 a HU-16). Método: revisión de código completa contra Análisis/Diseño/Arquitectura + recompilación independiente + verificación de migración aplicada + corrida real de 20s confirmando seed (13 campañas) sin excepciones. Cobertura del catálogo cross-proyecto reevaluada para los items relevantes a la superficie nueva (KOI-001 PASS, 32-estándares N/A justificado — la pantalla no usa combo multi-select tradicional, GAN-003 PASS, resto sin cambios respecto a la pasada anterior). **Cero defectos funcionales detectados** — solo 2 observaciones de UX no bloqueantes (inconsistencia reload vs. DOM-update entre AgregarIndustria y el resto de las acciones AJAX; comparación de `ClaveRubro` no fuerza case-insensitive a nivel SQL, sin impacto real porque todas las claves ya se generan en minúsculas). Estado: **GO** para uso interno; pipeline outbound real queda sujeto al mismo criterio ya vigente (no activar `Standby=false` sin verificación manual + credenciales confirmadas).
