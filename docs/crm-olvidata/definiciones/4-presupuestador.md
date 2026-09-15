# Memoria - Presupuestador

## Proyecto: crm-olvidata — CRM interno de OlvidataSoft
## Ultima actualizacion: 2026-09-14

## Definiciones vigentes

### Nota de alcance: proyecto interno, sin facturación a cliente externo

`crm-olvidata` es la herramienta propia de OlvidataSoft (owner = Joaquín Bourdin, el mismo estudio) — no hay un cliente externo al que cotizar. Esta ficha se usa igual, con la misma metodología PERT/horas del resto del dataset, **solo como estimación interna de esfuerzo** (para priorizar y para llevar registro de costo real de mantener el propio sistema) — no se aplica el aparato de precio al cliente (Tokens IA 25%, descuento de expansión agresiva, descuento por volumen, planes de mantenimiento, condiciones 50/50, documento `presupuesto-cliente.md`): esas secciones de `27-presupuesto-parametros.instructions.md` son para Build/Merge de clientes de pago, no aplican acá. El costo interno equivalente se calcula con la fórmula de trabajo evolutivo sobre sistema propio (`M / 2.5 × 1.20 × USD 35 = M × USD 16,80`, fork vigente de Merge/post-entrega), el mismo criterio del sprint 2026-08-27.

**Indicación de Joaquín (2026-09-14): "es para uso personal, no aplicar regla de presupuesto".** El gate de aprobación de presupuesto no bloquea la implementación en este proyecto: la estimación queda solo como referencia para el cierre de calibración, y se pasa directo a Implementación y QA.

### Calibración propia del proyecto (ancla obligatoria para rondas nuevas)

**Sprint 2026-08-27 "corrección de bugs/gaps de auditoría + 3 mejoras" — CIERRE REAL.** 17 items, estimado 22.0 h M base / 22.5 h PERT / 10.56 h facturables (≈ USD 370 equivalente). Real ≈ **2.5-3 h** (1.18 h de ejecución de subagentes — Implementador 18.4 + 12.2 min, QA 27.0 + 13.1 min — más ≈1-1.5 h de orquestación, deploy y documentación). Ratio PERT/real ≈ 7.5x-9x. Único retrabajo real: vocabulario de `Contacto.Rubro` no declarado en Arquitectura (regla derivada: la arquitectura declara el vocabulario canónico antes de implementar — aplicada en la feature vigente con `CategoriaHelpers`/`GanchoHelpers`).

### Feature vigente: "4 frentes — combo con gancho" (2026-09-14) — APROBADA, ALCANCE COMPLETO E1-E7

Entrada: `1-analista-funcional.md` (CU-30 a CU-35), `2-disenador-funcional.md` §8 y `3-arquitecto-mvc.md` §7.2 (aprobada con A1-a y A2). Estimación aprobada por Joaquín el 2026-09-14 con alcance completo (E1-E7, incluida E6). Implementación habilitada.

#### Paso 0 — Anclaje histórico

- **Ancla principal:** sprint propio 2026-08-27 (arriba), mismo repo, mismo tipo de trabajo (reglas de negocio + pantallas existentes + un helper compartido), 22 h M → 2.5-3 h reales.
- **Clasificación:** iteración evolutiva sobre módulos existentes (arquitecto §7.2.0: reutilización literal intra-repo; PAT-031 es patrón sin código portable). Todos los items anclados en "Modificación sobre módulo existente" (`dataset.yml` → `modificacion_modulo_existente`), nunca en rangos de módulo nuevo.
- **Regla de segunda/tercera ronda sobre el mismo proyecto:** aplica (rondas previas: migración 07/14, campañas 07/21, gestión comercial 08/14, sprint 08/27, LLM 09/13-14). Se usa el **piso** de cada fila: regla de negocio 1 h, campo simple 0.5 h, migración 0.5 h, pantalla modificada que reutiliza patrón 0.5-1 h.
- **Paso 0.5 (consulta a `olvidata-ceo`):** no aplica — proyecto interno, sin precio.

#### Pasos 1-6 — Tabla por etapa funcional

