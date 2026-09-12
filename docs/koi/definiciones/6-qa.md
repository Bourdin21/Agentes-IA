# Memoria QA — KoiDumplings
# Última actualización: 2026-09-11 (Etapa 6 — regresión completa de todo lo entregado desde el 2026-09-08)
# Última validación de reglas cross-proyecto: 2026-09-11

## Estado del sistema (2026-09-08)
- Build: **PASS** — `dotnet build` 0 errores, 9 warnings, todos preexistentes (8 × NU1902 MailKit/MimeKit = VUL-001, 1 × CS0114 `HomeController.StatusCode`).
- EF migrations: sin cambios pendientes. Última: `20260908162332_E19_ConceptoGastoImporteEditadoManual` (aplicada en producción).
- Producción: `https://portaldelinversor.com.ar/koi/` — 23 pantallas verificadas, **0 errores 500**.

---

## Etapa 6 — Regresión completa de lo entregado desde el 2026-09-08 (corrida 2026-09-11)

**Alcance:** los 16 commits de `b0f70a0` a `7cdfe20` (≈16.000 líneas agregadas). Pedido del dueño: *"volver a probar todas y cada una de las mejoras realizadas a partir del 8 de septiembre"*.

### Camino de verificación usado — IMPORTANTE
El MCP `playwright` **no estaba disponible** en la sesión. Los tres agentes cayeron al camino equivalente que prevé `33-verificacion-automatizada-qa`: **Chromium real vía el paquete npm `playwright` 1.63 desde Node**, cruzando cada número con SQL. No se dio nada por PASS desde HTML plano.

**Entornos aislados (uno por agente, para que las escrituras no se contaminen):** tres copias de `koidumplings_dev` (`koidumplings_qa_a/b/c`) y tres instancias de la app publicada en `https://localhost:7101/7102/7103`. **Producción quedó como sólo lectura** y sólo para el caso del path base `/koi`, que no se reproduce en localhost. Cada agente restauró su base al baseline al terminar.

### Cobertura
| Área | Agente | Casos | Resultado |
|---|---|---|---|
| Estado de Resultados y gastos | A (7101) | 23 | NO-GO por KOI-011 |
| Inversores y liquidaciones | B (7102) | 17 | NO-GO condicional por KOI-B01 |
| Accesos, Dashboard, Ayres | C (7103) | 26 | GO |

### Lo verificado del núcleo de la entrega (todo PASS, con evidencia)
- **Guard de duplicados del catálogo viejo (`7cdfe20`)** en los dos sentidos: mes con catálogo viejo vivo → 14 filas, 3 aperturas, 14 filas; una fila borrada a propósito NO se recrea. Mes sin catálogo viejo → completar vacíos sí crea la fila (`ImporteCalculado = 612.269,22` = 1 % de 61.226.922).
- **Regresión de la Etapa 19b cerrada (`l1`)**: 3 recargas del mes, 4 porcentuales idénticos. Abrir la pantalla no escribe nada.
- **Corte de la rentabilidad al último mes CERRADO (`7cdfe20`)**, con el borde forzado: pasando las liquidaciones de feb/mar/abr-26 a Pendiente (última pagada = enero), la UI sigue diciendo **19 meses**; cerrando agosto-26 salta a **22**. La regla vieja habría dicho 18.
- **Recupero ARS ≠ USD y ARS mayor en los 15 inversores**, al decimal contra SQL. Irigo: 41,2 % U$D = 6.180,03/15.000 y 53,2 % $ = 7.822.750/(15.000 × 980).
- **Duplicación de liquidaciones al reabrir**: cerrar → reabrir → cerrar da 15 / 0 vivas / 15 vivas, **0 duplicados**.
- **Aislamiento del inversor**: no ve facturado/informal ni etiquetas que lo insinúen; el reporte de otro inversor da **403** (IDOR cerrado, con usuario Inversor real — antes estaba BLOCKED).
- **Accesos y menús**: Gerente carga datos pero no cierra el mes (4 POST rechazados server-side) y no ve inversores (12 URLs directas); rol Encargado con permisos reales; "Notificaciones de cierre" arriba de "Nueva Notificación".
- **Dashboard**: 0 errores de consola JS en 14 pantallas × hasta 4 roles × 2 viewports; canvas de Chart.js renderizando de verdad; tarjetas parejas a 400 px.
- **Importador**: reimportar el mismo Excel da 0 nuevos / 53 actualizados.
- **Recuperar contraseña**: las 4 consignas PASS, con el mail real capturado y el envío asincrónico funcionando.

