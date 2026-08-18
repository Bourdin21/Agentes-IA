# Memoria - Analista funcional

## Proyecto: ShowroomGriffin
## Ultima actualizacion: 2026-08-16

## Definiciones vigentes

> Nota de consolidación (2026-08-16): este archivo no seguía la plantilla estándar del estudio (no tenía separación "Definiciones vigentes"/"Historial de ajustes") — tenía el análisis base v2 (2025-07) seguido de 3 secciones de nivel 2 apiladas por versión (V9, V10, V12). Se agregó la estructura estándar sin resumir ni tocar el contenido técnico; ver `## Historial de ajustes` al final para el resumen de una línea por versión.

### Decisiones validadas por el cliente

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

### Decisión clave adicional (por el cliente)

> **"Marcas y Modelos van a ser entidades anidadas. Subgrupos cambiar por Marcas y modelar nuevo esquema."**

#### Nuevo esquema de clasificación

```
Categoría (Indumentaria / Zapatillas / Accesorios)
  └── Marca  [renombrado desde Subgrupo]
        └── Modelo  [NUEVA entidad — hija de Marca]
                └── Producto  [CategoriaId + MarcaId + ModeloId]
                      └── VarianteProducto  [Color + Talle/Numero — SIN Marca ni Modelo]
```

---

### Alcance funcional v2

#### INCLUIDO

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

#### NO INCLUIDO
- Edición directa de Total o Subtotal por línea
- Impresión de anotaciones en remito
- Reportes por Empleado
- Integración con sistemas externos

#### DEPENDENCIAS
```
C10 → desbloquea C03, C05, C07
C11 → alimenta C03, C05 (combo talle)
C12 → requiere C10
C08 → requiere definir menú por rol
```

---

### Entidades nuevas y modificadas

#### RENOMBRADAS (semántica + labels)
- `Subgrupo` → `Marca` (tabla puede renombrarse `Marcas`)

#### MODIFICADAS
| Entidad | Antes | Después |
|---|---|---|
| `Producto` | CategoriaId, SubgrupoId | CategoriaId, MarcaId, ModeloId |
| `VarianteProducto` | Marca (str), Modelo (str), Talle/Numero (str libre) | SIN Marca/Modelo; TalleId FK a TalleConfig |

#### NUEVAS
| Entidad | Propiedades | Relación |
|---|---|---|
| `Modelo` | Id, Nombre, MarcaId | Hijo de Marca; padre de Producto |
| `TalleConfig` | Id, Valor (str), Tipo (enum) | FK en VarianteProducto.TalleId |

---

### Casos de uso principales

#### CU-01 · Alta de Venta con combos anidados
**Criterios de aceptación:**
- [ ] Al cambiar Categoría se resetean Marca, Modelo, Color, Talle
- [ ] Solo se muestran talles/colores con stock > 0
- [ ] Si no hay variante para la combinación, mensaje claro
- [ ] PrecioUnitario precargado desde VarianteProducto.PrecioVenta, editable
- [ ] Subtotal = PrecioUnitario × Cantidad (no editable)
- [ ] Total = Suma subtotales − Descuento (no editable)
- [ ] Autofill importe pago = Total − pagos ya agregados

#### CU-02 · Crear cliente rápido desde modal
**Criterios de aceptación:**
- [ ] Accesible para Vendedor y Empleado
- [ ] Nombre obligatorio; teléfono opcional
- [ ] Nuevo cliente queda seleccionado automáticamente en el Select2 de la venta
- [ ] Visible en módulo Clientes para completar datos después

#### CU-03 · Consulta rápida de stock
**Criterios de aceptación:**
- [ ] Rol Empleado puede acceder a /Stock/Index
- [ ] Filtros por Categoría, Marca, Modelo, Color, Talle
- [ ] Precio de costo oculto para Empleado y Vendedor
- [ ] Alerta visual en stock <= StockMinimo

#### CU-04 · Cambio/Devolución con búsqueda rápida
**Criterios de aceptación:**
- [ ] Búsqueda por fecha, nombre de cliente (parcial), descripción producto/variante
- [ ] Solo ventas Confirmada o Entregada
- [ ] Para cambio: selección con combos anidados (igual C03)
- [ ] Stock ajustado automáticamente y trazado en MovimientoStock

