<!-- Archivado de docs/marihogar/definiciones/5-implementador.md el 2026-10-02 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - 2026-09 (2 bloques archivados)

- Sprint CR-83 (2026-09-30) — Costo de cobranza por venta: comisión de plataforma + IVA + impuestos bancarios
- Sprint CR-84 (2026-09-30) — Los pagos a proveedores descuentan de la caja del local

---

## Sprint CR-83 (2026-09-30) — Costo de cobranza por venta: comisión de plataforma + IVA + impuestos bancarios

**Gate de presupuesto salteado por pedido explícito del cliente.** Definiciones 1/2/3 cerradas el 2026-09-30 (CA-83.1 a CA-83.9; diseño HU-83.1 a HU-83.5; mapa por capa en `3-arquitecto-mvc.md`). Sobre el working tree convivían dos trabajos ajenos sin commitear (descuento adicional de Orden de Compra y CR-82, reversión de estado de cheque): **no se tocó ninguno de sus archivos**. El único archivo compartido es `AppDbContextModelSnapshot.cs`, que la migración nueva regeneró sobre los cambios que ya tenían pendientes esos dos trabajos — al commitear hay que separar los hunks o commitear los tres juntos.

### Escaneo de reutilización

Paso 1 (`docs/patrones/cat_resumen.txt`): sin patrón de costo de cobranza / comisión de plataforma — es construcción nueva. Sí dio match en tres patrones que se aplicaron tal cual, ya identificados por Arquitectura:

- **PAT-020** (marihogar, CR-64/65/67) — reversión acotada a lo efectivamente posteado. El código real reutilizado no es el del catálogo sino `ChequeService.RevertirEstadoAsync` (CR-82, en el working tree): el cálculo de saldo neto `Σ Egreso no-reversión − Σ Ingreso reversión` se copió de ahí y se adaptó de `MovimientoCCProveedor` a `MovimientoCCLocal`.
- **PAT-023** (delicias-naturales) — editar un pago ya posteado es reversión + alta, nunca UPDATE del movimiento. Aplicado en `VentaService.ActualizarProcesadorPagoAsync`.
- **PAT-012** — previsualizar → confirmar. Aplicado en la pantalla de recálculo retroactivo.
- **Precedente interno `ConfiguracionCuotaTarjeta` (CR-40)** — configuración de porcentajes en base de datos editable en pantalla. `TasaCostoCobranza` es su generalización con vigencia por fecha. De ahí también sale la decisión de sembrar en `SeedData` y no en la migración (ver abajo).

Sin patrón nuevo para agregar al catálogo: el cálculo de costo de cobranza es específico del dominio de marihogar (tasas de MP/Payway, extracto del Banco Provincia) y no hay una pieza genéricamente reutilizable más allá de los tres patrones que ya existen.

### Archivos y capas

**Domain**
- `Enums/ProcesadorPago.cs` — nuevo. `Ninguno=1, MercadoPago=2, Payway=3, BancoCarrefour=4`. Agregado puro, `Ninguno` como default: los ~700 `PagoVenta` históricos quedan con costo 0 y comportamiento idéntico.
- `Entities/TasaCostoCobranza.cs` — nueva. **No** hereda `SoftDestroyable` (configuración con vigencia, se cierra con `VigenteHasta`, nunca se borra).
- `Entities/PagoVenta.cs` — +6 columnas: `Procesador`, `CostoComision`, `CostoIva`, `CostoImpuestosBancarios`, `CostoTotalCobranza`, `TasaCostoCobranzaId`. Todas con default 0 / `Ninguno`.

**Application**
- `DTOs/CostoCobranzaDtos.cs` — nuevo: `CostoCobranzaDto` (con `NetoAcreditado` y `SinTasaConfigurada`), `TasaCostoCobranzaListItemDto/Filtro/Input`, `RecalculoCostoCobranzaLineaDto/PreviewDto/ResultDto`.
- `Interfaces/ICostoCobranzaService.cs`, `Interfaces/ITasaCostoCobranzaService.cs` — nuevos.
- `DTOs/VentaDtos.cs` (`PagoVentaInput.Procesador`; `PagoVentaDto` + plataforma y desglose), `DTOs/RegistroPagoVentaDtos.cs` (`PagoVentaLineaInput.Procesador`), `DTOs/PagoTarjetaDtos.cs` (columnas de costo + filtros `Procesador`/`SinProcesador` + `RequiereProcesador`), `DTOs/RentabilidadDtos.cs` (`CostoCobranza`, `MargenNeto`, `MargenNetoPorcentaje`), `Interfaces/IVentaService.cs` (`ActualizarProcesadorPagoAsync`).

**Infrastructure**
- `Services/CostoCobranzaService.cs` — nuevo, **único punto que calcula y postea** (CRM-001). Resolución de tasa por `Procesador+Metodo+Cuotas` con vigencia (Cuotas matchea NULL con NULL, nunca "cualquiera"); recálculo previsualizar/aplicar compartiendo un único núcleo (`ArmarLineasRecalculoAsync`) para que el paso 1 y el paso 2 de PAT-012 no puedan divergir.
- `Services/TasaCostoCobranzaService.cs` — nuevo. CRUD sin baja, detección de solape real de intervalos de vigencia y cierre automático de la anterior al dar de alta la nueva.
- `Data/AppDbContext.cs` — `DbSet<TasaCostoCobranza>`, config de `PagoVenta` (defaults + índice por `Procesador`) y de la tabla nueva (índice compuesto en el orden exacto en que resuelve el Service).
- `Data/SeedData.cs` — `SembrarTasasCostoCobranzaAsync`, 18 filas idempotentes con `VigenteDesde = 01/09/2026`.
- `Services/VentaService.cs` — los 3 puntos de alta/reversión propios (`ConfirmarAsync`, `AcreditarPagoAsync`, `CancelarAsync`, `EliminarPagoAsync`), validación server-side de plataforma obligatoria (REG-004), columnas y filtros nuevos en `ListarPagosTarjetaAsync`, y `ActualizarProcesadorPagoAsync` (PAT-023).
- `Services/PagoVentaService.cs` — tercer punto de alta (`RegistrarPagoAsync`), delegando en el mismo método de dominio.
- `Services/RentabilidadService.cs` — costo de cobranza del período y margen neto, leídos de `ICostoCobranzaService` (un único origen por número, criterio de CR-80). El margen bruto NO se toca.
- `Services/CCLocalService.cs` — la exclusión de movimientos de ventas canceladas (CR-67) ahora cubre también `OrigenTipo="CostoCobranza"`.
- `Services/CajaService.cs`, `Services/ProyeccionFinancieraService.cs` — revisados por LP-002 y documentados; sin cambio de comportamiento (ver "LP-002" abajo).
- `DependencyInjection.cs` — registrados los 2 servicios nuevos (Scoped).

**Web**
- `Controllers/ConfiguracionCostosCobranzaController.cs` + `Views/ConfiguracionCostosCobranza/{Index,Create,Edit,_Form,_FormScripts,Recalcular}.cshtml` + `Models/TasaCostoCobranzaViewModels.cs` — nuevos, `[Authorize(Policy = "RequireAdministracion")]`. El recálculo vive en el mismo controller que la configuración (decisión, ver abajo). `_Form`/`_FormScripts` van separadas porque una partial de Razor no puede declarar `@section Scripts`.
- `Views/Shared/_Layout.cshtml` — link "Costos de cobranza" bajo Configuración, al lado de Cuotas de tarjeta. REG-010 verificado: el controller al que apunta tiene la misma policy que envuelve ese bloque del sidebar.
- `Controllers/PagosTarjetaController.cs` + `Views/PagosTarjeta/Index.cshtml` — 5 columnas nuevas (Plataforma + 4 de costo), filtros por plataforma y "Sin plataforma asignada", y edición inline de la plataforma por AJAX con `ajax.reload(null, false)` (patrón on-demand de CR-69).
- `Controllers/VentasController.cs` + `Views/Ventas/{Create,Details}.cshtml` — select de Plataforma condicional por medio de pago (REG-002), costo estimado informativo por fila actualizando sólo el elemento afectado (REG-008), validación en JS además del Service (REG-004), y endpoint `CostoCobranzaEstimado` de sólo lectura. En `Details`, la tabla de pagos gana Plataforma y Costo de cobranza (desglose en el tooltip).
- `Views/Rentabilidad/Index.cshtml` — card "Margen neto del período" al lado del bruto, que pasa a rotularse "Margen bruto". El chip de ventana dice que el costo de cobranza se cuenta por fecha de acreditación (KOI-017).
- `Views/CCLocal/Index.cshtml` — la columna Origen resuelve el caso `CostoCobranza` con link a la Venta y etiqueta legible.

### Migración EF

`20260930161626_AddCostoCobranzaPorVenta` — crea `TasasCostoCobranza` (con índice compuesto `Procesador+Metodo+Cuotas+VigenteDesde`, no único: la misma combinación tiene una fila por período de vigencia) y agrega las 6 columnas a `PagosVenta` con sus defaults + índice por `Procesador`. **Sin remapeo de datos existentes y sin INSERTs**: las tasas las siembra `SeedData`. **No se aplicó contra ninguna base** — queda pendiente `dotnet ef database update`.

### Decisiones tomadas que no estaban en las definiciones

1. **Base de los impuestos bancarios: el NETO acreditado, no el bruto.** Corrección recibida durante la implementación. `ImpuestosBancarios = (Monto − Comision) × (%IIBB + %Ley25413) / 100`. Verificado contra la liquidación del 29/09/2026 de $292.428,59: ARBA $5.263,70 = 1,80% de ese neto y Ley 25413 $1.754,57 = 0,60% — sobre el bruto del pago ($366.000) ninguno da. Documentado en el XML doc de `CalcularAsync` con ese ejemplo.
2. **`PorcentajeComision` con precisión `decimal(18,4)`, no `18,2`** como fijaba Arquitectura. El coeficiente real de las cuotas de Payway se despejó del extracto como **20,2714%** y con 2 decimales se truncaba a 20,27: ~$29 de diferencia sobre una liquidación de $670.600. Los 4 porcentajes de la tabla usan 18,4; todas las columnas de dinero siguen en 18,2.
3. **Seed de tasas en `SeedData.cs`, no en la migración.** Arquitectura ponía los INSERTs en la migración. Se siguió el único precedente del repo (CR-40 con `ConfiguracionCuotaTarjeta`): es idempotente, no pisa un porcentaje ya corregido por el Administrador, y una migración ya aplicada no puede completar una combinación que se agregue después.
4. **Tasas de Payway despejadas del extracto, reemplazando el 2,00% plano del seed original.** 1 pago 3,92% · 3 cuotas 4,00% exacto · 6 cuotas 20,2714% (coeficiente 0,797286, verificado en 4 liquidaciones independientes). **9 y 12 cuotas quedan en 0,00 a propósito**: esos planes se cobran por Mercado Pago y no aparecen en ninguna liquidación del Provincia. Débito 1,30% y transferencia 0,80% son **informados, no medidos**.
5. **`PorcentajeIva = 0` en TODAS las filas del seed**, incluidas las de Mercado Pago. Los porcentajes sembrados son costo total (con IVA adentro si lo llevan) y no hay liquidación de MP contra la cual despejarlo. Sembrar 21% sobre los ~$530.000 de comisión de MP de septiembre habría inventado ~$111.000 de costo que puede no existir. La columna se mantiene para cuando el cliente traiga una liquidación real. **Consecuencia a avisar:** las filas de Payway llevan IVA 0 también en Débito y Transferencia, donde el porcentaje es un arancel informado y no una quita observada — ahí el IVA podría corresponder. Es editable en pantalla y está comentado en el seed.
6. **El recálculo filtra por la fecha con la que se POSTEA el egreso, no por `PagoVenta.Fecha`.** Para tarjeta de crédito eso es `FechaAcreditacionEfectiva`. Es el criterio que fija CA-83.4 y el mismo que corrigió el análisis de septiembre en `trazabilidad.md` (12 pagos acreditados, no 11 con fecha de pago en el mes).
7. **Sin FK de `PagoVenta.TasaCostoCobranzaId` a `TasasCostoCobranza`.** Es una referencia de auditoría, no una relación de negocio: una FK `Restrict` impediría para siempre depurar una fila de configuración mal cargada. Mismo criterio que `MovimientoCCLocal.UsuarioId` (CR-62).
8. **`AcreditarPagoAsync` RECALCULA el desglose antes de postear**, en vez de usar el que se persistió al registrar el pago. La tasa vigente en la fecha de acreditación puede no ser la que estaba vigente al registrarlo, y es la de la acreditación la que la plataforma efectivamente aplica.
9. **El recálculo y la configuración comparten controller.** Un segundo controller sumaba ruta, link de menú y policy que mantener sincronizados sin ganar nada; el acceso al recálculo es un botón en el listado de tasas.
10. **`RentabilidadService` lee el costo de cobranza ANTES del early-return de "período sin ventas".** Un período sin ventas puede igual tener costo posteado (acreditación de una tarjeta cobrada el mes anterior), y dejarlo en 0 contradiría la Caja del mismo período.

