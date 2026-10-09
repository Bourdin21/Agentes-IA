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

# ITERACION 4: Agrupar por categoria en modal "Stock bajo"

## Estado: DISEÑO CERRADO

## 0. Escaneo de reutilizacion
No hay un patron de "agrupar tabla por categoria dentro de un modal" ya construido en otro proyecto del historial (los agrupamientos existentes en otros proyectos son de listados DataTables server-side, no modales client-side). Se reutiliza si: Bootstrap ya usado en toda la app (`table-warning`/`table-danger`, `input-group` de busqueda ya existente en este mismo modal).

## 1. Flujo de pantalla
- Se agrega un `<select id="filtro-categoria-stock-bajo">` junto al buscador existente, con "Todas las categorias" + una opcion por cada categoria presente en `ProductosBajoMinimo` (no el listado completo de categorias del sistema, solo las que tienen algun producto en stock bajo).
- La tabla se reemplaza por grupos: una fila de encabezado de grupo (nombre de categoria + cantidad de items de ese grupo) seguida de las filas de producto de esa categoria, en orden alfabetico de categoria y de producto dentro de cada una. Productos sin `CategoriaId` van al grupo "Sin categoria" al final.
- El buscador de texto ya existente sigue filtrando por nombre/codigo, combinado con el filtro de categoria (JS: una fila se muestra si matchea AMBOS filtros; un encabezado de grupo se oculta si su grupo quedo sin filas visibles).

## 2. Validaciones / UI
- Sin resultados (por buscador + categoria combinados): mismo mensaje "No se encontraron productos con ese criterio" ya existente.
- El contador de "N productos con stock bajo" del botón/alert y del `<h5>` del modal no cambia (sigue siendo el total sin filtrar).

## 3. Contrato de datos (Controller -> Vista)
- `ProductosController.Index`: agregar `.Include(p => p.Categoria)` a la query de `productosBajoMinimo` (hoy no lo tiene — gap encontrado en Analisis; sin esto, agrupar por `p.Categoria.Nombre` dispara lazy-load por fila o revienta si el proxy no esta disponible fuera de contexto).
- Vista: agrupar en el propio `.cshtml` con LINQ (`productosBajoMinimo.GroupBy(p => p.Categoria?.Nombre ?? "Sin categoria").OrderBy(g => g.Key)`), no requiere ViewModel nuevo ni cambios de ruta.

## 4. Impacto por capa
- Presentacion unicamente: `Views/Productos/Index.cshtml` (agrupado + select) y `Controllers/ProductosController.cs` (agregar el Include faltante). Sin cambios de Negocio ni Datos, sin migracion.

## 5. Riesgos
- Bajo. Unico cuidado: el JS de filtrado debe recorrer TR de encabezado de grupo y TR de producto por separado (son elementos distintos), y ocultar el encabezado cuando las 0 filas de su grupo quedan visibles — de lo contrario quedan encabezados de categoria "vacios" flotando tras filtrar.

## 6. Historias de usuario
**HU1** — Como usuario que abre el modal de stock bajo, quiero ver los productos agrupados por categoria, para ubicar mas rapido lo que me interesa sin escanear una lista plana larga.
- Cada grupo muestra su nombre de categoria y cantidad de items: los productos aparecen ordenados alfabeticamente dentro de su grupo, los grupos ordenados alfabeticamente entre si, "Sin categoria" al final.

**HU2** — Como usuario, quiero poder filtrar el modal a una sola categoria, para revisar el stock bajo de un rubro puntual.
- Elegir una categoria del select deja visibles solo sus productos (y su encabezado); el resto de los grupos se ocultan.

**HU3** — Como usuario, quiero poder combinar el buscador de texto con el filtro de categoria, para acotar aun mas la busqueda.
- Escribir en el buscador con una categoria seleccionada filtra dentro de esa categoria unicamente.

---

## Sesion: Frente A recortado — higiene del circuito de Pagos (A1 + A3 + A5)

## Estado: EN DISEÑO — pendiente aprobacion para pasar a Arquitectura