#### CU-05 · Rol Empleado
**Criterios de aceptación:**
- [ ] Puede crear y ver sus propias ventas
- [ ] Puede operar cambios/devoluciones
- [ ] Puede consultar stock (sin precio de costo)
- [ ] NO accede a: Compras, ABM Productos/Variantes, Configuración, Clientes ABM, Usuarios, Auditoría, Resumen semanal, Aumento masivo

---

### Validaciones clave

| Cambio | Validación |
|---|---|
| C01 Anotaciones | Texto libre, max 1000 chars, opcional |
| C02 Modal cliente | Nombre obligatorio; deduplicación por nombre+teléfono |
| C03/C05 Combos | Combinación Marca+Modelo+Color+Talle debe resolver VarianteProductoId existente |
| C07 Dev/Cambio | Venta Confirmada o Entregada; cantidad devuelta ≤ cantidad original |
| C10 Refactor | Migración: no dejar variantes huérfanas; backup previo |
| C11 TalleConfig | Talle debe pertenecer al catálogo de la categoría |

---

### Riesgos

| Riesgo | Mitigación |
|---|---|
| R1 — C10 es el cambio más invasivo | Backup + migración en 2 pasos (agregar columnas, luego quitar) |
| R2 — Combos sin stock confunden usuario | Solo mostrar talles/colores con stock > 0 |
| R3 — Solapamiento Empleado/Vendedor en permisos | Definir menú por rol explícitamente |
| R4 — BuscarVenta solo acepta ID exacto hoy | Ampliar con búsqueda multi-criterio |
| R5 — TalleConfig indumentaria: valores resueltos | ✅ XS, S, M, L, XL, XXL |

---

### C11a — Talles de Indumentaria ✅ RESUELTO

**Decisión confirmada — Opción A:** Solo talle por letra (adulto).  
Valores seed: `XS`, `S`, `M`, `L`, `XL`, `XXL`

#### Catálogo TalleConfig completo

| Tipo (enum) | Valores |
|---|---|
| `ZapatillaAdulto` | 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46 |
| `ZapatillaNino` | 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33 |
| `Indumentaria` | XS, S, M, L, XL, XXL |

---

### Banderas de implementación

| Flag | Estado |
|---|---|
| ✅ Requiere migración EF | SÍ — C01, C10, C11, C12 |
| ❌ Integración externa | NO |
| ✅ Máquina de estados impactada | SÍ — C07 (Confirmada + Entregada habilitan devolución) |
| ✅ Nuevo rol/policy | SÍ — C08 Empleado |
| ✅ Nuevas entidades de dominio | SÍ — Modelo, TalleConfig |
| ✅ Refactor entidad existente | SÍ — Subgrupo→Marca, VarianteProducto, Producto |

---

### V9 — Redirect post-ajuste de stock (2026-07-02) — Fast-path

**Pedido:** en la pantalla de ajuste manual de stock (`Stock/Ajuste`), tras cargar el ajuste de un producto, hoy redirige a `Stock/Index` (listado general). El usuario suele cargar ajustes de varios productos seguidos y quiere quedarse en la misma pantalla de ajuste tras guardar, en vez de volver al listado cada vez.

**Alcance:** cambiar el destino del `RedirectToAction` en el POST `StockController.Ajuste` de `Index` a `Ajuste` (GET), limpiando el formulario para el próximo ajuste.

**Fuera de alcance:** no cambia validaciones, permisos (`RequireAdministrador`), lógica de `AjusteManualAsync`, ni el modelo `AjusteStockViewModel`.

**Criterio de aceptación:** al guardar un ajuste válido desde `Stock/Ajuste`, la respuesta redirige (GET) a `Stock/Ajuste` con `TempData["Success"]` mostrando el mensaje de confirmación, y el formulario queda listo para cargar el siguiente producto.

**Banderas:** sin migración EF, sin cambio de permisos, sin nueva entidad. Riesgo: bajo.

---

