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

### Maquina de estados
No aplica en ningun modulo (confirmado en Analisis, P4-A).

### Reglas de negocio vigentes (estado final, incluye derogaciones/reemplazos)
| Ref | Regla | Capa | Estado |
|---|---|---|---|
| RN-02 | Practica/Perfil admite composicion (relacion M:N) | Service + DataAnnotation | Vigente, ya informativa (ver RN-20) |
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
| RN-14 | Alta rapida de Perfil no exige composicion (relaja RN-02 solo en este flujo) | Service | Vigente |
| RN-15 | Alta rapida de Practica (UnidadBioquimica) sin cambios respecto al ABM existente | Service | Vigente |
| RN-16 | `Practica.PrecioActual = Unidad × PrecioPorUnidad.ValorVigente`, recalculado al crear/editar el Perfil y en cada cambio del `PrecioPorUnidad` global (recalculo batch) | Service | Vigente |
| RN-17 | `Unidad` entero, obligatorio, >= 1 | DataAnnotation | Vigente |
| RN-18 | `PrecioPorUnidad.Valor` obligatorio, >= 0 | DataAnnotation + Service | Vigente |
| RN-19 | Aumento %: `NuevoValor = round(ValorActual × (1 + %/100), 2)`, dispara recalculo batch de todos los Perfiles activos | Service | Vigente |
| RN-20 | Reemplaza RN-01 original ("precio Perfil < sumatoria de componentes") | — | RN-01 DEROGADA para Perfiles |
| RN-21 | F-001 (`Precios/AumentoMasivo`) ya no ofrece edicion/cascade sobre Perfiles; sigue aplicando sin cambios sobre Practicas (UnidadBioquimica) | Web | Vigente |
| RN-22 | `CentroSalud.Nombre` obligatorio, <=150 caracteres | DataAnnotation | Vigente |
| RN-23 | `CentroSalud.Tipo` obligatorio (Privado o Mutual) | DataAnnotation | Vigente |
| RN-24 | Reemplaza RN-11 original ("no duplicar mismo mes+año"): no puede existir mas de un periodo por Mes+Año+CentroSaludId, tratando NULL como valor propio | Service | RN-11 REEMPLAZADA |
| RN-25 | `CentroSaludId` en `ProduccionMensual` opcional; si se informa, debe corresponder a un `CentroSalud` activo y no eliminado | Service | Vigente |

**Permisos:** ABM de Centros de Salud, alta rapida de Perfil/Practica desde carga masiva: `[Authorize]` sin politica especifica (igual que Unidades Bioquimicas/Practicas). Editar `PrecioPorUnidad` (valor manual o aumento %): `RequireAdministracion` (mismo criterio que F-001 y guardado de IVA).

### Contratos funcionales de Services vigentes
- `IUnidadBioquimicaService`: GetAllAsync, GetActivasAsync, GetByIdAsync, CreateAsync, UpdateAsync, DeleteAsync.
- `IPracticaService`: GetAllAsync, GetActivasAsync, GetByIdAsync, CreateAsync, UpdateAsync, DeleteAsync + logica de recalculo de precio derivado (RN-16), sin la validacion RN-01 original (`CalcularSumatoria` queda como dato informativo).
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
- **DD-01:** un Perfil creado por alta rapida puede quedar "sin composicion" (0 Unidades Bioquimicas asociadas) — cambio de comportamiento respecto a RN-02 original, aceptado porque la composicion ya no determina el precio. Se muestra badge/aviso "Sin composicion" en el listado.
- **DD-02:** el recalculo batch de todos los Perfiles activos al cambiar `PrecioPorUnidad` debe ser transaccional. Volumen esperado bajo (mismo supuesto que la arquitectura original).
- **DD-03:** al guardar una fila de carga masiva para un periodo historico, aplica el mismo aviso P5-B ya vigente — no es un caso nuevo.
- **DD-04:** unicidad Mes+Año+CentroSaludId con NULL como valor propio no es un unique index nativo simple en MySQL — se resuelve en Service con consulta explicita que distingue el caso NULL (mismo patron que la unicidad original Mes+Año).
- **DD-05:** se acepta convivencia de nombres duplicados entre `CentroSalud` y `Mutual` (FABA) sin vinculo — decision explicita del cliente (P12), no es un defecto.
- Riesgo heredado RA-01 original (baja logica de UnidadBioquimica con composicion activa en Perfil) ya no afecta el precio (independiente de la composicion); se mantiene badge informativo si un componente esta inactivo.
- Unico riesgo tecnico pendiente heredado del diseño original: RF-03 (baja logica de unidad con composicion activa — recalcular sumatoria/snapshot informativo).
- AJAX endpoint `GET /ProduccionMensual/GetPrecioItem?tipo=&id=` para pre-completado de precio en modal.