| Etapa | Tipo | Drivers | O | M | P | PERT | Riesgo | Cont. | Horas finales | Hs. fact. (M/2.5×1.2) | USD equiv. (M×16,80) |
|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| E1 Vocabulario y árbol | Regla de negocio ×2 | `CategoriaHelpers` (fuente única, 3 consumidores), cuestionarios nuevos, `TryGetValue` + escalada, `merge` fuera de IA | 1.5 | 2.0 | 3.0 | 2.08 | Bajo | 8% | 2.25 | 0.96 | 33.60 |
| E2 Prompt de la IA | Regla de negocio + verificación LLM | Identidad 4 frentes, descripciones/ejemplos, venta cruzada, cliente actual; prueba contra producción con mensajes de test | 1.0 | 1.5 | 2.5 | 1.58 | Medio | 15% | 1.82 | 0.72 | 25.20 |
| E3 Gancho en contacto | 5 campos + migración + regla de decisión + 2 pantallas existentes | Enum + props + `AsignarGancho` (0.5), migración (0.5), `GanchoHelpers` dominios + tabla (1.5), alta Maps + carga inicial + botón (1.0), Contactos Index/Create/Edit/Details (1.5), Chats filtro/chip/card (1.0) | 4.0 | 6.0 | 9.0 | 6.17 | Medio | 15% | 7.10 | 2.88 | 100.80 |
| E4 Conversación por gancho | Regla de negocio ×2 en el webhook | `OnConfirmarContinuarAsync` por gancho, pregunta 1 por frente, contexto de gancho en la IA | 1.5 | 2.0 | 3.5 | 2.17 | Medio | 15% | 2.50 | 0.96 | 33.60 |
| E5 Envío por gancho | Regla de negocio en envío facturable + config + diagnóstico | `ResolverPlantilla` + filtro antes del `Take(cupo)` + 4 casos `BuildComponents` (1.5), card `/Bot` + 2 acciones (1.5), `/Bot/Salud` + fix `TemplatesSinCampana` (0.5), guardas rename/delete de Templates (0.5), A1-a follow-up/frío (1.0) | 3.5 | 5.0 | 8.0 | 5.25 | Alto | 25% | 6.56 | 2.40 | 84.00 |
| E6 Módulos por frente | Campo + refactor de consulta compartida + pantallas existentes | `Frente` (en la migración de E3), `ModuloCatalogoQueries` (1.0), Módulos Create/Edit/Index (1.0), Armar presupuesto multi-frente (1.5) | 2.5 | 3.5 | 6.0 | 3.75 | Medio | 15% | 4.31 | 1.68 | 58.80 |
| E7 Documentación | Ajuste documental | `arbol-comunicacion-bot.md`, `logica-negocio-bot.md` | 0.5 | 1.0 | 1.5 | 1.00 | Bajo | 8% | 1.08 | 0.48 | 16.80 |
| **Total** | | | **14.5** | **21.0** | **33.5** | **22.00** | | | **25.62** | **10.08** | **352.80** |

Distribución interna del esfuerzo (sobre M, no suma aparte): ≈70% implementación, ≈20% pruebas (QA automatizada por navegador + mensajes de test al webhook), ≈10% documentación y deploy.

#### Paso 7 — Autocorrección por item

| Etapa | Referencia | Ratio (PERT / referencia) | Ajuste | Motivo |
|---|---|---:|---|---|
| E1 | Regla de negocio ×2, piso 2 × 1 h | 1.04 | Mantener | Dentro de banda |
| E2 | Regla de negocio 1 h + verificación contra producción (sprint LLM 09/13 (11), mismo tipo de trabajo) ≈ 1.5 h | 1.05 | Mantener | La verificación con mensajes de test es obligatoria: el cambio es de comportamiento, no de código |
| E3 | Suma de pisos: 3 campos/props 0.5 + migración 0.5 + 2 reglas 2.0 + carga inicial 1.0 + 2 pantallas 2.0 = 6.0 h | 1.03 | Mantener | Dentro de banda |
| E4 | Regla de negocio ×2, piso 2 × 1 h | 1.08 | Mantener | P algo más alto: camino crítico del webhook (CRM-020) |
| E5 | Reglas ×3 3.0 + config/pantalla 1.0 + guardas 1.0 = 5.0 h | 1.05 | Mantener | Riesgo alto por envío facturable y tope de gasto (CRM-017), no por volumen de código |
| E6 | Refactor de consulta 1.0 + campo 0.5 + pantallas 2.0 = 3.5 h | 1.07 | Mantener | Checklist agrupado por frente es la única pieza con algo de UI nueva |
| E7 | Ajuste documental 1 h | 1.00 | Mantener | — |

