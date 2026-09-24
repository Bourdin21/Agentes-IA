# Memoria QA — KoiDumplings
# Última actualización: 2026-09-23 (Etapa 7b — re-test del sprint "Fixes y mejoras", agente A: GO)
# Última validación de reglas cross-proyecto: 2026-09-23

## Estado del sistema (2026-09-08)
- Build: **PASS** — `dotnet build` 0 errores, 9 warnings, todos preexistentes (8 × NU1902 MailKit/MimeKit = VUL-001, 1 × CS0114 `HomeController.StatusCode`).
- EF migrations: sin cambios pendientes. Última: `20260908162332_E19_ConceptoGastoImporteEditadoManual` (aplicada en producción).
- Producción: `https://portaldelinversor.com.ar/koi/` — 23 pantallas verificadas, **0 errores 500**.

---

## Etapa 7 — QA del sprint "Fixes y mejoras" — AGENTE B (corrida 2026-09-23)

**Alcance:** ítems **2, 3, 6, 7, 8 y 9** + barrido legal **E1**, sobre `5a52462`, `ef47250` y `e7c24d8`
(base `f017f01`). Estado de Resultados, conceptos y gestión de usuarios quedaron para el agente A.

### Camino de verificación usado — IMPORTANTE
El MCP `playwright` **no estaba disponible** en la sesión. Se declaró y se usó el camino equivalente ya
validado el 2026-09-11: **Chromium real vía el paquete npm `playwright` 1.63 desde Node**, contra
`https://localhost:7102` (Development) y la base aislada `koidumplings_qa_b`, cruzando cada número con SQL.
**Ayres no es alcanzable desde esta máquina**: se montó un **stub fiel al contrato** (login → `tokenAccess`,
`GET /ventas` con Bearer, fechas de ida `yyyy-MM-dd` y de vuelta `dd/MM/yyyy`, sobre anidado, estados `C`/`X`).
**Producción no se tocó.** Por regla dura del pedido **no se modificó código fuente**, así que el auto-fix
obligatorio quedó suspendido y declarado.

### Lo verificado en verde (con evidencia)
- **Ítem 3 — endpoint de sincronización.** Sin header → **401**; clave equivocada (incluida una con el mismo
  prefijo y un carácter de más) → **401**; clave correcta → **202**; repetido → **200 `yaEncolada:true`**;
  `GET` → 405. **Fail-closed verificado de verdad**: con `Integraciones:ApiKey` vacía los 4 intentos dan
  **503** y no se escribe nada. El trabajo encolado **escribe**: 23 filas (corta en HOY, no a fin de mes),
  total 17.500.000, días sin ventas en **0** y no omitidos, **anuladas `X` excluidas** (140 cubiertos = 20×7),
  3 tramos de 10 días. **Idempotente**: segunda corrida deja 23 filas, mismo total, 0 duplicados.
- **Ítem 2 — gráfico.** Canvas con **91.379 píxeles pintados** (getImageData), barras, **una sola serie**,
  23 labels, suma = SQL exacto. "Actualizado el 23/09/2026 a las 16:01 h". **Borde de 26 h exacto**:
  25 h sin aviso, 26 h con aviso; redacta "hace un día / 2 días / 8 días". Tabla vacía → 200 con
  "Todavía no se actualizó" (distinto de "vendió $ 0"). Con el **E.R. del mes vacío** la pantalla igual dibuja
  el gráfico: los tres bloques son independientes, que era el punto del rediseño.
- **Ítem 7 — flechitas.** **82 inputs `type=number`** en 5 pantallas de carga, **100 % con
  `appearance: textfield`**. La regla está en `site.css` **y** en `olvidata-theme.css`. **Rueda real**
  (`mouse.wheel` ×5) sobre un campo enfocado: el valor no se mueve.
- **Ítem 8 — Enter.** Las dos grillas (`.concepto-input` 46 campos, `.consumo-input` 15): Enter baja 1,
  Shift+Enter sube 1, última fila hace **blur sin navegar**, Tab intacto. **6 Enter seguidos en Preview de
  cierre: 0 navegaciones, sin modal, y 2026-07 sigue Abierto.**
