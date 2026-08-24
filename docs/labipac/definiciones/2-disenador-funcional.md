# Memoria - Disenador funcional

## Proyecto: labipac
## Ultima actualizacion: 2026-07-23

## Definiciones vigentes

### Flujo funcional
- Login → Dashboard → Sidebar (Configuracion / Produccion)
- Configuracion: ABM Unidades Bioquimicas, ABM Practicas ("Perfiles" en UI, con composicion muchos-a-muchos informativa), ABM Centros de Salud.
- Produccion: Index del historial (con columna/filtro Centro de Salud) → Crear periodo (con selector opcional de Centro de Salud) → Detalle/Carga (tabla de lineas + panel resumen) o Carga Masiva (pantalla dedicada, filas repetibles).
- Modal Agregar linea: tipo radio + Select2 por tipo + cantidad + precio editable + aviso historico (P5-B) via AJAX.
- Modal Editar linea: cantidad + precio editable.
- Eliminar linea: soft delete con SweetAlert2 confirm.

### Pantallas vigentes
- WF-01: Unidades Bioquimicas Index (DataTables client-side, baja logica, reactivar).
- WF-02: Unidades Bioquimicas Create/Edit (col-md-6, campo precio, estado checkbox).
- WF-03: Practicas/Perfiles Index (DataTables client-side) — columna "Unidad" agregada, columna "Precio actual" (editable) reemplazada por "Precio (calculado)" solo lectura; card "Precio por Unidad" arriba de la tabla (valor vigente + input editable + input % con confirmacion SweetAlert2).
- WF-04: Practicas/Perfiles Create/Edit — sin campo "Precio actual" editable; campo "Unidad" (entero >=1) con texto informativo "Precio calculado: $ X" recalculado en vivo por JS; seccion de composicion (Select2 multiple) se mantiene pero es informativa/opcional, ya no valida contra el precio.
- WF-05: Practicas/Perfiles Details (tabla composicion readonly + totales).
- WF-06: Produccion Mensual Index/Historial — columna "Centro de Salud" (nombre o "— Global —") + filtro dropdown por esa columna.
- WF-07: Produccion Mensual Crear Periodo — campo "Centro de Salud" (Select2 opcional, default "Sin centro asignado (global)").
- WF-08: Produccion Mensual Detalle/Carga (col-md-8 tabla + col-md-4 panel resumen sticky) — boton nuevo "Carga masiva" (btn-outline-primary) junto a "Agregar ítem" (el modal existente no cambia).
- WF-09: Modal Agregar Item (radio tipo, Select2 dinamico, cantidad, precio editable + aviso P5-B).
- WF-10: Modal Editar Linea (cantidad y precio editable).
- WF-11: Produccion Mensual — Carga Masiva (pantalla nueva, `GET/POST /ProduccionMensual/CargaMasiva/{id}`) — tabla dinamica de filas (Tipo, Item con Select2 + opcion "+ Crear nuevo…", Cantidad, Precio autocompletado editable, Subtotal JS, Quitar fila), boton "+ Agregar fila", Total general JS, submit unico "Guardar todas las líneas". Modal Alta Rapida Perfil (Nombre + Unidad, precio calculado en vivo, sin exigir composicion) y Modal Alta Rapida Practica (Nombre + Precio actual), ambos con insercion AJAX sin recargar.
- WF-12: Fix reporte PDF — columna "Precio unit." de 55 a 75pt de ancho fijo (compensado reduciendo "Tipo" de 65 a 60).
- WF-13: Centros de Salud Index (pantalla nueva) — mismo patron que WF-01, badge Tipo (Privado=secondary, Mutual=info).
- WF-14: Centros de Salud Create/Edit (pantalla nueva) — mismo patron que WF-02 (Nombre, Tipo select, Activo checkbox en Edit).
- WF-15: Ajuste reporte PDF — linea "Centro de Salud: {Nombre} ({Tipo})" en el encabezado cuando `CentroSaludId != null`.
- Ajuste F-001 (`Precios/AumentoMasivo.cshtml`): se quita el tab "Perfiles" (ya no aplica), se agrega nota informativa; el tab "Practicas" (UnidadBioquimica) sigue igual.
- WF-16 (sesion 6, nueva): **Precio de Unidad Bioquimica por Centro de Salud** — pantalla simple, NO una matriz item×centro. Selector/listado de Centros de Salud, cada uno con un unico campo editable "Precio de Unidad Bioquimica" (+ boton de aumento %), mismo patron visual/AJAX que la card "Precio por Unidad" ya existente en `Practicas/Index` (CU-08) — es literalmente la misma interaccion, repetida una vez por Centro de Salud en vez de un unico valor global. Al guardar el valor de un centro, el precio de TODAS las Practicas (por su `CantidadUnidades`) y Perfiles (por el volumen de su composicion) en ese centro queda determinado automaticamente.
- WF-01/WF-02 (sesion 6, ajuste — Practicas = entidad Domain `UnidadBioquimica`, "Practica" en UI): agrega el campo **CantidadUnidades** (entero >= 1) al ABM; `PrecioActual` deja de ser editable a mano y pasa a mostrarse solo lectura como "Precio de referencia: $ X" (`CantidadUnidades × PrecioPorUnidad` global), calculado en vivo por JS — mismo cambio que ya sufrio el Perfil en sesion 4. Columna nueva "Cant. Unidades" en el listado.
- WF-03/WF-04 (sesion 6, ajuste — Perfiles = entidad Domain `Practica`): **revierte el ajuste de sesion 4** — el campo `Unidad` deja de cargarse a mano: pasa a ser solo lectura, calculado en vivo por JS a partir de la composicion (`Σ Cantidad_componente × CantidadUnidades_componente`). La seccion de composicion (Select2 multiple) vuelve a ser **obligatoria** (minimo 1 componente, ya no opcional/informativa) — cada componente debe tener su `CantidadUnidades` cargada; si algun componente no la tiene, aviso bloqueante "Este componente no tiene Cantidad de Unidades Bioquimicas cargada, no se puede calcular el precio del Perfil".
- WF-07 (sesion 6, ajuste): selector de Centro de Salud en Crear Periodo pasa de opcional a **obligatorio** (ya no hay opcion "Sin centro asignado (global)" para periodos nuevos); si el centro elegido todavia no tiene cargado su "Precio de Unidad Bioquimica", aviso informativo (no bloqueante a nivel de creacion del periodo, el bloqueo ocurre recien al intentar cargar un item).
- WF-09/WF-11 (sesion 6, ajuste): Modal Agregar Item / fila de Carga Masiva — el AJAX de precio bloquea el guardado de la linea con mensaje claro en 2 casos: (a) el Centro de Salud del periodo todavia no tiene cargado su "Precio de Unidad Bioquimica" (enlace a WF-16); (b) el item (Practica sin `CantidadUnidades`, o Perfil con algun componente sin `CantidadUnidades`) no tiene volumen calculable (enlace a editar el item).
- Modales de alta rapida (`_ModalAltaRapidaPerfil`/`_ModalAltaRapidaPractica`, sesion 6, **revierte RN-14**): el alta rapida de Perfil deja de omitir la composicion — ahora pide seleccionar al menos 1 componente (igual que el ABM completo), porque sin composicion el Perfil no tiene precio calculable. El alta rapida de Practica pide `CantidadUnidades` en vez de un precio en $.
- Ajuste F-001 (`Precios/AumentoMasivo.cshtml`, sesion 6): **se simplifica en vez de crecer** — con el modelo corregido, aumentar precios por Centro de Salud ya no requiere seleccionar Practicas una por una: es la misma operacion de "editar/aumentar %" que WF-16 (CU-10). F-001 se mantiene sin cambios, operando exclusivamente sobre el precio de referencia global de cada Practica (catalogo), igual que hoy.

