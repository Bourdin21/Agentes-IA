# Precios

**Fuente única de precios de Olvidata.** Vivía dentro de `.claude/agents/olvidata-ceo.md`, donde lo
citaban `olvidata-marketing`, `olvidata-sales` y `olvidata-presupuesto-bot` de memoria — y así nació
la contradicción que `decisiones.md` registra como DEC-003: la lista 2027 figuraba confirmada en un
agente y sin confirmar en otro. **Resuelta el 2026-10-16: está confirmada** (promo × 1,20), y el que
estaba desactualizado era `olvidata-marketing`.

**Regla de edición, controlada por `scripts/doctor.py`:** todo cambio a este archivo deja una línea
en `docs/olvidata/trazabilidad.md` con la fecha, el precio viejo, el nuevo y quién lo decidió. Un
precio que cambia sin rastro es un precio que nadie puede defender frente a un cliente que pregunta
por qué le cotizaron distinto el mes pasado.

Los parámetros de estimación (tasa, factores, rangos por tipo de módulo, descuentos) **no están
acá**: viven en `.github/instructions/27-presupuesto-parametros.instructions.md`, que es lo que lee
el presupuestador de proyectos. Este archivo son los precios de catálogo y de los planes.

---

### Planes de precios (USD/año + IVA, pagados en ARS al TC del día)
**Todos los precios de Olvidata son SIN IVA** (confirmado por Joaquín 2026-09-19): se cotizan y publican "+ IVA".

**Vigente desde 2026-09-19** (suba ~20% tras research de SaaS minorista argentino: Dux ~USD 281, Xubio ~341, Bsale 469/594/1.063 por año + IVA — ver `docs/referencia/research-precios-landing-build-2026-09.md`). Reemplaza 300/400/500/850 (2026-07-24), que no se aplica retroactivamente a clientes ya firmados.
- STARTER (1–5 tablas): USD 360 · 1 usuario
- PRO (6–15 tablas): USD 480 · hasta 2 usuarios
- PREMIUM (16–30 tablas): USD 600 · hasta 3 usuarios ← el más vendido
- SCALE (31+ tablas): USD 1.000 · usuarios ilimitados

Cargado en `27-presupuesto-parametros.instructions.md` de Agentes-IA. **No publicar estos precios en el sitio** (decisión de Joaquín 2026-09-19): el sitio en vivo sigue mostrando la tabla vieja y no se despliega el cambio.

Incluye: PWA móvil, hosting + SSL + dominio, actualizaciones de seguridad. Sin permanencia.

### Upsells (ronda cada 6 meses a toda la base)
**Vigente desde 2026-07-24, corregido 2026-09-14:** Módulo nuevo desde USD 250 (antes 200, pendiente confirmar si sigue vigente tras la baja de Merge — ver arriba) · UI personalizada $100 · Backup mensual $80/año.
- **Usuario adicional: sin cargo fijo, no es upsell.** Coherente con la regla vigente desde 2026-08-27 (los usuarios NUNCA modifican el precio del plan — ver memoria `feedback-mantenimiento-usuarios-anio1-gratis`): más allá de 10 usuarios se acuerda puntualmente con el cliente, sin cifra publicada. La cifra de USD 125/año que figuraba acá quedó desactualizada frente a esa regla; corregido ahora.
- **Performance y Ronda de ajuste: dejaron de ser upsells** (corrección 2026-09-14) — van incluidos en el precio del plan de mantenimiento (STARTER/PRO/PREMIUM/SCALE), no se cobran aparte.
Upsell observado H1 2026 (con precios pre-suba): +39% sobre el plan base → ticket efectivo real **observado: USD 474**. Para planificación se usa un valor conservador de **USD 426** (90% del observado, descontando funciones one-time) — es el número que aparece en el plan financiero, no el techo real. Recalcular con datos reales una vez que la nueva base de precios tenga uno o más ciclos de upsell.

### Planes AI Agents y Chatbots (vigente desde 2026-09-14 — confirmado por Joaquín, PROMO de entrada)

