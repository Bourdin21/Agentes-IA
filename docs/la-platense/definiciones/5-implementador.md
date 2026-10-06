# Memoria - Implementador

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-10-05 (v13 — Entrega 3 item 4c + paso 6: moneda y cotizacion CONGELADAS en la compra aplicadas de punta a punta (era un bug activo que contaminaba el catalogo) y pagos programados con aviso oportunista en vez de hosted service. Commit local, SIN deploy, SIN push)

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

## Etapa 3 — Migración de catálogo (items de app del WBS, 2026-08-17)

**Ojo con la nomenclatura:** "Etapa 3" (migración de catálogo, esta sección) NO es lo mismo que "Entrega 3" (Compras/CtaCtes/Presupuestos/Devoluciones, todavía sin implementar). Son dos alcances distintos que corren en paralelo en la documentación. Esta etapa se desarrolló en la rama `migracion-catalogo`, creada desde `entrega-2`.

Alcance cerrado según `1-analista-funcional.md` (sección "Etapa 3 — Migración de catálogo", con datos reales del backup del cliente), `2-disenador-funcional.md` (flujo 10 completo + ViewModels `ImportacionCatalogoMigracionViewModel`/`ReporteExcepcionesMigracionViewModel`) y `3-arquitecto-mvc.md` (sección "Etapa 3"). Cubre los **ítems 2 a 6 del WBS de `4-presupuestador.md` (15h de las 27h de la etapa)**. Fuera de este alcance, como pasos separados posteriores: el ítem 1 (herramienta batch de extracción/limpieza contra el backup real) y el ítem 7 (carga real a producción).

### Resultado del escaneo de reutilización (obligatorio antes de implementar)

- **`docs/patrones/catalogo.yml`**: sin match. `PAT-008` (DataTables server-side + filtro por columna) se reutiliza en el reporte de excepciones, pero no hay patrón de "importación de archivo con preview→confirmar" catalogado. **Se agregó `PAT-012`** con este patrón (ver el catálogo) — renumerado desde `PAT-009` original el 2026-08-18 por colisión con el `PAT-009` de tema oscuro agregado por otra sesión en paralelo (ver `25-frontend-design-system.instructions.md`).
- **`IListaPreciosProveedorImportService` (referencia indicada por el alcance): NO EXISTE en el repo.** El alcance pedía replicar su contrato "de Entrega 2", pero ese servicio pertenece al módulo 7 del WBS (Proveedores + compras + importación de listas), que **no se implementó todavía** — está listado en `2-disenador-funcional.md` como contrato funcional previsto, no como código existente. Se diseñó entonces el contrato de `ICatalogoMigracionService` desde cero, siguiendo el patrón general de Services del proyecto (`ServiceResult<T>`, DTOs en Application, DataTables server-side), y queda como la referencia a replicar cuando se implemente `IListaPreciosProveedorImportService`.
- **`marihogar` / `tools/ImportarHistorico/Program.cs`** (encontrado escaneando `docs/*/definiciones/5-implementador.md`, sprint CR-D): único precedente real de importación de Excel a EF Core en el historial del estudio. Se reutilizó el **conocimiento**, no el código (allá es una consola de un solo uso, acá es un servicio web con preview): lectura con `ClosedXML` (`XLWorkbook`/`LastRowUsed`/`Cell(r,c).IsEmpty()`), resolución "buscar catálogo o crearlo mínimo en vez de descartar la fila", y sobre todo la decisión de **escribir las entidades directo por el DbContext en vez de invocar los Services de negocio** (los Services estampan valores propios que un import no debe pisar — acá: `Stock`, `StockVerificado`, `ClasificacionABC` manual).
- **`CatalogoSimpleServiceBase` (Entrega 1, mismo repo)**: reutilizado directo para `Proveedor` y para la creación de Marca/Modelo/Categoría faltantes durante el import (no se reimplementó la validación de nombre único).
- **`labipac` / `IFabaImportService`**: revisado y descartado — es una sincronización contra una API externa, no un import de archivo con previsualización.

### Prerequisito no contemplado antes: `Proveedor` mínimo

`CodigoProveedorProducto` no se puede modelar sin la entidad `Proveedor`, y `Proveedor` pertenece al módulo de Compras (ítem 7 del WBS de Etapa 1), **todavía no implementado**. Se creó una **versión mínima** (`Nombre` + `Activo`, hereda `SoftDestroyable`, se comporta como catálogo simple igual que Marca/Modelo/Categoría) exclusivamente como prerequisito: sin ABM propio, sin entrada de sidebar, se completa solo desde el import. Cuando se implemente Compras, la entidad se **amplía de forma aditiva** (CUIT, condición IVA, TC propio, % descuento, cuenta corriente) y `IProveedorService` deja de heredar de `ICatalogoSimpleService` — el punto de extensión está documentado en la propia interfaz. Esto no estaba en `3-arquitecto-mvc.md` (que lista `CodigoProveedorProducto` sin mencionar que su FK no existe todavía) y es la principal desviación de arquitectura de esta etapa.

### Formato del archivo de intercambio (ESPECIFICACIÓN para la herramienta del paso 1)

Contrato exacto que debe cumplir la herramienta batch de extracción/limpieza. Está replicado en el XML-doc de `CatalogoMigracionService` y en la propia pantalla de importación (para que el operador lo tenga a la vista).

**Formato:** Excel `.xlsx` (no CSV — se eligió un solo formato explícito, y `ClosedXML` ya está en el proyecto). **Tres hojas obligatorias**, con esos nombres exactos: `Productos`, `CodigosPorProveedor`, `Clientes`. En cada hoja: **fila 1 = encabezado** con los nombres de columna de abajo, **datos desde la fila 2**. Los nombres de columna se matchean sin distinguir mayúsculas, acentos, espacios ni guiones, y **el orden de las columnas no importa**. Si falta una hoja o una columna obligatoria, el análisis se rechaza completo (no se importa nada).

| Hoja | Columnas | Obligatorias |
|---|---|---|
| `Productos` | `nombre`, `codigo`, `marca`, `modelo`, `categoria`, `precioCompra`, `precioVenta`, `porcentajeIVA`, `unidadVenta`, `bonificacion`, `clasificacionABCSugerida`, `codigoBarras` | `nombre`, `codigo`, `marca`, `modelo`, `categoria`, `precioCompra`, `precioVenta`, `porcentajeIVA` |
| `CodigosPorProveedor` | `nombreProveedor`, `codigoProveedor`, `codigoProducto` | las tres |
| `Clientes` | `nombre`, `cuit`, `condicionIVA`, `telefono`, `domicilio`, `localidad`, `email`, `notas` | `nombre` |

**Decisiones de formato a respetar:**
- **`codigoProducto` referencia el `codigo` de la hoja `Productos`**, no la posición de la fila. Se eligió así porque es estable entre corridas y es la misma clave con la que funciona la idempotencia — una referencia por posición se rompería si el paso 1 se vuelve a correr con un dataset ligeramente distinto.
- `unidadVenta` acepta el nombre del enum (`Unidad`/`Peso`/`Metro`/`Bulto`) o alias del legacy (`kg`, `kilogramos`, `metros`, `mt`, `bultos`, `caja`, …). **Lo que el enum no modela (Litros, Pares, Escalones) cae en `Unidad`** con una excepción informativa — extender el enum es un cambio de Entrega 1, fuera de esta etapa.
- `porcentajeIVA` debe ser 10,5 o 21 (las alícuotas ya permitidas por `ProductoService`). Cualquier otro valor se importa como 21 con excepción informativa.
- `clasificacionABCSugerida` acepta `A`/`B`/`C` o `1`/`2`/`3`; vacío = sin sugerencia.
- `bonificacion` es **texto libre** (`"33+5"`), no un porcentaje — es la decisión de negocio ya cerrada en Análisis (bonificación compuesta).
- `cuit` se normaliza quitando guiones/puntos (mismo criterio que el ABM de Cliente de Entrega 2).
- Números: se acepta celda numérica de Excel o texto con separador decimal `.` o `,`.

### Reglas de idempotencia y de excepción implementadas

**Claves de identidad (una segunda corrida actualiza, no duplica):** `Producto` por `Codigo`; `Cliente` por `CuitDni` si lo trae, y si no por nombre exacto **contra clientes que tampoco tengan CUIT cargado** (matchear un homónimo con CUIT le borraría el CUIT al cliente existente — corregido durante la implementación); `CodigoProveedorProducto` por `(ProveedorId, CodigoDelProveedor)`.

**Baja lógica:** todas las consultas de matcheo usan `IgnoreQueryFilters()`. Motivo concreto: el índice único de MySQL **no distingue registros soft-deleted**, así que un `Producto`/`Cliente`/código/catálogo dado de baja sigue ocupando su clave. Al reimportarlo se **revive** (`DeletedAt = null`) en vez de fallar el insert.

**Lo que el import NUNCA pisa:** `Producto.Stock`, `Producto.StockVerificado` (el stock del legacy no es confiable — ya resuelto por el plan de puesta a punto de Entrega 1) y `Producto.ClasificacionABC` (el campo manual del cliente). En una reimportación no se pierde el trabajo ya hecho en el sistema nuevo.

**Excepciones bloqueantes (la fila no se importa):** producto sin nombre / sin código / sin precio de venta > 0 / con código repetido en el archivo; código de proveedor sin proveedor, sin código o sin `codigoProducto`; par proveedor+código repetido en el archivo; `codigoProducto` que no existe ni en el sistema ni en el archivo; cliente sin nombre; CUIT repetido en el archivo; dos filas del archivo apuntando al mismo cliente del sistema.

**Excepciones informativas (la fila SÍ se importa, con un valor por defecto):** sin marca → `"Sin marca"`; sin modelo → `"Sin modelo"`; sin categoría → `"Sin categoría"` (criterio ya acordado en Análisis: asignar categoría por defecto en vez de bloquear); IVA no permitido → 21%; unidad desconocida → `Unidad`; ABC inválida → sin sugerencia; **código de barras ya usado por otro producto → el producto se importa sin código de barras** (resuelve el ~10% de códigos ambiguos del legacy sin romper el índice único de Entrega 1).

Tope de excepciones detalladas: 50.000 (con flag `ExcepcionesTruncadas` visible en el reporte).

### Clasificación ABC automática — criterio implementado

Ventana móvil de N meses (default 12, configurable por `appsettings` sección `ClasificacionAbc` y por la propia pantalla), suma de `ItemVenta.Cantidad` agrupada en la base de datos, **piso en 0** para netos negativos por devoluciones, Pareto ordenando de mayor a menor: ≤80% acumulado = A, ≤95% = B, resto = C (cortes también configurables). **Los productos sin ninguna venta en la ventana quedan en `C`, no en `null`** — decisión tomada acá y documentada: es el mismo criterio ya acordado para la puesta a punto de stock ("la mayoría del catálogo arranca sin verificar") y "bajo/nulo movimiento" es información útil, no ausencia de dato; con ~1.500 de 121.691 productos con venta en el último año, `C` describe correctamente al resto.

**Nunca escribe `Producto.ClasificacionABC`.** El único camino de la sugerencia al campo manual es el botón "Aceptar sugerencia" de la ficha del producto (acción explícita, POST propio con confirmación SweetAlert2). Corrección técnica aplicada: la ventana se calcula en **UTC** (`Venta.Fecha` se guarda en UTC) y solo se convierte a hora de Argentina para mostrarla — comparar una columna UTC contra `ArgentinaTime.Now` corre el rango 3 horas (bug ya catalogado en el XML-doc de `ArgentinaTime`).

### Archivos y capas modificadas (Etapa 3)

**Domain (nuevo):** `Entities/Proveedor.cs` (versión mínima), `Entities/CodigoProveedorProducto.cs` (índice único compuesto).
**Domain (modificado):** `Entities/Producto.cs` (+`ClasificacionABCSugerida`, +`Bonificacion`), `Entities/Cliente.cs` (+`Domicilio`, `Localidad`, `Email`, `Notas`).

**Application (nuevo):** `DTOs/CatalogoMigracionDtos.cs` (`SeccionesMigracion`, `ExcepcionMigracionDto`, `ProductoPreviewMigracionDto`, `ResumenMigracionDto`, `ImportacionCatalogoMigracionPreviewDto`, `ImportacionCatalogoMigracionResultadoDto`, `ReporteExcepcionesMigracionDto`, `ResultadoClasificacionAbcDto`), `Interfaces/ICatalogoMigracionService.cs`, `Interfaces/IClasificacionAbcAutomaticaService.cs`, `Settings/ClasificacionAbcSettings.cs`.
**Application (modificado):** `Interfaces/ICatalogoSimpleService.cs` (+`IProveedorService`), `DTOs/ProductoDtos.cs` (+`Bonificacion`, +`ClasificacionABCSugerida` de solo lectura), `DTOs/ClienteDtos.cs` (+4 campos).

**Infrastructure (nuevo):** `Services/ProveedorService.cs`, `Services/CatalogoMigracionService.cs`, `Services/ClasificacionAbcAutomaticaService.cs`.
**Infrastructure (modificado):** `Data/AppDbContext.cs` (2 `DbSet` + config Fluent de las 2 entidades nuevas y de las 6 columnas nuevas), `DependencyInjection.cs` (3 Services Scoped + `ClasificacionAbcSettings`), `Services/ProductoService.cs` (mapeo de los 2 campos nuevos; `ClasificacionABCSugerida` no se escribe desde el ABM), `Services/ClienteService.cs` (mapeo de los 4 campos nuevos + validación de formato de email + normalización de opcionales a `null`).

**Web (nuevo):** `Models/MigracionCatalogoViewModels.cs`, `Controllers/MigracionCatalogoController.cs`, `Views/MigracionCatalogo/Index.cshtml` (carga + especificación del formato a la vista), `Previsualizar.cshtml` (resumen + muestra + confirmar), `Excepciones.cshtml` (DataTables server-side con 4 filtros + export a Excel), `Resultado.cshtml`.
**Web (modificado):** `Controllers/StockController.cs` (+`RecalcularClasificacionAbc`), `Views/Stock/Index.cshtml` (botón + diálogo de ventana en meses), `Controllers/ProductosController.cs` (+`AceptarClasificacionAbcSugerida`, mapeo), `Models/ProductoFormViewModel.cs` (+`Bonificacion`, +`ClasificacionABCSugerida`, +`HaySugerenciaDistinta`), `Views/Productos/Create.cshtml` y `Edit.cshtml` (bonificación + bloque de sugerencia ABC), `Models/ClienteFormViewModel.cs` y `Views/Clientes/Create.cshtml`/`Edit.cshtml` (card "Domicilio y contacto"), `Views/Shared/_Layout.cshtml` (link de sidebar, exclusivo de Administración), `appsettings.json` (sección `ClasificacionAbc`), `wwwroot/css/site.css` (clase `.ov-monto`, que faltaba en este proyecto pese a ser regla del design system).

**Permisos:** todo lo nuevo va contra `RequireAdministracion` (SuperUsuario + Administrador) — no se creó una policy nueva porque el conjunto de roles es exactamente el ya definido. El link de sidebar usa la misma condición de roles que la policy del controller (verificado por revisión de código, no ejecutando la app).

### Migración EF generada (Etapa 3)

`20260817164053_EntregaTres_MigracionCatalogo` — **generada, NO aplicada a ninguna base** (ni desarrollo ni producción). Es **puramente aditiva**: crea las tablas `Proveedores` (índice único en `Nombre`) y `CodigosProveedorProducto` (índice único compuesto `(ProveedorId, CodigoDelProveedor)` + índice en `ProductoId`, FKs `Restrict`), y agrega 6 columnas nullable (`Productos.Bonificacion`, `Productos.ClasificacionABCSugerida`, `Clientes.Domicilio/Localidad/Email/Notas`). No modifica ninguna migración ya existente ni ninguna columna existente: los datos de Entrega 1/2 quedan intactos.

### Riesgos residuales y asunciones (Etapa 3)

1. **`Proveedor` mínimo creado como prerequisito** (ver sección arriba). Riesgo real: si el módulo de Compras se implementa asumiendo que `Proveedor` no existe, va a chocar con esta tabla. Está documentado en el XML-doc de la entidad y acá.
2. **Tiempo de proceso con el volumen real (121.691 productos) sin medir.** El import corre síncrono dentro del request HTTP; el análisis y la confirmación recorren el archivo completo (lotes de 500 con `SaveChanges` + `ChangeTracker.Clear()`), pero con ese volumen puede superar el timeout del hosting. Mitigaciones ya implementadas: límite de request subido a 200 MB (el default de Kestrel de 30 MB rechazaría el archivo), lotes acotados y modal de "no cierre esta ventana". Mitigación operativa recomendada, aprovechando que el import es idempotente: **partir el archivo en tandas** (ej. 10 archivos de ~12.000 productos, con la hoja `CodigosPorProveedor` de cada tanda referenciando solo productos de esa tanda o ya importados). Sigue pendiente de medición real, tal como lo anticipó `3-arquitecto-mvc.md`.
3. **Staging en la carpeta temporal del sistema operativo.** El archivo subido y el JSON del análisis quedan en `%TEMP%/FerreteriaLaPlatense/migracion-catalogo/{token}`. Si el hosting recicla el proceso o limpia el temp entre el análisis y la confirmación, hay que volver a subir el archivo (el sistema lo avisa con un mensaje claro, no falla con 500). No se implementó limpieza automática de archivos viejos de staging: **los archivos quedan ahí y hay que borrarlos a mano después de la migración** (contienen datos del cliente).
4. **Recálculo ABC también síncrono** sobre todo el catálogo. Menos pesado que el import (una query agrupada + updates por lote solo de los productos cuya sugerencia cambió), pero con 121.691 productos la primera corrida escribe todas las filas. No hay job programado: es acción manual, tal como lo decidió Arquitectura.
5. **Unidades del legacy no modeladas** (Litros, Pares, Escalones) caen en `Unidad`. Queda registrado en el reporte de excepciones fila por fila, así que es auditable después del import; corregir producto por producto desde el ABM, o extender el enum `UnidadMedida` como cambio aparte.
6. **Movimientos de cuenta corriente de clientes NO se migran** (los clientes migrados arrancan con saldo 0). No estaba en el alcance de esta etapa; si el cliente espera arrancar con los saldos de fiado del sistema anterior, es alcance nuevo.
7. **`Bonificacion` es informativa**: no participa de ningún cálculo de precio. La conversión de `"33+5"` a un porcentaje efectivo (36,35%) no se implementó — no estaba pedida.
8. **Un código de barras retenido por un producto dado de baja lógica bloquea su reasignación** (el índice único incluye los soft-deleted). El producto nuevo se importa sin código de barras y queda en el reporte. Es conservador a propósito: la alternativa era liberar el código del registro eliminado, que es una decisión de negocio no relevada.
9. **`ProductoService` no expone todavía los `CodigoProveedorProducto` de un producto en su ficha.** La tabla se llena por import y se consulta por base de datos; la pantalla que los muestre/edite corresponde al módulo de Compras.

### Guía de pruebas manuales (Etapa 3 — a ejecutar por el cliente/QA, no por el Implementador)

Requiere aplicar antes la migración `EntregaTres_MigracionCatalogo` a la base de desarrollo (`dotnet ef database update --project FerreteriaLaPlatense.Infrastructure --startup-project FerreteriaLaPlatense.Web`) y un archivo `.xlsx` de prueba armado con el formato de arriba (basta una decena de filas por hoja; **no hace falta el dataset real** para validar el circuito).

**Permisos**
1. Con un usuario `Vendedor`: el link "Migración de catálogo" NO debe aparecer en el sidebar, y entrar a `/MigracionCatalogo` por URL directa debe dar 403 (no 500, no acceso silencioso). Ídem `/Stock/RecalcularClasificacionAbc` y `/Productos/AceptarClasificacionAbcSugerida`.
2. Con `Administrador`: el link aparece bajo Catálogo y la pantalla carga.

**Importación — camino feliz**
3. Subir el archivo de prueba: debe llevar a la pantalla de revisión con los contadores de altas/actualizaciones por sección y los catálogos a crear.
4. Con el archivo teniendo al menos una excepción, verificar que el botón "Confirmar la importación" está **deshabilitado** y que hay un aviso pidiendo revisar el reporte.
5. Abrir el reporte de excepciones, volver al resumen: ahora el botón de confirmar debe estar habilitado.
6. Confirmar: debe mostrar la pantalla de resultado con los mismos números que el preview.
7. Verificar en `Productos` que los productos del archivo están cargados con su marca/modelo/categoría (las creadas nuevas deben existir en `Marcas`/`Modelos`/`Categorías`), y en `Clientes` que están los clientes con domicilio/localidad/email/notas.

**Idempotencia (la prueba más importante)**
8. Volver a subir y confirmar **exactamente el mismo archivo**: el preview debe mostrar **0 altas y todas actualizaciones** en las tres secciones, y 0 catálogos a crear. Después de confirmar, el total de productos y clientes del sistema no debe haber cambiado.
9. Editar a mano un producto migrado (cambiarle el stock mínimo por el ABM y el stock por "Ajustar"), reimportar el archivo, y verificar que **el stock y la clasificación ABC manual siguen como los dejó usted** (el import solo actualiza nombre/precios/IVA/unidad/bonificación/categoría).

**Excepciones**
10. Armar un archivo con: una fila de producto sin nombre, una sin precio de venta, un código repetido, una fila de código de proveedor apuntando a un `codigoProducto` inexistente, y un cliente sin nombre. Cada una debe aparecer en el reporte con su motivo y marcada "No se importa"; el resto del archivo debe importarse igual.
11. Filtrar el reporte por sección, por texto en el motivo y por "No se importa": los filtros deben funcionar sobre datos reales.
12. Exportar el reporte a Excel: debe bajar un archivo con las mismas filas y encabezados en español.
13. Subir un archivo al que le falte una hoja (o una columna obligatoria): debe rechazarlo con un mensaje claro que diga qué falta, **sin importar nada**.

**Clasificación ABC**
14. Con ventas ya registradas (de las pruebas de Entrega 2), entrar a `Stock` y usar "Recalcular clasificación ABC" con ventana de 12 meses: debe mostrar un resumen con la cantidad de productos A, B y C, cuántos tuvieron ventas en el período y cuántos tienen una sugerencia distinta de su clasificación actual.
15. Abrir un producto que haya vendido y editarlo: debe verse la sugerencia al lado del campo manual, indicando si coincide o no.
16. En un producto donde la sugerencia difiera, usar "Aceptar sugerencia" y confirmar: el campo manual debe quedar con el valor sugerido. Volver a intentarlo debe avisar que ya coinciden.
17. Verificar que el recálculo **no cambió** la clasificación manual de ningún otro producto (comparar contra los valores que había antes en el listado de `Stock`).
18. Repetir el recálculo con una ventana de 1 mes: los resultados deben cambiar (menos productos con venta), confirmando que el parámetro se aplica.

**Regresión de Entrega 1 y 2**
19. Alta y edición de producto por el ABM normal (con y sin bonificación) siguen funcionando, y el combo de marca/modelo/categoría de Editar sigue llegando con el valor asignado.
20. Alta y edición de cliente con los 4 campos nuevos vacíos: debe guardar sin problemas (todos son opcionales). Con un email mal escrito debe bloquear con mensaje.
21. Una venta completa (borrador → facturada) sigue funcionando igual que antes de esta etapa.

### Próximos pasos de Etapa 3
1. Aplicar la migración `EntregaTres_MigracionCatalogo` a la base de desarrollo.
2. QA funcional sobre esta etapa con la guía de arriba.
3. **Ítem 1 del WBS (paso separado)**: construir la herramienta batch de extracción/limpieza contra una copia del backup real, cumpliendo la especificación de formato documentada arriba y las reglas de deduplicación cerradas en Análisis.
4. **Ítem 7 del WBS (paso separado)**: medir tiempos con el dataset real completo, decidir si se parte en tandas, y ejecutar la carga a producción con backup previo.
5. Borrar los archivos de staging (`%TEMP%/FerreteriaLaPlatense/migracion-catalogo/`) al terminar la migración real — contienen datos del cliente.
6. Confirmar con Joaquín las decisiones tomadas acá que no venían cerradas: productos sin venta en la ventana quedan en `C` (no null), unidades no modeladas caen en `Unidad`, y los movimientos de cuenta corriente de clientes no se migran.

## Rama de producción `entrega-1-migracion` — Etapa 1 + migración de catálogo, aisladas de Entrega 2 (2026-08-17)

### Por qué existe esta rama
El cliente aprobó llevar a producción **Etapa 1 (Catálogo/Stock/Usuarios) + la migración de catálogo (Etapa 3)**, pero **NO la Entrega 2** (Ventas / CC clientes / AFIP / Caja / Gastos / Entregas / Dashboard): esa entrega pasó QA de código pero nunca se probó manualmente en caliente, así que no está aprobada para producción.

El problema es de topología de ramas, no de código: `migracion-catalogo` se creó **desde `entrega-2`** (la migración necesitaba la entidad `Cliente`, que nació en Entrega 2), así que arrastra toda la Entrega 2 como ancestro. Deployar `migracion-catalogo` habría puesto Ventas/AFIP/Caja en producción sin aprobación.

`entrega-1-migracion` se creó **desde `entrega-1`** (commit `bdf3796`) y contiene exactamente lo aprobado. No se mergeó a `master` ni se pusheó: queda local para revisión del orquestador antes del deploy.

### Por qué no se resolvió con `cherry-pick`
El commit `71daf36` mezcla en un mismo diff la extensión de `Cliente`/`ClienteService` (Entrega 2) con las entidades nuevas de Etapa 3 (`Proveedor`, `CodigoProveedorProducto`), y varios archivos compartidos (`AppDbContext`, `DependencyInjection`, `ProductoService`) tienen el delta de Etapa 3 apilado sobre el de Entrega 2. Se trajo **archivo por archivo** con `git show migracion-catalogo:<ruta>`, aplicando el delta de Etapa 3 sobre la versión de `entrega-1` donde hacía falta.

Dato útil que simplificó el trabajo: Entrega 2 solo modificó 8 archivos preexistentes (`IProductoService`, `AppDbContext`, `DependencyInjection`, `ModelSnapshot`, `ProductoService`, `Program.cs`, `_Layout.cshtml`, `appsettings.json`) — todo lo demás que toca Etapa 3 era idéntico en `entrega-1` y `entrega-2` y se pudo copiar tal cual.

### Qué quedó en la rama (2 commits sobre `entrega-1`)
`b06f895` — código de app:
- **Domain**: `Proveedor` (versión mínima), `CodigoProveedorProducto`, `Producto` extendido (`Bonificacion`, `ClasificacionABCSugerida`), `Cliente` + enum `CondicionIVA`.
- **Application**: `IProveedorService`, `IClasificacionAbcAutomaticaService` (reducido, ver abajo), `Bonificacion`/`ClasificacionABCSugerida` en `ProductoDto`, `Categoria` en `StockListItemDto`, parámetro `categoriaId` en `IAjusteStockService.ListarStockAsync`.
- **Infrastructure**: `ProveedorService`, `ClasificacionAbcAutomaticaService`, `AppDbContext` (DbSets + config de `Proveedor`/`CodigoProveedorProducto`/`Cliente` y columnas nuevas de `Producto`), `DependencyInjection`, `ProductoService`, `AjusteStockService`.
- **Web**: campo `Bonificacion` y bloque de sugerencia ABC en la ficha de Producto, acción `AceptarClasificacionAbcSugerida`, y la **columna + filtro de Categoría en Stock** (parte de `138d8a4` — fix puro de Entrega 1, sin relación con Entrega 2).
- **tools/MigracionCatalogo**: script de carga real completo, en su estado final (`229c6c1`), sin ningún cambio.

`8e6de67` — migración EF nueva `20260817233056_EtapaTres_MigracionCatalogo`.

### Qué NO se trajo
`VentasController`/`CajaController`/`DashboardController`/`EntregasController`/`GastosController`/`ClientesController` y sus vistas; `VentaWorkflowService`, `AfipService`, `CajaMovimientoService`, `GastoService`, `EntregaService`, `DashboardService`, `CuentaCorrienteClienteService`, `RecargoCuotasService`, `ClienteService`; las entidades `Venta`/`ItemVenta`/`PagoVenta`/`MovimientoCCCliente`/`CajaMovimiento`/`CierreCajaDiario`/`CierreCajaMensual`/`Gasto`/`Entrega`; y las 2 migraciones EF de Entrega 2. Verificado: el `AppDbContextModelSnapshot` de esta rama no contiene ninguna entidad de Entrega 2, y el sidebar solo enlaza los controllers de Entrega 1.

### Migración EF generada
`20260817233056_EtapaTres_MigracionCatalogo` — **aditiva pura, sin drops**. Se generó nueva sobre esta rama en vez de portar `20260817164053_EntregaTres_MigracionCatalogo`: aquella asume las tablas de Entrega 2 ya creadas (agrega `Domicilio`/`Localidad`/`Email`/`Notas` a una tabla `Clientes` preexistente) y no aplica sobre una base con solo Entrega 1.

Contenido:
- `Productos`: `+ Bonificacion varchar(50) NULL`, `+ ClasificacionABCSugerida int NULL`.
- `Clientes` (tabla nueva): `Nombre(200)` NOT NULL, `CuitDni(20)` único, `CondicionIVA`, `Telefono(50)`, `Domicilio(300)`, `Localidad(150)`, `Email(200)`, `Notas(1000)` + auditoría/soft-delete. Las definiciones son **la unión exacta** de la migración de Entrega 2 más la extensión de Etapa 3, para que cuando se habilite Entrega 2 sobre esta base la tabla ya esté como corresponde.
- `Proveedores` (tabla nueva): `Nombre(200)` NOT NULL único, `Activo`.
- `CodigosProveedorProducto` (tabla nueva): FK `Restrict` a `Productos` y `Proveedores`, índice único `(ProveedorId, CodigoDelProveedor)`, índice por `ProductoId`.

Impacto sobre la base de producción actual (solo Entrega 1 aplicada): 3 tablas nuevas vacías + 2 columnas nullable. No modifica ni borra nada existente — no hay riesgo de pérdida de datos al aplicarla.

### Decisiones de diseño a validar con el cliente
1. **`Cliente` queda como tabla y entidad, sin nada más.** Sin `IClienteService`/`ClienteService`, sin `ClienteDtos`, sin `ClientesController`, sin vistas y sin entrada de sidebar. Existe únicamente para recibir las ~3.000 fichas de cliente que trae la migración del legacy y no perderlas. El script `tools/MigracionCatalogo` escribe directo por `DbContext` (nunca usó `ClienteService`), así que no hizo falta ningún servicio para que la carga funcione. **En producción no aparece ninguna pantalla de "Clientes"** — eso se habilita con Entrega 2.
2. **El recálculo POR LOTE de la clasificación ABC sugerida no existe en esta rama.** `IClasificacionAbcAutomaticaService.RecalcularAsync` agrega `ItemVenta.Cantidad` sobre una ventana de ventas facturadas — es técnicamente imposible sin el módulo de Ventas. Se retiraron `RecalcularAsync`, `StockController.RecalcularClasificacionAbc`, el botón "Recalcular clasificación ABC" de la pantalla de Stock, y los tipos que solo servían a ese flujo (`ResultadoClasificacionAbcDto`, `ClasificacionAbcSettings`, `RecalculoClasificacionAbcViewModel`, la sección `ClasificacionAbc` de `appsettings.json`) — para no dejar código muerto en una rama que va a producción. **Impacto funcional real: ninguno para el arranque.** La clasificación ABC con la que arranca producción la escribe la carga inicial de catálogo (mismo Pareto 80/95, calculado sobre las ventas del sistema legacy — ver entrada del 2026-08-17 "ABC real, no solo sugerida"), y el cliente la sigue editando a mano producto por producto como siempre. Se conservó `AceptarSugerenciaAsync` y su botón en la ficha de Producto, que no dependen de Ventas.
3. **No se trajo la regla CSS `.ov-monto`** que venía en el mismo commit: ninguna vista de Entrega 1 la usa (la usan las vistas de Ventas/Caja), así que habría quedado como CSS muerto.
4. `tools/MigracionCatalogo` **no se agregó al `.slnx`** (igual que en `migracion-catalogo`): es una herramienta de un solo uso, se compila y corre con `--project`.

### Evidencia de build
- `dotnet build FerreteriaLaPlatense.slnx` → **Compilación correcta, 0 errores**, 9 warnings, todos preexistentes en `entrega-1` (`NU1902` MailKit/MimeKit y `CS0114` en `HomeController.StatusCode`).
- `dotnet build tools/MigracionCatalogo/MigracionCatalogo.csproj` → **0 errores**. Confirma que el script standalone compila contra el `AppDbContext` reducido de esta rama (solo usa `Productos`/`Marcas`/`Modelos`/`Categorias`/`Proveedores`/`CodigosProveedorProducto`/`Clientes`).
- Nota operativa: los builds se corrieron con `--artifacts-path` a un directorio temporal, y la migración EF se generó en un `git worktree` aparte, porque había una instancia de la app corriendo en dev que bloqueaba `FerreteriaLaPlatense.Web/bin`. No se detuvo ese proceso.

### Guía de verificación manual antes del deploy (a ejecutar por el orquestador/cliente, no por el Implementador)
1. Aplicar `20260817233056_EtapaTres_MigracionCatalogo` sobre una copia de la base de producción y confirmar que crea las 3 tablas y las 2 columnas sin tocar nada más.
2. Levantar la app desde esta rama y confirmar que el sidebar **no** muestra Ventas, Caja, Gastos, Entregas, Dashboard ni Clientes.
3. Stock: confirmar que aparece la columna Categoría, que el combo de filtro se puebla y filtra, y que **no** aparece el botón "Recalcular clasificación ABC".
4. Producto → Editar: confirmar que aparece el campo Bonificación y, en productos migrados, el bloque "Clasificación sugerida según las ventas registradas" (debería decir que coincide con la cargada, porque la migración escribe ambos campos con el mismo valor).
5. Correr `tools/MigracionCatalogo` contra una base limpia con esta migración aplicada y verificar los conteos contra los de la corrida de dev (112.485 productos / 128 marcas / 16 categorías / 85 proveedores / 110.683 códigos / 2.990 clientes).

### Cómo reconciliar cuando Entrega 2 se apruebe
Al habilitar Entrega 2 hay que restituir desde `migracion-catalogo`: `RecalcularAsync` en el servicio y su interfaz, `StockController.RecalcularClasificacionAbc`, el botón de Stock, `ClasificacionAbcDtos.cs`, `ClasificacionAbcSettings.cs`, `ClasificacionAbcViewModels.cs`, la sección `ClasificacionAbc` de `appsettings.json` y el `Configure<ClasificacionAbcSettings>` en `DependencyInjection`. Del lado de la base, la tabla `Clientes` ya existirá con la forma final, así que la migración de Entrega 2 que la crea hay que **saltearla o marcarla como aplicada** en vez de correrla.

### Deploy real a producción — ejecutado 2026-08-17

Con las 2 decisiones de diseño de arriba aceptadas por Joaquín, se ejecutó el deploy completo:

1. **Backup de seguridad** de `db_a7251f_laplaten` (mysqldump completo, rutinas+triggers, `--single-transaction`) antes de cualquier cambio.
2. **Hallazgo antes de migrar**: producción ya tenía 1 producto cargado ("Foco led 12W", código `000001`, `CreatedAt` 2026-08-15) — un smoke-test post-deploy de Entrega 1. Confirmado con Joaquín que era de prueba; borrado (y, tras la carga real, se detectaron y borraron también sus 3 filas huérfanas de catálogo — Marca "TBCin", Categoría "Iluminación", Modelo "Led" — sin ningún producto que las referenciara).
3. **Migración EF aplicada** (`dotnet ef database update --connection "<prod>"`): verificado por `DESCRIBE`/`SHOW TABLES` en la base real que creó exactamente `Proveedores`, `Clientes`, `CodigosProveedorProducto` y las 2 columnas de `Productos` — nada más.
4. **Código publicado** a `olvidatasoft-002-site17` vía Web Deploy (`msdeploy.exe -verb:sync`, con `-enableRule:AppOffline` para liberar los locks de archivo y `-enableRule:DoNotDeleteRule` para no borrar contenido del servidor ausente en el paquete publicado — logs, etc.). Confirmado sitio arriba (`HTTP 200`) tras el sync.
5. **`tools/MigracionCatalogo` corrido contra producción real** (origen: `LaPlatense_MigracionAnalisis` restaurada localmente desde el backup del cliente; destino: MySQL de producción). Resultado, verificado independientemente por consulta directa a la base — **coincide con la corrida de dev**: 112.485 Productos, 128 Marcas, 16 Categorías, 85 Proveedores, 110.683 `CodigoProveedorProducto`, 2.990 Clientes, ABC inicial A=100/B=483/C=111.902. 270 excepciones (mismo tipo que en dev: códigos duplicados, unidades sin mapeo exacto, proveedores/clientes duplicados en el legacy) en `tools/MigracionCatalogo/bin/Release/net10.0/excepciones-migracion-20260817-215218.csv` — **pendiente de limpiar del disco local una vez que Joaquín confirme que ya no la necesita** (contiene referencias a datos del cliente).

**Credenciales de deploy**: la password de Web Deploy de la cuenta `olvidatasoft-002` (compartida por todos los sitios de clientes en SmarterASP) quedó guardada en `docs/credenciales.local.md` (gitignored, nunca al historial de git) — ver ese archivo antes de cualquier deploy futuro a un sitio de SmarterASP.

**Pendiente real remanente**: borrar el backup local (`backup-prod-pre-migracion.sql`) y el CSV de excepciones cuando Joaquín confirme que ya no los necesita — ambos contienen datos del cliente y hoy viven en una carpeta temporal de la sesión, no en el repo.

### Modelo de precios de Producto — corrección post-deploy (2026-08-18, rama `entrega-1-migracion`)

