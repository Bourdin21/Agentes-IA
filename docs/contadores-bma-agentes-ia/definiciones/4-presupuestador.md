# Presupuestador — contadores-bma-agentes-ia

Estado: **FIJADO 2026-09-23 — NO SE ENTREGA AL CLIENTE TODAVÍA** (decisión de Joaquín). Los números quedan congelados
acá; la propuesta se arma cuando él lo indique.

Se apoya en el [Análisis cerrado](1-analista-funcional.md), el [Diseño](2-disenador-funcional.md), la
[Arquitectura](3-arquitecto-mvc.md) y el [research de servicios externos](../research-arca-arba-sos-2026-09.md).

---

## 1. Qué se cotiza y qué no

**No es un desarrollo a medida.** BMA es una **organización del producto `olvidata-agentes-multirubro`**, que ya está
construido. Lo que se cotiza es:

1. Lo que **falta en el núcleo** del rubro contable (3 agentes, 2 documentos de conocimiento, 1 conector).
2. La **configuración** de la organización.
3. El **acompañamiento** del piloto.

**Lo que NO se cotiza como desarrollo:** los 10 agentes del rubro que ya existen, ni el producto (M1–M15), ni el
relevamiento tarea por tarea — eso lo hace cada usuario con el analista de automatizaciones.

> ⚠️ **La pregunta comercial que define el precio, y que no resuelve el WBS:** todo lo del bloque A **queda en el
> producto y se revende a cualquier otro estudio contable**. Cuánto de eso se le carga a BMA es decisión de
> `olvidata-ceo`, no del presupuestador. Consultada el 2026-09-23.

## 2. Anclaje histórico

| Referencia | Por qué sirve |
|---|---|
| **`contadores-bma-conversor`** — 8 h reales, **USD 199** final (cierre 2026-06-29) | **Mismo cliente.** Es el único precio que BMA ya aceptó. Sirve de referencia de expectativa, no de alcance: aquel era un conversor puntual |
| **"Integración REST documentada (token que vence, 1-2 endpoints)"** — M 3-5 h, USD 32-53 | Ancla directa del **conector de SOS**. Nota del dataset: *el riesgo dominante es la habilitación de acceso, no el mapeo de endpoints* |
| **"Módulo con lógica compleja"** — M 5-8 h | Ancla del agente de control ARCA↔SOS |
| **M15 (analista de automatizaciones), 2026-09-23** | **Único dato real de cuánto cuesta un agente del núcleo de punta a punta**: prompt + ficha + 6 casos de evaluación + **4 versiones hasta aprobar** + 5 corridas reales (USD 4,1 de tokens). Se usa como ancla de la categoría nueva del bloque A |

### Categoría nueva: "Agente del núcleo"

No existe en el dataset. Se abre con el ancla de M15 y **se cierra con el real de este proyecto**. Incluye: prompt con
su ficha, casos de evaluación, corridas reales **hasta que apruebe** (la primera versión casi nunca pasa) y publicación.

| Sub-tipo | M (h) | Nota |
|---|---|---|
| Agente que **compara y detecta diferencias** (lógica de negocio fina) | 6 | El de M15 llevó 4 versiones |
| Agente de **constatación** contra un organismo | 4 | Menos casos borde |
| Agente de **consulta sobre conocimiento ya cargado** | 3 | El conocimiento es el trabajo, no el prompt |

## 3. WBS

### Bloque A — Núcleo del rubro contable *(queda en el producto, revendible)*

| # | Módulo | Tipo | M (h) |
|---|---|---|---|
| A1 | **Agente `cont-control-arca`** — cruza el export de Mis Comprobantes contra los recibidos de SOS; detecta duplicados, faltantes y diferencias de monto | Agente del núcleo (comparación) | **6** |
| A2 | **Agente `cont-arba`** — constata padrones y alícuotas en ARBA | Agente del núcleo (constatación) | **4** |
| A3 | **Agente `cont-soporte-sistemas`** — dudas de uso de SOS, Onvio, ARCA y ARBA | Agente del núcleo (consulta) | **3** |
| A4 | **Conocimiento `60-arca.md` + `61-arba.md`** — qué se puede consultar, con qué habilitación, qué significa cada dato, y el límite de 12-15 días de Autoimpo | Conocimiento del rubro | **4** |
| A5 | **Conector SOS Contador** — `IConectorTipo` + `HerramientaConector`: login de dos pasos, token por CUIT, `/compra/listado` y `/compra/consulta`, bajo el guardia de destinos | Integración REST documentada **+ tipo nuevo en el producto** | **5** |
| | | **Subtotal A** | **22** |

> **A4 sale más barato de lo que parece** porque el research de ARCA, ARBA y SOS **ya está hecho y verificado**
> (2026-09-23) y quedó como memoria del estudio. Se escribe el documento, no se investiga de cero.

### Bloque B — Configuración de la organización *(servicio, no queda en el producto)*