**Condición de la promo:** estos precios son **promocionales de entrada**, válidos solo para clientes que **cierren (firman/pagan anticipo) hasta el 2026-12-31**. Desde el 2027-01-01 rige la lista post-promo (ver más abajo): **promo × 1,20, confirmada por Joaquín** el 2026-09-19 y reconfirmada el 2026-10-16 (DEC-003). Setup = pago único; Recurrente = USD/año, mismo esquema de pago que el resto del catálogo (ARS al TC del día).

**AI Agents** — agentes administrativos/operacionales, tier por complejidad del agente (no por costo de IA, que es marginal frente al valor de horas administrativas ahorradas):

| Tier | Setup (único) | Recurrente/año |
|---|---|---|
| Básico (1 proceso, sin integraciones externas) | USD 1.500–2.500 | USD 2.400 |
| Intermedio (2-3 pasos, 1 integración externa) | USD 3.000–5.000 | USD 4.800 |
| Avanzado (multi-step, herramientas múltiples) | USD 6.000–9.000 | USD 8.400 |

> **ACTUALIZADO 2026-09-19, confirmado por Joaquín**, por research de mercado argentino (`docs/olvidata-agentes-multirubro/research-precios-ai-agents-2026-09.md`): la tabla anterior (300–400/600–800/1.200–1.500 + 400/650/1.000) quedaba debajo del piso local. La promo queda entre el piso y la mediana argentina; la lista 2027 (×1,20) en la mediana/mediana alta.

**Reglas de cotización de AI Agents (definidas por Joaquín 2026-09-15):**
- **El precio es POR AGENTE**, no por cantidad de agentes: el tier mide la complejidad de cada agente (pasos encadenados del proceso + integraciones con sistemas externos). Un cliente con 2 agentes paga 2 setups y 2 recurrentes, cada uno según su tier.
- **Varios agentes para un mismo cliente: 10% de descuento en cada agente nuevo** (a partir del segundo, sea en la misma propuesta o sumado después). Supuesto a confirmar por Joaquín: el 10% aplica a setup y recurrente de ese agente adicional; el primer agente va a precio de lista.
- **Conteo de integraciones:** cada sistema/proveedor externo distinto cuenta como una integración (2 cuentas del mismo banco = 1; banco + Mercado Pago = 2). Supuesto a confirmar por Joaquín.
- **Cambio de tier:** si un agente suma pasos o integraciones y pasa de tier (ej. Básico → Intermedio), paga la diferencia de setup entre tiers y desde la renovación siguiente el recurrente del tier nuevo.

**El portal (`Olvidata Agentes Multi-rubro`) NO es un SaaS aparte — corrección de Joaquín 2026-09-21.** Es el **modo estandarizado de entregar AI Agents**: desarrollo a medida de agentes IA personalizados por organización, construido sobre el portal multi-tenant en vez de un proyecto artesanal desde cero por cliente. El setup de la tabla de arriba sigue existiendo (es el trabajo de análisis + configuración + entrenamiento del agente), el portal es la infraestructura que lo sostiene (licencia, versionado, telemetría, conectores, aprobaciones). Cualquier tabla anterior que planteaba el portal como un SaaS de abono fijo separado (Starter/Pro/Business) queda **descartada**.

**Mapeo tier → configuración en el portal (confirmado por Joaquín 2026-09-21):**
- **Básico**: un agente propio de la organización (`AgenteOrganizacion`), típicamente derivado de un agente del núcleo del rubro con personalización de instrucciones/tono; sin conectores (M11) activos; reglas de organización/cliente básicas; sin subagentes.
- **Intermedio**: agente propio + **1 conector (M11) activo** con sus credenciales propias de la organización (aprobación por llamada del Director); reglas más específicas; eventualmente un coordinador simple con 1 subagente si el proceso lo requiere.
- **Avanzado**: agente(s) coordinador con subagentes (M7a), múltiples conectores activos, posible tarea programada (M12), reglas de aprobación por rol (M6) para pasos sensibles.