**Bug real detectado por el cliente.** Joaquín revisó los precios ya migrados a producción y encontró que el modelo de precios de `Producto` estaba incompleto y que `PrecioConDescuento` no representaba nada real. Causa exacta: la carga inicial poblaba ese campo con `fila.PrecioEfectivo > 0 && fila.PrecioEfectivo != fila.PrecioVenta ? fila.PrecioEfectivo : null`, o sea comparaba `PrecioEfectivo` (**con** IVA) contra `PrecioVenta` (**sin** IVA) como si tuvieran que coincidir cuando no hay descuento. Al tener una IVA y la otra no, casi nunca coinciden: **112.407 de 112.485 productos** quedaron con un "precio con descuento" que no era ninguna oferta.

**Fórmula real del legacy, verificada contra filas reales** de `Articulo` (base `LaPlatense_MigracionAnalisis`):

```
PrecioEfectivo (con IVA) = PrecioCompraFinal x (1 + PorcentajeRecargo/100)
PrecioVenta    (sin IVA) = PrecioEfectivo / (1 + PorcentajeIVA/100)
```

Verificada con `ArticuloKey 14`: `PrecioCompraFinal=5,48` + recargo 100% → efectivo `10,96` → `10,96 / 1,21 = 9,0579`, exacto contra el dato real.

**Campos nuevos en `Producto`:**
- `PorcentajeRecargo decimal(9,2) NULL` — el margen que faltaba modelar. Existe en el legacy como `Articulo.PorcentajeRecargo`, poblado en 121.112 de 121.691 artículos activos. Más ancho que `PorcentajeIVA` (`decimal(5,2)`) porque en el catálogo real hay recargos de tres dígitos.
- `PrecioConDescuento` **renombrado a `PrecioOferta`**, ahora con vigencia real: `PrecioOfertaDesde` / `PrecioOfertaHasta` (`datetime NULL`). Regla de negocio en `Producto.EsOfertaVigente(fecha)`: hay oferta cuando `PrecioOferta` tiene valor Y cada extremo de fecha está vacío o contiene a la fecha. La oferta del legacy (`EnOferta`/`PrecioOferta`/`DuracionOfertaHasta`) existía en apenas 1.671 de 121.691 artículos, y 1.657 de esos tenían `PrecioOferta = 0` con `DuracionOfertaHasta` en un centinela sin sentido (2100-12-31) — es decir, no hay prácticamente ninguna oferta real que migrar y **la oferta arranca vacía**.

**`PrecioVenta` sigue siendo persistido y editable a mano.** El cálculo por defecto vive en el front (jQuery en `Create.cshtml`/`Edit.cshtml`, mismo patrón que el auto-toggle de `FactorConversion`): al tocar compra, recargo o IVA se auto-completa el precio de venta sugerido; el valor escrito a mano se respeta y solo se vuelve a sugerir cuando cambia alguno de esos tres campos de origen. El Service **no** intenta detectar el override: guarda tal cual lo que llega en el DTO, como antes.

**`PrecioCompra` y `Bonificacion` quedan sin cambios estructurales, por decisión explícita de Joaquín.** `Producto.PrecioCompra` ya equivale a `Articulo.PrecioCompraFinal` del legado (así se migró) y sigue siendo un único campo manual; `Bonificacion` (texto libre "33+5") sigue siendo **puramente informativa y no participa de ningún cálculo**. El concepto de "precio de compra bruto del proveedor menos bonificación real por proveedor" queda **diferido hasta que exista el módulo de Compras real con historial de transacciones (Entrega 3, no construida)**.

**Limpieza de datos incluida en la migración EF.** El rename por sí solo era peligroso: con la semántica nueva, un `PrecioOferta` con ambas fechas en `NULL` se interpreta como *oferta vigente hoy*, así que los ~112.400 valores basura habrían puesto todo el catálogo "en oferta" a un precio inventado — y `CodigoBarrasLookupService` habría devuelto ese precio al mostrador. Por eso el `Up()` cierra con `UPDATE Productos SET PrecioOferta = NULL;`, comentado en el propio archivo. Es la única parte no reversible (el `Down()` restituye estructura, no esos valores) y es intencional: son datos inválidos, no información del cliente.

### Migración EF generada (no aplicada)
`20260818013656_EtapaTres_RecargoYPrecioOferta` — aditiva + 1 rename, **sin drops de columnas ni de tablas**:
- `RenameColumn` `Productos.PrecioConDescuento` → `Productos.PrecioOferta` (preserva la columna y sus datos; el `UPDATE` posterior los limpia a propósito).
- `+ PorcentajeRecargo decimal(9,2) NULL`
- `+ PrecioOfertaDesde datetime(6) NULL`
- `+ PrecioOfertaHasta datetime(6) NULL`
- `UPDATE Productos SET PrecioOferta = NULL;` (limpieza de los valores inválidos, ver arriba)

**No se aplicó a ninguna base (ni dev ni producción)** — la aplica Joaquín, que quiere controlar el momento exacto del re-deploy junto con la corrección del script de catálogo.

### Contrato compartido con `tools/MigracionCatalogo`
Ese script lo estaba corrigiendo Joaquín en paralelo y **no se tocó** desde acá. Al terminar se verificó que su versión ya usa exactamente los mismos nombres de propiedad definidos en el Domain (`PorcentajeRecargo`, `PrecioOferta`, `PrecioOfertaDesde`, `PrecioOfertaHasta`) y que **compila sin errores contra la entidad nueva** (`dotnet build tools/MigracionCatalogo/MigracionCatalogo.csproj` → 0 errores). El proyecto no está en el `.slnx`, así que el build de la solución no lo cubre: hay que compilarlo aparte, como se hizo.

### Deploy real del fix de precios — ejecutado 2026-08-18

Con el build combinado (Domain/Service/Views del implementador + `tools/MigracionCatalogo` del orquestador) en 0 errores:

1. **Backup de seguridad** nuevo de `db_a7251f_laplaten` (31 MB, ya con el catálogo cargado) antes de tocar nada.
2. **Migración `20260818013656_EtapaTres_RecargoYPrecioOferta` aplicada** contra producción (`dotnet ef database update --connection`) — verificado por `DESCRIBE Productos`: rename + 3 columnas nuevas, `PrecioOferta` en 0 filas tras el `UPDATE` de limpieza.
3. **Código republicado** vía Web Deploy (mismo mecanismo que el deploy del día anterior) — sitio verificado arriba (`HTTP 200`).
4. **Catálogo vaciado y recargado desde cero** (`TRUNCATE` de las 7 tablas de catálogo + re-corrida de `tools/MigracionCatalogo` contra producción real) — se eligió este camino en vez de un `UPDATE` fila por fila porque no había ninguna actividad real todavía sobre los datos migrados el día anterior (0 ajustes de stock, 0 verificados, 0 clasificación manual — confirmado antes de truncar). Resultado idéntico en cantidades a la corrida anterior (112.485 Productos, 128 Marcas, 16 Categorías, 85 Proveedores, 110.683 códigos, 2.990 Clientes) más los campos nuevos: **112.435 productos con `PorcentajeRecargo`**, **381 con `PrecioOferta` real**, **4 con fecha de vencimiento real** (no centinela).
5. **Segundo bug real encontrado en esta misma corrida** (por ejecución real, no por revisión de código): `PrecioOfertaHasta` se estaba migrando en **65.487 productos que no tenían ningún `PrecioOferta`** — el legacy pobla `DuracionOfertaHasta` también en artículos sin oferta activa, y el mapeo no lo condicionaba a que existiera un precio de oferta real. No rompía la regla de vigencia (`EsOfertaVigente` exige `PrecioOferta.HasValue` primero), pero dejaba una fecha huérfana sin sentido. Corregido en `Program.cs` (condicionar `precioOfertaHasta` a `precioOferta.HasValue`) y **aplicado en producción con un `UPDATE` puntual** (no hizo falta volver a vaciar y recargar todo): `UPDATE Productos SET PrecioOfertaHasta = NULL WHERE PrecioOferta IS NULL AND PrecioOfertaHasta IS NOT NULL` — verificado 0 huérfanos después.
6. **Verificación cruzada de la fórmula contra un producto real** post-carga: `PrecioCompra=110.886,75`, `PorcentajeRecargo=40`, `PorcentajeIVA=10,5` → `PrecioVenta` calculado `140.489,5` ≈ dato real `140.490,00`. Confirma la fórmula en producción, no solo contra la muestra del legado.

**Pendiente igual que el deploy anterior**: backups locales y el nuevo CSV de excepciones (`excepciones-migracion-20260818-000420.csv`) quedan en la carpeta temporal de la sesión — borrar cuando Joaquín confirme que ya no los necesita.

### Código de barras múltiple por producto (2026-08-21, rama `entrega-1-migracion`)

**Origen.** Misma investigación que el fix del 2026-08-19 sobre el código de barras mal migrado: al filtrar por `Tipo='B'` en la tabla `Codigo` del legado quedó a la vista que **4.371 de 23.197 artículos con código de barras tienen más de uno real** (caso testigo: "Recarga Aromatizador", un solo artículo interno con 22 EAN de fábrica, uno por aroma/marca de repuesto). El modelo de un único campo `Producto.CodigoBarras` no puede representarlo y el script de migración descartaba a esos 4.371 como "ambiguos", dejándolos sin ningún código utilizable en el escáner. Ver `1-analista-funcional.md` §10, `2-disenador-funcional.md` / `3-arquitecto-mvc.md` / `4-presupuestador.md`, sección "Código de barras múltiple por producto".

**Escaneo de reutilización (antes de codificar).** No hizo falta salir del propio repo: el patrón exacto ya está resuelto acá mismo por `CodigoProveedorProducto` (Etapa 3), que es la plantilla de la entidad nueva (mismo shape, misma forma de config Fluent, mismo criterio de "sin ABM propio, se carga por script"). Los otros proyectos del estudio (`docs/*/definiciones/5-implementador.md`) no documentan ningún equivalente de "N códigos de barras de fábrica por producto" — el hallazgo es propio de este dataset.

**Domain — `FerreteriaLaPlatense.Domain/Entities/CodigoBarrasProducto.cs` (nueva).** `SoftDestroyable` con `ProductoId`/`Producto`, `Codigo` (string, 64) y `Activo` (bool, default `true`, permite discontinuar un código sin borrar el registro ni liberar el valor).

**Diferencia deliberada de índice contra `CodigoProveedorProducto`** (documentada en el XML-doc de la entidad para que no se copie mal):
- `CodigoBarrasProducto` → único sobre **`Codigo` solo**, NO compuesto. Un código de barras de fábrica identifica al producto en sí: no puede pertenecer a dos productos distintos.
- `CodigoProveedorProducto` → único **compuesto** `(ProveedorId, CodigoDelProveedor)`, porque ahí el mismo código sí puede repetirse legítimamente entre proveedores distintos (caso real confirmado en el legado).

**`Producto.CodigoBarras` no se tocó.** Sigue siendo el código PROPIO que el cliente asigna con su impresora interna, 1 por producto, con su índice único, su validación de unicidad en `ProductoService.ValidarAsync` y su campo editable en `Create.cshtml`/`Edit.cshtml` sin ningún cambio de comportamiento. La entidad nueva es puramente aditiva.

**Infrastructure — `Data/AppDbContext.cs`.** `DbSet<CodigoBarrasProducto> CodigosBarrasProducto` + config Fluent: `Codigo` `HasMaxLength(64).IsRequired()` (mismo ancho que `Producto.CodigoBarras`, guardan el mismo tipo de dato), índice único en `Codigo`, índice no único en `ProductoId` (para "qué códigos tiene este producto"), y FK a `Producto` con `DeleteBehavior.Restrict` — mismo criterio que `CodigoProveedorProducto`. Hereda automáticamente el query filter global de soft delete.

**Application — `ICodigoBarrasLookupService` (firma sin cambios).** `BuscarPorCodigoAsync` conserva exactamente el mismo contrato (`Task<ServiceResult<ProductoLookupDto>>`); solo se amplió su lógica interna. Sigue resolviendo primero por `Producto.CodigoBarras`/`Producto.Codigo` (el código propio/interno manda) y, **solo si no encontró nada**, cae a `CodigosBarrasProducto` filtrando por `Activo`. La pantalla de Venta (Entrega 2) hereda el comportamiento nuevo sin tocarse.

**Web — ficha de Producto, solo lectura.** `ProductoDto.CodigosBarrasAlternos` / `ProductoFormViewModel.CodigosBarrasAlternos` (`List<string>`), poblados por `ProductoService.ObtenerAsync` (consulta aparte, no `Include`: la enorme mayoría de los productos no tiene ninguno) y mapeados en `ProductosController.Edit` GET. `Views/Productos/Edit.cshtml` muestra la sección "Otros códigos de barras válidos" **solo cuando hay alguno** (sin mensaje de "no hay ninguno"), como badges de solo lectura dentro de la card de Datos generales. **No se agregó en `Create.cshtml`**: un producto recién creado nunca tiene alternos. Sin ABM en esta ronda — mismo criterio que `CodigoProveedorProducto`, que tampoco tiene pantalla de gestión propia. Los alternos se repueblan también en los caminos de error del POST de `Edit` (`PoblarCodigosBarrasAlternosAsync`), porque al ser de solo lectura no viajan en el form y si no la sección desaparecería tras un error de validación.

**Migración EF generada (no aplicada):** `20260821163451_AgregarCodigoBarrasProducto` — **aditiva pura**: crea la tabla `CodigosBarrasProducto` (+ índice único en `Codigo`, índice en `ProductoId`, FK `Restrict` a `Productos`). **No toca `Productos` ni ninguna tabla existente.** No se aplicó a ninguna base (ni dev ni producción) — la aplica Joaquín.

**Backfill de los 4.371 artículos: fuera de este alcance, por decisión explícita.** `tools/MigracionCatalogo/Program.cs` **no se tocó desde acá** — lo estaba extendiendo Joaquín en paralelo (mismo patrón que el 2026-08-18). Verificado al cerrar que su versión usa exactamente los nombres del Domain definidos acá (`CodigoBarrasProducto`, `Codigo`, `Activo`, `ProductoId`, tabla `CodigosBarrasProducto`), así que el contrato compartido cierra.

**Limitación conocida (no es un bug introducido, es alcance no pedido):** el listado de Catálogo (`ProductoService.ListarAsync`) sigue buscando y mostrando **solo** `Producto.CodigoBarras` en su columna "Cód. barras" y en el filtro de texto libre — un código alterno no encuentra al producto desde ese buscador de grilla. El escáner (`ICodigoBarrasLookupService`, que es lo que usa el mostrador y usará Venta) sí lo resuelve. Extenderlo sería aditivo y no rompe nada, pero no estaba en el alcance aprobado de las 4,5h. **Cerrado el mismo día, ver sección siguiente.**

### Código de barras múltiple — gaps cerrados + rollout real a producción (2026-08-21, continuación same-day)

Joaquín pidió cerrar en la misma ronda los 3 puntos que la implementación del subagente había dejado explícitamente fuera de alcance, más la migración de datos real y una regla nueva de proceso. Ejecutado directamente (sin subagente, orquestador):

1. **Navegación `Producto.CodigosBarrasAlternos`** (`ICollection<CodigoBarrasProducto>`) agregada a `Producto.cs`, con `.WithMany(p => p.CodigosBarrasAlternos)` en `AppDbContext.cs` (antes `.WithMany()` sin navegación inversa). Verificado que no introduce cambio de esquema: migración de prueba generada y removida con `Up()`/`Down()` vacíos.
2. **`ICodigoBarrasLookupService`/`CodigoBarrasLookupService`** — el fallback a `CodigosBarrasProducto` (ya implementado por el subagente con una query de 2 pasos) se simplificó a una sola consulta usando la navegación nueva. Se agregó `ProductoLookupDto.CodigoEscaneado` (el código efectivamente tipeado/escaneado, útil para quien consuma el DTO sin acceso al request original — ej. el detalle de un ítem de Venta cuando se resolvió por un alterno).
3. **Gap de Catálogo cerrado:** `ProductoService.ListarAsync` ahora incluye `p.CodigosBarrasAlternos.Any(c => c.Activo && c.Codigo.Contains(term))` en el filtro de texto libre y proyecta `ProductoListItemDto.CantidadCodigosAlternos`. `Views/Productos/Index.cshtml` muestra un badge `+N` junto a "Cód. barras" cuando `cantidadCodigosAlternos > 0` (título con tooltip, sin listar los códigos inline — el detalle completo sigue en la ficha).
4. **Bug real encontrado y corregido en `tools/MigracionCatalogo/Program.cs`:** la lógica de resolución de alternos (`codigosAlternosPorArticulo`) estaba correctamente calculada pero **solo se insertaba en el modo correctivo (`--solo-codigo-barras`)** — el flujo principal/completo de migración nunca escribía `CodigoBarrasProducto`, solo seteaba `Producto.CodigoBarras` para los códigos sin ambigüedad. Detectado por ejecución real: tras una recarga completa de `laplatense_dev`, la tabla `CodigosBarrasProducto` tenía 0 filas y "Recarga Aromatizador" no tenía ningún alterno pese a que el análisis había confirmado 22. Corregido agregando una sección nueva (7b) inmediatamente después de insertar los `Producto` y antes de `CodigoProveedorProducto`, que resuelve cada `ArticuloKey` de `codigosAlternosPorArticulo` contra el diccionario `productoPorArticuloKey` (ya con `Id` real post-`SaveChanges`) e inserta en lotes — mismo patrón que la sección 8 ya existente.
5. **Validado en dev con el modo correctivo** (`--solo-codigo-barras`, ahora también capaz de backfillear alternos sobre una base ya migrada, sin recargar todo): 16.974 `CodigoBarras` corregidos, 8.276 códigos alternos insertados sobre 3.865 productos. Verificado por consulta directa: `CodigosBarrasProducto` = 8.276 filas, "Recarga Aromatizador" (dev Id=1567) con exactamente 22 alternos — coincide con el análisis original.
6. **Rollout a producción, con aprobación explícita de Joaquín antes de tocarla:** (a) backup fresco de `db_a7251f_laplaten` vía `mysqldump` (32 MB, guardado en carpeta temporal local, no en el repo); (b) migración `20260821163451_AgregarCodigoBarrasProducto` aplicada (`dotnet ef database update`, confirmada por `dotnet ef migrations list` sin marca `(Pending)`); (c) modo correctivo corrido contra producción real — resultado idéntico a dev en las mismas magnitudes (16.974 corregidos, 8.276 alternos / 3.865 productos); (d) verificado por consulta directa a producción: "Recarga Aromatizador" (prod Id=1835, Id distinto al de dev) con sus 22 alternos, conteos de `Productos`/`Marcas` activos sin alteración (reflejan bajas reales del cliente, no pérdida de datos); (e) build Release publicado vía Web Deploy (MSDeploy, `AppOffline`+`DoNotDeleteRule`, 11 archivos actualizados) — sitio verificado `HTTP 200` post-deploy.
7. **Detalle de conexión (solo para quien repita el script):** el origen SQL Server local (`.\MSSQLSERVER01`) dejó de resolverse por el protocolo TCP por defecto de `Microsoft.Data.SqlClient` porque el servicio `SQLBrowser` está deshabilitado en esta máquina (no se tocó el servicio) — se resolvió pasando explícitamente el connection string con protocolo Named Pipes (`Server=np:\\.\pipe\MSSQL$MSSQLSERVER01\sql\query;...`, pipe real obtenido del registro `HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL16.MSSQLSERVER01\MSSQLServer\SuperSocketNetLib\Np`), en vez de `Server=.\MSSQLSERVER01` (que sí funciona con `sqlcmd`/sesiones anteriores pero no con `SqlClient` en este estado del entorno).
8. **Regla nueva de proceso agregada a Agentes-IA** (pedido explícito de Joaquín, motivado directamente por el punto 3 de arriba): toda modificación del modelo de datos debe ir acompañada, en la misma ronda de trabajo, de un relevamiento de **todos** los sitios existentes que usan el campo/entidad que se extiende — no solo el punto de entrada que motivó el pedido. Agregada como `LP-002` en `32-estandares-qa-implementador.instructions.md` y como paso 6 (+ smoke-check 4) en la sección "Checklist modificación sobre módulo existente" de `26-checklists.instructions.md`.

**Build:** `dotnet build FerreteriaLaPlatense.slnx` y `dotnet build tools/MigracionCatalogo/MigracionCatalogo.csproj` → 0 errores en ambos.

### PAT-016 — búsqueda global multi-formato + filtros persistidos en Session, en los 6 listados (2026-08-24, rama `entrega-2`)

Aplicación de `PAT-016` (regla normativa del design system, ya vigente) sobre los **6 listados DataTables server-side** de Entrega 1 + Entrega 2: **Ventas, Clientes, Productos (Catálogo), Caja (movimientos), Gastos y Entregas**. Gap confirmado antes de tocar código: ninguno de los 6 hacía que el buscador global del DataTable (el input "Search", no un filtro de columna) matcheara contra columnas de importe o fecha, y el botón "Limpiar filtros" que ya existía en Ventas/Clientes no tenía nada que limpiar del lado servidor porque los filtros nunca se persistieron ahí. **Sin migración EF: no se tocó ninguna entidad** (por lo tanto `LP-002` no aplica — el cambio es de Services/Controllers/Views).

**Referencia portada:** `delicias-naturales` — `Helper/BusquedaHelper.cs` (`ParsearImportes`) y `Controllers/VentasController.cs` (`ListarVentas`, bloque `if (!string.IsNullOrEmpty(searchValue))`) para la búsqueda multi-formato; `Controllers/ProductosController.cs` (`Index`) para la persistencia en `Session`. Adaptado de MVC clásico/EF6 a Clean Architecture: el parseo y el armado de `extraIds` viven en Application/Infrastructure (donde ya están las queries a `AppDbContext`), la persistencia en `Session` vive en Web (único lugar con `HttpContext`).

**Piezas nuevas (2 archivos + 1 módulo JS):**
- `FerreteriaLaPlatense.Application/Helpers/BusquedaHelper.cs` — `ParsearImportes` (es-AR `"837.441,39"` / invariante `"837441.39"`, el último separador es el decimal), `RangoImporte` (`[v-0.005, v+0.005)`, nunca `==`), `TryParsearFecha` (`TryParseExact` contra `dd/MM/yyyy` y variantes), `DigitosDeBusqueda` + `IdsPorSubstringDeImporte` (la pasada de substring numérico), `EnumsQueCoinciden<T>` y `CoincideEtiqueta` (comparación sin mayúsculas/tildes/espacios, para que "caja chica" encuentre `CajaChica` y "deposito" encuentre `Deposito`, que en pantalla se ve "Depósito").
- `FerreteriaLaPlatense.Web/Helpers/FiltrosSessionHelper.cs` — `Guardar`/`Leer`/`LeerTodos`/`Limpiar`/`EsLimpieza`, con key `"<Entidad>_<Filtro>"` (ej. `"Ventas_Estado"`). **Semántica elegida: un filtro vacío BORRA su key** en vez de guardar cadena vacía — así "Limpiar filtros" queda funcional de punta a punta sin lógica extra.
- `wwwroot/js/site.js` → `window.Filtros` (`valor`, `reponer`, `etiquetaRango`, `limpiarBuscador`), para no repetir el mismo bloque en las 6 vistas.

**Patrón de `extraIds` aplicado, listado por listado** (cada tipo de dato se resuelve en su propia sub-query `SELECT Id` y al final se combina con `WHERE textoEnColumnaTexto OR Id IN (extraIds)`):

| Listado | Columnas de texto en el OR final | `extraIds` (importe) | `extraIds` (fecha) | `extraIds` (otros) |
|---|---|---|---|---|
| **Ventas** (`VentaWorkflowService`) | `Cliente.Nombre`, `CAE` | `Total` (rango + substring) | `Fecha` (Y/M/D) | `NumeroComprobante` exacto + substring; enum `EstadoVenta` |
| **Clientes** (`ClienteService`) | `Nombre`, `CuitDni`, `Telefono` | `Saldo` (rango + substring) | — (sin columna de fecha) | enum `CondicionIVA` |
| **Productos** (`ProductoService`) | `Codigo`, `Nombre`, `Marca.Nombre`, `Modelo.Nombre`, `Categoria.Nombre`, `CodigoBarras`, códigos alternos activos | `PrecioVenta` (rango + substring), `Stock` (solo rango) | — (sin columna de fecha) | — |
| **Caja** (`CajaMovimientoService`) | `OrigenTipo`, `Descripcion` | `Monto` (rango + substring) | `Fecha` (Y/M/D) | enum `TipoMovimientoCaja` |
| **Gastos** (`GastoService`) | `Descripcion` | `Monto` (rango + substring) | `Fecha` (Y/M/D) | enums `CategoriaGasto`/`FormaPagoGasto`/`TipoImpactoGasto` + badge `Anulado`/`Vigente` |
| **Entregas** (`EntregaService`) | `Direccion`, `Venta.Cliente.Nombre` | `CostoFinal` (rango + substring) | `FechaProgramada` (Y/M/D, nullable) | `VentaId` exacto + substring; enums `TipoEntrega`/`EstadoEntrega`; nombre de repartidor |

**Decisiones de criterio propio tomadas acá (no venían dadas por el patrón):**
1. **Productos — `Stock` entra por valor pero NO por substring numérico.** El substring existe para que "500" encuentre "$ 1.500,00" en un importe; aplicado a `Stock` haría que tipear un precio arrastre cualquier producto cuyo stock contenga esos dígitos, que es ruido puro. `PrecioVenta` sí tiene las dos pasadas.
2. **Entregas — se busca `FechaProgramada`, no `FechaEntregada`.** Es la única de las dos que la grilla muestra (primera columna) y la que ya usan los filtros `fechaDesde`/`fechaHasta` del listado. `FechaEntregada` no es columna visible.
3. **Tope de filas para la pasada de substring numérico (`BusquedaHelper.MaxFilasSubstringNumerico = 5000`).** Es la única pasada del patrón que no se puede resolver en SQL: `MySql.EntityFrameworkCore` (proveedor de Oracle, no Pomelo) no traduce `decimal.ToString()`, así que hay que materializar los pares `(Id, importe)` y comparar en memoria — que es exactamente lo que hace la implementación de referencia de delicias-naturales. **Acá eso no se podía portar tal cual: el catálogo tiene ~121.691 productos activos migrados**, y sin tope cada pulsación de tecla en el buscador de Catálogo se traería las 121.691 filas. Resuelto con `Take(tope + 1)` en una sola consulta (sin `COUNT` aparte): si el conjunto ya filtrado se pasa del tope se omite **solo esa pasada** — la coincidencia por valor exacto del importe y todas las columnas de texto siguen funcionando. Pérdida práctica nula: sobre más de 5.000 filas un "contiene estos dígitos" devuelve miles de resultados y no le sirve al usuario.
4. **Productos — las sub-queries de valor exacto también van acotadas (`AgregarAcotadoAsync`).** Mismo motivo de escala, caso concreto: tipear `0` matchearía el `Stock` de prácticamente todo el catálogo migrado y armaría un `Id IN (...)` de más de cien mil elementos. Los otros 5 listados **no** llevan este tope: son tablas transaccionales que no llegan a ese orden de magnitud, y agregarlo sería complejidad sin beneficio.
5. **`TryParsearFecha` usa `InvariantCulture`, no `CurrentCulture`** (el original de delicias-naturales usa `CurrentCulture`). El separador del formato es el literal `/`; no depender de la cultura del hilo hace el parseo determinista en el hosting, donde la cultura del proceso no es es-AR.
6. **`DigitosDeBusqueda` exige que el texto no tenga letras** antes de habilitar la pasada de substring (el original solo filtraba los no-dígitos). Sin eso, "Martillo 500" arrastraría todos los importes que contengan "500".
7. **El substring numérico compara contra la parte entera del importe**, igual que el original — incluir los centavos generaría falsos positivos del tipo "005" matcheando "$ 1.500,50".
8. **Se persiste también el buscador global** (key `"<Entidad>_Busqueda"`), no solo los filtros de columna, y se repone vía `search: { search: ... }` en la config del DataTable.

**Cambio de comportamiento en Clientes y Productos (deliberado, sin regresión):** los dos Controllers hacían `string.IsNullOrWhiteSpace(texto) ? request.SearchValue : texto`, es decir, usaban el buscador global como *fallback* del filtro de texto de columna. Eso se retiró: ahora `texto` es solo el filtro de columna y `request.SearchValue` lo resuelve el Service contra todas las columnas visibles. No hay pérdida — las columnas que cubría el fallback están todas dentro del nuevo OR global, más las que faltaban (Marca/Modelo/Categoría en Productos, Condición de IVA y Saldo en Clientes).

**Persistencia en Session (parte 2), por Controller.** Cada `Listar` llama a un `GuardarFiltros()` privado y cada `Index()` repone con `FiltrosSessionHelper.LeerTodos` → `ViewBag.Filtros` → `window.filtrosGuardados` en la vista. Keys por entidad: `Ventas_*` (Estado, ClienteId, FechaDesde, FechaHasta, TotalDesde, TotalHasta, Busqueda), `Clientes_*` (Texto, CondicionIVA, SaldoDesde, SaldoHasta, Busqueda), `Productos_*` (Texto, MarcaId, ModeloId, CategoriaId, PrecioDesde, PrecioHasta, StockDesde, StockHasta, Busqueda), `Caja_*` (Tipo, OrigenTipo, FechaDesde, FechaHasta, Busqueda), `Gastos_*` (Categoria, FormaPago, TipoImpacto, FechaDesde, FechaHasta, Anulado, Busqueda), `Entregas_*` (Estado, Tipo, RepartidorId, FechaDesde, FechaHasta, Busqueda). La infraestructura de `Session` ya estaba registrada en `Program.cs` (`AddDistributedMemoryCache` + `AddSession` + `UseSession`, con el comentario "persistir filtros de usuario entre navegaciones") — **no se agregó middleware nuevo, solo se empezó a usar el que ya existía**.

**"Limpiar filtros" ahora funciona de punta a punta.** El JS: vacía los controles visibles (como antes), vacía el buscador global vía `window.Filtros.limpiarBuscador(tabla)` — que limpia el estado interno **y** el `<input>` del DOM, porque DataTables no sincroniza de forma confiable el input cuando `search()` se llama por código — y manda `limpiar=true` una sola vez en ese draw, que es lo que hace que el Controller borre las keys de `Session`.

**Dos casos de reposición que necesitaron tratamiento propio en las vistas:**
- **Ventas / combo de Cliente (Select2 con carga AJAX):** no alcanza con el id guardado, hace falta la etiqueta. `VentasController.Index` pasó a `async` y resuelve el nombre con `_clienteService.ObtenerAsync` para renderizar el `<option selected>` del lado servidor. En el botón limpiar se usa `.trigger('change.select2')` en vez de `.trigger('change')`, para no disparar un draw extra antes del draw de limpieza.
- **Entregas / combo de Repartidor (poblado por `$.get`):** un `<select>` no retiene un `value` cuyo `<option>` todavía no existe. Se agrega una opción provisoria ("Cargando…") con el id guardado para que el **primer** draw ya viaje con el filtro puesto, y el callback del `$.get` la reemplaza por la lista real preservando la selección. Si el repartidor guardado ya no está en la lista, `val()` queda null y el filtro simplemente deja de aplicarse.

**Nota sobre fechas en Ventas y Caja (observación, no cambio):** `Venta.Fecha` y `CajaMovimiento.Fecha` se guardan con `DateTime.UtcNow` y se serializan a JSON con `Kind=Unspecified` (sin sufijo `Z`), así que el navegador las interpreta como hora local **sin convertir** — la grilla muestra el reloj UTC. La búsqueda por fecha compara `Year`/`Month`/`Day` de la columna tal cual está guardada, o sea que matchea exactamente lo que el usuario ve, y es el mismo criterio que ya usaban los filtros `fechaDesde`/`fechaHasta`. Que la grilla muestre UTC en vez de hora de Argentina (`ArgentinaTime`) es una inconsistencia **preexistente**, ajena a este cambio y fuera de este alcance — anotada acá para que QA no la reporte como regresión de PAT-016.

**Archivos y capas modificadas:**
- *Application*: `Helpers/BusquedaHelper.cs` (**nuevo**).
- *Infrastructure*: `Services/VentaWorkflowService.cs`, `ClienteService.cs`, `ProductoService.cs`, `CajaMovimientoService.cs`, `GastoService.cs`, `EntregaService.cs` (un `AplicarBusquedaGlobalAsync` privado en cada uno + la llamada dentro del `Listar*Async`, antes del `CountAsync` del filtrado).
- *Web*: `Helpers/FiltrosSessionHelper.cs` (**nuevo**); `Controllers/VentasController.cs`, `ClientesController.cs`, `ProductosController.cs`, `CajaController.cs`, `GastosController.cs`, `EntregasController.cs`; `Views/{Ventas,Clientes,Productos,Caja,Gastos,Entregas}/Index.cshtml`; `wwwroot/js/site.js`.
- *Domain*: **sin cambios**. Sin migración EF.

**Migración EF:** ninguna. No se tocó el modelo de datos.

**Build:** `dotnet build FerreteriaLaPlatense.slnx` → **0 errores** (9 advertencias, todas preexistentes: `NU1902` de MailKit/MimeKit y `CS0114` de `HomeController.StatusCode`). Verificado además que las 6 vistas `.cshtml` efectivamente pasan por el compilador de Razor en el build (no quedan errores de vista para runtime).

**Pruebas mínimas para QA (no ejecutadas acá — el Implementador no corre la app):**
1. En cada uno de los 6 listados, tipear un **importe** que se vea en pantalla (con y sin formato: `1.500,50`, `1500.50`, `1500`) y verificar que trae la fila.
2. Tipear `500` y verificar que trae también las filas de `$ 1.500,00` (substring). En **Catálogo**, verificar el caso con algún filtro de columna puesto (marca/categoría) — sin filtro, el conjunto supera el tope de 5.000 y esa pasada se omite a propósito.
3. En Ventas, Caja, Gastos y Entregas: tipear una **fecha** `dd/MM/yyyy` de una fila visible y verificar que la trae.
4. Tipear el texto de un **badge/enum** (`Facturada`, `Ingreso`, `Caja chica`, `Depósito`, `Anulado`, `En camino`) y verificar que filtra.
5. Dejar filtros puestos en un listado, navegar a otra pantalla, volver: los filtros y el buscador global tienen que estar como se dejaron, y la grilla ya filtrada en el primer draw.
6. **Ventas**: verificar que el combo de Cliente vuelve con el nombre correcto (no vacío ni "undefined"). **Entregas**: verificar que el combo de Repartidor vuelve con el nombre correcto y no queda en "Cargando…".
7. Botón **"Limpiar filtros"**: tiene que vaciar los controles, vaciar el texto del buscador global (visualmente, no solo los resultados) y, al volver a entrar a la pantalla, no reponer nada.
8. Regresión: los filtros de columna que ya existían (rango de fechas, combos, desde/hasta de importe) tienen que seguir funcionando igual, y el orden por columna también.

### Sprint 0 — Deuda abierta (2026-10-05, rama `entrega-1-migracion`)

Cierre de los 4 ítems de deuda previos a la Entrega 3, según el bloque "Sprint 0" del
`4-presupuestador.md`. Las decisiones de negocio venían cerradas con el cliente el 2026-10-05 y no
se re-litigaron. Un commit por ítem.

#### Resultado del escaneo de reutilización (obligatorio antes de implementar)

Paso 1 (`docs/patrones/cat_resumen.txt`) dio **3 matches directos**, no hizo falta llegar al grep
dirigido de definiciones de otros proyectos:

| Patrón | Uso en este sprint |
|---|---|
| **PAT-010** (ArgentinaTime) | Ya estaba portado al proyecto. **No se construyó nada nuevo**: se amplió el helper existente con el concepto de día/mes de negocio. Catálogo actualizado con la API nueva. |
| **PAT-001** (Ledger CC) | Base del cobro/ajuste del ítem 0.5. Su entrada tenía `pendiente_verificar: true` — **resuelto en esta misma pasada**: rutas reales confirmadas contra `C:/Sistemas/vino-y-se-fue` (`VinoSeFue.Domain/Entities/CuentaCorriente.cs` + `MovimientoCC.cs` + `MovimientoCCProveedor.cs`). |
| **PAT-019** (autocompletar con el saldo pendiente) | Aplicado al formulario de cobro: el importe arranca con la deuda completa + botón "Todo", editable para pago parcial. Tercera instancia del patrón en el proyecto. |

Reglas del catálogo aplicadas de forma activa: **LP-002** (barrido completo de usos al ampliar),
**LP-003** (decimales invariantes en los `value`), **MH-001** (apareció de verdad, ver abajo),
**MH-033** (el cobro del fiado entra al ledger de caja), **REG-010** (visibilidad del botón
acompañando al permiso real).

#### Ítem 0.2 — D8: "Confirmar y facturar" no persiste el borrador

**Ya estaba corregido en el commit `a6a78f0`** (2026-09-03, construido y **nunca deployado**). Ese
commit reemplazó `submitAccion(url)` — que armaba un form nuevo con solo el token antiforgery — por
`guardarYContinuar(continuar)`, que postea el formulario **entero** a `GuardarBorrador` con un
hidden `continuar`; el Controller guarda primero y solo sigue a `Confirmar`/`ConfirmarYFacturar` si
`result.Success`. Aplica a los **dos** botones, que era la parte que el parte de defecto pedía
verificar. Así que D8 no se volvió a implementar: se **verificó y se endureció**.

Lo que sí se agregó (defecto real encontrado al revisar ese código, no reportado por QA): la
función **no tenía guarda de doble envío**. Los dos hidden comparten `name="continuar"`, así que un
segundo click posteaba `continuar=confirmar,confirmar`, el `switch` del Controller caía en el caso
por defecto (`_`) y **el borrador se guardaba sin cerrar la venta, sin ningún aviso en pantalla** —
el mismo síntoma de clase que D8 (la pantalla dice una cosa y el server hace otra). Corregido con un
flag de reentrada, el borrado de cualquier hidden previo y el bloqueo de los tres botones de acción
hasta que el POST navegue.

#### Ítem 0.3 — D9: día de negocio de la caja

**Definición aplicada:** día de negocio = día **calendario en hora Argentina** (sin corte nocturno)
y mes de negocio = mes calendario. La base sigue guardando `DateTime` en **UTC**.

