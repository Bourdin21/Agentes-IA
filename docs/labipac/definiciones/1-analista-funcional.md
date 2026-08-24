# Memoria - Analista funcional

## Proyecto: labipac
## Ultima actualizacion: 2026-07-23

## Definiciones vigentes

### Terminologia de dominio (IMPORTANTE — invertida entre entidad Domain y nombre en UI)
| Termino de negocio | Entidad Domain | Definicion |
|---|---|---|
| "Practica" (UI, sentido nuevo del cliente) | `UnidadBioquimica` | Estudio medico individual con precio propio. |
| "Perfil" (UI) | `Practica` | Conjunto de N `UnidadBioquimica` via `PracticaDetalle` (M:N), con precio propio. |
| PRECIO | — | Valor monetario ($) asignado a una unidad bioquimica o practica/perfil. |
| PRODUCCION MENSUAL | `ProduccionMensual` | Cantidad de unidades bioquimicas y practicas/perfiles realizadas en un mes, opcionalmente por Centro de Salud. |

Toda mencion a "Perfil" en este documento = entidad `Practica`. Toda mencion a "Práctica" (sentido nuevo) = entidad `UnidadBioquimica`. Ejemplos de PERFILES: Rutina, Libreta Sanitaria.

### Alcance funcional resumido

**Incluido:**
1. Login con usuario y contraseña (usuario unico).
2. ABM de Unidades Bioquimicas ("Practicas" en UI) con nombre y precio.
3. ABM de Practicas ("Perfiles" en UI) con nombre, composicion (M:N con unidades bioquimicas) y precio — ver regla de precio vigente mas abajo (ya no editable a mano, derivado de Unidad × PrecioPorUnidad).
4. Carga mensual de cantidades: perfiles y/o unidades bioquimicas sueltas en el mismo mes, opcionalmente asociada a un Centro de Salud.
5. Carga masiva + creacion inline de Perfiles/Practicas desde Produccion Mensual (pantalla nueva dedicada, CU-07).
6. Precio snapshot por linea de produccion: cada linea guarda el precio vigente al momento de su carga. Al editar un periodo historico, el precio aparece pre-completado y editable con aviso visual.
7. Calculo automatico del total estimado: suma de (cantidad × precio_snapshot) de todos los items del mes.
8. Historial de calculos mensuales con detalle de cantidades, precios snapshot y totales, filtrable/agrupable por Centro de Salud.
9. Consulta y comparacion de periodos anteriores.
10. Edicion de cualquier mes en cualquier momento sin restriccion (sin cierre de periodo).
11. Aumento masivo de precios (F-001, ya implementado) — vigente para Unidades Bioquimicas sueltas; derogado para Perfiles (ver regla de precio de Perfil).
12. IVA en resumen mensual (F-002, ya implementado).
13. ABM de Centros de Salud (Privado/Mutual), catalogo independiente del catalogo `Mutual` de FABA.

**No incluido:**
1. Integracion con laboratorios, sistemas externos o APIs (mas alla de la sincronizacion `Mutual` ya existente de FABA).
2. Emision de factura o comprobante fiscal.
3. Gestion de pacientes, historias clinicas, resultados de estudios o turnos.
4. App movil nativa.
5. Multiusuario con roles complejos.
6. Cierre/bloqueo de periodos mensuales, maquina de estados de periodo.
7. Vinculo entre el catalogo `CentroSalud` y el catalogo `Mutual` (duplicacion de nombres aceptada explicitamente, P12).

### Reglas funcionales vigentes