### V10 — Carga masiva de stock por Modelo + filtros completos en Consulta de Stock (2026-07-30) — EN DISCOVERY

**Estado:** análisis inicial entregado, pendiente de respuestas del cliente (Q1–Q7) y aprobación para pasar a Diseño.

**Pedido del cliente:** "es muy tedioso cargar el stock por modelo, por talle, por color, y cada talle cargarlo individualmente" (sobre `/Stock/Ajuste`, hoy 1 variante por vez vía select2 + `CantidadNueva` + submit). Además: "los filtros en la pantalla de consulta de stock tienen que tener todas las propiedades del stock que se lista" (sobre `/Stock/Index`).

#### Punto A — Carga masiva de stock (Ajuste Manual)

**Incluido (hipótesis de alcance):**
- Nuevo modo de carga: elegir un Modelo → grilla con todas sus variantes existentes (Color × Talle) con stock actual editable inline.
- Guardado en lote: un submit dispara N `AjusteStock` + `MovimientoStock` (uno por variante modificada), reutilizando `AjusteManualAsync` fila a fila dentro de una operación de conjunto.
- Filas sin cambios no generan movimiento. Convive con el ajuste individual actual (no lo reemplaza).
- Mismo permiso `RequireAdministrador` que hoy.

**No incluido (salvo pedido explícito):** alta de variantes nuevas (combinaciones Talle×Color inexistentes) desde esta pantalla; carga cruzando múltiples modelos a la vez; importación Excel/CSV.

**Riesgos:** volumen de filas por modelo (posible necesidad de paginar/virtualizar la grilla); concurrencia por fila (`RowVersion` de `VarianteProducto` debe seguir chequeándose individualmente, no solo a nivel de página); trazabilidad del motivo si se agrupa en un solo campo por lote.

#### Punto B — Filtros completos en Consulta de Stock

**Incluido (hipótesis de alcance):**
- Agregar filtro por Talle (dependiente de Modelo, mismo patrón que Color).
- Integrar "Solo alertas" (hoy botón que recarga toda la página) como filtro "Estado" (Todos/OK/Límite/Bajo) dentro de la barra de filtros cascada, vía AJAX igual que el resto.
- Código ya cubierto por búsqueda global de DataTables; Stock/Mínimo/Déficit son columnas ordenables, no filtros (a confirmar en Q7).

**Riesgo:** si se agrega filtro Talle, hay que sumarlo también a `ExportarExcelAsync` (hoy solo recibe marcaId/modeloId/color) para mantener consistencia entre grilla y export.

#### Banderas tempranas
- Migración EF: NO. Integración externa: NO. Máquina de estados: NO.

#### Preguntas abiertas — hipótesis a validar con el cliente

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

#### Decisiones confirmadas por el cliente (2026-07-30)

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

#### Replanteo de alcance tras Q3/Q3a — ALERTA para Arquitectura

La decisión Q3 (crear variantes al vuelo) **amplía el alcance real del Punto A**: deja de ser un cambio acotado a `Stock`/`AjusteStock`/`MovimientoStock` y pasa a tocar también la capa de Negocio de **Productos/Variantes** (alta de `VarianteProducto` con `ProductoId`, `PrecioVenta`, `StockMinimo`, `Color`, `TalleConfigId`). Esto debe evaluarse explícitamente en la etapa de Arquitectura (agente 3):
- Validar unicidad de la combinación Color+TalleConfigId dentro del mismo Producto antes de crear (evitar duplicados).
- Definir si la creación de variante desde Stock requiere el mismo nivel de permiso (`RequireAdministrador`, ya vigente) o si además debe quedar auditada como alta de catálogo (`AuditLog`), no solo como movimiento de stock.
- Confirmar si `CodigoInterno`/`CodigoBarra` quedan nulos al crear (el modelo ya los admite como `string?`, no bloquea el alta).

#### Alcance funcional actualizado — Punto A (carga masiva)

