# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-06-23 19:05 - presupuestador — TOKEN IA EXPLICITO
- Etapa: Presupuesto / Estandarizacion de formato
- Cambio: Se adopta presentacion de Tokens IA como item individual y visible (sin prorrateo visible por modulo) en la memoria de presupuesto y en la plantilla de presupuesto cliente para futuros proyectos.
- Motivo: Mejor transparencia comercial y comunicacion del valor agregado de desarrollo asistido por IA.
- Impacto en capas: Documentacion comercial y memoria interna del agente presupuestador.
- Riesgos/supuestos: Mantener consistencia entre subtotal desarrollo, Tokens IA y total cliente para evitar doble conteo en cierres futuros.

### 2026-06-23 18:40 - presupuestador — ACTUALIZACION POST-IMPLEMENTACION
- Etapa: Presupuesto / Cierre de calibracion estimado vs real
- Cambio: Se actualizo el presupuesto para incorporar alcance implementado adicional: ABM de Pacientes + integracion parcial con web service de FABA (analitos, mutuales y consulta de pacientes). Se recalcularon tablas O/M/P, PERT, contingencia y totales economicos. Se registro hora real total informada: 12h.
- Motivo: Ajustar memoria presupuestaria al alcance finalmente implementado y cerrar calibracion con dato real.
- Impacto en capas: Web (ABM Pacientes y pantallas de consulta), Application (servicios/DTOs de pacientes e integracion parcial), Infrastructure (consumo de endpoints FABA y mapeo de catalogos), Datos (persistencia/normalizacion de datos sincronizados si aplica).
- Riesgos/supuestos: Integracion FABA asumida como parcial (sin sincronizacion bidireccional ni workflow de estados complejos). Desvio observado por sobreestimacion inicial para este tipo de modulos; se propone recalibrar banda M/P en futuros presupuestos comparables.

### 2026-06-12 13:58 - analista-funcional
- Etapa: Discovery/Analisis
- Cambio: Se creó la carpeta documental del proyecto y se definio el alcance funcional inicial de labipac.
- Motivo: Dejar memoria persistente para las siguientes etapas y ordenar el relevamiento funcional.
- Impacto en capas: Presentacion, Negocio, Datos
- Riesgos/supuestos: Falta validar si las practicas son paquetes cerrados o si se desglosan por estudios, si los precios tienen vigencia historica y si los meses quedan cerrados.

### 2026-06-13 sesion 2 - analista-funcional
- Etapa: Discovery/Analisis — cierre de preguntas P1-P4
- Cambio: P1-B confirmado (practicas y unidades bioquimicas sueltas coexisten en produccion mensual). P2-B confirmado (unidad bioquimica compartida entre multiples practicas, relacion muchos a muchos). P3-A confirmado (precio snapshot por linea, inmutable retroactivamente). P4-A confirmado (periodos siempre editables, sin cierre). Se elimino maquina de estados del alcance. Se elimino R1 como riesgo activo. Se identifico nueva pregunta P5: comportamiento del snapshot al editar un mes historico.
- Motivo: El usuario respondio las 4 preguntas pendientes de la sesion anterior.
- Impacto en capas: Datos (campo precio_snapshot en ProduccionDetalle, relacion muchos-a-muchos en PracticaDetalle). Negocio (regla de calculo usa snapshot, no precio actual). Presentacion (sin logica de cierre en UI del periodo mensual).
- Riesgos/supuestos: R2 activo — posible inconsistencia de snapshots al editar un mes historico (P5 pendiente). R3 aceptado por diseno.
- Preguntas pendientes: P5 (precio snapshot al agregar una linea a un mes historico ya existente).

### 2026-06-13 sesion 3 - analista-funcional — ANALISIS CERRADO
- Etapa: Discovery/Analisis — cierre de P5 y cierre total del relevamiento
- Cambio: P5-B confirmado. Al agregar una linea nueva a un periodo historico, el sistema muestra el precio actual del catalogo pre-completado en un campo editable con aviso visual. El usuario puede ajustarlo manualmente antes de guardar. Las lineas ya guardadas no se modifican. R2 marcado como mitigado por diseno.
- Motivo: El usuario respondio la ultima pregunta pendiente.
- Impacto en capas: Presentacion (campo precio editable + aviso en formulario de nueva linea de produccion). Datos (precio_snapshot siempre editable al momento de la carga, nunca retroactivo). Negocio (el usuario es responsable del valor final del snapshot en edicion de historico).
- Estado final: ANALISIS FUNCIONAL CERRADO. Sin preguntas pendientes. Listo para pasar a etapa de diseno funcional.
- Entidades funcionales definitivas: UnidadBioquimica, Practica, PracticaDetalle (muchos a muchos), ProduccionMensual, ProduccionDetalle (precio_snapshot editable).

