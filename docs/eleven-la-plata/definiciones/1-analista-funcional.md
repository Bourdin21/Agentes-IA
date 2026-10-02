# Memoria - Analista funcional

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-10-01

## Definiciones vigentes

### Modulos/features analizados
Barrido de Discovery (2026-08-20) sobre: Alquileres (alta/edición/finalización, contadores por máquina), cambio de máquina dentro de un alquiler/contrato activo, Notificaciones ("avisos"), Incidencias, y verificación cruzada de items pendientes de sesiones anteriores (Contratos con precio en texto libre, curación de Artículos, roles/Identity).

### Reglas funcionales acordadas
- `AlquilerService.CreateAsync` valida los contadores iniciales (`ContadorBNInicial`/`ContadorColorInicial`) contra el `HistoriaContador` de la máquina elegida (contador anterior y siguiente en el tiempo) antes de dar de alta — esta es la regla de integridad vigente para el alta.
- El alquiler queda vinculado a **una sola máquina a la vez** vía `Alquiler.MaquinaId` (escalar, no histórico).

### Criterios de aceptacion vigentes

## Análisis — H1: Cambio de máquina en Alquiler/Contrato sin validar (2026-08-20)
**Aprobado por:** Joaquín (owner del proyecto) — "solucionar bug crítico, el resto depende de definiciones con el usuario". H2 (Avisos) y H3–H7 quedan explícitamente fuera de este ciclo, pendientes de definición.

**Resumen del problema:** `AlquilerService.UpdateAsync` y `ContratoService.UpdateAsync` permiten cambiar `MaquinaId` (y en Alquiler, además `ContadorBNInicial`/`ContadorColorInicial`) sin repetir la validación de consistencia contra `HistoriaContador` que sí aplica `AlquilerService.CreateAsync`. Resultado: se puede guardar un alquiler/contrato con contadores iniciales incompatibles con el historial real de la máquina (ej. menor al último contador registrado), lo que corrompe la base de cálculo de facturación por copia.

**Alcance incluido (este ciclo):**
- Reaplicar en `UpdateAsync` (Alquiler y Contrato) la misma validación de contadores que ya existe en `AlquilerService.CreateAsync` cuando `MaquinaId` cambia respecto al valor guardado.
- Si al cambiar de máquina no existe un `HistoriaContador` que cubra el nuevo `ContadorBNInicial`/`ContadorColorInicial`, crear uno (mismo criterio "Regla de Negocio Legacy" que ya usa `CreateAsync`), para no dejar el contador inicial "flotando" sin respaldo en el historial de la máquina.
- Mensaje de error claro al usuario si los contadores no son consistentes (mismo texto/formato que ya usa Create).

**Alcance excluido (fuera de este ciclo — pasa a "resto, depende de definiciones"):**
- No se crea una pantalla/acción dedicada "Cambiar Máquina" separada del Edit genérico.
- No se agrega un historial estructurado multi-máquina por alquiler (tabla nueva tipo `AlquilerMaquinaHistorial`) — la vista de detalle sigue mostrando el consumo en base a la máquina *actual* del alquiler. Si en el futuro se cambia de máquina, el consumo previo a ese cambio seguirá sin aparecer en el detalle de ese alquiler puntual (mismo comportamiento actual), pero al menos los datos que se guardan van a ser consistentes y no van a corromper la facturación de la máquina.
- No se toca Notifications/Avisos (H2) ni los items H3–H7.

**Reglas funcionales:**
1. Al guardar Edit de un Alquiler donde `MaquinaId` cambió respecto al valor original: validar `ContadorBNInicial`/`ContadorColorInicial` contra el `HistoriaContador` anterior y siguiente de la nueva máquina (idéntico criterio que Create). Si no pasa, rechazar con el mismo mensaje de error que usa Create.
2. Al guardar Edit de un Alquiler donde `MaquinaId` NO cambió: mantener el comportamiento actual (no re-pedir contadores ya validados en el alta, evitar falsos rechazos sobre datos ya consistentes).
3. **Corrección de alcance tras revisar `ContratoService`:** `Contrato` no tiene campos de contador (`ContadorBNInicial`/`ContadorColorInicial`) ni su `CreateAsync` valida nada contra `HistoriaContador` — es una entidad más simple (Fecha/Condición/Monto/Cliente/Máquina). Por lo tanto `ContratoService.UpdateAsync` es consistente con su propio Create: no hay ninguna validación que "falte reaplicar" ahí. **El bug confirmado queda acotado exclusivamente a `AlquilerService.UpdateAsync`.** Se descarta tocar `ContratoService` en este ciclo.

