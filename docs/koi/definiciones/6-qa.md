# Memoria QA — KoiDumplings
# Última actualización: 2026-09-08 (Etapa 6 — QA del módulo E2-01 "Integración Ayres POS")

## Estado del sistema (2026-09-08)
- Build: **PASS** — `dotnet build` 0 errores, 9 warnings, todos preexistentes (8 × NU1902 MailKit/MimeKit = VUL-001, 1 × CS0114 `HomeController.StatusCode`).
- EF migrations: sin cambios pendientes. Última: `20260908162332_E19_ConceptoGastoImporteEditadoManual` (aplicada en producción).
- Producción: `https://portaldelinversor.com.ar/koi/` — 23 pantallas verificadas, **0 errores 500**.

---

## Etapa 6 — QA del módulo E2-01 "Integración Ayres POS" (2026-09-08)

### Camino de verificación usado — IMPORTANTE
El servidor **MCP `playwright` NO se cargó en la sesión** (el namespace `mcp__playwright__*` no estaba disponible; `.mcp.json` lo declara pero el server no levantó). Según `33-verificacion-automatizada-qa.instructions.md` correspondía caer al procedimiento manual, pero se encontró un camino automatizado equivalente y **se declaró explícitamente**: se manejó Chromium **directamente con `playwright-core` desde Node**, usando los binarios ya cacheados en `~/AppData/Local/ms-playwright/chromium-1243`.

- Scripts de la sesión: `<scratchpad>/qa/*.js` (`lib.js` + `t0`..`t17`, `baseline.js`, `final.js`).
- **Toda la verificación de UI de esta etapa es automatizada por navegador real contra PRODUCCIÓN**, no simulada por HTTP.
- Lo que **no** se pudo automatizar (requiere tocar config o infraestructura de producción) quedó como **prueba manual pendiente**, listado abajo.

### ⚠️ Hallazgo de estado que corrige la premisa de entrada
La consigna decía que septiembre 2026 tenía **todas las ventas en 0** y que era **el único período abierto**. **Las dos cosas son falsas** al 2026-09-08:

| Premisa de entrada | Realidad verificada |
|---|---|
| Septiembre en 0 | Septiembre **ya tenía ventas de Ayres aplicadas**: Salón 9.104.600,00 · Pedidos 1.573.830,00 · Mostrador 476.900,00 · 285 comensales · 180 ventas (total 11.155.330,00). Coincide exactamente con el preview de Ayres del momento de la verificación por HTTP → **`AplicarAyres` ya se había ejecutado sobre septiembre**. |
| Único período abierto = septiembre | Abiertos: **junio, julio, septiembre, octubre, noviembre y diciembre** (6). Cerrados: enero–mayo y **agosto**. |

**Decisión de QA:** NO se restauró septiembre a 0 —habría destruido datos—. Se capturó el estado real como baseline (`baseline-exacto.json`) y **se restauró exactamente a ese baseline** tras cada escritura. Verificado idéntico en ventas, conceptos y KPIs al cerrar.

Además, dos observaciones operativas para el dueño (no son defectos del módulo):
- **Junio 2026 está abierto y con ventas en 0**, pero Ayres tiene **46.969.508,00 / 841 ventas / 1.226 comensales** para ese mes. Hay un período abierto sin cargar.
- **Julio 2026 está abierto** con Salón A 33.889.149,00 y Salón B 27.337.773,00 cargados a mano.

### Escrituras realizadas en producción (todas informadas y revertidas)
| # | Qué | Dónde | Reversión | Verificado |
|---|---|---|---|---|
| 1 | `GuardarConcepto` — Gastos Extras (subgrupo 90) 0,00 → 1.234,56 | 2026-09 | → 0,00 | ✅ idéntico |
| 2 | `GuardarConcepto` — Gastos Extras 0,00 → 1.234,56 (2ª pasada, medición de KPIs) | 2026-09 | → 0,00 | ✅ idéntico |
| 3 | `GuardarConcepto` — Regalías (subgrupo 39) override a 999.999,99 | 2026-09 | `RevertirConcepto` → 334.659,90, vuelve a `ov-concepto-auto` | ✅ idéntico |
| 4 | `Recalcular` porcentuales | 2026-09 | idempotente | ✅ |
| 5 | **`AplicarAyres`** — escribió 9.301.600 / 1.573.830 / 476.900 / 291 / 183 | 2026-09 | `GuardarVentas` con los valores del baseline | ✅ idéntico |

