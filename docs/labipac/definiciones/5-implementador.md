# Implementador — LabIPAC
> Memoria acumulativa del agente implementador. Actualizar al inicio y cierre de cada etapa.

---

## Historial de sesiones

### Sesión 4 — Implementación M10+M11+M12 (Produccion Mensual por Centro de Salud)
**Fecha:** 2026-07-23
**Estado:** ✅ BUILD OK — Migración generada y aplicada exitosamente a la base de desarrollo local (`labipac_dev`)

**Nota operativa:** el subagent delegado (`agentes-ia-implementador`, ejecutado como agente en background) se cortó a mitad de la verificación manual por haber alcanzado el limite de gasto mensual de la cuenta de Claude (error de API, no un fallo de codigo). El orquestador retomo el trabajo directamente: revisó todo el diff generado antes del corte, corrió `dotnet build` (OK, 0 errores nuevos), verificó contra la base real (`mysqlsh`) que la migracion estaba aplicada y que los datos de prueba dejados por el subagent confirmaban la regla RN-24 (3 períodos para el mismo Mes+Año: 2 con distinto CentroSaludId + 1 global, todos coexistiendo sin conflicto), y limpió los datos de prueba (`Centro Salud Test A/B` y los 3 períodos de prueba Mayo 2031) y el log de debug (`run_app.log`) que quedaron en el working tree.

**Cambio:** Implementado el alcance completo de M10 (ABM `CentroSalud`), M11 (`CentroSaludId` en `ProduccionMensual` + RN-24 + selector + columna en listado) y M12 (Centro de Salud en encabezado del PDF), según diseño/arquitectura de sesión 2026-07-23.

**Archivos nuevos:**
- `LabIPAC.Domain/Entities/CentroSalud.cs`, `LabIPAC.Domain/Enums/TipoCentroSalud.cs`
- `LabIPAC.Application/Interfaces/ICentroSaludService.cs`
- `LabIPAC.Infrastructure/Services/CentroSaludService.cs`
- `LabIPAC.Web/Controllers/CentrosSaludController.cs`, `LabIPAC.Web/Models/CentroSaludViewModels.cs`
- `LabIPAC.Web/Views/CentrosSalud/{Index,Create,Edit}.cshtml`
- Migración `20260723214415_AddCentroSaludYProduccionMensualCentroSalud` (tabla `CentrosSalud`, columna nullable `CentroSaludId` + FK Restrict en `ProduccionMensuales`, sin backfill)

**Archivos modificados:**
- `LabIPAC.Domain/Entities/ProduccionMensual.cs` (+`CentroSaludId`, +nav `CentroSalud`)
- `LabIPAC.Application/Interfaces/IProduccionMensualService.cs` (doc de RN-24/RN-25)
- `LabIPAC.Infrastructure/Services/ProduccionMensualService.cs` (`CreateAsync` valida RN-24 unicidad Mes+Año+CentroSaludId y RN-25 centro activo; `GetAllAsync`/`GetByIdAsync` +`Include(CentroSalud)`)
- `LabIPAC.Infrastructure/Data/AppDbContext.cs` (+`DbSet<CentroSalud>`, Fluent config)
- `LabIPAC.Infrastructure/DependencyInjection.cs` (+registro `ICentroSaludService`)
- `LabIPAC.Web/Controllers/ProduccionMensualController.cs` (Create GET/POST con selector de centro, GetData +`nombreCentroSalud`, `ReportePdf` +línea condicional de encabezado)
- `LabIPAC.Web/Models/ProduccionMensualViewModels.cs` (+`CentroSaludId`/`CentrosSaludDisponibles` en Create VM, +`NombreCentroSalud` en Row VM)
- `LabIPAC.Web/Views/ProduccionMensual/Create.cshtml` (selector), `Index.cshtml` (columna), `Views/Shared/_Layout.cshtml` (+entrada sidebar)

**Build:** OK, 0 errores (mismos warnings preexistentes de NuGet — MailKit/MimeKit — y CS0114 de HomeController, ninguno introducido por esta sesión).

**Migración EF:** generada y **aplicada exitosamente** a `labipac_dev`. Verificado contra la base real: tabla `CentrosSalud` creada, columna `ProduccionMensuales.CentroSaludId` presente, `__EFMigrationsHistory` confirma la migración aplicada. Pendiente aplicar a Producción en el próximo deploy.

**Desvíos respecto al plan de Arquitectura:** el memo de arquitectura mencionaba DTOs de creación (`CentroSaludCreateDto`, etc.) — la implementación real siguió el patrón vigente del repo (Controller arma la entidad directo, Service recibe la entidad), consistente con `UnidadBioquimica`/`ProduccionMensual` existentes. No se crearon DTOs nuevos, es una simplificación correcta respecto al patrón real, no una desviación de riesgo.

**Riesgos/supuestos:** ninguno nuevo. Períodos históricos quedan con `CentroSaludId = NULL` según lo definido en Análisis (P13), sin backfill.

**Estado:** IMPLEMENTACIÓN CERRADA (build OK, migración aplicada y verificada contra base real, RN-24 verificada con datos reales de prueba — luego eliminados). Pendiente: QA funcional formal, aplicar migración en Producción, documento de cliente.

### Sesión 3 — Implementación M7+M8+M9 (Unidad/PrecioPorUnidad, Carga masiva + alta rápida, fix PDF)
**Fecha:** 2026-07-08
**Estado:** ✅ BUILD OK — Migración generada, aplicada exitosamente a la base de desarrollo local (`labipac_dev`)

Input: `1-analista-funcional.md` sesión 4, `2-disenador-funcional.md` sesión 2, `3-arquitecto-mvc.md` sesión 2, `4-presupuestador.md` SESIÓN 3 — todos cerrados y aprobados. Presupuesto aprobado por el cliente; se implementó todo el alcance en una sola pasada (Etapa 1 M7+M9 / Etapa 2 M8 solo a efectos de facturación, sin dividir la entrega técnica).

#### 0. Escaneo de reutilización
Se escaneó `C:/Sistemas/Agentes-IA/docs/*/definiciones/5-implementador.md` buscando patrones "fila única" / "PrecioPorUnidad" / "valor global de configuración" en otros proyectos del estudio: sin coincidencias cross-proyecto. Decisión: implementar desde cero dentro de labipac, reutilizando el patrón visual+AJAX intra-proyecto ya existente ("IVA del período" en `Views/ProduccionMensual/Detalle.cshtml`, F-002) para la nueva card "Precio por Unidad" en `Views/Practicas/Index.cshtml`.

#### Terminología (recordatorio): `Practica` (Domain) = "Perfil" en UI. `UnidadBioquimica` (Domain) = "Práctica" en UI.

#### Archivos creados

