# Memoria - QA

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-08-17 (v2 — QA de Etapa 3: migración de catálogo, rama `migracion-catalogo`)

---

# Etapa 3 — Migración de catálogo (QA, 2026-08-17)

## Alcance funcional validado

Rama `migracion-catalogo`, cambios **sin commitear**, revisión pre-merge de los ítems de app de la
Etapa 3 (ítems 2 a 6 del WBS): `CodigoProveedorProducto`, `Proveedor` mínimo, extensión de
`Producto`/`Cliente`, `ICatalogoMigracionService`, `IClasificacionAbcAutomaticaService`, pantallas de
importación (`Views/MigracionCatalogo/*`, 4 vistas) y de excepciones.

**Fuera de alcance de esta validación** (no es código de esta etapa): el ítem 1 del WBS (herramienta
batch de extracción/limpieza contra el backup real) y el ítem 7 (carga a producción). Entregas 1 y 2 no
se revalidaron: solo se verificó que esta etapa no las rompa (regresión puntual).

**Metodología: sin ejecución en caliente.** No hay base con la migración aplicada — el Implementador
generó `EntregaTres_MigracionCatalogo` y **no la aplicó a ninguna base**. Evidencia = lectura completa
de código por capa + `dotnet build`. Los casos que exigen UI/datos reales quedan como procedimiento
manual para Joaquín (ver "Pruebas manuales pendientes").

## Build

`dotnet build FerreteriaLaPlatense.slnx` → **Compilación correcta, 0 Errores**. 9 advertencias, todas
preexistentes y ajenas a Etapa 3: 8×NU1902 (MailKit/MimeKit) + 1×CS0114 (`HomeController.StatusCode`,
ya documentada en el QA de Entrega 1). Verificado antes y después de los dos auto-fixes.

## Cobertura por criterio de aceptación (PASS/FAIL/BLOCKED)

| Criterio de aceptación (origen) | Resultado | Evidencia |
|---|---|---|
| Dedup de nombre: conservar el de venta más reciente en `VentaItem`, respaldo `FechaModificacionPrecio` (analista, "Regla de deduplicación de nombres — versión final") | **N/A en esta etapa** | Es el paso 1 del flujo 10 (extracción/limpieza batch), ítem 1 del WBS explícitamente **no implementado**. El importador recibe un dataset ya deduplicado y no tiene forma de aplicar la regla (el formato de archivo no trae `FechaModificacionPrecio` ni historial de ventas del legacy). Queda como criterio a validar cuando se construya la herramienta. |
| Dedup de `articuloProveedor` por última importación con `Procesado=1` y `ArticuloKey` no nulo (analista) | **N/A en esta etapa** | Ídem: paso 1. La hoja `CodigosPorProveedor` ya llega conciliada; el importador solo valida unicidad del par `(proveedor, código)` dentro del archivo y contra la base. |
| Exclusión de productos sin nombre | **PASS** | `CatalogoMigracionService.LeerProductos`: excepción **bloqueante** "El producto no tiene nombre. No se importa." y `ProductosOmitidos++`. Cubre el caso real del legacy (3.203 artículos con nombre vacío y `Activo=1`), que la regla "excluir inactivos" no filtraba. |
| Exclusión de productos con precio de venta 0 | **PASS** | Ídem, guard `!precioVenta.HasValue \|\| precioVenta.Value <= 0` → bloqueante. |
| Exclusión de productos inactivos | **N/A en esta etapa** | El formato de intercambio no tiene columna `activo` por diseño: el filtro de `Activo=0` (20.536 filas) corresponde al paso 1. Decisión coherente, pero conviene dejarla explícita para que nadie espere que el importador la aplique. |
| Producto sin categoría válida → "Sin categoría" en vez de bloquear (analista) | **PASS** | Excepción **informativa** + `CatalogoPorDefecto.Categoria`. Mismo criterio aplicado a marca y modelo. |
| ABC por Pareto 12 meses sobre `VentaItem`, ventana móvil configurable | **PASS con defecto corregido** | `ClasificacionAbcAutomaticaService.RecalcularAsync`: ventana `MesesVentana` (appsettings + parámetro de pantalla), `GroupBy` en base de datos, piso en 0 para netos negativos, cortes 80/95 configurables y validados. **Defecto D1 detectado y corregido por QA**: la agregación no filtraba `Venta.Estado`, así que los borradores contaban como venta (ver Defectos). |
| La ventana ABC se calcula en la zona horaria correcta (riesgo declarado por el Implementador) | **PASS** | Confirmado en el código final, no solo en el relato de cierre: `hastaUtc = DateTime.UtcNow`, `desdeUtc = hastaUtc.AddMonths(-meses)`, comparados contra `Venta.Fecha`, que se persiste en UTC (`Venta.Fecha = DateTime.UtcNow` en la entidad). La conversión a hora Argentina (`ArgentinaTime.From`) se aplica **solo** a `FechaDesde`/`FechaHasta` del DTO, para mostrar. El bug de comparar columna UTC contra `ArgentinaTime.Now` **no** está presente. |
| `ClasificacionABCSugerida` nunca pisa `ClasificacionABC` (R10, diseñador flujo 10 punto 3) | **PASS** | Triple verificación: (a) el recálculo por lote solo asigna `entidad.ClasificacionABCSugerida`; (b) `ProductoService.EditarAsync/CrearAsync` escribe `ClasificacionABC` (campo manual del ABM) y **no** la sugerida, con comentario explícito; (c) el único camino sugerida→manual es `AceptarSugerenciaAsync`, invocado por `ProductosController.AceptarClasificacionAbcSugerida` (POST + antiforgery + `RequireAdministracion` + confirmación SweetAlert2), que además rechaza el caso "ya coinciden" y "sin sugerencia". |
| Idempotencia: reimportar el mismo archivo da 0 altas y no duplica | **PASS (por revisión de código)** | Claves de identidad: `Producto` por `Codigo`; `Cliente` por `CuitDni`, y si no lo trae por nombre exacto **solo contra clientes sin CUIT** (evita borrarle el CUIT a un homónimo); `CodigoProveedorProducto` por `(ProveedorId, CodigoDelProveedor)`. Todas las consultas de matcheo usan `IgnoreQueryFilters()`, así que un registro soft-deleted se revive en vez de chocar con el índice único (MySQL no distingue soft-deleted en un índice único). En la 2ª corrida: productos → `EsAlta=false`; códigos → `yaMapeados` contiene la clave → `Actualizaciones`; clientes → `porCuit`/`porNombreSinCuit` matchean → `Actualizaciones`. Los catálogos (Marca/Modelo/Categoría/Proveedor) ya existen → `faltantes=0`. **Verificación funcional pendiente** (requiere base). |
| La reimportación no pisa `Stock` ni `ClasificacionABC` manual | **PASS** | En el upsert de `ProcesarProductosAsync` se asignan exclusivamente `Nombre`, `MarcaId`, `ModeloId`, `CategoriaId`, `PrecioCompra`, `PrecioVenta`, `PorcentajeIVA`, `UnidadVenta`, `Bonificacion`, `ClasificacionABCSugerida`, `CodigoBarras`. **No** se tocan `Stock`, `StockVerificado`, `StockMinimo`, `ClasificacionABC`, `PrecioConDescuento`, `UnidadCompra`, `FactorConversion`. Decisión de diseño correcta y deliberada: el import escribe por `DbContext` y no por los Services de negocio, justamente para que estos no estampen valores propios. |
| No se puede confirmar el import sin revisar el reporte de excepciones (diseñador, "Validaciones de UI") | **PASS** | Doble barrera, no solo UI: la vista deshabilita el botón y muestra el aviso, y `MigracionCatalogoController.Confirmar` repite el guard server-side (`TotalExcepciones > 0 && !ExcepcionesFueronRevisadas(token)` → redirect con mensaje). La marca se setea al abrir `Excepciones` y vive en `Session` (registrada y con `UseSession()` antes del middleware de endpoints). Un archivo sin excepciones no exige abrir el reporte — interpretación razonable del criterio. |
| Archivo con hoja o columna obligatoria faltante se rechaza completo, sin importar nada | **PASS** | `ObtenerHoja`/`LeerEncabezado` lanzan `ArchivoMigracionInvalidoException` con el detalle de lo que falta; `PrevisualizarAsync` la captura, descarta el staging y devuelve `CreateError`. No hay persistencia posible antes de esa validación. |
| Permisos: todo lo nuevo detrás de `RequireAdministracion` | **PASS** | Verificado controller por controller, no por el reporte del Implementador: `MigracionCatalogoController` con `[Authorize(Policy="RequireAdministracion")]` **a nivel de clase** (cubre las 7 acciones, incluidas `ExcepcionesListar` y `ExportarExcepciones`); `StockController.RecalcularClasificacionAbc` y `ProductosController.AceptarClasificacionAbcSugerida` con el atributo a nivel de acción (sus clases son `RequireCatalogoConsulta`, que incluye Vendedor — el atributo de acción es imprescindible y está). La policy resuelve a SuperUsuario+Administrador; el link de sidebar usa exactamente `User.IsInRole("SuperUsuario") \|\| User.IsInRole("Administrador")`. |
| `Proveedor` no rompe nada existente y su migración es puramente aditiva | **PASS** | `20260817164053_EntregaTres_MigracionCatalogo`: solo `AddColumn` ×6 (todas `nullable: true`) + `CreateTable` ×2 + `CreateIndex` ×3. **Ningún `AlterColumn`, `DropColumn` ni cambio sobre tablas/columnas de Entregas 1/2.** FKs `Restrict` (no cascada destructiva). `Down()` es el reverso limpio. `Proveedor` no tiene ABM, ni sidebar, ni se referencia desde ninguna entidad preexistente: solo `CodigoProveedorProducto` (tabla nueva) la apunta. Riesgo real es de coordinación futura (el módulo de Compras debe ampliarla, no recrearla), ya documentado en el XML-doc de la entidad. |

