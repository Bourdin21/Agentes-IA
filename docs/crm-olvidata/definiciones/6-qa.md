# Memoria - QA

## Proyecto: crm-olvidata — migración de BotPublicitario
## Ultima actualizacion: 2026-08-28

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

## QA — ajuste UI de Notificaciones: ícono X + SweetAlert2 (2026-07-25)

### 0. Alcance funcional validado

Ajuste de UI puntual sobre `Views/Notifications/Index.cshtml`, feature ya en producción ("eliminar notificaciones"): (1) reemplazo de ícono `fas fa-trash` → `fas fa-xmark` en el botón de eliminar individual y en "Eliminar leídas"; (2) reemplazo del `confirm()` nativo del navegador por un modal `Swal.fire`, sobre el patrón de confirmación ya validado en `Campanas/Index.cshtml`. Base leída: `1-analista-funcional.md` (Discovery+Análisis exprés 2026-07-24), `2-disenador-funcional.md` (Diseño exprés 2026-07-24), `5-implementador.md` (implementación 2026-07-25). Cliente pidió pasar este ajuste cosmético por el flujo completo del orquestador (Presupuesto salteado, mismo precedente ya usado 2 veces en el proyecto).

**Método:** revisión de código completa del único archivo tocado + diff contra `HEAD` de los 4 archivos con cambios pendientes de commit (`INotificationService.cs`, `NotificationService.cs`, `NotificationsController.cs`, `Views/Notifications/Index.cshtml`) para aislar qué pertenece a esta tarea vs. a la feature previa de "eliminar notificaciones" (2026-07-24) + recompilación independiente de la solución. **No se probó en navegador** (regla del estudio) — verificación 100% por código, con procedimiento manual entregado para que el cliente la ejecute a mano.

**Build:** `dotnet build OlvidataCRM.slnx --no-incremental` desde `C:\Sistemas\olvidatasoft-crm` → **Compilación correcta, 0 errores**, 9 warnings — todos preexistentes y confirmados idénticos a los ya documentados (`NU1902` MailKit/MimeKit ×4, `CS0114` `HomeController.StatusCode` ×2 por doble referencia de proyecto). Confirmado por este QA en corrida independiente (no solo por el reporte del implementador).

### 1. Cobertura por criterio de aceptación

| Criterio (pedido del cliente / Diseño 2026-07-24) | Resultado | Evidencia |
|---|---|---|
| Ícono del botón de eliminar individual = X, no papelera | **PASS** | `Views/Notifications/Index.cshtml` línea 61: `<i class="fas fa-xmark"></i>` dentro del form `Delete`. `grep "fas fa-trash"` sobre el archivo → 0 coincidencias. |
| Ícono del botón "Eliminar leídas" = X, no papelera | **PASS** | Línea 18: `<i class="fas fa-xmark me-1"></i>`. |
| `confirm()` nativo reemplazado 100% por SweetAlert2 en ambos flujos de borrado | **PASS** | `grep "confirm("` sobre el archivo → 0 coincidencias; `grep "onsubmit"` → 0 coincidencias. Los 2 `<form>` (`form-delete-notif`, `form-delete-all-read`) perdieron el atributo `onsubmit` y la confirmación pasa 100% por los 2 handlers `$(document).on('submit', ...)` en `@section Scripts`. |
| Patrón `Swal.fire` + `.then(isConfirmed → submit)` bien formado y consistente con el resto del proyecto | **PASS** | Comparado línea a línea contra `Views/Campanas/Index.cshtml` (`icon:'warning'`, `showCancelButton:true`, `confirmButtonText:'Sí, eliminar'`, `cancelButtonText:'Cancelar'`, `confirmButtonColor:'#ef4444'`, `.then(result => if(result.isConfirmed) ...)`). Mismos textos y color, mismo criterio funcional; única diferencia justificada: acá se intercepta el evento `submit` de un `<form>` real (no hay DataTable/botón suelto de por medio), en vez de armar un `<form>` dinámico como hace `Campanas/Index.cshtml` — patrón más simple y igual de robusto para este caso (2 forms server-rendered, no filas dinámicas). |
| `NotificationsController.cs`/`NotificationService.cs`/`INotificationService.cs` sin tocar por esta tarea | **PASS** | `git diff HEAD` sobre los 3 archivos: el único contenido son `DeleteAsync`/`DeleteAllReadAsync` (interfaz + implementación) y las acciones `Delete(id)`/`DeleteAllRead()` del controller — exactamente lo que documenta la entrada previa "eliminar notificaciones" (2026-07-24), sin ninguna línea adicional atribuible a la tarea de ícono/SweetAlert2 de hoy. |
| Comportamiento funcional de fondo (qué se elimina, cuándo, antiforgery) idéntico a antes del cambio | **PASS** | Los `<form>` conservan `asp-controller`/`asp-action`/`asp-route-id`/`method="post"` sin modificar (tag helper sigue inyectando el token antiforgery automáticamente); único cambio en cada `<form>` es agregar una `class` para poder targetearlos por selector CSS. `Delete(id)`/`DeleteAllRead()` conservan `[ValidateAntiForgeryToken]` sin cambios. |

### 2. Máquina de estados

No aplica — confirmado en Análisis y Diseño de este ajuste ("Activa"/flags no forman parte de este cambio; no hay máquina de estados involucrada, es un ajuste cosmético sobre una acción de borrado ya existente).

### 3. Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Se reevaluaron solo los items potencialmente relevantes a la superficie tocada (el resto ya fue evaluado N/A para este proyecto en pasadas anteriores y no cambia con este ajuste puntual de un solo archivo de Vista):

| id | aplica (sí/no/N/A) | resultado | acción |
|---|---|---|---|
| KOI-001 (botón SweetAlert2 fuera del `<form>`, `closest('form')` falla) | Sí (patrón revisado) | **PASS** | No aplica el bug: acá no hay un botón *fuera* de su form apoyándose en `closest('form')` — el botón `type="submit"` vive *dentro* del propio `<form>` y el JS escucha el evento `submit` del form mismo (`$(document).on('submit', '.form-delete-notif', ...)`), captura `var form = this` y llama `form.submit()` tras confirmar. Patrón distinto y más simple que el de KOI-001, sin su causa raíz. |
| REG-010 / KOI-003/005/006 (sidebar / rutas rotas) | No | **N/A** | Sin cambios de sidebar ni de rutas — mismo controller/acciones ya existentes. |
| CRM-002 (control visible para rol sin permiso) | No | **N/A** | Sistema opera con único rol (`SuperUsuario`) desde 2026-07-21; no hay gating por rol en esta pantalla. |
| Resto del catálogo (REG-001/002/003/005/006/007/008/009, KOI-002, DN-001/002, GAN-001/002/003/004, VSF-001/002, CRM-001/003/004/005/006) | No | **N/A** | Sin cambios en las superficies que esos items cubren (Compras/Ventas/Devoluciones/pagos/backfills/máquinas de estado del bot/outbound/Google Maps) — evaluación sin cambios respecto a las pasadas anteriores de este proyecto. |

### 4. Defectos detectados

**Ninguno.** El ajuste es cosmético, acotado a un solo archivo de Vista, y coincide exactamente con lo definido en Diseño (2026-07-24) e implementado (2026-07-25). No se encontró ningún caso donde el ícono siga siendo papelera, quede algún `confirm()` residual, o donde el patrón `Swal.fire` esté mal formado.

### 5. Auto-fixes aplicados

Ninguno — no se detectó ningún defecto a corregir en esta pasada.

### 6. Riesgos de liberación y mitigaciones

- **Riesgo técnico mínimo:** cambio 100% de presentación sobre una acción de borrado ya probada y en producción; no hay lógica de negocio nueva ni cambio de contrato de datos.
- **Sin prueba de navegador propia (regla del estudio):** la verificación en caliente (ver el ícono real, abrir el modal, cancelar/confirmar) queda a cargo del cliente — ver procedimiento manual abajo.
- **Working tree con 4 archivos sin commitear** (`INotificationService.cs`, `NotificationService.cs`, `NotificationsController.cs`, `Views/Notifications/Index.cshtml`, todos correspondientes a la feature "eliminar notificaciones" + este ajuste, ninguno de otra tarea) — no bloquea el GO funcional, pero se deja registrado para que el cliente decida cuándo commitear/deployar.

### 7. Pruebas mínimas ejecutadas por este QA

- `git diff HEAD` de los 4 archivos modificados, para aislar exactamente qué pertenece a esta tarea vs. a la feature previa de borrado de notificaciones.
- `grep` sobre `Views/Notifications/Index.cshtml`: 0 coincidencias de `fas fa-trash`, `confirm(`, `onsubmit`; 2 coincidencias de `fas fa-xmark` (una por cada botón de eliminar).
- Comparación línea a línea del bloque `Swal.fire(...).then(...)` contra `Views/Campanas/Index.cshtml`.
- `dotnet build OlvidataCRM.slnx --no-incremental` (rebuild completo, no incremental) → 0 errores, 9 warnings preexistentes confirmados idénticos a los ya documentados, ninguno nuevo.

**No ejecutado (fuera de alcance de este agente):** prueba en navegador real (ver el modal, clickear, confirmar/cancelar) — regla del estudio, queda como hand-off al cliente.

### 8. Procedimiento de prueba manual (para Joaquín)

1. Ir a Notificaciones con al menos 1 notificación leída y 1 no leída. **Esperado:** el ícono de "Eliminar" (individual, a la derecha de cada notificación) y de "Eliminar leídas" (header) se ven como una X, no como una papelera.
2. Click en "Eliminar" de una notificación individual. **Esperado:** aparece un modal (no el diálogo gris nativo del navegador) con título "¿Eliminar esta notificación?", botones "Sí, eliminar" (rojo) / "Cancelar".
3. Click en "Cancelar". **Esperado:** no pasa nada, la notificación sigue en la lista al recargar.
4. Repetir el borrado y click en "Sí, eliminar". **Esperado:** la notificación desaparece de la lista.
5. Con al menos 1 notificación leída, click en "Eliminar leídas". **Esperado:** modal con título "¿Eliminar todas las notificaciones leídas?" y texto "Esta acción no se puede deshacer.". Cancelar no borra nada; confirmar borra solo las leídas (las no leídas quedan intactas).
6. Regresión: "Marcar todas leídas" y "Marcar leída" (individual) siguen funcionando igual que antes (no se tocaron en este ajuste).

### Estado go/no-go

**GO** para que Joaquín pruebe manualmente y, si el resultado visual coincide con lo esperado en los 6 pasos de arriba, dé por cerrado el ajuste. Sin defectos encontrados, build limpio, sin cambios fuera del alcance de presentación autorizado.

## QA — corrección de bugs/gaps de auditoría completa + 3 mejoras (2026-08-27)

### 0. Alcance funcional validado

QA sobre los 17 items del sprint cerrado por el Implementador el 2026-08-27 (B1-B7 bugs, G1-G7 gaps, M-A/M-B/M-C mejoras), contra los criterios de aceptación de `2-disenador-funcional.md` §7. Checkout local `C:\Sistemas\olvidatasoft-crm`, working tree sin commitear (25 archivos modificados + 10 nuevos). **Sin deploy** — fuera de alcance por instrucción explícita.

**Método — esta es la primera pasada de QA de este proyecto con la app efectivamente ejecutada:**