Origen: seccion 9 de `1-analista-funcional.md` (relevamiento del 2026-10-07). El Frente A completo tiene 5 items; **esta iteracion disena solo A1, A3 y A5**, que son los que no dependen de ninguna respuesta pendiente del cliente. A2 (cerrar el camino del borrar-y-recrear) queda fuera hasta resolver P11, y A4 (habilitar MercadoPago/Cheque) hasta P5b-d.

Objetivo medible de la iteracion: reducir las causas C1, C3 y la causa raiz #0 de la diferencia mensual. **No** construye conciliacion: eso es el Frente B.

## 0. Resultado del escaneo de reutilizacion cross-proyecto

| Fuente | Que aporta | Decision |
|---|---|---|
| **PAT-019** — autocompletar el monto con el saldo pendiente (marihogar → la-platense) | **Ya esta aplicado en este proyecto**: `Views/Ventas/Details.cshtml:382` y `Views/Ventas/Edit.cshtml:357` precargan el input con `montoRestanteVenta`. | **Reuso invertido.** El escaneo encontro que el patron ya esta — y que para los metodos bancarios **es la causa directa de C3**: el operador confirma el importe facturado que viene precargado en vez de tipear lo que el banco acredito. A3 **acota** PAT-019 a los metodos de caja en vez de volver a aplicarlo. Ver 2.2. Corresponde anotar la variante en la nota del patron al cerrar Diseño. |
| **la-platense**, leccion LP-009 (`5-implementador.md:368-374`) | Rechazar fecha futura contra la hora **de Argentina**, no contra `DateTime.UtcNow`: entre las 21:00 y la medianoche ART `UtcNow.Date` ya es el dia siguiente, y la validacion rechaza pagos legitimos del mismo dia. Les costo 6 fallas de test que parecian del codigo y eran del reloj. | **Se reusa tal cual.** A1 ancla en `DeliciasNaturales.Helper.DateTimeExtended.ToArgentinaTimeZone()`, que ya existe en este repo y ya es lo que usan `RegistrarPago` y los dos modales para el valor por defecto. |
| **vinosefue** (`2-disenador-funcional.md:72`) | "Fecha de Pago/NCR: no puede ser futura (igual criterio que otras fechas de movimiento del sistema)". | Confirma que "fecha de movimiento no futura" ya es **convencion del estudio**, no una regla nueva de este proyecto. A1 la trae a delicias-naturales. |
| **PAT-023** — editar un pago: reversion + alta enlazada (origen: este mismo proyecto) | El punto unico por donde pasan alta y edicion es `PagoService`. | Las validaciones de A1 van en `PagoService.RegistrarPagoInterno`, **no** en el Controller: asi cubren de una sola vez `RegistrarPago` y `EditarPago`, que son las dos entradas. |
| **PAT-057** — saldo inicial declarado (la-platense) | Su mitad no-codigo: *"la pantalla no llama 'saldo' al numero; el rotulo dice lo que el numero ES"*. | **Se reusa el principio, no el codigo.** Es exactamente el problema de A5: la pantalla rotula "Transferencia" un numero que el cliente lee como "lo que entro al banco". Ver 2.3. |
| Instruccion 38 (diseño de pantallas del portal) | Regla 0: lo que la persona vino a hacer entra en la primera pantalla. | Aplica **solo como principio** a la fila de totalizadores de A5. El design system Olvidata no aplica: esta pantalla es Bootstrap + FontAwesome del admin legacy, no el portal. |

Patron nuevo candidato a catalogar al cerrar Diseño: **"el importe por defecto de un pago depende del medio"** (prellenar con el saldo cuando el importe lo determina quien cobra; dejarlo vacio cuando lo determina un tercero — banco, tarjeta, billetera). Es una restriccion de PAT-019, no un patron independiente: va como nota/variante en PAT-019.

## 1. Alcance funcional resumido

**Incluido:**
- A1 — validacion de `Pago.Fecha` en servidor (3 reglas) y sus topes en los 3 formularios que la cargan.
- A3 — el importe por defecto del pago pasa a depender del metodo, y la consecuencia del importe tipeado se muestra en vivo.
- A5 — los totalizadores de la pantalla de Pagos se reagrupan en 3 grupos con rotulos que dicen que es cada numero.

