# Memoria - Implementador

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-10-06 (v18 - HOTFIX DE TRANSACCIONES PARA PRODUCCION, rama `hotfix-transacciones-ventas` desde `2580f7c`, AMPLIADO por decision de Joaquin a 5 sitios: ConfirmarAsync, FacturarAsync, CancelarBorradorAsync, GastoService.AnularAsync y RegistrarCobroAsync. Backport de `PAT-059` sin migracion EF ni columnas nuevas (`EsReversion` NO se porto: la reversion del gasto va por el monto del documento, con las 3 razones verificadas). HALLAZGO QUE ENCONTRO EL ARNES Y CAMBIA EL PATRON: `ReloadAsync` NO SIRVE como relectura bajo lock para una entidad con soft delete — el filtro global esconde la fila, la entidad queda detached y la relectura PARECE HECHA sin releer; y `Estado` no discrimina porque cancelar solo pone `DeletedAt`. El fix mecanico FALLO el criterio 8 (5 exitos de 8 y una venta borrada CON la plata movida) y se cerro con un helper unico `RelerEstadoBajoLockAsync` (IgnoreQueryFilters + proyeccion de Estado y DeletedAt) que usan los 3 metodos del workflow. Arnes 82/82 OK en 4 corridas, y control positivo de los 3 sitios nuevos: 40 FALLADAS, con una deuda de $1.000 cobrada 8 veces (saldo -$7.000, $8.000 de caja) y +$3.500 de reversiones de gasto que nunca entraron. Commit local, SIN push, SIN deploy. v16 sigue vigente para la rama de desarrollo)

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

### Entrega 4 — Cuenta corriente de empleados (M12) + cuenta corriente del negocio (M13) (2026-10-06, rama `entrega-1-migracion`)

**Frontera de la ronda, y lo que NO se hizo.** Commit local, **SIN push y SIN deploy** (pedido explícito de Joaquín: "no publicar, dejar el desarrollo listo"). La migración se aplicó **solo a `laplatense_dev`**; nada se ejecutó contra `mysql8001.site4now.net` ni contra el fixture `laplatense_qa_d9`. Producción sigue 5 migraciones atrás (6 con esta).

#### Escaneo de reutilización (instrucción 39, sección 3)

Encontrado en el **paso 1** (`cat_resumen.txt`), sin necesidad de llegar al grep dirigido:

| Patrón | Qué aportó | Cómo se usó |
|---|---|---|
| `PAT-001` (ledger) | El molde completo del cuarto ledger | `MovimientoCCEmpleado` es `MovimientoCCProveedor` con otra clave de cuenta: inmutable, no `SoftDestroyable`, saldo calculado, usuario explícito, saldo corrido por fila sobre todo el ledger |
| `PAT-053` (un pago, dos ledgers) | El punto único de egreso | **Tercera aplicación en el estudio y primera sobre sueldos** — el patrón lo preveía textualmente ("también aplica a honorarios, sueldos, comisiones"). `EgresoCCEmpleadoService` es `EgresoPagoProveedorService` con otro `OrigenTipo` |
| `PAT-017` (portal con scoping por identidad) | El modelo de seguridad del autoservicio | **Primera implementación real del patrón en el estudio**: estaba registrado con `pendiente_verificar: true` desde `cma-centro-medico` y la verificación del 2026-09-14 confirmó que `IPortalPacienteService` no existe en ningún repo |
| `PAT-020` / `PAT-051` / `PAT-016` / `PAT-015` | Reversión por neto vivo, medio como dimensión del ledger único, buscador global + filtros en Session, baja/acción AJAX sin perder la página | Aplicados tal cual |

**Lo que NO tiene precedente y se construyó nuevo:** la distinción devengar/pagar como decisión de un solo lugar invocable (`OrigenCCEmpleado.MueveCaja`), la identidad del movimiento para revertir cuando no hay documento (`MovimientoRevertidoId`), el saldo inicial de caja por medio de pago, y el contraste cierre-firmado vs. recálculo.

---

#### Parte 1 — Cuenta corriente del negocio (M13): NO se construyó un ledger nuevo

**La decisión más importante de la ronda, y el nombre del módulo engaña.** En `marihogar` existen `CCLocalService` + `CCLocalController` + `MovimientoCCLocal`, y el mapa de dependencias de ese proyecto es tajante: **`MovimientoCCLocal` ES la caja de marihogar** — su único ledger de dinero, y su `CajaService` no tiene entidad propia, es pura agregación sobre ese ledger.

En La Platense ese ledger **ya existe y se llama `CajaMovimiento`**, y encima tiene cierres diarios y mensuales que marihogar no tiene. Construir un `MovimientoCCLocal` al lado habría sido **duplicar el mismo libro con dos nombres** — y dos libros del mismo dinero es como se descubre, meses después, que ninguno de los dos cuadra. Lo que el presupuesto pide es textualmente *"vista consolidada de cierres de caja, ingresos y egresos"*: **una pantalla de lectura**. Eso es lo que se hizo.

Lo traído de `CCLocalController`: pantalla de ledger con saldo actual, saldo filtrado, listado paginado server-side con **saldo corrido por fila calculado sobre todo el ledger** y filtros por rango de fecha y por origen. Lo propio de acá, que es el valor del módulo: los **cierres diarios y mensuales firmados** como parte de la vista, el desglose por **medio de pago** y el **contraste contra el recálculo**.

**Decisión sobre el saldo inicial — se eligió la opción que resuelve el problema, no la que lo rotula.**

La ola 1 dejó anotado: *"ningún arreglo del flujo hace que el saldo signifique la plata que hay si el punto de partida es un cero inventado"*. Esta pantalla es exactamente donde el cliente va a mirar ese número y creerle, así que la alternativa de poner una leyenda y seguir era dejar el problema intacto con un cartel encima. Se implementó **el saldo inicial declarado por medio de pago** (`OrigenCajaMovimiento.SaldoInicialCaja`), con el mismo shape que el saldo inicial de un proveedor: fecha, motivo obligatorio, usuario, **una sola vez por medio**, y pasando por `ValidarPeriodoAbiertoAsync` (no se puede declarar un punto de partida dentro de un arqueo ya firmado).

**Y las dos cosas a la vez, porque la honestidad no se negocia con la funcionalidad:** mientras NO haya apertura declarada, la pantalla **no llama "saldo" al número**. El rótulo de la tarjeta dice literalmente *"Movimiento acumulado del sistema"* y arriba de todo hay un aviso en amarillo que explica por qué, con el link para resolverlo. Cuando hay apertura parcial, el cuadro por medio marca con un badge **"Sin saldo inicial"** cada cuenta que todavía no la tiene — accionable ("te falta declarar el efectivo del cajón") en vez de una advertencia genérica.

**El criterio de marihogar sobre la apertura SÍ aplica acá, y es lo que hace que no rompa nada.** Su `CajaService` excluye `OrigenTipo = "AjusteApertura"` de los totales del período. Acá la exclusión vive en un solo lugar (`OrigenCajaMovimiento.EsApertura` + el filtro en `ObtenerTotalesRangoUtcAsync` y `ObtenerTotalesPorMedioRangoUtcAsync`) y alcanza a los **seis** lectores de totales: resumen del día, resumen del mes, cierre diario, cierre mensual, arqueo por medio y Dashboard (que consume el resumen del día). Sin esa exclusión, el cierre firmado del día en que se declara el saldo inicial diría que ese día entraron $500.000. **Verificado ejecutando:** declarar una apertura de $500.000 dejó los ingresos del día en $250.000 (sin cambio) y subió el saldo acumulado de $-46.586,20 a $453.413,80.

**Neto vs. bruto: la promesa vencida de la ola 1, encontrada y expuesta en vez de tapada.**

El XML-doc de `CajaMovimiento.EsReversion` (ola 1) promete que con la columna *"el arqueo"* ya puede separar "plata que entró" de "plata que nunca salió". **Nunca se aplicó**: `ObtenerTotalesRangoUtcAsync` suma todos los Ingresos y todos los Egresos ignorando el flag, así que un gasto anulado infla los dos brutos en el mismo importe. Medido en dev: ingresos brutos **$97.415,05** contra netos **$5.914,55**; egresos brutos **$94.001,25** contra netos **$2.500,75**. El saldo es el mismo con los dos criterios ($3.413,80).

**No se cambió el criterio de los cierres** —hacerlo dejaría a los cierres ya firmados sin cuadrar contra su recálculo— y en la pantalla consolidada se muestran **los dos números con el puente entre ellos**: los netos arriba como cifra principal, los brutos abajo rotulados "criterio de los cierres", y el total de reversiones del período que explica la diferencia. Es una decisión pendiente de Joaquín, no un defecto silencioso.

La definición de "neto" es `Σ(Ingreso no-reversión) − Σ(Egreso de reversión)` y simétrica para los egresos: la reversión se descuenta **del lado que deshace**. Es la única definición con la que `ingresos − egresos` da siempre el neto real, incluso cuando el original y su reversión caen en períodos distintos — caso real en dev, donde un gasto del 21/08 se revirtió el 03/09. **Consecuencia correcta y contraintuitiva:** el egreso neto de un período puede ser **negativo** (volvió más plata de la que salió), y la pantalla lo explica en vez de recortarlo a cero.

**Saldo corrido: se copió el patrón de casa y se declaró su costo.** `ObtenerSaldosAcumuladosAsync` materializa `(Id, Tipo, Monto)` de todo el ledger y acumula en memoria, igual que `CCProveedorService`. Es O(n) por draw y está documentado: por eso `ListarConsolidadoAsync` es un método **aparte** y no un flag de la grilla operativa de `Caja/Index`, que se dibuja todo el día. Con ~36.000 filas/año de operación sigue siendo una consulta de milisegundos; si llegara a cientos de miles, la alternativa (suma de prefijo con función de ventana, `SUM() OVER (ORDER BY Fecha, Id)`, que EF no sabe expresar) está escrita en el XML-doc para que se encuentre.

---

#### Parte 2 — Cuenta corriente de empleados (M12)

**Entidad nueva `MovimientoCCEmpleado`**, inmutable, **no** `SoftDestroyable`, mismo molde que `MovimientoCCProveedor`. Semántica idéntica a la de proveedores porque la deuda va en la misma dirección (del negocio hacia afuera): `Cargo` aumenta lo que se le debe al empleado, `Pago` lo reduce, `Saldo = Σ(Cargo) − Σ(Pago)`, positivo = se le debe.

**Devengar no es pagar — la distinción modelada en un solo lugar invocable.** `OrigenCCEmpleado.MueveCaja(origenTipo)` es el único código que declara si un concepto implica plata que sale:

| Concepto | Tipo | ¿Mueve caja? |
|---|---|---|
| Sueldo devengado | `Cargo` (fijo) | **No** — registra la deuda, no el pago |
| Adelanto de sueldo | `Pago` (fijo) | **Sí** |
| Retiro de dinero | `Pago` (fijo) | **Sí** |
| Pago de sueldo | `Pago` (fijo) | **Sí** |
| Ajuste manual | el usuario elige | **No** |

El `_ => false` del switch es el **default seguro a propósito**: un egreso que falta se nota (el arqueo no cuadra contra el efectivo del cajón y alguien pregunta), mientras que un egreso de más por un concepto devengado descuadra la caja en silencio y en la dirección que nadie revisa.

**El `Tipo` lo impone el concepto, no la vista.** `OrigenCCEmpleado.TipoFijo` lo resuelve server-side y el Service lo aplica ignorando lo que postee el formulario. **Verificado ejecutando:** se posteó `Tipo = Cargo` con concepto `Adelanto` (un adelanto que *aumentaría* la deuda con el empleado) y el Service persistió `Pago`. El formulario, además, no pregunta el sentido salvo en el ajuste manual.

**La asimetría de la guarda de período es deliberada.** Solo los conceptos que escriben caja pasan por `ValidarPeriodoAbiertoAsync` (y antes de abrir la transacción, porque si fallara dentro ya habría filas en el change tracker). Un devengamiento retroactivo a un mes cerrado **sí entra**: no escribe caja, así que no hay arqueo que pueda quedar desfasado. Mismo criterio que `ICCProveedorService.RegistrarAjusteAsync`: lo que decide si hace falta la guarda es si el movimiento escribe **caja**, no si escribe este ledger. **Verificado ejecutando:** un `PagoSueldo` fechado 21/08/2026 fue rechazado ("la caja del mes 08/2026 ya tiene cierre mensual") y un `SueldoDevengado` con la misma fecha entró.

