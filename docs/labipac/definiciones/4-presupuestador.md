# Memoria - Presupuestador

## Proyecto: labipac
## Ultima actualizacion: 2026-07-23 — SESION 4: presupuesto de Produccion Mensual por Centro de Salud — PRESUPUESTO CERRADO, pendiente aprobacion cliente

## SESION 4 (2026-07-23) — Presupuesto: Produccion Mensual por Centro de Salud

Input: `1-analista-funcional.md` sesion 5, `2-disenador-funcional.md` sesion 3, `3-arquitecto-mvc.md` sesion 3 — todos cerrados.

### PASO 0 — Anclaje historico
Referencia primaria: la propia memoria de labipac, en particular SESION 3 (2026-07-08), que confirmo el patron de "ronda evolutiva sobre sistema ya maduro" con ratio PERT-contingencia/real 6.84x. Este pedido es la **4ta ronda de mejoras** sobre labipac — aplica la regla de "segunda/tercera ronda sobre el mismo modulo" (27-presupuesto-parametros.instructions.md): usar el piso de "Modificacion sobre modulo existente" en vez de la mediana, incluso para el ABM que aparenta ser "nuevo" (reutiliza 100% el patron ya construido 2 veces en este proyecto para Unidades Bioquimicas y Practicas).

### PASO 1-3 — Modulos funcionales identificados y drivers

| Modulo | Tipo | Drivers |
|---|---|---|
| M10 ABM Centro de Salud | ABM simple nuevo, calco de patron existente | Entidad de 2 campos utiles (Nombre, Tipo enum) + Activo, sin relaciones ni validaciones numericas — calco directo de `UnidadBioquimicaService`/`UnidadesBioquimicasController` ya construidos 2 veces en este proyecto (M1 original y su propio patron reutilizado en Practicas) |
| M11 CentroSaludId en Produccion Mensual (FK + selector + RN-24 + columna/filtro listado) | Modificacion sobre modulo existente | +1 FK nullable, selector Select2 en Crear Periodo (reutiliza patron ya usado en modales de Produccion Mensual), ajuste de regla de unicidad ya existente (RN-11 -> RN-24, mismo patron de validacion en Service ya usado), columna + filtro en listado (patron DataTables ya usado en el sistema) |
| M12 Centro de Salud en encabezado PDF | Ajuste puntual | 1 linea condicional nueva en `ReportePdf` ya existente, sin logica de negocio nueva |

### PASO 4-5 — M ajustado, O y P

| Modulo | Referencia / mediana base | Ratio M/mediana | O | M | P |
|---|---|---|---|---|---|
| M10 | M1 Unidades Bioquimicas (mismo proyecto, ABM simple con precio+validacion numerica: 1.5h) | 0.67 (mas simple: sin campo decimal ni validacion de rango) | 0.65 | 1.0 | 1.55 |
| M11 | Tabla "Modificacion sobre modulo existente" (agregar campo simple 0.5h + regla de negocio 1-2h + nuevo filtro/columna 1-2h + migracion 0.5h), piso de cada rango por ser 4ta ronda evolutiva | — (suma de items de tabla, no de mediana unica) | 1.4 | 2.2 | 3.4 |
| M12 | Ajuste puntual (mediana ~0.5h, ya usado en M9 de sesion 3) | 0.80 | 0.25 | 0.4 | 0.62 |

**Justificacion de M10 por debajo de la mediana M1:** `CentroSalud` no tiene campo de precio ni validacion decimal (a diferencia de `UnidadBioquimica`), es un calco casi literal del CRUD ya construido, con menos superficie de validacion.

**Justificacion de M11 (piso de rango, no mediana):** por ser la 4ta ronda evolutiva sobre labipac (regla agregada en la calibracion de SESION 3), se usa el piso de cada item de "Modificacion sobre modulo existente" en vez de la mediana: campo simple (0.5h, piso de rango 0.5h), regla de negocio (1.0h, piso del rango 1-2h aunque en este caso es un ajuste sobre una regla ya existente, mas simple que una regla nueva desde cero), filtro/columna en listado (0.5h adicional, reutiliza el patron DataTables ya presente en todos los listados del sistema, mas bajo que el piso generico 1h por tratarse de una sola columna+filtro simple), migracion EF (0.5h, sin backfill). Suma ajustada a M=2.2h.

### PASO 6 — PERT y contingencia

