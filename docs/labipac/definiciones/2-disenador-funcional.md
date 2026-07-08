# Memoria - Disenador funcional

## Proyecto: labipac
## Ultima actualizacion: 2026-07-08 (sesion 2 — diseno de 3 mejoras: carga masiva, Unidad/PrecioPorUnidad, fix PDF)

## Sesion 2 (2026-07-08) — Diseno funcional de 3 mejoras

Input: `1-analista-funcional.md` sesion 4, ANALISIS CERRADO, preguntas P6-P10 confirmadas.

### 1. Alcance funcional resumido
1. Pantalla nueva de carga masiva de lineas de Produccion Mensual (filas repetibles, un submit) + alta rapida inline de Perfiles y Practicas (modales AJAX) sin salir de la pantalla.
2. Propiedad `Unidad` en Perfil (entidad `Practica`) + configuracion global `PrecioPorUnidad` (editable a mano + boton de aumento %), ubicada en el listado de Perfiles. El precio del Perfil pasa a ser 100% calculado (`Unidad x PrecioPorUnidad`), se retira la edicion manual y se ajusta F-001 (Aumento masivo) para excluir Perfiles.
3. Fix de ancho de columna "Precio unit." en el reporte PDF de Produccion Mensual.

### 2. Flujo de pantallas y wireframes textuales

**WF-11: Produccion Mensual — Carga Masiva (pantalla nueva)**
- Ruta: `GET/POST /ProduccionMensual/CargaMasiva/{produccionMensualId}`
- Se accede desde un boton nuevo "Carga masiva" junto a "Agregar ítem" en `Detalle.cshtml`.
- Header: titulo "Carga masiva — {Periodo}" + badge Periodo historico (mismo patron ya usado, P5-B) + boton "Volver al detalle".
- Card con tabla dinamica de filas (manejada por JS, sin DataTables — es un formulario, no un listado):
  - Columnas por fila: Tipo (radio/select Perfil|Practica) · Item (Select2 dependiente del tipo, con opcion "+ Crear nuevo…" al final de la lista) · Cantidad · Precio unitario (autocompletado por AJAX `GetPrecioItem` existente, editable, con aviso de periodo historico igual que hoy) · Subtotal (solo lectura, JS) · Accion Quitar fila.
  - Boton "+ Agregar fila" al pie de la tabla (clona fila plantilla, minimo 1 fila visible siempre).
  - Total general (JS, suma de subtotales) visible al pie, antes del boton final.
  - Boton "Guardar todas las líneas" (submit unico, POST de todas las filas). Boton "Cancelar" vuelve a Detalle sin guardar nada.
- Modal Alta Rapida Perfil (se abre desde "+ Crear nuevo…" del select de Perfil en cualquier fila): Nombre + Unidad. Muestra "Precio calculado: $ X" en vivo (JS, Unidad × PrecioPorUnidad vigente inyectado en la vista). Sin exigencia de composicion (DD-01, ver Riesgos). Al guardar (AJAX), se inserta como nueva opcion seleccionada en el select de la fila que lo origino, sin recargar la pantalla.
- Modal Alta Rapida Practica (UnidadBioquimica): Nombre + Precio actual (igual que el ABM existente hoy). Mismo comportamiento de insercion AJAX.

**Ajuste WF-08 (Detalle.cshtml):** se agrega boton "Carga masiva" (btn-outline-primary) junto a "Agregar ítem". El modal "Agregar ítem" existente NO se modifica (sigue sirviendo para alta de una sola linea rapida).

**Ajuste WF-03/WF-04 (Perfiles Index/Create/Edit — hoy "Practicas"):**
- Index: se agrega columna "Unidad" y se reemplaza la columna "Precio actual" (editable) por "Precio (calculado)" de solo lectura. Se agrega, arriba de la tabla, una card "Precio por Unidad" (mismo patron visual que la card "IVA del período" de `Detalle.cshtml`): valor vigente destacado + input editable con boton "Guardar" + input % con boton "Aumentar %" (confirmacion SweetAlert2, muestra antes/despues de cuantos Perfiles se veran afectados).
- Create/Edit: se quita el campo "Precio actual" editable. Se agrega campo "Unidad" (numero entero >= 1). Se muestra un texto informativo "Precio calculado: $ X" recalculado en vivo por JS al tipear Unidad (usa `PrecioPorUnidadVigente` inyectado en el ViewModel). La seccion de composicion (Select2 multiple de Unidades Bioquimicas / "Practicas") se mantiene pero pasa a ser **informativa/opcional**, ya no valida contra el precio (se quita el texto "sumatoria de componentes debe superar el precio").