### ViewModels vigentes
- VM-01/VM-02: UnidadBioquimicaCreateViewModel/EditViewModel, UnidadBioquimicaRowViewModel.
- VM-03 `PracticaCreateViewModel` (modificado): Nombre, **Unidad** (nuevo, reemplaza PrecioActual editable), PrecioPorUnidadVigente (solo lectura), UnidadBioquimicaIds (ahora opcional), UnidadesDisponibles. Validacion RN-01 original removida.
- VM-04 `PracticaRowViewModel` (modificado): + campo **Unidad**.
- VM-05: PracticaDetailsViewModel (composicion readonly + totales).
- VM-06 `ProduccionMensualCreateViewModel` (modificado): + `CentroSaludId` (int?), + `CentrosSaludDisponibles` (SelectList).
- VM-07 `ProduccionMensualRowViewModel` (modificado): + `NombreCentroSalud` (string?, "— Global —" si null).
- VM-08 `ProduccionMensualDetalleViewModel` (modificado): + `NombreCentroSalud` (string?); flag `EsPeriodoHistorico` (aviso P5-B).
- VM-09: ProduccionDetalleRowViewModel (NombreSnapshot, PrecioSnapshot, Subtotal).
- VM-10: ProduccionDetalleAgregarViewModel (PrecioSugerido para AJAX, EsPeriodoHistorico).
- VM-11: ProduccionDetalleEditarViewModel.
- VM-12 `ProduccionCargaMasivaViewModel`: ProduccionMensualId, Periodo, EsPeriodoHistorico, List\<VM-13\> Filas, PerfilesDisponibles, PracticasDisponibles.
- VM-13 `ProduccionCargaMasivaFilaViewModel`: TipoItem (enum), ItemId, Cantidad, PrecioSnapshot.
- VM-14 `PerfilAltaRapidaViewModel`: Nombre, Unidad.
- VM-15 `PracticaAltaRapidaViewModel` (UnidadBioquimica): Nombre, PrecioActual.
- VM-16 `PrecioPorUnidadViewModel`: ValorActual, NuevoValor, PorcentajeAumento.
- VM-17 `CentroSaludCreateViewModel`/`EditViewModel`: Nombre, Tipo (enum), Activo (solo Edit).
- VM-18 `CentroSaludRowViewModel`: Id, Nombre, Tipo, Activo.
- VM-19 `PrecioUnidadBioquimicaCentroRowViewModel` (sesion 6): CentroSaludId, NombreCentroSalud, PrecioUnidadBioquimicaVigente (decimal?, null = sin cargar), CantidadPracticasYPerfilesAfectados (informativo, para el aviso de confirmacion del aumento %, mismo patron que CU-08). Una fila por Centro de Salud, no por item.
- VM-01/VM-02 `UnidadBioquimicaCreateViewModel`/`EditViewModel`/`RowViewModel` (sesion 6, ajuste — entidad Domain `UnidadBioquimica`, "Practica" en UI): + campo **CantidadUnidades** (entero >=1, reemplaza la carga manual de precio), `PrecioActual` deja de ser editable, se agrega `PrecioReferenciaVigente` (solo lectura, calculado, igual patron que `PrecioPorUnidadVigente` del Perfil).
- VM-03 `PracticaCreateViewModel`/VM-04 `PracticaRowViewModel` (sesion 6, **revierte el ajuste de sesion 4** — entidad Domain `Practica`, "Perfil" en UI): `Unidad` deja de ser un campo de entrada — pasa a `UnidadCalculada` (solo lectura, derivada de la composicion); `UnidadBioquimicaIds` vuelve a ser obligatorio (minimo 1), ya no opcional.
- VM-14 `PerfilAltaRapidaViewModel` (sesion 6, ajuste): Nombre + `UnidadBioquimicaIds` (minimo 1, ya no se omite la composicion) — se quita el campo `Unidad` de entrada (pasa a calcularse).
- VM-15 `PracticaAltaRapidaViewModel` (sesion 6, ajuste — UnidadBioquimica): Nombre + **CantidadUnidades** (reemplaza el campo `PrecioActual` de entrada).