#### Paso 8 — Sanity check del total

- **Comparable:** sprint propio 2026-08-27 — 22.0 h M base, 17 items de modificación sobre el mismo repo.
- **Esta feature:** 21.0 h M base, 7 etapas (≈30 items chicos).
- **Ratio total:** 21.0 / 22.0 = **0.95** → dentro de 0.80-1.20, se mantiene.
- **Expectativa real calibrada (dato interno, no reemplaza al PERT):** con el ratio propio de 7.5-9x sobre 25.62 h con contingencia, el real esperado ronda **3-3.5 h**. Techo realista **4.5-5 h**, porque E2 y E5 exigen verificación contra producción (webhook y envío real), que el sprint 08/27 no tuvo.

#### Paso 9 — Cierre numérico en dos pasos

- **Paso A (preliminar):** 22.00 h PERT → 25.62 h con contingencia variable por etapa.
- **Paso B (final):** sin cambios. Sanity check en 0.95, contingencia aplicada una sola vez por etapa (sin recargo global). **21.0 h M base / 25.62 h techo interno / 10.08 h facturables / ≈ USD 353 de costo interno equivalente.**

#### Etapas (entrega interna)

| Etapa | Contenido | M (h) | USD equiv. | Desplegable sola |
|---|---|---:|---:|---|
| **Etapa 1 — Mejora inmediata del inbound** | E1 + E2 | 3.5 | 58.80 | **Sí.** Sin migración, sin tocar el envío. La IA clasifica y conversa con los 4 frentes desde el día del deploy (el inbound de ads sigue entrando con el outbound pausado) |
| **Etapa 2 — Reactivación del outbound con el combo** | E3 + E4 + E5 + E7 | 14.0 | 235.20 | Sí, en bloque. La migración va en E3. Para **enviar** además hacen falta los textos de marketing y la aprobación de Meta de las 4 plantillas (días, no horas) |
| **Etapa 2b — Módulos por frente (diferible)** | E6 | 3.5 | 58.80 | Sí. Se puede postergar sin bloquear el outbound: sin módulos cargados, la IA y el árbol usan la pregunta fija. Si se posterga, su columna sale de la migración de E3 (arquitecto 7.2.9) |
| **Total** | | **21.0** | **352.80** | |

#### Paso 10 — Costo interno de IA (sombra, solo estudio)

| Concepto | Cálculo | USD |
|---|---|---:|
| E1 | 0.96 h × USD 4 | 3.84 |
| E2 | 0.72 h × USD 4 | 2.88 |
| E3 | 2.88 h × USD 4 | 11.52 |
| E4 | 0.96 h × USD 4 | 3.84 |
| E5 | 2.40 h × USD 4 | 9.60 |
| E6 | 1.68 h × USD 4 | 6.72 |
| E7 | 0.48 h × USD 4 | 1.92 |
| Overhead Ask-mode | 6 h × USD 1 (Discovery→Presupuesto de esta feature fue más largo que el placeholder de 4 h: 2 rondas de rediseño y lectura extensa del código) | 6.00 |
| **Total** | | **≈ 46.32** |

Umbral 15% no aplica (no hay precio de lista que proteger). Dato de trazabilidad: al cierre, registrar el costo real de las sesiones de Implementador/QA para calibrar `tarifa_Opus_USD_hora`.

**Costos de operación que NO son horas y no entran en la tabla** (para que no se lean como omisión): reescritura de la cache del prompt una vez al desplegar E2 (≈ USD 0,03); mensajería de Meta y consumo de IA de las plantillas y conversaciones reales, ya gobernados por el tope único mensual de `/Bot`.

#### Riesgos y supuestos