| Modulo | PERT = (O+4M+P)/6 | Riesgo | Cont. | Hs finales |
|---|---:|---|---:|---:|
| M10 | 1.033 | Bajo | 8% | 1.116 |
| M11 | 2.267 | Medio | 15% | 2.607 |
| M12 | 0.412 | Bajo | 8% | 0.445 |
| **TOTAL** | **3.712** | | | **4.168** |

Riesgo M11 clasificado Medio (no Bajo) porque modifica una regla de unicidad ya viva en produccion (RN-11 -> RN-24) sobre una entidad con datos reales; riesgo de edge case en el manejo de NULL, mitigado por reutilizar el mismo patron de Service ya validado en la arquitectura original.

Sin doble contingencia (aplicada una unica vez por item, sobre PERT).

### PASO 7 — Sanity check por item
M10 (0.67) y M12 (0.80) estan por debajo de 0.85 pero justificados por reutilizacion literal de patron ya construido 2 veces en el mismo proyecto (regla de "segunda/tercera ronda"). M11 no tiene ratio M/mediana unico por construirse como suma de items de la tabla de modificaciones (ya son pisos de rango por diseno).

### PASO 8 — Sanity check del total del proyecto
Lote muy chico (3.6h M) comparado con SESION 3 (11.5h M, 3 modulos) y con el presupuesto inicial (26.0h M, 6 modulos). Coherente: este pedido es una sola dimension nueva (un catalogo + una FK opcional), sin pantalla dinamica ni logica de calculo nueva, muy por debajo de cualquier modulo de las rondas anteriores. Sin correccion adicional.

### PASO 9 — Cierre numerico
Paso A (preliminar) = Paso B (final): sin ajuste adicional post sanity-check. M base total = 3.6h.

### Resumen economico (formula vigente: Costo = M x $16.80)

| Modulo | M (h) | USD base |
|---|---:|---:|
| M10 ABM Centro de Salud | 1.0 | $16.80 |
| M11 CentroSaludId en Produccion Mensual (FK + selector + RN-24 + listado) | 2.2 | $36.96 |
| M12 Centro de Salud en encabezado PDF | 0.4 | $6.72 |
| **Subtotal desarrollo** | **3.6** | **$60.48** |

Horas facturables internas (M/2.5x1.20): 1.728h — **por debajo del piso de 4h**, por lo que **no aplica cargo de Tokens IA** (regla vigente: "No aplica a iteraciones evolutivas menores a 4 h facturables, salvo indicacion contraria").

| Concepto | USD |
|---|---:|
| Subtotal desarrollo | 60.48 |
| Tokens IA | No aplica (bajo piso de 4h facturables) |
| **TOTAL CLIENTE** | **60.48** |

### Division por etapas
Alcance chico sin dependencias fuertes entre items (M11 depende solo de que M10 este resuelto para poblar el selector). Se propone **entrega en una sola etapa** (igual que la SESION 3 anterior, donde el cliente prefirio no dividir la entrega tecnica): M10+M11+M12 juntos. Subtotal unico: **USD 60.48**.

### Mantenimiento anual
**Atencion:** la tabla nueva `CentrosSalud` sube el conteo de tablas del sistema (~15 segun ultimo registro de SESION 3) a ~16, lo que **cruzaria el umbral del Plan PRO (6-15 tablas, USD 300/año) hacia Plan PREMIUM (16-30 tablas, USD 400/año)**. Se deja como punto a confirmar con el cliente al cierre — no se factura el upgrade automaticamente sin confirmar el conteo exacto de tablas vigente.

### Riesgos y supuestos
- Riesgo de regla de unicidad (RA-10 de arquitectura): mitigado por reutilizar el mismo patron de validacion en Service ya usado para Mes+Anio, cubierto dentro de la contingencia Medio (15%) de M11.
- Supuesto: no se pide vincular `CentroSalud` con el catalogo `Mutual` de FABA (decision explicita del cliente, P12) — si se pide en el futuro, es alcance adicional a presupuestar aparte.
- Supuesto: no se pide migrar/asignar retroactivamente los periodos historicos a un Centro de Salud (P13) — si se pide, es alcance adicional (tarea de datos, no de desarrollo).