**Crédito de IA incluido y excedente (confirmado por Joaquín 2026-09-21) — reemplaza la frase anterior sobre "costo real medido" en el recurrente:**
- El recurrente **incluye un crédito de IA mensual a costo real** (sin margen — el margen del recurrente está en el resto del servicio: infra, monitoreo, ronda de ajuste de prompt). Regla: **crédito mensual = 10 % del recurrente/año ÷ 12** de ese agente (Básico USD 20/mes · Intermedio USD 40/mes · Avanzado USD 70/mes). Es un supuesto de arranque de `olvidata-ceo`, a confirmar con datos reales una vez medido el consumo de los primeros agentes en producción.
- **Excedente:** una vez agotado el crédito del mes, el costo real medido en `EventoUso` se factura al cliente **× 3**, en el ciclo siguiente.
- **Tope de gasto por defecto (corta el servicio, portal ya lo soporta vía `Tenant.LimiteMensualUsd`/M6):** crédito × 5 (Básico USD 100/mes de costo real · Intermedio USD 200 · Avanzado USD 350) — coincide con el default de plataforma de USD 100/org/mes para el caso Básico. Configurable por agente/organización.
- **Precio de token verificado 2026-09-21** (antes marcado como supuesto no verificado): Sonnet 5 (modelo por defecto del portal) USD 2/10 por millón de tokens entrada/salida, estándar sin promo; Opus 5 USD 5/25; Haiku 4.5 USD 1/5; caché de prompts 5 min: escritura ×1,25, lectura ×0,1; búsqueda web USD 10 cada 1.000.

**Chatbots** — ventas y consultas automáticas, tier por volumen de conversaciones/mes (acá el driver es volumen porque es cara al prospecto, no complejidad interna):

| Tier | Setup (único) | Recurrente/año |
|---|---|---|
| Starter (hasta 200 conv/mes) | USD 700–900 | USD 480 |
| Pro (hasta 600 conv/mes) | USD 900–1.200 | USD 700 |
| Scale (alto volumen) | USD 1.200–1.800 | USD 1.100 |
| **Grandes empresas** (nuevo 2026-09-19) | USD 2.500–4.000 | USD 3.000 |

> **Asistente dentro de un sistema del estudio — un solo recurrente (COM-021, 2026-10-17).** Cuando el
> chatbot/asistente no es un servicio suelto sino que vive **dentro de un Build nuestro** —mismo hosting,
> misma base, mismo deploy—, **no se cobran dos abonos anuales**. Las dos líneas facturan lo mismo
> (infra, monitoreo, ronda de ajuste) y superponerlas es cobrar dos veces la misma infraestructura: no se
> puede defender si el cliente lo mira de cerca.
>
> Qué se cobra entonces:
> - **Recurrente: una sola línea**, la del plan de mantenimiento, y el plan sale de la tabla por **cantidad
>   de tablas de negocio** contando las que agrega el asistente (conversaciones, mensajes, mapeo
>   teléfono→cliente). En la práctica eso suele mover el sistema un escalón de plan, que es exactamente lo
>   que paga la atención extra del bot: afinar el prompt y mirar conversaciones con clientes reales.
> - **Setup: sí se cobra separado.** Construir el sistema y configurar el asistente son trabajos distintos,
>   más las horas de integración (API de alta de solicitud, consulta de estado, aviso de salida,
>   idempotencia). Ahí no hay duplicación.
> - **El año 1 de mantenimiento gratis (COM-014) cubre la parte del sistema, no el servicio del asistente**:
>   el año 1 se cobra el recurrente del tier de chatbot que corresponda, y recién desde el año 2 rige la
>   línea única del plan.
>
> Origen: lead Grupo Arreglo Todo (2026-10-17). La regla **no existía** y el primer armado cotizaba
> USD 480 de mantenimiento + USD 480 del asistente = USD 960/año sobre un único sistema. Lo detectó Joaquín
> preguntando por qué se cobraba doble.