**Ajuste F-001 (`Precios/AumentoMasivo.cshtml`):** se quita el tab "Perfiles" (ya no aplica: el precio de Perfil no se edita manualmente ni cascade). Se agrega una nota informativa: "Los precios de los Perfiles se actualizan automaticamente segun el Precio por Unidad configurado en Perfiles." El tab "Practicas" (UnidadBioquimica) sigue igual, sin cambios de logica.

**WF-12: Fix reporte PDF (sin cambio de pantalla, solo ajuste de reporte)**
- Columna "Precio unit." pasa de 55 a 75 puntos de ancho fijo en la tabla del PDF (`ProduccionMensualController.ReportePdf`). Se ajusta "Tipo" de 65 a 60 para compensar y mantener balance visual en A4 portrait.

### 3. ViewModels propuestos

| VM | Campos | Validaciones |
|---|---|---|
| VM-12 `ProduccionCargaMasivaViewModel` | ProduccionMensualId, Periodo, EsPeriodoHistorico, List\<VM-13\> Filas, PerfilesDisponibles, PracticasDisponibles | Al menos 1 fila con Cantidad >= 1 |
| VM-13 `ProduccionCargaMasivaFilaViewModel` | TipoItem (enum), ItemId, Cantidad, PrecioSnapshot | Cantidad entero >=1, PrecioSnapshot >=0, TipoItem+ItemId requeridos, sin duplicados TipoItem+ItemId dentro del mismo submit (RN-13) |
| VM-14 `PerfilAltaRapidaViewModel` | Nombre, Unidad | Nombre requerido (<=150), Unidad entero >=1 |
| VM-15 `PracticaAltaRapidaViewModel` (UnidadBioquimica) | Nombre, PrecioActual | Igual que ABM existente hoy (Nombre requerido, Precio >=0) |
| VM-16 `PrecioPorUnidadViewModel` | ValorActual, NuevoValor (edicion manual), PorcentajeAumento (accion aumento) | ValorActual/NuevoValor >=0; PorcentajeAumento 0,01-999,99 |
| VM-03 `PracticaCreateViewModel` (modificado) | Nombre, **Unidad** (nuevo, reemplaza PrecioActual editable), PrecioPorUnidadVigente (solo lectura, para JS), UnidadBioquimicaIds (ahora opcional), UnidadesDisponibles | Unidad entero >=1. Se quita validacion RN-01 |
| VM-04 `PracticaRowViewModel` (modificado) | + campo **Unidad** | — |

### 4. Maquina de estados
No aplica (confirmado en analisis original, P4-A). Los 3 items no introducen estados nuevos.

### 5. Reglas de negocio y permisos

| Ref | Regla | Capa |
|---|---|---|
| RN-12 | Guardado de carga masiva es atomico: todas las filas se guardan en una unica transaccion o ninguna | Service |
| RN-13 | No se permite la misma combinacion TipoItem+ItemId repetida dentro del mismo submit de carga masiva | Service + validacion cliente |
| RN-14 | Alta rapida de Perfil no exige composicion (relaja RN-02 solo para este flujo); queda "sin composicion" hasta completarla luego en Perfiles/Edit | Service |
| RN-15 | Alta rapida de Practica (UnidadBioquimica) sin cambios respecto al ABM existente | Service |
| RN-16 | `Practica.PrecioActual = Unidad * PrecioPorUnidad.ValorVigente`, recalculado al crear/editar el Perfil y en cada cambio del `PrecioPorUnidad` global (recalculo batch de todos los Perfiles activos) | Service |
| RN-17 | `Unidad` es entero, obligatorio, >= 1 | DataAnnotation |
| RN-18 | `PrecioPorUnidad.Valor` obligatorio, >= 0 | DataAnnotation + Service |
| RN-19 | Aumento %: `NuevoValor = round(ValorActual * (1 + %/100), 2)`, aplica sobre el unico valor global, dispara recalculo batch de todos los Perfiles activos | Service |
| RN-20 | DEROGADA: RN-01 (precio Perfil < sumatoria de componentes) ya no aplica a Perfiles | — |
| RN-21 | F-001 (`Precios/AumentoMasivo`) deja de ofrecer edicion/cascade sobre Perfiles; sigue aplicando sin cambios sobre Practicas (UnidadBioquimica) | Web |