**Domain:**
- `LabIPAC.Domain/Entities/PrecioPorUnidad.cs` — hereda `SoftDestroyable`, `Valor decimal`. Patrón de fila única (enforced en `PracticaService`, no en DB).

**Web:**
- `LabIPAC.Web/Views/ProduccionMensual/CargaMasiva.cshtml` — pantalla nueva de carga masiva (filas dinámicas JS, un submit).
- `LabIPAC.Web/Views/ProduccionMensual/_ModalAltaRapidaPerfil.cshtml` — partial, modelo `decimal` (PrecioPorUnidadVigente).
- `LabIPAC.Web/Views/ProduccionMensual/_ModalAltaRapidaPractica.cshtml` — partial.

#### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `LabIPAC.Domain/Entities/Practica.cs` | + `public int Unidad { get; set; }`. Comentarios actualizados (RN-01 derogada, RN-02 relajada, RN-16). |
| `LabIPAC.Application/Interfaces/IPracticaService.cs` | + `ObtenerPrecioPorUnidadVigenteAsync()`, `ActualizarPrecioPorUnidadAsync(decimal)`, `AumentarPrecioPorUnidadPorcentajeAsync(decimal)`. `CreateAsync`/`UpdateAsync` sin cambio de firma (siguen recibiendo `Practica` + `IList<int>`), pero ahora la entidad trae `Unidad` y el precio se calcula internamente. |
| `LabIPAC.Application/Interfaces/IProduccionMensualService.cs` | + `AgregarLineasAsync(int, IEnumerable<ProduccionDetalleLineaDto>)`. |
| `LabIPAC.Application/DTOs/PracticaDtos.cs` | `PracticaSummaryDto` + campo `Unidad`. |
| `LabIPAC.Application/DTOs/ProduccionMensualDtos.cs` | + `ProduccionDetalleLineaDto` (TipoItem, ItemId, Cantidad, PrecioSnapshot). |
| `LabIPAC.Infrastructure/Data/AppDbContext.cs` | + `DbSet<PrecioPorUnidad> PreciosPorUnidad` + Fluent config (`Valor` decimal(18,2)). |
| `LabIPAC.Infrastructure/Services/PracticaService.cs` | RN-02 (mínimo 1 componente) eliminada de `CreateAsync`/`UpdateAsync`. Ambos calculan `PrecioActual = Unidad * PrecioPorUnidad vigente` antes de persistir. + 3 métodos nuevos (`ObtenerPrecioPorUnidadVigenteAsync`, `ActualizarPrecioPorUnidadAsync` con recálculo batch en un único `SaveChangesAsync`, `AumentarPrecioPorUnidadPorcentajeAsync` con redondeo `AwayFromZero` igual criterio que F-001). |
| `LabIPAC.Infrastructure/Services/ProduccionMensualService.cs` | + `AgregarLineasAsync`: valida ítem activo/existente, cantidad >=1, sin duplicados dentro del batch (RN-13) ni contra líneas ya existentes del período (RN-04 heredada); `AddRangeAsync` + único `SaveChangesAsync` (atomicidad). |
| `LabIPAC.Web/Controllers/PracticasController.cs` | `Index` pasa `ViewBag.PrecioPorUnidadVigente` + `ViewBag.CantidadPerfilesActivos`. `Create`/`Edit` GET pasan `PrecioPorUnidadVigente`. POST ya no reciben `PrecioActual`, reciben `Unidad`. + acciones AJAX `ActualizarPrecioPorUnidad` y `AumentarPrecioPorUnidadPorcentaje` (`[Authorize(Policy = "RequireAdministracion")]`). `GetData` agrega campo `unidad`. |
| `LabIPAC.Web/Controllers/PreciosController.cs` | **Simplificado**: se eliminó toda la lógica de cascade UB→Perfil y de "Perfiles seleccionados directamente" en `AumentoMasivo`, `Previsualizar`, `AplicarAumento`. Ahora opera solo sobre `UnidadBioquimica`. |
| `LabIPAC.Web/Controllers/ProduccionMensualController.cs` | + `CargaMasiva` (GET/POST), `CrearPerfilRapido` (AJAX, reusa `IPracticaService.CreateAsync`), `CrearPracticaRapido` (AJAX, reusa `IUnidadBioquimicaService.CreateAsync`) — las 3 con `[Authorize]` de clase sin política, igual que `AgregarLinea`. `ReportePdf`: `ConstantColumn(55)`→`75` (Precio unit.), `ConstantColumn(65)`→`60` (Tipo). |
| `LabIPAC.Web/Models/PracticaViewModels.cs` | `PracticaCreateViewModel`: quita `PrecioActual`, agrega `Unidad` (`[Range(1,int.MaxValue)]`) y `PrecioPorUnidadVigente` (solo lectura). `PracticaRowViewModel` + `Unidad`. + `PrecioPorUnidadViewModel` (VM-16, definido para trazabilidad de diseño; los endpoints AJAX reales usan parámetros primitivos siguiendo el mismo patrón que `ActualizarIva` existente). |
| `LabIPAC.Web/Models/ProduccionMensualViewModels.cs` | + `ProduccionCargaMasivaViewModel`, `ProduccionCargaMasivaFilaViewModel`, `PerfilAltaRapidaViewModel`, `PracticaAltaRapidaViewModel`. |
| `LabIPAC.Web/Models/PreciosViewModels.cs` | `AumentoMasivoViewModel` quita `PerfilesSeleccionados`. |
| `LabIPAC.Web/Views/Practicas/Index.cshtml` | + card "Precio por Unidad" (mismo patrón visual/AJAX que card IVA de F-002, con SweetAlert2 de confirmación mostrando cantidad de perfiles activos afectados). + columna "Unidad". "Precio actual" → "Precio (calculado)" solo lectura. Se quitó el badge de advertencia RN-01 (derogada). |
| `LabIPAC.Web/Views/Practicas/Create.cshtml` / `Edit.cshtml` | Se quitó el campo "Precio actual" editable y el aviso RN-01. Se agregó campo "Unidad" (entero >=1) + texto "Precio calculado: $ X" recalculado en vivo por JS. Composición (Select2) se mantiene como informativa/opcional. |
| `LabIPAC.Web/Views/Precios/AumentoMasivo.cshtml` | Se quitó el tab "Perfiles" y toda su tabla/JS asociada (incluida en el panel de previsualización). Se agregó nota informativa sobre el nuevo mecanismo de precio de Perfiles. Solo queda la tabla de Prácticas (UnidadBioquimica). |
| `LabIPAC.Web/Views/ProduccionMensual/Detalle.cshtml` | + botón "Carga masiva" (btn-outline-primary) junto a "Agregar ítem", enlaza a `CargaMasiva/{id}`. |

