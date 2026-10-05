# Memoria - Presupuestador

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-09-14

## Definiciones vigentes

### Estado de la etapa
**Presupuesto OMITIDO por decisión de Joaquín (2026-09-14): "Saltear el presupuesto porque es un proyecto personal".** Producto propio de Olvidata Soft sin cliente externo: no hay precio, tasa, contingencia ni Tokens IA a cotizar. El gate "Implementación requiere presupuesto aprobado por el cliente" queda cumplido por la dispensa explícita del cliente (Joaquín).

### WBS funcional vigente
Sin WBS valorizada. Referencia de alcance: plan funcional por etapas de `3-arquitecto-mvc.md` (Base de organización → Áreas → Miembros + backoffice → Cartera → Tareas por rol).

### Estimaciones PERT por item
No aplica (omitido).

### Tasa vigente y contingencia aplicada
No aplica.

### Resumen economico (con Tokens IA como item individual)
No aplica: proyecto personal sin cotización.

### Calibraciones historicas usadas
Ninguna.

### Cierre estimado vs real (si disponible)
**Cierre M4b Configurador de reglas (2026-09-14)** — sin estimación (presupuesto omitido); desvío no calculable.

| Item | Estimado (h) | Real | Desvío | Causa principal |
|---|---:|---:|---:|---|
| Etapas 0–3 | — | no registrado en horas humanas | n/a | sin estimado |
| Implementación (subagent, incluye borrador del prompt del configurador) | — | ~72 min de agente, 257 acciones | n/a | sin estimado |
| QA en navegador con modelo simulado (sin auto-fix) | — | ~29 min de agente, 104 acciones | n/a | sin estimado |

Sin cambios de alcance. **Lecciones M4b:** (1) el simulador con guion por palabras clave permitió probar los 4 tipos de propuesta sin cargar datos: incluir guiones de herramientas desde el diseño en toda feature con tool use; (2) la verificación de contraste en el implementador funcionó (0 defectos en lo nuevo) pero destapó deuda global del theme (OLV-004): conviene un ítem de mantenimiento propio; (3) la implementación de features con herramientas del modelo tiene costo similar a M4 (~70 min): estimar tool use + permisos en segundo plano como complejidad alta.

**Cierre M4 Agentes de la organización (2026-09-14)** — sin estimación (presupuesto omitido); desvío no calculable.

| Item | Estimado (h) | Real | Desvío | Causa principal |
|---|---:|---:|---:|---|
| Etapas 0–3 (incluye cambio de alcance en el gate de Diseño: sin revisión del Director) | — | no registrado en horas humanas | n/a | sin estimado |
| Implementación (subagent) | — | ~70 min de agente, 300 acciones | n/a | sin estimado |
| QA en navegador con modelo simulado (subagent, 1 auto-fix CSS) | — | ~39 min de agente, 85 acciones | n/a | sin estimado |

Cambio de alcance: se sacó la revisión del Director (reduce alcance). **Lecciones M4:** (1) M4 fue la feature más grande hasta ahora (implementación ~2x M3b): features con entidad nueva + versiones + integración con constructor/tareas/reglas/núcleo/licencias deben estimarse como varias features; (2) el test golden de hash calculado con el código previo evitó romper tareas existentes: hacerlo obligatorio en todo cambio del constructor de contexto; (3) tercera vez que QA encuentra contraste en tema oscuro (OLV-001/002/003): mover la verificación de contraste al checklist del implementador como paso obligatorio.

**Cierre M3b Seguir conversando (2026-09-14)** — sin estimación (presupuesto omitido); desvío no calculable.

| Item | Estimado (h) | Real | Desvío | Causa principal |
|---|---:|---:|---:|---|
| Etapas 0–3 (conversación con Joaquín, incl. definición de tareas programadas → M12) | — | no registrado en horas humanas | n/a | sin estimado |
| Implementación (subagent) | — | ~37 min de agente, 130 acciones | n/a | sin estimado |
| QA en navegador con modelo simulado (subagent, 1 auto-fix CSS) | — | ~32 min de agente, 98 acciones | n/a | sin estimado |