- El sistema es web, de uso para un unico usuario autenticado.
- Cada Unidad Bioquimica ("Practica" en UI) tenia un precio monetario editable directamente **hasta sesion 6** — desde sesion 6 pasa a tener una `CantidadUnidades` propia y su precio (de referencia y por Centro de Salud) se calcula, ya no se edita a mano (ver regla de precio por Centro de Salud mas abajo).
- **Regla de precio de Perfil (vigente desde sesion 4, reemplaza la regla original):** el precio de un Perfil (`Practica`) ya NO es editable a mano ni valida contra la suma de sus componentes (RN-01 derogada para Perfiles). Es 100% derivado: `Practica.PrecioActual = Unidad × PrecioPorUnidad`, donde `Unidad` es un campo propio del Perfil y `PrecioPorUnidad` es una configuracion global unica (valor de referencia al confirmarse: $892.03), editable junto con la accion de aumento por % desde el listado de Perfiles (Practicas Index) — no en una pantalla de Configuracion separada. La composicion M:N (`PracticaDetalle`) se conserva solo como dato informativo/de laboratorio, ya no determina ni valida el precio.
- **Formula de aumento masivo F-001 (CASCADE PRECIO) — vigente solo para Unidades Bioquimicas sueltas, derogada para Perfiles:**
  ```
  delta_ub       = round(PrecioActual_UB × pct / 100, 2)
  UB.PrecioActual += delta_ub

  Para cada PracticaDetalle donde UnidadBioquimicaId == UB.Id (informativo, ya no repercute en precio de Perfil):
      # cascade retirado para Perfiles — ver regla de precio de Perfil arriba
  ```
- Una unidad bioquimica puede pertenecer a mas de una practica/perfil simultaneamente, sin exclusividad (P2-B).
- En la produccion mensual coexisten perfiles y unidades bioquimicas sueltas en el mismo mes, sin restriccion (P1-B).
- El calculo mensual suma todos los items cargados: Σ (cantidad × precio_snapshot) de cada linea (perfil o unidad suelta).
- El precio que se guarda en cada linea del historial es el precio vigente al momento de cargar/calcular ese item — snapshot inmutable (P3-A). Al agregar una linea nueva a un periodo historico, el sistema muestra el precio actual pre-completado en un campo editable con aviso visual ("Precio vigente: $X.XXX — podés modificarlo"); el usuario decide si lo ajusta antes de guardar (P5-B). Las lineas ya guardadas no cambian su snapshot.
- Los periodos mensuales son siempre editables, sin cierre ni bloqueo (P4-A) — no requieren maquina de estados.
- **Centro de Salud (sesion 5):** `ProduccionMensual` tiene `CentroSaludId` — catalogo `CentroSalud` (Nombre, Tipo enum Privado/Mutual, Activo) totalmente independiente del catalogo `Mutual` (FABA) — se acepta convivencia de nombres duplicados entre ambos sin vinculo (el cliente prefirio simplicidad sobre evitar duplicacion).
- **Precio por Unidad Bioquimica y por Perfil, diferenciado por Centro de Salud (sesion 6, 2026-08-23 — VERSION FINAL confirmada por el cliente, tras 2 correcciones):** la "unidad bioquimica" es una propiedad propia de la Practica ("Practica" en UI, entidad Domain `UnidadBioquimica`, hoy con precio propio editable directo) — cada Practica tiene una **cantidad de unidades bioquimicas** (campo nuevo, `CantidadUnidades`). El Perfil (entidad Domain `Practica`) YA NO carga su `Unidad` a mano: se calcula a partir de su composicion (`PracticaDetalle`, relacion M:N con cantidad por componente que ya existe hoy mas alla de ser informativa) — `Volumen(Perfil) = Σ (PracticaDetalle.Cantidad × UnidadBioquimica.CantidadUnidades)` de cada componente activo. Formulas de precio real por centro:
  - Precio de una Practica en el Centro X = `CantidadUnidades × PrecioUnidadBioquimica(Centro X)`.
  - Precio de un Perfil en el Centro X = `Volumen(Perfil) × PrecioUnidadBioquimica(Centro X)`.
  - `PrecioUnidadBioquimica(Centro)`: un unico valor por cada Centro de Salud (fila unica por centro, analogo al `PrecioPorUnidad` global que ya existe hoy) — NO hay una matriz de precio por cada combinacion item×centro.
  - **Cambio de fondo respecto a lo ya implementado y en produccion (revierte la decision de sesion 4):** la composicion del Perfil (`PracticaDetalle`) vuelve a determinar su precio, dejando de ser meramente informativa. Esto reactiva la necesidad de que todo Perfil tenga al menos 1 componente con `CantidadUnidades` cargada (RN-02 vuelve a ser obligatoria) para poder calcular su precio en cualquier centro. Confirmado explicitamente por el cliente (opcion elegida sobre la alternativa de mantener `Unidad` cargado a mano).