- **Ítem 9 — filtros.** Los 4 filtros cruzados contra SQL, uno a uno y combinados (12 casos, todos exactos).
  **Se aplican en el servidor**: el cliente recibe 19 / 15 / 1 filas según el filtro, no 280. Los combos no
  colapsan. El filtro **sobrevive al detalle** (Reabrir → Cancelar) **y a un POST** (marcar pagadas: 15→13
  pendientes, 0→2 pagadas, vuelve con el filtro puesto).
- **E1 — lo explícito.** 11 patrones (facturado/informal/lado A/B/blanco/declarado/fiscal…) → **0 hits** en el
  texto visible **y** en el HTML servido completo. Gráfico de **una sola serie** rotulada "Ventas". **La serie
  no viaja por un endpoint aparte** (va en el ViewModel; único XHR: notificaciones).
- **PAT-017 / IDOR cerrado.** Inversor ligado al id 26: propio → 200; ids 27, 28 y 1 → **AccessDenied**.
- **Permisos.** El Inversor recibe AccessDenied en Liquidaciones, RepartoGeneral, Users, Inversores,
  E.R. Mensual, Configuración y Audit.

### Defectos
| Id | Sev. | Qué | Estado |
|---|---|---|---|
| **KOI-015** (DEF-B01) | **CRÍTICA** | `ConceptosGastoQuery.ImportesAplicados` devuelve un `IQueryable` **ya proyectado** a `ImporteConceptoRow`; cualquier `.Where()` encadenado después **EF no lo traduce**. **500 reproducido** en `/RepartoGeneral`, `/EstadoResultados/Anual` y `/Dashboard/Historico?meses=12\|24` (canvas `#chartHistorico` con **0 píxeles pintados**). Falla igual con el predicado escalar que con el `Contains`: el problema es **filtrar después de proyectar**. 4 call sites (`InversionesService:249`, `EstadoResultadosService:1244`, `DashboardService:105`, `ImportacionExcelKoiService:522`). Introducido por el ítem 4 (`5a52462`). El build compila en verde: es falla de traducción en runtime. **`/EstadoResultados/Anual` está en el sidebar del Inversor.** | Alta en el catálogo; **fix NO aplicado** por la regla dura del pedido |
| **DEF-B02** | **ALTA** | **E1**: no hay desglose expuesto, pero **sí derivable**. "Ventas Totales" = A+B = $ 22.500.000 y la suma de las barras = A = $ 17.500.000 → la resta da **$ 5.000.000 = exactamente B**. Los montos diarios están **literales en el fuente** (`"monto":900000.00`) y el tooltip da el valor exacto por barra. **Es información nueva de este sprint.** | **Decisión del dueño pendiente** |
| **DEF-B03** | MEDIA | Regla nueva **OLV-002**: `badge bg-warning text-dark` ("Pendiente") mide **9,46 en claro** y **1,49 en oscuro** — el tema pisa `text-dark` a `rgb(241,245,249)` sobre amarillo. En Liquidaciones e Inversores | A implementación |
| **DEF-B04** | BAJA | Regla nueva **OLV-018**: el proyecto sirve **Bootstrap 5.1.0**, que no trae `fw-semibold` (existe desde 5.2). Resuelve a **font-weight 400**. Usada en **20 vistas** | A implementación |
| OBS-B05 | Obs. | `btn-primary`/`bg-primary` blanco sobre `#2b9de4` = 2,98 en los **dos** temas; `#64748b` del sidebar/footer = 3,75–4,31. Pre-existente, del design system compartido | Backlog del baseline |
| OBS-B06 | Obs. | La copia de dev **no tiene** las filas defectuosas del ítem 4 (0 filas, 0 AuditLogs de normalización): el defecto estaba en producción. **La corrección de datos del ítem 4 no pudo ejercitarse acá** | Para el agente A / copia de producción |

### Re-test del agente B tras los fixes (misma corrida, 2026-09-23 — build `8c22af6`)

