# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-07-08 - presupuestador — CIERRE DE CALIBRACION SESION 3 (M7+M8+M9 + 3 fixes)
- Etapa: Cierre de calibracion estimado vs real
- Cambio: Cliente confirmo verificacion funcional OK de los 3 fixes post-QA (Details con Unidad, combo de composicion corregido, columna Unidad en Detalle) y reporto horas reales: **2.0h totales** para todo el sprint (M7+M8+M9 + los 3 fixes). Estimado M base 11.5h (desvio -82.6%), con contingencia 13.69h (desvio -85.4%). Ratio PERT-contingencia/real = 6.84x y ratio formula-vigente/real = 2.76x — segundo lugar del dataset historico, detras de vinosefue (7.07x/2.86x).
- Motivo: Cierre formal del sprint segun secuencia obligatoria del estudio (Cierre de calibracion es la ultima etapa).
- Accion de recalibracion: se agrego una regla nueva a `27-presupuesto-parametros.instructions.md` ("segunda/tercera ronda sobre el mismo modulo") — cuando un proyecto ya tuvo rondas previas de mejoras que dejaron patrones de UI/AJAX/servicios reutilizables, aplicar el piso del rango de "Modificacion sobre modulo existente" en vez de la mediana, incluso para lo que parezca una pantalla nueva. Se registro el cierre en el dataset cross-proyecto (tabla de ratios PERT/real y formula/real).
- Estado: PROYECTO labipac — SESION 3 CERRADA INTEGRALMENTE (Discovery -> Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> QA -> Documentacion -> Cierre de calibracion). Sin pendientes tecnicos abiertos salvo aplicar la migracion `AddPracticaUnidadYPrecioPorUnidad` en Produccion en el proximo deploy.

### 2026-07-08 - qa-mvc — pruebas manuales de UI ejecutadas por el cliente — 3 hallazgos
- Etapa: Pruebas funcionales (manual, ejecutada por el cliente sobre las 8 pruebas de UI listadas en el cierre de QA anterior)
- Hallazgos reportados: (1) `Practicas/Details` no muestra la cantidad de `Unidad` configurada para el Perfil; (2) `Practicas/Edit` no autocompleta/preselecciona el combo de composicion con las Practicas (UnidadBioquimica) ya asociadas al Perfil; (3) `ProduccionMensual/Detalle` no muestra el valor de `Unidad` en las lineas de tipo Perfil.
- Clasificacion: completions/fixes de bajo esfuerzo dentro del alcance ya aprobado (M7/M8), no nuevo alcance de negocio — se resuelven directo sin pasar por un nuevo ciclo de Presupuesto.
- Se delega a `agentes-ia-implementador` para investigar causa raiz (especialmente el punto 2, que por lectura de codigo estatico parecia correctamente cableado) y aplicar el fix.
- Estado: CORREGIDO (ver entrada de implementador-dotnet SESION 4 debajo, 2026-07-08, para el detalle de causa raiz y fix de cada punto).

### 2026-07-08 - documentador — resumen de sprint M7+M8+M9
- Etapa: Documentacion
- Cambio: Se redacto y entrego `docs/labipac/resumen-sprint-2026-07-08.md` con formato obligatorio de cliente, reflejando solo lo implementado y validado por QA (sin defectos bloqueantes): Precio por Unidad (M7), carga masiva + alta rapida (M8), fix PDF (M9). Se documenta como pendiente (no solicitado en este sprint) actualizar `manual-practicas.md` con el nuevo modelo de precios.
- Motivo: QA cerrado sin defectos bloqueantes (ver entrada QA debajo), habilita etapa de Documentacion.
- Estado: DOCUMENTACION ENTREGADA. Pendiente: que el cliente ejecute las 8 pruebas manuales de UI listadas por QA y reporte horas reales para el cierre de calibracion.

