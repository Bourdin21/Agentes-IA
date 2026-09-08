# Memoria - Disenador funcional

## Proyecto: delicias-naturales
## Ultima actualizacion: 2026-06-XX

---

# ITERACION 2: Devolucion cliente — Mejoras modulo Solicitudes de Ingreso de Stock

## Estado: EN DISEÑO — pendiente aprobacion para pasar a Arquitectura

---

## 1. Alcance funcional resumido

| # | Mejora | Prioridad |
|---|---|---|
| 1 | Modo de aplicacion de stock: PISAR o SUMAR, elegible al aprobar cada item | CRITICA |
| 2 | Admin puede hacer el flujo completo (crear con cantidades, verificar, aprobar/rechazar) | ALTA |
| 3 | Vendedor puede crear solicitudes (sin cantidades; el deposito las verifica despues) | ALTA |
| 4 | Deposito crea solicitudes directamente en estado VerificadoDeposito con cantidades | ALTA |
| 5 | Fecha de actualizacion de stock en Producto; badge desactualizado si >= 10 dias sin actualizar | ALTA |
| 6 | Tarjeta de Ingreso de Stock visible en Home para Admin y Deposito | MEDIA |

---

## 2. Flujos de pantalla acordados

### 2.1 Create — roles: Admin, Deposito, Vendedor

**Bloque informativo de contexto por rol (parte superior del form):**
- Admin: "Cargando cantidades, la solicitud quedará lista para que puedas aprobar los ítems."
- Deposito: "La solicitud quedará en Verificado Depósito para que el administrador la apruebe."
- Vendedor: "La solicitud quedará pendiente. El depósito ingresará las cantidades."

**Tabla de productos:**
- Admin y Deposito: columna Cantidad editable al crear (input numerico por producto).
- Vendedor: sin columna Cantidad (solo nombre y categoría del producto).

**Estado inicial segun rol:**
- Admin → cabecera `VerificadoDeposito`; items `VerificadoDeposito`.
- Deposito → cabecera `VerificadoDeposito`; items `VerificadoDeposito`.
- Vendedor → cabecera `Pendiente`; items `Pendiente`.