**INCLUIDO:**
- Selección de una Marca completa (select2, mismo patrón de búsqueda que hoy) → grilla agrupada por Modelo, con todas las variantes existentes (Color×Talle) de cada Modelo de esa Marca.
- Cantidad nueva = stock resultante absoluto, editable por fila, solo para filas modificadas.
- Filas de combinaciones Talle×Color inexistentes se muestran igual (stock 0) con columnas adicionales editables: Precio de Venta y Stock Mínimo, para completar el alta de la variante en el mismo guardado.
- Guardado en lote: una acción dispara alta de variantes nuevas (si corresponde) + `AjusteStock`/`MovimientoStock` por cada variante con cantidad cargada, dentro de una transacción por fila (no todo-o-nada global: se informa qué filas se guardaron y cuáles no).
- Un único campo "Motivo" aplicado a todo el lote.
- Mismo permiso `RequireAdministrador`.

**NO INCLUIDO (salvo pedido explícito):** importación Excel/CSV; edición de Precio de Venta/Stock Mínimo de variantes ya existentes desde esta grilla (eso sigue siendo responsabilidad de Productos/Variantes); baja de variantes desde esta pantalla.

**Banderas actualizadas:** Migración EF: NO (entidades ya existen). Integración externa: NO. Máquina de estados: NO. **Nueva bandera: toca capa de Negocio de Productos/Variantes además de Stock** (impacto cross-módulo a validar en Arquitectura).

---

### V12 — Extensión de Vista Matriz: accesorios sin talle + alta de Color nuevo, con vistas a retirar Carga Masiva y Ajuste Manual (2026-08-16) — DISCOVERY + ANÁLISIS

**Nota de contexto:** la Vista Matriz (Marca → Modelo → Color × Talle) nunca pasó formalmente por Discovery/Análisis/Diseño — se construyó en 3 etapas fast-path (`022bd07`, `06bb253`, `0eba0fc`, ver `trazabilidad.md` 2026-08-11) más 4 ajustes puntuales posteriores (menú principal, stock 0 editable, aviso de guardado, alta desde celda vacía — este último con un hotfix el mismo 2026-08-16 tras rechazo de QA, ver `6-qa.md` sección "Barrido QA post-V10"). Esta es la primera vez que una extensión de la Matriz pasa por el flujo completo del estudio, a partir de la lección del rechazo de QA: *"si un cambio agrega un ViewModel nuevo con binding de formulario, sale del fast-path"*.

#### Pedido del cliente

Tras un repaso de gaps/bugs pendientes, dos hallazgos quedaron para resolver:
1. La Matriz (hoy pantalla principal de Stock) **excluye por completo los Modelos sin sistema de Talle** (accesorios: bijou, carteras, etc.) — `StockService.ObtenerMatrizAsync` descarta la sección cuando `TalleConfig.Tipo == null`. Hoy la única forma de tocar el stock de un accesorio es `/Stock/CargaMasiva` (Talle opcional ahí) o `/Stock/Ajuste` (variante por variante).
2. La Matriz editable (`MatrizEditar`) solo permite completar un **Talle faltante en un Color que ya existe** como fila (celda "—"). No hay forma de dar de alta un **Color completamente nuevo** para un Modelo — eso también depende de `/Stock/CargaMasiva`.

**Objetivo final del cliente:** una vez que la Matriz cubra ambos casos, **retirar del menú `/Stock/CargaMasiva` y `/Stock/Ajuste`** — ambas pantallas de carga variante-por-variante o grilla separada que el cliente calificó de tediosas, y que hoy solo se mantienen porque cubren estos dos huecos de la Matriz.

#### Contexto y objetivo

Consolidar **una única pantalla** (la Matriz editable) como el punto de entrada completo para gestionar stock — talle o sin talle, variante existente o nueva, Color existente o nuevo — eliminando la necesidad de dos pantallas paralelas con lógica muy similar (`CargaMasiva` y `MatrizEditar` ya comparten el mismo patrón de guardado parcial fila-por-fila, `IVarianteService.CrearAsync` para altas, y `AplicarAjusteInternoAsync` para el ajuste de stock — la duplicación de lógica entre ambas pantallas es hoy un costo de mantenimiento real, agravado por el bug D-01/D-02 recién corregido en una de las dos implementaciones paralelas).

#### Alcance inicial — incluido