### LP-002 — los 5 lugares que leen `OrigenTipo`, revisados

`OrigenTipo="CostoCobranza"` es nuevo en `MovimientoCCLocal` (OrigenId = VentaId, PagoVentaId siempre poblado).

- `CajaService.ObtenerTotalesAsync` — **sin cambios**. Suma todo Egreso que no sea `AjusteApertura`: el costo entra en `EgresosPeriodo`, que es lo buscado.
- `CajaService.ObtenerDesgloseFacturadoAsync` — **sin cambios, invariante de MH-004 verificada**: `noFacturados` se calcula como `totalIngresos − facturados` sobre el mismo universo que `ObtenerTotalesAsync`, así que la igualdad se mantiene por construcción. El egreso no aparece (la consulta sólo trae Ingresos) y el contramovimiento de reversión, que sí es un Ingreso, cae del lado "no facturado" — correcto: no es un cobro a un cliente. Mismo caso que el Ingreso de un Gasto anulado, que es el que motivó ese fix. Documentado en el código.
- `CCLocalService.ListarMovimientosAsync` — **2 cambios**: (a) la columna Origen de CR-62 resuelve `CostoCobranza` con link a la Venta y etiqueta "Costo de cobranza" (sin esto quedaba texto crudo sin link); (b) **hallazgo no previsto por Arquitectura**: la exclusión de movimientos de ventas canceladas (CR-67) filtraba sólo `OrigenTipo="Venta"`, así que cancelar una venta ocultaba su Ingreso pero dejaba visibles el egreso de costo y su contramovimiento. Se extendió el filtro.
- `ProyeccionFinancieraService` — **sin cambio de comportamiento, decisión documentada**: el egreso entra en `EgresosReales` (es plata que salió de verdad) pero NO alimenta `gastoOperativoPorMes`, que es el promedio con el que se proyectan los meses futuros. El costo de cobranza no es un gasto recurrente independiente: es proporcional a las ventas, que ya se proyectan por su propio camino (cobros comprometidos + saldos de ventas abiertas). Sumarlo proyectaría dos veces el mismo efecto.
- `DashboardService` — **sin cambios**. Desde CR-80 el margen delega en `IRentabilidadService` y no tiene cálculo propio: la card se actualiza sola.

### Doble conteo (riesgo técnico de CR-83)

La previsualización del recálculo **muestra** los gastos de categoría `ComisionesBancarias` no anulados del rango, con cantidad y monto, en un `alert-danger` que va primero en la pantalla y se repite en el SweetAlert de confirmación (cambiando el botón a rojo). **No los anula**: la decisión es del usuario. En septiembre 2026 son 14 gastos por $1.561.000 que representan lo mismo que el recálculo va a postear.

### Evidencia

`dotnet build MariHogar.slnx` → **0 errores** (9 warnings preexistentes de NU1902 por MailKit/MimeKit). Verificado además que las vistas Razor se compilan en el build (se introdujo un error deliberado en `Recalcular.cshtml`, el build lo reportó, se revirtió y volvió a 0 errores) — o sea que el build limpio cubre también las 6 vistas nuevas y las 6 modificadas. **Sin smoke test propio** (regla del proyecto: el cliente prueba a mano).

### Pendientes para el cliente / QA

1. Aplicar la migración (`dotnet ef database update`) y reiniciar, para que el seed de tasas corra.
2. Verificar los **19** porcentajes sembrados en Configuración > Costos de cobranza (10 de Mercado Pago — incluida `MercadoPago + Transferencia`, agregada al corregir MH-031 —, 7 de Payway, 1 de Banco Carrefour y 1 de `BancoDirecto + Transferencia`, agregada al corregir MH-032), en especial IVA (todas en 0) y los de Payway de 9/12 cuotas y débito/transferencia.
3. Completar la plataforma de los pagos históricos en Ingresos con el filtro "Sin plataforma asignada".
4. Anular los 14 gastos manuales de septiembre **antes** de aplicar el recálculo del período.
5. Correr el recálculo de 01/09/2026 a 30/09/2026 y contrastar contra el objetivo **reenunciado** (el de $1.278.947,36 estaba mal calculado, ver MH-031): **$1.279.554,27** = Payway $517.869,27 (comisión $461.810,32 + impuestos bancarios $56.058,95) + Mercado Pago $761.685,00. Con dos salvedades que NO son bugs: (a) el pago de $366.000 del 29/09 va a dar $621,91 de comisión de más que el extracto (0,17%) porque Payway aplicó ese día 20,1015% y no el 20,2714% del seed — desvío conocido, documentado en el seed, no se persigue; (b) el objetivo **excluye transferencias y débito**, que hoy no tienen plataforma asignada y por lo tanto no generan costo. Si en el paso 3 se les asigna plataforma, el total posteado va a superar el objetivo (~$20.000 sobre los $609.997,97 de transferencias y $239.000 de débito de septiembre) y eso es correcto, no un error.
6. Confirmar que correr el recálculo dos veces sobre el mismo rango no duplica nada (CA-83.8).
7. Verificar que cancelar una venta con costo posteado, eliminar un pago y cambiar la plataforma de un pago ya acreditado dejan el saldo de la CC Local igual que antes de la operación (CA-83.5).

### Correcciones del parte de QA (2026-09-30, NO-GO → aplicado, pendiente de re-verificación)

QA dio **NO-GO** sobre la primera pasada. Parte completo en `6-qa.md`, sección "CR-83 (2026-09-30)". Los 4 defectos de código están **aplicados y pendientes de re-verificación** — el cierre lo declara QA en contexto nuevo. Build tras las correcciones: **0 errores**.

**MH-027 (crítico) — aplicado, pendiente de re-verificación.** `MariHogar.Infrastructure/Services/VentaService.cs`, `EliminarPagoAsync`. El lookup `.Where(m => m.PagoVentaId == pagoVentaId && !m.EsReversion).FirstOrDefaultAsync()` dependía de una unicidad **de hecho, nunca declarada**: hasta CR-83, `PagoVentaId` identificaba una sola fila no-reversión del ledger (QA lo verificó contra producción: 77 filas, todas con n=1). El egreso de costo la vuelve no-única. Se agregó `&& m.OrigenTipo == "Venta"` y un `OrderBy(m => m.Id)` determinista. El barrido pedido (`grep -rn "PagoVentaId" MariHogar.Infrastructure/`) dio **un solo** lookup de tipo "buscar *la* fila" — ese —; los 4 restantes en `CostoCobranzaService` ya filtraban por `OrigenTipo`, y los de `CCLocalService`/`PagoVentaService` son escrituras o agregaciones. `PagoOrdenCompraService:287` (la clave hermana `PagoOCId` en el ledger de proveedores) ya filtra por `OrigenTipo` y no lo toca este CR.

**MH-028 (alto) — aplicado, pendiente de re-verificación, con un desvío respecto de lo sugerido.** `ICostoCobranzaService.RevertirEgresoAsync` acepta ahora una `DateTime? fecha`. La decisión NO se resolvió igual en los 3 call sites, porque la naturaleza de la acción no es la misma:
- `ActualizarProcesadorPagoAsync` → **pasa la fecha del egreso que reemplaza**. Es el caso que QA reportó y el escenario central de CA-83.7: es una corrección de dato histórico, y el egreso nuevo se postea en el período original, así que la reversión tiene que ir al mismo período.
- `CancelarAsync` y `EliminarPagoAsync` → **siguen en hoy (`fecha: null`), a propósito y ahora documentado**. Son hechos reales de hoy (MH-021), y el contramovimiento del Ingreso hermano — que estos dos métodos ya posteaban antes de CR-83 — también queda con la fecha de hoy. Retrofechar solo la mitad "costo" de la misma corrección creaba una inconsistencia nueva en vez de arreglar una. El efecto que QA señala para el caso "venta cancelada" se resuelve por MH-029, no retrofechando.

**MH-029 (medio) — aplicado, pendiente de re-verificación.** `CostoCobranzaService.ObtenerCostoPeriodoAsync` excluye los movimientos de ventas canceladas con la misma subquery correlacionada MH-001-safe que usa `CCLocalService.ListarMovimientosAsync`. Sin esto, el listado de CC Local ocultaba el egreso de una venta cancelada pero la card "Margen neto" del mismo período lo seguía descontando.

**MH-030 (bajo) — aplicado, pendiente de re-verificación.** `VentasController.CostoCobranzaEstimado` resuelve la tasa con `HorarioArgentino.Ahora` en vez de `DateTime.UtcNow` (PAT-010).

**MH-031 (calibración) — resuelto en documentación y con una fila de seed.** Tres cosas:
1. El ejemplo del XML doc de `CalcularAsync` pasa a usar una liquidación que **sí** verifica la tasa sembrada (670.600 → 534.659,95, ARBA 9.623,88 y Ley 25413 3.207,96 sobre el neto). El ejemplo anterior (366.000 → 292.428,59) contradecía el propio seed, como detectó QA.
2. El desvío de ese pago queda documentado en el seed como **desvío conocido**: $621,91 (0,17%) porque Payway aplicó ese día 20,1015%. **No** se agrega una segunda fila de 6 cuotas: la tabla tiene una sola tasa vigente por combinación a propósito, y romper eso para tapar $621,91 haría inauditable todo el resto.
3. Se agregó la fila **`MercadoPago + Transferencia` al 3,40%**, que faltaba y dejaba un hueco funcional real (cobrar una transferencia por MP es un caso normal del negocio). El 3,40% sale de la misma fuente que el resto de las filas de MP (memoria del proyecto, "Pix / transferencia 3,40% al instante"), no es un número inventado. El seed pasa de 17 a **18** filas, que es lo que decía esta memoria — la discrepancia que QA marcó queda resuelta por el lado correcto. **No** se agregaron `MercadoPago + BancoCarrefour` ni `Payway + MercadoPago`: no tienen fuente y, más importante, no existen en el negocio.

