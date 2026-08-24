# Memoria QA

Proyecto: labipac
Ultima actualizacion: 2026-08-23 (sesion 3 — QA de M19–M25 Precio por Unidad Bioquimica y por Perfil segun Centro de Salud)

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

## Sesion 3 (2026-08-23) — QA de M19–M25 (Precio por Unidad Bioquimica y por Perfil segun Centro de Salud)

Input: `1-analista-funcional.md` sesion 6, `2-disenador-funcional.md` sesion 6 (HU-10/HU-11/HU-12, RN-25 a RN-33), `3-arquitecto-mvc.md` sesion 6 (RA-13/RA-15/RA-17/RA-18), `4-presupuestador.md` SESION 5 (pruebas minimas M19-M24), `5-implementador.md` Sesion 5 + Sesion 5 bis (M25).
**Nota de gate:** el gate de aprobacion formal del presupuesto fue salteado por instruccion explicita del usuario del estudio. Primera verificacion independiente del alcance.

### Metodo de verificacion
- Build real: `dotnet build LabIPAC.slnx` -> Compilacion correcta, **0 errores, 9 warnings**, todos preexistentes (NU1902 MailKit/MimeKit, CS0114 `HomeController.StatusCode`). Sin warnings nuevos, antes y despues del auto-fix.
- Lectura de codigo real de todo lo tocado: `ProduccionMensualService.GetPrecioVigenteAsync`, `PracticaService` (RN-33, cascada, batch, solver M25), `UnidadBioquimicaService`, `PrecioPorUnidadCentroSaludService`, `ProduccionMensualController`, `PreciosPorCentroController`, `UnidadesBioquimicasController`, `PracticasController`, VMs y las 12 vistas modificadas/nuevas.
- **Verificacion en vivo con la app corriendo** (`dotnet run`, HTTPS 7200, login real con cookie de Identity + antiforgery) contra `labipac_dev`, incluyendo flujos de escritura. Backup completo (`mysqldump`) tomado antes de escribir y **restaurado al terminar**: `labipac_dev` quedo byte a byte en su estado pre-QA (verificado por query; 0 filas residuales `ZZ QA%`, migracion intacta, sin bases temporales).
- Catalogo cross-proyecto `docs/qa/regresiones-manuales.yml` cargado y ejecutado sobre los modulos equivalentes.
- **Declaracion de herramientas (`33-verificacion-automatizada-qa`):** el servidor MCP `playwright` **no estuvo disponible en esta sesion** (sus herramientas `mcp__playwright__*` no fueron expuestas). Se cayo al procedimiento alternativo previsto: app levantada localmente + cliente HTTP autenticado con cookie real de Identity y token antiforgery, verificando el HTML servido y el estado de la base tras cada accion. Cubre lo verificable por assertion (renderizado de mensajes, valores calculados, persistencia, codigos de respuesta); **queda pendiente de confirmacion manual por el usuario lo estrictamente visual/interactivo**: comportamiento de los modales de alta rapida y del Select2, marcado en rojo de la fila bloqueada en Carga Masiva, confirmacion SweetAlert2 del aumento %, y revision visual del PDF.

### Cobertura por criterio de aceptacion

