# Memoria - Presupuestador

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-10-01

## Definiciones vigentes

### Nota de contexto comercial
`eleven-la-plata` no opera bajo el ciclo comercial externo estándar (no hay negociación de presupuesto con el cliente final por cada item — Joaquín gestiona el proyecto y autoriza el trabajo directamente). Por eso este ciclo NO genera `presupuesto-cliente.md` ni tabla PERT/USD formal — se deja una estimación interna liviana solamente, y el gate de aprobación queda satisfecho por la instrucción explícita: *"solucionar bug crítico, el resto depende de definiciones con el usuario"* (2026-08-20).

### H1 — Estimación interna (2026-08-20)
- **Tipo de item:** ajuste puntual (fix de validación en un service existente, sin pantallas nuevas, sin migración).
- **Referencia histórica:** no hay un caso 1:1 en otros proyectos (lógica de negocio específica de facturación por contador). Se estima directamente por alcance de código: 1 archivo (`AlquilerService.cs`), 1 método nuevo extraído + 1 condicional agregado en `UpdateAsync`, sin cambios de capa Presentación/Datos.
- **Horas estimadas:** 1.5–2.5 h (implementación + build + verificación de las 5 pruebas funcionales definidas en Arquitectura). Riesgo: **Bajo**.
- **Aprobado para pasar a Implementación:** sí.

## Historial de ajustes
- 2026-08-20: Gate de Presupuesto satisfecho por autorización directa del owner del proyecto. Sin documento comercial generado (no aplica para este proyecto).

### Lote 2026-10-01 (F1-F5) — Estimación interna

Mismo criterio que H1: proyecto sin ciclo comercial externo, sin `presupuesto-cliente.md`. Gate satisfecho por autorización directa del owner (2026-10-01: respondió las 3 preguntas bloqueantes y aprobó el alcance F1-F4 + blindaje de F5).

| Ítem | Tipo | O | M | P | PERT | Riesgo |
|---|---|---|---|---|---|---|
| F1 — desempate por `Id` en el orden de la grilla | ajuste puntual | 0,2 | 0,3 | 0,6 | **0,33 h** | Bajo |
| F2 — default Egreso | ajuste puntual | 0,1 | 0,2 | 0,3 | **0,20 h** | Bajo |
| F3 — redirect a la cuenta de origen | ajuste puntual | 0,3 | 0,5 | 1,0 | **0,55 h** | Bajo |
| F4 — columna comprobante en 3 grillas | ajuste de UI x3 | 0,6 | 1,0 | 1,8 | **1,07 h** | Bajo |
| F5 — blindaje de contadores (3 puntos de entrada + reutilización de `ValidarContadoresAsync`) | lógica de negocio | 1,5 | 2,5 | 4,5 | **2,67 h** | Medio |
| Build + verificación de las 12 pruebas funcionales | — | 0,8 | 1,2 | 2,0 | **1,27 h** | — |
| **Total** | | **3,5** | **5,7** | **10,2** | **6,09 h** | |

**Rango a comunicar:** 5,5 – 7 h. Desvío esperado concentrado en F5 (es el único con decisión técnica real: compartir `ValidarContadoresAsync` entre dos services sin romper el refactor de H1).

**No incluido en esta estimación (trabajo aparte, a presupuestar cuando el owner decida):** saneamiento de las **69 filas regresivas en 0** de producción. Estimación preliminar 1,5–3 h según si se corrigen con valores reales aportados por el cliente (requiere planilla) o se dan de baja lógica.

**Aprobado para pasar a Implementación:** sí.

### Cierre de calibración — Lote 2026-10-01 (F1-F5)

**Veredicto de QA:** GO para el merge del lote completo (pasadas A, B y C). Sin defectos abiertos introducidos por el lote.

#### Estimado vs. real, por ítem

