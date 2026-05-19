# Análisis de Impacto — ShowroomGriffin v2
**Fecha:** 2025-07  
**Analista:** Agente Funcional Senior  
**Base:** Codebase actual en `C:\Sistemas\ShowroomGriffin` (rama `main`)

---

## Resumen ejecutivo

Se analizaron **12 solicitudes de cambio** contra el estado real de la solución.  
Se identificaron **3 cambios críticos** (refactor estructural con migración EF + cascada de impacto), **5 cambios medios** (nuevas funcionalidades acotadas) y **4 cambios leves** (UI/config sin migración de datos).

---

## Mapa de impacto por cambio

---

### C01 · Agregar campo `Anotaciones` en Venta

**Impacto:** LEVE  
**Banderas:** ✅ Requiere migración EF · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
`Venta.cs` ya tiene `Observaciones` (string nullable). El campo `Anotaciones` es **adicional** (no reemplaza).

#### Capas afectadas
| Capa | Cambio |
|---|---|
| Domain | Agregar `public string? Anotaciones { get; set; }` en `Venta.cs` |
| Application | Agregar `Anotaciones` en `VentaCreateViewModel` y `VentaDetalleViewModel` |
| Infrastructure | Nueva migración EF (columna nullable, sin ruptura) |
| Web | Mostrar campo en vista `Crear.cshtml` y `Detalle.cshtml` de ventas |

#### Preguntas abiertas
1. ¿`Anotaciones` es visible para el cliente (ej.: nota para remito) o es una nota interna del vendedor?  
   - **Hipótesis A (validar):** es una nota interna, no aparece en remito ni en historial del cliente.  
   - **Hipótesis B (validar):** es una nota que puede imprimirse junto al remito.
2. ¿Tienen distinto propósito `Observaciones` y `Anotaciones` o se pueden unificar?

---

### C02 · Crear cliente desde modal en Alta/Edición de Venta

**Impacto:** MEDIO  
**Banderas:** ❌ Migración EF · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
- `ClientesController.Crear` (GET y POST) está decorado con `[Authorize(Policy = "RequireAdministrador")]`.
- `VentasController` opera con `[Authorize(Policy = "RequireVendedor")]` (incluye Vendedor, Administrador, SuperUsuario).
- El flujo actual de venta no expone ningún endpoint AJAX para crear cliente.

#### Problema de autorización
Un vendedor actualmente **no puede** crear clientes. Si se quiere que un vendedor cree clientes desde el modal de venta, hay dos opciones:

- **Hipótesis A (validar):** Agregar un endpoint `POST /Clientes/CrearRapido` con política `RequireVendedor`, limitado a nombre y teléfono (campos mínimos). El cliente completo (CUIT, dirección) sólo lo completa el Administrador.  
- **Hipótesis B (validar):** El modal sólo está disponible para Administrador/SuperUsuario. El Vendedor debe seleccionar un cliente existente o dejar la venta sin cliente.

#### Capas afectadas
| Capa | Cambio |
|---|---|
| Application | Nuevo método `CrearRapidoAsync` en `IClienteService` (si se elige Hipótesis A) |
| Infrastructure | Implementación del método en `ClienteService` |
| Web | Nuevo endpoint AJAX en `ClientesController`; modal Bootstrap en vista `Crear` de ventas; JavaScript para inyectar el nuevo clienteId en el Select2 |

---

### C03 · Combos anidados Marca → Modelo → Color → Talle en Ventas

**Impacto:** CRÍTICO (acoplado a C10)  
**Banderas:** ✅ Requiere migración EF (C10) · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
- `IVarianteService.BuscarAsync(term)` expone búsqueda de texto libre. No hay endpoints de combos cascadeados.
- `Marca` y `Modelo` están en `VarianteProducto`, NO en `Producto`. Mientras C10 no se implemente, los combos deben derivarse desde variantes, no desde productos.
- `VentaCreateViewModel.Items` usa directamente `VarianteId` — la UI actual selecciona la variante con un Select2 de texto libre.