| HU / Modulo / Criterio | Resultado | Evidencia (en vivo salvo aclaracion) |
|---|---|---|
| **RA-15** — cambio de firma `GetPrecioVigenteAsync`, revision de TODOS los callers | **PASS** | `grep` exhaustivo: 1 solo caller (`GetPrecioItem`). Los 2 puntos que calculan el multiplicador para la vista (`Detalle`, `ConstruirCargaMasivaViewModelAsync`) ramifican bien por `CentroSaludId`. **Probado en vivo:** periodo 5 (centro con $1.100) / Perfil `Unidad=17` -> `{"precio":18700.00}` = 17x1100, **no** el de referencia global 15619,43 |
| HU-11 / RN-28 — precio de Practica = `CantidadUnidades x PrecioUnidad(centro)` | PASS | CREATININA `CantidadUnidades=5`, centro $1.100 -> `{"precio":5500.00}`; linea persistida con ese snapshot |
| HU-11 / RN-28 — precio de Perfil = `Unidad x PrecioUnidad(centro)` | PASS | 17 x 1100 = 18700 |
| HU-11 / RN-28.a — bloqueo si el centro no tiene precio cargado | PASS | mensaje accionable con nombre del centro + ruta a Precios por Centro |
| HU-11 / RN-28.b — bloqueo si el item no tiene volumen calculable | PASS | mensaje accionable con nombre de la practica + ruta a Practicas > Editar |
| **RN-29** — periodos historicos con `CentroSaludId = NULL` | **PASS** | periodos 1 y 6 (preexistentes) siguen cotizando al precio de referencia (15619,43 / 3675,16 / 4593,95), se pueden editar y agregar lineas sin exigir centro. Sin migracion ni cambio de esos datos |
| **RN-25** — Centro de Salud obligatorio en periodos NUEVOS | **PASS** | selector sin "— Global —" (solo placeholder "— Seleccion&aacute; un Centro de Salud —"); POST sin centro rechazado, nada creado |
| RN-24 — unicidad Mes+Anio+Centro | PASS (funcional) | duplicado exacto bloqueado; mismo Mes+Anio con otro centro permitido. Mensaje NO era visible -> ver **QA-S3-01** |
| **HU-12 / M19 / RN-32** — ABM de Practica pide `CantidadUnidades`, precio solo lectura | PASS | form sin input de `PrecioActual`; `CantidadUnidades=5` -> `PrecioActual` 4593,95 = 5 x 918,79 |
| **HU-04 / M20 / RN-33** — `Unidad` del Perfil calculada por composicion | PASS | Perfil con 2 componentes (5 + 3) -> `Unidad=8`, `PrecioActual=7350,32`. Campo `Unidad` en la vista es `readonly disabled` |
| **M20 / RN-02 REACTIVADA** — Perfil sin composicion no se puede crear | PASS | POST sin composicion -> se queda en el form con "Seleccion&aacute; al menos una practica..."; **nada creado** (verificado por query) |
| **RA-18 / DD-09 / M20** — recalculo en cascada al editar `CantidadUnidades` de un componente | **PASS** | Practica A 5->10 -> el Perfil que la usa pasa de `Unidad` 8 a 13 y precio 11944,27 automaticamente. **El Perfil que NO la usa ("Rutina") quedo intacto** (consulta inversa correcta, no es un batch global) |
| Control de la cascada — editar solo el nombre NO debe reescribir Perfiles | PASS | `UpdatedAt` del Perfil sin cambios tras editar solo el nombre (decision 2 del implementador confirmada) |
| **RA-17 caso (b)** — cambiar el `PrecioPorUnidad` GLOBAL recalcula tambien `Unidad` | **PASS (confirmado, y es el riesgo mas serio de la entrega)** | 918,79 -> 1000: "Se recalcularon 2 perfil(es)"; el Perfil sano paso a 13x1000=13000 y **"Rutina" cayo de `Unidad`=17 a 0 y de $15.619,43 a $0,00**, sin que nadie lo tocara. Ver **RL-1** |
| Decision 4 del implementador — `UnidadBioquimica.PrecioActual` NO entra al batch global | PASS (comportamiento) / ver **QA-S3-02** | tras el cambio global las 3 practicas conservaron su `PrecioActual` viejo. Preserva F-001 como se documento, pero deja el precio de referencia visiblemente desfasado |
| **M21 / RN-27** — precio por centro, aumento % aislado | PASS | centro A $1.000 y centro B $500; aumento 10% sobre A -> $1.100 y **B intacto en $500**. Upsert sin violar el indice unico |
| **M22 / RN-30 / M23** — alta rapida ajustada | PASS | Perfil sin composicion -> `{"success":false}`; con composicion -> crea con `unidad` calculada (13); Practica -> pide `cantidadUnidades`, no precio |
| **M24** — reporte de diagnostico | PASS | detecta correctamente "Rutina" como *Sin composicion* (sus 2 componentes estan soft-deleted) y las practicas sin `CantidadUnidades`. Ver **QA-S3-03** sobre el texto del mensaje |
| **M25** — solver de sugerencias, incl. el bug que el implementador corrigio | **PASS** | escenario armado en vivo: 2 Perfiles con la misma composicion y `Unidad` 13 vs 15 -> la fila sale **"Inconsistente"** con **ambos** valores (10/12) y **ambos** origenes, sin elegir por el usuario. Con ambos Perfiles coherentes -> **"Exacta = 10"** con el detalle del despeje. La correccion de la deteccion de conflicto quedo bien aplicada |
| M25 — solo lectura | PASS | `Diagnostico` no escribe: verificado por comparacion de la base antes/despues de abrir la pantalla |
| Permisos | PASS | `PreciosPorCentro/Index`+AJAX con `RequireAdministracion`; link de sidebar dentro del bloque `SuperUsuario/Administrador` (respaldado por autorizacion real, patron de `32-estandares-qa-implementador`) |
| Regresion — catalogo de Practicas/Perfiles | PASS | listados, Create/Edit/Details 200; precio de referencia se sigue mostrando y calculando |
| Regresion — PDF y Excel de Produccion Mensual | PASS | PDF 200 `application/pdf` para periodos con centro, sin centro e historico (167–208 KB); Excel 200 (7,6–7,9 KB). Leen `PrecioSnapshot`, sin cambios |
| **Regresion — F-001 (`Precios/AumentoMasivo`)** | PASS | pantalla 200, sigue operando solo sobre Practicas. `PreciosController.cs` sin cambios en la sesion (ultimo commit que lo toca es de sesion 3) |
| Smoke de pantallas | PASS | **19/19** pantallas (nuevas, modificadas y heredadas) devuelven 200 con la app corriendo |