**No incluido:** A2, A4, el modulo de conciliacion (Frente B), y la correccion de los datos sucios ya en produccion (3 pagos con fecha futura por $852.206,16 — es un script de datos, no codigo; se trata aparte).

**Sin migracion EF.** Las 3 historias tocan Negocio y Presentacion unicamente.

## 2. Flujos de pantalla acordados

### 2.1 A1 — Fecha del pago

Puntos de carga de `Pago.Fecha` hoy: el modal "Registrar Pago" de `Views/Ventas/Details.cshtml` (~l.377), el mismo modal duplicado en `Views/Ventas/Edit.cshtml` (~l.352), y el modal de "Editar pago" (`EditarPago`, iteracion 3). Los tres resuelven el valor por defecto con `DateTimeExtended.ToArgentinaTimeZone()`; ninguno acota el rango.

**La fecha futura NO es un error: es como se cargan los cheques.** El diseño original de esta seccion rechazaba toda fecha posterior a hoy. La medicion sobre los 14.131 pagos activos lo desmintio y obligo a partir la regla en dos:

- **242 pagos activos (1,71 %) estan fechados hacia adelante** respecto del dia en que se cargaron, por $72,4 M. **145 son `Transferencia`** ($62,7 M) — es exactamente la practica documentada en el hallazgo 2 del analisis de agosto: los cheques se anotan como Transferencia con `Fecha` = el dia en que se espera depositarlos. Es practica **vigente** (5 casos en septiembre, 21 en agosto), no un residuo historico.
- La cola legitima llega hasta **41 dias** hacia adelante y ahi se corta. Despues hay un hueco y **2 outliers a 350 y 358 dias**: son los dos pagos de diciembre 2026 cargados en enero 2026 ($163.780,83) — typos de año, los unicos de toda la base.

Esa separacion limpia (41 → hueco → 350) es la que permite fijar el tope duro sin falsos positivos.

**Servidor (fuente de verdad, en `PagoService`):**

| Regla | Condicion | Comportamiento | Casos historicos que alcanza (de 14.131 activos) | Mensaje |
|---|---|---|---|---|
| **R1a** | `fecha.Date > hoyART.AddDays(90)` | **Rechazo** (`PagoNegocioException`) | **2** (los typos de año), **0 falsos positivos** — el maximo legitimo medido es 41 dias | "La fecha del pago es de mas de 90 dias en el futuro. Revisa el año." |
| **R1b** | `fecha.Date > hoyART` (y hasta +90) | **Aviso con confirmacion** | 240 — la practica de cheques | "La fecha es posterior a hoy. Si es un cheque a depositar, confirma; si te equivocaste, corregila." |
| **R2** | `fecha.Date < venta.Fecha.Date` | **Rechazo** | **38 (0,27 %)** — margen suficiente para rechazar | "La fecha del pago no puede ser anterior a la fecha de la venta (dd/MM/yyyy)." |
| **R3** | `fecha.Date < hoyART.AddDays(-30)` | **Aviso con confirmacion** | 24 | "La fecha que pusiste es de hace mas de 30 dias. Confirmas que el pago es de esa fecha?" |

Por que cada una es rechazo o aviso, con el numero detras:
- **R1a y R2 rechazan** porque el dato muestra que ningun pago legitimo las viola (2 y 38 casos sobre 14.131, todos identificables como error).
- **R1b avisa y no rechaza** porque rechazar romperia el circuito de cheques, que es el workaround mas usado del sistema. Es la correccion mas importante de esta seccion: el diseño que rechazaba fecha futura habria bloqueado 145 pagos de Transferencia por $62,7 M de practica vigente.
- **R3 avisa** porque la carga tardia es un caso real (254 pagos a 4-7 dias, 187 a 8-15). El umbral de 30 dias deja pasar la cola normal y alcanza los 24 casos donde ya hay algo raro. Se descarto el umbral de 60 dias que proponia el borrador: alcanzaba **4 casos sobre 14.131** — una regla que no mide nada.

Los tres umbrales (90, 30, y el comparador de R2) son constantes del Service, sin campo de configuracion en pantalla — mismo criterio que P6.

**Cliente (friccion temprana, no sustituye al servidor):** `max` = hoy ART **+ 90 dias** y `min` = fecha de la venta en los tres `<input type="date">`. Los avisos de R1b y R3 viajan en la respuesta JSON con `tipoMensaje = "confirmar"` y se muestran re-enviando el formulario con `confirmaFecha = true`.