#### Migración EF generada y aplicada
- Nombre: `AddPracticaUnidadYPrecioPorUnidad` (`20260708175303_AddPracticaUnidadYPrecioPorUnidad`)
- Cambios de esquema: `ALTER TABLE Practicas ADD COLUMN Unidad int NOT NULL DEFAULT 0`; `CREATE TABLE PreciosPorUnidad` (Id, Valor decimal(18,2) + columnas estándar SoftDestroyable).
- Seed: `InsertData` — 1 fila `Id=1, Valor=892.03`.
- **Backfill de datos ejecutado** (RA-06, riesgo crítico mitigado): `UPDATE Practicas SET Unidad = GREATEST(1, CAST(ROUND(PrecioActual / 892.03) AS SIGNED)) WHERE DeletedAt IS NULL;` vía `migrationBuilder.Sql(...)` en el método `Up`.
- **Estado: APLICADA** a `labipac_dev` (localhost MySQL). Verificado post-aplicación vía `mysqlsh`: `PreciosPorUnidad` tiene la fila seed (Id=1, Valor=892.03); columna `Practicas.Unidad` existe (int NOT NULL default 0); backfill correcto en datos reales (ej. Perfil "Rutina" PrecioActual=$15000.00 → Unidad=17, consistente con `ROUND(15000/892.03)=17`).
- Pendiente: aplicar la misma migración al ambiente de Producción cuando se despliegue (usa `appsettings.Production.json`, credenciales ya configuradas ahí — no se tocó ese ambiente en esta sesión).

#### Reglas de negocio implementadas
- RN-16: `Practica.PrecioActual = Unidad * PrecioPorUnidad.Valor vigente`, recalculado en `CreateAsync`/`UpdateAsync` y en recálculo batch.
- RN-17: `Unidad` entero, obligatorio, >= 1 (DataAnnotation + Domain).
- RN-18: `PrecioPorUnidad.Valor` obligatorio, >= 0 (validado en `ActualizarPrecioPorUnidadAsync`).
- RN-19: aumento % con `Math.Round(valorActual * (1 + pct/100m), 2, MidpointRounding.AwayFromZero)` (mismo criterio que F-001).
- RN-20: RN-01 derogada (ya no se valida `PrecioActual < SumatoriaComponentes`; nunca existió como bloqueo server-side, solo era un aviso JS en las vistas — removido).
- RN-02 relajada GLOBALMENTE (no solo alta rápida, decisión de arquitectura confirmada en presupuesto): `UnidadBioquimicaIds` ya no exige mínimo 1 en ningún flujo (ABM completo ni alta rápida).
- RN-12/RN-13: `AgregarLineasAsync` atómico (un único `SaveChangesAsync`), sin duplicados TipoItem+ItemId dentro del envío ni contra líneas ya existentes del período.
- RN-21 / simplificación F-001: `PreciosController` ya no opera sobre Perfiles (Practica), solo sobre Prácticas (UnidadBioquimica).

#### Permisos
- `[Authorize(Policy = "RequireAdministracion")]`: `ActualizarPrecioPorUnidad`, `AumentarPrecioPorUnidadPorcentaje` (PracticasController) — mismo criterio que F-001/IVA.
- `[Authorize]` sin política: `CargaMasiva`, `CrearPerfilRapido`, `CrearPracticaRapido` (ProduccionMensualController) — igual que ABM/`AgregarLinea` existentes.
- `PreciosController` mantiene `[Authorize(Policy = "RequireAdministracion")]` a nivel de clase, sin cambios.

#### Desvíos respecto a la arquitectura documentada
- Ninguno relevante. Un detalle menor: `PrecioPorUnidadViewModel` (VM-16) quedó definido en `PracticaViewModels.cs` para trazabilidad de diseño, pero los endpoints AJAX reales (`ActualizarPrecioPorUnidad`, `AumentarPrecioPorUnidadPorcentaje`) usan parámetros primitivos (`decimal nuevoValor` / `decimal porcentaje`) en lugar de bindear ese VM completo, replicando exactamente el patrón ya usado por `ActualizarIva(int, decimal?)` en `ProduccionMensualController` (consistencia con convención existente, sin agregar una capa de binding adicional).

#### Pendiente
- [ ] Aplicar la migración `AddPracticaUnidadYPrecioPorUnidad` a Producción en el próximo deploy.
- [x] QA funcional de los 3 módulos (M7, M8, M9) según pruebas mínimas de `4-presupuestador.md` SESIÓN 3. (QA SESIÓN 2, sin bloqueantes; ver Sesión 4 para los 3 hallazgos de UI reportados por el cliente en pruebas manuales posteriores).
- [ ] Revisión manual por el cliente de los valores de `Unidad` backfilleados en Perfiles existentes (aproximación automática, confirmada como tarea post-deploy del cliente).

---

### Sesión 4 — Fix de 3 hallazgos de UI reportados por el cliente (pruebas manuales post M7+M8+M9)
**Fecha:** 2026-07-08
**Estado:** ✅ BUILD OK — Los 3 hallazgos corregidos y verificados en vivo contra `labipac_dev`

Input: el cliente ejecutó las pruebas manuales de UI pendientes tras el sprint M7+M8+M9 y reportó 3 hallazgos concretos. Se clasificaron como completions/fixes de bajo esfuerzo dentro del alcance ya aprobado (no alcance nuevo), resueltos directo sin nuevo ciclo de Presupuesto, según pedido explícito del orquestador/cliente.

#### 0. Escaneo de reutilización
No aplica: son fixes puntuales sobre código ya implementado en esta misma sesión de trabajo del proyecto (Sesión 3), no una funcionalidad nueva a buscar en otros proyectos del estudio.

#### Hallazgo 1 — `Practicas/Details.cshtml` no mostraba el campo `Unidad`
- **Causa raíz:** `PracticaDetailsViewModel` nunca tuvo la propiedad `Unidad` (quedó fuera al agregar el campo `Practica.Unidad` en la Sesión 3, ya que Details no formaba parte del alcance original de esa sesión); por lo tanto `PracticasController.Details` tampoco la mapeaba ni la vista la mostraba.
- **Fix:** se agregó `public int Unidad { get; set; }` a `PracticaDetailsViewModel` (`LabIPAC.Web/Models/PracticaViewModels.cs`), se mapeó en `PracticasController.Details` (`Unidad = practica.Unidad`), y se agregó la fila "Unidad" en la card "Información general" de `Views/Practicas/Details.cshtml`.
- **Capas afectadas:** Web (ViewModel, Controller, View). Sin migración EF (el campo `Practica.Unidad` ya existía desde la Sesión 3).
- **Verificado en vivo:** `GET /Practicas/Details/1` (Perfil "Rutina") muestra "Unidad: 17".

