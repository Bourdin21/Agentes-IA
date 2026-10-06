<!-- Archivado de docs/la-platense/definiciones/5-implementador.md el 2026-10-06 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - 2026-10 (7 bloques archivados)

- Sprint 0 — Deuda abierta (2026-10-05, rama `entrega-1-migracion`)
- Sprint 0 — ronda de fixes de QA: los 7 defectos abiertos (2026-10-05, rama `entrega-1-migracion`)
- Sprint 0 — gate de precio por rol en Ventas (2026-10-05, rama `entrega-1-migracion`)
- Entrega 3 — pasos 1 a 3: Proveedores, CC de proveedores y Ordenes de compra (2026-10-05, rama `entrega-1-migracion`)
- Entrega 3 — pasos 4 y 5: recepción de mercadería y pagos a proveedores (2026-10-05, rama `entrega-1-migracion`)
- Entrega 3 — ítem 4c (moneda y tipo de cambio) + paso 6 (pagos programados) (2026-10-05, rama `entrega-1-migracion`)
- Entrega 6 — Presupuestos en PDF + aumento masivo de precios (2026-10-05, rama `entrega-1-migracion`)

---

### Sprint 0 — Deuda abierta (2026-10-05, rama `entrega-1-migracion`)

Cierre de los 4 ítems de deuda previos a la Entrega 3, según el bloque "Sprint 0" del
`4-presupuestador.md`. Las decisiones de negocio venían cerradas con el cliente el 2026-10-05 y no
se re-litigaron. Un commit por ítem.

#### Resultado del escaneo de reutilización (obligatorio antes de implementar)

Paso 1 (`docs/patrones/cat_resumen.txt`) dio **3 matches directos**, no hizo falta llegar al grep
dirigido de definiciones de otros proyectos:

| Patrón | Uso en este sprint |
|---|---|
| **PAT-010** (ArgentinaTime) | Ya estaba portado al proyecto. **No se construyó nada nuevo**: se amplió el helper existente con el concepto de día/mes de negocio. Catálogo actualizado con la API nueva. |
| **PAT-001** (Ledger CC) | Base del cobro/ajuste del ítem 0.5. Su entrada tenía `pendiente_verificar: true` — **resuelto en esta misma pasada**: rutas reales confirmadas contra `C:/Sistemas/vino-y-se-fue` (`VinoSeFue.Domain/Entities/CuentaCorriente.cs` + `MovimientoCC.cs` + `MovimientoCCProveedor.cs`). |
| **PAT-019** (autocompletar con el saldo pendiente) | Aplicado al formulario de cobro: el importe arranca con la deuda completa + botón "Todo", editable para pago parcial. Tercera instancia del patrón en el proyecto. |

Reglas del catálogo aplicadas de forma activa: **LP-002** (barrido completo de usos al ampliar),
**LP-003** (decimales invariantes en los `value`), **MH-001** (apareció de verdad, ver abajo),
**MH-033** (el cobro del fiado entra al ledger de caja), **REG-010** (visibilidad del botón
acompañando al permiso real).

#### Ítem 0.2 — D8: "Confirmar y facturar" no persiste el borrador

**Ya estaba corregido en el commit `a6a78f0`** (2026-09-03, construido y **nunca deployado**). Ese
commit reemplazó `submitAccion(url)` — que armaba un form nuevo con solo el token antiforgery — por
`guardarYContinuar(continuar)`, que postea el formulario **entero** a `GuardarBorrador` con un
hidden `continuar`; el Controller guarda primero y solo sigue a `Confirmar`/`ConfirmarYFacturar` si
`result.Success`. Aplica a los **dos** botones, que era la parte que el parte de defecto pedía
verificar. Así que D8 no se volvió a implementar: se **verificó y se endureció**.

Lo que sí se agregó (defecto real encontrado al revisar ese código, no reportado por QA): la
función **no tenía guarda de doble envío**. Los dos hidden comparten `name="continuar"`, así que un
segundo click posteaba `continuar=confirmar,confirmar`, el `switch` del Controller caía en el caso
por defecto (`_`) y **el borrador se guardaba sin cerrar la venta, sin ningún aviso en pantalla** —
el mismo síntoma de clase que D8 (la pantalla dice una cosa y el server hace otra). Corregido con un
flag de reentrada, el borrado de cualquier hidden previo y el bloqueo de los tres botones de acción
hasta que el POST navegue.

#### Ítem 0.3 — D9: día de negocio de la caja

**Definición aplicada:** día de negocio = día **calendario en hora Argentina** (sin corte nocturno)
y mes de negocio = mes calendario. La base sigue guardando `DateTime` en **UTC**.

La causa raíz medida es que `CajaMovimiento.Fecha` convivía con **dos semánticas en la misma
columna**: `VentaWorkflowService` y `GastoService.AnularAsync` escribían un instante UTC, mientras
`GastoService.CrearAsync` y `RegistrarMovimientoManualAsync` escribían una fecha calendario a
medianoche. Sobre eso, las agregaciones comparaban contra `DateTime.Today` (hora del **SO**, huso
Pacífico en producción) y las guardas contra `DateTime.UtcNow.Date` (día calendario **UTC**).
Imposible ser consistente sin unificar primero la columna.

**Decisión:** `CajaMovimiento.Fecha` y `MovimientoCCCliente.Fecha` son **siempre un instante UTC**;
el día de negocio se **deriva** proyectando a ART. Toda la conversión vive en un único lugar,
`ArgentinaTime` (ampliación de PAT-010): `Hoy`, `MesActual`, `DiaDeNegocio(utc)`,
`InicioDiaUtc(día)`, `RangoDiaUtc`, `RangoDiasUtc` (último día **inclusive**, que es lo que espera
el daterangepicker) y `RangoMesUtc`. Después del cambio **no queda ningún** `DateTime.Today` ni
`DateTime.UtcNow.Date` en una decisión de día/mes, y **ninguna** `ConvertTimeToUtc`/`FromUtc` fuera
del helper.

Por **LP-002** se barrieron todos los usos, no solo Caja: `CajaMovimientoService` (filtros del
listado, búsqueda global por fecha tipeada, `EstaCerradoAsync`, resumen y cierre diario/mensual,
proyección de la fecha a ART para la grilla), `GastoService` (3 sitios, incluida la separación de
"instante que se persiste" vs. "día de negocio que se consulta" en `AnularAsync`),
`VentaWorkflowService` (la guarda de caja cerrada), `CuentaCorrienteClienteService`,
`CajaController`, `DashboardService` (ya era ART-aware pero armaba la conversión a mano — se pasó a
`RangoMesUtc`), `EntregaService.ReagendarAsync`, `ProductoService` y `CodigoBarrasLookupService`
(vigencia de oferta), más los defaults de ViewModels/DTOs y las vistas de Dashboard y Productos.

**Dos hallazgos que el parte de defecto no mencionaba:**

1. **El cierre mensual no tenía ninguna guarda de período.** Dejaba cerrar un mes anterior (bien, es
   el flujo real del cliente) pero también el mes **en curso** y cualquier mes **futuro**. Cerrar el
   mes en curso el día 10 congelaría un mes incompleto y bloquearía el resto del mes sin que nadie
   lo note hasta la primera venta rechazada. Agregada la guarda explícita: mes anterior **sí**, mes
   en curso **no** (con mensaje que explica que el cierre se hace a partir del día 1 del mes
   siguiente), mes futuro **no**. Simétricamente, `CerrarDiaAsync` ahora rechaza un día futuro (el
   día en curso sí se puede cerrar — es el cierre diario de la ferretería).
2. **`ArgentinaTime.Zone` resolvía la zona con un único `FindSystemTimeZoneById("Argentina Standard
   Time")`**, que es el id de **Windows** y no existe en Linux. Al volverse este helper la fuente
   única de **todas** las fechas del sistema, un `TimeZoneNotFoundException` ahí ya no rompería una
   pantalla: rompería el **arranque de la aplicación** (es un inicializador estático). Se le portó la
   cadena de fallback que `AfipService` ya tenía resuelta (IANA entonces id de Windows entonces UTC-3
   custom) y `AfipService` ahora **reusa** `ArgentinaTime.Zone` en vez de mantener su copia.

**Migración de datos:** `20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`, **solo
datos, sin cambio de esquema**. Suma 3 horas a las filas de `CajaMovimientos` escritas como
medianoche calendario, para que pasen a ser el instante UTC equivalente a las 00:00 ART del mismo
día. Sin esto, las filas viejas proyectarían a las 21:00 del día **anterior** y descuadrarían dos
días a la vez. Discriminador: hora exactamente `00:00:00.000000` **y** `OrigenTipo IN ('Gasto',
'Ajuste')` — los dos únicos orígenes que podían escribir así (un `DateTime.UtcNow` real no cae nunca
en la medianoche exacta al microsegundo). `Down` es la reversa exacta. Aplicada a `laplatense_dev`:
4 de 9 filas corregidas, verificado por consulta directa.

#### Ítem 0.4 — Corrección de datos: `UnidadVenta`

Modo correctivo nuevo `--solo-unidad-venta` en `tools/MigracionCatalogo`, mismo patrón que
`--solo-codigo-barras` y `--solo-codigo-propio`. **No toca SQL Server**: resuelve y retorna *antes*
de `sql.OpenAsync()`, porque la base legada ya no existe en la máquina.

Hace dos cosas, en este orden (el listado va **primero**: después del UPDATE ya no se podría
distinguir cuáles venían de `Metro`):

1. Emite el **listado** de candidatos reales a corte por metro a un CSV, con el grupo detectado.
   Solo listado: **no cambia nada y no deja nada en `Metro`**.
2. Pasa **todos** los `Metro` a `Unidad` con un `UPDATE` directo (son ~87k filas; entidad por
   entidad con tracking tardaría minutos y estamparía auditoría sobre todo el catálogo).

**No se infiere la unidad por palabra clave**, según la regla cerrada. El propio CSV confirma por
qué: entre los matches de "alambre" aparecen `ABRAZADERA DE ALAMBRE 32-50 MM` y `ALAMBRE 0,9 X 5 KG
(PRECIO X KILO)`, que no se cortan por metro. Los 14 productos en `Peso` quedan como están. Se
agregó además un aviso (no una corrección) si alguna fila queda con `UnidadCompra != UnidadVenta` y
sin `FactorConversion` válido (R4) — el script no inventa el factor; en la corrida real no hubo
ninguna.

**Números reales de la corrida contra `laplatense_dev`:**

| | Antes | Después |
|---|---:|---:|
| `Metro` | 87.542 | **0** |
| `Unidad` | 24.929 | **112.471** |
| `Peso` | 14 | 14 |

Candidatos listados (deduplicados: un producto se cuenta una sola vez, en el primer grupo que lo
toma): cable 804, manguera 535, cadena 534, alambre 276, soga/piola/cuerda 271, tanza 215 — **total
2.635**, que coincide exactamente con el total previsto en el plan. CSV conservado en
`Migracion/candidatos-corte-por-metro-20261005-121947.csv`.

**MH-001, quinta aparición en el proyecto — variante nueva.** La primera versión del listado era un
solo query con `patrones.Any(pat => EF.Functions.Like(p.Nombre.ToUpper(), pat))` sobre un `string[]`
local. Revienta con `UnreachableException: A RelationalTypeMapping collection type mapping could not
be found` — mismo defecto de fondo que el `IN` de MH-001, pero por `Any()` + `LIKE`, con un
**mensaje de error distinto** y, lo más importante, **invisible al grep canónico de la regla**
(`.Contains(`): no hay ningún `.Contains` en ese código. La encontró la **ejecución real** contra
`laplatense_dev`, no la revisión. Corregido con una consulta por patrón (parámetro escalar) uniendo
ids en un `HashSet`. La variante quedó documentada en `MH-001` de
`32-estandares-qa-implementador.instructions.md`, con el barrido ampliado a
`grep -rnE "\.(Contains|Any)\("`.

#### Ítem 0.5 — Cobro de cuenta corriente de clientes

Dos acciones nuevas sobre la pantalla que ya existía (`ClientesController.CuentaCorriente`), que
hasta ahora era **solo de consulta** — los orígenes `Pago` y `Ajuste` del enum no tenían camino desde
la UI y el cobro del fiado se llevaba por fuera del sistema.

**Cobro** (`RegistrarCobroAsync`): `Credito` con `Origen = Pago` en la CC **más** un `Ingreso` en
Caja, en **una sola transacción** con dos `SaveChanges` (el primero asigna el Id que se usa como
`OrigenId` del movimiento de caja — mismo criterio que `GastoService.CrearAsync`). Son dos hechos
distintos y uno no reemplaza al otro: **MH-033**, el ledger de caja registra toda entrada real de
dinero y el cobro del fiado es una entrada real. Guardas: importe > 0, no mayor a la deuda, fecha no
futura, **caja del día no cerrada** (misma guarda que `ConfirmarAsync`), y se rechaza el medio
`CuentaCorriente` (cobrar la CC con CC no mueve plata, solo rotaría la deuda).

**Ajuste** (`RegistrarAjusteAsync`): `Debito` o `Credito` con `Origen = Ajuste` y **motivo
obligatorio**. **No toca Caja, a propósito** — un ajuste corrige el ledger de la deuda (una venta
fiada mal cargada, una bonificación acordada, un arrastre del sistema viejo); meterlo en Caja
inflaría el arqueo con dinero que nunca se movió. Confirmación SweetAlert2 previa.

**Origen nuevo del ledger de caja: `"CobroCC"`.** Por **LP-002** se barrió todo lo que ya lee
`OrigenTipo` y se agregó la opción al combo "Origen" del filtro de `Views/Caja/Index.cshtml` — sin
eso el cobro entraría a la caja pero sería imposible de aislar en la grilla.

**Permisos — se siguió el precedente de la Entrega 2, sin inventar criterio nuevo.** *Cobrar* es
parte de la operación diaria del mostrador y es exactamente lo que ya hace un Vendedor al confirmar
una venta (genera un `CajaMovimiento` de `Ingreso` desde un documento de negocio): queda con el
`RequireVentas` del controller. *Ajustar* mueve el saldo sin respaldo de una operación real, igual
que el movimiento manual de caja, y ese es Administrador exclusivo (`CajaController` es
`RequireAdministracion`): el ajuste lleva su propio `[Authorize(Policy = "RequireAdministracion")]`
en las dos acciones, y el botón se oculta para el Vendedor (**REG-010**: la visibilidad acompaña al
permiso real, que además está validado en el server).

Las dos pantallas siguen el design system ya aplicado a las 21 existentes (`.ov-form-page`,
`.ov-page-head`, `.ov-form-actions`, `.ov-required`, Select2 por auto-init global). **LP-003**
aplicado explícitamente: el importe del cobro arranca **prellenado con la deuda**, así que `asp-for`
con cultura es-AR habría emitido `value="1234,56"`, el navegador lo habría considerado inválido y
habría dejado el input **vacío sin ningún mensaje** — se renderiza con `InvariantCulture` vía el
helper `num` de la vista. No es un riesgo latente acá, es el caso inmediato.

#### Archivos y capas modificadas (Sprint 0)

**Application**
- `Helpers/ArgentinaTime.cs` — día/mes de negocio + zona por fallback (PAT-010 ampliado).
- `Interfaces/ICajaMovimientoService.cs` — contrato del día de negocio documentado en la firma.
- `Interfaces/ICuentaCorrienteClienteService.cs` — `RegistrarCobroAsync`, `RegistrarAjusteAsync`.
- `DTOs/MovimientoCCClienteDtos.cs` — `CobroCCClienteDto`, `AjusteCCClienteDto`.
- `DTOs/CajaDtos.cs`, `DTOs/GastoDtos.cs` — defaults al día de negocio.

**Infrastructure**
- `Services/CajaMovimientoService.cs` — todas las fronteras de día/mes; totales centralizados en `ObtenerTotalesDiasAsync`/`ObtenerTotalesMesAsync`; guardas de período del cierre diario y mensual.
- `Services/CuentaCorrienteClienteService.cs` — cobro + ajuste, filtros y proyección de fecha; depende ahora de `ICajaMovimientoService`.
- `Services/GastoService.cs`, `Services/VentaWorkflowService.cs`, `Services/DashboardService.cs`, `Services/EntregaService.cs`, `Services/ProductoService.cs`, `Services/CodigoBarrasLookupService.cs` — día de negocio.
- `Services/AfipService.cs` — reusa `ArgentinaTime.Zone`, se eliminó su `ResolverTzArgentina` duplicado.
- `Migrations/20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio.cs` — solo datos.

**Web**
- `Controllers/ClientesController.cs` — 4 acciones nuevas (GET/POST de cobro y de ajuste) + helpers de repintado.
- `Controllers/CajaController.cs` — día/mes de negocio.
- `Models/CuentaCorrienteClienteViewModels.cs` — **nuevo**.
- `Models/CajaViewModels.cs`, `Models/GastoViewModels.cs`, `Models/EntregaViewModels.cs` — defaults.
- `Views/Clientes/RegistrarCobro.cshtml`, `Views/Clientes/RegistrarAjuste.cshtml` — **nuevas**.
- `Views/Clientes/CuentaCorriente.cshtml` — botones de acción.
- `Views/Caja/Index.cshtml` — origen `CobroCC` en el filtro (LP-002).
- `Views/Ventas/Editar.cshtml` — guarda de doble envío en `guardarYContinuar`.
- `Views/Dashboard/Index.cshtml`, `Views/Productos/Edit.cshtml` — día de negocio.

**tools**
- `MigracionCatalogo/Program.cs` — modo `--solo-unidad-venta`.

#### Migraciones EF generadas

`20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio` — **solo datos, sin DDL**. Aplicada a
`laplatense_dev`. **Producción está dos migraciones atrás**: le falta esta y
`20260903160346_EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago` (el ítem 0.1, que es de
Joaquín).

#### Evidencia

- **Build de la solución: 0 errores** (`dotnet build FerreteriaLaPlatense.slnx`). Verificado que las
  vistas Razor **sí** se compilan en el build (comprobado introduciendo a propósito un símbolo
  inexistente en una `.cshtml`: el build falló; revertido), así que el build limpio también cubre las
  dos pantallas nuevas.
- **Grafo de DI validado** con `ValidateOnBuild` + `ValidateScopes` sin levantar la app:
  `CuentaCorrienteClienteService` resuelve con su dependencia nueva, sin ciclo ni captive dependency
  (ambos `Scoped`).
- **Fronteras de día/mes: 8 de 8 verificaciones ejecutadas en verde**, incluido el criterio de
  aceptación de D9 (instante UTC `2026-09-25 01:44` da día de negocio `2026-09-24`; el arqueo del 24
  la incluye y el del 25 no; y la venta de las 22:44 del 30/09 cae en el mes de septiembre).
- **Cobro/ajuste ejercitados contra `laplatense_dev` a nivel Service: 24 de 24 en verde** — el cobro
  baja la CC y genera exactamente un `Ingreso` de caja con `OrigenTipo="CobroCC"` y `OrigenId`
  correcto; el ajuste mueve el saldo y **no** genera movimiento de caja; las 4 guardas del cobro
  rechazan; con la caja cerrada el cobro y el movimiento manual quedan bloqueados; se puede cerrar un
  mes anterior y **no** el mes en curso ni uno futuro. Las filas de prueba se borraron al final (dev
  quedó en su línea base: 9 `CajaMovimientos`, 0 `MovimientosCCCliente`).
- **Ítem 0.4 corrido contra `laplatense_dev`** con los números de la tabla de arriba.
- **Sin smoke test funcional por navegador** (regla del rol). La verificación en navegador queda en
  la guía de abajo — ver la nota de discrepancia con el brief en `trazabilidad.md`.

#### Guía de verificación manual (a ejecutar por el cliente/QA, no por el Implementador)

1. **D8** — abrir un borrador de venta, cambiar la **cantidad** de un ítem sin guardar, apretar
   **Confirmar venta**: la venta queda `Confirmada` con la cantidad **que estaba en pantalla**.
   Repetir con "Confirmar y facturar". Hacer **doble click** rápido en Confirmar: tiene que confirmar
   una sola vez, nunca quedar en Borrador guardado.
2. **D9 (el criterio de aceptación)** — registrar una venta cerca de las **22:44 hora Argentina** y
   verificar que aparece en el arqueo **de ese día**, no del siguiente. Después **cerrar la caja de
   ese día** e intentar una venta nueva con esa fecha, a cualquier hora: tiene que quedar bloqueada.
3. **D9 / mensual** — el **día 1**, cerrar la caja del **mes anterior**: tiene que dejar. Intentar
   cerrar el **mes en curso**: tiene que rechazar con el mensaje de "todavía está en curso".
4. **D9 / listados** — mirar la columna Fecha de Caja y de la cuenta corriente: la hora mostrada
   tiene que ser la hora **argentina** del movimiento. Filtrar por un rango de fechas que incluya un
   movimiento nocturno y confirmar que cae del lado esperado.
5. **0.4** — en Catálogo, confirmar que ya **no hay productos en "Metro"** y abrir alguno del CSV de
   candidatos (ej. un cable) para ver que quedó en "Unidad" a la espera de la marcación manual.
6. **0.5 / cobro** — cliente con deuda, **Registrar cobro**: el importe viene **prellenado con la
   deuda**, el botón "Todo" lo repone, un importe mayor a la deuda se rechaza. Guardar y verificar
   que (a) baja el saldo, (b) aparece el movimiento `Pago` en el historial de la cuenta y (c) aparece
   un **Ingreso** en Caja filtrable por origen **"Cobro de cuenta corriente"**.
7. **0.5 / ajuste** — con usuario **Administrador**: registrar un ajuste de crédito con motivo, mueve
   el saldo y **no** aparece nada en Caja. Intentar sin motivo: rechaza.
8. **0.5 / permisos** — con usuario **Vendedor**: el botón "Ajuste manual" **no** se ve, y entrar a
   `/Clientes/RegistrarAjuste/{id}` a mano tiene que dar acceso denegado. "Registrar cobro" **sí**
   tiene que estar disponible.
9. **LP-003** — guardar un cobro, volver a abrir el formulario y mirar que los inputs numéricos **no**
   quedan vacíos.

#### Riesgos y supuestos (Sprint 0)

- **La migración de datos D9 asume el discriminador de la medianoche exacta.** Verificado contra
  `laplatense_dev` (4 filas, todas legítimas). En producción el volumen es chico pero **conviene
  mirar el conteo antes de aplicar**: `SELECT OrigenTipo, COUNT(*) FROM CajaMovimientos WHERE
  TIME_TO_SEC(TIME(Fecha))=0 AND MICROSECOND(Fecha)=0 GROUP BY OrigenTipo`.
- **`Gasto.Fecha` y `CierreCajaDiario.Fecha` siguen siendo fechas calendario** (día de negocio
  argentino), no instantes. Es deliberado y está documentado en el código: son columnas de semántica
  date-only. No se las tocó ni se las debe proyectar.
- **El ajuste de CC no impacta Caja, por diseño.** Si el cliente lo usa para registrar un cobro real,
  la caja va a quedar corta. Mitigado en el texto de la pantalla, no por código.
- **El cobro no registra la cuenta real donde entró la plata** (MH-034). El medio de pago queda en la
  descripción del movimiento, pero el ledger de caja sigue siendo único y sin dimensión "cuenta".
  Consistente con lo que ya hace Ventas; si el negocio necesita conciliar, es un cambio de alcance
  aparte.
- **No se tocó la vigencia de oferta más allá de cambiar el "hoy"**, ni el circuito AFIP (sigue
  deshabilitado, sin certificado).

#### Hallazgo fuera de alcance, para decidir (CERRADO el 2026-10-05 en el commit `7477550`)

`DashboardService` contaba las ventas del día y del mes filtrando **solo**
`Estado == EstadoVenta.Facturada`. Se resolvió con el criterio anticipado acá
(`Confirmada || Facturada`), junto con el mismo filtro en `ClasificacionAbcAutomaticaService`.
Queda como antecedente de por qué apareció después `LP-008`: el código se corrigió pero los
comentarios prescriptivos que explicaban el criterio viejo no, y dejaron una regla de negocio
falsa en el repo (ver la sección siguiente).
### Sprint 0 — ronda de fixes de QA: los 7 defectos abiertos (2026-10-05, rama `entrega-1-migracion`)