**`MovimientoRevertidoId`: por qué el `(OrigenTipo, OrigenId)` de los otros tres ledgers no servía acá.** En caja y en proveedores ese par identifica un **documento** y el neto vivo de ese documento es lo que se revierte. Acá no hay documento: todos los movimientos de un concepto comparten `OrigenId = 0`, así que el neto de `("Adelanto", 0)` sumaría **todos** los adelantos del empleado en un solo número y revertir uno revertiría la plata de los otros. Es el mismo problema que `CCProveedorService.ObtenerNetoVivoAsync` documenta para sus orígenes manuales y que allá se parchea acotando por `ProveedorId` — un parche que acá **no alcanzaría**, porque dos adelantos del mismo empleado seguirían compartiendo clave. Con la columna, el movimiento es su propio documento: `neto(X) = signo(X) + Σ signo(movimientos con MovimientoRevertidoId == X.Id)`.

El neto es **con signo sobre los dos tipos**, no "originales menos reversiones dentro de un tipo" — es la corrección que el ledger de proveedores necesitó tras encontrar el bug ejecutando (un saldo inicial de 100.000 reajustado a 60.000 devolvía 160.000). Efecto colateral deseado: `EsReversion` queda informativo y **no participa de la aritmética**.

**Dos pantallas, dos controllers, y la diferencia es de seguridad.**

- **`MiCuentaController`** (`[Authorize]`, cualquier usuario autenticado). Sus acciones **no declaran ningún parámetro de identidad**: no hay un `usuarioId`, ni un `id`, ni nada que el model binder pueda llenar desde la URL, el query string o el form. El id sale siempre del claim. No es que se valide el parámetro: **es que no existe**, que es la única forma de este control que no se puede romper olvidándose una validación.
- **`CCEmpleadoController`** (`[Authorize(Policy = "RequireAdministracion")]`). Recibe el id de la ruta, y lo que autoriza es la policy de la clase.

Son dos controllers y no dos acciones del mismo por la prescripción de `PAT-017`: así el permiso **se lee en el atributo de la clase** y no hay que auditar acción por acción. Con un controller mixto, una acción nueva a la que se le olvide el atributo hereda el permiso **más permisivo** de la clase — y en este módulo eso significaría exponer la cuenta de todos.

**Mínimo privilegio en la proyección, no en la vista.** El autoservicio pasa `incluirQuienRegistro: false` y el nombre del Administrador que cargó cada movimiento **no sale del servidor** (viaja en `null`). No es que la vista no lo dibuje: es que el dato no viaja.

**La grilla es un partial compartido** (`_LedgerEmpleado.cshtml` + `wwwroot/js/ledger-empleado.js`) porque el requisito dice que la diferencia entre las dos pantallas es de seguridad y **no de presentación** — y la única forma de que eso siga siendo cierto en seis meses es que no haya dos copias del markup. (El JS vive en un `.js` y no en el partial porque un partial de Razor **no puede definir `@section Scripts`**: el bloque no se renderiza y el JS nunca se ejecuta.)

**Listado de empleados: decisión de volumen explícita.** Se resuelve **en memoria** sobre el padrón completo de `AspNetUsers`. Son unidades (4 en dev, una decena en producción), no un padrón de clientes; y la alternativa en SQL exige sub-consultas correlacionadas de **agregación** por fila para poder ordenar y filtrar por saldo, que el provider MySQL traduce de forma impredecible — e "impredecible" en este proyecto ya significó dos 500 por `MH-001`. El saldo se obtiene con **un** `GroupBy` sobre todo el ledger **sin ningún parámetro de colección**, que es de paso la forma `MH-001`-proof de agregar por un string. Documentado en el XML-doc: si el padrón creciera a cientos, lo que hay que cambiar es eso y nada más.

---

#### `MH-001` — el riesgo central de esta ronda, y cómo se cerró

La identidad de la cuenta es un `string` de `AspNetUsers`, y esa tabla **no tiene navegación**: resolver nombres de empleados es **exactamente** el caso que ya explotó dos veces (el `MH-001` original de marihogar y la reincidencia en el buscador de los cierres de caja). Las únicas dos formas permitidas, ambas usadas y cada una documentada en su call site:

1. **Sub-consulta correlacionada** (`_context.Users.Any(u => ...)`), que se traduce entera a SQL.
2. **Materializar `AspNetUsers`** —tabla chica— y filtrar en memoria. Extraído a `CajaMovimientoService.ResolverNombresAsync`, porque desde esta ronda son **cuatro** los lugares que lo necesitan.

Cero `IN`/`Contains`/`Any` sobre colección local de **string** hacia SQL. Las colecciones de `int` (ids de página) y de **enum** (tipos que coinciden con el término buscado) sí se usan, que es el alcance seguro de la regla, y **se ejecutaron igual** para no asumirlo.

#### Barrido `LP-002` — 6 hallazgos

1. **Los seis lectores de totales de caja** no se arrastran solos cuando se agrega un origen. El helper de orígenes propaga el combo y las etiquetas (eso ya estaba resuelto), pero `ObtenerTotalesRangoUtcAsync` y `ObtenerTotalesPorMedioRangoUtcAsync` había que tocarlos a mano o la apertura se habría sumado a los ingresos del día, al cierre firmado y al Dashboard. Anotado en el XML-doc de `OrigenTipo` para la próxima vez.
2. **Las dos consultas de totales tenían que excluir lo mismo.** Si una excluyera la apertura y la otra no, el pie del arqueo dejaría de sumar las tarjetas de arriba y la pantalla se contradiría a sí misma. **Verificado ejecutando:** arqueo del día y del mes siguen sumando su saldo con la apertura cargada.
3. **`CajaMovimiento.UsuarioId` era una columna de solo escritura.** Se persiste desde la ola 1 y **ninguna pantalla la mostraba**. Ahora es la columna "Usuario" de la grilla consolidada.
4. **La "promesa vencida" de `EsReversion`** (ver arriba): la columna existe desde la ola 1, su XML-doc promete que el arqueo puede separar los dos casos, y ningún lector de totales usa el flag. Expuesto en la pantalla consolidada; cambiar los cierres es decisión de Joaquín.
5. **`Dashboard` hereda el cambio sin tocarlo**, porque consume `ObtenerResumenDiaAsync`. Relevado: `CajaHoyIngresos`/`CajaHoyEgresos`/`CajaHoyCerrada`. Los egresos del día van a **subir** cuando se empiecen a cargar adelantos y retiros — aviso de impacto, no bug (ver abajo).
6. **Fuera de alcance, encontrado y NO corregido:** `Views/Clientes/CuentaCorriente.cshtml` sigue con los orígenes **hardcodeados en dos lugares** (el combo y el mapa de etiquetas del JS), con un comentario que admite el riesgo. Es el **único de los cuatro ledgers sin su helper `Origen*`**. No se tocó porque ningún campo de esta ronda lo alcanza y corregirlo obligaría a QA a re-verificar un módulo que no es de esta entrega. **Requiere decisión.**

#### `LP-008` — comentarios y XML-doc corregidos

- `CajaMovimiento` (cabecera): la lista de escritores decía cuatro orígenes y ahora son **siete**, con la declaración de que `SaldoInicialCaja` es el único que no es actividad del período.
- `CajaMovimiento.OrigenTipo`: enumeraba los valores a mano; ahora apunta al helper y advierte qué **no** se arrastra solo (los lectores de totales).
- `CierreCajaDiario`: decía *"se agregan todos los CajaMovimiento de esa fecha"*, que ya no es exacto. Ahora precisa qué entra (reversiones sí, apertura no) y por qué los totales son brutos.
- `CierreCajaMensual`: idem, apuntando al criterio compartido.
- `ObtenerTotalesRangoUtcAsync`: documenta la exclusión de apertura y **declara el límite conocido** del bruto/neto en vez de dejarlo implícito.

#### Hallazgo con datos reales: el cierre mensual de agosto 2026 **no cuadra**, y es anterior a esta ronda

El contraste cierre-firmado vs. recálculo encontró, **la primera vez que se ejecutó**, una inconsistencia real en `laplatense_dev`:

```
Agosto 2026   firmado $ -89.749,25   recalculado $ -92.250,00   diferencia $ 2.500,75
21/08/2026    firmado $ -89.749,25   recalculado $ -89.749,25   diferencia $ 0,00  (cuadra)
```

Causa, verificada por SQL de solo lectura: el cierre mensual se firmó el **2026-08-21 19:05** y el movimiento `#5` (Gasto, Egreso $2.500,75, fecha **2026-08-24**) se creó el **2026-08-25 02:00** — cuatro días **después** de que el mes estuviera firmado.

**Es exactamente el defecto que `LP-009` cerró** (*"con el mes cerrado el sistema seguía aceptando movimientos fechados dentro de ese mes y el arqueo mensual ya firmado quedaba desfasado del ledger real"*, defecto major de QA, Sprint 0 lote 1). La guarda ya existe y **funciona** —se verificó ejecutando que rechaza una imputación nueva a ese mes—, pero esta fila es **residuo histórico** de antes del fix. No es un defecto de esta ronda: es la ronda haciendo **visible por primera vez** una inconsistencia que estaba ahí y nadie podía ver.

**Importa para el deploy:** producción tiene el mismo código viejo que generó esta fila en dev, así que **puede tener el mismo residuo**. No se consultó producción (prohibido en esta corrida). Hay que mirarlo al deployar.

#### Aviso de impacto en los números que el cliente ya mira

Este es el **segundo** egreso automático que entra al arqueo de caja además de los gastos y los pagos a proveedor. Los **retiros de dinero del titular y los adelantos al personal son plata que siempre salió y que hasta ahora no se registraba en ningún lado**: el día que se empiecen a cargar, los egresos del período van a subir de golpe. No es un bug. Es el mismo aviso que se dejó para los pagos a proveedor en la Entrega 3 y que en marihogar se vivió en producción.

#### Cambios por capa

**Domain** (2 nuevos, 3 modificados)
- `Entities/MovimientoCCEmpleado.cs` — **nueva**, ledger inmutable.
- `Enums/TipoMovimientoCCEmpleado.cs` — **nuevo** (`Cargo`/`Pago`, valores explícitos).
- `Entities/CajaMovimiento.cs`, `CierreCajaDiario.cs`, `CierreCajaMensual.cs` — solo XML-doc (`LP-008`).

**Application** (5 nuevos, 3 modificados)
- `Helpers/OrigenCCEmpleado.cs` — **nuevo**: conceptos + etiquetas + `MueveCaja` + `TipoFijo`.
- `Interfaces/ICCEmpleadoService.cs`, `Interfaces/IEgresoCCEmpleadoService.cs` — **nuevos**.
- `DTOs/MovimientoCCEmpleadoDtos.cs` — **nuevo** (4 DTOs).
- `Helpers/OrigenCajaMovimiento.cs` — `CCEmpleado` y `SaldoInicialCaja` + `EsApertura`.
- `DTOs/CajaDtos.cs` — `CajaConsolidadoDto`, `CajaSaldoPorMedioDto`, `CierreCajaContrasteDto`, `CajaMovimientoConsolidadoListItemDto`, `SaldoInicialCajaDto`.
- `Interfaces/ICajaMovimientoService.cs` — 4 métodos nuevos.

**Infrastructure** (2 nuevos, 3 modificados)
- `Services/CCEmpleadoService.cs`, `Services/EgresoCCEmpleadoService.cs` — **nuevos**.
- `Services/CajaMovimientoService.cs` — consolidado, apertura, `ResolverNombresAsync` extraído, exclusión de apertura en los dos helpers de totales.
- `Data/AppDbContext.cs` — DbSet + Fluent API (3 índices, **sin FK a `AspNetUsers`** en las dos columnas de usuario, criterio ya vigente en el proyecto: un empleado dado de baja no debe arrastrar ni ocultar su cuenta corriente, que es inmutable y conserva valor contable).
- `DependencyInjection.cs` — 2 registros `Scoped`.

**Web** (9 nuevos, 3 modificados)
- `Controllers/MiCuentaController.cs`, `Controllers/CCEmpleadoController.cs` — **nuevos**.
- `Models/CCEmpleadoViewModels.cs`, `Models/LedgerEmpleadoPartialViewModel.cs` — **nuevos**.
- `Views/MiCuenta/Index.cshtml`, `Views/CCEmpleado/{Index,Detalle,RegistrarMovimiento}.cshtml`, `Views/Shared/_LedgerEmpleado.cshtml` — **nuevas**.
- `Views/Caja/{Consolidado,SaldoInicial}.cshtml`, `Views/Caja/{_SaldoPorMedio,_ContrasteCierres}.cshtml` — **nuevas**.
- `wwwroot/js/ledger-empleado.js` — **nuevo**, compartido por las dos pantallas de empleado.
- `Controllers/CajaController.cs` — `Consolidado`, `ConsolidadoListar`, `SaldoInicial` (GET/POST).
- `Models/CajaViewModels.cs` — `SaldoInicialCajaViewModel`.
- `Views/Shared/_Layout.cshtml` — "Cuenta del negocio" y "Cuentas de empleados" (Administrador), "Mi cuenta corriente" (**fuera de todo `if` de rol**).
- `Views/Caja/Index.cshtml` — link a la consolidada.