### Historias de usuario vigentes
**HU-01** — Cargar varias lineas de produccion mensual en un solo formulario. AC: N filas dinamicas antes de guardar; un solo "Guardar todas las líneas" persiste todo; fila invalida bloquea el guardado completo con errores puntuales por fila.

**HU-02** — Crear un Perfil o Practica nueva sin salir de la carga masiva. AC: opcion "+ Crear nuevo…" por fila; el nuevo registro queda seleccionado sin recargar; un Perfil nuevo no exige composicion.

**HU-03** — Configurar el Precio por Unidad y aumentarlo por porcentaje. AC: valor vigente destacado en el listado de Perfiles; editable a mano; aumento por % con confirmacion previa; ambos cambios recalculan todos los Perfiles activos.

**HU-04** — El precio de un Perfil se calcula solo a partir de su cantidad de Unidades. AC: sin campo de precio editable al crear/editar; precio calculado en vivo (Unidad × Precio por Unidad); F-001 ya no permite editar Perfiles.

**HU-05** — El PDF de Produccion Mensual muestra el precio unitario completo sin recorte. AC: montos de 4+ digitos se muestran completos sin superposicion.

**HU-06** — Cargar un periodo de Produccion Mensual para un Centro de Salud especifico. AC: selector opcional de Centro de Salud activo al crear; varios periodos por mismo Mes/Año si cada uno tiene Centro distinto (o uno solo sin centro); duplicado (mismo Mes+Año+Centro, o global duplicado) bloqueado con mensaje claro.

**HU-07** — Administrar un catalogo simple de Centros de Salud. AC: crear/editar/baja logica con Nombre y Tipo; el catalogo distingue el Tipo con badge.

**HU-08** — Ver y filtrar el historial de Produccion Mensual por Centro de Salud. AC: columna con nombre del Centro o "— Global —"; filtro por Centro de Salud.

**HU-09** — El PDF de un periodo muestra el Centro de Salud al que corresponde. AC: si tiene Centro asignado, aparece en el encabezado; si no, el PDF se ve igual que antes.

## Historial de ajustes
- 2026-06-13: Diseño funcional completo (v1) producido — 10 wireframes textuales (WF-01 a WF-10), 11 ViewModels, 11 reglas de negocio (RN-01 a RN-11), 3 contratos de Services, plan funcional en 3 etapas. Input: `1-analista-funcional.md` v1 aprobado (P1-P5).
- 2026-07-08 (sesion 2): Diseño de 3 mejoras — carga masiva + alta rápida (WF-11, VM-12 a VM-15), Unidad/PrecioPorUnidad reemplazando el precio manual y el cascade F-001 para Perfiles (RN-16 a RN-21, deroga RN-01), fix de ancho de columna del PDF (WF-12). 5 historias de usuario (HU-01 a HU-05). Input: `1-analista-funcional.md` sesión 4 aprobada (P6-P10).
- 2026-07-23 (sesion 3): Diseño de Producción Mensual por Centro de Salud — ABM nuevo (WF-13/WF-14, VM-17/VM-18), selector opcional en Crear Periodo (WF-07 ajustado), columna/filtro en historial (WF-06 ajustado), línea en PDF (WF-15), RN-22 a RN-25 (RN-24 reemplaza RN-11). 4 historias de usuario (HU-06 a HU-09). Input: `1-analista-funcional.md` sesión 5 aprobada (P11-P14).
- 2026-08-16: Reestructuración documental — este archivo tenía el diseño base v1 (`## Definiciones vigentes` original) ubicado *después* de las sesiones 2 y 3 (orden cronológico invertido), con un encabezado `## Historial de ajustes` duplicado a mitad de archivo. Consolidado en una única `## Definiciones vigentes` con el estado final de cada pantalla/ViewModel/regla (marcando explícitamente qué reglas derogaron o reemplazaron a cuáles — RN-20 deroga RN-01, RN-24 reemplaza RN-11) + este historial cronológico único. Ningún dato funcional se perdió.