### 2026-06-13 sesion 5 - presupuestador — PRESUPUESTO CERRADO
- Etapa: Presupuesto
- Cambio: Presupuesto completo producido. 4 modulos: M1 ABM simple (1.5h/$34), M2 ABM intermedio (6.0h/$135), M3 ABM complejo cabecera/detalle (8.5h/$191), M4 Infra (1.5h/$34). Total M=17.5h, PERT=18.17h, horas finales=20.67h. USD base=$294, USD cliente=$394 (incluye IA $100 implicito). Mantenimiento anual Plan PRO USD 300/anio. Pasos 0-9 ejecutados. Sanity check OK sin correccion. Sin doble contingencia.
- Motivo: Arquitectura aprobada. Todas las etapas previas cerradas.
- Anclaje historico: M1 ref ABM Camiones/Categorias (1.5h), M2 ref ABM intermedios Lumitrack/Delicias (5.0h), M3 ref SG cabecera/detalle (9.6h), M4 ref SG infra (0.5h/migracion).
- Riesgos de presupuesto: todos en rango 0.85-1.15 salvo M2 (1.20, justificado con 5 drivers). M3 en limite inferior (0.885, sin workflow P4-A).
- Estado: PRESUPUESTO CERRADO. Listo para presentar al cliente y pasar a implementacion.


- Etapa: Arquitectura MVC
- Cambio: Arquitectura completa producida. Domain: 5 entidades + 1 enum (todos heredan SoftDestroyable). Application: 3 interfaces de servicio + 6 DTOs + modificacion de IRepository (RestoreAsync). Infrastructure: 3 servicios nuevos + modificacion de AppDbContext, Repository y DependencyInjection. Web: 3 controllers + 11 ViewModels + 10 Views + modificacion de _Layout. 1 migracion EF. Sin nuevos roles ni policies.
- Motivo: Diseno funcional aprobado. Se validaron todos los componentes reutilizables de BlankProject. Se resolviron los 5 riesgos arquitectonicos identificados (RA-01 a RA-05).
- Impacto en capas: Domain (solo adicion), Application (adicion + IRepository.RestoreAsync), Infrastructure (AppDbContext + Repository + DependencyInjection + 3 servicios nuevos + 1 migracion), Web (3 controllers + VMs + Views + sidebar).
- Decisiones clave: ProduccionDetalle con 2 FK nullable (PracticaId? + UnidadBioquimicaId?) en lugar de ItemId logico. IgnoreQueryFilters en PracticaService para sumatoria con componentes soft-deleted. Unicidad Mes+Anio enforced en Service (no DB). [Authorize] sin politica en todos los controllers nuevos.
- Estado: ARQUITECTURA CERRADA. Listo para generar presupuesto.


- Etapa: Diseno funcional
- Cambio: Diseno funcional completo producido. 10 wireframes textuales (WF-01 a WF-10), 11 ViewModels (VM-01 a VM-11), 11 reglas de negocio (RN-01 a RN-11), logica de distribucion de elementos estandarizada, 3 contratos de Services (IUnidadBioquimicaService, IPracticaService, IProduccionMensualService), maquina de estados (NO aplica), impacto por capa, plan funcional en 3 etapas (A: catalogos, B: motor produccion, C: historial y dashboard).
- Motivo: Analisis funcional aprobado con todas las preguntas resueltas (P1-P5).
- Impacto en capas: Presentacion (4 Controllers, 11 ViewModels, ~15 Views, 1 endpoint AJAX precio, sidebar 3 entradas). Negocio (3 interfaces + 3 servicios, todas las RN viven en Services). Datos (5 entidades nuevas, 1 enum, 1 migracion EF, campos NombreSnapshot y PrecioSnapshot en ProduccionDetalle).
- Riesgos: RF-03 pendiente para arquitecto (baja logica de unidad con composicion activa en practica).
- Estado: DISENO FUNCIONAL CERRADO. Listo para revision del arquitecto.



- Etapa: Discovery/Analisis — actualizacion con nuevo brief del cliente
- Cambio: Se confirmo terminologia de dominio (UNIDAD BIOQUIMICA, PRACTICA, PRECIO). Se actualizaron casos de uso, criterios de aceptacion, validaciones, riesgos y banderas tempranas. Se incorporo explicitamente el requerimiento de historial mensual persistente. Se reemplazaron preguntas genéricas por hipotesis contrastadas con ejemplos del dominio (Rutina, Libreta Sanitaria).
- Motivo: El cliente proporciono mas contexto sobre el modelo del sistema: terminos oficiales, ejemplos concretos de practicas y confirmacion del historial mensual.
- Impacto en capas: Presentacion (pantallas de carga, historial, catalogos), Negocio (regla precio practica < sumatoria, calculo mensual, snapshot de precios), Datos (entidades: UnidadBioquimica, Practica, PracticaDetalle, ProduccionMensual, ProduccionDetalle).
- Riesgos/supuestos: R1 doble conteo (pendiente P1), R2 historial de precios (pendiente P3), R3 editabilidad del periodo (pendiente P4).
- Preguntas pendientes: P1 (paquete vs componentes), P2 (unidad en multiples practicas), P3 (snapshot vs precio actual), P4 (mes editable vs cerrado).