#### Migración EF

`20261006032953_EntregaCuatro_CCEmpleadoYSaldoInicialCaja` — **una sola tabla nueva** (`MovimientosCCEmpleado`) con 3 índices. **Cero cambios sobre tablas existentes**: los dos orígenes nuevos de caja son valores de una columna `varchar(50)` que ya existe. Aplicada solo a `laplatense_dev` y verificada con `SHOW CREATE TABLE`.

#### Evidencia

**Build:** solución completa en **0 errores**, 8 advertencias, **todas `NU1902` preexistentes** de MailKit/MimeKit. Cero advertencias nuevas. Las vistas Razor compilan en el build (el proyecto no usa runtime compilation), así que el build cubre los 9 `.cshtml` nuevos. El JS compartido pasó `node --check`.

**Sonda EF desechable** contra `laplatense_dev` (proyecto consola en el scratchpad, borrado al terminar — **no es un smoke test funcional**: no levanta la app ni prueba por HTTP/navegador; es la evidencia de ejecución real que `MH-001` exige y que un build limpio no cubre). 14 bloques, **~45 verificaciones**, con la línea base calculada por **SQL crudo** y no por el código bajo prueba:

| # | Qué se ejecutó | Resultado |
|---|---|---|
| 0 | Línea base por SQL crudo | 9 filas, saldo $3.413,80 |
| 1 | `ObtenerConsolidadoAsync` (`GroupBy` con enum **nullable** + clave anónima) | **Criterio 1 OK** (saldo == SQL), **Criterio 3 OK** (desglose suma el total), **Criterio 5 OK** (neto == saldo) |
| 2 | `ListarConsolidadoAsync`, páginas 1-2-3 de 3 filas | **Criterio 2 OK**: última fila de la **página 3** = $3.413,80 = saldo de todo el ledger. Y el saldo de la fila #8 es **idéntico con filtro y sin filtro** |
| 3 | Buscador global: 11 términos (origen por etiqueta, medio por etiqueta, badge, importe, fecha, tipo) + filtro `MedioPago IS NULL` | Sin `InvalidOperationException`: ningún `IN` sobre colección de string llegó a SQL |
| 4 | Listado de empleados con roles resueltos + 4 búsquedas | 4 empleados, `MH-001` evitado |
| 5 | Sueldo devengado $900.000 | **Criterio 4 OK**: `CajaMovimientos` 9 → **9** (cero movimientos) |
| 6 | Adelanto $250.000 en efectivo | **Criterio 3 OK**: 1 Egreso exacto, medio Efectivo, cuenta 900.000 → 650.000, **`OrigenId` idéntico en los dos ledgers** |
| 7 | Retiro sin medio de pago | Rechazado |
| 8 | Adelanto posteando `Tipo = Cargo` | Persistió **`Pago`**: el concepto gana sobre la vista |
| 9 | Reversión: neto vivo, dos ledgers, medio arrastrado, segundo intento | **Criterio 5 OK**: netos en 0 en **ambos** ledgers, saldo vuelve a 900.000, medio = Efectivo, segundo intento **no escribe nada** |
| 10 | `PagoSueldo` y `SueldoDevengado` fechados 21/08/2026 (mes cerrado) | **Criterio 6 OK**: el pago rechazado, el devengamiento aceptado |
| 11 | **IDOR** (ver abajo) | **Criterio 2/7 OK** |
| 12 | Saldo inicial: apertura, segunda apertura, apertura en mes cerrado | Apertura fuera de los ingresos del día, dentro del saldo acumulado, desglose sigue sumando, duplicada y en mes cerrado rechazadas |
| 13 | Grilla operativa de Caja + los **7** orígenes + arqueo diario y mensual | Los 7 filtran sin tocar la vista; los dos arqueos siguen sumando su saldo |
| 14 | Las dos grillas de empleado + los 5 conceptos + 8 búsquedas + contraste de los dos ledgers | `TotalPagado` de la cuenta == neto que salió de caja (`PAT-053`) |

**La prueba concreta de que un empleado no puede ver la cuenta de otro (bloque 11).** Se instanció `MiCuentaController` como lo haría un request, con el claim del **Repartidor QA** y el `usuarioId` del **Vendedor QA** inyectado en el form por **tres vías** (`usuarioId`, `id`, `UsuarioId`), y se invocó `Listar()`:

```
movimientos del Repartidor : [10, 6, 7, 9]
movimientos del Vendedor   : [8]
ids devueltos por el endpoint: [10, 6, 7, 9]
```

Devolvió **solo** los 4 movimientos del Repartidor. Ni una fila ajena, y el `RegistradoPorNombre` viajó en `null`. Las cuentas tenían saldos distintos y distinguibles ($901.000 vs. −$50.000), así que la prueba no es vacía. Segunda capa verificada por código: la ruta de administración (`/CCEmpleado/Detalle/{id}`) lleva `RequireAdministracion` **a nivel de clase**, así que un empleado que la intente recibe 403.

**Las 2 verificaciones que fallaron son el mismo hallazgo pre-existente** (el cierre de agosto 2026, ver arriba) — assertions de la sonda que asumían dev consistente, no defectos del código.

**Base devuelta a su línea base exacta:** `CajaMovimientos` 9 filas / saldo $3.413,80 / `MAX(Id) = 9`, `MovimientosCCEmpleado` 0, cierres 1 y 1. Las tablas se respaldaron con `mysqldump` antes de la sonda.

#### Riesgos y supuestos

1. **El saldo sigue sin significar "la plata que hay" hasta que alguien cargue la apertura.** La herramienta está; el dato lo tiene que poner el cliente contando el cajón y mirando los extractos. Mientras no lo haga, la pantalla lo dice con esas palabras.
2. **El cierre de agosto 2026 no cuadra en dev y producción puede tener lo mismo.** Revisar al deployar.
3. **Bruto vs. neto en los cierres firmados**: decisión pendiente (ver arriba).
4. **El listado de empleados se resuelve en memoria.** Supuesto: el padrón es de unidades. Documentado en el XML-doc.
5. **Toda la nómina del sistema es "empleado".** No hay un flag `EsEmpleado` en `ApplicationUser`, así que la pantalla de administración lista **todos** los usuarios, incluido el `SuperUsuario` técnico. Si el cliente quiere separar "personal" de "usuarios del sistema", es un campo nuevo y una ronda aparte.
6. **No hay saldo inicial de arrastre para empleados.** No estaba pedido; el ajuste manual lo cubre. Si hace falta como concepto propio, es una constante más en `OrigenCCEmpleado`.
7. **No hay liquidación de sueldos ni cálculo de haberes.** El módulo registra lo que el Administrador declara; no calcula el sueldo.

#### Pruebas mínimas requeridas para QA

1. **Cuenta del negocio sin apertura**: el rótulo debe decir "Movimiento acumulado del sistema" y el aviso amarillo estar presente. Comparar el saldo contra `SELECT SUM(CASE WHEN Tipo=1 THEN Monto ELSE -Monto END) FROM CajaMovimientos`.
2. **Saldo corrido en la página 3**: paginar a 3 filas por página y confirmar que la última fila de la última página da el saldo total. Después filtrar por un origen y confirmar que el saldo de una fila **no cambia**.
3. **Desglose por medio**: la columna Saldo debe sumar exactamente la tarjeta de saldo acumulado.
4. **Cierres**: deben verse los diarios y los mensuales con su contraste. **Se espera que el mensual de agosto 2026 aparezca en rojo** (hallazgo pre-existente, no un defecto nuevo).
5. **Apertura**: declarar efectivo, confirmar que los ingresos del día **no** cambian y que el saldo acumulado **sí**. Intentar una segunda apertura del mismo medio (debe rechazarse) y una con fecha en un mes cerrado (debe rechazarse).
6. **Devengar vs. pagar**: registrar sueldo devengado y confirmar que la grilla de Caja no suma nada; registrar un adelanto y confirmar el egreso con su medio.
7. **IDOR, a mano**: entrar como Repartidor a "Mi cuenta corriente", abrir la consola y repetir el POST de la grilla agregando `usuarioId=<id de otro>`. Deben seguir viéndose los propios. Y pegar `/CCEmpleado/Detalle/<id>` en la barra: debe dar **403**.
8. **Reversión**: revertir un adelanto, confirmar el contramovimiento en los dos ledgers con el mismo medio, y confirmar que el botón de revertir desaparece.
9. **Período cerrado**: cerrar el día e intentar un adelanto con esa fecha (debe rechazarse); un devengamiento con la misma fecha debe entrar.
10. **Rol `Repartidor`**: el sidebar debe mostrar Dashboard, Entregas, Mi cuenta corriente y Notificaciones, y **nada** de Caja, Cuenta del negocio ni Cuentas de empleados.
11. **`PAT-016`** en los 3 listados nuevos: filtrar, navegar a otra pantalla, volver (los filtros siguen), "Limpiar filtros" los borra de verdad.
12. **Dashboard**: confirmar que los egresos del día incluyen el adelanto cargado.

#### Checklist de salida para merge

- [x] Build de la solución en 0 errores, sin advertencias nuevas.
- [x] Migración EF generada, revisada (una tabla nueva, cero cambios sobre tablas existentes) y aplicada solo a `laplatense_dev`.
- [x] `MH-001`: cero colecciones locales de string hacia SQL; los shapes nuevos **ejecutados**, no supuestos.
- [x] `LP-002`: barrido completo con 6 hallazgos documentados.
- [x] `LP-008`: 5 XML-doc corregidos, incluida una promesa vencida.
- [x] `LP-003`: `InvariantCulture` en los `value` de los 2 formularios nuevos con `<input type="number">`.
- [x] `LP-009` / día de negocio: toda frontera por `ArgentinaTime`; los 2 campos de fecha nuevos declaran su semántica.
- [x] Enums: valores nuevos al final, numerados explícito.
- [x] Lógica de negocio en Services; los Controllers solo resuelven identidad, filtros y binding.
- [x] Design system: `.ov-form-page`, `.ov-page-head`, `.ov-detail-grid`, `.ov-required`, `.ov-field-hint`, `.ov-form-actions`, SweetAlert2 en las 3 acciones destructivas o irreversibles, DataTables server-side con filtro por columna visible, `PAT-016` en los 3 listados.
- [x] Sidebar: entradas por rol, con el autoservicio fuera de todo `if`.
- [x] Base de dev devuelta a su línea base exacta.
- [x] Commit local. **Sin push. Sin deploy. Producción intacta.**
- [ ] **Pendiente de decisión de Joaquín**: bruto vs. neto en los cierres firmados; el cierre de agosto 2026 que no cuadra; el helper `OrigenCCCliente` que falta; si "empleado" debe separarse de "usuario del sistema".

### Ronda de atomicidad y concurrencia — la familia del `LP-018` (2026-10-06, rama `entrega-1-migracion`)

**Origen.** Seis lotes de QA sobre las 6 olas de desarrollo (3 GO, 3 NO-GO) dejaron 4 partes de defecto que **eran una sola cosa**, encontrada por 3 lotes independientes en 4 módulos distintos: *leer, decidir y después escribir, sin nada que lo haga atómico*. `LP-018` (critical, plata revertida dos veces), `LP-023` (major, avisos duplicados), `LP-024` (major, lost update del stock) y `LP-021` (minor latente, el neto sin acotar). Esta ronda cierra esa familia y nada más.

#### Escaneo de reutilización

- **Paso 1 (`cat_resumen.txt`)**: match en `PAT-004` (RowVersion manual para concurrencia optimista en MySQL, origen ShowroomGriffin) y en `PAT-056` (idempotencia en la base, no en el scheduler, origen este mismo proyecto). También `PAT-020` (ledger inmutable + reversión acotada), que es el patrón que esta ronda **corrige en su cláusula de idempotencia** sin tocar el resto.
- **Paso 2**: leída la entrada de `PAT-004` y el código real en `marihogar` (`AppDbContext.OnBeforeSaveChanges` + la config Fluent de `Producto.RowVersion`) y en `ShowroomGriffin`. Las dos rutas de `archivos_referencia` existen y son correctas; ningún `pendiente_verificar` quedó colgado.
- **Decisión**: se reutilizó el **criterio** (la garantía vive en la base, verificada al guardar) y **no la implementación literal** de `PAT-004`. El fundamento está más abajo, en "Lo que NO se hizo y por qué". Se agregó `PAT-059` al catálogo con el patrón nuevo, que es la contracara del antipatrón: *idempotencia por lectura previa, que solo es segura en secuencia*.