**Riesgo residual que NO se corrigió, con argumento.** QA marca que `AplicarRecalculoAsync` es read-then-write sin constraint única, y que dos corridas concurrentes podrían duplicar. No se agrega la única: un índice único sobre `(OrigenTipo, PagoVentaId, EsReversion)` **prohibiría un segundo posteo legítimo** después de una reversión, que es exactamente lo que hace PAT-023 al cambiar de plataforma. La mitigación ya está y es la barata que QA propone: el botón de confirmar se deshabilita al enviar y sólo se rehabilita cuando la previsualización posterior dice que todavía queda algo por postear, y el posteo corre en una transacción única.

### MH-032 (2026-09-30) — plataforma "Directo a la cuenta bancaria" (aplicado, pendiente de re-verificación)

Último defecto abierto de la re-verificación de QA, cerrado con el dato que confirmó el cliente el 30/09/2026 (las transferencias de clientes entran a la cuenta del Banco Provincia).

**El problema.** La validación de CA-83.2 exigía una plataforma para `Transferencia` pero sólo ofrecía Mercado Pago, Payway y Banco Carrefour. Una transferencia que el cliente recibe directo en su cuenta no pasó por ninguna de las tres, así que el operador quedaba forzado a informar una plataforma que no intervino — 4 cobros por $609.997,97 sólo en septiembre 2026, o sea que se dispara en el uso diario. Y esos cobros sí tienen costo real: ~$14.640 de IIBB + Ley 25413 que hasta ahora no se registraban de ninguna forma.

**Qué se hizo.**
- `ProcesadorPago.BancoDirecto = 5`, agregado puro al final. **Sin migración**: `Procesador` es un `int`, el seed corre en runtime y es idempotente. No es lo mismo que `Ninguno` — Ninguno significa "este medio no tiene costo de cobranza"; BancoDirecto es una plataforma elegida a conciencia, con comisión 0 pero IIBB 1,80% y Ley 25413 0,60%, porque la acreditación entra al banco (verificado: el 30/09/2026 una transferencia de $130.000 generó ARBA $2.340 e impuesto al crédito $780).
- Fila de seed `(BancoDirecto, Transferencia, null, 0, 0, 1.80, 0.60)`. El seed pasa de 18 a **19** filas.
- **`MariHogar.Domain/Helpers/PlataformasDeCobro.cs` (nuevo)** — tabla medio → plataformas permitidas como **única fuente de verdad**. La consumen la validación server-side (`CostoCobranzaService`), la configuración de tasas (`TasaCostoCobranzaService`) y las 4 pantallas, que la serializan a JS en vez de repetirla a mano. Vive en Domain porque es una regla de negocio y así la Web la lee sin inyectar un servicio para pintar un combo. Reemplaza tres listas escritas a mano que estaban en `CostoCobranzaService`, `TasaCostoCobranzaService` y el JS de Ventas.
- `ICostoCobranzaService` gana `ProcesadoresPermitidos(metodo)` y `EsProcesadorValido(metodo, procesador)`. Los 3 puntos de alta y `ActualizarProcesadorPagoAsync` validan ahora **qué** plataforma, no sólo que esté informada: antes un payload armado a mano podía guardar combinaciones que no existen (Payway + MercadoPago, o BancoDirecto en una tarjeta). `TasaCostoCobranzaService.Validar` también, así que ya no se puede configurar una tasa para una combinación inexistente.
- UI: los combos de plataforma de `Ventas/Create`, `Ventas/Details`, la edición inline de `PagosTarjeta/Index` y el formulario de tasas se acotan al medio elegido (REG-004: la regla queda en el JS **y** en el Service). Cambiar el medio de una línea descarta la plataforma si el medio nuevo no la procesa — antes sólo se limpiaba cuando el medio no llevaba plataforma, así que pasar de transferencia a tarjeta dejaba una plataforma inválida puesta y el combo vacío.

**Decisión sobre `TarjetaDebito`: NO se habilitó `BancoDirecto` ahí, en contra de la preferencia del brief.** El argumento: un cobro con tarjeta de débito pasa **siempre** por una terminal (el Point de Mercado Pago o la Payway del Banco Provincia); "sin plataforma" no es un estado posible del mundo real para ese medio. Lo que el cliente no identificó es *cuál* de las dos terminales, no *si* hubo una — y resolver esa ambigüedad es exactamente para lo que está el vendedor en la línea de pago (es el fundamento de CA-83.2, que descartó la regla automática porque ninguna acierta). Habilitarlo con una fila en 0 no evitaría un dato falso: lo volvería **indistinguible de una carga correcta**, escondiendo el arancel real (1,30% Payway / 2,88% MP) detrás de un cobro con comisión 0% que después nadie puede detectar ni corregir, porque no queda registro de que el canal era desconocido. Forzar la elección entre dos opciones reales es peor UX pero deja el dato auditable; la alternativa produce un número que parece cierto y no lo es. En `Transferencia` el caso es distinto y por eso sí se habilitó: ahí "entró directo al banco" es un tercer estado genuino, no un desconocido.

Build tras el cambio: **0 errores**. Sin migración nueva.
## Sprint CR-84 (2026-09-30) — Los pagos a proveedores descuentan de la caja del local

**Alcance de este sprint: el punto 1 del alcance de CR-84 (el mecanismo) y el punto 5 PREPARADO pero NO ejecutado.** Los puntos 2 (cuenta como atributo), 3 (saldo inicial) y 4 (conciliación por flujo) quedan fuera. Discovery en `1-analista-funcional.md`, sección "CR-84". Regla cross-proyecto: **MH-033**.

### El problema, con el número medido
`MovimientoCCLocal.OrigenTipo` admitía `"Venta"`, `"Gasto"` y `"CostoCobranza"`. Los `PagoOrdenCompra` iban únicamente a `MovimientoCCProveedor`, así que las compras pagadas bajaban la deuda con el proveedor pero **no la plata de la caja**. En producción al 30/09/2026: **$23.750.495,09** en 74 pagos ausentes del ledger de caja (cheque $10.578.712,98 · transferencia $9.797.494,07 · Mercado Pago $2.954.356,72 · efectivo $419.931,32). El saldo mostraba $16.250.558,95 cuando el real descontando las compras era **−$7.499.936,14**. El riesgo ya se había materializado: el cliente leyó esos $16,2M como plata disponible y pidió cuadrarlos contra el extracto, lo que habría significado postear un egreso de $16.201.179,73 sin causa económica.

### Escaneo de reutilización
Sin patrón propio en `cat_resumen.txt`. Se reutilizan los mismos tres que CR-83, y el código real se copió de `CostoCobranzaService` (escrito horas antes): **PAT-020** (reversión acotada al neto posteado), **PAT-012** (previsualizar → confirmar para el backfill) y el cálculo de saldo neto de `ChequeService.RevertirEstadoAsync` (CR-82). `EgresoPagoProveedorService` es estructuralmente el gemelo de `CostoCobranzaService` con otro `OrigenTipo` — misma forma de `ObtenerNetoPosteadoAsync`, `RevertirEgresoAsync`, núcleo compartido entre previsualizar y aplicar.

### Archivos y capas

**Application**
- `DTOs/EgresoPagoProveedorDtos.cs` — nuevo: `BackfillEgresoPagoProveedorLineaDto`, `...PreviewDto` (con `SaldoResultante` y `SaldoResultanteNegativo`), `...ResultDto`.
- `Interfaces/IEgresoPagoProveedorService.cs` — nuevo. Lleva en el XML doc el número medido y el **aviso de impacto** (ver abajo).
- `DTOs/CCLocalDtos.cs` — `OrdenCompraId` nullable, sólo para `OrigenTipo="PagoOC"`: ahí `OrigenId` es el Id del PAGO y no del documento, así que el Origen clickeable necesita el Id de la OC aparte.

**Infrastructure**
- `Services/EgresoPagoProveedorService.cs` — nuevo, **único punto que postea y revierte el egreso de caja de un pago a proveedor** (CRM-001). `OrigenTipo="PagoOC"` y `OrigenId = pago.Id`: el MISMO literal y el mismo OrigenId que ya usa `MovimientoCCProveedor`, así que un pago se rastrea de un ledger al otro sin traducción.
- `Services/PagoOrdenCompraService.cs` — 2 altas + el séptimo punto (ver abajo).
- `Services/ChequeService.cs` — 1 alta (`AcreditarAsync`) + 1 reversión (`RevertirEstadoAsync`).
- `Services/OrdenCompraService.cs` — 1 reversión (`CancelarAsync`). El `Cargo` de `RecibirAsync` quedó con un comentario explicando por qué **no** lleva egreso.
- `Services/CCLocalService.cs` — exclusión de documentos cancelados extendida a `PagoOC`, y resolución de la OC de cada pago para el Origen clickeable.
- `Services/CajaService.cs`, `Services/ProyeccionFinancieraService.cs` — revisados por LP-002 y documentados; sin cambio de comportamiento.
- `DependencyInjection.cs` — `IEgresoPagoProveedorService` registrado (Scoped).

**Web**
- `Controllers/RegularizacionCajaController.cs` + `Views/RegularizacionCaja/Index.cshtml` — nuevos, `[Authorize(Policy = "RequireAdministracion")]`, PAT-012. **La acción no se corrió.**
- `Views/Shared/_Layout.cshtml` — link "Regularizar caja" bajo Configuración (REG-010 verificado).
- `Views/CCLocal/Index.cshtml` — la columna Origen resuelve `PagoOC` con etiqueta "Pago a proveedor" y link a la orden de compra.

### Los 6 puntos de integración, uno por uno — y el séptimo que faltaba en el inventario

Los 6 `_ccProveedorService.RegistrarMovimientoAsync` del brief, con la decisión de cada uno:

| # | Punto | Qué lleva | Por qué |
|---|---|---|---|
| 1 | `PagoOrdenCompraService.RegistrarPagosAsync` | **Egreso** | Pago no programado: la plata sale ahora. Verificado que `esProgramado` es siempre true para Cheque (línea 116), así que un cheque NUNCA postea egreso acá — no hay doble posteo con el punto 3 |
| 2 | `PagoOrdenCompraService.ConfirmarPagoAsync` | **Egreso** | Pago programado que se confirma. Fecha = `FechaPagoTentativa`, ya pisada con la fecha real de la acción por CR-63 |
| 3 | `ChequeService.AcreditarAsync` | **Egreso** | CR-46: el cheque recién cuenta como pagado al acreditarse. Fecha = vencimiento del cheque. El guard `if (pago.Estado == Pendiente)` que ya existía impide postearlo dos veces |
| 4 | `ChequeService.RevertirEstadoAsync` | **Reversión** | CR-82. Dentro del `if (estadoAnterior == Acreditado)`: un cheque Rechazado o Pendiente nunca posteó |
| 5 | `OrdenCompraService.CancelarAsync` | **Reversión** | Fuera del `if/else` de las 3 ramas de CR-67 y sin filtrar por Estado: si el neto posteado es 0 no postea nada, así que no hace falta replicar el criterio ni se puede reversar dos veces |
| 6 | `OrdenCompraService.RecibirAsync` (`Cargo`) | **Nada** | Recibir mercadería genera una DEUDA, no una salida de dinero. Postear acá contaría la compra dos veces |

