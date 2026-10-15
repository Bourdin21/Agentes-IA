# Reglas de comunicación — Olvidata Soft

**Fuente única** de las reglas de comunicación y contenido (consolidado 2026-10-15). Antes estaban copiadas en `olvidata-ceo`, `olvidata-marketing` y `olvidata-cm`, y se habían desincronizado: `ceo` y `marketing` seguían prohibiendo abrir por el dolor en Agentes IA cuando `cm` ya tenía la derogación del 2026-10-14.

- **Dueño:** `olvidata-marketing` (la edita). Una decisión nueva de Joaquín se escribe **acá**, como regla nueva con fecha, y la que reemplaza queda marcada `superada por COM-xx`.
- **La aplican:** `olvidata-cm` (cada pieza), `olvidata-marketing` (templates y canales), `olvidata-sales` (demo y propuesta), `olvidata-ceo` (encuadre de producto).
- **Leerla entera antes de producir o revisar una pieza.** Es corta a propósito.
- Detalle de origen en `C:\Sistemas\BotPublicitario\MARCA.md` § 0 y § 0e, y `claims.md`.

## Tabla rápida — qué se puede en cada frente

| | Build (sistemas de gestión por rubro) | Agentes IA / Second Brain corporativo |
|---|---|---|
| Abrir por el dolor del dueño | **Sí** | **Sí** (desde 2026-10-14) |
| Contar cómo se hizo (paso a paso, decisiones técnicas) | **Sí** — molde problema → intento → cómo quedó | **No, nunca** |
| Mostrar el producto terminado operando | Sí | Sí — es la pieza |
| Precio o CTA de venta en contenido público | No | No |
| Nombre o logo del cliente | No | No |
| Compararse contra un competidor o "el mercado" | No | No |

---

## COM-01 — El contenido de autoridad no vende (2026-10-01)

*"Quiero contar mi experiencia antes que vender un producto; que vean que soy bueno y que me vengan a pedir lo que hago."*

- **Alcance:** Instagram, LinkedIn, el sitio y el **mensaje de apertura del bot outbound**. No aplica a la propuesta ni al WhatsApp una vez que el prospecto mostró interés: esa es **la única zona de venta directa**.
- **Ningún precio en pantalla ni en caption.** El precio no cambia, cambia dónde se dice: en la demo o la propuesta.
- **Ningún CTA pide la venta.** Va la **pregunta de oficio** (*"¿cómo lo hacés vos?"*) o el **pedido de volver** (*"la semana que viene muestro cómo quedó"*).
- **Ningún nombre de cliente.** Los casos se cuentan por rubro ("una ferretería"). Cara y pantalla sí; nombre y logo no. Montos y datos de cliente solo con autorización.
- **Riesgo asumido:** sin CTA, Instagram va a parecer que no rinde justo cuando empiece a rendir. Se mide **conversión asistida** (leads que mencionan el perfil y su tasa de cierre contra los fríos), nunca alcance.

## COM-02 — Nada se afirma sin fuente puntual (2026-10-01)

Todo caso sale del **proyecto real** — qué se pidió, qué problema había, cómo se resolvió — sacado del repo o de los docs. Nunca de memoria, nunca "verosímil". **Sin fuente puntual, no se publica.** El 2026-10-01 se escribieron ocho captions deduciendo la historia desde el rubro: las ocho eran plausibles y ninguna salía de ningún lado. El inventario de qué se puede afirmar de cada caso lo mantiene `olvidata-cm`.

## COM-03 — Directo al grano, sin compararse (2026-10-11; la parte del dolor, superada por COM-04)

*"Tenés que ir directo al grano. Estamos mostrando un producto sin querer venderlo. El cliente compra experiencias."*

- **La primera placa muestra la cosa**, no el contexto que la justifica. Si la primera línea se puede borrar sin perder nada, era preámbulo.
- **Se muestra la experiencia de usarlo**: qué se siente, qué pasa cuando lo usás.
- **No se arma la pieza contra nada:** ni un competidor nombrado ni "la práctica genérica del mercado". Compararse es vender.
- ~~Prohibido abrir por el problema, el riesgo o el error ajeno~~ → **superado por COM-04**.

## COM-04 — El hook puede abrir por el dolor, en todos los frentes (2026-10-14)

