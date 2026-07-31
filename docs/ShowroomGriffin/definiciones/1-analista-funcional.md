# Analista Funcional — ShowroomGriffin v2
**Fecha última actualización:** 2025-07  
**Estado:** Análisis de impacto completado. Decisiones validadas. Listo para diseño técnico.

---

## Decisiones validadas por el cliente

| # | Pregunta | Decisión confirmada |
|---|---|---|
| P1 | ¿`Anotaciones` es interna o para imprimir? | **A — Nota interna del vendedor** |
| P2 | ¿Unificar `Observaciones` + `Anotaciones`? | **B — Unificar en un solo campo** (renombrar o reutilizar `Observaciones`) |
| P5 | Autofill importe de pago | **A — Sugiere saldo restante** (Total − pagos ya en lista) |
| P11 | ¿Subtotal de línea editable? | **A — No. Solo PrecioUnitario y Cantidad son editables** |
| P12 | ¿Total de venta editable directamente? | **A — No. Es resultado del cálculo** |
| P14 | ¿Marca en Producto = FK a Subgrupo? | **A — Subgrupo se renombra a Marca. SubgrupoId = MarcaId** |
| P13 | ¿Datos en DB son consistentes? | **A — Sí, migración segura** |
| P4 | ¿Combos varían por categoría? | **B — Varía por categoría** |
| P15 | Talles de indumentaria predefinidos | **B — Sí, también predefinidos** (XS, S, M, L, XL, XXL ✅) |
| PC02 | ¿Vendedor crea cliente desde modal? | **B — Sí, datos mínimos (nombre + teléfono)** |
| P10 | ¿Empleado puede crear ventas? | **A — Sí (Vendedor con acceso reducido)** |
| P8 | ¿Devolución desde qué estado? | **B — Desde Confirmada y Entregada** |
| P9 | ¿Combos en modal de cambio? | **A — Sí, mismos combos anidados** |
| P6 | ¿Stock rápido = nueva vista o existente? | **B — Misma vista mejorada visualmente + acceso Empleado** |

---

## Decisión clave adicional (por el cliente)

> **"Marcas y Modelos van a ser entidades anidadas. Subgrupos cambiar por Marcas y modelar nuevo esquema."**

### Nuevo esquema de clasificación

```
Categoría (Indumentaria / Zapatillas / Accesorios)
  └── Marca  [renombrado desde Subgrupo]
        └── Modelo  [NUEVA entidad — hija de Marca]
                └── Producto  [CategoriaId + MarcaId + ModeloId]
                      └── VarianteProducto  [Color + Talle/Numero — SIN Marca ni Modelo]
```

---

## Alcance funcional v2

### INCLUIDO

| Ref | Cambio | Tipo |
|---|---|---|
| C01 | Unificar campo: renombrar Observaciones → Anotaciones (nota interna) | Aditivo |
| C02 | Modal crear cliente rápido (nombre+tel) desde venta, disponible para Vendedor | Nuevo flujo |
| C03 | Combos anidados Marca→Modelo→Color→Talle en ventas (varía por categoría) | Nuevo flujo |
| C04 | Autofill importe pago = saldo restante | UI/JS |
| C05 | Combos anidados en Compras (reutiliza C03) | Nuevo flujo |
| C06 | Vista stock mejorada visualmente + acceso Empleado | Mejora UI + rol |
| C07 | Búsqueda rápida venta (fecha/cliente/producto) en Cambios; desde Confirmada y Entregada | Mejora flujo |
| C08 | Nuevo rol Empleado: Ventas + Cambios + Stock (sin Admin) | Nuevo rol |
| C09 | PrecioUnitario y Cantidad editables; Subtotal/Total calculados (no editables) | UI/JS |
| C10 | Refactor: Subgrupo→Marca, nueva entidad Modelo, quitar Marca/Modelo de VarianteProducto | Refactor estructural |
| C11 | TalleConfig: Zapatilla Adulto 34–46, Zapatilla Niño 22–33, Indumentaria XS–XXL | Nueva entidad + seed |
| C12 | Seed categorías + renombrar labels Subgrupo→Marca en UI | Seed + labels |

