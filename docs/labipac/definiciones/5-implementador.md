# Implementador — LabIPAC
> Memoria acumulativa del agente implementador. Actualizar al inicio y cierre de cada etapa.

---

## Historial de sesiones

### Sesión 6 — QA-S3-02: un solo escritor para `UnidadBioquimica.PrecioActual` + retiro completo de F-001
**Fecha:** 2026-08-24
**Estado:** ✅ BUILD OK (`dotnet build LabIPAC.slnx --no-incremental` → **0 errores, 9 warnings**, exactamente los mismos preexistentes: NU1902 MailKit/MimeKit ×8 + CS0114 `HomeController.StatusCode`). **Sin migración EF** — no cambió ninguna entidad ni columna.
**Nota de numeración:** en los comentarios de código esta sesión figura como *"sesión 7"*, siguiendo la numeración de analista/diseñador/arquitecto que ya usaba el resto del código (donde M19–M25 es "sesión 6"). La memoria del implementador lleva su propia secuencia.

Input: hallazgo **QA-S3-02** (`6-qa.md`, sesión 3, major, escalado sin auto-fix) + **decisión de negocio ya tomada por el usuario del estudio**: retirar F-001 de Prácticas, mismo criterio aplicado a Perfiles el 2026-07-08.

#### 0. Escaneo de reutilización
No aplica como búsqueda cross-proyecto: no es funcionalidad nueva, es la **reconciliación de dos escritores sobre un mismo campo** dentro de labipac y el retiro de una pantalla existente. Se reutilizó el patrón **intra-proyecto** ya validado: el batch atómico de `ActualizarPrecioPorUnidadAsync` (sesión 3, extendido en sesión 5) como molde exacto del recálculo agregado. Sin altas al catálogo (no hay componente genérico nuevo).

#### 1. Problema resuelto
Desde RN-32 (sesión 5) `UnidadBioquimica.PrecioActual` tenía **dos escritores sin reconciliación**: F-001 (`PreciosController`) lo escribía directo en $, y la fórmula `CantidadUnidades × PrecioPorUnidad` lo recalculaba en el ABM. La decisión 4 de la sesión 5 excluía a `UnidadBioquimica` del batch global justamente para no pisar F-001, con el efecto colateral de que el precio de referencia quedaba visiblemente desfasado (listado y formulario mostraban números distintos). **Resuelto eligiendo un único escritor: la fórmula.** F-001 se retira por completo, porque tras la simplificación del 2026-07-08 ya solo operaba sobre `UnidadBioquimica`.

#### 2. Cambios por capa

| Capa | Archivo | Cambio |
|---|---|---|
| Application | `LabIPAC.Application/Interfaces/IPracticaService.cs` | Doc de contrato de `ActualizarPrecioPorUnidadAsync` / `AumentarPrecioPorUnidadPorcentajeAsync`: ahora declaran el recálculo de Perfiles **y** Prácticas y el escritor único. Sin cambio de firma. |
| Infrastructure | `LabIPAC.Infrastructure/Services/PracticaService.cs` | `ActualizarPrecioPorUnidadAsync` recalcula además `PrecioActual = CantidadUnidades × nuevoValor` de todas las `UnidadBioquimica` activas no eliminadas, **en el mismo `SaveChangesAsync`**. Mensaje de retorno informa ambos conteos. Se quitó la exclusión de la decisión 4. |
| Web | `LabIPAC.Web/Controllers/PreciosController.cs` | **ELIMINADO** (F-001). |
| Web | `LabIPAC.Web/Views/Precios/AumentoMasivo.cshtml` | **ELIMINADO** (la carpeta `Views/Precios/` queda vacía y desaparece). |
| Web | `LabIPAC.Web/Models/PreciosViewModels.cs` | **ELIMINADO** — `AumentoMasivoViewModel` y `AumentoItemPreviewDto` eran de uso exclusivo de F-001 (verificado por grep). |
| Web | `LabIPAC.Web/Views/Shared/_Layout.cshtml` | Quitada la entrada de sidebar "Aumento masivo". El bloque `SuperUsuario/Administrador` queda con "Precios por Centro". |
| Web | `LabIPAC.Web/Controllers/PracticasController.cs` | `Index` agrega `ViewBag.CantidadPracticasActivas` y `ViewBag.CantidadPracticasSinVolumen`. |
| Web | `LabIPAC.Web/Views/Practicas/Index.cshtml` | Copy de la card actualizado (ahora describe también la fórmula de Prácticas y declara ser el único mecanismo de aumento masivo); confirmación SweetAlert2 informa ambos conteos; alerta preventiva si hay Prácticas sin `CantidadUnidades`. |
| Web | `LabIPAC.Web/Controllers/PreciosPorCentroController.cs` | Solo comentario de clase: decía "F-001 NO se toca", afirmación ya falsa. |

`AumentarPrecioPorUnidadPorcentajeAsync` **no necesitó cambios**: delega en `ActualizarPrecioPorUnidadAsync`, así que hereda el comportamiento nuevo.

#### 3. Decisiones de implementación
1. **La lógica queda en `PracticaService`, no en `IUnidadBioquimicaService`.** Dos razones concretas, no de estilo: (a) la **atomicidad** pedida exige un único `SaveChangesAsync` sobre la misma unidad de trabajo — repartirlo entre dos servicios rompería la operación en dos transacciones; (b) `UnidadBioquimicaService` **ya depende de `IPracticaService`** (`ObtenerPrecioPorUnidadVigenteAsync`), con lo que la dependencia inversa sería **circular** y rompería el contenedor DI. Se accede por `AppDbContext`, mismo patrón que el resto del archivo (`CalcularVolumenComposicionAsync`, `ObtenerDiagnosticoCatalogoAsync`). **No se creó ninguna interfaz nueva.**
2. **Se borró el código de F-001, no se dejó inaccesible.** Criterio por defecto del estudio (no dejar código muerto). No se encontró ninguna razón concreta para conservarlo: la pantalla no es linkeable desde ningún otro lado (grep exhaustivo: las únicas 2 referencias eran el sidebar y la propia vista), no hay integraciones externas ni endpoints consumidos por terceros, y el historial de git conserva el código si hiciera falta recuperarlo. `/Precios/AumentoMasivo` pasa a devolver **404**.
3. **Filtro `Activo && DeletedAt == null`** para las `UnidadBioquimica`, idéntico al que ya usaba la consulta de `Practicas` en el mismo método. Las prácticas dadas de baja conservan su `PrecioActual` histórico.
4. **Adición deliberada fuera del pedido estricto (fácil de revertir):** alerta preventiva en la card cuando hay Prácticas activas con `CantidadUnidades = 0`. Motivo: este cambio **extiende a Prácticas el riesgo RA-17/RL-1** que QA verificó en vivo sobre Perfiles (mover el precio global tiró un Perfil real a $0). Antes de esta sesión las Prácticas estaban blindadas por la exclusión de la decisión 4; ahora ya no. Es presentación pura (un `@if` + un contador), sin lógica de negocio nueva, y enlaza al diagnóstico M24 que ya existía. Ver riesgo R-1 abajo.
5. **Copy de la card actualizado** porque decía "recalcula los N perfil(es) activo(s)" — afirmación que quedó incompleta y que el usuario lee justo antes de confirmar una operación destructiva.

#### 4. Migraciones EF
**Ninguna.** No se agregó, quitó ni modificó ninguna propiedad persistida. El cambio es de *quién y cuándo* escribe un campo que ya existía.

#### 5. Verificación ejecutada
- **Build:** `dotnet build LabIPAC.slnx --no-incremental` → **0 errores, 9 warnings**, los mismos 9 preexistentes de la sesión anterior. Ningún warning nuevo. Corrido 3 veces (tras Tarea 1, tras Tarea 2 y al cierre).
- **Referencias rotas:** grep sobre `*.cs`, `*.cshtml`, `*.js`, `*.json` de `AumentoMasivoViewModel`, `AumentoItemPreviewDto`, `PreciosController`, `"Precios"` y `Precios/AumentoMasivo` → **0 resultados** fuera de la documentación histórica. La carpeta `LabIPAC.Web/Views/Precios/` ya no existe. Las vistas Razor compilan en build (sin runtime compilation), así que el build limpio confirma también que `_Layout.cshtml` y `Practicas/Index.cshtml` bindean bien.
- **Estado de `labipac_dev` (consulta read-only, sin escrituras):** `PrecioPorUnidad` = 918,79; 1 Práctica activa, **con `CantidadUnidades = 0`**; 1 Perfil activo. Ver R-1.
- **Sin smoke test funcional propio** (regla del rol): no se levantó la app ni se ejercitaron flujos por navegador/HTTP. La base de desarrollo **no fue modificada** — no se cargaron datos de prueba, así que queda limpia por construcción. Ver la guía de verificación manual abajo.

#### 6. Riesgos
- **R-1 (ALTO — el riesgo más serio de esta entrega) — el riesgo RA-17/RL-1 ahora también alcanza a las Prácticas.** Con `CantidadUnidades = 0`, cualquier cambio del precio global deja el `PrecioActual` de esa Práctica en **$0,00**. En `labipac_dev` la única Práctica activa está exactamente en ese estado. **Y en Producción es peor:** según la entrada del orquestador del 2026-08-24 en `trazabilidad.md`, la migración se aplicó **sin backfill** sobre una base con **60 Prácticas activas reales** — todas hoy en `CantidadUnidades = 0`. El primer aumento global que se aplique tras publicar este código pondría el precio de referencia de **las 60** en $0,00 de una sola vez. Antes de esta sesión la exclusión de la decisión 4 las protegía por accidente. Mitigación implementada en UI: alerta preventiva en la card + link al diagnóstico M24. **Mitigación obligatoria de proceso: cargar `CantidadUnidades` en las 60 Prácticas ANTES de mover el precio global en Producción** — se suma al bloqueante RL-1/RL-2 que QA ya había dejado abierto.
- **R-2 (MEDIO) — pérdida de una capacidad funcional: el aumento selectivo.** F-001 permitía aumentar **un subconjunto elegido** de Prácticas con un % propio. El mecanismo que lo reemplaza es **global y uniforme**: mueve el precio por unidad y recalcula todo el catálogo. Es exactamente lo que pidió la decisión de negocio, pero conviene que el usuario lo confirme: si alguna vez necesita subir solo algunas Prácticas, el camino ahora es editar su `CantidadUnidades`, que es un cambio de *volumen*, no de *precio*.
- **R-3 (BAJO) — descubribilidad.** El usuario que estaba acostumbrado a "Configuración > Aumento masivo" en el sidebar ahora debe entrar a **Perfiles** para operar el precio de las **Prácticas**, lo cual es contraintuitivo dada la nomenclatura invertida del dominio. Mitigado parcialmente por el copy nuevo. Si molesta en uso real, la solución natural es replicar la card en `UnidadesBioquimicas/Index` (no se hizo: sería una pantalla nueva fuera de alcance, y duplicaría el control).
- **R-4 (BAJO) — costo del batch.** Ahora se materializan y actualizan también todas las `UnidadBioquimica` activas. Volumen de catálogo chico; sin impacto esperado.

#### 7. Pruebas mínimas requeridas para QA
1. **Recálculo de Prácticas (el fix de QA-S3-02):** cargar 2-3 Prácticas con `CantidadUnidades` distintos (ej. 3, 5, 10), aplicar un aumento % desde la card "Precio por Unidad" de `Practicas/Index` y verificar que el `PrecioActual` de **las tres** quedó en `CantidadUnidades × nuevo valor`, y que el listado de Prácticas y el formulario de edición muestran **el mismo número** (era el síntoma exacto de QA-S3-02).
2. **Atomicidad:** confirmar que Perfiles y Prácticas quedan consistentes entre sí después de la misma operación (un solo commit).
3. **Vía "Guardar valor" además de "Aumentar %":** ambas entran por `ActualizarPrecioPorUnidadAsync`, verificar las dos.
4. **F-001 retirado:** `/Precios/AumentoMasivo` → **404**; el sidebar no muestra "Aumento masivo" ni para SuperUsuario ni para Administrador.
5. **Alerta preventiva:** con al menos una Práctica en `CantidadUnidades = 0`, la card muestra el aviso amarillo con link al diagnóstico; con todas cargadas, el aviso desaparece.
6. **Conteos del mensaje y del SweetAlert:** deben coincidir con la cantidad real de Perfiles y Prácticas activos.
7. **No-regresión:** ABM de Prácticas y Perfiles, `PreciosPorCentro` (RN-31: los precios por centro **no** deben moverse al cambiar el global), y PDF/Excel de Producción Mensual (leen `PrecioSnapshot`, no deberían verse afectados).

#### 8. Checklist de salida para merge
- [x] Build OK, 0 errores, sin warnings nuevos.
- [x] Sin migración EF (verificado: ninguna entidad tocada).
- [x] Sin referencias rotas tras el retiro de F-001 (grep exhaustivo, 0 resultados).
- [x] `labipac_dev` sin datos de prueba (no se escribió nada en la base).
- [x] Lógica de negocio en Service, no en Controller.
- [ ] QA funcional de los 7 puntos de arriba (**incluye la verificación en vivo del recálculo, que este rol no ejecuta**).
- [ ] Marcar QA-S3-02 como resuelto tras la verificación de QA.
- [ ] Confirmar con el usuario R-2 (pérdida del aumento selectivo) y R-3 (descubribilidad).
- [ ] **Antes del deploy a Producción (R-1):** cargar `CantidadUnidades` en todas las Prácticas activas ANTES de tocar el precio global.