### Maquina de estados
No aplica (P4-A). M19–M25 no introducen estados nuevos. Estados de entidades: Activa/Inactiva via soft delete (`DeletedAt`). Sin cambios.

### Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | accion |
|---|---|---|---|
| REG-001..REG-009 | no | N/A | modulos inexistentes en labipac (variantes/stock, compras, ventas, devoluciones, cascada categoria-subgrupo) |
| REG-010 | si | PASS | link de sidebar nuevo ("Precios por Centro") respaldado por autorizacion real coincidente con la politica del controller |
| KOI-001 | si | PASS | sin botones `btn-swal-confirm` fuera de su form en las vistas nuevas |
| KOI-002/003/004 | no | N/A | sin modulo equivalente |
| KOI-005/006 | si | PASS | `PreciosPorCentroController` existe y responde 200 desde el link del sidebar (no genera 404 como el patron catalogado) |
| DN-001/DN-002 | si | PASS | sin 500 en listados; `GetData` de UnidadesBioquimicas responde correctamente con orden dinamico |
| GAN-001 | si | PASS | `ProduccionCargaMasivaViewModel.Filas` sigue con default `new()` (lista vacia), sin fila fantasma; el guard "al menos una linea" se dispara de verdad |
| GAN-002 | si | PASS (nota) | sin backfill en la migracion de sesion 6 (decision explicita): `CantidadUnidades=0` y `PreciosPorUnidadCentroSalud` vacia son el estado esperado, no un defecto |
| GAN-003 | si | PASS | los modales de alta rapida son partials normales, no `<script type="text/x-template">` con `<partial>` adentro |
| GAN-004 | no | N/A | sin `<datalist>` |
| VSF-001/002 | no | N/A | sin maquina de estados |
| CRM-001..006 | no | N/A | sin bot/outbound/notificaciones |
| CRM-002 | si | PASS | defensa en profundidad de vista/controller alineada en `PreciosPorCentro` |
| CRM-003 | si | PASS | el listado de Practicas respeta `order[0][column]/order[0][dir]` |
| MH-001/002 | si | PASS | sin `Contains` sobre coleccion local en las consultas nuevas; sin enum serializado como int en los VMs nuevos |
| MH-003 | si | **FAIL parcial -> QA-S3-04** | mismo patron: el bloqueo RN-28 existe solo en el cliente, sin revalidacion server-side equivalente en el POST |
| MH-004..MH-013 | no | N/A | sin caja/AFIP/remitos/cheques |
| SG-001 | si | PASS | la grilla de carga masiva no rompe el binding con filas vacias |
| LP-001/LP-003 | si | PASS | sin `Venta.Estado` equivalente; los `value` numericos de las vistas nuevas se emiten con `InvariantCulture` (`precioPorUnidadVigente = 1000.00`, con punto) |
| ELV-001 | si | PASS | `PreciosPorCentroController` tiene `[Authorize]` de clase + politica en las acciones sensibles |
| ELV-002 | si | PASS | `CreateAsync` y `UpdateAsync` de `PracticaService` y `UnidadBioquimicaService` validan lo mismo (sin asimetria) |
| **LIP-001** | si | **FAIL -> auto-fix aplicado** | item **nuevo**, creado en esta sesion (ver abajo) |

### Defectos detectados

**QA-S3-01 (major) — LIP-001: los rechazos de regla de negocio del Service eran invisibles. AUTO-FIX APLICADO.**
Reproducido en vivo: al crear un periodo duplicado (RN-24), un periodo con centro inactivo (RN-25 rama 2) o cualquier registro con nombre repetido en los 3 ABMs, la pagina responde 200, vuelve al formulario con los datos tipeados y **no muestra ningun mensaje**. La regla se aplica bien (verificado por query: no se persiste nada) — el defecto es puramente de feedback: el usuario ve que "el boton no hace nada" y reintenta.
Causa raiz: los Controllers hacen `ModelState.AddModelError(string.Empty, result.Message)` y devuelven `View(model)` (patron correcto), pero **7 vistas Create/Edit no tenian `asp-validation-summary` ni bloque equivalente**, con lo que los errores de clave vacia no tenian donde renderizarse. Los errores de DataAnnotation si se veian (tienen su `<span asp-validation-for>`), lo que enmascaraba el problema.
Mayormente **preexistente**, pero relevante para esta entrega porque RN-25 (nueva en sesion 6) cae exactamente en ese agujero.