### NO INCLUIDO
- Edición directa de Total o Subtotal por línea
- Impresión de anotaciones en remito
- Reportes por Empleado
- Integración con sistemas externos

### DEPENDENCIAS
```
C10 → desbloquea C03, C05, C07
C11 → alimenta C03, C05 (combo talle)
C12 → requiere C10
C08 → requiere definir menú por rol
```

---

## Entidades nuevas y modificadas

### RENOMBRADAS (semántica + labels)
- `Subgrupo` → `Marca` (tabla puede renombrarse `Marcas`)

### MODIFICADAS
| Entidad | Antes | Después |
|---|---|---|
| `Producto` | CategoriaId, SubgrupoId | CategoriaId, MarcaId, ModeloId |
| `VarianteProducto` | Marca (str), Modelo (str), Talle/Numero (str libre) | SIN Marca/Modelo; TalleId FK a TalleConfig |

### NUEVAS
| Entidad | Propiedades | Relación |
|---|---|---|
| `Modelo` | Id, Nombre, MarcaId | Hijo de Marca; padre de Producto |
| `TalleConfig` | Id, Valor (str), Tipo (enum) | FK en VarianteProducto.TalleId |

---

## Casos de uso principales

### CU-01 · Alta de Venta con combos anidados
**Criterios de aceptación:**
- [ ] Al cambiar Categoría se resetean Marca, Modelo, Color, Talle
- [ ] Solo se muestran talles/colores con stock > 0
- [ ] Si no hay variante para la combinación, mensaje claro
- [ ] PrecioUnitario precargado desde VarianteProducto.PrecioVenta, editable
- [ ] Subtotal = PrecioUnitario × Cantidad (no editable)
- [ ] Total = Suma subtotales − Descuento (no editable)
- [ ] Autofill importe pago = Total − pagos ya agregados

### CU-02 · Crear cliente rápido desde modal
**Criterios de aceptación:**
- [ ] Accesible para Vendedor y Empleado
- [ ] Nombre obligatorio; teléfono opcional
- [ ] Nuevo cliente queda seleccionado automáticamente en el Select2 de la venta
- [ ] Visible en módulo Clientes para completar datos después

### CU-03 · Consulta rápida de stock
**Criterios de aceptación:**
- [ ] Rol Empleado puede acceder a /Stock/Index
- [ ] Filtros por Categoría, Marca, Modelo, Color, Talle
- [ ] Precio de costo oculto para Empleado y Vendedor
- [ ] Alerta visual en stock <= StockMinimo

### CU-04 · Cambio/Devolución con búsqueda rápida
**Criterios de aceptación:**
- [ ] Búsqueda por fecha, nombre de cliente (parcial), descripción producto/variante
- [ ] Solo ventas Confirmada o Entregada
- [ ] Para cambio: selección con combos anidados (igual C03)
- [ ] Stock ajustado automáticamente y trazado en MovimientoStock

### CU-05 · Rol Empleado
**Criterios de aceptación:**
- [ ] Puede crear y ver sus propias ventas
- [ ] Puede operar cambios/devoluciones
- [ ] Puede consultar stock (sin precio de costo)
- [ ] NO accede a: Compras, ABM Productos/Variantes, Configuración, Clientes ABM, Usuarios, Auditoría, Resumen semanal, Aumento masivo

---

## Validaciones clave

| Cambio | Validación |
|---|---|
| C01 Anotaciones | Texto libre, max 1000 chars, opcional |
| C02 Modal cliente | Nombre obligatorio; deduplicación por nombre+teléfono |
| C03/C05 Combos | Combinación Marca+Modelo+Color+Talle debe resolver VarianteProductoId existente |
| C07 Dev/Cambio | Venta Confirmada o Entregada; cantidad devuelta ≤ cantidad original |
| C10 Refactor | Migración: no dejar variantes huérfanas; backup previo |
| C11 TalleConfig | Talle debe pertenecer al catálogo de la categoría |

