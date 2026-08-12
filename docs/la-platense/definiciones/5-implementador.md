# Memoria - Implementador

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-08-10 (v2 — ajuste puntual sobre Entrega 1 ya en GO: rol Administrador + redirect post-login)

## Definiciones vigentes

### Estrategia de ramas Git por entrega (NUEVO, pedido explícito de Joaquín 2026-08-10)

Pedido: desarrollar las 3 entregas en 3 ramas separadas en cascada, con re-entrega y merge hacia adelante cuando una entrega ya delivered recibe mejoras/fixes post-entrega.

**Estructura creada:**
- `master` (rama por defecto del repo local, protegida como "lo ya entregado/production"): en `f5e6af9`, HEAD de Entrega 1.
- `entrega-1` ← creada desde `master` (mismo commit `f5e6af9`). Es donde se aplican las mejoras/fixes que surjan de la prueba del cliente sobre la Entrega 1 ya entregada.
- `entrega-2` ← creada desde `entrega-1`. Es donde se desarrolla la Entrega 2 (Ventas/AFIP/Caja/Entregas/Dashboard Corte 1).
- `entrega-3` ← creada desde `entrega-2`. Es donde se desarrolla la Entrega 3 (Compras/CtaCtes/Presupuestos/Devoluciones/Dashboard Corte final).

Las 3 ramas están pusheadas a `origin` (`git@gitlab.com:olvidata/ferreteria-la-platense.git`), cada una trackeando su par remoto.

**Flujo de trabajo (ciclo que se repite por cada entrega):**
1. Se desarrolla la entrega N en su rama `entrega-N`.
2. Se entrega al cliente para prueba (build + migración aplicada + guía de pasos manuales).
3. El cliente prueba y pide mejoras/fixes → se aplican **en la rama `entrega-N`** (no en una rama nueva).
4. Se re-entrega (vuelta al paso 2 tantas veces como haga falta).
5. Una vez aprobada la entrega N, se **mergea `entrega-N` hacia adelante** en todas las ramas de entregas posteriores todavía no entregadas (ej. al cerrar `entrega-1`: merge `entrega-1` → `entrega-2` y `entrega-1` → `entrega-3`), para que ningún fix se pierda cuando esas entregas posteriores continúen su propio desarrollo. También se mergea `entrega-N` → `master` (production) en este punto.
6. Se repite el ciclo con la entrega siguiente: mientras se desarrolla/prueba `entrega-2`, pueden seguir llegando mejoras sobre `entrega-1` — cada vez que eso pase, re-mergear `entrega-1` → `entrega-2` (y → `entrega-3` si ya existe contenido ahí) antes de la entrega de N+1.

**Regla operativa para el Implementador/QA:** antes de empezar a trabajar en una mejora o fix, confirmar en qué rama corresponde (la entrega ya entregada que la pide, NO necesariamente la rama activa de desarrollo) y hacer `git merge --no-ff entrega-N` hacia las ramas posteriores inmediatamente después de aplicar el fix, para minimizar drift entre ramas. No commitear el mismo fix de forma independiente en más de una rama (siempre merge, nunca reaplicar el cambio a mano en cada rama).

**Riesgo declarado:** el repo remoto ya tenía una rama `main` con un `README.md` inicial (commit `20e7f92`, historia no relacionada a la de `master`) creada por GitLab al momento de crear el proyecto — no se tocó, sigue siendo la rama por defecto en GitLab aunque todo el código real vive en `master`/`entrega-*`. Pendiente: decidir con Joaquín si en algún momento se hace merge/reemplazo de `main` para que coincida con la rama por defecto real del código, o si se cambia la default branch del proyecto en GitLab a `master`.

### Plan de entregas funcionales incrementales (NUEVO, pedido explícito de Joaquín 2026-08-10)

Pedido: dividir la Implementación (101h Etapa 1 + 38h Etapa 2 = 139h totales, ya presupuestadas y aprobadas por el cliente) en **3 entregas funcionales** que el cliente pueda empezar a probar/usar de forma incremental, en vez de esperar al cierre total del proyecto. Motivo declarado: dar dinamismo al proyecto y entregar valor real antes de tiempo.

**Criterio de armado:** cada entrega es un conjunto de módulos con dependencias satisfechas únicamente por entregas anteriores (nunca hacia adelante) — ver mapa de dependencias en `3-arquitecto-mvc.md` — y agrupados temáticamente para que el cliente pueda probar un ciclo de trabajo coherente, no piezas sueltas. El total de horas coincide exacto con el WBS ya aprobado (139h) — **no es una re-estimación**, es una reorganización de secuencia de entrega sobre el mismo alcance y precio ya cerrado con el cliente.

#### Entrega 1 — Fundamentos: Catálogo, Stock y Usuarios (30h)

| Módulo (ref. WBS) | M (h) |
|---|---:|
| 1. Usuarios y roles (admin/vendedor/repartidor) | 5 |
| 2. Catálogo de productos (marca/modelo/categoría/IVA/descuento) | 9 |
| 3. Unidades de medida y conversión compra↔venta | 5 |
| 4. Stock + puesta a punto inicial (ABC, ajuste manual auditado, arranque con negativo permitido) | 8 |
| 11. Código de barras (vinculación al producto) | 3 |
| **Subtotal** | **30** |

**Por qué va primero:** no depende de ningún módulo de Ventas/Compras/Caja — es 100% autocontenida. Ataca directamente el problema real más urgente que el cliente declaró en el relevamiento ("hoy no tenemos stock confiable, se maneja de memoria por la rotación") antes de que el resto del sistema esté terminado. El cliente puede empezar a cargar su catálogo real y clasificar ABC mientras se construyen las entregas 2 y 3.

**Qué puede probar el cliente al cierre de esta entrega:** alta/edición de usuarios por rol; alta de marcas/modelos/categorías; alta de productos con conversión de unidad de compra↔venta; clasificación ABC de productos; ajuste manual de stock con motivo auditado; vinculación de código de barras a un producto.

#### Entrega 2 — Motor de ventas: Ventas, Facturación AFIP, Caja y Entregas (61h)

| Módulo (ref. WBS) | M (h) |
|---|---:|
| 5. Ventas + CC clientes (workflow Borrador→Facturada, recargo cuotas) | 23 |
| 6. Facturación AFIP (Factura) | 7 |
| 8. Caja (cierre diario + mensual) | 7 |
| 9. Gastos varios | 4 |
| 15. Entregas a domicilio (markup, propia/tercerizada) | 8 |
| 10. Dashboard — **Corte 1**: nivel 1 "estado del día" + nivel 3 "tendencias" | 12 |
| **Subtotal** | **61** |

**Por qué va segunda:** depende de Producto (Entrega 1). Es el ciclo diario de venta — la operación central del negocio — y concentra el mayor riesgo técnico del proyecto (workflow editable + integración AFIP), por lo que queda aislada en su propia entrega para poder dedicarle foco de prueba sin bloquear el resto. Se adelanta "Entregas a domicilio" desde la Etapa 2 original porque el nivel 1 del Dashboard necesita datos de entregas pendientes del día — sin este adelanto, el primer corte del dashboard quedaría incompleto.

**Dashboard en 2 cortes (no es una re-estimación, es fasear el mismo módulo de 12h ya presupuestado):** el diseño ya define el dashboard en 3 niveles jerárquicos (día / salud financiera / tendencias — ver `2-disenador-funcional.md` flujo 6). Nivel 1 (ventas de hoy, caja del día, entregas pendientes) y nivel 3 (gastos del mes, top productos, stock crítico) solo necesitan datos que ya existen al cierre de esta entrega. Nivel 2 (cobros/pagos pendientes, saldo de caja consolidado) necesita CC proveedores y el consolidado del negocio — ver Entrega 3.

**Qué puede probar el cliente al cierre de esta entrega:** venta rápida con carrito editable (cantidad/precio/IVA/descuento por ítem) en estado Borrador; pago mixto (efectivo + tarjeta + fiado) con recargo de cuotas calculado; emisión de comprobante AFIP real; fiado con seguimiento de saldo por cliente; cierre de caja diario y mensual; registro de gastos; seguimiento de entregas a domicilio; primer corte del dashboard con datos reales de venta/caja/stock.

#### Entrega 3 — Ciclo completo: Compras, Cuentas corrientes y Cierre de negocio (48h)

| Módulo (ref. WBS) | M (h) |
|---|---:|
| 7. Proveedores + compras (TC propio, % descuento, importación de listas) | 18 |
| 12. Cuenta corriente de empleados (autoservicio) | 4 |
| 13. Cuenta corriente propia del negocio (consolidado) | 5 |
| 14. Presupuestos y cotizaciones en PDF | 8 |
| 16. Aumento masivo de precios (categoría/proveedor/marca) | 4 |
| 17. Devoluciones de mercadería + Notas de crédito/débito AFIP | 9 |
| 10. Dashboard — **Corte final**: nivel 2 "salud financiera" | (incluido en los 12h de Entrega 2) |
| **Subtotal** | **48** |