- **Centro de Salud pasa a ser obligatorio (sesion 6, reemplaza la opcionalidad de P13/sesion 5):** todo periodo de Produccion Mensual **nuevo** debe tener un Centro de Salud asignado — ya no se puede crear un periodo "global" sin centro. Los periodos historicos ya existentes con `CentroSaludId = NULL` (creados antes de esta sesion) NO se migran retroactivamente y se siguen pudiendo editar/consultar con el comportamiento anterior (precio de referencia, sin dependencia de centro) — compatibilidad hacia atras obligatoria, ya que el sistema no impone cierre de periodos (P4-A sigue vigente).
- **Precio de referencia en el catalogo (sesion 6):** fuera de una carga de Produccion Mensual concreta, el catalogo de Practicas y de Perfiles sigue mostrando un unico "precio de referencia", calculado con la misma formula pero usando el `PrecioPorUnidad` global historico como multiplicador (`CantidadUnidades × PrecioPorUnidad global` para Practicas, `Volumen(composicion) × PrecioPorUnidad global` para Perfiles) — el precio real de produccion para un centro especifico solo se usa/exige al cargar produccion para ese centro.
- **Backfill (sesion 6, riesgo relevante):** `UnidadBioquimica.CantidadUnidades` es un campo nuevo sin dato historico y **sin formula de aproximacion confiable** (a diferencia del backfill de sesion 2, que sí pudo aproximar `Practica.Unidad` a partir de un precio ya existente con una relacion directa) — no existe una relacion equivalente hoy entre el precio de una Practica y su "cantidad de unidades bioquimicas". El cliente debe cargar este valor a mano para cada Practica activa antes de que el calculo por centro funcione con esa Practica (o con cualquier Perfil que la tenga como componente). Es una carga mas chica que la "matriz item×centro" descartada en la correccion anterior, pero sigue siendo carga manual obligatoria, no automatizable.

### Casos de uso principales

| # | Caso de uso | Actor | Resumen |
|---|---|---|---|
| CU-01 | Iniciar sesion | Usuario unico | Acceso al sistema con credenciales validas. |
| CU-02 | Administrar Unidades Bioquimicas | Usuario unico | ABM con nombre y precio editable directamente. |
| CU-03 | Administrar Practicas (Perfiles) | Usuario unico | ABM con composicion M:N y `Unidad`; precio 100% derivado de `Unidad × PrecioPorUnidad`, no editable a mano. |
| CU-04 | Cargar produccion mensual | Usuario unico | Registrar cantidades de perfiles y/o unidades sueltas por mes, opcionalmente por Centro de Salud, con precio snapshot editable por linea. |
| CU-05 | Calcular estimacion de cobro | Sistema | Sumar (cantidad × precio_snapshot) de todos los items del mes y mostrar total. |
| CU-06 | Consultar historial mensual | Usuario unico | Ver detalle y total calculado de periodos anteriores, filtrar/comparar por Centro de Salud. |
| CU-07 | Carga masiva de produccion mensual | Usuario unico | Pantalla dedicada: filas repetibles (tipo + selector + cantidad + precio) con un unico submit, incluye creacion inline de Perfiles/Practicas nuevos. |
| CU-08 | Configurar Precio por Unidad de referencia y aplicar aumento % | Usuario unico | Editar el precio de referencia global (catalogo) que se usa fuera de un Centro de Salud especifico, con aumento % que recalcula Practicas y Perfiles activos. |
| CU-09 | Administrar Centros de Salud | Usuario unico | ABM simple (Nombre, Tipo Privado/Mutual, Activo), mismo patron que Unidades Bioquimicas. |
| CU-10 | Configurar el Precio de Unidad Bioquimica por Centro de Salud (sesion 6) | Usuario unico | Cargar/editar el "Precio de Unidad Bioquimica" de un Centro de Salud (un unico valor por centro, no una matriz) — a partir de el se calculan automaticamente los precios de todas las Practicas (`CantidadUnidades × valor`) y Perfiles (`Volumen de composicion × valor`) en ese centro. |

