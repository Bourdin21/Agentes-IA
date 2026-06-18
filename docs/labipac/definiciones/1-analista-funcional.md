# Memoria - Analista funcional

## Proyecto: labipac
## Ultima actualizacion: 2026-06-13 (sesion 3 — P5-B confirmado — analisis CERRADO sin pendientes)

## Terminologia de dominio confirmada

| Termino | Definicion |
|---|---|
| UNIDAD BIOQUIMICA | Estudio medico individual con precio propio |
| PRACTICA | Conjunto de unidades bioquimicas agrupadas con precio propio distinto a la sumatoria |
| PRECIO | Valor monetario ($) asignado a una unidad bioquimica o practica |
| PRODUCCION MENSUAL | Cantidad de unidades bioquimicas y practicas realizadas en un mes |

Ejemplos de PRACTICAS: Rutina, Libreta Sanitaria.

## Definiciones vigentes

### Modulos/features analizados
- Acceso al sistema con usuario y contrasena.
- Catalogo de unidades bioquimicas (estudios individuales) con precio.
- Catalogo de practicas (conjuntos de estudios) con precio propio.
- Carga mensual de cantidades realizadas por unidad bioquimica y por practica.
- Calculo del monto estimado a cobrar en base a cantidades y precios configurados.
- Historial de calculos mensuales con detalle de cantidades, precios y totales.
- Consulta y comparacion de periodos anteriores.

### Reglas funcionales acordadas
- El sistema es web y de uso para un unico usuario.
- El acceso requiere autenticacion con usuario y contrasena.
- Cada unidad bioquimica tiene un precio monetario.
- Cada practica tiene un precio monetario propio.
- El precio de una practica debe ser menor que la sumatoria de las unidades bioquimicas que la componen.
- Una unidad bioquimica puede pertenecer a mas de una practica simultaneamente (P2 confirmado).
- En la produccion mensual el usuario puede cargar tanto practicas como unidades bioquimicas sueltas en el mismo mes (P1 confirmado).
- El calculo mensual suma todos los items cargados: suma de (cantidad x precio) de cada practica + suma de (cantidad x precio) de cada unidad bioquimica suelta.
- El precio que se guarda en cada linea del historial es el precio vigente al momento de cargar/calcular ese item — snapshot inmutable (P3 confirmado).
- Los periodos mensuales son siempre editables, sin cierre ni bloqueo (P4 confirmado).
- Se debe guardar el historial de cada calculo mensual para registros historicos y comparacion con periodos anteriores.

### Decisiones de diseno funcional confirmadas
| Referencia | Decision |
|---|---|
| P1-B | En produccion mensual coexisten practicas y unidades bioquimicas sueltas. El sistema no impide registrar ambas. |
| P2-B | Una unidad bioquimica puede pertenecer a multiples practicas. La composicion es muchos a muchos sin exclusividad. |
| P3-A | El precio guardado en cada linea de produccion es un snapshot del precio vigente al momento de la carga. Es inmutable retroactivamente. |
| P4-A | Los periodos mensuales no se cierran. Siempre son editables. No se requiere maquina de estados. |
| P5-B | Al agregar una linea nueva a un periodo historico, el sistema muestra el precio actual pre-completado en un campo editable con aviso visual. El usuario puede modificarlo manualmente antes de guardar. |

### Criterios de aceptacion vigentes
- El usuario solo accede al sistema con credenciales validas.
- Pueden configurarse unidades bioquimicas con nombre y precio.
- Pueden configurarse practicas con nombre, precio y composicion de unidades bioquimicas.
- El sistema bloquea una practica cuyo precio sea mayor o igual a la suma de sus componentes.
- El sistema muestra la sumatoria de componentes como referencia al configurar el precio de una practica.
- Una unidad bioquimica puede asociarse a multiples practicas sin restriccion.
- En la carga mensual pueden registrarse practicas y unidades bioquimicas sueltas en el mismo mes.
- Cada linea de produccion guarda el precio vigente al momento de su carga (snapshot).
- Al agregar una linea nueva a un periodo historico, el sistema muestra el precio actual pre-completado en un campo editable con indicacion visible (ej: "Precio vigente: $12.000 — podés modificarlo"). Las lineas ya guardadas no cambian su snapshot.
- El historial de cada mes conserva cantidades, precios snapshot y total calculado.
- El sistema permite consultar y comparar calculos de periodos anteriores.
- Cualquier mes puede editarse en cualquier momento sin restriccion de cierre.

### Supuestos y dependencias
- Se asume que el usuario es responsable de no registrar la misma unidad bioquimica dos veces en el mismo mes (una como parte de una practica y otra como item suelto) si no corresponde.
- Al agregar una linea a un mes historico, el usuario es responsable de ajustar el precio snapshot si el vigente no corresponde al periodo que esta editando.

