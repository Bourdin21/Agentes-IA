# Memoria - QA

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-08-10

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