| Ítem | Estimado (PERT) | Real | Desvío | Comentario |
|---|---|---|---|---|
| F1 — desempate por `Id` | 0,33 h | ~0,3 h | ≈0 | Una línea, como estaba previsto. |
| F2 — default Egreso | 0,20 h | ~0,2 h | ≈0 | |
| F3 — redirect a la cuenta | 0,55 h | ~0,4 h | **−0,15** | El patrón de `CreateUnificado` estaba ahí para copiar, como anticipó Arquitectura. |
| F4 — columna comprobante | 1,07 h | ~0,7 h | **−0,37** | Se estimó sobre 3 vistas y resultaron **2** (ver desvío 2). |
| F5 — blindaje de contadores | 2,67 h | ~2,5 h | ≈0 | La extracción a `ContadorValidator.cs` salió sin fricción. |
| Build + verificación | 1,27 h | ~1,2 h | ≈0 | |
| **Subtotal alcance planificado** | **6,09 h** | **~5,3 h** | **−13%** | Dentro del rango comunicado (5,5-7 h), en el extremo bajo. |
| *Fixes no planificados (ELV-003/005/006/007)* | *0* | *~1,2 h* | *+1,2* | No estaban en el alcance: salieron de QA. |
| **Total real** | **6,09 h** | **~6,5 h** | **+7%** | |

#### Desvíos y qué aprendimos

**1. La estimación del alcance planificado fue buena (−13%); el total se fue +7% por defectos que QA destapó.** Es el patrón esperable y sano: la estimación no falló, el alcance creció. Lo que importa es que **4 de los 5 defectos se corrigieron dentro del ciclo** porque eran criterios de aceptación ya aprobados o defectos del propio cambio — no alcance nuevo.

**2. Arquitectura pidió un cambio que contradecía un criterio de aceptación aprobado.** Pedí que `AgregarHistoriaContadorSiCorresponde` dejara de insertar en el caso "sin anterior ni siguiente", que es exactamente CA-F5.4 (máquina nueva acepta 0). El implementador lo levantó en vez de ejecutarlo, y tenía razón. **Aprendizaje: cuando Arquitectura especifica un cambio sobre una rama de código, verificar contra la tabla de CA antes de cerrarla** — el costo de no hacerlo lo paga el implementador en forma de desvío.

**3. Se estimó una vista que no existe.** F4 se presupuestó sobre "3 grillas" porque el Discovery leyó el pedido del cliente ("en todas las cuentas") sin verificar que `Clientes/Details` tuviera grilla propia — linkea a la de `Cuentas/Details`. **Aprendizaje: contar archivos reales, no pantallas conceptuales, antes de estimar trabajo de UI.** Acá jugó a favor (−0,37 h), pero la misma omisión en sentido inverso habría sido un sobrecosto.

**4. Un CA describía un escenario inalcanzable.** CA-F3.3 pedía conservar un fallback para un caso que `CreateAsync` rechaza antes. QA lo marcó BLOCKED en vez de FAIL, correctamente. **Aprendizaje: un criterio de aceptación que no se puede ejercitar no es un criterio** — al escribirlos, preguntarse si existe un camino real para llegar ahí.

**5. El hallazgo de mayor valor del lote no estaba en el alcance.** ELV-005 (movimiento anulado mostrando acumulado $0,00) **reproduce exactamente el síntoma que el cliente reportó**, por una puerta distinta de la que arreglamos. Si QA no lo encontraba, F1 se entregaba "resuelto" y el cliente lo volvía a reportar en cuanto anulara un movimiento. **Aprendizaje: al arreglar un síntoma, buscar explícitamente los otros caminos que producen el mismo síntoma** — en este caso, preguntarle a QA por ellos fue lo que lo destapó (misma técnica que funcionó en el lote B con ELV-004).

#### Ajustes para próximas estimaciones
- Mantener los rangos actuales para ajustes puntuales de 1 archivo: vienen calibrando bien (F1, F2, F5 todos dentro del ±10%).
- **Agregar una partida explícita de "corrección de hallazgos de QA" del orden del 15-20% del subtotal** en lotes que tocan módulos financieros o con histórico de defectos. Este lote la habría absorbido sin desvío.
- Para trabajo de UI, **verificar la cantidad de archivos reales antes de estimar**, no la cantidad de pantallas que describe el cliente.