### Pruebas minimas requeridas
- M10: crear, editar y dar de baja logica un Centro de Salud de cada Tipo (Privado/Mutual); verificar que aparece/desaparece del selector de Produccion Mensual segun su estado Activo.
- M11: crear 2 periodos para el mismo Mes/Anio con distinto Centro de Salud (debe permitirlo); intentar crear un duplicado exacto (mismo Mes+Anio+Centro, y tambien mismo Mes+Anio sin centro ya existente) y verificar que el sistema lo bloquea; verificar columna y filtro por Centro de Salud en el listado.
- M12: generar el PDF de un periodo con Centro de Salud asignado y de uno sin asignar, verificar que la linea aparece solo en el primero.

### Checklist de salida para merge
- Migracion EF generada y aplicada a base de desarrollo (sin backfill requerido).
- Build OK sin warnings nuevos.
- Verificacion manual de los 3 flujos (M10, M11, M12) segun pruebas minimas.
- `docs/labipac/definiciones/5-implementador.md` y `6-qa.md` actualizados al cierre.

### Condiciones comerciales
50% al inicio / 50% a la entrega. Sin clausula de validez de oferta (regla vigente).

### Estado
**PRESUPUESTO CERRADO Y APROBADO POR EL CLIENTE** (2026-07-23, USD 60.48, entrega en una sola etapa). Gate abierto — implementacion delegada y cerrada, ver `5-implementador.md` sesion 4. Pendiente: cierre de calibracion con horas reales.

## SESION 3 (2026-07-08) — Presupuesto de 3 mejoras

Input: `1-analista-funcional.md` sesion 4, `2-disenador-funcional.md` sesion 2, `3-arquitecto-mvc.md` sesion 2 — todos cerrados y aprobados.

### PASO 0 — Anclaje historico
Referencia primaria: **la propia memoria de labipac** (mismo proyecto, mismo stack, mismo equipo). Cierre real anterior: 6 modulos, 26.0h M base estimado -> 12.0h reales (ratio M/real ~2.17x, productividad observada 2.0h/modulo). La nota de calibracion de esa sesion ya recomendaba "bajar banda M... si no hay workflow de estados" para proximos presupuestos similares — se aplica aqui.
Referencias secundarias cross-proyecto: Ganaderia (referencia comercial, 20h reales/8 modulos), vinosefue sprint compras (7.07x record del dataset, iteracion evolutiva con reutilizacion de patrones ya resueltos).

### PASO 1-3 — Modulos funcionales identificados y drivers

| Modulo | Tipo | Drivers |
|---|---|---|
| M7 Unidad y Precio por Unidad en Perfiles | Modificacion de modulo existente (logica de precios) | +1 campo (Unidad), +1 entidad simple de configuracion (fila unica), recalculo automatico (create/edit + batch), panel Precio por Unidad + aumento % (reutiliza patron visual/AJAX de la card IVA ya implementada), remocion de RN-01, relajacion global RN-02, simplificacion de PreciosController (se elimina cascade UB->Perfil), 1 migracion EF con backfill de datos |
| M8 Carga masiva + alta rapida de Perfiles/Practicas | Pantalla nueva sobre modulo existente | Pantalla nueva con filas repetibles (JS nuevo), 2 modales de alta rapida via AJAX (reutilizan CreateAsync de servicios ya existentes), guardado atomico nuevo (`AgregarLineasAsync`), reutiliza AJAX `GetPrecioItem` ya existente |
| M9 Fix ancho de columna PDF | Ajuste puntual | Cambio de 2 valores `ConstantColumn` en reporte ya existente, sin logica nueva |

### PASO 4-5 — M ajustado, O y P

| Modulo | Referencia / mediana base | Ratio M/mediana | O | M | P |
|---|---|---|---|---|---|
| M7 | M2 Practicas (mismo proyecto, build original completo del ABM Practica: 6.0h) | 0.75 | 3.0 | 4.5 | 7.0 |
| M8 | M3 Produccion Mensual+Historial (mismo proyecto, build original de Detalle+modales+AJAX: 8.5h) / cross-proyecto ABM complejo padre-hijos (7.7-11.5h) | 0.76 (vs M3) / 0.84 (vs piso cross-proyecto) | 4.5 | 6.5 | 10.0 |
| M9 | Ajuste puntual (tabla, mediana ~0.75h) | 0.67 | 0.3 | 0.5 | 0.8 |