### Maquina de estados
No aplica en ningun modulo (confirmado en Analisis, P4-A).

### Reglas de negocio vigentes (estado final, incluye derogaciones/reemplazos)
| Ref | Regla | Capa | Estado |
|---|---|---|---|
| RN-02 | Perfil requiere al menos 1 componente (composicion M:N con Practicas) | Service + DataAnnotation | **REACTIVADA en sesion 6** (habia sido relajada globalmente en sesion 4) — vuelve a ser obligatoria porque el volumen de unidades del Perfil se calcula a partir de la composicion |
| RN-03 | Cambio de precio de unidad no afecta historial (precio_snapshot) | Diseño de campo | Vigente |
| RN-04 | No duplicar el mismo item en el mismo periodo | Service | Vigente |
| RN-05 | Precio pre-completado por AJAX al seleccionar item en modal | Controller AJAX | Vigente |
| RN-06 | Aviso de periodo historico (mes/año != actual) | Flag EsPeriodoHistorico en VM | Vigente |
| RN-07 | Cantidad entero >= 1 | DataAnnotation | Vigente |
| RN-08 | PrecioSnapshot >= 0 | DataAnnotation | Vigente |
| RN-09 | Solo items activos en nuevas lineas | Service (GetActivasAsync) | Vigente |
| RN-10 | Total recalculado en tiempo real | JS sobre DataTable | Vigente |
| RN-12 | Guardado de carga masiva atomico: todas las filas o ninguna | Service | Vigente |
| RN-13 | Sin combinacion TipoItem+ItemId repetida dentro del mismo submit de carga masiva | Service + cliente | Vigente |
| RN-14 | Alta rapida de Perfil no exige composicion (relaja RN-02 solo en este flujo) | Service | **DEROGADA en sesion 6** — el alta rapida vuelve a exigir composicion (RN-02 reactivada), ya que sin componentes el Perfil no tiene volumen de unidades calculable |
| RN-15 | Alta rapida de Practica (UnidadBioquimica) sin cambios respecto al ABM existente | Service | Vigente (sesion 6: el ABM ahora pide `CantidadUnidades` en vez de precio, ver RN-32) |
| RN-16 | `Practica.PrecioActual = Unidad × PrecioPorUnidad.ValorVigente` (catalogo/referencia) o `× PrecioUnidadBioquimica(Centro)` (produccion mensual por centro, sesion 6); `Unidad` a su vez es calculado (sesion 6, ver RN-33) | Service | Vigente, formula de `Unidad` MODIFICADA en sesion 6 |
| RN-17 | `Unidad` de Perfil entero, obligatorio, >= 1 | DataAnnotation | **Sesion 6: deja de ser DataAnnotation de entrada de usuario** — pasa a ser un valor calculado (RN-33), la validacion >=1 aplica sobre el resultado (un Perfil sin componentes con `CantidadUnidades` da `Unidad`=0, invalido) |
| RN-18 | `PrecioPorUnidad.Valor` obligatorio, >= 0 | DataAnnotation + Service | Vigente |
| RN-19 | Aumento %: `NuevoValor = round(ValorActual × (1 + %/100), 2)`, dispara recalculo batch de todos los Perfiles activos | Service | Vigente |
| RN-20 | Reemplaza RN-01 original ("precio Perfil < sumatoria de componentes") | — | RN-01 DEROGADA para Perfiles |
| RN-21 | F-001 (`Precios/AumentoMasivo`) ya no ofrece edicion/cascade sobre Perfiles; sigue aplicando sin cambios sobre Practicas (UnidadBioquimica) | Web | Vigente |
| RN-22 | `CentroSalud.Nombre` obligatorio, <=150 caracteres | DataAnnotation | Vigente |
| RN-23 | `CentroSalud.Tipo` obligatorio (Privado o Mutual) | DataAnnotation | Vigente |
| RN-24 | Reemplaza RN-11 original ("no duplicar mismo mes+año"): no puede existir mas de un periodo por Mes+Año+CentroSaludId, tratando NULL como valor propio | Service | RN-11 REEMPLAZADA |
| RN-25 | `CentroSaludId` en `ProduccionMensual`: obligatorio para periodos nuevos (sesion 6, reemplaza opcionalidad); si se informa, debe corresponder a un `CentroSalud` activo y no eliminado; periodos historicos con NULL preexistente siguen siendo validos y editables | Service | Modificada (sesion 6) |
| RN-26 (sesion 6, VERSION FINAL) | `UnidadBioquimica.CantidadUnidades`: entero obligatorio >= 1 | DataAnnotation | Vigente |
| RN-27 (sesion 6) | "Precio de Unidad Bioquimica" por Centro de Salud: fila unica por CentroSaludId, obligatorio >= 0 al cargarse (reemplaza al `PrecioPorUnidad` global para produccion en un centro especifico) | Service | Vigente |
| RN-28 (sesion 6, VERSION FINAL) | Al agregar una linea (individual o carga masiva) a un periodo CON Centro de Salud: precio de Practica = `CantidadUnidades × PrecioUnidadBioquimica(centro)`; precio de Perfil = `Unidad calculada × PrecioUnidadBioquimica(centro)`. Bloquea el alta con mensaje explicito si (a) el centro no tiene su Precio de Unidad Bioquimica cargado, o (b) el item no tiene cantidad/volumen calculable | Service | Vigente |
| RN-29 (sesion 6) | Al agregar una linea a un periodo historico SIN Centro de Salud (NULL, preexistente a sesion 6), el precio snapshot se resuelve contra el precio de referencia de catalogo, igual que antes de esta sesion | Service | Vigente (compatibilidad) |
| RN-30 (sesion 6, VERSION FINAL) | Alta rapida de Practica desde un periodo con Centro de Salud: pide `CantidadUnidades` (no un precio); alta rapida de Perfil: pide composicion (RN-02 reactivada) — en ambos casos el precio para ese centro se calcula automaticamente con RN-28, sin cargar un precio individual | Service | Vigente |
| RN-31 (sesion 6) | El precio de referencia (catalogo) usa siempre el `PrecioPorUnidad` global historico — independiente de los precios por Centro de Salud, no se recalcula ni se sincroniza automaticamente entre ambos | Service | Vigente |
| RN-32 (sesion 6, nueva) | El ABM de Practica (UnidadBioquimica) ya no recibe `PrecioActual` de entrada — recibe `CantidadUnidades`, y `PrecioActual` (referencia) se calcula igual que ya hace `Practica.PrecioActual` desde sesion 4 | Service | Vigente |
| RN-33 (sesion 6, nueva) | `Practica.Unidad` (volumen del Perfil) se calcula como `Σ (PracticaDetalle.Cantidad × UnidadBioquimica.CantidadUnidades)` sobre los componentes activos del Perfil, recalculado al crear/editar el Perfil o al editar la `CantidadUnidades` de algun componente ya asociado (recalculo en cascada, analogo al recalculo batch que ya dispara un cambio de `PrecioPorUnidad`) | Service | Vigente |