#### Hallazgo 2 — `Practicas/Edit` no preseleccionaba el combo de composición (BUG REAL, causa raíz confirmada por reproducción)
- **Descartado como falso positivo:** se reprodujo localmente contra `labipac_dev` con el Perfil real "Rutina" (Id=1, con 2 componentes asociados: Urea y Triglicéridos), por lo que la hipótesis "Perfil sin composición" no aplica a este caso.
- **Causa raíz real (confirmada corriendo la app y comparando el HTML servido antes/después del fix):**
  1. `PracticasController.Edit` (GET) arma `UnidadesDisponibles` únicamente a partir de `IUnidadBioquimicaService.GetActivasAsync()`, que filtra `Where(e => e.Activo)` **sobre un `DbSet` que ya tiene aplicado el query filter global de soft-delete** (`DeletedAt == null`, definido en `AppDbContext.ApplySoftDeleteFilter`). Es decir: cualquier `UnidadBioquimica` soft-deleted queda excluida de `UnidadesDisponibles` **aunque su columna `Activo` siga en `true`**.
  2. En la base real, las dos `UnidadBioquimica` asociadas al Perfil "Rutina" (Urea Id=1, Triglicéridos Id=2) están soft-deleted (`DeletedAt` no nulo) pero con `Activo=1`. Por lo tanto no se generaba ningún `<option>` para esos IDs en el `<select>` del formulario.
  3. `UnidadBioquimicaIds` (el array `seleccionados` que usa el JS de Select2) sí se arma correctamente desde `practica.Detalles.Select(d => d.UnidadBioquimicaId)` — el problema no era el JSON ni el timing de Select2 (ambas hipótesis descartadas): sin `<option>` en el DOM para esos valores, ni el atributo `selected` de Razor ni el `.val(seleccionados).trigger('change')` de JS tienen sobre qué actuar. El bug era 100% de datos faltantes en el combo, no de front-end.
  4. **Bug secundario relacionado (más grave, de pérdida de datos):** como el formulario nunca renderiza esos `<option>`, al guardar el Edit sin tocar el combo el navegador no los envía en el POST, por lo que `PracticaService.UpdateAsync` los eliminaba silenciosamente de la composición del Perfil. Es decir, el bug visual escondía un bug funcional de pérdida de datos en cada guardado.
  5. **Bug adicional detectado en el mismo código:** el banner de advertencia "Atención: los siguientes componentes están inactivos" (`ComponentesInactivos`) solo evaluaba `d.UnidadBioquimica is { Activo: false }`, por lo que tampoco se disparaba para este caso (Activo=true, solo soft-deleted), dejando al usuario sin ninguna pista visual del problema.
- **Fix aplicado en `PracticasController.cs`:**
  - Nuevo método privado `BuildUnidadesDisponiblesAsync(IEnumerable<int> idsAsociados)`: arma la lista de unidades activas (comportamiento igual que antes) y además agrega, vía `_context.UnidadesBioquimicas.IgnoreQueryFilters().Where(u => idsFaltantes.Contains(u.Id))`, las unidades ya asociadas a la Práctica/Perfil que no aparecen entre las activas (inactivas o soft-deleted). Así el combo siempre puede renderizar y preseleccionar la composición real, y el POST no pierde la asociación si el usuario no la toca.
  - Se reemplazaron las 6 repeticiones inline del patrón `(await _unidadService.GetActivasAsync()).Select(...).ToList()` (Create GET, Create POST x2, Edit GET, Edit POST x2) por llamadas a este helper — no es un refactor cosmético, es la corrección mínima necesaria para que los 3 puntos de re-render del formulario (GET inicial, ModelState inválido, fallo de servicio) se comporten igual y no reintroduzcan el bug en los otros caminos.
  - Se corrigió la condición de `ComponentesInactivos` en `Edit` (GET) de `d.UnidadBioquimica is { Activo: false }` a `d.UnidadBioquimica is { } ub && (!ub.Activo || ub.DeletedAt != null)`, para que el banner de advertencia también contemple componentes soft-deleted.
- **Capas afectadas:** Web (`PracticasController`) únicamente. Sin cambios de ViewModel ni de vista (`Edit.cshtml` ya estaba correctamente cableado, tal como indicaba la lectura de código estática original). Sin migración EF.
- **Verificado en vivo (antes/después, mismo Perfil real):**
  - Antes del fix: `GET /Practicas/Edit/1` devolvía un único `<option value="3">` (la única `UnidadBioquimica` activa y no eliminada); `seleccionados = ["2","1"]` en el JS pero sin `<option>` para esos valores → nada preseleccionado, banner "Atención" ausente.
  - Después del fix: el mismo request devuelve `<option value="1" selected="selected">`, `<option value="2" selected="selected">` y `<option value="3">`; el banner "Atención: los siguientes componentes están inactivos: Urea, Triglicéridos" ahora se muestra correctamente.

#### Hallazgo 3 — `ProduccionMensual/Detalle` no mostraba `Unidad` del Perfil
- **Causa raíz:** la tabla de líneas del período no tenía columna para ese dato; no era snapshot histórico (a diferencia de `PrecioSnapshot`/`NombreSnapshot`), así que nunca se había cargado ni mapeado.
- **Fix (lookup en vivo, sin snapshot ni migración EF, según lo pedido):**
  - `ProduccionMensualService.GetByIdAsync`: se agregó `.ThenInclude(d => d.Practica)` al include de `Detalles` (antes solo incluía `Detalles` sin la navegación a `Practica`), para poder leer `Practica.Unidad` vigente.
  - `ProduccionDetalleRowViewModel` (`Models/ProduccionMensualViewModels.cs`): se agregó `public int? UnidadPerfil { get; set; }`.
  - `ProduccionMensualController.Detalle`: se pobló `UnidadPerfil = d.TipoItem == TipoItemProduccion.Practica ? d.Practica?.Unidad : null` (null también si el Perfil referenciado fue soft-deleted, ya que la navegación respeta el query filter global — se resuelve igual que otros casos similares en el código existente, con fallback a "—" en la vista).
  - `Views/ProduccionMensual/Detalle.cshtml`: se agregó la columna "Unidad" en `#tablaLineas` (entre "Item" y "Precio"), con `@(linea.UnidadPerfil?.ToString() ?? "—")` — vacío/"—" para líneas de tipo Práctica.
- **Capas afectadas:** Infrastructure (`ProduccionMensualService`), Web (ViewModel, Controller, View). Sin migración EF.
- **Verificado en vivo:** `GET /ProduccionMensual/Detalle/1` muestra "17" en la fila de línea tipo Perfil ("Rutina") y "—" en las líneas de tipo Práctica (Triglicéridos, Creatinina).