**Justificacion de ratios por debajo de 0.85 (simplificacion real confirmada, no omision):**
- M7: no se reconstruye el ABM de Practica (ya existe) — solo se le agrega un campo y se cambia el origen del precio; la UI de configuracion reutiliza literalmente el patron visual+AJAX de la card "IVA del período" ya construida en `Detalle.cshtml`; `PreciosController` pierde codigo (se elimina el bloque de cascade), no gana.
- M8: reutiliza el AJAX `GetPrecioItem` y el `CreateAsync` de ambos servicios (Practica/UnidadBioquimica) para las altas rapidas — no se construye logica de precio ni de ABM desde cero, solo el envoltorio de pantalla + filas dinamicas + guardado batch.

### PASO 6 — PERT y contingencia

| Modulo | PERT = (O+4M+P)/6 | Riesgo | Cont. | Hs finales |
|---|---:|---|---:|---:|
| M7 | 4.667 | Medio | 15% | 5.367 |
| M8 | 6.750 | Medio | 15% | 7.763 |
| M9 | 0.517 | Bajo | 8% | 0.558 |
| **TOTAL** | **11.933** | | | **13.687** |

Sin doble contingencia (aplicada una unica vez por item, sobre PERT).

### PASO 7 — Sanity check por item
Todos los ratios M/mediana caen en 0.67-0.76 (fuera del rango 0.85-1.15) pero con justificacion de reutilizacion real documentada arriba (regla: "ratio menor a 0.85 -> revisar omisiones o justificar simplificacion real" — se opta por justificar, no por subir M artificialmente, porque la reutilizacion es verificable en el codigo actual).

### PASO 8 — Sanity check del total del proyecto
Comparable directo: la propia sesion anterior de labipac (6 modulos, 26.0h M, cerro en 12.0h reales) y el sprint de vinosefue (8 items, reconstruccion 23.8h M, cerro en 4h reales por alta reutilizacion). Este lote: 3 modulos, 11.5h M base = 3.83h/modulo, por debajo de los 4.33h/modulo del lote anterior de labipac — coherente con que 2 de los 3 items son modificaciones sobre un sistema ya maduro (mas superficie reutilizable que en la sesion anterior) y el tercero es trivial. Sin correccion adicional.

### PASO 9 — Cierre numerico
Paso A (preliminar) = Paso B (final): sin ajuste adicional post sanity-check. M base total = 11.5h.

### Resumen economico (formula vigente: Costo = M x $16.80)

| Modulo | M (h) | USD base |
|---|---:|---:|
| M7 Unidad y Precio por Unidad en Perfiles | 4.5 | $75.60 |
| M8 Carga masiva + alta rapida | 6.5 | $109.20 |
| M9 Fix columna PDF | 0.5 | $8.40 |
| **Subtotal desarrollo** | **11.5** | **$193.20** |

Horas facturables internas (M/2.5x1.20): 5.52h — por encima del piso de 4h, aplica cargo de Tokens IA.

| Concepto | USD |
|---|---:|
| Subtotal desarrollo (sin Tokens IA) | 193.20 |
| Tokens IA (10% del total presupuestado) | 19.32 |
| **TOTAL CLIENTE** | **212.52** |

### Division por etapas
- **Etapa 1 (MVP operable):** M7 (Unidad y Precio por Unidad — corrige el modelo de precio de base) + M9 (fix PDF — defecto visual ya en produccion). Subtotal: **USD 84.00**.
- **Etapa 2 (resto del alcance):** M8 (Carga masiva + alta rapida — mejora de productividad, depende de que M7 este resuelto para que el alta rapida de Perfil calcule el precio en vivo). Subtotal: **USD 109.20**.
- Justificacion del orden: M7 corrige un modelo de precio que hoy convive en conflicto con F-001 (riesgo activo de inconsistencia si no se resuelve primero); M9 es un fix de bajo costo y alto valor percibido inmediato; M8 es la mejora de UX que puede esperar un segundo tramo sin bloquear la operacion diaria.

### Mantenimiento anual
Sin cambio de plan: la nueva tabla `PreciosPorUnidad` lleva el conteo de tablas de ~14 a ~15, dentro del mismo rango del **Plan PRO (6-15 tablas) — USD 300/año**, ya vigente para este proyecto (ver cierre 2026-06-23). No corresponde upgrade de plan.