**Permisos:** ABM de Centros de Salud, alta rapida de Perfil/Practica desde carga masiva: `[Authorize]` sin politica especifica (igual que Unidades Bioquimicas/Practicas). Editar `PrecioPorUnidad` (valor manual o aumento %): `RequireAdministracion` (mismo criterio que F-001 y guardado de IVA).

### Contratos funcionales de Services vigentes
- `IUnidadBioquimicaService`: GetAllAsync, GetActivasAsync, GetByIdAsync, CreateAsync, UpdateAsync, DeleteAsync.
- `IPracticaService`: GetAllAsync, GetActivasAsync, GetByIdAsync, CreateAsync, UpdateAsync, DeleteAsync + logica de recalculo de precio derivado (RN-16); sesion 6: `CalcularSumatoria` deja de ser meramente informativo — su equivalente en "unidades" (no en $) vuelve a determinar `Unidad`/precio del Perfil (RN-33); RN-01 original (precio Perfil vs. suma de PRECIOS de componentes) sigue derogada, es un concepto distinto de RN-33 (suma de CANTIDADES de unidades).
- `IProduccionMensualService`: GetAllAsync, GetByIdAsync, CreateAsync (ajustado a RN-24), DeleteAsync, GetPrecioVigente, AgregarLineaAsync, EditarLineaAsync, EliminarLineaAsync, + `AgregarLineasAsync` (batch atomico, carga masiva).
- `ICentroSaludService` (nuevo, mismo shape que `IUnidadBioquimicaService`): GetAllAsync, GetActivasAsync, GetByIdAsync, CreateAsync, UpdateAsync, DeleteAsync, RestoreAsync.
- `IPrecioPorUnidadService` (nuevo): ObtenerVigente, ActualizarValor, AumentarPorcentaje (dispara recalculo batch de Perfiles activos).

