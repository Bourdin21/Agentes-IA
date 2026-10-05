# Memoria - QA

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-10-05 (v8 — Sprint 0, **RE-VERIFICACION del commit `00f7dd4`: GO**, los 7 defectos `LP-006`..`LP-012` CERRADOS, 1 hallazgo `minor` nuevo `LP-013`; antes: lote 1 dia/mes de negocio D9, lote 3 `UnidadVenta` + Dashboard/ABC, lote 2 cobro/ajuste de CC + D8, rama `entrega-1-migracion`)
## Ultima validacion de reglas cross-proyecto: 2026-10-05

---
# Sprint 0 — RE-VERIFICACIÓN de los 7 defectos (QA, 2026-10-05, rama `entrega-1-migracion`)

Gate del commit `00f7dd4` "Sprint 0 ronda de fixes: cierre de los 7 defectos de QA" (un solo commit,
25 archivos, **sin migración EF**). Contexto nuevo: los 7 criterios arrancaron **en FAIL** y se
re-ejecutaron contra el sistema corriendo; no se leyó la transcripción del implementador, sólo el
diff y el bloque "Sprint 0 — ronda de fixes de QA" de `5-implementador.md`.

## **GO.** Los 7 defectos quedan CERRADOS. Deja 1 hallazgo `minor` nuevo, no bloqueante (`LP-013`).

## Entorno y metodología

- `dotnet build FerreteriaLaPlatense.slnx` → **0 errores**, 9 advertencias **todas preexistentes**
  (8 × NU1902 MailKit/MimeKit + CS0114 en `HomeController.StatusCode`).
- `dotnet ef migrations has-pending-model-changes` → **"No changes have been made to the model since
  the last migration."** La afirmación del implementador de que no hace falta migración se verificó
  de forma independiente; la última migración aplicada sigue siendo la D9 del commit anterior.
- **Navegador real, esta vez sí.** El MCP `playwright` sigue sin estar expuesto en la sesión, pero —
  corrigiendo el error de método del lote 1 — se instaló `playwright-core` en el scratchpad de QA y
  se condujo el **Chromium completo** de `ms-playwright/chromium-1243/chrome-win64/chrome.exe`, con
  `locale: es-AR` y `timezoneId: America/Argentina/Buenos_Aires`. Eso es lo que permitió cerrar
  `LP-006`, que por HTTP era inverificable. El harness HTTP (cookies de Identity + antiforgery) se
  usó para las guardas de servidor y las 123 llamadas de regresión.
- Fixture `laplatense_qa_d9` reutilizado (el clon del lote 1). Línea base fijada antes de probar: se
  borraron los cierres diarios de 03/10 y 05/10 para dejar hoy abierto, se volvieron las ventas 10 y
  11 a Borrador y la entrega 2 a NoEntregada. **`laplatense_dev` y producción no se tocaron.**
- Siembras deliberadas, todas declaradas: un `CierreCajaMensual` de **10/2026** (el mes en curso, que
  por diseño no se puede cerrar desde la UI) para hacer alcanzable la rama mensual de la guarda en
  las vías que imputan a "hoy" — **eliminado al terminar**; y un `AjusteStock` con `Fecha` =
  `2026-10-01 01:44 UTC` para tener un caso nocturno en el historial de stock.
- **El repo del sistema bajo prueba no se modificó.** `git status --porcelain`: sólo `?? .claude/`,
  que ya estaba al abrir la sesión.

## Cobertura por defecto re-verificado

| id | sev. | resultado | evidencia observada |
|---|---|---|---|
| **LP-009** | `major` | **CERRADO** | Ver la tabla de las 6 vías abajo. 6/6 rechazadas con el mensaje del cierre **mensual**, **cero** filas persistidas, y los 3 controles positivos (mes abierto) siguen aceptando |
| **LP-010** | `major` | **CERRADO** | Venta 8 (`2026-08-25 01:44:10` UTC = 24/08 22:44 ART): rango `24/08..24/08` → `filtered=1` con `fecha: 2026-08-24T22:44:10.778381`; rango `25/08..25/08` → **0**; búsqueda `24/08/2026` → 1 y `25/08/2026` → 0; `/Ventas/Details/8` → **"24/08/2026 22:44"**; y en el **navegador** la grilla de Ventas dibuja `24/08/2026, 22:44`, el mismo día que Caja. Orden por la columna Fecha sigue funcionando tras materializar la página (12 filas, desc coherente) |
| **LP-011** | `minor` | **CERRADO** | `?anio=2026&mes=13`, `?anio=0&mes=0`, `?anio=1999&mes=5`, `?anio=2026&mes=-1` → los 4 **HTTP 200**, mensaje "Mes o año inválido (NN/AAAA): se muestra el mes en curso." y la pantalla cae en Octubre 2026. `POST CerrarMes mes=13` → 200 con el mismo mensaje, **ya no 500**. Controles: `?anio=2026&mes=9` → Septiembre 2026 sin mensaje; sin parámetros → mes en curso |
| **LP-012** | `minor` | **CERRADO** | Los dos buscadores **filtran de verdad**: en cierres diarios `1751,25`/`1751.25`/`1751` → ids `[1]`, `21/08/2026` → `[1]`, `30/09/2026` → `[4]`, `Zzz-nadie` → 0, `QA Super` → 3; en mensuales `2026` → `[1,3]`, `Septiembre`/`septiembre` → `[3]`, `Agosto` → `[1]`, `Marzo` → 0, `96.898,36` → `[3]`. **MH-001 no reproduce** (ver abajo) |
| **LP-007** | `minor` | **CERRADO** | `POST /Ventas/GuardarBorrador` con `continuar=zzz` → **"Acción no reconocida (\"zzz\"): el borrador se guardó pero la venta NO se cerró. Volvé a usar los botones Confirmar o Confirmar y facturar de la pantalla."**, y la venta 11 **sigue en Borrador** en la base. Control positivo: `continuar=""` → "Borrador de venta guardado correctamente." |
| **LP-008** | `minor` | **CERRADO** | Los 3 bloques de texto dicen "Confirmada o Facturada", conservan la justificación de `Borrador`/`Anulada`, y coinciden con los 3 predicados reales (`ClasificacionAbcAutomaticaService:86`, `DashboardService:62` y `:111`). Barrido: **cero** ocurrencias de "solo Facturada" / "únicamente Facturada" en esos archivos |
| **LP-006** | `minor` | **CERRADO (navegador real)** | `window.Fmt.fechaHora('…T00:00:00')` → **`05/10/2026, 00:00`** (antes `12:00:00`); `'…T13:04:22'` → **`05/10/2026, 13:04`** (antes `01:04:22`); `'…T22:44:10'` → `24/08/2026, 22:44`. `Fmt.fecha('2026-09-30T00:00:00')` → `30/09/2026` sin hora. `null`, `''` y `'no-es-fecha'` → string vacío, **nunca "Invalid Date"**. Las 8 grillas lo usan y dibujan 24h (Caja `13:10`/`12:56`/`00:00`, Ventas `22:44`, CC `00:00`, Stock `22:44`) |

### LP-009 — las 6 vías de escritura de caja, una por una

| # | vía | periodo cerrado probado | mensaje observado | persistió algo |
|---|---|---|---|---|
| 1 | Venta confirmada (`/Ventas/Confirmar/10`) | mes **10/2026** (sembrado) | "La caja del mes 10/2026 ya tiene cierre mensual: no se puede confirmar la venta. Contactar al administrador." | no — venta 10 sigue `Borrador` |
| 2 | Gasto alta (`/Gastos/Create`) | mes **09/2026**, día 15/09 abierto | "La caja del mes 09/2026 ya tiene cierre mensual: no se puede registrar un gasto con esa fecha." | no |
| 3 | Gasto anulación (`/Gastos/Anular/3`) | mes **10/2026** (sembrado) | "…no se puede anular un gasto hoy." | no — gasto 3 sigue `Anulado=0` |
| 4 | Cobro de CC (`/Clientes/RegistrarCobro`) | 09/2026 y 10/2026 | "…no se puede registrar un cobro con esa fecha." | no |
| 5 | Movimiento manual (`/Caja/MovimientoManual`) | mes **09/2026**, día 15/09 abierto | "…no se puede registrar un movimiento con esa fecha." | no |
| 6 | Cierre diario (`/Caja/CerrarDia`) | 16/09 (mes 09 cerrado) y 15/08 (mes 08 cerrado) | "La caja del mes 09/2026 ya tiene cierre mensual: no se puede cerrar un día de ese mes." (ídem 08/2026) | no — ninguna fila nueva en `CierresCajaDiarios` |
| — | **controles positivos** (mes 10/2026 abierto, día 02/10 abierto) | — | gasto, movimiento manual y cierre diario del 02/10 **aceptados** | sí, como corresponde |

`RegistrarAjusteAsync` **queda afuera con razón, verificado y no asumido**: el ajuste de CC con fecha
`15/09/2026` (dentro del mes cerrado) **se aceptó** y quedó en `MovimientosCCCliente` (id 7, Origen
`Ajuste`), y **no apareció ninguna fila nueva en `CajaMovimientos`**. Es decir: no toca Caja, así que
no le corresponde la guarda. No es un olvido.

### Lo que busqué por mi cuenta y no estaba en el parte

- **Doble conversión en el round-trip del borrador** — riesgo que introduce `MapearDetalle` al
  proyectar `Fecha = ArgentinaTime.From(venta.Fecha)`, porque ese DTO alimenta
  `VentaEditableViewModel.Fecha` y la pantalla de Editar lo postea de vuelta. Si `GuardarBorrador`
  escribiera ese valor, cada guardado correría la venta 3 horas. **Probado, no deducido:** 5
  guardados consecutivos del borrador 11 → `Fecha` intacta en `2026-09-03 16:20:14.338415`. **PASS.**
- **Barrido propio de la convención de fechas**, sin confiar en la tabla de 15 propiedades del
  implementador. `Domain/Entities` tiene **22** propiedades `DateTime` (las 15 de negocio + las de
  auditoría de `SoftDestroyable`/`ApplicationUser.UpdatedAt`). Clasificación verificada una por una:

| propiedad | semántica | cómo se expone | resultado |
|---|---|---|---|
| `CajaMovimiento.Fecha`, `Venta.Fecha`, `AjusteStock.Fecha`, `Entrega.FechaEntregada`, `MovimientoCCCliente.Fecha`, `CierreCajaDiario.FechaCierre`, `CierreCajaMensual.FechaCierre`, `ApplicationUser.CreatedAt` | instante UTC | proyectadas con `ArgentinaTime.From` | **PASS** — verificadas en pantalla: Stock/Historial `2026-10-01 01:44 UTC → 30/09/2026, 22:44`; **Entregas/Details/3 `2026-08-25 02:00 UTC → "ENTREGADA EL 24/08/2026 23:00"`** (caso nocturno real); Users `21/08` y `18/08` |
| `Gasto.Fecha`, `CierreCajaDiario.Fecha`, `Entrega.FechaProgramada`, `Producto.PrecioOfertaDesde/Hasta`, `Venta.VencimientoCAE` | día calendario argentino | se muestran crudas, con `Fmt.fecha` (sin hora) | **PASS** — correcto no proyectarlas; Gastos dibuja `30/09/2026` y `15/09/2026`, Entregas `21/08/2026` |
| `Gasto.FechaAnulacion`, `PagoVenta.Fecha` | instante UTC | **no se muestran en ninguna pantalla** | **N/A** — sin exposición, nada que proyectar (si mañana se muestran, van proyectadas) |
| `Notification.CreatedAt` / `ReadAt` | instante UTC | sólo vía `GetTimeAgo` = `DateTime.UtcNow - CreatedAt` | **PASS** — es un delta, el huso no interviene |
| `SoftDestroyable.CreatedAt/UpdatedAt/DeletedAt`, `ApplicationUser.UpdatedAt` | auditoría | no se exponen | **N/A** |

  Barridos mecánicos, los tres limpios: **cero** `DateTime.Today` / `DateTime.UtcNow.Date` /
  `DateTime.Now` / `ToLocalTime` en una decisión de día/mes en toda la app; **cero**
  `toLocaleString`/`toLocaleDateString` de fecha fuera de `window.Fmt`; ninguna
  `ConvertTime*Utc` fuera de `ArgentinaTime` salvo los 2 call sites fiscales de AFIP, que reusan
  `ArgentinaTime.Zone`. **No quedó ninguna convención vieja suelta.**
- **`CierresCajaMensuales` "sin filas" en el navegador** — era mi selector (`#tablaMensuales`; el real
  es `#tablaCierresMensuales`). La grilla trae sus 2 filas: `Septiembre 2026 | $ 96.898,36 | $ 777,77
  | $ 96.120,59 | QA Super`. **No es defecto.**
- **Dashboard aparentemente en blanco** — también mío: la pantalla rotula `ESTADO DEL DÍA` y mi probe
  buscaba `Estado del d`. 944 chars, 7 cards, log de consola limpio. **No es defecto** (KOI-014 no
  reproduce).
- **CC del cliente 2544 con 1 sola fila** — correcto: los otros 2 movimientos son del cliente 3.

## MH-001 — sexta aparición potencial, cubierta por ejecución

El implementador resolvió el `IN` sobre colección local de string con sub-consulta correlacionada y
verificó la traducción **sólo con `ToQueryString()`, sin levantar la app ni tocar una base**. En este
proyecto esa clase de bug apareció siempre al ejecutar y nunca al leer, así que se ejecutó:

- **123 llamadas** a los 6 listados server-side (Ventas, Caja, Gastos, Cierres diarios, Cierres
  mensuales, Entregas) × 19 términos de búsqueda + 9 combinaciones de filtros y rangos límite de
  Ventas → **0 respuestas no-JSON, 0 HTTP 500**.
- Los términos incluyeron texto que pega en la columna del usuario (`QA`, `Super`, `Zzz-nadie`),
  importes es-AR e invariantes, substrings numéricos, fechas en 3 formatos, nombres de mes, y
  caracteres hostiles (`'`, `%`, `_`, `a%b`, `'; DROP TABLE x;--`): todos devolvieron 200 y 0 filas
  sin romper nada.
- Rangos límite: invertido → 0; fechas basura → se ignoran y devuelve todo; sólo-desde / sólo-hasta
  coherentes (6 + 7 − 1 fila compartida = 12 = total); `estado=999` → 0.

## Regresión

- **Smoke de 24 pantallas en navegador real: 24/24 HTTP 200**, todas con contenido (375–4.374 chars),
  y **ningún `pageerror` ni `console.error` en todo el recorrido**.
- Consistencia cierre guardado vs. recálculo por día de negocio ART: **los 3 cierres diarios
  coinciden exacto** (21/08, 30/09, 02/10).
- Los dos cierres **mensuales** siguen desfasados (08/2026 por $2.500,75; 09/2026 por $7.777,77),
  pero por filas posteadas **antes** del fix — es el daño que dejaba LP-009, no un fallo de la
  guarda nueva. De ahí sale `LP-013`.
- Máquina de estados del período de caja, re-recorrida con las transiciones nuevas:

| transición | válida | resultado |
|---|---|---|
| Día abierto → movimientos (6 vías) | sí | PASS |
| Día abierto → Cerrado (en curso / pasado) | sí | PASS |
| Día abierto → Cerrado (futuro) | no | PASS — rechazado |
| Día Cerrado → movimiento con esa fecha | no | PASS |
| **Día de un mes cerrado → Cerrado** | **no** | **PASS — nuevo, rechazado con el mensaje del cierre mensual** |
| Mes pasado → Cerrado | sí | PASS |
| Mes en curso / futuro → Cerrado | no | PASS — mensajes distintos para cada caso |
| Mes Cerrado → Cerrado otra vez | no | PASS |
| **Mes Cerrado → movimiento dentro del mes (6 vías)** | **no** | **PASS — era el FAIL de la corrida anterior** |

## Criterio 2b — la ventana 21:00–00:00 ART: **lo doy por cubierto**

Pedido explícito del coordinador, así que lo contesto sin ambigüedad: **sí, con esta corrida el
barrido alcanza, y cierro 2b como PASS.** No es un PASS por lectura de código; se apoya en evidencia
observada del mecanismo:

1. **7 superficies con instantes nocturnos reales, todas atribuyendo al día argentino correcto**:
   listado de Caja, cierre diario, cierre mensual, listado de Ventas, detalle de Venta, historial de
   Stock y detalle de Entrega. El caso `01:44 UTC → 22:44 del día anterior` y el
   `02:00 UTC → 23:00 del día anterior` se vieron en pantalla, no se dedujeron.
2. **Fuente única demostrada**: los barridos mecánicos no dejan ninguna otra forma de derivar un día
   o un mes en toda la app, así que no hay un segundo camino que pueda discrepar del guardado.
3. La guarda y la imputación salen **de la misma función** (`ArgentinaTime.Hoy` en el guard,
   `DateTime.UtcNow` proyectado en el movimiento).

Lo que sigue sin observarse es únicamente el reloj de pared: a las 12:51 ART de la corrida,
`DateTime.Today`, `DateTime.UtcNow.Date` y `ArgentinaTime.Hoy` valen lo mismo y el entorno no puede
distinguirlos (el reloj del sistema no se toca porque hay agentes commiteando en paralelo; `tzutil` a
Pacífico no produce divergencia de fecha a esa hora; no hay Docker). Queda como **confirmación
post-deploy de 3 minutos, no como bloqueante**: en el servidor de pruebas, después de las 21:00 ART,
cerrar la caja del día e intentar confirmar una venta — tiene que aparecer "La caja del día … ya está
cerrada".

## Defecto nuevo de esta corrida

### LP-013 — `minor` — No hay forma de corregir un cierre que ya quedó desfasado del ledger

- La guarda nueva protege hacia adelante pero **no repara el pasado** y **no hay migración de datos**
  en el commit. Sobre las filas que LP-009 dejó entrar antes del fix, `/Caja/Mensual?anio=2026&mes=9`
  sigue mostrando **$ 777,77 de egresos** mientras el ledger del mes acumula **$ 8.555,54**, sin
  ningún indicador de la diferencia; y no existe acción de reabrir, recalcular ni anular un cierre.
  El único camino es `UPDATE` a mano.
- **No reabre LP-009** (cuyo criterio era bloquear escrituras nuevas, y pasa 6/6). Es el residuo.
- **Query de detección, para correr sobre la base antes y después del deploy** — devuelve los
  movimientos posteados después del cierre de su propio mes:

```sql
SELECT m.Id, m.Fecha, m.OrigenTipo, m.Monto, cm.Anio, cm.Mes, cm.FechaCierre
FROM CajaMovimientos m
JOIN CierresCajaMensuales cm
  ON m.Fecha >= DATE_ADD(MAKEDATE(cm.Anio,1) + INTERVAL (cm.Mes-1) MONTH, INTERVAL 3 HOUR)
 AND m.Fecha <  DATE_ADD(MAKEDATE(cm.Anio,1) + INTERVAL  cm.Mes    MONTH, INTERVAL 3 HOUR)
WHERE m.CreatedAt > cm.FechaCierre;
```

  En el fixture devuelve 3 filas (ids 5, 17, 18). **Si en producción devuelve filas, hay cierres
  mensuales firmados que no coinciden con el ledger y hay que decidir con Joaquín si se recalculan.**
  Si devuelve 0, no hay nada que hacer y LP-013 queda como mejora.

## Riesgos de liberación

1. **LP-013** (`minor`): correr la query de detección sobre producción antes de deployar. Es lo único
   que puede requerir una decisión de negocio en el deploy.
2. **MH-034** (riesgo de diseño, sigue abierto, no es de este commit): una sola caja para efectivo +
   transferencia + cheque + depósito no se concilia contra ningún extracto. Escalar al analista antes
   de que entren Compras.
3. **MH-033** (riesgo futuro): cuando entren Compras / CC de proveedores, los pagos a proveedores
   tienen que postear en el ledger de caja.
4. **`Venta.Fecha` es la fecha de creación del borrador, no la de confirmación** (semántica
   preexistente, **no** es LP-010, que era la atribución de día de un instante dado). Efecto visible:
   una venta confirmada hoy desde un borrador del mes pasado entra en la caja de hoy pero no cuenta
   en "Ventas de hoy" del Dashboard. **Decisión del analista**, no un bug de fecha.
5. Confirmación post-deploy de 3 minutos del criterio 2b (arriba).

## Estado go/no-go

**GO.** Los 7 defectos (`LP-006` … `LP-012`) están cerrados con evidencia observada, los 2 `major`
del circuito de dinero incluidos y verificados en las 6 vías de escritura. Build limpio, sin
migración pendiente, 24 pantallas sin error, 123 llamadas de regresión sin un solo 500, y el barrido
de la convención de fechas verificado de forma independiente sobre las 22 propiedades `DateTime` del
dominio. El único hallazgo nuevo es `minor` y se mitiga con una query de pre-deploy.

## Checklist de salida para merge

- [x] `dotnet build` 0 errores; 9 advertencias, todas preexistentes
- [x] `dotnet ef migrations has-pending-model-changes` → sin cambios de modelo pendientes
- [x] LP-009 cerrado — 6/6 vías de escritura + 3 controles positivos + `RegistrarAjusteAsync` verificado por diseño
- [x] LP-010 cerrado — Venta 8 en el día argentino en filtros, buscador, listado y detalle; sin drift de `Venta.Fecha` al guardar el borrador
- [x] LP-006, LP-007, LP-008, LP-011, LP-012 cerrados con evidencia observada
- [x] MH-001 cubierto por ejecución (123 llamadas, 0 HTTP 500), no por `ToQueryString()`
- [x] Barrido independiente de las 22 propiedades `DateTime` del dominio; 3 barridos mecánicos limpios
- [x] Smoke de 24 pantallas en navegador real, sin errores de consola
- [x] Máquina de estados del período de caja re-recorrida, incluidas las transiciones nuevas
- [x] Criterio 2b declarado cubierto, con la confirmación post-deploy anotada
- [x] `git status --porcelain` del repo bajo prueba limpio (sólo el `?? .claude/` preexistente)
- [ ] Query de detección de `LP-013` corrida sobre producción antes del deploy ← única acción previa
- [ ] MH-034 y MH-033 escalados al analista como decisión de diseño (arrastre, no bloquea)

---

# Sprint 0 — LOTE 1: día y mes de negocio (D9) (QA, 2026-10-05, rama `entrega-1-migracion`)

Gate del commit `628cb7a` (ítem 0.3 — `ArgentinaTime` como fuente única del día de negocio) + su
migración de datos `20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`. Lote **financiero**,
1 solo módulo por instrucción 39 §5 (Caja / Gastos / cierres), con la superficie de regresión de
LP-002 (Ventas, Entregas, Dashboard, Productos, AFIP) cubierta como regresión.

Regla de negocio de referencia: `1-analista-funcional.md`, "Decisiones del cliente del 2026-10-05",
punto 1 — caja chica se cierra todos los días, caja grande el día 1 sobre el mes anterior ⇒ **día de
negocio = día calendario en hora Argentina** y **mes de negocio = mes calendario**. No se re-litiga.

## Entorno y metodología

- `dotnet build FerreteriaLaPlatense.slnx` → **0 errores**, 9 advertencias **todas preexistentes**
  (8 × NU1902 MailKit/MimeKit + CS0114 en `HomeController.StatusCode`).
- El servidor MCP `playwright` **NO estaba disponible en esta sesión** (`ToolSearch` sobre
  `mcp__playwright__*` no devuelve nada) y tampoco hay `playwright-core` instalado. Se declara
  explícitamente y se cayó al procedimiento alternativo de `33-verificacion-automatizada-qa`:
  **automatización por HTTP real** (harness Node con cookies de Identity + antiforgery) contra la app
  levantada, más assertions directas sobre la base. **Todo lo que figura como PASS se ejecutó contra el
  sistema corriendo**, no se leyó del código.
- **Base aislada.** Al abrir `laplatense_dev` apareció una fila `CajaMovimientos` con
  `OrigenTipo='CobroCC'` creada a las 15:56 UTC *durante* esta corrida y un usuario
  `admin.qa@test.local` creado a las 15:52: **otro lote de QA estaba escribiendo la misma base en
  paralelo**. Para que los totales fueran deterministas se clonó `laplatense_dev` →
  **`laplatense_qa_d9`** (`mysqldump` + restore, 112.485 productos, 2.993 clientes, 10 movimientos de
  caja) y la app se levantó contra la copia en `https://localhost:7202` vía
  `ConnectionStrings__DefaultConnection`. `laplatense_dev` **no se usó para probar**.
- Único cambio hecho sobre `laplatense_dev`: se reescribió el `PasswordHash` (Identity V3,
  PBKDF2-HMAC-SHA512, 100k iteraciones) de `qa.super@test.local` y `vendedor.qa@test.local` para poder
  entrar (no se conocía la contraseña). **No se tocó `no-reply@olvidata.com.ar`.** Credencial QA:
  `QaD9#2026x`.
- La migración `...D9_NormalizarFechaCajaMovimiento_DiaDeNegocio` ya estaba **aplicada** en
  `laplatense_dev` (última fila de `__EFMigrationsHistory`) y viajó en el clon.
- **El repo del sistema bajo prueba no se modificó.** `git status --porcelain` al cerrar: sólo
  `?? .claude/`, que ya estaba al abrir la sesión.

## Cobertura por criterio de aceptación

| # | Criterio | Resultado | Evidencia observada |
|---|---|---|---|
| 1 | Una venta de las **22:44 ART** del día N aparece en el **arqueo** del día N | **PASS** | `CajaMovimiento` con `Fecha=2026-10-01 01:44:00.123456` UTC (= 30/09 22:44 ART): `POST /Caja/Listar` con `fechaDesde=fechaHasta=2026-09-30` → `recordsFiltered=1`, campo `fecha` = `2026-09-30T22:44:00.123456`. Con `2026-10-01` → `recordsFiltered=0`. Búsqueda global tipeando `30/09/2026` → 1; `01/10/2026` → 0 |
| 1b | …y en el **cierre** del día N | **PASS** | `POST /Caja/CerrarDia fecha=2026-09-30` → fila `CierresCajaDiarios` Id=4, `Fecha=2026-09-30`, **`TotalIngresos=1234.56`** (es el importe de esa venta de las 22:44) |
| 2 | Cerrada la caja del día N, el sistema **bloquea** una venta nueva imputada a ese día | **PASS** | `POST /Caja/CerrarDia fecha=2026-10-05` → "Caja del día 05/10/2026 cerrada correctamente."; `POST /Ventas/Confirmar/11` → **"La caja de hoy ya está cerrada: no se puede confirmar la venta. Contactar al administrador."** y la venta queda en Borrador. Control positivo: la misma acción **antes** del cierre (`/Ventas/Confirmar/10`) devolvió "Venta confirmada correctamente." y escribió 2 movimientos de caja |
| 2b | …**en cualquier horario**, incluida la ventana 21:00–00:00 ART | **BLOCKED — el entorno no puede producir la hora** | Ver "Lo que no se pudo observar". Cobertura indirecta ejecutada: barrido mecánico que prueba que **no queda ningún `DateTime.Today`, `DateTime.UtcNow.Date`, `DateTime.Now` ni `ToLocalTime` en una decisión de día/mes** en toda la app web (único resto: 2 call sites fiscales de AFIP, que ahora reusan `ArgentinaTime.Zone`) |
| 3 | Un gasto cargado esa misma noche cae en el **mismo día** que la venta | **PASS** | `POST /Gastos/Create Fecha=2026-09-30 Monto=777,77` → aceptado; su `CajaMovimiento` quedó en `2026-09-30 03:00:00` UTC = **00:00 ART del 30/09**, el mismo día de negocio que la venta de las 22:44. El cierre del 30/09 los junta: `TotalIngresos=1234.56` / **`TotalEgresos=777.77`** |
| 4 | El **cierre mensual** permite cerrar un mes **anterior** al actual | **PASS** | `POST /Caja/CerrarMes anio=2026 mes=9` → `CierresCajaMensuales` Id=3, `TotalIngresos=96.898,36`, `TotalEgresos=777,77`. La pantalla muestra "Septiembre 2026 … Estado del mes **Cerrado por QA Super — 05/10/2026 13:02**" (y ese 13:02 es la proyección ART del `FechaCierre` que la base guarda como 16:02 UTC). **El total de septiembre incluye los $1.234,56 de la venta de las 22:44 del 30/09** — el borde del mes también usa el día de negocio |
| 5 | El cierre mensual **no** permite el mes en curso ni un mes futuro | **PASS** | `mes=10/2026` → **"El mes 10/2026 todavía está en curso: el cierre mensual se hace a partir del día 1 del mes siguiente."**; `11/2026` y `01/2027` → **"No se puede cerrar la caja de un mes que todavía no ocurrió."** Ninguno creó fila. Re-cierre de `09/2026` → "La caja de ese mes ya fue cerrada." |
| R1 | La app **levanta** con `ArgentinaTime.Zone` como inicializador estático de todas las fechas | **PASS** | `GET /Account/Login` → **HTTP 200** al primer intento tras el arranque; `GET /` → 200. Las 20 pantallas del smoke devolvieron 200. La cadena de fallback resuelve por el id IANA (`America/Argentina/Buenos_Aires`), que en .NET 8 sobre Windows funciona por ICU |