---

## Riesgos

| Riesgo | Mitigación |
|---|---|
| R1 — C10 es el cambio más invasivo | Backup + migración en 2 pasos (agregar columnas, luego quitar) |
| R2 — Combos sin stock confunden usuario | Solo mostrar talles/colores con stock > 0 |
| R3 — Solapamiento Empleado/Vendedor en permisos | Definir menú por rol explícitamente |
| R4 — BuscarVenta solo acepta ID exacto hoy | Ampliar con búsqueda multi-criterio |
| R5 — TalleConfig indumentaria: valores resueltos | ✅ XS, S, M, L, XL, XXL |

---

## C11a — Talles de Indumentaria ✅ RESUELTO

**Decisión confirmada — Opción A:** Solo talle por letra (adulto).  
Valores seed: `XS`, `S`, `M`, `L`, `XL`, `XXL`

### Catálogo TalleConfig completo

| Tipo (enum) | Valores |
|---|---|
| `ZapatillaAdulto` | 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46 |
| `ZapatillaNino` | 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33 |
| `Indumentaria` | XS, S, M, L, XL, XXL |

---

## Banderas de implementación

| Flag | Estado |
|---|---|
| ✅ Requiere migración EF | SÍ — C01, C10, C11, C12 |
| ❌ Integración externa | NO |
| ✅ Máquina de estados impactada | SÍ — C07 (Confirmada + Entregada habilitan devolución) |
| ✅ Nuevo rol/policy | SÍ — C08 Empleado |
| ✅ Nuevas entidades de dominio | SÍ — Modelo, TalleConfig |
| ✅ Refactor entidad existente | SÍ — Subgrupo→Marca, VarianteProducto, Producto |

---

## V9 — Redirect post-ajuste de stock (2026-07-02) — Fast-path

**Pedido:** en la pantalla de ajuste manual de stock (`Stock/Ajuste`), tras cargar el ajuste de un producto, hoy redirige a `Stock/Index` (listado general). El usuario suele cargar ajustes de varios productos seguidos y quiere quedarse en la misma pantalla de ajuste tras guardar, en vez de volver al listado cada vez.

**Alcance:** cambiar el destino del `RedirectToAction` en el POST `StockController.Ajuste` de `Index` a `Ajuste` (GET), limpiando el formulario para el próximo ajuste.

**Fuera de alcance:** no cambia validaciones, permisos (`RequireAdministrador`), lógica de `AjusteManualAsync`, ni el modelo `AjusteStockViewModel`.

**Criterio de aceptación:** al guardar un ajuste válido desde `Stock/Ajuste`, la respuesta redirige (GET) a `Stock/Ajuste` con `TempData["Success"]` mostrando el mensaje de confirmación, y el formulario queda listo para cargar el siguiente producto.

**Banderas:** sin migración EF, sin cambio de permisos, sin nueva entidad. Riesgo: bajo.

---

## V10 — Carga masiva de stock por Modelo + filtros completos en Consulta de Stock (2026-07-30) — EN DISCOVERY

**Estado:** análisis inicial entregado, pendiente de respuestas del cliente (Q1–Q7) y aprobación para pasar a Diseño.

**Pedido del cliente:** "es muy tedioso cargar el stock por modelo, por talle, por color, y cada talle cargarlo individualmente" (sobre `/Stock/Ajuste`, hoy 1 variante por vez vía select2 + `CantidadNueva` + submit). Además: "los filtros en la pantalla de consulta de stock tienen que tener todas las propiedades del stock que se lista" (sobre `/Stock/Index`).

### Punto A — Carga masiva de stock (Ajuste Manual)