Entorno actualizado: `343818f`, `e431905`, `8c22af6` en `https://localhost:7102`, base `koidumplings_qa_b`
con **E24, E25, E26 y E27** aplicadas.

- **KOI-015 CERRADO.** Las 16 rutas del barrido dan **200**, sin errores de consola ni 5xx.
  `/RepartoGeneral` abre; `/EstadoResultados/Anual` abre; `#chartHistorico` pasó de **0 a 175.033
  píxeles pintados** (12 puntos, 3 series) para SuperUsuario y para Inversor.
- **Ítem 6 CERRADO — PASS.** Las **22 filas** de Utilidad U$D coinciden con SQL **una por una**
  (`data-order` invariante: 30762.21, 3387.09, 0, -878.91, …). Orden **numérico** verificado por
  monotonía ascendente (-1.345 → 30.762). **Guion**: forzando `TipoCambio` a **NULL** y a **0**, las dos
  filas muestran `—` con `data-order` vacío y quedan agrupadas al ordenar, sin leerse como 0. La única
  fila que muestra `U$D 0` es Junio 2026, que efectivamente dio 0.
- **Estados del dato (PASS).** Caché vacía → las **cuatro** tarjetas muestran `—`, sin canvas, con aviso,
  0 errores JS: **ningún cero engañoso**. Filas con `Tickets` NULL (las viejas, previas a E27) → Ventas y
  Cubiertos con su valor real y **Ticket Promedio / Cant. de Tickets en `—`**, sin división por cero ni
  promedio absurdo. Dato de 40 h → aviso presente y tarjetas correctas.
- **Regresión de los ítems 3, 2, 7, 8 y 9: intacta.** Endpoint 401/401/401/**202**/**200 `yaEncolada`**/405
  + **503** fail-closed con clave vacía; caché 23 filas, 17.500.000, 140 cubiertos, **40 tickets** (E27
  puebla bien), días 7/14/21 en 0, idempotente (0 duplicados). Gráfico 91.379 px, 1 serie, suma exacta,
  0 errores. 82 inputs sin flechitas + rueda real bloqueada. Enter/Shift+Enter/blur/Tab y **6 Enter sin
  cerrar el período** (2026-07 sigue Abierto). Los 10 casos de filtros coinciden con SQL y el filtro
  sobrevive al detalle.

#### E1 — el intento de romperlo

**Dentro de `Mes actual`, el implementador tiene razón y se confirma.** Escenario con el local distinto
del POS (local A 19.317.431 + B 6.742.889 = 26.060.320; POS 17.500.000). Las cuatro tarjetas salen del
POS y cierran entre sí (17.500.000 / 437.500 = 17.500.000÷40 / 40 / 140 / 125.000 por cubierto). La torta
**manda sólo porcentajes** (57.9, 28.5, 13.7) y sus tooltips también. Los tooltips de las barras sólo dicen
Vendido y Cubiertos del POS. **Búsqueda exhaustiva sobre 207 números distintos** (visibles + HTML servido +
datasets), con 1, 2 y 3 operandos y +, −, ×, ÷ y porcentajes: **el total del local, el lado B y el lado A
del E.R. NO se reconstruyen**. Los tres "hits" que devolvió la búsqueda son falsos positivos sobre enteros
chicos (173, 51) alcanzables por azar desde valores de layout. Ningún secreto aparece literal en el HTML.

**Pero la pantalla no es el perímetro, y el dato sigue siendo deducible — DEF-B07 (ALTA).** Con el rol
Inversor, **sin tocar una sola URL a mano, sólo con dos links de su propio sidebar**:

1. "Mes actual" → **Ventas registradas = $ 17.500.000** (sólo POS).
2. "Historial de Resultados" (`/EstadoResultados/Anual`) → fila **Septiembre 2026: Ventas 26.060.320**,
   que es el **total del local (A+B)**.
3. Resta → **$ 8.560.320** (= lado B + la brecha POS vs. E.R.).