- **Dependencias externas, sin horas:** textos de las 4 plantillas por `olvidata-marketing`; aprobación de Meta (puede tardar días o rechazarse → reestimar E5 si hay que rehacer parámetros); contenido de módulos por frente por `olvidata-presupuesto-bot` (E6); precio del paquete combo por `olvidata-ceo` (no afecta horas, sí la primera propuesta real).
- **Riesgo alto en E5:** es el único punto que gasta plata real; un error en el filtro antes del `Take(cupo)` o en la exclusión del follow-up (A1-a) afecta volumen y tope. Contingencia 25% ya aplicada solo ahí.
- **E2 no es determinístico:** la verificación del prompt puede pedir una vuelta extra de ajuste de texto (cubierta por P).
- **Supuesto:** outbound y Places siguen pausados hasta cerrar la Etapa 2 (S4), así no hay que coordinar el deploy con envíos en curso.
- **Gatillos de reestimación:** rechazo de Meta que cambie los parámetros de plantilla; decisión de hacer A1-c (plantillas de follow-up combo); cambio de la tabla de grupos por rubro o de la lista de dominios después de implementar E3.

#### Pruebas mínimas requeridas

Las 10 de `3-arquitecto-mvc.md` §7.2.10, más la regresión explícita del camino actual: `v13` + A/B de campaña sin gancho, Armar presupuesto solo Build idéntico, y endpoints nuevos ejercitados con base vacía (MH-001).

#### Checklist de salida para merge

- [ ] `dotnet build -c Release` sin errores.
- [ ] Migración `AddGanchoYFrenteComercial` aplicada en `olvidatacrm_dev` y después en producción; módulos existentes en Build, contactos existentes consistentes.
- [ ] QA GO sobre las pruebas mínimas (incluye mensajes de test al webhook para E2/E4).
- [ ] Deploy verificado (sitio 200, `/Bot` y `/Bot/Salud` sin 500).
- [ ] Outbound sigue pausado hasta que haya al menos 1 plantilla combo aprobada y configurada.
- [ ] `arbol-comunicacion-bot.md` y `logica-negocio-bot.md` actualizados (E7).
- [ ] Reglas nuevas generalizables llevadas al catálogo `32-estandares` si aparecen bugs en QA.

#### Gate de aprobación

Gate cliente = Joaquín (owner). A diferencia del sprint 08/27, esta feature no vino con autorización explícita de ejecución en el pedido original: **no habilitar Implementación hasta que Joaquín apruebe la estimación** y elija si arranca por la Etapa 1 sola o por Etapa 1 + 2 (con o sin E6). **Resuelto 2026-09-14: aprobado con alcance completo E1-E7** (una sola migración con las columnas de E3, E5 y E6).

## Historial de ajustes
- 2026-08-27: Primera ficha de presupuesto real de este proyecto (plantilla nunca se había completado — todo el trabajo previo fue ad-hoc en sesión de chat). Sprint "corrección de bugs/gaps + 3 mejoras": 17 items, 22.0 h M base, 10.56 h facturables, ≈USD 370 de costo interno equivalente (sin cobro a cliente, proyecto propio del estudio). Gate aprobado por el pedido explícito del cliente/owner.
- 2026-08-27: Cierre de calibración. Real ≈2.5-3 h (1.18 h de ejecución de subagentes + orquestación), contra 22.0 h M base estimadas — ratio ≈7.5x-9x, nuevo techo del dataset del estudio. Sprint deployado a producción el mismo día, QA final GO. Causa del único desvío real (retrabajo post-QA): vocabulario de `Contacto.Rubro` no declarado explícitamente en Arquitectura — regla derivada para la próxima vez.
- 2026-09-14: Estimación de "4 frentes — combo con gancho" (pendiente de aprobación). 7 etapas, 21.0 h M base / 22.0 h PERT / 25.62 h con contingencia variable / 10.08 h facturables / ≈USD 353 equivalente + ≈USD 46 de IA sombra. Anclada en el cierre propio del 08/27 (ratio total 0.95) con pisos de "modificación sobre módulo existente" por ronda repetida. Real esperado 3-3.5 h (techo 4.5-5 h). Detalle del sprint 08/27 condensado en "Calibración propia del proyecto" (sin perder los números del cierre).