### Riesgos y supuestos
- Riesgo de migracion con backfill de datos (RA-06 de arquitectura): mitigado con formula de aproximacion automatica confirmada por el cliente, pero requiere revision manual posterior de los Perfiles existentes — se aclara como tarea del cliente post-deploy, no una entrega tecnica adicional.
- Riesgo de regresion en `PreciosController` al remover el cascade UB->Perfil: cubierto dentro de la contingencia Medio (15%) de M7.
- Supuesto: no se requiere pantalla de historial de cambios de `PrecioPorUnidad` (solo el valor vigente) — si el cliente pide auditoria visible de cambios de precio por unidad, es alcance adicional (ya cubierto informalmente por el AuditLog automatico del sistema, pero sin UI dedicada).

### Pruebas minimas requeridas
- M7: crear/editar un Perfil con distintos valores de Unidad y verificar el precio calculado; editar el Precio por Unidad a mano y verificar recalculo batch de todos los Perfiles activos; aplicar un aumento % y verificar el nuevo valor y el recalculo; verificar que `Precios/AumentoMasivo` ya no ofrece Perfiles.
- M8: cargar 3+ filas de tipos mixtos (Perfil y Practica) en un solo submit y verificar guardado atomico; forzar un error en una fila (cantidad invalida) y verificar que no se guarda ninguna; crear un Perfil nuevo y una Practica nueva desde los modales de alta rapida y verificar que aparecen seleccionados en la fila de origen sin recargar.
- M9: generar el PDF de un periodo con montos de 4+ digitos y verificar que "Precio unit." no corta digitos.

### Checklist de salida para merge
- Migracion EF generada y aplicada a base de desarrollo, incluyendo el backfill de `Unidad`.
- Build OK sin warnings nuevos.
- Verificacion manual de los 3 flujos (M7, M8, M9) segun pruebas minimas.
- `docs/labipac/definiciones/5-implementador.md` y `6-qa.md` actualizados al cierre.

### Condiciones comerciales
50% al inicio / 50% a la entrega de cada etapa. Sin clausula de validez de oferta (regla vigente).

## Items presupuestables (historico acumulado)

| Modulo | Tipo | M (h) | USD base (M×$16.80) |
|---|---|---|---|
| M1 Unidades Bioquimicas | ABM simple | 1.5 | $25.20 |
| M2 Practicas | ABM intermedio | 6.0 | $100.80 |
| M3 Produccion Mensual + Historial | ABM complejo cabecera/detalle | 8.5 | $142.80 |
| M4 Infra transversal | Ajustes puntuales | 1.5 | $25.20 |
| M5 Pacientes | ABM intermedio | 3.5 | $58.80 |
| M6 Integracion parcial FABA (analitos, mutuales, consulta pacientes) | Integracion externa parcial | 5.0 | $84.00 |
| M7 Unidad y Precio por Unidad en Perfiles | Modificacion modulo existente | 4.5 | $75.60 |
| M8 Carga masiva + alta rapida Perfiles/Practicas | Pantalla nueva sobre modulo existente | 6.5 | $109.20 |
| M9 Fix columna PDF Produccion Mensual | Ajuste puntual | 0.5 | $8.40 |
| **TOTAL DESARROLLO ACUMULADO (sin Tokens IA)** | | **37.5** | **$630.60** |

## Cierre de calibracion SESION 3 (2026-07-08) — M7+M8+M9 + 3 fixes post-QA

Cliente confirmo verificacion funcional OK (incluye los 3 hallazgos post-QA: Details sin Unidad, combo de composicion no preseleccionaba por bug real de soft-delete, columna Unidad faltante en Produccion Mensual/Detalle) y reporto horas reales.

- **Horas reales de desarrollo informadas: 2.0h** (cubre el sprint completo: M7+M8+M9 + los 3 fixes de la ronda posterior de QA manual).
- Estimado base (M): 11.5h -> desvio: -82.6% (real muy por debajo del estimado).
- Estimado PERT sin contingencia: 11.93h -> desvio: -83.2%.
- Estimado con contingencia (Hs finales): 13.69h -> desvio: -85.4%.
- Horas facturables formula vigente (M/2.5×1.20): 5.52h -> desvio vs real: -63.8%.

| Ratio | Valor | Comparacion con record del dataset |
|---|---:|---|
| M base / real | 5.75x | por debajo del record (vinosefue 7.07x en PERT/real) |
| PERT-contingencia / real | 6.84x | **segundo mas alto del dataset**, detras de vinosefue (7.07x) |
| Formula vigente (M/2.5×1.20) / real | 2.76x | **segundo mas alto del dataset**, detras de vinosefue (2.86x) |