### Logica de distribucion de elementos (estandar todo el sistema)
- Listado: Header + card > DataTables client-side. Badge estado. btn-group-sm acciones.
- Formulario simple: Header + card > col-md-6 campos + Guardar/Cancelar.
- Formulario con relacion: igual, con secciones separadas por divisor visual + Select2 multiple.
- Detalle readonly: Header + card > info + tabla composicion.
- Pantalla principal de trabajo: Header + row col-md-8 tabla + col-md-4 panel resumen sticky.
- Pantalla de carga por filas (Carga Masiva): tabla dinamica manejada por JS (no DataTables — es formulario, no listado) + boton "+ Agregar fila" + total JS + submit unico.
- Modal: campos minimos + aviso contextual si aplica.

### Riesgos y supuestos vigentes
- **DD-01 (sesion 6, REVERTIDO):** ya NO aplica — desde sesion 6 un Perfil no puede quedar "sin composicion" (RN-02 reactivada, RN-14 derogada), porque la composicion vuelve a determinar el precio. Los Perfiles ya existentes que hoy estan sin composicion (permitido entre sesion 4 y sesion 6) quedan sin precio calculable hasta que el cliente les cargue componentes — ver RA/R-PC7 en Arquitectura/Analisis.
- **DD-02:** el recalculo batch de todos los Perfiles activos al cambiar `PrecioPorUnidad` debe ser transaccional. Volumen esperado bajo (mismo supuesto que la arquitectura original).
- **DD-03:** al guardar una fila de carga masiva para un periodo historico, aplica el mismo aviso P5-B ya vigente — no es un caso nuevo.
- **DD-04:** unicidad Mes+Año+CentroSaludId con NULL como valor propio no es un unique index nativo simple en MySQL — se resuelve en Service con consulta explicita que distingue el caso NULL (mismo patron que la unicidad original Mes+Año).
- **DD-05:** se acepta convivencia de nombres duplicados entre `CentroSalud` y `Mutual` (FABA) sin vinculo — decision explicita del cliente (P12), no es un defecto.
- Riesgo heredado RA-01 original (baja logica de UnidadBioquimica con composicion activa en Perfil) ya no afecta el precio (independiente de la composicion); se mantiene badge informativo si un componente esta inactivo.
- Unico riesgo tecnico pendiente heredado del diseño original: RF-03 (baja logica de unidad con composicion activa — recalcular sumatoria/snapshot informativo).
- AJAX endpoint `GET /ProduccionMensual/GetPrecioItem?tipo=&id=` para pre-completado de precio en modal — sesion 6: pasa a requerir tambien `centroSaludId` (del periodo activo) como parametro.
- **DD-06 (sesion 6, VERSION FINAL):** sin backfill confiable de `UnidadBioquimica.CantidadUnidades` (campo nuevo) — el cliente debe cargar este valor a mano por cada Practica activa. Es una carga acotada (1 valor por Practica, no una matriz), pero bloquea el calculo de precio de esa Practica y de cualquier Perfil que la tenga como componente hasta completarse.
- **DD-07 (sesion 6):** bloqueo de linea por falta de precio (RN-28) puede generar friccion mientras la carga de `CantidadUnidades`/composicion/precio de centro esta incompleta — se decide bloquear (no autocompletar) para evitar cobrar mal por defecto; el aviso debe ser explicito y accionable.
- **DD-08 (sesion 6):** el Centro de Salud pasa de opcional a obligatorio en Crear Periodo — los periodos historicos con NULL preexistente no se tocan (RN-29), evitando romper el historial ya cargado.
- **DD-09 (sesion 6, nuevo):** RN-33 implica un recalculo en cascada — al editar la `CantidadUnidades` de una Practica, todos los Perfiles activos que la tengan como componente deben recalcular su `Unidad` (volumen). Requiere una consulta inversa (que Perfiles usan esta Practica) antes de poder guardar el cambio, similar en espiritu al recalculo batch ya existente por cambio de `PrecioPorUnidad`, pero ahora disparado tambien desde el ABM de Practicas.
- **DD-10 (sesion 6, nuevo):** los Perfiles activos que hoy (antes de sesion 6) tienen 0 componentes, o componentes sin `CantidadUnidades` cargada, quedan con `Unidad`=0 (invalido) hasta que el cliente complete su composicion — se recomienda relevar cuantos Perfiles estan en esa situacion antes del deploy, para dimensionar el trabajo manual pendiente.

