# 2 - Dominio

Proyecto: `VirtualWallet.Domain` (`net10.0`, sin dependencias externas).

## Entidades

### `SoftDestroyable` (clase base)

Base de toda entidad de negocio borrable. Provee:

- `Id` (int, identity).
- `IsDeleted` (bool).
- `DeletedAt` (DateTime?), `DeletedBy` (string?).
- `CreatedAt`, `CreatedBy`, `UpdatedAt`, `UpdatedBy`.

Las entidades que **NO** heredan de `SoftDestroyable` son `ApplicationUser` (extiende `IdentityUser`), `AuditLog` y `Notification`.

### `ApplicationUser : IdentityUser`

Usuario del sistema. Campos extra: `NombreCompleto`, `Estado` (`EstadoUsuario`), `FechaAlta`, etc. Los blocks de Identity (`LockoutEnd`, `AccessFailedCount`) estan habilitados.

### `Cuenta : SoftDestroyable`

Cuenta financiera del usuario. Campos clave:

- `Nombre`, `Descripcion`.
- `Tipo` (efectivo, banco, tarjeta credito).
- `TipoTarjeta` (`TipoTarjeta`: Visa, Mastercard, etc; opcional, solo si es tarjeta).
- `Estado` (`EstadoCuenta`: Activa / Inactiva). Las inactivas no aparecen en alta de movimientos pero **si** deben seguir disponibles en edicion para no romper datos historicos (defecto D-08).
- `UsuarioId`.

### `Categoria : SoftDestroyable`

Agrupador raiz de movimientos.

- `Nombre`, `Descripcion`.
- `Tipo` (`TipoMovimiento`: Ingreso o Egreso) -> determina que tipo de movimientos puede asociar.
- `Clasificacion` (`ClasificacionPresupuesto`: Fijo, Variable, etc).
- `UsuarioId`.

### `SubCategoria : SoftDestroyable`

Hija opcional de `Categoria`. Hereda implicitamente el tipo del padre.

- `CategoriaId`, `Nombre`, `Descripcion`, `UsuarioId`.

### `Movimiento : SoftDestroyable`

Eje del dominio. Ingreso o egreso de dinero.

- `Monto` (decimal), `Fecha` (DateTime), `Descripcion`, `DescripcionOriginal` (max 500, viene del PDF importado).
- `Tipo` (`TipoMovimiento`).
- `Estado` (`EstadoMovimiento`: Realizado / Pendiente / Anulado).
- `CotizacionDolar`, `MontoUsd` (dolarizacion al momento del registro).
- `EsPagoTarjeta` (bool): cuando es egreso pagado a una tarjeta de credito; **debe excluirse** de aggregations de gasto y de subcategoria, pero **debe incluirse** en el calculo de deuda de tarjeta (reduce saldo).
- `CategoriaId`, `SubCategoriaId?`, `CuentaId`, `CuotaId?`, `UsuarioId`.

**Invariantes**:
- Si `Tipo == Ingreso`, `EsPagoTarjeta` debe ser `false` (normalizado en controller).
- Si `CuotaId` no es null, el movimiento es **gestionado por la cuota** y no puede editarse/eliminarse individualmente (D-03).
- `MontoUsd` y `CotizacionDolar` son consistentes (monto / cotizacion).

### `Cuota : SoftDestroyable`

Plan de financiacion en cuotas (tipico de tarjeta).

- `Descripcion`, `MontoTotal`, `CantidadCuotas`, `FechaInicio`, `UsuarioId`.
- El monto por cuota **no se persiste**: se deriva como `MontoTotal / CantidadCuotas`.
- Categoria/subcategoria/cuenta **no viven en `Cuota`**: se toman de los `Movimiento` generados
  (la vista de edicion los muestra leyendo el primer movimiento asociado).
- Genera N `Movimiento` con `Estado = Pendiente` y los marca `Realizado` mes a mes.
- Solo puede asociarse a categorias de tipo **Egreso** (D-09).

**Editabilidad (regla de negocio explicita, no omision de implementacion):**