**Lectura de calibracion:** confirma el mismo patron que vinosefue (2026-07-03) — cuando el alcance es una **iteracion evolutiva sobre un sistema ya maduro con alta reutilizacion de patrones ya resueltos** (en este caso: patron visual/AJAX de la card IVA de F-002 reutilizado para Precio por Unidad, `GetPrecioItem` y `CreateAsync` reutilizados en carga masiva, `PreciosController` simplificado en vez de ampliado), la sobreestimacion es sistematica y mucho mayor que en modulos genuinamente nuevos. Los ratios M/mediana ya se habian ajustado a la baja (0.67-0.76) en el Paso 4-5 con justificacion de reutilizacion documentada, pero igual resultaron altos frente al real — sugiere que incluso esa correccion se quedo corta para este patron especifico de proyecto (labipac ya tenia 2 sesiones previas de alta reutilizacion, ver cierre de 2026-06-23 con ratio 2.17x).

**Accion de recalibracion:** para labipac especificamente, y para cualquier proyecto en su segunda o tercera ronda de mejoras sobre el mismo modulo (no la primera implementacion), aplicar un descuento adicional sobre la banda M ya ajustada por reutilizacion: usar el piso del rango "Modificacion sobre modulo existente" (27-presupuesto-parametros) en vez de la mediana, y tratar la "Pantalla nueva" del rango ABM-complejo como excepcion solo si NO reutiliza AJAX/servicios ya existentes en el mismo repo. Se traslada esta observacion a `27-presupuesto-parametros.instructions.md` (dataset cross-proyecto) para que futuros presupuestos de cualquier proyecto la tengan disponible.

## Items presupuestables

| Modulo | Tipo | M (h) | USD base (M×$16.80) |
|---|---|---|---|
| M1 Unidades Bioquimicas | ABM simple | 1.5 | $25.20 |
| M2 Practicas | ABM intermedio | 6.0 | $100.80 |
| M3 Produccion Mensual + Historial | ABM complejo cabecera/detalle | 8.5 | $142.80 |
| M4 Infra transversal | Ajustes puntuales | 1.5 | $25.20 |
| M5 Pacientes | ABM intermedio | 3.5 | $58.80 |
| M6 Integracion parcial FABA (analitos, mutuales, consulta pacientes) | Integracion externa parcial | 5.0 | $84.00 |
| **TOTAL DESARROLLO (sin Tokens IA)** | | **26.0** | **$436.80** |

## Resumen economico para cliente

| Concepto | USD |
|---|---:|
| Subtotal desarrollo (sin Tokens IA) | $436.80 |
| Tokens IA (item individual) | $132.20 |
| **TOTAL CLIENTE** | **$569.00** |

Factor cliente/desarrollo: 569/436.8 = 1.3027.

## Estimacion por esfuerzo

| Modulo | O | M | P | PERT | Riesgo | Cont. | Hs finales |
|---|---|---|---|---|---|---|---|
| M1 | 1.0 | 1.5 | 2.5 | 1.58 | Bajo | 8% | 1.71 |
| M2 | 4.0 | 6.0 | 9.0 | 6.17 | Medio | 15% | 7.09 |
| M3 | 6.0 | 8.5 | 13.0 | 8.83 | Medio | 15% | 10.16 |
| M4 | 1.0 | 1.5 | 2.5 | 1.58 | Bajo | 8% | 1.71 |
| M5 | 2.0 | 3.5 | 5.0 | 3.50 | Medio | 15% | 4.03 |
| M6 | 3.0 | 5.0 | 8.0 | 5.17 | Alto | 25% | 6.46 |
| TOTAL | 17.0 | 26.0 | 40.0 | 26.83 | | | 31.16 |

## Anclaje historico por modulo

| Modulo | Referencia | Mediana base | Ratio M/mediana | Decision |
|---|---|---|---|---|
| M1 | ABM Camiones/Categorias (1.5h) | 1.5h | 1.00 | Mantener |
| M2 | ABM intermedios Lumitrack/Delicias (5.0h) | 5.0h | 1.20 | Justificado: 5 drivers concretos (Select2 M:N, sumatoria JS, RN-01 server, IgnoreQueryFilters, Details) |
| M3 | ShowroomGriffin cabecera/detalle (9.6h) | 9.6h | 0.885 | Mantener: sin workflow (P4-A), drivers AJAX+P5-B sostienen |
| M4 | ShowroomGriffin infra (0.5h/migracion) | 0.5h/migracion | 1.00 | Mantener |
| M5 | ABM intermedio generico (3.0h) | 3.0h | 1.17 | Mantener: ABM con validaciones y busqueda |
| M6 | Integraciones parciales API (4.5h) | 4.5h | 1.11 | Mantener: mapeo externo + consumo parcial por catalogos |