#### El mecanismo elegido: `BloqueoDeFila` (`SELECT ... FOR UPDATE`) + relectura

Archivo nuevo: `FerreteriaLaPlatense.Infrastructure/Data/BloqueoDeFila.cs`. Un solo helper, usado igual en los 9 sitios, con el razonamiento completo en su XML-doc. El arreglo es el mismo en todos: **la transacción se mueve de "antes de escribir" a "antes de LEER"**, arranca con el lock de la fila del documento dueño, y después se **relee** el dato sobre el que se decide.

- **Por qué lock de fila y no índice único** (las dos opciones que planteaba el brief): el índice único sobre `(origen, EsReversion)` haría imposible la segunda reversión del mismo origen — y **eso rompe un comportamiento que QA ya verificó**. El neto vivo existe justamente para permitir reversiones **parciales**: $400 primero y $600 después del mismo documento son dos filas de reversión legítimas sobre la misma clave. El lock serializa sin prohibir. (Criterio 4 del parte, preservado y medido.)
- **Por qué no un flag en memoria**: en SmarterASP lo normal es más de un worker process y el pool recicla por inactividad. Un `static` no es una garantía. Es la misma lección que ya estaba escrita en `PAT-056` y que `LP-023` demostró que no se había aplicado donde importaba.
- **La relectura no es un detalle**: sin ella el lock serializa pero igual se decide con el dato de antes de esperar al competidor. En los 9 sitios hay un `ReloadAsync()` (o una lectura que ocurre *después* del lock) explícito y comentado.
- **Orden de bloqueo encapsulado en el helper**, no en los callers: documento primero, productos después y siempre ordenados por Id ascendente. Dos flujos que tomen los mismos productos en orden distinto fabrican un deadlock intermitente, y no quiero que eso dependa de que el próximo caller se acuerde.
- **El helper tira si se lo llama fuera de una transacción**: ahí el lock se libera en el acto y no falla — sería una garantía fantasma, de las que se descubren en producción.

#### Los 4 partes de defecto, aplicados

| id | módulo | qué cambió |
|---|---|---|
| `LP-018` | `VentaWorkflowService.AnularAsync` | Transacción + lock de la venta y de sus productos **antes** de leer `Estado` y los netos vivos; relectura bajo lock; la guarda de permiso se adelantó (no depende de nada concurrente y así un usuario sin permiso no se entera del estado de una venta ajena). |
| `LP-018` | `PagoProveedorService.RevertirPagoAsync` | Lock de la **línea** de pago (no de la compra: el `OrigenId` de los dos ledgers es el Id de la línea — MH-027), relectura del `Estado`, y los **dos** netos vivos (caja y CC de proveedor) leídos ya dentro de la transacción. |
| `LP-018` | `CCEmpleadoService.RevertirMovimientoAsync` | Lock de la fila del movimiento; la lectura del original y de `ObtenerNetoVivoAsync` pasaron a correr después del lock. La transacción ya existía — estaba en el lugar equivocado. |
| `LP-023` | `PagoProveedorService.ObtenerYMarcarPagosVencidosNoNotificadosAsync` | **Reserva** con `SELECT ... FOR UPDATE` sobre las filas candidatas, dentro de una transacción, y marcado antes del commit. El locking read va **sin** el join a `OrdenesCompra` a propósito: un locking read con `LEFT JOIN` bloquea también las filas de la otra tabla, y no hay razón para frenar operaciones sobre una compra porque se está mandando un aviso. La exclusión de compras canceladas se aplica después, en la consulta de EF, que no bloquea nada — y esas filas quedan **sin marcar**, igual que antes. |
| `LP-024` | `AjusteStockService.AplicarAjusteAsync` + `AjusteStockDto.StockEsperado` + `AjusteStockViewModel` + `Views/Stock/Ajuste.cshtml` + `StockController` | **Dos mecanismos, porque son dos carreras distintas** (ver abajo). |
| `LP-021` | `CajaMovimientoService.ObtenerNetoPosteadoAsync` | `origenId <= 0` tira `ArgumentOutOfRangeException`. Los orígenes manuales se postean con `OrigenId = 0` y comparten clave, así que un neto sobre esa clave suma los movimientos de todos y revertirlo sacaría plata ajena. Se rompe fuerte en vez de devolver 0, porque 0 significa "ya está todo revertido" y haría que el caller no postee nada **en silencio**. Verificado que los otros tres ledgers ya estaban acotados (`CCProveedor` por `ProveedorId`, `CCEmpleado` por Id propio del movimiento, `CCCliente` por `VentaId + ClienteId`), así que el único sitio real era el de caja. |

#### `LP-024` — dos carreras, dos mecanismos

1. **Carrera de milisegundos** (venta vs. recepción vs. ajuste, los tres escritores de `Producto.Stock`): lock de las filas de producto del documento, dentro de la transacción, ordenadas por Id. Los tres escritores lo toman, así que el read-modify-write en memoria queda serializado **por producto** y no por catálogo: dos documentos de productos distintos no se esperan.
2. **Carrera de tiempo humano** (el GET muestra "30", el POST llega minutos después con "29"): ningún lock cubre eso — no se sostiene un lock de base esperando que alguien termine de contar. Va concurrencia optimista: `StockEsperado` viaja en un **campo oculto** con el número que la pantalla mostró, y el service lo compara contra el stock real bajo lock. Si no coincide, **rechaza** con un mensaje que nombra los dos números, no aplica el conteo, **no marca `StockVerificado`** y **no escribe la fila de auditoría**.

#### Lo que NO se hizo y por qué — desvío declarado respecto del brief

El brief pedía **portar `Producto.RowVersion` de marihogar, literal**. Se portó el criterio y no la implementación, y la decisión queda para que Joaquín la confirme o la revierta. Tres razones, en orden de peso:

1. **Un token de concurrencia es global al modelo.** `Producto` tiene dos escritores **masivos** que guardan entidades trackeadas por lotes sobre 112.485 filas: `AumentoMasivoPrecioService` y `ClasificacionAbcAutomaticaService`. Con `IsConcurrencyToken()`, **una sola** edición concurrente de un producto aborta el `SaveChanges` del lote **completo** — hoy el aumento masivo rechaza fila por fila y sigue, contando los rechazos. Habría cambiado el comportamiento de dos módulos que QA ya pasó, y habría exigido manejo de conflictos en los dos.
2. **El `RowVersion` compara la cosa equivocada para este caso.** Cambia con **cualquier** columna: una edición de precio o una reclasificación ABC entre el GET y el POST rechazaría un conteo físico correcto, sin ninguna razón de negocio. `StockEsperado` compara el número que el operador vio, que es exactamente lo que el criterio 1 del parte pide.
3. **El propio catálogo ya había escrito este criterio para este proyecto.** La nota de `PAT-004`, del 2026-10-05: *"Cuando el patrón no existe en el proyecto, la salida no es agregar RowVersion a una entidad de 112.485 filas en el medio de otra entrega"*.

**Consecuencia: esta ronda no tiene migración EF.** Ninguna columna nueva, ningún enum nuevo, ningún índice nuevo. Todo el cambio es de código.

#### Barrido `LP-002` — 5 hallazgos propios, y uno peor que el reportado

No se arregló el sitio que reportó QA: se buscó la **forma**. `grep` de los métodos de transición de estado (`Anular|Cancelar|Confirmar|Cerrar|Convertir|Revertir|Marcar`) y, en cada uno, si la lectura que decide está antes o después del `BeginTransaction`.

| sitio | qué pasaba con 2 requests simultáneos | estado |
|---|---|---|
| `VentaWorkflowService.ConfirmarAsync` | **doble** ingreso de caja + **doble** débito de CC + **doble** descuento de stock. La transacción no existía: el método era atómico por accidente (un solo `SaveChanges` al final). | arreglado |
| `VentaWorkflowService.FacturarAsync` | **dos CAE de AFIP** para la misma venta. Dos comprobantes fiscales de un solo hecho económico no se arreglan con una reversión interna: se arreglan con una nota de crédito ante AFIP. | arreglado |
| `OrdenCompraService` (recepción) | **doble** stock + **doble** Cargo de deuda + 2 filas en el ledger de stock. El mensaje de la guarda ya decía *"recibirla otra vez duplicaría las dos cosas"* — faltaba que fuera cierto. | arreglado |
| `PagoProveedorService.ConfirmarPagoProgramadoAsync` | **doble** egreso de caja + **doble** Pago de deuda. Mismo caso: el mensaje lo describía y el código no lo impedía. | arreglado |
| `GastoService.AnularAsync` | **doble** devolución de la misma plata a la caja. | arreglado |
| `PresupuestoService.ConvertirAVentaAsync` | **dos ventas** en borrador del mismo presupuesto, las dos apuntando a él. Si después se confirman las dos, se vende dos veces la misma cotización. | arreglado |
| `CajaMovimientoService.CerrarDiaAsync` / `CerrarMesAsync` | nada: `CierreCajaDiario` tiene índice **único** en `Fecha` y `CierreCajaMensual` en `(Anio, Mes)`. El motor ya impide la doble firma. | **verificado, sin cambio** |
| `EntregaService.MarcarEntregada/NoEntregadaAsync`, `OrdenCompraService.ConfirmarAsync/CancelarAsync`, `PagoProveedorService.CancelarPagoProgramadoAsync`, `VentaWorkflowService.CancelarBorradorAsync`, `PresupuestoService.AprobarAsync/CancelarBorradorAsync` | tienen la forma, pero **no postean plata ni stock**: el peor caso es una transición escrita dos veces con el mismo resultado. | relevado, **no** arreglado (ver pendientes) |

#### `LP-008` — 6 XML-doc corregidos, cuatro de ellos promesas vencidas

El defecto se encontró, en parte, **leyendo comentarios que afirmaban lo contrario de lo que el código hacía**. Corregidos: `IVentaWorkflowService.AnularAsync`, `ICajaMovimientoService.ObtenerNetoPosteadoAsync`, `ICCEmpleadoService.RevertirMovimientoAsync`, `IPagoProveedorService.ObtenerYMarcar...`, `IAvisoPagosProgramadosService`, `IAjusteStockService.AplicarAjusteAsync`, más los comentarios en línea de `GastoService` y `CCEmpleadoService`. En todos el patrón del error era el mismo: *"idempotente por construcción"* / *"imposible por construcción"* / *"correrlo dos veces en paralelo no duplica nada"*, sin calificar que valía **en serie**. Las correcciones dicen qué garantiza el neto vivo (el importe, y las reversiones parciales) y qué garantiza el lock (la exclusión mutua), que son dos cosas distintas.

**Yo escribí la frase equivocada.** En la ronda del 2026-10-05 se le presentó a Joaquín el neto vivo como una garantía por construcción contra la doble reversión. Era falso para el caso concurrente, y el comentario lo repitió en cinco archivos.

#### `MH-001`

El código nuevo no introduce ni un caso. Los dos lugares con `IN` son deliberados y están comentados para que nadie los "arregle": el `IN` de `BloqueoDeFila` es **SQL crudo con parámetros `int`** (no una traducción de LINQ), y el `candidatos.Contains(p.Id)` de la reserva de avisos es `List<int>`, que el provider mapea bien. La regla aplica a colecciones locales de **string**.

#### Evidencia

- **Build**: `dotnet build FerreteriaLaPlatense.slnx` → **Compilación correcta, 0 errores**, 9 advertencias **todas preexistentes** (4× NU1902 de MailKit/MimeKit, 1× CS0114 en `HomeController`, duplicadas por proyecto).
- **Sin smoke test funcional** (no se levantó la app, no se probó por navegador ni por HTTP). En su lugar, **sonda desechable** (proyecto consola en el scratchpad, borrada al terminar) contra un **clon aislado** `laplatense_probe_lp018`, hecho con `mysqldump` de `laplatense_dev`. `laplatense_dev` quedó **intacto** (verificado por conteo: 112.485 productos, 13 ventas, 9 movimientos de caja, 0 ajustes, 0 notificaciones, producto 67 en −11,000 — su línea base exacta). Los 7 clones de QA (`laplatense_qa_l1..l6`, `laplatense_qa_d9`) **no se tocaron**. El clon de la sonda se dropeó.
- **La concurrencia se ejercitó de verdad, con conexiones separadas y barrera de sincronización** — que es el dato de método que explica por qué nadie lo había visto: con un cliente compartido las sentencias se serializan solas y el test da **falso verde**. Equivalente en capa de datos: N scopes de DI independientes (N `DbContext`, N conexiones a MySQL), las N conexiones abiertas **antes** de la barrera, soltadas juntas con un `TaskCompletionSource`, y se cuentan **filas**, no respuestas. **35 afirmaciones, 35 OK.** Las líneas base se calcularon con **SQL crudo**, nunca con el código bajo prueba.