## Cobertura del catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Cargado completo (43 ids, incluye el LP-001 creado en este ciclo). Mapeo contra los módulos tocados por
Etapa 3. Los ids ya marcados N/A en el QA de Entrega 1 por módulo inexistente que siguen sin superficie
en esta etapa se agrupan al final.

| id | aplica | resultado | acción |
|---|---|---|---|
| REG-001 (RowVersion MySQL) | no | N/A | El proyecto no usa `RowVersion` ni control de concurrencia optimista en ninguna entidad (grep sobre Domain/Data: 0 hits). Las 2 entidades nuevas heredan `SoftDestroyable`, sin token de concurrencia. |
| REG-002 / REG-006 (campos condicionales de un select) | no | N/A | Ningún select nuevo de esta etapa condiciona campos obligatorios adicionales. |
| REG-003 / REG-005 / REG-007 / REG-009 (Select2 / autocomplete AJAX / cascada) | no | N/A | Sin Select2 ni autocomplete en las vistas nuevas ni en los bloques agregados a `Productos`/`Clientes` (grep: 0 hits). Los combos son `<select>` poblados server-side. |
| REG-004 / KOI-004 / VSF-001 / VSF-002 (botones derivados del estado real, transiciones completas) | no | N/A | Esta etapa no agrega máquina de estados ni botones de transición. El flujo de import es lineal (subir → previsualizar → confirmar), sin estados persistidos. |
| REG-008 (recálculo de UI sin perder foco) | no | N/A | Sin grillas dinámicas con recálculo por `input`/`keyup` en las vistas nuevas. |
| REG-010 / KOI-003 / KOI-005 / KOI-006 (sidebar vs autorización real) | **sí** | **PASS** | Verificado por revisión de código, los 4 puntos del checklist: el controller existe (`MigracionCatalogoController`), la ruta del link coincide (`asp-controller="MigracionCatalogo"` / `asp-action="Index"`, acción `Index()` presente), el atributo de autorización es el esperado (`RequireAdministracion` a nivel de clase) y la condición de roles del link es idéntica a la de la policy. Sin links huérfanos ni roles sin link. |
| KOI-001 (SweetAlert2 fuera del `<form>`) | **sí** | **PASS** | `Productos/Edit.cshtml`: el botón "Aceptar sugerencia" está **dentro** del form de edición pero debe postear a **otro** action — se resuelve con `btn-swal-confirm` + `data-form-id="formAceptarSugerencia"` y un `<form>` separado, **no anidado**, fuera del form principal. Es exactamente el patrón que KOI-001 exige. El diálogo avisa además que se pierden los cambios sin guardar. |
| KOI-002 (falta export a Excel) | **sí** | **PASS** | El reporte de excepciones tiene `ExportarExcepciones` (botón + action + `IExportService`), con encabezados en español. |
| DN-001 / DN-002 (DataTable server-side + Include de colección) | **sí (por patrón)** | **PASS** | El listado nuevo (`ExcepcionesListar`) es server-side pero **no toca EF**: filtra/ordena/pagina en memoria sobre el JSON de staging, así que la causa raíz (2+ `Include` de colección + orden dinámico + `Skip`/`Take`) no puede darse. Los listados EF de `Stock`/`Productos` no se modificaron. |
| CRM-003 (DataTable ignora `order[0][column]`) | **sí** | **PASS** | `ListarExcepcionesAsync` implementa el ordenamiento server-side por `SortColumn`/`SortDirection` con `switch` sobre las 5 columnas reales, y `DataTableRequestHelper.Parse` sí lee `order[0][column]` → `columns[i][data]` → `order[0][dir]`. Los nombres del `switch` coinciden con los `data` declarados en la vista. |
| CRM-002 (control visible para un rol que la acción rechaza) | **sí** | **PASS** | El botón "Aceptar sugerencia" está envuelto en `User.IsInRole("SuperUsuario") \|\| User.IsInRole("Administrador")`, coincidente con `RequireAdministracion` de la acción. Defensa en profundidad correcta en ambos lados. |
| GAN-001 (guard "al menos un ítem" sobre lista dinámica) | no | N/A | Sin listas dinámicas bindeadas por índice en esta etapa. |
| GAN-003 (`<script type="text/x-template">` con Tag Helper) | no | N/A | Sin templates JS en las vistas nuevas (grep: 0 hits). |
| GAN-004 (`<datalist>` nativo) | no | N/A | Sin `<input list>`/`<datalist>`. |
| GAN-002 / VSF-001 (backfill que no filtra por estado de la entidad relacionada) | **sí (por patrón)** | **FAIL → corregido** | Antecedente conceptual del defecto **D1**: un cálculo masivo que agrega filas hijas sin considerar el estado del documento padre. Ver Defectos y el ítem nuevo **LP-001**. |
| **MH-001 (IN sobre colección local de string en MySQL/EF Core 10)** | **sí** | **FAIL → corregido** | **Reaparición real del patrón catalogado.** Dos `Where(...Contains(...))` sobre `List<string>` locales en `CatalogoMigracionService`, ambos en el camino de persistir. Ver Defectos (**D2**). |
| MH-002 (enum serializado como int rompe el badge) | **sí** | **PASS** | `ExcepcionMigracionDto.Seccion` es `string` y `Bloqueante` es `bool`; el `render` de la vista los interpreta correctamente. Sin enums crudos en el JSON de la grilla. |
| MH-003 (validación solo client-side) | **sí** | **PASS** | El guard de "revisó el reporte de excepciones" y el rango de la ventana ABC (1-120 meses) están **los dos** en cliente y en servidor (`RecalcularAsync` revalida el rango y los cortes Pareto; `Confirmar` revalida la revisión del reporte). |
| MH-005 (endpoint no revalida estado server-side) | **sí** | **PASS** | `Confirmar`, `Excepciones`, `ExcepcionesListar` y `ExportarExcepciones` revalidan el token contra el staging en cada request y devuelven un mensaje de negocio si venció; el token se valida como GUID antes de construir la ruta (previene path traversal). |
| MH-009 (fecha calendario pura desplazada por conversión de huso) | **sí** | **PASS** | Las fechas nuevas (`FechaAnalisis`, `FechaDesde`/`FechaHasta` del ABC) se renderizan server-side con `ToString("dd/MM/yyyy HH:mm")` en Razor, no vía JSON+moment.js, así que la causa raíz no aplica. |
| MH-010 (maskMoney no dispara `input`) | no | N/A | Sin campos de dinero editables en las pantallas nuevas (los importes del preview son solo lectura). |
| SG-001 (inputs opcionales vacíos contra ViewModel no nullable) | **sí** | **PASS** | Los campos nuevos de `ProductoFormViewModel` (`Bonificacion`) y `ClienteFormViewModel` (`Domicilio`/`Localidad`/`Email`/`Notas`) son todos `string?`; `RecalculoClasificacionAbcViewModel.MesesVentana` es `int` **no** nullable pero tiene default 12 y el input nunca se renderiza vacío. Sin grillas de inputs indexados. |
| KOI-006, MH-004, MH-006, MH-007, MH-008, MH-011, CRM-001, CRM-004, CRM-005, CRM-006, REG-002…REG-009 (módulos sin superficie en esta etapa: Compras/OC, Caja mensual, Remitos, Bot/CRM, AFIP NC) | no | N/A | Módulos no tocados por Etapa 3 (varios todavía no implementados en el proyecto: Compras, Devoluciones/NC). Sin equivalente que probar. |
| **LP-001 (nuevo, creado en este ciclo)** | **sí** | **FAIL → corregido** | Ver D1. |