**QA-S3-02 (major, sin auto-fix — requiere decision de negocio) — el "Precio de referencia" de las Practicas queda desfasado tras cambiar el `PrecioPorUnidad` global.**
Reproducido: con `CantidadUnidades=5` y global $918,79, `PrecioActual` = $4.593,95. Al pasar el global a $1.000, el batch recalcula `Unidad` y `PrecioActual` de los **Perfiles** pero deliberadamente **no** el `PrecioActual` de las **Practicas** (decision 4 del implementador, para no pisar F-001). Resultado: el listado sigue mostrando "Precio referencia $4.593,95" para una practica de 5 unidades con el valor vigente en $1.000, mientras el formulario de edicion de esa misma practica calcula en vivo $5.000,00. **Dos numeros distintos para el mismo concepto en dos pantallas.**
Antes de sesion 6 esto no podia pasar: `UnidadBioquimica.PrecioActual` era un valor manual sin formula. Ahora RN-32 le da una formula, pero hay **dos escritores sin reconciliacion** (F-001 en $ y el ABM por formula), y ademas F-001 pisa el valor derivado hasta que alguien edite la practica, momento en que se recalcula y el aumento de F-001 se pierde en silencio.
**No se auto-fixea:** elegir cual de los dos escritores manda es una decision de negocio (¿el precio de referencia sigue a la formula, o F-001 sigue siendo la fuente de verdad y el ABM no debe recalcular?). **Escalado al implementador/analista**, segun la regla del rol de no adivinar causa raiz ambigua.

> ✅ **RESUELTO EN CODIGO el 2026-08-24 — pendiente de verificacion por QA.**
> Decision de negocio tomada por el usuario del estudio: **manda la formula**. F-001 (`PreciosController` + `Precios/AumentoMasivo` + `PreciosViewModels.cs` + entrada de sidebar) fue **retirado por completo** — como ya no operaba sobre Perfiles desde el 2026-07-08, su unico alcance restante eran las Practicas. `UnidadBioquimica.PrecioActual` queda con **un solo escritor**: `PrecioActual = CantidadUnidades × PrecioPorUnidad` (RN-32), aplicada tanto en el ABM como ahora tambien en el batch de `ActualizarPrecioPorUnidadAsync` / `AumentarPrecioPorUnidadPorcentajeAsync`, en el mismo `SaveChangesAsync` que los Perfiles. El aumento masivo de Practicas pasa a hacerse desde la card "Precio por Unidad" de `Practicas/Index`, igual que los Perfiles. Detalle completo en `5-implementador.md`, Sesion 6.
> **Para re-verificar (no ejecutado por el implementador, que no corre smoke tests):** cargar 2-3 Practicas con `CantidadUnidades` distintos, aplicar un aumento % desde la card y confirmar que listado y formulario de edicion muestran **el mismo** `PrecioActual` = `CantidadUnidades × valor nuevo` (era el sintoma exacto del hallazgo); ademas, `/Precios/AumentoMasivo` debe dar **404** y el sidebar no debe mostrar "Aumento masivo".
> ⚠️ **Efecto colateral que QA debe mirar (nuevo R-1, relacionado con RL-1):** al entrar las Practicas al batch, una Practica con `CantidadUnidades = 0` pasa a `PrecioActual` $0 en cuanto se mueve el precio global — antes estaban blindadas por la exclusion que este fix revierte. Con la migracion ya aplicada a produccion **sin backfill**, las **60 Practicas activas reales** estan en ese estado. Se agrego una alerta preventiva en la card con link al diagnostico M24, pero la mitigacion real es de proceso: **cargar `CantidadUnidades` antes de tocar el precio global**.

**QA-S3-03 (minor) — el mensaje de M24 afirma un precio $0 que no es el precio real que se cobra.**
Reproducido: "Rutina" (`Unidad=17`, componentes soft-deleted) aparece en el diagnostico como *Sin composicion* con el texto "su volumen de unidades es 0 y su precio queda en $ 0". En ese mismo momento `GetPrecioItem` devolvia **$18.700** para ese Perfil (17 x 1.100). El mensaje describe el estado **futuro** (post-recalculo), no el actual. Un usuario puede concluir que el Perfil esta bloqueado cuando en realidad esta cotizando con un volumen heredado obsoleto — que es justo el escenario mas peligroso de RA-17. Sugerencia: redactar como "su precio pasara a $0 en cuanto se recalcule".