- **Accesorios sin talle en la Matriz (lectura y edición):** los Modelos con `TipoTalle == null` pasan a mostrarse como una sección sin columnas de Talle — una fila por Color con una única celda "Cantidad" (en vez del pivot Talle×Color). Aplica tanto a `Matriz.cshtml` (solo lectura) como a `MatrizEditar.cshtml` (edición).
- **Alta de Color nuevo desde la Matriz editable:** cada sección de Modelo (con o sin sistema de Talle) agrega una forma de cargar un Color que todavía no tiene ninguna variante — mismos datos que ya pide la alta-desde-celda-vacía actual (Color, Talle si el Modelo lo usa, Precio de Venta, Stock Mínimo, cantidad inicial), reutilizando `StockMatrizAltaGuardarViewModel`/`GuardarMatrizAsync` ya existentes (extender, no reemplazar).
- **Retiro de `/Stock/CargaMasiva` y `/Stock/Ajuste`** del menú y de los botones de acceso en `Stock/Index.cshtml`, una vez validado que la Matriz cubre el 100% de los casos de uso de ambas.

#### Alcance inicial — no incluido (salvo pedido explícito)

- Importación masiva por Excel/CSV (no existía en ninguna de las dos pantallas a retirar).
- Baja de variantes/Colores desde la Matriz (sigue siendo responsabilidad de Productos/Variantes).
- Migración de datos históricos: no aplica, no hay cambio de esquema previsto en esta etapa (a confirmar en Arquitectura).
- Eliminación física del código de `CargaMasiva`/`Ajuste` (ver pregunta D3 abajo — el alcance de "retirar" es una decisión a confirmar).

#### Actores, permisos y reglas críticas heredadas

- Edición de Matriz: `RequireAdministrador` (ya vigente, sin cambios).
- Lectura de Matriz: `RequireEmpleado` (ya vigente).
- Reutiliza sin modificar: `IVarianteService.CrearAsync` (alta de variante), `StockService.AplicarAjusteInternoAsync` (ajuste sin transacción propia, para participar de la transacción por fila), el patrón de deduplicación Color+Talle ya usado en `GuardarCargaMasivaAsync`/`GuardarMatrizAsync`, y ahora también el **índice único `(ProductoId, Color, TalleConfigId)`** agregado el 2026-08-16 (OBS-V10-02) como respaldo de base de datos ante cualquier condición de carrera que la validación aplicativa no cubra.

#### Supuestos y dependencias

- El catálogo de accesorios (Modelos con `TipoTalle == null`) ya existe en producción con variantes reales — no requiere altas de catálogo previas.
- No hay lógica de precios/impuestos distinta para accesorios vs. calzado — mismo `VarianteProducto.PrecioVenta`/`StockMinimo`.
- El patrón de guardado parcial (transacción por fila, `ChangeTracker.Clear()` tras cada rollback — fix D-03 del 2026-08-16) ya es la base común a reutilizar; no se introduce un mecanismo nuevo.

#### Riesgos tempranos

- **R1 (medio):** la fila de "alta de Color nuevo" necesita, para Modelos CON sistema de Talle, un input por cada columna de Talle de esa sección (igual que hoy hace `CargaMasiva.cshtml` para una variante nueva, pero ahí es una fila plana, no una fila dentro de una tabla pivot ya angosta). El layout debe decidirse en Diseño — es la pieza de UI más nueva de esta feature, sin precedente exacto dentro del proyecto.
- **R2 (bajo):** al fusionar dos flujos de alta (uno para Talle faltante en Color existente, otro para Color nuevo) en el mismo `StockMatrizAltaGuardarViewModel`, hay que asegurar que la view los indexe sin colisión (mismo criterio que ya reveló el bug D-01: cualquier ViewModel nuevo con binding de formulario dinámico debe revisarse contra nulabilidad + cultura antes de cerrar Implementación).
- **R3 (bajo, de proceso):** dado que el rechazo de QA fue justo sobre este tipo de cambio (grilla dinámica + ViewModel con binding), esta feature **no debe tratarse como fast-path** — de ahí que el cliente haya pedido explícitamente pasar por el orquestador completo.
- **R4 (a resolver en Arquitectura):** confirmar si "retirar" `CargaMasiva`/`Ajuste` implica eliminar el código (controllers, vistas, métodos de servicio) o solo ocultar el acceso — impacta el checklist de QA de regresión (si se elimina código, hay que confirmar que nada más lo referencia).