**Criterios de aceptación:**
- CA1: Editar un Alquiler cambiando la máquina a una con contador inicial MENOR al último `HistoriaContador` registrado de esa máquina → el sistema rechaza el guardado con mensaje de error, igual que en Create.
- CA2: Editar un Alquiler cambiando la máquina a una con contador inicial consistente → el sistema guarda correctamente y, si corresponde, crea el `HistoriaContador` inicial.
- CA3: Editar un Alquiler sin cambiar la máquina (solo otro campo, ej. Observación) → el guardado funciona igual que hoy, sin nuevas validaciones de por medio.
- CA4: Los alquileres/contratos existentes en producción no se ven afectados retroactivamente por este fix (es una validación hacia adelante, no una corrección de datos históricos).

**Impacto por capa (preliminar):** Negocio (`Eleven.Infrastructure/Services/AlquilerService.cs`, `ContratoService.cs`) — sin cambios de esquema, sin nueva migración EF esperada.

**Riesgos y supuestos:**
- Supuesto: no hay hoy en producción alquileres/contratos con contadores ya inconsistentes que esta validación bloquearía si alguien los vuelve a editar (riesgo bajo, a confirmar en QA con una consulta a la base antes de cerrar).
- Riesgo: si el equipo (técnicos) efectivamente necesita cambiar la máquina de un alquiler seguido, la validación estricta puede generar fricción — pero es la fricción correcta (evita guardar datos que rompen la facturación). Si se vuelve un problema de UX, eso alimenta la definición pendiente de una pantalla "Cambiar Máquina" dedicada (fuera de este ciclo).

### Supuestos y dependencias
- El negocio es de renta de equipos de impresión con facturación basada en contador de copias (B/N y Color) por máquina — la integridad de `HistoriaContador` es crítica para la facturación.
- Notifications/"avisos" está pensado como sistema in-app (entidad + servicio + UI ya existen desde el scaffold base), no como email/WhatsApp.

### Exclusiones confirmadas
- Este barrido es **Discovery únicamente**: no se implementó ningún fix de los detectados abajo. Quedan para pasar por Análisis → Diseño → Arquitectura → Presupuesto (gate cliente) antes de Implementación, según el flujo del orquestador.

## Hallazgos (gaps / bugs funcionales) — 2026-08-20

### 🔴 Crítico

**H1. Cambiar la máquina de un Alquiler activo no valida contadores ni deja rastro histórico.**
- `AlquilerService.UpdateAsync` (`Eleven.Infrastructure/Services/AlquilerService.cs`) reasigna `MaquinaId`, `ContadorBNInicial` y `ContadorColorInicial` sin repetir ninguna de las validaciones que sí tiene `CreateAsync` (consistencia contra `HistoriaContador` anterior/siguiente de la máquina).
- Como `Alquiler.MaquinaId` es un campo escalar (no una relación histórica tipo "máquina X hasta fecha Y, máquina Z desde fecha Y"), cambiar la máquina de un alquiler en curso **reescribe qué máquina fue ese alquiler completo**. `AlquilerService.GetDetailsAsync` arma el historial de consumo filtrando `HistoriaContador` de la máquina **actual** del alquiler — al cambiar la máquina, el consumo registrado durante el período con la máquina anterior deja de aparecer vinculado a ese alquiler.
- Mismo patrón, mismo riesgo, en `ContratoService.UpdateAsync` (`contrato.MaquinaId = dto.MaquinaId;` sin validación).
- **Impacto de negocio:** es un mecanismo plausible de discrepancias de saldo como la reportada por el cliente en la cuenta Efectivo ($612.000) — si en algún momento se cambió la máquina de un alquiler activo desde Editar, la facturación por copia de ese tramo queda huérfana.
- **No existe hoy** una operación dedicada "Cambiar máquina" (con motivo, fecha de corte, cierre de contador de la máquina saliente) — se hace, si se hace, a través del Edit genérico.