### Exclusiones confirmadas
- No se definieron integraciones externas.
- No se pidio facturacion electronica.
- No se pidio gestion de pacientes, resultados clinicos ni turnos.
- No se pidio aplicacion movil nativa.
- No se requiere maquina de estados ni cierre de periodos.

## Historial de ajustes
- 2026-06-12: Se creo la memoria inicial del proyecto y se fijo el alcance base de calculo, catalogos y carga mensual.
- 2026-06-12: Se marco a .NET 10 en smarteasp como destino recomendado por coherencia con el stack y el tipo de aplicacion.
- 2026-06-13 sesion 1: Se confirmo la terminologia de dominio: UNIDAD BIOQUIMICA, PRACTICA, PRECIO. Se confirmaron ejemplos de practicas (Rutina, Libreta Sanitaria). Se confirmo el requerimiento de historial mensual con registro de precios y comparacion de periodos.
- 2026-06-13 sesion 2: Se cerraron P1-P4. P1-B: practicas y unidades bioquimicas sueltas coexisten en la produccion mensual. P2-B: unidad bioquimica compartida entre multiples practicas. P3-A: precio snapshot por linea de produccion, inmutable retroactivamente. P4-A: periodos siempre editables, sin cierre. Se elimino R1 como riesgo activo (es comportamiento esperado). Se elimino maquina de estados del alcance. Se identifico nueva pregunta P5 sobre snapshot en edicion de historico.
- 2026-06-13 sesion 3: Se cerro P5-B. Al agregar una linea nueva a un periodo historico, el sistema muestra el precio actual pre-completado en campo editable con aviso visual para que el usuario pueda corregirlo. ANALISIS FUNCIONAL CERRADO — sin preguntas pendientes.

## Alcance funcional resumido

### Incluido
1. Login con usuario y contraseña (usuario unico).
2. ABM de Unidades Bioquimicas con nombre y precio.
3. ABM de Practicas con nombre, precio propio y composicion (muchos a muchos con unidades bioquimicas).
4. Validacion: precio de practica < sumatoria de sus componentes.
5. Carga mensual de cantidades: practicas y/o unidades bioquimicas sueltas en el mismo mes.
6. Precio snapshot por linea de produccion: cada linea guarda el precio vigente al momento de su carga. Al editar un periodo historico, el precio aparece pre-completado y editable con aviso visual.
7. Calculo automatico del total estimado: suma de (cantidad x precio_snapshot) de todos los items del mes.
8. Historial de calculos mensuales con detalle de cantidades, precios snapshot y totales.
9. Consulta y comparacion de periodos anteriores.
10. Edicion de cualquier mes en cualquier momento sin restriccion.

### No incluido
1. Integracion con laboratorios, sistemas externos o APIs.
2. Emision de factura o comprobante fiscal.
3. Gestion de pacientes, historias clinicas o resultados de estudios.
4. App movil nativa.
5. Multiusuario con roles complejos.
6. Cierre/bloqueo de periodos mensuales.
7. Maquina de estados.

### Dependencias pendientes
- Ninguna. Todas las decisiones han sido confirmadas.

## Casos de uso principales

| # | Caso de uso | Actor | Resumen |
|---|---|---|---|
| CU-01 | Iniciar sesion | Usuario unico | Acceso al sistema con credenciales validas. |
| CU-02 | Administrar Unidades Bioquimicas | Usuario unico | ABM de unidades bioquimicas con nombre y precio. |
| CU-03 | Administrar Practicas | Usuario unico | ABM de practicas con composicion (muchos a muchos) y precio propio. |
| CU-04 | Cargar produccion mensual | Usuario unico | Registrar cantidades de practicas y/o unidades sueltas por mes, con precio snapshot editable por linea. Al agregar linea a mes historico, se muestra precio actual con aviso y campo editable. |
| CU-05 | Calcular estimacion de cobro | Sistema | Sumar (cantidad x precio_snapshot) de todos los items del mes y mostrar total. |
| CU-06 | Consultar historial mensual | Usuario unico | Ver detalle y total calculado de periodos anteriores para comparar. |

## Criterios de aceptacion verificables por caso de uso

### CU-01
- Con credenciales validas, el usuario ingresa al sistema.
- Con credenciales invalidas, el sistema rechaza el acceso con mensaje de error.

### CU-02
- Se pueden crear unidades bioquimicas con nombre y precio >= 0.
- Se puede editar nombre y precio en cualquier momento.
- El sistema impide precio negativo.
- La unidad queda disponible para asociarla a practicas y para la carga mensual.
- La baja es logica: no aparece en nuevas cargas pero el historial la conserva con su precio snapshot.
- Una unidad bioquimica puede asociarse a multiples practicas sin restriccion.

### CU-03
- Se pueden crear practicas con nombre, precio y al menos una unidad bioquimica componente.
- Una misma unidad bioquimica puede pertenecer a multiples practicas (P2-B confirmado).
- El sistema muestra la sumatoria de componentes como referencia al configurar el precio.
- El sistema impide guardar una practica cuyo precio sea >= a la sumatoria de sus componentes.
- La composicion de la practica queda visible para su validacion.

