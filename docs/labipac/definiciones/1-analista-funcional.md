# Memoria - Analista funcional

## Proyecto: labipac
## Ultima actualizacion: 2026-07-23 (sesion 5 — Produccion Mensual por Centro de Salud (Privado/Mutual) — analisis CERRADO)

## Sesion 5 (2026-07-23) — Produccion Mensual por Centro de Salud (Privado/Mutual)

### Resumen del problema
Hoy `ProduccionMensual` es un unico periodo global por Mes+Anio, sin ninguna nocion de a que centro/pagador corresponde. El cliente pidio poder cargar Produccion Mensual separada por centro de salud privado o por mutual (obra social).

### Definicion escogida (P11-P14, confirmadas por el cliente via preguntas dirigidas)
- **P11 (granularidad):** CONFIRMADO — un periodo por cliente. `ProduccionMensual` pasa a tener `CentroSaludId` (FK nullable). Se permiten varios periodos para el mismo Mes+Anio, uno por cada centro/mutual, mas un periodo "global" sin centro.
- **P12 (catalogo):** CONFIRMADO — entidad nueva unificada `CentroSalud` (Nombre, Tipo enum `Privado`/`Mutual`, Activo), **totalmente independiente** del catalogo `Mutual` ya existente (sincronizado desde FABA para integracion de afiliados/analitos). Se acepta convivencia de nombres duplicados entre ambos catalogos (ej. "IOMA" en `Mutual` y en `CentroSalud`) sin vinculo entre ellos — el cliente prefirio simplicidad sobre evitar duplicacion.
- **P13 (obligatoriedad):** CONFIRMADO — el campo sigue siendo opcional para periodos nuevos (no solo para el historico). El usuario puede seguir creando periodos sin centro asignado ("global") de aca en mas.
- **P14 (nombre en UI):** CONFIRMADO — el concepto se llama "Centro de Salud" en toda la interfaz (menu, catalogo, selector). La entidad Domain se llama `CentroSalud` (sin inversion de terminologia, a diferencia de Practica/UnidadBioquimica).

### Impacto en alcance funcional vigente
- RN-11 se actualiza: unicidad ya no es solo Mes+Anio, pasa a ser **Mes+Anio+CentroSaludId** (tratando NULL como un valor propio: solo puede existir un periodo "global" sin centro por Mes+Anio, ademas de un periodo por cada CentroSalud distinto).
- Nuevo caso de uso: CU-09 Administrar Centros de Salud (ABM simple, mismo patron que Unidades Bioquimicas).
- CU-04 (Cargar produccion mensual) se extiende: al crear un periodo, selector opcional de Centro de Salud.
- CU-06 (Consultar historial) se extiende: filtro y columna por Centro de Salud en el listado.
- Reporte PDF de Produccion Mensual: si el periodo tiene centro asignado, se muestra su nombre en el encabezado.

### Riesgos y supuestos
- R-CS1: duplicacion semantica entre `Mutual` (FABA) y `CentroSalud` tipo Mutual — aceptado explicitamente por el cliente (P12), sin vinculo entre ambos catalogos.
- R-CS2: la unicidad Mes+Anio+CentroSaludId (con NULL como valor propio) no es expresable como constraint parcial en MySQL — se enforcea en Service, mismo patron ya usado para la unicidad original de Mes+Anio (RA-03 de la arquitectura original).
- S-CS1: no se requiere migrar ni asignar retroactivamente los periodos historicos existentes — quedan sin centro (P13/respuesta de migracion).

### Preguntas resueltas en sesion 5
| Ref | Pregunta | Respuesta confirmada |
|---|---|---|
| P11 | Granularidad: un periodo por cliente o clasificacion por linea | Un periodo por cliente (CentroSaludId en ProduccionMensual) |
| P12 | Catalogo a usar | Entidad nueva unificada `CentroSalud` (Privado/Mutual), independiente de `Mutual` (FABA) |
| P13 | Obligatoriedad del campo en periodos nuevos | Opcional, tambien para periodos nuevos |
| P14 | Nombre en UI | "Centro de Salud" |

### Estado
ANALISIS FUNCIONAL DE SESION 5 CERRADO. Sin preguntas pendientes. Listo para Diseno funcional.