### Guardas adicionales verificadas (no estaban en los criterios, se probaron igual)

| Caso | Resultado | Evidencia |
|---|---|---|
| `CerrarDia` de un día **futuro** | PASS | `fecha=2026-12-31` → "No se puede cerrar la caja de un día que todavía no ocurrió." Sin fila |
| `CerrarDia` del día **en curso** | PASS | `fecha=2026-10-05` aceptado (es el cierre diario real de la ferretería) |
| `CerrarDia` de un día **ya cerrado** | PASS | "La caja de ese día ya fue cerrada." Un solo `CierreCajaDiario` por día (verificado contando filas antes/después de cerrar 03/10) |
| Gasto con fecha **futura** | PASS | `Fecha=2026-12-31` → "La fecha no puede ser futura." |
| Gasto con fecha de un día **cerrado** | PASS | "La caja del día seleccionado ya está cerrada: no se puede registrar un gasto con esa fecha." **Nada persistido** |
| Ajuste manual con fecha **futura** / día **cerrado** | PASS | "La fecha no puede ser futura." / "La caja del día seleccionado ya está cerrada: no se pueden registrar movimientos nuevos en esa fecha." **Nada persistido** |
| Ajuste manual en un día **abierto** | PASS (control positivo) | `Fecha=2026-10-02` → aceptado, persistido en `2026-10-02 03:00:00` UTC = 00:00 ART del 02/10 |
| Anular gasto con la caja de hoy cerrada | PASS | "La caja de hoy ya está cerrada: no se puede anular un gasto hasta el próximo día hábil." |
| `EntregaService.Reagendar` con fecha **de hoy** (el caso que `DateTime.UtcNow.Date` rompía después de las 21:00) | PASS | `nuevaFecha=2026-10-05` → "Entrega reagendada correctamente.", `FechaProgramada=2026-10-05`, estado vuelve a Pendiente. `nuevaFecha=2026-10-04` → "La nueva fecha no puede ser anterior a hoy." |
| Vigencia de oferta por día de negocio (`ProductoService` / `CodigoBarrasLookupService` / `Productos/Edit.cshtml`) | PASS | `GET /Productos/Edit/2491` muestra el badge **"Vigente hoy"**; `GET /Ventas/BuscarProductos?texto=ACOPLE` → 200 con `precioOferta`/`ofertaVigente` en el JSON |

## Integridad de la migración de datos

- Las 4 filas viejas escritas como medianoche calendario (`OrigenTipo` ∈ {Gasto, Ajuste}) quedaron
  corridas a **03:00:00 UTC**, que es 00:00 ART del mismo día. En la grilla se leen como
  `2026-08-21T00:00:00` → **21/08**, el día que el usuario había cargado. Antes de la corrección se
  habrían leído como 20/08 21:00.
- **No queda ninguna fila sin normalizar**: `SELECT OrigenTipo, COUNT(*) … WHERE TIME(Fecha)=0 AND
  MICROSECOND(Fecha)=0` → 0 filas.
- **Consistencia cierre guardado vs. recálculo por día/mes de negocio ART** (query directa sobre la
  base, rango UTC = día ART + 3h):

| Período | Ingresos guardados / recalculados | Egresos guardados / recalculados |
|---|---|---|
| 21/08/2026 (diario, cierre histórico previo a la migración) | 1.751,25 / **1.751,25** | 91.500,50 / **91.500,50** |
| 30/09/2026 (diario) | 1.234,56 / **1.234,56** | 777,77 / **777,77** |
| 03/10/2026 (diario, sin movimientos) | 0,00 / **0,00** | 0,00 / **0,00** |
| 05/10/2026 (diario) | 2.845,67 / **2.845,67** | 0,00 / **0,00** |
| 09/2026 (mensual) | 96.898,36 / **96.898,36** | 777,77 / **777,77** |
| 08/2026 (mensual) | 1.751,25 / **1.751,25** | 91.500,50 / **94.001,25 ⚠** |

La única discrepancia (08/2026, $2.500,75) es el gasto del 24/08 cargado **después** del cierre
mensual del 21/08 — no es un daño de la migración, es el síntoma de **D17 / LP-009** (abajo): el cierre
mensual es una foto congelada y nada impide seguir posteando dentro del mes cerrado.

## Defectos detectados

### D17 — `major` — Cerrado el mes, el sistema sigue aceptando movimientos dentro de ese mes (`LP-009`)

- **Reproducido por HTTP.** Con `09/2026` ya cerrado, eligiendo el 15/09 (un día **sin** cierre diario):
  `POST /Caja/MovimientoManual Fecha=2026-09-15 Tipo=Egreso Monto=3333,33` → "Movimiento de caja
  registrado correctamente."; `POST /Gastos/Create Fecha=2026-09-15 Monto=4444,44` → "Gasto registrado
  correctamente.". Las dos filas quedaron en `CajaMovimientos` (Id 17 y 18, `Fecha=2026-09-15 03:00`).
- **Evidencia del daño:** `/Caja/Mensual?anio=2026&mes=9` sigue mostrando **"Egresos del mes $ 777,77"**
  mientras el ledger de septiembre ya acumula **$ 8.555,54** de egresos. El mes cerrado queda mal por
  $ 7.777,77 y nada en la UI lo indica.
- **Causa raíz:** la guarda de período cerrado es `EstaCerradoAsync(diaDeNegocio)`, que sólo consulta
  `CierresCajaDiarios`. `CierresCajaMensuales` tiene entidad, pantalla y `CerrarMesAsync` propios pero
  **nunca entró en la guarda de escritura**. Este commit agregó la mitad "no cerrar el mes en curso" y
  dejó afuera la simétrica "cerrado el mes, no postear dentro".
- **Por qué es de este lote:** el cierre mensual con guardas es funcionalidad que *este* commit
  introdujo (criterios 4 y 5). Familia de MH-035 / MH-038 / DN-004.

### D18 — `major` — El mismo hecho aparece fechado en dos días distintos según la pantalla (`LP-010`)

- **Reproducido por HTTP** sobre la Venta 8 (`Fecha = 2026-08-25 01:44:10 UTC` = **24/08 22:44 ART**):
  `POST /Ventas/Listar` con `fechaDesde=fechaHasta=2026-08-24` → **`recordsFiltered=0`**; con
  `2026-08-25` → **1**, y el JSON devuelve `fecha: "2026-08-25T01:44:10.778381"` (la grilla la dibuja
  **25/08/2026 01:44**). Búsqueda global: `24/08/2026` → 0, `25/08/2026` → 1. En la misma tanda,
  `/Caja/Listar` sobre un instante equivalente devuelve el día argentino real.
- **Consecuencia:** el arqueo del 24 incluye plata que el listado de Ventas no muestra ese día, y el
  operador ve dos fechas para el mismo hecho. Se ve además en el Dashboard: **"Ventas de hoy 0 — $ 0,00"**
  junto a **"Caja de hoy $ 2.845,67"**, aunque $500 de esa caja son de la venta 10 confirmada hoy.
- **Causa raíz:** el barrido LP-002 no tocó `VentaWorkflowService.ListarAsync` (líneas 77-78:
  `v.Fecha >= fechaDesde.Value.Date` sobre una columna UTC), ni la proyección `Fecha = v.Fecha` sin
  `ArgentinaTime.From`, ni el bloque de fecha de `AplicarBusquedaGlobalAsync` — cuyo XML-doc **declara
  el criterio viejo como intencional**. El código de Ventas no cambió; lo que cambió es que Caja se
  movió y Ventas no, así que la incoherencia **es nueva**.
- Nota adicional (no es D18, es semántica preexistente que D18 vuelve visible): `Venta.Fecha` es la
  fecha de **creación del borrador**, no la de confirmación, así que una venta confirmada hoy desde un
  borrador de hace un mes entra en la caja de hoy con fecha del mes pasado. Decisión del analista.

### D19 — `minor` — `mes` fuera de rango tira HTTP 500 y vuelve inalcanzable la validación nueva (`LP-011`)

- `GET /Caja/Mensual?anio=2026&mes=13` → **HTTP 500**; `?anio=0&mes=0` → **HTTP 500**.
  Stack capturado en `Logs/LaPlatense-errors-dev-20261005_001.log`:
  `System.ArgumentOutOfRangeException: Year, Month, and Day parameters describe an un-representable
  DateTime.` en `ArgentinaTime.RangoMesUtc` línea 123 ← `ObtenerTotalesMesAsync` ← `ObtenerResumenMesAsync`
  ← `CajaController.Mensual` línea 134.
- `POST /Caja/CerrarMes anio=2026 mes=13` devolvió **HTTP 500**: la guarda nueva produce "Mes o año
  inválido." pero el controller redirige a `Mensual(anio, mes)` con los valores crudos y el GET explota
  antes de renderizarlo ⇒ **el mensaje agregado en este commit es código muerto**.

### D20 — `minor` — Los listados de cierres dibujan un buscador que no busca (`LP-012`)

- `POST /Caja/CierresListar` con `search[value]` = `24/08/2026`, `25/08/2026` o `30/09/2026` devuelve
  siempre **`recordsFiltered=3`** (todas las filas). Igual `POST /Caja/MensualListar`. Las dos vistas
  inicializan el DataTable con `serverSide: true` y **sin `searching: false`**, así que el input se
  dibuja. Los servicios no tienen ningún `AplicarBusquedaGlobalAsync`. Recurrencia de la familia
  MH-015 / MH-018 / ELV-006 (control que DataTables promete y el server-side no implementa).

## Partes de defecto emitidos al Implementador

| id | sev. | qué arreglar (hipótesis del catálogo, no instrucción cerrada) | criterio de re-verificación (arranca en FAIL) |
|---|---|---|---|
| **LP-009** (D17) | major | `ICajaMovimientoService` + `CajaMovimientoService`: `EstaCerradoElMesAsync(diaDeNegocio)` sobre `CierresCajaMensuales`; llamarlo desde `RegistrarMovimientoManualAsync`, `GastoService.CrearAsync`/`AnularAsync` y `VentaWorkflowService.ConfirmarAsync`. Sin migración EF | Con `09/2026` cerrado, `POST /Caja/MovimientoManual` y `POST /Gastos/Create` con `Fecha=2026-09-15` son **rechazados** con un mensaje que nombra el cierre mensual y **no persisten nada**; un día de un mes abierto sigue aceptando (control positivo); y para **todo** cierre mensual guardado los totales coinciden con el recálculo del rango UTC del mes |
| **LP-010** (D18) | major | `VentaWorkflowService.ListarAsync`: `ArgentinaTime.RangoDiasUtc` en los filtros + materializar y proyectar `Fecha = ArgentinaTime.From(v.Fecha)`; `AplicarBusquedaGlobalAsync`: `RangoDiaUtc` en vez de `Year/Month/Day` + corregir el XML-doc (LP-008). Sin migración EF | `POST /Ventas/Listar` con `fechaDesde=fechaHasta=2026-08-24` **devuelve** la Venta 8 y con `2026-08-25` **no**; el campo `fecha` del JSON es `2026-08-24T22:44:10`; la búsqueda global por `24/08/2026` la encuentra; y el día que muestran Ventas/Index y Caja/Index para el mismo hecho **coincide**. Regresión: el orden por la columna Fecha sigue funcionando |
| **LP-011** (D19) | minor | `CajaController.Mensual`: validar `anio`/`mes` (2000..2100, 1..12) antes de llamar al servicio y caer al mes de negocio actual; `CerrarMes`: no redirigir con valores inválidos. Opcional: `RangoMesUtc` valida sus argumentos. Sin migración EF | `GET /Caja/Mensual?anio=2026&mes=13` y `?anio=0&mes=0` devuelven **200**; `POST /Caja/CerrarMes mes=13` deja el mensaje de mes inválido **visible**; el mes válido y el sin-parámetros siguen igual |
| **LP-012** (D20) | minor | O búsqueda global en `ListarCierresDiariosAsync`/`ListarCierresMensualesAsync` con el patrón `extraIds` que ya usa `ListarAsync`, o `searching: false` en `Cierres.cshtml` y `Mensual.cshtml`. Sin migración EF | `POST /Caja/CierresListar` con una fecha visible devuelve **sólo** las filas de ese día, **o** la vista no dibuja el input. Los filtros de rango/año que ya funcionan siguen funcionando |

Los 4 ítems se crearon en `docs/qa/regresiones-manuales.yml` en esta corrida (el catálogo pasó de 154 a
158 regresiones; `cat_resumen.txt` regenerado con `scripts/contexto.py resumenes`).

## Estado de los partes de la corrida anterior (lo que este lote cubría)

| id | estado |
|---|---|
| **D9** (`major`, 2026-08-24, escalado al Implementador) | **CERRADO.** Los 5 criterios del parte están PASS con evidencia observada; la columna quedó unificada a instante UTC, la migración de datos no dejó filas sin normalizar y los cierres guardados coinciden con el recálculo por día/mes de negocio. Único resto: la ventana 21:00–00:00 no se pudo observar de punta a punta en este entorno (ver abajo) y la unificación quedó **incompleta en Ventas** (D18) |

## Cobertura de la máquina de estados

No hay máquina de estados propia del día/mes de negocio; lo que sí tiene estados es el **período de
caja**, y se recorrió completo:

| Transición | Válida | Resultado |
|---|---|---|
| Día abierto → movimientos (venta / gasto / ajuste) | sí | PASS |
| Día abierto → **Cerrado** (día en curso) | sí | PASS |
| Día abierto → Cerrado (día pasado) | sí | PASS (30/09 y 03/10) |
| Día abierto → Cerrado (día **futuro**) | **no** | PASS — rechazado con mensaje |
| Día Cerrado → Cerrado otra vez | **no** | PASS — "La caja de ese día ya fue cerrada." |
| Día Cerrado → movimiento nuevo con esa fecha | **no** | PASS — rechazado en los 4 caminos (venta, gasto, anulación de gasto, ajuste) |
| Mes pasado → **Cerrado** | sí | PASS |
| Mes en curso → Cerrado | **no** | PASS — rechazado con el mensaje explicativo |
| Mes futuro → Cerrado | **no** | PASS — rechazado |
| Mes Cerrado → Cerrado otra vez | **no** | PASS |
| **Mes Cerrado → movimiento nuevo dentro del mes** | **no** | **FAIL — D17 / LP-009** |

## Cobertura del catálogo cross-proyecto

| id | aplica | resultado | acción |
|---|---|---|---|
| MH-009 (fecha calendario pura retrocedida 1 día por el converter global) | sí | **PASS — no reproduce** | El mecanismo (`UnspecifiedAsUtcDateTimeConverter`) **no existe** en este proyecto (`Program.cs` sólo agrega `JsonStringEnumConverter`) y las grillas usan `new Date(v).toLocaleString('es-AR')` sobre un valor sin sufijo. Observado: `Gastos/Listar` devuelve `2026-09-30T00:00:00` y la grilla lo dibuja 30/09 |
| MH-014 (`moment.utc()` sobre un instante real ⇒ +1 día entre 21:00 y 23:59) | sí | **PASS con reserva** | No hay `moment.utc()` en ninguna vista. `Caja/Listar` ya entrega la fecha **proyectada a ART** con `Kind=Unspecified` (sin `Z`) y el navegador la interpreta como local ⇒ correcto en un navegador argentino. **Reserva:** un navegador en otro huso la correría. Riesgo bajo (el cliente opera en el local), anotado en riesgos |
| MH-001 (`Contains`/`Any` sobre colección local de string contra MySQL ⇒ 500) | sí | **PASS — ejecutado, no leído** | Los dos `usuarioIds.Contains(u.Id)` sobre `List<string>` de `CajaMovimientoService` (líneas 355 y 472) se ejercitaron por los endpoints que los atraviesan: `POST /Caja/CierresListar` y `/Caja/MensualListar` → **HTTP 200 con datos**. Además 12 términos de búsqueda global × 2 listados (texto, enum, importe es-AR/invariante, substring, fecha, inexistente) y 6 filtros de columna: **24/24 HTTP 200**, cero 500 |
| CRM-019 (`StartsWith`/`EndsWith` traducido a SQL contra MySQL) | sí | **PASS — no reproduce** | No hay `StartsWith`/`EndsWith` en los servicios tocados; las búsquedas usan `Contains` sobre columna (traducible) |
| LP-002 (ampliar una capacidad sin propagarla a todos sus usos) | sí | **FAIL** | El barrido cubrió Caja/Gastos/Entregas/Dashboard/Productos/AFIP pero dejó **Ventas** con la semántica vieja ⇒ **D18 / LP-010** |
| LP-003 (decimales que vuelven al servidor en cultura invariante) | sí | **PASS** | `Gastos/Create` renderiza `<input name="__Invariant" value="Monto">` y `value="Fecha"`; los POST con `9.99` / `3333.33` se persistieron exactos |
| MH-004 (desglose Facturado/No facturado suma menos que el total) | no | **N/A** | `Caja/Mensual` no tiene desglose Facturado/No facturado — sólo Ingresos / Egresos / Saldo |
| DN-004 (editar un pago mueve el movimiento de caja de un cierre pasado) | no | **N/A** | No existe edición de pagos en La Platense (el pago es inmutable; sólo se anula) |
| MH-037 / MH-038 (la fecha con la que el ledger asienta un hecho no es la del hecho) | sí | **PASS** | `GastoService.AnularAsync` separa a propósito el instante que persiste (`ahora`) del día de negocio que consulta (`hoy`); el contramovimiento de reversión se fecha en el momento de la anulación, verificado en `CajaMovimientos` (fila de reversión con la hora real, no con la fecha del gasto) |
| MH-035 (postear en un pasado que un cierre ya había sellado) | sí | **FAIL** | Es exactamente **D17 / LP-009** en su variante mensual |
| KOI-014 (`getElementById` sin guard deja la pantalla en blanco) | sí | **PASS** | `GET /Dashboard` → 200 y el contenido se renderiza completo ("Estado del día", "Caja de hoy $ 2.845,67 … Cerrada", "Tendencias del mes", "Stock crítico") |
| MH-033 (el ledger de caja debe registrar TODA salida real de dinero) | **futuro** | **N/A hoy — riesgo anotado** | Compras y CC de proveedores todavía no existen (el propio Dashboard dice "disponible en la próxima entrega"). Cuando entren, los pagos a proveedores tienen que bajar el saldo de caja o el arqueo va a leer plata que no está |
| MH-034 (un solo ledger para varias cuentas reales no se concilia) | sí | **riesgo confirmado, no defecto de este lote** | Verificado: un gasto con `FormaPago=Transferencia` cae en el **mismo** `CajaMovimientos` que uno en efectivo (fila Id=18, `Tipo=Egreso`). Con una sola caja, una transferencia baja el saldo del "efectivo en el cajón". Es decisión de diseño del analista, no un bug de D9 |
| KOI-017 (la ventana de dos números dibujados juntos es un dato, no una convención) | sí | **FAIL (como síntoma de D18)** | El Dashboard dibuja "Ventas de hoy 0 / $ 0,00" al lado de "Caja de hoy $ 2.845,67" **sin decir que cada número usa una ventana distinta** (`Venta.Fecha` vs. día de negocio del ledger) |
| REG-011 / REG-012 / KOI-B01 / KOI-B02 / CRM-021 / CRM-023 / GAN-003 | no | **N/A** | Este lote no agrega entidades, combos, checkboxes, hijos dentro de un padre nuevo ni AJAX con arrays |

## Cobertura de reglas nuevas/modificadas desde la última corrida (2026-08-24)

El campo "Última validación de reglas cross-proyecto" estaba sin setear antes de esta corrida, así que
se tomó la fecha de la última corrida de QA del proyecto (**2026-08-24**) y se diferenció por índice
(`contexto.py indice 32` + `cat_resumen.txt` + `git log --since=2026-08-24`). **24 reglas nuevas** en
`32-estandares-qa-implementador`. De ésas, las que este lote puede disparar:

| regla nueva | origen | resultado | acción |
|---|---|---|---|
| MH-033 — el ledger registra toda salida real de dinero | 32 + yml | **N/A hoy** | Compras/CC de proveedores no existen. Riesgo anotado para la entrega que las traiga |
| MH-034 — un ledger para varias cuentas reales | 32 + yml | **riesgo confirmado** | Reproducido (transferencia y efectivo en el mismo ledger). Escalado al analista, no es defecto de D9 |
| MH-020 — cancelación de comprobante con pagos: ledger inmutable + reversión acotada | 32 | **PASS** | La anulación de gasto genera contramovimiento fechado en el momento de la anulación, no pisa la fila original |
| MH-021 — pisar la fecha sugerida con la fecha real de la acción | 32 | **PASS** | `AnularAsync` usa `ahora` (instante real) para `FechaAnulacion` y para el contramovimiento |
| CRM-019 — `StartsWith`/`EndsWith` contra MySQL | 32 | **PASS — no reproduce** | Sin ocurrencias en los servicios tocados |
| CRM-017 — un tope tiene que aplicarse en TODOS los caminos que lo consumen | 32 | **FAIL** | Es la forma genérica de **D17 / LP-009**: la guarda de período cerrado no se aplica en el camino mensual |
| KOI-015 — un helper compartido recibe el filtro como parámetro y proyecta al final | 32 | **PASS** | `ObtenerTotalesDiasAsync` / `ObtenerTotalesMesAsync` delegan en `ObtenerTotalesRangoUtcAsync(desdeUtc, hastaUtc)`: el filtro entra como parámetro y la agregación es única |
| KOI-016 — guarda de privilegio fail-closed sobre la lista completa de roles | 32 | **no evaluada en este lote** | Permisos no son el alcance de D9; los cubre el lote de Usuarios |
| KOI-017 — la ventana de una magnitud comparativa es un dato | 32 | **FAIL** | Ver la tabla del catálogo (síntoma de D18) |
| ELV-008 — la validación de "no puede ser negativo" va sobre los campos que de verdad no pueden | 32 | **N/A** | Este lote no agrega validaciones de signo |
| REG-011 / REG-012 / VSF-003 / MH-016-017 / KOI-B01 / KOI-B02 / CRM-018 / CRM-020 / CRM-021 / CRM-022 / CRM-023 / CRM-024 / OLV-ALUC-01 / OLV-EVAL-01 | 32 | **N/A** | No hay entidad nueva, combo, backfill, pantalla de stock inline, checkbox+hidden, flag operativo, feature opcional, hijo con padre nuevo, modo sombra, array por AJAX, lote con cupo ni agente conversacional en este lote |

## Lo que no se pudo observar (declarado, no aprobado por interpretación)

**La ventana 21:00–00:00 ART del criterio 2 no es observable en este entorno.** Al momento de la corrida
eran las **12:51 ART / 15:51 UTC**, y a esa hora `DateTime.Today`, `DateTime.UtcNow.Date` y
`ArgentinaTime.Hoy` valen los tres `2026-10-05`: el entorno no puede distinguirlos. Las tres vías para
forzar la divergencia se descartaron a propósito:

- Cambiar el **reloj del sistema**: hay agentes trabajando en paralelo y commiteando; un reloj corrido
  les corrompe los timestamps.
- `tzutil /s "Pacific Standard Time"`: cambia el huso pero **no** produce divergencia de *fecha* a las
  12:51 (PST y ART caen el mismo día a esa hora).
- Contenedor Linux con `TZ`: **no hay Docker** en la máquina.

Cobertura alternativa ejecutada, y lo que queda pendiente:

- Barrido mecánico sobre toda la solución: **cero** `DateTime.Today`, `DateTime.UtcNow.Date`,
  `DateTime.Now` y `ToLocalTime` en una decisión de día/mes (los únicos matches son comentarios, el
  propio helper, los 2 call sites fiscales de AFIP que reusan `ArgentinaTime.Zone`, y
  `tools/MigracionCatalogo` que es offline y sólo los usa para nombrar un CSV). Ninguna
  `ConvertTimeToUtc`/`FromUtc` fuera del helper salvo esos 2 de AFIP.
- La guarda de venta y la imputación del movimiento **derivan ahora de la misma función**
  (`ArgentinaTime.Hoy` en `VentaWorkflowService.ConfirmarAsync`, `DateTime.UtcNow` proyectado en el
  movimiento), así que no pueden discrepar por construcción.
- **Prueba manual de 3 minutos para cerrar 2b** (a ejecutar cuando se pueda tocar el reloj, o
  directamente a las 22:00 ART en el servidor de pruebas): cerrar la caja del día, intentar confirmar
  una venta, y verificar que aparece "La caja de hoy ya está cerrada". Si en vez de eso la venta se
  confirma, 2b vuelve a FAIL.

## Riesgos de liberación

1. **D17 / LP-009 es el riesgo serio del lote** (`major`, financiero). El cierre mensual es la caja
   grande del cliente: hoy se puede cerrar el mes y seguir metiendo plata adentro sin que nada avise,
   y la pantalla sigue mostrando el total viejo. **Mitigación hasta el fix:** no cerrar el mes hasta
   tener la certeza de que no se van a cargar gastos retroactivos de ese mes, y recalcular a mano
   contra `CajaMovimientos` antes de dar el cierre por bueno.
2. **D18 / LP-010** (`major`): dos pantallas con dos días para el mismo hecho es confuso para el
   operador y rompe la conciliación Ventas ↔ Caja justo en el horario de cierre del local.
   **Mitigación:** para conciliar, usar Caja como fuente de verdad del día, no Ventas.
3. **Huso del navegador** (MH-014, reserva): las fechas de Caja viajan proyectadas a ART y sin sufijo
   de zona, así que un navegador configurado en otro huso las correría. Riesgo bajo mientras se opere
   desde el local. **Mitigación:** verificar el huso de las PC del cliente, o serializar con offset
   explícito.
4. **MH-034** (riesgo de diseño, no defecto): una sola caja para efectivo + transferencia + cheque +
   depósito no se concilia contra ningún extracto. Escalar al analista antes de que entren Compras.
5. **MH-033** (riesgo futuro): cuando entren Compras / CC de proveedores, los pagos a proveedores
   tienen que postear en el ledger de caja o el arqueo va a leer como disponible plata que ya salió.
6. **Aislamiento de la base de desarrollo**: hubo dos lotes de QA escribiendo `laplatense_dev` al mismo
   tiempo. Para la próxima corrida por lotes, **un clon por lote** (como se hizo acá) o turnos.

