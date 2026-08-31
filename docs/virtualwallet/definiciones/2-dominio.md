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