## NOTA — divergencia documental detectada (2026-07-08), resuelta (2026-07-23)
El repo `C:\Sistemas\labipac\docs\labipac\` contiene una copia local de las definiciones (incluye `analisis-funcional-F001-F002.md`) generada por una sesion previa que no escribio en la ruta canonica `C:/Sistemas/Agentes-IA/docs/labipac/`. Esa copia documenta F-001 (Aumento masivo de precios, `Precios/AumentoMasivo`) y F-002 (IVA en resumen mensual) — **ambas ya implementadas y en produccion** segun `docs/labipac/definiciones/5-implementador.md` (copia local, sesion 2026-06-25).

**Formula exacta de F-001 (RN-F001-01, CASCADE PRECIO), migrada aca el 2026-07-23 tras spot-check contra la copia local — coincide sin discrepancias:**

Al aumentar una Unidad Bioquimica (UB), todas las Practicas/Perfiles que la contengan aumentan automaticamente en el mismo monto en pesos (delta $), ponderado por la cantidad de esa UB dentro de la Practica:

```
delta_ub       = round(PrecioActual_UB × pct / 100, 2)
UB.PrecioActual += delta_ub

Para cada PracticaDetalle donde UnidadBioquimicaId == UB.Id:
    Practica.PrecioActual += delta_ub × PracticaDetalle.Cantidad