**Por qué va tercera:** Devoluciones/NC depende de Venta Facturada + AFIP (Entrega 2). Aumento masivo por proveedor depende de Proveedor (mismo módulo, esta entrega). CtaCte consolidada del negocio depende de Caja+Gastos (Entrega 2) y de Compras (esta entrega). Ninguno de estos módulos es prerequisito de las entregas anteriores — cierran el ciclo completo del negocio (compras, cuentas corrientes, devoluciones) sin bloquear valor entregado antes.

*Nota: "Cuenta corriente de empleados" (módulo 12) solo depende de Usuarios (Entrega 1) — no tiene bloqueo técnico para adelantarse a la Entrega 2 si el cliente prioriza verlo antes. Se mantiene en Entrega 3 por afinidad temática (cuentas corrientes) salvo pedido explícito de reordenar.*

**Qué puede probar el cliente al cierre de esta entrega (= cierre del proyecto):** registro de compras con actualización de stock; importación de lista de precios de proveedor con TC propio + % descuento; cuenta corriente de proveedores; cuenta corriente de empleados (autoservicio); cuenta corriente consolidada del negocio; presupuestos/cotizaciones en PDF; aumento masivo de precios; devolución de mercadería con nota de crédito AFIP y anulación de venta; dashboard completo (3 niveles).

#### Verificación de consistencia con el presupuesto aprobado

- Suma de las 3 entregas: 30h + 61h + 48h = **139h = Etapa 1 (101h) + Etapa 2 (38h) del WBS aprobado.** Ningún módulo se agregó ni se quitó — solo se reordenó la secuencia de entrega.
- El precio ya cerrado con el cliente (USD 1.500/3 pagos o USD 1.800/12 pagos) **no cambia** — esto es una decisión de secuenciación de Implementación, no una re-cotización. Ver `4-presupuestador.md`.
- Encaje comercial natural (a proponer, no impuesto): las 3 entregas funcionales quedan alineadas 1 a 1 con la modalidad de pago en 3 cuotas si el cliente la elige — cada entrega cerrada puede disparar el cobro de la cuota correspondiente. Si el cliente eligió la modalidad de 12 pagos, las entregas funcionan igual como hitos de prueba, sin atarse a cuotas individuales.

### Archivos y capas modificadas

**Cierre de Entrega 1 (2026-08-10) — Catálogo, Stock y Usuarios.** Repo: `C:\Sistemas\Ferreteria La Platense`, solución `FerreteriaLaPlatense.slnx`.

Reutilización aplicada (ver escaneo debajo): patrón de `Marca`/`Modelo`/`Categoria` de `ShowroomGriffin`, patrón de `AjusteStock`/`StockController` de `ShowroomGriffin`, helper `DataTableRequestHelper` de `marihogar`.

- **Domain** (`FerreteriaLaPlatense.Domain`):
  - `Enums/UnidadMedida.cs` (Unidad/Peso/Metro/Bulto), `Enums/ClasificacionABC.cs` (A/B/C) — nuevos.
  - `Entities/ICatalogoSimpleEntity.cs` — contrato común (Nombre/Activo) para no triplicar el CRUD de los 3 catálogos simples.
  - `Entities/Marca.cs`, `Entities/Modelo.cs`, `Entities/Categoria.cs` — nuevas, heredan `SoftDestroyable` + `ICatalogoSimpleEntity` (Nombre, Activo).
  - `Entities/Producto.cs` — nueva, núcleo de la entrega (todas las columnas de `3-arquitecto-mvc.md`: precios, IVA, unidades de compra/venta + `FactorConversion`, `Stock`, `StockMinimo`, `ClasificacionABC`, `StockVerificado`, `CodigoBarras`).
  - `Entities/AjusteStock.cs` — nueva (ProductoId, Fecha, UsuarioId, CantidadAnterior, CantidadNueva, Motivo).
- **Application** (`FerreteriaLaPlatense.Application`):
  - `DTOs/CatalogoItemDto.cs`, `DTOs/ProductoDtos.cs` (ProductoListItemDto/ProductoDto/ProductoLookupDto), `DTOs/StockDtos.cs` (StockListItemDto con `Alerta` calculada, AjusteStockDto, AjusteStockHistorialItemDto) — nuevos.
  - `Interfaces/ICatalogoSimpleService.cs` (+ marcadoras `IMarcaService`/`IModeloService`/`ICategoriaService`), `Interfaces/IProductoService.cs`, `Interfaces/IUnidadMedidaConversionService.cs`, `Interfaces/IAjusteStockService.cs`, `Interfaces/ICodigoBarrasLookupService.cs` — nuevos, todos los contratos funcionales pedidos por `2-disenador-funcional.md`.
- **Infrastructure** (`FerreteriaLaPlatense.Infrastructure`):
  - `Data/AppDbContext.cs` — agregados `DbSet<Marca/Modelo/Categoria/Producto/AjusteStock>` + Fluent API (índices únicos en `Nombre`/`Codigo`/`CodigoBarras`, precisión decimal, `OnDelete(Restrict)` en las FK a los catálogos).
  - `Data/SeedData.cs` — agregados roles `Vendedor` y `Repartidor` al array de seed (antes solo `SuperUsuario`).
  - `Services/CatalogoSimpleServiceBase.cs` — clase base genérica (CRUD + listado DataTable + validación de unicidad + bloqueo de baja si el catálogo está en uso por un Producto) reutilizada por `MarcaService`, `ModeloService`, `CategoriaService`.
  - `Services/ProductoService.cs` — CRUD + `ListarAsync` (DataTable con filtros) + validación de negocio en el Service (R4: `FactorConversion` obligatorio y > 0 si `UnidadCompra != UnidadVenta`; unicidad de `Codigo`/`CodigoBarras`; IVA en {10,5; 21}).
  - `Services/UnidadMedidaConversionService.cs` — cálculo simple (multiplicación por `FactorConversion`), sin precedente exacto en el historial, tal como anticipó `3-arquitecto-mvc.md`.
  - `Services/AjusteStockService.cs` — listado de Stock con `Alerta` (stock negativo o bajo el mínimo), `AplicarAjusteAsync` (registra auditoría + pisa `Producto.Stock` + `StockVerificado = true`), `HistorialAsync`.
  - `Services/CodigoBarrasLookupService.cs` — resuelve producto por `CodigoBarras` o `Codigo`.
  - `DependencyInjection.cs` — registrados como Scoped: `IMarcaService`, `IModeloService`, `ICategoriaService`, `IProductoService`, `IUnidadMedidaConversionService`, `IAjusteStockService`, `ICodigoBarrasLookupService`.
- **Web** (`FerreteriaLaPlatense.Web`):
  - `Helpers/DataTableRequestHelper.cs` — parseo estándar de `Request.Form` a `DataTableRequest` (adaptado de `marihogar`), reutilizado por todos los controllers nuevos.
  - `Models/CatalogoSimpleFormViewModel.cs`, `Models/ProductoFormViewModel.cs` (con combos `SelectListItem` para Marca/Modelo/Categoria), `Models/AjusteStockViewModel.cs` — nuevos.
  - `Controllers/MarcasController.cs`, `Controllers/ModelosController.cs`, `Controllers/CategoriasController.cs` — CRUD + `Listar` (DataTable server-side) + `ListarActivas` (combo). Policy `RequireCatalogoConsulta` a nivel de clase (lectura), `RequireSuperUsuario` en Create/Edit/Delete.
  - `Controllers/ProductosController.cs` — CRUD + `Listar` (DataTable con filtros: texto libre, Marca, Modelo, Categoria, rango de Precio, rango de Stock) + `BuscarPorCodigoBarras` (endpoint de prueba de `ICodigoBarrasLookupService`, reutilizable por Ventas en la Entrega 2). Combos en Editar se inicializan con la Marca/Modelo/Categoria ya asignada aunque esté inactiva (regla `32-estandares-qa-implementador.instructions.md`).
  - `Controllers/StockController.cs` — `Listar` (DataTable con alerta), `Ajuste` (GET/POST, solo Admin), `Historial`/`HistorialListar`.
  - `Controllers/UsersController.cs` — `GetAssignableRoles()` extendido a `[SuperUsuario, Vendedor, Repartidor]` (antes solo `SuperUsuario`); no se reescribió el resto del controller ni las Views de Usuarios (ya soportaban una lista dinámica de roles).
  - `Program.cs` — nueva policy `RequireCatalogoConsulta` (`SuperUsuario` + `Vendedor`).
  - `Views/Marcas/*`, `Views/Modelos/*`, `Views/Categorias/*` (Index con DataTable server-side + filtros Nombre/Estado, Create, Edit), `Views/Productos/*` (Index con DataTable + filtros por cada columna visible + buscador de código de barras, Create, Edit con card de Stock de solo lectura), `Views/Stock/*` (Index con alerta visual, Ajuste, Historial) — nuevas, con SweetAlert2 para confirmaciones destructivas y DataTables server-side en todos los listados.
  - `Views/Shared/_Layout.cshtml` — nueva sección de sidebar "Catálogo" (Productos/Stock/Marcas/Modelos/Categorías), visible a `SuperUsuario` y `Vendedor`, respaldada por `[Authorize(Policy=...)]` en cada controller (defensa en profundidad).