**Estado final de septiembre 2026 = baseline exacto.** Ventas 11.155.330,00 · Total Gastos 836.649,75 · Resultado 10.318.680,25 (USD 6.744,24) · 0 overrides manuales.
**Ningún período cerrado fue tocado.** Sobre agosto solo se abrió el diálogo de reapertura y se canceló; siguió `Cerrado`.

### Cobertura de las 8 historias

| HU | Criterio | Resultado | Evidencia |
|---|---|---|---|
| **HU-A01** | Botón con período abierto; preview; nada se escribe hasta confirmar | **PASS** | Botón `#btnTraerAyres` visible en jun/jul/sep/oct/nov/dic (abiertos), ausente en ene–may/ago (cerrados). Al pulsarlo pasa a "Consultando Ayres..." + `disabled`. Solo se dispara `POST /EstadoResultados/PreviewAyres`. |
| **HU-A02** | Comparativo lado a lado, resalta solo lo que difiere, informa cuántas ventas y qué rango | **PASS** | Modal con tabla En el sistema / En Ayres. Filas que cambian en `fw-semibold`; iguales en `text-muted` con "=". Pie: *"Se leyeron 183 ventas entre el 01/09/2026 y el 30/09/2026 en 3 consulta(s) a Ayres."* Advertencia: *"Se excluyeron 4 venta(s) sin cerrar: X (4)…"* + KPIs (ticket 62.034,59 · cubierto 39.011,44 · ítems 5,54). |
| **HU-A03** | Al aplicar se guarda, los porcentuales se recalculan solos y se actualiza sin recargar | **PASS** | `AplicarAyres` escribió 11.352.330,00 / 291 / 183. Los 4 porcentuales se recalcularon solos: 340.569,90 (3 %), 283.808,25 (2,5 %), 113.523,30 y 113.523,30 (1 %) — todos exactos sobre la base nueva y todos siguieron en `ov-concepto-auto`. Total Gastos 836.649,75 → 851.424,75 y Resultado 10.318.680,25 → 10.500.905,25 **sin recargar la página** (URL sin cambio). Lado B intacto en 0,00. |
| **HU-A04** | Mes largo resuelto en tramos de ≤10 días, invisible para el usuario | **PASS** | Septiembre (30 d) → *"3 consulta(s)"*; junio (30 d) → 3; diciembre (31 d) → **4**. El usuario solo ve el número en el pie. |
| **HU-A05** | Caída de Ayres: avisa y el período queda intacto | **PASS (por código)** — no ejercitado en vivo | `AyresService` lanza `AyresIndisponibleException` **antes** de cualquier `GuardarVentasAsync`; el controller la captura y devuelve `success:false`. Mensajes separados: `"No se pudo conectar con Ayres. El período quedó sin cambios."` (red) vs `"Ayres rechazó las credenciales. Revisá la configuración."` (credenciales, flag `EsCredenciales`). **No se apagó la regla de puerto de producción.** |
| **HU-A06** | En período cerrado el botón no aparece y el endpoint rechaza | **PASS** | Agosto (cerrado): `#btnTraerAyres` ausente, 0 inputs de venta, 0 inputs de concepto. Enero–mayo y agosto: sin botón. El rechazo del endpoint (`"El período está cerrado."`) ya estaba verificado por HTTP por el dueño. Gating doble confirmado: vista `@if (esAdmin && !Model.EsCerrado …)` (línea 103) + `[Authorize(Policy="SoloAdministrador")]`. |
| **HU-A07** | `sectorTipo` desconocido → "Otros" + advertencia, sin descarte ni error | **PASS (por código)** — no reproducible en vivo | `AyresService.cs:420-421` mapea el canal desconocido a `CanalesAyres.Otros`, acumula en `SectoresNoMapeados` y arma la advertencia en el preview + `LogWarning`. Requiere que Ayres emita un sector nuevo: no forzable contra producción. |
| **HU-A08** | Probar la conexión desde Sistema sin tocar un período | **PASS** | `/System` → tarjeta "Conexión con Ayres POS" (`http://koi.ayresit.com:8520`) con la leyenda *"No consulta ni modifica ningún dato del sistema"*. "Probar conexión" → alerta **verde**: *"Conexión con Ayres correcta (467 ms). Las credenciales fueron aceptadas."* El diagnóstico temporal quedó eliminado: `/System/DiagnosticoAyres`, `?ping=1` y `?puertos=1` → **404** los tres. |

### Otros criterios de la consigna