Cierre de los 7 partes de defecto que dejaron los 3 lotes de QA del Sprint 0 (`LP-006` a `LP-012`
en `docs/qa/regresiones-manuales.yml`; parte completo en `6-qa.md`). El lote 1 (día/mes de negocio)
había dado **NO-GO** con 2 `major` en el circuito de dinero, y el deploy a producción estaba
bloqueado hasta cerrarlos. **Un solo commit** (`00f7dd4`), **sin migración EF** — no se modificó el
modelo de datos (verificado con `dotnet ef migrations has-pending-model-changes`: *"No changes have
been made to the model since the last migration"*).

#### Resultado del escaneo de reutilización

Paso 1 (`docs/patrones/cat_resumen.txt`): dos matches directos, los dos aplicados.

- **`PAT-010`** (ArgentinaTime, hora correcta en hosting compartido) — es la pieza que ya centraliza
  la convención; `LP-009`/`LP-010`/`LP-011` se resuelven **ampliándola**, no construyendo nada nuevo.
- **`PAT-016`** (búsqueda global multi-formato + filtros persistidos en Session) — `LP-012` es
  exactamente su caso de uso; se portó la implementación que ya está en los 6 listados de este mismo
  repo (`BusquedaHelper` + `FiltrosSessionHelper` + `window.Filtros`), sin escribir helpers nuevos.

No se agregó ningún patrón al catálogo: todo lo implementado es aplicación de patrones ya
catalogados o corrección puntual de este sistema.

#### `LP-009` (major) — la guarda de caja cerrada ignoraba el cierre mensual

Causa confirmada: la guarda consultaba **únicamente** `CierresCajaDiarios`. El commit `628cb7a`
había agregado la mitad "no se puede cerrar el mes en curso ni uno futuro" y dejó afuera la
simétrica "no se puede imputar a un mes ya cerrado" — son la misma regla vista de los dos lados.

**Pieza nueva, una sola y compartida:** `ICajaMovimientoService.ValidarPeriodoAbiertoAsync(diaDeNegocio, accion)`,
que consulta **mes y día** y devuelve `null` si el período está abierto o el **mensaje listo para
mostrar** si está cerrado (más `EstaMesCerradoAsync(anio, mes)`, que antes era una consulta inline
dentro de `CerrarMesAsync`). Se eligió que devuelva el mensaje y no un bool para que ninguna vía de
escritura pueda redactar el suyo y divergir: el parámetro `accion` completa la frase
(*"La caja del mes 09/2026 ya tiene cierre mensual: no se puede registrar un gasto con esa fecha."*).
El mes se consulta **antes** del día: es el bloqueo más fuerte (abarca días que individualmente
pueden no tener cierre diario) y es el mensaje que al usuario le explica de verdad por qué no puede
imputar ahí.

**Todas las vías de escritura de caja quedaron cubiertas** (no solo la que reportó QA), relevadas
por los usos de `EstaCerradoAsync`:

| Vía de escritura | Archivo | Día de negocio que valida |
|---|---|---|
| Venta confirmada (es el paso que mueve caja; `FacturarAsync` no la toca) | `VentaWorkflowService.ConfirmarAsync` | `ArgentinaTime.Hoy` |
| Gasto — alta | `GastoService.CrearAsync` | `dto.Fecha` (la que eligió el usuario) |
| Gasto — anulación (contramovimiento fechado hoy) | `GastoService.AnularAsync` | `ArgentinaTime.DiaDeNegocio(ahora)` |
| Cobro de cuenta corriente | `CuentaCorrienteClienteService.RegistrarCobroAsync` | `dto.Fecha` |
| Movimiento manual de caja | `CajaMovimientoService.RegistrarMovimientoManualAsync` | `dto.Fecha` |
| Cierre diario (no es un movimiento, pero no puede abrirse dentro de un mes cerrado) | `CajaMovimientoService.CerrarDiaAsync` | `fechaDia` |

**Decidido NO cubrir, con motivo:** `CuentaCorrienteClienteService.RegistrarAjusteAsync` **no** lleva
la guarda, porque por diseño explícito no toca Caja (un ajuste corrige el ledger de la deuda, no
representa plata que entró o salió — ver su XML-doc). No es una vía de escritura de caja.

#### `LP-010` (major) — `Venta.Fecha` quedó con la semántica vieja

Decisión ya cerrada por el orquestador y aplicada tal cual: `Venta.Fecha` sigue el **mismo** criterio
que `CajaMovimiento.Fecha` — instante UTC en la base, día de negocio derivado proyectando a ART con
`ArgentinaTime`. Sin una segunda convención, y **sin migración de datos**: la columna ya guardaba
`DateTime.UtcNow`, lo que estaba mal era **cómo se consumía**.

Cuatro puntos de consumo corregidos en `VentaWorkflowService`, más el XML-doc de la entidad:

1. **Filtros `fechaDesde`/`fechaHasta`**: comparaban la columna UTC contra la medianoche cruda del
   día elegido → ahora `ArgentinaTime.InicioDiaUtc(...)` en los dos extremos (hasta inclusive).
2. **Proyección del listado**: se materializa la página ya paginada en un tipo anónimo y recién
   después se proyecta `Fecha = ArgentinaTime.From(...)` — la conversión no se traduce a SQL. Mismo
   patrón exacto que `CajaMovimientoService.ListarMovimientosAsync`.
3. **Buscador global por fecha** (`PAT-016`): comparaba `Year`/`Month`/`Day` de la columna cruda
   (= día calendario UTC) contra el día que tipeó el usuario (= día argentino) → ahora
   `ArgentinaTime.RangoDiaUtc(fecha)`.
4. **Detalle** (`MapearDetalleAsync`): `Fecha = ArgentinaTime.From(venta.Fecha)`.

Verificado además que **`Venta.Fecha` nunca se escribe desde un DTO ni desde un ViewModel** (solo el
inicializador `= DateTime.UtcNow` de la entidad), así que no hay round-trip que pueda re-persistir el
valor ya proyectado a ART como si fuera UTC. El `OrderBy` sigue sobre la columna UTC a propósito: el
offset es fijo, así que el orden UTC y el orden ART son idénticos.

#### Barrido `LP-002` de la convención de fechas — resultado completo

Es la **segunda** vez en el sprint que un barrido `LP-002` queda incompleto (la primera fue el
Dashboard/ABC), así que se relevaron **todas** las propiedades `DateTime` de `Domain/Entities` y
todos sus sitios de uso, no solo `Venta`. Tabla de cierre:

| Entidad.Campo | Semántica en base | Estado |
|---|---|---|
| `CajaMovimiento.Fecha` | instante UTC | OK (D9) |
| `MovimientoCCCliente.Fecha` | instante UTC | OK (proyecta con `From`, filtra por rango UTC) |
| `Venta.Fecha` | instante UTC | **corregido acá** (`LP-010`) |
| `AjusteStock.Fecha` | instante UTC | **corregido acá** — el historial de stock la mostraba cruda con hora |
| `Entrega.FechaEntregada` | instante UTC | **corregido acá** — el detalle de entrega la mostraba cruda con hora |
| `ApplicationUser.CreatedAt` | instante UTC | **corregido acá** — listado y detalle de usuarios (campo de auditoría, no de negocio, pero misma convención) |
| `Gasto.Fecha` | día calendario ART | OK (se guarda y se compara como día) |
| `Gasto.FechaAnulacion` | instante UTC | OK — no se muestra en ninguna pantalla |
| `CierreCajaDiario.Fecha` | día calendario ART | OK |
| `CierreCajaDiario/Mensual.FechaCierre` | instante UTC | OK (proyecta con `From`) |
| `Entrega.FechaProgramada` | día calendario ART | OK (se guarda con `.Date`, se filtra como día) |
| `PagoVenta.Fecha` | instante UTC | OK — no se expone en ningún DTO |
| `Producto.PrecioOfertaDesde/Hasta` | día calendario ART | OK (vigencia cortada contra `ArgentinaTime.Hoy`) |
| `Venta.VencimientoCAE` | fecha pura de AFIP (`yyyyMMdd`) | OK — no es un instante, no se proyecta |
| `Notification.CreatedAt`/`ReadAt`, `SoftDestroyable.*`, `ApplicationUser.UpdatedAt` | instante UTC | OK — auditoría, no se renderiza |

**Tres hallazgos propios** (`AjusteStock.Fecha`, `Entrega.FechaEntregada`,
`ApplicationUser.CreatedAt`), los tres corregidos en este mismo commit como pedía el parte.

#### `LP-007` (minor) — un valor desconocido de `continuar` era un no-op silencioso

El `switch` del POST de Venta resolvía el `default` como "guardar y listo", así que un valor
desconocido devolvía HTTP 200 con el mensaje de guardado mientras la venta quedaba abierta sin que
nadie se enterara. Ahora **solo la ausencia del campo** significa "guardar el borrador"
(`null or ""`, con `Trim()` previo) y cualquier otro valor cae en `AccionNoReconocida`.

**Decisión de criterio propio:** no se devuelve `BadRequest` seco. Cuando se llega a ese punto el
borrador **ya quedó guardado**, así que un 400 haría pensar que no se guardó nada; se redirige a
`Editar` con `TempData["ErrorMessage"]` diciendo explícitamente *"el borrador se guardó pero la venta
NO se cerró"*. Cumple el criterio (nunca un 200 que parece éxito) y no miente sobre el estado real.
Verificado que el botón "Guardar borrador" (un `type="submit"` que no agrega el hidden) sigue
cayendo en la rama de guardado normal.

Se corrigió además el **comentario** de `Views/Ventas/Editar.cshtml` que afirmaba la premisa que QA
refutó (que el doble click posteaba `"confirmar,confirmar"` — el model binder toma el primer valor).
La guarda de reentrada **se queda**, porque lo que previene sí es real: dos POST de cierre en vuelo
sobre la misma venta, donde el segundo encuentra la venta fuera de `Borrador` y le muestra un error
innecesario al vendedor. El comentario ahora dice ese motivo, no el inventado.

#### `LP-008` (minor) — comentarios que contradecían el código

`ClasificacionAbcAutomaticaService` (XML-doc de clase + comentario previo al `Where`) y
`DashboardService` (XML-doc de `ObtenerTopProductosMesAsync`) seguían afirmando que *"solo cuentan
los ítems en estado `Facturada`"* y que *"el filtro por `Estado == Facturada` es imprescindible"*,
cuando el código ya filtra `Confirmada || Facturada` desde `7477550`. Son prescriptivos, así que
dejaban una **regla de negocio falsa** en el repo.

**Corregidos, no borrados**: se conserva (y se explicita mejor) la parte válida —por qué `Borrador` y
`Anulada` quedan afuera, que un borrador abandonado infla la rotación y sube la clase ABC— y se
agrega por qué `Confirmada` **tiene que** estar: es el estado normal de una venta cerrada, la factura
es un paso posterior y opcional, y dejarla afuera subcontaba la rotación real. Se arregló también la
referencia cruzada rota (`DashboardService.ObtenerProductosMasVendidos`, que no existe → es
`ObtenerTopProductosMesAsync`).

#### `LP-006` (minor) — reloj de 12 horas sin AM/PM

No era un problema de huso: el wire ya entrega la fecha proyectada a ART. Era `toLocaleString('es-AR')`
a secas en el cliente, que usa reloj de 12 h sin meridiano (13:04 → `01:04:22`, 00:00 → `12:00:00`).

**Pieza nueva:** `window.Fmt` en `site.js`, con `fechaHora(v)` (`hour12: false`, sin segundos — en una
grilla no aportan) y `fecha(v)` para las columnas que son día calendario. Las dos toleran null y fecha
inválida. Se reemplazaron los **8** renders de fecha de las grillas (`Caja/Index`, `Caja/Cierres` ×2,
`Clientes/CuentaCorriente`, `Stock/Historial`, `Ventas/Index`, `Gastos/Index`, `Entregas/Index`) para
que el formato no vuelva a divergir pantalla por pantalla. Se incluyeron también los renders de solo
fecha, que no tenían el bug: el objetivo es que no quede ningún `toLocaleString`/`toLocaleDateString`
de fecha suelto en las vistas.

#### `LP-011` (minor) — `/Caja/Mensual?mes=13` devolvía HTTP 500

La validación *"Mes o año inválido"* de `628cb7a` era **código muerto para este GET**: el `mes=13`
llegaba hasta `ArgentinaTime.RangoMesUtc` → `new DateTime(anio, 13, 1)` →
`ArgumentOutOfRangeException`, mucho antes de llegar a ella (la validación vivía solo en
`CerrarMesAsync`).

Resuelto poniendo el rango válido en un único lugar —`ArgentinaTime.EsMesDeNegocioValido(anio, mes)`
(2000–2999, 1–12)— consultado **tanto** por el GET de la pantalla **como** por `CerrarMesAsync`, para
que las dos no puedan divergir. El GET inválido ahora redirige al mes en curso con
`TempData["ErrorMessage"]` (el redirect no lleva parámetros, así que no puede reciclar). Se documentó
el precondicional en el XML-doc de `RangoMesUtc`.

#### `LP-012` (minor) — buscador que no buscaba en los listados de cierres

**Corresponde `PAT-016`**: las dos pantallas dibujaban el buscador del DataTable (está activo por
defecto) y los Services ignoraban `request.SearchValue`. Se aplicó igual que en los otros 6 listados,
en vez de sacar el control.

| Listado | Columna de texto en el OR final | `extraIds` (importe) | `extraIds` (fecha) | `extraIds` (otros) |
|---|---|---|---|---|
| **Cierres diarios** | `FullName` del usuario que cerró | `TotalIngresos`/`TotalEgresos`/`Saldo` (rango + substring) | `Fecha` (día calendario, comparación directa) **y** `FechaCierre` (instante UTC, rango del día de negocio) | — |
| **Cierres mensuales** | `FullName` del usuario que cerró | `TotalIngresos`/`TotalEgresos`/`Saldo` (rango + substring) | — (no hay columna de fecha en la grilla) | `Anio` tipeado; nombre del mes (`"septiembre"` → `Mes == 9`) |

**`MH-001` evitado, y por qué fue el riesgo real de este ítem.** La única columna de texto de las dos
grillas es el nombre del usuario que cerró, que vive en `AspNetUsers` y **no tiene navegación** desde
las entidades de cierre. El camino intuitivo —resolver los ids de usuario que matchean y filtrar con
`CerradoPorUsuarioId IN (...)`— es exactamente `MH-001`: un `IN` sobre colección local de **string**,
que en este provider revienta incluso con la colección vacía (ya pasó 4 veces acá, y está documentado
en el propio `ListarCierresDiariosAsync`). Se resolvió con una **sub-consulta correlacionada**
(`_context.Users.Any(u => u.Id == c.CerradoPorUsuarioId && u.FullName.Contains(termino))`), que se
traduce entera a SQL y nunca trae una colección a memoria. **Traducción verificada sin levantar la
app ni conectar a ninguna base**, con `ToQueryString()` sobre el `DbContext` configurado con el
provider real: baja a `EXISTS (SELECT 1 FROM AspNetUsers AS a WHERE a.Id = c.CerradoPorUsuarioId AND
(... LOCATE(...) > 0))`. En el listado mensual, el match por nombre de mes también se armó como un
`Where(c => c.Mes == mes)` por mes encontrado, en vez de un `Contains` sobre la lista local de ≤12
ints — la forma prohibida no se usa ni donde sería inocua.

**`PAT-016` parte 2 (filtros en Session)** aplicada a los dos listados, con las keys
`CierresDiarios_*` (FechaDesde, FechaHasta, Busqueda) y `CierresMensuales_*` (Anio, Busqueda), más el
botón "Limpiar filtros" funcional de punta a punta (`limpiar=true` una sola vez en el draw del click,
`window.Filtros.limpiarBuscador` para vaciar el `<input>` visible).

**Gap de diseño cerrado de paso:** `MensualListar` leía un filtro `anio` del form que **la vista nunca
mandaba** (filtro muerto desde que se escribió). Se agregó el control de Año al header del listado de
cierres mensuales, con su botón de limpiar — por la regla del rol de que el usuario tiene que poder
filtrar por lo que ve en la grilla (la columna "Período" muestra mes y año). Sin `value` en el
`<input type="number">`, así que `LP-003`/`D5` no aplica: el valor se repone por JS desde Session.

#### Archivos y capas modificadas

- *Domain*: `Entities/Venta.cs` (**solo XML-doc** de la convención de `Fecha` — sin cambio de modelo).
- *Application*: `Helpers/ArgentinaTime.cs` (`EsMesDeNegocioValido` + precondición de `RangoMesUtc`),
  `Interfaces/ICajaMovimientoService.cs` (`EstaMesCerradoAsync`, `ValidarPeriodoAbiertoAsync`).
- *Infrastructure*: `Services/CajaMovimientoService.cs` (guarda de período, las dos búsquedas globales
  de cierres, `NombresMes`), `VentaWorkflowService.cs` (`LP-009` + los 4 puntos de `LP-010`),
  `GastoService.cs`, `CuentaCorrienteClienteService.cs` (guarda de período), `AjusteStockService.cs`,
  `EntregaService.cs` (barrido `LP-002`), `ClasificacionAbcAutomaticaService.cs`,
  `DashboardService.cs` (`LP-008`).
- *Web*: `Controllers/CajaController.cs` (`LP-011` + Session de los 2 listados),
  `Controllers/VentasController.cs` (`LP-007`), `wwwroot/js/site.js` (`window.Fmt`),
  `Views/Caja/Cierres.cshtml`, `Views/Caja/Mensual.cshtml` (`LP-012` + `LP-006`),
  `Views/Caja/Index.cshtml`, `Views/Clientes/CuentaCorriente.cshtml`, `Views/Stock/Historial.cshtml`,
  `Views/Ventas/Index.cshtml`, `Views/Gastos/Index.cshtml`, `Views/Entregas/Index.cshtml` (`LP-006`),
  `Views/Users/Index.cshtml`, `Views/Users/Details.cshtml` (barrido `LP-002`),
  `Views/Ventas/Editar.cshtml` (comentario de `LP-007`).

#### Migración EF

**Ninguna.** `dotnet ef migrations has-pending-model-changes` → *"No changes have been made to the
model since the last migration"*. Tampoco hizo falta migración **de datos**: `Venta.Fecha` ya guardaba
instantes UTC correctos; el defecto era de consumo, no de almacenamiento.

#### Evidencia de build y de verificación técnica

- `dotnet build FerreteriaLaPlatense.slnx` → **0 errores**, 9 advertencias, **todas preexistentes**
  (8 × `NU1902` de MailKit/MimeKit + `CS0114` de `HomeController.StatusCode`). Corrido 3 veces: tras
  la primera tanda de cambios, tras el comentario de `Editar.cshtml`, y tras normalizar los BOM que
  había introducido el script de reemplazo masivo en las vistas. Las vistas Razor pasan por el
  compilador en el build, así que no quedan errores de vista para runtime.
- **Traducción a SQL verificada con `ToQueryString()`** (no es un smoke test: no levanta la app ni abre
  conexión a ninguna base) para las 5 formas de consulta nuevas o modificadas que podían no traducir:
  la sub-consulta correlacionada de usuario en los dos listados de cierres, la misma combinada con
  `ids.Contains` de `extraIds`, el filtro por rango UTC de `Venta.Fecha` con la proyección anónima, y
  el OR de los 3 importes de cierres. Las 5 bajan a SQL válido.
- **No se ejecutó smoke test funcional** (regla del rol): la verificación por navegador la hace QA. Lo
  que sí se verificó por lectura dirigida: que `Venta.Fecha` no se escribe desde ningún DTO/ViewModel,
  que "Guardar borrador" no cae en la rama de error nueva de `LP-007`, y los 15 campos `DateTime` de
  la tabla del barrido `LP-002`.
- **Producción intacta**: no se ejecutó ningún deploy, ni Web Deploy, ni ninguna operación contra
  `mysql8001.site4now.net`. La base `laplatense_qa_d9` que QA dejó como fixture **no se tocó ni se
  borró**.

#### Riesgos residuales y asunciones

- **`ValidarPeriodoAbiertoAsync` hace 2 consultas** (mes y día) donde antes había 1. Son dos `EXISTS`
  sobre tablas chicas con índice (`IX_CierresCajaMensuales_Anio_Mes`, `IX_CierresCajaDiarios_Fecha`) y
  corren una vez por operación de escritura, no por fila. Impacto despreciable.
- **La UI no avisa de antemano que un mes está cerrado.** El rechazo es claro y llega al guardar, que
  es lo que pide el criterio de aceptación, pero el formulario de movimiento manual deja elegir una
  fecha de un mes cerrado y recién al enviar explica el problema. Mostrar el estado del mes en la
  pantalla de Caja sería una mejora de UX — **no se hizo para no ampliar alcance**; queda anotado.
- **El mensaje de `GastoService.AnularAsync` cambió**: antes decía *"no se puede anular un gasto hasta
  el próximo día hábil"*, ahora *"no se puede anular un gasto hoy"*. Es más veraz (el día siguiente
  podría estar cerrado también) pero es un texto distinto del que QA vio en el lote anterior.
- **Búsqueda por nombre de mes en cierres mensuales**: se compara contra la etiqueta real de la grilla
  con la normalización de `BusquedaHelper` (sin tildes ni mayúsculas), así que `"septiembre"` matchea
  pero `"setiembre"` **no**. Decisión deliberada: la grilla dice "Septiembre".
- **`Venta.Fecha` sigue siendo el momento en que nació el BORRADOR**, no el de la confirmación. Una
  venta empezada el día N y confirmada el N+1 aparece en el día N en Ventas y en el N+1 en Caja. Es
  comportamiento preexistente, ajeno a `LP-010` (que era de proyección, no de qué instante se guarda),
  y no está en ningún parte de defecto — **si el negocio espera otra cosa, es una decisión de
  Joaquín**, no un bug de esta ronda.
- **`ApplicationUser.CreatedAt` se proyectó desde la vista**, no desde un Service: `UserListViewModel`/
  `UserDetailsViewModel` exponen la entidad y no hay un mapeo intermedio donde ponerlo. Es un campo de
  auditoría, así que no se agregó una capa de DTO solo para esto.

#### Pruebas mínimas requeridas para QA (re-verificación)

1. **`LP-009`** — con un mes cerrado (el fixture `laplatense_qa_d9` ya tiene 09/2026 cerrado), probar
   las **6** vías con fecha dentro de ese mes: movimiento manual de caja, gasto nuevo, anulación de
   gasto, cobro de cuenta corriente, confirmación de venta y cierre diario. Las 6 tienen que rechazar
   con el mensaje del **mes** (*"ya tiene cierre mensual"*). Verificar además que el ledger de egresos
   de la pantalla vuelva a coincidir con el total real (el defecto mostraba $777,77 contra $8.555,54).
2. **`LP-009` regresión** — con el mes **abierto** y un **día** cerrado, las mismas 6 vías tienen que
   seguir rechazando con el mensaje del **día**; con los dos abiertos, tienen que seguir funcionando.
3. **`LP-010`** — la Venta 8 (24/08 22:44 ART) tiene que verse **24/08** en el listado de Ventas, en su
   detalle, en Caja y en el Dashboard. Las tres pantallas tienen que decir lo mismo.
4. **`LP-010`** — filtrar Ventas por el rango `24/08 - 24/08` tiene que traer esa venta, y tipear
   `24/08/2026` en el buscador global también. Con `25/08` no tiene que aparecer.
5. **Barrido `LP-002`** — historial de ajustes de stock, detalle de una entrega finalizada y listado/
   detalle de usuarios: todas las fechas con hora tienen que mostrar el día y la hora argentinos
   (probar con un registro creado entre las 21:00 y las 24:00 ART).
6. **`LP-007`** — postear a `Ventas/GuardarBorrador` con `continuar=cualquier-cosa` (DevTools o un
   form armado a mano) tiene que mostrar el error explícito, **no** el mensaje de guardado. Y los 3
   caminos normales (Guardar borrador / Confirmar / Confirmar y facturar) tienen que seguir igual.
7. **`LP-006`** — un cobro de las 13:04 tiene que leerse `13:04` (no `01:04`) y un movimiento de las
   00:00 tiene que leerse `00:00` (no `12:00`), en el ledger de CC **y** en `/Caja`. Revisar también
   Ventas, Historial de stock y los dos listados de cierres.
8. **`LP-011`** — `/Caja/Mensual?mes=13`, `?mes=0`, `?anio=99999`, `?anio=1` y `?mes=abc` tienen que
   mostrar el mensaje de mes inválido y el mes en curso, nunca un 500. Y `?anio=2026&mes=9` tiene que
   seguir funcionando.
9. **`LP-012`** — en los dos listados de cierres, buscar por: importe con y sin formato (`1.500,50`,
   `1500.50`, `1500`), substring de importe (`500` tiene que traer `$ 1.500,00`), fecha `dd/MM/yyyy`
   (en el diario tiene que matchear tanto la fecha del cierre como la fecha de ejecución), nombre del
   usuario que cerró, año (`2026`) y nombre del mes (`septiembre`, solo en el mensual).
10. **`LP-012`** — dejar filtros y buscador puestos en los listados de cierres, navegar a otra pantalla
    y volver: tienen que estar como se dejaron y la grilla ya filtrada en el primer draw. El botón
    Limpiar tiene que vaciar los controles **y** el texto del buscador, y al volver a entrar no
    reponer nada. Verificar que el filtro de Año nuevo del listado mensual filtra de verdad.
11. **Regresión `MH-001`** — abrir los dos listados de cierres **sin ningún filtro ni búsqueda** y con
    búsqueda puesta: ninguno de los dos casos puede tirar `InvalidOperationException`.
12. **Regresión `PAT-016`** — los 6 listados que ya tenían búsqueda global (Ventas, Clientes,
    Productos, Caja, Gastos, Entregas) tienen que seguir funcionando igual, con especial atención a
    Ventas, cuyo filtro y buscador por fecha cambiaron de criterio.