> **CORREGIDO 2026-09-17, confirmado por Joaquín.** Reemplaza la tabla anterior (setup USD 400–700 igual para los 3 tiers + recurrente 350/550/900), que estaba 5–10x debajo del mercado de desarrollo a medida y **por debajo del piso de rentabilidad**: un Starter a 200 conv/mes tenía USD 6–21/mes de costo directo contra USD 29/mes de ingreso. Fundamento en `docs/olvidata-agentes-multirubro/trazabilidad.md` (2026-09-17), con research de mercado de septiembre 2026: agencia bot esencial USD 1.500–3.000, bot inteligente USD 3.500–6.000 + USD 200–400/mes; SaaS autoservicio USD 59–279/mes. Todos esos precios **excluyen la mensajería de Meta**, igual que el de Olvidata — la comparación es directa. Cambios respecto de la tabla vieja: (1) el setup ahora **escala por tier** (antes era el mismo rango para los tres, a diferencia de AI Agents); (2) **piso duro: no vender un Starter por debajo de USD 40/mes (USD 480/año)**.
>
> **Modelo de facturación de mensajería — Tech Provider (decidido 2026-09-17, aplica a TODOS los planes).** El WABA es del cliente y **el cliente le paga a Meta directo** con su medio de pago (~USD 0,0618 por conversación de marketing en Argentina); Olvidata no tiene línea de crédito ni responsabilidad por el consumo. El cliente trae además **su propia key de Claude**. Consecuencia: el costo directo por cliente queda en hosting + monitoreo, y el encarecimiento de Meta del 01/10/2026 (cobra por mensaje, incluidas las respuestas de servicio en la ventana de 24hs) **no golpea el margen de Olvidata**. Decir siempre en la propuesta que la mensajería va aparte — es lo que hace todo el mercado.
>
> **Pendientes de definir (no bloquean cotizar):** qué cuenta como "conversación" (la ventana de 24hs de Meta es lo razonable) y qué pasa si un Starter supera 200 conv/mes de forma sostenida — para AI Agents la regla de cambio de tier existe, para Chatbots no está escrita.

El recurrente cubre: infra/hosting, tope de gasto con kill switch (mismo patrón que el CRM propio), monitoreo, 1 ronda de ajuste de prompt/mes, y el **crédito de IA incluido a costo real** (ver regla de crédito + excedente ×3 en la sección de AI Agents arriba — reemplaza la redacción anterior de "costo real medido incluido sin tope explícito"). Costo real medido de referencia (bot del CRM propio): USD 0,006–0,045 por conversación con Opus 5 — el margen en estos dos frentes es alto por diseño.

**LISTA VIGENTE AI Agents / portal — Joaquín 2026-09-21 (REEMPLAZA las tablas Básico/Intermedio/Avanzado de arriba, que le resultaron muy elevadas; solo el plan base entraba en lo que tenía pensado):** esquema **plan base + adicional por agente**. USD, + IVA, promo hasta 2026-12-31, lista 2027 = ×1,20.
- **Plan base = Rubro estándar** (contable o inmobiliario, agentes del núcleo sin personalizar): setup USD 1.500 (50/50) + USD 90/mes. Crédito IA USD 15/mes, tope USD 60/mes.
- **Agente a medida Básico:** + USD 500 setup + USD 40/mes (+ USD 5 de crédito, + USD 20 de tope).
- **Agente a medida Intermedio:** + USD 1.000 setup + USD 80/mes (+ USD 10 de crédito, + USD 40 de tope).
- **Agente a medida Avanzado:** + USD 2.000 setup + USD 150/mes (+ USD 20 de crédito, + USD 80 de tope).
- Excedente de consumo = costo real × 3. Sin descuento multi-agente (los adicionales ya son bajos).
- La propuesta de USD 11.000 + 13.200/año para BMA queda sin efecto: con este esquema, base + 2 Intermedios + 2 Básicos = USD 4.500 setup + USD 330/mes.