```

Si multiples UBs de la misma seleccion forman parte de la misma Practica, esta acumula la suma de los deltas de todas ellas:

```
Practica.PrecioActual += Σ (delta_ub_i × Cantidad_i)   ∀ UB_i seleccionada en esa Practica
```

Nota vigente (ver P10 mas abajo, sesion 2026-07-08): este cascade **se deroga para Perfiles** bajo el nuevo modelo (precio de Perfil pasa a ser 100% derivado de `Unidad × PrecioPorUnidad`), pero **sigue vigente sin cambios para Practicas (UnidadBioquimica) sueltas**.

Se recomienda de todos modos migrar la copia local completa (`analisis-funcional-F001-F002.md`, `5-implementador.md`) a la ruta canonica en una proxima sesion para no depender de dos ubicaciones.

## Sesion 4 (2026-07-08) — 3 mejoras funcionales sobre labipac

### Terminologia vigente en UI (IMPORTANTE — invertida respecto al nombre de entidad)
- Entidad `Practica` (Domain) = compuesta por N `UnidadBioquimica` via `PracticaDetalle` (M:N) → se muestra en toda la UI como **"Perfil"**.
- Entidad `UnidadBioquimica` (Domain) = estudio individual → se muestra en toda la UI como **"Práctica"**.
- Toda referencia a "Perfil" en esta sesion = entidad `Practica`. Toda referencia a "Práctica" (en el sentido nuevo del cliente) = entidad `UnidadBioquimica`.

### Pedido 1 — Carga masiva + creacion inline de Perfiles/Practicas desde Produccion Mensual
- Hoy `ProduccionMensual/Detalle` tiene boton "Agregar ítem" que abre un modal con una sola linea por vez, solo seleccion de existentes (sin crear nuevos).
- **P6 (pantalla vs partial):** CONFIRMADO — pantalla nueva dedicada (no partial). Justificacion: centraliza carga masiva + creacion inline sin sobrecargar el modal existente ni la pantalla de Detalle.
- **P7 (patron de carga masiva):** CONFIRMADO — filas repetibles en un mismo formulario (boton "agregar fila", cada fila con tipo + selector + cantidad + precio), guardado con un unico submit. Se descarta importacion Excel/CSV por mayor esfuerzo sin necesidad confirmada.
- Creacion inline de nuevos Perfiles/Practicas: el usuario podra dar de alta un Perfil o Practica nuevo sin salir de la pantalla nueva de carga. Pendiente definir en Diseno si la creacion inline de un Perfil exige composicion completa (RN-02: minimo 1 componente) o admite alta rapida con composicion diferida al catalogo — queda para etapa de Diseno.

### Pedido 2 — Propiedad "Unidad" en Perfiles + Precio por Unidad configurable
- Nueva propiedad numerica `Unidad` en la entidad `Practica` (UI "Perfil"): cantidad de unidades que pondera el valor del perfil.
- Nueva configuracion global `PrecioPorUnidad` (valor de referencia actual: $892.03).
- Formula: `Practica.PrecioActual = Unidad * PrecioPorUnidad` (calculado, ya no editable a mano).
- `ProduccionMensual estimada` = para lineas tipo Perfil, `PrecioSnapshot (= PrecioActual al momento de carga) * Cantidad` — sin cambios en el mecanismo de snapshot ya vigente (P3-A), solo cambia como se origina el PrecioActual del Perfil.
- **P8 (relacion Unidad-Precio):** CONFIRMADO — precio calculado automaticamente. Se elimina la edicion manual de `Practica.PrecioActual`.
- **P9 (ubicacion de configuracion):** CONFIRMADO — el valor `PrecioPorUnidad` y la accion de aumento por % viven dentro del listado de Perfiles (Practicas Index), no en pantalla de Configuracion separada.
- **P10 (conflicto con F-001 — CONFIRMADO):** F-001 (Aumento masivo de precios, ya implementado) permite hoy editar manualmente el precio de un Perfil y cascada UB→Perfil ponderada por `PracticaDetalle.Cantidad`. Con el nuevo modelo, ambos mecanismos quedan obsoletos para Perfiles. Decision: **se reemplaza para Perfiles** — el precio de Perfil pasa a ser 100% derivado de `Unidad * PrecioPorUnidad`; se retira la edicion manual de precio de Perfil y el cascade UB→Perfil deja de aplicarse a Perfiles. F-001 sigue vigente sin cambios para Practicas (UnidadBioquimica) sueltas. La composicion M:N (`PracticaDetalle`) se conserva solo como dato informativo/de laboratorio (que UBs integra un Perfil), ya no determina ni valida el precio (RN-01 "precio < sumatoria componentes" queda derogada para Perfiles).
- Accion de aumento simple: se aplica un % sobre `PrecioPorUnidad` (unico valor global), lo que recalcula automaticamente el precio de todos los Perfiles activos (via la formula). No hay cascade manual a implementar: al ser derivado, el aumento es automatico en cada lectura o requiere un recalculo batch de `PrecioActual` — a definir en Diseno/Arquitectura si `PrecioActual` se persiste desnormalizado (para performance/orden en listados) o se calcula al vuelo.

### Pedido 3 — Fix exportacion PDF Produccion Mensual
- Causa raiz identificada: `ProduccionMensualController.cs` (metodo `ReportePdf`), columna "Precio unit." definida con `c.ConstantColumn(55)` — insuficiente para montos con miles/decimales, provoca corte de digitos.
- Fix: ampliar el ancho constante (ej. a 70-75) y ajustar el resto de columnas fijas si es necesario para no desbalancear el layout A4 portrait. QuestPDF no tiene "shrink to fit" nativo por celda como Excel; la solucion practica es ancho fijo mayor + `AlignRight()` (ya presente).
- Sin impacto en otras capas. Sin migracion. Riesgo minimo — se resuelve directo en Implementacion sin pasar por Diseno/Arquitectura extendidos (WBS de 0.5h aprox., ver Presupuesto).

### Impacto en alcance funcional vigente
- Se deroga RN-01 (precio Practica/Perfil < sumatoria componentes) para la entidad `Practica` (Perfil). Sigue vigente el concepto de composicion pero sin validacion de precio.
- Se deroga la edicion manual de `Practica.PrecioActual` y su inclusion como target editable en F-001 (`Precios/AumentoMasivo`) — pasa a ser solo lectura/informativo para Perfiles en esa pantalla, o se remueve el tab de Perfiles de F-001 (a definir en Diseno).
- Nuevo caso de uso: CU-07 Carga masiva de produccion mensual (pantalla nueva). CU-08 Configurar Precio por Unidad y aplicar aumento %.

### Preguntas resueltas en sesion 4
| Ref | Pregunta | Respuesta confirmada |
|---|---|---|
| P6 | Carga masiva: partial o pantalla nueva? | Pantalla nueva dedicada |
| P7 | Patron de carga masiva | Filas repetibles en un formulario, un solo submit |
| P8 | Relacion Unidad-Precio en Perfil | Precio calculado automaticamente (Unidad x PrecioPorUnidad) |
| P9 | Ubicacion configuracion PrecioPorUnidad + aumento % | Dentro del listado de Perfiles |
| P10 | Que pasa con F-001 (cascade + edicion manual) para Perfiles | Se reemplaza: precio de Perfil 100% derivado, cascade UB→Perfil ya no aplica a Perfiles |

### Estado
ANALISIS FUNCIONAL DE SESION 4 CERRADO. Sin preguntas pendientes. Listo para pasar a Diseno funcional de los 3 items.

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