#### Checklist de salida para merge

- [x] Build de la solución en 0 errores, sin advertencias nuevas.
- [x] Sin migración EF (verificado con `has-pending-model-changes`).
- [x] Traducción a SQL verificada para las consultas nuevas (`ToQueryString`).
- [x] `MH-001` revisado en todo el código nuevo: cero `IN`/`.Contains()`/`Any()` sobre colección local.
- [x] `LP-002`: barrido completo de la convención de fechas, con tabla de cierre de las 15 propiedades.
- [x] `LP-003`/`D5`: el único `<input type="number">` nuevo no lleva `value` server-side.
- [x] `PAT-016` aplicado con el mismo criterio que los 6 listados existentes.
- [x] Un solo commit (`00f7dd4`) en `entrega-1-migracion`, sin tocar producción ni el fixture de QA.
- [ ] **Re-verificación de QA de los 7 defectos** — pendiente, la declara QA en contexto nuevo.
- [ ] **Deploy a producción** — sigue bloqueado hasta el GO de QA; lo aprueba Joaquín aparte.

#### Partes de defecto aplicados en esta corrida

Los 7, **"aplicado, pendiente de re-verificación"** — el cierre lo declara QA, nunca el Implementador:

| id | sev | Archivos principales |
|---|---|---|
| `LP-009` | major | `ICajaMovimientoService`, `CajaMovimientoService`, `VentaWorkflowService`, `GastoService`, `CuentaCorrienteClienteService` |
| `LP-010` | major | `Venta`, `VentaWorkflowService`, `AjusteStockService`, `EntregaService`, `Views/Users/*` |
| `LP-007` | minor | `VentasController`, `Views/Ventas/Editar.cshtml` |
| `LP-008` | minor | `ClasificacionAbcAutomaticaService`, `DashboardService` |
| `LP-006` | minor | `wwwroot/js/site.js` + 8 vistas de listado |
| `LP-011` | minor | `ArgentinaTime`, `CajaController`, `CajaMovimientoService` |
| `LP-012` | minor | `CajaMovimientoService`, `CajaController`, `Views/Caja/Cierres.cshtml`, `Views/Caja/Mensual.cshtml` |
### Sprint 0 — gate de precio por rol en Ventas (2026-10-05, rama `entrega-1-migracion`)

**Defecto corregido.** Cualquier usuario con la política `RequireVentas` (incluido el rol `Vendedor`) podía vender a cualquier precio: `VentasController.GuardarBorrador` tomaba `Items[].PrecioUnitario`, `Items[].Descuento` y `Items[].Recargo` del formulario y `VentaWorkflowService.GuardarBorradorAsync` los persistía sin ningún control de rol. Un vendedor podía postear `PrecioUnitario = 1` y confirmar: descontaba stock y posteaba Caja y cuenta corriente al precio que eligió. Estaba abierto en producción.

**Precedente reutilizado.** `marihogar` (`C:/Sistemas/marihogar`, ya en producción), `VentaService.ConfirmarAsync` (~407-465) y `EditarAsync` (~738-773), identificado como CR-22. Se copió el criterio: un booleano `esAdministrador` resuelto **solo** en el Controller con `User.IsInRole`, pasado al Service como dato explícito (el Service no consulta Identity), y que es la **única** puerta que habilita leer del payload los campos de precio. Lo que **no** se trajo de marihogar: la cascada `(1-d/100)*(1+r/100)` (acá la fórmula comercial correcta es `(1 - d/100 + r/100)` sobre precio de lista, corregida el 2026-09-03) y su manejo de subtotal (el de La Platense, con el subtotal c/IVA editable que despeja el precio unitario hacia atrás, es mejor y se queda).

**Qué hace el gate.**

| Rol | Precio unitario | Descuento / Recargo | Subtotal c/IVA editable |
|---|---|---|---|
| `Administrador`, `SuperUsuario` | override desde el formulario (como hasta hoy) | override, validados en 0..100 | sí (entra por `PrecioUnitario`) |
| `Vendedor` y cualquier otro rol/caller | resuelto server-side desde el `Producto` | forzados a 0 | no |

Para un vendedor los tres campos del payload **se descartan en silencio**, no con un error: no es un error del usuario, la UI simplemente no se lo deja editar. Corolario deliberado: un descuento fuera de rango (>100%) posteado por un vendedor **no** devuelve el mensaje de validación, se ignora; para un administrador sigue rechazando.

**Qué precio es "el del producto".** `VentaWorkflowService.PrecioDeVentaVigente(producto)`: `PrecioOferta` si la oferta está vigente hoy (`Producto.EsOfertaVigente(ArgentinaTime.Hoy)`, día de negocio argentino) **y** es `> 0`; si no, `PrecioVenta`. Es exactamente la misma resolución que ya hacía la pantalla al agregar un ítem (`producto.precioOferta || producto.precioVenta` en `Views/Ventas/Editar.cshtml`, sobre el `PrecioOferta` que `ProductoService.BuscarParaVentaAsync` y `CodigoBarrasLookupService.BuscarPorCodigoAsync` ya filtran por vigencia), de modo que el vendedor termina con el precio que la UI le mostró y no con otro. El `> 0` no es decorativo: replica el `||` de JavaScript, que con una oferta cargada en 0 cae igual a `PrecioVenta` — sin esa condición el servidor cobraría 0 donde la pantalla mostró el precio de lista. **Los dos caminos de la UI (buscador Select2 y lector de código de barras) usan la misma resolución, así que no hubo que elegir ninguno a dedo.** Quedó anotado en los dos lados que si se cambia una hay que cambiar la otra.

**Barrido `LP-002` — puntos de entrada del precio relevados.** Cuatro pasadas, no solo el grep obvio:

1. **Puntos de entrada del precio (grep de `PrecioUnitario` sobre `Application/`, `Domain/`, `Infrastructure/`, `Web/`).** `GuardarBorradorAsync` es el **único** método que escribe `ItemVenta` y por lo tanto el único punto de entrada del precio. `ConfirmarAsync`, `FacturarAsync` y `ConfirmarYFacturarAsync` trabajan sobre lo ya persistido y nunca leen el payload; `Details.cshtml` es solo lectura. El subtotal c/IVA editable **no tiene atributo `name`**: no se postea, la UI lo despeja sobre `PrecioUnitario` client-side, así que el gate de `PrecioUnitario` lo cubre por elevación y no hacía falta un segundo control.
2. **Hermanos semánticos del mismo payload.** `Items[].PorcentajeIVA` sigue llegando del cliente para los dos roles → **hueco hermano, deuda abierta** (ver abajo). `Pagos[].PorcentajeRecargoAplicado` ya se resolvía server-side vía `IRecargoCuotasService` (precedente del mismo patrón, dentro del mismo método). `Pagos[].Monto` se dejó como está: es lo que el cliente pagó, no un precio, y `ConfirmarAsync` valida que los pagos cubran el total salvo que haya una línea de cuenta corriente. `ClientesController.RegistrarCobro` queda en `RequireVentas` a propósito (decisión previa documentada en ese archivo) y `RegistrarAjuste` ya era `RequireAdministracion`.
3. **Comentarios y XML-doc (el fallo de `LP-008`).** Encontrado y corregido un comentario prescriptivo **falso** preexistente: `ItemVenta` declaraba la fórmula en **cascada** `Cantidad*PrecioUnitario*(1-Descuento/100)*(1+Recargo/100)` en dos lugares (encabezado de clase y doc de `Subtotal`), cuando la fórmula real desde el 2026-09-03 es `(1 - Descuento/100 + Recargo/100)`. Era una regla de negocio falsa viviendo en el repo, exactamente el patrón de `LP-008`. Actualizados además los docs de `ItemVentaInputDto`, `ItemVentaDto.SubtotalConIva`, `ItemVentaViewModel.SubtotalConIva` e `IVentaWorkflowService.GuardarBorradorAsync` para que digan el nuevo criterio de rol.
4. **La mitad simétrica.** El otro lado del gate es la **reapertura** de un borrador: si un administrador dejó un override de precio y después un `Vendedor` re-guarda ese mismo borrador, el precio vuelve al del producto y el descuento/recargo a 0 — el override se pierde. Es la consecuencia inevitable de copiar el criterio de marihogar ("para un no-administrador el precio SIEMPRE se recalcula") y se eligió a propósito por sobre la alternativa de conservar el valor persistido, que sería un agujero (un vendedor podría fijar un precio y después mantenerlo). Está verificado por ejecución y anotado como riesgo operativo.
5. **Vistas y JS.** `Views/Ventas/Editar.cshtml`: precio, descuento, recargo y subtotal van en `readonly` cuando el usuario no es administrador, en las filas que renderiza Razor **y** en las que arma el JS (`agregarFilaItem`), más el texto de ayuda reemplazado por uno que explica que el precio lo toma el sistema. Se usó `readonly` y **no** `disabled` a propósito: un input `disabled` no se postea y rompe los índices contiguos `0..N-1` que exige el model binder de `List<T>`. La UI es cortesía — el control que vale es el del servidor.

**Reglas del catálogo aplicadas.**
- `LP-002`: las 5 pasadas de arriba.
- `MH-001`: la única colección local que llega al SQL de este método es `productoIds` (`List<int>`), que la regla declara explícitamente segura (el problema es específico de colecciones de `string`). No se introdujo ningún `Contains`/`Any` nuevo.
- `LP-003`: no se agregó ningún `value` de input nuevo; los existentes ya usaban el helper `num()` con `InvariantCulture` y se mantuvieron intactos. El atributo agregado es `readonly`, que no transporta decimales.

**Archivos y capas modificadas.**

| Capa | Archivo | Motivo |
|---|---|---|
| Domain | `Domain/Entities/ItemVenta.cs` | Solo documentación: corrección del comentario prescriptivo falso de la fórmula + nota del gate. |
| Application | `Application/DTOs/VentaDtos.cs` | `GuardarVentaBorradorDto.EsAdministrador` (`init`) + XML-doc del gate en los campos de precio. |
| Application | `Application/Interfaces/IVentaWorkflowService.cs` | Contrato: `GuardarBorradorAsync` declara que es el único punto de entrada del precio y qué hace el gate. |
| Infrastructure | `Infrastructure/Services/VentaWorkflowService.cs` | El gate propiamente dicho dentro del loop de ítems + helper `PrecioDeVentaVigente`. |
| Web | `Web/Controllers/VentasController.cs` | `EsAdministrador()` con `User.IsInRole` y su paso al DTO. |
| Web | `Web/Models/VentaViewModels.cs` | Solo documentación del subtotal restringido. |
| Web | `Web/Views/Ventas/Editar.cshtml` | `readonly` por rol en Razor y en el JS, texto de ayuda por rol. |

**Migración EF: ninguna.** No hay cambio de modelo — `dotnet ef migrations has-pending-model-changes` responde *"No changes have been made to the model since the last migration"*. El gate no recalcula nada histórico: las ventas ya existentes (Confirmada/Facturada) no son editables y ningún camino las toca.

**Evidencia ejecutada (sin navegador, según la regla del rol).**
- `dotnet build FerreteriaLaPlatense.slnx`: **correcto, 0 errores**, 9 advertencias, todas preexistentes (2 `NU1902` de MailKit/MimeKit por proyecto y `CS0114` de `HomeController.StatusCode`).
- Las vistas Razor **sí** compilan en el build: comprobado metiendo a propósito un símbolo inexistente en `Editar.cshtml` → `error CS0103 ... Editar.cshtml(749,2)`; revertido y recompilado limpio.
- El render del atributo booleano `readonly="@(!esAdministrador)"` se verificó **ejecutando** `RazorPageBase.BeginWriteAttribute/WriteAttributeValue/EndWriteAttribute` (las tres llamadas que emite `Editar_cshtml.g.cs`, inspeccionado con `EmitCompilerGeneratedFiles`): con `true` emite `readonly="readonly"` y con `false` **omite el atributo entero**. Importa porque un `readonly=""` sería verdadero en HTML.
- `VentaWorkflowService.GuardarBorradorAsync` ejercitado **directamente contra `laplatense_dev`** con los dos roles, dentro de una transacción revertida al final (0 filas sobrevivientes, base en su línea base). 15 checks, todos OK: precio manipulado a $1 → se guardó `PrecioVenta` del producto; descuento 90% y recargo 50% → 0 y 0; producto con oferta vigente → cobró `PrecioOferta`; administrador → override de 1234,56 con 10%/5% respetado y subtotal por la fórmula no-cascada; 10%+10% devuelve el precio original; descuento >100% sigue rechazado para administrador y se ignora en silencio para vendedor; y la simétrica (vendedor que re-guarda pisa el override del administrador) confirmada.

**Deuda abierta que deja esta ronda.**
- **`Items[].PorcentajeIVA` sigue llegando del cliente para cualquier rol.** Es el hermano del hueco que se acaba de cerrar y el único que queda: un vendedor que postea `PorcentajeIVA = 0` baja el total de la venta ~21% sin tocar el precio unitario, porque `RecalcularTotales` suma `Subtotal * PorcentajeIVA / 100`. Se dejó **deliberadamente sin tocar** porque el brief de esta ronda lo excluyó de forma explícita ("el IVA por línea no se toca") y el alcance era un solo defecto. **Es una decisión de Joaquín**, no un olvido: si el IVA por línea es un dato del producto y no una decisión del vendedor, la corrección es idéntica a la de esta ronda (resolverlo desde `Producto.PorcentajeIVA` cuando el usuario no es administrador) y son tres líneas. Si en cambio el vendedor tiene que poder elegir la alícuota, hay que decir por qué.
- Un `PrecioUnitario` **negativo** posteado por un administrador no se rechaza en el Service (sí lo limita el `min="0"` del input y el `[Range]` del ViewModel, pero `GuardarBorrador` no chequea `ModelState.IsValid`). Preexistente, no se tocó para no ampliar alcance; marihogar sí lo valida (`PrecioUnitario <= 0`).
- Un borrador con override de administrador re-guardado por un vendedor pierde el override (ver "mitad simétrica"). Si eso molesta operativamente, la salida no es relajar el gate sino que el borrador con override no sea editable por un vendedor.
### Entrega 3 — pasos 1 a 3: Proveedores, CC de proveedores y Ordenes de compra (2026-10-05, rama `entrega-1-migracion`)

**No pusheado y no deployado** — pedido explicito de Joaquin ("no publicar, dejar el desarrollo listo"). Nada corrio contra produccion: la migracion se aplico unicamente a `laplatense_dev`.

Cierra el **alta y la edicion completa de compras**, con una frontera deliberada: **nada de lo que se construyo aca toca stock, ni caja, ni cuenta corriente**. El impacto real de una compra (incrementar stock + postear el Cargo de deuda) es la RECEPCION, que es el paso 4; los pagos son el paso 5. El contrato `IOrdenCompraService` ni siquiera expone `RecibirAsync`, y `OrdenCompraService` no inyecta `IStockService`, `ICajaMovimientoService` ni `ICCProveedorService`: no se puede llamar por accidente lo que no esta inyectado.

#### Resultado del escaneo de reutilizacion (obligatorio antes de implementar)

Encontrado en el **paso 1** del escaneo (`docs/patrones/cat_resumen.txt`), sin necesidad de grep dirigido:

- **`PAT-001`** — "Ledger / Cuenta corriente". Entrada leida completa, las dos rutas confirmadas reales. Se porto `marihogar/CCProveedorService.cs` con el camino de vuelta ya recorrido en casa (`MovimientoCCCliente` + `CuentaCorrienteClienteService` de este proyecto son un port del `MovimientoCCProveedor` de vinosefue). **Se actualizo PAT-001** con tres `archivos_referencia` nuevos de la-platense y la aplicacion en `proyectos_que_lo_usan`.
- **`PAT-005`** — "Maquina de estados (workflow generico)". Aplicado: enum en Domain, transiciones validadas en el Service con conjuntos EXPLICITOS de estados (`EstadosEditables`/`EstadosCancelables`, nunca una negacion), y ViewModel que calcula las acciones disponibles por estado.
- **`PAT-008`** / **`PAT-016`** — DataTables server-side con filtro por columna visible + busqueda global multi-formato + filtros en `Session`. Aplicados a los tres listados nuevos.
- **`PAT-020`** / **`PAT-051`** — leidos y declarados como **el camino que hay que seguir en los pasos 4 y 5**, no aplicados todavia: en esta ronda cancelar no tiene nada que revertir porque el Cargo no se postea hasta recibir. El contrato de la reversion por neto vivo quedo DEFINIDO (`ObtenerNetoVivoAsync`) para que esos pasos no lo reinventen sobre el nominal.
- **`PAT-050`** revisado y descartado: el gate de precio por rol no aplica aca — todo el modulo es Administrador exclusivo, no hay un rol menor del que proteger el precio.
- **Sin antecedente, declarado y catalogado**: el modelo de unidad de la linea de compra. `marihogar/OrdenCompraItem.cs` tiene `Cantidad` como `int` y la linea no declara unidad. Se construyo nuevo y se agrego al catalogo como **`PAT-052`** ("Linea de documento que declara su unidad y CONGELA el factor de conversion").
- **Sin antecedente, declarado**: el buscador de productos por codigo de proveedor (0 hits de `CodigoProveedor` en marihogar; su buscador va solo por nombre de producto). Construido nuevo.
- **Sin antecedente, declarado**: `TipoCambio`/`Moneda`/`PorcentajeDescuentoHabitual`/`FormaPagoHabitual` en `Proveedor` (0 hits en marihogar, verificado). Desarrollo nuevo dentro del alcance del item 3.1.

#### Barrido LP-002 al ampliar `Proveedor` — las 4 pasadas, con lo que rindio cada una

El brief daba por sentado que `Proveedor` "se consume como catalogo simple en los combos del catalogo de productos". **Eso es falso y el barrido lo corrigio**: la premisa habia que verificarla, no heredarla.

**Pasada 1 — relevamiento directo.** `grep -rn "Proveedor"` sobre `*.cs`/`*.cshtml`/`*.js` (excluyendo `obj`/`bin`/`publish`/`Migrations` y los falsos positivos `MovimientoCCProveedor`/`CodigoProveedorProducto`): **`Proveedor` tenia CERO consumidores en `Web/`**. Ningun controller, ninguna vista, ningun combo. Los unicos consumidores reales eran:

- `tools/MigracionCatalogo/Program.cs:808` — `new Proveedor { Nombre = ..., Activo = true }`, inicializador de objeto. **Es el unico escritor real de la entidad** y el contrato que habia que preservar.
- `ProveedorService : CatalogoSimpleServiceBase<Proveedor>` — el unico lector, y es justamente el que se reemplazo.
- `CodigoProveedorProducto.ProveedorId` — la FK.

Consecuencia practica: la ampliacion se pudo hacer **estrictamente aditiva** (18 `AddColumn`, 3 `CreateTable`, 9 `CreateIndex`, **cero `DropColumn`/`AlterColumn`** sobre lo existente) y **`Nombre` se MANTUVO como nombre de columna** aunque marihogar lo llame `RazonSocial`: renombrarlo era una migracion destructiva sobre 85 razones sociales reales migradas del legado y habria roto el contrato de la herramienta de migracion, a cambio de nada funcional. En pantalla se rotula "Razon social".

**Pasada 2 — hermanos semanticos (fechas).** Grep reproducible, el numero sale de aca y QA lo puede recontar:

```
grep -hn "DateTime" FerreteriaLaPlatense.Domain/Entities/*.cs | grep "get; set;"
```

Da **29 propiedades `DateTime`** en Domain, de las cuales **6 son nuevas de esta ronda**, y las 6 declaran su semantica en el XML-doc (LP-009):

| Propiedad | Semantica |
|---|---|
| `Proveedor.FechaSaldoInicial` | instante UTC derivado de un DIA DE NEGOCIO elegido por el usuario (se persiste con `ArgentinaTime.InicioDiaUtc`) |
| `MovimientoCCProveedor.Fecha` | instante UTC; si se imputa a un dia anterior, las 00:00 ART de ese dia |
| `OrdenCompra.Fecha` | instante UTC derivado de dia de negocio; nunca futura, pasada SI permitida |
| `OrdenCompra.FechaConfirmacion` | instante UTC del momento de la accion |
| `OrdenCompra.FechaRecepcion` | instante UTC — **declarada, nunca escrita en esta ronda** (paso 4) |
| `OrdenCompra.FechaCancelacion` | instante UTC del momento de la accion |

**Pasada 3 — comentarios y XML-doc (el texto de la regla, no solo el codigo).** Rindio **2 hallazgos propios** que el grep de codigo no toca:

1. `AppDbContext.cs:36-38` decia *"Proveedor es una version minima... el modulo de Compras la amplia mas adelante"*. Dejo de ser cierto en esta misma ronda. **Corregido**, con la nota de por que.
2. `Views/Dashboard/Index.cshtml` decia que el nivel 2 del dashboard *"depende de Compras y Cuenta Corriente de proveedores"*. **Las dos piezas ya existen**, asi que la afirmacion quedo falsa: lo que falta de verdad es la cuenta corriente propia del negocio (Entrega 4, item 4.2). **Corregido el texto**, no el panel (construirlo no es alcance de esta ronda).

**Pasada 4 — vistas y JS.** Verificado que las columnas de fecha de los listados nuevos pasan por `window.Fmt` y que **ningun `toLocaleString` suelto formatea una fecha** (los 7 que hay son sobre importes, porcentajes y cantidades, que es la convencion del proyecto). LP-006 cubierto.

**Pasada extra — la mitad simetrica.** Rindio **1 hallazgo propio y un fix real**: las lineas de la compra viajan en inputs `hidden` que el JS arma en el submit. `EditarAsync` reemplaza el set completo, asi que un post con CERO lineas (JS que no cargo, POST armado a mano) **habria vaciado la compra en silencio, sin que nada falle**. Se agrego la guarda: un Edit sin lineas sobre una compra que SI las tiene se rechaza con mensaje. `CrearAsync` SI acepta un borrador vacio, a proposito — empezar una compra y completarla despues es el caso normal, y `ConfirmarAsync` exige al menos una linea.

**Pasada extra — `Proveedor.Activo` y su simetrico.** Se impide cargar una compra nueva a un proveedor inactivo, **pero NO se bloquea editar un borrador cuyo proveedor se desactivo despues**: lo que se impide es MOVER la compra a un proveedor inactivo. Sin esa asimetria, desactivar un proveedor dejaba borradores inmodificables.

#### Como quedo modelada la unidad en la linea de compra

Es la parte del port que **no es mecanica** (ver `PAT-052`). `OrdenCompraItem` lleva **tres** columnas en vez de una cantidad:

- **`Cantidad`** es `decimal(18,3)` (en marihogar es `int`), mismo ancho que `Producto.Stock` e `ItemVenta.Cantidad`. Esta expresada en la unidad de **COMPRA**, no convertida: si se compra el bulto, la cantidad es en bultos y **`PrecioCompra` es el precio DEL BULTO**. Es lo que dice la factura del proveedor, y es lo unico contra lo que se puede auditar la linea.
- **`UnidadCompra`** la declara la linea, como columna propia. No alcanza con mirar `Producto.UnidadCompra`: el mismo producto se compra a veces por bulto y a veces por unidad suelta, y la ficha solo puede decir una de las dos. El operador la puede cambiar por linea.
- **`FactorConversionAplicado`** es un **snapshot congelado** de `Producto.FactorConversion` al cargar la linea. `UnidadVenta` tambien se congela. La conversion a stock usa ESE factor, no relee la ficha — mismo criterio con el que `ItemVenta` congela precio e IVA.

**`CantidadEnUnidadVenta` es una propiedad CALCULADA** (`Cantidad * FactorConversionAplicado`), con `entity.Ignore(...)` explicito en el DbContext: es derivada exacta de dos columnas que si se persisten, y duplicarla en la base abriria la puerta a que queden en desacuerdo. Es el valor que el paso 4 va a ingresar al stock.

**Por que el snapshot y no releer la ficha:** `FactorConversion` es un campo editable. Si el proveedor cambia el tamano del bulto y alguien actualiza el producto, una compra vieja todavia sin recibir pasaria a ingresar una cantidad de stock **distinta de la que se cargo**, y una ya recibida mostraria un equivalente que no coincide con el movimiento de stock real.

**Guarda que no es cosmetica:** cuando `UnidadCompra == UnidadVenta`, el factor se **FUERZA a 1** aunque llegue otro valor del formulario. Verificado ejecutando: con factor 99 y unidades iguales, se persiste 1 y el equivalente queda en 3, no en 297. Sin esa guarda, un factor heredado de la ficha queda de fantasma en una linea que vino en unidades sueltas y al recibir multiplica el stock.

**La validacion se delega al contrato que ya existe** (`IUnidadMedidaConversionService.EsFactorConversionValido`, regla R4 del catalogo) en vez de reimplementar la regla con otro criterio. Cuando las unidades difieren y no hay factor, el error es funcional y explicito, no un 500 ni un stock mal ingresado.