#### Dependencia con C10
Si C10 (mover Marca/Modelo a Producto) se implementa **antes**, los combos quedan:  
`Categoría (Producto.CategoriaId)` → `Marca (Producto.SubgrupoId o nuevo campo)` → `Modelo (Producto.Modelo)` → `Color (Variante.Color)` → `Talle (Variante.Talle)`

Si C10 **no** se implementa, los combos se arman desde variantes con agrupamiento:  
`Marca (Variante.Marca)` → `Modelo (Variante.Modelo)` → `Color (Variante.Color)` → `Talle (Variante.Talle)`

#### Capas afectadas
| Capa | Cambio |
|---|---|
| Application | Nuevos métodos en `IVarianteService`: `ObtenerMarcasAsync()`, `ObtenerModelosPorMarcaAsync(marca)`, `ObtenerColoresPorModeloAsync(marca, modelo)`, `ObtenerTallesPorModeloColorAsync(marca, modelo, color)`, `ObtenerVarianteAsync(marca, modelo, color, talle)` |
| Infrastructure | Implementación en `VarianteService` con queries LINQ agrupados |
| Web | 4 nuevos endpoints AJAX en `VariantesController`; reemplazar Select2 de texto libre en vista Crear de ventas por 4 `<select>` anidados con JS |

#### Preguntas abiertas
3. ¿El combo de marca es la misma entidad `Subgrupo` o es el campo libre `Variante.Marca`?  
   - **Hipótesis A (validar):** Marca = `Subgrupo`. El combo carga los subgrupos de la categoría seleccionada.  
   - **Hipótesis B (validar):** Marca sigue siendo texto libre en variante hasta que se haga C10.
4. ¿El orden de los combos es siempre Marca → Modelo → Color → Talle, o varía según categoría (ej: Indumentaria podría ser Color → Talle sin Modelo)?

---

### C04 · Autocompletar importe de pago con el total de la venta

**Impacto:** LEVE  
**Banderas:** ❌ Migración EF · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
- El total de la venta se calcula en el front (sumatoria de líneas menos descuento).
- `VentaPagoItemViewModel.Importe` es ingresado manualmente.
- No hay ningún mecanismo de prellenado.

#### Capas afectadas
| Capa | Cambio |
|---|---|
| Web (JS) | Al abrir el modal de "Agregar Pago", calcular el saldo pendiente (Total − suma de pagos ya cargados) e inyectarlo como valor por defecto en el campo `Importe`. Cambio 100% front-end. |

#### Preguntas abiertas
5. Si hay múltiples pagos (ej: parte en efectivo, parte en tarjeta), ¿el autocompletado debe sugerir el **saldo restante** después de los pagos ya agregados, o siempre el **total completo**?  
   - **Hipótesis A (validar):** sugiere saldo restante (Total − pagos previos ya en la lista).  
   - **Hipótesis B (validar):** siempre sugiere el total completo y el usuario lo ajusta.

---

### C05 · Combos anidados en Compras (misma lógica que C03)

**Impacto:** MEDIO (acoplado a C03 y C10)  
**Banderas:** ✅ Migración EF (C10) · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
- `CompraDetalleItemViewModel` usa `VarianteId` directamente.
- `ComprasController` no tiene endpoints de combos anidados.

#### Capas afectadas
Idénticas a C03 (los endpoints AJAX son reutilizables). Solo requiere adaptar la vista `Crear.cshtml` de compras para usar el mismo componente de 4 combos.

---

### C06 · Pantalla de consulta rápida de stock

**Impacto:** LEVE  
**Banderas:** ❌ Migración EF · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
- `StockController.Index` ya existe con filtro `soloAlertas` y DataTable.
- `IStockService.ListarAsync` ya devuelve stock paginado.
- La pantalla actual es funcional pero es la misma pantalla de gestión de stock (con ajustes y carga inicial).