### 2026-07-08 - qa-mvc — SESION 2: QA funcional M7+M8+M9 — SIN BLOQUEANTES
- Etapa: Pruebas funcionales
- Cambio: QA del alcance implementado en sesion 3 del implementador (M7 Unidad/PrecioPorUnidad + simplificacion F-001, M8 Carga masiva + alta rapida atomica, M9 fix PDF). Verificacion por lectura de codigo real (no solo memoria documental) de `PreciosController.cs`, `PracticasController.cs`, `PracticaService.cs`, `ProduccionMensualService.cs`, `ProduccionMensualController.cs`, ViewModels y vistas afectadas + migracion EF. Build real (`dotnet build LabIPAC.Web`) OK, 0 errores. Consulta directa a `labipac_dev` via `mysqlsh` para verificar el backfill de `Unidad` (foco de riesgo pedido): confirmado sin precios en $0 (Perfil "Rutina" Unidad=17, PrecioActual=$15000, consistente con ROUND(15000/892.03)); `PreciosPorUnidad` con seed correcto; `__EFMigrationsHistory` confirma la migracion aplicada.
- Cobertura de criterios de aceptacion: HU-01 a HU-05 (RN-12 a RN-21) todas PASS por revision de codigo; algunas requieren confirmacion visual/manual del usuario (marcadas explicitamente, sin automatizar UI). RA-06 (backfill) confirmado PASS con evidencia de base real.
- Hallazgos no bloqueantes: QA-F1 (minor, UX) — validacion de duplicados (RN-13) en carga masiva es solo server-side, el mensaje de error no señala la fila puntual; atomicidad preservada, no es bug funcional. QA-F2 (informativo) — `ObtenerPrecioPorUnidadVigenteAsync` sin `OrderBy` explicito, seguro mientras se respete el patron de fila unica. QA-F3 (informativo) — patron heredado de F-002 en autorizacion AJAX de acciones `RequireAdministracion`, sin regresion introducida.
- Catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`): ejecutado, mayoria de items N/A por falta de modulo equivalente en labipac (stock/variantes, compras, ventas, camaras, notificaciones, autorizaciones con maquina de estados). Patrones aplicables (RowVersion MySQL, EF6 dynamic OrderBy+Include+Skip/Take, lista con fila fantasma en binder tipo GAN-001, `script+partial` tipo GAN-003, delete fuera de `<form>` tipo KOI-001) verificados sin reproducirse en el codigo nuevo ni en el existente tocado.
- Sin bugs funcionales reproducidos: no se activo el flujo de auto-fix obligatorio (no habia nada que parchear).
- Motivo: cierre del gate de QA antes de habilitar Documentacion al cliente, segun secuencia obligatoria del estudio.
- Riesgos de liberacion: pendiente aplicar la migracion `AddPracticaUnidadYPrecioPorUnidad` a Produccion; pendiente revision manual del cliente sobre los valores de `Unidad` backfilleados (tarea ya identificada por el implementador, no tecnica); pendiente ejecucion manual de las pruebas de UI listadas (carga masiva end-to-end, modales de alta rapida, card Precio por Unidad, PDF con montos largos) por tratarse de flujos de navegador que QA no automatiza.
- Estado: QA CERRADO SIN BLOQUEANTES. Checklist de salida para merge: PASS (con pendientes operativos de deploy/manual arriba listados, no de codigo).

### 2026-07-08 - implementador-dotnet — SESION 3: implementacion M7+M8+M9 completa
- Etapa: Implementacion
- Cambio: Se implemento todo el alcance aprobado en una sola pasada (sin dividir en Etapa 1/Etapa 2 tecnicas, solo a efectos de facturacion segun pedido del cliente). M7: campo `Practica.Unidad`, nueva entidad `PrecioPorUnidad` (fila unica), `PrecioActual` pasa a ser 100% calculado (`Unidad x PrecioPorUnidad vigente`), RN-01 derogada, RN-02 relajada globalmente, card "Precio por Unidad" en `Practicas/Index` (reutiliza patron visual/AJAX de la card IVA de F-002), `PreciosController` (F-001) simplificado eliminando el cascade UB->Perfil. M8: pantalla nueva `ProduccionMensual/CargaMasiva` (filas dinamicas, un submit atomico via `AgregarLineasAsync`), 2 modales de alta rapida (Perfil y Practica) via AJAX reutilizando `CreateAsync` de ambos servicios existentes. M9: fix de ancho de columnas en `ReportePdf` (Precio unit. 55->75, Tipo 65->60).
- Escaneo de reutilizacion: se escaneo `docs/*/definiciones/5-implementador.md` de otros proyectos buscando el patron "fila unica"/configuracion global — sin coincidencias cross-proyecto. Se reutilizo el patron intra-proyecto ya existente (card IVA del periodo, F-002) para la nueva card Precio por Unidad.
- Motivo: Presupuesto SESION 3 aprobado por el cliente, quien pidio ejecutar todo el alcance junto en una sola entrega tecnica.
- Impacto en capas: Domain (+1 entidad `PrecioPorUnidad`, `Practica` +campo `Unidad`), Application (`IPracticaService` +3 metodos, `IProduccionMensualService` +`AgregarLineasAsync`, 2 DTOs ajustados), Infrastructure (`AppDbContext` +DbSet, `PracticaService` y `ProduccionMensualService` extendidos, 1 migracion EF con seed y backfill), Web (`PracticasController` extendido, `PreciosController` simplificado -40% de codigo aprox., `ProduccionMensualController` +3 acciones, 5 ViewModels nuevos/modificados, 1 vista nueva + 2 partials, 5 vistas modificadas).
- Migracion EF: `AddPracticaUnidadYPrecioPorUnidad` — generada, ajustada manualmente con seed (`Valor=892.03`) y backfill SQL (`UPDATE Practicas SET Unidad = GREATEST(1, CAST(ROUND(PrecioActual / 892.03) AS SIGNED)) WHERE DeletedAt IS NULL`), y **aplicada exitosamente** a la base de desarrollo local `labipac_dev`. Verificado post-aplicacion: seed correcto, backfill correcto sobre datos reales. Pendiente aplicar a Produccion en el proximo deploy.
- Build: OK, 0 errores (solo warnings preexistentes de NuGet — MailKit/MimeKit — y 1 warning CS0114 preexistente en HomeController, ninguno introducido por esta sesion).
- Riesgos/supuestos: RA-06 (backfill de Unidad, mitigado y verificado). RA-07 (Perfiles "congelados" hasta primer recalculo, comportamiento esperado). Pendiente QA funcional de los 3 flujos y revision manual del cliente sobre los valores de Unidad backfilleados.
- Estado: IMPLEMENTACION CERRADA (build OK, migracion aplicada en desarrollo). Pendiente: QA funcional, aplicar migracion en Produccion, documento de cliente.

### 2026-07-08 - analista-funcional — SESION 4: 3 mejoras funcionales — ANALISIS CERRADO
- Etapa: Discovery/Analisis
- Cambio: Se relevaron 3 pedidos nuevos: (1) carga masiva + creacion inline de Perfiles/Practicas desde Produccion Mensual, resuelto con pantalla nueva dedicada + filas repetibles (P6, P7); (2) nueva propiedad `Unidad` en Perfiles (entidad `Practica`) + configuracion global `PrecioPorUnidad` ($892.03 ref.) con formula `PrecioActual = Unidad x PrecioPorUnidad` calculada, ubicada en el listado de Perfiles (P8, P9); (3) fix de ancho de columna "Precio unit." en el PDF de Produccion Mensual (causa raiz: `ConstantColumn(55)` en `ProduccionMensualController.ReportePdf`).
- Hallazgo critico (P10): el nuevo modelo de precio de Perfil entra en conflicto con F-001 (Aumento masivo de precios, ya implementado en produccion — `Precios/AumentoMasivo`) que hoy permite editar el precio de Perfil a mano y cascada UB→Perfil por composicion. Se confirmo con el cliente: se reemplaza para Perfiles (precio 100% derivado de Unidad x PrecioPorUnidad, se retira edicion manual y cascade a Perfiles). F-001 sigue vigente sin cambios para Practicas (UnidadBioquimica) sueltas.
- Motivo: pedido directo del cliente para ampliar Produccion Mensual y corregir un defecto visual de exportacion.
- Impacto en capas: Domain (`Practica` +campo Unidad, posible nueva entidad/config `PrecioPorUnidad`), Application/Infrastructure (recalculo de precio derivado, nuevo service de configuracion), Web (pantalla nueva de carga masiva, ajuste PreciosController/AumentoMasivo.cshtml para excluir edicion de Perfiles, fix ReportePdf).
- Riesgos/supuestos: se deroga RN-01 (precio Perfil < sumatoria componentes) para Perfiles. Pendiente definir en Diseno/Arquitectura si `PrecioActual` de Perfil se persiste desnormalizado o se calcula al vuelo.
- Nota: se detecto una copia local de documentacion en `C:\Sistemas\labipac\docs\labipac\` (F-001/F-002, sesiones de implementador) no replicada en la ruta canonica de Agentes-IA. Se tomo como fuente valida por estar verificada contra el codigo, pero se recomienda migrarla a la ruta canonica.
- Estado: ANALISIS CERRADO. Listo para Diseno funcional.

### 2026-07-08 - disenador-funcional — SESION 2: diseno de 3 mejoras — DISENO CERRADO
- Etapa: Diseno funcional
- Cambio: Diseno completo de las 3 mejoras. WF-11 (pantalla nueva Carga Masiva con filas repetibles + alta rapida de Perfiles/Practicas via modales AJAX). Ajustes a Perfiles Index/Create/Edit (card Precio por Unidad, columna Unidad, se quita precio editable) y a F-001 (se quita tab Perfiles). Fix de ancho de columna en PDF documentado sin cambio de pantalla. 5 ViewModels nuevos (VM-12 a VM-16) + 2 modificados (VM-03, VM-04). 10 reglas de negocio nuevas (RN-12 a RN-21), incluye derogacion formal de RN-01 para Perfiles. Plan funcional en 3 etapas (A: Unidad/Precio por Unidad — base; B: Carga masiva + alta rapida — depende de A; C: fix PDF — independiente). 5 historias de usuario con criterios de aceptacion (HU-01 a HU-05).
- Motivo: Analisis funcional sesion 4 aprobado (P6-P10).
- Impacto en capas: Presentacion (1 vista nueva + 3 acciones de controller + ajustes en 4 vistas existentes), Negocio (nuevo contrato IPrecioPorUnidadService, extension de IProduccionMensualService e IPracticaService), Datos (campo Practica.Unidad + nueva entidad de configuracion PrecioPorUnidad, migracion EF pendiente de definir formato exacto en Arquitectura).
- Riesgos: DD-01 (Perfil por alta rapida puede quedar sin composicion), DD-02 (recalculo batch transaccional al cambiar Precio por Unidad), DD-03 (reutiliza aviso de periodo historico existente, sin caso nuevo).
- Estado: DISENO FUNCIONAL CERRADO. Listo para revision del arquitecto.

### 2026-07-08 - arquitecto-mvc — SESION 2: arquitectura de 3 mejoras — ARQUITECTURA CERRADA
- Etapa: Arquitectura MVC
- Cambio: Arquitectura completa de las 3 mejoras. 1 entidad nueva `PrecioPorUnidad` (fila unica, patron analogo a unicidad Mes+Anio de ProduccionMensual), 1 entidad modificada `Practica` (+Unidad int). `IPracticaService` extendido con calculo de precio derivado y gestion de PrecioPorUnidad (sin crear una interfaz nueva, para evitar dependencia circular entre servicios). `IProduccionMensualService` +`AgregarLineasAsync` para guardado atomico de carga masiva. `PreciosController` (F-001) simplificado: se elimina toda la logica de cascade UB→Perfil (queda obsoleta porque el precio de Perfil ya no depende de su composicion). 1 migracion EF (`AddPracticaUnidadYPrecioPorUnidad`) que incluye backfill de datos obligatorio para no dejar los Perfiles existentes en precio $0 (RA-06, riesgo critico identificado y mitigado con formula de aproximacion).
- Decision de simplificacion propuesta: relajar RN-02 (composicion minima) globalmente en vez de solo para alta rapida, para evitar logica condicional — pendiente de confirmar con el cliente en Presupuesto.
- Motivo: Diseno funcional sesion 2 aprobado.
- Impacto en capas: Domain (+1 entidad, +1 campo), Application (2 interfaces extendidas, nuevos DTOs), Infrastructure (AppDbContext +DbSet, 2 Services modificados, 1 migracion con data backfill), Web (2 controllers modificados +3 acciones nuevas, 1 controller simplificado con reduccion de codigo, 2 ViewModels modificados + 4 nuevos, 1 vista nueva + 2 partials, 4 vistas modificadas).
- Riesgos: RA-06 (critico, backfill de Unidad en migracion), RA-07 (Perfiles "congelados" hasta primer recalculo, comportamiento esperado), RA-08 (recalculo batch O(n), sin impacto a volumen actual), RA-09 (deuda tecnica preexistente en PreciosController, no corregida en este alcance).
- Estado: ARQUITECTURA CERRADA. Pendiente confirmar con cliente: relajacion global de RN-02 y criterio de backfill de Unidad (RA-06). Listo para generar presupuesto.

### 2026-07-08 - presupuestador — SESION 3: presupuesto de 3 mejoras — PRESUPUESTO CERRADO
- Etapa: Presupuesto
- Cambio: Presupuesto completo de 3 modulos (M7 Unidad y Precio por Unidad 4.5h/$75.60, M8 Carga masiva + alta rapida 6.5h/$109.20, M9 Fix columna PDF 0.5h/$8.40). Total M=11.5h, PERT=11.93h, horas finales con contingencia=13.69h. USD desarrollo=$193.20, Tokens IA=$19.32, USD cliente=$212.52. Division: Etapa 1 = M7+M9 (USD 84.00), Etapa 2 = M8 (USD 109.20). Mantenimiento anual sin cambio (Plan PRO, USD 300/año). Pasos 0-9 del metodo PERT ejecutados; ratios M/mediana por debajo de 0.85 justificados con reutilizacion real confirmada (patron IVA reutilizado para el panel de Precio por Unidad, AJAX GetPrecioItem y CreateAsync reutilizados en carga masiva, PreciosController pierde codigo en vez de ganar). Documento comercial generado en `docs/labipac/presupuesto-cliente.md` con formato obligatorio (31-formato-documento-cliente).
- Anclaje historico: primario la propia memoria de labipac (sesion anterior 26.0h M -> 12.0h real, ratio 2.17x); secundario Ganaderia y vinosefue (evidencia de sobreestimacion sistematica en iteraciones evolutivas con alta reutilizacion).
- Motivo: Arquitectura aprobada, todas las etapas previas cerradas.
- Riesgos de presupuesto: M7 y M8 riesgo Medio (15%), M9 riesgo Bajo (8%). Sin doble contingencia.
- Estado: PRESUPUESTO CERRADO. Pendiente de aprobacion del cliente antes de iniciar Implementacion.

### 2026-07-08 - presupuestador — PRESUPUESTO APROBADO POR EL CLIENTE
- Etapa: Presupuesto -> gate cliente
- Cambio: Cliente aprueba el presupuesto tal cual (USD 212.52, M7+M8+M9). Pide ejecutar todo en una sola etapa de implementacion (no dividir la entrega en Etapa 1 / Etapa 2 como estaba planteado para facturacion) — se implementan los 3 modulos juntos en el mismo sprint. La division Etapa 1/Etapa 2 del presupuesto se mantiene solo a efectos de facturacion/orden logico documentado, no como entregas separadas en el tiempo.
- Motivo: Decision del cliente de simplificar la entrega.
- Estado: GATE ABIERTO. Se delega Implementacion al subagent `agentes-ia-implementador` con el alcance completo de M7+M8+M9.

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

### 2026-07-08 - implementador-dotnet — SESION 4: fix de 3 hallazgos de UI (pruebas manuales del cliente) — CORREGIDO
- Etapa: Implementacion (completion/fix de bajo esfuerzo dentro del alcance ya aprobado, sin nuevo ciclo de Presupuesto)
- Cambio: Hallazgo 1 — `PracticaDetailsViewModel` no tenia `Unidad`; se agrego la propiedad, el mapeo en `PracticasController.Details` y la fila en `Views/Practicas/Details.cshtml`. Hallazgo 2 — **bug real confirmado por reproduccion en vivo** (no falso positivo): `UnidadesDisponibles` en `PracticasController.Edit` se armaba solo con `GetActivasAsync()`, que excluye `UnidadBioquimica` soft-deleted aunque tengan `Activo=true` (query filter global de soft-delete); las 2 unidades asociadas al Perfil de prueba real ("Rutina") estaban en ese estado, por lo que no se generaba ningun `<option>` para ellas y el combo no podia preseleccionarlas — ademas, al guardar sin tocar el combo, esas asociaciones se perdian silenciosamente del Perfil (bug de perdida de datos, no solo visual). Se agrego el metodo `BuildUnidadesDisponiblesAsync` que incluye tambien las unidades ya asociadas aunque esten inactivas/eliminadas, y se corrigio la deteccion de `ComponentesInactivos` para contemplar soft-delete ademas de `Activo=false`. Hallazgo 3 — `ProduccionMensual/Detalle` no mostraba `Unidad` del Perfil; se resolvio con lookup en vivo (sin snapshot ni migracion EF): se agrego `.ThenInclude(d => d.Practica)` en `ProduccionMensualService.GetByIdAsync`, campo `UnidadPerfil` en `ProduccionDetalleRowViewModel`, mapeo en el controller y columna nueva en la vista.
- Metodo de verificacion: se corrio la app localmente (`dotnet run` contra `labipac_dev`), se autentico via `curl` con cookie de Identity, y se comparo el HTML servido antes/despues de cada fix (no solo lectura estatica de codigo) — esto fue decisivo para el Hallazgo 2, cuya causa raiz estaba en la interseccion entre el query filter global de soft-delete y el filtro `Activo` de `GetActivasAsync()`, no visible solo leyendo la vista y el controller.
- Motivo: pruebas manuales de UI ejecutadas por el cliente tras el sprint M7+M8+M9 (ver entrada QA arriba, ahora CORREGIDO).
- Impacto en capas: Web (`PracticasController`, `ProduccionMensualController`, `PracticaViewModels.cs`, `ProduccionMensualViewModels.cs`, `Views/Practicas/Details.cshtml`, `Views/ProduccionMensual/Detalle.cshtml`), Infrastructure (`ProduccionMensualService.GetByIdAsync`). Sin migraciones EF.
- Build: OK, 0 errores (mismos warnings preexistentes de NuGet y CS0114, ninguno introducido).
- Riesgos: el bug de perdida de datos del Hallazgo 2 pudo haber afectado Perfiles en Produccion editados/guardados entre el deploy de la Sesion 3 y este fix, si su composicion incluye `UnidadBioquimica` soft-deleted — recomendado verificar en Produccion tras aplicar el fix.
- Estado: IMPLEMENTACION CERRADA (build OK, verificado en vivo). Pendiente: QA funcional de los 3 fixes y confirmacion del cliente.
