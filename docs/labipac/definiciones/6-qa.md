# Memoria QA

Proyecto: labipac
Ultima actualizacion: 2026-07-08 (sesion 2 — QA de M7 Unidad/PrecioPorUnidad + M8 Carga masiva/alta rapida + M9 fix PDF)

---

## Nomenclatura de dominio vigente

UnidadBioquimica -> label Practica en UI
Practica (entidad) -> label Perfil en UI
TipoItemProduccion.Practica -> badge Perfil
TipoItemProduccion.UnidadBioquimica -> badge Practica

---

## Maquina de estados

No aplica. P4-A confirmado: periodo siempre editable, sin cierre.
Estados de entidades: Activa / Inactiva via soft delete (DeletedAt).
M7/M8/M9 no introducen estados nuevos (confirmado en diseno sesion 2).

---

## Sesion 2 (2026-07-08) — QA de M7 + M8 + M9

Input: `1-analista-funcional.md` sesion 4, `2-disenador-funcional.md` sesion 2 (HU-01 a HU-05, RN-12 a RN-21), `3-arquitecto-mvc.md` sesion 2, `4-presupuestador.md` SESION 3 (pruebas minimas sugeridas), `5-implementador.md` Sesion 3 — todos cerrados.

### Metodo de verificacion
- Lectura completa de codigo real tocado (no solo memoria documental): `PreciosController.cs`, `PracticasController.cs`, `PracticaService.cs`, `ProduccionMensualService.cs`, `ProduccionMensualController.cs`, `ProduccionMensualViewModels.cs`, `PracticaViewModels.cs`, migracion `AddPracticaUnidadYPrecioPorUnidad`, vistas `Practicas/Index.cshtml`, `Create.cshtml`, `Edit.cshtml`, `Precios/AumentoMasivo.cshtml`, `ProduccionMensual/CargaMasiva.cshtml` + 2 partials, `ProduccionMensual/Detalle.cshtml`.
- Build real: `dotnet build LabIPAC.Web/LabIPAC.Web.csproj -c Debug` -> Compilacion correcta, 0 errores, 8 warnings preexistentes (NuGet MailKit/MimeKit, no introducidos por esta sesion).
- Verificacion de datos reales contra `labipac_dev` via `mysqlsh` (foco de riesgo pedido): confirmado backfill de `Unidad` correcto — Perfil "Rutina" Id=1, PrecioActual=$15000.00, Unidad=17 (=ROUND(15000/892.03)), sin precios en $0. `PreciosPorUnidad` tiene la fila seed (Id=1, Valor=892.03, sin soft-delete). `__EFMigrationsHistory` confirma la migracion `20260708175303_AddPracticaUnidadYPrecioPorUnidad` aplicada como ultima entrada.
- Confirmado por lectura de codigo que `PreciosController` (F-001) ya NO ofrece ni opera sobre Perfiles: `AumentoMasivo`, `Previsualizar` y `AplicarAumento` trabajan exclusivamente sobre `UnidadBioquimica`. Vista `AumentoMasivo.cshtml` no tiene tab/seccion de Perfiles, solo tabla de Practicas + nota informativa.
- Confirmado por lectura de codigo que `AgregarLineasAsync` (M8) es atomico: todas las validaciones (RN-13 duplicados en batch, cantidad >=1, item activo/existente, RN-04 duplicado contra lineas ya existentes) ocurren ANTES de tocar el `DbContext`; recien al final se hace `AddRangeAsync` + un unico `SaveChangesAsync`. Si cualquier fila es invalida, la funcion retorna error sin persistir nada (no hay tracking previo de entidades).
- Confirmado que `ProduccionCargaMasivaViewModel.Filas` tiene default `= new()` (lista vacia), a diferencia del patron que causo GAN-001 (lista con 1 fila "fantasma" precargada en el constructor) — el guard `model.Filas == null || model.Filas.Count == 0` en el controller SI se dispara correctamente si no se envia ninguna fila.
- Revisado `PracticaService.CreateAsync`/`UpdateAsync`: no queda ningun resto de la validacion RN-01 (precio < sumatoria) ni de RN-02 (minimo 1 componente) — ambas correctamente removidas del flujo de guardado, consistente con la derogacion/relajacion documentada.

