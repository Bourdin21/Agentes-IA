# 2 — Diseño Funcional
## Sistema de Gestión Comercial — Indumentaria y Calzado

**Cliente:** Ulises  
**Proveedor:** OlvidataSoft  
**Versión:** 1.0  
**Estado:** Diseño funcional cerrado — listo para handoff a Arquitectura  
**Base:** `analisis-funcional.md` v1.1 aprobado (incluye decisiones D1–D6)  

> Memoria acumulativa del agente "diseñador funcional". Este documento es la fuente de verdad para la etapa de Diseño. El detalle extendido de pantallas, ViewModels y contratos vive en `diseño-funcional.md` (heredado v1.0). Aquí se consolidan los entregables exigidos por el agente y se añade lo que faltaba: máquina de estados tabular y plan por etapas para el arquitecto.

---

## 1. Alcance funcional resumido

Diseñar para los **9 módulos + Dashboard** del sistema:

- Flujo de pantallas con ruta, acción y rol.
- ViewModels con validaciones funcionales.
- **Máquina de estados** de Compra y Venta en tabla `origen / evento / destino / guarda / acción / error`.
- Reglas de negocio y permisos **por acción**.
- Impacto funcional por capa.
- Plan funcional por etapas para handoff al arquitecto.

Decisiones funcionales adoptadas (del análisis v1.1):

| ID | Decisión |
|---|---|
| D1 | Numeración de venta: `int` autoincremental gestionado por DB. |
| D2 | Cuotas: el recargo se distribuye en cada cuota; diferencia por redondeo a la última. |
| D3 | Dañadas devueltas a proveedor antes de recepcionar: se ignoran. |
| D4 | Aumento masivo: no se persiste preview; el registro se crea solo al confirmar. |
| D5 | Cliente con ventas: bloqueo de inactivación (igual a categoría con productos). |
| D6 | Aumento masivo concurrente: first-write-wins (bloqueo optimista por `RowVersion`). |

---

## 2. Flujo de pantallas y wireframe textual por pantalla

Las rutas, acciones, roles y wireframes textuales por pantalla están consolidados en `diseño-funcional.md` §2 (heredado). Resumen del mapa de pantallas:

| Módulo | Pantallas clave |
|---|---|
| Seguridad | Login (existente), Perfil, Usuarios (Admin) |
| Maestros | Listados + ABM de Categorías, Subgrupos, Clientes, Proveedores, TiposPrecioZapatilla |
| Productos | Listado, Detalle, ABM Producto, ABM Variante (formulario dinámico Ropa/Zapatilla) |
| Stock | Listado con alertas, Carga inicial, Ajuste manual, Historial movimientos |
| Compras | Listado, Crear, Detalle, Editar, Cambiar estado, **Recepcionar** (compleja) |
| Ventas ⭐ | Listado, **Nueva venta single-page** (4 secciones), Detalle, Anular, Entregar, Remito PDF |
| Devoluciones | Listado, **Wizard 4 pasos**, Detalle |
| Resumen semanal | Vista con navegación semanal + export Excel |
| Aumento masivo | Pantalla única con preview + confirmación |
| Dashboard | Widgets diferenciados por rol |

### Lógica de distribución estándar (design system)

Para garantizar consistencia de uso, **toda pantalla** sigue esta distribución:

```
┌─ Breadcrumb + Título de la pantalla ─────────────────────────────┐
│                                                                  │
│  [Acción primaria]   [Acción secundaria]   [Filtros colapsables] │
│                                                                  │
├─ Cuerpo (DataTable / Formulario / Wizard) ───────────────────────┤
│                                                                  │
│   • Listados: DataTable server-side con columnas estandarizadas. │
│   • Formularios: layout 2 columnas en desktop, 1 en mobile.      │
│   • Detalles: header con metadatos + tabs/secciones colapsables. │
│   • Wizard: stepper superior + cuerpo del paso + footer con      │
│     botones [Anterior] [Siguiente/Confirmar].                    │
│                                                                  │
├─ Footer de acciones (sticky en formularios largos) ──────────────┤
│   [Cancelar] ──────────────────────── [Guardar / Confirmar]      │
└──────────────────────────────────────────────────────────────────┘
```