**Escaneo de reutilización realizado antes de codificar:** se revisó `docs/ShowroomGriffin/definiciones/5-implementador.md` (no existe un `5-implementador.md` de reutilización directa en ese proyecto, pero sí código de referencia real en `C:\Sistemas\ShowroomGriffin` — `Marca`/`MarcaConfiguration`/`MarcasController`/`MarcaService` y `AjusteStock`/`AjusteStockConfiguration`/`StockController`) y `marihogar` (`CategoriaService`, `DataTableRequestHelper`). Decisión: reutilizar el patrón (estructura de entidad, Fluent API, forma del Controller/Service) adaptándolo a las diferencias reales de este proyecto — acá el repositorio usa `IRepository<T>` genérico para las mutaciones (en vez de `AppDbContext` directo como en ShowroomGriffin) y el stock vive directamente en `Producto` (no hay `Stock`/`VarianteProducto` separados, porque este catálogo no tiene variantes).

### Migraciones EF generadas
- `EntregaUno_CatalogoStockUsuarios` (20260810165155) — **primera migración real del proyecto** (no había ninguna previa). Incluye: todo el esquema base de Identity (`AspNetUsers`, `AspNetRoles`, etc., `Notifications`, `PreferenciasUsuario` — ya existían en código pero nunca se habían migrado) + las tablas nuevas de esta entrega: `Marcas`, `Modelos`, `Categorias` (Nombre único, Activo), `Productos` (FK Restrict a Marca/Modelo/Categoria, índices únicos en `Codigo` y `CodigoBarras`, decimales con precisión `18,2`/`5,2`/`18,3` según el campo), `AjustesStock` (FK Restrict a Producto).
- Generada con `dotnet ef migrations add EntregaUno_CatalogoStockUsuarios --project FerreteriaLaPlatense.Infrastructure --startup-project FerreteriaLaPlatense.Web`. **No se aplicó contra ninguna base de datos** (el Implementador no ejecuta `dotnet ef database update` ni levanta la app — ver guía de verificación manual en la sección de pruebas). El `HostAbortedException` que aparece en la consola al generarla es el comportamiter normal de la tooling de EF Core (aborta el host de diseño a propósito), no un error.
- Impacto: sobre una base nueva, `database update` crea todo el esquema. Sobre una base ya con datos reales del cliente (no es el caso hoy — el proyecto no tiene datos de producción todavía), habría que revisar si `AspNetUsers`/`Notifications`/`PreferenciasUsuario` ya existen antes de aplicarla.

### Riesgos residuales
- Pregunta abierta sin cerrar con el cliente (no bloquea Entrega 1, sí bloquea el módulo de anulación en Entrega 3): quién puede anular una venta facturada (¿solo admin o también vendedor?) y si hay límite de tiempo — ver `1-analista-funcional.md` §9.
- Riesgos técnicos ya declarados en `3-arquitecto-mvc.md` (venta con stock negativo permitido, conversión de unidades sin precedente, workflow Venta editable, importación de listas por proveedor no 100% genérica) se mantienen vigentes, sin cambios por esta reorganización.
- **Nuevo (Entrega 1):** `Producto.CodigoBarras` es único a nivel de base (MySQL permite múltiples `NULL`, así que productos sin código de barras coexisten sin problema) — si el cliente en algún momento pide códigos de barras "sugeridos" no únicos (ej. balanza con código variable por peso) el modelo actual no lo soporta y habría que revisar el índice único.
- **Nuevo (Entrega 1):** la hipótesis de `2-disenador-funcional.md` ("el factor de conversión es fijo por producto") queda **codificada tal cual** en `UnidadMedidaConversionService` — si el cliente confirma que un mismo producto llega en bultos de distinto tamaño según el proveedor, este servicio y el modelo de `Producto` necesitan revisión antes de la Entrega 2 (Compras).
- **Nuevo (Entrega 1):** al ajustar manualmente el stock (`AjusteStockService.AplicarAjusteAsync`), la cantidad nueva **pisa** el stock actual (no lo suma/resta) — es el comportamiento pedido ("cantidad nueva", no "cantidad a sumar"); confirmar con el cliente que esto matchea su expectativa operativa antes de que lo use el personal de mostrador.
- **Nuevo (Entrega 1):** `Marca`/`Modelo`/`Categoria` bloquean la baja física (soft delete) si hay algún `Producto` activo que los referencia (mensaje explícito, sugiere desactivar en su lugar) — esto es una regla de integridad agregada por el Implementador (no estaba explícita en `3-arquitecto-mvc.md`), coherente con el patrón ya usado en `marihogar`.
- **Nuevo (Entrega 1):** no se generó ninguna migración de datos/seed para Marca/Modelo/Categoria — el catálogo arranca vacío, el cliente carga sus propias marcas/modelos/categorías antes de poder cargar productos.

### Ajuste puntual (2026-08-10, post-QA/GO) — rol Administrador + redirect post-login a Stock

Modificacion sobre modulo existente (Entrega 1 ya en GO), no una entrega nueva. Pedido explicito de Joaquin (ver `trazabilidad.md` 2026-08-10 17:00 y 17:30): agregar un rol **Administrador** con acceso a todo el sistema salvo las herramientas tecnicas de `SystemController` (exclusivas de `SuperUsuario`, acceso tecnico de Olvidata Soft), y redirigir a `Stock/Index` despues del login en vez de `Home/Index`.

- **Infrastructure** (`FerreteriaLaPlatense.Infrastructure`):
  - `Data/SeedData.cs` — agregado `public const string RolAdministrador = "Administrador"` y sumado al array `roles` de `InitializeAsync` (se crea automaticamente en el seed).
- **Web** (`FerreteriaLaPlatense.Web`):
  - `Program.cs` — nueva policy `RequireAdministracion` (`SuperUsuario` + `Administrador`); `RequireCatalogoConsulta` extendida para incluir `Administrador`. `RequireSuperUsuario` sin cambios (sigue exclusiva de `SystemController` y `/health`).
  - `Controllers/MarcasController.cs`, `Controllers/ModelosController.cs`, `Controllers/CategoriasController.cs`, `Controllers/ProductosController.cs`, `Controllers/StockController.cs` — todas las acciones de escritura (`Create`/`Edit`/`Delete`/`Ajuste`) cambiaron de `[Authorize(Policy = "RequireSuperUsuario")]` a `[Authorize(Policy = "RequireAdministracion")]`.
  - `Controllers/UsersController.cs` — atributo de clase cambiado a `RequireAdministracion`; `GetAssignableRoles()` extendido a `[SuperUsuario, Administrador, Vendedor, Repartidor]`. Administrador gestiona usuarios igual que SuperUsuario, incluida la asignacion del rol `SuperUsuario` a otro usuario desde esta pantalla — decision de negocio confirmada explicitamente por Joaquin, no limitada por criterio propio.
  - `Controllers/SystemController.cs` — **no tocado**, sigue exclusivo de `RequireSuperUsuario` (unica excepcion explicita del pedido).
  - `Controllers/AccountController.cs` — `Login` GET (shortcut si ya autenticado) y `Login` POST (exito) redirigen por defecto a `Stock/Index` en vez de `Home/Index`; se preserva `returnUrl` si el usuario venia de un deep-link. `Logout` y `AccessDenied` sin cambios.
  - `Views/Home/Index.cshtml`, `Views/Stock/Index.cshtml`, `Views/Marcas/Index.cshtml`, `Views/Modelos/Index.cshtml`, `Views/Categorias/Index.cshtml`, `Views/Productos/Index.cshtml` — `User.IsInRole("SuperUsuario")` cambiado a `(User.IsInRole("SuperUsuario") || User.IsInRole("Administrador"))` en los botones de alta/edicion/baja y en la card de "Administrar Usuarios" de Home.
  - `Views/Shared/_Layout.cshtml` — sidebar "Catalogo" (Productos/Stock/Marcas/Modelos/Categorias) extendido a `SuperUsuario || Administrador || Vendedor`. Sidebar "Sistema" reestructurado: el link "Sistema / Email" (`SystemController`) quedo aislado en un `if` propio exclusivo de `SuperUsuario`; "Usuarios" y "Notificaciones" ahora se muestran tambien a `Administrador` (el `if` contenedor paso a `SuperUsuario || Administrador`).
- **Migraciones EF**: ninguna — los roles de Identity (`AspNetRoles`) no requieren cambio de esquema, se crean via seed en `InitializeAsync`.
- **Build**: `dotnet build FerreteriaLaPlatense.slnx` → 0 errores, mismas advertencias preexistentes (NU1902 MailKit/MimeKit, CS0114 en `HomeController`).
- **No se ejecuto smoke test funcional** (regla del rol Implementador) — ver guia de pruebas manuales mas abajo.