Sin cambios de alcance. **Lecciones M3b:** (1) el proveedor de modelo simulado solo en Development permitió QA de punta a punta sin costo: incluirlo desde el inicio en toda feature del motor; (2) la normalización de la conversación para la API fue la parte crítica y se resolvió con tests de casos borde antes de UI: mantener ese orden; (3) componentes visuales nuevos siguen fallando primero en tema oscuro (OLV-001 en M2, OLV-002 en M3b): sumar verificación de contraste en tema oscuro al checklist del implementador; (4) EF InMemory no es transaccional: la atomicidad se prueba contra MySQL real.

**Cierre M3 Reglas (2026-09-14)** — sin estimación (presupuesto omitido); desvío no calculable. Esfuerzo real registrado:

| Item | Estimado (h) | Real | Desvío | Causa principal |
|---|---:|---:|---:|---|
| Etapas 0–3 (conversación con Joaquín, incl. pedidos nuevos N-01/N-02 y ajustes de simplificación) | — | no registrado en horas humanas | n/a | sin estimado |
| Implementación (subagent) | — | ~52 min de agente, 160 acciones | n/a | sin estimado |
| QA en navegador (subagent, sin auto-fix) | — | ~28 min de agente, 89 acciones | n/a | sin estimado |

Cambios de alcance durante la ejecución: ninguno en M3 (N-01, N-02, M3b y reglas sugeridas se enviaron al roadmap). Comparado con M2: implementación ~20% más larga (constructor de contexto + cambio de firma del motor) y QA más corta sin defectos, confirmando que reutilizar helpers/vistas de M2 bajó el costo de UI.

**Lecciones M3:** (1) cambiar contratos del motor (`SolicitudModelo`) arrastra tests de M1: estimarlo como ítem propio; (2) el proveedor MySQL generó bien el check constraint esta vez: la lección de M2 se mantiene como verificación, no como trabajo manual fijo; (3) funcionalidades con prompts dejan una validación que solo se cierra con corrida paga: presupuestarla explícitamente como ítem "validación con modelo real".

**Cierre M2 Organización (2026-09-14)** — sin estimación previa (presupuesto omitido), por lo que no hay desvío calculable. Se registra el esfuerzo real para calibrar futuras features de este producto.

| Item | Estimado (h) | Real | Desvío | Causa principal |
|---|---:|---:|---:|---|
| Etapas 0–3 (análisis, diseño, arquitectura; conversación con Joaquín) | — | no registrado en horas humanas | n/a | sin estimado |
| Implementación (subagent implementador) | — | ~43 min de agente, 148 acciones | n/a | sin estimado |
| QA en navegador + 2 auto-fix (subagent QA) | — | ~32 min de agente, 125 acciones | n/a | sin estimado |
| Revisión humana | — | no registrada | n/a | — |

Desvío total: no calculable. Cambios de alcance durante la ejecución: ninguno (solo decisiones menores del implementador ante ambigüedades, documentadas en `5-implementador.md`).

**Lecciones aprendidas (para estimar las próximas features M3–M12):**
- `MySql.EntityFrameworkCore 10.0.9` ignora `stored: true` en columnas computadas y exige orden manual de índices con FK: sumar margen fijo en toda migración con columnas generadas, check constraints o reemplazo de índices sobre FKs.
- Cambios transversales de sesión/autorización (middleware, resolvedor, policies) arrastran ajustes en tests existentes y en el hub de SignalR: tratarlos como ítem propio, no como parte de una pantalla.
- Reutilizar literal (formularios, Select2, bajas AJAX de la-platense) redujo trabajo de UI pero QA encontró huecos de tema oscuro en componentes portados: incluir verificación de tema oscuro de cada componente portado.
- Features con reglas de aislamiento/invariantes (último Director, IDOR) justifican el tiempo de QA con ids manipulados y concurrencia real: mantenerlo en el alcance de QA.