### Criterios de aceptacion verificables

**CU-01:** con credenciales validas el usuario ingresa; con credenciales invalidas el sistema rechaza el acceso con mensaje de error.

**CU-02:** se pueden crear/editar unidades bioquimicas con nombre y precio >= 0 en cualquier momento; el sistema impide precio negativo; la baja es logica (no aparece en cargas nuevas, el historial conserva su precio snapshot); una unidad puede asociarse a multiples perfiles sin restriccion.

**CU-03 (sesion 1-4):** se pueden crear perfiles con nombre, `Unidad` y al menos 1 unidad bioquimica componente; el precio se calcula automaticamente (`Unidad × PrecioPorUnidad`), sin campo de edicion manual de precio; la composicion queda visible como dato informativo (sin validacion de precio contra la suma de componentes). **Ajuste sesion 6:** `Unidad` deja de cargarse a mano — se calcula a partir de la composicion (`Σ Cantidad_componente × CantidadUnidades_componente`); la composicion vuelve a ser obligatoria (minimo 1 componente, y cada componente debe tener `CantidadUnidades` cargada para que el Perfil tenga precio calculable). La Practica (Unidad Bioquimica) pasa a tener tambien su propio campo `CantidadUnidades`, y su `PrecioActual` de catalogo pasa a ser derivado (`CantidadUnidades × PrecioPorUnidad` de referencia), dejando de editarse a mano — mismo cambio que ya sufrio el Perfil en sesion 4.

**CU-04:** el usuario selecciona mes/año y **Centro de Salud (obligatorio para periodos nuevos desde sesion 6)** y carga cantidades (enteras, >= 0) por item; puede cargar perfiles y/o unidades sueltas en el mismo mes sin restriccion; cada linea captura como snapshot el precio vigente **para el Centro de Salud del periodo**: para una Practica, `CantidadUnidades × Precio de Unidad Bioquimica de ese centro`; para un Perfil, `Volumen de su composicion × Precio de Unidad Bioquimica de ese centro` (no el precio de referencia de catalogo); si ese Centro de Salud todavia no tiene cargado su Precio de Unidad Bioquimica, o si el item no puede calcular su cantidad/volumen (falta `CantidadUnidades` en algun componente), el sistema bloquea el alta de la linea con mensaje claro; al agregar una linea nueva a un periodo historico ya existente, se muestra el precio pre-completado y editable con aviso visual, sin modificar el snapshot de lineas ya guardadas; el periodo nunca se cierra. Periodos historicos sin Centro de Salud (creados antes de sesion 6) siguen usando el precio de referencia de catalogo.

**CU-05:** el total estimado = Σ (cantidad × precio_snapshot) de cada linea del mes; se muestra el detalle linea por linea (nombre, tipo, cantidad, precio snapshot, subtotal); si no hay cantidades cargadas el total es cero; se recalcula automaticamente al agregar/editar/eliminar una linea.

**CU-06:** el usuario puede seleccionar cualquier periodo historico y ver su detalle completo (cantidades y precios snapshot inmutables); se puede comparar periodos anteriores en tabla paginada, filtrada/agrupada por Centro de Salud si corresponde; el reporte PDF muestra el nombre del Centro de Salud en el encabezado cuando el periodo lo tiene asignado.

**CU-07/CU-08/CU-09:** sin tabla detallada de CA propia en el analisis original — ver bullets funcionales de cada caso de uso arriba; el detalle verificable de estos 3 se desarrollo directamente en Diseño/Arquitectura de sesiones 4 y 5.

### Permisos, estados y validaciones

**Permisos:** un unico usuario autenticado con capacidad de administracion total.

**Estados:**
| Entidad | Estados |
|---|---|
| Unidad Bioquimica | Activa / Inactiva (baja logica) |
| Practica (Perfil) | Activa / Inactiva (baja logica) |
| Periodo mensual | Sin estados — siempre editable (P4-A) |
| Centro de Salud | Activo / Inactivo |