**Correccion inmediata (2026-08-10, minutos despues del cierre anterior):** Joaquin corrigio el alcance — gestion de Usuarios y Herramientas del Sistema quedan **exclusivas de `SuperUsuario`**, Administrador es "todo lo demas" (Catalogo/Stock, que si quedan en `RequireAdministracion`). Revertido:
- `Controllers/UsersController.cs` — atributo de clase vuelto a `[Authorize(Policy = "RequireSuperUsuario")]` (estaba en `RequireAdministracion`). `GetAssignableRoles()` sin cambios (Administrador sigue siendo un rol asignable desde esta pantalla, solo que ahora unicamente SuperUsuario puede entrar a asignarlo).
- `Views/Shared/_Layout.cshtml` — separado el bloque: "Usuarios" y "Sistema / Email" quedan bajo `@if (User.IsInRole("SuperUsuario"))` exclusivamente; "Notificaciones" se sacó de ese `if` (no tiene restriccion de rol en `NotificationsController`, es personal de cualquier usuario autenticado) para que Administrador (y en rigor cualquier rol) la siga viendo.
- Build no pudo confirmar el paso final de copia (`MSB3027`, archivo `.dll` en uso por un proceso `dotnet FerreteriaLaPlatense.Web.dll` corriendo en paralelo, PID 22748) — 0 errores de compilacion de codigo, solo fallo el copy-to-output por lock de archivo. Cambios de bajo riesgo (revertir un valor de atributo + condicionales Razor con sintaxis ya probada en otras vistas del mismo archivo).

### Cierre de Entrega 2 — ola 1: Ventas, CC Clientes, AFIP (2026-08-11)

Repo: `C:\Sistemas\Ferreteria La Platense`, rama `entrega-2` (checkout activo, no se cambió de rama). Esta es la primera mitad de la Entrega 2 — motor de ventas (Cliente/CC cliente/Venta/AFIP). La segunda mitad (Caja/Gastos/Entregas/Dashboard Corte 1) queda para una tarea siguiente, dependiente de esta.

**Corrección aplicada sobre `3-arquitecto-mvc.md` (verificada antes de codificar, confirmada por el orquestador):** "Ventas + CC clientes" NO reusa `marihogar` para el ledger de cuenta corriente — la `Venta` de marihogar no tiene entidad `Cliente` (es texto libre) ni ledger de saldo. Se reutilizó la **forma** de `Venta`/`VentaItem`/`PagoVenta`/`VentaService`/`VentasController` de `marihogar` (adaptada: máquina de estados nueva Borrador/Facturada/Anulada en vez de Pendiente/PagadaParcial/Pagada/Cancelada, porque acá la venta nace editable en vez de crearse completa en una transacción). El ledger de cuenta corriente se adaptó del patrón `MovimientoCCProveedor`/`Proveedor` de `vino-y-se-fue` (`ClienteId` en vez de `ProveedorId` singleton) — **confirmado por lectura directa de `Proveedor.cs` que no persiste una columna de saldo**, por lo que `Cliente` tampoco la persiste (contradice literalmente a `3-arquitecto-mvc.md`, que sí la lista — se documenta como imprecisión de ese documento, no se sigue literal). La integración AFIP (`AfipService`/`IAfipService`/`AfipSettings`/`AfipTokenCache`, WSAA+WSFEv1 armado a mano con `System.Xml.Linq` + firma CMS con `System.Security.Cryptography.Pkcs`) se portó tal cual desde `marihogar`, sin cambios al mecanismo, solo adaptando namespaces y el mapeo DocTipo/DocNro hacia el modelo de `Cliente` de este proyecto.

**Domain** (`FerreteriaLaPlatense.Domain`):
- `Enums/EstadoVenta.cs` (Borrador/Facturada/Anulada — enum nuevo, no reutiliza el `EstadoVenta` de marihogar), `Enums/MedioPago.cs` (Efectivo/Debito/CreditoCuotas/CuentaCorriente), `Enums/CondicionIVA.cs` (ResponsableInscripto/Monotributo/ConsumidorFinal/Exento), `Enums/TipoMovimientoCC.cs` (Debito/Credito, adaptado de vino-y-se-fue), `Enums/OrigenMovimientoCC.cs` (VentaFiado/Pago/Ajuste), `Enums/TipoComprobanteAfip.cs` (FacturaA=1/FacturaB=6, coincide con el código AFIP "CbteTipo").
- `Entities/Cliente.cs` — Nombre, CuitDni (nullable, único), CondicionIVA, Telefono. **Sin columna de saldo** (ver corrección arriba).
- `Entities/MovimientoCCCliente.cs` — ClienteId, Fecha, Tipo, Origen, Importe, Referencia, VentaId (nullable, trazabilidad), UsuarioId (patrón explícito igual a `AjusteStock.UsuarioId` de Entrega 1, sin navegación a Identity).
- `Entities/Venta.cs` — Fecha, ClienteId (nullable = Consumidor Final), Estado, Subtotal, TotalIVA, Total, TipoComprobanteAfip (nullable), CAE, VencimientoCAE, NumeroComprobante, VendedorId, colecciones Items/Pagos.
- `Entities/ItemVenta.cs` — Cantidad **decimal** (no `int` como en marihogar, porque el catálogo de este proyecto admite `UnidadVenta` fraccionable — Peso/Metro), UnidadVenta copiada del Producto al momento de la venta (snapshot, no se recalcula si el producto cambia después), PrecioUnitario, PorcentajeIVA, Descuento, Recargo (montos monetarios, no porcentajes — asunción documentada, ver riesgos), Subtotal.
- `Entities/PagoVenta.cs` — MedioPago, Monto (importe base financiado), Cuotas/PorcentajeRecargoAplicado (solo si CreditoCuotas, validado en el Service).

**Application** (`FerreteriaLaPlatense.Application`):
- `DTOs/ClienteDtos.cs`, `DTOs/MovimientoCCClienteDtos.cs`, `DTOs/VentaDtos.cs` (VentaListItemDto/VentaDetalleDto con `TotalPagos`/`SaldoPendiente` calculados/ItemVentaDto/PagoVentaDto + DTOs de entrada `ItemVentaInputDto`/`PagoVentaInputDto`/`GuardarVentaBorradorDto`), `DTOs/AfipDtos.cs` (portado de marihogar).
- `Settings/AfipSettings.cs` (portado de marihogar), `Settings/RecargoCuotasSettings.cs` (nuevo — dictionary cuotas→% configurable en `appsettings.json`, sin pantalla dedicada, ver riesgos).
- `Interfaces/IClienteService.cs`, `ICuentaCorrienteClienteService.cs`, `IRecargoCuotasService.cs`, `IVentaWorkflowService.cs`, `IAfipService.cs` (portado de marihogar) — todos los contratos ya definidos en `2-disenador-funcional.md`.
- `Interfaces/IProductoService.cs` (Entrega 1, **modificado mínimamente**) — agregado `BuscarParaVentaAsync(string?)` para que la pantalla de Venta reutilice el mismo servicio de Catálogo en vez de duplicar el query.

**Infrastructure** (`FerreteriaLaPlatense.Infrastructure`):
- `Data/AppDbContext.cs` — agregados `DbSet<Cliente/MovimientoCCCliente/Venta/ItemVenta/PagoVenta>` + Fluent API (índice único en `Cliente.CuitDni` permitiendo múltiples NULL igual que `Producto.CodigoBarras`; `OnDelete(Restrict)` en FKs a Cliente/Producto; `OnDelete(Cascade)` en ItemVenta/PagoVenta → Venta; decimales con precisión `18,2`/`5,2`/`18,3` según el campo).
- `Services/ClienteService.cs` — CRUD + `ListarAsync` (DataTable con Saldo calculado por subconsulta) + `BuscarAsync` (Select2).
- `Services/CuentaCorrienteClienteService.cs` — `ObtenerSaldoAsync` (suma Debito-Credito, sin persistir), `ListarMovimientosAsync` (DataTable con filtro de fecha/tipo/origen), `RegistrarMovimientoAsync` (sin SaveChanges propio — lo controla `VentaWorkflowService` como parte de la transacción de confirmación).
- `Services/RecargoCuotasService.cs` — resuelve % desde `RecargoCuotasSettings`, nunca confía en un porcentaje enviado por el cliente.
- `Services/VentaWorkflowService.cs` — el más grande y de mayor riesgo: `GuardarBorradorAsync` (upsert completo de Items/Pagos con soft-delete de los quitados, nunca `Remove` físico), `CancelarBorradorAsync`, `ConfirmarYFacturarAsync` (valida guardas → llama AFIP **primero** → solo si `Exito=true` descuenta stock + genera `MovimientoCCCliente` + persiste CAE + pasa a Facturada, todo en una única `SaveChangesAsync`; si AFIP falla no se toca nada, la venta queda en Borrador reintentable).
- `Services/AfipService.cs` + `Services/AfipTokenCache.cs` — portados tal cual de marihogar (mismo WSAA/WSFEv1 armado a mano), adaptados a namespaces y a `MapearCondicionIvaReceptor`/`DeterminarDocumentoReceptor` de este proyecto.
- `Services/ProductoService.cs` (Entrega 1, modificado mínimamente) — agregado `BuscarParaVentaAsync`.
- `DependencyInjection.cs` — registrados `IClienteService`, `ICuentaCorrienteClienteService`, `IRecargoCuotasService`, `IVentaWorkflowService` (Scoped), `IAfipService` (Scoped) + `AfipTokenCache` (Singleton, cachea el token WSAA entre requests) + `IOptions<AfipSettings>`/`IOptions<RecargoCuotasSettings>` + `HttpClient` nombrado `"Afip"`.