**Ajustes recomendados:** registrar horas humanas de revisión por feature desde M3 para tener base real; si en el futuro se presupuesta este producto, usar M2 como referencia de complejidad "ABM x3 + cambio transversal de sesión + migración con SQL manual".

**Acción obligatoria para el próximo presupuesto (si se hace):** anotar al cierre de cada etapa la duración real (agentes + revisión humana).


## Cierre de calibracion — M29, buscar en internet y el archivo que se guarda o se descarta (2026-10-02/03)

**Presupuesto: OMITIDO** (producto propio, proyecto personal). Igual que en M28, este cierre no calibra un precio:
registra el esfuerzo real y, sobre todo, **donde se fue**.

### Esfuerzo real

| Etapa | Corridas | Tokens de subagente | Reloj |
|---|---|---|---|
| Discovery + Analisis + Diseno + Arquitectura | en el hilo del orquestador + 1 relevamiento de codigo | — | — |
| Implementacion | **8 corridas** (3 de alcance + 3 de arreglos + **2 de prompt**) | ~1.790.000 | ~2 h 50 |
| QA | **3 corridas** (2 lotes + 1 re-verificacion) | ~954.000 | ~1 h 45 |
| **Total** | **11 corridas de subagente** | **~2.744.000** | **~4 h 35** |

**Costo en dinero real: USD 3,84** de la bolsa mensual de pruebas de prompts (tope interno de USD 30), en tres corridas
de evaluacion contra produccion. Es el primer modulo de la familia que gasta plata ademas de tokens de desarrollo.

### El dato de calibracion que M29 agrega, y no lo tenia ninguno de los anteriores

**Hay una etapa que no estaba en la cuenta: afinar el prompt.** De las 8 corridas de implementacion, **2 fueron solo
prompt** —ni una linea de `src/`— y son las que destrabaron la mitad del valor del modulo. Y encima quedo sin terminar
por una causa externa.

El patron a incorporar al dataset: **en un modulo que agrega un agente, el codigo verde no significa que el modulo
funcione.** M29 y M28 llegaron a 1223 tests verdes, QA apto y despliegue hecho, y la primera corrida real del prompt
mostro que el agente **no usaba dos de las cuatro herramientas de propuesta** — es decir, *crear automatizaciones
mencionando*, que era la mitad de lo que Joaquin pidio. Ningun test unitario ni ninguna prueba de QA podia encontrarlo,
porque los dos corren con el **modelo simulado**, que no lee el prompt.

**Consecuencia para estimar:** un modulo que agrega o cambia un agente del nucleo lleva **una etapa propia de afinado de
prompt con corridas reales**, del orden de **2 a 3 corridas de evaluacion** (~USD 1,7 cada una) mas 1 o 2 rondas de
edicion del prompt. En M28 esa etapa no se estimo y en M29 tampoco: aparecio al final las dos veces.

### Los dos hallazgos que cambian como se escriben las pruebas de prompt

Los dos salieron de leer la corrida real en la base, no de inspeccionar:

1. **El revisor automatico solo ve el texto final de la respuesta, nunca la entrada de una herramienta.** Un criterio
   sobre el contenido de una tarjeta es **incalificable por construccion**. Esto invalido tres casos de la suite del
   chat libre de un saque, y la suite del analista ya respetaba la convencion sin que estuviera escrita en ningun lado.
   **Ahora esta escrita.**
2. **Alucinacion de accion.** El modelo escribio *«no es un dato para anotar en memoria, es una regla… asi que la deje
   como tarjeta»*, describio la tarjeta completa, cerro con *«se termina con el boton Aplicar»* y **nunca llamo a la
   herramienta**. Los dos criterios de texto en verde y la accion inexistente. Es la contracara exacta del hallazgo 1, y
   la leccion para todo prompt que proponga algo: **hay que decirle que dejar una tarjeta ES llamar a la herramienta**,
   porque la prosa puede sustituir la llamada.