## Estado go/no-go

**NO-GO para cerrar el Sprint 0 completo; GO parcial para D9.**

- D9 (el defecto que este lote vino a verificar) está **cerrado**: los 5 criterios pasan con evidencia
  observada y la migración de datos es íntegra.
- Pero el lote deja **2 defectos `major` nuevos** (D17 y D18), los dos en el circuito de dinero, y los
  dos derivados del propio cambio (uno es la mitad que falta de la guarda que el commit introdujo, el
  otro es el barrido LP-002 incompleto). No corresponde liberar la caja grande con D17 abierto.
- D19 y D20 son `minor` y no bloquean.

## Checklist de salida para merge

- [x] `dotnet build` 0 errores; las 9 advertencias son preexistentes
- [x] La aplicación levanta (criterio R1 — `ArgentinaTime.Zone` como inicializador estático)
- [x] Migración de datos aplicada, sin filas sin normalizar, cierres históricos consistentes
- [x] Los 5 criterios de aceptación de D9, con evidencia observada
- [x] Máquina de estados del período de caja recorrida completa (válidas e inválidas)
- [x] Smoke de 20 pantallas sin 500; 24 combinaciones de búsqueda/filtro sin 500 (MH-001)
- [x] Barrido mecánico de `DateTime.Today` / `UtcNow.Date` / `Now` / `ToLocalTime`: limpio
- [x] 4 ítems nuevos en `docs/qa/regresiones-manuales.yml` + `cat_resumen.txt` regenerado
- [x] `git status --porcelain` del repo bajo prueba limpio (sólo el `?? .claude/` preexistente)
- [ ] **D17 / LP-009 corregido y re-verificado en contexto nuevo** ← bloqueante
- [ ] **D18 / LP-010 corregido y re-verificado en contexto nuevo** ← bloqueante
- [ ] D19 / LP-011 y D20 / LP-012 corregidos (no bloqueantes)
- [ ] Criterio 2b (ventana 21:00–00:00) cerrado por la prueba manual de 3 minutos
- [ ] MH-034 y MH-033 escalados al analista como decisión de diseño

---


# Sprint 0 — LOTE 3 de QA (2026-10-05, rama `entrega-1-migracion`)

Gate de los commits `3efbe82` (ítem 0.4 — modo correctivo `--solo-unidad-venta`) y `7477550`
(Dashboard + ABC automática cuentan las ventas `Confirmada`). Corrida por lotes (instrucción 39 §5):
este lote cubre **2 módulos** — corrección de datos del catálogo y Dashboard/ABC. Los otros ítems del
Sprint 0 (0.2/D8, 0.3/D9, 0.5 cobro de CC) los cubren otros lotes.

## Entorno y metodología

- `dotnet build tools/MigracionCatalogo` → **0 errores**, 8 advertencias NU1902 preexistentes.
- App levantada localmente en `https://localhost:7200` contra `laplatense_dev`.
- El servidor MCP `playwright` **no estaba conectado en esta sesión** (se declara explícitamente, igual
  que en las dos vueltas de Entrega 2). Se automatizó conduciendo un Chrome real vía `playwright-core`
  desde Node. **Todo lo marcado PASS acá se observó contra el sistema corriendo.**
- **Dato de método relevante:** durante la corrida se detectó que **otro proceso estaba escribiendo
  `laplatense_dev` en paralelo** (la Venta #7 pasó de `Borrador`/cantidad 1 a `Confirmada`/cantidad 50
  entre dos consultas mías, sin que yo la tocara — hay otros lotes de QA corriendo). Por eso los
  oráculos numéricos de la ABC se recalcularon **inmediatamente antes** de cada medición en vez de
  reusar el valor de la consulta anterior. Los criterios del Dashboard no se vieron afectados porque
  las filas de prueba son del día de hoy y las que movió el otro proceso son de agosto.
- **Datos de prueba creados y borrados por QA:** 7 Ventas (ids 9001-9007) + 4 ItemsVenta, y un backup
  temporal de la columna `ClasificacionABCSugerida` (tabla `qa_bk_abc`). Todo **restaurado y verificado**
  al cierre (ver "Estado de la base al cerrar").
- `git status --porcelain` en el repo del sistema: **limpio** (solo el `?? .claude/` que ya existía al
  arrancar la sesión, ajeno a QA). No se escribió ninguna línea en el repo bajo prueba.

## Parte A — Corrección de datos: `UnidadVenta`

| # | Criterio | Resultado | Evidencia observada |
|---|---|---|---|
| A1 | No queda **ningún** producto en `Metro` y el total no cambió | **PASS** | `SELECT UnidadVenta, COUNT(*) FROM Productos GROUP BY UnidadVenta` → `1 (Unidad) = 112.471`, `2 (Peso) = 14`, **`3 (Metro)` no devuelve ninguna fila**. Total `112.485`. Coincide exacto con lo reportado |
| A2 | Los 14 de `Peso` siguen en `Peso` | **PASS** | 14 filas con `UnidadVenta = 2`, listadas una por una (ALAMBRE DE FARDO X 1 KG, electrodos, cloro granulado, varilla de bronce…) |
| A3 | Los 2.635 candidatos están **listados** y **no modificados** | **PASS** | CSV `Migracion/candidatos-corte-por-metro-20261005-121947.csv`: **2.635 registros únicos** (2.637 líneas físicas; el id 66109 tiene un salto de línea embebido dentro del campo `Nombre`, que va entrecomillado → es un registro RFC4180 válido partido en 2 líneas, no 2 registros). Grupos: cable 804, manguera 535, cadena 534, alambre 276, soga/piola/cuerda 271, tanza 215 = 2.635. Los 2.635 ids se consultaron contra la base: **2.635 encontrados, los 2.635 con `UnidadVenta = 1`** — listados pero no tocados |
| A4 | El input de cantidad vuelve a `step` 1 para esos productos y sigue aceptando decimales en los fraccionables | **PASS** | `/Ventas/Nueva`, Select2 real. Producto 2324 "ACCES.CABLE CANAL 18 X 21 VARIOS KALOP" (**está en el CSV de candidatos**, o sea venía de `Metro`) → `step="1"`, `checkValidity()` con `2.5` = **false**, con `3` = true. Producto 3597 "ALAMBRE DE FARDO X 1 KG" (`Peso`) → `step="0.001"`, acepta `2.5`. Repetido con el producto 1008 (también del CSV): `step="1"`. El endpoint `/Ventas/BuscarProductos` devuelve `"unidadVenta":"Unidad"` / `"Peso"` (nombre del miembro del enum, por `JsonStringEnumConverter` sin naming policy), que es exactamente lo que compara el JS de la vista |
| A5 | El modo correctivo **no requiere conexión a SQL Server** | **PASS** | Corrido con una cadena de conexión a SQL Server **deliberadamente inalcanzable** (`Server=NO-EXISTE\INVALIDO;…;Connect Timeout=3`): imprime `Origen (SQL Server): NO SE USA — este modo trabaja solo contra MySQL`, completa el trabajo y sale con **exit code 0**. (Nota: MSSQLSERVER y SQLEXPRESS están corriendo en la máquina, así que la ausencia del servicio no habría probado nada — de ahí la cadena inválida como oráculo) |
| A6 | El modo es **idempotente**: correrlo dos veces no rompe nada ni duplica el CSV | **PASS** | Segunda corrida sobre la base ya corregida: `No hay productos con UnidadVenta = Metro: nada que corregir`, exit 0, **ningún CSV nuevo** (el `return` temprano va antes de la generación del listado) y la base sin cambios |

**Verificación extra del fix de `MH-001` (variante nueva).** La segunda corrida corta antes del query
de patrones, así que **no** ejercita el fix. Se sembraron a propósito **2 filas en `Metro`** (producto
2324, que matchea "CABLE", y producto 1559 "MARTILLO GALPONERO", que no matchea ningún patrón) y se
volvió a correr el modo: los 6 grupos / 8 patrones `LIKE` corrieron **sin ninguna excepción**, el CSV
listó solo al 2324 en el grupo `cable`, y las 2 filas pasaron a `Unidad`. Estado restaurado al snapshot
exacto (mismo `COUNT(*)` y mismo `SUM(Id)` por unidad). **El fix está verificado por ejecución, no por
lectura.**

## Parte B — Dashboard y clasificación ABC: ventas `Confirmada`

Datos de prueba sembrados (todos del día de negocio argentino 2026-10-05 salvo donde se indica):

| Venta | Estado | `Fecha` (UTC) | Día ART | Total | Ítems |
|---|---|---|---|---:|---|
| 9001 | Confirmada | 05/10 14:00 | **hoy** | 1.234,56 | prod 1008 × 7 |
| 9002 | Confirmada | 05/10 17:00 | **hoy** | 765,44 | — |
| 9003 | **Borrador** | 05/10 14:30 | hoy | 99.999,00 | prod 2324 × **9.999** |
| 9004 | **Anulada** | 05/10 14:40 | hoy | 88.888,00 | prod 1559 × **5.555** |
| 9005 | Facturada | 05/10 15:00 | **hoy** | 500,00 | prod 1008 × 1 |
| 9006 | Confirmada | 05/10 **02:00** | **04/10** (23:00 ART) | 777,77 | — |
| 9007 | Confirmada | 06/10 **02:00** | **05/10** (23:00 ART) | 111,11 | — |

| # | Criterio | Resultado | Evidencia observada |
|---|---|---|---|
| B1 | Con ventas `Confirmada`, el Dashboard muestra ventas del día **distinto de cero** y coincidente con la suma real | **PASS** | `/Dashboard` renderiza **"Ventas de hoy: 4 · $ 2.611,11"**. Oráculo: 9001+9002+9005+9007 = 1.234,56 + 765,44 + 500,00 + 111,11 = **2.611,11**, cantidad **4**. Coincide exacto |
| B2 | "Productos más vendidos del mes" incluye los ítems de ventas `Confirmada` | **PASS** | La card "Top productos del mes" muestra **`'PINZA PELA CABLE 7" AUTOMATICA'` → 8**. Oráculo: 7 unidades de la `Confirmada` 9001 + 1 de la `Facturada` 9005 = 8. Sin la `Confirmada` habría mostrado 1 |
| B3 | La ABC automática por rotación considera las `Confirmada` | **PASS** | Recálculo disparado desde la UI (`/Stock` → "Recalcular clasificación ABC" → SweetAlert2 → submit). Mensaje: *"…1 productos A, 1 B y 112483 C. **5 productos con ventas en el período**."* Oráculo medido justo antes: 5 productos (11683=60u, 67=14u, 1008=8u, 2491=3u, 44969=1u). **Con el criterio viejo (solo `Facturada`) habrían sido 4.** Discriminador decisivo: el **producto 67** aparece **únicamente** en las ventas 12 y 13, las dos `Confirmada`, y quedó con `ClasificacionABCSugerida = 2 (B)`; antes del fix habría quedado en `C` por no tener ninguna venta |
| B4 | `Borrador` y `Anulada` siguen excluidas de los tres puntos anteriores | **PASS** | (a) Ventas del día: si contaran, el total sería ≈ **$ 191.498** en vez de $ 2.611,11 y la cantidad 6. (b) Top del mes: el prod 2324 (9.999 u, Borrador) y el 1559 (5.555 u, Anulada) **no aparecen** — serían #1 y #2 por lejos. (c) ABC: `ProductosConVenta = 5`, no 7, y 2324/1559 quedaron en **`C`** cuando con 9.999 unidades el 2324 habría sido `A` y habría corrido el Pareto de todo el catálogo. **`Producto.ClasificacionABC` (la manual del cliente) quedó intacta** (99/483/111.903 antes y después) |
| B5 | El Dashboard respeta el día de negocio argentino | **PASS** | Par de borde construido a propósito: la 9006 (05/10 **02:00 UTC** = 04/10 23:00 ART, **ayer**) quedó **excluida**, y la 9007 (06/10 **02:00 UTC** = 05/10 23:00 ART, **hoy**) quedó **incluida**. Es exactamente el escenario de **D7 / MH-009**, y el corrimiento de día no reaparece. El encabezado dice "lunes 05 de octubre de 2026". `DashboardService` usa `ArgentinaTime.HoyRangoUtc()` y `ArgentinaTime.RangoMesUtc(anio, mes)`, sin ningún `DateTime.Today` |

## Cobertura del catálogo cross-proyecto

| id | aplica | resultado | acción |
|---|---|---|---|
| `MH-001` | **sí** | **PASS** | Quinta aparición (variante `Any()` + `EF.Functions.Like` sobre `string[]` local). Fix verificado **por ejecución** con 2 filas sembradas en `Metro`. Barrido ampliado `grep -rnE "\.(Contains\|Any)\("` sobre toda la solución: los casos restantes son colecciones de `int`/`enum` (seguras, ver `nota_qa_sprint4`) o `string` con el workaround en memoria y el comentario de MH-001 al lado. Se agregó `nota_qa_laplatense_sprint0` al item del YAML (en `32` ya estaba documentado) |
| `MH-050` | sí | **PASS** | Es el mismo patrón en superficie nueva. No hay ningún `Where(coleccionLocalDeString.Contains(...))` sin workaround en los dos archivos del lote |
| `LP-001` | **sí** | **PASS** | Es la familia de la Parte B. El predicado se escribe contra el **conjunto explícito de estados consumados** (`Confirmada \|\| Facturada`), no como `!= Borrador`. Verificado funcionalmente con el borrador de 9.999 unidades que la regla manda probar |
| `LP-002` | **sí** | **PASS** | Barrido completo `grep -rn "EstadoVenta.Facturada"` sobre la solución: 10 sitios. Los 3 de agregación están corregidos; los 7 restantes son correctos por diseño (`VentaWorkflowService` **asigna** el estado y guarda contra re-facturar; `EntregaService` ya aceptaba `Confirmada or Facturada`; `Views/Ventas/Details.cshtml` distingue el badge y el bloque de CAE, que **sí** son solo de `Facturada`). No quedó ningún cuarto sitio |
| `MH-009` | **sí** | **PASS** | Ver criterio B5. El par 9006/9007 es el test de borde de la familia |
| `MH-023` | sí | **no reproducible hoy — riesgo latente** | El denominador del Pareto suma `ItemVenta` de productos que podrían estar soft-deleted, mientras la lista a clasificar los excluye. Hoy hay **0 productos con `DeletedAt`**, así que no se puede observar. Queda anotado como riesgo, **no es un defecto de este commit** |
| `LP-003` | sí | **PASS** | El input de cantidad de la venta se renderiza con `InvariantCulture` vía el helper `num` (`value="1"`, `step="1"` / `"0.001"`); ningún input quedó vacío |
| `LP-004` | N/A | — | Buscador global de listados, fuera del alcance del lote |
| `KOI-017` | sí | **PASS con observación** | "Ventas de hoy" y "Caja de hoy" se dibujan lado a lado y **las dos usan la misma ventana** (día de negocio ART: `HoyRangoUtc()` y `ObtenerResumenDiaAsync(ArgentinaTime.Hoy)`), así que no hay el defecto de ventanas distintas. Observación de liberación abajo |
| `MH-033` | N/A | — | Ledger de caja / cobro de CC: es el ítem 0.5, otro lote |
| `LP-005`, `LP-006`, `LP-007` | N/A | — | Fuera del alcance del lote |

## Cobertura de reglas nuevas/modificadas desde la última corrida de QA

`6-qa.md` **no tenía** el campo "Ultima validacion de reglas cross-proyecto" (última corrida:
**2026-08-24**). Según la instrucción, eso obliga a tratar el catálogo vigente como "a validar por
primera vez" — que es más de lo que cabe en un lote. Se validó el **subconjunto que toca los 2 módulos
de este lote** y se deja declarado qué quedó afuera, para que el lote que cierre el Sprint 0 lo complete.

| regla | origen | resultado | acción |
|---|---|---|---|
| `KOI-017` — la ventana de cada magnitud comparativa es un dato | `32`, 2026-09-23 (nueva) | **PASS con observación** | Ejecutada contra el Dashboard aunque el commit no la dispara |
| `MH-022` — proyección que estima por promedio un solo lado | `32`/YAML, 2026-09-24 (nueva) | **N/A** | El nivel 2 del Dashboard ("salud financiera") todavía no existe: la card dice "disponible en la próxima entrega". **Hay que volver a correr esta regla cuando se construya** |
| `MH-023`, `MH-024` — Pareto ABC: denominador y "última venta" | YAML, 2026-09-25 (nuevas) | `MH-023` latente / `MH-024` **N/A** | `MH-024` no aplica: esta ABC no muestra columna "última venta" |
| `MH-001` variante `Any()` | `32`, 2026-10-05 (modificada hoy) | **PASS** | Verificada por ejecución |
| `KOI-015`, `KOI-016`, `CRM-017` a `CRM-024`, `MH-020`, `MH-021`, `MH-034`, `ELV-008`, `OLV-*` | `32`, 2026-08-28 a 2026-09-25 | **no validadas en este lote** | No tocan ninguno de los 2 módulos del lote. **Pendiente**: asignarlas a los lotes de Ventas/Caja/CC/Entregas |

## Defectos detectados

### LP-008 — `minor` — El XML-doc y el comentario que justifican el filtro siguen diciendo "solo Facturada" (NO corregido)

- **Severidad:** `minor`. No afecta el comportamiento, pero persiste una **regla de negocio falsa** en el repo.
- **Pasos:** abrir `ClasificacionAbcAutomaticaService.cs` y leer el XML-doc de la clase (punto 2) y el
  comentario de bloque anterior al `Where`; comparar con el predicado de la línea 82. Repetir con el
  XML-doc de `DashboardService.ObtenerTopProductosMesAsync` contra el `Where` de la línea 109.
- **Evidencia observada:** el XML-doc dice *"Solo cuentan los items de Ventas en estado `Facturada`"*;
  el comentario de bloque dice *"El filtro por `Estado == Facturada` es imprescindible"*; el XML-doc
  del Dashboard dice *"sobre Ventas Facturadas"*. Los tres son **prescriptivos** — argumentan a favor
  del criterio viejo — mientras el código filtra por `(Confirmada || Facturada)`.
- **Por qué importa:** es el texto que el próximo implementador o QA va a leer como la autoridad sobre
  qué estados cuentan, y suena más autorizado que el predicado. Es el mismo tipo de trampa que hizo
  falta corregir en el propio commit (el criterio estaba escrito en un comentario y nadie lo revisó).
- **Catalogado como `LP-008`** (nuevo, creado en esta corrida).

## Partes de defecto emitidos al Implementador

### Parte 1 — `LP-008`

- **id / severidad / módulo:** `LP-008` / `minor` / documentación en el código de las agregaciones por estado.
- **`archivos_fix` sugeridos** (hipótesis, no instrucción cerrada):
  - `FerreteriaLaPlatense.Infrastructure/Services/ClasificacionAbcAutomaticaService.cs` — XML-doc de la
    clase (≈ líneas 22-24) y comentario de bloque previo al `Where` (≈ líneas 71-78).
  - `FerreteriaLaPlatense.Infrastructure/Services/DashboardService.cs` — XML-doc de
    `ObtenerTopProductosMesAsync` (≈ líneas 96-99).
  - **No borrar el comentario, corregirlo:** la parte que explica por qué `Borrador` y `Anulada` quedan
    afuera es correcta y es lo valioso (`LP-001`).
- **`migracion_ef`:** ninguna.
- **Criterio de re-verificación (arranca en FAIL):** en los dos archivos, ningún comentario ni XML-doc
  nombra "solo `Facturada`" / "`Estado == Facturada`" como el criterio vigente, **y** sigue escrito el
  motivo por el que `Borrador` y `Anulada` se excluyen.

## Estado de los partes de la corrida anterior

Los defectos abiertos de la memoria previa (`D8` a `D14`) los cierran los otros lotes del Sprint 0;
este lote no los re-verificó salvo lo que pisa su alcance: **`D7` (ventana de fechas del Dashboard)
sigue cerrado** — ver criterio B5.

## Riesgos de liberación y mitigaciones

1. **El modo `--solo-unidad-venta` todavía no se corrió contra producción.** Lo corre Joaquín. Riesgo
   bajo y acotado: un `UPDATE` de una sola columna, idempotente y verificado. **Mitigación:** backup
   previo y guardar el CSV de candidatos que sale de la corrida de producción (va a ser otro archivo,
   con otros ids — los ids de dev **no sirven** para marcar a mano en producción).
2. **Los 2.635 candidatos siguen en `Unidad`.** Es la regla acordada, no un defecto: hasta que el
   cliente marque los que de verdad corta al mostrador, un corte de 2,5 m de cable se carga como 2 o 3.
   **Mitigación:** entregarle el CSV y dejar el listado como tarea pendiente del cliente.
3. **Los 14 de `Peso` son igual de sospechosos** (el legado no trae el dato). Mismo camino: lista para
   marcar a mano.
4. **`KOI-017` / observación del Dashboard:** "Ventas de hoy" y "Caja de hoy" usan la misma ventana,
   pero son magnitudes distintas (la caja incluye cobros de CC y excluye lo vendido en cuenta
   corriente) y la pantalla no lo dice. Es muy probable que el cliente lea los dos números juntos y
   reporte "no cierra". **Mitigación barata:** una línea de ayuda bajo la card de caja. No bloquea.
5. **`MH-023` latente en la ABC:** el día que haya productos con `DeletedAt`, el denominador del Pareto
   va a incluir ventas de productos que no están en la tabla clasificada. Hoy son 0.
6. **Deuda de cobertura de reglas:** 2026-08-24 → 2026-10-05 sin validación de reglas cross-proyecto.
   Este lote cubrió su subconjunto; el resto queda asignado arriba.

## Estado go/no-go (lote 3)

**GO** para los dos commits. Los 11 criterios de aceptación del lote están en **PASS con evidencia
observada**, y el único defecto es `LP-008`, `minor` y de documentación — no bloquea el merge, pero
tiene que entrar antes de que alguien vuelva a tocar esas dos agregaciones.

## Estado de la base de desarrollo al cerrar

- `UnidadVenta`: `Unidad` 112.471 / `Peso` 14 / `Metro` 0, total 112.485 — **idéntico al snapshot de
  apertura**, mismo `SUM(Id)` por unidad.
- `ClasificacionABCSugerida`: restaurada desde `qa_bk_abc` a 99 A / 483 B / 111.903 C (**0 diferencias**).
- `ClasificacionABC` (manual del cliente): nunca se tocó, 99 / 483 / 111.903.
- Ventas 9001-9007 y sus 4 `ItemsVenta`: **borradas**. Tabla `qa_bk_abc`: **borrada**.
- CSV de la corrida de prueba de QA en `bin/Debug/net10.0`: **borrado**. El CSV real de la corrida del
  implementador (`20261005-121947`) quedó intacto.

## Checklist de salida para merge (lote 3)

- [x] `dotnet build` de la herramienta de migración: 0 errores.
- [x] `Metro` = 0 y total de productos sin cambios, verificado en la base.
- [x] Los 14 de `Peso` intactos.
- [x] 2.635 candidatos listados y los 2.635 sin modificar.
- [x] `step` del input de cantidad: 1 en ex-`Metro`, 0.001 en `Peso`, verificado en pantalla.
- [x] Modo correctivo sin SQL Server (cadena inválida) e idempotente.
- [x] Fix de `MH-001` (variante `Any()`) ejercitado por ejecución, no por lectura.
- [x] Dashboard: ventas del día y top del mes cuentan `Confirmada`, con el número exacto.
- [x] ABC automática: cuenta `Confirmada`; `ClasificacionABC` manual intacta.
- [x] `Borrador` y `Anulada` excluidas de los tres cálculos, con discriminadores de 9.999 y 5.555 unidades.
- [x] Día de negocio ART en el borde 21:00-24:00 (par 9006/9007).
- [x] Sin errores de consola JS ni HTTP ≥ 500 en toda la corrida.
- [x] Base de desarrollo restaurada y verificada.
- [x] `git status --porcelain` limpio en el repo del sistema bajo prueba.
- [ ] `LP-008` aplicado por el Implementador y re-verificado en contexto nuevo.
- [ ] Modo correctivo corrido contra producción + CSV de candidatos de producción entregado al cliente.

---

# Sprint 0 — LOTE 2: cobro/ajuste de cuenta corriente + D8 (QA, 2026-10-05, rama `entrega-1-migracion`)

Lote **financiero** (1 módulo por corrida). Commits bajo prueba: `3b4d9fa` (item 0.5, cobro y ajuste de CC) y
`800db75` (item 0.2, guarda de doble envío en Confirmar). Contexto fresco: no se leyó la transcripción del
Implementador, sólo el diff y el mensaje de los dos commits.

## Entorno y metodología

- Build: `dotnet build FerreteriaLaPlatense.slnx` → **Compilación correcta, 0 errores** (8 warnings NU1902
  preexistentes de MailKit/MimeKit).
- App levantada en `https://localhost:7200`, `ASPNETCORE_ENVIRONMENT=Development`, base `laplatense_dev`.
- **El servidor MCP `playwright` NO estaba disponible en la sesión** (no expone `mcp__playwright__*`). Se
  declaró y se cayó a verificación automatizada equivalente: Playwright instalado en el scratchpad de QA,
  manejando los binarios de Chromium ya presentes en `ms-playwright` (`chrome-headless-shell-1243` y
  `chromium-1243` completo). **Toda la evidencia de abajo es de navegador real + lectura directa de MySQL**,
  no revisión de código.
- Usuarios: `admin.qa@test.local` (rol Administrador, creado para esta corrida y **eliminado al cerrar**),
  `vendedor.qa@test.local` (Vendedor, preexistente), `no-reply@olvidata.com.ar` (SuperUsuario sembrado).
- Datos de prueba: cliente 3 (TAVELA) con una deuda de **$ 12.345,67** (importe con centavos a propósito,
  para ejercitar `LP-003`/`D5`). Ventas 7, 9, 10 y 11 (borradores preexistentes de QA) para la parte B.
- **El repo del sistema no se tocó.** `git status --porcelain` al cerrar devuelve sólo `?? .claude/`, que ya
  estaba al arrancar la corrida y no es de QA.

## Parte A — Cobro y ajuste de cuenta corriente