**Incluido (hipótesis de alcance):**
- Nuevo modo de carga: elegir un Modelo → grilla con todas sus variantes existentes (Color × Talle) con stock actual editable inline.
- Guardado en lote: un submit dispara N `AjusteStock` + `MovimientoStock` (uno por variante modificada), reutilizando `AjusteManualAsync` fila a fila dentro de una operación de conjunto.
- Filas sin cambios no generan movimiento. Convive con el ajuste individual actual (no lo reemplaza).
- Mismo permiso `RequireAdministrador` que hoy.

**No incluido (salvo pedido explícito):** alta de variantes nuevas (combinaciones Talle×Color inexistentes) desde esta pantalla; carga cruzando múltiples modelos a la vez; importación Excel/CSV.

**Riesgos:** volumen de filas por modelo (posible necesidad de paginar/virtualizar la grilla); concurrencia por fila (`RowVersion` de `VarianteProducto` debe seguir chequeándose individualmente, no solo a nivel de página); trazabilidad del motivo si se agrupa en un solo campo por lote.

### Punto B — Filtros completos en Consulta de Stock

**Incluido (hipótesis de alcance):**
- Agregar filtro por Talle (dependiente de Modelo, mismo patrón que Color).
- Integrar "Solo alertas" (hoy botón que recarga toda la página) como filtro "Estado" (Todos/OK/Límite/Bajo) dentro de la barra de filtros cascada, vía AJAX igual que el resto.
- Código ya cubierto por búsqueda global de DataTables; Stock/Mínimo/Déficit son columnas ordenables, no filtros (a confirmar en Q7).

**Riesgo:** si se agrega filtro Talle, hay que sumarlo también a `ExportarExcelAsync` (hoy solo recibe marcaId/modeloId/color) para mantener consistencia entre grilla y export.

### Banderas tempranas
- Migración EF: NO. Integración externa: NO. Máquina de estados: NO.

### Preguntas abiertas — hipótesis a validar con el cliente

| # | Pregunta | Opción A (hipótesis) | Opción B (hipótesis) |
|---|---|---|---|
| Q1 | Semántica del valor en la grilla masiva | Cantidad nueva = stock resultante absoluto (igual que hoy) | Cantidad a sumar/restar (delta), sin necesitar saber el stock actual de memoria |
| Q2 | Alcance de selección | Se elige un Modelo puntual y se ven sus variantes | Se elige una Marca completa y se ven todos sus Modelos agrupados |
| Q3 | Variantes faltantes en la matriz Talle×Color | Solo se muestran/editan variantes ya existentes | Se muestran con stock 0 y se pueden crear+cargar en el mismo paso (impacta catálogo) |
| Q4 | Motivo del ajuste masivo | Un campo "Motivo" único para todo el lote | Motivo autogenerado ("Ajuste masivo"), sin pedirlo |
| Q5 | Filtro Talle en Consulta de Stock | Dependiente de Modelo (igual que Color hoy) | Independiente desde el arranque, con todos los valores usados en Stock |
| Q6 | Filtro Estado vs. botón "Solo alertas" | Reemplaza al botón por un combo integrado | Conviven: botón de acceso directo + combo "Estado" más fino |
| Q7 | Filtro numérico de Stock/Déficit | No se incluye (son columnas informativas/ordenables) | Se agrega filtro "Stock ≤ umbral" |

**Gate:** no iniciar Diseño (agente 2) hasta que el cliente resuelva Q1–Q7 y apruebe el alcance de los puntos A y B.

### Decisiones confirmadas por el cliente (2026-07-30)