| Ítem | Resultado | Evidencia |
|---|---|---|
| Cancelar → no escribe nada | **PASS** | Tras Cancelar: modal cerrado, botón restaurado, pantalla igual **y** el estado del servidor idéntico tras recargar. Única request: `PreviewAyres`. |
| Leyenda "mes en curso" | **PASS** | Septiembre (mes actual): *"El mes todavía no terminó: el total es parcial."* |
| Advertencia de ventas excluidas | **PASS** | Septiembre 4 anuladas, junio 23 — con la explicación de por qué importan (comensales y ticket). Se repite en el diálogo de éxito de `AplicarAyres`. |
| Mes sin ventas en Ayres | **PASS** | Diciembre 2026 → diálogo informativo *"Ayres no devolvió ventas para este período."* con **solo "Entendido"**, sin botón Aplicar. |
| Feature flag apagado esconde el botón | **PASS (por código)** — no ejercitado | `vm.AyresHabilitado = _features.IntegracionAyres && _ayresService.EstaConfigurado && !vm.EsCerrado` y `@if (Model.AyresHabilitado)`. Que el botón desaparezca en períodos cerrados prueba que el condicional funciona; la rama del flag no se pudo aislar sin editar la config de producción. |

### Regresión sobre el trabajo de hoy (misma pantalla)

| Etapa | Resultado | Evidencia |
|---|---|---|
| **18** — edición inline de gastos por AJAX + indicador por fila | **PASS** | Gastos Extras 0,00 → 1.234,56: spinner → check verde → se desvanece. Sin recarga. Subtotal del rubro 1.234,56, Total Gastos 836.649,75 → 837.884,31, Resultado −1.234,56 y USD actualizado. Persistió tras F5. Negativo (`-100`) → diálogo bloqueante, **0 requests**, revierte. Vacío → **0 requests**, revierte. Sin cambio → **0 requests**. |
| **19** — override manual de conceptos porcentuales + volver al % | **PASS** | Regalías 334.659,90 (`ov-concepto-auto`, botón oculto) → override 999.999,99 → clase `ov-concepto-override` + botón de reversión visible. **Sobrevivió a "Recalcular %"** (la decisión de diseño clave). "Volver al %" → 334.659,90, `ov-concepto-auto`, botón oculto. Idéntico tras recargar. |
| **19b** — recálculo automático de porcentuales al abrir | **PASS** | Sin tocar "Recalcular %", el GET rinde los 4 porcentuales exactos sobre las ventas vigentes (3 % → 334.659,90; 2,5 % → 278.883,25; 1 % → 111.553,30 ×2 sobre 11.155.330,00), marcados `ov-concepto-auto` (borde punteado). Subtotales 613.543,15 y 223.106,60 correctos. |
| **17** — reapertura de períodos por el Admin | **PASS** | Agosto (cerrado): "Reabrir período" visible. El diálogo informa **15 liquidaciones** reales, la salida de Rendimiento Histórico y la baja lógica + auditoría, y exige motivo. **Cancelado**: agosto siguió `Cerrado`. El guard de motivo vacío está en `preConfirm` (Mensual.cshtml:754) — **verificado por código, no ejercitado**, porque un fallo del guard habría reabierto un período cerrado real. |
| **20** — `ImportacionInicial` visible en "Sistema" | **PASS** | Sidebar: `/koi/ImportacionInicial :: Importación desde Excel` bajo la sección **SISTEMA** (no bajo Super Usuario). `GET /ImportacionInicial` → 200. ⚠️ Verificado con SuperUsuario; **falta confirmarlo con un login real de rol Administrador** (el estudio no tiene esas credenciales). |

---

## Defectos detectados

### KOI-009 [major] — URLs AJAX absolutas desde la raíz rompen bajo la app anidada `/koi` — **NUEVO, NO corregido**
- **Síntoma:** en producción, en toda pantalla: `404 GET https://portaldelinversor.com.ar/Notifications/GetRecent` y `404 GET .../Dashboard/Historico?meses=12` — **sin el prefijo `/koi`**. En consola: `Unexpected token '<', "<!DOCTYPE "... is not valid JSON` (el HTML del 404 parseado como JSON).
- **Impacto:** la campanita **nunca** lista notificaciones; el gráfico histórico del Dashboard **nunca** carga; marcar notificaciones como leídas no persiste; el toggle de tema no persiste.
- **Causa raíz:** 5 call sites escriben la URL como literal absoluto desde la raíz en vez de `Url.Action`/`Url.Content`. Funciona en local (PathBase vacío) y falla solo deployado bajo subdirectorio → pasa el build y la prueba local.
  - `KoiDumplings.Web/wwwroot/js/notifications.js:11` `$.get('/Notifications/GetRecent', …)`
  - `KoiDumplings.Web/wwwroot/js/notifications.js:46` `$.post('/Notifications/MarkAsRead', …)`
  - `KoiDumplings.Web/wwwroot/js/notifications.js:56` `$.post('/Notifications/MarkAllAsRead', …)`
  - `KoiDumplings.Web/Views/Dashboard/Index.cshtml:906` `fetch('/Dashboard/Historico?meses=' + meses)`
  - `KoiDumplings.Web/Views/Shared/_Layout.cshtml:402` `fetch('/Account/ToggleTema', …)`