## Defectos detectados

### D1 — `major` — El recálculo ABC contaba las ventas en Borrador como rotación real (CORREGIDO)

- **Capa:** Infrastructure. **Archivo:** `FerreteriaLaPlatense.Infrastructure/Services/ClasificacionAbcAutomaticaService.cs`.
- **Detección:** revisión de código + contraste contra el precedente interno del propio repo.
- **Síntoma:** la agregación de rotación filtraba **solo por fecha**
  (`i.Venta.Fecha >= desdeUtc && i.Venta.Fecha <= hastaUtc`), sin mirar `Venta.Estado`. En este proyecto la
  venta **nace editable** (`Borrador`) y sus `ItemVenta` existen desde que se agrega la línea, así que un
  borrador abandonado —o de prueba— sumaba cantidad vendida e inflaba la clase ABC sugerida del producto.
  Con el módulo de anulación por NC de Entrega 3, las ventas `Anulada` sumarían igual.
- **Evidencia de que es un defecto y no una decisión:** `DashboardService.ObtenerProductosMasVendidos`
  hace **exactamente la misma agregación** (`ItemVenta.Cantidad` por producto sobre una ventana) y sí filtra
  `v.Estado == EstadoVenta.Facturada`. Dos cálculos de rotación en el mismo repo con criterios distintos: el
  que no filtra es el que está mal. El criterio funcional del analista es "cantidad vendida", y un borrador
  no vendió nada.
- **Fix aplicado:** agregado `i.Venta.Estado == EstadoVenta.Facturada` al `Where`, contra el conjunto
  **explícito** de estados consumados (no `!= Borrador`, que dejaría pasar `Anulada`). Actualizado el
  XML-doc de la clase para que el criterio documentado coincida con el código.
- **Catalogado como `LP-001`** en `docs/qa/regresiones-manuales.yml` + sección nueva de patrón generalizable
  ("Agregaciones sobre filas hijas de un documento con máquina de estados") en
  `32-estandares-qa-implementador.instructions.md`.

### D2 — `blocker` — El "Confirmar la importación" habría fallado con 500 en MySQL (CORREGIDO)

- **Capa:** Infrastructure. **Archivo:** `FerreteriaLaPlatense.Infrastructure/Services/CatalogoMigracionService.cs`.
- **Detección:** ejecución del catálogo cross-proyecto — item **MH-001**, cuya `nota_qa_sprint4` acota el
  riesgo a colecciones locales de **string** y lo confirma empíricamente contra
  `MySql.EntityFrameworkCore` 10.0.1. **Este proyecto usa ese provider y esa versión exacta.**
- **Síntoma esperado:** dos `Where(coleccionLocalDeString.Contains(columna))` traducidos a `IN` de SQL:
  (1) `ProcesarProductosAsync`, `codigos.Contains(p.Codigo)` con `codigos` = `List<string>` del lote;
  (2) `ProcesarCodigosProveedorAsync`, `codigos.Contains(c.CodigoDelProveedor)`, ídem.
  El provider no asigna type mapping al parámetro de array de strings →
  `InvalidOperationException: Expression '@codigos' in the SQL tree does not have a type mapping assigned` → 500.
- **Por qué era grave:** ambos están **solo en el camino de persistir** (`if (!persistir) return;` corta antes
  en el preview). El operador habría visto un preview perfecto y el fallo aparecería recién al confirmar —
  el paso más caro y menos reversible del flujo, y el que el propio Implementador marcó como la prueba más
  importante de la etapa. No se detectó antes porque la migración EF nunca se aplicó a ninguna base.
- **Fix aplicado (adaptado, no copiado):** el `archivos_fix` canónico de MH-001 es "traer la tabla a memoria
  y filtrar en proceso", **inaceptable acá**: `Productos` tiene 121.691 filas y el bucle procesa lotes de 500
  (≈244 relecturas del catálogo completo). En su lugar se convirtió el `IN` de string en un `IN` de `Id`
  (colección de `int`, segura según la propia nota del catálogo), aprovechando que **ambos métodos ya tenían
  en memoria** el mapa `codigo→Id` / `clave→Id` de la proyección completa que hacen al arrancar: **cero
  consultas extra** y semántica idéntica (ambas proyecciones usan `IgnoreQueryFilters()`, así que el conjunto
  alcanzado por `Id` es el mismo que alcanzaba el `IN` por string, soft-deleted incluidos). Para
  `CodigoProveedorProducto` se agregó el diccionario `idPorClave` sobre la proyección ya existente.
- **Registrado** como `nota_qa_laplatense_etapa3` en MH-001 (reaparición en otro proyecto + la lección de que
  el fix canónico no escala a tablas de volumen).

### D3 — `minor` — La reimportación sobreescribe la sugerencia ABC recién calculada (ACEPTADO, no corregido)

- El upsert de producto asigna `entidad.ClasificacionABCSugerida = f.ClasificacionABCSugerida`. Si el
  operador corre "Recalcular clasificación ABC" y después reimporta el archivo, la sugerencia calculada se
  reemplaza por la del archivo (o por `null`, si la columna viene vacía).
- No se corrige: `clasificacionABCSugerida` es una columna declarada del formato de intercambio y el campo
  manual `ClasificacionABC` —el que importa— nunca se toca. Se resuelve volviendo a recalcular.