**Libreria de dialogos — verificado, no asumido:** el proyecto carga **SweetAlert 1** (`Scripts/sweetalert.min.js`, referenciada en `Views/Shared/_Layout.cshtml:56`) y las vistas la usan con la forma `swal("", mensaje, "warning")` (ej. `Views/Ventas/Details.cshtml:468`). **No hay SweetAlert2 ni `Swal.fire` en el repo.** La confirmacion va con la API de la v1 (`swal({ title, text, type, showCancelButton: true }, function (isConfirm) { ... })`); no introducir una libreria nueva para esto.

**Dependencia declarada con A4 (ahora en los dos sentidos):**
- `R1a`/`R1b` aplican a `Fecha` y **nunca** a `FechaAcreditacion`: un cheque diferido tiene acreditacion futura por definicion.
- Cuando entre `MetodoPago.Cheque`, **R1b se endurece a rechazo para todos los metodos menos `Cheque`** — la unica razon por la que hoy es un aviso es que no existe el lugar correcto donde poner esa fecha. Queda escrito aca para que la iteracion de A4 lo cierre y no quede un aviso que nadie se anima a tocar.

### 2.2 A3 — El importe por defecto depende del metodo

Hoy el modal ordena **Fecha → Monto → Metodo**, y Monto arranca precargado con el saldo restante de la venta. Para Efectivo eso es correcto (el importe lo determina quien cobra, y es el **59,2 %** de los pagos de septiembre: 439 de 741). Para Transferencia es la causa de C3: el importe lo determina **el cliente que transfirio**, el sistema propone el de la factura, y el operador confirma.

**Lo que ya existe (verificado en el codigo, condiciona el diseño):** `Views/Ventas/Details.cshtml:441-461` (y su gemelo en `Edit.cshtml:464-...`) ya tiene un handler `$('#MetodoPago').on('change')` que reescribe el Monto segun el metodo elegido, con un flag `montoEditadoManualmente` que **protege lo que el usuario ya tipeo** y un `window.resetMontoAutocompletado()` para el reset del modal. Hoy ese handler solo distingue `SaldoFavor` del resto.

Consecuencias:
- **HU4 es una extension de ese handler, no un mecanismo nuevo.** Baja el costo y el riesgo de la historia.
- El criterio "cambiar el metodo no borra el importe tipeado" **ya se cumple** por el flag existente; la historia solo debe no romperlo.
- **El reorden del modal NO es un requisito tecnico.** El handler reacciona al `change` del select con independencia del orden en el DOM. Se **recomienda** igual el orden Fecha → Metodo → Monto (evita que el operador tenga que volver hacia arriba cuando el campo se le vacia), pero si el cliente prefiere no tocar el layout de una pantalla que se usa ~700 veces por mes, **se puede omitir sin perder nada funcional**. Decision del cliente, no bloqueante.

**Cambios de flujo:**

1. Orden recomendado del modal: Fecha → Metodo → Monto (opcional, ver arriba).
2. **Metodos de caja** (`Efectivo`, `SaldoFavor`): Monto se precarga con `max(Total - pagos, 0)` — PAT-019, comportamiento actual sin cambio (`SaldoFavor` mantiene su clamp contra el saldo a favor disponible).
3. **Metodos de terceros** (`Transferencia`, `Debito`, `Credito`, `MercadoPago`): Monto arranca **vacio**, con `placeholder="Importe acreditado"` y el texto de ayuda *"Pone el importe que entro al banco, no el total de la venta."*. El saldo restante sigue visible, como dato, en una linea aparte ("Saldo restante de la venta: $ X") con un boton chico "usar el saldo" para el caso en que coincidan — asi no se pierde la comodidad, pero deja de ser el default silencioso.
4. **Consecuencia en vivo**, debajo del input, recalculada en cada tecla (reemplaza al texto estatico actual sobre cobrar de mas):
   - `monto == saldo` → "Con esto la venta queda totalmente pagada."
   - `monto < saldo` → "Quedan $ X por cobrar de esta venta."
   - `monto > saldo` y la venta tiene cliente → "Se cobra $ X de mas: el excedente queda como credito en la cuenta corriente de <cliente>."
   - `monto > saldo` y la venta no tiene cliente → "Se cobra $ X de mas: el excedente queda a favor en la caja, identificado en el movimiento."

