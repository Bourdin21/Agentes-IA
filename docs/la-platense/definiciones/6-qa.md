# Memoria - QA

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-08-24 (v4 — segunda vuelta de QA de Entrega 2, rama `entrega-2`)

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