#### Preguntas abiertas
6. ¿"Consulta rápida" implica una **nueva vista simplificada** (solo lectura, sin botones de ajuste), o es la misma `StockController/Index` con acceso habilitado para el rol Empleado (C08)?  
   - **Hipótesis A (validar):** nueva vista `/Stock/Consulta` de solo lectura, accesible para Empleado, con filtros por categoría/marca/talle y sin botones de acción.  
   - **Hipótesis B (validar):** la vista `Index` existente ya sirve; solo se necesita ajustar el rol de acceso en C08.
7. ¿Debe mostrar el precio de costo? (actualmente en la vista de stock está visible sólo para Admin)

---

### C07 · Cambios/Devoluciones desde detalle de venta finalizada con búsqueda rápida

**Impacto:** MEDIO  
**Banderas:** ❌ Migración EF · ❌ Integración externa · ✅ Máquina de estados (venta Entregada/Confirmada)

#### Hallazgo en codebase
- `DevolucionesController` ya existe con `Crear`, `BuscarVenta(ventaId)`, `Detalle`.
- `BuscarVenta` sólo acepta `ventaId` (número exacto). **No hay búsqueda por fecha, cliente o producto.**
- `DevolucionCreateViewModel` no tiene campo para búsqueda de venta, sólo `VentaId`.
- El flujo actual requiere saber el ID exacto de la venta.
- `IDevolucionService.ObtenerVentaParaDevolucionAsync` no filtra por estado — se desconoce si restringe a ventas `Confirmada`/`Entregada`.
- La entidad `DevolucionCambio` ya admite `NuevaVarianteProductoId` (para cambio de producto).

#### Capas afectadas
| Capa | Cambio |
|---|---|
| Application | Nuevo método `BuscarVentasAsync(fecha?, clienteId?, varianteId?)` en `IDevolucionService` (o reutilizar `IVentaService.ListarAsync` con filtros ampliados) |
| Infrastructure | Query de búsqueda multi-criterio en `DevolucionService` |
| Web | Ampliar vista `Crear` de devoluciones con buscador por fecha/cliente/producto antes de seleccionar la venta; botón de acceso directo desde `Ventas/Detalle` cuando la venta está en estado `Confirmada` o `Entregada` |

#### Preguntas abiertas
8. ¿El cambio/devolución puede hacerse desde ventas en estado `Confirmada` o sólo `Entregada`?  
   - **Hipótesis A (validar):** solo `Entregada` (la mercadería ya salió del local).  
   - **Hipótesis B (validar):** también `Confirmada` (el cliente puede arrepentirse antes de retirar).
9. Cuando el usuario hace "cambio", ¿la nueva variante debe poder seleccionarse también con combos anidados (igual que C03)?

---

### C08 · Rol Empleado con acceso restringido a Ventas / Cambios / Stock

**Impacto:** MEDIO  
**Banderas:** ❌ Migración EF · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
- `SeedData.cs` define 3 roles: `SuperUsuario`, `Administrador`, `Vendedor`. **No existe `Empleado`.**
- `Program.cs` define 4 policies: `RequireSuperUsuario`, `RequireAdministracion`, `RequireAdministrador`, `RequireVendedor`.
- Los controllers `VentasController`, `DevolucionesController`, `StockController` usan `RequireVendedor` (que incluye Vendedor + Admin + SuperUsuario).

#### Diferencia Vendedor vs Empleado
Es necesario definir claramente si `Empleado` es más restrictivo que `Vendedor`:

| Funcionalidad | Vendedor (actual) | Empleado (propuesto) |
|---|---|---|
| Crear ventas | ✅ | ✅ |
| Ver todas las ventas | ❌ (solo las propias) | ❓ |
| Anular ventas | ✅ | ❓ |
| Cambios/Devoluciones | ✅ | ✅ |
| Stock (solo consulta) | ✅ (con ajuste si Admin) | ✅ (solo lectura) |
| Compras | ❌ (solo Admin) | ❌ |
| Productos/Variantes | ✅ (solo lectura) | ❓ |
| Clientes | ✅ (solo lectura) | ❓ |