- **Acción:** documentado acá y en Riesgos. Conviene avisarlo en la pantalla o recalcular al final del import;
  queda como mejora menor para el Implementador, no bloquea.

### D4 — `informativo` — Entrega 2 nunca pasó por el gate de QA

- La memoria de QA solo tenía el ciclo de Entrega 1 (2026-08-10). Ventas/AFIP/Caja/Gastos/Entregas/Dashboard
  se cerraron el 2026-08-11 y **no hay registro de QA**. No es un defecto de Etapa 3, pero sí un riesgo de
  liberación: esta etapa se apoya en `ItemVenta`/`Venta` (para el ABC) y en `Cliente` (para el import), que
  nunca fueron validados funcionalmente.
- **Observación colateral** (Entrega 2, fuera de alcance, no corregida): `DashboardService` usa
  `DateTime.Today` para armar la ventana del mes contra `Venta.Fecha`, que está en UTC — es la misma clase de
  bug de huso horario que el Implementador sí evitó en el ABC. Recomendado revisarlo en el QA pendiente de
  Entrega 2.

## Auto-fixes aplicados por QA

| id catálogo | defecto | archivos tocados | resultado post-parche |
|---|---|---|---|
| `LP-001` (nuevo) | D1 — ABC contaba borradores | `FerreteriaLaPlatense.Infrastructure/Services/ClasificacionAbcAutomaticaService.cs` (filtro `Estado == Facturada` + XML-doc) | `dotnet build` → 0 errores. Verificación funcional pendiente de base (prueba manual 4 de abajo). |
| `MH-001` (existente, reaparición) | D2 — `IN` de string en MySQL | `FerreteriaLaPlatense.Infrastructure/Services/CatalogoMigracionService.cs` (relectura de lote por `Id` en los 2 puntos + `idPorClave`) | `dotnet build` → 0 errores. Verificación funcional pendiente de base (prueba manual 2). |

Ninguno de los dos introduce lógica de negocio nueva: D1 replica el criterio de estado que ya usaba
`DashboardService` en el mismo repo, y D2 replica el patrón de evitar `IN` de string ya catalogado.

## Pruebas manuales pendientes (a ejecutar por Joaquín — requieren UI y base con la migración aplicada)

**Prerequisito obligatorio antes de cualquier prueba en caliente:**
`dotnet ef database update --project FerreteriaLaPlatense.Infrastructure --startup-project FerreteriaLaPlatense.Web`
(la migración `EntregaTres_MigracionCatalogo` **no fue aplicada** por el Implementador). Hace falta además un
`.xlsx` de prueba con las 3 hojas y una decena de filas cada una — no se necesita el dataset real.

1. **Permisos (cierra la verificación en caliente de REG-010/KOI-005).** Con un usuario `Vendedor`: el link
   "Migración de catálogo" no debe aparecer en el sidebar, y `/MigracionCatalogo` por URL directa debe dar
   **403, no 500 ni acceso silencioso**. Repetir con `POST /Stock/RecalcularClasificacionAbc` y
   `POST /Productos/AceptarClasificacionAbcSugerida`. Con `Administrador`: el link aparece bajo Catálogo y la
   pantalla carga.
2. **Confirmación del fix D2 (la prueba más importante).** Subir el archivo → revisar → **Confirmar**. Debe
   completar y mostrar la pantalla de resultado con los mismos números que el preview. Si apareciera un 500
   con `does not have a type mapping assigned`, el fix no alcanzó y hay que escalar al Implementador.
3. **Idempotencia.** Reimportar **exactamente el mismo archivo**: el preview debe mostrar **0 altas y todas
   actualizaciones** en las 3 secciones y 0 catálogos a crear; el total de productos y clientes del sistema no
   debe cambiar. Después: editar a mano un producto migrado (stock mínimo por el ABM, stock por "Ajustar",
   clasificación ABC manual), reimportar, y verificar que **stock y clasificación ABC manual siguen como los
   dejó usted**.
4. **Confirmación del fix D1.** Crear una venta con 500 unidades de un producto que no rota y **dejarla en
   Borrador**. Recalcular ABC a 12 meses → ese producto **no** debe quedar A/B por el borrador, y no debe
   contarse en "productos con ventas en el período". Después facturar esa venta y recalcular → ahora sí debe
   reflejarse.
5. **Excepciones.** Archivo con: producto sin nombre, producto sin precio de venta, código repetido, código de
   proveedor apuntando a un `codigoProducto` inexistente, y cliente sin nombre. Cada uno debe aparecer con su
   motivo y marcado "No se importa"; el resto del archivo debe importarse igual. Verificar que con al menos una
   excepción el botón "Confirmar" arranca **deshabilitado**, y que se habilita recién después de abrir el
   reporte y volver al resumen. Probar además a confirmar por POST directo sin haber abierto el reporte: debe
   rechazarlo con mensaje (guard server-side).
6. **Filtros y export del reporte.** Filtrar por sección, por texto del motivo y por "No se importa"; ordenar
   haciendo click en cada encabezado (verifica CRM-003 en caliente). Exportar a Excel: mismas filas y
   encabezados en español.
7. **Archivo inválido.** Subir un `.xlsx` al que le falte una hoja, y otro al que le falte una columna
   obligatoria: debe rechazarlos con un mensaje que diga qué falta, **sin importar nada**.
8. **Ventana ABC.** Recalcular con ventana de 1 mes y comparar contra 12 meses: los resultados deben cambiar
   (menos productos con venta). Verificar que el recálculo **no** cambió la clasificación manual de ningún
   producto (comparar el listado de `Stock` antes y después).
9. **"Aceptar sugerencia".** En un producto donde la sugerencia difiera, usar el botón y confirmar → el campo
   manual queda con el valor sugerido. Reintentarlo debe avisar que ya coinciden. Verificar que el botón
   **no** aparece para `Vendedor`.
10. **Regresión de Entrega 1/2.** Alta y edición de producto por el ABM normal, con y sin bonificación (el
    combo de marca/modelo/categoría de Editar debe seguir llegando con el valor asignado); alta y edición de
    cliente con los 4 campos nuevos vacíos (deben guardar: son opcionales) y con un email mal escrito (debe
    bloquear con mensaje); una venta completa Borrador → Facturada.

## Riesgos de liberación (Etapa 3)

1. **La migración EF no está aplicada a ninguna base.** Prerequisito absoluto y bloqueante para cualquier
   prueba. Es aditiva pura, así que el riesgo de aplicarla es bajo — pero hacer backup antes igual.
2. **Nada de esta etapa se ejecutó nunca.** Los dos defectos encontrados (uno de ellos `blocker`) salieron de
   revisión de código, no de ejecución. Sin las pruebas manuales 2 y 3 no hay evidencia de que el import
   funcione de punta a punta. **Es el riesgo principal.**
3. **Tiempo de proceso con 121.691 productos sin medir** (riesgo ya declarado por el Implementador, sigue
   abierto). El import es síncrono dentro del request. Mitigación operativa: partir el archivo en tandas
   aprovechando la idempotencia. Medir con el dataset real antes de comprometer una ventana de corte.
4. **Staging en el temp del sistema operativo**, sin limpieza automática: los archivos con datos del cliente
   quedan en `%TEMP%/FerreteriaLaPlatense/migracion-catalogo/` y **hay que borrarlos a mano**. Si el hosting
   recicla el proceso entre analizar y confirmar, hay que volver a subir (el sistema lo avisa con un mensaje
   claro, no rompe con 500 — verificado en código).