#### Método de verificación (los 3 hallazgos)
Se corrió la aplicación localmente (`dotnet run --urls https://localhost:5099`) contra `labipac_dev`, se autenticó vía `curl` (cookie de Identity, usuario seed `no-reply@olvidata.com.ar` / password default `Super123!` de `SeedData.cs`, sin overrides en User Secrets) y se inspeccionó el HTML servido crudo antes y después de cada fix, en vez de asumir por lectura estática — esto fue clave para el Hallazgo 2, donde la lectura de código sola no revelaba el problema (el bug estaba en la intersección de dos servicios: el query filter global de soft-delete de `UnidadBioquimica` + el filtro `Activo` de `GetActivasAsync()`).

#### Build
`dotnet build LabIPAC.slnx` → **Compilación correcta, 0 errores** (mismos warnings preexistentes de NuGet MailKit/MimeKit y el warning CS0114 de `HomeController`, ninguno introducido por esta sesión).

#### Migraciones EF
Ninguna. Los 3 hallazgos se resolvieron con cambios de código (ViewModel/Controller/View/Service) sobre columnas y relaciones ya existentes.

#### Riesgos y supuestos
- El Hallazgo 2 tenía un componente de **pérdida silenciosa de datos** (ítem 4 de la causa raíz) que ya pudo haber afectado Perfiles editados y guardados entre el deploy de la Sesión 3 y este fix, si algún Perfil en Producción tiene composición con `UnidadBioquimica` soft-deleted. Recomendación: verificar en Producción, tras aplicar este fix, si hay Perfiles cuya composición actual no coincide con lo esperado (comparar contra backups/logs si existen).
- El fix de Hallazgo 2 asume que el patrón correcto es "mostrar y preservar" componentes soft-deleted ya asociados (igual criterio que ya usaba el sistema para componentes con `Activo=false`, vía el badge "Inactiva" en `Details.cshtml` y el banner en `Edit.cshtml`) — no se agregó lógica para impedir volver a poner `Activo=true`/restaurar la `UnidadBioquimica` desde esta pantalla, porque no formaba parte del hallazgo reportado.

#### Pruebas mínimas para QA
1. `Practicas/Details` de un Perfil cualquiera: confirmar que se ve la fila "Unidad" con el valor correcto.
2. `Practicas/Edit` del Perfil "Rutina" (u otro con componentes soft-deleted si existe en el ambiente a probar): confirmar que el combo de composición aparece con las Prácticas ya asociadas preseleccionadas, y que el banner "Atención" lista los componentes inactivos/eliminados. Guardar sin tocar el combo y confirmar que la composición no se pierde (recargar Details y comparar).
3. `Practicas/Edit` de un Perfil cuya composición sea 100% de `UnidadBioquimica` activas (caso sin regresión): confirmar que el combo sigue funcionando igual que antes.
4. `ProduccionMensual/Detalle` de un período con líneas de ambos tipos: confirmar columna "Unidad" con el valor numérico en líneas de Perfil y "—" en líneas de Práctica.

#### Checklist de salida para merge
- [x] Build OK (0 errores).
- [x] Los 3 hallazgos reproducidos y verificados en vivo (no solo por lectura de código).
- [x] Causa raíz documentada para los 3, incluyendo el bug de pérdida de datos descubierto en el Hallazgo 2.
- [x] Sin migraciones EF nuevas.
- [x] Sin cambios fuera del alcance de los 3 hallazgos.
- [ ] QA funcional de los 3 fixes (pendiente, agente `agentes-ia-qa`).
- [ ] Confirmación del cliente de que los 3 hallazgos quedaron resueltos.

---

### Sesión 1 — Análisis de integración FABA AOL WS V2
**Fecha:** 2025  
**Estado:** ANÁLISIS COMPLETO — pendiente aprobación para implementar

---

### Sesión 2 — Implementación FABA (Etapas 1–4 + Web Layer)
**Fecha:** 2026-06-17/18  
**Estado:** ✅ BUILD OK — Migración generada, pendiente aplicar a DB (credenciales no configuradas en entorno de desarrollo)

#### Archivos creados

**Application:**
- `LabIPAC.Application/Settings/FabaSettings.cs`
- `LabIPAC.Application/Interfaces/IFabaClient.cs`
- `LabIPAC.Application/Interfaces/IFabaImportService.cs`
- `LabIPAC.Application/DTOs/Faba/FabaMutualDto.cs`
- `LabIPAC.Application/DTOs/Faba/FabaUnidadBioquimicaDto.cs`
- `LabIPAC.Application/DTOs/Faba/FabaAfiliadoRequest.cs`
- `LabIPAC.Application/DTOs/Faba/FabaAfiliadoDto.cs`
- `LabIPAC.Application/DTOs/Faba/FabaImportResumenDto.cs`

**Domain:**
- `LabIPAC.Domain/Entities/Mutual.cs` — hereda SoftDestroyable
- `LabIPAC.Domain/Entities/UnidadBioquimicaFabaCodigo.cs` — sin SoftDestroyable (gestión por campo Activo)
- `LabIPAC.Domain/Entities/Paciente.cs` — extendido con `MutualId`, `DigitoAfiliado`, `RelacionAfiliado`, `TipoDocumentoFabaId`

**Infrastructure:**
- `LabIPAC.Infrastructure/Services/Faba/FabaClient.cs`
- `LabIPAC.Infrastructure/Services/Faba/FabaResponseParser.cs`
- `LabIPAC.Infrastructure/Services/Faba/FabaImportService.cs`

**Web:**
- `LabIPAC.Web/Controllers/FabaController.cs` — acceso `RequireAdministracion`
- `LabIPAC.Web/Models/FabaViewModels.cs`
- `LabIPAC.Web/Views/Faba/Index.cshtml` — listado de mutuales + sincronización
- `LabIPAC.Web/Views/Faba/Analitos.cshtml` — analitos por mutual + vinculación AJAX a UB local
- `LabIPAC.Web/Views/Faba/ConsultarAfiliado.cshtml` — consulta afiliado por DNI o legajo

#### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `LabIPAC.Infrastructure/Data/AppDbContext.cs` | DbSets Mutuales, UnidadesBioquimicasFabaCodigos; config Fluent API; FK Paciente→Mutual |
| `LabIPAC.Infrastructure/DependencyInjection.cs` | Registro FabaSettings, HttpClient "faba", IFabaClient, IFabaImportService |
| `LabIPAC.Web/appsettings.json` | Sección `Faba` placeholder |
| `LabIPAC.Web/Views/Shared/_Layout.cshtml` | Entrada "Integración FABA" en sidebar bajo Administración |