**Decisiones de Joaquín 2026-09-21 tras el research freelance** (`docs/olvidata-agentes-multirubro/research-precios-freelance-ai-agents-2026-09.md`):
- **Tier "Rubro estándar" APROBADO para los rubros contable e inmobiliario**: agentes del núcleo del rubro sin personalización a medida, para competir con productos verticales cerrados (caso Top Producer System: USD 2.200 + USD 50/mes). Rango propuesto por el research: setup USD 1.000–1.500 + USD 60–90/mes con crédito de IA topado. **Montos fijados por Joaquín 2026-09-21: setup USD 1.500 (pago 50/50) + USD 90/mes por organización y rubro, con crédito de IA incluido de USD 15/mes, excedente ×3 y tope de corte USD 60/mes; lista 2027 ×1,20; + IVA.** La personalización (agentes propios, reglas a medida, conectores) pasa a Básico/Intermedio/Avanzado.
- **Entrega de código: se vende el núcleo del sistema a un valor más elevado** (por encima de los USD 5.000–6.000 de un proyecto aparte que sugería el research). Es una excepción comercial y consciente a la regla §9 del producto ("lo que baja al disco del cliente ya se perdió"): se cotiza como transferencia del know-how, con contrato de licencia (sin reventa ni redistribución) revisado por abogado. **Monto fijado por Joaquín 2026-09-21 (corregido el mismo día, antes USD 20.000): USD 6.000 por rubro (pago único, incluye plataforma + núcleo del rubro, licencia de uso interno sin reventa ni redistribución) + soporte opcional USD 1.200/año (consultas y correcciones, sin actualizaciones del núcleo); + IVA.**

**Propuesta de precio — Contadores BMA (primer cliente en producción, precio de LISTA sin piloto, confirmado por Joaquín 2026-09-21) — PROPUESTA de `olvidata-ceo`, pendiente del presupuestador real:**
Discovery de `contadores-bma-agentes-ia` todavía abierto (Presupuestador sin iniciar) — este cálculo es una estimación de referencia, no el presupuesto formal. Alcance Fase 0-1 (ver `docs/contadores-bma-agentes-ia/definiciones/1-analista-funcional.md`): 1 agente piloto + 2-4 agentes más, todos sobre adaptador A (archivos exportados a mano, sin integración automatizada — Bejerman/Onvio bloqueado contractualmente por Thomson Reuters). Supuesto de 4 agentes para esta estimación, setup al punto medio del rango de cada tier:

| # | Agente | Tier | Setup | Recurrente/año | Con descuento multi-agente |
|---|---|---|---|---|---|
| 1 | Bot de consultas (manuales Bejerman + SOS Contador) | Básico | USD 2.000 | USD 2.400 | — (1º, precio de lista) |
| 2 | Conciliación bancaria | Intermedio* | USD 3.600 | USD 4.320 | -10 % |
| 3 | Impuestos/IVA ("Impuestos BMA") | Intermedio* | USD 3.600 | USD 4.320 | -10 % |
| 4 | Balances | Básico | USD 1.800 | USD 2.160 | -10 % |
| | **Total** | | **USD 11.000** | **USD 13.200/año** (≈ USD 1.100/mes) | |

\* Conciliación e Impuestos se cotizan Intermedio por sus varios pasos internos (parseo + matching/cálculo + resolución de excepciones), aunque en Fase 0-1 no tengan conector M11 activo (la definición de tier liga Intermedio a "1 integración externa" — acá no la hay todavía). **Marcar como supuesto a confirmar por Joaquín**: si se aplica estricto el criterio de la tabla, estos dos agentes bajarían a Básico. La versión personal "Mi IVA" (variante de Impuestos BMA para un solo usuario) se asume **incluida en el mismo agente**, no facturada aparte, porque es una personalización (ficha "Crear mi versión"), no un agente nuevo — otro supuesto a confirmar.