#### Capas afectadas
| Capa | Cambio |
|---|---|
| Infrastructure/Data | Agregar `RolEmpleado = "Empleado"` en `SeedData` y seed del rol en `InitializeAsync` |
| Web | Nueva policy `RequireEmpleado` en `Program.cs`; revisar decoradores `[Authorize]` en `VentasController`, `DevolucionesController`, `StockController`; ajustar menú de navegación por rol |

#### Preguntas abiertas
10. ¿Un `Empleado` puede **crear** ventas o sólo visualizarlas?  
	- **Hipótesis A (validar):** puede crear y cobrar ventas (es básicamente un Vendedor restringido).  
	- **Hipótesis B (validar):** sólo puede ver ventas y hacer cambios/devoluciones; no puede crear nuevas ventas.

---

### C09 · Importes de venta calculados automáticamente pero editables (PrecioUnitario, Subtotal, Total)

**Impacto:** LEVE-MEDIO  
**Banderas:** ❌ Migración EF · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
- `VentaDetalleItemViewModel` ya tiene `PrecioUnitario` editable.
- `VentaCreateViewModel` tiene `DescuentoPorcentaje` pero **no** `DescuentoMonto` editable por el usuario.
- El subtotal y total actuales son calculados en el service (`VentaService.CrearAsync`) a partir de las líneas enviadas.
- No hay un `Subtotal` por línea en `VentaDetalleItemViewModel` (sólo `PrecioUnitario` × `Cantidad`).

#### Capas afectadas
| Capa | Cambio |
|---|---|
| Application | Agregar `Subtotal` en `VentaDetalleItemViewModel` (enviado desde el front) o mantenerlo calculado en service — definir qué gana prioridad |
| Web (JS) | Al modificar `PrecioUnitario` o `Cantidad`, recalcular automáticamente `Subtotal` de la línea y el `Total` de la venta; todos los campos deben ser editables (no read-only) |

#### Preguntas abiertas
11. Si el usuario edita manualmente el `Subtotal` de una línea (sin cambiar el precio ni la cantidad), ¿eso implica un descuento implícito en esa línea, o es un error de validación?  
	- **Hipótesis A (validar):** el `Subtotal` no es editable directamente; sólo lo son `PrecioUnitario` y `Cantidad`.  
	- **Hipótesis B (validar):** el `Subtotal` también es editable y genera automáticamente un `PrecioUnitario` calculado = Subtotal / Cantidad.
12. ¿El `Total` final puede ser editado directamente (ej: negocio con cliente "te dejo en $X")? Si es así, ¿se ajusta como descuento de monto?

---

### C10 · Refactor entidad VARIANTE: quitar Marca y Modelo; pasarlos a PRODUCTO

**Impacto:** CRÍTICO  
**Banderas:** ✅ Requiere migración EF · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
Actualmente:
- `VarianteProducto`: tiene `Marca` (string?), `Modelo` (string?) y `Numero` (zapatillas).
- `Producto`: tiene `Nombre`, `CategoriaId`, `SubgrupoId`. **No tiene Marca ni Modelo.**
- `VarianteViewModel` tiene `Marca` y `Modelo` con validaciones `[MaxLength]`.
- `EsCalzado` en `VarianteViewModel` depende de `CategoriaNombre` (ok, no se mueve).

#### Cascada de impacto
| Artefacto | Cambio requerido |
|---|---|
| `VarianteProducto.cs` | Eliminar propiedades `Marca` y `Modelo` |
| `Producto.cs` | Agregar `Marca` (string? o FK) y `Modelo` (string?) |
| `VarianteViewModel` | Quitar `Marca` y `Modelo` |
| `ProductoViewModel` | Agregar `Marca` y `Modelo` |
| `ProductoService` | Persistir/recuperar Marca y Modelo |
| `VarianteService` | Quitar Marca/Modelo de queries y filtros |
| `BuscarAsync` en variantes | Ya no filtra por Marca/Modelo directamente |
| Migración EF | Mover columnas de tabla `VarianteProductos` a tabla `Productos` — **con script de datos para preservar valores existentes** |
| Vistas de Variantes | Quitar campos Marca/Modelo del formulario de variante |
| Vistas de Productos | Agregar campos Marca/Modelo al formulario de producto |
| Combos C03/C05 | Ahora Marca y Modelo se leerán desde `Productos` en lugar de `VarianteProductos` |