**Riesgo declarado (pregunta abierta 6 de `4-presupuestador.md`, sin resolver):** el factor es **fijo por producto**. Si el mismo producto llega en bultos de distinto tamano segun el proveedor, tendria que vivir en `CodigoProveedorProducto`. El snapshot **absorbe** ese caso sin cambio de esquema mientras el operador corrija el factor a mano al cargar la compra, pero no lo resuelve de raiz. **Hay que preguntarselo al cliente antes de escribir la migracion del paso 4.**

#### `CodigoProveedorProducto` leido por primera vez

Los **110.683 mapeos** migrados en dev (el brief decia 127.629; en `laplatense_dev` son 110.683) no los leia **ninguna pantalla** hasta esta entrega. `IProductoService.BuscarParaCompraAsync(texto, proveedorId)` es el primer consumidor: resuelve por nombre, codigo interno, codigo de barras propio, codigos de barras alternos **y el codigo de ESE proveedor**.

El match por codigo de proveedor esta **acotado a `proveedorId`**, que es exactamente por lo que el indice unico de la tabla es compuesto `(ProveedorId, CodigoDelProveedor)`: el mismo codigo puede identificar productos distintos en proveedores distintos, asi que buscar sin acotar devolveria el producto equivocado — con 110.683 filas, en silencio. Verificado ejecutando contra dato real: el codigo `-0099-42` del proveedor #1 resuelve al producto #19078, y **sin `proveedorId` no lo resuelve**. Los resultados que matchearon por codigo de proveedor se ordenan PRIMERO.

#### Aritmetica fiscal de la compra — el Service es la autoridad

Dos descuentos **en cascada** + tres impuestos, los cinco como par `%`/importe bidireccional. La misma aritmetica esta espejada en el JS de `Create.cshtml` para feedback inmediato, pero **lo que se persiste siempre se recalcula en `OrdenCompraService.AplicarFiscal`**: el cliente puede manipular el JS, asi que los montos que llegan del formulario son una PROPUESTA.

Criterio del par bidireccional server-side (`ResolverPar`): si viene un **porcentaje > 0**, manda el porcentaje. Si el porcentaje viene en 0 pero el **importe** no, manda el importe y se despeja el porcentaje — es el caso real *"el proveedor me puso $317.526,41 de descuento y no me dice el %"*. El importe se acota a la base para que la compra nunca quede en negativo.

**La cascada verificada con numeros**, sobre un subtotal de 10.000 con `33+5`:

| Concepto | Importe |
|---|---:|
| Subtotal | 10.000,00 |
| Descuento 33% | − 3.300,00 |
| Descuento adicional 5% **del neto** (no del subtotal) | − 335,00 |
| **Base imponible** | **6.365,00** |
| IVA 21% sobre la base | 1.336,65 |
| Percepcion IIBB 4% sobre la **misma** base (sin sumar el IVA) | 254,60 |
| Otros 1,5% sobre la misma base | 95,48 |
| **Total** | **8.051,73** |

El descuento efectivo del `33+5` es **36,35%**, no 38%. Esa cifra es la que valida la estructura contra dato propio: `Producto.Bonificacion` del catalogo migrado guarda literalmente valores como `"33+5"`.

**PENDIENTE DE CONFIRMAR CON EL CLIENTE:** la ESTRUCTURA de dos niveles en cascada esta respaldada por el dato propio (`Bonificacion`), pero la **formula exacta** — en particular que las percepciones se liquiden sobre la base pelada y no sobre base + IVA — viene de una factura real de un proveedor de marihogar, no de uno de La Platense. **Hay que verificarla contra una factura real suya antes de darla por cerrada.**

Defensivo y verificado ejecutando: con `Facturada = false`, los tres impuestos se **fuerzan a 0** y `TipoComprobante`/`PuntoVenta`/`NumeroComprobante` a null, aunque lleguen cargados a mano desde el formulario. Una compra en negro con un IVA colgado inflaria el Total y, cuando llegue el paso 4, la deuda que se postea en la cuenta del proveedor.

**Nada de AFIP entro a este modulo**, confirmado: `TipoComprobanteCompra` es A/B/C manual sin correlato fiscal, el CUIT del proveedor es texto libre validado solo por longitud (11 digitos), y no hay constatacion de comprobante ni consulta de padron. Es el mismo criterio de marihogar (0 hits de afip en su `OrdenCompraService` y su controlador).

#### Bugs propios encontrados EJECUTANDO (no leyendo)

1. **`ObtenerNetoVivoAsync` devolvia 160.000 en vez de 60.000.** La primera version recibia un `TipoMovimientoCCProveedor` y calculaba *"suma de originales no-reversion menos suma de reversiones DENTRO de ese tipo"*, copiando el shape del ledger de caja. Pero en un ledger de **deuda** la reversion de un `Cargo` se postea como un `Pago` (es la unica forma de mover el saldo en sentido contrario), asi que **filtrar por tipo dejaba la reversion afuera del calculo**: un saldo inicial de 100.000 reajustado a 60.000 devolvia la SUMA de los dos cargos. Corregido a **neto CON SIGNO sobre los dos tipos**. Efecto colateral deseado: `EsReversion` queda como dato informativo (el badge de la grilla) y **no participa de la aritmetica** — un contramovimiento al que se le olvide el flag igual neutraliza bien el saldo.
2. **El neto vivo no estaba acotado por proveedor.** Los origenes manuales (`SaldoInicial`, `AjusteManual`) no tienen documento y usan `OrigenId = 0`, asi que sin filtrar por `ProveedorId` el calculo **mezclaba el saldo inicial de TODOS los proveedores en un solo neto**: reajustar el saldo de uno habria revertido la plata de los otros. Encontrado en revision de codigo propia antes de ejecutar, y el arnes tiene un check dedicado que lo deja observable (crea dos proveedores con saldo inicial, reajusta uno y verifica que el otro no se movio).

Y un tercero **en el arnes mismo**, que vale registrar porque confirma que la regla sigue viva en este proyecto: la linea que verificaba la limpieza usaba `p.Nombre.StartsWith("ZZVERIF-E3")` y **revento con `Expression '[SqlConstantExpression] COLLATE utf8mb4_bin' does not have a type mapping assigned`**. Es **`CRM-019`** (misma familia que `MH-001`), reproducido en vivo. Fix: `EF.Functions.Like`. **El codigo de produccion de esta ronda no tiene ni un `StartsWith`/`EndsWith`** (verificado por grep) y **ninguna coleccion local de string** llega al provider: los IN que hay son de `int` o de enum, y el match por etiqueta de enum se resuelve con una consulta por valor ESCALAR (la forma que MH-001 prescribe para su quinta aparicion).

#### Archivos y capas modificadas

**Domain — enums nuevos (5):**

- `Enums/TipoMovimientoCCProveedor.cs` — `Cargo`/`Pago`. Enum PROPIO, separado del de clientes: la semantica es la deuda hacia afuera.
- `Enums/EstadoOrdenCompra.cs` — `Borrador`/`Confirmada`/`Recibida`/`Cancelada`. `Recibida` declarada SIN transicion implementada.
- `Enums/TipoComprobanteCompra.cs` — A/B/C manual, sin correlato AFIP.
- `Enums/MonedaProveedor.cs` — `Peso`/`Dolar`. Desarrollo nuevo.
- `Enums/FormaPagoProveedor.cs` — 5 valores. Desarrollo nuevo.

**Domain — entidades:**

- `Entities/Proveedor.cs` — **AMPLIADO** (aditivo). Sigue implementando `ICatalogoSimpleEntity` y conservando `Nombre`+`Activo` con el mismo significado.
- `Entities/MovimientoCCProveedor.cs` — NUEVA. **No hereda de `SoftDestroyable`** (ledger inmutable), con `UsuarioId` explicito porque no la alcanza el stamping de auditoria del DbContext.
- `Entities/OrdenCompra.cs` — NUEVA.
- `Entities/OrdenCompraItem.cs` — NUEVA, con el modelo de unidad de `PAT-052`.

**Application:**

- `Helpers/OrigenCCProveedor.cs` — NUEVO. Los origenes del ledger en **un solo lugar invocable** (antidoto a LP-002: el combo del filtro y el mapa de etiquetas de la vista salen del mismo diccionario, asi que agregar un origen no requiere tocar la vista).
- `DTOs/ProveedorDtos.cs`, `DTOs/MovimientoCCProveedorDtos.cs`, `DTOs/OrdenCompraDtos.cs` — NUEVOS.
- `Interfaces/IProveedorService.cs` — NUEVO (archivo propio). **Reemplaza** al `IProveedorService : ICatalogoSimpleService` que vivia en `ICatalogoSimpleService.cs`.
- `Interfaces/ICCProveedorService.cs`, `Interfaces/IOrdenCompraService.cs` — NUEVOS.
- `Interfaces/ICatalogoSimpleService.cs` — se saco `IProveedorService`, con la nota de por que.
- `Interfaces/IProductoService.cs` — `+ BuscarParaCompraAsync(texto, proveedorId)`.

**Infrastructure:**

- `Services/ProveedorService.cs` — **REESCRITO**. Ya no hereda de `CatalogoSimpleServiceBase<Proveedor>`.
- `Services/CCProveedorService.cs`, `Services/OrdenCompraService.cs` — NUEVOS.
- `Services/ProductoService.cs` — `+ BuscarParaCompraAsync`.
- `Data/AppDbContext.cs` — 3 `DbSet` nuevos, configuracion de las 3 entidades, ampliacion del bloque de `Proveedor`, y la correccion del comentario viejo.
- `DependencyInjection.cs` — 3 registraciones (`ICCProveedorService`, `IProveedorService` reapuntado, `IOrdenCompraService`).
- `Migrations/20261005231651_EntregaTres_ProveedoresCCCompras.cs` — ver abajo.

**Web:**

- `Models/ProveedorViewModels.cs`, `Models/OrdenCompraViewModels.cs` — NUEVOS.
- `Controllers/ProveedoresController.cs`, `Controllers/OrdenesCompraController.cs` — NUEVOS, los dos con `[Authorize(Policy = "RequireAdministracion")]` **a nivel de clase, sin overrides por accion**.
- `Views/Proveedores/` — `Index`, `Create`, `Edit`, `_Formulario` (parcial compartida por los dos formularios, 20 campos), `_FormularioScripts`, `CuentaCorriente`, `RegistrarAjuste`.
- `Views/OrdenesCompra/` — `Index`, `Create` (sirve tambien para Edit: el controller hace `return View("Create", vm)`), `Details`.
- `Views/Shared/_Layout.cshtml` — seccion "Compras" en el sidebar, dentro del bloque de Administrador.
- `Views/Dashboard/Index.cshtml` — correccion del texto prescriptivo (pasada 3 del barrido).

#### Migracion EF

**`20261005231651_EntregaTres_ProveedoresCCCompras`** — generada **y aplicada SOLO a `laplatense_dev`**. 100% **aditiva**: 18 `AddColumn` sobre `Proveedores`, 3 `CreateTable` (`MovimientosCCProveedor`, `OrdenesCompra`, `OrdenCompraItems`), 9 `CreateIndex`. **Cero `DropColumn`, cero `AlterColumn`** sobre lo que ya existia. `has-pending-model-changes`: sin drift.

**Correccion de datos agregada a mano sobre la migracion generada** — y es el hallazgo que la hace no-trivial: `Moneda` es un enum **no nullable** y EF la agrega con `defaultValue: 0`, pero el primer valor del enum es `MonedaProveedor.Peso = 1` (la convencion del proyecto numera explicito desde 1). Sin corregirlo, los **85 proveedores que ya existian** quedaban con `Moneda = 0`, que no corresponde a ningun valor del enum: el listado mostraria "0" crudo, el filtro "Pesos" no los encontraria y `p.Moneda == MonedaProveedor.Peso` daria false para todos. **Es exactamente la clase de incoherencia de LP-002: la columna funciona perfecto para las filas nuevas y esta mal en las que ya estaban, en silencio.** Se agrego `UPDATE Proveedores SET Moneda = 1 WHERE Moneda = 0;`, con `WHERE` acotado para que correr la migracion dos veces sea inocuo. Verificado despues de aplicar: los 85 quedaron en 1.

**Produccion sigue atras y ahora son TRES migraciones:** le faltan `EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago`, `D9_NormalizarFechaCajaMovimiento_DiaDeNegocio` y esta.

#### Evidencia de verificacion (ejecutada, sin navegador)

El rol del Implementador prohibe levantar la app y probar por navegador, y "compila y lo lei" no es evidencia suficiente en este proyecto. La combinacion usada, toda ejecutada de verdad:

1. **`dotnet build FerreteriaLaPlatense.slnx` — 0 errores, 9 advertencias** (las 9 son `NU1902` de MailKit/MimeKit, preexistentes). **Las vistas Razor SI compilan en el build, confirmado en esta misma ronda sin tener que provocarlo**: un `autofocus` condicional en `_Formulario.cshtml` rompio el build con `RZ1031` y hubo que corregirlo. Asi que el build limpio tambien dice algo sobre las 10 vistas nuevas.
2. **Grafo de DI validado** con `BuildServiceProvider(ValidateOnBuild + ValidateScopes)` en un proyecto de consola aparte, con stubs de `IConfiguration` e `IWebHostEnvironment` (los aporta el host de ASP.NET; su ausencia en un arnes de consola es falla del arnes, no del codigo). Los 4 servicios del modulo resuelven en un scope real: sin ciclos ni captive dependencies.
3. **Los Services ejercitados DIRECTAMENTE contra `laplatense_dev`** — no simular requests, la capa de negocio real: **161 checks, 161 OK**, con limpieza al final que dejo la base en su linea base exacta (85 proveedores, 0 compras, 0 movimientos CC, 0 residuo de prueba). Cobertura: los 2 bugs propios de arriba, la aritmetica fiscal con numeros, el modelo de unidad (bultos, decimales, factor fantasma, factor faltante), las transiciones de estado validas e invalidas, el perimetro (stock/caja/CC/ajustes de stock contados antes y despues de confirmar y de cancelar), las 3 relaciones que bloquean la baja, los 8 filtros de columna, 30 terminos distintos de busqueda global (texto, importe es-AR e invariante, fecha, etiquetas de enum, badges), las 30 combinaciones de columna x direccion de ordenamiento, y 5 checks de regresion sobre lo que ya estaba (catalogo completo, codigos de proveedor completos, ningun proveedor con enum invalido, el contrato de `tools/MigracionCatalogo`, y la CC de clientes).
4. **`has-pending-model-changes`** — sin drift entre el modelo y la ultima migracion.

**Lo que NO se verifico y le queda a QA:** todo lo que solo se ve en un navegador — el Select2 AJAX del buscador de productos, la grilla de items renderizada por JS, los cinco pares `%`/importe bidireccionales, el daterangepicker, los popup de SweetAlert2, y que el JS de la pantalla de compra de el **mismo** total que el Service (la duplicacion es deliberada, pero que las dos mitades coincidan hoy solo esta verificado del lado del Service).

#### Riesgos y supuestos

1. **La formula fiscal exacta es un supuesto de negocio tomado de otro cliente.** La estructura de cascada esta respaldada por dato propio (`Bonificacion = "33+5"`); el orden exacto de las percepciones, no. Confirmar contra una factura real de La Platense.
2. **El factor de conversion es fijo por producto** (pregunta abierta 6 de `4-presupuestador.md`). El snapshot de la linea absorbe el caso del bulto distinto por proveedor, pero no lo resuelve de raiz.
3. **El filtro por rango de saldo del listado de proveedores se aplica sobre la pagina visible**, no sobre el conjunto completo, porque el saldo no es una columna (vive en el ledger). Con 85 proveedores y `pageLength` 15 alcanza; si el padron creciera a miles habria que materializar el saldo. **Esta declarado en la propia pantalla** con un `ov-field-hint`, no escondido. Por el mismo motivo, la columna de saldo **no es ordenable**: se declara `orderable: false` en vez de ofrecer un orden que no haria nada.
4. **El JS y el Service duplican la aritmetica fiscal.** Es deliberado (el Service es la autoridad), pero si se cambia una mitad hay que cambiar la otra o el operador ve un total distinto del que se guarda. Esta anotado en los dos lados.
5. **La recepcion no existe**, y los mensajes de la UI lo dicen explicitamente ("El stock y la cuenta corriente del proveedor se actualizan al registrar la recepcion de la mercaderia"). Sin esos mensajes, el perimetro de esta ronda se lee como un bug en la prueba.
6. **El ajuste manual de CC de proveedores no consulta `ValidarPeriodoAbiertoAsync`**, igual que el de clientes: no escribe en caja, asi que no hay arqueo que pueda quedar desfasado. **El egreso real del paso 5 SI tiene que pasar por esa guarda** — el camino no quedo preparado de ninguna otra forma.
7. **`EstadoOrdenCompra.Recibida` existe en el enum y ningun codigo la escribe.** La guarda de `CancelarAsync` ya la contempla, para que el dia que exista la recepcion no haya que acordarse de endurecerla.

#### Pruebas minimas requeridas para QA

Las de navegador, que son las que este rol no puede hacer:

1. **Proveedores/Index**: filtrar por cada una de las 8 columnas visibles; buscar en el buscador global por un importe visible (tipear "1480" tiene que encontrar un TC de "$ 1.480,50"), por una fecha `dd/MM/yyyy`, y por una etiqueta ("Pesos", "Monotributo", "Inactivo"). Navegar a otra pantalla y volver: los filtros siguen aplicados. "Limpiar filtros" vacia los controles Y al reentrar no los repone.
2. **Proveedores/Create**: alta con solo razon social; alta con moneda Dolar **sin** TC (tiene que bloquear); alta con descuento adicional **sin** descuento base (bloquear); alta con saldo inicial 100.000 y verificar que la cuenta corriente muestra un movimiento de apertura por ese importe.
3. **Proveedores/Edit**: que los 20 campos vuelvan cargados (**mirar el HTML crudo**: una coma dentro de un `value` de un `input type="number"` es LP-003). Cambiar el saldo inicial y verificar que la CC muestra 3 movimientos (original + reversion + nuevo) y el saldo correcto.
4. **Proveedores/CuentaCorriente**: cargar un ajuste manual y verificar que el saldo corrido de la ultima fila coincide con la card de saldo; filtrar por rango de fecha y comprobar que el saldo corrido **no** arranca de cero; verificar que **el ajuste no aparece en Caja**.
5. **Baja de proveedor**: estando en la pagina 2+ del listado, eliminar uno y confirmar que el DataTable **no vuelve a la pagina 1**. Intentar eliminar uno con codigos del catalogo mapeados (tiene que bloquear con mensaje).
6. **OrdenesCompra/Create** — es la pantalla con mas riesgo: elegir un proveedor con descuento habitual y verificar que se precarga; buscar un producto **tipeando el codigo del proveedor** (los hay reales en la base); agregar una linea en bultos y verificar la columna "Equivale a"; tocar el `%` de descuento y ver que se recalcula el importe, y al reves; marcar/desmarcar "vino con factura" y ver que la card de impuestos aparece y desaparece y que los impuestos vuelven a 0; **guardar y comparar el total de la pantalla contra el de la pantalla de detalle** (son dos calculos distintos y tienen que coincidir).
7. **Reabrir un borrador** (`Edit`): que las lineas vuelvan con su cantidad, unidad, factor y precio, y que el combo de proveedor llegue **con el proveedor ya elegido**.
8. **Maquina de estados**: desde Borrador, los botones visibles tienen que ser Editar + Confirmar + Cancelar. Confirmar: no aparece Editar, no se mueve el stock del producto ni aparece nada en Caja ni en la CC del proveedor. Cancelar con motivo vacio (bloquear). Probar `POST /OrdenesCompra/Confirmar/{id}` sobre una ya confirmada (error funcional, nunca 500).
9. **Permisos**: con usuario Vendedor, el sidebar NO muestra "Compras", y `GET /Proveedores` y `GET /OrdenesCompra` devuelven 403.
10. **Regresion**: que el catalogo de productos, el buscador de la venta y la CC de clientes sigan funcionando igual.

#### Checklist de salida para merge

- [x] Build limpio de la solucion (0 errores; las vistas Razor entran en el build, confirmado)
- [x] Grafo de DI validado (`ValidateOnBuild` + `ValidateScopes`)
- [x] Services ejercitados contra `laplatense_dev` (161/161) y base devuelta a su linea base
- [x] Migracion EF generada, aditiva, aplicada **solo a dev**, sin drift de modelo
- [x] Correccion de datos del enum `Moneda` incluida en la migracion y verificada
- [x] Barrido LP-002 completo (4 pasadas + 2 extras), con 5 hallazgos propios y sus fixes
- [x] MH-001 / CRM-019: cero colecciones locales de string, cero `StartsWith`/`EndsWith` en el codigo nuevo; todas las consultas nuevas **ejecutadas**
- [x] LP-003: `InvariantCulture` en todos los `value` de los inputs numericos de las vistas nuevas
- [x] LP-009: las 6 propiedades de fecha nuevas declaran su semantica
- [x] Enums: los 5 nuevos numerados explicito desde 1, con la nota de "todo valor nuevo al final"
- [x] Design system: `.ov-form-page`/`.ov-page-head`/`.ov-form-actions`/`.ov-required`/`.ov-field-hint`/`.ov-detail-grid`, Select2 en todo combo, SweetAlert2, daterangepicker, DataTables server-side con filtro por columna visible, PAT-016 en los 3 listados
- [x] `PAT-052` agregado al catalogo; `PAT-001` actualizado con 3 referencias nuevas; `cat_resumen.txt` regenerado
- [x] `5-implementador.md` y `trazabilidad.md` actualizados
- [ ] **Sin push y sin deploy** (pedido explicito de Joaquin) — el commit queda local en `entrega-1-migracion`
- [ ] Verificacion por navegador: le corresponde a QA (ver "Pruebas minimas")
### Entrega 3 — pasos 4 y 5: recepción de mercadería y pagos a proveedores (2026-10-05, rama `entrega-1-migracion`)

**No pusheado y no deployado** — pedido explícito de Joaquín ("no publicar, dejar el desarrollo listo"). Nada corrió contra producción: la migración se aplicó únicamente a `laplatense_dev`.

Cierra el **impacto real del módulo de Compras**. Hasta el paso 3 nada de Compras movía un peso ni una unidad de stock; desde esta ronda:

- **`RecibirAsync`** (`Confirmada → Recibida`) incrementa stock, escribe un ledger de stock nuevo y postea el `Cargo` de deuda, **todo en una transacción**. **No toca la caja**: recibir genera deuda, la plata sale al pagar.
- **`PagoProveedorService`** es el **primer punto del módulo por donde sale plata de la caja**: cada línea de pago postea un `Pago` en la cuenta corriente del proveedor y un `Egreso` en el ledger de caja, mismo monto, misma fecha y mismo `OrigenId`.

#### Resultado del escaneo de reutilización (obligatorio antes de implementar)

Encontrado en el **paso 1** del escaneo (`docs/patrones/cat_resumen.txt`):

- **`PAT-052`** — "Línea de documento que declara su unidad y CONGELA el factor de conversión". Es el patrón que esta ronda **consume**: el paso 3 lo construyó, el paso 4 lo usa. **Se amplió** con un `archivos_referencia` nuevo: el consumidor y la lección que solo aparece al escribirlo (ver abajo).
- **`PAT-020`** — "Cancelación de comprobante con pagos: ledger inmutable + reversión acotada a lo posteado". Aplicado tal cual a la reversión de un pago a proveedor, en los dos ledgers.
- **`PAT-019`** — "Autocompletar el monto de un pago nuevo con el saldo pendiente". Aplicado: la primera línea del formulario de pago arranca con el saldo pendiente completo y la forma de pago habitual del proveedor.
- **`PAT-003`** / **`PAT-051`** — pago multi-medio y medio como dimensión del ledger único. El pago a proveedor es multi-línea con su `MedioPagoCaja` por línea.
- **`PAT-016`** — búsqueda global multi-formato. Aplicado a las dos columnas nuevas (origen de caja por etiqueta, estado del precio del catálogo).

**Dos patrones NUEVOS agregados al catálogo** (el criterio ya vivía en el estudio y no estaba catalogado):

- **`PAT-053`** — "Un pago, dos ledgers: punto único de egreso con la MISMA clave de origen en los dos". Origen `marihogar` (CR-84, en producción), portado y **simplificado**: de sus 579 líneas solo ~80 son runtime, el resto es backfill one-shot de datos históricos suyos y **no se portó**.
- **`PAT-054`** — "Bandera `costo actualizado, precio sin recalcular`". **Primera implementación en el estudio**, sin precedente: `RecibirAsync` de marihogar **no toca** `Producto.PrecioCompra`.

#### Paso 4 — la conversión de unidades, que es lo que NO se podía copiar

El precedente (`marihogar/OrdenCompraService.RecibirAsync`, línea ~390) tiene `Cantidad` como `int`, `StockActual` como `int`, y el ingreso de stock es literalmente la misma cantidad del ítem sin traducir nada. Acá hay que convertir, y con el factor **congelado en la línea**.