### CU-04
- El usuario selecciona un mes/anio y carga cantidades (enteras, >= 0) por item.
- Puede cargar practicas y/o unidades bioquimicas sueltas en el mismo mes sin restriccion (P1-B confirmado).
- Cada linea de produccion captura el precio vigente como snapshot editable al momento de guardar (P3-A confirmado).
- Al agregar una linea nueva a un periodo historico ya existente, el sistema muestra el precio actual del catalogo pre-completado en un campo editable, con aviso visual del tipo "Precio vigente: $X.XXX — podés modificarlo". El usuario decide si ajusta el valor antes de guardar (P5-B confirmado).
- Las lineas ya guardadas en el historial no modifican su precio snapshot al editar otras lineas del mismo periodo.
- El periodo no se cierra; puede editarse en cualquier momento (P4-A confirmado).
- No se permiten cantidades negativas.

### CU-05
- El total estimado = suma de (cantidad x precio_snapshot) de cada linea del mes.
- El sistema muestra el detalle linea por linea (nombre del item, tipo, cantidad, precio snapshot, subtotal).
- Si no hay cantidades cargadas, el total del mes es cero.
- El calculo se actualiza automaticamente al agregar, editar o eliminar una linea.

### CU-06
- El usuario puede seleccionar cualquier periodo historico y ver el detalle completo.
- El historial muestra las cantidades y los precios snapshot de cada linea (inmutables desde su carga).
- Se puede comparar periodos anteriores en tabla paginada.

## Permisos, estados y validaciones identificados

### Permisos
- Un unico usuario autenticado con capacidad de administracion total.

### Estados
| Entidad | Estados |
|---|---|
| Unidad Bioquimica | Activa / Inactiva (baja logica) |
| Practica | Activa / Inactiva (baja logica) |
| Periodo mensual | Sin estados — siempre editable (P4-A confirmado) |

### Validaciones
| Campo | Regla |
|---|---|
| Precio unidad bioquimica | Obligatorio, >= 0 |
| Precio practica | Obligatorio, >= 0, estrictamente < sumatoria de sus componentes |
| Composicion de practica | Al menos 1 unidad bioquimica asociada |
| Cantidad produccion mensual | Entero, >= 0 |
| Periodo de carga | Mes/anio validos; no duplicar el mismo item en el mismo mes |

## Riesgos y supuestos

### Riesgos
| # | Riesgo | Impacto | Estado |
|---|---|---|---|
| R1 | Coexistencia de practicas y componentes en la misma carga | El usuario es responsable de no duplicar intencionalmente el mismo trabajo | Aceptado por diseno (P1-B) |
| R2 | Al agregar una linea nueva a un mes historico, el precio pre-completado es el actual — el usuario debe ajustarlo manualmente si no corresponde | Bajo — el sistema avisa y el campo es editable antes de guardar | Mitigado por diseno (P5-B) |
| R3 | Sin cierre de periodo, el usuario puede modificar cualquier mes pasado sin trazabilidad visible | Bajo — el usuario es unico y consciente | Aceptado por diseno (P4-A) |

### Supuestos
| # | Supuesto |
|---|---|
| S1 | El sistema sera de uso local para un solo usuario autenticado. |
| S2 | El calculo buscado es una estimacion de cobro, no una facturacion fiscal. |
| S3 | El stack destino es ASP.NET Core MVC sobre .NET 10 con EF Core y MySQL (BlankProject base). |
| S4 | El usuario entiende que registrar la misma unidad bioquimica como parte de una practica Y como suelta en el mismo mes es valido si corresponde a trabajos distintos. |

## Banderas tempranas

| Bandera | Valor | Nota |
|---|---|---|
| Requiere migracion EF | SI | Entidades: UnidadBioquimica, Practica, PracticaDetalle (muchos a muchos), ProduccionMensual, ProduccionDetalle (con campo precio_snapshot) |
| Integracion externa | NO | Sin integraciones externas. |
| Maquina de estados | NO | Descartada: P4-A confirma que no hay cierre ni bloqueo de periodos. |

## Preguntas para aclarar requerimientos

### TODAS RESPONDIDAS — ANALISIS CERRADO

| Ref | Pregunta | Respuesta confirmada |
|---|---|---|
| P1 | Como se registra una practica en la produccion mensual? | B — practicas y unidades sueltas coexisten en la carga mensual |
| P2 | Una unidad bioquimica puede pertenecer a mas de una practica? | B — si, relacion muchos a muchos sin exclusividad |
| P3 | El historial conserva el precio historico o el actual? | A — snapshot por linea, inmutable retroactivamente |
| P4 | El mes queda editable o se cierra? | A — siempre editable, sin cierre |
| P5 | Al agregar linea nueva a mes historico, el precio es editable o fijo? | B — precio actual pre-completado en campo editable con aviso visual; el usuario puede ajustarlo antes de guardar |