### Sesión 5 bis — M25: sugerencia de `CantidadUnidades` por resolución del sistema de ecuaciones (extensión de M24)
**Fecha:** 2026-08-23
**Estado:** ✅ BUILD OK (0 errores, 9 warnings preexistentes) — algoritmo verificado con 9/9 casos esperados sobre base MySQL aislada + corrida read-only sobre `labipac_dev` + 2 casos borde. **Sin migración EF** (no se agregó ni cambió ningún dato persistido).

Input: pedido del orquestador (`trazabilidad.md`, entrada "M25 — INICIADO"). Extensión puntual de M24; **no se tocó nada de M19–M24** salvo agregar la sección nueva a la pantalla de diagnóstico.

#### 0. Escaneo de reutilización
- `docs/patrones/catalogo.yml` (17 patrones): **sin match de código**. Lo más cercano conceptualmente es **PAT-013** (la-platense, "Stock arranca en cero + verificación por conteo"): mismo criterio de fondo — *el sistema no inventa el dato faltante, lo sugiere/prioriza y el usuario lo carga a mano con su propio criterio*. M25 es la variante "sugerencia derivada de datos históricos" de esa misma familia; el código no es reutilizable (allá es un ajuste auditado de stock, acá un solver read-only).
- Escaneo de `docs/*/definiciones/5-implementador.md`: sin ningún proyecto que reconstruya valores faltantes resolviendo un sistema de ecuaciones a partir de agregados históricos.
- **Decisión:** implementar desde cero dentro de labipac, reutilizando el patrón **intra-proyecto** de la propia pantalla M24 (tabla DataTables de solo lectura con fila accionable hacia el ABM).
- Catálogo: se agregó **PAT-018** ("Reconstruir un dato faltante despejándolo de los totales históricos ya calculados"), por ser una técnica generalizable a cualquier migración donde el total derivado sobrevive pero sus componentes se perdieron.

#### Archivos modificados (5, ninguno nuevo)

| Archivo | Cambio |
|---------|--------|
| `LabIPAC.Application/DTOs/PrecioPorUnidadCentroSaludDtos.cs` | + `SugerenciaCantidadUnidadesDto` (Id, Nombre, `EstaEliminada`, `CantidadUnidadesActual`, `Sugerencia`, `Confianza`, `Origen`, `Detalle`). |
| `LabIPAC.Application/Interfaces/IPracticaService.cs` | + `SugerirCantidadUnidadesAsync()` (documentada como SOLO LECTURA). |
| `LabIPAC.Infrastructure/Services/PracticaService.cs` | + `SugerirCantidadUnidadesAsync` (el solver), + privados `RegistrarSugerencia`, `ConstruirDetalleSugerencia` y la clase interna `SugerenciaEnConstruccion`. **No se tocó ningún método existente.** |
| `LabIPAC.Web/Controllers/PreciosPorCentroController.cs` | `Diagnostico` llama además a `SugerirCantidadUnidadesAsync` y mapea las filas al VM. Sigue sin escribir nada. |
| `LabIPAC.Web/Models/PreciosPorCentroViewModels.cs` | + `SugerenciaCantidadUnidadesRowViewModel`; `DiagnosticoCatalogoViewModel` + `Sugerencias` y `SugerenciasParaPracticasSinCantidad`. |
| `LabIPAC.Web/Views/PreciosPorCentro/Diagnostico.cshtml` | + sección/card "Sugerencias de Cantidad de Unidades" con su propia tabla DataTables (`#tablaSugerencias`). El bloque de M24 quedó intacto. |

#### Algoritmo implementado (`PracticaService.SugerirCantidadUnidadesAsync`)
Premisa: la migración de la sesión 5 puso `UnidadBioquimica.CantidadUnidades = 0` en todos los registros, pero **no tocó `Practica.Unidad`**, que conserva el valor histórico. Como RN-33 define `Unidad = Σ (PracticaDetalle.Cantidad × UnidadBioquimica.CantidadUnidades)`, cada Perfil con `Unidad > 0` es una **ecuación** cuyas incógnitas son los `CantidadUnidades` de sus componentes. Se resuelve por **sustitución iterativa**, sin librerías de álgebra lineal ni mínimos cuadrados (volumen chico + lógica auditable).

1. **Ecuaciones:** Perfiles activos, no eliminados, con `Unidad > 0` y al menos un `PracticaDetalle` no eliminado. Los componentes se leen con `IgnoreQueryFilters()` para **incluir los que hoy están soft-deleted** (criterio distinto y deliberado respecto de RN-33: acá se reconstruye un dato histórico, y la `Unidad` guardada se calculó cuando esos componentes estaban vigentes). Si un Perfil repite la misma Práctica en dos detalles, se agrupan sumando `Cantidad` (una incógnita, no dos).
2. **Semilla de conocidos:** las Prácticas que ya tienen `CantidadUnidades > 0` (cargadas a mano por el cliente) se toman como dato exacto.
3. **Regla única de despeje**, aplicada en pasadas sucesivas: si a una ecuación le queda **exactamente una incógnita**, `valor = (Unidad − Σ Cantidad×valor_conocido_de_los_demás) / Cantidad_de_la_incógnita`. Los casos "1 componente con Cantidad = 1" (asignación directa) y "1 componente con Cantidad = N" (división) son el caso particular con Σ de los demás = 0 — una sola rama de código para los tres casos del enunciado.
4. **Iteración:** cada valor despejado pasa a los conocidos y puede destrabar otras ecuaciones. Se corta en la primera pasada que no produce nada nuevo (cota de seguridad: cantidad de Prácticas + 1).
5. **Confianza:** `Exacta` (división entera **y** todos los valores sustituidos exactos), `Estimada` (hubo redondeo `AwayFromZero` en algún punto de la cadena — el redondeo se **propaga**), `Inconsistente` (dos Perfiles despejan valores distintos para la misma Práctica: se muestran ambos y **no se sobreescribe** ninguno).
6. **Descartes:** valor despejado ≤ 0 (no es sugerencia válida, RN-26 pide ≥ 1); Perfiles con `Unidad = 0`, inactivos o eliminados; Prácticas que no participan de ninguna ecuación resoluble (esas ya las lista M24, sin dato).
7. **No escribe nada.** Ni la sugerencia ni un flag: la pantalla es de solo lectura y el usuario carga el valor a mano en Prácticas > Editar (mismo criterio que el backfill aproximado de `Unidad` de la sesión 3 y que PAT-013).

#### Decisiones de implementación y desvíos respecto al pedido
1. **Semilla con los valores ya cargados en la base** (`CantidadUnidades > 0`), no solo con los derivados. El enunciado hablaba de "un paso anterior"; se interpretó que un valor cargado por el cliente es el conocido más fuerte que existe, y es lo que más ecuaciones destraba (caso real: un Perfil con 2 componentes, uno ya cargado → el otro se despeja). Esos valores semilla **no** aparecen como sugerencia si ninguna ecuación los volvió a derivar.
2. **Detección de inconsistencia con ecuaciones ya determinadas.** Con la regla literal "exactamente una incógnita", el segundo Perfil que habla de la misma Práctica ya no tiene incógnitas y el conflicto pasaba desapercibido (verificado: el caso salía "Exacta" con un solo origen). Se agregó: una ecuación sin incógnitas funciona como **control** — si su Σ no da la `Unidad` guardada y exactamente **una** de sus Prácticas tiene valor *sugerido* (las demás son datos cargados por el cliente, que no se ponen en duda), se la re-despeja desde esa ecuación y aflora el conflicto. Si hay 2+ sugeridas, no se puede atribuir el desvío a ninguna y se deja pasar.
3. **Se incluyen componentes soft-deleted** (ver punto 1 del algoritmo) — el enunciado lo pedía explícitamente. La fila sale marcada con badge "Eliminada" porque para aplicar la sugerencia primero hay que reactivar la Práctica.
4. **Columnas extra sobre las 4 pedidas:** "Cargado hoy" (para ver de un vistazo si la sugerencia contradice un valor ya cargado) y la acción "Cargar a mano" (link al ABM, mismo patrón que la tabla de M24). **No hay guardado, ni individual ni masivo**, por diseño.
5. **Sin migración EF y sin cambios en entidades.** M25 es puramente derivado.

#### Verificación ejecutada
**Build:** `dotnet build LabIPAC.slnx --no-incremental` → **0 errores**, 9 warnings todos preexistentes (NU1902 MailKit/MimeKit, CS0114 `HomeController.StatusCode`). Las vistas Razor compilan en build (el proyecto no usa runtime compilation): se confirmó que el markup nuevo de `Diagnostico.cshtml` quedó embebido en `LabIPAC.Web.dll`, o sea que la vista bindea correctamente contra el VM extendido.

**Algoritmo (9/9 casos esperados):** harness temporal fuera del repo (scratchpad, no versionado) que referencia `LabIPAC.Infrastructure` y corre el servicio real contra una base MySQL **aislada** (`labipac_m25`, creada con `CREATE TABLE ... LIKE` de las 3 tablas involucradas y **eliminada al terminar**). 16 Perfiles / 15 Prácticas / 21 detalles cubriendo:

| Caso | Esperado | Resultado |
|------|----------|-----------|
| 1 componente × 1 | Exacta = 7 | ✅ |
| 1 componente × 4, Unidad 20 | Exacta = 5 | ✅ |
| 1 componente × 3, Unidad 10 | Estimada = 3 (redondeo) | ✅ |
| 2 componentes, uno despejado en una pasada previa | Exacta = 6 por sustitución | ✅ |
| 2 componentes, uno **ya cargado** en la base | Exacta = 5 | ✅ |
| Componente **soft-deleted** | Exacta = 5 + badge "Eliminada" | ✅ |
| Misma Práctica con 2 Perfiles que dan 9 y 11 | **Inconsistente**, ambos valores y ambos orígenes | ✅ |
| Cadena de 3 niveles (requiere 3 pasadas) | Exacta = 19 | ✅ |
| Componente que hereda de un valor estimado | **Estimada** = 7 (el redondeo se propaga) | ✅ |
| Perfil con `Unidad = 0` / resto negativo / Perfil inactivo / Perfil eliminado / Práctica sin Perfil / Práctica ya cargada | **sin sugerencia** | ✅ (no aparecen) |
| Regresión M24 sobre la misma base | 27 ítems, sin cambios de comportamiento | ✅ |

**Casos borde:** (a) base sin ningún Perfil con `Unidad > 0` → 0 filas, sin excepción; (b) Perfil sin componentes y Perfil con su único detalle soft-deleted → ecuación descartada, sin excepción; (c) `Cantidad` de la incógnita siempre > 0 por construcción (no hay división por cero).

**Datos reales:** corrida **read-only** contra `labipac_dev` → 0 sugerencias, como estaba previsto (el único Perfil, "Rutina", tiene `Unidad = 17` y **2 componentes sin dato** → 1 ecuación con 2 incógnitas, no resoluble). El reporte M24 devolvió los mismos 2 ítems de siempre. Se verificó después que `labipac_dev` quedó intacta (1 Perfil / 3 Prácticas / 2 detalles) y que las bases temporales fueron eliminadas.

**Sin smoke test funcional propio** (regla del rol): la guía de verificación manual queda abajo.

#### Guía de verificación manual (para el usuario/cliente)
1. Entrar como Administrador/SuperUsuario → sidebar **Precios por Centro** → botón/badge del **reporte de diagnóstico** (`/PreciosPorCentro/Diagnostico`).
2. Con la base como está hoy, la sección nueva **"Sugerencias de Cantidad de Unidades"** debe mostrar el aviso gris explicando que todavía no se puede despejar nada (falta al menos un Perfil con Unidad > 0 al que le quede una sola práctica sin dato).
3. Para verla funcionando: cargar la composición del Perfil "Rutina" con **una sola** práctica activa y guardar… **ojo**: al guardar, `Unidad` se recalcula (RN-33) y se pierde el valor histórico. Para probar sin destruir el dato, conviene hacerlo sobre un Perfil de prueba nuevo, o directamente esperar a Producción, donde hay Perfiles reales con `Unidad` histórica y composición cargada.
4. En Producción (después de aplicar la migración de la sesión 5): abrir la pantalla **antes de tocar nada** y revisar la tabla. Verificar contra el criterio del laboratorio: las filas "Exacta" deberían coincidir con lo que el bioquímico espera; las "Estimada" hay que revisarlas sí o sí; las "Inconsistente" indican que un Perfil tiene mal la `Unidad` o mal la composición.
5. Cargar los valores a mano desde **Prácticas > Editar > Cantidad de unidades**. La pantalla no guarda nada por sí sola: al volver a entrar, las filas ya cargadas aparecen con su valor en "Cargado hoy" y pueden destrabar sugerencias nuevas para el resto.