### Cobertura por criterio de aceptacion

| HU / Criterio | Resultado | Evidencia |
|---|---|---|
| HU-01 AC1 (agregar N filas dinamicamente) | PASS (revision de codigo) | `CargaMasiva.cshtml` JS `agregarFila()` clona fila y reindexa; requiere confirmacion manual de UX (ver plan de pruebas manuales) |
| HU-01 AC2 (un submit persiste todas las filas validas) | PASS | `AgregarLineasAsync` un unico `SaveChangesAsync` |
| HU-01 AC3 (fila invalida -> no se guarda ninguna, errores por fila) | PASS parcial | Atomicidad confirmada (backend). Los errores se muestran como lista general (`ModelState.AddModelError(string.Empty, ...)`), no anclados a la fila puntual — ver hallazgo QA-F1 (minor) |
| HU-02 AC1 (opcion "+ Crear nuevo..." en selector) | PASS | presente en `select-item` de cada fila y en `agregarFila()` |
| HU-02 AC2 (nuevo registro aparece seleccionado sin recargar) | PASS (revision de codigo) | `poblarSelectItem(..., res.id)` tras AJAX exitoso, sin `location.reload()` en ese flujo — requiere confirmacion manual |
| HU-02 AC3 (alta rapida de Perfil no exige composicion) | PASS | `CrearPerfilRapido` llama `CreateAsync(practica, new List<int>())` |
| HU-03 AC1 (valor vigente destacado en listado) | PASS | badge `#badgeValorVigente` en card "Precio por Unidad" |
| HU-03 AC2 (editar a mano y guardar) | PASS | `ActualizarPrecioPorUnidad` + input `#inputNuevoValor` |
| HU-03 AC3 (aumento % con confirmacion previa) | PASS | SweetAlert2 `aplicarPrecioPorUnidad()` antes de `$.post` |
| HU-03 AC4 (recalculo batch visible en listado) | PASS | `ActualizarPrecioPorUnidadAsync` recalcula todas las Practicas activas en la misma operacion; vista hace `location.reload()` tras exito |
| HU-04 AC1 (sin campo precio editable en Create/Edit) | PASS | `Create.cshtml`/`Edit.cshtml` sin input de precio, solo "Unidad" |
| HU-04 AC2 (precio calculado en vivo) | PASS | JS `calcularPrecio()` en ambas vistas |
| HU-04 AC3 (AumentoMasivo ya no permite editar Perfiles) | PASS | confirmado por lectura de `PreciosController.cs` y `AumentoMasivo.cshtml` |
| HU-05 (PDF sin recorte en montos 4+ digitos) | PASS | `ConstantColumn(75)` para "Precio unit." (antes 55), `ConstantColumn(60)` para "Tipo" (antes 65) — requiere confirmacion visual manual |
| RA-06 (backfill evita precio $0) | PASS | verificado contra `labipac_dev`: Perfil "Rutina" Unidad=17, PrecioActual=$15000, sin registros en 0 |

### Hallazgos QA (no bloqueantes)

**QA-F1 (minor, UX)** — Carga masiva: la validacion RN-13 (duplicados TipoItem+ItemId en el mismo envio) solo se valida client-side de forma parcial: el JS de submit (`$('#formCargaMasiva').on('submit', ...)`) valida item seleccionado + cantidad >=1 por fila, pero NO detecta duplicados antes de enviar. El servidor si los detecta y bloquea el guardado completo (atomicidad preservada, sin riesgo de dato corrupto), pero el mensaje de error se muestra como alerta general arriba del formulario, no señalado en la fila puntual duplicada, a diferencia de lo que sugiere el texto del HU-01 AC3 ("se muestran los errores puntuales por fila"). No es un bug funcional (el guardado bloquea correctamente), es una mejora de UX pendiente. Se recomienda al implementador (fuera de este alcance de QA, no autofix por no ser un bug catalogado) resaltar la fila duplicada si se decide iterar.

