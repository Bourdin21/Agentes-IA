# Memoria - Analista funcional

## Proyecto: agentes-ia-sistema (sistema de agentes LLM del estudio)
## Ultima actualizacion: 2026-09-17

---

# ETAPA 0 — DISCOVERY (2026-09-17)

## 1. Contexto y objetivo

Pedido textual de Joaquin: *"la idea es que el sistema utilice los agentes LLM con el siguiente
criterio de programacion claude"*, seguido de 6 criterios:

| # | Criterio |
|---|---|
| C1 | Proyectos LLM individuales para clientes particulares (con sus reglas y su contexto) |
| C2 | Skills para cosas que se hacen de la misma manera y se reutilizan |
| C3 | Tareas programadas con resultados listos para ver |
| C4 | Activar busqueda web en paralelo para research de info que no se tenga |
| C5 | Dashboard de control de gastos del estudio por cliente: llamadas a la API, tokens, USD |
| C6 | Mantenimiento mensual: anotar que tareas repetitivas se pueden automatizar con codigo para consumir menos tokens |

**Objetivo declarado:** que el trabajo del estudio asistido por LLM deje de depender de la memoria
de cada sesion y pase a tener estructura explicita: contexto por cliente, piezas reutilizables,
ejecucion desatendida, investigacion propia, y visibilidad economica.

## 2. BLOQUEANTE PRINCIPAL — sobre que sistema se aplica esto

El pedido dice "el sistema" sin nombrarlo, y los 6 criterios encajan en **tres sistemas distintos
que ya existen**, con consecuencias muy diferentes de alcance, esfuerzo y precio:

| Interpretacion | Que seria | Evidencia a favor |
|---|---|---|
| **(A) El propio setup de Claude Code del estudio** — este repo `Agentes-IA` | Configurar skills, subagents, tareas programadas, web search y un tablero de costos **para como trabaja Joaquin**, no para vender | "criterios de programacion **claude**"; "dashboard de gastos **del estudio**"; "mantenimiento mensual **del sistema**"; C2 ya existe como `.claude/skills/` |
| **(B) El producto `olvidata-agentes-multirubro`** | Features del SaaS .NET multi-tenant que se vende a terceros | C1/C3/C5 son literalmente M5/M12/M6, ya implementados ahi |
| **(C) Un sistema nuevo** | Plataforma propia distinta de las dos anteriores | Nada en el pedido lo sugiere; se registra para descartarlo explicitamente |

**Lectura preliminar del analista: (A)**, por "programacion claude", "del estudio" y porque C2 ya
existe en este repo. Pero **no se avanza a Analisis sin que Joaquin lo confirme**, porque bajo (B)
cinco de los seis criterios ya estan construidos y el trabajo seria casi nulo.

## 3. Estado real hoy, criterio por criterio (relevado, no supuesto)

| # | Que existe hoy | Donde | Gap real |
|---|---|---|---|
| C1 | Contexto por proyecto en `docs/<proyecto>/definiciones/` (7 archivos por agente), memoria por repo en `.claude/memorias/<repo>/`, memoria por subagente en `.claude/agent-memory/`. **37 carpetas de proyecto activas.** | este repo | No hay "proyecto LLM" como unidad con reglas propias: hay convencion documental + memoria, no aislamiento ni carga automatica de contexto por cliente |
| C2 | **5 skills ya operativas**: `estandares-qa`, `presupuesto-parametros`, `design-system`, `checklists-modulo`, `memoria-documental` | `.claude/skills/` | Cubierto en su forma basica. Gap: no hay criterio de cuando nace una skill nueva ni revision de las existentes |
| C3 | **No existe.** Hay 3 hooks (`PostToolUse`, `SessionStart`, `Stop`) que disparan `doctor.py`, pero son reactivos a eventos de sesion, no programados | `.claude/settings.json` + `.claude/hooks/hook_doctor.py` | Gap completo: nada corre sin que Joaquin abra una sesion |
| C4 | Disponible como herramienta del harness (WebSearch / WebFetch). Ya se uso de hecho (research de Fixed API en `libreria-horizonte`) | harness | Gap: es ad-hoc, no hay criterio de cuando se dispara ni se guarda el resultado del research como activo reutilizable |
| C5 | **No existe como tablero.** Existe el metodo de *costo sombra* proyectado por modulo, a precio de lista de la API | `27-presupuesto-parametros.instructions.md`, seccion "Costo interno de IA" | Ver seccion 4 — hay un impedimento duro de datos |
| C6 | **No existe.** Lo mas cercano es `scripts/doctor.py`, que chequea consistencia documental, no consumo | `scripts/doctor.py` | Gap completo |