**Validaciones:**
| Campo | Regla |
|---|---|
| Precio unidad bioquimica | Obligatorio, >= 0 |
| `Unidad` de Perfil | Obligatorio, numerico |
| `PrecioPorUnidad` (global) | Obligatorio, >= 0 |
| Composicion de perfil | Al menos 1 unidad bioquimica asociada, **cada una con `CantidadUnidades` cargada** (sesion 6: vuelve a ser obligatoria y determina el precio del Perfil — ya NO es solo informativa) |
| `CantidadUnidades` de Practica (sesion 6) | Obligatorio, entero >= 1, sin backfill automatico confiable |
| `PrecioUnidadBioquimica` por Centro de Salud (sesion 6) | Obligatorio, >= 0, uno por cada Centro de Salud |
| Cantidad produccion mensual | Entero, >= 0 |
| Periodo de carga | Mes/año validos; no duplicar el mismo item en el mismo mes+Centro de Salud |
| `ProduccionMensual` unicidad | Mes+Año+CentroSaludId, tratando NULL como valor propio |

### Riesgos y supuestos vigentes

| # | Riesgo/Supuesto | Detalle | Estado |
|---|---|---|---|
| R1 | Coexistencia de perfiles y componentes sueltos en la misma carga | El usuario es responsable de no duplicar intencionalmente el mismo trabajo | Aceptado por diseño (P1-B) |
| R2 | Precio pre-completado al agregar linea a mes historico es el actual | El usuario debe ajustarlo manualmente si no corresponde; sistema avisa, campo editable | Mitigado por diseño (P5-B) |
| R3 | Sin cierre de periodo, cualquier mes pasado puede modificarse sin trazabilidad visible | Usuario unico y consciente | Aceptado por diseño (P4-A) |
| R-CS1 | Duplicacion semantica entre `Mutual` (FABA) y `CentroSalud` tipo Mutual | Sin vinculo entre ambos catalogos | Aceptado explicitamente por el cliente (P12) |
| R-CS2 | Unicidad Mes+Año+CentroSaludId (NULL como valor propio) no expresable como constraint parcial en MySQL | Se enforcea en Service, mismo patron que la unicidad original Mes+Año (RA-03) | Vigente, sin resolver a nivel DB |
| S1 | Uso local para un solo usuario autenticado | — | Vigente |
| S2 | El calculo es una estimacion de cobro, no facturacion fiscal | — | Vigente |
| S3 | Stack: ASP.NET Core MVC .NET 10 + EF Core + MySQL (BlankProject base) | — | Vigente |
| S-CS1 | No se migran ni asignan retroactivamente los periodos historicos existentes a un Centro de Salud | Quedan sin centro | Confirmado (respuesta de migracion, sesion 5) |
| R-PC1 (sesion 6, VERSION FINAL) | Backfill de `UnidadBioquimica.CantidadUnidades` (campo nuevo, sin formula de aproximacion confiable a partir del precio actual) | El cliente debe cargar a mano la cantidad de unidades bioquimicas de cada Practica activa antes de que esa Practica (o cualquier Perfil que la tenga como componente) pueda cotizarse en un centro. Carga acotada (1 valor por Practica), pero manual y obligatoria | Riesgo medio, a coordinar con el cliente antes del deploy — bloqueante parcial (Practicas/Perfiles sin el dato cargado no pueden usarse en produccion mensual por centro hasta completarlo) |
| R-PC2 | Centro de Salud sin su "Precio de Unidad Bioquimica" cargado todavia, al momento de cargar produccion para ese centro | El sistema debe bloquear el alta de lineas para ese centro con mensaje claro hasta que se cargue el valor | A confirmar tolerancia operativa con el cliente (¿bloquea o permite completar el precio ahi mismo?) |
| R-PC3 (sesion 6, VERSION FINAL) | Alta rapida de Practica o Perfil nuevo desde dentro de un periodo con Centro de Salud | Una Practica nueva requiere cargar su `CantidadUnidades` en el mismo alta (o queda sin precio calculable); un Perfil nuevo requiere componentes con `CantidadUnidades` ya cargada para tener precio — el alta rapida sin composicion (habilitada en sesion 4) deja de tener sentido practico para Perfiles bajo este modelo | A resolver en Diseno: ¿se exige composicion de nuevo en el alta rapida de Perfil? |
| R-PC7 (sesion 6, nuevo) | Reactivar la dependencia composicion→precio para Perfiles revierte una decision explicita de sesion 4 (RN-02 relajada globalmente, RN-01 derogada) que ya esta en produccion, con Perfiles reales que hoy pueden tener 0 componentes o componentes con `CantidadUnidades` inexistente | Perfiles activos existentes sin composicion completa quedarian sin precio calculable en ningun centro hasta que el cliente complete su composicion — requiere relevamiento previo de cuantos Perfiles estan en esa situacion | Confirmado por el cliente como direccion elegida; pendiente medir el impacto real sobre los Perfiles ya cargados |
| R-PC4 | Cambio de regla ya cerrada y en produccion (P13/RN-25, sesion 5): Centro de Salud pasa de opcional a obligatorio para periodos nuevos | Cambia el comportamiento visible para el cliente respecto de lo ya entregado | Confirmado explicitamente por el cliente en esta sesion |
| R-PC5 (revisado) | F-001 (Aumento masivo de precios) hoy aplica un % sobre el precio de referencia de cada Unidad Bioquimica individualmente — con el modelo corregido (un unico "Precio de Unidad Bioquimica" por centro que multiplica a todas las Practicas y Perfiles de ese centro), aumentar el precio en un centro pasa a ser una unica operacion (editar o aumentar % ese valor), igual patron que ya usa CU-08 para Perfiles — probablemente hace innecesaria la seleccion item por item de F-001 dentro de un contexto de centro | Oportunidad de simplificacion a confirmar en Diseno (¿F-001 se mantiene solo para el precio de referencia global, y el aumento por centro se hace desde la pantalla de CU-10?) |
| R-PC6 | Doble mantenimiento: precio de referencia (catalogo) + N precios por Centro de Salud, sin vinculo automatico entre ambos | Riesgo de que el cliente actualice uno y no el otro, generando inconsistencia percibida | Aceptado como consecuencia del modelo elegido (precio de referencia independiente, confirmado por el cliente) |