| # | Criterio | Resultado | Evidencia observada |
|---|---|---|---|
| A1 | Cobro de $X baja la CC en $X **y** genera un Ingreso de Caja por $X | **PASS** | Cobro de $ 2.345,67 → `MovimientosCCCliente` id 5 (Tipo=Credito, Origen=Pago, 2345.67) + `CajaMovimientos` id 11 (Tipo=Ingreso, 2345.67, `OrigenTipo='CobroCC'`, `OrigenId=5`). Pantalla: "Cobro de $ 2.345,67 registrado. Saldo nuevo: $ 10.000,00". Al cerrar los 2 cobros de la corrida: `SUM(Importe) Origen=Pago = 3095.37` y `SUM(Monto) OrigenTipo='CobroCC' = 3095.37` — **1:1 exacto, sin huérfanos** |
| A2 | Si una de las dos escrituras falla, **ninguna** queda persistida | **PASS** | Fallo inyectado con un trigger MySQL `BEFORE INSERT ON CajaMovimientos` que hace `SIGNAL` sobre `OrigenTipo='CobroCC'`. Cobro de $ 1.111,11 → pantalla "Error al registrar el cobro: Could not save changes…", **0 filas nuevas** en `MovimientosCCCliente` y en `CajaMovimientos`, saldo intacto en $ 10.000,00. El `AUTO_INCREMENT` saltó de 5 a 7, lo que confirma que el insert de CC se hizo y se **revirtió**. Trigger eliminado al cerrar |
| A3 | Un ajuste no genera ningún movimiento de Caja | **PASS** | 2 ajustes (Crédito $ 1.500,55 y Débito $ 250,25) → `COUNT(*) CajaMovimientos` **sin cambios** (10 antes, 10 después); las 2 filas de CC quedan con `Origen=Ajuste` |
| A4 | Un ajuste sin motivo es rechazado | **PASS** | Por UI: jquery-validate bloquea el submit (el SweetAlert2 no llega a abrirse). Salteando la validación de cliente con un `form.submit()` directo y `Motivo="   "` → el server igual repinta el formulario con el error de Motivo. No se persistió nada |
| A5 | `Vendedor` cobra y **no** ajusta; `Administrador` las dos | **PASS** | Vendedor en `/Clientes/CuentaCorriente/3`: botones = `['Registrar cobro','Volver a Clientes']` (**"Ajuste manual" oculto**). `GET /Clientes/RegistrarAjuste/3` → redirige a `/Account/AccessDenied?ReturnUrl=…`. `POST` directo a `RegistrarAjuste` con un token antiforgery válido suyo → redirect, **0 filas** con `Origen=Ajuste` de su `UsuarioId`. Cobro real como Vendedor → "Cobro de $ 749,70 registrado. Saldo nuevo: $ 8.000,00", fila con su `UsuarioId`. Administrador: `GET` de las dos pantallas → HTTP 200 |
| A6 | El saldo de la pantalla coincide con la suma real de los movimientos | **PASS** | Tras cobrar y ajustar: pantalla "SALDO ACTUAL $ 8.749,70" y `SUM(CASE WHEN Tipo=1 THEN Importe ELSE -Importe END) = 8749.70`. Tras el cobro del Vendedor: pantalla $ 8.000,00 = DB 8000.00 |
| A7 | La fecha del movimiento respeta el día de negocio argentino | **PASS** | Movimientos persistidos con el instante UTC real (`2026-10-05 15:56:34`, `16:04:22`), que proyectado a ART cae en el día de negocio **2026-10-05**. El wire de `CuentaCorrienteListar` entrega `"fecha":"2026-10-05T13:04:22.42715"` — ART, **sin sufijo `Z`**, o sea sin doble conversión. El `<input type="date">` de Fecha arranca en `2026-10-05` con `max="2026-10-05"` (= `ArgentinaTime.Hoy`, no `DateTime.Today`) |

### Importes, signos y bordes (lo que el brief pidió mirar expresamente)

- **Cobrar más que la deuda: comportamiento definido y rechazado.** Con `max` quitado del input y $ 99.999,99
  → "El importe (12.345,67) supera la deuda actual del cliente (12.345,67). Si la diferencia es un pago a
  cuenta, registrarla como ajuste." No es un hallazgo: la decisión está tomada y además se le indica al
  usuario el camino alternativo.
- **No se puede invertir el saldo por un error de signo en el cobro.** Con `min`/`max` quitados e importe
  `-5000.00` → "El importe del cobro debe ser mayor a cero." El signo del movimiento no lo decide el usuario:
  el cobro es siempre `Credito` y el ajuste lo deriva del combo Tipo, con el importe siempre positivo.
- **`LP-003`/`D5` (cultura) — PASS, y era el lugar natural para que reapareciera.** El importe arranca
  prellenado: el HTML real trae `value="12345.67"`, `max="12345.67"` y el hidden `SaldoActual="12345.67"`,
  todos en cultura invariante. El input **llega poblado** en el navegador (con `asp-for` puro habría salido
  `value="12345,67"` y el campo habría quedado vacío sin aviso). Importes con centavos probados de punta a
  punta: 2345.67, 1500.55, 250.25 y 749.70 se persistieron exactos.
- **`MH-001` (IN/`Any()` sobre colección local contra MySQL) — no aplica a este lote:** ni el cobro, ni el
  ajuste, ni el listado de CC filtran por una colección en memoria; los filtros son escalares y el combo de
  origen es un enum. Los 3 endpoints nuevos y el listado se ejercitaron por navegador sin un solo 500.
- **`LP-002` (origen nuevo en el ledger de caja) — PASS:** `/Caja` ofrece `CobroCC = "Cobro de cuenta
  corriente"` en el combo Origen y, filtrando por él, aísla exactamente los 2 cobros de la corrida.
- Guardas de negocio adicionales verificadas: fecha de caja **cerrada** (2026-08-21) → rechazada; fecha
  **futura** (2026-12-31) → rechazada; medio `CuentaCorriente` → no se ofrece en el combo.

## Parte B — D8 y guarda de doble envío

| # | Criterio | Resultado | Evidencia observada |
|---|---|---|---|
| B1 | Editar la cantidad **sin** guardar borrador y apretar Confirmar → se confirma lo que está en pantalla | **PASS** | Reproducción exacta del D8 original sobre la venta 7: cantidad 1 → **50**, pantalla "$ 76,84" (el bug original facturaba $ 1,54). Tras Confirmar: `Ventas.Id=7` queda Confirmada con **Total = 76.84**, `ItemsVenta.Cantidad = 50.000`. Repetido en la venta 11 (cantidad → 3, pantalla "$ 1.499,99" → `Total = 1499.99`) |
| B2 | Doble click en Confirmar → la venta se cierra **una sola vez** y no queda guardada como borrador sin confirmar | **PASS** | Venta 11: 3 invocaciones del handler con `jQuery.trigger('click')` (que **ignora** el atributo `disabled`, así que ejercita la guarda de reentrada y no sólo el bloqueo del botón) → **un único POST** observado en la red: `/Ventas/GuardarBorrador` con `continuar=confirmar` (un solo valor, no `confirmar,confirmar`). Resultado: `/Ventas/Details/11`, estado Confirmada. Venta 7, triple click sobre el confirm del SweetAlert2 → también una sola confirmación |
| B3 | Confirmar descuenta stock, registra Caja y registra CC **exactamente una vez** | **PASS** | Venta 7 (pago Efectivo): stock del producto 11683 `0 → -50` (= 50 exacto, no 100), **1** `CajaMovimiento` Ingreso de 76.84 `OrigenTipo='Venta' OrigenId=7`, CC sin tocar (correcto: no hubo pago en CC). Venta 11 (pago CuentaCorriente): stock del producto 67 `-11 → -14` (= 3 exacto), Caja **sin cambios** (correcto: no entró efectivo), **1** Débito de CC por fila de pago en CC. Venta 10 (Efectivo + CreditoCuotas): exactamente **2** movimientos de caja, uno por pago — sin duplicación |
| B4 | "Confirmar y facturar" sigue deshabilitado y eso no rompe la pantalla | **PASS (parcial)** | Sin certificado AFIP el botón **no se renderiza** (`@if (afipConfigurado)` en `Editar.cshtml`): `#btnConfirmarYFacturar` tiene `count = 0` en el DOM. La pantalla carga y opera sin errores de consola ni requests fallidos, y `guardarYContinuar` deshabilita un id inexistente sin romperse. **Ver BLOCKED abajo:** la rama `facturar` de la guarda no se puede ejercitar |

### BLOCKED

- **B4b — la rama `facturar` de `guardarYContinuar` es no ejercitable en este entorno.** Sin certificado AFIP
  el botón no existe en el DOM, así que no hay forma de disparar `continuar=facturar` por el camino de
  usuario. Queda **BLOCKED por entorno** (no por criterio mal escrito): se re-verifica cuando se cargue el
  certificado real, y es la verificación que de verdad cierra el riesgo fiscal original de D8.

### Hallazgo sobre la premisa del commit `800db75`

El commit justifica la guarda en que un segundo click posteaba `continuar=confirmar&continuar=confirmar`, el
`switch` caía en el default y el borrador se guardaba sin cerrar la venta. **Ese camino concreto no se
reproduce:** se posteó a mano ese POST duplicado sobre la venta 10 (borrador confirmable) y la venta **quedó
Confirmada**, con sus 2 movimientos de caja correctos — el `SimpleTypeModelBinder` de ASP.NET Core toma el
primer valor, no la concatenación. La guarda de reentrada **igual es correcta y se queda** (evita dos POST
independientes y el doble disparo de la UI, y eso sí se verificó en B2); lo que corresponde es dejar
registrado que el defecto que decía cerrar era otro. El agujero real de esa clase que **sigue abierto** es el
valor desconocido → `LP-007`.

## Cobertura del catálogo cross-proyecto

| id | aplica | resultado | acción |
|---|---|---|---|
| `LP-003` (decimal es-AR en `value` de input numérico) | sí | **PASS** | Las 2 pantallas nuevas usan el helper `num` con `InvariantCulture`; verificado en el HTML real |
| `D11` / `LP-003` *nota_generalizacion* (hidden decimal parseado ×100) | sí | **PASS** | El hidden `SaldoActual` sale invariante (`12345.67`) y además el Service re-resuelve el saldo desde la base: el valor posteado no decide nada |
| `LP-002` (origen nuevo en el ledger ⇒ barrer todo lo que lee `OrigenTipo`) | sí | **PASS** | Opción `CobroCC` presente en el filtro de `/Caja` y aislando correctamente |
| `MH-033` (el ledger de caja registra toda entrada real de dinero) | sí | **PASS** | El cobro del fiado entra como Ingreso real; el ajuste, a propósito, no |
| `MH-001` (IN/`Any()` sobre colección local en MySQL) | no | N/A | Ningún filtro por colección en el alcance; endpoints nuevos sin 500 |
| `MH-027` (un `OrigenTipo` nuevo vuelve no-única la FK al hijo) | sí | **PASS con riesgo residual** | Hoy no hay contramovimiento ni reversión de cobro de CC, así que el guard no existe y no puede romperse. **Riesgo para cuando se implemente "anular cobro"** — ver riesgos |
| `MH-014` (fecha de un instante UTC proyectada de más en el cliente) | sí | **PASS** | El wire entrega ART sin `Z`; el cliente no reconvierte. Pero el **formato** de la hora falla → `LP-006` |
| `MH-037` (carga retroactiva imputada al día de hoy) | sí | **PASS** | Un cobro con fecha anterior se persiste con `ArgentinaTime.InicioDiaUtc(día)`, no con "hoy" |
| `REG-010` (visibilidad del botón acompaña al permiso real) | sí | **PASS** | Botón de ajuste oculto para Vendedor **y** `[Authorize]` server-side verificado por `GET` y por `POST` directo |
| `LP-004` (buscador global se pierde al volver al listado) | sí | no ejecutado | Fuera del alcance del lote (listado de Clientes/Productos, no la CC). Queda para el lote de listados |
| `LP-001`, `LP-005`, `REG-006`, `REG-008`, `GAN-005`, `GAN-006`, `MH-020/021/044/048`, `DN-003/004` | no | N/A | Módulos fuera del lote (ABC, Details de venta, pagos de compra, facturas de venta, reversión de pagos) |

## Cobertura de reglas nuevas/modificadas desde la última corrida

`6-qa.md` **no tenía** el campo "Ultima validacion de reglas cross-proyecto" (memoria v4, previa a que la
regla existiera), así que por contrato todo el catálogo vigente contaba como "a validar por primera vez".
Ese barrido completo es trabajo del **lote 1**, y **esta corrida no recibió su resultado** — se declara el
hueco en vez de darlo por hecho. Lo que sí se ejecutó acá es el subconjunto que toca la superficie del lote
(tabla de arriba: `LP-002`, `LP-003`, `MH-001`, `MH-014`, `MH-027`, `MH-033`, `MH-037`, `REG-010`). El campo
queda inicializado en **2026-10-05** para que la próxima corrida tenga desde dónde diferenciar.

## Defectos detectados

### LP-006 — `minor` — La hora del ledger se muestra en reloj de 12 horas sin AM/PM

- **Pasos:** registrar un cobro de CC pasado el mediodía ART y abrir `/Clientes/CuentaCorriente/{id}`.
- **Evidencia observada:** la grilla muestra `5/10/2026, 01:04:22` para un movimiento de las **13:04:22 ART**,
  y `5/10/2026, 12:00:00` para el Débito imputado a las **00:00 ART**. La **fecha** es correcta (el día de
  negocio se proyecta bien); la **hora** miente y sin AM/PM no se puede desambiguar: la medianoche se lee como
  mediodía. Mismo efecto en `/Caja`.
- **No es artefacto del entorno de prueba:** `new Date('2026-10-05T13:04:22').toLocaleString('es-AR')`
  devuelve `"5/10/2026, 01:04:22"` **idéntico** en `chrome-headless-shell` y en el Chromium completo.
- **No hay doble conversión de huso:** el wire de `CuentaCorrienteListar` entrega
  `"fecha":"2026-10-05T13:04:22.42715"`, ya en ART y sin `Z`. El servidor está bien; el defecto es sólo de
  formato en el cliente.
- **Por qué importa:** es el ledger que el operador lee para conciliar la caja del día. Dos movimientos
  separados por 12 horas se muestran con la misma hora.
- Catalogado como **`LP-006`**. Preexistente también en `/Caja` (no lo introdujo este sprint).

### LP-007 — `minor` — Un `continuar` desconocido guarda el borrador y no cierra la venta, en silencio

- **Pasos:** `POST /Ventas/GuardarBorrador` con el formulario completo de un borrador confirmable y un hidden
  `continuar=zzz`.
- **Evidencia observada:** HTTP 200 → redirect a `/Ventas/Editar/9`; el borrador queda guardado con los datos
  nuevos pero la venta **sigue en Borrador**, sin stock descontado, sin movimiento de Caja y **sin ningún
  mensaje**. Contraste en la misma corrida: `continuar=confirmar` sobre la misma venta → `/Ventas/Details/9`,
  Confirmada.
- **Por qué importa:** es exactamente el síntoma de clase de D8 (la pantalla pide una cosa, el server hace
  otra, en silencio) del lado del servidor. Hoy sólo se alcanza con un POST fabricado, de ahí `minor`; pero es
  el agujero que el commit `800db75` se propuso cerrar y la guarda que agregó es **sólo de cliente**.
- Catalogado como **`LP-007`**.

### D17 — `informativo` — El error de la transacción de cobro se muestra crudo al usuario

Con el fallo inyectado, la pantalla muestra `Error al registrar el cobro: Could not save changes. Please
configure your entity type accordingly.` — texto interno de EF Core en inglés. El rollback es **correcto**
(eso es lo que importa y es A2 en PASS); lo que se filtra es el mensaje. Se reporta sin catalogar: es el
`catch (Exception ex)` de `RegistrarCobroAsync` concatenando `ex.Message`.

### D18 — `informativo` — Un ajuste de Crédito puede dejar el saldo invertido sin ningún aviso

El ajuste no tiene tope contra el saldo (a diferencia del cobro). Es **coherente con el diseño** — el propio
mensaje de error del cobro dirige el pago a cuenta al ajuste, y la pantalla ya pinta el saldo negativo en
verde con "a favor" — así que no se reporta como defecto. Se anota porque es la única vía desde la UI para
dejar un saldo negativo y conviene que esté explícito en la memoria antes de que alguien lo lea como un bug.

### D19 — `informativo` — Confirmar admite pagos que superan el total cuando hay un pago en CC

La guarda de `ConfirmarAsync` es `pagosCC.Count == 0 && sumaPagos < venta.Total - 0.01m`: con un pago en
cuenta corriente presente, la verificación se saltea **en los dos sentidos**. En la corrida quedó una venta
con pagos por $ 1.500,00 contra un total de $ 1.499,99 (la pantalla mostró "saldo pendiente $ -0,01" y
confirmó igual), y la CC del cliente quedó debiendo $ 1.500,00. Es comportamiento **preexistente de Ventas**,
fuera del alcance de estos dos commits; se anota para el lote de Ventas.

## Partes de defecto emitidos al Implementador

### Parte 1 — `LP-006`

- **Severidad:** minor. **Módulo:** grillas de ledger (CC de clientes y Caja).
- **Reproducción y evidencia:** ver el defecto arriba.
- **`archivos_fix` sugeridos (hipótesis, no instrucción cerrada):**
  `FerreteriaLaPlatense.Web/Views/Clientes/CuentaCorriente.cshtml` y
  `FerreteriaLaPlatense.Web/Views/Caja/Index.cshtml`, columna `fecha` del DataTable: reemplazar
  `new Date(v).toLocaleString('es-AR')` por un formateo con reloj de 24 horas explícito (`{ hour12: false }`,
  o `moment(v).format('DD/MM/YYYY HH:mm:ss')` — moment ya está cargado para el daterangepicker).
  **No usar `moment.utc()`:** el valor ya viene en ART (ese es el error opuesto, `MH-014`).
- **`migracion_ef`:** ninguna.
- **Criterio de re-verificación (arranca en FAIL):** registrar un cobro de CC después del mediodía ART y leer
  la columna Fecha en `/Clientes/CuentaCorriente/{id}` **y** en `/Caja` filtrando por `CobroCC`: la hora
  mostrada tiene que ser `>= 13` y coincidir en las dos pantallas; un movimiento imputado a las 00:00 del día
  de negocio tiene que mostrarse `00:00`, no `12:00`. La fecha (día de negocio) no puede cambiar.

### Parte 2 — `LP-007`

- **Severidad:** minor. **Módulo:** Ventas / `GuardarBorrador`.
- **Reproducción y evidencia:** ver el defecto arriba.
- **`archivos_fix` sugeridos (hipótesis):** `FerreteriaLaPlatense.Web/Controllers/VentasController.cs`,
  `GuardarBorrador`: separar `continuar is null or ""` (guardado normal → `GuardadoOk`) de un valor
  desconocido (→ `TempData["ErrorMessage"]` explícito, o tipar el parámetro como un enum acotado para que el
  binder lo rechace antes de entrar a la acción). No tocar `"confirmar"` / `"facturar"`.
- **`migracion_ef`:** ninguna.
- **Criterio de re-verificación (arranca en FAIL):** `POST /Ventas/GuardarBorrador` con `continuar=zzz` sobre
  un borrador confirmable → mensaje de error **visible en pantalla** y la venta sin cerrar; `POST` sin
  `continuar` sigue guardando con mensaje de éxito; `continuar=confirmar` sigue confirmando. **Regresión
  obligatoria de B2:** dos invocaciones seguidas de Confirmar siguen produciendo **un** POST y **una** sola
  confirmación (stock, Caja y CC una vez).

## Estado de los partes de la corrida anterior

| defecto | estado en esta corrida |
|---|---|
| **D8** — "Confirmar y facturar" factura datos viejos | **CERRADO** por B1/B2. El fix de fondo fue `a6a78f0` (`guardarYContinuar` postea el form entero); `800db75` agregó la guarda de reentrada. La rama `facturar` queda **BLOCKED** hasta que haya certificado AFIP |
| **D9** — `CajaMovimiento.Fecha` con dos semánticas | **PASS en el alcance de este lote**: los movimientos nuevos de cobro y ajuste usan `ArgentinaTime` (día de negocio ART) y la guarda de caja cerrada consulta `ArgentinaTime.Hoy`. La verificación a fondo es de otro lote |
| **D11** — decimal es-AR parseado ×100 en hidden | **PASS en el alcance de este lote**: los hidden decimales de las 2 pantallas nuevas salen invariantes |
| D10, D12, D13, D14, D16 | fuera del alcance del lote, sin cambios |

## Riesgos de liberación

1. **`MH-027` latente (medio).** El ledger de caja estrenó el origen `CobroCC` con `OrigenId` apuntando al
   `MovimientoCCCliente`. Hoy la relación es 1:1 y verificada, pero **no existe "anular un cobro"**: cuando se
   implemente, el contramovimiento va a tener que resolver *cuál* movimiento de caja corresponde, y ese es
   exactamente el escenario de `MH-027` (un `OrigenTipo` nuevo vuelve no-única la FK al hijo). Mitigación:
   atar el contramovimiento por `(OrigenTipo, OrigenId)` y nunca por `(VentaId, Monto)`.
2. **Sin control de concurrencia en el cobro (bajo).** `RegistrarCobroAsync` lee el saldo y después inserta,
   sin bloqueo ni `RowVersion`: dos cobros simultáneos del mismo cliente pueden pasar los dos la guarda de
   "no mayor a la deuda" y dejar el saldo negativo. Probabilidad real baja (un mostrador, un cajero), pero el
   ajuste manual lo corrige, así que no es bloqueante.
3. **El riesgo fiscal original de D8 no está cerrado del todo (medio).** La rama `facturar` quedó BLOCKED por
   no haber certificado. Mitigación: **re-verificar B4b como condición de habilitar AFIP**, no después.
4. **`LP-007` (bajo).** Sólo alcanzable con un POST fabricado, pero deja el server sin red de contención para
   la clase de bug que el sprint se propuso cerrar.

## Estado go/no-go

**GO** para los dos commits del lote. Los 7 criterios de la parte A y los 4 de la parte B están en PASS con
evidencia observada; los 2 defectos nuevos son `minor` y ninguno toca la corrección de los importes, de los
saldos ni de la atomicidad. Condición: `LP-006` y `LP-007` entran al backlog del Implementador y se
re-verifican en la corrida siguiente, con los criterios de vuelta en FAIL.

## Estado de `laplatense_dev` tras esta vuelta

**Restaurada a su línea base**, verificado por consulta:

- `MovimientosCCCliente` → **0 filas** (igual que al arrancar).
- `CajaMovimientos` → **9 filas** (ids 1..9, igual que al arrancar).
- Ventas 7 / 9 / 10 / 11 → de vuelta en **Borrador** con sus totales originales ($ 1,54 / $ 1.100,55 /
  $ 500,00 / $ 500,00). Los encabezados se recalcularon **con la lógica del propio sistema** (abrir el
  borrador y "Guardar borrador"), no a mano por SQL.
- Stock: producto 11683 → `0.000`; producto 67 → `-11.000`.
- `PagosVenta` restaurados a sus medios, montos y cuotas originales.
- Usuario `admin.qa@test.local` y su asignación de rol **eliminados**; hash del Vendedor restaurado.
  `AspNetUsers` de vuelta en 4 filas.
- Trigger de inyección de fallo **eliminado** (`SHOW TRIGGERS` vacío).

## Pruebas mínimas ejecutadas

1. Build de la solución completa.
2. Cobro con centavos (parcial), botón "Todo", cobro por el total.
3. Cobro > deuda, importe negativo, fecha futura, fecha de caja cerrada, medio CuentaCorriente.
4. Rollback de la transacción con fallo inyectado en la segunda escritura.
5. Ajuste Crédito y Débito con decimales; ajuste sin motivo (por UI y por POST directo).
6. Permisos de las 4 acciones nuevas por `GET` y por `POST` directo, con Vendedor y con Administrador.
7. Grilla de CC (orígenes, fechas, saldo) y filtro `CobroCC` en `/Caja`.
8. D8: cantidad editada sin guardar + Confirmar, en 2 ventas distintas.
9. Doble/triple envío de Confirmar, con conteo de POST en la red.
10. Confirmación con pago en Efectivo, en CuentaCorriente y mixta: stock, Caja y CC una sola vez.
11. `continuar` ausente / `confirmar` / duplicado / desconocido.

## Checklist de salida para merge

- [x] Build sin errores.
- [x] Los 7 criterios de aceptación de la parte A en PASS con evidencia observada.
- [x] Los 4 criterios de la parte B en PASS; la rama `facturar` declarada BLOCKED por entorno.
- [x] Atomicidad del cobro demostrada con un fallo inyectado, no por lectura de código.
- [x] Permisos verificados también por POST directo, no sólo por visibilidad del botón.
- [x] `LP-003`/`D5` (cultura) verificado sobre el HTML real de las 2 pantallas nuevas.
- [x] `LP-002` verificado: el origen nuevo del ledger es visible y filtrable.
- [x] 2 defectos nuevos catalogados (`LP-006`, `LP-007`) con parte de defecto y criterio de re-verificación.
- [x] Base de desarrollo restaurada a su línea base y verificada.
- [x] `git status --porcelain` del repo del sistema sin cambios de QA.
- [ ] `LP-006` y `LP-007` aplicados por el Implementador y re-verificados en contexto nuevo.
- [ ] B4b (`continuar=facturar`) re-verificado al cargar el certificado AFIP — **condición para habilitar AFIP**.

---

# Entrega 2 — SEGUNDA VUELTA DE QA (2026-08-24, rama `entrega-2`)

Gate de liberación previo al despliegue a un servidor de pruebas para el cliente. **No** repite la matriz
completa de la primera vuelta (2026-08-21, sección siguiente): se enfoca en los 3 lotes de cambios
posteriores y en la regresión de lo que ya pasaba.

## Commits validados (posteriores al ciclo del 2026-08-21)

| commit | contenido |
|---|---|
| `30f6c90` | Cierre de D10, D11, D12, D13 + hardening AFIP + botón "Confirmar y facturar" `disabled` |
| `9c6b1db` | `ItemVenta.Descuento`/`Recargo`: monto fijo → **porcentaje** (0-100) + fix de `PrecioOferta` |
| `53e2c48` | **PAT-016**: búsqueda global multi-formato + filtros persistidos en `Session` en los 6 listados |

## Entorno y metodología

- `dotnet build FerreteriaLaPlatense.slnx` → **0 errores** (verificado 2 veces: inicial y post auto-fix).
  8 advertencias, todas preexistentes (NU1902 MailKit/MimeKit).
- Migración pendiente `20260825005540_ItemVenta_DescuentoRecargoPorcentaje` **aplicada** a `laplatense_dev`.
  Verificado post-aplicación: `ItemsVenta.Descuento`/`Recargo` son `decimal(5,2)`.
- El servidor MCP `playwright` **no estaba conectado en esta sesión** (se declara explícitamente, igual que
  en la primera vuelta). Se automatizó conduciendo un Chromium real vía `playwright-core` desde Node contra
  `https://localhost:7200`. **Todo lo de esta sección se ejecutó contra el sistema real.**
- Prerequisito resuelto: no se conocía la contraseña de los 3 usuarios QA creados el 21/08. Se les reescribió
  el hash de Identity (PBKDF2-HMAC-SHA512, formato V3) directamente en `laplatense_dev`. **No se tocó el
  usuario real `no-reply@olvidata.com.ar`.**

## Cobertura por criterio (PASS / FAIL / BLOCKED)