### Dos casos de prueba estaban mal, y se arreglaron mas duros

Vale registrarlo porque el incentivo natural es el contrario: uno **se contradecia solo** (el criterio premiaba
preguntar primero y la verificacion exigia la herramienta en el mismo turno: premiaba y castigaba la misma conducta) y
otro medía lo incalificable. Los dos se corrigieron **endureciendo** el caso, con el motivo escrito adentro. Ninguno se
afloho y ninguno se elimino: *un «paso» falso es peor que no tener pruebas*.

### Lo que la arquitectura hizo mal y se detecto a tiempo (dos veces, en el mismo modulo)

1. **B-03 era factualmente falso.** Dije «guardar en un cliente no mueve el archivo porque la ruta se resuelve por
   `ArchivoId`», y la ruta es `{raiz}/{tenant}/{cliente}/{archivoId}`. Seguirlo al pie dejaba **todo documento guardado
   apuntando a bytes que nadie busca, sin fallar en el momento**. El relevamiento decia lo contrario dos parrafos antes:
   **una afirmacion de arquitectura sobre codigo existente es una cosa a verificar, no un supuesto.**
2. **A-07 declaro un alcance sin chequear un gate anterior**, y la propuesta resultante se podia proponer y no se podia
   aplicar: se quemaba sola (OLV-033).

**Ajuste para la proxima:** las dos las refuto el implementador contra el codigo. Eso funciono porque el brief le pedia
explicitamente discutir mis lecturas, no obedecerlas. **Conviene que eso sea parte del formato del hand-off**, no una
cortesia: pedirle al subagente que marque lo que no cierra es mas barato que el defecto que evita.

### Resultado tecnico

- **1223 tests verdes** (de 1164 al abrir M29: **+59**), build limpio, **dos migraciones**
  (`DocumentoSinClienteM29`, `DuenoDelTransitorioM29`), **11 commits locales sin push**.
- **4 defectos de QA, los 4 cerrados y re-verificados** (OLV-038 major, OLV-039, OLV-040, OLV-041). **Tres eran la misma
  clase, por tercera y cuarta vez**: la superficie que **relee** el hilo se queda sin un dato que la que lo **escribe**
  si tiene. Al cerrar el ultimo se compararon los dos renderizadores campo por campo y aparecio que **el arreglo obvio
  abria el mismo defecto invertido**.
- **Desplegado a produccion** (migraciones aplicadas, sitio sincronizado, `/health/vivo` 200, assets nuevos verificados
  desde afuera). **El agente del chat libre NO se publico**, por decision de Joaquin del 2026-10-03: sin saldo en la
  cuenta de Anthropic, publicarlo lo pondria en el menu y fallaria en el primer mensaje. El estado actual es el seguro.

## Cierre de calibracion — M28, el chat libre (2026-10-02)

**Presupuesto: OMITIDO** (producto propio de Olvidata Soft, proyecto personal). No hay numero estimado contra el que
medir desvio, asi que este cierre no calibra un precio: **registra el esfuerzo real para que la familia agentica tenga
un dato mas**, y sobre todo registra **donde se fue el esfuerzo**, que es lo unico accionable.

### Esfuerzo real por etapa

| Etapa | Corridas | Tokens de subagente | Reloj |
|---|---|---|---|
| Discovery + Analisis + Diseno + Arquitectura | en el hilo del orquestador + 2 relevamientos de codigo | — | — |
| Implementacion | **6 corridas** (3 de alcance + 3 de arreglos) | ~1.680.000 | ~3 h 10 |
| QA | **4 corridas** (3 lotes + 1 re-verificacion) | ~1.073.000 | ~2 h 10 (lotes 2 y 3 en paralelo) |
| **Total** | **10 corridas de subagente** | **~2.753.000** | **~5 h 20 de reloj de agente** |