### Banderas tempranas
| Bandera | Valor | Nota |
|---|---|---|
| Requiere migracion EF | SI | `UnidadBioquimica`, `Practica`, `PracticaDetalle` (M:N), `ProduccionMensual` (+`CentroSaludId`), `ProduccionDetalle` (precio_snapshot), `CentroSalud` (nueva), config global `PrecioPorUnidad`. Sesion 6: +1 campo nuevo (`UnidadBioquimica.CantidadUnidades` — la entidad "Practica" en UI, no confundir con la entidad Domain `Practica` que es "Perfil" — con backfill por aproximacion) + 1 tabla nueva ("Precio de Unidad Bioquimica" por Centro de Salud, una fila por centro). |
| Integracion externa | NO | Sin integraciones externas mas alla de la sincronizacion `Mutual` de FABA ya existente. |
| Maquina de estados | NO | Descartada — P4-A confirma que no hay cierre ni bloqueo de periodos. |

### Exclusiones confirmadas
- Integraciones externas (mas alla de FABA/`Mutual` ya existente).
- Facturacion electronica / comprobante fiscal.
- Gestion de pacientes, resultados clinicos ni turnos.
- Aplicacion movil nativa.
- Multiusuario con roles complejos.
- Maquina de estados ni cierre de periodos.
- Vinculo entre catalogo `CentroSalud` y catalogo `Mutual`.