**Web** (`FerreteriaLaPlatense.Web`):
- `Models/ClienteFormViewModel.cs`, `Models/VentaViewModels.cs` (`VentaEditableViewModel`/`ItemVentaViewModel`/`PagoViewModel`, tal como los definió `2-disenador-funcional.md`).
- `Controllers/ClientesController.cs` — CRUD + `Listar` (DataTable con filtro Nombre/CondicionIVA/Saldo) + `Buscar` (Select2) + `CuentaCorriente`/`CuentaCorrienteListar` (saldo calculado + historial con filtro de fecha via daterangepicker). Policy `RequireVentas` (Vendedor tiene escritura completa acá, a diferencia de Catálogo).
- `Controllers/VentasController.cs` — `Index`/`Listar` (DataTable con filtro fecha/cliente/estado/total), `Nueva`/`Editar` (pantalla de carrito editable), `GuardarBorrador`, `Cancelar`, `ConfirmarYFacturar`, `Details` (solo lectura, Facturada/Anulada), `BuscarProductos`/`BuscarPorCodigoBarras` (reutiliza `ICodigoBarrasLookupService` de Entrega 1 sin cambios, R11/PF15).
- `Program.cs` — nueva policy `RequireVentas` (`SuperUsuario`+`Administrador`+`Vendedor`, escritura completa en Ventas/Clientes).
- `appsettings.json` — secciones `Afip` (placeholder vacío: `CertificadoPath`/`CUIT` en blanco) y `RecargoCuotas` (seed `{3: 10%, 6: 20%}`, ejemplo editable).
- `Views/Clientes/*` (Index con DataTable+filtros, Create, Edit, CuentaCorriente con saldo destacado + daterangepicker), `Views/Ventas/*` (Index con DataTable+filtros incl. Select2 de cliente, `Editar.cshtml` — carrito dinámico con Select2 de producto + input de escaneo de código de barras + filas de Items/Pagos agregadas/quitadas por JS con reindexado, `Details.cshtml` solo lectura) — SweetAlert2 en confirmaciones de Cancelar/Confirmar y facturar.
- `Views/Shared/_Layout.cshtml` — nueva sección de sidebar "Ventas" (Ventas/Clientes), visible a SuperUsuario/Administrador/Vendedor.

**Migración EF:** `EntregaDos_VentasCCClientesAfip` (20260811132055) — tablas `Clientes`, `Ventas`, `ItemsVenta`, `MovimientosCCCliente`, `PagosVenta`. **No aplicada a ninguna base** (igual que en Entrega 1).

**Build:** `dotnet build FerreteriaLaPlatense.slnx` → 0 errores, mismas advertencias preexistentes (NU1902 MailKit/MimeKit, CS0114 HomeController).

### Riesgos residuales y asunciones (Entrega 2, ola 1)

1. **AFIP sin datos reales (bloqueante solo para probar, no para el código):** no hay CUIT ni certificado `.p12` de La Platense todavía. `AfipService.EmitirAsync` devuelve `Exito=false` con `DetalleError` explícito mientras `Afip:CertificadoPath`/`Afip:CUIT` estén vacíos en `appsettings` — comportamiento igual al ya validado en marihogar, no bloquea el resto del sistema. No hay nada para probar de punta a punta contra AFIP real hasta que el cliente traiga esos datos.
2. **Asunción sobre Descuento/Recargo de `ItemVenta`:** se modelaron como importes monetarios de la línea, no porcentajes — `3-arquitecto-mvc.md` no precisa la unidad. A confirmar con el cliente en la prueba de esta entrega.
3. **Asunción sobre el recargo de cuotas:** a diferencia de marihogar (donde el interés es solo informativo), aquí el recargo de `CreditoCuotas` se suma efectivamente al `Venta.Total` (tal como pide `2-disenador-funcional.md`: "el sistema calcula el recargo... y lo suma al total antes de confirmar"). El `PagoVenta.Monto` es el importe **base** financiado; el recargo se calcula aparte (`Monto * %/100`) y se agrega al total — no hay un campo adicional en el modelo para el "monto con recargo", se reconstruye en tiempo de cálculo.
4. **Asunción sobre cobertura de pagos:** se exige que la suma de pagos (+ recargo de cuotas) cubra el `Total` de la venta, **salvo** que exista alguna línea de pago `CuentaCorriente` (en cuyo caso no se exige cobertura completa — el saldo pendiente ahí es intencional, tal como pide el diseño). No hay una regla de "monto exacto restante" automático: el vendedor decide cuánto carga a la cuenta corriente escribiendo el monto de esa línea.
5. **% de recargo por cuotas sin pantalla propia de configuración:** se resolvió con una sección de `appsettings.json` (`RecargoCuotas`) en vez de una pantalla de administración — `2-disenador-funcional.md` no define una pantalla específica para esto. Si el cliente pide poder cambiarlo sin depender de un despliegue/reinicio, hay que migrar `RecargoCuotasSettings` a una entidad con su propio CRUD (el contrato `IRecargoCuotasService` no cambiaría).
6. **Filtro de "Comprobante" no implementado en el listado de Ventas:** la columna "Comprobante" (número/CAE) se muestra en la grilla pero no tiene un filtro de columna dedicado (a diferencia del resto de columnas, que sí cumplen la regla de `25-frontend-design-system.instructions.md`) — desvío menor, documentado para no perderlo de vista en QA.
7. **`Marca`/`Modelo`/`Categoria` y `Producto` no se tocaron** salvo la extensión mínima de `IProductoService`/`ProductoService` (nuevo método `BuscarParaVentaAsync`, aditivo, sin cambiar comportamiento existente).
8. El descuento de stock al facturar permite negativo sin bloquear (R10/PF13, ya resuelto en Entrega 1) — no se agregó ninguna validación nueva de stock en `VentaWorkflowService`.
9. `IUnidadMedidaConversionService` (Entrega 1) **no tiene un call-site real en Venta**: el ítem siempre se carga en `UnidadVenta` (no hay conversión compra→venta en el flujo de venta, eso es exclusivo de Compras). Se documenta en vez de forzar un uso artificial del servicio solo para cumplir la letra del pedido — el servicio queda disponible sin cambios para cuando se implemente Compras.

### Guía de pruebas manuales (Entrega 2, ola 1 — a ejecutar por el cliente/QA, no por el Implementador)

1. Aplicar la migración `EntregaDos_VentasCCClientesAfip` contra la base de desarrollo (`dotnet ef database update`).
2. Alta de Cliente (Responsable Inscripto y Consumidor Final) — verificar que el CUIT/DNI duplicado se rechaza.
3. Venta rápida: crear una venta nueva, agregar 2-3 ítems (por búsqueda y por código de barras), guardar borrador, volver a editar (cambiar cantidad/precio/IVA) y verificar que los totales se recalculan.
4. Pago mixto: efectivo + tarjeta en 3 cuotas — verificar que el recargo se muestra y se suma al total antes de confirmar.
5. Venta con pago a cuenta corriente (requiere Cliente asignado, no Consumidor Final) — confirmar y verificar que aparece el movimiento en `Clientes/CuentaCorriente/{id}` con el saldo actualizado.
6. Intentar confirmar una venta sin ítems, y una venta con pagos insuficientes (sin cuenta corriente) — verificar que ambas quedan bloqueadas con el mensaje de error esperado.
7. Confirmar y facturar una venta sin certificado AFIP configurado — verificar que devuelve el error explícito de "AFIP no está configurado" y la venta queda en Borrador (no se descontó stock).
8. Verificar que el stock del producto efectivamente se descontó tras una facturación exitosa (una vez que haya certificado AFIP de homologación configurado).
9. Cancelar un borrador y verificar que desaparece del listado de Ventas.
10. Verificar permisos: un usuario con rol Vendedor puede crear/editar/facturar ventas y clientes; un usuario sin ninguno de los 3 roles (`SuperUsuario`/`Administrador`/`Vendedor`) recibe 403 en `/Ventas` y `/Clientes`.

### Cierre de Entrega 2 — ola 2: Caja, Gastos, Entregas, Dashboard Corte 1 (2026-08-11)

Repo: `C:\Sistemas\Ferreteria La Platense`, rama `entrega-2` (checkout activo, no se cambió de rama). Esta es la segunda mitad de la Entrega 2 — depende de `Venta`/`ItemVenta`/`PagoVenta`/`IVentaWorkflowService` ya construidos en la ola 1. **Con este cierre, la Entrega 2 completa (61h) queda funcionalmente terminada** — ver marca de cierre al final de esta sección.