**H2. "Avisos" (Notifications) — infraestructura completa pero nunca se dispara.**
- Existen `Notification` (entidad), `NotificationService`, `NotificationsController` y el ícono/dropdown en el sidebar — pero **ningún servicio de negocio llama a `INotificationService`** (ni Alquileres, ni Contratos, ni Incidencias, ni Pedidos, ni Insumos Críticos).
- Confirmado en producción: la tabla `Notifications` tiene **0 filas históricamente** — nunca se generó un aviso, ni uno solo, desde que existe la funcionalidad.
- El cliente no recibe ningún aviso proactivo de nada (contrato por vencer, stock crítico bajo, incidencia sin resolver, pedido a proveedor pendiente de recepción, etc.) pese a que la base ya está lista para engancharse.

### 🟡 Pendiente de sesiones anteriores (sin resolver, verificar estado con el cliente)

**H3.** 3 Contratos del sistema viejo (Id 77, 78, 79) con precio en texto libre ("precio por copia de $13", etc.) — el cliente iba a cargarlos a mano en NEW. No hay forma de verificar desde el sistema si ya se hizo; recomendable preguntar.

**H4.** Lista de repuestos (`revision_repuestos_pendientes.xlsx`, entregada) con 37 códigos sin match y 11 grupos ambiguos — sin confirmación de que el cliente ya la revisó y devolvió decisiones.

**H5.** 6 cuentas de tipo test (`admin@admin.com`, `chino@chino.com`, etc.) siguen con rol `Administrador` en producción — decisión previa del cliente fue dejarlas, pero sigue siendo superficie de riesgo si esas contraseñas son débiles/conocidas.

### 🔵 Informativo — confirmar si es esperado o no

**H6.** 255 de 310 alquileres activos (sin `FechaDevolucion`) llevan más de 2 años abiertos. Puede ser normal para este modelo de negocio (alquileres de largo plazo), pero si alguno debería estar finalizado y no lo está, también corta la cadena de contadores. Vale una pasada del cliente para confirmar cuáles siguen vigentes de verdad.

**H7.** Solo 3 `Incidencias` registradas históricamente en producción — uso muy bajo del módulo. Confirmar si el flujo real del técnico pasa directo por Pedidos Técnico (sin pasar por Incidencias) o si hay fricción de UX que hace que no se cargue.

## Alcance inicial (Discovery) — incluido / no incluido
**Incluido en este barrido:** Alquileres (alta/edición/finalización/contadores), cambio de máquina en alquiler y contrato, Notificaciones, Incidencias, verificación de pendientes previos.
**No incluido (fuera de este barrido, no revisado en profundidad):** Pedidos Proveedor/Técnico más allá del fix de tabla ya aplicado, Máquinas/Repuestos más allá de lo ya trabajado, Reportes/Informes, exportaciones Excel/PDF.

## Preguntas abiertas para el cliente
1. ¿Alguna vez se cambió la máquina de un alquiler/contrato ya activo usando "Editar"? Si sí, en qué casos — ayuda a acotar el impacto real de H1 en los datos históricos.
2. ¿Qué avisos concretos quiere recibir (H2)? Ej.: contrato por vencer, stock crítico bajo, incidencia sin resolver, pedido a proveedor pendiente — para poder alcanzar/presupuestar bien.
3. Estado real de H3 (3 contratos) y H4 (repuestos pendientes) — ¿ya resueltos por su cuenta o siguen pendientes?
4. De los 255 alquileres sin fecha de devolución hace 2+ años (H6): ¿siguen vigentes o falta finalizarlos en el sistema?

## Condición de paso a Análisis
Bloqueado hasta que el cliente confirme cuáles de H1–H7 quiere llevar adelante y responda las preguntas abiertas 1–4. H1 y H2 son los únicos que ameritan pasar a Análisis por su cuenta sin depender de más info (son gaps confirmados en el código, no dudas de dato); H3–H7 dependen de la respuesta del cliente.

## Historial de ajustes
- 2026-08-20: Barrido de Discovery inicial (primera vez que este proyecto pasa por el flujo formal de agentes pese a estar registrado como "cerrado" en el índice — se corrige el estado).

---

## Discovery — Lote 2026-10-01 (5 reportes del cliente: Finanzas + Contadores)