Confirmaciones destructivas o de cambio de estado: **SweetAlert2**.  
Búsquedas remotas: **Select2**.  
Mensajes de feedback: toasts top-right.  
Formato de moneda: `$ #.###,##` (es-AR).

---

## 3. ViewModels propuestos (campos y validaciones funcionales)

Catálogo completo de **~35 ViewModels** consolidado en `diseño-funcional.md` §3. Resumen:

- **Maestros**: `CategoriaViewModel`, `SubgrupoViewModel`, `ClienteViewModel`, `ProveedorViewModel`, `TipoPrecioZapatillaViewModel`.
- **Productos**: `ProductoViewModel`, `VarianteViewModel` (con campos condicionales Ropa vs Zapatilla; `UltimoPrecioCompra` y `Ganancia` solo para Admin).
- **Stock**: `StockListItemViewModel`, `AjusteStockViewModel`, `MovimientoStockListItemViewModel`.
- **Compras**: `CompraCreateViewModel`, `CompraDetalleItemViewModel`, `CompraRecepcionViewModel`, `CompraRecepcionLineaViewModel` (validación custom: `Recibida + Dañada + Devuelta ≤ Pedida`).
- **Ventas ⭐**: `VentaCreateViewModel`, `VentaDetalleItemViewModel`, `VentaPagoItemViewModel` (con `PorcentajeFinanciamiento` solo si `MedioPago = Cuotas`), `VentaDetalleViewModel` (con `CostoTotal` y `GananciaTotal` solo Admin).
- **Devoluciones**: `DevolucionCreateViewModel`, `DevolucionItemViewModel` (validación custom: `CantidadDevolver ≤ CantidadDisponible`).
- **Resumen semanal**: `ResumenSemanalViewModel` + detalle.
- **Aumento masivo**: `AumentoMasivoViewModel` + `AumentoMasivoPreviewItemViewModel`.

Convenciones aplicadas:
- DataAnnotations con mensajes en es-AR.
- `[Required]`, `[MaxLength]`, `[Range]`, `[EmailAddress]`, validaciones custom para invariantes de dominio.
- ViewModels nunca exponen entidades de dominio directamente.

---

## 4. Máquina de estados (formato tabla)

### 4.1 Compra

| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| (∅) | `CrearCompra` | Borrador | Proveedor activo, ≥1 línea, costo>0, cantidad>0 | Persistir cabecera + detalles | "Compra inválida: revise líneas/proveedor" |
| Borrador | `EditarCompra` | Borrador | Estado = Borrador | Reemplazar líneas/cabecera | "Solo se edita en Borrador o EnProceso" |
| Borrador | `Avanzar` | EnProceso | Estado = Borrador | Cambiar estado | "Transición no permitida" |
| EnProceso | `EditarCompra` | EnProceso | Estado = EnProceso | Reemplazar líneas/cabecera | "Solo se edita en Borrador o EnProceso" |
| EnProceso | `Avanzar` | Verificada | Estado = EnProceso | Cambiar estado | "Transición no permitida" |
| Verificada | `Avanzar` | Recibida | Estado = Verificada, líneas válidas | **Recepcionar**: para cada línea `Rec+Dañ+Dev ≤ Pedida`; impactar stock con `CantidadRecibida` (Movimiento `CompraRecepcion`); si hay `DevueltaProveedor` y ya hubo recepción previa → Movimiento `DevolucionProveedor` (D3: si no hubo recepción aún, se ignora); actualizar `UltimoPrecioCompra` por variante | "Cantidades de recepción inválidas (Rec+Dañ+Dev > Pedida)" / "Stock no puede quedar negativo" |
| Recibida | * (cualquiera) | — | — | — | "Compra recibida: solo lectura" |
| Borrador / EnProceso / Verificada / Recibida | `AdjuntarArchivo` | (mismo) | Tamaño ≤ 5 MB y formato válido | Guardar en `wwwroot/uploads/compras/{guid}` | "Archivo inválido (formato o tamaño)" |