5. **La deduplicación real (paso 1) no existe todavía.** Los criterios de aceptación centrales de la etapa
   (dedup de nombre y de `articuloProveedor`) **no son validables** con lo implementado: dependen de la
   herramienta batch del ítem 1 del WBS, que hay que construir y que va a necesitar su propio ciclo de QA.
   Conviene no comunicar la Etapa 3 como "migración terminada": está el importador, no la extracción.
6. **Entrega 2 sin QA** (D4). Esta etapa se apoya en `Venta`/`ItemVenta`/`Cliente`, nunca validados.
7. `Proveedor` mínimo: cuando se implemente Compras, hay que **ampliar** la entidad, no recrearla. Riesgo de
   coordinación, ya documentado en el XML-doc.
8. `Bonificacion` es informativa y no participa de ningún cálculo de precio — si el cliente espera que "33+5"
   descuente, es alcance nuevo.

## Estado go/no-go (Etapa 3)

**GO CONDICIONADO** al merge de la rama, con dos condiciones de cumplimiento obligatorio:

1. Aplicar `EntregaTres_MigracionCatalogo` a la base de desarrollo.
2. Ejecutar las pruebas manuales **1, 2, 3, 4 y 5** (permisos, confirmar, idempotencia, fix del ABC,
   excepciones) y reportar PASS/FAIL. Las pruebas 2 y 4 son la verificación en caliente de los dos auto-fixes
   de este ciclo y **no pueden saltearse**.

Fundamento: el código está bien construido —el diseño de idempotencia es sólido y deliberado, los permisos
son correctos controller por controller, la migración es aditiva pura y el bug de huso horario que el
Implementador declaró haber corregido está efectivamente corregido en el código final—, pero **el `blocker`
D2 demuestra el costo de cerrar una etapa sin ejecutar nada**: el camino de confirmación, que es el corazón
de la etapa, habría fallado en la primera prueba real. Con los dos fixes aplicados y el build limpio no hay
motivo para frenar el merge, pero **no hay GO para la carga a producción** hasta tener las pruebas en caliente
y la herramienta del paso 1.

## Checklist de salida para merge (Etapa 3)

- [x] `dotnet build FerreteriaLaPlatense.slnx` → 0 errores (verificado 3 veces: inicial y tras cada auto-fix).
- [x] Permisos verificados controller por controller, no por el reporte del Implementador.
- [x] Migración EF revisada línea por línea y confirmada aditiva pura.
- [x] Idempotencia revisada a fondo por código (claves de identidad, `IgnoreQueryFilters`, campos no pisados).
- [x] `IClasificacionAbcAutomaticaService` confirmado: nunca escribe `ClasificacionABC`; ventana en UTC correcta.
- [x] Catálogo cross-proyecto ejecutado (43 ids) y cobertura reportada.
- [x] 2 defectos corregidos con auto-fix + catalogados (`LP-001` nuevo, `MH-001` reaparición).
- [x] Patrón generalizable agregado a `32-estandares-qa-implementador.instructions.md`.
- [ ] **Migración aplicada a la base de desarrollo** (pendiente, bloqueante para pruebas).
- [ ] **Pruebas manuales 1-5 ejecutadas por Joaquín** (pendiente, bloqueante para producción).
- [ ] Pendiente (no bloqueante): D3 — avisar o recalcular la sugerencia ABC tras un reimport.
- [ ] Pendiente (no bloqueante): QA de Entrega 2, nunca ejecutado (D4).
- [ ] Pendiente (no bloqueante): confirmar con Joaquín las 3 decisiones que tomó el Implementador (productos sin
      venta en `C` y no `null`; unidades no modeladas → `Unidad`; CC de clientes no se migra).

---

# Entrega 1 — Catálogo / Stock / Usuarios (QA, 2026-08-10)

## Definiciones vigentes

### Alcance funcional validado

Primera entrada del proyecto a la etapa de QA. Alcance de esta validación: **exclusivamente Entrega 1**
(Catálogo, Stock, Usuarios/roles, Código de barras), sobre el repo `C:\Sistemas\Ferreteria La Platense`
(`FerreteriaLaPlatense.slnx`, .NET 10, EF Core 10 + MySQL, ASP.NET Core Identity).

No se validó (no existe código todavía, confirmado por inspección del repo — 0 controllers/entidades
de esos módulos): Ventas, AFIP/Facturación, Caja, Compras, Cuenta corriente (clientes/empleados/negocio),
Devoluciones/NC, Presupuestos, Entregas, Dashboard. Quedan para Entrega 2/3.

Metodología: sin ejecución en caliente (no hay base de datos con la migración aplicada — ver Riesgos).
Evidencia = lectura de código completa por capa (Domain/Application/Infrastructure/Web) + `dotnet build`.
Para los casos que requieren UI se deja el procedimiento manual paso a paso para que Joaquín/el cliente
lo ejecuten y reporten PASS/FAIL/BLOCKED.

### Build

`dotnet build FerreteriaLaPlatense.slnx` → **Compilación correcta, 0 Errores** (9 advertencias: 4×NU1902
vulnerabilidad conocida de MailKit/MimeKit preexistente, 1×NETSDK1057 por SDK preview, 1×CS0114
`HomeController.StatusCode` oculta miembro heredado — las 3 categorías son preexistentes, no introducidas
por Entrega 1). Verificado antes y después de aplicar los auto-fixes de ortografía (ver Defectos).

### Cobertura de historias de usuario

| Historia / módulo (Entrega 1) | Resultado |
|---|---|
| Usuarios y roles (Admin/Vendedor/Repartidor) | Cumple |
| Catálogo de productos (Marca/Modelo/Categoría/IVA/precio/descuento) | Cumple |
| Unidades de medida y conversión compra↔venta (R4) | Cumple |
| Stock + puesta a punto inicial (ABC, ajuste manual auditado, arranque con negativo permitido) | Cumple |
| Código de barras — vinculación al producto (M11) | Cumple (parcial por alcance: sin pantalla de Venta todavía, expuesto vía endpoint de prueba) |

### Cobertura por criterio de aceptación (PASS/FAIL/BLOCKED)

| Criterio | Resultado | Evidencia |
|---|---|---|
| PF13 — producto sin stock verificado puede "venderse" igual (stock negativo con aviso, sin bloqueo) | PASS (parcial, dato/flag) | `Producto.Stock` es `decimal` sin restricción de signo; `StockVerificado=false` por defecto en `CrearAsync`; ningún Service bloquea valores negativos. No hay pantalla de Venta en esta entrega — el criterio completo (aviso visual en el flujo de venta) se termina de cerrar en Entrega 2, tal como está planificado. |
| PF14 — ajuste manual de stock con motivo, auditado (quién/cuándo/motivo) | PASS | `AjusteStockService.AplicarAjusteAsync` registra `AjusteStock` (ProductoId, Fecha UTC, UsuarioId desde `ClaimTypes.NameIdentifier`, CantidadAnterior/Nueva, Motivo obligatorio) antes de pisar `Producto.Stock`; `StockController.Historial` expone el historial por producto vía DataTable server-side. |
| R4 — `UnidadCompra != UnidadVenta` exige `FactorConversion` > 0 | PASS | Validado en `ProductoService.ValidarAsync` (Service, no solo ViewModel) vía `IUnidadMedidaConversionService.EsFactorConversionValido`; UI oculta/limpia el campo con JS cuando no aplica; `[Range(0.0001,...)]` en el ViewModel como cota adicional de UI. |
| R11 — código de barras único, propio o de fábrica, sin distinción funcional | PASS | `Producto.CodigoBarras` nullable + índice único (MySQL permite múltiples NULL); `CodigoBarrasLookupService.BuscarPorCodigoAsync` busca indistintamente por `CodigoBarras` o `Codigo`. |
| Permisos: Admin (todo) / Vendedor (catálogo y stock en consulta) / Repartidor (sin pantallas en Entrega 1) | PASS | Policies `RequireCatalogoConsulta` (SuperUsuario+Vendedor) en `ProductosController`/`StockController`/`MarcasController`/`ModelosController`/`CategoriasController` a nivel de clase; alta/edición/baja y ajuste de stock exclusivos de `RequireSuperUsuario` a nivel de acción; sidebar coincide (ver catálogo cross-proyecto, id REG-010/KOI-003). Repartidor no tiene ningún link ni policy que lo habilite — correcto para el alcance de esta entrega. |
| Bloqueo de baja de Marca/Modelo/Categoría en uso | PASS (regla agregada por el Implementador, no exigida explícitamente por el análisis, pero consistente y correcta) | `CatalogoSimpleServiceBase.EliminarAsync` verifica `EstaEnUsoAsync` (override por entidad, contra `Producto.MarcaId/ModeloId/CategoriaId`) antes de permitir soft-delete; mensaje sugiere desactivar en su lugar. |