#### Migración EF generada
- Nombre: `AddFabaMutualYAnalitos`
- Script SQL: `docs/labipac/migrations/AddFabaMutualYAnalitos.sql`
- Estado: **generada, pendiente aplicar** (requiere connection string en User Secrets)
- Tablas nuevas: `Mutuales`, `UnidadesBioquimicasFabaCodigos`
- Columnas nuevas en `Pacientes`: `MutualId`, `DigitoAfiliado`, `RelacionAfiliado`, `TipoDocumentoFabaId`

#### Corrección modelo de datos
- ⚠️ FABA "prácticas" (PracticasPorMutual) son **analitos bioquímicos individuales** → mapean a `UnidadBioquimica`, NO a `Practica` (que es un paquete interno del sistema)
- La entidad `UnidadBioquimicaFabaCodigo` reemplaza el nombre `PracticaFabaMapping` del plan original

#### Pendiente (Etapas 5–6)
- [ ] Aplicar migración a DB de desarrollo (configurar User Secrets: `Faba:IdUsuario`, `Faba:Password`)
- [ ] Etapa 5: Módulo Autorizaciones (`AutorizacionFaba`, `ValidarOrdenV4`)
- [ ] Etapa 6: Catálogos auxiliares (Diagnósticos, Prestadores)
- [ ] Integración lookup FABA desde formulario Create/Edit de Paciente

---

## 0. Escaneo de reutilización
No existe `/docs/indice.md` ni otros proyectos en el historial. Implementación desde cero.

---

## 1. Análisis del Web Service FABA AOL V2

**WSDL:** `http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.wsdl`  
**Endpoint SOAP 1.1 / HTTP POST**  
**Auth:** `idUsuario` (int) + `password` (int) en cada llamada  
**Respuestas:** todas retornan `Result: xsd:string` — contiene XML embebido como texto

### 1.1 Inventario completo de operaciones (37)

| # | Operación | Grupo | Parámetros clave (sin auth) |
|---|-----------|-------|-----------------------------|
| 1 | `UsuariosMutuales` | Maestros | — |
| 2 | `DatosMutual` | Maestros | `Idmutual` |
| 3 | `TiposDocumentos` | Maestros | `Idmutual` |
| 4 | `Coseguros` | Maestros | `Idmutual` |
| 5 | `TiposBonos` | Maestros | — |
| 6 | `ConsultarAfiliado` | Afiliados | `Idmutual`, `IdTipoBusqueda`, `strLegajo`, `strDigito`, `strRelacion`, `strTipoDocumento`, `intNroDocumento` |
| 7 | `ConsultarAfiliadoOsde` | Afiliados | `Idmutual`, `IdTipoBusqueda`, `strLegajo`, `strCodSeguridad`, `CodFacturante` |
| 8 | `ConsultarAfiliadoTransaccion` | Afiliados | `NroTransaccion` |
| 9 | `PracticasPorMutual` | Catálogos | `Idmutual` |
| 10 | `DiagnosticosV3` | Catálogos | `Idmutual`, `MuestraCombo` |
| 11 | `Diagnosticos` | Catálogos | (versión anterior de DiagnosticosV3) |
| 12 | `DiagnosticosAlfabetico` | Catálogos | — |
| 13 | `Prestadores` | Catálogos | `Idmutual`, `nombre` (búsqueda) |
| 14 | `UltimoCambioPractica` | Sincronización | `Idmutual` |
| 15 | `UltimoCambioUsuario` | Sincronización | — |
| 16 | `ValidarOrdenV4` | Autorizaciones | `Idmutual`, datos afiliado, datos médico, hasta 24 prácticas (int), coseguro, bono, diagnósticos |
| 17 | `ValidarOrdenfV4` | Autorizaciones | Igual pero prácticas como `string` (lista separada) |
| 18 | `ValidarOrdenV3` | Autorizaciones (old) | Versión anterior de ValidarOrdenV4 |
| 19 | `ValidarOrdenfV3` | Autorizaciones (old) | Versión anterior de ValidarOrdenfV4 |
| 20 | `ValidarOrdenOsde` | Autorizaciones OSDE | Específico OSDE (versión anterior) |
| 21 | `ValidarOrdenOsdeWS` | Autorizaciones OSDE | Específico OSDE (versión actual, hasta 24 prácticas) |
| 22 | `ConsultarOrden` | Gestión órdenes | `Idmutual`, `NroTransaccion` |
| 23 | `ConsultarOrdenConValoresSugeridos` | Gestión órdenes | `Idmutual`, `NroTransaccion` |
| 24 | `ModificarFechaRealizacion` | Gestión órdenes | `NroTransaccion`, `FechaRealizacion` |
| 25 | `SuspenderOrden` | Gestión órdenes | `NroTransaccion` |
| 26 | `EliminarSuspensionOrden` | Gestión órdenes | `NroTransaccion` |
| 27 | `ConsultarSuspension` | Gestión órdenes | `NroTransaccion` |
| 28 | `Recurrir` | Apelaciones | `NroTransaccion`, `Mensaje` |
| 29 | `AgregarBono` | Bonos | `NroTransaccion`, `Coseguro`, `TipoBono`, `NroBono`, `BonoNuevo` |
| 30 | `EliminarBono` | Bonos | `NroTransaccion`, `Coseguro`, `TipoBono`, `NroBono`, `BonoNuevo` |
| 31 | `ConsultarBonos` | Bonos | `NroTransaccion` |
| 32 | `ConsultarTransaccionDeBono` | Bonos | `NroTransaccion` |
| 33 | `AceptarAuditoria` | Auditoría | `NroAutorizacion` |
| 34 | `ConsultaConfirmacionAuditoria` | Auditoría | `NroAutorizacion` |
| 35 | `ConsultarMensajes` | Mensajería | — |
| 36 | `GrabarMensajes` | Mensajería | — |
| 37 | `ValidarUsuario` | Sistema | — |
| 38 | `CambioClave` | Sistema | — |

### 1.2 Notas técnicas del WS
- SOAP 1.1, estilo RPC/encoded (antiguo)
- Todas las respuestas son `Result: xsd:string` conteniendo **XML embebido como string**
- El XML de respuesta debe parsearse con `XDocument.Parse(result)`
- `ProcessingId` = GUID generado por el cliente por llamada
- `Terminal` = identificador de la máquina cliente (ej: nombre del host)
- **No usa WS-Security** — credenciales van en el body de cada operación

---

## 2. Funcionalidades del WS relevantes para LabIPAC

### Prioridad ALTA — Impacto directo en flujo de trabajo