### 4.2 Venta

| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| (∅) | `CrearVenta` | Confirmada | ≥1 línea, stock suficiente por variante, ≥1 pago, suma pagos = total (±0,01); si `Cuotas` → `CantidadCuotas≥2` y `% ≥0`; si hay cliente referenciado debe existir | **Transacción serializable**: asignar nro correlativo (D1, autoincremental DB), decrementar stock por línea (Movimiento `Venta`), persistir detalles y pagos; si `Cuotas` distribuir recargo en cada cuota con redondeo y ajuste en última (D2) | "Stock insuficiente para variante X" / "Suma de pagos ≠ total" / "Datos de cuotas inválidos" |
| Confirmada | `Anular` | Anulada | Estado = Confirmada | Reponer stock por línea (Movimiento `AnulacionVenta`), marcar Anulada | "Solo se puede anular una venta Confirmada" |
| Confirmada | `MarcarEntregada` | Entregada | Estado = Confirmada | Cambiar estado | "Solo se entrega una venta Confirmada" |
| Confirmada / Entregada | `EmitirRemito` | (mismo) | Estado ≠ Anulada | Generar PDF QuestPDF | "Venta anulada: no genera remito" |
| Confirmada / Entregada | `AdjuntarComprobante` | (mismo) | Tamaño ≤ 5 MB y formato válido | Guardar en `wwwroot/uploads/ventas/{guid}` | "Archivo inválido" |
| Entregada | `Anular` | — | — | — | "Venta entregada: usar Devolución/Cambio" |
| Anulada | * | — | — | — | "Venta anulada: solo lectura" |
| Confirmada / Entregada | `RegistrarDevolucion` | (mismo) | Wizard válido (ver 4.3) | Crear `DevolucionCambio` asociada | (ver 4.3) |

### 4.3 Devolución / Cambio (operación atómica, sin estados internos)

| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| (∅) | `CrearDevolucionDinero` | Registrada | Venta en (Confirmada\|Entregada), `CantidadDevolver ≤ CantidadVendida − DevolucionesPrevias` por variante, motivo presente | Reingresar stock por ítem (Movimiento `DevolucionCliente`) | "Cantidad supera disponible" / "Venta no admite devolución" |
| (∅) | `CrearCambioMismoValor` | Registrada | Idem + valor ítems nuevos = valor ítems devueltos + stock suficiente nuevos | Reingresar stock devueltos + decrementar stock nuevos | "Valores no coinciden" / "Stock insuficiente nuevo" |
| (∅) | `CrearCambioMayorValor` | Registrada | Idem + diferencia > 0 + medio de pago informado | Reingresar stock devueltos + decrementar stock nuevos + registrar pago diferencia | "Diferencia inválida" / "Medio de pago obligatorio" |

### 4.4 Maestros (soft delete)

| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Activo | `Inactivar` (Categoría) | Inactivo | Sin productos activos asociados | Setear `DeletedAt` | "Categoría con productos activos" |
| Activo | `Inactivar` (Cliente) | Inactivo | **D5**: sin ventas asociadas | Setear `DeletedAt` | "Cliente con ventas: no se puede inactivar" |
| Activo | `Inactivar` (Variante) | Inactivo | `StockActual = 0` | Setear `DeletedAt` | "Variante con stock > 0" |
| Activo | `Inactivar` (otros) | Inactivo | Sin dependencias activas | Setear `DeletedAt` | "Maestro con dependencias activas" |

### 4.5 Aumento masivo (operación atómica con D6)

| Origen | Evento | Destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| (∅) | `Previsualizar` | (sin persistir) | Filtros válidos, % > 0 y ≤ 500 | Calcular precios nuevos en memoria; **no persistir** (D4) | "Parámetros inválidos" |
| (∅) | `Aplicar` | Registrado | ≥1 variante seleccionada, % > 0 | **Bloqueo optimista** por `RowVersion` (D6): batch update; si conflicto de concurrencia → first-write-wins, segundo recibe error y debe re-previsualizar; persistir log `AumentoMasivo` solo en confirmación | "Conflicto de concurrencia: re-previsualice" / "Sin variantes seleccionadas" |