| # | Pregunta | Decisión confirmada |
|---|---|---|
| Q1 | Semántica del valor en la grilla masiva | **A — Cantidad nueva absoluta** (igual que el ajuste individual actual) |
| Q2 | Alcance de selección | **B — Se elige una Marca completa**; la grilla agrupa por Modelo dentro de esa Marca, mostrando todas las variantes de todos sus Modelos |
| Q3 | Variantes faltantes en la matriz Talle×Color | **B — Se crean al vuelo** desde la misma grilla masiva (amplía el alcance: ya no es solo Stock, también da de alta `VarianteProducto`) |
| Q3a | Datos obligatorios de la variante nueva (Precio de Venta, Stock Mínimo) | **Se piden en la misma grilla** — las filas correspondientes a variantes que no existen agregan columnas editables de Precio de Venta y Stock Mínimo además de la cantidad de stock inicial. Código interno/barra: **pendiente de confirmar** (asumido opcional, completable después desde Productos/Variantes salvo indicación contraria). |
| Q6 | Filtro Estado vs. botón "Solo alertas" | **A — Reemplaza el botón** por un combo "Estado: Todos/OK/Límite/Bajo" integrado a la barra de filtros; el deep-link `/Stock/Index?soloAlertas=true` (usado desde Dashboard) se preserva mapeándolo a Estado="Bajo" preseleccionado |

**Pendientes de menor impacto (default asumido salvo corrección del cliente):**
- Q4 — Motivo del ajuste masivo: **asumido Opción A** (un campo "Motivo" único para todo el lote, mejor trazabilidad con fricción mínima).
- Q5 — Filtro Talle en Consulta de Stock: **asumido Opción A** (dependiente de Modelo, mismo patrón que Color).
- Q7 — Filtro numérico de Stock/Déficit: **asumido Opción A** (no se incluye; son columnas ordenables/informativas).

### Replanteo de alcance tras Q3/Q3a — ALERTA para Arquitectura

La decisión Q3 (crear variantes al vuelo) **amplía el alcance real del Punto A**: deja de ser un cambio acotado a `Stock`/`AjusteStock`/`MovimientoStock` y pasa a tocar también la capa de Negocio de **Productos/Variantes** (alta de `VarianteProducto` con `ProductoId`, `PrecioVenta`, `StockMinimo`, `Color`, `TalleConfigId`). Esto debe evaluarse explícitamente en la etapa de Arquitectura (agente 3):
- Validar unicidad de la combinación Color+TalleConfigId dentro del mismo Producto antes de crear (evitar duplicados).
- Definir si la creación de variante desde Stock requiere el mismo nivel de permiso (`RequireAdministrador`, ya vigente) o si además debe quedar auditada como alta de catálogo (`AuditLog`), no solo como movimiento de stock.
- Confirmar si `CodigoInterno`/`CodigoBarra` quedan nulos al crear (el modelo ya los admite como `string?`, no bloquea el alta).

### Alcance funcional actualizado — Punto A (carga masiva)

**INCLUIDO:**
- Selección de una Marca completa (select2, mismo patrón de búsqueda que hoy) → grilla agrupada por Modelo, con todas las variantes existentes (Color×Talle) de cada Modelo de esa Marca.
- Cantidad nueva = stock resultante absoluto, editable por fila, solo para filas modificadas.
- Filas de combinaciones Talle×Color inexistentes se muestran igual (stock 0) con columnas adicionales editables: Precio de Venta y Stock Mínimo, para completar el alta de la variante en el mismo guardado.
- Guardado en lote: una acción dispara alta de variantes nuevas (si corresponde) + `AjusteStock`/`MovimientoStock` por cada variante con cantidad cargada, dentro de una transacción por fila (no todo-o-nada global: se informa qué filas se guardaron y cuáles no).
- Un único campo "Motivo" aplicado a todo el lote.
- Mismo permiso `RequireAdministrador`.

**NO INCLUIDO (salvo pedido explícito):** importación Excel/CSV; edición de Precio de Venta/Stock Mínimo de variantes ya existentes desde esta grilla (eso sigue siendo responsabilidad de Productos/Variantes); baja de variantes desde esta pantalla.

**Banderas actualizadas:** Migración EF: NO (entidades ya existen). Integración externa: NO. Máquina de estados: NO. **Nueva bandera: toca capa de Negocio de Productos/Variantes además de Stock** (impacto cross-módulo a validar en Arquitectura).