| escenario | N | resultado medido |
|---|---:|---|
| `AnularAsync` sobre la misma venta | 3 | 1 éxito, 2 rechazos *"Esta venta ya está anulada"*; **1** fila de reversión; neto vivo **0,00**; stock devuelto **una** vez (−11 → −1) |
| `AnularAsync` sobre la misma venta | 8 | 1 éxito, 7 rechazos; **1** fila de reversión; neto **0,00**; stock **una** vez |
| `AnularAsync` secuencial (no regresión) | 2 en serie | 1ª anula ($5.163,80), 2ª rechaza explícito; **1** reversión |
| Reversión por **neto vivo**, no por nominal | 1 | con una reversión parcial previa de $1.000 ya posteada sobre la línea de pago, la anulación revirtió **$4.163,80** (el neto) y no $5.163,80 (el nominal); neto final **0,00** |
| `RevertirPagoAsync` (pago a proveedor de $2.500) | 8 | 1 éxito, 7 *"Este pago ya fue revertido"*; **1** fila de reversión **en cada** ledger (caja y CC de proveedor); los dos netos en **0,00** |
| `RevertirMovimientoAsync` (adelanto de $1.800) | 8 | 1 éxito, 7 *"ya fue revertido"*; **1** contramovimiento; neto del ledger **0,00**; **1** reversión de caja, neto **0,00** |
| `GastoService.AnularAsync` (gasto de $3.200) | 8 | 1 éxito, 7 *"ya está anulado"*; **1** reversión; neto **0,00** |
| `LP-023` chequeo de avisos | 8 | devoluciones `[0,0,0,0,0,0,0,8]` → **7 de 8 devuelven 0**; los 4 pagos marcados **una** vez; **8** notificaciones = 4 pagos × 2 destinatarios, **no** 32 |
| `LP-024` GET→POST con stock cambiado | 1 | pantalla mostró 30, entró una recepción de +5, el operador guardó 29 → **rechazado**; stock sigue en **35**; `StockVerificado` sigue en **false**; **0** filas de auditoría |
| `LP-024` camino feliz (no regresión) | 1 | sin carrera el ajuste entra igual: stock 34, verificado, 1 fila de auditoría |
| `LP-024` ajustes simultáneos | 8 | 1 éxito, 7 rechazos; **1** fila de auditoría |

**Nota sobre la cuenta de `LP-023`:** el criterio del parte pedía 4 notificaciones; en el clon hay **2** usuarios en los roles destinatarios, y el diseño es *una notificación por pago y por usuario*, así que el número correcto es 4 × 2 = **8**. Lo que el criterio mide de verdad — que 7 de las 8 llamadas devuelvan 0 y que cada pago se marque una sola vez — dio exacto.

#### Lo que esta ronda NO cierra

- **`LP-024` criterio 2** (`SUM(MovimientosStock)` y `Producto.Stock` no pueden divergir) **no se puede cumplir en esta ronda y no es un defecto de este cambio.** El ledger de stock tiene **un solo escritor**: la recepción de compras. `TipoMovimientoStock` declara `Venta`, `Ajuste` y `AnulacionVenta` *"sin escritor"*, y los movimientos históricos de venta y de ajuste **nunca se migraron hacia atrás** — ya estaba declarado como tarea de datos pendiente en esta misma memoria. El lost update **sí** quedó cerrado (que es lo que hacía crecer la divergencia), pero la suma histórica no va a cuadrar hasta que se decida (a) que los tres escritores posteen al ledger **y** se haga el backfill, o (b) dejar escrito que el ledger es *rastro* y no *libro mayor*, y que el contraste no aplica. **Decisión de Joaquín.**
- **Comprobante AFIP huérfano.** `FacturarAsync` ya no puede emitir dos CAE, pero si el proceso muere **entre** la respuesta de AFIP y el commit, el comprobante existe en AFIP y no en el sistema. Eso no es concurrencia: es una falla parcial contra un tercero, y se resuelve con un estado intermedio *"facturación en curso"* persistido **antes** de llamar (columna nueva + valor de enum nuevo). No se improvisó en una ronda de concurrencia.
- **Costo asumido en `FacturarAsync`**: el lock **se sostiene** mientras AFIP responde. Soltarlo antes dejaría la ventana abierta justo donde dura más. Se bloquea **una** fila, así que ninguna otra venta se entera, pero si AFIP tarda más que `innodb_lock_wait_timeout` (50 s por defecto) un segundo request **sobre esa misma venta** falla con un error de base en vez de un mensaje lindo.
- **Los 7 sitios de la última fila del barrido** (transiciones que no mueven plata ni stock) quedaron relevados y **sin arreglar**, a propósito: el peor caso es una transición escrita dos veces con el mismo resultado. Si se quieren cerrar por consistencia, son 3 líneas cada uno con el helper que ya existe.
- **`OrdenCompraService` (recepción)** y **`PresupuestoService.ConvertirAVentaAsync`** están arreglados y **compilados**, pero **no** ejercitados por la sonda (no había fixtures de compra recibible ni presupuestos aprobados en el clon). El mecanismo es idéntico a los 6 que sí se midieron. **Van en la lista de QA.**

#### Checklist de salida

- [x] `LP-002`: barrido completo, 5 hallazgos propios arreglados + 1 verificado sin cambio + 7 relevados y declarados.
- [x] `LP-008`: 6 XML-doc + 2 comentarios en línea corregidos, cuatro de ellos promesas vencidas.
- [x] `MH-001`: sin casos nuevos; los 2 `IN` deliberados comentados.
- [x] Enums: ninguno nuevo. Migraciones EF: **ninguna**.
- [x] Lógica de negocio en Services; el único cambio en un Controller es pasar `StockEsperado` desde el campo oculto.
- [x] Design system: el único cambio de vista es un `<input type="hidden">`; no se tocó layout.
- [x] Base de dev devuelta a su línea base exacta; clon de la sonda dropeado; clones de QA intactos.
- [x] `PAT-059` agregado al catálogo cross-proyecto; `cat_resumen.txt` regenerado.
- [x] Commit local. **Sin push. Sin deploy. Producción intacta.**
- [ ] Los 4 partes (`LP-018`, `LP-021`, `LP-023`, `LP-024`) quedan **"aplicado, pendiente de re-verificación"**. El cierre lo declara QA en contexto nuevo, con el test de sockets separados por HTTP.
- [ ] **Pendiente de decisión de Joaquín**: (1) el desvío de `RowVersion`; (2) `SUM(MovimientosStock)` vs. `Producto.Stock`; (3) el estado intermedio de facturación AFIP; (4) si se cierran por consistencia los 7 sitios sin plata.


## Hotfix de transacciones de ventas — rama `hotfix-transacciones-ventas` (2026-10-06)

**Esto no es una ola de desarrollo.** Es un hotfix sobre el estado exacto de producción, en una rama
propia creada **desde el commit `2580f7c`** — lo que está publicado hoy en
`ferreterialaplatense.com.ar` — y **no** desde `entrega-1-migracion`, que tiene 7 commits de
desarrollo encima que no se pueden publicar. El deploy lo ejecuta Joaquín después de que QA
re-verifique; esta ronda **no tocó producción** (ni Web Deploy ni `mysql8001.site4now.net`).

### Por qué existió

El código publicado tenía **cero** `BeginTransaction` en `VentaWorkflowService` (verificado:
`git show 2580f7c:...VentaWorkflowService.cs | grep -c BeginTransaction` → `0`). `ConfirmarAsync`
descontaba stock, posteaba el movimiento de caja y debitaba la cuenta corriente del cliente con
escrituras separadas, decidiendo sobre una lectura sin lock. `FacturarAsync` tenía la misma forma y
podía emitir **dos CAE de AFIP por la misma venta** — hoy inalcanzable porque la facturación está
deshabilitada por falta de certificado, pero un comprobante fiscal duplicado no se corrige: se anula
con nota de crédito, que todavía no existe.

Producción no tiene daño hecho (se borraron los datos de prueba y quedó en cero transacciones). El
riesgo se materializaba en la **primera venta real del cliente**.

### Reutilización: paso 1 del escaneo, hit directo