`ChequeService.RechazarAsync` **verificado en el código antes de asumirlo**: por CR-46 no postea ningún movimiento (un cheque sólo se rechaza desde Pendiente, y Pendiente nunca posteó el Pago). No lleva egreso ni reversión.

**Séptimo punto, que no estaba en el inventario de los 6 y es un hallazgo de esta corrida:** `PagoOrdenCompraService.ActualizarFechaPagoAsync` no postea nada nuevo — **corrige en el lugar la fecha del movimiento de CC Proveedor ya posteado** —, así que no aparece buscando `RegistrarMovimientoAsync`. Sin tocarlo, corregir la fecha de un pago dejaba el mismo hecho en **meses distintos en los dos ledgers**, que es exactamente la inconsistencia que CR-84 viene a cerrar. Se agregó `ActualizarFechaEgresoAsync`. Decisión: se corrige en el lugar, replicando el criterio de ese método (CR-52), en vez de reversión + alta — entre replicar una excepción consciente a la inmutabilidad del ledger y que los dos ledgers cuenten la misma corrección de forma distinta, se replica.

### AVISO DE IMPACTO — los números que el cliente ya mira van a cambiar

El día del deploy los **Egresos del período suben mucho** en la Caja y en el Dashboard, porque por primera vez incluyen la mercadería comprada. **Es la corrección pedida, no un defecto** — misma clase de cambio que R-CR80.1 (el margen del Dashboard cambió de valor al corregir el costo histórico), y hay que avisarlo de antemano para que no se lea como un error. Queda dicho en el XML doc de `IEgresoPagoProveedorService` y en el de `CajaService.ObtenerTotalesAsync`.

Ojo con el orden: para los pagos **nuevos** el efecto es inmediato al deployar; para los $23,7M históricos recién cuando el cliente corra la regularización.

### LP-002 — relevamiento por los dos lados (la lección de MH-027)

`"PagoOC"` es el segundo `OrigenTipo` nuevo del ledger de caja en el día. El relevamiento se hizo por **los dos lados**, no sólo por los lectores del discriminador:

*(a) Lugares que LEEN `OrigenTipo`:*
- `CajaService.ObtenerTotalesAsync` — **sin cambios, efecto deliberado**: los pagos entran en `EgresosPeriodo`, que es lo que pide MH-033. Documentado con el aviso de impacto.
- `CajaService.ObtenerDesgloseFacturadoAsync` — **sin cambios, invariante de MH-004 verificada**: el egreso no entra (la consulta sólo trae Ingresos) y el contramovimiento de reversión, que sí es un Ingreso, cae del lado "no facturado", que es correcto (no es un cobro a un cliente). La igualdad `facturados + noFacturados == IngresosPeriodo` se mantiene por construcción.
- `CCLocalService.ListarMovimientosAsync` — **cambiado**: la exclusión de documentos cancelados se extendió a `PagoOC`, con la MISMA subquery que ya usa `CCProveedorService.ListarAsync` para ese mismo `OrigenTipo` en el otro ledger. Sin esto, cancelar una OC ocultaba el movimiento del lado del proveedor pero dejaba el egreso y su contramovimiento visibles en la caja.
- Origen clickeable de CR-62 — **cambiado**: caso `PagoOC` con etiqueta legible y link a la OC. Ojo, acá `OrigenId` es el Id del **pago**, no del documento, a diferencia de `Venta`/`CostoCobranza`; por eso hizo falta resolver la OC aparte en el Service.
- `ProyeccionFinancieraService` — **sin cambio de comportamiento, decisión documentada**: el egreso entra en `EgresosReales` pero NO alimenta `gastoOperativoPorMes`. Las compras de mercadería no son un gasto operativo recurrente (son decisiones puntuales de reposición, de importe muy variable) y el bloque de compromisos ya las proyecta por su camino — cheques emitidos por vencimiento + pagos programados. Sumarlas al promedio proyectaría dos veces el mismo dinero, con un promedio dominado por el mes en que se compró fuerte.
- `DashboardService` — **sin cambios**: el saldo de caja sale de `ICCLocalService.ObtenerSaldoActualAsync`, que no filtra por origen, así que se actualiza solo.

*(b) Claves que el cambio podría volver ambiguas (lo que enseñó MH-027):* barrido `grep -rn "OrigenId ==" MariHogar.Infrastructure/`. Los 2 hits (`ChequeService:225`, `PagoOrdenCompraService:287`) son sobre `MovimientosCCProveedor`, no sobre el ledger de caja, y los dos ya filtran por `OrigenTipo`. En `MovimientosCCLocal` el único lookup de "buscar *la* fila" es el de `VentaService.EliminarPagoAsync`, ya acotado por `OrigenTipo == "Venta"` al corregir MH-027 esta misma jornada, así que `PagoOC` no lo alcanza. **Sin hallazgos nuevos por este lado.**

### Backfill — preparado, NO ejecutado

`RegularizacionCaja/Index`, PAT-012. La decisión de aplicarlo es del cliente y al cerrar el sprint no la había tomado.

Decisión de diseño: **la fecha y el monto del egreso no se recalculan, se leen del movimiento de CC Proveedor que acompaña a ese pago.** Es la única forma de garantizar por construcción el requisito de "misma fecha y mismo monto" sin reimplementar las cuatro reglas de fecha que ya resolvieron los puntos de alta (vencimiento del cheque, `FechaPagoTentativa`, fecha elegida de la transferencia, o `UtcNow`). Un pago sin movimiento de proveedor identificable queda fuera: no hay contra qué espejarlo, y no se le inventa una fecha (mismo criterio que CR-83 con los pagos sin plataforma).

La previsualización informa cantidad, monto, desglose por forma de pago, saldo actual y saldo resultante, y **advierte que el saldo va a quedar negativo** en un `alert-warning` que va primero en la pantalla y se repite en el SweetAlert de confirmación. El texto explica por qué: el ajuste de apertura del 10/08/2026 llevó el saldo a $0 y borró el capital de trabajo de ese día, así que el negativo es por el punto de partida y no por el negocio ni por el backfill. Se corrige con el saldo inicial (punto 3 del alcance), que no es de este sprint.

### Evidencia

`dotnet build MariHogar.slnx` → **0 errores**. **Sin migración**: `OrigenTipo` es un string y no se agregó ninguna columna. **Sin smoke test** (regla del proyecto). **No se commiteó ni deployó.**

### Pendientes para el cliente / QA

1. Avisarle al cliente, **antes del deploy**, que los Egresos de la Caja y del Dashboard van a subir: es la corrección pedida.
2. Verificar que registrar un pago a proveedor nuevo (no programado, programado+confirmado, y cheque+acreditado) deja el pago en los **dos** ledgers con la misma fecha y el mismo monto.
3. Verificar que cancelar una OC con pagos ya realizados, y revertir un cheque acreditado, devuelven el saldo de la caja al valor previo — y que hacer las dos cosas sobre el mismo pago **no** reversa dos veces.
4. Verificar que corregir la fecha de un pago con transferencia mueve el movimiento en los dos ledgers (séptimo punto).
5. Verificar que una OC cancelada deja de mostrar sus movimientos en el listado de CC Local, igual que ya pasa del lado del proveedor.
6. Correr la previsualización de Regularizar caja y contrastar contra los **$23.750.495,09** en **74 pagos** del análisis (cheque $10.578.712,98 · transferencia $9.797.494,07 · Mercado Pago $2.954.356,72 · efectivo $419.931,32). El saldo resultante esperado es **−$7.499.936,14**.
7. Verificar que correr la regularización dos veces no duplica nada.

### Correcciones del parte de QA sobre el backfill de CR-84 (2026-09-30, NO-GO → aplicado, pendiente de re-verificación)

El **punto 1 (el mecanismo) pasó con GO condicionado** y no se tocó. Los tres defectos son todos del **punto 5 (el backfill)**. Parte completo en `6-qa.md`, sección "CR-84 (2026-09-30)". Build tras las correcciones: **0 errores**. Sin migración.

**MH-035 (critical) — aplicado, pendiente de re-verificación.** `ArmarLineasBackfillAsync` no tenía piso de fecha, así que reincorporaba los 331 pagos anteriores al ajuste de apertura del 10/08/2026, cuyo neto **ya estaba** dentro de ese Egreso de $96.986.104,22. La réplica SQL de QA contra producción devolvía **404 pagos / $120.186.982,10** y habría dejado el saldo en **−$103.936.423,15** mientras la pantalla prometía −$7.499.936,14. Dos correcciones:
- `ObtenerPisoFechaAsync` **deriva** el piso del movimiento `OrigenTipo="AjusteApertura"` del propio ledger (el más reciente si hubiera varios; sin ajuste de apertura devuelve null y no filtra). Nunca hardcodeado. El piso se aplica sobre la fecha del **movimiento** — la que se usaría para postear — y no sobre `PagoOrdenCompra.Fecha`, para que el recorte coincida exactamente con lo que el ajuste absorbió.
- **`AplicarBackfillAsync` ahora llama a `PrevisualizarBackfillAsync` y postea las líneas que esa previsualización devuelve.** No es cosmético: "el número que se muestra es el que se aplica" pasa a ser verdad por construcción y no por disciplina. Compartir un método privado no alcanzaba — es lo que ya hacía, y el defecto igual ocurrió, porque el error estaba en la consulta compartida y nada ataba el número mostrado al aplicado.
- El piso se **muestra en pantalla** ("Se incorporan los pagos desde el …"): un recorte invisible no se puede contrastar contra nada.

**MH-036 (high) — aplicado, pendiente de re-verificación.** Mi decisión de espejar fecha **y monto** del movimiento de CC Proveedor fallaba justo donde ese ledger ya estaba sucio: 5 pagos con cheque (ids 339, 340, 341, 344, 345) arrastran **dos** movimientos `Pago` no-reversión cada uno, secuela del cambio de criterio de CR-46. Se habrían posteado al doble ($2.224.700,00 de exceso) con una fecha que no corresponde a ninguno de los dos. Ahora:
- el **monto sale del documento** (`pago.Monto`): el documento es la autoridad, el ledger hermano es sólo la fuente de la fecha;
- un pago con más de un movimiento no-reversión se **excluye** y se lista para revisar a mano, igual que ya se hacía con los pagos sin movimiento identificable;
- **agregado por criterio propio**: también se excluye el pago cuyo único movimiento tiene un monto distinto al del documento. Es la misma clase de suciedad y no hay forma de decidir cuál de los dos importes vale;
- la **regla de fecha determinista** queda escrita aunque sea inalcanzable por el camino de posteo (esos pagos quedan excluidos): fecha **mínima** entre los movimientos no-reversión, o sea cuando el dinero salió por primera vez. Se deja declarada para que la decisión no quede implícita si alguna vez se los habilita.