| Criterio | Resultado | Evidencia |
|---|---|---|
| D5 sigue cerrado tras el cambio a porcentaje (misma pantalla `Ventas/Editar.cshtml`) | **PASS** | Borrador reabierto: los 5 inputs llegan poblados (`3.000`, `4600.00`, `21.00`, `10.00`, `5.00`), subtotal $ 13.041,00; re-guardar sin tocar nada se acepta |
| Descuento/Recargo como % — recálculo **UI** | **PASS** | 3 × 4600 con 10% y 5% → la grilla muestra $ 13.041,00 en vivo |
| Descuento/Recargo como % — recálculo **servidor** (el que manda) | **PASS** | Persistido: `Subtotal=13041.00`, `TotalIVA=2738.61`, `Total=15779.61`. Coincide exacto con la UI |
| Límites 0% y 100% | **PASS** | desc 100%→$ 0,00; rec 100%→$ 27.600,00; 50/50→$ 10.350,00. Ninguno rompe |
| Rechazo de >100 y negativos — **client-side** | **PASS** | `min="0" max="100"`; `checkValidity()=false` con mensaje del navegador para 150 y -5 |
| Rechazo de >100 y negativos — **server-side** (POST manipulado) | **PASS** | 150, -5 y recargo 150 rechazados con "El descuento/recargo de 'X' debe estar entre 0 y 100%." y **sin persistir** |
| Producto con oferta vigente carga el precio de oferta | **PASS** | Producto 2491: lookup devuelve `precioOferta:4600` (lista 4871,24) y el input "Precio unitario" carga **4600**. Bug de esta ronda confirmado cerrado |
| PAT-016 (a) buscar por importe visible | **PASS** | 11/11 casos en Productos, Clientes, Ventas, Caja, Gastos, Entregas: es-AR (`15.779,61`), invariante (`7312.54`), substring (`81436`), entero |
| PAT-016 (b) buscar por fecha visible | **PASS** | Gastos `21/08/2026` → 2; Caja `24/08/2026` → 1; Ventas `25/08/2026` → 1 (coincide con lo que la grilla muestra) |
| PAT-016 (c) filtro de **columna** persiste al navegar y volver | **PASS** | Productos, Clientes, Gastos, Ventas: 4/4 |
| PAT-016 (c) **buscador global** persiste al navegar y volver | **FAIL en Productos** | 0/6 en Productos con espera de 1,2 s; 6/6 en Clientes/Gastos/Ventas. Ver **D14** |
| PAT-016 (d) "Limpiar filtros" deja todo vacío y no repone | **PASS** | 4/4 listados, verificado reentrando tras navegar |
| AFIP: botón deshabilitado con tooltip | **PASS** | `disabled=true` + title "AFIP no está configurado todavía — pendiente del certificado y CUIT real del cliente." Y el **backend rechaza igual** un POST manipulado con el mismo mensaje |
| D10 — campos de Cliente en el ABM | **PASS (cerrado)** | Domicilio/Localidad/Email/Notas presentes en Create, se guardan y vuelven poblados en Edit (cliente 2993) |
| D11 — decimal es-AR en input no numérico | **PASS (cerrado)** | `Entregas/Create?ventaId=8`: el hidden `VentaTotal` renderiza `15779.61` (invariante), no `15.779,61` |
| D12 — aterrizaje del Repartidor | **PASS (cerrado)** | Login de Repartidor → `/Entregas`, sin `AccessDenied` |
| D13 — redondeo comercial | **PASS (cerrado)** | `MidpointRounding.AwayFromZero` en los 6 puntos, incluido el computed `TotalPagos` del DTO |

## Regresión de lo que ya pasaba en la primera vuelta

| Área | Resultado |
|---|---|
| Permisos, 3 roles × 18 rutas | **54/54 PASS**. Sidebar coincide exacto con la autorización real en los 3 roles |
| 9 listados server-side sin 500 | **PASS** (Ventas, Clientes, Productos 112.485, Caja, Cierres, Mensual, Gastos, Entregas, Stock). El fix de `MH-001` sigue firme |
| Venta Facturada no editable | **PASS** — redirige a Details y el POST manipulado responde "ya fue facturada o anulada: no se puede editar." |
| Máquina de estados de Entrega | **PASS** — Pendiente → EnCamino → Entregada; botones exactos por estado; Entregada → EnCamino rechazada (queda en `Estado=3`) |
| Markup de Entrega 20% | **PASS** — base $ 1.000,00 → final $ 1.200,00 |
| Combo de repartidores | **PASS** — carga (era uno de los 5 call sites de `MH-001`) |
| Gastos → Egreso automático en Caja | **PASS** — gasto $ 2.500,75 genera el Egreso con fecha correcta |
| Guarda de fecha futura en Gasto | **PASS** — rechaza con "La fecha no puede ser futura." |
| Dashboard (D7) | **PASS** — "Ventas de hoy: 1 · $ 15.779,61", la venta correcta. Sin corrimiento de día |
| Errores JS / HTTP 500 en toda la corrida | **Ninguno** |

## Defectos nuevos de esta vuelta

### D14 — `minor` — El buscador global se pierde al volver a Productos (NO corregido, catalogado `LP-004`)

- **Pasos:** `/Productos` → tipear "2026" en el buscador global → esperar ~1,2 s → ir a `/Dashboard` → volver.
- **Síntoma medido:** el buscador vuelve **vacío** y la grilla sin filtrar. **0 de 6** intentos conservaron el
  filtro en Productos con espera de 1,2 s; **6 de 6** con espera de 4 s; **6 de 6** en Clientes (2.992 filas)
  con la misma espera de 1,2 s. Los filtros de **columna** persisten siempre.
- **Causa raíz:** el endpoint `Listar` escribe `Session["<Entidad>_Busqueda"]` en **cada draw**. DataTables
  dispara un draw por pulsación y aborta el XHR anterior del lado del cliente, pero el servidor sigue
  procesando las abortadas y **todas escriben Session**. Con 112k filas cada búsqueda tarda 2-2,6 s, así que
  las respuestas completan fuera de orden y gana la última en terminar — habitualmente un draw anterior con
  `search` vacío, que según la semántica de `FiltrosSessionHelper.Guardar` **borra** la key. Cronología
  medida: REQ `''` 2597ms / REQ `'2'` 2612ms / REQ `'2026'` 3332ms → RESP `''` 3137ms / RESP `'2'` 4843ms /
  RESP `'2026'` 5980ms.
- **Por qué NO se auto-corrigió:** es una condición de carrera de escritura en Session, no un error de lógica
  del helper, y hay más de una solución razonable (debounce de la escritura, descartar escrituras rancias con
  el contador `draw`, no persistir el buscador global). Toca infraestructura compartida por los 6 listados.
  **Escalado al Implementador.** El fix recomendado está en `LP-004.archivos_fix`: guardar el `draw` junto
  con los filtros y aplicar el lote solo si su `draw` es ≥ al último persistido — usa un dato que DataTables
  **ya manda**.
- **Nota:** el riesgo crece con el tamaño de la tabla, así que es invisible en los listados chicos y
  sistemático justo en el grande, que es donde recordar el filtro más le sirve al usuario.

### D15 — `minor` — Details mostraba el porcentaje como importe (CORREGIDO, auto-fix, catalogado `LP-005`)

- **Pasos:** venta con descuento 10% y recargo 5% → facturarla → `/Ventas/Details/{id}`.
- **Síntoma medido:** la fila mostraba `21,00 % | $ 10,00 | $ 5,00 | $ 13.041,00`. El 10% se rotulaba
  **"$ 10,00"**, como si fueran diez pesos. La contradicción es visible en la propia fila: con un descuento
  literal de $10 y recargo de $5 el subtotal sería $ 13.795,00, no $ 13.041,00.
- **Causa raíz:** el cambio de unidad se aplicó en la entidad, el Service, el DTO, el ViewModel y la vista
  **editable**, pero `Views/Ventas/Details.cshtml` quedó con el render anterior. Barrido incompleto: se
  cubrieron los puntos que **calculan** o **validan** y se pasó por alto el que solo **muestra**.
- **Por qué importa más de lo que parece:** es la pantalla de revisión de un comprobante **ya emitido**.
- **Fix:** encabezados a "Descuento %" / "Recargo %" y celdas a `@it.Descuento.ToString("N2") %`. Réplica
  exacta del criterio ya aplicado en `Editar.cshtml`; cero lógica de negocio nueva.
- **Verificación post-parche:** la fila pasa a `21,00 % | 10,00 % | 5,00 % | $ 13.041,00`. Subtotal, IVA
  ($ 2.738,61) y Total ($ 15.779,61) sin cambios.

### D16 — `informativo` — La migración de porcentaje no tiene backfill de datos

- `20260825005540_ItemVenta_DescuentoRecargoPorcentaje` es un `AlterColumn` puro `decimal(18,2)` →
  `decimal(5,2)` **sin ninguna conversión de datos**. Cualquier fila preexistente con `Descuento` como
  **importe** pasa a interpretarse como **porcentaje** (un descuento de $100 se vuelve 100%), y un importe
  > 999,99 no entra en `decimal(5,2)`.
- **Impacto real hoy: ninguno.** Verificado antes de aplicar: las 5 filas de `ItemsVenta` en `laplatense_dev`
  tenían `Descuento` y `Recargo` en 0, y Entrega 2 nunca se desplegó, así que no hay `ItemsVenta` con datos
  en ningún otro ambiente. Se anota porque el riesgo se materializaría si la migración se aplicara sobre
  una base donde ya se hubiera vendido con descuentos.

## Defectos heredados de la primera vuelta que siguen abiertos

| id | severidad | estado |
|---|---|---|
| **D8** — "Confirmar y facturar" no guarda el borrador y factura datos viejos | `major` | **Sigue abierto.** Hoy inocuo porque el botón está `disabled` y el backend rechaza sin certificado. **Bloqueante antes de cargar el certificado AFIP** |
| **D9** — `CajaMovimiento.Fecha` mezcla dos semánticas y la guarda de caja cerrada mira otro día | `major` | **Sigue abierto** y ahora **confirmado en la UI**: la corrida se hizo a las 23:00 ART (02:00 UTC), justo dentro de la ventana del defecto, y una venta hecha a las 22:44 del 24/08 se muestra en el listado de Ventas como **25/08/2026 01:44** — el día equivocado. `GastoService` sigue mezclando `DateTime.Today` (líneas 172 y 255) con `DateTime.UtcNow` (línea 226). Requiere definición del **día de negocio** por parte del cliente |

## Cobertura del catálogo cross-proyecto

Se ejecutaron los ids con superficie en los cambios de esta vuelta. Sin cambios respecto de la primera vuelta
salvo lo indicado:

| id | aplica | resultado | acción |
|---|---|---|---|
| `MH-001` | sí | **PASS** | Los 5 call sites siguen corregidos; 9 listados y el combo de repartidores sin 500 |
| `MH-003` | sí | **PASS** | Los límites 0-100 de Descuento/Recargo están en cliente **y** servidor; fecha futura de Gasto rechazada server-side |
| `MH-009` | sí | **FAIL parcial** | Familia de huso horario: D7 sigue cerrado en Dashboard, pero D9 sigue abierto y ahora visible en el listado de Ventas |
| `SG-001` / `LP-003` | sí | **PASS** | D5 sigue cerrado tras el cambio a porcentaje; D11 cerrado en `Entregas/Create` |
| `CRM-002` / `REG-010` / `KOI-003/005/006` | sí | **PASS** | Sidebar vs autorización real: 54/54 en 3 roles |
| `CRM-003` / `DN-001` / `DN-002` | sí | **PASS** | 9 listados server-side con orden dinámico, sin 500 |
| `REG-004` / `VSF-001` / `VSF-002` | sí | **PASS** | Máquina de estados de Entrega con botones derivados del estado real; transición inválida rechazada |
| `GAN-002` | sí | **informativo** | Migración sin backfill — ver **D16** |
| **`LP-004`** | sí | **nuevo** | Creado en este ciclo — ver **D14** |
| **`LP-005`** | sí | **nuevo, corregido** | Creado en este ciclo — ver **D15** |

## Auto-fixes aplicados en esta vuelta

| id catálogo | defecto | archivos tocados | resultado post-parche |
|---|---|---|---|
| `LP-005` (nuevo) | D15 — Details mostraba el % como importe | `FerreteriaLaPlatense.Web/Views/Ventas/Details.cshtml` (2 encabezados + 2 celdas) | build 0 errores; verificado por navegador: `10,00 %` / `5,00 %`, totales intactos |

**Sin commitear**, en el working tree, para revisión desde la conversación principal (mismo criterio que la
primera vuelta).

## Estado de `laplatense_dev` tras esta vuelta

Se suma a lo que ya había dejado la primera vuelta:

- Contraseña de los 3 usuarios QA reescrita a un valor conocido (`qa.super@`, `vendedor.qa@`, `repartidor.qa@`).
- **Venta 8 forzada a `Facturada` por SQL con CAE inventado** (`71234567890125`), igual que las 2 de la
  primera vuelta. **No es una venta facturada de verdad y no generó movimientos de Caja.**
- Cliente 2993 ("QA Ronda2 …"), 1 gasto de $ 2.500,75 con su Egreso en Caja, y la entrega 3 en estado
  `Entregada`.

## Riesgos de liberación

1. **AFIP sigue sin poder probarse de punta a punta.** Es el mismo riesgo de la primera vuelta y no se movió.
   Todo lo posterior a un CAE exitoso (descuento de stock real, asiento en cuenta corriente, ingreso
   automático en Caja) **nunca se ejecutó**. Mitigación adoptada en esta ronda: el botón está `disabled` con
   tooltip **y** el backend rechaza igual — un tester externo no puede tropezarse con el camino fiscal.
2. **D8 sigue siendo la bomba de tiempo atada a ese hito.** Corregirlo **antes** de cargar el certificado.
3. **D9 necesita una definición del cliente** (día de negocio de la caja). Ahora tiene síntoma visible: una
   venta de la noche aparece con la fecha del día siguiente. En una prueba con el cliente esto se va a
   reportar como bug de entrada.
4. **D14** degrada PAT-016 justo en el listado más grande. No corrompe datos; el usuario retipea.
5. **El hosting de producción no está en huso argentino** — sigue pendiente el barrido de
   `DateTime.Today`/`DateTime.Now` en el resto del sistema.
6. **Producción sigue con `Stock/HistorialListar` caído** (el fix de `MH-001` vive en `entrega-2`).
7. Las asunciones de negocio siguen sin confirmar con el cliente, con una menos: Descuento/Recargo **ya se
   resolvió como porcentaje**, alineado con el resto del estudio.

## Estado go/no-go

**GO para desplegar a un servidor de PRUEBAS con usuarios externos. NO-GO para producción.**

Fundamento del GO: los 4 defectos que la primera vuelta dejó abiertos como corregibles (D10, D11, D12, D13)
están cerrados y verificados por ejecución real; los 3 lotes de cambios nuevos funcionan de punta a punta
(el porcentaje calcula exacto en UI y servidor, valida en ambos lados y rechaza lo inválido sin persistir; la
oferta vigente carga bien; PAT-016 encuentra por importe, fecha, enum y etiqueta en los 6 listados); la
regresión no encontró **nada roto** de lo que ya pasaba (54/54 permisos, 9 listados sin 500, máquinas de
estado íntegras, Dashboard correcto); y no apareció **ningún** error de JS ni HTTP 500 en toda la corrida.
Los 2 defectos nuevos son `minor` y ninguno corrompe datos: uno ya está corregido y el otro hace que el
usuario retipee un filtro.

Condición de encuadre del GO: **es un ambiente de prueba, no de producción**, porque AFIP no está configurado
y el circuito fiscal completo nunca se ejecutó. Antes de que alguien externo lo use conviene:

1. Avisar que **facturar está deshabilitado a propósito** (el botón lo dice, pero conviene decirlo).
2. Cargar datos limpios: **borrar las 3 ventas con CAE inventado** (1, 3 y 8), que no tienen movimientos de
   Caja asociados y descuadran cualquier arqueo.
3. Asumir que **D9 va a reportarse** como "las ventas de la noche salen con la fecha de mañana".

Condiciones para el GO a producción (sin cambios respecto de la primera vuelta, más las nuevas):

1. Corregir **D8** antes de configurar el certificado AFIP.
2. Cerrar **D9** con Joaquín (definición del día de negocio).
3. Prueba end-to-end de AFIP en homologación, con el circuito completo posterior al CAE.
4. Resolver **D14** (o aceptarlo explícitamente).
5. Evaluar adelantar a producción el fix de `AjusteStockService` (`MH-001`), que arregla una pantalla hoy caída.

## Checklist de salida

- [x] `dotnet build FerreteriaLaPlatense.slnx` → 0 errores (inicial + post auto-fix).
- [x] Migración `ItemVenta_DescuentoRecargoPorcentaje` aplicada y verificada en `laplatense_dev`.
- [x] Verificación automatizada por navegador real sobre la app levantada.
- [x] D5 revalidado tras el cambio a porcentaje.
- [x] Descuento/Recargo %: UI, servidor, límites 0/100 y rechazo de inválidos (cliente y servidor).
- [x] Precio de oferta vigente al agregar un producto.
- [x] PAT-016 (a)(b)(d) en los 6 listados; (c) PASS salvo el buscador global de Productos (D14).
- [x] AFIP: botón `disabled` + tooltip + rechazo server-side.
- [x] D10, D11, D12, D13 verificados cerrados.
- [x] Regresión: 54/54 permisos, 9 listados sin 500, estados, Caja, Gastos, Entregas, Dashboard.
- [x] `LP-004` y `LP-005` creados en el catálogo cross-proyecto.
- [x] 1 auto-fix aplicado (D15) y verificado post-parche, **sin commitear**.
- [ ] **D8 pendiente — bloqueante antes de configurar AFIP.**
- [ ] **D9 pendiente — requiere definición de Joaquín.**
- [ ] D14 pendiente (no bloqueante).
- [ ] Limpiar los datos de prueba de `laplatense_dev` (3 ventas con CAE inventado).
- [ ] AFIP end-to-end en homologación.

---

# Entrega 2 — Ventas / CC Clientes / AFIP / Caja / Gastos / Entregas / Dashboard (QA, 2026-08-21)

Primera corrida real de QA sobre Entrega 2 (cierra el defecto informativo D4 de Etapa 3). Rama `entrega-2`,
ya reconciliada con producción. Base: `laplatense_dev` con las 5 migraciones aplicadas y el catálogo real
migrado (112.485 productos, 2.990 clientes, 8.276 códigos de barras alternos).

## Alcance funcional validado

Ventas (workflow Borrador→Facturada, carrito editable, escaneo de código de barras propio y alterno),
Cuenta corriente de clientes, Facturación AFIP (solo el camino de error controlado), Caja (movimientos,
cierre diario y mensual), Gastos (alta, R7, anulación con contramovimiento), Entregas a domicilio (máquina
de estados completa, R9), Dashboard Corte 1, y la matriz de permisos de los 3 roles.

## Verificación automatizada por navegador

El servidor MCP `playwright` de `.mcp.json` **no estaba conectado en esta sesión** (se declara explícitamente,
según `33-verificacion-automatizada-qa.instructions.md`). No se cayó al procedimiento manual: los binarios de
Chromium de Playwright ya estaban en la caché local, así que se automatizó igual conduciendo un navegador real
vía `playwright-core` desde Node contra la app levantada en `https://localhost:7200`. **Todos los casos de esta
memoria se ejecutaron contra el sistema real**, ninguno se dio por válido por lectura de código.

Prerequisito de entorno resuelto durante el ciclo: la contraseña del `SuperUsuario` de `laplatense_dev` había
sido rotada en la prueba del flujo de reset de contraseña del 2026-08-18, así que no había forma de entrar. Se
creó un usuario `qa.super@test.local` (rol SuperUsuario) **sin tocar el usuario existente**, más `vendedor.qa@`
y `repartidor.qa@` desde la propia pantalla de Usuarios.

## Build

`dotnet build FerreteriaLaPlatense.slnx` → **0 errores** (verificado 4 veces: inicial y después de cada
auto-fix). Advertencias: solo las preexistentes NU1902 de MailKit/MimeKit.

## Cobertura por historia de usuario

| Historia / criterio | Resultado | Evidencia |
|---|---|---|
| PF2 — editar precio/cantidad/IVA/descuento antes de facturar, sin anular ni recrear | **FAIL → PASS tras auto-fix** | Era D5 (blocker). Post-fix: cant 3→10, precio 1,27→2,50, IVA 21→10,5 recalcula a total $ 40,98 en el servidor |
| PF3 — cobro con tarjeta en 3/6 cuotas mostrando el recargo antes de confirmar | PASS | UI muestra `+10% ($ 10,00)` antes de confirmar; el server recalcula y lo suma al Total |
| PF7 — cierre de caja diario y mensual como reportes separados | **FAIL → PASS tras auto-fix** | Era D6 (blocker, HTTP 500 en ambos listados). Post-fix: cierre diario $ 1.751,25 / $ 91.500,50 y cierre mensual en su histórico |
| PF11 — el repartidor ve el listado completo de entregas | PASS | `/Entregas/Listar` con usuario Repartidor devuelve todas, sin filtro por usuario |
| PF13 — vender con stock sin verificar / negativo no bloquea | PASS | Ítems agregados con `Stock=0` y aviso "stock sin verificar", nunca bloqueo |
| PF15 — escanear código de barras agrega el producto al carrito | PASS | Código propio (`00000000523925`→ producto 11683) y **alterno** (`7793300423428`→ producto 44969) |
| R7 — gasto clasificado en caja chica **o** mensual, no ambos | PASS | 2 gastos con `TipoImpacto` excluyente, cada uno con su Egreso en Caja |
| R9 — repartidor ve todas las entregas | PASS | ver PF11 |
| Venta con pago a cuenta corriente | PARCIAL | La guarda de cobertura y la validación "CC exige cliente" PASS; el asiento en el ledger **no se pudo verificar** (depende de facturar, bloqueado por AFIP) |
| Facturación AFIP end-to-end | **BLOCKED** | Sin CUIT ni certificado del cliente. Sí se validó el camino de error controlado |
| Dashboard Corte 1 | **FAIL → PASS tras auto-fix** | Era D7. Nivel 1, nivel 3 y la card "próximamente" de nivel 2 renderizan bien |

## Matriz de casos ejecutados

**Permisos — 37/37 PASS.** Matriz completa de `/Dashboard`, `/Ventas`, `/Ventas/Nueva`, `/Clientes`,
`/Clientes/Create`, `/Caja`, `/Caja/Cierres`, `/Caja/Mensual`, `/Caja/MovimientoManual`, `/Gastos`,
`/Gastos/Create`, `/Entregas`, `/Entregas/Create` contra los 3 roles. Sin ningún acceso indebido ni 500 en
lugar de 403. El sidebar coincide **exactamente** con la autorización real de cada rol (cierra en caliente el
patrón REG-010/KOI-003/KOI-005/CRM-002):

- SuperUsuario: Dashboard, Ventas, Clientes, Productos, Stock, Marcas, Modelos, Categorías, Caja, Gastos, Entregas, Usuarios, Sistema, Notificaciones
- Vendedor: sin Caja/Gastos/Usuarios/Sistema
- Repartidor: solo Dashboard, Entregas, Notificaciones

**Ventas — 18 casos.** Lookup por código propio / alterno / inexistente / texto libre; alta de borrador por
escaneo; recálculo servidor; pago mixto efectivo + 3 cuotas; bloqueo por pagos insuficientes; bloqueo de venta
sin ítems; pago CC sin cliente rechazado; AFIP con error explícito sin descontar stock; cancelar borrador vía
botón real + SweetAlert2 (desaparece del listado y da 404); Facturada no editable; POST manipulado sobre una
Facturada rechazado server-side; refacturar una Facturada rechazado.

**Caja / Gastos — 14 casos.** Alta de gasto caja chica y mensual; Egreso automático en Caja; anulación con
contramovimiento de Ingreso fechado hoy; gasto anulado sigue visible; anular dos veces rechazado; movimiento
manual con origen "Ajuste"; cierre diario con totales correctos; gasto en día cerrado bloqueado; cierre
mensual con histórico.

**Entregas — 12 casos.** Alta desde venta Facturada con markup 20% (base 1.000 → final 1.200; base 500 → 600);
segunda entrega para la misma venta rechazada; combo de repartidores; R9; ciclo Pendiente → EnCamino →
Entregada; EnCamino → NoEntregada con motivo obligatorio → Reagendar → Pendiente; reagendar con fecha pasada
rechazado; transición inválida Entregada → EnCamino rechazada server-side.

**Listados DataTable server-side — 7 listados × varios ordenamientos.** `/Ventas/Listar`, `/Clientes/Listar`
(2.992 filas), `/Entregas/Listar`, `/Caja/Listar`, `/Caja/CierresListar`, `/Caja/MensualListar`,
`/Gastos/Listar`. Los 2 de Caja daban 500 (ver D6); el resto PASS, con ordenamiento real por cada columna
(cierra en caliente CRM-003).

## Cobertura de la máquina de estados

**Venta** (`Borrador → Facturada → Anulada`):

| Transición | Resultado |
|---|---|
| (alta) → Borrador | PASS |
| Borrador → Borrador (editar/re-guardar) | **FAIL → PASS tras auto-fix D5** |
| Borrador → cancelado (soft delete) | PASS — 404 y fuera del listado |
| Borrador → Facturada | **BLOCKED** por AFIP (se verificó que ante fallo queda en Borrador, sin descontar stock ni generar movimientos) |
| Borrador → Facturada sin ítems | PASS — rechazada |
| Borrador → Facturada con pagos insuficientes y sin CC | PASS — rechazada |
| Facturada → editar (POST manipulado) | PASS — rechazada |
| Facturada → Facturada (refacturar) | PASS — rechazada |
| Facturada → Anulada | N/A — es Entrega 3, no implementada |

**Entrega** (`Pendiente / EnCamino / Entregada / NoEntregada`): las 4 transiciones válidas PASS, las inválidas
rechazadas server-side, y **los botones de cada estado coinciden exactamente con las transiciones reales**
(Pendiente → solo "Iniciar recorrido"; EnCamino → "Marcar entregada" + "No entregada"; NoEntregada →
"Reagendar"; Entregada → ninguna). Cumple el patrón de `32-estandares-qa-implementador`.

## Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

48 ids. Resumen por resultado:

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001 | no | N/A | No hay `RowVersion` en las entidades de Entrega 2 |
| REG-002 | no | N/A | Sin variantes de producto (confirmado en Análisis) |
| REG-003, REG-005, REG-007 | sí | PASS | Select2 AJAX de producto y de cliente devuelven resultados con texto correcto |
| REG-004 | sí | PASS | Máquina de estados de Entrega y de Venta con botones derivados del estado real |
| REG-006 | sí | PASS | `CreditoCuotas` muestra el selector de cuotas y el % de recargo |
| REG-008 | sí | PASS | Escribir en Cantidad/Monto no pierde el foco (handlers `input`/`change` sin re-render de fila) |
| REG-009 | no | N/A | No hay cascada categoría→subgrupo en Entrega 2 |
| REG-010, KOI-003, KOI-005, KOI-006 | sí | PASS | Sidebar vs autorización real verificado en los 3 roles, sin links a controllers inexistentes |
| KOI-001 | sí | PASS | "Cancelar borrador" y "Anular gasto" con SweetAlert2 fuera del form ejecutan realmente |
| KOI-002, KOI-004 | no | N/A | Sin export Excel ni cierre de período de inversores en esta entrega |
| DN-001, DN-002 | sí | PASS | Listados con `Include` + orden dinámico + `Skip/Take` sin 500 |
| GAN-001 | sí | PASS | Guarda "al menos un ítem" se dispara de verdad (mensaje explícito, no efecto colateral) |
| GAN-002 | no | N/A | Sin backfill en las migraciones de esta entrega |
| GAN-003 | sí | PASS | Filas dinámicas de ítems/pagos se agregan por template JS en string, no por `<partial>` |
| GAN-004 | no | N/A | Sin `<datalist>` |
| VSF-001, VSF-002 | sí | PASS | Borrador tiene salida por cancelación; ninguna entidad queda sin transición de escape |
| CRM-001 | no | N/A | Sin audit trail por `SaveChanges` en el alcance |
| CRM-002 | sí | PASS | Ningún control de escritura visible para un rol sin la policy correspondiente |
| CRM-003 | sí | PASS | Ordenamiento por encabezado real en los 7 listados |
| CRM-004, CRM-005, CRM-006 | no | N/A | Sin bot ni scraping |
| **MH-001** | **sí** | **FAIL → corregido** | **Reaparición en 5 call sites — ver D6** |
| MH-002 | sí | PASS | Enums serializados como string (`"Ingreso"`, `"CajaChica"`, `"Borrador"`) |
| MH-003 | sí | PASS | `Gasto.Fecha` futura rechazada server-side; `Reagendar` con fecha pasada rechazado server-side |
| MH-004 | sí | PASS (con matiz) | La anulación de un gasto genera un Ingreso fechado hoy, por diseño explícito — mismo desglose que MH-004 describe, acá es deliberado y documentado |
| MH-005, MH-006 | no | N/A | Sin remito ni link público en esta entrega |
| MH-007 | no | N/A | Sin ajuste de apertura de CC |
| MH-008 | sí | PASS | Mensajes de medio de pago consistentes con el enum vigente |
| MH-009 | sí | **FAIL parcial** | Misma familia de huso horario — ver D7 |
| MH-010 | no | N/A | No se usa `maskMoney`; los importes son `<input type="number">` nativos |
| MH-011, MH-012, MH-013 | no | N/A | Notas de crédito y refacturación son Entrega 3 |
| SG-001 | sí | **FAIL → corregido** | Inputs numéricos vacíos posteados contra tipos de valor no nullables — ver D5 |
| LP-001 | sí | PASS | El recálculo ABC sigue filtrando `Estado == Facturada` tras el merge (no se perdió el fix de Etapa 3) |
| LP-002 | sí | PASS | El código de barras alterno resuelve en el buscador de Venta, no solo en Catálogo |
| **LP-003** | **sí** | **nuevo** | **Creado en este ciclo — ver D5** |
| ELV-001 | sí | PASS | Los 6 controllers de Entrega 2 tienen `[Authorize]` con policy explícita |
| ELV-002 | sí | PASS | `ClienteService.EditarAsync` reaplica la misma validación de unicidad que `CrearAsync` |