| # | Módulo | M (h) |
|---|---|---|
| B1 | Alta del tenant, licencia del rubro, 3 áreas, 6 miembros con sus roles, etapa de entrega | **2** |
| B2 | Reglas de la empresa (las dos no negociables) + conexión a SOS cargada y **probada contra una CUIT real** | **2** |
| B3 | Carga de la cartera: **~100 empresas** (por importación, no a mano) | **3** |
| | | **Subtotal B** | **7** |

### Bloque C — Puesta en marcha

| # | Módulo | M (h) |
|---|---|---|
| C1 | Sesión de arranque con las 6 personas: **cómo relevar lo propio con el analista**. Es lo que hace que el modelo funcione | **2** |
| C2 | **Piloto de conciliación bancaria** con Marcial y Gastón, sobre los archivos reales ya cargados, con ajuste de instructivos | **4** |
| | | **Subtotal C** | **6** |

### Total

| Bloque | M (h) | Queda en el producto |
|---|---|---|
| A — Núcleo del rubro | 22 | **Sí** (revendible a otros estudios) |
| B — Configuración | 7 | No |
| C — Puesta en marcha | 6 | No |
| **Total** | **35** | |

## 4. Costos variables que NO son horas

| Concepto | Estimado | Quién lo paga |
|---|---|---|
| **Tokens de las corridas de evaluación** de los 3 agentes nuevos | ~USD 12-15 (ancla real: **USD 4,1 por agente** en M15, con 5 corridas hasta aprobar) | Olvidata (es desarrollo) |
| **Tokens de operación** del estudio | ~USD 25-40/mes estimados, **tope acordado USD 50/mes** | **El cliente**, acotado por el tope del producto |

> Precios verificados el 2026-09-23 contra la lista oficial: Sonnet 5 USD 2/10 por millón. El modelo por defecto del
> producto es Sonnet 5 por costo (decisión 2026-09-21).

## 5. Riesgos que afectan el número

| # | Riesgo | Efecto |
|---|---|---|
| R1 | **Primera vez que el estudio usa la API de SOS.** Nunca se ejerció | El dataset avisa que en una integración REST *el riesgo dominante es la habilitación de acceso, no el mapeo*. **A5 puede irse a 7-8 h** si el acceso da pelea |
| R2 | **Los agentes casi nunca aprueban en la primera versión** | Ya está en el M de A1-A3 (el ancla de M15 incluye 4 versiones), pero si un agente necesita más vueltas, se nota |
| R3 | **4 Directores sobre 6 personas** | No cambia el precio, sí el acompañamiento: más gente con criterio propio sobre lo que vale para toda la empresa |
| R4 | **Convenio Multilateral por COMARB, sin verificar** (A7) | A2 cotiza **solo lo de ARBA**. Si CM resulta automatizable, es un ítem aparte |
| R5 | **Credenciales hoy en archivos planos** | Migrarlas al producto está incluido en B2 para SOS. **Las de ARCA de ~100 clientes no están cotizadas**: hace falta definir alcance antes |

## 6. Decisión de `olvidata-ceo` (2026-09-23)

### Descuento: **NO aplica el Tier 1 de expansión agresiva**

Override del mismo tipo que FABINCO. Razón: BMA **ya paga SOS Contador y Bejerman/Onvio**, tiene 4 socios y capacidad de
pago demostrada — no necesita incentivo de precio para cerrar, y descontarle al lead mejor capitalizado juega en contra
del posicionamiento premium 2027.

- Se cotiza a **precio de lista promo** (vigente hasta 2026-12-31), sin descuento extra.
- El **grandfathering de la promo** (recurrente fijo de por vida si cierra antes de fin de año) es la palanca comercial.
- El **testimonio / caso de referencia se pide como condición aparte**, no se paga con descuento. La relación ya existe:
  el conversor está en producción desde junio.

### Modelo de cobro: setup + suscripción anual

Esquema **"Rubro estándar"** (aprobado 2026-09-21 para contable) + **un addon** por el único componente con conector.
**Nada por usuario ni por cliente de cartera** — coherente con la regla vigente de que los usuarios no modifican precio.

| Componente | Qué incluye | Setup | Mensual |
|---|---|---|---|
| **Rubro estándar** | Los 10 agentes existentes + `cont-arba` y `cont-soporte-sistemas` (sin conector) + configuración de organización, áreas y cartera | USD 1.500 (50/50) | USD 90 |
| **Addon Intermedio** | `cont-control-arca` **con el conector a la API de SOS Contador** | USD 1.000 | USD 80 |
| | | **USD 2.500** | **USD 170** |

**Números finales propuestos:**

| | |
|---|---|
| **Setup** | **USD 2.500** (rango del CEO: 2.000–3.000; se toma el punto que refleja la carga real de 100 clientes y 6 usuarios en la configuración inicial) |
| **Suscripción** | **USD 170/mes — USD 2.040/año** (rango del CEO: 1.800–2.400) |
| Tokens de IA | **Los paga el cliente**, con tope de USD 50/mes ya acordado (consumo estimado USD 25-40) |