Crédito de IA incluido total: USD 20+36+36+18 = **USD 110/mes**. Tope de gasto por defecto total: **USD 550/mes** (crédito × 5 por agente). Cifras de setup y cantidad/tier de agentes deben cerrarse recién cuando termine Discovery y corra el Presupuestador real de `contadores-bma-agentes-ia`. **Superada por el rediseño de 2026-10-13 de abajo** (el esquema "plan base + N agentes a medida" asumía pocos agentes por cliente — no es así, ver regla nueva).

**REDISEÑO de pricing AI Agents multirubro — Joaquín, 2026-10-13.** Motivo: *"las empresas pueden tener infinitos agentes. no escatimar en esto y recuantificar la manera de incluirlos en los planes."* **Joaquín aprueba el MODELO como regla fija. El PRECIO (los montos de abajo) queda VIGENTE PERO BAJO REVISIÓN — textual: "no estoy seguro del precio, me parece caro"** — no tratar estos números como definitivos sin chequear si ya se ajustaron. Research de mercado hecho el mismo día (ver tabla comparativa más abajo): en los tres mercados comparables (implementadores Argentina, gestorías España, AI accounting SaaS EE.UU.) y contra el costo de construir la plataforma desde cero (USD 100.000–300.000, agencia, 2026), el precio vigente de Olvidata aparece **barato, no caro** — queda registrado así, la decisión final de ajustar o no es de Joaquín.

El driver de costo real **no es la cantidad de agentes** (un agente derivado por instructivo vía M15, self-service, cuesta USD 0 de construir) — son: integraciones reales a mantener, ingeniería nueva genuina (agente no derivable del núcleo), y volumen de tokens medido (ya cubierto por crédito/excedente ×3). Reemplaza el supuesto de "plan base + N agentes a medida" con tope implícito.

1. **Setup — tres ejes, nunca por cantidad de agentes:**
   - Licencia de rubro + organización (alta tenant, roles, cartera, piloto): USD 1.500, 50/50. Sin cambios respecto de lo ya fijado.
   - Conector nuevo (integración externa), por sistema distinto, sin importar cuántos agentes lo usen: Simple USD 500 · Media USD 900 · Compleja/sin API USD 1.500.
   - Agente 100% personalizado (bespoke, no derivable del núcleo por instructivo): Básico +500 · Intermedio +1.000 · Avanzado +2.000 (mismos montos y crédito/tope ya fijados el 2026-09-21).
   - **Agente derivado por instructivo (self-service, M15): USD 0, cantidad ilimitada.** Es la pieza que resuelve el "infinitos agentes" de Joaquín.

2. **Mensual:** base por tier de volumen de uso real de la organización — Org S/M/L, **números propuestos por `olvidata-ceo`, no fijados por Joaquín todavía**: S USD 90 (crédito 20, tope 100) · M USD 150 (crédito 50, tope 250) · L USD 250 (crédito 100, tope 500) — + USD 25/mes por cada conector activo (monitoreo/credenciales) + el mensual propio de cada agente personalizado (40/80/150, sin cambios). Un cliente con muchos agentes derivados paga más automáticamente porque cae en un tier Org más alto por volumen medido, no porque se facture "por agente".

3. **Regla operativa de clasificación núcleo vs. personalizado (aplicable, no a ojo): si la regla la fija el organismo o el sistema externo (ARCA, ARBA, el formato de Bejerman/SOS Contador), va al núcleo, dentro de la licencia. Si la regla la fija el estudio/organización, es personalizado y se cobra aparte.** Reutiliza la distinción que el propio portal ya usa en diseño ("reglas de organización/cliente" vs. reglas del rubro) también como criterio de facturación.

4. **El núcleo se nutre en cada setup — eso NO sube el precio de la licencia.** Lo generalizable de cada cliente (bajo la regla del punto 3) pasa al núcleo y beneficia a todos los próximos estudios del rubro. La licencia se mantiene estable dentro de cada ciclo de promo/lista; el enriquecimiento del núcleo es argumento de venta y respalda las subas YA calendarizadas (lista 2027 ×1,20), nunca un recálculo ad hoc cliente por cliente.