#### Preguntas abiertas — antes de pasar a Diseño

| # | Pregunta | Opción A (hipótesis, recomendada) | Opción B |
|---|---|---|---|
| D1 | Layout de la sección de accesorios (sin Talle) | Una tabla simple: Color + una columna "Cantidad" (sin pivot), igual espíritu visual que las secciones con Talle pero con una sola columna | Reutilizar la tabla pivot con una única columna genérica "—" (menos consistente visualmente) |
| D2 | Layout del alta de Color nuevo en Modelos con Talle | Una fila extra al final de cada sección con un input de Color + un input de cantidad por cada columna de Talle (mismo patrón que la fila "+ Agregar variante nueva" de Carga Masiva, pero embebida en la tabla pivot) | Un modal separado por Modelo que pide Color + Talle + cantidad + Precio + Stock Mínimo de a una combinación por vez |
| D3 | Alcance de "retirar" Carga Masiva y Ajuste Manual | **Ocultar** del menú y de los botones de `Stock/Index` (reversible, bajo riesgo) — el código queda pero inaccesible por UI hasta una limpieza posterior confirmada | **Eliminar** controllers/vistas/métodos de servicio en el mismo sprint (mayor alcance, requiere confirmar que nada más los referencia) |
| D4 | Momento del retiro | Recién después de que el cliente confirme en producción que la Matriz cubre ambos casos (accesorios + Color nuevo) sin problemas — dos entregas separadas | Retirar en el mismo sprint que la extensión, sin período de validación intermedio |

**Gate:** no iniciar Diseño (agente 2) hasta que el cliente resuelva D1–D4 (o confirme las hipótesis recomendadas) y apruebe el alcance.

#### Decisiones confirmadas por el cliente (2026-08-16)

| # | Pregunta | Decisión confirmada |
|---|---|---|
| D1 | Layout de accesorios (sin Talle) | **A — Tabla simple: Color + una columna "Cantidad"**, sin pivot |
| D2 | Layout del alta de Color nuevo | **A — Fila extra al final de la tabla pivot**, un input de Color + un input de cantidad por columna de Talle, mismo espíritu que "+ Agregar variante nueva" de Carga Masiva pero embebido en la grilla |
| D3 | Alcance de "retirar" Carga Masiva y Ajuste Manual | **A — Solo ocultar del menú** y de los botones de `Stock/Index` (reversible, bajo riesgo); el código de `CargaMasiva`/`Ajuste` queda intacto para una limpieza posterior confirmada, no se borra en este sprint |
| D4 | Momento del retiro | **B — Todo en el mismo sprint**: se extiende la Matriz y se ocultan ambas pantallas en la misma entrega, sin período de validación intermedio en producción |

**ANÁLISIS V12 CERRADO Y APROBADO.** Listo para Diseño (agente 2).

## Historial de ajustes
- 2025-07: Análisis funcional v2 cerrado — decisiones validadas con el cliente, alcance funcional, entidades nuevas/modificadas, casos de uso principales, validaciones clave, riesgos, C11a (talles de indumentaria) resuelto, banderas de implementación.
- 2026-07-02: V9 — Redirect post-ajuste de stock (fast-path).
- 2026-07-30: V10 — Carga masiva de stock por Modelo + filtros completos en Consulta de Stock.
- 2026-08-16: V12 — Extensión de Vista Matriz (accesorios sin talle + alta de Color nuevo), con retiro (oculto, no borrado) de Carga Masiva y Ajuste Manual.
- 2026-08-16: Reestructuración documental — este archivo no seguía la plantilla estándar del estudio. Se agregó el encabezado `## Proyecto:`/`## Ultima actualizacion:`/`## Definiciones vigentes` y este historial, sin tocar el contenido técnico existente (solo se bajó un nivel cada encabezado para que todo quede bajo un único `## Definiciones vigentes`).