**Wireframe textual:**
```
┌─────────────────────────────────────────────────────────────┐
│  Nueva Solicitud de Ingreso de Stock                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [icono] Contexto segun rol (banner informativo)      │   │
│  └─────────────────────────────────────────────────────┘   │
│  Observacion: [________________________]                    │
│  Filtrar categoría: [select ▼]                              │
│  Productos: [select2 multiple ▼]                            │
│                                                             │
│  ┌──────────────────┬──────────────┬─────────────────┐     │
│  │ Producto         │ Categoría    │ Cantidad (*)     │     │
│  ├──────────────────┼──────────────┼─────────────────┤     │
│  │ Harina x 1kg     │ Harinas      │ [___5.00___]     │     │
│  └──────────────────┴──────────────┴─────────────────┘     │
│  (*) solo visible para Admin y Deposito                     │
│                                                             │
│  [Cancelar]                        [Crear solicitud]        │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.2 Details — modal de aprobacion de item (UX premium)

Al presionar "Aprobar" en un item `VerificadoDeposito`, se abre un modal (SweetAlert2 o Bootstrap modal custom) con:

```
┌──────────────────────────────────────────────────────────┐
│  ⚡ Confirmar aprobación de ítem                          │
│                                                          │
│  Producto:          Harina x 1kg                         │
│  Cantidad ingresada: 5.00 kg                             │
│  Stock actual:       12.00 kg                            │
│                                                          │
│  ¿Cómo deseas aplicar el stock?                          │
│                                                          │
│  ◉ Pisar stock                                           │
│    El stock quedará en: 5.00 kg                          │
│                                                          │
│  ○ Sumar al stock actual                                 │
│    El stock quedará en: 5.00 + 12.00 = 17.00 kg          │
│                                                          │
│  [Cancelar]                  [Confirmar aprobación]      │
└──────────────────────────────────────────────────────────┘
```

- Calculo del preview se actualiza en JS al cambiar el radio button.
- Default seleccionado: **Pisar** (preserva comportamiento anterior).
- El boton "Confirmar" envia via AJAX: `{ detalleId, modoStock: "pisar"|"sumar" }`.

---

### 2.3 Index — visibilidad por rol

| Rol | Ve |
|---|---|
| Admin | Todas las solicitudes (todos los usuarios) |
| Deposito | Solo sus propias solicitudes |
| Vendedor | Solo sus propias solicitudes |

---

### 2.4 Home — bloque Deposito ampliado

- Tarjeta "Ingreso de Stock" agregada al bloque Admin (ademas de su bloque propio).
- Bloque Deposito muestra la misma tarjeta con icono de almacen.
- Icono sugerido: `fas fa-warehouse`, color: `text-secondary` / `btn-outline-secondary`.

---

### 2.5 Indicador stock desactualizado en Productos

Badge visible en:
- Listado de productos (columna nueva "Estado stock").
- Detalle de solicitud (columna producto, junto al nombre).

| Condicion | Badge |
|---|---|
| `FechaActualizacionStock` es NULL | ⚠️ Desactualizado (badge warning) |
| Dias desde actualizacion >= 10 | ⚠️ Desactualizado (badge warning) |
| Dias desde actualizacion < 10 | ✅ Actualizado (badge success) |

---

## 3. ViewModels definidos

### SolicitudIngresoStockCreateViewModel (extendido)
| Campo | Tipo | Validacion |
|---|---|---|
| Observacion | string | Opcional, max 500 |
| ProductosIds | List<int> | Requerido, min 1 |
| CantidadesPorProducto | Dictionary<int, decimal?> | Requerido para todos los roles; valor > 0 por item |
| EsCreacionConCantidades | bool | Siempre true (todos los roles crean con cantidades) |

### SolicitudIngresoStockDetalleDetalleVM (extendido)
| Campo | Tipo | Uso |
|---|---|---|
| StockActual | decimal? | Pasado al modal JS para calcular preview |
| EsPendiente | bool | Control de botones (ya existe) |
| EsVerificadoDeposito | bool | Control de botones (ya existe) |

### AprobarItemRequest (nuevo DTO)
| Campo | Tipo | Validacion |
|---|---|---|
| DetalleId | int | Requerido |
| ModoStock | string | Requerido; valor "pisar" o "sumar" |

### ProductoStockViewModel (nuevo o extendido en lista Productos)
| Campo | Tipo | Uso |
|---|---|---|
| FechaActualizacionStock | DateTime? | Nueva columna en tabla |
| EstaDesactualizado | bool (calc) | `fecha == null || dias >= 10` |

---

## 4. Validaciones de UI acordadas

| Pantalla | Validacion |
|---|---|
| Create (todos los roles) | Cantidad requerida por item seleccionado; valor > 0 |
| Modal aprobacion | ModoStock requerido antes de confirmar (radio siempre tiene default) |
| Modal aprobacion | Preview de stock se recalcula en JS sin llamada al servidor |

---

## 5. Contratos funcionales para Services

### SolicitudIngresoStockService.CrearSolicitud
- Parametros: `cantidadesPorProducto: Dictionary<int, decimal?>`; `esCreacionConCantidades` ya no es necesario como parametro (siempre true).
- Todos los roles crean items con `EstadoDetalle = VerificadoDeposito` y cabecera en `VerificadoDeposito`.
- Validacion: todos los items deben tener cantidad > 0.

### SolicitudIngresoStockService.AprobarItem
- Parametros nuevos: `modoStock: string` ("pisar" o "sumar")
- Si "pisar": `producto.StockActual = detalle.Cantidad`
- Si "sumar": `producto.StockActual = (producto.StockActual ?? 0) + detalle.Cantidad`
- Siempre: `producto.FechaActualizacionStock = DateTime.Now`

### ProductoService (o logica en AprobarItem)
- `MarcarActualizacionStock(int productoId)`: centraliza la actualizacion de `FechaActualizacionStock = Now`.

---

## 6. Maquina de estados — Solicitud de Ingreso de Stock (actualizada)

| Estado origen | Evento | Estado destino | Guarda | Accion | Error esperado |
|---|---|---|---|---|---|
| (nueva) | Crear (Admin, Deposito o Vendedor) | VerificadoDeposito | Al menos 1 producto con cantidad > 0 | Registrar con cantidades en items | Cantidad faltante o <= 0 |
| VerificadoDeposito | GuardarCantidad (Deposito/Vendedor/Admin) | VerificadoDeposito (si todos) | Item en Pendiente | Item → VerificadoDeposito; si todos → cabecera VerificadoDeposito | Cantidad negativa |
| VerificadoDeposito | AprobarItem (Admin) + modoStock | sin cambio / Verificada | Item en VerificadoDeposito | Aplicar stock; actualizar FechaActualizacionStock; si todos resueltos → Verificada | ModoStock invalido |
| VerificadoDeposito | RechazarItem (Admin) | sin cambio / Verificada | Item en VerificadoDeposito | Sin cambio de stock; si todos resueltos → Verificada | — |
| Pendiente/VerificadoDeposito | Cancelar (Admin) | Cancelada | No estar en Verificada/Cancelada | Sin cambio de stock | — |
| Verificada | cualquiera | (terminal) | — | — | Estado final; no operable |

---

## 7. Impacto funcional por capa

### Presentacion
| Elemento | Cambio |
|---|---|
| `Create.cshtml` | Banner contextual por rol; columna cantidad visible para todos |
| `Details.cshtml` | Modal SweetAlert2 con selector pisar/sumar + preview JS |
| `Index.cshtml` | Filtro por usuario: Admin ve todas; Deposito y Vendedor ven solo las propias |
| `Home/Index.cshtml` | Tarjeta Ingreso de Stock en bloque Admin y Deposito |
| ViewModels | Extender Create, DetalleDetalle; agregar AprobarItemRequest |
| Productos list/view | Badge stock desactualizado |

### Negocio
| Elemento | Cambio |
|---|---|
| `SolicitudIngresoStockService.CrearSolicitud` | Aceptar cantidades y flag de rol |
| `SolicitudIngresoStockService.AprobarItem` | Recibir modoStock; aplicar pisar/sumar; actualizar fecha |

### Datos
| Elemento | Cambio |
|---|---|
| `Producto` | Nueva propiedad `FechaActualizacionStock DateTime?` |
| Migracion EF | 1 migracion: ADD COLUMN nullable en tabla `productos` |

---

## 8. Riesgos y supuestos

| # | Riesgo / Supuesto | Impacto | Mitigacion |
|---|---|---|---|
| 1 | Modo "sumar" puede producir stock incorrecto si el operador no entiende el contexto | Alto | Preview calculado en el modal antes de confirmar |
| 2 | Productos existentes tendran FechaActualizacionStock = NULL al deploar (aparecen como desactualizados) | Medio operativo | Comportamiento esperado; se resuelve al hacer la primera solicitud |
| 3 | Admin saltea la etapa de revision si crea con cantidades directamente | Intencional | Documentar como flujo abreviado valido para el admin |
| 4 | Deposito o Vendedor accede a Details de solicitudes ajenas | Medio seguridad | Filtrar por UsuarioId en Details para roles no-Admin |

---

## 9. Plan funcional por etapas (para el arquitecto)

| Etapa | Descripcion | Capas afectadas | Prerequisito |
|---|---|---|---|
| 1 | Modelo: agregar FechaActualizacionStock a Producto + migracion EF | Datos | — |
| 2 | Logica AprobarItem: recibir modoStock, aplicar pisar/sumar, actualizar fecha | Negocio + Presentacion (AJAX) | Etapa 1 |
| 3 | UX modal aprobacion: modal con selector y preview JS | Presentacion | Etapa 2 |
| 4 | Creacion con cantidades para todos los roles; banner contextual en Create | Presentacion + Negocio | — |
| 5 | Habilitar VendedorRol; filtrar Index por usuario para Deposito y Vendedor | Presentacion + Negocio | — |
| 6 | Badge stock desactualizado en Productos y Details | Presentacion | Etapa 1 |
| 7 | Home: tarjeta Ingreso de Stock en bloque Admin | Presentacion | — |

---

# ITERACION 3: Ajuste directo de un Pago

## Estado: DEPLOYADO A PRODUCCION (2026-09-07) — iteracion cerrada

## 0. Resultado del escaneo de reutilizacion cross-proyecto
- No existe en `docs/*/definiciones/{2-disenador-funcional,5-implementador}.md` de ningun otro proyecto una pantalla/flujo de "editar el monto de un pago ya cargado" — es una variante nueva, no una reutilizacion directa de pantalla.
- Principio de fondo SI reutilizado: **PAT-020** (ledger inmutable, marihogar) y su aplicacion gemela en ganaderia (`EgresoService.AnularAsync`/`FacturaService` — reversion via contramovimiento para movimientos `Acreditado`, mutacion/baja directa solo para `Pendiente`, nunca se edita ni borra una fila ya posteada). Aca no hay anulacion total sino un ajuste de monto, asi que el diseno es una variante: en vez de "reversar todo y listo", se **reversa el pago viejo (soft-delete + reversion de movimientos) y se crea uno nuevo correcto**, enlazados para trazabilidad. Se recomienda catalogar esta variante como patron nuevo (**PAT-023**, sujeto a numero real libre en `catalogo.yml`) al cerrar Implementacion, dado que es genuinamente reutilizable en cualquier proyecto del estudio con pagos/cobros editables (marihogar, la-platense, ganaderia tienen la misma superficie de riesgo).
- Decisiones de Analisis ya cerradas (ver `1-analista-funcional.md`): P1 Administrador y Vendedor (mismos roles que `RegistrarPago`/`EliminarPago` hoy); P2 se muestran ambos pagos (viejo tachado + nuevo) en el listado; P3 sin limite de tiempo para ajustar.
- **Ampliacion de alcance post-cierre (2026-09-07, mismo dia):** a pedido de Joaquin se evaluo unificar el boton ya existente "Editar fecha" (`ActualizarFechaPago`, mutacion directa sin historial) con el nuevo "Ajustar monto" en un unico boton **"Editar pago"** que permite cambiar Fecha, Monto y Metodo de pago juntos. Se pregunto explicitamente que pasa si el usuario edita SOLO la fecha (sin tocar monto/metodo): **decision de Joaquin — toda edicion, incluida la de solo fecha, pasa siempre por el mismo camino de reversion+alta con motivo obligatorio** (se descarto la alternativa de un camino liviano solo para fecha). Esto **reemplaza y elimina** `ActualizarFechaPago` como endpoint separado — un unico camino de edicion para todo el `Pago`, sin excepciones. Todo lo que sigue en este documento ya refleja esta decision ampliada.

## 1. Flujo de pantalla y navegacion
- **Ubicacion:** listado de pagos de una Venta (`Views/Ventas/Details.cshtml` / `Edit.cshtml`). Se **elimina** el boton "Editar fecha" existente (JS `editarFechaPago`) y se reemplaza por un unico boton **"Editar pago"** por fila, junto al ya existente "Eliminar".
- **Modal "Editar pago"** (mismo patron visual que el modal ya existente "Registrar Pago"):
  - Campos editables, prellenados con los valores actuales: **Fecha**, **Monto** (mascara de moneda), **Metodo de pago** (mismo combo que "Registrar Pago", incluyendo SaldoFavor).
  - Campo obligatorio: **Motivo de la edicion** (textarea corto, max 500) — siempre requerido, sin excepcion aunque el usuario solo cambie la fecha.
  - Botones: Cancelar / Confirmar edicion.
  - Validacion minima: al menos un campo debe ser distinto del valor original (si Fecha, Monto y Metodo quedan identicos, no hay nada que editar).
- Al confirmar: POST AJAX a `PagosController.EditarPago` (nombre final sujeto a Arquitectura/Implementacion; reemplaza tanto a `ActualizarFechaPago` como al `AjustarPago` propuesto originalmente), sin recargar la pagina completa; en `success`, refrescar solo la seccion de pagos de la venta (mismo patron que `eliminarPago` ya usa) y mostrar notificacion (Toastr) de exito.
- **No se permite editar un pago que ya fue reemplazado por una edicion anterior** (evitar editar un pago ya tachado/soft-deleted) — el boton "Editar" no se renderiza sobre filas de pagos ya reemplazados (solo sobre el pago vigente de la cadena).
- **Se permite editar pagos de una Venta en cualquier estado** (Ingresada, Finalizada o Facturada) — a diferencia de `CambiarEstadoIngresada` (bloqueado si hay Factura activa), editar un pago no toca `ProductosVenta` ni `Factura`, por lo que no reintroduce el problema del incidente de la venta 9444. Esta es, de hecho, la via correcta para terminar de resolver esa venta.

## 2. Validaciones de UI y mensajes
| Campo/accion | Validacion | Mensaje |
|---|---|---|
| Fecha/Monto/Metodo | Al menos uno debe diferir del valor actual | "No se modifico ningun dato del pago." |
| Monto | Si se edita, > 0 | "El monto debe ser mayor a cero." |
| Motivo | Requerido siempre, no vacio/whitespace | "El motivo de la edicion es obligatorio." |
| Boton Editar | Oculto/deshabilitado si el pago ya fue reemplazado por una edicion anterior | — (no aplica mensaje, el boton no se muestra) |
| Confirmacion | Igual que Eliminar hoy: SweetAlert2 de confirmacion antes de enviar el AJAX | "¿Confirmas editar este pago? Esta accion no se puede deshacer." |

## 3. ViewModels / contratos propuestos

### `EditarPagoRequest` (nuevo, entrada del endpoint — reemplaza `AjustarPagoRequest`)
| Campo | Tipo | Validacion |
|---|---|---|
| PagoId | int | Requerido |
| NuevaFecha | DateTime | Requerido |
| NuevoMonto | decimal | Requerido, > 0 |
| NuevoMetodoPago | MetodoPago (enum) | Requerido |
| Motivo | string | Requerido, max 500 |

### Respuesta JSON (mismo formato que `EliminarPago`/`RegistrarPago` hoy)
`{ mensaje: string, tipoMensaje: "success"|"error", pagoNuevoId?: int }`

### `Pago` (entidad existente, campos nuevos)
| Campo | Tipo | Uso |
|---|---|---|
| UsuarioId | string, nullable (FK AspNetUsers) | Quien registro/ajusto el pago. Nullable por los ~15.000+ pagos historicos sin este dato. |
| Observacion | string, nullable, max 500 | Motivo del ajuste (obligatorio solo cuando el pago se crea via `AjustarPago`; libre/nulo en un `RegistrarPago` normal). |
| PagoAnteriorId | int, nullable (self-FK a `pagos.Id`) | Si no es null, este pago **reemplaza** al pago con ese Id (fue creado por un ajuste). Permite reconstruir toda la cadena de ajustes sobre un mismo pago original si se ajusta mas de una vez. |

Con `PagoAnteriorId` en el registro NUEVO alcanza (no hace falta un campo inverso "reemplazadoPorId" en el viejo): se lo resuelve con un JOIN inverso (`Pagos.Where(p => p.PagoAnteriorId == viejoId)`).

## 4. Eventos de negocio relevantes
- **AjustarPago(pagoId, nuevoMonto, motivo, usuarioActual)** — dentro de `lock(_registrarPagoLock)` (mismo lock de `RegistrarPago`) + transaccion DB unica:
  1. Cargar el pago viejo (`Include(p => p.Venta)`); si no existe, ya esta eliminado, o ya fue reemplazado (existe un `Pago` con `PagoAnteriorId == pagoId`) → error funcional explicito, no generico.
  2. Reversar sus efectos: mismo criterio que `EliminarPago` — buscar y eliminar el `MovimientoCaja` (`OrigenMovimiento.Venta`, `OrigenId = VentaId`, `Monto = pago.Monto`, no eliminado) y los `MovimientoCuentaCorriente` con `PagoId = pago.Id` no eliminados. Esto se ejecuta **siempre**, incluso si el usuario solo cambio la Fecha (decision explicita de Joaquin: un unico camino, sin atajo liviano — ver seccion 0).
  3. Soft-delete el pago viejo (`DeletedAt`).
  4. Releer `montoRestante`/`saldoDisponible` de la Venta **despues** de la reversion del paso 2 (para que la logica de sobrepago/SaldoFavor de `RegistrarPago` evalue el estado correcto, no el de antes de la edicion).
  5. Crear el pago nuevo reusando la misma logica de alta de `RegistrarPago` (incluida la generacion de `MovimientoCaja` y, si corresponde, `MovimientoCuentaCorriente` por sobrepago/SaldoFavor) con `Monto = nuevoMonto`, `MetodoPago = nuevoMetodoPago`, `Fecha = nuevaFecha` (los tres editables, con el valor anterior como default si el usuario no los toco en el modal), `UsuarioId = usuarioActual`, `Observacion = motivo`, `PagoAnteriorId = pagoId`.
  6. Commit.
- **Caso particular Metodo = SaldoFavor:** si el metodo VIEJO era `SaldoFavor` (el pago original debito saldo del cliente), la reversion del paso 2 debe re-acreditar ese debito (ya cubierto por el criterio general "revertir todo MovimientoCuentaCorriente con `PagoId` = el viejo"). Si el metodo NUEVO es `SaldoFavor`, el alta del paso 5 debe re-validar `saldoDisponible` igual que `RegistrarPago` lo hace hoy para un alta normal — no asumir que el cambio de metodo es valido solo porque el pago viejo existia.
- No hay recalculo de `Venta.Estado` disparado por este evento (mismo criterio MH-020 punto 4: editar un pago nunca debe mutar el estado de la Venta).

## 5. Impacto por capa

### Presentacion
| Elemento | Cambio |
|---|---|
| `Views/Ventas/Details.cshtml` / `Edit.cshtml` | **Se elimina** el boton "Editar fecha" (JS `editarFechaPago`); nuevo boton unico "Editar pago" por fila vigente con modal (Fecha + Monto + Metodo + Motivo obligatorio); render de pagos reemplazados (tachado + motivo) enlazados con el pago vigente |
| JS (`ventas.js` o script inline de la vista) | Se retira el handler de `editarFechaPago`; nuevo handler unico del modal "Editar pago", envio AJAX, refresco de la seccion de pagos tras exito (mismo patron que `eliminarPago`) |
| ViewModel de pagos de la Venta | Incluir `UsuarioId`/nombre de usuario, `Observacion`, `PagoAnteriorId` (o el pago enlazado ya resuelto) para poder renderizar la cadena |

### Negocio
| Elemento | Cambio |
|---|---|
| `PagosController.EditarPago` (nuevo, `[Authorize(Roles = "Administrador,Vendedor")]`, `[HttpPost]`) — **reemplaza** `AjustarPago` (nombre de trabajo usado hasta ahora en este documento) y **elimina** `ActualizarFechaPago` | Orquesta el evento de negocio descripto en la seccion 4 (Fecha+Monto+Metodo juntos, siempre reversion+alta), dentro del lock `_registrarPagoLock` existente |
| Reutilizacion de logica | Extraer a metodo privado compartido la reversion ya escrita en `EliminarPago` (para no duplicarla) y la logica de alta ya escrita en `RegistrarPago`, de forma que `EditarPago` los invoque en secuencia dentro de la misma transaccion, en vez de reimplementarlos |

### Datos
| Elemento | Cambio |
|---|---|
| `Pago` | + `UsuarioId` (string, nullable, FK), `Observacion` (string, nullable), `PagoAnteriorId` (int, nullable, self-FK) |
| Migracion EF | 1 migracion: ADD COLUMN x3 en `pagos`, todas nullable (no rompe los pagos historicos) |

## 6. Riesgos de implementacion
| # | Riesgo | Impacto | Mitigacion |
|---|---|---|---|
| 1 | La reversion de `MovimientoCaja` en `EliminarPago` (y por herencia en `EditarPago`) busca por `VentaId + Monto` (no por FK directa a `Pago`) — si la misma venta tiene 2+ pagos con el MISMO monto exacto, podria revertir el movimiento equivocado. Riesgo preexistente en `EliminarPago`, heredado (no introducido) por esta feature, y ahora **mas frecuente** porque cualquier correccion de fecha (antes liviana, sin tocar movimientos) tambien pasa por este camino. | Medio-Alto — mas superficie de uso que en el diseño original. | Marcar para decision explicita del Arquitecto: agregar `MovimientoCaja.PagoId` (FK directa) ahora que se va a reusar la reversion en TODA edicion de pago, no solo en ajustes de monto puntuales. |
| 2 | Cadena de ediciones multiples (editar un pago que ya es resultado de una edicion anterior) — el diseño lo permite (self-FK encadenable) pero la UI debe recorrer toda la cadena, no asumir un unico predecesor. Con "toda edicion pasa por aca" (incluida fecha), esta cadena va a crecer mas seguido que si solo aplicara a cambios de monto. | Bajo si se implementa la iteracion sobre la cadena; Alto (UI rota) si se asume 1 solo nivel. | Explicitar en el contrato del ViewModel que `PagoAnteriorId` puede encadenarse N veces; QA debe probar una edicion sobre un pago ya editado, y una cadena de 3+ ediciones (ej. 2 correcciones de fecha seguidas de un cambio de monto). |
| 3 | Reusar `RegistrarPago` para el alta del pago nuevo implica heredar tambien su logica de sobrepago→credito / SaldoFavor→debito — si la edicion bajase el monto pagado por debajo de lo ya "consumido" como SaldoFavor en otro lado, o si CAMBIA el Metodo hacia o desde SaldoFavor, podria generar un movimiento de cuenta corriente inconsistente. | Medio, caso de borde poco frecuente pero ahora con mas combinaciones posibles (monto Y metodo editables). | Cubrir explicitamente en QA: editar el monto de un pago que genero un credito por sobrepago bajandolo por debajo del sobrepago original; editar el Metodo de un pago normal a SaldoFavor y viceversa. |
| 4 | Volumen de historial: al exigir reversion+alta incluso para una correccion trivial de fecha (decision explicita de Joaquin), el listado de pagos de ventas con varias correcciones de fecha va a acumular mas filas tachadas de las que acumularia con un camino liviano. | Bajo (UX), aceptado conscientemente. | Ninguna — riesgo aceptado a cambio de un unico camino de codigo mas simple y 100% auditable. |

## 7. Historias de usuario completas

**HU1** — Como Administrador o Vendedor, quiero poder corregir el monto de un pago que cargue mal, para que el saldo de la venta y de la cuenta corriente del cliente queden correctos sin tener que borrar y re-cargar el pago a mano.
- Dado un pago de $X sin movimientos de cuenta corriente asociados, al editarlo a $Y: el pago viejo queda soft-deleted, existe un pago nuevo por $Y con `PagoAnteriorId` apuntando al viejo, el `MovimientoCaja` refleja $Y (no $X ni la suma de ambos), y el total pagado de la venta pasa a incluir $Y en lugar de $X.
- Dado un pago que genero un credito en cuenta corriente por sobrepago, al editarlo a un monto menor: el credito viejo se revierte y se recalcula el nuevo credito/debito segun el monto ajustado (nunca queda el credito viejo sumado al nuevo).
- Editar un pago de una Venta en estado Facturada funciona igual que en Ingresada/Finalizada, sin tocar `ProductosVenta` ni `Factura`.

**HU2** — Como Administrador, quiero ver en el historial de pagos de una venta que un pago fue editado, con el motivo y los valores anteriores, para poder auditar correcciones hechas por cualquier usuario.
- El pago reemplazado se muestra tachado en el listado, con su motivo visible (tooltip o texto inline).
- El pago vigente indica visualmente que reemplaza a otro (badge/icono), sin necesidad de abrir un detalle aparte.
- Si un pago fue editado mas de una vez, se ve toda la cadena (no solo el ultimo salto).

**HU3** — Como Administrador o Vendedor, quiero que el sistema me impida editar un pago sin indicar un motivo, para que toda correccion quede siempre justificada.
- Intentar confirmar el modal sin motivo: error de validacion explicito en el modal, no se envia el request.
- Intentar forzar el request sin motivo (bypaseando la UI): el servidor lo rechaza igual, no persiste nada.

**HU4** — Como Administrador, quiero poder editar un pago de una venta ya Facturada, para poder resolver casos como el de la venta 9444 sin tener que reabrir la venta ni tocar la Factura.
- Editar un pago de una Venta `Facturada` no dispara ningun cambio en `Factura` ni en `ProductosVenta`, y no requiere revertir el estado de la Venta.

**HU5** — Como Administrador o Vendedor, quiero que un pago ya reemplazado por una edicion no se pueda volver a editar directamente (solo el pago vigente), para evitar cadenas inconsistentes o editar dos veces el mismo movimiento historico.
- El boton "Editar" no aparece sobre una fila de pago ya tachada/reemplazada.
- Un intento de request directo contra un `pagoId` ya reemplazado es rechazado por el servidor con error funcional explicito.

**HU6** — Como Administrador o Vendedor, quiero poder corregir solo la fecha de un pago (ej. un typo) desde el mismo boton "Editar pago", para no tener que aprender dos flujos distintos segun que campo cambio.
- Editar unicamente la Fecha (dejando Monto y Metodo identicos) exige motivo igual que cualquier otra edicion, y genera el mismo par pago-viejo-tachado/pago-nuevo-vigente — no hay un camino especial mas liviano (decision explicita: consistencia por sobre friccion minima en este caso de uso).
- El `MovimientoCaja` del pago nuevo refleja la fecha corregida.

**HU7** — Como Administrador o Vendedor, quiero poder cambiar el metodo de pago de un pago ya cargado (ej. se anoto como Efectivo y en realidad fue Transferencia), para que los reportes por metodo de pago sean correctos.
- Cambiar el Metodo hacia o desde `SaldoFavor` revalida `saldoDisponible`/genera el movimiento de cuenta corriente correspondiente igual que un alta nueva con ese metodo (no se asume valido solo porque el pago viejo ya existia).

## Historial de ajustes
- 2026-06-XX: Creacion. Diseno iteracion 2 del modulo Solicitudes de Ingreso de Stock a partir de devolucion del cliente.
- 2026-09-07: Diseno cerrado de "Ajuste directo de un Pago" (iteracion 3) — modal de ajuste sobre el listado de pagos de Venta, migracion EF (UsuarioId/Observacion/PagoAnteriorId en Pago), reversion+alta atomica reusando EliminarPago/RegistrarPago bajo el mismo lock. Mismo dia, alcance ampliado a pedido de Joaquin: el boton "Editar fecha" existente (`ActualizarFechaPago`) se unifica con el ajuste de monto en un unico boton/endpoint "Editar pago" (Fecha+Monto+Metodo), con la decision explicita de que TODA edicion (incluida solo-fecha) pasa siempre por reversion+alta con motivo obligatorio — sin camino liviano alternativo. `ActualizarFechaPago` queda reemplazado/eliminado. 7 historias de usuario (HU1-HU7). Patron nuevo candidato a catalogar (variante de PAT-020). Pendiente aprobacion para pasar a Arquitectura.