`docs/patrones/cat_resumen.txt` → **`PAT-059`** ("Idempotencia por lectura previa: el patrón que solo
es seguro en secuencia (lock de fila del documento dueño)"), catalogado en esta misma ronda de
`bdfd99b`. El mecanismo se **portó del commit `bdfd99b`** de `entrega-1-migracion`, que es el mismo
repo: `FerreteriaLaPlatense.Infrastructure/Data/BloqueoDeFila.cs`, autocontenido y sin dependencias
de las olas de desarrollo. **No se agregó entrada nueva al catálogo** — `PAT-059` ya documenta el
patrón completo y este hotfix es su segundo consumidor, en la rama de producción.

**Lo que se adaptó y por qué** (no fue copiar y pegar): el `BloqueoDeFila` de `bdfd99b` declara 7
constantes de tabla, y en producción **solo existen 3** (`Ventas`, `Gastos`, `Productos`);
`Presupuestos`, `OrdenesCompra`, `PagosOrdenCompra` y `MovimientosCCEmpleado` **no existen**. Se
dejaron las **dos** que este hotfix bloquea. Y el XML-doc de la clase se reescribió: el original
fundamenta la decisión contra el índice único hablando de las **reversiones parciales de
`AnularAsync`**, método que **no existe en producción** (llegó en `59dd715`, posterior). Copiar ese
texto habría plantado un comentario prescriptivo que describe código ausente — exactamente el
defecto `LP-008` que el barrido `LP-002` existe para cortar.

### Alcance: estrictamente dos métodos

`ConfirmarAsync` y `FacturarAsync`. **No** entró el resto de la familia `LP-018` (`AnularAsync`,
pagos a proveedor, CC de empleados, recepción de compra, conversión de presupuesto, aviso de pagos
programados): no existe en producción o pertenece a código no publicado. **No** entró `LP-024` (lost
update del stock del ajuste manual): es real, pero su exposición es mucho menor y mezclarlo agranda
la superficie de un hotfix que tiene que ser auditable de un vistazo.

### Cambios por capa

| Capa | Archivo | Motivo |
|---|---|---|
| Infrastructure / Data | `BloqueoDeFila.cs` (**nuevo**, 2 constantes) | `SELECT ... FOR UPDATE` por Id, deduplicado y ordenado por Id asc (prevención de deadlock encapsulada); tira `InvalidOperationException` si se lo llama fuera de transacción, porque ahí el lock se libera solo y la garantía sería fantasma. |
| Infrastructure / Services | `VentaWorkflowService.ConfirmarAsync` | Transacción abierta **antes de LEER**; lock de la venta y de los productos de esa venta; relectura bajo lock de `Estado` y de cada `Producto.Stock`; `CommitAsync` tras el `SaveChanges` que ya existía. |
| Infrastructure / Services | `VentaWorkflowService.FacturarAsync` | Lo mismo con el lock de la venta, **sostenido durante la llamada a AFIP** a propósito, con el costo declarado en el comentario. |

**Migraciones EF: ninguna.** El hotfix no toca el modelo. Es lo que lo hace deployable sobre la base
de producción tal como está.

**Diff: 3 archivos, +93 líneas, 0 borradas.** Puramente aditivo; de esas líneas **20 son código** y
el resto fundamento. Ningún Controller, ninguna vista, ningún contrato de interfaz.

### Las DOS premisas del brief que se refutaron ejecutando (pasada 0 del barrido `LP-002`)

Las dos venían del brief con toda la razón aparente, y las dos son **falsas**. Importa porque las dos
habrían quedado escritas como comentario prescriptivo en el código publicado.

1. **"Una falla en el medio deja la venta a mitad: stock descontado sin plata registrada."** Falso.
   El método tenía **un solo `SaveChangesAsync` al final** (ni `RegistrarMovimientoAsync` de caja ni
   el de CC persisten por su cuenta) y **EF envuelve cada `SaveChanges` en una transacción
   implícita**. Verificado abortando el `INSERT` de caja con un trigger `SIGNAL SQLSTATE '45000'`:
   **el criterio 2 pasa también contra el código roto** — venta en `Borrador`, stock intacto, 0
   movimientos. El método era **atómico por accidente**. La transacción explícita lo vuelve atómico
   por construcción y, sobre todo, es lo único que habilita el lock.
2. **"Dos requests concurrentes duplican las tres cosas, incluido el descuento de stock."** Las dos
   de plata sí, deterministas. El stock **no se duplicaba: se perdía.** Los dos competidores leían
   `Stock = 100`, los dos escribían `98`, y el resultado coincidía con el correcto **por
   casualidad** (lost update que se tapa solo). Medido en 3 corridas contra el código roto: siempre
   `98`. Con otro entrelazado daría `96`. No es una garantía, es el resultado de una carrera — y el
   lock sobre los productos lo cierra igual.

**Las dos quedaron escritas en el código**, en el comentario de `ConfirmarAsync`, como "lo que **no**
estaba roto", para que la próxima ronda no venga a "arreglar" una atomicidad que ya existía ni a
buscar una duplicación de stock que nunca se vio.

### Evidencia ejecutada

Build de la solución: **0 errores**, 9 advertencias **todas preexistentes** (`NU1902` de
MailKit/MimeKit y el `CS0114` de `HomeController`). Sin advertencias nuevas.

**Arnés de concurrencia: `tools/ArnesHotfixTransacciones`** (proyecto propio, **fuera** de
`FerreteriaLaPlatense.slnx`, así que no entra al build de la solución ni se publica). Queda en el
commit, es idempotente (prefijo `ZZHOTFIX`, `LimpiarAsync` al principio y al final) y **QA lo puede
re-correr**. Corre contra `laplatense_hotfix_tx`, un clon con las **8 migraciones exactas de
`2580f7c`**, y tiene una **guarda que aborta** si la cadena de conexión menciona `laplatense_dev`,
`laplatense_qa` o `site4now` — atiende la observación que QA levantó del arnés de la ronda anterior,
que apuntaba a `laplatense_dev` hardcodeado y escribía la base compartida.

**Método**: un scope de DI por competidor (un `AppDbContext` y una **conexión MySQL** propia), la
conexión **abierta antes** de la barrera para que el handshake no se cuele en la ventana medida, y
`Barrier.SignalAndWait()` para largarlos juntos. Con un cliente HTTP compartido las requests se
serializan y el test da **falso verde**.

**46 afirmaciones, 46 OK**, corrido 3 veces. Escenario: 2 unidades × $1.000 + IVA 21% = Total
**$2.420**; pagos Efectivo **$1.420** (va a caja) + Cuenta Corriente **$1.000** (va al ledger);
stock 100 → 98. Números elegidos para que ningún importe duplicado coincida con otro valor legítimo.

| Criterio | Resultado |
|---|---|
| 1 — N simultáneos, un solo cierre (**N=3 y N=8**) | 1 éxito de N, **1** ingreso de caja ($1.420), **1** débito de CC ($1.000), **1** descuento de stock (98), 0 excepciones, los N−1 restantes con rechazo explícito |
| 2 — falla de caja/CC, nada persistido | venta en `Borrador`, 0 caja, 0 CC, stock 100 intacto; y el **reintento posterior confirma bien** y deja un solo cierre |
| 3 — secuencial sin regresión | total $2.420, caja $1.420, CC $1.000, stock 98, estado `Confirmada` |
| 4 — confirmar una ya confirmada | rechazo explícito y **no escribe nada** |
| 5 — `FacturarAsync` (**N=3 y N=8**) | 1 éxito de N y **AFIP invocado UNA sola vez**; un solo CAE persistido; caja/CC/stock sin retocar |

**La verificación que vale más que las 46**: el arnés se corrió **contra el código roto** (revirtiendo
el service a `2580f7c` y dejando el arnés igual) y dio **12 fallas / 34 OK**, reproduciendo el
defecto con números: con N=8, **2 éxitos**, **2** movimientos de caja por **$2.840** y **2** débitos
de CC por **$2.000**; y `FacturarAsync` con N=8 **emitió 8 comprobantes AFIP** (8 de 8 éxitos, 8
invocaciones). Un arnés verde que no se probó contra el defecto no prueba nada: podría estar verde
porque no mide.

### Pendiente declarado en el código, no resuelto: comprobante AFIP huérfano

Si el proceso muere **entre la respuesta de AFIP y el commit**, el CAE existe en AFIP y no en el
sistema: la venta queda `Confirmada` y reintentar emitiría un **segundo** comprobante del mismo hecho
económico. **No es concurrencia** — el lock no lo cubre y no puede cubrirlo — es una falla parcial
contra un tercero. Lo que falta: un estado intermedio **persistido** antes de llamar ("facturación en
curso": columna nueva + valor de enum + migración) y que el reintento consulte a AFIP
(`CompConsultar`) en vez de emitir a ciegas. **Fuera de alcance acá y con fundamento**: AFIP está
deshabilitado, así que el camino no se puede ejecutar en producción, y un estado nuevo con migración
no entra en un hotfix. Queda escrito en el XML-doc de `FacturarAsync` con la frase **"el día que se
cargue el certificado esto hay que resolverlo ANTES de habilitar la facturación"**, para que no se
descubra de nuevo.

### Guía de pasos para verificación manual (el Implementador no corre smoke por navegador)

1. Cargar una venta en `Borrador` con al menos un ítem y un pago en efectivo, y confirmarla.
   Controlar que el ingreso de caja, el total y el stock sean **los mismos** que antes del hotfix.
2. Confirmar una venta que ya está `Confirmada`: tiene que dar rechazo explícito y **no** mover nada.
3. El caso que motiva el hotfix: **doble click real** en Confirmar (o `Confirmar y facturar`) sobre
   la misma venta. Tiene que quedar **un** ingreso de caja, **un** débito de CC y **un** descuento de
   stock. Antes del hotfix quedaban dos.
4. Una venta con pago a cuenta corriente: el débito tiene que aparecer **una** vez en el ledger del
   cliente y **no** como ingreso de caja.
5. Arqueo de caja del día: el total no puede tener movimientos repetidos del mismo `OrigenId`.
6. Re-correr el arnés si se quiere la medición de concurrencia:
   `dotnet run --project tools/ArnesHotfixTransacciones` contra un clon propio (**nunca** contra
   `laplatense_dev`; el arnés aborta solo si se lo intenta).

### Checklist de salida para merge

- [x] Rama `hotfix-transacciones-ventas` creada **desde `2580f7c`**, no desde `entrega-1-migracion`.
- [x] Alcance estricto: `ConfirmarAsync` y `FacturarAsync`. Nada más tocado.
- [x] Lógica en Services; cero cambios en Controllers, vistas e interfaces.
- [x] **Sin migración EF**: deployable sobre la base de producción tal como está.
- [x] Diff aditivo de 3 archivos (+93/−0), 20 líneas de código.
- [x] Build 0 errores; 9 advertencias, todas preexistentes.
- [x] Concurrencia medida con conexiones separadas y barrera: 46/46 OK, y **arnés validado contra el
      código roto** (12 fallas).
- [x] `laplatense_dev` sin tocar; clones `laplatense_qa_l1..l6` y `laplatense_qa_d9` **intactos**;
      clon propio `laplatense_hotfix_tx`.
- [x] Producción sin tocar: ni Web Deploy ni `mysql8001.site4now.net`.
- [x] `PAT-059` reusado (paso 1 del escaneo); sin entrada nueva al catálogo.
- [x] Commit local. **Sin push. Sin deploy.**
- [ ] Queda **"aplicado, pendiente de re-verificación"**. El cierre lo declara QA en contexto nuevo,
      con el test de sockets separados por HTTP.
- [ ] **Pendiente de decisión de Joaquín**: (1) el estado intermedio de facturación AFIP, antes de
      cargar el certificado; (2) si este hotfix se mergea hacia `entrega-1-migracion` o se descarta
      ahí (el mecanismo ya está en `bdfd99b`, así que el merge va a colisionar en los dos métodos);
      (3) el desfasaje de migraciones de producción descripto abajo.

### Riesgo de deploy que no es de este hotfix pero lo condiciona

La memoria del proyecto dice que **producción está cinco migraciones atrás**, y dos de las que lista
(`EntregaTres_ConfirmarSinFactura_RecargoCuotas_NotaPago` y
`D9_NormalizarFechaCajaMovimiento_DiaDeNegocio`) **sí están en `2580f7c`**, que es lo que el brief
declara publicado. O el código publicado no es exactamente `2580f7c`, o la base de producción está
atrás de su propio código. **No se consultó producción** (estaba prohibido), así que queda como
condición a verificar **antes** del deploy: `SELECT MigrationId FROM __EFMigrationsHistory` contra
producción, comparado con las 8 migraciones de esta rama. Este hotfix no agrega ninguna, así que no
cambia el cuadro — pero si la base está atrás, el problema es anterior y hay que resolverlo primero.

### Segunda pasada: ampliación a tres sitios más (decisión de Joaquín, 2026-10-06)

Joaquín amplió el alcance **contra su propio pedido inicial** — "preferí un deploy a dos, y el
patrón ya es mecánico con `BloqueoDeFila` puesto" — a los tres sitios que el barrido había
relevado. Orden de exposición real que fijó él, y **corrigió un dato mío**: yo había dicho que el
gasto era alcanzable "porque los gastos ya se usan", y **producción tiene 0 gastos**. El bug está
vivo en el código publicado pero no hay nada que corromper todavía. El cobro de cuenta corriente,
en cambio, es la única vía por la que hoy entra la plata de un fiado.

Tambien cerró dos cosas que yo había dejado abiertas: **las migraciones de producción son
exactamente las 8 de esta rama** (el "5 atrás" de la memoria era de la rama de desarrollo, así que
el riesgo de deploy que declaré queda cancelado), y **no hay que intentar un índice único** en
`CajaMovimientos`/`MovimientosCCCliente` como refuerzo: el lock de fila es el único mecanismo.

#### Los tres sitios

| Sitio | Dueño que se bloquea | Dato que se relee | Qué dejaba pasar |
|---|---|---|---|
| `CuentaCorrienteClienteService.RegistrarCobroAsync` | **`Clientes`** (no un documento) | el **saldo**, re-consultado | saldo de CC negativo + ingresos de caja duplicados |
| `GastoService.AnularAsync` | `Gastos` | `gasto.Anulado` | dos Ingresos de caja por el mismo gasto |
| `VentaWorkflowService.CancelarBorradorAsync` | `Ventas` | `Estado` **y `DeletedAt`** | venta borrada con la plata movida |

**`RegistrarCobroAsync` pidió un tratamiento distinto y se declaró en vez de improvisarlo.** El
dueño que se bloquea **no es un documento, es el cliente**, porque el dato sobre el que decide la
guarda es el **saldo**, y el saldo es un **agregado del ledger**, no una columna: no existe una
"fila del saldo" que bloquear. Se bloquea la fila del cliente, que alcanza porque todos los
movimientos de esa cuenta cuelgan de él (dos cobros del mismo cliente se serializan, dos de
clientes distintos no se esperan). Y por la misma razón la relectura **no es un `ReloadAsync`** sino
**volver a correr la consulta del saldo** ya con el lock tomado. La transacción se adelantó: antes
`ObtenerSaldoAsync` y las dos guardas corrían **fuera** de ella.

**`GastoService.AnularAsync`: la reversión va por el MONTO DEL DOCUMENTO, no por el "neto vivo".**
Joaquín preguntó explícitamente, y la respuesta es que el neto vivo **no corresponde acá**, por tres
razones verificadas (no supuestas): (1) **no hay reversiones parciales** — `Anulado` es un booleano,
y el neto vivo existe justamente para permitir revertir $400 de $1.000 y después los $600; (2)
**`Gasto.Monto` es inmutable** — `IGastoService` expone solo Listar/Crear/Anular, **no hay método de
edición**, así que el Egreso que posteó el alta siempre vale exactamente `gasto.Monto`; (3) **el lock
es la exclusión**, no una segunda línea: con la relectura bajo lock se postea como máximo UNA
reversión. Y lo que se **descartó explícitamente**: inferir cuáles movimientos son reversiones por
el **signo** (un Ingreso con `OrigenTipo = "Gasto"`) para simular el neto sin la columna
`EsReversion`. Hoy funcionaría de casualidad —un gasto tiene un Egreso y a lo sumo un Ingreso— pero
es una **regla nueva disfrazada de port**, y se rompe en silencio el día que un gasto tenga otra vía
de ingreso asociada. **`EsReversion` no se portó y no se agregó ninguna columna.**

#### EL HALLAZGO DE ESTA PASADA, y lo encontró el arnés: `ReloadAsync` NO SIRVE como "relectura bajo lock" para una entidad con soft delete

Apliqué el patrón mecánicamente a `CancelarBorradorAsync` y **el criterio 8 falló**: con 8 requests
mezclados, **5 "éxitos"** (1 confirmar + 4 cancelar) y el estado prohibido en la base —
`borrada = True` **con** `caja = 1`, `cc = 1`, `stock = 98`. O sea: el fix mecánico no alcanzaba, y
el invariante que importa seguía roto.

Son **dos defectos distintos**, los dos invisibles leyendo el código:

1. **`Estado` no es un discriminador suficiente.** `CancelarBorradorAsync` cancela poniendo
   `DeletedAt` y **no toca `Estado`**: una venta cancelada sigue diciendo `Borrador`. Así que una
   guarda que solo mira `Estado` (a) deja pasar dos cancelaciones de la misma venta, las dos
   "exitosas", y (b) deja que una confirmación postee caja, CC y stock sobre una venta que otro
   request acaba de cancelar. **Es la mitad simétrica que nadie había escrito** (pasada 5 del
   barrido `LP-002`): había guarda de estado y ninguna de "ya cancelada".
2. **`_context.Entry(venta).ReloadAsync()` no ve las filas que el filtro global esconde.** El modelo
   tiene `HasQueryFilter(e => e.DeletedAt == null)`, así que para una venta ya cancelada la consulta
   de recarga **no trae nada**, la entidad queda *detached* y los valores en memoria siguen siendo
   los de **antes** del lock. **La relectura "ocurre" y no relee** — el peor modo de falla posible,
   porque parece hecha y el código se lee bien.

Se cerró con **un solo helper compartido**, `RelerEstadoBajoLockAsync`, que proyecta `Estado` **y**
`DeletedAt` con `IgnoreQueryFilters()`, y que usan **los tres** métodos del workflow
(`ConfirmarAsync`, `FacturarAsync`, `CancelarBorradorAsync`): una sola forma, para que el que lea el
diff no tenga que verificar tres variantes. Los tres ganaron además la guarda explícita de
"cancelada".

**Y la asimetría con `GastoService` se verificó y quedó escrita en el código, en vez de alinear los
dos por prolijidad:** ahí `ReloadAsync` **sí** es válido, porque `Gasto` nunca se borra —
`IGastoService` expone solo Listar/Crear/Anular, nadie escribe `Gasto.DeletedAt` y el único uso de
`_gastoRepository` es el `AddAsync` del alta; `Anulado` es una columna normal y la recarga la ve.
Está comentado con la condición: *si algún día se agrega una baja de gastos, esa recarga hay que
cambiarla por el patrón de la venta*.

**Regla generalizable para el catálogo:** en este proyecto **toda** entidad de negocio hereda
`SoftDestroyable` y tiene el filtro global. Por lo tanto `ReloadAsync` es una relectura **no
confiable** para cualquiera de ellas, y el patrón `PAT-059` necesita esta nota: *la relectura bajo
lock se hace con `IgnoreQueryFilters()` y proyectando los campos que deciden, salvo que se haya
verificado que la entidad no tiene ningún escritor de `DeletedAt`.*

#### Evidencia de la segunda pasada

Build **0 errores** (9 advertencias, todas preexistentes). Arnés ampliado a **82 afirmaciones, 82
OK**, corrido **4 veces** (el criterio 8 tiene un ganador legítimamente no determinista: en las
corridas ganó confirmar con N=4 y cancelar con N=8, y el estado final fue coherente con el ganador
en los dos sentidos).

**Control positivo de los tres sitios nuevos** (los tres services revertidos a `2580f7c`, arnés
igual): **42 OK / 40 FALLADAS**, reproducible en 2 corridas.

- **Cobro de CC**, el peor de los tres: **los N éxitos de N**. Con N=8, una deuda de $1.000 se cobró
  **8 veces**: saldo de cuenta corriente **−$7.000**, 8 créditos en el ledger y **$8.000** de
  ingresos de caja. Con N=3: saldo **−$2.000** y $3.000 de caja.
- **Anulación de gasto**: los N éxitos de N. Con N=8, **9 movimientos** de caja sobre el gasto y neto
  **+$3.500** de plata que nunca entró (con N=3, +$1.000). Con el fix: 2 movimientos y **neto 0**.
- **Cancelar contra confirmar**: 5 y 6 éxitos de 8 según la corrida, con el invariante violado
  (`borrada = True` con caja y CC posteadas) y además `DbUpdateException` en los perdedores.

#### Checklist de la ampliación

- [x] Los 3 sitios con la **misma forma reconocible**: lock del dueño → relectura → guarda. La única
      variante es `RegistrarCobroAsync` (dueño maestro + relectura por consulta), **declarada** en el
      código y acá, no improvisada.
- [x] **Sin migración EF** y **sin columnas nuevas**: `EsReversion` no se portó.
- [x] Código productivo agregado en esta pasada: **32 líneas** (27 en `VentaWorkflowService`
      incluyendo el helper compartido, 3 en `GastoService`, 2 en `CuentaCorrienteClienteService`) más
      3 constantes en `BloqueoDeFila`. El resto del diff es fundamento.
- [x] `RegistrarAjusteAsync` **no se tocó** (no estaba en el alcance que fijó Joaquín).
- [x] Control positivo corrido por sitio y reportado con números.
- [x] `laplatense_dev` sin tocar; fixtures `laplatense_qa_l1..l6` y `laplatense_qa_d9` intactos.
- [ ] Sigue **"aplicado, pendiente de re-verificación"**. El cierre lo declara QA.
- [ ] **Queda para decisión**: los 4 sitios restantes del barrido (`AjusteStockService`/`LP-024`,
      `GuardarBorradorAsync`, la carrera contra el cierre de caja de
      `RegistrarMovimientoManualAsync`/`GastoService.CrearAsync`, y `RegistrarAjusteAsync`), más la
      nota de `ReloadAsync` para `PAT-059`.


### Barrido `LP-002` sobre el resto del código publicado: 7 sitios relevados — **3 de ellos ya entraron** (ver la sección de la ampliación, arriba), 4 siguen sin tocar

El brief pidió explícitamente reportar y **no** arreglar. Ninguno se tocó: entrarían en la
superficie de un hotfix que tiene que ser auditable de un vistazo. Dato transversal que los
enmarca: **no existe ningún índice único sobre `CajaMovimientos` ni sobre `MovimientosCCCliente`**,
así que en esas dos tablas nada del motor protege contra plata duplicada — el lock de fila es el
único mecanismo disponible, y hoy `BloqueoDeFila` solo se usa en los dos métodos de este hotfix.

Ordenados por gravedad:

1. **`GastoService.AnularAsync` — el peor, y es la misma forma exacta del defecto que se acaba de
   arreglar.** Tiene transacción, pero la guarda `if (gasto.Anulado)` se evalúa **antes** de
   abrirla y nunca se relee bajo lock. Dos anulaciones simultáneas del mismo gasto pasan las dos y
   postean **dos Ingresos de caja por el mismo hecho**; el `UPDATE Anulado = true` es idempotente y
   no lo delata. **Alcanzable hoy en producción** (los gastos ya se usan). Es el candidato número
   uno a un segundo hotfix.
2. **`CuentaCorrienteClienteService.RegistrarCobroAsync`.** Tiene transacción, pero
   `ObtenerSaldoAsync` y la guarda `dto.Importe > saldoPrevio` corren **antes** de abrirla y sin
   lock del cliente. Dos cobros simultáneos pasan los dos → **saldo de cuenta corriente negativo y
   dos Ingresos de caja**. También alcanzable hoy.
3. **`AjusteStockService.AplicarAjusteAsync` — es `LP-024`, y el hotfix lo deja a medio camino en un
   sentido que conviene tener presente.** El ajuste es un **set absoluto** (`Stock = CantidadNueva`)
   sobre una lectura sin lock y sin transacción, así que **no lo frena el lock que ahora toma
   `ConfirmarAsync` sobre `Productos`**: un ajuste concurrente pisa el descuento de una venta que se
   está confirmando y deja la auditoría `CantidadAnterior` falsa. El hotfix protege el lado de la
   venta contra otra venta, no contra el ajuste. Excluido del alcance por decisión del brief.
4. **`VentaWorkflowService.CancelarBorradorAsync` — está en la misma clase que se tocó y vale
   decirlo.** Soft-delete sin transacción ni lock, con la guarda `Estado != Borrador` sobre una
   lectura libre: puede cancelar una venta que `ConfirmarAsync` está confirmando en paralelo y dejar
   **stock descontado + Ingreso de caja + Débito de CC sobre una venta borrada lógicamente**. No se
   incluyó porque el brief acotó a dos métodos; es el segundo candidato, y es barato (el lock ya
   existe en el proyecto y la venta es la misma fila).
5. **`VentaWorkflowService.GuardarBorradorAsync`.** `BloquearAsync` bloquea `Ventas` y `Productos`
   pero **no** las filas de `ItemsVenta`/`PagosVenta`: un ítem agregado en la ventana se persiste
   sobre una venta que ya quedó `Confirmada`, sin descuento de stock ni impacto en caja.
6. **`CajaMovimientoService.RegistrarMovimientoManualAsync` y `GastoService.CrearAsync` — la carrera
   contra el cierre de caja.** Las dos deciden con `ValidarPeriodoAbiertoAsync` y después escriben,
   sin lock: un `CerrarDiaAsync` que commitea en el medio deja el movimiento **dentro de un día ya
   cerrado y fuera del arqueo firmado**. La variante simétrica: `CerrarDiaAsync`/`CerrarMesAsync`
   están protegidos contra el cierre **duplicado** por índice único (cae como `DbUpdateException`
   cruda, no como error de negocio), pero leen los totales sin lock, así que un movimiento que
   commitea entre la lectura y el insert queda dentro del período y fuera de los totales
   congelados. **Descuadre silencioso** — y es la misma familia del descuadre de $2.500,75 de
   agosto 2026 que la Entrega 4 hizo visible.
7. **`CuentaCorrienteClienteService.RegistrarAjusteAsync`.** Sin guarda de estado y sin índice
   único: un doble click duplica el ajuste de deuda. Y, a diferencia de `RegistrarCobroAsync`,
   **no llama a `ValidarPeriodoAbiertoAsync`**, así que mueve el saldo de CC con fecha retroactiva
   de un mes ya cerrado.

Un octavo, sin plata ni stock pero es el único escritor con `SaveChanges` **intercalados** y sin
transacción del código publicado: **`ClasificacionAbcAutomaticaService.RecalcularAsync`** guarda por
lotes dentro del `foreach`, así que un fallo en el lote N deja los N−1 aplicados y el contador
`ProductosActualizados` del log miente.

**Nada de esto se tocó.** Son candidatos a un segundo hotfix, en el orden 1 → 2 → 4.


## Historial de ajustes

### Bloques archivados (2026-10-06)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **2026-10** — 7 bloques (2026-10-05 a 2026-10-05) → [`5-implementador-2026-10.md`](historial/5-implementador-2026-10.md)

- 2026-10-06 (**HOTFIX de transacciones de ventas**, rama `hotfix-transacciones-ventas` creada desde `2580f7c`): **no es una ola de desarrollo**, es un hotfix sobre el estado exacto de produccion. El codigo publicado tenia **cero** `BeginTransaction` en `VentaWorkflowService`: `ConfirmarAsync` descontaba stock, posteaba caja y debitaba la cuenta corriente decidiendo sobre una lectura sin lock, y `FacturarAsync` podia emitir **dos CAE de AFIP por la misma venta**. Se **porto `PAT-059`** (hit en el paso 1 del escaneo) desde el commit `bdfd99b` del mismo repo, aplicado **solo** a esos dos metodos: transaccion abierta **antes de LEER**, lock de la fila de la venta y de los productos de esa venta, y relectura bajo lock. **No fue copiar y pegar:** de las 7 constantes de tabla del helper original **solo 3 existen en produccion**, y su XML-doc fundamentaba la decision hablando de las reversiones parciales de `AnularAsync`, **metodo que no existe en la rama publicada** — copiar ese texto habria plantado un comentario que describe codigo ausente (`LP-008`). **Dos premisas del brief refutadas ejecutando** y escritas en el codigo como 'lo que NO estaba roto': (a) la falla parcial **ya estaba cubierta** por el `SaveChanges` unico mas la transaccion implicita de EF (verificado abortando el INSERT de caja con un trigger: el criterio 2 pasa **tambien contra el codigo roto**), y (b) el stock **no se duplicaba, se perdia** — los dos competidores leian 100 y escribian 98, y el resultado coincidia con el correcto por casualidad. **SIN migracion EF**, diff aditivo de 3 archivos (+93/−0, 20 lineas de codigo). Concurrencia medida con conexiones separadas y barrera en un clon aislado: **46/46 OK**, y lo que mas vale: el arnes se corrio **contra el codigo roto** y dio 12 fallas (N=8 → 2 exitos, $ 2.840 de caja y $ 2.000 de CC donde iban $ 1.420 y $ 1.000; y `FacturarAsync` **emitio 8 comprobantes AFIP**). El huerfano de AFIP queda **declarado en el codigo** y fuera de alcance con fundamento (AFIP deshabilitado). **Barrido: 7 sitios mas que mueven plata o stock sin lock.** **AMPLIADO despues por decision de Joaquin a 3 de ellos** (contra su propio pedido inicial: "prefiero un deploy a dos"): `RegistrarCobroAsync` —el mas expuesto, es la unica via por la que hoy entra la plata de un fiado—, `GastoService.AnularAsync` (y **se corrigio un dato mio**: produccion tiene **0 gastos**, asi que el bug esta vivo pero no hay nada que corromper) y `CancelarBorradorAsync`. `EsReversion` **NO se porto**: la reversion del gasto va por el monto del documento, con tres razones verificadas (no hay reversiones parciales, `Gasto.Monto` es inmutable porque no hay metodo de edicion, y el lock YA es la exclusion). **EL HALLAZGO QUE CAMBIA EL PATRON, y lo encontro el arnes:** aplicar `PAT-059` mecanicamente a `CancelarBorradorAsync` **FALLO** — 5 exitos de 8 y el estado prohibido en la base (venta **borrada CON la plata movida**). Dos defectos invisibles leyendo: (a) **`Estado` no discrimina**, porque cancelar pone `DeletedAt` y **no toca `Estado`** —la mitad simetrica que nadie habia escrito—, y (b) **`ReloadAsync` no ve las filas que el filtro global esconde**: la entidad queda detached y los valores en memoria siguen siendo los de antes del lock, asi que **la relectura parece hecha y no relee**. Se cerro con un helper unico `RelerEstadoBajoLockAsync` (`IgnoreQueryFilters` + proyeccion de `Estado` y `DeletedAt`) que usan los tres metodos del workflow. La asimetria con `GastoService` **se verifico y quedo escrita** en vez de alinear los dos por prolijidad: ahi `ReloadAsync` si vale porque un `Gasto` nunca se borra. Arnes **82/82 OK en 4 corridas**; control positivo de los 3 sitios nuevos **40 FALLADAS**, con una deuda de $ 1.000 **cobrada 8 veces** (saldo **−$ 7.000**, $ 8.000 de caja) y **+$ 3.500** de reversiones de gasto que nunca entraron. Commit local, **SIN push, SIN deploy**.
- 2026-10-06 (**Entrega 4**, rama `entrega-1-migracion`): **cuenta corriente de empleados (M12)** y **cuenta corriente del negocio (M13)**. La decision mas importante es la que NO se construyo: el modulo 13 **no tiene entidad ni ledger nuevo**. El nombre engaña — en `marihogar` el `MovimientoCCLocal` de `CCLocalService` **ES la caja** (su unico ledger de dinero, y su `CajaService` es pura agregacion sobre el), y aca ese ledger ya existe y se llama `CajaMovimiento`, con cierres diarios y mensuales que alla no hay. Construir un segundo libro del mismo dinero es como se descubre, meses despues, que ninguno de los dos cuadra. Lo que el presupuesto pide es textualmente una *vista consolidada*, y eso es lo que se hizo: saldo acumulado, actividad del periodo, desglose por medio que **suma exactamente el saldo**, saldo corrido por fila sobre **todo** el libro (no sobre la pagina ni sobre lo filtrado) y cada cierre firmado al lado de su **recalculo**. **Sobre el cero inventado se eligio resolverlo, no rotularlo:** se implemento el **saldo inicial declarado por medio de pago** (`OrigenCajaMovimiento.SaldoInicialCaja`, con fecha, motivo, usuario y una sola vez por medio, pasando por `ValidarPeriodoAbiertoAsync`) **y ademas** la pantalla no llama 'saldo' al numero mientras no haya apertura: el rotulo dice literalmente *Movimiento acumulado del sistema* y cada cuenta sin apertura lleva su badge. El criterio de marihogar de excluir la apertura de los totales del periodo SI aplica y vive en un solo lugar (`EsApertura` + los dos helpers de totales), alcanzando a los **seis** lectores — sin eso, el cierre del dia en que se declara el saldo inicial diria que ese dia entraron $ 500.000 (verificado ejecutando: los ingresos del dia no se movieron y el acumulado paso de $ -46.586,20 a $ 453.413,80). **El contraste encontro un problema real la primera vez que corrio:** el cierre mensual de **agosto 2026 no cuadra por $ 2.500,75**, porque se firmo el 21/08 19:05 y el movimiento #5 (fecha 24/08) se cargo el 25/08 02:00 — cuatro dias despues. Es **residuo historico del defecto que `LP-009` ya cerro** (la guarda funciona, se verifico), no un bug de esta ronda: es la ronda haciendo visible algo que nadie podia ver. **Produccion tiene el mismo codigo viejo que lo genero, asi que puede tener el mismo residuo** (no se consulto, estaba prohibido). Del lado de empleados, `MovimientoCCEmpleado` es el **cuarto ledger** con el molde de `MovimientoCCProveedor`, y lo propio es la distincion **devengar no es pagar** resuelta en un solo lugar invocable (`OrigenCCEmpleado.MueveCaja`, con `_ => false` como default seguro a proposito: un egreso que falta se nota, uno de mas descuadra en silencio). El `Tipo` lo impone el **concepto** y no la vista (verificado: se posteo `Cargo` con concepto `Adelanto` y persistio `Pago`). La guarda de periodo es **asimetrica a proposito** — solo la corren los conceptos que escriben caja, asi que un devengamiento retroactivo a un mes cerrado entra y un pago no. **`MovimientoRevertidoId` es nuevo y necesario:** el par `(OrigenTipo, OrigenId)` de los otros tres ledgers identifica un *documento*, y aca no hay documento (todo comparte `OrigenId = 0`), asi que el neto de `('Adelanto', 0)` sumaria **todos** los adelantos del empleado y revertir uno revertiria la plata de los otros — acotar por empleado, el parche de proveedores, **no alcanzaria**. **`PAT-053` por tercera vez** (primera sobre sueldos, que el patron ya preveia) y **`PAT-017` estrenado con codigo real** tras estar con `pendiente_verificar` desde `cma-centro-medico`: dos pantallas en **dos controllers**, y las acciones del autoservicio **no declaran ningun parametro de identidad** — no es que se valide, es que no existe. Probado inyectando el id del Vendedor por **tres vias** en el form con el claim del Repartidor: devolvio solo las 4 filas del Repartidor, cero ajenas. **`MH-001` era el riesgo central** (la identidad de la cuenta es un `string` de `AspNetUsers`, el caso que ya explotó dos veces) y se cerro con sub-consulta correlacionada y materializar-y-filtrar, extraido a `ResolverNombresAsync` porque ya son cuatro los lugares que lo necesitan; los shapes se **ejecutaron**, no se supusieron. **Barrido `LP-002`: 6 hallazgos**, incluidos que los seis lectores de totales **no** se arrastran solos con el helper de origenes, que `CajaMovimiento.UsuarioId` era una columna de **solo escritura** desde la ola 1 (ninguna pantalla la mostraba) y la **promesa vencida** de `EsReversion` — su XML-doc promete desde la ola 1 que el arqueo puede separar 'plata que entro' de 'plata que nunca salio', y ningun lector de totales usa el flag (medido: ingresos brutos $ 97.415,05 contra netos $ 5.914,55). No se cambio el criterio de los cierres (dejaria sin cuadrar a los ya firmados): la pantalla consolidada muestra **los dos numeros con el puente entre ellos** y la decision queda para Joaquin. Septimo hallazgo fuera de alcance y **sin corregir**: `Views/Clientes/CuentaCorriente.cshtml` es el **unico de los cuatro ledgers sin su helper `Origen*`**. Migracion `EntregaCuatro_CCEmpleadoYSaldoInicialCaja`: **una tabla nueva, cero cambios sobre tablas existentes**. Evidencia: build 0 errores sin advertencias nuevas y sonda EF desechable con ~45 verificaciones contra dev, con la linea base calculada por **SQL crudo** y no por el codigo bajo prueba; base devuelta a su linea base exacta (9 filas / $ 3.413,80 / `MAX(Id) = 9`). **Aviso de impacto:** los retiros del titular y los adelantos al personal son plata que siempre salio y nunca se registraba — el dia que se carguen, los egresos del periodo suben de golpe. Commit local, **SIN deploy, SIN push**.
- 2026-10-05 (**Entrega 6**, rama `entrega-1-migracion`): **presupuestos en PDF** y **aumento masivo de precios**, los dos declarados reuse total de `marihogar`. El reuse rindio en la ESTRUCTURA (maquina de estados, estado derivado calculado al leer, previsualizar->confirmar, patron de PDF con QuestPDF que ya estaba en el repo) y **no** en la aritmetica, porque el modelo de datos de este proyecto es distinto en los dos casos. En presupuestos hubo que reemplazar cantidad `int` por `decimal(18,3)`, agregar unidad congelada e **IVA por linea discriminado por alicuota** (marihogar tiene el 21% hardcodeado), cambiar la cascada `base*(1-d)*(1+r)` por la formula no-cascada —que es el bug corregido aca el 2026-09-03— y meter el **gate de precio por rol** (`PAT-050`/`LP-014`/`LP-016`) que alla no existe: un presupuesto que acepte precios del navegador reabre el agujero por una puerta nueva. La **conversion a venta** cambio de lugar y es una mejora: alla la transicion a `Convertido` espera a que la venta se confirme porque no hay estado editable intermedio; aca la Venta nace en `Borrador`, que es justo el "carrito precargado" que marihogar tenia que simular. En aumento masivo, el punto de la entrega es que el precio de venta de La Platense es **derivado** (`costo x (1+rec)/(1+IVA)`) y no editable a mano como el `PrecioEfectivo` de marihogar, asi que la corrida opera sobre **dos palancas** —recalcular desde el costo (el modo que **apaga** `PrecioVentaDesactualizado`, la mitad que le faltaba a `PAT-054`) o cambiar el `PorcentajeRecargo`— y en las dos el precio sale de la misma formula. `PAT-004` **no era aplicable**: ninguna entidad de La Platense tiene `RowVersion`, asi que la concurrencia optimista se resolvio con `SoftDestroyable.UpdatedAt` (el mecanismo que el proyecto YA usa, estampado por `SaveChanges`) mas una **guarda de universo** por recuento, que cubre lo que `UpdatedAt` no ve: altas, bajas y productos que cambiaron de categoria. Por eso se descarto `ExecuteUpdateAsync` aunque es mucho mas rapido: no dispara `SaveChanges` y dejaria al proximo aumento sin la marca que usa. **Dos defectos propios encontrados EJECUTANDO:** el preview mostraba el precio nuevo sin redondear (`26254,014876...` contra `26254,02` que escribia el aplicar — exactamente lo que el patron de dos pasos existe para evitar), y la variacion porcentual del preview estaba **secuestrada por tres filas basura** del catalogo migrado (costo de 6,3 billones): daba 0,00% mientras 112.000 productos cambiaban de precio, y se reemplazo por contadores sube/baja/igual. **Tercera exclusion no pedida pero necesaria:** 38 productos con costo cero o negativo, que la formula convertia fielmente en un **precio de venta negativo** (medido: -4,00). El **barrido `LP-002`** rindio **7 hallazgos**, incluido un `LP-008` (el XML-doc de `VentaWorkflowService` seguia declarando que descuento y recargo eran importes monetarios, falso desde el 2026-08-21) y que la regla de la oferta vigente esta escrita en **4 lugares**. Medido sobre 112.485 productos reales: preview 464 ms, aplicar 7,6-10,4 s. Commit local, SIN push y SIN deploy por pedido explicito de Joaquin; la migracion se aplico solo a `laplatense_dev` y la tabla `Productos` se respaldo y restauro para que la base quede en su linea base.
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