5. **Cliente 1 (el que aporta el criterio que después se estandariza) se reconoce con precio piloto, no con regalía ni % de reventa** — mismo mecanismo que "Pilotos con descuento hasta 2027" ya fijado el 2026-09-19.

6. **Bernarda (relevamiento externo) dentro de este modelo: +USD 700 flat al setup (por cliente, no por agente) cuando el proyecto tiene ≥1 agente 100% personalizado Intermedio/Avanzado.** Su entregable tiene que cumplir, como condición exigible del acuerdo: (1) vocabulario exacto del cliente/rubro, (2) reglas de negocio en formato condicional, (3) circuitos paso a paso con actor/rol/herramienta real, (4) ejemplos reales anonimizados, (5) excepciones/casos borde que se resuelven a mano, (6) inventario de integraciones con tipo de acceso. Sin estos seis puntos no sirve de insumo de configuración. Su trabajo arranca **después del 50% de anticipo cobrado**, nunca antes de firmar — así no hay riesgo de que Olvidata le pague sin que el cliente cierre. Lo que releva alimenta tanto el núcleo (lo generalizable) como lo personalizado (lo que se cobra) — parte de lo que paga ese cliente termina mejorando el producto para los próximos.

7. **BMA recalculado sobre los 4 ejes reales del requerimiento original** (`metadata.md` / `guion-discovery.md` Bloque 3: conciliación bancaria, balances, impuestos, sueldos — "manuales/soporte" queda fuera del conteo como transversal, no eje de negocio) **y no sobre los agentes nacidos del research técnico** (`cont-control-arca`, `cont-arba`, `cont-soporte-sistemas`: surgieron del research de ARCA/ARBA/SOS del 2026-09-23 para probar capacidad del sistema, no del relevamiento con el cliente): **setup USD 4.000 (+USD 700 Bernarda si aplica) / mensual USD 290, sin conector** (los 4 ejes trabajan sobre archivo exportado, no necesitan integración). La brecha contra lo informalmente pactado (USD 2.500/USD 170) queda registrada como **descuento piloto**, no como error de cálculo — detalle en `docs/contadores-bma-agentes-ia/trazabilidad.md`, entrada 2026-10-13.

**Research de mercado 2026-10-13 (resumen; detalle completo lo tiene el chat con Joaquín, no reproducido aquí para no congelar un número en revisión):** en los tres comparables — implementadores de agentes IA en Argentina (setup US$5.000–15.000+/mensual US$300–1.500+ para "agente integrado", cosys.com.ar, 2026-09-18), gestorías/asesorías España (€9.000–15.000 setup + €280–450/mes para un despacho de 7-15 personas con 3 flujos, agregado de javadex.es, 2026) y AI accounting SaaS EE.UU. (US$20.000–80.000/año mid-market) — el precio vigente de Olvidata para un caso tipo BMA (USD 4.000–4.700 setup / USD 290/mes) queda **por debajo de los tres**. Contra el costo de construir la plataforma desde cero (plataforma multi-tenant con compliance/monitoreo: USD 100.000–300.000 + USD 2.000–15.000/mes de mantenimiento, agencia, groovyweb.co 2026), la diferencia es de un orden de magnitud — es el argumento de fondo de por qué vender licencia de un núcleo ya construido, no re-construirlo por cliente.

**DECISIÓN de Joaquín 2026-09-19 — posicionamiento premium de AI Agents (la tabla de abajo queda REEMPLAZADA por esta regla):**
1. **Promo 2026 fijada por research de mercado** (Argentina primero): aplicada en las tablas de arriba.
2. **Lista 2027 = promo × 1,20** (suba de 20%, no la ~25-30% recomendada abajo). Objetivo: salir como opción premium ("la startup más cara") en 2027.
3. **Pilotos con descuento hasta 2027**, a cambio de caso/logo/testimonio (prueba de autoridad que exige PACS para vender premium a grandes empresas). Porcentaje de descuento y cantidad de pilotos: a definir.

**Lista 2027 vigente (desde 2027-01-01, promo × 1,20, + IVA):**