**No se bloquea ningun importe.** Cobrar de mas una venta ya cubierta es un pedido funcional explicito de la iteracion anterior (`PagoService.RegistrarPagoInterno`, comentario en l.125-129) y se mantiene intacto. A3 informa; no decide.

### 2.3 A5 — Totalizadores de la pantalla de Pagos

Hoy `Views/Pagos/Index.cshtml` muestra una card "Total Filtrado" (que excluye `SaldoFavor`) y abajo una card por cada uno de los 6 valores del enum, incluso las que dan $0 — `MercadoPago` da $0 todos los meses y ocupa una card. El cliente lee la card "Transferencia" y la compara contra el total del extracto; de ahi sale la causa raiz #0.

**Nueva fila de totalizadores (3 cards, reemplaza a "Total Filtrado"):**

| Card | Incluye | Rotulo y subtitulo |
|---|---|---|
| 1 | `Efectivo` | **"Cobrado en efectivo"** — *"no se compara contra el banco"* |
| 2 | `Transferencia` (mas `Cheque` acreditado cuando exista) | **"Cobrado por transferencia"** — *"comparable con los creditos del extracto, descontando tus propios depositos de efectivo"* |
| 3 | `Debito`, `Credito`, `MercadoPago` | **"Tarjetas y billeteras"** — *"se liquidan con plazo y retencion: no coinciden linea a linea con el extracto"* |

`SaldoFavor` queda fuera de las 3 (no es plata que entro) y se muestra aparte, abajo, con el rotulo **"Aplicado de saldo a favor (no es ingreso)"** — hoy ya esta excluido del total pero sin decirlo.

Aplicacion de PAT-057: el subtitulo de cada card **dice contra que se compara ese numero**. Es la mitad no-codigo del patron y es lo que evita que el cliente vuelva a restar dos magnitudes distintas.

Las cards por metodo de abajo se mantienen para el detalle, con un unico cambio: **se ocultan las que dan $0** en el filtro vigente.

## 3. ViewModels y contratos

Sin ViewModels nuevos. Cambios de contrato:

- **`PagoService.RegistrarPagoInterno(venta, monto, metodoPago, fecha, usuarioId, observacion, pagoAnteriorId)`** — se agrega un parametro `bool confirmaFechaAntigua = false` (opcional, para no tocar las llamadas existentes) y las 3 validaciones de 2.1 al inicio del metodo, antes de la rama de `SaldoFavor`. R3 lanza una excepcion distinguible (`PagoConfirmacionRequeridaException : PagoNegocioException`) para que el Controller la pueda traducir a un JSON de confirmacion en vez de a un error.
- **`PagosController.RegistrarPago` y `EditarPago`** — aceptan `confirmaFechaAntigua` y devuelven `tipoMensaje = "confirmar"` con el texto de R3 cuando corresponde. El resto del contrato JSON no cambia.
- **`PagosController.ListarPagos`** — el objeto de respuesta agrega `totalesPorGrupo` (array de `{ grupo, monto, subtitulo }`, los 3 de 2.3) y `totalSaldoFavor`. `montoTotal` y `totalesPorMetodo` se mantienen para no romper nada que los consuma; `totalesPorMetodo` pasa a omitir los metodos en $0.

## 4. Impacto funcional por capa

**Presentacion:** `Views/Pagos/Index.cshtml` (fila de totalizadores + JS de `dataSrc`), `Views/Ventas/Details.cshtml` y `Views/Ventas/Edit.cshtml` (reorden del modal, topes de fecha, comportamiento del input Monto, linea de consecuencia), y el modal de Editar pago (topes de fecha + flujo de confirmacion de R3).
**Negocio:** `Services/PagoService.cs` (3 validaciones + nueva excepcion), `Controllers/PagosController.cs` (parametro y traduccion del JSON de confirmacion, y los 3 grupos en `ListarPagos`).
**Datos:** **sin migracion.**