### Historias de usuario vigentes
**HU-01** — Cargar varias lineas de produccion mensual en un solo formulario. AC: N filas dinamicas antes de guardar; un solo "Guardar todas las líneas" persiste todo; fila invalida bloquea el guardado completo con errores puntuales por fila.

**HU-02** — Crear un Perfil o Practica nueva sin salir de la carga masiva. AC: opcion "+ Crear nuevo…" por fila; el nuevo registro queda seleccionado sin recargar; **(sesion 6: un Perfil nuevo SI exige al menos 1 componente con `CantidadUnidades` cargada — revierte "no exige composicion")**.

**HU-03** — Configurar el Precio por Unidad y aumentarlo por porcentaje. AC: valor vigente destacado en el listado de Perfiles; editable a mano; aumento por % con confirmacion previa; ambos cambios recalculan todos los Perfiles activos. (Sesion 6: este es el precio de referencia global de catalogo — el aumento por Centro de Salud especifico se hace desde WF-16/CU-10.)

**HU-04** — El precio de un Perfil se calcula solo a partir de su composicion. AC: sin campo de precio ni de Unidad editable al crear/editar; Unidad se calcula en vivo a partir de la composicion (`Σ Cantidad × CantidadUnidades` de cada componente); precio = Unidad calculada × Precio por Unidad (global o del Centro de Salud segun el contexto); F-001 ya no permite editar Perfiles.