---

## 5. Reglas de negocio y permisos por pantalla / acción

### 5.1 Matriz de permisos por acción (consolidada)

| Acción | Admin | Vendedor | Notas |
|---|---|---|---|
| Login / Editar perfil propio | ✅ | ✅ | — |
| Gestión Usuarios (CRUD) | ✅ | ❌ | Admin no puede crear SuperUsuario |
| ABM Categorías / Subgrupos / Proveedores / TiposPrecio | ✅ | ❌ | Soft delete con guardas |
| ABM Clientes | ✅ | 👁️ | Vendedor solo lectura + Select2 búsqueda |
| ABM Productos / Variantes | ✅ | 👁️ sin costos | Vendedor sin `UltimoPrecioCompra` ni `Ganancia` |
| Inactivar variante | ✅ | ❌ | Guarda: `Stock = 0` |
| Listar / consultar Stock + Historial | ✅ | ✅ | — |
| Carga inicial / Ajuste manual de stock | ✅ | ❌ | — |
| Crear/editar/avanzar/recepcionar Compra | ✅ | ❌ | 403 en cualquier ruta `/Compras/*` |
| Adjuntar a Compra | ✅ | ❌ | — |
| Listar Ventas | ✅ con costos | ✅ sin costos | Filtra payload server-side por rol |
| Crear Venta | ✅ | ✅ | — |
| Anular Venta | ✅ | ✅ | Guarda estado Confirmada |
| Marcar Entregada | ✅ | ✅ | — |
| Generar Remito PDF | ✅ | ✅ | — |
| Adjuntar comprobante venta | ✅ | ✅ | — |
| Crear Devolución / Cambio | ✅ | ✅ | — |
| Resumen Semanal + Excel | ✅ | ❌ | 403 |
| Aumento Masivo (preview + aplicar) | ✅ | ❌ | 403 |
| Dashboard Admin (full) | ✅ | ❌ | — |
| Dashboard Vendedor (limitado) | ❌ | ✅ | Sin costos/ganancias |

### 5.2 Reglas críticas por pantalla

- **Nueva Venta**: validación JS de stock al agregar línea; suma pagos = total con tolerancia ±0,01; si `Cuotas` → cuotas ≥ 2 y % ≥ 0; al confirmar el server re-valida en transacción serializable.
- **Recepción Compra**: validación JS por línea `Rec + Dañ + Dev ≤ Pedida`; al confirmar, server re-valida y solo `CantidadRecibida` impacta stock; D3 aplica para dañadas pre-recepción.
- **Wizard Devolución**: estado JS por paso, pero **toda la validación dura es server-side** al POST del paso 4 (cantidad disponible, valores, stock items nuevos, medio de pago si aplica).
- **Aumento masivo**: preview en memoria (D4), aplicación con bloqueo optimista (D6).
- **Sidebar dinámico**: ítems renderizados condicionalmente con `User.IsInRole()`.

---

## 6. Impacto funcional por capa

### 6.1 Presentación (Web)
- 13 controllers nuevos + ajuste a `HomeController` y sidebar.
- ~30 vistas + partials para líneas dinámicas.
- ~35 ViewModels con DataAnnotations es-AR.
- 7 endpoints AJAX (Subgrupos por categoría, búsquedas Select2, stock por variante, resumen semanal, variantes de aumento).
- JS complejo en 3 pantallas: Nueva Venta, Recepción Compra, Wizard Devolución.
- Autorización por policies por controller/acción.

### 6.2 Negocio (Application)
- 14 interfaces de servicio (catálogo en `diseño-funcional.md` §4).
- Todos los retornos vía `ServiceResult`/`ServiceResult<T>`.
- Validaciones cruzadas y reglas de transición de estado encapsuladas en services (no en controllers).
- Política de visibilidad de costos por rol (parámetro `incluirCostos` o resolución por contexto del usuario).
- Servicios con dependencia entre sí: `IVentaService → IStockService`, `ICompraService → IStockService`, `IDevolucionService → IStockService`, `IRemitoService → IVentaService`.