- **Preexistente**, introducido con el deploy anidado (`4d88cea`). **No es una regresión de la Etapa 21.**
- **Por qué NO se auto-fixeó:** el impacto es *major*, no menor; el fix re-activa endpoints de **escritura** hoy muertos (`MarkAsRead`/`MarkAllAsRead`) y toca 3 archivos que afectan **todas** las pantallas, así que necesita su propia pasada de regresión con deploy — que este rol no hace. **Escalado al implementador** con el parche especificado en el catálogo.

### KOI-010 [minor] — el % de referencia se repinta con punto decimal — **AUTO-FIX APLICADO ✅**
- **Síntoma:** tras "volver al %" (o cualquier repintado AJAX), la celda mostraba **`3.00 %`** en vez de **`3,00 %`**. Se corregía solo al recargar. Convivía en la misma grilla con importes en es-AR.
- **Causa raíz:** `pintarPorcentajeConcepto()` usaba `valor.toFixed(2)` (siempre punto) en vez del helper `fmt()` que usa el resto de la vista (`toLocaleString('es-AR')`). Era **el único** repintado numérico de la vista que no pasaba por `fmt()`.
- **Fix aplicado** en `KoiDumplings.Web/Views/EstadoResultados/Mensual.cshtml:552-554`: `valor.toFixed(2)` → `fmt(valor)`, conservando el fallback `'—'`. Sin lógica de negocio nueva, sin migración, sin tocar cálculo ni escritura.
- **Post-parche:** `dotnet build` → **0 errores**, 9 warnings preexistentes. **Sin commit ni deploy** (los hace el dueño). La verificación en navegador del fix queda pendiente del deploy.

### Defectos anteriores — cambios de estado verificados en esta pasada
- **KOI-002 [major] → RESUELTO ✅** — "Exportar Excel" existe en Historial de Resultados → `/EstadoResultados/ExportarAnualExcel?anio=2026`, dispara la descarga.
- **KOI-005 [blocker] → RESUELTO ✅** — `CamarasController.cs` existe; `/Camaras/Ver` y `/Camaras` → 200.
- **KOI-006 [major] → RESUELTO ✅** — no hay link a `NotificacionesConfig` en el sidebar; los links de notificaciones apuntan a `/Notifications`, `/Notifications/Crear` y `/NotificacionCierre`, los tres → 200.
- **KOI-007 [major] → SIGUE ABIERTO** — `/Users` sin DataTables (`dt=0`), paginación manual.
- **KOI-008 [minor] → SIGUE ABIERTO** — `/TipoCambio` sin DataTables (`dt=0`).
- **VUL-001 → SIGUE ABIERTO** — MailKit 4.14.1 / MimeKit 4.14.0 con vulnerabilidad moderada; disponible 4.17.0.

---

## Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml` — 67 ítems)

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001..REG-009 | no | N/A | ShowroomGriffin (variantes/stock/compras/autocomplete). Sin equivalente en KOI. |
| REG-010 | sí | **PASS** | "Auditoría" solo bajo la sección SUPER USUARIO del sidebar. |
| KOI-001 | sí | **PASS** | Rubros/Subgrupos/Parámetros cargan y renderizan sus acciones; sin errores JS. |
| KOI-002 | sí | **RESUELTO** | Botón + acción `ExportarAnualExcel` presentes y funcionando. Cerrar en el catálogo. |
| KOI-003 | sí | **BLOCKED** | Requiere login con rol Inversor; el estudio solo tiene credenciales de SuperUsuario. El link existe en `_Layout` bajo el bloque Inversor. |
| KOI-004 | sí | **BLOCKED** | Verificarlo exige entrar al preview de cierre de un período real. No se ejecutó para no arriesgar un cierre en producción. Guard confirmado por código (JS + `CerrarPeriodoAsync`). |
| KOI-005 | sí | **RESUELTO** | `/Camaras/Ver` y `/Camaras` → 200. |
| KOI-006 | sí | **RESUELTO** | Sin link huérfano; todas las rutas de notificaciones → 200. |
| KOI-007 / KOI-008 | sí | **FAIL (abiertos)** | Sin DataTables en `/Users` y `/TipoCambio`. Sin impacto funcional; volumen bajo. |
| **KOI-009** | sí | **FAIL — NUEVO** | Alta en el catálogo. Escalado al implementador. |
| **KOI-010** | sí | **FAIL → CORREGIDO** | Alta en el catálogo + auto-fix aplicado. |
| DN-001, DN-002 | sí (patrón) | **PASS** | 23 pantallas, 0 errores 500; los listados con Include+OrderBy renderizan. |
| DN-003, DN-004 | no | N/A | Caja chica / reversa de pagos. KOI no tiene ese modelo. |
| GAN-001..GAN-006 | no | N/A | Facturas/pagos de Ganamos. GAN-005 (cultura en filas) sí se chequeó por analogía → los inputs de KOI rinden `F2`/`InvariantCulture` y hay `InvariantDecimalModelBinder` global. **PASS**. |
| VSF-001, VSF-002 | no | N/A | Máquina de estados de CompraProveedor. |
| CRM-001..CRM-016 | no | N/A | CRM de WhatsApp / bot. |
| MH-001..MH-021 | no | N/A | MariHogar. **MH-016** (edición inline + concurrencia) sí se revisó por analogía con la Etapa 18: KOI guarda por fila, sin RowVersion, y `pintarImporteConcepto` no pisa un campo con foco ni con guardado en curso → **PASS**. |
| SG-001 | sí (patrón) | **PASS** | Input de gasto vacío no rompe el POST: se valida en cliente, revierte y **no** manda request. |
| LP-001, LP-004, LP-005, LIP-001 | no | N/A | Otros proyectos. |
| LP-003 | sí (patrón) | **PASS** | Los `<input type=number>` rinden con `InvariantCulture` (`"9104600.00"`), no con es-AR: el navegador no descarta el value. |
| ELV-001 | sí | **PASS** | 10 rutas sensibles sin sesión → todas redirigen a Login. `POST /EstadoResultados/AplicarAyres` sin sesión → devuelve el HTML del login, no escribe. |
| ELV-002 | no | N/A | Sin equivalente Create/Update asimétrico. |
| PAT-017 (IDOR) | sí | **PASS (parcial)** | `/MiInversion` con `?inversorId=1`, `?inversorId=2`, `?id=1` → contenido idéntico: el parámetro se ignora y la identidad se resuelve server-side. **Parcial**: probado solo con SuperUsuario, sin credenciales de Inversor. |

---

## Máquina de estados verificada

### EstadoPeriodo (PeriodoMensual)
- `Abierto → Cerrado` — botón "Cerrar período" presente solo en abiertos ✅
- `Cerrado → Abierto` — **reapertura** (Etapa 17): botón solo en cerrados, motivo obligatorio, informa las liquidaciones a descartar. Diálogo abierto y **cancelado** ✅ (transición no ejecutada: es destructiva sobre datos reales)
- **Invariantes en período Cerrado** ✅ — sin inputs de venta, sin inputs de concepto, sin indicador por fila, **sin botón "Traer de Ayres"**
- **Invariante nueva (E2-01)** ✅ — `AyresHabilitado` es falso en todo período cerrado

### EstadoConceptoGasto (Etapa 19)
- `SigueEl% (ov-concepto-auto) → Override (ov-concepto-override)` — al escribir el importe a mano ✅
- `Override → Override` — **sobrevive a "Recalcular %"** ✅ (transición inválida correctamente bloqueada)
- `Override → SigueEl%` — vía `RevertirConcepto`, con confirmación ✅
- `SigueEl% → SigueEl%` — recálculo automático en el GET de períodos abiertos (19b) ✅

---

## Riesgos de liberación