#### Riesgos y observaciones para QA
- **La sugerencia es un dato derivado, no una verdad.** Si un Perfil quedó con la `Unidad` desactualizada respecto de su composición real, la sugerencia arrastra ese error. Por eso no se persiste nada ni se ofrece "aplicar todo".
- **Ventana de tiempo (importante):** las ecuaciones dependen de que los Perfiles conserven su `Unidad` histórica. Como ya está documentado en RA-17, esa `Unidad` se pierde en cuanto el Perfil se edita, cambia el `CantidadUnidades` de un componente, **o cambia el `PrecioPorUnidad` global**. Conviene **abrir esta pantalla y anotar las sugerencias ANTES** de cualquiera de esas tres acciones en Producción.
- **Orden de carga:** cargar primero las sugerencias "Exacta" y volver a abrir la pantalla — cada valor cargado se usa como semilla y suele destrabar sugerencias nuevas.
- **Costo de la pantalla:** 2 consultas (Perfiles + composición) y resolución en memoria. Para el volumen de un laboratorio es despreciable; el corte por convergencia evita pasadas de más.
- La sección nueva es de **solo lectura y sin acciones de escritura**, con lo cual no agrega superficie de riesgo sobre M19–M24. Permisos: hereda el `[Authorize]` sin política que ya tenía `Diagnostico`.

#### Pendiente
- [ ] QA funcional de la pantalla extendida (incluir en el mismo pase de QA de M19–M24).
- [ ] Ejecutar el paso 4 de la guía manual **en Producción, antes de tocar precios o composiciones** (ventana de RA-17).
- [ ] Que el documentador incluya la pantalla en el documento de cliente del cambio de modelo de precios.

### Sesión 5 — Implementación M19→M24 (Precio por Unidad Bioquímica y por Perfil según Centro de Salud)
**Fecha:** 2026-08-23
**Estado:** ✅ BUILD OK (0 errores) — Migración generada y aplicada a `labipac_dev` — 39/39 verificaciones automáticas de servicio OK contra MySQL real — 17/17 pantallas renderizando 200 con la app corriendo

Input: `1-analista-funcional.md` sesión 6, `2-disenador-funcional.md` sesión 6, `3-arquitecto-mvc.md` sesión 6 (VERSION FINAL), `4-presupuestador.md` SESION 5 (M19–M24, 8.166h PERT, USD 132.72).

**Nota de gate:** el presupuesto quedó documentado pero **el gate de aprobación formal del cliente fue salteado por instrucción explícita del usuario del estudio** — se procedió directo a implementar. Queda registrado para trazabilidad.

#### 0. Escaneo de reutilización cross-proyecto
Se escaneó `C:/Sistemas/Agentes-IA/docs/*/definiciones/5-implementador.md` (20 proyectos) buscando dos patrones: **(a) "recálculo en cascada"** disparado por el cambio de un valor en una entidad hija hacia sus padres, y **(b) "un valor de configuración por fila padre"** (precio por cliente/sucursal/centro/lista).

**Resultado: sin coincidencias reutilizables.** Detalle de lo revisado:
- `crm-olvidata`: "cascada" es soft-delete manual campaña→industria→query (propagación de baja, no recálculo de un valor derivado).
- `la-platense`: `RecalcularClasificacionAbc` recorre TODAS las ventas de una ventana temporal (batch global, no consulta inversa por relación); además fue retirado de la rama que fue a producción.
- `marihogar` / `vinosefue`: recálculos de totales **dentro de un mismo agregado** (venta→items, pedido→items) o recálculo en cliente por JS. `RecalcularSnapshotComprasVinculadasAsync` (vinosefue) es lo más cercano conceptualmente (actualiza el padre al tocar el hijo) pero opera sobre un snapshot de costo con guard de estado, no sobre una relación M:N ni una fórmula de volumen.
- `ShowroomGriffin` / `koi`: "cascada" es combos dependientes en UI y proyección de KPIs, sin relación.
- Patrón (b): sin ningún proyecto con precio diferenciado por entidad padre.

**Decisión:** implementar desde cero dentro de labipac, reutilizando patrones **intra-proyecto** ya construidos: el recálculo batch atómico de `PracticaService.ActualizarPrecioPorUnidadAsync` (sesión 3) como molde para la cascada, y la card AJAX "Precio por Unidad" de `Practicas/Index.cshtml` (sesión 3, CU-08) como molde visual de la pantalla nueva WF-16. Esto confirma la estimación de M20 por encima del rango (sin floor de reutilización), tal como lo justificó el presupuestador.

#### Terminología (recordatorio): `Practica` (Domain) = "Perfil" en UI. `UnidadBioquimica` (Domain) = "Práctica" en UI.

#### Archivos creados

**Domain:**
- `LabIPAC.Domain/Entities/PrecioPorUnidadCentroSalud.cs` — hereda `SoftDestroyable`. FK `CentroSaludId` (índice único) + `Valor` decimal(18,2). Patrón de fila única **por centro**.

**Application:**
- `LabIPAC.Application/Interfaces/IPrecioPorUnidadCentroSaludService.cs` — `ObtenerVigenteAsync(int)`, `ListarPorCentroAsync()`, `ActualizarValorAsync(int, decimal)`, `AumentarPorcentajeAsync(int, decimal)`.
- `LabIPAC.Application/DTOs/PrecioPorUnidadCentroSaludDtos.cs` — `PrecioPorUnidadCentroSaludDto` + `DiagnosticoCatalogoItemDto` (M24).

**Infrastructure:**
- `LabIPAC.Infrastructure/Services/PrecioPorUnidadCentroSaludService.cs` — upsert por centro con reactivación de fila soft-deleted, aumento % con el mismo redondeo `AwayFromZero` de F-001/RN-19.

**Web:**
- `LabIPAC.Web/Controllers/PreciosPorCentroController.cs` — `Index` (WF-16), `ActualizarValor`/`AumentarPorcentaje` (AJAX), `Diagnostico` (M24).
- `LabIPAC.Web/Models/PreciosPorCentroViewModels.cs` — VM-19 + VMs del reporte de diagnóstico.
- `LabIPAC.Web/Views/PreciosPorCentro/Index.cshtml` y `Diagnostico.cshtml`.
- Migración `20260823230449_AddCantidadUnidadesYPrecioPorUnidadCentroSalud`.

#### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `LabIPAC.Domain/Entities/UnidadBioquimica.cs` | + `CantidadUnidades` (int, RN-26). `PrecioActual` pasa a documentarse como calculado (RN-32). |
| `LabIPAC.Domain/Entities/Practica.cs` | `Unidad` pasa a documentarse como CALCULADA por composición (RN-33); RN-02 marcada como reactivada. |
| `LabIPAC.Application/Interfaces/IUnidadBioquimicaService.cs` | Doc de RN-32 en `CreateAsync`/`UpdateAsync` + DD-09 (cascada) en `UpdateAsync`. Sin cambio de firma (la entidad transporta `CantidadUnidades`, mismo patrón que `IPracticaService` desde sesión 2). |
| `LabIPAC.Application/Interfaces/IPracticaService.cs` | + `RecalcularPorCambioDeCantidadUnidadesAsync(int)`, + `CalcularVolumenComposicionAsync(IList<int>)`, + `ObtenerDiagnosticoCatalogoAsync()`. Doc de RN-33/RN-02 reactivada. |
| `LabIPAC.Application/Interfaces/IProduccionMensualService.cs` | **`GetPrecioVigenteAsync(tipo, itemId)` → `GetPrecioVigenteAsync(tipo, itemId, int? centroSaludId)`** (bisagra RA-15). `CreateAsync` documenta RN-25 modificada. |
| `LabIPAC.Application/DTOs/UnidadBioquimicaDtos.cs` | `UnidadBioquimicaSummaryDto` + `CantidadUnidades`. |
| `LabIPAC.Infrastructure/Data/AppDbContext.cs` | + `DbSet<PrecioPorUnidadCentroSalud>` + Fluent config (índice único en `CentroSaludId`, FK Restrict); `UnidadBioquimica.CantidadUnidades` requerido con default 0. |
| `LabIPAC.Infrastructure/Services/UnidadBioquimicaService.cs` | Inyecta `IPracticaService`. `CreateAsync`/`UpdateAsync` calculan `PrecioActual = CantidadUnidades × PrecioPorUnidad` global. `UpdateAsync` compara el valor previo (query `AsNoTracking` contra la base, no `OriginalValue`) y **solo si cambió** dispara la cascada. |
| `LabIPAC.Infrastructure/Services/PracticaService.cs` | `CreateAsync`/`UpdateAsync`: RN-02 reactivada (rechazan composición vacía) y calculan `Unidad` desde la composición antes del precio. + `CalcularVolumenComposicionAsync`, + `RecalcularPorCambioDeCantidadUnidadesAsync` (consulta inversa + un único `SaveChangesAsync`), + `ObtenerDiagnosticoCatalogoAsync`, + privado `RecalcularUnidadYPrecioAsync` (una sola consulta para todo el conjunto, evita N+1). `ActualizarPrecioPorUnidadAsync` ahora recalcula **también** `Unidad` en el batch. |
| `LabIPAC.Infrastructure/Services/ProduccionMensualService.cs` | `GetPrecioVigenteAsync` reescrito con la nueva firma (RN-28/RN-29). `CreateAsync` rechaza `CentroSaludId == null` (RN-25 modificada) y se eliminó la rama muerta del mensaje de duplicado sin centro. |
| `LabIPAC.Infrastructure/DependencyInjection.cs` | + registro `IPrecioPorUnidadCentroSaludService` (Scoped). |
| `LabIPAC.Web/Controllers/UnidadesBioquimicasController.cs` | Inyecta `IPracticaService` (para el `PrecioPorUnidad` global). `Create`/`Edit` reciben `CantidadUnidades` en vez de `PrecioActual`. `GetData` + columna `cantidadUnidades` + ordenamiento por ella. |
| `LabIPAC.Web/Controllers/PracticasController.cs` | `Create`/`Edit` POST dejan de asignar `Unidad` desde el formulario. `BuildUnidadesDisponiblesAsync` agrega `CantidadUnidades` (0 para componentes inactivos/eliminados, coherente con el cálculo server-side). |
| `LabIPAC.Web/Controllers/ProduccionMensualController.cs` | Inyecta `IPrecioPorUnidadCentroSaludService`. `GetPrecioItem` recibe `produccionId` y resuelve el centro **server-side** (RA-15) + `ConstruirMensajeBloqueoPrecioAsync` (mensajes accionables, DD-07). `Detalle` y `ConstruirCargaMasivaViewModelAsync` resuelven el multiplicador por centro (antes usaba siempre el global — corrección de RA-15). `CrearPerfilRapido` recibe `UnidadBioquimicaIds`; `CrearPracticaRapido` recibe `CantidadUnidades`. |
| `LabIPAC.Web/Models/UnidadBioquimicaViewModels.cs` | `PrecioActual` deja de ser campo de entrada; + `CantidadUnidades` (`[Range(1, int.MaxValue)]`) y `PrecioPorUnidadVigente` (solo lectura). Row VM + `CantidadUnidades`. |
| `LabIPAC.Web/Models/PracticaViewModels.cs` | `Unidad` pasa a solo lectura (sin `[Required]`/`[Range]` de entrada); `UnidadBioquimicaIds` vuelve a `[Required, MinLength(1)]` (RN-02). `UnidadBioquimicaSelectItem` + `CantidadUnidades`. |
| `LabIPAC.Web/Models/ProduccionMensualViewModels.cs` | `CentroSaludId` pasa a `[Required]`. Carga masiva y Detalle + `NombreCentroSalud`/`TieneCentroSalud`/`PrecioUnidadBioquimicaVigente`; carga masiva + `UnidadesParaComposicion`. `PerfilAltaRapidaViewModel`: `Unidad` → `UnidadBioquimicaIds`. `PracticaAltaRapidaViewModel`: `PrecioActual` → `CantidadUnidades`. |
| `LabIPAC.Web/Views/UnidadesBioquimicas/{Create,Edit}.cshtml` | Campo `CantidadUnidades` editable; precio de referencia solo lectura calculado en vivo por JS. |
| `LabIPAC.Web/Views/UnidadesBioquimicas/Index.cshtml` | + columna "Cantidad de unidades" con badge rojo "Sin cargar" si es 0 (RA-17); "Precio actual" → "Precio referencia". |
| `LabIPAC.Web/Views/Practicas/{Create,Edit}.cshtml` | Composición pasa a obligatoria (rótulo en rojo); `Unidad` pasa a input `readonly disabled` calculado en vivo por JS desde la composición. |
| `LabIPAC.Web/Views/Practicas/Index.cshtml` | Columna Unidad con badge "Sin calcular" si es 0 (RA-17); texto de la card aclara que el precio de facturación sale del centro, con link a WF-16. |
| `LabIPAC.Web/Views/ProduccionMensual/Create.cshtml` | Se quitó la opción "Sin centro asignado (global)"; aviso si no hay centros activos. |
| `LabIPAC.Web/Views/ProduccionMensual/{Detalle,CargaMasiva}.cshtml` | Banner de centro + precio de unidad vigente (3 estados: cargado / sin cargar / histórico sin centro). `GetPrecioItem` pasa `produccionId`. Bloqueo visual de la línea/botón cuando el precio no es calculable (DD-07). |
| `LabIPAC.Web/Views/ProduccionMensual/_ModalAltaRapidaPerfil.cshtml` | Modelo `decimal` → `List<UnidadBioquimicaSelectItem>`. Campo "Unidad" reemplazado por Select2 de composición obligatoria + preview de Unidad calculada. |
| `LabIPAC.Web/Views/ProduccionMensual/_ModalAltaRapidaPractica.cshtml` | Campo "Precio actual" reemplazado por "Cantidad de unidades" + preview del precio en el centro del período. |
| `LabIPAC.Web/Views/Shared/_Layout.cshtml` | + entrada de sidebar "Precios por Centro" (dentro del bloque ya restringido a SuperUsuario/Administrador). |