**Escaneo de reutilización (antes de codificar):** se revisó `docs/*/definiciones/5-implementador.md` (ningún proyecto documenta el concepto de "cierre de caja" como bloqueo de período — confirma que es desarrollo nuevo, ya anticipado por `3-arquitecto-mvc.md`) y se leyó código real en `C:\Sistemas\marihogar` (`MovimientoCCLocal`, `Gasto`/`CategoriaGasto`/`FormaPagoGasto`, `Entrega`/`EntregaIntento`/`EstadoEntrega`, `DashboardService`/`DashboardController`) y `C:\Sistemas\ganaderia - emo` (`CajaService`/`CajaController`, revisado como referencia secundaria — tampoco modela un "cierre", confirma el mismo hallazgo). Decisión: reutilizar la **forma** de `MovimientoCCLocal` (adaptado como `CajaMovimiento`, con la diferencia explícita de heredar `SoftDestroyable` por convención del estudio, a diferencia del original inmutable de marihogar), reutilizar `Gasto` de marihogar casi directo (agregando `TipoImpactoGasto` para R7, ausente en el original), reutilizar la forma de `Entrega`/`EstadoEntrega` simplificada (sin `EntregaIntento` ni cobro-en-destino vía `PagoVenta`, que no forman parte del alcance de La Platense — no hay pedido funcional de cobro en destino en `1-analista-funcional.md`/`2-disenador-funcional.md`), y reutilizar la forma de `DashboardService`/`DashboardController` resuelta en un único método `ObtenerAsync()` en vez de un endpoint AJAX por KPI (volumen de datos de esta entrega no lo justifica todavía). El cierre diario/mensual (`CierreCajaDiario`/`CierreCajaMensual` + guarda de "no movimiento retroactivo a un día cerrado") es 100% desarrollo nuevo, sin precedente exacto en ningún proyecto del historial.

**Domain** (`FerreteriaLaPlatense.Domain`):
- `Enums/TipoMovimientoCaja.cs` (Ingreso/Egreso — nombre propio para no confundir con `TipoMovimientoCC` del ledger de CC cliente), `Enums/CategoriaGasto.cs` (Alquiler/Servicios/Sueldos/Impuestos/Flete/Otro), `Enums/FormaPagoGasto.cs` (Efectivo/Transferencia/Cheque/Deposito), `Enums/TipoImpactoGasto.cs` (CajaChica/CajaMensual — R7, campo que el `Gasto` de marihogar no tiene), `Enums/TipoEntrega.cs` (Propia/Tercerizada), `Enums/EstadoEntrega.cs` (Pendiente/EnCamino/Entregada/NoEntregada, simplificado de marihogar).
- `Entities/CajaMovimiento.cs` — Fecha/Tipo/Monto/OrigenTipo("Venta"|"Gasto"|"Ajuste")/OrigenId/Descripcion, hereda `SoftDestroyable` (desvío documentado explícitamente respecto del original de marihogar, que es inmutable — acá los ajustes se resuelven con contramovimiento nuevo, nunca editando/borrando el original, así que el soft delete heredado queda sin uso práctico en el flujo normal).
- `Entities/CierreCajaDiario.cs` / `Entities/CierreCajaMensual.cs` — mismo shape (TotalIngresos/TotalEgresos/Saldo/CerradoPorUsuarioId/FechaCierre), índice único en `Fecha` / en `(Anio, Mes)` respectivamente. Pieza sin precedente exacto (ver escaneo arriba).
- `Entities/Gasto.cs` — Fecha/Categoria/Monto/FormaPago/TipoImpacto/Descripcion/Anulado/FechaAnulacion. Igual que en marihogar, un Gasto no se edita después de creado (solo Anular), y la anulación usa un flag `Anulado` propio (no soft delete) para que el gasto anulado siga visible con badge — el query filter global de `SoftDestroyable` lo ocultaría si se usara `DeletedAt`.
- `Entities/Entrega.cs` — VentaId (FK a la `Venta` de este proyecto, `OnDelete(Restrict)`, índice único — máximo 1 Entrega por Venta)/Tipo/CostoBase/PorcentajeMarkup/CostoFinal/Estado/RepartidorId (nullable, string sin FK a Identity, mismo patrón explícito que `Venta.VendedorId`)/Direccion/FechaProgramada/MotivoNoEntrega/FechaEntregada. `PorcentajeMarkup` es un snapshot del valor vigente en `EntregaMarkupSettings` al crear la entrega (mismo criterio de snapshot que `PagoVenta.PorcentajeRecargoAplicado`).

**Application** (`FerreteriaLaPlatense.Application`):
- `Settings/EntregaMarkupSettings.cs` (R2 — mismo criterio que `RecargoCuotasSettings`: appsettings.json en vez de pantalla dedicada, sin precedente de pantalla en `2-disenador-funcional.md`).
- `DTOs/CajaDtos.cs`, `DTOs/GastoDtos.cs`, `DTOs/EntregaDtos.cs`, `DTOs/DashboardDtos.cs` — nuevos.
- `Interfaces/ICajaMovimientoService.cs`, `IGastoService.cs`, `IEntregaService.cs`, `IDashboardService.cs` — nuevos.
- `Interfaces/IProductoService.cs` (Entrega 1, **modificado mínimamente**) — agregado `ContarStockCriticoAsync()` (mismo criterio de alerta que `AjusteStockService`, reutilizado por el Dashboard).

**Infrastructure** (`FerreteriaLaPlatense.Infrastructure`):
- `Data/AppDbContext.cs` — agregados `DbSet<CajaMovimiento/CierreCajaDiario/CierreCajaMensual/Gasto/Entrega>` + Fluent API (índice único `CierreCajaDiario.Fecha`, índice único `(CierreCajaMensual.Anio, Mes)`, índice único `Entrega.VentaId`, decimales con precisión `18,2`/`5,2` según el campo).
- `Services/CajaMovimientoService.cs` — `ListarMovimientosAsync` (DataTable), `EstaCerradoAsync` (guarda de negocio consultada por `VentaWorkflowService`/`GastoService` antes de persistir), `RegistrarMovimientoAsync` (sin `SaveChanges` propio, mismo patrón que `CuentaCorrienteClienteService`), `RegistrarMovimientoManualAsync` (alta manual con su propio `SaveChanges` + guarda de día cerrado), `ObtenerResumenDiaAsync`/`CerrarDiaAsync`/`ListarCierresDiariosAsync`, `ObtenerResumenMesAsync`/`CerrarMesAsync`/`ListarCierresMensualesAsync` (el cierre mensual agrega `CajaMovimiento` del mes calendario directamente, **no** exige que todos los días del mes ya tengan su `CierreCajaDiario` individual — asunción documentada, ver riesgos).
- `Services/GastoService.cs` — `CrearAsync` (transacción explícita `BeginTransactionAsync`, dos `SaveChangesAsync`: el primero asigna `Gasto.Id`, necesario como `OrigenId` del `CajaMovimiento`; guarda de día cerrado antes de crear), `AnularAsync` (contramovimiento de Ingreso fechado **hoy**, nunca en la fecha original del Gasto — así nunca choca con un día ya cerrado ni modifica retroactivamente un período cerrado), `ObtenerGastosMesPorCategoriaAsync` (consumido por el Dashboard).
- `Services/EntregaService.cs` — `ListarAsync` (**sin ningún filtro implícito por el usuario autenticado**, ver R9), `ListarRepartidoresAsync` (join `UserRoles`/`Roles` por `SeedData.RolRepartidor`), `ObtenerPrecargaDesdeVentaAsync` (exige `Venta.Estado == Facturada` + máximo 1 Entrega por Venta), `CrearAsync` (calcula `CostoFinal` desde `EntregaMarkupSettings` vigente), `IniciarRecorridoAsync`/`MarcarEntregadaAsync`/`MarcarNoEntregadaAsync`/`ReagendarAsync` (transiciones de estado validadas server-side), `ContarPendientesAsync` (consumido por el Dashboard).
- `Services/DashboardService.cs` — `ObtenerAsync()` único (nivel 1 + nivel 3), agrega `Venta`/`CajaMovimiento`(vía `ICajaMovimientoService`)/`Entrega`(vía `IEntregaService`)/`Gasto`(vía `IGastoService`)/`ItemVenta`/`Producto`(vía `IProductoService.ContarStockCriticoAsync`) — top 5 productos y gastos por categoría acotados al **mes calendario actual** (asunción documentada, `2-disenador-funcional.md` no precisa el período de "tendencias").
- `Services/ProductoService.cs` (Entrega 1, modificado mínimamente) — agregado `ContarStockCriticoAsync()`.
- `Services/VentaWorkflowService.cs` (ola 1, **modificado**) — inyectado `ICajaMovimientoService`. `ConfirmarYFacturarAsync` ahora: (a) valida `EstaCerradoAsync(hoy)` **antes** de llamar a AFIP (evita emitir un comprobante fiscal real si después no se puede persistir nada); (b) tras el éxito de AFIP, genera un `CajaMovimiento` de Ingreso por cada `PagoVenta` confirmado **excepto** los de medio `CuentaCorriente` (asunción documentada: ese pago es una deuda diferida, ya registrada como Débito en `MovimientoCCCliente`, no un ingreso real de caja del día).
- `DependencyInjection.cs` — registrados `ICajaMovimientoService`, `IGastoService`, `IEntregaService`, `IDashboardService` (Scoped) + `IOptions<EntregaMarkupSettings>`.