Deuda declarada: el modal "Registrar Pago" esta **duplicado** entre `Ventas/Details.cshtml` y `Ventas/Edit.cshtml`. Esta iteracion lo toca en los dos lugares; extraerlo a una partial `_ModalRegistrarPago.cshtml` es la forma correcta y queda como propuesta al arquitecto (bajo riesgo, evita que la proxima iteracion los desincronice).

## 5. Riesgos de implementacion

| # | Riesgo | Mitigacion |
|---|---|---|
| R-A1 | ~~R2 puede rechazar cargas legitimas~~ | **Cerrado en Diseño, con medicion.** R2 alcanza **38 de 14.131** pagos activos (0,27 %) y R1a **2**. Margen suficiente para que las dos sean rechazo. Arquitectura no necesita volver a medirlo. |
| R-A1c | R1b queda como **aviso** y un aviso que se puede saltar no corrige nada: si el operador confirma por reflejo, los 240 pagos fechados a futuro siguen igual. | Asumido a proposito: hoy no existe el lugar correcto para esa fecha (es A4). El valor de R1b en esta iteracion es que **R1a atrape los typos de año** y que el aviso haga visible la practica. El cierre real es A4, y queda escrito en 2.1 que al entrar endurece R1b. **No vender R1b como la solucion del problema de fechas.** |
| R-A1b | `TimeZoneInfo.FindSystemTimeZoneById("Argentina Standard Time")` ya se usa en produccion, pero si el helper falla la validacion queda sin referencia de hoy. | No agregar manejo nuevo: si el helper falla, hoy ya falla el valor por defecto de los 3 modales. Mismo riesgo preexistente, no se amplia. |
| R-A3 | El cambio toca un flujo que los operadores usan ~740 veces por mes. Mal recibido, genera la misma resistencia que "Editar Pago" (0 usos en un mes). | Mantener los mismos campos y etiquetas; el reorden es opcional (ver 2.2). Y el aprendizaje de P11 aplica aca antes que en ningun lado: **avisar al cliente antes del deploy, no despues.** Una herramienta que nadie anuncio es una herramienta que nadie usa. |
| R-A3b | Dejar Monto vacio para metodos bancarios agrega tipeo en ~245 pagos por mes, justo sobre los operadores que ya rechazaron una herramienta nueva. | El boton "usar el saldo" cubre con un click el caso en que coinciden. Plan B explicito si el cliente lo rechaza: mantener el prefill y quedarse solo con la linea de consecuencia en vivo (2.2.4) — ataca C3 mas debil, pero no agrega friccion. Degrada, no rompe. |
| R-A5 | La agrupacion de la card 3 asume que Debito/Credito/MercadoPago **no** se acreditan en la misma cuenta y mes que las transferencias. En septiembre suman $4.768.320,49; si se acreditaran ahi, el numero comparable con el extracto no es el de la card 2. | El subtitulo de la card 3 ya declara el supuesto en pantalla. **Queda como pregunta P12** (abajo). El diseño es robusto en ambos casos: si la respuesta cambia, cambia que metodos entran en cada card, no la estructura. |
| R-A5b | `montoTotal` y `totalesPorMetodo` se mantienen por compatibilidad: si nadie los consume, queda codigo muerto. | Verificar en Arquitectura si algo fuera de `Views/Pagos/Index.cshtml` los lee; si no, eliminarlos en la misma iteracion. |

## 6. Historias de usuario

**HU1** — Como Administrador, quiero que el sistema rechace una fecha de pago disparatada hacia adelante, para que un error de año no deje el cobro fuera de todos los cierres.
- Guardar un pago con fecha de mas de 90 dias en el futuro devuelve error "La fecha del pago es de mas de 90 dias en el futuro. Revisa el año." y **no** crea el pago.
- Guardar un pago con fecha futura **dentro** de los 90 dias pide confirmacion con el texto de R1b; confirmar lo guarda con esa fecha (es el caso del cheque a depositar).
- La validacion resuelve "hoy" con `DateTimeExtended.ToArgentinaTimeZone()`, **no** con `DateTime.UtcNow`: un pago con fecha de hoy registrado a las 22:30 ART se guarda sin error (leccion LP-009 de la-platense).
- Aplica por igual en "Registrar Pago" (desde Details y desde Edit) y en "Editar pago".
- El `<input type="date">` de los tres formularios tiene `max` = hoy ART + 90 dias.
- Regresion: los 2 pagos historicos de diciembre 2026 ($163.780,83) son los unicos de la base que esta regla habria rechazado; ningun pago de los otros 14.129 cambia de comportamiento al guardarse de nuevo.