**QA-F2 (informativo, sin accion)** — `PracticaService.ObtenerPrecioPorUnidadVigenteAsync()` usa `_context.PreciosPorUnidad.FirstOrDefaultAsync()` sin `OrderBy` explicito. Es seguro mientras se respete el patron de fila unica (enforced en Service, confirmado que solo hay 1 fila en `labipac_dev`), pero si en el futuro se corrompiera esa invariante (2+ filas), el resultado seria no determinista. No es un bug reproducible hoy, se documenta como observacion de robustez.

**QA-F3 (informativo, patron heredado no regresionado)** — Los endpoints `ActualizarPrecioPorUnidad` / `AumentarPrecioPorUnidadPorcentaje` (`RequireAdministracion`) son llamados via `$.post` desde `Practicas/Index.cshtml`, visible para cualquier usuario autenticado (la vista `Index` solo tiene `[Authorize]` de clase). Si un usuario no-Administrador hace click, `[Authorize(Policy=...)]` puede redirigir a AccessDenied en vez de devolver JSON, y el `.done()`/`success` del `$.post` recibiria HTML en vez de `{success:false}` (mismo patron ya usado por `ActualizarIva` de F-002, no introducido por esta sesion). Riesgo bajo dado que el sistema es de uso unico/monousuario segun el analisis funcional original. No requiere autofix.

### Verificacion de dato — labipac_dev (evidencia cruda)

```
Practicas: Id=1, Nombre=Rutina, Unidad=17, PrecioActual=15000.00, Activo=1, DeletedAt=NULL
PreciosPorUnidad: Id=1, Valor=892.03, DeletedAt=NULL
__EFMigrationsHistory (ultima): 20260708175303_AddPracticaUnidadYPrecioPorUnidad
```

---

## Reglas de negocio cubiertas (acumulado)

RN-01: DEROGADA 2026-07-08 (verificado: ya no se valida en `PracticaService`)
RN-02: RELAJADA GLOBALMENTE 2026-07-08 (verificado: sin minimo de componentes en Create/Edit ni en alta rapida)
RN-03: Snapshot precio inmutable retroactivamente
RN-04: No duplicar mismo item en mismo periodo (heredada, tambien aplicada dentro de `AgregarLineasAsync`)
RN-05: Precio AJAX pre-completado al seleccionar item
RN-06: Aviso visual periodo historico
RN-07: Cantidad entero >= 1
RN-08: PrecioSnapshot >= 0
RN-09: Solo items activos en nuevas lineas
RN-10: Total recalculado en tiempo real
RN-11: No duplicar periodo mismo mes+anio
RN-12: Carga masiva atomica (verificado: un unico SaveChangesAsync, validaciones previas)
RN-13: Sin duplicados TipoItem+ItemId en el mismo envio de carga masiva (verificado server-side; ver QA-F1 sobre validacion cliente parcial)
RN-14: Alta rapida de Perfil sin composicion obligatoria
RN-15: Alta rapida de Practica igual al ABM existente
RN-16: PrecioActual(Perfil) = Unidad x PrecioPorUnidad vigente (verificado en Create/Update/recalculo batch)
RN-17: Unidad entero >= 1 (DataAnnotation + Domain)
RN-18: PrecioPorUnidad.Valor >= 0
RN-19: Aumento % con redondeo AwayFromZero, 2 decimales (mismo criterio que F-001)
RN-20: Confirmacion formal de derogacion de RN-01
RN-21: `Precios/AumentoMasivo` ya no ofrece ni afecta Perfiles (verificado)

---

## Casos de prueba