La causa raíz medida es que `CajaMovimiento.Fecha` convivía con **dos semánticas en la misma
columna**: `VentaWorkflowService` y `GastoService.AnularAsync` escribían un instante UTC, mientras
`GastoService.CrearAsync` y `RegistrarMovimientoManualAsync` escribían una fecha calendario a
medianoche. Sobre eso, las agregaciones comparaban contra `DateTime.Today` (hora del **SO**, huso
Pacífico en producción) y las guardas contra `DateTime.UtcNow.Date` (día calendario **UTC**).
Imposible ser consistente sin unificar primero la columna.

**Decisión:** `CajaMovimiento.Fecha` y `MovimientoCCCliente.Fecha` son **siempre un instante UTC**;
el día de negocio se **deriva** proyectando a ART. Toda la conversión vive en un único lugar,
`ArgentinaTime` (ampliación de PAT-010): `Hoy`, `MesActual`, `DiaDeNegocio(utc)`,
`InicioDiaUtc(día)`, `RangoDiaUtc`, `RangoDiasUtc` (último día **inclusive**, que es lo que espera
el daterangepicker) y `RangoMesUtc`. Después del cambio **no queda ningún** `DateTime.Today` ni
`DateTime.UtcNow.Date` en una decisión de día/mes, y **ninguna** `ConvertTimeToUtc`/`FromUtc` fuera
del helper.

Por **LP-002** se barrieron todos los usos, no solo Caja: `CajaMovimientoService` (filtros del
listado, búsqueda global por fecha tipeada, `EstaCerradoAsync`, resumen y cierre diario/mensual,
proyección de la fecha a ART para la grilla), `GastoService` (3 sitios, incluida la separación de
"instante que se persiste" vs. "día de negocio que se consulta" en `AnularAsync`),
`VentaWorkflowService` (la guarda de caja cerrada), `CuentaCorrienteClienteService`,
`CajaController`, `DashboardService` (ya era ART-aware pero armaba la conversión a mano — se pasó a
`RangoMesUtc`), `EntregaService.ReagendarAsync`, `ProductoService` y `CodigoBarrasLookupService`
(vigencia de oferta), más los defaults de ViewModels/DTOs y las vistas de Dashboard y Productos.

**Dos hallazgos que el parte de defecto no mencionaba:**

1. **El cierre mensual no tenía ninguna guarda de período.** Dejaba cerrar un mes anterior (bien, es
   el flujo real del cliente) pero también el mes **en curso** y cualquier mes **futuro**. Cerrar el
   mes en curso el día 10 congelaría un mes incompleto y bloquearía el resto del mes sin que nadie
   lo note hasta la primera venta rechazada. Agregada la guarda explícita: mes anterior **sí**, mes
   en curso **no** (con mensaje que explica que el cierre se hace a partir del día 1 del mes
   siguiente), mes futuro **no**. Simétricamente, `CerrarDiaAsync` ahora rechaza un día futuro (el
   día en curso sí se puede cerrar — es el cierre diario de la ferretería).
2. **`ArgentinaTime.Zone` resolvía la zona con un único `FindSystemTimeZoneById("Argentina Standard
   Time")`**, que es el id de **Windows** y no existe en Linux. Al volverse este helper la fuente
   única de **todas** las fechas del sistema, un `TimeZoneNotFoundException` ahí ya no rompería una
   pantalla: rompería el **arranque de la aplicación** (es un inicializador estático). Se le portó la
   cadena de fallback que `AfipService` ya tenía resuelta (IANA entonces id de Windows entonces UTC-3
   custom) y `AfipService` ahora **reusa** `ArgentinaTime.Zone` en vez de mantener su copia.

**Migración de datos:** `20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`, **solo
datos, sin cambio de esquema**. Suma 3 horas a las filas de `CajaMovimientos` escritas como
medianoche calendario, para que pasen a ser el instante UTC equivalente a las 00:00 ART del mismo
día. Sin esto, las filas viejas proyectarían a las 21:00 del día **anterior** y descuadrarían dos
días a la vez. Discriminador: hora exactamente `00:00:00.000000` **y** `OrigenTipo IN ('Gasto',
'Ajuste')` — los dos únicos orígenes que podían escribir así (un `DateTime.UtcNow` real no cae nunca
en la medianoche exacta al microsegundo). `Down` es la reversa exacta. Aplicada a `laplatense_dev`:
4 de 9 filas corregidas, verificado por consulta directa.

#### Ítem 0.4 — Corrección de datos: `UnidadVenta`

Modo correctivo nuevo `--solo-unidad-venta` en `tools/MigracionCatalogo`, mismo patrón que
`--solo-codigo-barras` y `--solo-codigo-propio`. **No toca SQL Server**: resuelve y retorna *antes*
de `sql.OpenAsync()`, porque la base legada ya no existe en la máquina.

Hace dos cosas, en este orden (el listado va **primero**: después del UPDATE ya no se podría
distinguir cuáles venían de `Metro`):

1. Emite el **listado** de candidatos reales a corte por metro a un CSV, con el grupo detectado.
   Solo listado: **no cambia nada y no deja nada en `Metro`**.
2. Pasa **todos** los `Metro` a `Unidad` con un `UPDATE` directo (son ~87k filas; entidad por
   entidad con tracking tardaría minutos y estamparía auditoría sobre todo el catálogo).

**No se infiere la unidad por palabra clave**, según la regla cerrada. El propio CSV confirma por
qué: entre los matches de "alambre" aparecen `ABRAZADERA DE ALAMBRE 32-50 MM` y `ALAMBRE 0,9 X 5 KG
(PRECIO X KILO)`, que no se cortan por metro. Los 14 productos en `Peso` quedan como están. Se
agregó además un aviso (no una corrección) si alguna fila queda con `UnidadCompra != UnidadVenta` y
sin `FactorConversion` válido (R4) — el script no inventa el factor; en la corrida real no hubo
ninguna.

**Números reales de la corrida contra `laplatense_dev`:**

| | Antes | Después |
|---|---:|---:|
| `Metro` | 87.542 | **0** |
| `Unidad` | 24.929 | **112.471** |
| `Peso` | 14 | 14 |

Candidatos listados (deduplicados: un producto se cuenta una sola vez, en el primer grupo que lo
toma): cable 804, manguera 535, cadena 534, alambre 276, soga/piola/cuerda 271, tanza 215 — **total
2.635**, que coincide exactamente con el total previsto en el plan. CSV conservado en
`Migracion/candidatos-corte-por-metro-20261005-121947.csv`.

**MH-001, quinta aparición en el proyecto — variante nueva.** La primera versión del listado era un
solo query con `patrones.Any(pat => EF.Functions.Like(p.Nombre.ToUpper(), pat))` sobre un `string[]`
local. Revienta con `UnreachableException: A RelationalTypeMapping collection type mapping could not
be found` — mismo defecto de fondo que el `IN` de MH-001, pero por `Any()` + `LIKE`, con un
**mensaje de error distinto** y, lo más importante, **invisible al grep canónico de la regla**
(`.Contains(`): no hay ningún `.Contains` en ese código. La encontró la **ejecución real** contra
`laplatense_dev`, no la revisión. Corregido con una consulta por patrón (parámetro escalar) uniendo
ids en un `HashSet`. La variante quedó documentada en `MH-001` de
`32-estandares-qa-implementador.instructions.md`, con el barrido ampliado a
`grep -rnE "\.(Contains|Any)\("`.

#### Ítem 0.5 — Cobro de cuenta corriente de clientes

Dos acciones nuevas sobre la pantalla que ya existía (`ClientesController.CuentaCorriente`), que
hasta ahora era **solo de consulta** — los orígenes `Pago` y `Ajuste` del enum no tenían camino desde
la UI y el cobro del fiado se llevaba por fuera del sistema.

**Cobro** (`RegistrarCobroAsync`): `Credito` con `Origen = Pago` en la CC **más** un `Ingreso` en
Caja, en **una sola transacción** con dos `SaveChanges` (el primero asigna el Id que se usa como
`OrigenId` del movimiento de caja — mismo criterio que `GastoService.CrearAsync`). Son dos hechos
distintos y uno no reemplaza al otro: **MH-033**, el ledger de caja registra toda entrada real de
dinero y el cobro del fiado es una entrada real. Guardas: importe > 0, no mayor a la deuda, fecha no
futura, **caja del día no cerrada** (misma guarda que `ConfirmarAsync`), y se rechaza el medio
`CuentaCorriente` (cobrar la CC con CC no mueve plata, solo rotaría la deuda).

**Ajuste** (`RegistrarAjusteAsync`): `Debito` o `Credito` con `Origen = Ajuste` y **motivo
obligatorio**. **No toca Caja, a propósito** — un ajuste corrige el ledger de la deuda (una venta
fiada mal cargada, una bonificación acordada, un arrastre del sistema viejo); meterlo en Caja
inflaría el arqueo con dinero que nunca se movió. Confirmación SweetAlert2 previa.

**Origen nuevo del ledger de caja: `"CobroCC"`.** Por **LP-002** se barrió todo lo que ya lee
`OrigenTipo` y se agregó la opción al combo "Origen" del filtro de `Views/Caja/Index.cshtml` — sin
eso el cobro entraría a la caja pero sería imposible de aislar en la grilla.

**Permisos — se siguió el precedente de la Entrega 2, sin inventar criterio nuevo.** *Cobrar* es
parte de la operación diaria del mostrador y es exactamente lo que ya hace un Vendedor al confirmar
una venta (genera un `CajaMovimiento` de `Ingreso` desde un documento de negocio): queda con el
`RequireVentas` del controller. *Ajustar* mueve el saldo sin respaldo de una operación real, igual
que el movimiento manual de caja, y ese es Administrador exclusivo (`CajaController` es
`RequireAdministracion`): el ajuste lleva su propio `[Authorize(Policy = "RequireAdministracion")]`
en las dos acciones, y el botón se oculta para el Vendedor (**REG-010**: la visibilidad acompaña al
permiso real, que además está validado en el server).

Las dos pantallas siguen el design system ya aplicado a las 21 existentes (`.ov-form-page`,
`.ov-page-head`, `.ov-form-actions`, `.ov-required`, Select2 por auto-init global). **LP-003**
aplicado explícitamente: el importe del cobro arranca **prellenado con la deuda**, así que `asp-for`
con cultura es-AR habría emitido `value="1234,56"`, el navegador lo habría considerado inválido y
habría dejado el input **vacío sin ningún mensaje** — se renderiza con `InvariantCulture` vía el
helper `num` de la vista. No es un riesgo latente acá, es el caso inmediato.

#### Archivos y capas modificadas (Sprint 0)

**Application**
- `Helpers/ArgentinaTime.cs` — día/mes de negocio + zona por fallback (PAT-010 ampliado).
- `Interfaces/ICajaMovimientoService.cs` — contrato del día de negocio documentado en la firma.
- `Interfaces/ICuentaCorrienteClienteService.cs` — `RegistrarCobroAsync`, `RegistrarAjusteAsync`.
- `DTOs/MovimientoCCClienteDtos.cs` — `CobroCCClienteDto`, `AjusteCCClienteDto`.
- `DTOs/CajaDtos.cs`, `DTOs/GastoDtos.cs` — defaults al día de negocio.

**Infrastructure**
- `Services/CajaMovimientoService.cs` — todas las fronteras de día/mes; totales centralizados en `ObtenerTotalesDiasAsync`/`ObtenerTotalesMesAsync`; guardas de período del cierre diario y mensual.
- `Services/CuentaCorrienteClienteService.cs` — cobro + ajuste, filtros y proyección de fecha; depende ahora de `ICajaMovimientoService`.
- `Services/GastoService.cs`, `Services/VentaWorkflowService.cs`, `Services/DashboardService.cs`, `Services/EntregaService.cs`, `Services/ProductoService.cs`, `Services/CodigoBarrasLookupService.cs` — día de negocio.
- `Services/AfipService.cs` — reusa `ArgentinaTime.Zone`, se eliminó su `ResolverTzArgentina` duplicado.
- `Migrations/20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio.cs` — solo datos.

**Web**
- `Controllers/ClientesController.cs` — 4 acciones nuevas (GET/POST de cobro y de ajuste) + helpers de repintado.
- `Controllers/CajaController.cs` — día/mes de negocio.
- `Models/CuentaCorrienteClienteViewModels.cs` — **nuevo**.
- `Models/CajaViewModels.cs`, `Models/GastoViewModels.cs`, `Models/EntregaViewModels.cs` — defaults.
- `Views/Clientes/RegistrarCobro.cshtml`, `Views/Clientes/RegistrarAjuste.cshtml` — **nuevas**.
- `Views/Clientes/CuentaCorriente.cshtml` — botones de acción.
- `Views/Caja/Index.cshtml` — origen `CobroCC` en el filtro (LP-002).
- `Views/Ventas/Editar.cshtml` — guarda de doble envío en `guardarYContinuar`.
- `Views/Dashboard/Index.cshtml`, `Views/Productos/Edit.cshtml` — día de negocio.

**tools**
- `MigracionCatalogo/Program.cs` — modo `--solo-unidad-venta`.

#### Migraciones EF generadas

`20261005151611_D9_NormalizarFechaCajaMovimiento_DiaDeNegocio` — **solo datos, sin DDL**. Aplicada a
`laplatense_dev`. **Producción está dos migraciones atrás**: le falta esta y
`20260903160346_EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago` (el ítem 0.1, que es de
Joaquín).

#### Evidencia

- **Build de la solución: 0 errores** (`dotnet build FerreteriaLaPlatense.slnx`). Verificado que las
  vistas Razor **sí** se compilan en el build (comprobado introduciendo a propósito un símbolo
  inexistente en una `.cshtml`: el build falló; revertido), así que el build limpio también cubre las
  dos pantallas nuevas.
- **Grafo de DI validado** con `ValidateOnBuild` + `ValidateScopes` sin levantar la app:
  `CuentaCorrienteClienteService` resuelve con su dependencia nueva, sin ciclo ni captive dependency
  (ambos `Scoped`).
- **Fronteras de día/mes: 8 de 8 verificaciones ejecutadas en verde**, incluido el criterio de
  aceptación de D9 (instante UTC `2026-09-25 01:44` da día de negocio `2026-09-24`; el arqueo del 24
  la incluye y el del 25 no; y la venta de las 22:44 del 30/09 cae en el mes de septiembre).
- **Cobro/ajuste ejercitados contra `laplatense_dev` a nivel Service: 24 de 24 en verde** — el cobro
  baja la CC y genera exactamente un `Ingreso` de caja con `OrigenTipo="CobroCC"` y `OrigenId`
  correcto; el ajuste mueve el saldo y **no** genera movimiento de caja; las 4 guardas del cobro
  rechazan; con la caja cerrada el cobro y el movimiento manual quedan bloqueados; se puede cerrar un
  mes anterior y **no** el mes en curso ni uno futuro. Las filas de prueba se borraron al final (dev
  quedó en su línea base: 9 `CajaMovimientos`, 0 `MovimientosCCCliente`).
- **Ítem 0.4 corrido contra `laplatense_dev`** con los números de la tabla de arriba.
- **Sin smoke test funcional por navegador** (regla del rol). La verificación en navegador queda en
  la guía de abajo — ver la nota de discrepancia con el brief en `trazabilidad.md`.

#### Guía de verificación manual (a ejecutar por el cliente/QA, no por el Implementador)

1. **D8** — abrir un borrador de venta, cambiar la **cantidad** de un ítem sin guardar, apretar
   **Confirmar venta**: la venta queda `Confirmada` con la cantidad **que estaba en pantalla**.
   Repetir con "Confirmar y facturar". Hacer **doble click** rápido en Confirmar: tiene que confirmar
   una sola vez, nunca quedar en Borrador guardado.
2. **D9 (el criterio de aceptación)** — registrar una venta cerca de las **22:44 hora Argentina** y
   verificar que aparece en el arqueo **de ese día**, no del siguiente. Después **cerrar la caja de
   ese día** e intentar una venta nueva con esa fecha, a cualquier hora: tiene que quedar bloqueada.
3. **D9 / mensual** — el **día 1**, cerrar la caja del **mes anterior**: tiene que dejar. Intentar
   cerrar el **mes en curso**: tiene que rechazar con el mensaje de "todavía está en curso".
4. **D9 / listados** — mirar la columna Fecha de Caja y de la cuenta corriente: la hora mostrada
   tiene que ser la hora **argentina** del movimiento. Filtrar por un rango de fechas que incluya un
   movimiento nocturno y confirmar que cae del lado esperado.
5. **0.4** — en Catálogo, confirmar que ya **no hay productos en "Metro"** y abrir alguno del CSV de
   candidatos (ej. un cable) para ver que quedó en "Unidad" a la espera de la marcación manual.
6. **0.5 / cobro** — cliente con deuda, **Registrar cobro**: el importe viene **prellenado con la
   deuda**, el botón "Todo" lo repone, un importe mayor a la deuda se rechaza. Guardar y verificar
   que (a) baja el saldo, (b) aparece el movimiento `Pago` en el historial de la cuenta y (c) aparece
   un **Ingreso** en Caja filtrable por origen **"Cobro de cuenta corriente"**.
7. **0.5 / ajuste** — con usuario **Administrador**: registrar un ajuste de crédito con motivo, mueve
   el saldo y **no** aparece nada en Caja. Intentar sin motivo: rechaza.
8. **0.5 / permisos** — con usuario **Vendedor**: el botón "Ajuste manual" **no** se ve, y entrar a
   `/Clientes/RegistrarAjuste/{id}` a mano tiene que dar acceso denegado. "Registrar cobro" **sí**
   tiene que estar disponible.
9. **LP-003** — guardar un cobro, volver a abrir el formulario y mirar que los inputs numéricos **no**
   quedan vacíos.

#### Riesgos y supuestos (Sprint 0)

- **La migración de datos D9 asume el discriminador de la medianoche exacta.** Verificado contra
  `laplatense_dev` (4 filas, todas legítimas). En producción el volumen es chico pero **conviene
  mirar el conteo antes de aplicar**: `SELECT OrigenTipo, COUNT(*) FROM CajaMovimientos WHERE
  TIME_TO_SEC(TIME(Fecha))=0 AND MICROSECOND(Fecha)=0 GROUP BY OrigenTipo`.
- **`Gasto.Fecha` y `CierreCajaDiario.Fecha` siguen siendo fechas calendario** (día de negocio
  argentino), no instantes. Es deliberado y está documentado en el código: son columnas de semántica
  date-only. No se las tocó ni se las debe proyectar.
- **El ajuste de CC no impacta Caja, por diseño.** Si el cliente lo usa para registrar un cobro real,
  la caja va a quedar corta. Mitigado en el texto de la pantalla, no por código.
- **El cobro no registra la cuenta real donde entró la plata** (MH-034). El medio de pago queda en la
  descripción del movimiento, pero el ledger de caja sigue siendo único y sin dimensión "cuenta".
  Consistente con lo que ya hace Ventas; si el negocio necesita conciliar, es un cambio de alcance
  aparte.
- **No se tocó la vigencia de oferta más allá de cambiar el "hoy"**, ni el circuito AFIP (sigue
  deshabilitado, sin certificado).

#### Hallazgo fuera de alcance, para decidir (CERRADO el 2026-10-05 en el commit `7477550`)

`DashboardService` contaba las ventas del día y del mes filtrando **solo**
`Estado == EstadoVenta.Facturada`. Se resolvió con el criterio anticipado acá
(`Confirmada || Facturada`), junto con el mismo filtro en `ClasificacionAbcAutomaticaService`.
Queda como antecedente de por qué apareció después `LP-008`: el código se corrigió pero los
comentarios prescriptivos que explicaban el criterio viejo no, y dejaron una regla de negocio
falsa en el repo (ver la sección siguiente).

### Sprint 0 — ronda de fixes de QA: los 7 defectos abiertos (2026-10-05, rama `entrega-1-migracion`)

Cierre de los 7 partes de defecto que dejaron los 3 lotes de QA del Sprint 0 (`LP-006` a `LP-012`
en `docs/qa/regresiones-manuales.yml`; parte completo en `6-qa.md`). El lote 1 (día/mes de negocio)
había dado **NO-GO** con 2 `major` en el circuito de dinero, y el deploy a producción estaba
bloqueado hasta cerrarlos. **Un solo commit** (`00f7dd4`), **sin migración EF** — no se modificó el
modelo de datos (verificado con `dotnet ef migrations has-pending-model-changes`: *"No changes have
been made to the model since the last migration"*).

#### Resultado del escaneo de reutilización

Paso 1 (`docs/patrones/cat_resumen.txt`): dos matches directos, los dos aplicados.

- **`PAT-010`** (ArgentinaTime, hora correcta en hosting compartido) — es la pieza que ya centraliza
  la convención; `LP-009`/`LP-010`/`LP-011` se resuelven **ampliándola**, no construyendo nada nuevo.
- **`PAT-016`** (búsqueda global multi-formato + filtros persistidos en Session) — `LP-012` es
  exactamente su caso de uso; se portó la implementación que ya está en los 6 listados de este mismo
  repo (`BusquedaHelper` + `FiltrosSessionHelper` + `window.Filtros`), sin escribir helpers nuevos.

No se agregó ningún patrón al catálogo: todo lo implementado es aplicación de patrones ya
catalogados o corrección puntual de este sistema.

#### `LP-009` (major) — la guarda de caja cerrada ignoraba el cierre mensual

Causa confirmada: la guarda consultaba **únicamente** `CierresCajaDiarios`. El commit `628cb7a`
había agregado la mitad "no se puede cerrar el mes en curso ni uno futuro" y dejó afuera la
simétrica "no se puede imputar a un mes ya cerrado" — son la misma regla vista de los dos lados.

**Pieza nueva, una sola y compartida:** `ICajaMovimientoService.ValidarPeriodoAbiertoAsync(diaDeNegocio, accion)`,
que consulta **mes y día** y devuelve `null` si el período está abierto o el **mensaje listo para
mostrar** si está cerrado (más `EstaMesCerradoAsync(anio, mes)`, que antes era una consulta inline
dentro de `CerrarMesAsync`). Se eligió que devuelva el mensaje y no un bool para que ninguna vía de
escritura pueda redactar el suyo y divergir: el parámetro `accion` completa la frase
(*"La caja del mes 09/2026 ya tiene cierre mensual: no se puede registrar un gasto con esa fecha."*).
El mes se consulta **antes** del día: es el bloqueo más fuerte (abarca días que individualmente
pueden no tener cierre diario) y es el mensaje que al usuario le explica de verdad por qué no puede
imputar ahí.

**Todas las vías de escritura de caja quedaron cubiertas** (no solo la que reportó QA), relevadas
por los usos de `EstaCerradoAsync`:

| Vía de escritura | Archivo | Día de negocio que valida |
|---|---|---|
| Venta confirmada (es el paso que mueve caja; `FacturarAsync` no la toca) | `VentaWorkflowService.ConfirmarAsync` | `ArgentinaTime.Hoy` |
| Gasto — alta | `GastoService.CrearAsync` | `dto.Fecha` (la que eligió el usuario) |
| Gasto — anulación (contramovimiento fechado hoy) | `GastoService.AnularAsync` | `ArgentinaTime.DiaDeNegocio(ahora)` |
| Cobro de cuenta corriente | `CuentaCorrienteClienteService.RegistrarCobroAsync` | `dto.Fecha` |
| Movimiento manual de caja | `CajaMovimientoService.RegistrarMovimientoManualAsync` | `dto.Fecha` |
| Cierre diario (no es un movimiento, pero no puede abrirse dentro de un mes cerrado) | `CajaMovimientoService.CerrarDiaAsync` | `fechaDia` |

**Decidido NO cubrir, con motivo:** `CuentaCorrienteClienteService.RegistrarAjusteAsync` **no** lleva
la guarda, porque por diseño explícito no toca Caja (un ajuste corrige el ledger de la deuda, no
representa plata que entró o salió — ver su XML-doc). No es una vía de escritura de caja.

#### `LP-010` (major) — `Venta.Fecha` quedó con la semántica vieja

Decisión ya cerrada por el orquestador y aplicada tal cual: `Venta.Fecha` sigue el **mismo** criterio
que `CajaMovimiento.Fecha` — instante UTC en la base, día de negocio derivado proyectando a ART con
`ArgentinaTime`. Sin una segunda convención, y **sin migración de datos**: la columna ya guardaba
`DateTime.UtcNow`, lo que estaba mal era **cómo se consumía**.

Cuatro puntos de consumo corregidos en `VentaWorkflowService`, más el XML-doc de la entidad:

1. **Filtros `fechaDesde`/`fechaHasta`**: comparaban la columna UTC contra la medianoche cruda del
   día elegido → ahora `ArgentinaTime.InicioDiaUtc(...)` en los dos extremos (hasta inclusive).
2. **Proyección del listado**: se materializa la página ya paginada en un tipo anónimo y recién
   después se proyecta `Fecha = ArgentinaTime.From(...)` — la conversión no se traduce a SQL. Mismo
   patrón exacto que `CajaMovimientoService.ListarMovimientosAsync`.
3. **Buscador global por fecha** (`PAT-016`): comparaba `Year`/`Month`/`Day` de la columna cruda
   (= día calendario UTC) contra el día que tipeó el usuario (= día argentino) → ahora
   `ArgentinaTime.RangoDiaUtc(fecha)`.
4. **Detalle** (`MapearDetalleAsync`): `Fecha = ArgentinaTime.From(venta.Fecha)`.

Verificado además que **`Venta.Fecha` nunca se escribe desde un DTO ni desde un ViewModel** (solo el
inicializador `= DateTime.UtcNow` de la entidad), así que no hay round-trip que pueda re-persistir el
valor ya proyectado a ART como si fuera UTC. El `OrderBy` sigue sobre la columna UTC a propósito: el
offset es fijo, así que el orden UTC y el orden ART son idénticos.

#### Barrido `LP-002` de la convención de fechas — resultado completo

Es la **segunda** vez en el sprint que un barrido `LP-002` queda incompleto (la primera fue el
Dashboard/ABC), así que se relevaron **todas** las propiedades `DateTime` de `Domain/Entities` y
todos sus sitios de uso, no solo `Venta`. Tabla de cierre:

| Entidad.Campo | Semántica en base | Estado |
|---|---|---|
| `CajaMovimiento.Fecha` | instante UTC | OK (D9) |
| `MovimientoCCCliente.Fecha` | instante UTC | OK (proyecta con `From`, filtra por rango UTC) |
| `Venta.Fecha` | instante UTC | **corregido acá** (`LP-010`) |
| `AjusteStock.Fecha` | instante UTC | **corregido acá** — el historial de stock la mostraba cruda con hora |
| `Entrega.FechaEntregada` | instante UTC | **corregido acá** — el detalle de entrega la mostraba cruda con hora |
| `ApplicationUser.CreatedAt` | instante UTC | **corregido acá** — listado y detalle de usuarios (campo de auditoría, no de negocio, pero misma convención) |
| `Gasto.Fecha` | día calendario ART | OK (se guarda y se compara como día) |
| `Gasto.FechaAnulacion` | instante UTC | OK — no se muestra en ninguna pantalla |
| `CierreCajaDiario.Fecha` | día calendario ART | OK |
| `CierreCajaDiario/Mensual.FechaCierre` | instante UTC | OK (proyecta con `From`) |
| `Entrega.FechaProgramada` | día calendario ART | OK (se guarda con `.Date`, se filtra como día) |
| `PagoVenta.Fecha` | instante UTC | OK — no se expone en ningún DTO |
| `Producto.PrecioOfertaDesde/Hasta` | día calendario ART | OK (vigencia cortada contra `ArgentinaTime.Hoy`) |
| `Venta.VencimientoCAE` | fecha pura de AFIP (`yyyyMMdd`) | OK — no es un instante, no se proyecta |
| `Notification.CreatedAt`/`ReadAt`, `SoftDestroyable.*`, `ApplicationUser.UpdatedAt` | instante UTC | OK — auditoría, no se renderiza |

**Tres hallazgos propios** (`AjusteStock.Fecha`, `Entrega.FechaEntregada`,
`ApplicationUser.CreatedAt`), los tres corregidos en este mismo commit como pedía el parte.

#### `LP-007` (minor) — un valor desconocido de `continuar` era un no-op silencioso

El `switch` del POST de Venta resolvía el `default` como "guardar y listo", así que un valor
desconocido devolvía HTTP 200 con el mensaje de guardado mientras la venta quedaba abierta sin que
nadie se enterara. Ahora **solo la ausencia del campo** significa "guardar el borrador"
(`null or ""`, con `Trim()` previo) y cualquier otro valor cae en `AccionNoReconocida`.

**Decisión de criterio propio:** no se devuelve `BadRequest` seco. Cuando se llega a ese punto el
borrador **ya quedó guardado**, así que un 400 haría pensar que no se guardó nada; se redirige a
`Editar` con `TempData["ErrorMessage"]` diciendo explícitamente *"el borrador se guardó pero la venta
NO se cerró"*. Cumple el criterio (nunca un 200 que parece éxito) y no miente sobre el estado real.
Verificado que el botón "Guardar borrador" (un `type="submit"` que no agrega el hidden) sigue
cayendo en la rama de guardado normal.

Se corrigió además el **comentario** de `Views/Ventas/Editar.cshtml` que afirmaba la premisa que QA
refutó (que el doble click posteaba `"confirmar,confirmar"` — el model binder toma el primer valor).
La guarda de reentrada **se queda**, porque lo que previene sí es real: dos POST de cierre en vuelo
sobre la misma venta, donde el segundo encuentra la venta fuera de `Borrador` y le muestra un error
innecesario al vendedor. El comentario ahora dice ese motivo, no el inventado.

#### `LP-008` (minor) — comentarios que contradecían el código

`ClasificacionAbcAutomaticaService` (XML-doc de clase + comentario previo al `Where`) y
`DashboardService` (XML-doc de `ObtenerTopProductosMesAsync`) seguían afirmando que *"solo cuentan
los ítems en estado `Facturada`"* y que *"el filtro por `Estado == Facturada` es imprescindible"*,
cuando el código ya filtra `Confirmada || Facturada` desde `7477550`. Son prescriptivos, así que
dejaban una **regla de negocio falsa** en el repo.

**Corregidos, no borrados**: se conserva (y se explicita mejor) la parte válida —por qué `Borrador` y
`Anulada` quedan afuera, que un borrador abandonado infla la rotación y sube la clase ABC— y se
agrega por qué `Confirmada` **tiene que** estar: es el estado normal de una venta cerrada, la factura
es un paso posterior y opcional, y dejarla afuera subcontaba la rotación real. Se arregló también la
referencia cruzada rota (`DashboardService.ObtenerProductosMasVendidos`, que no existe → es
`ObtenerTopProductosMesAsync`).

#### `LP-006` (minor) — reloj de 12 horas sin AM/PM

No era un problema de huso: el wire ya entrega la fecha proyectada a ART. Era `toLocaleString('es-AR')`
a secas en el cliente, que usa reloj de 12 h sin meridiano (13:04 → `01:04:22`, 00:00 → `12:00:00`).

**Pieza nueva:** `window.Fmt` en `site.js`, con `fechaHora(v)` (`hour12: false`, sin segundos — en una
grilla no aportan) y `fecha(v)` para las columnas que son día calendario. Las dos toleran null y fecha
inválida. Se reemplazaron los **8** renders de fecha de las grillas (`Caja/Index`, `Caja/Cierres` ×2,
`Clientes/CuentaCorriente`, `Stock/Historial`, `Ventas/Index`, `Gastos/Index`, `Entregas/Index`) para
que el formato no vuelva a divergir pantalla por pantalla. Se incluyeron también los renders de solo
fecha, que no tenían el bug: el objetivo es que no quede ningún `toLocaleString`/`toLocaleDateString`
de fecha suelto en las vistas.

#### `LP-011` (minor) — `/Caja/Mensual?mes=13` devolvía HTTP 500

La validación *"Mes o año inválido"* de `628cb7a` era **código muerto para este GET**: el `mes=13`
llegaba hasta `ArgentinaTime.RangoMesUtc` → `new DateTime(anio, 13, 1)` →
`ArgumentOutOfRangeException`, mucho antes de llegar a ella (la validación vivía solo en
`CerrarMesAsync`).

Resuelto poniendo el rango válido en un único lugar —`ArgentinaTime.EsMesDeNegocioValido(anio, mes)`
(2000–2999, 1–12)— consultado **tanto** por el GET de la pantalla **como** por `CerrarMesAsync`, para
que las dos no puedan divergir. El GET inválido ahora redirige al mes en curso con
`TempData["ErrorMessage"]` (el redirect no lleva parámetros, así que no puede reciclar). Se documentó
el precondicional en el XML-doc de `RangoMesUtc`.

#### `LP-012` (minor) — buscador que no buscaba en los listados de cierres

**Corresponde `PAT-016`**: las dos pantallas dibujaban el buscador del DataTable (está activo por
defecto) y los Services ignoraban `request.SearchValue`. Se aplicó igual que en los otros 6 listados,
en vez de sacar el control.

| Listado | Columna de texto en el OR final | `extraIds` (importe) | `extraIds` (fecha) | `extraIds` (otros) |
|---|---|---|---|---|
| **Cierres diarios** | `FullName` del usuario que cerró | `TotalIngresos`/`TotalEgresos`/`Saldo` (rango + substring) | `Fecha` (día calendario, comparación directa) **y** `FechaCierre` (instante UTC, rango del día de negocio) | — |
| **Cierres mensuales** | `FullName` del usuario que cerró | `TotalIngresos`/`TotalEgresos`/`Saldo` (rango + substring) | — (no hay columna de fecha en la grilla) | `Anio` tipeado; nombre del mes (`"septiembre"` → `Mes == 9`) |

**`MH-001` evitado, y por qué fue el riesgo real de este ítem.** La única columna de texto de las dos
grillas es el nombre del usuario que cerró, que vive en `AspNetUsers` y **no tiene navegación** desde
las entidades de cierre. El camino intuitivo —resolver los ids de usuario que matchean y filtrar con
`CerradoPorUsuarioId IN (...)`— es exactamente `MH-001`: un `IN` sobre colección local de **string**,
que en este provider revienta incluso con la colección vacía (ya pasó 4 veces acá, y está documentado
en el propio `ListarCierresDiariosAsync`). Se resolvió con una **sub-consulta correlacionada**
(`_context.Users.Any(u => u.Id == c.CerradoPorUsuarioId && u.FullName.Contains(termino))`), que se
traduce entera a SQL y nunca trae una colección a memoria. **Traducción verificada sin levantar la
app ni conectar a ninguna base**, con `ToQueryString()` sobre el `DbContext` configurado con el
provider real: baja a `EXISTS (SELECT 1 FROM AspNetUsers AS a WHERE a.Id = c.CerradoPorUsuarioId AND
(... LOCATE(...) > 0))`. En el listado mensual, el match por nombre de mes también se armó como un
`Where(c => c.Mes == mes)` por mes encontrado, en vez de un `Contains` sobre la lista local de ≤12
ints — la forma prohibida no se usa ni donde sería inocua.

**`PAT-016` parte 2 (filtros en Session)** aplicada a los dos listados, con las keys
`CierresDiarios_*` (FechaDesde, FechaHasta, Busqueda) y `CierresMensuales_*` (Anio, Busqueda), más el
botón "Limpiar filtros" funcional de punta a punta (`limpiar=true` una sola vez en el draw del click,
`window.Filtros.limpiarBuscador` para vaciar el `<input>` visible).

**Gap de diseño cerrado de paso:** `MensualListar` leía un filtro `anio` del form que **la vista nunca
mandaba** (filtro muerto desde que se escribió). Se agregó el control de Año al header del listado de
cierres mensuales, con su botón de limpiar — por la regla del rol de que el usuario tiene que poder
filtrar por lo que ve en la grilla (la columna "Período" muestra mes y año). Sin `value` en el
`<input type="number">`, así que `LP-003`/`D5` no aplica: el valor se repone por JS desde Session.

#### Archivos y capas modificadas

- *Domain*: `Entities/Venta.cs` (**solo XML-doc** de la convención de `Fecha` — sin cambio de modelo).
- *Application*: `Helpers/ArgentinaTime.cs` (`EsMesDeNegocioValido` + precondición de `RangoMesUtc`),
  `Interfaces/ICajaMovimientoService.cs` (`EstaMesCerradoAsync`, `ValidarPeriodoAbiertoAsync`).
- *Infrastructure*: `Services/CajaMovimientoService.cs` (guarda de período, las dos búsquedas globales
  de cierres, `NombresMes`), `VentaWorkflowService.cs` (`LP-009` + los 4 puntos de `LP-010`),
  `GastoService.cs`, `CuentaCorrienteClienteService.cs` (guarda de período), `AjusteStockService.cs`,
  `EntregaService.cs` (barrido `LP-002`), `ClasificacionAbcAutomaticaService.cs`,
  `DashboardService.cs` (`LP-008`).
- *Web*: `Controllers/CajaController.cs` (`LP-011` + Session de los 2 listados),
  `Controllers/VentasController.cs` (`LP-007`), `wwwroot/js/site.js` (`window.Fmt`),
  `Views/Caja/Cierres.cshtml`, `Views/Caja/Mensual.cshtml` (`LP-012` + `LP-006`),
  `Views/Caja/Index.cshtml`, `Views/Clientes/CuentaCorriente.cshtml`, `Views/Stock/Historial.cshtml`,
  `Views/Ventas/Index.cshtml`, `Views/Gastos/Index.cshtml`, `Views/Entregas/Index.cshtml` (`LP-006`),
  `Views/Users/Index.cshtml`, `Views/Users/Details.cshtml` (barrido `LP-002`),
  `Views/Ventas/Editar.cshtml` (comentario de `LP-007`).

#### Migración EF

**Ninguna.** `dotnet ef migrations has-pending-model-changes` → *"No changes have been made to the
model since the last migration"*. Tampoco hizo falta migración **de datos**: `Venta.Fecha` ya guardaba
instantes UTC correctos; el defecto era de consumo, no de almacenamiento.

#### Evidencia de build y de verificación técnica

- `dotnet build FerreteriaLaPlatense.slnx` → **0 errores**, 9 advertencias, **todas preexistentes**
  (8 × `NU1902` de MailKit/MimeKit + `CS0114` de `HomeController.StatusCode`). Corrido 3 veces: tras
  la primera tanda de cambios, tras el comentario de `Editar.cshtml`, y tras normalizar los BOM que
  había introducido el script de reemplazo masivo en las vistas. Las vistas Razor pasan por el
  compilador en el build, así que no quedan errores de vista para runtime.
- **Traducción a SQL verificada con `ToQueryString()`** (no es un smoke test: no levanta la app ni abre
  conexión a ninguna base) para las 5 formas de consulta nuevas o modificadas que podían no traducir:
  la sub-consulta correlacionada de usuario en los dos listados de cierres, la misma combinada con
  `ids.Contains` de `extraIds`, el filtro por rango UTC de `Venta.Fecha` con la proyección anónima, y
  el OR de los 3 importes de cierres. Las 5 bajan a SQL válido.
- **No se ejecutó smoke test funcional** (regla del rol): la verificación por navegador la hace QA. Lo
  que sí se verificó por lectura dirigida: que `Venta.Fecha` no se escribe desde ningún DTO/ViewModel,
  que "Guardar borrador" no cae en la rama de error nueva de `LP-007`, y los 15 campos `DateTime` de
  la tabla del barrido `LP-002`.
- **Producción intacta**: no se ejecutó ningún deploy, ni Web Deploy, ni ninguna operación contra
  `mysql8001.site4now.net`. La base `laplatense_qa_d9` que QA dejó como fixture **no se tocó ni se
  borró**.

#### Riesgos residuales y asunciones

- **`ValidarPeriodoAbiertoAsync` hace 2 consultas** (mes y día) donde antes había 1. Son dos `EXISTS`
  sobre tablas chicas con índice (`IX_CierresCajaMensuales_Anio_Mes`, `IX_CierresCajaDiarios_Fecha`) y
  corren una vez por operación de escritura, no por fila. Impacto despreciable.
- **La UI no avisa de antemano que un mes está cerrado.** El rechazo es claro y llega al guardar, que
  es lo que pide el criterio de aceptación, pero el formulario de movimiento manual deja elegir una
  fecha de un mes cerrado y recién al enviar explica el problema. Mostrar el estado del mes en la
  pantalla de Caja sería una mejora de UX — **no se hizo para no ampliar alcance**; queda anotado.
- **El mensaje de `GastoService.AnularAsync` cambió**: antes decía *"no se puede anular un gasto hasta
  el próximo día hábil"*, ahora *"no se puede anular un gasto hoy"*. Es más veraz (el día siguiente
  podría estar cerrado también) pero es un texto distinto del que QA vio en el lote anterior.