*"El hook lo considero que está bien. Reescribir regla si es necesario."* — sobre el Reel de agentes (*"¿Estás cansado de hacer lo mismo todos los días?"*), que había sido bloqueado esa tarde.

Un hook que nombra la vida del dueño no enseña nada. Lo que protege el negocio en Agentes IA es la prohibición del **método** (COM-05), que sigue intacta. Build ya lo tenía habilitado desde la mañana del 14/10. Pieza que lo motivó: `contenido/reels/reel-agentes-criterio.mp4` (bloqueo levantado, no se reabre).

## COM-05 — Agentes IA: se muestra el producto operando, el método no se publica (2026-10-13; alcance acotado 2026-10-14)

*"Mostrar cómo se hacen las cosas es correr el peligro de que aprendan a hacerlo por su cuenta y no necesiten mis servicios. Quiero mostrar el producto final terminado operando. La información es energía. La fórmula es secreta de Olvidata."*

**Alcance: solo el frente de Agentes IA / Second Brain** (*"En los sistemas Build está bien abrir por el dolor y contar cómo se hizo"*). En Build, el relato de cómo se resolvió **es** la prueba de oficio, y sin él las piezas quedaron sin arco (*"no tienen narrativa"*).

**Lo que va:** el producto andando, filmado o capturado del proyecto real. Molde por defecto: el Reel de la ferretería.

**Lo que no va, en ninguna pieza pública de Agentes IA:** el paso a paso, "lo que no funcionó", la decisión técnica explicada como enseñanza, tips, tutoriales, stack, arquitectura interna, prompts, pipeline, repos, nombres de archivos, las herramientas con que se produce, cuánto tardó.

**Escalera de revelación** — el detalle sube solo con el compromiso del lead:

| Nivel | Qué se muestra |
|---|---|
| Público | El producto funcionando, qué hace, qué se siente. Nada reproducible |
| Demo | Operando sobre el caso del prospecto. Se contesta *qué hace*, no *cómo está hecho* |
| Propuesta | Alcance, módulos, límites, precio |
| Cliente firmado | Criterios de diseño y documentación de su propio sistema |
| Nunca | Stack, arquitectura interna, prompts, pipeline, repos, herramientas, tiempos de construcción |

**Por qué:** el how-to es justo lo que cualquier IA produce en segundos; publicarlo comoditiza la autoridad y entrena al prospecto para no necesitarte. **El que quiere aprender a hacerlo no es un lead.** El consenso de contenido 2026 recomienda enseñar: acá está vetado y no se reabre.

## COM-06 — Concepto rector: es el mapa, no las instrucciones (2026-10-11)

El activo diferencial de Agentes Multi-rubro **no es su funcionalidad**: es que está construido sobre un concepto rector escrito, con un lugar y un límite por pieza.

- **La computadora** (`C:\Sistemas\Olvidata Agentes Multi-rubro\docs\el-sistema-como-computadora.md`, aprobado 2026-09-24): RAM, CPU, disco, ojos, oídos, impresora, buses, reloj, energía. Para quien evalúa con criterio técnico.
- **El organismo** (`docs\el-agente-como-organismo.md`, 2026-10-11): conciencia, inconsciente, memoria, sentidos, nervios, manos. Para quien no es técnico; se puede dibujar.

Cómo se usa: nunca como lista de funciones ni por volumen (módulos, tests, integraciones). Una lectura por pieza, sin mezclar. Cada criterio como **comportamiento** (*"la CPU no ve el disco: pide"*). **Lo que no existe se dice** (el agente no tiene oído ni voz): es lo que hace creíble el resto. **Se publica el mapa; nunca las instrucciones**: si una pieza pasa del mapa al instructivo, se cae. El concepto es lo que sostiene el ticket en la propuesta.

## COM-07 — El mapa está pausado: as bajo la manga (2026-10-13)

Las piezas que explican el producto con el concepto rector **salen del feed y se guardan** (no se cayeron: se reservan).

- **Pausadas:** carrusel del organismo, su compañera de LinkedIn (la computadora), memoria de corto plazo, de instrucción a regla, carrusel del producto (`LINEA-SECOND-BRAIN.md` § PAUSADA).
- **Dónde se usan:** demo, propuesta y 1 a 1. El carrusel del organismo es material de venta, no de feed.
- **En público mientras tanto:** solo producto operando.
- **Cómo vuelve:** lo decide Joaquín, cuando haya casos operando publicados que lo respalden. No se producen piezas nuevas de concepto rector para el feed; si un pedido pide explicar el producto, se produce para demo o propuesta y se dice.