**`PreciosController.cs` (F-001): NO se tocó**, según lo confirmado en Diseño y Arquitectura (RA-16).

#### Migración EF generada y aplicada
- Nombre: `20260823230449_AddCantidadUnidadesYPrecioPorUnidadCentroSalud`
- `ALTER TABLE UnidadesBioquimicas ADD COLUMN CantidadUnidades int NOT NULL DEFAULT 0`
- `CREATE TABLE PreciosPorUnidadCentroSalud` (Id, CentroSaludId int + FK Restrict + **índice único**, Valor decimal(18,2), + columnas estándar `SoftDestroyable`)
- **SIN backfill** de `CantidadUnidades` ni seed de `PreciosPorUnidadCentroSalud` (R-PC1/DD-06/RA-13 — instrucción explícita: carga manual del cliente).
- **Estado: APLICADA** a `labipac_dev`. Verificado con `mysqlsh` contra la base real: columna presente (`int NOT NULL default 0`), tabla creada, índice único `IX_PreciosPorUnidadCentroSalud_CentroSaludId` presente, `__EFMigrationsHistory` con la migración registrada, y datos preexistentes intactos.
- Riesgo de rollback: **bajo** (columna nueva con default + tabla nueva; el `Down` las quita sin tocar datos existentes).
- Pendiente: aplicar a Producción en el próximo deploy.

#### Reglas de negocio implementadas
- **RN-26**: `UnidadBioquimica.CantidadUnidades` entero obligatorio >= 1 (DataAnnotation en el VM; el Service admite 0 para no romper las filas migradas con default 0).
- **RN-27**: fila única de precio por `CentroSaludId`, valor >= 0 (Service + índice único).
- **RN-28**: precio en período CON centro = volumen × precio de unidad del centro; bloqueo con `null` si el centro no tiene valor cargado (a) o el ítem no tiene volumen calculable (b).
- **RN-29**: período histórico SIN centro → precio de referencia de catálogo, comportamiento idéntico al previo.
- **RN-30**: alta rápida de Práctica pide `CantidadUnidades`; alta rápida de Perfil pide composición.
- **RN-31**: el precio de referencia global y los precios por centro son independientes; no se sincronizan.
- **RN-32**: `UnidadBioquimica.PrecioActual` calculado, ya no de entrada.
- **RN-33**: `Practica.Unidad = Σ (PracticaDetalle.Cantidad × UnidadBioquimica.CantidadUnidades)` de componentes activos.
- **RN-02 REACTIVADA** (revierte la relajación global de sesión 3): composición obligatoria en ABM completo **y** alta rápida.
- **RN-14 DEROGADA**: el alta rápida ya no puede omitir composición.
- **RN-25 modificada**: `CentroSaludId` obligatorio en altas nuevas de período; los NULL históricos no se migran ni se bloquean.
- **DD-09/RA-18**: recálculo en cascada por consulta inversa desde `PracticaDetalle`.

#### Permisos
- `[Authorize(Policy = "RequireAdministracion")]`: `PreciosPorCentro/Index`, `ActualizarValor`, `AumentarPorcentaje` — mismo criterio que F-001/IVA/`ActualizarPrecioPorUnidad`.
- `[Authorize]` sin política: `PreciosPorCentro/Diagnostico` (solo lectura, sin acciones destructivas) y todo lo preexistente sin cambios.
- Sidebar: "Precios por Centro" dentro del bloque ya condicionado a `SuperUsuario`/`Administrador`.

#### Decisiones de implementación y desvíos respecto a la arquitectura
1. **Interfaz propia `IPrecioPorUnidadCentroSaludService`** en vez de agregar los métodos a `IPracticaService` (la arquitectura dejaba ambas opciones abiertas). Razón: a diferencia del `PrecioPorUnidad` global, este valor **no** dispara recálculo del catálogo (RN-31) y su consumidor real es Producción Mensual, no Prácticas — meterlo en `IPracticaService` habría mezclado dos ciclos de vida distintos.
2. **Detección del cambio de `CantidadUnidades`** en `UnidadBioquimicaService.UpdateAsync` vía query `AsNoTracking` contra la base, no vía `ChangeTracker.OriginalValue`. Razón: el Controller muta una entidad ya trackeada obtenida con `GetByIdAsync`; una consulta `AsNoTracking` devuelve el valor realmente persistido y funciona igual si la entidad llegara desacoplada. Sin esto, editar solo el nombre reescribiría N Perfiles innecesariamente (verificado con test explícito).
3. **`ActualizarPrecioPorUnidadAsync` ahora recalcula también `Unidad`**, no solo `PrecioActual` (Arquitectura línea 25 lo pide explícitamente). **Consecuencia a vigilar (ver Riesgos):** un cambio del precio global recalcula la `Unidad` de todos los Perfiles activos, y los que tengan composición incompleta caen a 0.
4. **`UnidadBioquimica.PrecioActual` NO se incluye en el recálculo batch por cambio del `PrecioPorUnidad` global** (solo se calcula en su propio Create/Update). Razón: F-001 (`PreciosController`, que no se toca) sigue escribiendo `UnidadBioquimica.PrecioActual` directo en su aumento masivo; incluirlo en el batch global pisaría silenciosamente ese aumento. Es una decisión de **preservación de comportamiento legacy**, no un olvido.
   > ⚠️ **REVERTIDA el 2026-08-24 (Sesión 6).** QA-S3-02 mostró que el efecto colateral (precio de referencia desfasado, dos números para el mismo concepto) pesaba más que la preservación. El usuario del estudio decidió retirar F-001 por completo, con lo que `UnidadBioquimica.PrecioActual` pasa a tener un único escritor (la fórmula RN-32) y **sí** entra al batch global.
5. **Criterio de "componente activo" para RN-33**: solo suman los componentes cuya `UnidadBioquimica` está activa y no eliminada. Alineado con RA-01 revertido ("dar de baja una UnidadBioquimica reduce el volumen del Perfil en el próximo recálculo"). La sumatoria informativa en $ sigue usando `IgnoreQueryFilters()` y mostrando el badge — son dos conceptos distintos y se documentó así en el código.
6. **`ConstruirMensajeBloqueoPrecioAsync`** (nuevo, en el Controller): DD-07 pedía un aviso "explícito y accionable". Distingue las 3 causas de bloqueo **después** de que el Service ya devolvió `null` — no duplica la decisión de negocio, solo la explica. Se mantuvo en el Controller por ser exclusivamente presentación.
7. **M24 alojado en `PreciosPorCentroController.Diagnostico`** (la arquitectura dejaba abierto dónde ponerlo). Razón: es el punto del flujo donde el cliente descubre que le falta cargar datos; se linkea desde la propia pantalla WF-16 con un badge de conteo.

#### Verificación ejecutada

**Build:** `dotnet build LabIPAC.slnx --no-incremental` → **0 errores**. 9 warnings, todos preexistentes (NU1902 MailKit/MimeKit, CS0114 `HomeController.StatusCode`); ninguno introducido en esta sesión.

**Verificación automática de servicios (39/39 OK):** se construyó un harness temporal fuera del repo (scratchpad, no versionado) que referencia `LabIPAC.Infrastructure` y corre contra una base MySQL **aislada** (`labipac_verif`, creada aplicando toda la cadena de migraciones desde cero y eliminada al terminar). Cubre: M19 (precio calculado desde `CantidadUnidades`), M20 (RN-02 rechaza composición vacía; `Unidad` = 5+3 = 8; precio 800), cascada DD-09 (5→10 ⇒ Perfil pasa a Unidad 13 / precio 1300; editar solo el nombre NO dispara cascada), M21 (2 centros con valores distintos, aumento 10% en A no afecta a B, upsert sin violar el índice único, aumento % sobre centro sin valor rechazado), M22 (las 4 fórmulas + los 3 casos de bloqueo + RN-29 + ítem inexistente + período sin centro rechazado + RN-24), RN-29 sobre un histórico NULL simulado, M24 y la regresión del recálculo batch global.

**Verificación end-to-end con la app corriendo (`dotnet run`, login real, cookies + antiforgery):**
- **17/17 pantallas devuelven HTTP 200** y renderizan (incluidas las 2 nuevas y todas las modificadas). Confirma que las vistas Razor compilan y bindean con los VMs nuevos.
- `GetPrecioItem` contra **datos reales de `labipac_dev`**, antes de cargar nada: período con centro → bloqueo con el mensaje del centro sin precio; período histórico sin centro → `{"success":true,"precio":15619.43}` (**RN-29 confirmada contra el dato preexistente real**); práctica con `CantidadUnidades=0` (default de la migración) → bloqueo accionable.
- Flujo completo WF-16: cargar $1000 en el centro → aumento 15% → $1150; luego cargar `CantidadUnidades=4` en la práctica real → los precios pasan a calcularse (perfil 19550, práctica 4600) y el histórico sin centro sigue devolviendo su precio de referencia sin cambios.
- RN-02 en el ABM completo: POST sin composición → HTTP 200 (se queda en el formulario), mensaje de validación renderizado, **y nada creado en la base** (verificado por query).
- M23: alta rápida de Perfil sin composición → `{"success":false,...}`; con composición → crea con `unidad` calculada; alta rápida de Práctica → crea con `cantidadUnidades`.
- M22: POST de período nuevo sin centro → se queda en el formulario con "El Centro de Salud es obligatorio."
- M24: el reporte, corrido sobre datos reales, detecta correctamente el Perfil "Rutina" como "Sin composición" (sus 2 componentes apuntan a `UnidadBioquimica` soft-deleted) — es exactamente el caso RA-17.

**Datos de prueba:** los registros creados durante la verificación (`Perfil rapido QA`, `Practica rapida QA` y su detalle) fueron **eliminados** de `labipac_dev`. La base `labipac_verif` fue **eliminada**. Quedan en `labipac_dev` dos valores de configuración cargados durante la prueba, **arbitrarios y no representativos**, que QA/el cliente deben ajustar: `PreciosPorUnidadCentroSalud` del centro 3 = $1150,00 y `UnidadesBioquimicas.Id=3.CantidadUnidades = 4`.

#### Riesgos y observaciones para QA
- **RA-17 (crítico, confirmado con datos reales):** el Perfil "Rutina" de `labipac_dev` conserva `Unidad = 17` (valor heredado del backfill de sesión 3) aunque sus 2 componentes están soft-deleted. **Los Perfiles existentes NO se recalculan retroactivamente por la migración** (no hay backfill, por instrucción): mantienen su `Unidad` heredada — y por lo tanto cotizan con ella — hasta que algo los toque. Caen a `Unidad = 0` (precio $0) en cuanto ocurra cualquiera de: (a) alguien los edite y guarde, (b) cambie el `PrecioPorUnidad` global (el batch ahora también recalcula `Unidad` — ver decisión 3), (c) cambie el `CantidadUnidades` de un componente suyo. **El caso (b) puede dispararse sin que nadie toque el Perfil**: conviene relevar con el reporte M24 y completar composiciones ANTES de tocar el precio global en Producción.
- **RA-15 (bisagra):** se revisaron **todos** los callers de `GetPrecioVigenteAsync` (eran 1: `GetPrecioItem`) y también el caller indirecto que la arquitectura marcó como incorrecto (`ConstruirCargaMasivaViewModelAsync`, que usaba `ObtenerPrecioPorUnidadVigenteAsync()` global — corregido). `grep` posterior confirma que no queda ningún uso del multiplicador global en rutas de producción por centro. El compilador forzó la revisión al cambiar la firma.
- **RA-13/DD-06:** `CantidadUnidades` queda en 0 para todas las prácticas existentes y `PreciosPorUnidadCentroSalud` nace vacía. Hasta que el cliente los cargue, **el sistema bloquea el alta de líneas en períodos con centro** con mensaje accionable (comportamiento deseado, DD-07 — no es un bug).
- **Períodos históricos con `CentroSaludId = NULL`:** verificados intactos y funcionando igual que antes (lectura, edición de notas y cotización con precio de referencia). No se migraron ni se tocaron.

#### Pendiente
- [ ] QA funcional formal de M19–M24 según las pruebas mínimas de `4-presupuestador.md` SESION 5, con foco en M20 (cascada) y M22 (bisagra de precio).
- [ ] Carga de datos del cliente: `CantidadUnidades` de cada Práctica activa y "Precio de Unidad Bioquímica" de cada Centro de Salud (usar el reporte de diagnóstico como checklist).
- [ ] Relevamiento y corrección de los Perfiles listados por M24 **antes** de operar en Producción (RA-17).
- [ ] Aplicar la migración `AddCantidadUnidadesYPrecioPorUnidadCentroSalud` a Producción en el próximo deploy.
- [ ] Ajustar/limpiar en `labipac_dev` los 2 valores arbitrarios de prueba indicados arriba.
- [ ] Documento de cliente (documentador) del cambio de modelo de precios.