**MH-037 (medium) — aplicado como ADVERTENCIA, no como bloqueo**, de acuerdo con el veredicto de QA. La previsualización lista los lotes de carga sospechosos — varios pagos con el **mismo `CreatedAt` al microsegundo** (firma de una única sesión de carga) y fecha del pago igual al día de esa carga — con su cantidad, monto y las órdenes de compra alcanzadas, en un `alert-warning` que se repite en el SweetAlert de confirmación. En producción son **14 pagos por $6.382.868,96** sobre **13** órdenes (20, 31, 47, 48, 55, 58, 63, 65, 119, 129, 130, 131, 132). No bloquea: la fecha real es un dato de negocio que sólo el cliente puede corregir, y el sistema no puede decidir cuál era. El texto dice explícitamente por qué conviene corregirla **antes**: el backfill la congela en los dos ledgers.

**Mitigación aplicada: el link "Regularizar caja" está RETIRADO del `_Layout`.** Queda como comentario de Razor con el bloque exacto a reponer cuando QA cierre MH-035 y MH-036, y con la explicación de por qué se sacó. El controller sigue existiendo y accesible por URL directa con su policy `RequireAdministracion`, para que QA pueda re-verificar sin reponer el link.

**Hallazgo P de QA (rótulo del saldo), parcialmente atendido.** El rótulo "Saldo de la caja" de **esta pantalla** pasa a "Resultado desde la apertura", con tooltip que aclara que no es plata disponible mientras no exista el saldo inicial. Es la pantalla que va a dejar el número en un negativo grande, así que ahí el rótulo importa más. Los rótulos de `CCLocal/Index` y de la card del Dashboard **NO se tocaron**: son pantallas de uso diario del cliente y el brief acotó esta corrida al backfill.

**~~Tensión entre los dos criterios de re-verificación~~ — RESUELTA por QA en la corrida 2: no existía, ver el bloque siguiente.** Lo que sigue queda como registro de lo que creí en la corrida 1. El criterio de MH-035 pide que la consulta devuelva "la cantidad y el monto del análisis" (74 pagos / $23.750.495,09); el de MH-036 pide que **no** incluya ningún pago con `COUNT(*)>1` en el ledger proveedor. Los dos no pueden cumplirse a la vez: los 5 pagos excluidos son pagos reales que forman parte de esos $23.750.495,09. La reconstrucción correcta es **incorporados + excluidos == total del período**, y la pantalla ahora la imprime en una línea al pie ("Se incorporan N por $X, y quedan afuera M por $Y (total del período: $Z)") justamente para que el contraste sea reconstruible en vez de leerse como un faltante. Nota adicional: la propia réplica de QA contó **73** pagos post-apertura, no 74 — esa diferencia de 1 conviene resolverla del lado del análisis antes de fijar el criterio.

### Correcciones de la corrida 2 de QA sobre el backfill de CR-84 (2026-09-30, MH-035 seguía abierto → aplicado, pendiente de re-verificación)

MH-036 y MH-037 quedaron **cerrados** por QA (incluido el segundo caso de exclusión que había agregado por criterio propio: aceptado porque dispara 0 filas hoy y lista en vez de saltear en silencio). **MH-035 seguía FAIL** y ése es todo el contenido de esta corrida. Build: **0 errores**. Sin migración. Parte en `6-qa.md`, subsección "Re-verificación de los fixes del backfill (corrida 2)".

**MH-035 — el piso estaba sobre el campo equivocado. Aplicado, pendiente de re-verificación.**

Había puesto el piso sobre `mov.Fecha` — la fecha del movimiento de CC Proveedor — con el argumento de que era "la que se usaría para postear, para que el recorte coincida con lo que el ajuste absorbió". El argumento era plausible y estaba escrito en el código, y era falso: para un cheque, la fecha del movimiento de proveedor es el **vencimiento**, porque `ChequeService.AcreditarAsync` postea con `cheque.FechaVencimiento`. Ese vencimiento puede caer en cualquier momento respecto del hecho real.

El caso que lo demuestra: **pago 364, cheque #30, $495.200,00, OC 44**. Movimiento fechado 2026-08-05 (vencimiento), cheque acreditado el **22/08**, o sea doce días **después** del ajuste de apertura del 10/08, que por lo tanto no pudo absorberlo. Mi piso lo descartaba y la pantalla mostraba **73 / $23.255.295,09** contra el objetivo de CA-84.8.

El fix: **el piso y la fecha del egreso salen los dos de `PagoOrdenCompra.Fecha`**, la fecha del documento. QA probó cinco discriminadores contra producción y sólo ése reproduce **74 / $23.750.495,09**, y además reproduce el rubro **cheque $10.578.712,98** que la corrida 1 no había podido cuadrar — con eso queda cerrada esa pregunta abierta y confirmado que el objetivo del analista es correcto. (`CreatedAt` no sirve de discriminador: los 404 pagos son todos posteriores al 10/08.)

Que el **mismo campo** decida la inclusión y feche el egreso es deliberado, y es la parte que me había faltado ver: si el piso mira un campo y el posteo otro, el backfill puede dejar un egreso fechado **antes del piso que supuestamente lo contiene** — un movimiento que su propio criterio de inclusión diría que no debería existir. Es exactamente lo que habría pasado con el pago 364 al 05/08, y es el defecto secundario que QA marcó aparte.

**~~Desvío consciente del brief original~~ — NO se aceptó: era una falsa disyuntiva, ver MH-038 más abajo.** Lo que sigue queda como registro de lo que decidí en la corrida 2. Para un cheque histórico cuyo vencimiento no coincide con la fecha de pago, el egreso que postea el backfill queda con **fecha distinta** a la del movimiento de proveedor, así que la invariante "misma fecha en los dos ledgers" no se cumple para esos casos. Se privilegia la coherencia interna del backfill (un solo campo decide inclusión y fecha, y ningún egreso cae antes del piso) sobre espejar una fecha que en el ledger de origen es el vencimiento y no el hecho. **El camino en vivo no cambia**: `AcreditarAsync` sigue posteando los dos ledgers con el vencimiento, así que ahí sí coinciden — el desvío afecta sólo a los pagos que el backfill reconstruye. Queda en el XML doc del núcleo del backfill.

**La tensión que había planteado en la corrida 1 no existía.** Con el piso correcto la reconstrucción es **69 por $21.525.795,09 + 5 excluidos por $2.224.700,00 = 74 por $23.750.495,09**, y los criterios de MH-035 y MH-036 se cumplen los dos a la vez. Mi planteo salía de dar por buena mi propia elección de campo: con 73 en vez de 74, la diferencia de 1 parecía un problema del objetivo y era un problema de mi filtro.

**Dos menores del parte, también aplicados.**
- La línea de reconstrucción al pie sumaba sólo `APostear`, así que dejaba de cerrar después de una corrida parcial. Ahora suma **ya posteado + pendiente + excluido** (campo nuevo `MontoYaPosteado` en el preview), y la identidad vale en cualquier momento.
- El bloque comentado del sidebar tenía `@@(`, así que reponerlo "tal cual" emitía un `@(` literal. Corregido a `@(` — dentro de un comentario de Razor no hace falta escaparlo — y el comentario ahora lo dice, para que no se "arregle" de vuelta.

**El link del sidebar sigue retirado**, como indicó el parte: no se repone hasta que MH-035 pase la re-verificación.

### MH-038 (2026-09-30, corrida 3) — fecha efectiva de salida de dinero (aplicado, pendiente de re-verificación)

MH-035 quedó **cerrado** (verificado en SQL por QA) junto con los dos menores de la corrida 2, y QA aceptó explícitamente el razonamiento del campo único. **MH-038 era el único bloqueante** y es todo el contenido de esta corrida. Build: **0 errores**. Sin migración.

**El desvío que había declarado era una falsa disyuntiva, y eso es el aprendizaje.** Había planteado la elección como "vencimiento del cheque vs. fecha de pago", declaré que ninguna era perfecta, elegí una y documenté la pérdida con un argumento de coherencia interna que era válido. El problema es que la tercera opción — la correcta — **ya estaba guardada en la base**: `Cheque.FechaAcreditacion`, que es cuando el banco cobró el cheque y la plata salió. Documentar una pérdida con un buen argumento no reemplaza buscar si la pérdida era evitable.

Lo que midió QA sobre los 24 cheques que el backfill incorpora, con la acreditación como patrón: `PagoOrdenCompra.Fecha` (la que había elegido) se desviaba **10,75 días promedio, máximo 32**; `cheque.FechaVencimiento` (la que había reemplazado) **2,38**. Cambié un error de 2,4 días por uno de 10,75. Y el efecto material: **9 pagos por $3.197.940,56 — el 13% del backfill —** quedaban imputados a un **mes distinto** que el ledger hermano, lo que inutiliza justamente la conciliación por flujo mensual del punto 4 del alcance.

**El fix.** Se introduce `FechaEfectivaSalida(fechaDocumento, fechaPagoTentativa, fechaAcreditacionCheque)`, que reconstruye por tipo de pago el evento que efectivamente movió el dinero — el mismo que cada punto de alta del camino en vivo usa para fechar su movimiento. **El razonamiento del campo único se mantiene**: ese valor decide la inclusión (piso) y fecha el egreso, así que un egreso anterior al piso sigue siendo imposible por construcción. Sólo cambió de dónde sale el valor:
1. **Cheque acreditado → `Cheque.FechaAcreditacion`.** Un cheque sale de la caja cuando el banco lo cobra.
2. **Pago programado y confirmado → `PagoOrdenCompra.FechaPagoTentativa`.** `ConfirmarPagoAsync` la pisa con la fecha real de la confirmación (CR-63) antes de postear el movimiento de proveedor con ella, mientras `PagoOrdenCompra.Fecha` quedó en el momento de la CARGA. **Este es el caso de los 2 pagos que QA encontró fuera del universo cheque** — 1 en efectivo ($72.604,56, 27 días) y 1 por transferencia ($396.195,84, 5 días) — y con esta regla los dos vuelven a coincidir con el ledger hermano. Fue lo que me pidieron decidir con el código a la vista, y la respuesta estaba en el propio mecanismo: esos pagos son programados, y el campo que guarda cuándo se confirmaron ya existía.
3. **El resto → `PagoOrdenCompra.Fecha`.** Un pago no programado se paga cuando se carga, ahí la fecha del documento **es** la del hecho.

Detalle de implementación: las acreditaciones se traen en **consulta aparte con `IgnoreQueryFilters`**, no como navegación `p.Cheque.*` en la proyección. `Cheque` hereda `SoftDestroyable`, así que tocar la navegación habría convertido la consulta en un INNER JOIN filtrado y los pagos con cheque dado de baja habrían desaparecido del backfill — es exactamente el agujero de MH-026 en `RentabilidadService`. Un cheque dado de baja que se acreditó igual movió el dinero.

### El número nuevo — medido, no estimado

Me habían advertido que el conteo de 74 podía cambiar al cruzar algún pago el piso con la fecha nueva, y que no lo forzara. **No cambió.** Verificado con una consulta **de sólo lectura** contra la base de producción (`SELECT` únicamente, sin levantar la app, replicando la lógica de `ArmarBackfillAsync` campo por campo):

| | pagos | monto |
|---|---|---|
| **Total del período** (fecha efectiva >= 10/08/2026) | **74** | **$23.750.495,09** |
| **A incorporar** | **69** | **$21.525.795,09** |
| **Excluidos** (ledger hermano sucio, MH-036) | **5** | **$2.224.700,00** |