### Defectos nuevos
| Id | Sev. | Qué | Estado |
|---|---|---|---|
| **KOI-011** (DEF-A01) | **CRÍTICA** | `AuditLogs.Action` es `varchar(20)` y dos acciones nuevas miden 21: `RecalculoPisaManuales` (`f7d8413`) y `EdicionPeriodoCerrado` (`48fc20e`) → `Data too long for column 'Action'`. **Corregir un mes cerrado y pisar manuales nunca funcionaron en producción** (verificado: la columna es `varchar(20)` y no hay ninguna fila con esas acciones). Es fail-safe, pero empuja al usuario a reabrir el mes — la operación destructiva que la Etapa 25 vino a evitar. | Enviado a implementación |
| **KOI-012** (DEF-A03) | ALTA | La migración `E20_ConsolidacionCatalogos_A2` tiene el mapeo como **ids literales de producción**. En una base con otros ids traslada plata al concepto equivocado (observado: `Alquiler del local 4.500.000 → Cristalería & Equipamiento`). Producción quedó bien; se corrompe cualquier entorno nuevo. | Enviado a implementación |
| **KOI-B01** | ALTA | El tilde "Se muestra" de un benchmark **siempre se guarda en `false`**: el `<input type="hidden" value="false">` está **antes** del checkbox y el binder de `bool` toma el primero. Rompe la comparativa de mercado de los 15 inversores al primer guardado, sin vuelta atrás por UI. `Views/Configuracion/Benchmarks.cshtml:90-92` y `:135-136`. Confirmado en código por el orquestador. | Enviado a implementación |
| **DEF-A02** | ALTA | `PisarManuales` (`EstadoResultadosController.cs:592-615`) no captura `DbUpdateException`: HTTP 500 con body vacío. `GuardarConceptoEnPeriodoCerradoAsync` sí lo maneja. | Enviado a implementación |
| **KOI-B02** | MEDIA | Dashboard en blanco al cambiar de año desde la vista del inversor: `cargarHistorico(12)` hace `getElementById('btnHist12').classList` sin null-guard (`Views/Dashboard/Index.cshtml:1013-1014`, invocado desde `:1093`). Confirmado en código por el orquestador. | Enviado a implementación |
| **KOI-B05** | MEDIA | El historial marca `Enviado` justo después de llamar a `SendEmailAsync`, que corta en silencio sin SMTP host o sin destinatarios válidos (`NotificacionCierreService.cs:91-92`). | **Decidido 2026-09-11:** marcar `Enviado` recién con el OK del envío. Pendiente de implementar |
| **KOI-B06** | MEDIA | Cerrar un mes **manda los mails solo**: `ConfirmarCierre` encola el envío (líneas 783-789). La previsualización protege el reenvío, no el mes recién cerrado. | **Decidido 2026-09-11:** sacar el envío del cierre; se administra sólo desde Notificaciones de cierre. Pendiente de implementar |
| **D-C01** | MENOR | El Administrador llega a `/Audit` por URL (200) aunque el link esté oculto. Sin filtración: la consulta filtra por usuario. Choque entre `AuditController.cs:10` y `_Layout.cshtml:339`. | **Decidido 2026-09-11:** Auditoría sólo para SuperUsuario. Pendiente de implementar |
| **D-C02** | MENOR | Con `ModuloCamaras` apagado, `/Camaras/Ver` sigue en 200 para todos, incluido el Inversor. El flag esconde en vez de apagar (diseño catalogado en KOI-005). | **Decidido 2026-09-11:** bloquear también la pantalla. Pendiente de implementar |
| **KOI-B03/B04, D-C03, OBS-A06** | BAJA | Pantallas de acción que sólo rechazan en el POST; flechas de orden en una tabla `ordering:false`; copia vieja del JS en `obj/` de publicación; el detalle de liquidaciones pendientes aparece después de guardar y no antes. | Backlog |