**HU-05** — El PDF de Produccion Mensual muestra el precio unitario completo sin recorte. AC: montos de 4+ digitos se muestran completos sin superposicion.

**HU-06** — Cargar un periodo de Produccion Mensual para un Centro de Salud especifico. AC: selector opcional de Centro de Salud activo al crear; varios periodos por mismo Mes/Año si cada uno tiene Centro distinto (o uno solo sin centro); duplicado (mismo Mes+Año+Centro, o global duplicado) bloqueado con mensaje claro.

**HU-07** — Administrar un catalogo simple de Centros de Salud. AC: crear/editar/baja logica con Nombre y Tipo; el catalogo distingue el Tipo con badge.

**HU-08** — Ver y filtrar el historial de Produccion Mensual por Centro de Salud. AC: columna con nombre del Centro o "— Global —"; filtro por Centro de Salud.

**HU-09** — El PDF de un periodo muestra el Centro de Salud al que corresponde. AC: si tiene Centro asignado, aparece en el encabezado; si no, el PDF se ve igual que antes.

**HU-10 (sesion 6, VERSION FINAL)** — Cargar/editar el "Precio de Unidad Bioquimica" de cada Centro de Salud. AC: pantalla con un listado de Centros de Salud, cada uno con un unico campo editable (+ aumento %); un unico guardado por centro; centros sin precio cargado se distinguen visualmente. A partir de ese valor se calculan automaticamente los precios de todas las Practicas y Perfiles en ese centro (no hay que cargar nada por item).