- **Búsqueda por nombre de mes en cierres mensuales**: se compara contra la etiqueta real de la grilla
  con la normalización de `BusquedaHelper` (sin tildes ni mayúsculas), así que `"septiembre"` matchea
  pero `"setiembre"` **no**. Decisión deliberada: la grilla dice "Septiembre".
- **`Venta.Fecha` sigue siendo el momento en que nació el BORRADOR**, no el de la confirmación. Una
  venta empezada el día N y confirmada el N+1 aparece en el día N en Ventas y en el N+1 en Caja. Es
  comportamiento preexistente, ajeno a `LP-010` (que era de proyección, no de qué instante se guarda),
  y no está en ningún parte de defecto — **si el negocio espera otra cosa, es una decisión de
  Joaquín**, no un bug de esta ronda.
- **`ApplicationUser.CreatedAt` se proyectó desde la vista**, no desde un Service: `UserListViewModel`/
  `UserDetailsViewModel` exponen la entidad y no hay un mapeo intermedio donde ponerlo. Es un campo de
  auditoría, así que no se agregó una capa de DTO solo para esto.

#### Pruebas mínimas requeridas para QA (re-verificación)

1. **`LP-009`** — con un mes cerrado (el fixture `laplatense_qa_d9` ya tiene 09/2026 cerrado), probar
   las **6** vías con fecha dentro de ese mes: movimiento manual de caja, gasto nuevo, anulación de
   gasto, cobro de cuenta corriente, confirmación de venta y cierre diario. Las 6 tienen que rechazar
   con el mensaje del **mes** (*"ya tiene cierre mensual"*). Verificar además que el ledger de egresos
   de la pantalla vuelva a coincidir con el total real (el defecto mostraba $777,77 contra $8.555,54).
2. **`LP-009` regresión** — con el mes **abierto** y un **día** cerrado, las mismas 6 vías tienen que
   seguir rechazando con el mensaje del **día**; con los dos abiertos, tienen que seguir funcionando.
3. **`LP-010`** — la Venta 8 (24/08 22:44 ART) tiene que verse **24/08** en el listado de Ventas, en su
   detalle, en Caja y en el Dashboard. Las tres pantallas tienen que decir lo mismo.
4. **`LP-010`** — filtrar Ventas por el rango `24/08 - 24/08` tiene que traer esa venta, y tipear
   `24/08/2026` en el buscador global también. Con `25/08` no tiene que aparecer.
5. **Barrido `LP-002`** — historial de ajustes de stock, detalle de una entrega finalizada y listado/
   detalle de usuarios: todas las fechas con hora tienen que mostrar el día y la hora argentinos
   (probar con un registro creado entre las 21:00 y las 24:00 ART).
6. **`LP-007`** — postear a `Ventas/GuardarBorrador` con `continuar=cualquier-cosa` (DevTools o un
   form armado a mano) tiene que mostrar el error explícito, **no** el mensaje de guardado. Y los 3
   caminos normales (Guardar borrador / Confirmar / Confirmar y facturar) tienen que seguir igual.
7. **`LP-006`** — un cobro de las 13:04 tiene que leerse `13:04` (no `01:04`) y un movimiento de las
   00:00 tiene que leerse `00:00` (no `12:00`), en el ledger de CC **y** en `/Caja`. Revisar también
   Ventas, Historial de stock y los dos listados de cierres.
8. **`LP-011`** — `/Caja/Mensual?mes=13`, `?mes=0`, `?anio=99999`, `?anio=1` y `?mes=abc` tienen que
   mostrar el mensaje de mes inválido y el mes en curso, nunca un 500. Y `?anio=2026&mes=9` tiene que
   seguir funcionando.
9. **`LP-012`** — en los dos listados de cierres, buscar por: importe con y sin formato (`1.500,50`,
   `1500.50`, `1500`), substring de importe (`500` tiene que traer `$ 1.500,00`), fecha `dd/MM/yyyy`
   (en el diario tiene que matchear tanto la fecha del cierre como la fecha de ejecución), nombre del
   usuario que cerró, año (`2026`) y nombre del mes (`septiembre`, solo en el mensual).
10. **`LP-012`** — dejar filtros y buscador puestos en los listados de cierres, navegar a otra pantalla
    y volver: tienen que estar como se dejaron y la grilla ya filtrada en el primer draw. El botón
    Limpiar tiene que vaciar los controles **y** el texto del buscador, y al volver a entrar no
    reponer nada. Verificar que el filtro de Año nuevo del listado mensual filtra de verdad.
11. **Regresión `MH-001`** — abrir los dos listados de cierres **sin ningún filtro ni búsqueda** y con
    búsqueda puesta: ninguno de los dos casos puede tirar `InvalidOperationException`.
12. **Regresión `PAT-016`** — los 6 listados que ya tenían búsqueda global (Ventas, Clientes,
    Productos, Caja, Gastos, Entregas) tienen que seguir funcionando igual, con especial atención a
    Ventas, cuyo filtro y buscador por fecha cambiaron de criterio.

#### Checklist de salida para merge

- [x] Build de la solución en 0 errores, sin advertencias nuevas.
- [x] Sin migración EF (verificado con `has-pending-model-changes`).
- [x] Traducción a SQL verificada para las consultas nuevas (`ToQueryString`).
- [x] `MH-001` revisado en todo el código nuevo: cero `IN`/`.Contains()`/`Any()` sobre colección local.
- [x] `LP-002`: barrido completo de la convención de fechas, con tabla de cierre de las 15 propiedades.
- [x] `LP-003`/`D5`: el único `<input type="number">` nuevo no lleva `value` server-side.
- [x] `PAT-016` aplicado con el mismo criterio que los 6 listados existentes.
- [x] Un solo commit (`00f7dd4`) en `entrega-1-migracion`, sin tocar producción ni el fixture de QA.
- [ ] **Re-verificación de QA de los 7 defectos** — pendiente, la declara QA en contexto nuevo.
- [ ] **Deploy a producción** — sigue bloqueado hasta el GO de QA; lo aprueba Joaquín aparte.

#### Partes de defecto aplicados en esta corrida

Los 7, **"aplicado, pendiente de re-verificación"** — el cierre lo declara QA, nunca el Implementador:

| id | sev | Archivos principales |
|---|---|---|
| `LP-009` | major | `ICajaMovimientoService`, `CajaMovimientoService`, `VentaWorkflowService`, `GastoService`, `CuentaCorrienteClienteService` |
| `LP-010` | major | `Venta`, `VentaWorkflowService`, `AjusteStockService`, `EntregaService`, `Views/Users/*` |
| `LP-007` | minor | `VentasController`, `Views/Ventas/Editar.cshtml` |
| `LP-008` | minor | `ClasificacionAbcAutomaticaService`, `DashboardService` |
| `LP-006` | minor | `wwwroot/js/site.js` + 8 vistas de listado |
| `LP-011` | minor | `ArgentinaTime`, `CajaController`, `CajaMovimientoService` |
| `LP-012` | minor | `CajaMovimientoService`, `CajaController`, `Views/Caja/Cierres.cshtml`, `Views/Caja/Mensual.cshtml` |

### Sprint 0 — gate de precio por rol en Ventas (2026-10-05, rama `entrega-1-migracion`)

**Defecto corregido.** Cualquier usuario con la política `RequireVentas` (incluido el rol `Vendedor`) podía vender a cualquier precio: `VentasController.GuardarBorrador` tomaba `Items[].PrecioUnitario`, `Items[].Descuento` y `Items[].Recargo` del formulario y `VentaWorkflowService.GuardarBorradorAsync` los persistía sin ningún control de rol. Un vendedor podía postear `PrecioUnitario = 1` y confirmar: descontaba stock y posteaba Caja y cuenta corriente al precio que eligió. Estaba abierto en producción.

**Precedente reutilizado.** `marihogar` (`C:/Sistemas/marihogar`, ya en producción), `VentaService.ConfirmarAsync` (~407-465) y `EditarAsync` (~738-773), identificado como CR-22. Se copió el criterio: un booleano `esAdministrador` resuelto **solo** en el Controller con `User.IsInRole`, pasado al Service como dato explícito (el Service no consulta Identity), y que es la **única** puerta que habilita leer del payload los campos de precio. Lo que **no** se trajo de marihogar: la cascada `(1-d/100)*(1+r/100)` (acá la fórmula comercial correcta es `(1 - d/100 + r/100)` sobre precio de lista, corregida el 2026-09-03) y su manejo de subtotal (el de La Platense, con el subtotal c/IVA editable que despeja el precio unitario hacia atrás, es mejor y se queda).

**Qué hace el gate.**

| Rol | Precio unitario | Descuento / Recargo | Subtotal c/IVA editable |
|---|---|---|---|
| `Administrador`, `SuperUsuario` | override desde el formulario (como hasta hoy) | override, validados en 0..100 | sí (entra por `PrecioUnitario`) |
| `Vendedor` y cualquier otro rol/caller | resuelto server-side desde el `Producto` | forzados a 0 | no |

Para un vendedor los tres campos del payload **se descartan en silencio**, no con un error: no es un error del usuario, la UI simplemente no se lo deja editar. Corolario deliberado: un descuento fuera de rango (>100%) posteado por un vendedor **no** devuelve el mensaje de validación, se ignora; para un administrador sigue rechazando.

**Qué precio es "el del producto".** `VentaWorkflowService.PrecioDeVentaVigente(producto)`: `PrecioOferta` si la oferta está vigente hoy (`Producto.EsOfertaVigente(ArgentinaTime.Hoy)`, día de negocio argentino) **y** es `> 0`; si no, `PrecioVenta`. Es exactamente la misma resolución que ya hacía la pantalla al agregar un ítem (`producto.precioOferta || producto.precioVenta` en `Views/Ventas/Editar.cshtml`, sobre el `PrecioOferta` que `ProductoService.BuscarParaVentaAsync` y `CodigoBarrasLookupService.BuscarPorCodigoAsync` ya filtran por vigencia), de modo que el vendedor termina con el precio que la UI le mostró y no con otro. El `> 0` no es decorativo: replica el `||` de JavaScript, que con una oferta cargada en 0 cae igual a `PrecioVenta` — sin esa condición el servidor cobraría 0 donde la pantalla mostró el precio de lista. **Los dos caminos de la UI (buscador Select2 y lector de código de barras) usan la misma resolución, así que no hubo que elegir ninguno a dedo.** Quedó anotado en los dos lados que si se cambia una hay que cambiar la otra.

**Barrido `LP-002` — puntos de entrada del precio relevados.** Cuatro pasadas, no solo el grep obvio:

1. **Puntos de entrada del precio (grep de `PrecioUnitario` sobre `Application/`, `Domain/`, `Infrastructure/`, `Web/`).** `GuardarBorradorAsync` es el **único** método que escribe `ItemVenta` y por lo tanto el único punto de entrada del precio. `ConfirmarAsync`, `FacturarAsync` y `ConfirmarYFacturarAsync` trabajan sobre lo ya persistido y nunca leen el payload; `Details.cshtml` es solo lectura. El subtotal c/IVA editable **no tiene atributo `name`**: no se postea, la UI lo despeja sobre `PrecioUnitario` client-side, así que el gate de `PrecioUnitario` lo cubre por elevación y no hacía falta un segundo control.
2. **Hermanos semánticos del mismo payload.** `Items[].PorcentajeIVA` sigue llegando del cliente para los dos roles → **hueco hermano, deuda abierta** (ver abajo). `Pagos[].PorcentajeRecargoAplicado` ya se resolvía server-side vía `IRecargoCuotasService` (precedente del mismo patrón, dentro del mismo método). `Pagos[].Monto` se dejó como está: es lo que el cliente pagó, no un precio, y `ConfirmarAsync` valida que los pagos cubran el total salvo que haya una línea de cuenta corriente. `ClientesController.RegistrarCobro` queda en `RequireVentas` a propósito (decisión previa documentada en ese archivo) y `RegistrarAjuste` ya era `RequireAdministracion`.
3. **Comentarios y XML-doc (el fallo de `LP-008`).** Encontrado y corregido un comentario prescriptivo **falso** preexistente: `ItemVenta` declaraba la fórmula en **cascada** `Cantidad*PrecioUnitario*(1-Descuento/100)*(1+Recargo/100)` en dos lugares (encabezado de clase y doc de `Subtotal`), cuando la fórmula real desde el 2026-09-03 es `(1 - Descuento/100 + Recargo/100)`. Era una regla de negocio falsa viviendo en el repo, exactamente el patrón de `LP-008`. Actualizados además los docs de `ItemVentaInputDto`, `ItemVentaDto.SubtotalConIva`, `ItemVentaViewModel.SubtotalConIva` e `IVentaWorkflowService.GuardarBorradorAsync` para que digan el nuevo criterio de rol.
4. **La mitad simétrica.** El otro lado del gate es la **reapertura** de un borrador: si un administrador dejó un override de precio y después un `Vendedor` re-guarda ese mismo borrador, el precio vuelve al del producto y el descuento/recargo a 0 — el override se pierde. Es la consecuencia inevitable de copiar el criterio de marihogar ("para un no-administrador el precio SIEMPRE se recalcula") y se eligió a propósito por sobre la alternativa de conservar el valor persistido, que sería un agujero (un vendedor podría fijar un precio y después mantenerlo). Está verificado por ejecución y anotado como riesgo operativo.
5. **Vistas y JS.** `Views/Ventas/Editar.cshtml`: precio, descuento, recargo y subtotal van en `readonly` cuando el usuario no es administrador, en las filas que renderiza Razor **y** en las que arma el JS (`agregarFilaItem`), más el texto de ayuda reemplazado por uno que explica que el precio lo toma el sistema. Se usó `readonly` y **no** `disabled` a propósito: un input `disabled` no se postea y rompe los índices contiguos `0..N-1` que exige el model binder de `List<T>`. La UI es cortesía — el control que vale es el del servidor.

**Reglas del catálogo aplicadas.**
- `LP-002`: las 5 pasadas de arriba.
- `MH-001`: la única colección local que llega al SQL de este método es `productoIds` (`List<int>`), que la regla declara explícitamente segura (el problema es específico de colecciones de `string`). No se introdujo ningún `Contains`/`Any` nuevo.
- `LP-003`: no se agregó ningún `value` de input nuevo; los existentes ya usaban el helper `num()` con `InvariantCulture` y se mantuvieron intactos. El atributo agregado es `readonly`, que no transporta decimales.

**Archivos y capas modificadas.**

| Capa | Archivo | Motivo |
|---|---|---|
| Domain | `Domain/Entities/ItemVenta.cs` | Solo documentación: corrección del comentario prescriptivo falso de la fórmula + nota del gate. |
| Application | `Application/DTOs/VentaDtos.cs` | `GuardarVentaBorradorDto.EsAdministrador` (`init`) + XML-doc del gate en los campos de precio. |
| Application | `Application/Interfaces/IVentaWorkflowService.cs` | Contrato: `GuardarBorradorAsync` declara que es el único punto de entrada del precio y qué hace el gate. |
| Infrastructure | `Infrastructure/Services/VentaWorkflowService.cs` | El gate propiamente dicho dentro del loop de ítems + helper `PrecioDeVentaVigente`. |
| Web | `Web/Controllers/VentasController.cs` | `EsAdministrador()` con `User.IsInRole` y su paso al DTO. |
| Web | `Web/Models/VentaViewModels.cs` | Solo documentación del subtotal restringido. |
| Web | `Web/Views/Ventas/Editar.cshtml` | `readonly` por rol en Razor y en el JS, texto de ayuda por rol. |

**Migración EF: ninguna.** No hay cambio de modelo — `dotnet ef migrations has-pending-model-changes` responde *"No changes have been made to the model since the last migration"*. El gate no recalcula nada histórico: las ventas ya existentes (Confirmada/Facturada) no son editables y ningún camino las toca.

**Evidencia ejecutada (sin navegador, según la regla del rol).**
- `dotnet build FerreteriaLaPlatense.slnx`: **correcto, 0 errores**, 9 advertencias, todas preexistentes (2 `NU1902` de MailKit/MimeKit por proyecto y `CS0114` de `HomeController.StatusCode`).
- Las vistas Razor **sí** compilan en el build: comprobado metiendo a propósito un símbolo inexistente en `Editar.cshtml` → `error CS0103 ... Editar.cshtml(749,2)`; revertido y recompilado limpio.
- El render del atributo booleano `readonly="@(!esAdministrador)"` se verificó **ejecutando** `RazorPageBase.BeginWriteAttribute/WriteAttributeValue/EndWriteAttribute` (las tres llamadas que emite `Editar_cshtml.g.cs`, inspeccionado con `EmitCompilerGeneratedFiles`): con `true` emite `readonly="readonly"` y con `false` **omite el atributo entero**. Importa porque un `readonly=""` sería verdadero en HTML.
- `VentaWorkflowService.GuardarBorradorAsync` ejercitado **directamente contra `laplatense_dev`** con los dos roles, dentro de una transacción revertida al final (0 filas sobrevivientes, base en su línea base). 15 checks, todos OK: precio manipulado a $1 → se guardó `PrecioVenta` del producto; descuento 90% y recargo 50% → 0 y 0; producto con oferta vigente → cobró `PrecioOferta`; administrador → override de 1234,56 con 10%/5% respetado y subtotal por la fórmula no-cascada; 10%+10% devuelve el precio original; descuento >100% sigue rechazado para administrador y se ignora en silencio para vendedor; y la simétrica (vendedor que re-guarda pisa el override del administrador) confirmada.

**Deuda abierta que deja esta ronda.**
- **`Items[].PorcentajeIVA` sigue llegando del cliente para cualquier rol.** Es el hermano del hueco que se acaba de cerrar y el único que queda: un vendedor que postea `PorcentajeIVA = 0` baja el total de la venta ~21% sin tocar el precio unitario, porque `RecalcularTotales` suma `Subtotal * PorcentajeIVA / 100`. Se dejó **deliberadamente sin tocar** porque el brief de esta ronda lo excluyó de forma explícita ("el IVA por línea no se toca") y el alcance era un solo defecto. **Es una decisión de Joaquín**, no un olvido: si el IVA por línea es un dato del producto y no una decisión del vendedor, la corrección es idéntica a la de esta ronda (resolverlo desde `Producto.PorcentajeIVA` cuando el usuario no es administrador) y son tres líneas. Si en cambio el vendedor tiene que poder elegir la alícuota, hay que decir por qué.
- Un `PrecioUnitario` **negativo** posteado por un administrador no se rechaza en el Service (sí lo limita el `min="0"` del input y el `[Range]` del ViewModel, pero `GuardarBorrador` no chequea `ModelState.IsValid`). Preexistente, no se tocó para no ampliar alcance; marihogar sí lo valida (`PrecioUnitario <= 0`).
- Un borrador con override de administrador re-guardado por un vendedor pierde el override (ver "mitad simétrica"). Si eso molesta operativamente, la salida no es relajar el gate sino que el borrador con override no sea editable por un vendedor.

### Fundación del ledger de caja + anulación de venta confirmada (2026-10-05, rama `entrega-1-migracion`)

Commit local **`59dd715`**. **No pusheado y no deployado** — pedido explícito de Joaquín ("no publicar, dejar el desarrollo listo"). Nada corrió contra producción: la migración se aplicó únicamente a `laplatense_dev`.

Es el prerrequisito de los pagos a proveedores (Entrega 3) y del ciclo de cobranza de Ventas, y cierra el gap más urgente del sistema: **no existía ninguna anulación**.

#### Resultado del escaneo de reutilización (obligatorio antes de implementar)

Encontrado en el **paso 1** del escaneo (`cat_resumen.txt`), sin necesidad de grep dirigido:

- **`PAT-020`** — "Cancelación de comprobante con pagos: ledger inmutable + reversión acotada a lo posteado" (origen `marihogar`, CR-64/CR-65, bug real del cliente sobre la Venta #694 en producción). Entrada leída completa; los dos `archivos_referencia` ya tenían `pendiente_verificar: false` y **las dos rutas se confirmaron reales**. Se copió de `MariHogar.Infrastructure/Services/VentaService.cs` (`CancelarAsync`, líneas ~607-694) y de `EgresoPagoProveedorService.ObtenerNetoPosteadoAsync` (líneas 59-83).
- **`PAT-003`** / **`PAT-023`** revisados y descartados para esta ronda: el primero es el alta del pago dividido (ya implementado acá), el segundo es la edición de un pago posteado (no entra en el alcance).
- **`MH-034` no tiene antecedente que copiar y se declaró así**: se verificó en el repo de `marihogar` que su `MovimientoCCLocal` **no** tiene medio de pago ni id de cuenta (el medio vive en el texto libre de `Descripcion`), tal como ya había registrado el orquestador en `trazabilidad.md`. El discriminador se construyó nuevo.

Lo que se trajo tal cual de marihogar: el par motivo+fecha de anulación, el contramovimiento de stock, la reversión acotada a lo realmente posteado, el guard de Entrega asociada y el mecanismo `EsReversion` + neto vivo. Lo que se adaptó está documentado en el XML-doc de `AnularAsync` (tres divergencias: cantidades decimales, reversión por línea de pago en vez de agregada, y ausencia del estado "pago no posteado").

#### Parte 1 — `CajaMovimiento`: las 4 columnas que faltaban

| Columna | Regla | Por qué |
|---|---|---|
| `EsReversion` (bool) | `MH-020` | `GastoService.AnularAsync` simulaba la reversión posteando un `Ingreso` sobre el mismo `OrigenTipo`/`OrigenId`: **un gasto anulado era indistinguible de un ingreso real** para la grilla, el arqueo y cualquier consulta. |
| `PagoVentaId` (int?) | `MH-027` | `OrigenTipo`+`OrigenId` apuntan a la **venta**, no al pago. Una venta con dos pagos postea dos filas con la misma clave, y con dos importes iguales (pago mixto de $5.000 + $5.000, nada exótico) revertir una obligaba a adivinar por monto. Es el defecto que marihogar ya sufrió en producción. |
| `UsuarioId` (string?) | — | Quién provocó el movimiento. Sin navegación a Identity, mismo criterio explícito que `AjusteStock.UsuarioId` y `Venta.VendedorId`. |
| `MedioPago` (`MedioPagoCaja?`) | `MH-034` | Una sola caja indiferenciada para efectivo, transferencia y tarjeta: su flujo no se podía contrastar contra **ningún** extracto. |

**El mecanismo del neto vivo** (`CajaMovimientoService.ObtenerNetoPosteadoAsync`) es la pieza central: el neto de un origen es `Σ(movimientos del tipo original, no-reversión) − Σ(movimientos del tipo opuesto que sí son reversión)`, y **toda reversión se postea por ese neto, nunca por el monto del documento**. Con eso, revertir dos veces el mismo dinero es imposible *por construcción* y no por un flag de estado que haya que acordarse de chequear en cada vía nueva — que es exactamente cómo nació `MH-020` en marihogar. `ObtenerNetoPosteadoPorPagoVentaAsync` es la variante acotada por `PagoVentaId`, y devuelve `Identificable` como dato **aparte** del neto: `false` significa "no hay ninguna fila con ese `PagoVentaId`", y el caller tiene que distinguir "pago a cuenta corriente que nunca posteó" de "fila histórica sin desambiguar" y, en el segundo caso, **bloquear**.

`GastoService.AnularAsync` quedó migrado a este mecanismo. Efecto medible: los dos gastos ya anulados de `laplatense_dev` tienen hoy neto vivo **0,00**, así que re-anularlos no postearía nada.

**`MedioPagoCaja` es un enum nuevo y propio** (`Efectivo`, `TarjetaDebito`, `TarjetaCredito`, `Transferencia`, `Cheque`, `Deposito`, `Otro`), unión de `MedioPago` (venta) y `FormaPagoGasto`. No se extendió ninguno de los dos existentes a propósito: agregarle `Transferencia`/`Cheque` a `MedioPago` habría metido opciones sin sentido en el combo de pago de la Venta, y las tarjetas en el de Gasto — justo la propagación que `LP-002` obliga a relevar. La traducción vive en **un** helper (`MedioPagoCajaMapper`) con `switch` **exhaustivos sin `_ =>`**: si mañana se agrega un valor a cualquiera de los dos enums de origen, avisa el compilador (CS8509) en vez de entrar a la caja mal clasificado y en silencio. Es el barrido `LP-002` delegado al compilador.

**Decisión de diseño sobre `MH-034`, declarada:** el medio es un **atributo del movimiento para filtrar y conciliar**, no una caja con saldo propio. El saldo de caja sigue siendo **uno y agrupado**, y el arqueo por medio es un desglose del mismo total. Es el corolario que marihogar aprendió con datos: si se parte en cajas con saldo independiente, cada traspaso entre cuentas propias que nadie carga —y este negocio no los carga— descuadra dos cajas a la vez en vez de ninguna. El rótulo de la pantalla lo dice explícitamente ("Desglose por medio de pago · Para conciliar contra el extracto de cada cuenta") y la fila de Total repite el saldo agrupado.

`CuentaCorriente` **no** figura en el enum: ese pago no postea en caja (es deuda diferida, va al ledger de `MovimientoCCCliente`). El mapper devuelve `null` para ese valor, y un `null` devuelto ahí significa que el caller está por postear un movimiento que no corresponde postear.

#### Parte 2 — Anulación de una venta `Confirmada`

Hasta este cambio `EstadoVenta.Anulada` estaba en el enum y **ningún código la disparaba**: sus únicos usos eran un filtro de listado y un badge. Un error de carga en una venta confirmada era irreparable — el stock salió, la caja y la cuenta corriente se movieron.

`VentaWorkflowService.AnularAsync(ventaId, motivo, usuarioId, esAdministrador)`, todo en una transacción:

1. **Stock**: `item.Producto.Stock += item.Cantidad`, el contramovimiento exacto de lo que restó `ConfirmarAsync`. La cantidad está en `ItemVenta.UnidadVenta` (snapshot), que es la unidad en que salió — **no se convierte nada**: aplicar una conversión contra la `UnidadVenta` *actual* del producto devolvería una cantidad distinta de la que se descontó. El caso en que la unidad del producto cambió *después* de la venta se detecta y **se avisa en el mensaje** pidiendo un conteo, pero no bloquea ni corrige: la reversión sigue siendo la correcta y lo que ya está inconsistente es la columna `Stock`.
2. **Caja**: un contramovimiento `Egreso` **por línea de pago**, por el neto vivo de cada `PagoVentaId`. marihogar postea uno solo y agregado; acá se hace pago por pago porque es la única forma de saber que se deshace exactamente lo que se posteó (`MH-027`) y de dejar el desglose por medio coherente — un contramovimiento agregado no tiene medio que declarar.
3. **Cuenta corriente**: `ICuentaCorrienteClienteService.RevertirDebitoVentaAsync` postea un `Credito` con el origen nuevo `AnulacionVenta` por el **débito vivo** de esa venta (`Σ Debito VentaFiado − Σ Credito AnulacionVenta`), nunca por el total nominal. Los cobros que el cliente ya hizo **no** se tocan ni se descuentan: son hechos económicos propios. Si ya había pagado parte del fiado de una venta que se anula, le queda saldo a favor, que es lo correcto — pagó algo que el negocio ya no le reclama.
4. **Estado**: `Anulada` + `MotivoAnulacion` + `FechaAnulacion` (instante UTC) + `AnuladaPorUsuarioId`.

**Guardas, en orden** (todas server-side, ninguna depende de que la pantalla muestre el botón):

| Guarda | Criterio | Nota |
|---|---|---|
| Motivo no vacío | decisión del cliente | También validado en el cliente, solo para evitar el round-trip |
| Ya `Anulada` → rechazo explícito | 5 | La protección real contra la doble reversión no es este `if`, es el neto vivo (que la segunda vez ya es 0) |
| `Borrador` → usar "Cancelar" | — | No movió nada; no hay nada que anular |
| `Facturada` → **rechazo con mensaje** | alcance | Necesita nota de crédito AFIP (Entrega 5) |
| Administrador **o** el vendedor que la creó | 7 | `esAdministrador` lo resuelve el Controller con `User.IsInRole`, nunca un campo posteado — mismo criterio que el gate de precio |
| Sin `Entrega` asociada | 6 | `Entrega` hereda `SoftDestroyable`: una entrega dada de baja no bloquea |
| Período de la venta **y** de hoy abiertos | 8 / `LP-009` | Dos consultas separadas para que el mensaje diga **cuál** está cerrado |
| Todos los pagos identificables | `MH-027` | Se releva **antes** de abrir la transacción: si uno falla, se bloquea **completa** |

**Por qué se validan dos períodos y no uno.** El criterio 8 pide el de la venta: si ese arqueo ya se cerró y firmó, anular la venta dejaría el ledger de ese período mostrando el ingreso de una venta que el Dashboard y la ABC ya no cuentan — dos lecturas del mismo día que no coinciden y que nadie notaría hasta compararlas. Y además hace falta el de **hoy**, porque el contramovimiento se fecha hoy (`MH-028`/`MH-021`: una anulación es un hecho real de hoy, no la corrección de un dato histórico; retrofecharla modificaría un arqueo pasado).

**Por qué el relevamiento de identificabilidad va antes de la transacción.** Revertir "los que se pueden" dejaría la venta anulada con la caja a medio revertir, que es **peor** que no anularla: el stock volvió, el estado cambió, y falta plata que nadie va a ir a buscar. Se bloquea completa, con un mensaje que nombra los pagos problemáticos y manda a soporte. No se infiere por monto: esa es exactamente la adivinanza que produjo `MH-027`.

**Diseño preparado para la NC de AFIP (Entrega 5).** El guard de `Facturada` es el punto exacto donde se enchufa. El orden importa y está documentado en el código: la NC tiene que emitirse **antes** de revertir plata y stock, porque si AFIP la rechaza la reversión no se puede aplicar. El orden inverso (el de `ConfirmarYFacturar`) dejaría la caja revertida con una factura viva. Todo lo que hay debajo de ese guard —guardas de período, contramovimiento de stock, reversión por neto vivo y reversión de CC— es reutilizable tal cual; lo único que se le agrega adelante es la emisión.

#### Barrido `LP-002` — resultado completo

**`OrigenTipo` del ledger de caja (4 lectores + 2 en vista).** Relevados todos: `CajaMovimientoService.ListarMovimientosAsync` (filtro), su `switch` de ordenamiento, el `WHERE` final del buscador global, y en `Views/Caja/Index.cshtml` el combo `#fOrigenTipo` y el mapeo del ajax. **Ninguno necesitó cambio**: la reversión de una venta anulada comparte `OrigenTipo="Venta"`/`OrigenId` con el movimiento original (es lo que `PAT-020` exige), así que **no se agregó ningún origen nuevo** y el combo queda completo. Los 4 literales (`"Venta"`, `"Gasto"`, `"Ajuste"`, `"CobroCC"`) pasaron a constantes (`CajaMovimientoService.OrigenVenta`/`OrigenGasto`/`OrigenAjuste`, y el ya existente `CuentaCorrienteClienteService.OrigenCajaCobroCC`): un typo en una sola de las dos puntas dejaba el guard de `ObtenerNetoPosteadoPorPagoVentaAsync` sin efecto y **no fallaba nada**.

**`EstadoVenta` (criterio 4 — verificado, no asumido).** Los lectores que agregan plata o rotación son `DashboardService:62` (ventas de hoy), `DashboardService:111` (top productos del mes) y `ClasificacionAbcAutomaticaService:86` (rotación ABC). Los tres filtran por **whitelist** (`Estado == Confirmada || Estado == Facturada`), que es la forma robusta: `Anulada` queda afuera sola, sin tocar nada. Los arqueos no filtran por estado y **no deben**: se calculan sobre el ledger, donde el contramovimiento neutraliza el ingreso. `EntregaService:249/309` ya impedía crear una entrega sobre una venta que no esté `Confirmada`/`Facturada`, que es la dirección complementaria del criterio 6. `Views/Ventas/Index.cshtml` ya tenía la opción "Anulada" en el combo de estado, y `ListarAsync` ya ocultaba las anuladas salvo filtro explícito (pedido de Joaquín del 2026-09-03).

**`OrigenMovimientoCC` (origen nuevo: `AnulacionVenta = 4`).** Acá sí hubo propagación. Lectores: `CuentaCorrienteClienteService.ListarMovimientosAsync` (filtro, genérico por enum, sin cambio), `ClientesController:177` (parseo, sin cambio) y **dos** en `Views/Clientes/CuentaCorriente.cshtml` que sí había que tocar: el combo `#fOrigen` y el mapa `etiquetasOrigen`. Son dos y no uno — si el combo queda viejo el movimiento no se puede aislar en la grilla, y si el mapa queda viejo la celda muestra el nombre crudo del enum. El valor va **al final y numerado explícito**, por la misma razón que `Confirmada=4`.

**`MedioPago` (dimensión nueva).** Toda columna visible tiene su filtro: se agregó el combo `#fMedioPago` (con la opción "Sin declarar", que es el `NULL`), la columna "Medio" en la grilla con su caso en el `switch` de ordenamiento (`MH-015`), el término en el buscador global —comparado contra la **etiqueta** que el usuario ve, no contra el nombre del enum, así "tarjeta" encuentra débito y crédito y "deposito" sin tilde también—, el campo opcional en el alta manual, y el desglose en los arqueos diario y mensual.

El `NULL` del medio **necesitó un parámetro booleano propio** (`soloSinMedioPago`) y no un valor centinela del enum: un `<option>` no puede postear `null` y `""` ya significa "todos". Meterlo como valor del enum habría sido ensuciar el dominio con un caso que solo existe en la UI. El literal que viaja vive en `CajaController.ValorFiltroSinMedioPago` para que la vista y el parseo no se desincronicen por un typo — si se desincronizan, **el filtro deja de filtrar en silencio**.

#### Migración EF: `20261005221747_LedgerCaja_Identidad_MedioPago_AnulacionVenta`

**Aditiva**: 7 columnas nullable (o con default) y 2 índices. Ninguna columna existente cambia de tipo ni de nullabilidad, así que el código viejo seguiría funcionando contra este esquema. **Aplicada solo a `laplatense_dev`.**

- `CajaMovimientos`: `EsReversion` (`tinyint(1)`, default 0), `PagoVentaId` (`int?` + índice), `UsuarioId` (`varchar(450)`), `MedioPago` (`int?` + índice).
- `Ventas`: `MotivoAnulacion` (`varchar(500)`), `FechaAnulacion` (`datetime(6)`), `AnuladaPorUsuarioId` (`varchar(450)`).

**Trae backfill en 5 pasos, y no es opcional.** Sin él, cada fila anterior queda con `MedioPago NULL` (invisible para la conciliación) y —mucho peor— con `PagoVentaId NULL`, que es lo que hace que `AnularAsync` **bloquee la anulación de las ventas ya confirmadas**. Hacerlo después, con miles de pagos encima, sería una reconstrucción sobre texto libre; hacerlo ahora es un `UPDATE` de unas pocas filas.

1. `EsReversion = 1` donde `OrigenTipo='Gasto' AND Tipo=Ingreso`. **No es heurística**: `GastoService` postea exactamente dos cosas sobre ese origen, un `Egreso` al crear y un `Ingreso` al anular, y no hay otra vía.
2. `MedioPago` de los gastos, derivado de `Gasto.FormaPago` (dato duro, no texto).
3. `MedioPago` de ventas y cobros de CC, derivado del sufijo de la `Descripcion`. Es el único lugar donde el dato quedó, y el sufijo lo genera el `ToString()` del enum, así que el conjunto de literales es cerrado y conocido — no es parseo de texto tipeado por un humano. Que haya que leer texto para recuperarlo es, literalmente, la razón por la que la columna tiene que existir.
4. `PagoVentaId`, **solo cuando la venta tiene exactamente un pago de ese medio** (`HAVING n = 1`, el corazón del paso). Si tiene dos del mismo medio queda `NULL` a propósito.
5. `UsuarioId` desde `Venta.VendedorId` y `MovimientoCCCliente.UsuarioId`. Los gastos quedan en `NULL` porque `Gasto` no guarda usuario y nunca lo guardó: es el dato honesto.

El mapeo `FormaPagoGasto`/`MedioPago` → `MedioPagoCaja` queda escrito dos veces (el `CASE` del SQL y el `switch` del mapper) porque SQL no puede llamar al helper. Si se agrega un valor, el que avisa es el `switch` exhaustivo en C#, no este SQL — que ya corrió y no vuelve a correr.

#### Archivos y capas modificadas

- **Domain**: `Enums/MedioPagoCaja.cs` (nuevo), `Enums/OrigenMovimientoCC.cs` (+`AnulacionVenta`), `Enums/EstadoVenta.cs` (XML-doc), `Entities/CajaMovimiento.cs` (4 columnas), `Entities/Venta.cs` (3 columnas), `Entities/MovimientoCCCliente.cs` (XML-doc de `VentaId`).
- **Application**: `Helpers/MedioPagoCajaMapper.cs` (nuevo), `DTOs/CajaDtos.cs` (`CajaTotalPorMedioDto` nuevo + `MedioPago`/`EsReversion` en la fila del listado + `TotalesPorMedio` en los dos resúmenes), `DTOs/VentaDtos.cs`, `Interfaces/ICajaMovimientoService.cs`, `Interfaces/ICuentaCorrienteClienteService.cs`, `Interfaces/IVentaWorkflowService.cs`.
- **Infrastructure**: `Data/AppDbContext.cs` (config + 2 índices), `Services/CajaMovimientoService.cs` (constantes de origen, filtro y búsqueda por medio, `ObtenerNetoPosteadoAsync`, `ObtenerNetoPosteadoPorPagoVentaAsync`, `NetoVivo`, `ObtenerTotalesPorMedioRangoUtcAsync`), `Services/VentaWorkflowService.cs` (`AnularAsync` + identidad en el posteo de `ConfirmarAsync`), `Services/GastoService.cs` (reversión por neto vivo + medio), `Services/CuentaCorrienteClienteService.cs` (`RevertirDebitoVentaAsync` + medio en el cobro), `Migrations/20261005221747_*`.
- **Web**: `Controllers/CajaController.cs`, `Controllers/VentasController.cs` (acción `Anular`), `Models/CajaViewModels.cs`, `Models/VentaViewModels.cs`, `Views/Caja/_ArqueoPorMedio.cshtml` (nuevo, compartido por Index y Mensual), `Views/Caja/Index.cshtml`, `Views/Caja/Mensual.cshtml`, `Views/Caja/MovimientoManual.cshtml`, `Views/Clientes/CuentaCorriente.cshtml`, `Views/Ventas/Details.cshtml`.

Sin cambios en DI: no hay servicios nuevos, solo métodos nuevos en contratos ya registrados.

#### Evidencia

**Build:** `dotnet build FerreteriaLaPlatense.slnx` → **0 errores**. 9 advertencias, **todas preexistentes** (4× `NU1902` de MailKit/MimeKit, `CS0114` en `HomeController`). Rebuild forzado de `FerreteriaLaPlatense.Web` con `--no-incremental` para compilar de verdad las 5 vistas Razor tocadas: **0 errores**.

**JS embebido de las vistas** (el compilador de Razor no lo chequea): extraído y pasado por `node --check` con las expresiones Razor reemplazadas por placeholders. `Ventas/Details.cshtml`, `Caja/Index.cshtml` y `Clientes/CuentaCorriente.cshtml`: **los tres parsean**.

**`MH-001`** — barrido ampliado (`grep -rnE "\.(Contains|Any)\("` sobre `Infrastructure/Services`, `Web/Controllers` y `Application`, quedándose con las colecciones locales de `string`): **el código nuevo no introduce ni un caso**. El filtro por medio del buscador global se resuelve con **una consulta por medio y el valor como parámetro escalar**, explícitamente para no armar la forma prohibida. Los casos preexistentes ya tenían el fix canónico aplicado (`AjusteStockService:156`, `CajaMovimientoService:556/754`, `EntregaService:99/237`, y `EntregaService:207`, que es íntegramente en memoria).

**Ejecución real contra `laplatense_dev`** (la regla pide ejecutar, no inspeccionar): sonda desechable en el scratchpad —**fuera del repo**, borrada después— que referenció `Infrastructure` y corrió las consultas nuevas. Las 7 se tradujeron y ejecutaron, incluido el `GroupBy` con **enum nullable en la clave** del arqueo por medio, que era el shape de mayor riesgo. Resultado medido sobre las 9 filas del ledger:

- **Backfill correcto**: 2 reversiones marcadas ($91.500,50, los dos gastos anulados), medio derivado en 8 de 9 filas (la novena es el ajuste manual, que legítimamente no tiene medio).
- **Identidad `MH-027` completa**: las 3 filas de venta quedaron con su `PagoVentaId` exacto, cada una apuntando a un pago de la **misma venta** y del **mismo medio** (venta #12 → pagos #7 Efectivo $200 y #8 CréditoCuotas $300; venta #13 → pago #10 $5.163,80). **Ninguna fila de venta quedó sin `PagoVentaId`**, así que en dev no hay ninguna venta bloqueada.
- **Netos vivos**: gastos #1 y #2 en **0,00** (ya anulados — re-anularlos no postearía nada, que es el fix `MH-020` funcionando), gasto #3 en 2.500,75, ventas #12 en 500,00 y #13 en 5.163,80.
- **Desglose por medio**: Efectivo $96.864,30 / $94.001,25, Tarjeta de crédito $300,00 / $0, Sin declarar $250,75 / $0.
- Guard de entrega: ventas #1, #3 y #8 tienen entrega (y son `Facturada`, así que las rechaza el guard anterior); #12 y #13 no.

#### Guía de verificación manual (a ejecutar por el cliente/QA, no por el Implementador)

Contra `laplatense_dev`, con la migración ya aplicada. Las ventas **#12** y **#13** están `Confirmada` y son las anulables.

1. **Caja → desglose.** `/Caja` muestra la tarjeta "Desglose por medio de pago" con una fila por medio, la de "Sin declarar" con el ícono de ayuda, y el Total coincidiendo con las tarjetas de arriba. Ídem `/Caja/Mensual`.
2. **Filtro y columna de medio.** Filtrar por "Efectivo" y por "Sin declarar" (esta última debe traer solo el ajuste manual). Ordenar por la columna "Medio" clickeando el header y comprobar que **reordena de verdad** (si ordena por fecha, falta el caso en el `switch`). Buscar "tarjeta" en el buscador global: debe traer débito y crédito.
3. **Badge de reversión.** Los dos ingresos de gasto anulado tienen que mostrar el badge "Reversión" junto al origen. Buscar "reversión" en el buscador global debe traer esas filas.
4. **Doble anulación de gasto (`MH-020`).** Dar de alta un gasto, anularlo (el mensaje debe decir "Se revirtió el egreso en la caja") y verificar que el saldo del día vuelve al valor previo. El gasto queda con badge "Anulado".
5. **Anular la venta #13** (1 pago, Efectivo $5.163,80). Anotar antes el stock de sus ítems y el saldo del día. Después: estado `Anulada` con el panel rojo mostrando motivo, fecha y usuario; stock devuelto exacto; un `Egreso` de reversión por $5.163,80 en `/Caja` con badge "Reversión" y medio "Efectivo"; el Dashboard y el arqueo del día bajan en ese importe.
6. **Motivo obligatorio.** En el diálogo de anulación, confirmar con el motivo vacío → tiene que rechazarlo sin cerrar.
7. **Doble anulación de venta (criterio 5).** Reintentar sobre la #13 ya anulada → "Esta venta ya está anulada", y **ningún** movimiento nuevo en caja.
8. **Anular la venta #12** (dos pagos de **distinto** importe y distinto medio). Deben aparecer **dos** contramovimientos: uno de $200 con medio "Efectivo" y otro de $300 con medio "Tarjeta de crédito". Que el de $300 no salga como efectivo es el punto del ejercicio.
9. **Venta facturada (alcance).** Entrar a la #1, #3 o #8 (`Facturada`) → **no** debe aparecer el botón "Anular venta". Postear `/Ventas/Anular` a mano con ese id debe devolver el mensaje de nota de crédito, sin tocar nada.
10. **Permiso por rol (criterio 7).** Con un usuario `Vendedor` que no sea el vendedor de la venta: el botón no aparece, y el POST a mano debe devolver "Solo un administrador o el vendedor que registró la venta pueden anularla". Con el vendedor que sí la creó, tiene que poder.
11. **Entrega asociada (criterio 6).** Programar una entrega sobre una venta confirmada e intentar anularla → rechazo pidiendo resolver la entrega primero. Dar de baja la entrega y reintentar → ahora debe dejar.
12. **Período cerrado (criterio 8, `LP-009`).** Cerrar la caja del día de una venta confirmada e intentar anularla → rechazo nombrando **ese** día. Cerrar un mes e intentar anular una venta de ese mes → el mensaje debe hablar del **cierre mensual**, no del diario.
13. **Fiado (criterio 3).** Crear una venta con un pago a cuenta corriente, confirmarla, anotar el saldo del cliente, anularla → el saldo vuelve al valor previo con un movimiento `Credito` de origen **"Anulación de venta"**, que tiene que aparecer con ese nombre en el combo y en la celda de la grilla de la CC (si sale "AnulacionVenta" crudo, falta el mapa de etiquetas). Caso que vale la pena: cobrar **parte** del fiado antes de anular — el cliente debe quedar con **saldo a favor**, no en cero.
14. **Alta manual con medio.** `/Caja/MovimientoManual` con y sin medio elegido. Sin medio debe guardar y listarse como "Sin declarar".

#### Riesgos y supuestos

- **No deployado y no pusheado.** Producción sigue con el ledger viejo. Cuando se publique, **primero el backup** y después la migración: trae `UPDATE`s de datos, no solo DDL. Producción tiene 4 movimientos de caja, todos de Venta, y 3 ventas `Confirmada` — el backfill debería resolverles el `PagoVentaId` si cada una tiene un solo pago por medio. **Hay que verificarlo contra producción antes de publicar**, porque es lo que determina si esas 3 ventas quedan anulables o bloqueadas. Query de control: `SELECT OrigenTipo, COUNT(*), SUM(PagoVentaId IS NULL) FROM CajaMovimientos GROUP BY OrigenTipo` después de migrar.
- **El `Down` de la migración borra las columnas**, y con ellas el resultado del backfill. Es irreversible en términos de datos aunque el esquema vuelva: rehacerlo requiere correr el backfill otra vez (y el paso 3, el del texto, solo funciona mientras las descripciones no se hayan tocado).
- **Supuesto sobre el día del contramovimiento**: la reversión se fecha hoy y, además, se exige que el período de la venta esté abierto. Es más estricto que marihogar, y es lo que pedía el criterio 8. El efecto práctico: una venta de un día ya cerrado **no se puede anular** y hay que resolverla con un ajuste manual de caja. Si al cliente le resulta demasiado rígido, la guarda a relajar es la del período de la venta (la de hoy es técnica y no se puede sacar). **Decisión para Joaquín.**
- **Supuesto sobre el stock y la unidad**: si la `UnidadVenta` del producto cambió después de la venta, la reversión devuelve la cantidad en la unidad vieja y el mensaje avisa pidiendo un conteo. La alternativa —convertir— devolvería una cantidad distinta de la que salió. Se eligió la reversión fiel + aviso.
- **`MedioPago` de las tarjetas no dice dónde quedó la plata.** `MH-034` lo advierte: con tarjeta de crédito el medio y la cuenta no coinciden (liquida en el banco o en la billetera según la terminal). Para gastos y compras la forma de pago **sí** alcanza. Si el cliente llega a necesitar conciliar las liquidaciones de tarjeta, hace falta una dimensión "cuenta" además del medio — **no entra en esta ronda** y queda declarado.
- **El saldo inicial sigue sin estar.** `MH-034` es explícito: ningún arreglo del flujo hace que un saldo signifique "la plata que hay" si el punto de partida es un cero inventado. Este cambio hace **conciliable el flujo** del período, que es lo que se puede conciliar con saldo agrupado; el saldo de apertura por medio es una tarea aparte, barata y de una sola vez. **Pendiente, para decidir con Joaquín.**
- **Las 3 ventas `Facturada` de dev no tienen pagos cargados.** Se notó al correr la sonda. No afecta a esta ronda (el guard de `Facturada` las rechaza antes), pero es un dato raro de la base de dev que conviene que QA tenga a mano.
- La anulación **no** notifica a nadie ni deja asiento más allá del ledger y de los 3 campos de la venta. No se pidió.

#### Pruebas mínimas requeridas para QA

Los 14 pasos de la guía de arriba, más tres controles de integridad en SQL que valen como smoke permanente del módulo:

1. **Neto vivo nunca negativo**: `SELECT OrigenTipo, OrigenId, SUM(CASE WHEN EsReversion=0 AND Tipo=1 THEN Monto ELSE 0 END) - SUM(CASE WHEN EsReversion=1 AND Tipo=2 THEN Monto ELSE 0 END) AS neto FROM CajaMovimientos GROUP BY OrigenTipo, OrigenId HAVING neto < 0` → **cero filas**. Una fila acá es dinero revertido dos veces.
2. **Identidad de los movimientos de venta**: `SELECT COUNT(*) FROM CajaMovimientos WHERE OrigenTipo='Venta' AND PagoVentaId IS NULL` → cada fila es una venta que no se va a poder anular. Y `SELECT m.Id FROM CajaMovimientos m JOIN PagosVenta p ON p.Id=m.PagoVentaId WHERE m.OrigenTipo='Venta' AND p.VentaId <> m.OrigenId` → **cero filas** (un `PagoVentaId` apuntando a otra venta sería el `MH-027` de nuevo).
3. **Cierres vs. ledger** (la query que destapó `LP-009`): comparar cada cierre guardado contra el recálculo por rango UTC del día/mes de negocio. Sigue valiendo y ahora también conviene comparar la suma del desglose por medio contra el total del período.

#### Checklist de salida para merge

- [x] Build limpio, sin advertencias nuevas.
- [x] Rebuild forzado de las vistas Razor.
- [x] JS embebido de las 3 vistas con script validado con `node --check`.
- [x] Migración aditiva, con backfill, aplicada y **verificada con datos** en `laplatense_dev`.
- [x] Barrido `LP-002` de los 4 campos tocados, con resultado escrito.
- [x] Barrido `MH-001` ampliado + ejecución real de las consultas nuevas.
- [x] `LP-003` verificado (sin inputs numéricos nuevos; barrido de comas en `value` sin hallazgos).
- [x] Enums con valores nuevos **al final** y numerados explícito.
- [x] Fechas nuevas con su semántica declarada en el XML-doc (`FechaAnulacion` = instante UTC).
- [x] Design system aplicado (`.ov-form-page`, SweetAlert2 fuera del `<form>` por `KOI-001`, filtro por cada columna visible, `ov-field-hint`).
- [x] Commit local.
- [ ] **Push y deploy: NO ejecutados a propósito.** Los decide Joaquín.
- [ ] Re-verificación de QA.
- [ ] Verificar contra **producción** que el backfill le resuelve el `PagoVentaId` a las 3 ventas `Confirmada` (ver riesgos).

### Entrega 3 — pasos 1 a 3: Proveedores, CC de proveedores y Ordenes de compra (2026-10-05, rama `entrega-1-migracion`)

**No pusheado y no deployado** — pedido explicito de Joaquin ("no publicar, dejar el desarrollo listo"). Nada corrio contra produccion: la migracion se aplico unicamente a `laplatense_dev`.

Cierra el **alta y la edicion completa de compras**, con una frontera deliberada: **nada de lo que se construyo aca toca stock, ni caja, ni cuenta corriente**. El impacto real de una compra (incrementar stock + postear el Cargo de deuda) es la RECEPCION, que es el paso 4; los pagos son el paso 5. El contrato `IOrdenCompraService` ni siquiera expone `RecibirAsync`, y `OrdenCompraService` no inyecta `IStockService`, `ICajaMovimientoService` ni `ICCProveedorService`: no se puede llamar por accidente lo que no esta inyectado.

#### Resultado del escaneo de reutilizacion (obligatorio antes de implementar)

Encontrado en el **paso 1** del escaneo (`docs/patrones/cat_resumen.txt`), sin necesidad de grep dirigido:

- **`PAT-001`** — "Ledger / Cuenta corriente". Entrada leida completa, las dos rutas confirmadas reales. Se porto `marihogar/CCProveedorService.cs` con el camino de vuelta ya recorrido en casa (`MovimientoCCCliente` + `CuentaCorrienteClienteService` de este proyecto son un port del `MovimientoCCProveedor` de vinosefue). **Se actualizo PAT-001** con tres `archivos_referencia` nuevos de la-platense y la aplicacion en `proyectos_que_lo_usan`.
- **`PAT-005`** — "Maquina de estados (workflow generico)". Aplicado: enum en Domain, transiciones validadas en el Service con conjuntos EXPLICITOS de estados (`EstadosEditables`/`EstadosCancelables`, nunca una negacion), y ViewModel que calcula las acciones disponibles por estado.
- **`PAT-008`** / **`PAT-016`** — DataTables server-side con filtro por columna visible + busqueda global multi-formato + filtros en `Session`. Aplicados a los tres listados nuevos.
- **`PAT-020`** / **`PAT-051`** — leidos y declarados como **el camino que hay que seguir en los pasos 4 y 5**, no aplicados todavia: en esta ronda cancelar no tiene nada que revertir porque el Cargo no se postea hasta recibir. El contrato de la reversion por neto vivo quedo DEFINIDO (`ObtenerNetoVivoAsync`) para que esos pasos no lo reinventen sobre el nominal.
- **`PAT-050`** revisado y descartado: el gate de precio por rol no aplica aca — todo el modulo es Administrador exclusivo, no hay un rol menor del que proteger el precio.
- **Sin antecedente, declarado y catalogado**: el modelo de unidad de la linea de compra. `marihogar/OrdenCompraItem.cs` tiene `Cantidad` como `int` y la linea no declara unidad. Se construyo nuevo y se agrego al catalogo como **`PAT-052`** ("Linea de documento que declara su unidad y CONGELA el factor de conversion").
- **Sin antecedente, declarado**: el buscador de productos por codigo de proveedor (0 hits de `CodigoProveedor` en marihogar; su buscador va solo por nombre de producto). Construido nuevo.
- **Sin antecedente, declarado**: `TipoCambio`/`Moneda`/`PorcentajeDescuentoHabitual`/`FormaPagoHabitual` en `Proveedor` (0 hits en marihogar, verificado). Desarrollo nuevo dentro del alcance del item 3.1.

#### Barrido LP-002 al ampliar `Proveedor` — las 4 pasadas, con lo que rindio cada una

El brief daba por sentado que `Proveedor` "se consume como catalogo simple en los combos del catalogo de productos". **Eso es falso y el barrido lo corrigio**: la premisa habia que verificarla, no heredarla.

**Pasada 1 — relevamiento directo.** `grep -rn "Proveedor"` sobre `*.cs`/`*.cshtml`/`*.js` (excluyendo `obj`/`bin`/`publish`/`Migrations` y los falsos positivos `MovimientoCCProveedor`/`CodigoProveedorProducto`): **`Proveedor` tenia CERO consumidores en `Web/`**. Ningun controller, ninguna vista, ningun combo. Los unicos consumidores reales eran:

- `tools/MigracionCatalogo/Program.cs:808` — `new Proveedor { Nombre = ..., Activo = true }`, inicializador de objeto. **Es el unico escritor real de la entidad** y el contrato que habia que preservar.
- `ProveedorService : CatalogoSimpleServiceBase<Proveedor>` — el unico lector, y es justamente el que se reemplazo.
- `CodigoProveedorProducto.ProveedorId` — la FK.

Consecuencia practica: la ampliacion se pudo hacer **estrictamente aditiva** (18 `AddColumn`, 3 `CreateTable`, 9 `CreateIndex`, **cero `DropColumn`/`AlterColumn`** sobre lo existente) y **`Nombre` se MANTUVO como nombre de columna** aunque marihogar lo llame `RazonSocial`: renombrarlo era una migracion destructiva sobre 85 razones sociales reales migradas del legado y habria roto el contrato de la herramienta de migracion, a cambio de nada funcional. En pantalla se rotula "Razon social".

**Pasada 2 — hermanos semanticos (fechas).** Grep reproducible, el numero sale de aca y QA lo puede recontar:

```
grep -hn "DateTime" FerreteriaLaPlatense.Domain/Entities/*.cs | grep "get; set;"
```

Da **29 propiedades `DateTime`** en Domain, de las cuales **6 son nuevas de esta ronda**, y las 6 declaran su semantica en el XML-doc (LP-009):

| Propiedad | Semantica |
|---|---|
| `Proveedor.FechaSaldoInicial` | instante UTC derivado de un DIA DE NEGOCIO elegido por el usuario (se persiste con `ArgentinaTime.InicioDiaUtc`) |
| `MovimientoCCProveedor.Fecha` | instante UTC; si se imputa a un dia anterior, las 00:00 ART de ese dia |
| `OrdenCompra.Fecha` | instante UTC derivado de dia de negocio; nunca futura, pasada SI permitida |
| `OrdenCompra.FechaConfirmacion` | instante UTC del momento de la accion |
| `OrdenCompra.FechaRecepcion` | instante UTC — **declarada, nunca escrita en esta ronda** (paso 4) |
| `OrdenCompra.FechaCancelacion` | instante UTC del momento de la accion |

**Pasada 3 — comentarios y XML-doc (el texto de la regla, no solo el codigo).** Rindio **2 hallazgos propios** que el grep de codigo no toca:

1. `AppDbContext.cs:36-38` decia *"Proveedor es una version minima... el modulo de Compras la amplia mas adelante"*. Dejo de ser cierto en esta misma ronda. **Corregido**, con la nota de por que.
2. `Views/Dashboard/Index.cshtml` decia que el nivel 2 del dashboard *"depende de Compras y Cuenta Corriente de proveedores"*. **Las dos piezas ya existen**, asi que la afirmacion quedo falsa: lo que falta de verdad es la cuenta corriente propia del negocio (Entrega 4, item 4.2). **Corregido el texto**, no el panel (construirlo no es alcance de esta ronda).

**Pasada 4 — vistas y JS.** Verificado que las columnas de fecha de los listados nuevos pasan por `window.Fmt` y que **ningun `toLocaleString` suelto formatea una fecha** (los 7 que hay son sobre importes, porcentajes y cantidades, que es la convencion del proyecto). LP-006 cubierto.

**Pasada extra — la mitad simetrica.** Rindio **1 hallazgo propio y un fix real**: las lineas de la compra viajan en inputs `hidden` que el JS arma en el submit. `EditarAsync` reemplaza el set completo, asi que un post con CERO lineas (JS que no cargo, POST armado a mano) **habria vaciado la compra en silencio, sin que nada falle**. Se agrego la guarda: un Edit sin lineas sobre una compra que SI las tiene se rechaza con mensaje. `CrearAsync` SI acepta un borrador vacio, a proposito — empezar una compra y completarla despues es el caso normal, y `ConfirmarAsync` exige al menos una linea.

**Pasada extra — `Proveedor.Activo` y su simetrico.** Se impide cargar una compra nueva a un proveedor inactivo, **pero NO se bloquea editar un borrador cuyo proveedor se desactivo despues**: lo que se impide es MOVER la compra a un proveedor inactivo. Sin esa asimetria, desactivar un proveedor dejaba borradores inmodificables.

#### Como quedo modelada la unidad en la linea de compra

Es la parte del port que **no es mecanica** (ver `PAT-052`). `OrdenCompraItem` lleva **tres** columnas en vez de una cantidad:

- **`Cantidad`** es `decimal(18,3)` (en marihogar es `int`), mismo ancho que `Producto.Stock` e `ItemVenta.Cantidad`. Esta expresada en la unidad de **COMPRA**, no convertida: si se compra el bulto, la cantidad es en bultos y **`PrecioCompra` es el precio DEL BULTO**. Es lo que dice la factura del proveedor, y es lo unico contra lo que se puede auditar la linea.
- **`UnidadCompra`** la declara la linea, como columna propia. No alcanza con mirar `Producto.UnidadCompra`: el mismo producto se compra a veces por bulto y a veces por unidad suelta, y la ficha solo puede decir una de las dos. El operador la puede cambiar por linea.
- **`FactorConversionAplicado`** es un **snapshot congelado** de `Producto.FactorConversion` al cargar la linea. `UnidadVenta` tambien se congela. La conversion a stock usa ESE factor, no relee la ficha — mismo criterio con el que `ItemVenta` congela precio e IVA.

**`CantidadEnUnidadVenta` es una propiedad CALCULADA** (`Cantidad * FactorConversionAplicado`), con `entity.Ignore(...)` explicito en el DbContext: es derivada exacta de dos columnas que si se persisten, y duplicarla en la base abriria la puerta a que queden en desacuerdo. Es el valor que el paso 4 va a ingresar al stock.

**Por que el snapshot y no releer la ficha:** `FactorConversion` es un campo editable. Si el proveedor cambia el tamano del bulto y alguien actualiza el producto, una compra vieja todavia sin recibir pasaria a ingresar una cantidad de stock **distinta de la que se cargo**, y una ya recibida mostraria un equivalente que no coincide con el movimiento de stock real.

**Guarda que no es cosmetica:** cuando `UnidadCompra == UnidadVenta`, el factor se **FUERZA a 1** aunque llegue otro valor del formulario. Verificado ejecutando: con factor 99 y unidades iguales, se persiste 1 y el equivalente queda en 3, no en 297. Sin esa guarda, un factor heredado de la ficha queda de fantasma en una linea que vino en unidades sueltas y al recibir multiplica el stock.

**La validacion se delega al contrato que ya existe** (`IUnidadMedidaConversionService.EsFactorConversionValido`, regla R4 del catalogo) en vez de reimplementar la regla con otro criterio. Cuando las unidades difieren y no hay factor, el error es funcional y explicito, no un 500 ni un stock mal ingresado.

**Riesgo declarado (pregunta abierta 6 de `4-presupuestador.md`, sin resolver):** el factor es **fijo por producto**. Si el mismo producto llega en bultos de distinto tamano segun el proveedor, tendria que vivir en `CodigoProveedorProducto`. El snapshot **absorbe** ese caso sin cambio de esquema mientras el operador corrija el factor a mano al cargar la compra, pero no lo resuelve de raiz. **Hay que preguntarselo al cliente antes de escribir la migracion del paso 4.**

#### `CodigoProveedorProducto` leido por primera vez

Los **110.683 mapeos** migrados en dev (el brief decia 127.629; en `laplatense_dev` son 110.683) no los leia **ninguna pantalla** hasta esta entrega. `IProductoService.BuscarParaCompraAsync(texto, proveedorId)` es el primer consumidor: resuelve por nombre, codigo interno, codigo de barras propio, codigos de barras alternos **y el codigo de ESE proveedor**.

El match por codigo de proveedor esta **acotado a `proveedorId`**, que es exactamente por lo que el indice unico de la tabla es compuesto `(ProveedorId, CodigoDelProveedor)`: el mismo codigo puede identificar productos distintos en proveedores distintos, asi que buscar sin acotar devolveria el producto equivocado — con 110.683 filas, en silencio. Verificado ejecutando contra dato real: el codigo `-0099-42` del proveedor #1 resuelve al producto #19078, y **sin `proveedorId` no lo resuelve**. Los resultados que matchearon por codigo de proveedor se ordenan PRIMERO.

#### Aritmetica fiscal de la compra — el Service es la autoridad

Dos descuentos **en cascada** + tres impuestos, los cinco como par `%`/importe bidireccional. La misma aritmetica esta espejada en el JS de `Create.cshtml` para feedback inmediato, pero **lo que se persiste siempre se recalcula en `OrdenCompraService.AplicarFiscal`**: el cliente puede manipular el JS, asi que los montos que llegan del formulario son una PROPUESTA.

Criterio del par bidireccional server-side (`ResolverPar`): si viene un **porcentaje > 0**, manda el porcentaje. Si el porcentaje viene en 0 pero el **importe** no, manda el importe y se despeja el porcentaje — es el caso real *"el proveedor me puso $317.526,41 de descuento y no me dice el %"*. El importe se acota a la base para que la compra nunca quede en negativo.

**La cascada verificada con numeros**, sobre un subtotal de 10.000 con `33+5`:

| Concepto | Importe |
|---|---:|
| Subtotal | 10.000,00 |
| Descuento 33% | − 3.300,00 |
| Descuento adicional 5% **del neto** (no del subtotal) | − 335,00 |
| **Base imponible** | **6.365,00** |
| IVA 21% sobre la base | 1.336,65 |
| Percepcion IIBB 4% sobre la **misma** base (sin sumar el IVA) | 254,60 |
| Otros 1,5% sobre la misma base | 95,48 |
| **Total** | **8.051,73** |

El descuento efectivo del `33+5` es **36,35%**, no 38%. Esa cifra es la que valida la estructura contra dato propio: `Producto.Bonificacion` del catalogo migrado guarda literalmente valores como `"33+5"`.

**PENDIENTE DE CONFIRMAR CON EL CLIENTE:** la ESTRUCTURA de dos niveles en cascada esta respaldada por el dato propio (`Bonificacion`), pero la **formula exacta** — en particular que las percepciones se liquiden sobre la base pelada y no sobre base + IVA — viene de una factura real de un proveedor de marihogar, no de uno de La Platense. **Hay que verificarla contra una factura real suya antes de darla por cerrada.**

Defensivo y verificado ejecutando: con `Facturada = false`, los tres impuestos se **fuerzan a 0** y `TipoComprobante`/`PuntoVenta`/`NumeroComprobante` a null, aunque lleguen cargados a mano desde el formulario. Una compra en negro con un IVA colgado inflaria el Total y, cuando llegue el paso 4, la deuda que se postea en la cuenta del proveedor.

**Nada de AFIP entro a este modulo**, confirmado: `TipoComprobanteCompra` es A/B/C manual sin correlato fiscal, el CUIT del proveedor es texto libre validado solo por longitud (11 digitos), y no hay constatacion de comprobante ni consulta de padron. Es el mismo criterio de marihogar (0 hits de afip en su `OrdenCompraService` y su controlador).

#### Bugs propios encontrados EJECUTANDO (no leyendo)

1. **`ObtenerNetoVivoAsync` devolvia 160.000 en vez de 60.000.** La primera version recibia un `TipoMovimientoCCProveedor` y calculaba *"suma de originales no-reversion menos suma de reversiones DENTRO de ese tipo"*, copiando el shape del ledger de caja. Pero en un ledger de **deuda** la reversion de un `Cargo` se postea como un `Pago` (es la unica forma de mover el saldo en sentido contrario), asi que **filtrar por tipo dejaba la reversion afuera del calculo**: un saldo inicial de 100.000 reajustado a 60.000 devolvia la SUMA de los dos cargos. Corregido a **neto CON SIGNO sobre los dos tipos**. Efecto colateral deseado: `EsReversion` queda como dato informativo (el badge de la grilla) y **no participa de la aritmetica** — un contramovimiento al que se le olvide el flag igual neutraliza bien el saldo.
2. **El neto vivo no estaba acotado por proveedor.** Los origenes manuales (`SaldoInicial`, `AjusteManual`) no tienen documento y usan `OrigenId = 0`, asi que sin filtrar por `ProveedorId` el calculo **mezclaba el saldo inicial de TODOS los proveedores en un solo neto**: reajustar el saldo de uno habria revertido la plata de los otros. Encontrado en revision de codigo propia antes de ejecutar, y el arnes tiene un check dedicado que lo deja observable (crea dos proveedores con saldo inicial, reajusta uno y verifica que el otro no se movio).

Y un tercero **en el arnes mismo**, que vale registrar porque confirma que la regla sigue viva en este proyecto: la linea que verificaba la limpieza usaba `p.Nombre.StartsWith("ZZVERIF-E3")` y **revento con `Expression '[SqlConstantExpression] COLLATE utf8mb4_bin' does not have a type mapping assigned`**. Es **`CRM-019`** (misma familia que `MH-001`), reproducido en vivo. Fix: `EF.Functions.Like`. **El codigo de produccion de esta ronda no tiene ni un `StartsWith`/`EndsWith`** (verificado por grep) y **ninguna coleccion local de string** llega al provider: los IN que hay son de `int` o de enum, y el match por etiqueta de enum se resuelve con una consulta por valor ESCALAR (la forma que MH-001 prescribe para su quinta aparicion).

#### Archivos y capas modificadas

**Domain — enums nuevos (5):**

- `Enums/TipoMovimientoCCProveedor.cs` — `Cargo`/`Pago`. Enum PROPIO, separado del de clientes: la semantica es la deuda hacia afuera.
- `Enums/EstadoOrdenCompra.cs` — `Borrador`/`Confirmada`/`Recibida`/`Cancelada`. `Recibida` declarada SIN transicion implementada.
- `Enums/TipoComprobanteCompra.cs` — A/B/C manual, sin correlato AFIP.
- `Enums/MonedaProveedor.cs` — `Peso`/`Dolar`. Desarrollo nuevo.
- `Enums/FormaPagoProveedor.cs` — 5 valores. Desarrollo nuevo.

**Domain — entidades:**

- `Entities/Proveedor.cs` — **AMPLIADO** (aditivo). Sigue implementando `ICatalogoSimpleEntity` y conservando `Nombre`+`Activo` con el mismo significado.
- `Entities/MovimientoCCProveedor.cs` — NUEVA. **No hereda de `SoftDestroyable`** (ledger inmutable), con `UsuarioId` explicito porque no la alcanza el stamping de auditoria del DbContext.
- `Entities/OrdenCompra.cs` — NUEVA.
- `Entities/OrdenCompraItem.cs` — NUEVA, con el modelo de unidad de `PAT-052`.

**Application:**

- `Helpers/OrigenCCProveedor.cs` — NUEVO. Los origenes del ledger en **un solo lugar invocable** (antidoto a LP-002: el combo del filtro y el mapa de etiquetas de la vista salen del mismo diccionario, asi que agregar un origen no requiere tocar la vista).
- `DTOs/ProveedorDtos.cs`, `DTOs/MovimientoCCProveedorDtos.cs`, `DTOs/OrdenCompraDtos.cs` — NUEVOS.
- `Interfaces/IProveedorService.cs` — NUEVO (archivo propio). **Reemplaza** al `IProveedorService : ICatalogoSimpleService` que vivia en `ICatalogoSimpleService.cs`.
- `Interfaces/ICCProveedorService.cs`, `Interfaces/IOrdenCompraService.cs` — NUEVOS.
- `Interfaces/ICatalogoSimpleService.cs` — se saco `IProveedorService`, con la nota de por que.
- `Interfaces/IProductoService.cs` — `+ BuscarParaCompraAsync(texto, proveedorId)`.

**Infrastructure:**

- `Services/ProveedorService.cs` — **REESCRITO**. Ya no hereda de `CatalogoSimpleServiceBase<Proveedor>`.
- `Services/CCProveedorService.cs`, `Services/OrdenCompraService.cs` — NUEVOS.
- `Services/ProductoService.cs` — `+ BuscarParaCompraAsync`.
- `Data/AppDbContext.cs` — 3 `DbSet` nuevos, configuracion de las 3 entidades, ampliacion del bloque de `Proveedor`, y la correccion del comentario viejo.
- `DependencyInjection.cs` — 3 registraciones (`ICCProveedorService`, `IProveedorService` reapuntado, `IOrdenCompraService`).
- `Migrations/20261005231651_EntregaTres_ProveedoresCCCompras.cs` — ver abajo.

**Web:**

- `Models/ProveedorViewModels.cs`, `Models/OrdenCompraViewModels.cs` — NUEVOS.
- `Controllers/ProveedoresController.cs`, `Controllers/OrdenesCompraController.cs` — NUEVOS, los dos con `[Authorize(Policy = "RequireAdministracion")]` **a nivel de clase, sin overrides por accion**.
- `Views/Proveedores/` — `Index`, `Create`, `Edit`, `_Formulario` (parcial compartida por los dos formularios, 20 campos), `_FormularioScripts`, `CuentaCorriente`, `RegistrarAjuste`.
- `Views/OrdenesCompra/` — `Index`, `Create` (sirve tambien para Edit: el controller hace `return View("Create", vm)`), `Details`.
- `Views/Shared/_Layout.cshtml` — seccion "Compras" en el sidebar, dentro del bloque de Administrador.
- `Views/Dashboard/Index.cshtml` — correccion del texto prescriptivo (pasada 3 del barrido).

#### Migracion EF

**`20261005231651_EntregaTres_ProveedoresCCCompras`** — generada **y aplicada SOLO a `laplatense_dev`**. 100% **aditiva**: 18 `AddColumn` sobre `Proveedores`, 3 `CreateTable` (`MovimientosCCProveedor`, `OrdenesCompra`, `OrdenCompraItems`), 9 `CreateIndex`. **Cero `DropColumn`, cero `AlterColumn`** sobre lo que ya existia. `has-pending-model-changes`: sin drift.

**Correccion de datos agregada a mano sobre la migracion generada** — y es el hallazgo que la hace no-trivial: `Moneda` es un enum **no nullable** y EF la agrega con `defaultValue: 0`, pero el primer valor del enum es `MonedaProveedor.Peso = 1` (la convencion del proyecto numera explicito desde 1). Sin corregirlo, los **85 proveedores que ya existian** quedaban con `Moneda = 0`, que no corresponde a ningun valor del enum: el listado mostraria "0" crudo, el filtro "Pesos" no los encontraria y `p.Moneda == MonedaProveedor.Peso` daria false para todos. **Es exactamente la clase de incoherencia de LP-002: la columna funciona perfecto para las filas nuevas y esta mal en las que ya estaban, en silencio.** Se agrego `UPDATE Proveedores SET Moneda = 1 WHERE Moneda = 0;`, con `WHERE` acotado para que correr la migracion dos veces sea inocuo. Verificado despues de aplicar: los 85 quedaron en 1.

**Produccion sigue atras y ahora son TRES migraciones:** le faltan `EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago`, `D9_NormalizarFechaCajaMovimiento_DiaDeNegocio` y esta.

#### Evidencia de verificacion (ejecutada, sin navegador)

El rol del Implementador prohibe levantar la app y probar por navegador, y "compila y lo lei" no es evidencia suficiente en este proyecto. La combinacion usada, toda ejecutada de verdad:

1. **`dotnet build FerreteriaLaPlatense.slnx` — 0 errores, 9 advertencias** (las 9 son `NU1902` de MailKit/MimeKit, preexistentes). **Las vistas Razor SI compilan en el build, confirmado en esta misma ronda sin tener que provocarlo**: un `autofocus` condicional en `_Formulario.cshtml` rompio el build con `RZ1031` y hubo que corregirlo. Asi que el build limpio tambien dice algo sobre las 10 vistas nuevas.
2. **Grafo de DI validado** con `BuildServiceProvider(ValidateOnBuild + ValidateScopes)` en un proyecto de consola aparte, con stubs de `IConfiguration` e `IWebHostEnvironment` (los aporta el host de ASP.NET; su ausencia en un arnes de consola es falla del arnes, no del codigo). Los 4 servicios del modulo resuelven en un scope real: sin ciclos ni captive dependencies.
3. **Los Services ejercitados DIRECTAMENTE contra `laplatense_dev`** — no simular requests, la capa de negocio real: **161 checks, 161 OK**, con limpieza al final que dejo la base en su linea base exacta (85 proveedores, 0 compras, 0 movimientos CC, 0 residuo de prueba). Cobertura: los 2 bugs propios de arriba, la aritmetica fiscal con numeros, el modelo de unidad (bultos, decimales, factor fantasma, factor faltante), las transiciones de estado validas e invalidas, el perimetro (stock/caja/CC/ajustes de stock contados antes y despues de confirmar y de cancelar), las 3 relaciones que bloquean la baja, los 8 filtros de columna, 30 terminos distintos de busqueda global (texto, importe es-AR e invariante, fecha, etiquetas de enum, badges), las 30 combinaciones de columna x direccion de ordenamiento, y 5 checks de regresion sobre lo que ya estaba (catalogo completo, codigos de proveedor completos, ningun proveedor con enum invalido, el contrato de `tools/MigracionCatalogo`, y la CC de clientes).
4. **`has-pending-model-changes`** — sin drift entre el modelo y la ultima migracion.

**Lo que NO se verifico y le queda a QA:** todo lo que solo se ve en un navegador — el Select2 AJAX del buscador de productos, la grilla de items renderizada por JS, los cinco pares `%`/importe bidireccionales, el daterangepicker, los popup de SweetAlert2, y que el JS de la pantalla de compra de el **mismo** total que el Service (la duplicacion es deliberada, pero que las dos mitades coincidan hoy solo esta verificado del lado del Service).

#### Riesgos y supuestos

1. **La formula fiscal exacta es un supuesto de negocio tomado de otro cliente.** La estructura de cascada esta respaldada por dato propio (`Bonificacion = "33+5"`); el orden exacto de las percepciones, no. Confirmar contra una factura real de La Platense.
2. **El factor de conversion es fijo por producto** (pregunta abierta 6 de `4-presupuestador.md`). El snapshot de la linea absorbe el caso del bulto distinto por proveedor, pero no lo resuelve de raiz.
3. **El filtro por rango de saldo del listado de proveedores se aplica sobre la pagina visible**, no sobre el conjunto completo, porque el saldo no es una columna (vive en el ledger). Con 85 proveedores y `pageLength` 15 alcanza; si el padron creciera a miles habria que materializar el saldo. **Esta declarado en la propia pantalla** con un `ov-field-hint`, no escondido. Por el mismo motivo, la columna de saldo **no es ordenable**: se declara `orderable: false` en vez de ofrecer un orden que no haria nada.
4. **El JS y el Service duplican la aritmetica fiscal.** Es deliberado (el Service es la autoridad), pero si se cambia una mitad hay que cambiar la otra o el operador ve un total distinto del que se guarda. Esta anotado en los dos lados.
5. **La recepcion no existe**, y los mensajes de la UI lo dicen explicitamente ("El stock y la cuenta corriente del proveedor se actualizan al registrar la recepcion de la mercaderia"). Sin esos mensajes, el perimetro de esta ronda se lee como un bug en la prueba.
6. **El ajuste manual de CC de proveedores no consulta `ValidarPeriodoAbiertoAsync`**, igual que el de clientes: no escribe en caja, asi que no hay arqueo que pueda quedar desfasado. **El egreso real del paso 5 SI tiene que pasar por esa guarda** — el camino no quedo preparado de ninguna otra forma.
7. **`EstadoOrdenCompra.Recibida` existe en el enum y ningun codigo la escribe.** La guarda de `CancelarAsync` ya la contempla, para que el dia que exista la recepcion no haya que acordarse de endurecerla.

#### Pruebas minimas requeridas para QA

Las de navegador, que son las que este rol no puede hacer:

1. **Proveedores/Index**: filtrar por cada una de las 8 columnas visibles; buscar en el buscador global por un importe visible (tipear "1480" tiene que encontrar un TC de "$ 1.480,50"), por una fecha `dd/MM/yyyy`, y por una etiqueta ("Pesos", "Monotributo", "Inactivo"). Navegar a otra pantalla y volver: los filtros siguen aplicados. "Limpiar filtros" vacia los controles Y al reentrar no los repone.
2. **Proveedores/Create**: alta con solo razon social; alta con moneda Dolar **sin** TC (tiene que bloquear); alta con descuento adicional **sin** descuento base (bloquear); alta con saldo inicial 100.000 y verificar que la cuenta corriente muestra un movimiento de apertura por ese importe.
3. **Proveedores/Edit**: que los 20 campos vuelvan cargados (**mirar el HTML crudo**: una coma dentro de un `value` de un `input type="number"` es LP-003). Cambiar el saldo inicial y verificar que la CC muestra 3 movimientos (original + reversion + nuevo) y el saldo correcto.
4. **Proveedores/CuentaCorriente**: cargar un ajuste manual y verificar que el saldo corrido de la ultima fila coincide con la card de saldo; filtrar por rango de fecha y comprobar que el saldo corrido **no** arranca de cero; verificar que **el ajuste no aparece en Caja**.
5. **Baja de proveedor**: estando en la pagina 2+ del listado, eliminar uno y confirmar que el DataTable **no vuelve a la pagina 1**. Intentar eliminar uno con codigos del catalogo mapeados (tiene que bloquear con mensaje).
6. **OrdenesCompra/Create** — es la pantalla con mas riesgo: elegir un proveedor con descuento habitual y verificar que se precarga; buscar un producto **tipeando el codigo del proveedor** (los hay reales en la base); agregar una linea en bultos y verificar la columna "Equivale a"; tocar el `%` de descuento y ver que se recalcula el importe, y al reves; marcar/desmarcar "vino con factura" y ver que la card de impuestos aparece y desaparece y que los impuestos vuelven a 0; **guardar y comparar el total de la pantalla contra el de la pantalla de detalle** (son dos calculos distintos y tienen que coincidir).
7. **Reabrir un borrador** (`Edit`): que las lineas vuelvan con su cantidad, unidad, factor y precio, y que el combo de proveedor llegue **con el proveedor ya elegido**.
8. **Maquina de estados**: desde Borrador, los botones visibles tienen que ser Editar + Confirmar + Cancelar. Confirmar: no aparece Editar, no se mueve el stock del producto ni aparece nada en Caja ni en la CC del proveedor. Cancelar con motivo vacio (bloquear). Probar `POST /OrdenesCompra/Confirmar/{id}` sobre una ya confirmada (error funcional, nunca 500).
9. **Permisos**: con usuario Vendedor, el sidebar NO muestra "Compras", y `GET /Proveedores` y `GET /OrdenesCompra` devuelven 403.
10. **Regresion**: que el catalogo de productos, el buscador de la venta y la CC de clientes sigan funcionando igual.

#### Checklist de salida para merge

- [x] Build limpio de la solucion (0 errores; las vistas Razor entran en el build, confirmado)
- [x] Grafo de DI validado (`ValidateOnBuild` + `ValidateScopes`)
- [x] Services ejercitados contra `laplatense_dev` (161/161) y base devuelta a su linea base
- [x] Migracion EF generada, aditiva, aplicada **solo a dev**, sin drift de modelo
- [x] Correccion de datos del enum `Moneda` incluida en la migracion y verificada
- [x] Barrido LP-002 completo (4 pasadas + 2 extras), con 5 hallazgos propios y sus fixes
- [x] MH-001 / CRM-019: cero colecciones locales de string, cero `StartsWith`/`EndsWith` en el codigo nuevo; todas las consultas nuevas **ejecutadas**
- [x] LP-003: `InvariantCulture` en todos los `value` de los inputs numericos de las vistas nuevas
- [x] LP-009: las 6 propiedades de fecha nuevas declaran su semantica
- [x] Enums: los 5 nuevos numerados explicito desde 1, con la nota de "todo valor nuevo al final"
- [x] Design system: `.ov-form-page`/`.ov-page-head`/`.ov-form-actions`/`.ov-required`/`.ov-field-hint`/`.ov-detail-grid`, Select2 en todo combo, SweetAlert2, daterangepicker, DataTables server-side con filtro por columna visible, PAT-016 en los 3 listados
- [x] `PAT-052` agregado al catalogo; `PAT-001` actualizado con 3 referencias nuevas; `cat_resumen.txt` regenerado
- [x] `5-implementador.md` y `trazabilidad.md` actualizados
- [ ] **Sin push y sin deploy** (pedido explicito de Joaquin) — el commit queda local en `entrega-1-migracion`
- [ ] Verificacion por navegador: le corresponde a QA (ver "Pruebas minimas")

### Entrega 3 — pasos 4 y 5: recepción de mercadería y pagos a proveedores (2026-10-05, rama `entrega-1-migracion`)

**No pusheado y no deployado** — pedido explícito de Joaquín ("no publicar, dejar el desarrollo listo"). Nada corrió contra producción: la migración se aplicó únicamente a `laplatense_dev`.

Cierra el **impacto real del módulo de Compras**. Hasta el paso 3 nada de Compras movía un peso ni una unidad de stock; desde esta ronda:

- **`RecibirAsync`** (`Confirmada → Recibida`) incrementa stock, escribe un ledger de stock nuevo y postea el `Cargo` de deuda, **todo en una transacción**. **No toca la caja**: recibir genera deuda, la plata sale al pagar.
- **`PagoProveedorService`** es el **primer punto del módulo por donde sale plata de la caja**: cada línea de pago postea un `Pago` en la cuenta corriente del proveedor y un `Egreso` en el ledger de caja, mismo monto, misma fecha y mismo `OrigenId`.

#### Resultado del escaneo de reutilización (obligatorio antes de implementar)

Encontrado en el **paso 1** del escaneo (`docs/patrones/cat_resumen.txt`):

- **`PAT-052`** — "Línea de documento que declara su unidad y CONGELA el factor de conversión". Es el patrón que esta ronda **consume**: el paso 3 lo construyó, el paso 4 lo usa. **Se amplió** con un `archivos_referencia` nuevo: el consumidor y la lección que solo aparece al escribirlo (ver abajo).
- **`PAT-020`** — "Cancelación de comprobante con pagos: ledger inmutable + reversión acotada a lo posteado". Aplicado tal cual a la reversión de un pago a proveedor, en los dos ledgers.
- **`PAT-019`** — "Autocompletar el monto de un pago nuevo con el saldo pendiente". Aplicado: la primera línea del formulario de pago arranca con el saldo pendiente completo y la forma de pago habitual del proveedor.
- **`PAT-003`** / **`PAT-051`** — pago multi-medio y medio como dimensión del ledger único. El pago a proveedor es multi-línea con su `MedioPagoCaja` por línea.
- **`PAT-016`** — búsqueda global multi-formato. Aplicado a las dos columnas nuevas (origen de caja por etiqueta, estado del precio del catálogo).

**Dos patrones NUEVOS agregados al catálogo** (el criterio ya vivía en el estudio y no estaba catalogado):

- **`PAT-053`** — "Un pago, dos ledgers: punto único de egreso con la MISMA clave de origen en los dos". Origen `marihogar` (CR-84, en producción), portado y **simplificado**: de sus 579 líneas solo ~80 son runtime, el resto es backfill one-shot de datos históricos suyos y **no se portó**.
- **`PAT-054`** — "Bandera `costo actualizado, precio sin recalcular`". **Primera implementación en el estudio**, sin precedente: `RecibirAsync` de marihogar **no toca** `Producto.PrecioCompra`.

#### Paso 4 — la conversión de unidades, que es lo que NO se podía copiar

El precedente (`marihogar/OrdenCompraService.RecibirAsync`, línea ~390) tiene `Cantidad` como `int`, `StockActual` como `int`, y el ingreso de stock es literalmente la misma cantidad del ítem sin traducir nada. Acá hay que convertir, y con el factor **congelado en la línea**.

**El problema que apareció al escribirlo, y que el brief no podía anticipar:** `IUnidadMedidaConversionService.ConvertirCompraAVenta(producto, cantidad)` lee `producto.FactorConversion`, o sea el factor **de hoy**. Usarlo en la recepción habría roto exactamente el congelamiento que `OrdenCompraItem` existe para garantizar (`PAT-052`). Y la salida fácil —que la recepción se arme la multiplicación por su cuenta— parte la regla en dos lugares, que es cómo nacen las reincidencias de `LP-002`.

Se resolvió agregando al contrato una sobrecarga que **recibe** el factor:

- `ConvertirConFactor(unidadCompra, unidadVenta, factorCongelado, cantidad, nombreProducto)` — la aritmética y la condición de error viven **acá y solo acá**; `ConvertirCompraAVenta` quedó como envoltorio que le pasa los valores de la ficha.
- `ValidarConversion(...)` — la **misma** condición como pregunta en vez de como excepción: devuelve el mensaje listo para mostrar o `null`.

**Por qué `ValidarConversion` y no un try/catch adentro de la transacción:** `ConvertirConFactor` lanza `InvalidOperationException` si falta el factor. Con una factura de 80 renglones, descubrirlo en el renglón 40 dejaría 39 productos ya modificados en el change tracker: funcionaría por el rollback, pero "no deja nada a medio aplicar" sería una propiedad de la base y no del código. El guard previo recorre **todas** las líneas, junta **todos** los problemas y la recepción **no arranca** — y el operador ve las tres líneas que hay que arreglar, no la primera.

**Nota de contexto que importa para QA:** en `laplatense_dev` hay **0 productos** con `UnidadCompra != UnidadVenta` sobre 112.485. El ítem 0.4 pasó los 87.542 `Metro` a `Unidad` en bloque y los 2.635 candidatos a corte por metro esperan marcación manual del cliente. **O sea que hoy el camino de conversión no tiene ni un dato real que lo ejercite**: se midió con productos sembrados y limpiados (ver "Casos medidos").

#### Paso 4 — el ledger de stock, construido de cero

Este proyecto **no tenía** ledger de stock. Los únicos escritores de `Producto.Stock` eran `VentaWorkflowService` (resta directa, sin rastro) y `AjusteStockService.AplicarAjusteAsync`, que hace un **SET absoluto** y además fuerza `StockVerificado = true`.

`AjusteStock` **no servía** como rastro de una compra, por dos motivos independientes: no tiene `OrigenTipo`/`OrigenId` (el movimiento no se puede atar al documento que lo causó) y su semántica es "alguien contó y corrigió", que es otra cosa. Marcar productos como verificados porque llegó un bulto sería, además, falso — y por eso **`RecibirAsync` no toca `StockVerificado`**.

`MovimientoStock` nuevo, con el criterio de `marihogar/MovimientoStock` y dos adaptaciones:

1. `Cantidad` es `decimal(18,3)` y no `int` — mismo ancho que `Producto.Stock`.
2. Se agrega **`OrigenTipo`** (el precedente solo tiene `OrigenId`, porque allá el `Tipo` ya determina la tabla). Acá se declara el par completo, y el `OrigenId` del movimiento de stock es **el mismo** que el del `Cargo` de deuda.

**Inmutable: no hereda `SoftDestroyable`**, mismo criterio que `MovimientoCCProveedor`. Único escritor: `MovimientoStockService`.

**ALCANCE DECLARADO, y hay que tenerlo a la vista: `Σ MovimientoStock.Cantidad` NO reconstruye `Producto.Stock`.** Los movimientos históricos de venta y los ajustes ya aplicados **no se migraron hacia atrás** (no estaba en alcance y toca dos módulos ya en producción). El ledger es el rastro de las compras recibidas, no el libro mayor. Por eso la recepción escribe **las dos cosas** (el stock del producto y el movimiento del ledger) y no deriva una de la otra. Los otros tres valores del enum (`Venta`, `Ajuste`, `AnulacionVenta`) están **declarados sin escritor** para no renumerar el enum el día que se unifique.

#### Paso 4 — el costo del producto: lo que se actualiza y lo que NO

**Decisión del orquestador, sin precedente portable** (`RecibirAsync` de marihogar no toca `Producto.PrecioCompra`): la recepción **sí** actualiza `PrecioCompra` con el costo real, y **no** toca `PrecioVenta` ni `PorcentajeRecargo`.

El motivo está en la fórmula: `PrecioVenta = PrecioCompra × (1+Recargo%)/(1+IVA%)`. Recalcularla en cada recepción movería los precios de mostrador de **112.485 productos** sin que nadie lo pida y a espaldas del cliente — un aumento de lista del proveedor se convertiría en un aumento al público automático y silencioso.

**La base del costo NO es el total de la factura**, y confundirlas infla el catálogo entero:

```
ratioDescuento   = (Subtotal − MontoDescuento − MontoDescuentoAdicional) / Subtotal
costoNetoLinea   = item.Subtotal × ratioDescuento
costoUnitario    = Σ(costoNetoLinea por producto) / Σ(cantidadConvertida por producto)
```

**Sin IVA ni percepciones**: eso es lo que se le transfiere al proveedor, no lo que costó la unidad. Sumárselo inflaría el costo de todo el catálogo un 21% y, por la fórmula derivada, después el precio de venta. Es un número **distinto** del que va al `Cargo` de deuda (que sí es el total con impuestos): los dos son correctos y responden a preguntas distintas. Conviene que quede escrito antes de que alguien lo "arregle".

Dos detalles que no son cosméticos:

- **Se acumula por PRODUCTO, no por línea.** Una compra puede traer el mismo producto en dos renglones (dos bultos de distinto tamaño, o el ítem repetido). Con los acumuladores, el costo que queda es el **promedio ponderado real** de la compra; tomando el último renglón, el resultado dependería del orden de carga.
- **Un costo calculado en 0 NO se escribe.** Pasa con un remito sin precios o un descuento del 100%, y pisar el costo del catálogo con 0 sería destructivo y silencioso: el precio de venta derivado pasaría a 0 en el próximo recálculo masivo.

**El enganche con la Entrega 6 (`PAT-054`):** `Producto.PrecioVentaDesactualizado` (bool) + `FechaUltimoCostoCompra` (instante UTC). La bandera se muestra en el **listado del catálogo** como columna, **filtro tri-estado**, criterio de **orden** y en la **búsqueda global** por su etiqueta visible — porque sobre 112.485 filas una alerta que no se puede aislar es inservible, y el caso de uso es exactamente masivo: después de recibir 80 renglones lo que el cliente necesita es la **lista**, no abrir 80 fichas.

**La mitad simétrica (hallazgo propio del barrido): alguien tiene que APAGARLA.** Nada la apagaba. Una alerta que no se apaga deja de significar algo. Se agregó a `ProductoService.EditarAsync`: se apaga **solo si cambió `PrecioVenta` o `PorcentajeRecargo`** (eso *es* reaplicar el margen a mano) y se **mantiene** si el usuario guardó la ficha sin tocar ninguno de los dos — guardar no es decidir el precio. El otro apagador previsto es el aumento masivo de la Entrega 6, que va a necesitar apagarla por lote.

#### Paso 5 — pagos: `PAT-053` y por qué el punto único se crea ahora

`PagoOrdenCompra` portado del precedente (39 líneas): `OrdenCompraId`, `Metodo` (reusa `FormaPagoProveedor`, el enum que ya vive en la ficha del proveedor — mismo universo de valores), `Monto`, `Fecha`, `Estado`, `FechaPagoTentativa?`, `Notificado`. **Los dos últimos quedan declarados y ningún código los escribe**: son el esquema del paso 6 (pagos programados). **No hay entidad de cheque** (paso 7).

`IEgresoPagoProveedorService` es el **único punto** que postea y revierte el egreso de caja. Hoy tiene **dos** escritores (registrar y revertir) y los pasos 6 y 7 van a sumar más: **el punto único se crea ahora, antes de que el problema exista.** En marihogar son 6 los caminos que bajan la deuda y, mientras el egreso estuvo armado inline en el primero, los otros cinco movieron la deuda sin mover la plata. Crearlo después obligó allá a un backfill que fue 500 de las 579 líneas del servicio.

**Lo que se copió del precedente y es lo más valioso:** el egreso usa el **mismo `OrigenTipo`** (`"PagoOC"`) y el **mismo `OrigenId`** que el `Pago` de la cuenta corriente, y ese `OrigenId` es el id de la **línea de pago**, no el del documento (`MH-027`: dos líneas del mismo importe compartiendo clave harían revertir la equivocada). Los literales viven en dos helpers distintos (`OrigenCajaMovimiento.PagoOC` y `OrigenCCProveedor.PagoOC`) porque son dos ledgers con dominios de valores distintos, pero el **valor es idéntico a propósito**.

**Guardas, todas ANTES de abrir la transacción** (adentro no queda ninguna decisión que pueda rechazar la operación):

1. Al menos una línea con monto > 0 — nunca solo `Count == 0`: un post con tres líneas en cero no es un pago y postearía tres movimientos de $0.
2. Forma de pago válida. **`CuentaCorriente` se rechaza**: "pagar a cuenta corriente" es dejar la deuda viva. Aceptarla postearía un egreso por plata que no salió **y** cancelaría una deuda que sigue existiendo — descuadra los dos ledgers a la vez. Se rechaza en el Service **y** no se ofrece en el combo (las dos puntas).
3. Estado pagable (`Confirmada` o `Recibida`). Pagar una `Confirmada` es un **anticipo** y es un caso real (se paga para que el proveedor despache): deja al proveedor con saldo a favor del negocio hasta que la recepción postee el `Cargo`.
4. No más que el saldo pendiente. El criterio de "lo ya pagado" sale del **mismo** método que usa la pantalla (`ObtenerTotalPagadoAsync`): la variante en que la pantalla suma con un criterio y el Service valida con otro es como se deja pagar de más sin que nada falle.
5. **`LP-009`**: `ValidarPeriodoAbiertoAsync` sobre el día de negocio al que se imputa. Es la única vía de escritura de caja del módulo y la guarda no es opcional. El ajuste manual de CC la saltea a propósito; acá no. **Lo que decide si hace falta la guarda es si el movimiento escribe CAJA**, no si escribe el ledger de proveedores.

El `SaveChangesAsync` intermedio para obtener `pago.Id` va **dentro** de la transacción: hace falta porque ese id es el `OrigenId` de los dos ledgers, y no rompe el todo-o-nada.

**Reversión:** neto vivo de **cada ledger por separado** — `ObtenerNetoVivoAsync` (con signo, sobre los dos tipos) para la cuenta corriente y `ObtenerNetoPosteadoAsync` para la caja. Nunca el monto del documento (`MH-020` punto 3). **Idempotente por construcción**: la segunda vez los dos netos están en 0 y no se escribe nada — no hay flag de estado que haya que acordarse de consultar. Calcular los dos netos por separado arregla además el caso en que uno de los dos lados ya se había revertido y el otro no.

Dos detalles de la reversión que descuadran el arqueo si se omiten:

- **Arrastra el MISMO medio de pago que el egreso original.** Si la plata salió por transferencia y vuelve sin medio declarado, al arqueo por medio le falta el ingreso en la cuenta real **y** le sobra en la fila "Sin declarar": se descuadra de a dos.
- **Se imputa a HOY, no a la fecha del pago**, y pasa por `ValidarPeriodoAbiertoAsync` igual. Postear el contramovimiento con la fecha original mete plata en un arqueo posiblemente ya firmado, que es exactamente lo que la guarda existe para impedir.

**Cancelar una compra NO revierte sus pagos anticipados**, a propósito: la plata salió de verdad y el proveedor queda con saldo a favor, que es lo que realmente pasó. Decidir si se pide de vuelta o queda a cuenta de la próxima compra es del negocio. Revertir es una acción aparte y explícita.

#### Barrido `LP-002` — 6 pasadas, 6 hallazgos propios

La **pasada 0** (verificar las premisas del brief, no heredarlas) rindió dos veces:

1. **El brief afirmaba que el único call site de la conversión era `EsFactorConversionValido` en `ProductoService:444`.** Verificado: `ProductoService.cs:554` **y** `OrdenCompraService.cs:707` (el paso 3 ya lo había cableado). Lo que sí era cierto es que **`ConvertirCompraAVenta` tenía CERO call sites**. La diferencia importa: creer que el validador estaba huérfano habría llevado a tratarlo como código nuevo en vez de como un contrato con dos consumidores.
2. **El brief pedía usar `ConvertirCompraAVenta` Y el factor congelado — las dos cosas son incompatibles**, porque ese método lee la ficha viva. Verificarlo es lo que produjo la sobrecarga `ConvertirConFactor` en vez de una multiplicación duplicada.

**Pasada 1 — ¿el campo se postea?** Los inputs de la grilla de pago **a propósito** no tienen `name`: el JS los renumera a índices contiguos en el submit. Por eso quitar una línea del medio **obliga** a renumerar — si no, el model binder corta la lista en el primer hueco y las líneas de abajo se pierden en silencio.

**Pasada 2 — hermanos semánticos.** Grep reproducible: `grep -hn "DateTime" FerreteriaLaPlatense.Domain/Entities/*.cs | grep "get; set;"` da **34** (eran 29 al cerrar el paso 3). Las 5 nuevas declaran su semántica: `MovimientoStock.Fecha`, `PagoOrdenCompra.Fecha`, `PagoOrdenCompra.FechaReversion` y `Producto.FechaUltimoCostoCompra` son **instantes UTC**; `PagoOrdenCompra.FechaPagoTentativa` es un **día calendario de negocio** (sin hora).

**Pasada 3 — comentarios y XML-doc: 20 correcciones.** Es la pasada que más rindió otra vez. Reglas de negocio **falsas** que vivían en el repo: `OrdenCompra` decía "la transición a `Recibida` no está implementada"; `EstadoOrdenCompra.Recibida` decía "DECLARADA, SIN TRANSICIÓN IMPLEMENTADA"; `OrdenCompra.FechaRecepcion` decía "DECLARADO, nunca escrito"; `MovimientoCCProveedor` listaba `OrdenCompra` y `PagoOC` como "No implementado todavía"; `OrigenCCProveedor` declaraba los dos como "sin escritor todavía"; `TipoMovimientoCCProveedor` decía "paso 4, todavía no implementado"; `ICCProveedorService` decía "el día que el paso 5 postee el EGRESO real".

**Y un hallazgo que NO es un comentario viejo sino una promesa vencida:** `Proveedor.TipoCambio` decía *"convertir la línea de compra a pesos desde la moneda del proveedor es alcance del paso 4"*. **No lo fue** — el paso 4 se cerró sin eso, y ahora importa **más** que antes porque ese costo se persiste en la ficha del producto. Se reescribió como **pendiente declarado** (ver "Riesgos") y no como una promesa dentro del código: una promesa vencida en un comentario hace creer que el caso está cubierto.

**Pasada 4 — vistas y JS.** Cero `toLocaleString` sobre una fecha: todas las fechas van por `window.Fmt`, los `toLocaleString('es-AR')` son solo importes y cantidades. `LP-003` aplicado en los `value` de los `<input type="number">` del formulario de pago (`InvariantCulture`).

**Pasada 5 — la mitad simétrica.** Dos hallazgos:

- **Quién APAGA `PrecioVentaDesactualizado`** (resuelto arriba). Nada lo hacía.
- **`ovAplicarSelect2` en las filas agregadas por JS.** El auto-init de `site.js` corre en el ready y no alcanza a las filas nuevas del pago multi-línea: hay que llamarlo a mano sobre la fila insertada.

**Pasada 6 — la migración sobre las filas que YA estaban.** La lección del paso 3 (los 85 proveedores con `Moneda = 0`) **no aplica acá, y esta vez se verificó en vez de suponerse**: `PrecioVentaDesactualizado` es un **bool** (`false` es un valor legítimo del dominio y es el correcto: ningún producto tuvo todavía una recepción), `FechaUltimoCostoCompra` es **nullable**, y `PagoOrdenCompra.Estado` sí es un enum no nullable con `defaultValue: 0` pero está en una **tabla nueva** sin filas. Verificado con `GROUP BY` sobre la base después de aplicar: **una sola fila, `0` con 112.485**.

#### El cierre de `LP-002` que corta la recurrencia: `OrigenCajaMovimiento`

El relevamiento encontró el ledger de caja **ya desincronizado antes de agregarle nada**:

- Los valores vivían como **tres constantes** en `CajaMovimientoService` y un **cuarto (`"CobroCC"`) como literal suelto** en `CuentaCorrienteClienteService`: no había un lugar donde estuvieran los cuatro.
- El combo de filtro de `Views/Caja/Index.cshtml` tenía los cuatro **hardcodeados con etiquetas legibles** ("Cobro de cuenta corriente", "Ajuste manual") mientras la columna "Origen" de la **misma grilla** renderizaba el valor **crudo** (`CobroCC`, `Ajuste`). **El filtro y la fila ya decían cosas distintas.** Es textualmente el defecto que el ledger de clientes sufrió y que `OrigenCCProveedor` cerró para proveedores.

Se creó `Application/Helpers/OrigenCajaMovimiento.cs` con los **cinco** orígenes y sus etiquetas. Las tres constantes de `CajaMovimientoService` y la de `CuentaCorrienteClienteService` quedaron como **alias** que apuntan ahí (no se tocaron los call sites). El combo sale de `Todos`, la grilla muestra `OrigenEtiqueta` proyectada por el Service, y la búsqueda global compara contra la **etiqueta visible** — una consulta por origen con el valor como **parámetro escalar** (`MH-001`: nunca `origenes.Contains(m.OrigenTipo)`, que es la variante que el grep de `.Contains(` no detecta). **Agregar un origen ya no requiere tocar la vista.**

Mismo criterio aplicado de entrada al ledger nuevo: `OrigenMovimientoStock` nace como helper, no como constantes dentro del Service.

#### Archivos y capas modificadas

**Domain (6 archivos)**
- `Entities/MovimientoStock.cs` — **nuevo**, ledger inmutable de stock.
- `Entities/PagoOrdenCompra.cs` — **nuevo**, línea de pago a proveedor.
- `Enums/TipoMovimientoStock.cs` — **nuevo** (`Compra=1`, `Venta=2`, `Ajuste=3`, `AnulacionVenta=4`; solo el primero tiene escritor).
- `Enums/EstadoPagoProveedor.cs` — **nuevo** (`Pendiente=1` declarado sin escritor, `Pagado=2`, `Revertido=3`).
- `Entities/Producto.cs` — `PrecioVentaDesactualizado` + `FechaUltimoCostoCompra`.
- `Entities/OrdenCompra.cs` — navegación `Pagos` + XML-doc corregido.
- (`Enums/EstadoOrdenCompra.cs`, `Enums/TipoMovimientoCCProveedor.cs`, `Enums/FormaPagoProveedor.cs`, `Entities/OrdenCompraItem.cs`, `Entities/Proveedor.cs`: XML-doc, pasada 3.)

**Application (9 archivos)**
- `Helpers/OrigenCajaMovimiento.cs` — **nuevo**, cierre de `LP-002`.
- `Helpers/OrigenMovimientoStock.cs` — **nuevo**.
- `Helpers/MedioPagoCajaMapper.cs` — `DesdeFormaPagoProveedor` (devuelve `null` para `CuentaCorriente`) + `EtiquetaFormaProveedor`.
- `Interfaces/IMovimientoStockService.cs`, `Interfaces/IEgresoPagoProveedorService.cs`, `Interfaces/IPagoProveedorService.cs` — **nuevos**.
- `Interfaces/IUnidadMedidaConversionService.cs` — `ConvertirConFactor` + `ValidarConversion`.
- `Interfaces/IOrdenCompraService.cs` — `RecibirAsync`.
- `Interfaces/IProductoService.cs` — filtro `precioVentaDesactualizado`.
- `DTOs/MovimientoStockDtos.cs`, `DTOs/PagoProveedorDtos.cs` — **nuevos**.
- `DTOs/OrdenCompraDtos.cs` — `RecepcionOrdenCompraResultDto`.
- `DTOs/CajaDtos.cs` — `OrigenEtiqueta`.
- `DTOs/ProductoDtos.cs` — `PrecioVentaDesactualizado` + `FechaUltimoCostoCompra`.

**Infrastructure (8 archivos)**
- `Services/MovimientoStockService.cs`, `Services/EgresoPagoProveedorService.cs`, `Services/PagoProveedorService.cs` — **nuevos**.
- `Services/OrdenCompraService.cs` — `RecibirAsync` + `EstadosRecibibles` + `ResolverFechaRecepcion`; ahora inyecta `IMovimientoStockService` e `ICCProveedorService` (**sigue sin inyectar `ICajaMovimientoService`**: no puede postear un egreso por accidente porque no tiene con qué).
- `Services/UnidadMedidaConversionService.cs` — las dos entradas nuevas, una sola fórmula.
- `Services/CajaMovimientoService.cs` — constantes → alias del helper, `OrigenEtiqueta` en la proyección, búsqueda por etiqueta de origen, orden por `origenEtiqueta`.
- `Services/CuentaCorrienteClienteService.cs` — el literal `"CobroCC"` → alias del helper.
- `Services/ProductoService.cs` — filtro + proyección + orden + búsqueda global de la bandera, y **quién la apaga** en `EditarAsync`.
- `Data/AppDbContext.cs` — 2 `DbSet` + configuración de las dos entidades nuevas.
- `DependencyInjection.cs` — 3 servicios nuevos.

**Web (5 archivos)**
- `Controllers/OrdenesCompraController.cs` — `Recibir`, `RegistrarPago` (GET/POST), `RevertirPago`, `ArmarDetalleAsync`.
- `Models/OrdenCompraViewModels.cs` — `PuedeRecibir` real, `PuedePagar`, `TotalPagado`, `SaldoPendiente`, `Pagos`, `MovimientosStock` + el ViewModel del formulario de pago.
- `Views/OrdenesCompra/RegistrarPago.cshtml` — **nueva**.
- `Views/OrdenesCompra/Details.cshtml` — botones de recepción y pago, alerta de recibida, card "Lo que entró al stock", card de pagos con reversión, pagado/pendiente en el total.
- `Views/Caja/Index.cshtml` — combo y columna desde el helper.
- `Views/Productos/Index.cshtml` — columna "Estado del precio" + filtro tri-estado.

#### Migración EF generada y aplicada

`20261006002448_EntregaTres_RecepcionMercaderiaYPagosProveedor` — **aplicada SOLO a `laplatense_dev`**.

- `Productos`: + `PrecioVentaDesactualizado` (`tinyint(1)`, `defaultValue: false`) y `FechaUltimoCostoCompra` (`datetime(6)` nullable).
- `MovimientosStock` (tabla nueva): índices `(ProductoId, Fecha)` y `(OrigenTipo, OrigenId)`.
- `PagosOrdenCompra` (tabla nueva): índices `OrdenCompraId`, `Fecha`, `Estado`.

**Estrictamente aditiva**: ninguna columna existente cambia de tipo, nombre ni nullabilidad, y no se borra nada. Sobre 112.485 productos no es una formalidad, es la condición para aplicarla sin ventana de mantenimiento. **Sin backfill, verificado** (ver pasada 6; el razonamiento completo está escrito en el `Up()` de la migración junto con la query de control).

**Producción sigue 4 migraciones atrás** (le faltan `EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago`, `D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`, `EntregaTres_ProveedoresCCCompras` y esta).

#### Evidencia de build y de ejecución

**Sin smoke test funcional por navegador** (lo prohíbe el rol del Implementador). Compensado con evidencia **ejecutada**, no con lectura de código:

1. **`dotnet build` de la solución: 0 errores**, 9 advertencias, todas preexistentes (`NU1902` de MailKit/MimeKit).
2. **Las vistas Razor SÍ compilan en el build** — comprobado metiendo un símbolo inexistente en `RegistrarPago.cshtml` a propósito (`CS0103` en la línea 293), y revertido. Sin esa comprobación, un build limpio no dice nada sobre las dos vistas nuevas.
3. **Grafo de DI validado** con `BuildServiceProvider(ValidateOnBuild + ValidateScopes)` en un proyecto de consola aparte: sin ciclos ni captive dependencies, y los 7 servicios (3 nuevos + 4 con constructor cambiado) resuelven de verdad. Las 3 fallas que aparecieron primero son **del arnés** y no del código (`IConfiguration` e `IWebHostEnvironment` los aporta el host de ASP.NET): se stubearon, porque si no tapan las fallas reales del grafo.
4. **51/51 checks de los Services ejercitados DIRECTO contra `laplatense_dev`**, con la base **devuelta a su línea base** al final (verificado: 0 filas de prueba restantes, 112.485 productos).

#### Casos medidos de conversión de unidades (los números, no "funciona")

Compra sembrada: proveedor nuevo, 2 productos, descuento de cabecera 10%, IVA 21%.

| Línea | Producto | Cantidad | Unidad compra | Factor | Precio | Subtotal |
|---|---|---|---|---|---|---|
| 1 | bulto de tornillos | 5 | Bulto | **12** | $12.000 | $60.000 |
| 2 | martillo suelto | 10 | Unidad (= stock) | **1** | $500 | $5.000 |

Aritmética fiscal: `Subtotal 65.000 → Desc 6.500 → base 58.500 → IVA 12.285 → Total 70.785`. `ratioDescuento = 0,9`.

| Criterio | Esperado | Medido |
|---|---|---|
| CA-1: bultos × factor | stock `0 → 60` (5 × 12, **no** 5) | **60,000** |
| CA-2: unidad simple tal cual | stock `5 → 15` | **15,000** |
| CA-6a: costo del bulto | `60.000 × 0,9 / 60 u = 900` | **900,00** |
| CA-6b: costo de la unidad | `5.000 × 0,9 / 10 u = 450` | **450,00** |
| CA-6c: `PrecioVenta` intacto | `1239,67` y `619,83` sin cambio | **sin cambio** |
| CA-6d: bandera prendida | `true` en los dos | **true** |
| CA-6e: `StockVerificado` | sigue en `false` (recibir no es contar) | **false** |
| CA-4a: `Cargo` por el Total | 1 movimiento de `70.785,00` | **1 / 70.785,00** |
| CA-4b: recepción no toca caja | movimientos de caja antes = después | **9 = 9** |
| CA-5: ledger por línea | 2 filas, `[60, 10]`, suma 70 | **2 / [60,000, 10,000] / 70,000** |
| CA-5b: mismo `OrigenId` | stock y CC apuntan a la misma OC | **43 / 43** |

**CA-3 + CA-8 (lo que más vale, y se midió corrompiendo el dato a mano):** se cargó una segunda compra con un producto `Bulto → Metro`, se puso su `FactorConversionAplicado = 0` **directo en la base** (es el único camino por el que puede quedar inválido, porque la carga lo valida) y se intentó recibir.

- Rechazada, con el mensaje nombrando el producto: *"ZZTEST Cable por rollo se compró por bulto y el stock se lleva por metro, pero la línea no tiene un factor de conversión válido..."*.
- **Y nada quedó a medio aplicar**, verificado campo por campo: stock `15,000 → 15,000` y `7,000 → 7,000`, movimientos de CC `1 → 1`, ledger de stock `2 → 2`, estado `Confirmada`. La línea 1 de esa compra (el martillo, que **sí** se podía convertir) **no se movió** — que es el punto del guard previo.

**CA-7:** recibir un `Borrador` → rechazado; recibir dos veces → rechazado ("duplicaría las dos cosas"); cancelar una `Recibida` → rechazado.

#### Casos medidos del paso 5

| Criterio | Medido |
|---|---|
| CA-1: multi-línea, un egreso por línea con su medio | `Egreso 40.000,00 Efectivo` / `Egreso 30.785,00 Transferencia` |
| CA-1b: un `Pago` de CC por línea | `Pago 40.000,00` / `Pago 30.785,00` |
| Mismo `OrigenTipo`/`OrigenId` en los dos ledgers | caja `[3,4]` = cc `[3,4]` |
| Misma fecha y mismo monto | igualdad por `(OrigenId, Monto, Fecha)` |
| CA-2: saldo del proveedor | `70.785 − 70.785 = 0,00` |
| CA-4: no pagar más que el saldo | `$70.786,00` rechazado contra `$70.785,00`; y `$1,00` sobre una compra saldada también |
| `CuentaCorriente` como forma de pago | rechazado con mensaje propio |
| Todas las líneas en cero | rechazado |
| CA-5: reversión por neto vivo | netos antes `CC −40.000,00` / `caja 40.000,00` → después **`0,00` y `0,00`** |
| CA-5: idempotencia por construcción | `RevertirEgresoAsync` sobre un pago ya revertido devuelve **`0,00`** (probado salteando la guarda de `Estado`) |
| Saldo después de revertir | vuelve a `40.000,00` |
| Total pagado excluye el revertido | `30.785,00` |
| CA-6: `LP-009` | día cerrado → *"La caja del día 04/10/2026 ya está cerrada..."*; fecha futura → rechazada |
| CA-7: `LP-002` | `PagoOC` en `Todos`, etiqueta "Pago a proveedor", filtro por origen y búsqueda global por etiqueta: **3 filas** |

`MH-001` cubierto **por ejecución** en las 10 consultas nuevas, **incluido el caso de resultado vacío** (que es donde la regla revienta): 0 excepciones.

#### Guía de pruebas manuales (a ejecutar por el cliente/QA, no por el Implementador)

**Preparación.** `laplatense_dev` no tiene ni un producto con unidad de compra distinta de la de venta: **hay que crear uno** o el camino principal del paso 4 no se ejercita. Producto nuevo con `UnidadVenta = Unidad`, `UnidadCompra = Bulto`, `FactorConversion = 12`, stock conocido.

1. **Conversión.** Compras → nueva, elegir ese producto, cantidad **5**, unidad **Bulto**, precio $12.000. Confirmar → **Registrar recepción** (elegir el día en que entró). El stock del producto tiene que subir **60**, no 5. En el detalle, la card "Lo que entró al stock" tiene que decir `+60,000 unidad`.
2. **Unidad simple.** Mismo flujo con un producto sin unidad de compra: el stock sube la cantidad tal cual.
3. **Factor faltante.** Producto con `UnidadCompra = Bulto` y **sin** `FactorConversion` (o en 0): la línea no se puede ni cargar (lo valida el alta). Para probar el guard de la recepción hace falta el escenario de la tabla de arriba (corromper el factor en la base) — **o** editar la ficha del producto para quitarle el factor después de cargar la compra y antes de recibirla.
4. **Caja no se mueve al recibir.** Mirar el total de egresos del día **antes** de recibir y **después**: tiene que ser el mismo. La deuda sí sube: Proveedores → Cuenta corriente.
5. **No se recibe dos veces / no se cancela una recibida.** Los dos botones tienen que desaparecer y, si se fuerza el POST, el sistema rechaza con mensaje.
6. **Costo sí, precio no.** Anotar `PrecioCompra` y `PrecioVenta` del producto antes de recibir. Después: el costo cambió al de la factura (neto de descuentos y por unidad de stock), el precio de venta **no**, y en Catálogo aparece el badge **"Precio sin recalcular"**. Filtrar por *"Costo actualizado, precio sin recalcular"*: tiene que traer solo esos productos.
7. **Quién apaga la bandera.** Editar el producto y guardar **sin tocar el precio**: el badge sigue. Editar y **cambiar el precio de venta**: el badge desaparece.
8. **Pago multi-línea.** En la compra recibida → **Registrar pago**: dos líneas (parte efectivo, parte transferencia) que sumen el total. Verificar en **Caja** dos egresos con su medio correcto, y filtrar por origen **"Pago a proveedor"**. El saldo del proveedor tiene que quedar en 0.
9. **No pagar de más.** Intentar un importe mayor al saldo pendiente: el botón se deshabilita en pantalla **y** el servidor rechaza si se fuerza.
10. **Reversión.** Revertir una de las dos líneas: la plata vuelve a la caja **con fecha de hoy** y con el **mismo medio**; la deuda sube; el pago queda con badge "Revertido"; el saldo pendiente de la compra vuelve a mostrar lo que falta. Intentar revertir de nuevo: rechazado.
11. **`LP-009`.** Cerrar la caja de un día y después intentar imputar un pago a ese día: rechazado nombrando el cierre.
12. **Anticipo.** Pagar una compra **Confirmada** (sin recibir): el saldo del proveedor queda **negativo** (a favor del negocio). Recibirla después: el `Cargo` lo salda.

#### Riesgos residuales y asunciones

1. **`Proveedor.TipoCambio` NO se aplica, y ahora pesa más.** La recepción convierte **unidades** pero **no monedas**. Si el operador carga una compra de un proveedor en dólares con los precios en dólares, el costo que queda en `Producto.PrecioCompra` **queda en dólares y mal** — y antes esto solo afectaba al total del documento, ahora se persiste en la ficha del producto. El comentario que prometía resolverlo en el paso 4 se corrigió. **Pendiente real, no cubierto.**
2. **El ledger de stock no es el libro mayor.** `Σ MovimientoStock` ≠ `Producto.Stock`: Ventas y el ajuste manual siguen escribiendo el stock sin dejar rastro, y lo histórico no se migró. Cualquier reporte que asuma lo contrario va a dar mal. Unificarlo es una tarea de datos + dos módulos en producción.
3. **Cheques sin cartera.** `Cheque` y `ChequeElectronico` se aceptan y mueven la plata **como si saliera en el momento**, cuando en realidad sale cuando el cheque se cobra. Simplificación declarada; la cartera es el paso 7.
4. **La fórmula fiscal exacta de la compra sigue sin confirmarse** contra una factura real del cliente (viene de una de marihogar). Ahora el `ratioDescuento` de esa fórmula determina el **costo que se persiste en el catálogo**, así que el error se propaga más lejos que antes.
5. **El factor de conversión sigue siendo fijo por producto** (pregunta abierta, sin respuesta del cliente). El snapshot de la línea lo absorbe mientras el operador corrija a mano, pero no lo resuelve.
6. **Recepción siempre total.** No hay parciales. Si llega la mitad de la compra, el operador tiene que elegir entre recibir todo (y el stock queda de más) o nada.
7. **El primer egreso automático del arqueo del cliente.** Ver el aviso de impacto abajo.
8. **Un producto dado de baja entre la carga y la recepción bloquea la recepción completa.** Es deliberado (no se puede ingresar stock a un producto que no existe, y saltearlo dejaría la deuda posteada por mercadería que no entró a ningún lado), pero el operador no tiene salida en pantalla más que cancelar la compra y cargarla de nuevo.

#### Aviso de impacto para el cliente — hay que darlo ANTES del deploy

**Este es el primer módulo que mete egresos automáticos en el arqueo de caja, además de los gastos.** En marihogar, el día que se deployó el equivalente, los egresos del período *"subieron mucho"* de golpe. **No es un bug**: es plata que siempre salió y hasta ese momento no se registraba en ningún lado. Pero si el cliente lo ve primero y pregunta después, el módulo nace con sospecha encima.

### Entrega 3 — ítem 4c (moneda y tipo de cambio) + paso 6 (pagos programados) (2026-10-05, rama `entrega-1-migracion`)

Dos frentes en una ronda. El primero **no era una feature pendiente: era un bug activo**. La ola 2
agregó `Proveedor.Moneda` y `Proveedor.TipoCambio` y **ninguno de los dos se aplicaba en ningún
cálculo** (verificado por grep: 100% de los hits eran persistencia, proyección o pantalla, cero
aritmética). Desde que la ola 3 hizo que la recepción escriba `Producto.PrecioCompra`, una compra
en dólares persistía el costo **en dólares dentro de un campo que todo el sistema lee como pesos**,
y aguas abajo de `PrecioCompra` cuelgan `PorcentajeRecargo` → `PrecioVenta` → `PrecioOferta`.

#### Resultado del escaneo de reutilización

1. **`cat_resumen.txt`**: sin match para moneda/cotización. Lo más cercano es `PAT-052` (línea que
   congela el factor de conversión) — **no es el patrón, es el CRITERIO**, y se copió entero.
   `PAT-053` (un pago, dos ledgers) ya estaba consumido por la ola 3.
2. **Código de `marihogar`**: `TipoCambio`, `Cotizacion` y `Moneda` dan **0 hits** en todo el repo.
   Todo es pesos implícitos, sin campo de moneda en ninguna entidad. **Sin antecedente: la moneda
   se construyó nueva.**
3. **Pagos programados SÍ tienen precedente** y se copió: `PagoOrdenCompraService.RegistrarPagoAsync`
   (programa si la fecha tentativa es futura), `ConfirmarPagoAsync`, `ActualizarFechaPagoAsync` y
   `ObtenerYMarcarPagosVencidosNoNotificadosAsync`. **Lo que NO se copió es su scheduler** (ver
   abajo).
4. **Dos patrones nuevos agregados al catálogo**: `PAT-055` (documento que congela su moneda y su
   cotización) y `PAT-056` (chequeo oportunista al primer request del día en vez de hosted service).

#### Parte 1 — la moneda, de punta a punta

**El modelo.** Tres columnas nuevas en `OrdenesCompra`:

- `Moneda` (enum, default `Peso`) y `Cotizacion` (`decimal(18,4)`, el **mismo ancho** que
  `Proveedor.TipoCambio` para que congelarla no la trunque). Se **precargan** de la ficha del
  proveedor al elegirlo y son **editables**: un proveedor que lista en dólares puede mandar una
  factura en pesos.
- `TotalEnPesos` (`decimal(18,2)`, **persistida**, con índice).

**Por qué `TotalEnPesos` se persiste y no se calcula.** Dos razones concretas, las dos medidas:

1. El `Cargo` de la cuenta corriente y el tope de pago tienen que ser **el mismo número al
   centavo**, o pagar el total no deja el saldo del proveedor en cero (criterio de aceptación 2).
   Recalcular pone una multiplicación y un redondeo en cada consumidor, que es cómo dos de ellos
   terminan difiriendo en un centavo.
2. **El listado ordena por el total del lado del servidor.** Una propiedad calculada en C# no
   traduce a SQL, y ordenar por `Total` mezclando monedas pone una compra de USD 1.000 arriba de
   una de $ 1.500.000. Es la columna que la grilla muestra como principal, así que es la que se
   ordena, se filtra y se busca.

**El punto único: `ConversionMoneda`** (`Application/Helpers/`). Estático, sin dependencias, mismo
rol que `ArgentinaTime` y `OrigenCajaMovimiento`. Tiene:

- `APesos(moneda, cotizacion, importe)` — **una sola fórmula**, un solo redondeo
  (`AwayFromZero`, igual que el resto de la aritmética del módulo). En pesos devuelve el importe
  tal cual e **ignora** la cotización. **LANZA** si la moneda es extranjera y falta la cotización:
  devolver el importe sin convertir "por las dudas" es exactamente el bug que esta ronda cierra.
- `Validar(...)` — la **única** definición de "cuándo hace falta cotización", consumida por las
  **cuatro mitades** de la guarda: alta, edición, confirmación y recepción.
- `Etiquetas` / `Simbolos` / `QueCoincidenConElTexto(...)` — un solo diccionario para el combo de
  filtro, el renderer de la grilla, los símbolos del formulario y la búsqueda global.

**Dónde se aplica.** Los importes del documento (`Subtotal`, `Total`, descuentos, impuestos, el
`PrecioCompra` de cada línea) quedan **en la moneda del documento**: es lo que dice la factura y lo
que el operador tiene delante. Los **tres** importes que salen de la compra van en **pesos**:

| Salida | Antes | Ahora |
|---|---|---|
| `Cargo` en la CC del proveedor | `orden.Total` (en dólares) | `orden.TotalEnPesos` |
| `Egreso` en caja (vía el tope de pago) | contra `orden.Total` | contra `TotalEnPesos` |
| `Producto.PrecioCompra` | el costo en dólares | convertido, una sola vez, al final |

En `RecibirAsync` la conversión va **al final y una sola vez**: el costo acumulado y la cantidad
están los dos en las unidades del documento, así que se divide primero y se convierte después — un
redondeo en vez de dos. El `ratioDescuento` es adimensional (cociente de dos importes de la misma
moneda) y no se toca.

**La guarda y sus cuatro mitades.** Guardar ya exige la cotización, pero eso no alcanza: hay
guardas simétricas en **confirmar** y en **recibir**, que cubren lo que la del alta no puede — un
documento cargado antes de que la columna existiera, o un `UPDATE` directo sobre la base. Sin
ellas, `TotalEnPesos = 0` posteaba una deuda de cero **en silencio**. Y `Validar` rechaza además
`Moneda = 0`, el valor que un POST armado a mano o un combo vacío mandan y que no corresponde a
ningún valor del enum.

#### Parte 2 — pagos programados

El esquema ya existía declarado sin escritor (`Estado = Pendiente`, `FechaPagoTentativa`,
`Notificado`): esta ronda le puso el escritor, **no el esquema** — cero columnas nuevas en
`PagosOrdenCompra`.

**Una línea de pago con `FechaPagoTentativa` estrictamente futura** nace en `Pendiente` y **no
mueve nada**: ni cuenta corriente ni caja. El par de asientos lo postea
`ConfirmarPagoProgramadoAsync`, por el **mismo** `PostearAsientosAsync` que usa el alta inmediata
(dos escritores, un solo lugar que escribe los dos ledgers; el paso 7 será el tercero).

**Tres números distintos y no intercambiables**, cada uno con su método:

- `ObtenerTotalPagadoAsync` — solo `Pagado`. Lo que **efectivamente salió**, y es lo que la cuenta
  corriente refleja.
- `ObtenerTotalComprometidoAsync` — `Pagado` + `Pendiente`. **Es el tope** del alta de un pago
  nuevo: con el primero como tope se podría agendar el total completo tres veces.
- `ObtenerSaldosAsync` — los devuelve juntos, en **una** consulta agrupada por estado (dos
  llamadas separadas podrían leer estados distintos si alguien confirma un pago en el medio).

**La fecha de los asientos es HOY, no la tentativa** (criterio del precedente, su CR-63, un defecto
que le reportó su cliente): la tentativa es una fecha sugerida y confirmar antes o después de ella
es lo habitual, así que imputar la plata al día planeado la mete en un arqueo al que nunca
perteneció.

**Divergencia deliberada del precedente.** Allá la confirmación **pisa** `FechaPagoTentativa` con
la fecha de hoy y deja `PagoOrdenCompra.Fecha` en el instante del registro: el documento y sus
asientos quedan con fechas distintas y **se pierde el plazo que se había pactado**. Acá se hace al
revés — `Fecha` (que está documentada como "el instante en que la plata salió") se reescribe a hoy
y `FechaPagoTentativa` queda **intacta** como registro de lo prometido.

**`ValidarPeriodoAbiertoAsync` (`LP-009`) y su mitad simétrica.** El alta de un pago enteramente
programado **no corre la guarda**, y es a propósito: no mueve un peso, así que exigirle un período
abierto sería impedir agendar un pago futuro porque el mes pasado ya se cerró. El criterio del
proyecto es el que ya decidía que el ajuste manual de CC la saltee: **lo que la hace necesaria es
que el movimiento escriba CAJA**, no que la operación se llame "pago". La **confirmación** sí la
corre, sobre el día de hoy.

#### La notificación: por qué NO hay hosted service (decisión de diseño)

`marihogar` usa un `BackgroundService` + `PeriodicTimer` a hora fija (03:10 ART, con triple
fallback de timezone duplicado en cada job). **No se portó**, por dos hechos del entorno:

1. Este proyecto no tiene **ni un** hosted service (verificado: 0 hits de `AddHostedService`), así
   que portar el patrón no reusa nada — construye una capacidad nueva.
2. Corre en **SmarterASP, donde el application pool se recicla por inactividad**. Un job de las
   03:10 en un sistema que se usa de 8 a 20 **puede no correr nunca** y nadie se enteraría: el
   aviso no llega y no hay ningún error que lo delate. Un scheduler que no se puede garantizar es
   **peor** que no tenerlo, porque se confía en él.

En su lugar: **`AvisoPagosProgramadosMiddleware`**, chequeo oportunista al primer request
autenticado de cada día de negocio argentino. Tres guardas, de la más barata a la más cara: solo
autenticados → un flag estático con el último día procesado (una comparación de `DateTime`, así
que el costo real es **una consulta por día y por proceso**) → y la idempotencia real, que **no es
el flag**.

**La idempotencia la da el mecanismo del precedente que no depende del scheduler**: filtrar
`Estado == Pendiente && !Notificado` y marcar `Notificado = true` **en la misma llamada**, con su
`SaveChanges`. Correrlo dos veces, o dos veces en paralelo, no duplica avisos. El orden importa:
si la garantía viviera en el flag en memoria, **cada reciclado de pool mandaría los avisos de
nuevo**. Y su **mitad simétrica**: reprogramar un pago pone `Notificado = false`, porque la fecha
nueva es un vencimiento nuevo — sin eso, reprogramar lo dejaba marcado como avisado para siempre.

El bloque de notificación va en su **propio try/catch** y no relanza: lo dispara un request del
operador, y que no se pueda crear un aviso no puede tumbar la pantalla que estaba abriendo.

**Si en el futuro hacen falta jobs de verdad, la decisión es DE HOSTING y no de código**:
application pool en `startMode: AlwaysRunning` con Idle Time-out en 0. **Corresponde consultarlo
con `olvidata-infra` antes de escribir un hosted service que el entorno no puede sostener.**

#### El barrido `LP-002` — 7 hallazgos propios

La **pasada 0** (verificar las premisas del brief) confirmó las cuatro: `TipoCambio`/`Moneda` sin
un solo uso aritmético, 0 hits de `AddHostedService`, `INotificationService.CreateAsync` con firma
**idéntica** a la del precedente, y los tres campos del paso 6 ya declarados. **El brief no tenía
premisas falsas esta vez** — es la primera ronda en que la pasada 0 confirma todo.

1. **La resta `Total − TotalPagado` estaba escrita a mano en CUATRO lugares** (el Service, el
   ViewModel del detalle, `RegistrarPago` del controller y `RecargarPagoAsync`) y los cuatro usaban
   `Total`. Con la moneda en el documento, los cuatro pasaron a restar **unidades distintas**:
   dólares menos pesos. Se cerró con `ObtenerSaldosAsync` — **ahora no la repite ninguno**.
2. **El listado ordenaba por `Total` del lado del servidor**, mezclando monedas: la grilla mentía
   por yuxtaposición. Pasó a ordenar y buscar por `TotalEnPesos`, con la moneda como columna
   visible **y su filtro** (regla del proyecto).
3. **`Details.cshtml` mostraba `ProveedorTipoCambio`**, o sea la cotización de HOY de la ficha, en
   una compra vieja: un número que esa compra **nunca usó**. Pasó a mostrar la congelada, con un
   aviso cuando la ficha difiere (`CotizacionDifiereDeLaFicha`) — el aviso es la prueba de que
   congelar sirve, no un error.
4. **El total de las compras en la CC del proveedor** (`Proveedores/CuentaCorriente.cshtml`) estaba
   en la moneda del documento, **al lado de movimientos de ledger que están todos en pesos**.
5. **`OrdenCompraItem.PrecioCompra` decía "en pesos"** en su XML-doc: cierto solo mientras la
   moneda no existía en el documento. Es `LP-008` — regla de negocio falsa viviendo en el repo.
6. **`Views/Proveedores/CuentaCorriente.cshtml` decía que la recepción "es la próxima etapa del
   módulo"**: falso desde el paso 4. Es un texto de la era del paso 3 que la ola 3 no barrió.
7. **La tercera copia del mapa de monedas.** `BusquedaHelper.EnumsQueCoinciden` compara contra el
   **nombre del enum** (`Dolar`), no contra la etiqueta visible (`Dólares`), así que
   `ProveedorService` tenía las dos etiquetas **escritas a mano** al lado de la llamada. Con el
   combo del filtro y el renderer de la grilla, eran **tres copias**. Se cerró con
   `ConversionMoneda.QueCoincidenConElTexto` y las dos líneas hardcodeadas se borraron: **agregar
   una moneda al enum ya no toca ningún call site.** Lo encontró el arnés, no la lectura: la
   consulta *ejecutaba* y devolvía 0 filas.

**Pasada 3 (promesas vencidas)** — 9 correcciones: los 5 lugares de `PagoOrdenCompra` que decían
"DECLARADO, NUNCA ESCRITO (paso 6)", los 2 de `EstadoPagoProveedor`, el de `IPagoProveedorService`,
y el de `DependencyInjection` ("para que los pasos 6 y 7 no vuelvan a armar el egreso inline") —
que ahora dice que **el paso 6 ya lo consumió y entró sin tocar una línea del punto único, que es
exactamente para lo que se había creado**. Más el `Proveedor.TipoCambio` que quedaba como PENDIENTE
DECLARADO y ya no lo es, y la referencia de `AppDbContext` a "la importación de listas (paso 6)",
que ahora no inventa un número de paso.

**Pasada 2 (hermanos semánticos)**: el grep de `DateTime` en entidades sigue dando **34** — esta
ronda **no agregó ninguna columna de fecha**. Lo que sí cambió es la **semántica** de dos que ya
existían, y las dos están declaradas: `PagoOrdenCompra.Fecha` ahora se **reescribe** al confirmar,
y `FechaPagoTentativa` es un **DÍA CALENDARIO sin hora**, no un instante UTC — por eso
`ListarPorOrdenCompraAsync` **no** la proyecta con `ArgentinaTime.From`, que le restaría tres horas
y la correría al día anterior. Verificado por grep que ningún call site la proyecta.

**Pasada 4 (vistas y JS)**: los 9 `toLocaleString` de las vistas tocadas son todos sobre importes,
cantidades, porcentajes y conteos. **Ninguno sobre una fecha** (`LP-006`). Los días hasta el
vencimiento los calcula el **Service** contra el día de negocio argentino, nunca un `new Date()` en
el navegador.

**Pasada 6 (la migración sobre las filas que YA estaban)** — y es el hallazgo más caro de la ronda,
ver abajo.

#### Migración EF — `EntregaTres_MonedaCompraYPagosProgramados`

Aditiva sobre el esquema (3 columnas + 1 índice en `OrdenesCompra`, **ninguna** en
`PagosOrdenCompra`). **Lo que no es aditivo es el dato**, y EF lo deja mal en las dos columnas NOT
NULL:

- **`Moneda` queda en 0**, que no corresponde a ningún valor del enum (el proyecto numera explícito
  desde 1). Es **literalmente el mismo defecto** que la migración de la ola 2 tuvo que repararle a
  85 proveedores.
- **`TotalEnPesos` queda en 0, y eso es PEOR**: es un importe que miente. Toda compra ya cargada
  pasaría a tener saldo pendiente 0 — la pantalla la mostraría como **totalmente pagada**, el tope
  de pago sería 0 así que no se le podría imputar un peso, y recibirla postearía un `Cargo` de
  **$ 0,00** en la cuenta corriente, en silencio.

Los dos `UPDATE` del backfill, con `WHERE` acotado para que correrla dos veces sea inocuo:

```sql
UPDATE OrdenesCompra SET Moneda = 1 WHERE Moneda = 0;
UPDATE OrdenesCompra SET TotalEnPesos = Total WHERE Moneda = 1 AND TotalEnPesos = 0 AND Total <> 0;
```

El índice se crea **después** del backfill. Y el backfill **se verificó ejecutándolo**, no
suponiéndolo: `laplatense_dev` tiene **0 compras**, así que los `UPDATE` no tocaron ni una fila
real — se fabricaron dos filas en el estado exacto post-`defaultValue` (una con total y una con
total 0), se corrieron los dos `UPDATE` literales de la migración, se comprobó con `GROUP BY` que
no quedara ninguna fila en `Moneda = 0` ni ninguna incoherente, se corrieron **otra vez** para
probar que son inocuos, y `ROLLBACK`. **La base quedó en su línea base.**

#### Archivos y capas modificadas

**Domain** — `OrdenCompra` (+`Moneda`, +`Cotizacion`, +`TotalEnPesos`, XML-doc de `Total`),
`OrdenCompraItem` (XML-doc de `PrecioCompra`), `Proveedor` (XML-docs de `Moneda` y `TipoCambio`),
`PagoOrdenCompra` (5 XML-docs), `EstadoPagoProveedor`, `FormaPagoProveedor`.

**Application** — **`Helpers/ConversionMoneda.cs` (NUEVO: el punto único)**,
`Interfaces/IAvisoPagosProgramadosService.cs` (NUEVO), `IPagoProveedorService` (reescrito: +5
métodos), `IOrdenCompraService` (+ filtro de moneda en `ListarAsync`), `OrdenCompraDtos`,
`PagoProveedorDtos` (+`SaldosCompraDto`, +`PagoProgramadoVencidoDto`, +`PagoProgramadoListItemDto`).

**Infrastructure** — `OrdenCompraService` (`AplicarFiscal` congela y convierte, `RecibirAsync`
postea en pesos y convierte el costo, `ConfirmarAsync` guarda, listado), `PagoProveedorService`
(reescrito: alta con programación, confirmación, reprogramación, baja, chequeo de vencidos, 3
saldos), **`Services/AvisoPagosProgramadosService.cs` (NUEVO)**, `ProveedorService` (se le quitó la
tercera copia del mapa), `AppDbContext`, `DependencyInjection`, la migración.

**Web** — **`Middleware/AvisoPagosProgramadosMiddleware.cs` (NUEVO)**, `Program.cs` (lo registra
**después de `UseAuthentication`**, o `context.User` no está poblado y no dispararía nunca),
`OrdenesCompraController` (+3 acciones de pagos programados + la agenda; los saldos salen del punto
único), `OrdenCompraViewModels`, `Views/OrdenesCompra/{Create,Details,Index,RegistrarPago}.cshtml`,
**`Views/OrdenesCompra/PagosProgramados.cshtml` (NUEVO)**,
`Views/Proveedores/{Index,CuentaCorriente}.cshtml`, `_Layout.cshtml`.

**tools/** — `ArnesEntrega3Item4c` (NUEVO, no es parte de la aplicación).

#### Evidencia de build y de ejecución

- **`dotnet build` de la solución: `Compilación correcta. 0 Errores`.**
- **Las vistas Razor SÍ compilan en el build**, probado como cada ronda: se metió un símbolo
  inexistente en `PagosProgramados.cshtml`, el build falló con `CS0103` **con número de línea
  (6,20)**, se revirtió y volvió a compilar limpio. Un build limpio por sí solo no dice nada sobre
  las vistas nuevas.
- **Grafo de DI** validado con `BuildServiceProvider(ValidateOnBuild + ValidateScopes)`. Esta vez
  el arnés necesitó **registrar Identity de verdad** (`AddIdentityCore` + `AddRoles` +
  `AddEntityFrameworkStores`), no stubear: `IAvisoPagosProgramadosService` depende de
  `UserManager<ApplicationUser>` y sin eso **el grafo falla por el arnés y esa falla tapa las del
  código**. Los tres servicios nuevos se resuelven.
- **Los Services ejercitados directamente contra `laplatense_dev`**, idempotente (prefijo `ZZTEST`,
  `LimpiarAsync` al principio y al final), corrido **3 veces**. Cierre: **0 filas de prueba
  restantes, 112.485 productos** (la línea base).
- **`MH-001`: las 7 consultas nuevas o modificadas se EJECUTARON, no se leyeron**, incluidas las
  dos que filtran por colección (`monedas.Contains(...)` en los dos listados) y el caso borde de la
  regla: la búsqueda global con **todas** las colecciones de enum **vacías**. Ejecutar fue lo que
  encontró el hallazgo 7 del barrido: la consulta *andaba* y devolvía 0 filas.
- **Lo que NO se probó**: `INotificationService.CreateAsync` dentro del flujo del aviso y el
  middleware en el pipeline real. Los dos necesitan usuarios con rol y un request HTTP, que es
  navegador — **queda para QA** (pasos 13 a 16 de la guía).

#### Los números medidos de una compra en dólares, de punta a punta

Compra de **10 bultos a US$ 100** (factor 10 → 100 unidades de venta), **10% + 5% en cascada**,
facturada con **21% de IVA**, cotización congelada **$ 1.480,50**:

| Concepto | Medido |
|---|---|
| Subtotal | US$ 1.000,00 |
| Descuento 10% | − US$ 100,00 |
| Descuento adicional 5% (**cascada**: sobre 900, no sobre 1000) | − US$ 45,00 |
| Base imponible | US$ 855,00 |
| IVA 21% | US$ 179,55 |
| **Total del documento** | **US$ 1.034,55** |
| Cotización congelada | $ 1.480,50 |
| **Total en pesos** | **$ 1.531.651,28** |
| **`Cargo` en la CC del proveedor** | **$ 1.531.651,28** (en pesos) |
| **`Egreso` en caja** al pagar el total | **$ 1.531.651,28** (en pesos) |
| **Saldo del proveedor al pagar el total** | **$ 0,00** |
| Stock ingresado | 100,000 unidades |
| **`Producto.PrecioCompra` resultante** | **$ 12.658,28** |

`PrecioCompra` = 855 (base **neta**, sin IVA) × 1.480,50 ÷ 100 unidades de venta. **Antes de esta
ronda ese campo quedaba en `8,55`** — el costo en dólares por unidad, dentro de un campo que el
catálogo lee como pesos. Los 10 criterios de aceptación de las dos partes dieron **OK**.

#### Guía de pruebas manuales (a ejecutar por el cliente/QA, no por el Implementador)

**Moneda**

1. Ficha de un proveedor → moneda **Dólares** + cotización. Nueva compra a su nombre: la cabecera
   tiene que **precargar** las dos, y el panel de total mostrar **"Total en pesos"** con la cuenta
   (`US$ X × $ Y`) a la vista.
2. Cambiar la moneda a **Pesos** en el formulario: el campo de cotización se **oculta y se limpia**,
   y los prefijos `$` de descuentos e impuestos vuelven de `US$` a `$`.
3. Guardar un borrador en dólares **sin cotización**: tiene que rechazarse con el mensaje de la
   moneda, no con un error genérico.
4. Confirmar y **recibir** la compra en dólares. Verificar que el mensaje de éxito muestre la cuenta
   hecha, que la **CC del proveedor** tenga el `Cargo` **en pesos**, y que la ficha del producto
   tenga `PrecioCompra` en pesos y la bandera de precio desactualizado prendida.
5. Pagar el total: el formulario tiene que precargar el importe **en pesos** y el saldo del
   proveedor cerrar en **cero**.
6. **Cambiar `Proveedor.TipoCambio` después** y volver al detalle: la compra no se mueve y aparece
   el aviso de que la ficha difiere.
7. Listado de compras: la columna **Moneda** y su filtro, el total **en pesos** como cifra
   principal, y **ordenar por Total** mezclando una compra en pesos y una en dólares (tienen que
   quedar en orden de pesos, no de número crudo).
8. Buscar **"Dólares"** en el buscador global del listado de compras **y** en el de proveedores.

**Pagos programados**

9. Registrar un pago con **fecha futura**: la pantalla tiene que avisar **en la línea** que queda
   programado, el botón cambiar a **"Programar el pago"** y el pie desglosar qué sale y qué queda
   agendado.
10. Verificar en **Caja** y en la **CC del proveedor** que **no se movió nada**. El detalle de la
    compra tiene que mostrar el badge **Programado** y la fila "Programado sin confirmar".
11. Intentar registrar otro pago sobre esa compra: tiene que rechazarse nombrando lo programado.
12. **Confirmarlo** y verificar que el egreso de caja quedó en **el día de hoy**, no en la fecha
    prevista, y que el aviso del popup lo dijo **de antemano**.
13. **Reprogramar** un pago y **darlo de baja** (el importe tiene que volver a quedar disponible).
14. **`LP-009`**: cerrar la caja de hoy e intentar **confirmar** un pago programado → rechazado. En
    cambio **programar** uno nuevo a futuro tiene que seguir funcionando con la caja cerrada.
15. **El aviso**: dejar un pago programado con fecha de ayer, **cerrar sesión y volver a entrar** al
    día siguiente (o reiniciar el pool). Tiene que aparecer **una** notificación por pago en la
    campana, para `SuperUsuario` y `Administrador`, con link a la compra.
16. **Recargar varias pantallas el mismo día**: no se tienen que duplicar las notificaciones.
17. Menú **Compras → Pagos programados**: la agenda, con los vencidos resaltados y los días hasta el
    vencimiento.

#### Riesgos residuales y asunciones

1. **`laplatense_dev` tiene 0 compras**, así que el backfill de la migración no corrió sobre ni una
   fila real. Se verificó con filas fabricadas y `ROLLBACK`. **Antes del deploy conviene contar las
   filas afectadas en el destino**:
   `SELECT Moneda, COUNT(*) FROM OrdenesCompra GROUP BY Moneda;` y
   `SELECT COUNT(*) FROM OrdenesCompra WHERE TotalEnPesos = 0 AND Total <> 0;` — las dos tienen que
   dar 0 **después** de migrar.
2. **La fórmula fiscal de la compra sigue sin confirmarse** contra una factura real del cliente, y
   ahora el `ratioDescuento` determina el costo que se persiste **en pesos** en el catálogo: el
   error se propaga igual de lejos que antes, solo que ahora en la unidad correcta.
3. **Una cotización mal tipeada contamina el catálogo igual que antes el bug.** La guarda solo exige
   que sea > 0: un 1.480,50 tipeado como 14.805 pasa. Mitigación implementada: la pantalla muestra
   el total en pesos **con la cuenta hecha** antes de guardar y el mensaje de la recepción la
   repite. No hay (ni se pidió) validación contra una cotización de referencia.
4. **El aviso depende de que alguien entre al sistema.** Si la ferretería no abre el sistema un día,
   ese día no sale el aviso — pero tampoco hay a quién avisarle. Es el trade-off explícito contra un
   job que **puede no correr nunca** en este hosting. Si hacen falta jobs de verdad: **decisión de
   hosting, consultar con `olvidata-infra`.**
5. **Un pago programado con `Cheque` no tiene cartera** (paso 7): al confirmarlo la plata sale
   completa en el momento, sin esperar la acreditación. Simplificación declarada y **vigente**.
6. **`PagoOrdenCompra.Fecha` de un pago `Pendiente` es el instante del registro** y no significa
   nada económicamente. Toda consulta de "qué salió en este período" tiene que filtrar
   `Estado == Pagado`; la autoridad de lo que salió de caja es el **ledger de caja**.
7. **El tope de 730 días** para programar un pago no es una regla del cliente: es una guarda contra
   el error de tipeo del año.
8. **La agenda de pagos programados no es un DataTable server-side**, a propósito: son los
   pendientes, un puñado de filas por definición. Si creciera, la regla del proyecto aplica.


## Historial de ajustes
- 2026-10-05 (**Entrega 3, item 4c + paso 6**, rama `entrega-1-migracion`): aplicados la **moneda y la cotizacion de punta a punta** y construidos los **pagos programados**. El item 4c no era una feature pendiente sino un **bug activo**: `Proveedor.Moneda` y `Proveedor.TipoCambio` existian desde la ola 2 y **no se aplicaban en ningun calculo**, asi que desde que la ola 3 hizo que la recepcion escriba `Producto.PrecioCompra` una compra en dolares persistia el costo **en dolares** en un campo que todo el sistema lee como pesos (medido: $ 8,55 donde correspondia $ 12.658,28). La cabecera ahora **declara su moneda y congela la cotizacion** (mismo criterio que `PAT-052` con el factor de conversion) y los tres importes que SALEN de la compra van en pesos por un punto unico nuevo, `ConversionMoneda` — el `Cargo` de la CC, el `Egreso` de caja y el costo del catalogo. `TotalEnPesos` se **persiste** porque el Cargo y el tope de pago tienen que ser el mismo numero al centavo y porque el listado ordena por el total del lado del servidor. Los pagos programados se copiaron del precedente **menos su scheduler**: no se porto su `BackgroundService` a hora fija porque en SmarterASP el pool se recicla por inactividad y un job de las 03:10 **puede no correr nunca** sin que nada lo delate — en su lugar, chequeo oportunista al primer request del dia, con la idempotencia en la marca `Notificado` dentro de la misma llamada que lee las filas, que es el unico mecanismo del precedente que no depende del scheduler. El **barrido `LP-002`** rindio **7 hallazgos propios**, el mas grande que la resta "total - pagado" estaba escrita a mano en **cuatro** lugares y los cuatro pasaron a restar dolares menos pesos; y la **pasada 6** encontro que la migracion dejaba `TotalEnPesos = 0` en toda compra preexistente, que es peor que un enum sin etiqueta: una compra que se muestra como **totalmente pagada** y que al recibirse postea una deuda de **$ 0,00** en silencio. Commit local, **SIN deploy, SIN push**.
- 2026-10-05 (Entrega 3, pasos 1 a 3): implementados **Proveedor ampliado + ABM propio, cuenta corriente de proveedores y ordenes de compra**, sobre la rama `entrega-1-migracion`. Commit local, **sin push y sin deploy** (pedido explicito de Joaquin). Frontera deliberada: **nada toca stock, caja ni cuenta corriente** — la recepcion (paso 4) y los pagos (paso 5) no entran, y `IOrdenCompraService` no expone `RecibirAsync` justamente para que no se pueda llamar por accidente. Reutilizacion del paso 1 del escaneo: `PAT-001` (ledger, port de `marihogar/CCProveedorService.cs` con el camino de vuelta ya recorrido en `MovimientoCCCliente`), `PAT-005`, `PAT-008`/`PAT-016`. Sin antecedente y catalogado como **`PAT-052`**: el modelo de unidad de la linea de compra (`Cantidad` decimal + `UnidadCompra` declarada + factor **congelado** en la linea; en marihogar la cantidad es `int` y la linea no declara unidad). Primer consumidor de `CodigoProveedorProducto` en toda la app (110.683 mapeos que ninguna pantalla leia). **Barrido LP-002 completo con 5 hallazgos propios**, incluido que la premisa del brief era falsa (`Proveedor` tenia CERO consumidores en `Web/`, lo que permitio una migracion estrictamente aditiva y mantener `Nombre` como columna) y que la migracion dejaba los 85 proveedores existentes con `Moneda = 0`, un valor que no existe en el enum. **2 bugs propios encontrados ejecutando** (el neto vivo filtrado por tipo, que devolvia la suma en vez del vigente; y el neto vivo sin acotar por proveedor, que habria mezclado el saldo inicial de todos). Migracion `EntregaTres_ProveedoresCCCompras` aplicada **solo a `laplatense_dev`**. Build limpio y 161/161 checks ejecutados contra dev, con la base devuelta a su linea base. Detalle completo en la seccion "Entrega 3 — pasos 1 a 3" arriba.
- 2026-10-05 (**Sprint 0 - gate de precio por rol en Ventas**, rama `entrega-1-migracion`): cerrado el defecto por el que cualquier usuario con `RequireVentas` podia vender a cualquier precio — `GuardarBorrador` tomaba `PrecioUnitario`/`Descuento`/`Recargo` del formulario y el Service los persistia sin control de rol, abierto en produccion. Se copio el criterio de `marihogar` (CR-22, ya en produccion): un `esAdministrador` resuelto **solo** en el Controller con `User.IsInRole` y pasado al Service como dato explicito del DTO, unica puerta que habilita leer esos campos del payload; para cualquier otro rol el precio se resuelve server-side con `PrecioDeVentaVigente` (oferta vigente por dia de negocio argentino si la hay y es > 0, si no `PrecioVenta`), que es **la misma** resolucion que ya hacia la pantalla, y el descuento y el recargo quedan en 0, descartados **en silencio**. No se trajo de marihogar la cascada de descuento/recargo (el bug corregido el 2026-09-03) ni su manejo de subtotal. El **barrido `LP-002`** rindio dos hallazgos propios: el subtotal c/IVA editable no tiene `name` y por lo tanto el gate de `PrecioUnitario` ya lo cubre (no hacia falta un segundo control), y un **comentario prescriptivo falso preexistente** en `ItemVenta` que declaraba la formula en cascada en dos lugares — el patron de `LP-008`, corregido en la misma pasada. Queda **una deuda explicita para Joaquin**: `Items[].PorcentajeIVA` sigue llegando del cliente para cualquier rol (un vendedor que lo postea en 0 baja el total ~21%), excluido a proposito por el brief de esta ronda. Sin migracion EF. Evidencia ejecutada sin navegador: build limpio, prueba de que las vistas Razor compilan, render del atributo booleano `readonly` verificado ejecutando las tres llamadas que emite Razor, y el Service ejercitado directo contra `laplatense_dev` con los dos roles en una transaccion revertida (15 checks OK, 0 filas sobrevivientes).
- 2026-10-05 (**Sprint 0 - ronda de fixes de QA**, rama `entrega-1-migracion`, commit `00f7dd4`): cerrados los **7 defectos** abiertos por los 3 lotes de QA (`LP-006` a `LP-012`), incluidos los 2 `major` del circuito de dinero que habían dejado el lote 1 en NO-GO. **`LP-009`**: la guarda de caja cerrada miraba solo `CierresCajaDiarios`, así que con el mes cerrado seguían entrando movimientos fechados dentro de ese mes — se centralizó en `ValidarPeriodoAbiertoAsync(dia, accion)`, que consulta mes **y** día y devuelve el mensaje listo para mostrar, y se aplicó en las **6** vías de escritura de caja relevadas (venta confirmada, gasto alta/anulación, cobro de CC, movimiento manual, cierre diario), no solo en la que reportó QA; `RegistrarAjusteAsync` queda afuera a propósito porque por diseño no toca Caja. **`LP-010`**: `Venta.Fecha` pasó al mismo criterio que `CajaMovimiento.Fecha` (instante UTC + día de negocio vía `ArgentinaTime`) en sus 4 puntos de consumo — filtros, proyección del listado, buscador global por fecha y detalle; sin migración de datos, porque la columna ya guardaba UTC correcto y el defecto era de consumo. **Barrido `LP-002` completo** (era la segunda vez en el sprint que quedaba a medias): relevadas las **15** propiedades `DateTime` de `Domain/Entities` con tabla de cierre, y **3 hallazgos propios** corregidos en el mismo commit — `AjusteStock.Fecha`, `Entrega.FechaEntregada` y `ApplicationUser.CreatedAt`. **`LP-007`**: el `default` del `switch` de `continuar` dejó de ser "guardar y listo"; un valor desconocido falla de forma ruidosa aclarando que el borrador se guardó pero la venta NO se cerró (se eligió eso y no un 400 seco, que haría pensar que no se guardó nada), y se corrigió el comentario de `Editar.cshtml` que afirmaba el doble envío `"confirmar,confirmar"` que QA refutó — la guarda de reentrada se queda, con su motivo real. **`LP-008`**: corregidos los comentarios prescriptivos de `ClasificacionAbcAutomaticaService`/`DashboardService` que dejaban la regla de negocio falsa "solo cuentan los Facturada", conservando la parte válida sobre `Borrador`/`Anulada`. **`LP-006`**: helper nuevo `window.Fmt` (`hour12: false`) aplicado en los 8 renders de fecha de las grillas, para que el formato no vuelva a divergir pantalla por pantalla. **`LP-011`**: el rango válido de mes vive ahora en `ArgentinaTime.EsMesDeNegocioValido`, consultado por el GET de la pantalla (donde reventaba al construir el `DateTime`, dejando muerta la validación del Service) y por `CerrarMesAsync`. **`LP-012`**: `PAT-016` aplicado a los 2 listados de cierres (búsqueda global multi-formato + filtros en Session + limpieza real), y cerrado de paso un filtro `anio` muerto que el Service leía y la vista nunca mandaba. **`MH-001` evitado justo donde era el riesgo real del ítem**: el nombre del usuario que cerró vive en `AspNetUsers` sin navegación, y el camino intuitivo era exactamente el `IN` sobre colección local de string — se resolvió con sub-consulta correlacionada (`EXISTS`) y se **verificó la traducción a SQL con `ToQueryString()`**, sin levantar la app ni conectar a ninguna base. Evidencia: build 0 errores (9 advertencias, todas preexistentes), **sin migración EF** (`has-pending-model-changes` confirma que el modelo no cambió) y sin migración de datos. **Producción intacta y el fixture `laplatense_qa_d9` sin tocar.** Los 7 defectos quedan **"aplicado, pendiente de re-verificación"** — el cierre lo declara QA en su corrida siguiente. Detalle completo en la sección "Sprint 0 — ronda de fixes de QA" arriba.
- 2026-10-05 (**Sprint 0 - deuda abierta**, rama `entrega-1-migracion`): cerrados los 4 items previos a la Entrega 3. **0.2 (D8)** ya estaba corregido en `a6a78f0` (nunca deployado): verificado el diff y agregada la guarda de doble envio que faltaba (dos hidden `continuar`, el `switch` caia en el default y la venta se guardaba **sin cerrarse, en silencio**). **0.3 (D9)**: la causa raiz era que `CajaMovimiento.Fecha` tenia **dos semanticas en la misma columna** (instante UTC vs. fecha calendario a medianoche), asi que primero se unifico a instante UTC y se derivo el dia de negocio proyectando a ART; toda la conversion quedo en `ArgentinaTime` (PAT-010 ampliado: `Hoy`, `MesActual`, `DiaDeNegocio`, `InicioDiaUtc`, `RangoDiaUtc/DiasUtc/MesUtc`), cero `DateTime.Today`/`UtcNow.Date` en decisiones de dia/mes y cero conversiones fuera del helper; barrido LP-002 sobre Caja, Gastos, Ventas, CC, Dashboard, Entregas, Productos y vistas; migracion **solo de datos** `D9_NormalizarFechaCajaMovimiento_DiaDeNegocio` (+3h a las filas de medianoche de `Gasto`/`Ajuste`, 4 de 9 en dev). Dos hallazgos propios: el **cierre mensual no tenia ninguna guarda de periodo** (dejaba cerrar el mes en curso y meses futuros; ahora mes anterior si, en curso y futuro no) y `ArgentinaTime.Zone` resolvia la zona con el id de **Windows** unicamente, lo que al volverse la fuente unica de las fechas pasaba de romper una pantalla a romper el **arranque de la app** (se le porto la cadena de fallback de `AfipService`, que ahora reusa el helper). **0.4**: modo `--solo-unidad-venta` que **no toca SQL Server** (retorna antes de abrir la conexion); corrido contra `laplatense_dev`: **87.542 `Metro` a 0**, `Unidad` 24.929 a **112.471**, `Peso` 14 sin cambios, y **2.635 candidatos** a corte por metro listados a CSV sin modificarlos (coincide exacto con lo previsto). Ahi aparecio **MH-001 por quinta vez en el proyecto, en variante nueva**: `Any()` + `EF.Functions.Like` sobre `string[]` local, con mensaje de error distinto y **invisible al grep canonico** de `.Contains(`; la encontro la ejecucion real, no la revision; documentada en `32-estandares`. **0.5**: cobro de CC (Credito + Ingreso en caja en una transaccion, MH-033) y ajuste manual (solo CC, **sin** tocar caja, con motivo obligatorio) sobre la pantalla existente; origen nuevo `"CobroCC"` del ledger propagado al filtro de Caja (LP-002); permisos por precedente de Entrega 2 (cobrar = Vendedor, como al confirmar una venta; ajustar = Administrador, como el movimiento manual de caja); PAT-019 y LP-003 aplicados en el formulario. Evidencia: build 0 errores (verificado que las vistas compilan en el build), grafo de DI validado, 8/8 verificaciones de frontera de dia/mes y **24/24** del cobro/ajuste ejercitadas contra `laplatense_dev` (filas de prueba borradas). **Sin deploy**: lo aprueba Joaquin aparte. **Hallazgo fuera de alcance sin corregir, requiere decision**: `DashboardService` cuenta ventas solo con `Estado == Facturada`, asi que con `Confirmada` como cierre normal el Dashboard va a mostrar cerca de cero. Detalle completo en la seccion "Sprint 0 - Deuda abierta" arriba.
- 2026-08-24 (`PAT-016` en los 6 listados, rama `entrega-2`): implementada la búsqueda global multi-formato (texto + importe + fecha, compuesta vía `extraIds`) y la persistencia de filtros en `Session` en **Ventas, Clientes, Productos, Caja, Gastos y Entregas**. Portado de `delicias-naturales` (`BusquedaHelper.ParsearImportes` + el bloque de `searchValue` de `VentasController.ListarVentas` + la persistencia en `Session` de `ProductosController.Index`) y adaptado a Clean Architecture: helper de parseo en Application, `extraIds` en cada Service de Infrastructure, `Session` en los Controllers de Web. **Sin migración EF ni cambios de Domain** — por eso `LP-002` no aplica. Piezas nuevas: `Application/Helpers/BusquedaHelper.cs`, `Web/Helpers/FiltrosSessionHelper.cs` y el módulo `window.Filtros` en `site.js`. Decisión de escala propia y necesaria: la pasada de substring numérico no se puede resolver en SQL (`MySql.EntityFrameworkCore` no traduce `decimal.ToString()`) y el catálogo tiene ~121.691 productos activos, así que se acotó con `MaxFilasSubstringNumerico = 5000` vía `Take(tope+1)` — sin ese tope, cada tecla en el buscador de Catálogo traía las 121.691 filas; en Productos se acotaron también las sub-queries de valor exacto, porque tipear `0` matcheaba el `Stock` de todo el catálogo. Otras decisiones propias: `Stock` entra por valor pero no por substring; en Entregas se busca `FechaProgramada` (la única visible en la grilla); `InvariantCulture` en el parseo de fecha en vez de `CurrentCulture`; se persiste también el buscador global. Retirado en Clientes y Productos el fallback `texto ?? SearchValue` (ahora son dos cosas distintas, sin pérdida de cobertura). "Limpiar filtros" quedó funcional de punta a punta: vacía controles, vacía el `<input>` del buscador global y manda `limpiar=true` para que el Controller borre las keys de `Session`. Build de la solución en 0 errores. Detalle completo en la sección "PAT-016 — búsqueda global multi-formato + filtros persistidos en Session" arriba.
- 2026-08-21 (cierre same-day: gaps cerrados + rollout a producción): agregada la navegación `Producto.CodigosBarrasAlternos`, simplificado `CodigoBarrasLookupService` a una sola consulta vía esa navegación + agregado `ProductoLookupDto.CodigoEscaneado`, y cerrado el gap del listado de Catálogo (`ProductoService.ListarAsync` busca/muestra alternos, badge `+N` en la grilla). **Bug real encontrado y corregido en `tools/MigracionCatalogo/Program.cs`**: la inserción de `CodigoBarrasProducto` solo existía en el modo correctivo, nunca en el flujo principal de migración — detectado por ejecución real contra `laplatense_dev` (0 filas en la tabla nueva tras una recarga completa). Corregido con una sección nueva (7b) que resuelve `codigosAlternosPorArticulo` contra `productoPorArticuloKey` ya con Id real. Validado en dev (8.276 alternos / 3.865 productos, "Recarga Aromatizador" con sus 22 códigos) y luego **desplegado a producción real**: backup fresco, migración EF aplicada, modo correctivo corrido (mismas magnitudes que dev), verificado por consulta directa, código publicado vía Web Deploy (`HTTP 200` post-deploy). Agregada regla nueva de proceso a Agentes-IA (`LP-002` en `32-estandares-qa-implementador.instructions.md` + checklist en `26-checklists.instructions.md`): toda modificación del modelo de datos requiere relevar y actualizar TODOS los sitios de uso existentes del campo/entidad extendida, en la misma ronda — no solo el punto de entrada del pedido original. Detalle completo en "Código de barras múltiple — gaps cerrados + rollout real a producción" arriba.
- 2026-08-21 (código de barras múltiple por producto, rama `entrega-1-migracion`): implementada la entidad `CodigoBarrasProducto` (1 a N con `Producto`, `SoftDestroyable`, reuse directo del patrón `CodigoProveedorProducto`) para los 4.371 artículos que tienen más de un código de barras real de fábrica y que hoy quedaban sin ninguno por "ambiguos". **Índice único sobre `Codigo` solo, deliberadamente NO compuesto** — a diferencia de `CodigoProveedorProducto`, cuyo único es `(ProveedorId, CodigoDelProveedor)`: un código de fábrica identifica al producto y no puede repetirse entre productos, mientras que un código de proveedor sí puede repetirse entre proveedores. La diferencia quedó documentada en el XML-doc de la entidad nueva. `Producto.CodigoBarras` **sin cambios** (sigue siendo el código propio de la impresora interna, 1 por producto). `ICodigoBarrasLookupService.BuscarPorCodigoAsync` mantiene su firma y solo amplía la búsqueda: resuelve primero por el código propio/interno y recién después por los alternos activos. Ficha de Producto (`Edit.cshtml` únicamente, no `Create.cshtml`): sección de solo lectura "Otros códigos de barras válidos", visible solo si el producto tiene alguno, sin ABM (mismo criterio que los códigos de proveedor). Migración `20260821163451_AgregarCodigoBarrasProducto` generada (aditiva pura, 1 tabla nueva) y **no aplicada a ninguna base**. `tools/MigracionCatalogo/Program.cs` no se tocó — el backfill lo hace Joaquín. Build de la solución en 0 errores. Detalle completo en la sección "Código de barras múltiple por producto" arriba.
- 2026-08-18 (fix del combo de % IVA en Producto, deployado a producción): Joaquín reportó que al editar un producto el combo de IVA mostraba "10,5%" pero el precio ya calculado correspondía a 21%. No era un problema de datos (el dato migrado siempre fue correcto: 111.458/112.485 productos con IVA real 21,00, el resto 10,50) sino de renderizado: `<select asp-for="PorcentajeIVA">` con `<option value="10.5">`/`<option value="21">` hardcodeados — el TagHelper de `asp-for` recalcula la selección comparando el string del valor actual del modelo contra el `Value` de cada `<option>`, y como `PorcentajeIVA` es `decimal(5,2)` el valor real siempre serializa con 2 decimales ("21.00"/"10.50"), que nunca matchea contra "21"/"10.5" — sin ningún match, el navegador cae en la primera opción (10,5%) sin relación con el valor real. Corregido con `ProductoFormViewModel.PorcentajesIVA` (`List<SelectListItem>`) poblado en `ProductosController.PoblarCombosAsync` comparando por valor decimal, y el `<select>` en `Create.cshtml`/`Edit.cshtml` usando `asp-items` **sin** `asp-for` (con "For" presente el TagHelper vuelve a pisar la selección con la misma comparación de string rota). Verificado end-to-end corriendo la app local contra una base de prueba (no solo por inspección de código): GET renderiza el `<option selected>` correcto para IVA=21,00 y para IVA=10,50; POST con `PorcentajeIVA=21` persiste bien. Sin migración ni cambio de datos — deployado solo el código vía Web Deploy. El deploy se retrasó ~40 minutos por una caída transitoria del servicio de administración de Web Deploy de SmarterASP (puerto 8172; el sitio en sí seguía respondiendo `HTTP 200` todo el tiempo) — reintentado hasta que se recuperó.
- 2026-08-18 (deploy real del fix de precios a producción): aplicada la migración `EtapaTres_RecargoYPrecioOferta` contra producción, código republicado, catálogo vaciado y recargado desde cero con el script corregido (0 actividad real que perder, confirmado antes de truncar). Resultado idéntico en cantidades a la corrida anterior más los campos nuevos: 112.435 productos con `PorcentajeRecargo`, 381 con `PrecioOferta` real, 4 con fecha de vencimiento real. **Segundo bug real encontrado en esta corrida** (no en dev, en producción): `PrecioOfertaHasta` se migraba en 65.487 productos sin ningún `PrecioOferta` (el legacy pobla esa fecha también sin oferta activa) — sin impacto funcional (`EsOfertaVigente` exige `PrecioOferta` primero) pero con datos huérfanos; corregido en `Program.cs` y aplicado en producción con un `UPDATE` puntual, verificado 0 huérfanos. Fórmula de precio verificada también contra un producto real ya cargado. Detalle completo en "Deploy real del fix de precios — ejecutado 2026-08-18" arriba.
- 2026-08-18 (modelo de precios de Producto — bug real reportado por el cliente): Joaquín detectó, revisando los precios ya en producción, que el modelo de precios estaba incompleto y que `PrecioConDescuento` no representaba ninguna oferta. Causa confirmada contra el backup del legado: la carga inicial comparaba `PrecioEfectivo` (**con** IVA) contra `PrecioVenta` (**sin** IVA), que casi nunca coinciden → 112.407 de 112.485 productos con un valor sin significado. Fórmula real verificada con filas reales (`PrecioEfectivo = PrecioCompraFinal x (1 + Recargo/100)`, `PrecioVenta = PrecioEfectivo / (1 + IVA/100)`). Agregado `Producto.PorcentajeRecargo` (el margen que faltaba modelar, presente en 121.112 de 121.691 artículos del legado), renombrado `PrecioConDescuento` → `PrecioOferta` y agregada vigencia real (`PrecioOfertaDesde`/`PrecioOfertaHasta` + regla `EsOfertaVigente`); la oferta arranca vacía porque en el legado prácticamente no hay ofertas reales (1.671 de 121.691, y 1.657 de esas con precio 0). `PrecioVenta` se calcula por defecto en el front y sigue siendo editable a mano. **`PrecioCompra` y `Bonificacion` sin cambios estructurales por decisión explícita de Joaquín** — el precio de compra bruto por proveedor menos bonificación real queda diferido al futuro módulo de Compras. Migración `20260818013656_EtapaTres_RecargoYPrecioOferta` generada (rename + 3 columnas nullable + limpieza de los valores inválidos) y **no aplicada a ninguna base**. Build de la solución y del script de migración: 0 errores. Detalle completo en la sección "Modelo de precios de Producto — corrección post-deploy" arriba.
- 2026-08-17 (deploy real a producción): con las 2 decisiones de `entrega-1-migracion` aceptadas, se ejecutó el deploy completo — backup de seguridad de la base real, borrado de 1 producto de prueba que ya existía en producción (confirmado con Joaquín) más sus 3 filas huérfanas de catálogo, migración EF aplicada y verificada, código publicado vía Web Deploy (site en pie, `HTTP 200`), y `tools/MigracionCatalogo` corrido contra la base de producción real. Resultado verificado por consulta directa: 112.485 Productos / 128 Marcas / 16 Categorías / 85 Proveedores / 110.683 códigos / 2.990 Clientes — coincide con dev. Detalle completo en "Deploy real a producción — ejecutado 2026-08-17" arriba.
- 2026-08-17 (rama de producción `entrega-1-migracion`): creada la rama desde `entrega-1` para poder deployar **Etapa 1 + migración de catálogo sin arrastrar la Entrega 2**, que nunca se aprobó para producción y que `migracion-catalogo` incluye entera como ancestro (esa rama se creó desde `entrega-2` porque la migración necesitaba `Cliente`). Se trajo archivo por archivo (no por `cherry-pick`: `71daf36` mezcla `Cliente` de Entrega 2 con `Proveedor`/`CodigoProveedorProducto` de Etapa 3 en el mismo diff) `Proveedor`, `CodigoProveedorProducto`, la extensión de `Producto`, `Cliente` mínimo, `ProveedorService`, la parte de `ClasificacionAbcAutomaticaService` que no depende de Ventas, el fix de Categoría en Stock y `tools/MigracionCatalogo` completo. Generada una migración EF nueva y limpia (`EtapaTres_MigracionCatalogo`, aditiva pura: 3 tablas nuevas + 2 columnas nullable). **Dos decisiones a validar**: `Cliente` queda como tabla sin ABM/servicio/pantalla (solo destino de los datos migrados), y el recálculo por lote de la ABC sugerida se retiró porque agrega `ItemVenta` (sin impacto en el arranque: la ABC inicial la escribe la migración, y "Aceptar sugerencia" se conservó). Build de la solución y del script: 0 errores. **No mergeada a `master`, no pusheada** — queda local para revisión y deploy del orquestador. Detalle completo en la sección "Rama de producción `entrega-1-migracion`" arriba.
- 2026-08-17 (ABC real, no solo sugerida): Joaquín notó que la clasificación de stock por rotación (calculada sobre las ventas reales del backup) no había quedado como clasificación inicial real, solo como sugerencia (`ClasificacionABCSugerida`) — correcto para el recálculo periódico en producción (R10, el cliente clasifica a mano), pero impráctico como arranque: nadie va a aceptar 112.485 sugerencias una por una. Corregido en `tools/MigracionCatalogo/Program.cs`: la migración (bootstrap único, sin clasificación manual previa posible) escribe directo `Producto.ClasificacionABC` con la rotación real calculada — el cliente puede seguir editándola a mano después, igual que siempre. Verificado en dev: 112.485 productos con `ClasificacionABC` real (99 A / 483 B / 111.903 C), sin ningún mismatch contra la sugerida.
- 2026-08-17 (corrección Rubro→Marca/Categoría, pedido de Joaquín tras revisar los datos migrados en dev): Joaquín detectó que lo que el script cargaba como `Categoria` era en realidad nombre de marca/proveedor (ej. "SIBON", "VIOLINI", "SUVINIL") y que la pantalla de Stock (Entrega 1) no muestra/filtra por categoría. Investigado: el legacy no separa categoría de marca de forma limpia — `Rubro` es jerárquico (hasta 5 niveles, `PadreRubroKey`) y el Rubro puntual de cada `Articulo` (el nivel más específico) es en la práctica una marca/proveedor, mientras que la categoría real es la **raíz** de esa cadena (ej. "ferreteria", "electricidad", "sanitarios", "pinturas"). Corregido en `tools/MigracionCatalogo/Program.cs`: `Marca` = nombre puntual del Rubro (antes se intentaba sacar de la tabla `Marca` legacy, que está vacía — 0 filas reales); `Categoria` = raíz resuelta caminando `PadreRubroKey` hacia arriba (función `ResolverCategoriaRaiz`, con protección de ciclos). Re-corrida completa en dev: 128 Marcas (antes 1), 16 Categorías reales (antes 128 nombres de marca disfrazados de categoría) — "ferreteria" 62.857 productos, "electricidad" 8.841, "sanitarios" 8.512, más algunas raíces residuales que también son brand-like (WADFOW, ITURRIA, GAMMA 2024 — limitación real de la data del cliente, no resoluble sin criterio de negocio del cliente). Agregada además la columna y el filtro de Categoría a `Views/Stock/Index.cshtml`/`StockController`/`IAjusteStockService` (gap de Entrega 1 sin relación directa con la migración, detectado en la misma revisión). Build limpio.
- 2026-08-17 (script real de migración, corrido en dev): construido `tools/MigracionCatalogo` (herramienta de consola de una sola corrida, no forma parte de `FerreteriaLaPlatense.Web`) y ejecutada de punta a punta contra `laplatense_dev` con los datos reales del backup restaurado. **Resultado real**: 112.485 Productos, 128 Categorías, 1 Marca (el legacy no tiene ningún dato de marca cargado), 1 Modelo ("Sin especificar", gap real: el legacy no tiene concepto de Modelo), 85 Proveedores, 110.683 `CodigoProveedorProducto`, 2.990 Clientes, 70.808 productos con código de barras asignado sin ambigüedad, clasificación ABC inicial (99 A / 483 B / 111.903 C). 270 excepciones documentadas en un CSV (duplicados resueltos, unidades sin mapeo exacto — Litros/pares/Escalones —, nombres de proveedor/CUIT de cliente duplicados en el legacy). **3 bugs reales encontrados y corregidos durante la corrida** (no por revisión de código — por ejecución real contra el volumen real): (1) `ChangeTracker.Clear()` entre lotes de 500 destrackeaba también a Marca/Categoría/Proveedor (mismo `DbContext`) — EF intentaba reinsertarlas con su Id ya asignado → PK duplicada; se pasó a asignar las FK (`MarcaId`/`CategoriaId`/`ProductoId`/`ProveedorId`) por valor en vez de por navegación. (2) Código de barras y Código de producto duplicados solo por diferencias de mayúsculas/minúsculas — el índice único de MySQL es case-insensitive pero la comparación de string en C# no lo era — pasado a `StringComparer.OrdinalIgnoreCase` en todos los diccionarios/HashSets de deduplicación de código. (3) `Proveedor.Nombre` y `Cliente.CuitDni` duplicados en el legacy (5 y varios grupos respectivamente) sin dedup previa — agregada antes de insertar, mismo patrón que la deduplicación de nombre de `Articulo`. También: timeout de 30s insuficiente contra la tabla de 58,8M filas de `articuloProveedor` → `Command Timeout=600` en la connection string de origen. **No se corrió todavía contra producción** — falta decidir con Joaquín el momento del corte real y si se re-ejecuta la extracción sobre un backup más nuevo antes de esa fecha.
- 2026-08-17 (corrección posterior al QA GO): Joaquín decidió que la carga real del catálogo histórico va por **script directo a la base**, no por la pantalla web recién implementada — al ser una carga de una sola vez, no justifica mantener el flujo subir archivo→preview→confirmar dentro de la app. **Retirados** `ICatalogoMigracionService`/`CatalogoMigracionService`, `MigracionCatalogoController`, `MigracionCatalogoViewModels.cs`, las 4 vistas de `Views/MigracionCatalogo/`, y `CatalogoMigracionDtos.cs` (se rescataron a archivos propios los 2 tipos de ese archivo que sí seguían en uso por `IClasificacionAbcAutomaticaService`/`StockController`: `ResultadoClasificacionAbcDto` → `ClasificacionAbcDtos.cs`, `RecalculoClasificacionAbcViewModel` → `ClasificacionAbcViewModels.cs`). Se sacó también el link del sidebar y la registración en `DependencyInjection.cs`. **Se mantienen** `Proveedor`, `CodigoProveedorProducto`, la extensión de `Producto`/`Cliente`, y `IClasificacionAbcAutomaticaService` completo (con su botón "Recalcular"/"Aceptar sugerencia" en Stock/Productos) — toda esa lógica y esas entidades las va a reutilizar el script de migración real. Build limpio verificado tras la baja (`dotnet build`, 0 errores). No fue necesario tocar la migración EF (`Proveedor`/`CodigoProveedorProducto`/columnas de `Producto`/`Cliente` siguen siendo necesarios independientemente del mecanismo de carga). Próximo paso real: construir el script de migración (herramienta separada, fuera de `FerreteriaLaPlatense.Web`) que lea del backup real (o de la base `LaPlatense_MigracionAnalisis` ya restaurada localmente) y escriba directo contra MySQL, reutilizando las reglas de deduplicación ya diseñadas en `1-analista-funcional.md`/`2-disenador-funcional.md`.
- 2026-08-17: implementados los ítems de app de la **Etapa 3 — Migración de catálogo** (ítems 2 a 6 del WBS, 15h de 27h) sobre la rama `migracion-catalogo`. Entidades nuevas `CodigoProveedorProducto` y `Proveedor` (**versión mínima creada como prerequisito no contemplado en Arquitectura** — su FK no existía porque el módulo de Compras no está implementado); `Producto` extendido con `Bonificacion`/`ClasificacionABCSugerida` y `Cliente` con `Domicilio`/`Localidad`/`Email`/`Notas`. Servicios nuevos `ICatalogoMigracionService` (import preview→confirmar sobre archivo `.xlsx` de 3 hojas, idempotente, con reporte de excepciones paginado y exportable) e `IClasificacionAbcAutomaticaService` (Pareto 80/95 sobre `ItemVenta` en ventana móvil configurable; nunca escribe el campo manual). **Hallazgo relevante: `IListaPreciosProveedorImportService`, que el alcance daba por existente en Entrega 2, no existe en el repo** — el contrato de esta etapa se diseñó desde cero y queda como referencia para cuando se implemente aquel. Reutilización real: `CatalogoSimpleServiceBase` (mismo repo) y el conocimiento de `marihogar/tools/ImportarHistorico` (ClosedXML + escribir entidades directo sin pasar por los Services de negocio). Patrón `PAT-012` agregado a `docs/patrones/catalogo.yml` (renumerado desde `PAT-009` original el 2026-08-18, ver nota más abajo en el historial de ajustes). Migración `EntregaTres_MigracionCatalogo` generada (aditiva pura) y no aplicada. Build limpio. Detalle completo en la sección "Etapa 3 — Migración de catálogo" arriba.
- 2026-08-11: cerrada la segunda mitad de la Entrega 2 (Caja, Gastos, Entregas a domicilio, Dashboard Corte 1) sobre la rama `entrega-2` — **cierra el alcance funcional completo de la Entrega 2 (61h)**. Implementadas las entidades `CajaMovimiento`/`CierreCajaDiario`/`CierreCajaMensual`/`Gasto`/`Entrega`, los servicios `ICajaMovimientoService`/`IGastoService`/`IEntregaService`/`IDashboardService`, y la integración de `VentaWorkflowService` con Caja (guarda de día cerrado antes de facturar + generación de `CajaMovimiento` por cada `PagoVenta` no-CuentaCorriente). El concepto de "cierre" (bloqueo de período) es desarrollo nuevo confirmado sin precedente en el historial. R9 (repartidor ve todas las entregas) respetado explícitamente en `EntregaService.ListarAsync`. Migración `EntregaDos_CajaGastosEntregasDashboard` generada y no aplicada. Build limpio (verificado 2 veces). Detalle completo de archivos/riesgos/pruebas en la sección "Cierre de Entrega 2 — ola 2" arriba.
- 2026-08-11: cerrada la primera mitad de la Entrega 2 (Ventas, CC Clientes, Facturación AFIP) sobre la rama `entrega-2`. Implementadas las entidades `Cliente`/`MovimientoCCCliente`/`Venta`/`ItemVenta`/`PagoVenta`, el workflow `IVentaWorkflowService` (Borrador→Facturada, Anulada modelada pero sin implementar — Entrega 3), `IRecargoCuotasService` (config por appsettings), y el puerto completo de `AfipService`/`IAfipService`/`AfipSettings`/`AfipTokenCache` desde marihogar (mismo circuito WSAA/WSFEv1). Corregida la reutilización documentada en `3-arquitecto-mvc.md`: el ledger de CC cliente se adaptó de `vino-y-se-fue` (no de marihogar), y `Cliente` no persiste columna de saldo (se calcula on-the-fly). Migración `EntregaDos_VentasCCClientesAfip` generada y no aplicada. Build limpio. AFIP queda sin poder probarse de punta a punta hasta que el cliente traiga CUIT real + certificado `.p12`. Detalle completo de archivos/riesgos/pruebas en la sección "Cierre de Entrega 2 — ola 1" arriba.
- 2026-08-10 (17:45, corrección inmediata): Joaquín corrigió el alcance del rol `Administrador` — gestión de Usuarios y Herramientas del Sistema quedan exclusivas de `SuperUsuario`; Administrador conserva el resto (Catálogo/Stock). Revertido `UsersController` a `RequireSuperUsuario` y reestructurado el sidebar en `_Layout.cshtml` (Usuarios/Sistema exclusivos de SuperUsuario, Notificaciones liberado de esa restricción). Sin migración EF.
- 2026-08-10 (17:30, post-QA/GO de Entrega 1): agregado el rol `Administrador` (todo el sistema salvo `SystemController`, exclusivo de `SuperUsuario`) y cambiado el redirect post-login de `Home` a `Stock`. Modificacion puntual sobre la Entrega 1 ya cerrada y en GO, no una entrega nueva. Sin migracion EF. Build limpio. Detalle completo en la seccion "Ajuste puntual (2026-08-10, post-QA/GO)" arriba y en `trazabilidad.md` (entradas 17:00 y 17:30).
- 2026-08-10: Creado el plan de 3 entregas funcionales incrementales sobre el WBS ya aprobado (139h), a pedido explícito de Joaquín para dar dinamismo al proyecto y permitir prueba temprana del cliente. Sin cambios de alcance ni de precio — solo reordenamiento de secuencia de entrega respetando dependencias técnicas. Se adelantó el módulo "Entregas a domicilio" (originalmente Etapa 2/módulo 15) a la Entrega 2 para que el Dashboard Corte 1 (nivel día) pueda mostrar entregas pendientes reales. El Dashboard (12h) se fasea en 2 cortes sin agregar horas: nivel 1+3 en Entrega 2, nivel 2 en Entrega 3.
- 2026-08-10 (cierre Entrega 1): implementados Catálogo (Marca/Modelo/Categoria/Producto), Stock (AjusteStock + alerta visual), Código de barras (lookup service + endpoint de prueba) y roles nuevos (Vendedor/Repartidor). Reutilización de `ShowroomGriffin` (Marca/Modelo/Categoria, AjusteStock/StockController) y `marihogar` (DataTableRequestHelper). Build limpio, migración `EntregaUno_CatalogoStockUsuarios` generada (primera migración real del proyecto) y no aplicada a ninguna base. Ver detalle completo de archivos/riesgos en las secciones arriba.