#### Riesgo alto
- Si existen variantes de un mismo producto con distintas marcas o modelos actualmente en la DB, el refactor requiere una estrategia de consolidación de datos (qué Marca/Modelo "gana" para el producto padre).
- La migración debe incluir un script SQL de migración de datos, no sólo DDL.

#### Preguntas abiertas
13. ¿Todos los productos actualmente en la DB tienen las mismas Marca y Modelo en todas sus variantes, o puede haber inconsistencias (ej: variantes del mismo producto con distintas marcas)?
14. ¿`Marca` en `Producto` será texto libre o una FK a la entidad `Subgrupo` (que ya existe como "marca" según la taxonomía definida)?  
	- **Hipótesis A (validar):** `Producto.SubgrupoId` ya representa la Marca (Subgrupo = Marca). Solo hay que quitar el campo de variante y asegurarse de que el Subgrupo se llene correctamente.  
	- **Hipótesis B (validar):** `Marca` en Producto es un campo de texto libre adicional al Subgrupo (double-track).

---

### C11 · Talles de zapatillas configurados de antemano (Adultos 34–46, Niños 22–33)

**Impacto:** MEDIO  
**Banderas:** ✅ Requiere migración EF · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
- `VarianteProducto.Talle` es `string?` libre.
- `VarianteProducto.Numero` es `string?` libre (usado para número de zapatilla).
- Existe la entidad `TipoPrecioZapatilla` (con FK en `VarianteProducto.TipoPrecioZapatillaId`), lo que indica que ya hay conceptos de configuración de zapatillas.
- No existe entidad `TalleConfig` ni tabla de talles predefinidos.

#### Opciones de diseño
- **Hipótesis A (validar):** Nueva entidad `TalleConfig` con campos `Numero` (int), `Rango` (enum: Adulto/Niño), seeded con 22–33 (Niño) y 34–46 (Adulto). El campo `VarianteProducto.Numero` pasa a ser FK a esta entidad.  
- **Hipótesis B (validar):** Sin nueva entidad. Se hace seed de valores en una tabla de lookup simple y el campo `Numero` en variante se valida contra ese rango (sin FK, solo validación).

#### Capas afectadas
| Capa | Cambio |
|---|---|
| Domain | Nueva entidad `TalleConfig` (si Hipótesis A) |
| Application | ViewModel para selector de talle (dropdown con valores del seed) |
| Infrastructure | Migración + seed de talles 22–46 |
| Web | Reemplazar campo de texto libre por `<select>` en formulario de variante de zapatilla |

#### Preguntas abiertas
15. ¿Los talles de indumentaria (ropa) también deben ser predefinidos (ej: XS/S/M/L/XL/XXL, o 1/2/4/6/8...) o siguen siendo texto libre?

---

### C12 · Taxonomía fija: Categorías = Indumentaria/Zapatillas/Accesorios; Subgrupos = Marcas; Variantes = Modelo/Color/Talle

**Impacto:** LEVE (datos/seed) + MEDIO (labels en UI)  
**Banderas:** ❌ Migración EF (solo seed) · ❌ Integración externa · ❌ Máquina de estados

#### Hallazgo en codebase
- `Categoria.Nombre` es texto libre; no hay categorías seeded actualmente (o las existentes no están auditadas aquí).
- `Subgrupo.Nombre` es texto libre con FK a Categoría.
- Las vistas probablemente dicen "Subgrupo" donde debería decir "Marca".

#### Capas afectadas
| Capa | Cambio |
|---|---|
| Infrastructure/Data | Seed de categorías: Indumentaria, Zapatillas, Accesorios |
| Web | Renombrar labels "Subgrupo" → "Marca" en vistas de Productos, Variantes, y filtros |
| Web | Lógica de formulario dinámico de variante: si `Categoría = Zapatillas`, mostrar combo de talles predefinidos (C11); si `Categoría = Indumentaria`, mostrar Talle libre o combo de talles de ropa |