### 6.3 Datos (Infrastructure / requerimientos esperados)
- 20 entidades + 5 enums (catálogo en análisis funcional §7).
- Requerimientos por pantalla detallados en `diseño-funcional.md` §5.
- Operaciones que exigen transacción serializable: crear venta, recepcionar compra, registrar devolución/cambio.
- Bloqueo optimista (`RowVersion`) en `VarianteProducto` para D6 (aumento masivo).
- Adjuntos en disco local: `wwwroot/uploads/{compras|ventas}/{guid}`.
- Queries directas (no por service) tolerables solo para reportes: Resumen Semanal.

---

## 7. Riesgos y supuestos

| # | Tipo | Descripción | Mitigación |
|---|---|---|---|
| R1 | Riesgo | Concurrencia en stock entre vendedores | Transacción serializable en `IVentaService.CrearAsync` |
| R2 | Riesgo | Carrito de venta volátil (memoria JS) | Aceptado v1; sin persistencia de borrador |
| R3 | Riesgo | Adjuntos en disco sin backup | GUID + estrategia de migración a blob en v2 |
| R4 | Riesgo | Wizard devolución con estado JS | Validación server-side completa al POST |
| R5 | Riesgo | Concurrencia en aumento masivo | D6: bloqueo optimista por `RowVersion`, first-write-wins |
| R6 | Riesgo | Redondeo en cuotas (D2) podría generar centavos no asignados | Ajustar diferencia en última cuota |
| S1 | Supuesto | El proyecto es MVC clásico (Controllers/Views), no Razor Pages | A confirmar con arquitecto si la guía operativa cambia |
| S2 | Supuesto | `ServiceResult<T>`, `DataTableRequest/Response`, soft delete global existen | Verificado en `analisis-funcional.md` §7 |
| S3 | Supuesto | Auth con Identity y rol Vendedor agregable al seed | Verificado |
| S4 | Supuesto | Disponibilidad de QuestPDF y ClosedXML como librerías locales | Sin integración externa requerida |

---

## 8. Plan funcional por etapas para el arquitecto

> El plan está expresado en **incrementos funcionales verticales**. No incluye plan de codificación (responsabilidad del arquitecto).

### Etapa F0 — Base de seguridad (preparación)
- Alta del rol **Vendedor**, policies y sidebar dinámico.
- Criterios cierre: vendedor recibe 403 en módulos restringidos; sidebar oculta entradas no permitidas.

### Etapa F1 — Maestros comerciales
- ABMs Categorías, Subgrupos, Clientes, Proveedores, TiposPrecioZapatilla.
- Cascada Categoría → Subgrupo (AJAX).
- Reglas D5 (cliente con ventas → bloqueado, anticipado conceptualmente; verificación dura llega en F5).
- Criterios cierre: ABMs operativos con guardas de soft delete.

### Etapa F2 — Productos y Variantes
- Producto + Variante con formulario dinámico Ropa vs Zapatilla.
- Búsquedas AJAX para selectores de venta/compra.
- Visibilidad de costos por rol.
- Criterios cierre: variantes con campos condicionales correctos; Vendedor sin columnas de costo.

### Etapa F3 — Stock e Inventario
- Listado con alerta visual, carga inicial, ajuste manual, historial.
- Trazabilidad polimórfica de movimientos (FKs a Compra/Venta/Devolución/Ajuste según corresponda).
- Criterios cierre: cualquier alteración de stock genera `MovimientoStock` consistente.

### Etapa F4 — Compras (incluye máquina de estados)
- Listado, crear, editar, cambio de estado lineal, **recepción** con validación `Rec+Dañ+Dev ≤ Pedida`, adjuntos.
- D3 aplicado en recepción.
- Actualización de `UltimoPrecioCompra` al recepcionar.
- Criterios cierre: máquina de estados §4.1 verificada con casos felices y de error.