| Funcionalidad | Operaciones WS | Módulo LabIPAC afectado |
|---|---|---|
| Maestro de Mutuales sincronizado | `UsuariosMutuales`, `DatosMutual` | Nuevo módulo `Mutuales` |
| Validación/búsqueda de afiliado | `ConsultarAfiliado`, `ConsultarAfiliadoOsde` | Módulo `Pacientes` (lookup en carga) |
| Catálogo de prácticas por mutual | `PracticasPorMutual`, `UltimoCambioPractica` | Módulo `Practicas` (mapeo FABA codes) |
| Autorización de órdenes | `ValidarOrdenV4`, `ValidarOrdenfV4` | Nuevo módulo `Autorizaciones` |
| Consulta de orden autorizada | `ConsultarOrden`, `ConsultarOrdenConValoresSugeridos` | Nuevo módulo `Autorizaciones` |

### Prioridad MEDIA

| Funcionalidad | Operaciones WS | Módulo LabIPAC afectado |
|---|---|---|
| Gestión de bonos/coseguros | `AgregarBono`, `EliminarBono`, `ConsultarBonos` | Módulo `Autorizaciones` (sub-flujo) |
| Diagnósticos CIE-10 | `DiagnosticosV3` | Nuevo módulo `Diagnosticos` (catálogo) |
| Modificar / suspender órdenes | `ModificarFechaRealizacion`, `SuspenderOrden`, etc. | Módulo `Autorizaciones` |
| Prestadores médicos | `Prestadores` | Nuevo catálogo `Prestadores` |
| Apelaciones | `Recurrir` | Módulo `Autorizaciones` |

### Prioridad BAJA (backlog)

| Funcionalidad | Operaciones WS |
|---|---|
| Auditoría médica FABA | `AceptarAuditoria`, `ConsultaConfirmacionAuditoria` |
| Mensajería interna FABA | `ConsultarMensajes`, `GrabarMensajes` |
| Soporte OSDE específico | `ValidarOrdenOsdeWS`, `ConsultarAfiliadoOsde` |
| Gestión de credenciales | `ValidarUsuario`, `CambioClave` |

---

## 3. Plan de implementación por etapas

### Etapa 1 — Infraestructura SOAP y configuración (prereq de todo)

**Objetivo:** cliente SOAP reutilizable, configuración segura de credenciales.

**Archivos a crear:**
- `LabIPAC.Application/Settings/FabaSettings.cs` — POCO con `IdUsuario`, `Password`, `TerminalId`, `EndpointUrl`
- `LabIPAC.Application/Interfaces/IFabaClient.cs` — interfaz de bajo nivel (enviar/recibir SOAP)
- `LabIPAC.Application/Interfaces/IFabaService.cs` — interfaz de alto nivel (métodos de negocio)
- `LabIPAC.Infrastructure/Services/Faba/FabaClient.cs` — implementación HTTP SOAP (raw envelope, `IHttpClientFactory`)
- `LabIPAC.Infrastructure/Services/Faba/FabaResponseParser.cs` — parseador `XDocument` de respuestas
- `appsettings.json` (sección `Faba`) — sólo placeholder, sin credenciales reales
- User Secrets: `Faba:IdUsuario` y `Faba:Password`

**Técnica:** `IHttpClientFactory` + SOAP 1.1 envelope generado dinámicamente (sin WCF). Evitar `dotnet-svcutil` ya que el WSDL es RPC/encoded y genera código difícil de mantener en .NET 10.

**Patrón SOAP envelope:**
```xml
POST http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.asmx
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://tempuri.org/{OperationName}"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
	<{OperationName} xmlns="http://tempuri.org/">
	  <idUsuario>5903</idUsuario>
	  <password>8491</password>
	  <!-- params -->
	</{OperationName}>
  </soap:Body>
</soap:Envelope>
```

---

### Etapa 2 — Módulo Mutuales (maestro sincronizado)

**Objetivo:** Entidad `Mutual` local sincronizada con `UsuariosMutuales` + `DatosMutual`.

**Domain:**
- Nueva entidad `Mutual : SoftDestroyable`
  - `IdFaba` (int) — clave del WS, unique index
  - `Nombre` (string)
  - `CodigoFacturante` (int?)
  - `EsOsde` (bool) — para bifurcar entre ValidarOrdenV4 / ValidarOrdenOsdeWS
  - `Activo` (bool)

**Application:**
- `IFabaService.SincronizarMutualesAsync()` → llama `UsuariosMutuales`, upsert en DB

**Infrastructure:**
- `FabaService.SincronizarMutualesAsync()`

**Web:**
- `MutualesController` — CRUD local + botón "Sincronizar con FABA"
- Vista `Index` con DataTables server-side, badge activo/inactivo, columna `IdFaba`

**Migración EF:** `AddMigration AddMutual`

---

### Etapa 3 — Mapeo Prácticas ↔ FABA por mutual

**Objetivo:** Cada `Practica` local tiene un código FABA por mutual para poder incluirla en una autorización.

**Domain:**
- Nueva entidad `PracticaFabaMapping : SoftDestroyable`
  - `PracticaId` (FK → Practica)
  - `MutualId` (FK → Mutual)
  - `CodigoFaba` (int) — `IdPractica` del WS
  - Índice único (`PracticaId`, `MutualId`)

**Application:**
- `IFabaService.SincronizarPracticasAsync(int mutualId)` → llama `PracticasPorMutual`, upsert mappings
- `IFabaService.UltimoCambioPracticaAsync(int mutualId)` → para invalidar caché

**Web:**
- En `PracticasController.Edit`: nueva sección "Códigos FABA por mutual" — tabla de mappings

**Migración EF:** `AddMigration AddPracticaFabaMapping`

---

### Etapa 4 — Lookup de afiliado en módulo Pacientes

**Objetivo:** Al crear/editar un paciente, buscar en FABA para completar datos de mutual y validar afiliación.

**Domain — expansión `Paciente`:**
- `MutualId` (int?, FK → Mutual)
- `DigitoAfiliado` (string?) — `strDigito` del WS
- `RelacionAfiliado` (string?) — `strRelacion` (titular/familiar)
- `TipoDocumentoFabaId` (int?) — tipo de documento según la mutual

**Application:**
- `IFabaService.ConsultarAfiliadoAsync(FabaAfiliadoRequest)` → devuelve `FabaAfiliadoDto`
- DTO `FabaAfiliadoDto`: NombreCompleto, Sexo, FechaNacimiento, NroAfiliado, Mutual, Estado

**Web:**
- `PacientesController`: nuevo endpoint `[HttpGet] BuscarAfiliadoFaba` (AJAX, devuelve JSON)
- En `Create`/`Edit` Paciente: botón "Buscar en FABA" que dispara AJAX y pre-completa campos

**Migración EF:** `AddMigration PacienteAddMutualFields`

---

### Etapa 5 — Módulo Autorizaciones (core)

**Objetivo:** Registrar y gestionar autorizaciones de órdenes FABA.