**QA-S3-04 (minor, defensa en profundidad — no auto-fixeado) — el bloqueo RN-28 es solo del lado del cliente.**
Reproducido: creado un centro sin precio cargado y su periodo, el AJAX bloquea correctamente, pero un `POST` directo a `/ProduccionMensual/AgregarLinea` con `PrecioSnapshot=99999` **persiste la linea**. Igual en carga masiva: `AgregarLineaAsync`/`AgregarLineasAsync` aceptan el `PrecioSnapshot` del cliente sin revalidar contra `GetPrecioVigenteAsync`. Mismo patron que MH-003 del catalogo.
**Atenuante fuerte:** el precio de la linea es **editable por diseño desde la sesion 1** (RN-05), asi que una revalidacion estricta server-side chocaria con esa decision funcional. Por UI normal el usuario esta correctamente bloqueado. Se documenta como riesgo residual, no se parchea (seria logica de negocio nueva).

**QA-S3-05 (minor, higiene de repositorio) — worktree stale versionable.**
`.claude/worktrees/agent-a4b3377faf900fd9b/` es un git worktree bloqueado con **109 archivos `.cs` de la version PRE-sesion 6**, y `.claude/` **no esta en `.gitignore`**. Un `git add -A` antes del commit de la entrega arrastraria una copia duplicada y obsoleta de todo el codigo fuente. Mitigacion trivial: agregar `.claude/` a `.gitignore` y `git worktree remove --force` del worktree.

### Auto-fixes aplicados

**LIP-001** (item nuevo creado en `docs/qa/regresiones-manuales.yml` — el bug no estaba catalogado).
- Archivos: `LabIPAC.Web/Views/{ProduccionMensual,Practicas,UnidadesBioquimicas,CentrosSalud}/{Create,Edit}.cshtml` — 7 vistas, **+2 lineas cada una**.
- Parche: `<div asp-validation-summary="ModelOnly" class="text-danger mb-3">` como primer hijo del `<form>`, replicando el patron **ya validado dentro del mismo proyecto** (`Views/Users/Create.cshtml`, `Views/Account/Login.cshtml`). Cero logica de negocio nueva.
- Migracion EF: ninguna.
- Post-parche: build OK (0 errores, 9 warnings preexistentes, ninguno nuevo). Los 5 rechazos ahora muestran su mensaje. No-regresion: las 4 altas validas siguen persistiendo (302) y el error de campo sigue apareciendo una sola vez (`ModelOnly` no duplica los errores con clave de campo).

### Riesgos de liberacion y mitigaciones

- **RL-1 (ALTO) — RA-17 confirmado en vivo: un cambio del `PrecioPorUnidad` global puede poner Perfiles en $0 sin que nadie los toque.** Verificado: "Rutina" paso de `Unidad`=17 / $15.619,43 a 0 / $0,00 solo por mover el precio global. En Produccion, cualquier Perfil con composicion incompleta o componentes dados de baja cae igual. **Mitigacion obligatoria antes del deploy:** (1) abrir `/PreciosPorCentro/Diagnostico` y anotar las sugerencias de M25 **antes de tocar precios o composiciones** (las ecuaciones dependen de la `Unidad` historica y se pierden al primer recalculo); (2) completar composiciones y `CantidadUnidades`; (3) recien despues operar precios.
- **RL-2 (ALTO) — dato faltante bloqueante (RA-13/DD-06).** `CantidadUnidades=0` en todas las practicas y `PreciosPorUnidadCentroSalud` vacia. Hasta que el cliente cargue ambos, **toda alta de linea en periodos con centro esta bloqueada** (comportamiento deseado por DD-07, pero es friccion real en el dia 1). Mitigacion: usar el reporte M24 como checklist de carga; coordinar la carga con el cliente **antes** del deploy.
- **RL-3 (MEDIO) — QA-S3-02 sin resolver:** el precio de referencia de catalogo puede mostrar dos valores distintos segun la pantalla, y F-001 y el ABM se pisan mutuamente. No afecta la facturacion (que sale del precio por centro), si afecta la confianza en el catalogo. Requiere decision del analista/implementador.
- **RL-4 (MEDIO) — la entrega esta 100% sin commitear.** Las 31 modificaciones + 7 archivos nuevos de M19–M25 estan solo en el working tree de `main`. Sin commit ni rama no hay punto de rollback. Mitigacion: crear rama, commitear y recien ahi mergear (ver checklist).
- **RL-5 (BAJO) — QA-S3-04:** revalidacion server-side ausente para RN-28. Sin impacto por UI normal.
- **RL-6 (BAJO) — QA-S3-05:** worktree stale versionable.
- **Migracion:** `20260823230449_AddCantidadUnidadesYPrecioPorUnidadCentroSalud` aplicada y verificada en `labipac_dev` (columna con default 0 + tabla nueva con indice unico). Riesgo de rollback bajo. **Pendiente aplicarla a Produccion.**