**Prueba de movimiento (la decisiva):** moviendo **sólo el lado B** en la base, "Ventas registradas" queda
clavada en 17.500.000 mientras la fila anual acompaña **uno a uno**: B=0 → 19.317.431; B=6.742.889 →
26.060.320; B=17.000.000 → 36.317.431. La anual es una función directa del secreto.

**Paradoja del fix, y es el punto:** mientras `Mes actual` mostraba el total del local —lo mismo que la
anual— **no había nada que restar**. Al pasarla a "sólo punto de venta" se publicó el lado A a alguien que
ya veía el total, y **se creó la diferencia**. El fix cerró la deducción dentro de una pantalla y abrió la
de dos pantallas, a un clic de distancia. **La confidencialidad hay que evaluarla sobre el menú completo
del rol, no pantalla por pantalla.** Alta en el catálogo como **KOI-016**.

**Fuga menor de la torta (DEF-B08, MEDIA):** los porcentajes de canal se calculan sobre el **local (A+B)**,
no sobre el POS. Comprobado moviendo sólo el lado B: pasan de 57,9/28,5/13,7 a **39,8/20,4/39,8** con el
POS intacto. No son invertibles a pesos por sí solos, pero son una función del secreto en una pantalla que
se declaró "sólo punto de venta", y delatan el movimiento del lado informal.

**El Administrador sigue viendo el total real (PASS):** E.R. Mensual muestra 26.060.320, el lado A
19.317.431 y los seis campos A/B de carga; el Dashboard muestra Ventas Totales y el desglose por canal con
las columnas "CON IMPTO. / S/IMPTO. (A)".

#### Go / No-go del área B tras el re-test
**GO condicionado a una decisión de negocio.** Todo lo técnico del área quedó en verde: los ítems **2, 3,
6, 7, 8 y 9 pasan**, KOI-015 está cerrado y los estados del dato no mienten. Queda abierto **DEF-B07**, que
no es un bug de código sino la misma decisión de E1 corrida de lugar: mientras el Inversor vea el total del
local en la anual y el total del POS en Mes actual, la resta existe. **DEF-B08** (la torta) sí es corregible
en código.

### Reglas cross-proyecto
Última validación previa: **2026-09-11**. El catálogo pasó de **71 a 92** ítems: **21 reglas nuevas**
(`OLV-001…OLV-020` + `CRM-023`, de `olvidata-agentes-multirubro`, 2026-09-14 al 16). `32-estandares-qa-implementador`
sin cambios posteriores. Ejecutadas todas las aplicables: **FAIL en OLV-002 y OLV-018**; **PASS** en OLV-001,
003, 005, 007, 008, 009, 011, 012, 013, 017, 019; **OBS** en OLV-004; **N/A** OLV-006, 010, 014, 015, 016, 020 y
CRM-023 (multi-tenant / flujos inexistentes en KOI). Del catálogo viejo: **FAIL en REG-004** y en **KOI-005/006**
(el link del sidebar del Inversor a `/EstadoResultados/Anual` da 500), PASS el resto del alcance.
**Alta nueva: `KOI-015`** — el catálogo queda en **93** ítems.

### Go / No-go del área B
**NO-GO.** Dos bloqueantes: **KOI-015** y la **decisión sobre E1**. Los ítems **3, 2, 7, 8 y 9 están en verde**
con evidencia cruzada contra SQL y navegador real; el **ítem 6 quedó BLOCKED** porque su pantalla no abre
(su fórmula sí se cruzó contra el E.R. mensual en 5 meses: 30.762,21 / 3.387,09 / -878,91 / 8.919,36 / 10.759,67).

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


---

# Etapa 7 — Sprint "Fixes y mejoras" (corrida 2026-09-23) — **agente A: ítems 4, 5, 10 y 1**

**Commits:** `5a52462` (E29), `ef47250` (E30), `e7c24d8` (E31) sobre `f017f01`. Matriz completa en
`<scratch>/qa/resultados-sprint-A.md`. Los ítems 2, 3, 6, 7, 8 y 9 los cubrió el agente B.