### Cuánto del núcleo se le carga a BMA

**Solo el conector de SOS** (complejidad Intermedio, porque toca credenciales y configuración específicas). Los agentes
`cont-arba` y `cont-soporte-sistemas` entran en la tarifa plana del Rubro estándar **como inversión de producto**: el
núcleo se amortiza contra los próximos estudios contables, no se le cobra completo al primero. Es el mismo criterio que
ya se aplica en Build con la reutilización cross-proyecto.

## 7. El precio NO sale de las horas — y eso hay que tenerlo claro

Las 35 h M del WBS, por la fórmula de Build (M × 10,50), darían **USD 367**. El precio es **casi siete veces eso**, y
está bien que así sea: **acá no se vende esfuerzo, se vende un producto ya construido** (M1–M15) más el rubro contable
ya escrito. La fórmula de Build no aplica a este modelo (decisión de producto propio, 2026-09-21).

El WBS **sigue sirviendo para lo que sirve**: saber cuánto trabajo real hay detrás, dimensionar riesgos y alimentar la
calibración al cierre. **No para fijar el precio.** Conviene no mezclarlos al explicarlo internamente.

## 8. Una corrección al supuesto del CEO — y lo que hay que decidir

El CEO clasificó `cont-arba` como agente **"sin conector"**, y advirtió: *"si constatación ARBA termina requiriendo
scraping, pasa a Intermedio y sube el número"*.

**El research del 2026-09-23 dice algo distinto, y mejor: ARBA sí tiene web service oficial.** Consulta de alícuotas de
regímenes generales por CUIT y período (SOAP/XML, usuario y contraseña de ARBA), más el padrón mensual completo
descargable en `.txt`. **No hace falta scraping.**

Eso abre dos caminos, y hay que elegir uno **antes de presentar**:

| Camino | Qué hace `cont-arba` | Precio |
|---|---|---|
| **A — como está cotizado** | Trabaja sobre el **padrón `.txt` que la persona baja** de ARBA | Incluido en Rubro estándar. **Sin cambios** |
| **B — con conector ARBA** | Consulta el servicio DFE por CUIT y período, sin que nadie baje nada | **Segundo addon Intermedio**: +USD 1.000 setup y +USD 80/mes |

**Recomendación del presupuestador: arrancar con A.** El padrón mensual se baja una vez por mes y sirve para toda la
cartera de una; el conector ahorra ese único paso. Si después se ve que molesta, B se suma sin reescribir el agente
—es exactamente la arquitectura en capas que se definió— y se cobra como ampliación.

> Y queda dicho: **el conector de ARCA no se cotiza porque no existe** (research 2026-09-23). Si alguna vez apareciera,
> sería otro addon.

## 9. Lo que NO está cotizado

| Qué | Por qué |
|---|---|
| **Migrar las claves fiscales de los ~100 clientes** al almacenamiento cifrado del producto | Hace falta definir alcance primero. Hoy están en archivos planos: es el punto de seguridad marcado en el Análisis |
| **Conector de ARBA** | Camino B de arriba, a decidir |
| **Convenio Multilateral (COMARB)** | Sin verificar (riesgo A7) |
| **Absorber el conversor de sueldos** ya entregado | Decisión A3: más adelante |
| **Conector de ARCA** | **No existe el servicio** |

## 10. Estado final de la etapa (2026-09-23)

**Números FIJADOS por Joaquín: setup USD 2.500 · USD 170/mes (USD 2.040/año).** Sin descuento, según la decisión de
`olvidata-ceo`.

**ARBA: camino A, con automatización.** Elegido por Joaquín. `cont-arba` trabaja sobre el **padrón mensual que se
descarga de ARBA** (un archivo por mes que cubre toda la cartera), y **el control corre solo**: una programación mensual
(M12) dispara la constatación sin que nadie se acuerde de pedirla. La persona solo sube el padrón cuando lo baja.
**Sin cambio de precio** — el conector DFE (camino B) queda como ampliación posible.

> **Ampliación anotada, no cotizada:** también se podría automatizar **la descarga del ZIP del padrón** de ARBA (es una
> descarga autenticada con CIT, no scraping de pantalla). Eliminaría el último paso manual de esta rama. Queda como
> addon a evaluar después del piloto, junto con el camino B.

**La propuesta al cliente NO se arma todavía.** Decisión explícita de Joaquín: el presupuesto queda fijado internamente
y la implementación arranca igual.

> ⚠️ **Gate saltado a conciencia.** El flujo del estudio pide aprobación del cliente antes de Implementación. Joaquín
> decidió avanzar sin ese gate, como ya se hizo en otros proyectos (ganaderia, koi, vinosefue). **Queda registrado que
> lo que se construya antes de la aprobación es inversión de Olvidata en su propio producto** — y de hecho lo es: todo
> el bloque A queda en el núcleo y se revende a cualquier estudio contable, así que el riesgo real de avanzar es bajo.