### Pruebas minimas ejecutadas (segun `4-presupuestador.md` SESION 5)

- **M19** PASS — crear/editar Practica con `CantidadUnidades`; `PrecioActual` calculado (4593,95 = 5x918,79) y sin input editable.
- **M20** PASS — Perfil sin componentes rechazado (RN-02); Perfil con 2 componentes -> `Unidad` = 5+3 = 8; editar `CantidadUnidades` de un componente (5->10) -> el Perfil recalcula solo a 13; el Perfil no relacionado no se toca.
- **M21** PASS — 2 centros con valores distintos; aumento 10% en uno no afecta al otro.
- **M22** PASS — periodo nuevo sin centro rechazado; Practica y Perfil en periodo con centro cotizan por la formula del centro (5500 y 18700); los 3 casos de bloqueo con mensaje accionable; periodo historico sin centro sigue usando el precio de referencia.
- **M23** PASS — alta rapida de Perfil exige >=1 componente; alta rapida de Practica pide `CantidadUnidades`.
- **M24** PASS — el reporte lista correctamente contra datos reales de `labipac_dev`.
- **M25** PASS — casos "Exacta" e "Inconsistente" verificados en vivo; sin escritura en base.

### Checklist de salida para merge

- [x] Migracion EF generada y aplicada a base de desarrollo (sin backfill, columna con default 0).
- [x] Build OK sin warnings nuevos (0 errores, 9 warnings preexistentes), antes y despues del auto-fix.
- [x] Verificacion de los flujos M19–M25 segun pruebas minimas, con foco en M20 (cascada) y M22 (bisagra RA-15) — **ejecutada en vivo, no solo por lectura**.
- [x] Auto-fix LIP-001 aplicado, catalogado y verificado post-parche.
- [x] Datos de prueba eliminados: `labipac_dev` restaurado a su estado exacto pre-QA desde backup `mysqldump` (0 residuos, migracion intacta, sin bases temporales).
- [ ] **BLOQUEANTE DE PROCESO — commitear la entrega en una rama** (hoy esta todo sin commitear sobre `main`).
- [ ] **BLOQUEANTE DE DEPLOY — RL-1:** correr el reporte M24/M25 en Produccion y completar composiciones/`CantidadUnidades` ANTES de tocar el precio global o los precios por centro.
- [ ] Carga de datos del cliente (RL-2) coordinada antes de habilitar el uso.
- [x] Decision de negocio sobre QA-S3-02 (escalado al implementador/analista) — **tomada y aplicada en codigo el 2026-08-24** (manda la formula; F-001 retirado). Queda pendiente la **re-verificacion funcional por QA**, ver la nota de resolucion arriba.
- [ ] Agregar `.claude/` a `.gitignore` y remover el worktree stale (QA-S3-05).
- [ ] Aplicar la migracion a Produccion en el proximo deploy.

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
RN-02: **REACTIVADA 2026-08-23** (revierte la relajacion de sesion 2) — verificado en ABM completo y en alta rapida
RN-14: **DEROGADA 2026-08-23** — el alta rapida de Perfil ya exige composicion (verificado)
RN-24: Unicidad Mes+Anio+CentroSaludId (verificado: duplicado exacto bloqueado, mismo Mes+Anio con otro centro permitido)
RN-25: Centro de Salud obligatorio en periodos NUEVOS; los NULL historicos siguen validos y editables (verificado en vivo)
RN-26: `UnidadBioquimica.CantidadUnidades` entero >= 1 (DataAnnotation en el VM; el Service admite 0 por las filas migradas)
RN-27: Fila unica de precio por CentroSaludId, >= 0 (verificado: upsert sin violar el indice unico)
RN-28: Precio en periodo CON centro = volumen x precio de unidad del centro; bloqueo en los 3 casos (verificado en vivo; ver QA-S3-04 sobre revalidacion server-side)
RN-29: Periodo historico SIN centro -> precio de referencia, identico al comportamiento previo (verificado contra datos reales preexistentes)
RN-30: Alta rapida de Practica pide `CantidadUnidades`; alta rapida de Perfil pide composicion (verificado)
RN-31: Precio de referencia global y precios por centro independientes (verificado; ver QA-S3-02 sobre la coherencia interna del de referencia)
RN-32: `UnidadBioquimica.PrecioActual` calculado, ya no de entrada (verificado: sin input en el form)
RN-33: `Practica.Unidad = SUM(PracticaDetalle.Cantidad x UnidadBioquimica.CantidadUnidades)` de componentes activos (verificado en Create/Update, cascada y batch global)

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