**El problema que apareció al escribirlo, y que el brief no podía anticipar:** `IUnidadMedidaConversionService.ConvertirCompraAVenta(producto, cantidad)` lee `producto.FactorConversion`, o sea el factor **de hoy**. Usarlo en la recepción habría roto exactamente el congelamiento que `OrdenCompraItem` existe para garantizar (`PAT-052`). Y la salida fácil —que la recepción se arme la multiplicación por su cuenta— parte la regla en dos lugares, que es cómo nacen las reincidencias de `LP-002`.

Se resolvió agregando al contrato una sobrecarga que **recibe** el factor:

- `ConvertirConFactor(unidadCompra, unidadVenta, factorCongelado, cantidad, nombreProducto)` — la aritmética y la condición de error viven **acá y solo acá**; `ConvertirCompraAVenta` quedó como envoltorio que le pasa los valores de la ficha.
- `ValidarConversion(...)` — la **misma** condición como pregunta en vez de como excepción: devuelve el mensaje listo para mostrar o `null`.

**Por qué `ValidarConversion` y no un try/catch adentro de la transacción:** `ConvertirConFactor` lanza `InvalidOperationException` si falta el factor. Con una factura de 80 renglones, descubrirlo en el renglón 40 dejaría 39 productos ya modificados en el change tracker: funcionaría por el rollback, pero "no deja nada a medio aplicar" sería una propiedad de la base y no del código. El guard previo recorre **todas** las líneas, junta **todos** los problemas y la recepción **no arranca** — y el operador ve las tres líneas que hay que arreglar, no la primera.

**Nota de contexto que importa para QA:** en `laplatense_dev` hay **0 productos** con `UnidadCompra != UnidadVenta` sobre 112.485. El ítem 0.4 pasó los 87.542 `Metro` a `Unidad` en bloque y los 2.635 candidatos a corte por metro esperan marcación manual del cliente. **O sea que hoy el camino de conversión no tiene ni un dato real que lo ejercite**: se midió con productos sembrados y limpiados (ver "Casos medidos").

#### Paso 4 — el ledger de stock, construido de cero

Este proyecto **no tenía** ledger de stock. Los únicos escritores de `Producto.Stock` eran `VentaWorkflowService` (resta directa, sin rastro) y `AjusteStockService.AplicarAjusteAsync`, que hace un **SET absoluto** y además fuerza `StockVerificado = true`.

`AjusteStock` **no servía** como rastro de una compra, por dos motivos independientes: no tiene `OrigenTipo`/`OrigenId` (el movimiento no se puede atar al documento que lo causó) y su semántica es "alguien contó y corrigió", que es otra cosa. Marcar productos como verificados porque llegó un bulto sería, además, falso — y por eso **`RecibirAsync` no toca `StockVerificado`**.

`MovimientoStock` nuevo, con el criterio de `marihogar/MovimientoStock` y dos adaptaciones:

1. `Cantidad` es `decimal(18,3)` y no `int` — mismo ancho que `Producto.Stock`.
2. Se agrega **`OrigenTipo`** (el precedente solo tiene `OrigenId`, porque allá el `Tipo` ya determina la tabla). Acá se declara el par completo, y el `OrigenId` del movimiento de stock es **el mismo** que el del `Cargo` de deuda.

**Inmutable: no hereda `SoftDestroyable`**, mismo criterio que `MovimientoCCProveedor`. Único escritor: `MovimientoStockService`.

**ALCANCE DECLARADO, y hay que tenerlo a la vista: `Σ MovimientoStock.Cantidad` NO reconstruye `Producto.Stock`.** Los movimientos históricos de venta y los ajustes ya aplicados **no se migraron hacia atrás** (no estaba en alcance y toca dos módulos ya en producción). El ledger es el rastro de las compras recibidas, no el libro mayor. Por eso la recepción escribe **las dos cosas** (el stock del producto y el movimiento del ledger) y no deriva una de la otra. Los otros tres valores del enum (`Venta`, `Ajuste`, `AnulacionVenta`) están **declarados sin escritor** para no renumerar el enum el día que se unifique.

#### Paso 4 — el costo del producto: lo que se actualiza y lo que NO

**Decisión del orquestador, sin precedente portable** (`RecibirAsync` de marihogar no toca `Producto.PrecioCompra`): la recepción **sí** actualiza `PrecioCompra` con el costo real, y **no** toca `PrecioVenta` ni `PorcentajeRecargo`.

El motivo está en la fórmula: `PrecioVenta = PrecioCompra × (1+Recargo%)/(1+IVA%)`. Recalcularla en cada recepción movería los precios de mostrador de **112.485 productos** sin que nadie lo pida y a espaldas del cliente — un aumento de lista del proveedor se convertiría en un aumento al público automático y silencioso.

**La base del costo NO es el total de la factura**, y confundirlas infla el catálogo entero:

```
ratioDescuento   = (Subtotal − MontoDescuento − MontoDescuentoAdicional) / Subtotal
costoNetoLinea   = item.Subtotal × ratioDescuento
costoUnitario    = Σ(costoNetoLinea por producto) / Σ(cantidadConvertida por producto)
```

**Sin IVA ni percepciones**: eso es lo que se le transfiere al proveedor, no lo que costó la unidad. Sumárselo inflaría el costo de todo el catálogo un 21% y, por la fórmula derivada, después el precio de venta. Es un número **distinto** del que va al `Cargo` de deuda (que sí es el total con impuestos): los dos son correctos y responden a preguntas distintas. Conviene que quede escrito antes de que alguien lo "arregle".

Dos detalles que no son cosméticos:

- **Se acumula por PRODUCTO, no por línea.** Una compra puede traer el mismo producto en dos renglones (dos bultos de distinto tamaño, o el ítem repetido). Con los acumuladores, el costo que queda es el **promedio ponderado real** de la compra; tomando el último renglón, el resultado dependería del orden de carga.
- **Un costo calculado en 0 NO se escribe.** Pasa con un remito sin precios o un descuento del 100%, y pisar el costo del catálogo con 0 sería destructivo y silencioso: el precio de venta derivado pasaría a 0 en el próximo recálculo masivo.

**El enganche con la Entrega 6 (`PAT-054`):** `Producto.PrecioVentaDesactualizado` (bool) + `FechaUltimoCostoCompra` (instante UTC). La bandera se muestra en el **listado del catálogo** como columna, **filtro tri-estado**, criterio de **orden** y en la **búsqueda global** por su etiqueta visible — porque sobre 112.485 filas una alerta que no se puede aislar es inservible, y el caso de uso es exactamente masivo: después de recibir 80 renglones lo que el cliente necesita es la **lista**, no abrir 80 fichas.

**La mitad simétrica (hallazgo propio del barrido): alguien tiene que APAGARLA.** Nada la apagaba. Una alerta que no se apaga deja de significar algo. Se agregó a `ProductoService.EditarAsync`: se apaga **solo si cambió `PrecioVenta` o `PorcentajeRecargo`** (eso *es* reaplicar el margen a mano) y se **mantiene** si el usuario guardó la ficha sin tocar ninguno de los dos — guardar no es decidir el precio. El otro apagador previsto es el aumento masivo de la Entrega 6, que va a necesitar apagarla por lote.

#### Paso 5 — pagos: `PAT-053` y por qué el punto único se crea ahora

`PagoOrdenCompra` portado del precedente (39 líneas): `OrdenCompraId`, `Metodo` (reusa `FormaPagoProveedor`, el enum que ya vive en la ficha del proveedor — mismo universo de valores), `Monto`, `Fecha`, `Estado`, `FechaPagoTentativa?`, `Notificado`. **Los dos últimos quedan declarados y ningún código los escribe**: son el esquema del paso 6 (pagos programados). **No hay entidad de cheque** (paso 7).

`IEgresoPagoProveedorService` es el **único punto** que postea y revierte el egreso de caja. Hoy tiene **dos** escritores (registrar y revertir) y los pasos 6 y 7 van a sumar más: **el punto único se crea ahora, antes de que el problema exista.** En marihogar son 6 los caminos que bajan la deuda y, mientras el egreso estuvo armado inline en el primero, los otros cinco movieron la deuda sin mover la plata. Crearlo después obligó allá a un backfill que fue 500 de las 579 líneas del servicio.

**Lo que se copió del precedente y es lo más valioso:** el egreso usa el **mismo `OrigenTipo`** (`"PagoOC"`) y el **mismo `OrigenId`** que el `Pago` de la cuenta corriente, y ese `OrigenId` es el id de la **línea de pago**, no el del documento (`MH-027`: dos líneas del mismo importe compartiendo clave harían revertir la equivocada). Los literales viven en dos helpers distintos (`OrigenCajaMovimiento.PagoOC` y `OrigenCCProveedor.PagoOC`) porque son dos ledgers con dominios de valores distintos, pero el **valor es idéntico a propósito**.

**Guardas, todas ANTES de abrir la transacción** (adentro no queda ninguna decisión que pueda rechazar la operación):

1. Al menos una línea con monto > 0 — nunca solo `Count == 0`: un post con tres líneas en cero no es un pago y postearía tres movimientos de $0.
2. Forma de pago válida. **`CuentaCorriente` se rechaza**: "pagar a cuenta corriente" es dejar la deuda viva. Aceptarla postearía un egreso por plata que no salió **y** cancelaría una deuda que sigue existiendo — descuadra los dos ledgers a la vez. Se rechaza en el Service **y** no se ofrece en el combo (las dos puntas).
3. Estado pagable (`Confirmada` o `Recibida`). Pagar una `Confirmada` es un **anticipo** y es un caso real (se paga para que el proveedor despache): deja al proveedor con saldo a favor del negocio hasta que la recepción postee el `Cargo`.
4. No más que el saldo pendiente. El criterio de "lo ya pagado" sale del **mismo** método que usa la pantalla (`ObtenerTotalPagadoAsync`): la variante en que la pantalla suma con un criterio y el Service valida con otro es como se deja pagar de más sin que nada falle.
5. **`LP-009`**: `ValidarPeriodoAbiertoAsync` sobre el día de negocio al que se imputa. Es la única vía de escritura de caja del módulo y la guarda no es opcional. El ajuste manual de CC la saltea a propósito; acá no. **Lo que decide si hace falta la guarda es si el movimiento escribe CAJA**, no si escribe el ledger de proveedores.

El `SaveChangesAsync` intermedio para obtener `pago.Id` va **dentro** de la transacción: hace falta porque ese id es el `OrigenId` de los dos ledgers, y no rompe el todo-o-nada.

**Reversión:** neto vivo de **cada ledger por separado** — `ObtenerNetoVivoAsync` (con signo, sobre los dos tipos) para la cuenta corriente y `ObtenerNetoPosteadoAsync` para la caja. Nunca el monto del documento (`MH-020` punto 3). **Idempotente por construcción**: la segunda vez los dos netos están en 0 y no se escribe nada — no hay flag de estado que haya que acordarse de consultar. Calcular los dos netos por separado arregla además el caso en que uno de los dos lados ya se había revertido y el otro no.

Dos detalles de la reversión que descuadran el arqueo si se omiten:

- **Arrastra el MISMO medio de pago que el egreso original.** Si la plata salió por transferencia y vuelve sin medio declarado, al arqueo por medio le falta el ingreso en la cuenta real **y** le sobra en la fila "Sin declarar": se descuadra de a dos.
- **Se imputa a HOY, no a la fecha del pago**, y pasa por `ValidarPeriodoAbiertoAsync` igual. Postear el contramovimiento con la fecha original mete plata en un arqueo posiblemente ya firmado, que es exactamente lo que la guarda existe para impedir.

**Cancelar una compra NO revierte sus pagos anticipados**, a propósito: la plata salió de verdad y el proveedor queda con saldo a favor, que es lo que realmente pasó. Decidir si se pide de vuelta o queda a cuenta de la próxima compra es del negocio. Revertir es una acción aparte y explícita.

#### Barrido `LP-002` — 6 pasadas, 6 hallazgos propios

La **pasada 0** (verificar las premisas del brief, no heredarlas) rindió dos veces:

1. **El brief afirmaba que el único call site de la conversión era `EsFactorConversionValido` en `ProductoService:444`.** Verificado: `ProductoService.cs:554` **y** `OrdenCompraService.cs:707` (el paso 3 ya lo había cableado). Lo que sí era cierto es que **`ConvertirCompraAVenta` tenía CERO call sites**. La diferencia importa: creer que el validador estaba huérfano habría llevado a tratarlo como código nuevo en vez de como un contrato con dos consumidores.
2. **El brief pedía usar `ConvertirCompraAVenta` Y el factor congelado — las dos cosas son incompatibles**, porque ese método lee la ficha viva. Verificarlo es lo que produjo la sobrecarga `ConvertirConFactor` en vez de una multiplicación duplicada.

**Pasada 1 — ¿el campo se postea?** Los inputs de la grilla de pago **a propósito** no tienen `name`: el JS los renumera a índices contiguos en el submit. Por eso quitar una línea del medio **obliga** a renumerar — si no, el model binder corta la lista en el primer hueco y las líneas de abajo se pierden en silencio.

**Pasada 2 — hermanos semánticos.** Grep reproducible: `grep -hn "DateTime" FerreteriaLaPlatense.Domain/Entities/*.cs | grep "get; set;"` da **34** (eran 29 al cerrar el paso 3). Las 5 nuevas declaran su semántica: `MovimientoStock.Fecha`, `PagoOrdenCompra.Fecha`, `PagoOrdenCompra.FechaReversion` y `Producto.FechaUltimoCostoCompra` son **instantes UTC**; `PagoOrdenCompra.FechaPagoTentativa` es un **día calendario de negocio** (sin hora).

**Pasada 3 — comentarios y XML-doc: 20 correcciones.** Es la pasada que más rindió otra vez. Reglas de negocio **falsas** que vivían en el repo: `OrdenCompra` decía "la transición a `Recibida` no está implementada"; `EstadoOrdenCompra.Recibida` decía "DECLARADA, SIN TRANSICIÓN IMPLEMENTADA"; `OrdenCompra.FechaRecepcion` decía "DECLARADO, nunca escrito"; `MovimientoCCProveedor` listaba `OrdenCompra` y `PagoOC` como "No implementado todavía"; `OrigenCCProveedor` declaraba los dos como "sin escritor todavía"; `TipoMovimientoCCProveedor` decía "paso 4, todavía no implementado"; `ICCProveedorService` decía "el día que el paso 5 postee el EGRESO real".

**Y un hallazgo que NO es un comentario viejo sino una promesa vencida:** `Proveedor.TipoCambio` decía *"convertir la línea de compra a pesos desde la moneda del proveedor es alcance del paso 4"*. **No lo fue** — el paso 4 se cerró sin eso, y ahora importa **más** que antes porque ese costo se persiste en la ficha del producto. Se reescribió como **pendiente declarado** (ver "Riesgos") y no como una promesa dentro del código: una promesa vencida en un comentario hace creer que el caso está cubierto.

**Pasada 4 — vistas y JS.** Cero `toLocaleString` sobre una fecha: todas las fechas van por `window.Fmt`, los `toLocaleString('es-AR')` son solo importes y cantidades. `LP-003` aplicado en los `value` de los `<input type="number">` del formulario de pago (`InvariantCulture`).

**Pasada 5 — la mitad simétrica.** Dos hallazgos:

- **Quién APAGA `PrecioVentaDesactualizado`** (resuelto arriba). Nada lo hacía.
- **`ovAplicarSelect2` en las filas agregadas por JS.** El auto-init de `site.js` corre en el ready y no alcanza a las filas nuevas del pago multi-línea: hay que llamarlo a mano sobre la fila insertada.

**Pasada 6 — la migración sobre las filas que YA estaban.** La lección del paso 3 (los 85 proveedores con `Moneda = 0`) **no aplica acá, y esta vez se verificó en vez de suponerse**: `PrecioVentaDesactualizado` es un **bool** (`false` es un valor legítimo del dominio y es el correcto: ningún producto tuvo todavía una recepción), `FechaUltimoCostoCompra` es **nullable**, y `PagoOrdenCompra.Estado` sí es un enum no nullable con `defaultValue: 0` pero está en una **tabla nueva** sin filas. Verificado con `GROUP BY` sobre la base después de aplicar: **una sola fila, `0` con 112.485**.

#### El cierre de `LP-002` que corta la recurrencia: `OrigenCajaMovimiento`

El relevamiento encontró el ledger de caja **ya desincronizado antes de agregarle nada**:

- Los valores vivían como **tres constantes** en `CajaMovimientoService` y un **cuarto (`"CobroCC"`) como literal suelto** en `CuentaCorrienteClienteService`: no había un lugar donde estuvieran los cuatro.
- El combo de filtro de `Views/Caja/Index.cshtml` tenía los cuatro **hardcodeados con etiquetas legibles** ("Cobro de cuenta corriente", "Ajuste manual") mientras la columna "Origen" de la **misma grilla** renderizaba el valor **crudo** (`CobroCC`, `Ajuste`). **El filtro y la fila ya decían cosas distintas.** Es textualmente el defecto que el ledger de clientes sufrió y que `OrigenCCProveedor` cerró para proveedores.

Se creó `Application/Helpers/OrigenCajaMovimiento.cs` con los **cinco** orígenes y sus etiquetas. Las tres constantes de `CajaMovimientoService` y la de `CuentaCorrienteClienteService` quedaron como **alias** que apuntan ahí (no se tocaron los call sites). El combo sale de `Todos`, la grilla muestra `OrigenEtiqueta` proyectada por el Service, y la búsqueda global compara contra la **etiqueta visible** — una consulta por origen con el valor como **parámetro escalar** (`MH-001`: nunca `origenes.Contains(m.OrigenTipo)`, que es la variante que el grep de `.Contains(` no detecta). **Agregar un origen ya no requiere tocar la vista.**

Mismo criterio aplicado de entrada al ledger nuevo: `OrigenMovimientoStock` nace como helper, no como constantes dentro del Service.

#### Archivos y capas modificadas

**Domain (6 archivos)**
- `Entities/MovimientoStock.cs` — **nuevo**, ledger inmutable de stock.
- `Entities/PagoOrdenCompra.cs` — **nuevo**, línea de pago a proveedor.
- `Enums/TipoMovimientoStock.cs` — **nuevo** (`Compra=1`, `Venta=2`, `Ajuste=3`, `AnulacionVenta=4`; solo el primero tiene escritor).
- `Enums/EstadoPagoProveedor.cs` — **nuevo** (`Pendiente=1` declarado sin escritor, `Pagado=2`, `Revertido=3`).
- `Entities/Producto.cs` — `PrecioVentaDesactualizado` + `FechaUltimoCostoCompra`.
- `Entities/OrdenCompra.cs` — navegación `Pagos` + XML-doc corregido.
- (`Enums/EstadoOrdenCompra.cs`, `Enums/TipoMovimientoCCProveedor.cs`, `Enums/FormaPagoProveedor.cs`, `Entities/OrdenCompraItem.cs`, `Entities/Proveedor.cs`: XML-doc, pasada 3.)

**Application (9 archivos)**
- `Helpers/OrigenCajaMovimiento.cs` — **nuevo**, cierre de `LP-002`.
- `Helpers/OrigenMovimientoStock.cs` — **nuevo**.
- `Helpers/MedioPagoCajaMapper.cs` — `DesdeFormaPagoProveedor` (devuelve `null` para `CuentaCorriente`) + `EtiquetaFormaProveedor`.
- `Interfaces/IMovimientoStockService.cs`, `Interfaces/IEgresoPagoProveedorService.cs`, `Interfaces/IPagoProveedorService.cs` — **nuevos**.
- `Interfaces/IUnidadMedidaConversionService.cs` — `ConvertirConFactor` + `ValidarConversion`.
- `Interfaces/IOrdenCompraService.cs` — `RecibirAsync`.
- `Interfaces/IProductoService.cs` — filtro `precioVentaDesactualizado`.
- `DTOs/MovimientoStockDtos.cs`, `DTOs/PagoProveedorDtos.cs` — **nuevos**.
- `DTOs/OrdenCompraDtos.cs` — `RecepcionOrdenCompraResultDto`.
- `DTOs/CajaDtos.cs` — `OrigenEtiqueta`.
- `DTOs/ProductoDtos.cs` — `PrecioVentaDesactualizado` + `FechaUltimoCostoCompra`.

**Infrastructure (8 archivos)**
- `Services/MovimientoStockService.cs`, `Services/EgresoPagoProveedorService.cs`, `Services/PagoProveedorService.cs` — **nuevos**.
- `Services/OrdenCompraService.cs` — `RecibirAsync` + `EstadosRecibibles` + `ResolverFechaRecepcion`; ahora inyecta `IMovimientoStockService` e `ICCProveedorService` (**sigue sin inyectar `ICajaMovimientoService`**: no puede postear un egreso por accidente porque no tiene con qué).
- `Services/UnidadMedidaConversionService.cs` — las dos entradas nuevas, una sola fórmula.
- `Services/CajaMovimientoService.cs` — constantes → alias del helper, `OrigenEtiqueta` en la proyección, búsqueda por etiqueta de origen, orden por `origenEtiqueta`.
- `Services/CuentaCorrienteClienteService.cs` — el literal `"CobroCC"` → alias del helper.
- `Services/ProductoService.cs` — filtro + proyección + orden + búsqueda global de la bandera, y **quién la apaga** en `EditarAsync`.
- `Data/AppDbContext.cs` — 2 `DbSet` + configuración de las dos entidades nuevas.
- `DependencyInjection.cs` — 3 servicios nuevos.

**Web (5 archivos)**
- `Controllers/OrdenesCompraController.cs` — `Recibir`, `RegistrarPago` (GET/POST), `RevertirPago`, `ArmarDetalleAsync`.
- `Models/OrdenCompraViewModels.cs` — `PuedeRecibir` real, `PuedePagar`, `TotalPagado`, `SaldoPendiente`, `Pagos`, `MovimientosStock` + el ViewModel del formulario de pago.
- `Views/OrdenesCompra/RegistrarPago.cshtml` — **nueva**.
- `Views/OrdenesCompra/Details.cshtml` — botones de recepción y pago, alerta de recibida, card "Lo que entró al stock", card de pagos con reversión, pagado/pendiente en el total.
- `Views/Caja/Index.cshtml` — combo y columna desde el helper.
- `Views/Productos/Index.cshtml` — columna "Estado del precio" + filtro tri-estado.

#### Migración EF generada y aplicada

`20261006002448_EntregaTres_RecepcionMercaderiaYPagosProveedor` — **aplicada SOLO a `laplatense_dev`**.

- `Productos`: + `PrecioVentaDesactualizado` (`tinyint(1)`, `defaultValue: false`) y `FechaUltimoCostoCompra` (`datetime(6)` nullable).
- `MovimientosStock` (tabla nueva): índices `(ProductoId, Fecha)` y `(OrigenTipo, OrigenId)`.
- `PagosOrdenCompra` (tabla nueva): índices `OrdenCompraId`, `Fecha`, `Estado`.

**Estrictamente aditiva**: ninguna columna existente cambia de tipo, nombre ni nullabilidad, y no se borra nada. Sobre 112.485 productos no es una formalidad, es la condición para aplicarla sin ventana de mantenimiento. **Sin backfill, verificado** (ver pasada 6; el razonamiento completo está escrito en el `Up()` de la migración junto con la query de control).

**Producción sigue 4 migraciones atrás** (le faltan `EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago`, `D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`, `EntregaTres_ProveedoresCCCompras` y esta).

#### Evidencia de build y de ejecución

**Sin smoke test funcional por navegador** (lo prohíbe el rol del Implementador). Compensado con evidencia **ejecutada**, no con lectura de código:

1. **`dotnet build` de la solución: 0 errores**, 9 advertencias, todas preexistentes (`NU1902` de MailKit/MimeKit).
2. **Las vistas Razor SÍ compilan en el build** — comprobado metiendo un símbolo inexistente en `RegistrarPago.cshtml` a propósito (`CS0103` en la línea 293), y revertido. Sin esa comprobación, un build limpio no dice nada sobre las dos vistas nuevas.
3. **Grafo de DI validado** con `BuildServiceProvider(ValidateOnBuild + ValidateScopes)` en un proyecto de consola aparte: sin ciclos ni captive dependencies, y los 7 servicios (3 nuevos + 4 con constructor cambiado) resuelven de verdad. Las 3 fallas que aparecieron primero son **del arnés** y no del código (`IConfiguration` e `IWebHostEnvironment` los aporta el host de ASP.NET): se stubearon, porque si no tapan las fallas reales del grafo.
4. **51/51 checks de los Services ejercitados DIRECTO contra `laplatense_dev`**, con la base **devuelta a su línea base** al final (verificado: 0 filas de prueba restantes, 112.485 productos).

#### Casos medidos de conversión de unidades (los números, no "funciona")

Compra sembrada: proveedor nuevo, 2 productos, descuento de cabecera 10%, IVA 21%.

| Línea | Producto | Cantidad | Unidad compra | Factor | Precio | Subtotal |
|---|---|---|---|---|---|---|
| 1 | bulto de tornillos | 5 | Bulto | **12** | $12.000 | $60.000 |
| 2 | martillo suelto | 10 | Unidad (= stock) | **1** | $500 | $5.000 |