Piso derivado: **2026-08-10**. La reconstrucción cierra: 69 + 5 = 74, y $21.525.795,09 + $2.224.700,00 = $23.750.495,09. **El objetivo de CA-84.8 se mantiene sin tocarlo.**

Desglose por método de lo que se incorpora, y los cuatro rubros reproducen el análisis: efectivo **$419.931,32** (6) · transferencia **$9.797.494,07** (27) · Mercado Pago **$2.954.356,72** (12) · cheque **$8.354.012,98** (24), que con los 5 excluidos reconstruye el **$10.578.712,98** del análisis.

**Y el criterio central de re-verificación de MH-038 se cumple:** los pagos imputados a un mes distinto que el movimiento de proveedor bajan de **9 ($3.197.940,56) a 2 ($918.799,97)**, y los 2 que quedan se explican **únicamente** por el desfasaje vencimiento-vs-acreditación del ledger hermano, que es el CR de fondo y no éste:

| Pago | Monto | Acreditado | Vencimiento (= fecha del mov. de proveedor) |
|---|---|---|---|
| 362 | $354.000,01 | 01/09/2026 | 31/08/2026 |
| 407 | $564.799,96 | 25/09/2026 | 23/10/2026 |

En los dos casos **el egreso de caja queda en el mes correcto** y es el movimiento de proveedor el que está mal fechado — el 407 es justamente el cheque que se acreditó 28 días antes de vencer y que hace que el ledger asiente en octubre plata que salió en septiembre.

**Sobre la divergencia que queda**, ahora documentada en el XML doc como síntoma y no como elección: con la fecha efectiva, el egreso de caja queda en la fecha **correcta** y el movimiento de proveedor en una **aproximada**. Eso ya no es una decisión de este backfill sino el problema de fondo del camino en vivo (`AcreditarAsync` postea con el vencimiento), falso en el **92% del monto** según la medición de QA. Tiene CR propio y no se toca acá: el camino en vivo ya está deployado. Lo que sí hace este backfill es **no propagar el error a la caja**.

~~El link "Regularizar caja" **sigue retirado** hasta que MH-038 pase la re-verificación.~~ — **repuesto** al cerrarse los cuatro defectos (ver el bloque de cierre).

### Cierre del backfill de CR-84 (2026-09-30) — GO condicionado, último pase

Los **cuatro defectos del backfill están cerrados** por QA (MH-035, MH-036, MH-037, MH-038). Este pase son tres cosas chicas. Build: **0 errores**. Sin migración. **No queda nada técnico pendiente del backfill.**

**1. CA-84.10 — el rótulo del saldo, en las dos pantallas de uso diario.** Era el riesgo más concreto que dejó QA, por encima del backfill: después de la regularización, `CCLocal/Index` y la card del Dashboard mostrarían un **negativo grande rotulado "Saldo actual"**, que es literalmente lo que originó todo este hilo — el cliente leyó $16.250.558,95 como plata disponible y pidió cuadrarlos contra el extracto, lo que habría significado postear un egreso de $16.201.179,73 sin causa económica.

Aplicado el corolario de MH-033 (**el rótulo nombra lo que el número mide**), con el mismo criterio que ya tenía la pantalla del backfill:
- `CCLocal/Index`: "Saldo actual" → **"Resultado desde la apertura"** con tooltip, más un texto chico bajo el importe ("No incluye el capital de trabajo previo al ajuste del 10/08/2026"). De paso se corrigió el subtítulo de la pantalla, que seguía diciendo "egresos (compras/gastos, **sprints futuros**)" cuando desde CR-83/CR-84 esos egresos ya existen.
- `Dashboard/Admin`: "Balance de caja" → **"Resultado desde la apertura"** con tooltip, y el texto de apoyo pasa a decir explícitamente **"No es la plata disponible"**.

**Cambio de TEXTO únicamente: ninguna suma se tocó.** El cálculo sigue siendo el mismo `ICCLocalService.ObtenerSaldoActualAsync`, y así está anotado en las dos vistas para que nadie lo lea como un cambio de lógica.

**2. Las dos observaciones de QA, declaradas en el código** (0 casos hoy las dos: es documentar la decisión, no cambiar comportamiento).

- **Asimetría del soft delete en el backfill.** Tenía razón QA en que el código no declaraba la decisión: uso `IgnoreQueryFilters` para las acreditaciones de cheque pero `p.OrdenCompra!.Estado` sigue siendo una navegación con filtro global, así que los pagos de una OC dada de baja **se caían en silencio**. Decisión tomada y escrita: **quedan afuera, a propósito**, y la asimetría es deliberada — un cheque dado de baja que **se acreditó** igual movió el dinero, así que su fecha tiene que contar; una OC dada de baja es un documento que el sistema decidió no reconocer más, y reconstruirle egresos de caja sería darle efecto contable a algo que ya no existe para Compras, CC Proveedor ni Rentabilidad. Si esos pagos tuvieran que entrar, el problema no es del backfill: es que la OC no debería estar dada de baja.
- **Riesgo latente en `ActualizarFechaPagoTransferenciaAsync`.** Corrige `pago.Fecha` y los dos ledgers pero **no** `FechaPagoTentativa`, que es el campo que `FechaEfectivaSalida` **prefiere** para un pago programado y confirmado. Comentario puesto en ese método, con por qué hoy no dispara y qué hay que decidir si se amplía el alcance de cualquiera de los dos lados: o se corrige también `FechaPagoTentativa` ahí, o `FechaEfectivaSalida` deja de preferirla. Lo que no puede quedar es implícito.

**3. Link "Regularizar caja" repuesto** en el sidebar, con la autorización de QA. El comentario explica que estuvo retirado mientras los defectos estaban abiertos y por qué (la pantalla prometía un número distinto del que aplicaba, sobre un ledger inmutable), así que la decisión queda trazable y no parece un link que apareció sin motivo. REG-010 verificado.

### Lo que queda, y no es técnico

Tres datos del cliente y una decisión, todos fuera del código:
1. La terminal (Mercado Pago o Payway) del pago de débito de $239.000.
2. Las fechas reales de los lotes de carga retroactiva que la previsualización advierte.
3. El conteo de la plata para el saldo inicial (punto 3 del alcance de CR-84), que es lo que convierte este número en tesorería real y lo que hace que hoy dé negativo.
4. La decisión pendiente sobre el pago 441.

Y un CR propio ya identificado: el camino en vivo postea el movimiento de CC Proveedor de un cheque con `cheque.FechaVencimiento`, supuesto falso en el **92% del monto** (27 de 29 cheques acreditados, $9.745.379,65; 3 cruzan de mes; el pago 407 se acreditó 28 días antes de vencer). Afecta conciliación por fecha y `ProyeccionFinancieraService`. No entró en este sprint porque toca código ya deployado.

### Runner de regularización — `tools/RegularizarCaja` (2026-09-30)

Herramienta de **un solo uso**, mismo patrón que `tools/ImportarHistorico`: no forma parte del producto y **no está en `MariHogar.slnx`** (los 5 tools del repo tampoco), así que `dotnet build MariHogar.slnx` **no la compila**. Se compila aparte:

```
dotnet build tools/RegularizarCaja/RegularizarCaja.csproj     → 0 errores
dotnet run  --project tools/RegularizarCaja                   → dry-run (default, no escribe)
dotnet run  --project tools/RegularizarCaja -- --aplicar      → escribe
dotnet run  --project tools/RegularizarCaja -- --desde 2026-09-01 --hasta 2026-09-30
```

**Por qué un runner y no SQL.** Invoca la **lógica real** de `ICostoCobranzaService` y de `IEgresoPagoProveedorService` resueltos por el contenedor de DI de la app (`AddInfrastructure`), no instanciándolos a mano. Replicar en SQL el recálculo y el backfill sería duplicar exactamente lo que QA verificó en cuatro corridas — incluidos el piso derivado del ajuste de apertura, la fecha efectiva de salida de dinero, las dos reglas de exclusión y la idempotencia por saldo neto.

**Decisiones de diseño del runner:**
- **`--dry-run` es el default, a propósito.** Corre contra producción y escribe sobre dos ledgers inmutables: escribir tiene que pedirse explícitamente.
- **`BuildServiceProvider` y NO un `Host`.** `AddInfrastructure` registra tres `IHostedService` (acreditación de cheques, de pagos con tarjeta, vencimiento de pagos de OC) que con un Host **arrancarían en paralelo** a la corrida y podrían acreditar un cheque o emitir notificaciones en el medio de la regularización. Sin Host no se instancian nunca. Es el tipo de accidente que un runner de regularización no puede provocar, así que está comentado en el código.
- **Grafo de DI verificado**: los tres servicios que resuelve dependen sólo de `AppDbContext` + `ICCLocalService`, así que no arrastra `IWebHostEnvironment`, `AfipSettings` ni `HttpClient`.
- **Aborta sin dejar nada a medias**: si el recálculo de costo falla, no corre el backfill y devuelve exit code 1. Si falla el backfill después de que el costo sí se aplicó, lo dice explícitamente (estado consistente pero mitad hecho). Cualquier excepción aborta e imprime que lo que falló quedó revertido por su propia transacción.
- **`usuarioId = "regularizacion-2026-09-30"`** en vez de null: sin `HttpContext` no hay usuario real, y null dejaría estos movimientos indistinguibles de los automáticos (confirmación de venta, alta de gasto). Así queda rastro en `MovimientoCCLocal.UsuarioId` de que fue una corrida de regularización.
- **La verificación post-aplicación incluye re-previsualizar con la misma lógica.** Si las dos operaciones hicieron lo que dijeron, lo pendiente tiene que quedar en 0 — es la verificación más fuerte posible sin duplicar las consultas en SQL. Además imprime los movimientos de la CC Local agrupados por `OrigenTipo`/`Tipo`/`EsReversion` (lectura cruda, contraste independiente de lo que informaron los servicios), el saldo final, y los pendientes que no resuelve la corrida (pagos sin plataforma, sin tasa, excluidos, y pagos con costo calculado pero sin egreso — que debería ser 0).

**No lo corrí.** La corrida la hace el orquestador: dry-run, validación contra sus números y después `--aplicar`.

#### Chequeo aritmético del número esperado (sin tocar la base)

Me avisaron que, tras corregir en producción las fechas de los 15 pagos compensatorios a la fecha de su orden de compra, el backfill debería pasar de 74 / $23.750.495,09 a **59 / $16.786.267,17**, y que no forzara ese número. No lo forcé — y además **cierra exacto contra lo que QA ya había medido**, lo que se puede verificar sin correr nada:

- Los lotes de carga retroactiva que la previsualización advertía eran **13 pagos / $6.382.868,84** (15:02:43) + **2 / $581.359,08** (15:27:28) = **15 pagos / $6.964.227,92**.
- $23.750.495,09 − $6.964.227,92 = **$16.786.267,17**, y 74 − 15 = **59**. Los dos coinciden al centavo con el número esperado: **los 15 compensatorios son exactamente los dos lotes que el runner advertía**, que ahora caen por debajo del piso del ajuste de apertura.

Desglose esperado, para contrastar contra el dry-run (los 5 excluidos son cheques — 339/340/341/344/345 — y los 15 compensatorios son transferencias, así que son conjuntos disjuntos y los excluidos no cambian):