## 4. HALLAZGO DURO — C5 no se puede construir como esta pedido

`27-presupuesto-parametros.instructions.md` lo dice explicito y esta confirmado en la cuenta:

> el estudio paga Claude Code via **suscripcion Stripe** (`billingType: stripe_subscription`), **no
> por token via API**.

Consecuencia directa: **no existe una facturacion por token ni por llamada que se pueda desglosar
por cliente.** Un dashboard con "cantidad de llamadas a la API, cantidad de tokens, cantidad de USD"
del trabajo del estudio en Claude Code **no tiene fuente de datos real de facturacion**. Lo que si
se puede hacer, en orden de fidelidad decreciente:

1. **Medicion real, solo donde se usa API propia.** `olvidata-agentes-multirubro` ya registra
   `PasoTarea.CostoUsd` por paso, `EventoUso` por tarea y tiene pantalla "Uso y consumo" por
   organizacion y rango de fechas (M6). Ahi el numero es real porque el consumo pasa por API key.
   El CRM tambien mide: `contactomensajesia` guarda `InputTokens`, `OutputTokens`,
   `CacheLecturaTokens`, `CacheEscrituraTokens`, `CostoUsd`, `Modelo` por mensaje.
2. **Costo sombra a precio de lista** para el trabajo del estudio en Claude Code, que es el metodo
   que ya se usa en presupuestos. Es una *proyeccion*, no un gasto.
3. **Consumo de la suscripcion** (ventanas de uso), si el harness lo expone — **a verificar**, no
   se asume que exista.

Esto **no invalida C5**, pero cambia su naturaleza: pasa de "tablero de facturacion" a "tablero de
consumo estimado + consumo real donde hay API". Hay que decidir cual de las tres se quiere.

## 5. REUTILIZACION CROSS-PROYECTO (regla obligatoria) — solapamiento fuerte con `olvidata-agentes-multirubro`

Escaneado `docs/*/definiciones/` de todo el historial. Hallazgo central:

**`olvidata-agentes-multirubro` (repo `C:\Sistemas\Olvidata Agentes Multi-rubro`) ya implemento
5 de los 6 criterios**, roadmap M1-M12 completo, 478/478 tests, 2 rondas de QA integral cerradas
el 2026-09-16, entregado a Joaquin para prueba propia:

| Criterio del pedido | Modulo ya construido ahi |
|---|---|
| C1 proyectos por cliente | **M5 — Workspace por cliente de cartera** |
| C2 skills reutilizables | **M10 — Base de conocimiento por rubro** (parcial: es contenido por rubro, no "skill" ejecutable) |
| C3 tareas programadas | **M12 — Tareas programadas y autonomia gradual por rol** |
| C4 busqueda web | **M11 — Conectores** deja el *mecanismo* + un conector HTTP generico. **No hay conector de busqueda web.** Parcial |
| C5 dashboard de gastos | **M6 — Aprobaciones y limites de gasto**: `PasoTarea.CostoUsd`, `EventoUso`, `LimiteGastoMiembro`, pantalla "Uso y consumo" |
| C6 mantenimiento mensual | **Nada.** Es el unico criterio sin precedente en ningun proyecto del historial |

**Implicancia de alcance:** si la respuesta al bloqueante de la seccion 2 es **(B)**, el trabajo se
reduce a C4 (conector de busqueda) + C6 y un repaso de C2 — el resto ya esta hecho. Si es **(A)**,
el producto multirubro **no se reutiliza como codigo** (es .NET SaaS, otro plano) pero **si como
diseño**: su modelo de costo por paso, su esquema de limites por miembro y su diseño de tareas
programadas son el precedente a copiar conceptualmente en vez de inventar.

Patrones aplicables del catalogo: revisar `docs/patrones/catalogo.yml` en Diseño — no se hizo en
Discovery por no corresponder a esta etapa.

## 6. Alcance inicial

**Incluido (sujeto a la respuesta de la seccion 2):**
- Definicion del criterio de "proyecto LLM por cliente": que es, que lo compone, como se carga (C1).
- Criterio de nacimiento y revision de skills (C2).
- Mecanismo de tareas programadas con resultado persistido y revisable (C3).
- Criterio y destino del research web: cuando se dispara y donde queda guardado (C4).
- Tablero de consumo, con la fuente de datos que se decida en la seccion 4 (C5).
- Rutina mensual que detecte tareas repetitivas candidatas a automatizarse con codigo (C6).