## Defectos detectados

### D5 — `blocker` — Un borrador de venta reabierto queda inutilizable (CORREGIDO, auto-fix)

- **Pasos:** Ventas → Nueva → agregar 2 ítems por escaneo → "Guardar borrador" → reabrir `/Ventas/Editar/{id}`.
- **Síntoma:** las filas muestran el producto correcto pero **todos** los inputs numéricos (Cantidad, Precio
  unit., % IVA, Descuento, Recargo) llegan **vacíos**, y los totales de pantalla muestran `$ 0,00` aunque la
  venta está bien guardada (`Total = 17,97` en la base). Si el vendedor vuelve a apretar "Guardar borrador",
  el Service rechaza con "La cantidad de 'BOLSAS DE CONSORCIO LA PLATENSE' debe ser mayor a 0." El borrador
  queda **imposible de editar y de re-guardar**: solo se puede cancelar o facturar con los valores originales.
- **Causa raíz:** el `value` de un `<input type="number">` tiene que ser un *valid floating-point number*
  (punto decimal siempre). Con la cultura fija `es-AR` de `Program.cs`, Razor renderizaba
  `value="@it.Cantidad"` como `value="3,000"` y `value="@it.PrecioUnitario"` como `value="1,27"` — el
  navegador descarta el value por inválido y deja el input vacío, sin ningún error visible. Es la contraparte
  de **salida** del problema que el proyecto ya tenía resuelto solo del lado de **entrada** con
  `InvariantDecimalModelBinderProvider`.
- **Impacto:** rompía PF2, el criterio de aceptación central y de mayor riesgo de toda la Entrega 2.
- **Por qué no lo detectó nadie antes:** la pantalla funciona perfecto al **crear** (las filas que agrega el JS
  vienen de un JSON, que serializa con punto) y solo se rompe al **reabrir**.
- **Fix:** helper `Func<decimal,string> num = v => v.ToString(CultureInfo.InvariantCulture)` en
  `Views/Ventas/Editar.cshtml`, aplicado a los 6 `value` de inputs numéricos. Los textos de solo lectura
  (subtotales, totales) siguen en es-AR, como corresponde.
- **Catalogado como `LP-003`** (nuevo) + sección preventiva nueva en `32-estandares-qa-implementador`.

### D6 — `blocker` — 4 endpoints caídos con HTTP 500 por el patrón MH-001 (CORREGIDO, auto-fix)

- **Pasos:** entrar a Caja → Cierres, o Caja → Mensual, o abrir el combo de repartidores de Entregas, o
  Stock → Historial de ajustes.
- **Síntoma:** `HTTP 500` — `InvalidOperationException: Expression '@usuarioIds' in the SQL tree does not have
  a type mapping assigned`.
- **Causa raíz:** `_context.Users.Where(u => usuarioIds.Contains(u.Id))` con `usuarioIds` como colección local
  de `string`. Es exactamente `MH-001`, ya catalogado y ya corregido dos veces (marihogar Sprint 1, La Platense
  Etapa 3). **Tercera aparición.**
- **Hallazgo que amplía el item del catálogo:** el error se dispara **también con la colección vacía** — se
  comprobó con 0 filas en `CierresCajaDiarios` y el endpoint devolvió 500 igual. O sea que estos listados
  estaban rotos desde el día 1, al 100% de las cargas, sin necesidad de que existiera ningún dato.
- **Alcance real — 5 call sites, uno de ellos en producción:**
  - `CajaMovimientoService.ListarCierresDiariosAsync` → 500 siempre (rompe PF7)
  - `CajaMovimientoService.ListarCierresMensualesAsync` → 500 siempre (rompe PF7)
  - `EntregaService.ListarRepartidoresAsync` → 500 siempre (el combo de repartidores no cargaba nunca)
  - `AjusteStockService.HistorialAsync` → 500 siempre — **esto es código de Entrega 1, ya desplegado a
    producción: la pantalla de historial de ajustes de stock estaba caída en producción sin que nadie lo
    hubiera reportado**
  - `EntregaService.ListarAsync` → latente: lo salvaba un `if (ids.Count == 0)`, iba a reventar con la primera
    entrega con repartidor asignado
- **Fix:** patrón canónico del catálogo en los 5 puntos — materializar `AspNetUsers` con `ToListAsync()` y
  filtrar en memoria con un `HashSet<string>`. Es seguro acá porque la tabla de usuarios es el personal del
  negocio (unidades, no miles).
- **Barrido posterior:** `grep` de `.Contains(` sobre Services y Controllers — todos los casos restantes son
  colecciones de `int` (seguras según la nota del propio item) o filtros en memoria.

### D7 — `major` — El Dashboard mostraba las ventas del día equivocado (CORREGIDO, auto-fix)

Es la confirmación del punto que Etapa 3 había dejado anotado en D4 como "observación colateral". **Es un bug
real, y se reprodujo.**

- **Pasos:** con dos ventas Facturadas, una del 21/08 22:00 ART y otra del 20/08 22:00 ART, abrir `/Dashboard`.
- **Síntoma:** "Ventas de hoy" mostraba **1 venta, $ 121,00** — que es la de **ayer**. La venta real de hoy
  ($ 40,98) **no aparecía**.
- **Causa raíz:** `DashboardService` armaba la ventana con `DateTime.Today` (día calendario del **servidor**)
  y la comparaba contra `Venta.Fecha`, que se guarda en UTC (`DateTime.UtcNow`). La ventana efectiva quedaba
  en ART `[21:00 de ayer, 21:00 de hoy)`: toda venta posterior a las 21:00 se contaba al día siguiente, y las
  de ayer a esa hora se contaban como de hoy. Afectaba "Ventas de hoy" y "Top productos del mes".
- **Agravante en producción:** el hosting real (SmarterASP/site4now) **no está en huso argentino** — el XML-doc
  de `ArgentinaTime` documenta offset `-07:00`. Ahí además cambia el día calendario de referencia, no solo el
  corte horario.
- **Fix:** usar `ArgentinaTime.HoyRangoUtc()` — helper que **ya existía en este mismo repo**, escrito
  precisamente para esta clase de bug — y convertir los bordes del mes a UTC para "Top productos". Es el mismo
  criterio que `ClasificacionAbcAutomaticaService` ya aplicaba bien y que se usó de referencia.
- **Verificación post-fix:** "Ventas de hoy" pasa a mostrar **1 venta, $ 40,98** (la correcta) y deja de
  contar la de ayer.
- **No se tocó** `ObtenerGastosMesPorCategoriaAsync`: `Gasto.Fecha` es una fecha calendario pura (`dto.Fecha.Date`,
  cargada por el usuario), así que compararla contra `DateTime.Today` es correcto. Cambiarlo habría **introducido**
  un bug.

### D8 — `major` — "Confirmar y facturar" no guarda el borrador: factura datos viejos en silencio (NO corregido)