| | pagos | monto |
|---|---|---|
| Total del período | **59** | **$16.786.267,17** |
| A incorporar | **54** | **$14.561.567,17** |
| Excluidos (sin cambio) | **5** | **$2.224.700,00** |

Es aritmética sobre cifras ya medidas, no una medición propia: **el número bueno es el que imprima el dry-run.** Si no coincide con esto, hay algo que ninguno de los dos vio — y la línea de reconstrucción que el runner imprime (ya incorporado + a incorporar + afuera = total del período) es por dónde empezar a mirar.

El saldo resultante de **−$535.708,22** no lo puedo contrastar así: depende también de lo que postee el recálculo de costo de cobranza de CR-83, que corre antes en la misma corrida.

### Las dos regularizaciones corrieron en producción + tercer paso del runner (2026-09-30)

**Corrida real (la hizo el orquestador, no yo):** 23 egresos de costo de cobranza por **$1.301.077,43** y 54 pagos a proveedores por **$14.561.567,17**; saldo de la CC Local en **$387.914,35**; re-previsualización en cero. El desglose del backfill coincidió con el chequeo aritmético que había dejado anotado (54 a incorporar, 5 excluidos, 59 del período).

#### Modo `--anular-gastos-duplicados`

Tercer paso: anular los gastos de comisiones que el cliente venía cargando a mano, ahora que el costo se calcula solo. Instrucción del cliente: *"si se calcularon automáticamente, eliminar los casos que se cargaron a mano"*.

```
dotnet run --project tools/RegularizarCaja -- --anular-gastos-duplicados            (dry-run)
dotnet run --project tools/RegularizarCaja -- --anular-gastos-duplicados --aplicar
```

**12 gastos, $1.511.000,00**: 506, 507, 508, 510, 511, 513, 518, 521, 527, 529, 530, 532. Saldo esperado después: **$1.898.914,35** ($387.914,35 + $1.511.000,00).

Decisiones del modo:
- **Es un modo exclusivo**: cuando se pasa, el runner NO corre las dos regularizaciones. Este paso tiene que ejecutarse *después* de verificar que el costo automático quedó posteado, no en la misma pasada.
- **Respeta `--dry-run` por default**, igual que los otros.
- **Verificación previa COMPLETA y abort-all-or-nothing.** Antes de anular nada se chequea que los 12 existan, sean `ComisionesBancarias`, no estén anulados y tengan fecha de septiembre 2026. Si alguno falla, **no se anula ninguno**. El motivo está en el código: anular a medias dejaría el costo del período contado dos veces en una parte y una sola en la otra, y el número resultante no sería ni el viejo ni el nuevo — nadie podría saber cuál es. Es peor que no haber hecho nada.
- **`IGastoService.AnularAsync`, nunca SQL sobre `Anulado`.** `AnularAsync` marca el gasto y postea el contramovimiento de reversión en la CC Local en la misma transacción. Tocar la columna por SQL dejaría el Egreso original sin su reversión, o sea la caja descuadrada por $1.511.000 — exactamente el problema que esta regularización viene a cerrar. Anotado así en el código.
- Se anula **de a uno informando el resultado de cada uno**, y si alguno falla aborta diciendo cuántos quedaron hechos. Cada `AnularAsync` es su propia transacción, así que los anteriores quedaron bien (gasto + contramovimiento) y el que falló no dejó nada a medias; volver a correr con la misma lista es seguro porque el guard de "ya está anulado" los rechaza en la verificación previa.
- **Verificación**: saldo antes / después / diferencia contra lo anulado; conteo de contramovimientos `Gasto`/`Ingreso`/`EsReversion` **antes y después con el delta explicito** (tiene que ser +12) — y el conteo "ahora" también se imprime en el **dry-run**, para que haya contra qué comparar; y el listado de los gastos de `ComisionesBancarias` que siguen activos en septiembre.

#### El gasto 520 queda afuera, y el motivo está en el código

Subcategoría **"COMISION PERCEPCION MP"** ($50.000, 14/09/2026). Si esos $50.000 son una **percepción** de IVA o IIBB que Mercado Pago retiene, **no son comisión de cobranza**: son un pago a cuenta, y CR-83 los excluyó explícitamente del alcance ("las retenciones de IVA y Ganancias que practica la plataforma no son costo, son pagos a cuenta"). O sea que el cálculo automático **no lo reemplaza** y anularlo borraría un costo real sin contrapartida. Su descripción dice sólo "COMISION MP", así que el dato es ambiguo y la decisión es del cliente.

El comentario en el runner lo dice y cierra con **"NO agregarlo 'para completar la lista': que sean 12 y no 13 es la decisión"**, porque una lista de 12 ids con un hueco invita exactamente a eso. La verificación final del modo además imprime que se espera que el #520 quede activo, para que su presencia no se lea como una anulación que falló.

**Build:** `dotnet build tools/RegularizarCaja/RegularizarCaja.csproj` → **0 errores**. Recordatorio: `tools/` no está en `MariHogar.slnx`, así que el build de la solución no lo compila. **No lo corrí**: dry-run y aplicación las hace el orquestador.

### Auditoría de consistencia cross-pantalla (2026-09-30) — inventario completo

Pedido del cliente: *"el margen del periodo y los pagos a las compras deben ser compensados en todos los cards donde se muestra el dato, o sea estos arreglos tienen que estar replicados en todo el sistema"*. Con las tres regularizaciones ya corridas en producción (23 `CostoCobranza` por $1.301.077,43 · 54 `PagoOC` por $14.561.567,17 · 12 gastos anulados, saldo **$1.898.914,35**), los dos orígenes nuevos tienen datos reales: cualquier pantalla que los ignore o los duplique muestra un número incorrecto **en vivo**.

Build: **0 errores**. Verificado con consultas de **sólo lectura** contra producción, no sólo leyendo código.

#### Inventario — cada pantalla y cada card

| # | Pantalla / card | Fuente | Veredicto |
|---|---|---|---|
| 1 | **Dashboard · Margen del período** | `DashboardService.ObtenerMargenBrutoAsync` → `IRentabilidadService` | **FALTABA — corregido.** `MargenBrutoDto` no tenía `CostoCobranza` ni `MargenNeto`, así que el card mostraba el **bruto rotulado como "margen real del período"** mientras Rentabilidad ya mostraba los dos (CA-83.6). Dos números distintos del mismo período en dos pantallas — exactamente lo que CR-80 vino a cerrar. Ahora el valor grande es el **neto**, el bruto baja a línea de referencia diciendo sobre qué se calcula, y el color de alerta mira el neto (KOI-017). |
| 2 | **Dashboard · Resultado desde la apertura** (ex "Balance de caja") | `ICCLocalService.ObtenerSaldoActualAsync` | **Ya estaba bien.** No filtra por origen, así que incorporó los dos orígenes nuevos sin tocar nada. Rótulo ya corregido por CA-84.10. |
| 3 | **Dashboard · Compras del período** | `OrdenCompraService.ObtenerResumenFacturacionAsync` | **Bien, y deliberadamente NO lleva los egresos.** Mide compras **facturadas** (totales de OC), no plata que salió. Sumarle los pagos sería mezclar dos preguntas distintas: cuánto compré vs cuánto pagué. |
| 4 | **Dashboard · Deuda total a proveedores** | `ICCProveedorService.ObtenerSaldoTotalAsync` | **Bien, y NO debe descontar los egresos de caja.** La baja de la deuda ya la produce el `Pago` en el ledger del proveedor; descontar también el egreso de caja contaría dos veces la misma cancelación. Son dos ledgers que responden preguntas distintas. |
| 5 | **Dashboard · Gastos operativos** | `GastoService.ObtenerTotalPeriodoAsync` | **Bien, y deliberadamente sólo Gastos.** Las compras y el costo de cobranza **no** son gastos operativos; incluirlos ahí duplicaría lo que ya muestra Caja. Efecto correcto de la regularización: los 12 gastos anulados dejaron de contar. |
| 6 | **Dashboard · Cheques por vencer / Tarjetas por acreditar** | consultas de compromiso | **Bien.** Son compromisos a futuro, no movimientos de caja. Un cheque Pendiente todavía no posteó egreso (CR-84 postea al acreditar), así que no hay solape. |
| 7 | **Dashboard · Posición de IVA** (card + gráfico) | `DashboardService.ObtenerPosicionIvaAsync` | **Sin cambios — y con un hallazgo, ver abajo.** El crédito fiscal sale de `OrdenCompra.MontoIva` (transcripto de la factura real), no del ledger de caja, así que los orígenes nuevos no lo afectan ni lo duplican. |
| 8 | **Dashboard · Capital inmovilizado / Plata quieta / Stock crítico** | `IInventarioService` | **Bien, y deliberadamente ajenos.** Son valuación de stock (`PrecioCompra` × existencias). No tocan el ledger: responden "cuánta plata está quieta en mercadería", no cuánta salió. |
| 9 | **Dashboard · Todo lo comprometido** | sin número propio | **Bien por diseño.** Es sólo el acceso a Proyección financiera; el comentario del código ya decía que no se duplica el dato. |
| 10 | **Dashboard Vendedor** | `VentasHoyTotal` | **No aplica.** La única cifra es ventas del día; no muestra caja, egresos, saldo ni margen (y los endpoints financieros tienen policy de Administración, REG-010). |
| 11 | **Caja mensual** | `CajaService.ObtenerTotalesAsync` | **Ya estaba bien — se agregó el aviso.** `EgresosPeriodo` incorporó los dos orígenes sin filtrar, que es lo pedido. Pero el número **subió ~$14,5M** respecto de lo que mostraba antes, así que el subtítulo ahora dice que los egresos incluyen gastos, compras pagadas y costo de cobranza (misma clase de aviso que R-CR80.1). |
| 12 | **Caja · desglose facturado / no facturado** | `CajaService.ObtenerDesgloseFacturadoAsync` | **Bien, invariante de MH-004 revalidada.** Parte sólo de Ingresos y calcula `noFacturados = total − facturados`, así que la igualdad se mantiene por construcción. Los egresos nuevos no entran; sus contramovimientos de reversión (que sí son Ingreso) caen del lado "no facturado", que es correcto: no son cobros a un cliente. |
| 13 | **CC Local** | `CCLocalService` | **Ya corregido en CR-84.** Exclusión de documentos cancelados extendida a `PagoOC`, Origen clickeable con el caso nuevo, y rótulo del saldo bajo CA-84.10. |
| 14 | **Rentabilidad** | `IRentabilidadService` | **Ya estaba bien (CA-83.6).** Es la pantalla que ya mostraba bruto + neto; el card del Dashboard era el que estaba desalineado, no esta. |
| 15 | **Inventario** | `IInventarioService` | **Bien, y deliberadamente ajeno.** Mismo motivo que el ítem 8. |
| 16 | **Proyección financiera** | `ProyeccionFinancieraService` | **Un defecto latente encontrado y corregido — ver abajo.** El doble conteo que se temía **no existe**, y el motivo vale registrarlo. |

#### Proyección financiera — lo que se verificó y lo que se corrigió

