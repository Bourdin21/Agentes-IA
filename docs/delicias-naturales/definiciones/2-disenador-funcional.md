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

## Historial de ajustes
- 2026-06-XX: Creacion. Diseno iteracion 2 del modulo Solicitudes de Ingreso de Stock a partir de devolucion del cliente.