1. **[alto] KOI-009 está vivo en producción.** Notificaciones y gráfico del Dashboard rotos en silencio desde el deploy anidado. No lo introdujo la Etapa 21, pero está en producción hoy. *Mitigación:* aplicar el parche del catálogo y re-verificar que no queden 404 a endpoints propios.
2. **[medio] D-A01 — la regla de salida del hosting apunta a la IP fija `190.245.226.181`.** Si Ayres migra de servidor la integración se corta sin aviso. *Mitigación:* el mensaje de red ya es explícito y "Probar conexión" (HU-A08) diagnostica en un click.
3. **[medio] R-A02 — la API de Ayres sigue siendo HTTP plano** con la credencial en el body. No lo resuelve el código de KOI. *Mitigación:* pedido a Ayres/MaxiSistemas de exponerla en 443 con TLS.
4. **[medio] Hay 6 períodos abiertos, no 1.** Junio abierto con ventas en 0 mientras Ayres tiene 46,9 M para ese mes. Con "Traer de Ayres" disponible en los 6, un click sobre el mes equivocado sobrescribe datos cargados a mano — el preview lo muestra antes, pero la superficie de error humano es real. *Mitigación:* cerrar los períodos que ya estén conciliados.
5. **[medio] HU-A05 y HU-A07 verificadas solo por código.** Nunca se ejercitó una caída real de Ayres ni un `sectorTipo` desconocido contra producción.
6. **[bajo] El rol Administrador nunca se probó con un login real** (solo SuperUsuario). Las policies y los `@if` están confirmados por código, pero KOI-003 y la Etapa 20 quedan sin evidencia funcional de ese rol.
7. **[bajo] `Mensual` (GET) escribe** — el refresco de porcentuales de la Etapa 19b crea/actualiza `ConceptosGasto` en un GET. Es idempotente y acotado a períodos abiertos, pero es un efecto lateral a recordar si alguna vez se cachea la pantalla.
8. **[bajo] VUL-001** — MailKit/MimeKit con vulnerabilidad moderada; actualizar a 4.17.0.

---

## Pruebas manuales que quedan pendientes (no automatizables desde acá)

1. **HU-A05 — caída de Ayres.** Apagar la regla de puerto saliente en el panel del hosting (o apuntar `Ayres:BaseUrl` a un puerto muerto) → "Traer de Ayres" debe decir *"No se pudo conectar con Ayres. El período quedó sin cambios."* y el período debe quedar intacto. **Restaurar la regla.**
2. **Credenciales rechazadas.** Cambiar `Ayres:Pass` por algo inválido → "Probar conexión" debe dar alerta **amarilla** con el mensaje de credenciales, distinto del de red. **Restaurar la clave.**
3. **Feature flag.** Poner `Features.IntegracionAyres: false` en `appsettings.Production.json` y recargar → el botón desaparece sin redeploy. Volver a `true`.
4. **Un solo login por importación.** Con el log en `Information`, una importación debe dejar **un** "login OK" y **un** "resuelto en N tramos". Si aparecen 4 logins, los ciclos de vida de DI quedaron invertidos (`AyresTokenCache` debe ser Singleton).
5. **Rol Administrador real.** Entrar con un usuario Administrador y confirmar: ve "Traer de Ayres", ve "Importación desde Excel" bajo Sistema, y **no** ve Auditoría.
6. **Rol Inversor real.** Confirmar KOI-003 (link "Historial de Resultados") y que no ve campos editables ni el botón de Ayres.
7. **KOI-004 — consumos > bruto** en el preview de cierre, sobre un período de prueba, nunca sobre uno real.

---

## Checklist de salida para merge

- [x] Build verde — 0 errores, sin warnings nuevos
- [x] Sin migración EF pendiente
- [x] Las 8 historias HU-A01..HU-A08 cubiertas (6 PASS por navegador, 2 PASS por código)
- [x] Cancelar no escribe — verificado contra el servidor
- [x] Período cerrado sin botón y sin inputs
- [x] Antiforgery + policy `SoloAdministrador` en `PreviewAyres` y `AplicarAyres`
- [x] Regresión de las Etapas 17, 18, 19, 19b y 20 — todas PASS
- [x] 23 pantallas sin error 500
- [x] Sin acceso sin autenticar; IDOR no reproducible
- [x] Producción restaurada al baseline exacto (ventas, conceptos y KPIs idénticos)
- [x] Ningún período cerrado modificado
- [x] KOI-010 corregido + alta en el catálogo
- [x] KOI-009 documentado y escalado con parche especificado
- [ ] **KOI-009 — aplicar el fix de rutas AJAX** (implementador)
- [ ] Pruebas manuales 1–7 de la lista de arriba
- [ ] Commit y deploy del fix de KOI-010 (los hace el dueño)
- [ ] Actualizar MailKit/MimeKit a 4.17.0 (VUL-001)
- [ ] KOI-007 / KOI-008 (DataTables) — backlog menor