## Historial de ajustes
- 2026-06-12: Memoria inicial del proyecto — alcance base de calculo, catalogos y carga mensual. .NET 10 en smarteasp confirmado como destino.
- 2026-06-13 (sesion 1): Terminologia de dominio confirmada (Unidad Bioquimica, Practica, Precio), ejemplos de practicas, requerimiento de historial mensual con comparacion de periodos.
- 2026-06-13 (sesion 2): Cerradas P1-P4 — coexistencia de practicas/unidades sueltas (P1-B), unidad compartida entre multiples practicas (P2-B), precio snapshot inmutable por linea (P3-A), periodos siempre editables sin cierre (P4-A). Eliminada maquina de estados del alcance.
- 2026-06-13 (sesion 3): Cerrado P5-B — precio pre-completado editable con aviso al agregar linea a periodo historico. ANALISIS FUNCIONAL ORIGINAL CERRADO.
- 2026-06-25 (F-001/F-002, documentadas en copia local, migradas a esta ruta canonica el 2026-07-23): implementados y en produccion Aumento masivo de precios (`Precios/AumentoMasivo`, formula CASCADE PRECIO por delta ponderado) e IVA en resumen mensual.
- 2026-07-08 (sesion 4): 3 mejoras — (1) carga masiva + creacion inline de Perfiles/Practicas desde Produccion Mensual (CU-07, pantalla dedicada con filas repetibles); (2) precio de Perfil pasa a ser 100% derivado (`Unidad × PrecioPorUnidad`), deroga edicion manual y el cascade F-001 para Perfiles (sigue vigente para Unidades Bioquimicas sueltas) (CU-08); (3) fix de exportacion PDF (columna "Precio unit." truncaba montos grandes).
- 2026-07-23 (sesion 5): Produccion Mensual separable por Centro de Salud (Privado/Mutual) — `CentroSaludId` opcional en `ProduccionMensual`, catalogo nuevo `CentroSalud` independiente de `Mutual` (FABA), unicidad Mes+Año+CentroSaludId (CU-09). Sin migracion retroactiva de periodos historicos.
- 2026-08-23 (sesion 6): Precio por Unidad Bioquimica y por Perfil diferenciado por Centro de Salud. Se confirmaron con el cliente 4 puntos bloqueantes iniciales: (1) granularidad por Centro de Salud individual (no por Tipo); (2) alcance incluye tanto Practicas sueltas como Perfiles; (3) Centro de Salud obligatorio para periodos nuevos (cambia P13/RN-25 de sesion 5, sin migracion retroactiva); (4) el catalogo sigue mostrando un precio de referencia unico. **2 rondas de correccion posterior del cliente el mismo dia, hasta llegar al modelo final:** (a) el precio NO es una matriz item×centro — hay un unico "Precio de Unidad Bioquimica" por Centro de Salud; (b) la "cantidad de unidades bioquimicas" es una propiedad de la Practica (no del Perfil); el Perfil calcula su volumen de unidades a partir de su composicion (`Σ Cantidad_componente × CantidadUnidades_componente`), reactivando la dependencia composicion→precio que se habia derogado en sesion 4 (confirmado explicitamente por el cliente sobre la alternativa de mantener `Unidad` cargado a mano). Formulas finales: Practica en Centro X = `CantidadUnidades × PrecioUnidadBioquimica(X)`; Perfil en Centro X = `Volumen(composicion) × PrecioUnidadBioquimica(X)`. Riesgo de backfill revisado (R-PC1: sin formula de aproximacion confiable para `CantidadUnidades`, carga manual pero acotada a 1 valor por Practica) y nuevo riesgo R-PC7 (Perfiles ya en produccion sin composicion completa quedarian sin precio calculable). CU-10 y CU-03 ajustados. ANALISIS CERRADO — listo para Diseno funcional.
- 2026-08-16: Reestructuración documental — este archivo tenía las sesiones 4 y 5 prependidas como secciones de nivel 2 al principio (orden cronológico invertido respecto al resto del documento) y una sección `## Historial de ajustes` duplicada a mitad de archivo, con contenido base (Alcance/Casos de uso/CA/Permisos/Riesgos/Banderas) apareciendo *después* de esa sección duplicada. Consolidado en una única `## Definiciones vigentes` (terminología, alcance, reglas — incluida la regla de precio de Perfil que reemplazó a la original y la fórmula F-001 con su alcance acotado tras sesión 4 —, casos de uso CU-01 a CU-09, criterios de aceptación, permisos/estados/validaciones, riesgos y banderas) + este historial cronológico único. Ningún dato funcional se perdió.