**HU2** — Como Administrador, quiero que el sistema no me deje fechar un pago antes de la venta que paga, para que no haya cobros que existan antes de lo que cobran.
- Guardar un pago con fecha anterior a `venta.Fecha` devuelve error con la fecha de la venta en el mensaje y no crea el pago.
- Un pago con fecha **igual** al dia de la venta se guarda sin error (comparacion por dia, no por hora).
- El `<input type="date">` tiene `min` = fecha de la venta.

**HU3** — Como Administrador, quiero que el sistema me pida confirmar cuando fecho un pago muy viejo o en el futuro, para poder cargar un cobro atrasado o un cheque sin que un error de tipeo pase inadvertido.
- Una fecha de mas de 30 dias hacia atras muestra el aviso de R3 y **no** guarda todavia.
- Una fecha posterior a hoy y hasta +90 dias muestra el aviso de R1b y **no** guarda todavia.
- Confirmar guarda el pago con esa fecha. Cancelar no guarda nada y deja el formulario abierto con los datos tipeados (no se pierde lo tipeado).
- Una fecha entre hoy y 30 dias hacia atras se guarda directo, sin aviso — es el 98,1 % de los pagos (13.865 de 14.131).
- El dialogo usa `swal` de SweetAlert 1, la libreria que ya carga el layout; no se agrega ninguna libreria.

**HU4** — Como vendedor, quiero que al elegir un metodo bancario el importe arranque vacio, para que no se me escape el total de la factura cuando el cliente transfirio otra cosa.
- Con `Efectivo` o `SaldoFavor` elegido, Monto se precarga con el saldo restante de la venta (comportamiento actual).
- Con `Transferencia`, `Debito`, `Credito` o `MercadoPago` elegido, Monto queda vacio con placeholder "Importe acreditado" y el texto de ayuda sobre no usar el total de la venta.
- El saldo restante sigue visible en el modal, y el boton "usar el saldo" lo copia al input en un click.
- Cambiar el metodo despues de haber tipeado un importe **no borra** lo tipeado.

**HU5** — Como vendedor, quiero ver en el momento que consecuencia tiene el importe que estoy poniendo, para no dejar una venta mal cobrada sin darme cuenta.
- Tipear un importe menor al saldo muestra "Quedan $ X por cobrar de esta venta." con X recalculado en cada tecla.
- Tipear un importe mayor al saldo muestra el excedente y donde queda, distinguiendo venta con cliente de venta sin cliente.
- Tipear exactamente el saldo muestra "Con esto la venta queda totalmente pagada."
- Ningun importe mayor a cero queda bloqueado por esta historia.

**HU6** — Como Administrador, quiero que la pantalla de Pagos me muestre separado lo que entro por banco de lo que entro por caja, para poder comparar contra el extracto sin restar cosas distintas.
- La fila de totalizadores muestra 3 cards —"Cobrado en efectivo", "Cobrado por transferencia", "Tarjetas y billeteras"— cada una con su subtitulo de 2.3.
- Los 3 totales respetan los filtros vigentes (rango de fechas, metodo, busqueda) igual que el total actual.
- `SaldoFavor` no entra en ninguna de las 3 y se muestra aparte rotulado "no es ingreso".
- Con el filtro de metodo puesto en un metodo unico, la card de su grupo muestra ese importe y las otras dos muestran $0.

**HU7** — Como Administrador, quiero que no me ocupen lugar las cards de metodos que no use, para leer de un vistazo los que si uso.
- Las cards por metodo de la fila inferior solo aparecen si su importe es distinto de $0 en el filtro vigente.
- Si ningun metodo tiene importe (filtro sin resultados), la fila inferior queda vacia sin romper el layout.

## 7. Pregunta nueva para el cliente