- **Pasos:** abrir un borrador guardado, cambiar la cantidad de un ítem en la grilla (sin apretar "Guardar
  borrador") y apretar "Confirmar y facturar" → confirmar en el SweetAlert2.
- **Síntoma medido:** la pantalla mostraba **$ 76,84** (cantidad 50) y el sistema facturó sobre **$ 1,54**
  (cantidad 1). La edición en curso se descarta sin ningún aviso.
- **Causa raíz:** `submitAccion()` en `Views/Ventas/Editar.cshtml` arma un form nuevo con **solo el token
  antiforgery** y postea a `ConfirmarYFacturar/{id}`; nunca envía el estado del formulario ni dispara un
  guardado previo. El server factura lo último persistido.
- **Por qué importa:** hoy es inocuo porque AFIP no está configurado y la emisión siempre falla. **En cuanto
  se cargue el certificado real, esto emite un comprobante fiscal con un importe distinto al que el vendedor
  tenía en pantalla** — y un comprobante fiscal emitido no se corrige, se anula con nota de crédito (que es
  Entrega 3, todavía no implementada).
- **Por qué NO se auto-corrigió:** hay más de una solución razonable (guardar y después facturar en un solo
  paso; bloquear "Confirmar" mientras el formulario esté sucio; pedir confirmación explícita) y la elección
  cambia el flujo de trabajo del vendedor sobre el camino fiscal. Es una decisión de diseño, no la réplica de
  un fix ya validado. **Escalado al Implementador.**
- **Recomendación:** que "Confirmar y facturar" ejecute primero el `GuardarBorrador` con el estado actual del
  form y solo continúe si el guardado fue exitoso.

### D9 — `major` — `CajaMovimiento.Fecha` mezcla dos semánticas y la guarda de "caja cerrada" mira otro día (NO corregido)

- **Evidencia (revisión de código, confirmada contra el comportamiento real):**
  - `VentaWorkflowService` escribe el movimiento de una venta con `Fecha = DateTime.UtcNow` → un **instante UTC**.
  - `GastoService` y `RegistrarMovimientoManualAsync` escriben `Fecha = dto.Fecha.Date` → una **fecha calendario**
    a medianoche.
  - `CajaController` cierra y resume el día con `DateTime.Today` (local), pero `VentaWorkflowService` (línea 334)
    y `GastoService.AnularAsync` consultan la guarda con `DateTime.UtcNow.Date`.
- **Consecuencias:** (a) una venta de las 22:00 ART cae en la caja del día siguiente, mientras un gasto cargado
  esa misma noche cae en el día correcto — el arqueo diario mezcla días; (b) entre las 21:00 y las 00:00 ART
  (7 horas por día en el servidor de producción, que está en huso Pacífico) `DateTime.UtcNow.Date` y
  `DateTime.Today` son **días distintos**, así que después de cerrar la caja el sistema **no bloquea** una
  venta nueva, que es justamente lo que la guarda existe para impedir.
- **Por qué NO se auto-corrigió:** alinearlo exige definir cuál es el **día de negocio** (¿a qué día pertenece
  una venta de las 22:00? ¿el cierre corta a medianoche o al cierre del local?). Es una regla de negocio que
  tiene que confirmar el cliente, no algo que QA pueda inferir. **Escalado al Implementador + pregunta abierta
  para Joaquín.**

### D10 — `minor` — Los 4 campos de Cliente de Etapa 3 no existen en el ABM (NO corregido)

- `Cliente` tiene `Domicilio`, `Localidad`, `Email` y `Notas` en la entidad y en la base, y la migración los
  cargó con datos reales: **2.739 clientes con domicilio, 1.082 con localidad, 100 con email**. Pero
  `ClienteFormViewModel` y las vistas Create/Edit de Entrega 2 solo exponen Nombre / CUIT-DNI / Teléfono /
  Condición de IVA. Los datos migrados son **invisibles e ineditables** desde la aplicación.
- **No hay pérdida de datos:** `ClienteService.EditarAsync` asigna solo los 4 campos mapeados, así que editar
  un cliente migrado **preserva** los otros 4. Verificado por lectura del Service.
- Es un gap de alcance entre Etapa 3 (agregó los campos) y Entrega 2 (dueña de la pantalla), no una regresión
  del merge: la rama de producción no tiene pantalla de Clientes. Se reporta sin corregir porque agregar campos
  a un ABM es alcance funcional, no un fix.
- **Nota operativa:** `Entregas/Create` pide la dirección a mano teniendo el domicilio del cliente ya migrado
  en la base — precargarlo sería una mejora obvia.

### D11 — `minor` — Los decimales renderizados en es-AR sobre inputs no numéricos se parsean ×100 (NO corregido)

- **Evidencia:** en `Entregas/Create` el hidden `VentaTotal` de una venta de $ 40,98 se renderiza como
  `value="40,98"`. `InvariantDecimalModelBinder` intenta `decimal.TryParse(value, NumberStyles.Any,
  InvariantCulture, ...)` **primero**, donde la coma es separador de **miles**: `"40,98"` entra como **4098**.
- **Impacto hoy: ninguno.** `VentaTotal` es solo informativo y no se persiste. Se reporta porque es el hermano
  silencioso de D5 (mismo render culture-dependiente, falla opuesta) y porque cualquier campo decimal futuro
  que se renderice así y sí se persista va a corromperse ×100 sin ningún error.
- Documentado dentro de `LP-003` (`nota_generalizacion`) y en la sección preventiva de
  `32-estandares-qa-implementador`.

### D12 — `minor` — El Repartidor aterriza en "Acceso denegado" en cada login (NO corregido)

- Al iniciar sesión, `AccountController` redirige a `Stock/Index`, pantalla a la que el rol `Repartidor` no
  tiene acceso: el resultado observado es `.../Account/AccessDenied?ReturnUrl=%2FStock`. Es el **único** rol
  cuya pantalla principal (Entregas) no es la del redirect.
- **Recomendación:** redirigir según rol (Repartidor → `Entregas/Index`) o mandar a `Dashboard`, accesible para
  todos. No se corrige por cuenta propia porque el redirect a Stock fue un pedido explícito de Joaquín
  (2026-08-10) y cambiarlo es una decisión suya.

### D13 — `informativo` — Redondeo bancario en el IVA por línea

- `Math.Round(x, 2)` sin `MidpointRounding` usa redondeo bancario (*to even*). Con IVA 10,5% sobre $ 25,00 el
  sistema calcula $ 2,62; el redondeo comercial habitual (*away from zero*) daría $ 2,63.
- Es consistente en todo el cálculo (incluido el `ImporteTotal` que se manda a AFIP), así que no genera
  descuadres internos. Se deja anotado porque la convención de facturación en Argentina suele ser
  *away from zero* y es una decisión del cliente, no de QA.

## Auto-fixes aplicados por QA

| id catálogo | defecto | archivos tocados | resultado post-parche |
|---|---|---|---|
| `LP-003` (nuevo) | D5 — borrador reabierto inutilizable | `FerreteriaLaPlatense.Web/Views/Ventas/Editar.cshtml` (helper `num` + 6 `value`) | build 0 errores; verificado por navegador: inputs poblados, total $ 17,97, re-guardado OK, PF2 recalcula bien |
| `MH-001` (3ª aparición) | D6 — 500 por `IN` de colección local de string | `CajaMovimientoService.cs` (×2), `EntregaService.cs` (×2), `AjusteStockService.cs` | build 0 errores; los 5 endpoints pasan de 500 a 200 con datos correctos |
| `MH-009` / familia huso horario | D7 — Dashboard con el día equivocado | `DashboardService.cs` (`ArgentinaTime.HoyRangoUtc()` + bordes del mes en UTC) | build 0 errores; "Ventas de hoy" pasa de $ 121,00 (ayer) a $ 40,98 (hoy) |

Ninguno introduce lógica de negocio nueva: D5 y D6 replican soluciones ya validadas del catálogo, y D7 usa un
helper que ya existía en este mismo repositorio y que otro servicio del proyecto ya usaba correctamente.

## Estado de la base de desarrollo tras el ciclo

`laplatense_dev` quedó con datos de prueba de QA que conviene conocer antes de la próxima corrida:

- Usuarios nuevos: `qa.super@test.local`, `vendedor.qa@test.local`, `repartidor.qa@test.local`.
- **2 ventas forzadas a `Facturada` por SQL directo, con CAE inventado** (`71234567890123`/`...124`). Fue la
  única forma de habilitar Entregas y Dashboard, porque `ConfirmarYFacturar` exige un CAE real de AFIP. **No
  son ventas facturadas de verdad y no generaron movimientos de Caja** — hay que borrarlas antes de cualquier
  prueba de Caja que dependa del ingreso automático por venta.
- 2 gastos, 1 movimiento manual, el cierre diario del 21/08 y el cierre mensual de 08/2026, 2 entregas, 3
  clientes de prueba y algunos borradores de venta.

## Riesgos de liberación

1. **AFIP sigue sin poder probarse de punta a punta** (sin CUIT ni certificado del cliente). Es el riesgo
   principal y no se movió: todo lo que ocurre *después* de un CAE exitoso — descuento de stock real, asiento
   en la cuenta corriente del cliente, ingreso automático en Caja — **nunca se ejecutó**. Lo único validado es
   que ante el fallo no se toca nada y la venta queda en Borrador reintentable.
2. **D8 es una bomba de tiempo atada a ese mismo hito.** Hoy no hace daño porque AFIP falla siempre; el día que
   se configure el certificado, la primera venta que se facture sin guardar sale con el importe equivocado.
   **Corregir D8 antes de cargar el certificado, no después.**
3. **D9 (día de negocio de la caja) necesita una definición del cliente**, no una decisión técnica. Mientras no
   se cierre, el arqueo diario puede mezclar días y la guarda de caja cerrada tiene un agujero de varias horas.
4. **El hosting de producción no está en huso argentino.** D7 se corrigió en el Dashboard, pero conviene un
   barrido de `DateTime.Today`/`DateTime.Now` en el resto del sistema antes de desplegar, con el mismo criterio.
5. **D6 dejó al descubierto que hay código de Entrega 1 caído en producción** (`Stock/HistorialListar`). Ya está
   corregido en esta rama, pero **el fix vive en `entrega-2`**: producción sigue rota hasta que se despliegue.
   Conviene evaluar llevar ese fix puntual a la rama de producción sin esperar a toda la Entrega 2.
6. La cuenta corriente de clientes quedó validada solo en sus guardas de entrada; el ledger real depende de
   facturar.
7. Las asunciones de negocio que el Implementador dejó abiertas **siguen sin confirmar** con el cliente:
   Descuento/Recargo de `ItemVenta` como monto y no porcentaje, mecánica del recargo de cuotas, markup de
   Entrega sobre el costo base (no sobre el valor del producto), cierre de caja bloqueando ventas del día, y
   acceso del Vendedor a Caja/Gastos. Ninguna es verificable por QA: son decisiones del cliente.

## Estado go/no-go

**GO CONDICIONADO para merge de `entrega-2`. NO-GO para producción.**

Fundamento: los tres bloqueantes/mayores encontrados por ejecución real están corregidos y verificados, el
build está limpio, los permisos y las dos máquinas de estados son sólidos, y el resto del alcance (Caja,
Gastos, Entregas, Dashboard) funciona de punta a punta. Pero **la Entrega 2 se había declarado "funcionalmente
terminada" con dos blockers que rompían su propio criterio de aceptación central (PF2) y dejaban 4 endpoints
en 500** — incluido uno ya desplegado a producción. Eso confirma, por segunda etapa consecutiva, el costo de
cerrar sin ejecutar la aplicación.

Condiciones para el GO a producción:

1. Corregir **D8** antes de configurar el certificado AFIP (bloqueante para producción).
2. Cerrar **D9** con Joaquín (definición del día de negocio de la caja).
3. Prueba end-to-end de AFIP en homologación, con el circuito completo posterior al CAE.
4. Confirmar con el cliente las asunciones del punto 7 de riesgos.
5. Evaluar adelantar a producción el fix de `AjusteStockService` (D6), que arregla una pantalla hoy caída.

## Checklist de salida para merge

- [x] `dotnet build FerreteriaLaPlatense.slnx` → 0 errores (4 veces: inicial + tras cada auto-fix).
- [x] Verificación automatizada por navegador real ejecutada sobre la app levantada contra `laplatense_dev`.
- [x] Matriz de permisos de los 3 roles (37 casos) y sidebar vs autorización real.
- [x] Máquina de estados de Venta y de Entrega, transiciones válidas e inválidas, incluidas por POST manipulado.
- [x] 7 listados DataTable server-side sin 500, con ordenamiento real por columna.
- [x] Catálogo cross-proyecto ejecutado (48 ids) y cobertura reportada.
- [x] 3 defectos corregidos con auto-fix y verificados post-parche (D5, D6, D7).
- [x] `LP-003` creado; `MH-001` ampliado con la nota de la 3ª aparición.
- [x] 2 secciones preventivas nuevas en `32-estandares-qa-implementador.instructions.md` (MH-001 y LP-003).
- [x] D4 de Etapa 3 cerrado (Entrega 2 ya pasó por el gate de QA).
- [ ] **D8 pendiente — bloqueante antes de configurar AFIP.**
- [ ] **D9 pendiente — requiere definición de Joaquín.**
- [ ] D10, D11, D12, D13 pendientes (no bloqueantes).
- [ ] Limpiar los datos de prueba de `laplatense_dev`, en especial las 2 ventas con CAE inventado.
- [ ] AFIP end-to-end en homologación (sigue bloqueado por el certificado del cliente).

---

# Etapa 3 — Migración de catálogo (QA, 2026-08-17)

## Alcance funcional validado

Rama `migracion-catalogo`, cambios **sin commitear**, revisión pre-merge de los ítems de app de la
Etapa 3 (ítems 2 a 6 del WBS): `CodigoProveedorProducto`, `Proveedor` mínimo, extensión de
`Producto`/`Cliente`, `ICatalogoMigracionService`, `IClasificacionAbcAutomaticaService`, pantallas de
importación (`Views/MigracionCatalogo/*`, 4 vistas) y de excepciones.

**Fuera de alcance de esta validación** (no es código de esta etapa): el ítem 1 del WBS (herramienta
batch de extracción/limpieza contra el backup real) y el ítem 7 (carga a producción). Entregas 1 y 2 no
se revalidaron: solo se verificó que esta etapa no las rompa (regresión puntual).

**Metodología: sin ejecución en caliente.** No hay base con la migración aplicada — el Implementador
generó `EntregaTres_MigracionCatalogo` y **no la aplicó a ninguna base**. Evidencia = lectura completa
de código por capa + `dotnet build`. Los casos que exigen UI/datos reales quedan como procedimiento
manual para Joaquín (ver "Pruebas manuales pendientes").

## Build

`dotnet build FerreteriaLaPlatense.slnx` → **Compilación correcta, 0 Errores**. 9 advertencias, todas
preexistentes y ajenas a Etapa 3: 8×NU1902 (MailKit/MimeKit) + 1×CS0114 (`HomeController.StatusCode`,
ya documentada en el QA de Entrega 1). Verificado antes y después de los dos auto-fixes.

## Cobertura por criterio de aceptación (PASS/FAIL/BLOCKED)

| Criterio de aceptación (origen) | Resultado | Evidencia |
|---|---|---|
| Dedup de nombre: conservar el de venta más reciente en `VentaItem`, respaldo `FechaModificacionPrecio` (analista, "Regla de deduplicación de nombres — versión final") | **N/A en esta etapa** | Es el paso 1 del flujo 10 (extracción/limpieza batch), ítem 1 del WBS explícitamente **no implementado**. El importador recibe un dataset ya deduplicado y no tiene forma de aplicar la regla (el formato de archivo no trae `FechaModificacionPrecio` ni historial de ventas del legacy). Queda como criterio a validar cuando se construya la herramienta. |
| Dedup de `articuloProveedor` por última importación con `Procesado=1` y `ArticuloKey` no nulo (analista) | **N/A en esta etapa** | Ídem: paso 1. La hoja `CodigosPorProveedor` ya llega conciliada; el importador solo valida unicidad del par `(proveedor, código)` dentro del archivo y contra la base. |
| Exclusión de productos sin nombre | **PASS** | `CatalogoMigracionService.LeerProductos`: excepción **bloqueante** "El producto no tiene nombre. No se importa." y `ProductosOmitidos++`. Cubre el caso real del legacy (3.203 artículos con nombre vacío y `Activo=1`), que la regla "excluir inactivos" no filtraba. |
| Exclusión de productos con precio de venta 0 | **PASS** | Ídem, guard `!precioVenta.HasValue \|\| precioVenta.Value <= 0` → bloqueante. |
| Exclusión de productos inactivos | **N/A en esta etapa** | El formato de intercambio no tiene columna `activo` por diseño: el filtro de `Activo=0` (20.536 filas) corresponde al paso 1. Decisión coherente, pero conviene dejarla explícita para que nadie espere que el importador la aplique. |
| Producto sin categoría válida → "Sin categoría" en vez de bloquear (analista) | **PASS** | Excepción **informativa** + `CatalogoPorDefecto.Categoria`. Mismo criterio aplicado a marca y modelo. |
| ABC por Pareto 12 meses sobre `VentaItem`, ventana móvil configurable | **PASS con defecto corregido** | `ClasificacionAbcAutomaticaService.RecalcularAsync`: ventana `MesesVentana` (appsettings + parámetro de pantalla), `GroupBy` en base de datos, piso en 0 para netos negativos, cortes 80/95 configurables y validados. **Defecto D1 detectado y corregido por QA**: la agregación no filtraba `Venta.Estado`, así que los borradores contaban como venta (ver Defectos). |
| La ventana ABC se calcula en la zona horaria correcta (riesgo declarado por el Implementador) | **PASS** | Confirmado en el código final, no solo en el relato de cierre: `hastaUtc = DateTime.UtcNow`, `desdeUtc = hastaUtc.AddMonths(-meses)`, comparados contra `Venta.Fecha`, que se persiste en UTC (`Venta.Fecha = DateTime.UtcNow` en la entidad). La conversión a hora Argentina (`ArgentinaTime.From`) se aplica **solo** a `FechaDesde`/`FechaHasta` del DTO, para mostrar. El bug de comparar columna UTC contra `ArgentinaTime.Now` **no** está presente. |
| `ClasificacionABCSugerida` nunca pisa `ClasificacionABC` (R10, diseñador flujo 10 punto 3) | **PASS** | Triple verificación: (a) el recálculo por lote solo asigna `entidad.ClasificacionABCSugerida`; (b) `ProductoService.EditarAsync/CrearAsync` escribe `ClasificacionABC` (campo manual del ABM) y **no** la sugerida, con comentario explícito; (c) el único camino sugerida→manual es `AceptarSugerenciaAsync`, invocado por `ProductosController.AceptarClasificacionAbcSugerida` (POST + antiforgery + `RequireAdministracion` + confirmación SweetAlert2), que además rechaza el caso "ya coinciden" y "sin sugerencia". |
| Idempotencia: reimportar el mismo archivo da 0 altas y no duplica | **PASS (por revisión de código)** | Claves de identidad: `Producto` por `Codigo`; `Cliente` por `CuitDni`, y si no lo trae por nombre exacto **solo contra clientes sin CUIT** (evita borrarle el CUIT a un homónimo); `CodigoProveedorProducto` por `(ProveedorId, CodigoDelProveedor)`. Todas las consultas de matcheo usan `IgnoreQueryFilters()`, así que un registro soft-deleted se revive en vez de chocar con el índice único (MySQL no distingue soft-deleted en un índice único). En la 2ª corrida: productos → `EsAlta=false`; códigos → `yaMapeados` contiene la clave → `Actualizaciones`; clientes → `porCuit`/`porNombreSinCuit` matchean → `Actualizaciones`. Los catálogos (Marca/Modelo/Categoría/Proveedor) ya existen → `faltantes=0`. **Verificación funcional pendiente** (requiere base). |
| La reimportación no pisa `Stock` ni `ClasificacionABC` manual | **PASS** | En el upsert de `ProcesarProductosAsync` se asignan exclusivamente `Nombre`, `MarcaId`, `ModeloId`, `CategoriaId`, `PrecioCompra`, `PrecioVenta`, `PorcentajeIVA`, `UnidadVenta`, `Bonificacion`, `ClasificacionABCSugerida`, `CodigoBarras`. **No** se tocan `Stock`, `StockVerificado`, `StockMinimo`, `ClasificacionABC`, `PrecioConDescuento`, `UnidadCompra`, `FactorConversion`. Decisión de diseño correcta y deliberada: el import escribe por `DbContext` y no por los Services de negocio, justamente para que estos no estampen valores propios. |
| No se puede confirmar el import sin revisar el reporte de excepciones (diseñador, "Validaciones de UI") | **PASS** | Doble barrera, no solo UI: la vista deshabilita el botón y muestra el aviso, y `MigracionCatalogoController.Confirmar` repite el guard server-side (`TotalExcepciones > 0 && !ExcepcionesFueronRevisadas(token)` → redirect con mensaje). La marca se setea al abrir `Excepciones` y vive en `Session` (registrada y con `UseSession()` antes del middleware de endpoints). Un archivo sin excepciones no exige abrir el reporte — interpretación razonable del criterio. |
| Archivo con hoja o columna obligatoria faltante se rechaza completo, sin importar nada | **PASS** | `ObtenerHoja`/`LeerEncabezado` lanzan `ArchivoMigracionInvalidoException` con el detalle de lo que falta; `PrevisualizarAsync` la captura, descarta el staging y devuelve `CreateError`. No hay persistencia posible antes de esa validación. |
| Permisos: todo lo nuevo detrás de `RequireAdministracion` | **PASS** | Verificado controller por controller, no por el reporte del Implementador: `MigracionCatalogoController` con `[Authorize(Policy="RequireAdministracion")]` **a nivel de clase** (cubre las 7 acciones, incluidas `ExcepcionesListar` y `ExportarExcepciones`); `StockController.RecalcularClasificacionAbc` y `ProductosController.AceptarClasificacionAbcSugerida` con el atributo a nivel de acción (sus clases son `RequireCatalogoConsulta`, que incluye Vendedor — el atributo de acción es imprescindible y está). La policy resuelve a SuperUsuario+Administrador; el link de sidebar usa exactamente `User.IsInRole("SuperUsuario") \|\| User.IsInRole("Administrador")`. |
| `Proveedor` no rompe nada existente y su migración es puramente aditiva | **PASS** | `20260817164053_EntregaTres_MigracionCatalogo`: solo `AddColumn` ×6 (todas `nullable: true`) + `CreateTable` ×2 + `CreateIndex` ×3. **Ningún `AlterColumn`, `DropColumn` ni cambio sobre tablas/columnas de Entregas 1/2.** FKs `Restrict` (no cascada destructiva). `Down()` es el reverso limpio. `Proveedor` no tiene ABM, ni sidebar, ni se referencia desde ninguna entidad preexistente: solo `CodigoProveedorProducto` (tabla nueva) la apunta. Riesgo real es de coordinación futura (el módulo de Compras debe ampliarla, no recrearla), ya documentado en el XML-doc de la entidad. |

## Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Cargado completo (43 ids, incluye el LP-001 creado en este ciclo). Mapeo contra los módulos tocados por
Etapa 3. Los ids ya marcados N/A en el QA de Entrega 1 por módulo inexistente que siguen sin superficie
en esta etapa se agrupan al final.

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001 (RowVersion MySQL) | no | N/A | El proyecto no usa `RowVersion` ni control de concurrencia optimista en ninguna entidad (grep sobre Domain/Data: 0 hits). Las 2 entidades nuevas heredan `SoftDestroyable`, sin token de concurrencia. |
| REG-002 / REG-006 (campos condicionales de un select) | no | N/A | Ningún select nuevo de esta etapa condiciona campos obligatorios adicionales. |
| REG-003 / REG-005 / REG-007 / REG-009 (Select2 / autocomplete AJAX / cascada) | no | N/A | Sin Select2 ni autocomplete en las vistas nuevas ni en los bloques agregados a `Productos`/`Clientes` (grep: 0 hits). Los combos son `<select>` poblados server-side. |
| REG-004 / KOI-004 / VSF-001 / VSF-002 (botones derivados del estado real, transiciones completas) | no | N/A | Esta etapa no agrega máquina de estados ni botones de transición. El flujo de import es lineal (subir → previsualizar → confirmar), sin estados persistidos. |
| REG-008 (recálculo de UI sin perder foco) | no | N/A | Sin grillas dinámicas con recálculo por `input`/`keyup` en las vistas nuevas. |
| REG-010 / KOI-003 / KOI-005 / KOI-006 (sidebar vs autorización real) | **sí** | **PASS** | Verificado por revisión de código, los 4 puntos del checklist: el controller existe (`MigracionCatalogoController`), la ruta del link coincide (`asp-controller="MigracionCatalogo"` / `asp-action="Index"`, acción `Index()` presente), el atributo de autorización es el esperado (`RequireAdministracion` a nivel de clase) y la condición de roles del link es idéntica a la de la policy. Sin links huérfanos ni roles sin link. |
| KOI-001 (SweetAlert2 fuera del `<form>`) | **sí** | **PASS** | `Productos/Edit.cshtml`: el botón "Aceptar sugerencia" está **dentro** del form de edición pero debe postear a **otro** action — se resuelve con `btn-swal-confirm` + `data-form-id="formAceptarSugerencia"` y un `<form>` separado, **no anidado**, fuera del form principal. Es exactamente el patrón que KOI-001 exige. El diálogo avisa además que se pierden los cambios sin guardar. |
| KOI-002 (falta export a Excel) | **sí** | **PASS** | El reporte de excepciones tiene `ExportarExcepciones` (botón + action + `IExportService`), con encabezados en español. |
| DN-001 / DN-002 (DataTable server-side + Include de colección) | **sí (por patrón)** | **PASS** | El listado nuevo (`ExcepcionesListar`) es server-side pero **no toca EF**: filtra/ordena/pagina en memoria sobre el JSON de staging, así que la causa raíz (2+ `Include` de colección + orden dinámico + `Skip`/`Take`) no puede darse. Los listados EF de `Stock`/`Productos` no se modificaron. |
| CRM-003 (DataTable ignora `order[0][column]`) | **sí** | **PASS** | `ListarExcepcionesAsync` implementa el ordenamiento server-side por `SortColumn`/`SortDirection` con `switch` sobre las 5 columnas reales, y `DataTableRequestHelper.Parse` sí lee `order[0][column]` → `columns[i][data]` → `order[0][dir]`. Los nombres del `switch` coinciden con los `data` declarados en la vista. |
| CRM-002 (control visible para un rol que la acción rechaza) | **sí** | **PASS** | El botón "Aceptar sugerencia" está envuelto en `User.IsInRole("SuperUsuario") \|\| User.IsInRole("Administrador")`, coincidente con `RequireAdministracion` de la acción. Defensa en profundidad correcta en ambos lados. |
| GAN-001 (guard "al menos un ítem" sobre lista dinámica) | no | N/A | Sin listas dinámicas bindeadas por índice en esta etapa. |
| GAN-003 (`<script type="text/x-template">` con Tag Helper) | no | N/A | Sin templates JS en las vistas nuevas (grep: 0 hits). |
| GAN-004 (`<datalist>` nativo) | no | N/A | Sin `<input list>`/`<datalist>`. |
| GAN-002 / VSF-001 (backfill que no filtra por estado de la entidad relacionada) | **sí (por patrón)** | **FAIL → corregido** | Antecedente conceptual del defecto **D1**: un cálculo masivo que agrega filas hijas sin considerar el estado del documento padre. Ver Defectos y el ítem nuevo **LP-001**. |
| **MH-001 (IN sobre colección local de string en MySQL/EF Core 10)** | **sí** | **FAIL → corregido** | **Reaparición real del patrón catalogado.** Dos `Where(...Contains(...))` sobre `List<string>` locales en `CatalogoMigracionService`, ambos en el camino de persistir. Ver Defectos (**D2**). |
| MH-002 (enum serializado como int rompe el badge) | **sí** | **PASS** | `ExcepcionMigracionDto.Seccion` es `string` y `Bloqueante` es `bool`; el `render` de la vista los interpreta correctamente. Sin enums crudos en el JSON de la grilla. |
| MH-003 (validación solo client-side) | **sí** | **PASS** | El guard de "revisó el reporte de excepciones" y el rango de la ventana ABC (1-120 meses) están **los dos** en cliente y en servidor (`RecalcularAsync` revalida el rango y los cortes Pareto; `Confirmar` revalida la revisión del reporte). |
| MH-005 (endpoint no revalida estado server-side) | **sí** | **PASS** | `Confirmar`, `Excepciones`, `ExcepcionesListar` y `ExportarExcepciones` revalidan el token contra el staging en cada request y devuelven un mensaje de negocio si venció; el token se valida como GUID antes de construir la ruta (previene path traversal). |
| MH-009 (fecha calendario pura desplazada por conversión de huso) | **sí** | **PASS** | Las fechas nuevas (`FechaAnalisis`, `FechaDesde`/`FechaHasta` del ABC) se renderizan server-side con `ToString("dd/MM/yyyy HH:mm")` en Razor, no vía JSON+moment.js, así que la causa raíz no aplica. |
| MH-010 (maskMoney no dispara `input`) | no | N/A | Sin campos de dinero editables en las pantallas nuevas (los importes del preview son solo lectura). |
| SG-001 (inputs opcionales vacíos contra ViewModel no nullable) | **sí** | **PASS** | Los campos nuevos de `ProductoFormViewModel` (`Bonificacion`) y `ClienteFormViewModel` (`Domicilio`/`Localidad`/`Email`/`Notas`) son todos `string?`; `RecalculoClasificacionAbcViewModel.MesesVentana` es `int` **no** nullable pero tiene default 12 y el input nunca se renderiza vacío. Sin grillas de inputs indexados. |
| KOI-006, MH-004, MH-006, MH-007, MH-008, MH-011, CRM-001, CRM-004, CRM-005, CRM-006, REG-002…REG-009 (módulos sin superficie en esta etapa: Compras/OC, Caja mensual, Remitos, Bot/CRM, AFIP NC) | no | N/A | Módulos no tocados por Etapa 3 (varios todavía no implementados en el proyecto: Compras, Devoluciones/NC). Sin equivalente que probar. |
| **LP-001 (nuevo, creado en este ciclo)** | **sí** | **FAIL → corregido** | Ver D1. |

## Defectos detectados

### D1 — `major` — El recálculo ABC contaba las ventas en Borrador como rotación real (CORREGIDO)

- **Capa:** Infrastructure. **Archivo:** `FerreteriaLaPlatense.Infrastructure/Services/ClasificacionAbcAutomaticaService.cs`.
- **Detección:** revisión de código + contraste contra el precedente interno del propio repo.
- **Síntoma:** la agregación de rotación filtraba **solo por fecha**
  (`i.Venta.Fecha >= desdeUtc && i.Venta.Fecha <= hastaUtc`), sin mirar `Venta.Estado`. En este proyecto la
  venta **nace editable** (`Borrador`) y sus `ItemVenta` existen desde que se agrega la línea, así que un
  borrador abandonado —o de prueba— sumaba cantidad vendida e inflaba la clase ABC sugerida del producto.
  Con el módulo de anulación por NC de Entrega 3, las ventas `Anulada` sumarían igual.
- **Evidencia de que es un defecto y no una decisión:** `DashboardService.ObtenerProductosMasVendidos`
  hace **exactamente la misma agregación** (`ItemVenta.Cantidad` por producto sobre una ventana) y sí filtra
  `v.Estado == EstadoVenta.Facturada`. Dos cálculos de rotación en el mismo repo con criterios distintos: el
  que no filtra es el que está mal. El criterio funcional del analista es "cantidad vendida", y un borrador
  no vendió nada.
- **Fix aplicado:** agregado `i.Venta.Estado == EstadoVenta.Facturada` al `Where`, contra el conjunto
  **explícito** de estados consumados (no `!= Borrador`, que dejaría pasar `Anulada`). Actualizado el
  XML-doc de la clase para que el criterio documentado coincida con el código.
- **Catalogado como `LP-001`** en `docs/qa/regresiones-manuales.yml` + sección nueva de patrón generalizable
  ("Agregaciones sobre filas hijas de un documento con máquina de estados") en
  `32-estandares-qa-implementador.instructions.md`.

### D2 — `blocker` — El "Confirmar la importación" habría fallado con 500 en MySQL (CORREGIDO)

- **Capa:** Infrastructure. **Archivo:** `FerreteriaLaPlatense.Infrastructure/Services/CatalogoMigracionService.cs`.
- **Detección:** ejecución del catálogo cross-proyecto — item **MH-001**, cuya `nota_qa_sprint4` acota el
  riesgo a colecciones locales de **string** y lo confirma empíricamente contra
  `MySql.EntityFrameworkCore` 10.0.1. **Este proyecto usa ese provider y esa versión exacta.**
- **Síntoma esperado:** dos `Where(coleccionLocalDeString.Contains(columna))` traducidos a `IN` de SQL:
  (1) `ProcesarProductosAsync`, `codigos.Contains(p.Codigo)` con `codigos` = `List<string>` del lote;
  (2) `ProcesarCodigosProveedorAsync`, `codigos.Contains(c.CodigoDelProveedor)`, ídem.
  El provider no asigna type mapping al parámetro de array de strings →
  `InvalidOperationException: Expression '@codigos' in the SQL tree does not have a type mapping assigned` → 500.
- **Por qué era grave:** ambos están **solo en el camino de persistir** (`if (!persistir) return;` corta antes
  en el preview). El operador habría visto un preview perfecto y el fallo aparecería recién al confirmar —
  el paso más caro y menos reversible del flujo, y el que el propio Implementador marcó como la prueba más
  importante de la etapa. No se detectó antes porque la migración EF nunca se aplicó a ninguna base.
- **Fix aplicado (adaptado, no copiado):** el `archivos_fix` canónico de MH-001 es "traer la tabla a memoria
  y filtrar en proceso", **inaceptable acá**: `Productos` tiene 121.691 filas y el bucle procesa lotes de 500
  (≈244 relecturas del catálogo completo). En su lugar se convirtió el `IN` de string en un `IN` de `Id`
  (colección de `int`, segura según la propia nota del catálogo), aprovechando que **ambos métodos ya tenían
  en memoria** el mapa `codigo→Id` / `clave→Id` de la proyección completa que hacen al arrancar: **cero
  consultas extra** y semántica idéntica (ambas proyecciones usan `IgnoreQueryFilters()`, así que el conjunto
  alcanzado por `Id` es el mismo que alcanzaba el `IN` por string, soft-deleted incluidos). Para
  `CodigoProveedorProducto` se agregó el diccionario `idPorClave` sobre la proyección ya existente.
- **Registrado** como `nota_qa_laplatense_etapa3` en MH-001 (reaparición en otro proyecto + la lección de que
  el fix canónico no escala a tablas de volumen).

### D3 — `minor` — La reimportación sobreescribe la sugerencia ABC recién calculada (ACEPTADO, no corregido)

- El upsert de producto asigna `entidad.ClasificacionABCSugerida = f.ClasificacionABCSugerida`. Si el
  operador corre "Recalcular clasificación ABC" y después reimporta el archivo, la sugerencia calculada se
  reemplaza por la del archivo (o por `null`, si la columna viene vacía).
- No se corrige: `clasificacionABCSugerida` es una columna declarada del formato de intercambio y el campo
  manual `ClasificacionABC` —el que importa— nunca se toca. Se resuelve volviendo a recalcular.
- **Acción:** documentado acá y en Riesgos. Conviene avisarlo en la pantalla o recalcular al final del import;
  queda como mejora menor para el Implementador, no bloquea.

### D4 — `informativo` — Entrega 2 nunca pasó por el gate de QA — **CERRADO 2026-08-21**

- La memoria de QA solo tenía el ciclo de Entrega 1 (2026-08-10). Ventas/AFIP/Caja/Gastos/Entregas/Dashboard
  se cerraron el 2026-08-11 y **no había registro de QA**. No era un defecto de Etapa 3, pero sí un riesgo de
  liberación: esta etapa se apoya en `ItemVenta`/`Venta` (para el ABC) y en `Cliente` (para el import), que
  nunca habían sido validados funcionalmente.
- **CERRADO el 2026-08-21**: se ejecutó el primer ciclo completo de QA de Entrega 2 sobre la rama `entrega-2`
  ya reconciliada, con la migración aplicada y el catálogo real cargado. Ver la sección
  "Entrega 2 — ... (QA, 2026-08-21)" al principio de este archivo. Resultado: 3 defectos corregidos con
  auto-fix (2 de ellos `blocker`), 6 reportados sin corregir, GO condicionado a merge y NO-GO a producción.
- **Verificación cruzada para Etapa 3:** el ciclo confirmó que `LP-001` sigue vigente tras el merge — el
  recálculo ABC mantiene el filtro `Estado == Facturada` que se le agregó en esta etapa.
- **La observación colateral era un bug real y está corregida.** `DashboardService` usaba `DateTime.Today`
  contra `Venta.Fecha` (UTC): se reprodujo con datos controlados y el Dashboard mostraba **la venta de ayer**
  como "Ventas de hoy", omitiendo la de hoy. Quedó registrado como **D7** del ciclo de Entrega 2 y se corrigió
  usando `ArgentinaTime.HoyRangoUtc()`, el mismo criterio que el ABC ya aplicaba bien.

## Auto-fixes aplicados por QA

| id catálogo | defecto | archivos tocados | resultado post-parche |
|---|---|---|---|
| `LP-001` (nuevo) | D1 — ABC contaba borradores | `FerreteriaLaPlatense.Infrastructure/Services/ClasificacionAbcAutomaticaService.cs` (filtro `Estado == Facturada` + XML-doc) | `dotnet build` → 0 errores. Verificación funcional pendiente de base (prueba manual 4 de abajo). |
| `MH-001` (existente, reaparición) | D2 — `IN` de string en MySQL | `FerreteriaLaPlatense.Infrastructure/Services/CatalogoMigracionService.cs` (relectura de lote por `Id` en los 2 puntos + `idPorClave`) | `dotnet build` → 0 errores. Verificación funcional pendiente de base (prueba manual 2). |

Ninguno de los dos introduce lógica de negocio nueva: D1 replica el criterio de estado que ya usaba
`DashboardService` en el mismo repo, y D2 replica el patrón de evitar `IN` de string ya catalogado.

## Pruebas manuales pendientes (a ejecutar por Joaquín — requieren UI y base con la migración aplicada)

**Prerequisito obligatorio antes de cualquier prueba en caliente:**
`dotnet ef database update --project FerreteriaLaPlatense.Infrastructure --startup-project FerreteriaLaPlatense.Web`
(la migración `EntregaTres_MigracionCatalogo` **no fue aplicada** por el Implementador). Hace falta además un
`.xlsx` de prueba con las 3 hojas y una decena de filas cada una — no se necesita el dataset real.

1. **Permisos (cierra la verificación en caliente de REG-010/KOI-005).** Con un usuario `Vendedor`: el link
   "Migración de catálogo" no debe aparecer en el sidebar, y `/MigracionCatalogo` por URL directa debe dar
   **403, no 500 ni acceso silencioso**. Repetir con `POST /Stock/RecalcularClasificacionAbc` y
   `POST /Productos/AceptarClasificacionAbcSugerida`. Con `Administrador`: el link aparece bajo Catálogo y la
   pantalla carga.
2. **Confirmación del fix D2 (la prueba más importante).** Subir el archivo → revisar → **Confirmar**. Debe
   completar y mostrar la pantalla de resultado con los mismos números que el preview. Si apareciera un 500
   con `does not have a type mapping assigned`, el fix no alcanzó y hay que escalar al Implementador.
3. **Idempotencia.** Reimportar **exactamente el mismo archivo**: el preview debe mostrar **0 altas y todas
   actualizaciones** en las 3 secciones y 0 catálogos a crear; el total de productos y clientes del sistema no
   debe cambiar. Después: editar a mano un producto migrado (stock mínimo por el ABM, stock por "Ajustar",
   clasificación ABC manual), reimportar, y verificar que **stock y clasificación ABC manual siguen como los
   dejó usted**.
4. **Confirmación del fix D1.** Crear una venta con 500 unidades de un producto que no rota y **dejarla en
   Borrador**. Recalcular ABC a 12 meses → ese producto **no** debe quedar A/B por el borrador, y no debe
   contarse en "productos con ventas en el período". Después facturar esa venta y recalcular → ahora sí debe
   reflejarse.
5. **Excepciones.** Archivo con: producto sin nombre, producto sin precio de venta, código repetido, código de
   proveedor apuntando a un `codigoProducto` inexistente, y cliente sin nombre. Cada uno debe aparecer con su
   motivo y marcado "No se importa"; el resto del archivo debe importarse igual. Verificar que con al menos una
   excepción el botón "Confirmar" arranca **deshabilitado**, y que se habilita recién después de abrir el
   reporte y volver al resumen. Probar además a confirmar por POST directo sin haber abierto el reporte: debe
   rechazarlo con mensaje (guard server-side).
6. **Filtros y export del reporte.** Filtrar por sección, por texto del motivo y por "No se importa"; ordenar
   haciendo click en cada encabezado (verifica CRM-003 en caliente). Exportar a Excel: mismas filas y
   encabezados en español.
7. **Archivo inválido.** Subir un `.xlsx` al que le falte una hoja, y otro al que le falte una columna
   obligatoria: debe rechazarlos con un mensaje que diga qué falta, **sin importar nada**.
8. **Ventana ABC.** Recalcular con ventana de 1 mes y comparar contra 12 meses: los resultados deben cambiar
   (menos productos con venta). Verificar que el recálculo **no** cambió la clasificación manual de ningún
   producto (comparar el listado de `Stock` antes y después).
9. **"Aceptar sugerencia".** En un producto donde la sugerencia difiera, usar el botón y confirmar → el campo
   manual queda con el valor sugerido. Reintentarlo debe avisar que ya coinciden. Verificar que el botón
   **no** aparece para `Vendedor`.
10. **Regresión de Entrega 1/2.** Alta y edición de producto por el ABM normal, con y sin bonificación (el
    combo de marca/modelo/categoría de Editar debe seguir llegando con el valor asignado); alta y edición de
    cliente con los 4 campos nuevos vacíos (deben guardar: son opcionales) y con un email mal escrito (debe
    bloquear con mensaje); una venta completa Borrador → Facturada.

## Riesgos de liberación (Etapa 3)

1. **La migración EF no está aplicada a ninguna base.** Prerequisito absoluto y bloqueante para cualquier
   prueba. Es aditiva pura, así que el riesgo de aplicarla es bajo — pero hacer backup antes igual.
2. **Nada de esta etapa se ejecutó nunca.** Los dos defectos encontrados (uno de ellos `blocker`) salieron de
   revisión de código, no de ejecución. Sin las pruebas manuales 2 y 3 no hay evidencia de que el import
   funcione de punta a punta. **Es el riesgo principal.**
3. **Tiempo de proceso con 121.691 productos sin medir** (riesgo ya declarado por el Implementador, sigue
   abierto). El import es síncrono dentro del request. Mitigación operativa: partir el archivo en tandas
   aprovechando la idempotencia. Medir con el dataset real antes de comprometer una ventana de corte.
4. **Staging en el temp del sistema operativo**, sin limpieza automática: los archivos con datos del cliente
   quedan en `%TEMP%/FerreteriaLaPlatense/migracion-catalogo/` y **hay que borrarlos a mano**. Si el hosting
   recicla el proceso entre analizar y confirmar, hay que volver a subir (el sistema lo avisa con un mensaje
   claro, no rompe con 500 — verificado en código).
5. **La deduplicación real (paso 1) no existe todavía.** Los criterios de aceptación centrales de la etapa
   (dedup de nombre y de `articuloProveedor`) **no son validables** con lo implementado: dependen de la
   herramienta batch del ítem 1 del WBS, que hay que construir y que va a necesitar su propio ciclo de QA.
   Conviene no comunicar la Etapa 3 como "migración terminada": está el importador, no la extracción.
6. ~~**Entrega 2 sin QA** (D4). Esta etapa se apoya en `Venta`/`ItemVenta`/`Cliente`, nunca validados.~~
   **Resuelto 2026-08-21:** Entrega 2 pasó por QA. `Venta`/`ItemVenta`/`Cliente` quedaron validados
   funcionalmente y se confirmó que el fix `LP-001` de esta etapa sigue vigente tras el merge.
7. `Proveedor` mínimo: cuando se implemente Compras, hay que **ampliar** la entidad, no recrearla. Riesgo de
   coordinación, ya documentado en el XML-doc.
8. `Bonificacion` es informativa y no participa de ningún cálculo de precio — si el cliente espera que "33+5"
   descuente, es alcance nuevo.

## Estado go/no-go (Etapa 3)

**GO CONDICIONADO** al merge de la rama, con dos condiciones de cumplimiento obligatorio:

1. Aplicar `EntregaTres_MigracionCatalogo` a la base de desarrollo.
2. Ejecutar las pruebas manuales **1, 2, 3, 4 y 5** (permisos, confirmar, idempotencia, fix del ABC,
   excepciones) y reportar PASS/FAIL. Las pruebas 2 y 4 son la verificación en caliente de los dos auto-fixes
   de este ciclo y **no pueden saltearse**.

Fundamento: el código está bien construido —el diseño de idempotencia es sólido y deliberado, los permisos
son correctos controller por controller, la migración es aditiva pura y el bug de huso horario que el
Implementador declaró haber corregido está efectivamente corregido en el código final—, pero **el `blocker`
D2 demuestra el costo de cerrar una etapa sin ejecutar nada**: el camino de confirmación, que es el corazón
de la etapa, habría fallado en la primera prueba real. Con los dos fixes aplicados y el build limpio no hay
motivo para frenar el merge, pero **no hay GO para la carga a producción** hasta tener las pruebas en caliente
y la herramienta del paso 1.

## Checklist de salida para merge (Etapa 3)

- [x] `dotnet build FerreteriaLaPlatense.slnx` → 0 errores (verificado 3 veces: inicial y tras cada auto-fix).
- [x] Permisos verificados controller por controller, no por el reporte del Implementador.
- [x] Migración EF revisada línea por línea y confirmada aditiva pura.
- [x] Idempotencia revisada a fondo por código (claves de identidad, `IgnoreQueryFilters`, campos no pisados).
- [x] `IClasificacionAbcAutomaticaService` confirmado: nunca escribe `ClasificacionABC`; ventana en UTC correcta.
- [x] Catálogo cross-proyecto ejecutado (43 ids) y cobertura reportada.
- [x] 2 defectos corregidos con auto-fix + catalogados (`LP-001` nuevo, `MH-001` reaparición).
- [x] Patrón generalizable agregado a `32-estandares-qa-implementador.instructions.md`.
- [ ] **Migración aplicada a la base de desarrollo** (pendiente, bloqueante para pruebas).
- [ ] **Pruebas manuales 1-5 ejecutadas por Joaquín** (pendiente, bloqueante para producción).
- [ ] Pendiente (no bloqueante): D3 — avisar o recalcular la sugerencia ABC tras un reimport.
- [x] QA de Entrega 2 ejecutado (D4 cerrado el 2026-08-21) — ver la sección de Entrega 2 al principio.
- [ ] Pendiente (no bloqueante): confirmar con Joaquín las 3 decisiones que tomó el Implementador (productos sin
      venta en `C` y no `null`; unidades no modeladas → `Unidad`; CC de clientes no se migra).

---

# Entrega 1 — Catálogo / Stock / Usuarios (QA, 2026-08-10)

## Definiciones vigentes

### Alcance funcional validado

Primera entrada del proyecto a la etapa de QA. Alcance de esta validación: **exclusivamente Entrega 1**
(Catálogo, Stock, Usuarios/roles, Código de barras), sobre el repo `C:\Sistemas\Ferreteria La Platense`
(`FerreteriaLaPlatense.slnx`, .NET 10, EF Core 10 + MySQL, ASP.NET Core Identity).

No se validó (no existe código todavía, confirmado por inspección del repo — 0 controllers/entidades
de esos módulos): Ventas, AFIP/Facturación, Caja, Compras, Cuenta corriente (clientes/empleados/negocio),
Devoluciones/NC, Presupuestos, Entregas, Dashboard. Quedan para Entrega 2/3.

Metodología: sin ejecución en caliente (no hay base de datos con la migración aplicada — ver Riesgos).
Evidencia = lectura de código completa por capa (Domain/Application/Infrastructure/Web) + `dotnet build`.
Para los casos que requieren UI se deja el procedimiento manual paso a paso para que Joaquín/el cliente
lo ejecuten y reporten PASS/FAIL/BLOCKED.

### Build

`dotnet build FerreteriaLaPlatense.slnx` → **Compilación correcta, 0 Errores** (9 advertencias: 4×NU1902
vulnerabilidad conocida de MailKit/MimeKit preexistente, 1×NETSDK1057 por SDK preview, 1×CS0114
`HomeController.StatusCode` oculta miembro heredado — las 3 categorías son preexistentes, no introducidas
por Entrega 1). Verificado antes y después de aplicar los auto-fixes de ortografía (ver Defectos).

### Cobertura de historias de usuario

| Historia / módulo (Entrega 1) | Resultado |
|---|---|
| Usuarios y roles (Admin/Vendedor/Repartidor) | Cumple |
| Catálogo de productos (Marca/Modelo/Categoría/IVA/precio/descuento) | Cumple |
| Unidades de medida y conversión compra↔venta (R4) | Cumple |
| Stock + puesta a punto inicial (ABC, ajuste manual auditado, arranque con negativo permitido) | Cumple |
| Código de barras — vinculación al producto (M11) | Cumple (parcial por alcance: sin pantalla de Venta todavía, expuesto vía endpoint de prueba) |

### Cobertura por criterio de aceptación (PASS/FAIL/BLOCKED)

| Criterio | Resultado | Evidencia |
|---|---|---|
| PF13 — producto sin stock verificado puede "venderse" igual (stock negativo con aviso, sin bloqueo) | PASS (parcial, dato/flag) | `Producto.Stock` es `decimal` sin restricción de signo; `StockVerificado=false` por defecto en `CrearAsync`; ningún Service bloquea valores negativos. No hay pantalla de Venta en esta entrega — el criterio completo (aviso visual en el flujo de venta) se termina de cerrar en Entrega 2, tal como está planificado. |
| PF14 — ajuste manual de stock con motivo, auditado (quién/cuándo/motivo) | PASS | `AjusteStockService.AplicarAjusteAsync` registra `AjusteStock` (ProductoId, Fecha UTC, UsuarioId desde `ClaimTypes.NameIdentifier`, CantidadAnterior/Nueva, Motivo obligatorio) antes de pisar `Producto.Stock`; `StockController.Historial` expone el historial por producto vía DataTable server-side. |
| R4 — `UnidadCompra != UnidadVenta` exige `FactorConversion` > 0 | PASS | Validado en `ProductoService.ValidarAsync` (Service, no solo ViewModel) vía `IUnidadMedidaConversionService.EsFactorConversionValido`; UI oculta/limpia el campo con JS cuando no aplica; `[Range(0.0001,...)]` en el ViewModel como cota adicional de UI. |
| R11 — código de barras único, propio o de fábrica, sin distinción funcional | PASS | `Producto.CodigoBarras` nullable + índice único (MySQL permite múltiples NULL); `CodigoBarrasLookupService.BuscarPorCodigoAsync` busca indistintamente por `CodigoBarras` o `Codigo`. |
| Permisos: Admin (todo) / Vendedor (catálogo y stock en consulta) / Repartidor (sin pantallas en Entrega 1) | PASS | Policies `RequireCatalogoConsulta` (SuperUsuario+Vendedor) en `ProductosController`/`StockController`/`MarcasController`/`ModelosController`/`CategoriasController` a nivel de clase; alta/edición/baja y ajuste de stock exclusivos de `RequireSuperUsuario` a nivel de acción; sidebar coincide (ver catálogo cross-proyecto, id REG-010/KOI-003). Repartidor no tiene ningún link ni policy que lo habilite — correcto para el alcance de esta entrega. |
| Bloqueo de baja de Marca/Modelo/Categoría en uso | PASS (regla agregada por el Implementador, no exigida explícitamente por el análisis, pero consistente y correcta) | `CatalogoSimpleServiceBase.EliminarAsync` verifica `EstaEnUsoAsync` (override por entidad, contra `Producto.MarcaId/ModeloId/CategoriaId`) antes de permitir soft-delete; mensaje sugiere desactivar en su lugar. |

### Matriz de casos de prueba

**Casos felices**
1. Crear Marca/Modelo/Categoría con nombre único → alta correcta, aparece en combos de Producto.
2. Crear Producto con `UnidadCompra == UnidadVenta` (sin factor) → alta correcta, stock arranca en 0/sin verificar.
3. Crear Producto con `UnidadCompra=Bulto`, `UnidadVenta=Unidad`, `FactorConversion=100` → alta correcta.
4. Ajustar stock de un producto con motivo → `Stock` pasa a pisar el valor nuevo, `StockVerificado=true`, aparece en Historial.
5. Buscar producto por código de barras (endpoint de prueba en Productos/Index) → devuelve el producto.
6. Crear usuario con rol Vendedor o Repartidor → login exitoso, sidebar acorde al rol.
7. Editar Producto → combos Marca/Modelo/Categoría llegan preseleccionados con el valor actual.

**Casos de borde**
1. Crear Producto con `UnidadCompra != UnidadVenta` y `FactorConversion` vacío o 0 → debe rechazar (Service, R4). **PASS por código** — cubierto por `ValidarAsync`.
2. Ajuste de stock que deja `CantidadNueva` negativa → debe permitirse (arranque suave, R10) y quedar auditado igual. **PASS por código** — `AplicarAjusteAsync` no valida signo de `CantidadNueva`.
3. Crear Producto con `Codigo` o `CodigoBarras` duplicado (ya existente) → debe rechazar con mensaje claro. **PASS por código** — `ValidarAsync` chequea unicidad excluyendo el propio Id en edición.
4. Eliminar una Marca/Modelo/Categoría **en uso** por al menos un Producto activo → debe bloquear sugiriendo desactivar. **PASS por código** — `EstaEnUsoAsync` por entidad.
5. Editar Producto cuya Marca/Modelo/Categoría asignada fue desactivada después → el combo de Editar debe seguir mostrando esa opción seleccionada (no vacío). **PASS por código** — `ProductosController.PoblarCombosAsync` re-agrega la entidad inactiva si no está en el listado de activos.
6. Vendedor intenta acceder a Create/Edit/Delete de Producto o a Stock/Ajuste → debe ser rechazado (403/redirect AccessDenied). **PASS por código** — `[Authorize(Policy="RequireSuperUsuario")]` a nivel de acción.
7. Repartidor intenta acceder a `/Productos/Index` o `/Stock/Index` directamente por URL → debe ser rechazado. **PASS por código** — `RequireCatalogoConsulta` solo incluye SuperUsuario+Vendedor.
8. IVA con un valor fuera de {10,5; 21} vía manipulación directa del POST (no por el `<select>`) → debe rechazar. **PASS por código** — `AlicuotasIVA.Permitidas` validado en el Service.

**Procedimiento manual para el cliente (a ejecutar en caliente, reportar PASS/FAIL/BLOCKED)**

Prerrequisito obligatorio antes de cualquier prueba: aplicar la migración (ver Riesgos, punto 1).

1. Login como SuperUsuario (seed) → crear un usuario Vendedor y otro Repartidor desde Usuarios → cerrar sesión → loguearse con cada uno → verificar que el sidebar muestra exactamente lo esperado por rol (Vendedor: Catálogo+Stock; Repartidor: nada de Entrega 1).
2. Como SuperUsuario, crear una Marca, un Modelo y una Categoría.
3. Crear un Producto usando esa Marca/Modelo/Categoría, con `UnidadVenta=Unidad`, sin unidad de compra distinta. Guardar y verificar que aparece en el listado con Stock=0 y badge "Sin verificar".
4. Crear un segundo Producto con `UnidadCompra=Bulto` y sin completar el factor de conversión → debe bloquear el guardado con el mensaje de error correspondiente.
5. Completar el factor de conversión (ej. 100) y guardar → debe permitir el alta.
6. Ir a Stock → Ajuste sobre el primer producto → cargar cantidad nueva (probar también un valor negativo) y motivo → guardar → verificar badge "Verificado" y que el Historial muestra el registro con usuario/fecha/motivo.
7. En Productos/Index, usar el buscador de código de barras con el código interno de un producto sin código de barras propio → debe encontrarlo igual (busca por `Codigo` o `CodigoBarras`).
8. Intentar eliminar la Marca usada por el Producto creado → debe bloquear sugiriendo desactivar.
9. Desactivar esa Marca → editar el Producto → confirmar que el combo Marca sigue mostrando la marca (ahora inactiva) seleccionada, no vacío.
10. Login como Vendedor → confirmar que ve Productos/Stock/Marcas/Modelos/Categorías en modo **solo consulta** (sin botones Nuevo/Editar/Eliminar/Ajustar) y que forzar la URL de Create/Edit/Ajuste devuelve acceso denegado.

### Cobertura de maquina de estados

No hay una máquina de estados formal con transiciones múltiples en Entrega 1 (Venta/Compra, que sí la
tendrán, son Entrega 2/3). Los dos "estados" binarios presentes:

| Entidad.Campo | Transición | Resultado |
|---|---|---|
| `Producto.StockVerificado` | `false → true` (al aplicar el primer `AjusteStock`) | PASS — un solo sentido por diseño (R10/PF14), no hay ni debería haber vuelta a `false`. |
| `Marca/Modelo/Categoria.Activo` | `true ↔ true/false` libremente vía Editar | PASS — reversible en ambos sentidos, sin restricción indebida; la restricción real está en la baja física (bloqueada si está en uso), no en el toggle de Activo. |

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Playbook cargado completo (30 ids con `severidad != deprecated`, proyectos ShowroomGriffin/KOI/
delicias-naturales/ganaderia/vinosefue/crm-olvidata). Mapeo a Catálogo/Stock/Usuarios de La Platense:

| id | aplica (si/no/N/A) | resultado | accion |
|---|---|---|---|
| REG-001 | si (mismo stack MySQL+EF Core) | PASS — no reproduce | Ninguna entidad de Entrega 1 define `RowVersion`/`IsConcurrencyToken`, por lo que no puede ocurrir el `DbUpdateException` del catálogo. Nota para el Implementador: si Entrega 2/3 agrega concurrencia optimista (ej. edición simultánea de Venta), aplicar el patrón manual (`IsConcurrencyToken().ValueGeneratedNever()` + asignación manual en `SaveChanges`) desde el inicio. |
| REG-002 | si (patrón "falta stock inicial en el alta") | PASS — no es bug, es diseño confirmado | El Create de Producto no expone `Stock` a propósito (`2-disenador-funcional.md` flujo 8: la carga inicial es siempre vía Ajuste de stock, con auditoría). Comportamiento esperado, distinto del caso original (que sí era una omisión). |
| REG-003 | N/A | N/A | No hay ningún combo Select2 con autocomplete AJAX en Entrega 1 (Marca/Modelo/Categoría usan `<select>` simple con `asp-items`). Vigilar en Entrega 2 (buscador de productos/clientes en Venta). |
| REG-004 | N/A | N/A | Compras no existe en esta entrega. |
| REG-005 | N/A | N/A | Ventas no existe en esta entrega. |
| REG-006 | N/A | N/A | Ventas/medios de pago no existen en esta entrega. |
| REG-007 | N/A | N/A | Devoluciones no existe en esta entrega. |
| REG-008 | N/A | N/A | No hay grillas dinámicas de filas (pagos/ítems) en Entrega 1. |
| REG-009 | N/A | N/A | No hay combos en cascada en Entrega 1 (Marca/Modelo/Categoría son independientes entre sí). |
| REG-010 | si | PASS | Sidebar: sección "Catálogo" gateada por `SuperUsuario\|\|Vendedor`, coincide con policy `RequireCatalogoConsulta` real de los 5 controllers; sección "Sistema" (Usuarios/System/Notifications) gateada por `SuperUsuario`, coincide con `RequireSuperUsuario` de `UsersController`/`SystemController` (`NotificationsController` usa `[Authorize]` simple, pero es correcto: es la bandeja **propia** de cada usuario, filtrada por `userId` en el Service — no hay escalamiento de privilegio, solo falta el link de sidebar para Vendedor/Repartidor, defecto pre-existente fuera del alcance de Entrega 1, no introducido por esta entrega). |
| KOI-001 | si (patrón SweetAlert2 + delete) | PASS — no reproduce | Los botones eliminar de Productos/Marcas/Modelos/Categorías no dependen de `closest('form')`: el JS crea un `<form>` dinámico (`document.createElement`) recién al confirmar el SweetAlert2, así que no hay riesgo de "form no encontrado". |
| KOI-002 | N/A | N/A | No hay reportes/exportación en Entrega 1. |
| KOI-003 | si | PASS | Vendedor ve y puede acceder a Catálogo/Stock (coincide con `R` del analista); Repartidor no ve nada de Entrega 1 (correcto, no tiene pantallas propias todavía). |
| KOI-004 | si (patrón "validación solo en UI") | PASS | `ProductoService.ValidarAsync` valida `FactorConversion`, unicidad de `Codigo`/`CodigoBarras` e IVA permitido en el Service, no solo en el ViewModel/JS. |
| KOI-005 / KOI-006 | si (patrón "link de sidebar sin controller") | PASS | Los 8 links de sidebar de Entrega 1 (Productos/Stock/Marcas/Modelos/Categorías/Users/System/Notifications) tienen su controller real correspondiente en el repo, verificado por lectura de código. |
| DN-001 / DN-002 | N/A | N/A | Ningún listado de Entrega 1 combina `Include` de **colección** (uno-a-muchos) con `OrderBy` dinámico + `Skip`/`Take`; los `Include` de `ProductoService.ListarAsync` son de referencia (Marca/Modelo/Categoría, muchos-a-uno), patrón no afectado por el bug del proveedor EF6-MySQL (que además no aplica: este proyecto usa el proveedor `Pomelo`/EF Core 10, no `MySql.Data.EntityFramework`). Vigilar si Entrega 2 agrega un listado de Ventas con `Include(v => v.Items)`. |
| GAN-001 | N/A | N/A | No hay listas dinámicas bindeadas por índice (`Items[i]`) en Entrega 1. |
| GAN-002 | N/A | N/A | No hay backfill de datos de producción en este ciclo (proyecto sin datos reales todavía). |
| GAN-003 | N/A | N/A | No se usa el patrón `<script type="text/x-template">` con Tag Helpers adentro en ninguna vista de Entrega 1. |
| GAN-004 | N/A | N/A | No se usa `<input list>`+`<datalist>` en ninguna vista de Entrega 1; los combos son `<select>` estándar (Select2 está cargado en `_Layout.cshtml` pero todavía sin uso en Entrega 1). |
| VSF-001 / VSF-002 | N/A | N/A | No hay máquina de estados de Compra/Pedido en esta entrega. |
| CRM-001 | si (patrón "acción sin `SaveChanges` → sin auditoría") | PASS — no reproduce | Todas las mutaciones de Entrega 1 (alta/edición/baja de catálogos, ajuste de stock) pasan por `IRepository<T>.SaveChangesAsync()` → `AppDbContext.SaveChangesAsync` → `StampSoftDestroyable` (audita `CreatedAt/UpdatedAt` + usuario). No hay ninguna acción "fantasma" que cambie estado sin persistir. |
| CRM-002 | si (patrón "control visible en la vista sin gate de rol, pese a que el controller lo exige") | PASS | Los botones Editar/Eliminar/Ajustar en Productos/Marcas/Modelos/Categorías/Stock (`Index.cshtml`) están envueltos en `@if (User.IsInRole("SuperUsuario"))`, coincidiendo exactamente con la policy `RequireSuperUsuario` de las acciones correspondientes. |
| CRM-003 | si (patrón "click en columna no reordena, `order[0][column]` ignorado") | PASS — no reproduce | `DataTableRequestHelper.Parse` lee `order[0][column]`/`order[0][dir]` reales del request y resuelve el nombre de columna vía `columns[{col}][data]`; `ProductoService`/`AjusteStockService`/`CatalogoSimpleServiceBase` aplican un `switch` de `OrderBy` dinámico real sobre `request.SortColumn`, no un orden fijo hardcodeado. |
| CRM-004 | N/A | N/A | No hay alta masiva desde una API externa en Entrega 1. |
| CRM-005 | N/A | N/A | No hay bot/conversación en este proyecto. |
| CRM-006 | N/A | N/A | No hay flujo de notificación disparado por eventos de Catálogo/Stock en el diseño de Entrega 1. |

**Resumen cross-proyecto:** 30 ids evaluados → 12 aplican directamente (10 PASS sin reproducción,
2 identificados como diseño esperado no-bug), 18 N/A justificados por ausencia del módulo/patrón
equivalente en Entrega 1. **0 regresiones del catálogo reproducidas.**

### Defectos activos

| # | Severidad | Módulo | Descripción | Estado |
|---|---|---|---|---|
| D1 | minor | Productos/Marcas/Modelos/Categorías (Index) | Texto de confirmación SweetAlert2 del botón eliminar decía `"Si, eliminar"` (falta tilde; en español "si" sin tilde es la conjunción condicional, "sí" con tilde es la afirmación) — 4 vistas idénticas. Aplica la regla nueva de ortografía/acentuación (`25-frontend-design-system.instructions.md`, pedido explícito de Joaquín 2026-08-10). | **Corregido por QA** (auto-fix, ver abajo). |
| D2 | minor | `Views/Shared/_Layout.cshtml` | Título del toast SweetAlert2 de éxito (disparado por `TempData["SuccessMessage"]` en **toda** la aplicación) decía `"Exito"` sin tilde; correcto es `"Éxito"`. Máxima visibilidad — aparece tras cada alta/edición/baja exitosa de cualquier módulo. | **Corregido por QA** (auto-fix, ver abajo). |
| D3 | minor (fuera de alcance de Entrega 1, informativo) | `Web/Models/UserViewModels.cs` (líneas 37 y 73) | Mensaje de validación `[EmailAddress(ErrorMessage = "El formato de email no es valido.")]` — falta tilde en "válido". Archivo preexistente, no tocado por el Implementador en esta entrega (`UsersController` solo extendió `GetAssignableRoles()`). No corregido por no estar dentro del alcance de Entrega 1 pedido para esta validación; se deja registrado para que el Implementador lo corrija en el próximo touch de ese archivo. | Pendiente (fuera de alcance). |
| D4 | informativo, no bloqueante | `NotificationsController`/sidebar | El link "Notificaciones" del sidebar solo aparece en la sección gateada a `SuperUsuario`, pero el controller (`[Authorize]` simple, correcto porque la bandeja es propia de cada usuario vía `userId`) permitiría acceso a cualquier rol autenticado si se navega directo por URL. No es una falla de seguridad (no hay escalamiento de privilegio, cada usuario solo ve sus propias notificaciones) ni fue introducido por Entrega 1 (código preexistente). Se documenta como mejora de UX menor, no como defecto de esta entrega. | No corregido (fuera de alcance, preexistente). |

### Auto-fixes aplicados por QA

Ambos defectos (D1, D2) son errores de ortografía en texto de UI, no bugs funcionales — no requieren
alta en `docs/qa/regresiones-manuales.yml` (ese catálogo es exclusivamente para regresiones funcionales
reproducidas, ver regla de borde de `30-qa-regresiones.instructions.md`: "Solo se registran bugs
funcionales..."). Se aplicó el fix directo, de contenido puro, sin lógica de negocio nueva:

- `FerreteriaLaPlatense.Web/Views/Productos/Index.cshtml` — `'Si, eliminar'` → `'Sí, eliminar'`.
- `FerreteriaLaPlatense.Web/Views/Marcas/Index.cshtml` — idem.
- `FerreteriaLaPlatense.Web/Views/Modelos/Index.cshtml` — idem.
- `FerreteriaLaPlatense.Web/Views/Categorias/Index.cshtml` — idem.
- `FerreteriaLaPlatense.Web/Views/Shared/_Layout.cshtml` — `'Exito'` → `'Éxito'`.

Re-build post-parche: `dotnet build FerreteriaLaPlatense.slnx` → **Compilación correcta, 0 Errores**
(mismas 9 advertencias preexistentes, ninguna nueva). Pruebas mínimas re-ejecutadas: lectura de código
confirma que el cambio es de contenido de string únicamente, sin alterar la lógica de los handlers de
click ni el flujo de submit del form dinámico — sin riesgo de regresión funcional.

### Riesgos de liberacion

1. **Bloqueante para cualquier prueba en caliente:** la migración `EntregaUno_CatalogoStockUsuarios`
   (20260810165155) fue generada pero **no aplicada a ninguna base de datos** — confirmado en
   `5-implementador.md`. Antes de que Joaquín o el cliente prueben esta entrega, ejecutar:
   ```
   dotnet ef database update --project FerreteriaLaPlatense.Infrastructure --startup-project FerreteriaLaPlatense.Web
   ```
   contra la base de dev/staging real. Es la primera migración del proyecto (crea también el esquema
   base de Identity/Notifications/PreferenciaUsuario que nunca se había migrado).
2. Riesgo de negocio ya declarado por el Implementador, sin cerrar: la hipótesis de que el factor de
   conversión es **fijo por producto** (no varía según el bulto del proveedor) está codificada tal cual
   en `UnidadMedidaConversionService`. Si el cliente confirma que un mismo producto llega en bultos de
   distinto tamaño según el proveedor, el modelo de `Producto` necesita revisión **antes** de Entrega 2
   (Compras). No bloquea Entrega 1 (el dato ya es correcto para el caso simple), sí bloquea Compras.
3. Riesgo de negocio a confirmar con el personal de mostrador: el ajuste manual de stock **pisa** el
   valor (no suma/resta) — confirmar que matchea la expectativa operativa antes de que lo use el
   personal, ya que un error de interpretación (cargar "cuánto vendí" en vez de "cuánto queda") generaría
   datos de stock incorrectos sin que el sistema lo detecte.
4. Riesgo técnico menor, no bloqueante: no hay control de concurrencia optimista en `Producto.Stock`
   (dos ajustes simultáneos del mismo producto aplican "last write wins" sin fusionar). Bajo impacto en
   Entrega 1 (operación de mostrador, un usuario a la vez en la práctica), a revisar si Entrega 2/3
   introduce ajustes concurrentes de alto volumen.
5. `Marca`/`Modelo`/`Categoria` arrancan sin ningún registro seed — el cliente debe cargar su propio
   catálogo de marcas/modelos/categorías antes de poder cargar productos (comportamiento esperado,
   documentado por el Implementador, no es un defecto).

### Estado go/no-go

**GO condicionado** — Entrega 1 (Catálogo, Stock, Usuarios/roles, Código de barras) aprobada para que
el cliente comience a probarla, **una vez aplicada la migración pendiente** (riesgo #1, prerrequisito
obligatorio — sin ella no hay ninguna tabla creada y ninguna pantalla puede funcionar). No se encontraron
defectos funcionales ni de permisos por revisión de código; los 2 defectos de ortografía detectados
(D1, D2) ya fueron corregidos por este ciclo de QA. 0 regresiones del catálogo cross-proyecto
reproducidas. El defecto D3 (fuera de alcance) y D4 (informativo) no bloquean el go-live de esta entrega.

**Checklist de salida para merge:**
- [x] Build limpio (`dotnet build`, 0 errores) antes y después del auto-fix.
- [x] Revisión de fronteras por capa (Domain/Application/Infrastructure/Web) sin mezclas indebidas.
- [x] Validaciones de negocio (R4, unicidad, IVA permitido) presentes en el Service, no solo en la UI.
- [x] Permisos por rol verificados por código (policy de controller/action ↔ sidebar).
- [x] Combos de Editar preseleccionados correctamente (Marca/Modelo/Categoría), incluso si la entidad
      referenciada fue desactivada después.
- [x] Ortografía/acentuación de todo el texto de UI creado en Entrega 1 revisada y corregida.
- [x] Catálogo de regresiones cross-proyecto ejecutado (30 ids), 0 reproducidas.
- [ ] **Pendiente antes de prueba en caliente:** aplicar `dotnet ef database update` contra la base real.
- [ ] Pendiente (no bloqueante): confirmar con el cliente la hipótesis de factor de conversión fijo por
      producto antes de arrancar Compras (Entrega 2).

## Historial de ajustes
- 2026-08-10: Primera etapa de QA del proyecto. Cargado el playbook cross-proyecto completo
  (`docs/qa/regresiones-manuales.yml`, 30 ids) y mapeado contra Catálogo/Stock/Usuarios de Entrega 1 —
  0 regresiones reproducidas, 18 ids N/A justificados por módulo inexistente en esta entrega. Revisión de
  código completa por capa (Domain/Application/Infrastructure/Web) + `dotnet build` (0 errores). Detectados
  y corregidos 2 defectos de ortografía (D1 "Si, eliminar"→"Sí, eliminar" en 4 vistas; D2 "Exito"→"Éxito"
  en `_Layout.cshtml`) bajo la regla nueva de `25-frontend-design-system.instructions.md`. Documentado
  defecto D3 (fuera de alcance, archivo preexistente) y D4 (informativo, no bloqueante). Recomendación:
  GO condicionado a aplicar la migración `EntregaUno_CatalogoStockUsuarios` antes de cualquier prueba en
  caliente del cliente.
- 2026-08-21 (v3): primer ciclo de QA de **Entrega 2 completa** (Ventas/CC Clientes/AFIP/Caja/Gastos/Entregas/
  Dashboard) sobre la rama `entrega-2` reconciliada, contra `laplatense_dev` con el catálogo real migrado.
  Cierra el defecto D4 de Etapa 3. Primer ciclo del proyecto con **verificación automatizada por navegador
  real** (Playwright vía `playwright-core`, porque el MCP `playwright` no estaba conectado en la sesión):
  ~90 casos ejecutados contra la app corriendo, ninguno validado solo por lectura de código. 3 defectos
  corregidos con auto-fix — D5 `blocker` (borrador de venta inutilizable al reabrirlo, por render de decimales
  en cultura es-AR dentro de `<input type="number">`, catalogado como `LP-003` nuevo), D6 `blocker` (4
  endpoints en HTTP 500 por la 3ª aparición de `MH-001`, incluido `Stock/HistorialListar` que **está caído en
  producción**), y D7 `major` (el Dashboard mostraba las ventas del día equivocado — confirma y corrige la
  observación colateral que D4 había dejado anotada). 6 defectos reportados sin corregir por ser decisiones de
  diseño o de negocio: D8 (`Confirmar y facturar` factura datos viejos — bloqueante antes de configurar AFIP),
  D9 (`CajaMovimiento.Fecha` mezcla instante UTC y fecha calendario; la guarda de caja cerrada mira otro día),
  D10, D11, D12, D13. Agregadas 2 secciones preventivas a
  `32-estandares-qa-implementador.instructions.md` (MH-001 y LP-003). Recomendación: **GO condicionado a merge,
  NO-GO a producción**.