### Sesión 4 — Implementación M10+M11+M12 (Produccion Mensual por Centro de Salud)
**Fecha:** 2026-07-23
**Estado:** ✅ BUILD OK — Migración generada y aplicada exitosamente a la base de desarrollo local (`labipac_dev`)

**Nota operativa:** el subagent delegado (`agentes-ia-implementador`, ejecutado como agente en background) se cortó a mitad de la verificación manual por haber alcanzado el limite de gasto mensual de la cuenta de Claude (error de API, no un fallo de codigo). El orquestador retomo el trabajo directamente: revisó todo el diff generado antes del corte, corrió `dotnet build` (OK, 0 errores nuevos), verificó contra la base real (`mysqlsh`) que la migracion estaba aplicada y que los datos de prueba dejados por el subagent confirmaban la regla RN-24 (3 períodos para el mismo Mes+Año: 2 con distinto CentroSaludId + 1 global, todos coexistiendo sin conflicto), y limpió los datos de prueba (`Centro Salud Test A/B` y los 3 períodos de prueba Mayo 2031) y el log de debug (`run_app.log`) que quedaron en el working tree.

**Cambio:** Implementado el alcance completo de M10 (ABM `CentroSalud`), M11 (`CentroSaludId` en `ProduccionMensual` + RN-24 + selector + columna en listado) y M12 (Centro de Salud en encabezado del PDF), según diseño/arquitectura de sesión 2026-07-23.

**Archivos nuevos:**
- `LabIPAC.Domain/Entities/CentroSalud.cs`, `LabIPAC.Domain/Enums/TipoCentroSalud.cs`
- `LabIPAC.Application/Interfaces/ICentroSaludService.cs`
- `LabIPAC.Infrastructure/Services/CentroSaludService.cs`
- `LabIPAC.Web/Controllers/CentrosSaludController.cs`, `LabIPAC.Web/Models/CentroSaludViewModels.cs`
- `LabIPAC.Web/Views/CentrosSalud/{Index,Create,Edit}.cshtml`
- Migración `20260723214415_AddCentroSaludYProduccionMensualCentroSalud` (tabla `CentrosSalud`, columna nullable `CentroSaludId` + FK Restrict en `ProduccionMensuales`, sin backfill)

**Archivos modificados:**
- `LabIPAC.Domain/Entities/ProduccionMensual.cs` (+`CentroSaludId`, +nav `CentroSalud`)
- `LabIPAC.Application/Interfaces/IProduccionMensualService.cs` (doc de RN-24/RN-25)
- `LabIPAC.Infrastructure/Services/ProduccionMensualService.cs` (`CreateAsync` valida RN-24 unicidad Mes+Año+CentroSaludId y RN-25 centro activo; `GetAllAsync`/`GetByIdAsync` +`Include(CentroSalud)`)
- `LabIPAC.Infrastructure/Data/AppDbContext.cs` (+`DbSet<CentroSalud>`, Fluent config)
- `LabIPAC.Infrastructure/DependencyInjection.cs` (+registro `ICentroSaludService`)
- `LabIPAC.Web/Controllers/ProduccionMensualController.cs` (Create GET/POST con selector de centro, GetData +`nombreCentroSalud`, `ReportePdf` +línea condicional de encabezado)
- `LabIPAC.Web/Models/ProduccionMensualViewModels.cs` (+`CentroSaludId`/`CentrosSaludDisponibles` en Create VM, +`NombreCentroSalud` en Row VM)
- `LabIPAC.Web/Views/ProduccionMensual/Create.cshtml` (selector), `Index.cshtml` (columna), `Views/Shared/_Layout.cshtml` (+entrada sidebar)

**Build:** OK, 0 errores (mismos warnings preexistentes de NuGet — MailKit/MimeKit — y CS0114 de HomeController, ninguno introducido por esta sesión).

**Migración EF:** generada y **aplicada exitosamente** a `labipac_dev`. Verificado contra la base real: tabla `CentrosSalud` creada, columna `ProduccionMensuales.CentroSaludId` presente, `__EFMigrationsHistory` confirma la migración aplicada. Pendiente aplicar a Producción en el próximo deploy.

**Desvíos respecto al plan de Arquitectura:** el memo de arquitectura mencionaba DTOs de creación (`CentroSaludCreateDto`, etc.) — la implementación real siguió el patrón vigente del repo (Controller arma la entidad directo, Service recibe la entidad), consistente con `UnidadBioquimica`/`ProduccionMensual` existentes. No se crearon DTOs nuevos, es una simplificación correcta respecto al patrón real, no una desviación de riesgo.

**Riesgos/supuestos:** ninguno nuevo. Períodos históricos quedan con `CentroSaludId = NULL` según lo definido en Análisis (P13), sin backfill.

**Estado:** IMPLEMENTACIÓN CERRADA (build OK, migración aplicada y verificada contra base real, RN-24 verificada con datos reales de prueba — luego eliminados). Pendiente: QA funcional formal, aplicar migración en Producción, documento de cliente.

### Sesión 3 — Implementación M7+M8+M9 (Unidad/PrecioPorUnidad, Carga masiva + alta rápida, fix PDF)
**Fecha:** 2026-07-08
**Estado:** ✅ BUILD OK — Migración generada, aplicada exitosamente a la base de desarrollo local (`labipac_dev`)

Input: `1-analista-funcional.md` sesión 4, `2-disenador-funcional.md` sesión 2, `3-arquitecto-mvc.md` sesión 2, `4-presupuestador.md` SESIÓN 3 — todos cerrados y aprobados. Presupuesto aprobado por el cliente; se implementó todo el alcance en una sola pasada (Etapa 1 M7+M9 / Etapa 2 M8 solo a efectos de facturación, sin dividir la entrega técnica).

#### 0. Escaneo de reutilización
Se escaneó `C:/Sistemas/Agentes-IA/docs/*/definiciones/5-implementador.md` buscando patrones "fila única" / "PrecioPorUnidad" / "valor global de configuración" en otros proyectos del estudio: sin coincidencias cross-proyecto. Decisión: implementar desde cero dentro de labipac, reutilizando el patrón visual+AJAX intra-proyecto ya existente ("IVA del período" en `Views/ProduccionMensual/Detalle.cshtml`, F-002) para la nueva card "Precio por Unidad" en `Views/Practicas/Index.cshtml`.

#### Terminología (recordatorio): `Practica` (Domain) = "Perfil" en UI. `UnidadBioquimica` (Domain) = "Práctica" en UI.

#### Archivos creados

**Domain:**
- `LabIPAC.Domain/Entities/PrecioPorUnidad.cs` — hereda `SoftDestroyable`, `Valor decimal`. Patrón de fila única (enforced en `PracticaService`, no en DB).

**Web:**
- `LabIPAC.Web/Views/ProduccionMensual/CargaMasiva.cshtml` — pantalla nueva de carga masiva (filas dinámicas JS, un submit).
- `LabIPAC.Web/Views/ProduccionMensual/_ModalAltaRapidaPerfil.cshtml` — partial, modelo `decimal` (PrecioPorUnidadVigente).
- `LabIPAC.Web/Views/ProduccionMensual/_ModalAltaRapidaPractica.cshtml` — partial.

#### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `LabIPAC.Domain/Entities/Practica.cs` | + `public int Unidad { get; set; }`. Comentarios actualizados (RN-01 derogada, RN-02 relajada, RN-16). |
| `LabIPAC.Application/Interfaces/IPracticaService.cs` | + `ObtenerPrecioPorUnidadVigenteAsync()`, `ActualizarPrecioPorUnidadAsync(decimal)`, `AumentarPrecioPorUnidadPorcentajeAsync(decimal)`. `CreateAsync`/`UpdateAsync` sin cambio de firma (siguen recibiendo `Practica` + `IList<int>`), pero ahora la entidad trae `Unidad` y el precio se calcula internamente. |
| `LabIPAC.Application/Interfaces/IProduccionMensualService.cs` | + `AgregarLineasAsync(int, IEnumerable<ProduccionDetalleLineaDto>)`. |
| `LabIPAC.Application/DTOs/PracticaDtos.cs` | `PracticaSummaryDto` + campo `Unidad`. |
| `LabIPAC.Application/DTOs/ProduccionMensualDtos.cs` | + `ProduccionDetalleLineaDto` (TipoItem, ItemId, Cantidad, PrecioSnapshot). |
| `LabIPAC.Infrastructure/Data/AppDbContext.cs` | + `DbSet<PrecioPorUnidad> PreciosPorUnidad` + Fluent config (`Valor` decimal(18,2)). |
| `LabIPAC.Infrastructure/Services/PracticaService.cs` | RN-02 (mínimo 1 componente) eliminada de `CreateAsync`/`UpdateAsync`. Ambos calculan `PrecioActual = Unidad * PrecioPorUnidad vigente` antes de persistir. + 3 métodos nuevos (`ObtenerPrecioPorUnidadVigenteAsync`, `ActualizarPrecioPorUnidadAsync` con recálculo batch en un único `SaveChangesAsync`, `AumentarPrecioPorUnidadPorcentajeAsync` con redondeo `AwayFromZero` igual criterio que F-001). |
| `LabIPAC.Infrastructure/Services/ProduccionMensualService.cs` | + `AgregarLineasAsync`: valida ítem activo/existente, cantidad >=1, sin duplicados dentro del batch (RN-13) ni contra líneas ya existentes del período (RN-04 heredada); `AddRangeAsync` + único `SaveChangesAsync` (atomicidad). |
| `LabIPAC.Web/Controllers/PracticasController.cs` | `Index` pasa `ViewBag.PrecioPorUnidadVigente` + `ViewBag.CantidadPerfilesActivos`. `Create`/`Edit` GET pasan `PrecioPorUnidadVigente`. POST ya no reciben `PrecioActual`, reciben `Unidad`. + acciones AJAX `ActualizarPrecioPorUnidad` y `AumentarPrecioPorUnidadPorcentaje` (`[Authorize(Policy = "RequireAdministracion")]`). `GetData` agrega campo `unidad`. |
| `LabIPAC.Web/Controllers/PreciosController.cs` | **Simplificado**: se eliminó toda la lógica de cascade UB→Perfil y de "Perfiles seleccionados directamente" en `AumentoMasivo`, `Previsualizar`, `AplicarAumento`. Ahora opera solo sobre `UnidadBioquimica`. |
| `LabIPAC.Web/Controllers/ProduccionMensualController.cs` | + `CargaMasiva` (GET/POST), `CrearPerfilRapido` (AJAX, reusa `IPracticaService.CreateAsync`), `CrearPracticaRapido` (AJAX, reusa `IUnidadBioquimicaService.CreateAsync`) — las 3 con `[Authorize]` de clase sin política, igual que `AgregarLinea`. `ReportePdf`: `ConstantColumn(55)`→`75` (Precio unit.), `ConstantColumn(65)`→`60` (Tipo). |
| `LabIPAC.Web/Models/PracticaViewModels.cs` | `PracticaCreateViewModel`: quita `PrecioActual`, agrega `Unidad` (`[Range(1,int.MaxValue)]`) y `PrecioPorUnidadVigente` (solo lectura). `PracticaRowViewModel` + `Unidad`. + `PrecioPorUnidadViewModel` (VM-16, definido para trazabilidad de diseño; los endpoints AJAX reales usan parámetros primitivos siguiendo el mismo patrón que `ActualizarIva` existente). |
| `LabIPAC.Web/Models/ProduccionMensualViewModels.cs` | + `ProduccionCargaMasivaViewModel`, `ProduccionCargaMasivaFilaViewModel`, `PerfilAltaRapidaViewModel`, `PracticaAltaRapidaViewModel`. |
| `LabIPAC.Web/Models/PreciosViewModels.cs` | `AumentoMasivoViewModel` quita `PerfilesSeleccionados`. |
| `LabIPAC.Web/Views/Practicas/Index.cshtml` | + card "Precio por Unidad" (mismo patrón visual/AJAX que card IVA de F-002, con SweetAlert2 de confirmación mostrando cantidad de perfiles activos afectados). + columna "Unidad". "Precio actual" → "Precio (calculado)" solo lectura. Se quitó el badge de advertencia RN-01 (derogada). |
| `LabIPAC.Web/Views/Practicas/Create.cshtml` / `Edit.cshtml` | Se quitó el campo "Precio actual" editable y el aviso RN-01. Se agregó campo "Unidad" (entero >=1) + texto "Precio calculado: $ X" recalculado en vivo por JS. Composición (Select2) se mantiene como informativa/opcional. |
| `LabIPAC.Web/Views/Precios/AumentoMasivo.cshtml` | Se quitó el tab "Perfiles" y toda su tabla/JS asociada (incluida en el panel de previsualización). Se agregó nota informativa sobre el nuevo mecanismo de precio de Perfiles. Solo queda la tabla de Prácticas (UnidadBioquimica). |
| `LabIPAC.Web/Views/ProduccionMensual/Detalle.cshtml` | + botón "Carga masiva" (btn-outline-primary) junto a "Agregar ítem", enlaza a `CargaMasiva/{id}`. |