### Matriz de casos de prueba

**Casos felices**
1. Crear Marca/Modelo/Categoría con nombre único → alta correcta, aparece en combos de Producto.
2. Crear Producto con `UnidadCompra == UnidadVenta` (sin factor) → alta correcta, stock arranca en 0/sin verificar.
3. Crear Producto con `UnidadCompra=Bulto`, `UnidadVenta=Unidad`, `FactorConversion=100` → alta correcta.
4. Ajustar stock de un producto con motivo → `Stock` pasa a pisar el valor nuevo, `StockVerificado=true`, aparece en Historial.
5. Buscar producto por código de barras (endpoint de prueba en Productos/Index) → devuelve el producto.
6. Crear usuario con rol Vendedor o Repartidor → login exitoso, sidebar acorde al rol.
7. Editar Producto → combos Marca/Modelo/Categoría llegan preseleccionados con el valor actual.

**Casos de borde**
1. Crear Producto con `UnidadCompra != UnidadVenta` y `FactorConversion` vacío o 0 → debe rechazar (Service, R4). **PASS por código** — cubierto por `ValidarAsync`.
2. Ajuste de stock que deja `CantidadNueva` negativa → debe permitirse (arranque suave, R10) y quedar auditado igual. **PASS por código** — `AplicarAjusteAsync` no valida signo de `CantidadNueva`.
3. Crear Producto con `Codigo` o `CodigoBarras` duplicado (ya existente) → debe rechazar con mensaje claro. **PASS por código** — `ValidarAsync` chequea unicidad excluyendo el propio Id en edición.
4. Eliminar una Marca/Modelo/Categoría **en uso** por al menos un Producto activo → debe bloquear sugiriendo desactivar. **PASS por código** — `EstaEnUsoAsync` por entidad.
5. Editar Producto cuya Marca/Modelo/Categoría asignada fue desactivada después → el combo de Editar debe seguir mostrando esa opción seleccionada (no vacío). **PASS por código** — `ProductosController.PoblarCombosAsync` re-agrega la entidad inactiva si no está en el listado de activos.
6. Vendedor intenta acceder a Create/Edit/Delete de Producto o a Stock/Ajuste → debe ser rechazado (403/redirect AccessDenied). **PASS por código** — `[Authorize(Policy="RequireSuperUsuario")]` a nivel de acción.
7. Repartidor intenta acceder a `/Productos/Index` o `/Stock/Index` directamente por URL → debe ser rechazado. **PASS por código** — `RequireCatalogoConsulta` solo incluye SuperUsuario+Vendedor.
8. IVA con un valor fuera de {10,5; 21} vía manipulación directa del POST (no por el `<select>`) → debe rechazar. **PASS por código** — `AlicuotasIVA.Permitidas` validado en el Service.

**Procedimiento manual para el cliente (a ejecutar en caliente, reportar PASS/FAIL/BLOCKED)**

Prerrequisito obligatorio antes de cualquier prueba: aplicar la migración (ver Riesgos, punto 1).

1. Login como SuperUsuario (seed) → crear un usuario Vendedor y otro Repartidor desde Usuarios → cerrar sesión → loguearse con cada uno → verificar que el sidebar muestra exactamente lo esperado por rol (Vendedor: Catálogo+Stock; Repartidor: nada de Entrega 1).
2. Como SuperUsuario, crear una Marca, un Modelo y una Categoría.
3. Crear un Producto usando esa Marca/Modelo/Categoría, con `UnidadVenta=Unidad`, sin unidad de compra distinta. Guardar y verificar que aparece en el listado con Stock=0 y badge "Sin verificar".
4. Crear un segundo Producto con `UnidadCompra=Bulto` y sin completar el factor de conversión → debe bloquear el guardado con el mensaje de error correspondiente.
5. Completar el factor de conversión (ej. 100) y guardar → debe permitir el alta.
6. Ir a Stock → Ajuste sobre el primer producto → cargar cantidad nueva (probar también un valor negativo) y motivo → guardar → verificar badge "Verificado" y que el Historial muestra el registro con usuario/fecha/motivo.
7. En Productos/Index, usar el buscador de código de barras con el código interno de un producto sin código de barras propio → debe encontrarlo igual (busca por `Codigo` o `CodigoBarras`).
8. Intentar eliminar la Marca usada por el Producto creado → debe bloquear sugiriendo desactivar.
9. Desactivar esa Marca → editar el Producto → confirmar que el combo Marca sigue mostrando la marca (ahora inactiva) seleccionada, no vacío.
10. Login como Vendedor → confirmar que ve Productos/Stock/Marcas/Modelos/Categorías en modo **solo consulta** (sin botones Nuevo/Editar/Eliminar/Ajustar) y que forzar la URL de Create/Edit/Ajuste devuelve acceso denegado.

### Cobertura de maquina de estados

No hay una máquina de estados formal con transiciones múltiples en Entrega 1 (Venta/Compra, que sí la
tendrán, son Entrega 2/3). Los dos "estados" binarios presentes:

| Entidad.Campo | Transición | Resultado |
|---|---|---|
| `Producto.StockVerificado` | `false → true` (al aplicar el primer `AjusteStock`) | PASS — un solo sentido por diseño (R10/PF14), no hay ni debería haber vuelta a `false`. |
| `Marca/Modelo/Categoria.Activo` | `true ↔ true/false` libremente vía Editar | PASS — reversible en ambos sentidos, sin restricción indebida; la restricción real está en la baja física (bloqueada si está en uso), no en el toggle de Activo. |

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

Playbook cargado completo (30 ids con `severidad != deprecated`, proyectos ShowroomGriffin/KOI/
delicias-naturales/ganaderia/vinosefue/crm-olvidata). Mapeo a Catálogo/Stock/Usuarios de La Platense:

| id | aplica (si/no/N/A) | resultado | accion |
|---|---|---|---|
| REG-001 | si (mismo stack MySQL+EF Core) | PASS — no reproduce | Ninguna entidad de Entrega 1 define `RowVersion`/`IsConcurrencyToken`, por lo que no puede ocurrir el `DbUpdateException` del catálogo. Nota para el Implementador: si Entrega 2/3 agrega concurrencia optimista (ej. edición simultánea de Venta), aplicar el patrón manual (`IsConcurrencyToken().ValueGeneratedNever()` + asignación manual en `SaveChanges`) desde el inicio. |
| REG-002 | si (patrón "falta stock inicial en el alta") | PASS — no es bug, es diseño confirmado | El Create de Producto no expone `Stock` a propósito (`2-disenador-funcional.md` flujo 8: la carga inicial es siempre vía Ajuste de stock, con auditoría). Comportamiento esperado, distinto del caso original (que sí era una omisión). |
| REG-003 | N/A | N/A | No hay ningún combo Select2 con autocomplete AJAX en Entrega 1 (Marca/Modelo/Categoría usan `<select>` simple con `asp-items`). Vigilar en Entrega 2 (buscador de productos/clientes en Venta). |
| REG-004 | N/A | N/A | Compras no existe en esta entrega. |
| REG-005 | N/A | N/A | Ventas no existe en esta entrega. |
| REG-006 | N/A | N/A | Ventas/medios de pago no existen en esta entrega. |
| REG-007 | N/A | N/A | Devoluciones no existe en esta entrega. |
| REG-008 | N/A | N/A | No hay grillas dinámicas de filas (pagos/ítems) en Entrega 1. |
| REG-009 | N/A | N/A | No hay combos en cascada en Entrega 1 (Marca/Modelo/Categoría son independientes entre sí). |
| REG-010 | si | PASS | Sidebar: sección "Catálogo" gateada por `SuperUsuario\|\|Vendedor`, coincide con policy `RequireCatalogoConsulta` real de los 5 controllers; sección "Sistema" (Usuarios/System/Notifications) gateada por `SuperUsuario`, coincide con `RequireSuperUsuario` de `UsersController`/`SystemController` (`NotificationsController` usa `[Authorize]` simple, pero es correcto: es la bandeja **propia** de cada usuario, filtrada por `userId` en el Service — no hay escalamiento de privilegio, solo falta el link de sidebar para Vendedor/Repartidor, defecto pre-existente fuera del alcance de Entrega 1, no introducido por esta entrega). |
| KOI-001 | si (patrón SweetAlert2 + delete) | PASS — no reproduce | Los botones eliminar de Productos/Marcas/Modelos/Categorías no dependen de `closest('form')`: el JS crea un `<form>` dinámico (`document.createElement`) recién al confirmar el SweetAlert2, así que no hay riesgo de "form no encontrado". |
| KOI-002 | N/A | N/A | No hay reportes/exportación en Entrega 1. |
| KOI-003 | si | PASS | Vendedor ve y puede acceder a Catálogo/Stock (coincide con `R` del analista); Repartidor no ve nada de Entrega 1 (correcto, no tiene pantallas propias todavía). |
| KOI-004 | si (patrón "validación solo en UI") | PASS | `ProductoService.ValidarAsync` valida `FactorConversion`, unicidad de `Codigo`/`CodigoBarras` e IVA permitido en el Service, no solo en el ViewModel/JS. |
| KOI-005 / KOI-006 | si (patrón "link de sidebar sin controller") | PASS | Los 8 links de sidebar de Entrega 1 (Productos/Stock/Marcas/Modelos/Categorías/Users/System/Notifications) tienen su controller real correspondiente en el repo, verificado por lectura de código. |
| DN-001 / DN-002 | N/A | N/A | Ningún listado de Entrega 1 combina `Include` de **colección** (uno-a-muchos) con `OrderBy` dinámico + `Skip`/`Take`; los `Include` de `ProductoService.ListarAsync` son de referencia (Marca/Modelo/Categoría, muchos-a-uno), patrón no afectado por el bug del proveedor EF6-MySQL (que además no aplica: este proyecto usa el proveedor `Pomelo`/EF Core 10, no `MySql.Data.EntityFramework`). Vigilar si Entrega 2 agrega un listado de Ventas con `Include(v => v.Items)`. |
| GAN-001 | N/A | N/A | No hay listas dinámicas bindeadas por índice (`Items[i]`) en Entrega 1. |
| GAN-002 | N/A | N/A | No hay backfill de datos de producción en este ciclo (proyecto sin datos reales todavía). |
| GAN-003 | N/A | N/A | No se usa el patrón `<script type="text/x-template">` con Tag Helpers adentro en ninguna vista de Entrega 1. |
| GAN-004 | N/A | N/A | No se usa `<input list>`+`<datalist>` en ninguna vista de Entrega 1; los combos son `<select>` estándar (Select2 está cargado en `_Layout.cshtml` pero todavía sin uso en Entrega 1). |
| VSF-001 / VSF-002 | N/A | N/A | No hay máquina de estados de Compra/Pedido en esta entrega. |
| CRM-001 | si (patrón "acción sin `SaveChanges` → sin auditoría") | PASS — no reproduce | Todas las mutaciones de Entrega 1 (alta/edición/baja de catálogos, ajuste de stock) pasan por `IRepository<T>.SaveChangesAsync()` → `AppDbContext.SaveChangesAsync` → `StampSoftDestroyable` (audita `CreatedAt/UpdatedAt` + usuario). No hay ninguna acción "fantasma" que cambie estado sin persistir. |
| CRM-002 | si (patrón "control visible en la vista sin gate de rol, pese a que el controller lo exige") | PASS | Los botones Editar/Eliminar/Ajustar en Productos/Marcas/Modelos/Categorías/Stock (`Index.cshtml`) están envueltos en `@if (User.IsInRole("SuperUsuario"))`, coincidiendo exactamente con la policy `RequireSuperUsuario` de las acciones correspondientes. |
| CRM-003 | si (patrón "click en columna no reordena, `order[0][column]` ignorado") | PASS — no reproduce | `DataTableRequestHelper.Parse` lee `order[0][column]`/`order[0][dir]` reales del request y resuelve el nombre de columna vía `columns[{col}][data]`; `ProductoService`/`AjusteStockService`/`CatalogoSimpleServiceBase` aplican un `switch` de `OrderBy` dinámico real sobre `request.SortColumn`, no un orden fijo hardcodeado. |
| CRM-004 | N/A | N/A | No hay alta masiva desde una API externa en Entrega 1. |
| CRM-005 | N/A | N/A | No hay bot/conversación en este proyecto. |
| CRM-006 | N/A | N/A | No hay flujo de notificación disparado por eventos de Catálogo/Stock en el diseño de Entrega 1. |

**Resumen cross-proyecto:** 30 ids evaluados → 12 aplican directamente (10 PASS sin reproducción,
2 identificados como diseño esperado no-bug), 18 N/A justificados por ausencia del módulo/patrón
equivalente en Entrega 1. **0 regresiones del catálogo reproducidas.**

### Defectos activos