## COM-08 — Second Brain corporativo se comercializa desde noviembre: por la tarea, no por la idea (2026-10-13)

Plan completo en `BotPublicitario/plan_comercializacion_second_brain_nov2026.md`.

- **Se vende una tarea de oficina que deja de hacer una persona.** Cuatro beats: **el pedido** en castellano → **el agente trabajando** → **el entregable hecho** → **el límite dicho** (*"nada se presenta, se paga ni se manda solo"*). Cierra con pregunta de oficio, sin precio.
- **No se dice qué idea es.** El nombre es etiqueta al pie, nunca titular. El titular es la tarea resuelta.
- **Noviembre es el estudio contable**, el único caso real: conciliación (10/11), sueldos (24/11), impuestos (08/12). Por rubro, sin nombre, logo, montos ni resultados.
- **Desde diciembre, rubro por rubro como ejemplo declarado**: la pieza dice *"ejemplo armado sobre una organización de prueba"*. Nunca "un cliente de X lo usa".
- **Compuerta de los ejemplos — tres moldes:** solo lo que ya corre en producción: **A** cruce con entregable, **B** tarea programada, **C** control contra otra fuente. Si necesita entrar a un sistema, escribir en una base, mandar algo solo o decidir sin revisión, no se publica.

## COM-09 — ChatGPT, Claude y Copilot no son competencia: son el motor (2026-10-15)

Olvidata vende esos productos aplicados a la empresa: los agentes corren sobre Claude.

- **Nunca se posiciona contra ellos:** ni "más barato que", ni "mejor que", ni "no es otro chat", ni nada que los desmerezca.
- **El argumento es de suma:** *Claude trabajando con lo que sabe tu oficina* — el núcleo del rubro, las reglas de la organización, la tarea hecha con revisión.
- **El precio se defiende por la tarea que deja de hacer una persona**, no comparándolo con licencias por usuario. El research de mercado (`docs/referencia/research-precios-ai-agents-second-brain-2026-10.md`) es referencia interna, no argumento frente al cliente.
- Si preguntan *"¿por qué no uso ChatGPT directo?"*: se responde por lo que suma, reconociendo que la herramienta es buena.

## COM-10 — Comunicación instantánea y la promesa (2026-10-13)

- **Un símbolo, un mensaje, una sensación.** Una pieza = una idea. Si hay que leer para entender, falló; si hay que explicarla, falló dos veces. Respaldo: Binet & Field (996 campañas, IPA Databank 1980–2010: las emocionales ganan en todas las métricas); Kahneman (decide el System 1).
- **La promesa transversal de Agentes IA: jubilar a la gente de su trabajo cotidiano** — que trabajen más las máquinas, entendiendo la lógica del usuario. Se muestra la máquina haciendo el trabajo; la conclusión sobre su propio día la saca el prospecto.

## COM-11 — Cómo se menciona un precio en la propuesta

- La **promo de AI Agents y Chatbots** (vigencia en `precios.md`) se dice **una sola vez**, como dato real con fecha (*"este valor es de lanzamiento, cierres hasta el 31/12"*). Nunca repetida como presión en los follow-ups ni con escasez fabricada encima.
- La urgencia operante es el **vencimiento de 7 días** de cada propuesta. Si un deal de diciembre cruza la fecha sin que el prospecto dilate a propósito, se respeta el precio promo de la propuesta.
- En Chatbots, decir siempre que la mensajería de Meta va aparte.

---

## Chequeo de cualquier pieza (sin consultar a nadie)

1. ¿Cada dato tiene **fuente puntual**? Si no, no sale (COM-02).
2. ¿Tiene precio o CTA de venta? Si sí, se cae (COM-01).
3. Si es de Agentes IA: ¿alguien podría **reproducir** algo con esto, o se ve cómo se construye? Si sí, se cae (COM-05).
4. ¿Se entiende **en un segundo, sin leer**, y deja una sensación? Si no, se reescribe (COM-10).
5. ¿Se compara contra alguien o desmerece a ChatGPT, Claude o Copilot? Si sí, se reescribe (COM-03, COM-09).
6. ¿Pasa `claims.md`?