Aritmética fiscal: `Subtotal 65.000 → Desc 6.500 → base 58.500 → IVA 12.285 → Total 70.785`. `ratioDescuento = 0,9`.

| Criterio | Esperado | Medido |
|---|---|---|
| CA-1: bultos × factor | stock `0 → 60` (5 × 12, **no** 5) | **60,000** |
| CA-2: unidad simple tal cual | stock `5 → 15` | **15,000** |
| CA-6a: costo del bulto | `60.000 × 0,9 / 60 u = 900` | **900,00** |
| CA-6b: costo de la unidad | `5.000 × 0,9 / 10 u = 450` | **450,00** |
| CA-6c: `PrecioVenta` intacto | `1239,67` y `619,83` sin cambio | **sin cambio** |
| CA-6d: bandera prendida | `true` en los dos | **true** |
| CA-6e: `StockVerificado` | sigue en `false` (recibir no es contar) | **false** |
| CA-4a: `Cargo` por el Total | 1 movimiento de `70.785,00` | **1 / 70.785,00** |
| CA-4b: recepción no toca caja | movimientos de caja antes = después | **9 = 9** |
| CA-5: ledger por línea | 2 filas, `[60, 10]`, suma 70 | **2 / [60,000, 10,000] / 70,000** |
| CA-5b: mismo `OrigenId` | stock y CC apuntan a la misma OC | **43 / 43** |

**CA-3 + CA-8 (lo que más vale, y se midió corrompiendo el dato a mano):** se cargó una segunda compra con un producto `Bulto → Metro`, se puso su `FactorConversionAplicado = 0` **directo en la base** (es el único camino por el que puede quedar inválido, porque la carga lo valida) y se intentó recibir.

- Rechazada, con el mensaje nombrando el producto: *"ZZTEST Cable por rollo se compró por bulto y el stock se lleva por metro, pero la línea no tiene un factor de conversión válido..."*.
- **Y nada quedó a medio aplicar**, verificado campo por campo: stock `15,000 → 15,000` y `7,000 → 7,000`, movimientos de CC `1 → 1`, ledger de stock `2 → 2`, estado `Confirmada`. La línea 1 de esa compra (el martillo, que **sí** se podía convertir) **no se movió** — que es el punto del guard previo.

**CA-7:** recibir un `Borrador` → rechazado; recibir dos veces → rechazado ("duplicaría las dos cosas"); cancelar una `Recibida` → rechazado.

#### Casos medidos del paso 5

| Criterio | Medido |
|---|---|
| CA-1: multi-línea, un egreso por línea con su medio | `Egreso 40.000,00 Efectivo` / `Egreso 30.785,00 Transferencia` |
| CA-1b: un `Pago` de CC por línea | `Pago 40.000,00` / `Pago 30.785,00` |
| Mismo `OrigenTipo`/`OrigenId` en los dos ledgers | caja `[3,4]` = cc `[3,4]` |
| Misma fecha y mismo monto | igualdad por `(OrigenId, Monto, Fecha)` |
| CA-2: saldo del proveedor | `70.785 − 70.785 = 0,00` |
| CA-4: no pagar más que el saldo | `$70.786,00` rechazado contra `$70.785,00`; y `$1,00` sobre una compra saldada también |
| `CuentaCorriente` como forma de pago | rechazado con mensaje propio |
| Todas las líneas en cero | rechazado |
| CA-5: reversión por neto vivo | netos antes `CC −40.000,00` / `caja 40.000,00` → después **`0,00` y `0,00`** |
| CA-5: idempotencia por construcción | `RevertirEgresoAsync` sobre un pago ya revertido devuelve **`0,00`** (probado salteando la guarda de `Estado`) |
| Saldo después de revertir | vuelve a `40.000,00` |
| Total pagado excluye el revertido | `30.785,00` |
| CA-6: `LP-009` | día cerrado → *"La caja del día 04/10/2026 ya está cerrada..."*; fecha futura → rechazada |
| CA-7: `LP-002` | `PagoOC` en `Todos`, etiqueta "Pago a proveedor", filtro por origen y búsqueda global por etiqueta: **3 filas** |

`MH-001` cubierto **por ejecución** en las 10 consultas nuevas, **incluido el caso de resultado vacío** (que es donde la regla revienta): 0 excepciones.

#### Guía de pruebas manuales (a ejecutar por el cliente/QA, no por el Implementador)

**Preparación.** `laplatense_dev` no tiene ni un producto con unidad de compra distinta de la de venta: **hay que crear uno** o el camino principal del paso 4 no se ejercita. Producto nuevo con `UnidadVenta = Unidad`, `UnidadCompra = Bulto`, `FactorConversion = 12`, stock conocido.

1. **Conversión.** Compras → nueva, elegir ese producto, cantidad **5**, unidad **Bulto**, precio $12.000. Confirmar → **Registrar recepción** (elegir el día en que entró). El stock del producto tiene que subir **60**, no 5. En el detalle, la card "Lo que entró al stock" tiene que decir `+60,000 unidad`.
2. **Unidad simple.** Mismo flujo con un producto sin unidad de compra: el stock sube la cantidad tal cual.
3. **Factor faltante.** Producto con `UnidadCompra = Bulto` y **sin** `FactorConversion` (o en 0): la línea no se puede ni cargar (lo valida el alta). Para probar el guard de la recepción hace falta el escenario de la tabla de arriba (corromper el factor en la base) — **o** editar la ficha del producto para quitarle el factor después de cargar la compra y antes de recibirla.
4. **Caja no se mueve al recibir.** Mirar el total de egresos del día **antes** de recibir y **después**: tiene que ser el mismo. La deuda sí sube: Proveedores → Cuenta corriente.
5. **No se recibe dos veces / no se cancela una recibida.** Los dos botones tienen que desaparecer y, si se fuerza el POST, el sistema rechaza con mensaje.
6. **Costo sí, precio no.** Anotar `PrecioCompra` y `PrecioVenta` del producto antes de recibir. Después: el costo cambió al de la factura (neto de descuentos y por unidad de stock), el precio de venta **no**, y en Catálogo aparece el badge **"Precio sin recalcular"**. Filtrar por *"Costo actualizado, precio sin recalcular"*: tiene que traer solo esos productos.
7. **Quién apaga la bandera.** Editar el producto y guardar **sin tocar el precio**: el badge sigue. Editar y **cambiar el precio de venta**: el badge desaparece.
8. **Pago multi-línea.** En la compra recibida → **Registrar pago**: dos líneas (parte efectivo, parte transferencia) que sumen el total. Verificar en **Caja** dos egresos con su medio correcto, y filtrar por origen **"Pago a proveedor"**. El saldo del proveedor tiene que quedar en 0.
9. **No pagar de más.** Intentar un importe mayor al saldo pendiente: el botón se deshabilita en pantalla **y** el servidor rechaza si se fuerza.
10. **Reversión.** Revertir una de las dos líneas: la plata vuelve a la caja **con fecha de hoy** y con el **mismo medio**; la deuda sube; el pago queda con badge "Revertido"; el saldo pendiente de la compra vuelve a mostrar lo que falta. Intentar revertir de nuevo: rechazado.
11. **`LP-009`.** Cerrar la caja de un día y después intentar imputar un pago a ese día: rechazado nombrando el cierre.
12. **Anticipo.** Pagar una compra **Confirmada** (sin recibir): el saldo del proveedor queda **negativo** (a favor del negocio). Recibirla después: el `Cargo` lo salda.

#### Riesgos residuales y asunciones

1. **`Proveedor.TipoCambio` NO se aplica, y ahora pesa más.** La recepción convierte **unidades** pero **no monedas**. Si el operador carga una compra de un proveedor en dólares con los precios en dólares, el costo que queda en `Producto.PrecioCompra` **queda en dólares y mal** — y antes esto solo afectaba al total del documento, ahora se persiste en la ficha del producto. El comentario que prometía resolverlo en el paso 4 se corrigió. **Pendiente real, no cubierto.**
2. **El ledger de stock no es el libro mayor.** `Σ MovimientoStock` ≠ `Producto.Stock`: Ventas y el ajuste manual siguen escribiendo el stock sin dejar rastro, y lo histórico no se migró. Cualquier reporte que asuma lo contrario va a dar mal. Unificarlo es una tarea de datos + dos módulos en producción.
3. **Cheques sin cartera.** `Cheque` y `ChequeElectronico` se aceptan y mueven la plata **como si saliera en el momento**, cuando en realidad sale cuando el cheque se cobra. Simplificación declarada; la cartera es el paso 7.
4. **La fórmula fiscal exacta de la compra sigue sin confirmarse** contra una factura real del cliente (viene de una de marihogar). Ahora el `ratioDescuento` de esa fórmula determina el **costo que se persiste en el catálogo**, así que el error se propaga más lejos que antes.
5. **El factor de conversión sigue siendo fijo por producto** (pregunta abierta, sin respuesta del cliente). El snapshot de la línea lo absorbe mientras el operador corrija a mano, pero no lo resuelve.
6. **Recepción siempre total.** No hay parciales. Si llega la mitad de la compra, el operador tiene que elegir entre recibir todo (y el stock queda de más) o nada.
7. **El primer egreso automático del arqueo del cliente.** Ver el aviso de impacto abajo.
8. **Un producto dado de baja entre la carga y la recepción bloquea la recepción completa.** Es deliberado (no se puede ingresar stock a un producto que no existe, y saltearlo dejaría la deuda posteada por mercadería que no entró a ningún lado), pero el operador no tiene salida en pantalla más que cancelar la compra y cargarla de nuevo.

#### Aviso de impacto para el cliente — hay que darlo ANTES del deploy

**Este es el primer módulo que mete egresos automáticos en el arqueo de caja, además de los gastos.** En marihogar, el día que se deployó el equivalente, los egresos del período *"subieron mucho"* de golpe. **No es un bug**: es plata que siempre salió y hasta ese momento no se registraba en ningún lado. Pero si el cliente lo ve primero y pregunta después, el módulo nace con sospecha encima.
### Entrega 3 — ítem 4c (moneda y tipo de cambio) + paso 6 (pagos programados) (2026-10-05, rama `entrega-1-migracion`)

Dos frentes en una ronda. El primero **no era una feature pendiente: era un bug activo**. La ola 2
agregó `Proveedor.Moneda` y `Proveedor.TipoCambio` y **ninguno de los dos se aplicaba en ningún
cálculo** (verificado por grep: 100% de los hits eran persistencia, proyección o pantalla, cero
aritmética). Desde que la ola 3 hizo que la recepción escriba `Producto.PrecioCompra`, una compra
en dólares persistía el costo **en dólares dentro de un campo que todo el sistema lee como pesos**,
y aguas abajo de `PrecioCompra` cuelgan `PorcentajeRecargo` → `PrecioVenta` → `PrecioOferta`.

#### Resultado del escaneo de reutilización

1. **`cat_resumen.txt`**: sin match para moneda/cotización. Lo más cercano es `PAT-052` (línea que
   congela el factor de conversión) — **no es el patrón, es el CRITERIO**, y se copió entero.
   `PAT-053` (un pago, dos ledgers) ya estaba consumido por la ola 3.
2. **Código de `marihogar`**: `TipoCambio`, `Cotizacion` y `Moneda` dan **0 hits** en todo el repo.
   Todo es pesos implícitos, sin campo de moneda en ninguna entidad. **Sin antecedente: la moneda
   se construyó nueva.**
3. **Pagos programados SÍ tienen precedente** y se copió: `PagoOrdenCompraService.RegistrarPagoAsync`
   (programa si la fecha tentativa es futura), `ConfirmarPagoAsync`, `ActualizarFechaPagoAsync` y
   `ObtenerYMarcarPagosVencidosNoNotificadosAsync`. **Lo que NO se copió es su scheduler** (ver
   abajo).
4. **Dos patrones nuevos agregados al catálogo**: `PAT-055` (documento que congela su moneda y su
   cotización) y `PAT-056` (chequeo oportunista al primer request del día en vez de hosted service).

#### Parte 1 — la moneda, de punta a punta

**El modelo.** Tres columnas nuevas en `OrdenesCompra`:

- `Moneda` (enum, default `Peso`) y `Cotizacion` (`decimal(18,4)`, el **mismo ancho** que
  `Proveedor.TipoCambio` para que congelarla no la trunque). Se **precargan** de la ficha del
  proveedor al elegirlo y son **editables**: un proveedor que lista en dólares puede mandar una
  factura en pesos.
- `TotalEnPesos` (`decimal(18,2)`, **persistida**, con índice).

**Por qué `TotalEnPesos` se persiste y no se calcula.** Dos razones concretas, las dos medidas:

1. El `Cargo` de la cuenta corriente y el tope de pago tienen que ser **el mismo número al
   centavo**, o pagar el total no deja el saldo del proveedor en cero (criterio de aceptación 2).
   Recalcular pone una multiplicación y un redondeo en cada consumidor, que es cómo dos de ellos
   terminan difiriendo en un centavo.
2. **El listado ordena por el total del lado del servidor.** Una propiedad calculada en C# no
   traduce a SQL, y ordenar por `Total` mezclando monedas pone una compra de USD 1.000 arriba de
   una de $ 1.500.000. Es la columna que la grilla muestra como principal, así que es la que se
   ordena, se filtra y se busca.

**El punto único: `ConversionMoneda`** (`Application/Helpers/`). Estático, sin dependencias, mismo
rol que `ArgentinaTime` y `OrigenCajaMovimiento`. Tiene:

- `APesos(moneda, cotizacion, importe)` — **una sola fórmula**, un solo redondeo
  (`AwayFromZero`, igual que el resto de la aritmética del módulo). En pesos devuelve el importe
  tal cual e **ignora** la cotización. **LANZA** si la moneda es extranjera y falta la cotización:
  devolver el importe sin convertir "por las dudas" es exactamente el bug que esta ronda cierra.
- `Validar(...)` — la **única** definición de "cuándo hace falta cotización", consumida por las
  **cuatro mitades** de la guarda: alta, edición, confirmación y recepción.
- `Etiquetas` / `Simbolos` / `QueCoincidenConElTexto(...)` — un solo diccionario para el combo de
  filtro, el renderer de la grilla, los símbolos del formulario y la búsqueda global.

**Dónde se aplica.** Los importes del documento (`Subtotal`, `Total`, descuentos, impuestos, el
`PrecioCompra` de cada línea) quedan **en la moneda del documento**: es lo que dice la factura y lo
que el operador tiene delante. Los **tres** importes que salen de la compra van en **pesos**:

| Salida | Antes | Ahora |
|---|---|---|
| `Cargo` en la CC del proveedor | `orden.Total` (en dólares) | `orden.TotalEnPesos` |
| `Egreso` en caja (vía el tope de pago) | contra `orden.Total` | contra `TotalEnPesos` |
| `Producto.PrecioCompra` | el costo en dólares | convertido, una sola vez, al final |

En `RecibirAsync` la conversión va **al final y una sola vez**: el costo acumulado y la cantidad
están los dos en las unidades del documento, así que se divide primero y se convierte después — un
redondeo en vez de dos. El `ratioDescuento` es adimensional (cociente de dos importes de la misma
moneda) y no se toca.

**La guarda y sus cuatro mitades.** Guardar ya exige la cotización, pero eso no alcanza: hay
guardas simétricas en **confirmar** y en **recibir**, que cubren lo que la del alta no puede — un
documento cargado antes de que la columna existiera, o un `UPDATE` directo sobre la base. Sin
ellas, `TotalEnPesos = 0` posteaba una deuda de cero **en silencio**. Y `Validar` rechaza además
`Moneda = 0`, el valor que un POST armado a mano o un combo vacío mandan y que no corresponde a
ningún valor del enum.

#### Parte 2 — pagos programados

El esquema ya existía declarado sin escritor (`Estado = Pendiente`, `FechaPagoTentativa`,
`Notificado`): esta ronda le puso el escritor, **no el esquema** — cero columnas nuevas en
`PagosOrdenCompra`.

**Una línea de pago con `FechaPagoTentativa` estrictamente futura** nace en `Pendiente` y **no
mueve nada**: ni cuenta corriente ni caja. El par de asientos lo postea
`ConfirmarPagoProgramadoAsync`, por el **mismo** `PostearAsientosAsync` que usa el alta inmediata
(dos escritores, un solo lugar que escribe los dos ledgers; el paso 7 será el tercero).

**Tres números distintos y no intercambiables**, cada uno con su método:

- `ObtenerTotalPagadoAsync` — solo `Pagado`. Lo que **efectivamente salió**, y es lo que la cuenta
  corriente refleja.
- `ObtenerTotalComprometidoAsync` — `Pagado` + `Pendiente`. **Es el tope** del alta de un pago
  nuevo: con el primero como tope se podría agendar el total completo tres veces.
- `ObtenerSaldosAsync` — los devuelve juntos, en **una** consulta agrupada por estado (dos
  llamadas separadas podrían leer estados distintos si alguien confirma un pago en el medio).

**La fecha de los asientos es HOY, no la tentativa** (criterio del precedente, su CR-63, un defecto
que le reportó su cliente): la tentativa es una fecha sugerida y confirmar antes o después de ella
es lo habitual, así que imputar la plata al día planeado la mete en un arqueo al que nunca
perteneció.

**Divergencia deliberada del precedente.** Allá la confirmación **pisa** `FechaPagoTentativa` con
la fecha de hoy y deja `PagoOrdenCompra.Fecha` en el instante del registro: el documento y sus
asientos quedan con fechas distintas y **se pierde el plazo que se había pactado**. Acá se hace al
revés — `Fecha` (que está documentada como "el instante en que la plata salió") se reescribe a hoy
y `FechaPagoTentativa` queda **intacta** como registro de lo prometido.

**`ValidarPeriodoAbiertoAsync` (`LP-009`) y su mitad simétrica.** El alta de un pago enteramente
programado **no corre la guarda**, y es a propósito: no mueve un peso, así que exigirle un período
abierto sería impedir agendar un pago futuro porque el mes pasado ya se cerró. El criterio del
proyecto es el que ya decidía que el ajuste manual de CC la saltee: **lo que la hace necesaria es
que el movimiento escriba CAJA**, no que la operación se llame "pago". La **confirmación** sí la
corre, sobre el día de hoy.

#### La notificación: por qué NO hay hosted service (decisión de diseño)

`marihogar` usa un `BackgroundService` + `PeriodicTimer` a hora fija (03:10 ART, con triple
fallback de timezone duplicado en cada job). **No se portó**, por dos hechos del entorno:

1. Este proyecto no tiene **ni un** hosted service (verificado: 0 hits de `AddHostedService`), así
   que portar el patrón no reusa nada — construye una capacidad nueva.
2. Corre en **SmarterASP, donde el application pool se recicla por inactividad**. Un job de las
   03:10 en un sistema que se usa de 8 a 20 **puede no correr nunca** y nadie se enteraría: el
   aviso no llega y no hay ningún error que lo delate. Un scheduler que no se puede garantizar es
   **peor** que no tenerlo, porque se confía en él.

En su lugar: **`AvisoPagosProgramadosMiddleware`**, chequeo oportunista al primer request
autenticado de cada día de negocio argentino. Tres guardas, de la más barata a la más cara: solo
autenticados → un flag estático con el último día procesado (una comparación de `DateTime`, así
que el costo real es **una consulta por día y por proceso**) → y la idempotencia real, que **no es
el flag**.

**La idempotencia la da el mecanismo del precedente que no depende del scheduler**: filtrar
`Estado == Pendiente && !Notificado` y marcar `Notificado = true` **en la misma llamada**, con su
`SaveChanges`. Correrlo dos veces, o dos veces en paralelo, no duplica avisos. El orden importa:
si la garantía viviera en el flag en memoria, **cada reciclado de pool mandaría los avisos de
nuevo**. Y su **mitad simétrica**: reprogramar un pago pone `Notificado = false`, porque la fecha
nueva es un vencimiento nuevo — sin eso, reprogramar lo dejaba marcado como avisado para siempre.

El bloque de notificación va en su **propio try/catch** y no relanza: lo dispara un request del
operador, y que no se pueda crear un aviso no puede tumbar la pantalla que estaba abriendo.

**Si en el futuro hacen falta jobs de verdad, la decisión es DE HOSTING y no de código**:
application pool en `startMode: AlwaysRunning` con Idle Time-out en 0. **Corresponde consultarlo
con `olvidata-infra` antes de escribir un hosted service que el entorno no puede sostener.**

#### El barrido `LP-002` — 7 hallazgos propios

La **pasada 0** (verificar las premisas del brief) confirmó las cuatro: `TipoCambio`/`Moneda` sin
un solo uso aritmético, 0 hits de `AddHostedService`, `INotificationService.CreateAsync` con firma
**idéntica** a la del precedente, y los tres campos del paso 6 ya declarados. **El brief no tenía
premisas falsas esta vez** — es la primera ronda en que la pasada 0 confirma todo.

1. **La resta `Total − TotalPagado` estaba escrita a mano en CUATRO lugares** (el Service, el
   ViewModel del detalle, `RegistrarPago` del controller y `RecargarPagoAsync`) y los cuatro usaban
   `Total`. Con la moneda en el documento, los cuatro pasaron a restar **unidades distintas**:
   dólares menos pesos. Se cerró con `ObtenerSaldosAsync` — **ahora no la repite ninguno**.
2. **El listado ordenaba por `Total` del lado del servidor**, mezclando monedas: la grilla mentía
   por yuxtaposición. Pasó a ordenar y buscar por `TotalEnPesos`, con la moneda como columna
   visible **y su filtro** (regla del proyecto).
3. **`Details.cshtml` mostraba `ProveedorTipoCambio`**, o sea la cotización de HOY de la ficha, en
   una compra vieja: un número que esa compra **nunca usó**. Pasó a mostrar la congelada, con un
   aviso cuando la ficha difiere (`CotizacionDifiereDeLaFicha`) — el aviso es la prueba de que
   congelar sirve, no un error.
4. **El total de las compras en la CC del proveedor** (`Proveedores/CuentaCorriente.cshtml`) estaba
   en la moneda del documento, **al lado de movimientos de ledger que están todos en pesos**.
5. **`OrdenCompraItem.PrecioCompra` decía "en pesos"** en su XML-doc: cierto solo mientras la
   moneda no existía en el documento. Es `LP-008` — regla de negocio falsa viviendo en el repo.
6. **`Views/Proveedores/CuentaCorriente.cshtml` decía que la recepción "es la próxima etapa del
   módulo"**: falso desde el paso 4. Es un texto de la era del paso 3 que la ola 3 no barrió.
7. **La tercera copia del mapa de monedas.** `BusquedaHelper.EnumsQueCoinciden` compara contra el
   **nombre del enum** (`Dolar`), no contra la etiqueta visible (`Dólares`), así que
   `ProveedorService` tenía las dos etiquetas **escritas a mano** al lado de la llamada. Con el
   combo del filtro y el renderer de la grilla, eran **tres copias**. Se cerró con
   `ConversionMoneda.QueCoincidenConElTexto` y las dos líneas hardcodeadas se borraron: **agregar
   una moneda al enum ya no toca ningún call site.** Lo encontró el arnés, no la lectura: la
   consulta *ejecutaba* y devolvía 0 filas.

**Pasada 3 (promesas vencidas)** — 9 correcciones: los 5 lugares de `PagoOrdenCompra` que decían
"DECLARADO, NUNCA ESCRITO (paso 6)", los 2 de `EstadoPagoProveedor`, el de `IPagoProveedorService`,
y el de `DependencyInjection` ("para que los pasos 6 y 7 no vuelvan a armar el egreso inline") —
que ahora dice que **el paso 6 ya lo consumió y entró sin tocar una línea del punto único, que es
exactamente para lo que se había creado**. Más el `Proveedor.TipoCambio` que quedaba como PENDIENTE
DECLARADO y ya no lo es, y la referencia de `AppDbContext` a "la importación de listas (paso 6)",
que ahora no inventa un número de paso.

**Pasada 2 (hermanos semánticos)**: el grep de `DateTime` en entidades sigue dando **34** — esta
ronda **no agregó ninguna columna de fecha**. Lo que sí cambió es la **semántica** de dos que ya
existían, y las dos están declaradas: `PagoOrdenCompra.Fecha` ahora se **reescribe** al confirmar,
y `FechaPagoTentativa` es un **DÍA CALENDARIO sin hora**, no un instante UTC — por eso
`ListarPorOrdenCompraAsync` **no** la proyecta con `ArgentinaTime.From`, que le restaría tres horas
y la correría al día anterior. Verificado por grep que ningún call site la proyecta.

**Pasada 4 (vistas y JS)**: los 9 `toLocaleString` de las vistas tocadas son todos sobre importes,
cantidades, porcentajes y conteos. **Ninguno sobre una fecha** (`LP-006`). Los días hasta el
vencimiento los calcula el **Service** contra el día de negocio argentino, nunca un `new Date()` en
el navegador.