**P12 — Los cobros con tarjeta de debito/credito y los de MercadoPago se acreditan en la misma cuenta bancaria que las transferencias?** En septiembre suman $4.768.320,49 (Debito $3.922.955,34 + Credito $845.365,15 + MercadoPago $0).
- Hipotesis A: se acreditan en la misma cuenta, con plazo y retencion — entonces el extracto de esa cuenta tiene creditos de liquidacion que no son transferencias de clientes, y el Frente B tiene que clasificarlos como una tercera categoria (ademas de los depositos propios de 9.1).
- Hipotesis B: se acreditan en otra cuenta o en la billetera, y nunca aparecen en el extracto que el cliente usa — entonces la card 2 es efectivamente el unico numero comparable, como asume el diseño.
- Impacto: no bloquea A5 (la estructura de 3 cards sirve para las dos hipotesis; cambia que metodo entra en cual). **Si** condiciona el Frente B.

## Historial de ajustes
- 2026-10-07: **Diseño abierto del "Frente A recortado — higiene del circuito de Pagos (A1 + A3 + A5)"**, a partir de la seccion 9 de `1-analista-funcional.md`. Sin migracion EF; Negocio + Presentacion. 7 historias de usuario (HU1-HU7). El escaneo de reutilizacion dio un resultado inusual: **PAT-019 ya estaba aplicado en este proyecto y resulto ser la causa de C3** (el prefill del saldo restante hace que el operador confirme el importe facturado en vez de tipear el acreditado), asi que A3 lo *acota* a los metodos de caja en vez de reaplicarlo. Se reusa la leccion LP-009 de la-platense (validar fecha futura contra la hora de Argentina, no UTC), el criterio de fecha de vinosefue y el principio no-codigo de PAT-057 (el rotulo dice lo que el numero ES) para los totalizadores de A5. **Correccion importante contra el borrador:** la medicion sobre los 14.131 pagos activos mostro que fechar un pago a futuro **no es un error sino la practica de carga de los cheques** (242 pagos, 145 de ellos Transferencia por $62,7 M, vigente: 5 casos en septiembre), con cola legitima hasta 41 dias y 2 outliers a 350/358 dias que son los typos de año. La regla se partio en R1a (rechazo > +90 dias, alcanza 2 casos, 0 falsos positivos) y R1b (aviso, 240 casos, se endurece cuando entre A4). El umbral de R3 bajo de 60 a 30 dias porque a 60 alcanzaba 4 casos sobre 14.131. Tambien se verifico contra el codigo que el handler de `$('#MetodoPago').on('change')` ya existe con proteccion de lo tipeado (HU4 es una extension, no un mecanismo nuevo), que el reorden del modal **no** es requisito tecnico, y que la libreria de dialogos es **SweetAlert 1** (`swal`), no SweetAlert2. 1 pregunta nueva (P12: donde se acreditan Debito/Credito/MercadoPago) que no bloquea A5 pero si condiciona el Frente B. **Pendiente aprobacion para pasar a Arquitectura.**
- 2026-06-XX: Creacion. Diseno iteracion 2 del modulo Solicitudes de Ingreso de Stock a partir de devolucion del cliente.
- 2026-09-23: Diseno cerrado iteracion 4 "Agrupar por categoria en modal Stock bajo" — solo Presentacion, 3 historias de usuario, sin migracion.
- 2026-09-07: Diseno cerrado de "Ajuste directo de un Pago" (iteracion 3) — modal de ajuste sobre el listado de pagos de Venta, migracion EF (UsuarioId/Observacion/PagoAnteriorId en Pago), reversion+alta atomica reusando EliminarPago/RegistrarPago bajo el mismo lock. Mismo dia, alcance ampliado a pedido de Joaquin: el boton "Editar fecha" existente (`ActualizarFechaPago`) se unifica con el ajuste de monto en un unico boton/endpoint "Editar pago" (Fecha+Monto+Metodo), con la decision explicita de que TODA edicion (incluida solo-fecha) pasa siempre por reversion+alta con motivo obligatorio — sin camino liviano alternativo. `ActualizarFechaPago` queda reemplazado/eliminado. 7 historias de usuario (HU1-HU7). Patron nuevo candidato a catalogar (variante de PAT-020). Pendiente aprobacion para pasar a Arquitectura.