TC-M19-01: Editar Practica con `CantidadUnidades=5` -> `PrecioActual` = 5 x 918,79 = 4593,95. PASS (en vivo).
TC-M19-02: Form de Practica sin input de `PrecioActual`. PASS (en vivo).
TC-M20-01: Crear Perfil sin composicion -> rechazado, nada persistido. PASS (en vivo).
TC-M20-02: Crear Perfil con 2 componentes (5+3) -> `Unidad`=8, precio 7350,32. PASS (en vivo).
TC-M20-03: Editar `CantidadUnidades` de un componente (5->10) -> el Perfil que lo usa pasa a `Unidad`=13 / 11944,27; el Perfil no relacionado queda intacto. PASS (en vivo).
TC-M20-04: Editar solo el nombre de una Practica -> NO dispara cascada (`UpdatedAt` del Perfil sin cambios). PASS (en vivo).
TC-M21-01: 2 centros con precios distintos; aumento 10% en uno no afecta al otro. PASS (en vivo).
TC-M22-01: Periodo nuevo sin centro -> rechazado; selector sin "— Global —". PASS (en vivo).
TC-M22-02: Practica en periodo con centro -> 5 x 1100 = 5500. PASS (en vivo).
TC-M22-03: Perfil en periodo con centro -> 17 x 1100 = 18700 (NO el de referencia 15619,43). PASS (en vivo) — **bisagra RA-15**.
TC-M22-04: Centro sin precio cargado -> bloqueo con mensaje accionable. PASS (en vivo).
TC-M22-05: Practica sin `CantidadUnidades` -> bloqueo con mensaje accionable. PASS (en vivo).
TC-M22-06: Periodo historico sin centro -> precio de referencia, edicion y alta de lineas normales. PASS (en vivo, contra datos preexistentes).
TC-M23-01: Alta rapida de Perfil sin composicion -> rechazada. PASS (en vivo).
TC-M23-02: Alta rapida de Perfil con composicion -> creada con `unidad` calculada. PASS (en vivo).
TC-M23-03: Alta rapida de Practica -> pide `cantidadUnidades`, no precio. PASS (en vivo).
TC-M24-01: Reporte detecta Perfil sin composicion y Practicas sin `CantidadUnidades` sobre datos reales. PASS (en vivo). Ver QA-S3-03 sobre el texto.
TC-M25-01: Conflicto entre 2 Perfiles -> "Inconsistente" con ambos valores y origenes, sin elegir. PASS (en vivo) — **confirma la correccion del implementador**.
TC-M25-02: Ecuacion resoluble -> "Exacta" con detalle del despeje. PASS (en vivo).
TC-M25-03: La pantalla de diagnostico no escribe nada en la base. PASS (en vivo).
TC-RA15-01: Unico caller real de `GetPrecioVigenteAsync`; los 2 puntos que resuelven el multiplicador para la vista ramifican por centro. PASS (codigo + en vivo).
TC-REG-01: PDF y Excel de Produccion Mensual (con centro, sin centro, historico). PASS (en vivo).
TC-REG-02: F-001 `Precios/AumentoMasivo` sin cambios y operativo. PASS (en vivo + git).
TC-REG-03: Smoke 19/19 pantallas -> 200. PASS (en vivo).
TC-LIP001-01: Rechazos de Service (RN-24, RN-25, nombre duplicado x3) ahora muestran su mensaje. PASS (post auto-fix, en vivo).

---

## Bugs resueltos

BUG-001 [2026-06-15] CRITICAL
Modulo: Produccion Mensual / Eliminar linea
Causa: site.js usaba closest-form ignorando data-form del boton externo al form.
Fix: getElementById con data-form attribute en site.js
Verificacion: codigo inspeccionado + build OK + suite 50/50 PASS

Sin bugs funcionales nuevos reproducidos en la sesion 2 (M7+M8+M9). QA-F1/F2/F3 son hallazgos no bloqueantes (ver seccion arriba), sin autofix aplicado por no tratarse de bugs reproducidos (son observaciones de robustez/UX).