**No incluido (inicial):**
- Migrar los 37 proyectos existentes de `docs/` a una estructura nueva (si la hubiera).
- Cambiar el modelo de facturacion del estudio (pasar de suscripcion a API).
- Cualquier feature del producto multirubro que se venda a terceros, salvo que la seccion 2
  resuelva (B).
- Automatizar efectivamente las tareas que C6 detecte: C6 **detecta y anota**, no implementa.

## 7. Supuestos y dependencias

| # | Supuesto | Riesgo si falla |
|---|---|---|
| S1 | El sistema objetivo es (A), el setup propio del estudio | Alcance completo mal dimensionado |
| S2 | "Tareas programadas" corre en la maquina de Joaquin, no en un servidor | Si tiene que ser server-side, cambia de plano (infra, costo, disponibilidad) |
| S3 | El consumo real por cliente se puede imputar a un cliente | **Debil**: hoy una sesion toca varios proyectos; no hay atribucion natural |
| S4 | C6 es una rutina asistida, no un analizador automatico de transcripts | Si se espera automatico, hace falta acceso programatico al historial de sesiones — **no verificado que exista** |

## 8. Riesgos tempranos

| # | Riesgo | Sev | Nota |
|---|---|---|---|
| R1 | **C5 sin fuente de datos real** (seccion 4) | **Alta** | Es el criterio con mayor distancia entre lo pedido y lo posible |
| R2 | **Duplicar lo que multirubro ya hace** (seccion 5) | **Alta** | Regla de reutilizacion obligatoria del estudio |
| R3 | Atribucion de consumo por cliente (S3) | Media | Sin una unidad de trabajo por cliente, el tablero muestra un total sin desglose util |
| R4 | C3 depende de que la maquina este prendida | Media | "resultados listos para ver" implica que corrio sin nadie mirando |
| R5 | Sobre-ingenieria de C2 | Baja | Ya hay 5 skills funcionando; el riesgo es formalizar de mas algo que ya anda |

## 9. Preguntas abiertas

**Bloqueantes (sin esto no se abre Analisis):**
- **P1.** Sobre que sistema aplica: (A) el setup Claude Code del estudio, (B) el producto
  multirubro, o (C) uno nuevo. Ver seccion 2.
- **P2.** Dado la seccion 4, que version de C5 se quiere: (a) costo sombra estimado del trabajo del
  estudio, (b) consumo real solo donde hay API propia (multirubro + CRM), o (c) las dos en un solo
  tablero.
- **P3.** "Por cliente" significa por proyecto de `docs/` (37 carpetas), por cliente comercial
  (varios proyectos pueden ser del mismo), o por repo.

**No bloqueantes (se pueden asumir y confirmar en Diseño):**
- **P4.** C3: que tareas concretas querrias programadas hoy (candidatas observadas: `doctor.py`
  diario, chequeo de vencimientos de SSL/dominios, resumen de pipeline comercial, control de gasto
  del CRM).
- **P5.** C3: donde se ven los resultados (archivo en `docs/`, notificacion, tablero).
- **P6.** C4: el research queda como archivo de proyecto, como entrada del catalogo de patrones, o
  solo en la conversacion.
- **P7.** C6: frecuencia real mensual, y quien la dispara.

## 10. Condicion de paso a Analisis

Se abre Analisis cuando:
1. P1 respondida (sistema objetivo definido) — **bloqueante duro**.
2. P2 respondida (naturaleza del tablero de C5) — **bloqueante duro**.
3. P3 respondida (unidad de "cliente") — **bloqueante duro**.
4. Confirmado por Joaquin que el solapamiento de la seccion 5 se resuelve por reutilizacion y no por
   construccion paralela.

---

## Definiciones vigentes
Pendiente: no hay definiciones cerradas todavia. Discovery abierto, 3 preguntas bloqueantes.

## Historial de ajustes
- 2026-09-17: Discovery inicial. 6 criterios relevados contra el estado real del repo. Dos hallazgos
  que condicionan todo: (1) el estudio paga Claude Code por suscripcion, no por token, asi que C5 no
  tiene fuente de facturacion real; (2) `olvidata-agentes-multirubro` ya implemento 5 de los 6
  criterios como producto .NET. 3 preguntas bloqueantes abiertas.