### Camino de verificación
MCP `playwright` **no disponible** — declarado, y sustituido por **Chromium real vía el paquete npm
`playwright` 1.63.0 desde Node** (`33-verificacion-automatizada-qa`). App `https://localhost:7101`,
base `koidumplings_qa_a` (vínculo app↔base verificado por la conexión MySQL del PID, no por
`appsettings`). **Producción no se tocó.** Foto SQL antes/después: **22 períodos idénticos al centavo**.

### Veredicto por ítem
| Ítem | Veredicto |
|---|---|
| 4 — cierre vs. vista anual | **NO-GO** — D-A01 (la anual da 500) + D-A02 (E25 aborta) |
| 5 — el Encargado da de alta conceptos | **GO** (con O-A01) |
| 10 — eliminar concepto con alcance | **GO** (con O-A02) |
| 1 — gestión de usuarios | **NO-GO** — D-A02 (las 3 acciones de contraseña en 500) + D-A03 |

### Defectos nuevos

**D-A01 — [CRÍTICO] Cuatro rutas en 500 por el código del ítem 4.** `ConceptosGastoQuery.ImportesAplicados`
proyecta a un `record` y los cuatro consumidores encadenan el `.Where` **después** de la proyección; EF no
traduce a través del constructor del record. Caen `/EstadoResultados/Anual` (la pantalla que el ítem 4
venía a arreglar, visible para **todos** los roles incluido Inversor), `/Dashboard/Historico`,
`/EstadoResultados/ExportarAnualExcel` y `/RepartoGeneral`. Un quinto consumidor
(`ImportacionExcelKoiService:522`) tiene la misma forma. **Engaña:** un año sin períodos devuelve 200
porque el bucle no ejecuta la consulta. *Fix propuesto:* filtrar **antes** de proyectar, dentro de
`ConceptosGastoQuery`.

**D-A02 — [CRÍTICO] `AuditLogs.Action` es `varchar(20)`; los literales nuevos miden 22, 25, 26 y 31.**
Las etapas 29 y 30 declararon "sin migraciones EF". Rompe: las tres acciones de contraseña (500),
`Users/Edit` con contraseña (**regresión de legado**, ya existía antes del sprint) y el script
`E25_normalizar.sql` (`ERROR 1406`, aborta en la primera sentencia y **no mueve ninguna fila**).
**Lo grave es el orden:** la contraseña se cambia antes del registro de auditoría, así que el 500 llega
con el daño hecho — `ResetPassword` deja la cuenta con una clave generada que **nunca se muestra**
(verificado: `qa.admin2@qa.koi` quedó inaccesible). Ampliando la columna a `varchar(64)` sólo en la base
QA, E25 corre limpio y sus 4 controles dan lo esperado (0 pendientes, 0 períodos divergentes, las dos
reglas iguales en 1.423.104.404,31). *Columna restaurada a `varchar(20)` al cerrar.*

**D-A03 — [ALTO] La rendija del SuperUsuario sin rol es real.** `CanManageUser` resuelve el rol con
`FirstOrDefault() ?? ""` y compara por desigualdad: sin fila en `AspNetUserRoles`, el SuperUsuario aparece
en el listado como "Sin rol" y un Administrador **lo edita, lo bloquea y le resetea la contraseña**
(verificado: quedó `Estado = 2` con hash distinto; restaurado desde `koidumplings_dev`). Es una decisión
**fail-open** sobre la identidad más privilegiada.

**O-A01 — [obs]** El alta de un concepto porcentual por el Encargado no se rechaza: el servidor la
**coerciona a Manual en silencio** y contesta "creado correctamente".
**O-A02 — [obs]** "Para siempre" deja el concepto visible con badge "Histórico" e importe 0 en el mes
desde el que se dio de baja.

### Lo que sí quedó verificado (con evidencia)
- **Regla unificada del importe:** mensual, Dashboard y cierre dan el mismo número en 6 períodos, cruzado
  contra SQL. Con el defecto de producción **sembrado a mano** en 2026-05, las tres convergen; tras E25
  vuelven a incluir el gasto. La **anual no se pudo comparar** (D-A01).