- `Descripcion` y `FechaInicio` **son editables** en `Cuotas/Edit`. Cambiar `FechaInicio` es
  seguro: no altera la cantidad ni el monto de los movimientos mensuales ya generados; es la
  metadata con la que se calcula la fecha de fin de la cuota ("activa" en
  `DashboardController.ObtenerCuotasActivas`, "vigente" en `HomeController`).
- `MontoTotal` y `CantidadCuotas` son de **solo lectura una vez creada la cuota**. Motivo: los N
  movimientos mensuales se generan de una sola vez en el alta (`CuotasController.Create`), y
  cambiar el total o la cantidad exigiria reconciliar/regenerar esos movimientos (altas, bajas y
  reproporcion de importes, con parte de las cuotas posiblemente ya en `Realizado`). Esa
  reconciliacion **no esta implementada a proposito**. Para corregir el monto o la cantidad, el
  flujo soportado es eliminar la cuota (soft delete en cascada de sus movimientos) y volver a
  cargarla. La vista de edicion muestra esta limitacion al usuario de forma explicita.
- Esta es la **unica excepcion** admitida en el proyecto a la regla general de
  `32-estandares-qa-implementador.instructions.md` ("toda propiedad de negocio debe ser editable
  en Alta y Edicion salvo auditoria").

**Redondeo de cuotas (PAT-003):** al generar los N movimientos, las primeras N-1 cuotas llevan
`Math.Round(MontoTotal / CantidadCuotas, 2)` y la **ultima absorbe la diferencia de centavos**
(`MontoTotal - montoCuota * (N-1)`), de modo que la suma de los movimientos cierre exactamente
contra `MontoTotal`. Ej.: $100 en 3 cuotas -> 33,33 + 33,33 + 33,34.

### `PlanReserva : SoftDestroyable` (2026-09-04)

Plan de reserva de un mes: cuanta plata se decide apartar, por categoria/subcategoria, para cubrir
el gasto del mes siguiente. Medido **siempre en dolares** (`MontoUsd`): la serie en pesos esta
distorsionada por inflacion y no sirve para estimar contra la historia.

- `Anio`, `Mes` (mes objetivo), `CotizacionUsada` (oficial venta al momento de guardar), `UsuarioId`.
- Un plan por `(UsuarioId, Anio, Mes)`. El indice **no es unico** a proposito: el soft delete
  dejaria filas viejas con la misma clave y un unique rechazaria recrear el plan.

**Invariante central**: el plan **no genera movimientos, no toca saldos y no entra en ningun total
de gastos** de ninguna pantalla. Es un plan persistido y nada mas. Si generara movimientos, la
estimacion del mes siguiente (mediana de los 6 meses cerrados) estaria promediando su propia
reserva y el numero se realimentaria a si mismo.

### `PlanReservaLinea : SoftDestroyable` (2026-09-04)

Linea de un `PlanReserva`. `PlanReservaId`, `CategoriaId`, `SubCategoriaId?`, `MontoSugeridoUsd`
(lo que propuso el sistema) y `MontoReservaUsd` (lo que decidio el usuario, que es el numero que
manda). Se guardan los dos para poder distinguirlos despues.

- `SubCategoriaId == null` **NO** significa "toda la categoria": es el bucket
  **"(sin subcategoria)"** de esa categoria — el gasto real cargado sin subcategoria (14% de los
  egresos historicos). Mismo criterio que `DashboardController.ConstruirEgresosSubcategoria`.

### `AuditLog`

Registro inmutable de cambios:
- `Entity`, `EntityId`, `Action` (Create/Update/Delete), `User`, `Timestamp`, `BeforeJson`, `AfterJson`.
- Lo genera `VirtualWalletDbContext.OnBeforeSaveChanges`/`OnAfterSaveChanges`.
- El soft delete se registra como `Delete` (no `Update`).

### `Notification`

Aviso in-app para un usuario: `Title`, `Message`, `Level`, `IsRead`, `CreatedAt`, `UserId`.

## Enums (`VirtualWallet.Domain.Enums`)

- `TipoMovimiento`: `Ingreso`, `Egreso`.
- `EstadoMovimiento`: `Realizado`, `Pendiente`, `Anulado`.
- `EstadoCuenta`: `Activa`, `Inactiva`.
- `TipoTarjeta`: `Visa`, `Mastercard`, etc.
- `EstadoUsuario`: `Activo`, `Bloqueado`, etc.
- `ClasificacionPresupuesto`: `Fijo`, `Variable`, `Discrecional`.
- `NivelConfianza`: usado por categorizador automatico de importacion.

## Reglas de negocio criticas

1. **Multi-tenant**: ninguna entidad del dominio escapa al filtro `UsuarioId`. Las queries del Web siempre filtran. Excepciones admin requieren rol explicito.
2. **Tipo categoria <-> movimiento**: un movimiento `Egreso` solo puede usar categorias `Egreso`. Cuota idem (solo egreso).
3. **EsPagoTarjeta**: solo aplica a egresos. Excluido del gasto del periodo y de la curva de subcategorias del dashboard. Sumado al saldo a favor en deuda de tarjeta.
4. **Borrado fisico prohibido**: usar siempre soft delete. Antes de borrar, verificar dependencias (movimientos asociados a cuenta/categoria, etc.) y avisar (D-13).
5. **Estado pendiente**: las cuotas generan movimientos `Pendiente`. **Ningun total de dashboard
   incluye movimientos `Pendiente`**: tanto `Dashboard/ResumenGeneral` como la portada
   (`Home/Index`) calculan ingresos, egresos, comparativo mes anterior, top categorias, deuda de
   tarjeta, alertas y KPIs de proyeccion **solo sobre `Estado == Realizado`**. Los pendientes se
   muestran aparte, como proyeccion informativa (cuotas futuras + ingresos por cobrar), en la
   card "Pendientes" de `ResumenGeneral`. Criterio unico: para un mismo periodo, los numeros de
   la portada y los de `ResumenGeneral` deben coincidir.

## Impuestos y percepciones de tarjeta de credito (Argentina) — reglas de negocio

Relevado contra resumenes reales del titular (Banco Provincia Mastercard/Visa 08-2026 y Mercado
Pago 09-2026). **Distincion central: hay impuestos RECUPERABLES y otros DEFINITIVOS, y el sistema
los tiene que tratar distinto** — reservar plata para algo que te devuelven sobreestima la reserva.

### Percepcion de Ganancias / Bienes Personales (recuperable, pero NO de la misma forma en cada emisor)

`PERCEP.AFIP RG 4815 30%`, `DB.RG 5617 30%`, `Percepción ganancias RG 5617 (USD)` — 30% sobre el
consumo en moneda extranjera. Es **pago a cuenta**, no impuesto definitivo: siempre se recupera,
pero **cuando** se recupera cambia por emisor, y de eso depende si hay que reservar la plata.

**Mercado Pago — reversion total, antes de pagar. NO es desembolso.**
Si se cancela el saldo en moneda extranjera EN dolares, revierte la percepcion completa por el
monto exacto, dentro del mismo resumen, y el total a pagar ya viene neteado. Verificado
(resumen 09-2026): `Percepción ganancias RG 5617 (USD)` $250.613,14 el 12-09 ->
`Reembolso percepción ganancias RG 5617 (USD)` -$250.613,14 el 13-09, tras pagar US$ 553,78 en
dolares el 11-09 (el pago fue ANTES del cierre y la reversion salio igual). El total a pagar del
resumen ($207.965,89) no la incluye: **nunca sale de la caja, no hay que reservarla**.

**Banco Provincia Mastercard / Visa — devolucion PARCIAL mensual + tramite anual. SI es desembolso.**
(Confirmado por el titular, 2026-09-16.) La percepcion se cobra entera y se paga con el resumen.
Una **parte** vuelve automaticamente en el resumen siguiente (lineas `DEV PER RG 4815 30%`,
`DEV.IMP. RG 5617 30%`) y **el resto se recupera recien por el tramite anual de AFIP**.
Movimientos reales 2026: devoluciones de $93.453,85 (08-06), $153.740,72 (13-07), $112.024,98
(07-08) y $4.030,22 (10-08) — esta ultima calzando exacto contra el `DB.RG 5617 30%` de $4.030,22
cobrado el 30-07. Contra eso, el resumen de agosto cobro $427.402,20 solo de percepcion RG 4815.

> **Regla para la reserva: en Mastercard/Visa hay que reservar la percepcion COMPLETA.** Es plata
> que sale en el mes aunque despues vuelva en parte. En Mercado Pago no, porque se revierte antes
> de que salga. Tratar las dos igual subestima la reserva de MC/Visa.

No se puede medir hoy que proporcion vuelve automaticamente: el importer totaliza todas las lineas
de impuestos en un movimiento unico, asi que la percepcion no queda separada por mes (ver
"Consecuencias conocidas" mas abajo). Separarla es lo que permitiria calcular ese ratio real.

### Definitivos (costo real, NO se recuperan pagando en dolares)

| Concepto | Como figura | Tasa aprox. |
|---|---|---|
| IVA servicios digitales | `IVA servicios digitales RG 4240`, `PERCEPCION IVA DTO 354/18` | 21% |
| Ingresos Brutos servicios digitales | `IIBB servicios digitales`, `PERC IIBB SERV DIG BS AS`, `IIBB PERCEP-BSAS 2,00%` | 2% |
| Impuesto de sellos (provincial) | `IMPUESTO DE SELLOS`, `Impuesto al sello Buenos Aires` | sobre el resumen |

Excepcion: si el consumo es de la empresa y el titular es responsable inscripto, el **IVA puede
computarse como credito fiscal**. Caso real: US$ 542,72 de Google Cloud (gasto de Olvidata)
generaron $175.429,20 de IVA servicios digitales en el resumen de Mercado Pago 09-2026.

### Pesificacion del saldo en moneda extranjera

Los saldos por consumos en moneda extranjera **no cancelados al vencimiento se pesifican al
"dolar tarjeta", ~30% mas caro que el oficial** (dato aportado por el titular, consistente con la
percepcion del 30%). Cancelar en dolares evita el recargo **y** dispara el reembolso de la
percepcion: son la misma decision, no dos.

### Como entran hoy en los datos (y que distorsiona)

- **Percepcion cobrada**: `Tipo=Egreso`, `EsPagoTarjeta=false`, categoria `Impuestos / Obligaciones`.
  Cuenta como gasto en las medianas.
- **Devolucion**: `Tipo=Ingreso`, `EsPagoTarjeta=true`, categoria `Reintegro Tarjeta`.

**Consecuencias conocidas:**

1. **[CORREGIDO 2026-09-16]** El ingreso mediano de "Proyeccion y reserva" contaba los reintegros
   como ingreso (no excluia `EsPagoTarjeta`): daba U$D 2.597,71 en vez de U$D 2.520,21 en la
   ventana marzo-agosto 2026, inflando el margen disponible para la deuda en U$D 77,50/mes.
2. **[CORREGIDO 2026-09-16]** El importer de Mastercard **totalizaba todas las lineas de
   impuestos en un unico movimiento** (`IMPUESTO CREDITO MASTERCARD`), mezclando lo recuperable
   con lo definitivo. Ahora emite uno por concepto (el parser de Visa ya lo hacia). En
   el resumen Mastercard de 08-2026 ese movimiento fue de $456.942,46, de los cuales **$427.402,20
   (93,5%) eran percepcion RG 4815** y solo $29.540,26 impuestos definitivos. La reserva por el
   monto total **es correcta** (en MC/Visa la percepcion se desembolsa), pero mientras siga
   totalizado no se puede medir **que proporcion vuelve** automaticamente al mes siguiente ni
   proyectar el recupero. **Aplica solo a resumenes importados desde el 2026-09-16**: los
   historicos siguen totalizados, y reimportar un PDF ya cargado crea las filas nuevas por
   concepto sin borrar la totalizada vieja (la clave de dedup cambio).

### Regla para cualquier calculo de deuda o reserva

La percepcion de Ganancias **siempre se recupera**, pero eso no la vuelve gratis: lo que importa
para una reserva es **si sale de la caja en el mes**.

- **Mercado Pago**: no sale (se revierte antes de pagar) -> no se reserva.
- **Mastercard / Visa (Banco Provincia)**: sale entera -> **se reserva entera**, aunque una parte
  vuelva el mes siguiente y el resto por el tramite anual.

IVA, IIBB y sellos son costo real en los dos casos (salvo que el IVA sea credito fiscal por ser
gasto de empresa con responsable inscripto).