**Permisos:** alta rapida de Perfil/Practica desde carga masiva usa los mismos permisos que los ABM existentes hoy (`[Authorize]` sin politica especifica). Editar `PrecioPorUnidad` (valor manual o aumento %) requiere `RequireAdministracion` (mismo criterio que F-001 y el guardado de IVA).

### 6. Impacto funcional por capa
- **Presentacion:** 1 controller nuevo o extendido (`ProduccionMensualController` +3 acciones: `CargaMasiva` GET/POST, `CrearPerfilRapido` AJAX, `CrearPracticaRapido` AJAX), 1 vista nueva (`CargaMasiva.cshtml`) + 2 modales parciales, ajustes en `Detalle.cshtml` (boton nuevo), `Practicas/Index.cshtml` + `Create.cshtml` + `Edit.cshtml` (card Precio por Unidad, columna Unidad, quitar precio editable), `Precios/AumentoMasivo.cshtml` (quitar tab Perfiles), `ReportePdf` (ancho columna).
- **Negocio:** `IProduccionMensualService` +metodo `AgregarLineasAsync` (batch atomico); `IPracticaService` +logica de recalculo de precio derivado y quitar validacion RN-01; nuevo contrato `IPrecioPorUnidadService` (ObtenerVigente, ActualizarValor, AumentarPorcentaje — dispara recalculo batch).
- **Datos:** nuevo campo `Practica.Unidad` (int). Nueva entidad/tabla para persistir `PrecioPorUnidad` (valor unico global, con auditoria de quien/cuando lo cambio) — a definir formato exacto en Arquitectura (tabla dedicada vs. fila de configuracion generica). Migracion EF requerida.

### 7. Riesgos y supuestos
- **DD-01:** se acepta que un Perfil creado por alta rapida quede "sin composicion" (0 Unidades Bioquimicas asociadas) — es un cambio de comportamiento respecto a RN-02 original ("minimo 1 componente"), se relaja porque la composicion ya no determina el precio. Se debe mostrar un badge/aviso "Sin composicion" en el listado de Perfiles para que el usuario la complete si la necesita para otro fin (trazabilidad de laboratorio).
- **DD-02:** el recalculo batch de todos los Perfiles activos al cambiar `PrecioPorUnidad` reescribe `PrecioActual` de N registros — debe ser una operacion transaccional. Si el volumen de Perfiles crece mucho a futuro, evaluar performance (hoy volumen esperado es bajo, mismo supuesto SA-04 de la arquitectura original).
- **DD-03:** al guardar una fila de carga masiva para un periodo historico, aplica el mismo aviso P5-B ya vigente (precio pre-completado editable) — no es un caso nuevo, se reutiliza.
- Riesgo heredado RA-01 (baja logica de UnidadBioquimica con composicion activa en Perfil) ya no aplica al precio (que ahora es independiente de la composicion), pero se mantiene el badge visual informativo si un componente esta inactivo.

### 8. Plan funcional por etapas (para Arquitectura)
- **Etapa A — Unidad y Precio por Unidad:** campo `Unidad` en Practica, entidad/config `PrecioPorUnidad`, recalculo de precio, ajuste de Perfiles Index/Create/Edit, ajuste de F-001 (quitar tab Perfiles). Es la base de la que depende el resto (el precio mostrado en carga masiva y en el nuevo alta rapida de Perfil depende de esto).
- **Etapa B — Carga masiva + alta rapida:** pantalla `CargaMasiva`, modales de alta rapida, `AgregarLineasAsync` atomico. Depende de Etapa A para el calculo de precio del alta rapida de Perfil.
- **Etapa C — Fix PDF:** independiente, sin dependencias, puede hacerse en paralelo o primero (es el de menor esfuerzo).

### Historias de usuario

**HU-01** — Como usuario del sistema, quiero cargar varias lineas de produccion mensual en un solo formulario, para no tener que repetir el modal de a una linea por vez.
- AC: la pantalla permite agregar N filas dinamicamente antes de guardar.
- AC: un unico click en "Guardar todas las líneas" persiste todas las filas validas en una sola operacion.
- AC: si una fila es invalida (cantidad <1, item no seleccionado, duplicado), no se guarda ninguna fila y se muestran los errores puntuales por fila.