| # | Severidad | Módulo | Descripción | Estado |
|---|---|---|---|---|
| D1 | minor | Productos/Marcas/Modelos/Categorías (Index) | Texto de confirmación SweetAlert2 del botón eliminar decía `"Si, eliminar"` (falta tilde; en español "si" sin tilde es la conjunción condicional, "sí" con tilde es la afirmación) — 4 vistas idénticas. Aplica la regla nueva de ortografía/acentuación (`25-frontend-design-system.instructions.md`, pedido explícito de Joaquín 2026-08-10). | **Corregido por QA** (auto-fix, ver abajo). |
| D2 | minor | `Views/Shared/_Layout.cshtml` | Título del toast SweetAlert2 de éxito (disparado por `TempData["SuccessMessage"]` en **toda** la aplicación) decía `"Exito"` sin tilde; correcto es `"Éxito"`. Máxima visibilidad — aparece tras cada alta/edición/baja exitosa de cualquier módulo. | **Corregido por QA** (auto-fix, ver abajo). |
| D3 | minor (fuera de alcance de Entrega 1, informativo) | `Web/Models/UserViewModels.cs` (líneas 37 y 73) | Mensaje de validación `[EmailAddress(ErrorMessage = "El formato de email no es valido.")]` — falta tilde en "válido". Archivo preexistente, no tocado por el Implementador en esta entrega (`UsersController` solo extendió `GetAssignableRoles()`). No corregido por no estar dentro del alcance de Entrega 1 pedido para esta validación; se deja registrado para que el Implementador lo corrija en el próximo touch de ese archivo. | Pendiente (fuera de alcance). |
| D4 | informativo, no bloqueante | `NotificationsController`/sidebar | El link "Notificaciones" del sidebar solo aparece en la sección gateada a `SuperUsuario`, pero el controller (`[Authorize]` simple, correcto porque la bandeja es propia de cada usuario vía `userId`) permitiría acceso a cualquier rol autenticado si se navega directo por URL. No es una falla de seguridad (no hay escalamiento de privilegio, cada usuario solo ve sus propias notificaciones) ni fue introducido por Entrega 1 (código preexistente). Se documenta como mejora de UX menor, no como defecto de esta entrega. | No corregido (fuera de alcance, preexistente). |

### Auto-fixes aplicados por QA

Ambos defectos (D1, D2) son errores de ortografía en texto de UI, no bugs funcionales — no requieren
alta en `docs/qa/regresiones-manuales.yml` (ese catálogo es exclusivamente para regresiones funcionales
reproducidas, ver regla de borde de `30-qa-regresiones.instructions.md`: "Solo se registran bugs
funcionales..."). Se aplicó el fix directo, de contenido puro, sin lógica de negocio nueva:

- `FerreteriaLaPlatense.Web/Views/Productos/Index.cshtml` — `'Si, eliminar'` → `'Sí, eliminar'`.
- `FerreteriaLaPlatense.Web/Views/Marcas/Index.cshtml` — idem.
- `FerreteriaLaPlatense.Web/Views/Modelos/Index.cshtml` — idem.
- `FerreteriaLaPlatense.Web/Views/Categorias/Index.cshtml` — idem.
- `FerreteriaLaPlatense.Web/Views/Shared/_Layout.cshtml` — `'Exito'` → `'Éxito'`.

Re-build post-parche: `dotnet build FerreteriaLaPlatense.slnx` → **Compilación correcta, 0 Errores**
(mismas 9 advertencias preexistentes, ninguna nueva). Pruebas mínimas re-ejecutadas: lectura de código
confirma que el cambio es de contenido de string únicamente, sin alterar la lógica de los handlers de
click ni el flujo de submit del form dinámico — sin riesgo de regresión funcional.

### Riesgos de liberacion

1. **Bloqueante para cualquier prueba en caliente:** la migración `EntregaUno_CatalogoStockUsuarios`
   (20260810165155) fue generada pero **no aplicada a ninguna base de datos** — confirmado en
   `5-implementador.md`. Antes de que Joaquín o el cliente prueben esta entrega, ejecutar:
   ```
   dotnet ef database update --project FerreteriaLaPlatense.Infrastructure --startup-project FerreteriaLaPlatense.Web
   ```
   contra la base de dev/staging real. Es la primera migración del proyecto (crea también el esquema
   base de Identity/Notifications/PreferenciaUsuario que nunca se había migrado).
2. Riesgo de negocio ya declarado por el Implementador, sin cerrar: la hipótesis de que el factor de
   conversión es **fijo por producto** (no varía según el bulto del proveedor) está codificada tal cual
   en `UnidadMedidaConversionService`. Si el cliente confirma que un mismo producto llega en bultos de
   distinto tamaño según el proveedor, el modelo de `Producto` necesita revisión **antes** de Entrega 2
   (Compras). No bloquea Entrega 1 (el dato ya es correcto para el caso simple), sí bloquea Compras.
3. Riesgo de negocio a confirmar con el personal de mostrador: el ajuste manual de stock **pisa** el
   valor (no suma/resta) — confirmar que matchea la expectativa operativa antes de que lo use el
   personal, ya que un error de interpretación (cargar "cuánto vendí" en vez de "cuánto queda") generaría
   datos de stock incorrectos sin que el sistema lo detecte.
4. Riesgo técnico menor, no bloqueante: no hay control de concurrencia optimista en `Producto.Stock`
   (dos ajustes simultáneos del mismo producto aplican "last write wins" sin fusionar). Bajo impacto en
   Entrega 1 (operación de mostrador, un usuario a la vez en la práctica), a revisar si Entrega 2/3
   introduce ajustes concurrentes de alto volumen.
5. `Marca`/`Modelo`/`Categoria` arrancan sin ningún registro seed — el cliente debe cargar su propio
   catálogo de marcas/modelos/categorías antes de poder cargar productos (comportamiento esperado,
   documentado por el Implementador, no es un defecto).

### Estado go/no-go

**GO condicionado** — Entrega 1 (Catálogo, Stock, Usuarios/roles, Código de barras) aprobada para que
el cliente comience a probarla, **una vez aplicada la migración pendiente** (riesgo #1, prerrequisito
obligatorio — sin ella no hay ninguna tabla creada y ninguna pantalla puede funcionar). No se encontraron
defectos funcionales ni de permisos por revisión de código; los 2 defectos de ortografía detectados
(D1, D2) ya fueron corregidos por este ciclo de QA. 0 regresiones del catálogo cross-proyecto
reproducidas. El defecto D3 (fuera de alcance) y D4 (informativo) no bloquean el go-live de esta entrega.

**Checklist de salida para merge:**
- [x] Build limpio (`dotnet build`, 0 errores) antes y después del auto-fix.
- [x] Revisión de fronteras por capa (Domain/Application/Infrastructure/Web) sin mezclas indebidas.
- [x] Validaciones de negocio (R4, unicidad, IVA permitido) presentes en el Service, no solo en la UI.
- [x] Permisos por rol verificados por código (policy de controller/action ↔ sidebar).
- [x] Combos de Editar preseleccionados correctamente (Marca/Modelo/Categoría), incluso si la entidad
      referenciada fue desactivada después.
- [x] Ortografía/acentuación de todo el texto de UI creado en Entrega 1 revisada y corregida.
- [x] Catálogo de regresiones cross-proyecto ejecutado (30 ids), 0 reproducidas.
- [ ] **Pendiente antes de prueba en caliente:** aplicar `dotnet ef database update` contra la base real.
- [ ] Pendiente (no bloqueante): confirmar con el cliente la hipótesis de factor de conversión fijo por
      producto antes de arrancar Compras (Entrega 2).

## Historial de ajustes
- 2026-08-10: Primera etapa de QA del proyecto. Cargado el playbook cross-proyecto completo
  (`docs/qa/regresiones-manuales.yml`, 30 ids) y mapeado contra Catálogo/Stock/Usuarios de Entrega 1 —
  0 regresiones reproducidas, 18 ids N/A justificados por módulo inexistente en esta entrega. Revisión de
  código completa por capa (Domain/Application/Infrastructure/Web) + `dotnet build` (0 errores). Detectados
  y corregidos 2 defectos de ortografía (D1 "Si, eliminar"→"Sí, eliminar" en 4 vistas; D2 "Exito"→"Éxito"
  en `_Layout.cshtml`) bajo la regla nueva de `25-frontend-design-system.instructions.md`. Documentado
  defecto D3 (fuera de alcance, archivo preexistente) y D4 (informativo, no bloqueante). Recomendación:
  GO condicionado a aplicar la migración `EntregaUno_CatalogoStockUsuarios` antes de cualquier prueba en
  caliente del cliente.