**Web** (`FerreteriaLaPlatense.Web`):
- `Models/CajaViewModels.cs`, `Models/GastoViewModels.cs`, `Models/EntregaViewModels.cs`, `Models/DashboardViewModels.cs` — nuevos.
- `Controllers/CajaController.cs` — `Index`/`Listar`/`MovimientoManual`(GET/POST)/`CerrarDia`/`Cierres`/`CierresListar`/`Mensual`/`CerrarMes`/`MensualListar`. Policy `RequireAdministracion` a nivel de clase (Vendedor no figura en la tabla de permisos del analista para este módulo).
- `Controllers/GastosController.cs` — `Index`/`Listar`/`Create`(GET/POST)/`Anular`. Policy `RequireAdministracion`.
- `Controllers/EntregasController.cs` — `Index`/`Listar`/`Repartidores`(combo)/`Create`(GET/POST, override a `RequireVentas` — sin Repartidor)/`Details`/`IniciarRecorrido`/`MarcarEntregada`/`NoEntregada`/`Reagendar`. Policy de clase `RequireEntregas` (nueva, `SuperUsuario`+`Administrador`+`Vendedor`+`Repartidor`) — primera pantalla real del rol `Repartidor`.
- `Controllers/DashboardController.cs` — `Index` único, policy `ConsultaDashboard` (ya existía, cualquier usuario autenticado) — sin reducción de contenido por rol en este corte (nivel 1/3 no expone datos sensibles restringidos a Admin, a diferencia de marihogar).
- `Controllers/VentasController.cs` — **no tocado** (la integración con Caja vive en `VentaWorkflowService`, capa de Negocio).
- `Views/Ventas/Details.cshtml` — agregado el botón "Programar entrega" (visible solo si `Estado == Facturada`), enlaza a `Entregas/Create?ventaId=`.
- `Program.cs` — nueva policy `RequireEntregas`.
- `appsettings.json` — nueva sección `EntregaMarkup` (`PorcentajeMarkup: 20`, ejemplo editable).
- `Views/Caja/*` (Index con resumen del día + botón de cierre + DataTable de movimientos + filtros, MovimientoManual, Cierres, Mensual con selector de período + histórico), `Views/Gastos/*` (Index con DataTable + filtros por cada columna visible + botón Anular con SweetAlert2, Create), `Views/Entregas/*` (Index con DataTable + filtro de repartidor cargado por AJAX, Create desde una Venta Facturada, Details con acciones derivadas del estado real — Iniciar recorrido/Marcar entregada/No entregada con motivo vía SweetAlert2 input/Reagendar vía SweetAlert2 date input), `Views/Dashboard/Index.cshtml` (jerarquía visual de 3 bloques: nivel 1 con 3 stat-cards grandes cliqueables al detalle, card "Próximamente: salud financiera" muted para nivel 2, nivel 3 con gráfico doughnut de Chart.js para gastos por categoría + lista de top productos + stat-card de stock crítico) — todas con SweetAlert2 en confirmaciones y DataTables server-side.
- `Views/Shared/_Layout.cshtml` — nuevo link "Dashboard" (primer ítem del sidebar, visible a cualquier usuario autenticado), nueva sección "Caja" (SuperUsuario/Administrador), nueva sección "Entregas" (SuperUsuario/Administrador/Vendedor/Repartidor).

**Migración EF:** `EntregaDos_CajaGastosEntregasDashboard` (20260811134720) — tablas `CajaMovimientos`, `CierresCajaDiarios`, `CierresCajaMensuales`, `Entregas`, `Gastos`. **No aplicada a ninguna base** (igual que las 2 migraciones previas del proyecto).

**Build:** `dotnet build FerreteriaLaPlatense.slnx` → 0 errores, mismas advertencias preexistentes (NU1902 MailKit/MimeKit, CS0114 HomeController). Verificado dos veces (antes y después de reforzar `GastoService` con transacción explícita).

### Riesgos residuales y asunciones (Entrega 2, ola 2)

1. **Interpretación del markup de Entrega (R2):** se asumió `CostoFinal = CostoBase * (1 + PorcentajeMarkup/100)` (markup sobre el costo de envío, no sobre el valor del producto/venta) — `3-arquitecto-mvc.md` no distingue explícitamente entre ambas lecturas. A confirmar con el cliente.
2. **CajaMovimiento por PagoVenta, no por Venta:** se generó un `CajaMovimiento` por cada línea de `PagoVenta` (excepto CuentaCorriente), no uno consolidado por Venta — permite ver en Caja el desglose por medio de pago, pero implica varias filas de Caja para una sola venta con pago mixto. Documentado como decisión de diseño, no contradice `3-arquitecto-mvc.md` (que no precisa el nivel de agregación).
3. **Cierre mensual independiente del diario:** `CerrarMesAsync` no exige que los días del mes ya estén cerrados individualmente — agrega `CajaMovimiento` directo por rango de fecha. Si el cliente espera que el cierre mensual dependa de los cierres diarios (ej. bloquear el cierre de mes si falta cerrar algún día), hay que agregar esa validación.
4. **Entregas sin cobro en destino ni intentos históricos:** a diferencia de marihogar, no se implementó `EntregaIntento` (historial de intentos fallidos) ni el cobro en destino vía `PagoVenta` — no hay pedido funcional explícito de esto en `1-analista-funcional.md`/`2-disenador-funcional.md` para La Platense. Si el cliente lo pide, es una extensión aditiva sobre `IEntregaService` sin romper lo ya construido.
5. **Acceso a Caja/Gastos exclusivo de Administrador:** interpretado de la tabla de permisos del analista ("Vendedor: ventas, catálogo consulta, stock consulta, su propia CC" — no menciona Caja/Gastos). Si el cliente espera que el Vendedor consulte (no necesariamente escriba) Caja/Gastos, es un cambio de policy de una línea.
6. **Dashboard sin reducción de contenido por rol:** a diferencia de marihogar (que reduce el dashboard de Vendedor), en este corte cualquier usuario autenticado ve el mismo contenido — nivel 1/3 no expone datos que la tabla de permisos restrinja explícitamente. A revisar si el cliente considera que Caja/Gastos del día son datos sensibles que el Vendedor no debería ver ni en el Dashboard.
7. **Top productos y gastos del mes acotados al mes calendario actual** — asunción documentada, sin precedente explícito en `2-disenador-funcional.md`.
8. **Guarda de "día cerrado" aplicada de forma amplia:** tanto el alta de Gasto como la confirmación de Venta (para la fecha de hoy) y la anulación de Gasto (fecha de hoy) quedan bloqueadas si esa fecha ya tiene `CierreCajaDiario`. Esto significa que, una vez cerrada la caja de hoy, **no se puede seguir vendiendo ni registrando gastos hasta el otro día** — comportamiento coherente con un cierre de caja físico real, pero a confirmar explícitamente con el cliente antes de que el personal de mostrador lo experimente en producción.
9. **`Marca`/`Modelo`/`Categoria`/`Producto`/`Cliente`/`Venta` no se tocaron** salvo la extensión aditiva de `IProductoService`/`ProductoService` (`ContarStockCriticoAsync`) y la modificación de `VentaWorkflowService` (integración con Caja, ya declarada arriba).

### Guía de pruebas manuales — Entrega 2 completa (ola 1 + ola 2, a ejecutar por el cliente/QA, no por el Implementador)

**Antes de empezar:**
1. Aplicar la migración `EntregaDos_VentasCCClientesAfip` y luego `EntregaDos_CajaGastosEntregasDashboard` contra la base de desarrollo (`dotnet ef database update`).
2. Asignar el rol `Repartidor` a al menos un usuario de prueba (además de `Vendedor`/`Administrador`) para poder probar Entregas.

**Ventas / CC Clientes / AFIP (ola 1):**
3. Alta de Cliente (Responsable Inscripto y Consumidor Final) — verificar que el CUIT/DNI duplicado se rechaza.
4. Venta rápida: crear una venta, agregar 2-3 ítems (por búsqueda y por código de barras), guardar borrador, volver a editar (cambiar cantidad/precio/IVA) y verificar que los totales se recalculan.
5. Pago mixto: efectivo + tarjeta en 3 cuotas — verificar que el recargo se muestra y se suma al total antes de confirmar.
6. Venta con pago a cuenta corriente (requiere Cliente asignado) — confirmar y verificar el movimiento en `Clientes/CuentaCorriente/{id}`.
7. Confirmar una venta sin certificado AFIP configurado — debe devolver el error explícito y la venta queda en Borrador (no se descontó stock, no se generó movimiento de Caja).
8. Cancelar un borrador y verificar que desaparece del listado de Ventas.
9. Verificar permisos: Vendedor puede operar Ventas/Clientes; un usuario sin esos roles recibe 403.

**Caja (ola 2, nuevo):**
10. Facturar una venta con certificado AFIP configurado (homologación) y verificar que aparece un `CajaMovimiento` de Ingreso en `Caja/Index` por cada medio de pago usado (excepto si hubo una línea a cuenta corriente, que NO debe generar movimiento de Caja).
11. Registrar un Gasto y verificar que aparece automáticamente como Egreso en `Caja/Index`.
12. Registrar un movimiento manual (`Caja/MovimientoManual`) — verificar que aparece en el listado con origen "Ajuste".
13. Cerrar la caja de hoy (`Caja/Index` → "Cerrar caja de hoy") y verificar: (a) los totales del cierre coinciden con la suma de movimientos del día; (b) intentar facturar otra venta o registrar otro gasto con fecha de hoy debe fallar con el mensaje de "caja cerrada"; (c) el cierre aparece en `Caja/Cierres`.
14. Ir a `Caja/Mensual`, verificar el resumen del mes actual y cerrar el mes — verificar que aparece en el histórico de cierres mensuales de esa misma pantalla.