**Pasada 6 (la migración sobre las filas que YA estaban)** — y es el hallazgo más caro de la ronda,
ver abajo.

#### Migración EF — `EntregaTres_MonedaCompraYPagosProgramados`

Aditiva sobre el esquema (3 columnas + 1 índice en `OrdenesCompra`, **ninguna** en
`PagosOrdenCompra`). **Lo que no es aditivo es el dato**, y EF lo deja mal en las dos columnas NOT
NULL:

- **`Moneda` queda en 0**, que no corresponde a ningún valor del enum (el proyecto numera explícito
  desde 1). Es **literalmente el mismo defecto** que la migración de la ola 2 tuvo que repararle a
  85 proveedores.
- **`TotalEnPesos` queda en 0, y eso es PEOR**: es un importe que miente. Toda compra ya cargada
  pasaría a tener saldo pendiente 0 — la pantalla la mostraría como **totalmente pagada**, el tope
  de pago sería 0 así que no se le podría imputar un peso, y recibirla postearía un `Cargo` de
  **$ 0,00** en la cuenta corriente, en silencio.

Los dos `UPDATE` del backfill, con `WHERE` acotado para que correrla dos veces sea inocuo:

```sql
UPDATE OrdenesCompra SET Moneda = 1 WHERE Moneda = 0;
UPDATE OrdenesCompra SET TotalEnPesos = Total WHERE Moneda = 1 AND TotalEnPesos = 0 AND Total <> 0;
```

El índice se crea **después** del backfill. Y el backfill **se verificó ejecutándolo**, no
suponiéndolo: `laplatense_dev` tiene **0 compras**, así que los `UPDATE` no tocaron ni una fila
real — se fabricaron dos filas en el estado exacto post-`defaultValue` (una con total y una con
total 0), se corrieron los dos `UPDATE` literales de la migración, se comprobó con `GROUP BY` que
no quedara ninguna fila en `Moneda = 0` ni ninguna incoherente, se corrieron **otra vez** para
probar que son inocuos, y `ROLLBACK`. **La base quedó en su línea base.**

#### Archivos y capas modificadas

**Domain** — `OrdenCompra` (+`Moneda`, +`Cotizacion`, +`TotalEnPesos`, XML-doc de `Total`),
`OrdenCompraItem` (XML-doc de `PrecioCompra`), `Proveedor` (XML-docs de `Moneda` y `TipoCambio`),
`PagoOrdenCompra` (5 XML-docs), `EstadoPagoProveedor`, `FormaPagoProveedor`.

**Application** — **`Helpers/ConversionMoneda.cs` (NUEVO: el punto único)**,
`Interfaces/IAvisoPagosProgramadosService.cs` (NUEVO), `IPagoProveedorService` (reescrito: +5
métodos), `IOrdenCompraService` (+ filtro de moneda en `ListarAsync`), `OrdenCompraDtos`,
`PagoProveedorDtos` (+`SaldosCompraDto`, +`PagoProgramadoVencidoDto`, +`PagoProgramadoListItemDto`).

**Infrastructure** — `OrdenCompraService` (`AplicarFiscal` congela y convierte, `RecibirAsync`
postea en pesos y convierte el costo, `ConfirmarAsync` guarda, listado), `PagoProveedorService`
(reescrito: alta con programación, confirmación, reprogramación, baja, chequeo de vencidos, 3
saldos), **`Services/AvisoPagosProgramadosService.cs` (NUEVO)**, `ProveedorService` (se le quitó la
tercera copia del mapa), `AppDbContext`, `DependencyInjection`, la migración.

**Web** — **`Middleware/AvisoPagosProgramadosMiddleware.cs` (NUEVO)**, `Program.cs` (lo registra
**después de `UseAuthentication`**, o `context.User` no está poblado y no dispararía nunca),
`OrdenesCompraController` (+3 acciones de pagos programados + la agenda; los saldos salen del punto
único), `OrdenCompraViewModels`, `Views/OrdenesCompra/{Create,Details,Index,RegistrarPago}.cshtml`,
**`Views/OrdenesCompra/PagosProgramados.cshtml` (NUEVO)**,
`Views/Proveedores/{Index,CuentaCorriente}.cshtml`, `_Layout.cshtml`.