QA-S3-01 / LIP-001 [2026-08-23] MAJOR
Modulo: ABMs de catalogo + Produccion Mensual / Create-Edit
Causa: 7 vistas Create/Edit sin `asp-validation-summary`, con lo que los errores de `ModelState` de clave vacia (los que propagan un `ServiceResult.CreateError`) no se renderizaban en ningun lado. Rechazo silencioso: la regla se aplicaba bien, el usuario no veia nada.
Fix: `<div asp-validation-summary="ModelOnly" class="text-danger mb-3">` como primer hijo del `<form>` en las 7 vistas (patron ya validado en `Views/Users/Create.cshtml` y `Views/Account/Login.cshtml` del mismo proyecto).
Verificacion: build OK sin warnings nuevos + 5 casos de rechazo mostrando su mensaje en vivo + no-regresion de las 4 altas validas y de los errores de campo.

Nota de correccion a la memoria de sesion 2: el hallazgo QA-F1 afirmaba que en carga masiva "el mensaje de error se muestra como alerta general arriba del formulario". Eso es **correcto solo para `CargaMasiva.cshtml`** (que si tiene su propio bloque manual de `ModelState`); el resto de las vistas Create/Edit del sistema no mostraba nada — lo que dio origen a LIP-001.

---

## Evidencia sesion 2026-06-15

Suite 50 checks: 29 positivos + 21 negativos = 50/50 PASS
Build: OK
Renombre: Unidades Bioquimicas -> Practicas; Practicas -> Perfiles
Tildes: Layout, Home, ProduccionMensual, Practicas

---

## Historial

2026-06-15: Primera carga QA. Fix BUG-001. Renombre UI. Tildes. 50/50 PASS. Build OK.
2026-08-23: QA de M19–M25 (Precio por Unidad Bioquimica y por Perfil segun Centro de Salud), primera verificacion independiente del alcance — el gate de aprobacion del presupuesto habia sido salteado. Metodo: lectura de codigo real + build + **app corriendo con login real contra `labipac_dev`, incluyendo flujos de escritura** (backup `mysqldump` previo y restore completo al cierre). Confirmados en vivo los 4 focos de riesgo: **RA-15** (la bisagra de precio funciona: 17x1100=18700 con centro, 15619,43 de referencia sin centro; un solo caller real y los 2 puntos de vista corregidos), **RA-18/DD-09** (cascada por consulta inversa correcta, no toca Perfiles no relacionados, y no se dispara si solo cambia el nombre), **RA-17** (reproducido: mover el `PrecioPorUnidad` global tiro un Perfil real de `Unidad`=17/$15.619,43 a 0/$0,00 sin que nadie lo tocara — RL-1, riesgo alto de deploy), **RN-29** (historicos sin centro intactos). M25 verificado incluyendo el caso "Inconsistente" que el implementador habia corregido. Regresion OK: PDF/Excel, F-001 sin cambios, 19/19 pantallas 200. **1 auto-fix aplicado (LIP-001, item nuevo en el catalogo cross-proyecto): 7 vistas Create/Edit sin validation-summary hacian invisibles los rechazos de regla de negocio.** 4 hallazgos adicionales sin auto-fix: QA-S3-02 (major, desfasaje del precio de referencia — **escalado, requiere decision de negocio**), QA-S3-03 (minor, mensaje de M24 enganoso), QA-S3-04 (minor, RN-28 solo client-side), QA-S3-05 (minor, worktree stale versionable). `labipac_dev` restaurado a su estado exacto pre-QA. Merge condicionado a commitear la entrega (hoy 100% sin commitear sobre `main`) y a ejecutar el relevamiento de RA-17 antes del deploy.
2026-07-08: QA de M7 (Unidad/PrecioPorUnidad + simplificacion F-001) + M8 (Carga masiva + alta rapida atomica) + M9 (fix PDF). Verificacion por codigo real + build + consulta directa a `labipac_dev` via mysqlsh (foco de riesgo: backfill de Unidad, PreciosController sin Perfiles, atomicidad de AgregarLineasAsync). Sin bugs bloqueantes. 3 hallazgos menores no bloqueantes (QA-F1 UX carga masiva, QA-F2 robustez PrecioPorUnidad sin OrderBy, QA-F3 patron heredado de autorizacion AJAX). Catalogo cross-proyecto ejecutado: mayoria N/A por falta de modulo equivalente (stock/variantes/compras/ventas/camaras/notificaciones/autorizaciones), sin regresiones de los patrones aplicables (RowVersion MySQL, EF6 dynamic OrderBy, lista con fila fantasma tipo GAN-001, template+partial tipo GAN-003, delete fuera de form tipo KOI-001). Checklist de salida para merge: PASS, pendiente ejecucion manual de UI por el usuario y aplicar migracion a Produccion.