**Domain:**
- Nueva entidad `AutorizacionFaba : SoftDestroyable`
  - `PacienteId` (FK → Paciente)
  - `MutualId` (FK → Mutual)
  - `NroTransaccion` (int?) — asignado por FABA al autorizar
  - `NroAutorizacion` (string?) — número legible de autorización
  - `Estado` (enum `EstadoAutorizacion`: Borrador, Autorizada, Rechazada, Suspendida, Apelada)
  - `FechaPrescripcion` (DateOnly)
  - `FechaRealizacion` (DateOnly)
  - `NombreMedico` (string)
  - `MatriculaMedico` (string)
  - `TipoMatricula` (string) — Nacional/Provincial
  - `IdDiagnostico1` (string?), `IdDiagnostico2` (string?)
  - `Telefono` (string?)
  - `Observacion` (string?)
  - `TipoBono` (int?), `NroBono` (int?), `Coseguro` (int?)
  - `RespuestaXmlFaba` (string?) — XML completo de respuesta para auditoría
  - Navegación: `ICollection<AutorizacionDetalle>`

- Nueva entidad `AutorizacionDetalle`
  - `AutorizacionFabaId` (FK)
  - `PracticaId` (FK → Practica)
  - `CodigoFaba` (int) — código enviado al WS
  - `Orden` (int) — posición 1..24

**Application:**
- `IFabaService.ValidarOrdenAsync(FabaOrdenRequest)` → devuelve `FabaOrdenResultDto`
- `IFabaService.ConsultarOrdenAsync(int mutual, int nroTransaccion)` → estado actual
- `IFabaService.SuspenderOrdenAsync(int nroTransaccion)`
- `IFabaService.RecurrirAsync(int nroTransaccion, string mensaje)`
- DTO `FabaOrdenRequest`, `FabaOrdenResultDto`

**Web:**
- `AutorizacionesController`: CRUD completo + acción `Autorizar` (POST → WS → guarda resultado)
- Vistas: `Index` (DataTables server-side), `Create`, `Details`, `Autorizar` (wizard 3 pasos)

**Migración EF:** `AddMigration AddAutorizacionFaba`

---

### Etapa 6 — Diagnósticos y Prestadores (catálogos auxiliares)

**Objetivo:** Catálogos locales con sincronización on-demand.

**Domain:**
- `DiagnosticoFaba` (sin herencia SoftDestroyable — sólo lectura): `Codigo`, `Descripcion`, `MutualId`
- `Prestador` (sin herencia): `IdFaba`, `Nombre`, `MutualId`

**Application:** `IFabaService.ObtenerDiagnosticosAsync(int mutual)`, `IFabaService.BuscarPrestadoresAsync(int mutual, string nombre)`

**Web:** Endpoints AJAX para autocompletar en formulario de autorización.

---

## 4. Cambios por capa — resumen

| Capa | Nuevos archivos | Archivos modificados |
|------|----------------|---------------------|
| Domain | `Mutual`, `PracticaFabaMapping`, `AutorizacionFaba`, `AutorizacionDetalle`, `DiagnosticoFaba`, `Prestador` + enum `EstadoAutorizacion` | `Paciente` (+ campos mutual) |
| Application | `IFabaClient`, `IFabaService`, `FabaSettings`, DTOs: `FabaAfiliadoDto`, `FabaOrdenRequest`, `FabaOrdenResultDto` | — |
| Infrastructure | `FabaClient`, `FabaService`, `FabaResponseParser` + config `AddFabaServices()` | `AppDbContext` (DbSets nuevos + config Fluent) |
| Web | `MutualesController`, `AutorizacionesController` + ViewModels + Vistas | `PacientesController` + vista Create/Edit, `appsettings.json`, `Program.cs` |

---

## 5. Migraciones EF requeridas

```
1. AddMutual
2. AddPracticaFabaMapping
3. PacienteAddMutualFields
4. AddAutorizacionFaba
5. AddCatalogsFabaAux  (DiagnosticoFaba, Prestador)
```

---

## 6. Configuración segura de credenciales

**appsettings.json** (placeholder sin valor real):
```json
"Faba": {
  "EndpointUrl": "http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.asmx",
  "IdUsuario": 0,
  "Password": 0,
  "TerminalId": "LABIPAC-01",
  "TimeoutSeconds": 30
}
```

**User Secrets (desarrollo) — ejecutar:**
```powershell
dotnet user-secrets set "Faba:IdUsuario" "5903" --project LabIPAC.Web
dotnet user-secrets set "Faba:Password"  "8491" --project LabIPAC.Web
```

**Producción:** variables de entorno `Faba__IdUsuario` / `Faba__Password`.  
❌ **NUNCA hardcodear credenciales en código ni en appsettings.Production.json**.

---

## 7. Paquetes NuGet necesarios

| Paquete | Capa | Justificación |
|---------|------|---------------|
| Ninguno nuevo | — | Se usa `IHttpClientFactory` (ya en `Microsoft.AspNetCore.App`) + `System.Xml.Linq` (BCL). No se necesita WCF ni `dotnet-svcutil` |

---

## 8. Riesgos y supuestos

| Riesgo | Mitigación |
|--------|------------|
| El WS responde con XML mal formado o con entidades HTML | `FabaResponseParser` debe ser tolerante; loguear raw response |
| Timeout en validaciones (el WS es lento) | `TimeoutSeconds` configurable; mostrar spinner en UI |
| Mutual OSDE requiere flujo diferente (`ValidarOrdenOsdeWS`) | Campo `EsOsde` en `Mutual` bifurca la lógica en `FabaService` |
| Los códigos de prácticas FABA difieren entre mutuales | `PracticaFabaMapping` resuelve el M:N |
| Respuestas varían entre mutuales (no todas implementan todo) | Manejo defensivo en parser, `ServiceResult.IsSuccess = false` con detalle |
| WSDL en HTTP (no HTTPS) | Riesgo en producción; usar proxy HTTPS si es posible |

---

## 9. Decisión de arquitectura

- **No usar WCF / `dotnet-svcutil`**: el WSDL es RPC/encoded (no Document/Literal), genera proxies difíciles de mantener en .NET 10. En su lugar, envelopes SOAP construidos con interpolación de strings o `XDocument`, enviados con `HttpClient`.
- **`IFabaClient`** (Infrastructure): responsable del transporte HTTP SOAP puro.
- **`IFabaService`** (Application interface / Infrastructure impl): responsable de la lógica de negocio, mapeo de DTOs y orquestación.
- **No exponer `FabaClient` a Controllers**: los controllers solo inyectan `IFabaService`.

---

## 10. Próximos pasos (pendiente aprobación)

- [ ] Aprobar plan por etapas
- [ ] Comenzar Etapa 1 (cliente SOAP + config)
- [ ] Test de conectividad con `ValidarUsuario` antes de continuar
- [ ] Definir qué mutuales están activas (de `UsuariosMutuales`) para priorizar Etapa 3