**tools/** — `ArnesEntrega3Item4c` (NUEVO, no es parte de la aplicación).

#### Evidencia de build y de ejecución

- **`dotnet build` de la solución: `Compilación correcta. 0 Errores`.**
- **Las vistas Razor SÍ compilan en el build**, probado como cada ronda: se metió un símbolo
  inexistente en `PagosProgramados.cshtml`, el build falló con `CS0103` **con número de línea
  (6,20)**, se revirtió y volvió a compilar limpio. Un build limpio por sí solo no dice nada sobre
  las vistas nuevas.
- **Grafo de DI** validado con `BuildServiceProvider(ValidateOnBuild + ValidateScopes)`. Esta vez
  el arnés necesitó **registrar Identity de verdad** (`AddIdentityCore` + `AddRoles` +
  `AddEntityFrameworkStores`), no stubear: `IAvisoPagosProgramadosService` depende de
  `UserManager<ApplicationUser>` y sin eso **el grafo falla por el arnés y esa falla tapa las del
  código**. Los tres servicios nuevos se resuelven.
- **Los Services ejercitados directamente contra `laplatense_dev`**, idempotente (prefijo `ZZTEST`,
  `LimpiarAsync` al principio y al final), corrido **3 veces**. Cierre: **0 filas de prueba
  restantes, 112.485 productos** (la línea base).
- **`MH-001`: las 7 consultas nuevas o modificadas se EJECUTARON, no se leyeron**, incluidas las
  dos que filtran por colección (`monedas.Contains(...)` en los dos listados) y el caso borde de la
  regla: la búsqueda global con **todas** las colecciones de enum **vacías**. Ejecutar fue lo que
  encontró el hallazgo 7 del barrido: la consulta *andaba* y devolvía 0 filas.
- **Lo que NO se probó**: `INotificationService.CreateAsync` dentro del flujo del aviso y el
  middleware en el pipeline real. Los dos necesitan usuarios con rol y un request HTTP, que es
  navegador — **queda para QA** (pasos 13 a 16 de la guía).

#### Los números medidos de una compra en dólares, de punta a punta

Compra de **10 bultos a US$ 100** (factor 10 → 100 unidades de venta), **10% + 5% en cascada**,
facturada con **21% de IVA**, cotización congelada **$ 1.480,50**:

| Concepto | Medido |
|---|---|
| Subtotal | US$ 1.000,00 |
| Descuento 10% | − US$ 100,00 |
| Descuento adicional 5% (**cascada**: sobre 900, no sobre 1000) | − US$ 45,00 |
| Base imponible | US$ 855,00 |
| IVA 21% | US$ 179,55 |
| **Total del documento** | **US$ 1.034,55** |
| Cotización congelada | $ 1.480,50 |
| **Total en pesos** | **$ 1.531.651,28** |
| **`Cargo` en la CC del proveedor** | **$ 1.531.651,28** (en pesos) |
| **`Egreso` en caja** al pagar el total | **$ 1.531.651,28** (en pesos) |
| **Saldo del proveedor al pagar el total** | **$ 0,00** |
| Stock ingresado | 100,000 unidades |
| **`Producto.PrecioCompra` resultante** | **$ 12.658,28** |

`PrecioCompra` = 855 (base **neta**, sin IVA) × 1.480,50 ÷ 100 unidades de venta. **Antes de esta
ronda ese campo quedaba en `8,55`** — el costo en dólares por unidad, dentro de un campo que el
catálogo lee como pesos. Los 10 criterios de aceptación de las dos partes dieron **OK**.

#### Guía de pruebas manuales (a ejecutar por el cliente/QA, no por el Implementador)

**Moneda**

1. Ficha de un proveedor → moneda **Dólares** + cotización. Nueva compra a su nombre: la cabecera
   tiene que **precargar** las dos, y el panel de total mostrar **"Total en pesos"** con la cuenta
   (`US$ X × $ Y`) a la vista.
2. Cambiar la moneda a **Pesos** en el formulario: el campo de cotización se **oculta y se limpia**,
   y los prefijos `$` de descuentos e impuestos vuelven de `US$` a `$`.
3. Guardar un borrador en dólares **sin cotización**: tiene que rechazarse con el mensaje de la
   moneda, no con un error genérico.
4. Confirmar y **recibir** la compra en dólares. Verificar que el mensaje de éxito muestre la cuenta
   hecha, que la **CC del proveedor** tenga el `Cargo` **en pesos**, y que la ficha del producto
   tenga `PrecioCompra` en pesos y la bandera de precio desactualizado prendida.
5. Pagar el total: el formulario tiene que precargar el importe **en pesos** y el saldo del
   proveedor cerrar en **cero**.
6. **Cambiar `Proveedor.TipoCambio` después** y volver al detalle: la compra no se mueve y aparece
   el aviso de que la ficha difiere.
7. Listado de compras: la columna **Moneda** y su filtro, el total **en pesos** como cifra
   principal, y **ordenar por Total** mezclando una compra en pesos y una en dólares (tienen que
   quedar en orden de pesos, no de número crudo).
8. Buscar **"Dólares"** en el buscador global del listado de compras **y** en el de proveedores.

**Pagos programados**

9. Registrar un pago con **fecha futura**: la pantalla tiene que avisar **en la línea** que queda
   programado, el botón cambiar a **"Programar el pago"** y el pie desglosar qué sale y qué queda
   agendado.
10. Verificar en **Caja** y en la **CC del proveedor** que **no se movió nada**. El detalle de la
    compra tiene que mostrar el badge **Programado** y la fila "Programado sin confirmar".
11. Intentar registrar otro pago sobre esa compra: tiene que rechazarse nombrando lo programado.
12. **Confirmarlo** y verificar que el egreso de caja quedó en **el día de hoy**, no en la fecha
    prevista, y que el aviso del popup lo dijo **de antemano**.
13. **Reprogramar** un pago y **darlo de baja** (el importe tiene que volver a quedar disponible).
14. **`LP-009`**: cerrar la caja de hoy e intentar **confirmar** un pago programado → rechazado. En
    cambio **programar** uno nuevo a futuro tiene que seguir funcionando con la caja cerrada.
15. **El aviso**: dejar un pago programado con fecha de ayer, **cerrar sesión y volver a entrar** al
    día siguiente (o reiniciar el pool). Tiene que aparecer **una** notificación por pago en la
    campana, para `SuperUsuario` y `Administrador`, con link a la compra.
16. **Recargar varias pantallas el mismo día**: no se tienen que duplicar las notificaciones.
17. Menú **Compras → Pagos programados**: la agenda, con los vencidos resaltados y los días hasta el
    vencimiento.

#### Riesgos residuales y asunciones

1. **`laplatense_dev` tiene 0 compras**, así que el backfill de la migración no corrió sobre ni una
   fila real. Se verificó con filas fabricadas y `ROLLBACK`. **Antes del deploy conviene contar las
   filas afectadas en el destino**:
   `SELECT Moneda, COUNT(*) FROM OrdenesCompra GROUP BY Moneda;` y
   `SELECT COUNT(*) FROM OrdenesCompra WHERE TotalEnPesos = 0 AND Total <> 0;` — las dos tienen que
   dar 0 **después** de migrar.
2. **La fórmula fiscal de la compra sigue sin confirmarse** contra una factura real del cliente, y
   ahora el `ratioDescuento` determina el costo que se persiste **en pesos** en el catálogo: el
   error se propaga igual de lejos que antes, solo que ahora en la unidad correcta.
3. **Una cotización mal tipeada contamina el catálogo igual que antes el bug.** La guarda solo exige
   que sea > 0: un 1.480,50 tipeado como 14.805 pasa. Mitigación implementada: la pantalla muestra
   el total en pesos **con la cuenta hecha** antes de guardar y el mensaje de la recepción la
   repite. No hay (ni se pidió) validación contra una cotización de referencia.
4. **El aviso depende de que alguien entre al sistema.** Si la ferretería no abre el sistema un día,
   ese día no sale el aviso — pero tampoco hay a quién avisarle. Es el trade-off explícito contra un
   job que **puede no correr nunca** en este hosting. Si hacen falta jobs de verdad: **decisión de
   hosting, consultar con `olvidata-infra`.**
5. **Un pago programado con `Cheque` no tiene cartera** (paso 7): al confirmarlo la plata sale
   completa en el momento, sin esperar la acreditación. Simplificación declarada y **vigente**.
6. **`PagoOrdenCompra.Fecha` de un pago `Pendiente` es el instante del registro** y no significa
   nada económicamente. Toda consulta de "qué salió en este período" tiene que filtrar
   `Estado == Pagado`; la autoridad de lo que salió de caja es el **ledger de caja**.
7. **El tope de 730 días** para programar un pago no es una regla del cliente: es una guarda contra
   el error de tipeo del año.
8. **La agenda de pagos programados no es un DataTable server-side**, a propósito: son los
   pendientes, un puñado de filas por definición. Si creciera, la regla del proyecto aplica.
### Entrega 6 — Presupuestos en PDF + aumento masivo de precios (2026-10-05, rama `entrega-1-migracion`)

Dos módulos en una ronda, los dos declarados **reuse total** de `marihogar` por el presupuesto. El reuse rindió en la estructura (máquina de estados, previsualizar→confirmar, patrón de PDF, conversión a venta) y **no** en la aritmética: el modelo de datos de este proyecto es distinto en los dos casos y es ahí donde estuvo el trabajo.

#### Resultado del escaneo de reutilización (obligatorio antes de implementar)

Paso 1 (`cat_resumen.txt`), con match en **6 patrones**:

- `PAT-050` (gate de precio por rol) — **aplicado tal cual** al presupuesto, incluidas sus dos condiciones de borde: la resolución server-side es *exactamente* la que ya usa la pantalla de venta (misma oferta, misma ventana de vigencia) y la validación de rango de los porcentajes va **adentro** de la rama de administrador.
- `PAT-052` (línea que declara su unidad y la congela) — `ItemPresupuesto.UnidadVenta` es snapshot del producto, mismo criterio que `ItemVenta`.
- `PAT-054` (bandera de costo actualizado con precio sin recalcular) — esta entrega construye **la mitad que faltaba**: el módulo que la **apaga** por lote. Hasta hoy la apagaba solo una edición manual de la ficha.
- `PAT-004` (RowVersion manual para concurrencia optimista en MySQL) — **no aplicable**: ninguna entidad de La Platense tiene `RowVersion` (verificado en todo el dominio). Resuelto con el criterio equivalente que el proyecto ya usa, ver abajo.
- `PAT-016` (búsqueda global + filtros en Session) — aplicado al listado de Presupuestos.
- `PAT-021` (modo de precio por ítem: fórmula vs. valor manual) — leído y **descartado** para esta ronda: el aumento masivo de acá no necesita excluir ítems del recálculo batch porque la exclusión se expresa por filtro, no por una marca por producto.

Paso 2 (código real de `marihogar`, en producción): copiados `Presupuesto`/`PresupuestoItem`/`EstadoPresupuesto`/`IPresupuestoService`/`PresupuestoService` (incluido el PDF con QuestPDF) y `AumentoMasivoDtos`/`IAumentoMasivoPrecioService`/`AumentoMasivoPrecioService`.

#### Lo que NO se pudo copiar, y por qué (presupuestos)

| Qué | marihogar | La Platense | Por qué importa |
|---|---|---|---|
| Cantidad | `int` | `decimal(18,3)` | El catálogo tiene productos en Peso y Metro. 2,5 kg y 0,750 m no son enteros. |
| Unidad de la línea | no existe | `UnidadVenta` congelada | El PDF tiene que decir "2,500 Kg" con la unidad que valía al cotizar. |
| IVA | 21% hardcodeado en dos precios fijos por producto | `PorcentajeIVA` por línea + discriminación por alícuota | Una ferretería mezcla 21% y 10,5% en el mismo documento. |
| Descuento + recargo | cascada `base*(1-d)*(1+r)` | `base*(1 - d/100 + r/100)` | La cascada es **el bug corregido acá el 2026-09-03**: 10% y 10% tienen que cancelarse. |
| Precio de la línea | llega del formulario, sin gate | lo resuelve el servidor salvo Administrador | `LP-014`/`LP-016`, cerrado el 2026-10-05. Un presupuesto que acepte precios del navegador reabre el agujero por una puerta nueva. |
| Vigencia | `VigenciaDias` + `FechaEnvio` | `ValidoHasta` (fecha explícita) | El cliente cotiza "hasta el viernes", y el PDF tiene que imprimir esa fecha incluso antes de enviarlo. |
| Destinatario | texto libre (no había módulo de Clientes) | `ClienteId` **o** nombre libre | Clientes existe y tiene cuenta corriente; el nombre libre cubre el caso real del mostrador. |

Sí se trajo tal cual: el estado derivado **calculado al leer y nunca persistido por un job** (`Vencido`, que acá se llama así y no `Expirado` para no introducir un segundo vocabulario), y el par `Estado = Convertido` + `VentaGeneradaId`.

**La conversión a venta sí cambió de lugar, y es una mejora:** en marihogar el botón navega a la pantalla de Ventas con los ítems precargados y la transición a `Convertido` ocurre recién cuando el vendedor confirma esa venta, porque allá la Venta se crea completa en una sola transacción y no hay estado editable intermedio. Acá la Venta **nace en `Borrador`**, que es exactamente el "carrito precargado" que marihogar tenía que simular: `ConvertirAVentaAsync` crea la Venta en Borrador con los ítems copiados 1 a 1, en una transacción con el cambio de estado del presupuesto. No queda ningún presupuesto marcado `Convertido` sin una Venta real detrás — el riesgo que el diseño de marihogar evitaba.

#### Separación `Observaciones` / `NotaInterna` (criterio 7)

Dos campos de texto y no uno, a propósito. El PDF imprime **solo** `Observaciones`. Con un único campo libre, cualquier anotación de margen o de costo termina impresa en la cotización que se le manda al cliente. El PDF tampoco imprime `PrecioCompra`, `PorcentajeRecargo` ni el precio de lista contra el cotizado. Sí imprime el descuento/recargo de la línea: eso el cliente **tiene** que verlo (le están bonificando).

#### Aumento masivo: las dos palancas, que es el punto de la entrega

En marihogar el aumento ajusta `PrecioEfectivo`, un precio de venta editable a mano: una sola palanca y un porcentaje. Acá el precio de venta es **derivado**:

```
PrecioVenta (sin IVA) = PrecioCompra x (1 + PorcentajeRecargo/100) / (1 + PorcentajeIVA/100)
```

Con ese modelo "aumentar los precios" son dos cosas distintas, y confundirlas deja el catálogo inconsistente. `ModoAumentoMasivo`:

- **`RecalcularDesdeCosto`** — el costo ya se movió (lo movió la recepción) y falta reaplicar el margen que el producto ya tiene. No cambia ninguna política: pone el precio donde la fórmula dice que debería estar. Es el modo que consume `PrecioVentaDesactualizado` y **el único que la apaga**.
- **`CambiarRecargo`** — escribe un `PorcentajeRecargo` nuevo por categoría/marca/proveedor y recalcula en consecuencia. Acá sí cambia una decisión comercial, y queda escrita.

En los dos modos el precio sale de la misma fórmula, así que el catálogo nunca queda con un `PrecioVenta` que no se corresponda con su `PorcentajeRecargo` (criterio 4, verificado sobre 2.000 filas: 0 inconsistencias).

#### Concurrencia optimista sin `RowVersion`: el criterio que SÍ usa el proyecto

`PAT-004`/marihogar protegen la ventana real de riesgo —el tiempo que el usuario tarda en revisar la previsualización— haciendo viajar el `RowVersion` de cada fila al navegador y de vuelta. **Ninguna entidad de La Platense tiene `RowVersion`** (verificado en todo `Domain/Entities` y en la configuración Fluent). El mecanismo que este proyecto ya usa para "cuándo se modificó esta fila" es `SoftDestroyable.UpdatedAt`, que `AppDbContext.StampSoftDestroyable` estampa en UTC en toda entidad modificada. Así que:

- El preview devuelve su instante (`GeneradoEn`, UTC) y vuelve en el aplicar.
- El aplicar **rechaza fila por fila** toda la que tenga `UpdatedAt > GeneradoEn`, en vez de pisarla, y las cuenta aparte. No aborta la corrida: con decenas de miles de productos en juego, tirar todo porque alguien editó un producto en el medio dejaría la pantalla inusable.
- **Guarda de universo además de la de fila:** el aplicar recuenta y, si el total no coincide con el que el preview informó, rechaza la corrida entera. Cubre lo que `UpdatedAt` no ve: altas, bajas, y productos que cambiaron de categoría/marca/proveedor (esos **salen o entran** del filtro, no quedan "modificados" dentro de él).

No se introdujo un tercer mecanismo. **Límite declarado:** `UpdatedAt` es `datetime(6)`, así que una modificación en el mismo microsegundo que el preview no se detecta — ventana irrelevante al lado de la que el patrón protege.

**`ExecuteUpdateAsync` se descartó a propósito**, aunque es una sola sentencia SQL y mucho más rápida: no dispara `SaveChanges`, así que **no estampa `UpdatedAt`** y el próximo aumento masivo se quedaría sin la marca que usa para la concurrencia. Se eligió la versión más lenta y consistente: lotes de 2.000 entidades trackeadas, un `SaveChanges` por lote y `ChangeTracker.Clear()` entre lotes (sin eso el `DetectChanges` se vuelve cuadrático sobre 112.485 filas).

#### Volumen: por qué el preview no manda el universo al navegador

marihogar devuelve **todas** las filas afectadas en el preview y las recibe **todas** de vuelta en el aplicar. Con 112.485 productos un filtro amplio haría viajar decenas de miles de filas y volver: pantalla inusable y un POST que no entra en los límites por defecto de ASP.NET. Acá el universo se identifica por el **filtro** (que el aplicar vuelve a ejecutar server-side) más el recuento esperado y el instante del preview; la muestra es una página de 25 (tope 100) y los totales son del universo completo.

#### Criterio tomado con las ofertas vigentes (criterio 5)

**Por defecto los productos con oferta vigente quedan AFUERA de la corrida**, con su contador visible en el preview y un checkbox explícito para incluirlos.

El motivo no es prudencia genérica: con una oferta vigente el precio que se cobra en el mostrador es `PrecioOferta` (`Producto.EsOfertaVigente` + `VentaWorkflowService.PrecioDeVentaVigente`), así que mover el `PrecioVenta` de esos productos **no cambia nada hoy y cambia todo el día que la oferta vence** — un aumento que entra en vigencia solo, en una fecha futura, sin que nadie lo haya pedido ese día. Si el usuario los incluye, se recalcula el precio de lista y **la oferta no se toca** (el preview lo dice con esas palabras, y marca cada fila con oferta vigente con un badge).

#### Dos defectos propios encontrados EJECUTANDO, no leyendo

1. **El preview prometía un precio distinto del que escribía.** La muestra proyectaba el precio nuevo en SQL sin redondear y mostraba `26254,014876033058` mientras el aplicar escribía `26254,02`. Es exactamente lo que el patrón de dos pasos existe para evitar. `Math.Round` con `MidpointRounding` no se traduce a SQL, así que se redondea en memoria sobre la página de muestra (≤100 filas, no cuesta nada).

2. **La variación porcentual del preview era un número secuestrable por tres filas basura.** El catálogo migrado tiene **tres productos con `PrecioCompra` de 6,3 billones** (datos sucios del legacy, preexistentes — verificados contra el backup de la tabla antes de la primera corrida). Esos tres aportan ~el 99,99% de la suma de precios, así que la "variación promedio ponderada" del catálogo entero daba **0,00% mientras 112.000 productos cambiaban de precio**. Se reemplazó por los contadores **sube / baja / igual** (inmunes a outliers) y las sumas quedaron etiquetadas como lo que son: un total de control. Medido sobre todo el catálogo: **14.781 suben, 14.808 bajan, 82.433 quedan igual** — o sea que ~29.600 productos del catálogo migrado tienen hoy un `PrecioVenta` que no coincide con su propia fórmula por centavos.

#### Tercera exclusión, no pedida pero necesaria: costo en cero o negativo

El catálogo tiene **37 productos con `PrecioCompra` negativo y 1 en cero** (medidos por SQL en `laplatense_dev`). La fórmula es fiel y por eso les escribe un **precio de venta negativo** (medido: `T78501500`, costo −3,64 y recargo 33%, quedaba en −4,00). Un precio de venta negativo es peor que un costo mal cargado: el costo lo ve solo el administrador, el precio lo ve el mostrador y lo cobra la venta. Se excluyen en los dos modos, se informan en el preview con un aviso rojo que nombra el problema, y **no se corrigen desde acá**: arreglar esos 38 productos es una decisión del cliente sobre su catálogo.

#### Auditoría: por qué una entidad propia y no `AuditLog`

marihogar escribe la auditoría de su aumento masivo en `AuditLogs` con el filtro serializado a JSON. **Esa tabla no existe en La Platense**: se eliminó por pedido explícito del cliente el 2026-07-28. El precedente real del proyecto para "cambio masivo auditado" es `AjusteStock` — entidad propia, columnas tipadas, usuario responsable. `AumentoMasivoPrecio` sigue ese criterio: columnas y no JSON, así que el listado se lee y se filtra sin parsear nada.

**Granularidad: una fila por corrida, no una por producto.** Con 112.485 productos, un detalle por producto significaría hasta 112.485 filas por corrida y una tabla de auditoría más grande que el catálogo. Lo que el criterio 6 pide (quién, cuándo, qué filtro, cuántos) entra entero en la cabecera. **Consecuencia declarada: este registro no alcanza para deshacer una corrida producto por producto.** Deshacer no está en el alcance; si el cliente lo pide, hace falta una tabla de detalle.

#### Barrido `LP-002` — resultado completo

Radio: todo lector/escritor de `PrecioVenta`, `PorcentajeRecargo`, `PrecioOferta`, `PrecioVentaDesactualizado` y `FechaUltimoCostoCompra`.

| # | Hallazgo | Resolución |
|---|---|---|
| 1 | `VentaWorkflowService` (XML-doc de clase) seguía declarando como asunción vigente que *"Descuento/Recargo de `ItemVenta` son importes monetarios de la línea, no porcentajes"* — **falso desde el 2026-08-21** (defecto D-descuento, QA Entrega 2), con la fórmula corregida tres líneas más abajo en la misma clase. | Reescrito como corrección fechada, apuntando al XML-doc de `ItemVenta` como definición de referencia. `LP-008`, cuarta aparición en el proyecto. |
| 2 | `ProductoService.UpdateAsync` era **el único** que apagaba `PrecioVentaDesactualizado`. El flag lo prende la recepción; sin un apagador por lote, el cliente tenía que abrir 112.485 fichas de a una. | Es el módulo de esta entrega: `RecalcularDesdeCosto` lo apaga, y **solo en los productos aplicados** (verificado: 50 banderas sembradas dentro del filtro → 0; 50 afuera → 50, intactas). |
| 3 | `PorcentajeRecargo` tiene **un solo lector funcional** en toda la app (el precio sugerido del formulario de Producto). Cambiarlo masivamente no rompe nada más — pero tampoco se refleja en ningún lado si el `PrecioVenta` no se recalcula. | Es la razón de que `CambiarRecargo` recalcule el precio **siempre**, no opcionalmente. |
| 4 | La regla de la oferta vigente está escrita **cuatro veces**: `Producto.EsOfertaVigente` (definición de referencia, método de instancia → no traducible a SQL), inline en `ProductoService.ListarAsync`, inline en `BuscarParaVentaAsync`/`CodigoBarrasLookupService`, y `PrecioDeVentaVigente` en `VentaWorkflowService`. | Las dos nuevas (`PresupuestoService.PrecioDeVentaVigente` y la `Expression` del aumento masivo) llevan un comentario que dice explícitamente *"si se cambia una, hay que cambiar las dos/cuatro"* y por qué: si divergen, el vendedor cotiza a un precio distinto del que vio. **Pendiente declarado:** extraer la regla a un punto único. No se hizo en esta ronda para no tocar código de Ventas ya en producción. |
| 5 | La columna "Venta" del listado nuevo era `orderable` y **no tenía rama de ordenamiento** en el Service: el click en el encabezado no hacía nada y el usuario no tenía forma de saberlo. | Rama agregada y ejecutada (las 7 columnas × 2 direcciones, más una columna inexistente que cae al default). |
| 6 | `PrecioVenta` es `decimal(18,2)` y hay productos con precio hasta **6,9 billones** y hasta **negativo**. Ningún lector lo acota. | Origen de las dos correcciones del preview (contadores en vez de variación ponderada) y de la exclusión por costo no positivo. |
| 7 | Conversión presupuesto→venta: la venta creada queda en `Borrador`, y si un **Vendedor** la vuelve a guardar, el gate de precio por rol le **recalcula los precios desde el producto** y los cotizados se pierden. | **No se debilitó el gate.** Se agregó `Venta.PresupuestoOrigenId` y la pantalla de venta muestra un aviso que lo dice con esas palabras (más fuerte para el Vendedor, que es quien lo sufre). Es una **decisión abierta para Joaquín**, abajo. |

#### Migración EF — `20261006021452_EntregaSeis_PresupuestosYAumentoMasivo`

Totalmente **aditiva**, sin backfill necesario:

- `Presupuestos` (nueva). `ValidoHasta` como `date` a propósito: es un día de negocio, y el tipo impide la tentación de compararlo contra `DateTime.UtcNow`. Índices: `Fecha`, `(Estado, ValidoHasta)` —el filtro por estado efectivo es siempre ese par— y `VentaGeneradaId`.
- `ItemsPresupuesto` (nueva). Mismos tipos y precisiones que `ItemsVenta` **campo por campo**: la conversión es una copia 1 a 1 y cualquier diferencia de precisión perdería datos en silencio.
- `AumentosMasivosPrecio` (nueva). FKs `Restrict` a Categoría/Marca/Proveedor: el registro de auditoría no deja borrar la categoría que nombra.
- `Ventas.PresupuestoOrigenId` (columna nueva, nullable, **sin FK** — trazabilidad, no dependencia de ciclo de vida) + su índice.

Aplicada **solo a `laplatense_dev`**. Producción no se tocó y sigue 4 migraciones atrás (más esta, 5).

#### Archivos y capas modificadas

**Domain**
- `Enums/EstadoPresupuesto.cs`, `Enums/ModoAumentoMasivo.cs` — nuevos, valores explícitos y `[Display]`.
- `Entities/Presupuesto.cs`, `Entities/ItemPresupuesto.cs`, `Entities/AumentoMasivoPrecio.cs` — nuevos.
- `Entities/Venta.cs` — `+PresupuestoOrigenId`.

**Application**
- `DTOs/PresupuestoDtos.cs`, `DTOs/AumentoMasivoDtos.cs` — nuevos.
- `Interfaces/IPresupuestoService.cs`, `Interfaces/IAumentoMasivoPrecioService.cs` — nuevos.
- `DTOs/VentaDtos.cs` — `+VentaDetalleDto.PresupuestoOrigenId`.

**Infrastructure**
- `Services/PresupuestoService.cs` — CRUD + máquina de estados + conversión a venta + PDF (QuestPDF, ya en el repo vía `ExportService`; **no se agregó ninguna librería**).
- `Services/AumentoMasivoPrecioService.cs` — preview + aplicar por lotes + historial.
- `Services/VentaWorkflowService.cs` — `PresupuestoOrigenId` en el mapeo + corrección `LP-008` del XML-doc.
- `Data/AppDbContext.cs` — 3 `DbSet` + Fluent API + índice en `Ventas.PresupuestoOrigenId`.
- `DependencyInjection.cs` — los dos Services como Scoped.

**Web**
- `Controllers/PresupuestosController.cs` (policy `RequireVentas`), `Controllers/AumentoMasivoPreciosController.cs` (policy **`RequireAdministracion`**) — nuevos.
- `Models/PresupuestoViewModels.cs`, `Models/AumentoMasivoViewModels.cs` — nuevos.
- `Views/Presupuestos/{Index,Editar,Details}.cshtml`, `Views/AumentoMasivoPrecios/Index.cshtml` — nuevas.
- `Views/Ventas/Editar.cshtml` — aviso de precios congelados; `Models/VentaViewModels.cs` y `Controllers/VentasController.cs` lo cablean.
- `Views/Shared/_Layout.cshtml` — 2 entradas de menú, cada una con su condición de rol (la del aumento masivo es **más estricta que la sección** en la que vive).

**Por qué el aumento masivo es `RequireAdministracion` y no `RequireVentas`:** cambia el precio de mostrador de hasta 112.485 productos en un click. Es la contracara del gate de precio por rol, que ya le impide al Vendedor cambiar el precio de **una** línea de venta.

#### Evidencia ejecutada (sin smoke test funcional, sin navegador)

- **Build de la solución completa: 0 errores** (4 advertencias `NU1902` preexistentes de MailKit/MimeKit).
- **`node --check` sobre el JS embebido de las 4 vistas nuevas + `Ventas/Editar.cshtml` como control** (vista preexistente en producción, usada para validar el extractor): 5/5 OK. El compilador de Razor no chequea el JS de `@section Scripts`.
- **Dos sondas EF desechables en el scratchpad** (proyecto consola fuera del repo que referencia `Infrastructure`, corridas contra `laplatense_dev`, borradas al terminar) con **la tabla `Productos` respaldada por `mysqldump` antes y restaurada después** — la base quedó en su línea base exacta (112.485 productos, 0 presupuestos, 0 corridas de aumento).
- **`MH-001` cubierto POR EJECUCIÓN, no por lectura**, en las 6 combinaciones de filtro del aumento masivo (incluidas las que devuelven **0 filas**, que es donde la regla revienta) y en las 10 ramas del buscador global del listado. Cero colecciones locales de `string` en el código nuevo: los filtros de catálogo son comparaciones por Id **escalar** (la pantalla elige *una* categoría, no una lista, precisamente porque un `IN` sobre colección local era el candidato obvio a la séptima aparición), y los dos `IN` que hay son de `int`. El de proveedor es un `EXISTS` correlacionado sobre `CodigoProveedorProducto`, no un `IN`.
- Se verificó que una `Expression<Func<Producto,bool>>` era obligatoria para la regla de la oferta: un método `static bool` compila igual y **revienta en runtime** contra MySQL, que es la misma razón por la que `Producto.EsOfertaVigente` ya estaba escrita inline en `ProductoService`.

#### Los tiempos medidos sobre el catálogo real (criterio 7)

Catálogo: **112.485 productos** en `laplatense_dev`.

| Operación | Alcance | Tiempo |
|---|---|---|
| Preview, filtro vacío (peor caso) | 112.022 productos | **464 ms** (caliente) / 1,0–2,2 s (frío) |
| Preview por categoría | 62.657 | 527 ms – 1,1 s |
| Preview por marca | 15.592 | 206 – 318 ms |
| Preview por proveedor (`EXISTS` sobre 110.683 mapeos) | 15.593 | 465 ms – 2,5 s |
| Preview "solo desactualizados" | 0 | 607 – 693 ms |
| Preview con las 4 palancas juntas | 0 | 371 – 961 ms |
| **Aplicar** por categoría | 62.657 | **10,4 s** |
| **Aplicar** todo el catálogo (peor caso) | 112.054 | **7,6 – 8,0 s** |
| Generar PDF de un presupuesto | 2 ítems | 585 ms |

El preview está **muy por debajo** de lo que necesita una pantalla interactiva. El aplicar sobre el catálogo completo tarda ~8 s, que es un tiempo de operación batch aceptable y que **la pantalla informa al usuario** (el mensaje de éxito trae la duración medida server-side). No hizo falta paginar el aplicar más allá de los lotes de 2.000 ni sacarlo a background.

#### Criterios de aceptación verificados con números, no con "funciona"

**Parte 1 — Presupuestos**

1. 2,5 kg y 0,750 m guardados **sin truncar** (`2,500` / `0,750`), con su unidad congelada (`Peso`/`Metro`) y el PDF imprimiéndolas con 3 decimales + etiqueta (`Kg`/`Mt`). ✔
2. 10% desc + 10% rec sobre 2,5 × $1.000 → subtotal **$2.500,00 exactos** = precio de lista. ✔
3. IVA mixto: $2.500 al 21% + $1.500 al 10,5% → IVA **$682,50**, exacto contra el cálculo a mano, y el PDF lo discrimina **por alícuota**. ✔
4. Vendedor posteando `precio=1, iva=0, desc=90` → guardado `precio=1000,00 (el del producto), iva=21,00, desc=0,00, rec=0,00`. Administrador posteando `precio=777, iva=0` → `precio=777,00` (su privilegio) e `iva=21,00`: **el IVA se ignora para todos los roles**. ✔
5. Conversión: presupuesto → `Convertido` + `VentaGeneradaId=9022`; venta `#9022` en `Borrador` con 2 ítems, cantidades, unidades, precios, IVA, descuento y recargo **idénticos**, totales iguales al centavo ($4.682,50), y `PresupuestoOrigenId=1`. Reconvertir el mismo → rechazado nombrando la venta. Con un Cliente real del catálogo, la venta hereda ese `ClienteId`. ✔
6. Presupuesto vencido (`ValidoHasta` 3 días atrás, estado persistido `Aprobado`, efectivo `Vencido`): conversión **sin** confirmación → rechazada con la fecha en el mensaje; **con** confirmación → convierte y el mensaje de éxito avisa que se convirtió vencido. La UI usa un diálogo **distinto** del normal, rojo, que nombra la fecha y exige tildar una casilla. ✔
7. PDF: **94.689 bytes**, cabecera `%PDF-`, `NotaInterna` ausente de los bytes crudos, y PDF de un id inexistente → `null` (no 500). ✔

**Parte 2 — Aumento masivo**

1. Preview con precio actual y resultante por producto + total de afectados (y, de yapa, sube/baja/igual, excluidos por oferta, por falta de recargo y por costo no positivo). ✔
2. Aplicar por categoría tocó **solo** esos: suma de `PrecioVenta` **fuera** del filtro, `1.198.213.420,28` antes y después (idéntica al centavo); cantidad de productos en la categoría sin cambios (62.857 → 62.857). ✔
3. `PrecioVentaDesactualizado`: 50 banderas sembradas dentro del filtro → **0**; 50 afuera → **50**. ✔
4. `CambiarRecargo` a 77% sobre una marca: 15.592 aplicados, **2.000 filas revisadas, 0 inconsistentes** entre `PorcentajeRecargo` y `PrecioVenta`. ✔
5. Ofertas vigentes: criterio **excluir por defecto**, declarado arriba, visible en el preview y por fila (badge). ✔
6. Auditoría con usuario, fecha UTC, modo, % aplicado, las 4 palancas del filtro y los 4 contadores de resultado. ✔
7. Tiempos medidos arriba. ✔

**De yapa, verificado:** concurrencia optimista — 3 productos editados entre preview y aplicar → `rechazadosPorConcurrencia=3`, los otros 62.719 aplicados, y el mensaje le dice al usuario que vuelva a previsualizar para esos. Guarda de universo — recuento esperado mentido en +7 → corrida **rechazada completa** nombrando los dos números.

#### Guía de verificación manual (a ejecutar por el cliente/QA, no por el Implementador)

1. **Presupuestos → Nuevo**: destinatario libre, vigencia a 15 días, agregar un producto en Peso con cantidad `2,5` y otro al 10,5%, guardar, **reabrir** y confirmar que los inputs numéricos **no quedaron vacíos** (`LP-003`: la regla aplica a la mitad de salida, y reabrir es el único momento donde se ve).
2. Como **Vendedor**: los inputs de precio/desc/rec van en `readonly`, y el cartel de candado explica por qué.
3. Marcar como enviado → aprobar → **Ver PDF**: comprobar que la vigencia sale impresa, que el IVA se discrimina por alícuota y que la nota interna **no** aparece.
4. **Convertir en venta** → la venta abre en Borrador con el aviso de precios congelados; cargarle pagos y confirmar.
5. Forzar un vencido (editar `ValidoHasta` a ayer mientras está en Borrador no se puede: hay que vencerlo por el paso del tiempo o por base) y probar la conversión: tiene que pedir la confirmación explícita.
6. **Aumento masivo** (solo Administrador): previsualizar sobre una categoría, mirar los contadores y los avisos de exclusión, paginar la muestra, **cambiar un filtro** y verificar que la vista previa se invalida sola.
7. Aplicar sobre una categoría chica y verificar en el catálogo que la columna de precio desactualizado se apagó **solo ahí**.
8. Entrar a `/AumentoMasivoPrecios` como **Vendedor**: tiene que dar **403**.

#### Riesgos y supuestos

1. **La venta convertida pierde los precios cotizados si un Vendedor la re-guarda.** Documentado en el código, avisado en la pantalla, **no resuelto**: resolverlo requiere una excepción al gate de precio por rol y eso es una decisión de Joaquín (abajo).
2. **`laplatense_dev` tiene 0 productos con `PrecioVentaDesactualizado`**, porque ninguna recepción corrió ahí. El modo "recalcular desde el costo" con el filtro de desactualizados **no tiene ni un dato real que lo ejercite**: se midió sembrando 100 banderas a mano. Para probarlo de punta a punta hay que recibir una compra primero.
3. **Datos sucios del catálogo migrado, preexistentes:** 3 productos con costo de 6,3 billones, 37 con costo negativo, 1 en cero. Los 38 de costo no positivo quedan excluidos del aumento; los 3 de 6,3 billones **sí entran** y se recalculan (su costo es absurdo pero positivo, y excluirlos por "parecer raro" sería un criterio arbitrario). Hay que corregirlos en el catálogo.
4. **~29.600 productos** tienen hoy un `PrecioVenta` que no coincide con su propia fórmula por centavos. Una corrida de "recalcular desde el costo" sobre todo el catálogo los alinea. Es inocuo en importe pero conviene que el cliente sepa que su primer uso del módulo va a reportar ~29.600 cambios.
5. **No hay deshacer.** La auditoría es por corrida, no por producto.
6. El aplicar sobre el catálogo completo tarda ~8 s de request sincrónico. En SmarterASP, con el pool frío, puede ser más. Si el cliente lo usa seguido sobre todo el catálogo, conviene medirlo en producción antes de decidir si va a background.

#### Pruebas mínimas requeridas para QA

- Presupuesto con cantidades decimales + IVA mixto, guardado y **reabierto** (`LP-003`).
- Gate de precio con los 3 roles, incluido un POST armado a mano contra `/Presupuestos/Guardar` con precio e IVA manipulados.
- Ciclo completo Borrador → Enviado → Aprobado → Convertido, y los caminos de rechazo y de baja.
- PDF en los 6 estados, y de un presupuesto sin ítems.
- Buscador global del listado con texto, número, importe, fecha y nombre de estado (incluido "vencido").
- Aumento masivo: preview + aplicar en los dos modos, con cada filtro y con los 4 combinados; `403` como Vendedor; invalidación de la vista previa al cambiar un filtro; y el caso de concurrencia (editar un producto en otra pestaña entre previsualizar y aplicar).
- Contar productos antes y después de aplicar, **dentro y fuera** del filtro.

#### Checklist de salida para merge

- [x] Lógica de negocio en Services, nada en Controllers.
- [x] Migración EF aditiva, generada y aplicada **solo a dev**.
- [x] `MH-001` verificado por ejecución, incluidos los resultados vacíos.
- [x] `LP-002` barrido completo, 7 hallazgos, todos resueltos o declarados.
- [x] `LP-003` aplicado en los dos formularios nuevos (helper `num` con `InvariantCulture`).
- [x] `LP-008` corregido (1 comentario que contradecía el código desde el 2026-08-21).
- [x] `LP-007` aplicado al `continuar` del guardado de presupuestos.
- [x] `KOI-B01` respetado (los dos checkboxes del aumento masivo usan `asp-for`).
- [x] Día de negocio por `ArgentinaTime`; `ValidoHasta` declarado como día de negocio y `Fecha`/`PreviewGeneradoEn` como instantes UTC.
- [x] Enums con valores explícitos y nuevos al final.
- [x] Design system: `.ov-form-page--wide`, `.ov-page-head`, `.ov-form-actions`, `.ov-required`, `.ov-field-hint`; Select2 en todo combo; SweetAlert2 en toda confirmación; DataTables server-side con filtro por columna visible; `PAT-016` en el listado nuevo.
- [x] Build 0 errores + `node --check` 5/5.
- [x] Base de dev devuelta a su línea base.
- [ ] **Sin push y sin deploy** (pedido explícito de Joaquín: "no publicar, dejar el desarrollo listo"). Producción sigue 4 migraciones atrás.

#### Decisiones que necesita Joaquín

1. **La venta convertida y el gate de precio.** Si un Vendedor re-guarda el borrador de una venta que salió de un presupuesto, los precios cotizados se reemplazan por los vigentes. Hoy: aviso en pantalla y nada más. Las opciones son (a) dejarlo así, (b) que el Vendedor no pueda editar una venta con `PresupuestoOrigenId`, o (c) que el gate acepte los precios de una venta convertida porque ya pasaron por él al cotizarse. **(c) es la que respeta el espíritu del presupuesto, y es la que más hay que pensar antes de escribir.**
2. **Los 38 productos con costo cero o negativo y los 3 con costo de 6,3 billones.** Son datos del catálogo migrado. ¿Se corrigen a mano, se dan de baja, o se deja que el módulo los siga excluyendo?
3. **¿El preview tiene que poder exportarse a Excel antes de aplicar?** Con 112.000 productos, "revisar la vista previa" en una muestra de 25 por página es revisar poco. No estaba pedido y no se hizo.
4. **¿Hace falta deshacer una corrida?** Si sí, hay que agregar la tabla de detalle y es una ronda aparte.
5. **La regla de la oferta vigente está escrita en 4 lugares** (ahora 6 con los dos nuevos). Extraerla a un punto único toca `VentaWorkflowService`, que está en producción. ¿Se hace ahora o se deja declarado?


## Bullets del historial de ajustes archivados el 2026-10-06 (segunda tanda)

- 2026-10-05 (Entrega 3, pasos 1 a 3): implementados **Proveedor ampliado + ABM propio, cuenta corriente de proveedores y ordenes de compra**, sobre la rama `entrega-1-migracion`. Commit local, **sin push y sin deploy** (pedido explicito de Joaquin). Frontera deliberada: **nada toca stock, caja ni cuenta corriente** — la recepcion (paso 4) y los pagos (paso 5) no entran, y `IOrdenCompraService` no expone `RecibirAsync` justamente para que no se pueda llamar por accidente. Reutilizacion del paso 1 del escaneo: `PAT-001` (ledger, port de `marihogar/CCProveedorService.cs` con el camino de vuelta ya recorrido en `MovimientoCCCliente`), `PAT-005`, `PAT-008`/`PAT-016`. Sin antecedente y catalogado como **`PAT-052`**: el modelo de unidad de la linea de compra (`Cantidad` decimal + `UnidadCompra` declarada + factor **congelado** en la linea; en marihogar la cantidad es `int` y la linea no declara unidad). Primer consumidor de `CodigoProveedorProducto` en toda la app (110.683 mapeos que ninguna pantalla leia). **Barrido LP-002 completo con 5 hallazgos propios**, incluido que la premisa del brief era falsa (`Proveedor` tenia CERO consumidores en `Web/`, lo que permitio una migracion estrictamente aditiva y mantener `Nombre` como columna) y que la migracion dejaba los 85 proveedores existentes con `Moneda = 0`, un valor que no existe en el enum. **2 bugs propios encontrados ejecutando** (el neto vivo filtrado por tipo, que devolvia la suma en vez del vigente; y el neto vivo sin acotar por proveedor, que habria mezclado el saldo inicial de todos). Migracion `EntregaTres_ProveedoresCCCompras` aplicada **solo a `laplatense_dev`**. Build limpio y 161/161 checks ejecutados contra dev, con la base devuelta a su linea base. Detalle completo en la seccion "Entrega 3 — pasos 1 a 3" arriba.
- 2026-10-05 (**Sprint 0 - gate de precio por rol en Ventas**, rama `entrega-1-migracion`): cerrado el defecto por el que cualquier usuario con `RequireVentas` podia vender a cualquier precio — `GuardarBorrador` tomaba `PrecioUnitario`/`Descuento`/`Recargo` del formulario y el Service los persistia sin control de rol, abierto en produccion. Se copio el criterio de `marihogar` (CR-22, ya en produccion): un `esAdministrador` resuelto **solo** en el Controller con `User.IsInRole` y pasado al Service como dato explicito del DTO, unica puerta que habilita leer esos campos del payload; para cualquier otro rol el precio se resuelve server-side con `PrecioDeVentaVigente` (oferta vigente por dia de negocio argentino si la hay y es > 0, si no `PrecioVenta`), que es **la misma** resolucion que ya hacia la pantalla, y el descuento y el recargo quedan en 0, descartados **en silencio**. No se trajo de marihogar la cascada de descuento/recargo (el bug corregido el 2026-09-03) ni su manejo de subtotal. El **barrido `LP-002`** rindio dos hallazgos propios: el subtotal c/IVA editable no tiene `name` y por lo tanto el gate de `PrecioUnitario` ya lo cubre (no hacia falta un segundo control), y un **comentario prescriptivo falso preexistente** en `ItemVenta` que declaraba la formula en cascada en dos lugares — el patron de `LP-008`, corregido en la misma pasada. Queda **una deuda explicita para Joaquin**: `Items[].PorcentajeIVA` sigue llegando del cliente para cualquier rol (un vendedor que lo postea en 0 baja el total ~21%), excluido a proposito por el brief de esta ronda. Sin migracion EF. Evidencia ejecutada sin navegador: build limpio, prueba de que las vistas Razor compilan, render del atributo booleano `readonly` verificado ejecutando las tres llamadas que emite Razor, y el Service ejercitado directo contra `laplatense_dev` con los dos roles en una transaccion revertida (15 checks OK, 0 filas sobrevivientes).