**~~El doble conteo que se temía NO existe, y no por casualidad.~~ — REFUTADO por QA (MH-040): el solape SÍ era posible. Ver el bloque de correcciones más abajo.** `NetoProyectado` descuenta `ChequesPendientes` y `EgresosPosteadosFuturos`, y los dos conjuntos son **disjuntos por construcción**: un cheque postea su egreso de caja recién al **acreditarse**, y `ChequesPendientes` cuenta únicamente los `Pendiente`. Lo mismo con `PagosCompraProgramados`, que son pagos `Pendiente` y por lo tanto aún sin egreso. La distinción `ChequesVencimiento` vs `ChequesPendientes`, que existía por otro motivo, resultó ser exactamente la que protege de este solape. Quedó escrito en el doc-comment de `NetoProyectado`, porque hoy no estaba dicho y es lo que un lector necesita para no "arreglarlo".

**Lo que sí estaba mal: una base desalineada en el gasto operativo estimado.** `EgresoOperativoEstimado` netea el promedio de gasto operativo contra lo ya posteado del mes, y ese promedio (`gastoOperativoPorMes`) se calcula **sólo** sobre `OrigenTipo="Gasto"`. Hasta CR-84 los dos lados compartían base. Con `PagoOC` en el ledger, `EgresosPosteadosFuturos` pasa a incluir egresos de compra — un cheque acreditado cuyo vencimiento cae en el futuro, porque `AcreditarAsync` postea con `cheque.FechaVencimiento` — y netear eso contra un promedio que no los contiene **subestima el gasto operativo estimado** por el monto del cheque, haciendo desaparecer gasto proyectado que nada reemplaza.

Corregido con un campo nuevo, `EgresosGastoPosteadosFuturos`, que se netea en lugar del total; `EgresosPosteadosFuturos` sigue completo para el saldo, porque todos esos egresos son plata que va a salir.

**Verificado con datos reales, y es honesto decir que hoy da 0.** En producción no hay ningún egreso posteado con fecha futura: el único cheque acreditado con vencimiento futuro (pago 407, $564.799,96, vto 23/10/2026) tiene su egreso fechado el **25/09** porque lo posteó el backfill con la fecha de acreditación (MH-038). El defecto es **latente, no activo** — pero el camino en vivo sí produce estos casos de acá en adelante, así que se corrige ahora. Es, otra vez, el CR de fondo (vencimiento vs. acreditación) asomándose por otro lado.

**Tres comentarios obsoletos corregidos, que eran los más peligrosos del cambio.** La curva de saldo decía *"no descuenta pagos a proveedores porque la cuenta del local nunca los registro"*, y `ChequesPendientes` justificaba su existencia con el mismo argumento. **Desde CR-84 eso es falso.** El comportamiento es correcto en los dos casos, pero la justificación escrita era al revés de la realidad — justo la clase de supuesto obsoleto que lleva a alguien a "corregir" código que está bien. Reescritos con el motivo que sí vale hoy.

#### Hallazgo que NO se implementa: el IVA del costo de cobranza en la posición de IVA

El IVA sobre la comisión de la plataforma es **crédito fiscal computable**, y hoy la posición de IVA no lo incluye: su crédito sale de `OrdenCompra.MontoIva` (facturas de compra) y nada más.

Hoy el impacto es **$0 y no es una omisión**: el seed tiene `PorcentajeIva = 0` en las 19 filas porque los porcentajes disponibles son costo total con IVA incluido si lo llevan, y no hay liquidación contra la cual desglosarlo (ver el bloque del seed). O sea que `PagoVenta.CostoIva` es 0 en todos los pagos: no hay crédito fiscal que sumar.

**Si el cliente consigue una liquidación de Mercado Pago o de Payway y se cargan los porcentajes desglosados**, ese IVA empieza a existir y la posición de IVA quedaría subestimando el crédito fiscal. Es **alcance nuevo** — toca `CalcularCreditoFiscalAsync` y la definición funcional de la posición de IVA, que hoy es "base devengado por fecha de comprobante" y el costo de cobranza no tiene comprobante propio en el sistema. **Hay que presupuestarlo**: no lo implementé.

#### Rótulos bajo CA-84.10

Revisados los tres lugares que muestran el saldo: `CCLocal/Index`, la card del Dashboard y la pantalla del backfill. Ninguno dice "disponible"; los tres dicen **"Resultado desde la apertura"** con el tooltip que explica que no incluye el capital de trabajo previo al ajuste del 10/08/2026. Mientras el saldo inicial siga en 0, ese rótulo no se toca.

### Correcciones del parte de QA sobre la auditoría (2026-09-30) — MH-040 y MH-041

GO condicionado. QA confirmó con datos *Deuda a proveedores* (los 54 egresos tienen 1 a 1 su `Pago` en CC Proveedor por el mismo importe, 0 huérfanos, 0 desalineados), las otras 4 "ajenas", mi defecto propio de base desalineada y el "hoy da 0", más margen y rótulos. Build tras las correcciones: **0 errores**.

#### MH-040 — mi "disjuntos por construcción" era falso, y el contraejemplo estaba en el repo

Había concluido que `ChequesPendientes` y `EgresosPosteadosFuturos` no podían solaparse porque *"un cheque sólo postea su egreso al acreditarse, y ChequesPendientes cuenta sólo los Pendiente"*. El razonamiento es correcto para el camino de ida y **no contempla la vuelta**: `ChequeService.RevertirEstadoAsync` (CR-82, de dos commits antes) devuelve un cheque Acreditado a Pendiente, pero **no puede borrar el egreso ya posteado** — el ledger es inmutable — y su contramovimiento se fecha hoy. Resultado: el cheque vuelve a contar en `ChequesPendientes` **y** su egreso sigue imputado al mes del vencimiento, así que ese mes descuenta el doble en `NetoProyectado`.

0 casos hoy (no hay ninguna fila del ledger con fecha futura), pero el camino en vivo lo produce en cuanto alguien revierta un cheque con vencimiento a futuro — que es exactamente para lo que se hizo CR-82.

**Lo que falló en mi razonamiento, y es lo que vale registrar:** audité cómo **nace** cada dato y no cómo se **deshace**. Un ledger inmutable con reversiones no puede razonarse mirando sólo las altas: la reversión no borra la fila original, así que todo invariante del tipo "el estado del documento me dice si hay movimiento posteado" se rompe en cuanto existe un camino de vuelta. Y lo escribí como "por construcción", que es la forma más fuerte de afirmarlo — justo lo que desalienta a verificarlo.

**Fix elegido: la proyección excluye los cheques cuyo pago ya tiene egreso posteado**, leído del ledger y no del estado del documento. Descarté la otra opción (que la reversión de CR-82 postee su contramovimiento con la fecha del egreso que neutraliza) por dos motivos concretos:
1. Un contramovimiento con fecha futura entra en el ledger como **Ingreso futuro**, y el bucket de ingresos futuros de la proyección es `CobrosVentaComprometidos`: aparecería un "cobro de venta comprometido" fantasma por el monto del cheque. El neto cerraría, pero dos cards mostrarían plata que no existe.
2. Desincronizaría la fecha del contramovimiento de caja respecto del `Cargo` de reversión que CR-82 postea en el ledger del proveedor, que se fecha hoy. Volvería a abrir la discusión de MH-028 del lado contrario.

El fix no cambia ninguna escritura del ledger ni ninguna semántica de fecha: sólo cómo lee la proyección. El cheque sigue apareciendo en `ChequesVencimiento` (el informativo de "qué vence este mes", que no alimenta el saldo).

**Doc-comment reescrito.** Ahora dice que los dos conjuntos son disjuntos **por una exclusión explícita y no por construcción**, con el contraejemplo de CR-82 nombrado. La diferencia no es semántica: "por construcción" significa que no hay que mantener nada, y esto hay que mantenerlo. El único solape que sí es estructural — `PagosCompraProgramados`, que son pagos Pendientes y por definición sin egreso — queda marcado como tal, separado del otro.

#### MH-041 — el inventario estaba corto: 5 pantallas más

| # | Pantalla / card | Veredicto |
|---|---|---|
| 17 | **Dashboard · Ventas del período → facturado / no facturado** | **CORREGIDO.** Era el hallazgo más importante de los dos: este desglose se mide sobre **ventas emitidas** y el de Caja sobre **plata cobrada**. Mismo rótulo, universos distintos, y ninguno de los dos declaraba su base — así que un mismo período puede mostrar "facturado" distinto en las dos pantallas sin que ninguna esté mal, y no había forma de saberlo. Cada uno dice ahora sobre qué se calcula (KOI-017), en las dos pantallas. |
| 18 | **Recalcular costos de cobranza** (CR-83) | **Bien, ya estaba correcto.** Lee el ledger acotado a `OrigenTipo="CostoCobranza"` y por `PagoVentaId`, así que `PagoOC` no lo alcanza, y la idempotencia va por saldo neto. **Efecto correcto de la regularización a tener presente:** su aviso de doble conteo ahora lista sólo **1 gasto, el 520 por $50.000**, porque los otros 12 se anularon. Es el comportamiento buscado, no un resto. |
| 19 | **Regularizar caja** (CR-84) | **Bien.** Mismo criterio: lee `OrigenTipo="PagoOC"` acotado por `OrigenId`, y la identidad de reconstrucción que imprime es su propio control. Ya auditada en las cuatro corridas de QA del backfill. |
| 20 | **Dashboard · gráfico Posición de IVA mes por mes** | **Sin cambios, y corresponde.** Misma fuente que el card (`ObtenerSeriePosicionIvaAsync` sobre comprobantes de venta y `OrdenCompra.MontoIva`): no toca el ledger de caja, así que los orígenes nuevos no lo afectan ni lo duplican. Le aplica el mismo hallazgo del IVA de cobranza que al card, no uno propio. Su ventana es fija (12 meses) y ya está rotulada como tal. |
| 21 | **Proyección · 4 cards secundarias** (cobros comprometidos, cheques a vencer, egresos posteados futuros, saldo proyectado final) | **Sin cambios propios: quedan cubiertas por el fix de MH-040.** Las cuatro son sumas de los mismos campos por mes (`CobrosVentaComprometidos`, `ChequesPendientes`, `EgresosPosteadosFuturos`, `SaldoAcumulado`), así que arreglar el doble conteo en el cálculo las arregla a las cuatro. No tenían lógica propia que auditar — y eso es, en sí, el motivo por el que están bien. |

#### El aviso del IVA va en la pantalla de tasas, no en la de Posición de IVA

QA dictaminó que el crédito fiscal del IVA de cobranza es **alcance nuevo y no defecto** (hoy $0 verificado), y marcó algo que yo no había visto: **el gatillo no es un deploy, es una fila de configuración.** El día que alguien cargue un `PorcentajeIva` distinto de 0 en Configuración > Costos de cobranza, `PagoVenta.CostoIva` deja de ser 0 y la Posición de IVA empieza a subestimar el crédito **sin que nadie toque código**.

Por eso el aviso va en la pantalla **donde se produce el cambio** y no en la que muestra el síntoma: un `alert-warning` en Configuración > Costos de cobranza que dice que el % de IVA cargado ahí todavía no se computa como crédito fiscal, que es computable, y que hoy todas las filas están en 0 y el efecto es nulo. Es el lugar donde lo va a leer la persona que puede provocarlo, en el momento en que lo está por hacer.

El gasto **520** sigue sin resolverse y es decisión del cliente: no se tocó.