**HU-11 (sesion 6, VERSION FINAL)** — Al cargar Produccion Mensual, el precio de cada item corresponde al Centro de Salud del periodo. AC: Centro de Salud obligatorio al crear un periodo nuevo; el precio de cada Practica se calcula como `CantidadUnidades × Precio de Unidad Bioquimica del centro`, y el de cada Perfil como `Unidad (calculada de su composicion) × Precio de Unidad Bioquimica del centro`; si el centro no tiene su precio cargado, o el item no tiene cantidad/volumen calculable, el sistema bloquea el alta con mensaje claro y accionable; los periodos historicos sin centro (previos a esta sesion) siguen funcionando exactamente igual que antes.

**HU-12 (sesion 6, nueva)** — Cargar la cantidad de unidades bioquimicas de cada Practica. AC: el ABM de Practicas pide `CantidadUnidades` (entero >= 1) en vez de un precio en $; el precio de referencia se calcula y se muestra solo lectura.

## Historial de ajustes
- 2026-06-13: Diseño funcional completo (v1) producido — 10 wireframes textuales (WF-01 a WF-10), 11 ViewModels, 11 reglas de negocio (RN-01 a RN-11), 3 contratos de Services, plan funcional en 3 etapas. Input: `1-analista-funcional.md` v1 aprobado (P1-P5).
- 2026-07-08 (sesion 2): Diseño de 3 mejoras — carga masiva + alta rápida (WF-11, VM-12 a VM-15), Unidad/PrecioPorUnidad reemplazando el precio manual y el cascade F-001 para Perfiles (RN-16 a RN-21, deroga RN-01), fix de ancho de columna del PDF (WF-12). 5 historias de usuario (HU-01 a HU-05). Input: `1-analista-funcional.md` sesión 4 aprobada (P6-P10).
- 2026-07-23 (sesion 3): Diseño de Producción Mensual por Centro de Salud — ABM nuevo (WF-13/WF-14, VM-17/VM-18), selector opcional en Crear Periodo (WF-07 ajustado), columna/filtro en historial (WF-06 ajustado), línea en PDF (WF-15), RN-22 a RN-25 (RN-24 reemplaza RN-11). 4 historias de usuario (HU-06 a HU-09). Input: `1-analista-funcional.md` sesión 5 aprobada (P11-P14).
- 2026-08-23 (sesion 6): Diseño de Precio por Unidad Bioquimica y por Perfil diferenciado por Centro de Salud — 2 rondas de correccion del cliente hasta el modelo final: la "unidad bioquimica" es propiedad de la Practica (`CantidadUnidades`, campo nuevo); el Perfil calcula su `Unidad` a partir de la composicion (RN-33), lo que **reactiva RN-02** (composicion obligatoria, derogada en sesion 4) y **deroga RN-14** (alta rapida ya no puede omitir composicion). Pantalla nueva WF-16 (un valor de "Precio de Unidad Bioquimica" por Centro de Salud, no una matriz), ajustes WF-01/WF-02 (Practicas piden CantidadUnidades en vez de precio) y WF-03/WF-04 (Unidad de Perfil pasa a solo lectura), RN-26 a RN-33, DD-06 a DD-10 (DD-09: recalculo en cascada al editar CantidadUnidades de una Practica ya usada en Perfiles; DD-10: Perfiles ya en produccion sin composicion completa quedan sin precio calculable), HU-10/HU-11 revisadas + HU-12 nueva. Input: `1-analista-funcional.md` sesion 6 aprobada (version final). DISEÑO FUNCIONAL CERRADO — listo para revision del arquitecto.
- 2026-08-16: Reestructuración documental — este archivo tenía el diseño base v1 (`## Definiciones vigentes` original) ubicado *después* de las sesiones 2 y 3 (orden cronológico invertido), con un encabezado `## Historial de ajustes` duplicado a mitad de archivo. Consolidado en una única `## Definiciones vigentes` con el estado final de cada pantalla/ViewModel/regla (marcando explícitamente qué reglas derogaron o reemplazaron a cuáles — RN-20 deroga RN-01, RN-24 reemplaza RN-11) + este historial cronológico único. Ningún dato funcional se perdió.