- **El defecto del ítem 4 NO existe en `koidumplings_dev`:** los cuatro conceptos tienen las dos columnas
  iguales, E25 movió **0 filas** y escribió **0 AuditLogs**. El alcance real de producción (8 filas,
  $ 15.680.662 y $ 27.263.960,72) **no está verificado por este QA**.
- **Ítem 5:** 15 rutas/POST del resto de `ConfiguracionController` → todas AccessDenied; alta manual OK;
  el concepto nuevo aparece en el E.R. del mes en curso.
- **Ítem 10:** los dos caminos contra la base (lápida + revivir; baja de catálogo con históricos
  conservados), guard de importe 0 en los dos, mes histórico sin "Para siempre", mes cerrado sin botón.
- **Ítem 1:** la **barrera sobre SuperUsuario aguanta las 8 acciones armando el POST a mano**; el combo de
  Editar preselecciona el rol actual y no lo degrada; los guards de borrado (inversor, auditoría, uno
  mismo) explican y ofrecen desactivar; **la auditoría ya no guarda el hash** (`AffectedColumns` = solo
  `["UpdatedAt"]`); POST sin antiforgery → 400.

### Reglas cross-proyecto nuevas desde 2026-09-11 (diff `c09e84d`..`HEAD`)
11 reglas nuevas en el `32` + 33 ítems nuevos en el yml. Ejecutadas las de mi alcance:
**REG-011** PASS · **REG-012** PASS · **VSF-003** PASS con nota (E25 no filtra por `Subgrupo.DeletedAt` a
propósito) · **CRM-019** PASS (sin `StartsWith` en consultas EF) · **OLV-010** PASS · **OLV-019** PASS con
O-A01 · **OLV-008** PASS · **OLV-015/016** PASS. El resto (contraste/tema oscuro, Select2, filtros
persistidos, multi-tenant, topes de gasto) no aplica a mis ítems o es del agente B.

### Altas sugeridas para `regresiones-manuales.yml` (no escritas — el archivo tiene cambios de otros proyectos en curso)
- **KOI-012** — proyección a un `record` con `.Where` encadenado después: EF no traduce, 500 en runtime con build verde.
- **KOI-013** — literal de auditoría más largo que la columna `Action`: el `SaveChanges` tira y se lleva puesta la operación que **ya se ejecutó**.
- **KOI-014** — guarda de privilegio que resuelve el rol con `FirstOrDefault() ?? ""`: sin rol = gestionable (fail-open).

### Pendientes bloqueantes
- [ ] **D-A01** — filtrar antes de proyectar y re-verificar las 5 rutas.
- [ ] **D-A02** — migración EF que amplíe `AuditLogs.Action` a ≥ 64, desplegada **antes o junto** al código y al script E25.
- [ ] **D-A03** — guarda fail-closed sobre usuarios sin rol resoluble.
- [ ] Pre-vuelo de E25 contra producción para confirmar el alcance real (8 filas esperadas).
- [ ] Documentar al cliente que agosto-2025 y mayo-2026 repartieron por encima del resultado real.
- [ ] **Código y script E25 van juntos:** el código sin el script hace que la anual pase a mostrar el número **optimista equivocado** en esos dos meses.


---

## Etapa 7b — RE-TEST del sprint "Fixes y mejoras" (2026-09-23, agente A) — **GO**

**Build:** `343818f`, `e431905`, `8c22af6` sobre los tres commits del sprint. **Base:** `koidumplings_qa_a` con **E24, E25, E26 y E27**; `AuditLogs.Action` en `varchar(50)`, modelo EF `HasMaxLength(50)` — sin drift. Vínculo app↔base re-verificado (PID 26728 → `:61172` → `koidumplings_qa_a`).

| Defecto | Veredicto |
|---|---|
| **D-A01** — 4 rutas en 500 | **CERRADO** |
| **D-A02** — `AuditLogs.Action` corta | **CERRADO — era diferencia de entorno, no defecto de producción** |
| **D-A03** — SuperUsuario sin rol | **CERRADO** |
| Ítems 5 y 10 | **siguen PASS**, sin cambios |
| Regresión de períodos sanos | **PASS** — 22 períodos idénticos al centavo |