**HU-02** — Como usuario del sistema, quiero crear un Perfil o una Practica nueva sin salir de la pantalla de carga masiva, para no interrumpir la carga del mes.
- AC: cada fila tiene una opcion "+ Crear nuevo…" en su selector de item.
- AC: al crear, el nuevo registro aparece automaticamente seleccionado en esa fila sin recargar la pagina.
- AC: crear un Perfil nuevo no exige cargar su composicion (puede completarse despues).

**HU-03** — Como usuario del sistema, quiero configurar el Precio por Unidad y aumentarlo por porcentaje de forma simple, para no tener que editar cada Perfil uno por uno cuando sube el valor de referencia.
- AC: el valor vigente de Precio por Unidad se ve destacado en el listado de Perfiles.
- AC: puedo editarlo a mano y guardar.
- AC: puedo ingresar un porcentaje y aplicar un aumento con un solo click, con confirmacion previa.
- AC: al aplicar cualquiera de los dos cambios, el precio de todos los Perfiles activos se actualiza automaticamente y se ve reflejado en el listado.

**HU-04** — Como usuario del sistema, quiero que el precio de un Perfil se calcule solo a partir de su cantidad de Unidades, para no tener que fijarlo a mano ni mantenerlo consistente manualmente.
- AC: al crear/editar un Perfil, no hay campo de precio editable, solo "Unidad".
- AC: se muestra el precio calculado en vivo (Unidad x Precio por Unidad vigente) antes de guardar.
- AC: la pantalla de Aumento masivo de precios (F-001) ya no permite editar Perfiles directamente.

**HU-05** — Como usuario del sistema, quiero que el reporte PDF de Produccion Mensual muestre el precio unitario completo sin que se corten los digitos, para poder leerlo correctamente.
- AC: en un periodo con montos de 4+ digitos, la columna "Precio unit." muestra el valor completo sin recorte ni superposicion.

## Historial de ajustes
- 2026-06-13: Diseno funcional completo producido. 10 wireframes textuales, 11 ViewModels, 11 reglas de negocio, 3 contratos de Services, plan funcional en 3 etapas. Input: 1-analista-funcional.md aprobado con P1-P5 confirmadas.
- 2026-07-08: Diseno funcional de 3 mejoras (carga masiva + alta rapida, Unidad/PrecioPorUnidad reemplazando F-001 para Perfiles, fix ancho columna PDF). 1 wireframe nuevo (WF-11 Carga Masiva) + ajustes a WF-03/04/08 y a F-001. 5 ViewModels nuevos + 2 modificados. 10 reglas de negocio nuevas (RN-12 a RN-21, incluye derogacion de RN-01). Plan funcional en 3 etapas (A: Unidad/Precio, B: Carga masiva, C: fix PDF). 5 historias de usuario con criterios de aceptacion. Input: 1-analista-funcional.md sesion 4 aprobada (P6-P10).

## Definiciones vigentes

### Flujo funcional
- Login → Dashboard → Sidebar (Configuracion / Produccion)
- Configuracion: ABM UnidadesBioquimicas, ABM Practicas (con composicion muchos-a-muchos y sumatoria JS)
- Produccion: Index del historial → Crear periodo → Detalle/Carga (pantalla principal con tabla de lineas + panel resumen)
- Modal Agregar linea: tipo radio + Select2 por tipo + cantidad + precio editable + aviso historico P5-B via AJAX
- Modal Editar linea: cantidad + precio editable
- Eliminar linea: soft delete con SweetAlert2 confirm

### Pantallas definidas
- WF-01: Unidades Bioquimicas Index (DataTables client-side, baja logica, reactivar)
- WF-02: Unidades Bioquimicas Create/Edit (col-md-6, campo precio, estado checkbox)
- WF-03: Practicas Index (DataTables client-side, columna sumatoria, boton ver composicion)
- WF-04: Practicas Create/Edit (col-md-6 base + seccion composicion Select2 multiple + sumatoria JS + precio con referencia)
- WF-05: Practicas Details (tabla composicion readonly + totales)
- WF-06: Produccion Mensual Index/Historial (DataTables client-side, orden desc, total estimado)
- WF-07: Produccion Mensual Crear Periodo (col-md-4, mes dropdown, anio, notas)
- WF-08: Produccion Mensual Detalle/Carga (col-md-8 tabla + col-md-4 panel resumen sticky)
- WF-09: Modal Agregar Item (radio tipo, Select2 dinamico, cantidad, precio editable + aviso P5-B)
- WF-10: Modal Editar Linea (campos cantidad y precio editable)