#### Migración EF generada y aplicada
- Nombre: `AddPracticaUnidadYPrecioPorUnidad` (`20260708175303_AddPracticaUnidadYPrecioPorUnidad`)
- Cambios de esquema: `ALTER TABLE Practicas ADD COLUMN Unidad int NOT NULL DEFAULT 0`; `CREATE TABLE PreciosPorUnidad` (Id, Valor decimal(18,2) + columnas estándar SoftDestroyable).
- Seed: `InsertData` — 1 fila `Id=1, Valor=892.03`.
- **Backfill de datos ejecutado** (RA-06, riesgo crítico mitigado): `UPDATE Practicas SET Unidad = GREATEST(1, CAST(ROUND(PrecioActual / 892.03) AS SIGNED)) WHERE DeletedAt IS NULL;` vía `migrationBuilder.Sql(...)` en el método `Up`.
- **Estado: APLICADA** a `labipac_dev` (localhost MySQL). Verificado post-aplicación vía `mysqlsh`: `PreciosPorUnidad` tiene la fila seed (Id=1, Valor=892.03); columna `Practicas.Unidad` existe (int NOT NULL default 0); backfill correcto en datos reales (ej. Perfil "Rutina" PrecioActual=$15000.00 → Unidad=17, consistente con `ROUND(15000/892.03)=17`).
- Pendiente: aplicar la misma migración al ambiente de Producción cuando se despliegue (usa `appsettings.Production.json`, credenciales ya configuradas ahí — no se tocó ese ambiente en esta sesión).

#### Reglas de negocio implementadas
- RN-16: `Practica.PrecioActual = Unidad * PrecioPorUnidad.Valor vigente`, recalculado en `CreateAsync`/`UpdateAsync` y en recálculo batch.
- RN-17: `Unidad` entero, obligatorio, >= 1 (DataAnnotation + Domain).
- RN-18: `PrecioPorUnidad.Valor` obligatorio, >= 0 (validado en `ActualizarPrecioPorUnidadAsync`).
- RN-19: aumento % con `Math.Round(valorActual * (1 + pct/100m), 2, MidpointRounding.AwayFromZero)` (mismo criterio que F-001).
- RN-20: RN-01 derogada (ya no se valida `PrecioActual < SumatoriaComponentes`; nunca existió como bloqueo server-side, solo era un aviso JS en las vistas — removido).
- RN-02 relajada GLOBALMENTE (no solo alta rápida, decisión de arquitectura confirmada en presupuesto): `UnidadBioquimicaIds` ya no exige mínimo 1 en ningún flujo (ABM completo ni alta rápida).
- RN-12/RN-13: `AgregarLineasAsync` atómico (un único `SaveChangesAsync`), sin duplicados TipoItem+ItemId dentro del envío ni contra líneas ya existentes del período.
- RN-21 / simplificación F-001: `PreciosController` ya no opera sobre Perfiles (Practica), solo sobre Prácticas (UnidadBioquimica).

#### Permisos
- `[Authorize(Policy = "RequireAdministracion")]`: `ActualizarPrecioPorUnidad`, `AumentarPrecioPorUnidadPorcentaje` (PracticasController) — mismo criterio que F-001/IVA.
- `[Authorize]` sin política: `CargaMasiva`, `CrearPerfilRapido`, `CrearPracticaRapido` (ProduccionMensualController) — igual que ABM/`AgregarLinea` existentes.
- `PreciosController` mantiene `[Authorize(Policy = "RequireAdministracion")]` a nivel de clase, sin cambios.

#### Desvíos respecto a la arquitectura documentada
- Ninguno relevante. Un detalle menor: `PrecioPorUnidadViewModel` (VM-16) quedó definido en `PracticaViewModels.cs` para trazabilidad de diseño, pero los endpoints AJAX reales (`ActualizarPrecioPorUnidad`, `AumentarPrecioPorUnidadPorcentaje`) usan parámetros primitivos (`decimal nuevoValor` / `decimal porcentaje`) en lugar de bindear ese VM completo, replicando exactamente el patrón ya usado por `ActualizarIva(int, decimal?)` en `ProduccionMensualController` (consistencia con convención existente, sin agregar una capa de binding adicional).

#### Pendiente
- [ ] Aplicar la migración `AddPracticaUnidadYPrecioPorUnidad` a Producción en el próximo deploy.
- [x] QA funcional de los 3 módulos (M7, M8, M9) según pruebas mínimas de `4-presupuestador.md` SESIÓN 3. (QA SESIÓN 2, sin bloqueantes; ver Sesión 4 para los 3 hallazgos de UI reportados por el cliente en pruebas manuales posteriores).
- [ ] Revisión manual por el cliente de los valores de `Unidad` backfilleados en Perfiles existentes (aproximación automática, confirmada como tarea post-deploy del cliente).

---

### Sesión 4 — Fix de 3 hallazgos de UI reportados por el cliente (pruebas manuales post M7+M8+M9)
**Fecha:** 2026-07-08
**Estado:** ✅ BUILD OK — Los 3 hallazgos corregidos y verificados en vivo contra `labipac_dev`

Input: el cliente ejecutó las pruebas manuales de UI pendientes tras el sprint M7+M8+M9 y reportó 3 hallazgos concretos. Se clasificaron como completions/fixes de bajo esfuerzo dentro del alcance ya aprobado (no alcance nuevo), resueltos directo sin nuevo ciclo de Presupuesto, según pedido explícito del orquestador/cliente.

#### 0. Escaneo de reutilización
No aplica: son fixes puntuales sobre código ya implementado en esta misma sesión de trabajo del proyecto (Sesión 3), no una funcionalidad nueva a buscar en otros proyectos del estudio.

#### Hallazgo 1 — `Practicas/Details.cshtml` no mostraba el campo `Unidad`
- **Causa raíz:** `PracticaDetailsViewModel` nunca tuvo la propiedad `Unidad` (quedó fuera al agregar el campo `Practica.Unidad` en la Sesión 3, ya que Details no formaba parte del alcance original de esa sesión); por lo tanto `PracticasController.Details` tampoco la mapeaba ni la vista la mostraba.
- **Fix:** se agregó `public int Unidad { get; set; }` a `PracticaDetailsViewModel` (`LabIPAC.Web/Models/PracticaViewModels.cs`), se mapeó en `PracticasController.Details` (`Unidad = practica.Unidad`), y se agregó la fila "Unidad" en la card "Información general" de `Views/Practicas/Details.cshtml`.
- **Capas afectadas:** Web (ViewModel, Controller, View). Sin migración EF (el campo `Practica.Unidad` ya existía desde la Sesión 3).
- **Verificado en vivo:** `GET /Practicas/Details/1` (Perfil "Rutina") muestra "Unidad: 17".

#### Hallazgo 2 — `Practicas/Edit` no preseleccionaba el combo de composición (BUG REAL, causa raíz confirmada por reproducción)
- **Descartado como falso positivo:** se reprodujo localmente contra `labipac_dev` con el Perfil real "Rutina" (Id=1, con 2 componentes asociados: Urea y Triglicéridos), por lo que la hipótesis "Perfil sin composición" no aplica a este caso.
- **Causa raíz real (confirmada corriendo la app y comparando el HTML servido antes/después del fix):**
  1. `PracticasController.Edit` (GET) arma `UnidadesDisponibles` únicamente a partir de `IUnidadBioquimicaService.GetActivasAsync()`, que filtra `Where(e => e.Activo)` **sobre un `DbSet` que ya tiene aplicado el query filter global de soft-delete** (`DeletedAt == null`, definido en `AppDbContext.ApplySoftDeleteFilter`). Es decir: cualquier `UnidadBioquimica` soft-deleted queda excluida de `UnidadesDisponibles` **aunque su columna `Activo` siga en `true`**.
  2. En la base real, las dos `UnidadBioquimica` asociadas al Perfil "Rutina" (Urea Id=1, Triglicéridos Id=2) están soft-deleted (`DeletedAt` no nulo) pero con `Activo=1`. Por lo tanto no se generaba ningún `<option>` para esos IDs en el `<select>` del formulario.
  3. `UnidadBioquimicaIds` (el array `seleccionados` que usa el JS de Select2) sí se arma correctamente desde `practica.Detalles.Select(d => d.UnidadBioquimicaId)` — el problema no era el JSON ni el timing de Select2 (ambas hipótesis descartadas): sin `<option>` en el DOM para esos valores, ni el atributo `selected` de Razor ni el `.val(seleccionados).trigger('change')` de JS tienen sobre qué actuar. El bug era 100% de datos faltantes en el combo, no de front-end.
  4. **Bug secundario relacionado (más grave, de pérdida de datos):** como el formulario nunca renderiza esos `<option>`, al guardar el Edit sin tocar el combo el navegador no los envía en el POST, por lo que `PracticaService.UpdateAsync` los eliminaba silenciosamente de la composición del Perfil. Es decir, el bug visual escondía un bug funcional de pérdida de datos en cada guardado.
  5. **Bug adicional detectado en el mismo código:** el banner de advertencia "Atención: los siguientes componentes están inactivos" (`ComponentesInactivos`) solo evaluaba `d.UnidadBioquimica is { Activo: false }`, por lo que tampoco se disparaba para este caso (Activo=true, solo soft-deleted), dejando al usuario sin ninguna pista visual del problema.
- **Fix aplicado en `PracticasController.cs`:**
  - Nuevo método privado `BuildUnidadesDisponiblesAsync(IEnumerable<int> idsAsociados)`: arma la lista de unidades activas (comportamiento igual que antes) y además agrega, vía `_context.UnidadesBioquimicas.IgnoreQueryFilters().Where(u => idsFaltantes.Contains(u.Id))`, las unidades ya asociadas a la Práctica/Perfil que no aparecen entre las activas (inactivas o soft-deleted). Así el combo siempre puede renderizar y preseleccionar la composición real, y el POST no pierde la asociación si el usuario no la toca.
  - Se reemplazaron las 6 repeticiones inline del patrón `(await _unidadService.GetActivasAsync()).Select(...).ToList()` (Create GET, Create POST x2, Edit GET, Edit POST x2) por llamadas a este helper — no es un refactor cosmético, es la corrección mínima necesaria para que los 3 puntos de re-render del formulario (GET inicial, ModelState inválido, fallo de servicio) se comporten igual y no reintroduzcan el bug en los otros caminos.
  - Se corrigió la condición de `ComponentesInactivos` en `Edit` (GET) de `d.UnidadBioquimica is { Activo: false }` a `d.UnidadBioquimica is { } ub && (!ub.Activo || ub.DeletedAt != null)`, para que el banner de advertencia también contemple componentes soft-deleted.
- **Capas afectadas:** Web (`PracticasController`) únicamente. Sin cambios de ViewModel ni de vista (`Edit.cshtml` ya estaba correctamente cableado, tal como indicaba la lectura de código estática original). Sin migración EF.
- **Verificado en vivo (antes/después, mismo Perfil real):**
  - Antes del fix: `GET /Practicas/Edit/1` devolvía un único `<option value="3">` (la única `UnidadBioquimica` activa y no eliminada); `seleccionados = ["2","1"]` en el JS pero sin `<option>` para esos valores → nada preseleccionado, banner "Atención" ausente.
  - Después del fix: el mismo request devuelve `<option value="1" selected="selected">`, `<option value="2" selected="selected">` y `<option value="3">`; el banner "Atención: los siguientes componentes están inactivos: Urea, Triglicéridos" ahora se muestra correctamente.

#### Hallazgo 3 — `ProduccionMensual/Detalle` no mostraba `Unidad` del Perfil
- **Causa raíz:** la tabla de líneas del período no tenía columna para ese dato; no era snapshot histórico (a diferencia de `PrecioSnapshot`/`NombreSnapshot`), así que nunca se había cargado ni mapeado.
- **Fix (lookup en vivo, sin snapshot ni migración EF, según lo pedido):**
  - `ProduccionMensualService.GetByIdAsync`: se agregó `.ThenInclude(d => d.Practica)` al include de `Detalles` (antes solo incluía `Detalles` sin la navegación a `Practica`), para poder leer `Practica.Unidad` vigente.
  - `ProduccionDetalleRowViewModel` (`Models/ProduccionMensualViewModels.cs`): se agregó `public int? UnidadPerfil { get; set; }`.
  - `ProduccionMensualController.Detalle`: se pobló `UnidadPerfil = d.TipoItem == TipoItemProduccion.Practica ? d.Practica?.Unidad : null` (null también si el Perfil referenciado fue soft-deleted, ya que la navegación respeta el query filter global — se resuelve igual que otros casos similares en el código existente, con fallback a "—" en la vista).
  - `Views/ProduccionMensual/Detalle.cshtml`: se agregó la columna "Unidad" en `#tablaLineas` (entre "Item" y "Precio"), con `@(linea.UnidadPerfil?.ToString() ?? "—")` — vacío/"—" para líneas de tipo Práctica.
- **Capas afectadas:** Infrastructure (`ProduccionMensualService`), Web (ViewModel, Controller, View). Sin migración EF.
- **Verificado en vivo:** `GET /ProduccionMensual/Detalle/1` muestra "17" en la fila de línea tipo Perfil ("Rutina") y "—" en las líneas de tipo Práctica (Triglicéridos, Creatinina).