### Etapa F5 — Ventas ⭐ (core)
- Carrito single-page AJAX, múltiples medios de pago, cuotas con D2.
- Numeración correlativa D1.
- Transacción serializable.
- Anulación con reposición; entrega; remito PDF; adjuntos.
- Reforzar D5 (validación dura de cliente con ventas en inactivación de Maestros).
- Criterios cierre: máquina de estados §4.2 verificada; pruebas de concurrencia (R1) pasan.

### Etapa F6 — Devoluciones y Cambios
- Wizard 4 pasos con validación dura server-side al confirmar.
- Tres tipos: Devolución dinero, Cambio mismo valor, Cambio mayor valor.
- Criterios cierre: stock reingresa correctamente; cantidades disponibles respetan devoluciones previas.

### Etapa F7 — Resumen semanal + Aumento masivo
- Resumen semanal (transferencias) con export Excel.
- Aumento masivo con preview no persistido (D4) y aplicación con bloqueo optimista (D6).
- Criterios cierre: aumento concurrente devuelve error consistente al segundo actor.

### Etapa F8 — Dashboard final + endurecimiento
- Widgets diferenciados por rol.
- Revisión integral de permisos, mensajes, formato es-AR.
- Criterios cierre: dashboard correcto por rol; checklist de salida funcional cumplido.

### Dependencias entre etapas

```
F0 → F1 → F2 → F3 → F4 → F5 → F6 → F7 → F8
				  ↘── F5 (Ventas requiere Stock) ──↗
```

### Preguntas abiertas para el arquitecto

1. Mecanismo concreto para **bloqueo optimista (D6)**: `RowVersion` (timestamp) en `VarianteProducto` vs lock pesimista en transacción del batch. Recomendado: `RowVersion`.
2. Estrategia de **persistencia del redondeo en cuotas (D2)**: persistir cada cuota como fila propia (recomendado para auditoría) o un único registro `VentaPago` con metadatos de cuotas.
3. **Índices únicos** sugeridos: `Sku`, `CodigoBarra`, `Numero` correlativo de venta, `Email` de usuario.
4. Política de **transacciones**: confirmar `IsolationLevel.Serializable` para ventas/recepciones/devoluciones.
5. Mecanismo de **filtrado de payload por rol** para no exponer costos: ¿filtro en service vía `ICurrentUser` o vía dos DTOs distintos? Recomendado: parámetro explícito `incluirCostos` resuelto en controller a partir del rol.

---

## 9. Checklist de salida — Diseño funcional

```
DISEÑO FUNCIONAL — CHECKLIST DE SALIDA
────────────────────────────────────────────────────────────────────
[✓] Alcance funcional resumido
[✓] Flujo de pantallas y wireframes textuales (consolidados)
[✓] ViewModels con validaciones funcionales
[✓] Máquina de estados en formato tabla (Compra, Venta, Devolución,
	Maestros soft delete, Aumento masivo)
[✓] Reglas y permisos por acción
[✓] Impacto por capa (Presentación / Negocio / Datos)
[✓] Riesgos y supuestos
[✓] Plan funcional por etapas F0..F8 para el arquitecto
[✓] Decisiones D1..D6 incorporadas
[✓] Preguntas abiertas para arquitectura
────────────────────────────────────────────────────────────────────
```

---

## 10. Handoff a Arquitectura

### Paquete entregado
1. Este documento (`2-disenador-funcional.md`).
2. `analisis-funcional.md` v1.1 (decisiones D1–D6 cerradas).
3. `diseño-funcional.md` v1.0 (catálogo extendido de pantallas, ViewModels y contratos de servicio).

### Foco esperado del arquitecto
- Validar separación por capa (sin lógica de negocio en Controllers).
- Definir contratos técnicos de los services en función de los contratos funcionales propuestos.
- Plan de **6 migraciones EF (M1–M6)** según análisis §8.
- Estrategia técnica para D6 (RowVersion) y D2 (persistencia de cuotas).
- Política de transacciones serializables.
- Estimación técnica para presupuesto.

### Sin bloqueantes funcionales
- No quedan decisiones funcionales abiertas.
- Las cinco preguntas de §8 son de **diseño técnico**, no funcional.