### ViewModels definidos (11 total)
- VM-01: UnidadBioquimicaCreateViewModel / EditViewModel
- VM-02: UnidadBioquimicaRowViewModel
- VM-03: PracticaCreateViewModel / EditViewModel (incluye UnidadesDisponibles + PreciosDisponibles para JS)
- VM-04: PracticaRowViewModel
- VM-05: PracticaDetailsViewModel
- VM-06: ProduccionMensualCreateViewModel
- VM-07: ProduccionMensualRowViewModel
- VM-08: ProduccionMensualDetalleViewModel (con flag EsPeriodoHistorico para aviso P5-B)
- VM-09: ProduccionDetalleRowViewModel (con NombreSnapshot, PrecioSnapshot, Subtotal)
- VM-10: ProduccionDetalleAgregarViewModel (con PrecioSugerido para AJAX, EsPeriodoHistorico)
- VM-11: ProduccionDetalleEditarViewModel

### Reglas de negocio modeladas
- RN-01: PrecioActual(Practica) < SumatoriaComponentes — Service + JS referencia
- RN-02: Practica requiere al menos 1 componente — Service + DataAnnotation
- RN-03: Cambio de precio de unidad no afecta historial — por diseno de campo precio_snapshot
- RN-04: No duplicar mismo item en el mismo periodo — Service
- RN-05: Precio pre-completado por AJAX al seleccionar item en modal — Controller AJAX
- RN-06: Aviso de periodo historico (mes/anio != actual) — flag EsPeriodoHistorico en VM
- RN-07: Cantidad entero >= 1 — DataAnnotation
- RN-08: PrecioSnapshot >= 0 — DataAnnotation
- RN-09: Solo items activos en nuevas lineas — Service (filtra GetActivasAsync)
- RN-10: Total recalculado en tiempo real — JS sobre DataTable
- RN-11: No duplicar periodo (mismo mes+anio) — Service

### Contratos funcionales de Services
- IUnidadBioquimicaService: GetAllAsync, GetActivasAsync, GetByIdAsync, CreateAsync, UpdateAsync, DeleteAsync
- IPracticaService: GetAllAsync, GetActivasAsync, GetByIdAsync, CalcularSumatoria, CreateAsync, UpdateAsync, DeleteAsync
- IProduccionMensualService: GetAllAsync, GetByIdAsync, CreateAsync, DeleteAsync, GetPrecioVigente, AgregarLineaAsync, EditarLineaAsync, EliminarLineaAsync

### Logica de distribucion de elementos (estandar todo el sistema)
- Listado: Header + card > DataTables client-side. Badge estado. btn-group-sm acciones.
- Formulario simple: Header + card > col-md-6 campos + Guardar/Cancelar
- Formulario con relacion: igual con secciones separadas por divisor visual + Select2 multiple
- Detalle readonly: Header + card > info + tabla composicion
- Pantalla principal de trabajo: Header + row col-md-8 tabla + col-md-4 panel resumen sticky
- Modal: campos minimos + aviso contextual si aplica

### Supuestos y dependencias
- Maquina de estados: NO aplica (P4-A).
- Unico riesgo tecnico pendiente para arquitecto: RF-03 (baja logica de unidad con composicion activa en practica — recalcular sumatoria o snapshot).
- AJAX endpoint: GET /ProduccionMensual/GetPrecioItem?tipo=&id= para pre-completado de precio en modal.
- Sumatoria en Practicas Create/Edit puede resolverse con datos del ViewModel en JS (sin AJAX adicional).

## Historial de ajustes
- 2026-06-13: Diseno funcional completo producido. 10 wireframes textuales, 11 ViewModels, 11 reglas de negocio, 3 contratos de Services, plan funcional en 3 etapas. Input: 1-analista-funcional.md aprobado con P1-P5 confirmadas.