### El dato de calibracion que vale: el reparto entre alcance y correccion

De las 6 corridas de implementacion, **3 fueron de alcance y 3 de arreglos** — la mitad. Y de las 4 de QA, **1 fue
re-verificacion**. Dicho de otra forma: **el 40 % del esfuerzo de implementacion y QA se fue en encontrar y cerrar
defectos, no en construir.**

Eso **no** es un sintoma de haber trabajado mal: es el precio de haber puesto a QA a probar de verdad, y lo que compro
fue concreto. Para la proxima estimacion de un modulo de esta familia, **la linea de QA + arreglos no es un 15 % de
contingencia: es del orden del 40 % del trabajo de implementacion**, y conviene presupuestarla como etapa propia en vez
de esconderla en un porcentaje.

### Lo que el modulo costo de mas por una causa identificable

**Dos corridas de implementacion (1b y la ronda de los cinco defectos) existieron por huecos del brief de arquitectura,
no por errores del implementador:**

- La tanda 1b existio porque **A-02 no listaba el camino de las propuestas**: CU-03 —la mitad del pedido— quedo sin
  implementar, y el implementador lo marco en vez de inventar el alcance. El brief se corrigio (A-07) y se volvio a
  delegar, que es exactamente lo que manda la instruccion `39` §4: *si el brief no alcanza, el problema es el brief*.
- OLV-033 existio porque **A-07 declaro «alcance personal» sin chequear un gate de diseño anterior** (una preferencia
  personal solo podia nacer de una tarea de trabajo). Se cerro en A-10.

**Ajuste para la proxima:** al agregar un valor a un enum de dominio, el relevamiento de arquitectura tiene que buscar
**las dos formas**, y hasta M28 solo buscaba una. Los numeros medidos: **7 sitios de clase A** (`default` / `_ =>` que
**aceptan** el valor nuevo en silencio y lo mapean mal) y **84 comparaciones de clase B** (`== UnValor` o lista blanca de
un solo valor que lo **rechazan** en silencio), de las cuales **5 eran del molde del defecto**. Buscamos los 7 y no los
84. **Esa sola linea en el checklist de arquitectura habria evitado dos de las seis corridas de implementacion.**

### Resultado tecnico

- **1164 tests verdes** (de 1120 al abrir M28: **+44**), build limpio, **sin migracion EF**, 6 commits locales sin push.
- **10 defectos reportados por QA** (OLV-028 a OLV-037): **9 cerrados y re-verificados**, **1 abierto** (OLV-036) que
  **no es de M28** y necesita decision de producto.
- **7 defectos preexistentes** encontrados y arreglados de paso, **4 de ellos silenciosos** — ninguno lo habria
  encontrado un test de los que ya existian.

### Nota para la calibracion de la familia agentica

M28 es la **cuarta** fila de la familia (tras M19/M20/M21, M27). El rasgo que se repite y que conviene incorporar al
dataset: **en los modulos que extienden el motor de agentes, el costo no esta en la capacidad nueva sino en los lugares
viejos que no sabian del caso nuevo.** En M28 la capacidad nueva fue chica (una puerta a un motor ya entero, PAT-029) y
el trabajo real fueron ~10 switches, 84 comparaciones revisadas una por una, y 7 defectos ajenos. Estimar estos modulos
por la capacidad que agregan los subestima sistematicamente.

## Historial de ajustes
- 2026-09-14: Etapa omitida por decisión de Joaquín (proyecto personal). Arquitectura M2 aprobada implícitamente al pedir saltear el presupuesto.
- 2026-09-14: M3 Reglas — presupuesto omitido (proyecto personal, criterio vigente). Implementación habilitada tras aprobar Arquitectura M3.
- 2026-09-14: Cierre de calibración M2 (etapa 8): esfuerzo real registrado sin estimado; lecciones sobre migraciones con MySql.EntityFrameworkCore, cambios transversales de sesión y tema oscuro de componentes portados.