## Sanity check del total

- Comparable: eleven-la-plata (50h, 27 modulos simples). labipac 6 modulos mix simple/intermedio/complejo/integracion parcial -> 4.33h/modulo coherente.
- ShowroomGriffin (7.87h/modulo): labipac por debajo, correcto (sin workflow complejo y con integracion parcial acotada).
- Rango esperado sistema pequenio-mediano 5-7 modulos: 18-32h -> labipac 26.0h dentro de rango. Sin correccion.

## Cierre

- Paso A = Paso B = 26.0h M base / $436.80 base / $569 cliente (con IA)
- Doble contingencia: NO aplicada (unica vez por item)
- Etapa 1: todo el alcance (USD 569). Etapa 2: sin modulos adicionales definidos.
- Mantenimiento anual: Plan PRO (14 tablas, 6-15) — USD 300/anio
- Condiciones: 50/50 por etapa.

## Cierre de calibracion estimado vs real

- Horas reales de desarrollo informadas: 12.0h
- Estimado base (M): 26.0h -> desvio: -53.85%
- Estimado con contingencia (Hs finales): 31.16h -> desvio: -61.49%
- Productividad real observada: 2.00h/modulo (6 modulos)
- Lectura de calibracion: sobreestimacion en M/P para modulos ABM e integracion parcial de baja profundidad.
- Accion de recalibracion sugerida: para proximos presupuestos similares, bajar banda M de integraciones parciales y usar P mas acotado si no hay workflow de estados ni sincronizacion bidireccional.

## Riesgos y contingencia

- M1: 8% (riesgo bajo — ABM estandar)
- M2: 15% (riesgo medio — logica JS + IgnoreQueryFilters + M:N)
- M3: 15% (riesgo medio — AJAX + snapshot + multiples validaciones)
- M4: 8% (riesgo bajo — ajustes tecnicos puros)
- M5: 15% (riesgo medio — ABM con validaciones de identidad y busqueda)
- M6: 25% (riesgo alto — integracion externa parcial FABA, posibles variaciones de contrato)

## Historial de ajustes
- 2026-06-13: Presupuesto inicial cerrado. 4 modulos, 17.5h M total, $294 base, $394 cliente (con IA implicit). Metodo PERT pasos 0-9 completo. Sanity check OK. Sin doble contingencia. Listo para presentar al cliente.
- 2026-06-23: Presupuesto actualizado por ampliacion de alcance implementado (ABM Pacientes + integracion parcial FABA para analitos, mutuales y consulta de pacientes). Nuevo total: 6 modulos, 26.0h M, $436.80 base, $569 cliente. Se registra cierre real con 12.0h ejecutadas y desvio de -53.85% vs M base para calibracion futura.
- 2026-06-23: Se ajusta formato para mostrar Tokens IA como item individual explicito en el resumen economico del presupuesto (sin prorrateo visible en modulos), manteniendo el total cliente en USD 569.00.
- 2026-07-08: SESION 3 cerrada con presupuesto de 3 mejoras (M7 Unidad/PrecioPorUnidad $75.60, M8 Carga masiva $109.20, M9 fix PDF $8.40; total USD 212.52 con Tokens IA). Cliente aprobo y pidio entrega en una sola pasada. Implementado, QA sin bloqueantes, 3 hallazgos de pruebas manuales corregidos (incluyo 1 bug real de perdida de datos por soft-delete en combo de composicion). Cliente confirmo verificacion OK y reporto 2.0h reales totales. Cierre de calibracion: ratio PERT-contingencia/real 6.84x y formula/real 2.76x, ambos segundo lugar del dataset detras de vinosefue (7.07x/2.86x) — mismo patron de sobreestimacion en iteraciones evolutivas de alta reutilizacion, ya en su 3ra ronda de mejoras sobre el mismo sistema. Accion trasladada a 27-presupuesto-parametros.instructions.md.