**D-A01.** El fix fue el propuesto: `ConceptosGastoQuery` ya no expone `IQueryable`; recibe los ids de período, filtra **antes** de proyectar y materializa adentro (`ImportesAplicadosAsync` / `TotalesPorPeriodoAsync`), y los 4 consumidores pasaron al API nuevo. **Verificado con contenido, no con el status:** `Anual` 2024/2025/2026 con 2/12/8 filas y sus totales, `Dashboard/Historico` con 22 meses de decimales exactos, `ExportarAnualExcel` devolviendo un xlsx real (magic `504b`), `RepartoGeneral` con 22 filas. **Las 22 filas de la anual coinciden una por una con SQL.** El falso negativo del año sin datos sigue existiendo (`?anio=2030` → 200 vacío), por eso se probó sobre años con datos.

**Criterio 4c, que estaba BLOCKED, ahora PASS.** Con el defecto de producción **sembrado** en 2026-05, las **cuatro** pantallas convergen en 41.540.795 (antes la anual habría dicho 58.371.917 y la mensual 41.540.795 — esa era la divergencia del dueño). `E25_normalizar.sql` corre con `EXIT=0`: 3.1 → 0 pendientes, 3.2 → 0 períodos divergentes, 3.3 → las dos reglas iguales, 3.4 → 2 filas auditadas. Después, las cuatro vuelven a 58.371.917 con el gasto incluido.

**D-A02 — corrección de mi reporte anterior.** No era un defecto de producción: mi base venía de `koidumplings_dev`, tres migraciones atrás, con `Action` en `varchar(20)`; producción tenía **E24** desde el 11/9. Lo que sí valió del hallazgo es el modo de falla, confirmado: **la contraseña se cambia antes del registro de auditoría**, así que cualquier excepción ahí deja la cuenta modificada con la clave sin mostrar. Ahora las tres acciones y `Users/Edit` con contraseña dan 302; la clave generada **se muestra una sola vez**, **loguea**, y no queda en la auditoría (0 apariciones); 0 filas nuevas con `PasswordHash`/`SecurityStamp`. Literales de `Action`: 11 distintos, máximo 31 (`MailRecuperacionEnviadoPorAdmin`) + 26 del script — entran holgados en 50.

**D-A03.** `PuedeGestionar(roles, email)` es fail-closed: cuenta del seed intocable por identidad, lista **completa** de roles, y sin rol resoluble sólo la gestiona un SuperUsuario. Cuatro escenarios × 8 acciones: **Administrador 32/32 rechazos**; SuperUsuario 24/32, y las 8 que pasan son las de `qa.sinrol`, que es exactamente lo que la regla 3 habilita. **Cero daño** — los cuatro objetivos quedaron con estado, email y hash intactos, contra la corrida anterior donde el SuperUsuario terminaba bloqueado y con la clave cambiada. Confirmado también el caso del **doble rol** Administrador+SuperUsuario, que antes se colaba por `FirstOrDefault`.

**Observación nueva — O-A03:** ningún SuperUsuario se gestiona desde la pantalla, **ni siquiera por otro SuperUsuario** (las reglas 1 y 2 no tienen válvula de escape). Es endurecimiento deliberado, pero deja sin camino en la app para resetear la contraseña de un segundo SuperUsuario: queda "olvidé mi contraseña" o la base. **O-A01** (el porcentual del Encargado se coerciona en silencio) y **O-A02** (el concepto dado de baja sigue visible como "Histórico" en ese mes) siguen abiertas, ninguna bloqueante.

**Pendiente que sigue vigente:** el código y `E25_normalizar.sql` **van juntos**, y el alcance real en producción (8 filas) **sigue sin verificar** — hay que correr el pre-vuelo del script contra producción antes de aplicarlo.

**Veredicto del área A (ítems 4, 5, 10 y 1): GO.**