- `dotnet build -c Release --no-incremental` → **Compilación correcta, 0 errores**, 13 advertencias (todas preexistentes: `NU1902` MailKit/MimeKit, `CS8524`, `CS0114`). Confirmado por este QA en corrida propia, no tomado del reporte del Implementador.
- **App levantada localmente** (`http://localhost:5199` + `https://localhost:5443`, `ASPNETCORE_ENVIRONMENT=Development`) contra `olvidatacrm_dev`, autenticado como SuperUsuario (`no-reply@olvidata.com.ar`), y ejercitada por HTTP real: 12 pantallas + 6 endpoints POST/AJAX.
- **Consultas directas a `olvidatacrm_dev`** (MySQL 8.0) antes/después de cada acción, para verificar el efecto real en datos y no solo la respuesta HTTP.
- Revisión de código línea por línea del diff completo (`git diff` + archivos nuevos).
- **Servidor MCP `playwright` NO disponible en esta sesión** (no expuesto entre las herramientas del agente). Se declara explícitamente según `33-verificacion-automatizada-qa.instructions.md`. Se sustituyó por verificación HTTP + assertions sobre la base de datos, que cubre todo lo objetivamente chequeable de este sprint salvo lo estrictamente visual (render de toasts/modales SweetAlert2, que quedan en el procedimiento manual).
- **Datos de dev restaurados** al estado previo al terminar (campañas 27/28/29, contactos 194/236, industria #11, cliente de prueba borrado). Verificado post-restauración.

**Cambio de estado del entorno de dev (necesario y declarado):** la migración `20260827005735_AddMensajeProgramado` **no estaba aplicada** en `olvidatacrm_dev` — el arranque tiraba `Table 'olvidatacrm_dev.mensajesprogramados' doesn't exist` en loop cada 60s y `Chats/Detail` era inalcanzable. Se aplicó (`dotnet ef database update`) para poder probar. Ver defecto **CRM-008**: esa migración es parte de este release candidate y **falta aplicarla en producción**.

### 1. Cobertura por historia de usuario (17 items del Diseño §7)

| Item | Criterio de aceptación | Resultado | Evidencia |
|---|---|---|---|
| **B1** — truncado defensivo | Mensaje largo se guarda truncado; error de otro tipo no aborta la campaña | **PASS** | `MensajeriaHelpers.Truncar` (2000/500, coincide con `AppDbContext:117-118`). Aplicado en los 4 `new ContactoRespuesta` sueltos de `BotFlowService` (:339, :373, :390, :1039) y en `LogRespuesta` (:948), que es el punto único de las 8 escrituras del guion — cobertura completa verificada call-site por call-site. `catch (DbUpdateException)` + `ChangeTracker.Clear()` agregado por contacto en `SendDailyBatchAsync` y `ProcessFollowUpsAsync`. El `Clear()` es correcto y necesario (sin él la entidad rota se arrastra al contacto siguiente). |
| **B2** — rebalanceo por día individual | Campaña Lunes+Miércoles pesa en AMBOS días; el resumen coincide con el volumen real | **PASS (verificado en vivo)** | Escenario armado en dev: campaña 27 (Lunes), 28 (Miércoles), 29 (Lunes+Miércoles, `Dias=5`), las 3 al 30%. `CupoDiario=940`, `MetaDiaria=400` → `targetPct=42,553%`. Tras `POST /Bot/RebalancearMatriz`: las 3 quedaron en **21,28%**, y la carga real resultante fue **Lunes 42,56% = 400 msj** y **Miércoles 42,56% = 400 msj** — exactamente la meta. Con el agrupamiento viejo por combinación de flags, cada una habría escalado a 42,55% por separado y el Lunes real habría sido 85,1% = **800 msj (2× la meta)**. Datos restaurados. |
| **B3** — polling no pisa "última lectura" | Chat abierto en otra pestaña + contacto escribe → se marca "No leído" pese al polling | **PARCIAL** | 3 ramas medidas contra la DB sobre el contacto #194 (`MaxRespId=4`): **(A)** `HiloParcial/194?ultimoIdVisto=4` (sin novedad) → `FechaUltimaLecturaAgente` intacta en `2020-01-01` y `MarcadoNoLeidoManual=1` conservado → **el bug original está corregido**. **(B)** `HiloParcial/194` sin parámetro (fallback legacy) → pisa a `now` y borra la marca (esperado por diseño, ver riesgo de ventana de deploy). **(C)** `HiloParcial/194?ultimoIdVisto=3` (simula mensaje entrante nuevo) → **pisa `FechaUltimaLecturaAgente` y borra `MarcadoNoLeidoManual`**, es decir el chat NO queda "No leído". Ver defecto **CRM-009**. Cableado del JS verificado en el HTML renderizado: `_ChatThread` emite `data-msg-id` en cada burbuja/evento, las burbujas son hijas directas de `#chatThread` (`.children('[data-msg-id]')` las alcanza), y `Url.Action("HiloParcial")` renderiza `'/Chats/HiloParcial/'` **sin** arrastrar el `id` ambiente. |
| **B4** — etiquetas de evento sincronizadas | Nunca ver un mensaje de diagnóstico del bot como burbuja saliente nuestra | **PASS (verificado en vivo)** | Barrido exhaustivo de los 14 literales de `Pregunta` que `BotFlowService` escribe (`LogRespuesta` + `ProcesarBajaAsync` + los `new ContactoRespuesta` sueltos): **los 14 están en `EtiquetasDeEvento`**, y el caso dinámico (`LogRespuesta(contacto, pregunta, text)` :740) cae al `else` por diseño correcto (ahí `Pregunta` sí es texto real enviado). Render real: `GET /Chats/Detail/7` devuelve `<div class="chat-evento" data-msg-id="1">Consulta inicial: ...` — no burbuja saliente. (Nota menor: los comentarios `⟵B4 BotFlowService:NNN` tienen las líneas corridas 3-6 posiciones; los literales son correctos.) |
| **B5** — bloquear rename con campañas activas | Renombrar template en uso se bloquea con mensaje; editar el texto sigue permitido | **PASS (verificado en vivo)** | `POST /Templates/Edit` con `Nombre=olv_frio_v4_RENAMED` sobre `olv_frio_v3` (26 campañas activas) → HTTP 200 sin redirect, `field-validation-error data-valmsg-for="Nombre"`: *"26 campaña(s) activa(s) usan este template por su nombre actual ('olv_frio_v3')…"*. DB: nombre **sin cambiar**. Mismo POST con el nombre original y texto editado → **302 a `/Templates`**, cambio aplicado. Ambas ramas correctas. |
| **B6** — fórmula única "Respuesta → Presupuesto" | El número es el mismo en Bot/Outbound, Contactos/Pipeline y Campañas/Dashboard | **PARCIAL** | Fórmula centralizada en `MensajeriaHelpers.TuvoPresupuesto`/`TuvoPresupuestoExpr` y consumida por las 3 pantallas — verificado en código. **Bot/Index y Contactos/Pipeline ahora coinciden exactamente: 199 enviados / 19 respondieron** (antes Pipeline calculaba sobre los 433 contactos totales). **Campañas/Dashboard sigue dando 198 / 18**, porque su universo base es deliberadamente más angosto (`FechaPrimerEnvio != null && Rubro != null` + tiene que mapear a una campaña). El Diseño §7 solo pedía alinear el universo de *Pipeline*, así que la implementación cumple el diseño, pero **el criterio literal de la HU ("los 3 números") no se cumple** y la prueba #4 del Implementador no es un check válido de PASS/FAIL. Además, con los datos de dev `conPresupuesto = 0` en las 3 pantallas, así que la parte de *fórmula* (las 3 señales) quedó verificada solo por código, no por datos. |
| **B7** — canal Referido desde la UI | Cargar un Referido a mano y que **entre al circuito ya construido** (template dedicado, prioridad de cupo) | **PARCIAL** | La mitad de carga funciona: `CanalOrigen`/`ReferidoPor`/`MotivoReferido` presentes y persistidos en Create y Edit (partial compartido `_CamposCanalYPresupuesto`, incluido por ambas vistas; `ContactoEditViewModel : ContactoCreateViewModel` hereda las 4 props). `NormalizarReferido` descarta los datos de referido si el canal final no es Referido — correcto. **Pero el contacto NO entra al pipeline outbound**: `Contactos/Create` escribe `Rubro` = `IndustriaCatalogo.Nombre` (ej. `"Farmacias"`), mientras `SendDailyBatchAsync:183` filtra por `claves.Contains(c.Rubro)` contra `CampanaOutboundIndustria.ClaveRubro` (ej. `"farmacia"`). Nunca matchea. Ver defecto **CRM-010** (misma causa raíz que CRM-007). |
| **G1** — templates de catálogo con N placeholders | Template de 4-5 placeholders se asigna y envía sin tocar código; el fallo se ve en el contacto | **PASS (código)** / **BLOCKED (E2E)** | `BuildComponentsDinamico` + `ContarPlaceholders` (cuenta índices `{{N}}` **distintos**, correcto contra la semántica de Meta), con 8 campos genéricos disponibles y fallback a los 3 históricos si no hay texto — retrocompatible exacto para templates de 3. `RenderMensajeFrio` convierte `{{N}}` (base 1, Meta) a `{N-1}` (base 0, `string.Format`) — bug real que habría dejado `{1}` crudo en el hilo. `RegistrarFalloEnvioAsync` + `MaxIntentosFallidosPorContacto=3` implementados. **E2E bloqueado**: exige envío real contra Meta. Ver defecto **CRM-011** (el tope cuenta fallos históricos totales, no consecutivos). |
| **G2** — corrida manual con shuffle + `UltimaCorridaUtc` | Corrida manual a las 8am impide que el scheduler de 9:30 reprocese; sin sesgo por Id | **PASS (código)** / **NO EJECUTADO (E2E, deliberado)** | Shuffle `OrderBy(c => (c.Id + hoyAr) % 997)` subido a `CampanasActivasHoyAsync`, que es efectivamente el único punto por el que pasan la corrida manual y la automática (verificado). `MarcarCorridaAsync` sella `UltimaCorridaUtc` al final de cada campaña **y** en la rama `pendientes.Count == 0`; `OutboundSchedulerService:101` ya saltea por `yaCorrioHoy`, así que el circuito cierra. Sellado correctamente omitido cuando el cupo global se agota antes del `break`. **No se ejecutó `Bot/EjecutarAhora`**: el scheduler local corría con `standby=False` y dispararlo habría intentado envíos reales de WhatsApp a 234 contactos pendientes. Queda como prueba manual. |
| **G3** — `PrimerAnioGratis` en el alta de Cliente | Marcarlo al convertir; el ARR del Dashboard no lo cuenta | **PASS (verificado end-to-end)** | Switch presente en `_ConvertirClienteModal` con su `<input type="hidden" value="false">` compañero (patrón correcto de checkbox de ASP.NET). `POST /Clientes/ConvertirDesdeContacto` con `PrimerAnioGratis=true` sobre el contacto #194 en `Cerrado` → Cliente creado con **`PrimerAnioGratis=1`** en DB. `/Negocio/Dashboard`: **"1 Clientes activos"** pero **"USD 0 Ticket promedio real"**, **"USD 0 de USD 15.000 — Avance hacia la meta"**, **"USD 0 Ingresos totales"** — el ARR efectivamente lo excluye. Cliente de prueba eliminado. |
| **G4** — `PresupuestoCotizadoUsd` editable | Cargarlo a mano desde la ficha; las lecturas dejan de estar vacías | **PASS** | Presente en Create y Edit (`name="PresupuestoCotizadoUsd"` renderizado en ambas, HTTP 200), persistido en ambos handlers, con `[Range(0, 1_000_000)]`. |
| **G5** — acciones AJAX devuelven JSON | Toast de confirmación/error en la lista; el form de Detail sigue redirigiendo | **PASS (verificado en vivo, ambos invocadores)** | `POST /Chats/MarcarNoLeido` **con** `X-Requested-With: XMLHttpRequest` → `application/json`, `{"ok":true,"mensaje":"Conversación marcada como no leída."}`. **Sin** el header (form POST normal de `Chats/Detail`) → **302 a `/Chats?fecha=hoy&interaccion=todos`**, sin volcado de JSON. `MarcarTodosLeidos` → JSON siempre (único invocador es AJAX, correcto). JS: `.done(manejarRespuesta)/.fail(manejarError)` reemplaza al `.always()` ciego, y la lista solo se refresca con `ok=true`. jQuery agrega el header solo en llamadas AJAX same-origin, así que la negociación es fiable. El render visual del toast queda para la prueba manual. |
| **G6** — `ExecuteUpdateAsync` con auditoría | Rápido y sin consumo proporcional al total | **PASS (verificado en vivo, incluida la auditoría)** | `POST /Chats/MarcarTodosLeidos` con `Fecha=todos` → `{"ok":true,"mensaje":"4 conversaciones marcadas como leídas."}` en **27 ms**, un solo `UPDATE`. DB: los 4 contactos con `FechaUltimaLecturaAgente`/`UpdatedAt` idénticos y **`UpdatedByUserId = 6cdb16cd-7a0c-4879-a4a2-0a8051d63706`**, que es exactamente el Id del SuperUsuario en `AspNetUsers`. **El stamping manual es correcto en los 2 call sites**: usa `ClaimTypes.NameIdentifier`, el mismo claim que `AppDbContext.StampSoftDestroyable` (:333). El segundo call site (`IndustriasController.Delete` con `reasignarA`) también se verificó en vivo y estampó el mismo GUID. `QueryFiltrada` parte de `_db.Contactos`, así que el filtro global de soft-delete se conserva. |
| **G7** — aviso al eliminar industria con contactos | El sistema dice cuántos contactos quedan sin campaña que los alcance | **FAIL** | Mitad correcta / mitad rota. **`CampanasController.EliminarIndustria` es correcto** (cuenta por `industria.ClaveRubro`, el vocabulario real). **`IndustriasController.ImpactoDelete`/`Delete` son incorrectos**: cuentan por `IndustriaCatalogo.Nombre`. Medido en vivo: `ImpactoDelete` devuelve **`contactos: 0` para las 14 industrias del catálogo**, mientras `/Bot/Salud` del mismo sprint reporta **425 contactos huérfanos**. El modal renderiza *"Ningún contacto tiene ese rubro asignado. No hay impacto."* — la misma afirmación engañosa que G7 venía a eliminar, ahora con apariencia de dato calculado. Ver defecto **CRM-007**. |
| **M-A** — constante de dominio compartida | Agregar una etiqueta saliente se hace en un solo lugar | **PASS** | `MensajeriaHelpers` en `Application` es la fuente única; `ChatsController`, `OutboundCampaignService`, `VentanaExpiracionSchedulerService` y `MensajesProgramadosSchedulerService` consumen alias `const` que apuntan a ella. Corrigió de paso 2 desincronizaciones reales: `VentanaExpiracionSchedulerService` tenía literales crudos y le faltaba `[Follow-up]` en las 3 subqueries de "último mensaje entrante". `EtiquetaErrorEnvio` agregada a las 8 repeticiones de la condición. La decisión de dejar las condiciones inline (con `const`, que el compilador inlinea en el árbol de expresión) es correcta y preserva la traducción a SQL — confirmado empíricamente: `/Chats`, `/Bot` y `/Bot/Salud` devuelven 200 con datos, sin caer en MH-001. |
| **M-B** — reclasificación asistida | Reasignar los contactos a otra categoría en el mismo paso | **FAIL** | Inerte en la práctica y conceptualmente incorrecto cuando dispara. Demostrado en vivo: se plantó un contacto con `Rubro = "Finanzas personales (gestión completa)"` (un `Nombre` de catálogo); `ImpactoDelete/11` entonces sí devolvió `contactos: 1`, confirmando que el conteo **solo** funciona con ese vocabulario. `POST /Industrias/Delete/11` con `reasignarA=E-commerce / tiendas online` reasignó al contacto — pero al valor `"E-commerce / tiendas online"`, que **no es `ClaveRubro` de ninguna campaña activa** (verificado: 0 coincidencias). El contacto sigue huérfano. Con los datos reales el `WHERE` nunca matchea, así que M-B no hace nada (no corrompe datos, pero tampoco rescata a nadie). Ver **CRM-007**. |
| **M-C** — endpoint de salud del pipeline | Una sola pantalla para confirmar que el pipeline está sano | **PASS (con 1 observación)** | `/Bot/Salud` → **HTTP 200**, solo lectura, con datos correctos y contrastados contra la DB: 0 templates activos sin campaña, 0 campañas con template inválido, **425 contactos huérfanos** desglosados por rubro (indumentaria 135, consultorio 101, inmobiliaria 56, servicios 38, estudio 28, ganaderia 22, comercio 16, restaurant 13, agro 13, farmacia 1, +2). El número es **legítimo**: en dev las 26 campañas activas usan claves con sufijo de zona (`indumentaria-palermo`, `consultorio-microcentro`, …) mientras esos 425 contactos llevan las claves base. Cruce template↔campaña resuelto en memoria, evitando MH-001 correctamente. Observación: `Alineadas = true` está **hardcodeado** (ver **CRM-012**). |

**Resumen: 10 PASS · 4 PARCIAL · 2 FAIL · 1 PASS-con-observación.**

### 2. Cobertura de máquina de estados

`FaseConversacion`: **sin cambios en este sprint**. B4/M-A tocan cómo se *renderizan* las filas que el guion escribe, no las transiciones. Verificado que los 14 literales de evento y el caso dinámico cubren todas las ramas de `HandleIncomingAsync` sin dejar ninguna cayendo al render por default.

`EstadoEmbudo`: 2 transiciones tocadas, ambas verificadas.

| Transición | Cambio del sprint | Resultado |
|---|---|---|
| `Pendiente → MensajeEnviado` | G1: se saltea el contacto con ≥3 fallos; G2: se sella `UltimaCorridaUtc` | PASS (código) / BLOCKED E2E |
| `Pendiente` (se mantiene) tras fallo de envío | G1: ahora deja fila `[Error de envío outbound]` en vez de fallar en silencio | PASS (código) |
| `Cerrado → Cliente` | G3: `PrimerAnioGratis` se setea en el alta | **PASS (E2E real)** |
| Guarda "solo desde `Cerrado`" | sin cambios | PASS — `ConvertirDesdeContacto:207` sigue rechazando cualquier otro estado |
| Transición inválida (`Respondido → Cliente`) | — | PASS — bloqueada por la misma guarda |

`EtiquetaErrorEnvio` cuenta como **saliente**, así que no corre la ventana de 24hs ni marca el chat como no leído — correcto, y consistente en las 4 capas.

### 3. Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | acción |
|---|---|---|---|
| MH-001 (Contains sobre colección local de string no traduce en MySQL) | **sí** | **PASS** | El sprint agrega varios `Contains`/`ToHashSet`. Los que van a SQL son sobre `enum`/`int` (`CanalesOutbound.Contains(c.CanalOrigen)`, `idsConError.Contains(c.Id)`) y traducen bien; los de string se resuelven **en memoria** a propósito (`GetSaludAsync`, `SendDailyBatchAsync`), con el comentario justificándolo. Confirmado en vivo: `/Bot/Salud`, `/Bot`, `/Contactos/Pipeline` y `/Campanas/Dashboard` devuelven 200 con datos. |
| ELV-001 (controllers sin `[Authorize]`) | **sí** | **PASS** | Los 3 endpoints nuevos/modificados probados sin autenticar → **302 a `/Account/Login`**: `/Bot/Salud`, `/Industrias/ImpactoDelete/2`, `/Chats/HiloParcial/7`. |
| LIP-001 (errores de `ModelState` invisibles) | **sí** | **PASS** | El `AddModelError` de B5 se renderiza como `field-validation-error data-valmsg-for="Nombre"` con el texto completo — verificado en el HTML de respuesta. |
| KOI-001 (`btn-swal-confirm` fuera del form no ejecuta el delete) | **sí** | **PASS** | El modal de `Industrias/Index` construye el form por JS y lo submitea; `POST /Industrias/Delete/11` ejecutó realmente (soft-delete aplicado y luego revertido). El `preConfirm` devuelve el valor del select correctamente. |
| CRM-003 (DataTable ignora `order[...]`) | sí | sin cambios | Fuera del alcance del sprint; sigue abierto. |
| CRM-004 (duplicado de teléfono en batch de Google Maps) | sí | sin cambios | Fuera del alcance del sprint; sigue abierto. **Ojo:** los comentarios de `IndustriasController` y `GetSaludAsync` citan "regla CRM-004" para la regla de *huérfanos*, que no es lo que CRM-004 documenta. Ver **CRM-013**. |
| CRM-001, CRM-002, CRM-005, CRM-006 | sí | sin cambios | Fuera del alcance del sprint. |
| REG-008 (input pierde foco al tipear) | no | N/A | No hay grilla con recálculo en el alcance. |
| REG-010 / KOI-003 / KOI-005 / KOI-006 (sidebar vs. rol) | parcial | N/A justificado | Rol único `SuperUsuario`; el link nuevo (`Bot/Salud`) está respaldado por autorización real (probado arriba) y su controller existe. |
| GAN-003 (`<partial>` dentro de `<script>`) | no | N/A | Los templates de fila nuevos no usan ese patrón. |
| SG-001 / LP-003 (binding de numéricos vacíos / cultura) | **sí** | **PASS** | `PresupuestoCotizadoUsd` es `decimal?` (nullable), así que un campo vacío no rompe el POST — probado: alta y edición con el campo vacío devuelven 200/302 sin error de binding. |
| DN-001 / DN-002, MH-002..MH-013, LP-001/004/005, ELV-002, VSF-001/002, GAN-001/002/004, REG-001..007/009, LIP-001 (resto) | no | N/A | Módulos inexistentes en este proyecto (compras, ventas, AFIP, cheques, stock). |

### 4. Defectos detectados

| id | severidad | descripción y pasos |
|---|---|---|
| **CRM-007** | **major (bloqueante de G7 y M-B)** | *`Industrias/ImpactoDelete` y `Industrias/Delete` usan `IndustriaCatalogo.Nombre` como si fuera el rubro del contacto, cuando el vocabulario real de `Contacto.Rubro` es `CampanaOutboundIndustria.ClaveRubro`.* `IndustriaCatalogo` **no tiene** campo `ClaveRubro` — la clave granular vive en `CampanaOutboundIndustria` a propósito (varios rubros operativos comparten una fila de precio: `ganaderia`/`agro` → "Ganadería / producción agropecuaria"). **Pasos:** `GET /Industrias/ImpactoDelete/{id}` para cualquiera de las 14 industrias → `contactos: 0`. Contrastar con `/Bot/Salud` → 425 huérfanos. **Impacto:** el modal siempre dice "No hay impacto" (G7 no cumple), y la reasignación de M-B nunca dispara; cuando se la fuerza, escribe un `Nombre` de catálogo que tampoco es `ClaveRubro` de ninguna campaña activa, así que el contacto sigue huérfano. **No es un fix de una línea**: hay que decidir cuál es el vocabulario canónico de `Contacto.Rubro` y ofrecer como destino de reasignación una `ClaveRubro` de campaña activa, no un `Nombre` de catálogo. **Escalado al Implementador** (causa raíz = decisión de diseño, no ambigüedad de código). |
| **CRM-008** | **major (bloqueante de deploy)** | *La migración `20260827005735_AddMensajeProgramado` no está aplicada.* No es del sprint (viene de la sesión previa de "mensajes programados"), pero está en el mismo working tree y sale en el mismo release. **Pasos:** levantar la app sin aplicarla → `MySqlException: Table '…mensajesprogramados' doesn't exist` cada 60s desde `MensajesProgramadosSchedulerService`, y `Chats/Detail` (que ahora proyecta `MensajesProgramados`) queda inalcanzable. **Acción:** aplicar la migración en producción **antes o junto con** el deploy del código. Aplicada y verificada en dev por este QA. |
| **CRM-009** | medium | *B3: un mensaje entrante nuevo se marca como leído solo por estar la pestaña abierta en background.* La HU pide lo contrario ("se marca No leído … sin importar que el polling siga corriendo"); el párrafo de Diseño §7 y la prueba #1 del Implementador piden lo implementado. Contradicción **dentro del propio Diseño**. **Pasos:** ver caso (C) de la fila B3. **Impacto:** ventana de hasta 8s en la que el chat figura no leído y después se limpia solo, sin que nadie lo haya mirado. **Fix sugerido (no aplicado):** condicionar el marcado a `document.visibilityState === 'visible'` (o mandar un flag `visible` en el tick) para que una pestaña en background nunca cuente como lectura. **Escalado** por ser decisión funcional. |
| **CRM-010** | medium | *B7: un Referido cargado a mano nunca entra al pipeline outbound.* `Contactos/Create` escribe `Rubro` = `IndustriaCatalogo.Nombre`; `SendDailyBatchAsync:183` matchea contra `ClaveRubro`. **Pasos:** alta manual con canal Referido y rubro "Farmacias" → el contacto queda `Pendiente` y ninguna corrida lo toma. Misma causa raíz que CRM-007. Confirmado en datos: 0 de 435 contactos tienen un `Nombre` de catálogo como rubro; 434 usan claves. |
| **CRM-011** | minor | *G1: el tope de reintentos cuenta fallos históricos totales, no consecutivos, y no se resetea nunca.* `fallidosPorContacto` agrupa **todas** las filas `[Error de envío outbound]` del contacto, sin ventana temporal ni reset tras un envío exitoso, pese a que el log dice "fallos de envio seguidos". Un contacto con 3 fallos transitorios repartidos en meses queda excluido del outbound para siempre, y no hay UI para limpiarlo (`/Bot/Salud` lo muestra como `Agotado` pero no ofrece acción). |
| **CRM-012** | minor | *M-C: `Alineadas = true` está hardcodeado en `GetSaludAsync`.* El aviso "si alguna vez difieren de nuevo" que pide la HU no puede dispararse jamás. Además, lo que compara son la fórmula nueva vs. la vieja **sobre el mismo universo**, no lo que realmente calculan las 3 pantallas — no detectaría la divergencia de universo que sí existe hoy en Campañas/Dashboard (ver B6). |
| **CRM-013** | minor (documentación) | *Citas cruzadas incorrectas al catálogo de QA.* `IndustriasController.ImpactoDelete` y `OutboundCampaignService.GetSaludAsync` atribuyen la regla de contactos huérfanos a "CRM-004", que en `regresiones-manuales.yml` es el duplicado de teléfono en el batch de Google Maps. Confunde a quien lea el código buscando el item. También: los punteros `⟵B4 BotFlowService:NNN` de `EtiquetasDeEvento` tienen las líneas corridas (ej. dice `:565`, el literal está en `:569`). |

**Sin auto-fix aplicado.** Los 2 defectos major y CRM-009/CRM-010 tienen causa raíz en una **decisión de diseño no tomada** (cuál es el vocabulario canónico de `Contacto.Rubro`; si una pestaña en background cuenta como lectura). Por regla del rol, ante causa raíz ambigua se escala al Implementador en vez de adivinar. **Ningún archivo de código fue modificado por este QA** (`git status` idéntico al inicio: 25 modificados + 10 nuevos).

**Items nuevos NO agregados al catálogo por instrucción explícita del orquestador** (el alta en `regresiones-manuales.yml` y en `32-estandares-qa-implementador.instructions.md` queda para el cierre de Documentación). Quedan redactados arriba, listos para transcribir.

### 5. Patrones que generalizan a `32-estandares-qa-implementador.instructions.md`

Dos hallazgos de este sprint no son bugs puntuales de este CRM sino patrones reutilizables, hoy no documentados:

1. **"Clave de negocio duplicada en dos vocabularios sin FK"** (de CRM-007/CRM-010). Cuando una columna de texto libre (`Contacto.Rubro`) se puebla desde **dos fuentes con vocabularios distintos** (un catálogo por `Nombre` y una tabla de relación por `ClaveRubro`), toda pantalla que cuente, filtre o reasigne por esa columna tiene que declarar contra cuál compara — y QA tiene que verificarlo **contra datos reales**, porque el código compila y la pantalla renderiza igual con el vocabulario equivocado, devolviendo cero en silencio. Chequeo objetivo propuesto: para cada pantalla que informe "N registros afectados", correr la misma query contra la BD y comparar; si da 0 en todos los casos, sospechar del vocabulario antes de creerle.
2. **"`ExecuteUpdateAsync` se saltea la auditoría automática"** (de G6/M-B, que acá está **bien** resuelto). `ExecuteUpdateAsync`/`ExecuteDeleteAsync` no pasan por `SaveChangesAsync`, así que el stamping de `UpdatedAt`/`UpdatedByUserId` no corre. El patrón correcto — replicarlo a mano con **el mismo claim** que usa el interceptor del `DbContext` — merece quedar documentado como regla, junto con el chequeo de QA (verificar en la BD que las filas afectadas quedaron con `UpdatedByUserId` poblado, no solo que la acción respondió 200).

### 6. Validación de los 4 puntos que el Implementador marcó como delicados

1. **B3 / el JS manda `ultimoIdVisto` siempre** → **CONFIRMADO**. Verificado en el HTML renderizado, no solo en el `.cshtml`: `data-msg-id` presente en burbujas y eventos, hijas directas de `#chatThread`, `ultimoIdVisto()` recalculado del DOM en cada tick, y la URL renderiza `'/Chats/HiloParcial/'` sin arrastrar el `id` ambiente de la ruta. El caso (A) medido contra la DB prueba que el parámetro llega y surte efecto. El fallback legacy sí reproduce el bug (caso B) — riesgo de ventana de deploy real, mitigable con hard-refresh.
2. **G6 / stamping manual en los 2 call sites** → **CONFIRMADO EN AMBOS, con evidencia en base de datos.** `ChatsController.MarcarTodosLeidos` y `IndustriasController.Delete` estampan `UpdatedAt` + `UpdatedByUserId` con `ClaimTypes.NameIdentifier`, el mismo claim que `AppDbContext.StampSoftDestroyable:333`. Verificado que las filas afectadas quedaron con el GUID real del SuperUsuario.
3. **G5 / negociación por `X-Requested-With`** → **CONFIRMADO, los 2 caminos probados en vivo.** AJAX → JSON; form POST normal → 302 al listado con los filtros. Ningún usuario ve JSON crudo.
4. **`EtiquetaErrorEnvio` en la lista de eventos** → **CONFIRMADO**. Tiene su propia rama en `ConstruirMensajes` (evento centrado con etiqueta "Error de envío"), antes del `else` por default, y está incluida en las 8 subqueries de "último mensaje entrante" de las 4 capas. El Implementador efectivamente detectó y cerró esa trampa.

### 7. Riesgos de liberación y mitigaciones

| riesgo | severidad | mitigación |
|---|---|---|
| Migración `AddMensajeProgramado` sin aplicar en producción → `Chats/Detail` caído y scheduler en loop de error | **alta** | Aplicarla en el mismo deploy. **Bloqueante.** |
| G7/M-B dan información falsa ("no hay impacto") sobre 425 contactos | **alta** | No liberar esas 2 pantallas, o liberarlas con el modal degradado al texto anterior hasta corregir CRM-007. |
| Ventana de deploy de B3: clientes con la página cacheada siguen reproduciendo el bug | media | Avisar de hard-refresh (Ctrl+F5) tras el deploy. Autolimitado. |
| B6: Campañas/Dashboard sigue dando un número distinto a las otras 2 pantallas | media | Es decisión de alcance, pero hay que **documentarlo en la pantalla** o el usuario va a reportarlo como bug. |
| G1/G2 sin prueba E2E (exigen envío real contra Meta) | media | Primera corrida real supervisada, con `/Bot/Salud` abierto para ver fallos acumulados. |
| CRM-011: exclusión permanente de contactos por 3 fallos históricos | baja | Revisar `/Bot/Salud` → "Contactos con errores de envío" antes de la primera corrida real. |

### 8. Pruebas mínimas ejecutadas por este QA

1. `dotnet build -c Release --no-incremental` → 0 errores, 13 advertencias preexistentes. ✔
2. Migraciones: detectada 1 pendiente, aplicada en dev, verificada en `__EFMigrationsHistory`. ✔
3. App levantada y 12 pantallas cargadas autenticado (todas 200 salvo `/Bot/Outbound`, que no existe como ruta — el panel real es `/Bot`). ✔
4. B3: 3 ramas de `HiloParcial` medidas contra la BD. ✔
5. B4: render real de un hilo con la etiqueta "Consulta inicial". ✔
6. B5: rename bloqueado / edición de texto permitida, ambos contra la BD. ✔
7. B2: rebalanceo con campaña multi-día, resultado verificado y datos restaurados. ✔
8. G3: conversión end-to-end + exclusión del ARR en el Dashboard. ✔
9. G5: los 2 invocadores de `MarcarNoLeido`. ✔
10. G6: `MarcarTodosLeidos` con auditoría verificada en BD. ✔
11. G7/M-B: `ImpactoDelete` sobre las 14 industrias + experimento controlado de reasignación. ✔
12. M-C: `/Bot/Salud` contrastado contra consultas directas a la BD. ✔
13. Autorización de los 3 endpoints nuevos sin autenticar. ✔
14. Restauración y verificación del estado de `olvidatacrm_dev`. ✔

**No ejecutado:** `Bot/EjecutarAhora` (habría disparado envíos reales de WhatsApp a 234 contactos) y el render visual de toasts/modales SweetAlert2 (sin MCP `playwright` en esta sesión).

### 9. Checklist de salida para merge

- [x] Build en Release, 0 errores, sin advertencias nuevas — confirmado por QA.
- [x] Vistas Razor compiladas (verificado por el Implementador y respaldado por la carga real de las 10 vistas tocadas).
- [x] 0 migraciones EF **del sprint** — confirmado.
- [ ] **Migración `AddMensajeProgramado` aplicada en producción** — pendiente, bloqueante (CRM-008).
- [x] Lógica de negocio en `Application`/`Infrastructure`, no en controllers.
- [x] Autorización real en los endpoints nuevos.
- [x] Auditoría preservada en los 2 usos de `ExecuteUpdateAsync`.
- [ ] **CRM-007 corregido (G7 + M-B)** — pendiente, bloqueante.
- [ ] CRM-009 / CRM-010 resueltos o aceptados explícitamente como alcance reducido.
- [ ] Items nuevos transcritos a `regresiones-manuales.yml` y a `32-estandares-qa-implementador.instructions.md` — pendiente, cierre de Documentación.

### 10. Estado go/no-go

**NO-GO para deploy de producción en el estado actual.** Dos bloqueantes:

1. **CRM-008** — la migración `AddMensajeProgramado` no está aplicada; sin ella `Chats/Detail` (la pantalla más usada del sistema) queda caída y un hosted service loguea una excepción por minuto. Es de resolución mecánica.
2. **CRM-007** — G7 y M-B, 2 de los 17 items, no cumplen su criterio de aceptación y además **muestran información falsa** al usuario sobre 425 contactos, contradiciendo a `/Bot/Salud` del mismo sprint. Liberar así es peor que no haberlos tocado: el modal viejo al menos no simulaba haber calculado nada.

**GO parcial recomendado:** los otros 15 items están sólidos y varios corrigen bugs reales que hoy están en producción (B2 mandaba el doble de la meta los días con campañas multi-día; B3 hacía imposible marcar un chat como no leído; B4 mostraba diagnóstico interno como si se lo hubiéramos escrito al cliente; B5 evitaba romper campañas en silencio; G6 tenía una regresión de auditoría en potencia). Si conviene liberar ya, la vía limpia es: aplicar la migración + revertir `IndustriasController.ImpactoDelete`/`Delete` y el modal de `Industrias/Index` al comportamiento previo (o dejar el modal sin el número), y liberar los 15 restantes. `CampanasController.EliminarIndustria` (la mitad correcta de G7) puede quedar.

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

## QA — matriz de módulos valorizados + borrador de propuesta MVP/FULL (2026-08-28)

Verificación previa al **primer deploy** de la feature. Nada estaba deployado: código sin commitear (working tree), migración aplicada sólo en `olvidatacrm_dev`. Reglas de negocio: agente `olvidata-presupuesto-bot` (9 reglas de redacción, qué no preguntar en el cuestionario). Referencia: §"Matriz de módulos valorizados…" de `5-implementador.md` (11 escenarios de QA + 3 decisiones propias del Implementador).

### M1. Método y alcance

App levantada en Release contra `olvidatacrm_dev` (`https://127.0.0.1:5444` + `http://127.0.0.1:5313`, Development), autenticada como SuperUsuario, y ejercitada por HTTP real: 26 pantallas, 8 endpoints POST/AJAX y **29 generaciones de mensaje** sobre datos reales, con assertions SQL independientes contra la base antes y después. **MCP `playwright` no expuesto en la sesión** — se declara explícitamente y se sustituye por verificación HTTP + SQL, igual que en las 2 pasadas anteriores; queda un residuo manual acotado (§M7).

`dotnet build -c Release --no-incremental` corrido por QA **2 veces** (antes y después del auto-fix): **0 errores / 13 advertencias**, idénticas al baseline (2 NU1902 de MailKit/MimeKit, 2 CS8524, 1 CS0114, 2 CS8620 y las de restore). **0 `[ERR]`/`[FTL]`** en Serilog en las 3 corridas completas de la app.

### M2. El ajuste manual del cliente sobre `Questions["build"]` — PASS

Primer chequeo pedido, y el que condicionaba todo lo demás.

| Verificación | Resultado |
|---|---|
| `Questions["build"]` tiene 2 preguntas, no 3 | **PASS** — "¿qué necesitás que haga el sistema?" + "¿Tenés una fecha…?" |
| Numeración de emoji intacta | **PASS** — 1️⃣ y 2️⃣ consecutivos, sin 3️⃣ huérfano. `rent`, `rent_other` y `landing` también quedaron consistentes |
| Ningún otro flujo depende de esa categoría | **PASS** — `CategoryNames["build"]` intacto; `MecanismoPregunta1Async` sólo actúa sobre `Categoria == "rent"`, así que `build` nunca entró en el mecanismo nuevo ni sale afectado |
| `Contacto.CantidadUsuarios` sin escritores | **PASS por grep, no por supuesto** — la única aparición fuera de migraciones es la declaración de la propiedad en `Contacto.cs`. Cero lecturas, cero escrituras. El bloque de captura de dígitos de `OnAnswerAsync` ya no existe |
| Build tras el cambio | **PASS** — confirmado de nuevo por QA, 0 errores |

El comentario de cabecera de `Questions` quedó **actualizado y correcto** (dice "se sacó de TODAS las categorías… el cliente prefirió sacarla de todos lados igual"), o sea que el cambio manual no dejó documentación contradictoria. El riesgo #2 que el Implementador había declarado ("`build` conserva su pregunta") queda **cerrado por decisión del cliente**, no pendiente.

### M3. Seed de datos — PASS (y una corrección al conteo)

Verificado **contra la base, no contra el reporte**:

```
modulos vivos: 84 | asignaciones vivas: 88 | industrias con matriz: 9 | imprescindibles: 62
```

Los 9 rangos por rubro coinciden **exactamente**, uno por uno, con la tabla de `5-implementador.md` (Retail 510-806/991-1653, Laboratorios 637-1051/871-1387, Dietéticas 386-774/487-942, Alq. maquinaria 452-713/769-1152, Estudios contables 354-587/404-654, Ganadería 565-897/582-967, Residuos 168-304/360-551, Landing 194-260/261-344, Utilities 335-590/464-783). Los 3 módulos compartidos son los 3 declarados.

**Matiz de método que vale documentar:** la primera consulta dio 89/10 en vez de 88/9. No era una discrepancia real: eran **2 filas soft-deleteadas de datos de prueba** (una del Implementador el 2026-08-28 02:48, otra mía al ejercitar el CRUD de asignación), que sólo aparecen si uno consulta `ModuloCatalogoIndustrias` sin filtrar `DeletedAt`. Filtrando bien, el seed es 84/88/9/62. Las 2 filas se **eliminaron en duro** al cerrar, así que dev queda idéntico al seed limpio. Lección para la próxima pasada: sobre este esquema, todo conteo de control va con `DeletedAt IS NULL` explícito.

**Los 5 rubros sin matriz — PASS.** `E-commerce`, `Alquiler de inmuebles / gestión de propiedades`, `Finanzas personales`, `Finanzas simples` y `Farmacias` tienen **0 módulos** en base. `GET /Modulos/Checklist` sobre los 5 devuelve el aviso *"Todavía no hay módulos cargados para {rubro}"* con link a `/Modulos/Create` — **no** un checklist vacío ni un error. El combo de `/Modulos/Presupuesto` lista las 14 industrias y marca las 5 como `(sin matriz)` sin necesidad de entrar. El hallazgo del Implementador sobre **"Alquiler de inmuebles"** (que el pedido original enumeraba 13 de 14) queda **confirmado y correctamente tratado**: es el `industriaId=9`, 0 módulos, aviso presente.

### M4. Cobertura de los 11 escenarios del Implementador

| # | Escenario | Resultado | Evidencia |
|---|---|---|---|
| 1 | `/Modulos` → 84 módulos, badges por rubro | **PASS** | `GetData` → `recordsTotal: 84`; los 3 compartidos traen 2 entradas en `rubros` |
| 2 | Retail: 14 módulos, 6 pre-tildados, rangos al abrir | **PASS** | 14 checkboxes, 6 con `checked`; `Calcular` → MVP 510-806 / FULL 991-1653 |
| 3 | Rubro sin matriz → aviso, no checklist vacío | **PASS** | Los 5, uno por uno (§M3) |
| 4 | Generar mensaje → las 9 reglas | **PASS con 1 defecto** | §M5 — reglas OK; defecto de texto **CRM-015**, auto-fixeado |
| 5 | Casos degradados (sin MVP / sólo MVP / nada) | **PASS** | Los 3 discriminados con el mensaje y la advertencia correctos; "nada tildado" → `success:false` sin texto |
| 6 | `/Modulos/Edit` → asignar / cambiar MVP / quitar rubro | **PASS** | Los 3 por AJAX; duplicado rechazado con mensaje claro; el rubro quitado **vuelve** al combo de disponibles |
| 7 | Manipulación: id de otro rubro por inspector | **PASS** | `Calcular` con los 6 MVP de Retail + los 6 ids de Utilities + `99999/-1/0` da **exactamente el mismo resultado** que sin la basura (510-806, `cantidadFull: 6`) |
| 8 | `Chats/Detail` de `indumentaria` → las 2 opciones | **PASS** | §M6 |
| 9 | `Chats/Detail` de `inmobiliaria`/`restaurant` → comportamiento viejo | **PASS** | §M6 |
| 10 | Bot: `rent`/`rent_other` en 2 preguntas; matriz vs. menú fijo | **PASS** | §M2 y §M7 |
| 11 | Idempotencia del seed (2 reinicios) | **PASS** | 2 arranques completos posteriores al seed: **cero** líneas de "sembrada" en el log y conteos clavados en 84/88/9 |

### M5. Las 9 reglas del agente `olvidata-presupuesto-bot`

29 mensajes generados sobre los 9 rubros con matriz (variantes: todo tildado, sólo MVP, sólo no-MVP, un solo módulo, nada).

| Regla | Resultado | Evidencia |
|---|---|---|
| R1 nunca tabla | **PASS** | Texto corrido en los 29; ni un pipe de tabla, ni "Plan A/Plan B" |
| R2 máx. 3-4 ítems por opción | **PASS** | Tope duro de 4 + `"y N más"`. **Ganadería con 7 imprescindibles** (el caso que se pidió mirar): MVP lista 4 y cierra `"y 3 más"`. **El bug de la doble "y" está efectivamente corregido** — verificado leyendo la salida, no el código: en los 29 mensajes no aparece nunca `"… y X y N más"` como separador de lista |
| R3 frasear por resultado | **PASS** | "todo resuelto de una" / "la base para salir del Excel ya". Cero apariciones de "versión reducida/completa" |
| R4 FULL primero, MVP segundo | **PASS** | El bloque `*FULL*` precede a `*MVP*` en los 29 |
| R5 extensión acotada | **PASS con observación** | §M8 |
| R6 nunca número cerrado | **PASS** | `Ronda entre USD {mvpMin} y USD {fullMax}` + "te lo afino con el detalle exacto", en los 29 **incluidos los 3 degradados y el de un solo módulo** |
| R7 ARS/cuotas en una línea | **PASS** | "en pesos, en cuotas, sin letra chica", sin desglose |
| R8 a medida sin la frase de landing | **PASS** | Cero apariciones de "software factory y consultora de desarrollo de sistemas" |
| R9 cierre de dirección, nunca de agenda | **PASS** | "¿Cuál te cierra más?" (2 opciones) / "¿Te sirve por ahí?" (degradados). **Cero** pedidos de fecha u horario |

**Sobre R6 con más rigor.** El riesgo teórico de que el rango colapse a un número cerrado existe: hay **2 módulos con `PrecioMin == PrecioMax`** ("Pantalla única sin base de datos" y "Formulario de contacto", 17/17, ambos de Landing). Si alguna vez se tildara **sólo uno de esos dos**, el mensaje diría *"Ronda entre USD 17 y USD 17"*, que es un número cerrado disfrazado de rango. **Hoy es inalcanzable en la práctica** (los 2 son de Landing, que tiene 7 módulos y 6 imprescindibles) y no lo cuento como defecto, pero queda anotado como condición a vigilar si el catálogo crece con módulos de precio plano.

**Las 3 decisiones propias del Implementador, revisadas de nuevo y no dadas por buenas:**

1. **Truncado con "y N más"** — correcto, y el fix del doble "y" verificado empíricamente (arriba).
2. **Sin ningún imprescindible → una sola opción** — correcto: el mensaje no inventa un MVP vacío y la advertencia explica por qué.
3. **Sólo imprescindibles → una sola opción** — correcto, con una advertencia **distinta** de la anterior que además dice cómo obtener las dos ("Sumá algún módulo del bloque Solo FULL"). Buen criterio: 2 opciones idénticas sí habrían leído a relleno.

### M6. Wiring del botón "Sugerir" en `Chats/Detail` — PASS

12 contactos reales de dev, cubriendo los 3 vocabularios de `Contacto.Rubro`:

| Contacto | Rubro | `matriz` | Comportamiento |
|---|---|---|---|
| #11 | `indumentaria` | Retail (14) | 2 opciones |
| #424 | `indumentaria-once` (**sufijo de región**) | Retail (14) | 2 opciones |
| #151 | `consultorio` | Laboratorios (14) | 2 opciones |
| #1 | `estudio` | Estudios contables (10) | 2 opciones — **el fix del mapeo funcionando** |
| #126 | `ganaderia` | Ganadería (8) | 2 opciones |
| #230 | `servicios` | Utilities (6) | 2 opciones |
| #53 | `comercio` | Alq. maquinaria (11) | 2 opciones |
| #292 | `inmobiliaria` | `null` | **comportamiento viejo** |
| #236 | `Inmuebles / Real estate` (reescrito por el bot) | `null` | **viejo**, con sugerencia genérica real |
| #128 | `restaurant` | `null` | **viejo** |
| #158 | `farmacia` | `null` | **viejo** |
| #194 | `Otro rubro` | `null` | **viejo** |

Los 4 caminos del JS revisados y coherentes con el servidor: con matriz y con sugerencia → SweetAlert de 2 opciones; con matriz y sin sugerencia → derecho al checklist (el caso que dejaba al botón sin uso); sin matriz y con sugerencia → prellena `#txtRespuesta` como siempre; sin matriz y sin sugerencia → el aviso de siempre. `btn-usar-en-chat` sólo escribe en `#txtRespuesta` y cierra el modal: **no hay flujo de envío paralelo**, el envío sigue siendo `Chats/EnviarMensaje`.

### M7. Cuestionario del bot — PASS

La tabla de decisión de `MecanismoPregunta1Async` computada contra la base para las 8 claves de `DolorOptionsPorRubro`:

| Rubro del diálogo | Fila de catálogo | MVP en base | Mecanismo |
|---|---|---|---|
| Comercio o alquiler de maquinaria | Alquiler de maquinaria | 7 | **MatrizModulos** |
| Alquiler de maquinaria | Alquiler de maquinaria | 7 | **MatrizModulos** |
| Dietéticas y venta de productos | Dietéticas y comercios… | 8 | **MatrizModulos** |
| Indumentaria o calzado | Retail | 6 | **MatrizModulos** |
| Agro / Ganadería | Ganadería | 7 | **MatrizModulos** |
| Servicios urbanos o técnicos | Utilities | 5 | **MatrizModulos** |
| Recolección de residuos y logística | Residuos | 4 | **MatrizModulos** |
| **Vinos y bebidas** | Gastronomía (**fila retirada 2026-07-17**) | 0 | **MenuFijo** ← el menú viejo intacto |

**7 pasan al mecanismo nuevo, 1 se queda con el menú de 3 opciones** — exactamente lo que afirma el reporte. La coexistencia con `DolorOptionsPorRubro` es correcta: la matriz tiene prioridad y el menú viejo **no se retiró**.

**Los 2 hallazgos que el Implementador dice haber corregido, verificados:**

- **`MecanismoPregunta1Async` como fuente única** — **confirmado en los 2 call sites**: `SendCurrentQuestionAsync` (qué mandar) y `OnAnswerAsync` (cómo interpretar). En `OnAnswerAsync` la condición es `MecanismoPregunta1Async(...) == MenuFijo && DolorOptionsPorRubro.TryGetValue(...)`, o sea que el mapeo id→título **sólo** corre cuando efectivamente se mandó un menú. El bug que evita es real: sin eso, un prospecto de Indumentaria (que hoy recibe texto libre) que conteste "1" quedaba guardado como "Stock talle/color", una opción que nunca vio.
- **`ArmarPitchPostDolorAsync` extendido** — **confirmado**: `tieneSistemaReal = DolorOptionsPorRubro.ContainsKey(industria) || (await ModulosMvpDelRubroAsync(industria)).Count > 0`. Y la prueba social que reciben los rubros nuevos **existe de verdad**, no cae al default: `SocialProofByType("estudio")` → "Contadores BMA", `("consultorio")` → "un centro médico en La Plata". Sin la extensión, esos 2 (que nunca estuvieron en `DolorOptionsPorRubro`) habrían caído al pitch genérico.

**Residuo manual (sin MCP de navegador ni envío real a Meta):** el texto exacto que llega al WhatsApp del prospecto en la pregunta 1 con matriz no se verificó contra la API real de Meta — se verificó la función que lo arma y los datos que la alimentan. Queda para prueba manual con un número de test: *abrir una conversación de un rubro con matriz y confirmar que la pregunta 1 llega como texto libre con las viñetas de los 3-4 imprescindibles, y que un rubro de "Vinos y bebidas" sigue recibiendo la lista interactiva de 3 opciones*.

### M8. Defectos

**CRM-015 — `major` — AUTO-FIXEADO Y VERIFICADO.** Los módulos cuyo nombre **empieza** con una sigla salían deformados en el texto que se copia tal cual al WhatsApp del cliente: `ABM Cuadrilla` → **`aBM Cuadrilla`**, `SEO básico y deploy` → **`sEO básico y deploy`**, `CRM de WhatsApp (bandeja de conversaciones)` → **`cRM de WhatsApp…`**.

- *Causa raíz:* `PropuestaMvpFullService.Minuscula()` bajaba **siempre** la inicial para que el nombre entrara en frase corrida. El comentario del propio método declaraba la intención de no romper siglas, pero sólo contemplaba las del **medio** del nombre (por eso no usa `ToLower()` completo); la sigla en la **primera** palabra no estaba contemplada.
- *Alcance real:* **9 de los 84 módulos**, en **4 de los 9 rubros** con matriz (Utilities, Residuos, Landing, Alq. maquinaria). Los 9 son **imprescindibles**, o sea que caen dentro de los 4 ítems que el mensaje lista explícitamente — no es un caso de borde: Utilities mostraba 4 de sus 5 ítems del MVP deformados.
- *Por qué `major` y no cosmético:* es el mensaje que Joaquín copia y pega en una conversación real después de una demo, y el capitalizado mixto lee como error de tipeo justo donde se está pidiendo confianza para un precio.
- *Auto-fix aplicado* (sin lógica de negocio nueva — restaura la intención ya declarada en el comentario del propio método): guard de 2 mayúsculas iniciales en `Minuscula()`, `OlvidataCRM.Application/Services/PropuestaMvpFullService.cs`. Catalogado como **CRM-015** en `docs/qa/regresiones-manuales.yml` **antes** de proponer el fix, con `deteccion_qa` automatizable (regex de minúscula seguida de 2+ mayúsculas sobre el `texto` de `GenerarMensaje`).
- *Re-ejecución post-parche:* build Release **0 errores / 13 advertencias** (baseline); `deteccion_qa` corrida sobre los **9 rubros × 2 variantes = 18 mensajes** → **0 fallas**; los 3 criterios de aceptación literales verificados (`ABM Cuadrilla`, `SEO básico y deploy`, `CRM de WhatsApp (bandeja de conversaciones)` presentes intactos); **sin regresión** en los nombres que sí deben bajar la inicial (`catálogo con variantes de color y talle`, `stock e inventario`) ni en las siglas del medio (`facturación electrónica AFIP/ARCA`, `reserva con QR`).

**Observaciones no bloqueantes (ningún defecto abierto):**

1. *(R5, juicio de negocio)* El mensaje tiene **5 bloques + cierre** (apertura, "armé dos caminos", FULL, MVP, precio, a-medida, pregunta), contra los "2 párrafos cortos + 1 línea de cierre" que pide la regla 5. Es defendible leer FULL y MVP como los 2 párrafos y el resto como andamiaje, pero **es una interpretación, no un cumplimiento literal**. No lo trato como defecto porque la regla es de criterio y su dueño es `olvidata-presupuesto-bot`: conviene que lo adjudique él en la primera revisión de un mensaje real.
2. *(cosmético)* Cuando el nombre del módulo termina en una frase coordinada, el cierre del truncado repite la conjunción: *"…ventas con cobro multi-medio **y** cuotas **y** 2 más"*. **No es** el bug del doble "y" que el Implementador corrigió (ese era el separador de la lista, y está bien resuelto): acá la primera "y" pertenece al nombre del módulo. Se resuelve editando el nombre desde `/Modulos/Edit`, sin tocar código.
3. *(inconsistencia menor, sin impacto hoy)* Un rubro con módulos pero **cero imprescindibles** es tratado distinto por los 2 consumidores: `ChatsController.MatrizDelRubroAsync` cuenta **todos** los módulos y ofrece el checklist, mientras que `BotFlowService.ModulosMvpDelRubroAsync` cuenta **sólo los MVP** y apaga el mecanismo nuevo. Reproducido a propósito asignando 1 módulo no-MVP a Farmacias. Los 2 comportamientos son defendibles por separado (la pantalla necesita un checklist, el bot necesita nombres que listar) y el generador maneja el caso con su degradado, así que no es defecto — pero si alguien carga un rubro entero como "sólo FULL", el bot no lo va a reflejar.
4. *(comentario desactualizado)* El XML-doc de `RubroHelpers.CatalogoNombreDeRubroContacto`, paso (2), sigue citando "(Farmacia, Contabilidad)" como ejemplos de entradas mapeadas a `null` — justo las 2 que esta feature dejó de mapear a `null`. El código es correcto; el comentario induce a error a quien lo lea después.
5. *(higiene de dev, ya resuelta)* Las 2 filas de asignación soft-deleteadas de datos de prueba se eliminaron en duro; dev cerró en 84/88/9/62 verificado.

### M9. El fix del mapeo Farmacia/Contabilidad — no reintroduce cotización automática

Punto explícitamente auditado, porque la regla del 2026-08-24 es que **el bot nunca más cotiza solo**. Rastreados **todos** los consumidores de `IndustriaACatalogoNombre`:

- `BotFlowService.ResolveIndustriaCatalogoAsync` → devuelve la fila y se la pasa a `SendBriefToAdminAsync`, donde `industria?.Plan` se usa **únicamente** dentro de `if (contacto.PresupuestoCotizadoUsd.HasValue)`. Y `PresupuestoCotizadoUsd` **el bot ya no lo setea nunca**: `CompleteAsync` fija `EstadoEmbudo = DerivadoManual` y manda `MsgClosing`, sin ninguna rama de cálculo (el bloque está eliminado, con el comentario de la decisión en su lugar). Hoy ese campo sólo se escribe **a mano** desde `Contactos/Edit` (G4).
- `IndustriasController` (ImpactoDelete) y `ChatsController.MatrizDelRubroAsync` → lectura, sin efecto sobre precio.
- `CotizaAutomatico` de las 2 filas sigue en **`false`** en el seed, y el bot no lo consulta en ningún lado.

**Conclusión: el fix no abre ningún camino hacia cotización automática.** Lo único que cambia de comportamiento es que un contacto de `farmacia`/`estudio` ahora **encuentra su fila de catálogo** — que es precisamente el punto, porque Estudios contables es uno de los 9 rubros con matriz real. Verificado end-to-end con el contacto #1 (`estudio`), que ahora sí recibe la matriz de 10 módulos.

### M10. `.gitignore` y material de clave — PASS

| Verificación | Resultado |
|---|---|
| Regla presente | **PASS** — `.gitignore:91` → `OlvidataCRM.Web/DataProtection-Keys/` |
| Regla efectiva | **PASS** — `git check-ignore -v` la resuelve a esa línea; `git status --ignored` marca la carpeta como ignorada |
| Ningún archivo de clave trackeado hoy | **PASS** — `git ls-files` sin coincidencias para `dataprotection`/`key-` |
| Ningún archivo de clave commiteado **nunca** | **PASS** — `git log --all -- "*DataProtection-Keys/*" "*key-*.xml"` **sin resultados** en toda la historia |

Hay una clave real en disco (`key-0cb0b67f-….xml`, generada al correr en local) y está correctamente ignorada. La duda que el Implementador dejó abierta ("vale confirmar que nunca se commiteó") queda **cerrada**: nunca se commiteó, no hace falta reescribir historia ni rotar el keyring.

### M11. Regresión del resto del sistema — PASS

Smoke autenticado sobre el sprint de 17 items ya deployado y el resto del CRM: **24 rutas** respondiendo 200/302, cero 500. `/Contactos` (+ Details/Create/Edit), `/Chats` (+ Detail), `/Campanas` (+ Edit), `/Industrias` (+ Create), `/Bot`, `/Bot/Salud`, `/Clientes`, `/Negocio/Dashboard`, `/Templates`, `/System`, `/Users`, `/Notifications`, `/Modulos` (+ las 5 vistas nuevas). Los 2 404 que aparecieron (`/Clientes/Create`, `/Negocio`) son **rutas que no existen** en esos controllers (`ClientesController` no tiene `Create`; `NegocioController` expone `Dashboard`, no `Index`) — error de mi lista de URLs, no del sistema. **0 `[ERR]`/`[FTL]`** en Serilog.

### M12. Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

54 items. Los que aplican a la superficie nueva:

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-010, KOI-003, KOI-005, KOI-006, CRM-002 | sí | **PASS** | Link "Módulos / Presupuesto" dentro de `@if (User.IsInRole("SuperUsuario"))`, respaldado por `[Authorize(Policy = "RequireSuperUsuario")]` real en el controller. Anónimo → 302 a Login en las 4 rutas. Ningún link a un controller inexistente |
| CRM-003, MH-015 | sí | **PASS** | `AplicarOrden` con whitelist por índice (0-3) y las columnas 4-6 declaradas `orderable: false`: el conjunto de la vista y el del switch **coinciden exactamente**. Verificado por HTTP en asc/desc de las 4 columnas ordenables + índice fuera de rango (cae al default sin romper) |
| MH-001 | sí | **PASS** | El cruce contra los ids del navegador se hace **en memoria** (`ResolverElegidosAsync`), justo el patrón que el catálogo marca como no traducible por este proveedor. `Calcular`/`GenerarMensaje` sin 500 en 29 corridas |
| MH-003 | sí | **PASS** | Validación de servidor real, no sólo del cliente: POST directo con `max < min` → rechazado; precio negativo → rechazado por `[Range]`; nombre vacío → rechazado por `[Required]` |
| KOI-001 | sí | **PASS** | El delete de `/Modulos/Index` construye el `<form>` por JS con el antiforgery adentro — no es un botón fuera del form |
| GAN-003 | sí | **PASS** | El checklist no usa `<script type="text/x-template">` con `<partial>` adentro; se sirve como partial real desde `/Modulos/Checklist` |
| DN-001, DN-002 | sí | **PASS** | `RubrosConMatrizAsync` evita la subconsulta correlacionada a propósito (2 consultas planas + agrupación en memoria); `GetData` no combina Include de colección con OrderBy dinámico + Skip/Take sobre navegación |
| MH-002 | sí | **N/A** | No hay enums serializados a JSON en esta superficie |
| REG-004, VSF-001, VSF-002 | sí | **N/A** | La feature no tiene máquina de estados propia (§M13) |
| CRM-001, CRM-004, CRM-005, CRM-006 | no | sin cambios | Superficie del bot/outbound no tocada por esta feature más allá de §M7 |
| REG-001…009, KOI-002, KOI-004, GAN-001/002/004, LP-\*, ELV-\*, LIP-\*, SG-001, MH-004…014 | no | N/A | Otros proyectos / módulos sin equivalente |
| **CRM-015** | **sí** | **FAIL → auto-fixeado → PASS** | **Item nuevo, creado en esta pasada** (§M8) |

### M13. Máquina de estados

**No aplica**: la feature no introduce ninguna. `ModuloCatalogo` y `ModuloCatalogoIndustria` sólo tienen el ciclo `activo → soft-deleted` común a todo `SoftDestroyable`, verificado en sus 2 sentidos (quitar un rubro lo saca del checklist; el rubro quitado vuelve al combo de disponibles). `EsImprescindible` es un flag booleano editable en ambos sentidos, no un estado con transiciones restringidas. `EstadoEmbudo` **no se toca** desde esta feature: el borrador termina en un textarea, no cambia el estado de ningún contacto.

### M14. Riesgos de liberación y mitigaciones

1. **La migración falta aplicar en producción.** `20260828023654_AddModuloCatalogo` son **2 `CREATE TABLE` + 3 índices, cero `ALTER` sobre tablas existentes** (verificado leyendo el archivo, no el reporte): riesgo sobre datos existentes **nulo**. *Mitigación:* aplicarla antes o durante el deploy; sin ella, `/Modulos` y el botón "Sugerir" fallan.
2. **El seed corre solo en el primer arranque post-deploy** y siembra 84 módulos. Es idempotente por fila y verificado en 2 reinicios. *Mitigación:* mirar el log del primer arranque y confirmar 84/88/9 en producción con la misma consulta de §M3 (con `DeletedAt IS NULL`).
3. **Los nombres técnicos del seed** ("Parser de Excel propietario", "Producción mensual por centro", "Vista de resultados para confirmar o rechazar", y ahora también los "ABM …") siguen sonando a jerga en un WhatsApp. Riesgo #3 del Implementador, **confirmado y vigente**: el auto-fix de CRM-015 corrige el capitalizado, **no** el vocabulario. *Mitigación:* `olvidata-presupuesto-bot` los afina desde `/Modulos/Edit` sin tocar código — conviene hacerlo antes del primer envío real.
4. **Interpretación de la regla 5** (§M8, obs. 1) sin adjudicar. *Mitigación:* que el dueño de las reglas revise el primer mensaje real antes de mandarlo.
5. **Módulos de precio plano** (§M5): si el catálogo suma más, el rango puede colapsar a "USD 17 y USD 17". *Mitigación:* al cargar un módulo nuevo, dejar `PrecioMax > PrecioMin`.
6. **Código sin commitear.** Todo el feature (incluido mi auto-fix) está en el working tree. *Mitigación:* commitear antes de deployar; el `.gitignore` ya cubre el material de clave (§M10).
7. **Residuo de prueba manual** (§M7): el texto real de la pregunta 1 por WhatsApp, sin MCP de navegador ni envío a Meta.

### M15. Checklist de salida para merge

- [x] Build en Release, 0 errores / 13 advertencias preexistentes (2 corridas: pre y post auto-fix)
- [x] Migración revisada: 2 tablas nuevas, 0 `ALTER`; aplicada en dev, sin pendientes
- [x] Seed verificado contra la base: 84/88/9/62, 9 rangos coincidentes uno por uno
- [x] Los 5 rubros sin matriz muestran el aviso, no un checklist vacío
- [x] Las 9 reglas de redacción verificadas sobre 29 mensajes reales
- [x] Autorización real (policy + sidebar) y CSRF en los POST
- [x] Validación de servidor independiente del cliente
- [x] Manipulación de ids del navegador sin efecto sobre el cálculo
- [x] Wiring de "Sugerir" en los 2 caminos, 12 contactos reales
- [x] Tabla de decisión del cuestionario del bot verificada contra la base (7 matriz + 1 menú)
- [x] Sin camino a cotización automática (todos los consumidores rastreados)
- [x] `.gitignore` efectivo y sin material de clave en la historia de git
- [x] Regresión: 24 rutas sin 500, 0 errores en Serilog
- [x] Idempotencia del seed en 2 reinicios
- [x] Defecto encontrado catalogado (CRM-015) antes del fix, auto-fixeado y re-verificado
- [x] Estado de dev restaurado (84/88/9/62)
- [ ] **Pendiente del cliente:** commitear, aplicar la migración en producción, deployar, y la prueba manual de §M7

### M16. Estado go/no-go

**GO para deploy de producción.**

La feature hace lo que dice el reporte, y lo verifiqué contra la base y contra la salida real del generador, no contra el reporte. El ajuste manual del cliente sobre `Questions["build"]` está bien hecho y no rompió nada. Las 3 decisiones propias del Implementador resisten revisión crítica. El fix del mapeo Farmacia/Contabilidad no abre ningún camino hacia cotización automática — punto auditado hasta el último consumidor. El único defecto encontrado (CRM-015) era `major` por ir en el texto que se le manda al cliente, y quedó catalogado, corregido y re-verificado sobre 18 mensajes sin regresión.

Condiciones de liberación, ninguna bloqueante: aplicar la migración en producción (riesgo nulo, 2 `CREATE TABLE`), confirmar el seed en el primer arranque, y **afinar los nombres técnicos del catálogo desde `/Modulos/Edit` antes del primer envío real a un cliente** — es lo único que todavía puede hacer que un mensaje correcto suene mal.

## QA — expansión nacional de outbound: 176 campañas nuevas en 22 ciudades (2026-08-28, cambio de datos)

### N0. Alcance y método

Segunda auditoría de un **cambio de datos en producción** (`MYSQL5044.site4now.net` / `db_a7251f_olvidat`, MySQL 8.0.41), esta vez sobre la expansión geográfica nacional de las campañas outbound de Google Maps: **176 `CampanasOutbound` + 176 `CampanaOutboundIndustrias` + 528 `CampanaQueries`** insertadas por **dos agentes en paralelo** (tanda A: Cuyo/Patagonia/Litoral/resto de Buenos Aires, 12 ciudades; tanda B: NOA/NEA, 10 ciudades), cubriendo 8 rubros core en 22 ciudades nuevas.

**Método:** sin build, sin migración, sin deploy, sin navegador. Consultas de **sólo lectura** con `mysql.exe` (`C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe`, credenciales de `OlvidataCRM.Web/appsettings.Production.json`) contra la base real, más lectura de `GoogleMapsService.RestockCampanasAsync`/`SearchByRubroAsync`, `OutboundCampaignService.SendDailyBatchAsync`/`BusquedaDiariaGlobalAsync`, `OutboundSchedulerService` y `DiasSemana` para entender cómo se consumen realmente los campos tocados. **Cero escrituras** de mi parte. La ronda previa del mismo día (93 queries sobre 33 campañas) ya estaba auditada y aprobada — fuera de alcance.

**Veredicto: GO. 7/7 criterios PASS, 0 defectos.**

### N1. Cobertura por criterio

| # | Criterio | Resultado | Evidencia |
|---|---|---|---|
| 1 | Conteo global real (176/176/528, ~284 activas) | **PASS** | 176 campañas `Id` 142-317 (span 176), 176 industrias mismo rango, 528 queries `Id` 881-1408 (span 528). Total: 284 vivas / 284 activas = 108 + 176. 1189 queries vivas = 721 + 528. 22 regiones × 8 campañas, 176 industrias × 3 queries |
| 2 | `ClaveRubro` único en todo el sistema | **PASS** | 284 distintas de 284 (y 284 normalizando `LOWER(TRIM())`). Extendido a las 20 industrias soft-deleteadas: 304/304 únicas |
| 3 | `IndustriaCatalogoId` correcto y consistente | **PASS** | Las **22** ciudades (no una muestra) con firma idéntica `clinica:5 comercio:2 consultorio:5 dieteticas:14 estudio:16 farmacia:15 indumentaria:2 inmobiliaria:9`. Ningún `rubroBase` del sistema con >1 catálogo; 0 NULL |
| 4 | Ninguna campaña/industria preexistente tocada | **PASS** | Las 6 protegidas con `UpdatedAt` ≤ 2026-08-26. Únicas escrituras de hoy sobre `Id<142`: 03:02-03:09 (scheduler), ninguna a las 04:0x. Integridad referencial total: 0 huérfanos en 5 direcciones |
| 5 | Cupo diario por día de la semana | **PASS** | 465-469 msj/día (49,43-49,86% de `CupoDiario`=940). Ningún día cerca del techo; tope global duro en `SendDailyBatchAsync` lo hace imposible por construcción. **Observación:** ~117% de `MetaDiaria`=400 |
| 6 | Calidad geográfica de las queries nuevas | **PASS** | Las **528** (no 30-40): 510 con nombre de ciudad en el texto, 18 con localidad vecina + provincia. Anclaje correcto en 528/528. 0 duplicados entre ellas, 0 colisiones con `GoogleMapsQueryUsadas` |
| 7 | Sin rastro de la corrida fallida de MySqlConnector | **PASS** | Contigüidad perfecta de los 3 rangos de `Id` (un INSERT abortado habría quemado `AUTO_INCREMENT`). 0 soft-deletes hoy, 0 huérfanos, `UpdatedAt IS NULL` en las 880 filas nuevas |

### N2. Cupo diario real (`CupoDiario`=940, `MetaDiaria`=400)

Ninguna campaña activa es multi-día (todas 1 bit de `DiasSemana`) ni cae en fin de semana → sin doble conteo. `Completa=1` **no** excluye del envío (`SendDailyBatchAsync` filtra sólo por `Activa` y `Dias`), así que las 17 completas también suman.

| Día | Campañas | % previas | % tanda A | % tanda B | % total | Mensajes/día | % de MetaDiaria |
|---|---|---|---|---|---|---|---|
| Lunes | 46 | 42,55 | 3,80 | 3,21 | 49,56 | **466** | 116,5% |
| Martes | 65 | 42,60 | 4,00 | 3,17 | 49,77 | **468** | 117,0% |
| Miércoles | 71 | 42,55 | 4,00 | 3,31 | 49,86 | **469** | 117,2% |
| Jueves | 60 | 42,54 | 3,80 | 3,35 | 49,69 | **467** | 116,8% |
| Viernes | 42 | 42,55 | 3,60 | 3,28 | 49,43 | **465** | 116,2% |
| Sáb/Dom | 0 | — | — | — | 0,00 | 0 | — |

### N3. Observaciones no bloqueantes

1. **(MEDIUM, coste) El próximo barrido nocturno triplica el consumo de la API de Google Maps.** `BusquedaDiariaGlobalAsync` → `SearchTodasActivasAsync` recorre **todas** las campañas activas **todos** los días, sin filtrar por `Dias`. Hoy ejecutó 91 queries en 6-7 min con 108 campañas; con 284 campañas y 164 industrias nuevas sin backlog va a disparar del orden de **~255 queries** (Text Search hasta 3 páginas + Place Details por resultado cada una). No rompe nada — el scheduler reintenta sin re-ejecutar queries ya usadas — pero conviene mirar la factura del primer día.
2. **(LOW) Demanda diaria agregada ~17% arriba de `MetaDiaria`** (≈467 vs 400). Preexistente (el 2026-08-25 ya se enviaron 519 reales), no causado por esta expansión (aporta 6,4-7,3 puntos), pero ahora con pool suficiente (1474 `Pendiente`, 1141 alcanzables) para materializarse. Palanca: `RebalancearMatrizAsync`.
3. **(LOW, cosmético)** Slug vs. `Nombre`: `comercio-sanjuancapital` se llama "Comercio San Juan". Sin impacto — el `Nombre` no participa de ninguna resolución.

### N4. Efecto colateral positivo no reportado por ninguna tanda

12 de las `ClaveRubro` nuevas ya existían como valor de `Contacto.Rubro` de contactos huérfanos. Al crearse las campañas quedaron **adoptados 266 contactos preexistentes, 127 de ellos `Pendiente`** (`comercio-tucuman` 25, `comercio-bahiablanca` 21, `comercio-mardelplata` 18, `dieteticas-bahiablanca` 13, `dieteticas-salta` 11, `comercio-salta` 8, `indumentaria-ushuaia` 7, y 5 rubros más). Los huérfanos `Pendiente` bajaron a **333**. Esas 12 industrias van a saltear la búsqueda en el próximo barrido (`RestockCampanasAsync` omite si `pendientes >= perRubro`, y `perRubro`=2): empiezan a enviar sin gastar API.

### N5. Hallazgo preexistente confirmado — queries viejas sin anclaje geográfico

Lo reportó la tanda B de paso; queda cuantificado: **140 de las 721 queries previas** no contienen ni la primera ni la última palabra de la `Region` de su campaña. Muchas son barrios distintivos que Maps resuelve solo (`Fisherton`, `Cerro de las Rosas`, `Las Cañitas`, `City Bell`), pero hay un subconjunto genuinamente ambiguo: `clinica Ensenada`, `farmacia Tolosa`, `boutique Gonnet`, `farmacia Los Hornos`, `clinica Berisso` (La Plata); `boutique/farmacia/sanatorio Godoy Cruz` (Mendoza); `inmobiliaria Olivos/Tigre/Pilar/Boulogne` (Zona Norte GBA); `farmacia Av. Corrientes`, `estudio jurídico Tribunales`, `negocio Avenida de Mayo`, `farmacia Diagonal Norte`, `casa de moda Florida` (Microcentro); `boutique Chacarita`, `sanatorio Colegiales`, `centro médico Chacarita` (Palermo). **No se tocó nada.** Candidato natural a la próxima ronda de "afinar campañas".

### N6. Aprendizajes de método reutilizables

- **La contigüidad de `AUTO_INCREMENT` es la mejor prueba de que un script abortado no dejó rastro.** Si `COUNT(*) = MAX(Id)-MIN(Id)+1` sobre el rango insertado, ningún INSERT falló a mitad de camino (un rollback igual quema el id). Más barato y más concluyente que buscar filas huérfanas una por una.
- **Verificar el universo entero en vez de muestrear, cuando el universo cabe en un `GROUP BY`.** El pedido pedía 3 ciudades por tanda para el `IndustriaCatalogoId` y 30-40 queries para la calidad geográfica; una firma agregada por ciudad (`GROUP_CONCAT(rubro:catalogo)`) cubre las 22, y un `LIKE` contra un diccionario derivado cubre las 528. Mismo coste, cobertura total.
- **La separación de escrituras por timestamp sigue funcionando** (ya usada en la auditoría del mismo día): scheduler 03:02-03:09, expansión de queries 03:49-03:50, tanda A 04:01-04:04, tanda B 04:05. Permite atribuir cada `UpdatedAt` a su autor sin que el script haya dejado marca propia.
- **Chequear la unicidad de una clave incluyendo las filas soft-deleteadas** cuando el código que la resuelve no filtra `DeletedAt` — `SearchByRubroAsync` hace `.Where(i => i.ClaveRubro == rubro).OrderByDescending(i => i.CampanaOutbound.Activa).FirstOrDefault()` sin filtro de borrado.
- **Un alta masiva de campañas no sólo agrega superficie de envío: agrega superficie de búsqueda diaria.** El restock global corre sobre todas las campañas activas todos los días, desacoplado de `Dias`, así que el impacto en la factura de la API escala con el total de campañas, no con las de hoy.

## Historial de ajustes
- 2026-08-28 (expansión nacional de outbound): QA de un **cambio de datos** en producción — 176 campañas + 176 industrias + 528 queries insertadas por 2 agentes en paralelo sobre 22 ciudades nuevas. Sólo lectura contra la base real, 0 escrituras. **GO, 7/7 PASS, 0 defectos.** Conteos exactos y rangos de `Id` perfectamente contiguos (142-317 / 142-317 / 881-1408), `ClaveRubro` única en 304/304 filas incluyendo las soft-deleteadas, `IndustriaCatalogoId` verificado en **las 22 ciudades** con firma idéntica y coincidente con el mapeo de las 108 preexistentes, las 6 campañas protegidas intactas (`UpdatedAt` ≤ 08-26; las únicas escrituras de hoy sobre filas viejas son del scheduler de 03:02-03:09), integridad referencial sin un solo huérfano, y las **528** queries con anclaje geográfico correcto (510 con la ciudad en el texto, 18 con localidad vecina + provincia), 0 duplicados y 0 colisiones con `GoogleMapsQueryUsadas`. Cupo real **465-469 msj/día** (49,4-49,9% de `CupoDiario`=940, lejos del techo y con tope global duro que lo hace inviolable). El incidente de MySqlConnector de la tanda A no dejó rastro — probado por contigüidad de `AUTO_INCREMENT`. **3 observaciones no bloqueantes**: el próximo barrido nocturno pasa de 91 a ~255 queries de Google Maps (el restock global recorre todas las campañas activas todos los días, sin filtrar por `Dias`) → salto de coste de API a vigilar; la demanda diaria quedó ~17% arriba de `MetaDiaria`=400 (preexistente, palanca `RebalancearMatrizAsync`); slug vs. `Nombre` cosmético. **Efecto colateral positivo no reportado por las tandas**: 266 contactos huérfanos adoptados (127 `Pendiente`), huérfanos totales de 460 a 333. Hallazgo preexistente cuantificado: **140 de 721 queries viejas** sin anclaje geográfico a su `Region`, con ~20 genuinamente ambiguas — no se tocó, queda como deuda.
- 2026-08-28: QA de la feature **matriz de módulos valorizados + borrador de propuesta MVP/FULL**, previa al primer deploy (código sin commitear, migración sólo en dev). Método: build propio en Release **2 veces** (0 errores / 13 advertencias preexistentes, antes y después del auto-fix), app levantada contra `olvidatacrm_dev`, **26 pantallas, 8 endpoints POST/AJAX y 29 generaciones de mensaje** por HTTP autenticado, con assertions SQL independientes. MCP `playwright` no disponible (declarado; residuo manual acotado al texto real de la pregunta 1 por WhatsApp). **Los 11 escenarios del Implementador: 11 PASS** (el #4 con 1 defecto, auto-fixeado). Seed verificado contra la base —**84/88/9/62** y los 9 rangos por rubro coincidiendo uno por uno—; la lectura inicial de 89/10 resultó ser 2 filas soft-deleteadas de datos de prueba, eliminadas al cerrar. Los 5 rubros sin matriz (incluido **Alquiler de inmuebles**, el hallazgo del Implementador) muestran el aviso, no un checklist vacío. Las **9 reglas de redacción**: PASS, con el truncado a 4 ítems verificado en el caso pedido (**Ganadería con 7 imprescindibles → "y 3 más"**) y **el bug del doble "y" confirmado como corregido leyendo la salida, no el código**. Wiring de "Sugerir" probado con **12 contactos reales** cubriendo los 3 vocabularios de `Contacto.Rubro`: 7 con matriz (incluido `estudio`, o sea el fix del mapeo funcionando, y `indumentaria-once` con sufijo de región), 5 con el comportamiento viejo intacto. Cuestionario del bot: `Questions["build"]` en **2 preguntas** con la numeración de emoji correcta, `Contacto.CantidadUsuarios` **sin un solo escritor ni lector** (por grep), y la tabla de decisión computada contra la base da **7 rubros al mecanismo nuevo + "Vinos y bebidas" al menú fijo**; los 2 hallazgos del Implementador (`MecanismoPregunta1Async` como fuente única en los 2 call sites, `ArmarPitchPostDolorAsync` reconociendo las 2 fuentes) verificados, con la prueba social real confirmada para los rubros nuevos. **El fix Farmacia/Contabilidad no reintroduce cotización automática**: rastreados todos los consumidores hasta el último (`industria?.Plan` sólo dentro de `if (PresupuestoCotizadoUsd.HasValue)`, campo que el bot ya nunca setea; `CotizaAutomatico` sigue en `false`). `.gitignore` efectivo y **ningún archivo de clave commiteado nunca** (`git log --all` sin resultados) — cierra la duda que el Implementador dejó abierta. Regresión del sprint ya deployado: 24 rutas sin 500, 0 `[ERR]`/`[FTL]`. **1 defecto: CRM-015 (major) — auto-fixeado.** Los módulos cuyo nombre empieza con sigla salían deformados en el texto que se copia al WhatsApp del cliente (`ABM Cuadrilla` → `aBM Cuadrilla`, `SEO básico y deploy` → `sEO…`, `CRM de WhatsApp` → `cRM…`): 9 de 84 módulos, los 9 imprescindibles, en 4 de los 9 rubros. Catalogado en `docs/qa/regresiones-manuales.yml` **antes** del fix, corregido con un guard de sigla inicial en `PropuestaMvpFullService.Minuscula()` (sin lógica de negocio nueva: restaura la intención ya declarada en el comentario del propio método), y re-verificado sobre **18 mensajes con 0 fallas** y sin regresión en los nombres que sí deben bajar la inicial. 4 observaciones no bloqueantes (interpretación de la regla 5, "y" duplicada que viene del nombre del módulo, inconsistencia matriz-con-0-MVP entre los 2 consumidores, comentario desactualizado en `RubroHelpers`). Estado dev restaurado (84/88/9/62). Estado: **GO para deploy de producción** (deploy no ejecutado, queda para el cliente; pendiente commitear y aplicar la migración en producción).
- 2026-08-27 (re-verificación acotada post-corrección): re-test de **CRM-007 / CRM-010 / CRM-012** tras la corrección del Implementador (§9), con app corriendo contra `olvidatacrm_dev` y assertions SQL independientes. **CRM-007 cerrado**: `ImpactoDelete` contrastado contra ground truth propio en **las 14 industrias** (no solo las 7 con datos) con coincidencia exacta —Retail 155, Laboratorios 104, Inmuebles 58, Utilities 38, Ganadería 35, Estudios 28, Farmacias 1, y 0 legítimo en las otras 7—, más reasignación real probada en ambas ramas (destino inválido → rechazado sin borrar nada; destino válido → contacto #158 `farmacia`→`estudio-palermo`, con auditoría estampada, quedando cubierto por la campaña activa #35, que es el círculo que M-B nunca cerraba). **CRM-010 cerrado**: el selector guarda `ClaveRubro`; alta real de un Referido (#442) que satisface el filtro completo de `SendDailyBatchAsync`; `Edit` conserva el rubro heredado y no lo pisa al editar otro campo. **CRM-012 cerrado**: `Alineadas` es propiedad calculada, sus 3 entradas coinciden con SQL independiente (0/19, 0/19, 0/18), y se forzó una divergencia real para ver la alerta disparar (5,3%/5,3%/0,0% → badge "Divergen"). **CRM-008 descartado por el cliente** (falsa alarma de la pasada anterior: se probó contra dev y se confundió con producción). Riesgo declarado por el Implementador (`BotFlowService` sin tocar) **confirmado**: los contactos con rubro reescrito por el bot (#194, #236) no son contados ni reasignados —son inalcanzables por construcción—, pero se detectó que la protección es **incidental y no una guarda explícita**: 18 contactos con conversación (17 en `AwaitingCategory` esperando respuesta + 1 `Completed`) conservan su `ClaveRubro` y sí quedan dentro del conteo/reasignación, contra lo que afirma el comentario del código → nuevo **CRM-014 (minor)**, que incluye además la colisión por mayúsculas entre la clave `farmacia` y el nombre de diálogo `"Farmacia"` (sin impacto hoy: 0 contactos). Build propio en Release **0 errores / 13 advertencias preexistentes**, 0 migraciones nuevas, 18 pantallas autenticadas todas 200, 0 errores en Serilog, dev restaurado y verificado. Ningún archivo de código modificado por QA. Estado: **GO para deploy de producción** (deploy no ejecutado, queda para el cliente).
- 2026-08-27: QA del sprint "corrección de bugs/gaps de auditoría completa + 3 mejoras" (17 items: B1-B7, G1-G7, M-A/M-B/M-C). **Primera pasada de QA de este proyecto con la aplicación efectivamente ejecutada** — build propio en Release (0 errores), app levantada contra `olvidatacrm_dev`, 12 pantallas y 6 endpoints POST/AJAX ejercitados por HTTP autenticado, con verificación del efecto real en base de datos antes/después de cada acción y restauración del estado de dev al terminar. MCP `playwright` no disponible en la sesión (declarado); sustituido por verificación HTTP + assertions sobre la BD. Resultado: **10 PASS, 4 PARCIAL, 2 FAIL, 1 PASS-con-observación**. Los 4 puntos que el Implementador marcó como delicados quedaron los 4 confirmados (B3 manda `ultimoIdVisto` en cada tick; G6 estampa `UpdatedAt`/`UpdatedByUserId` con el claim correcto en los 2 call sites, verificado en BD; G5 negocia bien los 2 invocadores; `EtiquetaErrorEnvio` quedó como evento). 7 defectos nuevos: **CRM-007** (major, bloqueante — `Industrias/ImpactoDelete`/`Delete` cuentan y reasignan por `IndustriaCatalogo.Nombre` cuando el vocabulario real de `Contacto.Rubro` es `CampanaOutboundIndustria.ClaveRubro`: devuelve `contactos: 0` para las 14 industrias mientras `/Bot/Salud` del mismo sprint reporta 425 huérfanos, dejando a G7 y M-B sin cumplir e informando algo falso), **CRM-008** (major, bloqueante — la migración `AddMensajeProgramado` no estaba aplicada; se aplicó en dev, falta en producción, sin ella `Chats/Detail` queda caído), **CRM-009** (B3: pestaña en background marca leído un entrante nuevo, contradiciendo la HU), **CRM-010** (B7: el Referido manual no entra al pipeline, misma causa raíz que CRM-007), **CRM-011** (G1: tope de reintentos cuenta fallos históricos, no consecutivos, sin reset), **CRM-012** (M-C: `Alineadas=true` hardcodeado), **CRM-013** (citas cruzadas incorrectas al catálogo). **Sin auto-fix**: la causa raíz de los bloqueantes es una decisión de diseño no tomada (vocabulario canónico de `Contacto.Rubro`), así que se escala al Implementador por regla del rol. Ningún archivo de código modificado por QA. B2 verificado con el escenario exacto de su HU (campaña Lunes+Miércoles: 400 msj/día en ambos, contra los 800 que daba el agrupamiento viejo) y G3 verificado end-to-end incluida la exclusión del ARR. Estado: **NO-GO para producción** por los 2 bloqueantes; **GO parcial** para los otros 15 items una vez aplicada la migración y revertido/degradado el modal de Industrias.
- 2026-07-25: QA del ajuste de UI en `Notifications/Index.cshtml` (ícono `fas fa-xmark` + modal SweetAlert2 reemplazando `confirm()` nativo). Método: revisión de código + diff contra HEAD para aislar el alcance de esta tarea de la feature previa de borrado (2026-07-24) + rebuild completo independiente (`dotnet build --no-incremental` → 0 errores, 9 warnings preexistentes idénticos a lo ya documentado). Confirmado: 2 íconos `fa-xmark` (0 `fa-trash` residual), 0 `confirm()`/`onsubmit` residual, patrón `Swal.fire` consistente con `Campanas/Index.cshtml`, `NotificationsController`/`NotificationService`/`INotificationService` sin ningún cambio atribuible a esta tarea (solo contienen lo ya documentado de "eliminar notificaciones"). Catálogo cross-proyecto reevaluado para items relevantes (KOI-001 PASS, resto N/A sin cambios). **Cero defectos.** Estado: **GO** para prueba manual del cliente.
- 2026-07-17: Primera pasada de QA funcional sobre la migración de BotPublicitario (HU-01 a HU-11, CU-01 a CU-06 y CU-10 a CU-12). Método: revisión de código completa por capa + recompilación + verificación de migraciones + playbook cross-proyecto (24 items preexistentes evaluados + 6 items nuevos catalogados: CRM-001 a CRM-006). Validados los 3 riesgos que señaló el implementador (CU-04 sin bug de lógica, Farmacia/Contabilidad comportamiento esperado, credenciales ausentes confirmado como bloqueo). Detectados 6 defectos nuevos no catalogados previamente (3 major: CRM-001 sin auditoría del toggle outbound, CRM-004 sin manejo de duplicado en batch de Google Maps, CRM-006 notificación in-app nunca implementada; 3 minor: CRM-002 UI de cambio de estado visible para Vendedor, CRM-003 ordenamiento de columna ignorado, CRM-005 categoría de fallback incorrecta en máquina de estados del bot). Por instrucción explícita del orquestador para esta tarea, ningún defecto nuevo (no catalogado previamente) fue auto-corregido en esta pasada — los 6 quedan documentados en `docs/qa/regresiones-manuales.yml` con `archivos_fix` sugeridos, pendientes de una pasada del Implementador. Recomendación: NO-GO para producción/uso comercial real hasta resolver los 3 defectos major; GO condicional para uso interno de Contactos/Industrias sin bot activo.
- 2026-07-21: QA de "campañas de contacto frío configurables" (CU-13/14/15, HU-12 a HU-16). Método: revisión de código completa contra Análisis/Diseño/Arquitectura + recompilación independiente + verificación de migración aplicada + corrida real de 20s confirmando seed (13 campañas) sin excepciones. Cobertura del catálogo cross-proyecto reevaluada para los items relevantes a la superficie nueva (KOI-001 PASS, 32-estándares N/A justificado — la pantalla no usa combo multi-select tradicional, GAN-003 PASS, resto sin cambios respecto a la pasada anterior). **Cero defectos funcionales detectados** — solo 2 observaciones de UX no bloqueantes (inconsistencia reload vs. DOM-update entre AgregarIndustria y el resto de las acciones AJAX; comparación de `ClaveRubro` no fuerza case-insensitive a nivel SQL, sin impacto real porque todas las claves ya se generan en minúsculas). Estado: **GO** para uso interno; pipeline outbound real queda sujeto al mismo criterio ya vigente (no activar `Standby=false` sin verificación manual + credenciales confirmadas).
- 2026-08-28: QA de un cambio de **datos** en producción (no de código): expansión de 93 queries de Google Maps sobre 33 `CampanaOutboundIndustria` + reset de racha/`Completa`, hecha por script descartable ya borrado. Método nuevo para el rol: sin build/deploy/navegador — consultas de sólo lectura contra la base real + lectura de `GoogleMapsService` para entender el consumo de los campos tocados. **Aprendizaje reutilizable**: cuando el cambio se aplica por SQL crudo, `UpdatedAt` NO se setea (lo setea EF, no la base), así que no sirve para identificar filas tocadas ni para detectar daño colateral — hay que identificar el universo por `CreatedAt` de las filas insertadas y validar el resto por **reconciliación de estado** (acá: las campañas `Completa=1` pasaron de 50 a 17 y los 17 reconcilian exacto contra 10 Ski + 5 Mercado Municipal + 2 descartadas por cobertura). Ayuda mucho que el scheduler nocturno corra a otra hora (03:02-03:09) que el script (03:49-03:50): permite separar escrituras por timestamp. Resultado: **GO**, 5/5 criterios PASS, 0 duplicados, 0 daño colateral, `ClaveRubro` intacto (verificado indirectamente vía historial de `GoogleMapsQueryUsadas`). 6 observaciones LOW de calidad geográfica (deriva Palermo→Belgrano en 4 campañas, Gran Mendoza etiquetado como Mendoza Capital, etc.), todas cosméticas porque se verificó en código que `CampanaQuery.Zona` nunca llega a la API de Google y `Contacto.Zona` no filtra ni rutea nada. 1 hallazgo preexistente ajeno al cambio: `Dieteticas Montevideo` (57) con `SinResultadosNuevos=1` pero `Completa=0` — única fila así en la base, la campaña no busca nunca y no aparece como agotada en la UI.