#### Pendientes de decisión del owner (no son desvíos, son alcance diferido)
1. **Saneamiento de las 69 filas regresivas en 0** — estimado 1,5-3 h según si se corrigen con valores reales (requiere planilla del cliente) o se dan de baja lógica.
2. **ELV-004** — `Maquinas/AjustarContadores` acepta cualquier negativo sin piso; deja los contadores de una máquina en negativo con mensaje de éxito. Preexistente, pero **anula parcialmente la garantía que F5 vino a dar**. Estimado preliminar 0,5-1 h.
3. **Causa de fondo de ELV-006** — `Importe`, `Motivo`, `Tipo` y `Cuenta` siguen clickeables mientras el servicio ordena siempre por `Fecha`. Preexistente. Estimado preliminar 1-2 h (implementar el orden por columna, no solo apagar las cabeceras).

### Cierre de calibración — Lote 2026-10-01 bis (ELV-004 + orden por columna)

**Veredicto de QA:** GO para el lote bis completo (pasadas D y E).

| Ítem | Estimado | Real | Desvío |
|---|---|---|---|
| ELV-004 — piso al ajuste masivo | 0,5-1 h | ~1,8 h | **+80%** |
| Orden por columna (causa de fondo de ELV-006) | 1-2 h | ~1,3 h | dentro de rango |
| **Total** | **1,5-3 h** | **~3,1 h** | **+3% sobre el techo** |

#### Por qué ELV-004 se fue al doble
No fue el código: el fix original se escribió y compiló bien a la primera. **Se fue por un criterio de aceptación mal especificado** (CA-3), que obligó a una pasada completa de QA, un análisis de corrección y una re-verificación.

**El error:** CA-3 decía que ni `Durabilidad` ni `ContadorAsignacion` podían quedar negativas, tratando a las dos como magnitudes acumulativas. `Durabilidad` **no lo es** — es vida útil restante, y el negativo es un estado válido y previsto por el propio dominio (`DurabilidadPorcentaje` devuelve 0 para `<= 0`). El criterio se escribió mirando los nombres de los campos que la función mutaba, **sin revisar qué significa cada uno**.

**El costo real:** si QA no lo agarraba, se publicaba un fix que **bloqueaba todo ajuste negativo en el 46% del parque** (90 de 194 máquinas) sin ningún workaround — una regresión funcional peor que el defecto que venía a corregir.

#### Aprendizajes

**1. Un CA que dice "ningún valor de X puede quedar negativo" exige enumerar los campos y verificar la semántica de cada uno.** Es el segundo error de especificación del día (el primero fue pedirle a Arquitectura un cambio que contradecía CA-F5.4). Los dos comparten patrón: **se razonó sobre la forma del código — qué campos toca la función — en vez de sobre el significado del dato.** Regla para próximos ciclos: antes de cerrar un CA que impone una invariante sobre un conjunto de campos, listarlos y escribir al lado qué representa cada uno. Si alguno no se puede describir en una frase, no se conoce lo suficiente como para restringirlo.

**2. QA ganó su costo dos veces en este ciclo**, y las dos veces encontrando algo que el alcance no pedía: ELV-005 (que reproducía el síntoma original del cliente por otra puerta) y ELV-008. La técnica que funcionó en ambos casos fue **pedirle explícitamente a QA que buscara los otros caminos al mismo síntoma**, en vez de solo verificar los CA.

**3. La verificación campo por campo es lo que cierra este tipo de defecto.** QA no validó el piso con un caso: armó una máquina distinta para cada campo (`ContadorBN` en M6, `ContadorColor` en M425, `ContadorAsignacion` en M61) y comprobó en cada una que ese campo es el que define el mínimo. Sin eso, un piso que ignora un campo pasa inadvertido.

#### Ajuste para próximas estimaciones
- **Un ítem cuyo CA impone una invariante sobre datos existentes lleva +50% sobre la estimación de código**, para la verificación de la premisa contra el parque real. Acá la premisa de CA-3 era falsa para el 46% de las máquinas y nadie la chequeó antes de implementar. Verificarla cuesta una consulta; descubrirla tarde costó una pasada entera de QA.

#### Totales acumulados del día (lote F1-F5 + bis)
- Estimado: 6,09 h + 1,5-3 h = **7,6-9,1 h**
- Real: ~6,5 h + ~3,1 h = **~9,6 h** (+5% sobre el techo)
- Entregado: 5 pedidos del cliente, 6 defectos corregidos (ELV-003 a ELV-008), 2 escalados sin corregir (ELV-004 quedó corregido; ELV-009 pendiente), 5 pasadas de QA.