TC-UB-01 a TC-UB-07 PASS - modulo Practicas (UI: Practicas/UnidadBioquimica)
TC-P-01 a TC-P-07 PASS - modulo Perfiles (base, sesion anterior)
TC-PM-01 a TC-PM-15 PASS - modulo Produccion Mensual (base, sesion anterior)
TC-PM-08: BUG-001 CORREGIDO - Eliminar linea ahora funciona (sesion anterior).

TC-M7-01: Crear Perfil con Unidad=5 -> PrecioActual = 5 x PrecioPorUnidadVigente. PASS (codigo).
TC-M7-02: Editar Perfil cambiando Unidad -> precio recalculado. PASS (codigo).
TC-M7-03: Editar PrecioPorUnidad a mano -> recalculo batch de todos los Perfiles activos. PASS (codigo + logica batch confirmada).
TC-M7-04: Aplicar aumento % sobre PrecioPorUnidad -> nuevo valor + recalculo batch. PASS (codigo, redondeo AwayFromZero).
TC-M7-05: `Precios/AumentoMasivo` no ofrece Perfiles ni aplica cascade. PASS (codigo).
TC-M7-06: Backfill de Perfiles preexistentes no deja precio $0. PASS (verificado contra labipac_dev).
TC-M8-01: Cargar 3+ filas mixtas (Perfil + Practica) en un submit -> guardado atomico. PASS (codigo, requiere confirmacion manual UI).
TC-M8-02: Forzar fila invalida (cantidad <1 o duplicado) mezclada con filas validas -> no se guarda ninguna. PASS (codigo: validacion completa antes de cualquier `Add`).
TC-M8-03: Alta rapida de Perfil y Practica desde modales -> aparecen seleccionados sin recargar. PASS (codigo, requiere confirmacion manual UI).
TC-M9-01: PDF con montos de 4+ digitos en "Precio unit." -> sin corte de digitos. PASS (codigo: columna ampliada a 75pt; requiere confirmacion visual manual).

---

## Bugs resueltos

BUG-001 [2026-06-15] CRITICAL
Modulo: Produccion Mensual / Eliminar linea
Causa: site.js usaba closest-form ignorando data-form del boton externo al form.
Fix: getElementById con data-form attribute en site.js
Verificacion: codigo inspeccionado + build OK + suite 50/50 PASS

Sin bugs funcionales nuevos reproducidos en la sesion 2 (M7+M8+M9). QA-F1/F2/F3 son hallazgos no bloqueantes (ver seccion arriba), sin autofix aplicado por no tratarse de bugs reproducidos (son observaciones de robustez/UX).

---

## Evidencia sesion 2026-06-15

Suite 50 checks: 29 positivos + 21 negativos = 50/50 PASS
Build: OK
Renombre: Unidades Bioquimicas -> Practicas; Practicas -> Perfiles
Tildes: Layout, Home, ProduccionMensual, Practicas

---

## Historial

2026-06-15: Primera carga QA. Fix BUG-001. Renombre UI. Tildes. 50/50 PASS. Build OK.
2026-07-08: QA de M7 (Unidad/PrecioPorUnidad + simplificacion F-001) + M8 (Carga masiva + alta rapida atomica) + M9 (fix PDF). Verificacion por codigo real + build + consulta directa a `labipac_dev` via mysqlsh (foco de riesgo: backfill de Unidad, PreciosController sin Perfiles, atomicidad de AgregarLineasAsync). Sin bugs bloqueantes. 3 hallazgos menores no bloqueantes (QA-F1 UX carga masiva, QA-F2 robustez PrecioPorUnidad sin OrderBy, QA-F3 patron heredado de autorizacion AJAX). Catalogo cross-proyecto ejecutado: mayoria N/A por falta de modulo equivalente (stock/variantes/compras/ventas/camaras/notificaciones/autorizaciones), sin regresiones de los patrones aplicables (RowVersion MySQL, EF6 dynamic OrderBy, lista con fila fantasma tipo GAN-001, template+partial tipo GAN-003, delete fuera de form tipo KOI-001). Checklist de salida para merge: PASS, pendiente ejecucion manual de UI por el usuario y aplicar migracion a Produccion.