### Observaciones sobre datos (no son defectos de código)
- **OBS-A04:** en la copia de dev, 2026-08 suma dos veces Regalías, Canon y las dos Previsiones ($ 4.207.913,25). En producción ese mes **ya está conciliado** (2026-09-10), así que no aplica.
- **OBS-A05:** reimportar el Excel completo sobre los históricos duplicó los gastos de 2024-11 a 2025-12 en la copia de dev. En producción el efecto quedaría acotado a los 6 pares no consolidados: **no conviene reimportar el Excel completo sin resolverlos antes**.
- **Ayres:** `koi.ayresit.com:8520` no es alcanzable desde esta máquina (el permiso de salida está atado a la IP del hosting). Se cubrió con un stub fiel al contrato real: 4 ventas `C` + 3 `X` dieron 1.050.000 / 4 ventas / 22 comensales, y el día con una sola anulada no aparece en la serie. **La exclusión de anuladas funciona**. **El dueño confirmó el 2026-09-11 que la integración opera bien en producción**, así que el ítem queda cerrado: la limitación era del entorno de pruebas, no del código.
- `IntegracionAyres` está en `false` en dev: la tarjeta de evolución diaria no existe ahí.

### Reglas cross-proyecto
`6-qa.md` no tenía el campo de última validación, así que se ejecutó el catálogo entero como primera validación. **No hubo reglas nuevas ni modificadas desde el 2026-09-08.** Ejecutadas y PASS: REG-004, REG-008, REG-010, KOI-001, KOI-003, KOI-004, KOI-005/006 (43 links de sidebar × 3 roles, 0 rotos), KOI-010, SG-001, GAN-005, GAN-006, LP-003, LIP-001, ELV-001, MH-009/MH-014, PAT-017. **KOI-009 → RESUELTO** (verificado en producción: raíz → 404, `/koi/…` → 302, el JS desplegado usa `KOI_BASE`).

### Go / No-go de la corrida
**NO-GO hasta corregir KOI-011 y KOI-B01.** El núcleo de lo entregado desde el 8/9 está verde y verificado con evidencia; los dos bloqueantes son de superficie (una columna corta y dos líneas de Razor invertidas) pero dejan muertas dos funciones que el cliente va a usar.

### Re-test tras los fixes (misma corrida, 2026-09-11)

Se re-publicó la app en los tres entornos con los commits `db49b95`, `2baeced` y `4d82c86`, y se aplicó **E24** en las tres bases de prueba. Los agentes A y B re-testearon con su contexto y su base intactos.

**Área A → GO.**
- **k2 (corregir un mes cerrado):** 2026-02, Regalías `2.290.959,09 → 2.291.959,09`. Fila de auditoría `Id 2057`, `Action='EdicionPeriodoCerrado'` (21 car.). Liquidaciones **pendientes** 15/15 recalculadas (delta −950,00); **pagadas 0 cambiadas**, `UpdatedAt` intacto. El período sigue Cerrado.
- **l2 (pisar manuales):** HTTP **200** con `{"success":true,"pisados":1,...}` — ya no hay 500. `ImporteCalculado = 1.836.807,66`, `ImporteEditadoManual = 0`. Auditoría `Id 2074`, `Action='RecalculoPisaManuales'`.
- **DEF-A02 forzado de verdad:** volviendo la columna a `varchar(20)`, el pisado responde **200** con `{"success":false,"message":"…"}` y un cartel legible, en vez del 500 con body vacío; no se pisa nada; la excepción queda capturada en el log. Devuelta a `varchar(50)`, vuelve a funcionar.
- **OBS-A06 RETIRADA por el propio QA:** la observación se había hecho sobre 2026-02, cuyas 15 liquidaciones pagadas están soft-deleted por una reapertura previa, así que el bloque no tenía nada que mostrar. Re-testeado sobre 2026-04 (15 pagadas vivas), el aviso **previo** sí lista cada inversor con importe y fecha de pago. El ítem del checklist queda **cumplido**.
- **Regresión:** el guard de `7cdfe20` y `l1` se comportan exactamente igual que en la primera corrida (14→14 filas, fila borrada no se recrea, 3 recargas sin cambios).