#### Método de verificación (los 3 hallazgos)
Se corrió la aplicación localmente (`dotnet run --urls https://localhost:5099`) contra `labipac_dev`, se autenticó vía `curl` (cookie de Identity, usuario seed `no-reply@olvidata.com.ar` / password default `Super123!` de `SeedData.cs`, sin overrides en User Secrets) y se inspeccionó el HTML servido crudo antes y después de cada fix, en vez de asumir por lectura estática — esto fue clave para el Hallazgo 2, donde la lectura de código sola no revelaba el problema (el bug estaba en la intersección de dos servicios: el query filter global de soft-delete de `UnidadBioquimica` + el filtro `Activo` de `GetActivasAsync()`).

#### Build
`dotnet build LabIPAC.slnx` → **Compilación correcta, 0 errores** (mismos warnings preexistentes de NuGet MailKit/MimeKit y el warning CS0114 de `HomeController`, ninguno introducido por esta sesión).

#### Migraciones EF
Ninguna. Los 3 hallazgos se resolvieron con cambios de código (ViewModel/Controller/View/Service) sobre columnas y relaciones ya existentes.

#### Riesgos y supuestos
- El Hallazgo 2 tenía un componente de **pérdida silenciosa de datos** (ítem 4 de la causa raíz) que ya pudo haber afectado Perfiles editados y guardados entre el deploy de la Sesión 3 y este fix, si algún Perfil en Producción tiene composición con `UnidadBioquimica` soft-deleted. Recomendación: verificar en Producción, tras aplicar este fix, si hay Perfiles cuya composición actual no coincide con lo esperado (comparar contra backups/logs si existen).
- El fix de Hallazgo 2 asume que el patrón correcto es "mostrar y preservar" componentes soft-deleted ya asociados (igual criterio que ya usaba el sistema para componentes con `Activo=false`, vía el badge "Inactiva" en `Details.cshtml` y el banner en `Edit.cshtml`) — no se agregó lógica para impedir volver a poner `Activo=true`/restaurar la `UnidadBioquimica` desde esta pantalla, porque no formaba parte del hallazgo reportado.

#### Pruebas mínimas para QA
1. `Practicas/Details` de un Perfil cualquiera: confirmar que se ve la fila "Unidad" con el valor correcto.
2. `Practicas/Edit` del Perfil "Rutina" (u otro con componentes soft-deleted si existe en el ambiente a probar): confirmar que el combo de composición aparece con las Prácticas ya asociadas preseleccionadas, y que el banner "Atención" lista los componentes inactivos/eliminados. Guardar sin tocar el combo y confirmar que la composición no se pierde (recargar Details y comparar).
3. `Practicas/Edit` de un Perfil cuya composición sea 100% de `UnidadBioquimica` activas (caso sin regresión): confirmar que el combo sigue funcionando igual que antes.
4. `ProduccionMensual/Detalle` de un período con líneas de ambos tipos: confirmar columna "Unidad" con el valor numérico en líneas de Perfil y "—" en líneas de Práctica.

#### Checklist de salida para merge
- [x] Build OK (0 errores).
- [x] Los 3 hallazgos reproducidos y verificados en vivo (no solo por lectura de código).
- [x] Causa raíz documentada para los 3, incluyendo el bug de pérdida de datos descubierto en el Hallazgo 2.
- [x] Sin migraciones EF nuevas.
- [x] Sin cambios fuera del alcance de los 3 hallazgos.
- [ ] QA funcional de los 3 fixes (pendiente, agente `agentes-ia-qa`).
- [ ] Confirmación del cliente de que los 3 hallazgos quedaron resueltos.

---

### Sesión 1 — Análisis de integración FABA AOL WS V2
**Fecha:** 2025  
**Estado:** ANÁLISIS COMPLETO — pendiente aprobación para implementar

---

### Sesión 2 — Implementación FABA (Etapas 1–4 + Web Layer)
**Fecha:** 2026-06-17/18  
**Estado:** ✅ BUILD OK — Migración generada, pendiente aplicar a DB (credenciales no configuradas en entorno de desarrollo)

#### Archivos creados

**Application:**
- `LabIPAC.Application/Settings/FabaSettings.cs`
- `LabIPAC.Application/Interfaces/IFabaClient.cs`
- `LabIPAC.Application/Interfaces/IFabaImportService.cs`
- `LabIPAC.Application/DTOs/Faba/FabaMutualDto.cs`
- `LabIPAC.Application/DTOs/Faba/FabaUnidadBioquimicaDto.cs`
- `LabIPAC.Application/DTOs/Faba/FabaAfiliadoRequest.cs`
- `LabIPAC.Application/DTOs/Faba/FabaAfiliadoDto.cs`
- `LabIPAC.Application/DTOs/Faba/FabaImportResumenDto.cs`

**Domain:**
- `LabIPAC.Domain/Entities/Mutual.cs` — hereda SoftDestroyable
- `LabIPAC.Domain/Entities/UnidadBioquimicaFabaCodigo.cs` — sin SoftDestroyable (gestión por campo Activo)
- `LabIPAC.Domain/Entities/Paciente.cs` — extendido con `MutualId`, `DigitoAfiliado`, `RelacionAfiliado`, `TipoDocumentoFabaId`

**Infrastructure:**
- `LabIPAC.Infrastructure/Services/Faba/FabaClient.cs`
- `LabIPAC.Infrastructure/Services/Faba/FabaResponseParser.cs`
- `LabIPAC.Infrastructure/Services/Faba/FabaImportService.cs`

**Web:**
- `LabIPAC.Web/Controllers/FabaController.cs` — acceso `RequireAdministracion`
- `LabIPAC.Web/Models/FabaViewModels.cs`
- `LabIPAC.Web/Views/Faba/Index.cshtml` — listado de mutuales + sincronización
- `LabIPAC.Web/Views/Faba/Analitos.cshtml` — analitos por mutual + vinculación AJAX a UB local
- `LabIPAC.Web/Views/Faba/ConsultarAfiliado.cshtml` — consulta afiliado por DNI o legajo

#### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `LabIPAC.Infrastructure/Data/AppDbContext.cs` | DbSets Mutuales, UnidadesBioquimicasFabaCodigos; config Fluent API; FK Paciente→Mutual |
| `LabIPAC.Infrastructure/DependencyInjection.cs` | Registro FabaSettings, HttpClient "faba", IFabaClient, IFabaImportService |
| `LabIPAC.Web/appsettings.json` | Sección `Faba` placeholder |
| `LabIPAC.Web/Views/Shared/_Layout.cshtml` | Entrada "Integración FABA" en sidebar bajo Administración |

#### Migración EF generada
- Nombre: `AddFabaMutualYAnalitos`
- Script SQL: `docs/labipac/migrations/AddFabaMutualYAnalitos.sql`
- Estado: **generada, pendiente aplicar** (requiere connection string en User Secrets)
- Tablas nuevas: `Mutuales`, `UnidadesBioquimicasFabaCodigos`
- Columnas nuevas en `Pacientes`: `MutualId`, `DigitoAfiliado`, `RelacionAfiliado`, `TipoDocumentoFabaId`

#### Corrección modelo de datos
- ⚠️ FABA "prácticas" (PracticasPorMutual) son **analitos bioquímicos individuales** → mapean a `UnidadBioquimica`, NO a `Practica` (que es un paquete interno del sistema)
- La entidad `UnidadBioquimicaFabaCodigo` reemplaza el nombre `PracticaFabaMapping` del plan original

#### Pendiente (Etapas 5–6)
- [ ] Aplicar migración a DB de desarrollo (configurar User Secrets: `Faba:IdUsuario`, `Faba:Password`)
- [ ] Etapa 5: Módulo Autorizaciones (`AutorizacionFaba`, `ValidarOrdenV4`)
- [ ] Etapa 6: Catálogos auxiliares (Diagnósticos, Prestadores)
- [ ] Integración lookup FABA desde formulario Create/Edit de Paciente

---

## 0. Escaneo de reutilización
No existe `/docs/indice.md` ni otros proyectos en el historial. Implementación desde cero.

---

## 1. Análisis del Web Service FABA AOL V2

**WSDL:** `http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.wsdl`  
**Endpoint SOAP 1.1 / HTTP POST**  
**Auth:** `idUsuario` (int) + `password` (int) en cada llamada  
**Respuestas:** todas retornan `Result: xsd:string` — contiene XML embebido como texto

### 1.1 Inventario completo de operaciones (37)

| # | Operación | Grupo | Parámetros clave (sin auth) |
|---|-----------|-------|-----------------------------|
| 1 | `UsuariosMutuales` | Maestros | — |
| 2 | `DatosMutual` | Maestros | `Idmutual` |
| 3 | `TiposDocumentos` | Maestros | `Idmutual` |
| 4 | `Coseguros` | Maestros | `Idmutual` |
| 5 | `TiposBonos` | Maestros | — |
| 6 | `ConsultarAfiliado` | Afiliados | `Idmutual`, `IdTipoBusqueda`, `strLegajo`, `strDigito`, `strRelacion`, `strTipoDocumento`, `intNroDocumento` |
| 7 | `ConsultarAfiliadoOsde` | Afiliados | `Idmutual`, `IdTipoBusqueda`, `strLegajo`, `strCodSeguridad`, `CodFacturante` |
| 8 | `ConsultarAfiliadoTransaccion` | Afiliados | `NroTransaccion` |
| 9 | `PracticasPorMutual` | Catálogos | `Idmutual` |
| 10 | `DiagnosticosV3` | Catálogos | `Idmutual`, `MuestraCombo` |
| 11 | `Diagnosticos` | Catálogos | (versión anterior de DiagnosticosV3) |
| 12 | `DiagnosticosAlfabetico` | Catálogos | — |
| 13 | `Prestadores` | Catálogos | `Idmutual`, `nombre` (búsqueda) |
| 14 | `UltimoCambioPractica` | Sincronización | `Idmutual` |
| 15 | `UltimoCambioUsuario` | Sincronización | — |
| 16 | `ValidarOrdenV4` | Autorizaciones | `Idmutual`, datos afiliado, datos médico, hasta 24 prácticas (int), coseguro, bono, diagnósticos |
| 17 | `ValidarOrdenfV4` | Autorizaciones | Igual pero prácticas como `string` (lista separada) |
| 18 | `ValidarOrdenV3` | Autorizaciones (old) | Versión anterior de ValidarOrdenV4 |
| 19 | `ValidarOrdenfV3` | Autorizaciones (old) | Versión anterior de ValidarOrdenfV4 |
| 20 | `ValidarOrdenOsde` | Autorizaciones OSDE | Específico OSDE (versión anterior) |
| 21 | `ValidarOrdenOsdeWS` | Autorizaciones OSDE | Específico OSDE (versión actual, hasta 24 prácticas) |
| 22 | `ConsultarOrden` | Gestión órdenes | `Idmutual`, `NroTransaccion` |
| 23 | `ConsultarOrdenConValoresSugeridos` | Gestión órdenes | `Idmutual`, `NroTransaccion` |
| 24 | `ModificarFechaRealizacion` | Gestión órdenes | `NroTransaccion`, `FechaRealizacion` |
| 25 | `SuspenderOrden` | Gestión órdenes | `NroTransaccion` |
| 26 | `EliminarSuspensionOrden` | Gestión órdenes | `NroTransaccion` |
| 27 | `ConsultarSuspension` | Gestión órdenes | `NroTransaccion` |
| 28 | `Recurrir` | Apelaciones | `NroTransaccion`, `Mensaje` |
| 29 | `AgregarBono` | Bonos | `NroTransaccion`, `Coseguro`, `TipoBono`, `NroBono`, `BonoNuevo` |
| 30 | `EliminarBono` | Bonos | `NroTransaccion`, `Coseguro`, `TipoBono`, `NroBono`, `BonoNuevo` |
| 31 | `ConsultarBonos` | Bonos | `NroTransaccion` |
| 32 | `ConsultarTransaccionDeBono` | Bonos | `NroTransaccion` |
| 33 | `AceptarAuditoria` | Auditoría | `NroAutorizacion` |
| 34 | `ConsultaConfirmacionAuditoria` | Auditoría | `NroAutorizacion` |
| 35 | `ConsultarMensajes` | Mensajería | — |
| 36 | `GrabarMensajes` | Mensajería | — |
| 37 | `ValidarUsuario` | Sistema | — |
| 38 | `CambioClave` | Sistema | — |

### 1.2 Notas técnicas del WS
- SOAP 1.1, estilo RPC/encoded (antiguo)
- Todas las respuestas son `Result: xsd:string` conteniendo **XML embebido como string**
- El XML de respuesta debe parsearse con `XDocument.Parse(result)`
- `ProcessingId` = GUID generado por el cliente por llamada
- `Terminal` = identificador de la máquina cliente (ej: nombre del host)
- **No usa WS-Security** — credenciales van en el body de cada operación

---

## 2. Funcionalidades del WS relevantes para LabIPAC

### Prioridad ALTA — Impacto directo en flujo de trabajo

| Funcionalidad | Operaciones WS | Módulo LabIPAC afectado |
|---|---|---|
| Maestro de Mutuales sincronizado | `UsuariosMutuales`, `DatosMutual` | Nuevo módulo `Mutuales` |
| Validación/búsqueda de afiliado | `ConsultarAfiliado`, `ConsultarAfiliadoOsde` | Módulo `Pacientes` (lookup en carga) |
| Catálogo de prácticas por mutual | `PracticasPorMutual`, `UltimoCambioPractica` | Módulo `Practicas` (mapeo FABA codes) |
| Autorización de órdenes | `ValidarOrdenV4`, `ValidarOrdenfV4` | Nuevo módulo `Autorizaciones` |
| Consulta de orden autorizada | `ConsultarOrden`, `ConsultarOrdenConValoresSugeridos` | Nuevo módulo `Autorizaciones` |