---

## Matriz de prioridad e impacto

| # | Cambio | Complejidad | Migración EF | Prioridad sugerida |
|---|---|---|---|---|
| C10 | Refactor Marca/Modelo → Producto | 🔴 Alta | ✅ Sí | **Primero (bloquea C03/C05)** |
| C11 | Talles predefinidos zapatillas | 🟡 Media | ✅ Sí | Segundo (antes de UI de combos) |
| C03 | Combos anidados en Ventas | 🟡 Media | ❌ | Tercero |
| C05 | Combos anidados en Compras | 🟡 Media | ❌ | Cuarto (reutiliza C03) |
| C08 | Rol Empleado | 🟡 Media | ❌ | Independiente |
| C07 | Búsqueda rápida Cambios/Dev. | 🟡 Media | ❌ | Independiente |
| C02 | Crear cliente desde modal | 🟡 Media | ❌ | Independiente |
| C09 | Importes editables | 🟢 Baja | ❌ | Independiente |
| C12 | Taxonomía seed + labels | 🟢 Baja | ❌ | Independiente |
| C06 | Pantalla consulta stock | 🟢 Baja | ❌ | Independiente |
| C01 | Campo Anotaciones en venta | 🟢 Baja | ✅ Sí | Independiente |
| C04 | Autofill importe pago | 🟢 Baja | ❌ | Independiente |

---

## Preguntas pendientes de validación (resumen)

| # | Pregunta | Hipótesis A | Hipótesis B |
|---|---|---|---|
| 1 | ¿`Anotaciones` es interna o para imprimir? | Nota interna del vendedor | Se imprime en remito |
| 2 | ¿Unificar `Observaciones` + `Anotaciones`? | Son distintos campos | Se unifican |
| 3 | ¿Marca en combos = entidad `Subgrupo`? | Sí, Subgrupo es la Marca | No, es texto libre en variante |
| 4 | ¿Orden combos varía por categoría? | Siempre Marca→Modelo→Color→Talle | Varía (Indumentaria sin Modelo) |
| 5 | ¿Autofill pago sugiere saldo restante o total? | Saldo restante | Total completo siempre |
| 6 | ¿Stock rápido = nueva vista o misma existente? | Nueva vista de solo lectura | Misma vista ajustando rol |
| 8 | ¿Devolución solo desde venta Entregada? | Solo Entregada | También Confirmada |
| 9 | ¿Combos anidados también en modal de cambio? | Sí | No, búsqueda libre |
| 10 | ¿Empleado puede crear ventas? | Sí (Vendedor restringido) | No (solo ver/cambios/stock) |
| 11 | ¿Subtotal de línea es editable? | No (solo PrecioUnit y Cant) | Sí, y recalcula precio |
| 12 | ¿Total de venta editable directamente? | No | Sí (genera descuento) |
| 13 | ¿Datos actuales DB tienen Marca/Modelo consistentes? | Sí | No (requiere limpieza) |
| 14 | ¿Marca en Producto = FK a Subgrupo? | Sí (SubgrupoId ya es la Marca) | No, campo texto adicional |
| 15 | ¿Talles de indumentaria también predefinidos? | No, texto libre | Sí, también predefinidos |

---

## Dependencias críticas

```
C10 (Refactor Marca/Modelo) 
  └─ desbloquea ──► C03 (Combos Ventas)
  └─ desbloquea ──► C05 (Combos Compras)
  └─ desbloquea ──► C07 (selección variante en cambio)

C11 (Talles config) 
  └─ alimenta ────► C03 / C05 (combo de talle)
  └─ alimenta ────► C12 (formulario dinámico por categoría)

C08 (Rol Empleado)
  └─ requiere saber ► C06 (qué pantalla de stock ve el Empleado)
  └─ requiere saber ► C07 (si Empleado puede hacer cambios)
```

---

*Documento generado como hipótesis funcional a validar. Ningún ítem es dato confirmado hasta aprobación explícita del cliente.*