**Área B → GO.**
- **KOI-B01:** el POST ahora viaja `["checkbox=true","hidden=false"]`; `Activo` queda 1 / 0 / 1 en los tres pasos y un benchmark nuevo nace en 1. **La comparativa volvió al reporte del inversor** y escala bien contra KOI: S&P 500 15,0 % dibuja 36,4 % de la barra de KOI (41,2 %). Destildar lo saca del reporte; re-tildar lo devuelve.
- **KOI-B02:** año sin datos renderiza con su aviso y **consola limpia** (antes: `TypeError … reading 'classList'`); año con datos sigue dibujando (12 → 12 puntos, toggle a 24 → 22 puntos).
- **Regresión:** Irigo 41,2 % / 53,2 % sobre **19 meses** → 2,2 % / 2,8 %; Caicedo 15,7 % / 17,3 % sobre **14 meses**. Idénticos a la primera corrida y al cruce por SQL. 265 liquidaciones vivas, 0 duplicados, IDOR cerrado.

**Cosmético corregido después del re-test (`4d82c86`):** los tres mensajes de error decían "No se modifico nada" sin tilde, y el aviso previo mostraba `$115.435 , pagada el` (faltaba el espacio tras el signo y sobraba uno antes de la coma, por el salto de línea entre el `</span>` y el `@if`).

### Pasadas 3 y 4 — decisiones del dueño implementadas y verificadas (2026-09-11)

Los cinco cambios decididos por el dueño (`4dd42a9`) y el fix de `KOI-B07` (`f017f01`) se verificaron sobre los mismos entornos aislados. **Áreas B y C: GO.**

- **Auditoría sólo SuperUsuario:** Administrador pasa de **200** a **AccessDenied**, incluido `POST /Audit/GetData`, que es el que devuelve las filas. Es el único controller que toca `AuditLogs`.
- **Cámaras:** 404 en las 5 acciones con el flag apagado — incluido `/Camaras/Ver` con rol Inversor, que antes daba 200 con la pantalla a la vista. **Reversible encendiendo el flag, sin redeploy.**
- **Cierre sin mails:** 15 liquidaciones y `registrosenvionotificacion` en **0**, repetido dos veces. Aviso previo, toast y banner con link a la previsualización de ese período; el banner no reaparece al recargar.
- **`Enviado` con confirmación,** medido por mails entregados en un catcher SMTP propio: sin SMTP → **Fallido** con motivo (antes decía Enviado); con SMTP → **Enviado y los 3 entregados**; servidor caído → **Fallido** con el error de conexión. Ninguna fila fallida sin explicación. El test de email de Sistema ahora se pone rojo cuando corresponde.
- **`KOI-B07`:** tanda fallida reintentada → **3 mails**; período ya enviado → **0 mails incluso forzando el POST directo**; mezcla → **exactamente los 2 que faltaban**, sin duplicar al ya notificado; doble disparo simultáneo → **3 mails**, uno por inversor.
- **Tarjetas de Mi Inversión:** medidas por posición real en pantalla. 1440 px: Inversor · Dividendos U$D · Recupero U$D arriba, Capital · Dividendos $ · Recupero $ abajo. 400 px: cada par U$D/ARS junto, sin huérfanas ni scroll horizontal.
- **Regresión en las tres pasadas:** Irigo 41,2 % / 53,2 % sobre 19 meses; Caicedo 15,7 % / 17,3 % sobre 14. Idénticos al SQL. 0 errores de consola, 0 HTTP 5xx, IDOR cerrado.

### Estado final: DEPLOYADO Y VERIFICADO EN PRODUCCIÓN (2026-09-11)
Migración `E24` aplicada primero (backup `bkp_20260911_auditlogs`, 1.308 filas), después el deploy de los cinco commits (83 archivos). 8 pantallas en 200, `/Camaras/Ver` en 404, y los tres meses conciliados intactos. **Las dos funciones que nunca habían andado en producción —corregir un gasto de un mes cerrado y pisar valores manuales— quedan operativas.**

### Go / No-go final de la corrida
**GO para el build `4d82c86`**, con una condición de despliegue: en producción `AuditLogs.Action` **sigue en `varchar(20)`**, así que hasta que se corra el script de E24 allá, corregir un mes cerrado y confirmar el pisado **siguen rotas para el cliente**. Orden correcto: **script primero, deploy después**.

### Defectos nuevos dados de alta en el catálogo cross-proyecto
`KOI-011` (columna de auditoría corta), `KOI-012` (migración con ids de producción), `KOI-013` (hidden antes del checkbox), `KOI-014` (script de inicio sin guard). El catálogo pasó de 67 a 71 ítems.

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