### Prioridad MEDIA

| Funcionalidad | Operaciones WS | Módulo LabIPAC afectado |
|---|---|---|
| Gestión de bonos/coseguros | `AgregarBono`, `EliminarBono`, `ConsultarBonos` | Módulo `Autorizaciones` (sub-flujo) |
| Diagnósticos CIE-10 | `DiagnosticosV3` | Nuevo módulo `Diagnosticos` (catálogo) |
| Modificar / suspender órdenes | `ModificarFechaRealizacion`, `SuspenderOrden`, etc. | Módulo `Autorizaciones` |
| Prestadores médicos | `Prestadores` | Nuevo catálogo `Prestadores` |
| Apelaciones | `Recurrir` | Módulo `Autorizaciones` |

### Prioridad BAJA (backlog)

| Funcionalidad | Operaciones WS |
|---|---|
| Auditoría médica FABA | `AceptarAuditoria`, `ConsultaConfirmacionAuditoria` |
| Mensajería interna FABA | `ConsultarMensajes`, `GrabarMensajes` |
| Soporte OSDE específico | `ValidarOrdenOsdeWS`, `ConsultarAfiliadoOsde` |
| Gestión de credenciales | `ValidarUsuario`, `CambioClave` |

---

## 3. Plan de implementación por etapas

### Etapa 1 — Infraestructura SOAP y configuración (prereq de todo)

**Objetivo:** cliente SOAP reutilizable, configuración segura de credenciales.

**Archivos a crear:**
- `LabIPAC.Application/Settings/FabaSettings.cs` — POCO con `IdUsuario`, `Password`, `TerminalId`, `EndpointUrl`
- `LabIPAC.Application/Interfaces/IFabaClient.cs` — interfaz de bajo nivel (enviar/recibir SOAP)
- `LabIPAC.Application/Interfaces/IFabaService.cs` — interfaz de alto nivel (métodos de negocio)
- `LabIPAC.Infrastructure/Services/Faba/FabaClient.cs` — implementación HTTP SOAP (raw envelope, `IHttpClientFactory`)
- `LabIPAC.Infrastructure/Services/Faba/FabaResponseParser.cs` — parseador `XDocument` de respuestas
- `appsettings.json` (sección `Faba`) — sólo placeholder, sin credenciales reales
- User Secrets: `Faba:IdUsuario` y `Faba:Password`

**Técnica:** `IHttpClientFactory` + SOAP 1.1 envelope generado dinámicamente (sin WCF). Evitar `dotnet-svcutil` ya que el WSDL es RPC/encoded y genera código difícil de mantener en .NET 10.

**Patrón SOAP envelope:**
```xml
POST http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.asmx
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://tempuri.org/{OperationName}"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
	<{OperationName} xmlns="http://tempuri.org/">
	  <idUsuario>5903</idUsuario>
	  <password>8491</password>
	  <!-- params -->
	</{OperationName}>
  </soap:Body>
</soap:Envelope>
```

---

### Etapa 2 — Módulo Mutuales (maestro sincronizado)

**Objetivo:** Entidad `Mutual` local sincronizada con `UsuariosMutuales` + `DatosMutual`.

**Domain:**
- Nueva entidad `Mutual : SoftDestroyable`
  - `IdFaba` (int) — clave del WS, unique index
  - `Nombre` (string)
  - `CodigoFacturante` (int?)
  - `EsOsde` (bool) — para bifurcar entre ValidarOrdenV4 / ValidarOrdenOsdeWS
  - `Activo` (bool)

**Application:**
- `IFabaService.SincronizarMutualesAsync()` → llama `UsuariosMutuales`, upsert en DB

**Infrastructure:**
- `FabaService.SincronizarMutualesAsync()`

**Web:**
- `MutualesController` — CRUD local + botón "Sincronizar con FABA"
- Vista `Index` con DataTables server-side, badge activo/inactivo, columna `IdFaba`

**Migración EF:** `AddMigration AddMutual`

---

### Etapa 3 — Mapeo Prácticas ↔ FABA por mutual

**Objetivo:** Cada `Practica` local tiene un código FABA por mutual para poder incluirla en una autorización.

**Domain:**
- Nueva entidad `PracticaFabaMapping : SoftDestroyable`
  - `PracticaId` (FK → Practica)
  - `MutualId` (FK → Mutual)
  - `CodigoFaba` (int) — `IdPractica` del WS
  - Índice único (`PracticaId`, `MutualId`)

**Application:**
- `IFabaService.SincronizarPracticasAsync(int mutualId)` → llama `PracticasPorMutual`, upsert mappings
- `IFabaService.UltimoCambioPracticaAsync(int mutualId)` → para invalidar caché

**Web:**
- En `PracticasController.Edit`: nueva sección "Códigos FABA por mutual" — tabla de mappings

**Migración EF:** `AddMigration AddPracticaFabaMapping`

---

### Etapa 4 — Lookup de afiliado en módulo Pacientes

**Objetivo:** Al crear/editar un paciente, buscar en FABA para completar datos de mutual y validar afiliación.

**Domain — expansión `Paciente`:**
- `MutualId` (int?, FK → Mutual)
- `DigitoAfiliado` (string?) — `strDigito` del WS
- `RelacionAfiliado` (string?) — `strRelacion` (titular/familiar)
- `TipoDocumentoFabaId` (int?) — tipo de documento según la mutual

**Application:**
- `IFabaService.ConsultarAfiliadoAsync(FabaAfiliadoRequest)` → devuelve `FabaAfiliadoDto`
- DTO `FabaAfiliadoDto`: NombreCompleto, Sexo, FechaNacimiento, NroAfiliado, Mutual, Estado

**Web:**
- `PacientesController`: nuevo endpoint `[HttpGet] BuscarAfiliadoFaba` (AJAX, devuelve JSON)
- En `Create`/`Edit` Paciente: botón "Buscar en FABA" que dispara AJAX y pre-completa campos

**Migración EF:** `AddMigration PacienteAddMutualFields`

---

### Etapa 5 — Módulo Autorizaciones (core)

**Objetivo:** Registrar y gestionar autorizaciones de órdenes FABA.

**Domain:**
- Nueva entidad `AutorizacionFaba : SoftDestroyable`
  - `PacienteId` (FK → Paciente)
  - `MutualId` (FK → Mutual)
  - `NroTransaccion` (int?) — asignado por FABA al autorizar
  - `NroAutorizacion` (string?) — número legible de autorización
  - `Estado` (enum `EstadoAutorizacion`: Borrador, Autorizada, Rechazada, Suspendida, Apelada)
  - `FechaPrescripcion` (DateOnly)
  - `FechaRealizacion` (DateOnly)
  - `NombreMedico` (string)
  - `MatriculaMedico` (string)
  - `TipoMatricula` (string) — Nacional/Provincial
  - `IdDiagnostico1` (string?), `IdDiagnostico2` (string?)
  - `Telefono` (string?)
  - `Observacion` (string?)
  - `TipoBono` (int?), `NroBono` (int?), `Coseguro` (int?)
  - `RespuestaXmlFaba` (string?) — XML completo de respuesta para auditoría
  - Navegación: `ICollection<AutorizacionDetalle>`

- Nueva entidad `AutorizacionDetalle`
  - `AutorizacionFabaId` (FK)
  - `PracticaId` (FK → Practica)
  - `CodigoFaba` (int) — código enviado al WS
  - `Orden` (int) — posición 1..24

**Application:**
- `IFabaService.ValidarOrdenAsync(FabaOrdenRequest)` → devuelve `FabaOrdenResultDto`
- `IFabaService.ConsultarOrdenAsync(int mutual, int nroTransaccion)` → estado actual
- `IFabaService.SuspenderOrdenAsync(int nroTransaccion)`
- `IFabaService.RecurrirAsync(int nroTransaccion, string mensaje)`
- DTO `FabaOrdenRequest`, `FabaOrdenResultDto`

**Web:**
- `AutorizacionesController`: CRUD completo + acción `Autorizar` (POST → WS → guarda resultado)
- Vistas: `Index` (DataTables server-side), `Create`, `Details`, `Autorizar` (wizard 3 pasos)

**Migración EF:** `AddMigration AddAutorizacionFaba`

---

### Etapa 6 — Diagnósticos y Prestadores (catálogos auxiliares)

**Objetivo:** Catálogos locales con sincronización on-demand.

**Domain:**
- `DiagnosticoFaba` (sin herencia SoftDestroyable — sólo lectura): `Codigo`, `Descripcion`, `MutualId`
- `Prestador` (sin herencia): `IdFaba`, `Nombre`, `MutualId`

**Application:** `IFabaService.ObtenerDiagnosticosAsync(int mutual)`, `IFabaService.BuscarPrestadoresAsync(int mutual, string nombre)`

**Web:** Endpoints AJAX para autocompletar en formulario de autorización.

---

## 4. Cambios por capa — resumen

| Capa | Nuevos archivos | Archivos modificados |
|------|----------------|---------------------|
| Domain | `Mutual`, `PracticaFabaMapping`, `AutorizacionFaba`, `AutorizacionDetalle`, `DiagnosticoFaba`, `Prestador` + enum `EstadoAutorizacion` | `Paciente` (+ campos mutual) |
| Application | `IFabaClient`, `IFabaService`, `FabaSettings`, DTOs: `FabaAfiliadoDto`, `FabaOrdenRequest`, `FabaOrdenResultDto` | — |
| Infrastructure | `FabaClient`, `FabaService`, `FabaResponseParser` + config `AddFabaServices()` | `AppDbContext` (DbSets nuevos + config Fluent) |
| Web | `MutualesController`, `AutorizacionesController` + ViewModels + Vistas | `PacientesController` + vista Create/Edit, `appsettings.json`, `Program.cs` |

---

## 5. Migraciones EF requeridas

```
1. AddMutual
2. AddPracticaFabaMapping
3. PacienteAddMutualFields
4. AddAutorizacionFaba
5. AddCatalogsFabaAux  (DiagnosticoFaba, Prestador)
```

---

## 6. Configuración segura de credenciales

**appsettings.json** (placeholder sin valor real):
```json
"Faba": {
  "EndpointUrl": "http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.asmx",
  "IdUsuario": 0,
  "Password": 0,
  "TerminalId": "LABIPAC-01",
  "TimeoutSeconds": 30
}
```

**User Secrets (desarrollo) — ejecutar:**
```powershell
dotnet user-secrets set "Faba:IdUsuario" "5903" --project LabIPAC.Web
dotnet user-secrets set "Faba:Password"  "8491" --project LabIPAC.Web
```

**Producción:** variables de entorno `Faba__IdUsuario` / `Faba__Password`.  
❌ **NUNCA hardcodear credenciales en código ni en appsettings.Production.json**.

---

## 7. Paquetes NuGet necesarios

| Paquete | Capa | Justificación |
|---------|------|---------------|
| Ninguno nuevo | — | Se usa `IHttpClientFactory` (ya en `Microsoft.AspNetCore.App`) + `System.Xml.Linq` (BCL). No se necesita WCF ni `dotnet-svcutil` |

---

## 8. Riesgos y supuestos

| Riesgo | Mitigación |
|--------|------------|
| El WS responde con XML mal formado o con entidades HTML | `FabaResponseParser` debe ser tolerante; loguear raw response |
| Timeout en validaciones (el WS es lento) | `TimeoutSeconds` configurable; mostrar spinner en UI |
| Mutual OSDE requiere flujo diferente (`ValidarOrdenOsdeWS`) | Campo `EsOsde` en `Mutual` bifurca la lógica en `FabaService` |
| Los códigos de prácticas FABA difieren entre mutuales | `PracticaFabaMapping` resuelve el M:N |
| Respuestas varían entre mutuales (no todas implementan todo) | Manejo defensivo en parser, `ServiceResult.IsSuccess = false` con detalle |
| WSDL en HTTP (no HTTPS) | Riesgo en producción; usar proxy HTTPS si es posible |

---

## 9. Decisión de arquitectura

- **No usar WCF / `dotnet-svcutil`**: el WSDL es RPC/encoded (no Document/Literal), genera proxies difíciles de mantener en .NET 10. En su lugar, envelopes SOAP construidos con interpolación de strings o `XDocument`, enviados con `HttpClient`.
- **`IFabaClient`** (Infrastructure): responsable del transporte HTTP SOAP puro.
- **`IFabaService`** (Application interface / Infrastructure impl): responsable de la lógica de negocio, mapeo de DTOs y orquestación.
- **No exponer `FabaClient` a Controllers**: los controllers solo inyectan `IFabaService`.

---

## 10. Próximos pasos (pendiente aprobación)

- [ ] Aprobar plan por etapas
- [ ] Comenzar Etapa 1 (cliente SOAP + config)
- [ ] Test de conectividad con `ValidarUsuario` antes de continuar
- [ ] Definir qué mutuales están activas (de `UsuariosMutuales`) para priorizar Etapa 3