**Origen:** reporte directo del owner tras uso en producción, 5 ítems. Captura adjunta para el ítem 5 (Alquiler #372, Ricoh aficio 7500).

### F1 — Saldo acumulado del último movimiento != saldo de la cuenta (defecto, severidad major)
**Síntoma reportado:** en el detalle de una cuenta los movimientos se agrupan por fecha, pero dentro de la misma fecha el orden es el inverso al cronológico, y entonces la fila "última" muestra un acumulado que no coincide con el saldo actual de la cuenta.

**Causa raíz confirmada en código (no es un problema de cálculo):**
- `MovimientoService.GetSaldosAcumuladosAsync` (`Eleven.Infrastructure/Services/MovimientoService.cs:461`) calcula bien: ordena `OrderBy(Fecha).ThenBy(Id)` y filtra `DeletedAt == null && !Anulado`.
- `Cuenta.Saldo` (`Eleven.Domain/Entities/Cuenta.cs:17`) suma `ImporteConSigno` sobre **exactamente el mismo conjunto**. Por lo tanto el último acumulado **sí** es igual al saldo; no hay discrepancia de números.
- El defecto está en el orden de la **grilla**: `MovimientoService.GetDataTableAsync:72-73` ordena solo `OrderBy(m => m.Fecha)` / `OrderByDescending(m => m.Fecha)`, **sin desempate por `Id`**. Con varios movimientos en la misma fecha, MySQL devuelve el empate en orden arbitrario (en la práctica ascendente por Id), así que en vista descendente la fila de arriba de ese día no es el último movimiento del día. El usuario lee un acumulado intermedio y lo compara contra el saldo total.

**Conclusión:** es un bug de presentación, de una línea. No hay dato corrupto ni saldo mal calculado. Confirmado por lectura de código, sin necesidad de tocar producción.

### F2 — "Egreso" como tipo por defecto en nuevo movimiento de cuenta propia (mejora de UX)
**Pedido:** Cuentas propias -> cuenta X -> Nuevo movimiento debe venir con `Egreso` preseleccionado (99% de los casos). Los ingresos nacen de la cuenta corriente del cliente, por otro flujo.
**Estado actual:** `MovimientosController.Create` (GET) (`Eleven.Web/Controllers/MovimientosController.cs:56`) instancia `new MovimientoCreateViewModel()` sin fijar `TipoMovimiento`, así que queda en el default del enum (`Ingreso`, valor 0).
**Alcance:** solo el alta desde cuentas propias (`Movimientos/Create`). **No** toca `CreateUnificado` (cuentas corrientes de clientes/proveedores), que tiene su propia semántica.

### F3 — Tras cargar un movimiento vuelve a la pantalla "Movimientos" genérica (defecto de navegación)
**Pedido:** que vuelva a la cuenta de donde se partió (ej. cargué un gasto en Efectivo -> volver a Efectivo).
**Estado actual:** `MovimientosController.Create` (POST) termina en `RedirectToAction(nameof(Index))` (`MovimientosController.cs:104`), que lleva al listado global de Movimientos — pantalla sin entrada por menú, que ofrece cargar movimientos obligando a elegir cuenta entre todas (propias + CC proveedores + CC clientes), que es justo la confusión reportada.
**Precedente ya existente en el propio proyecto (patrón a reutilizar, no inventar):** `MovimientosController.CreateUnificado` (POST) ya hace `RedirectToAction("Details", "Cuentas", new { id = ... })` (`MovimientosController.cs:235`). El fix es alinear `Create` con ese mismo criterio cuando el alta vino con `cuentaId`.
**Nota de alcance:** el cliente además insinúa que la pantalla `Movimientos/Index` sobra. **No se propone eliminarla en este ciclo** — es decisión funcional aparte; alcanza con dejar de aterrizar ahí.

### F4 — El número de comprobante no se muestra en ningún listado de movimientos (gap funcional)
**Pedido:** mostrar el Nro. de comprobante en todos los listados de movimientos, de todas las cuentas; especialmente útil en cuentas corrientes de clientes.
**Estado actual:** el dato existe y viaja (`Movimiento.NumeroComprobante`, está en el DTO, se carga en Create/Edit y se ve en Details). Incluso **ya hay filtro por comprobante** en `Views/Cuentas/Details.cshtml:139-140`, pero **no hay columna** en la grilla (`columns:` en `Cuentas/Details.cshtml:233`). Lo mismo en los otros listados.
**Superficie a tocar (3 vistas con grilla de movimientos):** `Views/Cuentas/Details.cshtml`, `Views/Clientes/Details.cshtml`, `Views/Movimientos/Index.cshtml`. Sin cambio de backend ni de datos — el campo ya está en el DTO.

### F5 — Contadores de máquinas en 0 cuando no corresponde (defecto, severidad major — **causa raíz NO cerrada**)
**Síntoma (captura):** Alquiler #372, máquina Ricoh aficio 7500. La Historia de Contadores tiene filas 09/04/2026 y 06/05/2026 con B/N Digital = 0, entre valores reales de ~4.018.041. Eso produce una diferencia de -4.018.041 y un "Total B/N: -230.536" sin sentido.

**Lo que se descartó (verificado, no supuesto):**
- *No* es el colapso de las 4 columnas legacy (`ContadorBNAnalogico`/`BNDigital`/`ColorAnalogico`/`ColorDigital`) a 2 que hace `ReMigrateContadoresScript.cs:33,36`. Se analizó el dump legacy `Eleven.Migration/db_a7251f_eleven.sql` (6.154 filas): solo 44 tienen `ContadorBNDigital = 0` y **las 44 tienen también `ContadorBNAnalogico = 0`**; ninguna fila pierde información por quedarse con la columna Digital. Idem Color. La migración no inventó ceros.
- El dump es del 2026-03-19, y las filas del caso son de abril y mayo de 2026 -> **no están en el dump**, se crearon después (el sistema legacy siguió operando hasta ~2026-07).

**Causas candidatas, las dos reales y vigentes en el código nuevo:**
1. **Carga manual sin validación.** `MaquinaService.CreateContadorAsync` (`Eleven.Infrastructure/Services/MaquinaService.cs:268`) inserta el contador **sin ninguna validación**: no exige > 0 ni monotonicidad contra el contador anterior/siguiente de la máquina. El ViewModel incluso lo habilita explícitamente: `HistoriaContadorFormViewModel` usa `[Range(0, int.MaxValue)]` (`Eleven.Web/Models/Maquinas/MaquinaDetailViewModels.cs:84,88`), y un campo dejado vacío bindea a 0 y se guarda en silencio. `UpdateContadorAsync` tiene el mismo hueco.
2. **Alta de alquiler con contador inicial vacío.** `AlquilerService.AgregarHistoriaContadorSiCorresponde` (`AlquilerService.cs:317-335`) inserta un `HistoriaContador` con el `ContadorBNInicial`/`ContadorColorInicial` del alquiler. Su primera cláusula (`contadorAnterior == null && contadorSiguiente == null`) inserta **sin comparar contra nada**, así que un 0 entra derecho. La regla legacy es idéntica (`Migration-Legacy/Controllers/AlquileresController.cs:142-157`), o sea que el sistema viejo generaba el mismo tipo de fila. Y ya está registrado en trazabilidad (2026-08-20) que **la mayoría de los alquileres activos tiene `ContadorBNInicial`/`Color` en 0**.

**Lo que falta para cerrar la causa raíz:** una consulta de solo lectura a producción sobre `Contadores` para (a) contar cuántas filas en 0 hay y desde cuándo, (b) cruzar su `Fecha` contra `Alquiler.Fecha` de la misma máquina — si coinciden, el origen es el alta de alquiler (candidata 2); si no, es carga manual (candidata 1). **Requiere autorización del owner** (toda consulta a producción en este proyecto la requiere). Sin ese dato no se puede decidir si además de blindar el alta hay que corregir datos históricos.

### Alcance propuesto para este ciclo
**Incluido:** F1, F2, F3, F4 (los cuatro acotados, de causa raíz confirmada y sin migración EF) + el **blindaje preventivo** de F5 (validar contadores en alta/edición manual y en alta de alquiler).
**No incluido:** la **corrección de datos históricos** de F5 (depende de la consulta a producción), y la eventual eliminación de la pantalla `Movimientos/Index` (decisión funcional del cliente, F3).

### Preguntas abiertas
1. **(F5, bloqueante para la parte de datos)** ¿Autorizás la consulta de solo lectura a producción sobre `Contadores` para dimensionar cuántas filas en 0 hay y de dónde salieron?
2. **(F5)** Una vez identificadas: ¿las filas en 0 se corrigen con el valor real (lo aporta el cliente), se borran, o se dejan y solo se blinda hacia adelante?
3. **(F5)** ¿Un contador en 0 es *siempre* inválido, o existe la máquina recién instalada que legítimamente arranca en 0? De esto depende si la validación es "debe ser > 0" o "debe ser >= al contador anterior" (esta segunda cubre los dos casos y es la recomendada).
4. **(F4)** ¿La columna de comprobante va en las 3 grillas por igual, o alcanza con cuentas propias y CC de clientes?
5. **(F3)** ¿Querés que además se saque del sistema la pantalla `Movimientos/Index`, o la dejamos accesible aunque ya no se aterrice ahí?

### Condición de paso a Análisis
F1-F4 pueden pasar a Análisis sin bloqueos (causa raíz confirmada en código). F5 pasa **solo en su parte de blindaje preventivo**; la parte de corrección de datos queda bloqueada por las preguntas 1-3.

## Análisis — Lote 2026-10-01 (F1-F5)

**Aprobado por:** Joaquín (owner), 2026-10-01. Respondió las 3 preguntas bloqueantes: (1) autoriza la consulta de solo lectura a producción; (2) la validación de contadores es **">= al contador anterior"**; (3) la columna de comprobante va en **las 3 grillas**.

### F5 — Causa raíz CERRADA con datos de producción (consulta de solo lectura, autorizada 2026-10-01)

Resultado sobre la tabla `Contadores` de producción (`db_a7251f_eleven2`):

| Medición | Valor |
|---|---|
| Filas totales | 6.280 |
| Filas con `ContadorBN = 0` (incluye borradas) | 126 |
| Filas con `ContadorBN = 0` **activas** (`DeletedAt IS NULL`) | **110** |
| De esas, con `ContadorBN = 0` **y** `ContadorColor = 0` | 117 de 126 |
| **Ceros regresivos** (existe un contador anterior > 0 en la misma máquina) | **69** |
| Máquinas afectadas | **58** |
| Ceros cuya `Fecha` coincide con la de un Alquiler de esa máquina | 15 |
| Concentración temporal (`CreatedAt`) | 2026-03: 10, **2026-04: 34, 2026-05: 21**, 2026-06: 3, 2026-07: 2 |

**Conclusión:** la causa dominante es la **carga manual del contador con los campos vacíos** (se bindean a 0 y se guardan sin validación), no el alta de alquiler — solo 15 de 110 coinciden con la fecha de un alquiler, y 117 de 126 tienen **ambos** contadores en 0, que es la firma de un formulario enviado en blanco. El pico de abril-mayo 2026 coincide con el caso de la captura.

**Caso de la captura verificado:** máquina del Alquiler #372 — filas `Id 6179` (09/04/2026) y `Id 6216` (06/05/2026), ambas con `ContadorBN = 0` y `ContadorColor = 0`, `CreatedAt` a segundos de la `Fecha` (carga manual en el momento), intercaladas después de `Id 6039` con `ContadorBN = 4.018.041`. Caso regresivo de manual, confirmado.

**Universo a corregir:** 69 filas activas regresivas (las inequívocamente inválidas). Las 41 restantes son primer contador de su máquina o sin anterior > 0 — se revisan aparte, pueden ser legítimas.

### Criterios de aceptación

**F1 — Orden de la grilla de movimientos**
- **CA-F1.1** Con dos o más movimientos en la misma fecha en una cuenta, la grilla en orden descendente muestra arriba el movimiento de `Id` más alto de ese día, y en orden ascendente el de `Id` más bajo.
- **CA-F1.2** En orden descendente, el saldo acumulado de la **primera** fila de la grilla (sin filtros aplicados) es exactamente igual al saldo de la cuenta que muestra el encabezado.
- **CA-F1.3** El cambio no altera ningún importe, saldo ni acumulado ya existente — solo el orden de presentación.

**F2 — Egreso por defecto**
- **CA-F2.1** Cuentas propias → cuenta X → Nuevo movimiento abre con **Egreso** seleccionado.
- **CA-F2.2** El usuario puede cambiarlo a Ingreso o Transferencia sin restricción; no se agrega ninguna validación nueva.
- **CA-F2.3** El alta desde cuentas corrientes (`CreateUnificado`) **no cambia** su comportamiento actual.

**F3 — Volver a la cuenta de origen**
- **CA-F3.1** Al guardar un movimiento iniciado desde una cuenta, el sistema redirige al **detalle de esa cuenta**, no al listado global de Movimientos.
- **CA-F3.2** El movimiento recién cargado se ve en la grilla de esa cuenta y el mensaje de éxito se muestra ahí.
- **CA-F3.3** Si el alta se inició sin cuenta de contexto, el comportamiento actual (ir al listado) se conserva — no se rompe esa ruta.
- **CA-F3.4** En una transferencia, se vuelve a la cuenta **origen** (desde donde se partió).

**F4 — Número de comprobante en las grillas**
- **CA-F4.1** Las 3 grillas de movimientos (cuenta propia, cuenta corriente de cliente, listado global) muestran una columna **Nro. Comprobante**.
- **CA-F4.2** Un movimiento sin comprobante muestra el guion largo (—) en gris, igual que el resto de las columnas opcionales de esas grillas.
- **CA-F4.3** El filtro por comprobante que ya existe en el detalle de cuenta sigue funcionando y queda alineado con la columna nueva (coherencia con **PAT-008**: toda columna visible tiene su filtro).

**F5 — Blindaje de contadores (hacia adelante)**
- **CA-F5.1** Al cargar un contador nuevo para una máquina, el sistema **rechaza** con mensaje claro si el valor es **menor** al último contador registrado antes de esa fecha. Igual o mayor se acepta.
- **CA-F5.2** Misma validación al **editar** un contador existente, y además contra el contador **siguiente** (no puede quedar mayor al posterior).
- **CA-F5.3** La misma regla aplica al contador inicial que se carga desde el **alta de un alquiler**.
- **CA-F5.4** Una máquina **sin** contadores previos acepta cualquier valor, 0 incluido (máquina recién instalada) — por eso la regla es ">= al anterior" y no "> 0".
- **CA-F5.5** El contador Color solo se valida en máquinas con `Color = true`, igual que la regla ya vigente en `AlquilerService`.
- **CA-F5.6** El mensaje de error nombra el valor mínimo admitido (ej. "El contador B/N debe ser mayor o igual a 4.018.041").

### Alcance incluido / no incluido

**Incluido:** F1, F2, F3, F4 y el **blindaje preventivo** de F5 (CA-F5.1 a CA-F5.6). Sin migración EF en ningún ítem.

**No incluido (explícito):**
- **Corrección de las 69 filas históricas en 0.** Es un saneamiento de datos sobre producción, con decisión de negocio pendiente (¿valor real aportado por el cliente, o baja lógica de la fila?). Se presupuesta y ejecuta aparte una vez decidido.
- Eliminar la pantalla `Movimientos/Index` (pregunta 5 del Discovery, sin respuesta — se deja accesible).
- Cualquier cambio en `CreateUnificado` más allá de no romperlo.
- Revisión de las 41 filas en 0 no regresivas.

### Reutilización detectada (escaneo instrucción 39 sección 3)
- **PAT-008** (DataTables server-side + filtro por columna visible) aplica a F4: hoy existe el filtro por comprobante **sin** la columna, que es la violación inversa del patrón.
- **marihogar CR-14** (`docs/marihogar/definiciones/3-arquitecto-mvc.md:307,315`) resolvió exactamente la clase de bug de F1: saldo acumulado con movimientos de la misma `Fecha`, con **"desempate determinístico por `Id` (orden de creación)"** registrado como mitigación de riesgo. Se reutiliza la decisión de diseño (no hay código portable: acá el cálculo ya es correcto, falta el desempate en la query de listado).
- F2, F3 y F5 se resuelven con patrones internos del propio proyecto (`CreateUnificado` para el redirect; `AlquilerService.ValidarContadoresAsync` para la validación de contadores).

**Corrección 2026-10-01 (post-QA):** CA-F3.3 queda **anulado** — describía un escenario inalcanzable (`CreateAsync` rechaza antes si la cuenta no existe, así que la rama de fallback es código muerto). La cobertura real de F3 son CA-F3.1, CA-F3.2 y CA-F3.4. Ver trazabilidad 2026-10-01.
