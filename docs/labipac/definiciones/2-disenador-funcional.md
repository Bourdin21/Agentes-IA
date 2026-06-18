# Memoria - Disenador funcional

## Proyecto: labipac
## Ultima actualizacion: 2026-06-13 (sesion 1 — diseno funcional COMPLETO)

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