| Frente / Tier | Setup 2027 | Recurrente/año 2027 |
|---|---|---|
| AI Agents Básico | USD 1.800–3.000 | USD 2.880 |
| AI Agents Intermedio | USD 3.600–6.000 | USD 5.760 |
| AI Agents Avanzado | USD 7.200–10.800 | USD 10.080 |
| Chatbot Starter | USD 840–1.080 | USD 576 |
| Chatbot Pro | USD 1.080–1.440 | USD 840 |
| Chatbot Scale | USD 1.440–2.160 | USD 1.320 |
| Chatbot Grandes empresas | USD 3.000–4.800 | USD 3.600 |

**Lista post-promo (desde 2027-01-01) — RECOMENDACIÓN anterior de `olvidata-ceo`, SUPERADA por la decisión de arriba (×1,20), se deja como historial:**

| Frente / Tier | Setup post-promo | Recurrente/año post-promo |
|---|---|---|
| AI Agents Básico | USD 400–500 | USD 500 |
| AI Agents Intermedio | USD 800–1.000 | USD 800 |
| AI Agents Avanzado | USD 1.500–1.900 | USD 1.300 |
| Chatbot Starter | USD 500–800 | USD 450 |  ← **RECALCULAR**: quedó por debajo del precio promo nuevo (480)
| Chatbot Pro | USD 500–800 | USD 700 |
| Chatbot Scale | USD 500–800 | USD 1.150 |

Justificación de la suba (~25-30%): (1) precedente propio — la suba de Build de 2026-07-24 y la ronda de upsells del mismo día aplicaron incrementos del mismo orden (~20-25%); (2) para 2027 estos dos frentes van a tener casos reales/prueba social (hoy cero) que suben la disposición a pagar (category design: una vez posicionado como categoría propia, no hace falta competir por precio); (3) mantiene la cadencia ya usada de rondas de precio, sin regalar dos veces la eficiencia ganada. **Lista confirmada por Joaquín** (2026-09-19, reconfirmada 2026-10-16 al resolver DEC-003): se cotiza desde el 2027-01-01. El cliente que cerró con la promo antes del 2026-12-31 mantiene su precio (COM-016), así que esta lista aplica a clientes nuevos, no a la base.

**Cómo comunicar la promo en la venta (coherente con cierre pasivo, ver sección de canales):**
- Se menciona **una sola vez**, como parte natural de la propuesta ("este valor es de lanzamiento, para cierres hasta el 31/12") — no se repite como presión en cada follow-up.
- La urgencia es **real** (hay fecha concreta, no fabricada) — mismo criterio que el vencimiento de 7 días de toda propuesta: se informa, no se empuja. Nunca sumar lenguaje de escasez inventado ("quedan pocos lugares") encima de la fecha real.
- No hace falta acelerar artificialmente el ciclo de 7–10 días por la promo — si un deal iniciado en diciembre cruza la fecha de forma natural sin que el prospecto haya dilatado a propósito, se respeta el precio promo acordado en la propuesta (la propuesta ya tiene su propio vencimiento de 7 días, que es la urgencia real operante turno a turno).

**Renovación — el cliente que entra con la promo mantiene ese precio (decisión recomendada, no una fecha límite oculta):** una vez cerrado antes del 2026-12-31, el recurrente promo queda **grandfathereado** (fijo) para ese cliente mientras siga activo sin discontinuar el servicio — no salta a lista en la renovación siguiente. Mismo criterio que ya se usó con los planes STARTER/PRO/PREMIUM/SCALE (la suba de 2026-07-24 no se aplicó retroactivamente a la base ya firmada) y con La Platense (año 1 regalado, año 2 a precio pactado, no recalculado). Motivo de negocio: son los primeros clientes de un frente sin trayectoria todavía — el incentivo real es la certeza de precio a cambio de ser caso de prueba, no un descuento que se retira apenas renuevan. Esta es una recomendación de `olvidata-ceo`; avisar si Joaquín prefiere otro criterio.