**Gastos (ola 2, nuevo):**
15. Registrar un gasto clasificado como "Caja chica" y otro como "Caja mensual" — verificar que la clasificación es excluyente (R7) y que ambos generan su Egreso en Caja.
16. Anular un gasto vigente — verificar que aparece con badge "Anulado" (sigue visible, no desaparece del listado) y que se genera un contramovimiento de Ingreso en Caja fechado hoy.
17. Intentar anular un gasto ya anulado — debe rechazarse con mensaje explícito.

**Entregas (ola 2, nuevo — primera pantalla real de Repartidor):**
18. Desde una Venta ya Facturada (`Ventas/Details`), hacer clic en "Programar entrega" — completar tipo (Propia/Tercerizada), costo base, repartidor y dirección. Verificar que el costo final se calcula con el markup vigente.
19. Intentar programar una segunda entrega para la misma venta — debe rechazarse ("ya tiene una entrega asociada").
20. Con un usuario del rol Repartidor, entrar a `Entregas/Index` y verificar que ve el listado COMPLETO (no solo las asignadas a él) — R9.
21. Recorrer el ciclo de estados desde `Entregas/Details`: Iniciar recorrido → Marcar entregada (o "No entregada" con motivo obligatorio → Reagendar con fecha futura).
22. Verificar permisos: un Repartidor puede ver/gestionar el estado de entregas pero NO puede acceder a `Entregas/Create` (debe dar 403).

**Dashboard (ola 2, nuevo — Corte 1):**
23. Entrar a `Dashboard/Index` con cualquier usuario autenticado y verificar: ventas de hoy (cantidad+total), caja de hoy (ingresos/egresos/saldo + si está cerrada), entregas pendientes — todo con datos reales de las pruebas anteriores.
24. Verificar la card "Próximamente: salud financiera" (nivel 2) — debe mostrarse claramente diferenciada como no disponible todavía, sin datos ni errores.
25. Verificar gastos del mes por categoría (gráfico), top 5 productos del mes y stock crítico — cada bloque debe navegar al detalle correspondiente (Gastos/Ventas o Productos/Stock) al hacer clic.

### Proximos pasos pendientes
1. QA funcional (`agentes-ia-qa`) sobre la Entrega 2 completa (ola 1 + ola 2).
2. Aplicar ambas migraciones (`EntregaDos_VentasCCClientesAfip`, `EntregaDos_CajaGastosEntregasDashboard`) contra la base de desarrollo.
3. Conseguir del cliente el CUIT real + certificado `.p12` de La Platense para poder probar AFIP de punta a punta (homologación primero) — sigue bloqueando la prueba end-to-end de Caja (el ingreso automático depende de una venta facturada con éxito).
4. Confirmar con el cliente las asunciones documentadas en ambas olas (Descuento/Recargo como monto, mecánica de recargo de cuotas, cobertura de pagos, markup de Entrega sobre costo base, alcance de "caja cerrada" bloqueando ventas/gastos, acceso de Vendedor a Caja/Gastos, reducción de contenido del Dashboard por rol).
5. Arrancar la Entrega 3 (Compras/Proveedores, CtaCte empleados, CtaCte consolidada del negocio, Presupuestos, Aumento masivo, Devoluciones+NC/ND AFIP, Dashboard Corte final) sobre la rama `entrega-3` — depende de que Entrega 2 esté aprobada por el cliente.
6. Sigue sin confirmar (heredado de Entrega 1): hipótesis de factor de conversión fijo por producto en `UnidadMedidaConversionService` — relevante para Compras (Entrega 3).

## Cierre de la Entrega 2 (61h) — completa

Con el cierre de esta ola 2 (Caja/Gastos/Entregas/Dashboard Corte 1) sumado a la ola 1 ya cerrada (Ventas/CC Clientes/AFIP), **la Entrega 2 completa del plan de 3 entregas funcionales queda con su alcance funcional 100% implementado y build limpio**. Pendiente antes de considerarla lista para el cliente: (a) aplicar ambas migraciones EF a la base de desarrollo, (b) QA funcional completo, (c) prueba manual del cliente siguiendo la guía completa de arriba. No se cerró ninguna pregunta abierta nueva de negocio en esta ola — las asunciones documentadas en ambas olas quedan pendientes de confirmación explícita del cliente, sin bloquear la entrega para prueba.

## Historial de ajustes
- 2026-08-11: cerrada la segunda mitad de la Entrega 2 (Caja, Gastos, Entregas a domicilio, Dashboard Corte 1) sobre la rama `entrega-2` — **cierra el alcance funcional completo de la Entrega 2 (61h)**. Implementadas las entidades `CajaMovimiento`/`CierreCajaDiario`/`CierreCajaMensual`/`Gasto`/`Entrega`, los servicios `ICajaMovimientoService`/`IGastoService`/`IEntregaService`/`IDashboardService`, y la integración de `VentaWorkflowService` con Caja (guarda de día cerrado antes de facturar + generación de `CajaMovimiento` por cada `PagoVenta` no-CuentaCorriente). El concepto de "cierre" (bloqueo de período) es desarrollo nuevo confirmado sin precedente en el historial. R9 (repartidor ve todas las entregas) respetado explícitamente en `EntregaService.ListarAsync`. Migración `EntregaDos_CajaGastosEntregasDashboard` generada y no aplicada. Build limpio (verificado 2 veces). Detalle completo de archivos/riesgos/pruebas en la sección "Cierre de Entrega 2 — ola 2" arriba.
- 2026-08-11: cerrada la primera mitad de la Entrega 2 (Ventas, CC Clientes, Facturación AFIP) sobre la rama `entrega-2`. Implementadas las entidades `Cliente`/`MovimientoCCCliente`/`Venta`/`ItemVenta`/`PagoVenta`, el workflow `IVentaWorkflowService` (Borrador→Facturada, Anulada modelada pero sin implementar — Entrega 3), `IRecargoCuotasService` (config por appsettings), y el puerto completo de `AfipService`/`IAfipService`/`AfipSettings`/`AfipTokenCache` desde marihogar (mismo circuito WSAA/WSFEv1). Corregida la reutilización documentada en `3-arquitecto-mvc.md`: el ledger de CC cliente se adaptó de `vino-y-se-fue` (no de marihogar), y `Cliente` no persiste columna de saldo (se calcula on-the-fly). Migración `EntregaDos_VentasCCClientesAfip` generada y no aplicada. Build limpio. AFIP queda sin poder probarse de punta a punta hasta que el cliente traiga CUIT real + certificado `.p12`. Detalle completo de archivos/riesgos/pruebas en la sección "Cierre de Entrega 2 — ola 1" arriba.
- 2026-08-10 (17:45, corrección inmediata): Joaquín corrigió el alcance del rol `Administrador` — gestión de Usuarios y Herramientas del Sistema quedan exclusivas de `SuperUsuario`; Administrador conserva el resto (Catálogo/Stock). Revertido `UsersController` a `RequireSuperUsuario` y reestructurado el sidebar en `_Layout.cshtml` (Usuarios/Sistema exclusivos de SuperUsuario, Notificaciones liberado de esa restricción). Sin migración EF.
- 2026-08-10 (17:30, post-QA/GO de Entrega 1): agregado el rol `Administrador` (todo el sistema salvo `SystemController`, exclusivo de `SuperUsuario`) y cambiado el redirect post-login de `Home` a `Stock`. Modificacion puntual sobre la Entrega 1 ya cerrada y en GO, no una entrega nueva. Sin migracion EF. Build limpio. Detalle completo en la seccion "Ajuste puntual (2026-08-10, post-QA/GO)" arriba y en `trazabilidad.md` (entradas 17:00 y 17:30).
- 2026-08-10: Creado el plan de 3 entregas funcionales incrementales sobre el WBS ya aprobado (139h), a pedido explícito de Joaquín para dar dinamismo al proyecto y permitir prueba temprana del cliente. Sin cambios de alcance ni de precio — solo reordenamiento de secuencia de entrega respetando dependencias técnicas. Se adelantó el módulo "Entregas a domicilio" (originalmente Etapa 2/módulo 15) a la Entrega 2 para que el Dashboard Corte 1 (nivel día) pueda mostrar entregas pendientes reales. El Dashboard (12h) se fasea en 2 cortes sin agregar horas: nivel 1+3 en Entrega 2, nivel 2 en Entrega 3.
- 2026-08-10 (cierre Entrega 1): implementados Catálogo (Marca/Modelo/Categoria/Producto), Stock (AjusteStock + alerta visual), Código de barras (lookup service + endpoint de prueba) y roles nuevos (Vendedor/Repartidor). Reutilización de `ShowroomGriffin` (Marca/Modelo/Categoria, AjusteStock/StockController) y `marihogar` (DataTableRequestHelper). Build limpio, migración `EntregaUno_CatalogoStockUsuarios` generada (primera migración real del proyecto) y no aplicada a ninguna base. Ver detalle completo de archivos/riesgos en las secciones arriba.
